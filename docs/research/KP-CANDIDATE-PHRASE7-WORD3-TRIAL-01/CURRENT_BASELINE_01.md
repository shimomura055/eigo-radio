# CURRENT_BASELINE_01 (現行Production方式の候補一覧。KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01)

現行方式 = Production既定 `er119_kp_candidates_01.generate_candidates`(call1=Prompt 2で3件 + call2=Prompt 2-Vで最大5件 = 要求最大8件)。
単語/フレーズ判定基準(事前固定): `used_form` が空白を含まない1トークン(ハイフン複合語を含む)=単語、空白区切りの2語以上=フレーズ(句動詞・空白区切り複合名詞もフレーズ)。

## 使用run・本文・sha256

| 記事 | Family | level | 本文ファイル | 本文sha256(先頭12) | 本文=Production selector promptの本文 | 現行候補の出所 |
|---|---|---|---|---|---|---|
| AIの仮想の島 | X | a2(Standard) | er019_output/ai_island_temple/run_ai_01/a2/article.md (正式run: er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_ai_01) | 76f80f62120b | True | reuse(既存kp_candidates.json) |
| AIの仮想の島 | X | b1b(Advanced) | er019_output/ai_island_temple/run_ai_01/b1b/article.md (正式run: er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_ai_01) | 00f14092c072 | True | reuse(既存kp_candidates.json) |
| 英国の電車マナー | X | a2(Standard) | er019_output/uk_train_speaker_playback/run_nws_02/a2/article.md (正式run: .../uk_train_speaker_playback__run_nws_02) | 3d17265a2887 | True | NO_EXISTING_8CAND_RUN(現行方式のfresh再実行が必要) |
| 英国の電車マナー | X | b1b(Advanced) | er019_output/uk_train_speaker_playback/run_nws_02/b1b/article.md (正式run: .../uk_train_speaker_playback__run_nws_02) | 4bd94d783355 | True | NO_EXISTING_8CAND_RUN(現行方式のfresh再実行が必要) |
| 猿の手 | Z | a2(Standard) | er026_output/family_z_production_e2e_01/the_monkeys_paw/run_sf_prod_01/writer/std.md を canonical_article_text 化 (CLOSED_USER_PASS。a2=std.md / b1b=r2.md) | 3b23d5b56b52 | True | NO_EXISTING_8CAND_RUN(現行方式のfresh再実行が必要) |
| 猿の手 | Z | b1b(Advanced) | er026_output/family_z_production_e2e_01/the_monkeys_paw/run_sf_prod_01/writer/r2.md を canonical_article_text 化 (CLOSED_USER_PASS。a2=std.md / b1b=r2.md) | 8388280adba4 | True | NO_EXISTING_8CAND_RUN(現行方式のfresh再実行が必要) |

注: 英国電車マナー・猿の手には『8候補方式(KP Human Review導入後)』の既存候補成果物が存在しない(両者とも正式runは3KP時代の `keywords_canonicalized.json`)ため、現行方式の候補は同一本文に対して Production既定の `generate_candidates` をDEV出力dirで1回実行して取得した(fresh。費用は下表)。AI島のみ既存 `kp_candidates.json` を再利用。run_fzcw_e1_01(STOP残置)は不使用。

## レベル別の現行方式実績

### AIの仮想の島 / Standard (a2)
- 出所: 既存再利用(`er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_ai_01/a2/key_phrases/kp_candidates.json`)。要求最大8、AI返答=7、Gate除外=2、最終=5(フレーズ5・単語0)。費用=この成果物単体の記録なし(fresh現行平均から推計)。

| 順位 | 区分 | 英語表現 | 日本語意味 | 出典文 | 選定理由 | origin |
|---|---|---|---|---|---|---|
| 1 | フレーズ | carry over | 持ち越す | But the work area with the AI's notes and programs carried over to the next hour |  | call1#1 |
| 2 | フレーズ | worth paying attention to | 注目する価値がある | One tip in the strategy notes was worth paying attention to |  | call1#2 |
| 3 | フレーズ | a useful card to play | 使える手札 | A discovery that is not useful now might be a useful card to play next time, if it is saved |  | call1#3 |
| 4 | フレーズ | take a detour | 遠回りをする | Those that had taken a detour were now one step ahead | 本来の道筋から外れることを比喩的に表す。 | call2#1 |
| 5 | フレーズ | one step ahead | 一歩先を行っている | Those that had taken a detour were now one step ahead | 一歩先を行く、優位に立つという定番の比喩表現。 | call2#2 |
| (除外) | - | too soon to wave a flag | - | - | **validate**: 語数が1〜5語でない(実際: 6語) | call2 |
| (除外) | - | studied separately | - | - | **canonicalization**: key_phrase('study separately')がdisplay_phraseと一致せず、source_span('studied separately')内の連続部分文字列でもない(人称代名詞・所有格の一般 | call2 |

### AIの仮想の島 / Advanced (b1b)
- 出所: 既存再利用(`er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_ai_01/b1b/key_phrases/kp_candidates.json`)。要求最大8、AI返答=7、Gate除外=0、最終=7(フレーズ7・単語0)。費用=この成果物単体の記録なし(fresh現行平均から推計)。

| 順位 | 区分 | 英語表現 | 日本語意味 | 出典文 | 選定理由 | origin |
|---|---|---|---|---|---|---|
| 1 | フレーズ | carry over | 次に持ち越す | In the experiment, the island and the conversation were reset every hour, but the work area where the AI kept notes and programs was carried over |  | call1#1 |
| 2 | フレーズ | call on | 頼まれる | So, would that experience help the AI the next time it was called on |  | call1#2 |
| 3 | フレーズ | look at separately | 分けて考える | The fact that the experienced group did better and the fact that removing a particular memory lowered its score need to be looked at separately |  | call1#3 |
| 4 | フレーズ | one step ahead | 一歩先を行く | The ones that had taken a detour were now one step ahead | 「一歩先を行く」という優位性を表す定番表現。 | call2#1 |
| 5 | フレーズ | card to play | 使える手 | A discovery that is no use right now might become a useful card to play next time, if it is saved | 「切れるカード・有効な手段」という比喩表現。 | call2#2 |
| 6 | フレーズ | take a detour | 寄り道をする | The ones that had taken a detour were now one step ahead | 本筋を外れて別の経験をする比喩的な表現。 | call2#3 |
| 7 | フレーズ | no use right now | 今は役に立たない | A discovery that is no use right now might become a useful card to play next time, if it is saved | 「今は役に立たない」を表す自然な言い回し。 | call2#4 |

### 英国の電車マナー / Standard (a2)
- 出所: fresh(`docs/research/KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01/runs/uk_train_speaker_playback__a2__current__r1/`)。要求最大8、AI返答=7、Gate除外=1、最終=6(フレーズ6・単語0)。実費=¥1.315(5 call)。
- 参考(正式runの確定3KP): sound no one asked for(誰も望んでいない音) / reach for one's wallet(自分の財布に手を伸ばす) / draw a line(一線を引く)

| 順位 | 区分 | 英語表現 | 日本語意味 | 出典文 | 選定理由 | origin |
|---|---|---|---|---|---|---|
| 1 | フレーズ | point to current rail rules | 今ある鉄道のルールを引き合いに出す | The campaign points to current rail rules and asks people to think about others |  | call1#1 |
| 2 | フレーズ | written permission | 書面での許可 | There is an exception when the train company has given written permission |  | call1#2 |
| 3 | フレーズ | draw a line | 境界線を引く | The words draw that line simply |  | call1#3 |
| 4 | フレーズ | put on an unwanted show | 見たくない人に見せ物を押しつける | Is Your Video Putting on an Unwanted Show on the Train | 「見せ物を演じる」という比喩的な用法が学べる。 | call2#1 |
| 5 | フレーズ | sound no one asked for | 誰も求めていない音 | Here's news about this kind of "sound no one asked for | 頼んでもいない騒音を皮肉っぽく表す口語表現。 | call2#2 |
| 6 | フレーズ | reach for one's wallet | 自分の財布を取ろうと手を伸ばす | That's enough to make you reach for your wallet before the volume button | 出費を覚悟することを表す慣用的な言い回し。 | call2#3 |
| (除外) | - | up to £1,000 | - | - | **validate**: 数字を含む(数値placeholder型の回避: 数値を補わないと成立しない形/音声化で不安定になる形は選ばない) | call2 |

### 英国の電車マナー / Advanced (b1b)
- 出所: fresh(`docs/research/KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01/runs/uk_train_speaker_playback__b1b__current__r1/`)。要求最大8、AI返答=8、Gate除外=0、最終=8(フレーズ8・単語0)。実費=¥1.577(5 call)。
- 参考(正式runの確定3KP): a blanket ban(全面的な禁止) / reach for one's wallet(お金を払おうとする) / draw a line(境目をはっきりさせる)

| 順位 | 区分 | 英語表現 | 日本語意味 | 出典文 | 選定理由 | origin |
|---|---|---|---|---|---|---|
| 1 | フレーズ | blanket ban | 全面的な禁止 | The UK has launched a nationwide campaign urging rail passengers to use headphones, not a blanket ban on sound |  | call1#1 |
| 2 | フレーズ | reach for one's wallet | 自分の財布に手を伸ばす | That's enough to make you reach for your wallet before the volume button |  | call1#2 |
| 3 | フレーズ | draw a line | 線を引く | The words draw that line simply |  | call1#3 |
| 4 | フレーズ | be covered | 規則の対象になる | A smartphone speaker can also be covered, if the situation meets the rules | 規則や制度の適用対象になることを表す。 | call2#1 |
| 5 | フレーズ | due to be shared | 伝えられる予定だ | The message is due to be shared through posters and announcements at stations and on trains | 予定を表す「be due to」の受動態の形。 | call2#2 |
| 6 | フレーズ | face a fine | 罰金を科される | If you don't follow the rules, you could face a fine of up to £1,000 | 罰金を科される可能性に直面する表現。 | call2#3 |
| 7 | フレーズ | written permission | 書面での許可 | There is an exception if the rail company has given written permission | 正式な許可を表す定型的な組み合わせ。 | call2#4 |
| 8 | フレーズ | up to | 最大で | If you don't follow the rules, you could face a fine of up to £1,000 | 金額などの上限を示す表現。 | call2#5 |

### 猿の手 / Standard (a2)
- 出所: fresh(`docs/research/KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01/runs/monkeys_paw__a2__current__r1/`)。要求最大8、AI返答=6、Gate除外=1、最終=5(フレーズ4・単語1)。実費=¥1.731(7 call)。
- 参考(正式runの確定3KP): sergeant-major(曹長) / take hold of(～をつかむ) / rise into the night(夜の中へと響き渡る)

| 順位 | 区分 | 英語表現 | 日本語意味 | 出典文 | 選定理由 | origin |
|---|---|---|---|---|---|---|
| 1 | 単語 | sergeant-major | 曹長 | An old friend visited them, a retired sergeant-major from India |  | call1#1 |
| 2 | フレーズ | break the silence | 静けさを破る | A quiet knock broke the silence |  | call1#3 |
| 3 | フレーズ | take hold of | つかむ | White took hold of his wife's hand | 「しっかりつかむ」を表す慣用的な表現です。 | call2#1 |
| 4 | フレーズ | for someone's loss | 誰かが大切な人を亡くしたことへの補償として | The company says it isn't to blame, but offers two hundred pounds for your loss | 死別への弔意や補償を伝える文脈で使われます。 | call2#2 |
| 5 | フレーズ | rise into the night | 夜に響き渡る | Cold wind blew in as her long cry of loss rose into the night | 声や音が夜へ広がる様子を描く文学的な表現です。 | call2#3 |
| (除外) | - | pulling free | - | - | **canonicalization**: key_phrase('pull free')がdisplay_phraseと一致せず、source_span('pulling free')内の連続部分文字列でもない(人称代名詞・所有格の一般化[閉じた語彙集合による1 | call1 |

### 猿の手 / Advanced (b1b)
- 出所: fresh(`docs/research/KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01/runs/monkeys_paw__b1b__current__r1/`)。要求最大8、AI返答=8、Gate除外=1、最終=7(フレーズ3・単語4)。実費=¥1.767(7 call)。
- 参考(正式runの確定3KP): interfere with fate(運命に干渉する) / in compensation(補償として) / wail of loss(失った悲しみの叫び)

| 順位 | 区分 | 英語表現 | 日本語意味 | 出典文 | 選定理由 | origin |
|---|---|---|---|---|---|---|
| 1 | フレーズ | interfere with fate | 運命に手を加える | It grants three wishes," he said, "but brings sorrow to anyone who interferes with fate |  | call1#1 |
| 2 | フレーズ | wail of loss | 失った悲しみの叫び声 | Cold wind swept into the house, and her long wail of loss rose into the night |  | call1#3 |
| 3 | フレーズ | pay off | 完済する | Enough to pay off the house | 借金などを完済する意味の句動詞です。 | call2#1 |
| 4 | 単語 | compensation | 補償金 | The firm accepts no responsibility, but offers you two hundred pounds in compensation | 損害や損失への補償を表す正式な語です。 | call2#2 |
| 5 | 単語 | snatch | さっとつかむ | White snatched it out | 急につかみ取る動作を表す力強い動詞です。 | call2#3 |
| 6 | 単語 | rattle | ガタガタ鳴らす | Wind rattled the windows, but the fire burned brightly | 揺らしてガタガタ鳴らす様子を表す動詞です。 | call2#4 |
| 7 | 単語 | sergeant-major | 曹長 | A knock announced an old friend, a retired sergeant-major home from India | 英語圏の軍隊で使われる上級下士官の階級名です。 | call2#5 |
| (除外) | - | accepts no responsibility | - | - | **canonicalization**: key_phrase('accept no responsibility')がdisplay_phraseと一致せず、source_span('accepts no responsibility')内の連続部分文字列でも | call1 |

