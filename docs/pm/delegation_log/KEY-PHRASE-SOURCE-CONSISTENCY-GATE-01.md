## 管理ID

KEY-PHRASE-SOURCE-CONSISTENCY-GATE-01(ユーザー正式決定2026-09-18、OPEN-170採用: Gate (a) Assembly直前の`source_span`本文実在確認、Gate (b) 他記事Key Phrase流用時の供給元本文sha256一致必須化)。並行Agentなし(PM-GOVERNANCE-DISTRIBUTION-PATH-PAGES-01は完了・push済み[`86c34946`]、Fable確認済み)。本タスクはTTS/ASR/Ledger書き込みを行わない(Gateはローカル比較のみ)ためaudio_stage.lockは不要(存在していたらSTOP)。`docs/pm/ACTIVE_TASK.md`の固定ヘッダ+要約を本タスク内容で更新してから開始。

## 性質/到達上限Status/禁止事項

- 性質: Production実装(`APPROVED_FOR_PRODUCTION`済み)。到達してよい最大Status: `PRODUCTION_WIRED`(下記Closeout条件全完了時のみ。1つでも未完なら`USER_DECISION_REQUIRED`/`STOPPED`として報告し、SSOTには未配線と記す)。
- 費用: 外部API支出禁止(¥0)。Gate実装・テスト・runtime evidenceはすべてローカル比較で行う(既存artifactに対するオフライン検証のみ。新規TTS/ASR/LLM呼び出し禁止)。
- 禁止: 記事本文・音声・Key Phrase asset・player・`user_test/`配下の変更禁止。既存Production関数のシグネチャ変更は後方互換を保つ(既存呼び出しが壊れない)。`git add -A`/`stash`/`amend`/`rebase`/`force push`禁止。「Claude判断で追加仕様を広げない」: Gate (a)(b)以外の新機能・新QA項目・スキーマ変更(KP assetへの新フィールド追加等)は行わない。必要と感じた場合はUSER_DECISION_REQUIRED候補として報告のみ。
- STOP条件: (1)Gateを共通の経路に置けない(Production Familyごとに独立したAssembly実装で共通化不能)、(2)既存20 canonical assetのいずれかがGate (a)でFAILする(=既存Productionに未知の不整合。修正せず報告)、(3)Gate挿入が既存テストを壊し後方互換で解決できない、(4)新Product仕様判断が必要(例: `source_span`を持たない旧形式assetの扱い)。該当時は該当時点までをcommitし報告。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
(本委任の保存先: `docs/pm/delegation_log/KEY-PHRASE-SOURCE-CONSISTENCY-GATE-01.md`)

## ユーザー指示(原文)

「1. Key Phrase追従漏れ防止Gate → 採用する。Productionへ以下2 Gateを実装してください。(a) Assembly直前に keywords_canonicalized.json の source_span が現行本文に実在するかを機械確認する。1件でも不在ならFAILで停止すること。(b) 他記事からKey Phraseを流用する経路では、供給元本文sha256一致を必須化する。不一致なら流用せずFAILで停止すること。今回見つかった『本文平易化後にKey Phraseが古いまま残る』事故の再発防止が目的。API追加支出は発生させないこと。重要: ユーザー正式採用済みなので、APPROVED_FOR_PRODUCTIONとして扱う。ただし、Gate実装・Production正式path反映・必要test・runtime evidence・CURRENT_SPEC / DECISION_LOG / OPEN_ITEMS / Git反映まで完了して初めてPRODUCTION_WIREDとする。retry / fallback / regeneration等、関連する後続経路でも同じ不整合を起こさないことを確認する。」「Claude判断で追加仕様を広げないこと。新しい問題・新しい仕様候補が出た場合は、USER_DECISION_REQUIREDでSTOPして報告すること。」

## 事前指定Read一覧

1. `CURRENT_SPEC.md` L583(Key Phrase選定(A2)行)、L1135(選定元行)、Grep `Assembly|Audio Validation Gate|MISSING_MANDATORY_A2_SLOWDOWN|HUMAN_APPROVED` → Assembly段のGate定義行(既存Gateの記述様式に合わせて追記するため、該当行+前後5行)
2. `CURRENT_SPEC.md`: Grep `PRODUCTION_WIRED` で、現在Production配線済みの記事生成経路(News path/B-Family 2V・3V A2/B1/Family C/Family A Trend・Discovery)の行を特定し、各経路のdriver/primitive名を把握(全文Read禁止)
3. `er003_v1_n3_01_scaffold_generate.py` L303付近(`run_key_phrases`、`keywords_canonicalized.json`の出力schema: `used_form`/`source_span`/`source_sentence`/`qa_*`のキー名を確認)
4. `er003_v1_n3_01_assemble.py`: Grep `def |keywords_canonicalized|key_phrase|parts.json|article` → Assembly入口関数とKey Phrase asset読込箇所
5. `er012_b_family_voices_a2_production_01.py` L565-640(`reuse_key_phrases_a2`/`run_key_phrases_a2_from_own_text`)、L769付近(`build_a2_voices_timeline`)、`er012_b_family_voices_production_01.py` L612/L747(`build_b1_voices_timeline`/`_3v`)、`er012_b_family_production_runner_01.py` L190/L704(`reuse_key_phrases`/`_3v`)・L407/L834/L1502/L1782(`run_assembly*`)、`er012_b_voices_3v_a2_user_test_01.py` L571/L645
6. News path driver例: `er014_output/user_test_news_convenience_ai_01/convenience_ai/run_pipeline.py`: Grep `assemble|key_phrase|keywords` → Assembly呼び出し箇所。Family C: Grep `def run_assembly|assemble` in `er013_*.py`(Production driver)。Family A: `er011_family_a_completion_a2_trend_end_to_end_01_run.py` L201付近、Discovery: `er014_output/four_type_observation_01/discovery/run_discovery_audio_completion.py` L290付近
7. 後続経路: `er010_ledger_local_rewrite_09.py`(Local Rewrite: 本文が変わる経路。Grep `def |article|parts`)、`er011_human_review_lock_01.py` `approve_regenerate`(segment再生成)、`apply_a2_slowdown_postprocess`(Grep in `er003_v1_n3_01_assemble.py`)、Phase Dの`er012_b_voices_a2_kp_fix_free_address_01.py`/`er012_b_voices_3v_a2_kp_fix_ai_hiring_01.py`(KP再生成driver、Grep `def |assemble|build_`)
8. 既存テストの様式: `er003_test_key_words_canonicalization.py` L1-60(テスト命名・import様式)、`run_project_regression.py`: Grep `pattern|glob` → 収集規則
9. `docs/pm/PM_GOVERNANCE.md`: Grep `2-1\. 既存対策|Reconciliation Check` → 該当節(新Gate追加前の既存対策確認手順)
10. `user_test/translations/index.json` 全文(20 canonical assetのpath: runtime evidence対象)、`docs/pm/RESULT_PACKET_SCRIPT_READABILITY_PROD_01.md` L166-178(不整合の原因: Free-Address=旧版byte reuse、AI Hiring=`reuse_key_phrases_a2`によるB1流用)

## 事前指定Grep一覧+追記位置・更新位置の手順

- Grep `keywords_canonicalized` in `er003_v1_n3_01_assemble.py`・`er012_b_family_voices_a2_production_01.py`・`er012_b_family_voices_production_01.py`・`er012_b_family_production_runner_01.py`・`er013_*.py`(Production driver)・`er011_family_a_completion_a2_trend_end_to_end_01_run.py`・`er014_output/**/run_pipeline.py` → Assembly直前にKey Phrase assetを読む箇所を列挙(Gate (a)の挿入候補)。
- Grep `reuse_key_phrases|kp_source_dir|copy.*key_phrases|shutil\.copy.*keywords` in `*.py`(`er014_output/**/runner_before_v2.py`等の履歴コピーは除外して報告) → Gate (b)の対象経路を列挙。
- 実装方針(共通化): 新規モジュール`er003_key_phrase_source_gate_01.py`に (a)`check_key_phrase_source_presence(article_text: str, keywords_path: str) -> dict`(各Key Phraseの`source_span`(無ければ`source_sentence`→無ければSTOP条件(4)として報告)を正規化[大小文字・apostrophe種・HTML entity・連続空白・ダッシュ種]して本文に部分文字列として実在するかを判定。結果`{status: PASS|FAIL, total, present, missing:[{used_form, source_span, reason}], normalized_rules}`。FAILは呼び出し側で`RuntimeError("KEY_PHRASE_SOURCE_MISSING: ...")`により停止)、(b)`assert_key_phrase_reuse_source_matches(source_article_text: str, target_article_text: str) -> dict`(sha256比較、不一致なら`RuntimeError("KEY_PHRASE_REUSE_SOURCE_MISMATCH: ...")`)。Gate結果は呼び出し側の`audit/key_phrase_source_gate.json`へ保存。
- 挿入位置(Gate (a)): Production各Familyが共通で通るAssembly primitiveの入口(`er003_v1_n3_01_assemble.py`のAssembly関数、B-Family `build_a2_voices_timeline`/`build_b1_voices_timeline(_3v)`/`build_a2_voices_timeline_3v`の入口、Family C・Family A・DiscoveryのProduction Assembly入口)。「本文」は当該Assemblyが使う本文テキスト(parts.json本文/article.md)を用いる。共通primitiveが無いFamilyは各Production driverの`run_assembly`入口に同じ1呼び出しを追加(コピー実装は禁止、必ず新規モジュールを呼ぶ)。Trial/履歴driver(`er014_output/**`のコピー、`*_trial_*`)は対象外として一覧報告。
- 挿入位置(Gate (b)): `er012_b_family_voices_a2_production_01.reuse_key_phrases_a2`、`er012_b_family_production_runner_01.reuse_key_phrases`/`reuse_key_phrases_3v`、その他Grepで見つかった流用関数。供給元article本文(kp_source_dirと同階層のarticle.md等)と流用先article本文のsha256を比較し、不一致で停止。既存呼び出しが供給元本文pathを渡していない場合は関数内で供給元dirから解決(解決できなければFAIL=流用不可)。
- 後続経路との整合確認(実装ではなく確認+必要最小の呼び出し追加): Local Rewrite後(本文が変わる)→Assemblyで(a)が必ず走ることを確認。Human Review `approve_regenerate`(segment再生成)→再Assembly時に(a)が走ることを確認。`apply_a2_slowdown_postprocess`(本文無変更)→対象外を確認。KP再生成driver(Phase D kp_fix)→Assembly入口で(a)が走ることを確認。retry/fallback(TTS retry cascade)→本文無変更のため対象外を確認。結果を表(経路/本文変更の有無/Gate (a)通過箇所/Gate (b)該当有無)で報告。
- SSOT追記位置: `CURRENT_SPEC.md`のKey Phrase選定(A2)行(L583)の直後または「選定元」行(L1135)近傍に新行「Key Phrase source整合Gate」(`PRODUCTION_WIRED`、内容(a)(b)、モジュール名、FAIL時の停止、旧形式assetの扱い)。Assembly Gate群の記述箇所にも1行参照追記。`DECISION_LOG.md`索引+本体`## KEY-PHRASE-SOURCE-CONSISTENCY-GATE-01`。`OPEN_ITEMS.md` OPEN-170をCLOSED(実装commit・evidence参照)。`ARTIFACT_REGISTRY.md`に新モジュール・テスト・evidence行。

## 実行コマンド全文

- 委任文検証: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\KEY-PHRASE-SOURCE-CONSISTENCY-GATE-01.md --json-out docs\pm\delegation_log\KEY-PHRASE-SOURCE-CONSISTENCY-GATE-01.md_check.json`
- runtime evidence(a)正例: `.venv\Scripts\python.exe er003_key_phrase_source_gate_01.py --index user_test\translations\index.json --out docs\pm\closeout_136_e2e\key_phrase_source_gate_01\gate_a_canonical20.json`(index.jsonの20 level[19 src]について、各srcの同階層/親階層から`keywords_canonicalized.json`と本文(parts.json/article.md)を解決してGate (a)を実行。期待: 20/20 PASS。CLIは新モジュール内に`if __name__=="__main__"`で実装)
- runtime evidence(a)負例(true positive証跡): `.venv\Scripts\python.exe er003_key_phrase_source_gate_01.py --keywords er012_output\editorial_b_family_voices_a2_production_wiring_01\key_phrases\keywords_canonicalized.json --article er012_output\editorial_b_family_voices_a2_production_wiring_01\article.md --out docs\pm\closeout_136_e2e\key_phrase_source_gate_01\gate_a_old_free_address_a2.json`(旧Free-Address A2。keywords/articleの実pathはGlobで確認して実値に置換。期待: FAIL、missing 5件)。同様に旧AI Hiring A2(`er012_output\user_test_voices_a2_minimal_01\ai_hiring_3v_a2\`配下、期待: FAIL、missing 4件)。
- runtime evidence(b): `.venv\Scripts\python.exe -c "..."`で`assert_key_phrase_reuse_source_matches`を、(i)同一本文→PASS、(ii)旧AI Hiring A2の流用元(3V B1 `er012_output\editorial_b_voices_3v_audio_trial_01\b1b\article.md`)と流用先(旧AI Hiring A2 `a2\article.md`)→FAIL(実pathはGlobで確認)、の2ケースで実行し`gate_b_evidence.json`へ保存。
- 単体テスト: `.venv\Scripts\python.exe -m pytest er003_test_key_phrase_source_gate_01.py -q`(新規テスト: 正規化差[大小文字/apostrophe/entity/空白]でPASS、欠落でFAIL、`source_span`無し時の挙動、(b)一致/不一致、Assembly入口でRuntimeErrorになる統合テスト[本文をわざと改変したfixture])
- 回帰: `.venv\Scripts\python.exe run_project_regression.py --pattern "er0*_test_*.py"`(既知3件[er003_test_bad、er003_test_p2j_investigate×2]以外の新規失敗なし)
- 既存Production driverのdry確認: Gate挿入後、Assembly関数をimportして構文/読み込みが壊れていないことを`.venv\Scripts\python.exe -c "import er003_v1_n3_01_assemble, er012_b_family_voices_a2_production_01, er012_b_family_voices_production_01, er012_b_family_production_runner_01; print('ok')"`で確認(TTS/API呼び出しは発生しない)。

## SSOT追記文

- CURRENT_SPEC新行(案): 「| Key Phrase source整合Gate | (a) Assembly直前に`keywords_canonicalized.json`各項目の`source_span`が当該Assemblyの本文に実在するかを`er003_key_phrase_source_gate_01.check_key_phrase_source_presence`で機械確認し、1件でも不在なら`KEY_PHRASE_SOURCE_MISSING`で停止。(b) 他記事Key Phraseを流用する経路(`reuse_key_phrases*`)は供給元本文と流用先本文のsha256一致を`assert_key_phrase_reuse_source_matches`で必須化し、不一致なら`KEY_PHRASE_REUSE_SOURCE_MISMATCH`で停止(流用しない)。対象: Production配線済み全Family(News/B-Family 2V・3V A2/B1/Family C/Family A Trend・Discovery)のAssembly入口。Local Rewrite・segment再生成後の再Assemblyでも(a)が走る。API支出なし。背景: 2026-09-18 Free-Address A2/AI Hiring A2で本文平易化後にKey Phraseが未追従(OPEN-170)。 | `PRODUCTION_WIRED` | KEY-PHRASE-SOURCE-CONSISTENCY-GATE-01 | 2026-09-18 |」(実装結果に合わせて調整)
- DECISION_LOG本体: 決定(ユーザー原文引用)/実装(モジュール・挿入箇所一覧)/後続経路整合表/テスト/runtime evidence(20/20 PASS・旧2 asset FAIL)/回帰/費用¥0/Status。
- OPEN_ITEMS: OPEN-170 → CLOSED(実装commit SHA・evidence path)。

## Git(明示add対象・コミットメッセージ・trailer)

- commit 1(実装+テスト+evidence): 明示add `er003_key_phrase_source_gate_01.py`、`er003_test_key_phrase_source_gate_01.py`、Gateを挿入したProductionファイル(実際に変更したもののみ列挙)、`docs/pm/closeout_136_e2e/key_phrase_source_gate_01/*.json`。メッセージ: `KEY-PHRASE-SOURCE-CONSISTENCY-GATE-01: Assembly直前のKey Phrase source_span本文実在Gate(a)+流用時の供給元本文sha256一致Gate(b)をProduction経路へ実装、テスト+runtime evidence`
- commit 2(SSOT): 明示add `CURRENT_SPEC.md`、`DECISION_LOG.md`、`OPEN_ITEMS.md`、`ARTIFACT_REGISTRY.md`、`docs/pm/delegation_log/KEY-PHRASE-SOURCE-CONSISTENCY-GATE-01.md`(+`_check.json`)、`docs/pm/RESULT_PACKET_KEY_PHRASE_SOURCE_GATE_01.md`。メッセージ: `KEY-PHRASE-SOURCE-CONSISTENCY-GATE-01: SSOT反映+OPEN-170 close`
- trailer各commit: `Task-ID: KEY-PHRASE-SOURCE-CONSISTENCY-GATE-01`。push前後`git fetch origin`、最終main=origin/main確認、`git status --porcelain`で混入なし確認。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_KEY_PHRASE_SOURCE_GATE_01.md`(新規)に:
1. 最終Status(`PRODUCTION_WIRED`/`USER_DECISION_REQUIRED`/`STOPPED`+理由)
2. 2-1 Reconciliation Check結果(既存に同種Gateが無いことの確認)
3. Gate (a)実装: モジュール・関数・正規化ルール・FAIL挙動・挿入箇所一覧(ファイル:関数:行)
4. Gate (b)実装: 対象流用関数一覧・供給元本文の解決方法・FAIL挙動
5. Production経路カバレッジ表(Family/経路/Assembly入口/Gate (a)有無/Gate (b)該当有無)+対象外とした履歴・Trial driver一覧
6. 後続経路整合表(Local Rewrite/Human Review segment再生成/A2 slowdown/KP再生成driver/TTS retry・fallback/Fact Checker等: 本文変更の有無・Gate通過箇所)
7. 単体テスト結果(件数・PASS)
8. runtime evidence: Gate (a) 20 canonical asset 20/20 PASS(level別表)、旧Free-Address A2 FAIL(missing 5)、旧AI Hiring A2 FAIL(missing 4)、Gate (b) PASS/FAIL 2ケース
9. 回帰テスト結果(新規失敗0)
10. `source_span`を持たない旧形式assetの扱い(該当有無、あればUSER_DECISION_REQUIRED候補)
11. SSOT更新内容(CURRENT_SPEC行番号/DECISION_LOG/OPEN-170 CLOSED/ARTIFACT_REGISTRY)
12. Git commit SHA(1/2)、main=origin/main
13. 費用(¥0の確認)
14. USER_DECISION_REQUIRED候補・未解決事項
15. 一覧外Read(理由1行)、check_delegation_prompt結果
