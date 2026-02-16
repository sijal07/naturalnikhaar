import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create/update an admin user from environment variables."

    def handle(self, *args, **options):
        username = os.getenv("ADMIN_USERNAME", "").strip()
        email = os.getenv("ADMIN_EMAIL", "").strip()
        password = os.getenv("ADMIN_PASSWORD", "").strip()

        if not username or not password:
            self.stdout.write("ensure_admin: skipped (ADMIN_USERNAME/ADMIN_PASSWORD not set)")
            return

        User = get_user_model()
        user = User.objects.filter(username=username).first()

        if user is None:
            user = User.objects.create_user(username=username, email=email or username)
            self.stdout.write(f"ensure_admin: created user '{username}'")
        else:
            self.stdout.write(f"ensure_admin: found existing user '{username}'")

        if email:
            user.email = email
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.set_password(password)
        user.save()

        self.stdout.write("ensure_admin: admin privileges and password ensured")
