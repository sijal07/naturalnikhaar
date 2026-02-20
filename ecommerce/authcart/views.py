from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.generic import View
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator  # ✅ IMPORTANT
import os


# ========== SIGNUP ==========
def signup(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("pass1", "").strip()
        confirm_password = request.POST.get("pass2", "").strip()

        if not email or not password or not confirm_password:
            messages.warning(request, "Please fill in all fields")
            return render(request, "signup.html")

        if password != confirm_password:
            messages.warning(request, "Passwords do not match")
            return render(request, "signup.html")

        if User.objects.filter(username=email).exists():
            messages.info(request, "Email is already registered")
            return render(request, "signup.html")

        try:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
            )
            user.is_active = True
            user.save()

            myuser = authenticate(request, username=email, password=password)
            if myuser:
                login(request, myuser)
                messages.success(request, "Signup successful! Welcome!")
                return redirect("/")

        except Exception as e:
            print("Signup Error:", e)
            messages.error(request, "Signup failed. Try again.")

    return render(request, "signup.html")


# ========== LOGIN ==========
def handlelogin(request):
    if request.method == "POST":
        username = request.POST.get("email", "").strip()
        password = request.POST.get("password", "").strip()

        if not username or not password:
            messages.error(request, "Please enter email and password")
            return render(request, "login.html")

        user = authenticate(request, username=username, password=password)

        if user is None and "@" in username:
            user_obj = User.objects.filter(email__iexact=username).first()
            if user_obj:
                user = authenticate(request, username=user_obj.username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                messages.success(request, "Login successful!")
                return redirect("/")
            else:
                messages.warning(request, "Account inactive.")
        else:
            messages.error(request, "Invalid email or password")

    return render(request, "login.html")


# ========== LOGOUT ==========
def handlelogout(request):
    logout(request)
    messages.info(request, "Logged out successfully")
    return redirect("/auth/login/")


# ========== REQUEST RESET EMAIL ==========
class RequestResetEmailView(View):
    def get(self, request):
        return render(request, "request-reset-email.html")

    def post(self, request):
        email = request.POST.get("email", "").strip()

        if not email:
            messages.error(request, "Please enter your email")
            return render(request, "request-reset-email.html")

        user = User.objects.filter(email__iexact=email).first()

        if user:
            try:
                # Domain
                domain = os.getenv("RENDER_EXTERNAL_HOSTNAME", "naturalnikhaar.com")
                if not domain.startswith("http"):
                    domain = f"https://{domain}"

                subject = "Natural Nikhaar - Reset Your Password"

                message = render_to_string(
                    "reset-user-password.html",
                    {
                        "domain": domain,
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "token": PasswordResetTokenGenerator().make_token(user),
                    },
                )

                email_message = EmailMessage(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    [email],
                )
                email_message.content_subtype = "html"
                email_message.send()

                messages.success(request, "Password reset email sent!")

            except Exception as e:
                print("Email Error:", e)
                messages.error(request, "Something went wrong. Try again.")
        else:
            messages.error(request, "No account found with this email")

        return render(request, "request-reset-email.html")


# ========== SET NEW PASSWORD ==========
class SetNewPasswordView(View):
    def get(self, request, uidb64, token):
        context = {"uidb64": uidb64, "token": token}

        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                messages.warning(request, "Invalid or expired link")
                return render(request, "request-reset-email.html")

        except (DjangoUnicodeDecodeError, User.DoesNotExist):
            messages.warning(request, "Invalid reset link")
            return render(request, "request-reset-email.html")

        return render(request, "set-new-password.html", context)

    def post(self, request, uidb64, token):
        context = {"uidb64": uidb64, "token": token}

        password = request.POST.get("pass1", "").strip()
        confirm_password = request.POST.get("pass2", "").strip()

        if not password or not confirm_password:
            messages.warning(request, "Please fill all fields")
            return render(request, "set-new-password.html", context)

        if password != confirm_password:
            messages.warning(request, "Passwords don't match")
            return render(request, "set-new-password.html", context)

        if len(password) < 8:
            messages.warning(request, "Password must be at least 8 characters")
            return render(request, "set-new-password.html", context)

        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)

            user.set_password(password)
            user.save()

            messages.success(request, "Password reset successful! Please login.")
            return redirect("/auth/login/")

        except Exception as e:
            print("Reset Error:", e)
            messages.error(request, "Reset failed. Try again.")
            return render(request, "set-new-password.html", context)