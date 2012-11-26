{% load i18n %}
{% if BOSH_JID %}
(function(){

  var BOSH_SERVICE = '{{ BOSH_ENDPOINT }}';
  var BOSH_JID = '{{ BOSH_JID }}';
  var BOSH_SID = '{{ BOSH_SID }}';
  var BOSH_RID = '{{ BOSH_RID }}';
  var connection = null;

  connection = new Strophe.Connection(BOSH_SERVICE);

  connect();
  function connect() {
    connection.attach(BOSH_JID, BOSH_SID, BOSH_RID, onStatusChange);
  }

  function onStatusChange(status)
  {
    if (status == Strophe.Status.CONNECTING) {
      log('Strophe is connecting.');
    } else if (status == Strophe.Status.CONNFAIL) {
      log('Strophe failed to connect.');
      dream.notify('{% trans "Connection to Dream Messaging failed" %}', 'error');
    } else if (status == Strophe.Status.DISCONNECTING) {
      log('Strophe is disconnecting.');
    } else if (status == Strophe.Status.DISCONNECTED) {
      log('Strophe is disconnected.');
      connect();
    } else if (status == Strophe.Status.CONNECTED || status == Strophe.Status.ATTACHED) {
      log('Strophe is connected.');

      connection.addHandler(onMessage, null, 'message', null, null, null); 
      connection.send($pres().tree());
    }
    log(status);
  }

  function onMessage(msg) {
    var to = msg.getAttribute('to');
    var from = msg.getAttribute('from');
    var type = msg.getAttribute('type');
    var elems = msg.getElementsByTagName('body');

    log(msg);

    if (type == "chat" && elems.length > 0) {
      var body = elems[0];
      
      log('Message from ' + from + ': ' + Strophe.getText(body));
      dream.notify(Strophe.getText(body));
    }

    // we must return true to keep the handler alive.  
    // returning false would remove it after it finishes.
    return true;
  }

  function log(msg) {
    console.log(msg);
  }

  Strophe.log = function(level, error) {
    console.log(level, error);
  }

})();
{% else %}
// No BOSH session
{% endif %}
