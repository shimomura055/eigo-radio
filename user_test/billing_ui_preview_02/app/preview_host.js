/* preview_host.js -- DISPLAY-ONLY stand-in for the iOS adapter (eigo_native_adapter.js), used ONLY by the public membership UI preview. NOT part of the app build; the real adapter is not published.
   What it reproduces (same DOM / wording as the app, display only): EigoHost.offline (the saved-article management list and the download button states the common webapp draws), the saved badge on list cards,
   the bundle-URL -> public data mapping, a silent audio stub (nothing is ever played), the online / offline switch. What it does NOT do: any download, any file, any audio, any native behaviour.
   Differences from the real adapter are listed in PREVIEW_MANIFEST.json (display_only_differences). */
(function (root) {
  'use strict';
  var doc = root.document, q = new URLSearchParams(root.location.search);
  var PAGES_ROOT = (root.EIGO_HOST_CONFIG && root.EIGO_HOST_CONFIG.pagesRoot) || 'https://shimomura055.github.io/eigo-radio/user_test/';
  var PAGES_BASE = (root.EIGO_HOST_CONFIG && root.EIGO_HOST_CONFIG.pagesBase) || (PAGES_ROOT + 'webapp_proto_01/');
  var APP_BASE = new root.URL('./', root.location.href).href, APP_PARENT = new root.URL('../', root.location.href).href;

  /* ---- URL mapping (same idea as the app's urlMap): data/* -> the public webapp data; ../<slug>/... -> the public article data. Nothing is copied into the preview. ---- */
  var realFetch = root.fetch.bind(root);
  root.fetch = function (input, init) {
    var u = typeof input === 'string' ? input : (input && input.url) || '';
    try {
      var abs = new root.URL(u, root.location.href).href;
      if (abs.indexOf(APP_BASE + 'data/') === 0) return realFetch(PAGES_BASE + abs.slice(APP_BASE.length), init);
      if (abs.indexOf(APP_PARENT) === 0 && abs.indexOf(APP_BASE) !== 0) return realFetch(PAGES_ROOT + abs.slice(APP_PARENT.length), init);
    } catch (e) { /* fall through */ }
    return realFetch(input, init);
  };

  /* ---- <img> thumbnails: same mapping as the app's adapter (imgMapper): an <img src> relative to the bundle (../<slug>/enduser/thumb.png) is read from the public article folder.
     Without this the card thumbnails of the preview stayed empty colour boxes (B4 defect N1: the preview mapped fetch() only). ---- */
  function mapImg(img) {
    try {
      var s = img.getAttribute && img.getAttribute('src'); if (!s) return;
      var abs = new root.URL(s, root.location.href).href;
      if (abs.indexOf(APP_PARENT) === 0 && abs.indexOf(APP_BASE) !== 0) img.setAttribute('src', PAGES_ROOT + abs.slice(APP_PARENT.length));
      else if (abs.indexOf(APP_BASE + 'data/') === 0) img.setAttribute('src', PAGES_BASE + abs.slice(APP_BASE.length));
    } catch (e) { /* fall through unmapped */ }
  }
  (function imgMapper() {
    if (!root.MutationObserver) return;
    function scan(n) { if (n.nodeType !== 1) return; if (n.tagName === 'IMG') mapImg(n); var l = n.querySelectorAll ? n.querySelectorAll('img') : []; for (var i = 0; i < l.length; i++) mapImg(l[i]); }
    new root.MutationObserver(function (recs) { recs.forEach(function (r) { [].forEach.call(r.addedNodes, scan); }); }).observe(doc.documentElement, { childList: true, subtree: true });
  })();

  /* ---- legal links (B6 sec 8, display only): the app links to the official pages <pagesRoot>../<key>/ (e.g. https://shimomura055.github.io/eigo-radio/privacy/). In the preview those are shown from the
     review copies under <pagesRoot>legal_preview_01/<key>.html (privacy / terms / tokushoho / support). The real app's official URLs are not changed. ---- */
  var LEGAL_KEYS = ['privacy', 'terms', 'tokushoho', 'support'];
  function mapLegal(a) {
    try {
      var h = a.getAttribute && a.getAttribute('href'); if (!h || h.charAt(0) === '#') return;
      var u = new root.URL(h, root.location.href), m = /\/(privacy|terms|tokushoho|support)\/?$/.exec(u.pathname);
      if (!m || LEGAL_KEYS.indexOf(m[1]) < 0) return;
      a.setAttribute('href', PAGES_ROOT + 'legal_preview_01/' + m[1] + '.html');
    } catch (e) { /* leave as is */ }
  }
  (function legalMapper() {
    if (!root.MutationObserver) return;
    function scan(n) { if (n.nodeType !== 1) return; if (n.tagName === 'A') mapLegal(n); var l = n.querySelectorAll ? n.querySelectorAll('a[href]') : []; for (var i = 0; i < l.length; i++) mapLegal(l[i]); }
    new root.MutationObserver(function (recs) { recs.forEach(function (r) { [].forEach.call(r.addedNodes, scan); }); }).observe(doc.documentElement, { childList: true, subtree: true });
    doc.addEventListener('click', function (e) { var a = e.target && e.target.closest ? e.target.closest('a[href]') : null; if (a) mapLegal(a); }, true);
  })();

  /* ---- silent audio stub: the common webapp's media elements never load or play anything ---- */
  var HM = root.HTMLMediaElement && root.HTMLMediaElement.prototype;
  if (HM) {
    HM.load = function () { };
    HM.play = function () { var el = this; try { Object.defineProperty(el, 'paused', { configurable: true, get: function () { return false; } }); } catch (e) { /* */ } try { el.dispatchEvent(new root.Event('play')); el.dispatchEvent(new root.Event('playing')); } catch (e) { /* */ } return Promise.resolve(); };
    HM.pause = function () { var el = this; try { Object.defineProperty(el, 'paused', { configurable: true, get: function () { return true; } }); } catch (e) { /* */ } try { el.dispatchEvent(new root.Event('pause')); } catch (e) { /* */ } };
  }

  /* ---- online / offline (the panel switches it live; the page also starts offline with ?online=0) ---- */
  var online = q.get('online') !== '0';
  try { Object.defineProperty(root.navigator, 'onLine', { configurable: true, get: function () { return online; } }); } catch (e) { /* */ }
  function setOnline(v) { online = !!v; try { root.dispatchEvent(new root.Event(online ? 'online' : 'offline')); } catch (e) { /* */ } notify(null); decorateSoon(); }

  /* ---- saved articles (display table): slugs passed by the panel (?saved=a,b) ---- */
  var saved = {}; (q.get('saved') || '').split(',').forEach(function (s) { if (s) saved[s] = 'saved'; });
  var limit = 524288000;
  function catalog() { try { return root.__WUL.ST.cat; } catch (e) { return null; } }
  function titleOf(slug) { var c = catalog(), l = c ? (c.items || []).concat(c.unlisted_items || []) : []; for (var i = 0; i < l.length; i++) if (l[i].slug === slug) return l[i].title_ja || slug; return slug; }
  function notify(slug) { try { root.dispatchEvent(new root.CustomEvent('eigo-offline-change', { detail: { slug: slug || null } })); } catch (e) { /* */ } }
  function state(slug) { var st = saved[slug]; return st === 'saved' ? { status: 'saved', online: online } : (st === 'busy' ? { status: 'busy', pct: 40, online: online } : { status: 'none', online: online }); }
  function summary() {
    var items = Object.keys(saved).map(function (s) { return { slug: s, title: titleOf(s), status: saved[s], bytes: 11400000 }; });
    return { loaded: true, online: online, usedBytes: items.length * 11400000, limitBytes: limit, items: items };
  }
  var host = root.EigoHost = root.EigoHost || {};
  host.mode = 'native'; host.v = 1;
  host.diag = function () { };
  Object.defineProperty(host, 'audioEl', { configurable: true, get: function () { return doc.getElementById('aud'); } });
  host.offline = {
    v: 1, state: state, touch: function () { }, refresh: function () { },
    start: function (slug) { if (!online) return; saved[slug] = 'busy'; notify(slug); root.setTimeout(function () { saved[slug] = 'saved'; notify(slug); decorateSoon(); }, 900); },
    remove: function (slug) { delete saved[slug]; notify(slug); decorateSoon(); },
    summary: summary, setLimit: function (b) { limit = b; notify(null); }, shareLog: function () { }
  };

  /* ---- saved badge on list cards (same wording and place as the app: a chip at the end of the chip row) ---- */
  var dTimer = 0;
  function decorateSoon() { if (dTimer || !doc.body) return; dTimer = root.setTimeout(function () { dTimer = 0; decorateCards(); }, 60); }
  function decorateCards() {
    try {
      [].forEach.call(doc.querySelectorAll('.card[data-open]'), function (c) {
        var slug = c.getAttribute('data-open'), s = state(slug), mk = c.querySelector('[data-eigo-saved]'), want = s.status === 'saved' ? '保存済' : '';
        if (!want) { if (mk) mk.remove(); return; }
        if (mk) return;
        mk = doc.createElement('span'); mk.setAttribute('data-eigo-saved', '1'); mk.textContent = want;
        mk.style.cssText = 'display:inline-block;margin:0;padding:1px 9px;border-radius:8px;background:#0a7a3d;color:#fff;font:11px/18px sans-serif;font-weight:700;white-space:nowrap;line-height:inherit';
        var chips = c.querySelector('.chips'); if (chips) chips.appendChild(mk); else { var h = c.querySelector('h4'); if (h && h.parentNode) h.parentNode.insertBefore(mk, h.nextSibling); }
      });
    } catch (e) { /* cosmetic */ }
  }
  function initUi() {
    var view = doc.getElementById('view');
    if (view && root.MutationObserver) new root.MutationObserver(function () { decorateSoon(); }).observe(view, { childList: true, subtree: true });
    root.addEventListener('hashchange', decorateSoon);
  }
  if (doc.body) initUi(); else doc.addEventListener('DOMContentLoaded', initUi);
  try { if (q.get('tut') !== '1') root.localStorage.setItem('wut01.tutorial_done', 'true'); } catch (e) { /* */ }
  root.__PVHost = { setOnline: setOnline, setSaved: function (slugs) { saved = {}; (slugs || []).forEach(function (s) { saved[s] = 'saved'; }); notify(null); decorateSoon(); }, savedSlugs: function () { return Object.keys(saved); } };
})(window);
