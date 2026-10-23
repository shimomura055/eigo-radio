MARKER: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_24 (2026-10-24, Fable→sonnet-worker)

# 管理ID: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_24(課題②配線のFable受入前確認: A-1に対するOpus条件C必須修正W-01〜04の本文復元と実装照合、静止状態での全回帰再確認。API 0)

## 背景
- 委任_20(commit 4128fffeb、SSOT 5963d6597/be09ae82d)で②+A-1をX/Z正式経路へ配線。報告 `docs/pm/RESULT_PACKET_KPGM20.md`、証跡 `docs/research/FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01/PROD_WIRING_EVIDENCE_07.md`。
- 開示事項: A-1(参照語の不定化)に対するOpus条件C必須修正 **W-01〜W-04 の本文がrepo内に無く**、W-02のみ反映確認済み。W-01/03/04は未照合。また全回帰で自分起因でない失敗6件(他agentの並行作業起因)があり、静止状態での再確認が未了。

## 作業
 A. **W-01〜04の本文復元**: セッション記録 `C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl` から、A-1配線設計(WIRING_DESIGN_01)に対するOpus条件Cレビューの本文(「W-01」「W-02」「W-03」「W-04」を含むopus-consultantの回答。2026-10-23)を抽出する(`py` + json行読み。`docs/pm/tools/extract_delegation_from_jsonl_01.py` はassistantのtool-input抽出用なので、必要なら同ツールを参考に tool_result/assistant text を検索する小scriptをscratchに書く。読み込みは `W-01` を含む行の該当フィールドのみ出力し、jsonl全文を表示しない)。見つかった本文を `docs/research/FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01/OPUS_REVIEW_A1_CONDC_01.md` に逐語保存(出典=jsonlのtimestamp/uuidを冒頭に記す)。見つからない場合は、その事実と検索条件を記録しFableへ(推測で本文を作らない)。
 B. **照合**: W-01/W-03/W-04それぞれについて、実装(4128fffeb: `er105_kp_fulltext_selector_01.py`/`er003_key_words_canonicalization.py`/`er003_v1_n3_01_scaffold_generate.py`/`er003_key_words_gloss_alignment.py`/template)が満たしているかを関数・行で照合し、`PROD_WIRING_EVIDENCE_08.md` に表(W-0n / 要求 / 実装箇所 / 充足○△× / 未充足なら必要な差分)。未充足があれば**実装せずFableへ報告**(修正は次委任)。
 C. **静止状態の全回帰**: 他agentの有料run・Production編集が進行中でないことを `docs/pm/ACTIVE_TASK.md` の各行(有料run進行中flag)と `git status` で確認し、進行中なら最大20分待つ(待機中にA/Bを進める)。`.venv\Scripts\python.exe run_project_regression.py` を実行し、失敗を1件ずつ「自分/委任_20起因か・他agentの一時状態か・既知3件か」に分類。er064のtracked変更検出は、未commitの他agent変更(er021等)が原因なら対象ファイルと担当管理IDを記録。
 D. 記録: `PROD_WIRING_EVIDENCE_08.md`、OPEN-474へ1行(Fable受入前確認の結果)。ACTIVE_TASK自分の行。委任文逐語保存 `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl <同上jsonl> --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-24_FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01_委任_24.md`(先頭MARKER一致、0始まり)。commit(`git status`でindexに他agentのstage済みファイルが無いことを確認→`git commit --only -- <paths>`、`git add -A/-u/-f`禁止、secret grep 0件)→`git push origin HEAD:main`。
 E. 報告 `docs/pm/RESULT_PACKET_KPGM24.md`: W-01〜04の復元可否と照合表、静止回帰結果(failed件数と分類)、PRODUCTION_WIRED受入可否についての事実(判定はFable)、4行、判定整合行。