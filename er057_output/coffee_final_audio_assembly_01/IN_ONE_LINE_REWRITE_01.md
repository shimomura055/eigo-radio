# IN_ONE_LINE_REWRITE_01(FAMILY-X-COFFEE-FINAL-AUDIO-ASSEMBLY-01 委任_01、2026-10-12、Trial隔離)

## 方針の区別(記録用)
- 既存仕様(CURRENT_SPEC): In One Line節構成=「中心1文(要約)+英語の短い補足2文程度」。現行完成版は中心1文のみで、**この既存仕様の履行不足**だった(Comment 4の導入に見合わない短さ)。
- 今回のユーザー決定(2026-10-12): 両レベル**2文基本(必要なら3文)**。1文目=記事の核心、2文目=意味・示唆で自然に締める。これは既存仕様の履行不足の是正とは別の「新方針」。仕様化(CURRENT_SPEC共通仕様への反映)は未決でOPENとして別管理(共通仕様は今回変更しない)。

## 生成条件
LLM: `gpt-6-luna`(Production英語Writerと同一、response model一致assert済み)、reasoning=medium、各レベル1 call(再生成なし)。入力=既存article本文(Story/Points)+Key Phrase+Comment 4+旧In One Line(参考)。新Fact追加禁止を指示。費用 Std JPY0.0806 / Adv JPY0.1237。生データ `iol_llm_result_01.json`、確定原稿 `iol_final_text_01.json`。

## 新原稿(確定、本文/Comment/KPは作り直さない)
- **Standard(A2)**: Coffee bean prices fell, but shop prices may take at least about nine months to change. Other costs also matter, so lower bean prices do not promise a cheaper cafe cup.
- **Advanced(B1B)**: Experts estimate raw-bean prices may take at least about nine months to show up in US retail prices. Even if bean prices fall, a cafe cup may not get cheaper because cups and labor also add to its cost.
- (参考)旧: Std「Falling coffee bean prices may take at least nine months to affect US shop prices.」/ Adv「...US retail prices.」(各1文)

## 事実対応表(既存Story/Pointsとの対応)
| level | 文 | 根拠(article.md段落) |
|---|---|---|
| Std | S1 豆価格が下がった / 店の価格は変わるまで少なくとも約9か月かかるかも | 段落2(ICO指標 8.7%下落)、段落6(Reuters取材で「at least about nine months」)。hedge「may」は段落8(推定であり約束ではない)と整合 |
| Std | S2 他の費用も関わるので豆が安くなってもカフェの1杯が安いとは限らない | 段落9(カフェ運営者: カップ・人件費・豆購入費。「Even if bean prices fall, other costs do not always fall」) |
| Adv | S1 専門家は生豆価格が米国小売価格に反映されるまで少なくとも約9か月かかる可能性と推定 | 段落6(estimates from market insiders and experts interviewed by Reuters / at least about nine months / show up in US retail prices) |
| Adv | S2 豆価格が下がってもカフェの1杯は安くならないかも。カップと人件費も費用に加わる | 段落9(cost of cups and labor ... Even if bean prices fall, other costs do not always fall) |
新Fact・新数値・新固有名: なし(数値は「nine months」のみ、既存と同一。「about/at least/may」のhedgeを保持)。

## 難易度チェック(既存compute_metrics相当: 英単語数・文数・文長)
| level | 語数 | 文数 | 文長(語) | 備考 |
|---|---|---|---|---|
| Std(A2) | 31 | 2 | 16 / 15 | 短文2つ。語彙は既存A2記事の語(price, shop, cost, cheaper, cafe, cup)の範囲。旧原稿(16語1文)の約2倍 |
| Adv(B1B) | 40 | 2 | 19 / 21 | 「Experts estimate」「show up」「retail」「labor」は既存B1B記事の語彙。1文最大21語(B1の文長診断目安内、hard制限なし) |
既存B1/A2の難易度指標は「平均文長を診断として記録、hard制限なし」(`er003_v1_n3_01_articles_generate.py` B1指示)。本件は診断記録のみで、制約違反なし。

## Comment 4との接続
- Std Comment 4(R2、日本語): 「...値段が変わる時期には、豆以外の費用も関わります。続いて、記事の要点を英語で聞いていきましょう。」 → 新IOL S1(時期=約9か月)、S2(豆以外の費用)がComment 4の2論点をそのまま英語で回収する構成。
- Adv Comment 4(既存承認): 「...There can be a delay, and other costs matter too. Now, let's bring the main idea together.」 → 新IOL S1(delay=約9か月)、S2(other costs)で同じ2論点を回収。Comment 4と語の重複は最小(「nine months」「cups and labor」は新情報としてCommentに出ていない既存記事内容)。
- 見出し「In One Line」は維持(timeline part名変更なし)。

## 音声生成(Trial隔離、Primary ASR判定、再生成0回)
| level | Style(sha先頭12) | model/voice | Primary ASR | duration | wav sha(先頭12) |
|---|---|---|---|---|---|
| Std | IN_ONE_LINE既存承認Style+A2減速指示(10e21170b1b1)、現行Std IOLと同一Prompt | gemini-3.8-flash-lite-tts / Aoede | NORMALIZED_MATCH、attempt 1 | raw 11.59s → 6%減速 12.272s(ratio 1.0588)、減速後sha c82267e275dc(参考ASR: NUMERIC_EQUIVALENCE_MATCH) | raw fdfb23a5d8b3 |
| Adv | IN_ONE_LINE既存承認Style(63495557ec82)、現行Adv IOLと同一Prompt | 同上 | NUMERIC_EQUIVALENCE_MATCH、attempt 1 | 13.36s | 645cac39d8a6 |
Secondary ASR / Local Rewrite / minimal fallback 不使用。詳細ログ `generation_log_v3_01.jsonl`。
