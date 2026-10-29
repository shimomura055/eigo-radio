# PUBLISH_EVIDENCE_01 (FX-MOON-SHRINKING-FINAL-PUBLISH-01、API 0)
## 公開URL
https://shimomura055.github.io/eigo-radio/user_test/family_x_moon_shrinking_reselect_01/index.html (Std/Adv同一ページ、音声audio/46件)
## 手順根拠
- ユーザー承認原文=docs/pm/delegation_log/2026-10-29_FX-MOON-SHRINKING-FINAL-PUBLISH-01_USER.md(UDR #217回答)。先例=FX-PAYCHECK-PERSONALITY-FINAL-PUBLISH-01(試聴物=公開パス、複製不要)。候補ページが既に公開パス(user_test/family_x_moon_shrinking_reselect_01/)のため複製なし。
- 索引ページ・CURRENT_SPEC公開台帳: 月記事の登録なし(Grep確認、Paycheck先例同様に新設せず)。
## 変更(1箇所のみ)
- div.note: 「状態: 完成候補・ユーザー試聴待ち(正式公開ではありません)(試聴PASSは未取得です)。」→「状態: 正式公開(2026-10-29)(ユーザー試聴PASS・公開承認 2026-10-29)。」。<title>に候補表記なし(変更なし)。本文/音声/KP/文法/ハイライト変更0、「=====」0件。
## 検証
- tools/user_test_page_standard_check_01.py: PASS(page_standard_check_01.json)
- 公開commit 88df63bb0(origin/mainへcherry-pick push、rebase/force無し)。
- live(cache無効、live_verify_01.json): HTTP200、新文言1件+「ユーザー試聴PASS・公開承認 2026-10-29」1件、旧文言0件、「=====」0件、音声46/46 HTTP200かつrepoとbyte一致、Playwright console/HTTP>=400 error 0。index.htmlはlive sha256先頭16=c4bc9cfb00534a83=git blob(LF)と一致(作業ツリーCRLFのためスクリプト上のmatch_repoはFalse)。
