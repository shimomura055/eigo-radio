管理ID: KEY-PHRASE-DB-HYBRID-FAMILY-X-PRODUCTION-WIRING-01(Sonnet修正1回目=Opus L2所見反映。**¥0、LLM/API呼び出しなし**、runtime evidence再取得不要)。一時ファイル `docs/pm/ACTIVE_TASK_KPX2.md` / `docs/pm/RESULT_PACKET_KPX2.md`(commitしない)。委任文全文を `docs/pm/delegation_log/2026-09-27_KEY-PHRASE-DB-HYBRID-FAMILY-X-PRODUCTION-WIRING-01_02.md` に保存しcommitに含める。

## 前提
REPORT `KEY-PHRASE-DB-HYBRID-FAMILY-X-PRODUCTION-WIRING-01_REPORT.md` に §7「Opus L2所見(逐語)」を先に追記(下記所見全文はRESULT_PACKET_KPX1の次に置かれたFable委任文=本ファイルの delegation_log から転記)。Fable判定: BLOCKER 3件解消前はPRODUCTION_WIRED不可。並行ルール: er029(Trial-04 baseline)・er032(Core v2 Trial-05、別Agent実行中)は変更禁止。er027/er028も変更禁止(Trial記録)。

## 必須修正(Opus L2所見)
- **B1 telemetry観測性**: `er003_v1_n3_01_scaffold_generate.py` の既定 strategy_l 経路でも `_log_kp_backend_telemetry(...)` を記録(1行/呼び出し、CURRENT_SPEC記述と一致させる)。全エントリに `requested_backend` / `backend_used` / `final_status` / `fallback_triggered` / `fallback_reason_code` / `synthetic`(bool) / `spec_id` / `article_id` / `level` / `model_id` / `cost_jpy` を持たせる。unit testは `mock.patch.object(sc, "KP_BACKEND_TELEMETRY_PATH", tmp)` に切替え、debug出力先もtmpへ。既存telemetry 11行(test偽エントリ・合成fallback含む)は削除せず `er030_output/kp_backend_telemetry_01/telemetry_bootstrap_evidence_2026-09-27.jsonl` へ退避し、本番集計の起点を明記。強制注入runは以後 `synthetic=true` で記録されるようevidence scriptにも反映。
- **B2 per-article traceability**: db_hybrid成功時も `{kp_dir}/keywords_runtime_metadata.json`(または `{kp_dir}/kp_backend.json`、追記型)に `kp_backend` / `kp_backend_used` / `fallback_reason_code` / `cost_jpy` / `model_id` / attempt履歴を記録(fallback時は「db_hybridを試して失敗した事実」も残す)。`run_theme_scaffold()` の `result[level]` へ `kp_backend_used` を載せ `entry_point.json` に残す。
- **B3 routing違反のfallback吸収**: `run_db_hybrid_selection` で `SelectorModelMismatchError` および契約系例外(`er006_model_routing_contract_01` 由来)を `DbHybridFailure` に包まず再raise(fail-closed維持)。`DbHybridFailure` に `fallback_allowed` フラグを持たせ、`_run_key_phrase_selection_db_hybrid_with_fallback` で不可理由はSTOP。test: mismatch注入でSTOPすること。

## SHOULD_FIX(Fable決定済み、実装する)
- **S1**: 12 fixtureで `er029 build_lightweight_user_message_v4` と `er030 build_lightweight_user_message` の**出力文字列完全一致**をassert。SSOT/REPORTの「byte-identical shortlist」表現を実測範囲(prompt文字列一致)に訂正。
- **S2**: 等価性testのWiktionary lookup 2関数を固定辞書fakeに差し替え決定化(実APIを叩かない)。
- **S3**: PASS直後に選定itemの `source_span`/`source_sentence` を `er003_key_phrase_source_gate_01.normalize_text` 基準で生 `article_text` に照合、不一致は `DbHybridFailure("SOURCE_SPAN_NOT_IN_RAW_ARTICLE")`(fallback可)。
- **S4 cost guard(Fable決定)**: 定数名・docを「per-call runaway検知」に改める。**PASS済み結果は破棄せず採用**し、telemetry/metadataに `cost_guard_exceeded=true` を残す(より高価な全文方式へ再課金しない)。加えて `run_key_phrases` スコープで `article_id` 単位の累積JPY(db_hybrid+fallback+retry)を持ち、累積閾値(既定 ¥15、定数化)超過は fallbackではなく **STOP**(`KP_ARTICLE_COST_CAP_EXCEEDED`)。既存の「cost guard→fallback」条件はこの意味論に置き換える(CURRENT_SPECのfallback条件記述も更新)。
- **S5 shortlist条件(Fable決定)**: `MIN_SHORTLIST_COUNT` を総数のみから「total>=12 かつ phrase_included+important_noun_included>=5」へ(Trial-04実測20〜24から導出、REPORTに根拠表)。
- **S6(a)**: `SELECTION_GUIDANCE` と util 4関数(`extract_static_instructions`/`extract_article_title`/`assert_no_full_article_body`/`_compact_evidence_string`)および er030 core が er023/er027/er028 から使う関数群を **er030側へ移設**(Trial版とのbyte一致test/sha256 guard testを追加。Trial module側は無変更)。Production moduleからTrial run scriptへのimportをゼロにする。
- **S7**: REPORT/DECISION_LOG/CURRENT_SPECの内訳(成功6・fallback 3、¥9.2517)・表現・docstringの参照test名を実測に訂正。
- **S8**: `run_key_phrases` スコープでshortlistをキャッシュ(article_text hash)、Redundancy QA retryはprompt再生成のみ。
- **N5**: OPEN_ITEMSへ「KP工程cost計測欠落(canonicalization/Redundancy QA/Strategy L選定、全Family共通の既存限界)」を新規OPEN(PM追跡)。**N2**: 「Family X KPをstrategy_lで再実行しうる別入口(ad-hoc retry script群・er017 Trial line)」をOPEN-202へ追記(B1のtelemetry化で検知可能になる旨)。**N7**: `db_hybrid_stage1_debug.json` は監査証跡として追跡対象のまま(REPORTに明記)。N6: fixtureの `skipTest` 退避を、対象article.md不在時に**FAIL**へ変更(無自覚なカバレッジ喪失防止)。

## 検証
新規/更新test全PASS(¥0)、`run_project_regression.py`(既知失敗以外なし、commit後に自己診断PASSを確認)。runtime evidenceは再取得しない(既存4記事evidenceは有効。B2のmetadataはevidence出力にも後付けで生成できるなら生成し、できなければ「次回run以降」と明記)。

## REPORT/SSOT
REPORT §8「修正1回目」: Opus所見との照合表(B1〜B3/S1〜S8/N1〜N10: 対応/決定/OPEN/対象外+理由)、diff要約、test、Gate 3表更新(Opus L2=実施済み・BLOCKER解消)。SSOT(CURRENT_SPEC Key Phrase節: fallback条件・cost意味論・shortlist条件・telemetry項目・per-article metadata; DECISION_LOG: 修正1回目エントリ[Fable決定S4/S5/S6を明記]; OPEN_ITEMS: N5新規・OPEN-202追記; REPORT_LEDGER Opus発火列)。SSOT編集直前に `git status` で他Agentの未commit差分(SSOT 3点)を確認、あれば最大10分待ち。

Git: 変更コード・test・fixture・退避telemetry・REPORT・SSOT 4点・delegation_logのみpath指定add(`git add -A`禁止、他Agent[er032_*, er019_output runtime, er003_v1_sing01_*, er025_*]のstageを外さない、index.lockリトライ)。トレーラー `Management-ID: KEY-PHRASE-DB-HYBRID-FAMILY-X-PRODUCTION-WIRING-01`。push origin main。reset/amend/rebase/force push禁止。RESULT_PACKETにcommit hash・変更ファイル・test件数・照合表要約・Gate 3残項目を記載。
