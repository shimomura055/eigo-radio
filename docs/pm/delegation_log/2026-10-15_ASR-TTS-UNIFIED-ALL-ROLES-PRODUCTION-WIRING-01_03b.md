# 委任_03b: AUW(ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01)— 委任_03の未commit変更に対する既存test 30件の分類・追随とcommit/push

場所: C:\Users\tensh\eigo-radio、branch feat/auw-unified-asr-01(委任_03の変更が未commit)。review_queue/post_en/index.jsonl等の無関係な変更はaddしない。禁止: git add -A/-f/stash/reset --hard/checkout -f/clean/rebase/amend/force push、mainへのpush/merge。有料API 0。

## T-0
本委任文を保存、check_delegation_prompt.py -> _check.json(FAILでも継続)。stop_scope_check rc=0。

## 事前指定参照
- er058_output/unified_all_roles_production_wiring_01/IMPLEMENTATION_03.md(§7), patch_03/test_full_baseline.json・test_full_post.json, DESIGN_01.md §4-3/§4-9, DESIGN_02_ADDENDUM_01.md §4・§7
- ユーザー原文: docs/pm/delegation_log/2026-10-15_ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01_01.md(基本フロー「TTS->Primary ASR->NGならSecondary->両NGで再生成->3回NGでLR/HR」「Primary NG->原則Secondary」「重複呼出防止」「Connected Speech/M1/F1再利用」「Regression基準: Melos said. 12/12・12/12・M1 21観測・誤受理0」「既存QA・HR Lock・予算維持」)
- 失敗30件: er006_secondary_asr_01_test 11 / er006_secondary_asr_01_m1_wiring_test 6 / er011 f1 6 / er011 CS wiring 3 / er021 Tier3 2 / er026 primary2_single_pass 1

## やること
1. 30件を1件ずつ分類(test名/失敗assert/旧挙動の前提/新設計の根拠のファイル:行/区分)。区分は
 - (alpha)撤去済み挙動の固定: 期待値を新設計に更新。コメント `# AUW 委任_03b: DESIGN_01 §4-9 / ユーザー原文「Primary NG→原則Secondary」に追随(旧: ...)`。安全側の意図(Secondary障害をPASS扱いしない、誤受理0、HR Lock維持)は新設計の対応assertに置換して残す。
 - (beta)承認済み等価・救済の最終判定を検証するもの(F1/CS/M1/Tier3): 期待値変更禁止。失敗が残れば実装側退行を疑い原因特定して実装を直す。直せない/設計判断要はSTOP報告(commitしない)。
 - (gamma)未commit-diff guard(er019 FamilyAUnchanged/er020x2/er064): commit後解消を確認。
 er011 f1 6件・CS wiring 3件・er021 Tier3 2件は(beta)の可能性を最初に疑い、assertが呼出回数/経路か最終判定かをコードで示す。
2. 更新後、er006*/er007*/er011*/er019*/er020*/er021*/er026*/er064*/er078* testをファイル単位で実行、baselineに対し新規失敗0を数値で示す(passed/failed合計、集計scriptのsummary解析問題を直す)。ledger.json依存の揺れは原因と再現条件を記録(安定化はしない)。
3. IMPLEMENTATION_03.md に §8「既存test追随(委任_03b)」を追記。
4. commit/push: 委任_03の17ファイル+新規test+更新test+IMPLEMENTATION_03.md+evidence_03_pages+patch_03+delegation_log(03/03b)を明示指定でadd -> secret_scan --staged hits=0 -> commit -> git push origin feat/auw-unified-asr-01。beta未解決ならcommitせずSTOP報告。
5. docs/pm/RESULT_PACKET_AUW3b.md に詳細。

## 報告様式(受入記録5項目)
(1)当初目的(ユーザー原文逐語・ファイル:行) (2)実際の成果物 (3)証拠(分類表・test数値・commit hash) (4)一致/不一致(alpha/beta/gamma件数、新規失敗0か、beta変更0か) (5)判定。加えて逸脱・委任_04への注意点・費用。
