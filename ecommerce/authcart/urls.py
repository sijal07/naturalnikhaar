from django.urls import path
from . import views  # ✅ FIXED: Import from current app (.)

app_name = 'authcart'  # ✅ Namespace for reverse URLs

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("login/", views.handlelogin, name="login"),  # ✅ FIXED: name="login"
    path("logout/", views.handlelogout, name="logout"),
    
    # Password reset endpoints
    path("request-reset-email/", views.RequestResetEmailView.as_view(), name="request-reset-email"),
    path("set-new-password/<uidb64>/<token>/", views.SetNewPasswordView.as_view(), name="set-new-password"),  # ✅ FIXED: Added missing "/"
]
