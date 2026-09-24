# 日本語Trial(NEWS-ITERATIVE-ENTERTAINMENT-TRIAL-02, Article A)
# vs 英語Trial(NEWS-ENTERTAINMENT-PRODUCTION-LINE-TRIAL-01 Phase B)比較

同一テーマ(Meta Muse AI電話代行「人間コンシェルジュ」実験、Reuters
2026-09-22)を素材にした2つの独立Trialの構造比較。日本語Trial側は本
タスクで変更していない(読み取りのみ)。

## 入力条件の違い

| 項目 | 日本語Trial(TRIAL-02) | 英語Trial(本Phase B) |
|---|---|---|
| Fact源 | Reuters記事1段落の素材文(2-3文)のみ、Web検索なし | 既存Production Research/Verification(web_search計8回、18 facts、Verified Fact Ledger) |
| Ledger | なし(単純な修正指示連鎖) | あり(Production正式形式、17 VERIFIED/1 AMBIGUOUS) |
| 構造Gate | なし(Trial側で構造検証は未実施) | あり(parser/Structure Validator/Ledger Deviation Checker/Point Overlap QA、全て既存Production関数) |
| 記事構造 | タイトル+自由形式本文(Point見出しなし) | Title + Main Story + `###`×2 + `## In one line`(既存News B1-B contract) |
| Revision回数 | Original→R1→R2→R3(4版、R3もTrial実施) | Original→R1→R2(3版、R3は生成しない契約) |
| 語数目安 | 800〜1000字(日本語文字数) | 280〜420語(英語、B1 soft target) |

## Title比較

| Stage | 日本語Trial | 英語Trial |
|---|---|---|
| Original | AI電話の舞台裏には、人がいた | The AI Phone Call That Needed a Human |
| Revision2(Final) | 「もしもし、AIです」――その声の裏で、人間が代役を務めていた | Muse, the AI Caller With a Human Plot Twist |

## 切り口(Angle)の比較

- 日本語Trial: 「舞台/人形/幕の後ろ」の比喩を一貫して使い、AIの電話に
  人間が「代役」として隠れているという劇場的な見立てで展開。
- 英語Trial: Original/R1では「trust(信頼)」を軸に説明的に展開し、
  R2(Final)で「script takes a sharp turn」「co-star」「opening night」
  という舞台・脚本の比喩へ収束した(Revisionを重ねるごとにEntertainment
  色が強まる点は日本語Trialと類似する傾向)。

## Fact Safetyの違い(観測事実)

日本語Trialは素材文(2-3文)のみが事実源であり、Ledger Deviation
Checkerのような機械的なFact Safety検査を経ていない。英語Trialは
Production正式Ledger(18 facts)に対しLedger Deviation Checkerを3
Stageすべてに実行し、Stage0で1件のMAJOR逸脱(Ledgerが直接支持しない
「人間ヘルパーを目立たせない意図があった」という解釈の追加)を検出、
Stage1/Stage2で自然に解消したことを確認した(詳細は本REPORT §10)。
この機械的検査は日本語Trial側には存在しないため、単純な優劣比較では
なく「英語Trialにのみ機械的Fact Safety検査が付与されている」という
条件差として記録する。

Editorial Quality(面白さ・自然さ)の主観評価はSonnetが行わない
(委任文の指示どおり、REPORT §17/§18はFable記入欄)。
