/* preview_native.js -- DISPLAY-ONLY stand-in for the native side, used ONLY by the public membership UI preview (scripts/build_preview_public.mjs). NOT part of the app build.
   It does not decide anything about real permissions: it holds a small STATE TABLE chosen by the preview panel and answers the same plugin calls the app's bridge makes
   (EigoMembership / EigoMetrics contract) so the REAL UI code (eigo_membership_bridge/text/ui + the common webapp) can be operated in a browser. No store, no Keychain, no clock rules, no audio.
   The state is chosen by the URL query of the app frame (scn=...), set by the panel (shell.js). Everything is in memory: a reload is a fresh start of that state. */
(function (root) {
  'use strict';
  var q = new URLSearchParams(root.location.search);
  var DAY = 86400;
  var T0 = Date.UTC(2026, 11, 5, 6, 0, 0) / 1000;                 // first launch of the example trial: 2026-12-05 15:00 JST
  var TRIAL_END = Date.UTC(2026, 11, 12, 15, 0, 0) / 1000;        // 2026-12-13 00:00 JST = end of the 8th calendar day
  var SCN = q.get('scn') || 'trial';
  var dayN = Math.min(8, Math.max(1, parseInt(q.get('day') || '5', 10) || 5));
  var S = {   // the display state table (mutated only by the user's own taps in the preview)
    scn: SCN, phase: 'trial', paidCancelled: false, pick: q.get('pick') || null, popupDue: 'none', firstDue: q.get('first') === '1', trialDaysLeft: 0, paidExpiresAt: null,
    purchaseState: 'idle', product: q.get('product') === 'fail' ? { available: false, displayPrice: null, periodText: null, reason: 'not_found' } : { available: true, displayPrice: '¥490', periodText: '1か月', periodValue: 1, periodUnit: 'month', currencyCode: 'JPY', reason: null },
    buy: q.get('buy') || 'success', restore: q.get('restore') || 'found', shown: {}, consent: q.get('consent') || 'unanswered'
  };
  function setScn(scn) {
    S.scn = scn;
    S.paidCancelled = false; S.paidExpiresAt = null; S.popupDue = 'none';
    if (scn === 'trial') { S.phase = 'trial'; S.trialDaysLeft = 9 - dayN; }
    else if (scn === 'trial_end') { S.phase = 'free'; S.popupDue = S.shown.trial_end ? 'none' : 'trial_end'; }
    else if (scn === 'free_unpicked') { S.phase = 'free'; }
    else if (scn === 'free_picked') { S.phase = 'free'; }
    else if (scn === 'periodic') { S.phase = 'free'; S.popupDue = S.shown.periodic ? 'none' : 'periodic'; }
    else if (scn === 'paid' || scn === 'canceled') { S.phase = 'paid'; S.paidCancelled = scn === 'canceled'; S.paidExpiresAt = T0 + 35 * DAY; }
    else if (scn === 'post_paid') { S.phase = 'free'; S.popupDue = S.shown.paid_end ? 'none' : 'paid_end'; }
    if (S.phase === 'free' && scn !== 'free_picked') S.pick = null;
  }
  setScn(SCN);
  if (SCN === 'free_picked' && !S.pick) S.pick = firstSlug();
  function firstSlug() { try { var c = root.__WUL.ST.cat; return ((c.items || [])[0] || {}).slug || null; } catch (e) { return null; } }
  function dayKey() { return new Date((TRIAL_END + DAY) * 1000).toISOString().slice(0, 10); }
  function view() {
    return { phase: S.phase, paidCancelled: S.paidCancelled, billingGrace: false, paidExpiresAt: S.paidExpiresAt, trialEndsAt: TRIAL_END, trialDaysLeft: S.phase === 'trial' ? S.trialDaysLeft : 0, graceEndsAt: null,
      today: { dayKey: dayKey(), pickSlug: S.phase === 'free' ? S.pick : null }, popupDue: S.popupDue, firstLaunchNoticeDue: S.phase === 'trial' && S.firstDue, storeSynced: true, degraded: false, clockAnomaly: false,
      product: JSON.parse(JSON.stringify(S.product)), purchaseState: S.purchaseState };
  }
  var listeners = {};
  function emit(n, d) { (listeners[n] || []).slice().forEach(function (cb) { try { cb(d || {}); } catch (e) { /* */ } }); }
  function later(v, ms) { return new Promise(function (res) { root.setTimeout(function () { res(v); }, ms || 0); }); }
  function showManageStandIn() {
    var d = root.document; if (!d || !d.body || d.querySelector('[data-pv-manage]')) return;
    var w = d.createElement('div'); w.setAttribute('data-pv-manage', '1'); w.setAttribute('role', 'dialog'); w.setAttribute('aria-modal', 'true');
    w.style.cssText = 'position:fixed;inset:0;z-index:2147483000;background:rgba(16,40,94,.45);display:flex;align-items:center;justify-content:center;padding:20px;font-family:sans-serif';
    var c = d.createElement('div'); c.style.cssText = 'background:#fff;border-radius:16px;padding:20px 18px;max-width:340px;width:100%;box-shadow:0 8px 30px rgba(0,0,0,.25);color:#10285e';
    c.innerHTML = '<div style="font-size:12px;font-weight:700;color:#5b6b8c;margin-bottom:6px">プレビュー専用の表示</div>' +
      '<h3 style="margin:0 0 8px;font-size:17px">実アプリではAppleの契約管理画面が開きます</h3>' +
      '<p style="margin:0 0 8px;font-size:14px;line-height:1.6">プレビューでは開けないため、この表示のみです。契約内容を確認しただけでは、会員の状態は変わりません。</p>' +
      '<p style="margin:0 0 14px;font-size:13px;line-height:1.6;color:#5b6b8c">解約したあとの見え方(自動更新停止済み)は、状態パネルで「有料会員(自動更新停止済み)」を選ぶと確認できます。</p>';
    var b = d.createElement('button'); b.type = 'button'; b.textContent = '閉じる'; b.setAttribute('data-pv-manage-close', '1');
    b.style.cssText = 'width:100%;min-height:46px;border:0;border-radius:12px;background:#1d4fd8;color:#fff;font-size:16px;font-weight:700;cursor:pointer';
    b.addEventListener('click', function () { if (w.parentNode) w.parentNode.removeChild(w); });
    c.appendChild(b); w.appendChild(c); d.body.appendChild(w);
  }
  var Membership = {
    getAccessState: function () { return Promise.resolve(view()); },
    canAccess: function (a) { var allow = S.phase !== 'free' || (!!S.pick && S.pick === a.slug); return Promise.resolve({ allow: allow, reason: allow ? 'ok' : (S.pick ? 'locked' : 'select_required') }); },
    refreshProduct: function () { return later(S.product.available ? { available: true, displayPrice: S.product.displayPrice, periodText: S.product.periodText } : { available: false, reason: S.product.reason }, 250); },
    purchase: function () {
      S.purchaseState = 'busy';
      return later(null, 700).then(function () {
        var o = S.buy;
        if (o === 'success') { S.phase = 'paid'; S.paidCancelled = false; S.paidExpiresAt = TRIAL_END + 30 * DAY; S.popupDue = 'none'; S.pick = null; S.purchaseState = 'idle'; emit('accessChanged'); return { result: 'success' }; }
        S.purchaseState = o === 'pending' ? 'pending' : 'idle';
        if (o === 'failed') return { result: 'failed', reason: 'preview' };
        return { result: o };   // cancelled / pending / unverified
      });
    },
    restore: function () {
      return later(null, 400).then(function () {
        if (S.restore === 'found') { S.phase = 'paid'; S.paidCancelled = false; S.paidExpiresAt = TRIAL_END + 20 * DAY; S.popupDue = 'none'; emit('accessChanged'); return { result: 'done', refreshed: true }; }
        if (S.restore === 'none') return { result: 'done', refreshed: true };
        return { result: 'failed', reason: 'network' };
      });
    },
    // The real app opens Apple's subscription management screen here (system UI: it cannot be opened in a browser). The preview shows a clearly marked stand-in notice instead, so the tap is not silent (USER_05 sec 3). Preview only: not part of the app build.
    openManageSubscriptions: function () { showManageStandIn(); return Promise.resolve({ opened: true }); },
    commitFreePick: function (a) {
      if (S.phase !== 'free') return Promise.resolve({ ok: false, code: 'not_needed' });
      if (S.pick) return Promise.resolve({ ok: false, code: 'already_picked' });
      S.pick = String(a.slug); emit('accessChanged'); return Promise.resolve({ ok: true, code: 'ok' });
    },
    markNoticeShown: function (a) {
      var k = String(a.kind);
      if (k === 'first_launch') { S.firstDue = false; S.shown.first_launch = true; }
      else { S.shown[k] = true; if (S.popupDue === k) S.popupDue = 'none'; }
      emit('accessChanged'); return Promise.resolve({ recorded: true });
    },
    addListener: function (n, cb) { (listeners[n] = listeners[n] || []).push(cb); return Promise.resolve({ remove: function () { var i = (listeners[n] || []).indexOf(cb); if (i >= 0) listeners[n].splice(i, 1); } }); }
  };
  var Metrics = {   // display-only: holds the answer in memory; nothing is ever sent anywhere
    getConsent: function () { return Promise.resolve({ consent: S.consent, available: true }); },
    setConsent: function (a) { if (a && (a.value === 'granted' || a.value === 'denied')) S.consent = a.value; return Promise.resolve({}); },
    addListener: function () { return Promise.resolve({ remove: function () { } }); }
  };
  var hasMetrics = S.consent !== 'none';
  root.Capacitor = {
    isNativePlatform: function () { return true; },
    isPluginAvailable: function (n) { return n === 'EigoMembership' || (hasMetrics && n === 'EigoMetrics'); },
    registerPlugin: function (n) { if (n === 'EigoMembership') return Membership; if (n === 'EigoMetrics') return Metrics; throw new Error('unexpected plugin ' + n); }
  };
  // Panel hooks (the shell calls these on the live frame; they are display controls, not an API of the app).
  root.__PV = {
    // USER_06 (2026-11-27, preview = real app in behaviour): the stand-in refuses to START an article the plan does not allow, the same decision as the real native gate for
    // a start (free: only the article picked for the day; trial / paid: any). The refusal is announced like the real one (accessDenied, point loadQueue) and nothing "plays".
    authorizeStart: function (slug) {
      var allow = S.phase !== 'free' || (!!S.pick && S.pick === slug);
      if (!allow) emit('accessDenied', { slug: slug, reason: S.pick ? 'locked_today' : 'needs_pick', point: 'loadQueue' });
      return allow;
    },
    state: function () { return JSON.parse(JSON.stringify(Object.assign(view(), { scn: S.scn, consent: S.consent, shown: S.shown }))); },
    // the next purchase / restore result, the next-day move (the date changes while the app stays open), the answer to the usage-data question
    set: function (o) {
      if (o.buy) S.buy = o.buy; if (o.restore) S.restore = o.restore;
      if (o.product === 'fail') S.product = { available: false, displayPrice: null, periodText: null, reason: 'not_found' };
      if (o.product === 'ok') S.product = { available: true, displayPrice: '¥490', periodText: '1か月', periodValue: 1, periodUnit: 'month', currencyCode: 'JPY', reason: null };
    },
    advanceDay: function () {   // a day later while the app stays open
      if (S.phase === 'trial') { if (S.trialDaysLeft > 1) { S.trialDaysLeft -= 1; } else { S.phase = 'free'; S.pick = null; S.popupDue = S.shown.trial_end ? 'none' : 'trial_end'; } }
      else if (S.phase === 'free') { S.pick = null; S.popupDue = 'none'; }
      emit('accessChanged');
    }
  };
})(window);
