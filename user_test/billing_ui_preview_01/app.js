/* eigo-radio 課金・会員UI 統合プレビュー(アプリ画面側) v2。開発用・模擬(実課金/StoreKit呼出/実際の送信なし)。
   元デザイン: 現行アプリのWeb層 user_test/webapp_proto_01 の style.css / pc.css(build e2a3bdb4b5ee を複製)+実記事カタログ(公開済みのみ)+実サムネ。
   このfileはプレビュー専用でProduction配線なし。承認済み文言は DOC の定数にそのまま保持(ユーザー原文 §4)。
   v2(委任_B2): 状態と表示の食い違いの是正(保存記事タップ・全件ロック表示・猶予表示・日付切替・購入保留・二重購入)、
   ユーザー判断の反映(残り日数B案・無料会員のおまかせ非表示・復習帳の音声・利用状況送信の同意案2)。 */
(function () {
  'use strict';
  var $ = function (id) { return document.getElementById(id); };
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  var WD = ['日', '月', '火', '水', '木', '金', '土'];
  function pd(s) { var p = s.split('-'); return new Date(+p[0], +p[1] - 1, +p[2]); }
  function iso(d) { return d.getFullYear() + '-' + ('0' + (d.getMonth() + 1)).slice(-2) + '-' + ('0' + d.getDate()).slice(-2); }
  function addDays(s, n) { var d = pd(s); d.setDate(d.getDate() + n); return iso(d); }
  function addMonth(s) { var d = pd(s); d.setMonth(d.getMonth() + 1); return iso(d); }
  function md(s) { var d = pd(s); return (d.getMonth() + 1) + '月' + d.getDate() + '日'; }
  function mdw(s) { var d = pd(s); return md(s) + '(' + WD[d.getDay()] + ')'; }
  function ymd(s) { var d = pd(s); return d.getFullYear() + '年' + md(s); }
  function dayDiff(a, b) { return Math.round((pd(b).getTime() - pd(a).getTime()) / 86400000); }
  var FIRST_LAUNCH = '2026-12-05';   // 仕様の具体例(12月5日初回起動 -> 12月12日終了時まで)
  var TRIAL_END = addDays(FIRST_LAUNCH, 7);   // 初回起動日を含む8日目 = 12/12
  /* 残り日数の表示規則(ユーザー判断 B案・2026-11-26): 当日を含まない数え方。終了日=12/12なら 12/9=あと3日、最終日(12/12)=本日まで。表示はこの1関数だけ。 */
  function remainLabel(todayIso, endIso) { var n = dayDiff(todayIso, endIso); return n > 0 ? 'あと' + n + '日' : '本日まで'; }

  /* ---------- 承認済み文言(ユーザー原文§4。一字一句保持。改行位置のみ<br>で調整) ---------- */
  var DOC = {
    confirmQ: function (t) { return '今日の無料記事は「' + t + '」にしますか？'; },
    confirmBody: ['（無料会員は1日1記事）', '一度決定すると、変更できません。', '有料会員なら、すべての記事を自由に視聴できます。'],
    trialEnd: { title: '無料体験が終了しました', body: 'eigo-radioをお楽しみいただけましたか？<br>これからも、面白い英語を<br>好きなだけ楽しみませんか？', merit: '有料会員のメリット', items: ['毎日の新着記事がすべて聴き放題', '気になる過去の記事も自由に楽しめる', '全記事を自由にダウンロード・オフライン再生'], priceLbl: '料金', price: '月額490円', per: '1日あたり約16円', go: '有料会員になる', free: '無料で利用を続ける（1日1記事）' },
    promo: { title: 'もっと自由に、<br>英語を楽しみませんか？', body: '有料会員なら、毎日1記事の制限なく、気になる記事を自由に楽しめます。', items: ['新着記事・過去記事がすべて聴き放題', '全記事を自由にダウンロード・オフライン再生'], price: '月額490円', go: '有料会員になる', free: '今は無料で利用する' },
    paywall: { title: 'この記事は有料会員限定です', body: '有料会員なら、新着記事も過去記事も、すべて自由にお楽しみいただけます。', price: '月額490円', go: '有料会員になる', close: '閉じる' },
    paidEnd: { title: '有料会員期間が終了しました', p1: 'これまでご利用いただき、ありがとうございます。', p2: 'これからも、毎日お好きな1記事を無料でお楽しみいただけます。', p3: '復習帳やお気に入りなど、これまでの学習データは引き続きご利用いただけます。', join: 'また、すべての記事を楽しみませんか？', price: '月額490円', go: '有料会員になる', free: '無料で利用を続ける' },
    sub: { title: '有料会員のご案内', main: 'もっと自由に、<br>英語を楽しもう。', sub: '気になる記事を、好きなだけ。', meritT: '有料会員のメリット', items: ['毎日の新着記事がすべて聴き放題', '過去の記事もすべて利用可能', '全記事を自由にダウンロード・オフライン再生'], plan: '有料会員プラン', price: '490円／月（税込）', renew: '1か月ごとの自動更新', btn: '月額490円で有料会員になる', restore: '購入を復元する', terms: '利用規約', privacy: 'プライバシーポリシー' },
    trialBuy: function (endMd) { return '現在、' + endMd + 'まで全機能を無料でご利用いただけます。有料会員に加入すると、加入時点から料金が発生します。'; },
    restoreName: '購入を復元する',
    restoreNote: '機種変更や再インストールなどで、契約済みの有料会員資格が反映されない場合にご利用ください。追加料金はかかりません。'
  };

  /* ---------- 文言案(未確定。画面上に「文言案・要確認」マーカーを出す。全文一覧=laneB/WORDING_DRAFTS_02.md) ---------- */
  var DRAFT = {
    intro: { title: 'eigo-radioへようこそ', lead: '今日から8日目の終わり(%END%)まで、すべての記事・すべての機能を無料でお使いいただけます。', items: ['すべての記事を自由に聴ける', 'ダウンロード・オフライン再生も使える', '決済情報の登録は不要。無料体験が終わっても、自動で課金されることはありません'], foot: '無料体験が終わったあとも、毎日好きな1記事は無料で利用できます。', btn: '次へ' },
    /* 利用状況の送信の同意確認(ユーザー判断: 案2=事前同意+撤回)。初回案内の2画面目。 */
    consent: {
      title: '利用状況の送信について',
      lead: 'eigo-radioをより良くするため、アプリの使われ方の情報をGoogle LLCへ送信してもよいか、お選びください。',
      itemsT: '送信する情報',
      items: ['アプリの使用の記録(起動・再生・機能の利用など)', '購入の手続きの結果(金額やカード情報は含みません)', 'エラーの種類', 'このアプリを区別するための番号', 'おおまかな地域(国・地域)'],
      toT: '送信先', to: 'Google LLC',
      whyT: '目的', why: 'アプリの使われ方を分析し、サービスの改善に役立てるためです。広告には使いません。',
      free: '「同意しない」を選んでも、無料・有料のすべての機能を同じようにお使いいただけます。',
      later: 'この設定は、あとから「マイページ」の「利用状況の送信」でいつでも変更できます。',
      yes: '同意する', no: '同意しない', policy: 'プライバシーポリシー'
    },
    analytics: {
      name: '利用状況の送信', on: '送信する', off: '送信しない',
      help: 'アプリの使われ方の情報(起動・再生・機能の利用など)を、サービス改善のためGoogle LLCへ送信します。オフにすると送信しません。どちらでも、すべての機能は変わらずお使いいただけます。',
      link: '送信する情報・送信先・目的を見る', sim: 'プレビューでは実際の送信は行いません(模擬)。',
      onToast: '利用状況の送信をオンにしました。(模擬)', offToast: '利用状況の送信をオフにしました。(模擬)'
    },
    paywallNote: '今日の無料記事はすでに選択済みです。明日(0時を過ぎると)になれば、この記事も無料記事として選べます。',
    expired: { title: 'この記事は、いまは再生できません', p1: 'ダウンロード済みのデータは削除されていません。', p2: '今日の無料記事として選ぶか、有料会員になると、また聴けるようになります。', p2sel: '明日(0時を過ぎると)になれば、今日の無料記事として選ぶこともできます。', pick: '今日の無料記事にする', go: '有料会員になる', close: '閉じる' },
    terms: [
      'お支払いは、購入の確定時に、お使いのApple Accountへ請求されます。',
      '契約は1か月ごとに自動更新されます。現在の契約期間が終了する24時間前までに自動更新をオフにしない限り、契約は自動的に更新され、更新料金(490円／月・税込)がApple Accountへ請求されます。',
      '契約の確認・解約は、購入後いつでも、iPhoneの「設定」>[自分の名前]>「サブスクリプション」から行えます。解約しても、現在の契約期間の終了までは有料会員としてご利用いただけます。'
    ],
    freeBarNone: '今日の無料記事：まだ選んでいません(好きな1記事を選べます)',
    freeBarSel: '今日の無料記事：%T%',
    trialLast: '全機能無料体験中　本日まで',
    buyPending: '購入はまだ確定していません(承認待ち)。承認されるまで、有料会員の機能はご利用いただけません。',
    buyFail: '購入を完了できませんでした。通信状況をご確認のうえ、もう一度お試しください。',
    grace: '契約の更新を確認できません。オンラインに戻ると確認します(通信できない場合、最大3日間はそのままご利用いただけます)。',
    saved: { ok: '利用できます', freeSel: '今日の無料記事として利用できます', pick: '今日の無料記事に選べます', ng: '今日は利用できません' },
    dlDone: 'ダウンロード済み',
    miniLast: 'この記事は最後まで聴けます'
  };

  /* ---------- 状態 ---------- */
  var ITEMS = [], S = null, LOG = [];
  var LV = { std: 'Standard', adv: 'Advanced' };
  var PRESETS = {
    trial: { mode: 'trial', day: 5, today: '', selected: null, offline: false, grace: false, pend: { te: false, pe: false }, promoSince: 0 },
    trial_end: { mode: 'free', day: 9, today: '2026-12-13', selected: null, offline: false, grace: false, pend: { te: true, pe: false }, promoSince: 0 },
    free_unsel: { mode: 'free', day: 9, today: '2026-12-20', selected: null, offline: false, grace: false, pend: { te: false, pe: false }, promoSince: 3 },
    free_sel: { mode: 'free', day: 9, today: '2026-12-20', selected: 2, offline: false, grace: false, pend: { te: false, pe: false }, promoSince: 3 },
    paid: { mode: 'paid', day: 9, today: '2026-12-20', selected: null, offline: false, grace: false, pend: { te: false, pe: false }, promoSince: 0, renew: '2027-01-10' },
    canceled: { mode: 'canceled', day: 9, today: '2026-12-20', selected: null, offline: false, grace: false, pend: { te: false, pe: false }, promoSince: 0, renew: '2027-01-10' },
    expired: { mode: 'free', day: 9, today: '2027-01-12', selected: null, offline: false, grace: false, pend: { te: false, pe: true }, promoSince: 0 },
    offline: { mode: 'free', day: 9, today: '2026-12-20', selected: null, offline: true, grace: false, pend: { te: false, pe: false }, promoSince: 3 }
  };
  var DEFAULT_SAVED = [4, 5, 1, 6];   // 保存済み(模擬)=カタログindex
  function clone(o) { return JSON.parse(JSON.stringify(o)); }
  function applyPreset(id) {
    var p = clone(PRESETS[id]);
    var keep = S ? { fav: S.fav, level: S.level, saved: S.saved, analytics: S.analytics } : null;
    S = p; S.preset = id; S.tab = 'home'; S.route = 'home'; S.stack = []; S.playing = null; S.paused = false; S.intro = false; S.introStep = 1; S.busy = false; S.pendingBuy = false;
    S.fav = keep ? keep.fav : []; S.level = keep ? keep.level : 'std';
    S.analytics = (keep && keep.analytics !== 'unset') ? keep.analytics : 'on';
    S.saved = keep ? keep.saved : DEFAULT_SAVED.map(function (i) { return ITEMS[i].slug; });
    if (typeof S.selected === 'number') S.selected = ITEMS[S.selected].slug;
    if (S.mode === 'trial') S.today = addDays(FIRST_LAUNCH, S.day - 1);
    S.renew = S.renew || addMonth(S.today);
    closeModal(); closeFull();
  }
  function byslug(s) { for (var i = 0; i < ITEMS.length; i++) if (ITEMS[i].slug === s) return ITEMS[i]; return null; }
  function isFreeLike() { return S.mode === 'free'; }
  /* 利用権限(その記事を今 聴ける/読めるか)。 */
  function canUse(slug) { return S.mode !== 'free' || S.selected === slug; }
  /* ロック表示(鍵アイコン)を出すか: 無料会員が今日の1記事を選び終えたあとの「他の記事」だけ。選択前はすべて選択候補なので鍵を出さない(原文§4 ④)。 */
  function isLocked(slug) { return S.mode === 'free' && S.selected != null && S.selected !== slug; }
  function isSaved(slug) { return S.saved.indexOf(slug) >= 0; }
  /* 保存済み記事の「今日の利用可否」表示(状態ごとの表=PREVIEW_AUDIT_02.md §A)。 */
  function accessInfo(slug) {
    var D = DRAFT.saved;
    if (S.mode !== 'free') return { k: 'ok', t: D.ok };
    if (S.selected === slug) return { k: 'ok', t: D.freeSel };
    if (S.selected == null) return { k: 'sel', t: D.pick };
    return { k: 'ng', t: D.ng };
  }
  function logEv(e) { LOG.push(e); try { if (window.parent && window.parent.PVshell && window.parent.PVshell.log) window.parent.PVshell.log(e); } catch (x) { } }
  function changed() { try { if (window.parent && window.parent.PVshell) window.parent.PVshell.sync(); } catch (x) { } }

  /* ---------- 部品(現行アプリの markup を踏襲) ---------- */
  var IC = {
    play: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5v14l11-7z"/></svg>',
    pause: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 5h4v14H7zM13 5h4v14h-4z"/></svg>',
    lock: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 10V8a5 5 0 0 1 10 0v2h1a1 1 0 0 1 1 1v9a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1v-9a1 1 0 0 1 1-1zm2 0h6V8a3 3 0 0 0-6 0z"/></svg>',
    bars3: '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="4" y="13" width="4" height="7" rx="1"/><rect x="10" y="9" width="4" height="11" rx="1"/><rect x="16" y="5" width="4" height="15" rx="1"/></svg>',
    bars4: '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="2" y="14" width="3.5" height="6" rx="1"/><rect x="7.5" y="10" width="3.5" height="10" rx="1"/><rect x="13" y="7" width="3.5" height="13" rx="1"/><rect x="18.5" y="3" width="3.5" height="17" rx="1"/></svg>',
    heart: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 20.5s-7.5-4.6-9.3-9.2C1.5 8 3.4 5 6.6 5c1.9 0 3.5 1 5.4 3 1.9-2 3.5-3 5.4-3 3.2 0 5.1 3 3.9 6.3-1.8 4.6-9.3 9.2-9.3 9.2z"/></svg>'
  };
  var LOGO = '<svg viewBox="0 0 32 32" aria-hidden="true"><g fill="#1d4fd8"><rect x="3" y="12" width="3" height="8" rx="1.5"/><rect x="9" y="7" width="3" height="18" rx="1.5"/><rect x="15" y="3" width="3" height="26" rx="1.5"/><rect x="21" y="8" width="3" height="16" rx="1.5"/><rect x="27" y="13" width="3" height="6" rx="1.5"/></g></svg>';
  function note(t) { return '<span class="kari pvnote">' + (t || '文言案・要確認') + '</span>'; }
  function topBar(back) {
    return '<div class="top"><div class="side">' + (back ? '<button class="iconbtn backbtn" data-act="back" aria-label="戻る"><span class="ba" aria-hidden="true">&#8249;</span><span class="bl">戻る</span></button>' : '') + '</div><div class="logo">' + LOGO + '<b>eigo-radio</b></div><div class="side"><button class="iconbtn q" data-act="help" aria-label="使い方">?</button></div></div>';
  }
  function thumbUrl(it) { var t = it.thumbnail; return '../' + it.slug + '/enduser/' + t.file + '?v=' + String(t.sha256).slice(0, 12); }
  function thumbHtml(it, dur, lock) {
    var h = 0; for (var i = 0; i < it.slug.length; i++) h = (h * 31 + it.slug.charCodeAt(i)) % 360; h = 205 + (h % 40);
    return '<div class="thumb" style="background:linear-gradient(135deg,hsl(' + h + ',72%,48%),hsl(' + (h + 14) + ',68%,20%))"><span class="fam">' + esc(it.family) + '</span><img src="' + esc(thumbUrl(it)) + '" alt="" loading="lazy" style="position:absolute;inset:0">' +
      (dur ? '<span class="dur">' + Math.round(it.total_sec / 60) + '分</span>' : '') + (lock ? '<span class="lockb" aria-label="ロック中">' + IC.lock + '</span>' : '') + '</div>';
  }
  document.addEventListener('error', function (e) { var t = e.target; if (t && t.tagName === 'IMG' && t.closest('.thumb')) t.remove(); }, true);
  function isFav(s) { return S.fav.indexOf(s) >= 0; }
  function cardHtml(it) {
    var locked = isLocked(it.slug), fv = isFav(it.slug), saved = isSaved(it.slug);
    var chips = '<div class="chips"><span class="chip">' + esc(it.genres[0]) + '</span><span class="chip lv' + (S.level === 'adv' ? 'adv' : '') + '">' + LV[S.level] + '</span>' +
      (S.mode === 'free' && S.selected === it.slug ? '<span class="chip free">今日の無料記事</span>' : '') +
      (S.offline ? (saved ? '<span class="chip saved">保存済み</span>' : '<span class="chip warn">未保存</span>') : '') + '</div>';
    var on = S.playing === it.slug && !S.paused;
    return '<article class="card' + (S.playing === it.slug ? ' now' : '') + '" data-open="' + it.slug + '" data-locked="' + (locked ? 1 : 0) + '" tabindex="0">' +
      '<div class="cgrid">' + thumbHtml(it, true, locked) + '<div class="cmain"><h4>' + esc(it.title_ja) + '</h4>' + chips + '</div>' +
      '<div class="acts"><button type="button" class="cardfav" data-fav="' + it.slug + '" aria-pressed="' + fv + '" aria-label="' + esc(it.title_ja) + ' をお気に入り' + (fv ? 'から外す' : 'に登録') + '">' + IC.heart + '</button>' +
      '<button type="button" class="cardplay' + (locked ? ' locked' : '') + (on ? ' on' : '') + '" data-play="' + it.slug + '" aria-label="' + esc(it.title_ja) + ' を' + (locked ? '再生(有料会員限定・ロック中)' : '再生') + '">' + (locked ? IC.lock : (on ? IC.pause : IC.play)) + '</button></div>' +
      '<p class="sum">' + esc(it.summary_ja) + '</p></div></article>';
  }
  function lvSeg() {
    return '<div class="lvseg" role="group" aria-label="レベル選択">' + ['std', 'adv'].map(function (k) { return '<button type="button" data-lv="' + k + '" aria-pressed="' + (S.level === k) + '">' + (k === 'std' ? IC.bars3 : IC.bars4) + LV[k] + '</button>'; }).join('') + '</div>';
  }
  function graceActive() { return S.offline && S.grace && (S.mode === 'paid' || S.mode === 'canceled'); }
  function statusBar() {
    var h = '';
    if (S.offline) h += '<div class="pvbar offline" data-bar="offline">オフライン中です。保存済みの記事だけ聴けます。' + (graceActive() ? note() + '<small>' + DRAFT.grace + '</small>' : '') + '</div>';
    if (S.mode === 'trial') {
      var n = dayDiff(S.today, TRIAL_END);
      h += '<div class="pvbar trial" data-bar="trial"><b>' + (n > 0 ? '全機能無料体験中　' + remainLabel(S.today, TRIAL_END) : DRAFT.trialLast + note()) + '</b><small>' + mdw(TRIAL_END) + 'の終わりまで</small></div>';
    } else if (S.mode === 'free') {
      var cur = byslug(S.selected);
      h += '<div class="pvbar" data-bar="free">' + note() + ' <b>' + (cur ? DRAFT.freeBarSel.replace('%T%', esc(cur.title_ja)) : DRAFT.freeBarNone) + '</b></div>';
    }
    return h;
  }
  /* おまかせラジオ: 現行アプリのホームにある入口。ユーザー判断(2026-11-26): 無料会員は不可=入口を表示しない。体験中・有料(解約済み期間内を含む)は従来どおり。 */
  function omakase() {
    if (S.mode === 'free') return '';
    return '<section class="omakase" id="omakase" data-omakase><span class="pill">おまかせラジオ</span><h2>今日も英語を楽しもう。</h2><p>新着記事からランダムに連続再生</p>' +
      '<button type="button" class="bigbtn" data-act="omakase">' + IC.play + '<span>' + LV[S.level] + 'で再生</span></button></section>';
  }

  /* ---------- 画面 ---------- */
  function viewHome() {
    return topBar() + '<p class="tag">英語を、ラジオで楽しく学ぼう。</p>' + statusBar() + lvSeg() +
      '<p class="lvnote">選んだレベルで再生されます(現在: <b>' + LV[S.level] + '</b>)</p>' + omakase() +
      '<div class="sh"><h3>新着エピソード</h3></div><div class="cards">' + ITEMS.map(cardHtml).join('') + '</div>';
  }
  function viewSearch() {
    return topBar() + '<h2 style="margin:4px 0 8px;color:var(--navy)">記事を探す</h2><div class="search" style="margin:0 0 12px"><input type="search" placeholder="タイトル・キーワード(プレビューでは未対応)" aria-label="検索" style="width:100%;min-height:48px;border-radius:14px;border:1.5px solid var(--line);padding:0 14px"></div>' + statusBar() + '<div class="cards">' + ITEMS.map(cardHtml).join('') + '</div>';
  }
  var REVIEW = [['Could you say that again?', 'もう一度言ってもらえますか?'], ['I\'ll get back to you.', '後ほどご連絡します。'], ['That makes sense.', 'なるほど、納得です。']];
  /* 復習帳: ユーザー判断(2026-11-26): 無料会員でも音声を再生できる。どの会員状態でも再生ボタンは常に使える(ロック・制限表示を出さない)。 */
  function viewReview() {
    return topBar() + '<h2 style="margin:4px 0 8px;color:var(--navy)">復習帳</h2>' +
      '<div class="dlmsg">復習帳は、どの会員状態でも(無料会員・契約終了後も)引き続きご利用いただけます。音声も再生できます。</div>' +
      '<div class="dummy">プレビューでは復習帳の中身はサンプル(模擬)です。</div><div class="rvlist" id="rvlist">' +
      REVIEW.map(function (r, i) { return '<div class="rvrow" data-rv="' + i + '"><button type="button" class="cardplay" data-act="review-play" data-i="' + i + '" aria-label="' + esc(r[0]) + ' の音声を再生">' + IC.play + '</button><div><b>' + esc(r[0]) + '</b><small>' + esc(r[1]) + '</small></div></div>'; }).join('') + '</div>';
  }
  function viewArticle(slug) {
    var it = byslug(slug), locked = isLocked(slug), fv = isFav(slug), saved = isSaved(slug), ai = accessInfo(slug);
    var dl = saved ? '<div class="dlbtn2 ' + (ai.k === 'ok' ? 'dldone2' : 'dlnot2') + '" role="status" data-dl-state="saved" data-access="' + ai.k + '">' + DRAFT.dlDone + '（' + (ai.k === 'ok' ? 'オフラインでも聴けます' : ai.t) + '）</div>' :
      '<button type="button" class="dlbtn2" data-req="dl" data-slug="' + slug + '">' + (S.offline ? 'オフライン用にダウンロード(オフラインのため不可)' : 'オフライン用にダウンロード') + '</button>';
    return topBar(true) + '<div class="artbody"><div class="thumbbig">' + thumbHtml(it, true, locked) + '<div><h1>' + esc(it.title_ja) + '</h1><p class="en">' + esc(it.title_en) + '</p><div class="chips"><span class="chip">' + esc(it.genres[0]) + '</span>' +
      (S.mode === 'free' && S.selected === slug ? '<span class="chip free">今日の無料記事</span>' : '') + '</div></div></div>' +
      '<p class="sumfull">' + esc(it.summary_ja) + '</p>' +
      '<div class="favrow"><button type="button" data-fav="' + slug + '" aria-pressed="' + fv + '">' + IC.heart + 'お気に入り</button></div>' + lvSeg() +
      '<div class="acts2"><button type="button" class="bigbtn" data-req="play" data-slug="' + slug + '">' + (locked ? IC.lock : IC.play) + '<span>' + LV[S.level] + 'で再生</span></button>' +
      '<button type="button" class="dlbtn2" data-req="text" data-slug="' + slug + '">英文・日本語訳を読む</button><button type="button" class="dlbtn2" data-req="study" data-slug="' + slug + '">学習コーナー</button></div>' + dl +
      '<div class="dlmsg" style="margin-top:12px">記事の概要の閲覧・お気に入り登録では、無料枠は消費されません。</div></div>';
  }
  function planCard() {
    var h = '<div class="plancard" data-plan="' + S.mode + '"><div class="pl0">現在の利用プラン</div>';
    var pend = S.pendingBuy ? '<p class="pendnote" data-pending-note>購入は承認待ちです。承認されるまで、有料会員にはなりません。' + note() + '</p>' : '';
    if (S.mode === 'trial') {
      h += '<div class="pn">無料体験中</div><div class="pr"><span>無料体験終了日</span><span>' + ymd(TRIAL_END) + '</span></div>' +
        '<p>すべての記事・機能をご利用いただけます。</p><p>無料体験が終わっても、自動で有料会員になることはありません。</p>' + pend +
        '<button type="button" class="pvbtn go" data-act="subscribe">有料会員になる</button>';
    } else if (S.mode === 'free') {
      h += '<div class="pn">無料会員</div><p>毎日、好きな1記事を全機能でご利用いただけます。</p><p>有料会員なら、すべての記事を自由にご利用いただけます。</p><div class="pr"><span>有料会員</span><span>月額490円</span></div>' + pend +
        '<button type="button" class="pvbtn go" data-act="subscribe">有料会員になる</button>';
    } else if (S.mode === 'paid') {
      h += '<div class="pn">有料会員</div><div class="pr"><span>料金</span><span>月額490円（税込）</span></div><div class="pr"><span>次回更新日</span><span>' + ymd(S.renew) + '</span></div>' +
        '<p>すべての記事・機能をご利用いただけます。</p>' + (graceActive() ? '<p>' + DRAFT.grace + ' ' + note() + '</p>' : '') +
        '<button type="button" class="pvbtn free" data-act="manage">契約内容の確認・解約</button>';
    } else {
      h += '<div class="pn">有料会員</div><div class="pr"><span>契約状態</span><span>自動更新停止済み</span></div><div class="pr"><span>利用期限</span><span>' + ymd(S.renew) + '</span></div>' +
        '<p>利用期限まで、すべての記事・機能をご利用いただけます。</p>' + (graceActive() ? '<p>' + DRAFT.grace + ' ' + note() + '</p>' : '') +
        '<button type="button" class="pvbtn free" data-act="manage">契約内容の確認・変更</button>';
    }
    return h + '</div>';
  }
  function savedRows() {
    var rows = S.saved.map(function (s) {
      var it = byslug(s), ai = accessInfo(s);
      return '<div class="dlrow" data-dl-row="' + s + '" data-access="' + ai.k + '"><a href="#" data-row="' + s + '">' + esc(it.title_ja) + '</a><small>保存済み(模擬 約12MB)　<span class="st ' + ai.k + '">' + ai.t + '</span></small>' +
        '<button type="button" class="dllink" data-act="del-saved" data-slug="' + s + '" aria-label="' + esc(it.title_ja) + 'の保存を削除">削除</button></div>';
    }).join('');
    return '<div class="pl">保存した記事(オフライン保存の管理)</div>' + (rows || '<div class="dlmsg">まだ保存した記事はありません。</div>') +
      '<div class="dlmsg"><small>保存データは契約終了・無料会員への移行で自動削除されません。利用の可否は現在の利用権限で決まります。記事名を押すと記事ページが開きます(利用できない記事は案内を表示します)。</small></div>';
  }
  function analyticsOn() { return S.analytics === 'on'; }
  function privacyRow() {
    var A = DRAFT.analytics, on = analyticsOn();
    return '<div class="pl">プライバシー</div><div class="anrow" id="analytics-row"><div class="an1"><b>' + A.name + '</b>' + note() + '<span class="anst" id="an-state" data-an="' + (on ? 'on' : 'off') + '">' + (on ? A.on : A.off) + '</span></div>' +
      '<button type="button" class="swt" id="an-switch" role="switch" aria-checked="' + on + '" aria-label="' + A.name + '" data-act="an-toggle"><i></i></button></div>' +
      '<p class="rnote" style="margin:2px 2px 4px">' + A.help + '</p><button type="button" class="pvlink" data-act="an-info" style="text-align:left">' + A.link + '</button><p class="rnote" style="margin:0 2px">' + A.sim + '</p>';
  }
  function viewMe() {
    return topBar() + '<h2 style="margin:4px 0 8px;color:var(--navy)">マイページ</h2>' + planCard() +
      '<div class="pl">レベル設定(共通)</div>' + lvSeg() +
      savedRows() +
      '<a class="setrow" href="#" data-act="fav-row">お気に入り記事<span>' + S.fav.length + '件 &#8250;</span></a>' +
      '<div class="pl" id="other-procs">その他の手続き</div><div class="restorebox" id="restorebox"><button type="button" class="setrow" data-act="restore" id="restorebtn">' + DOC.restoreName + '<span>&#8250;</span></button><p class="rnote">' + DOC.restoreNote + '</p></div>' +
      privacyRow() +
      '<div class="pl">サポート・規約</div>' +
      ['お問い合わせ・不具合報告', '利用規約', 'プライバシーポリシー', '特定商取引法に基づく表記'].map(function (x) { return '<a class="setrow" href="#" data-act="legal" data-name="' + x + '">' + x + '<span>&#8250;</span></a>'; }).join('') +
      '<div class="dlmsg"><small>診断ログの共有は「お問い合わせ・不具合報告」内にあります(既存仕様。プレビューでは省略)。</small></div>';
  }
  function viewSubscribe() {
    var D = DOC.sub, trial = S.mode === 'trial', already = S.mode === 'paid' || S.mode === 'canceled';
    var buyArea;
    if (already) buyArea = '<div class="dlmsg" data-already>すでに有料会員です(契約の確認・変更はマイページから)。</div>';
    else if (S.pendingBuy) buyArea = '<div class="trialnote" id="pendnote">' + DRAFT.buyPending + ' ' + note() + '</div><button type="button" class="pvbtn go" id="buybtn" data-act="buy" disabled>' + D.btn + '</button>';
    else buyArea = '<button type="button" class="pvbtn go" id="buybtn" data-act="buy">' + D.btn + '</button>';
    return topBar(true) + '<h2 style="margin:4px 0 0;color:var(--navy);font-size:15px">' + D.title + '</h2>' +
      '<div class="sub-hero"><h1>' + D.main + '</h1><p>' + D.sub + '</p></div>' +
      '<div class="pvcard"><h3>' + D.meritT + '</h3><ul>' + D.items.map(function (x) { return '<li>' + x + '</li>'; }).join('') + '</ul></div>' +
      '<div class="pvcard pvprice"><div class="nm">' + D.plan + '</div><div class="amt">' + D.price + '</div><div class="per">' + D.renew + '</div></div>' +
      (trial ? '<div class="trialnote" id="trialnote">' + DOC.trialBuy(md(TRIAL_END)) + '</div>' : '') + buyArea +
      '<div class="terms" id="terms">' + note('文言案・要確認(契約条件の説明)') + DRAFT.terms.map(function (x) { return '<p>' + x + '</p>'; }).join('') + '</div>' +
      '<div class="auxlist"><button type="button" class="pvlink" data-act="restore">' + D.restore + '</button><button type="button" class="pvlink" data-act="legal" data-name="' + D.terms + '">' + D.terms + '</button><button type="button" class="pvlink" data-act="legal" data-name="' + D.privacy + '">' + D.privacy + '</button></div>';
  }

  /* ---------- モーダル ---------- */
  function openModal(html, name) { $('pvmodalbody').innerHTML = html; $('pvmodal').className = 'on'; $('pvmodal').setAttribute('data-modal', name || ''); logEv({ ev: 'modal', name: name }); }
  function closeModal() { $('pvmodal').className = ''; $('pvmodal').setAttribute('data-modal', ''); $('pvmodalbody').innerHTML = ''; }
  function modalName() { return $('pvmodal').className === 'on' ? $('pvmodal').getAttribute('data-modal') : ''; }
  function closeFull() { $('pvfull').className = 'pvfull'; $('pvfull').innerHTML = ''; $('pvfull').removeAttribute('data-full'); }
  function fullOpen() { return $('pvfull').className.indexOf('on') >= 0; }
  function sheet(inner) { return '<div class="pvsheet">' + inner + '</div>'; }
  function lis(a) { return '<ul>' + a.map(function (x) { return '<li>' + x + '</li>'; }).join('') + '</ul>'; }
  function showTrialEnd() {
    var D = DOC.trialEnd;
    openModal(sheet('<h3>' + D.title + '</h3><p>' + D.body + '</p><div class="ttl2">' + D.merit + '</div>' + lis(D.items) + '<div class="ttl2">' + D.priceLbl + '</div><div class="price">' + D.price + '</div><p class="sub">' + D.per + '</p>' +
      '<div class="acts"><button type="button" class="pvbtn go" data-act="modal-sub">' + D.go + '</button><button type="button" class="pvbtn free" data-act="modal-close">' + D.free + '</button></div>'), 'trial_end');
  }
  function showPromo() {
    var D = DOC.promo;
    openModal(sheet('<h3>' + D.title + '</h3><p>' + D.body + '</p>' + lis(D.items) + '<div class="price">' + D.price + '</div>' +
      '<div class="acts"><button type="button" class="pvbtn go" data-act="modal-sub">' + D.go + '</button><button type="button" class="pvbtn free" data-act="modal-close">' + D.free + '</button></div>'), 'promo');
  }
  function showPaidEnd() {
    var D = DOC.paidEnd;
    openModal(sheet('<h3>' + D.title + '</h3><p>' + D.p1 + '</p><p>' + D.p2 + '</p><p>' + D.p3 + '</p><p><b>' + D.join + '</b></p><div class="price">' + D.price + '</div>' +
      '<div class="acts"><button type="button" class="pvbtn go" data-act="modal-sub">' + D.go + '</button><button type="button" class="pvbtn free" data-act="modal-close">' + D.free + '</button></div>'), 'paid_end');
  }
  function showPaywall(slug) {
    var D = DOC.paywall;
    openModal(sheet('<h3>' + D.title + '</h3><p>' + D.body + '</p><div class="price">' + D.price + '</div><p class="sub" data-paywall-note>' + note() + DRAFT.paywallNote + '</p>' +
      '<div class="acts"><button type="button" class="pvbtn go" data-act="modal-sub">' + D.go + '</button><button type="button" class="pvbtn free" data-act="modal-close">' + D.close + '</button></div>'), 'paywall');
  }
  function showConfirmSelect(slug, kind) {
    var it = byslug(slug), C = DOC.confirmBody;
    openModal(sheet('<h3>' + DOC.confirmQ(esc(it.title_ja)) + '</h3><p>' + C[0] + '</p><p>' + C[1] + '</p><p>' + C[2] + '</p>' +
      '<div class="acts"><button type="button" class="pvbtn go" style="background:linear-gradient(135deg,var(--blue),var(--blue2));box-shadow:0 6px 16px rgba(10,59,189,.35)" data-act="select-ok" data-slug="' + slug + '" data-kind="' + kind + '">決定する</button><button type="button" class="pvbtn free" data-act="select-cancel">キャンセル</button></div>'), 'select_confirm');
  }
  function showExpired(slug, kind) {
    var D = DRAFT.expired, it = byslug(slug), unsel = S.selected == null;
    openModal(sheet('<h3>' + D.title + ' ' + note() + '</h3><p><b>' + esc(it.title_ja) + '</b></p><p>' + D.p1 + '</p><p>' + (unsel ? D.p2 : D.p2 + ' ' + D.p2sel) + '</p>' +
      '<div class="acts"><button type="button" class="pvbtn go" data-act="modal-sub">' + D.go + '</button>' + (unsel ? '<button type="button" class="pvbtn free" data-act="select-from-expired" data-slug="' + slug + '" data-kind="' + (kind || 'play') + '">' + D.pick + '</button>' : '') + '<button type="button" class="pvbtn free" data-act="modal-close">' + D.close + '</button></div>'), 'expired_saved');
  }
  /* 初回案内: 1/2=無料体験の案内、2/2=利用状況の送信の同意確認(案2)。2画面は1つの初回フロー。 */
  function showIntro() {
    var step = S.introStep || 1, box = $('pvfull'), h;
    box.className = 'pvfull on'; box.setAttribute('data-full', 'intro'); box.setAttribute('data-step', step);
    if (step === 1) {
      var D = DRAFT.intro;
      h = '<div class="logo">' + LOGO + '<b style="font-family:Georgia,serif;font-size:27px;color:var(--navy)">eigo-radio</b></div><div class="steps">1 / 2</div><h2>' + D.title + '</h2><p style="text-align:center">' + note() + '</p><p>' + D.lead.replace('%END%', md(TRIAL_END)) + '</p>' + lis(D.items) + '<p style="color:var(--muted);font-size:13.5px">' + D.foot + '</p><button type="button" class="pvbtn go" data-act="intro-next">' + D.btn + '</button>';
    } else {
      var C = DRAFT.consent;
      h = '<div class="steps">2 / 2</div><h2 style="font-size:21px">' + C.title + '</h2><p style="text-align:center;margin:0">' + note() + '</p><p>' + C.lead + '</p>' +
        '<div class="ttl2">' + C.itemsT + '</div>' + lis(C.items) + '<div class="ttl2">' + C.toT + '</div><p style="margin:2px 0">' + C.to + '</p><div class="ttl2">' + C.whyT + '</div><p style="margin:2px 0">' + C.why + '</p>' +
        '<p style="color:var(--muted);font-size:13.5px">' + C.free + '<br>' + C.later + '</p>' +
        '<div class="cchoice"><button type="button" class="pvbtn pick" data-act="consent" data-v="on">' + C.yes + '</button><button type="button" class="pvbtn pick" data-act="consent" data-v="off">' + C.no + '</button></div>' +
        '<button type="button" class="pvlink" data-act="legal" data-name="' + C.policy + '" style="align-self:center">' + C.policy + '</button>';
    }
    box.innerHTML = h;
    logEv({ ev: 'full', name: 'intro', step: step });
  }
  function showAnalyticsInfo() {
    var C = DRAFT.consent;
    openModal(sheet('<h3>' + DRAFT.analytics.name + ' ' + note() + '</h3><div class="ttl2">' + C.itemsT + '</div>' + lis(C.items) + '<div class="ttl2">' + C.toT + '</div><p style="margin:2px 0">' + C.to + '</p><div class="ttl2">' + C.whyT + '</div><p style="margin:2px 0">' + C.why + '</p><p class="sub">' + DRAFT.analytics.sim + '</p>' +
      '<div class="acts"><button type="button" class="pvbtn free" data-act="modal-close">閉じる</button></div>'), 'analytics_info');
  }
  function toast(msg, ms) { var t = $('pvtoast'); t.textContent = msg; t.hidden = false; clearTimeout(toast._t); toast._t = setTimeout(function () { t.hidden = true; }, ms || 3200); }

  /* ---------- 購入(模擬) ---------- */
  function openApple() {
    if (S.offline) { toast('オフラインのため購入できません。通信できる状態でお試しください。'); return; }
    if (S.mode === 'paid' || S.mode === 'canceled') { toast('すでに有料会員です。契約内容はマイページから確認できます。'); return; }
    if (S.pendingBuy) { toast('購入は承認待ちです。承認されるまでお待ちください。'); return; }
    openModal('<div class="pvsheet applesheet"><div class="mock">【模擬】Appleの購入確認画面のイメージです。実際の課金は発生しません。</div><div class="hd"><div class="ico">e</div><div><b>有料会員（月額）</b><br><small>eigo-radio / 1か月ごとに自動更新</small></div></div>' +
      '<div class="bd"><div class="pr"><span>価格</span><span><b>490円／月</b>（税込）</span></div><div class="pr"><span>お支払い</span><span>Apple Account(模擬)</span></div><p class="sub">結果を選んでください(模擬)。</p></div>' +
      '<div class="ft"><button type="button" class="ok" data-act="buy-result" data-r="success">購入を確定する(成功)</button><button type="button" class="ot" data-act="buy-result" data-r="cancel">キャンセル</button><button type="button" class="ot" data-act="buy-result" data-r="fail">失敗にする(模擬)</button><button type="button" class="ot" data-act="buy-result" data-r="pending">保留(承認待ち)にする(模擬)</button></div></div>', 'apple_purchase');
  }
  function becomePaid() { S.mode = 'paid'; S.renew = addMonth(S.today); S.pend = { te: false, pe: false }; S.pendingBuy = false; S.grace = false; S.preset = 'paid_purchased'; }
  function buyResult(r) {
    if (S.busy) { logEv({ ev: 'double_tap_ignored' }); return; }
    if (r === 'cancel') { closeModal(); logEv({ ev: 'buy', r: r }); return; }
    S.busy = true;
    $('pvmodalbody').innerHTML = sheet('<h3><span class="spin"></span>処理しています…</h3><p class="sub">二重にお手続きされないよう、この間は操作できません(模擬)。</p>');
    setTimeout(function () {
      S.busy = false; logEv({ ev: 'buy', r: r });
      if (r === 'success') {
        becomePaid(); S.tab = 'me'; S.route = 'me'; S.stack = []; closeModal(); render(); toast('有料会員になりました。すべての記事・機能をご利用いただけます。(模擬)'); changed();
      } else if (r === 'fail') {
        openModal(sheet('<h3>購入できませんでした ' + note() + '</h3><p>' + DRAFT.buyFail + '</p><div class="acts"><button type="button" class="pvbtn go" data-act="buy">もう一度試す</button><button type="button" class="pvbtn free" data-act="modal-close">閉じる</button></div>'), 'buy_failed');
      } else {
        S.pendingBuy = true; render(true);
        openModal(sheet('<h3>購入は承認待ちです ' + note() + '</h3><p>' + DRAFT.buyPending + '</p><div class="acts"><button type="button" class="pvbtn free" data-act="modal-close">閉じる</button></div>'), 'buy_pending');
      }
    }, 700);
  }
  function openRestore() {
    openModal(sheet('<h3>購入を復元する</h3><p>' + DOC.restoreNote + '</p><p class="sub">【模擬】復元の結果を選んでください。</p><div class="acts"><button type="button" class="pvbtn free" data-act="restore-result" data-r="found">契約が見つかった(復元する)</button><button type="button" class="pvbtn free" data-act="restore-result" data-r="none">契約が見つからない</button><button type="button" class="pvbtn free" data-act="restore-result" data-r="cancel">閉じる</button></div>'), 'restore');
  }
  function openManage() {
    openModal(sheet('<h3>契約内容の確認・' + (S.mode === 'paid' ? '解約' : '変更') + '</h3><p>Appleのサブスクリプション管理画面を開きます。解約や変更はそこで行います。</p><p class="sub">【模擬】実際には画面が切り替わります。ここでは結果を選べます。</p><div class="acts">' +
      (S.mode === 'paid' ? '<button type="button" class="pvbtn free" data-act="manage-result" data-r="cancel">解約手続きをした(模擬)</button>' : '<button type="button" class="pvbtn free" data-act="manage-result" data-r="resume">自動更新を再開した(模擬)</button>') +
      '<button type="button" class="pvbtn free" data-act="manage-result" data-r="close">閉じる</button></div>'), 'manage');
  }

  /* ---------- 権限判定(プレビュー用の模擬。正式実装はネイティブ側で一元判定) ---------- */
  function perform(slug, kind) {
    if (kind === 'open') { logEv({ ev: 'open_article', slug: slug }); push('art:' + slug); return; }
    if (kind === 'play') { S.playing = slug; S.paused = false; render(true); toast('再生を始めます(模擬)'); }
    else if (kind === 'text') toast('英文・日本語訳を表示します(模擬)');
    else if (kind === 'study') toast('学習コーナーを開きます(模擬)');
    else if (kind === 'dl') { if (!isSaved(slug)) S.saved.push(slug); render(true); toast('ダウンロードしました(模擬)'); }
    logEv({ ev: 'perform', kind: kind, slug: slug });
  }
  function request(slug, kind) {
    var saved = isSaved(slug);
    if (S.offline && !saved) {
      if (kind === 'dl') toast('オフラインのためダウンロードできません。');
      else if (isFreeLike() && S.selected == null) toast('オフライン中は、保存済みの記事から今日の無料記事を選べます。');
      else toast('オフラインのため、保存していない記事は開けません。');
      return;
    }
    if (canUse(slug)) { perform(slug, kind); return; }
    if (isFreeLike() && S.selected == null) { showConfirmSelect(slug, kind); return; }
    /* 利用できない記事: マイページの保存一覧・オフライン中は「期限切れ案内」(ダウンロード済みデータは削除されていない旨+加入導線)、それ以外(ホーム・記事ページ)は「有料会員限定の加入案内」(現行アプリ eigo_membership_ui.js dialogForBlocked と同じ規則)。 */
    if (S.route === 'me' || S.offline) showExpired(slug, kind); else showPaywall(slug);
  }

  /* ---------- 画面遷移 ---------- */
  function navTab(t) { S.tab = t; S.route = t; S.stack = []; render(); }
  function push(route) { S.stack.push(S.route); S.route = route; render(); }
  function goBack() { S.route = S.stack.pop() || S.tab; render(); }

  /* ---------- 描画 ---------- */
  function render(keep) {
    var r = S.route, html, y = window.pageYOffset, vy = $('view').scrollTop;
    if (r === 'home') html = viewHome(); else if (r === 'search') html = viewSearch(); else if (r === 'review') html = viewReview(); else if (r === 'me') html = viewMe();
    else if (r === 'sub') html = viewSubscribe(); else if (r.indexOf('art:') === 0) html = viewArticle(r.slice(4)); else html = viewHome();
    $('view').innerHTML = html;
    Array.prototype.forEach.call(document.querySelectorAll('#nav a'), function (a) { if (a.getAttribute('data-tab') === S.tab) a.setAttribute('aria-current', 'page'); else a.removeAttribute('aria-current'); });
    var m = $('mini');
    if (S.playing) {
      var it = byslug(S.playing); m.hidden = false;
      m.innerHTML = '<div class="miniin">' + thumbHtml(it, false) + '<div class="mt"><b>' + esc(it.title_ja) + '</b><span>' + LV[S.level] + '(再生中・模擬)' + (canUse(S.playing) ? '' : '　' + DRAFT.miniLast) + '</span></div><button type="button" class="mpp" data-act="mini-pp" aria-label="再生/一時停止">' + (S.paused ? IC.play : IC.pause) + '</button><div class="bar"></div></div>'; document.body.classList.remove('nomini');
    }
    else { m.hidden = true; document.body.classList.add('nomini'); }
    if (keep) { $('view').scrollTop = vy; window.scrollTo(0, y); } else { $('view').scrollTop = 0; window.scrollTo(0, 0); }
    setTimeout(maybePopups, 30);
    changed();
  }
  function maybePopups() {
    if (S.route !== 'home' || modalName() || fullOpen() || S.playing) return;
    if (S.intro) { showIntro(); return; }
    if (!isFreeLike()) return;
    if (S.pend.te) { S.pend.te = false; S.promoSince = 0; showTrialEnd(); return; }
    if (S.pend.pe) { S.pend.pe = false; S.promoSince = 0; showPaidEnd(); return; }
    if (S.promoSince >= 7) { S.promoSince = 0; showPromo(); }
  }
  function endContract() { S.mode = 'free'; S.selected = null; S.pend = { te: false, pe: true }; S.promoSince = 0; S.grace = false; S.pendingBuy = false; }
  function endTrial() { S.mode = 'free'; S.day = 9; S.today = addDays(TRIAL_END, 1); S.selected = null; S.pend = { te: true, pe: false }; S.promoSince = 0; }

  /* ---------- イベント ---------- */
  document.addEventListener('click', function (e) {
    var t = e.target, el;
    if ((el = t.closest('[data-act]'))) {
      var a = el.getAttribute('data-act');
      e.preventDefault();
      if (el.disabled) return;
      if (a === 'modal-back') { var nm = modalName(); if (nm === 'select_confirm' || nm === 'paywall' || nm === 'trial_end' || nm === 'promo' || nm === 'paid_end' || nm === 'expired_saved' || nm === 'analytics_info') closeModal(); return; }
      if (a === 'modal-close') { closeModal(); return; }
      if (a === 'modal-sub') { closeModal(); if (S.route !== 'sub') push('sub'); return; }
      if (a === 'subscribe') { if (S.route !== 'sub') push('sub'); return; }
      if (a === 'back') { goBack(); return; }
      if (a === 'select-ok') { var sl = el.getAttribute('data-slug'), kd = el.getAttribute('data-kind'); S.selected = sl; closeModal(); logEv({ ev: 'selected', slug: sl }); perform(sl, kd); return; }
      if (a === 'select-cancel') { closeModal(); logEv({ ev: 'select_cancel' }); return; }
      if (a === 'select-from-expired') { var s2 = el.getAttribute('data-slug'); closeModal(); showConfirmSelect(s2, el.getAttribute('data-kind') || 'play'); return; }
      if (a === 'intro-next') { S.introStep = 2; showIntro(); return; }
      if (a === 'consent') { S.analytics = el.getAttribute('data-v') === 'on' ? 'on' : 'off'; S.intro = false; S.introStep = 1; closeFull(); logEv({ ev: 'consent', v: S.analytics }); toast((S.analytics === 'on' ? '「同意する」を選びました。' : '「同意しない」を選びました。') + 'あとから「マイページ」で変更できます。(模擬)', 4200); changed(); return; }
      if (a === 'an-toggle') { S.analytics = analyticsOn() ? 'off' : 'on'; logEv({ ev: 'analytics', v: S.analytics }); render(true); toast(analyticsOn() ? DRAFT.analytics.onToast : DRAFT.analytics.offToast); return; }
      if (a === 'an-info') { showAnalyticsInfo(); return; }
      if (a === 'buy') { openApple(); return; }
      if (a === 'buy-result') { buyResult(el.getAttribute('data-r')); return; }
      if (a === 'restore') { closeModal(); openRestore(); return; }
      if (a === 'restore-result') {
        var r = el.getAttribute('data-r'); logEv({ ev: 'restore', r: r });
        if (r === 'found') { closeModal(); if (S.mode !== 'paid' && S.mode !== 'canceled') becomePaid(); render(true); toast('有料会員の資格を復元しました。(模擬)'); }
        else if (r === 'none') openModal(sheet('<h3>復元できる契約が見つかりませんでした ' + note() + '</h3><p>この Apple Account で購入した有効な有料会員の契約がありません。追加料金はかかりません。</p><div class="acts"><button type="button" class="pvbtn free" data-act="modal-close">閉じる</button></div>'), 'restore_none');
        else closeModal();
        return;
      }
      if (a === 'manage') { openManage(); return; }
      if (a === 'manage-result') { var m2 = el.getAttribute('data-r'); logEv({ ev: 'manage', r: m2 }); closeModal(); if (m2 === 'cancel') { S.mode = 'canceled'; render(true); toast('自動更新を停止しました。利用期限までご利用いただけます。(模擬)'); } else if (m2 === 'resume') { S.mode = 'paid'; render(true); } return; }
      if (a === 'legal') { toast('「' + el.getAttribute('data-name') + '」ページへ移動します(プレビューでは移動しません)'); return; }
      if (a === 'fav-row') { toast('お気に入り記事の一覧へ移動します(プレビューでは省略)'); return; }
      if (a === 'help') { toast('使い方(チュートリアル)はプレビューでは省略しています'); return; }
      if (a === 'del-saved') { var d = el.getAttribute('data-slug'); S.saved = S.saved.filter(function (x) { return x !== d; }); render(true); toast('保存を削除しました'); return; }
      if (a === 'mini-pp') { S.paused = !S.paused; render(true); return; }
      if (a === 'omakase') { if (S.mode === 'free') return; perform(ITEMS[0].slug, 'play'); toast('おまかせラジオを始めます(模擬): ' + LV[S.level] + ' · ランダム連続再生'); return; }
      if (a === 'review-play') { var ri = +el.getAttribute('data-i'); logEv({ ev: 'review_play', i: ri }); toast('復習帳の音声を再生します(模擬): ' + REVIEW[ri][0]); return; }
      return;
    }
    if ((el = t.closest('[data-fav]'))) { e.preventDefault(); e.stopPropagation(); var f = el.getAttribute('data-fav'); S.fav = isFav(f) ? S.fav.filter(function (x) { return x !== f; }) : S.fav.concat([f]); logEv({ ev: 'fav', slug: f }); render(true); return; }
    if ((el = t.closest('[data-lv]'))) { S.level = el.getAttribute('data-lv'); render(true); return; }
    if ((el = t.closest('[data-play]'))) { e.preventDefault(); e.stopPropagation(); request(el.getAttribute('data-play'), 'play'); return; }
    if ((el = t.closest('[data-req]'))) { e.preventDefault(); request(el.getAttribute('data-slug'), el.getAttribute('data-req')); return; }
    if ((el = t.closest('#nav a'))) { e.preventDefault(); navTab(el.getAttribute('data-tab')); return; }
    if ((el = t.closest('[data-row]'))) { e.preventDefault(); var rs = el.getAttribute('data-row'); if (canUse(rs)) perform(rs, 'open'); else request(rs, 'open'); return; }
    if ((el = t.closest('[data-open]'))) { e.preventDefault(); logEv({ ev: 'open_article', slug: el.getAttribute('data-open') }); push('art:' + el.getAttribute('data-open')); return; }
  });
  document.addEventListener('keydown', function (e) { if (e.key === 'Enter' && e.target && e.target.classList && e.target.classList.contains('card')) e.target.click(); });

  /* ---------- 外部(操作パネル)用API: プレビュー専用 ---------- */
  var PV = {
    get: function () { return S; },
    log: function () { return LOG; },
    items: function () { return ITEMS; },
    preset: function (id) { applyPreset(id); render(); },
    patch: function (p) { for (var k in p) S[k] = p[k]; if (S.mode === 'trial') S.today = addDays(FIRST_LAUNCH, S.day - 1); render(true); },
    setDay: function (d) { S.day = d; S.today = addDays(FIRST_LAUNCH, d - 1); render(true); },
    setSelected: function (slug) { S.selected = slug || null; render(true); },
    setOffline: function (b) { S.offline = !!b; render(true); },
    setGrace: function (b) { S.grace = !!b; render(true); },
    setPromoSince: function (n) { S.promoSince = n; changed(); },
    /* 翌日0時: 無料枠リセット。体験中は日が進み、8日目の終わりを過ぎると無料会員へ移行。解約済みは利用期限を過ぎると契約終了。 */
    midnight: function () {
      var msg = '日付が変わりました(0時)。今日の無料記事がリセットされました。';
      S.selected = null; S.today = addDays(S.today, 1);
      if (S.mode === 'trial') {
        S.day += 1;
        if (S.day > 8) { endTrial(); msg = '日付が変わりました(0時)。無料体験が終了し、無料会員になりました。'; } else S.today = addDays(FIRST_LAUNCH, S.day - 1);
      } else if (S.mode === 'free') S.promoSince += 1;
      else if (S.mode === 'canceled' && S.today > S.renew) { endContract(); msg = '日付が変わりました(0時)。契約期間が終わり、無料会員になりました。'; }
      render(true); toast(msg);
    },
    endContract: function () { if (S.mode !== 'canceled' && S.mode !== 'paid') return; S.today = addDays(S.renew, 1); endContract(); render(true); toast('契約期間が終わりました。無料会員になりました。'); },
    resolvePending: function (ok) { if (!S.pendingBuy) return; if (ok) { becomePaid(); S.tab = 'me'; S.route = 'me'; S.stack = []; render(); toast('購入が承認されました。有料会員になりました。(模擬)'); } else { S.pendingBuy = false; render(true); toast('購入は承認されませんでした。(模擬)'); } },
    reshow: function (which) {
      S.tab = 'home'; S.route = 'home'; S.stack = []; S.playing = null; closeModal(); closeFull();
      if (which === 'te') { S.mode = 'free'; S.pend.te = true; } if (which === 'pe') { S.mode = 'free'; S.pend.pe = true; } if (which === 'promo') { S.mode = 'free'; S.promoSince = 7; }
      if (which === 'intro') { S.mode = 'trial'; S.day = 1; S.today = FIRST_LAUNCH; S.intro = true; S.introStep = 1; S.analytics = 'unset'; }
      render();
    },
    nav: function (route) {
      closeModal();
      if (route === 'home' || route === 'search' || route === 'review' || route === 'me') navTab(route);
      else { S.stack = [S.tab]; S.route = route; render(); }
    },
    request: function (slug, kind) { request(slug, kind); },
    scrollTo: function (id) { var el = $(id); if (el) el.scrollIntoView(); },
    notes: function (on) { document.body.classList.toggle('nonotes', !on); },
    remainLabel: function (todayIso) { return remainLabel(todayIso, TRIAL_END); },
    dayLabel: function (k) { var t = addDays(FIRST_LAUNCH, k - 1), d = pd(t); return k + '日目(' + (d.getMonth() + 1) + '/' + d.getDate() + ') → ' + remainLabel(t, TRIAL_END); },
    modal: modalName, trialEndISO: function () { return TRIAL_END; }
  };
  window.PV = PV;

  var xhr = new XMLHttpRequest();
  xhr.open('GET', 'data/catalog_preview.json');
  xhr.onload = function () {
    ITEMS = JSON.parse(xhr.responseText).items;
    applyPreset('trial'); render();
    window.PV_READY = true;
    try { if (window.parent && window.parent.PVshell && window.parent.PVshell.ready) window.parent.PVshell.ready(); } catch (x) { }
  };
  xhr.send();
})();
