# C1 stub E2E(API呼び出し0、¥0)
POST-EN Trialの実記事11本+実台帳を `er053_risk_flagger_production_01.run_risk_flagger`(call_fn=stub)に通し、
`er053_review_queue_01.save_queue` で保存した結果のサマリ(summary.json: unit,status,sentences,facts,issues,saved)と、
代表1本(X09、`ensuring U.S.` を含む)のQueue出力サンプル。**Flagはstubの固定値(Luna=0件、Gemini=文3に1件)であり、
モデルの検出結果ではない**。producer=`STUB_FIXTURE_NOT_REAL`。実Review Queue(`review_queue/post_en/`)には書いていない。
