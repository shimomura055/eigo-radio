# DESIGN_01 (委任_28: 再配達 構成・原稿改善Trial の設計。DEV/Trial専用)

作成: 2026-10-25。実装=`er110_family_y_redelivery_revision_01.py`(新module)+`er110_family_y_redelivery_revision_01_test_01.py`。**従来版`er110_family_y_redelivery_audio_01.py`(委任_27)は無変更**で、既定は従来挙動。本moduleは明示的にサブコマンドを実行したときだけ新工程を動かす(Trial比較のための併存)。Production file変更0。

## 1. 既存仕様との照合(照合したファイル:行)
- Y承認済み設計: `OPINION_BASED_02/PERSONAS_05.md`・`THEME_DEFINITION_02.md` §1〜3・`THEME_DATA_02.json`(sheets.*.role_ja/daily_life_ja/identity_cue_ja)。人物像・Voice本文は無変更(R0: `er110_output/family_y_opinion_based_03/redelivery_fee/run_01/article_ja.md`、`rr.load_r0()`でGate PASS・byte一致を実行時に検査)。
- 5パート契約: `er110_family_y_text_trial_01.py:115 check_contract`(段落内改行禁止)→ Voiceパートは『紹介1行+本人の語り』の2行構成になるため、本moduleの`parse_revised/check_revised/mapping_check_revised`で別に検査(従来のcheck_contractは従来版の検査として無変更)。
- 従来のLead/Tension生成: `er110_family_y_redelivery_audio_01.py` `LEAD_TMPL`(約70〜100字・開示文後置)、`er110_family_y_persona_text_trial_01.py:437 TENSION_DEVELOPER/TENSION_RULES`(約200〜240字・結論/教訓/解決策なし・具体的な問い)、`run_gate`(Leakage判定→局所書き換え→再判定、最大3判定)。
- 音声: `er110_family_y_audio_trial_01.py:44-50 Y_BODY`(lead=Aoede、Voice 1〜3=Algieba/Zephyr/Schedar、final=Aoede。levelに依らない)、同:487-498(Adv補助=Charon: Welcome/Topic/Preview/KP intro/Full story intro/Outro)。Z: `er062_family_z_structure_01.py:47-48`(Narrator=Aoede、Adv補助=Charon)。
- UDR #170/#172/#175/#176、OPEN-463/484(Y正式Production入口なし)との矛盾なし(DEV専用、`production_reachable=False`)。

## 2. 工程変更(従来版との差分)
| # | 変更 | 実装 | 従来版 |
|---|---|---|---|
| ① | 人物紹介ナレーション(新stage `intro`) | `INTRO_TMPL`/`generate_intros`: 3本を**1 call**(JSON strict)。入力=THEME_DATA_02の`role_ja/daily_life_ja/identity_cue_ja`+Voice本文(読み取り専用)。決定論検査`check_intro`: 一人称なし/です・ます調なし/数字なし/AI編集語なし/先取り語(有料・賛成・反対・請求・払う・料金)なし/人物の役割語あり/紹介文の具体物は**本人の語りに出るものだけ**/本人の語りと10字連続一致なし/32〜62字 | なし |
| ② | AI編集アナウンス廃止+Lead再生成 | `LEAD_TMPL`: 開示文を書かせず、テーマの範囲(`SCOPE_LINES`=THEME_DEFINITION_02 §1〜2の転記。再配達の定義・有料化の幅・関係する話題・争点)の中の情報1〜2つと問題提起1つ、最後に三人の予告。`check_lead`: 115〜160字、AI編集語なし、数字なし、予告あり。`rr.DISCLOSURE_JA`は組立に使わない(`check_revised`が旧開示文の混入を検出) | リード約88字+開示文54字 |
| ③ | In One Line廃止(Yのみ) | 本moduleの原稿・音声計画に`in_one_line`を持たない(`check_revised`が`In one line/ひとこと`を検出、`revised_segment_plan`にsegmentなし)。X/Zの生成・組立コード(`efam._advanced_in_one_line`等)は本moduleから呼ばず、変更もしない。英訳段階の`rr.cmd_english`はIn One Lineを生成するため、**英訳時は新moduleの英訳stageを追加する**(今回は対象外)。 | 英訳・音声・ページにあり |
| ④ | Tension+Closing抜本改善 | `ANGLES`(切り口パラメータ: 名称・狙い・brief)+`CLOSING_RULES`(骨格: 3人の語りを1文受ける[省略可]→切り口に沿った新しい見方2〜3文→切り口から導く具体的な問い。『立場によって違う』型の結論禁止、仮定は問いの形のみ、新事実禁止)+案ごとに**1 call**。`check_closing`: 175〜245字・「？」終わり・当然の結論の定型句なし・一人称なし・AI編集語なし・数字なし・1文55字以内。Gate: 既存`p.run_gate(kind="tension")`(判定→局所書き換え→再判定)。局所書き換えPromptには**切り口を付加**(切り口が書き換えで失われるのを防ぐ。process内patch、finallyで復元、`p`のファイルは無変更) | 約200〜240字・切り口なし |
| 注意書き | ページ側に掲載 | `PAGE_NOTICE_JA`(定数)。ページ実装は次の段階(試聴ページ・記事ページの本文外) | なし |

### Closing切り口の考案方針
事前固定をしない: 3人の本文とTHEME_DATA_02の`contradiction_or_weakness_ja`・`wishes_honest_ja`を分析し、互いに言い換えにならない3つの『着眼の軸』(言葉・仕組み・人の見方)を選んだ。分析と見送った案は`EVAL_01.md` §1。

## 3. 分量目標(委任_27実測 → 本Trial目標)
| パート | 前回 字数(比率) | 本Trial目標 |
|---|---|---|
| Lead | 142(12.5%)[本体88+開示54] | 115〜160字(開示文を消した分を問題提起で補う) |
| Voice 1/2/3 | 260/260/273(22.9/22.9/24.0%) | **本文は無変更**+紹介32〜62字(各約35〜40字を目標) |
| Closing | 202(17.8%) | 175〜245字(約200字) |
| 計 | 1,137字(Std音声約5:21、Adv約5:43) | 約1,240〜1,260字(+9〜11%、音声+約30秒の見込み) |

## 4. 費用見積(gpt-6.1-sol=既存正式構成・最新世代、既定effort=high不変)
前回実績: sol 1 callあたり1.1〜9.4円(Tensionは出力5.5k tokenで9.37円)。見積: Lead 1〜2円+人物紹介(1 call)3〜5円+Closing 3案(各4〜8円)+Gate判定(luna、各0.05〜0.6円)+Lead/紹介の補助判定0.2円=**期待22〜30円、最大38円**。個別上限40円。再生成・Gate書き換えが重なる最悪ケースでもguard(各stage後・Closing前に実費>Capで停止)で40円を超えない。日次: 着手時862.38円+最大40円=902円<1,000円で事前確認済み。

## 5. test計画(API 0)
`er110_family_y_redelivery_revision_01_test_01.py`:
- 隔離: 非er110_family_y_*のpyから参照0、`os.environ/getenv`なし、`--paid`なしでcmd_genが副作用0のまま例外、承認ファイルなしで例外、従来版のコマンド集合・開示文定数が無変更、patch後に`p.TENSION_RULES/COMMON_PREMISE_JA/y0.THEME_TAG/p.build_tension_rewrite_prompt`が復元される。
- 他Family不変: 本moduleのソースに`_advanced_in_one_line/fx_iol/efam`がない(In One Line廃止はY新moduleの原稿・音声計画側のみ。X/Z関数は無変更・非呼出)。
- 5パート対応検査の拡張(`mapping_check_revised`): Voiceパートの紹介行=ナレーター(一人称なし)・本人行=一人称+話者アンカー、Voice取り違えの検出、リード/Closingがナレーター。
- 組立: Voice本文byte一致、In One Line検出、旧開示文検出、AI編集語検出。分量表。音声計画: lead→紹介→Voice→…→closingの順、In One Lineなし、ナレーター=既存`Y_VOICE_OF`から導出(Aoede直書きなし)、Voice 1〜3=Algieba/Zephyr/Schedar、両level。
- 検査器: 旧開示文のLead混入、紹介の先取り語・役割語欠落・他人物の具体物・本文写し、Closingの定型結論句・非疑問終わり。
