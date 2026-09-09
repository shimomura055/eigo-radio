# EDITORIAL-B-FAMILY-VOICES-4V-ARTICLE-TRIAL-02

管理ID: EDITORIAL-B-FAMILY-VOICES-4V-ARTICLE-TRIAL-02(Lane B、HIGH系列の継続、Opusレビュー済み設計の
延長)。**Trial専用**(Production/Trial-07/registry/Contract編集禁止、SSOT・Git操作禁止)。並列稼働中:
Governance追記+SSOT統合タスク(SSOT・Git担当、本タスクとは無関係)。

ユーザー決定(2026-09-09)により、`EDITORIAL-B-FAMILY-VOICES-4V-ARTICLE-TRIAL-01_REPORT.md`のSTOP 2件
(B-4V-1=一人称"I"欠落、B-4V-2=Analytical Leakage Checkがflagged状態のままMAX_WRITER_ATTEMPTS到達)を、
承認済み範囲内の改善として実施した。Trial-01ファイル自体は一切変更していない(新規ファイル
`er012_editorial_b_voices_4v_article_trial_02.py`を作成)。

## 1. Reconciliation(一人称指示の所在・Leakage feedback方式の所在・Trial-01の差分)

- **一人称"I"指示の所在**: ユーザーは2026-09-08(`DECISION_LOG.md` PM-CLOSEOUT-CONSOLIDATION-05)に、
  B-Family Voices試聴後の`APPROVED_FOR_PRODUCTION`4項目の一つとして「**(4) Voice A/Bの一人称"I"記述**」
  を正式決定している(引用: 「ユーザーが`APPROVED_FOR_PRODUCTION`(2026-09-08、未配線)と正式決定した
  のは以下4項目: (1) Voice A=Algieba/Voice B=Erinome/Narrator見出し=Aoede固定、(2) Tension slot
  「Where the Difference Comes From」の正式構造への追加、(3) Key Phrase位置=Preview直後(現状維持)、
  (4) Voice A/Bの一人称"I"記述」)。同エントリは続けて、この一人称記述の配線は「Lane A共有Writer
  (`er003_v1_n3_01_articles_generate.py`)へのEditorial Type Module導入が前提のためSTOP(別タスク推奨)」
  と記録しており、Production配線は現時点でも未着手のままである。
- **Trial-07/Trial-09の2V promptに一人称指示があったか**: `er012_editorial_b_voices_trial_07.py`の
  ヘッダーコメント(49行目)に明記されている: 「一人称/三人称は固定しない(必須にしない、Writerが
  最も自然にVoicesとして成立する書き方を選び、選択結果を観察・記録する)」。つまり2V版のprompt自体には
  一人称を指示する文言は**一度も含まれていなかった**。DECISION_LOG(Trial-06/Trial-07追記)も「一人称
  "I"で書かれていた(Focus Module指示ではなくWriterの自発的選択)」と明記しており、2Vで一人称になった
  のはWriterの自発的選択(偶然)であり、4V複製時に指示文が「落ちた」わけではない(そもそも複製元に
  一人称指示は存在しなかった)。Trial-01の`B_FAMILY_VOICES_4V_FOCUS_MODULE_BLOCK`本文をgrep確認しても
  「一人称」「first person」の文言は0件であった。
- **結論**: 2026-09-08の承認決定(4)は、2V promptへも4V promptへも一度も明文化されたことがない
  未配線の設計原則だった。本Trial-02でこれを4V Focus Module Blockへ初めて明示するのは、**新しい原則の
  創作ではなく、既にユーザーが承認済みの原則を初めて実装へ適用するもの**である(矛盾なし、STOP該当なし)。
- **Leakage feedback方式の所在**: `er012_editorial_b_voices_trial_07.py`の`run_analytical_leakage_check`
  (Leakage判定)+`build_leakage_corrective_note`(是正メモ生成)がTrial-07由来の既存機構。4V版では
  Trial-01が`run_analytical_leakage_check_4v`+`build_leakage_corrective_note_4v`として複製済みで、
  `run_pipeline_4v`内のMAX_WRITER_ATTEMPTS=3ループ(初回+是正2回)で既に呼び出されている。本Trial-02は
  このコード自体を一切変更せずそのまま再利用した(新しいVoice別語り口指示は追加していない)。

## 2. 実施した変更(Trial-01からの差分は以下の2点のみ)

(a) `B_FAMILY_VOICES_4V_FOCUS_MODULE_BLOCK`へ「【人称】」セクションを新設し、Voice 1〜4本文を一人称"I"
    で書く指示を明示した(Hook/Tension/Closingは対象外、三人称のまま維持)。禁止事項まとめにも
    「Voiceセクションを三人称で書くこと」を追加した。
(b) 既存のLeakage是正フィードバックループ(`run_pipeline_4v`、MAX_WRITER_ATTEMPTS=3)をそのまま実行
    (Trial-01と同一設定、変更なし)。
Ledgerは`ai_screening_ledger_trial_01`をそのまま再利用(新規Research呼び出しなし)。

## 3. Writer stage結果(全attempt Fact Checker A' PASS、Ledger LEDGER_COMPLIANT)

| attempt | Fact Checker verdict | Ledger deviations | Local Rewrite | Leakage any_flagged | flagged voice/fields |
|---|---|---|---|---|---|
| 1 | PASS | MINOR×3 | 不要(MAJORなし) | True | voice_3(numbers/discovery/memorable), voice_4(同3項目) |
| 2 | PASS | MINOR×4 | 不要(MAJORなし) | True | voice_1(4項目), voice_3(discovery), voice_4(3項目) |
| 3(最終) | PASS | MINOR×2 | 不要(MAJORなし) | True | voice_2(unknowable/discovery), voice_3(3項目), voice_4(numbers/discovery) |

MAX_WRITER_ATTEMPTS(3)に到達してもLeakage flaggedは解消しなかった(voice_3/voice_4のDiscovery型逆戻り
[leak_discovery_syntax]がTrial-01同様3 attempts中で持続、Trial-01のF2failure modeが再現)。**新規failure
modeではなく既知の未解決課題の再現**のため、STOP条件「新規failure mode」には該当しないと判断し、以降の
QA measurementはすべて実施した(Editor省略なし、Diagnostic Full Retryは本Trial経路[`run_writer_no_
search`直接呼び出し、Trial-01からの既知の迂回]では発火対象外のまま、Local Rewriteは全attemptでMAJOR
0件のため不発、Trial-01より改善)。

## 4. 一人称使用率(機械計測、`first_person_usage_report.json`、attempt3最終article)

| section | 文数 | 一人称"I"を含む文数 | 比率 |
|---|---|---|---|
| hook | 5 | 0 | 0.0 |
| voice_1 | 6 | 3 | 0.5 |
| voice_2 | 6 | 3 | 0.5 |
| voice_3 | 6 | 2 | 0.333 |
| voice_4 | 6 | 2 | 0.333 |
| tension | 6 | 0 | 0.0 |
| closing | 3 | 0 | 0.0 |

4 Voiceすべてが冒頭文から一人称"I"で開始し(例: "I send my résumé, then sit before a camera..."、
"I use software to sort résumés..."、"I watch the hiring dashboard..."、"I open audit records...")、
Trial-01(全attempt・全section"I"使用0件)から明確に改善した。Hook/Tension/Closingは指示どおり三人称の
まま(比率0.0、意図どおり)。voice_3/voice_4の比率がやや低い(0.333)のは、Leakage Check flagged項目
(numbers_foreground/discovery_syntax)と同じ箇所(第三者の事実描写文)に一人称主語が伴っていないためで、
F1(一人称欠落)とF2(Discovery逆戻り)は別軸の問題として両方観察された。

## 5. Trial-01との差分表

| 項目 | Trial-01 | Trial-02 |
|---|---|---|
| 語数(final article、7区切り合計) | 523語 | 469語 |
| 推定尺(2V実測換算、gate外) | 411.9秒 | 385.0秒(目標380〜430秒内) |
| Point Overlap 16値(monitoring) | 0.042〜0.171、any_flagged=false | 0.0〜0.154、any_flagged=false |
| Leakage flagged(最終attempt) | voice_2/3/4 | voice_2/3/4 |
| 一人称使用率(Voiceセクション) | 0%(全section) | 33〜50%(Voice)、0%(Hook/Tension/Closing) |
| Ledger Deviation(MAJOR) | attempt1:1件→LR解消、attempt3:1件→LR解消 | 全attempt MAJOR 0件、LR不要 |
| Fact Checker A' | 3/3 PASS | 3/3 PASS |
| Distinctness direction_agreement_rate | 0.9(27/30) | 0.933(28/30) |
| Distinctness method_agreement_rate | 0.767(23/30) | 0.933(28/30) |
| 費用 | ¥37.2 | ¥76.6(writer ¥74.49+qa ¥2.08) |
| attempt数 | 3(MAX到達) | 3(MAX到達) |

## 6. Distinctness Check・Overlap Controls・costと時間

- Distinctness: 有向12ペア68.4秒、一括判定22.0秒。direction_agreement_rate=0.933、
  method_agreement_rate(一括 vs 有向)=0.933(いずれもTrial-01より改善)。
- Overlap ¥0 control群: positive=0.846(flagged想定どおり)、deterministic=0.711(指標の盲点再現)、
  negative(既存2V実採用ペア再計算)=0.14、theme_vocab_dummy=0.389(閾値0.40付近、偽陽性リスク近接、
  Trial-01と同水準)。
- required_structure 4V review: segment_count=18・voice_1〜4各1回・重複なし、全項目PASS(OPEN-132で
  正本統合追跡)。
- 費用が前回比で増加した主因は、Ledger Deviation Checker(`vfl01.run_deviation_check`、Production
  primitive、無変更)がattemptごとにweb_search呼び出し(11/8/8回)を行い、入力トークンが1回あたり
  6万〜10万に達したため(この呼び出しはTrial-01から関数・引数とも無変更で再利用しているだけで、
  本Trial-02が新規に呼び出しを増やしたものではない)。

## 7. コスト実測と量産概算

- Writer stage(21 call、web_search 27回込み): ¥74.49
- QA stage(15 call、Comment 1・4の2件+Distinctness 12+1件): ¥2.08
- **合計 ¥76.6**(上限¥150に対し十分な余裕)。
- 量産時概算: MAX_WRITER_ATTEMPTS=3をフルに消費し、かつLedger Deviation Checkerのweb_search呼び出しが
  今回同様の規模で発生する場合、記事あたり約¥70〜80/本。Local Rewriteが発生した場合はさらに数円〜十数円
  増える(Trial-01実績)。

## 8. Perspective Diversity・賛否2対2・Tension/Closing所見

Voice 1〜4本文と`perspective_map.md`を目視突合し、Ledger根拠との不一致・Voice間の証拠混入は確認
されなかった(Trial-01と同一Ledger・Voice Cardのため対応関係も同一)。4 Voiceは賛否2対2に分割されて
いない(Tensionは「These pressures do not line up」から始まり、4者それぞれ異なる負担[losing the
chance/a difficult explanation/time-cost-scale/audits and legal records]として描写)。Tensionは
Evidence要約に陥っておらず、Closing("What This Really Changes")は要約ではなく問いの再定義("who defines
a fair chance, who carries the cost...")で締めている。

## 9. Gate 4・Gate 1分類

- **Gate 4**: Production(`er012_b_family_voices_production_01.py`・
  `er012_b_family_editorial_type_registry_01.py`・`er012_b_family_production_runner_01.py`)・
  Trial-07(`er012_editorial_b_voices_trial_07.py`)・Trial-01(`er012_editorial_b_voices_4v_article_
  trial_01.py`)はいずれも`git diff`で無変更を確認(読み取り専用importのみ、Trial-01ファイル自体も
  一切編集していない)。SSOT・Git操作は実施していない。
- **Gate 1分類**: **USER_DECISION_REQUIRED**。B-4V-1(一人称)は達成(4 Voice全attemptで一人称が成立、
  副作用[代名詞衝突・誤読等]は本Trialのtext-only範囲では未検出)したが、B-4V-2(Leakage解消)は
  MAX_WRITER_ATTEMPTS到達後も未解消(voice_3/4のDiscovery型逆戻りが持続)であり、判定基準
  「Leakage flagが解消」を満たしていないため、VALIDATEDとはしない。Fact Check/Ledger
  Deviation/Overlap/Perspective Diversity/Distinctnessの各観点は個別にはVALIDATED相当(Trial-01より
  改善)。

## 10. 未承認仕様候補(前回どおりTrial-onlyと明記)

- Comment 2/3の4V版文言(design.md B-1手動ドラフト、registryへ未反映)。
- Analytical Leakage Check 4V版スキーマ(Trial側新規、registry未反映)。
- Pairwise Voice Distinctness Check(一括方式を主、有向方式を診断併走、正式採用は別途)。
- OPEN-129 required_structure 4V(voice_1..4命名のvoice_map方式、正本統合はOPEN-132)。
- 一人称"I"のFocus Module明記自体は2026-09-08承認決定の適用のためTrial-only扱いではないが、
  Production Editorial Type Moduleへの実配線は別途未着手(§1参照)。

## 11. STOP有無

**STOPなし(結果提示)**。B-4V-2(Leakage未解消)はSTOP条件に定められた既知シナリオそのもの
(「MAX_WRITER_ATTEMPTS(3)到達後もLeakage解消せず」)であり、結果を提示して報告するに留め、
prompt原則の追加は行っていない(未承認候補として上記§10に記載のみ)。新しい語り口指示・新原則の
追加は行っておらず、Reconciliationも承認記録との矛盾は検出しなかった。費用は上限内、
Production/Trial-07/registry書込みは発生していない。4V記事の賛否2対2化は発生していない。

## 12. 新規ファイル一覧

- `er012_editorial_b_voices_4v_article_trial_02.py`(新規、Trial-01ファイルは無変更のまま保持)
- `er012_output/editorial_b_voices_4v_article_trial_02/`配下一式(b1b_run01/b1b_run01_attempt1-3/qa/、
  attempt_history.json、summary.json、raw_usage_log_4v_writer.jsonl、raw_usage_log_4v_qa_stage.jsonl、
  required_structure_4v_trial_review.json、first_person_usage_report.json)
- 本Report(`EDITORIAL-B-FAMILY-VOICES-4V-ARTICLE-TRIAL-02_REPORT.md`)
