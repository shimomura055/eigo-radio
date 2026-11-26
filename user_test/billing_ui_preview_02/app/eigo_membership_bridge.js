/* eigo_membership_bridge.js -- EigoHost.membership (v1) + the article-data fetch gate (G9). RELEASE-IOS-BILLING-MEMBERSHIP-01 Lane C, C5. iOS ONLY.
   Loaded by the iOS app build right after eigo_native_adapter.js (scripts/anchors.mjs, html-scripts). The Web / Android builds do not contain this file and never define EigoHost.membership.
   Active ONLY when (1) the adapter is in mode 'native' and (2) the binary has the native plugin `EigoMembership` (contract: plugins/eigo-native-player/js/membership_contract.mjs).
   Otherwise this file does nothing at all (no property, no DOM, fetch untouched).
   Authority: the native side. This file is a thin READ + user-operation bridge: there is NO function here that grants or changes an entitlement
   (no phase / trial / pick / ledger writer exists in the plugin either). Enforcement of playback, download, study, seek, auto-advance and remote commands is native (EigoAccessGate).
   The fetch gate below is the web-layer part of design G9: the body text / translation / study data of an article the user may not use is not fetched
   (network, offline JSON cache and localStorage copies all pass the same check because the gate sits above the adapter's fetch). Article titles, summaries, thumbnails and favourites
   come from the catalog and are never gated. The public article URLs themselves stay public (approved boundary, user original section 4-8-4). */
(function (root) {
  'use strict';
  var host = root.EigoHost;
  if (!host || host.mode !== 'native') return;
  var Cap = root.Capacitor, NAME = 'EigoMembership';
  var plugin = null;
  try { if (Cap && typeof Cap.isPluginAvailable === 'function' && Cap.isPluginAvailable(NAME) && typeof Cap.registerPlugin === 'function') plugin = Cap.registerPlugin(NAME); } catch (e) { plugin = null; }
  if (!plugin) return;   // Web / Android / an iOS binary without the plugin: nothing is defined

  var last = null;   // last state read from native (display + fallback only; never a source of authority)
  var subs = { accessChanged: [], accessDenied: [] };
  function diag(ev, data) { try { if (typeof host.diag === 'function') host.diag(ev, data || {}); } catch (e) { /* record only */ } }
  function emit(name, payload) { subs[name].slice().forEach(function (cb) { try { cb(payload); } catch (e) { diag('js.membership.listener_error', { name: name, msg: String(e && e.message) }); } }); }
  function call(method, args) {
    try { return Promise.resolve(args === undefined ? plugin[method]() : plugin[method](args)); } catch (e) { return Promise.reject(e); }
  }

  function getAccessState() {
    return call('getAccessState').then(function (s) { last = s || null; return last; });
  }
  function refreshAndNotify() {
    return getAccessState().then(function (s) { emit('accessChanged', s); return s; }, function (e) { diag('js.membership.state_error', { code: e && e.code }); });
  }
  function listen(name, cb) { try { var h = plugin.addListener(name, cb); if (h && h.catch) h.catch(function (e) { diag('js.membership.listen_error', { name: name, code: e && e.code }); }); } catch (e) { diag('js.membership.listen_error', { name: name }); } }
  listen('accessChanged', function () { refreshAndNotify(); });
  listen('accessDenied', function (d) { emit('accessDenied', d || {}); });

  var membership = {
    v: 1,
    // ---- read ----
    getAccessState: getAccessState,
    peek: function () { return last; },
    canAccess: function (slug, intent) { return call('canAccess', { slug: String(slug), intent: intent || 'start' }); },
    // ---- user operations (each maps 1:1 to something the user did; none of them can grant anything by itself) ----
    refreshProduct: function () { return call('refreshProduct'); },
    purchase: function () { return call('purchase'); },
    restore: function () { return call('restore'); },
    openManageSubscriptions: function () { return call('openManageSubscriptions'); },
    commitFreePick: function (slug) { return call('commitFreePick', { slug: String(slug) }); },
    markNoticeShown: function (kind) { return call('markNoticeShown', { kind: String(kind) }); },
    // ---- subscriptions (accessChanged -> new state, accessDenied -> {slug, reason, point}) ----
    on: function (name, cb) {
      if (!subs[name] || typeof cb !== 'function') throw new Error('EigoHost.membership.on: unknown event ' + name);
      subs[name].push(cb);
      return function () { var i = subs[name].indexOf(cb); if (i >= 0) subs[name].splice(i, 1); };
    }
  };
  // Usage-data consent (user decision 2026-11-26 USER_02 sec 1, plan 2). The native plugin `EigoMetrics` (RELEASE-IOS-FIREBASE-ANALYTICS-01 FN2) owns the stored choice and what is sent:
  // getConsent() -> {consent:'unanswered'|'granted'|'denied', available:boolean}, setConsent({value:'granted'|'denied'}). This file only forwards the user's own tap; when the plugin
  // is missing (or reports available=false) the UI shows nothing about consent. Nothing is sent while the answer is not 'granted' (native rule).
  var metrics = null;
  try { if (typeof Cap.isPluginAvailable === 'function' && Cap.isPluginAvailable('EigoMetrics')) metrics = Cap.registerPlugin('EigoMetrics'); } catch (e) { metrics = null; }
  if (metrics) {
    membership.getUsageConsent = function () {
      return Promise.resolve().then(function () { return metrics.getConsent(); }).then(function (r) {
        return { consent: (r && (r.consent === 'granted' || r.consent === 'denied')) ? r.consent : 'unanswered', available: !!(r && r.available === true) };
      });
    };
    membership.chooseUsageConsent = function (value) {
      if (value !== 'granted' && value !== 'denied') return Promise.reject(new Error('bad consent value'));
      return Promise.resolve().then(function () { return metrics.setConsent({ value: value }); });
    };
  }
  host.membership = membership;

  /* ---------------------------------------------------------------- G9: article data fetch gate */
  var DATA_RE = /\/([^\/?#]+)\/enduser\/data\/(?:article|sync_std|sync_adv)\.json(?:[?#]|$)/;
  function slugOfDataUrl(u) { var m = DATA_RE.exec(String(u || '')); if (!m) return null; try { return decodeURIComponent(m[1]); } catch (e) { return m[1]; } }
  // The review book (復習帳) stays usable in every membership state (user original 4-4): its cards are built from the saved items' article data. Audio of an unavailable article is still refused by the native gate.
  function inReviewContext() { try { return /^#\/review(?:[\/?]|$)/.test(root.location.hash || ''); } catch (e) { return false; } }
  function decideRead(slug) {
    if (inReviewContext()) return Promise.resolve(true);
    return membership.canAccess(slug, 'start').then(function (a) { return !!(a && a.allow); }, function () {
      var s = last;   // native advisory read failed: use the last known state; with no state at all the data is NOT released (never open by default)
      return !!(s && (s.phase !== 'free' || (s.today && s.today.pickSlug === slug)));
    });
  }
  function lockedError(slug) {
    var e = new Error('membership_locked: article data of ' + slug + ' is not available with the current plan');
    e.code = 'membership_locked'; e.slug = slug;
    return e;
  }
  function gateUrl(u, run) {
    var slug = slugOfDataUrl(u);
    if (!slug) return run();
    return decideRead(slug).then(function (ok) {
      if (!ok) { diag('js.membership.fetch_denied', { slug: slug }); emit('accessDenied', { slug: slug, reason: 'locked', point: 'fetch' }); return Promise.reject(lockedError(slug)); }   // the UI explains (state may have been stale)
      return run();
    });
  }
  if (typeof root.fetch === 'function') {
    var gatedBase = root.fetch.bind(root);
    root.fetch = function (input, init) {
      var u = typeof input === 'string' ? input : (input && typeof input.url === 'string' ? input.url : (input && input.href) || '');
      return gateUrl(u, function () { return gatedBase(input, init); });
    };
  }
  if (typeof host.jsonFetch === 'function') {   // the adapter's JSON cache entry point (network first, cache fallback) is gated too
    var jsonBase = host.jsonFetch;
    host.jsonFetch = function (input, init) {
      var u = typeof input === 'string' ? input : (input && input.url);
      return gateUrl(u, function () { return jsonBase(input, init); });
    };
  }
  host.membershipGate = { slugOfDataUrl: slugOfDataUrl, inReviewContext: inReviewContext };
  refreshAndNotify();   // first read (also lets the UI start from a known state)
})(typeof window !== 'undefined' ? window : globalThis);
