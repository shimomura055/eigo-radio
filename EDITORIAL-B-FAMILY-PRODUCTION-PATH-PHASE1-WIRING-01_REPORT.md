# EDITORIAL-B-FAMILY-PRODUCTION-PATH-PHASE1-WIRING-01 報告書

**管理ID: EDITORIAL-B-FAMILY-PRODUCTION-PATH-PHASE1-WIRING-01**
**種別: Phase 1実装(候補)。Sonnetは`PRODUCTION_WIRED`を宣言しない(Fable/ユーザー受入判定待ち)**
**作成日: 2026-09-08**

---

## 0. 背景・範囲

`EDITORIAL-B-FAMILY-PRODUCTION-PATH-DESIGN-01_REPORT.md`第5節「Phase 1」の
構成に従い、Lane B内で閉じる範囲(Editorial Type registry・Voice A/B TTS・
Tension slot対応timeline builder・Comment 1-4 Role辞書・B-Family専用
Production runner)を実装した。Phase 2(Lane A共有`build_common_block()`への
`editorial_type_module`引数追加、一人称"I"の機械的強制)は実装していない
(委任文の禁止事項どおり)。

---

## 1. 変更・新規ファイル一覧

| ファイル | 種別 | 内容 |
|---|---|---|
| `er012_b_family_editorial_type_registry_01.py` | 新規 | Editorial Type registry。Voice A/B/Narrator割当、fallback、Tension slot名、Key Phrase位置、Comment 1-4 Role確定版テキスト(FINALIZE-11全文転記)、Phase 2保留事項 |
| `er012_b_family_voices_production_01.py` | 新規 | 5区切りparser、Voice可用性チェック+fallback解決、Voice A/B本文TTS(`generate_voice_body_wide_margin`)、B-Family専用timeline builder(`build_b1_voices_timeline`) |
| `er012_b_family_production_runner_01.py` | 新規 | B-Family専用Production runner(prepare→voice_check→kp_reuse→scaffold→tts→assemble→player、resumable stage方式) |
| `er012_editorial_b_family_production_phase1_test_01.py` | 新規 | 単体テスト12件(registry内容・parserガード・voice fallback分岐・timeline契約) |
| `er003_v1_sing01_news_tail_fix.py` | **無変更** | 既存関数はvoice_name以外の全primitiveが既に汎用のため、新関数追加は不要と判断(下記2節) |
| `er003_v1_n3_01_assemble.py` | **無変更** | `build_b1_timeline()`等の既存関数は一切変更せず、新timelineは別ファイルへ追加 |
| Lane A(`er003_v1_n3_01_articles_generate.py`等) | **無変更** | Phase 2範囲、今回は一切触れていない |

**共有モジュールへは一切変更を加えていない**(新関数追加すら発生していない)。

---

## 2. 「共有primitiveをvoice指定でラップする」で完結した判断根拠

設計案は`news_tail_fix.py`への新関数追加を代替案としていたが、実コード確認の
結果、同関数が内部で呼ぶ全primitive(`common._call_tts_with_retry`・
`batch_wiring.make_batch_tts_call_fn`・`p4c.build_tts_prompt`・
`p3u.trim_english_keyword_silence`・`secondary_asr.evaluate_attempt_with_cascade`・
`dq18.apply_disfluency_gate`・`review_lock.save_tts_attempt_audio`)は、
hardcodeされているのが呼び出し側の`voice_name`引数だけで、primitive自体は
既にvoice名を受け取れる。したがって`er012_b_family_voices_production_01.py`
側でこれらを直接組み立てるだけでVoice A/B対応が完成し、`news_tail_fix.py`
自体には触れる必要がなかった。Hook(`full_story_part1/2`)・Tension
(`tension_reflection`)・Closing(`in_one_line`)は、Narrator音声(Aoede)で
既存`news_tail_fix.generate_news_narration_wide_margin()`をそのまま
(無変更で)呼んでいる。

---

## 3. Gate 3 Production Wiring Checklist充足状況

| 項目 | 状況 |
|---|---|
| Production正式初回経路 | 充足。`er012_b_family_production_runner_01.py`はTrialスクリプト(`er012_editorial_b_voices_trial_*.py`)を一切importしない |
| retry・fallback・regenerationとの整合 | 充足。既存Human Review Lock(`guarded_generate`)・TTS retry cascade・ASR Validation・disfluency gateを無変更のまま使用(overrideなし)。実行中Human Review Lockは発動せず(全segment VALIDATED) |
| DEV・Trial-onlyではないこと | 充足。実体をLane B正式ファイルへ移設、Trialファイルは参照すらしていない |
| Production runtimeでの実発火 | 充足。下記4節のとおり実行、Voice A/B TTS・Tension timeline・Comment Role・Key Phrase位置(現状維持)すべて実発火 |
| 必要testのPASS | 充足。単体テスト12件PASS(下記5節)、project-wide regression PASS(既知3件除く、下記6節) |
| runtime evidence | 充足。下記4節 |
| 実際のmodel_id・routing確認 | 確認済み。TTS: `gemini-2.5-pro-preview-tts`(`p9a.ENGLISH_MODEL_NAME`)、voice=Algieba/Erinome/Aoede/Charon。Scaffold: `routing.require_model("B1_SUPPORT", ...)`=`gpt-5.6-luna` |
| SSOT反映・Git反映 | **未実施**(本タスク範囲外、SSOT編集・Git操作禁止のため。Fable/ユーザー判断待ち) |
| approved specとProduction挙動の一致 | 一致(Voice A=Algieba/B=Erinome/Narrator=Aoede、Tension slot名「Where the Difference Comes From」、Key Phrase位置=Preview直後、Comment 1-4確定版)。一人称"I"のみPhase 2待ちで機械的未保証 |

---

## 4. Runtime evidence

入力: `er012_output/editorial_b_voices_trial_07/b1b_run02_attempt2/article.md`
(既存承認済み記事、読み取り専用)。出力:
`er012_output/editorial_b_family_production_phase1_01/`。
`TTS_EXECUTION_MODE=STANDARD`。

- **Episode**: `b1b/assembled/B_Family_Production_Phase1_B1B.wav`
  duration=312.885s、peak=0.92764、clipping=False、headroom safety valve
  適用なし(閾値0.98未満)。
- **TTS**: 14 segment、全てstatus=OK(VALIDATED)。attempts合計16回
  (`preview`・`full_story_part2`のみ2回、他は1回)。Voice A(`point_one`,
  Algieba)・Voice B(`point_two`, Erinome)ともに1回目でASR verified。
- **Voice可用性チェック**: Algieba/Erinome双方status=OK(fallback発火なし)。
- **Comment 1-4**: registryのRole辞書経由で生成。Comment 1に"the question"
  の語句出現なし(禁止句確認)。Support Ledger Deviation Check
  (既存Production`vfl01.run_deviation_check`、monitoring専用)=
  `LEDGER_COMPLIANT`。
- **Key Phrase**: 現状維持のためTrial-08既存出力をhash一致確認のうえ再利用
  (`hash_match=True`、5件)。
- **Cost**: 合計¥27.56(gemini ¥25.72 / openai ¥0.66 / openai_asr ¥1.19)、
  上限¥200に対し十分な余裕。
- **Human Review Lock**: 実行中に発動なし(`human_review_queue.jsonl`への
  新規追記は0件、既存差分は2026-09-07の別タスク由来と確認済み)。
- **player.html**: `C:\Users\tensh\eigo-radio\er012_output\editorial_b_family_production_phase1_01\player.html`
  (Gate 7標準format、`audio_review_player.py`経由)。
- **副作用(既存安全装置の通常動作)**: `er011_output/attempt_history.jsonl`
  へTTS attempt保存機構が自動追記(本タスクは内容編集していない、報告のみ)。

**実装中に発見・修正した不整合**: 初回実行時、`in_one_line`を
`disfluency_qa`既定値(False)のまま呼び出したため
`asm.verify_episode_audio_validation_gate()`が
`MISSING_MANDATORY_DISFLUENCY_QA`でAssemblyをブロックした(Gate機構が
正しく機能した実例)。既存A-Family Production(`er003_v1_n3_01_tts_generate.py`
744行目)と同じ規約(`disfluency_qa=(name=="in_one_line")`)へ合わせて修正し、
`in_one_line`のみ再生成(1回追加、上記cost・attemptsに含む)してPASSした。

---

## 5. 単体テスト(`er012_editorial_b_family_production_phase1_test_01.py`)

12件全PASS: registry内容(voice/fallback/comment role/"the question"禁止句/
一人称未保証フラグ)、`split_five_voice_sections`のガード(正常系・見出し数
不一致・タイトル無し)、`resolve_voice_names`のfallback分岐3パターン、
`build_b1_voices_timeline`が既存`asm.build_b1_timeline()`を呼ばずTension/
Voice A/Bを含むこと(mock契約テスト)。

---

## 6. A-Family非影響の証拠

`run_project_regression.py`(唯一の正式回帰入口)を、本タスクの新規ファイル
「有り」「無し」の両方で実行し比較した。

| 実行 | collected | passed | failed |
|---|---|---|---|
| 新規ファイル無し(Phase1新規4ファイルを一時退避) | 2157 | 2154 | 3 |
| 新規ファイル有り(本タスク後) | 2169 | 2166 | 3 |

差分は新規テスト12件の追加のみ(2169-2157=12)。failed=3は両方で同一
(`er003_test_bad.FixtureTests.test_case_0`は意図的常時失敗fixture、
`er003_test_p2j_investigate`の履歴件数照合2件は既存の既知failure)であり、
本タスク起因の新規failureはゼロ。共有ファイル(`er003_v1_n3_01_assemble.py`・
`er003_v1_sing01_news_tail_fix.py`・Lane A)へのdiffはゼロ(`git diff --stat`
で無変更を確認)。

---

## 7. Phase 2保留部分(未実装、コメント・Reportに明示済み)

1. 一人称"I"の機械的強制(`build_common_block()`への`editorial_type_module`
   引数追加が前提)。
2. Point Overlap QA/Diagnostic Full RetryのB-Family専用扱い(monitoring専用か
   正式gate化か)。
3. Analytical Leakage Checkの正式化可否。
4. B-Family専用Writer retry上限(3回)の正式採用可否(Phase 1は記事生成
   [Writer]自体を範囲外とするため今回は無関係)。

---

## 8. 未確認事項・追加のUSER_DECISION_REQUIRED候補

1. **OPEN-121(repetition QA)/OPEN-122(connected speech equivalence layer)
   の適用範囲ギャップ**: A-Family既存Productionは`full_story_part1/2`・
   `point_one`・`point_two`でこれらを有効化しているが(`er003_v1_n3_01_tts_generate.py`
   745-754行目)、本Phase 1のHook/Tension/Closing呼び出し、および新規Voice
   A/B関数はこれらを実装していない(Trial-09と同じ状態を維持)。B-FamilyとA-Familyで
   safety feature適用に差がある状態のため、Phase 2以降での解消要否をご判断
   いただきたい。
2. Key Phrase選定(Trial-08出力の再利用)は本Phase 1の対象外としたため、
   記事とKey Phraseの整合性は既存Trial-08時点の検証に依拠している。
3. SSOT(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`)反映・Git操作は
   本タスクの範囲外、Fable/ユーザー判断待ち。

---

## 9. 修正指示1回目への対応(Fable、管理ID継続)

背景・指示内容は本Report冒頭のFable委任文のとおり。§8-1で報告した
OPEN-121/OPEN-122未適用ギャップに対し、A-Family既存Production
(`er003_v1_n3_01_tts_generate.py` 745-754行目)と**同一規約**を、対応する
B-Family本文相当segmentへ適用した。仕様拡張は行っていない(既存Production
機構の適用のみ)。

### 9-1. 適用segment表(A-Family / B-Family対比)

| A-Family segment(既存規約) | OPEN-121/OPEN-122 | B-Family相当segment | 本修正での適用 |
|---|---|---|---|
| `full_story_part1` | 有効 | Hook Part 1 (`full_story_part1`、Aoede) | **有効化(True)** |
| `full_story_part2` | 有効 | Hook Part 2 (`full_story_part2`、Aoede) | **有効化(True)** |
| `point_one` | 有効 | Voice A body (`point_one`、Algieba) | **有効化(True)** |
| `point_two` | 有効 | Voice B body (`point_two`、Erinome) | **有効化(True)** |
| `in_one_line` | 無効(disfluency_qaのみ対象) | Closing (`in_one_line`、Aoede) | 無効のまま(A-Familyと対称) |
| (A-Familyに存在しない) | — | Tension (`tension_reflection`、Aoede) | 無効のまま(A-Familyに対応segmentが無いため、独自拡張しない) |
| Comment/Preview/見出し等 | 無効 | Comment 1-4・Preview・Voice A/B見出し | 無効のまま(変更なし) |

disfluency_qaの既存規約(`in_one_line`のみTrue)はPhase 1のまま変更していない。

### 9-2. 変更ファイル・diff要約

| ファイル | 変更内容 |
|---|---|
| `er012_b_family_voices_production_01.py` | `generate_voice_body_wide_margin()`へ`enable_connected_speech_equivalence_layer`・`enable_repetition_qa`引数を追加(既定True、Voice A/B は常にA-Family 4segment集合の一員のため)。`er011_open121_repetition_qa_production_01`をimportし、`secondary_asr.evaluate_attempt_with_cascade()`呼び出しへ`enable_connected_speech_equivalence_layer`を、ASR判定後に`repetition_qa.apply_repetition_qa_gate()`を`dq18.apply_disfluency_gate()`と同一ANDゲートパターンで追加(`er003_v1_sing01_news_tail_fix.py` 118-124行目と同一実装)。attempt_log/save_tts_attempt_audio/戻り値へ`repetition_qa_checked`/`repetition_qa_evidence`を追加。既存の`generate_voice_body_minimal_fallback`(fallback生成専用、ASR判定は行わない)は無変更。 |
| `er012_b_family_production_runner_01.py` | (1) `run_tts()`内、`news_tail_fix.generate_news_narration_wide_margin()`呼び出しへ`enable_connected_speech_equivalence_layer=(name in ("full_story_part1","full_story_part2"))`・`enable_repetition_qa=(同上)`を追加(`tension_reflection`/`in_one_line`はFalseのまま)。Voice A/B呼び出しへ`enable_connected_speech_equivalence_layer=True, enable_repetition_qa=True`を明示指定。(2) `OUT_DIR`を`editorial_b_family_production_phase1_02`へ切替(`phase1_01`は無変更のまま保持)、`BUDGET_JPY_CAP`を200→100円へ変更(委任文の費用上限指示に合わせる)。 |
| `er012_editorial_b_family_production_phase1_test_01.py` | `VoiceBodySafetyFeatureDefaultsTests`(1件、シグネチャ既定値検査)・`RunTtsBodySegmentSafetyFeatureContractTests`(1件、`run_tts()`を全生成関数モック化して実行し、Voice A/B・Hook part1/2は両フラグTrue、Tension/Closingは両フラグFalseで呼ばれることを検証する契約テスト)を追加(既存12件は無変更)。 |
| 共有ファイル(`er003_v1_*`・`er011_*`・`er006_*`) | **無変更**(`git diff --stat`で確認済み)。 |

### 9-3. 単体テスト

`er012_editorial_b_family_production_phase1_test_01.py`: 14件全PASS
(既存12件+新規2件)。

### 9-4. project-wide regression(`run_project_regression.py`、唯一の正式入口)

`collected=2171 passed=2168 failed=3 errors=0 skipped=0`
(本タスク前2169件から新規テスト2件増、既存12件+今回2件=14件が
今回collectionに含まれる)。failed=3は
`er003_test_p2j_investigate`の3件(`test_combined_equals_sum_of_er002_and_er003`・
`test_p2h_reported_count_matches_er002_plus_er003_at_that_time`・
`test_p2i_reported_count_matches_er003_at_p2i_era`、履歴件数照合の既知
failureで本タスク以前から存在)のみで、本タスク起因の新規failureはゼロ。
(ログ中に一時的に現れる`er003_test_bad.FixtureTests.test_case_0`のFAILは、
`run_project_regression.py`自身の discovery ロジックを検証するmeta-testが
一時ディレクトリへ動的生成するfixtureの内部実行結果であり、top-level
2171件には含まれない。)

### 9-5. Runtime evidence再取得(`er012_output/editorial_b_family_production_phase1_02/`)

入力記事は`phase1_01`と同一(`er012_output/editorial_b_voices_trial_07/b1b_run02_attempt2/article.md`、読み取り専用)。既存の一般目的音声再利用機構(Key
Phrase専用のhash一致コピー以外)は見当たらなかったため、Voice A/B・Hook/
Tension/Closingを含む全body segmentは再生成した(byte-for-byte再利用は
不採用、理由は本節末尾)。`TTS_EXECUTION_MODE=STANDARD`、予算上限¥100
(`BUDGET_JPY_CAP`)。

- **TTS**: 14 segmentのうち13segmentはstatus=OK(1回目でASR verified、
  `point_one`/`full_story_part1`/`full_story_part2`はrepetition_qa_checked=True・
  flagged=False・connected_speech_info=None、すなわち安全機構が実発火し
  問題なく通過)。`tension_reflection`/`in_one_line`はrepetition_qa_checked=False
  (A-Familyとの対称性どおり無効)。
- **`point_two`(Voice B、Erinome)がstatus=STOPPED(3回試行、全てrepetition_qa
  flagged=True)** → **Assembly GATE_BLOCKED**(`asm.verify_episode_audio_
  validation_gate()`、`['point_two=STOPPED']`)。既存Gate・既存retry上限
  (`PRODUCTION_MAX_TTS_ATTEMPTS=3`)を独自に回避・拡張することはせず、
  ここでSTOPして報告する(Human Review Lock自体は不発火、
  `er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`は
  実行前後とも31件で変化なし。ただし別経路のGate=`STOPPED`終端状態が
  Assemblyをブロックした)。
  - **原因調査(evidence)**: `point_two`本文には著者が意図的に配置した
    反復句"do not need"が2回出現する(`"...I do not need one fixed spot
    at the office. ... the people I need—or do not need—around me."`)。
    共有`er011_open121_repetition_qa_production_01.py`の
    `_canonical_repeat_count()`は、canonical_text側の"do not need"が
    canonicalへ何回出現するかをスペース区切りtoken一致で数えるが、
    2回目の出現がem dash(`—`、前後にスペース無し)で"need—or"・
    "need—around"のように隣接語と結合したtokenになるため、plainな
    "need" tokenとして一致せず、`canonical_repeat_count=1`(実際は2)と
    誤カウントされる。一方TTS音声・ASR側では自然に区切られて発話される
    ため実際に2回検出され、`intentional=(canon_count>=2)`がFalseとなり
    flagged=Trueが3回連続した。これは`er003_v1_n3_01_tts_generate.py`の
    `tts_safe_news_en()`にもem dash正規化が無いため、A-Familyの記事が
    同じ句読点パターンを持てば同一事象が起き得る、既存共有moduleの
    一般的な既知未対応ケースであり、本タスクのVoice A/B配線自体が原因
    ではない(共有ファイルは無変更、Gateの意味も変更していない)。
  - 既存の救済経路として`asm.record_human_approval()`(人間が実際に
    聴取してPASS判定した場合に使う既存Production機構)が存在するが、
    「承認代行はしない」との委任指示に基づき、Sonnet側では一切使用
    していない。
- **Cost**: 合計¥28.64(gemini ¥26.77 / openai ¥0.59 / openai_asr ¥1.27)、
  上限¥100に対し十分な余裕(`point_two`3回試行分を含む)。
- **Assembly/player.html**: 上記GATE_BLOCKEDのため生成していない
  (`run_summary_assemble.json`のstatus=GATE_BLOCKED)。episode全体の
  duration/peak/clippingは本runでは取得できていない。
- **Voice可用性**: Algieba/Erinome双方status=OK(fallback発火なし、
  `voice_resolution.json`)。
- **Key Phrase**: `phase1_01`と同じくTrial-08既存出力をhash一致確認の
  うえ再利用(`hash_match=True`、5件)。
- **byte-for-byte再利用を採用しなかった理由**: 本runnerに既存の一般目的
  音声再利用機構は無く(Key Phrase専用のhash一致コピーのみ)、`phase1_01`
  の音声ファイルをそのままコピーする専用ロジックを新たに書くことは
  「呼び出し引数・ラッパーに限定」という委任範囲を超えるため、全body
  segmentを再生成する方式を採った。

### 9-6. 新たなUSER_DECISION_REQUIRED

1. **`point_two`(Voice B)がOPEN-121配線後にGATE_BLOCKEDのままである点**:
   上記9-5の原因分析のとおり、著者の意図的な反復("do not need"が
   em dashを挟んで2回)を共有canonical-repeat-count logicが誤検出した
   ものと考えられる。以下のいずれかのご判断を仰ぎたい(Sonnetからは
   いずれも実装していない):
   (a) 実際に音声を聴取のうえ、既存`record_human_approval()`機構で
       人間承認しAssemblyを進める、
   (b) 共有module(`er011_open121_repetition_qa_production_01.py`の
       `_normalize_tokens`/`_canonical_repeat_count`)のem dash
       tokenization改善を別タスクとして起票する、
   (c) その他の対応。
   いずれの場合も、本タスクの範囲(Lane B新規ファイルのみ・共有ファイル
   無変更・Gate無効化なし)を維持したままでは`phase1_02`のepisode完成
   (Assembly/player.html)まで到達できていない。
2. 上記1が解消するまで、`phase1_02`は`PRODUCTION_WIRED`候補としての
   完全なruntime evidence(完成episodeのduration/peak/clipping・
   player.html)を提供できていない。§8-1で報告したOPEN-121/OPEN-122の
   配線自体(本文相当4segmentへの適用)は完了・単体テスト/regression
   でも確認済みであり、Gate 3のうち「retry・fallback・regenerationとの
   整合」は本runでも維持されている(既存上限を超えるretryは行っていない)。

---

## Status

**Status: IMPLEMENTED(Phase 1候補)— PRODUCTION_WIREDはFable/ユーザー受入
判定待ち。Sonnetからの宣言はしない。**

**修正指示1回目後の状態: OPEN-121/OPEN-122のB-Family本文相当segmentへの
配線は完了・単体テスト/regressionでPASS。ただしruntime evidence再取得中に
`point_two`(Voice B)がGATE_BLOCKEDとなり(§9-5・§9-6参照)、`phase1_02`の
完成episode/player.htmlは未生成。Sonnetからの`PRODUCTION_WIRED`宣言は
引き続き行わない。次の判断(§9-6)をFable/ユーザーへ仰ぐ。**
