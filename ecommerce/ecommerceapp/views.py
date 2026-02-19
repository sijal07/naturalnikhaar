from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.conf import settings

from ecommerceapp.models import Contact, Product, OrderUpdate, Orders, CarouselAd

import razorpay
import traceback
import json
from datetime import timedelta


# ==============================
# Homepage
# ==============================
def index(request):
    query = request.GET.get("query", "").strip()

    try:
        products_qs = Product.objects.all()

        if query:
            products_qs = products_qs.filter(
                Q(product_name__icontains=query) |
                Q(category__icontains=query) |
                Q(subcategory__icontains=query) |
                Q(desc__icontains=query)
            )

        allProds = []
        catprods = products_qs.values("category", "id")
        cats = {item["category"] for item in catprods}

        for cat in cats:
            prod = products_qs.filter(category=cat)
            n = len(prod)
            nSlides = n // 4 + (1 if n % 4 != 0 else 0)
            allProds.append([prod, range(1, nSlides + 1), nSlides])

        ads = (
            CarouselAd.objects.filter(is_active=True)
            .exclude(image="")
            .exclude(image__isnull=True)
        )

        return render(request, "index.html", {
            "allProds": allProds,
            "query": query,
            "ads": ads,
        })

    except Exception as e:
        print("Homepage error:", traceback.format_exc())
        return HttpResponse("Site is live. Homepage recovering.")


# ==============================
# Contact
# ==============================
def contact(request):
    if request.method == "POST":
        Contact.objects.create(
            name=request.POST.get("name"),
            email=request.POST.get("email"),
            desc=request.POST.get("desc"),
            phonenumber=request.POST.get("pnumber")
        )
        messages.info(request, "We will get back to you soon.")

    return render(request, "contact.html")


# ==============================
# About
# ==============================
def about(request):
    return render(request, "about.html")


# ==============================
# Checkout
# ==============================
def checkout(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Login & Try Again")
        return redirect('/auth/login')

    if request.method == "POST":

        items_json = request.POST.get('itemsJson', '{}')
        name = request.POST.get('name', '')
        amount_raw = request.POST.get('amt', '0')
        email = request.POST.get('email', '')
        address1 = request.POST.get('address1', '')
        phone = request.POST.get('phone', '')

        try:
            amount_rupees = float(amount_raw) if amount_raw not in ['NaN', ''] else 0
            amount_paise = max(100, int(amount_rupees * 100))
        except:
            messages.error(request, "Invalid amount in cart")
            return render(request, 'checkout.html')

        if amount_rupees < 1:
            messages.error(request, "Cart is empty.")
            return render(request, 'checkout.html')

        # Save order
        order = Orders.objects.create(
            items_json=items_json,
            name=name,
            amount=int(amount_rupees),
            email=email,
            address1=address1,
            phone=phone,
            paymentstatus="Pending"
        )

        OrderUpdate.objects.create(
            order_id=order.order_id,
            update_desc="Order placed - Payment pending"
        )

        try:
            client = razorpay.Client(
                auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
            )

            razorpay_order = client.order.create({
                'amount': amount_paise,
                'currency': 'INR',
                'receipt': f"order_{order.order_id}",
                'payment_capture': 1,
            })

        except Exception as e:
            print("Razorpay Error:", e)
            messages.error(request, "Payment initialization failed.")
            return render(request, 'checkout.html')

        # Save Razorpay order id
        order.razorpay_order_id = razorpay_order['id']
        order.save()

        return render(request, 'razorpay.html', {
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_amount': amount_paise,
            'razorpay_key': settings.RAZORPAY_KEY_ID,
            'order_id': order.order_id,
            'name': name,
            'email': email,
            'phone': phone,
            'amount': amount_rupees
        })

    return render(request, 'checkout.html')


# ==============================
# Payment Success
# ==============================
@csrf_exempt
def payment_success(request):

    if request.method == "POST":

        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_signature = request.POST.get('razorpay_signature')

        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

        try:
            client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            })

            order = Orders.objects.get(razorpay_order_id=razorpay_order_id)
            order.paymentstatus = "Paid"
            order.amountpaid = order.amount
            order.save()

            OrderUpdate.objects.create(
                order_id=order.order_id,
                update_desc="Payment successful"
            )

            return redirect("profile")

        except Exception as e:
            print("Payment verification failed:", e)
            return redirect("checkout")

    return redirect("checkout")


# ==============================
# Profile
# ==============================
def profile(request):

    if not request.user.is_authenticated:
        messages.warning(request, "Login & Try Again")
        return redirect('/auth/login')

    orders = Orders.objects.filter(email=request.user.email)

    delivered_order_ids = set(
        OrderUpdate.objects.filter(
            order_id__in=orders.values_list('order_id', flat=True),
            delivered=True
        ).values_list('order_id', flat=True)
    )

    for order in orders:
        order.is_delivered = order.order_id in delivered_order_ids
        base_date = order.created_at or timezone.now()
        order.expected_delivery = base_date + timedelta(days=10)

    return render(request, "profile.html", {"items": orders})