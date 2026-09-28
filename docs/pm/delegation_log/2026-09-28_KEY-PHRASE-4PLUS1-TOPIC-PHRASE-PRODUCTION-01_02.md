## 管理ID

KEY-PHRASE-4PLUS1-TOPIC-PHRASE-PRODUCTION-01(Phase B: 最小実装+検証)。一時ファイルは `docs/pm/ACTIVE_TASK_KP41B.md` / `docs/pm/RESULT_PACKET_KP41B.md`(commitしない)。並行タスク衝突確認: 他Agentが `er021_*`・`er006_preprod_hardening_01_validation.py`・`er006_secondary_asr_01.py`(ASR包括対策)、`TTS-GEMINI-3.8-FLASH-LITE-*-02_REPORT.md`・`er033_output/`・`er019_output/`(Flash-Lite Assembly)、SSOT4点(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/`docs/pm/REPORT_LEDGER.md`、別Agentが反映作業中)を編集中。本タスクのコード対象(`er003_key_words_*`、`er030_*`、`er003_v1_n3_01_scaffold_generate.py`、prompt template)は commit `9fa6f388`/`53411d21` で他Agent分がcommit済み。開始時に `git status --porcelain` で本タスク対象ファイルに未commit差分が無いことを確認し、あれば触らずRESULT_PACKETへ記録してSTOP。SSOT4点は作業末尾で `git status --porcelain` 確認→差分あれば最大10分待機→解消しなければ追記案をRESULT_PACKETへ書いて未反映のまま報告(他Agent差分をcommit/unstageしない)。

## 性質/到達上限Status/禁止事項

- 性質: Production配線(ユーザー承認済み `APPROVED_FOR_PRODUCTION` の共通Key Phrase仕様変更)。到達上限Status: Sonnetは `PRODUCTION_WIRED` を宣言しない(Fable Gate 3判定。実装後にMandatory Opus L2レビューがある)。
- 費用: 上限¥80(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。
- 禁止: Production記事ディレクトリ(`er019_output/`、`er026_output/`、`er012_output/`等の既存記事artifact)の `keywords*.json` を上書きしない(検証出力は新規 `er035_output/kp_4plus1_evidence_01/` 配下のみ)。TTS実行なし。Web検索なし。legacy Family A/B/C のrunner・コードは編集しない(本文をread-only入力として使うのみ)。Family固有のrule・分岐・Family別Promptを追加しない(ユーザー明示: 本変更はA2/B1・Editorial Familyを横断する共通Key Phrase仕様の正式変更であり、共通Production Key Phrase経路へ適用する。「Family/3V専用Key Phrase仕様を新設しない」STOP条件とは競合しない)。追加LLM callを新設しない(既存selector call内で処理)。ユーザーが禁止した独自Product rule(固有名詞優先/専門語優先/タイトル語優先/出現回数N回以上/難易度/CEFR外優先/名詞優先/必ず複合語/カテゴリ除外・優先)をPrompt・コード・validatorに入れない。必要と感じたら実装せず `USER_DECISION_REQUIRED` としてSTOP報告。APIキー本文を表示・log・commit・報告に書かない。履歴書き換え禁止、`git add -A` 禁止。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0: 受領した委任文を `docs/pm/delegation_log/2026-09-28_KEY-PHRASE-4PLUS1-TOPIC-PHRASE-PRODUCTION-01_02.md` へ保存し、`.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-28_KEY-PHRASE-4PLUS1-TOPIC-PHRASE-PRODUCTION-01_02.md --json-out docs/pm/delegation_log/2026-09-28_KEY-PHRASE-4PLUS1-TOPIC-PHRASE-PRODUCTION-01_02.md_check.json` を実行し、結果をRESULT_PACKETへ1行記録する(FAILでも継続)。
T-2: 本委任はTTSを伴わない(TTS実行禁止)。
T-3: 費用上限は上記「性質」欄の定型文に従う。

## ユーザー指示(原文)

Phase A委任文(`docs/pm/delegation_log/2026-09-28_KEY-PHRASE-4PLUS1-TOPIC-PHRASE-PRODUCTION-01_01.md`)の「ユーザー正式決定」節を正本として参照(逐語要旨: 5枠=4重要語+1 Topic Phrase/Word。Topic定義「汎用性・一般的な学習重要度は必ずしも高くないが、その記事に特有であり、事前に意味・用法・音を理解しておくことで本文全体を追いやすくなるワードまたはフレーズ」、中心質問「この語・表現を事前に理解していると、この記事の本文を明確に追いやすくなるか?」。固有名詞枠ではない・例示hard-code禁止。追加表示用データは後段UI向け構造化データとして保持、UI新設しない。Strategy L全面置換しない、既存Gate群を壊さない、Important 4枠の品質低下なし)。追加ユーザー指示(2026-09-28): 「本変更はA2/B1・Editorial Familyを横断する共通Key Phrase仕様の正式変更であり、既存の『Family/3V専用Key Phrase仕様を新設しない』というSTOP条件とは競合しない。Family固有ルールは追加せず、共通Production Key Phrase経路へ適用すること。」

## Fable判断(Phase A設計書 `docs/pm/design_kp_4plus1_topic_phrase_01.md` §F STOP候補への回答、これに従う)

- 命名: `key_phrase_role`(enum `important|topic`)を採用。`keywords_runtime_metadata.json` へ `selection_contract="4plus1_v1"` を追加(DB Hybrid経路)。Strategy L経路にも同等のcontract表示が既存metadataにあれば同名で追加、無ければ `keywords*.json` トップレベルへ最小追加(既存フィールド無変更)。
- F-1(Stage 1候補プールにTopic候補が無い可能性): 新しい候補生成ロジック・新DB・新ヒューリスティックは**作らない**。既存プールのまま実装し、検証(観点7)で「Topic該当語がStage 1候補に存在したか」を記事ごとに記録。存在しない記事が観測されたら、その事実と選定LLMがどう振る舞ったか(candidate外を選べない契約なのでimportant寄りのtopicになるか等)を記録し、対処案は実装せず報告(USER_DECISION候補)。
- F-2(guidance文言の2軸並存): 既存guidance「重要語区分から最低1件」は**削除・変更しない**(既存承認済みrule)。Topic追記文言に「`key_phrase_role` は候補区分(重要語/phrase/word)とは独立した、選定後の役割ラベルである」旨の1文を加え、軸の混同を防ぐ。それ以上の文言整理はしない。
- F-3(4+1不成立時の経路): **既存の失敗経路を使う**。validator(`validate_min_unit_selection`)へrole集計チェックを追加し、不成立は既存 `KEY_WORDS_STRUCTURE_INVALID` に合流。Strategy L側は既存max_attempts=2内で再試行。DB Hybrid側は既存の「validator INVALID → `DbHybridFailure`(fallback_allowed=True)→ Strategy L fallback」に合流(新reason_codeは telemetry識別のために `ROLE_STRUCTURE_INVALID` を追加してよいが、分岐先は既存INVALIDと同一にする=新しい分岐点を作らない)。5件経路(`expected_item_count == PRODUCTION_ITEM_COUNT`)のみ評価、B2研究版10件はガード。
- F-4(Strategy L側の5枠外候補): **本Phaseでは実装しない**(新出力契約+件数判断はユーザー判断)。DB Hybrid側は既存 `db_hybrid_stage1_debug.json`/`shortlist_with_ids` から「選ばれなかった候補」を `keywords_runtime_metadata.json`(または同ディレクトリの新規 `kp_auxiliary_candidates.json`)へ「未検証・参考候補」フラグ付きで**件数上限なし・順序は既存shortlist順**で構造化保持するのみ(表示件数・配置はユーザー判断、決めない)。Strategy L経路は `auxiliary_candidates: null` + `reason: "not_available_strategy_l"` を記録。
- F-5(UI): 新規UI実装なし。既存Family X/Z向けUI経路なしと確認済みのため配線もなし。
- Redundancy QA/source gate/TTS reading copy/TTS本体は無改修(Phase A確認済み)。`merge_canonicalization_result()` のpassthroughリストへ `key_phrase_role` を追加(見落とし防止)。旧artifact(`key_phrase_role`欠落)は旧contractとして後方互換。

## 事前指定Read一覧

- `docs/pm/design_kp_4plus1_topic_phrase_01.md`:100-342(B〜G節)
- `er003_key_words_min_unit.py`: `_ITEM_SCHEMA_PROPERTIES`(115-135行)、`validate_min_unit_selection`(397-460行付近、Grepで位置再確認)
- `er003_key_words_production.py`:55-70(schema参照)+ `run_production_selection_gate` 定義(Grepで位置特定→該当範囲)
- `er003_key_words_canonicalization.py`:571-628(`merge_canonicalization_result`)
- `er003_v1_translator_briefs/b1_p2_keywords_l_prompt_template.txt` 全文(26行)
- `er030_key_phrase_db_hybrid_source_reference_contract_01.py`:100-190(`build_item_schema_properties`、`_FAMILY_X_SOURCE_REFERENCE_SELECTION_GUIDANCE`)+ validator/`DbHybridFailure` reason_code定義(Grep `reason_code` →該当範囲)
- `er030_key_phrase_db_hybrid_selector_01.py`:130-160(`extract_static_instructions`)、455-600(`run_db_hybrid_selection` のartifact出力・runtime_metadata)
- `er003_v1_n3_01_scaffold_generate.py`: `run_key_phrases`(Grep `def run_key_phrases` →該当範囲、Redundancy retry loop)
- 既存evidence runnerの雛形: `er030_output/family_x_kp_source_reference_contract_evidence_01/` の生成元script(Grep `family_x_kp_source_reference_contract_evidence_01` in `er030_*evidence*_run*.py`)→ 全文(新規evidence scriptの雛形にする)
- 検証入力(read-only、article本文のみ): Family X News = Meta A2/B1B・Hormuz A2/B1B(`er019_output/family_x_audio_production_wiring_01/` 配下、Grep `article.md`/`article_text` で特定)、Family Z Fiction = Melos A2(`er026_output/` 配下、既存evidenceで使用した本文)、Voices(legacy B、read-only入力)= `er012_output/user_test_voices_a2_minimal_01/ai_hiring_3v_a2/a2/article.md` と同記事のB1本文(同ディレクトリ配下をGlob)、Fiction Family C(legacy、read-only入力)= twins/Future Story本文(`er0*_output/` をGrep `twins`)。各1レベル以上、合計10〜14記事×レベル。

## 事前指定Grep一覧+追記位置・更新位置の手順

- Grep `_ITEM_SCHEMA_PROPERTIES` in `er003_key_words_min_unit.py` → 末尾要素の直後へ `key_phrase_role` を追加(enum、description=ユーザー定義の逐語+「候補区分とは独立した役割ラベル」)。
- Grep `display_phrase.*重複|rank.*重複` in `er003_key_words_min_unit.py::validate_min_unit_selection` → 同ブロック直後へrole集計チェック(設計書B-2のコード案)を追加。
- Grep `source_reference_contract` in `er003_key_words_canonicalization.py` 615-623行のpassthroughリスト → `key_phrase_role` を追加。
- Grep `{{article` または `ARTICLE` placeholder in `b1_p2_keywords_l_prompt_template.txt` → placeholderより前(静的instructions内)へTopic追記文言(設計書B-3案+F-2の1文)を追加。**例示語・優先カテゴリを書かない**。
- Grep `fallback_allowed=True` in `er030_key_phrase_db_hybrid_source_reference_contract_01.py`/`_selector_01.py` → validator INVALID経路に `ROLE_STRUCTURE_INVALID` reason_codeを合流(分岐先同一)。
- Grep `keywords_runtime_metadata` in `er030_key_phrase_db_hybrid_selector_01.py` → `selection_contract`・`role_counts`・`auxiliary_candidates` を追加。
- Grep `redundancy` in `er003_v1_n3_01_scaffold_generate.py::run_key_phrases` → 各attemptで `role_counts` をtelemetry(`er030_output/kp_backend_telemetry_01/telemetry.jsonl` 既存行に追加フィールド)へ記録。
- Dangling Reference Check: Grep `key_phrase_role|4plus1|ROLE_STRUCTURE_INVALID|auxiliary_candidates` 全体 → 定義・参照・test・REPORT・SSOT案が整合しているか一覧化。

## 実行コマンド全文

- 単体test: `.venv\Scripts\python.exe -m pytest er003_key_words_min_unit_4plus1_test_01.py er030_key_phrase_db_hybrid_source_reference_contract_01_test.py er030_key_phrase_db_hybrid_family_x_production_wiring_01_test.py er003_key_words_canonicalization_test.py -q`(新規test `er003_key_words_min_unit_4plus1_test_01.py` を作成: schema伝播、validator 4+1 PASS/FAIL、B2 10件ガード、canonicalization passthrough、DB Hybrid reason_code合流、旧artifact後方互換、Strategy L structure invalid→retry合流。既存test名が異なる場合はGlobで実名に置換し実行したコマンドを逐語記録)
- 回帰: `.venv\Scripts\python.exe run_project_regression.py`(全件1回、既知baseline failed=7/errors=2 と照合し新規regression 0件を確認)
- 検証evidence: 新規 `er035_kp_4plus1_topic_phrase_evidence_01_run.py`(既存evidence script雛形を流用、Production経路 `run_key_phrases` 相当をDB Hybrid[Family X本文]/Strategy L[Z・legacy本文、およびDB Hybrid fallback強制1件]で呼ぶ)を `.venv\Scripts\python.exe er035_kp_4plus1_topic_phrase_evidence_01_run.py --out-dir er035_output/kp_4plus1_evidence_01 --budget-jpy 80` で実行(引数名は雛形に合わせて実装、実行したコマンドを逐語記録)。出力: 記事×レベルごとに `keywords_canonicalized.json`・`keywords_runtime_metadata.json`・`kp_auxiliary_candidates.json`、集計 `summary.json` と `summary.md`(10観点表: 1構造PASS 2 Topic該当性の主観判定[中心質問に照らし、選定理由をそのまま転記] 3固有名詞への偏り 4 Important 4件の品質比較[同記事の既存Production KP 5件との差分] 5 Redundancy QA発火率 6 canonicalization PASS率 7 Stage 1候補にTopic該当語が存在したか[DB Hybridのみ] 8 retry発火率・cost 9 fallback後の4+1維持 10 補助候補データの有無・件数)。

## SSOT追記文

SSOT4点が編集可能な場合のみ適用、不可なら追記案をRESULT_PACKETへ:
- `CURRENT_SPEC.md` Key Phrase節末尾: 「**4+1構成(2026-09-28、KEY-PHRASE-4PLUS1-TOPIC-PHRASE-PRODUCTION-01、ユーザー承認 `APPROVED_FOR_PRODUCTION`、Sonnet実装済み・`PRODUCTION_WIRED` 判定はFable待ち)**: Key Phrase 5枠=重要語・重要表現4+Topic Phrase/Word 1。Topic定義・中心質問はユーザー定義の逐語のみ(固有名詞枠ではない、例示hard-code禁止)。実装: `key_phrase_role`(`important|topic`)を共通schema `er003_key_words_min_unit._ITEM_SCHEMA_PROPERTIES` へ追加(Strategy L/DB Hybrid両経路・全Familyへ伝播)、prompt template 1箇所追記、構造validatorでtopic=1/important=4を検証し不成立は既存 `KEY_WORDS_STRUCTURE_INVALID` 経路へ合流、canonicalization passthrough、`selection_contract="4plus1_v1"`。追加表示用データはDB Hybrid経路のみ既存shortlistから未検証・参考候補として構造化保持(件数・UIはユーザー判断未決)、Strategy L経路は未提供(ユーザー判断待ち)。追加LLM callなし、音声側無改修。」
- `DECISION_LOG.md` 新規エントリ `## KEY-PHRASE-4PLUS1-TOPIC-PHRASE-PRODUCTION-01: Phase A設計+Phase B最小実装(2026-09-28)`: 性質/Fable判断(F-1〜F-5への回答を上記のとおり転記)/実装/検証結果/STOP該当/根拠。
- `OPEN_ITEMS.md`: 新規OPEN「Strategy L経路の5枠外候補データ(runner_up契約)と表示件数・UI配置はユーザー判断待ち」+検証で観測されたSTOP候補があれば追加。
- `docs/pm/REPORT_LEDGER.md`: 本ID行新設(Phase A `53411d21`、Phase B commit hash、Opus発火=未[Fable判断待ち])。

## Git(明示add対象・コミットメッセージ・trailer)

- add対象: 変更した `er003_key_words_min_unit.py`、`er003_key_words_canonicalization.py`、`er003_v1_translator_briefs/b1_p2_keywords_l_prompt_template.txt`、`er030_key_phrase_db_hybrid_source_reference_contract_01.py`、`er030_key_phrase_db_hybrid_selector_01.py`、`er003_v1_n3_01_scaffold_generate.py`(必要時のみ)、新規test、`er035_kp_4plus1_topic_phrase_evidence_01_run.py`、`er035_output/kp_4plus1_evidence_01/`(json/md、音声なし)、`KEY-PHRASE-4PLUS1-TOPIC-PHRASE-PRODUCTION-01_REPORT.md`(新規: §1現行経路要約 §2実装 §3 Prompt追記文言逐語 §4 schema/validator/失敗経路 §5 追加表示データ §6検証10観点表 §7 cost §8 test/regression §9 Dangling Reference Check §10 STOP/USER_DECISION候補 §11 Gate 3表[Sonnet記入、判定欄空欄])、delegation_log `_02.md` と `_check.json`、SSOT4点(編集できた場合のみ)。
- コミットメッセージ: `KEY-PHRASE-4PLUS1-TOPIC-PHRASE-PRODUCTION-01 Phase B: Key Phrase 4+1(Topic Phrase)最小実装+全Family共通schema/validator配線+検証evidence`、trailer `Management-ID: KEY-PHRASE-4PLUS1-TOPIC-PHRASE-PRODUCTION-01`。`git push origin main`。index.lock競合時はretry。

## 報告(RESULT_PACKET項目)

T-0結果1行/変更ファイル一覧/Prompt追記文言逐語/schema・validator・失敗経路の差分要約/追加表示データ方式とartifact例/検証10観点表(記事×レベル)と各記事のTopic Phrase実選定結果+選定理由/Important 4件の既存比較/cost実測(call数・¥)/test・regression結果/Dangling Reference Check結果/STOP該当・USER_DECISION候補(F-1観測含む)/SSOT反映状況(未反映なら追記案)/commit hash/raw URL一覧。ユーザー向け表記はStandard/Advanced(A2/B1/B1Bは内部ID)。
