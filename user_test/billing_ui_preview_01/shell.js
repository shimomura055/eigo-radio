/* プレビュー専用の操作パネル(アプリ画面 app.html の外)。window.PV(app.js)を呼ぶだけ。 */
(function () {
  'use strict';
  var $ = function (id) { return document.getElementById(id); };
  var frame = $('frame'), PVs = null, lastScreen = 0, busy = false;
  function PV() { var w = frame.contentWindow; return w && w.PV_READY ? w.PV : null; }
  var SCREENS = [
    ['初回利用時の無料体験案内', '「初回起動を再現」。無料体験の案内(1/2)→利用状況の送信の同意確認(2/2)の初回フロー(文言案)'],
    ['無料体験中の記事一覧・残り日数', '状態「無料体験中」→ ホーム上部の「全機能無料体験中 あとN日」'],
    ['無料体験終了時のポップアップ', '状態「無料体験終了直後」→ ホームに1回だけ表示'],
    ['無料記事選択・確認画面', '状態「無料会員・当日記事未選択」→ 記事の▶を押す'],
    ['無料会員の記事一覧・ロック表示', '状態「無料会員・当日記事選択済み」→ ホームの他記事に鍵アイコン'],
    ['利用不可記事の選択時の加入案内', '状態「無料会員・当日記事選択済み」→ 鍵の付いた記事の▶/鍵を押す'],
    ['7日ごとの定期販促ポップアップ', '無料会員で「前回表示から7日以上」→ ホームを開くと表示'],
    ['有料会員加入画面', '各ポップアップ・設定画面の「有料会員になる」から遷移'],
    ['無料体験中の有料加入時の注意表示', '状態「無料体験中」→ 設定の「有料会員になる」→ 加入画面の黄色い注意'],
    ['有料契約終了時のポップアップ', '状態「有料契約終了後」→ ホームに1回だけ表示'],
    ['ダウンロード済み記事の利用期限切れ案内', '無料会員で保存済みの利用不可記事を、マイページの保存一覧から押す(文言案)'],
    ['各会員状態の設定画面', 'マイページを開き、状態ボタンで切替(無料体験中/無料会員/有料/解約済み)'],
    ['購入復元・契約管理への導線', 'マイページ「その他の手続き」の「購入を復元する」、有料時の「契約内容の確認・解約」'],
    ['(追加)利用状況の送信の同意確認', '初回案内の2画面目(「同意する」「同意しない」)と、マイページ「利用状況の送信」ON/OFF(文言案)']
  ];
  function applyShortcut(n) {
    var p = PV(); if (!p) return;
    var it = p.items();
    var run = {
      1: function () { p.preset('trial'); p.reshow('intro'); },
      2: function () { p.preset('trial'); },
      3: function () { p.preset('trial_end'); },
      4: function () { p.preset('free_unsel'); p.request(it[1].slug, 'play'); },
      5: function () { p.preset('free_sel'); },
      6: function () { p.preset('free_sel'); p.request(it[0].slug, 'play'); },
      7: function () { p.preset('free_unsel'); p.reshow('promo'); },
      8: function () { p.preset('free_unsel'); p.nav('sub'); },
      9: function () { p.preset('trial'); p.nav('sub'); },
      10: function () { p.preset('expired'); },
      11: function () { p.preset('free_sel'); p.nav('me'); p.request(it[5].slug, 'play'); },
      12: function () { p.preset('paid'); p.nav('me'); },
      13: function () { p.preset('free_unsel'); p.nav('me'); setTimeout(function () { p.scrollTo('other-procs'); }, 80); },
      14: function () { p.preset('trial'); p.reshow('intro'); setTimeout(function () { var w = document.getElementById('frame').contentWindow; var b = w.document.querySelector('[data-act=intro-next]'); if (b) b.click(); }, 120); }
    }[n];
    run(); lastScreen = n; sync();
  }
  function build() {
    var ol = $('screens');
    ol.innerHTML = SCREENS.map(function (s, i) { return '<li data-n="' + (i + 1) + '"><span class="n">' + (i + 1) + '</span><button type="button" data-shortcut="' + (i + 1) + '" title="' + s[1] + '">' + s[0] + '<br><small>' + s[1] + '</small></button></li>'; }).join('');
    var d = $('selday'); d.innerHTML = [1, 2, 3, 4, 5, 6, 7, 8].map(function (k) { var dd = new Date(2026, 11, 4 + k); return '<option value="' + k + '">' + PV().dayLabel(k) + '</option>'; }).join('');
    var a = PV().items(); $('selart').innerHTML = '<option value="">未選択</option>' + a.map(function (x) { return '<option value="' + x.slug + '">' + x.title_ja.slice(0, 24) + '</option>'; }).join('');
  }
  function sync() {
    var p = PV(); if (!p) return; var S = p.get();
    var pr = S.preset === 'paid_purchased' ? 'paid' : S.preset;
    Array.prototype.forEach.call(document.querySelectorAll('#presets button'), function (b) { b.className = b.getAttribute('data-preset') === pr ? 'on' : ''; });
    Array.prototype.forEach.call(document.querySelectorAll('#screens li'), function (li) { li.className = (+li.getAttribute('data-n') === lastScreen) ? 'on' : ''; });
    $('cur').textContent = '現在: ' + ({ trial: '無料体験中', free: '無料会員', paid: '有料会員', canceled: '解約済み・契約期間内' }[S.mode]) + ' / 今日=' + S.today + (S.offline ? ' / オフライン' : '') + (S.mode === 'free' ? ' / 今日の無料記事=' + (S.selected ? '選択済み' : '未選択') : '') + (S.pendingBuy ? ' / 購入=承認待ち' : '') + ' / 利用状況の送信=' + (S.analytics === 'on' ? '送信する' : (S.analytics === 'off' ? '送信しない' : '未回答'));
    $('pendrow').hidden = !S.pendingBuy; $('endrow').hidden = !(S.mode === 'canceled' || S.mode === 'paid');
    $('selday').value = S.day <= 8 ? S.day : 8; $('selday').disabled = S.mode !== 'trial';
    $('daynote').textContent = S.mode === 'trial' ? '無料体験は ' + p.trialEndISO() + ' の終わりまで(初回起動日を含む8日目)' : '(無料体験の日は「無料体験中」のときだけ変えられます)';
    $('selart').value = S.selected || ''; $('selart').disabled = S.mode !== 'free';
    $('chkoff').checked = !!S.offline; $('chkgrace').checked = !!S.grace;
    $('promo').value = S.promoSince; $('promoval').textContent = S.promoSince;
  }
  window.PVshell = {
    ready: function () { build(); sync(); },
    sync: function () { if (PV()) { try { sync(); } catch (e) { } } },
    log: function (e) { var el = $('evlog'); el.textContent = JSON.stringify(e) + '\n' + el.textContent; el.textContent = el.textContent.slice(0, 600); }
  };
  frame.addEventListener('load', function () { setTimeout(function () { if (PV() && !$('selday').options.length) window.PVshell.ready(); }, 400); });
  document.addEventListener('click', function (e) {
    var el, p = PV(); if (!p) return;
    if ((el = e.target.closest('[data-preset]'))) { var wasMe = p.get().route === 'me'; p.preset(el.getAttribute('data-preset')); if (wasMe) p.nav('me'); lastScreen = 0; sync(); return; }
    if ((el = e.target.closest('[data-shortcut]'))) { applyShortcut(+el.getAttribute('data-shortcut')); if (window.innerWidth <= 900) $('panel').classList.remove('open'); return; }
    if (e.target.id === 'midnight') { p.midnight(); return; }
    if (e.target.id === 'reopenhome') { p.nav('home'); return; }
    if (e.target.id === 'endcontract') { p.endContract(); return; }
    if (e.target.id === 'pendok') { p.resolvePending(true); return; }
    if (e.target.id === 'penddecl') { p.resolvePending(false); return; }
    if (e.target.id === 'resetall') { p.preset('trial'); lastScreen = 0; sync(); return; }
    if (e.target.id === 'ptoggle') { $('panel').classList.toggle('open'); return; }
  });
  $('selday').addEventListener('change', function () { PV().setDay(+this.value); });
  $('selart').addEventListener('change', function () { PV().setSelected(this.value); });
  $('chkoff').addEventListener('change', function () { PV().setOffline(this.checked); });
  $('chkgrace').addEventListener('change', function () { PV().setGrace(this.checked); });
  $('promo').addEventListener('input', function () { $('promoval').textContent = this.value; PV().setPromoSince(+this.value); });
  $('chknotes').addEventListener('change', function () { PV().notes(this.checked); });
})();
