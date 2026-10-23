FABLE-DELEGATION-MARKER: ASR-QUALITY-2ITEMS-COMPREHENSIVE-01-委任_07-OPEN-479-XZ-SCOPED-FIX-AND-OPEN-WINDOW-COMPLETION-20261023

# ASR-QUALITY-2ITEMS-COMPREHENSIVE-01 委任_07: OPEN-479をX/Z run scope限定で修正(Fable承認済み)→test→replay再実行→『開いた窓』c14 2clip再生成→正式Gate→組立→試聴ページ→page_verify→SSOT→Git。費用上限15円。

## 0. 先に読むもの
`docs/pm/PM_BRIEF.md`、`docs/pm/ACTIVE_TASK.md`(固定ヘッダ、line 2、ASR行、FAMILY-Z-SOURCE-FIDELITY行)、`.claude/agents/sonnet-worker.md`、`docs/pm/RESULT_PACKET_ASRQ_B6.md`、`docs/research/ASR-QUALITY-2ITEMS-COMPREHENSIVE-01/OPEN_479_IMPACT_01.md`、`B_STAGE_RESULT_01.md`、`docs/pm/delegation_log/2026-10-23_ASR-QUALITY-2ITEMS-COMPREHENSIVE-01_委任_05.md`(制約継承)、`er103_output/ret_prod_z_evidence_01/open479_replay_01.py`、ユーザー原文 `..._USER_02.md` §1-B/§3。

## 1. Fable判断(2026-10-23)
- 委任_06の影響分析を照合した結果: (a)共有関数のためB/C(Legacy凍結 §27-3)へ波及し得る → **X/Z run scope内(`er109_xz_scope_01.is_active_for_run()`)のときだけ** `segment_id` を渡す方式を採用(B/Cは完全に従来どおり)。(b)replayでの他層変化は『開いた窓』c2のTier3警告ラベル(SECONDARY_CONFIRMED→SECONDARY_CORROBORATED、verdict不変)と監査layersへのtier3追加のみで、PASS→NG/NG→PASS 0件。`er020_tts_retry_local_rewrite_01.py:133-136`(Opus M6)でZの会話clipにも5roleを適用する意図が既に承認されているため、**この変化は承認範囲内(区分B)**と判断。代替案(PNAP専用引数)は不採用(narratorとの同等性を崩し複雑化するため)。
- よって修正をFable承認済みの仕様内不具合修正として実施してよい。Production変更はこの1箇所(+必要最小のscope判定import)に限る。

## 2. 作業
### T-0 記録・予算(API 0)
- **委任_06の委任文が「要約した再掲」で保存されている(逐語でない)ため、逐語で上書き保存し直す**: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-23_ASR-QUALITY-2ITEMS-COMPREHENSIVE-01_委任_06.md`。Nは末尾付近から逆順に試し、先頭行が `FABLE-DELEGATION-MARKER: ASR-QUALITY-2ITEMS-COMPREHENSIVE-01-委任_06-OPEN-479-DIALOGUE-SEGMENT-ID-FIX-AND-OPEN-WINDOW-COMPLETION-20261023` のものを採用。同様に本委任_07(MARKER先頭行一致)を `..._委任_07.md` へ逐語保存。要約保存は不可。
- ACTIVE_TASKのASR行を 委任_07 Status=`OPEN_479_FIX_IN_PROGRESS`、上限15円、報告=`docs/pm/RESULT_PACKET_ASRQ_B7.md` に更新(自分の行のみ)。当日累計を`daily_dev_cost_01`で確認(上限1,400円、他予約枠: Family Y 残334.25円、KP 70円)。
- secret scan: `Glob **/secret_scan*` で実体を探す(例: `docs/pm/tools/` または `tools/` 配下)。見つかったscriptで `--staged` 相当を実行。見つからなければ、staged差分を `git diff --cached` でkey/token/URL認証情報のパターン(`sk-`, `pplx-`, `api_key`, `Bearer`, `AKIA`等)でGrepし0件を記録。
### T-1 修正・test(API 0)
1. `er012_b_family_voices_production_01.py:553` 付近: X/Z run scope内のときのみ `review_lock.derive_segment_key(out_path)` 由来の `segment_id` を `evaluate_attempt_with_cascade` へ渡す(narrator経路 `er003_v1_sing01_news_tail_fix.py:205-213` と同方式)。scope外(B/C)は引数を渡さず従来どおり。
2. test追加: (a)Z scopeで会話clipのroleが解決されPNAP/RETが適用可能(ROLE_NOT_APPLICABLEにならない) (b)scope外(B/C)では従来どおり`segment_id`なしで呼ばれる(呼出引数のassert) (c)narrator経路不変 (d)replay「PNAP/RET受理とTier3ラベル以外の変化0」を固定。
3. `open479_replay_01.py` を修正後コードで再実行し、委任_06のbefore結果と比較(変化がc2のTier3ラベル/tier3 layer追加のみであることを確認、`open479_replay_after.json`)。
4. 回帰: er012/er013(B/C golden・dry-run)、er103/er109/er063/er026/er020系、`run_project_regression.py`(`er0*`,`er1*`)。B/Cのgolden hashが不変であることを明記。他agent起因の既知失敗は切り分けて列挙。
### T-2 『開いた窓』完成(TTS直列化: 他行の「有料run(TTS)進行中」を待機、最大45分。自行にflag記載/終了更新)
- 保全(`run_sf_prod_01` → `_preserve_20261023_b7/`)。c14 2clip(a2/b1b)を `approve_regenerate`(根拠=USER_02 §1-B/§3・Fable承認・本委任)で解除し、正式CLIで `--only-clips full_story_part1_c14` を tts_b1b,tts_a2 で実行(再起動1回まで)。累計TTSカウンタ(6/15)記録。clip別に受理basis(entity_table/Ledger[Perplexity自動登録Bertie confidence=low]/secondary)・judge_role・HR有無を記録 → これが①RET/②UKUS(両flag ON共存)の**会話経路Z evidence**。
- 新たなHR Lockなら止めて報告(迂回なし)。
- 正式Gate(speed v2含む)→assemble(Std/Adv全編)→試聴ページ `user_test/family_z_open_window_01/` 差替え(全体・個別・スクリプト整合、確認点3つ=c12 speciality英式/米式、c2 Bertie、c14 Bertie)→page_verify→`docs/research/FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01/PHASE4_RESULT_03.md`。
### T-3 SSOT・Git・報告
- OPEN-479(原因・影響分析・scope限定修正・test・replay・実run結果)、OPEN-472/471(Z evidence: 会話経路の結果追記。Fable最終確認待ち表記)、OPEN-465、UDR #157更新。DECISION_LOG(Fable承認の仕様内不具合修正[scope限定]と approve_regenerate)。CURRENT_SPEC(会話clipでもX/Z scope内はPNAP/RET/5role有効、1〜2行)。REPORT_LEDGER。
- Git: secret scan 0件 → `git diff --cached --name-status` → `git commit --only -- <path…>` → `git push origin HEAD:main`。wav/raw_usage_log追跡禁止。raw URL添付。
- 報告=`docs/pm/RESULT_PACKET_ASRQ_B7.md`: (A)①②Z evidence最終(narrator+会話) (B)『開いた窓』完成状況・最終試聴URL・ユーザー確認点3つ (C)費用出典付き・時間 (D)Closeout(手段/目的の区別、撤去・残置、残リスク)。使用model名・最新か。

## 3. 禁止・制約
委任_05の禁止事項を全て継承(`git add -A/-u/-f`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・一時index禁止、PIDは自分のもののみ、Gate/HR Lock/STOP迂回禁止、Ledger手動登録禁止、`TTS_EXECUTION_MODE=STANDARD`、秘密情報出力禁止)。Production変更は上記1箇所のみ(他Prompt/閾値/flag不変)。B/Cの挙動・golden不変が必須。上限15円無断超過禁止(12円到達で見込み再計算)。`.venv\Scripts\python.exe`を使用。
## 4. handback
完了/新HR Lock/B・C golden変化/予算警告/blocker のいずれかで。