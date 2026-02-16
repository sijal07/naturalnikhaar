import json
from collections import Counter

from django.db import OperationalError, ProgrammingError
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate

from ecommerceapp.models import CarouselAd, Contact, Orders, Product


def admin_dashboard_context(request):
    if not request.path.startswith('/admin/'):
        return {}

    total_orders = Orders.objects.count()
    total_revenue = Orders.objects.aggregate(total=Sum('amount')).get('total') or 0
    total_products = Product.objects.count()
    total_contacts = Contact.objects.count()
    active_ads = CarouselAd.objects.filter(is_active=True).count()

    payment_rows = (
        Orders.objects.values('paymentstatus')
        .annotate(total=Count('order_id'))
        .order_by('-total')
    )
    payment_data = []
    for row in payment_rows:
        label = (row.get('paymentstatus') or 'Unknown').strip() or 'Unknown'
        payment_data.append((label, row['total']))

    state_rows = (
        Orders.objects.values('state')
        .annotate(total=Count('order_id'))
        .order_by('-total')[:7]
    )
    state_data = []
    for row in state_rows:
        label = (row.get('state') or 'Unknown').strip() or 'Unknown'
        state_data.append((label, row['total']))

    category_rows = (
        Product.objects.values('category')
        .annotate(total=Count('id'))
        .order_by('-total')[:7]
    )
    category_data = []
    for row in category_rows:
        label = (row.get('category') or 'Uncategorized').strip() or 'Uncategorized'
        category_data.append((label, row['total']))

    try:
        orders_by_day_rows = list(
            Orders.objects.exclude(created_at__isnull=True)
            .annotate(order_date=TruncDate("created_at"))
            .values("order_date")
            .annotate(total=Count("order_id"))
            .order_by("order_date")
        )
        order_series_labels = [row["order_date"].strftime("%Y-%m-%d") for row in orders_by_day_rows]
        order_series_values = [row["total"] for row in orders_by_day_rows]
    except (OperationalError, ProgrammingError):
        # DB schema not migrated yet (created_at missing). Keep admin usable.
        order_series_labels = []
        order_series_values = []

    domain_counter = Counter()
    for email in Contact.objects.values_list("email", flat=True):
        value = (email or "").strip().lower()
        if "@" in value:
            domain_counter[value.split("@", 1)[1]] += 1
        elif value:
            domain_counter["invalid-email"] += 1

    top_domains = domain_counter.most_common(7)

    return {
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'total_products': total_products,
        'total_contacts': total_contacts,
        'active_ads': active_ads,
        'payment_labels_json': json.dumps([item[0] for item in payment_data]),
        'payment_values_json': json.dumps([item[1] for item in payment_data]),
        'state_labels_json': json.dumps([item[0] for item in state_data]),
        'state_values_json': json.dumps([item[1] for item in state_data]),
        'category_labels_json': json.dumps([item[0] for item in category_data]),
        'category_values_json': json.dumps([item[1] for item in category_data]),
        'order_series_labels_json': json.dumps(order_series_labels),
        'order_series_values_json': json.dumps(order_series_values),
        'contact_domain_labels_json': json.dumps([item[0] for item in top_domains]),
        'contact_domain_values_json': json.dumps([item[1] for item in top_domains]),
    }
