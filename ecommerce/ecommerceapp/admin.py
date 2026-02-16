import csv
import io

from django.contrib import admin, messages
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import path, reverse

from ecommerceapp.models import Contact, Product, Orders, OrderUpdate, CarouselAd

admin.site.site_header = "NATURAL NIKHAAR Admin"
admin.site.site_title = "NATURAL NIKHAAR Admin Portal"
admin.site.index_title = "Welcome to NATURAL NIKHAAR Admin Portal"


def export_queryset_to_csv(queryset, field_names, filename):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)
    writer.writerow(field_names)
    for obj in queryset:
        writer.writerow([getattr(obj, field, "") for field in field_names])
    return response


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "phonenumber")
    search_fields = ("name", "email", "phonenumber")
    change_list_template = "admin/ecommerceapp/contact/change_list.html"
    actions = ("export_selected_to_csv",)

    csv_fields = ("id", "name", "email", "desc", "phonenumber")
    import_fields = ("name", "email", "desc", "phonenumber")

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "export-csv/",
                self.admin_site.admin_view(self.export_csv_view),
                name="ecommerceapp_contact_export_csv",
            ),
            path(
                "import-csv/",
                self.admin_site.admin_view(self.import_csv_view),
                name="ecommerceapp_contact_import_csv",
            ),
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["export_csv_url"] = reverse("admin:ecommerceapp_contact_export_csv")
        extra_context["import_csv_url"] = reverse("admin:ecommerceapp_contact_import_csv")
        return super().changelist_view(request, extra_context=extra_context)

    @admin.action(description="Export selected contacts to CSV")
    def export_selected_to_csv(self, request, queryset):
        return export_queryset_to_csv(queryset, self.csv_fields, "contacts_selected.csv")

    def export_csv_view(self, request):
        queryset = Contact.objects.all().order_by("id")
        return export_queryset_to_csv(queryset, self.csv_fields, "contacts_all.csv")

    def import_csv_view(self, request):
        if request.method == "POST":
            csv_file = request.FILES.get("csv_file")
            if not csv_file:
                self.message_user(request, "Please choose a CSV file.", level=messages.ERROR)
                return redirect("admin:ecommerceapp_contact_changelist")

            try:
                text_data = csv_file.read().decode("utf-8-sig")
                reader = csv.DictReader(io.StringIO(text_data))
            except Exception:
                self.message_user(request, "Invalid CSV file.", level=messages.ERROR)
                return redirect("admin:ecommerceapp_contact_changelist")

            missing_headers = [field for field in self.import_fields if field not in (reader.fieldnames or [])]
            if missing_headers:
                self.message_user(
                    request,
                    f"Missing headers: {', '.join(missing_headers)}",
                    level=messages.ERROR,
                )
                return redirect("admin:ecommerceapp_contact_changelist")

            created = 0
            skipped = 0
            for row in reader:
                try:
                    Contact.objects.create(
                        name=(row.get("name") or "").strip(),
                        email=(row.get("email") or "").strip(),
                        desc=(row.get("desc") or "").strip(),
                        phonenumber=int((row.get("phonenumber") or "0").strip() or 0),
                    )
                    created += 1
                except Exception:
                    skipped += 1

            self.message_user(
                request,
                f"CSV import complete. Created: {created}, Skipped: {skipped}",
                level=messages.SUCCESS,
            )
            return redirect("admin:ecommerceapp_contact_changelist")

        context = {
            **self.admin_site.each_context(request),
            "opts": self.model._meta,
            "title": "Import Contact CSV",
            "expected_headers": ", ".join(self.import_fields),
            "back_url": reverse("admin:ecommerceapp_contact_changelist"),
        }
        return render(request, "admin/csv_import.html", context)


@admin.register(Orders)
class OrdersAdmin(admin.ModelAdmin):
    list_display = ("order_id", "name", "products_summary", "email", "city", "state", "amount", "paymentstatus")
    list_filter = ("state", "paymentstatus", "city")
    search_fields = ("order_id", "name", "email", "phone", "oid")
    change_list_template = "admin/ecommerceapp/orders/change_list.html"
    actions = ("export_selected_to_csv",)

    csv_fields = (
        "order_id",
        "items_json",
        "amount",
        "name",
        "email",
        "address1",
        "address2",
        "city",
        "state",
        "zip_code",
        "oid",
        "amountpaid",
        "paymentstatus",
        "phone",
    )
    import_fields = (
        "items_json",
        "amount",
        "name",
        "email",
        "address1",
        "address2",
        "city",
        "state",
        "zip_code",
        "oid",
        "amountpaid",
        "paymentstatus",
        "phone",
    )

    @admin.display(description="Products")
    def products_summary(self, obj):
        return obj.get_products_summary()

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "export-csv/",
                self.admin_site.admin_view(self.export_csv_view),
                name="ecommerceapp_orders_export_csv",
            ),
            path(
                "import-csv/",
                self.admin_site.admin_view(self.import_csv_view),
                name="ecommerceapp_orders_import_csv",
            ),
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["export_csv_url"] = reverse("admin:ecommerceapp_orders_export_csv")
        extra_context["import_csv_url"] = reverse("admin:ecommerceapp_orders_import_csv")
        return super().changelist_view(request, extra_context=extra_context)

    @admin.action(description="Export selected orders to CSV")
    def export_selected_to_csv(self, request, queryset):
        return export_queryset_to_csv(queryset, self.csv_fields, "orders_selected.csv")

    def export_csv_view(self, request):
        queryset = Orders.objects.all().order_by("-order_id")
        return export_queryset_to_csv(queryset, self.csv_fields, "orders_all.csv")

    def import_csv_view(self, request):
        if request.method == "POST":
            csv_file = request.FILES.get("csv_file")
            if not csv_file:
                self.message_user(request, "Please choose a CSV file.", level=messages.ERROR)
                return redirect("admin:ecommerceapp_orders_changelist")

            try:
                text_data = csv_file.read().decode("utf-8-sig")
                reader = csv.DictReader(io.StringIO(text_data))
            except Exception:
                self.message_user(request, "Invalid CSV file.", level=messages.ERROR)
                return redirect("admin:ecommerceapp_orders_changelist")

            missing_headers = [field for field in self.import_fields if field not in (reader.fieldnames or [])]
            if missing_headers:
                self.message_user(
                    request,
                    f"Missing headers: {', '.join(missing_headers)}",
                    level=messages.ERROR,
                )
                return redirect("admin:ecommerceapp_orders_changelist")

            created = 0
            skipped = 0
            for row in reader:
                try:
                    Orders.objects.create(
                        items_json=(row.get("items_json") or "").strip(),
                        amount=int((row.get("amount") or "0").strip() or 0),
                        name=(row.get("name") or "").strip(),
                        email=(row.get("email") or "").strip(),
                        address1=(row.get("address1") or "").strip(),
                        address2=(row.get("address2") or "").strip(),
                        city=(row.get("city") or "").strip(),
                        state=(row.get("state") or "").strip(),
                        zip_code=(row.get("zip_code") or "").strip(),
                        oid=(row.get("oid") or "").strip(),
                        amountpaid=(row.get("amountpaid") or "").strip(),
                        paymentstatus=(row.get("paymentstatus") or "").strip(),
                        phone=(row.get("phone") or "").strip(),
                    )
                    created += 1
                except Exception:
                    skipped += 1

            self.message_user(
                request,
                f"CSV import complete. Created: {created}, Skipped: {skipped}",
                level=messages.SUCCESS,
            )
            return redirect("admin:ecommerceapp_orders_changelist")

        context = {
            **self.admin_site.each_context(request),
            "opts": self.model._meta,
            "title": "Import Orders CSV",
            "expected_headers": ", ".join(self.import_fields),
            "back_url": reverse("admin:ecommerceapp_orders_changelist"),
        }
        return render(request, "admin/csv_import.html", context)


admin.site.register(Product)
admin.site.register(OrderUpdate)


@admin.register(CarouselAd)
class CarouselAdAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("title", "link")
