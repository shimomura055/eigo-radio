# 委任文: USER-TEST-REVIEW-PAGE-FORMAT-RULE-01

## 管理ID
USER-TEST-REVIEW-PAGE-FORMAT-RULE-01

## 性質
ユーザーテスト視聴ページの表示フォーマット恒久ルール適用(表示・生成テンプレート・SSOTのみ、
音声・canonical・Key Phrase選定は不変)。並行Agentなし。API呼び出し0、TTS/ASR/音声変更0。
Sonnet委任、初回。

## 事前指定Read一覧
- build_web_player_common.py
- user_test/unified.html
- user_test/human_review.html
- 対象9本のplayer.html(Key Phrase/ヘッダー部分のみ)
- legacy web export 1本(er003_output/b1_p9a/A02/web/)
- docs/pm/closeout_136_e2e/ のE2Eスクリプト
- docs/pm/PM_GOVERNANCE.md 2節Gate 7・9-12

## 事前指定Grep一覧+追記位置・更新位置の手順
- Grep: `English:`/`日本語:`/`English｜`等のラベル文字列混入箇所(Key Phrase描画関数)
- Grep: `level` 表示分岐箇所(unified.html/human_review.html/build_web_player_common.py)
- 追記位置: PM_GOVERNANCE.md Gate 7 (2節) 末尾に(n)追加。CURRENT_SPEC.mdは該当行の有無を
  Grep(`unified.html`/`build_web_player_common`/`Web Player`)で確認し、あれば追記、無ければ
  理由を報告してPM_GOVERNANCEのみとする。DECISION_LOG.mdは
  `## USER-TEST-REVIEW-PAGE-FORMAT-RULE-01` の索引+本体セクションを新規追加。
  ARTIFACT_REGISTRY.mdは既存9本のURL行を新SHAへ置換。

## 実行コマンド全文
- `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\USER-TEST-REVIEW-PAGE-FORMAT-RULE-01.md --json-out docs\pm\delegation_log\USER-TEST-REVIEW-PAGE-FORMAT-RULE-01_check.json`
- `.venv\Scripts\python.exe docs\pm\tools\user_test_page_e2e_check.py --urls-file docs\pm\closeout_136_e2e\format_rule_01\urls.txt --out docs\pm\closeout_136_e2e\format_rule_01\e2e_result.json`(新規作成、Playwright headless Chromium)
- `sha256sum er014_output/user_test_news_light_01/tiny_bags/a2/episode.mp3`(各対象9本の音声/segmentsについて再build前後比較)
- `git fetch origin`
- `git merge origin/main --ff-only`

## SSOT追記文
- docs/pm/PM_GOVERNANCE.md: Gate 7 (2節) (n) ユーザー試聴ページ表示フォーマット(Key Phrase
  2列・ラベル禁止、Standard/Advanced表記、チェッカー名、2026-09-17ユーザー正式決定、管理ID)。
  9-12に「確認ページのlevel表示も同ルール」1行追記。変更履歴節に1行。
- CURRENT_SPEC.md: 該当行があれば表示フォーマット規定を追記(無ければ理由報告のみ)。
- DECISION_LOG.md: `## USER-TEST-REVIEW-PAGE-FORMAT-RULE-01`索引+本体(指摘内容・原因・修正箇所・
  9本再発行URL・E2E結果)。
- ARTIFACT_REGISTRY.md: 9本のURLを新SHAへ更新。
- OPEN_ITEMS.md: 恒久チェッカー導入完了扱い。未解決が残る場合のみ登録。

## Git(明示add対象・コミットメッセージ・trailer)
- 明示add対象のみ(git add -A禁止、wav禁止、mp3は差分なし確認)。
- 対象: build_web_player_common.py、user_test/unified.html、user_test/human_review.html(必要時)、
  対象9本のplayer.html、docs/pm/tools/user_test_page_e2e_check.py(新規)、
  docs/pm/closeout_136_e2e/format_rule_01/配下、PM_GOVERNANCE.md、CURRENT_SPEC.md、
  DECISION_LOG.md、ARTIFACT_REGISTRY.md、OPEN_ITEMS.md、docs/pm/delegation_log配下。
- commit分割可(コード+player再build → SSOT)。
- 各commitメッセージ末尾に `Task-ID: USER-TEST-REVIEW-PAGE-FORMAT-RULE-01` および
  `Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>`。
- fetch→merge(--ff-only優先)を先に実施。

## 報告(RESULT_PACKET項目)
docs/pm/RESULT_PACKET_REVIEW_PAGE_FORMAT_01.md へ、0.T-0 1.原因 2.修正箇所 3.9本URL一覧
4.E2E結果表 5.音声無変更証跡 6.legacy4本確認結果 7.SSOT反映箇所 8.Git SHA 9.ユーザー判断A/B
10.無変更証跡/事前指定外Read、をそれぞれ簡潔に記載する(★★★★報告ここから/ここまで)。

## 禁止事項
- Production正式path混入禁止(Trial実装の無断混入禁止)。
- 音声(TTS/ASR)再生成禁止、Key Phrase選定・canonical内容の変更禁止。
- git add -A禁止。破壊的git操作禁止。
- 未承認仕様のProduction実装禁止(表示フォーマットは既にユーザー正式指示のため対象外)。
