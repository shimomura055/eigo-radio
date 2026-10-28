# BUDGET_LOG_01B(FAMILY-Y-SOURCE-DEEP-RESEARCH-01 委任_01B、2026-10-28)

| 項目 | 内容 |
|---|---|
| 有料API(LLM/TTS/ASR/検索API) | 0回・0円 |
| 外部HTTP | 約130リクエスト(HN Algolia/SE API/Mumsnet/Guardian/Reddit RSS/Lemmy/Mastodon/MSE/各サイト到達確認)。いずれも無料・無認証 |
| 実費 | 0円(日次1,000円・案件300円に対する消費なし) |
| STOP確認 | `stop_check_01B.json` stop=false(rc=0) |
| 備考 | Redditは数リクエストで429、40秒以上空けて再取得(probe・一覧・本文RSSで合計約15回)。robots.txt全面Disallowのため必要最小限に留めた(要記載) |
