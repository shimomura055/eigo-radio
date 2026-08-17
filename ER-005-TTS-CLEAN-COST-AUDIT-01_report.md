# ER-005-TTS-CLEAN-COST-AUDIT-01 完了報告

**TTS Clean-run原価分解監査**
実施日: 2026-08-18
対象: ER-005-COST-BASELINE-01の既存ログ4番組(新規TTS生成なし、Production変更なし)

---

## A. Executive Summary

**1 Theme(A2+B1) Clean-run TTS Cost:**

| Theme | B1 Clean-run TTS | A2 Clean-run TTS | 1 Theme合計 |
|---|---|---|---|
| AKB48 | $0.133 | $0.197 | **$0.331** |
| Parenting | $0.170 | $0.204 | **$0.375** |
| **平均** | | | **約$0.35 / theme** |

- **Actual TTS Costの約55%(2テーマ加重平均)がretry/fallbackで捨てられている**($0.846 / $1.551)
- **Clean-run TTS Costの約94%が最終audio outputそのもの**(instruction inputは約6%のみ)
- **Segment統合(理論上の1 call化)による追加削減効果は、Clean-runからさらに約3.7%のみ**(ほぼ音声output量そのものが原価を決めているため)
- **結論(J節): `OPTIMIZE_RETRY_AND_PROMPTS_FIRST`** — TTS architecture(segment分割方式)の根本再設計は、コストの観点からは正当化されません。原価の大部分はretry/fallbackという運用上の問題であり、segment構造の問題ではありません。

## B. Actual vs Clean-run

| Program | Actual TTS Cost | Clean-run TTS Cost(推定) | Retry/Fallback Waste | Waste % |
|---|---|---|---|---|
| AKB48 B1 | $0.372 | $0.133 | $0.238 | **64.1%** |
| AKB48 A2 | $0.564 | $0.197 | $0.367 | **65.0%** |
| Parenting B1 | $0.357 | $0.170 | $0.187 | **52.4%** |
| Parenting A2 | $0.259 | $0.204 | $0.054 | **20.9%** |
| **4番組計** | **$1.551** | **$0.705** | **$0.846** | **54.5%** |

**Clean-run TTS Costの算出方法(重要な注記)**: raw_usage_log.jsonlにはsegment名が記録されておらず、segment側のattempts_logには公式token数が記録されていない(逆方向の欠落)。そのため、各attemptの実測音声長(trim_info.raw_duration_secondsまたはduration_seconds)を使い、そのstageの実測output cost合計を実測音声長合計で割った「$/秒」単価で各attemptのoutput costを推定し、input costはcall数按分とした。推定合計は実測Actual Total(公式usage metadata由来、完全に正確)へ正規化してスケーリングしている(正規化係数は1.01〜1.02倍、モデルの当てはまりが良いことを示す)。**Clean-run/segment別/原因別の内訳はESTIMATEDであり、Actual TTS Cost自体は公式usage metadataそのもの(厳密値)。**

## C. Segment / Call Structure

| Program | 必要segment数(Clean-run必要call数) | Actual Gemini Calls | Call Amplification |
|---|---|---|---|
| AKB48 B1 | 23 | 95 | **4.13x** |
| AKB48 A2 | 24 | 182 | **7.58x** |
| Parenting B1 | 23 | 67 | **2.91x** |
| Parenting A2 | 24 | 69 | **2.88x** |

Segment内訳(共通): topic_intro、[japanese_title(A2のみ)]、preview、comment_1〜4、point_one_heading、point_two_heading、full_story_part1〜2、point_one、point_two、in_one_line、Key Phrase EN×5、Key Phrase JA×5。

**不足項目として報告**: segment attempts_log(JSONログ)の論理attempt数合計(78/165/58/63)は、raw_usage_log.jsonlの実測Gemini call数(95/182/67/69)より少なく、差分(17/17/9/6)が存在する。原因は`common._call_tts_with_retry`という、より低レベルの技術的retry層(タイムアウト等の一時的エラーに対する自動再試行)がsegment側のattempts_logには反映されないためと判明した(監査中に発見、Production側の挙動そのものであり今回変更していない)。この差分はraw_usage_log側の実測Actual Costにはすでに含まれているため、Actual Cost自体は正確である。

## D. Necessary Audio vs Instruction Overhead

| Program | Output(audio) Cost % | Input(instruction+text) Cost % |
|---|---|---|
| AKB48 B1 | 93.5% | 6.5% |
| AKB48 A2 | 93.8% | 6.2% |
| Parenting B1 | 95.4% | 4.6% |
| Parenting A2 | 93.1% | 6.9% |

**audio outputが90%以上を占めており、segment統合だけでは大幅削減しない**という仮説(section 12)が実測で確認されました。

## E. Retry/Fallback Waste(Segment Type別)

| Segment Type | AKB48 B1 Retry Cost | AKB48 A2 Retry Cost | Parenting B1 Retry Cost | Parenting A2 Retry Cost |
|---|---|---|---|---|
| Key Phrase EN | $0.024 | $0.062 | $0.017 | $0.020 |
| Key Phrase JA | $0.000 | **$0.181** | **$0.155** | $0.003 |
| Heading | $0.001 | $0.006 | $0.000 | $0.031 |
| Full Story | $0.097 | $0.000 | $0.000 | $0.000 |
| Point Content | $0.030 | $0.084 | $0.000 | $0.000 |
| Preview | $0.027 | $0.032 | $0.000 | $0.000 |
| Comment | $0.012 | $0.000 | $0.015 | $0.000 |
| In One Line | $0.046 | $0.001 | $0.000 | $0.000 |

**Key Phrase JAが、AKB48 A2とParenting B1の2番組で突出したCost Wasteを生んでいます**(それぞれ$0.181、$0.155)。原因はF節参照。

## F. Failure Cause Breakdown

3種類の失敗原因を、各attemptのasr_text/statusフィールドから機械的に分類しました(推測ではなく、ログに記録された実データに基づく分類)。

| 原因区分 | 判定基準 | AKB48 B1 | AKB48 A2 | Parenting B1 | Parenting A2 |
|---|---|---|---|---|---|
| CONTENT_MISMATCH | ASR文字起こしが非空だが期待文字列と不一致(発音・聞き取りの実質的な齟齬) | 50件 $0.216 | 21件 $0.100 | 29件 $0.175 | 36件 $0.051 |
| ASR_EMPTY_RESPONSE | ASR文字起こしが空文字列(TTS自体は成功しているが検証不能) | 0件 | **119件 $0.243** | 1件 $0.002 | 0件 |
| TTS_API_ERROR | TTS呼び出し自体がエラー終了(タイムアウト・5xx等) | 10件 $0.001 | 13件 $0.001 | 7件 $0.001 | 5件 $0.001 |

**具体例(CONTENT_MISMATCHの内訳、代表例)**:
- **homophone(sole/soul)**: AKB48記事全体が"sole center"という語を核とするため、"sole"を"soul"とTTSが発音・ASRが認識する現象が複数segmentに波及(point_one_heading、Key Phrase 1、full_story_part1等)
- **heading misread**: Parenting A2の"Point One:"/"Point Two:"という見出し表記を、TTSが".1"/".2"と読み上げる(2見出しとも12回全滅)

**AKB48 A2のASR_EMPTY_RESPONSE(119件、$0.243)は、この監査で新たに発見した重大な事実です。** 全10個のKey Phrase音声(英語5+日本語5)が、標準経路(6回)・fallback経路(6回)とも全滅し、しかも全attemptのasr_textが例外なく空文字列でした。これは「TTSの発音が違う」のではなく「ASRが何も聞き取れなかったと報告している」現象で、ER-005-COST-BASELINE-01で確認したAzureクォータ枯渇時と同一の症状です。ただし、AKB48全体のTTS/ASR実行はAzureクォータ枯渇が発生する前(タイムスタンプ上、Parentingの1回目runより前)に完了しており、クォータ枯渇そのものが原因とは断定できません。**Key Phraseのような非常に短い音声(1〜2秒)に対するAzureリアルタイムASRの信頼性問題である可能性が高いですが、既存ログにはAzure側の詳細なエラーコードが記録されておらず、確定的な原因特定はできませんでした(不足項目として報告)。**

## G. Theoretical Consolidated-call Lower Bound

Voice分離・A2/B1言語配分・segment単位のretryメリット・音声品質制御を無視し、instruction入力の重複だけをゼロ化した場合の理論下限です(実装はしません)。

| Program | Clean-run Cost | Theoretical Consolidated Cost | 追加削減額 | 追加削減率 |
|---|---|---|---|---|
| AKB48 B1 | $0.133 | $0.126 | $0.007 | 5.2% |
| AKB48 A2 | $0.197 | $0.192 | $0.005 | 2.6% |
| Parenting B1 | $0.170 | $0.164 | $0.006 | 3.7% |
| Parenting A2 | $0.204 | $0.198 | $0.006 | 3.2% |

**Segment構造そのものを理論的に最小化しても、Clean-runからさらに削減できるのは3〜5%程度に留まります。** 原価の94%を占めるaudio output量は、segment分割の有無によらずほぼ変わらないためです。

## H. Latency Impact

| Program | TTS Actual Elapsed | TTS Clean-run推定 | ASR Actual Elapsed | ASR Clean-run推定 |
|---|---|---|---|---|
| AKB48 B1 | 45.0分(95 calls) | 約10.9分 | 4.6分 | 約1.6分 |
| AKB48 A2 | 40.5分(182 calls) | 約5.3分 | 24.1分 | 約3.8分 |
| Parenting B1 | 32.1分(67 calls) | 約11.0分 | 4.6分 | 約2.1分 |
| Parenting A2 | 23.5分(69 calls) | 約8.2分 | 2.9分 | 約1.2分 |

AKB48のTTS/ASR合計は約49〜65分(元報告書G節)でしたが、**retryがなければTTS+ASRは合計で12〜20分程度に収まっていた**と推定されます(call数比例のシンプルな推定であり、ESTIMATEDです)。

## I. TTS vs ASR Responsibility

| 原因区分 | 責任の所在 | 該当件数(4番組合計) |
|---|---|---|
| CONTENT_MISMATCH(homophone等) | TTS発音とASR聞き取りの両方が同じ「もっともらしい別の語」に収束する現象。TTS単独の問題ともASR単独の問題とも言い切れない(**cannot distinguish**、ただし「発音自体は自然な英語として成立しており、期待文字列側の語選択に無理がある」ケースが多い= "sole"や"Point One:"のような、TTSが自然に別の読みへ寄せやすい語) | 136件 |
| ASR_EMPTY_RESPONSE | ASR側の技術的な問題(短い音声に対する認識信頼性、またはクォータ/レート制限系)の可能性が高いが、既存ログでは確定できない | 120件 |
| TTS_API_ERROR | 明確にTTS呼び出し自体の失敗(タイムアウト・5xx) | 35件 |

**Q17への回答**: homophone系(sole/soul)とheading misread系(Point One:→.1)は、TTS側の発音選択とASR側の聞き取りの両方が絡む複合現象であり、厳密に分離はできません。一方、ASR_EMPTY_RESPONSE(120件)は、TTS音声自体は生成されている(output tokenが計測されている)ため、**ASR側(または短い音声に対するリアルタイム認識の限界)に起因する可能性が高い**と判断します。

## J. Recommendation

### Decision指標(Q1〜Q7)

| Q | 回答 |
|---|---|
| Q1: Actual TTS Costの何%がretry/fallbackで捨てられているか | **54.5%**(4番組加重平均、範囲20.9%〜65.0%) |
| Q2: Clean-run TTS Costの何%が最終audio outputそのものか | **約94%**(93.1〜95.4%) |
| Q3: Clean-run TTS Costの何%がrepeated instruction inputか | **約6%**(4.6〜6.9%) |
| Q4: 現行segment方式のままretryをほぼゼロにした場合、1テーマ(A2+B1)のTTSはいくらか | **約$0.35/theme** |
| Q5: segment構造を理論的に最小化した場合の追加削減額 | Clean-runからさらに**3〜5%**(4番組合計で約$0.024、ほぼ無視できる規模) |
| Q6: TTS Costを1/10へ下げるには、retry削減だけで達成可能か | **不可能**。Clean-run Total($0.705)はActual Total($1.551)の45.5%に過ぎず、retryを完全にゼロにしても現状の半分弱までしか下がらない。1/10まで下げるには、TTSモデル/voiceのグレードダウン等、retry削減以外の手段が別途必要 |
| Q7: Costだけを見るとTTS architectureの根本再設計が必要か | **NO** |

**Q7の根拠**: 原価の54.5%はretry/fallbackという運用上の無駄であり、これは既存のTTS/ASR検証ロジック・prompt設計の改善(例: homophone対策の語選択見直し、"Point One:"見出し表記の読み上げ対策、AKB48 A2のASR_EMPTY_RESPONSE原因調査)で対応できる可能性が高い問題です。一方、segment構造そのものを理論的に最小化しても追加で3〜5%しか削減できず(G節)、原価の94%を占めるaudio output量はsegment分割方式によらずほぼ一定です(D節)。したがって、**TTS architecture(segment分割方式)自体を再設計する経済的な根拠はありません**。

### 推奨: `OPTIMIZE_RETRY_AND_PROMPTS_FIRST`

優先順位:
1. **AKB48 A2のASR_EMPTY_RESPONSE(119件、$0.243、単一原因としては最大)の根本原因調査**(Key Phraseのような短い音声特有の問題か、Azure側の問題か)
2. **homophone/heading-misread系のprompt・語選択レベルでの対策検討**("sole"の代替表現、"Point One:"見出しの読み上げ対策)
3. 上記が難しい場合のみ、segment統合を検討(ただし期待削減効果は3〜5%と小さい)

---

## 付録: 手法・限界

- 新規TTS生成・ASR呼び出しは一切行っていません。既存の`raw_usage_log.jsonl`・`pricing_snapshot.json`・各番組の`tts_generation_results.json`・article/parts.jsonのみを再集計しました。
- Production側のコード(TTSモデル・ASR・retry上限・segment統合・prompt・validation)は一切変更していません。CURRENT_SPEC.mdも変更していません。
- Segment単位のClean-run/Waste/原因別コストはESTIMATED(音声長按分による推定)です。Actual TTS Cost自体(Program合計)は公式usage metadataに基づく厳密値です。
- ASR_EMPTY_RESPONSEの真因(Azure側かASRの短音声限界か)は既存ログからは確定できず、不足項目として報告しています。
