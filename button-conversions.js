// Measure outbound button clicks on this website, not donations or installs.
(function () {
  'use strict';
  if (window.paiButtonConversionsReady) return;
  window.paiButtonConversionsReady = true;
  document.addEventListener('click', function (event) {
    if (event.defaultPrevented || event.button !== 0) return;
    var link = event.target && event.target.closest ? event.target.closest('a[href]') : null;
    if (!link) return;
    var destination;
    try { destination = new URL(link.href, document.baseURI); } catch (_) { return; }
    if (destination.protocol !== 'https:') return;
    var label;
    if (destination.hostname === 'apps.microsoft.com' && /^\/detail\/[a-z0-9]+\/?$/i.test(destination.pathname)) {
      label = 'wtiPCLiztYAdEIbIiOVE';
    } else if (destination.hostname === 'www.zeffy.com' && destination.pathname === '/en-US/donation-form/donate-to-change-lives-23839') {
      label = 'V2rGCKuikYcdEIbIiOVE';
    }
    if (!label || typeof window.gtag !== 'function') return;
    var hit = {send_to: 'AW-18465563654/' + label};
    var sameTab = (!link.target || link.target === '_self') && !event.ctrlKey && !event.metaKey && !event.shiftKey && !event.altKey;
    if (sameTab) {
      event.preventDefault();
      var navigated = false;
      var navigate = function () {
        if (!navigated) { navigated = true; window.location.assign(link.href); }
      };
      hit.event_callback = navigate;
      hit.event_timeout = 1000;
      window.setTimeout(navigate, 1000);
    }
    try { window.gtag('event', 'conversion', hit); } catch (_) {
      if (sameTab) navigate();
    }
  });
}());
