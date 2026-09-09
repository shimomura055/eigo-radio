# HOUSEHOLD-FACT-03-PUBLISHED-ARTICLE-MINIMAL-FIX-02 実行報告

管理ID: HOUSEHOLD-FACT-03-PUBLISHED-ARTICLE-MINIMAL-FIX-02(OPEN-138、
A-FACT03-1=(a))
背景: ユーザー決定(2026-09-09)。Household公開記事(2026-08-17承認、
`er003_output/n3_01/household/{a2,b1b}/`)に含まれるFACT-03由来の誤記述を、
Numeric Precision修正(Theme 2 rerun_04、
`OPEN-112-THEME2-B1-NUMERIC-PRECISION-MINIMAL-FIX-RERUN-04_REPORT.md`)と
同じ「既存承認済みArtifactへの最小修正例外」方式で差し替える作業。
根拠: Ledger v4(`er003_output/n3_01/household/research/verified_fact_ledger.txt`
FACT-03、usable: no)。

**到達Status: STOP(Human Review Lock発動、指示された明示STOP条件に該当)**。
記事本文(text)側の修正はFact Checker PASS・Ledger Deviation COMPLIANTまで
到達済みだが、TTS再生成は完了していない。Assembly・player生成は未実施。

## 1. 該当文の一覧(全文検索、A2/B1B双方)

`article.md`・`parts.json`・Preview(`{a2,b1b}_support_texts.json`)・
`key_phrases/keywords_canonicalized.json`全てを対象に、
`strawberr*`/`citrus`/`orange`/`90 to 95`等でgrepした。

- **A2**: 一致ゼロ件(article.md/parts.json/a2_support_texts.json/
  keywords_canonicalized.json いずれにも該当文言なし)。A2の記事は元々
  「イチゴ・柑橘類=高湿度」という主張を含んでいなかった(apples/pears/
  leafy greensのみ言及)。**A2は変更対象外、コピーも行っていない**
  (`er003_output/n3_01/household/a2/`が引き続き最終成果物)。
- **B1B**: `article.md` 33行目・`parts.json`の`point_one_body`フィールド
  (完全に同一文字列)のみ1箇所。Preview(`b1_support_texts.json`)・
  Comment 1〜4・Key Phrase実出力(`keywords_canonicalized.json`)には
  一致ゼロ件(過去の生成過程プロンプトログ`audit/*`・
  `key_phrases/*_prompt.txt`には旧Ledger v2引用として残存するが、実際に
  読み上げ/表示されるcontentではないため非STOP事由、rerun_04と同一の
  取り扱い)。

## 2. 修正文(B1B point_one_body、2段階)

出力先: `er003_output/n3_01/household/fact03_fix_02/b1b/`(`b1b/`全体を
コピー後、この1文のみ書き換え。詳細diff:
`er011_output/open138_household_fact03_b1b_minimal_fix_02/textfix_diff.json`)

- **revision 1**(旧→中間案): "...Strawberries and citrus fruits,
  including oranges, prefer high humidity. UC Davis lists an ideal
  humidity of 90 to 95 percent for both..." → "...Strawberries and
  citrus fruits, including oranges, are one case. Refrigerator makers
  do not even agree on which drawer suits them best..."
  Fact Checkerでverdict=REVIEW_REQUIRED(citrus/orangesを含めての一般化が
  広すぎる、Ledger v4はイチゴのみのメーカー不一致を記録)。
- **revision 2**(最終、QA PASS): "The common shortcut—fruit in low
  humidity and vegetables in high humidity—has important exceptions.
  **Strawberries are one case: some refrigerator makers place them in
  the high-humidity drawer, others in the low-humidity one.** The
  food's behavior matters more than its category."
  citrus/orangesの言及を削除し、Ledger v4が実際に記録する範囲
  (GE=イチゴ・オレンジとも低湿度、Samsung=イチゴのみ高湿度)に厳密化。
  新しい具体的数値は一切追加していない。

## 3. QA結果(修正後の記事全体、B1B)

既存Production関数をそのまま使用(topic文字列・Ledger v4テキスト・model
[gpt-5.6-luna]はProduction本体[`er003_v1_n3_01_articles_generate.py`]と
同一であることをプログラムで突合確認済み)。

| | revision 1 | revision 2(最終) |
|---|---|---|
| Fact Checker(`er002_ja_web_research_r3.py`、web_search付き) | REVIEW_REQUIRED(unsupported_specific_claims 1件) | **PASS**(0件) |
| Ledger Deviation(`er003_v1_en_direct_vfl_01_generate.py::run_deviation_check`、hook_aware) | LEDGER_COMPLIANT(MAJOR 0) | **LEDGER_COMPLIANT**(MAJOR 0) |

revision 2はFact Checker PASS(公開時点のREVIEW_REQUIREDより厳格な結果)、
Ledger Deviation COMPLIANT。詳細:
`er011_output/open138_household_fact03_b1b_minimal_fix_02/qa_summary.json`
(revision 1は`qa_summary_revision1.json`に保存)。

## 4. TTS再生成(point_oneのみ) — Human Review Lock発動

revision 2のテキストで、既存Production関数
(`generate_news_narration_wide_margin`、
`enable_connected_speech_equivalence_layer=True`,
`enable_repetition_qa=True`、B1のpoint_one/point_twoと同一引数、
`TTS_EXECUTION_MODE=STANDARD`)を用いてnarration再生成を実行した。

3回試行、全てASR照合が`TRUE_CONTENT_MISMATCH`(原因: "the low-humidity
one"の2回目の"humidity"をTTSが省略発話し、ASRが"the low one"と書き起こす
elision。3回中3回とも同一パターンで再現)。3回目終了後、
`er011_human_review_lock_01.py`のHuman Review Lockが作動し、
`state=HUMAN_REVIEW_REQUIRED`で確定した
(`er003_output/n3_01/household/fact03_fix_02/b1b/audit/review_lock_state.json`)。

指示された明示STOP条件「Lock発動時はSTOP」に該当するため、**ここで処理を
停止**した。承認代行・追加試行・別文言への再挑戦は一切行っていない。

- `er003_output/n3_01/household/fact03_fix_02/b1b/narration/point_one.wav`
  は3回目(未検証・TRUE_CONTENT_MISMATCH)の音声のまま残っている。
  **この音声ファイルは検証未合格であり、使用不可**。
- `audit/tts_generation_results.json`は、アサーション(status=="OK")が
  書き込み前に失敗したため**未更新のまま**(旧[置換前]point_oneの記録が
  残存、データ破損なし)。
- Assembly・player.html生成は未実施(この時点でSTOP)。

## 5. 費用(実測、分離記録)

`er011_output/open138_household_fact03_b1b_minimal_fix_02/raw_usage_log.jsonl`
実測値、`er005_output/cost_baseline_01/pricing_snapshot.json`単価、
1USD=160円で計算。

- QA(Fact Checker×2回 + Ledger Deviation×2回、revision 1・2双方):
  $0.108228 ≒ **¥17.32**
- TTS(Gemini)+ASR(OpenAI)、point_one 3試行分: $0.015441 ≒ **¥2.47**
- **合計 $0.123669 ≒ ¥19.79**(上限¥60に対し実費¥19.79)

## 6. Gate 4(既存Production・新policy確認)

- 本タスクではProduction関数(`er002_ja_web_research_r3.py`・
  `er003_v1_en_direct_vfl_01_generate.py`・`er003_v1_n3_01_tts_generate.py`
  ・`er003_v1_sing01_news_tail_fix.py`・`er011_human_review_lock_01.py`)
  を一切変更していない(全て読み取り専用import)。
- 新しいpolicyは作成していない(Numeric Precision修正[rerun_04]と同じ
  「既存承認済みArtifactへの最小修正例外」を踏襲しただけ)。
- Ledgerの再改変は行っていない(v4は本タスク開始前から確定済み、本タスクは
  参照のみ)。
- Human Review Lockは既存の安全装置であり、独自判断で回避・無効化して
  いない(発動どおりSTOPした)。

## 7. player file:///パス

- **A2**: 変更なし。既存承認済み
  `er003_output/n3_01/household/a2/`をそのまま参照(本タスクでの新規
  player生成なし)。
- **B1B**: Assembly未実施のため、本タスクでの新規player.htmlは**存在しない**。

## 8. 新規/変更ファイル一覧

- 新規: `er011_output/open138_household_fact03_b1b_minimal_fix_02/`
  (`textfix.py`・`textfix_diff.json`・`qa_runtime_evidence.py`・
  `qa_summary.json`・`qa_summary_revision1.json`・
  `fact_qa_revision1.json`・`ledger_deviation_revision1.json`・
  `fact_check_attempts.json`・`deviation_full_record.json`・
  `tts_regen_runtime_evidence.py`・`point_one_regen_run_summary.json`・
  `raw_usage_log.jsonl`)
- 新規: `er003_output/n3_01/household/fact03_fix_02/b1b/`
  (`b1b/`全体をコピー後、`article.md`・`parts.json`の1文のみ書き換え
  [revision 1→2]。`fact_qa.json`・`ledger_deviation.json`はQA再実行結果
  [revision 2]で上書き済み。`narration/point_one.wav`は**未検証**、
  `audit/tts_generation_results.json`は**旧point_oneのまま未更新**、
  `audit/review_lock_state.json`は新規[`HUMAN_REVIEW_REQUIRED`]。
  `assembled/English_Your_Way_B1B_HOUSEHOLD.{mp3,wav}`は`shutil.copytree`
  によるコピー元[修正前]と完全byte一致[sha256照合済み]、**新規Assembly
  ではない**[`stage_assemble_b1`は未実行]。`player.html`は未生成)
- 不変(確認済み): `er003_output/n3_01/household/{a2,b1b}/`(元の公開済み
  Artifact、本タスクでは一切編集していない)、`CURRENT_SPEC.md`・
  `DECISION_LOG.md`・`OPEN_ITEMS.md`・`HISTORY_INDEX.md`(いずれも本タスク
  では編集していない、SSOT/Git禁止指示どおり)
- 副作用(既存Production関数がTTS/ASR呼び出し時に自動更新する共有台帳、
  タスク開始前から他タスクの変更で既に差分あり): `er011_output/
  attempt_history.jsonl`(本タスクの`point_one`試行1件[3attempt分の
  summary]追記を確認)・`er006_output/master_audio_store_01/manifest.json`・
  `er006_output/master_audio_store_01/reuse_telemetry.jsonl`・`er006_output/
  pronunciation_ledger_01/ledger.json`・`er006_output/
  audio_retry_cascade_prod_01/human_review_queue.jsonl`

## 9. USER_DECISION_REQUIRED / 次のアクション候補(実装せず提示のみ)

Human Review Lockが発動したnarration/point_one.wav(revision 2テキスト)は、
人間による試聴確認、または以下のいずれかの対応が必要:
(a) 現在のrevision 2文言のまま、人間が3回分のattempt音声
    (`narration/attempts/point_one_attempt{1,2,3}_*.wav`)を試聴し、
    ASR不一致(humidity省略)が許容範囲か判断する、
(b) さらに文言を調整する(例: "others in the low-humidity drawer instead"
    のように"low-humidity"の反復を避ける言い回しに変える)、
のいずれを取るかはユーザー/Fableの判断が必要。本タスクでは実装していない。

## 10. STOP条件該当性

- Ledger v4で裏付けできる修正文は作成できた(revision 2、Fact Checker
  PASS)ため非該当。
- Fact Checker FAIL: 非該当(revision 2はPASS)。
- **Lock発動: 該当。TTS再生成の3回目終了後にHuman Review Lockが作動し、
  ここでSTOPした。**
- 共有module変更が必要: 非該当。
- 費用超過: 非該当(¥19.79 / 上限¥60)。
- 新failure mode: 非該当(既存の安全機構[Human Review Lock]が設計どおり
  作動しただけ)。


## 11. 継続(Fable修正指示1回目、revision 3) — 到達Status: STOP(想定外のGate発見)

指示: revision2の同一文言は再生成せず、Ledger v4の範囲内で「TTSが省略
しやすい反復("the low-humidity one")」を避けた新しい文言(revision3)を
2案作成し、Fact Checker/Ledger Deviationで検証、PASSした方でpoint_oneの
TTSを再試行する。

### 11.1 revision3案と採用

- **revision3a**(採用): "...Strawberries are one case: some refrigerator
  makers put them in the high-humidity drawer, while others put them in
  the low-humidity drawer instead. The food's behavior matters more than
  its category."(「the low-humidity one」という省略誘発表現を、"one"を
  "drawer"へ書き戻す形に変更。新しい具体的事実は追加していない)
- revision3b(不採用、Fact Checker/Ledger両方PASSしたが、revision2との
  差分が大きいためminimal-fixの趣旨によりrevision3aを優先): "...some
  refrigerator makers keep them in the high-humidity drawer, but other
  brands choose the low-humidity setting instead. ..."

QA結果(両案とも): Fact Checker verdict=PASS、Ledger Deviation
overall_status=LEDGER_COMPLIANT(MAJOR 0)。詳細:
`er011_output/open138_household_fact03_b1b_minimal_fix_02/revision3_qa_results.json`。
diff: `.../textfix_diff_revision3.json`。

### 11.2 TTS再生成(point_oneのみ) — Lockは発動せず1回でPASS

`generate_news_narration_wide_margin`(前回と同一引数、
`enable_connected_speech_equivalence_layer=True`,
`enable_repetition_qa=True`, `TTS_EXECUTION_MODE=STANDARD`)を実行。
**attempt 1でstatus=OK・asr_verified=true**。ASR書き起こし: "...Strawberries
are one case. Some refrigerator makers put them in the high humidity
drawer, while others put them in the low humidity drawer instead...."
(想定どおり2回目の"humidity"も正しく聞き取られた)。revision2で3回連続
発生していたHuman Review Lockは今回発動しなかった。詳細:
`.../point_one_regen_run_summary_v3.json`。

### 11.3 Assembly — Production Gateにより STOP(想定外の発見、他segment起因)

他30segmentはoriginal `b1b/`との**sha256完全一致を確認済み**(reuse
manifest: `.../reuse_manifest_revision3.json`、mismatches 0件)。point_one
のみ新sha256。

既存Production関数`er003_v1_n3_01_assemble.py::stage_assemble_b1`を無変更
で実行したところ、**`EPISODE_BLOCKED_BY_AUDIO_VALIDATION`で例外停止**した。
原因はpoint_oneではなく、**このHousehold記事(2026-08-17承認)が現行の
Audio Validation Gate(disfluency QA必須化・STOPPED状態拒否、ER-008-N8-
FINAL-QA-HARDENING-21系)より前に生成・承認されたレガシー記事であり、
point_one以外の13segment**(`topic_intro`・`kp2_english`=STOPPED状態、
`preview`・`comment_1〜4`・`point_one_heading`・`point_two_heading`・
`in_one_line`・`kp1/3/4/5_english`=disfluency_checkedフィールドが
記録されていない[MISSING_MANDATORY_DISFLUENCY_QA])が、現行Gateの必須
条件を満たしていないため。`human_approved_segments.json`(Gateが承認済み
として扱う既存の正規承認記録)もこの記事には未作成(2026-08-17当時の
承認はこのGate機構が存在する前に行われたため)。

これはpoint_one修正やrevision3文言とは無関係の、**記事全体の前提条件の
問題**であり、解消するには(a)他segmentの再生成・disfluency QA再実行
(今回の指示で明示的に禁止)、または(b)`human_approved_segments.json`を
新規作成して2026-08-17時点の承認をGateへ遡及的に反映する、のいずれかの
判断が必要。いずれも本タスクの指示範囲(point_oneのみ・他segment再生成
禁止・Gate等の安全装置を独自判断で回避しない)を超えるため、**実装せず
ここでSTOPし、Fable/ユーザーへ判断を仰ぐ**。Assembly・player.htmlは
生成していない。

エラーメッセージ全文・block segment一覧:
`er011_output/open138_household_fact03_b1b_minimal_fix_02/assemble_revision3_summary.json`。

### 11.4 費用(実測、分離記録、revision3のみ)

- QA(Fact Checker×2 + Ledger Deviation×2、revision3a/b双方):
  $0.094959 ≒ **¥15.19**
- TTS(Gemini)+ASR(OpenAI)、point_one attempt 1回のみ: $0.010618 ≒
  **¥1.70**
- **合計 $0.105577 ≒ ¥16.89**(上限¥40に対し実費¥16.89)。revision2分
  ¥19.79と合算しても¥36.68。

### 11.5 新規/変更ファイル(継続分)

- 新規: `er011_output/open138_household_fact03_b1b_minimal_fix_02/`配下に
  `revision3_qa.py`・`revision3_qa_results.json`・
  `revision3_textfix.py`・`textfix_diff_revision3.json`・
  `tts_regen_runtime_evidence_v3.py`・`point_one_regen_run_summary_v3.json`・
  `raw_usage_log_revision3.jsonl`・`raw_usage_log_revision3_tts.jsonl`・
  `reuse_manifest_revision3.json`・`assemble_revision3.py`・
  `assemble_revision3_summary.json`
- 変更: `er003_output/n3_01/household/fact03_fix_02/b1b/article.md`・
  `parts.json`(revision2→revision3a)、`fact_qa.json`・
  `ledger_deviation.json`(revision3a再検証結果に更新)、
  `narration/point_one.wav`(revision3a音声、asr_verified=true)、
  `audit/tts_generation_results.json`(point_oneのみ更新)
- 不変: `er003_output/n3_01/household/{a2,b1b}/`(元の公開済みArtifact、
  引き続き無編集)。他30segmentのnarration wavは元b1bとsha256完全一致。

### 11.6 STOP条件該当性(継続分)

- Ledger v4で裏付けできる修正文: 該当なし(revision3a作成済み、Fact
  Checker PASS)。
- Fact Checker FAIL: 非該当(PASS)。
- TTS Human Review Lock: **非該当(1回でPASS、今回は発動せず)**。
- 他segment再生成が必要: 該当せず未実施(禁止指示どおり、代わりに
  ここでSTOP)。
- **想定外の発見によりSTOP: 該当。** Production Assembly Gateが、
  point_one以外の13レガシーsegment(2026-08-17承認時点でGate機構が
  存在しなかったため)をブロックした。これは指示範囲外の記事全体の
  前提条件問題であり、実装せず報告する。
- 費用超過: 非該当(¥16.89 / 上限¥40)。


## 12. 継続(Fable修正指示2回目、既存QA事後適用) — 到達Status: STOP
(13/14 PASS、kp2_englishのみ不合格)

指示: Gate回避・承認記録の遡及作成・レガシーsegmentの再生成は行わず、
現行Gateが要求する既存QA(disfluency QA・ASR照合)を、レガシー13segment
(point_one以外にブロックされた14件のうち13件、topic_intro・kp2_english
除く)の既存wav(byte不変)へ事後適用して証跡を生成する。全PASSなら
Assembly、1件でも不合格ならSTOP(再生成なし)。

### 12.1 現行Gateの必須項目(`er003_v1_n3_01_assemble.py`から列挙)

- `AUDIO_GATE_ALLOWED_STATUSES = ("VALIDATED", "HUMAN_APPROVED")`。
  `status`が`OK`ならVALIDATED、`STOPPED`/`ASR_VALIDATION_UNCERTAIN`は
  `human_approved_segments.json`に一致する承認記録が無い限りブロック。
- `DISFLUENCY_QA_MANDATORY_SEGMENTS_BY_LEVEL["B1"]` =
  `preview, comment_1〜4, in_one_line, point_one_heading,
  point_two_heading` + 末尾`_english`の全segment(kp1〜5_english)。
  これらは`disfluency_checked is True`が記録されていなければ
  `MISSING_MANDATORY_DISFLUENCY_QA`でブロック。
- `_segment_asset_hash_stale`: `tts_generation_results.json`記録sha256と
  実ファイルsha256の不一致でブロック(30 segmentは今回も突合済み、
  reuse_manifest_revision3と合わせて0件不一致)。

Gateが実際にブロックした14件(EPISODE_BLOCKED_BY_AUDIO_VALIDATION、
§11.3のエラー全文): `topic_intro=STOPPED`、`kp2_english=STOPPED`、
`preview/comment_1〜4/point_one_heading/point_two_heading/in_one_line/
kp1,3,4,5_english=VALIDATED(MISSING_MANDATORY_DISFLUENCY_QA)`(12件)。

### 12.2 disfluency QA事後適用(12件、全PASS)

既存Production関数`er008_disfluency_qa_18.check_segment_for_disfluency`
(faster-whisperローカル実行、追加API課金なし)を、既存wav12件
(narration/*.wav、書き込みなし)へ直接実行。全件`flagged=False`のため
`disfluency_checked=True`として`tts_generation_results.json`
(fact03_fix_02側コピー)へ追記した。全件事前/事後sha256一致を
assertで確認済み(wav自体は無変更)。

スクリプト: `er011_output/open138_household_fact03_b1b_minimal_fix_02/
legacy_disfluency_qa_reapply.py`。結果:
`.../legacy_disfluency_qa_reapply_summary.json`。

### 12.3 ASR再照合(topic_intro・kp2_english、STOPPED終端状態)

2026-08-17当時いずれも6回試行後STOPPED(canonical "crisper"をASRが
一貫して"CRISPR"と書き起こしていた、CMU辞書に"CRISPR"が存在しないため
homophone判定不能)。既存Production ASR Cascade
(`er006_secondary_asr_01.evaluate_attempt_with_cascade_detail`、
Primary#1/#2[OpenAI] → Secondary#1/#2[Azure]、entity_like/homophone
Case A判定)を、既存wav(byte不変、TTS呼び出しなし)へ実行:

- **topic_intro: PASS**(`NORMALIZED_MATCH`)。Primary#1/#2は変わらず
  "...your **CRISPR** drawer..."(ASR_VALIDATION_UNCERTAIN、entity_like)
  だったが、entity_like該当によりcascade続行、Secondary#1(Azure)が
  文全体の文脈込みで"...your **crisper** drawer..."と正しく書き起こし、
  `NORMALIZED_MATCH`でPASS。
- **kp2_english: FAIL**(`TRUE_CONTENT_MISMATCH`)。canonical
  "crisper drawer"（2語のみ、文脈なし）に対しPrimary#1が
  "CRISPR drawer."と書き起こし、この場合`entity_like=False`・
  `homophone_candidate=False`と判定されたため(CMU辞書に"CRISPR"が
  無くhomophone判定不能、かつ短いフレーズ単独では固有名詞様の大文字化
  手がかりも弱い)、cascade対象外条件に該当せずSecondary ASRへ進まず
  即FAILで終了(これはProduction実際のcascade eligibility判定と
  同一の挙動)。

スクリプト: `er011_output/open138_household_fact03_b1b_minimal_fix_02/
legacy_stopped_segments_asr_reverify.py`。結果:
`.../legacy_stopped_segments_asr_reverify_summary.json`。

`tts_generation_results.json`の`status`フィールド自体はSTOPPEDのまま
変更していない(承認記録の遡及作成はしていない、`legacy_asr_reverify`
という別フィールドへ証跡のみ追記)。

### 12.4 結論・Assembly

**1件(kp2_english)が現行QAでも不合格**のため、13/14 PASSであっても
指示どおりここでSTOPし、`stage_assemble_b1`・Audio Validation Gate・
player生成は実行していない。比較試聴ページ:
`er003_output/n3_01/household/fact03_fix_02/b1b/legacy_qa_review.html`
(narration/topic_intro.wav・narration/kp2_en.wavの既存wav[コピー元と
sha256完全一致、無変更]を直接埋め込み、各stepのASR書き起こしを併記)。

### 12.5 費用(実測、分離記録)

ASRのみ(OpenAI Primary×3呼び出し + Azure Secondary×1呼び出し)。
`er011_output/open138_household_fact03_b1b_minimal_fix_02/
raw_usage_log_legacy_stopped_asr_reverify.jsonl`実測値、
`pricing_snapshot.json`単価、1USD=160円で計算:
$0.0025578 ≒ **¥0.41**(上限¥30に対し実費¥0.41)。disfluency QAは
ローカル実行のため追加課金なし。

### 12.6 新規/変更ファイル(継続分)

- 新規: `er011_output/open138_household_fact03_b1b_minimal_fix_02/`配下に
  `legacy_disfluency_qa_reapply.py`・
  `legacy_disfluency_qa_reapply_summary.json`・
  `legacy_stopped_segments_asr_reverify.py`・
  `legacy_stopped_segments_asr_reverify_summary.json`・
  `raw_usage_log_legacy_stopped_asr_reverify.jsonl`
- 新規: `er003_output/n3_01/household/fact03_fix_02/b1b/
  legacy_qa_review.html`
- 変更: `er003_output/n3_01/household/fact03_fix_02/b1b/audit/
  tts_generation_results.json`(12segmentへ`disfluency_checked=True`+
  `disfluency_evidence`+`disfluency_qa_retroactive_note`を追記、
  topic_intro/kp2_englishへ`legacy_asr_reverify`を追記。**statusフィールド
  自体は変更していない**)。narration配下のwav自体は全て無変更
  (事前/事後sha256一致をassertで検証済み)。
- 不変: `er003_output/n3_01/household/{a2,b1b}/`(元の公開済み
  Artifact、無編集)。`docs/pm/ACTIVE_TASK.md`・`RESULT_PACKET.md`・
  `CURRENT_SPEC.md`等SSOT一式(本タスクでは編集していない)。

### 12.7 STOP条件該当性(継続分)

- disfluency QA: 12/12 PASS(不合格なし)。
- ASR再照合: topic_intro PASS、**kp2_english FAIL**。
- **1件でも不合格ならSTOP(指示どおり): 該当。** kp2_englishが現行QA
  基準でも不合格のため、Assembly・Gate通過・player生成は実施せず
  ここでSTOP。再生成・承認代行は一切行っていない。
- Gate回避・承認記録の遡及作成: 非該当(`human_approved_segments.json`
  は作成・変更していない、`status`フィールドも変更していない)。
- 費用超過: 非該当(¥0.41 / 上限¥30)。

### 12.8 OPEN item候補(実装・判断はしない、報告のみ)

一般論として、**2026-08-17以前に承認済みのepisodeは、その後追加された
現行Audio Validation Gate(disfluency QA必須化・ASR Cascade改善等、
ER-008-N8系)の証跡を一切持たない**。本タスクのHousehold記事のように
「既存QAを事後適用すれば大半はPASSするが、一部(短い2語フレーズの
Key Phraseなど、文脈の乏しいsegment)は依然として不合格になりうる」
ケースが今後も他のレガシー記事で発生しうる。遡及QA方針(事後適用で
PASSしたレガシー記事をどう扱うか、不合格segmentが残る場合の運用)は
ユーザー/Fableの判断が必要な事項として、ここでは実装せず提示のみ行う。


## 13. 継続(Fable修正指示3回目、kp2_english人間承認)— 到達Status:
STOP(topic_intro=STOPPEDが別途未解決)

指示: ユーザー決定(2026-09-09、A-FACT03-2(a))「kp2_englishはユーザー
試聴OK」に基づき、既存Production承認経路
(`er003_v1_n3_01_assemble.record_human_approval()`、ER-009-N1・
OPEN-112 Subtask Eと同一関数)でkp2_englishを`HUMAN_APPROVED`として
記録し、`stage_assemble_b1`→Audio Validation Gate→playerまで進める。

### 13.1 承認記録

`asm.record_human_approval(B1_DIR, "kp2_english", "", approved_by=
"user_2026-09-09_HOUSEHOLD-FACT-03-PUBLISHED-ARTICLE-MINIMAL-FIX-02")`
を実行(canonical_textはkey phrase sub-entry仕様上空文字列、
ER-010-NO9-kp2_english one-off採用と同型のパターンを踏襲)。承認記録
ファイル: `er003_output/n3_01/household/fact03_fix_02/b1b/audit/
human_approved_segments.json`(新規)。noteフィールドに指定文言
(「2026-09-09 ユーザー試聴承認、A-FACT03-2(a)、ASR同音異義による
false reject、音声はbyte不変」)およびASR同音異義の根拠
(`legacy_asr_reverify`参照)を追記。

### 13.2 追加で必要と判明したdisfluency QA(kp2_english、想定内の技術的前提)

承認記録後にGateを実行したところ、`kp2_english=HUMAN_APPROVED
(MISSING_MANDATORY_DISFLUENCY_QA)`が新たに検出された。Gateの
disfluency QA必須chekは承認statusとは独立した別条件(`_english`
サフィックスsegment全てが対象)であり、kp2_englishはcontinuation2
(Fable修正指示2回目)の12segment事後適用対象に含まれていなかった
(当時STOPPEDのため別枠扱い)ため未適用のままだった。「必要なAudio
Validation整合確認を実施」という指示範囲内の技術的前提と判断し、
continuation2と同一の既存Production関数
(`er008_disfluency_qa_18.check_segment_for_disfluency`、faster-whisper
ローカル実行、追加API課金なし)を既存wav(`narration/kp2_en.wav`、
byte不変)へ事後適用した。結果: `flagged=False`→**PASS**。適用前後の
sha256一致をassertで確認済み(wav無変更)。`tts_generation_results.json`
のkp2_english.englishへ`disfluency_checked=True`+`disfluency_evidence`を
追記(`status`フィールド自体はSTOPPEDのまま不変)。

### 13.3 sha256再確認(narration/*.wav全32件)

`fact03_fix_02/b1b/narration/`直下の全32件(attempts/配下除く)を
original(`er003_output/n3_01/household/b1b/narration/`)と突合。
**31件完全一致、point_one.wavのみ不一致(想定どおりrevision3a、
continuation1で既確認済みの差分)**。詳細:
`er011_output/open138_household_fact03_b1b_minimal_fix_02/
kp2_english_human_approval_and_assemble_03_result.json`
(`step1_sha256_precheck`)。

### 13.4 Gate結果・Assembly結果 — STOP(topic_intro=STOPPEDが未解決)

- 既定Gate経路(`verify_episode_audio_validation_gate(B1_DIR, "B1")`、
  `stage_assemble_b1`内蔵と同一)・opt-in `required_structure` ON経路
  (`derive_a_family_required_structure("B1")`)ともに**同一理由で
  BLOCKED**: `EPISODE_BLOCKED_BY_AUDIO_VALIDATION: ['topic_intro=
  STOPPED']`。kp2_englishはこの時点で完全にクリア(承認記録+
  disfluency QA PASS)されており、**残る唯一のブロック要因は
  topic_intro**。
- `stage_assemble_b1(theme)`本体も同一理由でRuntimeError、**Assembly・
  player生成は未実施**。
- topic_intro自体は既にcontinuation2(§12.3)で既存ASR Cascadeにより
  content的にはPASS(`NORMALIZED_MATCH`、Secondary ASRがcrisperと
  正しく書き起こし)しているが、Gateが見る`status`フィールドは
  2026-08-17当時の`STOPPED`のまま変更されていない
  (continuation2は「statusフィールド自体は変更せず、Gate合否判断は
  人間/Fable判断に委ねる」と明記して意図的に据え置いていた)。
- **今回のユーザー決定(2026-09-09、A-FACT03-2(a))はkp2_english
  のみを明示的に対象としており、topic_intro承認は範囲外**。指示された
  「Lock発動時は承認代行せずSTOP」の趣旨(STOPPED状態segmentの承認は
  ユーザー/Fableの明示判断が必要)に従い、**topic_introへの
  `record_human_approval()`は実行せずここでSTOP**した。承認代行・
  推測による拡大実装は行っていない。

### 13.5 費用

本ラウンドは全てローカル処理(record_human_approval=ファイルI/Oのみ、
disfluency QA=faster-whisperローカル実行、sha256突合=ローカル)。
**追加API課金なし、実費¥0.00**(上限¥10に対し実費¥0)。

### 13.6 player file:///パス

**Assembly未実施のため、本ラウンドでの新規player.htmlは存在しない**
(§7と同様、A2は無変更のため既存承認済み
`er003_output/n3_01/household/a2/`を引き続き参照)。

### 13.7 新規/変更ファイル

- 新規: `er011_output/open138_household_fact03_b1b_minimal_fix_02/
  kp2_english_human_approval_and_assemble_03.py`・
  `kp2_english_human_approval_and_assemble_03_result.json`
- 新規: `er003_output/n3_01/household/fact03_fix_02/b1b/audit/
  human_approved_segments.json`(kp2_englishの承認記録のみ)
- 変更: `er003_output/n3_01/household/fact03_fix_02/b1b/audit/
  tts_generation_results.json`(kp2_english.englishへ
  `disfluency_checked`/`disfluency_evidence`/
  `disfluency_qa_retroactive_note`/`disfluency_qa_retroactive_status`を
  追記。`status`フィールド自体は変更していない。narration配下のwav自体は
  無変更、sha256突合済み)
- 不変: `er003_output/n3_01/household/{a2,b1b}/`(元の公開済み
  Artifact、無編集)。`docs/pm/ACTIVE_TASK.md`・`RESULT_PACKET.md`・
  `CURRENT_SPEC.md`等SSOT一式(本タスクでは編集していない、SSOT/Git
  禁止指示どおり)。

### 13.8 STOP条件該当性

- kp2_englishのHUMAN_APPROVED記録: 完了(ユーザー決定どおり)。
- kp2_englishのdisfluency QA: PASS(想定内の技術的前提を追加適用)。
- sha256再確認: 31/32一致(point_oneのみ想定内の差分)。
- **Assembly: topic_intro=STOPPEDにより依然BLOCKED。ユーザー決定は
  kp2_englishのみを対象としており、topic_introの承認可否は本タスク
  範囲外のためSTOP。** Human Review Lock(er011機構)自体は今回発動して
  いない(発動する前段のGateでブロックされたため)が、「STOPPED状態
  segmentの承認代行はしない」という同じ安全原則に従いSTOPした。
- 費用超過: 非該当(¥0 / 上限¥10)。

### 13.9 USER_DECISION_REQUIRED(次のアクション候補、実装せず提示のみ)

topic_intro(canonical: "Today's topic is Your Crisper Drawer Has 2
Jobs—and One Tiny Switch Decides Which.")は、2026-08-17当時6回試行後
STOPPEDだが、continuation2で適用した現行ASR Cascadeでは
`NORMALIZED_MATCH`(Secondary ASRがcrisperと正しく書き起こし)でPASS
している。以下のいずれかの判断が必要:

(a) kp2_englishと同様、ユーザー試聴の上でtopic_introも
    `record_human_approval()`によりHUMAN_APPROVEDとして記録する
    (既存音声はbyte不変、再生成なし)、
(b) topic_introは対象外のまま、Assembly自体を見送る、

のいずれを取るかはユーザー/Fableの判断が必要。本タスクでは実装して
いない。判断が得られ次第、Assembly→Audio Validation Gate→player生成を
再試行することは技術的には即座に可能な状態(kp2_english側の前提条件は
全てクリア済み)。
