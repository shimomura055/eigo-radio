FABLE-DELEGATION-MARKER: BYUS-KP-LISTEN-CLOSEOUT-PREP-委任_02-20261022

# 委任(FAMILY-X-BYUS-KP-ASR-LISTENING-PAGE-01 委任_02: OPEN-444のCloseout準備記録のみ。API 0・JPY0・コード/音声/ページ無変更)

## 管理ID
FAMILY-X-BYUS-KP-ASR-LISTENING-PAGE-01 委任_02(OPEN-444。並行agent複数(er102 KPMP、er103 PNAP設計、HRQFIX 委任_02)がOPEN_ITEMS/REPORT_LEDGERを編集中。`git status`→該当行再Grep→自分の行だけ→即add+commit、`index.lock`は30秒待ち)。

## 性質/禁止
- 記録のみ。到達Status: OPEN-444=`EVIDENCE_COMPLETE_USER_EAR_CHECK_PENDING`。Opus非該当。JPY0。
- 禁止: `git add -A/-u/-f`、amend、rebase、force push、stash、clean、reset --hard、checkout -f。secret_scan hits=0。push=`git push origin HEAD:main`。ACTIVE_TASK/RESULT_PACKETはgitignore。SSOT全文読込禁止。他agentの未commit差分を混ぜない。

## 事前確認(0円)
1. 試聴ページ https://shimomura055.github.io/eigo-radio/user_test/byus_kp_asr_listen_01/index.html がHTTP 200で、`er099_byus_kp_asr_listen_play_verify_01.py`で再生検証を再実行(全9 player OK・console error 0)。結果を`docs/research/FAMILY-X-BYUS-KP-ASR-LISTENING-PAGE-01/pages_play_evidence_02.json`へ保存(ローカルPlaywrightのみ、API 0)。
2. `docs/research/FAMILY-X-BYUS-KP-ASR-LISTENING-PAGE-01/mapping_01.json`から、take part問題音声(sha 675cd6b1…)の判定回数(Production再判定3回=同一ファイル)と、byUs 7件のPrimary/Secondary/Whisper small・medium文字列を再掲用に抽出(数値を変えない)。

## 記録内容(Fable整理、逐語)
- 「take part 3/3 NG」の実体: NG 3回はProduction経路で**同一wav(sha 675cd6b1)を3回再判定**した結果(Primary/Azureとも「Take tart」)であり、別の3音声ではない。他のNG音声は保存されていない。同wavの追加判定: Primary 10回中 Take tart 6/Take part 3/Take heart 1、Azure 13/13 Take Tart、Whisper small「Take Tarte」/medium「Take Tart」。合格音声(現行KP4、sha e4405501…)は4系統とも「Take part.」。**発音不良かASR誤認識かの最終判断は耳(ユーザー)**。機械的根拠(独立3系統が揃ってtart系)はTTS側の発音逸脱を示唆するが断定しない。承認済み記事Bの音声は合格音声を使用(ユーザー受入済み2026-10-22)。今後の対応: KP英語フレーズはPrimary・Secondary両方PASS必須(OPEN-440、PRODUCTION_WIRED)で、この型は自動でNG→再生成される。追加の仕様・Trialは不要。
- byUs 7件: 全件Whisper small/medium追加確認済み(両サイズ同判定)。新基準NG=think up(Primary「ThinkUp.」PASS/Azure「Think.」NG/Whisper「Think up.」PASS)、blurt(Primary「Blur.」NG/Azure「Blurt.」PASS/Whisper「Blurt」PASS)。いずれも3系統中2系統が正しく聞き取っており、機械的根拠はASR側の揺れを示唆するが断定しない(最終は耳)。承認済み記事Bの音声は変更しない。Store上の2エントリは新基準でNGのため、次回のFamily X再利用時に自動で再生成される(既記録)。
- Closeout条件: ユーザーが試聴ページで(1)take part A/Bの聞き比べ、(2)think up/blurtの発音、を確認し「問題なし/異常あり」を回答→OPEN-444を`CLOSED_USER_CONFIRMED`(異常ありの場合は該当音声の扱いを別途1件判断)。確認・承認操作は記事完成の必須条件ではない(記事Bは受入済み)。

## 更新
- `OPEN_ITEMS.md` OPEN-444: Statusを`EVIDENCE_COMPLETE_USER_EAR_CHECK_PENDING`へ、履歴に上記要点1文+Closeout条件。
- `docs/pm/USER_DECISION_REGISTER_01.md`: Grep `#147` → 直後に `- #148(UDR・**回答待ち**・非blocking、FAMILY-X-BYUS-KP-ASR-LISTENING-PAGE-01、OPEN-444) 件名=byUs KP音声7件+take part聞き比べの耳確認(問題なし/異常あり)。証拠完備・ページ再生検証済み。Fable推奨=問題なしならCLOSED_USER_CONFIRMED。URL=https://shimomura055.github.io/eigo-radio/user_test/byus_kp_asr_listen_01/index.html` を追加。
- `docs/pm/REPORT_LEDGER.md`1行。T-0: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-22_FAMILY-X-BYUS-KP-ASR-LISTENING-PAGE-01_委任_02.md`(Nは`FABLE-DELEGATION-MARKER: BYUS-KP-LISTEN-CLOSEOUT-PREP-委任_02-20261022`を含むAgent tool_useの通番、278前後。先頭行で一致確認)。
- 明示add: 上記3ファイル+pages_play_evidence_02.json+delegation_log。commit: `BYUS-KP-LISTEN 委任_02: OPEN-444 Closeout準備(再生再検証・事実整理・UDR #148)、記録のみ¥0`。push。

## 報告(RESULT_PACKET_BYUSKP2.md)
再生検証結果/更新箇所/RESULT_PACKET 4行/raw URL。