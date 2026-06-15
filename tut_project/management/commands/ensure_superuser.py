from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from tut_project.config import config
import os


class Command(BaseCommand):
    help = "Creates a superuser if it does not exist"

    def handle(self, *args, **options):
        User = get_user_model()
        email = config.DJANGO_SUPERUSER_EMAIL
        password = config.DJANGO_SUPERUSER_PASSWORD

        if not all([email, password]):
            self.stdout.write(self.style.WARNING("Superuser credentials not provided"))
            return

        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f"Superuser {email} already exists"))
            return

        User.objects.create_superuser(email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f"Superuser {email} created successfully"))