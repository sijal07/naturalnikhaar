from django import template
from django.db.models import Count, Sum
import json

from ecommerceapp.models import CarouselAd, Orders, Product

register = template.Library()


@register.inclusion_tag("admin/dashboard_charts.html")
def admin_dashboard():
    total_orders = Orders.objects.count()
    total_revenue = Orders.objects.aggregate(total=Sum("amount")).get("total") or 0
    total_products = Product.objects.count()
    active_ads = CarouselAd.objects.filter(is_active=True).count()

    payment_rows = (
        Orders.objects.values("paymentstatus")
        .annotate(total=Count("order_id"))
        .order_by("-total")
    )
    payment_data = []
    for row in payment_rows:
        label = (row.get("paymentstatus") or "Unknown").strip() or "Unknown"
        payment_data.append((label, row["total"]))

    state_rows = (
        Orders.objects.values("state")
        .annotate(total=Count("order_id"))
        .order_by("-total")[:7]
    )
    state_data = []
    for row in state_rows:
        label = (row.get("state") or "Unknown").strip() or "Unknown"
        state_data.append((label, row["total"]))

    category_rows = (
        Product.objects.values("category")
        .annotate(total=Count("id"))
        .order_by("-total")[:7]
    )
    category_data = []
    for row in category_rows:
        label = (row.get("category") or "Uncategorized").strip() or "Uncategorized"
        category_data.append((label, row["total"]))

    recent_order_rows = list(
        Orders.objects.order_by("-order_id").values("order_id", "amount")[:10]
    )
    recent_order_rows.reverse()

    order_series_labels = [f"#{row['order_id']}" for row in recent_order_rows]
    order_series_values = [row.get("amount") or 0 for row in recent_order_rows]

    return {
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "total_products": total_products,
        "active_ads": active_ads,
        "payment_labels_json": json.dumps([item[0] for item in payment_data]),
        "payment_values_json": json.dumps([item[1] for item in payment_data]),
        "state_labels_json": json.dumps([item[0] for item in state_data]),
        "state_values_json": json.dumps([item[1] for item in state_data]),
        "category_labels_json": json.dumps([item[0] for item in category_data]),
        "category_values_json": json.dumps([item[1] for item in category_data]),
        "order_series_labels_json": json.dumps(order_series_labels),
        "order_series_values_json": json.dumps(order_series_values),
    }
