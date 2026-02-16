from django.shortcuts import render, redirect
from django.db.models import Q
from ecommerceapp.models import Contact, Product, OrderUpdate, Orders, CarouselAd
from django.contrib import messages
from math import ceil
from ecommerceapp import keys
from django.views.decorators.csrf import csrf_exempt
import razorpay
from decimal import Decimal
import traceback
from datetime import timedelta
from django.utils import timezone


# Test Razorpay connection first
try:
    client = razorpay.Client(auth=(keys.KEY_ID, keys.KEY_SECRET))
    print(f"Razorpay client initialized with KEY_ID: {keys.KEY_ID[:10]}...")
except Exception as e:
    print(f"Razorpay init failed: {e}")
    client = None


def index(request):
    query = request.GET.get("query", "").strip()
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

    # 🔥 Fetch active carousel ads for homepage
    ads = CarouselAd.objects.filter(is_active=True)

    return render(request, "index.html", {
        "allProds": allProds,
        "query": query,
        "ads": ads,
    })


def contact(request):
    if request.method == "POST":
        Contact.objects.create(
            name=request.POST.get("name"),
            email=request.POST.get("email"),
            desc=request.POST.get("desc"),
            phonenumber=request.POST.get("pnumber")
        )
        messages.info(request, "We will get back to you soon..")
    return render(request, "contact.html")


def about(request):
    return render(request, "about.html")


def checkout(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Login & Try Again")
        return redirect('/auth/login')

    if request.method == "POST":
        # Safe data extraction
        items_json = request.POST.get('itemsJson', '{}')
        name = request.POST.get('name', '')
        amount_raw = request.POST.get('amt', '0')
        email = request.POST.get('email', '')
        address1 = request.POST.get('address1', '')
        phone = request.POST.get('phone', '')

        # **CRITICAL: Fix amount parsing**
        try:
            amount_rupees = float(amount_raw) if amount_raw != 'NaN' and amount_raw != '' else 0
            amount_paise = max(100, int(amount_rupees * 100))  # Min ₹1
        except:
            messages.error(request, "Invalid amount in cart")
            return render(request, 'checkout.html')

        if amount_rupees < 1:
            messages.error(request, "Cart is empty. Add items first!")
            return render(request, 'checkout.html')

        print(f"Order: Rs.{amount_rupees} | Items: {items_json[:50]}...")

        # Save order
        order = Orders.objects.create(
            items_json=items_json,
            name=name,
            amount=int(amount_rupees),
            email=email,
            address1=address1,
            phone=phone
        )
        
        OrderUpdate.objects.create(order_id=order.order_id, update_desc="Order placed - Payment pending")

        # **DEBUG: Test Razorpay order creation**
        if not client:
            messages.error(request, "Payment service unavailable. Contact support.")
            return render(request, 'checkout.html')

        try:
            print("Creating Razorpay order...")
            razorpay_order = client.order.create({
                'amount': amount_paise,
                'currency': 'INR',
                'receipt': f"order_{order.order_id}",
                'payment_capture': 1,
                'notes': {'shipping': name, 'order_id': order.order_id}
            })
            print(f"Razorpay order created: {razorpay_order['id']}")
        except Exception as e:
            error_msg = str(e)
            print(f"Razorpay Error: {error_msg}")
            print(f"Full traceback: {traceback.format_exc()}")
            
            # Common fixes in messages
            if "INVALID_KEY" in error_msg or "KEY" in error_msg:
                messages.error(request, "Invalid payment keys. Admin: Check keys.py")
            elif "NETWORK" in error_msg:
                messages.error(request, "Payment service temporarily unavailable")
            else:
                messages.error(request, f"Payment setup failed: {error_msg[:50]}...")
            return render(request, 'checkout.html')

        # Success - redirect to payment
        return render(request, 'razorpay.html', {
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_amount': amount_paise,
            'razorpay_key': keys.KEY_ID,
            'order_id': order.order_id,
            'name': name,
            'email': email,
            'phone': phone,
            'amount': amount_rupees
        })

    return render(request, 'checkout.html')


@csrf_exempt
def handlerequest(request):
    if request.method != "POST":
        return render(request, 'paymentstatus.html', {'response': {'status': 'error', 'message': 'Invalid method'}})

    try:
        payment_id = request.POST.get('razorpay_payment_id')
        order_id = request.POST.get('razorpay_order_id')
        signature = request.POST.get('razorpay_signature')

        print(f"Payment callback: {payment_id}, {order_id}")

        if not all([payment_id, order_id, signature]):
            return render(request, 'paymentstatus.html', {'response': {'status': 'error', 'message': 'Missing payment data'}})

        # Verify signature
        client.utility.verify_payment_signature({
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        })

        # Update order
        rid = order_id.replace("order_", "")
        order = Orders.objects.get(order_id=int(rid))
        order.paymentstatus = "PAID"
        order.oid = payment_id
        order.amountpaid = str(float(order.amount))
        order.save()

        print(f"Order {rid} PAID with {payment_id}")
        return render(request, 'paymentstatus.html', {
            'response': {
                'status': 'success',
                'message': 'Payment successful!',
                'order_id': order.order_id,
                'payment_id': payment_id
            }
        })

    except Exception as e:
        print(f"Payment verification failed: {e}")
        return render(request, 'paymentstatus.html', {
            'response': {'status': 'error', 'message': f'Payment failed: {str(e)[:50]}'}
        })


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

    # Show delivery state from order updates; otherwise show expected date.
    for order in orders:
        order.is_delivered = order.order_id in delivered_order_ids
        base_date = order.created_at or timezone.now()
        order.expected_delivery = base_date + timedelta(days=10)
    
    context = {"items": orders}
    return render(request, "profile.html", context)
