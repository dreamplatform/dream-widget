
from django.shortcuts import render
from dreamwidget import settings

def get_bosh_session(request):
  from dreamwidget.boshclient import request_bosh_session
  session = request.session
  if 1: #not 'BOSH_JID' in session:
    bosh = request_bosh_session(request.user.username, 'SERVICE:%s'%settings.BOSH_PASSWORD, settings.BOSH_ENDPOINT)
    session['BOSH_JID'] = bosh['jid']
    session['BOSH_SID'] = bosh['sid']
    session['BOSH_RID'] = bosh['rid']
  return {
    'BOSH_JID': session['BOSH_JID'],
    'BOSH_SID': session['BOSH_SID'],
    'BOSH_RID': session['BOSH_RID'],
    'BOSH_ENDPOINT': settings.BOSH_ENDPOINT,
    }

def serve_libs(request, libname, filename):
  if filename.endswith('js'):
    content_type = 'application/javascript'
  elif filename.endswith('css'):
    content_type = 'text/css'
  elif filename.endswith('html'):
    content_type = 'text/html'
  else:
    content_type = 'application/octet-stream'
  context = {}
  #if request.user.is_authenticated():
    #print 'BOSH SESSION INIT'
    #context = get_bosh_session(request)
    #print repr(context)
  return render(request, 'dreamwidget/%s/%s' % (libname, filename), context, content_type=content_type)

