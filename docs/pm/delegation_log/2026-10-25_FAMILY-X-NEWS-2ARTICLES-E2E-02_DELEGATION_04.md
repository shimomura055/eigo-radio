# 委任文(Fable→sonnet-worker)
管理ID: FAMILY-X-NEWS-2ARTICLES-E2E-02 委任_04(Closeout)
件名: Family X 記事B『英国の電車マナー』(uk_train_speaker_playback、JAタイトル『その動画、車内で勝手にプレミア上映していませんか』)Std/Adv最終版=ユーザー試聴PASS・正式承認のCloseout記録
種別: SSOT記録のみ。API 0円。コード・Prompt・音声・公開ページの変更0(現公開版=最終版、再生成禁止)。

## 0. ユーザー原文(2026-10-25、逐語)
ユーザー指示文書「Claude Code指示｜Family X 段落単位TTS Chunk分割Trial」の§1が本委任の根拠。該当部分の逐語:

> ## 1. 最初に伝える承認事項
> **Family X『英国の電車マナー』Standard／Advancedの最終版は、ユーザー試聴PASS・正式承認済みです。**
> 対象：https://shimomura055.github.io/eigo-radio/user_test/uk_train_speaker_playback_e2e_02/index.html
> 記事の完成承認として、必要なSSOT・DECISION_LOG・OPEN_ITEMSのCloseoutを行ってください。
> 今回の新Trialとは独立した判断です。完成版を変更・再生成しないでください。

(同文書の§2以降は別管理ID FX-PARAGRAPH-CHUNK-TTS-TRIAL-01で並行進行中。本委任では扱わない。原文全文の逐語保存は並行agentが `docs/pm/delegation_log/2026-10-25_FX-PARAGRAPH-CHUNK-TTS-TRIAL-01_USER.md` に行う。本委任では上記§1逐語を `docs/pm/delegation_log/2026-10-25_FAMILY-X-NEWS-2ARTICLES-E2E-02_USER_03.md` として保存し、冒頭に「全文は上記TRIAL-01_USER.mdを参照」と注記する。)

## 1. 現状(Fable確認済み、鵜呑みにせず該当行を再Readすること)
- `OPEN_ITEMS.md:982` OPEN-467: 記事A=CLOSED_USER_PASS(2026-10-23)、記事B=USER_LISTENING_PENDING(2026-10-24 委任_35で最終版再提出、Std 307.05秒/Adv 280.84秒、page_verify 47/47 PASS)。
- `docs/pm/USER_DECISION_REGISTER_01.md:359` UDR #166: 記事A判断済み、記事B=最終承認保留→USER_LISTENING_PENDING。
- 先例(同形式で実施): 『英単語ガチャ』Closeout `docs/research/FAMILY-X-WORD-GACHA-PRODUCTION-01/CLOSEOUT_01.md`(commit 57be408ad)。記事Aの記録形式は OPEN-467行内の【2026-10-23 委任_03 ユーザー判断記録】。
- 成果物: run `er019_output/family_x_audio_production_wiring_01/uk_train_speaker_playback__run_nws_02/{a2,b1b}/assembled/`、公開ページ `user_test/uk_train_speaker_playback_e2e_02/index.html`。

## 2. 作業
1. 原文§1逐語保存(上記path)。
2. `docs/research/FAMILY-X-NEWS-2ARTICLES-E2E-02/CLOSEOUT_02.md`(記事B)を作成: 承認日2026-10-25、承認原文引用、最終版の識別(run id、Std/Adv秒数、最終commit[705b9316b 記事B再提出/78c5b4c1f SSOT]、公開URL)、費用(記事B 87.87円+委任_35再提出分=PROD_WIRING_EVIDENCE_10.md/QUALITY_CHECK_35.mdに記録された実費を引用、出典のない数字は書かない)、残Open(なければ「なし」。OPEN-474/501/502等は本記事の完成条件ではないので「独立継続」と明記)。既存`CLOSEOUT_01.md`があれば記事Aのもの=上書き禁止。
3. SSOT最小編集(編集直前に該当行を再Read、最小Edit、並行agentと衝突したら再Read→再Edit):
   - `OPEN_ITEMS.md` OPEN-467行: 先頭太字Statusを `[記事A=CLOSED_USER_PASS(2026-10-23) / 記事B=CLOSED_USER_PASS(2026-10-25)]` に更新し、末尾に【2026-10-25 委任_04 ユーザー判断記録: 記事B Std/Adv最終版=ユーザー試聴PASS・正式承認(原文=…USER_03.md)。追加修正・再生成不要、現公開版=最終版。OPEN-467=CLOSED】を追記。
   - `docs/pm/USER_DECISION_REGISTER_01.md` #166: 「判断済み[記事A・記事B]」に更新し、2026-10-25記事B PASSを追記(本ファイルはCRLF化事故の前例あり。編集後に `git diff --stat` で行数が異常に大きくないことを確認)。
   - `DECISION_LOG.md`: 直近エントリ形式に合わせ1件追加(「FAMILY-X-NEWS-2ARTICLES-E2E-02 記事B 完成承認(ユーザー試聴PASS、2026-10-25)。新Trial FX-PARAGRAPH-CHUNK-TTS-TRIAL-01とは独立」)。索引への追加が既存慣行なら同様に。
   - `docs/pm/ACTIVE_TASK.md`: 固定ヘッダ内の該当行(行21「FAMILY-X-NEWS-2ARTICLES-E2E-02」行)の記事B Statusを CLOSED_USER_PASS(2026-10-25) に更新のみ。他行は触らない。**並行agentが同時編集中。編集直前に再Readし自行のみ最小Edit。**
   - `docs/pm/REPORT_LEDGER.md` が運用中なら同形式で1行。
4. SSOT編集は編集前に対象ファイルをscratchpad(`C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1\scratchpad\`)へバックアップし、編集後に `git diff --stat -- <file>` で意図外の大量差分がないことを確認(空ファイル化事故の再発防止)。
5. 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index 496 --out docs/pm/delegation_log/2026-10-25_FAMILY-X-NEWS-2ARTICLES-E2E-02_DELEGATION_04.md`。抽出結果の冒頭が本委任文(「管理ID: FAMILY-X-NEWS-2ARTICLES-E2E-02 委任_04」)と一致するか確認し、不一致なら index 494〜499 を順に試す(`--index -1`は不可)。
6. Git: `git status` → 対象pathのみ `git add <path>`(禁止: `-A/-u/-f/-N`、amend、rebase、force push、stash、clean、reset --hard、checkout -f/`git checkout -- <file>`) → `git diff --cached --name-status` で意図外のD/Aがないこと・secret grep 0件 → `git commit --only -- <path…>` → `git push origin HEAD:main`。他agentの差分が同一SSOTファイルに混在しstageに入る場合は、HEAD blob+自分の変更のみの一時index方式(`git hash-object -w` → `git update-index --cacheinfo`)で自分の変更だけをcommit。ACTIVE_TASK/RESULT_PACKETはgitignore対象(commitしない)。
7. 報告: `docs/pm/RESULT_PACKET_FXN2_CO.md` に、変更ファイル一覧・commit hash・`check_delegation_prompt.py`結果・費用(0円)・問題点を記録。最終回答でも同内容を簡潔に。raw.githubusercontent.com URL(CLOSEOUT_02.md)を添える。

## 3. 禁止
- 音声・本文・KP・ページの再生成・変更。Production code/Prompt/flag変更。
- 新Trial(§2以降)の作業着手。
- API支出。