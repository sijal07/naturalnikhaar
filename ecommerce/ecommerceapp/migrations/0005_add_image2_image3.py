from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("ecommerceapp", "0004_remove_product_image_product_image1_product_image2_and_more"),
    ]

    # image fields were already added in 0004; keep this migration as a no-op
    # so existing production sqlite schemas do not fail with duplicate columns.
    operations = []
