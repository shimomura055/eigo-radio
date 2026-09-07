# PM-LANE-A-PRODUCTION-WIRED-FINAL-ACCEPTANCE-AUDIT-01

読み取り専用監査(実装担当Sonnetとは独立)。ファイル編集・git add/commit・API呼び出し・
音声生成は一切行っていない。`run_project_regression.py`のみ実行(unittest discover禁止、
実APIを呼ぶテストは実行しない指示を遵守。3件の新規テストファイルはソース確認の上、
API呼び出しがモック/既存evidence読み込みのみであることを確認してから実行した)。

対象: OPEN-122(commit `3297d1b`)、OPEN-121(commit `e6c2f37`)、OPEN-123(commit `9f25f7d`)。
現在のローカルHEAD/origin/mainは3件とも`9f25f7d`で一致(main反映済み、証跡は本文8参照)。

---

## OPEN-122-CONNECTED-SPEECH-EQUIVALENCE-LAYER-PRODUCTION-WIRING-01(commit 3297d1b)

### 1. Production正式初回pathへの配線

**確認済み**。呼び出し連鎖をコードで実際に追った(行番号は現HEAD時点)。

- [er003_v1_n3_01_tts_generate.py:748-749](file:///C:/Users/tensh/eigo-radio/er003_v1_n3_01_tts_generate.py)(B1、`generate_b1_segments()`)・
  [同867-868](file:///C:/Users/tensh/eigo-radio/er003_v1_n3_01_tts_generate.py)(A2、`generate_a2_segments()`):
  `enable_connected_speech_equivalence_layer=(name in ("full_story_part1","full_story_part2","point_one","point_two"))`。
  対象4segmentのみ`True`、他(`in_one_line`・見出し・Key Phrase・日本語)は渡されないため既定`False`。
- A2側は[er003_v1_n3_01_tts_generate.py:233-237](file:///C:/Users/tensh/eigo-radio/er003_v1_n3_01_tts_generate.py)
  `generate_a2_segment_with_slowdown()`が`generate_english_segment_with_fallback()`へ転送。
- [er003_v1_crosslevel_audio_02_common.py:99-103](file:///C:/Users/tensh/eigo-radio/er003_v1_crosslevel_audio_02_common.py)
  `generate_english_segment_with_fallback()`が`generate_narration_snippet_verified_strict()`へ転送(standard経路)。
  fallback[minimal instruction]経路にも[同131-135](file:///C:/Users/tensh/eigo-radio/er003_v1_crosslevel_audio_02_common.py)
  で`evaluate_attempt_with_cascade(enable_connected_speech_equivalence_layer=...)`が直接渡る。
- [er003_v1_repro01_main_generate.py:274-279](file:///C:/Users/tensh/eigo-radio/er003_v1_repro01_main_generate.py)
  `generate_narration_snippet_verified_strict()`が`secondary_asr.evaluate_attempt_with_cascade(text, asr_text, ...,
  enable_connected_speech_equivalence_layer=enable_connected_speech_equivalence_layer, detail_out=cascade_detail)`
  を呼ぶ(実際に`True`が渡る箇所)。
- [er006_secondary_asr_01.py:518-519](file:///C:/Users/tensh/eigo-radio/er006_secondary_asr_01.py)
  `evaluate_attempt_with_cascade_detail()`内のゲート条件
  `if (not verified and cascade_enabled and enable_connected_speech_equivalence_layer and
  cls.classification == "TRUE_CONTENT_MISMATCH" and cls.protected.passed):`。
- Key Phrase経路(`generate_key_phrase_component_verified`、
  [er003_v1_repro01_main_generate.py:634-650](file:///C:/Users/tensh/eigo-radio/er003_v1_repro01_main_generate.py))は
  `enable_connected_speech_equivalence_layer`を一切渡していないことをソース上直接確認(Trial専用pathへの
  誤配線ではなく、既存Production初回path=`evaluate_attempt_with_cascade_detail()`への正規配線)。

### 2. retry/regeneration/fallback/Human Review Lock/Cost Guardとの整合

**確認済み**。

- 新分類`CONNECTED_SPEECH_EQUIVALENCE_ACCEPT`/`PASS_WITH_WARNING`は
  [er006_preprod_hardening_01_validation.py:751-775](file:///C:/Users/tensh/eigo-radio/er006_preprod_hardening_01_validation.py)
  `VALID_CLASSIFICATIONS`へ追加済み。
- `should_stop_retrying()`/`evaluate_attempt()`
  ([同1015-1055](file:///C:/Users/tensh/eigo-radio/er006_preprod_hardening_01_validation.py))は
  `should_pass`真偽値のみで早期returnする設計のため、新分類が未知分類として誤って
  reject/ループし続けることはない。
- [er011_human_review_lock_01.py](file:///C:/Users/tensh/eigo-radio/er011_human_review_lock_01.py)
  (Cost Guard・Human Review Lock・`save_tts_attempt_audio`本体)は`classification`文字列を
  **一切参照していない**(grep 0件)。retry/Cost Guard/Human Review Lockはstatus/verified/attempt回数
  のみで判断するため、新分類ラベルが安全装置に対して不透明であることを確認した。
- [er006_secondary_asr_01.py:612-617](file:///C:/Users/tensh/eigo-radio/er006_secondary_asr_01.py)
  `cascade_eligible = is_entity_like_mismatch(cls) or is_homophone_candidate_mismatch(cls)`は
  Equivalence Layer accept時点で`verified=True`のため`if verified or ...: return result`で
  早期returnし、既存4-step cascade(entity/homophone判定)には一切到達しない(独立性確認済み)。

### 3. Runtime evidence

**確認済み**。`er011_output/open122_connected_speech_equivalence_layer_production_wiring_01/`配下の
[gate3_a2_flagship_result.json](file:///C:/Users/tensh/eigo-radio/er011_output/open122_connected_speech_equivalence_layer_production_wiring_01/gate3_a2_flagship_result.json)・
[gate3_negative_control_result.json](file:///C:/Users/tensh/eigo-radio/er011_output/open122_connected_speech_equivalence_layer_production_wiring_01/gate3_negative_control_result.json)を
実際に開き、Report §2/§4の記述(classification・カテゴリA/B/C・corroboration 2/0・N1/T2N4の
非accept理由)と完全一致することを確認した。B1 Part Bの「合成fallthrough」は
Report内で「合成」と明記されており、誤解を招く表記はない。

### 4. regression/validator/integration test

**確認済み(件数不一致1件を除く)**。`run_project_regression.py`を実際に実行し、最新状態
(3コミットすべて反映後)で`collected=2157 passed=2154 failed=3 errors=0`を再現した
(実行ログ: 本監査でのローカル再実行、詳細は本Reportの共通§参照)。failed 3件は
`er003_test_p2j_investigate.py`内の3テスト(件数照合arithmetic、pre-existing/既知)のみで、
音声/ASR無関係と確認。`er003_test_bad`のFAILは`er003_test_p2j_investigate`が動的に
生成する一時ファイル(`tmp*/er003_test_bad.py`)内の意図的self-checkであり、outer regression
の`collected`数には含まれない(ネストした別プロセスのstdout)。3件のReportがいずれも
「`er003_test_bad`の意図的self-check・`er003_test_p2j_investigate`のOPEN-77既知meta-test集計」
と表現している内容は実態と整合。

`er011_connected_speech_equivalence_layer_production_wiring_01_test_01.py`は16件の
平文function形式test(`unittest.TestCase`ではない)で全て存在し、モック/既存保全済みevidence
読み込みのみ(実API呼び出しなし)であることをソース確認の上、実際に実行し16/16 PASSを
確認した(OPEN-122 Report §6の「16件全PASS」と一致)。

### 5. actual model_id/ASR routing/TTS mode

**確認済み**。`gate3_a2_flagship_raw_usage_log.jsonl`(azure-speech-stt)・
`gate3_b1_raw_usage_log.jsonl`(gemini-2.5-pro-preview-tts/gpt-4o-mini-transcribe/
azure-speech-stt、`tts_execution_mode=STANDARD`)・`gate3_negative_control_raw_usage_log.jsonl`
(azure-speech-stt×2)を確認し、Report §7の記述と一致。

### 6. CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS

**確認済み(ステータス表記に不一致あり)**。3ファイルともOPEN-122エントリが存在し、
承認範囲(A2/B1英語本文segmentのみ)の記述も一致。Dangling reference(存在しないファイル名・
関数名)は見つからなかった。**不一致**: `OPEN_ITEMS.md`/`CURRENT_SPEC.md`は依然
`CODE_COMPLETE_PENDING_COMMIT`/「Git操作は未実施」のまま(commit前提の文言)だが、
実際には既にcommit・main反映済み(§7参照)。commitメッセージ自体は既に
「PRODUCTION_WIRED」と宣言している一方、SSOT側のステータスフィールドは未更新
(post-commitのフォローアップ編集が抜けている、Fable側の積み残しと推定)。

### 7. Git

**確認済み**。`git show --stat 3297d1b`のファイル一覧とReport §10の一覧は一致
(新規5点・既存編集9点、抜け漏れなし)。`git log origin/main -1`と`git rev-parse HEAD`が
`9f25f7d`(3件とも含む最新)で一致、main反映済み。

### 8. ユーザー承認内容と実挙動の一致、scope外項目の混入なし

**確認済み**。Key Phrase経路(`generate_key_phrase_component_verified`、
[er003_v1_repro01_main_generate.py:634-650](file:///C:/Users/tensh/eigo-radio/er003_v1_repro01_main_generate.py))が
新規フラグを一切渡さないことをソース上直接確認。日本語経路(`er007_ja_secondary_asr_01.py`)は
本Equivalence Layerモジュールを一切importしていない(grep確認)。A2 slowdown後の
独立再検証経路(`apply_a2_slowdown_postprocess`)への未配線ギャップは
[er003_v1_n3_01_tts_generate.py:197-202](file:///C:/Users/tensh/eigo-radio/er003_v1_n3_01_tts_generate.py)の
コードコメント自体にも明記されており、Report §1/§12の記述と整合。なお「2026-09-07ユーザーが
`APPROVED_FOR_PRODUCTION`と決定した」という承認行為そのものは、DECISION_LOG.md内の
自己言及以外に本監査でアクセス可能な独立記録(会話ログ等)が無く、一次証拠での直接確認は
本監査の範囲外(コード配線がその承認範囲の記述と矛盾しないことまでは確認済み)。

**総合判定: 受入可**(SSOTステータス表記のstaleさは軽微な記録上の不一致であり、
Production安全性・配線範囲そのものには影響しない)。

---

## OPEN-121-TTS-REPETITION-QA-PRODUCTION-WIRING-01(commit e6c2f37)

### 1. Production正式初回pathへの配線

**確認済み**。同一の4segmentループ条件式
`enable_repetition_qa=(name in ("full_story_part1","full_story_part2","point_one","point_two"))`を
[er003_v1_n3_01_tts_generate.py:753-754](file:///C:/Users/tensh/eigo-radio/er003_v1_n3_01_tts_generate.py)(B1)・
[同872-873](file:///C:/Users/tensh/eigo-radio/er003_v1_n3_01_tts_generate.py)(A2)で確認。
[er003_v1_repro01_main_generate.py:286-287](file:///C:/Users/tensh/eigo-radio/er003_v1_repro01_main_generate.py)
`rep_gate = repetition_qa.apply_repetition_qa_gate(verified, out_path, text, language="en",
enabled=enable_repetition_qa)`が実際に`apply_repetition_qa_gate()`へ到達する箇所。
fallback経路にも[er003_v1_crosslevel_audio_02_common.py:142-143](file:///C:/Users/tensh/eigo-radio/er003_v1_crosslevel_audio_02_common.py)
で同様のゲートが配線されている。Key Phrase経路には一切渡らないことを
[er003_v1_repro01_main_generate.py:634-650](file:///C:/Users/tensh/eigo-radio/er003_v1_repro01_main_generate.py)で確認。

### 2. retry/regeneration/fallback/Human Review Lock/Cost Guardとの整合

**確認済み**。[er011_open121_repetition_qa_production_01.py:345-364](file:///C:/Users/tensh/eigo-radio/er011_open121_repetition_qa_production_01.py)
`apply_repetition_qa_gate()`は既存`dq18.apply_disfluency_gate()`と同一のANDゲート
(`verified and not evidence["flagged"]`)。flag時は`verified=False`をそのまま返すだけで、
新規retry機構・新規Cost Guard予算を追加していないことをコードで確認(既存の
`generate_narration_snippet_verified_strict()`のattemptループ内でverified=Falseとして
既存retryへ自然に合流する設計、`er011_human_review_lock_01.py`も`classification`を
参照しないため本ゲートの追加が安全装置を迂回する経路にはならない)。

### 3. Runtime evidence

**確認済み**。`known_positive_negative_result.json`の`tp="3/3"`/`fp="0/10"`、
`positives`内の3件(`real_point_two_buggy`: A+D検知・D'非検知、
`real_in_one_line_buggy`: A+D検知・D'非検知、`real_b1_fsp1_falsestart_partial_word`:
D'のみrun長0.74秒で検知)がReport §3(a)の記述と完全一致。`negatives`10件全て
`flagged=False`(FP 0/10、Report記載のsegment名一覧とも一致)。
`theme2_b1_fsp1_regen/run_summary.json`もReport §3(c)の記述
(attempt1 OK・verified true・repetition_qa flagged=false・D' run長0.33秒)と一致。

### 4. regression/validator/integration test

**確認済み**。新規`er011_open121_repetition_qa_production_wiring_01_test_01.py`は
`unittest.TestCase`形式26件で、実際に`loadTestsFromModule()`で件数を確認(26件、
Report記載と一致)。`run_project_regression.py`の最新実行(collected=2157)から逆算すると、
OPEN-122時点(16件の平文テストが未収集のためcollected=2112)→OPEN-121時点
(+26件のTestCase形式が新規収集され2138)→OPEN-123時点(+19件で2157)という
増分が算術的に整合し、「OPEN-122の姉妹テストが平文function形式で回帰収集されなかった」
というOPEN-121 Report自身の指摘(既知gap)が正しいことを実測で裏付けた。

### 5. actual model_id/ASR routing/TTS mode

**確認済み**。`theme2_b1_fsp1_regen/raw_usage_log.jsonl`で
`gemini-2.5-pro-preview-tts`(input 570/output 1050 tokens、`tts_execution_mode=STANDARD`)・
`gpt-4o-mini-transcribe`(input 420/output 127 tokens)を確認、Report §7の数値と一致。
[er003_v1_sing01_news_tail_fix.py:58](file:///C:/Users/tensh/eigo-radio/er003_v1_sing01_news_tail_fix.py)
`@review_lock.guarded_generate("en")`デコレータの存在を確認し、Report §5の
「既存guardされた実関数を直接呼んだ」という主張(Review Lock/Cost Guardを実際に経由)を
コードで裏付けた。

### 6. CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS

**確認済み(OPEN-122と同じステータス不一致あり)**。OPEN-121行のスコープ記述
(A+D+D'をA2/B1英語本文4segmentへ、スペクトル計算統合、境界monitoring、gap<0.5秒は
Open Item、B1 FSP1再生成evidence)は実装内容と一致。ステータスは
`CODE_COMPLETE_PENDING_COMMIT`のまま更新されておらず(OPEN-122と同一の不一致)。

### 7. Git

**確認済み**。`git show --stat e6c2f37`のファイル一覧とReport §10は一致(新規4点・
既存編集4点)。Report §11で「本タスクと無関係な既存差分(`er006_preprod_hardening_01_
validation.py`のOPEN-123関連変更、他タスクによる既存dirty state)を確認したが編集・
stageしていない」と記録されている点も、実際のcommit差分に無関係ファイルの混入がない
ことと整合。

### 8. ユーザー承認内容と実挙動の一致、scope外項目の混入なし

**確認済み**。新規テスト`ProductionScopeSourceInspectionTests`クラス
(`inspect.getsource`によるKey Phrase/日本語/A2 Comment経路の非影響確認)の存在・
アサーション内容を確認。gap<0.5秒(方式C-v2)・A2 slowdown後再検証経路・
Secondary ASR窓検知は「未配線」として正直に記録されている(§8参照、隠蔽なし)。

**総合判定: 受入可**(SSOTステータス表記のstaleさのみ、OPEN-122と同一の軽微な不一致)。

---

## OPEN-123-TRANSCRIPT-STYLE-NORMALIZATION-PRODUCTION-WIRING-01(commit 9f25f7d)

### 1. フラグなし共通層であることの確認

**確認済み**。[er006_preprod_hardening_01_validation.py:952-1004](file:///C:/Users/tensh/eigo-radio/er006_preprod_hardening_01_validation.py)
`classify_asr_match()`自体が薄いラッパーへ変更され、既存分類本体は同ファイル794行の
`_classify_asr_match_core()`へリネームされているのみで中身は変更されていないことを
確認。`classify_asr_match()`を呼ぶ全既存経路(A2/B1本文・Key Phrase英語経路・
homophone/数字ゲート・OPEN-122 Equivalence Layer)へopt-inフラグ無しで共通適用される
設計であり、これはユーザー承認範囲(英語ASR照合経路全体、Key Phrase英語経路を含む)
と一致する。

### 2. retry/regeneration/fallback/Human Review Lock/Cost Guardとの整合

**確認済み**。新分類`TRANSCRIPT_STYLE_NORMALIZED_MATCH`は`should_pass=True`/
`should_retry=False`で即座に`evaluate_attempt()`(1049-1055行)がreturnするため、
`should_stop_retrying()`のロジックにすら到達しない安全側の設計。`VALID_CLASSIFICATIONS`
へ追加済み。Cost Guard/Human Review Lockが`classification`文字列を参照しないことは
OPEN-122監査時に確認済み(共通)。

### 3. Runtime evidence

**確認済み**。`gate_a_trial08_p3_result.json`(3/3救済、`cascade_invoked: false`)・
`gate_d_wanna_result.json`(`TRUE_CONTENT_MISMATCH`のまま非救済)・
`gate_c_key_phrase_result.json`(実データ5件は`verified: true`のまま変化なし、
合成2件は「合成」と明記の上で救済/非救済とも想定通り)を実際に開き、
Report §3の記述と完全一致することを確認した。

### 4. regression/validator/integration test

**確認済み(直接実行テーブルの件数に不一致2件)**。`run_project_regression.py`実行で
`collected=2157 passed=2154 failed=3 errors=0`を再現し、Report §4の数値と一致。
新規`er011_transcript_style_normalization_production_wiring_01_test_01.py`は
`loadTestsFromModule()`で19件と確認(Report記載と一致)。

**不一致(内容)**: Report §4の「直接実行で確認した関連テスト」表のうち2件が
実際のファイル内容と食い違う。
- `er011_connected_speech_equivalence_layer_production_wiring_01_test_01.py`:
  Report記載「8」だが、実際には`def test_`が16件存在し(`__main__`ブロックでも
  16件呼び出し)、本監査で実行して16/16 PASSを確認した(OPEN-122 Reportの
  「16件」の方が正しい)。
- `er006_secondary_asr_01_test.py`: Report記載「9」だが、実際には`def test_`が
  29件存在し(`__main__`ブロックでも29件呼び出し)、OPEN-122 Reportの
  「29件」の方が正しい。

いずれもOPEN-123タスク自身が変更したファイルではなく(commit 9f25f7dの変更対象
ファイル一覧に含まれない)、実行結果自体(全PASS)に誤りはないが、Report内の
件数表記に転記ミスがある。Production安全性・配線範囲には影響しないが、
SSOT記録の正確性の観点でFableへの修正報告事項として記録する。

### 5. actual model_id/ASR routing/TTS mode

**確認済み**。`er011_output/open123_transcript_style_normalization_production_wiring_01/`
配下にraw_usage_log相当のファイルが存在せず(TTS/ASR呼び出しゼロ)、各evidence json内の
`cascade_invoked: false`と合わせてReport §5「cost実測¥0」の主張と整合。

### 6. CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS

**確認済み(同一のステータス不一致あり)**。OPEN-123行のスコープ記述
(標準contraction展開のみ採用・wanna系不採用・Key Phrase英語経路を含む)は
実装と一致。ステータスは他2件と同様`CODE_COMPLETE_PENDING_COMMIT`のまま。

### 7. Git

**確認済み**。`git show --stat 9f25f7d`のファイル一覧とReport §7は一致(新規2点・
既存編集4点)。「日本語経路・OPEN-121担当ファイルは一切編集していない」という
Report末尾の主張も、commit差分に該当ファイルが含まれないことで裏付けられる。

### 8. ユーザー承認内容と実挙動の一致、scope外項目の混入なし

**確認済み**。Key Phrase英語経路は「共通層のため適用される」(範囲内)という
Reportの記述どおり、`classify_asr_match()`が全英語経路で共通に動くコードになって
おり、Key Phrase経路を除外する新規条件分岐は存在しない(意図通り)。日本語経路
(`er007_ja_asr_validator_01.py`等)は`_classify_asr_match_core()`/`classify_asr_match()`
を呼ばない別モジュールであり、本変更の影響を受けない設計であることをコード構造上
確認した。

**総合判定: 受入可**(件数表記の転記ミス2件は記録訂正が望ましいが機能・安全性には
影響しない、SSOTステータスのstaleさはOPEN-121/122と同一)。

---

## 総合判定

**3件とも受入可**。Production正式初回pathへの配線・既存retry/Cost Guard/Human Review Lock
との非干渉・Runtime evidenceの自己申告との一致・regression無回帰・SSOT記載範囲の一致は、
いずれもコード・evidence json・git履歴・実行ログの一次証拠で確認できた。false accept増加を
招く経路(新分類が誤ってexisting安全装置をバイパスする経路)は見つからなかった。

**不足あり(軽微、Production採用の可否そのものには影響しない)**:
1. `CURRENT_SPEC.md`/`OPEN_ITEMS.md`の3件のステータスフィールドが、実際にはcommit・
   main反映済みであるにもかかわらず`CODE_COMPLETE_PENDING_COMMIT`/「Git操作は未実施」の
   まま未更新(commitメッセージ自体は`PRODUCTION_WIRED`と宣言済みで矛盾)。Fableによる
   post-commitのSSOTステータス更新が必要。
2. OPEN-123 Report §4の直接実行テーブルに件数の転記ミス2件
   (`er011_connected_speech_equivalence_layer_production_wiring_01_test_01.py`
   8→正しくは16、`er006_secondary_asr_01_test.py` 9→正しくは29)。実行結果(全PASS)
   自体は正しい。
3. 「2026-09-07ユーザーが`APPROVED_FOR_PRODUCTION`と正式決定した」という承認行為自体は、
   DECISION_LOG.md内の各Reportからの自己言及以外に本監査で独立確認できる一次記録
   (会話ログ等)が無く、確認範囲外(コード実装がその記述範囲と矛盾しないことのみ確認済み)。

---

## er006_output系4ファイルの未commit差分分類

`git status`で検出された以下4ファイルの未commit差分を内容確認した。

| ファイル | 差分内容 | 発生源(推定) | 分類 |
|---|---|---|---|
| [er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl](file:///C:/Users/tensh/eigo-radio/er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl) | 1件追加(`timestamp=2026-09-07T18:01:34`、canonical_text="Another Voice: The freedom to move."、`wav_path=er012_output/editorial_b_voices_trial_09_audio/...`) | **Lane B(EDITORIAL-B-FAMILY-VOICES-TRIAL-09)由来**。OPEN-121/122/123いずれの案件のcanonical_text・wav_pathとも一致しない | 検証副産物(別タスク由来)。OPEN-121/122/123のcommitとは無関係、今回3件のcommitにも実際に含まれていない(git show --stat確認済み) |
| [er006_output/master_audio_store_01/manifest.json](file:///C:/Users/tensh/eigo-radio/er006_output/master_audio_store_01/manifest.json) | 新規24件のmaster_audio_idエントリ | 全件のaudio_pathが`er011_output/open112_trend_theme2_b_full_audio_trial_13/...`等、**2026-09-05のタイムスタンプを持つ既存タスク(Theme2 B Full Audio Trial-13/Voices Trial-08・09/KeyPhrase Display Trial-02/Theme2 B Final Rerun-02)由来** | 検証副産物(別タスク由来、OPEN-121/122/123実行[2026-09-07]より前の既存dirty state) |
| [er006_output/master_audio_store_01/reuse_telemetry.jsonl](file:///C:/Users/tensh/eigo-radio/er006_output/master_audio_store_01/reuse_telemetry.jsonl) | 新規99件のreuse/generatedイベント | 全件`out_path`をgrepしたがOPEN-121/122のevidence出力パス(`open121_tts_repetition_qa_production_wiring_01`/`open122_connected_speech_equivalence_layer_production_wiring_01`)は0件ヒット。タイムスタンプは2026-09-05 10:42〜12:52 UTC(上記manifest.jsonと同一発生源) | 検証副産物(別タスク由来) |
| [er006_output/pronunciation_ledger_01/ledger.json](file:///C:/Users/tensh/eigo-radio/er006_output/pronunciation_ledger_01/ledger.json) | 1件追加(`updated_at=2026-09-07T18:01:34`、surface="another voice") | human_review_queue.jsonlと同一timestamp・同一内容 → **Lane B Voices Trial-09由来** | 検証副産物(別タスク由来) |

**判定**: 4ファイルとも、OPEN-121/122/123のRuntime evidence実行(実生成はいずれも
`er011_output/open12x_*/`配下の隔離ディレクトリのみへ出力、B1本文segment生成は
Master Audio Store/pronunciation ledgerを経由しない設計)からは一切生成されていない
ことを確認した。OPEN-121 Report §11の「本タスクと無関係な既存差分を確認したが
編集・stageしていない」という記載は事実と一致している。これら4ファイルの差分は
別タスク(Lane B Voices Trial-08/09、OPEN-112 Theme2 Full Audio Trial-13、KeyPhrase
Display Trial-02)の未commit成果物であり、**今回3件の受入監査の対象外**。commit候補
とするかはそれぞれの発生源タスクの正式closeout時にFableが判断すべき事項であり、
今回のLane A 3件のcommitに含める合理性はない(実際、3件のcommitにも含まれていない)。

---

## 実行した検証コマンド(参考)

- `git log --oneline -15` / `git show --stat <commit>` / `git status` /
  `git rev-parse HEAD origin/main` / `git diff -- <path>`
- `.venv/Scripts/python.exe run_project_regression.py`(2回、うち1回`--json-summary`付き)
  → `collected=2157 passed=2154 failed=3 errors=0`(3コミット反映後の現状態)
- `.venv/Scripts/python.exe er011_connected_speech_equivalence_layer_production_wiring_01_test_01.py`
  (ソース確認の上、実API呼び出しがないことを確認してから実行) → 16/16 PASS
- `unittest.defaultTestLoader.loadTestsFromModule()`による件数直接確認(実行はせず件数のみ、
  対象: OPEN-121/OPEN-123の新規テストファイル、`er011_tts_attempt_audio_retention_wiring_01_test.py`、
  `er011_keyphrase_en_asr_false_rejection_cascade_prod_wiring_01_test_01.py`、
  `er007_ja_secondary_asr_01_test.py`、`er011_human_review_lock_01_test_01.py`)
