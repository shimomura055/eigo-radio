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
  function hideToast() { var tt = rootEl && $('em-toast'); if (tt) { tt.hidden = true; root.clearTimeout(toastTimer); } }   // a short working notice (e.g. "確認しています…") must not stay over the dialog that answers it
  function openModal(name, html, ctx) { ensureRoot(); hideToast(); modalName = name; modalCtx = ctx || null; $('em-sheet').innerHTML = html; $('em-modal').hidden = false; $('em-modal').setAttribute('data-em-modal', name); focusFirst($('em-sheet')); }
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
  function consentDetails(Cn) {   // the part behind "くわしく見る": what is sent / not sent / the policy
    return '<h3 class="em-ch">' + esc(Cn.whatTitle) + '</h3>' + ul(Cn.what) + '<h3 class="em-ch">' + esc(Cn.notSentTitle) + '</h3><p>' + esc(Cn.notSent) + '</p>' +
      '<p><a class="em-link" href="' + esc(legalHref(C.legalPages.privacy)) + '" target="_blank" rel="noopener" data-em-legal="privacy">' + esc(A.join.privacy) + '</a></p>';
  }
  // The first notice (B5: ONE short screen; the body scrolls only when the screen is small, the two buttons are a separate opaque block under it, never over the text).
  // Trial + consent asked: the free-trial points (3 lines) + the consent question (what / to whom / why) + "details" + two equal buttons. Consent only (asked again / opened from My Page): the question alone.
  // When the app has no usage-data plugin there is nothing to ask: the old single "はじめる" button.
  function showIntro(o) {   // o.combined: first launch of the trial (trial points + consent). Otherwise the consent question alone. o.closable: opened by the user from My Page (may leave without answering)
    o = o || {};
    var I = D.intro, Cn = D.consent, end = S && S.trialEndsAt ? mdText(S.trialEndsAt - 1) : '', ask = consentPending(), trial = !!o.combined && !!S && S.phase === 'trial';
    ensureRoot(); var f = $('em-full'); f.setAttribute('data-em-full', 'intro'); f.hidden = false; hideToast();
    var head = trial ? '<h2>' + esc(I.title) + '</h2>' + (C.showDraftMarks ? '<p style="text-align:center">' + mark() + '</p>' : '') + ul([fmt(I.lead, { end: end })].concat(I.items)) : '';
    var acts;
    if (!ask) acts = btn('intro-ok', 'em-go', I.button);
    else acts = '<div class="em-eqacts">' + btn('consent-yes', 'em-eq', trial ? Cn.agreeFirst : Cn.agree) + btn('consent-no', 'em-eq', trial ? Cn.declineFirst : Cn.decline) + '</div>' + (o.closable ? '<div class="em-closerow">' + btn('consent-close', 'em-linkbtn', D.close) + '</div>' : '');
    f.innerHTML = '<div class="em-intro" data-em-intro="' + (ask ? (trial ? 'trial_consent' : 'consent') : 'trial') + '"><div class="em-intro-body" data-em-scroll>' + head +
      (ask ? '<div class="em-consent" data-em-consent-box><h2 class="em-ch2">' + esc(Cn.title) + '</h2><p>' + esc(Cn.lead) + '</p><p><b>' + esc(Cn.freedom) + '</b></p>' +
        '<button type="button" class="em-linkbtn em-morebtn" data-em-act="consent-more" aria-expanded="false">' + esc(Cn.more) + '</button><div class="em-more" data-em-more hidden>' + consentDetails(Cn) + '</div></div>' : '') +
      '</div><div class="em-introacts">' + acts + '</div></div>';
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
    ensureRoot(); var f = $('em-full'); f.setAttribute('data-em-full', 'join'); f.hidden = false; hideToast();
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
    // USER_05 sec 2: the free-trial notice is NOT a coloured box above the button: it is the first paragraph of the notes under the button (same size / format), with the real trial end date
    var trialPara = S && S.phase === 'trial' ? '<p data-em-trialnote>' + esc(fmt(A.trialBuyNotice, { date: trialLastDayText(S) })) + '</p>' : '';
    var paidNote = S && (S.phase === 'paid' || S.phase === 'paid_grace_offline') ? '<div class="em-msg">' + esc(D.alreadyPaid) + '</div>' : '';
    var buy = canBuy ? '<button type="button" class="em-btn em-go" id="em-buy" data-em-act="buy"' + ((busy || waiting || !productOk()) ? ' disabled' : '') + '>' + (busy ? esc(D.working) : '<span class="em-b1">' + esc(fmt(J.button, v)) + '</span><span class="em-b2" data-em-buynote>' + esc(D.buyNote) + '</span>') + '</button>' : '';   // B6 sec 2-11: line 2 says this button starts Apple's purchase
    var pendNote = waiting ? '<div class="em-msg" data-em-pending>' + esc(D.buyPending) + '</div>' : '';
    var terms = '<div class="em-terms" id="em-terms">' + (C.showDraftMarks ? mark() : '') + trialPara + D.terms.map(function (t) { return '<p>' + esc(fmt(t, v)) + '</p>'; }).join('') + '</div>';
    f.innerHTML = '<div class="em-topbar"><button type="button" class="em-back-btn" data-em-act="join-close" aria-label="' + esc(D.back) + '"><span aria-hidden="true">&#8249;</span> ' + esc(D.back) + '</button></div>' +
      '<h2 class="em-jtitle">' + esc(J.title) + '</h2><div class="em-hero"><h1>' + lines(J.main) + '</h1><p>' + esc(J.sub) + '</p></div>' +
      '<div class="em-card"><h3>' + esc(J.meritTitle) + '</h3>' + ul(J.merits) + '</div>' + priceBlock + paidNote + pendNote + buy + (canBuy ? restoreLineHtml() : '') + terms +
      '<div class="em-aux">' +
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
        else if (res === 'already_active') { closeModal(); /* USER_05 G2: a paid contract already exists; the state refresh above shows it (join screen note alreadyPaid). No joined message. */ }
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
  /* B6/B7 (user decision 2026-11-27 USER_03 sec 2-2): the free-article confirmation ("今日の無料記事は〇〇にしますか？") opens ONLY from the user's operation on that article. */
  /* B7 (USER_03 sec 2-2, re-fix; supersedes the B6 time window): NO time window. A guidance / confirmation popup (pick confirmation, paid-only guidance, expired guidance) may only be
     opened from the processing of the user's operation "open / play THIS article": the click handler records a one-shot intent {slug}; only the decision for that slug (our own check
     or a native refusal) can claim it (claiming deletes it). No intent or another slug => nothing is shown (state re-read only). The intent is also deleted by any later gesture start
     (touch / pointer / key = scroll, another tap, long press) and when playback starts. Intent-less sources (history / reload hash change, a native refusal nobody asked for, the route
     restored at launch, the restored queue) never open a popup. */
  var intent = null;
  var INTENT_SEL = '[data-open],[data-play],a[href^="#/player/"],[data-omakase],#pp,#minipp,[data-fromstart],[data-from],[data-solosid],[data-fromsid],[data-pwplay]';
  function decodeSlug(s) { try { return decodeURIComponent(s); } catch (e) { return s; } }
  function intentSlugOf(el) {   // the article the operation means; null = "whatever the app starts" (omakase / mini player)
    var s = el.closest('[data-play]'); if (s) return s.getAttribute('data-play');
    s = el.closest('[data-open]'); if (s) return s.getAttribute('data-open');
    s = el.closest('a[href^="#/player/"]'); if (s) { var hm = /^#\/player\/([^?\/#]+)/.exec(s.getAttribute('href') || ''); return hm ? decodeSlug(hm[1]) : null; }
    var m = PLAYER_RE.exec(root.location.hash || ''); if (m && el.closest('#pp,[data-fromstart],[data-from],[data-solosid],[data-fromsid],[data-pwplay]')) return decodeSlug(m[1]);
    return null;
  }
  function setIntent(el) { intent = { slug: intentSlugOf(el) }; }
  function claimIntent(slug) {   // one-shot: true only when an operation asked for this article (or "whatever starts") and nobody used it yet
    if (!intent) return false;
    if (intent.slug !== null && slug && intent.slug !== slug) return false;
    intent = null; return true;
  }
  function noteGesture(e) { var t = e && e.target; if (t && rootEl && rootEl.contains && rootEl.contains(t)) return; intent = null; }
  ['pointerdown', 'touchstart', 'mousedown', 'keydown'].forEach(function (n) { doc.addEventListener(n, noteGesture, true); });
  function quiet(slug, ctx, why) { try { host.diag && host.diag('js.membership.popup_suppressed', { why: why, route: ctx && ctx.route }); } catch (e) { /* record only */ } refresh(); }
  function dialogForBlocked(slug, ctx, reason) {
    if (!isFree() && !isOffline()) { try { host.diag && host.diag('js.membership.denied_unexpected', { reason: String(reason) }); } catch (e) { /* record only */ } refresh(); return; }   // the plan says this is allowed and the refusal reason is not one the UI knows (any unknown code): never a plan guidance here, only re-read the state
    if (!(ctx && ctx.authorized)) { quiet(slug, ctx, 'no_operation'); return; }   // not the processing of a user operation on this article: no popup / toast of any kind
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
    var iel = t.closest(INTENT_SEL); if (iel) setIntent(iel);   // the operation "open / play this article": the one-shot intent (see above); recorded for allowed articles too (native may still refuse a stale state)
    var om = t.closest('[data-omakase]');
    if (om) { if (isFree()) { intent = null; e.preventDefault(); e.stopImmediatePropagation(); decorateSoon(); } return; }   // the free plan has no omakase (the button is hidden; a stale tap does nothing and no guidance is shown)
    var sq = t.closest('[data-seq]');
    if (sq) { if (isFree()) { intent = null; e.preventDefault(); e.stopImmediatePropagation(); decorateSoon(); } return; }   // the free plan has no continuous play (USER_06; the buttons are hidden): a stale tap starts nothing and no guidance is shown
    var pl = t.closest('[data-play]'), op = pl ? null : t.closest('[data-open]'), src = pl || op;
    if (!src) return;
    var slug = pl ? pl.getAttribute('data-play') : op.getAttribute('data-open');
    if (!slug || canOpenByState(slug)) return;
    e.preventDefault(); e.stopImmediatePropagation();
    blocked(slug, { route: hashName(), authorized: claimIntent(slug), resume: resumeOpen(slug, src) });
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
    blocked(slug, { route: route, authorized: claimIntent(slug), resume: function () { try { root.location.hash = '#/player/' + encodeURIComponent(slug); } catch (x) { /* */ } } });   // authorized only when a tap on a link to this article asked for it; history / reload / external hash changes are silent
  });

  /* ------------------------------------------------------------------ native refusals (accessDenied) */
  var deferredDenied = null;
  var EXPLICIT_POINTS = { loadQueue: 1, download: 1, playItem: 1, replaceQueueItem: 1, fetch: 1 };
  var lastFetchDenied = { slug: '', t: 0 };
  function showDenied(d, authorized) {   // authorized = this refusal answers a user operation (the intent was claimed when it arrived)
    var slug = d && d.slug;
    if (!slug) { if (authorized) toast(D.deniedToast); else quiet('', null, 'no_operation'); return; }
    blocked(slug, { route: hashName(), authorized: !!authorized, resume: function () { try { root.location.hash = '#/player/' + encodeURIComponent(slug); } catch (e) { /* */ } } });
  }
  M.on('accessDenied', function (d) {
    if (!d || d.point === 'prefetchClip') return;   // silent background prefetch: nothing to tell the user
    if (d.reason === 'slug_mismatch' || d.reason === 'bad_slug') { try { host.diag && host.diag('js.membership.denied_bad_id', { point: d.point, reason: d.reason }); } catch (e) { /* record only */ } return; }   // an id/URL fault, not a plan matter: no dialog (log only)
    if (d.point === 'playItem' && onReviewRoute()) { refresh(); try { host.diag && host.diag('js.membership.review_audio_refused', { reason: d.reason }); } catch (e) { /* record only */ } return; }   // review-book audio is playable in every plan (user decision 2026-11-26 USER_02 sec 3-2): never a restriction / join notice here
    if (d.point === 'autoNext') { refresh(); return; }   // a free member finishing the picked article is refused auto-advance every time (normal): silent; notices come only from popupDue
    if (d.point === 'download') { refresh().then(function () { if (!modalOpen()) toast(D.deniedToast); }); return; }   // answers the user's own save tap (no article popup)   // a refused save: one short notice, no dialog (saved files stay)
    if (d.point === 'fetch') {   // article data refused (the UI state was stale, e.g. the plan changed at midnight): one explanation per article, and leave the broken article page
      var tn = nowMs(); if (lastFetchDenied.slug === d.slug && tn - lastFetchDenied.t < 3000) return; lastFetchDenied = { slug: d.slug, t: tn };
    }
    var mine = claimIntent(d.slug);   // B7: only a refusal that answers the user's operation on this article may show anything
    refresh().then(function () {
      if (d.point === 'fetch' && PLAYER_RE.test(root.location.hash || '') && !canOpenByState(d.slug)) { try { root.history.replaceState(null, '', '#/home'); root.dispatchEvent(new root.Event('hashchange')); } catch (e) { /* */ } }
      if (!mine) { quiet(d.slug, null, 'refusal_without_operation:' + d.point); return; }   // restored queue at launch, background refusals, a refusal after a scroll / other tap: silent
      if (isPlaying()) { toast(D.deniedToast); return; }                // never put a popup in front of playback
      if (onListRoute() || EXPLICIT_POINTS[d.point]) { if (!modalOpen()) showDenied(d, true); else toast(D.deniedToast); return; }
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
    if (deferredDenied && onListRoute()) { var d = deferredDenied; deferredDenied = null; showDenied(d, true); return; }   // the deferred explanation answers an operation that was claimed when the refusal arrived
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
      case 'consent-more': { var mb = $('em-full') && $('em-full').querySelector('[data-em-more]'); if (mb) { var open = mb.hidden; mb.hidden = !open; el.setAttribute('aria-expanded', open ? 'true' : 'false'); el.textContent = open ? D.consent.less : D.consent.more; if (open) { try { mb.scrollIntoView({ block: 'nearest' }); } catch (e) { /* */ } } } return; }
      case 'consent-toggle':
        if (consentInfo && consentInfo.consent === 'unanswered') { if (!fullName() && !modalOpen()) showIntro({ closable: true }); return; }   // never answered: show the full explanation first
        chooseConsent(consentInfo && consentInfo.consent === 'granted' ? 'denied' : 'granted', false); return;
      case 'confirm-ok': doConfirm(el.getAttribute('data-slug'), el); return;
      case 'expired-pick': { var sl = el.getAttribute('data-slug'), c = modalCtx; closeModal(); showConfirm(sl, c || { route: hashName(), resume: function () { try { root.location.hash = '#/player/' + encodeURIComponent(sl); } catch (x) { /* */ } } }); return; }
      case 'buy': doBuy(); return;
      case 'manage': doManage(); return;
      case 'restore': closeModal(); doRestore(); return;
      case 'restore-help': simpleNotice('restore_help', A.restore.name, A.restore.help); return;
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
  // USER_05 sec 6: the purchase-restore entry sits right under a join button: a quiet text link + a "?" help button (the explanation opens on tap; it is not shown all the time)
  function restoreLineHtml() {
    var R = A.restore;
    return '<div class="em-restoreline" data-em-restoreline><button type="button" class="em-rlink" data-em-act="restore">' + esc(R.name) + '</button><button type="button" class="em-help" data-em-act="restore-help" aria-label="' + esc(D.restoreHelpAria) + '"><span class="em-q" aria-hidden="true">?</span></button></div>';
  }
  function planCardHtml() {
    var St = A.settings, DS = D.settings, v = priceVars(), h = '<div class="em-plan" data-em-plan="' + esc(S.phase) + (S.paidCancelled ? ':cancelled' : '') + '"><div class="em-pl0">' + esc(St.planLabel) + '</div>';
    if (S.phase === 'trial') {
      h += '<div class="em-pn">' + esc(St.trial) + '</div><div class="em-pr"><span>' + esc(St.trialEndDate) + '</span><span>' + esc(ymdText(S.trialEndsAt - 1)) + '</span></div><p>' + esc(DS.trialA) + '</p><p>' + esc(DS.trialB) + '</p>' + btn('join', 'em-go', St.join) + restoreLineHtml();
    } else if (S.phase === 'free') {
      h += '<div class="em-pn">' + esc(St.free) + '</div><p>' + esc(DS.freeA) + '</p><p>' + esc(DS.freeB) + '</p><div class="em-pr"><span>' + esc(DS.freeJoinLabel) + '</span><span>' + esc(fmt(St.monthlyShort, v)) + '</span></div>' + btn('join', 'em-go', St.join) + restoreLineHtml();
    } else {   // paid / paid_grace_offline
      h += '<div class="em-pn">' + esc(St.paid) + '</div>';
      if (S.paidCancelled) h += '<div class="em-pr"><span>' + esc(St.contractState) + '</span><span>' + esc(St.stoppedAuto) + '</span></div><div class="em-pr"><span>' + esc(St.expiry) + '</span><span>' + esc(S.paidExpiresAt ? ymdText(S.paidExpiresAt) : '') + '</span></div><p>' + esc(DS.paidCancelledA) + '</p>';
      else h += '<div class="em-pr"><span>' + esc(DS.priceLabel) + '</span><span>' + esc(fmt(St.monthly, v)) + '</span></div><div class="em-pr"><span>' + esc(St.nextRenewal) + '</span><span>' + esc(S.paidExpiresAt ? ymdText(S.paidExpiresAt) : '') + '</span></div><p>' + esc(DS.paidA) + '</p>';
      if (S.phase === 'paid_grace_offline') h += '<p class="em-sub">' + esc(D.grace) + '</p>';
      h += btn('manage', 'em-stay', S.paidCancelled ? D.manageRowCancelled : D.manageRow);
    }
    return h + '</div>';
  }
  /* ---- offline saving: drawn entirely by the common webapp (USER_05 sec 1; the usage line, the "保存した記事" row on My Page and the list screen #/me/saved are its own code, so nothing is trimmed or redrawn here).
     This overlay only keeps out of the way on the list screen (no plan card / procedures block there). */
  function meArg() { var h = (root.location.hash || '').replace(/^#\/?/, ''); return h.split(/[?#]/)[0].split('/')[1] || ''; }
  function savedMode() { return hashName() === 'me' && meArg() === 'saved'; }
  function legalHeadEl(v) { return [].filter.call(v.querySelectorAll('.pl'), function (n) { return /サポート・規約/.test(n.textContent); })[0] || null; }
  function decorateMe(v) {
    if (savedMode()) return;   // the saved-article list screen is the common webapp's own
    var old = v.querySelector('[data-em-plan]');
    if (hashName() !== 'me' || !S) { if (old) old.remove(); var ob = v.querySelector('[data-em-other]'); if (ob) ob.remove(); var ocs = v.querySelector('[data-em-consent-set]'); if (ocs) ocs.remove(); [].forEach.call(v.querySelectorAll('[data-em-legal-row]'), function (n) { n.remove(); }); return; }
    var want = planCardHtml();
    if (!old || old.outerHTML !== want) {
      var h = doc.createElement('div'); h.innerHTML = want; var nb = h.firstChild;
      if (old) old.replaceWith(nb); else { var h2 = v.querySelector('h2'); if (h2 && h2.parentNode) h2.parentNode.insertBefore(nb, h2.nextSibling); else v.insertBefore(nb, v.firstChild); }
    }
    // "その他の手続き": only the contract-management entry, and only for paid states (USER_05 sec 6: the purchase restore link sits under the join buttons; a block with nothing left is not drawn)
    var paidNow = S.phase === 'paid' || S.phase === 'paid_grace_offline';
    var otherWant = paidNow ? '<div class="em-other" data-em-other><div class="em-pl" id="em-other-procs">' + esc(A.restore.sectionTitle) + '</div><div class="em-restorebox"><button type="button" class="setrow" data-em-act="manage">' + esc(S.paidCancelled ? D.manageRowCancelled : D.manageRow) + '<span>&#8250;</span></button></div></div>' : '';
    var oo = v.querySelector('[data-em-other]');
    if (!otherWant) { if (oo) oo.remove(); }
    else if (!oo || oo.outerHTML !== otherWant) {
      var h3 = doc.createElement('div'); h3.innerHTML = otherWant; var nn = h3.firstChild;
      if (oo) oo.replaceWith(nn);
      else {
        var anchorEl = v.querySelector('[data-em-consent-set]') || legalHeadEl(v);
        if (anchorEl && anchorEl.parentNode) anchorEl.parentNode.insertBefore(nn, anchorEl); else v.appendChild(nn);
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
    // consent switch (only when the app has the usage-data plugin and it is available)
    var oc = v.querySelector('[data-em-consent-set]');
    if (!consentAvailable()) { if (oc) oc.remove(); }
    else {
      var CS = D.consentSettings, st2 = consentInfo.consent, stLabel = st2 === 'granted' ? CS.on : (st2 === 'denied' ? CS.off : CS.unanswered);
      var consWant = '<div data-em-consent-set data-em-sig="' + esc(st2 + '|' + consentMsg) + '"><div class="pl">' + esc(CS.section) + '</div>' +
        '<button type="button" class="setrow em-swrow" role="switch" aria-checked="' + (st2 === 'granted' ? 'true' : 'false') + '" data-em-act="consent-toggle"><span class="em-swlabel">' + esc(CS.row) + '</span><span class="em-swstate" data-em-consent-state>' + esc(stLabel) + '</span><span class="em-switch" aria-hidden="true"><i></i></span></button>' +   // B6 sec 2-10: a real switch (colour + knob position + state word)
        '<div class="lvnote" data-em-consent-note>' + esc(CS.note) + '</div><div class="lvnote" data-em-consent-msg role="status">' + esc(consentMsg) + '</div>' + '</div>';
      if (!oc || oc.getAttribute('data-em-sig') !== st2 + '|' + consentMsg) {
        var h4 = doc.createElement('div'); h4.innerHTML = consWant; var cn = h4.firstChild;
        if (oc) oc.replaceWith(cn);
        else { var oo2 = v.querySelector('[data-em-other]'), lh2 = legalHeadEl(v); if (oo2 && oo2.parentNode) oo2.parentNode.insertBefore(cn, oo2.nextSibling); else if (lh2 && lh2.parentNode) lh2.parentNode.insertBefore(cn, lh2); else v.appendChild(cn); }
      }
    }
  }
  function decorateOmakase(v) {   // the free plan has no omakase (user decision 2026-11-26 USER_02 sec 3-3): the whole section is hidden (no empty space); trial / paid are untouched
    var s = v.querySelector('#omakase'); if (!s) return;
    if (isFree()) { if (!s.hasAttribute('data-em-hidden')) { s.setAttribute('data-em-hidden', '1'); s.hidden = true; s.style.display = 'none'; } }
    else if (s.hasAttribute('data-em-hidden')) { s.removeAttribute('data-em-hidden'); s.hidden = false; s.style.display = ''; }
  }
  function hideEl(el, on) {   // fully removed from the layout (display:none, not greyed out); restored when the plan allows it again
    if (on) { if (!el.hasAttribute('data-em-hidden')) { el.setAttribute('data-em-hidden', '1'); el.hidden = true; el.style.display = 'none'; } }
    else if (el.hasAttribute('data-em-hidden')) { el.removeAttribute('data-em-hidden'); el.hidden = false; el.style.display = ''; }
  }
  function decorateSeq(v) {   // user decision 2026-11-27 USER_06 sec 2 / 3: the free plan has no continuous play on the lists (all articles / each genre): the two buttons (.seqbtns [data-seq]) and the note that only explains continuous play are hidden
    var free = isFree(), bars = v.querySelectorAll('.seqbtns');
    for (var i = 0; i < bars.length; i++) {
      var b = bars[i]; hideEl(b, free);
      var n = b.nextElementSibling;   // the note directly under the buttons ("continuous play also uses the selected level"); only that one note (the p.lvnote right after the bar; no word matching: W2 keeps wording out of this file); every other note stays
      if (n && n.classList && n.classList.contains('lvnote') && n.tagName === 'P') hideEl(n, free);
    }
    var lone = v.querySelectorAll('[data-seq]');   // a [data-seq] button outside a .seqbtns bar (a changed webapp): hidden the same way
    for (var j = 0; j < lone.length; j++) if (!lone[j].closest('.seqbtns')) hideEl(lone[j], free);
  }
  /* C14 (USER_06 sec 3 "continuous play does not exist for the free plan"; Fable decision on C13 candidate 1): when a trial / paid session that was playing a queue turns into the free plan, the mini player must not show
     "連続再生 n/N" and the webapp's toast "連続再生: 次は…" must not appear. Display only: the audio behaviour (the selected article plays to its end, then stops = USER_04 sec 8) is native/adapter and is not touched. Trial / paid: nothing is changed. */
  var CONT_MINI_RE = / · 連続再生 \d+\/\d+$/, CONT_TOAST_RE = /^連続再生: 次は/, moMini = null, moToast = null;
  function stripContMini() {
    if (!isFree()) return;
    var m = doc.getElementById('minilv'); if (!m) return;
    var t = m.textContent; if (t && CONT_MINI_RE.test(t)) m.textContent = t.replace(CONT_MINI_RE, '');
  }
  function hideContToast() {
    if (!isFree()) return;
    var t = doc.getElementById('toast'); if (t && !t.hidden && CONT_TOAST_RE.test(t.textContent || '')) t.hidden = true;
  }
  function watchCont() {
    if (!root.MutationObserver) return;
    var mini = doc.getElementById('mini'), tt = doc.getElementById('toast');
    if (mini && !moMini) { moMini = new root.MutationObserver(stripContMini); moMini.observe(mini, { childList: true, characterData: true, subtree: true }); }
    if (tt && !moToast) { moToast = new root.MutationObserver(hideContToast); moToast.observe(tt, { childList: true, characterData: true, attributes: true, attributeFilter: ['hidden'] }); }
    stripContMini(); hideContToast();
  }
  function decorate() {
    var v = view || (view = $('view')); if (!v) return;
    watchCont();
    if (mo) mo.disconnect();
    try { decorateCards(v); decorateBar(v); decorateOmakase(v); decorateSeq(v); decorateMe(v); } catch (e) { try { host.diag && host.diag('js.membership.ui_error', { msg: String(e && e.message) }); } catch (x) { /* */ } }
    if (mo) mo.observe(v, { childList: true, subtree: true });
  }

  /* ------------------------------------------------------------------ start */
  function init() {
    view = $('view');
    if (view && root.MutationObserver) { mo = new root.MutationObserver(function () { decorateSoon(); }); mo.observe(view, { childList: true, subtree: true }); }
    var a = host.audioEl; if (a && a.addEventListener) { a.addEventListener('pause', scheduleCheck); a.addEventListener('ended', scheduleCheck); }
    doc.addEventListener('visibilitychange', function () { if (!doc.hidden) { refresh(); scheduleCheck(); } });
    try { if (host.audioEl && host.audioEl.addEventListener) host.audioEl.addEventListener('playing', function () { intent = null; }); } catch (e) { /* cosmetic: the intent is also deleted by the next gesture */ }   // the operation succeeded: its intent is spent
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
