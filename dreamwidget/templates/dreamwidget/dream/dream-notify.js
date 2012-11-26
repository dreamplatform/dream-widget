{% load i18n %}
// Initialization
dream.notifications = {};
dream.notifications.closeDelay = 5000;
dream.notifications.closeDelayAfterHover = 5000;
dream.notifications.types = ['notify', 'error', 'success'];
dream.notifications.visibility = 'visible';
dream.notifications.historyToggle = false;

// Page Visibility API + fallback
/*! http://mths.be/visibility v1.0.5 by @mathias */
;(function(g,h,$,b){var e,i,f='onfocusin' in h&&'hasFocus' in h?'focusin focusout':'focus blur',d=['','moz','ms','o','webkit'],c=$.support,a=$.event;while((i=e=d.pop())!=b){i=(e?e+'H':'h')+'idden';if(c.pageVisibility=typeof h[i]=='boolean'){f=e+'visibilitychange';break}}$(/blur$/.test(f)?g:h).on(f,function(m){var l=m.type,j=m.originalEvent,k=j.toElement;if(!/^focus./.test(l)||(k==b&&j.fromElement==b&&j.relatedTarget==b)){a.trigger((i&&h[i]||/^(?:blur|focusout)$/.test(l)?'hide':'show')+'.visibility')}})}(this,document,jQuery));

// CSS
$('head').append('<link rel="stylesheet" href="{{ DREAMDESKTOP_DOMAIN }}/static/dreamwidget/dream/dream-notify.css" />');

/**
@function notify Displays a notification for the user and hides it after a timeout
@param {String} content - string containing the plaintext content of the notification box
@param {optional String} type - type of the notification box, defaults to first defined type
@param {optional Function} callback - function to be called when user clicks the notification
*/
dream.notify = function(content, type, callback) {
  // Notification object
  var $notification = $('<div class="dream-notification"></div>');
  $notification[0].appendChild(document.createTextNode(content));

  // Callback on click
  if( typeof callback !== 'undefined' ) {
    $notification.addClass('dream-notification-clickable');
    $notification.on('click.dream.dreamNotifyCallback', callback);
  }

  // Type class
  if( typeof type !== 'undefined' && $.inArray(type, dream.notifications.types) != -1 ) {
    $notification.addClass('dream-notification-' + type);
  } else {
    $notification.addClass('dream-notification-' + dream.notifications.types[0]);
  }

  // (re)Start close timeout
  if( dream.notifications.visibility == 'visible' ) {
    dream.notifications.hideAfter(dream.notifications.closeDelay);
  }

  // Prepend notification
  dream.notifications.list.prepend($notification);

  // Show notification container
  dream.notifications.container.fadeIn(200);
};

// Toggle history
dream.notifications.toggleHistory = function() {
  if( dream.notifications.historyToggle ) {
    dream.notifications.historyToggle = false;
    $('.js-dreamwidget-toggle-notifications').removeClass('active');
    dream.notifications.container.fadeOut(100, function() {
      dream.notifications.container.find('.dream-notification').hide();
    });
  } else {
    dream.notifications.historyToggle = true;
    window.clearTimeout(dream.notifications.timeout);
    $('.js-dreamwidget-toggle-notifications').addClass('active');
    dream.notifications.container.find('.dream-notification').show();
    dream.notifications.container.fadeIn(100);
  }
};

// Hider helper
dream.notifications.hideAfter = function(delay) {
  window.clearTimeout(dream.notifications.timeout);
  if( ! dream.notifications.historyToggle ) {
    dream.notifications.timeout = window.setTimeout(function() {
      dream.notifications.container.fadeOut(200, function() {
        dream.notifications.container.find('.dream-notification').hide();
      });
    }, delay);
  }
};

// Handle page visibility
$(document).on({
  'show': function() {
    dream.notifications.visibility = 'visible';
    dream.notifications.hideAfter(dream.notifications.closeDelay);
  },
  'hide': function() {
    dream.notifications.visibility = 'hidden';
  }
});

// Prepend notification container
$(function() {
  var $closebutton;
  dream.notifications.container = $('<div id="dream-notifications"></div>').hide();
  $closebutton = $('<span id="dream-notifications-close"></span>');
  dream.notifications.list = $('<div id="dream-notifications-list"><div class="dream-notification dream-notification-initial">{% trans "You have no notifications right now" %}</div></div>');
  dream.notifications.container.append($closebutton, dream.notifications.list);
  $('body').prepend(dream.notifications.container);

  // Pause close timeout on hover
  dream.notifications.container.mouseenter(function() {
      window.clearTimeout(dream.notifications.timeout);
  });
  dream.notifications.container.mouseleave(function() {
      dream.notifications.hideAfter(dream.notifications.closeDelayAfterHover);
  });

  // Close button
  $closebutton.on('click.dream.dreamNotifyClose', function() {
    window.clearTimeout(dream.notifications.timeout);
    dream.notifications.historyToggle = false;
    $('.js-dreamwidget-toggle-notifications').removeClass('active');
    dream.notifications.container.fadeOut(100, function() {
      dream.notifications.container.find('.dream-notification').hide();
    });
  });
});
