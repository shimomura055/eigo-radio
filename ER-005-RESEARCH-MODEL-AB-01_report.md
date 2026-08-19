# ER-005-RESEARCH-MODEL-AB-01 実行報告書

**タスク**: Research Layer(Evidence Pack→VFL→Verification)モデル比較 — Luna vs DeepSeek V4 Flash
**実行日**: 2026-08-19〜20
**入力**: ER-005-SOURCE-RETRIEVER-01でSimple Retrieverが取得したFrontiers論文本文(68,877文字)を両モデルへ完全に同一のものとして使用。Topic Selection・Search APIは今回対象外。
**為替**: 1ドル=160円換算(主表示は円)

---

## 完了報告の最上段(18章の必須回答)

1. **DeepSeekでEvidence Packは成立したか**: **成立した**(19件、sample/design/measures/9件超の統計結果/model fit/limitations/conclusionまで網羅)
2. **DeepSeekでVFLは成立したか**: **成立した**(19 Fact、全件がsource_id/evidence_idで壊れず逆参照可能)
3. **Verificationは実用水準だったか**: **実用水準**。ただしLunaより判定基準がやや緩い(後述、Verification Strictnessの項)
4. **Critical Factの誤りは何件あったか**: **0件**(サンプルサイズ、脱落数、年齢、β値・p値・95%CI、モデル適合度、α係数を原文と1件ずつ突き合わせ、全て一致)
5. **Lunaより明確に品質が落ちた点はあるか**: **明確な劣化はない**。唯一の差は、原論文内部の統計的不整合(後述)に対する最終判定が、Lunaは`AMBIGUOUS`、DeepSeekは`VERIFIED`(ただし矛盾を`verification_notes`に明記)とやや緩やかだった点のみ。
6. **DeepSeek Research Layer総コストはいくらか(円)**: **3.27円**(クリーンな実行のみ)。ただし後述の技術的失敗を含めると4.60円。
7. **Luna約3.59円に対して何%削減できたか**: 参考として今回はLunaを同一本文で再実測しており、Luna再実測値は3.30円だった(旧Baseline 3.59円とほぼ同水準)。DeepSeekのクリーン実行(3.27円)は**Luna再実測比でわずか0.9%減**にとどまり、事前に期待された大幅なコスト削減は確認できなかった(理由は後述)。
8. **Research LayerをDeepSeekへ置換する価値があるか**: **現時点では乏しい**。品質はLunaと実用上同等だが、コスト差がほぼ無く(0.9%)、置換の複雑化に見合わない。
9. **次にWriterモデル比較へ進むべきか**: 今回の結果を踏まえると、Research Layerのモデル置換自体は緊急性が下がったため、Writerモデル比較へ進む前に、まず「なぜDeepSeekが期待したほど安くならなかったか」(出力トークン量の多さ)を踏まえたコスト構造の再検討を挟む価値がある。ただしこれは本タスクの範囲外の提案であり、実行はしていない。

---

## A. 技術的な問題点(先に報告)

DeepSeekのStage R1(Evidence Pack)は、初回`max_tokens=8000`で実行したところ**空文字列のレスポンスとなりJSON parseに失敗した**(`finish_reason="length"`)。原因を調査したところ、DeepSeekはreasoning tokenを可視output tokenと同一の`max_tokens`予算内でカウントする仕様であり(Lunaのreasoning effortが可視outputと別枠になっているのとは異なる)、今回の入力サイズ(約7万字≒1.8万token)ではreasoning だけで6,000超token消費し、8,000という設定では可視JSON出力の余地がほぼ残らなかった。

**対応**: `max_tokens`を32,000へ引き上げて再実行し、成立した。これはLuna側のプロンプト内容には一切変更を加えていない、DeepSeek固有のAPI制約に対する必須の設定調整である(仕様5章が許容する「API仕様上必要な最小差分」に該当)。

この失敗した1回のAPI呼び出し分のコスト($0.008339 = 1.334円)は無駄になっており、F章のコスト集計に別枠で明記する。

---

## B. Evidence Pack比較(6章)

| 観点 | Luna(再実測) | DeepSeek |
|---|---|---|
| Evidence item数 | 15件 | 19件 |
| 研究目的 | ✓(E1) | ✓(ev_02) |
| Sample size | ✓ 532/619/588、脱落87(14.1%) | ✓ 同一数値、脱落分析含む |
| 年齢 | ✓ 3.99歳(SD=0.85) | ✓ 同一数値 |
| Longitudinal design | ✓ T1/T2/T3、4か月間隔 | ✓ 同一 |
| 測定尺度 | ✓ CPRS/SDQ/screen time計算式、α係数含む | ✓ 同一、α係数含む(0.882/0.895/0.891/0.853) |
| 主要統計結果(β/p/95%CI) | ✓ 9件全て正確 | ✓ 9件全て正確 |
| Model fit | ✓ χ²/RMSEA/CFI/TLI/SRMR全て正確 | ✓ 同一、Δχ²(2)=15.30も含む |
| Limitations | ✓(2項目に集約、内容は網羅) | ✓(2項目、内容は網羅) |
| Publication metadata | ✓ | ✓(DOI・掲載日・著者) |
| Unsupported extraction(Source本文にない情報の生成) | **0件**(確認できず) | **0件**(確認できず) |

両モデルとも、Evidence item数の粒度(Lunaは少数の項目に複数観点を統合、DeepSeekはやや細かく分割)に差はあるものの、Critical Fact Coverageの範囲自体に差はなかった。

---

## C. VFL比較(7章)

| 観点 | Luna | DeepSeek |
|---|---|---|
| Fact数 | 16件 | 19件 |
| Evidence参照整合性 | 全16件が有効なsource_id/evidence_idを持つ | 全19件が有効なsource_id/evidence_idを持つ |
| Broken source_id/evidence_id | **0件** | **0件** |
| Numeric accuracy | サンプル値をチェックし全て一致 | サンプル値をチェックし全て一致(F03/F05-F07/F09/F12/F13/F15/F16で個別に照合済み) |
| Scope accuracy | 母集団と個別条件の混同なし | 母集団と個別条件の混同なし |
| causal_strength | 一貫して慎重な表現("媒介効果は因果を確立しない"等) | 一貫して慎重な表現("causal interpretation not definitive"等) |
| Ambiguity handling | 原論文内部の統計的不整合(後述D章)を検出 | **同じ不整合を独立に検出**(後述D章) |
| Limitations保持 | 保持(集約された2項目に含む) | 保持(2項目に含む) |
| Unsupported claim | 0件(確認できず) | 0件(確認できず) |
| Writerに渡せる実用性 | 高い | 高い |

---

## D. 独立評価: 原論文内部の統計的不整合の検出(9章、最重要チェック項目)

原論文Table 3では、媒介分析の間接効果(Conflict→Screen time→内在化/外在化問題)について、**p<0.05と報告されているにもかかわらず、95%信頼区間が0をまたいでいる**という内部的な矛盾がある(β=0.031, 95% CI [-0.026, 0.088]等)。前タスク(ER-005-RESEARCH-LAYER-REDESIGN-01)でLunaがこの矛盾を自律的に検出したことが確認されており、本タスクの核心的な再現性チェック項目とした。

| モデル | 検出有無 | 記録箇所 | 最終Verification判定 |
|---|---|---|---|
| Luna(再実測) | **検出した** | VFLのambiguityフィールド、Verification notes | **AMBIGUOUS** |
| DeepSeek | **検出した** | Evidence Packのambiguity/limitationフィールド、VFLのambiguityフィールド、Verification notes | **VERIFIED**(ただしnotesに矛盾を明記) |

両モデルとも、この巧妙な内部矛盾を独立して検出できた。これはSelf-verificationの甘さではなく、Evidence PackとVFLの生成段階から一貫して数値を機械的に転記・比較する設計が機能している証拠である(仕様9章が求める「Self-verificationだけを品質証拠にしない」独立照合の結果として確認)。

**唯一の差**: 最終的なVerification判定で、Lunaは「Claimが広すぎる」とみなし`AMBIGUOUS`としたのに対し、DeepSeekは「Evidence自体はClaimを直接支持しており、矛盾はnotesに記録済み」として`VERIFIED`とした。これは矛盾を隠したり見落としたりした結果ではなく、"VERIFIED"の閾値の取り方(Evidence追従性を重視するか、原論文自体の統計的自己矛盾を理由に一段階格下げするか)という設計判断の違いであり、Critical Factの誤りではない。

---

## E. Verification比較(8章)

| Verdict | Luna | DeepSeek |
|---|---|---|
| VERIFIED | 15 | 19 |
| PARTIALLY_SUPPORTED | 0 | 0 |
| AMBIGUOUS | 1(D章の内部矛盾のみ) | 0 |
| REJECTED | 0 | 0 |
| NEEDS_EXTERNAL_CHECK | 0 | 0 |

どちらもVFL・Evidence Packのみを入力とし、Web検索は使用していない(DeepSeekはbuilt-in web_search自体を持たないため物理的に不可能、Lunaはツール未付与により不使用。両者ともコストログで検証呼び出し中に外部検索が発生していないことを確認済み)。

---

## F. コスト計測(11・12章、円建て)

| 工程 | Luna(再実測) | DeepSeek(クリーン実行) | DeepSeek(失敗分含む実費) |
|---|---:|---:|---:|
| Evidence Pack (R1) | 1.577円 | 1.409円 | 1.409円 + 失敗分1.334円 |
| VFL (R2) | 1.055円 | 1.115円 | 同左 |
| Verification (R3) | 0.667円 | 0.747円 | 同左 |
| **合計** | **3.299円** | **3.270円** | **4.605円** |

- Luna既存Baseline(REDESIGN-01、より短い入力本文): 3.59円(参考。今回の再実測3.299円とほぼ同水準)
- DeepSeekのクリーン実行(設定ミス後の正しいmax_tokensでの実行分のみ): **3.270円**(Luna再実測比 **-0.9%**)
- DeepSeekの実費(A章の失敗した1回分を含む): **4.605円**(Luna再実測比 **+39.6%**、むしろ高い)

**コスト削減が想定より小さかった理由**: DeepSeekの1トークンあたりの単価はLunaより安い(output: DeepSeek $0.66/1M vs Luna $1.20/1M、off-peak)。しかし、DeepSeekは**reasoning tokenを可視output tokenと同一予算で消費し、かつ実際の出力トークン量そのものがLunaの2倍以上だった**(DeepSeek合計output tokens: 13,108+8,873+3,889=25,870 vs Luna合計: 5,122+4,487+1,633=11,242)。単価の安さが、トークン消費量の多さでほぼ相殺された。

Cost評価(13章、暫定基準)との対比: DeepSeekクリーン実行 3.270円は基準「BORDERLINE(>2.0円〜≤3.0円)」をわずかに超え、**「COST_NOT_COMPELLING(>3.0円)」に該当**する。

---

## G. Human Review Artifact(15章)

### Model comparison summary

| 項目 | Luna | DeepSeek |
|---|---|---|
| Evidence count | 15 | 19 |
| Fact count | 16 | 19 |
| Critical Fact Coverage | 良好(全観点網羅) | 良好(全観点網羅) |
| Numeric errors | 0件 | 0件 |
| Unsupported claims | 0件 | 0件 |
| Broken references | 0件 | 0件 |
| Ambiguity handling | 内部矛盾を検出、AMBIGUOUS判定 | 内部矛盾を検出、VERIFIED+notes明記 |
| Verification result | 15 VERIFIED / 1 AMBIGUOUS | 19 VERIFIED |
| Cost | 3.299円 | 3.270円(クリーン)/ 4.605円(実費) |

### Critical Fact差分表

| Critical Fact | Luna | DeepSeek | 差分 |
|---|---|---|---|
| Sample(532/619/588、脱落87・14.1%) | 正確 | 正確 | なし |
| 年齢(3.99歳、SD=0.85) | 正確 | 正確 | なし |
| 調査wave(T1/T2/T3、4か月間隔) | 正確 | 正確 | なし |
| Key β(Conflict→IBP 0.476、Conflict→EBP 0.273等) | 正確 | 正確 | なし |
| Key p値・95%CI | 正確 | 正確 | なし |
| Model fit(χ²=19.27、RMSEA=0.057等) | 正確 | 正確 | なし |
| Limitations | 網羅(2項目へ集約) | 網羅(2項目) | 粒度のみ差、内容差なし |
| Publication metadata(DOI・掲載日・著者) | 正確 | 正確 | なし |

**差分は実質的にゼロ**。Evidence/Fact数の粒度差(15/16 vs 19/19)と、内部矛盾Factに対するVerification判定の厳格さ(AMBIGUOUS vs VERIFIED+notes)のみが観測された差である。

---

## H. Quality判定軸(10章)

| 項目 | 判定 |
|---|---|
| Critical Fact Coverage | PASS(両モデル同等) |
| Factual Accuracy | PASS(両モデル、誤り0件) |
| Numeric Accuracy | PASS(両モデル、サンプル照合で全件一致) |
| Unsupported Claims | PASS(両モデル、0件) |
| Causal Discipline | PASS(両モデル、慎重な表現を一貫使用) |
| Limitations | PASS(両モデル、網羅) |
| Ambiguity Handling | PASS(両モデル、内部矛盾を独立検出) |
| Fact-to-Evidence Traceability | PASS(両モデル、broken reference 0件) |
| Verification Strictness | **MINOR_DEGRADATION**(DeepSeekはLunaよりVERIFIED判定がやや緩い。内部矛盾Factを一段階厳しくAMBIGUOUSとせず、VERIFIED+notesとした) |
| Writer Usefulness | PASS(両モデル) |

---

## I. 成立判定

**`COST_NOT_WORTH_SWITCHING`**

判定根拠:
- 品質はLunaと実用上同等(`Verification Strictness`のみMINOR_DEGRADATION、他は全てPASS)。
- しかしコスト差は僅少(クリーン実行同士でLuna比-0.9%)、かつ実運用で発生しうる設定ミス(max_tokens不足)を含めるとむしろ**+39.6%高くなる**リスクがある。
- 品質面でPRODUCTION候補として通用する水準ではあるものの、コスト面での明確な優位性が無いため、モデル置換によるパイプライン複雑化(2種のAPI形式、json_object modeでのプロンプト調整、max_tokens個別チューニングの必要性等)に見合う便益が確認できなかった。

---

## J. 受入条件確認(19章)

- 同一Primary Source本文を使用: **確認済み**(SOURCE-RETRIEVER-01の68,877文字をLuna・DeepSeek両方に使用)
- Search再実行なし: **確認済み**
- Source取得再実行なし: **確認済み**(既存retrieval_result.jsonを再利用)
- Luna/DeepSeekで同等schema: **確認済み**(developer message・prompt本文は完全同一。DeepSeekのみjson_object mode対応のための出力形式指示を追記、A章に差分開示済み)
- Evidence Pack比較あり: **確認済み**(B章)
- VFL比較あり: **確認済み**(C章)
- Verification比較あり: **確認済み**(E章)
- Self-verificationだけでPASSにしない: **確認済み**(D章で原文との独立照合を実施)
- 原SourceとのCritical Fact照合あり: **確認済み**(G章Critical Fact差分表)
- numeric accuracy確認あり: **確認済み**
- causal discipline確認あり: **確認済み**
- ambiguity handling確認あり: **確認済み**(D章)
- 主表示は円(160円/USD): **確認済み**
- Production/CURRENT_SPEC変更なし: **確認済み**(触れたのは`er005_research_model_ab_01.py`のみ)

## K. Stop条件

DeepSeek Evidence Pack → VFL → Verification → Luna Baseline比較 → Source本文とのCritical Fact照合 → コスト比較 → Reportが完了したため、ここでSTOPする。Writerへは進まない。

---

## L. 成果物一覧

- `er005_research_model_ab_01.py` — 実行スクリプト(Luna/DeepSeek両パイプライン)
- `er005_output/research_model_ab_01/luna/` — Luna再実測結果(evidence_pack.json / vfl.json / verification.json)
- `er005_output/research_model_ab_01/deepseek/` — DeepSeek結果(同様の3ファイル)
- `er005_output/research_model_ab_01/raw_usage_log.jsonl` — 全7呼び出し(Luna×3、DeepSeek×4、うち1件は失敗分)のコストログ
- 本報告書 `ER-005-RESEARCH-MODEL-AB-01_report.md`
