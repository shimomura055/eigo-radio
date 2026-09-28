## 管理ID

KEY-PHRASE-4PLUS1-TOPIC-PHRASE-PRODUCTION-01(Fableからの修正1回目=ユーザー既決事項の実装+Opus L2 SHOULD_FIX反映)。一時ファイル `docs/pm/ACTIVE_TASK_KP42.md` / `docs/pm/RESULT_PACKET_KP42.md`(commitしない)。並行衝突: 別Sonnet 2件がTrial(`er037_*`/`er037_output`/`FAMILY-XY-*`、`er038_*`/`er038_output`/`user_test/tts_all_role_style_trial_01`/`TTS-ALL-*`)を実行中 → これらに触れない。本タスクの所有: `er003_key_words_min_unit.py`、`er003_key_words_production.py`(コメント1行)、`er003_key_words_canonicalization.py`、`er003_v1_translator_briefs/b1_p2_keywords_l_prompt_template.txt`、`er030_key_phrase_db_hybrid_selector_01.py`、`er030_key_phrase_db_hybrid_source_reference_contract_01.py`、`er003_v1_n3_01_scaffold_generate.py`、`er035_kp_4plus1_topic_phrase_evidence_01_run.py`、`er034_key_phrase_db_hybrid_source_reference_contract_trial_06_test.py`(fixture 1行)、関連test、`KEY-PHRASE-4PLUS1-TOPIC-PHRASE-PRODUCTION-01_REPORT.md`。**SSOT編集権: 本タスクのみ**(直列化ルール。開始時・commit直前に `git status --porcelain CURRENT_SPEC.md DECISION_LOG.md OPEN_ITEMS.md docs/pm/REPORT_LEDGER.md` で他差分なしを確認)。

## 性質/到達上限Status/禁止事項

- 性質: Production配線の修正(ユーザー承認 `APPROVED_FOR_PRODUCTION` 範囲内)。到達上限Status: Sonnetは `PRODUCTION_WIRED` を宣言しない(Gate 3再確認表を報告、判定はFable)。
- 費用: 上限¥20(Guardrail。既決事項の実データ検証のみ、evidence再実行は差分最小)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。
- 禁止: 独自Product rule追加(固有名詞優先/専門語優先/タイトル語優先/出現回数/難易度/CEFR外/名詞優先/複合語必須/カテゴリ除外・優先)、例示hard-code、追加LLM call新設(既存selector call内)、Family固有分岐、Strategy L全面置換、後段Gate(canonicalization/Redundancy QA/source gate/TTS)の挙動変更、`git add -A`、履歴書き換え、APIキー本文表示。新たなユーザー判断が必要になったらSTOP。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要。
T-0: 受領した委任文を `docs/pm/delegation_log/2026-09-28_KEY-PHRASE-4PLUS1-TOPIC-PHRASE-PRODUCTION-01_04.md` へ保存し `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-28_KEY-PHRASE-4PLUS1-TOPIC-PHRASE-PRODUCTION-01_04.md --json-out docs/pm/delegation_log/2026-09-28_KEY-PHRASE-4PLUS1-TOPIC-PHRASE-PRODUCTION-01_04.md_check.json`、結果1行記録。
T-2: TTSなし。
T-3: 上記「性質」欄の定型文に従う。

## ユーザー指示(原文、2026-09-28 既決事項)

「KP 4+1: 以下はすでにユーザー判断済みです。- Strategy L retry: 最大2回 - 2回目に到達した場合: 報告必須 - Topic Phraseが取れない場合: DB側で通常候補を 4件 + backup 1件、Topic欠損時はそのbackupで補完 - Topic slotが既存の重要語カテゴリに該当する場合: その条件を満たした扱いでよい - Strategy L側のrunner-up / 5-slot外候補: 現時点では不要、将来のUI設計時に再検討、Open Itemとしてdefer」。Opus L2所見(REPORT §12逐語)のSHOULD_FIX S1〜S7・N1・N7も本修正で反映する(Fable指示)。

## 実装内容

1. **Strategy L retry 最大2回**: `er003_v1_n3_01_scaffold_generate.py:262-265` 付近の `max_attempts=1` 固定を Production既定 `MAX_PRODUCTION_RETRY_ATTEMPTS`(=2)に揃える。**2回目到達時は報告必須**: `keywords_runtime_metadata.json` と telemetry に `strategy_l_attempts=2`/`retry_reached_second_attempt=true` と理由(role構成不成立等)を記録し、runner出力の要約(既存の `run_summary`/audit相当)に「KP選定が2回目に到達」の1行を出す(既存の報告経路を使う、新UIなし)。
2. **DB Hybrid: 通常候補4件+backup 1件、Topic欠損時はbackupで補完**(DB Hybrid経路のみ、同一selector call内): selector schemaへ「important 4件+topic 1件」に加えて `backup_item`(important役割の予備候補1件、候補IDで指定、必須プロパティだがtopicが選べた場合も常に1件返す)を追加。validator/合流ロジック: topic が(a)返らない/(b)構造・候補ID検証で無効、の場合は `backup_item` を5件目として `key_phrase_role="important"` で補完し、`keywords_runtime_metadata.json` に `topic_slot_filled_by_backup=true` と理由を記録(telemetryにも)。backupも無効なら既存 `KEY_WORDS_STRUCTURE_INVALID`→fallback 経路(変更なし)。**Topic候補がStage 1プールに存在しないケース**はこの補完で吸収される(新候補生成ロジックは作らない)。Prompt文言は「topicが該当しない場合はtopicを空にせず最善候補を選び、別途backupを1件返す」等の最小追記に留め、選定基準は増やさない。Strategy L経路は変更なし(4+1のまま、retry 2回)。
3. **Topic slot が既存の重要語カテゴリに該当する場合は「重要語区分から最低1件」の条件を満たした扱い**: `er030_key_phrase_db_hybrid_source_reference_contract_01.py:172-173` の guidance 文言はそのまま(変更しない)。validator側でその条件を機械検証している箇所があれば topic 由来を含めて判定するよう明記(検証していなければ設計書/SSOTに「topic 1件で充足可(ユーザー決定)」と記録のみ)。
4. **Strategy L runner-up**: 実装しない。OPEN-211 を「DEFERRED(将来UI設計時に再検討、ユーザー決定2026-09-28)」へ更新。
5. **Opus SHOULD_FIX反映**: S1 Strategy L INVALID時も `role_counts` を返してtelemetryに載せる+role起因INVALIDの識別タグ; S2 `er035_kp_4plus1_topic_phrase_evidence_01_run.py` に `synthetic=True` を渡す(既存混入10行は書き換えず、OPEN-214系またはOPEN-211系へ「article_id接頭辞 `KP_4PLUS1_EVIDENCE_01_` はevidence起源」を追記); S3 新規testを `er003_test_key_words_min_unit_4plus1_01.py` へrename(両patternに一致)し、REPORT §8を「編集前6→編集後7、差分1件は件数照合meta-test、rename後に解消」へ是正(rename後の実測で確認); S4 `er034_..._trial_06_test.py` fixtureへ `"key_phrase_role": "important"` を1行追加; S5 `er003_key_words_production.py:44` 付近へ「test専用・4+1契約非対応(本番経路は `b1_p2_keywords_l_prompt_template.txt`)」の1行コメント; S6 Prompt追記の「残り4個の基準」6項目再掲を「残り4個は、上記の基準に従って選んでください(key_phrase_role="important")」の参照形へ縮約し、DB Hybrid固有の区分名列挙を「候補の種類・区分」へ一般化(新rule追加なし); S7 「既存test 5ファイル」→4へ是正(REPORT/CURRENT_SPEC); N1 `detail_reason_code` 判定で `item_reasons` も参照; N7 `PRODUCTION_ITEM_COUNT_UNCHANGED == PRODUCTION_ITEM_COUNT` の等価性test 1件。
6. **検証**: 単体test(新規: backup補完のPASS/FAIL、topic無効→backup補完、backupも無効→INVALID、Strategy L retry 2回・2回目報告記録、S1 telemetry、N7)。実データ: DB Hybrid 2記事(Meta A2/B1B のどちらか1件+forced topic欠損を再現できる記事1件、`synthetic=True`、Guardrail内)、Strategy L 1記事(melos_a2、retry 2回の動作確認)。合計 ¥5〜10 想定。`run_project_regression.py` 全件1回(baseline照合、S3の解消を確認)。Dangling Reference Check(Grep `backup_item|topic_slot_filled_by_backup|retry_reached_second_attempt|key_phrase_role`)。

## 事前指定Read一覧

- `KEY-PHRASE-4PLUS1-TOPIC-PHRASE-PRODUCTION-01_REPORT.md` §12(Opus所見逐語、行番号参照が正)、§3(Prompt追記逐語)、§8(regression記載)
- `er003_v1_n3_01_scaffold_generate.py`:230-300(`_run_key_phrase_selection_strategy_l`、max_attempts、role_counts)
- `er030_key_phrase_db_hybrid_selector_01.py`:540-660(validator合流、runtime_metadata、auxiliary出力)
- `er030_key_phrase_db_hybrid_source_reference_contract_01.py`:100-200(schema build、guidance)
- `er003_key_words_min_unit.py`:110-140(schema)、:470-500(role集計)
- `er003_v1_translator_briefs/b1_p2_keywords_l_prompt_template.txt`:20-30
- `OPEN_ITEMS.md`: OPEN-211/214 行

## 実行コマンド全文

- `.venv\Scripts\python.exe -m pytest er003_test_key_words_min_unit_4plus1_01.py er030_key_phrase_db_hybrid_source_reference_contract_01_test.py er030_key_phrase_db_hybrid_family_x_production_wiring_01_test.py er003_test_key_words_min_unit.py er003_test_p2i_production.py er003_test_b1_p2.py -q`
- `.venv\Scripts\python.exe run_project_regression.py`
- evidence差分実行: `.venv\Scripts\python.exe er035_kp_4plus1_topic_phrase_evidence_01_run.py --out-dir er035_output/kp_4plus1_evidence_02 --budget-jpy 15 --only meta_a2,melos_a2,forced_topic_missing`(引数は実装に合わせ逐語記録、`synthetic=True`)

## SSOT追記文(本タスクが直接適用)

- CURRENT_SPEC Key Phrase 4+1行: 修正1回目の内容(retry 2回+2回目報告、DB Hybrid backup補完、topic=重要語区分充足可、runner-up DEFERRED、S6 Prompt縮約、S7是正)、Statusは「Fable Gate 3判定待ち」のまま。
- DECISION_LOG: 新規エントリ(ユーザー既決事項原文要旨+Opus S1〜S7/N1/N7反映+検証結果+commit)。
- OPEN_ITEMS: OPEN-211→DEFERRED(runner-up/UI)、evidence起源注記、Strategy L retry 2回目報告の運用注記。
- REPORT_LEDGER: 行更新(修正1回目、Gate 3判定待ち)。

## Git

- add対象: 所有ファイル+test(rename含む `git mv`)+`er035_output/kp_4plus1_evidence_02/`(json/md)+REPORT+SSOT 4点+delegation_log+`_check.json`。他Agent差分は一切addしない。
- メッセージ: `KEY-PHRASE-4PLUS1-TOPIC-PHRASE-PRODUCTION-01 修正1回目: ユーザー既決(Strategy L retry 2回+報告/DB Hybrid backup補完/runner-up DEFERRED)+Opus L2 SHOULD_FIX反映`、trailer `Management-ID: KEY-PHRASE-4PLUS1-TOPIC-PHRASE-PRODUCTION-01`。`git push origin main`。

## 報告(RESULT_PACKET項目)

T-0結果/既決事項→実装の照合表/Opus所見→対応の照合表/Prompt最終文言逐語/schema差分/検証結果(test・regression[S3解消確認]・実データ: backup補完の実例、retry 2回目の実例と報告記録)/cost実測/Dangling Reference Check/Gate 3再確認表(Production正式path・retry/fallback/regeneration・runtime evidence・regression/negative test・telemetry・SSOT・PM_GOVERNANCE[該当なし]・Git・Dangling)/STOP・新規USER_DECISION候補/commit hash/raw URL。ユーザー向け表記はStandard/Advanced。
