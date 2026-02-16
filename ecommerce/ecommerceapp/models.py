import json

from django.db import models


class Contact(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField()
    desc = models.TextField(max_length=500)
    phonenumber = models.IntegerField()

    def __int__(self):
        return self.id


class Product(models.Model):
    product_name = models.CharField(max_length=100)
    category = models.CharField(max_length=100, default="")
    subcategory = models.CharField(max_length=50, default="")

    # MRP (original price) and selling price
    mrp = models.IntegerField(default=0)           # this will be crossed
    selling_price = models.IntegerField(default=0)  # this will be shown as main price

    desc = models.CharField(max_length=300)

    image1 = models.ImageField(upload_to='images/images', blank=True, null=True)
    image2 = models.ImageField(upload_to='images/images', blank=True, null=True)
    image3 = models.ImageField(upload_to='images/images', blank=True, null=True)

    def __str__(self):
        return self.product_name

    @property
    def offer_percentage(self):
        """Calculate and return the offer percentage based on MRP and selling price"""
        if self.mrp > 0:
            discount = ((self.mrp - self.selling_price) / self.mrp) * 100
            return int(round(discount))
        return 0


class Orders(models.Model):
    order_id = models.AutoField(primary_key=True)
    items_json = models.CharField(max_length=5000)
    amount = models.IntegerField(default=0)
    name = models.CharField(max_length=90)
    email = models.CharField(max_length=90)
    address1 = models.CharField(max_length=200)
    address2 = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=100)
    oid = models.CharField(max_length=150, blank=True)
    amountpaid = models.CharField(max_length=500, blank=True, null=True)
    paymentstatus = models.CharField(max_length=20, blank=True)
    phone = models.CharField(max_length=100, default="")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.name

    def get_products_summary(self):
        """
        Return products in a readable format:
        1x- Herbal hair growth shampoo 200ml, 4x- Neem Tulsi Soap
        """
        if not self.items_json:
            return ""

        try:
            cart_data = json.loads(self.items_json)
        except (TypeError, ValueError):
            return self.items_json

        if not isinstance(cart_data, dict):
            return self.items_json

        formatted_items = []
        for values in cart_data.values():
            if not isinstance(values, (list, tuple)) or len(values) < 2:
                continue
            quantity = values[0]
            product_name = str(values[1]).strip()
            if not product_name:
                continue
            formatted_items.append(f"{quantity}x- {product_name}")

        return ", ".join(formatted_items) if formatted_items else self.items_json


class OrderUpdate(models.Model):
    update_id = models.AutoField(primary_key=True)
    order_id = models.IntegerField(default="")
    update_desc = models.CharField(max_length=5000)
    delivered = models.BooleanField(default=False)
    timestamp = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.update_desc[0:7] + "..."


# 🔥 NEW MODEL FOR CAROUSEL ADVERTISEMENTS 🔥
class CarouselAd(models.Model):
    title = models.CharField(max_length=150, blank=True)
    image = models.ImageField(upload_to='carousel_ads/')
    # Paste full product URL or any internal/external link
    link = models.URLField(max_length=500, help_text="URL of product or page")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title or f"Carousel Ad #{self.id}"
