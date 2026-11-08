/* PWA-BACKGROUND-AUDIO-TRIAL-01 独立Trial。Production非参照。外部ライブラリなし。
   A = End User player(rev01-t)同等: audio要素1個・src差替+load()・pause方式・MediaSession/AudioSession設定なし
   B = A + 再生開始直前に navigator.audioSession.type="playback"
   C = A + Media Session明示設定のみ(metadata/playbackState同期/action handler/setPositionState。audioSessionは設定しない)
   D = B + C 併用(audioSession.type="playback" + Media Session)
   A/Bは MediaSession playbackState の読取のみ(設定・action handler追加はしない) */
(function () {
  'use strict';
  var qs = new URLSearchParams(location.search);
  var VARIANT = (qs.get('v') || '').toUpperCase();
  if ('ABCD'.indexOf(VARIANT) < 0 || VARIANT.length !== 1) VARIANT = '?';
  var USE_AS = VARIANT === 'B' || VARIANT === 'D';
  var USE_MS = VARIANT === 'C' || VARIANT === 'D';
  var CLIPS = [
    '../family_x_ai_chat_sponsored_persuasion_02/audio/std_00.mp3',
    '../family_x_ai_chat_sponsored_persuasion_02/audio/std_02.mp3',
    '../family_x_ai_chat_sponsored_persuasion_02/audio/std_03.mp3',
    '../family_x_ai_chat_sponsored_persuasion_02/audio/std_06.mp3',
    '../family_x_ai_chat_sponsored_persuasion_02/audio/std_09.mp3'
  ];
  var RUN_ID = new Date().toISOString().replace(/[:.]/g, '-') + '_' + VARIANT;
  var KEY_PREFIX = 'pwa_bg_trial_01:';
  var KEY = KEY_PREFIX + RUN_ID;
  var T0 = performance.now();
  var lines = [];
  var $ = function (id) { return document.getElementById(id); };
  var A = $('aud');
  var idx = 0;

  function fmt(v) { return v === undefined || v === null ? 'n/a' : String(v); }
  function asState() { try { return 'audioSession' in navigator ? fmt(navigator.audioSession.state) : 'unsupported'; } catch (e) { return 'err:' + e.name; } }
  function asType() { try { return 'audioSession' in navigator ? fmt(navigator.audioSession.type) : 'unsupported'; } catch (e) { return 'err:' + e.name; } }
  function msState() { try { return 'mediaSession' in navigator ? fmt(navigator.mediaSession.playbackState) : 'unsupported'; } catch (e) { return 'err:' + e.name; } }
  function clip() { var s = A.currentSrc || A.src || ''; return s ? s.split('/').pop() : '-'; }

  function save() { try { localStorage.setItem(KEY, lines.join('\n')); } catch (e) { /* 容量超過等: 画面ログのみ */ } }
  function log(ev, extra) {
    var row = [
      new Date().toISOString(), '+' + ((performance.now() - T0) / 1000).toFixed(1) + 's', ev,
      'ms=' + msState(), 'paused=' + A.paused, 'ct=' + (A.currentTime || 0).toFixed(2), 'rs=' + A.readyState,
      'as=' + asState(), 'at=' + asType(), 'vis=' + document.visibilityState, 'clip=' + clip(), 'v=' + VARIANT
    ].join(' | ') + (extra ? ' | ' + extra : '');
    lines.push(row); save();
    var el = $('log'); if (el) { el.textContent = lines.slice(-60).join('\n'); el.scrollTop = el.scrollHeight; }
    status();
    return row;
  }
  function status() {
    var el = $('status'); if (!el) return;
    el.textContent = 'clip ' + (idx + 1) + '/' + CLIPS.length + ' ' + clip() + '  paused=' + A.paused + '  ct=' + (A.currentTime || 0).toFixed(1) +
      '\nmediaSession.playbackState=' + msState() + '  audioSession.state=' + asState() + '  type=' + asType();
  }

  function setPlayback() {   // Variant B/Dのみ。play()直前
    if (USE_AS) {
      if ('audioSession' in navigator) { try { navigator.audioSession.type = 'playback'; log('audioSession.type=playback set', 'type now=' + asType()); } catch (e) { log('audioSession.type set failed', e.name); } }
      else log('audioSession unsupported (B/D設定スキップ)');
    }
  }
  function playNow() { var pr = A.play(); if (pr && pr.catch) pr.catch(function (e) { log('play() rejected', e.name); }); }
  function load(i) { idx = i; A.src = CLIPS[i]; A.load(); msMeta(); }   // Aと同じ: src差替+load()
  function startFrom(i) { setPlayback(); load(i); playNow(); }

  $('btnPlay').addEventListener('click', function () { log('btn:play(先頭から)'); startFrom(0); });
  $('btnPP').addEventListener('click', function () {
    if (!A.src) { log('btn:pp(未開始→先頭から)'); startFrom(0); return; }
    if (A.paused) { log('btn:resume'); setPlayback(); playNow(); } else { log('btn:pause'); A.pause(); }
  });
  $('btnNext').addEventListener('click', function () { log('btn:next'); startFrom((idx + 1) % CLIPS.length); });
  $('btnMark').addEventListener('click', function () { log('MEMO', $('memo').value); $('memo').value = ''; });
  $('btnClear').addEventListener('click', function () {
    if (!confirm('この起動のログを消去しますか')) return;
    lines = []; save(); $('log').textContent = ''; log('log cleared');
  });
  A.addEventListener('ended', function () {
    log('ended');
    var n = idx + 1;
    if (n >= CLIPS.length) { if ($('chkLoop').checked) n = 0; else { log('playlist end'); msState_set('none'); return; } }
    load(n); playNow();   // ended→次クリップ(ユーザー操作外のsrc差替=実機での継続可否も観測対象)
  });

  ['play', 'playing', 'pause', 'seeking', 'seeked', 'stalled', 'suspend', 'waiting', 'emptied', 'abort', 'error', 'loadedmetadata'].forEach(function (n) {
    A.addEventListener(n, function () { log('audio:' + n, n === 'error' && A.error ? 'code=' + A.error.code : ''); });
  });

  document.addEventListener('visibilitychange', function () { log('visibilitychange'); });
  ['pagehide', 'pageshow', 'focus', 'blur', 'freeze', 'resume'].forEach(function (n) {
    (n === 'freeze' || n === 'resume' ? document : window).addEventListener(n, function (e) { log(n, e && e.persisted !== undefined ? 'persisted=' + e.persisted : ''); });
  });
  if ('audioSession' in navigator && navigator.audioSession.addEventListener) navigator.audioSession.addEventListener('statechange', function () { log('audioSession:statechange'); });
  setInterval(function () { log('heartbeat'); }, 10000);

  /* ---- Media Session (C/D のみ有効。A/Bでは一切呼ばない) ---- */
  var MS_OK = USE_MS && ('mediaSession' in navigator);
  var msLastPos = 0;
  function msState_set(st) {
    if (!MS_OK) return;
    try { navigator.mediaSession.playbackState = st; log('ms:playbackState=' + st + ' set', 'readback=' + msState()); } catch (e) { log('ms:playbackState set failed', e.name); }
  }
  function msMeta() {
    if (!MS_OK) return;
    try {
      if (typeof MediaMetadata === 'undefined') { log('ms:MediaMetadata unsupported'); return; }
      navigator.mediaSession.metadata = new MediaMetadata({ title: 'Trial clip ' + (idx + 1) + '/' + CLIPS.length + ' (' + clip() + ')', artist: 'eigo-radio PWA BG Trial', album: 'Variant ' + VARIANT });   // artworkなし(外部/新規画像を使わない)
      log('ms:metadata set', 'title=' + navigator.mediaSession.metadata.title);
    } catch (e) { log('ms:metadata set failed', e.name); }
  }
  function msPos() {
    if (!MS_OK || !navigator.mediaSession.setPositionState) return;
    var d = A.duration;
    if (!isFinite(d) || d <= 0) return;
    try { navigator.mediaSession.setPositionState({ duration: d, playbackRate: A.playbackRate || 1, position: Math.min(A.currentTime || 0, d) }); }
    catch (e) { log('ms:setPositionState failed', e.name); }
  }
  function msHandler(action, fn) {
    try {
      navigator.mediaSession.setActionHandler(action, function (details) {
        log('ms:' + action, 'src=remote' + (details && details.seekOffset ? ' seekOffset=' + details.seekOffset : ''));
        fn(details);
      });
      log('ms:handler registered', action);
    } catch (e) { log('ms:handler unsupported', action + ' (' + e.name + ')'); }
  }
  if (USE_MS) {
    if (!('mediaSession' in navigator)) log('ms:mediaSession unsupported (C/D設定スキップ)');
    else {
      msHandler('play', function () { setPlayback(); if (!A.src) startFrom(0); else playNow(); });
      msHandler('pause', function () { A.pause(); });
      msHandler('nexttrack', function () { startFrom((idx + 1) % CLIPS.length); });
      msHandler('previoustrack', function () { startFrom((idx + CLIPS.length - 1) % CLIPS.length); });
      msHandler('seekbackward', function (d) { A.currentTime = Math.max(0, (A.currentTime || 0) - ((d && d.seekOffset) || 10)); msPos(); });
      msHandler('seekforward', function (d) { A.currentTime = Math.min(A.duration || 1e9, (A.currentTime || 0) + ((d && d.seekOffset) || 10)); msPos(); });
      msMeta();
      A.addEventListener('playing', function () { msState_set('playing'); msPos(); });
      A.addEventListener('pause', function () { if (!A.ended) msState_set('paused'); });
      A.addEventListener('loadedmetadata', msPos);
      A.addEventListener('seeked', msPos);
      var lastTick = 0;
      A.addEventListener('timeupdate', function () { var t = Date.now(); if (t - lastTick > 5000) { lastTick = t; msPos(); } });
    }
  }

  /* ---- export ---- */
  function allText() {
    var hdr = ['# PWA-BG-AUDIO-TRIAL-01 log', 'run=' + RUN_ID, 'variant=' + VARIANT + ' (' + (CFG[VARIANT] || '?') + ')', 'UA=' + navigator.userAgent, 'url=' + location.href, ''];
    return hdr.concat(lines).join('\n');
  }
  function copyText(t) {
    if (navigator.clipboard && navigator.clipboard.writeText) return navigator.clipboard.writeText(t);
    return new Promise(function (res, rej) { var ta = document.createElement('textarea'); ta.value = t; document.body.appendChild(ta); ta.select(); try { document.execCommand('copy') ? res() : rej(new Error('execCommand false')); } catch (e) { rej(e); } document.body.removeChild(ta); });
  }
  $('btnCopy').addEventListener('click', function () { copyText(allText()).then(function () { log('export:copy ok'); }, function (e) { log('export:copy failed', e && e.name); }); });
  $('btnShare').addEventListener('click', function () {
    if (!navigator.share) { log('export:share unsupported'); return; }
    navigator.share({ title: 'PWA BG Audio Trial log', text: allText() }).then(function () { log('export:share ok'); }, function (e) { log('export:share failed', e && e.name); });
  });
  $('btnDl').addEventListener('click', function () {
    try {
      var b = new Blob([allText()], { type: 'text/plain' }), a = document.createElement('a');
      a.href = URL.createObjectURL(b); a.download = 'pwa_bg_trial_' + RUN_ID + '.txt'; document.body.appendChild(a); a.click(); document.body.removeChild(a);
      log('export:download triggered');
    } catch (e) { log('export:download failed', e.name); }
  });

  /* ---- 起動 ---- */
  var CFG = { A: 'audioSession=未設定 / MediaSession=未設定(Production現行同等)', B: 'audioSession.type=playback / MediaSession=未設定',
              C: 'audioSession=未設定 / MediaSession=明示設定(metadata+playbackState+handler+position)', D: 'audioSession.type=playback + MediaSession=明示設定(併用)' };
  var v = $('variant'); v.textContent = 'Variant ' + VARIANT + ': ' + (CFG[VARIANT] || '不明(?v=A|B|C|D)'); v.className = 'variant ' + VARIANT;
  var standalone = (navigator.standalone === true) || (window.matchMedia && matchMedia('(display-mode: standalone)').matches);
  $('env').textContent = 'run=' + RUN_ID + '\nUA=' + navigator.userAgent + '\nstandalone=' + standalone +
    '\naudioSession=' + ('audioSession' in navigator ? '対応' : '非対応') + '  mediaSession=' + ('mediaSession' in navigator ? '存在' : 'なし') +
    '\n保存済み起動ログ(localStorage): ' + Object.keys(localStorage).filter(function (k) { return k.indexOf(KEY_PREFIX) === 0; }).length + '件';
  if (VARIANT === '?') log('WARNING: ?v=A|B|C|D を指定してください');
  log('boot', 'standalone=' + standalone + ' audioSession=' + ('audioSession' in navigator ? 'supported' : 'unsupported') + ' mediaSession=' + ('mediaSession' in navigator ? 'present' : 'absent'));

  if (qs.get('dump') === '1') {   // 過去起動分を含めた全ログ表示
    var d = $('dump'); d.hidden = false;
    var out = [];
    Object.keys(localStorage).filter(function (k) { return k.indexOf(KEY_PREFIX) === 0; }).sort().forEach(function (k) { out.push('=== ' + k + ' ===\n' + localStorage.getItem(k)); });
    d.textContent = out.join('\n\n');
  }
  window.__TRIAL = { log: log, allText: allText, variant: VARIANT };
})();
