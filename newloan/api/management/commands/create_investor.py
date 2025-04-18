from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.models import Investor

class Command(BaseCommand):
    help = 'Creates an Investor record for an existing user'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username of the user')

    def handle(self, *args, **options):
        username = options['username']
        try:
            user = User.objects.get(username=username)
            investor, created = Investor.objects.get_or_create(user=user)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Successfully created Investor record for user {username}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Investor record already exists for user {username}'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User {username} does not exist')) 