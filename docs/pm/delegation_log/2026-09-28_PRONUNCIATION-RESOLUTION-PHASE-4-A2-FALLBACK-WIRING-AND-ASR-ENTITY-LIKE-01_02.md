# 委任文全文(PRONUNCIATION-RESOLUTION-PHASE-4-A2-FALLBACK-WIRING-AND-ASR-ENTITY-LIKE-01、02)

管理ID: PRONUNCIATION-RESOLUTION-PHASE-4-A2-FALLBACK-WIRING-AND-ASR-ENTITY-LIKE-01(Sonnet修正1回目=ユーザー判断 2026-09-28 反映。**¥0、API呼び出しなし、Lock解除なし、small_bag再実行なし**)。一時ファイル `docs/pm/ACTIVE_TASK_PRN9.md` / `docs/pm/RESULT_PACKET_PRN9.md`(commitしない)。委任文全文を `docs/pm/delegation_log/2026-09-28_PRONUNCIATION-RESOLUTION-PHASE-4-A2-FALLBACK-WIRING-AND-ASR-ENTITY-LIKE-01_02.md` に保存しcommitに含める。

## ユーザー判断(逐語要旨、厳守)
1. **A-1 Ledger登録surface条件はOFF**: 現時点のProduction仕様は `entity_tokens = 大文字始まり ∪ 非ASCII外来語` まで。`ledger_registered_entity_flags` の寄与を無効化(実装は残してもよいが**既定OFFの明示フラグ**とし、Productionから到達しないことをtestで固定。Ledger自体は読み解決/Resolverで引き続き使用)。Status: Ledger surface条件 = **DEFERRED / NOT_ADOPTED**(将来S1/量産telemetryで「必要」かつ「安全な追加条件でfalse accept非増加」の証拠が出たら再検討)。
2. **A-2はそのまま**(Opus BLOCKERなし、全経路同一hook確認済み)。
3. **S1(¥0)**: 既存 `er021_output/en_asr_semantic_equivalence_production_wiring_01/telemetry.jsonl` 等の全NG記録(canonical/ASR保持分)をread-onlyでオフライン再判定し、**Ledger条件OFFの前提で** 母数 / entity_like反転件数(TRUE_CONTENT_MISMATCH→UNCERTAIN) / そのうち `_case_a_entity_pass` でPASS化しうる件数 / 一般語誤りが隠れる件数 を集計(スクリプト `er025_phase4_s1_offline_reclassification_01.py` 新設、出力 `er025_output/phase4_s1_offline_01/`)。telemetryファイルは**読み取りのみ・改変禁止**。
4. **S3(¥0)**: `content_word_diffs[*].entity_like_source`(capitalized/loanword の集合)を付与し、`er021` telemetry record・cascade steps・human_review_queue へ透過(additiveキーのみ)。あわせて `pronun_ledger._load()` の毎回disk読込は、Ledger条件OFFにより分類経路から外れることを確認(残る場合はmtimeキャッシュ検討、実装は最小)。
5. **N1**: entity_like拡張がcascade起動条件と既存自動PASS機構(`_case_a_entity_pass`、ARPAbet完全一致条件)の入力域も広げる事実を CURRENT_SPEC / REPORT / DECISION_LOG に明記。N2: evidence記述の是正(Lock回避でattempt音声保存・segment_id role gateも無効化されていた点)。N3: `ALLOW_PRONUNCIATION_WEB_LOOKUP` 既定"1"でfallbackが初回lookup発火点になりうる点を記録。
6. **再実行候補の提示資料**(実行しない): small_bag A2 `full_story_part2`/`full_story_part3`、B1B `full_story_part2` について、segmentごとの期待救済内容、Altuzarra(Ledger登録・Phrase List有)/Khaite(cascade_unresolved、Phrase List有・TTS注入なし)/minaudière(未登録、loanword条件で再分類のみ)ごとの見込み、見積(attempt 2/segment想定、上限)、**実効guard**(`PRODUCTION_MAX_TTS_ATTEMPTS=3`×3、cascade `COST_GUARD_MAX_USD_PER_SEGMENT`)と¥見積の区別、Human Reviewが残る可能性、をREPORT §9に表で。small_bag B1B KP再選定(DB Hybrid 1 call、KP X配線はPRODUCTION_WIRED済み commit 8c2da18e)も候補として併記。
7. test更新(Ledger条件OFF固定、provenance、S1スクリプトのunit)、関連test+`run_project_regression.py`(既知baseline以外なし)。
8. REPORT §8「修正1回目」: Opus所見照合表(BLOCKER 0/S1〜S3/N1〜N7: 対応/決定/OPEN)、Gate 3チェックリスト最終表(Opus L2=実施済み、PRODUCTION_WIRED=Fable判定待ち)。SSOT: CURRENT_SPEC(Phase 4仕様=大文字始まり+非ASCII外来語、Ledger条件 DEFERRED/NOT_ADOPTED、N1明記)、DECISION_LOG(ユーザー判断エントリ)、OPEN_ITEMS(Ledger条件再検討を新規OPEN[PM追跡]、OPEN-207関連追記)、REPORT_LEDGER。**SSOT編集直前に `git status` で他Agent(KP contract配線: er030_*, er003_v1_n3_01_scaffold_generate.py, SSOT)の未commit差分を確認、SSOT 3点に差分があれば最大10分待ち、解消しなければ記載案をRESULT_PACKETへ。**

Git: 変更コード・test・S1出力・REPORT・SSOT 4点・delegation_logのみpath指定add(`git add -A`禁止、他Agentのstageを外さない、index.lockリトライ)。トレーラー `Management-ID: PRONUNCIATION-RESOLUTION-PHASE-4-A2-FALLBACK-WIRING-AND-ASR-ENTITY-LIKE-01`。push origin main。reset/amend/rebase/force push禁止。RESULT_PACKETにcommit hash・変更ファイル・S1集計結果・Gate 3最終表・再実行候補表を記載。

## 実施結果に関する補足(Sonnet記録、2026-09-28)

- `OPEN_ITEMS.md`は、着手前確認時点で`OPEN-202`行に別Agent
  (`KEY-PHRASE-DB-HYBRID-SOURCE-REFERENCE-CONTRACT-*`系)の未commit差分
  が存在し、待機後も解消しなかったため、本ラウンドでは編集していない
  (記載案をRESULT_PACKETへ記録)。
- `er003_v1_n3_01_scaffold_generate.py`も同様に別Agentの未commit差分が
  存在し、本タスクでは一切編集していない(`run_project_regression.py`
  の新規1件失敗の原因、詳細REPORT §8-4)。
