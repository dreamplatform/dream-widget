
from django.conf import settings

BOSH_PASSWORD = getattr(settings, 'DREAMWIDGET_BOSH_PASSWORD', '')
BOSH_ENDPOINT = getattr(settings, 'DREAMWIDGET_BOSH_ENDPOINT', '')

