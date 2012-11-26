{% load i18n %}

/*
 * Dream library          DREAMLIB
 * Dream notification     DREAMNOTIFY
 * Dream messaging (XMPP) DREAMMSG
 *
 * Embdded libraries:
 *  Library:            Tag:
 *
 *  jQuery 1.7          JQUERY
 *  ColorBox v1.3.18    COLORBOX
 *  Strophe.js 1.0.2    STROPHE
 *
 *  Begin of library is marked as //JQUERY and end //END JQUERY, for example.
 *  Any changes made to embedded code is marked as //DREAM_CHANGE
 */

(function(){

  window.dream = new Object();
  var jQuery;
  var $;

  //JQUERY
  {% include "dreamwidget/dream/jquery-1.8.2.min.js" %}
  //END JQUERY

  // Sandbox jQuery
  $ = jQuery = window.jQuery;
  window.jQuery.noConflict(true);

  //COLORBOX
  //DREAM_CHANGE: colorbox = colorboxDream, cbox = cboxDream
  {% include "dreamwidget/dream/jquery.colorbox-1.3.20.1.min.js" %}
  //END COLORBOX

  {% comment 'NOTIFICATION API' %}
  //DREAMNOTIFY
  {% include "dreamwidget/dream/dream-notify.js" %}
  //END DREAMNOTIFY

  //STROPHE
  {% include "dreamwidget/dream/strophe-1.0.2.min.js" %}
  //END STROPHE

  //DREAMMSG
  {% include "dreamwidget/dream/dream-msg.js" %}
  //END DREAMMSG
  {% endcomment %}

  //DREAMLIB
  $(document).ready(function(){
    var userNavTimeout, userNavToggle = false;

    // Append dreamwidget markup
    $("body").append(
      $('{% spaceless %}{% include "dreamwidget/widget.html" %}{% endspaceless %}')
    );

    {% comment 'NOTIFICATION API' %}
    // Toggle notifications
    $('.js-dreamwidget-toggle-notifications').on('click.dream.dreamWidgetNav', function () {
      dream.notifications.toggleHistory();
    });
    {% endcomment %}

    // Toggle user nav on click
    $('.js-dreamwidget-toggle-user-nav').on('click.dream.dreamWidgetNav', function () {
      if(userNavToggle) {
        userNavToggle = false;
        $(this).removeClass('active');
        $('#dreamwidget .dreamwidget-user-nav').removeClass('active');
      } else {
        userNavToggle = true;
        $(this).addClass('active');
        $('#dreamwidget .dreamwidget-user-nav').addClass('active');
      }
    });
    
    // Open user nav
    $('.js-dreamwidget-toggle-user-nav, .dreamwidget-user-nav').on('mouseenter.dream.dreamWidgetNav', function () {
      window.clearTimeout(userNavTimeout);
      $('.js-dreamwidget-toggle-user-nav').addClass('active');
      $('#dreamwidget .dreamwidget-user-nav').addClass('active');
    });

    // Close user nav
    $('.js-dreamwidget-toggle-user-nav, .dreamwidget-user-nav').on('mouseleave.dream.dreamWidgetNav', function () {
      userNavTimeout = window.setTimeout(function () {
        userNavToggle = false;
        $('.js-dreamwidget-toggle-user-nav').removeClass('active');
        $('#dreamwidget .dreamwidget-user-nav').removeClass('active');
      }, 200);
    });

    // Bind colorbox
    $('.js-dreamwidget-open-dialog').colorboxDream({
      transition: 'elastic',
      iframe: true,
      fastIframe: false,
      scrolling: false,
      innerWidth: '500px',
      innerHeight: '550px',
      initialWidth: '100px',
      initialHeight: '100px',
      opacity: 0.5,
      onLoad: function() {
        $('#cboxDreamClose').hide();
      },
      onComplete: function() {
        $('#cboxDreamClose').fadeIn(400);
      }
    });

    openDreamDialog = function(type){
      if (type == "settings"){
       dream.openURLInDialog("{{ DREAMUSERDB_DOMAIN }}/accounts/");
      }
      else if (type == "messaging"){
        dream.openURLInDialog("{{ DREAMDESKTOP_MSG_DOMAIN }}/dialog/");
      }
    }

    dream.openURLInDialog = function(url){
      $.colorboxDream({
        transition: 'elastic',
        iframe: true,
        fastIframe: false,
        scrolling: false,
        innerWidth: '500px',
        innerHeight: '550px',
        initialWidth: '100px',
        initialHeight: '100px',
        opacity: 0.5,
        href: url,
        onLoad: function() {
          $('#cboxDreamClose').hide();
        },
        onComplete: function() {
          $('#cboxDreamClose').fadeIn(400);
        },
        onClosed: function() {
          dream.maybeRedirect();
        }
      });
    }

    dream.maybeRedirect = function() {
      if ($('body').hasClass('redirect')) {
        window.location = "{{ DREAMDESKTOP_DOMAIN }}";
      }
    }
    
    // Append required CSS
    $('head')
    .append('<link rel="stylesheet" type="text/css" href="{{ DREAMDESKTOP_DOMAIN }}/static/dreamwidget/dream/dream-header.css" />')
    .append('<link rel="stylesheet" type="text/css" href="{{ DREAMDESKTOP_DOMAIN }}/static/dreamwidget/dream/dream-colorbox.css" />')
    .append('<link rel="stylesheet" type="text/css" href="https://fonts.googleapis.com/css?family=Open+Sans:400,400italic,600,600italic,700,700italic" />');

  });

  //END DREAMLIB

})();
