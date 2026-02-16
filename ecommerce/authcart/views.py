from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.views.generic import View
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from django.core.mail import EmailMessage
from django.conf import settings

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import authenticate, login, logout


# ========== SIGNUP (NO EMAIL ACTIVATION) ==========

def signup(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("pass1")
        confirm_password = request.POST.get("pass2")

        if not email or not password or not confirm_password:
            messages.warning(request, "Please fill in all fields")
            return render(request, "signup.html")

        if password != confirm_password:
            messages.warning(request, "Passwords do not match")
            return render(request, "signup.html")

        if User.objects.filter(username=email).exists():
            messages.info(request, "Email is already registered")
            return render(request, "signup.html")

        # Create ACTIVE user – no activation link
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
        )
        user.is_active = True
        user.save()

        # Auto-login after signup
        myuser = authenticate(request, username=email, password=password)
        if myuser is not None:
            login(request, myuser)
            messages.success(request, "Signup successful. You are now logged in.")
            return redirect("/")

        messages.success(request, "Signup successful. Please login.")
        return redirect("/auth/login/")

    return render(request, "signup.html")


# ========== LOGIN ==========

def handlelogin(request):
    if request.method == "POST":
        username = request.POST.get("email")       # accepts username or email
        userpassword = request.POST.get("password")

        if not username or not userpassword:
            messages.error(request, "Please fill in all fields")
            return redirect("/auth/login/")

        myuser = authenticate(request, username=username, password=userpassword)
        if myuser is None and "@" in username:
            # Fallback: allow login with email even when username is different.
            user_obj = User.objects.filter(email__iexact=username).first()
            if user_obj:
                myuser = authenticate(request, username=user_obj.username, password=userpassword)

        if myuser is not None:
            if myuser.is_active:
                login(request, myuser)
                messages.success(request, "Login success")
                return redirect("/")
            else:
                messages.warning(request, "Account is inactive")
                return redirect("/auth/login/")
        else:
            messages.error(request, "Invalid credentials")
            return redirect("/auth/login/")

    return render(request, "login.html")


# ========== LOGOUT ==========

def handlelogout(request):
    logout(request)
    messages.info(request, "Logout success")
    return redirect("/auth/login/")


# ========== REQUEST RESET EMAIL ==========

class RequestResetEmailView(View):
    def get(self, request):
        return render(request, "request-reset-email.html")

    def post(self, request):
        email = request.POST.get("email")
        user = User.objects.filter(email=email)

        if user.exists():
            email_subject = "[Reset Your Password]"
            message = render_to_string(
                "reset-user-password.html",
                {
                    "domain": "127.0.0.1:8000",
                    "uid": urlsafe_base64_encode(force_bytes(user[0].pk)),
                    "token": PasswordResetTokenGenerator().make_token(user[0]),
                },
            )

            # When SMTP is configured, uncomment to send email:
            # email_message = EmailMessage(
            #     email_subject, message, settings.EMAIL_HOST_USER, [email]
            # )
            # email_message.send()

            messages.info(
                request,
                f"WE HAVE SENT YOU AN EMAIL WITH INSTRUCTIONS ON HOW TO RESET THE PASSWORD. {message}",
            )
        else:
            messages.error(request, "No user found with this email")

        return render(request, "request-reset-email.html")


# ========== SET NEW PASSWORD ==========

class SetNewPasswordView(View):
    def get(self, request, uidb64, token):
        context = {
            "uidb64": uidb64,
            "token": token,
        }
        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                messages.warning(request, "Password reset link is invalid")
                return render(request, "request-reset-email.html")

        except DjangoUnicodeDecodeError:
            pass

        return render(request, "set-new-password.html", context)

    def post(self, request, uidb64, token):
        context = {
            "uidb64": uidb64,
            "token": token,
        }
        password = request.POST.get("pass1")
        confirm_password = request.POST.get("pass2")

        if password != confirm_password:
            messages.warning(request, "Password is not matching")
            return render(request, "set-new-password.html", context)

        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            user.set_password(password)
            user.save()
            messages.success(
                request, "Password reset success. Please login with new password."
            )
            return redirect("/auth/login/")
        except DjangoUnicodeDecodeError:
            messages.error(request, "Something went wrong")
            return render(request, "set-new-password.html", context)
