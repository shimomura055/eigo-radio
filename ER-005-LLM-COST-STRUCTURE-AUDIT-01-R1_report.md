# ER-005-LLM-COST-STRUCTURE-AUDIT-01-R1 完了報告

**Unit Economics / Cost Target定義修正を反映したCustomized Episode原価監査**
実施日: 2026-08-18
対象: ER-005-COST-BASELINE-01 / ER-005-TTS-CLEAN-COST-AUDIT-01の既存ログ(新規生成なし)

**注記**: 本タスクが参照する「オリジナルのER-005-LLM-COST-STRUCTURE-AUDIT-01指示」は受領していません。ご指示の通り、本R1を単独で完全な指示として扱い対応しました。Scenario Eの基本定義(Writer=Sol維持、その他LLM=低価格化)はR1本文中の記述からそのまま再構成しています。

---

## Executive Summary

| KPI | AKB48 | Parenting | Average |
|---|---|---|---|
| **Current B1-only customized episode cost** | $2.578 | $3.006 | **$2.792** |
| **Current A2-only customized episode cost** | $2.766 | $3.084 | **$2.925** |
| Target | $0.10 | $0.10 | $0.10 |
| **Gap to target(B1)** | 25.8x | 30.1x | **27.9x** |
| **Gap to target(A2)** | 27.7x | 30.8x | **29.3x** |

内訳(2テーマ平均、B1/A2共通のShared Researchのみ別掲):

| 費目 | B1 | A2 |
|---|---|---|
| Shared Research/Ledger cost | $1.850 | $1.850 |
| Article Writer cost(Sol) | $0.110 | $0.076 |
| Article Writer以外のLLM cost(Sol) | $0.618 | $0.726 |
| Clean-run TTS cost | $0.152 | $0.201 |
| Clean-run ASR cost | $0.063 | $0.073 |

**(A2+B1同時生成Total、Secondary reference)**: ER-005-COST-BASELINE-01のActual Cost $4.90/theme。これはShared Article Pool生産コストの参考値として引き続き有効ですが、Customized Daily DeliveryのPrimary KPIではありません(R1指示1・6節)。

**最重要の結論**: **Shared Research/Ledger cost($1.85、平均)だけで、すでに$0.10目標の18.5倍です。** Article Writerを含む他の全工程を合計しても$1.85には遠く及ばず、Research/Search costがCustomized Episode原価の圧倒的な支配要因です(下記Q5参照)。

## 1. Primary Cost Unit / Business Target(確認)

R1の定義通り、B1-only / A2-onlyそれぞれの完成エピソード原価をPrimary KPIとしました。Break-even reference $0.20/episode、Target AI Variable Cost ≤$0.10/episodeを正式なCost Optimization目標として使用しています。

## 2. Shared Research Costの全額算入(確認)

R1指示5節の通り、Shared Research/Ledger costはB1-only・A2-onlyの**両方に全額**含めています(50:50配賦はしていません)。理由: Customized Deliveryでは実際にはB1かA2のどちらか一方しか生成しないため、Research費を分割する扱いは実態に合わないためです。

## 3. Scenario E(Writer=Sol維持、その他LLM=低価格化)

低価格化想定モデルは`gpt-5.6-luna`(2026-08-18、[developers.openai.com/api/docs/pricing](https://developers.openai.com/api/docs/pricing)で確認。Input $0.20/1M、Cached $0.02/1M、Output $1.20/1M。Solの1/25)を使用しました。Shared Researchは(Web検索・事実確認の精度が重要なため)Scenario Eでも据え置きSolのままとし、Article Writer以外のLLM(Fact Checker・Ledger Deviation Check・Support/Scaffold生成・Key Phrase選定)のみをLunaへ置き換えた場合の理論原価を、実測トークン数にLuna単価を適用して再計算しました(実測token数を使った厳密な再計算であり、推定ではありません)。

| KPI | AKB48 B1 | AKB48 A2 | Parenting B1 | Parenting A2 |
|---|---|---|---|---|
| Scenario E cost | $1.977 | $2.054 | $2.537 | $2.527 |
| $0.10との差(倍率) | 19.8x | 20.5x | 25.4x | 25.3x |

**その他LLMをSolからLunaへ変更しても(コスト約85%減)、Shared Researchが手つかずのため、目標には遠く届きません。**

## 4. TTS/ASR Costの片レベル評価

| KPI | B1(平均) | A2(平均) |
|---|---|---|
| Clean-run TTS cost | $0.152 | $0.201 |
| $0.10 targetに占める割合 | 152% | 201% |
| Clean-run ASR cost | $0.063 | $0.073 |
| $0.10 targetに占める割合 | 63% | 73% |

**TTSだけでも$0.10 targetを超えます**(B1で152%、A2で201%)。ただしResearch costがそれをさらに大きく上回るため、「LLMを十分安くしてもTTSだけでCost Targetを圧迫するのか」という問いへの答えは、**「TTSも単独でTargetを超える規模の負担だが、Research costの方がさらに大きい」**となります。TTS provider/modelのテコ入れをExternal User Validation前に実施するかは、引き続き未決のままとします。

## 5. Writer品質についての方針(確認)

Article WriterはSolを維持する前提でScenario Eを計算しました。安価モデルへの変更で記事品質(切り口・自然さ・面白さ・Fact扱い・Listening quality)が明確に悪化する場合はWriterをSolへ戻す方針を、今回の計算にもそのまま反映しています(Writer costはScenario EでもCurrentと同額)。

## 6. Shared Pool記事との分離(確認)

本報告のCustomized episode cost(B1-only/A2-only)は、ER-005-COST-BASELINE-01のA2+B1合計コスト($4.90/theme、Shared Article Poolの生産コストに相当)とは独立して算出しています。両者を混同していません(Q6も参照)。

## 7. OPEN_ITEMS登録(確認)

AKB48 A2のKey Phrase全滅(ASR文字起こし空文字列)の件は、[OPEN_ITEMS.md](OPEN_ITEMS.md)のOPEN-43として登録しました。状態は`TBD`(原因未確定)のままで、CLOSEDにはしていません。

---

## 最終Q&A

### Q1. 現在、Customized B1を1本作るAI variable costはいくらか？

**平均 $2.79/episode**(AKB48 $2.578、Parenting $3.006)。Shared Research/Ledger cost $1.85を含む。

### Q2. 現在、Customized A2を1本作るAI variable costはいくらか？

**平均 $2.93/episode**(AKB48 $2.766、Parenting $3.084)。

### Q3. それぞれ$0.10目標の何倍か？

B1: **約27.9倍**。A2: **約29.3倍**。

### Q4. Article WriterだけSolを残し、その他LLMを大幅低価格化(Luna、Solの1/25)した場合、$0.10へ到達可能性があるか？

**到達できません。** Scenario E想定でもB1で$1.98〜2.54(19.8〜25.4倍)、A2で$2.05〜2.53(20.5〜25.3倍)に留まります。その他LLMのコストは元々小さく(Sol時点で$0.62〜0.73)、Lunaへの変更で$0.08〜0.09まで下がっても、削減額は$0.5〜0.65程度にしかなりません。Shared Research($1.85)が手つかずのままである限り、目標には届きません。

### Q5. 到達できない場合、残る最大Cost Floorは何か？

**Research/Search が圧倒的に最大のCost Floorです。**

| 費目 | B1平均 | A2平均 | 内訳の性質 |
|---|---|---|---|
| **Shared Research/Ledger** | **$1.850** | **$1.850** | **単独で$0.10の18.5倍** |
| Clean-run TTS | $0.152 | $0.201 | 単独で1.5〜2.0倍 |
| Article Writer(Sol) | $0.110 | $0.076 | Research の1/17〜1/24 |
| その他LLM(Sol) | $0.618 | $0.726 | Research の1/3弱 |
| Clean-run ASR | $0.063 | $0.073 | 0.6〜0.7倍 |

Sol Writerでも、TTSでも、ASRでもなく、**Shared Research/Ledger(OpenAI Responses API、`gpt-5.6-sol`、web_search tool、reasoning effort "high"による大量token消費)が、他の全費目を合計してもなお上回る規模のCost Floor**です。$0.10目標に近づくには、Research段階自体のコスト構造(web_search呼び出し回数、reasoning effort、収集Fact量)に踏み込んだ見直しが必須であり、これは今回のR1で明示的に「今回は変更しない」とされたTTS architectureとは全く別の論点です。

### Q6. Shared Pool記事のA2+B1生成費とCustomized episode原価が正しく分離されているか？

**分離されています。** 本報告のPrimary KPI(B1-only $2.79、A2-only $2.93、平均)は、ER-005-COST-BASELINE-01のA2+B1合計コスト($4.90/theme、Shared Article Pool生産コストに相当)とは別に、単一レベルのみの生成コストとして独立算出しました。Shared Research costは両者で二重計上していません(B1-only/A2-onlyそれぞれに全額算入する一方、A2+B1合計値では元々1回分のみ計上されているため、算出方法上の混同はありません)。

---

## 付録: 手法・限界

- 新規TTS/ASR/LLM生成は一切行っていません。既存の`raw_usage_log.jsonl`・`pricing_snapshot.json`・`tts_audit_summary.json`・各番組のsegment監査ログのみを再集計しました。
- Article Writer costとその他LLM costの分離は、`*_writer_and_fact_qa`ステージ内の3レコード(Writer→Fact Checker→Ledger Deviation Checkの実行順)のうち、時系列で最初の1件をWriterとみなす方法によります(retry・fallbackが実測上発生していないため、この対応は厳密です)。
- Clean-run TTS costはER-005-TTS-CLEAN-COST-AUDIT-01の推定値(音声長按分、公式合計へ正規化済み)をそのまま再利用しています。Clean-run ASR costは同じ手法(各segmentの最初のattemptの音声長のみを計上)で新たに算出しました。
- Luna単価は2026-08-18に公式ページ(developers.openai.com/api/docs/pricing)で確認した値です。Scenario Eは実測token数にLuna単価を適用した理論値であり、Lunaで実際に同等品質の出力が得られるかは検証していません(Writer以外の工程についても、低価格モデルへの変更が品質へ与える影響は今回未検証です)。
- Production側のコード・CURRENT_SPEC.mdは変更していません。
