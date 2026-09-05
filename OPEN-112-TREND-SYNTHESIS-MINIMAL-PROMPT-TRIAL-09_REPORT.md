# OPEN-112-TREND-SYNTHESIS-MINIMAL-PROMPT-TRIAL-09 報告書

対象: News系(A Family)Trend Synthesisモードについて、最小限のFocus Module Promptを
[OPEN-112-NEWS-MODE-DESIGN-08_REPORT.md](OPEN-112-NEWS-MODE-DESIGN-08_REPORT.md)の設計に基づき作成し、
実在テーマ(米国・イラン、ホルムズ海峡)で実際の記事Trialを行った。

**Production Prompt/code変更なし。News Focus Module正式実装・Topic Master変更・新Validator追加・
APPROVED_FOR_PRODUCTION/PRODUCTION_WIREDのいずれも行っていない。**

---

## 1. Trialテーマ・Source収集

タスク第一候補「イラン情勢」を採用。2026年9月5日に実際にWebSearch/WebFetchで新規収集した
(既存の`topic_package_イラン_アメリカ_情勢_2026-07-14.py`とは中心主張が異なる新テーマとして扱い、
Topic Masterへは追加していない)。

収集した独立Signal(S-1〜S-9、詳細: `er011_output/open112_trend_synthesis_minimal_prompt_trial_09/research/signal_inventory.json`):

| Signal | 内容 | 情報源種別 |
|---|---|---|
| S-1 | 4月封鎖の実効性を巡る対立(拿捕29隻 vs 回避26隻以上) | 米軍発表・Lloyd's List集計 |
| S-2 | 6月停戦→7月商船攻撃→7月14日封鎖再開 | 複数一次発表の集計 |
| S-3 | 8月、イラン国内ガス生産能力喪失・石油化学プラント停止 | イラン反体制派系メディア(要留保) |
| S-4 | 8月25日、米海軍による機雷除去作戦(100個超) | 米当局発表(集計経由) |
| S-5 | 8月18日、トランプ発言・交渉期限切れ | 大統領発言・報道 |
| S-6 | Eurasia Group、和平見通しを年末へ後退 | 民間政治リスク分析 |
| S-7 | CNN(9/4)、「持続不可能な膠着」評価 | 報道分析 |
| S-8(counter-signal) | 米エネルギー長官、「開戦後最高値」主張(9/2) | 政権高官発言 |
| S-9 | EIA四半期統計、輸送量の大幅減少 | 米政府公式統計 |

Trend Gate判定(`research/trend_gate_result.json`): 6条件すべてPASS、**TREND_READY**。
Mode判定2問テストでも`TREND_SYNTHESIS`を確認(単一日付に圧縮すると中心的主張が失われる/
いずれか1つのSignalを除いても中心的主張は残る)。既存Topic Master(7月分2件)との重複チェックも
実施し、状態変化・新しい強いSignal・十分な期間経過(約7〜8週間)のいずれも満たすため
**重複ではない**と判定した。

---

## 2. Trend Synthesis Focus Module(最小限Prompt)

タスク第5節の指示リストを直接反映した最小限のブロックを、Discovery/Why Trial
(`er011_open112_a_family_4layer_prompt_trial_05.py`)と同じAnchor 1箇所への単一挿入方式で追加した
(`er011_open112_trend_synthesis_minimal_prompt_trial_09.py`、Production Template自体は無変更)。

Phase A(機械的diff検証、テーマ非依存のNo.18 baseline基準): A2・B1Bとも
`clean_single_insert_confirmed=true`(意図しない差分なし)。

---

## 3. 生成結果

既存Production関数(`gen.run_one_pattern`、無変更)をそのまま経由。3回生成(A2×2、B1B×1、
Loop Budget範囲内)。全文は`er011_output/open112_trend_synthesis_minimal_prompt_trial_09/`配下。

| Run | 最終status | ブロック段階 | 主な内容 |
|---|---|---|---|
| a2_run01 | `NG_REVIEW_REQUIRED` | Point Overlap/Value QA | 詳細は4節 |
| a2_run02 | `OK`(複数段でREVIEW_REQUIRED) | — | 詳細は4節 |
| b1b_run01 | `NG_REVIEW_REQUIRED` | Fact Checker(FAIL) | 詳細は4節 |

3記事ともMain Story・Point One(counter-signal/evidence timeframe解釈)・Point Two(損害の
持続性・自己強化メカニズム)・In One Line(mixed evidenceの明示)という一貫した構成になり、
counter-signal(S-8 vs S-9)は3記事すべてで独立したセクションとして明示的に扱われた。

---

## 4. 発見事項(詳細)

### 4-1. A2 run1: Point One/Two「Signal列挙」問題は実際に発生し、既存Value QAが検知した

初回生成(attempt0)で、Point TwoがMain Storyの結論(複数Signalの列挙による「耐久試験」という
まとめ)をほぼそのまま繰り返す内容になり、既存Point Value QA(`qa_not_full_story_paraphrase`・
`qa_adds_new_value`)が正しくFAILと判定した。これはOPEN-112-NEWS-MODE-DESIGN-08 §8/§10で
懸念していた「Point One=Signal A、Point Two=Signal Bの単純列挙」リスクの実例であり、
**既存の意味ベースQAがこのリスクを実際に検知できることを確認した**(EXISTING_QA_SUFFICIENT寄り)。

Diagnostic Full Retryで2回全文再生成した結果、attempt2ではValue QA全項目PASSに到達したが、
Point Two対Full Storyの**lexical overlap比が0.421(閾値0.40)**でflagされたまま解消せず、
Point-only regeneration自体がER-008-N8-FINAL-QA-HARDENING-21で無効化されているため、
article retry上限(2回)に到達し`NG_REVIEW_REQUIRED`となった。

### 4-2. 追加A2実行(run2、再現性確認): 同じ内容が別の生成では1回のRetryで解消

4-1がPrompt構造の問題か生成のばらつきかを切り分けるため、Loop Budget内で追加のA2生成を実施した。
今回はattempt1(全文再生成1回)でPoint Overlap/Value QAが解消し、Fact Checker以降まで到達した。

→ **4-1の膠着は「構造的に必ず起きる」ものではなく、生成ごとのばらつきと、News/Trend記事が
Main StoryとPointで同じ固有名詞・事実語彙(mines/gas/capacity/navy/talksなど)を共有せざるを
得ない性質とが重なって、閾値0.40付近で不安定になりやすいことが原因と考えられる。**

### 4-3. a2_run02のFact Safety 3段QAの結果(重要)

- **Fact Checker**: `REVIEW_REQUIRED`。未出典の分析機関名(Eurasia Group)、攻撃船舶が
  「承認航路外」だったという条件の未確認、**F-005の「100個超の機雷」という具体的個数が
  一次資料で確認できない**、の3点を指摘。
- **Ledger Deviation Checker**: `overall_status=LEDGER_COMPLIANT`だが、Point Two内に
  **MINOR deviation 4件を検出、その全てが`changed_causality`/`changed_certainty`/
  `unsupported_new_claim`**(機雷の存在→「脅威」への格上げ、複数の圧力Signal→「将来の合意条件を
  変える」という因果、停戦しても「自動的には正常化しない」という反実仮想、膠着状態が
  「回復を困難にする」という因果)。これはOPEN-112-NEWS-MODE-DESIGN-08 §10で懸念していた
  **trend overclaim(複数Signalを積み上げた因果・確信度の誇張)そのもの**であり、
  専用カテゴリはないものの、**既存の一般カテゴリが実際にこれを検知した**。
- **Directional Fact Precheck**: `DIRECTION_REVIEW_REQUIRED`。ただし個別の検知内容を見ると、
  本Trial用に人手で作成したLedgerの注記文(「注記1: 本Ledgerは…」)がsentence matcherに
  拾われた可能性が高く、Trend Synthesis固有の新しいGapと断定はできない(Ledger整形上の
  注意点として記録するに留める)。

### 4-4. B1B run1: Fact CheckerがFAIL、原因はLedger作成側(本Trial)の精度不足

Point Overlap/Value QAはattempt1(全文再生成1回)で解消し、A2で見られたSignal列挙傾向は
B1レベルでは顕在化しなかった。一方でFact Checkerが`FAIL`と判定:

1. 本Trial用Ledgerに記載した「エネルギー長官の発言は9月1日(月曜)」という日付attributionについて、
   Fact Checker自身の独立Web検索が「実際には8月31日(月)の可能性が高い」と指摘した。これは
   **Writerの誤りではなく、本TrialでLedgerを作成する際の日付照合ミス**である。
2. F-005の「100個超の疑わしい機雷」という具体的個数が一次資料で確認できない、という指摘
   (4-3と同一の論点が独立に再現)。

**含意**: OPEN-112-NEWS-MODE-DESIGN-08 §10で述べた「Trend Synthesis用Ledgerは単一出来事の
Ledgerより材料点数が多く、この種の精度誤りが混入しやすい」という懸念が、実際に本Trialの
Ledger作成(WebSearch結果の人手集約)で2件現実化した。ただし**Fact Checkerの独立Web検索が
両方とも正しく検知しており、記事がFAILしたまま黙ってPASSすることはなかった**。

---

## 5. MUST受入条件(20項目)の評価

全項目の詳細は`er011_output/open112_trend_synthesis_minimal_prompt_trial_09/research/trial_findings_summary.json`
に記録。要点:

- **PASS**: Trend Gate、複数独立Signal使用、Point Role Planningによる意味ベース役割分離、
  Counter-signal明示、Fact Safety 3段QA稼働、Point Overlap/Value QA稼働、Evidence Compression稼働、
  CEFR長さ要件、model_id/routing確認、runtime evidence保存、Production無変更、新Validator無し、
  新Dangling Reference無し。
- **PARTIAL(重要)**: (a) Main Storyが「まず変化を提示する」よりも時系列の出来事列挙に近い構成に
  なりがちだった(Focus Module指示の効果は限定的)。(b) Trend strengthがEvidence範囲を超えない、
  という要件はPrompt指示だけでは完全に防げず、Point Twoの因果・確信度の誇張(4-3)は
  **Ledger Deviation Checkerが検知して初めて可視化された**(Promptだけで予防しきれるわけではない)。
- **未達のまま記事化された事例はない**: 全ての未対応論点はNG_REVIEW_REQUIRED/REVIEW_REQUIRED/
  MINOR deviationとして明示的に可視化され、silent incorrectのまま通過した例はゼロ。

---

## 6. 既存QA十分性判定(タスク第13節の4分類)

| 論点 | 分類 | 根拠 |
|---|---|---|
| Trend overclaim(複数Signal統合の因果・確信度誇張) | **A. EXISTING_QA_SUFFICIENT寄り** | 専用カテゴリはないが、既存の`changed_causality`/`changed_certainty`/`unsupported_new_claim`タグが実際に4件全て検知した。ただしseverityが一律MINORとなりoverall_statusを止めない点は要検討 |
| Point Overlap lexical閾値(0.40)とNews/Trend固有語彙の衝突 | **B〜C. PROMPT_TIGHTENING_MAY_BE_ENOUGH 〜 NEW_QA_MAY_BE_NEEDED** | 意味的に新しい価値を持つPoint(Value QA全PASS)でも、固有名詞・事実語彙の共有だけでNGになる事例が発生。Point-only regenerationが無効化されているため、閾値超過が記事全体の再生成コストに直結する |
| Trend Ledger作成時の精度誤り(日付照合・未確認個数の混入) | 既存Fact Checkerで検知可能(EXISTING_QA_SUFFICIENT)だが、**Ledger作成プロセス自体の頑健性**が課題 | 本Trialの人手Ledger作成で2件現実化。既存の自動Researcherパイプライン(`er003_v1_en_direct_vfl_01_generate.py`)を経由しない手動Trend Ledger作成には、この種の精度リスクが伴う |

---

## 7. Major/Daily境界の再確認

生成後も、3記事いずれも単一日付へ圧縮すると中心的主張(長期化する経済的消耗戦、かつ
回復を巡る評価の対立)が失われる内容であり、事前のTrend Gate判定(`TREND_SYNTHESIS`)は
覆らなかった。

## 8. Trend重複

既存Topic Master(7月分2件)とは中心主張が異なり(7月=停戦崩壊の切迫、9月=経済的消耗戦への
移行と評価の対立)、重複ではないと判定した(詳細は`research/trend_gate_result.json`)。

## 9. actual model_id / runtime evidence

全run、Writerモデルは`gpt-5.6-luna`(`routing.require_model()`経由で確認)。
API呼び出し・応答ID・所要時間は`raw_usage_log_trial09*.jsonl`・各`audit/*.json`に保存済み。

## 10. USER_DECISION_REQUIRED(候補、OPEN_ITEMSへは今回登録せず候補報告のみ)

1. Ledger Deviation Checkerが「trend overclaim的な因果・確信度の誇張」を実際に検知した場合、
   severityを一律MINOR(overall_statusを止めない)のままとするか、Trend Synthesisでは
   より厳しく扱うかの方針決定。
2. Point Overlap QAの固定lexical閾値(0.40)を、News/Trendのような固有名詞・事実語彙が
   本質的に共有されやすいEditorial Typeに対して調整(閾値緩和、または共有される固有名詞を
   重複判定から除外する等)する必要があるかの判断。
3. Trend Synthesis用Ledgerを、今回のような人手WebSearch集約ではなく、既存の自動Researcher
   パイプライン(`er003_v1_en_direct_vfl_01_generate.py`)を経由させるべきかの判断(今回現実化した
   日付照合ミス・未確認個数混入のリスク低減のため)。

## 11. Production変更なし確認

`git status`で新規ファイル(本レポート・Trialスクリプト・`er011_output/open112_trend_synthesis_minimal_prompt_trial_09/`配下)以外に変更が無いことを確認済み。Production Prompt・code・Topic Master・Validatorへの変更は一切無い。

## 12. 次アクション

10節のUSER_DECISION_REQUIRED 3点についてユーザーの意向を確認したうえで、
(a) Point Overlap閾値・Ledger Deviation severity方針を反映した追加Trial、または
(b) Major/Daily Newsモードの同様のTrialへ進む、のいずれかを次工程候補とする。
今回はここでSTOPし、Production実装・追加記事生成は行わない。

---

今回Status: `USER_DECISION_REQUIRED`
Trend Gate: `TREND_READY`
Trend Synthesis: 4slot構造で成立(Point Role Planningによる意味ベース役割分離を確認)
A2: run1 `NG_REVIEW_REQUIRED`(Point Overlap閾値)、run2 `OK`(複数段REVIEW_REQUIRED、再現性確認により閾値付近の不安定さと判定)
B1: `NG_REVIEW_REQUIRED`(Fact Checker FAIL、原因はLedger作成側の精度不足2件)
Trend overclaim: 既存QA(Ledger Deviation Checker)が実際に検知(EXISTING_QA_SUFFICIENT寄り、ただしseverity方針は要検討)
Existing QA: 概ね十分(Fact Checker・Ledger Deviation Checkerとも機能)、Point Overlap閾値のみ再検討候補
New QA: 新規Validator追加は不要と判断(既存カテゴリの範囲内で検知可能)
Production変更: なし
USER_DECISION_REQUIRED: あり(10節、3点)
次に進めてよい工程: 10節の3点についてユーザー判断後、追加Trial(閾値/severity調整)またはMajor/Daily Newsモードへの展開
