import httplib, sys, random
from base64 import b64decode, b64encode
from urlparse import urlparse
from xml.dom import minidom

from twisted.words.protocols.jabber.sasl_mechanisms import DigestMD5


def request_bosh_session(username, password, service):
    c = BOSHClient(service, '%s@msg.dreamschool.fi'%username, password)
    c.request_bosh_session()

    return {'jid': c.jabberid.full(), 'sid': c.sid, 'rid': c.rid}


NS_COMMANDS = 'http://jabber.org/protocol/commands'

class ConnectionError(Exception):
    """Error raised when connection with server failed"""
    pass


class BOSHClient:
    """
    Quite simple BOSH client used by Django-XMPPAuth.
    When you initialize the client, it does NOT connect! Here is a mock 
    connection process with the BOSH Client:
    
    >>> client = BOSHClient('http://debian/http-bind/', 'essai@debian', 'essai', resource='web', debug=False)
    >>> client.init_connection()
    >>> client.request_bosh_session()
    >>> sid = client.authenticate_xmpp()
    >>> client.close_connection()
    """
    
    def __init__(self, bosh_service, jid='', password='', resource='web', debug=False):
        """
        Initialize the client.
        You must specify the Jabber ID, the corresponding password and the URL
        of the BOSH service to connect to.
        """

        self.debug = False
        
        self.connection = None
        
        if jid:
            self.jid = JID(jid, resource)
        else:
            self.jid = ''
        self.password = password
        self.bosh_service = urlparse(bosh_service)
        self.resource = resource
        
        self.rid = random.randint(0, 10000000)
        self.log('Init RID: %s' % self.rid)
        
        self.content_type = "text/xml; charset=utf-8"
        self.headers = {
            "Content-type": "text/plain; charset=UTF-8",
            "Accept": "text/xml",
        }
        
        self.server_auth = []
    
    def log(self, message):
        """
        Print a message in the standard output. Warning: this function makes the
        client very verbose!
        """
        if self.debug:
            print '[DEBUG] ' + message
    
    def get_sid(self):
        """Return the SID assigned to this client"""
        return self.sid
    
    def get_rid(self):
        """Return the RID of this client"""
        return self.rid
    
    def set_rid(self, rid=0):
        """
        Create a random RID and use it, except if rid is specified and different
        from 0.
        """
        if rid == 0:
            self.rid = random.randint(0, 10000000)
        else:
            self.rid = rid
    
    def init_connection(self):
        """Initialize the HTTP connection (not the XMPP session!)"""
        self.log('Initializing connection to %s' % (self.bosh_service.netloc))
        self.connection = httplib.HTTPConnection(self.bosh_service.netloc)
        self.log('Connection initialized')
        # TODO add exceptions handler there (URL not found etc)
    
    def close_connection(self):
        """Close the HTTP connection (not the XMPP session!)"""
        self.log('Closing connection')
        self.connection.close()
        self.log('Connection closed')
        # TODO add execptions handler there

    def wrap_stanza_body(self, stanza, more_body=''):
        """Wrap the XMPP stanza with the <body> element (required for BOSH)"""
        if not stanza == '':
            return "<body rid='%s' sid='%s' %s xmlns='http://jabber.org/protocol/httpbind'>%s</body>" % (self.rid, self.sid, more_body, stanza)
        else:
            return "<body rid='%s' sid='%s' %s xmlns='http://jabber.org/protocol/httpbind' />" % (self.rid, self.sid, more_body)

    def send_request(self, xml_stanza):
        """
        Send a request to self.bosh_service.path using POST containing
        xml_stanza with self.headers.
        Returns the data contained in the response (only if status == 200)
        Returns False if status != 200
        """
        self.log('XML_STANZA:')
        self.log(xml_stanza)
        self.log('Sending the request')
        try:
            self.connection.request("POST", self.bosh_service.path, xml_stanza, self.headers)
        except AttributeError:
            raise ConnectionError
            return False
        self.rid += 1
        response = self.connection.getresponse()
        data = ''
        self.log('Response status code: %s' % response.status)
        if response.status == 200:
            data = response.read()
        else:
            self.log('Something wrong happened!')
            return False
            
        self.log('DATA:')
        self.log(data)
        return data
     def request_bosh_session(self):
        """
        Request a BOSH session according to
        http://xmpp.org/extensions/xep-0124.html#session-request
        Returns the new SID (str).
        This function also fill many fields of this BOSHClient object, such as:
            * sid
            * server_wait
            * server_auth_methods
        """
        self.log('Prepare to request BOSH session')
        
        xml_stanza = "<body rid='%s' xmlns='http://jabber.org/protocol/httpbind' to='%s' xml:lang='en' wait='60' hold='1' window='5' content='text/xml; charset=utf-8' ver='1.6' xmpp:version='1.0' xmlns:xmpp='urn:xmpp:xbosh'/>" % (self.rid, self.jid.host)
        data = self.send_request(xml_stanza)
      
        # This is XML. response_body contains the <body/> element of the
        # response.
        try:
            response_body = minidom.parseString(data).documentElement
        except TypeError:
            raise ConnectionError
            return 0;
        
        # Check if this there was a problem during the session request
        if response_body.getAttribute('type') == 'terminate':
            return 0;
        
        # Get the remote Session ID
        self.sid = response_body.getAttribute('sid')
        self.log('sid = %s' % self.sid)
        
        # Get the longest time (s) that the XMPP server will wait before
        # responding to any request.
        self.server_wait = response_body.getAttribute('wait')
        self.log('wait = %s' % self.server_wait)
        
        # Get the authid
        self.authid = response_body.getAttribute('authid')
        
        # Get the allowed authentication methods
        stream_features = response_body.firstChild
        auth_list = []
        try:
            mechanisms = stream_features.getElementsByTagNameNS('urn:ietf:params:xml:ns:xmpp-sasl', 'mechanisms')[0]
            if mechanisms.hasChildNodes():
                for child in mechanisms.childNodes:
                    auth_method = child.firstChild.data
                    auth_list.append(auth_method)
                    self.log('New AUTH method: %s' % auth_method)
            
                self.server_auth = auth_list
                
            else:
                self.log('The server didn\'t send the allowed authentication methods')
        except AttributeError:
            self.log('The server didn\'t send the allowed authentication methods')
            
            # FIXME: BIG PROBLEM THERE! AUTH METHOD MUSTN'T BE GUEST!
            auth_list = ['DIGEST-MD5']
            self.server_auth = auth_list
        
        #return self.sid
     
class JID:
    """
    Class built for ease to use JIDs
    
    >>> my_jid = JID('me@myserver.com')
    >>> print my_jid
    me@myserver.com
    >>> print my_jid.user
    me
    >>> print my_jid.host
    myserver.com
    >>> print my_jid.full_jid
    me@myserver.com
    """
    
    def __init__(self, jid, resource):
        """
        Initialize the JID object: cut the various par of the given string
        The JID must match the following form: user@domain
        So, DON'T provide the RESOURCE!
        """
        
        val = jid.split('@')
        self.user = val[0]
        self.host = val[1]
        self.resource = resource
        self.full_jid = jid
        self.jid_with_resource = '%s/%s' % (self.full_jid, self.resource)
        
    def __str__(self):
        """String representation for ease of use. Returns the full jid."""
        return self.full_jid
        
