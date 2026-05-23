from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import os


class Command(BaseCommand):
    help = 'Creates a superuser if none exists'

    def handle(self, *args, **options):
        try:
            username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin')
            email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
            password = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'admin123')

            print(f"🔍 Checking for superuser: {username}")

            if not User.objects.filter(username=username).exists():
                User.objects.create_superuser(username, email, password)
                print(f"✅ Successfully created superuser: {username}")
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created superuser "{username}"')
                )
            else:
                user = User.objects.get(username=username)
                # Update password if it already exists
                user.set_password(password)
                user.is_superuser = True
                user.is_staff = True
                user.save()
                print(f"✅ Superuser {username} already exists, updated credentials")
                self.stdout.write(
                    self.style.SUCCESS(f'Superuser "{username}" updated')
                )
        except Exception as e:
            print(f"❌ Error creating superuser: {str(e)}")
            self.stdout.write(
                self.style.ERROR(f'Error: {str(e)}')
            )
