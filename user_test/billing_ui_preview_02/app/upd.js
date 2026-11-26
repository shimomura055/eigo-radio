/* WEBAPP-PWA-UPDATE-DELIVERY-01: 既存端末(iOSホーム画面/Android/PC)を再インストールなしで最新版へ更新する起動時・復帰時の版確認。
   版=index.html の <meta name="wut-build">(build時に tools/webapp_build_stamp_01.py が内容shaから書く)。最新版=version.json(cache-bust付き・no-store)。
   異なれば location.reload() で最新 index.html を取り直す(全assetの ?v= も同じbuild idなので新URLになりHTTPキャッシュに依らない)。
   reloadしない条件(次回起動/復帰へ繰延): 音声再生中 / チュートリアル表示中 / 復習セッション中 / 入力中 / 起動直後でもユーザー操作済み。
   保存データ(localStorage wut01.*)・IndexedDBには一切触れない。Service Worker・新UI・更新案内表示は使わない(未承認)。 */
(function () {
  'use strict';
  var meta = document.querySelector('meta[name="wut-build"]'), CUR = meta && meta.getAttribute('content');
  if (!CUR) return;
  var KEY = 'wutupd.try', inflight = false, lastAt = 0, interacted = false;   // KEYはsessionStorage(reload無限ループ防止専用。保存データ領域ではない)
  ['pointerdown', 'keydown', 'touchstart'].forEach(function (ev) { addEventListener(ev, function () { interacted = true; }, { capture: true, passive: true }); });
  function ss(f) { try { return f(window.sessionStorage); } catch (e) { return null; } }
  function tries(b) { var v = ss(function (s) { return s.getItem(KEY); }); if (!v) return 0; var a = v.split('|'); return a[0] === b ? (+a[1] || 0) : 0; }
  function busy(reason) {
    var a = document.getElementById('aud'), t = document.getElementById('tut'), ae = document.activeElement;
    if (a && !a.paused && !a.ended) return 'audio_playing';
    if (t && !t.hidden) return 'tutorial_open';
    if (document.querySelector('#srsroot [data-srs-view="ask"], #srsroot [data-srs-view="answer"]')) return 'review_session';
    if (ae && (ae.tagName === 'INPUT' || ae.tagName === 'TEXTAREA' || ae.isContentEditable)) return 'text_input';
    if (reason === 'start' && interacted) return 'user_interacted';
    return '';
  }
  function remote() {
    return fetch('version.json?t=' + Date.now(), { cache: 'no-store' }).then(function (r) { return r.ok ? r.json() : null; })
      .then(function (j) { return j && j.schema === 'wut_version_v1' && /^[0-9a-f]{12}$/.test(j.build) ? j.build : null; }).catch(function () { return null; });
  }
  function go(b) {
    var n = tries(b); if (n >= 2) return 'give_up';   // CDN不整合等で直らない場合の無限reload防止(次の復帰/起動で再試行)
    ss(function (s) { s.setItem(KEY, b + '|' + (n + 1)); });
    if (n === 0) { location.reload(); return 'reload'; }
    var u = new URL(location.href); u.searchParams.set('_b', b); location.replace(u.toString()); return 'reload_busted';   // 2回目: index.html自体のURLを変えてHTTPキャッシュを回避(hash保持)
  }
  function check(reason) {
    if (inflight) return Promise.resolve('inflight'); inflight = true; lastAt = Date.now();
    return remote().then(function (b) {
      inflight = false;
      if (!b) return 'unknown';
      if (b === CUR) { ss(function (s) { s.removeItem(KEY); }); return 'current'; }
      var why = busy(reason); if (why) return 'deferred:' + why;
      return go(b);
    });
  }
  function soon(reason) { if (Date.now() - lastAt > 3000) check(reason); }
  try { var q = new URL(location.href); if (q.searchParams.get('_b') === CUR) { q.searchParams.delete('_b'); history.replaceState(history.state, '', q.pathname + q.search + q.hash); } } catch (e) { }   // 更新後は掃除用の ?_b= を外す
  document.addEventListener('visibilitychange', function () { if (document.visibilityState === 'visible') soon('resume'); });
  addEventListener('pageshow', function (e) { if (e.persisted) soon('resume'); });
  addEventListener('online', function () { soon('online'); });
  window.WUTUpd = { build: CUR, check: check, busy: busy };
  check('start');
})();
