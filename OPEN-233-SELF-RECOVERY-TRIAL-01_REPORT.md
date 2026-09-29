# OPEN-233-SELF-RECOVERY-TRIAL-01 REPORT

管理ID: OPEN-233-SELF-RECOVERY-TRIAL-01(前Phase`OPEN-233-CHECKER-
REDESIGN-TRIAL-01`から目標を転換した新Phase)。

## §1. 設計フェーズ(委任_01、2026-09-30、Production Self-Recovery Flow
設計書作成)

**注記(委任_02、2026-09-30追記、本文への遡及訂正ではない)**: 本§1が
参照する`docs/pm/opus_l2_review_open233_checker_trial_01.md`(前Phase
Opus L2レビュー#1)は、Fableが2026-09-30に実施したOpus model_id probe
(read-only)により、実行時のOpus agentエイリアス(`opus-consultant`、
`model: opus`)の自己申告モデル名が「Opus 5 (1M context)」・exact
model ID `claude-opus-5[1m]`・knowledge cutoff 2026-05であったことが
判明した。**Opus 5.5ではない**(ユーザーは本Phase開始時、Opus L2
レビューは実際のmodel_idを確認し利用可能なら最新Opus 5.5を明示使用
するよう指示、旧Opus固定なら勝手に実行せず報告するよう指示した)。
前Phase Opus L2レビュー#1も同エイリアス経由で実行されており、当時
model_idは記録されていないが、Opus 5で実行された可能性が高い。本Phase
(委任_02時点)のOpus L2レビューは、ユーザーへのmodel_id指定確認が
得られるまで**未実施**。詳細: `DECISION_LOG.md`2026-09-30`OPEN-233-
SELF-RECOVERY-TRIAL-01`委任_02エントリ。

**Status**: `DESIGN_READY_FOR_OPUS_L2`。

**背景**: 前Phase(`OPEN-233-CHECKER-REDESIGN-TRIAL-01`)は、Checker
単体の「不要BLOCK率≤25%」を目標とした改善Trialだったが、Opus L2
レビュー#1(論点2)により、現行fixture単位定義では正しいCheckerでも
下限50%であり指標自体が壊れていることが判明し、`USER_DECISION_
REQUIRED`のままStopした(累計¥45.6803/総枠¥400、残¥354.3197、
本Phaseの予算とは別管理)。ユーザーは2026-09-30、目標を「Checker単体の
過剰品質改善」から「**Production運用全体でLedger/Deviation Check起因
のUSER_DECISION_REQUIREDを実質ゼロにするSelf-Recovery Flow**」へ
転換する新Phase(本OPEN-233-SELF-RECOVERY-TRIAL-01)を開始した。

**本委任(委任_01)の内容**: API呼び出しなし・¥0・Production非接続・
実装なしの設計書作成のみ。`docs/pm/design_open233_self_recovery_
flow_01.md`(章立て12節、委任文で指定された固定構成)を新規作成した。

**設計の骨子**:
- **Stage 1 Initial Check**: 既存Production Deviation Check(Prompt/
  schema/モデル[gpt-5.6-luna]不変)をそのまま使い、`LEDGER_COMPLIANT`
  →ACCEPTABLE(継続)、`LEDGER_DEVIATION`→BLOCKING-candidate(Stage 2へ)
  の2値ルーティングとして実現する(現行アーキテクチャはQUALITYを
  Stage 1で直接出力できないため、QUALITYはStage 2専用の出力値とした)。
- **Stage 2 Second Judge**: 独立Prompt・別API call(Opus L2レビュー#1
  論点1推奨4「2段階呼び出し」採用)でmateriality(BLOCKING/QUALITY/
  ACCEPTABLE)をclaim単位判定。deterministic safety floor(changed_
  actor/number/negation/comparison/timeのいずれかtrueなら無条件
  BLOCKING)を設定し、V5-C(実データで見逃し実証済み、前Phaseで不採用
  推奨済み)は採用しない。
- **Stage 3 Automatic Rewrite**: JA側は既存案B(全文差し戻し、
  Production code再利用)、EN側は局所Rewrite(設計提案、Phase 1で
  新規実装・検証、既存`split_family_x_article_text_v2()`のNG guardを
  再利用)。Recheckは全文Checkerで実施(fail-closed優先、局所チェック
  にしない)。
- **Stage 4 Escalation**: cycle上限(記事あたり最大2)到達後もBLOCKING、
  またはJA Fact Check自体がSTOPした場合のみ発火。

**現行Production フローの実態調査(新規Evidence)**: `er012_e_family_
entertainment_two_level_runner_01.py`のコードを精読し、Hormuz run_01
(HF-006)/run_02(HF-011)/run_03(HF-009×2、Advanced側は案Bで解消・
Standard側で別claim新規発生)・Meta run_03(既存must-fix retry1回で
解消)の4件を、現行retry機構(段落数retry・deviation must-fix retry
1回・案B[JA差し戻し1回]の3独立axis)のどの分岐で何が起きたかまで
Evidence付きで特定した(設計書§2、§3-5参照)。**新規発見**: 現行
Production Checker(`er003_v1_en_direct_vfl_01_generate.py::MODEL =
routing.WRITER_MODEL = "gpt-5.6-luna"`)は、前Phase Trial(gpt-6-luna
固定)とは異なるモデルであり、Hormuz/Meta E2E実測データと前Phase
Trialデータは直接比較不可(設計書§2/§4-6/§10リスク8)。

**gold候補(最終到達状態ベース)**: 前Phaseのfixture単位/claim単位
gold候補表を変更せず、「どのStageでどう到達するのが期待されるか」の
軸で4群(Safety群/False・borderline群/Real-but-fixable群/Normal群)へ
再編した(設計書§7、いずれも候補gold・ユーザー確認待ち)。

**Phase 1 Trial計画**: 既存Trial 1/2/n=20のdeviation jsonをStage 2の
入力として再利用(Stage 1再課金なし)、Stage 3は代表fixtureで実際に
Rewrite→Recheckサイクルを実行する設計とした。概算費用¥15〜35
(要実測、次回委任で確定)。

**Opus L2への論点案(7個)**: deterministic safety floorの十分性、
局所Rewriteの優先度、cycle上限2回の妥当性、Stage 1 recall非決定性の
扱い、Escalation実質ゼロ化と「安全≠成功」原則の関係、モデル差異
(gpt-5.6-luna vs gpt-6-luna)、HOOK_CLAUSE整合(設計書§11)。

**ユーザー判断11該当**: 本設計書自体は非該当(文書のみ)。ただし
Phase 1 Trial実行(次回委任)着手前に、Stage 2のmateriality軸導入
(旧Opus論点1のC1相当、前Phaseで「事前了承要」と指摘済み)をFamily X
限定・Production非接続のTrialとして進めてよいかのユーザー確認を
Checkpoint Aで得ることを提案する(設計書§12)。

**費用**: 今回¥0(API呼び出しなし)。本Phase累計¥0/総枠¥400、残¥400。
前Phase累計¥45.6803は別枠(参考記載のみ)。

**Production/Dangling Reference確認**: `git diff --stat`でProduction
ファイル(`er003_*`/`er006_*`/`er012_*`/`er019_*`)に差分なし(コード
変更を一切行っていない)。

Evidence: `docs/pm/design_open233_self_recovery_flow_01.md`(新規、
全文)。入力: `OPEN-233-CHECKER-REDESIGN-TRIAL-01_REPORT.md`§9〜§13、
`docs/pm/design_open233_checker_redesign_trial_01.md`§2-補/§4-補、
`docs/pm/opus_l2_review_open233_checker_trial_01.md`(全文)、
`docs/pm/negative_claim_candidates_open233_01.md`、
`er012_e_family_entertainment_two_level_runner_01.py`(L260-679精読)、
`er019_family_x_entertainment_production_runner_01.py`(STOP箇所)、
`er003_v1_en_direct_vfl_01_generate.py`(L490-620、Prompt/HOOK_CLAUSE/
モデル定数)、`FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_REPORT.md`
(Hormuz run_01〜03・Meta run_03のSTOP/通過Evidence)。

## §2. コスト章追加(委任_02、2026-09-30、設計書へCost Cap要件を組み込む
修正+Opus model_id probe結果の記録)

**Status**: `DESIGN_READY_FOR_OPUS_L2`(model_id確認待ち、変わらず)。

**背景**: ユーザーが2026-09-30、量産時の継続コスト上限を**最大
+¥3/記事**(「使ってよい上限」ではなく「できる限り安く」が大前提)と
明示し、Stage別計測(発動率・1回コスト・1記事平均・worst case・
P50/P95、固定費と条件付き費の分離)、Safety/Self-Recovery/Costの同時
最適化、優先順位①Prompt改善→②BLOCK時のみRe-screen→③必要時のみ
Rewrite→④限定self-consistency、を追加指示した。あわせてOpus L2
レビュー投入前に実際のmodel_idを確認するよう指示した。

**Opus model_id probe結果(read-only、API呼び出しなし)**: Fableが
`opus-consultant`(`.claude/agents/opus-consultant.md`の`model: opus`
エイリアス)を確認した結果、自己申告モデル名「Opus 5 (1M context)」・
exact model ID `claude-opus-5[1m]`・knowledge cutoff 2026-05であり、
**Opus 5.5ではない**。前Phase Opus L2レビュー#1(`docs/pm/opus_l2_
review_open233_checker_trial_01.md`)も同エイリアス経由であり、当時
model_id未記録だがOpus 5で実行された可能性が高い。本委任では、この
事実を本REPORT§1と同レビューファイルの**冒頭ヘッダへ注記として追記**
した(本文は一字も変更していない)。本Phase(委任_02時点)のOpus L2
レビューはユーザーのmodel_id指定確認が得られるまで**未実施**のまま。

**設計書への追加内容**: `docs/pm/design_open233_self_recovery_flow_01.
md`へ以下を追加(既存節は削除せず追記のみ):
- **新設§13「コストモデルと+¥3/記事 Cap」**: 単価根拠(公式価格
  一次ソース、GPT6-MODEL-COMPARISON-TRIAL-01実測)、現行Production
  Checker(Stage 1)の実装確認済みベースライン構成(**Advanced+Standard
  各1 call/記事、通常ケース≈¥0.98/記事**)、Stage 2入力設計(§4-4)と
  費用見積り(§9-1)の**不整合発見**(§4-4は記事全文入力、§9-1は
  楽観的な縮小入力を仮定しており矛盾。本章で保守側へ統一)、Stage別
  unit cost見積り、3シナリオ(楽観/中央/悲観)での発動率モデルと
  「純増分=新方式総コスト−現行方式総コスト」という定義に基づく
  期待値計算(**楽観/中央シナリオでは現行よりむしろ安い[−¥0.47/
  −¥0.48記事]、悲観シナリオでも+¥0.60/記事**)、worst case分析
  (**設計§5-3の「同一記事でJA全文Rewrite案Bを2回使わない」制約を
  守れば純増分worst case≈¥2.88/記事[Cap余裕僅か¥0.12]、守らなければ
  ¥6.40/記事でCap超過**、この制約がCap遵守に構造的に必須と特定)、
  段階案α〜δの比較と第一候補(案γ=Stage1不変+BLOCK時のみStage2+
  必要時のみRewrite、cycle上限2)、Cap内で困難な要素(Stage 2実単価が
  最大の不確実性要因、worst case余裕が僅少)を中間報告として明記。
- §8-4(Stage別コスト計測項目の新設)、§9-3(Trial harnessのStage別
  usage記録要件)、§10リスク#9・#10(コスト肥大、Cap超過時のUSER_
  DECISION_REQUIRED条件)、§11 Opus論点8(Cap内での最適性・より安い
  代替の妥当性)、§12-1(Checkpoint A提示項目、ユーザー指定6項目+
  既存3項目)を追加。

**実測併用**: 本委任は設計書修正のみでAPI呼び出しは行っていないが、
既存の実Production run(Meta run_03 `raw_usage_log.jsonl`)を独立に
再計算し、公式単価ベースの合計¥4.13(既存報告¥4.213と概ね一致)を
確認、call単位で¥0.04〜¥1.29の幅があることを新規に特定した(§13-1)。

**費用**: 今回¥0(API呼び出しなし、既存artifactの再計算のみ)。本Phase
累計¥0/総枠¥400、残¥400。

**Production/Dangling Reference確認**: `git diff --stat`でProduction
ファイル(`er003_*`/`er006_*`/`er012_*`/`er019_*`)・`.claude/agents/`
に差分なし(コード変更・agent定義変更を一切行っていない)。

Evidence: `docs/pm/design_open233_self_recovery_flow_01.md`(§8-4/
§9-3/§10/§11/§12-1/§13追記)、本REPORT§1冒頭注記、`docs/pm/opus_l2_
review_open233_checker_trial_01.md`冒頭注記。入力:
`GPT6-MODEL-COMPARISON-TRIAL-01_REPORT.md`§C-2〜C-5、`FAMILY-X-
REFRESH-E2E-PRODUCTION-WIRING-01_REPORT.md`(Meta run_03費用実測)、
`er019_output/family_x_refresh_e2e_01/meta/run_03/raw_usage_log.
jsonl`(本委任で独立再計算)、`er012_e_family_entertainment_two_level_
runner_01.py`(L381-388/L477-484、Checker call構成確認)、`.claude/
agents/opus-consultant.md`(model_id probe対象、変更なし)。
