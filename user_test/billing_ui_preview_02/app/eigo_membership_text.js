/* eigo_membership_text.js -- the ONE wording / configuration table of the iOS membership UI (RELEASE-IOS-BILLING-MEMBERSHIP-01 Lane C, C5).
   iOS only: loaded by the app build next to the adapter (scripts/anchors.mjs, html-scripts). The Web / Android builds do not contain this file.
   Two kinds of text, kept apart so a later change touches exactly one place:
   - APPROVED : wording the user approved verbatim (user original 2026-11-26 section 4, file test/fixtures/membership_user_original_20261126.md). Never edit without a new user approval.
                test/membership_ui.test.mjs checks every APPROVED string against the original and against the rendered screens.
   - DRAFT    : proposals that are NOT approved yet (the user is reviewing user_test/billing_ui_preview_01). Same wording as the preview; replace here when the user answers.
   - CONFIG   : values that are settings, not wording (legal page keys, default price used only until the store answers).
   No code outside this file owns membership wording (test: eigo_membership_ui.js / bridge contain no such text). UI APPROVAL PENDING: nothing here is a final design. */
(function (root) {
  'use strict';
  var APPROVED = {
    confirm: {   // section 4-2 (free article choice). {title} is the article title
      question: '今日の無料記事は「{title}」にしますか？',
      lines: ['（無料会員は1日1記事）', '一度決定すると、変更できません。', '有料会員なら、すべての記事を自由に視聴できます。'],
      ok: '決定する', cancel: 'キャンセル'
    },
    trialEnd: {   // section 4-3-2
      title: '無料体験が終了しました',
      body: ['eigo-radioをお楽しみいただけましたか？', 'これからも、面白い英語を', '好きなだけ楽しみませんか？'],
      meritTitle: '有料会員のメリット',
      merits: ['毎日の新着記事がすべて聴き放題', '気になる過去の記事も自由に楽しめる', '全記事を自由にダウンロード・オフライン再生'],
      priceTitle: '料金', price: '月額{yen}円', perDay: '1日あたり約{perDay}円',
      join: '有料会員になる', stay: '無料で利用を続ける（1日1記事）'
    },
    promo: {   // section 4-3-3
      title: ['もっと自由に、', '英語を楽しみませんか？'],
      body: '有料会員なら、毎日1記事の制限なく、気になる記事を自由に楽しめます。',
      merits: ['新着記事・過去記事がすべて聴き放題', '全記事を自由にダウンロード・オフライン再生'],
      price: '月額{yen}円', join: '有料会員になる', stay: '今は無料で利用する'
    },
    paywall: {   // section 4-4 (unavailable article)
      title: 'この記事は有料会員限定です',
      body: '有料会員なら、新着記事も過去記事も、すべて自由にお楽しみいただけます。',
      price: '月額{yen}円', join: '有料会員になる', close: '閉じる'
    },
    paidEnd: {   // section 4-6
      title: '有料会員期間が終了しました',
      p1: 'これまでご利用いただき、ありがとうございます。',
      p2: 'これからも、毎日お好きな1記事を無料でお楽しみいただけます。',
      p3: '復習帳やお気に入りなど、これまでの学習データは引き続きご利用いただけます。',
      invite: 'また、すべての記事を楽しみませんか？',
      price: '月額{yen}円', join: '有料会員になる', stay: '無料で利用を続ける'
    },
    join: {   // section 4-5 (common join screen)
      title: '有料会員のご案内',
      main: ['もっと自由に、', '英語を楽しもう。'],
      sub: '気になる記事を、好きなだけ。',
      meritTitle: '有料会員のメリット',
      merits: ['毎日の新着記事がすべて聴き放題', '過去の記事もすべて利用可能', '全記事を自由にダウンロード・オフライン再生'],
      planName: '有料会員プラン', price: '{yen}円／月（税込）', renewal: '1か月ごとの自動更新',
      button: '月額{yen}円で有料会員になる',
      restore: '購入を復元する', terms: '利用規約', privacy: 'プライバシーポリシー'
    },
    trialBuyNotice: '現在、{date}まで全機能を無料でご利用いただけます。有料会員に加入すると、加入時点から料金が発生します。',   // section 4-5 (join during the trial); {date} = trial end date
    restore: {   // section 4-9
      sectionTitle: 'その他の手続き', name: '購入を復元する',
      note: '機種変更や再インストールなどで、契約済みの有料会員資格が反映されない場合にご利用ください。追加料金はかかりません。'
    },
    trialBar: '全機能無料体験中　あと{days}日',   // section 4-3-1 (example wording)
    settings: {   // section 4-9: item names are approved; the descriptive sentences are in DRAFT.settings
      planLabel: '現在の利用プラン', trial: '無料体験中', free: '無料会員', paid: '有料会員',
      trialEndDate: '無料体験終了日', monthly: '月額{yen}円（税込）', monthlyShort: '月額{yen}円', nextRenewal: '次回更新日', contractState: '契約状態', stoppedAuto: '自動更新停止済み', expiry: '利用期限',
      join: '有料会員になる'
    },
    legalRows: { terms: '利用規約', tokushoho: '特定商取引法に基づく表記' }   // section 4-9 (support / other): item names
  };

  var DRAFT = {   // NOT approved. Shown to the user in the preview as 文言案
    intro: { title: 'eigo-radioへようこそ', lead: '{end}の終わりまで、すべての記事・機能を無料でお使いいただけます。',
      items: ['決済情報の登録は不要。自動で課金されることはありません。', '体験が終わっても、毎日好きな1記事は無料で利用できます。'], button: 'はじめる' },
    // Usage-data consent (user decision 2026-11-26 USER_02 sec 1: plan 2, built into the first free-trial notice, plain and not heavy; the privacy policy sec 2-8 / 5 says the same).
    // B5: ONE short screen. The three notice items (what is sent / to whom / why) are in the lead; the details are one tap away. Both answers equal in weight and order; the app works the same with either answer.
    consent: {
      title: '利用状況の送信について',
      lead: 'アプリの使われ方の情報(再生や機能の利用状況、エラーの種類など)を、サービスの改善のため、Google LLC(Google アナリティクス)へ送ってもよいかおたずねします。広告には使いません。',
      freedom: 'どちらを選んでも、アプリの機能は同じです。あとから、マイページの「利用状況の送信」で変えられます。',
      more: 'くわしく見る', less: 'とじる',
      whatTitle: '送る情報', what: ['再生や機能の利用状況、購入手続きの進み具合', 'エラーの種類、端末とアプリの情報、おおよその地域', 'アプリごとの識別番号(氏名やApple Accountとは結び付きません)'],
      notSentTitle: '送らない情報', notSent: 'お支払い情報、氏名、メールアドレス、Apple Accountの情報、入力した文章、正確な位置情報は送りません。',
      agreeFirst: '同意して始める', declineFirst: '同意しないで始める', agree: '同意する', decline: '同意しない', saveFail: '選択を保存できませんでした。もう一度お試しください。'
    },
    consentSettings: {
      section: '利用状況の送信', row: '利用状況を送信する', on: 'オン', off: 'オフ', unanswered: '未選択',
      note: 'アプリの使われ方の情報を、サービス改善のためGoogle LLCへ送ります。オフにすると送りません。どちらでも機能は同じです。',
      offDone: 'オフにしました。これ以降は送信しません。', onDone: 'オンにしました。'
    },
    trialBarLast: '全機能無料体験中　本日まで',   // last trial day (user decision 2026-11-26 USER_02 sec 3-1: plan B = remaining days do not count today; the last day says "本日まで")
    paywallNote: '今日の無料記事はすでに選択済みです。明日(0時を過ぎると)になれば、この記事も無料記事として選べます。',
    expired: { title: 'この記事は、いまは再生できません', p1: 'ダウンロード済みのデータは削除されていません。',
      p2: '今日の無料記事として選ぶか、有料会員になると、また聴けるようになります。',
      p2picked: '明日(0時を過ぎると)になれば、今日の無料記事として選ぶこともできます。',
      pick: '今日の無料記事にする', join: '有料会員になる', close: '閉じる' },
    terms: [
      'お支払いは、購入の確定時に、お使いのApple Accountへ請求されます。',
      '契約は1か月ごとに自動更新されます。現在の契約期間が終了する24時間前までに自動更新をオフにしない限り、契約は自動的に更新され、更新料金({yen}円／月・税込)がApple Accountへ請求されます。',
      '契約の確認・解約は、購入後いつでも、iPhoneの「設定」>[自分の名前]>「サブスクリプション」から行えます。解約しても、現在の契約期間の終了までは有料会員としてご利用いただけます。'
    ],
    draftMark: '文言案・要確認',
    freeBarNone: '今日の無料記事：まだ選んでいません(好きな1記事を選べます)',
    freeBarPicked: '今日の無料記事：{title}',
    freeChip: '今日の無料記事',
    buyFailTitle: '購入できませんでした', buyFail: '購入を完了できませんでした。通信状況をご確認のうえ、もう一度お試しください。',
    buyPendingTitle: '購入は承認待ちです', buyPending: '購入はまだ確定していません(承認待ち)。承認されるまで、有料会員の機能はご利用いただけません。',
    buyUnverifiedTitle: '購入を確認できませんでした', buyUnverified: '購入の内容をAppleで確認できませんでした。有料会員の機能は、確認できるまでご利用いただけません。しばらくしてから「購入を復元する」をお試しください。',
    retry: 'もう一度試す', close: '閉じる', working: '処理しています…',
    buyOk: '有料会員になりました。すべての記事・機能をご利用いただけます。',
    productLoading: '価格を確認しています…', productFail: '価格を取得できません。通信状況をご確認のうえ、もう一度お試しください。', productRetry: 'もう一度取得する',
    restoreOk: '有料会員の資格を復元しました。', restoreNoneTitle: '復元できる契約が見つかりませんでした',
    restoreNone: 'このApple Accountで購入した有効な有料会員の契約がありません。追加料金はかかりません。', restoreFailTitle: '復元できませんでした', restoreFail: '通信状況をご確認のうえ、もう一度お試しください。', restoreWorking: '確認しています…',
    manageFail: '契約の管理画面を開けませんでした。iPhoneの「設定」から確認してください。',
    manageRow: '契約内容の確認・解約', manageRowCancelled: '契約内容の確認・変更',
    alreadyPaid: 'すでに有料会員です(契約の確認・変更はマイページから)。',
    grace: '契約の更新を確認できません。オンラインに戻ると確認します(通信できない場合、最大3日間はそのままご利用いただけます)。',
    offlineSelectHint: 'オフライン中は、保存済みの記事から今日の無料記事を選べます。',
    offlineLockedHint: 'オフラインのため、保存していない記事は開けません。',
    pickSaveFail: '選択を保存できませんでした。もう一度お試しください。',
    deniedToast: 'この記事は、今日は利用できません。有料会員なら、すべての記事を自由にお楽しみいただけます。',
    settings: {
      trialA: 'すべての記事・機能をご利用いただけます。', trialB: '無料体験が終わっても、自動で有料会員になることはありません。',
      freeA: '毎日、好きな1記事を全機能でご利用いただけます。', freeB: '有料会員なら、すべての記事を自由にご利用いただけます。', freeJoinLabel: '有料会員',
      paidA: 'すべての記事・機能をご利用いただけます。', paidCancelledA: '利用期限まで、すべての記事・機能をご利用いただけます。',
      priceLabel: '料金'
    },
    back: '戻る', lockBadgeAria: 'ロック中', lockedPlayAria: '{title} は今日は利用できません(有料会員限定)'
  };

  var CONFIG = {
    legalPages: { terms: 'terms', tokushoho: 'tokushoho', privacy: 'privacy', support: 'support' },   // keys under the public root (same rule as the webapp: <pagesBase>/../../<key>/). terms / tokushoho are NOT published yet (Lane A)
    showDraftMarks: false,   // true = draft (not yet approved) wording is tagged on screen. Off in the product build; the owner of the wording table may turn it on for a review build
    defaultYen: 490   // used ONLY until the store answers (the real price always comes from the store's displayPrice)
  };

  var FORMAT = { md: '{m}月{d}日', ymd: '{y}年{m}月{d}日' };   // date notation (JST calendar date)

  root.EigoMembershipText = { APPROVED: APPROVED, DRAFT: DRAFT, CONFIG: CONFIG, FORMAT: FORMAT };
})(typeof window !== 'undefined' ? window : globalThis);
