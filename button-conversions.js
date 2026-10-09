// Measure outbound button clicks on this website, not donations or installs.
(function () {
  'use strict';
  if (window.paiButtonConversionsReady) return;
  window.paiButtonConversionsReady = true;

  var storeLinks = {
    claims: 'https://apps.microsoft.com/detail/9P255VXPD5B4',
    legal: 'https://apps.microsoft.com/detail/9NP4XL1MRXP8'
  };

  function ensureGoogleAdsTag() {
    if (typeof window.gtag === 'function') return;
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag('js', new Date());
    window.gtag('config', 'AW-18465563654');
    if (!document.querySelector('script[src*="googletagmanager.com/gtag/js"]')) {
      var tag = document.createElement('script');
      tag.async = true;
      tag.src = 'https://www.googletagmanager.com/gtag/js?id=AW-18465563654';
      document.head.appendChild(tag);
    }
  }

  ensureGoogleAdsTag();

  function addDownloadBar() {
    if (document.querySelector('[data-pai-download-bar]')) return;

    var style = document.createElement('style');
    style.textContent = [
      '.pai-download-bar{position:fixed;z-index:2147483000;left:16px;right:16px;bottom:16px;display:flex;align-items:center;justify-content:center;gap:14px;max-width:980px;margin:auto;padding:14px 16px;background:#07182c;color:#fff;border:1px solid #4f7ca8;border-radius:14px;box-shadow:0 14px 38px rgba(0,0,0,.32);font-family:Segoe UI,Arial,sans-serif}',
      '.pai-download-bar__copy{min-width:190px;line-height:1.2}',
      '.pai-download-bar__copy strong{display:block;font-size:16px;color:#fff}',
      '.pai-download-bar__copy span{display:block;margin-top:4px;font-size:12px;color:#c8d7e8}',
      '.pai-download-bar__actions{display:flex;gap:10px;flex-wrap:wrap;justify-content:center}',
      '.pai-download-bar__button{display:inline-flex;align-items:center;justify-content:center;min-height:44px;padding:0 17px;border-radius:8px;background:#fff;color:#07182c!important;text-decoration:none!important;font-weight:750;font-size:14px;line-height:1.15;border:2px solid #fff}',
      '.pai-download-bar__button:hover,.pai-download-bar__button:focus{background:#ffd86b;border-color:#ffd86b;color:#07182c!important}',
      '.pai-download-bar__button:focus-visible{outline:3px solid #7dd3fc;outline-offset:3px}',
      '.pai-download-spacer{height:90px}',
      '@media(max-width:720px){.pai-download-bar{left:8px;right:8px;bottom:8px;display:block;padding:11px}.pai-download-bar__copy{text-align:center;margin-bottom:9px}.pai-download-bar__actions{gap:7px}.pai-download-bar__button{flex:1 1 145px;padding:0 10px;font-size:13px}.pai-download-spacer{height:190px}}',
      '@media(prefers-reduced-motion:reduce){.pai-download-bar *{scroll-behavior:auto!important}}',
      '@media print{.pai-download-bar{display:none!important}}'
    ].join('');
    document.head.appendChild(style);

    var bar = document.createElement('aside');
    bar.className = 'pai-download-bar';
    bar.setAttribute('data-pai-download-bar', 'true');
    bar.setAttribute('aria-label', 'Download PAi software from Microsoft Store');
    bar.innerHTML =
      '<div class="pai-download-bar__copy"><strong>Put your records to work</strong><span>Free Windows downloads from Microsoft Store</span></div>' +
      '<div class="pai-download-bar__actions">' +
      '<a class="pai-download-bar__button" href="' + storeLinks.claims + '" target="_blank" rel="noopener noreferrer" aria-label="Download PAi Claims from Microsoft Store">Download PAi Claims</a>' +
      '<a class="pai-download-bar__button" href="' + storeLinks.legal + '" target="_blank" rel="noopener noreferrer" aria-label="Download PAi Legal from Microsoft Store">Download PAi Legal</a>' +
      '</div>';
    var spacer = document.createElement('div');
    spacer.className = 'pai-download-spacer';
    spacer.setAttribute('aria-hidden', 'true');
    document.body.appendChild(spacer);
    document.body.appendChild(bar);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', addDownloadBar, {once: true});
  } else {
    addDownloadBar();
  }

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
