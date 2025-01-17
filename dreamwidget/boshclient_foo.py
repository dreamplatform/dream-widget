
# Original source https://friendpaste.com/1R4PCcqaSWiBsveoiq3HSy
# Copied at 2012-11-12
# Modified to suit our needs

import httplib, sys, random
from urlparse import urlparse
from xml.dom import minidom


class BOSHClient:

    def __init__(self, jid, password, bosh_service, debug=False):
        """
        Initialize the client.
        You must specify the Jabber ID, the corresponding password and the URL
        of the BOSH service to connect to.
        """
        self.debug = debug
        self.connection = None

        self.jid = jid
        self.sid = None
        self.rid = None
        self.password = password
        self.bosh_service = urlparse(bosh_service)

        self.generate_rid()
        self.log('Init RID: %s' % self.rid)

        self.content_type = "text/xml; charset=utf-8"
        self.headers = {
            "Content-type": "text/plain; charset=UTF-8",
            "Accept": "text/xml",
        }

        self.server_auth = []

    def log(self, message):
        if self.debug:
          print '[DEBUG] ' + message

    def generate_rid(self):
        self.rid = random.randint(0, 10000000)

    def init_connection(self):
        self.log('Initializing connection to %s' % (self.bosh_service.netloc))
        self.connection = httplib.HTTPConnection(self.bosh_service.netloc)
        self.log('Connection initialized')
        # TODO add exceptions handler there (URL not found etc)

    def close_connection(self):
        self.log('Closing connection')
        self.connection.close()
        self.log('Connection closed')
        # TODO add execptions handler there

    def wrap_stanza_body(self, stanza, more_body=''):
        """Wrap the XMPP stanza with the <body> element (required for BOSH)"""
        return"<body rid='%s' sid='%s' %s xmlns='http://jabber.org/protocol/httpbind'>%s</body>" % (self.rid, self.sid, more_body, stanza)

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
        self.connection.request("POST", self.bosh_service.path, xml_stanza, self.headers)
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

        xml_stanza = "<body rid='%s' xmlns='http://jabber.org/protocol/httpbind' to='msg.dreamschool.fi' xml:lang='en' wait='60' hold='1' window='5' content='text/xml; charset=utf-8' ver='1.6' xmpp:version='1.0' xmlns:xmpp='urn:xmpp:xbosh'/>" % (self.rid)
        data = self.send_request(xml_stanza)
        if not data:
          return None

        # This is XML. response_body contains the <body/> element of the
        # response.
        response_body = minidom.parseString(data).documentElement

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

        return self.sid

    def authenticate_xmpp(self):
        """
        Authenticate the user to the XMPP server via the BOSH connection.
        You MUST have the following settings set:
            * self.sid
            * self.jid
            * self.password
            * self.rid
            * self.server_auth
        Note also that the connection MUST be opened (see self.init_connection).
        """

        self.log('Prepare the XMPP authentication')

        self.send_request(self.wrap_stanza_body('='))

        xml_stanza = "<body rid='%s' xmlns='http://jabber.org/protocol/httpbind' sid='%s'><auth xmlns='urn:ietf:params:xml:ns:xmpp-sasl' mechanism='DIGEST-MD5'/></body>" % (self.rid, self.sid)
        self.send_request(unicode(xml_stanza))


if __name__ == '__main__':
    USERNAME = sys.argv[1]
    PASSWORD = sys.argv[2]
    SERVICE = sys.argv[3]

    request_bosh_session(USERNAME, PASSWORD, SERVICE)

def request_bosh_session(username, password, service):
    c = BOSHClient(username, password, service, debug=True)
    c.init_connection()
    if c.request_bosh_session():
      c.authenticate_xmpp()
    c.close_connection()
    return {'jid': c.jid, 'sid': c.sid, 'rid': c.rid}

