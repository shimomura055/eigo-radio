# ER-006-COST-WASTE-RCA-RESEARCH-COVERAGE-GATE-01 完了報告

**管理ID: ER-006-COST-WASTE-RCA-RESEARCH-COVERAGE-GATE-01**
**日付: 2026-08-23**

No.4〜6のProduction実績を使い、(1)Clean/Additional原価分解、
(2)No.4のResearch/Writer高コストRCA、(3)Research Coverage Gateの
小規模Backtest検証、(4)No.6のTTS高騰RCA、を実施した。

---

## 1. 何が問題だったか
これまでの原価報告は「実際にいくらかかったか」の合計値だけで、
「初回で成功していれば本来いくらで済んだか」と「やり直し・追加調査で
無駄になった分」が区別されていませんでした。特にNo.4は情報源不足に
起因する複数回のやり直しでコストが膨らみましたが、その原因を1件ずつ
掘り下げて確認したことはありませんでした。また、No.6だけ音声生成の
Batch呼び出し回数が突出して多かった理由も、まだ特定されていません
でした。

## 2. 何を変更したか
- 既存ログ・監査ファイルのみを使い、3記事それぞれのコストを
  「初回で成功していれば必要だった費用(Clean)」と「やり直し等の
  追加費用(Additional)」に分解しました
- No.4で実際に見つかった3件の重大な内容不一致(MAJOR Ledger
  Deviation)を1件ずつ調査し、原因を特定しました
- 「記事を書き始める前に、情報源が十分かどうかを自動チェックする
  仕組み(Research Coverage Gate)」を試作し、No.4〜6の実データに
  対して過去を遡ってテスト(Backtest)しました(新規記事生成は一切
  行っていません)
- No.6だけ音声生成が多かった理由を、区間ごとに分解して特定しました

## 3. 何が改善されるか
- 「今回の3記事の実際の原価はいくらで、そのうちどれだけが無駄
  だったか」が明確になりました(下記4節)
- Research Coverage Gateは、1記事あたり約¥0.31という極めて低コストで、
  No.4型の失敗パターンを的確に予測できることを確認しました。ただし
  3記事中1記事で「過剰に厳しすぎる」誤判定も出ており、本番導入には
  まだ調整が必要です
- No.6の音声コスト高騰は、特定の2つの固有名詞・数式表記の問題に
  起因することが判明し、次回以降の改善余地が明確になりました

## 4. リスク・注意点
- 今回の判断材料は3記事のみです。統計的に一般化できる結論ではなく、
  次の一歩(採用/見送り)を判断するための材料として提示します
- Research Coverage Gate・原価分解の手法とも、本番コードへの変更は
  一切行っていません(検証用スクリプトのみ作成)
- 新規API支出は約¥1(Gate検証3回+No.4の当時状態再構築3回)のみです

---

## Part A: No.4〜6 Actual Clean / Additional Cost

### A-1. Topic別サマリー

| Topic | Clean | Additional | Actual Total | Additional率 |
|---|---|---|---|---|
| No.4 Supermarket | ¥69.0 | ¥74.5 | ¥143.5 | 51.9% |
| No.5 Cafes | ¥74.2 | ¥21.3 | ¥95.6 | 22.3% |
| No.6 Delivery | ¥71.9 | ¥45.5 | ¥117.4 | 38.8% |
| **3 Topic平均** | **¥71.7** | **¥47.1** | **¥118.8** | **39.7%** |

参考: 既存Clean Production baseline(¥65.14)・Expected Production
baseline(¥111.17)とは近い水準になった(今回の3 Topic平均Clean=¥71.7、
平均Total=¥118.8)。これは既存baselineの妥当性を裏付ける一方、
**今回のActual実測値としては別数値として扱う**(既存baselineを
書き換えない)。

### A-2. Stage別 Clean / Additional

| Stage | No.4 Clean/Add | No.5 Clean/Add | No.6 Clean/Add |
|---|---|---|---|
| Research+Writer/QA+Support/KP(Luna) | ¥19.9 / ¥53.6 | ¥21.5 / ¥0.0 | ¥18.4 / ¥0.0 |
| TTS(Gemini Batch) | ¥38.3 / ¥16.3 | ¥44.6 / ¥18.0 | ¥45.9 / ¥39.1 |
| ASR(English OpenAI + Japanese Azure) | ¥10.8 / ¥4.6 | ¥8.2 / ¥3.3 | ¥7.6 / ¥6.4 |

### A-3. 算出方法(方法論の明記)

- **Research+Writer+Support**: No.5・No.6は1回のResearch/Writer/
  Supportで収束した実績があるため、その実費(平均¥19.9)を「クリーンな
  1回成功時のコスト」の代表値(ベンチマーク)として採用した。No.4は
  実際に4回のResearch/Writer反復が必要だったため、実費(¥73.5)から
  このベンチマークを差し引いた額をAdditionalとした
- **TTS/ASR**: 各segment(B1/A2合わせて47 unit、Key Phrase英日含む)に
  ついて、`tts_generation_results.json`の`attempts_log`
  (+`fallback_attempts_log`)の長さを実際にカウントし、「1回で
  成功していれば必要だった1 attempt」をClean、2回目以降の全attemptを
  Additionalとして按分した(単価は各TopicのBatch/ASR実費÷実際の
  attempt数から算出)

---

## Part B: No.4 Ledger Deviation MAJOR 3件のRCA

初回Research(SRC-001 Vogel et al. 2021のみ+SRC-002 Mantratzis et al.
2023のみ、情報源2件)で生成したB1B記事に対し、Ledger Deviation Check
が検出した3件のMAJOR。

### MAJOR-1

- **Writerが生成したclaim**: "Why Shelves Keep Moving"というタイトル
  文脈で、棚が繰り返し・日常的に動かされることを前提とした記述
- **初回Ledgerに存在していたEvidence**: 英国6店舗での健康的レイアウト
  への**単発の**介入研究(Vogel 2021)、店舗環境と感情反応・衝動買いの
  関連を扱った一般的な研究(Mantratzis 2023)のみ
- **何が不足していたか**: 「棚が実際に定期的・反復的に動かされている
  こと」「その頻度や典型的なタイミング」を直接示すEvidenceが皆無
- **なぜMAJORか**: タイトルの中心的な前提(継続性)がLedgerで裏付け
  られておらず、記事の存立基盤に関わるため
- **追加Researchで取得したSource**: Edirisinghe and Munson(2022年、
  Expert Systems with Applications誌、店舗全体の棚配置を定期的に
  データ駆動で再配置する手法の提案)、The Global Display Solution
  (2025年、業界誌、食料品店が新奇性・衝動買い・動線改善・季節
  プロモーションのために継続的にレイアウトを見直しているという一般的
  説明)
- **解消方法**: 上記2件を追加し、「棚替えが実務として行われている」
  という一般的な裏付けと、「データ駆動での定期的な再配置」という
  具体的な仕組みの両方をLedgerへ組み込んだ
- **原因分類**: **`RESEARCH_COVERAGE_INSUFFICIENT`**
- **追加発生したAPI call**: Research(evidence_pack/vfl/verification)
  2ラウンド分、Writer(B1B/A2)2ラウンド分
- **Additional Cost寄与**: 後述Part Aの¥53.6のうち、このMAJORの解消に
  紐づく分が大部分(3件のMAJORは同じ情報源不足に起因するため、個別に
  金額を切り分けることはできない。3件合計での寄与として扱う)

### MAJOR-2

- **Writerが生成したclaim**: 健康的レイアウト(Vogel研究)が衝動買いを
  誘導する例としても機能するかのような記述、または両研究(Vogel・
  Mantratzis)を同一の棚変更の効果として結びつける記述
- **初回Ledgerに存在していたEvidence**: Vogel研究(健康的レイアウトの
  効果)とMantratzis研究(店舗環境と衝動買いの関連)は、**別々の店舗・
  別々の研究デザイン**であり、両者を結ぶEvidenceはない
- **何が不足していたか**: 「健康的レイアウトの変更それ自体が衝動買い
  を誘導する」ことを直接示すEvidence、または両研究を同一文脈で扱って
  よいとする根拠
- **なぜMAJORか**: 異なる研究の知見を、あたかも同一現象の両面である
  かのように統合する記述は、Ledgerの範囲を明確に超えるため
- **追加Researchで取得したSource**: Edirisinghe and Munson(2022年)
  ―― 棚配置換えの明示的な目的が衝動買いの最大化であることを直接
  報告する研究
- **解消方法**: 「健康的配置」と「衝動買い誘導」を、それぞれ独立した
  Evidence(Vogel=健康、Edirisinghe=衝動買い)に基づく別々の側面として
  記述し直せるようにした
- **原因分類**: **`BOTH`**(情報源不足に加え、Writerが手元のEvidenceを
  過度に統合して解釈した点でWriter側の要因もある)
- **追加発生したAPI call**: MAJOR-1と共通(同一Research/Writerラウンド)

### MAJOR-3

- **Writerが生成したclaim**: 「棚移動は健康的選択と衝動買いの両方を
  形作りうる」という統合的・一般化した結論
- **初回Ledgerに存在していたEvidence**: 上記2研究の限定的な知見のみ
- **何が不足していたか**: 一般化を裏付ける、複数業態・複数店舗を
  横断した比較Evidence
- **なぜMAJORか**: 個別の限定研究から店舗運営全般への一般化は、
  Ledgerが慎重に維持していた因果の範囲を超えるため
- **追加Researchで取得したSource**: 同上2件
- **解消方法**: 一般化の程度を、追加Evidenceで裏付けられる範囲まで
  弱める形でWriterが再生成
- **原因分類**: **`RESEARCH_COVERAGE_INSUFFICIENT`**
- **追加発生したAPI call**: MAJOR-1と共通

### No.4でWriter前に検知可能だったか

**検知可能だった。** Part Cで後述する通り、Research Coverage Gateを
初回Research直後・Writer実行前に配置してBacktestしたところ、実際に
`MORE_RESEARCH_REQUIRED`と判定し、指摘内容もMAJOR-1〜3の原因と高い
精度で一致した(詳細はPart C参照)。

---

## Part C: Research Coverage Gateの検証

### C-1〜C-3. 設計

[er006_research_coverage_gate_01.py](er006_research_coverage_gate_01.py)
として実装。GPT-5.6 Lunaへ、対象TopicのタイトルとVerified Fact
Ledgerのみを渡し、Source数のような機械的閾値を使わず、7つの観点
(中心的な問いに答えられるか/説明ロジックの裏付け/主要論点の網羅/
因果説明の十分性/一方向への偏り/反証・限定条件の欠落/Writerの推論への
依存度)から`COVERAGE_PASS`/`MORE_RESEARCH_REQUIRED`を判定させる。
`MORE_RESEARCH_REQUIRED`の場合のみ、不足項目・理由・必要な証拠種別を
返す。Production本配線はしていない(検証用スクリプトのみ)。

### C-4. Backtest結果

**未来情報リークを防ぐため、No.4は当時実際に使っていた2ソース
(Vogel 2021・Mantratzis 2023)のみで初回Research状態を再構築し
(追加ソース・後続の発見内容は一切含めない)、Gateへ入力した。**

| Topic | 入力 | 期待結果 | 実際の結果 | 判定 |
|---|---|---|---|---|
| No.4(round1再構築、2ソースのみ) | Research Round1状態 | MORE_RESEARCH_REQUIRED | **MORE_RESEARCH_REQUIRED** | **MATCH** |
| No.5 | 実際の初回(唯一の)Research状態 | COVERAGE_PASS | **COVERAGE_PASS** | **MATCH** |
| No.6 | 実際の初回(唯一の)Research状態 | COVERAGE_PASS | MORE_RESEARCH_REQUIRED | **MISMATCH(false positive)** |

**No.4の指摘内容とMAJOR 3件との整合性**: Gateが指摘した不足項目3件
(①棚替えの反復性・頻度のEvidence欠如、②企業側の動機Evidence欠如、
③単発研究からの一般化に対する限定条件欠如)は、Part BのMAJOR-1〜3の
原因と**内容レベルで高く一致**している。特に①②は、実際に追加した
SRC-003(Edirisinghe、データ駆動の定期再配置+衝動買い目的)・SRC-004
(業界誌、継続的レイアウト見直し)が直接埋めた不足そのものである。

**No.6のfalse positiveの原因**: Gateは「配送追跡という具体的現象を
直接扱ったEvidenceがLedgerにない(SRC-001は選挙・司法試験・就職活動の
待機研究、SRC-002は無関係なラボ実験)」ことを理由に不足と判定した。
これは学術的には正しい指摘だが、**eigo-radioのPool記事という編集
フォーマット自体が、一般的な心理学・行動科学の知見を身近な具体例へ
類推適用することを前提としている**(既存記事Public Benches・
Subscriptions・Startupsも同様の構造)。Gateはこの「妥当な類推適用」と
「真に不足したEvidence」を区別できておらず、現状のプロンプトのままで
は本番運用に適さない**calibration不足**が判明した。

**false positive / false negative**: false positive 1件(No.6)。
false negativeは今回のサンプルでは0件(No.4を正しく検知)。

### C-5. Gate判定

**`PROMISING`**

根拠: 実際に問題が起きたケース(No.4)を、内容レベルで高精度に予測
できた一方、問題が起きなかったケース(No.6)では現状の判定基準が
厳しすぎるfalse positiveを1件出した。3 Topicのみのサンプルであり
Production一般化は判断しない。false positiveの原因(類推適用を
不足と誤認する)は具体的で、プロンプト調整による改善が見込める。

### C-6. Gate追加によるClean Cost増加

| Topic | model | input tokens | output tokens | API Cost | wall-clock |
|---|---|---|---|---|---|
| No.4(round1) | gpt-5.6-luna | 3,743 | 1,097 | ¥0.330 | 13.0s |
| No.5 | gpt-5.6-luna | 4,475 | 592 | ¥0.257 | 6.9s |
| No.6 | gpt-5.6-luna | 2,765 | 1,333 | ¥0.344 | 13.6s |
| **平均/Topic** | | | | **¥0.311** | **11.2s** |

**Clean Cost増加率**: ¥0.311 ÷ ¥65.14(既存Clean Production baseline)
= **約0.48%**(§8の「理想」基準である3%を大きく下回る)

### C-7. 採算評価(Break-even)

- **Cost added every Topic**: ¥0.311/Topic(恒常コスト)
- **Cost potentially avoided**: No.4型failureのResearch+Writer+
  Support Additional Cost=¥53.6/件(Part A-2参照)
- **Break-even**: ¥53.6 ÷ ¥0.311 ≈ **約172 Topic**に1回以上、No.4型
  failureを防げれば経済的に見合う

今回の3 Topic中1 Topic(33%)がNo.4型のResearch不足を起こしており、
この頻度が今後もある程度続くと仮定すれば、Break-eneuラインを大幅に
下回るコストで導入できる計算になる。ただし3 Topicのみのサンプルで
あり、実際のfailure頻度は不明である。

### C-8. Production導入判断

**推奨: Option B(もう数Topicで追加検証)**

理由:
1. コスト面は明確に「理想」基準をクリアしており、Clean Cost増加を
   懸念する必要はほぼない
2. No.4型の実際の失敗を高精度で予測できたことは強いポジティブ
   シグナルである
3. 一方、No.6のfalse positiveは、現状のプロンプトのままでは「常に
   MORE_RESEARCH_REQUIREDと言い続ける」過検知Gateになるリスクを
   示しており、この状態でProduction本配線すると、むしろ不要な追加
   Researchを誘発しかねない(Gate自体が新たなAdditional Costの発生源
   になる本末転倒のリスク)
4. false positiveの原因(類推適用の許容基準)はプロンプト側で対処
   可能と考えられるため、Option C(不採用)は時期尚早
5. Option A(即時本配線)は、false positive対策が入っていない現状の
   プロンプトのままでは時期尚早

**次のアクション(次タスクでの検討候補)**: プロンプトへ「類推適用
(analogical application)は不足とみなさない」旨を明示的に追加した上で、
No.7以降の数Topicで再Backtestし、false positive率が十分低いことを
確認してからProduction配線を判断する。

---

## Part D: No.6 TTS ¥85.0のRCA

### D-1. Batch job数の完全内訳(88 − 67 = 21の原因)

| Topic | Batch job数(実測) |
|---|---|
| No.4 | 67 |
| No.5 | 67 |
| No.6 | 88 |

No.6の超過21 jobsは、**主に2つの固有名詞・表記由来の問題を持つ3
segment**に集中している:

| Segment | Level | Attempts | 内訳 | 状態 |
|---|---|---|---|---|
| full_story_part1 | B1 | 6 | standard 6 | ASR_VALIDATION_UNCERTAIN |
| full_story_part1 | A2 | 12 | standard 6+fallback 6 | STOPPED |
| point_one | A2 | 12 | standard 6+fallback 6 | STOPPED |

この3 segmentだけで、クリーンな最小値(3 attempts)に対し+27
attemptsの超過。他のsegment(comment_4 B1: 5、point_one_heading B1: 4、
full_story_part2 B1: 2、point_two A2: 4等)の小さな超過(合計約+13)と
相殺した結果、正味の超過が全体で+20〜21 attempts相当となっている
(No.4・No.5もそれぞれ独自の小さな超過を持つため、単純な差分ではなく
按分計算が必要。詳細はPart A-3参照)。

### D-2. 直接原因の特定

- **full_story_part1(B1・A2共通)**: 実在する2025年Emotion誌の研究者
  姓 **"Sweeny"** を、ASR(OpenAI gpt-4o-mini-transcribe)が一貫して
  **"Sweeney"**(標準的な綴り)と誤認識した。TTS自体は正しく"Sweeny"
  と発話している可能性が高いが、ASRが「より一般的な綴りへ引っ張られる」
  形で誤って書き起こしている。これは既知のOttoni型(固有名詞ASR誤認識)
  と同じ系統の問題である
- **point_one(A2)**: 記事本文に含まれる数式表記
  **"*b* = 0.90"・"2 × 10⁻¹⁶"**(イタリック変数名・乗算記号・上付き
  指数を含む)を、TTSは正しく「B was 0.90」「2 times 10 to the minus
  16th」と読み上げているが、既存Validatorの正規化ロジックには
  数式記法の読み上げ変換パターンが存在せず、機械的に一致判定できない。
  **これは今回新たに発見された、既存パターンとは別種のValidator
  ギャップである**(数字の桁区切り・パーセント・通貨等は既存
  Validatorで対応済みだが、変数記号・指数表記の音声化は未対応)

### D-3. Clean TTS Cost / Additional TTS Cost

| | Clean | Additional | Additional率 |
|---|---|---|---|
| No.6 TTS(Batch) | ¥45.9 | ¥39.1 | 46.0% |

(算出方法はPart A-3参照)

### D-4. 高コストの主因

- **A. spoken text量が多い**: 該当なし(No.4〜6とも47 unit、同一構造)
- **B. 必須segment数が多い**: 該当なし(同上)
- **C. retry/fallbackが多い**: **主因。寄与度: 約90%以上**
  (上記3 segmentで+27 attempts、他の小さな超過が残り)
- **D. Master Audio reuseが少ない**: 該当なし。共通ナレーション
  (Welcome・番号読み上げ等)はNo.4完走時点で既にキャッシュ済みであり、
  No.5・No.6とも同条件でキャッシュを再利用している(3 Topicで差なし)
- **E. その他**: なし

**結論: No.6の高コストは、ほぼ全面的にC(retry/fallbackの多さ)に
起因し、その中でも「Sweeny」誤認識(2 segment)と数式表記(1 segment)
という具体的な2種類の既知/新規パターンが大部分を説明する。**

---

## 5. 使用ログ・reconciliation対象一覧

- `er006_output/pool_pilot_01/raw_usage_log.jsonl`(No.4〜6の全API使用ログ)
- `er006_output/pool_pilot_01/{pool_n4_supermarket,pool_n5_cafes,pool_n6_delivery}/*/audit/tts_generation_results.json`
- `er006_output/pool_pilot_01/{pool_n4_supermarket,pool_n5_cafes,pool_n6_delivery}/*/ledger_deviation.json`
- `er006_output/pool_pilot_01/pool_n4_supermarket/*/fact_qa.json`
- `er006_output/pool_pilot_01/coverage_gate_01/gate_usage_log.jsonl`(Gate検証専用ログ)
- `er005_output/cost_baseline_01/pricing_snapshot.json`

## 6. 新規API Cost

- Coverage Gate Backtest 3回: ¥0.932
- No.4 Round1状態の再構築(Evidence Pack/VFL/Verification、新規情報
  収集は行わず、当時と同一の2ソースから再導出): ¥2.214
- **合計: ¥3.15(新規記事生成・新規TTS・新規Researchは一切行っていない)**

## 7. Regression Test

コード変更(本番影響のあるファイル)は行っていないため、regression
testは対象外。新規検証スクリプト(`er006_research_coverage_gate_01.py`
等)はいずれもProduction非配線の独立ファイルであり、既存の
`run_project_regression.py`が対象とする`er0*_test_*.py`パターンにも
該当しない。

---

**完了。No.7以降の記事生成・Batch並列数変更・Standard TTS導入・
Research source最低件数ルール・Gate本配線・Writer prompt恒久変更・
新規Queue Architecture・Cost baseline ¥111.17の正式改定のいずれも
行っていない。**
