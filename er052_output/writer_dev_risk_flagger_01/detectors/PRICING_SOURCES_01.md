# PRICING_SOURCES_01 (WRITER-DEV-RISK-FLAGGER-DESIGN-01 委任_01B, 2026-10-09)
単価の出典。HTTPで公式ページを取得し(HTTP 200)、script/styleを除いてテキスト化した行を原文として記載(表セルが1行ずつ分割されているため ` | ` で連結)。推測値は登録していない。

## OpenAI  https://developers.openai.com/api/docs/pricing  取得日 2026-10-09
raw html sha256 = 79766b1f40e9444c433035400db0f85b699941371e2af6f3aa5fc215a60202a8
列順: Short context[Input | Cached input | Cache writes | Output] / Long context[同]
- gpt-6.1-sol 行(テキスト化 L863-L871、Standard表): `gpt-6.1-sol | $2.00 | $0.10 | $2.50 | $10.00 | $4.00 | $0.20 | $5.00 | $15.00`
  -> Short context Standard: input 2.00 / cached 0.10 / cache write 2.50 / output 10.00 ($/1M)。Long context(4.00/0.20/5.00/15.00)・Batch/Flexは登録しない。
- gpt-5.6-sol 行(Cyber models欄、L1051-L1059): `gpt-5.6-sol | $4.00 | $0.40 | $5.00 | $20.00 | $8.00 | $0.80 | $10.00 | $30.00`
  -> Short context: input 4.00 / cached 0.40 / cache write 5.00 / output 20.00。旧登録値(2026-08-17): 5.00 / 0.50 / 30.00。公式現行値へ更新、旧値は pricing_snapshot.json の price_history に保持。
- 脚注(L1035-L1036): `2026. GPT-5.6 Sol’s promotional pricing is available at least through | November 21, 2026.`
- gpt-6-astra(10.00/1.00/12.50/50.00)、gpt-6-luna(0.10/0.01/0.125/0.50) は本ページと既登録値が一致(変更なし)。

## DeepSeek  https://api-docs.deepseek.com/quick_start/pricing  取得日 2026-10-09
raw html sha256 = 210f102275ccf1a6542f08a3bc9e4b4c7c83278cb74b35217bffa112df6363b2
- モデル行(L41-L50): `deepseek-flash | (1) | deepseek-v4-pro | BASE URL (OpenAI Format) | https://api.deepseek.com | BASE URL (Anthropic Format) | https://api.deepseek.com/anthropic | MODEL VERSION | DeepSeek-V4.1-Flash | DeepSeek-V4-Pro-0813`
- 価格表(L82-L106): `PRICING | (2) | 1M INPUT TOKENS | (CACHE HIT) | OFF-PEAK | $0.003 | $0.022 | PEAK | $0.006 | $0.044 | 1M INPUT TOKENS | (CACHE MISS) | OFF-PEAK | $0.15 | $0.66 | PEAK | $0.3 | $1.32 | 1M OUTPUT TOKENS | OFF-PEAK | $0.6 | $1.98 | PEAK | $1.2 | $3.96`
  -> deepseek-v4-pro (DeepSeek-V4-Pro-0813): Peak cache hit 0.044 / cache miss(input) 1.32 / output 3.96; Off-peak 0.022 / 0.66 / 1.98 ($/1M)。Standard=Peak を費用算出に使用(既存deepseek-v4-flash登録と同方針)。
- 注: 本ページ上のFlashは `deepseek-flash`(旧名deepseek-v4-flashはFlash価格で課金)。
