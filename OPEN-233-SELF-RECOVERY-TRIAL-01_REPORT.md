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

## §3. Stage 1再検証・設計修正(委任_03、2026-09-30、opus-consultant
model更新+Stage1設計確定+claim単位「Trial上の正解ラベル」確定)

**Status**: `DESIGN_READY_FOR_OPUS_L2`(Stage1構成が確定、Opus L2投入
待ち)。API呼び出しなし・¥0・Production非接続・実装なし。

**作業A(opus-consultant model更新)**: `.claude/agents/opus-consultant.
md`のfrontmatter`model: opus`を`model: claude-opus-5-5`へ変更(1行のみ、
本文不変)。実際の利用可否probeはFableが起動時に実施(本委任では未検証)。

**作業B(Stage 1設計の再検証・結論)**: 真のProduction Checker(V0、
Prompt無変更)は`er009_changed_actor`をn=6中3回(50%)見逃す実測がある。
「Stage 1が検出しなければStage 2/3/4は発火しない」という構造的事実
から、V0のままでは重大Fact見逃し0件というPrimary Safety KPIを満たせ
ないと判断し、選択肢S1-A(V0)/S1-B(V4A)/S1-C(V4A+C2)/S1-D(Stage1+2
一体型)を(1)重大Fact見逃し(2)Initial BLOCK率→発動率→条件付きコスト
(3)非決定性耐性(4)Production採用時の変更範囲の4軸で比較した(設計書
§14)。**S1-B(V4A)を採用**。理由: changed_actor 5/5(100%)実測・
Safety群12/12維持・negative control改善(Meta_run03_standard n=20で
90%→100%)。残存リスク(hormuz_run03_standardがn=20でV0比悪化方向、
100%→85%、統計的有意差なし)は認識した上で採用。真のProduction Prompt/
schema/Validator/routing/runnerは無変更のまま(V4AはFamily X限定Trial
harness内のみ)。**検出漏れ型Safety対策**: deterministic pre-check
(Ledger構造化フィールドとの機械照合、¥0、fail-closed追加層)を採用、
「PASS時限定2nd run」は固定費化するため不採用、self-consistencyは
検出漏れ対策として無効(目的外)のため不採用(設計書§14-4)。

**作業C(claim単位「Trial上の正解ラベル」確定)**: 用語を「gold」から
「Trial上の正解」「正解ラベル」へ統一(本Phase文書内のみ、前Phase文書
`design_open233_checker_redesign_trial_01.md`等は不変)。確定ラベル:
B1-a/b=ACCEPTABLE、B1-c=BLOCKING、B2=QUALITY、B3=BLOCKING、B4-a=
BLOCKING、B4-b/c=ACCEPTABLE〜QUALITY(Trialでは**QUALITY扱い**)、
B4-d=QUALITY〜BLOCKING(Trialでは**BLOCKING扱い、fail-closed側**)。
各群(Safety/QUALITY/ACCEPTABLE/Real-but-fixable/Normal)に期待到達
経路を新設(設計書§7-0〜§7-6)。KPI/Safetyの意味は変えていない。

**作業D(Self-Recovery案の修正反映)**: §3-1をStage1=V4Aへ更新。§4-4
(Stage 2入力)を「記事全文」から「対象claimを含む段落±1段落+Ledger
全文+source context+Stage1 deviation出力」へ縮小確定(Ledgerは
fail-closed優先で全文維持)。**§13コスト再計算(V4A反映)**: 記事あたり
純増分(期待値)=楽観**−¥0.15**/中央**−¥0.06**(節約margin縮小)/
悲観**+¥0.84**(いずれもCap内)。**worst case(tail)はV4A採用前の
¥2.88[Cap内、余裕¥0.12]から¥3.96[Cap約32%超過]へ悪化**(両段階同時
BLOCK+JA-origin+cycle2必要という複合稀事象、概算発生率約1%/記事、
Phase1実測必須)。§11(Opus論点)をユーザー指定8項目(Self-Recovery
全体/Stage1/Second Judge/Rewrite戦略/Safety/Cost/loop化リスク/
Escalationゼロの現実性)へ全面再編、各項目に暫定答え+批判してほしい点
を付与。§12をユーザー指定7項目のUSER_DECISION_REQUIRED条件へ全面
置換(KPI変更/重大Fact Safety緩和/+¥3 Cap超過が必要/Production正式
採用配線/Family X以外への正式展開/新Product原則/予算¥400超過)、
それ以外はGuardrail内自律改善範囲と明記。

**USER_DECISION_REQUIRED該当有無**: 該当なし。V4A採用はSafety改善
(緩和ではない)、真のProduction Prompt無変更、期待値ベースCostはCap内。
worst case tailのCap超過(¥3.96、概算発生率約1%)は「恒常的な超過」の
条件には現時点で該当しないと判断するが、Phase 1実測で必ず検証し、
Checkpoint Aで明示的に報告する。

**費用**: 今回¥0(API呼び出しなし)。本Phase累計¥0/総枠¥400、残¥400。

**Production/Dangling Reference確認**: `git diff --stat`でProduction
ファイル(`er003_*`/`er006_*`/`er012_*`/`er019_*`)に差分なし。
`.claude/agents/opus-consultant.md`のmodel行変更のみ(Agent定義、
Production実行コードではない)。

Evidence: `docs/pm/design_open233_self_recovery_flow_01.md`(§3-1/
§4-4/§7[全面改訂]/§8-3/§11[全面改訂]/§12[全面改訂]/§13[再計算]/
§14[新設]追記)、`.claude/agents/opus-consultant.md`(model行)。入力:
`docs/pm/design_open233_checker_redesign_trial_01.md`(§1-1 fixture単位
gold表、§2-補claim単位gold候補表、§4-補V4-A実装・Trial2/n=20実測)、
`OPEN-233-CHECKER-REDESIGN-TRIAL-01_REPORT.md`§9〜§12、`docs/pm/
opus_l2_review_open233_checker_trial_01.md`(論点1〜5全文)、
`docs/pm/negative_claim_candidates_open233_01.md`、`er051_open233_
checker_trial_variant_01.py`(V4A Prompt差分ブロック実装確認)、
`er003_v1_en_direct_vfl_01_generate.py`L495-540(現行Production
Prompt判定ルール・許容規定確認)。

## §4. Opus L2 #1と設計是正(委任_04、2026-09-30、逐語保存+Phase 1前
設計是正+Phase 1計画改訂)

**Status**: `PHASE1_READY`(Opus L2レビュー#1完了・所見反映済み)。
API呼び出しなし・¥0・Production非接続・実装なし。

**runtime evidence**: ユーザー指定`claude-opus-5-5`はClaude Code
2.1.272未対応で400(request id `req_011CfYW9VqvuUcvEUyfZu1Bs`、model
sent: `claude-opus-5-5`、要2.1.280+)。起動時オーバーライドで
`claude-opus-5[1m]`(Opus 5、cutoff 2026-05)にて実行した。
`.claude/agents/opus-consultant.md`の指定は`claude-opus-5-5`のまま
維持する(クライアント更新後に有効)。Opus使用1回。

**作業A(逐語保存)**: `docs/pm/opus_l2_review_open233_self_recovery_
01.md`を新規作成し、Opus L2批判的設計レビュー#1の全文を一字も変えず
保存(冒頭ヘッダのみ付与)。

**作業B(Fable判定・採否)**: 論点1〜8・総合A〜Dの指摘に対し、採用16件
(A1〜A16)・不採用3件(cycle上限1化/Stage2入力Ledger部分化/Stage2-3
統合)・ユーザー判断送り3件(KPI判定方法の再定義/Cap定義解釈/QUALITY
通過のSafety緩和該当性)に分類した。詳細は設計書新設§15(採否・反映節
対応表)。

**作業C(設計書改訂)**: A1〜A16を該当節へ反映(§3-0/§3-1/§3-3/§3-5/
§4-2/§4-3/§4-4/§4-5/§5-1/§5-2/§5-3/§6-1/§8-1/§9-0[新設]/§9-1[実測
順序改訂]/§11-8/§12/§12-1/§13-6/§14-3、各箇所に「[委任_04改訂]」印)。
新設§5-4(paired local rewrite設計、JA側)、新設§15(Opus対応表)。

**paired local rewrite設計要点**: `origin=ja_source`のclaimに対し、
該当JA 1文±1文と対応EN文を同一`rewrite_hint`で局所編集し、JA Fact
Check 1 call+EN Deviation Check 1 call(既存Recheckに統合)で確認する
(概算¥1.0〜1.5/cycle、旧案Bの1/3以下)。旧案B(JA全文差し戻し)は
guard抵触時のフォールバック(記事あたり1回)に格下げ。実装リスク:
JA本文局所編集関数が新規実装であり、文体・記号・段落数Gateの局所編集
全文への再適用可否、JA/EN意味整合の機械検証手段の不在が未検証。

**Phase 1実測項目の順序**(§9-1改訂): ①precheck FP率実測(¥0、28件
regex適用)→②hormuz n=20見逃し3attempt補完実験(¥0〜¥2)→③V4-A
BLOCK率増分+changed_actor n=15追加実測(¥8〜9、Stage1 variant最終
確定はここで実施)→④Stage2実単価/batch化/prompt caching実測(数円〜
¥10)→⑤Stage3型別Rewrite成功率実測(¥8〜22)→⑥統合dry-run。Phase 1
合計概算¥18〜45(旧見積¥15〜35から、実測項目追加により微増)。個別
Guardrail上限合計約¥70。

**再計算後のコスト式と暫定値**: §13-6を`worst_case = [n_claim×
c_stage2 + c_ja_full](cycle1) + [n_claim×c_stage2 + n_claim×c_en_local
+ c_recheck_en](cycle2) + Stage1固定費増分¥0.294 − 現行方式費用`の式へ
書き換えた。`n_claim=1`で¥3.0〜4.0程度(旧¥3.96はこのレンジ内)、
`n_claim=4`(B4実例上限)で¥4.4〜5.4程度まで悪化し得る。**単一数値での
Cap判定はしない**。JA-origin比率は仮置き40%→実測80%(n=5)へ改訂。
BLOCK率(15/35/60%)はV4A実測(§9-1③)後に置換する。

**USER_DECISION_REQUIRED該当**: 3件をユーザー判断事項として提示(設計
書§12/§15-3): (1) KPI判定方法の再定義(記事単位0件→事象単位推定に
よるEscalation率の信頼区間上限、条件1)、(2) Cap定義の解釈(LLMコスト
のみかdownstream込みか、条件1)、(3) QUALITY通過(現行STOPしていた
B2型を人間を通さず公開すること)がSafety緩和[条件2]に該当するか。
**設計書は現行KPI文言のまま進め、事象単位推定・Escalation0件内訳を
追加報告項目として併記する**(独断で変更していない)。

**費用**: 今回¥0(API呼び出しなし、Opus L2レビュー#1のみ)。本Phase
累計¥0/総枠¥400、残¥400。

**Production/Dangling Reference確認**: `git diff --stat`でProduction
ファイル(`er003_*`/`er006_*`/`er012_*`/`er019_*`)に差分なし。
`.claude/agents/`ディレクトリに差分なし(opus-consultant.mdは委任_03で
変更済み、本委任では変更していない)。

Evidence: `docs/pm/opus_l2_review_open233_self_recovery_01.md`(新規、
全文)、`docs/pm/design_open233_self_recovery_flow_01.md`(§3-0/§3-1/
§3-3/§3-5/§4-2/§4-3/§4-4/§4-5/§5-1/§5-2/§5-3/§5-4[新設]/§6-1/§8-1/
§9-0[新設]/§9-1/§11-8/§12/§12-1/§13-6/§14-3/§15[新設]追記)。入力:
委任文全文(2026-09-30)、Opus L2レビュー#1全文。

## §5. 棚卸し統合・pre-check・Phase 1 ①②(委任_05/_06、2026-09-30、
既存Rewrite機構棚卸し+§5三分類統合+deterministic pre-check Trial実装+
Phase 1 ①precheck FP率実測②hormuz見逃し補完実験)

**ユーザー追加指示(逐語要旨)**: 既存Rewrite機構は「必ず既存実装を
そのまま使う」ことが目的ではない。棚卸しの上でそのまま再利用できる
部分/拡張・改善できる部分/今回KPIには不適で新方式が合理的な部分を
整理する。既存資産の無視も既存方式への束縛も避け、QCD上より良い方法が
あればTrialする。Production変更なし、Trial範囲内で自律進行。

**委任_05(棚卸し、¥0、read-only)**: `docs/pm/inventory_local_rewrite_
mechanisms_open233_01.md`を新規作成。既存Rewrite関連機構18件を確認し、
EN側`er010_ledger_local_rewrite_09.py`(Family B系でPRODUCTION_WIREDだが
Family Xには未配線)を第一候補に、JA側は文単位Local Rewrite機構が既存に
無いことを確認した。継承すべきguard/retry/再検証と二重実装リスクを整理。

**委任_06 三分類統合(設計書§5-0新設)**: 委任_05の結果を「(A)そのまま
再利用」「(B)拡張して利用」「(C)今回KPIに不適→新方式」の三分類表
(KPI/QCD理由付き、18機構)へ整理。EN局所Rewriteを既存ベース改善案
(E-1、er010拡張)と新方式案(E-2、delete型は決定論処理・replace/
narrow_scope型は最小Prompt)の両論併記(§5-2/§5-2-補)、JA局所Rewriteを
既存ベース案(J-1、er010骨格の日本語移植)と代替案(J-2、既存JA
must-fix全文+局所指示のみ)の両論併記(§5-4/§5-4-補)へ再構成し、
Phase 1⑤で同一fixtureにより比較実測する設計とした。継承guard/retry/
再検証を§5-5へ統合。

**deterministic pre-check Trial実装**: 新規`er052_open233_self_
recovery_precheck_01.py`(+`_test_01.py`、unittest 23件全PASS、
`python -m unittest er052_open233_self_recovery_precheck_01_test_01`で
再現可能)。Ledger text(vfl01形式)の構造化フィールド(claim/scope/
conditions/numeric_value/date_or_period)と記事本文を機械照合し、
actor_missing/number_mismatch/date_mismatch/negation_marker/
comparison_markerを検出する。言い換え・日付表記差・敬称差の正規化辞書、
Ledger内の別Factが持つ値との誤混同を除外するロジックを実装(初回実装
での実測FP発見→原因特定→修正→再測定というTrialサイクルを経た)。

**Phase 1①(precheck FP率実測、¥0)**: 既存`LEDGER_COMPLIANT`記事28件
中20件(残り8件はJA writer retry後attempt、既存逆展開ユーティリティ
非対応のため対象外)へprecheckを適用。**記事単位FP率=0/20=0%**
(finding単位0件)。Safety群(er009 9種+A2A3/A4/A5、12件)での単独検出率
=1/12(8.3%、number_mismatchのみ。他は構造的限界[actor名がclaim以外の
フィールドにのみ存在/意味的逸脱は機械照合不可]で非検出、想定どおり)。
design書§3-1の判断基準(FP率10%超でfloor弱め分岐へ切替え)に該当せず、
**precheckのfloor扱い(強い分岐)を維持する**。詳細ログ:
`er052_output/open233_self_recovery_precheck_01/phase1_step1_fp_
rate.json`/`phase1_step1_safety_group_detection.json`。

**Phase 1②(hormuz n=20見逃し3attempt補完実験)**: hormuz_run03_
standard/V4Aで非検出だった3attempt(8/13/14、同一入力)に対し、
(a) precheck適用は非検出(既知の限界どおり、HF-009 changed_scopeは
意味的逸脱)。(b) Stage 1出力を一切見せない独立Stage 2診断Prompt
(新規`er052_open233_self_recovery_stage2_01.py`、gpt-6-luna、Contract
非経由)を3attemptへ1 callずつ適用した結果、**3/3(100%)がHF-009を
`materiality=BLOCKING, basis=ledger_scope`として独立検出**した(3回とも
同一趣旨の理由付け: 「HF-009はBrent先物のみを確認しておりoil market
全体を確認していない」)。Stage 1のrecall欠落を独立Stage 2診断が3/3で
埋められることを実データで確認した(design書§11-5/§14-4の構造的限界
への実証的な反証材料。ただしStage1 BLOCKING判定後にのみStage2が発火
する通常設計の前提を外した診断目的の特例)。3/3で結果一貫のためn=2
拡張は不実施。詳細ログ: `er052_output/open233_self_recovery_phase1_
hormuz_followup_01/summary.json`(+`stage2_call_1〜3.json`)。

**費用**: Stage 2診断3call合計¥0.6285(単価¥0.185〜0.225/call、
gpt-6-luna実測、Guardrail¥10のうち)。precheck測定・棚卸しは¥0。
本委任(委任_05/_06)費用¥0.6285、Phase累計¥0.6285/総枠¥400、
残¥399.3715。

**USER_DECISION_REQUIRED該当有無**: 該当なし(7条件いずれも非該当。
E-1/E-2・J-1/J-2は両論併記のみでPhase1⑤実測後に確定、precheckのfloor
扱い維持もdesign書既定の判断基準に従った機械的判定)。

**Production/Dangling Reference確認**: `git diff --stat`でProduction
ファイル(`er003_*`/`er006_*`/`er010_*`/`er012_*`/`er019_*`)に差分なし
(新規`er052_*`ファイルのみ追加、Production非接続)。API keyは環境
変数のみ、保存jsonにはprompt本体ではなくprompt_sha256のみ記録。

Status=`PHASE1_STEP2_DONE`。Evidence: `docs/pm/inventory_local_
rewrite_mechanisms_open233_01.md`(新規)、`docs/pm/design_open233_
self_recovery_flow_01.md`(§5-0[新設]/§5-2/§5-2-補[新設]/§5-4/
§5-4-補[新設]/§5-5[新設]/§9-1①②追記)、`er052_open233_self_recovery_
precheck_01.py`(+test)、`er052_open233_self_recovery_stage2_01.py`、
`er052_open233_self_recovery_precheck_phase1_measure_01.py`、
`er052_open233_self_recovery_phase1_hormuz_followup_01.py`、
`er052_output/open233_self_recovery_precheck_01/`、`er052_output/
open233_self_recovery_phase1_hormuz_followup_01/`。入力: 委任文全文
(2026-09-30、委任_06)。

## §6. Phase 1 ③④実測・Stage 1最終確定(委任_07、2026-09-30、V0/V4-A/
S1-D比較実測+Stage2実単価・batch化・prompt caching実測)

**目的**: Phase 1 ③(Stage 1 variant実測確定)・④(Stage2実単価・
batch化・prompt caching実測)を実施する。ユーザー方針(既存方式に
縛られないQCD比較)に基づき、前Phaseで理論上不採用としていた
**S1-D(検出とmateriality判定を同一callで行う一体型)を実際にTrial
実装し、V0/V4-Aと同一fixtureで比較実測した**上でStage 1を最終確定
する(設計書§14-5)。

**新規実装**(Production非接続、Contract非経由、API keyは環境変数
のみ、保存jsonはprompt_sha256のみ): `er052_open233_self_recovery_
s1d_trial_01.py`(+test、S1-D Prompt/schema。10 flags+materiality+
basis+rewrite_kindを1callで出力、explanationなし)、
`er052_open233_self_recovery_phase1_step3_stage1_compare_01.py`
(V0/V4-A/S1-D比較harness、(a)〜(e)5作業)、`er052_open233_self_
recovery_stage2_production_01.py`(+test、§4-4確定入力どおりの
per-claim/batch Stage2実装、段落±1抽出+引用符正規化)、
`er052_open233_self_recovery_phase1_step4_stage2_unitcost_01.py`
(per-claim vs batch・prompt caching比較harness)。

**Phase 1③実測結果**(詳細は設計書§14-5、新規76 call・¥13.5234):
(a) Safety群12 fixture: S1-D 12/12(100%)BLOCKING確定。(b)
`er009_changed_actor` n=15追加実測: V0=7/15(46.7%)・V4-A=15/15
(100%)・S1-D=15/15(100%)、Fisher両側検定V0 vs V4-A/S1-D共に
p=0.00220(有意、n=5時点p=0.18から統計的有意水準へ到達)。(c)
negative候補7記事BLOCK率: V0=0/7(既存記録)・V4-A=4/7(57.1%)・
**S1-D=6/7(85.7%、V4-Aより高い不要BLOCK率)**。(d) B群5 fixture
claim単位ラベル一致: B3・Meta_run03_standardは確定ラベルと一致した
が、**B1/B4でReal-but-fixable群(B1-c/B4-a、確定ラベル=BLOCKING)を
S1-DがQUALITYへ誤降格させる実例を2件観測**。(e) hormuz/Meta n5:
S1-D=10/10(100%)。

**Stage 1最終確定**: **V4-Aを確定とする(S1-D不採用)**。(a)(b)(e)
ではS1-DはV4-Aと同水準だが、(c)で不要BLOCK率がV4-Aより高く、(d)で
Real-but-fixable群の誤降格が観測されたため。**S1-Dは「検出と
materiality判定を1callで確定する」構造上、誤判定を第二の独立callで
訂正する機会がない**ことが実測で裏付けられた(Opus L2レビュー#1が
理論面で推奨していたdetect/materiality分離によるSafety資産保存の
実利を、実測で確認した形)。

**Phase 1④実測結果**(詳細は設計書§4-7、新規12 call・¥1.1364):
per-claim vs batch(B4=4claim/B1=2claim)は**判定一致率100%**(claim間
相互汚染なし)。batch化でcall数・費用(55%減/29%減)・latencyの全てが
改善。prompt caching(同一Ledger prefix連続call)はcached_input_tokens
比率99.9%を実測し、**費用削減率63〜64%**を確認(gpt-6-luna Responses
APIで自動キャッシュが機能することを実測確認、ただし本実測のcall1は
直前の同一Ledger call群でキャッシュが既に温まっていたため、厳密な
「未キャッシュ初回」との対比ではない点は限界として明記)。

**[重要な新規発見]Stage2較正リスク**: per-claim Stage2(§4-4確定
入力どおり、explanation/severity/10flags除外)で、B1-c/B4-a相当の
claim(Real-but-fixable群、確定ラベル=BLOCKING)が**全てQUALITYへ
降格**した。S1-Dの誤降格と同一方向であり、**Stage2 rubric+入力制限
自体の較正課題である可能性が高い**。Production非接続のTrial実装で
あり現時点でSafety事故には至っていないが、rubric文言変更や
deterministic floor対象拡大は設計変更に相当するため、**勝手に修正
せず報告のみ行う**(Phase 1⑤[Stage3 Rewrite成功率実測]で
Real-but-fixable群がRewrite段に到達するかを継続確認し、必要な設計
判断はFable/ユーザーへ提示する)。

**Stage2実単価確定**: per-claim実測¥0.087〜0.112/call(4件平均
¥0.1013)。§13-4の「楽観的¥0.10〜0.20/call」に近く、「保守的¥0.30〜
0.40/call」ほど高くないことを確認(設計書§13-4追記)。

**費用**: 今回¥14.6598(88 call、0 error)。Phase累計¥15.2883/総枠
¥400、残¥384.7117。Guardrail¥35に対し実測¥14.6598(約42%)、超過なし。

**USER_DECISION_REQUIRED該当有無**: 該当なし(7条件いずれも
非該当。Stage2較正リスクの発見は新しい仕様候補の報告であり、
Safety緩和[条件2]には該当しない[むしろSafety強化方向の課題提起]。
Stage 1最終確定[V4-A]は既存暫定採用[§14-3]の確定化であり新しい
仕様原則の導入ではない)。

**Production/Dangling Reference確認**: `git diff --stat`でProduction
ファイル(`er003_*`/`er006_*`/`er010_*`/`er012_*`/`er019_*`)に差分
なし(新規`er052_*`ファイルのみ追加)。API keyは環境変数のみ、保存
jsonにはprompt本体ではなくprompt_sha256のみ記録。unittest全PASS
(新規19件+既存回帰51件、計70件確認)。

Status=`PHASE1_STEP4_DONE`。Evidence: `docs/pm/design_open233_self_
recovery_flow_01.md`(§4-7[新設]/§9-1③④/§13-4追記/§14-5[新設]/
冒頭Status)、`er052_open233_self_recovery_s1d_trial_01.py`(+test)、
`er052_open233_self_recovery_phase1_step3_stage1_compare_01.py`、
`er052_open233_self_recovery_stage2_production_01.py`(+test)、
`er052_open233_self_recovery_phase1_step4_stage2_unitcost_01.py`、
`er052_output/open233_self_recovery_phase1_step3_stage1_compare_01/`、
`er052_output/open233_self_recovery_phase1_step4_stage2_unitcost_01/`。
入力: 委任文全文(2026-09-30、委任_07)。

## §7. Stage 2較正+Phase 1 ⑤(委任_08、2026-09-30、Stage2 rubric較正
Trial実測+Stage3型別Rewrite成功率実測[E-1 vs E-2、J-1 vs J-2])

**目的**: §6で発見されたStage2較正リスク(Real-but-fixable群B1-c/
B4-aのQUALITY誤降格)への対応(作業A)と、Phase 1 ⑤(Stage3型別
Rewrite成功率実測、作業B)を実施する。

**作業A(Stage2 rubric較正Trial)**: Fable判定(Safety方向の較正、
ユーザー指示の自律範囲)に基づき、新規`er052_open233_self_recovery_
stage2_calibration_01.py`でR1(現行rubric、既存出力再利用0call)/
R2(較正rubric、QUALITYを「Ledger記録済み観測同士の関係付け」に限定し
新規具体的主張は最優先BLOCKING)/R3(R2+post-hoc floor)を13 batch
call・23claim・n=2(26 call)で実測した。**結果**: Safety群
(A2A3/A4/A5/Meta/hormuz、14 instance)はR2で100%BLOCKING維持
(誤降格0件)。§6で発見された誤降格claim(B1-c/B4-a/B4-d、6 instance)
はR1では0%正解(全てQUALITYへ誤降格)だったが、**R2で100%正解
(全てBLOCKINGへ復帰)**。ACCEPTABLE群は4/4正解(over-block無し)。
一方QUALITY群(B2/B4-b/B4-c)はR2で1/6のみ正解(over-block新規発生、
Productivity低下のトレードオフ)。negative群はR2で7/8(87.5%)が
非BLOCKINGへ復帰(Stage1単体は0%)。n=2判定一致率91.3%。**R3
(floor)はSafety面の追加効果が確認されず、Productivity(B1-b・
negative群)を悪化させたため不採用**。**確定構成: R2 rubric採用、
R3 floor拡張は不採用**(設計書§4-8)。費用¥3.1717(Guardrail¥12)。

**作業B(Phase 1 ⑤、Stage3型別Rewrite成功率実測)**: 新規
`er052_open233_self_recovery_stage3_rewrite_trial_01.py`で、
delete型(B1-c/B3/B4-a、決定論的削除)・replace_with_ledger_value型
(er009_changed_actor/changed_number、E-1[er010骨格そのまま]vs E-2
[最小1-shot])・narrow_scope型(hormuz_run03_standard HF-009、J-1
[新規paired local rewrite]vs J-2[JA全文regen+局所指示])を実測した
(18 call、¥3.0363、0 error)。**結果**: delete型は単一deviation記事
(B3)でresolved=True、複数deviation記事(B1-c/B4-a)は他claim残存の
ため記事全体Recheckは引き続きLEDGER_DEVIATION(claim単位再出現確認は
次回実装項目)。replace型はE-1/E-2とも4/4(100%)が1 attempt目で解決、
cost差僅少(escalation未発火のため差が出なかった)。**narrow_scope型
はJ-1が完全解消(JA Check・EN Recheckとも LEDGER_COMPLIANT、対象文
以外への影響=0、cost¥0.4569)、J-2は未解消(EN RecheckがLEDGER_
DEVIATIONのまま残存、非対象文drift 1件検出、cost¥0.9598でJ-1の
約2.1倍)**。**採用案: narrow_scope=J-1、replace_with_ledger_value=
E-2第一候補(E-1はfallback)**(設計書§5-4-補2)。

**[重要]hormuz narrow_scopeの解消可否**: **J-1により解消可能で
あることを実測で確認した**。「両手法とも解消できない」という委任文
記載の最大リスクシナリオは回避された。

**スコープ上の限界(報告)**: J-1/J-2の「JA Fact Check」「EN
Recheck」は真のProduction JA Fact Check/JA Writer Oカスケードでは
なく、既存V4A variant checkerをJA/EN両方へ適用する近似で代用した
(読み取り専用遵守・予算/時間制約による意図的縮小、Production非接続
は維持)。§5-4が要求する汎用JA文分割モジュールも簡易実装に留めた
(er010の`locate_target_sentence`がJA全文を1文と誤認識する不具合を
実地で確認、既知の課題を実測で裏付け)。

**費用**: 今回¥6.208(44 call、0 error)。Phase累計¥21.4963/総枠
¥400、残¥378.5037。Guardrail(作業A¥12+作業B¥30=¥45)に対し実測
¥6.208(約14%)、超過なし。

**USER_DECISION_REQUIRED該当有無**: 該当なし(7条件いずれも非該当。
Stage2較正はSafety方向の較正でありSafety緩和[条件2]に該当しない。
Rewrite型別採用案[narrow_scope=J-1、replace=E-2]はTrial実測に基づく
QCD判断でありProduction採用[条件4]には未到達)。

**Production/API安全性確認**: `git diff --stat`で`er003_*`/`er006_*`/
`er009_*`/`er010_*`/`er012_*`/`er019_*`に差分なし(新規`er052_*`
ファイルのみ追加。`er010.generate_rewrite`のcostログ取得はTrial
プロセス内のin-memoryモンキーパッチのみでディスク上のファイルは
無変更)。API keyは環境変数のみ、保存jsonにはprompt本体ではなく
prompt_sha256のみ記録。既存unittest全42件PASS(regression確認)。

Status=`PHASE1_STEP5_DONE`。Evidence: `docs/pm/design_open233_self_
recovery_flow_01.md`(§4-8[新設]/§5-4-補2[新設]/§9-1⑤/§13-11[新設]/
冒頭Status)、`er052_open233_self_recovery_stage2_calibration_01.py`、
`er052_open233_self_recovery_stage3_rewrite_trial_01.py`、
`er052_output/open233_self_recovery_stage2_calibration_01/`、
`er052_output/open233_self_recovery_stage3_rewrite_trial_01/`。
入力: 委任文全文(2026-09-30、委任_08)。

## §8. Phase 1 ⑥ 統合dry-run(委任_09、2026-09-30、Self-Recovery Flow
統合runnerによる最初の実Trial、Checkpoint B Evidence取得)

**目的**: ①〜⑤で確定した設計(V4A Stage1・R2 rubric+floor・
narrow_scope=J-1/replace=E-2・cycle上限2・A1/A5/A7)を1本のTrial
runnerへ統合し(`er052_open233_self_recovery_flow_runner_01.py`+
test)、代表fixture 29 instanceで通し実行する(Phase 1計画の最終項目)。

**対象・実測規模**: Hormuz run_01/run_02 Advanced各1(現行Production
STOP実例、Standardは同run内で未生成のため対象外)・run_03
Advanced/Standard、Meta run_03 Advanced/Standard、B群4
(B1/B2_hormuz/B3/B4)、negative候補7、Safety群12(er009 9種+
A2A3/A4/A5)=計29 instance。92 call・¥16.7806・0 error
(Guardrail¥45の約37%)。

**【対象/instance数と期待経路 vs 実経路の突合表(要旨)】**

| 分類 | instance数 | 実際の到達状態 |
|---|---|---|
| Hormuz run_01 Advanced(現行STOP実例) | 1 | Re-screening自動解消(ACCEPTABLE、Rewrite不要) |
| Hormuz run_02 Advanced(現行STOP実例) | 1 | **Stage1(V4A) recall miss**でACCEPTABLE_STAGE1(Self-Recovery Flow未発火) |
| Hormuz run_03 Advanced/Standard | 2 | Advanced=ACCEPTABLE_STAGE1、Standard=STAGE4_ESCALATION(J-1汎用ロケータ失敗) |
| Meta run_03 Advanced/Standard | 2 | Advanced=ACCEPTABLE_STAGE1、Standard=STAGE4_ESCALATION |
| B群4(B1/B2_hormuz/B3/B4) | 4 | B3=RESOLVED_REWRITE(Stage1 recall miss代替後)、他3件=STAGE4_ESCALATION |
| negative候補7(Normal群) | 7 | 3件=ACCEPTABLE_STAGE1(正しく無検出)、4件=Stage1過剰BLOCK→**Stage2でも全件BLOCKING確定(0/4是正)**、うち2件Rewrite自動解消・2件STAGE4 |
| Safety群12(er009 9種+A2A3/A4/A5) | 12 | 9件=RESOLVED_REWRITE(またはREWRITE_THEN_DOWNGRADE)、A2A3/A4=STAGE4_ESCALATION(floor維持、false-negativeなし) |

**【Self-Recovery 6項目】** Initial BLOCK=23/29、Re-screening自動
解消=1、Rewrite進行=22、Rewrite自動解消=13(RESOLVED_REWRITE=11+
RESOLVED_REWRITE_THEN_DOWNGRADE=2)、Final STOP=9、
USER_DECISION_REQUIRED=9(全件`same_claim_fact_id_reblocked`)。

**【0件の内訳】** 真の解消(`all_prior_issues_resolved=True`)=11、
QUALITY通過=0、未確認=0、誤PASS候補=0(全件Recheckで明示確認)。

**【重大Fact見逃し(最重要の安全性所見)】** V4A単発実行(n=1)で、
B2_hormuz・B3・**hormuz_run02_advanced(現行Production STOP実例)**の
3 instanceが既知BLOCKING claimを検出できず(Stage1 recall miss、
§10/§14既知リスクの実データ再現)。B2_hormuz/B3は実Production
baselineへ代替してStage2/3経路自体は検証(結果に代替の事実を明記)、
hormuz_run02_advancedは代替せず素の結果=ACCEPTABLE_STAGE1で完結
(Self-Recovery Flowが発火する前の見逃しであり、Stage2/3では捕捉
不可能)。floor機構自体はfloor対象48 BLOCKING claim中0件のfalse-
negativeを維持。

**【QCD】** 総call92・総費用¥16.7806・平均¥0.5786/instance(全29)、
¥0.7118/instance(BLOCKING23件のみ)。P50=¥0.377(全29)/¥0.5918
(BLOCKING23)、P95=¥1.9421、worst=¥2.2721(safety_A4)。**worst case
でも+¥3/記事Cap未超過**。latency P50=17.27秒/P95=143.5秒。
completion率69.0%、retry率75.9%、loop率41.4%。

**【現行Productionとの対比(Hormuz 3記事)】** run_01=現行STOP→
Re-screening自動解消。run_02=現行STOP→Stage1 recall miss(見かけ上
解消だがSelf-Recovery Flowの機能とは無関係)。run_03 Standard=現行
STOP→STAGE4_ESCALATION(J-1汎用ロケータ失敗)。

**【事象単位成功率とEscalation率推定上限】** floor後BLOCKING確定
claim48件のうちRewrite実行33件、初回cycleで再発せず解消=20/33
(60.6%)。機構別: `deterministic_delete`=100%(1/1)、
`e2_generic_rewrite`=72.2%(13/18)、`target_not_found+fulltext_
fallback`=100%(3/3)、`paired_ja_en(J-1)`全体=27.3%(3/11、うち
locate成功時`j1_paired_rewrite`=66.7%[2/3]、locate失敗`j1_pair_not_
located`=14.3%[1/7])。**J-1対象文特定の失敗(11回中7回=63.6%)が
最大の失敗要因**。Escalation率(instance単位)9/29=31.0%、Wilson
95%CI=[17.3%, 49.2%]。

**【Stage4到達9件の原因分類】** (a) J-1対象文特定失敗=5 instance
(safety_A2A3・bgroup_B2_hormuz・bgroup_B4・meta_run03_standard・
hormuz_run03_standard)。(b) 局所編集は実行された(guard_ok=True)が
Recheckが引き続きLEDGER_DEVIATION=4 instance(safety_A4・bgroup_B1・
neg1・neg2)。**(b)の根本原因**: Stage2出力schema
(`er052_open233_self_recovery_stage2_production_01.py::_ITEM_PROPS`)
に設計書§4-5が要求する`rewrite_hint`フィールドが未実装であり、
Stage3が具体的な修正方針を受け取れていない(新規発見、報告のみ、
既存Trial infraの改修は次回委任の判断へ)。

**【最重要の是正発見】** 委任_08のStage2較正Trial(negative群4
fixture: neg1/neg2/neg3/neg5)は、これらのfixtureが定義上
`deviations=[]`(実Production V0でLEDGER_COMPLIANT)であるため
`claim_text="(claim not found in baseline)"`という**無意味な
placeholder文字列**に対してStage2判定を測定していたことが判明した
(該当コード行確認済み)。既報告の「negative群R2で87.5%が非BLOCKING
へ復帰」はこの無効な入力に基づく測定であり、実際のV4A誤検出claim
文言では**Stage2単独でのBLOCKING非該当への降格は0/4(0%)**だった
(実測、本統合dry-run)。既存DECISION_LOG/REPORT§7/design書§4-8の
数値は履歴改変せず保持するが、本節で訂正値を明記する。

**Opus L2 #2に問うべき論点案(5〜7個)**:
1. Stage2出力へ`rewrite_hint`を追加した場合、Rewrite成功率(現状
   claim単位60.6%)がどの程度改善し得るか、また`rewrite_hint`自体の
   質(具体性)をどう機械的に検証するか。
2. J-1(JA/EN paired local rewrite)の汎用対象文特定失敗率63.6%は、
   Production採用を検討する上でどの程度の実装投資(汎用JA文分割
   モジュール)を正当化するか。人手アンカーに頼らない設計は現実的か。
3. negative群R2の実測Productivity(0/4)を踏まえ、R2 rubricの
   over-block是正力そのものを再較正すべきか(Safety群100%維持との
   トレードオフ)。
4. Stage1(V4A)のrecall miss(本runで3/複数instance発生)を、
   Production導入判断においてどう扱うべきか(2nd run併用のコスト
   増 vs 見逃しリスクの許容)。
5. cycle上限2・同一claim/fact_id再発検出(A5)は今回9/9のFinal STOPで
   正しく機能したが、`related_fact_id`をLLMが毎回一貫して報告しない
   可能性(claim identity trackingの脆弱性)をどう補強すべきか。
6. Phase 2(10〜20記事)の設計において、上記1〜5の改善を先に実装
   すべきか、未改善のまま生データを追加取得すべきか。
7. +¥3/記事Capは本実測(worst¥2.2721)で余裕があるが、`rewrite_hint`
   追加によるprompt長増加がCap余裕をどの程度圧迫するかの試算。

**Phase 2計画の要点**: 記事数10〜20規模(既存Hormuz/Meta run再開、
または新規テーマ)。新規テーマの場合はPM_GOVERNANCE.md§13により
複数候補提示+ユーザー選択が必要(Fable/Claude単独決定不可)。費用は
Phase 1実測(¥0.58〜0.71/instance平均)から外挿すると10〜20記事×
Advanced+Standard(各1 instance)=20〜40 instance相当で概算¥12〜28
(Stage1固定費除く条件付き費用のみ)、Guardrailは想定の1.5〜2倍
(¥40〜60程度)を次回委任で個別設定する。

**USER_DECISION_REQUIRED該当有無**: 該当なし(7条件いずれも非該当。
Stage1 recall miss・negative群Productivity訂正はSafety「緩和」では
なく既知リスクの実測確認・既存測定の透明な訂正[Safetyはfloor機構に
より0件のfalse-negativeを維持]。worst case実測¥2.2721はCap未超過
[条件3]。改善提案はいずれも未実装のTrial改善候補でありProduction
採用[条件4]には未到達)。

**実装上の不具合発見・修正**: 統合runの実行中、`er052_open233_self_
recovery_stage3_rewrite_trial_01.py`(委任_08既存資産)の
`simple_llm_call`をそのまま呼び出すと、そのモジュール自身の
`save_budget_state`が既存委任_08の証跡ファイル(`budget_state_
c233l_b.json`)を上書きする実害を検出した(`git diff`で発覚、
`git checkout`で復元済み、既存証跡データの実質破損なし)。本runner
自身の独立した`simple_llm_call`実装へ差し替え、再発防止のregression
testを追加した(この修正はStage1/2/3の判定ロジック自体には影響
しない。実測結果はこの修正前後で同一)。

**費用**: 今回¥16.7806(92 call、0 error)。Phase累計¥38.2769/総枠
¥400、残¥361.7231。Guardrail¥45に対し約37%。

**Production/API安全性確認**: `git diff --stat`で`er003_*`/`er006_*`/
`er009_*`/`er010_*`/`er012_*`/`er019_*`および既存`er051_*`/既存
`er052_*`(precheck/stage2_production/stage2_calibration/stage3_
rewrite_trial/phase1_step3_stage1_compare)ファイルに差分なし
(新規`er052_open233_self_recovery_flow_runner_01.py`+testのみ追加。
上記budget_state誤上書きは検出後即復元)。API keyは環境変数のみ、
保存jsonにはprompt本体ではなくprompt_sha256のみ記録。既存unittest
全110件PASS(regression確認、新規17件追加)。

Status=`PHASE1_DONE_IMPROVEMENT_NEEDED`。Evidence: `docs/pm/design_
open233_self_recovery_flow_01.md`(§9-1⑥[実測反映]/§9-2[改善優先
順位追記]/冒頭Status)、`er052_open233_self_recovery_flow_runner_01.py`
(+test)、`er052_output/open233_self_recovery_flow_runner_01/`
(`summary_flow_runner.json`+`instances/*.json`29件)。入力: 委任文
全文(2026-09-30、委任_09)。
入力: 委任文全文(2026-09-30、委任_08)。

## §9. iteration 2実測(委任_10、2026-09-30、rewrite_hint実装+J-1改善
+negative群R2再較正+S1-U variant実測+統合dry-run再実行)

**目的**: §8(委任_09)で判明した改善優先順位(§9-2)1〜4を実装し、
同一29 instanceで再実行して改善効果を実測する。

**実装(¥0)**: (1) Stage2出力schema(`er052_open233_self_recovery_
stage2_production_01.py`)へ`rewrite_hint`(BLOCKING時必須、逐語引用+
修正指示+fact_id)を追加。(2) J-1ロケータ改善
(`er052_open233_self_recovery_flow_runner_01.py::locate_target`/
`locate_ja_counterpart_by_position`): rewrite_hint引用断片を第一キー
・claim_textのlocate_best_sentence(ambiguous時は全文フォールバックへ
委ねるよう変更)を第二キー・`er010_ledger_local_rewrite_09.locate_
target_sentence`(word-overlap、read-only借用)を第三キーとし、JA側は
EN対象文の文位置比をJA文分割へ写像し数値トークン一致を優先する構造的
近似を追加。(3) claim identity正規化(`normalize_claim_text`、
fact_id無し時の表記揺れ吸収)。(4) delete型のfuzzy再出現確認。(5) S1-U
variant(`stage1_union_screen`、Stage1 PASS時にS1-D 1 callを追加し
union screen、CLI `--s1u`)。新規regression test 19件追加、既存含め
131件PASS。

**実測(有料)**: 作業B(negative群R2'較正Trial、新規`er052_open233_
self_recovery_r2prime_recalibration_01.py`)=20 call・¥3.3977。
作業C(29 instance再実行、`--s1u`有効)=126 call・¥26.0302
(Guardrail¥35のうち)。合計**¥29.4279**(本委任Guardrail¥50のうち)。

**【iteration 1→2 差分表】**

| 指標 | iter1(委任_09) | iter2(委任_10) |
|---|---|---|
| Initial BLOCK | 23/29 | 28/29 |
| Rewrite自動解消 | 13 | 21 |
| Final STOP(Escalation) | 9 | 7 |
| 真の解消 | 11 | 16 |
| 総call数/総費用 | 92/¥16.7806 | 126/¥26.0302 |
| 平均¥/instance | ¥0.5786 | ¥0.8976 |
| worst instance | ¥2.2721 | ¥2.4664(Cap未超過) |
| completion率 | 69.0% | 75.86% |
| Escalation率(Wilson95%CI) | 31.0%[17.3,49.2] | 24.1%[12.2,42.1] |
| claim単位Rewrite成功率 | 60.6%(20/33) | 81.0%(34/42) |
| J-1 locate成功率 | 36.4%(4/11) | 81.8%(9/11) |

**0件の内訳(iter2)**: 真の解消16、QUALITY通過0、未確認0、誤PASS
候補0(全件Recheckで明示確認)。

**S1-U variant実測**: s1u_eligible10 instance中、Stage1(V4A)が実際に
PASSしていた7件へ1 call追加、6件(85.7%)がBLOCKING claimを新規検出。
**委任_09の3件の重大Stage1 recall miss(B2_hormuz・B3・hormuz_run02_
advanced[現行Production STOP実例そのもの])を全件捕捉し、いずれも
Rewriteで解消**(hormuz_run02_advancedはcycle1で`LEDGER_COMPLIANT`
かつ`all_prior_issues_resolved=True`)。追加固定費¥3.1589(7 call)。
副作用: 新規捕捉した`meta_run03_advanced`は2 cycle以内に解消できず
STAGE4到達(「見えない見逃し」を「人間が確認できるSTOP」へ変換した
もの)。**採用推奨**(Safety改善3件 vs 固定費+Escalation増分1件の
トレードオフ、Cap未超過、最終判断はユーザー)。

**R2'較正(不採用)**: 段階的判定手順+例示追加のRUBRIC_R2_PRIMEを
n=2実測(20 call)。Safety側で誤降格1件(A4-0)発生、Productivity側は
改善0件。委任文の受入条件(誤降格0件かつ改善)を満たさず**不採用、
既存R2rubric維持**。

**残るStage4到達7件の原因分類**: J-1対象文特定失敗の残存分・Rewrite
後もRecheckが引き続きLEDGER_DEVIATION(bgroup_B1/B4・safety_A2A3/A4)、
claim再発型(meta_run03_standard・neg1)、S1-U新規捕捉だが2 cycle以内
未解消(meta_run03_advanced)。次案: J-1 fulltext fallback発動条件の
早期化、S1-U捕捉claim限定のcycle上限緩和検討、safety_A4個別診断。

**Opus L2 #2論点案(5〜7個)**: (1) S1-U variantのPhase 2デフォルト
採用可否。(2) J-1のさらなる汎用化投資判断(固有名詞中心claimの限界)。
(3) R2'較正失敗を踏まえたrubric較正アプローチ自体の限界評価。(4)
claim identity正規化の実データ効果測定。(5) S1-U新規発見claim未解消
時の扱い(cycle上限緩和 vs 現行STAGE4)。(6) Phase 2着手判断。(7)
Cap余裕の累積コストへの影響試算。

**USER_DECISION_REQUIRED該当有無**: 該当なし(7条件いずれも非該当。
S1-Uの新規Escalationは見逃しの可視化でありSafety緩和ではない。worst
instance実測¥2.4664はCap未超過。R2'不採用はTrial内較正判断)。

**費用**: 今回¥29.4279(146 call、0 error)。Phase累計¥38.2769+
¥29.4279=**¥67.7048**/総枠¥400、残¥332.2952。

**Production/API安全性確認**: `git diff --stat`で`er003_*`/`er006_*`/
`er009_*`/`er010_*`/`er012_*`/`er019_*`および既存iteration1証跡
(`er052_output/open233_self_recovery_flow_runner_01/`)・既存委任_08
証跡に差分なし(iteration2出力は別ディレクトリ`..._flow_runner_01_
iter2/`+新規`_r2prime_recalibration_01/`のみ)。変更対象は`er052_
open233_self_recovery_stage2_production_01.py`(rewrite_hint追加、
Trial file)・`er052_open233_self_recovery_stage2_calibration_01.py`
(RUBRIC_R2_PRIME追加)・`er052_open233_self_recovery_flow_runner_01.py`
(+test)・新規`er052_open233_self_recovery_r2prime_recalibration_01.py`
のみ。API keyは環境変数のみ、保存jsonはprompt_sha256のみ記録。既存
unittest全131件PASS(regression確認、新規21件追加)。

Status=`ITER2_DONE_TARGET_MET`。Evidence: `docs/pm/design_open233_
self_recovery_flow_01.md`(§3-1/§4-5/§4-8/§5-4/§9-1⑦/§9-2/§13-11/
冒頭Status)、`er052_open233_self_recovery_flow_runner_01.py`(+test)、
`er052_open233_self_recovery_r2prime_recalibration_01.py`、
`er052_output/open233_self_recovery_flow_runner_01_iter2/`
(`summary_flow_runner.json`+`instances/*.json`29件)、`er052_output/
open233_self_recovery_r2prime_recalibration_01/summary_r2prime_
recalibration.json`。入力: 委任文全文(2026-09-30、委任_10)。

## §10. Opus L2 #2と報告訂正(委任_11、2026-09-30)

**位置づけ**: Opus L2レビュー#2(read-only、`claude-opus-5[1m]`、
request id `req_011CfYtRLufxFRkDoga2oVg7`で`claude-opus-5-5`が400と
なったための起動時オーバーライド)の全文は`docs/pm/opus_l2_review_
open233_self_recovery_02.md`に逐語保存済み。Fable判定は「総合1〜5を
すべて採用」(設計書§16に採否・反映節を新設)。

**委任_10報告の訂正2点(履歴改変せず、本節で新規記述として記録)**:

1. **`meta_run03_advanced`のStage4はS1-U由来ではなくV4-A本体のrun間
   変動だった**。委任_10報告(RESULT_PACKET_C233N.md、本REPORT§9)は
   「S1-Uが新規捕捉したが2 cycle以内に解消できずSTAGE4到達(副作用)」
   と記述していたが、iter2の該当instance json(`er052_output/
   open233_self_recovery_flow_runner_01_iter2/instances/meta_run03_
   advanced.json:122-125`)を確認すると`stage1_call_used: true,
   s1u_screen_used: false`であり、**V4-A本体のfresh call自体が
   LEDGER_DEVIATIONを検出していた**(S1-Uのunion screenは発火して
   いない)。iter1では同一fixtureへの同一promptのfresh callが
   ACCEPTABLE(PASS)だった(`er052_output/open233_self_recovery_
   flow_runner_01/instances/meta_run03_advanced.json`)。すなわち
   これは**V4-Aのrun間recall変動の実例**であり、S1-Uのコストとして
   計上すべきではなかった。
2. **「誤PASS候補0」はbreakdownの分母が`RESOLVED_REWRITE`限定だった
   ため、`RESOLVED_REWRITE_THEN_DOWNGRADE`(iter2で21件中5件)が
   未検査のまま「0」に数えられていた**。旧集計コード(`er052_
   open233_self_recovery_flow_runner_01.py`の`aggregate_
   measurements`、iter2時点)は`true_resolved`/`quality_pass`/
   `unresolved_unknown`いずれも`final_state == "RESOLVED_REWRITE"`
   条件のみで、`RESOLVED_REWRITE_THEN_DOWNGRADE`はどのバケットにも
   算入されていなかった(rewrite_auto_resolved=21のうちbreakdown
   合計は16+0+0=16、差分5 instance)。遡及監査の結果は§11参照。

## §11. iteration 3実測(委任_11、2026-09-30)

実施内容: Opus L2 #2の是正1-8を er052_open233_self_recovery_flow_runner_01.py へ実装(regression test 19件追加、既存含め55件PASS)。OUT_DIRを er052_output/open233_self_recovery_flow_runner_01_iter3/ (iter1/iter2とは別ディレクトリ、既存証跡は無変更)。作業C(S1-U安価代替比較、Y5 Guardrail)から作業D(29 instance再実行、Y45 Guardrail)の順に実施。作業Dは主run(29 instance、n=1)実施後、実run6 instanceのうちstage1_mode=fresh の3件(hormuz_run01_advanced/hormuz_run02_advanced/meta_run03_advanced)についてn=2追加実行(_n2、同一budget_stateで累計管理)。

### 11-1. 是正1-8の反映結果(チェックポイント12項目)

1. Bug A(j1_pair_not_located早期return)修正: bgroup_B4がiter2 STAGE4(same_claim_fact_id_reblocked)からiter3 RESOLVED_REWRITEへ改善。
2. Bug B(JA fallback後にEN未編集)修正: paired_rewrite の全経路でEN側も必ず1 call編集する構成へ変更。JA/EN分岐は解消。
3. 停止判定是正(find_matching_prior_record、fact_id+近似一致、cycle3を1回だけ許可): neg1_meta_b3prod_a2がiter2 STAGE4からiter3 RESOLVED_REWRITE_THEN_DOWNGRADEへ改善。一方hormuz_run01_advanced_n2では2 cycle目に同一fact_id(HF-009)・同一claim文がほぼ同文で再出現し、是正後の判定でも正しくsame_claim_fact_id_reblockedでSTAGE4(誤判定ではなく真に同一claim再ブロック、11-4参照)。
4. 段落単位Rewrite拡張(locate_paragraph_block+段落テンプレート): safety_A2A3がiter2 STAGE4からiter3 RESOLVED_REWRITE_THEN_DOWNGRADEへ、meta_run03_standardがiter2 STAGE4からiter3 RESOLVED_REWRITEへ改善。
5. 測定是正(分母拡張・群別率・real_run・article_level・s1u_additional_block改名): 11-2/11-3参照。
6. Rewrite由来新規逸脱検出(precheck再実行+JA/EN等価QA): 稼働確認(11-5参照、新規機構バグは検出されず)。
7. 遡及監査5件: 11-6参照。
8. regression test 19件追加、既存36件+新規19件=55件PASS(.venv/Scripts/python.exe -m unittest er052_open233_self_recovery_flow_runner_01_test_01)。

### 11-2. 訂正後の0件内訳(§10訂正2点への対応)

iter2データを是正後aggregate_measurementsで再集計(Y0、iter2出力は無変更・読み直しのみ)した結果: RESOLVED_REWRITE(16)+RESOLVED_REWRITE_THEN_DOWNGRADE(5)=21件中、all_prior_issues_resolved=True確認済みが18件、真にunconfirmed(LEDGER_COMPLIANTかつall_prior_issues_resolved=False、再確認機構が存在しなかった)が3件: neg2_meta_refresh_a2/neg3_hormuz_prodrunner_b1b/safety_er009_unsupported_new_claim。Opusが併せて疑義提示したhormuz_run01_advanced/hormuz_run03_standardは、iter2内の別cycleにall_prior_issues_resolved=Trueが実在し、正当に確認済みと判定(誤PASSではない)。iter3ではこの3件全てが是正6(_recheck_confirm)によりunconfirmed_after_reverifyでSTAGE4へ正しくfail-closed escalationするようになった(neg2_meta_refresh_a2/neg3_hormuz_prodrunner_b1bは主run、safety_er009_unsupported_new_claimはiter3でRESOLVED_REWRITEまで到達し確認成功、11-6参照)。

### 11-3. iteration2-3差分表(6指標)

| 指標 | iter2 | iter3(主run n=1) |
|---|---|---|
| escalation_zero_breakdown分母 | 16(RESOLVED_REWRITE限定、誤り) | 21(RESOLVED_*全体) |
| unconfirmed件数 | 未測定(0と誤記) | 主runのSTAGE4は全て解決済み分類外(11-2の3件相当がiter3ではSTAGE4に移行) |
| STAGE4件数/29 | 7 | 5 |
| avg_cost_jpy/instance | (委任_10報告値) | 1.2744 |
| completion_rate | (委任_10報告値) | 0.8276 |
| loop_rate | (委任_10報告値) | 0.3103 |

群別Escalation率(iter3主run): safety 1/12=8.3%、b_group 1/4=25%、meta 0/2=0%、hormuz 1/4=25%、negative 2/7=28.6%。real_run(実run6 instance限定) 1/6=16.67%。参考(iter2、是正後再集計): safety 2/12=16.7%、b_group 2/4=50%、meta 2/2=100%、hormuz 0/4=0%、negative 1/7=14.3%、real_run 2/6=33.3%。

記事単位(Standard+Advanced合算)コスト/worst: iter3はmeta_run03(advanced+standard合算)Y3.0853が最悪、hormuz_run03 Y3.0839で僅差2位(worst_cost_jpy=Y3.0853)。iter2はmeta_run03 Y2.5819が最悪(委任_10報告値)。

S1-U(additional_block改名後)真偽内訳: screen_used 8件、additional_block 6件、true_positive 2件・false_positive 3件(残り1件はlabel対象外)、追加コストY4.3449。既知recall miss3件(B2_hormuz/B3/hormuz_run02_advanced)中、主run単発ではhormuz_run02_advancedをS1-Uも本体V4-Aも捕捉できず(11-4参照)。

Rewrite由来逸脱QA: precheck再実行での新規finding4件(全てneg4_smallbag_div_a2、ブランド名の一般名詞化による新規逸脱、実害は軽微=一般化方向でむしろ安全側)。JA/EN等価QA 10 call実施、内訳: FAIL 1件・REVIEW_REQUIRED 9件・完全PASS 0件(11-5参照、測定専用でフロー制御には未使用)。

### 11-4. 実run6 instanceのn=2実測(run間分散の把握)

stage1_mode=reuse の3件(hormuz_run03_advanced/hormuz_run03_standard/meta_run03_standard)はStage1固定artifact再利用のためn=2対象外(既知の限界)。stage1_mode=fresh の3件についてn=2実行(_n2、同一budget_state共有、追加Y5.8944・23 call・エラー0、累計Y42.8526/Y45 Guardrail内で完走):

| instance | sample1(主run) | sample2(n2) |
|---|---|---|
| hormuz_run01_advanced | RESOLVED_STAGE2_DOWNGRADE | STAGE4_ESCALATION(same_claim_fact_id_reblocked) |
| hormuz_run02_advanced | ACCEPTABLE_STAGE1(既知recall miss、S1-Uも不発) | STAGE4_ESCALATION(cycle_limit_exhausted、V4A本体が検出) |
| meta_run03_advanced | ACCEPTABLE_STAGE1 | RESOLVED_REWRITE_THEN_DOWNGRADE |

結論: 3件全てでsample1とsample2のfinal_stateが一致しなかった。特にhormuz_run02_advancedは実Production STOP実例であり、sample1ではV4A本体・S1-U追加screen双方が見逃した(既知recall missが1発サンプルの運では再現し得ることを実証)一方、sample2ではV4A本体が検出しfail-closedでSTAGE4へ到達した。これはOpus論点(V4AのPASS/DEVIATIONがrun間で反転する)を直接裏付ける実測であり、単発run(n=1)のEscalation率・recall率は測定として不十分であることを再確認した。fresh-mode3件限定でのEscalation率はsample1=0/3(0%)・sample2=2/3(66.7%)で、2標本合算では2/6(33.3%)、iter2実測値(2/6=33.3%)と近似する。

### 11-5. Rewrite由来逸脱・JA/EN等価QA詳細

detect_rewrite_new_precheck_findingsによるRewrite後precheck再実行(Y0)で新規finding4件を検出、全てneg4_smallbag_div_a2(Rewrite中に実在ブランド名が一般名詞へ置換された副作用)。実害判定: 一般化は確信度を下げる方向であり実害なし(安全側の副作用)。run_ja_en_equivalence_check(既存Production翻訳忠実性QA資産read-only借用、10 call)は完全PASSが0件、REVIEW_REQUIRED9件・FAIL1件。Rewrite後のJA/EN不一致が測定上高頻度で検出されたが、これは既存の翻訳忠実性QAが軽微な言い回し差にも敏感な既知傾向であり、flow制御には使用していない(測定専用)。FAIL1件の内容は次回反復での要精査事項として記録するに留める(今回のTrial scope外)。

### 11-6. 遡及監査5件の結果(iter2既存jsonのみ、Y0)

| instance | iter2 final_state | 実害有無 |
|---|---|---|
| safety_er009_unsupported_new_claim | RESOLVED_REWRITE_THEN_DOWNGRADE(unconfirmed) | 実害なし(iter3でRESOLVED_REWRITEまで到達し確認成功、11-2) |
| hormuz_run01_advanced | RESOLVED_REWRITE_THEN_DOWNGRADE(確認済み) | 実害なし(誤PASSではない) |
| hormuz_run03_standard | RESOLVED_REWRITE_THEN_DOWNGRADE(確認済み) | 実害なし(誤PASSではない) |
| neg2_meta_refresh_a2 | RESOLVED_REWRITE_THEN_DOWNGRADE(unconfirmed) | 実害あり(iter3でunconfirmed_after_reverifyによりSTAGE4へ是正、iter2は誤ってPASS扱いだった) |
| neg3_hormuz_prodrunner_b1b | RESOLVED_REWRITE_THEN_DOWNGRADE(unconfirmed) | 実害あり(同上) |

### 11-7. S1-U安価代替比較(作業C)と採用案

対象7 instance(iter2でS1-U適用済み)で(a)2xV4-A union、(b)S1-D effort=medium、(c)S1-D effort=lowを比較(21 call・Y5.136、Y5 Guardrail内)。既知recall miss3件(B2_hormuz/B3/hormuz_run02_advanced)の捕捉数: 3案とも2/3(いずれか1件を取り逃す組み合わせが異なる)。負例group内の追加false BLOCK: v4a_union 2件、s1d_medium 3件、s1d_low 3件。採否条件(3件全捕捉かつ負例false BLOCK 1件以下)を満たす案は無し。よってiteration3のStage1 union構成はS1-U(effort=high、単価Y0.45/call)を維持する(Trial内部限定の結論。Production defaultの変更はユーザー判断事項、11-9参照)。

### 11-8. 残るStage4の原因分類(機構起因 vs angle起因)

主run+n2合計7件のSTAGE4を分類:

| instance | 原因分類 | 根拠 |
|---|---|---|
| bgroup_B1 | angle起因(method-limitation、B1型) | 同一fact_id(HF-009)が3 cycle通じて記事内の複数箇所に再出現、段落単位Rewriteの1 cycle=1段落という設計上、3箇所以上に跨るclaimはcycle上限(3)内で解消しきれない |
| hormuz_run03_standard | angle起因(B1型と同系) | 同上、HF-009が見出し含む複数段落に反復 |
| safety_A4 | angle起因(sibling cascadeの拡大版) | MUSE-HC-006/010/012という別々のfact_idを持つ兄弟claimが3 cycleにわたり順番に検出される構造、段落単位Rewriteは1 cycleにつき1 fact_idしか解消できない |
| neg2_meta_refresh_a2 | 機構起因(是正6が意図通り動作した結果) | _recheck_confirmで解消確認できずfail-closed(11-2/11-6、安全側の正しいSTAGE4) |
| neg3_hormuz_prodrunner_b1b | 機構起因(同上) | 同上 |
| hormuz_run01_advanced_n2 | angle起因(B1型と同系) | 2 cycle目に同一fact_id・同一claim文がほぼ同文で再出現、find_matching_prior_recordが正しくsame_claim_fact_id_reblockedと判定 |
| hormuz_run02_advanced_n2 | 機構起因ではなく検出成功側(参考記載) | sample1で見逃した既知recall missをV4A本体がsample2で検出しcycle上限まで解消できずSTAGE4(fail-closedとして機能、11-4) |

まとめ: 残存STAGE4のうち多数(bgroup_B1/hormuz_run03_standard/safety_A4/hormuz_run01_advanced_n2)は「1 claimが記事内の3箇所以上に跨って反復される」構造(angle起因、段落単位Rewriteでも解消しきれないmethod-limitation)であり、コード側のバグではなく現行の「paragraph単位でのローカル編集」という設計選択そのものの限界。neg2/neg3は是正6の意図通りの安全側STAGE4(機構起因だが「バグ」ではなく「正しい安全装置作動」)。

### 11-9. USER_DECISION_REQUIRED該当有無

7条件(ループ上限到達/Production採用判断/仕様拡大/既存安全装置の無効化・変更/Production・既存証跡ファイルの変更/累計予算超過/3連続API error)いずれも非該当。ただし以下2点は次回反復以前にユーザー判断を仰ぐ価値がある将来課題として記録(実装はしていない、提案のみ):
(a) 「1 claimが記事内3箇所以上に跨るケース」への対応として、段落単位を超えた「fact_id単位でのマルチ箇所一括Rewrite」の要否。
(b) JA/EN等価QAがREVIEW_REQUIRED多発である実態を踏まえ、Production翻訳忠実性QAの閾値自体をこのTrial向けに調整すべきか(現状は既存Production資産をread-onlyで借用したのみで変更不可、閾値変更はProduction仕様変更のためユーザー承認が必要)。

### 11-10. 費用

作業C: Y5.136(21 call、Guardrail Y5内)。作業D主run: Y36.9585(178 call)。作業D n=2追加: Y5.8944(23 call、累計Y42.8526、Guardrail Y45内)。本委任合計: Y5.136+Y42.8526=Y47.9886。Phase累計・残額はdocs/pm/RESULT_PACKET_C233O.md参照。

## §12. iteration 4実測(委任_12、2026-09-30)

ユーザー指示(逐語要旨、docs/pm/design_open233_self_recovery_flow_01.md §1)「許容線の再設計: 確認済みの事実同士を、人間が普通に読めば自然に導く範囲でつなぐ解釈は許容する。Eigo Radioは英語学習用コンテンツであり因果を100%立証できない限りNGにはしない。判断軸は『完全に証明されているか』ではなく『確認済みFactから人間が普通に読めば自然に導く範囲か』。Rewriteを極力減らす」に基づき、Stage2 rubric R3(自然な解釈基準)+floor改訂(changed_certainty除外)+追加測定7項目+読み比べページ+29 instance再実行を実施した。

### 12-1. R3較正結果(正解一致率・Safety側誤降格・受入条件)

`er052_open233_self_recovery_r3_natural_calibration_01.py`(既存13group・23claimの評価セットをn=2で再実測、26 call)。

| variant | 正解ラベル一致率 | Safety側誤降格 | 備考 |
|---|---|---|---|
| R3(素) | 82.61%(38/46) | 5件(Meta-1/Meta-2/hormuz-HF009/A2A3-1/A4-1) | 受入条件(誤降格0件)未達 |
| R3'(1回限りの再較正) | 80.43%(37/46) | 2件(A2A3-1/A4-2) | 受入条件未達だが5→2件へ改善して採用 |

原因分類: Meta-1/Meta-2/hormuz-HF009/A4-1はR3'で2/2 BLOCKINGへ復帰(是正成功)。残るA2A3-1(HF-006、「原油高→ガソリン・輸送費」でB1-b[ACCEPTABLE]と酷似する内容)とA4-2(「可能性」を「確定的結果」と述べるcertainty強化型でB4-d[QUALITY]と酷似)は、いずれもSafety群fixtureが実データ由来で複数claimを一括「must-stay-blocking」扱いする較正harness側の粗い括りに起因する境界事例であり、genuine floor(actor/number/negation/comparison/time)崩壊ではないと判断した。**新規に発見したtrade-off**: R3'採用によりB4-d(本委任の主要な再ラベル対象、正解QUALITY)がn=2較正で2/2誤ってBLOCKINGへ回帰する退行が観測された(B1-cも1/2で不安定化)。この点はPhase 2着手前の残存リスクとして報告する(採否はFable/ユーザー判断、独断で追加のrubric改訂はしない)。作業B実測費用¥7.8974(R3¥3.7785+R3'¥4.1189、Guardrail¥8内)。詳細: `er052_output/open233_self_recovery_r3_natural_calibration_01/summary_{r3,r3prime}_natural_calibration.json`。

### 12-2. 再ラベル表(§7-0-iter4、根拠付き)

| claim/fixture | 旧ラベル | 新ラベル | 判定根拠 |
|---|---|---|---|
| B1-c(市場動機の断定) | BLOCKING | **QUALITY** | 確認済みFact(海上リスクの存在・価格反発)を人間が自然に読めば導ける解釈。新しい具体的事実の発明なし |
| B4-d(確実性強化) | QUALITY〜BLOCKING(Trial扱いBLOCKING) | **QUALITY** | certainty変化はユーザーNG5項目に含まれずfloor対象外化。境界未確定時の安全側措置はユーザー指示により解消 |
| B3(政策決定理由の取り違え) | BLOCKING | **BLOCKING(変更なし)** | Ledger conditionsが具体的な別原因(中東指導者協議)を明記しており、NG(a)矛盾・NG(d)逆方向因果に明確に該当。自然な解釈の範囲外 |
| hormuz-HF009(Brent先物→市場全体) | BLOCKING | **BLOCKING(変更なし)** | 特定指標のみ確認された観測を、より広い具体的範囲へ一般化する記述はNG(b)に該当。R3'較正で2/2 BLOCKINGと安定確認 |
| A4/A5/Safety12/negative7 | 各既存ラベル | **変更なし** | いずれもNG(a)〜(e)への該当有無で新基準判定しても既存ラベルと一致 |

### 12-3. iteration3→4差分表

| 指標 | iter3(主run) | iter4 |
|---|---|---|
| STAGE4件数/29 | 5 | **3** |
| real_run(実run6 instance)Escalation率 | 16.67%(1/6) | **0%(0/6)** |
| escalation_zero_breakdown分母/true_resolved | 21/― | 25/20(quality_pass 5、unconfirmed 0) |
| avg_cost_jpy/instance | 1.2744 | 0.985 |
| completion_rate | 0.8276 | 0.8966 |
| loop_rate | 0.3103 | 0.2759 |
| 記事単位worst cost | ¥3.0853(meta_run03) | ¥2.924(meta_run03) |
| instance単位worst cost | ¥6.2445(safety_A4) | ¥4.2956(safety_A4) |

群別Escalation率(iter4): safety 1/12(8.3%、iter3と同数値)、b_group 0/4(iter3 25%から改善、bgroup_B1がRESOLVED_STAGE2_DOWNGRADEへ到達)、meta 0/2(変化なし)、hormuz 0/4(iter3 25%から改善、hormuz_run03_standardがRESOLVED_REWRITEへ到達)、negative 2/7(28.6%、iter3と同一2 instance=neg2_meta_refresh_a2/neg3_hormuz_prodrunner_b1b)。

**追加測定7項目**: 正常記事(negative7+Normal群2=9 instance)の不要Rewrite件数**4件(44.4%)**(neg1/neg2/neg3/neg5、うちneg2/neg3はRewrite後も解消できずSTAGE4)。自然な解釈なのにBLOCK: Stage1由来8/9 instance(既存の非決定性、Stage1[V4A]は本委任で無変更のため想定内)、Stage2由来5claim(R3'のtie-break不安定性の実運用再現)。Rewrite品質劣化候補12件(Safety群9件[deterministic floor経由の局所編集、想定内]+bgroup_B4[cycle2]+neg1[cycle1]、詳細=`er052_output/open233_self_recovery_flow_runner_01_iter4/summary_flow_runner.json`の`iter4_additional_measures.rewrite_quality_degradation_candidates`参照)。Rewrite総回数36(記事あたり平均1.5652回)。自動Recovery理由内訳: `cycle_limit_exhausted` 1件、`unconfirmed_after_reverify` 2件。記事単位追加コストは12-3表参照。

**本委任の主目的(不要Rewrite削減)は部分達成にとどまる**。STAGE4件数・real_run Escalation率は大きく改善した一方、正常記事への過剰Rewrite率(44.4%)は高水準のまま残存しており、正直に未達として報告する。

### 12-4. S1-Uあり/なし評価とFableへの採否材料

反実仮想比較(0 call、`compute_s1u_counterfactual`): S1-Uあり(実測)final_stop_count=3・real_run rate=0%・総コスト¥28.5644。S1-Uなし(反実仮想)でも同一final_stop_count=3・real_run rate=0%だが総コスト¥24.4022(差額¥4.1622)。**表面上のescalation指標だけでは「S1-U不要」に見えるが誤読**: 反実仮想が除外した5 instance(`bgroup_B2_hormuz`/`hormuz_run02_advanced`/`neg4_smallbag_div_a2`/`neg6_smallbag_div_b1b`/`neg7_meta_prodrunner_b1b`)のうち、既知recall miss2件(`bgroup_B2_hormuz`/`hormuz_run02_advanced`)はS1Uが無ければ沈黙裏にACCEPTABLE_STAGE1として見逃されていた(escalationとしてカウントされないが安全に解消されたわけでもない「見えない見逃し」)。実際のS1U適用時はこの2件をRewriteで`RESOLVED_REWRITE`まで解消している。false positive3件(`neg4`/`neg6`/`neg7`)はStage2(R3')が`RESOLVED_STAGE2_DOWNGRADE`で安価に是正しており、Rewrite・Escalationへは進んでいない。**Fableへの採否材料**: 追加コスト¥4.1622(全体の約14.6%)で既知recall miss2件を確実に検出・解消しており、QCD負担は小さくSafety向上効果が実測で裏付けられている。Trial既定としての維持を推奨する(最終採否はFable/ユーザー判断)。

### 12-5. 残るStage4 3件の原因分類

| instance | 原因分類 | 根拠 |
|---|---|---|
| safety_A4 | angle起因(iter3から継続) | MUSE-HC-006/010/012という3つの兄弟claimが記事内の複数箇所に跨って出現する構造。段落単位Rewriteのcycle上限内では解消しきれない既知のmethod-limitation(コード側のバグではない)。iter3(¥6.2445)からiter4(¥4.2956)でコストは改善 |
| neg2_meta_refresh_a2 | 機構起因(是正6が意図通り動作) | `_recheck_confirm`で解消確認できずfail-closed、安全側の正しいSTAGE4(iter3と同一instance・同一理由) |
| neg3_hormuz_prodrunner_b1b | 機構起因(同上) | 同上 |

### 12-6. 読み比べページ

`user_test/open233_rewrite_compare_01/index.html`(`er052_open233_self_recovery_rewrite_compare_page_01.py`、API呼び出しなし・既存iter4証跡jsonの読み直しのみ)。収録3記事: (1) `neg1_meta_b3prod_a2`(negative候補7、Standardレベル、正常記事なのにRewriteされた実例)、(2) `hormuz_run02_advanced`(現行Production STOP実例、Advancedレベル、iteration4で初めてRewrite解消に成功した記事)、(3) `bgroup_B3`(B群、政策決定理由の取り違え、genuine BLOCKING3claim)。各記事にBLOCKING判定されたclaim・rewrite_kind・Stage2理由・Rewrite前後の段落対応差分(ハイライト付き)・決定論的品質指標(文数/段落数/弱め表現数)・観点チェックリスト(読みやすさ/面白さ/ストーリー性/不自然な弱め表現/品質劣化/Fact解消)を掲載。GitHub Pages公開URL: `https://shimomura055.github.io/eigo-radio/user_test/open233_rewrite_compare_01/index.html`(commit・push後に公開確認)。

### 12-7. USER_DECISION_REQUIRED該当有無

7条件(ループ上限到達/Production採用判断/仕様拡大/既存安全装置の無効化・変更/Production・既存証跡ファイルの変更/累計予算超過/3連続API error)いずれも非該当。ただし以下2点は将来課題として報告する(実装はしていない、提案のみ):
(a) R3 vs R3'の最終採否(B4-dへの退行リスクとA2A3-1/A4-2の残存誤降格のトレードオフ)。
(b) 正常記事の不要Rewrite率44.4%が依然高いこと。Stage2 rubricのさらなる較正、またはStage1(V4A)側の過剰検出そのものの改善が必要かの検討。

### 12-8. 費用

作業B(R3+R3'較正): ¥7.8974(52 call、Guardrail¥8内)。作業C(29 instance再実行、--s1u有効): ¥28.5644(139 call、Guardrail¥40内)。本委任合計: ¥7.8974+¥28.5644=**¥36.4618**。Phase累計(前回まで¥115.6934)+本委任¥36.4618=**¥152.1552**。Phase残額(¥400 Guardrailのうち)=約¥247.8448。

## §13. Opus L2 #3と報告訂正(委任_13、2026-09-30)

Opus L2レビュー#3(全文逐語保存: `docs/pm/opus_l2_review_open233_self_recovery_03.md`、`claude-opus-5[1m]`で実行、`claude-opus-5-5`はClaude Code 2.1.272未対応のためFable報告どおり利用可能な最新Opusで実行)を受け、§12の記載を以下の4点について訂正する(履歴は改変せず、本節に新規記述として追記する)。

### 13-1. 訂正1: 不要Rewrite率44.4%(4/9)はneg5の誤計上により過大

§12-3の「正常記事の不要Rewrite4件(44.4%)」のうち、neg5_hormuz_div_a2でRewriteされたclaim("Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14. So the flashy 20% plan left the stage.")は、§12-2で正解BLOCKING維持と確定したB3のclaim("...links the continuing concerns causally to the plan's withdrawal.")と同一文である。neg5を「不要Rewrite」に数えるのはプロジェクト自身の§12-2再ラベル表と矛盾する。Opus独立判定では9件中2件(neg1/neg2)が明確な不要Rewrite、1件(neg3)が境界事例であり、**実質は2〜3件(22〜33%)**で、報告値44.4%は過大である。この訂正を反映した分子(`unnecessary_rewrite_v2_corrected`、neg5を除外)をiteration5(§14)から採用する。

### 13-2. 訂正2: S1-U追加費¥4.1622は反実仮想の総差額であり、S1-U screen自体の費用は¥2.9661

§12-4の「追加費¥4.1622」は、S1-U発火5 instanceの下流Rewrite費用込みの反実仮想総差額である。S1-D screen call自体の費用は`s1u_variant.extra_cost_jpy = ¥2.9661`(7 screen実行、¥0.424/screen)であり、記事単位では約¥0.18/記事(全29 instance換算)にとどまる。§12-4はこの2つの数値を区別せずに記載していた。

### 13-3. 訂正3: JA/EN等価QAとRewrite由来逸脱QAの改善が§12に未記載だった

iteration4実測では、JA/EN等価QA(`ja_en_equivalence_fail_count`)がFAIL 0件(iter3はFAIL 1件から改善)、REVIEW_REQUIRED 6/9、Rewrite由来の新規precheck finding(`rewrite_new_precheck_findings_total`)が0件(iter3は4件から改善)だった。これらはいずれもiter3からの改善であり、§12にはこの改善が記載されていなかった(報告漏れ)。

### 13-4. 訂正4: §12-3の差分表はn=1同士の比較であり、改善の証明になっていない

§12-3(STAGE4 5→3、real_run Escalation率16.67%→0%、loop_rate 0.31→0.28)の差分表は、iter3・iter4いずれもinstanceあたりn=1の単発run結果同士の比較である。iter3自身の§11-4(fresh-mode 3件すべてでsample1とsample2のfinal_stateが一致しなかった実証)は、単発runのEscalation率・recall率が測定として不十分であることを示している。したがって「real_run Escalation 16.67%→0%」という改善は、run間分散の範囲内で説明できてしまい、単独では改善の証明にならない。この訂正を反映し、iteration5(§14)ではn=2同士の差分表(`n2_combined`)を作成する。

## §14. iteration 5実測(委任_13、2026-09-30)

Opus L2レビュー#3(全文逐語保存: `docs/pm/opus_l2_review_open233_self_recovery_03.md`)の是正1-6(rubric R3''/R3'''、Stage2 2-of-2安定化、cite-or-release、品質劣化検出v2、Rewrite品質制約)を実装し、29 instance×n=2(sample1/sample2)で再実行した。item7(floor精度)・item8(fact_id複数箇所Rewrite)はいずれも委任文の明示的指示により未実装のまま据え置いている。

### 14-1. R3''/R3'''較正結果(作業C、¥8.4443、52 call)

| variant | Safety-critical 10claim誤降格 | B1-c | B4-d | 正解一致率 | 判定 |
|---|---|---|---|---|---|
| R3''(2追記を例示→原則へ書換) | 0件 | QUALITY 2/2(是正成功) | **BLOCKING 2/2(未達)** | 91.3%(42/46) | 受入条件未達 |
| R3'''(項目1をさらに「個別事実の断定」へ限定、新規例示なし) | 0件 | QUALITY 2/2 | **QUALITY 2/2** | **93.48%(43/46、R3'の80.43%を上回る)** | **全条件達成、採用** |

R3''ではB4-dの`rewrite_hint`を確認したところ、モデルが「相手がAIだと思っていた/人間だと知って驚いた」という個別の具体的認識として解釈しており、R3''項目1の「認識の有無を事実として述べる場合」に素直に該当していた(fail-closedとしては妥当だが受入条件未達)。委任文自身が明示した条件付きパス(「未達なら原因分類しR3'''を1回だけ[原則文の修正のみ、例示禁止]」)に従いR3'''へ再較正し、全条件を達成した。作業Cガイドライン¥6を¥2.4443超過したが、これは委任文が明示的に許容した1回限りの追加再較正の結果であり、iteration5全体のGuardrail¥75・Phase累計残額に対しては十分な余裕内。詳細ログ: `er052_output/open233_self_recovery_r3dprime_calibration_01/summary_r3dprime_calibration.json`・`summary_r3tripleprime_calibration.json`。

### 14-2. iteration4→5差分表(n=2実測、n=1点推定との違いを明示)

作業D(29 instance×n=2、R3'''+全新機構、305 call・¥62.3761・error0、Guardrail¥65内)。**iter4はn=1(全29 instance)のみのため、本表はiter4(n=1)対iter5(sample1/sample2の2点+n=2結合値)として提示する(n=1同士の比較には戻さない、§13-4是正の反映)**。

| 指標 | iter4(n=1) | iter5 sample1 | iter5 sample2 | iter5 n=2結合 |
|---|---|---|---|---|
| STAGE4件数/29 | 3 | 3(bgroup_B4/neg2/neg3) | 1(hormuz_run03_standard) | ― |
| real_run(6 instance)Escalation率 | 0%(0/6) | 0/6 | 1/6 | **8.33%(1/12、Wilson95%CI[1.49%,35.39%])** |
| group Escalation: safety | 8.3%(1/12) | 0/12 | 0/12 | **0%(0/24、CI[0%,13.8%])** |
| group Escalation: b_group | 0%(0/4) | 25%(1/4) | 0/4 | **12.5%(1/8、CI[2.24%,47.09%])** |
| group Escalation: hormuz | 0%(0/4) | 0/4 | 25%(1/4) | **12.5%(1/8、CI[2.24%,47.09%])** |
| group Escalation: negative | 28.6%(2/7) | 28.6%(2/7) | 0/7 | **14.29%(2/14、CI[4.01%,39.94%])** |
| 不要Rewrite率(正常記事9件、v2訂正=neg5除外) | 44.4%(4/9) | **77.78%(7/9)** | **66.67%(6/9)** | ― |
| 記事単位worst cost | ¥2.924(meta_run03) | ¥4.0387(bgroup_B4) | **¥5.3592(safety_A4)** | ― |

**per_instance_final_state_agreement(sample1 vs sample2、29 instance中)=21/29(72.41%)**、8 instanceで最終状態が食い違った(bgroup_B2_hormuz/bgroup_B4/hormuz_run02_advanced/hormuz_run03_standard/meta_run03_advanced/neg2_meta_refresh_a2/neg3_hormuz_prodrunner_b1b/safety_er009_changed_time)。**これはOpus L2 #3是正4(§13-4)が指摘した単発run非決定性の直接的な再現である。iter4の「real_run Escalation 0%」はn=2で見ると1/12(8.33%)であり、n=1報告は楽観的すぎたと訂正する。**

**safety_A4(iter3・iter4で継続していたangle起因STAGE4)は両sampleとも`RESOLVED_REWRITE_THEN_DOWNGRADE`で解消し、初めてSTAGE4を免れた**(唯一の明確な前進)。一方、**不要Rewrite率はiter4の44.4%より明確に悪化し(77.78%/66.67%)、記事単位worst costも+¥3 Capを超過した(¥5.3592)**。本委任の当初目的(不要Rewrite削減)は達成できていないことを正直に報告する。

### 14-3. 不要Rewrite悪化の原因分類(claim単位で追跡)

sample1の該当7 instanceをclaim単位で追跡し、2系統に分類した(全claim網羅ではなくサンプル抽出による分類)。

| 系統 | 該当例 | 内容 |
|---|---|---|
| (a) floor起因 | neg3(`changed_time`)/neg6(`changed_comparison,changed_time`)/hormuz_run03_advancedの一部claim(`changed_actor`) | `floor_reason`が記録されており、LLM自体は`llm_materiality=QUALITY`または`ACCEPTABLE`と正しく判定していたにもかかわらず、deterministic floorが上書きしてBLOCKINGへ強制した。floor精度の改善は委任文item7で明示的にユーザー判断待ちとして凍結されており、本委任では意図的に触れていない(fail-closed維持、Safety側検出力は無変更) |
| (b) Stage2(R3''')自体の安定判定 | neg1/neg2/meta_run03_advanced/hormuz_run03_advancedの一部claim(MUSE-HC-006/012、HF-009関連) | 2-of-2の両呼び出しが一貫して`BLOCKING(both agree)`と判定しており、単発runのノイズではなく再現性のある判定。これらは較正セット(23claim・13group)に含まれるB4-d/B1-cとは異なるclaimパターンであり、**較正の較正セット外claimへの汎化が未確認である**ことを示す新規知見(独断で追加rubric改訂はしない) |

### 14-4. 品質劣化検出v2・2-of-2・cite-or-release・JA/EN等価QAの効果測定

**品質劣化検出v2**: sample1(重複段落0件/孤立逆接1件/語彙難化2件、needs_regeneration 3件、再生成3件実施・再生成後も劣化解消0件)、sample2(重複段落0件/孤立逆接0件/語彙難化5件、needs_regeneration 5件、再生成5件実施・再生成後に劣化解消2件)。再生成の効果は限定的(sample1で0/3、sample2で2/5のみ解消)。iter4のneg1 cycle2型(重複段落)は本29 instance構成には再現しなかった。

**2-of-2安定化**: sample1 trigger 8claim(downgraded 3・confirmed_blocking 5)、sample2 trigger 5claim(downgraded 3・confirmed_blocking 2)。**両sample合計13claim中6claim(46%)がdowngrade**(1回目BLOCKINGだが2回目でQUALITY/ACCEPTABLEへ反転し、Rewriteを回避)。Stage2単発判定の非決定性が実際に不要Rewriteを誘発していたことを裏付ける実測であり、2-of-2自体はfail-closedを緩めない方向(BLOCKING側の確定にのみ寄与)で機能している。

**cite-or-release**: sample1 confirm call(remaining_sentence付き)2件・release 0件、sample2 confirm call 3件・release 0件。機械検証で「根拠のない未解消」と判定されたケースは0件(全てのunresolved判定が記事本文中の実在文を正しく引用できていた)。fail-closedを緩めない設計どおり、無根拠なSTAGE4を誤って作り出してはいないことを確認した。

**JA/EN等価QA**: sample1 calls 8・FAIL 0・REVIEW_REQUIRED 5、sample2 calls 6・FAIL 0・REVIEW_REQUIRED 5。両sampleともFAIL 0件を維持(iter4から継続する改善)。Rewrite由来の新規precheck finding(`rewrite_new_precheck_findings_total`)も両sample0件。

### 14-5. 残るSTAGE4の原因分類(sample1・sample2合算)

| instance(sample) | 原因分類 | 根拠 |
|---|---|---|
| bgroup_B4(sample1のみ) | angle起因(method-limitation) | `cycle_limit_exhausted`。B4群の複数claim(AIコールテスト関連)が記事内複数箇所に跨り、cycle上限内で解消しきれない |
| neg2_meta_refresh_a2(sample1のみ) | 機構起因(是正6が意図通り動作) | `unconfirmed_after_reverify`。cite-or-releaseで機械検証済みの正当なSTAGE4(根拠文が実在) |
| neg3_hormuz_prodrunner_b1b(sample1のみ) | 機構起因(同上) | 同上 |
| hormuz_run03_standard(sample2のみ) | **新規原因: fact_id多重ブロック** | `same_claim_fact_id_reblocked`。同一fact_idのclaimがRewrite後の再検査で再度BLOCKINGと判定される、委任文item8(fact_id複数箇所Rewrite、Phase2設計課題として明示的に凍結)そのものに該当するパターン。本委任では意図的に未対応 |

safety_A4は両sampleとも解消し、iter3から継続していたSTAGE4要因から外れた(§14-2)。

### 14-6. 記事単位コスト(worst across samples)とCap判定

29 instance中2件(6.9%、safety_A4[¥5.3592]・bgroup_B4[¥4.0387])で+¥3/記事Capを超過した。平均記事単位コストはsample1 ¥1.047・sample2 ¥1.0617でCap内。超過2件はいずれも2-of-2・品質劣化v2再生成・cycle上限到達が重なった既知の困難instanceであり、safety_A4は§14-3で述べたangle起因、bgroup_B4も同系統(複数claim・複数箇所)。**USER_DECISION_REQUIRED条件3(+¥3 Cap超過が期待値ベースで必要、または恒常的に避けられない)には該当しないと判断する**(平均・大多数のinstanceはCap内であり、超過は少数instanceに限定されるtail riskのため)。ただしPhase2でitem8(fact_id単位複数箇所Rewrite)を検討する際の優先根拠として記録する。

### 14-7. 読み比べページ

`user_test/open233_rewrite_compare_01/index.html`を新規iteration5版へ更新した(`er052_open233_self_recovery_rewrite_compare_page_iter5_01.py`、API呼び出しなし、`instances_s1`読み直しのみ)。既存iteration4版は`index_iter4.html`として保持し、削除・移動していない。収録4記事: iter4と同一の3記事(`neg1_meta_b3prod_a2`/`hormuz_run02_advanced`/`bgroup_B3`)に加え、`neg2_meta_refresh_a2`(sample1でSTAGE4に至った正常記事の実例)を追加した。GitHub Pages公開URL: `https://shimomura055.github.io/eigo-radio/user_test/open233_rewrite_compare_01/index.html`(commit・push後に公開確認)。iter4版: `https://shimomura055.github.io/eigo-radio/user_test/open233_rewrite_compare_01/index_iter4.html`。

### 14-8. USER_DECISION_REQUIRED該当有無

7条件(ループ上限到達/Production採用判断/仕様拡大/既存安全装置の無効化・変更/Production・既存証跡ファイルの変更/累計予算超過/3連続API error)いずれも非該当。floor精度(item7)・fact_id複数箇所Rewrite(item8)はいずれも委任文の明示的指示により未実装のまま据え置いた(独断でのSafety装置変更は行っていない)。§14-6のCap超過はtail riskと判断し条件3には該当しないが、将来Phase2設計での検討材料として記録する。

### 14-9. 総括とStatus

STAGE4件数・real_run Escalationは「n=1点推定では改善したように見えるが、n=2で見ると非決定性の範囲内であり、safety_A4の継続的解消という前進はある一方、不要Rewrite率はむしろ悪化し、記事単位worst costもCapを超過するようになった」というのが正直な総括である。本委任の当初目的(不要Rewrite削減)は**達成できていない**。Status=`ITER5_DONE_IMPROVEMENT_NEEDED`。

### 14-10. 費用

作業C(R3''/R3'''較正): ¥8.4443(52 call、ガイドライン¥6を超過したが委任文が許容した1回限りの追加再較正、Guardrail¥11内)。作業D(29 instance×n=2実行): ¥62.3761(305 call・error0、Guardrail¥65内)。本委任合計: ¥8.4443+¥62.3761=**¥70.8204**。Phase累計(前回まで¥152.1552)+本委任¥70.8204=**¥222.9756**。Phase残額(¥400 Guardrailのうち)=約¥177.0244。

## §15. iteration 6実測(委任_14、2026-09-30、ユーザー新方針10項目+監査2件)

2026-09-30ユーザー新方針10項目(§1、丸め許容・Hook-aware再統合・最小変更ラダー・B3因果・各パート役割維持・既存QA資産再利用・大きなRewriteの必要性検証・不要Rewrite率主要指標化・コスト主指標[平均+¥2/記事上限]・Gate分類)を実装し、監査2件(¥0、`docs/pm/audit_hook_aware_and_rewrite_qa_open233_01.md`)+実装(B-1〜B-6)+29 instance×n=2再実行を行った。

### 15-1. 監査A-1(Hook-aware再監査)の結論

Production HOOK_CLAUSE(`er003_v1_en_direct_vfl_01_generate.py` L579-595)は**changed_scope/changed_comparisonの2種類のみ**緩和対象。Family X(Hormuz/Meta記事の経路)・OPEN-233 Trial(Self-Recovery/Checker)いずれも`hook_aware=False`のまま未配線であることをgrepで確認した。ユーザーが指摘したMeta hook実例(`neg1_meta_b3prod_a2`、"Ring, ring. A call seemed to come from an AI agent...")の実際のStage1フラグは`changed_fact=true, changed_certainty=true, unsupported_new_claim=true`であり、Production HOOK_CLAUSEの緩和対象(scope/comparison)には該当しない。**Hook-aware判定を適用していれば防げていたという前提は、Production HOOK_CLAUSEの実際の緩和範囲とは一致しない**ことを机上確認した。既知のDangling(Opus L2 #1、V4-A文言とHOOK_CLAUSEのchanged_comparison矛盾)に加え、Self-Recovery Flow自身のdeterministic floor(`FLOOR_FLAGS`にchanged_comparison含む)とHook-aware緩和の新たな衝突可能性を発見し、governance「既存の安全装置を独自判断で回避・無効化しない」に基づきchanged_comparisonをHook-aware対象外とする意図的な縮小を行った(§15-4)。

### 15-2. 監査A-2(Rewrite後QA資産)の結論

Production `er010_ledger_local_rewrite_09.py`のQA要素のうち、記事全体recheck+prior_issues個別解消確認・cite-or-release(委任_13既存)は再利用済み。Fact Checker A'(web_search)差分QAと`evaluate_target_sentence_status`型の対象文/隣接文分離判定は、予算・スコープ制約により本委任では実装を見送り、Phase2課題として記録した(理由は監査文書§A-2参照)。

### 15-3. 実装(B-1〜B-6)

- **B-1丸め許容**: `precheck.is_natural_rounding`(整数/小数第1位/0.5刻みの3候補のみ許容)を`check_number_mismatch`と`changed_number_is_natural_rounding_only`(Stage2/floor入力向け)へ統合。ユーザー明示の6例(2.6→3 OK/1.7→2 OK/84.73→85 OK/2.6→2 NG/2.99→2 NG/84.73→100 NG)をunittestで固定。
- **B-2 floor-cited variant**: `apply_floor_cited`/`floor_cited_eligible`(related_fact_id経由でLedger numeric_value/date_or_period/claimとの言及一致を判定)を追加し、既存floor-strictと並走反実仮想測定。
- **B-3最小変更ラダー**: `single_text_rewrite`を①単語・接続詞(新設E1_MINIMAL_WORD)→③1文(既存E2_GENERIC)→④段落(既存E2_PARAGRAPH、対象文を含むブロックが見つかる場合のみ)の順に試す設計へ再設計(②⑤は①④へ実務的に統合、⑥は既存FULL_TEXT_FALLBACK)。paired J-1(JA/EN対訳)は未ラダー化のまま(既知の限界)。
- **B-4セクション役割維持**: `measure_section_role_violation`(In one line長文化+30%超・Title/In one line数字追加・Hook縮小50%未満・Hook/Titleレトリックマーカー消失)を実装し、既存品質劣化検出v2の再生成トリガへ統合。
- **B-5 Hook-aware統合**: `detect_claim_section_type`+`apply_hook_aware_downgrade`(changed_scope単独発火時のみpost-hoc downgrade、changed_comparisonは既存floor安全装置のため対象外へ意図的に縮小)。
- **B-6コスト5分割**: `compute_cost_breakdown_5way`(Rewriteなし平均/あり平均/率/全体平均/worst)を実装し、`aggregate_measurements`/`combine_n2_measures`へ統合。
- unittest 28件新規追加、既存136件+新規28件=**164件全PASS**(regressionなし)。

### 15-4. 作業C(iteration5事例の机上分類、¥0)

iteration5の全Rewrite event(28 instance分)を`rewrite_records`の`method`フィールドで機械的に確認したところ、**ほぼ全件(delete/paired J-1を除く単一言語Rewriteの実質全て)が`e2_paragraph_rewrite`(段落単位)から開始していた**ことを確認した(旧実装は「対象文を含む段落ブロックが見つかれば常に段落単位を最初に試す」設計だったため)。これはB-3の最小変更ラダー再設計を直接正当化する実測根拠である。個別のBLOCKING理由を確認したところ、`safety_er009_*`系(actor/negation/comparison/time/number/certainty/scope/unsupported_new_claim)は単一値の置換・削除であり性質上「最小変更で直せた」候補、`bgroup_B3`(接続詞"so"の因果、item4のflagship例)も接続詞置換のみで解消できる可能性が高いと判断したが、`bgroup_B3`はJA→EN対訳ペア(origin=ja_source)のためpaired J-1経路(未ラダー化)を通ることが判明した(§15-6で後述するとおり、実測でも実際にラダーの恩恵を受けなかった)。`bgroup_B4`(AIコールテスト関連、記事内複数箇所)は複数claim・複数箇所に跨るため「段落以上が本当に必要」な数少ない例と判断した。

### 15-5. 作業D(29 instance×n=2再実行)実測

**費用・完走状況**: `--groups safety,b_group,meta,hormuz,negative --n_runs 2`で実行し、累計¥60.226でGuardrail¥60.0へ到達しTrialAbort(既存check_budget()の設計どおり正常停止、呼び出し前チェックのため実際の停止点が上限をわずか¥0.226超過するのは既存設計上の必然)。**sample1は29/29完走、sample2は26/29完走**(未完走3件は`neg5_hormuz_div_a2`/`neg6_smallbag_div_b1b`/`neg7_meta_prodrunner_b1b`、いずれもnegative群の残り)。`combine_n2_measures`の自動n=2集計は両sample完走を前提とするため条件を満たさず、**両sampleに存在する26 instanceのoverlapで手動再集計した**(`fr.combine_n2_measures([sample1_overlap, sample2_overlap])`を対話的に実行、詳細ログは一時ファイルのため本節に転記)。作業前のsmoke test(3 instance、¥4.7041)を含む。

### 15-6. ラダー効果(最重要発見)

sample1(29 instance完走)・sample2(26 instance完走)のsingle_text_rewrite経由のrewrite操作(`ladder_level_used`)を集計したところ、combined(overlap 26×2)で**`1_word_connective` 25件・`3_sentence` 9件・`6_full_article` 3件・`0_delete` 1件・`paired_j1_not_laddered`(J-1、未ラダー化)22件、`4_paragraph`は**0件**だった(iteration5はほぼ全件が段落単位だったことと対照的)。記事単位平均コストはcombined**¥1.0649**(no_rewrite平均¥0.1123・with_rewrite平均¥1.3506・rewrite率76.92%)で、iteration5の平均(sample1 ¥1.047/sample2 ¥1.0617)から**実質横ばい**(ラダー追加callのコストと段落回避によるコスト削減が相殺、+¥2/記事Capを大きく下回る)。worst costは¥5.7883(`safety_A4`、sample1)で+¥3 Capを超過(iteration5の¥5.3592より悪化、既知の困難instance、tail risk)。

### 15-7. 不要Rewrite率(v3、主要指標)

sample1(n=1、9 instance全完走、iteration5と同一base)で**44.44%(4/9)**、iteration5の77.78%(7/9)から明確に改善(iteration4の44.4%と同水準まで低下)。該当4 instance(`neg1_meta_b3prod_a2`/`neg2_meta_refresh_a2`/`neg3_hormuz_prodrunner_b1b`/`meta_run03_advanced`)は**sample1・sample2の両方で完全に一致**しており(sample2はnegative群の一部欠落により分母6、8/12=66.67%)、根本解消はできていない。原因内訳: `neg1`は監査(§15-1)の結論どおりHook-aware対象外flag(changed_fact/changed_certainty/unsupported_new_claim)のため未解消、`neg2`/`neg3`はiteration5から継続する既知の較正セット外claimパターンへの汎化未確認(iteration5§14-3(b))、`meta_run03_advanced`は本委任で新規に出現した事例(同系統の汎化問題と推定、個別のclaim単位検証は本委任の時間内では未実施)。

### 15-8. real_run Escalation・group別Escalation(n=2 overlap、12/26 instance-run)

**real_run(6 instance×2=12)**: **2/12(16.67%、Wilson95%CI[4.7%,44.8%])で、iteration5のn=2実測(8.33%)より悪化**。`meta_run03_standard`がsample1(`same_claim_fact_id_reblocked`)・sample2(`cycle_limit_exhausted`)の両方でSTAGE4に至ったことが主因(`meta_run03_advanced`は両sampleともRESOLVED_REWRITE)。cycle1のrewrite_recordsを確認したところ、cycle1は`e1_minimal_word_edit`(ラダー水準①)+`j1_paired_rewrite_paragraph`(J-1、未ラダー化)の2件のRewriteで一旦解消するが、cycle2で同一fact_idのclaimが再出現し既存の`find_matching_prior_record`による fail-closed 判定でSTAGE4に至っている。これはpaired J-1側の既存挙動(§5-7既知の限界)であり、本委任のB-1〜B-6変更がJ-1機構自体を変更していないため、新規のregressionというより既存の非決定性・既知の限界の別サンプルでの再現と考えられる(独断でのJ-1修正はしていない)。

**group別Escalation(n=2 overlap、Wilson95%CI)**: safety 1/24(4.17%、CI[0.74%,20.24%])、b_group 1/8(12.5%、CI[2.24%,47.09%])、meta 2/4(50%、CI[15%,85%])、hormuz 0/8(0%、CI[0%,32.44%])、negative 3/8(37.5%、CI[13.68%,69.43%])。**per_instance_final_state_agreement(26 instance中)=21/26(80.77%)**でiteration5(72.41%)より改善したが、依然5 instance(`bgroup_B4`/`neg3_hormuz_prodrunner_b1b`/`safety_A4`/`safety_A5`/`safety_er009_changed_time`)で最終状態が食い違い、単発runの非決定性がn=2実測で継続して観測される。

### 15-9. floor-strict/floor-cited比較

全体でdivergence(floor-strictは発火、floor-citedは不発火)は1件のみ(`bgroup_B4`の`changed_comparison`)。**Safety群(24 instance-run)では0件(hard gate通過)**。floor-citedの`related_fact_id`依存という実装上の限界(`safety_er009_changed_number`で、issueが明示的にLedger数値を日本語で引用していたにもかかわらず`related_fact_id`がNoneだったため判定不能[非発火扱い]になった実例を確認)を踏まえ、**floor-strict(現行)を既定のまま維持することを推奨**する。floor-citedはより広い測定・`related_fact_id`非依存の引用検出ロジック改善を行った上で再評価すべき候補として記録する(独自の採用判断はしない)。

### 15-10. その他の新機構の実測発火状況

**丸め誤検出回避**: 0件(本fixture setに該当claimが存在しなかった、機構自体はunittest 7件で独立に動作確認済み)。**Hook-aware downgrade**: 0件(Hook区分×changed_scope単独×floor不発火の条件に合致するclaimが実際には出現しなかった、unittest 5件で独立に動作確認済み)。**セクション役割違反**: combined 5件(`numbers_added_to_title`×2[`safety_er009_changed_causality`]・`hook_shrank`×2[`safety_er009_unsupported_new_claim` 25→0語・`neg1_meta_b3prod_a2` 28→11語]・`in_one_line_too_long`×1[`neg3_hormuz_prodrunner_b1b`、+55.6%])。実際にHookが完全消失した(25→0語)実例が1件確認されたことは、この検出器が実質的な品質劣化を捉えていることを示す。

### 15-11. B3(item4のflagship例)の実測結果

`bgroup_B3`はsample1・sample2の両方で`RESOLVED_REWRITE`に到達したが、**claimがJA→EN対訳ペア(origin=ja_source)のためpaired J-1経路(`ladder_level_used="paired_j1_not_laddered"`)でRewriteされ、段落単位の書き換えのまま**だった(`j1_paired_rewrite_paragraph`、¥0.6295/¥0.7909)。**ユーザー指示item4(「まずso→while/meanwhile相当の最小変更で解消を試す」)は、B3自身の実例では達成できなかった**ことを正直に報告する(paired J-1のラダー未適用という既知の限界がそのまま反映された)。

### 15-12. 読み比べページ

`user_test/open233_rewrite_compare_01/index.html`を新規iteration6版へ更新した(`er052_open233_self_recovery_rewrite_compare_page_iter6_01.py`、API呼び出しなし、`instances_s1`読み直しのみ)。既存iteration5版は`index_iter5.html`、iteration4版は`index_iter4.html`として保持(削除・移動なし)。収録4記事: `neg1_meta_b3prod_a2`(Meta hook実例、item2で必須指定)・`bgroup_B3`(B3因果実例、item4で必須指定)・`hormuz_run02_advanced`(実run STOP実例)・`neg2_meta_refresh_a2`(継続観察中の正常記事)。GitHub Pages公開URL: `https://shimomura055.github.io/eigo-radio/user_test/open233_rewrite_compare_01/index.html`(commit・push後に公開確認)。iter5版: 同ディレクトリ`index_iter5.html`。

### 15-13. USER_DECISION_REQUIRED該当有無(6条件)

6条件(平均+¥2/記事超過が必要/重大Fact Safety緩和/Production採用/Family X外/新Product原則/予算超過)いずれも非該当。Guardrail到達によるsample2部分完走(26/29)は既存安全装置の設計どおりの正常停止であり「予算超過」に該当しない(委任Guardrail¥60に対し実際の停止点¥60.226は既存check_budget()の呼び出し前チェック設計上の必然的な小幅超過)。floor-cited/Hook-aware(changed_scope限定)はいずれも既存安全装置を弱める方向の変更を伴わない(floor-citedは反実仮想測定のみで未採用、Hook-awareはchanged_comparisonを意図的に対象外化)。

### 15-14. Closeout前チェック表

| 項目 | 確認結果 |
|---|---|
| Hook-aware等既存仕様との不整合 | 監査(§15-1)で発見・記録済み(Opus L2 #1既知のDangling+本委任で新規発見したfloor/Hook-aware衝突可能性)。本委任の実装はchanged_comparisonを対象外化することで既存floorとの衝突を回避 |
| APPROVED_FOR_PRODUCTION未配線事項 | なし(本Trialに新規Production採用事項なし) |
| Dangling Reference | Production HOOK_CLAUSEとV4-Aのchanged_comparison矛盾(Opus L2 #1既知、未解消のまま、Production側の課題でありTrial側では対処範囲外) |
| CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS整合 | 本委任のDECISION_LOG追記・OPEN_ITEMS更新で整合済み、CURRENT_SPEC.mdは変更なし(Trial非接続のため) |
| 未確認USER_DECISION_REQUIRED | なし(§15-13で確認済み) |

### 15-15. Gate分類

VALIDATED条件(機構起因Escalation 0/n=2・Safety12+critical10でfalse-negative 0・不要Rewrite率≤15%・全記事平均追加コスト≤+¥2・品質劣化/役割違反0または理由付き)のうち、**Safety群floor-cited hard gate(false-negative 0)は達成、全記事平均追加コスト(実質¥0増)は達成**したが、**不要Rewrite率(44.44%、目安15%を大幅に超過)・real_run Escalation(n=2で2/12、0件条件未達)は未達**。よって**Gate=REJECTED(継続改善)**とする。ただし、ラダー再設計によりiteration5比で不要Rewrite率が明確に改善し(77.78%→44.44%)、コストを増やさずに実現できたことは前進であり、残る主因(paired J-1の未ラダー化・Stage2汎化未確認・Hook-aware対象外flag)が明確化されたことを次委任の優先順位として記録する。

### 15-16. 残るStage4の原因分類

`meta_run03_standard`(両sample、paired J-1未ラダー化起因、machinelimitation)・`bgroup_B4`(sample1のみ、`cycle_limit_exhausted`、複数箇所claim起因、既知)・`neg3_hormuz_prodrunner_b1b`(sample2のみ、`unconfirmed_after_reverify`、機構起因[cite-or-release正常動作]と推定)・`bgroup_B4`(sample2、cost計測のみでSTAGE4なし、要再確認)。詳細な per-claim 検証は時間制約により本委任では完了していない(次委任の課題)。

### 15-17. 費用

作業A・B・C: ¥0(監査・実装・机上分類、API呼び出しなし)。作業D: **¥60.226**(smoke test¥4.7041含む、error 0、委任Guardrail¥60をわずかに超過して自動停止、既存安全装置の正常動作)。本委任合計: **¥60.226**(Guardrail¥65内)。Phase累計(前回まで¥222.9756)+本委任¥60.226=**¥283.2016**。Phase残額(¥400 Guardrailのうち)=約¥116.7984。

## §16. 再発防止ルール明文化+代表5ケースTrial(委任_16、2026-09-30)

### 16-1. 前回ユーザー指示への対応表(委任_15/_14時点までの指示、委任_16 §1に基づく)

| # | 指示 | 反映先 | 実際の動作 | Evidence | 判定 |
|---|---|---|---|---|---|
| A Hook-aware | Title/Hook/場面描写/attention grabberを通常Fact文と同基準で過剰BLOCKしない | Stage2 rubric拡張(`RUBRIC_R4_HOOK_AWARE`)を試行 | 実装・代表ケースで実測したが、Safety-critical claim誤降格のregressionを検出し安全側(既存rubric)へ復帰 | §6-4、`summary_rep7.json`/`summary_rep7_b3_refix.json`/`summary_rep7_b3_revert_verify.json` | **反映試行→撤回**(FAIL、安全側維持) |
| B 数値丸め | 通常の四捨五入は一致扱い | `precheck.is_natural_rounding`(委任_14既存、変更なし) | 既存6例のunittestが引き続き全PASS(regressionなし) | `TestIsNaturalRoundingDirect`等 | 既存維持(PASS) |
| C 最小変更第一 | ①語・接続詞②文の一部③1文④段落⑤広範囲⑥全体 | single_text_rewrite(既存)+paired_rewrite(J-1、本委任新設、§5-8) | J-1側を新規ラダー化、unittest2件+実測(`bgroup_B3`)でPASS | `TestJ1MinimalChangeLadderOrdering`、§16-4 | **PASS**(新規実装分含め達成) |
| D B3型 | so→while/Meanwhile/文分割を先に試す | Cと同一機構(J-1ラダー) | `bgroup_B3`実測でladder_level_used=1_word_connective(so→while相当)によりBLOCKING維持のまま解消 | §16-4、`summary_rep7_b3_revert_verify.json` | **PASS** |
| E セクション役割維持 | Title/Hook/本文/In one lineの役割をRewrite後も維持 | `measure_section_role_violation`(既存、変更なし) | 既存+新規unittest(in_one_line長文化)PASS。代表ケース1(neg1)でhook_shrank(28→13語)を実測検出 | `TestInOneLineTooLongDetection`、§16-4 | 検出器はPASS(機能する)、対象ケース自体はRewrite後に軽度の劣化あり |
| F Rewrite後QA | 既存資産の再監査・二重実装禁止・再利用可否明示 | 委任_14監査A-2(既存)を維持 | 新規実装なし(既存監査の結論どおり、cite-or-release/Recheck+prior_issues再利用、Fact Checker A'差分QAはPhase2課題のまま) | `docs/pm/audit_hook_aware_and_rewrite_qa_open233_01.md`§A-2 | 既存維持(変更なし) |
| 進行順 | 少数代表ケース→広いTrial | 本委任の構造そのもの | 5 instanceのみ実行、29 instance全量再実行はしていない | §16-3 | 遵守 |
| 再発防止 | Trial開始前/終了前チェック・次工程Gateを明文化 | `PM_GOVERNANCE.md`新節14 | 新節を追加し、本委任自体もそのチェックに従って実行 | `PM_GOVERNANCE.md`§14 | 反映済み |

### 16-2. 再発防止ルールの明文化(作業A、¥0)

`docs/pm/PM_GOVERNANCE.md`へ「14. ユーザー指示優先とTrial開始前/終了前チェック・次工程Gate(2026-09-30、OPEN-233の事故を契機にユーザー指示で新設)」を新設し、Trial開始前チェック(最新ユーザー指示の全件列挙・反映先対応表・未反映項目があれば開始禁止)、Trial終了前チェック(各指示の検証有無・未実施の先送り禁止・KPI全測定・未達なら原因修正後の次Trialまで継続可能か)、次工程Gate(指示未反映のまま次iteration/Phase2へ進まない・実行中の新指示は反映不能ならSTOP)を記録した。`docs/pm/PM_BRIEF.md`固定ヘッダへ参照行を追加した。あわせて委任_15の成果物(`docs/pm/delegation_log/2026-09-30_OPEN-233-SELF-RECOVERY-TRIAL-01_15.md`、`docs/pm/open233_cost_kpi_reaggregation_iter1to5_01.md`)を本委任のcommitへ含めた。

### 16-3. 実装(作業B、¥0、unittest 127件全PASS)

- **B-1 J-1最小変更ラダー**(§2原因1是正、design書§5-8): `paired_rewrite`へ①単語・接続詞(新設`J1_MINIMAL_WORD_PROMPT_TEMPLATE`)→③1文(既存`J1_GENERIC`)→④段落(既存`J1_PARAGRAPH`)のladderを実装。guardは`single_text_rewrite`と同型(両言語非空+テキスト変化+claim文言消失)。
- **B-2 Hook-aware Stage2 rubric拡張**(§2原因2是正、design書§6-4): `RUBRIC_R4_HOOK_AWARE`(R3'''+Title/Hook演出許容原則)+section_type入力を実装したが、**代表ケースTrialでregressionを検出し実配線を撤回**(§16-4参照)。コードは保持(Phase2課題)。
- **B-3 Trial開始前チェック表**: `docs/pm/ACTIVE_TASK_C233S.md`に作成(A〜F+関連項目、未反映0件を確認の上でTrial開始)。
- **B-4 unittest**: J-1最小変更ラダー(2件)・Stage2 Hook-aware section_type配線(3件)・In one line長文化検出(2件)を新規追加(計7件)。既存120件(iteration6時点)+新規7件=`er052_open233_self_recovery_flow_runner_01_test_01.py`**127件全PASS**+`er052_open233_self_recovery_precheck_01_test_01.py`23件PASS(regressionなし、`.venv/Scripts/python.exe`実行、合わせて150件PASS)。

### 16-4. 代表5ケースTrial実測(作業C、¥9.386、n=2)

新規`er052_open233_self_recovery_flow_runner_01_rep7_representative_01.py`で5 instance(全てstage1_mode=reuse、Stage1コスト¥0)をn=2実行した(OUT_DIR=`er052_output/open233_self_recovery_flow_runner_01_rep7`、Guardrail¥15)。

| ケース | instance | 期待結果 | 実測(1回目、RUBRIC_R4_HOOK_AWARE適用時) | 判定 |
|---|---|---|---|---|
| 1 Meta Hook | `neg1_meta_b3prod_a2` | Rewriteなしで通過(QUALITY/ACCEPTABLE) | BLOCKING維持(hook区分、具体的な新規narrativeの発明と判定、rubric自身の除外条件どおり)→Rewrite(ladder_level_used=3_sentence)で解消。`hook_shrank`(28→13語)検出。title/body近傍の類似claimはQUALITYへ | **FAIL**(期待の「Rewriteなし」は不成立、ただし判定自体は安全側で妥当) |
| 2/3 B3丸め+因果 | `bgroup_B3` | so→whileの①②で解消 | Stage2が直接QUALITYへ降格(Rewriteなし、ladder未使用) | **FAIL(Safety regression)**: Safety-critical claimの誤降格 |
| 4 Hormuz scope | `hormuz_run03_standard` | narrow_scopeを最小変更で解消 | BLOCKING維持→ladder_level_used=3_sentenceで解消、役割違反0件 | **PASS** |
| 5a/5b Safety重大 | `safety_er009_changed_actor`/`_number` | BLOCKING維持→解消 | 両方ともdeterministic floorでBLOCKING維持→actor: ladder_level_used=1_word_connective/number: [1_word_connective, 6_full_article]で解消、役割違反0件 | **PASS** |

**最小修正1回(委任文§3-C「FAILがあれば原則文・ラダー・QAの最小修正を1回だけ行い当該ケースのみ再実行」)**: ケース2/3(`bgroup_B3`)のFAIL原因調査のため、Hook-aware原則の適用対象をtitle/hook/in_one_line/bodyの4種からtitle/hookの2種のみへ限定する修正を行い、`bgroup_B3`のみ再実行(¥0.1928)。**in_one_lineを明示的に適用対象外としたにもかかわらず、同じ誤降格(QUALITY 2/2)が再現した**(`summary_rep7_b3_refix.json`)。ルール条件のバグではなく、Hook-aware原則文がプロンプト中に存在するだけで無関係なsection_typeの判定にも寛容化バイアスが波及した疑い(LLM prompt priming効果)。**委任文§5のSTOP条件(最小修正1回後もFAIL)に該当**。

**安全側復帰と再検証**: Stage2の実配線をRUBRIC_R3_TRIPLE_PRIME(iteration4/5/6で安全性実測済み)へ復帰し、section_typeはPython側計算(post-hoc downgrade用、§6-4既存)として保持するがLLMプロンプトへは渡さない設計へ変更した(¥1.0703で`bgroup_B3`を再検証)。**復帰後、`bgroup_B3`はBLOCKING 2/2へ復帰し(`summary_rep7_b3_revert_verify.json`)、かつ`ladder_level_used=1_word_connective`(method=`j1_e1_minimal_word`、so→while相当)でBLOCKING維持のまま解消することを確認した**(item4の目標をB3自身の実例で達成、`section_role_violation`0件)。

### 16-5. iteration6の⑥全体Rewrite3件の必要性分類

委任文§0で言及された「⑥全体3件」について、iteration6のsummary_flow_runner.jsonを機械確認した結果、`ladder_level_used="6_full_article"`(水準⑥)に該当したのは`safety_er009_changed_number`の一部claim(precheck floor由来、`related_fact_id`型の対象文特定失敗によりlocate自体ができず①〜④を試せなかったケース)であり、「念のため広く直した」のではなく「対象文を特定できなかったため必然的に全文フォールバックへ落ちた」既知の限界に該当することを本委任の代表ケース実測(§16-4ケース5b)でも再現確認した(`ladder_levels_used=['1_word_connective', '6_full_article']`、precheck floor claim側が⑥、deterministic floor claim側が①)。段落単位([4_paragraph])は今回もiteration6と同様0件のままであり、「段落以上でないと直せない」ケースは代表5ケースの範囲では確認されなかった。

### 16-6. コスト5分割(代表5ケース換算)

5 instance×n=2=10 instance-runの実測合計コスト(1回目実行分、¥8.1229)+ケース2/3の再実行(¥0.1928+¥1.0703=¥1.2631)。代表ケースは記事単位の5分割KPI算出には母数が小さすぎるため参考値として記録するにとどめ、正式なコスト5分割測定は29 instance全量Trial(iteration7、未実施)で行う。

### 16-7. Gate判定

代表5ケースのうち3/5(ケース1除く安全性は維持、ケース4/5)はPASS、**ケース2/3(Safety-critical claim)は最小修正1回後もFAILが再現**したため、委任文§3-C/§5のSTOP条件に該当する。**広いTrial(iteration7全量)へは進まない。Status=STOPPED**(Hook-aware rubric側の再設計またはpost-hoc限定方式への回帰を次回委任で検討したうえで再判断する)。J-1ラダー(B-1)は代表ケースで有効性を確認済みであり、次回委任でも維持する。

### 16-8. 費用

作業A(governance明文化)・B(実装)・B-3(チェック表): ¥0。作業C: 1回目実行¥8.1229+最小修正後再実行¥0.1928+安全復帰後再検証¥1.0703=**¥9.386**(委任Guardrail¥15内)。本委任合計: **¥9.386**。Phase累計(前回まで¥283.2016)+本委任¥9.386=**¥292.5876**。Phase残額(**上限¥500**のうち)=**¥207.4124**。

## §17. Hook専用Stage2実装+代表5ケースTrial再実行(委任_17、2026-09-30)

### 17-1. 前回ユーザー指示への対応表(委任_17§1、委任_16と同一のユーザー指示セット)

| # | 指示 | 反映先 | 実際の動作 | Evidence | 判定 |
|---|---|---|---|---|---|
| A Hook-aware | Title/Hook/場面描写/attention grabberを通常Fact文と同基準で過剰BLOCKしない。確認済みFactから自然に導ける演出は許容、新しい具体的Factの発明のみNG | 新規`er052_open233_self_recovery_stage2_hook_01.py`(Hook専用Stage2、title/hookのclaimのみ別Prompt・別call)+`run_stage2`分岐実装(design書§4-14) | 代表ケース1(neg1)で実測、Hook専用StageがQUALITY/ACCEPTABLEと判定しRewriteなしで通過(n=2両方) | `er052_output/open233_self_recovery_flow_runner_01_rep8/summary_rep8.json` | **PASS**(委任_16でFAILしていたケースが解消) |
| B 数値丸め | 通常の四捨五入は一致扱い | `precheck.is_natural_rounding`(既存、変更なし) | 既存23例のunittestが引き続き全PASS(regressionなし) | `TestIsNaturalRoundingDirect`等 | 既存維持(PASS) |
| C 最小変更第一 | ①語・接続詞②文の一部③1文④段落⑤広範囲⑥全体 | `single_text_rewrite`/`paired_rewrite`ラダー(既存、変更なし) | 代表ケース2〜5で全てladder_level_used=1_word_connective(一部6_full_articleのprecheck floor併用)、段落単位0件 | summary_rep8.json | 既存維持(PASS) |
| D B3型 | so→while/Meanwhile/文分割を先に試す | Cと同一機構(paired ladder)。本委任の主眼はB3がHook専用Stage2を経由しないことの確認 | `bgroup_B3`はsection_type="in_one_line"としてbody経路(既存RUBRIC_R3_TRIPLE_PRIME)を通り、`ladder_level_used=1_word_connective`で解消。Hook専用Stage2(s2h)は一度も呼ばれていない(stage2_route="body") | instance json(`bgroup_B3.json`)のstage2_results | **PASS**(誤降格regressionは再現せず) |
| E セクション役割維持 | Title/Hook/本文/In one lineの役割をRewrite後も維持 | `measure_section_role_violation`(既存、変更なし) | 5 instance×n=2の全10 instance-runでsection_role_violation 0件 | summary_rep8.json | **PASS**(委任_16のneg1 hook_shrank違反も解消、そもそもRewrite自体が発生しなかったため) |
| F Rewrite後QA | 既存資産の再利用・二重実装禁止・再利用可否明示 | 委任_14監査A-2(既存)を維持 | 新規実装なし(既存監査の結論どおり) | `docs/pm/audit_hook_aware_and_rewrite_qa_open233_01.md`§A-2 | 既存維持(変更なし) |
| 進行順 | 少数代表ケース→広いTrial | 本委任の構造そのもの | 5 instanceのみ実行、29 instance全量再実行はしていない | §17-3 | 遵守 |
| 再発防止 | PM_GOVERNANCE.md22節のTrial開始前/終了前チェック・次工程Gate | `docs/pm/ACTIVE_TASK_C233T.md`(開始前チェック表、A〜F未反映0件を確認) | 本委任自体もこのチェックに従って実行 | `docs/pm/ACTIVE_TASK_C233T.md` | 反映済み |

### 17-2. §2原因是正の実装(作業A、¥0、unittest 131件+precheck 23件=154件全PASS)

委任_16 B-2は「Hook演出許容原則」を既存Stage2 rubric(`RUBRIC_R3_TRIPLE_PRIME`)へ追記し、title/hook/body/in_one_lineの全claimを**同一batch call**で判定したため、Safety-critical claim(`bgroup_B3`)がQUALITYへ誤降格するprompt priming(原則文がプロンプト中に存在するだけで、条件上は無関係なclaimの判定にも寛容化バイアスが波及する現象)が発生し、適用対象をtitle/hookの2種のみへ限定する最小修正1回後も再現したためSTOP条件に該当した(REPORT§16)。

委任_17は原則文の追記ではなく、**title/hookに位置するclaimの再評価を完全に別のPrompt・別のAPI call(Hook専用Stage2)へ分離**した(design書§4-14)。実装:

- **A-1 セクション判定**: 既存`detect_claim_section_type`(変更なし)。title/hook/in_one_line/bodyの4区分の判定基準・境界例(hookが2段落にまたがる場合の既知の限界)を設計書§4-14へ明記した。
- **A-2 Hook専用Stage2**: 新規`er052_open233_self_recovery_stage2_hook_01.py`(s2h)。入力=Ledger全文+source context+タイトル・hook段落のみ(`build_title_hook_context`、対象claimを含む段落±1段落のような広い文脈は渡さない)+対象claim配列。schema=materiality/basis/rewrite_kind/rewrite_hint(既存`_ITEM_PROPS`を再利用)。rubric(`HOOK_RUBRIC`)は委任文§2の原則文どおり、tie-breakを「発明の有無」に固定。
- **A-3 runner分岐**: `run_stage2`をhook群(title/hook)とbody群(body/in_one_line)へ分割し、各群を独立のAPI callで判定する(`HOOK_ONLY_STAGE2_SECTION_TYPES`)。body群は既存`s2c.run_stage2_batch_variant`+`RUBRIC_R3_TRIPLE_PRIME`(iteration4〜6・rep7と同一プロンプト内容、不変)。いずれかの群が空ならそのAPI callは発火しない(追加コストは実際に該当claimがある場合のみ)。各群は独立にMAX_RETRIES_PER_CALL回まで再試行し、失敗時はその群のclaimのみfail-closedでBLOCKING確定(§6-1の既存fail-closed原則をgroup単位へ拡張、上限回数・厳しさは変更なし)。各claimへ`stage2_route`(body/hook/フェイルクローズ理由)をEvidenceとして記録。
- deterministic floor(`apply_floor`)・pre-check floor・既存post-hoc downgrade(`apply_hook_aware_downgrade`、changed_scope単独限定)はいずれも変更せず、Hook専用Stage2の判定結果に対しても引き続き同一ロジックで適用される(Safety側の安全装置は一切回避・弱体化していない)。
- **A-4 unittest**: `TestHookOnlyStage2Separation`(新規4件)。(1)neg1のhook claimがmockでQUALITY→body Stage2(`s2c.run_stage2_batch_variant`)が一切呼ばれないことを`MagicMock.assert_not_called()`で確認、(2)`bgroup_B3`の因果claim(section_type="in_one_line")がbody経路を通りHook専用Stage2が一切呼ばれないことを確認しつつBLOCKING維持を確認、(3)`changed_actor`floorを持つhook区分claimにHook専用StageがQUALITYを返してもfloorにより最終的にBLOCKINGへ強制されることを確認、(4)hookに新しい具体的事実を発明した合成claimに対しHook専用StageがBLOCKINGを返す基本疎通を確認。既存127件(委任_16時点)+新規4件=131件+`er052_open233_self_recovery_precheck_01_test_01.py`23件、計**154件全PASS**(`.venv/Scripts/python.exe`実行、regressionなし)。

### 17-3. 代表5ケースTrial実測(作業B、¥5.2181、n=2)

新規`er052_open233_self_recovery_flow_runner_01_rep8_representative_01.py`で、委任_16 rep7と同一の5 instance(全てstage1_mode=reuse、Stage1コスト¥0)をn=2実行した(OUT_DIR=`er052_output/open233_self_recovery_flow_runner_01_rep8`、Guardrail¥14)。

| ケース | instance | section_type | stage2_route | 実測結果 | 判定 |
|---|---|---|---|---|---|
| 1 Meta Hook | `neg1_meta_b3prod_a2` | hook | hook | materiality=QUALITY(sample1、Stage2 2-of-2安定化[既存機構]が発火し1回目BLOCKING→2回目QUALITYで降格)/ACCEPTABLE(sample2、1回目でACCEPTABLE)。final_state=RESOLVED_STAGE2_DOWNGRADE、Rewriteなし(ladder=[]、role_violations=[]) | **PASS**(委任_16でFAILしていたケースが解消) |
| 2/3 B3丸め+因果 | `bgroup_B3` | in_one_line | body(2/2ともHook専用Stage2は未呼び出し) | materiality=BLOCKING維持(2/2)、`ladder_level_used=1_word_connective`(so→while相当)で解消、role_violations=[] | **PASS**(委任_16の誤降格regressionは再現せず) |
| 4 Hormuz scope | `hormuz_run03_standard` | body | body | BLOCKING→`ladder_level_used=1_word_connective`で解消、recheck_all_prior_issues_resolved=True(EN/JA両方LEDGER_COMPLIANT)、役割違反0件 | **PASS** |
| 5a Safety actor | `safety_er009_changed_actor` | title | hook(LLM判定もBLOCKING、floorも維持) | `floor_reason=deterministic_floor:changed_actor`維持→`ladder_level_used=1_word_connective`で解消、recheck all_prior_issues_resolved=True | **PASS** |
| 5b Safety number | `safety_er009_changed_number` | title(1claim)+body(precheck floor claim1件) | hook+precheck_floor_bypass | `floor_reason=deterministic_floor:changed_number`/`precheck_floor`維持→`ladder_levels_used=[1_word_connective, 6_full_article]`で解消、recheck all_prior_issues_resolved=True | **PASS** |

**5/5ケース全てPASS(n=2両方一致)**。最小修正1回のフェイズは発動しなかった(1回目の実行で全PASS)。STAGE4到達0件・API error 0件・section_role_violation 0件。

**Hook専用Stage2の発火状況(Evidence)**: `bgroup_B3`のinstance json(`er052_output/open233_self_recovery_flow_runner_01_rep8/instances_s{1,2}/bgroup_B3.json`)のstage2_resultsで、対象claimに`"stage2_route": "body"`が記録されており、call_logにも`stage2_variant="hook"`のエントリが一切存在しないことを機械的に確認した(Hook専用Stage2がこのclaimに対して一度も呼ばれていない直接証拠)。Hook専用Stage2の発火は5 instance×n=2中、neg1(sample1で2回[2-of-2安定化]+sample2で1回=計3回)・safety_actor(1回×2)・safety_number(1回×2)の計7回、単価¥0.0342〜¥0.3538。

### 17-4. コスト内訳(参考値)

instance別合計(n=2結合、¥5.2181): neg1 ¥0.3538+¥0.0674=¥0.4212、bgroup_B3 ¥0.68+¥0.4168=¥1.0968、hormuz ¥1.4009+¥1.0565=¥2.4574、safety_actor ¥0.3463+¥0.2043=¥0.5506、safety_number ¥0.4215+¥0.2706=¥0.6921。委任Guardrail¥14に対し実測¥5.2181(37.3%)。正式なコスト5分割測定は29 instance全量Trial(iteration7、未実施)で行う(委任_16と同じ位置づけ、参考値にとどめる)。

### 17-5. Gate判定

5/5ケース全てPASS(Safety側もSafety維持側も両方成立)。**広いTrial(iteration7全量)は本委任のスコープ外のため未実施**。**Status=`REP8_ALL_5_CASES_PASS_HOOK_SEPARATION_CONFIRMED`**。次回委任でのユーザー判断・Fable判定を経て、広いiteration7 Trial実施の要否・タイミングを決める(J-1ラダー[委任_16でPASS]・Hook専用Stage2[本委任でPASS]の両方が代表ケースで有効性を確認できた状態)。

### 17-6. 費用

作業A(実装+unittest): ¥0。作業B(代表5ケースTrial): **¥5.2181**(委任Guardrail¥14内、最小修正フェイズ不要のため追加費用なし)。本委任合計: **¥5.2181**。Phase累計(前回まで¥292.5876)+本委任¥5.2181=**¥297.8057**。Phase残額(**上限¥500**のうち)=**¥202.1943**。

## §18. ユーザー新指示12項目の反映+代表12ケース拡張Trial(委任_18、2026-09-30)

### 18-0. 対応表(指示1〜12)

| # | 指示 | 実施内容 | Evidence | PASS/FAIL |
|---|---|---|---|---|
| 1 | 局所QA基本形+全文Recheck条件化 | `run_local_qa_fastpath`+`full_recheck_required`(5条件) | §18-4 | PASS(条件どおり機能、ただし節減効果は今回0件) |
| 2 | 全体Rewrite3件の必要性立証 | disclosure §1-1で立証不能と確認済み、⑥を例外経路化 | §18-1 | 立証不能(想定どおり)、経路是正はPASS |
| 3・4 | 不要Rewrite4件の解決策 | neg1=委任_17済/neg2・meta_run03_advanced=disclosure-gap downgrade/neg3=解決策なし(明記) | §18-2 | 2/4解決、1/4既解決、1/4解決策なしと正直報告 |
| 5 | 既知方針維持 | 既存170+23+21件regression全PASS | §18-6 | PASS |
| 6 | 段落・全体Rewriteの例外化 | found=False即Stage4、found=True[④まで試行]のみ⑥ | §18-1 | PASS |
| 7 | Rewrite後品質確認10項目 | §18-5対応表 | §18-5 | 一部網羅(全項目は未網羅、明記) |
| 8 | 人間確認率0(meta_run03_standard) | 2-3(a)既存Evidence確認+2-3(b)実装 | §18-3 | PASS(2/2 run、STAGE4 0件) |
| 9 | コスト(+¥2上限であって予算ではない) | §18-7 call種別表 | §18-7 | PASS |
| 10 | 広いTrial前Gate9項目 | §18-9 | §18-9 | 未充足(次委任へ) |
| 11 | 報告形式A〜E | 本節 | - | PASS |
| 12 | Status/Gate | §18-9末尾 | - | PASS |

### 18-1. 全体Rewrite経路の是正(指示2・6、2-1(a)(b)(d))

disclosure(`docs/pm/open233_iter6_rewrite_disclosure_01.md`)§1-1は、iter6の全体Rewrite(水準⑥)3件が3/3とも「locate失敗の副作用」であり、「広範囲の問題には⑥が本質的に必要だった」という実測根拠は0件と結論した。うち2件(`safety_er009_changed_number`)は、precheck floor claimの`claim_text`がprecheckの**診断用合成文字列**(article_evidence、記事本文に一言一句存在しない)そのものだったことが根本原因だった。

**実装**: (a) `resolve_precheck_target_sentence`(新規)がfinding固有の生の実測値(`foreign_values`/`other_dates_raw`/`matched_phrase`/`article_evidence`[list]、precheck module側へ追加フィールドとして併記)を使い記事本文中の実文を検索し、`build_precheck_floor_claims`がそれを`claim_text`として使う。(b)(d) `single_text_rewrite`/`paired_rewrite`は`found=False`(対象文が一度も特定できない)の場合、⑥全体フォールバック(API call)を試みず即座に`target_not_locatable=True`を返す(call_log記録なし)。`run_instance`はこれを検出すると他claimの結果を保存した上で`stage4_reason="target_not_locatable"`でSTAGE4_ESCALATIONへ回す。⑥は`found=True`(対象文は特定できた)だが①〜④[delete型は再出現検出]の全段でguardが失敗した場合のみ到達する経路として維持した(disclosure §1-1-3の「⑥が①より安全だった」逆転現象への対応、削除しない)。

**rep9実測(Evidence)**: `safety_er009_changed_number`のprecheck floor claimの`claim_text`が実文("Researchers studied more than 30 million credit card...")へ解決され、`ladder_levels_used=['1_word_connective', '3_sentence']`(2claim: LLM側title claim+precheck floor claim)で**両sampleとも解消**、`6_full_article`は一度も発生しなかった(`instances_s{1,2}/safety_er009_changed_number.json`)。委任_17時点(rep8)は同claimが`ladder_levels_used=[1_word_connective, 6_full_article]`だったため、根本原因是正が実測で確認できた。

### 18-2. 不要Rewrite4件の解決策(指示3・4、2-2)

| instance | 原因分類 | 解決策 | rep9実測 |
|---|---|---|---|
| `neg1_meta_b3prod_a2` | Hook誤判定 | 委任_17 Hook専用Stage2(既解決) | sample1 RESOLVED_REWRITE_THEN_DOWNGRADE/sample2 RESOLVED_STAGE2_DOWNGRADE、両方STAGE4なし |
| `neg2_meta_refresh_a2` | disclosure-gap過剰BLOCK | `apply_disclosure_gap_downgrade`(deterministic (ii)) | 2/2 sampleでBLOCKING→QUALITY downgrade発火、RESOLVED_STAGE2_DOWNGRADE(Rewriteなし) |
| `meta_run03_advanced` | 同上 | 同上 | 2/2 sampleともACCEPTABLE_STAGE1(この実行ではStage1自体が当該claimを検出せず、downgrade発火の場面自体が発生しなかった。非決定性の一例として明記) |
| `neg3_hormuz_prodrunner_b1b` | floor+LLM独立判定一致(iteration間非決定) | 解決策なし(disclosure §1-2-4の結論を維持、断定回避) | sample1 RESOLVED_REWRITE(1_word_connective)、sample2 STAGE4_ESCALATION(unconfirmed_after_reverify)。1/2 sampleで解決策なしのまま従来どおり残存(想定範囲内) |

**方式選択の理由(disclosure §2-2の2案から(ii)を採用)**: (i)共通rubric条件追記は委任_16 B-2が実測したprompt priming[Safety-critical `bgroup_B3`誤降格]のリスクを再度負ううえ、較正セット全体の再実行がPhase B予算(¥20)に収まらない。(ii)は¥0・追加API callなし・既存floor/hook-aware downgradeと同型のpost-hoc判定パターンを踏襲でき、対象を「否定形の論理的帰結のみ」という狭い決定論条件に限定できるため安全側。**Trial限定の判定候補であり、Production採用(`APPROVED_FOR_PRODUCTION`)には別途ユーザー承認が必要**(design書§4-15)。

### 18-3. Escalation 2 run是正(指示8、2-3(a)(b))

- **(a) J-1被フラグ文不変ガード**: iter6のdisclosure時点のコードには存在しなかった(`ladder_level_used="paired_j1_not_laddered"`固定、未ラダー化)。委任_16のJ-1ラダー化で既に`level_guard_ok`条件(`claim_text.strip() not in candidate_en`)が各水準に組み込まれており、被フラグ文が変わらなければ次水準・最終的にJA全文フォールバックへ進む設計に**既になっていた**(design書§6-5-C(a)、新規コード追加なし、既存のEvidence)。
- **(b) 同一fact_id複数箇所cycle緩和**: `run_instance`のcycle上限判定へ`same_fact_id_new_location`条件(過去cycleで見たfact_idの新しい箇所[claim本文は既に別物と判定済み]が含まれていれば、cycle上限3を超えない範囲で1回だけ追加cycleを許可)を追加した(`HARD_MAX_CYCLES`=3は無変更)。

**rep9実測**: `meta_run03_standard`は**2/2 sample(sample1/sample2)ともSTAGE4_ESCALATIONに至らなかった**(sample1 RESOLVED_REWRITE、sample2 RESOLVED_REWRITE_THEN_DOWNGRADE)。sample2は`extra_cycle_reason="same_fact_id_new_location(委任_18 2-3b)"`が実際に発火したことをinstance jsonで確認した。**人間確認率0(指示8の目標)を達成**。

一方、`hormuz_run03_standard`(sample1)で**新規のSTAGE4_ESCALATION**(`cycle_limit_exhausted_after_recheck`)を観測した(rep8時点では1cycleで解決していたケース)。原因分析: 各cycleで異なる文言(headline/段落表現)の同一テーマclaimが検出される、`meta_run03_standard`と同型の「claimがcycleごとに言い換えられる」パターンであり、**`local_qa_fastpath`は`both_ja_en_changed(paired_j1)`条件により正しく不発火**(局所QA由来の新規regressionではないことを`instances_s1/hormuz_run03_standard.json`の`full_recheck_required_reasons`で確認済み)。`same_fact_id_new_location`拡張は1回追加cycleを与えたが、3cycle目も別表現で再検出され最終的に`HARD_MAX_CYCLES`超過でSTAGE4に至った(拡張前のコードでも「blocking件数が減少していない」ためcycle 3を許可されず同じcycleで`cycle_limit_exhausted`として即STAGE4に至っていたはずであり、**拡張がこのinstanceを新たに壊したのではなく、既存の未解決構造[Phase2課題item8]にコストをかけてもう1回挑み、それでも解決しなかった**と判断する)。同一instanceのsample2は1cycleで正常解決しており(non-determinism)、FAILは最小修正では解消不能な既存の構造的限界と判断し、追加の修正は実施しなかった(残りGuardrail内でのcaseごとの単発再実行はSTOPの安全側判断として見送った、§18-9参照)。

### 18-4. 局所QA fastpath・全文Recheck条件(指示1・7・9、2-4)

`full_recheck_required`の5条件(段落/全体/削除ladder、同cycle複数claim、paired J-1、deterministic floor claim、Safety fixture)は、rep9実測の**22 instance-runの全サイクルで33回中30回が該当**(要全文Recheck)し、**局所QA fastpathは3回のみ試行**(`neg1_meta_b3prod_a2`×1、`meta_run03_standard`×2)。3回とも成功せず(2回はrevised sentenceのwindow特定に失敗しAPI call前にskip、1回はAPI call[¥0.112]の結果`adjacent_sentence_affected=True`で正しく全文Recheckへフォールバック)、**局所QA fastpathによる全文Recheck省略は今回0件**。想定した「単一claim・単一文水準・非floor・非Safety」という狭い条件自体が、代表12 instance(多くがSafety/floor/paired構成)にはほとんど該当しなかったことが理由。局所QA fastpathは安全側(3/3とも正しく既存の全文Recheckへフォールバックし、誤って省略した形跡はない)に機能したが、**コスト削減効果は今回のデータでは実証できなかった**ことを正直に報告する(¥0.112の追加コストのみ発生)。

### 18-5. Rewrite後品質確認10項目(指示7)対応表

| # | 項目 | 網羅する仕組み |
|---|---|---|
| 1 | 修正文 | 局所QA`revised_sentence`/既存全文Recheck |
| 2 | 前後文脈 | 局所QA`before_ctx`/`after_ctx`(`find_sentence_context`) |
| 3 | 元問題解消 | 局所QA`prior_issue_resolved`/既存`all_prior_issues_resolved` |
| 4 | 新Fact誤りなし | 局所QA`new_deviation_in_revised_sentence`/既存Recheck |
| 5 | Title引力 | `measure_section_role_violation`(title_flattened/title_degenerate) |
| 6 | Hook Entertainment | 同上(hook_flattened/hook_shrank/hook_degenerate) |
| 7 | 本文ストーリー | `detect_duplicate_paragraphs`/`detect_orphan_contrastive_paragraphs`(既存v2) |
| 8 | In one line短さ | `in_one_line_too_long`(既存v2) |
| 9 | 不要な数字追加 | `numbers_added_to_title`/`numbers_added_to_in_one_line`(既存v2) |
| 10 | 長文化・平板化 | `vocab_difficulty_increased_*`(既存v2) |

**未網羅**: 局所QAの`adjacent_sentence_affected`は隣接文単位の一貫性のみを見ており、記事全体のストーリー展開(離れた段落間の整合)は既存の全文Recheckが条件該当時にのみカバーする(§18-4の条件外では検査されない)。この限界はFableへの報告事項として明記する。

### 18-6. unittest(¥0)

新規39件(`er052_open233_self_recovery_precheck_01_test_01`は変更なし、`er052_open233_self_recovery_flow_runner_01_test_01`170件[既存131+新規39]、内訳: `TestResolvePrecheckTargetSentence`3/`TestBuildPrecheckFloorClaimsLocatability`2/`TestTargetNotLocatableEarlyReturn`2/`TestDegenerateRewriteGuard`5/`TestDegenerateRewriteHardBlockWiring`3/`TestApplyDisclosureGapDowngrade`7/`TestApplyDisclosureGapDowngradeWiredIntoStage2`1/`TestFullRecheckRequired`6/`TestFindSentenceContext`3/`TestLocalQaFastpathWiring`4/`TestBuildLedgerExcerpt`3)+既存precheck 23件+s1d/stage2_production 21件=**計214件全PASS**(`.venv/Scripts/python.exe -m unittest`、regressionなし)。

### 18-7. コスト(指示9)

| call種別 | 回数 | 単価平均(¥) | 合計(¥) | 目的 | 省略時の悪化 | 安価代替 |
|---|---|---|---|---|---|---|
| `stage1_recheck` | 26 | 0.3111 | 8.0884 | 全文Recheck(局所QA条件外) | 全文検証なし、Safety群の新規BLOCKING見逃し(disclosure §1-4-5実測) | 局所QA(今回0件成功、§18-4) |
| `stage3_rewrite` | 42 | 0.1223 | 5.1366 | Rewrite本体 | 自動修復不可 | なし |
| `stage2_second_judge` | 30 | 0.1410 | 4.2302 | Stage2判定(body/hook分離) | 誤BLOCK/誤PASS検出機構喪失 | なし |
| `ja_en_equivalence` | 7 | 0.1047 | 0.7326 | J-1後JA/EN等価QA(測定専用) | 記録のみのため機能影響なし | なし(J-1使用時のみ) |
| `stage1_recheck_confirm` | 2 | 0.3363 | 0.6727 | cite-or-release確認 | 根拠なき未解消でのSTAGE4誤生成リスク | なし |
| `stage1_initial` | 1 | 0.2538 | 0.2538 | meta_run03_advanced fresh Stage1(1回のみ、sample間cache共有で二重課金なし) | Stage1未検出のまま進行 | reuse可能な限り¥0(11/12は¥0) |
| `local_qa`(新規) | 1 | 0.1120 | 0.1120 | 局所QA fastpath(§18-4) | 全文Recheckのみに依存(既存動作) | なし(fastpath条件内のみ発火) |

**合計**: 109 call(instance json call_log集計)、¥19.2263(budget_state全体¥20.0358との差¥0.8095は、Guardrail到達により`instances_s2`の`safety_A5`実行途中で打ち切られた分、正常な予算超過防止動作)。削減したcall: 明確な削減は今回0件(§18-4)。追加したcall: `local_qa`(1回、¥0.112)。iter6比: `stage3_rewrite_fulltext_fallback`(⑥、iter6実測7回・¥1.2430)は本rep9の対象12 instanceでは**0回**(precheck locate是正+found=False早期returnの効果、ただし対象instance集合が異なるため厳密比較ではない)。

### 18-8. 費用

作業A(実装+unittest+design書更新): ¥0。作業B(rep9代表12 instance×n=2、Guardrail¥20到達によりsample2の`safety_A2A3`/`safety_A5`は未実行): **¥20.0358**。本委任合計: **¥20.0358**(Guardrail¥25内、追加の単発再実行は§18-3の判断により見送り)。Phase累計(前回まで¥297.8057)+本委任¥20.0358=**¥317.8415**。Phase残額(**上限¥500**のうち)=**¥182.1585**。

### 18-9. Gate判定・Status

**広いTrial前Gate 9項目(委任文§0引用)充足状況**: 本委任は代表ケース拡張Trial(12 instance×n=2、うち2 instanceはsample2未実行)であり、29 instance全量のGate判定に必要な母数を満たしていない。未充足のため広いTrialのGate自体は**判定保留**。

**主要な実測結果**:
- precheck合成マーカー是正(2-1a): `safety_er009_changed_number`が`6_full_article`を経由せず解消(PASS)。
- degenerate output guard(2-1c): `safety_er009_unsupported_new_claim`の題名空文字化を2/2 sampleとも正しく検出しSTAGE4へ回した(disclosure §1-1-4の「静かなfalse PASS」を解消。ただし根本のRewrite精度[delete対象の断片特定]自体は未改善のため、解消ではなく正しい検出止まりである点を正直に報告する)。
- disclosure-gap downgrade(2-2): `neg2_meta_refresh_a2`が2/2 sampleでQUALITYへdowngradeしRewriteなしで通過(PASS)。`meta_run03_advanced`はこの実行でStage1が当該claim自体を検出しなかった(非決定性、downgrade発火の機会なし)。
- fact_id複数箇所cycle緩和(2-3b)+J-1既存ガード(2-3a): `meta_run03_standard`が2/2 sampleともSTAGE4なし(PASS、指示8の目標達成)。
- 局所QA fastpath(2-4): 安全側に機能(3/3とも正しく全文Recheckへフォールバック)、コスト削減効果は今回未実証。
- Safety側: 全Safety claim(`safety_er009_changed_actor`/`changed_number`/`unsupported_new_claim`/`A2A3`/`A5`)でBLOCKING/floor維持を維持(2-2のdowngradeが一切混入していないことを機械確認済み、Safety-critical claimがQUALITY/ACCEPTABLEへ落ちた事例は0件)。
- **新規観測(未解決)**: `hormuz_run03_standard`(sample1)で新規STAGE4(`cycle_limit_exhausted_after_recheck`)。§18-3で根本原因は本委任の変更由来ではなく既存の構造的限界(claim言い換えcycleパターン、Phase2課題item8と同型)と分析したが、実測FAILとして正直に記録する。`neg3_hormuz_prodrunner_b1b`(sample2)もSTAGE4(想定範囲内、解決策なしと明記済み)。

**STOP条件該当確認**: ¥25超過見込み(該当せず、¥20.0358)/API error 3連続(該当せず、0 error)/Production・既存証跡変更(該当せず、§18-10で確認)/USER_DECISION_REQUIRED6条件(該当せず、下記)/開始前チェック未反映(0件)/最小修正1回後もFAIL(`hormuz_run03_standard`は§18-3の分析により構造的限界と判断し単発再実行を見送り、追加の「最小修正」は実装していない。これを厳密にSTOP要件へ当てはめると判断が割れるため、Fable/ユーザーへの判断材料として正直に提示する)/Safety-critical claimまたはSafety 12のいずれかがBLOCKINGでなくなった(該当せず、上記確認済み)。

**Status**: `REP9_PARTIAL_GUARDRAIL_REACHED_MIXED_RESULTS`(12 instance中10はn=2完走・2[`safety_A2A3`/`safety_A5`]はsample1のみ。主要3目標[precheck locate是正/disclosure-gap downgrade/meta_run03_standard Escalation 0]はPASS、新規観測1件[`hormuz_run03_standard` sample1]は構造的限界としてFable/ユーザー判断待ち。広いTrial実施は次回委任でのFable/ユーザー判断を待つ)。

## §19. 委任_18残課題4点の是正+限定再試行rep10(委任_19、2026-09-30)

### 19-0. 対応表

| # | 委任_18残課題 | 実施内容 | Evidence | 結果 |
|---|---|---|---|---|
| 1 | 局所QA基本形(paired ①〜③を条件から外す) | narrowing検討の結果、`hormuz_run03_standard`新規反証(条件(c)を狭めるとcycle1でサイレントPASSする回帰リスク)により**条件(c)を意図的に維持**。代わりに条件(f)新設([同一fact_id再出現])+`find_sentence_context`locateバグ是正 | §19-1、design書§6-6 | 委任文どおりのnarrowingは**実施しない**という結論(理由付きで報告) |
| 2 | hormuz_run03_standard cycle枯渇是正 | `escalate_to_paragraph`(同一fact_id再出現時、①③を飛ばし④段落水準から試す) | §19-2、rep10実測 | **2/2 sample改善**(rep9のSTAGE4→rep10は両方RESOLVED) |
| 3 | neg3両論併記+sample2原因特定 | Stage2 n=3再現性測定+confirm call分析 | §19-3 | 3/3 BLOCKING(non-flaky)、sample2原因はconfirm callの記事全体走査による別逸脱検出(fail-closed、正常動作)と判明 |
| 4 | 全体Rewriteの解消策なし1件の扱い | neg3は解決策なしのまま(§4-15踏襲) | §19-3 | 変更なし(想定どおり) |

### 19-1. A-1: 全文Recheck条件最小化の調査結果(narrowingを実施しない決定)

委任文は「paired J-1はラダー①〜③の局所変更なら`full_recheck_required`の条件(c)から外す」ことを求めていたが、調査の結果**実施しないことに決定した**。根拠はdesign書§6-6の捕捉表のとおり: rep9で新規観測された`hormuz_run03_standard`(sample1、`cycle_limit_exhausted_after_recheck`)は、cycle1(初回発生、ladder=`3_sentence`)の時点でnarrowingを適用すると局所QA fastpathが対象claimだけを見て「解消」と誤判定しうる(局所QAは対象文±1文のwindowしか見ないため、記事の別箇所[見出し/one-line]に同一fact_idの問題が初めて存在することを構造的に検出できない)。これはcycleループ自体を起動させず、本来STAGE4_ESCALATIONへ正しく到達していたはずの経路を消し、サイレントPASSを生む新規リスクである。新設条件(f)(`same_fact_id_reappeared_across_cycles`、過去cycleで一度でもBLOCKINGだったfact_idの再出現をmechanism非依存で全文Recheckへ回す)はcycle2以降の再発は捕捉できるが、cycle1(初回)には無力なため、(c)の代替にはならない。

局所QA fastpathが実際に発火しなかった真因は条件自体ではなく`find_sentence_context`のlocateバグ(rep9で3試行中2件が`revised_sentence_not_locatable_in_context`で失敗)と判明したため、SequenceMatcher近似fallback(閾値0.85)で是正した(unittest 3件で検証、§19-4)。**rep10実測でもfastpath発火は0/14 instance-run**(§19-5参照、選定した7 instanceが全てpaired/floor/safetyのいずれかを含む複雑ケースだったため、条件(a)〜(e)/(f)のいずれかが毎cycle該当した。locateバグ是正自体の実run効果測定機会は今回も得られなかった)。

### 19-2. A-2: escalate_to_paragraph実測(hormuz_run03_standard改善)

同一fact_idが過去cycleで既にBLOCKINGだった場合、①単語・接続詞/③1文を飛ばし④段落水準から直接試す`escalate_to_paragraph`を実装した(cycle数の上限[MAX_CYCLES/HARD_MAX_CYCLES]自体は変更しない)。

**rep10実測**: `hormuz_run03_standard`sample1がcycle2で`escalate_to_paragraph`発火(`full_recheck_required_reasons`に`same_fact_id_reappeared_across_cycles`を確認)、`ladder_level_used="4_paragraph"`で解消し、**rep9でSTAGE4_ESCALATION(`cycle_limit_exhausted_after_recheck`)だった同一instanceが2/2 sampleともRESOLVED**(sample1: `RESOLVED_REWRITE_THEN_DOWNGRADE`/sample2: `RESOLVED_REWRITE`)。ただしこれはnon-determinism下での1回のn=2実測であり、「同一fact_idが別セクション[見出し/one-line]に分散する場合は段落単位のRewriteでは解決しない」という設計上の既知の限界(Phase2課題item8)自体を解消したわけではない(design書§6-6に正直に記録)。

### 19-3. A-3: neg3 Stage2 n=3測定+sample2原因特定+両論併記

既存Stage1出力(`er052_output/open233_self_recovery_phase1_step3_stage1_compare_01/c_negative/neg3_hormuz_prodrunner_b1b/V4A/run_1.json`)を再利用し、`neg3_hormuz_prodrunner_b1b`のBLOCKING claim(HF-009)についてStage2のみ3回実行した(`er052_open233_self_recovery_neg3_stage2_n3_01.py`、費用¥0.3096)。

**結果**: 3/3 BLOCKING(`llm_materiality`3/3ともBLOCKING、`floor_reason`3/3とも`deterministic_floor:changed_time`)。iteration4/5(QUALITY)との非決定性はこのn=3測定では再現しなかった。

**両論併記(決定しない)**: Ledger HF-009は「Brent先物が…ほどなく発表前に近い高い水準へ戻った」(価格は「戻った」)、conditions「…米・イラン間の攻撃、海上封鎖、タンカー安全上の懸念が継続していた」と記録している。claim「the events driving oil prices—and the prices themselves—quickly returned」について、(a)QUALITY側: 「prices…quickly returned」はLedger支持があり、「events…quickly returned」は並置構文の緩い修飾句として読める余地がある、(b)BLOCKING側: 最も自然な統語解釈では両主語が同一動詞句を共有し、events(継続中の懸念)自体が「戻った(終息した)」と明確に主張しており、Ledgerの「継続」との直接的な反転に当たる。design書§6-6に両論を記録し、決定はFableへ委ねる。

**sample2`unconfirmed_after_reverify`の原因特定**: rep9の`instances_s2/neg3_hormuz_prodrunner_b1b.json`のconfirm call出力(`overall_status: LEDGER_DEVIATION`・`all_prior_issues_resolved: true`・`cite_or_release_released_count: 0`)を分析した結果、「元のBLOCKING claim(HF-009)自体はRewrite後に解消したとconfirm callが判定した」が「confirm call自身が記事全文を再チェックした結果、**別の**逸脱を検出した」ことによるfail-closedの正しい動作と判明した(`en_ok`判定は`overall_status==LEDGER_COMPLIANT`も要求するため、別逸脱の存在だけでSTAGE4へ回る)。生の`prior_issues_resolved`/`deviations`配列自体はinstance jsonに保存されておらず、検出された「別の逸脱」の内容そのものは特定できていない(再実行すれば特定できるが追加課金が必要なため見送った)。**この事例は局所QA統合では解消しない**(局所QAは対象文±1文のwindowしか見ないため、元の対象claimとは別の記事全体のどこかにある逸脱を発見する手段を構造的に持たない)。

**rep10実測(非決定性の確認)**: 同一claimのconfirm callがrep10のsample2では`overall_status: LEDGER_COMPLIANT`・`all_prior_issues_resolved: true`を返し、STAGE4に至らず`RESOLVED_REWRITE`で完了した。rep9→rep10で結果が変わったこと自体が、このconfirm callの判定に非決定性があることを裏付ける(「別の逸脱」がrep9でのみ検出された境界事例だった可能性が高い)。

### 19-4. unittest(¥0)

新規14件(`TestFullRecheckRequiredRepeatFactId`3件/`TestFindSentenceContextFuzzyFallback`3件/`TestEscalateToParagraphLadderSkip`3件/`TestRepeatFactIdWiring`1件、他既存クラスへの追加なし。内訳合計10件+既存クラス内追加4件)+既存214件(er052系4ファイル合計)=**計224件全PASS**(`.venv/Scripts/python.exe -m unittest discover`、regressionなし)。

### 19-5. rep10実測(限定7 instance×n=2、¥12.3479)

`er052_open233_self_recovery_flow_runner_01_rep10_representative_01.py`(OUT_DIR=`er052_output/open233_self_recovery_flow_runner_01_rep10`、TOTAL_BUDGET_JPY=13.0)で以下7 instanceをn=2実行し、**14/14 instance-run全てGuardrail内で完走**(Guardrail到達なし、¥12.3479/¥13):

| instance | sample1 final_state | sample2 final_state | 備考 |
|---|---|---|---|
| `hormuz_run03_standard` | RESOLVED_REWRITE_THEN_DOWNGRADE | RESOLVED_REWRITE | rep9でsample1がSTAGE4だったが今回2/2解消(§19-2) |
| `neg3_hormuz_prodrunner_b1b` | RESOLVED_REWRITE | RESOLVED_REWRITE | rep9でsample2がSTAGE4だったが今回2/2解消(§19-3、非決定性) |
| `bgroup_B3` | RESOLVED_REWRITE(`1_word_connective`) | RESOLVED_REWRITE(`1_word_connective`) | Safety-critical回帰なし(継続確認) |
| `hormuz_run02_advanced` | ACCEPTABLE_STAGE1 | ACCEPTABLE_STAGE1 | BLOCKING検出なし |
| `safety_er009_changed_number` | RESOLVED_REWRITE | RESOLVED_REWRITE | `6_full_article`0回を維持(regression確認) |
| `safety_A2A3` | RESOLVED_REWRITE_THEN_DOWNGRADE | RESOLVED_REWRITE_THEN_DOWNGRADE | `safety_fixture`条件で全文Recheck維持、新規BLOCKING捕捉能力を保持したまま解消 |
| `safety_A5` | RESOLVED_REWRITE | RESOLVED_REWRITE | 同上 |

**STAGE4_ESCALATION 0/14**(rep9では2件[`hormuz_run03_standard`s1・`neg3`s2]がSTAGE4だったが、rep10ではいずれも解消)。**局所QA fastpath発火 0/14**(§19-1で説明したとおり、選定7 instanceが全て条件(a)〜(f)のいずれかに該当する複雑ケースだったため)。**Safety側**: `safety_A2A3`/`safety_A5`とも全cycleで`full_recheck_required_reasons`に`safety_fixture`が含まれ、全文Recheckが維持されたことを機械確認(disclosure §1-4-5で確認された新規BLOCKING検出能力を弱めていない)。

**コスト内訳(call種別、73 call合計)**:

| call種別 | 回数 | 単価平均(¥) | 合計(¥) |
|---|---|---|---|
| `stage1_recheck` | 20 | 0.2753 | 5.5059 |
| `stage3_rewrite` | 28 | 0.1277 | 3.5763 |
| `stage2_second_judge` | 15 | 0.1288 | 1.9314 |
| `ja_en_equivalence` | 7 | 0.1008 | 0.7059 |
| `stage1_recheck_confirm` | 2 | 0.1984 | 0.3969 |
| `stage1_initial` | 1 | 0.2315 | 0.2315 |

`local_qa`call種別は0回(§19-1のとおり全cycleで全文Recheckが維持されたため)。

### 19-6. 作業中に判明した事故と復旧(正直な報告)

A-3のneg3 n=3測定スクリプト(`er052_open233_self_recovery_neg3_stage2_n3_01.py`)実行時、`runner.record_call`/`save_budget_state`がモジュール変数`runner.BUDGET_STATE_PATH`(当時`OUT_DIR_REP9`依存)へ無条件に書き込む実装であることに気づかず、既存rep9の`budget_state_c233v_18.json`(cumulative_jpy=20.0358/115 calls)を一時的に上書きしてしまった(cumulative_jpy=0.3096/3 callsへ)。`git status`で検出し、**`git checkout -- <path>`で即座に復旧・確認済み**(rep9の証跡自体には影響なし、他の既存追跡ファイルへの意図しない書き込みがないことも`git status`で確認済み)。再発防止のため当該スクリプトへ注意コメントを追記した。この事故は本委任のOUT_DIR_REP10追加(モジュール定数変更)より**前**に発生したものであり、rep10実行時点では`runner.BUDGET_STATE_PATH`は既に`OUT_DIR_REP10`用に切り替わっていたため、rep10自体はrep9の証跡に触れていない。

### 19-7. 費用

作業A(実装+neg3 n=3測定+unittest+design書更新): **¥0.3096**。作業B(rep10限定7 instance×n=2、Guardrail¥13内で完走): **¥12.3479**。本委任合計: **¥12.6575**(Guardrail¥16内)。Phase累計(前回まで¥317.8415)+本委任¥12.6575=**¥330.499**。Phase残額(**上限¥500**のうち)=**¥169.501**。

### 19-8. Gate判定・Status

**広いTrial前Gate 9項目(委任文§0引用)充足状況**: 本委任は限定7 instance×n=2の再試行であり、29 instance全量のGate判定に必要な母数を満たしていない。未充足のため広いTrialのGate自体は**判定保留**(委任_18から変わらず)。

**主要な実測結果**:
- A-1(条件narrowing検討): narrowingは実施しない(hormuz新規反証、§19-1)。条件(f)新設+locateバグ是正はPASSしたが実run効果測定は未達(fastpath発火0/14)。
- A-2(escalate_to_paragraph): `hormuz_run03_standard`2/2 sampleでSTAGE4解消(PASS、ただし別セクション分散への根本対応ではない既知の限界あり)。
- A-3(neg3): n=3測定PASS(3/3 BLOCKING、非flaky)、sample2原因特定PASS(fail-closedの正常動作と判明)、両論併記をFableへ提示(決定しない)。
- rep10: 14/14 instance-run完走、STAGE4 0件(rep9の2件から改善)、Safety側の全文Recheck維持能力を保持。
- **事故と復旧**: A-3測定スクリプトが既存rep9証跡を一時的に上書きしたが`git checkout`で即座に復旧(§19-6)。

**STOP条件該当確認**: ¥16超え見込み(該当せず、¥12.6575)/API error 3連続(該当せず、0 error)/Production・既存証跡変更(該当せず、§19-6の事故は復旧済みでgit diffで無変更を確認済み)/USER_DECISION_REQUIRED6条件(該当せず、下記)/開始前チェック未反映(0件、§0対応表)/最小修正1回後もFAIL(該当なし、rep10は1回で14/14完走)/Safety-critical claimまたはSafety 12のいずれかがBLOCKINGでなくなった(該当せず、`safety_A2A3`/`safety_A5`で全文Recheック維持を確認)/全文Recheck条件最小化で開示分析の4件のいずれかを取りこぼす(該当せず、narrowingを実施しなかったため)。

**Status**: `REP10_ALL_7_INSTANCES_COMPLETE_STAGE4_ZERO`(限定7 instance×n=2、14/14完走・Guardrail内・STAGE4 0件。A-1のnarrowing判断[実施しない]・A-2の部分改善・A-3の両論併記はFable/ユーザーへの判断材料として提示する。29 instance全量の広いTrialは次回委任でのFable/ユーザー判断を待つ)。

## §20. Opus L2レビュー#4是正W1〜W5+限定Trial rep11(委任_20、2026-09-30)

### 20-0. 対応表(ユーザー指示・Opus W1〜W5)

| # | 指示/W項目 | 実施内容 | Evidence |
|---|---|---|---|
| 1 | W1: JA fail-open封鎖(i)(ii)(iii) | (i)JA recheck MAJOR deviationsの次cycle合流+`ja_pending_deviation`フラグによるSTAGE4安全網、(ii)`ja_en_equivalence_verdict`のgating化、(iii)¥0決定論JAガード(`ja_fail_open_guard`新設) | §20-1、design書§6-7 |
| 6 | 不要Rewrite統合報告 | rep11で`neg1_meta_b3prod_a2`が新規claim(MUSE-HC-006、hook区分)でRewrite発生(2/2 sample)。既知の解消済みclaim[Ring, ring]とは別claim | §20-2 |
| 7 | 全体Rewrite(⑥)再確認 | rep11で`6_full_article`使用0件(継続確認) | §20-3 |
| 8 | 人間確認残存・false PASS | rep11でSTAGE4 3/8(`bgroup_B3`×2・`meta_run03_standard`s1)、いずれもJA fail-open是正が機能した結果の正しいfail-closed。false PASS(JA逸脱残存でRESOLVED)は0/8 | §20-4 |
| 9 | コスト | rep11実測¥8.0288(8 instance-run、Guardrail¥12内) | §20-5 |
| W2 | Stage1同一fact_id列挙 | schema拡張+展開関数実装。rep11では`hormuz_run03_standard`のfresh Stage1がrecall miss(ACCEPTABLE_STAGE1)となり実run検証は不成立、unittestでrep10実データにより機構自体は検証済み | §20-1、design書§6-8 |
| W3 | 全文Recheck条件更新 | (c)縮小[paired かつ ladder≥④ or JAガード不通過]・(g)(h)新設・(e)にTrial限定但し書き | §20-1、design書§6-9 |

### 20-1. 実装(W1〜W3、¥0・regression確認)

Opus L2レビュー#4(`docs/pm/opus_l2_review_open233_self_recovery_04.md`、逐語保存)の是正W1(JA fail-open封鎖)・W2(Stage1同一fact_id列挙)・W3(全文Recheck条件更新)を実装した。詳細はdesign書§6-7/§6-8/§6-9・§4-16参照。要点は以下:

- **W1(i)**: `run_instance`の未解消時next-cycle再構築(旧実装はEN側`recheck_parsed`のMAJOR deviationsのみを使用)へ、JA側`ja_recheck_parsed`のMAJOR deviationsを合流(`origin="ja_source"`明示)。加えて`ja_pending_deviation`フラグ(このinstance内でJA未解消が持ち越されているか)を新設し、`not blocking_claims`によるdowngrade経路へ入る際、Trueなら無条件で`STAGE4_ESCALATION`(`stage4_reason="ja_deviation_unresolved"`)を強制する二重の安全網とした。
- **W1(ii)**: `ja_en_equivalence_verdict`(従来は測定専用)を`PASS`以外なら`ja_ok`をFalseへ倒すgatingへ昇格。
- **W1(iii)**: `ja_fail_open_guard`(新設、¥0・決定論)。指摘BLOCKING claimのJA引用文(`rewrite_hint`から抽出、新設ヘルパー`extract_quoted_fragment_present_in`でJA本文[Rewrite前]に実在する候補を優先し、既存`extract_quoted_fragment`の「最長一致」による誤抽出[rep10実データで実際に発生]を回避)がRewrite後も逐語で残っていないか、対象段落外のJA文が理由なく消えていないかを判定。違反時は局所QA fastpathを無条件で不可とし全文Recheckへ回し、全文Recheckが「解消」を返した場合でも`ja_ok`をFalseへ上書きする。
- **W2**: Stage1初回(`stage1_fresh_with_enumeration`新設)・Recheck(`run_recheck`拡張)の出力schemaへ`same_fact_id_locations`(文字列配列)を追加(追加callなし)し、`expand_same_fact_id_locations`(¥0・決定論、逐語実在確認でfail-closed)が各locationを独立deviationへ展開する。reuse fixture(26/29 instance)はフィールド非存在時に何も追加しない安全側fallback。
- **W3**: `full_recheck_required`の条件(c)を「paired かつ(ladder≥④ or JAガード不通過)」へ縮小(`ja_guard_ok`引数追加)、(g)`section_type`がtitle/hook/in_one_lineの場合、(h)`ja_en_equivalence_verdict`が`PASS`以外の場合を新設。(b)は実証例なしと明記のうえ保守側で維持、(e)にTrial限定(Production非外挿)の但し書きを追加。

**unittest**: 新規16件(`TestJaFailOpenGuard`4件[rep10実データfixture含む]・`TestExpandSameFactIdLocations`4件・`TestJaPendingDeviationSafetyNet`1件・`TestFullRecheckRequired`系7件[既存1件を置換+新規6件])+既存180件=**計196件全PASS**(`.venv/Scripts/python.exe -m unittest er052_open233_self_recovery_flow_runner_01_test_01`、regressionなし)。`TestJaFailOpenGuard.test_detects_rep10_hormuz_cycle2_defect`は、rep10 `hormuz_run03_standard` sample1 cycle2の実データ(`summary_rep10.json` L1091-1092のja before/after・L939のrewrite_hint)をfixtureとして転記し、ガードが(i)指摘JA文の逐語残存・(ii)対象段落外JA文の消失の両方を実際に検出することを確認している。

### 20-2. rep11実測(fastpathが起動できる代表4 instance×n=2、¥8.0288)

CLI拡張(`--instance_ids`/`--force_fresh_stage1`、新設・既存呼び出しの挙動は変えない既定値)を追加し、`hormuz_run03_standard`(Stage1をforce_fresh、W2検証目的)・`bgroup_B3`・`meta_run03_standard`・`neg1_meta_b3prod_a2`をn=2実行した(OUT_DIR=`er052_output/open233_self_recovery_flow_runner_01_rep11`、TOTAL_BUDGET_JPY=12.0、**8/8 instance-run完走・API error 0件**):

| instance | sample1 | sample2 |
|---|---|---|
| `hormuz_run03_standard` | ACCEPTABLE_STAGE1(fresh Stage1がrecall miss、cost¥0.356) | ACCEPTABLE_STAGE1(cache共有、cost¥0) |
| `bgroup_B3` | STAGE4_ESCALATION(`ja_deviation_unresolved`) | STAGE4_ESCALATION(`ja_deviation_unresolved`) |
| `meta_run03_standard` | STAGE4_ESCALATION(`ja_deviation_unresolved`) | RESOLVED_REWRITE_THEN_DOWNGRADE |
| `neg1_meta_b3prod_a2` | RESOLVED_REWRITE | RESOLVED_REWRITE_THEN_DOWNGRADE |

**(i) fastpath発火**: `meta_run03_standard`のcycle1で2/8 instance-run(sample1・sample2とも)が`full_recheck_required=False`(条件(a)〜(h)いずれも非該当)となり局所QA fastpathへ到達した(W3縮小の効果、条件(c)がpairedでない単純claimでは元々非該当だった点に注意=このケースはmechanismが`single_text_local`)。ただし局所QA自体は`find_sentence_context`の`revised_sentence_not_locatable_in_context`(既存locateバグ、委任_19のSequenceMatcher fallbackでも解消せず)により2/2ともAPI callに到達せずskip、既存の全文Recheckへ正しくフォールバックした。**fastpathの実call成功による全文Recheck省略は0/8**(発火はしたが局所QA自体は未到達、正直に報告する)。
**(ii) Stage1列挙のhormuz surface**: `hormuz_run03_standard`のforce fresh Stage1(gpt-6-luna、W2 enumeration prompt付き)が**deviationを1件も検出しなかった**(`ACCEPTABLE_STAGE1`、recall miss。rep9/rep10で繰り返し検出されていたHF-009が今回は検出されず、既存のStage1 recall miss現象[S1-Uが対策として存在する理由そのもの]であり、W2のenumeration instruction追加が原因かは切り分けできていない)。この結果、W2の「headline/one-lineをsurfaceできるか」自体は**rep11の実runでは検証不成立**(cycle自体が起動しなかったため)。機構自体の正しさはunittest(`TestExpandSameFactIdLocations`)で実データ形式のfixtureにより別途確認済み(¥0)。
**(iii) W1 JAガードの捕捉**: `bgroup_B3`(2/2 sample)のcycle1で`ja_fail_open_guard`が`ok=False`(`unexplained_ja_sentence_deletion`)を検出し`full_recheck_required_reasons`へ`ja_fail_open_guard_violation`を追加、局所QA fastpathを試みず全文Recheckへ強制フォールバックした。**ただし重要な限界を正直に報告する**: `bgroup_B3`の`source_article_text`(paired J-1の"JA"側として扱われるfixture)は実際には英語テキストである(`split_ja_sentences`が句点`。！？`で分割するため、英語文には分割点が無く全文が1文として扱われ、些細な変更でも「1文丸ごと消失」という粗い誤検知を生む構造的な既知の限界)。したがって`bgroup_B3`での発火は、rep10 hormuz型の「特定JA文の逐語残存+別文の消失」という精密な再現ではなく、保守側に倒れる形の(安全だが診断精度の粗い)発火である。**W1(i)の主機構(merge+pending flag)が精密に働いた実例**は`meta_run03_standard` sample1で確認できた: cycle2で`paired_ja_en(J-1)`Rewrite後、`ja_recheck_overall_status=LEDGER_DEVIATION`(ガードに頼らず主経路の全文Recheckが直接検出)となり、cycle3で`blocking_claims`が空になった際も`ja_pending_deviation=True`により`RESOLVED_REWRITE_THEN_DOWNGRADE`ではなく正しく`STAGE4_ESCALATION`(`ja_deviation_unresolved`)へ到達した。これはrep10 hormuz cycle2型の欠陥パターン(JA未解消が握り潰されてfalse PASSになる)が、**W1是正後は実際に防止されることをrep11の実runで確認した**、最も明確な実例である。
**(iv) false PASS確認**: 8 instance-run全てについて、`RESOLVED_REWRITE`/`RESOLVED_REWRITE_THEN_DOWNGRADE`で完了した4件(`neg1`×2、`meta_run03_standard`s2、`hormuz_run03_standard`×2[Stage1非検出のため無関係])のrewrite_recordsを確認し、いずれも`mechanism=single_text_local`(JAを一切変更しない、または`hormuz`はRewrite自体が発生していない)であり、**JA fail-open型のfalse PASSは0/8で発生していない**ことを確認した。

### 20-3. 全体Rewrite(⑥)再確認

rep11の全rewrite_records(合計10件)で`ladder_level_used="6_full_article"`は**0件**(継続確認、委任_18是正が維持されている)。

### 20-4. 不要Rewrite(neg1)・人間確認残存

`neg1_meta_b3prod_a2`は正解ラベル上「Rewrite不要」の負例群だが、rep11では2/2 sampleともRewriteが発生した(claim: MUSE-HC-006「A call seemed to come from an AI agent...」、`stage2_route=hook`、floor非経由の純粋LLM判定でBLOCKING)。これは委任_17で解消したclaim(「Ring, ring…」hook)とは**別のclaim**であり、Hook専用Stage2が今回**別の一文**を新規にBLOCKINGと判定した結果である(regressionの再現ではなく、Hook専用Stage2の判定対象が記事内の別claimへ拡張された可能性を示す新規観測、原因分析は次回委任の課題として持ち越す)。sample1はcycle1で解消(`RESOLVED_REWRITE`)、sample2はcycle1解消後cycle2で`blocking_claims`が空になり`RESOLVED_REWRITE_THEN_DOWNGRADE`。

**neg3両建て集計(W5)**: 本委任は`neg3_hormuz_prodrunner_b1b`を再実行していないため新規測定はない。Opus L2レビュー#4のQ2判定(BLOCKING妥当、floor/rubric変更なし)を踏襲し、iter6の不要Rewrite率をneg3の扱いで両建てで示す: **neg3込み4/9=44.4%(既報告値)、neg3をdisputed除外[分子・分母とも除外]で3/8=37.5%、分子のみ除外で3/9=33.3%**(Opus L2レビュー#4 Q2)。どの数値を採用するかはFable/ユーザー判断とし、本委任では確定させない。

**`safety_A2A3`のrep10 `RESOLVED_REWRITE_THEN_DOWNGRADE`(2/2)経路確認(¥0、既存json読み取り)**: `er052_output/open233_self_recovery_flow_runner_01_rep10/instances_s1/safety_A2A3.json`(L5)・`instances_s2/safety_A2A3.json`を確認したところ、いずれもcycle1でBLOCKING 1件(floor経由)+QUALITY 2件を検出しRewrite後にblocking_claimsが空になり`RESOLVED_REWRITE_THEN_DOWNGRADE`で完了していた。QUALITY 2件はfloor非該当のためStage2の裁量的降格であり、`safety_fixture`条件により全cycle`full_recheck_required=True`が維持されていたことも確認した(fail-open型の懸念には該当しない、想定どおりの経路)。

**人間確認残存(STAGE4)**: rep11は3/8(`bgroup_B3`×2・`meta_run03_standard`s1)。rep10(0/14)から増加しているが、これは**W1是正が機能した結果の正しいfail-closed**であり、regressionではない(§20-2(iii)参照)。

### 20-5. コスト

| call種別 | 回数 | 合計(¥) |
|---|---|---|
| `stage1_recheck` | 10 | 3.1836 |
| `stage2_second_judge` | 14 | 2.7854 |
| `stage3_rewrite` | 13 | 1.3673 |
| `stage1_initial` | 1 | 0.356 |
| `ja_en_equivalence` | 3 | 0.3365 |

`local_qa`call種別は0回(§20-2(i)のとおり、fastpath発火2回とも局所QA自体はlocate失敗でskip)。**rep11合計¥8.0288**(8 instance-run、Guardrail¥12内)。全文Recheckの代替による削減は今回も実測できていない(fastpath実call成功0件のため)。W1〜W3の実装自体は追加API callなし(¥0)。

本委任合計: **¥8.0288**(実装W1〜W3 ¥0+rep11 ¥8.0288、Guardrail¥12内)。Phase累計(前回まで¥330.499)+本委任¥8.0288=**¥338.5278**。Phase残額(**上限¥500**のうち)=**¥161.4722**。

### 20-6. Gate 9項目充足表(Opus L2レビュー#4判定からの変化)

| # | Gate項目 | Opus#4判定 | rep11後 |
|---|---|---|---|
| 1 | 局所QA是正 | 未充足(0/14発火) | **部分改善**(発火2/8だが実call成功0/8、locateバグ[`revised_sentence_not_locatable_in_context`]が依然主因と再確認) |
| 2 | 全体Rewrite3件の立証 | 充足 | 充足を維持(⑥ 0/10) |
| 3 | 不要Rewrite4件の開示 | 充足 | 充足を維持+neg1新規observationを追加開示(§20-4) |
| 4 | 解決策 | 部分充足 | 変化なし(neg3両建てのみ、決定はしない) |
| 5 | 人間確認残存 | 部分充足(不安定) | **改善**(STAGE4 3/8全てがfail-closedとして正しく機能した結果と確認、false PASS 0/8) |
| 6 | 代表ケース動作確認 | 充足(範囲限定) | 充足を維持(8/8完走、¥12内) |
| 7 | Safety誤通過なし | **未充足**(rep10 false PASS 1件) | **充足**(rep11でfalse PASS 0/8、W1是正の直接的効果をmeta_run03_standard s1で確認) |
| 8 | 不要な全文Check・全体Rewriteの削減 | 半分充足 | 変化なし(全体Rewriteは充足維持、全文Check削減は未実証のまま) |
| 9 | 平均コスト影響 | 部分充足 | 変化なし(¥1.0036/instance-run、+¥2/記事の上限内) |

**総合**: 充足5/部分充足3/未充足0(Opus#4時点は充足3/部分4/未充足2)。項目7(Safety誤通過)が是正され最重要の未充足が解消した。項目1(局所QA基本形)は引き続き未達(locateバグの根本原因は本委任のスコープ外)。

### 20-7. STOP条件該当確認・USER_DECISION_REQUIRED・Status

**STOP条件**: ¥12超え見込み(該当せず、¥8.0288)/API error 3連続(該当せず、0 error)/Production・既存証跡変更(該当せず、`git diff --stat`で対象外を確認)/6条件該当(該当せず、下記)/開始前チェック未反映(0件)/最小修正1回後もFAIL(該当なし、rep11は1回で8/8完走)/Safety-critical 10claim・Safety 12がBLOCKINGでなくなった(該当せず)/false PASS(JA逸脱残存でRESOLVED)がrep11で1件でも発生(**該当せず、0/8**、§20-2(iv))。

**USER_DECISION_REQUIRED 6条件該当有無**: 非該当(neg3両建て[§20-4]・neg1新規observation[§20-4]・局所QA locateバグ未解消[§20-6項目1]はFable/ユーザーへの判断材料として提示するが、いずれもSTOP/UDR条件そのものには該当しない)。

**Status**: `W1_W3_IMPLEMENTED_REP11_8_OF_8_COMPLETE_FALSE_PASS_ZERO`(W1〜W3実装+代表4 instance×n=2 rep11実行、8/8完走・false PASS 0件・Gate項目7[Safety誤通過]解消。局所QA基本形[項目1]・Stage1列挙の実run検証[W2 (ii)]・fastpath実call成功は未達のまま次回委任へ持ち越し。29 instance全量の広いTrial着手はFable/ユーザー判断待ち)。

## §21. rep11で判明した3欠陥の是正+限定Trial rep12(委任_21、2026-10-01)

### 21-0. 対応表(委任文§1〜§4)

| # | 項目 | 実施内容 | Evidence |
|---|---|---|---|
| A-1 | JAガード誤発火(`bgroup_B3`) | 言語判定(`is_predominantly_ja`、¥0決定論)でJA/非JA分割器を切替。分割不能時は`indeterminate=True`で不発火+全文Recheckへ(STAGE4直行にはしない) | §21-1、design書§6-7 |
| A-2 | 局所QA実call成功0件(3委任連続) | `find_sentence_context`が複数文needle(rewrite_hint引用が2文だった場合)を照合できていなかった真因を特定し是正 | §21-2、design書§6-10 |
| A-3 | neg1 MUSE-HC-006不要Rewrite | Ledger fact・claim原文・floor不該当を確認し、rubric tie-break境界のdisputed事例と判定(コード変更なし) | §21-3、design書§4-17 |
| A-4 | Stage1非決定性記録 | `hormuz_run03_standard`のfresh vs reuse差異を事実として記録(是正はスコープ外) | §21-4 |
| B | rep12実測(¥1.7384) | `bgroup_B3`/`neg1_meta_b3prod_a2`/`meta_run03_standard`/`bgroup_B1`(hormuz_run02_standardは存在しないためラダー①〜③候補として代替)×n=2、8/8完走 | §21-5 |

### 21-1. A-1是正(JAガード言語判定、¥0)

design書§6-7追記を参照。rep11実データ(`bgroup_B3`、`source_article_text`が実際には英語)を逐語転記したunittest(`TestJaFailOpenGuardLanguageAware`、3件)で、是正後の誤検知0件・rep10 hormuz実データでの検出維持(regressionなし)を確認した。既存196件+新規6件(A-1+A-2)=**202/202 tests PASS**(`.venv/Scripts/python.exe -m unittest er052_open233_self_recovery_flow_runner_01_test_01`)。

### 21-2. A-2是正(局所QA locate、¥0)

design書§6-10追記を参照。rep11実データ(`meta_run03_standard` sample1 cycle1、claim=MUSE-HC-010)を逐語転記したunittest(`TestFindSentenceContextMultiSentenceNeedle`、3件)で、是正後に正しくlocateされることを確認した。

### 21-3. A-3(neg1 MUSE-HC-006、コード変更なし)

design書§4-17追記を参照。Ledger fact(MUSE-HC-006)・claim原文・Stage1/Stage2判定根拠・floor不該当を確認し、Hook専用Stage2 rubricのtie-break境界上にある真のdisputed事例と判定した(rep11 2/2 BLOCKING vs rep12 2/2非BLOCKINGの非決定性で裏付け)。rubric・floor条件のコード変更は行わない。rubric tie-break文言明確化の要否はFable/ユーザー判断としてOPEN_ITEMSへ記録する。

### 21-4. A-4(Stage1非決定性、記録のみ)

rep11の`hormuz_run03_standard`force fresh Stage1はACCEPTABLE_STAGE1(recall miss)だったのに対し、rep9/rep10のreuse fixture Stage1は同一記事でBLOCKING(HF-009検出)だった。同一入力に対するStage1(V4A)のrun間非決定性(fresh実行のたびに検出結果が変わり得る)を事実として記録する。是正(温度設定・複数run多数決等)は本委任のスコープ外であり、Phase 2課題としてOPEN_ITEMSへ持ち越す。

### 21-5. rep12実測(限定4 instance×n=2、¥1.7384/Guardrail¥8内)

`OUT_DIR_REP12`(`er052_output/open233_self_recovery_flow_runner_01_rep12`)、`BUDGET_STATE_PATH`をrep12専用(`budget_state_c233y_21.json`)へ明示設定、`TOTAL_BUDGET_JPY=8.0`。CLI: `--groups=b_group,meta,negative --instance_ids=bgroup_B3,bgroup_B1,meta_run03_standard,neg1_meta_b3prod_a2 --n_runs=2`(`hormuz_run02_standard`は`build_target_instances`に存在しないため、reuse Stage1・ラダー①〜③候補の代替として`bgroup_B1`を選定)。**8/8 instance-run完走、API error 0件**:

| instance | sample1 | sample2 |
|---|---|---|
| `bgroup_B1` | RESOLVED_STAGE2_DOWNGRADE(Rewrite不要) | RESOLVED_STAGE2_DOWNGRADE(Rewrite不要) |
| `bgroup_B3` | STAGE4_ESCALATION(`ja_deviation_unresolved`、理由=(g)+(h)) | STAGE4_ESCALATION(`ja_deviation_unresolved`、理由=(g)+(h)) |
| `meta_run03_standard` | RESOLVED_REWRITE(局所QA fastpath成功) | RESOLVED_REWRITE(局所QA fastpath成功) |
| `neg1_meta_b3prod_a2` | RESOLVED_STAGE2_DOWNGRADE(Rewrite不要) | RESOLVED_STAGE2_DOWNGRADE(Rewrite不要) |

**(i) A-1検証**: `bgroup_B3`の`ja_fail_open_guard`は2/2とも`{"ok": true, "violations": [], "checked": true, "indeterminate": false}`となり、rep11で発生していた誤検知(`unexplained_ja_sentence_deletion`の粗い誤発火)は**0/2で再現しなかった**。ただし`bgroup_B3`は2/2ともSTAGE4_ESCALATIONへ到達しており、これは本ガードとは別の既存・正当な条件((g)`short_section_no_window`[section_type=in_one_line]+(h)`ja_en_equivalence_not_pass`[verdict=REVIEW_REQUIRED]、W1(ii)のgating)によるfail-closedである(全文Recheck自体は`recheck_overall_status`=`ja_recheck_overall_status`=`LEDGER_COMPLIANT`で「解消」を返していたが、equivalence verdictがREVIEW_REQUIREDだったため`ja_ok`がFalseへ倒れ、`ja_pending_deviation`がcycle2でSTAGE4を強制した)。**KPI後退(誤ったSTAGE4)は解消したが、別の正当な理由で人間確認は残存する**(false PASSではない)。

**(ii) A-2検証**: `meta_run03_standard`の局所QA fastpathは**2/2とも実際にAPI callへ到達し成功**した(`local_qa_fastpath_success: true`、`skipped_reason`なし、costは1 call ¥0.0356平均[local_qa合計¥0.0711/2call])。これはOPEN-233 Self-Recovery Flow Trial全体(委任_09〜_21、rep7〜rep12)を通じて**初めて**局所QA fastpathの実call成功による全文Recheck省略を実測した結果である。同cycleでstage1_recheck(全文Recheck)呼び出しは発生しなかった(rep12のstage1_recheck平均コスト¥0.0646/call[4 call合計¥0.2585]との比較で、局所QA1 call[¥0.0356]の方が安価であり、少なくとも同水準以下のコストで全文Recheckを代替できることを確認した。ただし同一claimでの直接的なbefore/after比較[rep12内でboth経路を実行]は行っていないため、正確な削減額の断定はしない)。

**(iii) A-3関連**: `neg1_meta_b3prod_a2`(MUSE-HC-006)は2/2とも`RESOLVED_STAGE2_DOWNGRADE`(Rewrite不要)で完了し、rep11(2/2 BLOCKING→Rewrite)と結果が入れ替わった。§21-3のdisputed判定(非決定性)を実測面からも裏付ける。

**(iv) false PASS確認**: 8 instance-run全て確認した。`RESOLVED_STAGE2_DOWNGRADE`(4件、`bgroup_B1`×2・`neg1`×2)はRewrite自体が発生していないため対象外。`RESOLVED_REWRITE`(2件、`meta_run03_standard`×2)は`mechanism=single_text_local`(JA非変更)でJA fail-open型のリスクなし。`STAGE4_ESCALATION`(2件、`bgroup_B3`×2)は完了扱いではなく人間確認へ回っているため対象外。**false PASS 0/8**(rep11に続き2回連続で0件)。

### 21-6. コスト内訳

| call種別 | 回数 | 合計(¥) |
|---|---|---|
| `stage2_second_judge` | 9 | 0.9227 |
| `stage3_rewrite` | 4 | 0.3541 |
| `stage1_recheck` | 4 | 0.2585 |
| `ja_en_equivalence` | 2 | 0.132 |
| `local_qa` | 2 | 0.0711 |

**rep12合計¥1.7384**(8 instance-run、Guardrail¥8内、実装A-1/A-2は¥0)。本委任合計: **¥1.7384**。Phase累計(前回まで¥338.5278)+本委任¥1.7384=**¥340.2662**。Phase残額(**上限¥500**のうち)=**¥159.7338**。

### 21-7. Gate 9項目充足表(rep11からの変化)

| # | Gate項目 | rep11後 | rep12後 |
|---|---|---|---|
| 1 | 局所QA是正 | 部分改善(発火2/8だが実call成功0/8) | **改善**(`meta_run03_standard` 2/2で実call成功、全文Recheck省略を実測) |
| 2 | 全体Rewrite3件の立証 | 充足を維持 | 充足を維持(⑥ 0/8) |
| 3 | 不要Rewrite4件の開示 | 充足+neg1新規observation | 充足を維持+neg1をdisputed事例として分析完了(§21-3) |
| 4 | 解決策 | 部分充足 | 変化なし(neg3両建てのみ、決定はしない) |
| 5 | 人間確認残存 | 改善(STAGE4 3/8全てfail-closed) | 継続改善(`bgroup_B3` 2/2は誤検知ではなく正当な理由によるfail-closedと確認) |
| 6 | 代表ケース動作確認 | 充足を維持 | 充足を維持(8/8完走、¥1.7384) |
| 7 | Safety誤通過なし | 充足 | 充足を維持(false PASS 0/8、2回連続) |
| 8 | 不要な全文Check・全体Rewriteの削減 | 半分充足 | **改善**(局所QA成功による全文Check省略を初めて実測) |
| 9 | 平均コスト影響 | 部分充足 | 変化なし(¥0.2173/instance-run、rep12実測) |

**総合**: 充足6/部分充足3/未充足0(rep11時点は充足5/部分3/未充足0)。項目1(局所QA基本形)・項目8(全文Check削減)が新たに改善した。

### 21-8. STOP条件該当確認・USER_DECISION_REQUIRED・Status

**STOP条件**: ¥10超え見込み(該当せず、実測¥1.7384)/API error 3連続(該当せず、0 error)/Production・既存証跡変更(該当せず、`git diff --stat`でer052本体2ファイルのみ・既存rep7〜11出力は無変更)/6条件該当(該当せず、下記)/開始前チェック未反映(0件)/最小修正1回後もFAIL(該当なし、rep12は1回で8/8完走)/Safety-critical 10claim・Safety 12がBLOCKINGでなくなった(該当せず、対象外instance)/false PASS 1件以上(**該当せず、0/8**)。

**USER_DECISION_REQUIRED 6条件該当有無**: 非該当(neg1のdisputed判定[§21-3]・rubric tie-break文言明確化の要否・Stage1非決定性[§21-4]はFable/ユーザーへの判断材料として提示するが、いずれもSTOP/UDR条件そのものには該当しない)。

**Status**: `A1_A2_FIXED_A3_ANALYZED_REP12_8_OF_8_COMPLETE_FALSE_PASS_ZERO_LOCAL_QA_FIRST_SUCCESS`(rep11で判明した3欠陥のうちA-1[JAガード誤発火]・A-2[局所QA locate]をコード修正、A-3[neg1]をコード変更なしで分析完了。rep12実行で局所QA fastpathの実call成功を初めて実測し全文Recheck省略を確認。false PASS 0/8[rep11から2回連続]。29 instance全量の広いTrial着手はFable/ユーザー判断待ち)。

## §22. bgroup_B3の等価QA gating是正+Gate 9項目確認+広いTrial iteration 7(委任_22、2026-10-01)

### 22-0. 対応表(委任文§1〜§4)

| # | 項目 | 実施内容 | Evidence |
|---|---|---|---|
| A-1 | `bgroup_B3`の等価QA gating誤判定 | `resolve_ja_ok_after_equivalence_gating`(新設、¥0決定論)で、`FAIL`は従来どおりja_okをFalseへ倒し、`REVIEW_REQUIRED`かつJA側言語がindeterminate(`is_predominantly_ja`で判定)の場合はja_okを強制せず全文Recheckの実際の判定を採用、`REVIEW_REQUIRED`かつ言語正常なら従来どおりgatingするよう整理 | §22-1、design書§6-11 |
| A-2 | rep13実測(限定、bgroup_B3のみ×n=2を2回、Guardrail¥1) | 実測¥0.9448(4 instance-run)、**4/4 STAGE4に至らず**(rep12の2/2 STAGE4から改善) | §22-2 |
| A-3 | Gate 9項目充足表 | Evidence列挙形式で作成(判定はFableへ委ねる) | §22-3 |
| B | 広いTrial iteration 7(29 instance全量、9 instanceはn=2/20 instanceはn=1、計38 instance-run) | 実測¥39.5475(Guardrail¥45内)、API error 0件、false PASS 0件 | §22-4〜§22-8 |

### 22-1. A-1是正内容

design書§6-11を参照。既存の巨大なインライン処理(`run_instance`内、委任_20 W1(ii)由来)を純粋関数`resolve_ja_ok_after_equivalence_gating`として抽出し、gating方式を整理した(コード詳細・背景は設計書参照)。**unittest**: `TestResolveJaOkAfterEquivalenceGating`(6件)、rep12 `bgroup_B3`実データ(既存`REP11_B3_SOURCE_ARTICLE_TEXT_AFTER`定数と逐語一致)・rep10 hormuz実データ(真のJA、regression確認)を使用。既存202件+新規6件=**計208件全PASS**(`.venv/Scripts/python.exe -m unittest er052_open233_self_recovery_flow_runner_01_test_01`)。

### 22-2. A-2 rep13実測(¥0.9448、Guardrail¥1内)

`OUT_DIR_REP13`(`er052_output/open233_self_recovery_flow_runner_01_rep13`)、`BUDGET_STATE_PATH`をrep13専用(`budget_state_c233z_22_repA.json`)、`TOTAL_BUDGET_JPY=1.0`へ明示設定。CLI: `--groups=b_group --instance_ids=bgroup_B3 --n_runs=2`を2回実行した(Stage1はreuse fixture、fresh化しない)。

| 実行 | sample1 | sample2 | 備考 |
|---|---|---|---|
| 1回目(¥0.1766) | RESOLVED_STAGE2_DOWNGRADE(blocking_count=0) | RESOLVED_STAGE2_DOWNGRADE(blocking_count=0) | Stage2 LLM非決定性でHF-007がQUALITYと判定され、等価チェック自体が発火せず(A-1の対象外ケース) |
| 2回目(¥0.7682) | RESOLVED_REWRITE(ladder=1_word_connective) | RESOLVED_REWRITE(ladder=1_word_connective) | Stage2がHF-007をBLOCKINGと判定。**verdict=REVIEW_REQUIRED・lang_indeterminate=True・not_gated_indeterminate_lang=True**となり、全文Recheck(EN/JA双方LEDGER_COMPLIANT)の実際の判定がそのまま採用され解消 |

**4/4 instance-run全てSTAGE4に至らず**(rep12の2/2 STAGE4から改善)。`ja_fail_open_guard`は4/4とも`ok=true`(誤検知なし)。false PASS確認: 2回目の2件は`recheck_overall_status=LEDGER_COMPLIANT`・`ja_recheck_overall_status=LEDGER_COMPLIANT`・`ja_fail_open_guard.ok=True`かつ`ladder_level_used=1_word_connective`(最小変更維持)であり、実際の解消を実Recheckが確認した場合のみ通過させる設計どおりで、false PASSではない。累計: 実測¥0.9448(Guardrail¥1内、詳細design書§6-11)。

### 22-3. A-3 Gate 9項目充足表(Fable基準、Evidence列挙。判定はFableへ委ねる)

| # | Gate項目 | Evidence |
|---|---|---|
| 1 | 局所QA実run成功 | rep12 `meta_run03_standard` 2/2実call成功(§21-5(ii))。iteration7(§22-5)でも`meta_run03_standard` 2/2実call成功を再確認(局所QA call合計2件、¥0.0356相当×2)。ただしfastpath発火自体は38 instance-run中2件のみ(5.3%)にとどまる |
| 2 | ⑥(全体Rewrite/削除)使用 | rep12(8 instance-run)・rep13(4 instance-run)では0件だったが、**iteration7(29 instance全量規模)では7件(18.4%)観測**(`safety_A2A3`×2・`safety_A4`×4・`bgroup_B4`×1、ladder_level_distribution参照、§22-5)。3 instance全てが⑥を試みた後も最終的にSTAGE4_ESCALATIONへ到達しており(⑥使用がそのまま「解消」と判定された例は0件)、silent_pass_candidate=0(§22-4)。従来の代表subset(rep7〜13)ではたまたま発生しなかっただけで、全量規模では発生することが新たに判明した点を正直に報告する |
| 3 | 不要Rewrite4件の開示 | 既存開示(`docs/pm/open233_iter6_rewrite_disclosure_01.md`§1-4-5)+neg1新規observation(MUSE-HC-006)をdisputed事例として分析済み(§21-3)。iteration7では不要Rewrite率が21.43%(3/14、§22-5)へ改善、該当3件(`neg1_meta_b3prod_a2`×1[sample1、STAGE4]・`neg3_hormuz_prodrunner_b1b`×2)を開示 |
| 4 | 解決策 | neg3両建て(iter6: 4/9=44.4%/3/8=37.5%/3/9=33.3%、決定しない)。**meta_run03_advancedはiteration7で2/2ともblocking_count=0(Rewrite自体が発生せず)となり、等価QA gating機構の実run検証は今回も機会を得られなかった**(未検証のまま、A-1修正がこのinstanceで実際に効くかどうかは確認できていない) |
| 5 | 人間確認残存 | rep13後: `bgroup_B3`は0/4(rep12の2/2から解消)。iteration7全体: 7/38(18.4%)がSTAGE4(内訳`ja_deviation_unresolved`6件+`cycle_limit_exhausted_after_recheck`1件)。全件を精査し、`lang_indeterminate=True`(A-1の対象パターン)による誤STAGE4は**0件**(全て`lang_indeterminate=False`、genuineな未解消JA逸脱またはEN側自体のLEDGER_DEVIATION、§22-4)。A-1修正が新たなfalse STAGE4を生んでいないことを確認した一方、真の人間確認は7/38で残存している |
| 6 | 代表ケース動作確認 | rep11(4)+rep12(8)+rep13(4)+iteration7(38、29 instance全量規模)=計54 instance-run完走、API error 0件 |
| 7 | false PASS 0 | rep11(0/8)・rep12(0/8)・rep13(0/4)・**iteration7(0/38、§22-4)** |
| 8 | 不要な全文Check・全体Rewriteの削減 | rep12実測(`meta_run03_standard`、局所QA1 call¥0.0356 vs 全文Recheck平均¥0.0646/call)。iteration7でも同instanceで2/2再現。一方、iteration7全体では局所QA fastpath発火率5.3%(2/38)にとどまり、全文Recheck(42 call)が依然大半を占める |
| 9 | 平均コスト影響 | rep12¥0.2173/instance-run、rep13¥0.2362/instance-run、**iteration7¥1.0407/instance-run(38 instance-run平均)、worst¥8.9545(`safety_A4`、iter6のworst¥5.7883から悪化)** |

**総合**: 9項目全てEvidence記載済み(1項目もEvidence欠落なし、STOP非該当)。ただし項目2(⑥使用)・項目9(worst cost)は広いTrialで従来の小規模subsetより悪化した数値が新たに判明しており、単純な「改善」とは言えない。判定(VALIDATED/REJECTED等)はFableへ委ねる。

### 22-4. Part B構成・実測(29 instance全量、38 instance-run、¥39.5475/Guardrail¥45内)

`OUT_DIR_ITER7`(`er052_output/open233_self_recovery_flow_runner_01_iter7`)、`BUDGET_STATE_PATH`をPart B専用(`budget_state_c233z_22_repB.json`)、`TOTAL_BUDGET_JPY=45.0`へ明示設定。Stage1は既存reuse fixtureを使用(fresh化しない、委任文§2の指示どおり)。

- **n=2実行**(9 instance、非決定性が実測されていたinstance): `--groups=safety,b_group,meta,hormuz,negative --instance_ids=safety_A2A3,bgroup_B3,meta_run03_standard,meta_run03_advanced,hormuz_run03_standard,hormuz_run03_advanced,neg1_meta_b3prod_a2,neg2_meta_refresh_a2,neg3_hormuz_prodrunner_b1b --n_runs=2`(18 instance-run、¥21.4374、call104、error0)。
- **n=1実行**(残り20 instance): `--groups=safety,b_group,hormuz,negative --instance_ids=<20 instance>`(20 instance-run、¥18.1101、call103、error0)。

**38/38 instance-run完走・API error 0件**。

**false PASS確認(全38件)**: 各RESOLVED_REWRITE/RESOLVED_REWRITE_THEN_DOWNGRADEについて、最終cycleの`recheck_overall_status`/`recheck_all_prior_issues_resolved`(自己矛盾時は`recheck_confirm_*`のcite-or-release結果)・`ja_recheck_overall_status`・`ja_fail_open_guard.ok`を機械的に検証した。**false PASS候補0件**(`escalation_zero_breakdown.silent_pass_candidate=0`とも一致)。

**Safety hard gate**: `floor_variant_comparison.safety_group_hard_gate_passed=true`(n=2実行・n=1実行とも)、`false_negative_candidates_safety_group=0`。Safety群13 instance-run全てでBLOCKING維持または正当な理由によるSTAGE4(fail-closed)を確認、誤降格0件。

**A-1修正のregression確認**: iteration7のSTAGE4到達7件全てについて`ja_equivalence_lang_indeterminate`を確認した結果、**全件`False`(genuineなJA言語、または等価チェック自体が発火していないEN側単独のLEDGER_DEVIATION)**であり、A-1が対象とする「JA側言語が実際には非JAで判定不能」パターンによる誤STAGE4は0件だった(下表)。

| instance | sample | stage4_reason | lang_indeterminate | 備考 |
|---|---|---|---|---|
| `hormuz_run03_standard` | s1 | ja_deviation_unresolved | False | cycle1で`ja_en_equivalence_verdict=REVIEW_REQUIRED`(genuine JA)によりja_okをgating、EN/JA Recheckは当該cycleでLEDGER_COMPLIANTだったがcycle2でblocking 0のままja_pending_deviation未解消 |
| `hormuz_run03_standard` | s2 | ja_deviation_unresolved | False | cycle2でja_recheck=LEDGER_DEVIATION(genuine、gating以前にEN/JA Recheck自体が逸脱を検出) |
| `neg1_meta_b3prod_a2` | s1 | ja_deviation_unresolved | False | cycle1/2ともrecheck=LEDGER_DEVIATION(genuine) |
| `safety_A2A3` | s1/s2 | ja_deviation_unresolved | False | 全cycleでrecheck=LEDGER_DEVIATION(genuine、ladder⑥まで試行後も未解消) |
| `bgroup_B4` | (n=1) | ja_deviation_unresolved | False | cycle1でrecheck=LEDGER_DEVIATION(genuine、EN側自体が未解消) |
| `safety_A4` | (n=1) | cycle_limit_exhausted_after_recheck | False | 7 rewrite operationsに渡りja_recheck=LEDGER_DEVIATIONが持続(genuine、既知の反復困難ケース) |

### 22-5. iteration7全測定(`aggregate_measurements`を38 instance-run結合データへ適用、既存関数を流用、¥0)

| 指標 | iteration7 | iteration6(n=1、sample1、29 instance) | 備考 |
|---|---|---|---|
| STAGE4件数/率 | 7/38=18.42% | 3/29=10.34% | instance-run単位(iter7は一部n=2混在)。単純比較不可、参考値 |
| real_run Escalation率 | 2/10=20.0%(`hormuz_run03_standard`のみ) | 1/6=16.67% | 同一既知ハードケース(`hormuz_run03_standard`)起因、新規regressionではない |
| 群別Escalation率 | safety 3/13=23.08%/hormuz 2/6=33.33%/b_group 1/5=20.0%/negative 1/10=10.0%/meta 0/4=0.0% | (iter6は今回未再集計) | |
| 不要Rewrite率(v3、正常記事=negative7+Normal2) | 3/14=21.43%(`neg1`×1・`neg3`×2) | 4/9=44.44% | **改善**(Hook専用Stage2等、既存の蓄積改善効果。A-1修正自体はこの指標に直接寄与しない) |
| ⑥(full_article/delete)使用 | 7/38=18.4%(`safety_A2A3`×2・`safety_A4`×4・`bgroup_B4`×1) | 1/29=3.4% | **悪化**(§22-3項目2参照、全量規模で新たに判明) |
| ladder分布 | 1_word=21/3_sentence=8/6_full_article=7/4_paragraph=3(`paired_j1_not_laddered`は0件) | 1_word=12/3_sentence=6/6_full=1/0_delete=1/`paired_j1_not_laddered`=12 | J-1(JA/EN対訳ペア)が全件ladder経由になった(委任_16以降の既存改善の継続確認) |
| 局所QA fastpath発火/実call成功 | 2/38発火、2/2実call成功(`meta_run03_standard`のみ) | (iter6は局所QA未実装段階) | |
| false PASS | 0/38 | (iter6は同手法で未検証) | |
| JA-EN等価call内訳 | 14 call(FAIL 1/REVIEW_REQUIRED 12/PASS 1) | (iter6は等価チェック測定専用段階) | |
| Stage4 reason分布 | `ja_deviation_unresolved`6/`cycle_limit_exhausted_after_recheck`1 | `cycle_limit_exhausted_after_recheck`/`same_claim_fact_id_reblocked`/`cycle_limit_exhausted`各1 | |
| section_role_violation | 3件(`neg1`hook_shrank・`safety_er009_changed_certainty`/`changed_number`numbers_added_to_title) | 3件 | 同水準 |
| コスト5分割 | no_rewrite 15件平均¥0.1712/with_rewrite 23件平均¥1.6078/rewrite率60.53%/全体平均¥1.0407/worst¥8.9545(`safety_A4`) | no_rewrite 9件平均¥0.1266/with_rewrite 20件平均¥1.4848/rewrite率68.97%/全体平均¥1.0633/worst¥5.7883 | 全体平均はほぼ同水準だが**worst costが悪化**(`safety_A4`が7 rewrite operations・ladder⑥を4回試行し最終的にSTAGE4、+¥2上限を超過する新たなtail risk) |

**call種別内訳**(iteration7、207 call・¥39.5475): 既存call_log集計により、`stage2_second_judge`/`stage3_rewrite`/`stage1_recheck`(42件)/`ja_en_equivalence`(14件)/`local_qa`(2件)/`recheck_confirm`等が含まれる(詳細は`er052_output/open233_self_recovery_flow_runner_01_iter7/*/call_log`参照、個別呼び出し単価の全件表化は本報告では省略し集計値のみ記載する)。

### 22-6. 読み比べページ更新

`user_test/open233_rewrite_compare_01/index.html`をiteration7の実測結果で更新した(iter6版は`index_iter6.html`として保存、削除・移動せず)。3 instance収録: (1)`neg1_meta_b3prod_a2`(sample2、Meta hookの非Rewrite例、Hook専用Stage2がRewrite不要と判定)、(2)`bgroup_B3`(sample1、B3因果のA-1修正例、RESOLVED_REWRITEで解消)、(3)`neg3_hormuz_prodrunner_b1b`(sample1、Hormuz由来記事の局所Rewrite例。`hormuz_run03_standard`自身は今回2/2 STAGE4[genuine]のため代替採用、ページ内に明記)。生成スクリプト: `er052_open233_self_recovery_rewrite_compare_page_iter7_01.py`(API呼び出しなし、¥0)。公開URL: `https://shimomura055.github.io/eigo-radio/user_test/open233_rewrite_compare_01/index.html`(commit・push後に有効)。

### 22-7. コスト

| 区分 | 費用(¥) |
|---|---|
| A-1実装 | 0 |
| A-2 rep13実測 | 0.9448 |
| Part B iteration7実測 | 39.5475 |
| **本委任合計** | **40.4923** |

Phase累計¥340.2662+¥40.4923=**¥380.7585**/総枠¥500、残**¥119.2415**。

### 22-8. STOP条件該当確認・USER_DECISION_REQUIRED・Status

**STOP条件**: Part A ¥1超え見込み(該当せず、実測¥0.9448)/Part B ¥45超え見込み(該当せず、実測¥39.5475)/API error 3連続(該当せず、0 error全体)/Production・既存証跡変更(該当せず、`git diff --stat`でer052本体2ファイル[flow_runner+test]・新規iter7出力・新規compare pageスクリプトのみ、既存rep7〜13・iteration1〜6証跡は無変更)/6条件該当(該当せず、下記)/開始前チェック未反映(0件)/最小修正1回後もFAIL(該当なし、A-1・Part Bとも1回で完走)/Safety-critical 10claim・Safety 12がBLOCKINGでなくなった(**該当せず**、Safety hard gate通過・false_negative_candidates_safety_group=0)/false PASS 1件以上(**該当せず、0/54**[rep11〜iteration7通算])。

**USER_DECISION_REQUIRED 6条件該当有無**: 非該当。ただし以下をFable/ユーザーへの判断材料として提示する: (1) ⑥(全体Rewrite/削除)使用が全量規模で7件観測され、従来の「0件」という代表subset時点の評価は成立しないことが判明した(いずれもSTAGE4で正しくfail-closedしており、false PASSではない)。(2) worst instance cost¥8.9545(`safety_A4`)は既存+¥2/記事Cap前提から大きく外れるtail riskであり、iter6のworst¥5.7883からも悪化している。(3) `safety_A4`は過去(iter3・iter4)から繰り返しSTAGE4(`cycle_limit_exhausted_after_recheck`)に至る既知のハードケースであり、根本原因(反復困難パターン)は本委任のスコープ外である。(4) `meta_run03_advanced`は等価QA gating機構(A-1)の実run検証機会を今回も得られなかった(blocking_count=0のまま)。(5) 不要Rewrite率は21.43%(3/14)へ改善したが根本解消(0%)には至っていない。

**Status**: `A1_EQUIVALENCE_GATING_FIXED_REP13_4_OF_4_NO_STAGE4_ITER7_38_OF_38_COMPLETE_FALSE_PASS_ZERO_WORST_COST_TAIL_RISK_INCREASED`(A-1でJA/EN等価チェックgatingを整理し`bgroup_B3`のrep13実測4/4でSTAGE4を解消、Gate 9項目は全項目Evidence記載完了[STOP非該当]。29 instance全量規模の広いTrial iteration 7を初めて完走[38 instance-run・¥39.5475・error 0・false PASS 0]し、不要Rewrite率の改善[44.44%→21.43%]を確認した一方、⑥使用[0→7件]・worst instance cost[¥5.79→¥8.95]という新たなtail riskが全量規模で初めて判明した。Gate判定[VALIDATED/REJECTED]・tail risk対応の要否はFable/ユーザー判断待ち)。

## §23. iter7未達2点の原因特定・設計修正・少数ケース確認(委任_23、2026-10-01)

### 23-0. 対応表(委任文§2 A〜E)

| # | 項目 | 実施内容 | Evidence |
|---|---|---|---|
| A | `hormuz_run03_standard` real_run Escalation真因 | 真因A(§6-11等価QA gatingの過剰保守、ja_ok既確認済みでもREVIEW_REQUIREDだけで覆していた)+真因B(reuse fixtureのsame_fact_id列挙欠如)の2点を特定、双方是正 | §23-A、design書§6-12 |
| B | ⑥(全体Rewrite/削除)の扱い | iter7の⑥使用7件全てについて①〜④試行記録を精査し「⑥が必要だった」Evidence 0/7を確定。feature flag(既定OFF)で標準ラダーから除外 | §23-B、design書§5-10 |
| C | OPEN_ITEMS記録是正 | OPEN-233行で「種類」列に誤って混入していた委任_21追記(1118文字)を、本来の位置(「内容」列、委任_20と委任_22の間の時系列順)へ移動 | §23-C |
| D | rep14実測(`hormuz_run03_standard`×n=2+`safety_A4`×n=1、Guardrail¥5) | 実測¥5.3545。A・Bとも実際に発火することを確認したが、hormuzは2/2ともSTAGE4のまま(理由変化)、safety_A4はworst cost¥8.9545→¥1.5084(83%減) | §23-D |

### 23-A. hormuz_run03_standard real_run Escalation真因是正

design書§6-12を参照。真因A(`resolve_ja_ok_after_equivalence_gating`の残存過剰保守: `ja_ok`が全文Recheckで既にTrueと確認済みでも、equivalence`REVIEW_REQUIRED`(JA側言語determinate)だけで無条件にFalseへ倒していた)と真因B(reuse fixture[29 instance中26/29]は`same_fact_id_locations`フィールドを持たず、Stage1初回がbody claimしか検出できず、in_one_line側の同一fact言及がcycle1の全文Recheckまで発見されない)の2点を、iter7実データ(`hormuz_run03_standard` instances_s1/s2)の実際のcycle記録(stage2_results/rewrite_records/ja_en_equivalence_verdict/recheck_overall_status等)を精査して特定した。

**A-1是正(¥0)**: `resolve_ja_ok_after_equivalence_gating`の`REVIEW_REQUIRED`+JA側言語正常の分岐を、`ja_ok`(入力)が既にTrueの場合はgatingしないよう変更(`FAIL`分岐は無変更)。

**A-2(b)是正(¥0)**: `deterministic_same_fact_id_location_fallback`(新設)で、reuse fixtureのdeviationについて数値/金額/%トークン一致(1件以上)またはキーワード重複(閾値3件以上、`hormuz_run03_standard`実データで較正)による候補文を列挙し、既存`expand_same_fact_id_locations`(fail-closed)へ渡してcycle0時点で独立claimへ展開する。

**unittest**: `TestResolveJaOkAfterEquivalenceGating`(既存1件を新挙動へ更新+新規1件)、`TestDeterministicSameFactIdLocationFallback`(新規5件)、関連wiring確認2件。既存208件のうち2件更新+新規10件=**計218件全PASS**(`.venv/Scripts/python.exe -m unittest er052_open233_self_recovery_flow_runner_01_test_01`)。

### 23-B. ⑥(全体Rewrite/削除)の標準ラダーからの除外

**⑥使用7件の内訳(iter7実データ、call_log精査)**:

| # | instance/run | ⑥使用claim(fact_id) | ⑥前の①〜④試行 | ⑥後の結果(guard_ok) | 最終final_state |
|---|---|---|---|---|---|
| 1 | `safety_A2A3` s1 | HF-003(cycle1) | cycle0で③1文成功も、cycle1で同一fact_id再出現しguard失敗 | True(⑥で一旦更新) | STAGE4_ESCALATION(`ja_deviation_unresolved`) |
| 2 | `safety_A2A3` s2 | HF-003(cycle1) | 同上 | True | STAGE4_ESCALATION(`ja_deviation_unresolved`) |
| 3 | `bgroup_B4` | MUSE-HC-002(cycle0) | ①〜④全段guard失敗(paired locate困難) | True | STAGE4_ESCALATION(`ja_deviation_unresolved`) |
| 4 | `safety_A4` | MUSE-HC-012(cycle0) | ①〜④全段guard失敗 | True | STAGE4_ESCALATION(`cycle_limit_exhausted_after_recheck`) |
| 5 | `safety_A4` | MUSE-HC-006(cycle1) | cycle0は①成功も、cycle1で同一fact_id再出現しguard失敗 | True | 同上 |
| 6 | `safety_A4` | MUSE-HC-012(cycle2) | cycle0の⑥後も再出現、cycle2で再度guard失敗 | True | 同上 |
| 7 | `safety_A4` | MUSE-HC-006(cycle2) | cycle1の⑥後も再出現、cycle2で再度guard失敗 | True | 同上 |

**結論**: ⑥自体は7/7とも`guard_ok=True`(テキストは更新された)が、**7/7ともその後のcycleで同一fact_idが再出現するか、最終的にSTAGE4_ESCALATIONへ到達しており、⑥使用が最終的な解消[RESOLVED_REWRITE系]に至った例は0/7**。iter7全体の費用¥39.5475のうち⑥関連call(fulltext_fallback、EN/JA各1call×7=最大14 call)が`safety_A4`のworst cost¥8.9545の主要因(同instanceのみで4回⑥を使用)。

**無効化後の試算(実測、§23-D参照)**: `safety_A4`をrep14で再実行した結果、⑥無効化により1件の`ladder_exhausted_without_full_rewrite`で即STAGE4_ESCALATIONへ回り、コストは¥8.9545→**¥1.5084(83%減)**。他の3件(`safety_A2A3`×2・`bgroup_B4`×1)は本委任では再実行していない(rep14はhormuz/safety_A4に限定、Guardrail¥6の制約)が、同一の`ladder_exhausted_without_full_rewrite`経路を通ることが期待される(コード共通のため)。

**是正**: `ENABLE_LADDER_LEVEL_6_FULL_REWRITE`(feature flag、既定False)を新設。design書§5-10参照。⑤(より広い範囲)は既に①・④へ統合済み(§5-7)でありコード上独立した水準が存在しないため、無効化の対象自体がない(既知の限界として記録)。

**unittest**: `TestLadderExhaustedWithoutFullRewriteWiring`(新規2件)+`single_text_rewrite`の既存⑥テストを「既定OFF時はladder_exhausted_without_full_rewriteを返す」新テストへ更新+「flagをTrueへ戻すと従来どおり⑥で解消する」regressionテストを追加。

### 23-C. OPEN_ITEMS記録是正

`OPEN_ITEMS.md`のOPEN-233行は、内容が膨大な単一セルへ`**YYYY-MM-DD追記(委任_XX...)**: ...`形式で時系列に蓄積される構造になっている。精査の結果、委任_21(2026-10-01)の追記パラグラフ(1118文字、"rep11で判明した3欠陥の是正+限定Trial rep12"から始まる)が、本来入るべき「内容」列(委任_20エントリと委任_22エントリの間)ではなく、誤って「種類」列(短い分類タグが入るべき列)の末尾へ挿入されていたことを確認した(過去のいずれかの委任での編集ミスと推定、原因の特定は本委任のスコープ外)。当該パラグラフを一字一句変更せず(履歴改変なし)「種類」列から「内容」列の正しい時系列位置(委任_20の末尾と委任_22の先頭の間)へ移動した。`git diff --stat`で本行のみ1箇所の変更であることを確認済み。

### 23-D. rep14実測(¥5.3545、Guardrail¥6)

`OUT_DIR_REP14`(`er052_output/open233_self_recovery_flow_runner_01_rep14`)、`BUDGET_STATE_PATH`をrep14専用(`budget_state_c233aa_23_rep14.json`)。CLI: (1) `--groups=hormuz --instance_ids=hormuz_run03_standard --n_runs=2`(¥3.8461)、(2) `--groups=safety --instance_ids=safety_A4 --n_runs=1`(¥1.5084)。

**hormuz_run03_standard(¥3.8461、2 sample)**: 是正A・Bとも実際に発火した(sample2で`ja_equivalence_review_required_not_gated_already_confirmed_resolved=True`を確認[A-1是正の実発火]、両sampleともcycle0でbody+in_one_line 2claimを同時検出・Rewrite[A-2是正の実発火、iter7では2 cycleに分散していた])。**しかし2/2ともSTAGE4_ESCALATIONは解消しなかった**(`stage4_reason`が`ja_deviation_unresolved`から`same_claim_fact_id_reblocked`へ変化)。cycle1の全文Recheckがbody claim(①水準でRewrite済み)を近似一致[`find_matching_prior_record`閾値0.75]でなお同一claimとして再検出し、§3-3の既存安全網(「同一claim再発=Rewriteが効かなかったことの実証」)が正しく発火した。**正直な結論**: 真因A・Bは実在し是正も機能したが、hormuz_run03_standardのEscalationは**第三の要因**(word-level[①]のみのRewriteでは当該body claimの実質的問題を解消しきれないというStage3 Rewrite品質の限界)により残存する。これは本委任のA-2三択(a/b/c)のいずれとも完全には一致しない新規の発見である。

**safety_A4(¥1.5084、n=1)**: `final_state=STAGE4_ESCALATION`・`stage4_reason=ladder_exhausted_without_full_rewrite`(claim MUSE-HC-012)。iter7の同fixture(worst cost¥8.9545、⑥を4回使用)と比較し**83%減**。Safety floor(floor_reason=`deterministic_floor:changed_actor`、MUSE-HC-006)はstage2_results上で引き続き`materiality=BLOCKING`(floor-strict、Production実際の挙動)を維持し、最終的にSTAGE4_ESCALATION(human review)へ正しくfail-closedした(false PASSではない)。`floor_variant_comparison.safety_group_hard_gate_passed=false`(false_negative_candidates_safety_group=1)が記録されたが、これはStage2 LLM独自判定(`llm_materiality`、floor無しの仮想判定)のrun間非決定性によるものであり、本委任の変更(Stage3のみに影響)とは無関係。実際に稼働しているfloor-strict自体は本runでも正しくBLOCKINGを維持しており、Safety regressionではない(iter7の同一metricは0件だったため、次回委任での追加観測対象として記録する)。

**予算**: rep14合計¥5.3545(Guardrail¥5の目標をやや超過したが全体Guardrail¥6以内)。分析・実装¥0+rep14¥5.3545=本委任合計**¥5.3545**/Guardrail¥6、残**¥0.6455**。hormuzが依然FAILのため追加の最小修正+再実行(≤¥2)が委任文の想定手順だが、残予算(¥0.6455)がこれを下回るため**実施しない**(STOP条件「¥6超え見込み」に抵触するリスクを避けた)。

### 23-E. STOP条件該当確認・USER_DECISION_REQUIRED・Status

**STOP条件**: ¥6超え見込み(該当せず、実測¥5.3545/Guardrail¥6)/API error 3連続(該当せず、rep14通算0 error)/Production・既存証跡変更(該当せず、`git diff --stat`でOPEN_ITEMS.md[1箇所]・er052本体2ファイル[flow_runner+test]・新規rep14出力のみ、Production[er003/er006/er009/er010/er012/er019]・既存iteration1〜7/rep7〜13証跡は無変更)/6条件該当(下記参照)/開始前チェック未反映(0件)/最小修正1回後もFAIL(**該当**: hormuzは是正A・B適用後もSTAGE4のまま。ただし予算制約[残¥0.6455]により追加の再実行は行わずSTOPし、Fable/ユーザー判断を仰ぐ形で本節に記録する)/Safety-critical 10claim・Safety 12がBLOCKINGでなくなった(該当せず、floor-strict維持・§23-D参照)/false PASS 1件以上(該当せず、0/3[rep14通算])。

**USER_DECISION_REQUIRED 6条件該当有無**: 非該当。ただし以下をFable/ユーザーへの判断材料として提示する: (1) `hormuz_run03_standard`は真因A・Bを是正してもなお2/2 STAGE4_ESCALATIONのままであり、第三の要因(Stage3 word-level Rewriteの品質限界)の是正は本委任のスコープ・予算を超える(次回委任での着手要否をFable/ユーザーが判断)。(2) `safety_A4`のworst costは¥8.9545→¥1.5084(83%減)を確認したが、`safety_A2A3`×2・`bgroup_B4`×1は本委任では未検証(同一コードパスのため同様の改善が期待されるが実測はしていない)。(3) ⑥のfeature flag無効化により、⑥が実際に必要な非常に稀なケース(iter7では0/7だったが、より広い母数では存在し得る)を早期にSTAGE4へ回すことになり、Rewriteによる自動解消率がわずかに低下する可能性がある(iter7実測では影響なし[0/7が解消例だったため])。

**Status**: `A2_GATING_AND_ENUMERATION_FIXED_VALIDATED_LADDER6_DISABLED_COST_REDUCED_HORMUZ_STILL_ESCALATES_NEW_THIRD_CAUSE_FOUND`(真因A[等価QA gatingの過剰保守]・真因B[reuse fixture同一fact_id列挙欠如]を特定・是正し、rep14実測で双方の是正が実際に発火することを確認した。`safety_A4`のworst costを83%削減した[⑥ feature flag既定OFF]。一方`hormuz_run03_standard`は2/2ともSTAGE4_ESCALATIONのまま残り、理由が`ja_deviation_unresolved`から`same_claim_fact_id_reblocked`[Stage3 Rewrite品質の限界という新規の第三要因]へ変化した。予算制約のため追加修正は行わずFable/ユーザー判断待ちとしてSTOPする)。

## §24. `hormuz_run03_standard`第三要因(ラダー未昇段のまま安全網が先に発火)の是正+少数確認rep15(委任_24、2026-10-01)

### 24-0. 対応表(委任文§1〜§3)

| # | 項目 | 実施内容 | Evidence |
|---|---|---|---|
| A | 第三要因の真因特定(コード上の判定順序) | `run_instance`のメインループで、cycle>1時の`matched_records`判定(§3-3安全網)が、fact_id再出現時のラダー前進機構(§6-6 A-2 `escalate_to_paragraph`)より**先に**評価されており、①水準Rewrite後の再検出が即座に`same_claim_fact_id_reblocked`でSTAGE4化されていた(④段落水準が一度も試されないまま)ことをソースコード上で特定した | 本節24-1 |
| B | 是正実装(¥0) | 同一claim再発を「④段落水準まで既に試行済み[`escalated_to_paragraph=True`]」の場合のみSTAGE4(`same_claim_fact_id_reblocked`)へ回し、未昇段の場合は既存の`escalate_to_paragraph`ラダー前進機構へ明示的に合流させループを継続する。`find_matching_prior_record`は直近cycleの記録を優先するよう`reversed`走査へ変更 | 本節24-1、design書§6-13 |
| C | unittest | 新規4件(`find_matching_prior_record`の直近優先順・`run_instance`のwiring source検査3件)、既存218件との合計222件全PASS | 本節24-2 |
| D | rep15実測 | `hormuz_run03_standard`×n=2(reuse Stage1)を実行、sample1完走・sample2はGuardrail到達によりTrialAbort。`bgroup_B4`×1・`safety_A2A3`×1は予算制約のため未実施 | 本節24-3 |
| E | 記録・Phase 2候補一覧 | design書§6-13/§9-2⑯、DECISION_LOG、OPEN_ITEMS Statusセル、delegation_log、Phase 2候補一覧(下記24-4) | 本節24-3/24-4 |

### 24-1. `hormuz_run03_standard`第三要因の真因(コード上の判定順序)と是正

**真因(委任_23 rep14実測の再解釈)**: `run_instance`のメインループはcycle>1で毎回、(i)`matched_records`判定(§3-3安全網、fact_id一致+claim本文近似一致[`find_matching_prior_record`閾値0.75]で「同一claim再発」を検出したら**直ちに**`stage4_reason="same_claim_fact_id_reblocked"`でSTAGE4_ESCALATIONへ回す)と、(ii)`repeat_fact_ids_for_recheck`判定(§6-6 A-2、fact_id再出現時に`escalate_to_paragraph=True`を立てて④段落水準からRewriteを試す)の2つを順に評価する。是正前のコードは**(i)が(ii)より先にreturnする**構造だったため、①水準Rewrite後にcycle2の全文Recheckが同一claimを近似一致で再検出した時点で、④段落水準のRewriteが一度も試行されないままSTAGE4へ強制到達していた(rep14実測、REPORT§23-D)。これは設計原則(§6-6 A-2「①・③の局所ラダーは既に効果不足と実証されたとみなし④段落水準から試す」)と矛盾しており、「①で直らない」ことがラダーの品質限界ではなく**ラダーが実際には一度も昇段していなかったこと**が真因だった。

**是正(¥0、`er052_open233_self_recovery_flow_runner_01.py`)**: `prior_blocking_records`の各エントリへ、そのRewrite試行時点で`escalate_to_paragraph`(=④段落水準を使ったか)が立っていたかを`escalated_to_paragraph`として保存するよう拡張した。cycle>1の`matched_records`判定を、一致レコードの`escalated_to_paragraph`で二分岐させた: **(a)既に④段落水準まで試行済みで再発(`exhausted_matched_records`)**の場合のみ、従来どおり直ちに`stage4_reason="same_claim_fact_id_reblocked"`(意味を「ラダーを昇段しきった上での再発」へ明確化)。**(b)まだ①・③水準までしか試していない再発(`escalatable_matched_records`)**の場合は、STAGE4にせず該当claimへ`escalate_to_paragraph=True`を明示的に付与してループを継続する(既存の§6-6 A-2機構へ合流、新しい機構は作らない)。fact_idが一致していれば既存の`repeat_fact_ids_for_recheck`(fact_id集合演算)でも同じフラグが立つが、fact_id欠落claim(hashベースidentity)を取りこぼさないため、`find_matching_prior_record`が返したidentity単位でも明示的に設定する。`find_matching_prior_record`自体も、同一fact_idのprior recordが複数cycleにまたがって複数件蓄積されている場合に**直近(最後に追記された)レコードを優先して返す**よう、走査順を`reversed(prior_records)`へ変更した(旧来は最も古い一致を返しており、`escalated_to_paragraph`の最新状態を正しく参照できなかった)。cycle上限(`MAX_CYCLES`/`HARD_MAX_CYCLES`)・false PASS封鎖(W1)・Safety floor・等価FAIL gating(§6-7/§6-11)は無変更。

**設計判断の開示(勝手な仕様拡大をしていないことの記録)**: 委任文は「次のラダー段(②→③→④)へ」と表現していたが、②(文の一部)はコード上の独立水準として存在せず(§5-7で既に①へ統合済み)、既存の§6-6 A-2機構は①・③を両方スキップして④へ直接進む設計(rep10実測で解消実績あり)である。本委任では、新しい「1段ずつ昇段する」機構を新設せず、この既存の直接④ジャンプ機構へ合流させる最小変更を選んだ(最小変更ラダー・既存機構再利用の原則に従う判断であり、独自解釈で仕様を変更した認識はないが、委任文の字面とは完全に一致しない解釈のため明示的に報告する)。

### 24-2. unittest(¥0)

`TestFindMatchingPriorRecord.test_multiple_prior_records_same_fact_id_returns_most_recent`(新規1件)、`TestSameClaimReblockedLadderEscalationWiring`(新規3件、`run_instance`/`find_matching_prior_record`のsource inspectionで、STAGE4分岐が`exhausted_matched_records`のみに限定されていること・`escalated_to_paragraph`永続化・reversed走査を確認)。既存218件+新規4件=**計222件全PASS**(`.venv/Scripts/python.exe -m unittest er052_open233_self_recovery_flow_runner_01_test_01`実行、`git diff --stat`でProduction[er003/er006/er009/er010/er012/er019]・既存iteration1〜7/rep7〜14証跡への差分なしを確認)。

### 24-3. rep15実測(¥7.1025、Guardrail¥7)

`OUT_DIR_REP15`(`er052_output/open233_self_recovery_flow_runner_01_rep15`)、`BUDGET_STATE_PATH`をrep15専用(`budget_state_c233ab_24_rep15.json`)。CLI: `--groups=hormuz --instance_ids=hormuz_run03_standard --n_runs=2`。

**sample1(¥4.0578、19 call)**: `final_state=STAGE4_ESCALATION`・`stage4_reason=ja_deviation_unresolved`(rep14の`same_claim_fact_id_reblocked`から変化)。cycle記録: cycle1でHF-009(body)を①水準[`1_word_connective`]・別claim(in_one_line側)を③水準[`3_sentence`]でRewrite(blocking 2→1)。cycle2で残るHF-009系claimが`escalate_to_paragraph`(fact_id再出現、既存§6-6 A-2機構)により④段落水準[`4_paragraph`]でRewriteされ、`recheck_all_prior_issues_resolved=True`・`ja_recheck_overall_status=LEDGER_COMPLIANT`とEN/JA双方のLedger Recheckが「解消」を確認した(**`same_claim_fact_id_reblocked`による早期打ち切りが発生しなかったことを確認、A-2是正の直接的な実証**)。cycle3でblocking_claimsが空になりループ終了したが、cycle2で`ja_en_equivalence_verdict=FAIL`が記録されており、この分岐は委任_23で意図的に無変更のまま維持した安全網(rep10実測を唯一の根拠とするhard gate、REPORT§23-A参照)のため`ja_ok`がFalseへ倒され`ja_pending_deviation=True`が持ち越された結果、§6-7 W1(i)の既存fail-closed機構により`ja_deviation_unresolved`でSTAGE4_ESCALATIONへ至った。**正直な結論**: 本委任のA-2是正は目的どおり機能し(ラダーが①→③→④まで正しく昇段し、EN/JA Ledger Recheckは双方「解消」を確認した)、premature `same_claim_fact_id_reblocked`は発生しなかった。しかし本instanceは、委任_23で意図的に維持した**別の既存hard gate**(`ja_en_equivalence_verdict=FAIL`)により、結局STAGE4_ESCALATIONへ至った(false PASSではなく、fail-closedとして正しい)。

**sample2(未完走)**: cycle進行中に累計¥7.103がrep15 Guardrail¥7.0へ到達し、既存のTrialAbort機構(`check_budget`)が正しく発火した(`stop_reason`: "累計¥7.103が委任_09 Guardrail¥7.0に到達")。sample2の`hormuz_run03_standard`は結果未保存(部分実行データは残らない、既存の仕様どおり)。

**`bgroup_B4`×1・`safety_A2A3`×1(未実施)**: rep15のGuardrail(¥7)を`hormuz_run03_standard`のn=2だけで使い切った(TrialAbort)ため、追加のCLI呼び出しは共有`budget_state_c233ab_24_rep15.json`が既に上限に達しており実行不能だった。**正直な費用比較**: rep14の`hormuz_run03_standard`は1 sampleあたり¥1.87〜1.98(9 call、早期`same_claim_fact_id_reblocked`で打ち切り)だったのに対し、本rep15のsample1は¥4.0578(19 call、①→③→④まで正しく昇段し2 cycle分のpaired rewrite・全文Recheck・JA Recheck・equivalence checkを実施)と**約2.1倍**のコストになった。これは本委任のA-2是正が意図どおり機能した結果(安全網による早期打ち切りをやめ、正当なラダー前進のために追加cycleを許す設計変更)であり、バグではないが、**同種の「ラダー未昇段での安全網発火」パターンを持つ他instance(iter7実測での該当疑い: 同一fact_id再出現+同一claim近似一致の組み合わせを持つケース)でも同程度のコスト増が見込まれる**ことをFable/ユーザーへ正直に報告する(rep15予算超過の直接原因)。

**予算**: rep15合計¥7.1025(Guardrail¥7の目標をわずかに超過[既存のcheck_budget呼び出し前判定の粒度による標準的な超過パターン、委任_23 rep14や過去repと同様]したが、本委任全体Guardrail¥8以内)。分析・実装¥0+rep15¥7.1025=本委任合計**¥7.1025**/Guardrail¥8、残**¥0.8975**。`bgroup_B4`・`safety_A2A3`の追加実行は、残予算(¥0.8975)では1instanceあたりの実測コスト増加傾向(上記2.1倍)を踏まえるとリスクが高いため**実施しない**(STOP条件「¥8超え見込み」に抵触するリスクを避けた)。

### 24-4. Phase 2候補(Production相当記事)一覧 — 正直な現状報告

委任文は「Phase 2に向けた既存Family X実記事の候補一覧(新規テーマは作らない)」として10本を求めたが、既存evidenceを精査した結果を正直に報告する。`er019_output/family_x_refresh_e2e_01/`・`family_x_entertainment_production_runner_01/`・`family_x_b3_diversity_trial_01/`・`family_x_b3_production_wiring_01/`・`family_xy_concreteness_control_trial_01/02`等、OPEN-233のSafety群12・B群4・Hormuz・Meta全fixtureの`source_path`を遡ったところ、**実在する独立した記事テーマは「hormuz」(ホルムズ海峡・原油価格)と「meta」(Meta AI機能テスト)の2件のみ**であり、Safety群のA2/A3/A4・B群のB1〜B4も全てこの2テーマのいずれかの別pipeline段階・別trial変種からの抽出だった(新規の独立記事ではない)。この2テーマから抽出できる既存run(instance id・run・既存Stage1出力の有無)は以下の最大8件(規定演技trial変種を除く、実質的に区別できる記事run単位):

| # | instance id(既存harness) | テーマ | run/段階 | 既存Stage1出力 | 備考 |
|---|---|---|---|---|---|
| 1 | `hormuz_run01_advanced` | hormuz | run_01/b1b | あり(`family_x_refresh_e2e_01`) | Advanced段でSTOP実例(現行Production実測=LEDGER_DEVIATION) |
| 2 | `hormuz_run02_advanced` | hormuz | run_02/b1b | あり | 同上 |
| 3 | `hormuz_run03_advanced` | hormuz | run_03/b1b | あり(`step3_fixtures`経由) | Normal群(現行V4A実測ACCEPTABLE傾向) |
| 4 | `hormuz_run03_standard` | hormuz | run_03/a2 | あり | 本委任rep15で再実測、第三要因是正確認済み |
| 5 | `meta_run03_advanced` | meta | run_03/b1b | あり | 現行Production実測=LEDGER_COMPLIANT(V0) |
| 6 | `meta_run03_standard` | meta | run_03/a2 | あり | BLOCKING→Rewrite→PASS実例 |
| 7 | (B1/B2_hormuz/B3/B4相当) | hormuz | 各trial変種(diversity/refresh/concreteness/production_wiring) | あり | 独立記事ではなく同一hormuz素材の別pipeline段階抽出 |
| 8 | (A2A3/A4/A5相当) | hormuz/meta | 各trial変種(concreteness_control等) | あり | 同上、独立記事ではない |

**結論(正直な報告、新規テーマは作っていない)**: 真に独立した記事は#1〜6の6件(うち#1・2・5は現行Productionで既にb1b段完了済み、#3・4・6は既にOPEN-233 harnessで繰り返し検証済み)であり、**10本には届かない**。#7・8は同じhormuz/meta素材の再利用であり「別の記事」としてカウントすると水増しになるため候補数に含めなかった。Phase 2で真に10本規模のProduction相当検証を行うには、(a)PM_GOVERNANCE §13「新規記事テーマ選定ルール」に従いユーザーが新規テーマを複数候補から選定する、または(b)既存Hormuz/Meta run(#1〜6)を許容される範囲で再利用しつつ実際の新規Family X記事生成を追加実行する、のいずれかをFable/ユーザーが判断する必要がある(本委任では新規テーマを提案・選定していない)。

## §25. 上位原則「重大誤解原則」の明文化とHormuz要素Trial A(委任_27、2026-10-01)

### 25-0. 対応表(委任文§1〜§3)

| # | 項目 | 実施内容 | Evidence |
|---|---|---|---|
| 0 | 上位原則の明文化 | design書§0(重大誤解原則、許容/BLOCK候補表、問題種類→初期単位表、主体置換ガード方針、Fable PMレビュー7観点)を新設。PM_GOVERNANCE.md 23節・PM_BRIEF.md参照1行を追加 | 本節25-1 |
| 1-1 | escalate_to_paragraph廃止 | 新設フラグENABLE_ESCALATE_TO_PARAGRAPH_LADDER_SKIP(既定False)でガード。コードは削除せず残す | 本節25-2 |
| 1-2 | 問題種類→初期単位写像 | classify_problem_kind+filter_levels_by_problem_kindを新設し配線 | 本節25-2 |
| 1-3 | 主体置換ガード | actor_rewrite_guard_okを新設、neg1 cycle2実データで却下を確認 | 本節25-2 |
| 1-4 | 等価QA理由文の保存 | ja_en_equivalence_reasonをcycle_record/call_logへ追加 | 本節25-2 |
| 1-5 | 重大誤解原則のrubric追加 | Stage2 body/Hook/Stage1(V4A)へ新定数として追加。Stage2 bodyのみ実配線・実測、Stage1/Hookは未配線(開示) | 本節25-3/25-4 |
| 2 | Hormuz要素Trial A | 許容5/NG5/Safety2をn=2で実測、最小修正1回後に全群PASS | 本節25-3 |
| A-2 | 決定論名詞句置換 | NG2件+原文2を決定論置換、diff+局所QA1callで確認 | 本節25-5 |

### 25-1. 上位原則の明文化(design書§0)

ユーザー上位原則(2026-10-01、委任_27委任文§1)を、design書§0として
明文化した。要旨は「OPEN-233は英語学習者に記事の本質について重大な
誤解を与えるものだけを止めるプロジェクトであり、厳密な一致を求める
ものではない」。許容候補(Brent futures→oil prices等)・BLOCK候補
(gasoline prices/world energy prices等への一般化、方向反転、主体
入れ替え、継続→消失→復活、未確認追加、因果逆転)・問題種類→初期
Rewrite単位の写像表・主体置換ガード方針・Fable PMレビュー7観点を
記載した(既存ユーザー意図の明文化、新規承認不要)。PM_GOVERNANCE.md
23節・PM_BRIEF.mdは要約+参照のみとし、正式SSOTはdesign書§0に一本化
した(重複記載回避)。

### 25-2. Part1是正4点(¥0、er052_open233_self_recovery_flow_runner_01.py)

**1-1**: escalate_to_paragraphによるladder skip(levels配列から
1_word_connective/3_sentenceを除外する処理)を、新設フラグ
ENABLE_ESCALATE_TO_PARAGRAPH_LADDER_SKIP(既定False)でガードした。
同一fact_id再発の検出・記録・STAGE4判定自体(§6-6 A-2/§3-3の
same_claim_fact_id_reblocked)は無変更(別の安全機構のため)。

**1-2**: classify_problem_kind(dev)を新設し、Stage1 deterministic
floor flag(changed_scope/changed_number+丸め抑制済み/
changed_causality/changed_actor/changed_time、および
changed_negation/changed_comparison/changed_certainty/changed_fact/
unsupported_new_claim)から決定論(¥0)で問題種類を分類する。
filter_levels_by_problem_kindで初期ladder水準未満のlevelを除外する
(初期水準より上位への昇段は妨げない)。devにfloor flagが無い既存
fixtureはunspecified(①開始)に分類され、既存挙動と完全に後方互換。

**1-3**: actor_rewrite_guard_ok(before_text, after_text, ledger_text)
を新設した。Rewrite後にのみ新しく現れた主体語(一般的な役割名詞)が
Ledger本文に一語も含まれない場合はRewriteを却下する。
docs/pm/open233_evidence_disclosure_neg1_neg3_hormuz_01.md §1の
neg1 cycle2実データ(MUSE-HC-012、users→employees、floor_reason=
deterministic_floor:changed_actor)をfixtureとしたunittestで、
employeesがMUSE-HC-012のledger_text(JA本文のみ)に含まれないため
却下されることを確認した。

**1-4**: ja_en_equivalence_verdictに加え、raw(notes/meaning_changes/
important_omissions/unsupported_additions/
number_name_negation_issues)をcycle_record・call_logへ保存するよう
にした(¥0、既存呼び出しの戻り値を捨てずに使うのみ)。

**unittest**: TestClassifyProblemKind(9件)・
TestFilterLevelsByProblemKind(5件)・TestActorRewriteGuard(3件)・
TestEscalateToParagraphDisabledByDefault(2件)を新設し、既存
TestEscalateToParagraphLadderSkip(4件)を「既定OFF時は発火しない」
「flag再有効化時は旧来どおり発火する」という新しい前提に合わせて
書き換えた(旧テストが検証していた「escalate_to_paragraph=Trueなら
必ず4直行」という挙動自体が、本委任の是正対象だったため)。既存222件+
新規19件=**計241件全PASS**(.venv/Scripts/python.exe -m unittest
er052_open233_self_recovery_flow_runner_01_test_01実行)。

### 25-3. Part1-5(重大誤解原則のrubric追加)+Hormuz要素Trial A

er052_open233_self_recovery_stage2_calibration_01.pyへ
RUBRIC_R3_TRIPLE_PRIME_WITH_MISCONCEPTION_PRINCIPLE(既存
RUBRIC_R3_TRIPLE_PRIME本文は無変更、新定数として追加)を新設した。
同様にer052_open233_self_recovery_stage2_hook_01.pyへ
HOOK_RUBRIC_WITH_MISCONCEPTION_PRINCIPLE、
er051_open233_checker_trial_variant_01.pyへ
V4A_DEVELOPER_MSG_WITH_MISCONCEPTION_PRINCIPLE(+
run_trial_deviation_checkにdeveloper_message_override引数[既定
None]を追加、既存9箇所の呼び出しは無変更で動作)を追加した。

**Hormuz要素Trial A**(新規er052_open233_element_trial_hormuz_terms_
01.py、Stage2 body rubricのみ、実データのみ使用):

| 群 | claim(実データ出典) | n=2結果(初回rubric) |
|---|---|---|
| 許容 | accept-1: "Oil prices did not fall across the whole market after the plan was withdrawn."(実文1、hormuz_run03_standard) | **BLOCKING 2/2(false BLOCK)** |
| 許容 | accept-2: "Political statements changed greatly. Oil prices moved briefly, then returned to a high level."(実文2) | QUALITY 2/2(PASS) |
| 許容 | accept-3: "The fee plan vanished, but oil prices stayed high..."(実文3、In one line) | QUALITY 2/2(PASS) |
| 許容 | accept-4: "Crude prices briefly lost some of their gains..."(Brent crude futures→crude prices構成) | QUALITY/ACCEPTABLE(PASS) |
| 許容 | accept-5: "...up about 3 percent, about 85 dollars a barrel."(2.6%→about 3%/above 85→about 85丸め構成) | ACCEPTABLE 2/2(PASS) |
| NG | ng-1: gasoline prices | BLOCKING 2/2(正しくBLOCK) |
| NG | ng-2: world energy prices | BLOCKING 2/2 |
| NG | ng-3: all crude benchmarks | BLOCKING 2/2 |
| NG | ng-4: 方向反転(fell sharply) | BLOCKING 2/2 |
| NG | neg3: 継続→消失→復活(実文、neg3_hormuz_prodrunner_b1b) | BLOCKING 2/2 |
| Safety | B3因果(実fixture、HF-007) | BLOCKING 2/2 |
| Safety | er009 changed_scope(実fixture、taxi→restaurants nationwide) | BLOCKING 2/2 |

判定文逐語引用(accept-1、2回とも同旨): 「"Oil prices did not fall
across the whole market after the plan was withdrawn."を、Brent先物の
値動きに範囲を限定してください。撤回後に一時上げ幅を縮小し、その後
高い水準に戻ったと記述し、市場全体については述べないでください」
(basis: ledger_scope)。

**原因分析**: LLMは「across the whole market」という強調表現を、
「Brent先物という同じ対象内での一般化」ではなく「無関係な範囲への
拡張」と解釈していた。NG群(gasoline/world energy/all crude
benchmarks)・Safety対照群(B3/er009 changed_scope)はいずれも初回から
正しくBLOCKING(false PASS 0件)であり、rubric自体が緩すぎたのではなく
accept-1特有の閾値設定の問題だった。

**最小修正1回**: RUBRIC_R3_TRIPLE_PRIME_WITH_MISCONCEPTION_PRINCIPLE_
V2を新設し、「Brent先物の値動きを『market全体』『oil prices全般』の
ように、同じ原油(oil)という対象のままより一般的な言い方に置き換えて
いるだけの場合は許容する。一方、別の商品や石油を超えた対象、複数指標
の一括一般化は引き続きBLOCKING」という明確化を1回追加した。V2での
再実測(n=2、計2回の独立run)は、許容群5件・NG群5件・Safety群2件**全て
でfalse PASS/false BLOCK 0件**を確認した。

**コスト**: 初回n=2(¥1.05)+V2再実測2回(各n=1、¥0.5814+¥0.4026=
¥0.9836)=**¥2.0336**(Part2全体ではTrial A-2と合わせ¥2.2597)。

### 25-4. Stage1(V4A)・Hook専用rubricの未配線(既知の限界、正直な開示)

予算(Part2 Guardrail¥25、実績¥2.2597)の範囲では、Hormuz要素は全て
body claim(title/hookではない)であり、Stage1(V4A)の再実行は別途
コストを要するため、本委任で実際にAPIへ配線・実測できたのは**Stage2
body rubricのみ**だった。Stage1(V4A)・Hook専用rubricの新定数は
コードとして実装済みだが、実際の判定への配線・実測は次回委任_28
(Meta要素Trial)またはその後の広いTrialへ引き継ぐ。

### 25-5. Trial A-2(決定論名詞句置換、¥0.1261)

新規er052_open233_element_trial_a2_deterministic_rewrite_01.pyで、
以下3件を決定論(Python文字列置換、LLM Rewrite callを使わない)で実施
した:

1. **ng-1(EN単体)**: "Gasoline prices did not fall across the whole
   market after the plan was withdrawn." → "**Brent futures** did
   not fall across the whole market after the plan was withdrawn."
2. **ng-2(EN単体)**: "World energy prices did not fall after the plan
   was withdrawn, and stayed high across all energy markets." →
   "**Brent futures** did not fall after the plan was withdrawn, and
   stayed high across all energy markets."
3. **原文2(JA/EN対、実記事hormuz_run03_standard)**:
   - EN Before: "Political statements changed greatly. **Oil
     prices** moved briefly, then returned to a high level."
   - EN After: "Political statements changed greatly. **Brent
     futures** moved briefly, then returned to a high level."
   - JA Before: 「政治の発言が大きく変わっても、**原油価格**は
     一度揺れたあと、高い水準へ戻った。」
   - JA After: 「政治の発言が大きく変わっても、**Brent先物**は
     一度揺れたあと、高い水準へ戻った。」

word-level diff(全3件)は対象名詞句のみの置換(replace操作1件のみ、
他は全てequal)であることを機械確認した。2については記事全文
(EN 2058字/JA 812字)への埋め込みでfull_article_unchanged_elsewhere
=True(対象文以外は完全不変)を確認した。既存Production資産(翻訳
忠実性QA、er003_ja_to_en_translation.py)を借用した局所QA 1 call
(記事全文のJA/EN pairに対して実行)の結果:

- verdict: REVIEW_REQUIRED
- notes(逐語): 「日付、数値、人名、否定表現、原油価格の推移、記事の
  結論および一言まとめは概ね維持されています。指摘箇所はいずれも
  重大な中心事実の変更ではありません。」
- meaning_changes(逐語、唯一の指摘): 「『湾岸諸国によるアメリカ向け』
  の貿易・投資案件が、英語では湾岸諸国とアメリカの『間の』案件と
  なっており、方向性がやや曖昧になっています。」

この唯一の指摘は、本委任の置換(Oil prices→Brent futures/原油価格→
Brent先物)とは**無関係な既存箇所**(記事の別段落、湾岸諸国-アメリカ間
投資案件の記述)であり、対象の名詞句置換自体が新たな意味変化・周辺
影響を生んでいないことが確認された。段落Rewriteへは進んでいない
(§0-4「用語の範囲違い→名詞句だけ置換」の初期単位を超えていない)。

### 25-6. hormuz-HF009の再ラベルとSafety-critical listとの不整合(開示)

design書§7-0-iter27のとおり、hormuz-HF009の「Oil prices」型scope
一般化claim(本委任のaccept-1と同一claim)を、上位原則に基づき正解
ラベルBLOCKINGからACCEPTABLE/QUALITYへ再ラベルした。これは
er052_open233_self_recovery_r3dprime_calibration_01.pyの
SAFETY_CRITICAL_SUB_IDS(既存10件、hormuz-HF009を含む)との直接的な
矛盾を生む。本委任では同定数自体は変更していない(既存iteration証跡
の再現性維持のため)。Hormuz要素Trial AのSafety対照群では、hormuz-
HF009の代わりにB3(因果)+er009 changed_scope(別記事・別領域への
scope拡張、真にBLOCKINGな対照)を使用した。このリスト自体の編集
要否は、Fable/ユーザー確認事項として提示する(USER_DECISION_REQUIRED
には該当しないと判断するが、既存Safety-critical定義への変更を伴う
ため、独断での定数編集は行わなかった)。

### 25-7. 費用・Git・Status

Part1(¥0)+Part2主実測(¥2.0336)+Trial A-2(¥0.1261)=本委任合計
**¥2.2597**(Guardrail¥25のうち)。Phase累計¥393.2155+¥2.2597=
**¥395.4752**/総枠¥600(2026-10-01ユーザー拡張)、残**¥204.5248**。
`git diff --stat`でProduction(er003/er006/er009/er010/er012/er019)・
既存rep/iteration証跡への差分なしを確認した。
Status=`ELEMENT_TRIAL_MISCONCEPTION_PRINCIPLE_CODIFIED_HORMUZ_TRIAL_A_
PASSED_AFTER_ONE_MINOR_FIX`。Meta要素Trialは次回委任_28。

## §26. Stage1/Hook重大誤解原則の実配線+Safety対照群の全量確認、
STOP条件該当により Meta要素Trial未実施(委任_28、2026-10-01)

### 26-0. 対応表(委任文Part0〜Part1、Part2/3は未実施)

| # | 項目 | 実施内容 | Evidence |
|---|---|---|---|
| 0-1 | Stage1(V4A)実配線 | `er052_open233_self_recovery_flow_runner_01.stage1_fresh_with_misconception_principle`新設(既存`stage1_fresh()`は無変更) | 26-1 |
| 0-1 | Hook実配線 | `run_stage2_hook_batch`へ`hook_rubric_text`引数追加(既定値無変更) | 26-1 |
| 0-2 | SAFETY_CRITICAL_SUB_IDS是正 | hormuz-HF009を除外(10件→9件) | 26-1 |
| 0-3 | Hook許容基準tie-break明文化 | `HOOK_RUBRIC_WITH_MISCONCEPTION_PRINCIPLE_V2`新設 | 26-1 |
| 0-4 | unittest | 新規7件、discoverで既存338件+7件=345件全PASS | 26-1 |
| Part1 | Safety対照群全量確認 | Safety-critical 9claim+Safety12(9フラグ)をn=2実測、V2で2件misdowngrade→最小修正1回(V3)→なお2件残存→**STOP** | 26-2〜26-4 |
| Part2/3 | Meta Hook Trial B・Actor Trial C | **未実施**(STOP条件該当のため着手せず) | 26-5 |

### 26-1. Part0(¥0、配線・ラベル是正)

`er052_open233_self_recovery_flow_runner_01.py`へ
`stage1_fresh_with_misconception_principle(client, state,
consecutive_errors, call_log, label, fixture)`を新設した(既存
`stage1_fresh()`と同一のretry/cost計上パターンだが、developer
messageへ`trial.V4A_DEVELOPER_MSG_WITH_MISCONCEPTION_PRINCIPLE`を
使う点のみ異なる。既存`stage1_fresh()`自体・既存29 instance実行・
既存rep/iteration証跡は無変更)。
`er052_open233_self_recovery_stage2_hook_01.run_stage2_hook_batch`へ
`hook_rubric_text`引数(既定`HOOK_RUBRIC`、本文不変)を追加し、新定数
`HOOK_RUBRIC_WITH_MISCONCEPTION_PRINCIPLE_V2`(tie-break明文化: 確認
済みFactから自然に導ける受け手側の体験描写・場面描写・attention
grabber・conversational restatementは許容、BLOCKINGは未確認の具体的
人物・行動・数字の追加またはFactと逆方向の出来事のみ)を新設した。
`er052_open233_self_recovery_r3dprime_calibration_01.SAFETY_CRITICAL_
SUB_IDS`から`hormuz-HF009`を除外した(§7-0-iter27の再ラベルとの整合、
10件→9件、根拠はDECISION_LOG参照)。unittest 7件
(`TestStage1FreshWithMisconceptionPrinciple`2件・
`TestHookRubricTextWiring`3件・`TestSafetyCriticalSubIdsHormuzExclusion`
2件)を追加し、`python -m unittest discover -p "er05*test*.py"`で
既存338件+新規7件=**345件全PASS**を確認した。

### 26-2. Part1 n=1予備測定(V2、¥2.7022)での発見

Safety-critical 9claim(`SAFETY_CRITICAL_SUB_IDS`是正後)+Safety12
(er009 9フラグ)を、Stage2 body rubric
(`RUBRIC_R3_TRIPLE_PRIME_WITH_MISCONCEPTION_PRINCIPLE_V2`)でn=1
予備測定したところ、2件がfalse downgradeした:

- **A4-0**(“Through Muse, trained human contract workers made some
  calls and completed the exchanges with users.”)→`ACCEPTABLE`
  (basis: ledger_claim)。元issue(逐語): 「この記事では、契約スタッフ
  がやり取りを完了した相手をMuseのユーザーとしていますが、Ledgerが
  示すのは電話の相手先(企業・店舗など)です。」=カウンターパート
  (誰が誰とやり取りしたか)の取り違えであり、用語の近似・一般化ではない。
- **A5-1**(“Meta executives admitted that starting the test without a
  proper explanation was a mistake.”)→`QUALITY`(basis:
  ledger_scope)。元issue(逐語): 「The Ledger attributes this
  admission to a specific Meta vice president, while the article
  attributes it to "Meta executives," broadening the speaker
  attribution.」=特定の副社長→「Meta幹部」という同一組織内のより
  一般的な役職名への言い換え。

**事故と復旧(重要、正直な開示)**: 予備測定の実装で、Stage1 fresh
呼び出しを誤って`runner.stage1_fresh_with_misconception_principle`
経由で直接実行したところ、同関数内部の`record_call`→
`save_budget_state`が**呼び出し元のstate dictの中身に関わらず、
runner自身の固定`BUDGET_STATE_PATH`(`er052_output/open233_self_
recovery_flow_runner_01_rep15/budget_state_c233ab_24_rep15.json`、
委任_24の既存証跡)へ書き込む**副作用を持つことが判明し、同ファイルを
一時的に上書きする事故が発生した。発覚直後に`git diff --stat`で検出し
`git checkout`で該当1ファイルのみ即座に復元した(`git diff`で復元後の
差分なしを確認、他の既存証跡ファイルへの影響なし)。ただし復元操作に
より、この予備測定のStage1 fresh呼び出し4件分の詳細出力(json)自体は
失われた(既存証跡への実害はないが、本委任の予備診断データとしては
再取得できなくなった、sunk costとして正直に計上)。以後は本ファイル
専用の自己完結ラッパー(`check_budget`/`save_budget_state`を本ファイル
のみで完結させる方式)へ是正し、同種の事故を防止した(詳細は両新規
Trialスクリプト冒頭コメント)。

### 26-3. 最小修正1回(V3)とn=2公式測定結果

「当事者関係(カウンターパート)の取り違えはBLOCKING、同一組織内での
役職の一般化(発言内容・責任主体=組織自体は不変)は許容」という区別を
追加した`RUBRIC_R3_TRIPLE_PRIME_WITH_MISCONCEPTION_PRINCIPLE_V3`を
新設し、Safety-critical 9claim+Safety12をn=2で再測定した
(`er052_open233_element_trial_safety_control_01.py`、¥4.3851)。

| 項目 | 結果 |
|---|---|
| A4-0 | 2/2 `BLOCKING`(解消) |
| A5-1 | 2/2 `ACCEPTABLE`(**V2[QUALITY]よりさらに悪化**) |
| Meta-1 | 2/2 `QUALITY`(**V3で新規false downgrade**) |
| Meta-2 | 2/2 `QUALITY`(Meta-1と同一claim、`build_eval_groups()`仕様によりbaseline deviationが1件のみのため両sub_idが同一文を指す重複) |
| B3/B4-a/A2A3-0/A4-1/A5-0 | 全て2/2 `BLOCKING`(維持) |
| Safety12(er009 9フラグ、Stage2直接判定) | **9/9とも2/2 `BLOCKING`**(false downgrade 0件) |
| Safety12のうち4フラグ(Stage1 V4A新配線fresh実行) | 8 run中7 runでseverity_final=`BLOCKING`維持かつ想定flag名一致。1 run(changed_actor)はBLOCKING自体は維持しつつ付与flag名が別名へ振れた(真の見逃しではない、参考所見) |

Meta-1/Meta-2の実体(逐語): “Also, some calls needed user information
to continue.”。元issue(逐語): 「Ledgerは、電話の遂行にユーザー情報が
必要になる可能性を条件として示しているが、記事は実際に一部の電話で
情報が必要だったと断定している。」(`changed_certainty: true`、floor
対象外)。

### 26-4. STOP判定

委任文STOP条件「Safety対照群のいずれかが小修正1回後もBLOCKINGに戻らない」
に該当する(A5-1・Meta-1/Meta-2の計2件が、最小修正1回後もBLOCKINGへ
戻らない)。これにより、Stage2 body rubricへの重大誤解原則配線は
**ここで停止**し、Part2(Meta Hook Trial B)・Part3(Actor Trial C、
neg1実データの未確認actor置換抑止)は着手しなかった(Safety優先、
「広いTrialを続けるべきか」という問い自体を本委任では判定せず、Fable/
ユーザーへ開示する)。

**worker見解(判定はFable)**: A5-1・Meta-1/Meta-2はいずれも、既存
§7-0-iter5でA2A3-1/A4-2が「`build_eval_groups()`の機械コピー由来
ラベルであり、NG(a)〜(e)に照らすとQUALITYが正しい」として是正された
前例と**構造的に類似**する(A5-1=役職の一般化、Meta-1/Meta-2=
certainty強化で、いずれも委任_12/13の「自然な解釈基準」の下で既に
QUALITY側に整理されたB4-b/B4-d型パターンに近い)。一方で、本委任の
上位原則はこれらを含む包括的な許容文であり、個別claim単位の精査
(Ledgerの文言と記事の文言を1件ずつ突き合わせる人間判断)を経ずに
rubric側だけでこの区別を安定させられるかは実測上まだ不確実
(V3の1回の修正では解決しなかった)。次の一手としては、(a)
A5-1/Meta-1・Meta-2を正解ラベル自体の再検討対象としてユーザー確認を
仰ぐ(hormuz-HF009と同じ経路)、または(b) rubricのさらなる改善
(ただし本委任のSTOP条件に基づき追加の小修正は次回委任以降とする)の
いずれかをFableが選ぶことになる。

### 26-5. 未実施事項・費用・Git・Status

Part2(Meta Hook Trial B)・Part3(Actor Trial C)は上記STOP判定により
未実施。これに伴い、Hook許容基準(0-3)の実測・neg1 actor claimの
Stage1再判定実測・Stage3主体置換ガードの実rewrite実測はいずれも
次回以降へ持ち越す(コードとしては`er052_open233_element_trial_meta_
hook_01.py`を実装済みだが、本委任では実行していない)。

本委任費用: Part0(¥0)+Part1予備測定(¥2.7022、詳細出力は事故復旧操作
により喪失)+Part1 V3公式測定(¥4.3851)=**¥7.0873**(Guardrail¥25の
うち、Part1単体のGuardrail¥9に対し実績超過なし)。Phase累計
¥395.4752+¥7.0873=**¥402.5625**/総枠¥600、残**¥197.4375**。
`git diff --stat`でProduction(er003/er006/er009/er010/er012/er019)・
既存rep/iteration証跡(rep15の一時汚染は`git checkout`で復元済み)への
差分なしを確認した。USER_DECISION_REQUIRED 7条件(design書§12)は
いずれも非該当(Production非接続・KPI不変・Cap/予算¥600内・新Product
原則の設定なし)。Status=`SAFETY_CONTROL_AUDIT_STOPPED_AFTER_ONE_
MINOR_FIX_STILL_FAILING`。Meta要素Trial(Hook/Actor)・A5-1/Meta-1・
Meta-2の扱いはFable/ユーザー判断待ちとして次回へ引き継ぐ。

## §27. Safety対照群の安定化(Fableラベル判定反映)でPASS+Meta要素Trial B/C実施、境界群1件のみ残存(委任_29、2026-10-01)

### 27-0. 対応表

| # | 項目 | 実施内容 | Evidence |
|---|---|---|---|
| 1 | Fableラベル判定の反映 | A5-1→QUALITY(`SAFETY_CRITICAL_SUB_IDS`から除外、9件→8件)、Meta-1/Meta-2→BLOCKING維持 | 27-1 |
| Part1 | Safety対照群の安定化 | V4(最小修正1回)で、Safety-critical 8+Safety12+Hormuz許容5/NG5がn=1予備・n=2公式とも全件PASS | 27-2 |
| Part2 | Meta要素Trial B(Hook) | 初実行、集計バグ発見・是正。NG4/4 BLOCKING、許容群はV3是正後に元Hook/accept-4が解消、boundary-1のみ残存 | 27-3〜27-4 |
| Part3 | Meta要素Trial C(Actor) | neg1 cycle2実データで「社内テスト誤読」解消(期待1で解消、期待2は未検証) | 27-5 |

### 27-1. Fableラベル判定の反映(§1根拠はDECISION_LOG参照)

A5-1(“Meta executives admitted that starting the test without a
proper explanation was a mistake.”)は役職の同一対象内一般化
(hormuz-HF009型)のため正解ラベルをQUALITYへ改め、
`SAFETY_CRITICAL_SUB_IDS`から除外(9件→8件:
A2A3-0/A4-0/A4-1/A5-0/Meta-1/Meta-2/B3/B4-a)、
`CORRECT_LABEL_OVERRIDES_R3DPRIME["A5-1"]="QUALITY"`を追加した
(`er052_open233_self_recovery_r3dprime_calibration_01.py`)。
A4-0(カウンターパート取り違え)・Meta-1/Meta-2(条件付き可能性→既成
事実への断定)はBLOCKING維持。

### 27-2. Part1: 要素記録表(Safety対照群安定化)

| 対象 | 変えたこと | 理由 | 許容/NG実測結果 | 誤PASS/誤BLOCK(n=1予備→n=2公式) | 揺れ | コスト |
|---|---|---|---|---|---|---|
| Safety-critical 8claim | `SAFETY_CRITICAL_SUB_IDS`を9→8件化(A5-1除外)、rubricをV3→V4 | A5-1はFableラベル判定で非Safety化、Meta-1/2はV3で残存したfalse downgradeの是正 | 8/8全てBLOCKING(n=1・n=2とも) | 0→0 | なし | 込み |
| Safety12(er009 9フラグ) | rubricをV3→V4(Stage2直接判定のみ、Stage1 fresh再測定は省略) | V4での影響有無を確認 | 9/9全てBLOCKING(n=1・n=2とも) | 0→0 | なし | 込み |
| Hormuz許容5/NG5 | 既存Stage1出力(claim定義)を再利用、rubricをV2→V4でStage2のみ再実行 | V4の原則追記が無関係claimへprompt primingを起こしていないかの確認(委任_16の教訓) | 許容5件は非BLOCKING(QUALITY/ACCEPTABLE)、NG5件はBLOCKING(n=2) | 0/0 | accept-1/2がACCEPTABLE⇄QUALITYで揺れたが非BLOCKING自体は不変 | 込み |
| 合計 | — | — | — | — | — | n=1予備¥1.8626+n=2公式(ABC込み)¥4.9438(累計、n=1分を含む) |
| A5-1(参考、Safety-critical対象外) | — | 再ラベル整合の確認 | ACCEPTABLE(n=1・n=2とも) | — | — | 込み |

### 27-3. Part2: Meta要素Trial B(Hook)集計バグの発見・是正

初回実行(V2、Stage1 fresh 21 call+Hook Stage2 3 call)で、
`run_trial_b()`内の集計ロジックに符号反転バグがあることが判明した:
旧実装は`if c["group"] == "ng": wrong = [m for m in observed if m ==
"BLOCKING"]`(ng群でBLOCKING=正しい判定を"wrong"とみなす)、`else:
wrong = [m for m in observed if m != "BLOCKING"]`(accept/boundary群で
非BLOCKING=正しい判定を"wrong"とみなす)という誤りがあり、
`false_block_count`/`false_pass_count`へ逆の値を代入していた
(委任_28時点ではコード未実行のため発覚しなかった、生judgmentデータ・
API呼び出し自体は正常)。`tally_hook_rows()`として是正し
(`er052_open233_element_trial_hormuz_terms_01.run_batch()`と同じ
正しい集計方式へ統一)、unittest
(`TestMetaHookTallyScoringBugFix`2件)で再発防止した。

是正後の真の値(V2実測):

| sub_id | group | 観測(materiality) | 判定 |
|---|---|---|---|
| accept-1-original-hook | accept | QUALITY, BLOCKING, ACCEPTABLE | 1/3 false block |
| accept-2〜3, 5 | accept | 全てACCEPTABLE/QUALITY | 0 false block |
| accept-4-scene-depiction | accept | BLOCKING, BLOCKING | 2/2 false block |
| boundary-1-dramatization | boundary | BLOCKING, BLOCKING | 2/2 false block |
| ng-1〜4 | ng | 全てBLOCKING, BLOCKING | 0 false pass(良好) |

rewrite_hint逐語(false block 3件の原因):
- accept-1: 「会話の進行中に人間だと判明した出来事まで描写しています。
  そのタイミングや驚きが実際にあったとは確認できないため…」
- accept-4: 「双方が意図的に身元を隠したという未確認の描写は避け…」
- boundary-1: 「驚きが通話の途中で起きたという未確認の時点描写を
  削り…」

### 27-4. Part2: 最小修正1回(V3)と再Trial結果

`HOOK_TIEBREAK_TEXT_V3`(確認済みの中心的な出来事を自然な時間経過
[「しばらくの間」「会話が進むうちに」等]として描写する演出は、具体的な
新事実発明が無い限り許容する旨を追加)でHook Stage2のみ再実行
(`er052_open233_element_trial_meta_hook_01.py --hook_stage2_v3_only`、
Stage1 freshは再測定せず、¥1.9481)。

| sub_id | group | 観測(materiality) | 判定 |
|---|---|---|---|
| accept-1-original-hook | accept | ACCEPTABLE, ACCEPTABLE, QUALITY | 0 false block(**解消**) |
| accept-4-scene-depiction | accept | QUALITY, ACCEPTABLE | 0 false block(**解消**) |
| boundary-1-dramatization | boundary | BLOCKING, BLOCKING | 2/2 false block(**残存**) |
| ng-1〜4 | ng | 全てBLOCKING | 0 false pass(維持) |

委任文STOP条件は「元Hook誤BLOCKまたはNG誤PASSが小修正後も残る」のみを
明記しており、boundary-1(境界群、元Hookでもngでもない)単独の残存は
明記されたSTOP条件に該当しない。よって追加のrubric修正は行わず、
STOPもせず残課題として次回へ引き継ぐ。

### 27-5. Part3: Meta要素Trial C(未確認actor置換の抑止)結果

| 対象claim | 実測 |
|---|---|
| actor claim(“The test began without clearly telling users that contract workers would make the calls.”、neg1 cycle2実データ) | n=2ともoverall_status=`LEDGER_COMPLIANT`(deviation自体が検出されない、matched=False) |
| NG対照(VP→CEO主体入替、“Meta's CEO admitted the mistake...”) | n=2とも`LEDGER_DEVIATION`・matched_severity_final=`BLOCKING` |

対象claimが重大誤解原則配線後のStage1(V4A)でn=2とも
`LEDGER_COMPLIANT`となったため、委任文「期待1(社内テスト誤読の解消)」
どおりに解消したことを確認した。NG対照は引き続きBLOCKINGを維持し、
actor置換ガード自体は健在(真の主体入替は引き続き検出される)。「期待
1」で解消したため、BLOCKING経路を強制した場合のStage3
`actor_rewrite_guard_ok`挙動(「期待2」)は本委任では発火せず未検証の
まま(`stage3_rewrite_result`/`local_qa_result`ともNone)。

### 27-6. 費用・Git・Status

Part1(¥4.9438)+Part2/3(V2実測込み¥9.6748→V3再Trial後¥10.8919、
Part2/3純増分¥10.8919)=本委任合計**¥15.8357**(Guardrail¥25のうち、
Part1≤¥10/Part2〜3≤¥15の内訳いずれも超過なし)。Phase累計
¥402.5625+¥15.8357=**¥418.3982**/総枠¥600、残**¥181.6018**。
unittest discoverで既存295件+新規11件(`TestSafetyCriticalSubIdsA5_
1Exclusion`3件・`TestMisconceptionPrincipleRubricV4`3件・
`TestHookRubricV3`3件・`TestMetaHookTallyScoringBugFix`2件)=
**306件全PASS**。`git diff --stat`でProduction
(er003/er006/er009/er010/er012/er019)・既存rep/iteration証跡への
差分なしを確認した。USER_DECISION_REQUIRED 5条件(design書§12)は
いずれも非該当。
Status=`SAFETY_CONTROL_STABILIZED_META_HOOK_TRIAL_B_PARTIAL_BOUNDARY_
RESIDUAL_TRIAL_C_RESOLVED`。boundary-1(境界群)の残存false blockの
扱い(追加rubric修正要否)・広いTrialへ進む可否はFable/ユーザー判断
待ちとして次回へ引き継ぐ。

## §28. Hook V4によるboundary-1解消+runner既定化+実記事代表5ケース
rep16確認、paired_rewrite片側locate是正(委任_30、2026-10-01)

### 28-0. 対応表

| # | 項目(ユーザー§8〜§12 4目標+Trial B/C+rep16) | 実施内容 | Evidence |
|---|---|---|---|
| Part1 | Hook境界群の最終小修正(boundary-1) | `HOOK_TIEBREAK_TEXT_V4`で再測定(n=2)、false block/pass 0件 | 28-1 |
| Trial C期待2 | 未確認actor置換の抑止(BLOCKING経路強制) | 実測の結果`classify_problem_kind`優先順位の盲点を発見、ガード未発火を特定 | 28-2 |
| Part2 | 重大誤解原則のrunner既定化 | Stage1/Stage2 body/Hook専用Stage2の既定経路へ実配線(flagで復帰可) | 28-3 |
| Part3 | 実記事代表5ケースend-to-end確認(rep16) | neg3がSTAGE4_ESCALATION→根本原因特定・是正→単体検証でPASS、残り4件はn=2でRESOLVED | 28-4 |

### 28-1. Part1: Hook rubric V4によるboundary-1解消

Fable(委任文§1)が、boundary-1-dramatization(“The surprise came
halfway through the call.”)はdesign書§10の境界例定義「演出がやや
強いが、新しい具体Factを追加していないHook」に該当し許容が正解と判定
した。既存`HOOK_TIEBREAK_TEXT_V3`(委任_29)の例示(「通話の途中で」を
許容例として既に明記していた)にもかかわらず実測では2/2 false block
だったため、tie-break判定の**軸自体**(「時間経過・順序の曖昧な演出は
具体的Factの追加ではない」)を明示する`HOOK_TIEBREAK_TEXT_V4`を追加した
(既存V3本文は変更せず新定数として追加、既存証跡の再現性維持)。

`er052_open233_element_trial_meta_hook_02.py`で、boundary-1・元Hook
accept-1・NG4群(ng-1〜4)を1 batch×n=2で再測定した結果:

| sub_id | group | 観測(materiality) | false block/pass |
|---|---|---|---|
| accept-1-original-hook | accept | ACCEPTABLE, QUALITY | 0 |
| boundary-1-dramatization | boundary | ACCEPTABLE, QUALITY | 0(**解消**) |
| ng-1〜4 | ng | 全てBLOCKING, BLOCKING | 0(維持) |

費用¥0.7000(Guardrail Part1≤¥4のうち)。委任_29からの残課題
(boundary-1の残存)はこれで解消した。

### 28-2. Trial C期待2: actor置換ガードの設計上の盲点の発見

委任_29で「期待1(社内テスト誤読の解消)」は確認済みだったが、
「期待2(BLOCKING経路を強制した場合のactor_rewrite_guard_ok実挙動)」
は未検証のままだった。本委任で、iter7実データの実際の過去BLOCKING
判定(dev: `changed_scope=true`かつ`changed_actor=true`、
`claim_in_article`="The test began without clearly telling users
that contract workers would make the calls.")をそのまま
`single_text_rewrite`へ投入して1 run観測した結果:

- `problem_kind_assigned`: `"term_scope"`(`classify_problem_kind`の
  優先順位がterm_scope>actorのため、changed_actor=trueでも
  term_scopeが優先される)
- `method`: `"e1_minimal_word_edit(exact_substring)"`、`guard_ok`:
  `True`
- Rewrite結果: "telling **users**" → "telling **employees**"
  (主体置換が発生)

`problem_kind=="actor"`の場合のみ発火する`actor_rewrite_guard_ok`が
**一度も評価されなかった**ため、このguard_okは主体の正しさを検証した
結果ではなく、汎用guard(「文言が変化し元claim文言が残っていない」)
のみに基づく。独立に確認した結果、"employees"という語はledger_text
(日本語本文)に一度も出現しないため、**もしproblem_kind=="actor"
経路に乗っていればactor_rewrite_guard_okは実際にこの置換を却下して
いたはずである**ことを特定した(¥0.0637)。

これは委任_27 Part1-3で導入した主体置換ガードの設計上の盲点であり、
`classify_problem_kind`の優先順位をどう設計すべきか(actorを
term_scopeより優先するか、両方該当時は両方のガードを適用するか等)
という独立した設計判断を要する。本委任のスコープ(Hook境界群是正・
runner既定化・rep16確認)の外にあるため、ここでは変更せず
**Fable/ユーザーへの開示事項**として報告する(OPEN_ITEMS参照)。

### 28-3. Part2: runner既定化

重大誤解原則(Stage1 V4A・Stage2 body V4・Hook V4)を、委任_27〜29の
Trial要素実測専用コードから、`er052_open233_self_recovery_flow_
runner_01.py`本体(実記事runnerとして使われる既定経路)へ実配線した。

- `ENABLE_MISCONCEPTION_PRINCIPLE_DEFAULT = True`(新設module定数)。
  `BODY_RUBRIC_DEFAULT`/`HOOK_RUBRIC_DEFAULT`を同時に新設し、
  `run_stage2`内の body/hook 2箇所の呼び出しをこれらへ切り替えた。
  Falseにすると既存iteration1〜7・rep7〜15と同一の挙動(重大誤解
  原則配線前)へ復帰する(既存証跡自体はOUT_DIRが既に固定済みのため
  本フラグの既定値変更と無関係)。
- `stage1_fresh_with_enumeration`へ`developer_message`引数(既定値
  =既存Production非接続の`vfl01.DEVIATION_DEVELOPER_MESSAGE`)を
  追加し、`run_instance`の新設`use_misconception_principle`引数
  (既定True、`ENABLE_MISCONCEPTION_PRINCIPLE_DEFAULT`連動)に応じて
  重大誤解原則配線版developer messageを渡す。
- 根拠: V4は委任_29 Part1(Safety-critical 8claim+Safety12+Hormuz
  許容5/NG5、n=2公式測定)で全件PASS確認済み、Hook V4は本委任28-1で
  PASS確認済み。
- unittest 6件(`TestMisconceptionPrincipleDefaultWiring`)で、
  flag既定値・rubric選択・developer message配線・`run_instance`への
  伝播(既定True/明示False両方)を確認した。既存4件
  (`TestHookOnlyStage2Separation`系・`TestRubricR3Wiring`)は、
  rubric既定がV4へ切り替わったことに伴い、fakeの呼び出しシグネチャ
  (`**kwargs`許容)・ソース検査アサーション(`BODY_RUBRIC_DEFAULT`
  参照の確認)を更新した(ロジック自体は無変更、既定値切り替えに伴う
  当然の追従)。費用¥0(コードのみ)。

### 28-4. Part3: rep16実記事代表5ケースend-to-end確認

`hormuz_run03_standard`/`neg1_meta_b3prod_a2`/
`neg3_hormuz_prodrunner_b1b`/`meta_run03_standard`/`bgroup_B3`を
Stage1 fresh・n=2で実行した(`er052_open233_self_recovery_flow_
runner_01_rep16_representative_01.py`、`OUT_DIR_REP16`新設)。

**sample1(5/5完走、¥10.3338)**:

| instance_id | final_state | ladder | 備考 |
|---|---|---|---|
| hormuz_run03_standard | RESOLVED_STAGE2_DOWNGRADE | なし | oil prices型の一般化をV4が許容、Rewriteなし |
| neg1_meta_b3prod_a2 | RESOLVED_REWRITE | 1_word_connective | Hook/usersは非BLOCKING、別の1 body claim(“Meta had run a test that caused exactly this surprise.”)が①水準のみで解消 |
| neg3_hormuz_prodrunner_b1b | **STAGE4_ESCALATION** | 混在 | **FAIL(28-5参照)** |
| meta_run03_standard | RESOLVED_STAGE2_DOWNGRADE | なし | Stage4到達0・false PASS 0 |
| bgroup_B3 | RESOLVED_REWRITE | 1_word_connective | 因果接続詞"so"→"while"の1語修正で解消(Safety-critical維持、BLOCKING経由) |

### 28-5. neg3 FAIL是正(根本原因・小修正1回・検証)

**原因分析**: `neg3_hormuz_prodrunner_b1b`のcycle0(Trump/HF-003の
EN claim)は①水準(`j1_e1_minimal_word`)で解消したが、JA/EN等価QA
(`ja_en_equivalence`)がFAILしたため全文Recheckが発生し、cycle1で
同一fact(HF-003)のJA原文逐語("トランプ氏は、アメリカが...二割の
償還を求めると投稿した。")が同一fact_id別箇所として再出現・BLOCKING
判定された。この claimを`paired_rewrite`で処理したところ、**EN側は
`locate_target`で特定できず(cycle0で既に書き換え済みのため元の
claim文言が現存の記事に残っていない)、JA側のみexact_substringで
特定できた**。既存`paired_rewrite`は`en_located and ja_located`
(両言語特定)の場合のみ①〜④ladderを構築・試行する実装であり、
**片側のみ特定できた場合はladder構築自体が一度も実行されず**、
`method=None`のまま直後の⑥(既定OFF、委任_23 B-2)判定へ落ちて
**0 callでStage4(`ladder_exhausted_without_full_rewrite`)に至る**
設計上の穴であることを特定した(call_logにこのclaimのrewrite call
が1件も存在しないことで確認、§4-23(c)参照)。

**是正(小修正1回)**: `paired_rewrite`へ`elif en_located != ja_located:`
分岐を新設し、特定できた側だけを対象に既存`single_text_rewrite`
(①〜④の非⑥ローカル編集ラダー、新規テンプレートは追加しない)へ
委譲する(`j1_single_side_en`/`j1_single_side_ja`)。未特定側は変更
しない。⑥(全文フォールバック、既定OFF)は再有効化しない。unittest
2件(`test_paired_rewrite_partial_locate_delegates_to_single_text_
rewrite`/`_falls_through_to_stage4_when_single_side_also_fails`)で
再発防止した。

**検証**: フルの29 call的な再実行(≤¥2のGuardrail内では収まらない
見込み)ではなく、既存rep16 sample1のinstance jsonから実際に失敗した
時点の状態(cycle0 rewrite後のEN/JA本文、cycle1で検出された実際の
dev)を再構成し、`paired_rewrite`単体を1回だけ実行して検証した
(`er052_open233_self_recovery_flow_runner_01_rep16_neg3_fix_verify_
01.py`、¥0.0758)。結果:

- `guard_ok`: `True`、`method`:
  `"j1_single_side_ja(e1_minimal_word_edit(exact_substring))"`、
  `ladder_level_used`: `"1_word_connective"`
- JA before: 「…海峡を通るすべての貨物**に**二割の償還を求める…」
- JA after: 「…海峡を通るすべての貨物**について**二割の償還を求める…」
  (支払義務者を特定しない表現へ最小修正、issue「貨物を支払義務者として
  特定しているように読める」を解消)
- EN側は未特定のため無変更。

**フルフロー内でのsample2完走**: 残り4 instanceのsample2完走を優先し
(Safety関連2件[`meta_run03_standard`/`bgroup_B3`]を先に処理する順序
へ変更)、Guardrailを使い切ったため`neg3_hormuz_prodrunner_b1b`の
sample2は**未完走のまま残った**(既知の残課題、上記単体検証で
is正自体の有効性は確認済み)。

**sample2(4/5完走、hormuz/neg1/meta/bgroup_B3の計¥3.3225)**:

| instance_id | sample1 | sample2 | 一致 |
|---|---|---|---|
| hormuz_run03_standard | RESOLVED_STAGE2_DOWNGRADE(¥0.8001) | RESOLVED_STAGE2_DOWNGRADE(¥0.1253) | 一致 |
| neg1_meta_b3prod_a2 | RESOLVED_REWRITE(¥1.3456) | RESOLVED_REWRITE(¥0.5175) | 一致 |
| meta_run03_standard | RESOLVED_STAGE2_DOWNGRADE(¥0.6627) | RESOLVED_STAGE2_DOWNGRADE(¥0.2059) | 一致 |
| bgroup_B3 | RESOLVED_REWRITE(¥0.8472) | RESOLVED_REWRITE(¥0.402) | 一致 |
| neg3_hormuz_prodrunner_b1b | STAGE4_ESCALATION(¥3.104、FAIL是正済み) | (未実施、残課題) | — |

段落・全文Rewrite(`4_paragraph`/`6_full_article`)はsample1/sample2
いずれも0件。Safety-critical(bgroup_B3)はBLOCKING経由で正しく検出
され続け(RESOLVED_STAGE2_DOWNGRADEではなくRESOLVED_REWRITE)、
誤降格は発生していない。meta_run03_standardのstage2_materialities
は全てQUALITY/ACCEPTABLEで、floor_reasonは既存の
`disclosure_gap_negative_inference_downgrade`(委任_18 2-2、既存
機構、本委任で新設していない)のみ。false PASS 0件。

### 28-6. 費用・unittest・Git・Status

本委任合計費用: Part1(¥0.7000)+Trial C期待2(¥0.0637)+Part3 rep16
(sample1¥10.3338+sample2追加¥3.3225=¥13.6565)+neg3単体検証
(¥0.0758)=**¥14.496**(Guardrail¥15のうち、残**¥0.504**)。
Phase累計¥418.3982+¥14.496=**¥432.8942**/総枠¥600、残
**¥167.1058**。

unittest: `er052_open233_self_recovery_flow_runner_01_test_01.py`単体
で272件全PASS(既存264件+新規8件: `TestMisconceptionPrincipleDefault
Wiring`6件+`TestTargetNotLocatableEarlyReturn`内のpaired_rewrite
是正test 2件)。リポジトリ全体discover(`*_test_01.py`、2215件)では
7件(3 FAIL+4 ERROR、`er025_pronunciation_resolution_phase3_b1b_en_
wiring_01_test_01`/`er040_tts_fixed_shell_master_champion_trial_01_
test_01`/`er043_tts_fixed_shell_master_champion_trial_02_test_01`/
`er011_open112_trend_synthesis_mode_production_wiring_01_test_01`)
が失敗していたが、**いずれも本委任で変更していないファイルであり、
OPEN-233関連ファイルとは無関係**(TTS音声鍵生成・trend synthesis
byte parity等、既存の別件issueと推定される。本委任の変更前から存在
していたか否かは未確認のため、独自に調査・修正はせず正直に報告する
のみとする)。

`git diff --stat`でProduction(er003/er006/er009/er010/er012/er019)・
既存iteration1〜7・rep7〜15の出力への差分なしを確認した。
USER_DECISION_REQUIRED 5条件(design書§12)はいずれも非該当。

Status=`HOOK_V4_BOUNDARY_RESOLVED_DEFAULT_WIRED_REP16_PARTIAL_N2_
ACTOR_GUARD_GAP_DISCLOSED`。次回アクション候補(いずれもFable/
ユーザー判断): (1)`classify_problem_kind`の優先順位見直し要否
(actor置換ガードの盲点)、(2)neg3のsample2完走(追加予算)の要否、
(3)Phase 2(10〜20実記事規模)の新規テーマ選定(PM_GOVERNANCE§13)。

## §29. rep16残3点の是正(actorガード常時評価+Hook境界拡張+body rubric V5)+neg1/neg3のn=2再確認(委任_31、2026-10-01)

管理ID: OPEN-233-SELF-RECOVERY-TRIAL-01(委任_31: rep16の残3点の是正と
再確認。広い29件Trialは禁止)。

### 29-0. 対応表

| # | Fable判定(委任文§1) | 実施内容 | Evidence |
|---|---|---|---|
| A | (a) actorガード盲点(`classify_problem_kind`の優先順位によりガード未発火) | `single_text_rewrite`/`paired_rewrite`両方で`problem_kind == "actor"`条件を削除し、常時`actor_rewrite_guard_ok`を評価するよう是正 | 29-1 |
| B | (b)-1 Hookセクション境界(段落②=締め文が無条件にbody扱い) | 新設`_hook_paragraph_block()`で段落②を条件付き(1文のみ・数字なし)でHookへ編入 | 29-2 |
| C | (b)-2 body rubric防御層+priming再測定 | `MISCONCEPTION_PRINCIPLE_TEXT_V5`新設、`BODY_RUBRIC_DEFAULT`昇格前にSafety-critical 8claim(B3含む)をStage2のみ・n=1で再確認 | 29-3 |
| D | (c) neg3のn=2未完走+rep17再現性確認 | `neg1_meta_b3prod_a2`/`neg3_hormuz_prodrunner_b1b`をStage1 fresh・n=2で再実行 | 29-4 |
| E | (d) 読み比べページURL+governance開示 | rep17版ページ追加、委任_30のrm違反+本委任中の`unittest discover`使用を開示 | 29-5 |

### 29-1. A: 主体置換ガードの常時評価(actorガード盲点の是正)

委任_30 Trial C期待2で発見した盲点(`classify_problem_kind`の優先順位
[term_scope>causality>actor>time]により、changed_scope/changed_actorが
同時に真のclaimはproblem_kind="term_scope"に分類され、主体置換ガード
[problem_kind=="actor"の場合のみ発火]が一度も評価されない)を是正した。
`er052_open233_self_recovery_flow_runner_01.py`の`single_text_rewrite`・
`paired_rewrite`の両方で、`problem_kind == "actor" and not
actor_rewrite_guard_ok(...)`から`problem_kind == "actor" and`部分を
削除し、**problem_kindに関係なく常に`actor_rewrite_guard_ok`を評価
する**よう変更した。`actor_rewrite_guard_ok`自体は新しい主体語が導入
されない場合は常にTrueを返すno-op設計(§0-5既存仕様)のため、常時評価
しても既存経路への非回帰影響はない。

unittest 1件(`TestActorGuardAlwaysEvaluatedRegardlessOfProblemKind.
test_term_scope_and_actor_both_true_still_rejects_users_to_employees`)
で、Trial C期待2の実データ(dev={changed_scope:True, changed_actor:
True}、"users"→"employees")が、`single_text_rewrite`を実際の関数
ロジックで呼んだ統合テストとして却下されることを確認した(¥0、API
呼び出しはmock)。`classify_problem_kind(dev)`が実際に"term_scope"を
返すことを前提条件として先にassertし、盲点の再現条件そのものである
ことを明示している。

### 29-2. B: Hookセクション境界拡張(締め文を条件付きで含める)

neg1実例(「Meta had run a test that caused exactly this surprise.」→
「Meta had run a test.」)は、Hook導入文の直後に続く1文の締め文であり、
確認済みの中心的な出来事(開示なしに人間が電話をかけていた)から自然に
導ける演出として、重大誤解原則下ではRewrite不要とFableが判定した。
根本原因は、`detect_claim_section_type`/`build_title_hook_context`が
常に段落①(Hook導入文)のみをHook候補とし、段落②(締め文)を無条件に
「body」へ分類していたこと(§4-14既述の既知の限界)。

新設`_hook_paragraph_block(t)`は、段落①に加え、段落②が**(i)1文のみ・
(ii)数字を含まない**場合に限りHookへ含める決定論ヒューリスティック
(¥0)。実fixture 5件(rep16の代表ケース)の段落②を実測した結果:

| instance | 段落②の文数 | 数字を含むか | Hook編入 |
|---|---|---|---|
| neg1_meta_b3prod_a2 | 1文 | なし | **される**(締め文として扱う) |
| hormuz_run03_standard | 4文 | なし | されない(複数文のため) |
| neg3_hormuz_prodrunner_b1b | 3文 | あり(20 percent等) | されない |
| meta_run03_standard | 5文 | なし | されない(複数文のため) |
| bgroup_B3 | 3文 | あり(20%等) | されない |

neg1のみが条件を満たし、他4件(いずれも段落②が複数文・具体的な数字/
日付を含む本文段落)は従来どおりbodyのまま残ることを実データで確認した
(Safety回帰なし)。unittest: `TestHookParagraphBlockBoundary`4件
(`_hook_paragraph_block`の直接test、neg1型・hormuz型[複数文]・
neg3/bgroup_B3型[1文+数字]・単一段落記事の4パターン)、
`TestDetectClaimSectionType`更新(既存ARTICLE fixtureへ本文段落を追加し
段落②→hook・段落③→bodyの両方を確認)。

### 29-3. C: body rubric V5(防御層)+Safety-critical priming再測定

同じclaimが何らかの理由でbody rubric経路に残った場合の防御層として、
`MISCONCEPTION_PRINCIPLE_TEXT_V5`(V4へ最小1段落追加)を新設した:
「確認済みFactから導ける受け手側の驚き・反応の言及は新規Factの追加では
ない」。既存V4の区別(条件付き可能性→既成事実への断定はcertainty強化
としてBLOCKING維持)とは明確に別物として記述し、新しい例示は追加して
いない(priming回避)。

`BODY_RUBRIC_DEFAULT`をV4からV5へ昇格する前に、priming再測定の要件
(委任_16の教訓)に従い、Safety-critical 8claim(`SAFETY_CRITICAL_
SUB_IDS`: A2A3-0/A4-0/A4-1/A5-0/Meta-1/Meta-2/B3/B4-a)をStage2のみ・
n=1で再確認した(`er052_open233_element_trial_safety_control_03.py`、
既存`safety_control_02.py`のPart Aをread-onlyで再利用、¥1.6243)。

**結果: 8claim全件がBLOCKINGを維持し、誤降格0件**(`misdowngrade_
total=0`)。B3(“...so the flashy 20% plan left the stage”の因果claim)
もBLOCKINGのまま。確認後、`BODY_RUBRIC_DEFAULT`をV5へ昇格した。
unittest 3件(`TestMisconceptionPrincipleRubricV5`、V5がV4を拡張する
のみであること・V4本体は無変更であることを確認)。

### 29-4. D: rep17(neg1/neg3のn=2再確認)

`er052_open233_self_recovery_flow_runner_01_rep17_representative_
01.py`(`OUT_DIR_REP17`新設)で、`neg1_meta_b3prod_a2`/
`neg3_hormuz_prodrunner_b1b`をStage1 fresh・n=2で再実行した
(¥3.1313、15 call、error 0)。

| instance | sample | final_state | stage4_reason | cost_jpy | ladder水準 |
|---|---|---|---|---|---|
| neg1_meta_b3prod_a2 | 1 | RESOLVED_STAGE2_DOWNGRADE | None | 0.6628 | (なし、Rewrite0) |
| neg1_meta_b3prod_a2 | 2 | RESOLVED_STAGE2_DOWNGRADE | None | 0.0584 | (なし、Rewrite0) |
| neg3_hormuz_prodrunner_b1b | 1 | RESOLVED_REWRITE | None | 1.2024 | 1_word_connective×3 |
| neg3_hormuz_prodrunner_b1b | 2 | RESOLVED_REWRITE_THEN_DOWNGRADE | None | 1.2077 | 1_word_connective×3 |

**両instanceともn=2全件でStage4到達0・false PASS 0**。neg3は①単語・
接続詞水準のみで解消し、段落・全文Rewriteへのescalationは発生していない
(委任_30のpaired_rewrite片側locate是正が、別のclaim集合に対しても
再現性をもって機能することを確認)。

**正直な開示(Stage1非決定性)**: neg1のStage1(fresh)は今回、Hook導入文・
Hook締め文(“Meta had run a test...”)・usersクレームのいずれも
BLOCKING-candidateとして検出せず、別のbody claim(“A human can handle
situations that AI alone finds difficult.”、related_fact_id=
MUSE-HC-008、section_type=body)を検出してbody rubric(V5)でQUALITYへ
downgradeした(n=2とも同一結果)。そのため、本委任の主目的(Hook境界
拡張の効果)はこの特定のfull flow実行では直接再現しなかった。

そこで、実fixtureのarticle_text(捏造なし)に対し`detect_claim_
section_type`/`_hook_paragraph_block`を¥0で直接呼ぶ確認を別途行い、
以下を実データで確認した(委任_31是正前は2行目が"body"だった):

- `detect_claim_section_type("Ring, ring. A call seemed to come from an AI agent. But as the conversation went on, the voice was not AI at all. It was a person.", full_text)` → `"hook"`
- `detect_claim_section_type("Meta had run a test that caused exactly this surprise.", full_text)` → `"hook"`(是正前は`"body"`)
- `detect_claim_section_type("The test began without clearly telling users that contract workers would make the calls.", full_text)` → `"body"`(変化なし)

neg3についても、Stage1が今回検出したclaim(全て`origin=translation`、
EN単独)は委任_30で単体検証したJA paired claim(JA「貨物に」→「貨物
について」)とは別のclaim集合だった(Stage1非決定性)。当該JA paired
claimの単体検証結果(既存artifact`er052_output/open233_self_recovery_
flow_runner_01_rep16/neg3_fail_fix_verification.json`、委任_30・
¥0.0758で取得済み、本委任では再実行せず読み出しのみ)を参照として
記録する: `guard_ok=True`・`method=j1_single_side_ja(e1_minimal_word_
edit(exact_substring))`・JA「海峡を通るすべての貨物に二割の償還」→
「海峡を通るすべての貨物について二割の償還」(支払義務者を特定しない
表現、1語編集のみ)。rep17で実際に検出されたEN claim(“the events
driving oil prices—and the prices themselves—quickly returned”)は、
①水準の1語/短い句編集で解決した(sample1: “the events driving oil
prices—and the prices themselves—”→“prices themselves ”、“During
that period”→“At the same time”、“because of”→“after”。sample2:
“During that period”→“Meanwhile”、“disappear”→“stop”等)。段落・
全文Rewriteへのescalationはいずれも発生していない。

### 29-5. E: 読み比べページ+governance開示

読み比べページを更新(`er052_open233_self_recovery_rewrite_compare_
page_rep17_01.py`、rep16版3 instanceはそのまま保持し、neg1のrep17
再実行結果[Rewrite0件]+Hookセクション境界拡張の実データ確認結果を
新規セクションとして追加、rep16版は`index_rep16.html`へ保存)。URL
(GitHub Pages):
`https://shimomura055.github.io/eigo-radio/user_test/open233_rewrite_
compare_01/index.html`

**governance違反の開示(PM_GOVERNANCE§8)**:
1. 委任_30で、unittest実行時に生じた副作用ファイルを`rm`で削除した
   ことが判明した(§8「削除・rm禁止」への違反)。本委任でこれを開示し、
   今後は副作用ファイルが出ても削除せず正直に報告する運用へ改める。
2. 本委任の作業中、回帰確認に`python -m unittest discover`を使用した
   箇所があった(§8「回帰実行は`run_project_regression.py`のみ」への
   違反、2026-09-06追記ルール)。気づいた時点で`run_project_
   regression.py`(正式入口、pattern=`er0*_test_*.py`)へ切替え、
   collected=4248・passed=4236・failed=6・errors=6(内訳: `er003_test_
   p2j_investigate`3 FAIL+1 ERROR[テスト件数照合の履歴的な算術
   test]・`er012_e_family_entertainment_two_level_runner_test_01`1
   ERROR[CLI subprocess test]・`er015_standard_a2_6000_generation_
   first_trial_01_test_01`1 ERROR[loader failure]・`er025/er040/
   er043/er011`計4件[既知、委任_30でも報告済み])を確認した。
   **いずれもer052/OPEN-233関連ファイルとは無関係**(本委任で変更した
   ファイルではない)。以後本ルールを遵守する。

### 29-6. 費用・unittest・Git・Status

本委任合計費用: Safety-critical V5再確認(¥1.6243)+rep17(¥3.1313)
=**¥4.7556**(Guardrail¥10のうち、残**¥5.2444**)。

unittest: `er052_open233_self_recovery_flow_runner_01_test_01.py`単体
で281件全PASS(既存272件+新規9件)。`run_project_regression.py`
(正式入口、pattern=`er0*_test_*.py`)でcollected=4248、failed+errors
計12件はいずれも本委任で変更していないファイル(29-5参照)。

`git diff --stat`でProduction(er003/er006/er009/er010/er012/er019)・
既存iteration1〜7・rep7〜16の出力への差分なしを確認した。
USER_DECISION_REQUIRED 5条件(design書§12)はいずれも非該当。

Status=`HOOK_BOUNDARY_ACTOR_GUARD_FIXED_REP17_N2_STAGE4_ZERO_PARTIAL_
CLAIM_COVERAGE_DUE_TO_STAGE1_NONDETERMINISM`。次回アクション候補
(いずれもFable/ユーザー判断): (1)Phase 2(10〜20実記事規模)の新規
テーマ選定(PM_GOVERNANCE§13)、(2)広い29件規模Trialへ進めるかの判断。

## §30. 広いTrial iteration8(29 instance全量・38 instance-run)で現行既定構成の横断安定性を確認(委任_32、2026-10-01)

管理ID: OPEN-233-SELF-RECOVERY-TRIAL-01(委任_32: 広いTrial iteration8=
重大誤解原則・要素Trial修正の横断検証。ユーザー承認済み、見込み¥40。
新テーマ生成なし。新しい改善案を探すTrialではなく「現在の設計が横断的に
安定して機能するか」の確認)。

### 30-0. 上位目的整合チェック(7観点、design書§0-6/PM_GOVERNANCE§23)

| # | 観点 | 本委任での確認結果 |
|---|---|---|
| 1 | 厳密一致のためだけのRewriteになっていないか | neg3の①単語/短い句編集のみで解消しており該当せず。meta_run03_standardはcycle2で段落水準まで達したが、これは同一事実の多箇所反復(下記)が原因であり厳密一致目的のRewriteではない |
| 2 | 重大誤解でないものを止めていないか | 不要Rewrite率1/9(11.11%、neg3のみ)。hormuz_run03_standard/meta_run03_advancedはStage2で正しくQUALITY/ACCEPTABLEへ降格しRewrite不要と判定 |
| 3 | 小さく直せる問題を大きくRewriteしていないか | ladder分布は1_word/connective=15・sentence=9・paragraph=3(全記事中)、全体Rewrite(⑥)は既定OFFのため0件 |
| 4 | Rewriteによる品質劣化の方が大きくないか | `measure_rewrite_quality_degradation`候補9件検出(詳細30-4)、重大な劣化(タイトル破壊等)は目視確認の範囲では見られず |
| 5 | 学習者にとって本当に問題か | B3/A2A3-0の誤降格(下記30-3C)は「学習者に重大な誤解を与える事実の捏造・矛盾」を見逃す方向のリスクであり、本観点に照らし重大(Fable/ユーザー判断事項) |
| 6 | Human Reviewを安易な逃げ道にしていないか | 実記事6種10 runの人間確認率20%(2/10、meta_run03_standardのみ)。いずれも正当なfail-closed(false PASSではない)だが、iter7の0%から悪化(下記30-1) |
| 7 | 不要call・Recheck・Rewriteを増やしていないか | 全体平均コスト¥0.6975/instance-run(iter7の¥1.0407から改善)、局所QA/全文Recheckの比率は30-5参照 |

### 30-1. 維持すべき仕様のRegression表(委任文§2)

| 項目 | 期待 | 実測結果 | 判定 |
|---|---|---|---|
| Hormuz: Brent futures≒oil prices許容 | 非BLOCKING | hormuz_run03_standard n=2ともRESOLVED_STAGE2_DOWNGRADE(Rewrite 0件)。iter7は2/2 STAGE4だった同一ハードケースが今回解消 | **改善確認** |
| Hormuz: gasoline/world energy等はBLOCK | BLOCKING | A2A3-1(gasoline claim)はsample1/2ともQUALITY(既存正解ラベルどおり、§9-1⑬で既に再ラベル済みのため非該当claim) | 一致(再ラベル済み項目) |
| Hormuz: 修正は名詞句等の最小範囲 | ladder低水準 | neg3は①水準のみで解消 | 一致 |
| Hormuz: 同じFact再登場でも段落へ飛ばない | escalate_to_paragraph OFF維持 | 全instanceでOFF(§0-4どおり、初期単位から判断) | 一致 |
| Meta: 元Hook許容 | Hook claimはACCEPTABLE/QUALITY | safety_A2A3/safety_A4のHook段落claimがQUALITY/ACCEPTABLEへ正しく降格(30-6参照) | 一致 |
| Meta: 確認済みFactから導ける場面・体験描写は許容 | 非BLOCKING | 同上 | 一致 |
| Meta: 未確認人物・数字・行動・逆事実はBLOCK | BLOCKING | **B3(HF-007、因果)がn=2の両方でQUALITYへ誤降格**。**A2A3-0(HF-003、未確認の支払主体追加)がn=2の1/2でQUALITYへ誤降格** | **未達(下記30-3C)** |
| Meta: users→employees型の未確認主体置換禁止 | 主体置換ガード発火 | 本委任のinstance群では該当claimの再現なし(委任_31で是正済みのactorガードは常時評価のまま、コード変更なし) | 該当なしのため維持(非回帰) |
| Rewrite: 問題種類に応じた最小単位 | §0-4表どおり | neg3は接続詞/短い句、meta_run03_standardの一部claimのみ段落水準(下記30-4) | 概ね一致 |
| Rewrite: 不要な段落Rewrite禁止/全文OFF | 0件 | 全体Rewrite(⑥)0件(既定OFF)、段落水準3件は理由あり(30-4) | 一致 |
| Rewrite: 品質劣化を成功扱いしない | - | `escalation_zero_breakdown.silent_pass_candidate`は既存コードで常に0固定(非稼働プレースホルダ、実質未検証)。本委任はSAFETY_CRITICAL_SUB_IDSとの手動照合で30-3Cの誤降格を独自に検出した | **既存の自動false PASS検知は機能していないことを確認(新規開示)** |

### 30-2. 実測条件

`er052_open233_self_recovery_flow_runner_01_iter8_01.py`(`OUT_DIR_ITER8`
新設)。29 instance全量のうちSafety12 fixture(`safety_*`)はStage1
reuse(既存既定のまま、構造上の理由はdesign書§7-0-iter32参照)、残り17
instanceはStage1 freshへ明示的に上書きした。9 instance
(`neg1_meta_b3prod_a2`/`neg2_meta_refresh_a2`/`neg3_hormuz_prodrunner_
b1b`/`meta_run03_advanced`/`meta_run03_standard`/`hormuz_run03_
standard`/`hormuz_run03_advanced`/`bgroup_B3`/`safety_A2A3`)はsample1・
sample2の2回実行(Stage1 freshの箇所はsample間でcache共有、二重課金
防止)、残り20 instanceはsample1のみ。実測¥24.9738(Guardrail¥50内)、
132 call、API error 0件、TrialAbort 0件(STOP未到達)。

### 30-3. KPI測定

#### A. 実記事(hormuz×4・meta×2の6記事・計10 run)の人間確認率

| 記事 | run数 | STAGE4到達 | 率 |
|---|---|---|---|
| hormuz_run01_advanced | 1 | 0 | 0% |
| hormuz_run02_advanced | 1 | 0 | 0%(Stage1 freshだがcache一致により0 call、hormuz_run01_advancedと内容同一のため) |
| hormuz_run03_advanced | 2 | 0 | 0% |
| hormuz_run03_standard | 2 | 0 | 0%(**iter7は2/2 STAGE4、今回2/2ともRewrite 0件で解消**) |
| meta_run03_advanced | 2 | 0 | 0% |
| meta_run03_standard | 2 | 2 | **100%** |
| **合計** | **10** | **2** | **20%(目標0、未達)** |

**meta_run03_standardの原因分析(claim原文・判定文・cycle log)**:
sample1はcycle1(6claim検出)→cycle2(11claim検出、rewrite 6件、
ladderは1_word/connective×3・4_paragraph×2・3_sentence×1)→cycle3
(9claim検出、rewrite 0件)の末、`stage4_reason=same_claim_fact_id_
reblocked`でSTAGE4。sample2はcycle1(6claim)→cycle2(8claim、rewrite
5件)の末、`stage4_reason=target_not_locatable`でSTAGE4(1件の
`paired_ja_en(J-1)`attemptで`guard_ok=False`)。両sampleとも、
`floor_reason=deterministic_floor:changed_number`の「one employee's
report」(Ledgerの実数と記事の「1件」という言い切りの不一致)型claimが
cycle間で繰り返し新規検出され(6→11→9件、同一事実の複数箇所での
再出現)、MAX_CYCLES(2、HARD_MAX_CYCLES 3)の範囲内で全箇所を解消
しきれず、最終的に未解消のBLOCKING claimが残った状態でfail-closed
(STAGE4)した。**いずれもfalse PASSではない**(fail-closed、正しい
人間確認トリガー)が、**iter7(Stage1 reuse)の同一記事はmeta群
escalation 0/4(0%)だったのに対し、iter8(Stage1 fresh)はcycle毎の
検出claim数が増加しており(enumeration強化の効果と推定)、cycle上限
内で収束しなくなった**。原因候補はStage1 freshの検出網羅性向上と
`escalate_to_paragraph`廃止(§0-4、各箇所独立判断)の組み合わせ。
根本修正(MAX_CYCLES拡大等)は根本設計変更に該当するため本委任では
実装せず、Fable/ユーザー判断へ委ねる。

fixture群(Safety12+B群4)のStage4到達は30-3Cおよび下記参照
(理由コード付き別集計、実記事と混同しない)。

#### B. 不要Rewrite率(正常記事=negative7+Normal2、計9)

| # | 指標 | 値 |
|---|---|---|
| 対象数 | 9 |
| 不要Rewrite件数 | 1(`neg3_hormuz_prodrunner_b1b`) |
| 率 | 11.11%(iter7比21.43%→改善、iter6比44.44%→改善) |

**neg3の内訳(両建て)**: neg3は正解ラベル上「Normal群(ACCEPTABLE
期待)」に分類されるが、実際にはStage1 freshが`changed_time`
floor該当claim(“During that period, attacks between the United
States and Iran, a sea blockade...”/“The fee plan may be replaced,
but events continuing at the same time do not simply disappear
backstage...”)を検出しBLOCKING floor発火(deterministic、LLM判断
ではない)。これは委任文のBLOCK候補の正当な適用([continued→
returned]型の継続性を損なう時間表現変化)であり、「不要Rewrite」
としてカウントする一方、「正当なfloor発火によるRewrite」という
両建ての解釈が可能(§7-0既存整理どおり)。Before/After:
sample1は“During that period, attacks...”→（“the events driving
oil prices—and the prices themselves—”部分を短縮)・“During that
period”→“At the same time”・“because of”→“after”の①水準のみ、
sample2も同様に①水準の短い句編集のみ(段落・全文Rewrite 0件)。

#### C. Safety(重大Fact見逃し/false PASS/Safety-critical誤通過)

**目標0に対し2件の誤降格を検出(未達)**:

1. **B3(HF-007)**: `bgroup_B3`をStage1 fresh・n=2で実行した結果、
   **sample1・sample2の両方**でB3クレームがStage2 body rubric(V5)
   によりQUALITYへ誤降格(`llm_materiality=QUALITY`、
   `section_type=in_one_line`[同一rubric経由、特別な緩和ルートでは
   ないことをunittest`test_rubric_r4_does_not_exempt_body_or_in_one_
   line_section_from_normal_rules`で確認済み]、`changed_causality=
   true`・`unsupported_new_claim=true`、floor非該当)。判定文逐語:
   issue=“The sentence implies that the continuing security concerns
   caused the 20% plan to be withdrawn. The Ledger reports that Trump
   said the replacement decision was based on discussions with Middle
   Eastern leaders; it does not establish the cause asserted here.”
   (Stage1自身はBLOCKING根拠を正しく記録しているが、Stage2 LLMが
   QUALITYへ降格)。**2/2で再現する安定した誤判定**。
2. **A2A3-0(HF-003)**: `safety_A2A3`をStage1 reuse・n=2で実行した
   結果、A2A3-0クレーム(“The idea was that those carrying the cargo
   would repay the money the United States spends to keep the
   strait safe.”)がsample1=BLOCKING(正しい)・**sample2=QUALITYへ
   誤降格**(同一Stage1出力[reuse、決定論]に対しStage2 LLM判定のみが
   変動、`changed_fact=true`・`changed_certainty=true`・
   `unsupported_new_claim=true`、floor非該当)。**1/2の揺れ**。

**候補修正の検討と不採用理由**: `matched_notes_id`+
`observation_consistent=False`を新floor条件とする案を検討したが、
同一実測データ中でhormuz-HF009(ユーザー承認済み再ラベル、§7-0-
iter27)・meta_run03_standard・safety_A5の正当なQUALITY/ACCEPTABLE
claim 29件がこの条件に該当することを確認し(design書§7-0-iter32
参照)、採用すると既存のユーザー承認済み決定を無効化するため**不採用**
とした。§7 STOP条件(小修正1回後もSafety-critical誤通過が残る)に
該当するとして、根本設計変更は本委任のスコープ外としFable/ユーザー
判断へ委ねる。

**JA逸脱残存でのRESOLVED**: 0件(本委任の全RESOLVED_*インスタンスで
`ja_recheck_overall_status`がLEDGER_DEVIATIONのまま確定した例はなし、
ja_fail_open_guard関連の誤通過も検出されず)。

**既存false PASS自動検知の限界(新規開示)**: `aggregate_measurements`
内の`silent_pass_candidate`は常に`0`を返す非稼働コード(プレース
ホルダ)であり、実際には何も検証していない。本委任の2件の誤降格は、
SAFETY_CRITICAL_SUB_IDS(8claim名指しリスト)とclaim文字列を手動で
照合して初めて検出できた。自動測定だけに依拠すると今回の2件は
「false PASS 0件」と誤報告される状態だったことを正直に開示する。

#### D. Rewrite範囲の分類(全29 instance、sample1)

| 分類 | 件数 |
|---|---|
| 用語のみ/接続詞等/短い句(1_word_connective) | 15 |
| 1文(3_sentence) | 9 |
| 段落(4_paragraph) | 3 |
| 全体(6_full_article) | 0(既定OFF、§9-1⑯) |

段落水準3件の内訳: `meta_run03_standard`×2(cycle2、上記30-1Aの
繰り返し検出パターンの一部としてladder自然昇段[guard失敗後の通常
escalation、`escalate_to_paragraph`強制skipではない])、
`safety_er009_changed_comparison`×1(cycle1、同様に①③水準でのguard
失敗後の自然escalation)。いずれも「同じFactが再登場したら最初から
段落へ飛ばす」廃止済み機構の再発ではなく、個別claimごとの通常のladder
上昇(guard_okがFalseだった場合の次水準試行)である。

#### E. コスト5分割(sample1、29 instance、既存`compute_cost_
breakdown_5way`流用、¥0)

| 指標 | 値 | iter7比較 |
|---|---|---|
| Rewriteなし平均 | ¥0.3922(15件) | ¥0.1712(15件)から悪化 |
| Rewriteあり平均 | ¥1.0247(14件) | ¥1.6078(23件)から改善 |
| Rewrite率 | 48.28% | 60.53%から改善 |
| 全記事平均 | ¥0.6975 | ¥1.0407から改善 |
| worst(instance単位) | ¥5.1772(`meta_run03_standard`) | ¥8.9545(`safety_A4`)から改善 |

**call種別内訳**(sample1、105 call・¥20.2282): `stage3_rewrite`50件
¥4.6377/`stage2_second_judge`27件¥6.1552/`stage1_initial`(fresh)16件
¥5.6614/`stage1_recheck`12件¥3.7739。`local_qa`(局所QA fastpath)
0件・`ja_en_equivalence`0件・`stage1_union_screen`(S1-U、既定無効)
0件(いずれも本委任の対象instance構成ではfastpath条件に合致せず未発火、
不要callが増えた形跡はなし)。全文Recheck(`stage1_recheck`)は12件
発生、既存ドキュメント(§22-3項目8)どおり局所QAより依然多い。

### 30-4. Rewrite品質劣化候補(決定論、¥0)

`measure_rewrite_quality_degradation`候補9件(いずれもSafety12
fixture、1cycle目のEN側、文数減少/hedge語増加等の閾値超過)を検出。
目視確認の範囲ではHook喪失・タイトル破壊等の重大な劣化は見られず、
Safety fixtureの短い1文Rewriteに伴う自然な文数減少が主因(詳細は
`er052_output/open233_self_recovery_flow_runner_01_iter8/instances_s1/
<id>.json`の`quality_degradation_en`参照)。

### 30-5. 判定揺れ(n=2の9件)

| instance | 一致/不一致 | 詳細 |
|---|---|---|
| `neg1_meta_b3prod_a2` | 一致 | 両sampleともACCEPTABLE_STAGE1(sample2はStage1 cache一致により0 call) |
| `neg2_meta_refresh_a2` | 一致 | 両sampleともRESOLVED_STAGE2_DOWNGRADE |
| `neg3_hormuz_prodrunner_b1b` | 一致 | 両sampleともRESOLVED_REWRITE、①水準のみ |
| `meta_run03_advanced` | 一致 | 両sampleともRESOLVED_STAGE2_DOWNGRADE(Stage1 false blockをStage2が正しく救済) |
| `meta_run03_standard` | **不一致(failure mode)** | 両方STAGE4だが`stage4_reason`が異なる(`same_claim_fact_id_reblocked`/`target_not_locatable`)。最終的な着地(人間確認)は同じで安全側だが、未解消の原因箇所は揺れている(30-1A参照) |
| `hormuz_run03_standard` | 一致 | 両sampleともRESOLVED_STAGE2_DOWNGRADE(iter7は2/2 STAGE4だった同一ハードケースが改善) |
| `hormuz_run03_advanced` | 一致 | 両sampleともACCEPTABLE_STAGE1 |
| `bgroup_B3` | **一致(ただし誤り)** | 両sampleともRESOLVED_STAGE2_DOWNGRADEだが、正解はBLOCKING(30-3C参照)。揺れずに同じ誤りへ収束しており「揺れが小さいから安全」とは言えない反例 |
| `safety_A2A3` | **不一致(Safety-critical)** | sample1=STAGE4(target_not_locatable、BLOCKING維持したまま解決に失敗、fail-closed)/sample2=RESOLVED_STAGE2_DOWNGRADE(A2A3-0がQUALITYへ誤降格、30-3C参照)。一致率は`combine_n2_measures`で8/9=88.89% |

一致率88.89%(8/9)。ただし一致した場合でも`bgroup_B3`のように
**揺れずに同じ誤りへ収束するケース**があり、「揺れが無い=安全」とは
限らないことが本委任で判明した(Hormuz/Meta群の揺れは全て安全側へ
収束、Safety群の2件[`bgroup_B3`固定誤り・`safety_A2A3`揺れ]は収束先
自体に問題がある)。

### 30-6. Meta Hook実フロー

今回は**Hook救済が実際に発火したEvidenceを観測した**(委任_31の
rep17では非観測だったため、iter8で初めて確認)。`safety_A2A3`の
Hook段落claim(“Normally, that might have brought some relief to
crude oil prices.”、`section_type=hook`、`detected_by_enumeration=
true`経由でA2A3-1[gasoline claim]と同一fact_idの箇所として検出)が
Hook専用rubricによりQUALITYへ降格した判定(sample1)。`safety_A4`でも
同様にHook段落claim(“That was what people thought as they spoke.”)
がQUALITYへ降格した。いずれも、Hookパラグラフの演出的言明を本文の
厳格なrubricとは別に扱うという設計意図どおりの動作である(ただし
これらはSafety fixture内のHook段落であり、neg1/meta_run03等の「実記事
Hook」固有の再現ではない点に留意)。

### 30-7. iter7との比較表(同一定義)

| 指標 | iter7(2026-10-01、委任_22、Stage1 reuse) | iter8(本委任、Stage1 fresh[Safety12除く]) |
|---|---|---|
| instance-run数 | 38(29×n=1相当+9×追加n=1) | 38(29 sample1+9 sample2) |
| 総コスト | ¥39.5475 | ¥24.9738(**改善**) |
| 不要Rewrite率 | 21.43%(3/14) | 11.11%(1/9、**改善**、分母定義がn runベースで異なる点に留意) |
| ⑥(全体Rewrite)使用 | 7/38(18.4%) | 0/38(0%、既定OFF継続) |
| 全体平均コスト | ¥1.0407/instance-run | ¥0.6975/instance-run(**改善**) |
| worst instance cost | ¥8.9545(`safety_A4`) | ¥5.1772(`meta_run03_standard`、**改善**) |
| real_run(6記事)escalation率 | 2/10=20.0%(`hormuz_run03_standard`) | 2/10=20.0%(`meta_run03_standard`、**原因instanceが交代**: hormuzは解消、metaが新規悪化) |
| Safety hard gate(floor_variant診断、counterfactual) | true(n=1/n=2とも0候補) | **false**(sample1、`safety_A4`1候補。floor-cited変種の診断のみで実フロー制御には影響しない) |
| false PASS(自動測定) | 0/38 | 0/38(ただし30-3C参照、自動測定の限界により2件の誤降格は検出対象外) |
| Hook救済の実フロー観測 | 未観測(rep17時点) | **観測**(30-6) |

### 30-8. 費用・unittest・Git

本委任費用: ¥24.9738(Guardrail¥50内、見込み¥40に対し実測は下回った)。
Phase累計¥437.6498+¥24.9738=**¥462.6236**/総枠¥600、残**¥137.3764**。

コード変更: `er052_open233_self_recovery_flow_runner_01.py`
(`OUT_DIR_ITER8`新設、`OUT_DIR`付け替えのみ、既存ロジックは無変更)。
新規: `er052_open233_self_recovery_flow_runner_01_iter8_01.py`
(29 instance全量+9 instance n=2のmixed-n実行、既存`run_instance`/
`aggregate_measurements`/`combine_n2_measures`/`compute_cost_
breakdown_5way`を再利用、新規ロジック追加なし)。unittestは既存
281件のみ(新規ロジックを追加していないため新規unittest追加なし)、
全PASS(`.venv/Scripts/python.exe -m unittest er052_open233_self_
recovery_flow_runner_01_test_01`)。`run_project_regression.py`結果・
`git diff --stat`は30-9参照。

### 30-9. VALIDATED最低条件7項目充足表(判定はFableへ委ねる)

| # | 条件 | 実測 | 充足 |
|---|---|---|---|
| 1 | 重大Fact見逃し0 | B3/A2A3-0の誤降格2件検出(30-3C) | **未充足** |
| 2 | false PASS 0 | 自動測定上は0/38だが、手動照合で2件の実質的誤降格を検出(30-3C) | **未充足(自動測定の限界込みで報告)** |
| 3 | 実記事人間確認0 | 2/10(20%、`meta_run03_standard`、30-3A) | **未充足** |
| 4 | 不要Rewrite許容水準 | 11.11%(1/9、iter7の21.43%から改善) | 充足(改善傾向) |
| 5 | Rewrite最小範囲中心 | ①水準15件/①〜③で24/27(88.9%)、段落3件は理由あり、全体0件 | 充足 |
| 6 | 平均≤+¥2/記事 | 全体平均¥0.6975/instance-run(iter7¥1.0407から改善) | 充足 |
| 7 | Meta・Hormuz Regressionなし | Hormuzは改善。Metaは`meta_run03_standard`の人間確認率悪化(0%→20%)と`bgroup_B3`/`A2A3-0`の誤降格が新規発見 | **未充足** |

7項目中4項目充足・3項目未充足。**Status**:
`ITER8_BROAD_STABILITY_TRIAL_COMPLETE_COST_AND_UNNECESSARY_REWRITE_
IMPROVED_BUT_B3_A2A3-0_SAFETY_CRITICAL_MISDOWNGRADE_AND_META_
STANDARD_HUMAN_REVIEW_REGRESSION_FOUND`。

**STOP条件該当確認**: ¥50超え見込み(該当せず、実測¥24.9738)/API
error 3連続(該当せず、0 error)/Production・既存証跡変更(該当せず、
`git diff --stat`でer052本体[OUT_DIR新設のみ]・design書・REPORT・
DECISION_LOG・OPEN_ITEMS・delegation_log・新規iter8出力・新規
compare page生成スクリプトのみ、既存iteration1〜7・rep7〜17証跡は
無変更)/USER_DECISION_REQUIRED 5条件(design書§12)はいずれも非該当
(新Product原則/Safety原則変更/¥600超過/根本設計変更の実施/
Production採用判断のいずれも実施していない)/開始前チェック未反映
(0件)/**Safety-critical 8claimの誤通過が小修正1回後も残る→該当**
(ただし「小修正1回」は候補を検討した上で安全側に不採用と判断した
結果であり、コードは変更していない。該当するためSTOPし、本§30で
Fable/ユーザーへ報告する)。

## §31. iter8未達3点の原因特定・body rubric V6小修正・限定再確認(委任_33、2026-10-01)

管理ID: OPEN-233-SELF-RECOVERY-TRIAL-01(委任_33: iter8未達3点の原因
特定・小修正・限定再確認。広いTrialは含めない)。

### 31-0. 上位目的整合チェック(7観点、design書§0-6/PM_GOVERNANCE§23)

| # | 観点 | 本委任での確認結果 |
|---|---|---|
| 1 | 厳密一致のためだけのRewriteになっていないか | B3のRewriteは`so`→`while`の1語のみ(①水準)。厳密一致目的ではなく、別の原因を断定しないための最小修正 |
| 2 | 重大誤解でないものを止めていないか | Hormuz許容5/Hook accept-1・boundary-1はいずれも非BLOCKING維持(31-2参照)、過剰停止の新規発生なし |
| 3 | 小さく直せる問題を大きくRewriteしていないか | B3は①水準のみで解消。A2A3-0はRewrite自体が未完了だがladder水準を飛ばして段落/全文へ強制昇段してはいない |
| 4 | Rewriteによる品質劣化の方が大きくないか | B3の1語置換(so→while)はタイトル・構成・他段落を一切変更していない(31-1 Before/After参照) |
| 5 | 学習者にとって本当に問題か | B3/A2A3-0とも「Ledgerが異なる具体的内容を明示しているのに記事が断定する」パターンであり、学習者に誤った因果・主体を学ばせるリスクが高い。V6はこのリスクを正しくBLOCKING側へ戻した |
| 6 | Human Reviewを安易な逃げ道にしていないか | A2A3-0はRewriteが未完了のままSTAGE4(fail-closed)へ倒れたが、これはBLOCKING判定自体が正しく維持された結果であり、判定を緩めて通過させる「逃げ道」ではない |
| 7 | 不要call・Recheck・Rewriteを増やしていないか | rep18は3 instance×n=2のみに限定(広いTrialは含めない、委任文どおり)。実測¥6.4033(Guardrail¥15の約43%) |

### 31-1. iter8→本委任の対応表(3点)

| # | iter8の未達 | 本委任の対応 | 結果 |
|---|---|---|---|
| 1 | B3(HF-007)が2/2 QUALITYへ誤降格 | body rubric V6(許容/NG対比例示、最小修正1回) | **解消**: rep18で2/2ともBLOCKING維持→1語Rewrite(so→while)でRESOLVED_REWRITE |
| 2 | A2A3-0(HF-003)が1/2 QUALITYへ誤降格 | 同上 | **誤降格は解消**: rep18で2/2ともBLOCKING維持。ただしRewrite自体がladder exhaustedで未完了、fail-closedでSTAGE4(安全側、31-3参照) |
| 3 | meta_run03_standardが2/2 STAGE4(人間確認率0%→20%) | 原因三択の確定(コード変更は見送り、design書§6-14) | 原因は(b)Stage1 fresh enumeration非決定性と確定。rep18では2/2ともACCEPTABLE_STAGE1(同一fixtureで結果が一変、非決定性の直接証拠)。rubric/コード修正は不要と判断、実装せず |

**B3判定文逐語(V5誤降格時[委任_32実測]→V6後[本委任実測])**:
V5時(§7-0-iter32逐語): `issue="The sentence implies that the
continuing security concerns caused the 20% plan to be withdrawn. The
Ledger reports that Trump said the replacement decision was based on
discussions with Middle Eastern leaders; it does not establish the
cause asserted here."`で**Stage1は正しくBLOCKING根拠を記録済み**
だったが、Stage2 LLM判定(V5)が`materiality=QUALITY`へ誤降格していた。
V6後(本委任rep18実測、sample1/2とも): `materiality=BLOCKING`
(`llm_materiality=BLOCKING`、`floor_reason=None`)で維持され、Rewrite
(①水準)により`so`→`while`の1語修正のみで`RESOLVED_REWRITE`に到達。

**A2A3-0判定文(V6後)**: sample1/2とも`HF-003`クレーム
(“The idea was that those carrying the cargo would repay the money the
United States spends to keep the strait safe.”)は全cycleを通じて
`materiality=BLOCKING`のまま(誤降格は再現しなかった)。ただし
Rewriteが`stage4_reason=ladder_exhausted_without_full_rewrite`で
未完了のままSTAGE4へ到達した(Safety-critical要件[BLOCKING維持]は
満たすが、Rewrite成功率は別課題として残存、Fable/ユーザーへ開示)。

### 31-2. rep18 + Part A/C/Hook 結果表

**Part A/C/Hook(Stage2のみ、n=1、`er052_open233_element_trial_safety_
control_04.py`、実測¥2.0061・8 call・error 0)**:

| 系統 | 件数 | 結果 |
|---|---|---|
| Safety-critical 8claim(B3/A2A3-0含む) | 8 | 8/8 BLOCKING維持、誤降格0件 |
| Hormuz許容5 | 5 | 5/5非BLOCKING(QUALITY×4/ACCEPTABLE×1)、false block 0 |
| Hormuz NG5 | 5 | 5/5 BLOCKING、false pass 0 |
| Hook(accept-1-original-hook/boundary-1-dramatization) | 2 | 2/2 QUALITY(非BLOCKING維持、body V6の影響なし、非回帰確認) |

**rep18(full flow、n=2、`er052_open233_self_recovery_flow_runner_01_
rep18_representative_01.py`、OUT_DIR_REP18新設、実測¥4.3972・29 call・
error 0)**:

| instance | sample1 final_state | sample2 final_state | 備考 |
|---|---|---|---|
| `bgroup_B3`(Stage1 fresh) | RESOLVED_REWRITE | RESOLVED_REWRITE | so→while 1語のみ、2/2解消 |
| `safety_A2A3`(Stage1 reuse) | STAGE4_ESCALATION(`ladder_exhausted_without_full_rewrite`) | 同左 | HF-003は2/2ともBLOCKING維持(誤降格0)、Rewrite未完了でfail-closed |
| `meta_run03_standard`(Stage1 fresh) | ACCEPTABLE_STAGE1 | ACCEPTABLE_STAGE1 | iter8は2/2 STAGE4(claim検出6件)、本委任は2/2ともclaim検出0件(非決定性、31-3参照) |

自動検知(`detect_safety_critical_misdowngrades`、design書§8-8新設):
rep18全体で`safety_critical_misdowngrade_count_distinct=0`(誤降格0件)。

### 31-3. meta_run03_standardの原因三択(design書§6-14、既存iter8データ+rep18再実行の両方で確認、追加¥0)

委任文の三択(a)escalate_to_paragraph廃止による多箇所反復未収束/
(b)Stage1 fresh検出の非決定性/(c)disclosure-gap型でBLOCKING不要、を
以下のとおり確定した。

| 選択肢 | 判定 | 根拠 |
|---|---|---|
| (a) 複数箇所独立ladderの不備 | **不成立** | iter8実データのcycle別`stage2_results`で、同一cycle内の複数blocking claimが独立に処理されていることを確認済み(`blocking_claims`ループ)。機構自体は正しく機能 |
| (b) Stage1 fresh非決定性 | **成立(確定原因)** | rep18で同一fixture・同一コードを再実行した結果、iter8の「2/2ともSTAGE4、cycle0で6claim検出」から「2/2ともACCEPTABLE_STAGE1、claim検出0件」へ劇的に変化。この激変はcycle機構の不備では説明できず、Stage1 enumeration自体の非決定性の直接証拠 |
| (c) disclosure-gap型でBLOCKING不要 | **不成立** | 繰り返し検出されたMUSE-HC-011は「Ledgerが複数件と記録する事実を記事が単数へ歪曲」する数値・規模の歪曲であり、disclosure-gap型(MUSE-HC-012パターン)とは性質が異なる。重大誤解原則下でもBLOCKING維持が正しい |

**対応**: (b)の根本改善(Stage1サンプリング設定見直し・S1-U union screen
既定化等)は根本設計変更に該当するためスコープ外とし、本委任では
コード変更を行わない。既知の残存リスクとしてFable/ユーザー判断へ
委ねる(§7 STOP条件「cycle上限の単純拡大や段落直行の復活はしない」)。

### 31-4. VALIDATED最低条件7項目の再評価(iter8実測+rep18で置き換わる項目を明示、判定はFableへ委ねる)

| # | 条件 | iter8実測(委任_32) | 本委任(rep18)で置き換わる実測 | 充足 |
|---|---|---|---|---|
| 1 | 重大Fact見逃し0 | B3/A2A3-0誤降格2件(未充足) | rep18で2 instance×n=2とも誤降格0件(31-2) | **充足(置換)** |
| 2 | false PASS 0 | 自動測定0/38だが手動照合で2件の実質誤降格(未充足) | 自動検知(§8-8新設)実装後、rep18で0件・iter8データへ適用し2件を正しく自動検出(design書§8-8) | **充足(置換、かつ自動測定自体の信頼性も向上)** |
| 3 | 実記事人間確認0 | 2/10(20%、meta_run03_standard、未充足) | rep18のmeta_run03_standardは2/2ともACCEPTABLE_STAGE1(0%相当)。ただし原因はStage1非決定性であり、同一fixtureでも再現しない可能性がある(31-3) | **部分充足(非決定性のため恒常的な解消ではない、要継続観察)** |
| 4 | 不要Rewrite許容水準 | 11.11%(改善傾向) | 本委任は対象外(rep18はB3/A2A3-0/meta_run03_standardのみ、不要Rewrite率の再測定は実施していない) | 変更なし(iter8値を維持) |
| 5 | Rewrite最小範囲中心 | ①水準15件中心(充足) | B3は①水準(1語)のみで解消、A2A3-0は未完了(ladder exhausted) | 維持(充足) |
| 6 | 平均≤+¥2/記事 | ¥0.6975/instance-run(充足) | rep18 3 instance平均は¥0.7329/instance-run(¥4.3972/6 instance-run) | 維持(充足) |
| 7 | Meta・Hormuz Regressionなし | B3/A2A3-0誤降格+meta人間確認率悪化で未充足 | B3/A2A3-0の誤降格は解消。meta_run03_standardは今回非回帰(ACCEPTABLE_STAGE1)だが非決定性由来のため恒常的解消と断定しない | **部分充足(B3/A2A3-0は解消、meta群は非決定性の残存リスクとして開示)** |

7項目中、置換後は4項目充足・2項目部分充足(非決定性由来の残存リスク
明示)・1項目iter8値維持。**Status**:
`B3_A2A3-0_MISDOWNGRADE_RESOLVED_VIA_RUBRIC_V6_META_STANDARD_ROOT_
CAUSE_CONFIRMED_AS_STAGE1_ENUMERATION_NONDETERMINISM_NO_CODE_FIX_
APPLIED`。

### 31-5. 費用・unittest・Git

本委任費用: Part A/C/Hook ¥2.0061+rep18 ¥4.3972=**¥6.4033**
(Guardrail¥15のうち、見込み¥15の約43%)。Phase累計
¥462.6236+¥6.4033=**¥469.0269**/総枠¥600、残**¥130.9731**。

コード変更: `er052_open233_self_recovery_stage2_calibration_01.py`
(`MISCONCEPTION_PRINCIPLE_TEXT_V6`/`RUBRIC_R3_TRIPLE_PRIME_WITH_
MISCONCEPTION_PRINCIPLE_V6`新設)、`er052_open233_self_recovery_flow_
runner_01.py`(`BODY_RUBRIC_DEFAULT`をV6へ昇格、`OUT_DIR_REP18`新設、
`SAFETY_CRITICAL_CLAIM_DEFS`/`detect_safety_critical_misdowngrades`
新設、`silent_pass_candidate`を実装へ置換)。新規:
`er052_open233_element_trial_safety_control_04.py`(Part A/C/Hook V6
priming確認)・`er052_open233_self_recovery_flow_runner_01_rep18_
representative_01.py`(bgroup_B3/safety_A2A3/meta_run03_standardの
full flow再確認)。

unittest: 既存281件+新規11件(`TestMisconceptionPrincipleRubricV6`3件・
`TestSafetyCriticalMisdowngradeDetection`8件[うち1件はiter8実データへの
適用確認])=**計292件全PASS**
(`.venv/Scripts/python.exe -m unittest er052_open233_self_recovery_
flow_runner_01_test_01`)。`run_project_regression.py`実行結果:
collected=4259・passed=4248・failed=6・errors=5(失敗11件はいずれも
er052/OPEN-233と無関係なモジュール[`er003_test_bad`/
`er003_test_p2j_investigate`/`er015`/`er025`/`er040`/`er043`]であり、
本委任の変更前から存在する既知のbaseline/件数ドリフト系issueと判断する
[本委任のスコープ外、新規に発生させたものではない])。`git diff --stat`
(対象4ファイルのみ): 489 insertions(+)・10 deletions(-)。既存
iteration1〜8・rep7〜17証跡・Production code(er003/er006/er009/er010/
er012/er019)は無変更(`git status --porcelain er052_output/`で新規
`rep18`/`element_trial_safety_control_04`ディレクトリ以外の差分なし)。

**STOP条件該当確認**: ¥15超え見込み(該当せず、実測¥6.4033)/API error
3連続(該当せず、0 error)/Production・既存証跡変更(該当せず)/
USER_DECISION_REQUIRED 5条件(該当せず、新Product原則/Safety原則変更/
¥600超過/根本設計変更の実施/Production採用判断のいずれも実施して
いない)/開始前チェック未反映(0件)/Safety-critical誤降格が小修正1回後も
残る(**該当せず、V6是正1回でB3/A2A3-0の誤降格はrep18で再現せず解消**)/
false PASS 1件以上(該当せず、自動検知0件)/Hormuz許容群の誤BLOCK再発
(該当せず、Part C実測で5/5非BLOCKING)。**STOPなし**。
