from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('contact/', views.contact, name="contact"),
    path('about/', views.about, name="about"),
    path('profile/', views.profile, name="profile"),
    path('checkout/', views.checkout, name="checkout"),
    path("payment_success/", views.payment_success, name="payment_success"),

    # AJAX endpoint used by the frontend autocomplete dropdown.  Returns a
    # filtered list of product names and active shop categories.
    path('autocomplete/', views.autocomplete, name="autocomplete"),
]