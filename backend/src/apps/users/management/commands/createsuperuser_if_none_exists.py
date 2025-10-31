import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Create a superuser if none exist'

    def handle(self, *args, **options):
        User = get_user_model()
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write(self.style.SUCCESS('Superuser already exists.'))
            return

        email = os.environ.get('DEFAULT_SUPERUSER_EMAIL')
        password = os.environ.get('DEFAULT_SUPERUSER_PASSWORD')

        if not email or not password:
            self.stderr.write(self.style.ERROR('DEFAULT_SUPERUSER_EMAIL and DEFAULT_SUPERUSER_PASSWORD must be set'))
            return

        User.objects.create_superuser(email=email, password=password)
        self.stdout.write(self.style.SUCCESS('Superuser created successfully.'))
