# FAMILY-Y-SOURCE-DEEP-RESEARCH-01 委任_02A「候補情報源の利用規約・ポリシー精査と用途適合判定」(委任本文、Fable→sonnet-worker、2026-10-28。逐語)

管理ID FAMILY-Y-SOURCE-DEEP-RESEARCH-01 委任_02A「候補情報源の利用規約・ポリシー精査と用途適合判定」。ユーザー決定(2026-10-28 USER_02、並行worker 委任_02Bが`docs/pm/delegation_log/2026-10-28_FAMILY-Y-SOURCE-DEEP-RESEARCH-01_USER_02.md`へ逐語保存中。Globで確認し存在すれば全文を読む): ①発言小町は当面除外 ②Reddit公式API申請は見送り・自動収集対象外 ③他の調査結果はRepoへ正式記録(候補登録≠Production利用承認)。**今回の必須条件(§4)**: 最終5テーマに使う全情報源について、Family Yの想定用途=「実際の投稿から意見・経験・価値観を読み取り、それを参考に独自のPersona・一人称原稿を生成し、商用の英語学習ラジオで提供する」に照らし、最新の利用規約・関連ポリシーを**実際に読んで**判定する。「閲覧できる/robots.txtで禁止されていない」だけで利用可能と判断しない。判定区分=利用可能/条件付き利用可能(条件明記)/未確認/利用不可。規約解釈に重大な不確実性が残る場合は「問題なし」としない。

**ファイル範囲**: `docs/research/FAMILY-Y-SOURCE-DEEP-RESEARCH-01/TERMS_REVIEW_01.md`、同`terms_evidence/`(規約本文の取得証跡: URL・取得日時・sha・該当条文の逐語抜粋)、同`BUDGET_LOG_02A.md`、同`stop_check_02A.json`、`docs/pm/delegation_log/2026-10-28_FAMILY-Y-SOURCE-DEEP-RESEARCH-01_委任_02A.md`(本文逐語)、`docs/pm/RESULT_PACKET_FYDR2A.md`。SSOT・ACTIVE_TASK・Production code編集禁止。LLM不使用、API 0(HTTP取得のみ、礼儀的レート、robots遵守。規約ページの取得はrobots許可範囲で)。Family A/B/C不可。
開始時 `.venv\Scripts\python.exe tools/stop_scope_check_01.py --managed-id FAMILY-Y-SOURCE-DEEP-RESEARCH-01 --run-dir docs/research/FAMILY-Y-SOURCE-DEEP-RESEARCH-01 --out docs/research/FAMILY-Y-SOURCE-DEEP-RESEARCH-01/stop_check_02A.json`(rc=3で停止)。

## 対象サイト(委任_01A/01Bの候補。`DOMESTIC_SOURCES_01.md`/`OVERSEAS_SOURCES_01.md`を先に読む)
国内: Yahoo!知恵袋(LINEヤフー利用規約+知恵袋ガイドライン+robots)、ガールズちゃんねる、はてな匿名ダイアリー(はてな利用規約・はてなラボ規約)、ママスタBBS、5ちゃんねる、note(参考)。海外: Hacker News(Y Combinator利用規約+Algolia HN Search API条件)、The Guardian(Open Platform利用規約=discussion APIの商用条件)、Mumsnet(Talk guidelines/Terms)、Stack Exchange(CC BY-SA 4.0+API規約)。発言小町は除外決定済み(判定不要、「利用不可(ユーザー決定①)」と記録のみ)。Reddit=「対象外(ユーザー決定②)」と記録のみ。

## 各サイトで確認・記録する項目(§4の列挙に対応)
最新の利用規約・関連ポリシーURLと取得日/自動収集・スクレイピングの可否/文章解析・AIへの入力(テキストマイニング・情報解析)の可否/AI原稿生成の参考素材としての利用可否/商用サービスでの利用可否/引用・要約・翻案・転載の制限/個人情報・プライバシー/robots.txt・API条件・アクセス制限/必要なライセンス・許諾。各項目に**条文の逐語抜粋(file:行 or URL#条)**を付け、条文が無い場合は「該当条文なし」と書く(「禁止がない=可」とは書かない)。日本法の著作権法30条の4(情報解析)・32条(引用)との関係は、一般的事実として注記してよいが法的助言ではないと明記し、規約が30条の4を契約で制限している場合はその旨を書く。
判定: 4区分+条件(例: 「人が読んで着想を得る/要約のみ/逐語転載なし/自動収集はAPI経由のみ/帰属表示」等)+残る不確実性。**判断が割れる場合は未確認または条件付きに倒す。**

## 成果物
- `TERMS_REVIEW_01.md`: サイト別の確認表(上記項目)+判定+根拠+確認日+「規約上の禁止/アクセス不能/低優先度」の区別。最後に「利用可能・条件付きのサイト一覧」と「5テーマの根拠資料に使えるサイト」を明示。
- `terms_evidence/`: 取得した規約本文(全文は転載せずsha+該当条文抜粋。全文はローカルcacheのみ、未追跡)。
- `BUDGET_LOG_02A.md`(API 0)、`docs/pm/RESULT_PACKET_FYDR2A.md`(≤15行: 判定一覧、未確認・不可の理由、判断候補A/B/C/D、判定整合行)。
- Git: `git diff --cached --name-only`空確認→自分のファイルのみ明示`git add … && git commit -m "FAMILY-Y-SOURCE-DEEP-RESEARCH-01 委任_02A: 候補情報源の利用規約精査・用途適合判定(API 0)"`を1コマンド、`git add -A`禁止、他workerファイル不可。`git push origin HEAD:main`(FFのみ、拒否時fetch後再試行、force禁止)。hand-back: サイト別判定(1行ずつ: 区分+決め手の条文)、5テーマ根拠に使えるサイト、未確認の理由、commit sha。
