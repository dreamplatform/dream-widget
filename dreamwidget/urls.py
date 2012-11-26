
from django.conf.urls.defaults import *

urlpatterns = patterns('dreamwidget.views',
  (r'dream.js', 'serve_libs', {'libname': 'dream', 'filename': 'dream.js'}),
)

