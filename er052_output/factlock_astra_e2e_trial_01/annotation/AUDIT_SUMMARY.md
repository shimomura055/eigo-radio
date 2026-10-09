# AUDIT_SUMMARY(FACTLOCK-ASTRA-E2E-TRIAL-01 委任_09、2026-10-09)
## 手順と特定
- 指定の `...\tasks\*.output` は本日分が全て0バイト(実体なし)だったため、同一セッションの実体 `C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\f2c17cf7-6207-4666-abec-016808eac6d3\subagents\agent-<id>.jsonl` を使用(.outputはこの実体への参照名)。
- 特定方法: 本日(2026-10-09)作成のjsonlのうち、先頭ユーザー発話が `あなたは注記者<A|B>です` で始まり、本文に `\annotation\prompts\<slug>__<A|B>.md` を含むもの。20/20を一意に特定(重複0、未特定0)。コピーを `annotation/out/<A|B>/<slug>/transcript.jsonl` に保存。
- 実行: `annotation/audit_strict_01.py`・`b3_annotator_audit_01.py`(既存、無改変)+補助 `annotation/audit_extra_01.py`・`audit_bash_detail_01.py`(新規)。runner `annotation/run_audits_01.py`。結果 `annotation/audit/<slug>__<A|B>.{strict,base,extra}.json`、`audit_all.json`、`bash_detail.json`。
## 結果
1. 既存2スクリプトは20/20が VIOLATION。ただし原因は、(a) 注記者へ渡された固定文言が「自分のreply.mdへWriteのみ許可」の例外付きで、既存スクリプトはWriteと環境付与の返却ツール(SubagentHandback)も違反扱いにする、(b) `b3_annotator_audit_01.py` の参照禁止語に `factlock_astra_e2e_trial_01` があり、自分のプロンプトのパス自体(区切りが`\`のためallow-substringの`/`形式に一致しない)と自分のreply.mdが禁止語に当たる、という既存スクリプトと運用文言のずれ。禁止された内容ファイル(他テーマ・他版・仕様・評価・過去の注記)へのRead/Grep/Glob/Web/MCPは**0件**。
2. 補助監査(許可=自分のプロンプトのRead + 自分のreply.mdへのWrite + 返却ツール): 
   - 全20本で Read は自分のプロンプト1件のみ(再読込0、他ファイルRead 0)。
   - 11本は Write(自分のreply.md)のみ: PASS_ONLY_ALLOWED(byd A / cbm A / hormuz A,B / inbound A / meta A / semiconductor A,B / small_bag B / streaming A,B)。
   - 9本は Write でなく **Bash** を使用(固定文言は「Grep/Glob/Bash...を使わない」例外外): byd B / cbm B / inbound B / meta B / openai A,B / small_bag A / space A,B。コマンド骨格は `mkdir -p <自分のout先> && cat > <自分のreply.md> <<'EOF' ... EOF`(+一部 `echo ok`)のみで、reply.md以外のパスへの接触は0。openai A は Bash と Write の両方で同一内容を書込み。判定: DISALLOWED_TOOL_USE(ツール規律違反。内容面の隔離違反ではない)。
   - 20本とも SubagentHandback の本文は保存済み reply.md と一致(meta A のみ末尾に保存先注記1行の差)。注記抽出は注記者が書込んだ reply.md を使用(呼出側の書込みではない)。
3. 結論: 隔離(他ファイル非参照)は20/20で維持。ツール規律は9/20で逸脱(Bash経由のreply.md書込み、実質は許可Writeと同じ効果)。これらの注記を採用するかはFable判断。採用した統合6テーマの内訳: byd(B=Bash)、cbm(B=Bash)、meta(B=Bash)、openai(A,B=Bash)、small_bag(A=Bash)、space(A,B=Bash)。
