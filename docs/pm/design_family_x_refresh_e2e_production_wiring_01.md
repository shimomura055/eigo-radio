# design_family_x_refresh_e2e_production_wiring_01.md

管理ID: `FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01`(Phase A、委任`_01`)
作成: Sonnet。**本Phase Aではコード・Prompt・SSOT・Master Store・出力
ディレクトリを一切変更していない(設計書のみ、API支出¥0、Grep/Read/
read-onlyハッシュ確認のみ実施)。**

## 0. ユーザー指示(原文要旨、委任文より逐語転記)

目的: 直近で正式採用したFamily Xの記事構造・Key Phrase・音声仕様を、
Trial用scriptの寄せ集めではなくProduction正式経路へすべて配線し、その
正式経路だけでHormuz/Metaの2記事を完成音声までE2E再構築する。新しい
改善Trialではない。

最初に: CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS/REPORT/Production codeを
確認し、各仕様について「既にPRODUCTION_WIRED/APPROVED_FOR_PRODUCTIONだが
未配線/旧仕様が残存/Trial専用scriptにしか存在しない」の対応表を作る。
Standard/Advanced共通仕様なのに片方だけに反映されている非対称を確認。

1. 記事入力: Hormuz/Metaの既存AN3-T0最終R2を再利用(再生成しない)。
   使用前に「正しいAN3-T0成果物か/R1/R2 reminderなしで生成された
   Trial-02条件と整合するか/Fact Check済みの最終R2か/artifact・hash・
   由来が特定できるか」を確認。特定不能なら代替生成せずSTOP報告。
2. 新記事構造(APPROVED_FOR_PRODUCTION): 途中Heading廃止/完成JA R2を
   忠実英訳(再構成・脚色なし、段落構造維持)/英訳後に本文を書き換えず
   自然な段落境界でbody1/2/3へ3分割(均等化のための書き換え禁止)/
   完成音声構造Comment1→body1→Comment2→body2→Comment3→body3→
   Comment4→In One Line/既存Heading Readoutを撤去/In One Lineは短い
   自然な一文(Trialの語数目標をそのまま絶対上限にしない)/既存の
   Deviation Check→MAJOR時must-fix retry1回を維持(新設ではない)。
3. OPEN-228: 新構造配線完了時点で旧Heading依存split・intro 2 paragraph
   前提・旧structure gate/retryを確認し、不要になったものを撤去・置換
   → OPEN-228=CLOSED/SUPERSEDED(履歴は残す)。OPEN-230のmust-fix retry
   論点も整合。
4. AN3-T0: AN3はOriginal側のみ、reminderは削除済み。normal R1/R2・
   Fact Check must-fix・symbol must-fix・fallbackのどこにも復活して
   いないことを再確認。E2E完走後にGate 3を満たせばPRODUCTION_WIRED
   判定対象。
5. Advanced Key Phrase英語解説: text仕様=既承認、Audio Style=**Trial-04
   Variant B**(`clear, precise, at a measured pace, without dragging`)、
   APPROVED_FOR_PRODUCTION。Trial scriptに依存せずProduction正式Key
   Phrase経路へ配線。Standard/Advancedの対象範囲を確認し、レベル固有で
   ない部分に非対称を作らない。
6. 固定フレーズMaster Champion(10 phrase決定済み): welcome=A、
   preview_intro=C、key_phrases_intro=C、full_story_intro=C、num_one=C、
   num_two=B、num_three=B/take1、num_four=C、num_five=B/take1、
   point_explanation=B。Three/Fiveのtake1はASR合格素材。再Trialしない。
   Production Master Storeへ正式登録しStandard/Advanced双方の正式経路で
   使用。model/voice不変(Flash-Lite/Charon系統)。
7. Variable Role Style: JA=J3(逐語「落ち着いた、自然な話し言葉で。意味の
   流れ・強調点・転換に応じて表情豊かに抑揚をつけてください。演技がかった
   話し方は避けてください。」)、EN=E2(Trialの Role別E2逐語)。
   APPROVED_FOR_PRODUCTION。**Japanese TitleもJ3系統へ統一**(Trial設計
   漏れ、追加Trial不要。Japanese Titleだけ旧長文JAPANESE_STYLE_PREFIXを
   残さない)。
8. Standard/Advanced整合: 6-role英語Styleは共通/Standard固有のslower
   instruction・6%slowdownは維持/固定Masterは両レベル共通/新記事構造・
   Heading廃止も両レベル共通/Full Story E2はpart1/2/3すべて同じRole
   解決/retry・fallback・Local RewriteでもRole Styleが矛盾しない。J3は
   日本語segmentの仕様であり、Advancedに同じ日本語segmentが無ければ
   無理に適用しない。
9. Opus L2指摘の是正(既報MAJOR): runtime evidence(TOPIC_INTRO/
   FULL_STORY/IN_ONE_LINE等の実style文字列・model_id・voiceをProduction
   経路で記録、Advanced英語経路含む)/cache(可変Role Styleのversionを
   使い、現行正式Styleとcache生成時Styleが不一致ならreuseしない。
   共有層を不必要に変更しない)/Japanese TitleのJ3統一。
10. E2E: すべて配線後、Hormuz/MetaをProduction正式pathだけで完成音声
    まで生成。Trial outputを完成品としてコピーしない。正式に再利用可能な
    ものはreuse可(source hash/model/voice/Style version/Master
    version/canonical textが現行正式仕様と一致することを確認)。
11. 完成確認: 両記事・両レベルで記事/Preview/Comment1〜4/body1/2/3/
    In One Line/Key Phrase/Advanced英語解説/固定Master phrase/Japanese
    Title/TTS/retry・fallback/Assembly/Audio Validation/player・試聴
    ページ。完成PodcastとしてStandard/Advancedの完成版を試聴可能にする。
12. Cost管理: A.開発・検証の一回限り費用とB.Production量産時の継続
    コストを分離して報告。E2E前に概算、完了後に実測。
13. Production Wiring Gate(すべて満たすまでPRODUCTION_WIREDとしない):
    初回path/retry/fallback/regeneration/Local Rewrite/cache/Master
    Store/Standard・Advanced整合/runtime evidence/actual model・voice・
    Style/Regression・integration test/Hormuz・MetaのE2E実発火/
    CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS/REPORT_LEDGER/commit・push/
    OPEN-228 close/approved仕様と実挙動の一致。
14. STOP条件: 承認済み仕様同士の矛盾/新しいProduct判断が必要/未承認
    Prompt変更が必要/既存Production機構では新構造を安全に実現できない/
    Hormuz・Metaの再利用すべき日本語R2が一意に特定できない/Standard・
    Advancedに意図しない非対称/共有TTS層への新しい意味変更が必要/予算
    Guardrail超過見込み。技術的に一意に直せる実装不備は既存承認仕様に
    沿って是正してよい。

Closeout項目: 1 各採用仕様のAPPROVED→WIRED状況 2 Hormuz/Meta×
Standard/Advanced完成状況 3 再利用/新規artifact 4 runtime evidence
5 regression/integration 6 一回限り費用 7 量産コスト増減 8 CLOSEDした
Open Item 9 残存USER_DECISION_REQUIRED 10 残存APPROVED but not WIRED。

---

## 1. 対応表(仕様ごとのStatus・所在・配線先・対称性・Opus L2要否)

| # | 仕様 | Status(現状) | 現在の所在 | 配線先(想定) | Standard/Advanced対称性 | Opus L2要否(共有層か) |
|---|---|---|---|---|---|---|
| 2 | 新記事構造(Heading廃止・忠実英訳・決定論3分割・Comment→body配置・In One Line簡潔化) | **APPROVED_FOR_PRODUCTION(本委任で確定)**。SSOT未反映(`OPEN_ITEMS.md` OPEN-228行の2026-09-28追記は「採用判断はユーザー判断待ち」のままで、本委任文の指示がその判断そのもの)。実証はText-onlyのTrial(`FAMILY-X-TRANSLATION-SEGMENTATION-NO-HEADING-TRIAL-01`、Hormuz初回PASS・Metaはmust-fix retry1回でLEDGER_COMPLIANT) | Trial script`er045_family_x_no_heading_segmentation_trial_01.py`のみ。Production `er003_v1_n3_01_advanced_adaptation_generate.py`(`ADVANCED_ARM3_BLOCK`/`ADVANCED_CONTRACT_SUFFIX_LINES`/`ADVANCED_SECTION_BOUNDARY_CONTRACT`)は旧Heading生成Prompt、`er003_v1_n3_01_scaffold_generate.py::split_article_text()`(L107-162)と`er019_family_x_audio_plan_01.py::split_family_x_article_text()`(L72-133)は旧`###×2`必須split(いずれも見出し前提、retry無しRuntimeError=OPEN-228のクラッシュ原因) | Production未配線 | 両scaffold関数ともStandard(A2)/Advanced(B1B)双方から呼ばれており(`er012_e_family_entertainment_two_level_runner_01.py` L351/419、`er019_family_x_audio_plan_01.py`)、**現状は対称に旧仕様**。新構造も両レベル共通で配線する必要がある(非対称なし、対称性維持が設計要件) | 要(Family X専用実装だがAdvanced化Prompt定数はFamily X専用モジュールであり他Family非共有。ただし`split_article_text`の汎用ロジック[累積語数diff最小化]はFamily A由来の考え方を流用するため、Family A側へ影響しないことの確認が必要) |
| 3 | OPEN-228(旧split無retryクラッシュ)/OPEN-230(must-fix retry欠如) | OPEN(是正待ち) | `OPEN_ITEMS.md` OPEN-228行・OPEN-230行 | #2の新構造配線と同時に、旧split関数の呼び出し撤去+新構造用Deviation Check must-fix retry1回を実装した時点でCLOSED/SUPERSEDED | 対称(両レベル影響) | 上記#2に従属 |
| 4 | AN3-T0(Concreteness Control、Original側のみ、reminder削除済み) | `PRODUCTION_WIRED`候補(`APPROVED_FOR_PRODUCTION`、配線完了・Fable Gate 3判定待ち、reminder削除commit`54739a9d`で現行コードから完全撤去確認済み) | `er019_family_x_ja_writer_o_r1_r2_01.py`(`CONCRETENESS_CONTROL_AN3_BLOCK`、`build_original_prompt()`)。`REMINDER`文字列はgrep 0件で確認済み(現行コード) | 配線済み(再確認のみ、変更不要) | Original Writerは両レベル共通の入力(JA記事は1本、Standard/Advanced共有) | 不要(既にGate 3判定待ちのみ、本タスクでは変更なし) |
| 5 | Advanced Key Phrase英語解説(text仕様B候補+Trial-04 Variant B style) | text仕様=`APPROVED_FOR_PRODUCTION`(配線未実施、`OPEN-221`)。Audio Style=**本委任でVariant B(`clear, precise, at a measured pace, without dragging`)がAPPROVED_FOR_PRODUCTIONへ確定**(SSOT/REPORT_LEDGER上は`KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-04`はまだ`USER_DECISION_REQUIRED`のまま、本委任文の指示がその判断そのもの) | text: `er041_key_phrase_advanced_english_explanation_trial_02.py`。Style: `er046_key_phrase_advanced_english_explanation_audio_style_trial_04.py`(Variant B、voice=Aoede、model=gemini-3.8-flash-lite-tts) | 新Role`KEY_PHRASE_EXPLANATION_EN`未実装。既存`generate_key_phrase_component_verified()`(`er003_v1_repro01_main_generate.py` L730、Aoede+Flash-Lite指定時)と対称の呼び出しを新設し、Assemblyの`_generate_key_phrase_segments_b1`(B1Bのみ)へ解説音声segmentを追加する設計 | **Advanced専用が正しい(非対称ではない)**。CURRENT_SPEC節見出し自体が「Advanced Key Phrase英語解説」であり、Standard(A2)はCEFR上JA直接意味のみで完結する設計(意図的な非対称、Product判断済み) | 要(既存`japanese_gloss`/`japanese_gloss_tts`と並ぶ新フィールド追加、Assembly順序[Phrase EN→解説EN→JA意味の順かは既存CURRENT_SPECのAdvanced KP構造未記載でSTOP候補、§6参照]) |
| 6 | 固定フレーズMaster Champion(10 phrase) | 8 phrase`APPROVED_FOR_PRODUCTION`(CURRENT_SPEC L1616記載、未配線)。**num_three/num_five=B-take1は本委任で確定**(SSOT上は`TTS-FIXED-SHELL-NUMBER-THREE-FIVE-RETRIAL-01`がREPORT_LEDGER上`USER_DECISION_REQUIRED`のまま、本委任文の指示がその判断そのもの。runtime上B-take1はASR合格実測済み、`er047_output/.../num_three_styleB/take1/`・`num_five_styleB/take1/`) | `er006_output/master_audio_store_01/manifest.json`(現行Production、welcome以外9件は旧style)。Champion候補音声は`er043_output/tts_fixed_shell_master_champion_trial_02/`・`er047_output/tts_fixed_shell_number_three_five_retrial_01/`(Trial Store隔離) | Production Master Store `register()`(`er006_master_audio_store_01.py`)で、welcome以外9 phraseの`style_instruction_id`/`style_instruction_version`をChampion採用値へ更新(`MasterAudioKey.EQUALITY_FIELDS`に両フィールドが含まれるため、値変更=新規key=旧Masterと共存、旧keyは参照されなくなるだけで削除不要) | 固定Master(`level=None`)は既にStandard/Advanced共有設計(shell層は元々level非依存)。対称性の懸念なし | 要(Master Store書き込みは共有層。旧9 phrase資産の扱い[残置/削除しない]・welcome[Aのみ=現行維持]の扱いを明記する必要) |
| 7 | Variable Role Style(J3/E2) | `APPROVED_FOR_PRODUCTION`(配線完了、`PRODUCTION_WIRED`判定待ち、`TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01`) | 配線済み: `er003_b1_p9a_audio.py`(ja分岐)、`er003_v1_n3_01_tts_generate.py`(`style_prefix_override`引数)、`er033_tts_flash_lite_family_x_styles_01.py`(`FAMILY_X_ROLE_STYLE_JA`/E2値)、`er019_family_x_audio_production_runner_01.py`(`_role_style_ja()`、preview/comment_1〜4のみ) | **japanese_titleが未配線であることを確認**(`er019_family_x_audio_production_runner_01.py` L764-770、`n3_tts.generate_a2_japanese_with_reading_safety(japanese_title, ...)`呼び出しに`style_prefix_override`引数が渡されていない。関数自体はPhase Bで対応済み[引数受け取り可能]だが呼び出し元が渡していない) | Standard(A2)のみJapanese Titleが存在(Advanced/B1Bは英語のみのためJ3適用対象外、非対称ではなく「同じ日本語segmentが存在しないため適用しない」という委任文§8の原則どおり) | 既にOpus L2レビュー対象(既報MAJOR含む)、japanese_title差分も同一PRとして扱うべき |
| 8 | Standard/Advanced整合(6-role英語Style共通・slower維持・Master共通・新構造共通・Full Story E2一貫・retry/fallback整合) | 6-role/slowerは`PRODUCTION_WIRED`(`TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-02`)。新構造共通性は#2に従属(未配線) | 上記各行に分散 | - | 本行自体が対称性の検証項目 | #2/#6/#7と共通 |
| 9 | Opus L2是正(runtime evidence欠落・cache version guard・Japanese Title J3統一) | 既報MAJOR(`TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01_REPORT.md`§Opus L2所見)、未是正 | `er003_b1_p9a_audio.py`(A2経路はstyle_prefix runtime evidence有り)、`voice01.generate_charon_english`/`news_tail_fix.generate_news_narration_wide_margin`/`point_headings.generate`(3ファイル、B1B[Advanced]英語経路、style_prefixフィールド無し) | 3ファイルへstyle_prefix runtime evidence追加(ファイル所有範囲外だった前タスクから引き継ぎ) | Advanced経路のみの欠落(非対称そのものがOpus L2指摘の対象) | 要(Family A/B/C[legacy]も共有する`voice01`/`news_tail_fix`/`point_headings`モジュールへの変更のため慎重な影響評価が必要) |
| AN3-T0参照 | AN3-T0で使うOpenAI Response API `previous_response_id`チェーン・fallback_full_text経路 | `PRODUCTION_WIRED`(#4と同一) | `er019_family_x_ja_writer_o_r1_r2_01.py` | 変更なし | 対称 | 不要 |
| Flash-Lite backend既定/明示条件 | `PRODUCTION_WIRED`(`TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-02`、既定`structured_separation`のまま、`--tts-backend speech_metadata_flash_lite`明示時のみ) | `er019_family_x_audio_production_runner_01.py`全域 | 変更なし(本タスクのE2EはFlash-Lite明示指定で実行する前提) | 対称(既定切替はFable/ユーザー判断待ちのまま、本タスクでは変更しない) | 不要 |
| KP 4+1構成・Strategy L/DB Hybrid | `DECIDED`/`PRODUCTION_WIRED`(既存、変更対象外) | `er003_v1_n3_01_scaffold_generate.py`系Key Phrase選定 | 変更なし | 対称 | 不要 |
| Pronunciation Ledger等関連既配線 | `PRODUCTION_WIRED`(既存) | `er006_pronunciation_research_01.py`等 | 変更なし | 対称 | 不要 |

**非対称の総括**: 意図的な非対称が1件(#5 Advanced Key Phrase英語解説はAdvanced専用、CEFR設計上正しい)。意図しない非対称が2件: (a) #7 japanese_title未配線(Standard固有segmentのため設計原則には反しないが、ユーザーの「Japanese TitleもJ3へ統一」という明示指示に対して**未達**)、(b) #9 Advanced英語経路のruntime evidence欠落(既報MAJOR)。#2/#3は両レベル共通で未配線という「非対称ではないが両方とも未達」の状態。

---

## 2. 記事入力の特定(Hormuz/Meta AN3-T0最終R2)

### 2-1. 候補の網羅的列挙

Grep結果、AN3-T0関連の日本語記事出力ディレクトリは1件のみ存在:
`er019_output/family_x_entertainment_production_runner_01/an3_t0_wiring_regression_01/{hormuz,meta}/`。
`er039_output/`配下にAN3-T0名のディレクトリは存在しない(AN3-T0は
`er039`ではなく`er019_family_x_ja_writer_o_r1_r2_01.py`経由、Trial-02は
`er039_family_xy_concreteness_control_trial_02.py`で別モジュール)。

### 2-2. reminder有無の実機確認(read-only、sha256/git blame)

`hormuz/ja_writer/runtime_evidence.json`・`meta/ja_writer/runtime_evidence.json`
の両方を直接読み、`verbatim_shas`に`concreteness_an3_reminder_sha256`
キーが存在し、かつR1/R2の`instruction`本文が実際に以下の一文で終わって
いることを確認した(mojibakeを避けるためPython読み込みで直接確認、
Hormuz/Meta両方で一致):

> 「この修正で、すでに減らした細かい数字・時刻や固有名詞を、記事理解に
> 必要でない限り再び増やさないでください。」

`git log -S"CONCRETENESS_CONTROL_AN3_REMINDER_JA"`で該当定数の定義箇所を
特定した結果、この文言は`1f47ff72`(reminder追加commit、初回Production
Wiring時)で導入され、`54739a9d`(reminder削除commit、2026-09-28ユーザー
正式決定「AN3はOriginal側のみ、Trial-02と同一条件」)で完全削除された
ものと**一致**する。すなわち`an3_t0_wiring_regression_01`は**`1f47ff72`
時点のコード(reminder有り)で生成されており、`54739a9d`後の現行仕様
(reminder無し)とは異なる条件で生成されている**。

Fact Check(`fact_checks_summary.r2.final_status`)はHormuz/Metaとも
`LEDGER_COMPLIANT`(Hormuzはmust-fix適用0件で初回COMPLIANT、Metaは
`HF-006`/`HF-009`のmust-fix1回適用後にCOMPLIANT)。

sha256(read-only確認、`certutil -hashfile`):
- Hormuz `revision2.md`: `5234ca71ecfb1e28f01f3c72b56240b7d38730710377e0d2ce35c94038a83ca5`
- Meta `revision2.md`: `04363a8e826581883381d15a7fe611a4faa20a11e2a259edea399a5758d2ff37`

### 2-3. 判定

**「Trial-02条件(AN3はOriginal側のみ、R1/R2は既存指示のみ、reminder無し)
かつFact Check済み最終R2」を満たす候補はディスク上に存在しない**
(唯一の候補がreminder有りで生成されており、条件を満たさない)。

**これはSTOP候補である**(委任文§1「特定不能なら代替生成せず
STOP報告」に該当)。代替案(実施しない、列挙のみ):
1. `an3_t0_wiring_regression_01`をreminder無し条件の代替として
   そのまま採用する(不採用推奨: ユーザーが明示的に「reminderは
   Trial未検証の追加仕様のため削除」と正式決定した経緯[§4]と矛盾する)。
2. 現行コード(reminder削除済み)でHormuz/MetaのOriginal→R1→R2を
   再実行する(Writer LLM呼び出し、有償。§5でA費用として概算)。
3. ユーザーが「reminder有り版でも実質的な内容差は軽微」と判断し、
   例外的に現行版をそのまま採用する(Product判断、Sonnetが独断で
   選択しない)。

Fable/ユーザー確認事項: 上記のうちどれを採用するか。本設計書は
選択肢2(現行仕様での再生成)を前提としたE2E費用概算(§5)を用意する。

---

## 3. 実装設計(最小diff、ファイル所有分割案)

### 3(a) 新記事構造

**Advanced化Prompt**: `er003_v1_n3_01_advanced_adaptation_generate.py`の
`ADVANCED_ARM3_BLOCK`(L110-117、"You may reorder, merge, or reshape
paragraphs..."=段落再構成を明示許可)と`ADVANCED_CONTRACT_SUFFIX_LINES`
(L210-218、見出し2つ+In one line生成指示)は、新構造(見出し廃止・忠実
英訳)とは非両立のため、Family X専用の新Prompt定数(Trial-01設計書
§3-1の`TRIAL_FAITHFUL_TRANSLATION_INSTRUCTION`をProduction定数として
移設)に置き換える。`ADVANCED_VOCAB_RULE_V2_BLOCK`(L144-187、sha256固定
検証あり)は語彙難易度ルールで構成編集とは独立のため**そのまま流用**
(Trial-01が既に確認済みの方針を踏襲)。In One Line生成は別Prompt呼び出し
に分離する(Trial-01 §3-2の`TRIAL_IN_ONE_LINE_V2_INSTRUCTION_TEMPLATE`を
Production定数化、絶対語数上限は設けず「参考ガイド」表現のみ)。

**Standard(A2)側**: `er012_e_family_entertainment_two_level_runner_01.py::run_writer_stage()`
のA2生成(`sc.split_article_text(standard_text)`呼び出し、L419)も同じ
旧split関数を使っているため、Advanced英訳結果をA2難易度へ変換する
既存経路(A2 Writerが別途生成しているか、Advanced本文をベースに変換
しているかは`run_writer_stage()`本体[L293-430]の全体像を要追加確認、
本Phase Aでは当該範囲を行番号のみ確認し全文読解していない。**Phase B
実装時に必ずA2生成ロジックの入力元を確認すること**、STOP候補ではないが
未確認事項として明記)。

**決定論的3分割**: `split_article_text()`(er003、L107-162)と
`split_family_x_article_text()`(er019_family_x_audio_plan_01、L72-133)を
どちらも置き換えるのではなく、**新規関数`split_family_x_article_text_v2()`
を同ファイルに追加**し、呼び出し元(`run_writer_stage()` L351/419、および
Family X audio plan生成箇所)を新関数へ切り替える設計を推奨する(旧関数
`split_article_text`はFamily A本体が現役利用[要`git grep`確認、Family X
以外の呼び出し元がないかPhase Bで再確認]のため、Family X向け新構造は
別名関数として追加し、旧関数へ手を入れない=Family A無影響を関数レベルで
保証)。アルゴリズムはTrial-01 §3-3(段落単位、2境界全探索、二乗誤差
最小化、段落3未満はエラー)をそのまま移植する。

**Assembly**: `er019_family_x_audio_production_runner_01.py`の
`stage_assemble_family_x_b1/a2()`(L1083/1293)自体は`asm.assemble_with_timeline()`
(既存汎用関数)を呼ぶのみのため無変更で流用可能。変更が必要なのは
segment順序を決めるsequence構築ロジック(`full_story_part2_heading`/
`full_story_part3_heading`のHEADING_READOUT sub-segmentを生成する箇所、
`er019_family_x_audio_plan_01.py`のCOMMENT_3/4 role定義付近)であり、
新構造ではHEADING_READOUT segment自体を生成しない(sequenceから除去)。

**Audio Validation Gate**: `verify_episode_audio_validation_gate()`
(asm、既存)がparts定義(現行はHEADING_READOUT込みの11ish part)を
前提にしている場合、新構造(9 part: Comment1-4+body1-3+In One Line+
Preview相当)へのGate定義更新が必要(本Phase Aでは`asm`モジュールの
Gate定義本体を未読了、Phase Bで確認要)。

### 3(b) KP英語解説

text生成: `er041_key_phrase_advanced_english_explanation_trial_02.py`の
Prompt(B候補、`explanation_en`仕様文の逐語再利用)を、KP選定
(`keywords_canonicalized.json`生成)直後・Assembly前のstageとして
Production KP経路(Advanced/B1Bのみ)へ追加する。音声: 既存
`generate_key_phrase_component_verified()`(`er003_v1_repro01_main_generate.py`
L730)と同型の新規呼び出し(voice=Aoede、model=gemini-3.8-flash-lite-tts、
style=Trial-04 Variant B)、Role名`KEY_PHRASE_EXPLANATION_EN`。

Assembly順序: **STOP候補**。CURRENT_SPECの既存Advanced KP構造記載
(「B-Family」節)は「英語句+日本語意味」の順序のみで、「英語句→英語解説→
日本語意味」の3層順序をどこにも規定していない。これは新しいProduct
判断が必要な事項であり、本Phase Aでは順序を決定しない(委任文§14の
STOP条件「新しいProduct判断が必要」に該当)。Fable/ユーザー確認が必要。

### 3(c) 固定Master登録

`er006_master_audio_store_01.py::register()`(関数名は要Phase B確認、
`MasterAudioKey`のadd相当)を使い、Champion採用9 phrase(welcome除く)の
音声ファイルを、Production命名規則(`style_instruction_id`は現行の
`"charon_english_fixed_shell"`/`"charon_japanese_fixed_shell"`を維持し
つつ、`style_instruction_version`をChampion用に新bump、例:
`"v3_champion_2026_09_29"`)で登録する。音声バイト自体はTrial出力
(`er043_output/.../champion_trial_results.json`のB/C選定音声、
`er047_output/.../num_three_styleB/take1/narration/num_three.wav`・
`num_five_styleB/take1/.../num_five.wav`)からコピー可能(sha256一致を
確認したうえでの再利用、新規TTS不要)。**重要**: Trial側`MasterAudioKey`は
`level="retrial01_take{N}"`のようなTrial限定値を使っているため、
Production登録時は`level=None`(既存shell仕様どおりlevel非依存)へ
正しく再構築する必要がある(単純コピーではなくkey再構築が必須)。旧
9 phrase資産(現行`v2_flash_lite_short_style`)は削除せず残置(新
versionのkeyが生成されるため、以後のreuseは新keyのみが参照される)。

### 3(d) Role Style(Japanese Title統一・cache version guard)

`er019_family_x_audio_production_runner_01.py` L767-770の
`n3_tts.generate_a2_japanese_with_reading_safety(japanese_title, ...)`
呼び出しへ`style_prefix_override=_role_style_ja()`を追加する1行diff
(`_role_style_ja()`は同ファイル内L728-731に既存、追加実装不要)。

cache version guard: `er033_tts_flash_lite_family_x_styles_01.py`に
`style_instruction_version`相当の識別子が存在しないことをPhase Aで
確認済み(§9-2既報のとおり、可変segmentはMaster Store対象外のため
version管理フィールド自体が無い)。Opus L2指摘の「cache versionを
使い不一致ならreuse しない」は、**可変segment自体がMaster Store非対象
という設計上、technical に該当しない**可能性が高いが、E2E実行時に
「以前のRun(reminder有りWriter時代等)で生成された音声ファイルを、
現行のJ3/E2 styleと知らずにreuseしてしまう」リスクは、可変segmentは
そもそもStore非対象=hormuz/metaの`narration/*.wav`ファイルを直接
readonly cacheする`_load_cached_tts_results()`/`_generate_or_reuse()`
機構(`er019_family_x_audio_production_runner_01.py`)側の問題である。
**Phase BでE2E実行時、旧runのnarration/*.wavディレクトリを新規out-dirへ
コピーしない(必ず新規out-dir、または明示的にstyle不一致を検知する
guardを`_generate_or_reuse()`へ追加)ことをGuardrailとして明記する**。

Advanced英語経路3ファイル(`voice01.generate_charon_english`/
`news_tail_fix.generate_news_narration_wide_margin`/
`point_headings.generate`)へのstyle_prefix runtime evidence追加は、
Family A/B/C(legacy)共有モジュールへの変更のため、Phase Bでは
「戻り値dictへの`style_prefix`フィールド追加のみ(呼び出し方は無変更)」
という最小スコープに限定し、Opus L2の事前了承を得てから実施する
(独断で共有層を変更しない)。

### 3(e) AN3 reminder不在の再確認手順

`git grep -n "REMINDER" er019_family_x_ja_writer_o_r1_r2_01.py`が0件
であることをPhase Bの実装完了後にも再実行し、確認結果をREPORTへ記録
する(Phase Aで既に0件であることを確認済み、§2-2)。

### 3(f) 影響ファイル一覧と並列実装の所有分割案

| ファイル | 変更内容 | 依存関係 |
|---|---|---|
| A: `er003_v1_n3_01_advanced_adaptation_generate.py` | 新Prompt定数追加(旧定数は無変更のまま残す、Family X専用呼び出し元のみ切替) | 独立(最初に実装可) |
| B: `er019_family_x_audio_plan_01.py` | `split_family_x_article_text_v2()`新設、COMMENT role文言調整(必要なら)、HEADING_READOUT除去 | Aに依存(新Prompt出力形式を前提にparseするため) |
| C: `er012_e_family_entertainment_two_level_runner_01.py` | `run_writer_stage()`の呼び出し先をv2 splitへ切替、In One Line v2生成stage追加 | A・Bに依存 |
| D: `er019_family_x_audio_production_runner_01.py` | japanese_title J3配線(1行)、KP解説音声生成呼び出し追加、Assembly sequence更新(HEADING_READOUT除去) | B・KP text生成(E)に依存 |
| E: KP解説text生成の新stage(新規ファイルまたは既存KP選定モジュールへの追加) | `er041`のPromptをProduction定数化 | 独立(A/B/Cと並行実装可) |
| F: `er006_master_audio_store_01.py`呼び出し側(Champion登録用の一回限りscript、新規) | Master Store書き込み(register呼び出し) | 独立(並行実装可、Store本体は無変更) |
| G: Assembly Gate定義(`er003_v1_n3_01_assemble.py`内、要Phase B精査) | parts定義更新 | B・Dに依存 |

依存順序: (A→B→C)と(E)と(F)は並行実装可能。D・Gは B/C/E の完了後に
統合。並列実装時のファイル所有はA+B+C(1名)、D+G(1名、B/C完了待ち)、
E(1名)、F(1名)の4分割を推奨(衝突しない単位)。

---

## 4. Regression/integration計画

**既存テストへの影響確認**:
- `er003*_test_*.py`(scaffold/assemble関連): 旧`split_article_text()`
  無変更のため既存Family A向けテストは無影響のはず(新関数を別名で
  追加する設計のため)。念のため`run_project_regression.py --pattern
  "er003*_test_*.py"`をPhase B実装後に実行する。
- `er019*_test_*.py`(157件、直近実測): Family X runner本体・
  `split_family_x_article_text`関連テストは新関数追加+呼び出し切替に
  伴い期待値更新が必要(HEADING_READOUT前提のテストは削除または新構造
  向けに書き換え)。
- `er033*_test_*.py`/`er044*_test_*.py`: Role Style定数の期待値は
  無変更(既にJ3/E2へ更新済み、Phase B分の追加は無し)。
- `er038*_test_*.py`: Role Style trial関連、japanese_title差分の影響
  範囲外(想定)。

**新規integration test(Phase B実装時に追加)**:
1. 新Assembly構造test(Comment1→body1→...→In One Line、HEADING_READOUT
   segmentが存在しないことをsequence assertionで確認)。
2. Master Store選択test(Champion採用9 phraseが新versionから正しく
   解決されること、旧versionへの誤fallbackが無いこと)。
3. Style version guard test(§3(d)のGuardrail、旧narration wavを
   誤ってreuseしないことのunit test)。
4. japanese_title J3配線のunit test(既存`er019_family_x_variable_role_style_wiring_01_test_01.py`
   への追加、13→14件相当)。
5. KP解説Role配線のunit/integration test。

---

## 5. E2E計画と費用概算(A/B分離)

### 5-1. 生成段階(Hormuz/Meta × Standard/Advanced)

1. JA記事: §2の判定に従い、STOP解消後(reminder無し版のOriginal→R1→R2)
   再生成が必要(Hormuz/Meta各1本)。
2. Advanced英訳: 新Prompt(3(a))で新規生成(2記事×1)。
3. 決定論3分割: LLM呼び出し無し(¥0)。
4. In One Line v2: 新規生成(2記事×1)。
5. Deviation Check: 新規1回(2記事×1)、MAJOR時must-fix retry1回
   (最大2記事×1追加)。
6. Standard(A2)本文: Advanced英訳ベースの変換方式に依存(§3(a)で要
   追加確認、Phase Bで費用確定)。
7. Comment1〜4: 委任文は「既存Comment1〜4は直近runのCommentをreuse」
   前提だが、新構造では本文3分割の内容配置が変わるため、Commentの
   文脈整合性を再確認する必要がある(reuse可否はPhase Bで文脈diffを
   確認してから判断、新規生成の可能性あり)。
8. KP選定: 既存Strategy L/DB Hybrid、変更なし(reuse可能性あり、
   JA記事が変われば新規選定が必要)。
9. KP解説text: 新規生成(2記事×5 phrase)。
10. TTS: Standard 12segment+Advanced 12〜19segment相当(既存実測
    Task B Advanced 19segment≈¥30、Task 3 24segment¥20.7を参考)、
    KP解説音声5segment×2記事、固定Master(reuse、追加TTS 0)。
11. ASR/Validation: 既存cascade(追加費用なし、TTS呼び出しに内包)。
12. Assembly: ¥0(API呼び出しなし)。

### 5-2. 費用概算(A: 一回限り／B: 量産1記事あたり増減)

| 項目 | A(一回限り、Wiring確認・E2E検証) | B(量産1記事あたり増減) |
|---|---|---|
| JA Original→R1→R2再生成(reminder無し、Hormuz/Meta各1) | 実測前例なし、Writer LLM(gpt-5.6-luna)3-4 call×2記事、既存AN3-T0実測費用が参考(未計上、Phase Aでは¥0のため実測なし。Phase Bで最初の1回を実測すること) | 影響なし(新規記事は元々必要な費用) |
| Advanced英訳+In One Line v2 | 2 call×2記事=4 call(Trial-01実測ベース、writer 1 call相当) | 既存Advanced化Promptと同程度(見出し2つ生成の代わりに構造無しの英訳、call数は同等かやや軽い) |
| Deviation Check(+must-fix retry) | 2記事×1(+最大2) | 既存仕様のまま(新設ではない) |
| KP解説text生成 | 2記事×5phrase相当、1 call/記事(小)) | **+1 call/記事**(新規) |
| KP解説音声(Variant B) | 2記事×5segment=10segment、Trial-04実測¥2.02/15segment(A+B+C)から概算 | **+5segment/記事**(Advancedのみ) |
| Heading Readout撤去による削減 | - | **-2segment/記事**(Advanced full_story_part2_heading/part3_heading相当が無くなる) |
| Master Champion登録(固定phrase) | ¥0(既存音声reuse、新規TTS無し) | **±0**(固定Masterはreuse、量産コストへの影響なし) |
| Standard/Advanced本体TTS(新構造) | Hormuz実測Task B Advanced 19segment≈¥30、Task3 24segment¥20.7を参考に、2記事×2レベルで概算¥80〜¥120 | 既存TTS呼び出し数と概ね同等(segment数の増減は上記Heading撤去分-2とKP解説+5が相殺方向) |
| must-fix retry(既存仕様) | 発生した場合のみ追加 | 影響なし(既存retry policy、新設ではない) |
| **概算合計(A)** | **¥150〜¥250程度**(JA再生成費用が未計上のため保守的な下限、Phase B実測で確定要) | - |

**Guardrail案(段階別)**:
1. JA再生成: `--budget-jpy 20`相当(記事1本あたり)。
2. Advanced英訳+分割+In One Line: `--budget-jpy 10`。
3. KP解説text+音声: `--budget-jpy 15`。
4. TTS本番E2E(Standard+Advanced、Hormuz/Meta各1): `--budget-jpy 60`
   (段階ごとに`assert_budget_ok`確認、OPEN-226の**冪等性ガード**を
   Phase Bで実装するまでは、`--stage all`の再実行を絶対に行わない
   [既存合格segmentの意図しない再生成・二重課金を防ぐため]、必ず
   `--stage`を個別指定して段階実行する)。

---

## 6. Gate 13項目の証拠計画とSTOP該当有無

| Gate項目(委任文§13) | 証拠計画 |
|---|---|
| 初回path/retry/fallback/regeneration/Local Rewrite | Phase B実装後、Hormuz/Meta実データでの実行ログ(`attempts_log`)を保存 |
| cache/Master Store | §3(c)のkey再構築を実施した後のmanifest.json diffを保存 |
| Standard・Advanced整合 | §1対応表の非対称欄が両方解消されたことをcommit後に再Grepで確認 |
| runtime evidence/actual model・voice・Style | §3(d)のjapanese_title style_prefix追加後の実行結果JSON、Advanced経路3ファイルへの追加(Opus L2了承後) |
| Regression・integration test | §4の全項目実行、PASS件数を記録 |
| Hormuz・MetaのE2E実発火 | §5実行後のassembled wav・player.html・sha256を記録 |
| CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS/REPORT_LEDGER | Phase B完了後にSonnetが追記(本Phase Aでは編集していない) |
| commit・push | 各Phase完了ごとに実施 |
| OPEN-228 close | §3(a)完了後にCLOSED/SUPERSEDEDへ更新 |
| approved仕様と実挙動の一致 | Fable/Opus L2レビューで最終確認 |

**STOP該当(現時点で判明分)**:
1. **§2の記事入力**: Trial-02条件を満たすAN3-T0最終R2がディスク上に
   一意に存在しない(reminder有り版のみ存在)。Fable/ユーザー判断が
   必要(§2-3の3選択肢)。
2. **§3(b)のAssembly順序**: Advanced KP解説の音声配置順序(英語句→
   解説→意味 の3層順序)がCURRENT_SPECに規定が無く、新しいProduct
   判断が必要。
3. **§3(a)のStandard(A2)本文生成経路**: `run_writer_stage()`の
   A2生成ロジックの入力元(Advanced英訳からの変換か独立生成か)を
   Phase Aでは確認しきれておらず、Phase B実装前に追加確認が必要
   (STOP候補ではなく未確認事項、ただし確認の結果次第でStandard側にも
   Advanced同様のProduction Prompt変更が必要になる可能性がある)。

上記1・2はFable/ユーザーへのSTOP報告事項。3はPhase B開始前の追加調査
事項として申し送る。

---

## 7. SSOT文案の骨子(Phase Bで反映、本Phase Aでは編集していない)

### CURRENT_SPEC.md

- 「Family X(Entertainment News)音声構造」節(L1144-)へ、新構造
  (Heading廃止・忠実英訳・決定論3分割・In One Line簡潔化)を
  `APPROVED_FOR_PRODUCTION`として追記(本委任文がユーザー正式決定の
  記録である旨を明記)。旧「本文1/2/3の区切り定義」(L1199-1205)は
  SUPERSEDEDとして履歴を残しつつ新定義を追加。
- 「固定フレーズ Champion」節(L1616-)のnum_three/num_five「未確定」
  記載を、B-take1確定(本委任文が正式決定の記録)へ更新。
- 「Advanced Key Phrase 英語解説」節(L1677-)のAudio Style欄を
  Trial-04 Variant B確定へ更新。
- 「可変segment Role Style(J3/E2)」節(L1563-)へJapanese Title統一
  configuration追記(§3(d)実装後)。

### OPEN_ITEMS.md

- OPEN-228: Phase B実装完了後、`CLOSED`/`SUPERSEDED`(旧split/Gate/retry
  撤去・新構造置換完了、履歴保持)。
- OPEN-230: 新構造のmust-fix retry実装(既存仕様の流用)完了時点で
  `LEDGER_COMPLIANT`運用が両記事とも確認できたことを追記しCLOSE検討。
- OPEN-221: `KEY_PHRASE_EXPLANATION_EN`配線完了時点でCLOSE検討。
- OPEN-229: japanese_title J3統一実装完了時点でCLOSE検討。

### REPORT_LEDGER.md

- 本管理ID(Phase A)の1行追加: Status=`設計完了(実装はPhase B)`、
  詳細列に本設計書パス・STOP項目3件を記載。

---

## 8. 参照した事前指定Read/Grep(実施記録)

- `CURRENT_SPEC.md`: L885-920(AN3-T0)、L1144-1218(Family X音声構造)、
  L1470-1608(Flash-Lite/Role Style)、L1616-1644(Champion)、
  L1677-1679(KP英語解説)、L1764(日本語外来語Gate)関連行をGrep→
  該当範囲Read。
- `OPEN_ITEMS.md`: OPEN-201/221/222/223/226/228/229/230をpython
  正規表現抽出で確認(ファイル全体はサイズ超過のためRead不可、抽出方式)。
- `docs/pm/REPORT_LEDGER.md`: TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-01/02、
  TTS-FIXED-SHELL-NUMBER-THREE-FIVE-RETRIAL-01、
  KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-03/04行を確認。
- `docs/pm/design_family_x_no_heading_segmentation_trial_01.md`(全文)。
- `docs/pm/design_tts_variable_role_style_production_wiring_01.md`
  §7(リスク)・§9(Phase B実施記録)を中心にRead。
- `docs/pm/design_tts_fixed_shell_master_champion_trial_02.md`(全文)。
- `docs/pm/design_key_phrase_advanced_english_explanation_audio_style_trial_04.md`(全文)。
- Production: `er003_v1_n3_01_scaffold_generate.py`(L100-163)、
  `er019_family_x_audio_plan_01.py`(L60-160)、
  `er012_e_family_entertainment_two_level_runner_01.py`(L293/351/419の
  grep行確認)、`er003_v1_n3_01_advanced_adaptation_generate.py`(定数
  grep行番号確認)、`er019_family_x_audio_production_runner_01.py`
  (L655-780)、`er006_master_audio_store_01.py`(L30-60)、
  `er006_audio_cost_pilot_02_shared_narration.py`(定数grep)、
  `er003_v1_repro01_main_generate.py`(L730-800grep)。
- Trial: `er041`〜`er047`の対象ファイル存在確認(ls)、
  `er047_output/tts_fixed_shell_number_three_five_retrial_01/retrial_results.json`・
  `master_store/manifest.json`をread-only確認(num_three/num_five
  B-take1のstyle_prefix_used・voice・model・asr_verifiedを実機確認)。
- read-onlyハッシュ確認: Hormuz/Meta `revision2.md`のsha256(§2-2)、
  AN3-T0 reminder導入/削除commit(`git log -S`)。

## 9. Phase A完了時点のGuardrail遵守確認

- API支出: ¥0(LLM/TTS/ASR呼び出し0件、実施したのはGrep/Read/
  `certutil -hashfile`/`git log`のみ)。
- 削除・移動・`rm`・`git clean`・stash/rebase/reset/amend/force push:
  実施なし。
- 未追跡ファイル: 他Agent/ユーザー作業物として一切触れていない。
- 本タスク由来の差分: 本設計書・delegation_log・delegation_log_check.json
  のみ(`git status --porcelain -- "er0*.py" CURRENT_SPEC.md`は
  Phase A完了時点で空である必要がある、§Git実行時に確認)。

Opus L2 実施済み(1 回、所見は REPORT 参照)、Status:
USER_DECISION_REQUIRED(E2E 発火前是正の要否)。

## 9-W3. Phase B(W3)実装完了時点の記録

2026-09-29、委任`FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01`(_03、W3)。
§3(d)の設計どおり、以下を実装した(詳細は`FAMILY-X-REFRESH-E2E-
PRODUCTION-WIRING-01_REPORT_W3.md`参照。§9本体・W2章は編集していない、
本節のみ追記)。

- **MAJOR-1(Japanese Title統一)**: `er019_family_x_audio_production_
  runner_01.py`の`generate_family_x_a2_segments()`内、japanese_title
  呼び出しへ`style_prefix_override=_role_style_ja()`を追加(§3(d)の
  1行diffどおり)。Advanced(B1B)側`generate_family_x_b1_segments()`には
  日本語title相当segmentが存在しないことをGrep+Read(L468-631)で確認し、
  「該当なし」と記録する。
- **MAJOR-3(cache version guard)**: `_generate_or_reuse()`内で閉じる
  形で実装(§3(d)で示唆した代替案の後者を採用、共有層[Master Audio
  Store/shared_narration]には触れていない)。`FAMILY_X_VARIABLE_ROLE_
  STYLE_VERSION = "v2_j3_e2_title"`を新設し、`tts_generation_results.
  json`のトップレベル(`style_version`)へ保存。cacheの`style_version`が
  現行値と不一致・欠落の場合、`_generate_or_reuse()`は可変segment
  (japanese_title/topic_intro/preview/comment_*/full_story_*/heading/
  in_one_line)のreuseを行わず必ず`generate_fn()`で再生成する。shell固定
  phrase・Key Phrase側の`_generate_or_reuse_kp()`・`shared_narration`は
  この値を一切参照せず無変更。
- **MAJOR-2(Advanced英語経路のruntime evidence)**: §3(d)の方針どおり
  「戻り値dictへの`style_prefix`/`tts_model_id`/`voice`フィールド追加
  のみ(呼び出し方は無変更)」に限定し、`voice01.generate_charon_
  english`/`news_tail_fix.generate_news_narration_wide_margin`/
  `point_headings.generate`の3関数へ実施した(共有層[p4c/p9a本体の
  TTS呼び出し方式・fallback順序]は無変更)。
- **MINOR-A(既定時ラベル化)**: `er003_b1_p9a_audio.py`
  `generate_narration_snippet()`および上記3関数で、
  `style_prefix_override`指定時のみ実値を記録し、既定時は
  `"<default:ENGLISH_STYLE_PREFIX>"`/`"<default:JAPANESE_STYLE_PREFIX>"`
  に統一(Opus L2案どおり、200字truncate方式は不採用)。
- **MINOR-B**: 本節および`REPORT_W3`に、「runner配線(japanese_title/
  preview等がどのstyleを選ぶか)はmockによる単体テストで確認し、実際に
  生成した音声へのstyle反映(runtime実測)は後続のE2Eで取得する」という
  2段構成である旨を明記する。

Guardrail遵守確認(W3):
- API支出: ¥0(TTS/ASR/LLM呼び出し0件、既存のunit testはすべてmock)。
- 削除・移動・`rm`・`git clean`・stash/rebase/reset/amend/force push:
  実施なし。
- 未追跡ファイル・W2所有ファイル(`er006_audio_cost_pilot_02_shared_
  narration.py`/`er006_audio_cost_pilot_02_shared_narration_test.py`/
  `er006_master_audio_store_01.py`/`er048_*`): 一切編集していない
  (`git diff --stat HEAD -- "er0*.py"`で確認済み、本タスク由来の差分は
  所有5ファイル+テスト2ファイルのみ)。

### 9-W2 Phase B(W2、2026-09-29)実施結果の要約

固定フレーズChampion(welcomeを除く9 phrase)をProduction Master Store
(`er006_output/master_audio_store_01/`)へ正式登録した。詳細は
`FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_REPORT.md` §W2を参照
(対応表・manifest前後・reuseドライラン・テスト結果・費用・Opus L2論点)。

§3(c)からの主な実装判断:
- style_instruction_versionのbump名は`"v3_champion_2026_09_29"`
  (§3(c)の例をそのまま採用)。
- welcomeは現行Master(`v2_flash_lite_short_style`)継続、新規登録なし
  (ユーザー決定「welcome=A」)。
- phrase別Champion style文言は`er006_audio_cost_pilot_02_shared_
  narration.py`の`SHELL_CHAMPION_STYLE_BY_PHRASE_EN`
  (English 8 phrase)・`SHELL_CHAMPION_STYLE_JA_POINT_EXPLANATION_B`
  (JA 1 phrase)として実装し、`_make_english_key`/`_resolve_shell_
  english_style_prefix_override`に`name`引数を追加した(§3(f)のF担当
  スコープ)。
- Store側は`er006_master_audio_store_01.py::register_precomputed()`を
  最小追加(既存`get_or_generate`は無変更)。
- point_explanation(JA)はstyle override機構自体が`generate_charon_
  japanese`に無いため、Champion style文言はcache hit経路でのみ実際の
  音声と対応する(既知の限界、Opus L2論点としてREPORT §W2に記録)。

### 9-W1 Phase B(W1、2026-09-29)実施結果の要約

新記事構造(途中Heading廃止・忠実英訳・段落境界3分割・Comment1〜4・
Heading Readout撤去)をFamily X Production経路(`er012_e_family_
entertainment_two_level_runner_01.run_writer_stage()`+`er019_family_x_
audio_production_runner_01.py`)へ配線した。詳細は`FAMILY-X-REFRESH-E2E-
PRODUCTION-WIRING-01_REPORT.md` §W1参照(変更ファイル・Prompt sha256・
split一致証拠・JA入力検証表・テスト結果・Opus L2論点)。

§3(a)からの主な実装判断:
- `er003_v1_n3_01_advanced_adaptation_generate.py`/`er003_v1_n3_01_
  standard_a2_generate.py`ともに、既存`ADVANCED_*`/`STANDARD_A2_*`
  Prompt・生成関数は一切変更せず、Family X専用の新Prompt定数・新生成
  関数(`generate_family_x_faithful_translation`/`generate_family_x_
  standard_a2_no_heading`)を追加する設計を採用した(§3(f)の想定どおり)。
- h3構造Gate(`vfl01.run_writer_with_technical_retry`、Family A本体・
  News等が共有)には一切触れず、Family X専用の独立retryループを新設した
  (§6のOpen items「h3 validator置換」を、共有primitive変更ではなく
  新規追加で解消)。
- `split_family_x_article_text_v2()`は`er003_v1_n3_01_scaffold_
  generate.py`(Writer stage用)と`er019_family_x_audio_plan_01.py`
  (Audio用、scaffold実装への薄いwrapper)の両方に配置し、単一の
  アルゴリズム実装(scaffold側)を共有する設計とした。
- §3(a)で未確認事項だったStandard(A2)生成の入力元は、`std_gen.
  generate_standard_a2(advanced_text)`(Advanced英訳結果を入力とする)
  であることをコード読解で確認した(STOP候補ではなかった)。
- §6のSTOP候補1(JA入力の一意特定)は、er039 AN3-T0セル(er037/er039
  経由、Trial-02で既に生成済み)が機械検証条件をすべて満たしたため解消
  した(REPORT §W1のJA入力検証表参照、STOPに至らなかった)。
- §6のSTOP候補2(Advanced KP解説のAssembly順序)は本W1のスコープ外
  (次Phaseへ持ち越し、未解消のまま)。
- Standard(A2)の見出し廃止Promptはer045等で未検証の新規文言であり、
  Opus L2レビュー対象として明記した(REPORT §W1)。

Guardrail遵守確認(W1):
- API支出: ¥0(LLM/TTS/ASR呼び出し0件、単体テストは全てmock)。
- 削除・移動・`rm`・`git clean`・stash/rebase/reset/amend/force push:
  実施なし。
- E2E入力配置(`er019_output/family_x_refresh_e2e_01/{hormuz,meta}/
  input/`)は既存`er039_output`のコピーのみ(元ファイル不変)。
- W2/W3で入れた`SHELL_CHAMPION_*`・`FAMILY_X_VARIABLE_ROLE_STYLE_
  VERSION`・style_prefix evidence: 一切編集していない(`git diff --stat
  HEAD -- "er0*.py"`で本タスク由来の差分ファイル一覧を確認済み)。

### 9-W4 Phase B(W4、2026-09-29)実施結果の要約

Key Phrase 音声構造(Standard/Advanced共通骨格、CURRENT_SPEC.md「Key
Phrase 音声構造」節、2026-09-29ユーザー正式決定)をProduction配線した。
詳細は`FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_REPORT.md` §W4参照
(現状確認表・変更ファイル・先頭=末尾証明・量産コスト・テスト結果・
Prompt/Style sha256・Opus L2論点)。

§3(d)からの主な実装判断:
- 現状確認の結果、末尾Phrase「反復」構造自体は共有`er003_b1_p9a_audio.
  py::build_key_phrase_block()`が配線前から実装済み(先頭と同一の
  in-memory配列を末尾へも渡すだけで新規wav生成は元々発生しない)ことが
  判明した。Standard(a2)はこの事実により無変更、Advancedは中間部分の
  みを日本語意味→英語解説へ差し替える設計にした。
- Advanced専用の新関数(`generate_key_phrase_explanation_en_verified`)
  は共有資産`er003_v1_n3_01_tts_generate.py`ではなくFamily X runner
  自身(`er019_family_x_audio_production_runner_01.py`)に配置した
  (`er019_family_x_pointless_01_test_01.py::FamilyAUnchangedTest`が
  同ファイルのgit working tree diff=0を機械的に強制しているため)。
- `key_phrase_meanings`という変数名/parts keyは、共有`build_b1_key_
  phrase_blocks()`がこの名前をハードコード参照するため意味的には
  「英語解説」を保持しながらも名前は変更しなかった(Opus L2論点1として
  明記)。
- text生成(explanation_en)は5件(4+1構成)まとめて1 callとし、run単位の
  text cache(`key_phrase_explanations_text`)を新設した。

Guardrail遵守確認(W4):
- API支出: ¥0(LLM/TTS呼び出し0件、単体テストは全てmock)。
- 削除・移動・`rm`・`git clean`・stash/rebase/reset/amend/force push:
  実施なし。
- W1/W2/W3の資産(新記事構造・Master Champion・可変Role Style/cache
  version guard): 一切編集していない(`git diff --stat HEAD --
  "er0*.py"`で本タスク由来の差分ファイル一覧を確認済み、
  `run_project_regression.py --pattern "er019*_test_*.py"`で
  collected=232 passed=232を再確認)。

### 9-W5 Phase B(W5、2026-09-29)実施結果の要約

Opus L2設計レビュー所見(BLOCKER 1件・MAJOR 4件、REPORT行459-548)を
「既承認仕様から一意に決まる実装是正」として是正し、Standard Key
Phrase日本語意味へのJ3適用(ユーザー正式決定`APPROVED_FOR_PRODUCTION`)
を配線した。詳細は`FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_REPORT.md`
§W5参照(変更箇所・E2E前¥0 Gate 6項目・Standard/Advanced対比表・
E2E-PLAN・テスト結果)。

§3(d)/(b)からの主な実装判断:
- BLOCKER-1是正により、KP英語解説のQA NGは技術retry(1回)後もそのまま
  採用せず(`NG_ACCEPTED_AFTER_RETRY`廃止)、fail-closedでTTSを呼ばず
  `status="STOPPED"`にした。既存Audio Validation Gate/
  `record_human_approval()`経路をそのまま流用し、新しいHuman Review
  機構は追加していない。
- MAJOR-1是正の`require_style_version`guardは、既存の可変segment
  cache version guard(W3で導入した`FAMILY_X_VARIABLE_ROLE_STYLE_
  VERSION`)をKey Phrase側(`_generate_or_reuse_kp`)へも拡張適用する
  設計にした(新しい別のversion管理機構は作らない)。Standard KP日本語
  意味へのJ3適用に伴い同versionをbumpした。
- MAJOR-2是正は`split_family_x_article_text_v2()`側にGateを集約する
  設計にした(`generate_family_x_standard_a2_no_heading()`側は`^#\s+`
  必須化のみ)。既存`_family_x_ensure_split_or_paragraph_retry()`が
  status非依存の汎用retryとして元々設計されていたため、呼び出し側の
  ロジック変更は不要だった。
- MAJOR-4是正は、`er012_e_family_entertainment_two_level_runner_01.py`
  の非writer stage関数(scaffold/tts/assemble/player)を関数呼び出し
  レベルでfail-fastする設計にした(CLIの`--stage`choices制限のみでは
  直接呼び出しからの到達を防げないため)。`build_player_html()`は
  `_row_info_b1b`/`_row_info_a2`/`_build_level_table`の追加削除を避け
  るため、元実装本体を到達不能なまま関数内に残置する最小diffを採用
  した。

Guardrail遵守確認(W5):
- API支出: ¥0(LLM/TTS/ASR呼び出し0件、単体テスト・regressionは全て
  mock)。
- 削除・移動・`rm`・`git clean`・stash/rebase/reset/amend/force push:
  実施なし(`git stash`/`git stash pop`はpre-existing失敗の非起因確認
  のためのみ使用し、即座にpopして復元、変更の破棄は発生していない)。
- W1〜W4の資産(新記事構造・Master Champion・可変Role Style/cache
  version guard・KP音声構造骨格): 承認済み構造は変更せず、Opus L2所見
  是正+Standard KP日本語意味へのJ3配線のみ追加した(`git diff --stat
  HEAD -- "er0*.py"`で本タスク由来の差分ファイル一覧を確認済み)。

## 9-E2E. Phase C(E2E、委任_09〜_10)実施結果の要約

委任_09でHormuz Advanced writer段がJA_RECHECK_REQUIRED STOP
(deviation MAJOR、origin=ja_source)。Fable判定によりこれを既存
fail-closed仕様どおりの動作と確認し、委任_10でJA記事をProduction正式
JA経路(`er019_family_x_entertainment_production_runner_01.py`→JA
Writer O)で新規生成し直しrun_02として継続したが、English Advanced
writer段で**別のclaim**によるja_source MAJORが再発しSTOP(詳細は
`FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_REPORT.md`§E2E再開参照)。
Audio段(scaffold/tts/assemble/player)・Gate 13+9項目・試聴ページは
Hormuz/Meta双方とも未到達のまま。コード・Prompt変更は本委任では
実施していない(発見事項はチェッカー間非対称のUDRとして報告のみ)。

## 9-W6. ja_source MAJOR暫定対応「案B」のProduction配線(委任_11、
2026-09-29、ユーザー明示決定によりAPPROVED_FOR_PRODUCTION、Gate 3まで
PRODUCTION_WIREDとしない)

### 配線位置の設計判断

委任_10のE2E実測により、実運用では2つの独立したCLI呼び出しパターンが
併存することを確認した: (i) `er019_family_x_entertainment_production_
runner_01.py`が単一プロセス内で`efam.run_writer_stage(only="advanced"
/"standard")`を順に呼ぶ経路、(ii) `er012_e_family_entertainment_two_
level_runner_01.py`をJA記事ファイル(`--ja-article`)を指定して**独立
プロセス**として直接実行する経路(委任_10のWriter段[English、run_02]
再実行が実際にこの経路を使った)。案Bの候補(i)(er012_eのwriter stage
がJARecheckRequiredErrorを自ら捕捉)と(ii)(er019 production runnerの
orchestration層で2 runnerを包む)のうち、**(i)を採用**した。理由:
候補(ii)はer019の単一プロセス内呼び出し(パターン(i)実測)にしか
効かず、pattern(ii)実測(独立CLI直接実行)では案Bが発動しない欠陥に
なるため。`run_writer_stage()`自体にJA再生成能力を持たせれば両パターン
に等しく効く。

### 実装(最小diff・既存契約維持)

- `er012_e_family_entertainment_two_level_runner_01.py`: 既存の
  `run_writer_stage()`本体(Advanced/Standard生成+deviation retry+
  paragraph retryの既存ロジック、無変更)を`_run_writer_stage_once()`
  へ改名し、新しい薄いwrapper`run_writer_stage(..., storyline_line=None,
  selected_fact_brief_text=None, _ja_recheck_attempted=False)`を追加
  した。両方がNone(既定)の場合は`_run_writer_stage_once()`の結果を
  そのまま返す(ja_recheck_used/ja_recheck_attemptsキーを追加するのみ、
  既存呼び出し元への影響なし・後方互換)。両方が渡された場合のみ、
  `JARecheckRequiredError`を捕捉し、
  `er019_family_x_ja_writer_o_r1_r2_01.run_ja_writer_o_r1_r2()`を
  `original_must_fix`(新規追加、既定None)付きで1回だけ呼び直し、成功
  すれば`_run_writer_stage_once(only=None)`でAdvanced/Standardを丸ごと
  再実行する(Advanced/Standard合計でJA再生成は1回、Standard段での
  発生も同じ枠を消費)。再実行後も`JARecheckRequiredError`ならreasonへ
  `ja_recheck_attempts=1`を付記して再送出し、STOPする(2回目のJA再生成
  は呼ばない=無限retry禁止、`_ja_recheck_attempted`は将来の呼び出し
  ネスト対策として保持するのみで現設計では再帰しない)。JA
  Fact Check自体がSTOP(`JAFactCheckStopError`)した場合は
  `RuntimeError`へ変換しSTOPする(既存`run_ja_writer`[er019]のSTOP方針
  と同型)。
- `er019_family_x_ja_writer_o_r1_r2_01.py`: `run_ja_writer_o_r1_r2()`に
  `original_must_fix: list | None = None`を追加し、Original段の最初の
  `build_original_prompt()`呼び出しへそのまま渡すのみ(既存の
  `build_must_fix_block`/`build_original_prompt`のmust_fix機構をそのまま
  再利用、新しいPrompt文言は追加していない)。Noneの場合(既定)は従来と
  完全に同じPromptになる(後方互換、既存8テスト全通過で確認)。
- `er019_family_x_entertainment_production_runner_01.py`: `main()`の
  advanced/standard呼び出し2箇所に`storyline_line=storyline_result[
  "selected_storyline"]`/`selected_fact_brief_text=storyline_result[
  "selected_fact_brief_text"]`(既にin-memoryで保持している値)を追加。
- `er012_e`のCLI`main()`: `--out-dir`配下に`storyline_b3/
  fact_selection_evidence.json`が存在する場合のみ自動でstoryline_line/
  selected_fact_brief_textを読み込み`run_writer_stage()`へ渡す(存在
  しない場合はNoneのまま=案B無効・従来どおり後方互換)。新しいCLI引数は
  追加していない(委任の「案B有効化に必要な引数(あれば逐語)」に対する
  回答は「なし、`--out-dir`配下のstoryline_b3成果物の有無で自動判定」)。

### 副作用として明示すべき挙動(意図的・spec通り)

`only="advanced"`のみを要求した呼び出し(例: er019の
`--stop-after advanced`)でJA recheckが発動した場合、redoは常に
`only=None`(Advanced+Standard両方)で行われるため、呼び出し元が
Standardを意図していなくてもa2/配下が生成される。これは委任「Advanced/
Standard合計でJA再生成は1回」の逐語指示どおりであり、Advancedの再生成
結果がStandardの入力(advanced_text)であるため技術的にも必然(Standard
だけを古いAdvancedのままにはできない)。

### 影響を受けた既存テストの改修(挙動不変・実装位置の追随のみ)

`er019_family_x_new_structure_wiring_01_test_01.py`の2テスト
(`test_advanced_and_standard_use_identical_retry_helper`、
`test_run_writer_stage_family_x_path_never_calls_old_split_article_
text`)は`inspect.getsource(runner.run_writer_stage)`でAdvanced/Standard
生成本体のソースを検査していたが、本体が`_run_writer_stage_once()`へ
移設されたため検査対象を追随させた(検証している性質[対称性・旧gate
不使用]自体は変更していない)。

Guardrail遵守確認(W6):
- API支出: ¥0(mock/regressionのみ)。
- Checker Prompt本体(`er003_v1_en_direct_vfl_01_generate.py`の
  `DEVIATION_PROMPT_TEMPLATE`/`HOOK_AWARE_DEVIATION_PROMPT_TEMPLATE`/
  `DEVIATION_FLAG_KEYS`)は本委任で一切編集しておらず、sha256を
  `er019_family_x_ja_recheck_retry_01_test_01.py`で既知値と一致確認
  (変更前後不変)。
- JA Writer Prompt本文(`R0_PROMPT`/`DEVELOPER_MESSAGE`/
  `REVISION_INSTRUCTIONS`/`CONCRETENESS_CONTROL_AN3_BLOCK`)も無変更
  (`original_must_fix`は既存`build_must_fix_block`機構への引数追加の
  み)。
- Ledger/Deviation severity設計・Family A/B/C/Z経路・共有`vfl01`の挙動
  は無変更。

## 9-E2E-run03. Phase C再開(E2E run_03、委任_12、2026-09-29、案B有効
での実発火・Hormuz再STOP)

案B(§9-W6)をarm(`storyline_b3/fact_selection_evidence.json`をrun_02/
an3_t0_wiring_regression_01から複製、sha256一致確認済み)した状態で
run_03を実発火した。Hormuz JA生成(Production JA経路、¥4.018、
`concreteness_an3_block_sha256`run_02と一致)→English Advanced writer段
で1回目のja_source MAJOR(HF-009関連、changed_causality)を検知し案Bが
自動発動、JA Writer Oを1回だけ再生成(`outcome=REGENERATED`)→Advanced
再実行は`LEDGER_COMPLIANT`で完成(article.md/parts.json保存)→Standard
(A2)生成でHF-009関連の**別のja_source MAJOR**(changed_scope)が新規
発生→案Bの1回上限により2回目のJA再生成は行わずfail-closedでSTOP
(`outcome=STILL_MAJOR_AFTER_RECHECK`)。`_11`委任のテスト
`test_ja_source_major_persists_after_recheck_then_stops_no_second_
regeneration`が想定した挙動と、実運用(モックなし・実API)の結果が
完全に一致することを確認した(設計どおりの安全装置が実データで機能)。

Audio段・Gate 13+9項目・ユーザー指定Gate 3項目・試聴ページはHormuz/Meta
双方とも未到達。Metaは1記事ずつ完結原則によりHormuz未完了のため着手
していない(storyline_b3/research_ledgerはrun_03向けに複製・sha256
確認済みで着手可能な状態のまま待機)。コード・Prompt変更は本委任では
実施していない。詳細ログ・費用実測(run_03累計¥10.35、本管理ID全体
累計約¥16.40)・Next Actionは`FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_
REPORT.md`§E2E run_03参照。

## 9-E2E-meta-run03. Phase C継続(E2E Meta run_03、委任_13、2026-09-29、
Hormuz deferred・Metaのみ実発火・Standard/Advanced完成)

ユーザー指示によりHormuz(run_01〜03、3回ともja_source MAJOR起因で
Standard段STOP)はdeferred/non-blockingとして保留し、Standard側
must-fixルール新設・JA再生成回数追加・Checker Prompt/severity/origin
判定変更を一切行わずMetaのみを実行した。JA生成(¥3.487、must-fix
retry 1回で`LEDGER_COMPLIANT`)→Writer段(Advanced初回`LEDGER_COMPLIANT`、
案B不要。Standard 1回目MAJOR[origin=translation、ja_source起因ではない]
→既存must-fix retry 1回で`LEDGER_COMPLIANT`)→Audio段
(scaffold/tts/assemble/player、¥23.98)まで完走し、Standard/Advanced
両方の完成podcast(mp3)・Gate 13+9+ユーザー指定Gate 3項目 全PASS・
試聴ページ(GitHub Pages公開確認7項目PASS)まで到達した。Meta E2E合計
¥31.68(本管理ID累計約¥48.08)。

**発見事項(コード変更なし、コピーのみで対処)**: `er019_family_x_audio_
production_runner_01.py`の`source_dir`は`--slug`/`--run`から
`er019_output/{slug}/{run}`として導出され、JA/writer段の出力先
(`er019_output/family_x_refresh_e2e_01/{slug}/{run}`)とはパスが異なる。
本委任ではresearch_ledger/storyline_b3コピー運用と同じ手法(ファイル
コピーのみ、コード非変更)で対処した。Hormuz再開時にも同じコピー手順が
必要になる。

詳細(Gate表・Pages 7項目・費用A/B・Closeout 10項目)は
`FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_REPORT.md`§E2E Meta run_03
参照。試聴URL: https://shimomura055.github.io/eigo-radio/user_test/family_x_refresh_e2e_01/index.html
