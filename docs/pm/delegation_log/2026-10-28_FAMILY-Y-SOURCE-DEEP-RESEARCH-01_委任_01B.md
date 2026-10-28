# FAMILY-Y-SOURCE-DEEP-RESEARCH-01 委任_01B「海外情報源・テーマのDeep Research」(委任本文、Fable→sonnet-worker、2026-10-28)

管理ID: FAMILY-Y-SOURCE-DEEP-RESEARCH-01。並行して委任_01A(国内)が同じ管理IDで稼働中。ユーザー原文は `docs/pm/delegation_log/2026-10-28_FAMILY-Y-SOURCE-DEEP-RESEARCH-01_USER.md`。
**ファイル範囲**: `docs/research/FAMILY-Y-SOURCE-DEEP-RESEARCH-01/OVERSEAS_*`・同`sources_overseas/`・同`BUDGET_LOG_01B.md`・同`stop_check_01B.json`、本ファイル、`docs/pm/RESULT_PACKET_FYDR1B.md`。SSOT・ACTIVE_TASK・Production code・Prompt・仕様は変更禁止。Family A/B/C不可。本文制作・英訳・TTS・公開は行わない。
開始時 `tools/stop_scope_check_01.py --managed-id FAMILY-Y-SOURCE-DEEP-RESEARCH-01 --run-dir docs/research/FAMILY-Y-SOURCE-DEEP-RESEARCH-01 --out .../stop_check_01B.json`(rc=3で停止)。費用: 原則API 0(requests+BeautifulSoup、公開JSON/RSS/API、本文取得可否を実測、礼儀的レート、robots/利用規約を確認し大量取得しない)。LLM呼出は要約目的でも使わない(ユーザー原文「AIがもっともらしい意見を補ったりする調査にはしない」)。既存成果 OPINION_BASED_02/SOURCE_LOG_02.md・PROVENANCE_04.md・scripts/search_01.py を先に読み重複調査を避ける。

## ユーザー要点(原文優先)
- 目的: Family Y 3 Voiceをリアルな一人称発言にするための議論テーマと情報源の発掘、継続利用可能なサイト・収集方法の発掘。調査のみ。
- 海外は次点。日本人の生活・価値観・社会問題と関係が薄いテーマ中心のサイトは優先度を下げる。日本のリスナーが自分事にできるテーマは高評価。所在地より日本人との関連性と意見の質(同程度なら国内優先)。
- 良いテーマ条件7点、情報源評価8観点、Persona設計思想、成果物B/C/D、QCD(70円/記事セット、中間報告不要)。実際の投稿本文を読んで検証し、見出し・検索結果だけで本文確認済みのように書かない。

## 手順
1. 候補サイト最低12。各サイトで実スレッドを本文取得し `sources_overseas/<site>_<n>.json`(URL・取得日時・投稿日時・本文抜粋[要約+短い抜粋]・取得方法)へ保存。取得不可は「未確認」と明記。
2. `OVERSEAS_SOURCES_01.md`(8観点+特徴・議論例URL・投稿質・3 Voice活用可能性・継続利用の容易さ・日本人関連テーマ発掘可否・推定収集コスト、優先順位付き)。
3. `OVERSEAS_THEMES_01.md`(実投稿から確認した有望テーマ最低8件、表形式C、想像と確認済みを区別)。
4. `OVERSEAS_METHOD_01.md`(低コスト・短時間の収集手順案、信頼性・偏り・規約注意、提案であり正式仕様ではない)。
5. `BUDGET_LOG_01B.md`、`docs/pm/RESULT_PACKET_FYDR1B.md`(≤15行: 上位サイト5・テーマ5・未確認・判断候補・判定整合行)。
6. Git: `git diff --cached --name-only`空確認→自分のファイルのみ明示add→commit "FAMILY-Y-SOURCE-DEEP-RESEARCH-01 委任_01B: 海外情報源・テーマDeep Research(API 0)"→`git push origin HEAD:main`(FFのみ、force禁止)。`git add -A`禁止。hand-back: 上位サイト5、テーマ上位5、未確認・制約、費用、commit sha。
