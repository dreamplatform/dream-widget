
#encoding=utf-8

from django.conf import settings as SETTINGS

def settings(context):
  return  {
    'DREAMWIDGETURL' : SETTINGS.DREAMWIDGET_URL,
    'DREAMWIDGET_DOMAIN': SETTINGS.DREAMWIDGET_DOMAIN,
    'DREAMWIDGET_USERDB_DOMAIN': SETTINGS.DREAMWIDGET_USERDB_DOMAIN,
    'DREAMWIDGET_MSG_DOMAIN': SETTINGS.DREAMWIDGET_MSG_DOMAIN,
    'DREAMWIDGET_DESKTOP_DOMAIN': SETTINGS.DREAMWIDGET_DESKTOP_DOMAIN,
    }
