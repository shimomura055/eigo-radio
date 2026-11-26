/* eigo_membership_ui.js -- membership UI of the iOS app (RELEASE-IOS-BILLING-MEMBERSHIP-01 Lane C, C5). iOS ONLY. UI APPROVAL PENDING: layout / colours / draft wording may still change.
   Loaded after eigo_membership_bridge.js and eigo_membership_text.js (scripts/anchors.mjs, html-scripts). The common webapp (lock-pinned 11 files) is NOT modified: this module overlays the
   existing DOM (cards, home / list top, My Page) with a MutationObserver, the same technique as the adapter's saved badges, and owns its own overlay layer (#em-root).
   Capability rule: when EigoHost.membership does not exist (Web, Android, an iOS binary without the plugin) this file does nothing and creates NO DOM.
   Authority rule: this file shows state and sends user operations. It never decides what may be played (native gates do); every "may I open this" answer here is a UI convenience that
   is re-asked from native (canAccess) before a dialog is shown, and the native refusal (accessDenied) is shown if the UI was stale.
   Wording lives ONLY in eigo_membership_text.js (APPROVED = user approved verbatim, DRAFT = proposal). There is no preview/state switch in this file (nothing here can fake a state). */
(function (root) {
  'use strict';
  var host = root.EigoHost, M = host && host.membership, X = root.EigoMembershipText, doc = root.document;
  if (!M || !X || !doc) return;
  var A = X.APPROVED, D = X.DRAFT, C = X.CONFIG, F = X.FORMAT;

  /* ------------------------------------------------------------------ small helpers */
  var ESC = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return ESC[c]; }); }
  function fmt(t, v) { return String(t).replace(/\{(\w+)\}/g, function (m, k) { return v && v[k] != null ? v[k] : m; }); }
  function $(id) { return doc.getElementById(id); }
  function nowMs() { return root.Date.now(); }
  function jst(sec) { var d = new root.Date((sec + 32400) * 1000); return { y: d.getUTCFullYear(), m: d.getUTCMonth() + 1, d: d.getUTCDate() }; }   // fixed +9h (same rule as the native core), device time zone independent
  function mdText(sec) { return fmt(F.md, jst(sec)); }
  function ymdText(sec) { return fmt(F.ymd, jst(sec)); }

  /* ------------------------------------------------------------------ the single display rules (change here only) */
  // Trial remaining-days display = plan B (user decision 2026-11-26 USER_02 sec 3-1): today is NOT counted (first day 7 ... last day 0 -> "本日まで").
  // The native core's trialDaysLeft counts today (first day 8 ... last day 1); the actual trial length is unchanged. To change the counting rule, change only this function.
  function displayTrialDays(s) { return s && typeof s.trialDaysLeft === 'number' ? Math.max(0, s.trialDaysLeft - 1) : null; }
  // Trial end date shown in the join-during-trial notice: the LAST trial day (trialEndsAt is 00:00 JST of the day after).
  function trialLastDayText(s) { return mdText(s.trialEndsAt - 1); }

  var S = null;   // last access state from native (display only)
  function phase() { return S ? S.phase : null; }
  function isFree() { return !!S && S.phase === 'free'; }
  function pickSlug() { return S && S.today ? S.today.pickSlug : null; }
  function canOpenByState(slug) { return !S || S.phase !== 'free' || pickSlug() === slug; }   // UI hint (state unknown => do not block; the native gate decides)
  function visuallyLocked(slug) { return isFree() && !!pickSlug() && pickSlug() !== slug; }   // all articles are candidates until one is picked: no lock before the pick (user original 4-4)
  function priceVars() {
    var yen = C.defaultYen, p = S && S.product;
    if (p && p.available && p.displayPrice && (!p.currencyCode || p.currencyCode === 'JPY')) { var n = parseInt(String(p.displayPrice).replace(/[^0-9]/g, ''), 10); if (n > 0) yen = n; }
    return { yen: yen, perDay: Math.round(yen * 12 / 365) };
  }
  function productOk() { return !!(S && S.product && S.product.available); }
  function mark() { return C.showDraftMarks ? '<span class="em-kari">' + esc(D.draftMark) + '</span>' : ''; }
  function isOffline() { try { return !!(root.navigator && root.navigator.onLine === false); } catch (e) { return false; } }
  function isSaved(slug) { try { var o = host.offline; var st = o && o.state && o.state(slug); return !!(st && st.status === 'saved'); } catch (e) { return false; } }
  function isPlaying() { var a = host.audioEl; return !!(a && a.paused === false); }
  function hashName() { var h = (root.location.hash || '').replace(/^#\/?/, ''); return h.split(/[?\/]/)[0] || 'home'; }
  function onHome() { return hashName() === 'home'; }
  function onReviewRoute() { return hashName() === 'review'; }
  function onListRoute() { return ['home', 'search', 'list', 'fav', 'me'].indexOf(hashName()) >= 0; }
  function tutorialOpen() { var t = $('tut'); return !!(t && !t.hidden && t.childNodes.length); }
  function catalogItems() { try { var c = root.__WUL.ST.cat; return (c.items || []).concat(Array.isArray(c.unlisted_items) ? c.unlisted_items : []); } catch (e) { return []; } }
  function titleOf(slug) { var l = catalogItems(); for (var i = 0; i < l.length; i++) if (l[i] && l[i].slug === slug) return l[i].title_ja || slug; return slug; }
  function legalHref(key) {
    var base = (root.EIGO_HOST_CONFIG && root.EIGO_HOST_CONFIG.pagesBase) || root.location.href;
    try { return new root.URL('../../' + key + '/', base).href; } catch (e) { return '../../' + key + '/'; }
  }

  /* ------------------------------------------------------------------ overlay layer (created on first use) */
  var rootEl = null, modalName = '', toastTimer = 0, opBusy = false;
  function ensureRoot() {
    if (rootEl) return rootEl;
    rootEl = doc.createElement('div'); rootEl.id = 'em-root';
    rootEl.innerHTML = '<div id="em-modal" class="em-modal" hidden role="dialog" aria-modal="true"><div class="em-back" data-em-act="modal-back"></div><div class="em-sheet" id="em-sheet"></div></div>' +
      '<div id="em-full" class="em-full" hidden role="dialog" aria-modal="true"></div><div id="em-toast" class="em-toast" role="status" aria-live="polite" hidden></div>';
    doc.body.appendChild(rootEl);
    return rootEl;
  }
  function openModal(name, html, ctx) { ensureRoot(); modalName = name; modalCtx = ctx || null; $('em-sheet').innerHTML = html; $('em-modal').hidden = false; $('em-modal').setAttribute('data-em-modal', name); focusFirst($('em-sheet')); }
  var modalCtx = null;
  function closeModal() { if (!rootEl) return; modalName = ''; modalCtx = null; $('em-modal').hidden = true; $('em-modal').removeAttribute('data-em-modal'); $('em-sheet').innerHTML = ''; }
  function modalOpen() { return !!modalName; }
  function fullName() { return rootEl && !$('em-full').hidden ? $('em-full').getAttribute('data-em-full') : ''; }
  function closeFull() { if (!rootEl) return; $('em-full').hidden = true; $('em-full').removeAttribute('data-em-full'); $('em-full').innerHTML = ''; }
  function focusFirst(el) { try { el.setAttribute('tabindex', '-1'); el.focus({ preventScroll: true }); } catch (e) { /* cosmetic */ } }   // focus the dialog itself (screen readers start there; no focus ring on a button)
  function toast(msg, ms) {
    ensureRoot(); var t = $('em-toast'); t.textContent = msg; t.hidden = false;
    root.clearTimeout(toastTimer); toastTimer = root.setTimeout(function () { t.hidden = true; }, ms || 4200);
  }
  function btn(act, cls, label, extra) { return '<button type="button" class="em-btn ' + cls + '" data-em-act="' + act + '"' + (extra || '') + '>' + esc(label) + '</button>'; }
  function lines(arr) { return arr.map(esc).join('<br>'); }
  function ul(arr) { return '<ul>' + arr.map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ul>'; }
  function sheet(inner) { return inner; }

  /* ------------------------------------------------------------------ dialogs */
  function showConfirm(slug, ctx) {
    var C0 = A.confirm;
    openModal('select_confirm', '<h3>' + esc(fmt(C0.question, { title: titleOf(slug) })) + '</h3>' + C0.lines.map(function (l) { return '<p>' + esc(l) + '</p>'; }).join('') +
      '<div class="em-acts">' + btn('confirm-ok', 'em-ok', C0.ok, ' data-slug="' + esc(slug) + '"') + btn('confirm-cancel', 'em-stay', C0.cancel) + '</div>', ctx);
  }
  function showTrialEnd() {
    var T = A.trialEnd, v = priceVars();
    openModal('trial_end', '<h3>' + esc(T.title) + '</h3><p>' + lines(T.body) + '</p><div class="em-h2">' + esc(T.meritTitle) + '</div>' + ul(T.merits) +
      '<div class="em-h2">' + esc(T.priceTitle) + '</div><div class="em-price">' + esc(fmt(T.price, v)) + '</div><p class="em-sub">' + esc(fmt(T.perDay, v)) + '</p>' +
      '<div class="em-acts">' + btn('join', 'em-go', T.join) + btn('stay', 'em-stay', T.stay) + '</div>');
  }
  function showPromo() {
    var P = A.promo, v = priceVars();
    openModal('promo', '<h3>' + lines(P.title) + '</h3><p>' + esc(P.body) + '</p>' + ul(P.merits) + '<div class="em-price">' + esc(fmt(P.price, v)) + '</div>' +
      '<div class="em-acts">' + btn('join', 'em-go', P.join) + btn('stay', 'em-stay', P.stay) + '</div>');
  }
  function showPaidEnd() {
    var P = A.paidEnd, v = priceVars();
    openModal('paid_end', '<h3>' + esc(P.title) + '</h3><p>' + esc(P.p1) + '</p><p>' + esc(P.p2) + '</p><p>' + esc(P.p3) + '</p><p><b>' + esc(P.invite) + '</b></p><div class="em-price">' + esc(fmt(P.price, v)) + '</div>' +
      '<div class="em-acts">' + btn('join', 'em-go', P.join) + btn('stay', 'em-stay', P.stay) + '</div>');
  }
  function showPaywall() {
    var P = A.paywall, v = priceVars();
    openModal('paywall', '<h3>' + esc(P.title) + '</h3><p>' + esc(P.body) + '</p><div class="em-price">' + esc(fmt(P.price, v)) + '</div>' +
      (isFree() && pickSlug() ? '<p class="em-sub" data-em-paywall-note>' + mark() + esc(D.paywallNote) + '</p>' : '') +
      '<div class="em-acts">' + btn('join', 'em-go', P.join) + btn('close', 'em-stay', P.close) + '</div>');
  }
  function showExpired(slug, ctx) {
    var E = D.expired, unpicked = isFree() && !pickSlug();
    openModal('expired_saved', '<h3>' + esc(E.title) + mark() + '</h3><p><b>' + esc(titleOf(slug)) + '</b></p><p>' + esc(E.p1) + '</p><p>' + esc(unpicked ? E.p2 : E.p2 + ' ' + E.p2picked) + '</p>' +
      '<div class="em-acts">' + btn('join', 'em-go', E.join) + (unpicked ? btn('expired-pick', 'em-stay', E.pick, ' data-slug="' + esc(slug) + '"') : '') + btn('close', 'em-stay', E.close) + '</div>', ctx);
  }
  function simpleNotice(name, title, body) {
    openModal(name, '<h3>' + esc(title) + mark() + '</h3><p>' + esc(body) + '</p><div class="em-acts">' + btn('close', 'em-stay', D.close) + '</div>');
  }
  /* ---- usage-data consent (plan 2, user decision 2026-11-26 USER_02 sec 1) ---- */
  var consentMsg = '';
  var consentInfo = null;   // null = not read yet; {consent, available} once read; {consent:'unanswered', available:false} when the app has no usage-data plugin (nothing to ask)
  function consentAvailable() { return !!consentInfo && consentInfo.available === true; }
  function consentPending() { return consentAvailable() && consentInfo.consent === 'unanswered'; }
  function loadConsent() {
    if (typeof M.getUsageConsent !== 'function') { consentInfo = { consent: 'unanswered', available: false }; return Promise.resolve(consentInfo); }
    return M.getUsageConsent().then(function (r) { consentInfo = r; return r; }, function () { consentInfo = { consent: 'unanswered', available: false }; return consentInfo; });
  }
  function consentBody(Cn) {
    return '<h3 class="em-ch">' + esc(Cn.whatTitle) + '</h3>' + ul(Cn.what) + '<p class="em-sub">' + esc(Cn.notSent) + '</p>' +
      '<h3 class="em-ch">' + esc(Cn.toTitle) + '</h3><p>' + esc(Cn.to) + '</p><h3 class="em-ch">' + esc(Cn.whyTitle) + '</h3><p>' + esc(Cn.why) + '</p>' +
      '<p><b>' + esc(Cn.freedom) + '</b></p><p>' + esc(Cn.later) + '</p>' +
      '<p><a class="em-link" href="' + esc(legalHref(C.legalPages.privacy)) + '" target="_blank" rel="noopener" data-em-legal="privacy">' + esc(A.join.privacy) + '</a></p>';
  }
  // The first notice. Trial + consent asked: ONE screen = the free-trial points + the consent question + two equal buttons. Consent only (not the trial, e.g. shown again after an unanswered close): the question alone.
  // When the app has no usage-data plugin there is nothing to ask: the old single "はじめる" button.
  function showIntro(o) {   // o.combined: first launch of the trial (trial points + consent). Otherwise (asked again / opened from My Page) the consent question alone. o.closable: opened by the user from My Page (may leave without answering)
    o = o || {};
    var I = D.intro, Cn = D.consent, end = S && S.trialEndsAt ? mdText(S.trialEndsAt - 1) : '', ask = consentPending(), trial = !!o.combined && !!S && S.phase === 'trial';
    ensureRoot(); var f = $('em-full'); f.setAttribute('data-em-full', 'intro'); f.hidden = false;
    var head = trial ? '<h2>' + esc(I.title) + '</h2>' + (C.showDraftMarks ? '<p style="text-align:center">' + mark() + '</p>' : '') + '<p>' + esc(fmt(I.lead, { end: end })) + '</p>' + ul(I.items) + '<p class="em-foot">' + esc(I.foot) + '</p>' : '';
    var acts;
    if (!ask) acts = btn('intro-ok', 'em-go', I.button);
    else acts = '<div class="em-eqacts">' + btn('consent-yes', 'em-eq', trial ? Cn.agreeFirst : Cn.agree) + btn('consent-no', 'em-eq', trial ? Cn.declineFirst : Cn.decline) + '</div>' + (o.closable ? '<div class="em-closerow">' + btn('consent-close', 'em-linkbtn', D.close) + '</div>' : '');
    f.innerHTML = '<div class="em-intro" data-em-intro="' + (ask ? (trial ? 'trial_consent' : 'consent') : 'trial') + '">' + head +
      (ask ? '<div class="em-consent" data-em-consent-box><h2' + (trial ? ' class="em-ch2"' : '') + '>' + esc(Cn.title) + '</h2><p>' + esc(Cn.lead) + '</p>' + consentBody(Cn) + '</div>' : '') +
      '<div class="em-introacts">' + acts + '</div></div>';
    focusFirst(f);
  }
  function chooseConsent(value, fromScreen) {
    if (opBusy || typeof M.chooseUsageConsent !== 'function') return;
    opBusy = true;
    M.chooseUsageConsent(value).then(function () { return loadConsent(); }).then(function () {
      opBusy = false;
      consentMsg = fromScreen ? '' : (value === 'denied' ? D.consentSettings.offDone : D.consentSettings.onDone);
      if (fromScreen) { closeFull(); refresh(); } else decorateSoon();
    }, function () { opBusy = false; toast(D.consent.saveFail); });
  }

  /* ---- join screen (common for every entry) ---- */
  function showJoin() {
    ensureRoot(); var f = $('em-full'); f.setAttribute('data-em-full', 'join'); f.hidden = false;
    renderJoin();
    if (!productOk()) loadProduct();
  }
  function loadProduct() {
    M.refreshProduct().then(function () { return M.getAccessState(); }, function () { return M.getAccessState(); }).then(function (s) { S = s; if (fullName() === 'join') renderJoin(); }, function () { if (fullName() === 'join') renderJoin(); });
  }
  function renderJoin() {
    var J = A.join, v = priceVars(), f = $('em-full'), keep = f.scrollTop, canBuy = !!S && (S.phase === 'trial' || S.phase === 'free');
    var busy = opBusy || (S && S.purchaseState === 'busy'), waiting = !!S && S.purchaseState === 'pending';
    var priceBlock;
    if (productOk()) priceBlock = '<div class="em-card em-pricecard"><div class="em-nm">' + esc(J.planName) + '</div><div class="em-amt">' + esc(fmt(J.price, v)) + '</div><div class="em-per">' + esc(J.renewal) + '</div></div>';
    else priceBlock = '<div class="em-card em-pricecard"><div class="em-nm">' + esc(J.planName) + '</div><div class="em-per" data-em-product="unavailable">' + esc(S && S.product && S.product.reason === 'not_loaded' ? D.productLoading : D.productFail) + '</div>' +
      '<button type="button" class="em-link" data-em-act="product-retry">' + esc(D.productRetry) + '</button></div>';
    var trialNote = S && S.phase === 'trial' ? '<div class="em-trialnote" data-em-trialnote>' + esc(fmt(A.trialBuyNotice, { date: trialLastDayText(S) })) + '</div>' : '';
    var paidNote = S && (S.phase === 'paid' || S.phase === 'paid_grace_offline') ? '<div class="em-msg">' + esc(D.alreadyPaid) + '</div>' : '';
    var buy = canBuy ? '<button type="button" class="em-btn em-go" id="em-buy" data-em-act="buy"' + ((busy || waiting || !productOk()) ? ' disabled' : '') + '>' + esc(busy ? D.working : fmt(J.button, v)) + '</button>' : '';
    var pendNote = waiting ? '<div class="em-msg" data-em-pending>' + esc(D.buyPending) + '</div>' : '';
    var terms = '<div class="em-terms" id="em-terms">' + (C.showDraftMarks ? mark() : '') + D.terms.map(function (t) { return '<p>' + esc(fmt(t, v)) + '</p>'; }).join('') + '</div>';
    f.innerHTML = '<div class="em-topbar"><button type="button" class="em-back-btn" data-em-act="join-close" aria-label="' + esc(D.back) + '"><span aria-hidden="true">&#8249;</span> ' + esc(D.back) + '</button></div>' +
      '<h2 class="em-jtitle">' + esc(J.title) + '</h2><div class="em-hero"><h1>' + lines(J.main) + '</h1><p>' + esc(J.sub) + '</p></div>' +
      '<div class="em-card"><h3>' + esc(J.meritTitle) + '</h3>' + ul(J.merits) + '</div>' + priceBlock + trialNote + paidNote + pendNote + buy + terms +
      '<div class="em-aux"><button type="button" class="em-link" data-em-act="restore">' + esc(J.restore) + '</button>' +
      '<a class="em-link" href="' + esc(legalHref(C.legalPages.terms)) + '" target="_blank" rel="noopener" data-em-legal="terms">' + esc(J.terms) + '</a>' +
      '<a class="em-link" href="' + esc(legalHref(C.legalPages.privacy)) + '" target="_blank" rel="noopener" data-em-legal="privacy">' + esc(J.privacy) + '</a></div>';
    f.scrollTop = keep;
  }

  /* ------------------------------------------------------------------ operations (each one maps to one user tap; none can grant anything by itself) */
  function afterStateChange() { decorateSoon(); scheduleCheck(); if (fullName() === 'join') renderJoin(); }
  function refresh() {
    return M.getAccessState().then(function (s) { S = s; afterStateChange(); return s; }, function () { return S; });
  }
  function doBuy() {
    if (opBusy || (S && S.purchaseState === 'busy') || !productOk()) return;
    opBusy = true; if (fullName() === 'join') renderJoin();
    M.purchase().then(function (r) {
      opBusy = false;
      var res = r && r.result;
      return refresh().then(function () {
        if (res === 'success') { closeModal(); closeFull(); toast(D.buyOk); try { root.location.hash = '#/me'; } catch (e) { /* */ } }
        else if (res === 'cancelled') { closeModal(); }
        else if (res === 'pending') simpleNotice('buy_pending', D.buyPendingTitle, D.buyPending);
        else if (res === 'unverified') simpleNotice('buy_unverified', D.buyUnverifiedTitle, D.buyUnverified);
        else if (res === 'busy') { /* the native side is already handling one purchase */ }
        else openModal('buy_failed', '<h3>' + esc(D.buyFailTitle) + mark() + '</h3><p>' + esc(D.buyFail) + '</p><div class="em-acts">' + btn('buy', 'em-go', D.retry) + btn('close', 'em-stay', D.close) + '</div>');
      });
    }, function () {
      opBusy = false; refresh();
      openModal('buy_failed', '<h3>' + esc(D.buyFailTitle) + mark() + '</h3><p>' + esc(D.buyFail) + '</p><div class="em-acts">' + btn('buy', 'em-go', D.retry) + btn('close', 'em-stay', D.close) + '</div>');
    });
  }
  function doRestore() {
    if (opBusy) return;
    opBusy = true; toast(D.restoreWorking, 2500);
    M.restore().then(function (r) {
      opBusy = false;
      var res = r && r.result;
      return refresh().then(function () {
        if (res === 'done') {
          if (S && (S.phase === 'paid' || S.phase === 'paid_grace_offline')) { closeModal(); closeFull(); toast(D.restoreOk); }
          else simpleNotice('restore_none', D.restoreNoneTitle, D.restoreNone);
        } else if (res === 'failed') simpleNotice('restore_fail', D.restoreFailTitle, D.restoreFail);
      });
    }, function () { opBusy = false; simpleNotice('restore_fail', D.restoreFailTitle, D.restoreFail); });
  }
  function doManage() {
    M.openManageSubscriptions().then(function (r) { if (!r || r.opened !== true) toast(D.manageFail); }, function () { toast(D.manageFail); });
  }
  function doConfirm(slug, btnEl) {
    if (btnEl.disabled) return;
    btnEl.disabled = true;
    var ctx = modalCtx;
    M.commitFreePick(slug).then(function (r) {
      return refresh().then(function () {
        closeModal();
        if (r && r.ok) { if (ctx && ctx.resume) ctx.resume(true); }
        else if (r && r.code === 'already_picked') showPaywall();
        else if (r && r.code === 'not_needed') { if (ctx && ctx.resume) ctx.resume(true); }
      });
    }, function () { btnEl.disabled = false; toast(D.pickSaveFail); });
  }

  /* ------------------------------------------------------------------ "may I open this article" flow */
  var bypassEl = null;
  function resumeOpen(slug, el) {
    return function () {
      if (el && el.isConnected) { bypassEl = el; try { el.click(); } finally { bypassEl = null; } }
      else { try { root.location.hash = '#/player/' + encodeURIComponent(slug); } catch (e) { /* */ } }
    };
  }
  function dialogForBlocked(slug, ctx, reason) {
    if (reason === 'grant_no_switch') { toast(D.deniedSwitchToast); return; }
    var unpicked = isFree() && !pickSlug();
    if (isOffline() && !isSaved(slug)) { toast(unpicked ? D.offlineSelectHint : D.offlineLockedHint); return; }
    if (unpicked) { showConfirm(slug, ctx); return; }
    if ((ctx && ctx.route === 'me') || isOffline()) showExpired(slug, ctx); else showPaywall();
  }
  function blocked(slug, ctx) {   // the UI state says "not available": ask native once more (a finish-grant may still allow it), then show the matching dialog
    var ask;
    try { ask = M.canAccess(slug, 'start'); } catch (e) { ask = Promise.reject(e); }
    ask.then(function (a) { if (a && a.allow) ctx.resume(false); else dialogForBlocked(slug, ctx, a && a.reason); }, function () { dialogForBlocked(slug, ctx, null); });
  }
  function onDocClick(e) {
    var t = e.target; if (!t || !t.closest) return;
    var ea = t.closest('[data-em-act]');
    if (ea) { e.preventDefault(); e.stopImmediatePropagation(); handleAct(ea); return; }   // buttons of this module (overlay or inside the page): the webapp never sees them
    if (rootEl && rootEl.contains(t)) return;
    if (t.closest('[data-fav]')) return;   // favourites are never limited
    if (bypassEl) return;
    var om = t.closest('[data-omakase]');
    if (om) { if (isFree()) { e.preventDefault(); e.stopImmediatePropagation(); decorateSoon(); } return; }   // the free plan has no omakase (the button is hidden; a stale tap does nothing and no guidance is shown)
    var pl = t.closest('[data-play]'), op = pl ? null : t.closest('[data-open]'), src = pl || op;
    if (!src) return;
    var slug = pl ? pl.getAttribute('data-play') : op.getAttribute('data-open');
    if (!slug || canOpenByState(slug)) return;
    e.preventDefault(); e.stopImmediatePropagation();
    blocked(slug, { route: hashName(), resume: resumeOpen(slug, src) });
  }
  doc.addEventListener('click', onDocClick, true);   // capture: runs before the webapp's own delegated handler
  var PLAYER_RE = /^#\/player\/([^?\/#]+)/;
  root.addEventListener('hashchange', function (e) {   // links / restored routes that go straight to an article page (registered before the webapp's own listener)
    var m = PLAYER_RE.exec(root.location.hash || ''); if (!m) { onRouteChange(); return; }
    var slug; try { slug = decodeURIComponent(m[1]); } catch (x) { slug = m[1]; }
    if (canOpenByState(slug)) { onRouteChange(); return; }
    e.stopImmediatePropagation();
    var oldUrl = e.oldURL || '', oldHash = oldUrl.indexOf('#') >= 0 ? oldUrl.slice(oldUrl.indexOf('#')) : '#/home';
    try { root.history.replaceState(null, '', oldUrl || ('#/home')); } catch (x) { try { root.location.hash = oldHash; } catch (y) { /* */ } }
    var route = oldHash.replace(/^#\/?/, '').split(/[?\/]/)[0] || 'home';
    blocked(slug, { route: route, resume: function () { try { root.location.hash = '#/player/' + encodeURIComponent(slug); } catch (x) { /* */ } } });
  });

  /* ------------------------------------------------------------------ native refusals (accessDenied) */
  var deferredDenied = null;
  var EXPLICIT_POINTS = { loadQueue: 1, download: 1, playItem: 1, replaceQueueItem: 1, fetch: 1 };
  var lastFetchDenied = { slug: '', t: 0 };
  function showDenied(d) {
    var slug = d && d.slug;
    if (d && d.reason === 'grant_no_switch') { toast(D.deniedSwitchToast); return; }
    if (!slug) { toast(D.deniedToast); return; }
    blocked(slug, { route: hashName(), resume: function () { try { root.location.hash = '#/player/' + encodeURIComponent(slug); } catch (e) { /* */ } } });
  }
  M.on('accessDenied', function (d) {
    if (!d || d.point === 'prefetchClip') return;   // silent background prefetch: nothing to tell the user
    if (d.reason === 'slug_mismatch' || d.reason === 'bad_slug') { try { host.diag && host.diag('js.membership.denied_bad_id', { point: d.point, reason: d.reason }); } catch (e) { /* record only */ } return; }   // an id/URL fault, not a plan matter: no dialog (log only)
    if (d.point === 'playItem' && onReviewRoute()) { refresh(); try { host.diag && host.diag('js.membership.review_audio_refused', { reason: d.reason }); } catch (e) { /* record only */ } return; }   // review-book audio is playable in every plan (user decision 2026-11-26 USER_02 sec 3-2): never a restriction / join notice here
    if (d.point === 'autoNext') { refresh(); return; }   // a free member finishing the picked article is refused auto-advance every time (normal): silent; notices come only from popupDue
    if (d.point === 'download') { refresh().then(function () { if (!modalOpen()) toast(D.deniedToast); }); return; }   // a refused save: one short notice, no dialog (saved files stay)
    if (d.point === 'fetch') {   // article data refused (the UI state was stale, e.g. the plan changed at midnight): one explanation per article, and leave the broken article page
      var tn = nowMs(); if (lastFetchDenied.slug === d.slug && tn - lastFetchDenied.t < 3000) return; lastFetchDenied = { slug: d.slug, t: tn };
    }
    refresh().then(function () {
      if (d.point === 'fetch' && PLAYER_RE.test(root.location.hash || '') && !canOpenByState(d.slug)) { try { root.history.replaceState(null, '', '#/home'); root.dispatchEvent(new root.Event('hashchange')); } catch (e) { /* */ } }
      if (isPlaying()) { toast(D.deniedToast); return; }                // never put a popup in front of playback
      if (onListRoute() || EXPLICIT_POINTS[d.point]) { if (!modalOpen()) showDenied(d); else toast(D.deniedToast); return; }
      deferredDenied = d; toast(D.deniedToast);                          // reading / learning an article page: tell now with a toast, explain in the list afterwards
    });
  });
  M.on('accessChanged', function (s) { if (s) { S = s; afterStateChange(); } });

  /* ------------------------------------------------------------------ notices (first launch / trial end / periodic / paid end) */
  var checkTimer = 0, noticeBusy = false;
  function scheduleCheck() { if (checkTimer) return; checkTimer = root.setTimeout(function () { checkTimer = 0; checkNotices(); }, 80); }
  function checkNotices() {
    if (!S || noticeBusy || modalOpen() || fullName() || opBusy) return;
    if (S.storeSynced === false) return;   // the first store sync is still running (max 15 s): no notice yet; native sends accessChanged when it ends
    if (isPlaying() || tutorialOpen() || (doc.hidden === true)) return;
    if (consentInfo === null) return;   // the consent answer is being read first (loadConsent -> scheduleCheck): the first notice must know whether it asks
    if (deferredDenied && onListRoute()) { var d = deferredDenied; deferredDenied = null; showDenied(d); return; }
    if (!onHome()) return;
    var kind = null;
    if (S.firstLaunchNoticeDue && S.phase === 'trial') kind = 'first_launch';
    else if (S.phase === 'free' && S.popupDue && S.popupDue !== 'none') kind = S.popupDue;
    if (consentPending() && kind !== 'first_launch') { showIntro(); return; }   // not answered yet (the app was closed without an answer): ask again at the next start; nothing is sent meanwhile (native)
    if (!kind) return;
    noticeBusy = true;
    M.markNoticeShown(kind).then(function (r) {   // recorded at the moment of display (the due day = the day it is actually shown)
      noticeBusy = false;
      if (!(r && r.recorded)) { refresh(); return; }
      if (isPlaying() || modalOpen() || fullName()) { refresh(); return; }
      if (kind === 'first_launch') showIntro({ combined: true }); else if (kind === 'trial_end') showTrialEnd(); else if (kind === 'paid_end') showPaidEnd(); else if (kind === 'periodic') showPromo();
      refresh();
    }, function () { noticeBusy = false; });
  }
  function onRouteChange() { refresh(); decorateSoon(); scheduleCheck(); }

  /* ------------------------------------------------------------------ overlay clicks */
  function handleAct(el) {
    var act = el.getAttribute('data-em-act');
    switch (act) {
      case 'modal-back': closeModal(); return;
      case 'close': case 'stay': case 'confirm-cancel': closeModal(); return;
      case 'join': closeModal(); showJoin(); return;
      case 'join-close': closeFull(); scheduleCheck(); return;
      case 'intro-ok': closeFull(); refresh(); return;
      case 'consent-yes': chooseConsent('granted', true); return;
      case 'consent-no': chooseConsent('denied', true); return;
      case 'consent-close': closeFull(); scheduleCheck(); return;
      case 'consent-toggle':
        if (consentInfo && consentInfo.consent === 'unanswered') { if (!fullName() && !modalOpen()) showIntro({ closable: true }); return; }   // never answered: show the full explanation first
        chooseConsent(consentInfo && consentInfo.consent === 'granted' ? 'denied' : 'granted', false); return;
      case 'confirm-ok': doConfirm(el.getAttribute('data-slug'), el); return;
      case 'expired-pick': { var sl = el.getAttribute('data-slug'), c = modalCtx; closeModal(); showConfirm(sl, c || { route: hashName(), resume: function () { try { root.location.hash = '#/player/' + encodeURIComponent(sl); } catch (x) { /* */ } } }); return; }
      case 'buy': doBuy(); return;
      case 'manage': doManage(); return;
      case 'restore': closeModal(); doRestore(); return;
      case 'product-retry': renderJoinLoading(); loadProduct(); return;
    }
  }
  function renderJoinLoading() { var p = rootEl && rootEl.querySelector('[data-em-product]'); if (p) p.textContent = D.productLoading; }

  /* ------------------------------------------------------------------ in-page decoration (cards / list top / My Page) */
  var LOCK_SVG = '<svg class="em-lockic" viewBox="0 0 24 24" aria-hidden="true"><path d="M7 10V8a5 5 0 0 1 10 0v2h1a1 1 0 0 1 1 1v9a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1v-9a1 1 0 0 1 1-1zm2 0h6V8a3 3 0 0 0-6 0z"/></svg>';
  var view = null, mo = null, decorTimer = 0;
  function decorateSoon() { if (decorTimer) return; decorTimer = root.setTimeout(function () { decorTimer = 0; decorate(); }, 30); }
  function decorateCards(v) {
    [].forEach.call(v.querySelectorAll('article.card[data-open]'), function (c) {
      var slug = c.getAttribute('data-open'), locked = visuallyLocked(slug), picked = isFree() && pickSlug() === slug;
      var th = c.querySelector('.thumb'), lb = th && th.querySelector('.em-lockb');
      if (locked) { c.setAttribute('data-em-locked', '1'); if (th && !lb) { lb = doc.createElement('span'); lb.className = 'em-lockb'; lb.setAttribute('aria-label', D.lockBadgeAria); lb.innerHTML = LOCK_SVG; th.appendChild(lb); } } else { c.removeAttribute('data-em-locked'); if (lb) lb.remove(); }
      var cp = c.querySelector('.cardplay');
      if (cp) {
        if (locked) {
          if (!cp.classList.contains('em-locked')) { cp.classList.add('em-locked'); cp.setAttribute('data-em-label', cp.getAttribute('aria-label') || ''); cp.setAttribute('aria-label', fmt(D.lockedPlayAria, { title: titleOf(slug) })); cp._emOrig = cp.innerHTML; }
          if (!cp.querySelector('.em-lockic')) { if (cp._emOrig == null || cp.innerHTML.indexOf('em-lockic') < 0) cp._emOrig = cp.innerHTML; cp.innerHTML = LOCK_SVG; }   // the lock icon replaces the play icon (restored when the lock goes)
        } else if (cp.classList.contains('em-locked')) {
          cp.classList.remove('em-locked'); cp.setAttribute('aria-label', cp.getAttribute('data-em-label') || ''); cp.removeAttribute('data-em-label');
          if (cp._emOrig != null) cp.innerHTML = cp._emOrig; cp._emOrig = null;
        }
      }
      var chips = c.querySelector('.chips'), fc = chips && chips.querySelector('.em-free');
      if (picked) { if (chips && !fc) { fc = doc.createElement('span'); fc.className = 'chip em-free'; fc.textContent = D.freeChip; chips.insertBefore(fc, chips.firstChild); } } else if (fc) fc.remove();
    });
  }
  function barHtml() {
    if (!S) return '';
    if (S.phase === 'trial') {
      var n = displayTrialDays(S);
      return n == null ? '' : '<div class="em-bar em-trial" data-em-bar="trial"><b>' + esc(n === 0 ? D.trialBarLast : fmt(A.trialBar, { days: n })) + '</b></div>';
    }
    if (S.phase === 'free') {
      var p = pickSlug();
      return '<div class="em-bar" data-em-bar="free">' + mark() + ' <b>' + esc(p ? fmt(D.freeBarPicked, { title: titleOf(p) }) : D.freeBarNone) + '</b></div>';
    }
    return '';
  }
  function decorateBar(v) {
    var name = hashName(), want = (name === 'home' || name === 'list' || name === 'search') ? barHtml() : '';
    var cur = v.querySelector('[data-em-bar]'), kind = want ? /data-em-bar="(\w+)"/.exec(want)[1] : '';
    if (!want) { if (cur) cur.remove(); return; }
    if (cur && cur.getAttribute('data-em-bar') === kind && cur.outerHTML === want) return;
    var holder = doc.createElement('div'); holder.innerHTML = want; var nb = holder.firstChild;
    if (cur) { cur.replaceWith(nb); return; }
    var anchor = v.querySelector('.tag') || v.querySelector('.top');
    if (anchor && anchor.parentNode) anchor.parentNode.insertBefore(nb, anchor.nextSibling); else v.insertBefore(nb, v.firstChild);
  }
  function planCardHtml() {
    var St = A.settings, DS = D.settings, v = priceVars(), h = '<div class="em-plan" data-em-plan="' + esc(S.phase) + (S.paidCancelled ? ':cancelled' : '') + '"><div class="em-pl0">' + esc(St.planLabel) + '</div>';
    if (S.phase === 'trial') {
      h += '<div class="em-pn">' + esc(St.trial) + '</div><div class="em-pr"><span>' + esc(St.trialEndDate) + '</span><span>' + esc(ymdText(S.trialEndsAt - 1)) + '</span></div><p>' + esc(DS.trialA) + '</p><p>' + esc(DS.trialB) + '</p>' + btn('join', 'em-go', St.join);
    } else if (S.phase === 'free') {
      h += '<div class="em-pn">' + esc(St.free) + '</div><p>' + esc(DS.freeA) + '</p><p>' + esc(DS.freeB) + '</p><div class="em-pr"><span>' + esc(DS.freeJoinLabel) + '</span><span>' + esc(fmt(St.monthlyShort, v)) + '</span></div>' + btn('join', 'em-go', St.join);
    } else {   // paid / paid_grace_offline
      h += '<div class="em-pn">' + esc(St.paid) + '</div>';
      if (S.paidCancelled) h += '<div class="em-pr"><span>' + esc(St.contractState) + '</span><span>' + esc(St.stoppedAuto) + '</span></div><div class="em-pr"><span>' + esc(St.expiry) + '</span><span>' + esc(S.paidExpiresAt ? ymdText(S.paidExpiresAt) : '') + '</span></div><p>' + esc(DS.paidCancelledA) + '</p>';
      else h += '<div class="em-pr"><span>' + esc(DS.priceLabel) + '</span><span>' + esc(fmt(St.monthly, v)) + '</span></div><div class="em-pr"><span>' + esc(St.nextRenewal) + '</span><span>' + esc(S.paidExpiresAt ? ymdText(S.paidExpiresAt) : '') + '</span></div><p>' + esc(DS.paidA) + '</p>';
      if (S.phase === 'paid_grace_offline') h += '<p class="em-sub">' + esc(D.grace) + '</p>';
      h += btn('manage', 'em-stay', S.paidCancelled ? D.manageRowCancelled : D.manageRow);
    }
    return h + '</div>';
  }
  function decorateMe(v) {
    var old = v.querySelector('[data-em-plan]');
    if (hashName() !== 'me' || !S) { if (old) old.remove(); var ob = v.querySelector('[data-em-other]'); if (ob) ob.remove(); var ocs = v.querySelector('[data-em-consent-set]'); if (ocs) ocs.remove(); [].forEach.call(v.querySelectorAll('[data-em-legal-row]'), function (n) { n.remove(); }); return; }
    var want = planCardHtml();
    if (!old || old.outerHTML !== want) {
      var h = doc.createElement('div'); h.innerHTML = want; var nb = h.firstChild;
      if (old) old.replaceWith(nb); else { var h2 = v.querySelector('h2'); if (h2 && h2.parentNode) h2.parentNode.insertBefore(nb, h2.nextSibling); else v.insertBefore(nb, v.firstChild); }
    }
    // "その他の手続き": purchase restore (every state, auxiliary position) + the contract management entry for paid states
    var otherWant = '<div class="em-other" data-em-other><div class="em-pl" id="em-other-procs">' + esc(A.restore.sectionTitle) + '</div><div class="em-restorebox"><button type="button" class="setrow" data-em-act="restore" id="em-restorebtn">' + esc(A.restore.name) + '<span>&#8250;</span></button>' +
      '<p class="em-rnote">' + esc(A.restore.note) + '</p>' + ((S.phase === 'paid' || S.phase === 'paid_grace_offline') ? '<button type="button" class="setrow" data-em-act="manage">' + esc(S.paidCancelled ? D.manageRowCancelled : D.manageRow) + '<span>&#8250;</span></button>' : '') + '</div></div>';
    var oo = v.querySelector('[data-em-other]');
    if (!oo || oo.outerHTML !== otherWant) {
      var h3 = doc.createElement('div'); h3.innerHTML = otherWant; var nn = h3.firstChild;
      if (oo) oo.replaceWith(nn);
      else {
        var legalHead = [].filter.call(v.querySelectorAll('.pl'), function (n) { return /サポート・規約/.test(n.textContent); })[0];
        if (legalHead && legalHead.parentNode) legalHead.parentNode.insertBefore(nn, legalHead); else v.appendChild(nn);
      }
    }
    // terms / specified-commercial-transactions rows next to the webapp's own support / privacy rows (URLs are settings: CONFIG.legalPages)
    var rows = v.querySelectorAll('a.setrow[data-legal]'), last = rows.length ? rows[rows.length - 1] : null;
    ['terms', 'tokushoho'].forEach(function (key) {
      if (v.querySelector('[data-em-legal-row="' + key + '"]')) return;
      var a = doc.createElement('a'); a.className = 'setrow'; a.setAttribute('data-legal', key); a.setAttribute('data-em-legal-row', key);
      a.href = legalHref(C.legalPages[key]); a.target = '_blank'; a.rel = 'noopener'; a.innerHTML = esc(A.legalRows[key]) + '<span>&#8250;</span>';
      if (last && last.parentNode) { last.parentNode.insertBefore(a, last.nextSibling); last = a; } else v.appendChild(a);
    });
    // saved-article rows (user instruction: no state label on a row -- neither the common list's "saved" word nor a membership availability word): row = title (tap = article page) + size + the management action (delete).
    // Only the plain "saved" word of the common list is dropped; the exceptional states (partial / busy / failed ...) stay because the user must act on them.
    [].forEach.call(v.querySelectorAll('.dlrow[data-dl-row]'), function (r) {
      var small = r.querySelector('small'), old = r.querySelector('.em-st'); if (old) old.remove();
      if (small && /^\s*保存済み/.test(small.textContent)) small.textContent = small.textContent.replace(/^\s*保存済み\s*/, '');
    });
    // consent switch (only when the app has the usage-data plugin and it is available)
    var oc = v.querySelector('[data-em-consent-set]');
    if (!consentAvailable()) { if (oc) oc.remove(); }
    else {
      var CS = D.consentSettings, st2 = consentInfo.consent, stLabel = st2 === 'granted' ? CS.on : (st2 === 'denied' ? CS.off : CS.unanswered);
      var consWant = '<div data-em-consent-set data-em-sig="' + esc(st2 + '|' + consentMsg) + '"><div class="pl">' + esc(CS.section) + '</div>' +
        '<button type="button" class="setrow" role="switch" aria-checked="' + (st2 === 'granted' ? 'true' : 'false') + '" data-em-act="consent-toggle">' + esc(CS.row) + '<span data-em-consent-state>' + esc(stLabel) + '</span></button>' +
        '<div class="lvnote" data-em-consent-note>' + esc(CS.note) + '</div><div class="lvnote" data-em-consent-msg role="status">' + esc(consentMsg) + '</div>' +
        '<a class="setrow" href="' + esc(legalHref(C.legalPages.privacy)) + '" target="_blank" rel="noopener" data-em-legal="privacy">' + esc(A.join.privacy) + '<span>&#8250;</span></a></div>';
      if (!oc || oc.getAttribute('data-em-sig') !== st2 + '|' + consentMsg) {
        var h4 = doc.createElement('div'); h4.innerHTML = consWant; var cn = h4.firstChild;
        if (oc) oc.replaceWith(cn);
        else { var oo2 = v.querySelector('[data-em-other]'); if (oo2 && oo2.parentNode) oo2.parentNode.insertBefore(cn, oo2.nextSibling); else v.appendChild(cn); }
      }
    }
  }
  function decorateOmakase(v) {   // the free plan has no omakase (user decision 2026-11-26 USER_02 sec 3-3): the whole section is hidden (no empty space); trial / paid are untouched
    var s = v.querySelector('#omakase'); if (!s) return;
    if (isFree()) { if (!s.hasAttribute('data-em-hidden')) { s.setAttribute('data-em-hidden', '1'); s.hidden = true; s.style.display = 'none'; } }
    else if (s.hasAttribute('data-em-hidden')) { s.removeAttribute('data-em-hidden'); s.hidden = false; s.style.display = ''; }
  }
  function decorate() {
    var v = view || (view = $('view')); if (!v) return;
    if (mo) mo.disconnect();
    try { decorateCards(v); decorateBar(v); decorateOmakase(v); decorateMe(v); } catch (e) { try { host.diag && host.diag('js.membership.ui_error', { msg: String(e && e.message) }); } catch (x) { /* */ } }
    if (mo) mo.observe(v, { childList: true, subtree: true });
  }

  /* ------------------------------------------------------------------ start */
  function init() {
    view = $('view');
    if (view && root.MutationObserver) { mo = new root.MutationObserver(function () { decorateSoon(); }); mo.observe(view, { childList: true, subtree: true }); }
    var a = host.audioEl; if (a && a.addEventListener) { a.addEventListener('pause', scheduleCheck); a.addEventListener('ended', scheduleCheck); }
    doc.addEventListener('visibilitychange', function () { if (!doc.hidden) { refresh(); scheduleCheck(); } });
    root.setInterval(function () { scheduleCheck(); }, 5000);
    var ticks = 0; root.setInterval(function () { if (!doc.hidden && ++ticks % 12 === 0) refresh(); }, 5000);   // picks up a date change / trial end while the app stays open
    loadConsent().then(function () { decorateSoon(); scheduleCheck(); });
    doc.addEventListener('visibilitychange', function () { if (!doc.hidden) loadConsent().then(function () { decorateSoon(); }); });
    refresh().then(function () {
      if (!productOk()) M.refreshProduct().then(function () { return refresh(); }, function () { /* the join screen retries on open */ });   // price for the popups comes from the store as early as possible (read only)
      var m = PLAYER_RE.exec(root.location.hash || '');   // started on an article page the plan does not allow (restored route)
      if (m) { var slug; try { slug = decodeURIComponent(m[1]); } catch (x) { slug = m[1]; } if (!canOpenByState(slug)) { try { root.location.hash = '#/home'; } catch (x) { /* */ } blocked(slug, { route: 'home', resume: function () { root.location.hash = '#/player/' + encodeURIComponent(slug); } }); } }
    });
  }
  if (doc.readyState === 'loading') doc.addEventListener('DOMContentLoaded', init); else init();
})(typeof window !== 'undefined' ? window : globalThis);
