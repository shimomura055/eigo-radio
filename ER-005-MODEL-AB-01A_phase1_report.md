# ER-005-MODEL-AB-01A Phase 1 完了報告

**Research / Verified Fact Ledger Low-Cost Model Comparison — Parenting theme**
実施日: 2026-08-18
DeepSeekは今回対象外(`HOLD_FOR_NON_SEARCH_STAGES`として保留)。Sol再実行なし(既存$2.094を使用)。各モデル1回のみ実行(best-of禁止)。

---

## 最上段サマリ

| Model | Parenting Cost(Research+Verification相当) | Quality | Cost Status | Phase 2 Recommendation |
|---|---|---|---|---|
| Sol | $2.094(既存) | Baseline | RED(Baseline) | Reference |
| **Luna** | **$0.1749** | **PASS**(Sol同等〜一部で上回る) | **COST_NOT_VIABLE**(単一要因: Search fee) | 保留・ユーザー判断待ち |
| **Gemini 3.5 Flash-Lite** | **$0.0042** | **FAIL**(実質未Research) | GREEN | 進めない(Quality Fail) |

**この時点でSTOPします。AKB48(Phase 2)へは自動的に進んでいません。**

---

## 詳細

### Luna: Quality PASS(Sol基準の8項目を全て満たす)

| 判定項目 | 結果 |
|---|---|
| Critical Facts | PASS。Solが持つ全項目をカバーし、さらにSolにない統計値(F(3,641)=17.5、p<.001、Cohen's d=0.44、95%CI等)を追加取得 |
| 主要数字・publication情報 | PASS(719人、32.7歳、DOI、Vol.97 Issue 2、95%参加率、全て一致) |
| 一次Source到達 | PASS(pure.ed.ac.uk、academic.oup.comの論文本体レベルまで到達) |
| Association→Causation | PASS(CORRELATIONAL/CAUSAL_STATED_BY_SOURCEを正しく使い分け) |
| Unsupported claim | なし |
| Study limitation保持 | PASS(観察研究である旨、SES指標の限定性、国横断一般化の制約を保持) |
| Editorial usefulness | PASS、Solより情報量が多い |
| Source traceability | PASS |

**LunaのLedger品質はSol baselineと同等、一部(統計的精度)ではSolを上回っています。**

Fact数: 21件(Sol: 32件。ただしLunaは統計的詳細を1 factへ集約する傾向があり、単純な件数比較はミスリーディング)。

### Luna: Cost NOT_VIABLE — ただし単一要因(Search fee)で説明可能

| 内訳 | Research | Verification | 合計 |
|---|---|---|---|
| Token cost | $0.0227 | $0.0222 | $0.0449 |
| Search cost(web_search calls) | 6件 × $0.01 = $0.06 | 7件 × $0.01 = $0.07 | **$0.1300** |
| **合計** | $0.0827 | $0.0922 | **$0.1749** |

**Search feeが総コストの74%を占めています。** Lunaのtoken単価はSolの1/25ですが、`web_search`ツールの$10/1,000callsという固定手数料はモデルによらず同一のため、token費用がほぼゼロに近づいても、13回のsearch call分($0.13)が下限として残ります。これが$0.05を大きく超える唯一の要因です(token costのみなら$0.0449で$0.05以内)。

### Gemini 3.5 Flash-Lite: Quality FAIL — Groundingが実質発動していない

- Research呼び出しで`web_search_queries: []`、`grounding_chunks_count: 0`。**Google Search Groundingツールを与えたにもかかわらず、一度も検索を実行しませんでした。**
- 結果、得られたFactは3件のみで、その内容は**私が与えたResearch Brief(トピック説明文)の再言明**にとどまり、Brief記載内容を超える新規事実の発見・独立検証という、Researcherの本来の役割を果たせていません。
- Verification呼び出しも同様に`web_search_queries: []`で、Ledger自身のsource_urlを鵜呑みにせず独立検証するという要件(VERIFICATION_DEVELOPER_MESSAGE)を満たしていません。
- Quality Gate 8項目のうち、「Critical Facts」「一次Source到達(Brief記載のURL止まり)」「Editorial usefulness」が明確にFAILです。

**技術的な設定不備の可能性も検討しましたが**、Gemini 3.x系はgoogle_searchツールとresponse_schemaを同一requestで併用可能であることを公式ドキュメントで確認済みで、実際にAPI呼び出し自体は正常終了(200 OK、構造化JSON取得)しています。したがって今回の結果は、**モデルが「検索は不要」と判断した(または高詳細なBriefを十分な情報と誤認した)という、モデル自身の挙動**と評価しています。best-of禁止の原則により、re-generateはしていません。

**注意点(Limitation)**: 今回のBriefは、Sol/Luna/Gemini全モデルに同一の、かなり具体的な内容(DOI・人数・主要知見を含む)を与えています。Lunaは同じBriefからさらに13回の独立検索を行い新規事実を追加した一方、Geminiは検索ゼロでBriefをほぼそのまま返しました。したがってこれは「Briefが詳しすぎたから」ではなく、**同一条件下でのモデル間のtool-use積極性の違い**として評価しています。

---

## Fact / Issue 比較表(抜粋、Source-based assessment)

| Fact / Issue | Sol | Luna | Gemini | Source-based assessment |
|---|---|---|---|---|
| 719人・95%参加率・32.7歳 | あり | あり(一致) | あり(Brief由来) | Luna/Sol双方が独立に確認。Geminiは検証なし |
| 4群の人数内訳(stable-low 152人=22.9%等) | なし | **あり**(新規発見) | なし | Luna独自の付加価値。Solにない詳細 |
| 統計値(F値・p値・Cohen's d・95%CI) | なし | **あり**(新規発見) | なし | Luna独自の付加価値 |
| Caveat(観察研究、因果確立不可) | あり | あり(一致) | あり(Brief由来のみ、独自検証なし) | 3モデルとも表現は保持 |
| Unsupported claim | なし | なし | なし | 該当なし |
| Missing fact(SESの一般化制約) | あり(F29-30) | あり(F021、一致) | なし(触れられていない) | Geminiのみ欠落 |

---

## Cost比較(Production-equivalent、Search/Grounding分離)

| Model | Theme | LLM Token Cost | Search/Grounding Cost | Total Research Cost | vs Sol | Cost status |
|---|---|---|---|---|---|---|
| Sol | Parenting | (内訳未分離、既存合計のみ) | (内訳未分離) | $2.0938 | 1.0x | Baseline |
| Luna | Parenting | $0.0449 | $0.1300(13 calls) | **$0.1749** | 0.084x(8.4%) | `COST_NOT_VIABLE`(単一要因で説明可) |
| Gemini 3.5 Flash-Lite | Parenting | $0.0042 | $0.0000(0 requests、grounding未発動) | **$0.0042** | 0.002x(0.2%) | `GREEN`だが`QUALITY_FAIL`により不採用方向 |

---

## 最終Q&A

### Q1. Lunaは$0.03以下か？

**いいえ。** $0.1749で、$0.03の約5.8倍、$0.05の約3.5倍です。

### Q2. Geminiは$0.03以下か？

**はい。** $0.0042で$0.03を大きく下回りますが、Quality Failのため採用候補にはなりません。

### Q3. $0.05以内でSol相当のResearch品質に最も近いモデルはどれか？

**該当なしです。** Luna はSol相当以上の品質ですが$0.05以内に収まらず(税抜き$0.1749)、Geminiは$0.05以内ですがSol相当の品質に到達していません(実質未Research)。両立するモデルは今回確認できませんでした。

### Q4. どちらをAKB48 Phase 2へ進めるべきか？

**現時点ではどちらも自動的には進めません。** Geminiは品質Failのため、ご指示の`QUALITY_FAIL → そのモデルはそこで停止`により対象外です。Lunaは品質はPASSですがCostが`COST_NOT_VIABLE`域にあり、かつ「$0.05をわずかに超え、単一要因(Search回数)で説明できる場合は、勝手に続行せず一度報告する」というご指示に該当するため、ここで報告し、ご判断を仰ぎます。

### Q5. モデル置換だけでResearch Cost Targetへ届きそうか？

**Luna単体では届きません(単純なモデル置換では$0.05の壁をSearch feeが作っている)。** ただし、token costだけを見ればLunaは$0.0449と既に$0.05以内であり、**もしSearch call数を減らせれば(例: 現状13回→数回程度)、Luna単体でもCost Green圏内に入る可能性があります。** これは「モデル置換」の範囲内(Search回数の抑制はprompt/運用調整であり、Architecture変更ではない)で改善余地がある領域です。ただし今回は本タスクのスコープ(Research Architecture変更なし)を超えるため、実施していません。

---

## Luna Cost Not Viableへの対応について、ご判断をお願いします

以下のいずれかをお選びください(私の判断だけでは決めません):

1. **Search回数抑制の余地を検証してから再判断する**(prompt側でSearch回数に上限目安を与える等、Architecture変更なしでの調整。実施の可否はご判断次第です)
2. **Lunaを"$0.05を超えるが単一要因で説明可能"として許容し、AKB48 Phase 2へ進める**
3. **Lunaもここで保留とし、Sol以外の候補探索を一旦止める**(DeepSeekと同様、Search不要工程向けの候補として保持)

Geminiについては、Quality Failのためご指示通りPhase 2(AKB48)へは進めません。

---

## 付録

- Ledger全文: `er005_output/model_ab_01a/parenting/luna/ledger_draft_raw.json`、`ledger_verification_raw.json`(Luna)、`er005_output/model_ab_01a/parenting/gemini/`(Gemini)
- Raw usage log: `er005_output/model_ab_01a/raw_usage_log.jsonl`(1 call = 1 record、公式usage metadata)
- Pricing: Luna($0.20/$0.02cached/$1.20 per 1M + $10/1k web_search、2026-08-18公式確認)、Gemini 3.5 Flash-Lite($0.30/$2.50 per 1M + grounding 5,000/月無料、超過$14/1,000、2026-08-18公式確認)
- OPEN-43は本タスクと無関係のため、`UNDER_REVIEW`(原因未確定)のまま維持し、CLOSEDにしていません。
- Production model・CURRENT_SPEC・Research Architecture・Search provider構成・Article Writer・Fact Checker・TTS/ASRは一切変更していません。
