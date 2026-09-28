# 2026-09-28 PM-CHECK-LUNA-TEST-AND-TRANSCRIPTS-01 委任文(保存)

read-only確認タスク(¥0、API呼び出しなし、コード/SSOT編集なし)。一時ファイル
`docs/pm/ACTIVE_TASK_CHK1.md` / `docs/pm/RESULT_PACKET_CHK1.md`(commitしない)。
他Agentが多数並行中(`er003_key_words_*`/`er030_*`/`er035_*`/SSOT/
`er033_output`/`er019_output` 等)→ 何も編集しない。

E-1: 同一task内で同一ファイルを再読しない。D-1: Grep→該当行範囲Read。
G-1: git出力は`--porcelain`/`--short`で最小化。F-1: 下記(2)の退避コマンドを
実行する。T-0: 本委任文を `docs/pm/delegation_log/2026-09-28_PM-CHECK-LUNA-
TEST-AND-TRANSCRIPTS-01.md` へ保存(commitは(2)のtranscript退避と一緒に
行う)。

(1) **regression failure原因確認**: 別Agent報告で「`er006_pool_benches_
luna_audio_wiring_test.py` が、commit `ccd7070e`(TTS-GEMINI-3.8-FLASH-
LITE-PRODUCTION-WIRING-FAMILY-X-02)による `er003_v1_sing01_news_tail_
fix.py` のimport文字列変更のため失敗」との指摘があった。一方その-02
Agentは「本Phase起因の新規regression 0件(failed=7/errors=2=既知
baseline)」と報告している。確認: `.venv\Scripts\python.exe -m pytest
er006_pool_benches_luna_audio_wiring_test.py -q` を実行し、失敗の有無・
assertion内容・原因箇所(`er003_v1_sing01_news_tail_fix.py` の該当行、
`git show ccd7070e --stat` / `git show ccd7070e -- er003_v1_sing01_news_
tail_fix.py`)を特定。このtestが「既知baseline failed=7」に含まれて
いたかを `KEY-PHRASE-DB-HYBRID-SOURCE-REFERENCE-CONTRACT-PRODUCTION-
WIRING-01_REPORT.md` §11 と `TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-
WIRING-FAMILY-X-02_REPORT.md` のregression節(Grep `failed=7`)の内訳で
照合。判定を「A: ccd7070e由来の新規regression(-02の報告漏れ)」
「B: 既知baseline」「C: 他Agentの未commit差分由来」のいずれかで報告し、
Aなら最小修正案(実装はしない: test側の期待文字列更新かProduction側か、
どちらが正か根拠付き)を書く。

(2) **transcript退避**(PM_GOVERNANCE 11節 F-1恒久手順): `.venv\Scripts\
python.exe docs/pm/tools/collect_subagent_transcripts.py --apply
--only-task-ids a589d532f89a2221e,a77531f3d1092b751,ab9e7e49e1d9f1a20,
a267c7dd138893ad4,a299e508cdaa64078,a20f4934c607fd80b,a46f7d5c8c08c9179`
を実行(既定の `--max-total-mb` 20MB、上書き・削除なし)。結果(コピー
件数・0バイト代替保存の有無・保存先)を記録。退避先が `docs/pm/
transcripts/` でgit管理対象なら、追加された退避ファイルとdelegation_log
のみをpath指定addし、コミットメッセージ `PM: subagent transcript退避
(7 task)+luna test確認記録`、trailer `Management-ID: PM-CHECK-LUNA-TEST-
AND-TRANSCRIPTS-01` でcommit、`git push origin main`。他Agentの差分
(SSOT、er0*.py等)は一切add/commitしない。`git add -A`禁止、履歴書き換え
禁止。退避先がgit管理外ならcommit不要。

RESULT_PACKETに: (1)の判定と根拠、(2)の実行結果、commit hash(あれば)。

---

## 実施結果メモ

### (1) 判定: B(既知baseline、ccd7070e由来ではない)

- 実行(pytest未導入のため直接実行): `.venv/Scripts/python.exe
  er006_pool_benches_luna_audio_wiring_test.py` → FAIL 1件
  (`er003_v1_sing01_news_tail_fix.py: audio_validationがimportされて
  いない`)。他4ファイル・他チェックは全OK。
- `git show ccd7070e -- er003_v1_sing01_news_tail_fix.py` の全diffを
  確認: `semantic_equivalence_info` フィールド追加のみで、import文への
  変更は一切ない(claim「import文字列変更」は事実誤認)。
- `git log --follow -p -- er003_v1_sing01_news_tail_fix.py` で
  `import er006_preprod_hardening_01_validation as audio_validation`
  の追加/削除箇所を追跡: 追加は`470eb790`(ER-006-POOL-BENCHES-LUNA-
  AUDIO-VALIDATION-01時)、削除は`2b40165d`(ER-008-ASR-VARIANT-
  HARDENING-AND-RETRY-15、ccd7070eよりはるか以前の過去コミット)。
  以降ccd7070eまで再追加なし。したがって本FAILはccd7070e以前から
  ずっと存在していた。
- `KEY-PHRASE-...01_REPORT.md`/`TTS-...FAMILY-X-02_REPORT.md`の
  `failed=7 errors=2`内訳(`er003_test_p2j_investigate`3+1、
  `er011_open112_...`3、`er015_standard_a2_...`1、
  `test_family_a_files_have_no_working_tree_diff`1)いずれにも
  `er006_pool_benches_luna_audio_wiring_test.py`は含まれない。理由:
  両報告が既に指摘済みの構造的gapと一致——
  `run_project_regression.py`の探索pattern`er0*_test_*.py`は
  ファイル名が`..._test_XXX.py`形式を要求するが、当該ファイル名は
  `..._wiring_test.py`(末尾`_test.py`で終わり後続語なし)のため
  収集対象に一度もならない。加えて本ファイルはpytest形式の
  `test_*`関数を持たない単発script(`run()`)であり、`python
  <file>.py`で手動実行しないと検知されない。
  → 「失敗が既存の`failed=7`カウントに載っていない」のは-02
  Agentの報告漏れではなく、そもそも両Agentの回帰実行がこの
  ファイルへ到達し得ない既知のカバレッジ欠落(両報告が
  OPEN_ITEMS化を提案済み)が原因。
- 結論: A(ccd7070e由来の新規regression)ではない。「known baseline」
  という語の厳密な意味では`failed=7`表には載っていないが、実質的には
  ccd7070e/-02 Phase より遥かに古い(2b40165d由来の)pre-existing
  failureであり、-02 Agentの「本Phase起因の新規regressionは0件」との
  報告は正しい。
- 最小修正案(実装はしていない、提案のみ): 修正すべきはtest側。この
  testファイル自身のコメント(37-43行目)が「evaluate_attempt()の
  直接呼び出しはER-006-AUDIO-RETRY-CASCADE-PROD-01以降
  `secondary_asr.evaluate_attempt_with_cascade()`へ置換され、
  どちらの呼び出し形でも配線済みとみなす」という設計変更を
  第2ループ(37-52行目)には反映済みだが、第1ループ(import存在
  chk、28-35行目)には未反映のまま。Production側
  (`er003_v1_sing01_news_tail_fix.py`)は`secondary_asr`経由で
  正しく`evaluate_attempt_with_cascade`を呼んでおり(第2/3
  チェックはOK)機能上の問題は無い。修正はtestの第1ループを
  「直接import」または「secondary_asr importで代替可」という
  同型の緩和ロジックへ更新することが妥当(Production側の変更は
  不要)。Production安全性の観点から、本タスクでは提案のみに留め
  実装はしていない。

### (2) transcript退避 実行結果

- 対象タスクの`tasks/*.output`は全て現session
  (`f1538907-8efe-486d-9790-ef5c6cd789fa`)配下で確認(0バイト7件)。
- 実行コマンド:
  `.venv/Scripts/python.exe docs/pm/tools/collect_subagent_transcripts.py
  --tasks-dir "...\f1538907-8efe-486d-9790-ef5c6cd789fa\tasks"
  --subagents-dir "...\f1538907-8efe-486d-9790-ef5c6cd789fa\subagents"
  --transcripts-dir "docs\pm\transcripts"
  --only-task-ids a589d532f89a2221e,a77531f3d1092b751,ab9e7e49e1d9f1a20,
  a267c7dd138893ad4,a299e508cdaa64078,a20f4934c607fd80b,a46f7d5c8c08c9179
  --apply`
- 結果: zero-byte tasks/*.output 7件、subagents/*.jsonlから全7件回収
  成功、合計18.13MB(上限20MB以内)、0バイト代替保存なし、skip 0件。
  保存先: `docs/pm/transcripts/{a589d532f89a2221e,a77531f3d1092b751,
  ab9e7e49e1d9f1a20,a267c7dd138893ad4,a299e508cdaa64078,
  a20f4934c607fd80b,a46f7d5c8c08c9179}_recovered.jsonl`
