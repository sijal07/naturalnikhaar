from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ecommerceapp", "0004_remove_product_image_product_image1_product_image2_and_more"),
    ]

    operations = [
        # image2 was created by a previous migration; only add image3 here
        migrations.AddField(
            model_name="product",
            name="image3",
            field=models.ImageField(blank=True, null=True, upload_to="images/images"),
        ),
    ]
