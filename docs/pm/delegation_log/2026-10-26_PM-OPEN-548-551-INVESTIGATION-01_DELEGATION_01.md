## 管理ID

PM-OPEN-548-551-INVESTIGATION-01 委任_01(read-only調査2件: OPEN-548 猿の手 seed provenance不一致の原因・意図照合・是正案、OPEN-551 Z側Style実測照合の網羅確認。API 0・JPY0。コード/SSOT/run dir/seed編集なし)。並行Agent: TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_03(X/Y/Z `run_tru_ev_*`で実TTS evidence。Z run dirへ書込禁止)、他なし。所有=`docs/research/PM-OPEN-548-551-INVESTIGATION-01/{OPEN548_PROVENANCE_01,OPEN551_Z_STYLE_CHECK_01}.md`、`docs/pm/delegation_log/2026-10-26_PM-OPEN-548-551-INVESTIGATION-01_DELEGATION_01.md`(+check.json)、`docs/pm/RESULT_PACKET_INV1.md`。SSOT編集権なし。pathspec付きcommit。

## 性質/禁止

- 性質: 調査(分類確定の材料)。到達上限=INVESTIGATED(是正案付き)。
- 禁止: seed/provenanceの書き換え、本文再生成、有料API、禁止Git操作。
- 時間見込み: 約1h。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1/D-1/G-1/F-1: 従来どおり。T-0: 委任文保存+`check_delegation_prompt.py`、結果をRESULT_PACKETへ1行(FAILでも継続)。T-2: TTSなし。T-3: 費用なし。
T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-26_PM-OPEN-548-551-INVESTIGATION-01_DELEGATION_01.md` をN=692から順に試し、先頭「## 管理ID」+「PM-OPEN-548-551-INVESTIGATION-01」のものを採用。

## 事前指定Read一覧

- OPEN-548: `er026_output/family_z_production_e2e_01/the_monkeys_paw/seed/`(`seed.json`・`seed_STALE_20261025.json`、sha・mtime・差分)、`git log --oneline -- <seed path>`(追跡されていれば)、`docs/pm/delegation_log/2026-10-25_*monkeys*|*MONKEYS*|*FZ*|*猿*`(Glob→10-25のseed更新を指示/記録した委任・ユーザー原文)、`OPEN_ITEMS.md` Grep `seed_STALE|seed.json|provenance` ±3、`er026_family_z_fiction_production_runner_01.py` Grep `FamilyZProvenanceMismatchStop|writer_provenance|seed_sha` ±15(照合ロジック・再pinの正規手順の有無)、`docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/evidence_runs/`の猿の手launch log(停止時の実値)、既存run(`run_sf_prod_01`等)のprovenance記録。
- OPEN-551: `er063_family_z_audio_01.py:266-312`(Z Style profile照合)、Grep `style_profile|resolve_run_profile|_final_style_record|checked` ±10、`er019_family_x_style_profile_01.py:685-760`(共通helper、読み取り)、Z最新Production run(`er026_output/.../melos/`等)の`audit/style_profile.json`と`style_actual_vs_approved`相当の有無、`docs/research/FAMILY-Y-STYLE-PROFILE-FIX-01/PREVENTION_01.md`(Yで導入した照合表・Y_ROLE_COVERAGE完全一致の考え方)。

## 事前指定Grep一覧+追記位置・更新位置の手順

- 成果物は新規dirに作成。

## 実施事項

1. **OPEN-548**: (a)事実=seed.jsonの現行sha/旧sha、更新日時、更新を行った委任ID・ユーザー指示(逐語引用)、更新内容の差分(本文に影響するフィールドか、メタのみか)。(b)既存run(公開済み本文・KP・音声)のprovenanceが指す旧seedとの関係=公開物は旧seedで生成された事実。(c)新規KP生成(Z runner)が停止する条件と、正規の解消手段(runnerに再pin手順があるか、新runは新seedで本文から再生成が必要か)。(d)是正案: 案1=新runを新seedで本文から再生成(有料・公開物差替え=D)、案2=旧seedを参照する再pin/provenance明示指定で既存本文を使う(API 0ならB)、案3=猿の手は新規KP生成を行わない(現状維持)。各案の費用・品質・公開物影響・推奨。
2. **OPEN-551**: Z runnerの正式経路で、承認profile(fx_20261017相当のZ適用分)と実送信prefixの照合が、全role×level×segmentで**実測値**に基づき行われているか(checked空でPASSになる経路、日本語roleの自己一致、セリフ[Dialogue]部位の扱い)。Yで導入した「期待集合との完全一致・fail-closed」と比較し、Zに不足があれば最小是正案(影響範囲・test案)。既存Z公開記事に不一致の疑いがある部位があれば列挙(推測禁止、audit記録で確認できる範囲)。

## 実行コマンド全文

- `py docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-26_PM-OPEN-548-551-INVESTIGATION-01_DELEGATION_01.md --json-out docs\pm\delegation_log\2026-10-26_PM-OPEN-548-551-INVESTIGATION-01_DELEGATION_01.md_check.json`
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## SSOT追記文

SSOT編集権なし。`RESULT_PACKET_INV1.md`にOPEN-548/551の更新文案(分類確定案・是正案・推奨)。

## Git

- add対象: `docs/research/PM-OPEN-548-551-INVESTIGATION-01/`、delegation_log。commit message: `PM-OPEN-548-551-INVESTIGATION-01: 猿の手seed provenance不一致の照合+Z Style実測照合の網羅確認(read-only、API 0)`。trailer: `Delegation: PM-OPEN-548-551-INVESTIGATION-01/01`。push `git push origin HEAD:main`。

## 報告

`docs/pm/RESULT_PACKET_INV1.md`: (0)T-0、(1)OPEN-548事実・是正案・推奨、(2)OPEN-551結果・不足・是正案、(3)判断候補(ユーザー判断が必要なもののみ)、(4)必須4行+「判定整合: 重大NG=<なし|あり>」、(5)一覧外Read、commit hash、raw URL。末尾5行要約。