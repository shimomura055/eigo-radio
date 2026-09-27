# KEY-PHRASE-DB-HYBRID-FAMILY-X-PRODUCTION-WIRING-01 委任文(全文)

管理ID: KEY-PHRASE-DB-HYBRID-FAMILY-X-PRODUCTION-WIRING-01(新規、ユーザー正式採用 2026-09-27)。一時ファイル `docs/pm/ACTIVE_TASK_KPX1.md` / `docs/pm/RESULT_PACKET_KPX1.md`(commitしない)。委任文全文を `docs/pm/delegation_log/2026-09-27_KEY-PHRASE-DB-HYBRID-FAMILY-X-PRODUCTION-WIRING-01_01.md` に保存しcommitに含める。Guardrail **¥40**(runtime evidenceのみ。コード・testは¥0)。APIキーは環境変数のみ。

## ユーザー決定(逐語要旨、再質問しない)
- Family X: DB Hybrid方式(Trial-04 VALIDATED、er029)を **Production正式採用。Status VALIDATED → APPROVED_FOR_PRODUCTION**。Gate 3完了まではPRODUCTION_WIREDにしない(判定はFable)。
- 基本方針: **Primary=DB Hybrid、Fallback=現行Strategy L全文方式**。Family XのProduction正式初回pathへ配線。retry/fallback/regenerationとの整合。**Trial専用scriptのまま残さない**(Production moduleへ昇格)。
- 現行Strategy L: 即時削除しない、fallbackとして残す、DB Hybrid failure時のfallback条件を明示、fallbackが勝手に通常経路化しないようtelemetryで観測可能に、旧方式と新方式の責務をSSOTに明記。
- 必須確認: shortlist生成 / important term保持 / rare・technical single word / phrase・idiom・phrasal verb優先 / source_sentence・source_span整合 / dialogue・quote segmentation修正がFamily X通常記事にregressionを起こさないこと / 既知bug A〜E再発なし / cost / runtime model_id・routing / actual Production runtime evidence / 現行Strategy L fallback実発火または統合経路検証 / rollback可能性。
- 共有KP層変更 → 実装後に**Mandatory Opus L2**(Fableが発火)。BLOCKER解消前にPRODUCTION_WIRED宣言しない。
- 並行ルール: **Trial-04挙動(er029 commit 57b61273)をbaselineとして固定**。Family Z Trial(別Agent、er029をread-only importで並行実行中)の都合でCore(candidate generation / shortlist logic / common validator)を変更しない。Core変更が必要なら理由・影響範囲・regressionを明示しSTOP。

## 先出しRead
- `KEY-PHRASE-DB-HYBRID-TRIAL-04_REPORT.md`、`er029_key_phrase_db_hybrid_trial_04_{stage1,run,test}.py`(baseline)、`er028_*`(確定版方式)、`KEY-PHRASE-DB-HYBRID-TRIAL-03_REPORT.md` §9(cost)
- 現行Production KP経路: `er003_key_words_production.py`(Strategy L、`SELECTOR_MODEL`→`er006_model_routing_contract_01.require_model`)、`er003_key_words_canonicalization.py`、Family X text runner `er019_family_x_entertainment_production_runner_01.py` のKP呼び出し、Key Phrase structural gate / source consistency gate(`KEY-PHRASE-SOURCE-CONSISTENCY-GATE-01`)、`qa_traceable_contiguous_span`、KP関連test
- CURRENT_SPEC「Key Phrase」関連節(Grep)、`docs/pm/PM_GOVERNANCE.md` Gate 3

## Phase 1(本委任): 昇格+opt-in配線+単体/統合test+最小runtime evidence
1. **Production module新設** `er030_key_phrase_db_hybrid_core_01.py`(Core: er029 stage1のcandidate generation/shortlist/validator を**ロジック無変更**で昇格。er029との等価性testで固定: 12本文のstage1_debug.jsonをfixtureにしshortlistが一致)+ `er030_key_phrase_db_hybrid_selector_01.py`(compact shortlist prompt→Strategy L 1回、canonicalization/既存Gateへ接続)。er029/er028/er027は無変更で残す(Trial記録)。
2. **配線**: `er003_key_words_production.py`(または適切な入口)に `kp_backend`(`"strategy_l"`既定 / `"db_hybrid"`)のopt-in引数を追加。Family X text runnerのKP呼び出しだけが `"db_hybrid"` を渡す。**既定はstrategy_lのまま**(Family A/B/C legacy不変。並走中のFamily X音声Agentが既定経路でsmall_bag B1B KP再選定を1回行うため、既定挙動を変えない)。
3. **Fallback設計**: DB Hybrid failure条件を明示(例: shortlist件数<閾値 / structural gate INVALID / selector例外 / cost guard超過)→ 現行Strategy L全文方式へfallback。telemetry(`er030_output/kp_backend_telemetry_01/telemetry.jsonl` 等、記事・レベル・backend・fallback理由・cost・model_id)で観測可能に。retry/regeneration(KP再選定)でも同じ入口を通ることを確認。rollback=`kp_backend` 既定値/Family X runner引数の1箇所。
4. **test**: er029等価性(12本文)、fallback発火(強制failure注入)、Family X通常記事に対するdialogue/quote分割の無回帰(Meta/Hormuz/small_bag 6本文でsentence unit数がTrial-03と一致)、bug A〜E fixture、legacy既定不変。`run_project_regression.py`(既知失敗以外なし)。
5. **runtime evidence(Guardrail ¥40)**: Family X既存記事(Meta A2/B1B、Hormuz A2/B1B)で新入口を **evidenceモード**(既存Production artifactの `keywords*.json` を上書きしない、出力は `er030_output/family_x_kp_db_hybrid_evidence_01/`)で実行し、model_id(routing contract経由、実測usage log)、cost、shortlist、最終5件、Gate通過、fallback非発火を記録。**fallback実発火**は強制failure注入で1本文分実測(¥1程度)。
6. **SSOT**: CURRENT_SPEC(Key Phrase節: Primary DB Hybrid / Fallback Strategy L の責務・fallback条件・telemetry・Family X限定・APPROVED_FOR_PRODUCTION、PRODUCTION_WIRED未到達明記)、DECISION_LOG(ユーザー決定エントリ)、OPEN_ITEMS(Trial-04留保①〜④をPM追跡OPENへ、shadow比較観測)、REPORT_LEDGER。**SSOT編集直前に `git status` で他Agentの未commit差分(SSOT 3点)を確認、あれば最大10分待ち。**
7. REPORT `KEY-PHRASE-DB-HYBRID-FAMILY-X-PRODUCTION-WIRING-01_REPORT.md` 新設: 既存資産照合、設計、diff要約、test、runtime evidence、Gate 3チェックリスト表(各項目evidence/未了)、Opus L2申し送り(共有KP層変更点と懸念)、rollback手順。

Git: 新規module・test・fixture・evidence出力・SSOT 4点・REPORT・delegation_logのみpath指定add(`git add -A`禁止、他Agent[er031_*, er019_family_x_audio_*, er003_v1_*, er007_*, er011_*]のstageを外さない、index.lockリトライ)。トレーラー `Management-ID: KEY-PHRASE-DB-HYBRID-FAMILY-X-PRODUCTION-WIRING-01`。push origin main。reset/amend/rebase/force push禁止。RESULT_PACKETに費用・commit hash・変更ファイル・Gate 3表要約・Opus申し送りを記載。
