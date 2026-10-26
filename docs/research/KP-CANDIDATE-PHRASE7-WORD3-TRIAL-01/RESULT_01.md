# RESULT_01 (KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01 委任_01、2026-10-26)

自動生成(`er124_kp_phrase_word_trial_01.py report`)。現行=Production既定(call1 Prompt 2=3件+call2 Prompt 2-V=最大5件)、Trial=P7(フレーズ最大7)→W3(単語最大3)。Gate=Production関数同一適用(DESIGN_01 §6)。判定: own=自ルーブリック Y/B/N、judge=gpt-6.1-sol(匿名・シャッフル)。

## AIの仮想の島 (X) / Standard (a2)  本文sha256=76f80f62120b 語数=505

現行の出所: reuse(既存kp_candidates.json、run_ai_01)

| 項目 | 現行方式 | Trial方式 r1 | Trial方式 r2 |
|---|---|---|---|
| 要求件数 | 最大8(3+5) | フレーズ7＋単語3(計10) | フレーズ7＋単語3(計10) |
| AI返答件数 | 7 | P7 6＋W3 3＝9 | P7 5＋W3 3＝8 |
| Gate除外件数 | 2 | 0  | 0  |
| 最終候補件数 | 5 | 9 | 8 |
| フレーズ件数 | 5 | 6 | 5 |
| 単語件数 | 0 | 3 | 3 |
| 学習価値・多様性(Y/B/N) | 自Y4/B1/N0・judge Y5/B0/N0・両者Y4 | 自Y7/B2/N0・judge Y9/B0/N0・両者Y7 | 自Y6/B2/N0・judge Y8/B0/N0・両者Y6 |
| 生成コスト | 推計 約¥1.6(他4 levelのfresh現行平均) | 実績 ¥1.447(5 call) | 実績 ¥1.387(5 call) |

### 現行方式 候補全文

| 順位 | 区分 | 英語表現(used_form) | 日本語意味 | 出典文 | 選定理由 | Gate | 自判定 | judge |
|---|---|---|---|---|---|---|---|---|
| 1 | フレーズ(call1#1) | carry over | 持ち越す | But the work area with the AI's notes and programs carried over to the next hour |  | PASS(auto) | Y 句動詞。汎用・適度 | Y |
| 2 | フレーズ(call1#2) | worth paying attention to | 注目する価値がある | One tip in the strategy notes was worth paying attention to |  | PASS(auto) | Y 定型構文。汎用 | Y |
| 3 | フレーズ(call1#3) | a useful card to play | 使える手札 | A discovery that is not useful now might be a useful card to play next time, if it is saved |  | PASS(auto) | B usefulは修飾語。card to play が核(R2過剰) | Y |
| 4 | フレーズ(call2#1) | take a detour | 遠回りをする | Those that had taken a detour were now one step ahead | 本来の道筋から外れることを比喩的に表す。 | PASS(auto) | Y 比喩を含む定番表現 | Y |
| 5 | フレーズ(call2#2) | one step ahead | 一歩先を行っている | Those that had taken a detour were now one step ahead | 一歩先を行く、優位に立つという定番の比喩表現。 | PASS(auto) | Y 定番の比喩表現 | Y |
| (除外) | - | too soon to wave a flag | - | - | - | **validate**: 語数が1〜5語でない(実際: 6語) | - | - |
| (除外) | - | studied separately | - | - | - | **canonicalization**: key_phrase('study separately')がdisplay_phraseと一致せず、source_span('studied separately')内の連続部分文字列でもない(人称 | - | - |

### Trial方式 r1 候補全文(P7返答6・W3返答3、call 5、¥1.447)

| 順位 | 区分 | 英語表現(used_form) | 日本語意味 | 出典文 | 選定理由 | Gate | 自判定 | judge |
|---|---|---|---|---|---|---|---|---|
| 1 | フレーズ(call1#1) | worth paying attention to | 注目する価値がある | One tip in the strategy notes was worth paying attention to |  | PASS(auto) | Y 定型構文。汎用 | Y |
| 2 | フレーズ(call1#2) | carry over | 次にも引き継がれる | But the work area with the AI's notes and programs carried over to the next hour |  | PASS(auto) | Y 句動詞。汎用・適度 | Y |
| 3 | フレーズ(call1#3) | a useful card to play | 使える一手 | A discovery that is not useful now might be a useful card to play next time, if it is saved |  | PASS(auto) | B usefulは修飾語。card to play が核(R2過剰) | Y |
| 4 | フレーズ(call1#4) | take a detour | 寄り道をする | Those that had taken a detour were now one step ahead |  | PASS(auto) | Y 比喩を含む定番表現 | Y |
| 5 | フレーズ(call1#5) | make a difference | 影響を与える | By themselves, they do not show that play itself made a difference |  | PASS(auto) | Y 汎用の定番イディオム | Y |
| 6 | フレーズ(call1#6) | one step ahead | 一歩先を行っている | Those that had taken a detour were now one step ahead |  | PASS(auto) | Y 定番の比喩表現 | Y |
| 7 | 単語(call2#1) | obstacle | 障害物 | Then one AI made its own obstacle course | 困難や妨げを表す汎用性の高い名詞。 | PASS(auto) | Y B1語彙。汎用 | Y |
| 8 | 単語(call2#2) | separately | 別々に | These two results need to be studied separately | 物事を個別に扱うことを示す実用的な副詞。 | PASS(auto) | Y 副詞。Standardでは適度 | Y |
| 9 | 単語(call2#3) | discovery | 新たに分かったこと | The island went back to how it was before, but the AI's discoveries stayed | 新たに得た知見を表す名詞の複数形。 | PASS(auto) | B 基本寄り(R4やや易) | Y |

### Trial方式 r2 候補全文(P7返答5・W3返答3、call 5、¥1.387)

| 順位 | 区分 | 英語表現(used_form) | 日本語意味 | 出典文 | 選定理由 | Gate | 自判定 | judge |
|---|---|---|---|---|---|---|---|---|
| 1 | フレーズ(call1#1) | a useful card to play | 使える切り札 | A discovery that is not useful now might be a useful card to play next time, if it is saved |  | PASS(auto) | B usefulは修飾語。card to play が核(R2過剰) | Y |
| 2 | フレーズ(call1#2) | carry over | 次にも引き継がれる | But the work area with the AI's notes and programs carried over to the next hour |  | PASS(auto) | Y 句動詞。汎用・適度 | Y |
| 3 | フレーズ(call1#3) | take a detour | 回り道をする | Those that had taken a detour were now one step ahead |  | PASS(auto) | Y 比喩を含む定番表現 | Y |
| 4 | フレーズ(call1#4) | worth paying attention to | 気に留める価値がある | One tip in the strategy notes was worth paying attention to |  | PASS(auto) | Y 定型構文。汎用 | Y |
| 5 | フレーズ(call1#5) | one step ahead | 一歩先を行く | Those that had taken a detour were now one step ahead |  | PASS(auto) | Y 定番の比喩表現 | Y |
| 6 | 単語(call2#1) | Strategy | 作戦 | But AI Has "Strategy Notes | 計画や方策を表す、幅広い場面で使える語です。 | PASS(auto) | B 基本寄り+見出し由来の大文字表記 | Y |
| 7 | 単語(call2#2) | separately | 分けて | These two results need to be studied separately | 物事を個別に扱うことを表す副詞です。 | PASS(auto) | Y 副詞。Standardでは適度 | Y |
| 8 | 単語(call2#3) | obstacle | じゃまになるもの | Then one AI made its own obstacle course | 進行を妨げる障害を表す汎用性の高い語です。 | PASS(auto) | Y B1語彙。汎用 | Y |

## AIの仮想の島 (X) / Advanced (b1b)  本文sha256=00f14092c072 語数=533

現行の出所: reuse(既存kp_candidates.json、run_ai_01)

| 項目 | 現行方式 | Trial方式 r1 | Trial方式 r2 |
|---|---|---|---|
| 要求件数 | 最大8(3+5) | フレーズ7＋単語3(計10) | フレーズ7＋単語3(計10) |
| AI返答件数 | 7 | P7 5＋W3 3＝8 | P7 5＋W3 3＝8 |
| Gate除外件数 | 0 | 0  | 0  |
| 最終候補件数 | 7 | 8 | 8 |
| フレーズ件数 | 7 | 5 | 5 |
| 単語件数 | 0 | 3 | 3 |
| 学習価値・多様性(Y/B/N) | 自Y5/B1/N1・judge Y5/B0/N2・両者Y5 | 自Y5/B2/N1・judge Y6/B0/N2・両者Y5 | 自Y4/B3/N1・judge Y6/B0/N2・両者Y4 |
| 生成コスト | 推計 約¥1.6(他4 levelのfresh現行平均) | 実績 ¥1.495(5 call) | 実績 ¥1.647(5 call) |

### 現行方式 候補全文

| 順位 | 区分 | 英語表現(used_form) | 日本語意味 | 出典文 | 選定理由 | Gate | 自判定 | judge |
|---|---|---|---|---|---|---|---|---|
| 1 | フレーズ(call1#1) | carry over | 次に持ち越す | In the experiment, the island and the conversation were reset every hour, but the work area where the AI kept notes and programs was carried over |  | PASS(auto) | Y 句動詞 | Y |
| 2 | フレーズ(call1#2) | call on | 頼まれる | So, would that experience help the AI the next time it was called on |  | PASS(auto) | Y 句動詞(頼まれる) | Y |
| 3 | フレーズ(call1#3) | look at separately | 分けて考える | The fact that the experienced group did better and the fact that removing a particular memory lowered its score need to be looked at separately |  | PASS(auto) | B 受動の語尾を落とした切り出しでやや不自然 | N |
| 4 | フレーズ(call2#1) | one step ahead | 一歩先を行く | The ones that had taken a detour were now one step ahead | 「一歩先を行く」という優位性を表す定番表現。 | PASS(auto) | Y 定番の比喩 | Y |
| 5 | フレーズ(call2#2) | card to play | 使える手 | A discovery that is no use right now might become a useful card to play next time, if it is saved | 「切れるカード・有効な手段」という比喩表現。 | PASS(auto) | Y 最小形のイディオム | Y |
| 6 | フレーズ(call2#3) | take a detour | 寄り道をする | The ones that had taken a detour were now one step ahead | 本筋を外れて別の経験をする比喩的な表現。 | PASS(auto) | Y 比喩を含む | Y |
| 7 | フレーズ(call2#4) | no use right now | 今は役に立たない | A discovery that is no use right now might become a useful card to play next time, if it is saved | 「今は役に立たない」を表す自然な言い回し。 | PASS(auto) | N 基本語のみ+right nowは余剰(数合わせ型) | N |

### Trial方式 r1 候補全文(P7返答5・W3返答3、call 5、¥1.495)

| 順位 | 区分 | 英語表現(used_form) | 日本語意味 | 出典文 | 選定理由 | Gate | 自判定 | judge |
|---|---|---|---|---|---|---|---|---|
| 1 | フレーズ(call1#1) | carry over | 次の期間に引き継ぐ | In the experiment, the island and the conversation were reset every hour, but the work area where the AI kept notes and programs was carried over |  | PASS(auto) | Y 句動詞 | Y |
| 2 | フレーズ(call1#2) | a useful card to play | 使える切り札 | A discovery that is no use right now might become a useful card to play next time, if it is saved |  | PASS(auto) | B usefulは修飾語(R2過剰) | N |
| 3 | フレーズ(call1#3) | call on | 何かを頼まれる | So, would that experience help the AI the next time it was called on |  | PASS(auto) | Y 句動詞(頼まれる) | Y |
| 4 | フレーズ(call1#4) | look at separately | 分けて考える | The fact that the experienced group did better and the fact that removing a particular memory lowered its score need to be looked at separately |  | PASS(auto) | B 受動の語尾を落とした切り出しでやや不自然 | N |
| 5 | フレーズ(call1#5) | take a detour | 寄り道をする | The ones that had taken a detour were now one step ahead |  | PASS(auto) | Y 比喩を含む | Y |
| 6 | 単語(call2#1) | performance | 課題の出来 | Saved discoveries may help with later tower building, but the results do not prove that play itself improves performance | 成果や遂行能力を幅広い文脈で表す重要語です。 | PASS(auto) | N 易しい語。glossも文脈依存 | Y |
| 7 | 単語(call2#2) | exploration | 周りを探検すること | They had no homework, but they were in exploration mode | 調査や探究を表し、幅広い分野で使われます。 | PASS(auto) | Y B2名詞。汎用 | Y |
| 8 | 単語(call2#3) | overlook | 見過ごす | One tip in the strategy notes was not something to overlook | 「見落とす」という意味の動詞で、文章読解にも役立ちます。 | PASS(auto) | Y B2動詞。汎用 | Y |

### Trial方式 r2 候補全文(P7返答5・W3返答3、call 5、¥1.647)

| 順位 | 区分 | 英語表現(used_form) | 日本語意味 | 出典文 | 選定理由 | Gate | 自判定 | judge |
|---|---|---|---|---|---|---|---|---|
| 1 | フレーズ(call1#1) | a useful card to play | 使える一手 | A discovery that is no use right now might become a useful card to play next time, if it is saved |  | PASS(auto) | B usefulは修飾語(R2過剰) | N |
| 2 | フレーズ(call1#2) | carry over | 持ち越す | In the experiment, the island and the conversation were reset every hour, but the work area where the AI kept notes and programs was carried over |  | PASS(auto) | Y 句動詞 | Y |
| 3 | フレーズ(call1#3) | call on | 頼む | So, would that experience help the AI the next time it was called on |  | PASS(auto) | Y 句動詞(頼まれる) | Y |
| 4 | フレーズ(call1#4) | take a detour | 寄り道をする | The ones that had taken a detour were now one step ahead |  | PASS(auto) | Y 比喩を含む | Y |
| 5 | フレーズ(call1#5) | exploration mode | 探検モード | They had no homework, but they were in exploration mode |  | PASS(auto) | B mode付きは記事寄り | N |
| 6 | 単語(call2#1) | overlook | 見過ごす | One tip in the strategy notes was not something to overlook | 「見落とす・軽視する」の意味で幅広く使える動詞。 | PASS(auto) | Y B2動詞。汎用 | Y |
| 7 | 単語(call2#2) | technique | やり方 | The researchers also removed a description of a technique for "throwing rocks to get more blocks" from one AI's memory | 方法や技能を表し、専門分野を問わず使える語。 | PASS(auto) | B 基本寄り | Y |
| 8 | 単語(call2#3) | performance | 出来 | Saved discoveries may help with later tower building, but the results do not prove that play itself improves performance | 能力や成果を表す、幅広い文脈で役立つ語。 | PASS(auto) | N 易しい語。glossも文脈依存 | Y |

## 英国の電車マナー (X) / Standard (a2)  本文sha256=3d17265a2887 語数=461

現行の出所: fresh(DEV実行、Production既定のgenerate_candidates)

| 項目 | 現行方式 | Trial方式 r1 | Trial方式 r2 |
|---|---|---|---|
| 要求件数 | 最大8(3+5) | フレーズ7＋単語3(計10) | フレーズ7＋単語3(計10) |
| AI返答件数 | 7 | P7 4＋W3 3＝7 | P7 5＋W3 3＝8 |
| Gate除外件数 | 1 | 1 {'canonicalization': 1} | 2 {'validate': 1, 'canonicalization': 1} |
| 最終候補件数 | 6 | 6 | 6 |
| フレーズ件数 | 6 | 3 | 3 |
| 単語件数 | 0 | 3 | 3 |
| 学習価値・多様性(Y/B/N) | 自Y3/B1/N2・judge Y3/B0/N3・両者Y3 | 自Y4/B2/N0・judge Y5/B0/N1・両者Y4 | 自Y4/B2/N0・judge Y5/B0/N1・両者Y4 |
| 生成コスト | 実績 ¥1.315(5 call) | 実績 ¥1.773(7 call) | 実績 ¥1.949(7 call) |

### 現行方式 候補全文

| 順位 | 区分 | 英語表現(used_form) | 日本語意味 | 出典文 | 選定理由 | Gate | 自判定 | judge |
|---|---|---|---|---|---|---|---|---|
| 1 | フレーズ(call1#1) | point to current rail rules | 今ある鉄道のルールを引き合いに出す | The campaign points to current rail rules and asks people to think about others |  | PASS(auto) | N 記事固有で再利用不可(R3) | N |
| 2 | フレーズ(call1#2) | written permission | 書面での許可 | There is an exception when the train company has given written permission |  | PASS(auto) | Y 汎用コロケーション | Y |
| 3 | フレーズ(call1#3) | draw a line | 境界線を引く | The words draw that line simply |  | PASS(auto) | Y 比喩の定番 | Y |
| 4 | フレーズ(call2#1) | put on an unwanted show | 見たくない人に見せ物を押しつける | Is Your Video Putting on an Unwanted Show on the Train | 「見せ物を演じる」という比喩的な用法が学べる。 | PASS(auto) | N 見出し由来で記事固有・glossも不自然 | N |
| 5 | フレーズ(call2#2) | sound no one asked for | 誰も求めていない音 | Here's news about this kind of "sound no one asked for | 頼んでもいない騒音を皮肉っぽく表す口語表現。 | PASS(auto) | B 見出し由来でやや記事寄り | N |
| 6 | フレーズ(call2#3) | reach for one's wallet | 自分の財布を取ろうと手を伸ばす | That's enough to make you reach for your wallet before the volume button | 出費を覚悟することを表す慣用的な言い回し。 | PASS(auto) | Y 定番表現 | Y |
| (除外) | - | up to £1,000 | - | - | - | **validate**: 数字を含む(数値placeholder型の回避: 数値を補わないと成立しない形/音声化で不安定になる形は選ばない) | - | - |

### Trial方式 r1 候補全文(P7返答4・W3返答3、call 7、¥1.773)

| 順位 | 区分 | 英語表現(used_form) | 日本語意味 | 出典文 | 選定理由 | Gate | 自判定 | judge |
|---|---|---|---|---|---|---|---|---|
| 1 | フレーズ(call1#1) | draw a line | はっきり区別する | The words draw that line simply |  | PASS(auto) | Y 比喩の定番 | Y |
| 2 | フレーズ(call1#2) | sound no one asked for | 誰も頼んでいない音 | Here's news about this kind of "sound no one asked for |  | PASS(auto) | B 見出し由来でやや記事寄り | N |
| 3 | フレーズ(call1#4) | reach for one's wallet | 自分の財布に手を伸ばす | That's enough to make you reach for your wallet before the volume button |  | PASS(auto) | Y 定番表現 | Y |
| 4 | 単語(call2#1) | exception | 例外となる場合 | There is an exception when the train company has given written permission | 例外を表し、幅広い説明や議論で使える語です。 | PASS(auto) | Y B1名詞。汎用 | Y |
| 5 | 単語(call2#2) | masterpiece | 名作 | A song may sound like a masterpiece to you, but not to the person beside you | 傑作を意味し、評価を表す語として応用できます。 | PASS(auto) | Y B2名詞。汎用 | Y |
| 6 | 単語(call2#3) | audience | 視聴者 | One smartphone makes the whole train carriage an audience | 聴衆や観客を表し、幅広い場面で使えます。 | PASS(auto) | B 基本寄り(R4やや易) | Y |
| (除外) | - | given written permission | - | - | - | **canonicalization**: key_phrase('give written permission')がdisplay_phraseと一致せず、source_span('given written permission')内の連 | - | - |

### Trial方式 r2 候補全文(P7返答5・W3返答3、call 7、¥1.949)

| 順位 | 区分 | 英語表現(used_form) | 日本語意味 | 出典文 | 選定理由 | Gate | 自判定 | judge |
|---|---|---|---|---|---|---|---|---|
| 1 | フレーズ(call1#1) | draw a line | 一線を引く | The words draw that line simply |  | PASS(auto) | Y 比喩の定番 | Y |
| 2 | フレーズ(call1#2) | sound no one asked for | 誰も求めていない音 | Here's news about this kind of "sound no one asked for |  | PASS(auto) | B 見出し由来でやや記事寄り | N |
| 3 | フレーズ(call1#4) | reach for one's wallet | 支払いに備えて自分の財布に手を伸ばす | That's enough to make you reach for your wallet before the volume button |  | PASS(auto) | Y 定番表現 | Y |
| 4 | 単語(call2#1) | exception | 決まりに当てはまらない場合 | There is an exception when the train company has given written permission | 規則や一般論の例外を表す汎用性の高い語です。 | PASS(auto) | Y B1名詞。汎用 | Y |
| 5 | 単語(call2#2) | masterpiece | とてもすばらしい作品 | A song may sound like a masterpiece to you, but not to the person beside you | 芸術作品や優れた成果を評価する際に使えます。 | PASS(auto) | Y B2名詞。汎用 | Y |
| 6 | 単語(call2#3) | carriage | 列車の車両 | One smartphone makes the whole train carriage an audience | 列車の客車を指す語で、英国英語の理解に役立ちます。 | PASS(auto) | B 基本寄り・英国寄りの意味 | Y |
| (除外) | - | up to £1,000 | - | - | - | **validate**: 数字を含む(数値placeholder型の回避: 数値を補わないと成立しない形/音声化で不安定になる形は選ばない) | - | - |
| (除外) | - | given written permission | - | - | - | **canonicalization**: key_phrase('give written permission')がdisplay_phraseと一致せず、source_span('given written permission')内の連 | - | - |

## 英国の電車マナー (X) / Advanced (b1b)  本文sha256=4bd94d783355 語数=477

現行の出所: fresh(DEV実行、Production既定のgenerate_candidates)

| 項目 | 現行方式 | Trial方式 r1 | Trial方式 r2 |
|---|---|---|---|
| 要求件数 | 最大8(3+5) | フレーズ7＋単語3(計10) | フレーズ7＋単語3(計10) |
| AI返答件数 | 8 | P7 6＋W3 3＝9 | P7 5＋W3 3＝8 |
| Gate除外件数 | 0 | 0  | 0  |
| 最終候補件数 | 8 | 9 | 8 |
| フレーズ件数 | 8 | 6 | 5 |
| 単語件数 | 0 | 3 | 3 |
| 学習価値・多様性(Y/B/N) | 自Y5/B1/N2・judge Y6/B0/N2・両者Y5 | 自Y7/B2/N0・judge Y9/B0/N0・両者Y7 | 自Y6/B2/N0・judge Y8/B0/N0・両者Y6 |
| 生成コスト | 実績 ¥1.577(5 call) | 実績 ¥1.744(5 call) | 実績 ¥1.572(5 call) |

### 現行方式 候補全文

| 順位 | 区分 | 英語表現(used_form) | 日本語意味 | 出典文 | 選定理由 | Gate | 自判定 | judge |
|---|---|---|---|---|---|---|---|---|
| 1 | フレーズ(call1#1) | blanket ban | 全面的な禁止 | The UK has launched a nationwide campaign urging rail passengers to use headphones, not a blanket ban on sound |  | PASS(auto) | Y コロケーション | Y |
| 2 | フレーズ(call1#2) | reach for one's wallet | 自分の財布に手を伸ばす | That's enough to make you reach for your wallet before the volume button |  | PASS(auto) | Y 定番表現 | Y |
| 3 | フレーズ(call1#3) | draw a line | 線を引く | The words draw that line simply |  | PASS(auto) | Y 比喩の定番 | Y |
| 4 | フレーズ(call2#1) | be covered | 規則の対象になる | A smartphone speaker can also be covered, if the situation meets the rules | 規則や制度の適用対象になることを表す。 | PASS(auto) | N 文脈依存で単独では不明確(R2) | N |
| 5 | フレーズ(call2#2) | due to be shared | 伝えられる予定だ | The message is due to be shared through posters and announcements at stations and on trains | 予定を表す「be due to」の受動態の形。 | PASS(auto) | B be due toが核。shared付きでやや過剰 | Y |
| 6 | フレーズ(call2#3) | face a fine | 罰金を科される | If you don't follow the rules, you could face a fine of up to £1,000 | 罰金を科される可能性に直面する表現。 | PASS(auto) | Y コロケーション | Y |
| 7 | フレーズ(call2#4) | written permission | 書面での許可 | There is an exception if the rail company has given written permission | 正式な許可を表す定型的な組み合わせ。 | PASS(auto) | Y コロケーション | Y |
| 8 | フレーズ(call2#5) | up to | 最大で | If you don't follow the rules, you could face a fine of up to £1,000 | 金額などの上限を示す表現。 | PASS(auto) | N 基本語(R4) | N |

### Trial方式 r1 候補全文(P7返答6・W3返答3、call 5、¥1.744)

| 順位 | 区分 | 英語表現(used_form) | 日本語意味 | 出典文 | 選定理由 | Gate | 自判定 | judge |
|---|---|---|---|---|---|---|---|---|
| 1 | フレーズ(call1#1) | draw a line | 境界線を引く | The words draw that line simply |  | PASS(auto) | Y 比喩の定番 | Y |
| 2 | フレーズ(call1#2) | blanket ban | 一律の禁止 | The UK has launched a nationwide campaign urging rail passengers to use headphones, not a blanket ban on sound |  | PASS(auto) | Y コロケーション | Y |
| 3 | フレーズ(call1#3) | due to be shared | 伝えられる予定だ | The message is due to be shared through posters and announcements at stations and on trains |  | PASS(auto) | B be due toが核。shared付きでやや過剰 | Y |
| 4 | フレーズ(call1#4) | reach for one's wallet | 自分の財布を手に取ろうとする | That's enough to make you reach for your wallet before the volume button |  | PASS(auto) | Y 定番表現 | Y |
| 5 | フレーズ(call1#5) | written permission | 文書での許可 | There is an exception if the rail company has given written permission |  | PASS(auto) | Y コロケーション | Y |
| 6 | フレーズ(call1#6) | face a fine | 罰金を科される | If you don't follow the rules, you could face a fine of up to £1,000 |  | PASS(auto) | Y コロケーション | Y |
| 7 | 単語(call2#1) | Uninvited | 望まれていない | Are You Giving That Video an Uninvited Premiere on the Train | 招かれていない・求められていない状態を表す形容詞です。 | PASS(auto) | Y B2形容詞 | Y |
| 8 | 単語(call2#2) | automatically | 勝手に | It doesn't mean everyone who plays something through a speaker automatically gets a £1,000 bill | 人や状況を問わず「自動的に」を表す汎用性の高い副詞です。 | PASS(auto) | B 基本寄り | Y |
| 9 | 単語(call2#3) | masterpiece | 傑作 | A song that's a masterpiece to you may not sound that way to the person beside you | 芸術作品などを「傑作」と評価する際に使える語です。 | PASS(auto) | Y B2名詞 | Y |

### Trial方式 r2 候補全文(P7返答5・W3返答3、call 5、¥1.572)

| 順位 | 区分 | 英語表現(used_form) | 日本語意味 | 出典文 | 選定理由 | Gate | 自判定 | judge |
|---|---|---|---|---|---|---|---|---|
| 1 | フレーズ(call1#1) | blanket ban | 一律の禁止 | The UK has launched a nationwide campaign urging rail passengers to use headphones, not a blanket ban on sound |  | PASS(auto) | Y コロケーション | Y |
| 2 | フレーズ(call1#2) | due to be shared | 伝えられることになっている | The message is due to be shared through posters and announcements at stations and on trains |  | PASS(auto) | B be due toが核。shared付きでやや過剰 | Y |
| 3 | フレーズ(call1#3) | reach for one's wallet | 支払いに備えて財布を出す | That's enough to make you reach for your wallet before the volume button |  | PASS(auto) | Y 定番表現 | Y |
| 4 | フレーズ(call1#4) | written permission | 書面での許可 | There is an exception if the rail company has given written permission |  | PASS(auto) | Y コロケーション | Y |
| 5 | フレーズ(call1#5) | face a fine | 罰金を科される | If you don't follow the rules, you could face a fine of up to £1,000 |  | PASS(auto) | Y コロケーション | Y |
| 6 | 単語(call2#1) | masterpiece | 傑作 | A song that's a masterpiece to you may not sound that way to the person beside you | 作品の傑作を表し、芸術や仕事など幅広い文脈で使えます。 | PASS(auto) | Y B2名詞 | Y |
| 7 | 単語(call2#2) | Uninvited | 望まれていない | Are You Giving That Video an Uninvited Premiere on the Train | 招かれていない、望まれていないことを表す形容詞です。 | PASS(auto) | Y B2形容詞 | Y |
| 8 | 単語(call2#3) | automatically | 自動的に | It doesn't mean everyone who plays something through a speaker automatically gets a £1,000 bill | 人や仕組みが自動的に動くことを表す汎用性の高い副詞です。 | PASS(auto) | B 基本寄り | Y |

## 猿の手 (Z) / Standard (a2)  本文sha256=3b23d5b56b52 語数=439

現行の出所: fresh(DEV実行、Production既定のgenerate_candidates)

| 項目 | 現行方式 | Trial方式 r1 | Trial方式 r2 |
|---|---|---|---|
| 要求件数 | 最大8(3+5) | フレーズ7＋単語3(計10) | フレーズ7＋単語3(計10) |
| AI返答件数 | 6 | P7 6＋W3 3＝9 | P7 7＋W3 3＝10 |
| Gate除外件数 | 1 | 1 {'canonicalization': 1} | 1 {'canonicalization': 1} |
| 最終候補件数 | 5 | 8 | 9 |
| フレーズ件数 | 4 | 5 | 6 |
| 単語件数 | 1 | 3 | 3 |
| 学習価値・多様性(Y/B/N) | 自Y2/B1/N2・judge Y2/B0/N3・両者Y2 | 自Y7/B1/N0・judge Y7/B0/N1・両者Y7 | 自Y6/B2/N1・judge Y6/B0/N3・両者Y6 |
| 生成コスト | 実績 ¥1.731(7 call) | 実績 ¥2.106(7 call) | 実績 ¥2.726(7 call) |

### 現行方式 候補全文

| 順位 | 区分 | 英語表現(used_form) | 日本語意味 | 出典文 | 選定理由 | Gate | 自判定 | judge |
|---|---|---|---|---|---|---|---|---|
| 1 | 単語(call1#1) | sergeant-major | 曹長 | An old friend visited them, a retired sergeant-major from India |  | PASS(auto) | N 軍の階級名で汎用性が低い(R3) | N |
| 2 | フレーズ(call1#3) | break the silence | 静けさを破る | A quiet knock broke the silence |  | PASS(auto) | Y 定番表現 | Y |
| 3 | フレーズ(call2#1) | take hold of | つかむ | White took hold of his wife's hand | 「しっかりつかむ」を表す慣用的な表現です。 | PASS(auto) | Y 定番表現 | Y |
| 4 | フレーズ(call2#2) | for someone's loss | 誰かが大切な人を亡くしたことへの補償として | The company says it isn't to blame, but offers two hundred pounds for your loss | 死別への弔意や補償を伝える文脈で使われます。 | PASS(auto) | N 切り出しが不自然な断片(R2) | N |
| 5 | フレーズ(call2#3) | rise into the night | 夜に響き渡る | Cold wind blew in as her long cry of loss rose into the night | 声や音が夜へ広がる様子を描く文学的な表現です。 | PASS(auto) | B 描写的で再利用は限定的 | N |
| (除外) | - | pulling free | - | - | - | **canonicalization**: key_phrase('pull free')がdisplay_phraseと一致せず、source_span('pulling free')内の連続部分文字列でもない(人称代名詞・所有格の一般化[閉 | - | - |

### Trial方式 r1 候補全文(P7返答6・W3返答3、call 7、¥2.106)

| 順位 | 区分 | 英語表現(used_form) | 日本語意味 | 出典文 | 選定理由 | Gate | 自判定 | judge |
|---|---|---|---|---|---|---|---|---|
| 1 | フレーズ(call1#1) | back to life | 生き返る | Bring our son back to life |  | PASS(auto) | Y 定番表現 | Y |
| 2 | フレーズ(call1#2) | to blame | 責任がある | The company says it isn't to blame, but offers two hundred pounds for your loss |  | PASS(auto) | Y be to blame の核 | Y |
| 3 | フレーズ(call1#3) | take hold of | つかむ | White took hold of his wife's hand |  | PASS(auto) | Y 定番表現 | Y |
| 4 | フレーズ(call1#5) | break the silence | 静けさを破る | A quiet knock broke the silence |  | PASS(auto) | Y 定番表現 | Y |
| 5 | フレーズ(call1#6) | rise into the night | 夜空へ響き渡る | Cold wind blew in as her long cry of loss rose into the night |  | PASS(auto) | B 描写的で再利用は限定的 | N |
| 6 | 単語(call2#1) | fate | 運命 | But trying to change your fate brings sadness | 運命を表す抽象語で、幅広い文脈で使えます。 | PASS(auto) | Y 汎用名詞 | Y |
| 7 | 単語(call2#2) | twist | ねじれる | The paw twisted in his hand, and he dropped it with a cry | 物理的にねじる意味のほか、比喩的な用法も学べます。 | PASS(auto) | Y 多義の汎用動詞 | Y |
| 8 | 単語(call2#3) | scrape | こすれて音を立てる | The chair scraped, and the last lock began to slide | こすれて音を立てる動作を表す動詞です。 | PASS(auto) | Y B2動詞。汎用 | Y |
| (除外) | - | pulling free | - | - | - | **canonicalization**: key_phrase('pull free')がdisplay_phraseと一致せず、source_span('pulling free')内の連続部分文字列でもない(人称代名詞・所有格の一般化[閉 | - | - |

### Trial方式 r2 候補全文(P7返答7・W3返答3、call 7、¥2.726)

| 順位 | 区分 | 英語表現(used_form) | 日本語意味 | 出典文 | 選定理由 | Gate | 自判定 | judge |
|---|---|---|---|---|---|---|---|---|
| 1 | フレーズ(call1#1) | back to life | 生き返る | Bring our son back to life |  | PASS(auto) | Y 定番表現 | Y |
| 2 | フレーズ(call1#2) | take hold of | つかむ | White took hold of his wife's hand |  | PASS(auto) | Y 定番表現 | Y |
| 3 | フレーズ(call1#3) | blame someone for what happens | 起きることを誰かのせいにする | Burn it, or don't blame me for what happens," his friend warned |  | PASS(auto) | B blame someone for が核。節まで含み過剰 | N |
| 4 | フレーズ(call1#4) | for someone's loss | 誰かの損失を埋め合わせるために | The company says it isn't to blame, but offers two hundred pounds for your loss |  | PASS(auto) | N 切り出しが不自然な断片(R2) | N |
| 5 | フレーズ(call1#5) | break the silence | 静けさを破る | A quiet knock broke the silence |  | PASS(auto) | Y 定番表現 | Y |
| 6 | フレーズ(call1#7) | rise into the night | 夜空に高く響き渡る | Cold wind blew in as her long cry of loss rose into the night |  | PASS(auto) | B 描写的で再利用は限定的 | N |
| 7 | 単語(call2#1) | fate | 運命 | But trying to change your fate brings sadness | 運命を表す抽象語で、幅広い文脈で使える。 | PASS(auto) | Y 汎用名詞 | Y |
| 8 | 単語(call2#2) | twist | ねじれる | The paw twisted in his hand, and he dropped it with a cry | 「ねじる・ひねる」を表し、比喩的にも使える。 | PASS(auto) | Y 多義の汎用動詞 | Y |
| 9 | 単語(call2#3) | scrape | こすれて音を立てる | The chair scraped, and the last lock began to slide | こすれて音を立てる動作を表す動詞。 | PASS(auto) | Y B2動詞。汎用 | Y |
| (除外) | - | pulling free | - | - | - | **canonicalization**: key_phrase('pull free')がdisplay_phraseと一致せず、source_span('pulling free')内の連続部分文字列でもない(人称代名詞・所有格の一般化[閉 | - | - |

## 猿の手 (Z) / Advanced (b1b)  本文sha256=8388280adba4 語数=430

現行の出所: fresh(DEV実行、Production既定のgenerate_candidates)

| 項目 | 現行方式 | Trial方式 r1 | Trial方式 r2 |
|---|---|---|---|
| 要求件数 | 最大8(3+5) | フレーズ7＋単語3(計10) | フレーズ7＋単語3(計10) |
| AI返答件数 | 8 | P7 7＋W3 3＝10 | P7 4＋W3 3＝7 |
| Gate除外件数 | 1 | 2 {'canonicalization': 2} | 0  |
| 最終候補件数 | 7 | 8 | 7 |
| フレーズ件数 | 3 | 5 | 4 |
| 単語件数 | 4 | 3 | 3 |
| 学習価値・多様性(Y/B/N) | 自Y4/B2/N1・judge Y5/B0/N2・両者Y3 | 自Y3/B4/N1・judge Y5/B1/N2・両者Y2 | 自Y3/B4/N0・judge Y6/B0/N1・両者Y3 |
| 生成コスト | 実績 ¥1.767(7 call) | 実績 ¥2.406(7 call) | 実績 ¥1.183(5 call) |

### 現行方式 候補全文

| 順位 | 区分 | 英語表現(used_form) | 日本語意味 | 出典文 | 選定理由 | Gate | 自判定 | judge |
|---|---|---|---|---|---|---|---|---|
| 1 | フレーズ(call1#1) | interfere with fate | 運命に手を加える | It grants three wishes," he said, "but brings sorrow to anyone who interferes with fate |  | PASS(auto) | B interfere withが核。fateは目的語で余剰気味 | Y |
| 2 | フレーズ(call1#3) | wail of loss | 失った悲しみの叫び声 | Cold wind swept into the house, and her long wail of loss rose into the night |  | PASS(auto) | B 描写的でやや記事固有 | Y |
| 3 | フレーズ(call2#1) | pay off | 完済する | Enough to pay off the house | 借金などを完済する意味の句動詞です。 | PASS(auto) | Y 句動詞 | Y |
| 4 | 単語(call2#2) | compensation | 補償金 | The firm accepts no responsibility, but offers you two hundred pounds in compensation | 損害や損失への補償を表す正式な語です。 | PASS(auto) | Y 汎用名詞 | N |
| 5 | 単語(call2#3) | snatch | さっとつかむ | White snatched it out | 急につかみ取る動作を表す力強い動詞です。 | PASS(auto) | Y 動詞 | Y |
| 6 | 単語(call2#4) | rattle | ガタガタ鳴らす | Wind rattled the windows, but the fire burned brightly | 揺らしてガタガタ鳴らす様子を表す動詞です。 | PASS(auto) | Y 動詞 | Y |
| 7 | 単語(call2#5) | sergeant-major | 曹長 | A knock announced an old friend, a retired sergeant-major home from India | 英語圏の軍隊で使われる上級下士官の階級名です。 | PASS(auto) | N 軍の階級名で汎用性が低い | N |
| (除外) | - | accepts no responsibility | - | - | - | **canonicalization**: key_phrase('accept no responsibility')がdisplay_phraseと一致せず、source_span('accepts no responsibility')内 | - | - |

### Trial方式 r1 候補全文(P7返答7・W3返答3、call 7、¥2.406)

| 順位 | 区分 | 英語表現(used_form) | 日本語意味 | 出典文 | 選定理由 | Gate | 自判定 | judge |
|---|---|---|---|---|---|---|---|---|
| 1 | フレーズ(call1#2) | pay off the house | 家のローンを払い終える | Enough to pay off the house |  | PASS(auto) | B pay offが核。目的語が記事固有(R2過剰) | N |
| 2 | フレーズ(call1#3) | interfere with fate | 運命に手を出す | It grants three wishes," he said, "but brings sorrow to anyone who interferes with fate |  | PASS(auto) | B interfere withが核。fateは目的語で余剰気味 | Y |
| 3 | フレーズ(call1#5) | caught in the machinery | 機械に巻き込まれる | Your son was caught in the machinery," he said |  | PASS(auto) | B 記事固有の文脈寄り | Y |
| 4 | フレーズ(call1#6) | wail of loss | 失った悲しみの叫び | Cold wind swept into the house, and her long wail of loss rose into the night |  | PASS(auto) | B 描写的でやや記事固有 | Y |
| 5 | フレーズ(call1#7) | shake one's husband awake | 夫を揺すって起こす | White shook her husband awake |  | PASS(auto) | N 記事固有の断片(R3) | B |
| 6 | 単語(call2#1) | compensation | 補償金 | The firm accepts no responsibility, but offers you two hundred pounds in compensation | 損害への補償を表す、汎用性の高い語です。 | PASS(auto) | Y 汎用名詞 | N |
| 7 | 単語(call2#2) | deserted | 人けのない | The street lamp opposite shone on a quiet, deserted road | 人けのない場所や見捨てられた状態を表せます。 | PASS(auto) | Y 形容詞。汎用 | Y |
| 8 | 単語(call2#3) | burial | 墓に納めること | A week after the burial, Mrs | 埋葬を意味し、葬儀や死を扱う文脈で役立ちます。 | PASS(auto) | Y B2名詞 | Y |
| (除外) | - | accepts no responsibility | - | - | - | **canonicalization**: key_phrase('accept no responsibility')がdisplay_phraseと一致せず、source_span('accepts no responsibility')内 | - | - |
| (除外) | - | pulled free | - | - | - | **canonicalization**: key_phrase('pull free')がdisplay_phraseと一致せず、source_span('pulled free')内の連続部分文字列でもない(人称代名詞・所有格の一般化[閉じ | - | - |

### Trial方式 r2 候補全文(P7返答4・W3返答3、call 5、¥1.183)

| 順位 | 区分 | 英語表現(used_form) | 日本語意味 | 出典文 | 選定理由 | Gate | 自判定 | judge |
|---|---|---|---|---|---|---|---|---|
| 1 | フレーズ(call1#1) | interfere with fate | 運命に逆らう | It grants three wishes," he said, "but brings sorrow to anyone who interferes with fate |  | PASS(auto) | B interfere withが核。fateは目的語で余剰気味 | Y |
| 2 | フレーズ(call1#2) | pay off | 完済する | Enough to pay off the house |  | PASS(auto) | Y 句動詞 | Y |
| 3 | フレーズ(call1#3) | in compensation | 補償として | The firm accepts no responsibility, but offers you two hundred pounds in compensation |  | PASS(auto) | B compensationと重複する学習点(R5)で前置詞付きは弱い | Y |
| 4 | フレーズ(call1#4) | wail of loss | 失ったものを嘆く叫び | Cold wind swept into the house, and her long wail of loss rose into the night |  | PASS(auto) | B 描写的でやや記事固有 | Y |
| 5 | 単語(call2#1) | responsibility | 責任 | The firm accepts no responsibility, but offers you two hundred pounds in compensation | 責任を表す汎用性の高い重要語です。 | PASS(auto) | B 基本寄り | N |
| 6 | 単語(call2#2) | snatch | さっとつかみ取る | White snatched it out | 素早く奪い取る動作を表す動詞です。 | PASS(auto) | Y 動詞 | Y |
| 7 | 単語(call2#3) | deserted | 人けのない | The street lamp opposite shone on a quiet, deserted road | 人けのない状態を表す形容詞です。 | PASS(auto) | Y 形容詞。汎用 | Y |

