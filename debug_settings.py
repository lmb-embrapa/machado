import os
import django
from django.conf import settings

# Set environment variable for settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "machadoproject.settings") # This might be wrong
# We need to find the actual settings module.
# Let's try to find where settings.py is in /var/www/YOURPROJECT
# find /var/www/YOURPROJECT -name "settings.py"
