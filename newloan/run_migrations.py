import os
import sys

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'newloan.config.settings')

# Import Django and run the migrations
import django
django.setup()

from django.core.management import call_command

# Run the migrations
call_command('makemigrations')
call_command('migrate') 