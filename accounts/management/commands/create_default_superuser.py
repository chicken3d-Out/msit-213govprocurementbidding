import os
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Creates a superuser if none exists'

    def handle(self, *args, **kwargs):
        User = get_user_model()
        username = os.environ.get('SUPERUSER_USERNAME', 'vincent')
        password = os.environ.get('SUPERUSER_PASSWORD', 'vincent@admin123')
        email = os.environ.get('SUPERUSER_EMAIL', 'vincentontuca@gmail.com')

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f'Superuser "{username}" created.'))
        else:
            self.stdout.write(f'Superuser "{username}" already exists.')