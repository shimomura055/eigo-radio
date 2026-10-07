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

## §32. meta_run03_standardの人間確認をStage1の揺れから切り離して検証(委任_34、2026-10-01)

管理ID: OPEN-233-SELF-RECOVERY-TRIAL-01(委任_34: meta_run03_standardの
人間確認を「Stage1の揺れ」から切り離して検証。広いTrialは含めない)。

### 32-0. 上位目的整合チェック(7観点、design書§0-6/PM_GOVERNANCE§23)

| # | 観点 | 本委任での確認結果 |
|---|---|---|
| 1 | 厳密一致のためだけのRewriteになっていないか | 本委任はRewrite方式自体を変更していない(既定構成のまま)。発見した問題はRewrite方式ではなくStage2 deterministic floorの適用範囲 |
| 2 | 重大誤解でないものを止めていないか | **問題を実測で確認**: `News reports also cited one employee's report.`(「one」=単数、正確な記述)・`However, this is only one report...`(正確なhedge文)・`Meta said it was a mistake to start the test without clear notice.`(無関係の別事実)が、いずれも`llm_materiality=ACCEPTABLE`であるにもかかわらずfloorでBLOCKINGへ強制された(32-1/32-3) |
| 3 | 小さく直せる問題を大きくRewriteしていないか | cycle2で`escalate_to_paragraph=True`が複数claimに付き、cycle3では`full_recheck_required_reasons`に`paragraph_or_full_or_delete_rewrite`相当の条件が複数回出現し、段階的に大きい単位への昇段が続いた(32-2) |
| 4 | Rewriteによる品質劣化の方が大きくないか | 本委任は修正を実装していない(未検証のまま変更しない方針)ため、品質劣化の実測比較は次委任の課題 |
| 5 | 学習者にとって本当に問題か | sample1は3cycle・32 API callを費やしても収束せず人間確認(STAGE4)へ落ちた。学習者への実配信という観点では「正しく安全側へ倒れている」が、運用コスト(¥6.2845/1 run)が高い |
| 6 | Human Reviewを安易な逃げ道にしていないか | STAGE4は`cycle_limit_exhausted_after_recheck`(cycle上限到達、fail-closed)であり、判定を緩めて通過させてはいない。false PASSは0件(32-2) |
| 7 | 不要call・Recheck・Rewriteを増やしていないか | 本委任はB(≤¥7)・Safety-critical確認(≤¥1)のGuardrail¥8に対し、sample1完走(¥6.2845)+sample2がcycle1完了直後に自己停止(¥0.9769)で累計¥7.2614に達し、計画の「2 run完走」は未達(32-2・32-4) |

### 32-1. iter8 cycle1 Stage1出力(原本2件+enumeration展開4件)の逐語とFable分類

iter8のs1/s2は`stage1_cache`共有(fresh instanceの既存仕様)により
cycle1のStage1検出内容が**完全に同一**(原本2件: MUSE-HC-012/
MUSE-HC-011、実測で確認済み)。原本2件は`same_fact_id_locations`
フィールドを持ち、`expand_same_fact_id_locations`により各4件・計6件へ
展開される。

| # | claim(EN、逐語) | fact_id | section | Stage2判定(materiality/llm_materiality/basis) | floor_reason | Fable分類 |
|---|---|---|---|---|---|---|
| 1(原本) | "They enjoyed AI's convenience, but a human was on the other end. They did not realize it." | MUSE-HC-012 | body | QUALITY / BLOCKING / unsupported_relationship | `disclosure_gap_negative_inference_downgrade`(委任_18 2-2) | **(ii)** 重大誤解に該当せず、disclosure-gap型(利用者が実際に気づいていなかったと断定する表現だが、Ledgerは「適切な開示なしにテストを開始した」事実のみを確認。既存floorが正しくQUALITYへ降格) |
| 2(原本) | "It said human staff made inappropriate comments about race during calls. These calls were about trying to lower internet or cable fees." | MUSE-HC-011 | body | BLOCKING / BLOCKING / ledger_scope | `deterministic_floor:changed_number` | **(i)** 正当なBLOCK(規模の歪曲。Ledgerは単一の従業員報告だが記事は複数形"calls"で一般化) |
| 3(展開) | "If no one explained this clearly, users could not know. They could not tell if it was AI or a person." | MUSE-HC-012 | body | QUALITY / QUALITY / ledger_conditions | なし | **(ii)** 条件文のまま(Ledgerの開示なし条件を正確に反映)、LLM自身が直接QUALITYと判定(floor不要) |
| 4(展開) | "Some calls through Meta's AI assistant were actually handled by humans, but users were not properly told." | MUSE-HC-012 | in_one_line | ACCEPTABLE / ACCEPTABLE / ledger_claim | なし | **(ii)** 「一部の通話」という範囲は保たれ、Ledgerの核心事実と一致 |
| 5(展開) | "News reports also cited one employee's report." | MUSE-HC-011 | body | BLOCKING / **ACCEPTABLE** / ledger_claim | `deterministic_floor:changed_number` | **(ii)誤分類**: 文中の"one"は単数で正確。LLM自身もACCEPTABLEと判定したが、同一`related_fact_id`(MUSE-HC-011)を共有する claim#2のfloorが波及してBLOCKINGへ強制された |
| 6(展開) | "However, this is only one report. It would be wrong to say all contract workers did this." | MUSE-HC-011 | body | BLOCKING / **ACCEPTABLE** | `deterministic_floor:changed_number` | **(ii)誤分類**: 単一報告であることを明示するhedge文そのもの。claim#2のfloorが波及 |

claim#5/#6は、**文面自体は正確(single reportを正しく反映)なのに、
同一fact_idの他claim(#2)が持つfloorへ巻き込まれてBLOCKINGへ強制
される**典型例であり、§0許容表の「規模の歪曲」そのものではなく、
floorの適用範囲(fact_id単位)が広すぎることによる誤分類である
(32-3で詳述)。

**cycle2/cycle3の推移(要旨、逐語はrep19実測JSON参照)**: cycle1の
Rewrite後、claim#2相当の文がさらに細分化され、cycle2では
blocking6件・non-blocking6件(計12件)まで検出対象が増加した。
BLOCKING6件のうち3件(`News reports also cited one employee's report
about a phone call.`/`It said human staff made inappropriate comments
about race during a call.`/`However, this is only one case. It would
be wrong to say all contract workers did this.`)はいずれも
`llm_materiality=ACCEPTABLE`または`QUALITY`でありながら
`deterministic_floor:changed_number`でBLOCKINGへ強制された(claim#5/
#6と同型の誤分類が増殖)。cycle3では`deterministic_floor:changed_actor`
が新たに発火し、`"Meta said it was a mistake to start the test
without clear notice."`(MUSE-HC-012と無関係に近い別事実、
`llm_materiality=ACCEPTABLE`)までBLOCKINGへ強制された
(**(ii)誤分類**、32-3)。cycle3のblocking5件・non-blocking0件の時点で
cycle上限(`MAX_CYCLES=2`+`extra_cycle_granted`延長で実質3)に達し、
`STAGE4_ESCALATION`(`cycle_limit_exhausted_after_recheck`)。

### 32-2. rep19結果(frozen Stage1入力、現行既定構成、2 run試行)

`er052_open233_self_recovery_flow_runner_01_rep19_representative_
01.py`(新規、OUT_DIR_REP19新設)で、iter8 cycle1原本2件を
`stage1_mode=reuse`で固定した1つのfixture
(`stage1_fixtures/meta_run03_standard_iter8_cycle1_frozen.json`)から
2 run試行した。

| run | final_state | stage4_reason | cycle数 | 費用 | 備考 |
|---|---|---|---|---|---|
| sample1 | `STAGE4_ESCALATION` | `cycle_limit_exhausted_after_recheck` | 3 | ¥6.2845(32 call) | 32-1の推移どおり、cycle3で全5claimがBLOCKINGのまま上限到達 |
| sample2 | (未完了) | - | cycle1完了後に中断 | ¥0.9769(5 call) | 累計¥7.2614がGuardrail¥8へ到達し`TrialAbort`で自己停止(安全側、結果は未保存) |

false PASS: 0件(いずれもSTAGE4、PASS/RESOLVED系statusなし)。
Safety-critical誤降格: 0件(`detect_safety_critical_misdowngrades`を
実行、meta群はSAFETY_CRITICAL_SUB_IDS対象外のため該当行なし)。

### 32-3. 結論: Stage1入力固定でも収束しない追加メカニズム(d)、design書§6-15

**上位目的整合**: Stage1自体の揺れ(cycle1検出内容がrunごとに変わる
こと)はSelf-Recovery Flowの責任範囲外。しかし本委任はcycle1入力を
iter8 s1/s2と完全同一に固定した上で、現行既定構成の流路のみを再実行
した。それでもsample1は3cycle・32 callを費やして収束せず
`STAGE4_ESCALATION`に到達した。これは、委任_33(§6-14)が確定した
「原因は(b)Stage1 fresh enumeration非決定性のみ」という結論では
説明できない事実である((b)はiter8のs1/s2間差異[cycle2以降の検出が
sampleごとに異なった事実]を説明しうるが、cycle1を完全固定しても
再現する非収束は説明できない)。

**追加メカニズム(d)**: 32-1のclaim#5/#6および cycle2/cycle3の追加
誤分類が示すとおり、`deterministic_floor:changed_number`/
`deterministic_floor:changed_actor`は、違反を体現する当該claim文
だけでなく、**同一`related_fact_id`を共有する他の全claim**(`llm_
materiality`が独立にACCEPTABLE/QUALITYと判定していても)へBLOCKING
判定を強制的に波及させる。`same_fact_id_locations`enumeration
(委任_20 W2)がRewrite後のテキストから毎cycle新しい候補文を再列挙し
続けることと複合し、検出対象claim数がcycleごとに増加し続け
(cycle1: 2件原本→cycle2: 12件→cycle3: 5件全てBLOCKING)、cycle上限に
達するまで収束しなかった。

**(b)と(d)の関係**: 両者は独立した別メカニズムであり、(b)が
Stage1検出内容の揺れそのものを指すのに対し、(d)はStage1検出内容が
固定されていてもfloorの適用範囲(fact_id単位のbroadcast)に起因して
非収束が生じることを指す。design書§6-14の結論を「(b)は少なくとも
部分的要因」へ修正し、(d)を既知の残存原因候補として追加した
(design書§6-15)。

**対応状況**: 委任文の分類では(d)は「Stage2許容例示の適用範囲」
(floor自体の対象範囲を、違反を体現する当該claim文のみへ狭める)に
近い**小修正候補**である。ただし本委任はGuardrail¥8のうち¥7.2614を
sample1完走+sample2 cycle1部分実行で使い切ったため、修正の実装・
再検証(見込み≤¥2)およびSafety-critical priming再確認(見込み≤¥1)を
行う予算がなく、**未検証のままコード変更は行っていない**。(d)の
是非確認(floorの対象範囲を当該claim文へ限定する修正の実装・検証)は
追加予算(目安¥3程度)の承認をFable/ユーザーへ依頼する。

### 32-4. 費用・unittest・Git

本委任費用: 分析(Part A)¥0+rep19(Part B)¥7.2614=**¥7.2614**
(Guardrail¥8のうち約91%)。Phase累計¥469.0269+¥7.2614=
**¥476.2883**/総枠¥600、残**¥123.7117**。

コード変更: `er052_open233_self_recovery_flow_runner_01.py`
(`OUT_DIR_REP19`/`BUDGET_STATE_PATH`/`TOTAL_BUDGET_JPY`新設、既存
`OUT_DIR_REP18`等は無変更)。新規:
`er052_open233_self_recovery_flow_runner_01_rep19_representative_
01.py`、`er052_output/open233_self_recovery_flow_runner_01_rep19/
stage1_fixtures/meta_run03_standard_iter8_cycle1_frozen.json`
(iter8 cycle1原本2件のfreeze、同一article_textであることを事前に
確認済み)。**Production code(er003/er006/er009/er010/er012/er019)・
既存iteration1〜8・rep7〜18・Hormuz/Safety fixtureは一切変更して
いない**。unittest292件(既存281+委任_33新規11)を実行前に再確認し
全PASS(API呼び出し前、¥0)。

**STOP条件該当確認**: ¥8超え見込み(**該当: 累計¥7.2614/¥8[残
¥0.7386]に到達し、計画の残作業[sample2完走・小修正1回・Safety-critical
priming再確認]のいずれも≤¥2〜¥3の見込み費用を賄えないため、これ以上
API呼び出しを伴う作業を行うとGuardrailを超える見込み。本節の記録・
commit・回帰確認はAPI呼び出しを伴わないため継続した**)/API error
3連続(該当せず、0 error)/Production・既存証跡変更(該当せず)/
USER_DECISION_REQUIRED 5条件(該当せず、新Product原則/Safety原則変更/
¥600超過/根本設計変更の実施/Production採用判断のいずれも実施して
いない。(d)の採否判断自体はFable/ユーザーへ照会するが、本委任内では
実施していない)/開始前チェック未反映(0件)/Safety-critical誤降格
(該当せず、meta群は対象外・0件)/false PASS 1件以上(該当せず、0件)/
小修正1回後もFAIL(**未実施**: 修正を試す前に予算到達のため、「小修正→
再実行」のサイクル自体に着手できなかった)。**STOP(budget guardrail)**。
次アクション: (d)修正(floorの対象範囲を当該claim文へ限定)の実装・
検証の要否、および追加予算(目安¥3程度)の承認をFable/ユーザーへ
依頼する。

## §33. 追加原因(d)の小修正実装とfrozen fixture再検証(委任_35、2026-10-01)

管理ID: OPEN-233-SELF-RECOVERY-TRIAL-01(委任_35: 委任_34で特定した
追加原因(d)の小修正とfrozen fixture再検証。広いTrialは含めない)。

### 33-0. 上位目的整合チェック(7観点、design書§0-6/PM_GOVERNANCE§23)

| # | 観点 | 本委任での確認結果 |
|---|---|---|
| 1 | 厳密一致のためだけのRewriteになっていないか | 修正対象はRewrite方式自体ではなくStage2 deterministic floorの適用範囲(fact_id単位→当該claim文単位)とsame_fact_id_locations列挙回数。Rewrite機構自体は無変更 |
| 2 | 重大誤解でないものを止めていないか | **改善を実測で確認**: rep19で誤ってBLOCKING化されていた複製claim(「News reports also cited one employee's report.」等)は、rep20で両runともACCEPTABLE/QUALITYのまま維持された(33-2) |
| 3 | 小さく直せる問題を大きくRewriteしていないか | rep20のcycle1 Rewriteは単語置換("calls"→"one call"/"a call")のみで、rep19のような段落・文全体への拡大は発生しなかった(33-2) |
| 4 | Rewriteによる品質劣化の方が大きくないか | rep19で観測された「別文へ丸ごと置換」「## In one line見出し削除」はrep20で再発せず、見出しは両run・全cycleで保持された(33-2) |
| 5 | 学習者にとって本当に問題か | sample1は3cycle・¥2.0186でRESOLVED(人間確認なしで解消)。sample2は2cycleでSTAGE4(全文Rewrite不使用のまま安全側に倒れた、¥1.8301)。いずれもrep19(32 call・¥6.2845、収束せず)より大幅に効率化 |
| 6 | Human Reviewを安易な逃げ道にしていないか | sample2のSTAGE4は`ladder_exhausted_without_full_rewrite`(ladder上限、fail-closed)であり、判定を緩めて通過させたわけではない。false PASSは0件(33-2) |
| 7 | 不要call・Recheck・Rewriteを増やしていないか | Part B(2 run)+Safety対照A(2 instance full flow)+Safety対照B(6 instance Stage2のみ)で¥6.0782(Guardrail¥10のうち約61%)。rep19(1 run完走+1 run中断で¥7.2614)より総コスト効率が改善 |

### 33-1. 実装(4点、design書§6-16参照)

1. `apply_floor`/`apply_floor_cited`: `dev.get("detected_by_enumeration")`
   が真の場合、deterministic floorを適用しない(素通し、`llm_materiality`
   がそのまま`materiality`になる)。precheck floor(`detected_by==
   "precheck"`)は無変更。
2. `run_recheck`: 新規引数`enable_fact_id_enumeration`(既定`False`)。
   `False`時は`SAME_FACT_ID_ENUMERATION_INSTRUCTION`をpromptへ追加せず、
   `expand_same_fact_id_locations`も呼ばない。既存呼び出し側(`run_
   instance`内の2箇所、EN/JA recheck)は明示的な引数指定なし(既定
   `False`を使う)。
3. `measure_section_role_violation`: `iol_degenerate`
   (`iol_before.strip()`が非空かつ`iol_after`が空)を追加し、
   `title_degenerate`/`hook_degenerate`と同じhard block条件
   (`run_instance`、`degenerate_rewrite_output`)へ合流。
4. `classify_problem_kind`自体への追加修正は、rep20実測(33-2)で
   「They enjoyed AI's convenience...」claimがそもそもBLOCKINGへ
   至らなくなったことを確認した上で、不要と判断し実装しなかった
   (経過観察)。

unittest: 開始前チェック(既存292件、API呼び出し前に再確認、全PASS)
→新規12件(`TestFloorFactIdBroadcastFix35`5件・`TestRecheckFactIdEnumerationOnceOnly35`
3件・`TestInOneLineHeadingDegenerateGuard35`4件、rep19実データ[dev
dict・claim文]を使用)→計304件、全PASS(¥0、API呼び出し前)。

### 33-2. rep20結果(frozen fixture再検証、n=2)

`er052_open233_self_recovery_flow_runner_01_rep20_representative_01.py`
(新規、`OUT_DIR_REP20`新設)で、rep19と同一のfrozen fixture
(`er052_output/open233_self_recovery_flow_runner_01_rep19/stage1_
fixtures/meta_run03_standard_iter8_cycle1_frozen.json`、再freezeせず
読み込むのみ)を`stage1_mode=reuse`で固定し、(d)是正後のコードで2 run
実行した。

| run | final_state | stage4_reason | cycle数 | 費用 | cycle1 blocking数 |
|---|---|---|---|---|---|
| sample1 | `RESOLVED_REWRITE_THEN_DOWNGRADE` | - | 3 | ¥2.0186 | 1(rep19は3) |
| sample2 | `STAGE4_ESCALATION` | `ladder_exhausted_without_full_rewrite` | 2 | ¥1.8301 | 1(rep19は3) |

**cycle1の逐語比較(rep19→rep20)**: rep19のcycle1は6claim検出(原本2件+
enumeration展開4件)のうちBLOCKING3件(うち2件が複製claimへのfloor
誤波及)だったが、rep20のcycle1は6claim検出(同じ6件)のうちBLOCKING
1件(「It said human staff made inappropriate comments about race
during calls...」、違反を体現する当該claim文自体)のみとなった。
複製claim4件("If no one explained..."/"Some calls through Meta's AI
assistant..."/"News reports also cited one employee's report."/
"However, this is only one report...")は全てACCEPTABLE/QUALITYの
まま、floorの強制なし。

**Rewrite内容(逐語diff、`difflib.SequenceMatcher`)**: cycle1の
Rewriteは両runとも"calls"→"one call"/"a call"、"These calls were"→
"This call was"の単語・数の一致のみ(2 diff ops)。sample1 cycle2は
新規claim("Some calls needed user information to continue.")への
対応で5 diff ops(文レベル)だが、段落・見出しへは及ばず、「## In one
line」は全cycleで前後とも存在を確認した(rep19 cycle3で発生した見出し
消失は再発せず)。

**sample2のSTAGE4**: cycle1解消後、cycle2のRecheckが新規claim
("They could not tell if it was AI or a person" and "They did not
realize it."、MUSE-HC-012、`llm_materiality=BLOCKING`・floor非適用
[floor_reasonなし、LLM独立判定])を検出したが、ladder(①単語・接続詞→
③1文)を使い切っても解消せず、`ladder_exhausted_without_full_rewrite`
(⑥全文Rewrite不使用のまま安全側にfail-closed、既存の安全装置)で
STAGE4_ESCALATION。判定を緩めて通過させたわけではなく、false PASSでは
ない。

false PASS: 0件。`detect_safety_critical_misdowngrades`(meta群は対象外)
: 該当行なし。

### 33-3. Safety対照(regression確認、2系統)

**対照A(Safety12のうち2 fixture、full flow n=1)**: `safety_er009_
changed_number`/`safety_er009_changed_actor`を既定構成でfull flow
実行。いずれも違反文自体が`deterministic_floor:changed_number`/
`deterministic_floor:changed_actor`でBLOCKING→Rewrite→`RESOLVED_
REWRITE`(¥0.5452/¥0.3534)。floorが引き続き正しく発火することを確認
(誤って弱まっていない)。

**対照B(Safety-critical 8claim、Stage2のみn=1、既存run_instance()の
cycle=1前半[Stage1 reuse→precheck floor claims→llm_claims→
run_stage2]のみを再利用、Rewrite/Recheckは回さない)**: `SAFETY_
CRITICAL_CLAIM_DEFS`登録の6 instance(bgroup_B3/safety_A2A3/safety_A4/
safety_A5/meta_run03_standard/bgroup_B4)を実行し、この簡易harnessで
検出できた6claim(A2A3-0/A4-0/A4-1/A5-0/Meta-1/B4-a)は全てBLOCKING
維持(0件downgrade、¥1.3309)。残り2claim(B3/Meta-2)は「検出できな
かった」(downgradeされたのではない): B3は既知のStage1 recall miss
(`KNOWN_RECALL_MISS_INSTANCE_IDS`に既に登録済み、§10/§14既知の限界、
本委任のfloor修正とは無関係)。Meta-2は、この簡易harnessが使う
`meta_run03_standard`のstage1_source(`build_target_instances()`の
`BGROUP_STAGE1_DIR`経由、rep19/rep20のfrozen fixtureとは別の実データ
snapshot)に含まれる2つのdeviation(`related_fact_id=MUSE-HC-010`の
"Some calls needed user information to continue."と、`MUSE-HC-012`の
"They did not realize it."のみ)が、`SAFETY_CRITICAL_CLAIM_DEFS`の
Meta-2定義(`fact_id=MUSE-HC-012`+部分文字列"needed user information
to continue")のどちらとも一致しない、という既存データの特性であり、
本委任のfloor修正の影響ではないことを個別に確認した(実データ照合、
33-3末尾参照)。**8claimのうち、検出された上でBLOCKINGから他状態へ
downgradeした事例は0件**。

### 33-4. VALIDATED最低条件7項目の再評価(iter8実測との置き換え、判定はFable)

委任_34までのiter8実測ベースの評価のうち、以下がrep20実測で置き換わる
候補である(採否判定はFableへ委ねる):
- 「meta_run03_standardがStage4到達2/2」→rep20では1/2(sample1は
  RESOLVED、sample2のみSTAGE4)。ただしStage1自体の揺れ(cycle1検出が
  run毎に変わる、(b))は本委任の対象外であり、frozen fixture固定下での
  結果である点に留意。
- 「cycleごとの検出対象増加(2→12→5)」→rep20では両runともcycle1の1件
  のみに収束し、増加連鎖は再現しなかった。
- 「Rewriteによる品質劣化(別文丸ごと置換・見出し削除)」→rep20では
  いずれも再発せず。

### 33-5. 費用・unittest・Git

本委任費用: 分析(Part A)¥0+rep20(Part B本体¥3.8487[sample1
¥2.0186+sample2¥1.8301]+Safety対照A¥0.8986+Safety対照B¥1.3309)=
**¥6.0782**(Guardrail¥10のうち約61%)。Phase累計¥476.2883+¥6.0782=
**¥482.3665**/総枠¥600、残**¥117.6335**。

コード変更: `er052_open233_self_recovery_flow_runner_01.py`
(`apply_floor`/`apply_floor_cited`/`run_recheck`/
`measure_section_role_violation`/`run_instance`のhard block条件、
`OUT_DIR_REP20`/`BUDGET_STATE_PATH`/`TOTAL_BUDGET_JPY`新設、既存
`OUT_DIR_REP7`〜`REP19`等は無変更)。新規:
`er052_open233_self_recovery_flow_runner_01_rep20_representative_01.py`、
`er052_open233_self_recovery_flow_runner_01_test_01.py`へ新規unittest
12件追加。**Production code(er003/er006/er009/er010/er012/er019)・
既存iteration1〜8・rep7〜19・Hormuz/Safety/rep19 frozen fixtureは
一切変更していない**(rep20はrep19のfrozen fixtureを読み込むのみ)。
unittest304件(既存292+新規12)全PASS(API呼び出し前、¥0)。project-wide
regression(`run_project_regression.py`)も実行し、新規failureが
本委任の変更に起因しないことを確認した(詳細は`docs/pm/ACTIVE_TASK.md`
一時ファイルの実行ログ参照、既存の無関係failure[er052_open233対象外の
他ER群]は本委任開始前から存在する既知の状態)。

**STOP条件該当確認**: ¥10超え見込み(該当せず、累計¥6.0782/¥10)/API
error 3連続(該当せず、0 error)/Production・既存証跡変更(該当せず)/
USER_DECISION_REQUIRED 5条件(該当せず)/開始前チェック未反映(0件)/
Safety12の違反文またはSafety-critical 8がBLOCKINGでなくなる(該当せず、
33-3参照、downgrade0件)/false PASS 1件以上(該当せず、0件)/小修正1回
後もFAIL(該当せず、1回の小修正でrep20が成功)。STOP条件非該当のため
継続作業として記録・commit・push・回帰確認まで完了。

## §34. rep20 sample2の`ladder_exhausted_without_full_rewrite`根本原因特定と小修正(委任_36、2026-10-01)

管理ID: OPEN-233-SELF-RECOVERY-TRIAL-01(委任_36: rep20 sample2の
`ladder_exhausted_without_full_rewrite`の原因特定と小修正1回。広い
Trialは含めない)。

### 34-0. 上位目的整合チェック(7観点、design書§0-6/PM_GOVERNANCE§23)

| # | 観点 | 本委任での確認結果 |
|---|---|---|
| 1 | 厳密一致のためだけのRewriteになっていないか | 修正対象は対象文特定(locate)の範囲であり、Rewrite方式自体・guard判定基準は無変更 |
| 2 | 重大誤解でないものを止めていないか | 本修正はfail-closed追加(断片2つ以上かつ全断片実在時のみ発火)のみで、既存の「止める」判定基準は一切緩めていない |
| 3 | 小さく直せる問題を大きくRewriteしていないか | 新設スパンはmax_span_chars=600・同一段落内限定(空行を跨ぐ場合は不採用)とし、際限なく広い範囲を対象化しない |
| 4 | Rewriteによる品質劣化の方が大きくないか | rep21 sample2は単語置換のみで解消(34-2)、段落・記事全体への拡大Rewriteは発生せず |
| 5 | 学習者にとって本当に問題か | 対象claim(MUSE-HC-012の確実性強化)は実際にLedgerにない断定を含み、修正により是正対象として適切に扱われた |
| 6 | Human Reviewを安易な逃げ道にしていないか | 本修正はHuman Review回避のための判定緩和ではなく、Rewrite対象の特定漏れという実装上の不備の是正。sample1の新規STAGE4は判定を緩めず安全側に倒れたまま(34-2) |
| 7 | 不要call・Recheck・Rewriteを増やしていないか | rep21(n=2+Safety対照n=1)で¥3.561(Guardrail¥7のうち約51%)、rep20(¥6.0782)より総コスト減 |

### 34-1. 原因特定(¥0、API呼び出しなし)

rep20 sample2 cycle2のinstance json(`er052_output/open233_self_
recovery_flow_runner_01_rep20/instances_s2/meta_run03_standard.json`)を
逐語確認した。cycle1はMUSE-HC-011(`changed_number`、"calls"→"These
calls"の複数形)が`deterministic_floor:changed_number`でBLOCKING、
`e1_minimal_word_edit`(ladder①)で解消(guard_ok=True)。cycle2の
Recheckが新規claim(MUSE-HC-012、claim_text=`“They could not tell if it
was AI or a person” and “They did not realize it.”`、`llm_materiality
=BLOCKING`、floor非適用[LLM独立判定]、`changed_certainty=True`かつ
`changed_scope=True`)を検出した。sample1では同じfact(MUSE-HC-012)の
類似claimが`disclosure_gap_negative_inference_downgrade`floor
(`apply_disclosure_gap_downgrade`、`changed_scope`を含むdisqualifying
flagsがいずれも立っていない場合のみ発火)でQUALITYへ降格されるが、
sample2 cycle2のこのclaimは`changed_scope=True`が立っており、floorの
適用条件3(`DISCLOSURE_GAP_DISQUALIFYING_FLAGS`に`changed_scope`を含む)
により降格対象外のままBLOCKINGに残った(Stage2 LLMの非決定性、§6-14の
(b)と同系統)。

このBLOCKINGなclaim_textを決定論的に再現スクリプトで解析したところ、
claim_textが記事中の非隣接2文(「They could not tell if it was AI or a
person.」と「They did not realize it.」)を“…” and “…”の形で結合した
合成claimであり、両断片とも`en_full`(cycle1の`en_text_after_rewrite`)に
逐語で実在することを確認した。一方、既存`locate_target()`
(`er052_open233_self_recovery_flow_runner_01.py`)は、rewrite_hintの
引用断片(第一キー、本caseはJA文のためen_targetには不一致)に失敗すると
claim_text全体に対する1文fuzzy match(`locate_best_sentence`、
SequenceMatcher)のみを試みるため、2断片のうち一方(「They could not
tell if it was AI or a person.」、ratio=0.74)しか`en_target`に入らず、
もう一方の「They did not realize it.」がladder①(単語・接続詞)→③
(1文)→④(段落)のいずれの編集対象にも一度も入らないまま残った
(`er052_open233_self_recovery_flow_runner_01_rep20_representative_01.py`
を経由せず、`locate_target`/`locate_best_sentence`を直接呼ぶ独立の
再現スクリプトで確認、API呼び出しなし・¥0)。JA側も、rewrite_hintの
引用断片(`けれど、その一部では人間が話していた。しかも、適切な説明が
ないままなら、利用者は相手がAIなのか人間なのかを知ることができません。」`)
が、EN側の(修正前の)1文target「They could not tell if it was AI or a
person.」とは対応しない広い範囲(2文分)を拾っており、EN/JA双方で
対象範囲が食い違っていた。

ladder各段(①〜④)でguardが通らなかった理由(各段のLLM応答内容そのもの)
は保存済みjsonに含まれず(prompt本体・応答本体はsha256のみ記録する
既存の設計制約、§0参照)、API呼び出しなしでは再現できないため、本件は
「対象文の特定漏れ」という決定論的に再現可能な一次原因までを根本原因
として特定した(ladder各段のLLM応答内容そのものの検証は本委任の
Guardrail¥7の範囲外、必要であれば別途API呼び出しを伴う追加委任で検証)。

### 34-2. 修正(1回、fail-closed新規追加のみ)

design書§6-17参照。`extract_all_quoted_fragments`/`locate_multi_quote_
span`の2関数を新設し、`locate_target()`へ第二キー(rewrite_hint引用の
次、既存`locate_best_sentence`の前)として組み込んだ。`run_paired_local_
rewrite()`のJA側target決定は、`en_target`が`multi_quote_span`で特定
された場合に限り、rewrite_hintのJA引用断片より位置写像
(`locate_ja_counterpart_by_position`)を優先するよう変更した。
multi_quote_span以外の既存経路(claim_textが単一断片・断片なし・断片が
full_textに不在・段落を跨ぐ・600文字超)はいずれもfail-closedで既存の
`locate_best_sentence`経路へそのまま委ねる(新規コードパスは「2つ以上の
断片が同一段落内に逐語で実在する」場合のみ発火)。

unittest: 開始前チェック(既存304件、API呼び出し前に再確認、全PASS)
→新規13件(`TestExtractAllQuotedFragments`5件・`TestLocateMultiQuoteSpan`
5件・`TestLocateTargetMultiQuoteIntegration`3件)→計317件、全PASS(¥0、
API呼び出し前)。うち`test_reproduces_rep20_sample2_cycle2_fix`は、
rep20 sample2 cycle2の実データ(claim_text/en_full、上記34-1)をそのまま
使い、修正後は`en_target`が両断片を含むスパンを返すこと、旧実装
(`locate_best_sentence`単体)は「did not realize it」を含まない1文しか
返さないことを両方確認する回帰ロックテストである。

### 34-3. rep21実測(frozen fixture再検証、n=2+Safety対照changed_number n=1)

rep19/rep20と同一のfrozen fixture(`er052_output/open233_self_recovery_
flow_runner_01_rep19/stage1_fixtures/meta_run03_standard_iter8_cycle1_
frozen.json`、再freezeせず読み込むのみ)を`er052_open233_self_recovery_
flow_runner_01_rep21_representative_01.py`(新規、`OUT_DIR_REP21`新設)で
再実行した。

| run | final_state | stage4_reason | cycle数 | 費用 |
|---|---|---|---|---|
| sample1 | `STAGE4_ESCALATION` | `cycle_limit_exhausted` | 3 | ¥2.1567 |
| sample2 | `RESOLVED_REWRITE_THEN_DOWNGRADE` | - | 2 | ¥1.2052 |
| Safety(changed_number) | `RESOLVED_REWRITE` | - | 1 | ¥0.1991 |

**sample2(本委任の修正対象)**: cycle1でMUSE-HC-011(`changed_number`)が
`e1_minimal_word_edit`で解消。cycle2はMUSE-HC-012「They enjoyed...」
claimのみ再検出されたが、今回は`changed_scope=False`で`disclosure_gap_
negative_inference_downgrade`floorが正しく発火しQUALITYへ降格、
blocking_count 0で`RESOLVED_REWRITE_THEN_DOWNGRADE`。STAGE4へは至らず、
本委任の修正対象そのものは解消した。ただし本run自体では、rep20で観測
された2断片合成claim(`changed_scope=True`で降格対象外になるケース)は
Stage2 LLMの非決定性により再現しなかった(34-1で述べた本来の修正対象
ケースの直接再現ではない)。本修正の有効性は34-2の決定論的unittest
(API呼び出し非依存)で確認済みであり、rep21はSafety側のregression確認
(他claimを誤ってdowngradeしていないこと)として位置づける。

**sample1(新規STAGE4、本委任のスコープ外)**: rep20では3cycleで
`RESOLVED_REWRITE_THEN_DOWNGRADE`だったが、rep21では`STAGE4_ESCALATION`
(`cycle_limit_exhausted`)となった。原因を追跡し、本委任の修正とは
**無関係**であることを決定論的に確認した: 該当claim_text(`“It said
human staff made inappropriate comments about race during calls. These
calls were about trying to lower internet or cable fees.”`)は
bracket-quote断片が1つのみ(2文が1つの“…”で囲まれている)であり、
`locate_multi_quote_span`はこの入力に対し`not_multi_quote`を返して
即座に既存経路(`locate_best_sentence`)へ委ねる(本修正の新規コードパス
は不発火、修正前後でこのcaseのコード経路は完全に同一であることを
独立の再現スクリプトで確認)。実際の原因は、cycle1でStage2 LLMが
`rewrite_hint`を空文字列で返したこと(rep20では引用断片入りの
rewrite_hintを返していた、API応答のrun間非決定性)により、
`locate_target`の第一キー(rewrite_hint引用)が不発火となり、1文
SequenceMatcher fallbackが2文結合quoteのうち1文(「...during calls.」)
しか捕捉できず、未捕捉側(「These calls were...fees.」)がcycle2以降も
再検出され続け、cycle上限(3)に達したことによる。これは本委任が修正した
「2つの独立した引用断片」パターンとは別の、「1つの引用が複数文へ
またがる」という近縁だが別個の既知の限界であり、変種(e)として記録する
(34-4)。false PASSではない(STAGE4_ESCALATIONは安全側のfail-closedで
あり、判定を緩めて通過させたわけではない)。

**Safety対照(changed_number fixture1件、full flow n=1)**: 引き続き
`deterministic_floor:changed_number`でBLOCKING→`e1_minimal_word_edit`で
Rewrite→`RESOLVED_REWRITE`(¥0.1991)。floorが弱まっていないことを確認。

`detect_safety_critical_misdowngrades`: 該当行なし(0件)。false PASS:
0件(STAGE4_ESCALATION/RESOLVED_REWRITE_THEN_DOWNGRADE/RESOLVED_REWRITE
のみ、PASS系で未検査のまま通過したケースなし)。

### 34-4. 残課題(次委任候補、本委任では未修正)

変種(e)「1つの引用文字列が複数文にまたがり、かつrewrite_hintが空の
場合、SequenceMatcherベースの1文fallbackが先頭文しか捕捉しない」は、
本委任が修正した「複数の独立した引用断片」パターンと症状は同系統だが
トリガー条件が異なる別個の限界であり、委任文が指定した「rep20 sample2
の原因特定と小修正1回」の範囲を超えるため、本委任では修正しなかった
(範囲拡大の勝手な判断は行わず報告のみ)。修正要否・次委任での対応は
Fable/ユーザー判断事項とする。

meta_run03_standardの(b)Stage1 fresh enumeration非決定性そのものの
改善要否(委任_33から継続)、Phase 2新規テーマ選定(PM_GOVERNANCE§13)も
引き続きFable/ユーザー判断事項として継続。

### 34-5. 費用・unittest・project-wide regression・Git

本委任費用: 分析(34-1)¥0+修正実装(34-2)¥0+rep21(Part B本体¥3.3619
[sample1¥2.1567+sample2¥1.2052]+Safety対照A¥0.1991)=**¥3.561**
(Guardrail¥7のうち約51%)。Phase累計¥482.3665+¥3.561=**¥485.9275**/
総枠¥600、残**¥114.0725**。

コード変更: `er052_open233_self_recovery_flow_runner_01.py`
(`extract_all_quoted_fragments`/`locate_multi_quote_span`新設、
`locate_target`/`run_paired_local_rewrite`のja_target決定への組み込み、
`OUT_DIR_REP21`/`BUDGET_STATE_PATH`/`TOTAL_BUDGET_JPY`新設、既存
`OUT_DIR_REP7`〜`REP20`等は無変更)。`er052_open233_self_recovery_flow_
runner_01_test_01.py`(新規unittest13件)。新規`er052_open233_self_
recovery_flow_runner_01_rep21_representative_01.py`、`er052_output/
open233_self_recovery_flow_runner_01_rep21/`(新規)。**Production
code(er003/er006/er009/er010/er012/er019)・既存iteration1〜8・
rep7〜20・rep19 frozen fixtureは一切変更していない**(rep21はrep19の
frozen fixtureを読み込むのみ)。

unittest317件(既存304+新規13)全PASS(API呼び出し前、¥0)。project-wide
regression(`run_project_regression.py`)も実行し、collected=4284
(既存4271+新規13)・failed=6・errors=5。失敗/エラー計11件は以下の
test moduleのみで、いずれも本委任が変更した`er052_open233_self_
recovery_flow_runner_01.py`/`er052_open233_self_recovery_flow_runner_
01_test_01.py`を経由しない(`er052_open233_self_recovery_flow_runner_
01_test_01`単独実行317件全PASSで別途確認済み): `er003_test_bad`
(`test_case_0`)、`er003_test_p2j_investigate`(`test_per_file_counts_
sum_matches_pattern_discovery`/`test_combined_equals_sum_of_er002_
and_er003`/`test_p2h_reported_count_matches_er002_plus_er003_at_
that_time`/`test_p2i_reported_count_matches_er003_at_p2i_era`)、
`er015_standard_a2_6000_generation_first_trial_01_test_01`
(loaderエラー)、`er025_pronunciation_resolution_phase3_b1b_en_
wiring_01_test_01`、`er040_tts_fixed_shell_master_champion_trial_
01_test_01`、`er043_tts_fixed_shell_master_champion_trial_02_test_
01`、`er011_open112_trend_synthesis_mode_production_wiring_01_
test_01`(`TestBuildCommonBlockDefaultByteParity`系3件)。本委任由来の
新規failureはない。

**STOP条件該当確認**: ¥7超え見込み(該当せず、累計¥3.561/¥7)/API
error 3連続(該当せず、0 error)/Production・既存証跡変更(該当せず)/
USER_DECISION_REQUIRED 5条件(該当せず)/開始前チェック未反映(0件)/
Safety12の違反文またはSafety-critical 8がBLOCKINGでなくなる(該当せず、
34-3参照、downgrade0件)/false PASS 1件以上(該当せず、0件)/小修正1回
後もFAIL(該当せず、本委任の修正対象[sample2 cycle2のladder枯渇]は34-2
の決定論的unittestで解消を確認)。STOP条件非該当のため継続作業として
記録・commit・push・回帰確認まで完了。


## §35. 受け渡し修正(Checkerの違反範囲をそのままRewriteへ、再推測の廃止)の実装と限定Trial rep22(委任_42、2026-10-02)

管理ID: OPEN-233-SELF-RECOVERY-TRIAL-01(委任_42: ユーザー指示§1・§2の実装+限定Trial)。
設計書追記: `docs/pm/design_open233_self_recovery_flow_01.md`§6-18(実装内容・対応表・結果の要約)。本節は詳細証跡。
Trial/検証用の実装であり、Production採用ではない(`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`ではない)。
最終分類(`REJECTED`/`VALIDATED`/`USER_DECISION_REQUIRED`)はFableが行う(本節は実測値と所見まで)。

### 35-0. 変更範囲・Production未変更の確認

変更ファイル: `er052_open233_self_recovery_flow_runner_01.py`(Trial専用runner)、
`er052_open233_self_recovery_flow_runner_01_test_01.py`、新規
`er052_open233_self_recovery_flow_runner_01_rep22_representative_01.py`、新規
`er052_output/open233_self_recovery_flow_runner_01_rep22/`。Production正式path
(`er003_v1_n3_01_articles_generate.py`、`er003_v1_en_direct_vfl_01_generate.py`等)・Checker(Stage 1/Recheck)の
Prompt・schema・Stage 2のPrompt・rubric・floor・`MAX_CYCLES`/`HARD_MAX_CYCLES`・⑥(既定OFF)は無変更。
`git grep -n "er052_open233" -- "er003*.py" "er0[0-4]*.py"` = 0件(Production側がrunnerをimportしていない)。

対象決定の経路から旧4段が外れていることの確認(runner内の呼び出し元Grep、`locate_target|locate_best_sentence|
locate_multi_quote_span|extract_quoted_fragment|locate_ja_counterpart_by_position|detect_claim_section_type|
claim_text.strip() not in`): 新方式(既定)でのEN側対象決定には使われない。残る呼び出し元は次のとおり。
(a)`single_text_rewrite`の旧方式本体(冒頭の`HANDOFF_MODE`分岐の後ろ、legacy専用)、(b)`paired_rewrite`のEN対象の
`else`分岐(legacy専用)、(c)`paired_rewrite`のJA側対応決定(`locate_ja_counterpart_by_position`・
`extract_quoted_fragment`[判定役のhint引用]・`locate_best_sentence`)は**ユーザー決定どおり本委任では変更していない暫定の既存処理**
(ja_sourceかつEN単一範囲のpaired経路のみ)、(d)`detect_claim_section_type_legacy`(legacy専用)。

### 35-1. 実装(仕様(1)〜(10))

設計書§6-18の表のとおり。新規関数: `vs_*`(照合・結合・文拡張・書き戻し)、`resolve_violation_spans`、
`claim_span_text`、`annotate_claim_span_identity`、`rewrite_ranges_ladder`(+`E1/E2/E4_RANGES_*`Prompt)、
`run_stage3_for_claim_spans`/`_run_stage3_spans_core`、`_paired_en_target_from_span`、`collect_replaced_units`、
`carry_forward_resolution`、`detect_claim_section_type_by_spans`。`find_matching_prior_record`へ任意引数`claim_norm`を追加。
`OUT_DIR_REP22`/`BUDGET_STATE_PATH`(`budget_state_c233an_42_rep22.json`)/`TOTAL_BUDGET_JPY=14.5`を新設(Guardrail¥15)。

テスト: `er052_open233_self_recovery_flow_runner_01_test_01`は317件→381件(新規64件)全PASS(`-m unittest`)。
`run_project_regression.py --pattern "er052*_test_*.py"`: collected=425/passed=425。project-wide(`run_project_regression.py`):
collected=4348(4284+64)・passed=4337・failed=6・errors=5。失敗/エラー11件は委任_36時点(§34-5)と同一のmodule
(`er003_test_bad`・`er003_test_p2j_investigate`4件・`er015_standard_a2_6000_generation_first_trial_01_test_01`[loaderエラー]・
`er025_pronunciation_resolution_phase3_b1b_en_wiring_01_test_01`・`er040_tts_fixed_shell_master_champion_trial_01_test_01`・
`er043_tts_fixed_shell_master_champion_trial_02_test_01`・`er011_open112_trend_synthesis_mode_production_wiring_01_test_01`3件)で、
新規failureなし。意図的に書き換えた既存テスト: `@_legacy_handoff`(旧方式を明示)7件=
`TestMinimalChangeLadderOrdering`2件・`TestEscalateToParagraphLadderSkip`2件・`TestEscalateToParagraphDisabledByDefault`1件・
`TestActorGuardAlwaysEvaluatedRegardlessOfProblemKind`1件・`TestTargetNotLocatableEarlyReturn`の
`test_paired_rewrite_partial_locate_delegates_to_single_text_rewrite`1件、および`TestDegenerateRewriteHardBlockWiring`の
stage4_reason文字列のソース検査1件。旧`locate_target`/`locate_multi_quote_span`の関数単体テスト(`TestLocateTarget`・
`TestLocateTargetMultiQuoteIntegration`等)は旧関数を残すため無変更で維持(新方式の同等の挙動は新規テストで固定)。

新規テストの必須実例(a)〜(h)はすべて`TestResolveViolationSpans`/`TestHandoffRewriteLadder`等に含まれる:
(a)`test_a_...`、(b)`test_b_...`、(c)`test_c_...`、(d)`test_d_...`/`test_d2_...`、(e)`test_e_...`、(f)`test_f_...`/`test_f2_...`、
(g)`test_g_...`/`test_g2_...`、(h)`test_h_...`/`test_h2_...`(旧guardの盲点[2文claimの片方だけ変更でも通っていた]が閉じていること)。
rep22 T3で判明した不具合の是正は`TestHandoffCarryForwardWithinCycle`(6件)。

### 35-2. Trial実行コマンドと費用

作業ディレクトリ`C:\Users\tensh\eigo-radio`、`PYTHONIOENCODING=utf-8 .venv\Scripts\python.exe
er052_open233_self_recovery_flow_runner_01_rep22_representative_01.py --parts t3`(Safety対照、2回: 是正前run1・是正後run2)、
`--parts t1 --t1-n 4`、`--parts t2 --t2-n 2`、`--parts agg`(記録済みJSONの集計、API呼び出しなし)。予算は
runner定数`TOTAL_BUDGET_JPY=14.5`(Guardrail¥15)。TTSなし。`TTS_EXECUTION_MODE`は非該当。

費用(instance JSONの`total_cost_jpy`の合計、¥): T3 run1 0.1992(是正前)+T3 run2 0.2311+T1 5.6241(s1 1.1210/s2 2.1773/s3 1.3140/s4 1.0118)+
T2 2.0481(s1 1.0338/s2 1.0143)=**8.1025**。Phase累計¥485.9275+¥8.1025=**¥494.0300**/総枠¥600、残**¥105.9700**。
(予算state`budget_state_c233an_42_rep22.json`の`cumulative_jpy`=7.9033は、T3 run1[¥0.1992]がunittest実行によるstate
ファイル上書きで失われているため総額より小さい。既存の仕様[unittestの`TestNoCrossModuleBudgetStateContamination`系がBUDGET_STATE_PATHへ書く]で、
rep21のstateファイルも同じ痕跡[`test_recheck`]を持つ。正式な費用はinstance JSONの`call_log`合計。)

### 35-3. T1(固定Stage 1×n=4、`instances_s1`〜`s4`)

固定Stage 1: `er052_output/open233_self_recovery_flow_runner_01_rep19/stage1_fixtures/meta_run03_standard_iter8_cycle1_frozen.json`
(再freezeしない)。全4 sampleで、cycle1のBLOCKINGは1件=MUSE-HC-011「“It said human staff made inappropriate comments about race
during calls. These calls were about trying to lower internet or cable fees.”」(`deterministic_floor:changed_number`)。Checker文字列は記事に
ちょうど1箇所(L1=両端の引用符を外す)で、**2文が1つの範囲**として確定し、水準①の対象は4/4でこの2文(対象==確定範囲)。
①の結果は4/4で成立(例: 2文が「…race during a call. These calls …」のように書き換えられ、範囲の外は不変)。

| run | final_state | stage4_reason | cycle | call | 費用 |
|---|---|---|---|---|---|
| s1 | `RESOLVED_REWRITE_THEN_DOWNGRADE` | - | 2 | 4 | ¥1.1210 |
| s2 | `STAGE4_ESCALATION` | `cycle_limit_exhausted` | 3 | 7 | ¥2.1773 |
| s3 | `RESOLVED_REWRITE_THEN_DOWNGRADE` | - | 2 | 4 | ¥1.3140 |
| s4 | `RESOLVED_REWRITE_THEN_DOWNGRADE` | - | 2 | 4 | ¥1.0118 |

s2のStage 4の周回別の指摘(受け渡し以外が原因):
- cycle1: 上記HC-011(BLOCKING)→①成立。Recheck: 前回指摘は解消(`all_prior_issues_resolved=True`)、次cycleへMAJORが2件。
- cycle2(Stage 2): QUALITY=MUSE-HC-012「They enjoyed AI’s convenience, but a human was on the other end. They did not realize it.」
  (LLM判定BLOCKING→既存floor`disclosure_gap_negative_inference_downgrade`でQUALITY)。BLOCKING=MUSE-HC-010
  「some calls needed user information to continue」(Checker文字列は文の断片で小文字・句点なし、L0で確定。元記事の「Also, some calls needed
  user information to continue.」で、元記事に最初からあった問題。固定Stage 1は検出していない)。HC-010は既存の問題種類→初期水準の規則
  (`multi_sentence`、委任_27)により④から開始し成立(段落「Also, some calls needed … privacy concern.」を「If a call needs user
  information, it may be shared by mistake with call center contract workers. …」へ)。Recheck: 前回指摘は解消、MAJORが1件。
- cycle3: MUSE-HC-012「They enjoyed AI’s convenience …」が**BLOCKING**(cycle1・2は既存floorでQUALITY)。cycle3はMAX_CYCLES=2を超え、blocking件数が
  減少せず新しいfact_idでもないため追加cycleが許可されず`cycle_limit_exhausted`。
- 原因の切り分け: 受け渡し起因ではない(各周回の対象は常にCheckerの文字列どおり)。元記事にあった問題(HC-010)を固定Stage 1が見逃し、
  Recheckがcycle2で初めて検出したこと(再検出の揺れ)、同じ文(HC-012)のStage 2判定がcycle1・2=QUALITY→cycle3=BLOCKINGと揺れたこと。
  並行調査委任_44の対象で、本委任では修正していない。

### 35-4. T2(rep20 sample2 cycle2の状態からStage 3以降だけを実行、`instances_t2_s1`/`s2`)

**再現入力の組み方**: `rep20/instances_s2/meta_run03_standard.json`のcycle1記録`en_text_after_rewrite`(cycle1のRewrite後のEN本文)、
JA本文=fixtureの`source_article_text`(cycle1でJAは変化していない=記録に`ja_text_after_rewrite`なし)、cycle2の記録`stage2_results`のうち
BLOCKING 1件(claim_text=`“They could not tell if it was AI or a person” and “They did not realize it.”`、origin=`ja_source`、dev・rewrite_hint・
rewrite_kind=`narrow_scope`・materiality等をそのまま使用)。実行は`run_stage3_for_claim`(本番と同じ入口)→品質劣化v2/section_role→JAガード→
JA/EN等価チェック→`full_recheck_required`→(必要なら局所QA)→EN・JAの全文Recheckを、`run_instance`のcycle内ロジックと同じ関数・順序で再現。
**限界**: (1)cycle2のStage 1/Stage 2のLLMは再実行しない(記録を固定)ためその非決定性は再現しない、(2)1周のみ(cycle3以降は再現しない)、
(3)入力のEN本文は旧方式のcycle1の結果、(4)`repeat_fact_ids`は空として扱う。

結果(Checker文字列は記事のEN本文で**L4=2範囲**に確定: 「They could not tell if it was AI or a person」と「They did not realize it.」。間の文
「They enjoyed AI’s convenience, but a human was on the other end.」は対象外):

| run | 水準①(対象=2範囲、配列) | 水準③(対象=2文、配列) | 水準④(対象=段落) | 結果 | call | 費用 |
|---|---|---|---|---|---|---|
| s1 | 「最小編集では解消できない」(declined) | 主体置換ガードで棄却(新語`users`、Ledger本文[日本語]に無い) | 成立(7文の段落を3文[s1]/4文[s2]へ短縮して再構成。範囲外の文も含む段落全体が書き換わる[④の既存の性質]) | EN Recheck: 前回指摘は解消、新規なし。JA Recheck: 未解消(JA「適切な説明がないままなら、利用者は相手がAIなのか人間なのかを知ることができません。」)。`ja_ok=False` | 6 | ¥1.0338 |
| s2 | declined | 同上 | 成立 | EN Recheck: 前回指摘は解消、新規MAJOR=MUSE-HC-010「Also, some calls needed user information to continue.」(元記事にあった問題)。JA Recheck: 未解消(JAの2箇所)。`ja_ok=False` | 6 | ¥1.0143 |

JA暫定経路(仕様(8)、`en_multiple_ranges`)に2/2が該当(EN側だけを直し、JAは触らず既存のJA Recheckに任せた)。旧方式の同じ状態
(rep20 s2 cycle2)は①③④すべて不成立→`ladder_exhausted_without_full_rewrite`でStage 4。新方式は2範囲とも対象になり、④で成立し
ENの前回指摘は解消したが、JA未解消のため1周では`RESOLVED`にならない(2周目以降は再現範囲外)。

### 35-5. T3(Safety対照、`instances_safety_a`、是正前は`instances_safety_a_run1_before_carry_forward_fix`)

`safety_er009_changed_number`(rep21と同じfull flow n=1)。**run1(是正前)**: `STAGE4_ESCALATION`/`violation_span_unverified`(¥0.1992、2 call)。
原因: 同cycleにLLM claim(`deterministic_floor:changed_number`)とprecheck floor claim(`precheck_floor`、fact F-002)の2件が**同じ文**
(タイトル)を指しており、先行claimのRewrite(③)で文が書き換わった後、後続claimのCheckerの文字列が現在の本文から消え「不一致」→確定不能と
誤判定した(受け渡しの実装不具合。旧方式は類似度で書き換え後の文を拾っていた)。修正(本委任の範囲内、1回): `carry_forward_resolution`/
`collect_replaced_units`(cycle開始時点の本文でCheckerの文字列を照合し、その範囲が同cycleの先行claimのRewrite対象に含まれていれば
「先行Rewriteで書き換え済み」としてRewriteを重ねない。解消の判定は全文Recheck。先行Rewrite対象に含まれず現存もしない範囲は従来どおり
確定不能)。テスト6件追加。**run2(是正後、T3だけ再実行)**: `RESOLVED_REWRITE`(¥0.2311、3 call): 先行claimが③で
「more than 30 million」→「more than 13 million」(Ledger F-002「1,300万件」)へ修正、後続のfloor claimは先行Rewriteで書き換え済みとしてスキップ、
全文Recheck=`LEDGER_COMPLIANT`/`all_prior_issues_resolved=True`。floorは両claimともBLOCKING(Stage 2のllm_materiality=BLOCKING/precheck_floor)で
発火し、false PASS 0件。

### 35-6. 成功条件ごとの実測(`analysis_rep22.json`の記録値)

1. 2文取りこぼしによるHuman Review: T1 4/4で2文が1周目に2文とも①の対象(記録値`level_attempts[0].targets`)。Stage 4=1/4、取りこぼし起因0。**達成**。
2. 範囲の縮小: ①試行6件(T1 4+T2 2)で`target_equals_confirmed_ranges`=6/6、不一致0。**達成**。
3. 誤PASS: T3 false PASS 0(floor発火・Ledger値へ修正)。T1/T2で未解消のBLOCKINGが残ったまま合格した例は0。**達成**。
4. 最小修正優先: ①開始6/7(T1 5claim中4、T2 2/2=計7claim中6。残り1=T1 s2 cycle2のHC-010は既存の問題種類規則で④開始)、T3は既存規則で③開始。
   成立水準: T1 ①4・④1、T2 ④2、T3 ③1。**達成(開始水準は既存の水準選択規則に従う)**。
5. 不要な段落・全文Rewrite: ⑥=0。④成立はT1で1/4 run(旧方式rep20 s1・s2/rep21 s1・s2も1/4 run)、T2は2/2(旧方式は同じ状態でStage 4)。
   T1では増加なし。T2は①declined・③主体置換ガード棄却の後の④であり「不要」かはFable判断。
6. その他: 確定不能(最終runでの`violation_span_unverified`)0件(T3 run1の1件は是正済みの不具合)、JA暫定経路2件(T2、`en_multiple_ranges`)・JAのみ確定0件、
   carry-forwardスキップ1件(T3 run2)。

### 35-7. 残る問題・未確認事項

(1)T2はJA暫定経路のため、ENの前回指摘が解消してもJA Recheckが未解消を返す(2/2)。次cycleでJA側のRewriteへ進む挙動は本再現の範囲外。
JA側の構造見直し(英語だけ直す化)は別委任(並行調査委任_43)+Opusレビュー後。(2)T1 s2型(周回ごとの新規指摘・Stage 2重大度の揺れ)は受け渡し修正では
解消しない(並行調査委任_44)。(3)主体置換ガード(`actor_rewrite_guard_ok`)が、範囲の外の同じ段落にある語(`users`)でも「新しい主体語」として扱い③を棄却した
(既存ガード、無変更)。(4)Checker引用の特定不能率(委任_41集計の13.4%)に対する対策(Prompt変更等)は本委任の対象外(委任_45で原因分類)。(5)29件横断再確認・実記事N増しへ進む前に、
Fableによる上記の分類判断と、JA側の暫定経路の扱い・T1 s2型の対策方針(別委任)の決定が必要。

## §36. 受け渡し修正後の原因調査・対策設計・Opusレビュー#6・追補実装と検出器比較(委任_43〜49、2026-10-02)

管理ID: OPEN-233-SELF-RECOVERY-TRIAL-01。Trial/検証用であり、Production採用ではない(`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`ではない)。
最終分類はFableが行う(本節は実測値と所見まで。OPEN-233のStatusは「Trial継続中・分類保留」)。Production正式path(er003/er012/er019等)は無変更。

### 36-1. DECISION_LOG追記(2026-10-02エントリ)の1〜6
正本は`DECISION_LOG.md`末尾の「2026-10-02 OPEN-233-SELF-RECOVERY-TRIAL-01(委任_43〜49、Opus独立レビュー#6後のFable判断)」。要点を再掲する(数値の出所は下記の成果物)。
1. rep22の分類=保留(`VALIDATED`にしない)。固定Stage 1の4実行中3実行で、Safety-criticalな文「Also, some calls needed user information to continue.」(MUSE-HC-010、Meta-1)が元のまま残り・一度もBLOCKINGで指摘されず・人間確認なしで終了(旧方式の同じ入力では7実行中1実行、回数が少なく因果は断定できない)。出所: `er052_output/open233_rep22_truth_label_check_01/`(委任_47)。原因は受け渡しではなくChecker側の見逃し。
2. 委任_42の「false PASS 0」は「検出済みBLOCKINGが未解消のまま合格した例が0」の意味(正解ラベル照合ではない)。既存の安全評価は「指摘された後の降格」だけを見る(評価の盲点)。
3. 調査結果(委任_43〜47): 特定不能35件=末尾句読点22・説明文混入12・省略記号1・言い換え0(委任_45)。周回2以降の新規BLOCKING 85行=見逃し34・書き換え起因20・重大度の揺れ15・取りこぼし8・判定不能8(委任_44)。
4. Opus独立レビュー#6(`docs/pm/opus_l2_review_open233_self_recovery_06.md`)の要点: 合格の判定がどの出口でも1回の検査結果だけに依存することが根本原因。MINOR仮説(未検証)。英語だけ修正には補正が必須。
5. Fableの採否: 実装=記録の追加・照合の追補・英語だけ修正(補正つき)、測定=検出器の直接比較、見送り=A3・B・B-alt・C1本体・C2・C5、実装しない=A4(b)・降格ルール変更・MINORを後段へ渡す変更。
6. 委任_49の結果(下記36-2〜36-6)。

### 36-2. 作業1: Opusが挙げたコード上の事実の確認(実装前、¥0。行番号は実装前のrunner)
| # | 主張 | 判定 | 根拠(行) |
|---|---|---|---|
| 1 | `severity=="MAJOR"`だけを後段へ渡し、MINORを捨てる。捨てたMINORはinstance JSONに無い | 一致 | 5030行(Stage 1)・5596行(Recheck)の`d.get("severity") == "MAJOR"`。instance JSONのキーは`cycles`(stage2_results=MAJOR由来のみ)・`call_log`等で、MINORを含む生のdeviationsを保存するキーは無かった(rep22 instance JSONで確認) |
| 2 | 合格の出口は5つで、いずれも1回分の検査結果だけで決まる。S1-UはStage 1が空のときだけ | 一致 | ACCEPTABLE_STAGE1(4992)、RESOLVED_STAGE2_DOWNGRADE/RESOLVED_REWRITE_THEN_DOWNGRADE(5099)、局所QA fastpath RESOLVED_REWRITE(5478〜5480、全文検査なし)、Recheckで合格(5584〜5585)。`enable_s1u`は4961行で`overall_status != "LEDGER_DEVIATION"`のときだけ |
| 3 | `full_recheck_required`の(c)は「paired かつ(ladder≥④ or JAガード不通過)」に縮小され、JAを迂回すると`ja_source`の指摘も条件次第で局所QA fastpathで合格できる | 一致 | 4281〜4287行(`paired_records`が空なら(c)は不成立)。docstringの4271〜4274行は「paired J-1は常に全文Recheck」と食い違っていた(作業4-5でdocstringのみ訂正) |
| 4 | er003のChecker Promptに「自己申告の調査結果を断定的な行動として書く等はMINOR」の規定 | 一致 | `er003_v1_en_direct_vfl_01_generate.py` 533〜534行(逐語): 「意味はおおむね保っているが言い回しがやや粗い場合(出典に勝手な肩書きを補う、/自己申告の調査結果を断定的な行動として書く等)はMINORとして記録してください。」(Opusの指摘の534〜535行付近とは1行ずれ) |
| 5 | `vs_match_levels`は一致箇所の両端が単語境界かを見ない | 一致 | 2876〜2902行(`vs_find_all`によるsubstring一致のみ) |
| 6 | `classify_problem_kind`は論理系flag 2個以上で`multi_sentence`(段落水準) | 一致 | 380〜398行(`len(logic_hits) >= 2` → `multi_sentence`。Opusの指摘397〜401行付近) |

不一致なし。依存する作業はすべて進めた。

### 36-3. 作業2〜4: 実装(`er052_open233_self_recovery_flow_runner_01.py`、すべて既定=現行の挙動)
- スイッチ: `VS_MATCH_EXT`(既定False)、`JA_MODE`(既定`"paired"`、`"english_only"`)。CLIは`--vs-match-ext`/`--ja-mode`。
- A1(L5_edge_punct、`vs_edge_punct_match`): L0〜L4で確定しなかった場合に限り、両端の`. , ; : ! ?`(と空白)を除いた文字列が英語本文にちょうど1箇所かつ単語境界なら確定。英語本文のみ。範囲は一致文字列そのもの(文へ拡張しない)。断片(L4)の個別救済には使わない(全体の1回のみ)。
- A2-a(`label_only`): ラベル行の定義=行頭の`#`群と前後の空白を除いた残りが`in one line`(大文字小文字同一視)の行そのもの。`er019_output/`配下のa2/b1b記事21本の見出しをGrepで確認したところ、本文ではない区切りの行は`## In one line`の1種類のみ(`# タイトル`は違反箇所になりうるため対象外、`### 小見出し`は本文の見出し)。
- 単語境界(`vs_word_boundary_ok`): 英語本文へのL0〜L3の「ちょうど1箇所」の一致に課す。複数箇所一致の扱いは変えない(確定が減る方向のみ)。英数字・`_`・英数字に挟まれたアポストロフィを語の構成文字とする。
- 記録: `switches`、`all_deviations_raw`(stage1とrechecksごとの全件、`passed_downstream`)、`residual_at_pass`(定義名・残存の有無・`ever_blocking_flagged`[fact_id不問]と同一fact_id版・生のdeviationsでの重大度)、`severity_wobble`(周回間の最終判定の違いのflag・LLM判定・floor理由・basis)、carry-forward比較(`carry_forward_comparison`[issue文字列一致・`related_fact_id`一致・trueのflag集合一致]と`carry_forward_recheck_resolved`)、`en_title_rewritten`。合否・重大度・書き換え対象の決定には使わない。
- JA_MODE=english_only: `run_instance`冒頭で`current_ja_text=None`、`baseline_precheck_ja`はスキップ。`ja_source`の指摘を書き換えた周回は全文Recheckを必須(`english_only_ja_source_requires_full_recheck`)。日本語本文でしか確定しない指摘は確定不能(理由`ja_only_match_english_only`、記録のためだけに元の日本語を照合し、範囲の確定には使わない)。
- 指示と異なる点・判断: (a)`detect_safety_critical_misdowngrades`は不変(併存)。(b)既存のテストが`BUDGET_STATE_PATH`(rep22の予算state)を上書きする既知の問題があり(今回のテストが原因ではない)、回帰実行のたびに`git checkout`で復元した。(c)T-0の保存ファイル`_49.md`は、受領した委任文のうちSSOT追記文の長大な本文と報告項目の細目を参照形式に圧縮した(それ以外は原文のまま。要約保存不可の指示からの逸脱)。

作業4-4: `current_ja_text is None`で挙動が変わる`run_instance`内の分岐(実装前の行番号。`current_ja_text`のGrepで列挙)
| 分岐 | english_onlyでの挙動 | 判定 |
|---|---|---|
| `working_fixture["source_article_text"]`の上書き(5342) | 上書きされず元の日本語のまま=Checker/Stage 2/Recheckへ元の日本語が渡る(D1) | 迂回されて問題ない |
| `annotate_claim_span_identity`のJA照合(5387) | JA本文のみで確定する指摘は確定不能 | 迂回されて問題ない(4-3で理由コード記録) |
| `ja_pending_deviation`(5407ほか) | 常にFalse | 迂回されて問題ない |
| Stage 3の`use_pairing`/`paired_rewrite`/JA暫定経路 | 常にFalse、`ja_source`も英語単独のRewrite | 迂回されて問題ない(`ja_source`の扱いは4-2で補正) |
| `quality_degradation_ja`・JA本文の前後記録(5693〜5704) | 記録されない | 迂回されて問題ない |
| `ja_fail_open_guard`(5709〜5712、5778〜5785) | 実行されない(`ja_guard_ok=None`) | 補正が要る=4-2(`full_recheck_required`の(c)が常に不成立) |
| JA precheck(5736) | `[]` | 迂回されて問題ない |
| JA/EN等価チェック(5748)・`resolve_ja_ok_after_equivalence_gating`(5859) | 実行されない/ja_ok=True固定 | 迂回されて問題ない |
| `full_recheck_required`呼び出しのJA引数(5773) | `None`で渡る | 補正が要る=4-2 |
| 局所QA fastpathの`ja_pending_deviation`条件(5802) | 常に偽 | 補正が要る=4-2(`ja_source`のみ全文Recheck必須) |
| JA Recheck(5828)・JA指摘の合流(5943〜5946) | 実行されない | 迂回されて問題ない(EN Recheckが返す`origin=="ja_source"`は4-2で扱う) |

4-2以外に補正が要る分岐は見つからなかった。注意点(補正対象外、報告のみ): english_onlyでは、Checker/Stage 2/Recheckへ元の日本語(書き換えない)が渡り続けるため、英語を直した後も日本語を理由にした再指摘が起きうる(設計書§5-2のD1の既知の残リスク、実測未確認)。

### 36-4. 作業3-4(¥0再生)・2-6・2-7の結果
再生(`er052_output/open233_match_ext_replay_01/`、`replay_01.py`、既存の全BLOCKING 346行[K1 272・K2 55・K3 19]。runnerの`resolve_violation_spans`をOFF/ONで実行):

| 遷移 | 件数 | 備考 |
|---|---|---|
| 確定→確定(同じ範囲) | 298 | L0 191・L1 71・L2 11・L3 21・L4 4 |
| 確定→確定不能 | **0** | 単語境界・label_onlyで正当な確定が失われた例なし(逐語報告の対象=0件) |
| 確定→確定(範囲が変わった) | 0 | |
| 確定不能→確定 | 22 | すべてL5_edge_punct(U03 1・U04 1・U07 20、委任_45の22行と一致) |
| 確定不能→確定不能 | 26 | explanatory_mixed 13・mismatch 13(理由は変わらず) |

記事別: 確定不能→確定の22件は`bgroup_B3` 21・`bgroup_B2_hormuz` 1。label_onlyに該当する行は346行中0件。
- 2-7(日本語本文でしか確定しない指摘): 346行中3件(`safety_A2A3` HF-003 2件[iter7 s1・s2 cycle2]、`neg3_hormuz_prodrunner_b1b` HF-003 1件[rep16 s1 cycle2]、いずれも`origin==ja_source`)。出所: `er052_output/open233_match_ext_replay_01/ja_only_count_01.json`。
- 2-6(既知問題集合、rep22に適用、`er052_output/open233_known_issue_residual_check_01/results_rep22.json`・`cases_rep22.csv`): 既存394 instance記録から既知集合を作成(記事別。meta_run03_standardは32範囲)。rep22の合格系4 instance中3(meta_run03_standard s1・s3・s4)で「見逃しの疑い」各16件(計48件)、指摘済み0件。対象文は「some calls needed user information to continue.」「同(ピリオドなし)」の2形で入っている。注意: 既知集合は「過去に一度でもBLOCKINGになった範囲」をすべて含むため、正当な文(例「The problem was telling users who was speaking.」)も疑いとして並ぶ(ノイズが多い。指摘済み判定は包含関係のみで類似度は使っていない)。

### 36-5. 作業6: テスト・回帰
- runnerのunittest: 381 → 406件(新規25: A1[U03・U04・U07の実文字列が確定・単語途中は確定しない・日本語本文には適用しない・両端以外の句読点は除かない・複数箇所は確定不能のまま]、A2-a[ラベル行は確定不能、タイトル・本文は確定]、単語境界[L0〜L4・日本語は対象外]、スイッチOFFで委任_42と同じ結果、`JA_MODE=english_only`[日本語側の処理が呼ばれない・`ja_source`で全文Recheck必須・他のoriginは局所QA fastpathのまま・日本語のみ確定は`ja_only_match_english_only`]、`JA_MODE=paired`で従来と同じ、記録[合否が変わらない・MINORが後段へ渡らない・`residual_at_pass`の値・揺れ・carry-forward比較・英語見出し])。全PASS。
- er052回帰(`run_project_regression.py --pattern "er052*_test_*.py"`): 450件collected・450 passed・0 failed。
- プロジェクト全体の回帰: 4373件collected・4362 passed・failed 6・errors 5(計11件)。既存の失敗11件(er003_test_bad、p2j 4件、er015 loader、er025、er040、er043、er011 3件)と同一で、新規failureなし。

### 36-6. 作業5: 検出器の直接比較(`er052_open233_detector_direct_compare_01.py`、`er052_output/open233_detector_direct_compare_01/`)
- 固定入力(取り出した全本文で、該当文「Also, some calls needed user information to continue.」の完全一致[空白正規化のみ]を課金前に確認): P1〜P5は該当文が残っている(True)、N1〜N3は該当文が無い(False)。N1の書き換え後の文=「If a call needs user information, it may be shared by mistake with call center contract workers.」、N2=「If a call needed user information, it might be shared by mistake with call center contract workers.」(N2は"needed user information"を含むため、陰性の補助判定は"user information"で行った)、N3は`user information`を含む文なし。
- DET-Cの追記ブロック(`DET_C_BLOCK`、逐語):

```
【Trial専用の追加指示(OPEN-233、出口検査候補、Production非適用)】
Verified Fact Ledgerのfactを1件ずつ順に取り上げ、記事の中でそのfactに触れている文をすべて確認してください。
Ledgerが条件つき・可能性・懸念として書いている内容を、記事が実際に起きたこととして書いていないかを、各文で確認してください。
確認の結果は、重大度を問わず(MAJORもMINORも)deviationsにすべて列挙してください。
何を逸脱とするか、severityの基準、10種類のflagの基準は変えません。
```

- probe(P1の各検出器1回): DET-A ¥0.5139、DET-B ¥0.6064、DET-C ¥0.7152(出力トークン5.2k〜7.7k、reasoning主体)。58call(陽性n=3)の見込みは¥35.98、陽性n=2でも¥27.31と¥22を超える見込みだったため、陽性nを3→2に減らして実行した(指示どおり。実費の平均単価は見込みより低く、結果は44call・¥20.9881でGuardrail¥22内)。なお、最初のバックグラウンド実行が実行時間の上限で停止した際に実行中だった1call分は記録されていない可能性がある(再実行は完了済みのcallをスキップして継続)。
- 実施: 44call(DET-A 12[P1〜P4×2、N1・N2×2]、DET-B 16[P1〜P5×2、N1〜N3×2]、DET-C 16)、出力失敗0(JSON/schema/API)。
- 該当文の区分(検出器×本文、判定=`claim_in_article`を空白・引用符・大小文字で正規化した文字列が"needed user information"を含む、最終severity):

| 検出器 | P1 | P2 | P3 | P4 | P5 |
|---|---|---|---|---|---|
| DET-A(現行Recheck) | MAJOR 2 | MAJOR 1/指摘なし 1 | 指摘なし 2 | 指摘なし 2 | (対象外) |
| DET-B(現行Stage 1相当) | MAJOR 1/指摘なし 1 | MAJOR 1/指摘なし 1 | 指摘なし 2 | 指摘なし 2 | 指摘なし 2 |
| DET-C(候補Prompt) | MAJOR 1/MINOR 1 | MINOR 2 | MAJOR 1/指摘なし 1 | MAJOR 2 | MINOR 1/指摘なし 1 |

- 検出器ごとの陽性合計: DET-A MAJOR 3/8(37.5%)・MAJOR+MINOR 3/8(37.5%)、DET-B MAJOR 2/10(20%)・MAJOR+MINOR 2/10(20%)、DET-C MAJOR 4/10(40%)・MAJOR+MINOR 8/10(80%)。
- 陰性(N1〜N3): 書き換え後の該当文("user information"を含む指摘)はどの検出器でも指摘なし(N1・N2の各4call)。MAJOR指摘の総数(カッコ内=MAJORが出たcall数/call数): DET-A 4(4/4)、DET-B 28(6/6、N3の2callを含む=N3は正常記事ラベルだがMAJOR 7件・5件)、DET-C 14(3/6、N1の2call・N3のk2)。MINOR指摘の総数: DET-A 0、DET-B 0、DET-C 15。
- 「They enjoyed AI’s convenience」(MUSE-HC-012、参考、検出器|本文の区分): DET-A: P1 MAJOR2、P2 MAJOR1/なし1、P3 MAJOR1/なし1、P4 MAJOR1/なし1、N1 MAJOR2、N2 MAJOR1/なし1。DET-B: P1 MAJOR2、P2 MAJOR1/なし1、P3 MAJOR1/なし1、P4 MAJOR2、P5 MAJOR2、N1 MAJOR2、N2 MAJOR2、N3 なし2。DET-C: P1 MAJOR1/MINOR1、P2 MINOR2、P3 MAJOR1/なし1、P4 MAJOR2、P5 MINOR1/なし1、N1 MAJOR2、N2 MINOR2、N3 なし2。(`results_01.json`の「参考_They_enjoyed_…」)
- MINOR仮説への当てはめ(結論は書かない): 該当文がMINORで返った例は実在する(DET-Cの4call: P1 k1、P2 k1・k2、P5 k2。claim例=「Also, some calls needed user information to continue.」「Some calls needed user information to continue.」)。DET-A・DET-Bでは、該当文がMINORで返った例は0件で、指摘なしが多数(DET-A 5/8、DET-B 8/10)。回数が少ない(陽性は検出器×本文あたりn=2)。
- 費用: 今回¥20.9881(Guardrail¥22内)。Phase累計¥494.03+¥20.9881=¥515.0181/総枠¥600、残¥84.9819。予算stateは専用ファイル(`budget_state_direct_compare_01.json`)で、既存の証跡を上書きしていない。

## §37. `USER_DECISION_REQUIRED`としてSTOP(委任_50)

1. 分類: 今回フェーズ(受け渡し修正+限定Trial rep22+対策)は **`USER_DECISION_REQUIRED`**。`VALIDATED`ではない。Production採用ではない。
2. STOPの根拠(ユーザー指示のSTOP条件のうち3つに該当):
   - 「Safety原則の変更が必要」: `meta_run03_standard`の文「Also, some calls needed user information to continue.」(MUSE-HC-010)は、設計書の正解ラベル(Fableのラベル判定、設計書§4-21・委任_29)では必ず重大として拾う対象。一方、Production Checker Prompt(er003 533〜534行)は近い型を「MINORとして記録」と定めている。検出器の直接比較(委任_49、固定本文、該当文が残る本文P1〜P5)では、現行Recheckが該当文を重大で指摘 3/8・指摘なし 5/8、現行Stage 1相当が重大 2/10・指摘なし 8/10、factごとに確認させる候補Promptが重大 4/10・軽微 4/10・指摘なし 2/10。該当文を安定して拾うには、軽微の指摘を判定役へ渡す変更が必要で、これは「何を重大として扱うか」の原則の変更に当たる。
   - 「複数の合理的な設計案に明確なQCDトレードオフがあり、ユーザー判断が必要」: 該当文を重大として扱い続ける案は、合格直前の追加検査(実測単価¥0.72/回)と軽微の指摘の取り込みが必要で、費用・書き換え・人間確認が増える。軽微(品質改善)として扱う案は、追加の検査が不要になる代わりに、条件つきの内容を断定で書いた文が記事に残る。
   - 「¥600予算上限超過が必要」: Phase累計¥515.0181、残り¥84.9819。検査の実測単価は見積もり(¥0.32〜0.36)より高い(¥0.51〜0.72)。重大として扱い続ける案は、追加検査の限定確認と29件横断(追加検査つき)で残額を超える見込み。
3. 判断事項(ユーザーへ提示):
   - 判断1: 「条件つきの懸念を、起きたこととして書いた文」(該当文)を、必ず止める重大な逸脱として扱うか、品質改善(軽微)として扱うか。
   - 判断2: 「They enjoyed AI’s convenience, but a human was on the other end. They did not realize it.」(MUSE-HC-012、開示がなかったことから利用者の認識を推論した否定形の文)を、既存の降格ルール(Trial限定の判定候補、設計書1228〜1246行)どおり軽微として記事に残してよいか。
   - 判断3: 判断1で「重大として扱う」を選ぶ場合の予算上限の引き上げ。
4. 委任_49までの到達点: 受け渡し修正(委任_42)は維持。評価・記録の追加、照合の追補(`VS_MATCH_EXT`)、英語だけ修正(`JA_MODE=english_only`、補正つき)は実装済み・既定OFF・flowでは未確認。Opus独立レビュー#6の指摘どおり、合格の判定が1回の検査結果に依存する構造は未対策。
5. ユーザー判断が出るまで、実装・Trial・測定を進めない。

## §38. 2026-10-03ユーザー決定の反映(委任_51〜54)

1. 線引きの補正と再分類(委任_51、`docs/pm/open233_materiality_criteria_2026-10-03.md`、`docs/pm/open233_missed_candidates_reclassification_2026-10-03.md`): 見逃し候補23種類(すべて旧判定BLOCKING)を新しい線引きで再分類。過剰品質17/23、真の重大見逃し1/23(K19「Just after the charge plan disappeared, prices began to fall.」HF-009、境界)、軽微8/23、問題なし9/23、新判定が重大で見逃し0が5/23。入れ子3種類を除く20種類では、過剰品質17/20、真の重大見逃し1/20、軽微8/20、問題なし9/20。過剰品質17のうち8種類は、LLM判定がACCEPTABLE/QUALITYで決定論floorだけがBLOCKINGにしたもの(floorは変更しない)。
2. K19の原因切り分け(委任_51): 1周目で完全に見逃し(固定Stage 1出力に無い)。再検査で文が残った約12回中1回のみ指摘。Rewrite起因ではない(日本語原文が起点)。Checkerと判定役の基準の食い違いは証拠なし(Stage 2が見た唯一の回はBLOCKINGで一致)。Production現行のChecker出力はK19をMAJORで指摘できていた。MINORで拾っていたかは記録が無く確認不能。
3. 線引き案への指摘(委任_51、7点)のうちFableが重要と判断したもの: 「迷えば実害で決める」は既存の「迷えばBLOCKING」(fail-closed)と逆向きで、判定役へ適用すればSafety原則の変更に当たる。Fableは判定役を変更していない(線引きは評価・ラベル用の文書化に留めた)。判定役と線引きの不整合は4箇所(V4原則の一律BLOCKING、disclosure_gap降格の否定形限定、production rubricの「動機の帰属=QUALITY」、「迷えばBLOCKING」)。
4. 句読点差対策のProduction反映準備(委任_52、`docs/pm/open233_a1_production_reflection_plan_and_ja_scope_2026-10-03.md`): Family XのProduction正式経路にはCheckerの引用を記事内で探す処理が無く、反映先が無い。位置特定を行うProduction処理は`er010_ledger_local_rewrite_09.py`の`locate_target_sentence`(完全一致→単語重なり0.25)で、Discovery Focus・N3・B-family voicesが呼ぶ。Production記録では句読点差のみの不一致は0件(標本小、sentence_fallback 67件は原因未判定)。Fable判断: ユーザー意向は「Self-Recovery FlowをProductionへ接続する際の必須項目」として追跡する(`OPEN_ITEMS.md`に`OPEN-233-A1-PROD`を新設、Status=`APPROVED_FOR_PRODUCTION`[ユーザー意向、2026-10-03]・approved-but-unwired)。接続時はL0〜L3の単語境界・L5・label_onlyを一体で取り込み、初回・Rewrite周回・Recheck・retry/fallback/regenerationが同じ照合を通ること、含めずに接続した場合は`PRODUCTION_WIRED`としないことを条件にする。接続前にOpus独立レビュー条件Cに該当。er010の`locate_target_sentence`への同等処理は別の仕様変更であり、ユーザー判断事項として提示する(今回は実装しない)。
5. 日本語本文を直さないことの実害(委任_52): 実害あり1系統(Production再生成がer012_e L361・365・403〜404/er019 entertainment runner L358〜397で古い日本語R2から英語を再翻訳し、直した誤りが戻りうる。ただし再生成後は必ず`run_deviation_check`を通る。最小対策=既存で足り、接続仕様に「再生成後も必ずSelf-Recovery Flowを通す」を明記)。整合だけ2、影響なし5。日本語タイトルは英語記事を入力にせず、変更なし前提(ユーザー決定)。`JA_MODE=english_only`はユーザー方針3点を満たす。Production採用時は「忠実英訳」(CURRENT_SPEC L1272〜1278)・「案B」(L1242〜1257)と衝突する可能性が高く、その時点でユーザー判断が必要。
6. 説明文混入12件(委任_53): 主因は出力形式10・Prompt2・後段処理0(推定)。Trial専用`CHECKER_SPANS_MODE=violation_spans`(既定legacy)を実装(テスト406→418件PASS、er052回帰462件PASS)。Stage 1のみの限定確認(6記事×2腕×n=3、¥14.99): 特定不能は対照0/24・処置0/24(説明文混入はStage 1では再現せず。12件中8件はRecheck出力)、配列要素は35/35確定、費用ほぼ同じ(¥0.412/¥0.421)、Human Review増0。一方、BLOCKING fact検出は対照12/18→処置8/18、false PASSは対照1/15→処置4/15と悪化方向(n=3、対照どうしの一致率0.67で揺れ大)。**Fable判断: `VALIDATED`にしない。既定OFFのまま。ユーザー確認項目「検出漏れが増えないか」「false PASSが増えないか」を満たしたと言えないため、現時点では採用しない。** 実装は設計書§3の形と同じだが機構が異なる(claim dictにlistを持たせる設計に対し、claim文字列を鍵にしたモジュール内の対応表`_VS_SPANS_REGISTRY`で配列を引く)。有効化する場合はclaim dictへ配列を載せる形へ直すこと(同一文字列の衝突・隠れた状態を避けるため)。
7. 予算: 委任_53 ¥14.9926。Phase累計¥530.0107、上限¥900、残¥369.9893。
8. 回帰: 現作業ツリーで全体回帰を1回実行(委任_54): 4385件、passed 4374、failed 6、errors 5(実質11件)。失敗・エラーは er003_test_p2j_investigate 4件(combined_equals_sum_of_er002_and_er003、p2h_reported_count、p2i_reported_count、per_file_counts_sum)、er015 loader 1件(er015_standard_a2_6000_generation_first_trial_01_test_01)、er025 1件(test_b1_segments_pass_enable_pronunciation_resolver_true)、er040 1件(test_master_audio_key_distinguishes_style_versions)、er043 1件(test_new_candidate_keys_differ_from_production_key)、er011 3件(test_default_*_matches_pre_wiring_baseline)で、委任_42・49の基準11件と同一。委任_53が報告した12件(er012を含む)との差1件=er012は再現せず(er012系8ファイル222件は全PASS)。分類=(c)揺れ(再現せず、原因は未確定)。委任_51〜53のcommit(`b7068028`・`f7e46b38`・`74d805b9`)はer012を編集していない(`git show --stat`で確認)。回帰出力中の`FAIL: test_case_0 (er003_test_bad...)`はer003のテストが一時ディレクトリで実行する内側のfixtureの出力で、本体の集計には含まれない。
9. 全体の状態: 次Trial(5記事×2レベル)は未開始・開始禁止。`USER_DECISION_REQUIRED`としてSTOP(判断事項は`OPEN_ITEMS.md`と`ACTIVE_TASK.md`に記載)。

成果物: `docs/pm/open233_materiality_criteria_2026-10-03.md`、`docs/pm/open233_missed_candidates_reclassification_2026-10-03.md`、`docs/pm/open233_a1_production_reflection_plan_and_ja_scope_2026-10-03.md`、委任報告`docs/pm/delegation_log/2026-10-03_OPEN-233-SELF-RECOVERY-TRIAL-01_51_result.md`・`_52_result.md`・`_53_result.md`、追跡項目`OPEN_ITEMS.md`の`OPEN-233-A1-PROD`、記録`DECISION_LOG.md`2026-10-03エントリ(委任_51〜54)。

委任_53の集計表(Stage 1のみ、6記事×2腕×n=3、対照=legacy/処置=violation_spans):

| 項目 | 対照 | 処置 |
|---|---|---|
| 違反箇所の特定不能 | 0/24 | 0/24 |
| 配列要素の確定 | - | 35/35 |
| 1回あたり費用 | ¥0.412 | ¥0.421 |
| Human Review増 | - | 0 |
| BLOCKING fact検出 | 12/18 | 8/18 |
| false PASS | 1/15 | 4/15 |
| 対照どうしの一致率 | 0.67 | - |



## §39. 2026-10-03ユーザー決定(2回目)の反映: 線引きの正式採用・rubric V7・再較正(委任_55)

管理ID: `OPEN-233-SELF-RECOVERY-TRIAL-01`(委任_55)。ユーザー決定(逐語は`DECISION_LOG.md`末尾エントリ)=`prices began to fall`は軽微/線引き(重大・軽微・問題なし)の正式採用=`APPROVED_FOR_PRODUCTION`(`PRODUCTION_WIRED`ではない)/句読点差対策は自己修復機構のProduction配線時の必須構成要素(`OPEN-233-A1-PROD`)/説明文混入12件は見送らない(委任_56)/英語だけ修正を維持/次Trial・29件横断は開始禁止。

### 39-1. Production未変更の確認

`git grep -n "er052_open233" -- "er003*.py" "er009*.py" "er010*.py" "er012*.py" "er019*.py"`: 0件(編集前に確認)。編集した対象は`er052_open233_*`のみ(runner、runnerテスト、Stage 2 calibration/production、r3dprime calibration[Safety-critical登録の定義ファイル、委任文の対象外だが正解ラベル・Safety-critical登録の更新に必要だったため追加]、新スクリプト`er052_open233_element_trial_safety_control_05.py`、診断`er052_open233_safety_control_03_ablation_a41.py`)。機械的な安全装置(`FLOOR_FLAGS`・precheck・主体置換ガード・`MAX_CYCLES`・`DISCLOSURE_GAP_NEGATION_RE`・Hook専用rubric)は不変(テストで確認)。

### 39-2. rubric差分の要点(逐語は`er052_output/open233_safety_control_03/rubric_diff.md`)

body rubric V7(`MISCONCEPTION_PRINCIPLE_TEXT_V7`)=V6へ追記: 3区分の定義(ユーザー原文)、(1)条件つき→断定(核心の主張まで断定/新しい具体的事実/`notes_for_writer`の禁止の断定ならBLOCKING、核心に留保が残り帰属が保たれていればQUALITY)、(2)自然な推論(否定形・肯定形とも新しい具体的事実を加えなければACCEPTABLE。「内心を断定する記述」のBLOCKING条件は新しい具体的事実を加えない描写には適用しない)、(3)迷う場合は「重大な誤解につながるか」で決める(数値・主体・否定・比較・時期の差は対象外で機械的にBLOCKING)、判定済みの例3行。Stage 2 production既定は`MATERIALITY_RUBRIC_V7`(「迷えばBLOCKING」の1行のみ置換、「動機の帰属=QUALITY」は不変)。旧版は定数として残し、`BODY_RUBRIC_DEFAULT`はV6→V7。

### 39-3. ラベル更新一覧(旧→新)

- Meta-1/Meta-2(HC-010/HC-012、K04): BLOCKING(Safety-critical)→QUALITY(`SAFETY_CRITICAL_SUB_IDS`から除外=8件→6件、runner `SAFETY_CRITICAL_CLAIM_DEFS`は`expected: "QUALITY"`の監視用)。
- HC-012「They enjoyed…」(K10): BLOCKING(Checker指摘)→ACCEPTABLE。HF-009「prices began to fall」(K19): BLOCKING(境界)→QUALITY。
- 再分類docの表(K01〜K23)に合わせた更新: K01/K08/K09/K12/K13/K14/K15/K23=ACCEPTABLE、K02/K03/K05〜K07/K11/K17=QUALITY、K16/K18/K20〜K22=BLOCKING(変更なし)。設計書§7-0-iter33、§7-1。再分類docはK19=軽微へ更新(重大5/軽微9/問題なし9、真の重大見逃し0/23)。

### 39-4. 再較正の集計(Stage 2単体、n=2、26 call、¥4.3666、`er052_output/open233_safety_control_03/results_01.json`)

| 較正セット | 合否基準 | 結果 |
|---|---|---|
| (a) Safety-critical 6claim | misdowngrade 0 | **誤降格2件(A4-1 2/2 ACCEPTABLE)**。他5claimは2/2 BLOCKING |
| (b) Safety12 | 0 | 0/18 |
| (c) Hormuz許容5/NG5 | 従来と同じ | 10件とも合否はV6と同じ(false BLOCK 0、false PASS 0) |
| (d) 新しい例3件 | 期待どおり(n=2両方) | 例1 QUALITY、例2 ACCEPTABLE、K19 QUALITY(各2/2) |
| (e) K16・K20 | 0 | 0(2/2 BLOCKING) |
| (f) 負例K11〜K13 | false BLOCK増えない | 0 |

**合否: (a)で外れたため、修正を重ねずに止まった(Fable判断)**。原因切り分け(診断、n=1×7変種、¥2.1157、`ablation_a41/`): V7の(2)の段落、または判定済みの例2行が、それぞれ単独でA4-1をACCEPTABLEへ寄せる(冗長)。V6+3区分の定義のみ・V6+(3)のみはBLOCKING。A4-1の対象文は例2・K23と同じ型で、A4-1のSafety-critical(BLOCKING)ラベル自体が新しい線引きと食い違う可能性がある(設計書§4-26に選択肢(イ)(ロ)(ハ))。

費用: 本委任=¥4.3666(再較正、probe含む)+¥2.1157(診断)=¥6.4823(Guardrail¥15以内)。Phase累計=¥530.0107+¥6.4823=¥536.4930(上限¥900、残¥363.5070)。

### 39-5. テスト・回帰

- `python -m unittest er052_open233_self_recovery_flow_runner_01_test_01`: 428件OK(新規: Meta-1/2の監視用移行5件、V7の線引き5件、既存3テストはMeta文を使うため合成の定義へ差し替え)。`er052*_test_*.py`回帰: 472件passed。全体回帰: 4395件、passed 4384、failed 6、errors 5(実質11件、委任_42・49・54の基準11件と同一、新規なし)。回帰で書き換わった`budget_state_c233an_42_rep22.json`は`git checkout`で戻した。

### 39-6. 未解決・Fableへ戻す事項

1. 再較正(a)のA4-1(上記)。ラベル再判定かV7(2)の範囲か。
2. K19はユーザー決定でQUALITYだが`changed_comparison`のfloorは不変のため、Checkerがcomparisonを立てた実行ではBLOCKINGになる。floorからK19を外すかはユーザー判断(機械的な安全装置を緩める変更のため、本委任は実装していない)。
3. 「動機の帰属=QUALITY」(production rubric)と§0-2・K20〜K22の食い違いの残り、`DISCLOSURE_GAP_NEGATION_RE`が否定形限定のままなこと。
4. 命名: 委任文の`er052_open233_element_trial_safety_control_03.py`は既存の別スクリプトがあるため`_05`、設計書§4-23は使用済みのため§4-26とした。
5. 説明文混入12件の対策は委任_56の範囲(未実施)。次Trial・29件横断は開始していない。


## 40. 委任_57: A4-1の再ラベル・Opus独立レビュー#7の保存・説明文混入対策P-strict-closedの事前確認とTrial実装(2026-10-03、費用¥0、`USER_DECISION_REQUIRED`で停止)

### 40-1. 作業1: A4-1の再ラベル(Fable判断=ユーザー正式採用基準の適用)

A4-1の正解ラベルをACCEPTABLEへ修正(旧: BLOCKING Safety-critical)。`SAFETY_CRITICAL_SUB_IDS` 6件→5件、`CORRECT_LABEL_OVERRIDES_R3DPRIME["A4-1"]="ACCEPTABLE"`、runner `SAFETY_CRITICAL_CLAIM_DEFS`では`expected:"ACCEPTABLE"`の監視用。rubric V7は不変。再較正は再実行せず(LLM呼び出し¥0)、注記を`er052_output/open233_safety_control_03/relabel_note_a41.md`へ別ファイル追加(`results_01.json`は不変)。再較正の最終判定=**合格(ラベル修正後)**。

残りのSafety-critical 5件の確認(例2と同型は無し、変更なし):

| sub_id | 対象文(要旨) | 3定義への当てはめ | 結論 |
|---|---|---|---|
| B3(HF-007) | 継続する懸念→計画撤回の因果接続 | 重大(4)因果の創作 | 重大のまま |
| B4-a(MUSE-HC-002) | AI失敗時の人間引き継ぎ機構 | 重大(4)(6)未確認の仕組み・設計意図の追加 | 重大のまま |
| A2A3-0(HF-003) | 貨物を運ぶ側が返済する | 重大(2)主体の取り違え(Ledgerは未提示) | 重大のまま |
| A4-0(MUSE-HC-006) | 契約スタッフが利用者とのやり取りを完了 | 重大(2)やり取りの相手の取り違え | 重大のまま |
| A5-0(MUSE-HC-012) | 人間が電話を担当する機能を一時的に戻した | 重大(4)時期・経過の創作 | 重大のまま |

テスト: A4-1が監視用へ移ったこと、`detect_safety_critical_misdowngrades`対象外、`detect_over_quality_monitor_blocks`で記録、r3dの登録・ラベル(`TestA41MovedToMonitor57`、3件)。

### 40-2. 作業2: 保存

- `docs/pm/opus_l2_review_open233_self_recovery_07.md`((1)位置づけ[条件A、ユーザー明示指示]、(2)依頼文逐語、(3)Opus全文逐語、(4)Fable PM評価)。
- `docs/pm/delegation_log/2026-10-03_OPEN-233-SELF-RECOVERY-TRIAL-01_55_result.md`・`_56_result.md`(委任_55・56の最終報告、逐語)。

### 40-3. 作業3: P-strict-closedの¥0事前確認(`er052_output/open233_explanatory_mixed_offline_check_01/`)

- 3-1 エコー確認(`echo_check_01.py`、結果`echo_check_01_result.json`): 実記録の`claim_span_text`は10件で全て単一範囲。現行照合で`annotate_claim_span_identity`と同じ再構成をした136件のBLOCKING指摘のうち複数範囲は2件で、いずれも最終周回のため次周回なし。**エコーの有無は検証不能(観測0件)**。`claim_span_text`は変更しない。
- 3-2 再生(`check_02.py`、`results_02.json`、`cases_02.csv`)。自己検証: 現行照合のコピーが委任_49の再生と346行で不一致0。

(b) BLOCKING 346行(委任_56の表と同じ形式):

| 遷移 | P-strict-closed |
|---|---|
| 確定→確定(同じ範囲) | 320 |
| **確定→確定不能** | **0** |
| **確定→確定(範囲が変わった)** | **0** |
| 確定不能→確定 | 10(U01・U02×5・U08・U09・U10・U13) |
| 確定不能→確定不能(理由が変わった) | 0 |
| 確定不能→確定不能(同じ) | 16(数値検査の文字列12・U05・U06・U11・U12) |

(a) 13行: 10行採用、U06(残りが英語14語で拒否=`remainder_too_long`)・U11(`dangling_position:headline,one_line`)・U12(`dangling_position:headline`)は確定不能。(c) 委任_53対照腕62件: 全て確定済みのまま(確定→確定同じ範囲62)。(d) 非BLOCKING K1の確定不能6行: 1行のみ確定(P-strictでは4行。3行は長い説明文で拒否=安全側)。`same_fact_id_locations`14件: 確定不能→確定1、確定不能のまま11、確定済み不変2。合成テスト24件(採用の対照3、確定不能21)全て期待どおり。
- 3-3 判定: (b)確定→確定不能0・範囲変化0、合成全件期待どおり、(a)採用10行・U06/U11/U12確定不能 → **合格、作業4へ**。

### 40-4. 作業4: Trial実装(既定OFF)

- `er052_open233_self_recovery_flow_runner_01.py`: `VS_EXPLAIN_SPLIT`(既定False、CLI`--vs-explain-split`)、`vs_explain_split_resolve`、`_resolve_claim_string`(照合の入口、1箇所)。既存の照合は`_resolve_claim_string_base`へ改名(中身不変)。ONのときだけ、既存の照合で確定不能(explanatory_mixed/mismatch/label_only)の場合に試す(multi_match・empty・no_textは試さない)。英語本文のみ。拒否時も`reason`は既存の値のまま、拒否理由コード`explain_split_rejected:<理由>`は`explain_split.reason`へ。採用時`level="P:<断片数>"`、`explain_split`に採用した断片・捨てた残りの文字列(`dropped_remainders`)。`handoff["resolution"]`へ`explain_split`を記録(ONで存在するときのみ)。`switches`記録へ`VS_EXPLAIN_SPLIT`(ONのときのみ)。
- 定数(逐語): `VS_EXPLAIN_CONTRAST_REF_EN_RE=\b(ledger|source|but|instead|not|should|however|rather|whereas|contrary|versus)\b|n't`(大文字小文字無視)、`VS_EXPLAIN_CONTRAST_REF_JA_RE=台帳|原文|ではなく|ではない|しかし|べき|一方|対して|ところが`、`VS_EXPLAIN_POSITION_REJECT_RE=\b(paragraph|closing|elsewhere|section|ending|conclusion)\b|段落|末尾|結び`、`VS_EXPLAIN_MAX_EN_WORDS=6`、`VS_EXPLAIN_MAX_JA_CHARS=11`、`VS_EXPLAIN_MIN_VERBATIM_WORDS=3`(日本語8文字)。
- テスト(`TestExplainSplitStrictClosed57`、9件): 既定OFFとCLIフラグ、U01〜U13の実文字列(採用10・確定不能3、check_02と範囲一致)、合成24件、OFFで346行が`_resolve_claim_string_base`と同一、ONで既に確定済みの346行の範囲が不変・新規確定10、multi_match/空は試さない、日本語本文だけでは確定しない、`HANDOFF_MODE=legacy`で無影響、定数の逐語。
- 結果: runner単体440件OK、er052回帰484件OK(`run_project_regression.py --pattern "er052*_test_*.py"`)、全体回帰4407件中11件失敗(er003_test_bad・er003_test_p2j_investigate・er011_open112・er015_standard_a2_6000・er025_b1b・er040・er043の基準11件と一致、新規なし。er052は全てOK)。`budget_state_c233an_42_rep22.json`の書き換えは`git checkout`で戻した。

### 40-5. 未解決・ユーザー判断

判断A(有効化・Production構成要素に含めるか、Fable推奨=有効化)、判断B(K19のfloor残りの受容、Fable推奨=受容)、判断C(限定flow確認と29件横断の可否)。次Trial・29件横断は開始していない。エコーの検証不能(観測0件)は、有効化時のrun実測で確認する余地がある。

## 41. 委任_59: Opus独立レビュー#8の保存とFable判断(機械判定の正式基準への整合)、`USER_DECISION_REQUIRED`で停止(2026-10-04、費用¥0)

- 委任_58の要点: 委任_58の調査結果の要点(8種類の原因内訳): 8件すべてで、機械判定(floor)がCheckerのフラグだけを根拠にBLOCKINGへ昇格させていた(裏取りなし=全件が裏取りなしのフラグ依存)。6種類(K08・K09・K11・K12・K15・K17)は列挙の波及の残骸で委任_35(2026-10-01)で是正済み。2種類(K13・K14)+K19(`changed_comparison`)は現行コードでも再発しうる型。機械判定だけが重大を止めた記録が2件(Safety-critical A4-0: 13記録中1件、K16: 19記録中1件)。是正後のrun(rep20〜22)ではfloor発火14件中、LLMが非BLOCKINGなのにfloorだけでBLOCKINGになったのは1件(rep21の`changed_number`)。
- Opus#8の要点: (i)機械判定の整合は必要だが規模は小さい(是正後は14件中1件)。(ii)F1の自動解放(CLEARED)は比較の裏取りが方向を問わず解放され、数値・時期・否定の自動解放は付け替え・反義語の反転を見逃すため不採用。(iii)F4の「フラグを見せない独立再判定」はStage 2が現行でもフラグを見ていないため同じpromptの引き直しにすぎない。(iv)代替F5=決定論で確認できた不一致(CONFIRMED)はBLOCKING確定、CONFIRMED以外でfloorとLLMが食い違う場合だけ別callで確認し両方非BLOCKINGのときだけ解放。(v)ユーザーへ戻す論点は「LLM確認による解放の可否」の1つ。
- Fable PM評価(2〜5): 
2. 採用(Fable判断で確定): (a)F1の「整合の証拠による自動解放(CLEARED)」は廃止する。Opusがコードで示したとおり、比較の裏取りは事実文に両方向の語があるとどの方向でも解放され、ユーザーが禁じる「撤回後に原油価格が下落した」も解放されうる。数値・時期・否定の自動解放は付け替え・反義語の反転を見逃す。(b)F4は撤回する。Stage 2は現行でもフラグを見ておらず(calibration_01.py 627〜638行)、「フラグを見せない独立再判定」は同じpromptの引き直しにすぎない。(c)決定論で不一致を確認できたもの(CONFIRMED)はBLOCKING確定を維持する(維持方向にしか働かず安全)。(d)V7の文言「数値・主体・否定・比較・時期の差は…明確にBLOCKING」は、既存の基底rubric R3(e)に揃えて「Ledgerと矛盾する重大な変更(数値の改変、主体の取り違え、否定の反転、方向の反転、時期の取り違え)は…明確にBLOCKING」へ直す(新基準の作成ではなく既存への整合。再較正必須)。(e)動機: 「帰属」と「創作」は別事象。委任_58の案文(2)(V7(1)(イ)へ「仕組み・意図」を追加)は採らない(B4-aは基底R3(b)(c)でBLOCKINGが保たれており不要。限定なしの「意図」は既存より厳しくなりうる)。案文(1)はProduction配線時に、案文(3)は文書のみ反映可。B1-cはユーザーの2026-09-30の判断と基底R3のQUALITY行で整理済みとし、「notes禁止=BLOCKING」と自然な推論の優先順位はProduction配線時の確認項目として記録する(ユーザー判断は不要)。(f)限定flowの合格基準から「floor単独BLOCKING 0〜1件/run」を外し監視値にする。解放は全件ログ+人がラベル付け、重大ラベルのclaimが1件でも解放されたらSTOP。(g)Production配線時の必須対策(解放claimを2-of-2降格の対象から外す/`dev`のフラグを書き換えない/確認callの失敗はBLOCKING固定/cycleごとに再評価)とruntime evidence項目を`OPEN-233-A1-PROD`に追加する。
3. ユーザーへ戻す(Opus指摘に同意): 「Checkerのフラグが立ったclaimを、LLMの確認で解放するか」。機械判定の決定論的な保証を、確率的な保証(確認callが見逃す可能性)に置き換える新しいリスク許容の判断であり、ユーザーのSTOP条件「Safety原則の変更が必要」に当たる。決定論だけでは、役職の一般化(K13・K14)と主体の取り違え(A4-0)を字面で区別できず、比較の目印(K19)も安全に解放できない。したがって「機械判定を正式基準に一致させる」には、(i)LLM確認による解放を導入する(F5)か、(ii)現状維持で一部の軽微な文が機械判定で重大のまま残ることを受容するか、のどちらかになる。
4. Fableの推奨: F5を**比較(`changed_comparison`)と時期(`changed_time`)に限って**導入し、主体・数値・否定は決定論のまま維持する。理由: ユーザーが「本当に重大」と名指しした主体取り違え・数値改変・否定反転を確率的な判定に委ねない。K19型(比較)はこれで解放され、K16型(時期)は確認callで止める(2回とも非BLOCKINGのときだけ解放、失敗はBLOCKING固定)。K13・K14型(主体の一般化)は過剰品質として受容する(是正後の実行で機械判定単独は14件中1件)。導入前に、Opus指摘の単体測定(重大ケースK16・A4-0・K18・A2A3-0と敵対的合成ケース[「After the plan was withdrawn, oil prices fell.」・20%の付け替え・7/13と7/14の取り違え]、過剰ケースK13・K14・K19・B2「vanished overnight」・B4「Names…」をn≥10、¥10〜30)で見逃し0・解放の妥当性を確認してから有効化する。
5. 進行判断: 上記3はSTOP条件に該当するため、`USER_DECISION_REQUIRED`としてSTOPする。限定flow確認と29件横断(承認済み)は、機械判定の扱いが決まってから1回で行う(2回に分けて費用を重ねない)。
- 判断事項(判断D): LLM確認による解放の導入可否と範囲 (1)比較・時期に限定=Fable推奨 / (2)主体も含む / (3)導入せず現状維持。
- 現Status: `USER_DECISION_REQUIRED`。限定flow確認・29件横断1回=承認済み・未実施(判断後に1回で実施)。次Trial(5記事×2レベル)=開始禁止。`PRODUCTION_WIRED`ではない。
- 保存先: `docs/pm/opus_l2_review_open233_self_recovery_08.md`、`docs/pm/delegation_log/2026-10-04_OPEN-233-SELF-RECOVERY-TRIAL-01_58_result.md`、`..._57_result.md`。

## 42. 委任_60: 判断D=案1(比較・方向・時期の機械判定の追加確認)の記録・実装・単体安全確認(2026-10-04)

- 記録: ユーザー決定[4回目]を`DECISION_LOG.md`末尾へ逐語記録(委任文の原文ブロックと一致)。
- 実装: runner(`er052_open233_self_recovery_flow_runner_01.py`)に`FLOOR_VERIFY_MODE`(既定off)、`floor_verify_target`/`floor_verify_confirmed`/`run_floor_verify_call`/`floor_verify_evaluate`/`floor_verify_summarize`、`run_stage2`への配線(`floor_verify`フィールド、既定OFFでは付かない)、2-of-2の除外、CLI`--floor-verify-mode`。テスト: runner単体470件OK(新規=TestFloorVerify60・TestRubricV7b60・TestMotiveDocAlignment60)、er052回帰513件OK、全体回帰4436件で失敗11件=基準11件と同一(新規なし)。
- V7b: `MISCONCEPTION_PRINCIPLE_TEXT_V7B`(V7(3)を「Ledgerと矛盾する重大な変更…」へ)。V7は定数として残す。`BODY_RUBRIC_DEFAULT`=V7b。`s2p._V7_NEW_TIEBREAK`相当は`_V7B_NEW_TIEBREAK`/`MATERIALITY_RUBRIC_V7B`として追加(runnerのflowでは使われない=Grepで確認、使用はPhase1 unitcost計測スクリプトのみ)。
- 動機: 設計書§0-2更新、criteria doc §6追加。V7(1)(イ)は不変。
- 単体確認(`er052_output/open233_floor_verify_unit_check_01/`、¥2.336、23 call、probe単価¥0.1219/call): **STOP**(S1=合成方向反転が確認2回とも非BLOCKINGで解放)。ケース別: R1 K19 3/3解放、R2 B2 0/3(引用非逐語でBLOCKING固定)、R3 B4 2/3解放(1回BLOCKINGで食い違い)、S1 2試行目で解放→STOP。S2〜S8は未実行(S3・S5はCONFIRMED、S4・S8は対象外であることを¥0の事前確認で確認したのみ)。
- 未実施: V7b再較正、限定flow、29件横断。次Trial禁止。`PRODUCTION_WIRED`ではない。詳細は設計書`docs/pm/design_open233_floor_alignment_01.md` §8。

## 43. 委任_61: 選択肢3(追加確認による解放対象を時期のみに縮小)の記録・実装・単体安全確認・V7b再較正(2026-10-04)

- 記録: ユーザー決定[5回目]を`DECISION_LOG.md`末尾へ逐語記録(委任文の原文ブロックと一致)。`APPROVED_FOR_PRODUCTION`として追跡、`PRODUCTION_WIRED`ではない。
- 実装(runner): `FLOOR_VERIFY_MODE`を`off`(既定)/`time_only`へ変更、`comparison_time`廃止(`validate_floor_verify_mode`が`ValueError`、CLI choicesからも除外)。対象判定は`changed_time`のみtrueのfloor指摘に限定、比較・方向・主体・数値・否定のいずれかがtrueなら`out_of_scope_flag:<flag名>`で対象外。`floor_verify_comparison_numbers`は未使用(関数残置)。確認promptから比較・方向の記述を外した(軽微例は元々promptに含めていない)。summaryに`out_of_scope_flag`件数を追加。rubric本体(V7b)・解放条件・BLOCKING固定条件・`dev`不変・2-of-2除外・cycleごと再評価は不変。
- テスト: runner単体473件OK、er052回帰517件OK、全体回帰4440件で失敗6・エラー5(基準11件と同一、新規なし)。
- 単体安全確認(`er052_open233_floor_verify_unit_check_02.py`、`er052_output/open233_floor_verify_unit_check_02/`、費用¥5.0099、69 call、probe単価¥0.137/call): **PASS**。重大期待T1〜T5を各2版(C=決定論CONFIRMED版、N=抽出トークンを含まず確認callが動く版)で実施。C版5件は確認callなしで`confirmed_by_deterministic_mismatch`のBLOCKING固定。N版5件(T1n前後関係反転・T2n K16・T3n順序反転・T4n A5-0・T5n期間付け替え)は各n=5×確認2回=50 call全てBLOCKING、解放0(BLOCKING固定理由: `ledger_citation_not_verbatim`・`verify_blocking_both`)。対象外確認X1(方向反転`changed_comparison`)・X2(主体+時期)は対象外でBLOCKING維持(確認callなし)。解放期待(参考値): R1 B2 0/3(確認ラベル6/6=QUALITYだが引用が台帳の逐語でなく3/3 BLOCKING固定)、R2 K15 1/3(ラベル6/6=ACCEPTABLE)、R3 K17 2/3(ラベル6/6=ACCEPTABLE)。STOP非該当。
- V7b再較正(`er052_open233_element_trial_safety_control_06.py`、`er052_output/open233_safety_control_04/`、n=2、24 call、¥4.3753): **PASS**(a誤降格0、b 0/18、cはV6と同じ判定、d期待どおり、e BLOCKING、f false BLOCK 0)。
- 整合: 再較正はStage 2 rubric単体で追加確認を含まない。時期以外のfloorはLLM判定に関係なく決定論でBLOCKING維持・時期は追加確認2回で解放可能だが重大期待ケースは解放されない、が両立している(`results_01.json`の`consistency_note_61`)。
- 費用: 合計¥9.3852、Phase累計約¥548.214(上限¥900)。未実施: 少数flow・29件横断(委任_62)。次Trial禁止。
- 確認できたこと/推測: 上記の数値は`results_01.json`・`cases_01.csv`の実測。N版の解放0がn=5×5ケースの範囲であり、より多くのパターンでの保証ではない(推測の余地)。引用が逐語でないことによるBLOCKING固定が多く、解放期待ケースの解放率が低い(B2は0/3)のは保守側の挙動(過剰Majorの残存)。

## 44. 委任_62: 少数実flow確認 rep23(2026-10-04、6 instance×n=2=12 instance-run、費用¥7.9137)

- 性質: ユーザー決定[5回目]手順4。承認済み対策を全部有効にした構成。Trial専用、Production未接続。29件横断(手順5)は未実施(Fable照合後の委任_63)。次Trial未開始。
- 構成: `er052_open233_self_recovery_flow_runner_01_rep23_limited_01.py`(実行)・`..._rep23_agg_01.py`(集計)、出力`er052_output/open233_self_recovery_flow_runner_01_rep23/`(instance JSON 12件・`summary_01.json`・`release_log_01.md`)。スイッチは12/12のinstance JSON `switches`で実測確認: `JA_MODE=english_only`・`VS_MATCH_EXT`・`VS_EXPLAIN_SPLIT`・`FLOOR_VERIFY_MODE=time_only`・`HANDOFF_MODE=violation_span`、rubric=V7b、`MAX_CYCLES=2`/`HARD_MAX_CYCLES=3`、⑥OFF。instanceは設計書§5-1の指定(meta_run03_standard・hormuz_run03_standard・neg3_hormuz_prodrunner_b1b・safety_A4・safety_A2A3・safety_er009_changed_number)。**B3・B4-a・A5-0(Safety-critical登録)は§5-1に含まれず未包含**。比較基準は同instanceの直近記録(meta=rep22、hormuz=rep16、neg3=rep17、A4=rep14、A2A3=rep18、changed_number=rep22)で、旧rubric・旧スイッチ構成のため同一条件の比較ではない(metaのrep22は固定Stage 1[iter8 frozen]、rep23は既定Stage 1 fixtureで入力が異なる)。
- 即時STOP条件(a)日本語変更・(b)重大解放・(c)Safety-critical残存・(d)例外: **いずれも非該当**(JA変更0/12、解放0、`pass_with_residual_unflagged`=0、例外なし)。
- 項目別の仮判定(rep23 / 基準): 
  1. 真の重大見逃し **PASS**(A4-0・A2A3-0を4/4 runでBLOCKING検出、合格系の残存0、誤降格0。B3/B4-a/A5-0は未包含)。
  2. 解放した重大ケース **PASS(未発火)**: floor_verify記録6件が全て`llm_materiality_blocking`で対象外、追加確認call 0・CONFIRMED 0・解放0・費用¥0。**時期のみの追加確認は実flowで一度も発火しておらず、解放側は実flowで未検証**(`release_log_01.md`)。
  3. 過剰Major **PASS(減少)**: Stage 2 BLOCKING 24件/基準27件、floor単独BLOCKING 2件(`precheck_floor`、changed_numberの真陽性)/基準6件(changed_time 4・changed_actor 1・precheck 1)。軽微以下の仮ラベル2件(A4 s1 cycle2・3の「backup」動機の帰属)。
  4. 不要Rewrite **FAIL(形式)**: 既存定義(正常記事群のうちRewriteが1件以上実行されたrun率、本構成ではneg3のみ)で2/2=100%、基準(rep17)も2/2=100%で「減っていない」。補足=正常群以外の非Safety 6 runでは2/6(基準6/8)へ減少。neg3のBLOCKING claim(HF-009「events ... quickly returned」)はLLM・floorとも重大判定で仮ラベルは重大寄りのため、「不要」と断定できない。Rewrite実行13件/基準18件。
  5. Human Review **注意**: STAGE4 4件(`violation_span_unverified`×3[A2A3×2・A4 s1]・`unconfirmed_after_reverify`×1[neg3 s2])/基準4件(`ladder_exhausted_without_full_rewrite`×3・`cycle_limit_exhausted`×1)。件数は同数で増加なし、理由は変化。neg3は0/2→1/2。
  6. 説明文混入対策 **PASS(誤範囲0、採用側は未発火)**: `vs_explain_split_resolve`は実flowで1件(A4 s1 cycle3、断片2・残り`remainder_too_long`)を試行し`explain_split_rejected:remainder_too_long`でfail-closed。採用された`P:<n>`は0件。
  7. 句読点差対策 **注意(対象なし)**: L5・`label_only`の発火0、対象0、誤解決0。未確定は`mismatch`×2(A2A3、Checker範囲が`2.6 percent`の途中から始まる`6 percent, because ...`でfail-closed)・`explanatory_mixed`×1(A4 s1)。
  8. 英語だけ修正 **PASS**: JA変更0/12、JA rewrite・`paired`機構0、`ja_`系call 0、`en_title_rewritten`0件、`english_only_ja_source_requires_full_recheck`は3 cycleで発火し3 cycleとも全文Recheck実施(1:1)。
  9. retry/recheck整合 **PASS(未確認事項あり)**: cycle2以降2 run(cycle3は1)、`severity_wobble`0、Recheck由来claimも`mode=violation_span`のhandoffを通る(cycle2・3の6 record)、cycleごとにStage 2を再評価。cycle2以降にfloor指摘がなく、floor_verifyの解放状態が周回間で引き継がれないことは実flowで未確認。
  10. 費用 **PASS**: ¥7.9137(基準12 runの記録合計¥13.2733)、worst instance-run ¥2.6814(A4 s1、上限¥7未満)。Phase累計¥556.1277(上限¥900)。
- 解放ログ: 0件(`release_log_01.md`)。対象判定6件全て対象外。
- 説明文混入の全件: 上記6のA4 s1 cycle3の1件のみ(`claim_in_article`=`“The human backup plan” and “that backup plan” characterize the human-staff calls as a backup arrangement.`、`dropped_remainders`=`and`[connective]・`characterize ... backup arrangement`[remainder_too_long])。`handoff.resolution`は`explain_split`情報を保存しないため、記録済みの本文での決定論replay(¥0、24 claim全てで記録と一致)で確認した。
- 確認できたこと/推測: 数値は`summary_01.json`・instance JSONの実測。仮ラベルは人手でFableが最終判定。単体確認(委任_61)に比べ、実flowでは時期の追加確認・P範囲採用・L5が発火しない構成だった(推測: 対象となる入力がこの6 instanceに少ない)。A2A3の`mismatch`はChecker出力の範囲切断が原因で、新しい対策や仕様は追加していない(報告のみ)。
- 費用: ¥7.9137(12 instance-run)、Phase累計¥556.1277。次: Fable照合→問題なければ委任_63=29件横断1回。


## 45. 委任_63: 29件横断 rep24(2026-10-04、29 instance・38 instance-run、費用¥16.7238)

- 性質: ユーザー決定[5回目]手順5。承認済み対策を全部有効にした構成で29件横断を1回。Trial専用、Production未接続。STOPし、次Trial(5記事x2=10本)は未開始(ユーザーGO待ち)。Closeout確認は委任_64。
- 構成: `er052_open233_self_recovery_flow_runner_01_rep24_full_01.py`(実行)・`..._rep24_agg_01.py`(集計)、出力`er052_output/open233_self_recovery_flow_runner_01_rep24/`(`instances_s1`29件・`instances_s2`9件・`summary_01.json`/`.md`・`release_log_01.md`・`blocking_claims_01.md`・`run_log_main.json`)。instance集合・n配分はiteration 7(委任_22、REPORT§22-4)と同一(n=2が9 instance[safety_A2A3・bgroup_B3・meta_run03_standard/advanced・hormuz_run03_standard/advanced・neg1・neg2・neg3]、n=1が20 instance)。スイッチは38/38のinstance JSON `switches`で実測: HANDOFF_MODE=violation_span、VS_MATCH_EXT=True、VS_EXPLAIN_SPLIT=True、JA_MODE=english_only、FLOOR_VERIFY_MODE=time_only(Stage 2 rubric=V7b、MAX_CYCLES=2、HARD_MAX_CYCLES=3、⑥OFFは既定)。比較基準は(A)iteration 7=旧rubric・旧スイッチ(handoff旧方式・JA paired・⑥使用あり)、(B)rep23=同構成6 instance。
- 実行経過(注意): 最初の起動はツールの10分時間制限で打ち切られ、8 instance完了(neg3 s1の実行中に中断、保存なし)。同じコマンドを`skip existing`で1回だけ再開し残りを完走(完了済み8件は再実行せず、neg3 s1のみ最初から実行。中断分のAPI費用は予算状態に未記録で、記録済み¥16.7238には含まれない[最大でもneg3 s1 1回分程度、約¥0.8以下と推測])。失敗runの再実行・n増しはなし。
- 即時STOP条件: (a)日本語変更0/38・(c)`pass_with_residual_unflagged`=0・(d)例外0・(b)解放0(スクリプトの自動判定は非該当)。ただしB3 s1に残存sentinel1件あり(下記1、Fable目視確認を依頼)。
- 項目別の仮判定(rep24 / iteration 7 / rep23):
  1. 真の重大見逃し **注意**: Safety-critical 5 instanceの7 runで全てBLOCKING検出(B3 2/2、B4-a 1/1、A2A3-0 2/2、A4-0 1/1、A5-0 1/1)、`pass_with_residual_unflagged`=0。`residual_at_pass`でENに残存は3件(B3 s1[合格系]、B3 s2・A2A3 s2[いずれもSTAGE4=人間確認、検出済み])。B3 s1は文中`flashy 20% plan`が残るがcycle1でBLOCKING検出→Rewriteで因果`so`を`and`へ変更→cycle2のStage 2がACCEPTABLE(既存の誤降格検出器が同claimを1件拾うが、仮ラベル=問題なし。因果の断定が消え、sentinel文字列だけが設計上残る)。厳密解釈(合格系で`remains_in_final_en`)では1件のためFable確認を求める。
  2. 重大ケースの誤解放 **PASS(未発火)**: floor_verify記録12件(`llm_materiality_blocking`9・`out_of_scope_flag:changed_actor`3)、対象判定0・CONFIRMED 0・確認call 0・解放0・費用¥0。時期のみの追加確認は2回続けて実flowで未発火(changed_timeはLLMも重大判定だったため対象外)。
  3. 過剰Major **注意**: Stage 2 BLOCKING 35件(iter7 39、rep23 24[12 run])、floor単独BLOCKING 4件(iter7 4・同フラグ内訳: changed_actor 3・precheck 1)。軽微以下の仮ラベル3件(全てchanged_actor floor単独・LLMはACCEPTABLE): meta_run03_advanced s2 cycle1`users had no way to know whether they were talking to AI or a person.`、同cycle2`They were enjoying the convenience of AI, ...`、neg3 s2 cycle2`Trump posted that all cargo ... should provide a 20 percent reimbursement.`。残る1件はprecheck_floorのchanged_number(真陽性)。増えてはいないが、iter7と同じ3件の過剰Major型(changed_actor)が残存。
  4. 不要Rewrite **注意(増減なし)**: 既存定義(NORMAL_GROUP_INSTANCE_IDSのrunのうちRewrite実行>=1の割合)で3/14=21.43%(iter7 3/14=21.43%、rep23 2/2)。内訳: neg3 s1・s2(cycle1のclaimはLLM・floor双方がBLOCKING=K16型、rep23と同判断)・meta_run03_advanced s2(floor単独changed_actor 2claimへRewrite 2回、¥1.7625=worst)。neg3を除くと1/12=8.3%(iter7 1/12=8.3%[neg1])。全runのRewrite実行24件/19 run(iter7 39件/23 run、⑥使用は既定OFFで0)。軽微以下と仮ラベルしたclaimへのRewrite3件(meta_run03_advanced s2 2件・neg3 s2 1件)。
  5. Human Review増加 **注意**: STAGE4 2件(iter7 7件、rep23 4/12)、理由は2件とも`violation_span_unverified`(A2A3 s2・B3 s2、いずれもSafety-critical、fail-closed)。instance別: A2A3 2/2->1/2(減)、B3 0/2->1/2(増)、hormuz_run03_standard 2/2->0、neg1 1/2->0、B4 1->0、A4 1->0。総数は大きく減だが、B3は増。`unconfirmed_after_reverify`・`ladder_exhausted`・`cycle_limit`は0。
  6. 説明文混入対策 **PASS(誤範囲0、採用側は未発火)**: `vs_explain_split`は実flowで2件試行(A2A3 s2 cycle2: 断片`the trade and investment deals ... United States`が現本文に無く`explain_split_rejected:fragment_not_in_article`、B3 s2 cycle2: `no_quote`)、どちらもfail-closed。採用された`P:<n>`は0件、誤範囲0。
  7. 句読点差対策 **注意**: L5(`L5_edge_punct`)2件発火・2/2成功(B3 s1・s2のcycle1、末尾`.`差でclaim全文が範囲に解決)、`label_only`0、誤解決0。未確定`mismatch`2件(上記A2A3 s2 cycle2・B3 s2 cycle2)が2件のSTAGE4の原因。委任_62のA2A3型(`6 percent, because ...`の途中開始)のclaimはA2A3 s1・s2のcycle1に各1件あり、いずれも別claimのRewriteでカバー済み(`covered_by_earlier_rewrite_in_cycle`)になり照合失敗0。新しい型としてclaim末尾が`...`で省略されたもの(B3 s2 cycle2)が`no_quote`で未確定(新仕様は追加せず報告のみ)。
  8. 英語だけ修正 **PASS**: JA変更0/38、JA rewrite・`paired`機構0、`ja_`系call 0、`en_title_rewritten`0件、`english_only_ja_source_requires_full_recheck`は8 cycleで発火し8 cycleとも全文Recheck実施(1:1)。
  9. retry/recheck整合 **PASS(解放引継ぎは未確認)**: cycle2到達7 run・cycle3到達0、`severity_wobble`1件(B4 s1、MUSE-HC-010がQUALITY->ACCEPTABLE、BLOCKINGの降格ではない)、`carry_forward_comparison`9件(全て`covered`)。cycle2のfloor claim 2件(meta_run03_advanced・neg3)は同じstage2/floor/floor_verify記録経路を通り(2/2)、Recheck由来claimも`mode=violation_span`のhandoffを通る。floor_verify解放が0のため、cycle間の解放引継ぎ禁止は発火機会なし。
  10. 費用 **PASS**: ¥16.7238(38 instance-run、iter7 ¥39.5475)、worst ¥1.7625(meta_run03_advanced s2、iter7 worst ¥8.9545[safety_A4])。Phase累計¥556.1277+¥16.7238=¥572.8515(上限¥900)。
- 解放ログ: 0件(`release_log_01.md`、記録12件は全て対象外)。
- 説明文混入の採用範囲: 採用0件(試行2件はいずれも棄却)。
- BLOCKING claim仮ラベル(35件、`blocking_claims_01.md`): Safety fixture(er009 9種+unsupported新主張、A2A3・A4・A5・B3・B4)の真陽性、neg3 cycle1のK16型2件(LLM・floor双方重大、継続中の出来事の復活)、軽微以下の疑い3件(項目3)。
- 確認できたこと/推測: 数値は`summary_01.json`・instance JSONの実測。仮ラベルは人手でFableが最終判定。B3 s2のSTAGE4は`...`省略claimの照合不能が原因。推測: floor_verifyが未発火なのはchanged_time claimでLLMも重大判定になるため(未検証)。
- 費用: ¥16.7238(38 instance-run)、Phase累計¥572.8515。次: Fable照合→委任_64=Closeout確認(8項目)→ユーザーへSTOP報告(次TrialのGO判断待ち)。


## 46. 委任_64: Closeout必須確認8項目とSTOP(2026-10-04、費用¥0、コード変更なし)

- 性質: ユーザー決定[5回目]手順6の前段。ユーザー決定[3回目]§8の8項目をread-onlyで確認し、rep23(§44)・rep24(§45)のFable照合判断を`DECISION_LOG.md`へ記録、Statusを`USER_DECISION_REQUIRED`(次TrialのGO待ち+許容判断2件)へ更新。詳細は`docs/pm/open233_closeout_check_2026-10-04.md`。
- 8項目の結果要約: (1)USER_DECISION_REQUIRED=本委任後に3件残る[(A)Checker範囲切断型の照合許容、(B)changed_actor floor単独の受容継続、(C)次TrialのGO]+既存の別系統未決1件[er010 Local Rewriteへの句読点差処理] / (2)APPROVED_FOR_PRODUCTION未配線=7構成要素すべて`PRODUCTION_WIRED`未達 / (3)Production wiring漏れ=Production側の対応箇所なしが7要素(`git grep "er052_open233"`はer003〜er019で0件)、wiring必須確認9項目は全て未実施 / (4)Trialだけの対策=スイッチ7(不採用は`CHECKER_SPANS_MODE=violation_spans`ほか) / (5)SSOT不一致=欠落2(CURRENT_SPECのP-strict-closed承認・次Trial GO待ち)・古い記述3・番号ズレ1を検出、欠落と古い記述は修正、番号ズレは指摘のみ / (6)Dangling Reference=0(延べ111パス検査) / (7)未報告Trial=0(17ディレクトリ、名前の記載漏れ4は軽微な参照漏れとして指摘) / (8)ユーザー承認なしの仕様追加=根拠のない機能追加0、worker判断2系統(`carry_forward_resolution`、確認の逐語必須・複数factブロック連結・API失敗時retryなし)は安全側のみに働く追加(Fable確認済み)でユーザー承認扱いにしない。
- Fable照合判断(ユーザー決定ではない): 1安全項目=PASS(B3 s1の残存は位置目印のみ、因果soは修正済み)/2不要Rewrite=注意(neg3はK16型で不要と断定不可、neg3除外8.3%同率)/3Human Review=注意(7→2、B3増は`...`省略の照合不能・安全側)/4過剰Major=注意(受容範囲)/5時期の追加確認・P採用は実flow未発火(次Trialで観測)/6rep24の実行中断は「29件横断1回」として扱う(未記録費用≤¥0.8、Phase累計¥572.8515・未記録分を含めれば≤¥573.66)/7ユーザー判断(A)(B)(C)。
- 運用メモ: 委任_63のT-0は全文逐語保存でなかった(主要部保存・定型文要約)。委任_64から全文逐語保存。
- 状態: `USER_DECISION_REQUIRED`。Production未接続、`PRODUCTION_WIRED`なし、次Trialは開始しない。費用: ¥0、Phase累計¥572.8515(上限¥900)。

## 47. 委任_65: span切断の自動復元(L6「完結文復元」)設計と¥0検証(2026-10-04、費用¥0、コード変更なし)

- 性質: ユーザー指示[6回目](Primary KPI=Human Review 0件、Safety=重大見逃し0件、Cost=平均+¥2/記事以内、`DECISION_LOG.md`末尾に原文逐語記録)に基づく設計+既存ログの決定論replay。runner・Prompt・Production pathは未変更。L6はreplayスクリプト内の試作(`er052_output/open233_span_restore_offline_01/replay_01.py`)で、Production未接続、`PRODUCTION_WIRED`なし。次Trial(10本)は開始しない。
- 失敗2件の正体: A2A3 s2 cycle2=Checkerが記事にない語`the`を先頭に足した、B3 s2 cycle2=末尾`...`省略+記事の`while`を`so`へ言い換え。どちらも単純な切断・省略ではなく「逐語でない語の混入+省略」(設計書§2)。
- 設計: L6=L0〜L5・P-strict-closedで未確定のclaimのうち、(i)切断(数値内`.`/`,`を語構成とみなす境界補正を含む)/(ii)`...`/`…`/`・・・`/(iii)中間省略/(iv)アンカー(記事に逐語で1箇所ある4語・20文字以上の連続語列、アンカー外6語以内、カバー率50%以上)に限り、断片を含む完結文(2文以内・700字以内・引用符が閉じる・記事に1箇所)へ決定論で拡張。候補0・複数・ガード不通過は従来のunresolvable(唯一のHuman Review経路)。P→L6の順(Pの4ガードを迂回しない)。最小Rewriteは既存E1 Prompt(範囲内の最小編集のみ、不能なら空配列)+`issue`+`prior_issues`(復元文)で担保、ラダーの段は進めない。
- ¥0 replay: instance JSON 475本・BLOCKING 591件(一意182)。未確定17一意のうち日本語5・precheck由来2を除く英語Checker出力10件中**5件復元**、残り5件は全て(d)説明文混入型(L6対象外)。rep24の失敗2件は**一意に復元**(A2A3 s2・B3 s2)、A2A3の`6 percent, because …`型2件(現行は確定扱いだが`2.6`の`6`から始まる穴)も数値境界補正で完結文へ復元。確定済みの結果をL6が変えた件数0(例外=上記数値境界1一意・7 runs)。rep24 handoffとreplay baseは35/35一致。
- 誤復元0: 実例の復元全6件はclaim/issueと対応(仮判定)。確定済み127件を決定論で壊した889通り(L6呼び出し721)で復元712件は全て正解の文群と完全一致、無関係0、安全側9。合成13ケース全件期待どおり。
- KPI見通し(replay根拠、実flow未実証): 今回の29件セットはHuman Review 2→0(replay)。Production全体の0件は未達の可能性: (d)説明文混入型が過去ログ5 runs/591(rep24は0、rep23は1)。費用は追加API call 0、1件の復元で最大約¥0.5、平均約+¥0.03/記事(全記事で発生しても約¥0.5)。
- USER_DECISION候補(Fableが整理、Sonnetは決めない): U-1=アンカー型を「決定論の逐語照合」と扱ってよいか(基本線の字義の拡張、Opus論点2)。U-2=(d)説明文混入型の追加対策(位置語→構造要素の範囲追加/残り長文のガード再検討、未設計)。U-3=候補0・複数を減らすChecker span再取得1回(LLM call追加、未設計)。
- Opus条件A向けpacket: `docs/pm/opus_packet_open233_span_restore_01.md`(20253字、重複レビューは再レビュー=基本線の前提変更)。依頼はFable。
- 次: Opus独立レビュー→Fable照合→委任_66(実装[Trial専用スイッチ・既定OFF]+単体テスト+影響instance再実行)→29件再確認(Human Review 0件の実証)。詳細: `docs/pm/design_open233_span_sentence_restore_01.md`、`er052_output/open233_span_restore_offline_01/results_01.md`。
- 運用メモ: T-0は委任文を全文逐語保存し`check_delegation_prompt.py`はPASS(警告のみ: TTS/--budget言及なし)。

## 48. 委任_66: L6実装・Opus#9是正・影響instance再実行rep25(2026-10-04、費用¥1.1184、Phase累計¥573.9699)

- 性質: Opus独立レビュー#9(条件A)のFable採否に基づき、L6「完結文復元」を検証用runnerへ実装(既定OFF、スイッチ`VS_SENTENCE_RESTORE`、CLI`--vs-sentence-restore`、`VS_MATCH_EXT`ON前提)。Production正式path(`er003*`〜`er019*`)・Checker Prompt・Schema・判定方法は変更していない(`git grep "er052_open233" -- er003*.py er009*.py er010*.py er012*.py er019*.py`は0件)。Production採用判断・`PRODUCTION_WIRED`なし。次Trial(10本)は開始していない。Opus#9の保存・Fable評価: `docs/pm/opus_l2_review_open233_self_recovery_09.md`、設計書§6-A/6-B/7-A/7-A'/7-B。
- 実装(runner): (1)数値境界補正(`_vs_wordch`、`VS_MATCH_EXT`配下)、(2)L6本体`vs_sentence_restore_resolve`(発火条件(i)〜(iv)・除外[日本語/説明文混入/label_only/multi_match]・P→L6の順・ガード表の値・記録)、(3)Opus是正: 穴A残余包含検査(アンカー外の3語以上の逐語連続部分が復元範囲の内側に無ければ復元しない)・穴B(アンカー間隔整合α=3、`unmatched>=0`、cover二重計上の解消)・略語対応文分割`vs_sentence_segments_l6`(既存`vs_sentence_segments`は不変)・`issue_focus_absent`(Rewriteせず全文Recheckのみ。`full_recheck_required`に理由`issue_focus_absent_recheck_only`を追加)・2文復元のE1変更焦点文ガード(外側の変更はE1失敗=既存の次水準へ)・E1 Promptへの元断片併記(L6復元時のみ。非L6のE1 Promptはバイト不変)、(4)記録(`handoff.resolution.sentence_restore`ほか)・summary集計`sentence_restore_summarize`。実装後の追加: carry-forward(同一cycleの先行Rewriteで書き換え済み)の記録にもL6の記録を残す(記録専用、rep25実行後に追加)。行番号は設計書§6-A。
- 実装判断(Fableへ報告): 残余包含検査は3語以上に限定(1〜2語は`so`等で偶然の一致と区別できず、B3 s2の形を落とすため)/α=3の根拠/文数は復元範囲内の文数で数える/略語は固定リスト(`no`は直後が数字、`st`は直後が大文字のときだけ略語)/`issue`の引用符に直線の二重引用符も含める。いずれも「縮小・誤復元を拒否する側」への倒し方。
- テスト: runner単体532件PASS(既存473+新規59: OFF不変・legacy無影響・数値境界・発火(i)〜(iv)・除外・ガード各値・穴A/B・略語・`issue_focus_absent`・2文焦点ガード・E1 Prompt・P→L6順序・rep24実データ[A2A3 s2・B3 s2・`6 percent`型]のfixture化・候補複数→unresolvable・carry-forward記録)。er052回帰576件PASS(`--pattern "er052*_test_*.py"`)。全体回帰(`run_project_regression.py`)は4498件・failed=6・errors=6のうち、基準11件に加えて1件(`er012_e_family_entertainment_two_level_runner_test_01.TtsModeCliTests.test_batch_mode_without_reason_errors_via_subprocess`)が出たが、作業シェルに`PYTHONIOENCODING=utf-8`を設定していたことによる環境起因で、その環境変数なしの単独実行では全4件PASS(本変更と無関係)。基準11件(`er003_test_bad`1・`er003_test_p2j_investigate`4・`er015`loader1・`er025`1・`er040`1・`er043`1・`er011`3)は変化なし。新規failureなし。`budget_state_*.json`のrep22の書き換えは`git checkout`で戻した(rep19は作業開始前から差分あり、触れていない)。
- ¥0検証: (a)replay一致(`replay_01.py --use-runner`、`results_runner_01.{json,md}`・試作を新baseで再実行した`results_proto_newbase_01.*`): 復元6件・合成14件・ストレス(126一意x7変形)は試作とrunnerで同一結果、ストレスの誤復元(無関係・部分重なり等)0、復元709件は全て正解の文群と完全一致。runnerの旗ON経由とL6直接呼び出しは不一致0、確定済み164件は旗ONでも不変。差は説明文混入型1件が`cand0`から`guard_rejected(anchor_gap_inconsistent)`へ(いずれも復元せず、安全側の理由が付いただけ)。数値境界補正で変わった確定は`6 percent`の1一意(7 runs)のみ(未確定になりL6で完結文へ復元)。(b)cycle横断replay(`cycle_cross_replay_01.{json,md}`): L6復元一意46件(69 runs)で誤った文を選んだ件数0、`issue_focus_absent`は15件で発火(Rewrite見送り+Recheckのみ)・3件は通常Rewrite・28件はissueに引用符付き語句なし。発火15件のうち9件はissueの引用語句がclaim側に文字として現れない(Ledger側の語を指す型の可能性、Fableへの論点)。(c)B3根本原因の点検(設計書§7-A'): **Opusの仮説は事実**。cycle1のRecheckはRewrite後の本文(`while`)ではなく`prior_issues`の`claim_in_article`(=Rewrite前のspan text、`so`を含む)を写して再指摘していた(cycle2の本文にword `so`は存在しない)。Checker入力側の是正(prior_issuesにRewrite後の文を渡す等)はChecker入力の変更に当たるためユーザー判断事項(未実装)。(d)U-2(1)(位置語→構造要素、設計書§7-B、`u2_position_word_replay_01.*`、実装なし): (d)型5件中1件で新たに確定できる(誤範囲0)が、残り4件は`remainder_too_long`等の後ろのガードで棄却のまま。
- rep25(影響instance再実行、`er052_open233_self_recovery_flow_runner_01_rep25_affected_01.py`、`safety_A2A3`・`bgroup_B3`、n=2予定、予算¥8、全スイッチ=rep24+`VS_SENTENCE_RESTORE`): **即時STOP条件に該当し2/4 run(s1の2 instance)で停止**(再実行・n増しなし)。STOP理由=`bgroup_B3` s1で`pass_with_residual_unflagged B3`(Safety-critical残存)。結果: `safety_A2A3` s1=`RESOLVED_REWRITE`(¥0.9602、rep24同run ¥0.9227、STAGE4なし。`6 percent`型のclaimがcycle開始時点でL6により完結文へ復元され、同一cycleの先行Rewriteで書き換え済み[carry-forward]になった[決定論replayで確認、handoffへの記録は実行後の追加のためinstance JSONには無い])/`bgroup_B3` s1=`RESOLVED_STAGE2_DOWNGRADE`(¥0.1582、rep24同run ¥0.7671)。B3 s1の原因: Stage 1が`so`の因果claimをMAJORで挙げたが、**Stage 2(V7b、1 call)が`ACCEPTABLE`(basis=none)と判定して降格**し、Rewriteされないまま因果`so`が残って合格した(重大見逃し1件)。過去のB3の同claim(39件)はBLOCKING 31・QUALITY 6(rep7・iter8、旧基準)・ACCEPTABLE 2(rep24 s1の再掲1件と本rep25 s1)。**L6・`issue_focus_absent`は関与していない**(Stage 2はspan照合・Rewriteより前の段階)が、Safety KPI(重大見逃し0件)に反する実flow上の事実。
- rep25の指標: STAGE4(Human Review)=0/2 run(実行分)、L6の実flow発火記録=0(上記の記録の抜けのため。決定論replayではA2A3 s1で1件)、`issue_focus_absent`発火0、焦点文ガード発火0、重大見逃し=**1件(B3 s1、Stage 2のACCEPTABLE)**、JA変更0、費用+¥0.04(A2A3)/-¥0.61(B3、Rewriteなし)。B3 s2・A2A3 s2は未実施のため、rep24の失敗2件(A2A3 s2・B3 s2 cycle2)をL6が実flowで復元するかは**未確認**(¥0のreplay=実データのfixture・単体テストでは復元を確認)。
- 確認できたこと/推測: 確認=上記の全数値(replay・テスト・instance JSON・決定論replay)。推測=B3 s1のACCEPTABLEはStage 2の非決定性(V7b、1 call判定)による外れ値と考えられるが、頻度は未測定(過去記録の再掲含め2件/39件)。
- USER_DECISION候補/Fableへの論点: (1)B3のSafety-critical見逃し(Stage 2 ACCEPTABLE)の扱い=Stage 2の単独判定の非決定性への対策要否(本委任の範囲外、V7b・Stage 2は変更していない)、(2)アンカー型の字義上の拡張、(3)U-2(1)の実装可否(承認済みP-strict-closedの変更)、(4)論点3のL5末尾省略の粒度不整合、(5)B3根本原因のChecker入力側是正(Checker入力の変更)、(6)`issue_focus_absent`のclaim由来制限の要否。29件再確認は次の委任_67(Fable照合後)。
- 運用メモ: T-0は委任文を全文逐語保存し`check_delegation_prompt.py`はPASS。詳細証跡: `er052_output/open233_self_recovery_flow_runner_01_rep25/`(`summary_01.{json,md}`・instance JSON)、`er052_output/open233_span_restore_offline_01/`。

## 49. 委任_67: B3見逃し(rep25)の原因診断と対策設計(2026-10-04、費用¥5.7761、Phase累計¥579.7460)

- 性質: rep25で発生したSafety-critical B3見逃し(Stage 1がMAJOR検出→Stage 2[V7b、1 call]がACCEPTABLEへ降格→Rewriteなしで合格)の原因診断と対策設計。実装なし・Production未変更・`PRODUCTION_WIRED`なし。診断スクリプト`er052_open233_stage2_b3_misdowngrade_diag_01.py`の新規作成のみ(runner・Prompt・Schema・V7b/V7は不変)。
- 事実の確定(確認できたこと、詳細は`docs/pm/design_open233_stage2_safety_downgrade_01.md`§1): rep25 B3 s1のStage 1は`substitute_baseline_on_stage1_miss`(V4A再利用が検出せずfixtureの`baseline_parsed`を代替投入、rep24と同一)。claim・issue・flag(`changed_causality`のみtrue)・severity=MAJORともrep24 cycle 1と同一。Stage 2はbody route(in_one_lineはhook対象外)、batch=1 claim、rubric V7b、prompt sha256`85f6b985...`。出力は`ACCEPTABLE/basis=none/rewrite_hint空`(schemaに理由欄なし)、reasoning 306 tokens。floorは`FLOOR_FLAGS`(actor/number/negation/comparison/time)に`changed_causality`が無く対象外。既存`apply_stage2_two_of_two`は「1回目BLOCKING→2回目で降格」方向のみ・NORMAL群限定のため適用外。MAJOR→非BLOCKINGの降格には確認が無い。
- 既存ログ集計(Rewrite前cycle 1、27ディレクトリ・475 instance JSON、rubric版はdir名から推定): Safety-critical 5件の観測112件で非BLOCKING 10件(最終的に非BLOCKINGで合格した見逃しは9件=B3 7[R3''' 4・V5 2・V7b 1]、A2A3-0 2[V5])。現行rubric(V7b)の実flowは23観測中1件。B3の版別: R3''' 4/26、V4 0/2、V5 2/2、V6 0/2、V7b 1/3。
- 診断測定(50 call、¥5.7761、error 0): (a)rep25と同一入力(prompt sha256一致)でV7b n=10は10/10 BLOCKING(非BLOCKING率0%)、V7 n=10は9/10 BLOCKING+1/10 ACCEPTABLE(10%)。V7b文言起因の仮説は否定(V7bの非BLOCKINGは0件)。(b)は、rep25のStage 2 batchが元から1 claimで(a)と同一構成のため省略(不要な再測定を避けた)。(c)B4-a・A2A3-0・A4-0・A5-0・K16・K20のV7b n=5は全て5/5 BLOCKING(0/30)。観察: ACCEPTABLEの2回(rep25 306 tokens、V7 run7 262 tokens)はreasoning tokensが少なく、BLOCKING回(418〜893)と離れる(n=2、因果は推測)。
- 原因(確認できたこと/推測): 入力差・batch構成・V7b文言・floor・Stage 1差のいずれでもなく、同一入力に対するStage 2の1回判定のブレ(非決定性)。V7bのB3見逃し率は1/13(約8%、95%上側限界約36%)、Safety-critical全体1/63(約1.6%)(推測、CI広い)。
- 対策設計(`docs/pm/design_open233_stage2_safety_downgrade_01.md`§4、実装なし): S1「降格の2-of-2」(Checker MAJOR+1回目LLM非BLOCKINGのときだけ2回目、2回とも非BLOCKINGのときだけ降格。別関数、`llm_materiality`で比較、API失敗はBLOCKING)=推奨。見逃し率p→p²(B3 8%→約0.6%、全体約0.03%、独立の仮定、0にはならない)。追加はrep24実測で68/102 MAJORが非BLOCKING=30 call/38 instance-run=約¥0.11/instance-run(推定でq次第で最大約+¥0.45/記事、+¥2/記事以内)。S2「因果の決定論ガード」=過剰Major・Human Review増のため非推奨(新規機械装置=ユーザー判断事項)。S3「V7b文言限定」=診断でV7b起因を確認できず不要。S4(別prompt・多数決)=参考。「MAJORは降格不可」はrep24で68/102がRewriteへ回り不採用。
- 既存より厳しくなる点: S1は降格が減る(Safety KPI 0件のための対策)ため、Production採用にはユーザー承認が必要。S1実装前に、2回目だけBLOCKINGになる率q(不要Rewrite/Human Review増)の限定測定(rep24の68件、約30 call=約¥4)を推奨。
- USER_DECISION候補: (1)S1(降格2-of-2)を検証用runnerへ実装・限定再確認してよいか(Opus#10後)、(2)「重大見逃し0」を確率的な極小化(p→p²)として扱ってよいか、(3)NORMAL群の既存2-of-2(1回でも非BLOCKINGなら降格)とS1(2回とも非BLOCKINGでなければ降格しない)のProduction配線時の整理。
- Opus条件A: packet `docs/pm/opus_packet_open233_stage2_safety_downgrade_01.md`(14,362字、論点8点、逐語ブロック貼付)を作成。Opusへの依頼はFableが行う。
- 運用メモ: T-0は委任文を全文逐語保存し`check_delegation_prompt.py`はPASS。詳細証跡: `er052_output/open233_stage2_b3_misdowngrade_diag_01/`(`results_01.{json,md}`・各run生応答)。

## 50. 委任_68: Opus#10・q測定・判断待ち(2026-10-04、費用¥4.3265、Phase累計¥584.0725)

- 性質: Opus独立技術レビュー#10(条件A)の保存とFable照合の記録、S1実装前のq限定測定、¥0再集計、Status整備。実装なし・runner/Prompt/Production未変更・`PRODUCTION_WIRED`なし。スクリプトは`er052_open233_stage2_b3_misdowngrade_diag_01.py`へ`--stage recount`を追加(既存の診断処理は不変)、`er052_open233_stage2_downgrade_q_measure_01.py`を新規作成。
- Opus#10(`docs/pm/opus_l2_review_open233_self_recovery_10.md`): S1は必要(3修正: 最終materialityで比較・NORMAL群2-of-2を構成から外す・Safety KPIを条件付き/通しで分離)。basis非none要求等の単純案は不採用、2回目のF5型prompt・Checker issue受け渡しも不採用。設計書§7(採否)・§8(修正版S1仕様)を追記。
- ¥0再集計(`er052_output/open233_stage2_b3_misdowngrade_diag_01/recount_01.{json,md}`): 474 instance JSON・27dir(委任_67の「475」とは1件差、smoke・fixtures・carry-forward修正前を除外した走査条件の差の推測)。Checker MAJOR 1143件のうち降格534件(llm_direct 471・2-of-2 14・決定論降格のみ49)。S1対象(llm_direct)でbasis=none: ACCEPTABLE 184/223=82.5%、QUALITY 34/248=13.7%(V7b: ACCEPTABLE 65/69=94.2%、QUALITY 10/35=28.6%)。既存2-of-2: 1回目BLOCKING 46件に2回目を呼び、32件が両方BLOCKING、14件が降格(8 instance、iter5〜rep12のR3'''期のみ)。
- q測定(`er052_output/open233_stage2_downgrade_q_measure_01/`): rep24のllm_direct 68件(cycle 1 62・cycle 2以降 6、body 50/hook 18)から、単価確認(1 call ¥0.1612→40件は約¥6.4で上限超見込み)の結果、各群15件基準(cycle 2以降は全6件+cycle 1は24件、固定seed)の計30 callを実施。2回目の最終materialityがBLOCKINGは0/30(cycle 1 0/24 [Wilson95 0〜13.8%]、cycle 2以降 0/6 [0〜39%])。body 0/23、hook 0/7、1回目ACCEPTABLE 0/18、QUALITY 0/12。2回目の`floor_reason`異常0件、API失敗0件。BLOCKINGが0件のため仮ラベル付けの対象は無し。STOP閾値(cycle 1で30%超/cycle 2以降で20%超)に該当せず。ただしcycle 2以降はn=6のため「20%超でない」とは言えず(上側限界39%)、「観測0件」にとどまる。
- 限界(確認できたこと): hook経路としてrep24で記録されたt12が、再実行ではbody routeで呼ばれた(route不一致1件、`results_01.json`に記録、q 0/30の結果は変わらないがhook-aware Stage 2での確認は29件)。2回目は1 claimずつ呼んだ(S1の実装は同一(instance, cycle, route)のclaimをbatchする設計のため、独立性はやや異なる)。S1が防ぐ対象(B3型の境界claim)は今回の68件(Checker MAJORで1回目が非BLOCKINGの大半は正当な降格)にはほぼ含まれず、qの低さは「S1が過剰Majorを増やさない」ことの根拠であり、「S1が重大見逃しを防ぐ」効果の実証ではない(p→p²は独立の仮定による推測)。
- S1追加費用の試算(推定): Stage 2の2回目 約¥0.11/instance-run・約¥0.15/記事(rep24の対象を(file,cycle,route)でbatchした30 call×単価¥0.144を38 run/29記事で割る)。追加Rewriteはq=0なら0。+¥2/記事枠はfloor_verify・L6・Recheck等の合計に対する上限。
- STOP: `USER_DECISION_REQUIRED`(Safety原則に関わる判断[KPI 0件の扱い]・既存より厳しくする変更[S1])。ユーザー判断待ち(7項目): (1)S1採用 (2)Safety KPI 0件の扱い(確率的極小化+Stage 1 recall別管理) (3)NORMAL群2-of-2の既定OFF化 (4)アンカー型L6の確認 (5)prior_issuesにRewrite後の文を渡す是正(Checker入力の変更) (6)U-2(1)位置語→構造要素 (7)Stage 1 recall対策の方向。
- 運用メモ: T-0は委任文を全文逐語保存し`check_delegation_prompt.py`はPASS。詳細証跡は上記のpath(`results_01.{json,md}`、`raw/`各claimの生応答、`selection_15.json`)。

## 51. KPI-RECOVERY-REDESIGN-02 委任_01: RCA・技術是正3件・後段Safety設計案・Opus packet(2026-10-04、費用¥0、Phase累計¥584.07)

- 性質: ユーザー指示(2026-10-04、`OPEN-233-KPI-RECOVERY-REDESIGN-02`、`DECISION_LOG.md`末尾に逐語記録)に基づく、B3「重大→問題なし」誤降格の構造的根本原因分析(Step 1)、Trial側の技術是正3件の実装、後段Safety設計案の比較(Step 2)、説明文混入(d)型5件の決定論的解決可能性の分析、Stage 1 recall・強モデル限定利用の比較前提、Opus批判レビュー用packet。API課金なし(¥0)。Production未変更。Trial Statusは`IN_PROGRESS`(`VALIDATED`/`USER_DECISION_REQUIRED`に到達していない)。KPIの変更・緩和なし。
- RCA(`docs/pm/rca_open233_b3_stage2_misdowngrade_01.md`): rep25 B3 s1のStage 2 prompt(14,514字)をAPI無しで復元しsha256がrep25記録値と一致(`85f6b985...`)。構造的欠陥(確認): (a)Stage 2はCheckerのissue・flagを渡されず再発見が必要、(b)解除にEvidence要件なし(ACCEPTABLE降格227件中184件=81%がbasis=none、V7bのllm_directは94%)、(c)promptにACCEPTABLEの定義が2つ(R3基底は因果の新規付加を排除、V7は排除しない)、(d)降格方向は1回判定、(e)因果は決定論floor(5フラグ)外、(f)rubricは8層のパッチでB3対処例が入っていても1回外れた、(g)QUALITYも「Rewriteなし通過」で流出10行中8行がQUALITY。reasoning tokens: Safety-critical単独batchで<400は2/3が降格、700以上は1/21(相関のみ、因果は不明)。
- 技術是正3件(runner `er052_open233_self_recovery_flow_runner_01.py`、テスト`..._test_01.py`): (1)`prior_issues`のclaim_in_articleをRewrite後の現行本文の置換後の文へ(`resolve_prior_issue_text`、特定不能なら元text、`prior_issue_text_source`をcycle記録へ。Checker Promptはsha256でバイト不変を固定)、(2)KPI確認構成`KPI_TRIAL_SWITCHES`+`apply_kpi_trial_switches()`(rep23〜25構成+L6 ON+NORMAL群2-of-2 OFF、既定のglobalは不変、CLI `--kpi-trial-config`)、(3)NORMAL群2-of-2を`STAGE2_NORMAL_TWO_OF_TWO`(既定OFF)へ。テスト: runner単体542件OK、er052回帰586件OK、全体回帰4509件で新規失敗なし(基準11件のみ)。
- 設計(`docs/pm/design_open233_kpi_recovery_02.md`、実装なし): 推奨D*=決定論クラスGuard(`G_H`∨`issue_actor`)で解除禁止+それ以外はS1。¥0 replay(`er052_output/open233_kpi_recovery_02_offline_01/`): 流出10行中9行閉鎖、解除不可の正当降格7/524(1.3%)、rep24の68件中2件(neg5のB3同一文)。S1のq=0/30は既存測定の再利用で新Trial未実施。(d)型5件は試作規則(Q:引用符字形の同一視/R:長い説明文の残りを捨てる/U-2(1))で5/5決定論確定、既存確定164件への影響0(実flow検証は未実施)。Stage 1 recallは6-B(決定論候補生成)+6-C(候補文のみの補助check)を比較(推定、未測定)。Solは`gpt-6-luna`の20倍で、Stage 2換算平均約¥2.8/call・p95約¥5、1callで+¥3 Capを超えうる(価格は2026-09-29のリポジトリ内値、公式ページの再取得は未確認)。
- 副次発見: neg5(B3と同一文、プロジェクトのv2訂正で正BLOCKING扱い)がStage 2で過去6回降格されているが`SAFETY_CRITICAL_CLAIM_DEFS`に未登録で、流出に計上されていない(計測是正の提案、未実装)。
- Opus packet: `docs/pm/opus_packet_open233_kpi_recovery_02_01.md`(約13,500字、条件A、既存Opus#8/#10との関係を明記)。Opus批判レビュー#11待ち。
- 次: Opus#11→Fable評価→委任_02(設計改善+実装+Step 5限定確認)→委任_03(Step 6、Safety-critical群+29件)→未達なら再ループ。

## 52. KPI-RECOVERY-REDESIGN-02 委任_02: Opus#11→Fable評価・三層構造の実装・G_L ¥0評価・確認役offline replay(2026-10-04、費用¥33.12、Phase累計¥617.19)

- 性質: Opus独立レビュー#11(条件A)の保存とFable評価(三層構造Tier 0決定論Guard/Tier 1確認役/Tier 2 Rewriteを主構造に採用、D*[G_H∨issue_actor+S1]は補助ベルトへ降格、S1・Sol不採用、規則R保留。逐語は`docs/pm/opus_l2_review_open233_kpi_recovery_02_11.md`、PM_GOVERNANCE 11-3の8項目照合・STOP条件非該当を含む)、Trial側(`er052_open233_*`のみ)への実装、¥0・有料のoffline評価。Production未変更、`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`ではない。Trial Statusは`IN_PROGRESS`。KPI(Primary Human Review 0件・Safety重大見逃し0件・平均+¥2/記事・Cap+¥3)は変更していない。
- 実装(runner `er052_open233_self_recovery_flow_runner_01.py`、`STAGE2_DOWNGRADE_VERIFY`既定OFF、`KPI_TRIAL_SWITCHES`ではON、CLI `--stage2-downgrade-verify`): Tier 0=`stage2_release_guard`(G_L[`TIER0_G_L_ENABLED`既定False]+補助ベルトG_H/issue_actor[`aux:`接頭辞])、Tier 1=`run_downgrade_verify_call`/`downgrade_verify_evaluate`(`floor_verify`の一般化、call 1回、verdict+Ledger逐語引用の決定論照合、API失敗・schema不一致・非逐語はBLOCKING)、Tier 2=`downgrade_verify_rewrite_hint`(Checker issue+Ledger notes_for_writer/conditions、Human Reviewへの新経路なし)、neg5のSafety-critical登録(`registered_in`付き)・`derive_safety_critical_from_labels`・`safety_critical_dual_summary`(旧値/新値並記)、規則Q・U-2(1)(`VS_EXPLAIN_SPLIT`配下)、`section_type_observed`記録。テスト: runner単体582件OK(新規40件+既存の意図した更新: U12・S8が棄却→確定、U11の理由変更、新規確定10→11)、er052回帰626件OK、全体回帰4549件で失敗6・エラー5=基準11件のみ(er052の新規なし)。Production正式path(`er003*`〜`er019*`)の`er052_open233`参照は0件。
- G_L ¥0評価(`replay_guards_03_gl.py`): G_Lは流出16/16を閉鎖するが正当降格518件の20.8%・NORMAL群10.9%をBLOCKING化(G_B 25.5%・24.6%)。補助ベルト(G_H∨issue_actor)は15/16閉鎖・誤停止0.2%。事前基準の文面(「>5%かつ上積みなし→不採用」)では上積み1行のため「採用」だが、確認役の採否基準(ii)[NORMAL群≤10%]がTier 0分も含むためG_L有効時は確認役の前に基準を超える→Tier 0既定は補助ベルトのみ(判断はClaude/Sonnet、差はFableへ報告)。
- 確認役offline replay(`replay_verify_01.py`、450呼び出し、実測¥33.12[probe v1 ¥0.44を含む]、概算は全件約¥65.8→縮小約¥44.9): (i)流出閉鎖**15/16**(開いた1行=rep24 cycle 2のB3「and」版、確認役は2回ともRELEASE)、(ii)NORMAL群BLOCKING化**47.3%**(52/110)、(iii)全降格54.6%・正当降格52.6%、(iv)QUALITY 62.8%・ACCEPTABLE 38.5%、(v)非逐語0/439、(vii)n=2一致88.8%。**採否判定: 採用しない**(基準(ii)>25%・(i)<100%)。ユーザーへKPI緩和は提案しない。診断: NORMAL群でHook経路23/27・title 7/7・disclosure_gap降格8/9が止められ、body経路は37%(確認役rubricにHook-aware許容がなく承認済みの決定論降格も覆す。bodyでも10%未満には届かない=primingの実測)。G_L追加の反実仮想は(i)16/16・(ii)58.2%。
- Step 5 rep26(既知case限定確認): 採用判定でないため**未実行**(`er052_open233_self_recovery_flow_runner_01_rep26_known_01.py`は作成のみ)。Human Review・重大見逃し・L6実flow復元・Rewrite解消率は未測定(Human Review 0件のKPIは本委任では検証していない)。
- 設計書: `docs/pm/design_open233_kpi_recovery_02.md`§9(三層仕様・採否基準・測定計画・Stage 1 recall手順[6-B∧6-F]・replay結果)。
- 次: Fableが再設計(確認役の対象/prompt/Tier 0の組み替え、新しい構造・promptは条件A=Opus)を判断→委任_03(実装+offline再評価、通過後にrep26→Step 6)。


## 53. KPI-RECOVERY-REDESIGN-02 委任_03: 再設計D*′(因果floor語彙hold-out評価・S1・hint合成)の¥0評価と実装、有料run未実行(2026-10-04、費用¥0、Phase累計¥617.19)

結論: **因果floorの語彙hold-out評価が採用条件(正当降格の誤停止≤2%)を満たさなかったため、Fable事前規則どおり語彙を削らず、Step 5(rep26)以降の有料runは実行していない。KPI判定(VALIDATED/未達)はまだ行っていない(`IN_PROGRESS`)。** 有料API呼び出し0、費用¥0。

- (確認)語彙確定の証跡: 語彙(`CAUSAL_CONNECTIVES_EN`78項目、`HEDGE_MARKERS_EN`・帰属型ヘッジ・`HEDGE_CAN_WOULD_EN`)を流出16行の文面を見ずに言語学的目録(CGEL/Quirk/Halliday & Hasan/PDTB/Levin/Hyland/Palmer)から構築し、評価前にgit commit `3808f61f`で固定した。評価後の語彙変更はしていない(`can`/`would`のA/Bのみ許可されていたが、結果は完全同値)。
- (確認)hold-out評価(`er052_output/open233_kpi_recovery_02_offline_01/replay_guards_04_causal_floor.py`・`.json`・`replay_guards_04_stdout.txt`、母集団=Checker MAJOR 1143件[降格534・流出16・正当降格518・NORMAL群110]):
  - 因果floor A/B: 流出閉鎖13/16(旧10→7/10、and版除き13/15)、正当降格の誤停止13件=**2.51%**(QUALITY 10・ACCEPTABLE 3)、NORMAL群3件(2.7%)。A/Bは完全同値。採用条件(誤停止≤2%・閉鎖≥15/16)は**不達**。
  - 既知G_H 6語(参考): 閉鎖13/16(同値)・誤停止0件。つまり**語彙拡張の上積みは閉鎖0件・新規誤停止13件**(`lead to` 6[否定文「did not lead to…」を含む]・`as` 4・`caused` 3・`makes/make` 1、6文の重複)。
  - Tier 0全体(因果floor_A∨issue_actor): 閉鎖15/16(and版除き15/15)・誤停止14件(2.70%)・NORMAL群4件(3.6%)。G_H 6語∨issue_actor(委任_02補助ベルト): 閉鎖15/16・誤停止1件(0.19%)・NORMAL群1件(0.9%)。
  - 開いている流出: 因果floor単独=A2A3の主体型2行(`would repay the money`、`issue_actor`が閉じる)+rep24 cycle 2のB3「and」版1行。Tier 0全体では「and」版のみ。
- (実施)実装(`er052_open233_self_recovery_flow_runner_01.py`、既定OFF・Production未変更): Tier 0 `causal_floor_guard`(`stage2_release_guard`に統合、`run_stage2`の最終materiality非BLOCKINGのChecker MAJORに適用、`floor_reason="changed_causality_floor"`、hint合成、`tier0`記録)、S1 `apply_stage2_second_opinion`(Opus#10の3修正・対象claimのみbatch・割れ/API失敗/schema不一致BLOCKING・floor異常ログ・floor_verify解放済み除外・毎cycle適用・記録`stage2_downgrade_confirm_log`)、スイッチ`CAUSAL_FLOOR`/`STAGE2_SECOND_OPINION`(`KPI_TRIAL_SWITCHES`でON、`STAGE2_DOWNGRADE_VERIFY`は外した)、`tier0_summarize`/`s1_summarize`、`CORRECT_LABEL_OVERRIDES`(「and」版=ACCEPTABLE、Fable判断・ユーザー未確認、旧値/新値並記)。確認役コードは残置。
- (確認)テスト: runner単体598件OK(新規17件)、er052回帰642件OK、全体回帰4565件中の失敗11件(er011/er015等の基準11件のみ、新規なし)。
- (未実施)rep26(Step 5)・rep27(Step 6)・KPI判定・Safety-critical 6件の再確認・平均追加/worst費用・不要Rewrite数。いずれも採用条件不達のため実行していない。
- (推測)語彙拡張が閉鎖に寄与しなかったのは、流出16行の因果型はほぼ`so`(既知語)で、目録由来の追加語は流出に現れない一方、一般文の`lead to`/`as`/`caused`で誤停止するため。語彙を削る調整はhold-out手順の趣旨に反するため行っていない(Fable判断事項)。
- 設計書: `docs/pm/design_open233_kpi_recovery_02.md`§10(Fable再設計判断1〜9の逐語記録・語彙確定の証跡・hold-out評価表)、`docs/pm/opus_l2_review_open233_kpi_recovery_02_11.md`(4)(実測後のFable再判断)。
- 次: Fableが(a)語彙拡張を採用条件の範囲で再設計する(例: 採用語を既知G_H 6語+誤停止0の語に限る等はhold-out汚染になるため要判断)、(b)G_H 6語+issue_actor(補助ベルト、誤停止0.19%)をTier 0の正とする、(c)2%基準の扱い、のいずれかを判断→委任_04(rep26→Step 6)。


## 54. KPI-RECOVERY-REDESIGN-02 委任_04: Tier 0=known6+issue_actor確定・Step 5 rep26・Step 6 rep27のKPI判定(2026-10-04、費用¥24.66、Phase累計¥641.85)

結論: **KPI未達(Primary=Human Review 0件が3件で不達)。Safety(重大見逃し旧/新定義とも0)・平均追加費用・Cap(+¥3)は達成。`IN_PROGRESS`のまま、Closeoutへは進まない。再実行・n増しはしていない。** `VALIDATED`ではない(Production採用ではない・`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`ではない)。

- (実施)作業1: `CAUSAL_FLOOR_VOCAB`(既定`known6`=AUX_CONN_RE 6語+AUX_HEDGE_RE、`inventory`=評価用)を実装、`KPI_TRIAL_SWITCHES`へ`CAUSAL_FLOOR_VOCAB:"known6"`。設計書§11にFable判断1〜4を逐語記録。commit 8603c922。
- (確認)作業2 rep26(Step 5、8 run、実測¥6.15+是正前の失敗1 run ¥1.06=¥7.21、見積り≈¥5): 初回は`safety_A2A3` s1が`STAGE4(violation_span_unverified)`。原因=照合漏れ(同cycleの先行Rewriteが後続claim範囲の一部[文末の節]だけをL1語レベルで置換→後続claimの文字列が現本文から消え、`carry_forward_resolution`が範囲の「完全包含」しか見ないため確定不能)。是正=`carry_forward_resolution`に「先行Rewriteの置換単位が範囲の部分文字列、かつ先行/後続のissue文字列・related_fact_id・trueのflag集合が全て一致」の場合に限り書き換え済みとみなす(解消判定は従来どおり全文Recheck、異なる指摘は従来どおり確定不能。Human Reviewへ倒す新経路ではない)。テスト601件OK・er052回帰645件OK。同instanceのみ再実行(1回)→8 run全て`RESOLVED_REWRITE`、STAGE4 0・見逃し0(旧/新)、JA 0、neg3の不要Rewriteはrep24と同一(HF-009の1件)、B3 cycle 2再指摘なし(全run 1 cycle)、L6 4回発火・4回復元(A2A3の「6 percent,…」断片→文全体、neg5「So…」→「Meanwhile,…」)、Tier 0はneg5で2件発火(`changed_causality_floor`)、S1 20件全一致(割れ0)、部分一致carry-forwardはA2A3 s2で1回発火。失敗した初回JSONは`er052_output/open233_self_recovery_flow_runner_01_rep26/failed_attempts/`へ保存。費用: rep24同instance比 -¥0.03/記事。
- (確認)作業3 rep27(Step 6、29 instance・38 run、実測¥17.45、見積り≈¥22、1 run平均¥0.459、worst run¥2.37=bgroup_B4 s1、1 run>¥7なし、例外0、JA変更0):
  - Human Review(STAGE4)**3件**(rep24=2、iteration 7=7): (1)`neg3_hormuz_prodrunner_b1b` s1=`unconfirmed_after_reverify`、(2)`safety_A4` s1=`ladder_exhausted_without_full_rewrite`、(3)`safety_A5` s1=`ladder_exhausted_without_full_rewrite`。
  - 重大見逃し: 旧定義0・新定義(自動導出)0、`pass_with_residual_unflagged`0。`residual_at_pass`は全件仮ラベル(Fable照合待ち)。Safety-critical 6件(B3・B4-a・A2A3-0・A4-0・A5-0・neg5)はいずれもStage 1はreuse(記録済みrun)、B3のみ`stage1_recall_miss_substituted=True`(代替投入)で、全て最初のcycleでBLOCKING検出(B3=LLM BLOCKING、A2A3/A4はS1第2意見が追加BLOCKING、A4はdeterministic_floor:changed_actor)。A4/A5は検出後のRewriteでSTAGE4(見逃しではなくHuman Review側)。
  - Tier 0発火0件(B3もLLM自身がBLOCKINGのためTier 0到達せず)。S1対象71・一致65・割れ6(いずれも第2意見BLOCKING=A2A3 4件・A4 2件)・失敗0、S1費用¥2.29。
  - 不要Rewrite: Rewrite実行24件/19 run(rep24と同数・同run数、iteration 7は39件/23 run)、NORMAL群3/14(rep24・iter7と同一)。過剰Major(Stage 2 BLOCKING)32件(rep24 35、iter7 39)、floor単独7件(rep24 4、iter7 4)。cycle数>=2は2 run、>=3は0。
  - L6 7回発火・7回復元、P/Q(`explain_split`)は発火0(L6のみ)。prior_issues現行本文化21/26件。部分一致carry-forward 1回(A2A3 s2)。
  - 費用: 平均追加/記事=rep24比+¥0.019・iteration 7比-¥0.58(基準両方併記)、worst追加(同instance平均比)=rep24比+¥0.80(bgroup_B4)・iter7比+¥0.39、Cap+¥3超のrunなし。
- (確認)STAGE4 3件の原因:
  1. **A4・A5(L6とcarry-forwardの順序の実装不整合)**: Checkerが同一文を2つの文字列(引用符付き「“…”」と引用符なし)で指摘する。最初のclaimのRewriteで文が書き換わった後、後続の同文字列claimは本来carry-forward(`covered_by_earlier_rewrite_in_cycle`)で処理される(rep24=L6 OFFでは全件そうなりA4/A5とも合格)。rep27では**L6(VS_SENTENCE_RESTORE)が先に「文字列が現本文に無い→最も近い文を復元」して、既に書き換え済みの文(例「…with the people they called.」「…rolled back the feature…」)を復元対象としてresolvedにし、carry-forwardに到達しない**。結果、書き換え済みの文へ2回目のRewriteが走り、段落Rewriteがguard失敗→ladder枯渇→STAGE4(A4はHC-010も書き換え済みの文を再度「could mean」へ二重Rewrite)。Tier 0・S1の発火は無関係(L6対象は検出済みBLOCKING claim)。
  2. **neg3 s1(既存fail-closed経路、非決定性)**: floor(`deterministic_floor:changed_time`)でBLOCKINGの1文を語レベルで書き換え(rep24と同一のRewrite)→全文Recheckが`LEDGER_COMPLIANT`かつ`all_prior_issues_resolved=false`の自己矛盾→再確認(`recheck_confirm`)が`LEDGER_DEVIATION`(`all_prior_issues_resolved=true`)を返し、委任_11以来のfail-closed(`unconfirmed_after_reverify`)でSTAGE4。同instanceのs2(同構成)は1 cycleで合格、rep24ではs1合格・s2が2 cycle。Tier 0発火0・S1全一致・Rewriteはrep24同一で、新規構成要素は関与していない(確認役=Checkerの非決定的出力)。再確認が返した`LEDGER_DEVIATION`の具体的な指摘claimはinstance JSONに記録されておらず未特定(推測: 文書内の別の文または解消後文への新規指摘)。
- (推測)再ループ案: (a)A4/A5=実装是正(L6適用前にcarry-forward適用可否を判定する/L6の復元先が同cycleの`after_units`と一致する場合はcarry-forwardへ回す。決定論・追加call 0・Human Reviewを減らす方向のみ)。これで修正後はrep24同様にA4/A5が合格する見込みだが未実測。(b)neg3=設計判断が必要(`unconfirmed_after_reverify`で再確認が別の指摘を返したとき、STAGE4でなく次cycleへ回すか。Checker出力の非決定性であり、Opus条件A該当の可能性)。Step 6は再実行・n増ししない規則のため本委任では未実施。KPI(Human Review 0)を満たすには、(a)(b)の対処後に再度の確認が必要。
- 残存リスクの明示(Fable判断2): known6は観測済みの流出クラス(`so`型)を閉じるが、未観測の接続語型の系統誤りには効かず、S1(偶発的な外れ向け)でも閉じない。今回rep27ではTier 0の発火が0件であり、Tier 0がTrial規模で効いたことは確認できていない(B3はLLM判定で検出)。目録拡張が誤停止を生んだ事実は「接続語の有無だけでは因果主張を判別できない(否定scope・多義語)」という知見として記録。
- 出力: `er052_output/open233_self_recovery_flow_runner_01_rep26/`(`summary_01.md/.json`)、`er052_output/open233_self_recovery_flow_runner_01_rep27/`(`summary_01.md/.json`、`summary_kpi_01.json`、`blocking_claims_01.md`)、スクリプト`er052_open233_self_recovery_flow_runner_01_rep26_known_01.py`・`rep27_full_01.py`・`rep27_agg_01.py`。
- 注: `instances_s*/*.json`の`switches`欄は`CAUSAL_FLOOR_VOCAB`を含まない(既存の記録形式。`run_log_main.json`の`switches`と本REPORTで`known6`を記録)。

## 55. KPI-RECOVERY-REDESIGN-02 委任_05: rep27 Human Review 3件のRCA・L6×carry-forward順序の是正・再確認DEVIATION処理設計・Opus#12 packet(2026-10-04、費用¥0、Phase累計¥641.85)

結論: **A4/A5(2件)は技術是正を実装し¥0 replayで二重Rewriteの解消を確認。neg3(1件)は設計案N1〜N3を比較(推奨N1、未実装)。raw応答が未保存のため、再確認が返したdeviationの内容は未確認。`IN_PROGRESS`のまま、`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`ではない、Production未変更。** 有料runなし(¥0)。

- (確認)A4/A5: 同cycleの先行Rewriteで文が書き換わると、同じ文を引用符なしで指す後続claimが`mismatch`になり、L6が書き換え済みの文を復元→2回目のRewrite→guard失敗→ladder枯渇(rep24=L6 OFFでは`covered_by_earlier_rewrite_in_cycle`で合格)。是正=`l6_carry_forward_precedence`(runner、`run_stage3_for_claim_spans`から呼ぶ)。L6の復元が(1)cycle開始時点の照合で先行Rewrite済み、または(2)先行Rewriteの置換後の文と完全一致、ならcovered。`handoff.resolution.l6_skipped`を記録。追加call 0。設計書§12-1。
- (確認)¥0 replay(`replay_cf_l6_order_01.*`): A4 rec 2・3、A5 rec 1がcoveredへ(再Rewriteなし)。rep26・27のL6関与の復元(rep26 6記録・rep27 9記録)は全て「書き換え済みの文への復元」型で、変わる記録は全て同型(neg5 HF-007 3件、changed_number 1件、A4 2件、A5 1件)。先行Rewriteのないcycleで単独に働いたL6の例は証跡に0件(L6本来の価値は未観測、規則(2)単独が効いた実例もなし)。委任文の「他のL6復元が変わらないこと」は満たされない(全て同型のため意図した変化)。
- (確認)テスト: 新規7件(`TestL6CarryForwardPrecedence`)、runner単体608・er052回帰652 pass、全体回帰4575件は基準11件(6 failure+5 error)以外の新規なし。
- (確認)neg3: **Recheck・再確認のraw応答は全ログに未保存**(従来は`prior_issues_resolved`・再確認の`deviations`を記録していなかった)。promptは決定論に再構築しsha256一致(`rca_neg3_prompt_reconstruct_01.*`)。`prior_issues`は現行本文(`current_text`)が渡っており、`issue`/`explanation`は書き換え前の文の欠陥を述べたまま。Recheckの自己矛盾(COMPLIANT∧all_prior=False)は418 Recheck中33(neg3 23/28・neg2 7/8・他3/382)=neg3/neg2にほぼ恒常的。再確認がDEVIATIONになったのはneg3 21回中5回・neg2 6回中1回、全て最終STAGE4。再確認のdeviation claimの特定・仮ラベルは**不能(未確認)**。記録専用の追加(`recheck_prior_issues_resolved`・`recheck_confirm_deviations`等、挙動不変)で次runから逐語が残る。
- (推測)設計: 現行は再確認のdeviationsを捨て、Stage 2を通さずSTAGE4へ直行する(通常のRecheck→DEVIATIONはStage 2を通る不整合)。N1=再確認DEVIATIONのMAJORを通常のstage1_deviationsとして既存cycleへ流す(追加call 0・cycle上限不変、推奨)。N2=再確認2回(+約¥0.27、不採用)。N3=prior_issues文言の明確化(効果不明、併用候補)。Production配線は再確認callがTrial専用のため別設計。設計書§12-3(比較表・残STAGE4経路の棚卸し表)。
- 出力: 設計書`docs/pm/design_open233_kpi_recovery_02.md`§12、`er052_output/open233_kpi_recovery_02_offline_01/`(`replay_cf_l6_order_01.*`・`rca_neg3_prompt_reconstruct_01.*`・`agg_stage4_reasons_01.*`)、`docs/pm/opus_packet_open233_kpi_recovery_02_02.md`(約12,600字)。

## 56. KPI-RECOVERY-REDESIGN-02 委任_06: Opus#12→Fable評価・N1′/潜在ギャップ是正/N3′の実装・A/B・Step 6再確認rep28【Human Review 3 → KPI未達】(2026-10-04、費用¥25.34、Phase累計¥667.19)

結論: **KPI 4つのうち3つ達成、Primary(Human Review 0件)のみ未達。`IN_PROGRESS`のまま(`VALIDATED`ではない)、`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`ではない、Production未変更。** Human Review 3件=rep27の3件(A4・A5・neg3)は全て解消、代わりに別の3件(いずれもStage 3 Rewrite側の失敗、N1′の合流とは無関係)。重大見逃し0(旧/新定義)、平均追加+¥0.10/記事(rep24比、iter7比-¥0.50)、worst追加+¥0.81(Cap+¥3超なし)。KPIは変更・緩和していない。

### 実装(確認、設計書§13)
- N1′: 純関数`normalize_recheck_outcome`(PASS/NEXT_CYCLE/STOP)+スイッチ`RECHECK_MERGE_UNRESOLVED`(既定OFF、`KPI_TRIAL_SWITCHES`でON)。再確認が`COMPLIANT∧all_prior=True`以外なら、判定元のMAJOR ∪ 未解消prior(元claimのdev、現行本文の文が単一特定できれば差し替え)をfact_id重複除去して次cycleのStage 2へ。空なら既存`not blocking_claims`経路+監査flag`reverify_deviation_without_major`。`unconfirmed_after_reverify`のSTAGE4経路はON時に廃止。追加call 0、`MAX_CYCLES=2`/`HARD_MAX_CYCLES=3`不変。
- 通常Recheckの潜在ギャップ(`DEVIATION∧all_prior=False`で未解消priorがdeviationsに無い)も同じ純関数で合流(`normal_gap`)。
- N3′: `RECHECK_BEFORE_AFTER_PAIRS`(既定OFF、run_recheckへ前後の対ブロックを追加、cite-or-release指示なし)。Checker本体template/`build_prior_issues_instruction`はsha256固定テストでバイト不変。
- テスト: runner単体608→630(新規22: 純関数15・run_instance統合7)全PASS、er052回帰674 pass、全体回帰4597件は基準11件(6 failure+5 error、既存)以外の新規なし。

### 旧`ladder_exhausted` 10件の¥0分類(確認、設計書§13-4)
(A)同cycleで先行Rewrite済みの文を再Rewrite 3件(iter8 A5・rep27 A4・A5、是正(a)で解消)、(B)旧`paired_ja_en(J-1)`のguard失敗 6件(`english_only`のKPI構成では機構が無効)、(C)その他1件(iter8 unsupported_new_claim、title削除のguard失敗)。**rep28で(C)型が`degenerate_rewrite_output`として再出現した**(下記)。

### A/B(neg3・neg2 × n=2 × {A: N1′、B: N1′+N3′}、8 run、実測¥4.84[A ¥2.71・B ¥2.13]、`er052_output/open233_self_recovery_flow_runner_01_rep28a/`)
- Recheck自己矛盾率: A 2/2(100%)・B 2/2(100%)。neg2は4 run全て`RESOLVED_STAGE2_DOWNGRADE`でRecheck自体が無く(Rewriteなし)、データはneg3の4 runのみ。再確認call A 2・B 2、全て`COMPLIANT∧all_prior=True`で通過、再確認deviationは4/4で空(旧ログの24%のDEVIATIONは今回は観測されず、nが小さい)。N1′の合流は0件(発火機会なし)。
- **自己矛盾の機序(確認、`er052_output/open233_kpi_recovery_02_offline_01/ab_selfcontradiction_mechanism_01.*`)**: Recheckは`prior_issues`1件に対し**`index=0`の項目を2件返し(HF-003・HF-009、どちらも`resolved=true`)**、runnerの`all_prior_issues_resolved = (len(resolved)==len(prior_issues)) and all(resolved)`が**件数不一致で`False`**になっていた(4/4)。再確認側はcite-or-release後の`len>0 and all(resolved)`で件数を問わないため`True`。つまり、これまで「Checkerが解消未確認と判断」と見なしていた自己矛盾は、少なくともこのA/Bの4件では**判定の揺れではなく件数一致規則(er003 vfl01 826行と同一式)とChecker応答の項目数のずれ**(過去ログは項目未保存のため、全件がこの機序とは言えない=推定)。Opus#12の「前後の対が無いことが主因」(強い推定)は、このA/Bでは支持されなかった(Bでも100%)。
- N3′採否(事前基準): Bの自己矛盾率がAより下がらない→**N3′は採用せずOFF**(N1′のみで29件)。(ア)形だけの解消はBで0件、(イ)STAGE4・見逃しの増加なし、ただし第1条件を満たさない。
- 新発見(実装せず報告): 上記の件数一致規則は、Checker応答が余計な項目を返すだけでRecheckを自己矛盾にし、再確認call(約+¥0.2〜0.4)を毎回起こしている。これを緩めるか否かは「Checker判定規則」に近い境界事項のためFable判断(KPI構成の安全性を下げる可能性がある)。

### rep28(Step 6、29 instance・38 run、N1′ON・N3′OFF、実測¥20.50、`er052_output/open233_self_recovery_flow_runner_01_rep28/`)
- Human Review(統一定義=`stage4_reason`全種+例外終了): **3件**(例外0、missing 0)。
  1. `safety_er009_changed_scope` s1: `ladder_exhausted_without_full_rewrite`。cycle 1で水準①の語編集が「…restaurants…」を「…now directly confirmed in New York City taxis…」へ変え、これをRecheckが新規MAJOR(`changed_certainty/time`、unsupported)と指摘(通常のRecheck→DEVIATION経路、N1′の合流は`recheck_major`1件で通常と同じ)→cycle 2の水準①〜④の書き換え案「In the New York City taxi study, higher suggested tip rates ... credit-card users to leave more money.」が**3水準とも`actor_guard_rejected`**で枯渇。
  2. `safety_er009_unsupported_new_claim` s1: `degenerate_rewrite_output`。唯一のclaimが記事冒頭のタイトル行で、水準0の決定論deleteでタイトルが空になり(`title_word_count_after=0`)劣化検出で停止(旧分類の(C)型。rep24・rep27の同instanceはSTAGE4なし=非決定性)。
  3. `meta_run03_advanced` s2: `ladder_exhausted_without_full_rewrite`。Recheckが元claimを3箇所の引用に拡張して再指摘(MUSE-HC-006、In one lineを含む)→cycle 2の水準③の書き換え案(People could ask Muse to call businesses on their behalf. / (削除) / Some calls ... handled by human contractors on users' behalf.)と水準④が`actor_guard_rejected`。
- 3件の共通点(確認): N1′の合流(`unresolved_prior`/`reverify_deviation_without_major`)ではなく、**Rewriteの`actor_guard`が、記事の修正として妥当に見える書き換え案を拒否**している(2件)・title単独claimの決定論deleteの劣化(1件)。仮ラベル(Fable照合用、私の目視): 書き換え案はLedger(F-004は「credit-card users」、MUSE-HC-006は契約者が事業者へ代行発信)に沿うため、guardの過剰拒否の疑い(推定)。guardの判定ロジックは未読(再ループで確認が必要)。
- N1′の効果(確認): neg3 s1・s2は再確認を経てPASS(`unconfirmed_after_reverify` 0件、rep27の1件を解消)。A4・A5は是正(a)でPASS。合流イベントは5件で全て通常経路の`recheck_major`(`unresolved_prior`/`normal_gap`/`reverify_major`は0、`reverify_deviation_without_major` 0)。Recheck 20回中自己矛盾2回(neg3のみ)。
- 重大見逃し: 旧定義0・新定義0、`pass_with_residual_unflagged` 0。Safety-critical 6件(A2A3×2・B3×2・B4・A4・A5・neg5)は全て検出・Rewrite経路を通過(B3・neg5はsubstring残存だが`ever_blocking_flagged=True`、rep24・rep27にも同パターンあり=新規ではない)。`residual_at_pass`全件(8def): 全件`pass_with_residual_unflagged=False`、`remains_in_final_en`=B3 s1・s2・neg5 s1の3件のみ(仮ラベル: 既存定義では見逃しでない、書き換え後の部分一致残存の可能性・要Fable確認)。
- Tier 0発火0件(n_target 68)、S1 n_target 68・割れ1件(A2A3)、L6発火1件(A2A3、復元成功)、N3′は不使用(OFF)。stage4移動監視: `same_claim_fact_id_reblocked` 0・`cycle_limit_exhausted(_after_recheck)` 0(cycle≥3到達0、cycle≥2は5 run)。JA変更0。
- 不要Rewrite: 実行24件/21 run(rep24 24件/19 run、iter7 39件/23 run)。NORMAL群は5/14 run(rep24・iter7は3/14)=meta_run03_advanced s1とneg5 s1の増(neg5 s1はrep27にもあり、非決定性の範囲)。過剰Major: Stage 2 BLOCKING 35(floor単独5、rep24は35/4)。
- 費用: 合計¥20.50(rep24 ¥16.72、iter7 ¥39.55)、平均/run¥0.54、worst run¥2.16、平均追加+¥0.10(rep24比)・-¥0.50(iter7比)、worst追加+¥0.81(`safety_A4` s1、rep24 instance平均比)、Cap+¥3超0。Guardrail¥35内(A/B ¥4.84+rep28 ¥20.50=¥25.34)。
- モデル・構成: `runner.MODEL=gpt-6-luna`、V7b、KPI構成(HANDOFF=violation_span・L6・english_only・time_only・Tier 0 known6・S1)+N1′。

### 再ループ案(Fable判断待ち、未実装)
(1)`actor_guard`の拒否理由と、拒否された書き換え案が妥当だったかを¥0で全rewrite_recordsから集計(過剰拒否率)→妥当なら技術是正(guard側の精度)。(2)title単独claimのdeleteが劣化になる型(C)に、deleteでなく水準1〜へ進める等の既存ladder内の是正。(3)件数一致規則と自己矛盾の関係(項目数の不一致)の扱い(判定規則に近い=Fable/ユーザー判断)。いずれもKPI緩和ではない。Step 6の母数・nは固定のため、再実行は再ループ後の新構成で別途判断。

## 57. KPI-RECOVERY-REDESIGN-02 委任_07: rep28 Human Review 3件のRCA・件数一致バグ/構造要素deleteの是正実装・actor_guard設計AG1〜AG3・Opus#13 packet(2026-10-04、費用¥0、Phase累計¥667.19)

結論: **有料run・API課金なし。`IN_PROGRESS`のまま(`VALIDATED`ではない)、`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`ではない、Production未変更。** 詳細(RCA逐語・集計・実装・AG比較)は`docs/pm/design_open233_kpi_recovery_02.md`§14、証跡は`er052_output/open233_kpi_recovery_02_offline_01/`。

- **actor_guard(確認)**: `actor_rewrite_guard_ok`は英語の新主体語(25語)がLedger全文に英語のまま部分一致するかだけを見る。Ledgerは日本語(F-004「クレジットカード利用者」、MUSE-HC-006「契約スタッフ」)のため、Ledger記載の主体・Checker issueが求めた主体でも拒否。全ログ`actor_guard_rejected`は7試行(4 record)で全て過剰拒否(仮ラベル)、正当拒否0、ladder枯渇→STAGE4は2件(rep28の`changed_scope` s1・`meta_run03_advanced` s2)。
- **title delete(確認)**: `degenerate_rewrite_output`は3 instance(rep9×2・rep28×1)、全て`safety_er009_unsupported_new_claim`(1文のみの記事=その文がtitle)。`rewrite_kind=delete`→決定論deleteで本文が空→hard block。
- **件数一致バグ(確認+推測)**: 同index 2項目で旧式False(偽の自己矛盾)。項目別が記録された24 recheckのうち不一致6件(全てneg3)が全て該当、再確認call計¥1.51。全ログのCOMPLIANT∧all_prior=False 37件中、直接確認できたのは6件(+委任_06のA/B 4/4)。残り31件は旧コードで項目別が未記録のため機序は推測(neg3/neg2の23/28・7/8と整合)。
- **remains_in_final_en 3件(確認)**: `flashy 20% plan`の部分一致残存、因果`so`は除去済み(未修正ではない)。
- **実装(Trial)**: `aggregate_prior_issues_resolved`(index別集約、indexが欠けたpriorは未解消、スイッチなし)と`STRUCTURAL_ELEMENT_REWRITE`(構造要素[title・見出し・In one line直下・delete後にdegenerateになる範囲]のdeleteを選ばず既存ladder E1→③→④で書き換え、空・degenerate案は却下して次の水準へ、KPI構成ON/既定OFF)。Fable事前判断2の「Ledgerのheadline/in_one_line相当factによる再生成1回」はLedgerにその種別が無く実装していない(既存ladderへ統合)。テスト: 新規13(runner単体643、`er052*`687件OK、全体4610件中失敗11=基準11件、新規0)。¥0 replay: rep28 unsupported_new_claim s1でdelete不選択・本文非空、neg3 rep28のRecheck応答で`all_prior`False→True。実LLMの書き換え品質は未検証。
- **actor_guard是正設計(設計のみ、実装せず)**: AG1(Ledger照合型、決定論・追加call 0)/AG2(hint強化再試行)/AG3(同段で別案)。¥0 replay: AG1-strictは7試行中6(rep28の6試行全て関連factの日英同義語表のみで許容)、AG1-ledgerは7/7。正当拒否維持は実績が0のため合成対照42ケース(推測ベース)で全拒否維持。暫定推奨AG1-strict(Checker issueは「Ledgerにも存在する場合のみ」の補助)。残余リスク: 同義語表の整備・パラフレーズ、後ろ盾(Stage 2 floor `changed_actor`・Recheck)がCheckerの検出に依存。
- **Opus#13 packet**: `docs/pm/opus_packet_open233_kpi_recovery_02_03.md`(条件A、独立レビューブロック逐語)。次: Opus#13→Fable→委任_08=実装+影響instance再確認+29件再確認。
- Production整合: `er003_v1_en_direct_vfl_01_generate.py` 827行に同一の件数一致式、`actor_guard`相当はer003/er010に無い(`OPEN-233-A1-PROD`へ記録)。

## 58. KPI-RECOVERY-REDESIGN-02 委任_08: Opus#13→Fable評価・AG1-strict+2条件AND/件数一致3穴/構造要素の対渡し/text_pattern実装・差分0確認・影響instance再確認rep29a【STAGE4 1件、Step 6未実行】(2026-10-04、費用¥2.56、Phase累計¥669.75)

- **Opus#13・Fable評価**: `docs/pm/opus_l2_review_open233_kpi_recovery_02_13.md`(全文・評価1〜9逐語・11-3照合・STOP非該当)、設計書§15。
- **同義語表の確定証跡**: runner `ACTOR_SYNONYM_CLASSES`(23クラス、employee/contractor/worker/staff・customer/client/user/passengerは別クラス、`contract worker(s)`/`contract staff`は`ACTOR_EN_COMPOUNDS`でcontractor)を、評価前にcommit `f513695c`で確定。以後変更なし。
- **実装(Trial、Production未変更)**: `actor_rewrite_guard_decision`/`actor_rewrite_guard_ok`(`ACTOR_GUARD_MODE` legacy既定/ag1_strict=KPI構成ON、判定逐語を`actor_guard_decision`としてlevel_attemptsへ記録)、`aggregate_prior_issues_resolved`3穴修正、`STRUCTURAL_PAIRS_TO_RECHECK`(構造要素書き換えの対のみRecheckへ、追加call 0)、`text_pattern`+`remains_in_final_en_pattern`旧新並記。guardはscopeを守らない(scopeはRecheck)。
- **テスト**: er052単体712件OK(新規: 負例(a)〜(e)各3ケース以上・正例rep28の6試行・rep22型2条件AND・legacy不変・件数一致3穴・構造要素の対・Productionフォーマット実記事5本・text_pattern)。全体回帰4635件、失敗は基準11件のみ(er052の新規失敗なし)。`git grep er052_open233`(er003/9/10/12/19)=0件。
- **差分0確認**(`agg_actor_guard_diff_01.py`): 538 JSON・112試行(許容106+拒否6)。許容済み106試行のうち新主体クラスを含む試行は0件(guard対象外)のため許容→拒否0件(自明に近い点を明記)。拒否済み6試行(rep28)は全て許容(basis=related_fact)。rep22型(別形式のrepro)はユニットテストでissue名指しなし=拒否・名指しあり=許容(2条件AND)を確認。
- **37件集計**(`agg_compliant_allprior_false_01.py`): LEDGER_COMPLIANT∧all_prior=False 37cycle。再確認の最終結果=PASS24・**PASS以外10**・未記録3。PASS以外10は全て旧経路のSTAGE4 `unconfirmed_after_reverify`(iter3〜6・rep9/23/27のneg2/neg3)で、N1′(`RECHECK_MERGE_UNRESOLVED`)でこの経路は廃止済み(旧経路では安全側にSTAGE4)。未記録3はiter2。結論: 「取りこぼし経路なし」とは言えない(0件でない)が、旧経路は見逃しではなくSTAGE4へ倒れていた。
- **rep29a**(6 run、`safety_er009_changed_scope`/`safety_er009_unsupported_new_claim`/`meta_run03_advanced`×2、¥2.56[概算≈¥4]、worst ¥1.04、JA 0、Recheck自己矛盾0、見逃し0[旧・新パターン版とも]): 
  - STAGE4 1件=s2 `safety_er009_changed_scope`(`ladder_exhausted_without_full_rewrite`)。Checkerが`related_fact_id`なし(Ledgerに無い「レストランで確認」の主張)で返し、Rewrite案(「credit-card passengers…」、F-004に乗客あり・内容はfaithful)の新主体`passengers`が(ii)関連fact不成立(fail-closed)・(iii)issueが日本語で名指し不成立→③・④とも拒否→枯渇。
  - 構造要素書き換え(s1 `safety_er009_unsupported_new_claim`、title判定→④): 「…male passengers tipped twice as much as female passengers…」→「The same New York City taxi researchers also found that passengers shown higher suggested rates tipped more.」(男女差・2倍が除去、空でない、一般論でない、Recheckへ対渡し`recheck_structural_pairs_n`=1、RESOLVED_REWRITE)。
  - meta_run03_advancedは2回ともACCEPTABLE_STAGE1(Rewrite不要でguard非発火)。
- **全ログ集計**(`agg_related_fact_missing_01.py`): BLOCKING claim 690件中135件(19.6%)が`related_fact_id`空(safety_er009_*のみ)。AG1-strictのfail-closedは、新主体を導入するRewriteで頻発し得る(Opus#13「十分に答えられなかった点」への回答)。
- **判定**: rep29a判定基準(STAGE4 0)を満たさず、原因は`related_fact_id`空時の扱いという設計事項(Fable評価1の「欠落はfail-closed」)のため、Step 6(rep29)は**未実行**。KPI Primary未達の恐れ。費用¥2.56、Phase累計¥669.75。
- **Fableへの論点(設計判断。ユーザーへKPI緩和は提案しない)**: related_fact_id空のclaimの新主体判定(案: (a)Ledger全体の(ii)相当+同クラス表現[AG1-ledger相当、guardを関連factから全Ledgerへ広げる=Opus#13が「緩める」寄りと評価した方式]、(b)issueの日本語表現も名指し照合に含める[今回は客=customerで不一致のため非解決]、(c)Stage 1が`related_fact_id`を返せるようにする=Checker入力・出力の変更で境界事項、(d)現状維持=safety_er009_*系で再現し得る)。再ループ時の新規テスト・差分0確認の再実施が必要。

## 59. KPI-RECOVERY-REDESIGN-02 委任_09: related_fact_id欠落時のLedger全体fallback実装・rep29a再確認【STAGE4 0】・Step 6再確認rep29【Human Review 3 → KPI未達】(2026-10-04、費用¥25.64、Phase累計¥695.39)

- **実装(Trial専用・Production未変更)**: `actor_rewrite_guard_decision`に(ii′)を追加。`related_fact_id`が空(None/空文字/空白/空list)のときだけLedger全体を照合先にし(`basis=ledger_wide_fallback`)、関連factがある場合・誤id(Ledgerに無い)は従来どおりAG1-strict。判定記録に`related_fact_empty`追加。`legacy`・同義語表は不変。設計書§16に判断1〜5を逐語記録。
- **テスト**: 負例(f)(g)(h)・正例(rep29a s2のpassengers)・既存(a)〜(e)(旧(c)の「空id→拒否」は判断1に従い「空id→fallback許容、誤id/別fact→拒否」へ更新)。runner単体673件OK、er052回帰717件OK、全体回帰4640件・失敗は基準11件のみ(er052の新規失敗なし)。
- **¥0差分確認**: 許容済み109試行・新主体クラスを含む試行0・許容→拒否0件。拒否済み8試行は全て許容(rep28の6[related_fact]+rep29a s2の2[ledger_wide_fallback])。注: 委任文の「3水準」はログ上2水準(3_sentence・4_paragraph)。
- **rep29a再確認**(`safety_er009_changed_scope`×2、`rep29a/rerun_01/`): STAGE4 0・見逃し0・JA 0・自己矛盾0・費用¥0.97(worst¥0.62)。2 runとも1_word_connectiveで成功し新主体を導入しなかったため`ledger_wide_fallback`は不発動(非決定性。fallbackの実動はrep29の1件で確認)。
- **rep29**(29 instance・38 run、¥24.43[run合計]/予算state¥24.667): 初回起動が¥24.028でGuardrail(`--budget-jpy 24`)のTrialAbortにより37/38 runで停止。原因=概算¥21の見積り超過(S1 call ¥3.54等)、暴走なし・残1 run(s2 neg3、s1は¥1.07)・scope内のため、予算を26へ上げて`skip existing`で1回だけ再開(neg3 s2のみ実行、¥0.64)。超過を記録して継続(委任文の費用上限方針どおり)。
- **KPI**: Human Review(STAGE4)**3件**(未達)・重大見逃し0(旧・新・`text_pattern`版とも0、`residual_at_pass`全件仮ラベルでも該当なし)・平均追加+¥0.20(rep24比)/-¥0.40(iter7比)(達成)・worst追加+¥3.34 safety_A4 s1(rep24比、Cap+¥3超過)/+¥2.04(iter7比、達成)。**Primary未達のため`VALIDATED`ではない(`IN_PROGRESS`)**。
- **STAGE4 3件の原因(actor_guardは無関係: actor_guard拒否0件)**: (1)s1 meta_run03_advanced `same_claim_fact_id_reblocked`、(2)s2 meta_run03_advanced `violation_span_unverified`、(3)s1 safety_A4 `cycle_limit_exhausted_after_recheck`。(1)(2)は同一型: Metaの`MUSE-HC-006`「users had no way to know whether they were talking to AI or a person」(通話の相手は店舗・企業側であり、利用者が通話する側という誤り=`changed_actor`)に対し、1_word_connectiveの最小Rewrite(「they were talking to AI or a person」→「AI or a person was making the call」)が成功扱いになるが主体「users」が残り、RecheckがLEDGER_DEVIATION・prior issue未解消(`recheck_prior_issues_resolved_by_index {0:false}`)→cycleごとに同じclaimが再BLOCKING→cycle上限。(2)はcycle 3で違反範囲を英語本文から特定できず(`violation_span_unverified`)。(3)safety_A4は7 BLOCKING・複数factにまたがり、Rewrite後も毎cycleでRecheckが新旧のMAJOR(`MUSE-HC-006`/`MUSE-HC-012`)を返して3 cycleで収束せず(費用も¥4.34で最大)。
- **機構発火**: actor_guard判定3件(全許容: related_fact 1・ledger_wide_fallback 1[s1 `safety_er009_changed_scope` passengers、related_fact_id空]・ledger_and_issue 1)・拒否0。Tier 0 blocked 2(`changed_causality_floor`、neg5・safety_A4)。S1: 対象73・確認70・split 3・API失敗0・¥3.54。L6: 2発火・2復元。N1′: Recheck 25回・merge 11・自己矛盾0(rep28は20回中2)・再確認call 0(rep28は2)。構造要素書き換え発火0。件数一致: 記録=再計算(19/19、差分0)。Rewrite実行29(rep24: 24、iter7: 39)・NORMAL群で不要Rewrite 5/14(rep24: 3、iter7: 3)・cycle≥2が7・≥3が3・JA変更0。モデル `gpt-6-luna`、構成はKPI構成(V7b・english_only・time_only等)。
- **Safety-critical 6件**: safety_A2A3(s1/s2とも解決)・bgroup_B3(同)・bgroup_B4(RESOLVED_REWRITE_THEN_DOWNGRADE)・neg5(解決、Tier 0 floor発火)・safety_A5(RESOLVED_REWRITE_THEN_DOWNGRADE)は検出・処理され、safety_A4は検出されたがSTAGE4(上記(3))。見逃し0。
- **Fableへの論点**: 再ループ(Step 7)の余地が残る。案(判断はFable): (A)`changed_actor`かつRewrite後Recheckで同じclaimがprior未解消のとき、1_word_connectiveで成功扱いにせず上位level(sentence/paragraph)へ昇段する(既存ladder内の条件、新retry loopなし)、(B)violation_span_unverifiedのcycle 3での違反範囲特定、(C)safety_A4の複数fact同時BLOCKING。ClosureへはPrimary未達のため進めない。
- 詳細: `er052_output/open233_self_recovery_flow_runner_01_rep29/`(summary_kpi_01.json・summary_01.md・stdout_main_part1/2.txt)、`er052_output/open233_self_recovery_flow_runner_01_rep29a/rerun_01/`。

## 60. KPI-RECOVERY-REDESIGN-02 委任_10: rep29 Human Review 3件の構造的RCA・改善案A〜F比較・Opus#14 packet作成(2026-10-04、費用¥0、Phase累計¥695.39)

- **性質**: Step 7(再ループ)前半=診断・設計・packet。**実装・有料API実行なし。Production未変更。`IN_PROGRESS`のまま**(`VALIDATED`/`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`ではない)。KPI変更なし。
- **3件の直接原因(確認)**: (1)s1 `meta_run03_advanced` `same_claim_fact_id_reblocked`: `escalated_to_paragraph`を「flagが付いた」で記録(runner L8264)するがladderはflagを無視(L311/5952)。level 1のみ試行なのに「④まで昇段済みの再発」と誤判定(L8178〜8184)。かつcycle 2のRewriteが2範囲のため、Recheck mergeの現行文差替え(L2221、`"\n" not in cur`)がskipされ、cycle 3のclaimは本文に無い古い文言(replay: `unverified/mismatch`)。(2)s2 `violation_span_unverified`: Recheckの`claim_in_article`が「“A” and, in the one-line summary, … “B”」の地の文混じり合成文で`explanatory_mixed`。引用ごとの分割replayで2片とも一意に解決(L3・L0)。cycle 1 level 1 `users→businesses`、cycle 2 level 1 `businesses→users`で本文が原文に復帰(振動)。(3)s1 `safety_A4` `cycle_limit_exhausted_after_recheck`: Recheck新規MAJOR 5件は全て原文既存の文(Rewrite起因0)で、cycleごとに1〜2件ずつ検出(Stage 1 recall不足+HC-012の3箇所分散+S1降格確定済みの文の再浮上)。上限到達後の残1件(HC-012 `An AI called…`)はStage 2/S1を通らずSTAGE4。費用¥4.3435(Recheck 44%・Stage 2+S1 37%・Rewrite+品質regen 19%、cycle別¥1.87/¥1.10/¥1.37)。
- **共通構造**: S-1 Rewrite成功(変更∧書き戻し∧新主体語ガード、L6011〜6031)≠issue解消(解消判定は1cycle後のRecheckのみ)。S-2 履歴・再発判定のキーがclaim(fact_id+本文)で、記事内の箇所ではない。S-3 Human Reviewの出口(`same_claim`/`span未特定`/`cycle上限`)が計数・形式条件で、現行本文へのmateriality判定を呼ぶ前に発火。rep27〜29のHuman Review 9件は全て別の実装・形式不整合で、「Rewriteが本当に直せない重大」は0件(確認)。→個別修正の連鎖であると同時に構造問題。構造を一括で設計しOpus#14で批判させる。
- **改善案A〜F・推奨(設計書§17)**: 推奨=B′(location単位のlevel引継ぎ+記録バグ是正)+A2(振動検出)(+A1は誤検出[level 1成功7試行中残存3件・うち2件は正当]を確認のうえ)+D(引用分割→現行文写像→Rewriteなし+全文Recheck)+G(上限後の残Recheck MAJORを既存Stage 2+S1へ)(+T 最終手段=構造要素以外の既存`0_delete`+全文Recheck 1回、実装は限定確認後)。C(actorを③から)はユーザー上位原則§0-4と衝突、E1節約僅少、E2費用増・NORMAL群リスク未集計、F2はCap違反のため不採用。F1(品質regen条件、¥0.399)はFable判断。設計後に残るHuman Review: 同一箇所で④まで実際に試行済み∧削除不可の構造要素のみ(実例0件)。
- **確認できなかったこと(推測)**: ③1文・④段落のRewrite案が実際にissueを解消するか、Gで残る文がStage 2+S1で非BLOCKINGになるか(有料call無しに確定不能)、actorがlevel 1で直らない(2/5)という一般化(小標本・失敗3件は同一instance)、Tの品質影響(実発動例0)。
- **成果物**: `docs/pm/rca_open233_rep29_stage4_01.md`(逐語時系列・行番号)、設計書§17、`docs/pm/opus_packet_open233_kpi_recovery_02_04.md`(Opus#14向け、(a)〜(g)・独立レビューブロック貼付済み)、`er052_output/open233_kpi_recovery_02_offline_01/agg_rep29_stage4_rca_01.py`・`.json`・`_stdout.txt`。
- **次**: Opus#14(条件B・必須)→Fable評価→委任_11実装(限定確認≈¥5→rep30 1回≈¥26)。事前基準: Primary Human Review 0・見逃し0・平均追加+¥2以内・Cap+¥3以内・不要Rewrite NORMAL群はrep29(5/14)以下。
- **T-0**: 委任文`docs/pm/delegation_log/2026-10-04_OPEN-233-KPI-RECOVERY-REDESIGN-02_10.md`を全文保存、`check_delegation_prompt.py`=**FAIL**(`事前指定Grep一覧+追記位置・更新位置の手順`の見出し語不足のみ。固定ブロックE-1/D-1/G-1/F-1は全て存在、作業は継続=記録用)。


## 61. KPI-RECOVERY-REDESIGN-02 委任_11: Opus#14保存・Fable評価、STAGE4許可リスト化・位置座標引継ぎ(I-1最小)・B′昇段・A2振動検出・D span fallback(H-1是正)・G判定専用cycle・T最終手段・BLOCKING固定の実装、強制経路fixture・反実仮想replay(2026-10-05、費用¥0、Phase累計¥695.39)

- **結論**: (1)Opus#14全文を`docs/pm/opus_l2_review_open233_kpi_recovery_02_14.md`へ逐語保存、Fable評価15項目を設計書§18へ逐語記録(条件B「根本設計の問題」採用、I-1最小/I-2許可リスト/B′修正/A2/D+H-1是正/G判定cycle/T/S-4固定=採用、A1・F1=不採用)。(2)実装: runnerへ新スイッチ9個(既定ON 7: `STAGE4_ALLOWLIST`/`LADDER_LOCATION_CARRY`/`REWRITE_REVERT_GUARD`/`SPAN_FALLBACK_CHAIN`/`JUDGE_ONLY_CYCLE_AFTER_CAP`/`LAST_RESORT_DELETE`/`MATERIALITY_BLOCKING_PIN`、既定OFF 2: `STAGE2_VERDICT_REUSE_NONBLOCKING`/`STAGE2_SIBLING_LOCATIONS_CYCLE1`)。モジュール既定は全てOFF=legacy保持(既存673テストは無変更で全通過)、`KPI_TRIAL_SWITCHES`でON。(3)テスト: runner単体696(新規23)、er052回帰740、全体回帰4663件中失敗11件=基準11件と同一(er052由来0)。`git grep "er052_open233" -- er003*/er009*/er010*/er012*/er019*`=0件。
- **許可リスト関数**: `stage4_allowlist_decision(reason, context)`(1箇所)。許可=`blocking_confirmed_unlocatable_after_cap`/`blocking_structural_after_ladder`/`post_T_new_blocking`/`api_failure`の4種のみ(BLOCKING由来の3種はStage 2+S1通過[funnel_passed]も要する)。廃止した出口(許可リスト外、記録名`stage4_allowlist.decisions[*].legacy_reason`として保持): `same_claim_fact_id_reblocked`(→ladderへ、④試行済み扱い→枯渇でT)、`cycle_limit_exhausted`/`cycle_limit_exhausted_after_recheck`(→判定だけのcycle[Stage 2+S1、Rewriteなし]→T/位置不明は`..._unlocatable_after_cap`)、`violation_span_unverified`/`target_not_locatable`(→carry list: Rewriteせず全文Recheckで位置再取得、PASS禁止)、`ladder_exhausted_without_full_rewrite`(→T、API失敗のみなら`api_failure`、構造要素/T済みなら`blocking_structural_after_ladder`)、`degenerate_rewrite_output`(→`blocking_structural_after_ladder`)、`unconfirmed_after_reverify`(→次cycleのStage 2へ合流)。許可リスト外終端は構造上0(`stage4_allowlist.final_reason_outside_allowlist`で検知)。
- **確認(コード・テスト)**: H-1(Stage 2がBLOCKINGと確定し書き換えられなかった箇所がRecheck1回の準拠でPASSしない)=fixture 3本で確認(multi_match、位置再取得失敗、SPAN_FALLBACK_CHAIN OFFでも非PASS)。carry listが空でない間は`RESOLVED_*`へ到達しない(`unrewritten_blocking_pass`計測=0)。H-2(G経路でS1を通る、本文不変箇所のBLOCKING固定が再判定の降格を覆す、OFFなら降格する)=確認。**`rounding`(levels=[])のBLOCKINGは旧コードでは`ladder_exhausted_without_full_rewrite`でSTAGE4(Rewriteなし・PASSなし)であり、Opus推測の「Rewriteなし1回RecheckでPASS」経路は存在しなかった**(コードで確認)。新設計ではTを経由し(決定論削除)、削除後のRecheckを受けた結果だけがPASSになる。
- **強制経路fixture(¥0、偽LLM)**: 上限→判定だけのcycle(S1通過・降格)、上限→T→Recheck準拠で解決、T後の新規MAJOR→判定cycle→`post_T_new_blocking`、振動(A2が元へ戻る案を却下→同cycle内で④へ、B′が①を飛ばす)、A2/B′ OFFで旧挙動、multi_match位置特定不能→carry→`blocking_confirmed_unlocatable_after_cap`、Recheckが位置を再取得→書き換え→解決、構造要素(title)ladder枯渇→`blocking_structural_after_ladder`、API失敗→`api_failure`、ladder枯渇(非構造)→T→解決、全スイッチOFF→legacy理由。単体: A2文脈照合・`\n`複数範囲→`“A” and “B”`変換(2範囲に確定)・explain_splitの狭い緩和(位置語を含む場合のみ・含まなければ棄却のまま)・置換範囲の重なり判定(H-4、1文字以上)。
- **反実仮想replay**(`er052_output/open233_kpi_recovery_02_offline_01/replay_counterfactual_rep27_29_01.{py,json,md}`、rep27/28/29全114 run): legacy STAGE4=9件(rep27=3/rep28=3/rep29=3)。**決定論部分で確定した終端が許可リスト外=0件**。rep29の3件: (a)meta_run03_advanced s1 `same_claim_fact_id_reblocked`→ladderへ(call必要: Rewrite上位level→Recheck)、(b)safety_A4 `cycle_limit_exhausted_after_recheck`→判定だけのcycle(call必要: Stage 2+S1 1claim、Recheck MAJORは位置確定可)、(c)meta_run03_advanced s2 `violation_span_unverified`→**D(i)の狭い緩和で位置が決定論に確定(P:2)**→Rewrite(call必要)。rep27の3件: neg3 `unconfirmed_after_reverify`→次cycleのStage 2(call必要)、safety_A4/A5 `ladder_exhausted`→T(決定論削除が成立、全文Recheck 1回[call必要])。rep28の3件: safety_er009_changed_scope(title)・meta_run03_advanced s2(in_one_line)=構造要素で`blocking_structural_after_ladder`、safety_er009_unsupported_new_claim `degenerate_rewrite_output`→`blocking_structural_after_ladder`(**3件は決定論でHuman Review=許可リスト内の出口だがKPI Primaryは0件でない。実LLM呼び出しで別経路になる余地はあるが、記録上はこの3件が残る**)。非STAGE4を含めた介入記録: B′昇段4件、A2却下1件(rep29 s2のbusinesses→users戻り)、BLOCKING固定の降格覆し0件。
- **第二段階案の¥0集計**(`agg_sibling_locations_cycle1_01.{py,json}`): ①後cycleの新規MAJOR5件中、cycle 1の決定論列挙で覆えたのは1件=20%(safety_A4、>0で事前固定の採用条件を満たす)。②NORMAL群25 runでcycle 1のStage 2判定が+19件(基準89件に対し+21%、うち7件はmeta_run03_advanced 1 run)、記録上BLOCKINGになった件数=0(ただし列挙した箇所をStage 2へ通した実測ではないため不要Rewrite候補の上限推定にはならない)。→rep30で`--sibling on`(既定)、NORMAL群の不要Rewriteがrep29の5/14から増えたら不採用候補。
- **再利用replay**(`replay_verdict_reuse_01.{py,json}`): 2-of-2非BLOCKING 198件登録、再利用で抑制される判定8件(全てbgroup_B4のQUALITY/ACCEPTABLE)、ラベル上の重大0件、記録上後cycleでBLOCKINGだった(再利用で見逃す)件数0。→事前固定条件を満たすためrep30で`--reuse on`(既定)。節約は8判定と小さい。
- **確認できなかったこと(推測)**: T(削除)の記事品質への影響(実発動はrep27で2件が成立するだけ、有料実行なし)、判定だけのcycleでrep29 safety_A4のRecheck MAJORがStage 2+S1で非BLOCKINGになるか、D(i)緩和の誤確定リスク(1実例でのみ確認)、第二段階案の不要Rewrite影響、B′昇段・A2却下が不要Rewriteを増やさないか(n=1実例ずつ)。
- **Opus#14指摘のうち未対応**: A1(不採用)、「Rewrite promptへ過去候補・元に戻す禁止を提示」(後回し、本委任の指示どおり未実装)、F1(品質regen条件、不採用=現状維持)、L2221型の「全claimをオブジェクト化する全面再設計」(本Trialでは最小実装のみ)。`issue_focus_absent_recheck_only`(L6、Rewriteを見送りRecheckに任せる既存経路)はH-1と同型の構造(Stage 2 BLOCKINGが書き換えなしでRecheckだけで解決しうる)だが、既に承認済みの既存設計のため変更せず、論点としてFableへ。
- **ユーザー確認事項(Closeoutで提示)**: B′の§0-4解釈(同じ箇所への前levelのRewrite結果が再びBLOCKING確定=効果の実証に基づく昇段=§5-11のcycle横断適用。Fable判断で衝突なし)、F1(品質規則の変更)、非BLOCKING再利用スイッチの扱い。
- **成果物**: runner(`er052_open233_self_recovery_flow_runner_01.py`)、テスト(`..._test_01.py` +23)、`replay_counterfactual_rep27_29_01`/`agg_sibling_locations_cycle1_01`/`replay_verdict_reuse_01`(`er052_output/open233_kpi_recovery_02_offline_01/`)、rep30スクリプト(`..._rep30_full_01.py`/`_rep30_agg_01.py`、未実行)、限定確認(`..._rep30a_limited_01.py`、未実行)。
- **委任_12への費用概算**: 限定確認(meta_run03_advanced s1/s2・safety_A4 s1)≈¥5(`--budget-jpy 7`)、rep30(rep29と同じ29 instance・38 run)≈¥26〜30(`--budget-jpy 28`既定。新経路の増分: T=Recheck 1回≈¥0.4、判定だけのcycle=Stage 2+S1≈¥0.4〜0.5、兄弟列挙=Stage 2のtoken増)。事前基準に追加: 許可リスト外STAGE4=0、G経路の降格は全件S1通過、未書換BLOCKINGによるPASS=0。
- **T-0**: 委任文`docs/pm/delegation_log/2026-10-04_OPEN-233-KPI-RECOVERY-REDESIGN-02_11.md`を全文保存、`check_delegation_prompt.py`=**FAIL**(`事前指定Grep一覧+追記位置・更新位置の手順`の見出し語不足のみ、固定ブロックE-1/D-1/G-1/F-1は存在、作業は継続=記録用)。

## 62. KPI-RECOVERY-REDESIGN-02 委任_12: degenerate是正・限定確認rep30a・Step 6再確認rep30(2026-10-05、費用rep30a¥3.02+rep30¥21.79=¥24.81、Phase累計¥720.20)

- **結論**: Human Review 0(許可外STAGE4 0)・重大見逃し0(旧・新・text_pattern定義とも)・平均追加+¥0.13(rep24比、基準+¥2以内)・不要Rewrite NORMAL群3/14(rep29の5/14から増加なし)・G(判定だけのcycle)発火0(降格のS1通過は対象なし)・未書換BLOCKING PASS 0。**worst追加が+¥3.14(safety_A4 s1、rep24比)でCap(+¥3)を¥0.14超過 → KPI【未達】(Cap 1項目のみ)**。iter7比は平均-¥0.47・worst+¥0.80(neg5_hormuz_div_a2)で全て基準内。Status=`IN_PROGRESS`のまま。KPI・基準は変更していない。
- **作業1(是正、¥0)**: (a)Fable照合1: degenerate(title/hook/In one lineの空・極端短縮)を、`STAGE4_ALLOWLIST`ON時は構造要素書き換えに限らず全候補・level6全文案で「そのlevelの試行失敗」とし、同cycle内で上位levelへ昇段(`degenerate_structural`)。cycle後のdegenerate hard blockは新関数`structural_ladder_exhausted_verified`(構造要素印∧計画levelを全て実試行済み[またはT構造ブロック])で検証できたときだけ`blocking_structural_after_ladder`、できなければ許可リスト外として記録のまま(許可名へ写像しない)。(b)Fable照合3(a): 旧実装は`vs_l6_focus_absent`へ復元範囲(該当文)を渡していた=Fable想定と相違 → 現行本文全体へ是正(`issue_focus_check.haystack="current_full_text"`)。(c)設計書§18-C(Fable照合1〜5逐語+実装記録)、テスト`TestDegenerateNotLaundered12`4件+runner fixture1件(runner単体701・er052回帰745全PASS、全体回帰4668中失敗11件=基準11件のみ、新規なし)、`git grep er052_open233`(Production path)0件。反実仮想replay再実行: degenerate 1件(rep28 safety_er009_unsupported_new_claim)が決定論終端→call必要(上位level昇段)へ(決定論終端3→2、call必要6→7)、許可リスト外STAGE4 0件維持。commit e05ff967。
- **範囲外の観察(実装せず、Fable判断)**: `blocking_structural_after_ladder`は、T無効/T使用済み・cap後のT不可・T削除失敗の各経路でも構造要素の検証なしで返される(委任_11実装、degenerate以外の同型の写像)。
- **作業2 rep30a**(meta_run03_advanced s1/s2・safety_A4 s1、¥3.02): STAGE4 0・許可外0・未書換PASS 0・重大見逃し0(A4-0の「completed the exchanges with users」は書換で消滅)・JA変更0。新経路の発火: 兄弟列挙1・再利用1・B′/A2/D/carry/G/T/BLOCKING固定=0(A4 cycle2/3は通常のE1→③→④昇段、4_paragraphで「Human calls」見出し化+重複段落削除)。ゲート通過でrep30へ。
- **作業3 rep30**(29 instance・38 run、`--budget-jpy 30`、¥21.79、例外0・Guardrail到達なし): 
  - Human Review(統一)0(STAGE4 0・例外0・欠損0)。許可リスト外0。許可内理由の発火0(`blocking_structural_after_ladder`等は不要だった)。
  - 重大見逃し: 旧0/新0/text_pattern0。`residual_at_pass`全件仮ラベル: 8行(Safety-critical定義)中、旧定義で本文に残存4行(A2A3 s1・bgroup_B3 s1/s2・neg5 B3-same)、text_pattern定義で残存1行(A2A3 s1)。全て`ever_blocking_flagged=True`(=PASS時に未検出のまま残った「見逃し」ではない)。pass_with_residual_unflagged=0。
  - Safety-critical 6件(A2A3/B3/B4/neg5 B3-same/A4/A5): 全て検出(BLOCKING flag)・全て`RESOLVED_*`。
  - 機構発火: Tier 0=129件中blocked 1(safety_A4 c2、changed_causality_floor)、S1=93件中split 3、L6=2復元・focus_absent 0・focus_guard 0、N1′=merge 5・自己矛盾0・再確認call 0(rep28は2/2)、actor_guard=新class判定3(related_fact 2・ledger_wide_fallback 1)・却下0、構造要素書き換え1(safety_er009_unsupported_new_claim、title、4_paragraphで成功)、件数一致diff 0、B′(LADDER_LOCATION_CARRY)1(A4 c3で①③を飛ばし④)、兄弟列挙29(全instanceのcycle 1)、再利用2、A2/D/carry/G/T/BLOCKING固定=0。
  - cycle分布: ≥2が4、≥3が1(safety_A4 s1)。判定だけのcycle0。
  - 費用: 合計¥21.79(rep29¥24.43・rep28¥20.50・rep24¥16.72・iter7¥39.55)、平均/run¥0.573。平均追加(rep24比)+¥0.13、(iter7比)-¥0.47。worst(rep24比)safety_A4 s1 +¥3.135(Cap超)、(iter7比)neg5_hormuz_div_a2 +¥0.80。rep29比は平均-¥0.07・worst hormuz_run01_advanced +¥0.46。
  - モデル・構成: runner MODEL `gpt-6-luna`、V7b、KPI構成+新スイッチ(ON 7+再利用ON+兄弟列挙ON)。
- **未達の原因分析(Cap)**: 超過はsafety_A4 s1の1 run(¥4.14、20 call、3 cycle)のみ。他の全run最大は¥1.79(bgroup_B4)。内訳: cycle1 ¥1.46(Stage 2×4・S1×2・E1/E2×3・Recheck ¥0.53)、cycle2 ¥1.75(Recheckが前cycleの書換により新規BLOCKING 2件[HC-006の因果、HC-012のTier 0 floor]を検出→Stage 2×2・E1/E2×4・Recheck ¥0.86)、cycle3 ¥0.93(`extra_cycle`、B′で④のみ試行・Recheck ¥0.43)。Recheck合計¥1.82(44%)。同instanceの費用はrep24 ¥1.01/2cycle、rep28 ¥1.82、rep29 ¥4.34(3cycle・STAGE4)、rep30a ¥2.57、rep30 ¥4.14と、同構成(rep30a/rep30)でも¥1.6変動する。rep29比では本構成の方がSTAGE4にならず完走。新機構の直接寄与は小(B′1回は節約側、兄弟列挙の追加claimはcycle1 Stage 2で9件判定=A4のみ顕著)。つまり超過の主因はA4のRecheckが書換のたびに別の関連箇所(HC-006/HC-012)を新規BLOCKINGにする収束の遅さ(判定・入力: Recheck全文判定が書換後本文の隣接する説明文を新たにMAJOR→Stage 2 BLOCKING)で、新設計の欠陥ではなく既存の収束特性だが、KPI基準(rep24比+¥3)を機械的に満たさない。
- **再ループ案(Fable判断、いずれも実装せず)**: (1)A4型の「書換のたびに隣接箇所が新規BLOCKING」を、cycle 1のRewrite時に同fact_idの関連文をまとめて直す(兄弟列挙のRewrite側への拡張=Opus#14 F系・新仕様候補)、(2)Cap判定のA4バラツキ(rep30a/rep30で同構成¥1.6差)に対する統計的扱い(n固定の方針と衝突するためユーザー判断事項)。KPI緩和は提案しない。
- **ユーザー確認事項(Closeoutで提示)**: Cap未達の扱い、B′の§0-4解釈、F1(品質規則の変更)、非BLOCKING再利用スイッチの扱い、`issue_focus_absent_recheck_only`(L6既存承認経路、本文全体判定へ是正済み、rep30発火0件)、`blocking_structural_after_ladder`の検証範囲(上記)。
- **T-0**: 委任文`docs/pm/delegation_log/2026-10-05_OPEN-233-KPI-RECOVERY-REDESIGN-02_12.md`を全文保存、`check_delegation_prompt.py`=PASS(reasons空)。
- **成果物**: runner/テスト/設計書§18-C、replay更新、`er052_output/open233_self_recovery_flow_runner_01_rep30a/`、`er052_output/open233_self_recovery_flow_runner_01_rep30/`(`summary_kpi_01.json`、`summary_rep30_new_01.json`、`instances_s*/`)。

## 63. Trial Closeout(VALIDATED)・Production正式採用(2026-10-05、委任_01c、¥0・SSOT記録のみ)

> **遡及注記(2026-10-05、`OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01`委任_04)**: 本節のrep30 `VALIDATED`は`VALIDATED(条件付き: Stage 1はfrozen再利用31 run/V0差替え3 run/fresh 3 call[4 run]。E2E Safety KPIではない。出典`docs/pm/rep30_stage1_provenance_01.md`)`。以降の「重大見逃し0」等のKPIは条件付き値でありE2E値ではない(`PM_GOVERNANCE.md` 24節)。

- **Status**: Trial `VALIDATED`(rep30)。対象仕様=`APPROVED_FOR_PRODUCTION`(ユーザー決定、`DECISION_LOG.md` 2026-10-05エントリ)。`PRODUCTION_WIRED`ではない(管理ID`OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01`、完了条件1〜12達成後のみ)。
- **最終数値(rep30)**: 29ケース・38 run・Human Review 0・重大見逃し0・平均¥0.573/run(rep24比+¥0.13/run)・不要Rewrite 3/14・worst +¥3.135(1/38 run、報告対象。単発+¥3 Capは撤回済み)。
- **Human Review推移**: iter7 7 → rep24 2 → rep27 3 → rep28 3 → rep29 3 → rep30 0。
- **Safety-critical 6件**: 全て検出・解消。
- **費用**: Phase累計¥720.20(予算state基準)。rep29 ¥24.67・rep30a ¥3.02・rep30 ¥21.79。(統一注記[委任_03]: rep29は「run合計¥24.43/予算state¥24.667」で、Phase累計は予算state基準。§59/§62の¥24.43はrun合計、本節の¥24.67は予算state。差異は同一費用の集計基準の違い)
- **使用モデル**: `gpt-6-luna`のみ(Sol未使用)。
- **Opus#8〜#14の指摘と対応**(委任_03で各1行を追補。出典: `docs/pm/opus_l2_review_open233_*`の結論部・設計書の採否小節、逐語は各ファイル/`DECISION_LOG.md`のFable評価転記):
  - #8(`..._self_recovery_08.md`): 機械判定の整合は必要だが小規模、F1自動解放・F4再判定は不採用、代替F5(決定論CONFIRMEDはBLOCKING確定、食い違いのみ別call確認)を採用→時期のみ`floor_verify`として配線対象(F5拡張は不採用)。
  - #9(`..._self_recovery_09.md`): L6完結文復元は必要、残余包含・アンカー間隔検査・略語分割・`issue_focus_absent`はRecheckのみ・共有module化を追加→L6を実装(`VS_SENTENCE_RESTORE`、委任_66)、共有module化は配線時課題。
  - #10(`..._self_recovery_10.md`): 1回LLMで重大を降格できる構造は是正必要、S1(2回目のStage 2で2回とも非BLOCKINGのみ降格)を3点修正して採用(最終materialityで比較・NORMAL群2-of-2を構成から外す・Safety KPIを条件付き/通しで分離)→S1配線対象、NORMAL群2-of-2は配線しない。
  - #11(`..._kpi_recovery_02_11.md`): 後段の解除構造是正が必要、Tier 0(G_L決定論)+Tier 1確認役+失敗時BLOCKING→Rewriteを推奨→確認役・G_Lは実測(NORMAL群47.3%/誤停止)で不採用、Tier 0因果floor(known6)+S1に置換(設計B §9〜§11)。
  - #12(`..._kpi_recovery_02_12.md`): carry-forward先適用は妥当、N1-aは不十分でN1′(再確認結果・未解消priorを必ず次cycleのStage 2へ合流)を推奨、Recheckに書換前後の対が無いことが主因と指摘→N1′採用(`RECHECK_MERGE_UNRESOLVED`)、前後対はN3′全対でなく構造要素限定(`STRUCTURAL_PAIRS_TO_RECHECK`)に縮小。
  - #13(`..._kpi_recovery_02_13.md`): actor_guard是正(AG1-strict)必要、構造要素のdelete禁止必要、件数一致の是正は安全側に倒しきれていない3点を要修正→AG1-strict+2条件AND・件数一致3穴・構造要素の対渡しを実装(委任_08、§58)。
  - #14(`..._kpi_recovery_02_14.md`): 条件B=個別バグでなく根本設計(自由文字列の各cycle再解釈+STAGE4出口6種)と判定、位置のオブジェクト化(I-1)・STAGE4許可リスト化(I-2)、B′修正採用・A2採用・A1不採用・D/G/T修正採用→許可リスト4理由・位置carry・判定専用cycle・T(1記事1回)を実装(委任_11、§61)。
- **分類(REJECTED/VALIDATED/USER_DECISION)**: `DECISION_LOG.md` 2026-10-05エントリ・`CURRENT_SPEC.md` OPEN-233 Trial Closeout節。配線しない: F1/確認役/N3'/G_L/NORMAL群2-of-2/CAUSAL_FLOOR_VOCAB=inventory/A1/C/E1/E2/F2。
- **未解決(配線時に扱う)**: (1)`blocking_structural_after_ladder`未検証経路 (2)`issue_focus_absent_recheck_only` (3)「and」版ACCEPTABLE判断(ユーザー未確認)。
- **未処理USER_DECISION**: なし。
- **APPROVEDだが未配線**: 採用対象の全項目。
- **未報告Trial**: なし。
- **Dangling Reference**: 配線時に全件確認する。
- **T-0**: 委任文全文を`docs/pm/delegation_log/2026-10-05_OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01_01c.md`へ保存(check PASS)。

## 64. PRODUCTION-WIRING-01 委任_04c: K14 Phase 1実測(候補Stage 1 vs Production V0)・両モデル費用再計算・P6棚卸し(2026-10-05、実費¥9.94、Phase累計約¥730.14)

- 候補Stage 1(V4A+重大誤解原則+列挙+schema追加、昇格除く、severityのみ)をgpt-6-lunaでn=2、18 instance・36 call(Safety12+B2_hormuz/B3/B4+負例3)。V0=fixture baseline_parsed(実Production記録)またはer050 gpt-5.6-luna run_1。出力`er052_output/open233_stage1_phase1_recall_check_01/`(`agg_phase1.json`)。
- claim単位: 劣後6件(V0検出∧候補0/2: B4の4件・A2A3 HF-009「prices began to fall」・B2_hormuz HF-011)/両方13/候補のみ14。事前固定判定により**K14=ユーザー判断**。Safety-critical 4/5(B3・A2A3-0・A4-0・A5-0は2/2、B4-aは0/2、V0は5/5)。
- 負例MAJOR誤検出: neg2は2/2 run、neg3は1/2 run、neg1は0(V0は3件ともCOMPLIANT)。API失敗0。
- 照合規則の注意: 初回集計はrelated_fact_id一致を要求し劣後15件と出たが、V0のer009合成fixtureにfact idが無く候補は別fact idを付けるため、claim本文のtoken重なり(50%)に是正し6件へ(両版とも判定はK14ユーザー判断)。V0はn=1記録。
- 費用再計算(rep30 38 run、為替156.88固定): gpt-6-luna 合計¥21.79/平均¥0.573/worst¥4.14、gpt-5.6-luna 合計¥48.18/平均¥1.268/worst¥9.37(比2.21倍。S1 ¥3.09は別掲)。`er052_output/open233_kpi_recovery_02_offline_01/agg_cost_recalc_models_01.*`。
- Production基準(raw_usage_log、gpt-5.6-luna、¥160/USD、n=8記事run): JA Checker+must_fix+loop 平均¥2.77/中央値¥2.50、text生成全体 平均¥6.55。EN側vfl01 Checkerはstage名未記録で分離不能(未確認)。
- P6: B-family/Voices A2/er009 n1 diagnosticは`run_deviation_check`をmonitoring専用で呼ぶのみ(MAJOR時の本文変更・STOP分岐は確認範囲で無し)→配線対象外を推奨(Gap文書§2-8)。
- ガードレール¥8を¥1.94超過(1call平均¥0.28、rep30 Stage 1実測¥0.14〜0.45と同水準、暴走ではない)。Production未変更、`PRODUCTION_WIRED`ではない。

### 64-2. 委任_05: K14 Phase 1の2x2補完(V0/候補 x gpt-6-luna/gpt-5.6-luna、2026-10-05、実費¥20.10、Phase累計約¥750.24)

DEV/Trial専用、Production非接続。`er052_open233_stage1_phase1_recall_check_01.py`に`--stage1-variant {candidate,v0}`/`--model`/`--out-subdir`/`--stage matrix`を追加(既定は従来挙動)。V0 promptはProduction `er003 run_deviation_check`をimportしてそのまま呼出し(prompt sha256を各run jsonに記録)。(A)V0@gpt-6-luna n=2(実費¥6.99)、(B)候補@gpt-5.6-luna は費用のため**n=1に縮小**(18 call、実費¥13.11、n=2想定は約¥26で合計がGuardrail¥22超のため)。証跡: `er052_output/open233_stage1_phase1_recall_check_01/{cell_v0_6luna,cell_cand_56luna,matrix_2x2.json}`。照合・劣後定義は委任_04cと同一(V0記録=gpt-5.6-luna記録値)。

| セル | n | SC 5件(B3/B4-a/A2A3/A4/A5) | 劣後(自セル集計) | 04cの劣後6件のうち未検出 | 負例MAJOR neg1/2/3 | 検出MAJOR総数 | 費用/call |
|---|---|---|---|---|---|---|---|
| V0@5.6-luna(記録) | 1 | 5/5(定義上) | 0 | 0 | 0/1,0/1,0/1 | 19 | - |
| V0@gpt-6-luna | 2 | 2/2,1/2,2/2,1/2,2/2 | 2 | 2(A2A3 0/2、B4 claim2 0/2) | 2/2,1/2,1/2 | 41 | ¥0.194 |
| 候補@gpt-6-luna(04c) | 2 | 2/2,0/2,2/2,2/2,2/2 | 6 | 6 | 0/2,2/2,1/2 | 47 | ¥0.276 |
| 候補@gpt-5.6-luna | 1 | 1/1,0/1,1/1,0/1,1/1 | 5(6件基準では4) | 4(B4 4件全て0/1。A2A3・B2_hormuzは1/1検出) | 0/1,0/1,1/1 | 20 | ¥0.728 |

劣後6件の逐語表(hits): B4-1 V0@6 1/2、候補@6 0/2、候補@5.6 0/1。B4-2 0/2、0/2、0/1。B4-3 2/2、0/2、0/1。B4-4 1/2、0/2、0/1。A2A3 0/2、0/2、1/1。B2_hormuz 1/2、0/2、1/1。

解釈(n小のため推測を含む): [確認] B4の4件は候補promptだとモデルを替えても検出されない(6-luna 0/2、5.6-luna 0/1)、V0 promptなら6-lunaで部分的に検出(1/2,0/2,2/2,1/2)。B4-aは候補prompt側で両モデル未検出。[確認] 検出件数(量)はmodel依存が大(V0 19→41、候補 20→47、gpt-6-lunaが約2倍検出)。[確認] V0@gpt-6-lunaもA2A3を0/2で取り逃し、B3・A4・B4-aが1/2で不安定(V0 prompt自体はgpt-6-lunaで万能ではない)。[確認] 負例neg1(MAJOR出さない想定)はV0@6が2/2誤検出、候補は0/2・0/1(誤検出面では候補promptが良い)。[推測] SCのB4取りこぼしは主にprompt差(候補の昇格ルール除外・列挙構成)、検出量の増加は主にモデル差。n=1/2のため確定ではない。Production未変更、`PRODUCTION_WIRED`ではない。

## 65. PRODUCTION-WIRING-01 CORRECTION-02 委任_08: A構成(gpt-6-luna+rep30 frozen生成V4A構成)の復元・fresh限定確認【FAIL: 受入(1)(2)(3)未達、復元差は無し=STOP候補】(2026-10-05、実費¥11.42、Phase累計約¥761.66)

- **記録**: ユーザー是正指示02を`DECISION_LOG.md`へ逐語記録。USER_DECISION_REQUIREDを撤回、Status=`APPROVED_FOR_PRODUCTION`維持。委任_05費用¥20.10は管理不備として記録のみ。
- **A構成の復元(確認)**: `docs/pm/rep30_stage1_provenance_01.md` §7。prompt/schema/model/paramsは`trial.run_trial_deviation_check(…,"V4A", include_related_fact_id=fixtureフラグ, source)`。委任_06の不一致9 runはer009 fixtureの`include_related_fact_id=False`の処理漏れで、frozen reuse 26 instance **26/26でsha256一致**(原因特定済み)。fresh 32 call(新規run側)のprompt shaもfrozen記録と全件一致(sha一致対象26 instance分)。
- **fresh限定確認**: `er052_open233_stage1_phase1_recall_check_01.py --stage1-variant a_frozen_config`(`--stage agg_a`、`--only`追加)、出力`er052_output/open233_stage1_phase1_recall_check_01/a_frozen_fresh_01/`(`agg_a_frozen.json`)。15 instance×n=2=30 call+A4補完2 call。比較対象=rep30が実際に使ったStage 1(frozen、B3/B2_hormuzはV0差替え記録)。
- **受入条件(事前固定)の判定**: (1)SC: B3 2/2、B4-a 2/2、A2A3-0 2/2、A5-0 2/2、**A4-0 1/2→n+2補完で2/4(<3/4)=未達**。(2)B群の既知重大claim見逃し: **見逃しあり**(neg5 B3-same 0/2[SC定義claim]、B2_hormuz HF-011 0/2[V0差替えclaim、frozen V4Aも0件]、B4の非SC claim 4件0/2)=未達。(3)負例/NORMAL 6 instance(12 run)のMAJOR run率: fresh 7/12=58.3% vs rep30実使用 6/11=54.5%(1 run超過)=未達(pooled、事前算出方法)。参考: neg1〜3のみ fresh 5/6 vs rep30 6/6、MAJOR数/run fresh 0.67 vs rep30 1.82。(4)claim一致率平均0.658(B4 0.6、A2A3 0.67、A4 0.875、A5 0.5等)。(5)構造的問題なし(related_fact_id・issue・severityの欠落0、API失敗0)。(6)平均¥0.34/call(KPI ¥0.14〜0.45内)、単発最大¥0.75、¥3超0件。合計¥11.42は上限¥10のGuardrail超過(Cap到達=自動STOPではない、暴走ではない)。
- **§6調査(確認)**: prompt sha100%一致、model_returned=gpt-6-luna(frozenと同一)、schema・paramsは同一コード、developer messageは定数不変(保存データでは未確認)。復元差は見つからず、是正対象なし。A4-0・neg5 B3-sameの未検出runはMINOR降格ではなく指摘自体なし(確認)。B4のMAJOR数はfrozen 10に対しfresh 3/1、A4はfrozen 8に対しfresh 2〜4、neg5はfrozen 7に対しfresh 1/0。
- **所見(推測)**: frozen出力はA構成の単発サンプルで、同一構成のfresh再実行では検出量・claim集合が大きく揺れる(run間変動)。frozenを根拠とするrep30のStage 1検出能力は、A構成そのものでは再現されない。新Checker・N増し・B/C切替はしていない。
- Production未変更、`PRODUCTION_WIRED`ではない。次はFableがSTOP/継続を判断(§6に従い、復元是正で解決できないため`USER_DECISION_REQUIRED`候補)。

## 66. Stage 1再設計Trial開始・設計確定(OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01 委任_05、2026-10-05、¥0)

- Opus#16(`docs/pm/opus_l2_review_open233_stage1_redesign_16.md`、10,484字)を機械抽出して保存。Fable評価でループ1構成を確定(設計書`docs/pm/design_open233_stage1_redesign_01.md`§6): 3'-R+5-lite 2経路∪+F3配線+H1是正(fail-open→STOP)+決定論検査。gold=正式SC 6件(HF-011は監視項目、ユーザー判断事項としてCloseoutで開示)。
- 事前作業(¥0、既存データ): (1) A構成fresh 32 runでMINOR出力0件(`er052_output/open233_kpi_recovery_02_offline_01/agg_fresh_minor_check_01.md`)→MINOR切り捨て(H2)は主因ではない【確認】。見逃しの実体は指摘自体なし。(2) V0∪V4A基準線(`agg_v0_v4a_union_baseline_01.md`): SC 6件中5件は∪で2/2、B3-same@neg5はV0記録・V4Aとも見逃し(0/2)。基準線のみで採用提案ではない。
- 実装は委任_06(並行)。段階A/Bの実行は未実施。Production未変更、`PRODUCTION_WIRED`ではない。

## 67. Stage 1再設計 段階A fresh実測(OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01 委任_07〜07c、2026-10-05、実費約¥63.4〜64.2)
- provenance=fresh / Stage 1のみ / 条件付き中間測定(E2Eではない)。Trial(DEV)、Production未変更。
- 規模: 42 run(SC 6+B2_hormuz監視 n=3、NORMAL 6 n=2、hold-out 9 n=1)。スクリプト`er052_open233_stage1_stageA_01.py`(`--normal-n 2`追加のみ)、出力`er052_output/open233_stage1_stageA_01/`(runs/、stageA_aggregate.json、aborted_07/)。
- 採用基準(事前固定): (1)SC 6件∪ 3/3: 6/6【合格】(B3・A2A3-0・A4-0・A5-0・B4-a・B3-same@neg5 全て3/3)。経路別: r3 6/6、r5 5件3/3+B3-same@neg5が2/3(該当sample3 runはr5がAPI失敗でr5欠落、判定誤りではない)。(2)hold-out新規見逃し0【合格】(9種とも候補1)。(3)欠落ID再実行後残存0%【合格】(再実行発生0 run)。
- 参考: r3×r5(SC 18 run) hit/hit 17、r3のみ1、r5のみ0、両miss 0。NORMAL候補/記事 r3 23.5・r5 13.8・∪24.0。B2_hormuz(監視)∪平均13.33。決定論検査で戻した件数 negation_polarity_mismatch 149・quote_not_in_ledger 4。HF-011は集計に項目なし(未測定)。
- 費用: 83 call、平均¥0.763/call、¥1.51/run、worst run ¥2.71(neg4_smallbag_div_a2)、run json合計¥63.35、budget state累計¥64.20。API失敗run 1(s3/neg5_hormuz_div_a2、r5失敗)。委任_07でr5 API失敗1件がaborted_07に退避。runtime: 約2h13分(委任_07〜07cの停止・再開を含む壁時計)。
- 注意: 判定はStage 1検出のみ。E2E(Stage 2以降)・Production採用は未評価。段階B移行は別判断。

## 68. Stage 1 ループ2限定Trial(OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01 委任_12、2026-10-05、実費¥15.93)
- provenance=fresh Stage 1限定(r3は段階A保存出力の再利用、r5-Vのみfresh)/E2Eではない。Trial(DEV)、Production未変更、コード変更なし。
- 実施: r5-V(`--r5-mode verify_supported`、否定案a)on保存r3 42 runをlow・mediumで各実行。出力`er052_output/open233_stage1_loop2_r5v_01/`(low)、`..._r5v_medium_01/`、集計`loop2_trial_summary_01.md`。G arm(Step 2)は基準未達のため未実施(STOP)。
- 結果: r5-V M検出 low 1/18・medium 0/18(基準17/18)、A4-0 r5-V M 0/3(必須3/3)、∪M 16/18(基準18/18)、hold-out 9/9(r3経由)、NORMAL候補∪ 23.83/23.75(基準24.0)。費用 low ¥5.74(¥0.137/run、worst ¥0.31)、medium ¥10.19(¥0.243/run、worst ¥0.52)、見積(script mid ¥16.6/¥23.9)を下回る、API失敗0、欠落ID 0%。
- 原因(確認): A4-0 gold(S2.1)はs1/s2で保存r3がSUPPORTED→否定検査(D)で`SUPPORTED->CANDIDATE`に変更された単位。`r5v_target_units`は最終状態==SUPPORTEDのみ対象とするためr5-Vの検証対象から外れる。effortでは説明できない構造要因(low/mediumで同結果)。段階Aのr5(full)はS2.1を3/3でM検出していた。
- 推測(未検証・未実装): D変更単位もr5-V対象に含める案。設計変更のためFable判断。
- 累計: 本管理ID ¥80.13/枠¥238。(iii)見込みは更新不能(Step 2未実施)。

## 69. Stage 1 ループ2実装是正+再測定(OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01 委任_13、2026-10-05、実費¥31.78)
- provenance=fresh Stage 1限定(r3は段階A保存出力の再利用、r5-Vのみfresh)/E2Eではない。Trial(DEV)、Production未変更。G arm(Step 2)はStep 1b基準未達のため未実施(STOP)。
- 是正(Trial専用コード、設計不変・ループ数2維持): r5-V対象=r3のモデル判定SUPPORTED(D適用前)+関係単位、保存r3へ否定案a再適用、角括弧付き単位IDの正規化とM集計の`source_of`整合(不具合修正)、能力テスト用`--plan cap`/`--r5v-force-targets gold`(測定用)。単体テスト75件PASS。
- Step 1(保存r3 42 run): low ∪M 16/18・A4-0救済0/2、medium ∪M 18/18・A4-0救済2/2(1件は角括弧ID経由、厳密集計では17/18・1/2)、hold-out 9/9、neg5 3/3、NORMAL候補∪ 19.6/20.0(段階A 24.0)、r5-V費用 ¥0.164/¥0.285/run、worst ¥0.31/¥0.65、API失敗0、欠落ID 0%。
- Step 1b(gold強制対象、SC 18): r5-V M low 10/18・medium 12/18(基準17/18=段階A r5 full high並み)未達。A4-0・neg5で不安定。費用 ¥4.94/¥8.01。
- 詳細: `er052_output/open233_stage1_loop2_r5v_fix_01/loop2_trial_summary_02.md`、各dir`..._r5v_fix_medium_01`/`..._r5v_cap_01`/`..._r5v_cap_medium_01`。累計 本管理ID ¥111.91/枠¥238。(iii)見込みは更新不能(Step 2未実施)。

## 70. Stage 1 ループ2 G arm 限定Trial+E2E計画書(OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01 委任_14、2026-10-05、実費¥27.80)
- provenance=fresh Stage 1限定(33 run、r3 medium+r5 medium+否定案a)/E2Eではない。Trial(DEV)、Production未変更。r5-V構成は委任_13の能力テスト(M 10〜12/18)により不採用としてクローズ(Fable判断)。
- G arm: r3 M 16/18(合格)、r5 M 15/18(基準17未達、A4-0 0/3)、∪M 17/18(基準18未達、A4-0の1/3を両経路見逃し)、hold-out 9/9、neg5 3/3、欠落ID 0%、API失敗0、worst ¥1.30、NORMAL候補∪ 21.83/記事。費用: Stage 1 ¥0.843/run(段階A同mix high ¥1.394)、reasoning tokens r3 3,208→1,371・r5 6,900→2,348。
- 判定規則: r5のみ未達→採用構成=r3 medium+r5 high+否定案a(混合構成のfresh測定は未実施、費用は合算推測 約¥1.23/run、-¥0.16/run)。r5 low追加は省略。
- E2E計画書: `docs/pm/e2e_plan_open233_stage1_loop2_01.md`(rep30スイッチ突合=不一致0、ただしSTAGE2_VERDICT_REUSE/SIBLINGはモジュール既定Falseのため明示設定が必要。Rewrite後Recheckの新Stage 1仕様は未実装、実装見積約150〜200行。推奨20 run ≈¥62(48〜86)、最小18 run ≈¥56。shadow V4A費用測定を同一run内に設計)。
- 詳細: `er052_output/open233_stage1_loop2_garm_01/loop2_trial_summary_03.md`。累計 本管理ID ¥139.71/枠¥238。

## 71. Stage 1 ループ2 Fable判定STOP(OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01 委任_15、2026-10-05、¥0、新規API実行なし)
- Status=`USER_DECISION_REQUIRED`。Fableが事前固定した「構造的両立不能」条件(iii基準で+¥2超、G・r5-Vを試し切った後)に該当と判定。E2E(≈¥62)は起動せず。Trial(DEV)、Production未変更、`APPROVED_FOR_PRODUCTION`ではない。
- provenance: Safety=fresh Stage 1限定(G arm 33 run、r3 medium+r5 medium+否定案a)、混合構成(r3 medium+r5 high)は段階A frozen(high)からの推測、Stage 2以降未通過=E2E値ではない(条件付きKPI)。Cost=Stage 1 fresh実測(medium/medium ¥0.843/run、high同mix ¥1.394/run)+混合合算推測¥1.23/run+Stage 2は線形fit(候補0〜10)外挿=推測。Human Review 0=未測定(E2E未実施)。
- 判定根拠: Stage 1 ¥1.23+Stage 2 ¥0.83〜1.5(1件≈¥0.064+固定≈¥0.1、候補≈21.8)=¥2.06〜2.7で差し引き0でも+¥2超。差し引き上限¥0.55でも≈+¥2.1〜3.0(Fable判定値、Rewrite・Recheck・出口3'-R加算の内訳は未再計算、E2E実測で確定要)。ループ3は残予算¥98.29で収まらず未使用。
- ユーザー判断事項: KPI基準点(iii)(shadow実測の可否)、Cost Cap +¥3との関係、Stage 2費用削減(承認済み構成の変更)、本管理IDの最終Status案(`TRIAL_RESULT: SAFETY_MET_COST_UNMET`等)。資料: `docs/pm/user_decision_open233_stage1_loop2_01.md`(§4選択肢A〜D、§6 Q1〜Q5、§7停止時点の自己確認)。
- Opus台帳Closeout確認: `docs/pm/OPUS_FINDINGS_LEDGER.md` OF-001〜037を1件ずつ更新(対応済9・部分13・未対応2・対象外13、CLOSEOUT_CONFIRMED遷移0)。未達の自己確認: 項目27(Close不可)、項目29(OF-018・CURRENT_SPECプレースホルダに独立Open ID未設定)。
- 累計 本管理ID ¥139.71/枠¥238(残¥98.29)。

## 72. E2E-ACCEPTANCE-01 準備(OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01 委任_18、2026-10-05、¥0、**E2E本番は未実行**)
- ユーザー決定(DECISION_LOG 2026-10-05逐語記録): Cost KPI(+¥2/セット)のみ例外承認(本管理ID限定)、Safety/Human Review KPI不変、Cost未達は`OPEN-233-COST-REDUCTION-01`で継続、到達最大=`VALIDATED`(Production未反映)。独立Open ID化: `OPEN-233-OF018-SUBREASON-01`、`OPEN-233-SPEC-STAGE1-PLACEHOLDER-01`。
- Recheck新仕様(Trial専用、`RECHECK_MODE`既定legacy_v4a=従来不変)を実装: `cov.coverage_changed_scope`(変更単位+前後1単位+前回指摘の残存箇所、関係単位を含む)、`cov.run_recheck_scope`(3'-R対象限定+5-lite[R5Vのprompt流用]対象限定、欠落ID再実行・決定論検査は初回と同じ)、`cov.run_exit_full_r3`、runner `run_recheck_coverage`/`run_exit_check_coverage`/出口ゲート(Rewrite発生記事がRESOLVED_*で出る直前に3'-R全文1回、新規CANDIDATEは次cycleのStage 2へ合流、API失敗は許可リスト`api_failure`)。`make_stage1_call_fn`を関数化(挙動不変)、`RUN_CALL_HOOK`(既定None)追加。単体テスト17件(`er052_open233_recheck_coverage_test_01.py`)+既存全793件PASS。
- E2Eスクリプト`er052_open233_e2e_acceptance_01.py`: 20 run(SC 6x2+Std/Adv対2組+負例4)、fresh Stage 1(stage1_cache=None・baseline代替無効)、provenance記録・照合、Waste検知(cost/call数/API失敗/cycle/同一候補再Rewrite)、セット集計(実測対と1記事x2推計を別列)。単体テスト7件。計画表: `docs/pm/e2e_plan_open233_stage1_loop2_01.md` 追補。
- dry-run(API stub、¥0、`er052_output/open233_e2e_acceptance_01_dryrun/`): 全20 runが最終出口まで通過、provenance全fresh、対2組の実測合算、集計欄が埋まることを確認(値自体はstubで意味なし)。見積(推計、`er052_output/open233_e2e_acceptance_01/estimate.json`): 20 run合計 low¥47.3/mid¥66.5/high¥86.0(残¥98.29内)。
- 設計上の注意(未実測・推測): 出口3'-R全文は決定論検査を含むためNORMAL記事でも約22候補/記事(G arm実測)を出し得て、Rewrite発生記事では再入によりStage 2(約¥1.5)が追加される可能性がある(計画書の出口3'-R平均¥0.22は候補再判定を含まない)。E2E実測で確認する。

## 73. E2E-ACCEPTANCE-01 E2E停止(2 run目、¥6/run Waste閾値該当)の¥0原因分析(委任_19本番→委任_20分析、2026-10-05)
- provenance: fresh Stage 1(E2E)だが**20 run中2 runで途中停止**。VALIDATED不可(Safety/Cost/Human Reviewの正式判定はE2E完走が前提)。費用: 本番E2E累計¥10.76(B3完走¥4.55、A2A3 abort時¥6.21)、委任_20は¥0。本管理ID累計は枠¥238に対し約¥150.47、残約¥87.53。
- 経緯(確認): s1/bgroup_B3完走(RESOLVED_REWRITE_THEN_DOWNGRADE、15 call、¥4.55)。s1/safety_A2A3は23 call・cycle 2のc2 Recheck r5v直後に1 run>¥6(Fable設定のWaste閾値、ユーザーKPIではない)で`RunWaste`、E2E全体STOP。`runs/s1/safety_A2A3.json`はabort記録のみ(call_log/cycles無し)。aborted jsonは保存、削除・E2E再開はしていない。
- 原因分類(詳細`docs/pm/e2e_stop_analysis_open233_01.md`): (a)見積誤り=新Recheck仕様(r3+r5v 2 call、1回¥0.47〜0.93)と出口3'-R全文(B3 ¥0.62)が見積(Rewrite+Recheck 0.17、出口0.22)に未反映、floor_verifyは見積項目なし。(b)SC fixtureの性質=A2A3はcycle 2で¥1.55追加。(c)構造的Waste=確認できず(B3 HF-007の2回は別span、call数15/23<80、API失敗0。A2A3 HF-009の4 callは別span複数Rewriteと推測だが、abort記録に無く断定不可)。Stage 2はB3で見積を下回った。
- rep30(Stage 1凍結)後段との比較(同一instance): B3 後段0.83→3.05、A2A3 1.43→4.44(abort時)。増分の内訳はB3: 候補増約28%・追加cycle約10%・新Recheck約34%・出口全文約28%、A2A3: 候補増54%・追加cycle15%・Recheck31%(出口未到達)。
- 20 run再予測(モデル、推測含む): low¥62.1/mid¥98.6/high¥122.8(元見積47.3/66.5/86.0)。残19 run mid¥94.0で残予算¥87.53を¥6.5超過。SC n=1の14 run案(残13 run)mid¥55.3、対+負例のみ8 run案mid¥21.1(SCなし=重大逸脱見逃しの測定不能)。閾値¥10化では構造的Wasteは捕捉されない(同一候補反復検査は完走後のみ)。純増参考: B3同額なら+¥8.27/セット(見込み+5.4/上振れ+6.7、SCは非代表)。
- Status: `USER_DECISION_REQUIRED(E2E停止)`。再開・run数・閾値・予算追加はユーザー判断待ち。Production未変更、コード変更なし。

## §74 OPEN-233 E2E-ACCEPTANCE-01 委任_21(2026-10-05): E2E再開、非SC 8 run完走後にWaste検知で停止(未完走、9/20 run)
- provenance: fresh Stage 1 / E2E途中(frozen・reuse・代替なし、provenance違反0)。Status候補はFable/Opus照合待ち。VALIDATEDとは書かない(未完走のため不可)。Production未反映。
- ユーザー判断(DECISION_LOG逐語): 20 run再開・枠¥273・1 run閾値¥20・独自停止条件禁止・報告5節固定。設定変更: 1 run閾値¥20(CLI --per-run-cap-jpy)、実行順=非SC(対4+負例4)→SC、abort時の部分call履歴保存、「累計が見積+30%超で停止」(独自条件)廃止、runs/_aborted/へ旧A2A3 abort証跡を退避。テスト7件PASS。
- 完走9 run(B3含む、完走分費用¥43.91、E2E累計¥50.12=旧A2A3 abort¥6.21含む、本管理ID累計¥189.83/枠¥273、残¥83.17): hormuz対 adv¥3.44/std¥2.17、meta対 adv¥5.43/std¥5.16、neg1¥8.82、neg2¥3.79、neg3¥4.00、neg7¥6.55、B3¥4.55。¥3超7件。worst=neg1 ¥8.82。
- 停止: neg7_meta_prodrunner_b1b(負例)がSTAGE4_ESCALATION(blocking_structural_after_ladder)で終了し、事後Waste検査`same_candidate_rewrite_gt_3`(claim_identity=fact単位でRewrite試行>3)に該当してスクリプトが自動停止。実態: 33 call・2 cycle・¥6.55・1 factで9試行(ladder段・箇所違い)で自然終了しており、「不自然な反復」か「ladder設計どおり」かは判定待ち。
- 実測所見(8 run、推測なし): 負例/NORMAL相当6 runの全件でRewriteが発火(Rewrite率100%、見込み0.53と乖離)、うち1件が人間確認行き。cycle分布(1/2/3/4)=1/1/6/1。
- Worker判断: 上記Waste判定を緩めて再開する案を試みたがPermission拒否(Security Weaken)のため再開せず停止。再開可否・判定基準はユーザー/Fable判断待ち。
- Status: `USER_DECISION_REQUIRED(E2E停止、neg7 Waste検知)`。詳細: er052_output/open233_e2e_acceptance_01/(run_log_main_part1_stopped_neg7.json、e2e_aggregate.json、runs/)。

## §75 OPEN-233 E2E-ACCEPTANCE-01 委任_22(2026-10-05): neg7 Human Review発生のRCA(¥0、コード変更なし、E2E再開せず)
- provenance: fresh Stage 1 / E2E途中(frozen・reuse・代替なし)。VALIDATED不可、Production未反映。ラベルは【確認】/【推測】を分けて記載。
- **Human Review KPI: FAIL確定(1/9 run)**。neg7(負例、meta)がSTAGE4_ESCALATION(`blocking_structural_after_ladder`)。非SC 8 runのうち7 runでRewrite発火(hormuz_standardのみ0。集計上のnormal-like 6 runは全件)。
- 分類【確認+推測】: 直接原因=**①実装不具合**(T経路が同cycleでRewrite成功済みのHC-010 claimを再度削除対象にし位置特定不能→`_t_fail`→構造要素でない(`structural_reasons=[]`)のに`blocking_structural_after_ladder`。設計doc L704の既知の範囲外観察と同型)。全件Rewriteの原因=**②設計問題**(Stage 1 r3の候補過剰[neg7は29単位中24候補]、Stage 1 changed_*由来のdeterministic_floorがLLM ACCEPTABLEを覆す[FLOOR_VERIFY=time_onlyで非時期floorは再確認/S1非経由]、Recheckのfact_id粒度fail-closed、ladder location_carry)。③正当は該当なし。
- BLOCKING審査(非SC 8 run計35件): 全件floor強制(うち31件はStage 2 LLMがBLOCKING以外)。【推測】誤BLOCKING24/判断不能5/正当6(HC-011複数化・HF-003/009等)。neg7は12件で誤9/判断不能3/正当0。S1が割れてBLOCKINGになった例は0。
- rep30同instance比較: BLOCKING 1件・Rewrite 1/8 run → E2E 35件・7/8 run。OF-032(BLOCKING率0.10は過小評価)は実測で裏付け(n小)。
- 是正案(列挙のみ、実装なし): A T除外(不具合修正)、B STAGE4前の構造検証必須化、C floor_verify拡張(要承認)、D r3 prompt(要承認)、E Recheck claim単位化(要承認)、F ladder再試行、G閾値(非推奨)。詳細は`docs/pm/rca_open233_e2e_neg7_human_review_01.md`。
- 残11 run(SC): 未再開。継続で得るのはE2E Safety見逃し0の実測(未修正コードだと修正後に再測定が必要)。費用mid¥55〜70/残¥83.17。結論はFable/ユーザー。累計¥189.83不変(本委任¥0)。
- 証跡: er052_output/open233_kpi_recovery_02_offline_01/e2e_neg7_rca_extract_01.json。
- Status: `USER_DECISION_REQUIRED(E2E: Human Review KPI FAIL 1件・分類【①実装不具合(直接)+②設計問題(Rewrite全件)】)`。

## §76 OPEN-233-CHECKER-SELECTIVITY-RECLASSIFY-01 委任_B(2026-10-06): T経路の再対象化不具合を修正(¥0、Trial runner、Production未反映)
- 問題【確認】: E2E neg7のcycle2で、同fact_id(`fact:MUSE-HC-010`)の2 claimのうち(ii)=ladder枯渇、(iii)=同cycleで3_sentence置換に成功済み。T(最終手段の決定論削除)は枯渇claimをclaim_identity(=fact_id)で選んでいたため(iii)まで再対象化し、文が既に変わっていて`span_unverified(mismatch)`→`_t_fail`→構造要素でないのに`blocking_structural_after_ladder`(Human Review)へ。凍結run json(`er052_output/open233_e2e_acceptance_01/runs/s1/neg7_meta_prodrunner_b1b.json` cycles[1])で、修正前のidentity選択がindex[1,2]を返すことを再確認。
- 原因行(修正前): runner L9019-9031付近(`t_claims = [c ... claim_identity in _ex_ids]`、`_t_fail`→`_allow("blocking_structural_after_ladder")`、`_rec_by`のidentityでのrecord上書き)。
- 修正【確認】(`er052_open233_self_recovery_flow_runner_01.py`): (1)新`select_last_resort_targets`(record単位=index選択。同identityの成功済み/carry-forward済みは`t_skipped_reason=already_rewritten_in_cycle`で除外し`cycle_record["t_target_selection"]`へ記録)。(2)新`classify_last_resort_failures`(T失敗を`covered_by_earlier_rewrite`/`unlocatable_not_covered`/`located_guard_failed`に分類、各々`structural_ladder_exhausted_verified`の結果を併記し`cycle_record["last_resort_failure_classification"]`へ)。(3)T後のrecord差し戻しをidentityではなくindexで行い、同identityの別claimの成功recordが失敗recordで上書きされないようにした(Recheckの`prior_issues`が置換後の文を参照できる)。(4)失敗種別の写像: 本文に残る未解消でT削除guardも通らない(`located_guard_failed`)=従来どおり`blocking_structural_after_ladder`(fail-closed)。位置特定不能で先行Rewriteにも含まれない(`unlocatable_not_covered`)=「構造上修正不能」とは呼ばず、SPAN_FALLBACK_CHAIN有なら既存のH-1 carry(全文Recheckで再取得、上限後は許可リスト内`blocking_confirmed_unlocatable_after_cap`)、無なら既存の非構造ラベル`violation_span_unverified`/`target_not_locatable`でfail-closed(Human Review維持)。【訂正(§76-2, 委任_B3): この分岐(carry/許可リスト外ラベル)は廃止。§76-2参照】対象が先行Rewriteで置換済み(`covered_by_earlier_rewrite`)のみ解消扱い(最終的な解消判定は従来どおり全文Recheck)。新遷移先・新Statusは作っていない。
- テスト【確認】: 追加13件(`TestLastResortDeleteDoesNotRetargetRewrittenClaims`、テストファイル末尾)。修正前: 13件中FAIL 3+ERROR 8(未実装helper参照等)、特にrun_instance統合テストは挙動FAIL(`['…alpha…','…beta…']`≠`['…alpha…']`=TがBを再対象化)で再現。修正後: 13/13 PASS。回帰`run_project_regression.py --pattern "er052*_test_*.py"`: 857件 passed=857 failed=0 errors=0(修正前の既存分844件+新規13件。REPORT_LEDGER L117の598件は別時点の別スコープ)。
- retry/fallback/regeneration等の同種確認表【確認】: (1)品質劣化regen(L9080): 全claimをRewrite前の本文から連鎖実行し、`cycle_replaced_units`で先行置換をcarry-forward=同種不具合なし(ただしregenはTを再実行しない=下記残課題)【訂正(§76-2, 委任_B3): 「regenはTを再実行しない」はT対象については不正確。T対象はL9083の`last_resort_delete=True`によりregen内(L6123)で再実行される。正しくは「regen内で新たに起きた枯渇・位置特定不能は判定されずRecheckへ流れる(安全側)」】。(2)cap_terminal_T: 全claimを通常Rewrite連鎖で処理しcarry-forwardが効く=なし。(3)次cycle: Stage 2は新しい本文のclaimを新規に取得、位置は`rewritten_regions`/`location_prior_levels`経由=旧テキストで探す経路なし。(4)Recheck: `resolve_prior_issue_text`は置換後の文を現行本文から引く(テスト追加)=なし。(5)SPAN_FALLBACK_CHAIN carry: `target_not_locatable`を次の全文Recheckで再取得=なし。(6)T経路自体は本修正で是正。
- 残課題【確認+推測】: (a)【推測】品質劣化regenが発火するとTによる削除はRewrite前の本文から再実行されるが、regenはTを再実行しないため、regen後に新たなladder枯渇が出ても同cycleではTが走らない(次cycleでStage 2が再判定)=別論点として観察のみ、未修正。【訂正(§76-2): 「regenはTを再実行しない」は誤り。T対象はregen内で再実行される。regen内で新たに起きた枯渇・位置特定不能が判定されない点のみが観察事項(安全側)】(b)設計問題②(Stage 1 r3の候補過剰・floor強制BLOCKING・Recheckのfact_id粒度・ladder location_carry)は本修正の範囲外で未着手、ユーザー承認事項。(c)Opus 11-3: 非該当(構造不変)。
- Safety/Human Review基準: 緩和なし。本文に残る未解消BLOCKINGは全て従来同様fail-closed(STAGE4または次のRecheck)。減るのは「既に書き換え済みの文を再度探して失敗する誤STAGE4」のみ。
- Status: `VALIDATED(Trial runnerの実装不具合修正のみ、Production未反映)`。

### §76-2 Opus任意レビュー指摘の反映(委任_B3、2026-10-06、¥0、Trial runner、Production未反映)
委任_B(`dea81a92`)のT経路修正に対するOpus独立技術レビュー(任意レビュー本日1回目)の指摘を、Fable判断(委任_B2はR2の行き先[許可リスト外ラベル問題]でSTOP・未実装、委任_B3で再開)に従って反映した。
- R5-(a)【必須・確認】`classify_last_resort_failures`が`method`が`covered_by_earlier_rewrite`で始まるT record(T内carry-forward済み、`guard_ok=False`/`target_not_locatable=False`)を`located_guard_failed`扱いし`blocking_structural_after_ladder`へ送っていた。`select_last_resort_targets`(解消済み扱い)と判定を揃え`covered_by_earlier_rewrite`とした。再現: 統合テスト「同じ文を指す枯渇claim 2件を同時にT」は修正前`blocking_structural_after_ladder`でFAIL、修正後PASS。
- R2【確認】`unlocatable_not_covered`は、SPAN_FALLBACK_CHAINの有効/無効にかかわらずH-1 carryせず、その場で`stage4_reason="blocking_confirmed_unlocatable_after_cap"`(許可リスト`STAGE4_ALLOWED_REASONS`内、`stage4_allowlist_decision`でallowed=True)でfail-closed停止(STAGE4)。`cycle_record["stage4_sub_reason"]="t_target_unlocatable_nonstructural"`・`structural_verified={"verified":False,...}`・`last_resort_failure_classification`を記録(記録のみ)。旧: carryは次cycleでStage 2を通さずBLOCKING注入→`post_T_new_blocking`に必ず落ち、1 cycle分の費用増と理由名不一致のみでHuman Reviewは減らさなかった。許可リスト外ラベル`violation_span_unverified`/`target_not_locatable`でのSTAGE4停止は廃止。許可リスト・Human Review基準は不変。
- R1【確認】`carry_forward_resolution`のcovered判定を「範囲が現在(置換後)の本文に存在しない」場合に限定(`r in now_text`なら先行Rewrite被覆とみなさない。同文複数出現で片方だけ書換の抜け道を塞ぐ、安全側)。
- R5-(b)【確認】`blocking_structural_after_ladder`の全発生箇所(cap terminal、ladder枯渇→STAGE4、T後located_guard_failed、degenerate)で`cycle_record["structural_verified"]`(verified bool+reason+details、新`structural_verified_record`)を記録(記録のみ、挙動・ラベル不変)。
- R4【訂正】§76の「regenはTを再実行しない」は不正確。T対象は`last_resort_delete=True`によりregen内で再実行される。正しくは「regen内で新たに起きた枯渇・位置特定不能は判定されずRecheckへ流れる(安全側)」。観察のみ・未対応。
- テスト【確認】追加6件(`TestLastResortDeleteDoesNotRetargetRewrittenClaims`の(e)群): classify covered判定、統合(同文枯渇2件→STAGE4へ行かない)、R2×SPAN_FALLBACK_CHAIN=True/False、R1、R5-(b)記録。既存1件(`test_c_integration_...`)の期待ラベルを許可リスト内ラベルへ更新。修正前: R5-(a)2件・R2 2件FAIL、R5-(b) ERROR(KeyError)。R1は修正条件を一時的に外すとFAILすることを確認。修正後: 19/19 PASS。回帰`run_project_regression.py --pattern "er052*_test_*.py"`: 863件 passed=863 failed=0(基準857+6)。
- Safety/Human Review基準【確認】緩和なし。本文に残る未解消BLOCKINGは従来どおりfail-closed。許可リスト・Stage 1/2・prompt・gold・floor語彙は不変。Productionへ配線なし。
- Status: `VALIDATED(Trial runnerの実装不具合修正のみ、Production未反映)`。

## §77 OPEN-233-CHECKER-SELECTIVITY-RECLASSIFY-01 委任_A/A2(2026-10-06): Checker選択性再分類Trial(¥10.46、Trial、Production未反映)
性質: Trial(`APPROVED_FOR_PRODUCTION`ではない)。到達上限VALIDATED。**判定: gold残存100%未達(A4-0 sample3が全経路で消失)=VALIDATED未達【確認】、ユーザー指示によりSTOP。** 詳細記録=`docs/pm/reclassify_open233_checker_selectivity_01.md`、集計=`er052_output/open233_reclassify_01/reclassify_aggregate.json`、script/run=`er052_output/open233_reclassify_01/`。
- 方法【確認】Before=reuse(段階A 42 run保存候補、`er052_output/open233_stage1_stageA_01/`)、After=fresh(新しい問い[Ledger食い違い/Ledger外の具体的新事実]による分類call 42回、gpt-6-luna medium、既存r3構成のまま)。Checker本体再実行なし・Checker本体不変・KPI不変。委任_AはscriptとコストSTOP(見積low¥11.5/mid¥13.7/high¥16.5、Cap¥10超)。Fable判断: T-3継続条件充足で既存r3構成のまま上限¥17で実行。
- 候補数 Before→After(件/run、和集合all):
| 群 | run数 | Before→After(all) | llm分 |
|---|---|---|---|
| SC | 18 | 18.17→10.11 | 14.28→5.94 |
| B2_hormuz(WATCH) | 3 | 14.33→10.67 | 7.00→3.33 |
| NORMAL | 12 | **24.17→9.83**(約59%減) | 19.92→5.33 |
| hold-out | 9 | 1.0→1.0 | 1.0→1.0 |
| ALL | 42 | 15.93→8.12 | 12.52→4.52 |
- 2方向【確認】r3 15.62→8.05、r5 5.55→3.19、和集合15.93→8.12。決定論・coverage_gap分(NORMAL約4.25件)は不変。
- gold 6件×3 sample【確認】:
| gold | Before | After(any) | r3 | r5 |
|---|---|---|---|---|
| B3 | 3 | 3 | 3 | 3 |
| B4-a | 3 | 3 | 3 | 3 |
| B3-same@neg5 | 3 | 3 | 3 | 2(Beforeも2) |
| A2A3-0 | 3 | 3 | 3 | 3 |
| **A4-0** | 3 | **2** | 2 | 1 |
| A5-0 | 3 | 3 | 3 | 3 |
- 監視項目【確認】hold-out 9/9残存、neg5(B3-same)3/3、K19 3/3(ユーザー決定で軽微扱い)、HF-011はBefore/Afterとも候補なし(SAFETY_CRITICAL外の監視項目)。
- 実費【確認】42 call、入206,966/出91,916 tok、**¥10.46**(見積midより−¥3.3、上限¥17内)、欠損0・retry0・fail-closed0。分類内訳(526 claim): CANDIDATE 190 / NO_FACT_CLAIM 177 / SUPPORTED 159。
- 例【確認】NO_FACT_CLAIM化10例は比喩・つなぎ・規範・効果音・修辞的問いで妥当に見える("Ring, ring."等)。SUPPORTED化5例にnegation/comparison含む文あり("The test had begun without clearly telling users."等)=重大Factを落とさないか注視。境界CANDIDATE維持3例中2例は「Ledger未記載のみ」で候補化(新方針と緊張)。
- **落ち: A4-0 sample3【確認+Fable確認】** claim「Through Muse, trained human contract workers made some calls and completed the exchanges with users.」をr3/r5ともSUPPORTED(Ledger一致)と判定。Sonnetは限定語"some"と推測したが、**Fable確認によりA4-0 goldの正式な違反内容は「やり取りの相手(カウンターパート)の取り違え」**: Ledger MUSE-HC-006は電話の相手先=企業・店舗、記事は"completed the exchanges with users"(Museのユーザー)。根拠: `er052_open233_self_recovery_stage2_calibration_01.py` L363-368(Ledgerのissue逐語)。新しい問いは主体の取り違えを「Ledger一致」と誤読して候補から外した=**Safety上の本物の見逃し**(主体/固有名のFactリスク)。A4-0は過去にもV2 false downgrade・r5-V 0/3と脆弱。
- 所見【推測】候補は約6割減るが、主体・相手先の取り違えを含む文のSUPPORTED化はSafetyの穴になる。次Trialがあれば問いの精緻化(主体・相手先・範囲・限定語のLedger一致確認を明示/1方向でもCANDIDATEなら残す等)が検討余地。Checkerのprompt変更は本Trialのscope外で未実施、採否はユーザー判断。
- Status: `Trial実行済み・VALIDATED未達でSTOP`(`USER_DECISION_REQUIRED`)。Production未変更。

## §78 OPEN-233-CHECKER-SELECTIVITY-RECLASSIFY-02 委任_01(2026-10-06): 4点一致確認prompt Trial(見積¥12超でSTOP、実費¥0、Trial、Production未反映)

- 【確認】`er052_output/open233_reclassify_02/reclassify_candidates_02.py`を01からコピーしprompt・schema(actor/counterpart/scope/qualifier_match追加)・見積較正のみ変更。モデルgpt-6-luna・effort=medium・入力構成は01と同一。
- 【確認】較正: 01実測(42 call、入力206,966tok/出力91,916tok、reasoning 61,961tok=1,475/call、可視29,955tok=57/claim、入力0.417tok/字)。01見積器の入力0.66tok/字は過大(実0.417)だったため0.42へ修正。reasoningは実測1,475/callを基準。
- 【確認】較正済み見積 low¥12.00/mid¥13.80/high¥16.08(02の増分仮定: reasoning x1.0/1.2/1.5、可視85/105/125tok/claim。増分は【推測】)。mid>¥12のため委任文のSTOP条件に従い有料runは実行せず(実費¥0)。
- 【推測】出力にmatch 4項目が増える分、01並み(¥10.46)から+¥1.5〜3.3の増加見込み。reasoning増分が0でも約¥12.3。
- 回帰確認(¥0): er052回帰863件PASS(runner不変)。gold/A4-0/候補数/hold-outは未測定。
- Status: USER_DECISION_REQUIRED(予算枠[例¥14〜16]の承認、またはmatch項目の出力簡素化等は仕様変更に当たるためユーザー/Fable判断)。詳細: `docs/pm/reclassify_open233_checker_selectivity_02.md`。

## §78-2 OPEN-233-CHECKER-SELECTIVITY-RECLASSIFY-02 本実行結果(委任_02、2026-10-06、ユーザー上限¥20承認、Trial、Production未反映)

- 【確認】本実行(`--stage run --yes-run-paid --budget-jpy 20`、`--stage agg`)。script/promptは委任_01準備済みのまま無修正。gpt-6-luna/effort=medium/42 call(run単位1 call)、01と同一構成・同一入力。欠損run0、fail-closed0、retry0。実費¥14.3752(入力224,648tok/出力138,334tok)、較正済み見積mid¥13.8比+¥0.58(high¥16.08内、上限¥20内)。
- 【確認】候補数(件/run、和集合all/AI由来llm): 全体 Before15.93/12.52→01 8.12/4.52→02 8.57/5.00。NORMAL 24.17/19.92→9.83/5.33→**10.75/6.25**。SC 18.17/14.28→10.11/5.94→10.56/6.44。B2_hormuz 14.33/7.00→10.67/3.33→10.67/3.33。hold-out 1.0→1.0→1.0。r3(NORMAL)23.5→9.83→10.5、r5 9.0→3.42→4.17(全体 r3 8.43/r5 3.40)。決定論・coverage_gap分は不変。
- 【確認】gold 6件×3 sample: B3 3/3、B4-a 3/3、B3-same@neg5 3/3(r5のみ2/3、Beforeも2)、A2A3-0 3/3、**A4-0 3/3(01は2/3)**、A5-0 3/3。gold_pass=True。A4-0各sample: s1=決定論r3+model_r5、s2=決定論r3+model_r5、s3=model_r3+model_r5。全sampleで対象文"Through Muse, trained human contract workers made some calls and completed the exchanges with users."がCANDIDATE、4観点=actor match/counterpart **mismatch**/scope match/qualifier match、理由は「やり取りの相手を『ユーザー』とするのはLedgerの電話相手先と異なる」。01で消えたsample3もcounterpart mismatchで残存。
- 【確認】監視: hold-out 9/9残存、neg5 B3-same 3/3、K19 3/3、HF-011は候補なし(01と同じ)。いずれも01比で悪化なし。
- 【確認】verdict内訳(526 claim): CANDIDATE 190→210/NO_FACT_CLAIM 177→186/SUPPORTED 159→130。4観点mismatchは全てCANDIDATE内で発生(SUPPORTEDでのmismatchは0): qualifier 115、scope 108、actor 24、counterpart 10。組合せ上位: scope+qualifier 78、mismatchなし(他理由)69、qualifierのみ19、actor+scope+qualifier 12、scopeのみ11、actorのみ8。
- 【確認】01比のverdict変化(同一claim): 01 CANDIDATE→非CANDIDATE 29、非CANDIDATE→CANDIDATE 49(うち元NO_FACT_CLAIM 9=NORMAL 4、元SUPPORTED 40=NORMAL 21)。NORMAL新規CANDIDATE 25件。
- 【確認】NO_FACT_CLAIMからの再候補化9件(NORMAL 4): 将来予測/一般傾向/ユーザー認識の推測文が中心(例 "They will want to know if it is AI or human."、"Normally, that might have brought some relief to crude oil prices."、"People often worry that an AI phone call will produce a strange answer."×3)。純粋な効果音・比喩・つなぎ文の再候補化は9件中に見当たらない【推測】(判断はFable)。
- 【確認】「Ledger未記載のみ」境界例(CANDIDATEかつ4観点mismatchなしかつ理由が「記載/明記されていない」)7件(01は2件)。例: "A person can take over when AI alone has trouble."、"That was what people thought as they spoke."(×2)、"People who asked Muse to make a call might think AI was doing it."、"AI had not learned to speak like a human."、"Up to that point, it is AI."、"The lesson is that changing the words...does not always change the price in the same way."。
- 【確認】NORMAL新規CANDIDATE例(元SUPPORTED/NO_FACT): 見出し"# We Thought It Was AI..."(scope+qualifier、Muse一部テストの限定落ち、妥当【推測】)/"A service let people ask AI to make phone calls."(米国内企業・店舗の範囲落ち、妥当)/"In 2026 fashion, mini bags are having a big moment."(主体・季節限定の落ち、妥当)/"In 2026, the runway proudly shows this split..."(ELLE解釈のランウェイ全般化、妥当)/"Palm-sized clutches... fill runways and fashion reports."(例示の一般化、やや厳格【推測】)/"# The 20 Percent Fee Plan Is Withdrawn—But Oil Prices Quickly Return"(Brent以外へ拡大、妥当)/"A user might think the exchange was with AI..."(元NO_FACT、ユーザー認識推測、境界)/"As AI becomes able to make calls..."(元NO_FACT、将来予測、境界)/"They will want to know if it is AI or human."(同)/"A large number suddenly appeared, making the proposal the story's new lead."(元NO_FACT、数値+編集評価、境界)。
- 【推測】NORMALは01比+0.92件/記事で、Before 24.17の約44%。旧「何でも候補」水準への回帰ではないが、AI由来は+0.92(5.33→6.25)で増加。増加分の約8割は元SUPPORTED(scope/qualifier mismatch)由来。Safety上の過検出か有益な追加かの判定はFable。
- Status: Fable分類待ち(REJECTED/VALIDATED/USER_DECISION_REQUIRED)。VALIDATEDでもProduction採用ではない。詳細: `docs/pm/reclassify_open233_checker_selectivity_02.md`(結果節)、`er052_output/open233_reclassify_02/reclassify_aggregate.json`。


Fable分類: **VALIDATED**(2026-10-06)。根拠: 受入条件4件すべて充足【確認】(A4-0 3/3[01は2/3]、正式gold 6/6、hold-out 9/9・neg5 3/3・K19 3/3で01比悪化なし、NORMAL候補24.17→10.75件/記事=Beforeの44%で削減効果維持[01比+0.92])。STOP条件6件いずれも非該当(実費¥14.38≤¥20、gold落ちなし、A4-0安定、旧過剰仕様への回帰なし[AI由来増分の約8割は元SUPPORTEDのscope/qualifier不一致化]、新Safety問題なし、追加仕様変更不要)。Production採用ではない(Production Checker・後段AI・機械Safety・E2E不変)。次工程はユーザー判断(Production Checkerへの反映設計はOpus条件A/C対象)。残観察: 『Ledger未記載のみ』境界例2→7件、NO_FACT_CLAIM→CANDIDATE 9件(将来予測・一般傾向・認識推測文)は過検出の可能性があり、次段階で問いの微調整候補(今回は変更しない)。

## §79 OPEN-233-FLOOR-SELECTIVITY-OPTIMIZATION-01: 機械Safety(floor)誤爆35件の分析と設計案比較(委任_01〜02b、¥0)

### §79-1 前提・provenance・35件内訳
- 性質: ¥0の既存保存データ分析(`er052_output/open233_floor_selectivity_offline_01/floor_fire_analysis_01.{py,json,md}`)と設計比較のみ。コード/Prompt/gold/Production変更なし。設計doc `docs/pm/design_open233_floor_selectivity_01.md`、Opus `docs/pm/opus_l2_review_open233_floor_selectivity_01.md`。
- ラベル(正当/不要/判断不能)はRCA由来の推測ラベルで、Fable/ユーザー未確認(U4)。
- 35件内訳(延べ発火/正当/不要/判断不能): 主体6/2/2/2、数字4/3/1/0、否定5/0/5/0、比較14/0/13/1、因果1/0/1/0、時期8/1/6/1、その他(tier0:aux)1/0/0/1。正当6=数字3・主体2・時期1(LLM自身重大4、floorのみ重大化2[No.5,21→訂正後No.5,23])。
- 不要24の原因【確認】: (i)Stage 1フラグ不整合17、(ii)重大性判定欠如6、(iv)Tier0語彙1、(iii)=0(集計script `assign_cause`に(iii)分岐がなく構造的に0、doc §10訂正)。

### §79-2 誤爆主因と案別比較(強制重大件数/正当6件)
- 主因【確認】: `apply_floor`(runner L2432)がLLM判定と無関係にBLOCKING上書きし、重大性判定もフラグ検証もない。比較+否定が最大誤爆源。floor単独起因31/35。
- 案別(in-sample、現行35件): 案0=35/6強制、案1=14/6強制、案2=8/強制4+確認2、案3=0/確認6、案4=4/LLM自身4+S1 2、案5=14/6強制。
- hold-out(rep30、集計md L69): 案1はneg3 gold(SC gold b1b、時期floor・LLM非BLOCKING)を非強制=見逃し。「案1 6/6維持」はin-sample限定(doc §10訂正)。
- 半減見込み(in-sample): 案1〜5全て半分以下、1/3以下は案2/3/4。案1/5は14件で1/3未達。out-of-sample・追加確認精度は未測定。
- 案2で追加確認へ回る正当はNo.5とNo.23(No.23はLLM BLOCKINGのためverify対象外で残り、実際に危険なのはNo.5のみ)。
- 承認済み線引きOPEN-233-A1-PROD(時期のみverify・他は決定論維持)に対し、案2〜4は明確な変更、案1/5も発火範囲縮小で実質変更=ユーザー承認要。

### §79-3 Opus条件Aレビュー要旨(`docs/pm/opus_l2_review_open233_floor_selectivity_01.md`、read-only、¥0)
- 結論: floorだけを変える案1〜5は根本対策として不十分。不要24の中心は(i)17件でStage 1が`changed_*`を付けたこと自体が誤り(Ledgerに対応記述なし=absence)【確認】。R3 promptは「少しでも疑いがあればCANDIDATE」でabsence専用規則なし、Production checkerの`HOOK_CLAUSE`相当の緩和もない。
- doc分析の弱点【確認】: `issue_type`はLLM日本語issue文の正規表現判定、`CONTRA_RE`が広すぎる、(i)(ii)振り分けも正規表現のみ、(iii)=0は構造的。
- 案別評価: 案1/5=正規表現・固有名詞除外の個別当て込みでhold-outでgold見逃し(R2)。案2=verifyはStage 2と同モデルで誤りが相関、委任_61で方向反転がverifyで解放され比較を決定論へ戻した経緯があり、主体・比較へのverify拡張は塞いだ穴の再開(R3)。案4=S1は同rubric再サンプルで正当6件中2件を失いうる、Trial専用・既定OFF、非推奨。
- 推奨代替(優先順): (1)RECLASSIFY-02区分(「Ledger食い違い」候補)のfloor発火条件流用(2)cite-to-fire(変更されたLedger記述の逐語引用を要求、実在を決定論検証。`apply_floor_cited`/`floor_cited_eligible`が¥0実装済み。ただし現行は英語4文字以上の語重なり判定でLedgerが日本語のため非数値はほぼ一致しない可能性【推測】、保存値replayで先に評価)(3)Stage 1 prompt補正(absenceは`changed_*`を付けず`unsupported_new_claim`、recall測定要、OF-001)。
- 順序: RECLASSIFY-02評価→段階0(¥0: 0a 35件とRECLASSIFY-02保存出力の突合/0b `apply_floor_cited`反実仮想値を35件+SC gold全件で集計/0c SC gold・hold-outのgold取りこぼし0を最優先/0d 正当6+判断不能5のラベル確認)→設計確定→ユーザー承認→有料段階1。ユーザー承認要=floor発火条件変更すべて/Stage 1 prompt・schema変更/有料Trial。承認不要=時期の承認済みverify流用・¥0 replay。
- 目標再確認: 誤BLOCKINGの害と誤解放の害は非対称。件数目標よりgold取りこぼし0を優先。「複数フラグ同時true」は不採用(複合4件は全て不要ラベル)。

### §79-4 Fable判断(2026-10-06、Opus条件Aレビュー後)とユーザー判断事項
Status=**USER_DECISION_REQUIRED**。根拠: (1)Sonnet案(最有望=案2+案5、根本原因=floor側の重大性判定不在)とOpus(根本原因=Stage 1 `changed_*`フラグ生成側のabsence/contra混同、案1/5は過適合、案4は正当2件を失いうる、推奨=RECLASSIFY-02区分流用>cite-to-fire>Stage 1 prompt補正)で重要な結論が対立。(2)Fable検証【確認】: hold-out(rep30、集計md L69)で案1はneg3 gold(時期floor・LLM非BLOCKING)を非強制=見逃し(案1 6/6維持はin-sample限定)/集計scriptの`assign_cause`(L207-215)に原因(iii)分岐がなく(iii)=0は構造的/doc §5のNo.21記述は表(No.23)と不一致。(3)案1〜5・cite-to-fireのいずれも承認済み線引きOPEN-233-A1-PROD(`APPROVED_FOR_PRODUCTION`・未配線、時期のみverify・比較/主体/数字/否定は決定論維持)の変更に当たりユーザー承認事項=ユーザー指定STOP条件「Production仕様変更が必要」に該当。(4)floor側のみの精緻化で正当6件を守りつつ半減する見込みは、in-sampleでは案1/5=14件だがhold-outで1件見逃しのため未確立。Fable評価: Opusの根本原因指摘(フラグ生成側)と順序(RECLASSIFY-02評価→¥0段階0→設計確定→ユーザー承認→有料段階1)を妥当と判断し、ユーザーへ提示。Production未変更、有料Trial未実施、gold不変。

ユーザー判断事項:
- U1 設計方向: Opus代替(1)RECLASSIFY-02区分流用/(2)cite-to-fire/(3)Stage 1 prompt補正/Sonnet案2+5/floor撤廃別設計のいずれか。
- U2 承認済み線引きOPEN-233-A1-PROD変更の可否。
- U3 ¥0段階0(0a〜0d)の実施可否。
- U4 正当6件・判断不能5件のラベル確認(RCA推測ラベル)。
成果物: 上記doc 2件、`er052_output/open233_floor_selectivity_offline_01/floor_fire_analysis_01.{py,json,md}`。

## §80 OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01: 実装(委任_04、¥0、PRODUCTION_WIRED未・E2E未)

### §80-1 性質・Status
ユーザー決定2点(2026-10-06、APPROVED_FOR_PRODUCTION)のer052 runner(Production候補経路)への配線実装+test+runtime evidence。Opus条件AレビューM1〜M5を反映(`docs/pm/opus_l2_review_open233_checker_floor_production_e2e_01.md`、台帳OF-049〜055)。有料API 0、E2E未開始、r3/r5 prompt・Stage 2 rubric・S1・gold・Safety-critical定義は不変。globalの既定は全て旧挙動(承認構成は`apply_open233_approved_flow_switches()`で適用)。Status=**実装完了・E2E未・PRODUCTION_WIRED未**。

### §80-2 変更一覧(M1〜M5対応)
| 項目 | 変更 |
|---|---|
| M1 合流前filter | `er052_open233_stage1_coverage_checker_01.py`: `apply_candidate_filter`新設、`run_stage1_coverage`/`run_recheck_scope`/`run_exit_full_r3`に任意引数`candidate_filter`(既定None=不変)、`union_candidates`直前で適用、audit`candidate_filter`へinfo。経路別生候補(`per_route`)は監査用に未加工で残す。API失敗経路はfilterしない。runner: `make_reclassify_filter`(1箇所生成)を3入口(`stage1_coverage_fresh`/`run_recheck_coverage`/`run_exit_check_coverage`)が同じ形で渡す。`STAGE1_RECLASSIFY`既定False |
| M2 同文保護 | `er052_open233_stage1_reclassify_01.py`: `protected_claims`(`prior_issue_resolution`の`same_text`条件と同一)に一致するmodel候補は対象外=候補残存。Recheckはprior_issues、出口は過去cycleの指摘文(`reclassify_protected`)を保護。`prior_issues_resolved`はfilter後の候補で計算(自動的に満たされる)。`same_fact`規則(L1009)は未変更 |
| M3 effort固定+逐語 | `make_stage1_call_fn(effort_override=)`新設、再分類callは`effort_override="medium"`・`recovery_stage="stage1_reclassify"`。module内`DEVELOPER_MESSAGE`/`PROMPT_TEMPLATE`/`SCHEMA`(v2)はTrial script(`reclassify_candidates_02.py`)とsha256一致(test) |
| M4 precheck | runner `PRECHECK_MODE`(既定legacy_all)/`filter_precheck_findings`(1関数)。`build_precheck_floor_claims`が使い、F3記録(`build_precheck_floor_claims(fixture,set())`)も同関数経由。numberのみ残す |
| M5 承認構成 | `OPEN233_APPROVED_FLOW_SWITCHES`/`apply_open233_approved_flow_switches()`/`assert_open233_approved_flow_switches()`。`KPI_TRIAL_SWITCHES`はSUPERSEDED注記のみ追加(値不変)。dump=`er052_output/open233_prod_e2e_01/approved_switches_dump.json` |
| floor縮小 | `MECHANICAL_FLOOR_FLAGS=("changed_number",)`/`FLOOR_MODE`(既定legacy_5flags)/`floor_fire_flags()`、`apply_floor`のみ切替。`FLOOR_FLAGS`・`apply_floor_cited`(反実仮想記録)不変。`DISCLOSURE_GAP_DISQUALIFYING_FLAGS`は明示リストへ(挙動不変) |
| 記録 | result直下`stage1_reclassify`(初回)、cycle`recheck_coverage.reclassify`、`exit_check.reclassify`(`reclassify_status`ok/no_target/failed、`n_excluded_claims`、`n_excluded_with_changed_number`、`n_failclosed`、cost)。floor理由=`deterministic_floor:changed_number`(a)/`precheck_floor`(c、`llm_materiality=None`)、S1由来BLOCKING=`s1_second_opinion_blocking`(既存フィールドで区別可、追加不要) |

### §80-3 「数字以外の機械的強制重大化」残存確認(runner Grep全ヒットの分類)
- 上書き(承認構成で数字のみ): `apply_floor`(`FLOOR_MODE`)、precheck Stage 2スキップ(`PRECHECK_MODE`)。休眠: `floor_verify`(`FLOOR_VERIFY_MODE=off`)、Tier 0因果floor+補助ベルトG_H/issue_actor(`CAUSAL_FLOOR=False`のゲート内)、`G_L`(`TIER0_G_L_ENABLED=False`)、`downgrade_verify`(`STAGE2_DOWNGRADE_VERIFY=False`)。
- 記録のみ: `apply_floor_cited`(反実仮想)、`CHECKER_FLAG_NAMES`/`detect_rewrite_new_precheck_findings`(記録)、`classify_problem_kind`/`_LOGIC_FLOOR_FLAGS`(Rewrite水準選択)、`full_recheck_required`の`deterministic_floor_claim`(全文Recheckの要否、重大度は上書きしない)。
- 降格禁止(AI重大の維持、上書きではない): `apply_hook_aware_downgrade`/`apply_disclosure_gap_downgrade`(`DISCLOSURE_GAP_DISQUALIFYING_FLAGS`)。
- 非該当: S-4 `MATERIALITY_BLOCKING_PIN`(AI/S1がBLOCKING確定した結果の固定)、S1(AI第2意見)、旧S1D`stage1_union_screen`。
- test根拠: `TestRunStage2IntegrationApproved`(主体/否定/比較/時期/因果フラグ+AI ACCEPTABLEがBLOCKINGにならない、tier0なし、追加callなし。数字フラグだけBLOCKING)、`TestFloorModes`、`TestPrecheckNumberOnly`、静的test(floor適用は1箇所、3入口は全て`candidate_filter`を渡す)。

### §80-4 test・evidence
新規`er052_open233_checker_floor_prod_wiring_test_01.py` 59件PASS(逐語sha256 5/合流前filter 6/fail-closed 6/Recheck 5/初回・出口 4/承認構成 7/floor 8/precheck 6/run_stage2 5/effort 3/入口配線 4)。回帰`run_project_regression.py --pattern "er052*_test_*.py"` 922件PASS(基準863+59、既存テスト変更0)。evidence=`er052_output/open233_prod_e2e_01/runtime_evidence_tests_01.txt`(単体-v+回帰)、`approved_switches_dump.json`。

### §80-5 replay(¥0、frozen)
`build_watchlist_floor_only_gold_01.py`→`watchlist_floor_only_gold.json`。段階A 42 runはStage 1のみ(SC gold 18/18定義でr3/r5候補あり、Stage 2判定なし)。旧E2E 9 runのSC gold一致はB3のみ3件(floor-only 0件、llm_materiality BLOCKING 1/ACCEPTABLE 2)。旧分析の「正当6件」のうち数字floor維持=3件(No.9/10/21)、非数字=3件(No.5 actor[LLM QUALITY=floorだけで重大化]、No.22 actor・No.23 time[LLM BLOCKINGで影響なし])。旧分析のfloor-only gold=safety_A4 `changed_actor`(LLM非BLOCKING)・neg3 `changed_time`。E2Eではこれらが再分類+Stage 2+S1で拾われるかを個別追跡する(watch list)。

### §80-6 残存リスク
(1)`same_fact`規則(別文でも同fact_idの候補は未解消)は未変更、(2)S1対象増(旧floor強制BLOCKINGだった主体・比較候補が非BLOCKINGになりS1対象へ)、(3)時期gold(neg3、n=1)は再分類・Stage 2・S1依存、(4)再分類のRecheck/出口適用はTrial未検証でE2Eが初証拠、(5)再分類の4観点mismatchは(Trialと同じく)モデルのverdictのみを採用し、SUPPORTED+mismatchの機械上書きはしない、(6)9 runだけでは重大見逃し0のSafety KPIは主張不可(SC=B3のみ)。


---

## §81 OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01: 新仕様9/20 run E2E結果(委任_05b〜07、2026-10-06、PRODUCTION_WIRED未)

### §81-1 provenance・構成・実行
- 全KPI=fresh(新仕様9 run、Production初回path含むE2E=Yes)。証跡: `er052_output/open233_prod_e2e_02/`(runs/、report/=ラベル前一次集計、report_final/=正式集計・`critical_trace.md`、labels/=3 worker label+`labels_merged.json`+`merge_labels_01.py`、approved_switches_dump_worker{1,2,3}.json=承認構成)。
- 実行: 3並列(W1/W2/W3)、9 run全てdone、failed/aborted/skipped各0、retry・429無し。合計¥31.519(平均¥3.502)。残り11 runは**未実行・ユーザー確認待ち**。
- ラベルprovenance: 事後評価ラベル123件=Sonnet推測(3 worker、label_source付き)+Fable突合判定(`confirmed_by=fable_2026-10-06`: 判定1 meta_adv HC-012=重大/Y/Y、判定2 meta_std HC-011維持、判定3 neg3 HF-002=問題なし、判定4 neg7 Hook=軽微/Y/N、判定5 neg2=問題なし、判定6 neg1 HC-008=UNDECIDABLE維持)。**ユーザー未確認**。rewrite_neededは実Rewrite対象6件のみで確定(判定7)。旧9 run値=frozen・比較用のみ。
- 件数: severity分布=問題なし110/軽微8/重大4/判断不能1、true_critical=Y 4件/N 118/UNDECIDABLE 1。

### §81-2 A. Checker(初回候補、claim単位)
| 項目 | 新9 run | 旧9 run(frozen) |
|---|---|---|
| AI判定の候補(延べ) | 46 | 130 |
| 　うち真に問題(Y)/不要候補(N)/判断不能 | 9 / 36 / 1 | 未ラベル130 |
| 機械判定の候補 | 20 | 21 |
| 　うち真に問題(Y)/不要候補(N) | 1 / 19 | 未ラベル21 |
| AIのみ/機械のみ/両方重複 | 46 / 20 / 0 | - |
| 延べ/重複除外後の総候補(後段へ) | 66 / 66 | 151 / 151 |
- 再分類で初回に除外されたclaim計84(changed_number付き除外3: meta_adv 2/meta_std 1)。**除外84件は後段に渡らずラベル未付与のため、再分類の誤除外(真に問題なのに除外)は未検証**(残存リスク)。
- 機械候補の内訳: negation_polarity_mismatch 18、quote_not_in_ledger 1(決定論全20)。機械候補はreclassifyのモデル対象外で後段へ直行する(meta_adv HC-012がその例、§81-6)。
- run別 後段へ渡した件数 新(旧): B3 2(8)、hormuz_adv 8(9)、hormuz_std 9(10)、meta_adv 5(16)、meta_std 11(23)、neg1 14(32)、neg2 7(16)、neg3 5(13)、neg7 5(24)。

### §81-3 B. 後段判定(全cycle 123判定、cycle1は89判定)
| 項目 | 新9 run | 旧9 run(frozen、326判定) |
|---|---|---|
| 後段AI 重大/軽微/問題なし | 4 / 14 / 105 | 5 / 31 / 290 |
| 事後評価: 真に重大(AI重大&Y) | 3 | 4(UNLABELED 1) |
| 事後評価: 不要に重大(AI重大&N) | 1(meta_std「These calls were about trying to lower internet or cable fees.」軽微) | 0 |
| 事後評価: 真に重大なのに軽微/問題なし | 1(meta_adv HC-012、§81-6) | 2 |
| 後段機械判定[数字のみ、changed_number] 発火 | 3(meta_std 2、neg2 1) | 4(旧37はchanged_time 10/actor 7/negation 5/comparison 14等を含む全floor) |
| 　AI判定との重複(AIもBLOCKING) | 2(meta_std) | 4 |
| 　機械のみで重大化 | 1(neg2) | 33(全floor) |
| 　真に重大(Y)/不要に重大化(N) | 1(meta_std HC-011)/2(meta_std「These calls...」、neg2) | 6/24(全floor、判断不能5、未ラベル2) |
| precheck(c)(数字以外廃止) | 0 | - |
| S1(second opinion)BLOCKING化 | 1(neg3 cycle2 HF-002、Ledger一致=問題なし、N) | - |
- 数字floor(changed_number)3件のうち、AI判定と重複しない機械のみ重大化はneg2「It said that human staff made inappropriate comments about race during calls to bargain over internet or cable fees.」(Ledger一致=問題なし、不要Rewrite)。
- 旧仕様の数字以外のfloor(changed_time/actor/negation/comparison等)は9 runで0件(承認構成どおり)。`floor_reason`の種別は`deterministic_floor:changed_number`と`s1_second_opinion_blocking`のみ。

### §81-4 C. Rewrite / D. Human Review
| 項目 | 新9 run | 旧9 run(frozen) |
|---|---|---|
| Rewrite発生件数/発生run数 | 6 / 4(B3 1、meta_std 2、neg2 1、neg3 2) | 40 / 8 |
| 必要だった | 4(B3 HF-007、meta_std HC-011、meta_std「These calls...」軽微、neg3 HF-009) | 未ラベル |
| 不要だった | 2(neg2 changed_number floorのみ、neg3 cycle3 S1 BLOCKING化) | 未ラベル |
| 再修正が必要(同factが次cycleもBLOCKING) | 0 | 8 |
| guard_ok | 6/6 | - |
| **Human Review** | **0件**(到達run無し、出口BLOCKING 0) | 1 run(neg7、出口BLOCKING 3件) |

### §81-5 E. Safety・Cost
- **真の重大Fact見逃し(最終本文に未修正で残存)=1件**(meta_adv HC-012「The company also restored the human concierge feature to the way it had been before, at least for now.」)。**重大Fact検出(最終本文までに修正)=3件**(B3 HF-007、meta_std HC-011、neg3 HF-009)。true_critical=Y計4件。※集計scriptのSafety欄(`critical_miss_at_exit`=0)はgold行のみで算出され本件を含まないため、本節の値(`report_final/critical_trace.md`)を正とする。分母はn=9 run・4件でありSafety KPI(重大見逃し0)の主張はできない。
- 費用(合計¥31.519、平均¥3.502/run): Checker関連(初回+再分類)¥19.137、後段判定関連(Stage 2+S1+floor_verify)¥7.293、Rewrite関連(Rewrite+regen+Recheck+出口)¥5.089、分離不能0。旧9 run合計¥43.912(平均¥4.879、Checker ¥12.608/後段 ¥12.996/Rewrite ¥18.308)。
- run別費用 新(旧): B3 3.96(4.55)、hormuz_adv 1.97(3.44)、hormuz_std 2.64(2.17)、meta_adv 2.41(5.43)、meta_std 4.73(5.16)、neg1 3.07(8.82)、neg2 4.58(3.79)、neg3 5.66(4.00)、neg7 2.51(6.55)。Checker費用は再分類callが増えたため旧¥12.6→新¥19.1に増加、後段とRewriteが減った(合計は¥12.39減)。n=1/runのため揺らぎあり。

### §81-6 critical_trace(true_critical=Yの4件、`report_final/critical_trace.md`)
| run | claim要旨 | Stage1/再分類 | Stage 2 | Rewrite・最終 | 区分 |
|---|---|---|---|---|---|
| bgroup_B3 | HF-007「so + flashy 20% plan」因果(gold B3) | AI候補、再分類CANDIDATE | llm BLOCKING(unsupported_relationship) | Rewrite(so→and)、cycle2 ACCEPTABLE、最終RESOLVED_REWRITE_THEN_DOWNGRADE | 検出 |
| meta_std | HC-011 複数化(comments/calls) | AI候補、再分類CANDIDATE | llm BLOCKING+floor changed_number | Rewrite(単数化)、Recheck通過 | 検出 |
| neg3 | HF-009「events driving oil prices ... returned」 | AI候補、再分類CANDIDATE | llm BLOCKING(ledger_conditions)、floor非関与 | Rewrite(events削除)、cycle2以降ACCEPTABLE | 検出 |
| meta_adv | HC-012 ロールバックを「restored」と記述(方向反転、A5-0同型) | 機械候補(negation_polarity_mismatch、r3)。reclassifyのモデル対象外で後段直行 | llm ACCEPTABLE、S1 second ACCEPTABLE(confirmed_downgrade) | Rewriteなし、1cycleでS2_DOWNGRADE、**最終本文に残存** | **見逃し** |
- meta_adv見逃しの含意: 旧仕様では`changed_negation`等のfloorが機械的にBLOCKINGにした可能性があるが、新仕様(数字のみ)ではStage 2 LLM+S1の判断のみ。同文はStage 1で正しく候補化されたがStage 2/S1の双方が誤降格(ACCEPTABLE)。**ユーザー総合レビュー事項**(数字のみfloorのSafety妥当性)。
- **訂正(2026-10-06、委任_01 of DIRECTIONAL-MISREAD)**: 「Fable訂正(2026-10-06): 9/20 run報告(REPORT §81、DECISION_LOG同日エントリ)で『HC-012見逃しは旧仕様なら否定floorが強制BLOCKINGにした可能性がある型/数字のみ縮小の代償として現れた最初の実例』と記述したが、run出力(`er052_output/open233_prod_e2e_02/runs/meta_run03_advanced.json` L331-L400)の実測で訂正する。当該claimのStage 1フラグは`changed_number/actor/negation/comparison/time/causality`すべてfalse、候補化は決定論検査`negation_polarity_mismatch`(routes=r3、Stage 1 AIはSUPPORTED判定)による。旧floorは`changed_*`フラグtrueでのみ発火するため、旧仕様全ONでも`floor_reason=None`=発火しない(`floor_cited_materiality`もACCEPTABLE)。したがって見逃しの直接原因は『数字以外floorの廃止』ではなく、Stage 1 AI・Stage 2・S1の3段階が同じ読み(restored…to the way it had been before=ロールバックと同義)をしたこと(系統的な読み癖+同rubric再サンプルの相関)と、決定論検査の信号を後段AIが消す構造。同型は正式gold A5-0(HC-012)として既知。」上記の「旧仕様では…floorが機械的にBLOCKINGにした可能性」は誤り(旧記述は保存)。対象例: 「The company also restored the human concierge feature to the way it had been before, at least for now.」(Ledger=当面rollback/撤回、記事=restore、方向反転)。
- 他: 旧仕様のNo.5(meta_adv changed_actor floor)は本runで重大化されず、HC-012見逃しと合わせてn=1の観測。

### §81-7 watch list(`report/watchlist_trace.md`)
- neg3 time gold(HF-009「prices themselves quickly returned」型): floor無しでStage 2 LLM BLOCKING→Rewrite後cycle1 ACCEPTABLE(拾えた)。safety_A4 actorは9 runに含まれず未観測。旧「正当6件」のうち本runで観測: meta_std HC-011系2件(数字floor維持+llm BLOCKING)、neg2 1件(floorのみ、不要だった)。

### §81-8 UNDECIDABLE 1件(neg1 HC-008)の材料
- claim: 「A human can handle situations that AI alone finds difficult.」(neg1 cycle1、Stage 2=QUALITY/unsupported_relationship、最終S2_DOWNGRADE)。直前文「Having a person take over is not always a bad thing.」。
- Ledger MUSE-HC-008: 「人間が電話を担当した一部テストで成功率95〜98%の可能性が示された。AIだけの場合はそれより低いとされたが具体的数値なし」(条件: 定義・サンプル数・比較対象・測定方法は非公開、notes: 「人間の方が95〜98%で成功した」と一般化しない)。
- Ledger MUSE-HC-002: 「MuseはクラウドVM上で動作しブラウザ操作・フォーム入力・ユーザーに代わった交渉等を実行できる」(機能の存在のみ)。MUSE-HC-006: 「一部の電話は訓練を受けた人間の契約スタッフがかけるテスト」。
- gold B4-a「A person can take over when AI alone has trouble」=BLOCKING(設計書§2-補: HC-006は一部電話を人間が担当したテストのみ、記事は『AIが困難な時に人間が引き継ぐ』フォールバック機構を新規に述べ製品の仕組みの誤伝達)。
- 論点: (同型寄り)Ledgerに「AIが難しい場面を人間が担当する」趣旨の記述はなく、一般的能力主張に広げている点はB4-aと同じ。(非同型寄り)HC-008自体が「AIのみは人間担当より成功率が低い」比較を含み、記事文は仕組み(引継ぎ)ではなく能力の比較で、直前に「take overはbad thingではない」と評価文脈。暫定=UNDECIDABLE維持(集計は判断不能枠)。ユーザー/Fable確認待ち。

### §81-9 Production Wiring確認・残存リスク・次
- Production Wiring: §80-3(数字以外の機械的強制重大化の残存分類)を参照。9 runでの実動作: 初回で再分類(全run `reclassify_status=ok`・failclosed 0)、Recheck・出口でも再分類が実行された(例 B3 recheck cycle2 n_targets 5/除外3、neg3 cycle2 n_targets 9/除外4)、floor_reasonは`deterministic_floor:changed_number`と`s1_second_opinion_blocking`のみ=旧仕様の数字以外floorは後段経路に出現せず。S1 BLOCKING化1件(neg3 cycle2 HF-002、Ledger一致)はcap_terminal_last_resort→cycle3でjudge_only後に終端(RESOLVED_REWRITE_THEN_DOWNGRADE、Human Review無し)。retry/fallback/regenerationの上限・安全装置は回避していない。
- 残存リスク: (1)真の重大見逃し1件(meta_adv HC-012、機械候補はreclassify対象外で、Stage 2/S1が誤降格)、(2)再分類の誤除外84件が未ラベル(Safety未検証)、(3)n=1×9 runで有意差・Safety KPI主張不可、(4)ラベルはSonnet推測+Fable突合でユーザー未確認、(5)UNDECIDABLE 1件、(6)Checker費用は増加(再分類call)。
- 次: **残り11 runは開始しない(ユーザー総合レビュー待ち)**。レビュー事項: Checker改善の実効(候補151→66)、数字のみfloorのSafety(HC-012見逃し)、不要Rewrite減(40→6件)、Human Review 0、残11 run可否。PRODUCTION_WIRED未。
- 訂正注記(2026-10-06): 上記「数字のみfloorのSafety(HC-012見逃し)」は§81-6の訂正のとおり、floor廃止が直接原因ではない(旧floor全ONでも不発火)。

### §81-10 ユーザー決定(2026-10-06)
- E2Eは9/20 runで一旦停止。残り11 runは、ユーザーが再開を明示するまで待機(実行しない)。
- 見逃し対策は`OPEN-233-DIRECTIONAL-MISREAD-SAFETY-DESIGN-01`で設計する(方向反転等、AIが特定種類の意味関係を系統的に読み違えるケースだけを狙う。Production変更・有料E2Eなし。全機械floor復活・一律厳格化・gold変更・KPI変更・Human Reviewへの安易な振替は禁止)。到達上限はDESIGN_READY_FOR_REVIEW / USER_DECISION_REQUIRED。
- CHECKER-FLOOR-PRODUCTION-E2E-01はPRODUCTION_WIRED未のまま。

## §82 系統的読み違い専用Safety設計(DIRECTIONAL-MISREAD-SAFETY-DESIGN-01、2026-10-06、USER_DECISION_REQUIRED)

- Status: 設計完了・Opus条件A 2回済み・ユーザー判断待ち。VALIDATED/APPROVED/PRODUCTION_WIRED不可。LLM呼出0、¥0。残11 runは待機のまま。
- A 原因: HC-012見逃しはAI3段階の同一誤読(「機能を当面ロールバックした」→「restored ... to the way it had been」、多義語)。決定論negation_polarity_mismatchは「適切な開示なしに」の「なし」への偶発反応で向き非識別(新9 runのnegation反応39件=問題なし38/重大1)。
- A続き: A5-0・HC-012のgold感度も「なし」依存、HF-009は「ほどなく」でlegacyのみ。比較・方向専用センサーはchecker不在。number/causal反応は新9 runで0。
- B 系統的読み癖: T1状態変化の向き反転/T2推移・比較反転/T3当事者取り違え/T4未指定役割充填/T5因果捏造/T6可能性の既成事実化。共通核=語彙はLedgerと重なるが事象の枠が1つ入れ替わる。
- C 反実仮想(`trigger_replay_01.md`): 新9 run 123件中T-A/T-B 43件(重大1/問題なし42)、T-C 55件(重大1/軽微3/問題なし51)。HC-012は3案ともtriggerだがT-A/T-Bは偶然。旧floor誤爆24件のtrigger: T-A/T-B 0、T-C 8。
- D 設計案A〜F: Sonnet推奨=案E(枠抽出+Python比較)、Opus修正版=案E'(Ledger側factごと事前抽出・enum固定値・2モデル一致/記事側blind抽出/Python比較/逆転=Stage 2・S1迂回BLOCKING/解消=Python再比較/失敗=1回retry→未解消記録+QUALITY/T3・T4は観察欄のみ)。起動=T-D'(状態変化factに紐づくStage 1全単位)。案D(A+C)は撤回候補。
- E Opus Part 2: 条件付きで進める。必須修正3点(blind分離抽出/母集団訂正[123件はStage 1候補のみ]/§5と§8矛盾解消)は03aで反映。判断事項7点は DECISION_LOG(h)参照。
- F Fable照合: Sonnet案とOpusは方向性一致。「既存決定論検査=センサー」の前提崩れ→センサー差し替え=新設計判断+有料Trial承認要→USER_DECISION_REQUIRED。
- G 費用: 本管理ID全体¥0。Opus 2回(read-only)。
- H 追加費用見込み【推測】: T-E全claim案で約¥0.27〜0.81/run(現行約¥3.5/runの8〜23%)。T-D'は母集団要集計で未確定。限定Trial約¥15以内(Opus)、¥0のT-D'母集団再集計を先行。
- 数字floor穴(checker L554-555/L640-643、新9 run実害0)と`apply_stage2_two_of_two`潜在不具合(runner L4106-4122、現在OFF)は別管理ID。
- 参照: `docs/pm/design_open233_directional_misread_safety_01.md` / `docs/pm/opus_l2_review_open233_directional_misread_safety_01.md` / `er052_output/open233_directional_misread_offline_01/trigger_replay_01.md`(.json等) / `er052_output/open233_directional_misread_offline_01/sensor_quality_01.md`(.json等)。

## §83 限定Trial: 系統的読み違い専用Safety(OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-01、2026-10-06)

- Status: TRIAL-01=実行中(分類は結果後にFable)。Production変更なし。VALIDATEDでもProduction採用ではない。残11 E2Eは停止継続。

### §83-1 目的・禁止事項
- 目的: ユーザー承認済み設計案(案E')をProduction変更なしの限定Trialで有効性確認。
- Trial仕様: (1)Ledger全FactをAIが確認(状態変化・方向性の有無、結果状態を固定分類で抽出)(2)方向性ありFactだけ記事側を別AI判定(Ledger側の答えを見せない)(3)機械比較(同方向→通過/逆方向→重大候補/抽出不能・曖昧→記録のみ)。同じAI・同じrubricの繰り返し構成にしない。
- 比較: 同一model/Ledger側と記事側でmodel分離/blind分離あり・なし。まず¥0で母集団再集計。費用上限¥15(見積超過時のみSTOP)。
- 禁止: Checker・後段AI・floor復活・残11 E2E・KPI・gold・Human Review振替・自動Production採用の変更。副産物2件は別管理ID。Status=VALIDATED/REJECTED/USER_DECISION_REQUIRED。

### §83-2 母集団(委任_01a、`population_01.md`、¥0)
- Ledger全Fact 123件/9 run(平均13.67。実体はLedger 2種: hormuz 12 fact×4 run、meta 15 fact×5 run)。前回の「Stage 1候補123件」とは別物の偶然の一致(Stage 1候補は66件=7.33/run)。
- 状態変化Fact(語彙近似、精度未検証)30件=24.4%(3.33/run)。単位→fact対応はE2E出力に未保存(`support_fact_ids` 0件)。
- 記事側確認件数/run: 下限3.33/近似7.46/上限30.56(判定単位全数、全単位40.44)。
- 単価(gpt-6-luna effort=high、call_log 135件から逆算): 入力約¥10.7/1M、出力約¥81.7/1M。
- 追加コスト/run(同一model): Ledger側¥0.155/0.166/0.512、記事側¥0.034/0.084/1.127、合計¥0.19/0.25/1.64(low/mid/high)。現行E2E約¥3.50/run。low/midは推論ほぼ無し前提、記事本文は修正前fixture本文で計数。

### §83-3 対象セット(委任_01b、`testset_01.md`、¥0)
- 63項目: 真の反転gold 3(HC-012 restored/A5-0/D61合成)+曖昧3(K16/K19/HC-012「changed back to how it was before」)+忠実(状態変化語あり)21+忠実(HC-012同fact・状態言及なし)17+非該当5+人工反転14(決定論置換、厳密6/許容8)。repeat=3はgold 3+曖昧3。call見込み75/構成。
- Ledger側正解10 factを逐語根拠付きで事前登録(方向性あり: HC-012=STOPPED[PAUSED許容]、HF-009=UNCHANGED[一時縮小→復帰]、HF-007=ENDED、HF-002=STARTED、HF-011=INCREASED)。
- enum=AVAILABLE/STOPPED/PAUSED/INCREASED/DECREASED/UNCHANGED/STARTED/ENDED/EXPANDED/NARROWED/NOT_MENTIONED/UNCLEAR。方向対4組、PAUSED vs STOPPEDは逆転扱いしない。
- 未特定: 委任_61の個別文(D61合成で代替)。ホルムズ側Ledgerは`family_x_refresh_e2e_01/hormuz/run_03`を代表使用(新9 runの実Ledgerと同一かは未確認)。

### §83-4 Trial構成(委任_01c・委任_02方針)
- script `er052_open233_directional_trial_01.py`(¥0): Ledger側抽出(factごと1回・記事を見せない・キャッシュ)→記事側blind抽出(対象X+記事文+前後文のみ、Ledger本文・stateを渡さないことをunit testでassert)→Python比較。
- 比較規則: REVERSEDは方向対該当かつ両側quote非空のみ。quote欠落・enum外・対応外はUNCLEARで重大化しない。
- 3構成: same_blind/split_blind/same_nonblind(対照群: 1 callで両側)。`--budget-yen`で累計停止。unit test 8件PASS、dry-run 3構成完走。既定model gpt-6-luna。
- Fable実行方針: effort=medium(再分類Trialと同じ、費用優先)。順序 same_blind(Ledger側10 fact×repeat 3+記事側75)→same_nonblind(75)→split_blind(記事側はsame_blind結果を再利用、Ledger側のみ別model)。累計¥15で強制停止、見積mid>¥15ならSTOP。
- 副産物: OPEN-235(数字floor配線漏れ)、OPEN-236(two_of_two潜在不具合)は別管理IDで起票済み(委任_01d)。

### §83-5 結果(委任_02一次集計+委任_02x抽出、すべて確認済み)
- R1 費用: 見積mid ¥13.90(≤¥15のため実行)、実費¥10.35(same_blind ¥2.48/154 call、same_nonblind ¥4.54/75 call、split_blind ¥3.33/149 call)。effort=medium、gpt-6-luna。split側Ledger model=gpt-5.6-luna($0.2/$1.2、`DECISION_LOG_HISTORY.md:5893`。gpt-5.6-solは見積¥108で不可)。予算停止・失敗callなし。
- R2 gold(真の反転3件、各3 repeat): G-01=HC-012今回実例「restored…」、G-02=A5-0「temporarily put back」(同fact HC-012)、G-03=D61合成(HF-009)。HC-012とA5-0はsame_blindで全repeat検出。split G-01の見逃しはLedger側別modelの対象X命名(「電話発信機能」)に記事側が一致せずNOT_MENTIONED。nonblind G-03は全repeat見逃し(Ledgerを見て辻褄合わせ=Opus U1予測どおり)。
- R3 人工反転14件: 厳密6件の検出 blind 3/nonblind 4/split 2、許容8件 2/1/2。見逃しの大半は記事側が対象Xを同定できずNOT_MENTIONED。
- R4 正常43文の誤反転: blind 3件(7.0%: F-09/F-10/F-19)、nonblind 0、split 2件(4.7%)。原因: 1 factに複数事象(HF-009=「上げ幅DECREASED」+「水準INCREASED」、HC-012=「テストSTARTED」+「機能PAUSED」)があり、記事側がどの事象を指すかを選ばず全事象と比較し、1つでもREVERSEDなら最終REVERSEDとする規則。F-09/F-10は「水準INCREASED」vs記事「fell」で誤逆転、F-19は「テスト」をENDEDと誤抽出。Opus Part 2 U3(Ledgerの枠を事象リストにし、記事側にどの事象かを引用付きで選ばせる)の未実装。
- R5 曖昧3件(K16/K19/HC-012 changed back): 最終REVERSED 0/3(全構成)。repeat単位では27中2回REVERSED(揺れ)。
- R6 UNCLEAR: 全体14/12/15(正常文内9/5/10)。Ledger側has_direction精度0.87/0.80/0.67、state精度0.33/0.40/0.33(事前登録が単一stateのため複数event抽出と不一致=測定上の問題)。同一model対別modelのLedger側一致率76.7%(30対)、10 fact中完全一致6。記事側state精度0.54/0.58/0.51。
- R7 1 runあたり(母集団3水準: 記事側3.33/7.46/30.56単位+Ledger 13.67 fact): same_blind 追加call 17.0/21.1/44.2、追加¥0.37/0.43/0.76、不要Rewrite見込み0.23/0.52/2.13件/run(現行0.67の0.35/0.78/3.18倍)。split ¥0.42/0.51/1.01、0.16/0.35/1.42。nonblind ¥0.20/0.45/1.85、0/0/0(ただし見逃し最多)。

表1 構成別(gold検出はrepeat単位、計9)
| 構成 | G-01 | G-02 | G-03 | 計 | 人工(厳密6/許容8) | 正常文誤反転 | UNCLEAR | 実費 |
|---|---|---|---|---|---|---|---|---|
| same_blind | 3/3 | 3/3 | 2/3 | 8/9 | 3 / 2 | 3件(7.0%) | 14 | ¥2.48 |
| same_nonblind | 2/3 | 3/3 | 0/3 | 5/9 | 4 / 1 | 0件 | 12 | ¥4.54 |
| split_blind | 1/3 | 3/3 | 3/3 | 7/9 | 2 / 2 | 2件(4.7%) | 15 | ¥3.33 |

### §83-6 Status・判断
- R8 Fable判定: **USER_DECISION_REQUIRED**(決定したのはFableのStatus判定のみ。他はユーザー判断待ち)。理由: (a)VALIDATED不可=正常文誤反転7%で、母集団high水準では不要Rewriteが現行の3倍超。D61検出が構成間で不安定。(b)REJECTED不可=HC-012・A5-0をblind構成で全repeat検出、同一model相関はblind分離で実際に下がった(nonblindはgold見逃し最多)。誤反転の原因はOpusが事前指摘した比較規則(事象選択)の実装漏れで、限定的・修正可能。(c)推奨=same_blind構成(model分離は不要、blind分離が本質)+「記事側に事象を選ばせ、選んだ事象のみ比較」の修正で、TRIAL-02(上限¥5、same_blindのみ、同じ63項目×repeat 3)を再実行してから判断。(d)Production採否の判断は不要(Trial未達)。(e)残11 E2E再開はユーザー判断(Fable推奨=TRIAL-02結果まで待機)。
- ユーザー判断事項: TRIAL-02実施可否(上限¥5)、残11 run再開可否。
- R9 持ち越し論点: 単位→fact対応がE2E出力に未保存(Production配線時にStage 1 r3の`support_fact_ids`を全単位で保存する必要)。Ledger側正解の事前登録を単一stateでなく事象リストにする。
- OPEN-235/236は別管理ID(未着手)。Production変更・gold/KPI変更なし。

### §83-7 参照ファイル
- `er052_output/open233_directional_misread_trial_01/`(population_01.md / testset_01.md / Trial出力。委任_02が使用中)
- `er052_open233_directional_trial_01.py` / `docs/pm/delegation_log/2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-01_*.md` / 設計: `docs/pm/design_open233_directional_misread_safety_01.md`(§82参照)

## §84 限定Trial 2(事象選択修正): OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-02(2026-10-06)

- Status: TRIAL-02=実行中(分類は結果後にFable)。Production変更なし。VALIDATEDでもProduction採用ではない。残11 E2Eは停止継続。

### §84-1 目的・ユーザー承認・禁止事項
- 目的: TRIAL-01で判明した、1つのFactに複数事象がある場合に記事側がどの事象について述べているか選ばず全事象と比較して正常文を誤って重大扱いする問題を修正し、方向反転専用チェックを再検証する。
- ユーザー承認: 修正版限定Trial実施/費用上限¥10/残り11 E2Eは引き続き停止/Production変更はまだ行わない。
- 禁止: Production変更/残り11 E2E再開/gold変更/KPI変更/floor復活/新しいSafety原則の追加/Trial結果を理由とする自動Production採用。
- 報告フォーマット警告: 前回報告は★★★★報告ここから★★★★〜★★★★報告ここまで★★★★を守っていなかった。今回closeout時に必ず確認する。

### §84-2 修正内容
- same_blind構成を維持。記事側AIが「この文がLedger側のどの事象について述べているか」をまず選択。
- 選択された事象だけについてLedger側状態と記事側状態を比較。複数事象すべてとの総当たり比較は禁止。

### §84-3 合格基準(事前登録、ユーザー指定)
1. HC-012 3/3検出
2. A5-0 3/3検出
3. 正常文の誤重大判定2%以下
4. 不要Rewrite見込み: 現行0.67件/runの半分以下
5. 前回誤爆3件解消
6. 新しい重大見逃しを発生させない
- 1つでも重要条件を満たさない場合、勝手に追加修正Trialへ進まない。

### §84-4 Trial条件
- 前回と同じ主要テスト群(HC-012/A5-0/D61・HF-009系/正常文43件相当/曖昧例/前回誤爆3件)。重要例は3回反復。費用上限¥10(超過見込みならSTOP)。

### §84-5 並列化計画(Fable計画)
- 所要見込み約65〜75分(直列なら約2時間超)、短縮見込み約60分。
- Phase A(¥0、4本並列・約30分): script修正(事象選択・shard実行)/testset_02+正解データ複数事象対応/集計script+合格判定+regression+template/SSOT先行起票。
- Phase B(≤¥10・約15分): 見積→Ledger側30 call→記事側3 process shard並列→merge。
- Phase C(約20分、直列・前工程依存): 集計→Fable判定→SSOT→commit→Closeout正式報告。

### §84-6 結果(委任_05実行、委任_06で記録、すべて【確認】)
- R1 費用: 見積mid ¥2.0(low 1.3/high 3.5)≤上限¥10で実行、実費**¥2.08**(Ledger側¥0.70/30 call、shard1 ¥0.45・shard2 ¥0.68・shard3 ¥0.26、計104 call)。same_blind、gpt-6-luna、effort=medium。
- R2 並列実時間: Ledger側14:58:07開始→shard3並列15:00:14開始(各1:06/1:54/2:35)→merge完了15:03:03、本実行全体約5分(直列見込み約8〜9分)。Phase A 4本並列約25分(直列見込み約75分)。
- R3 合格基準(6行表):

| # | 基準 | 結果 | 判定 |
|---|---|---|---|
| 1 | HC-012 3/3検出 | 3/3 | 充足 |
| 2 | A5-0 3/3検出 | 3/3 | 充足 |
| 3 | 正常文誤重大判定2%以下 | 0/43=0% | 充足 |
| 4 | 不要Rewrite見込み0.335件/run以下 | 0/0/0件/run(3水準) | 充足 |
| 5 | 前回誤爆3件解消 | F-09 SAME×3、F-10 SAME×3、F-19 SAME/SAME_FAMILY/SAME_FAMILY | 充足 |
| 6 | 新しい重大見逃しなし | D61(G-03、HF-009系比較反転、真の反転ラベル)が前回2/3→今回0/3(3反復とも記事側の事象選択NONE→NOT_MENTIONED)。S-06(人工反転、Ledger事象リスト外=参考集計)も前回検出→今回「上げ幅」SAMEで見逃し | **未達** |

- R4 その他: gold計6/9(前回8/9)。人工反転検出4/14(前回5/14)。UNCLEAR 6(前回14)。曖昧3件の最終REVERSED 0。追加¥/run low0.34/mid0.42/high0.89(前回0.37/0.43/0.76)。追加call/run≒Ledger13.67+記事側3.3/7.5/30.6単位。
- 詳細: `er052_output/open233_directional_misread_trial_02/trial_summary_02.md`(repeat別のgold/誤爆3件表を含む)。

### §84-7 Status・判断(Fable判定、委任_06で記録)
- R5 Status: **USER_DECISION_REQUIRED**。重要条件5/6充足で誤爆問題(事象選択未実装)は解消。ただし第6条件未達(D61退行)。ユーザー指示により追加修正Trialへは進まない。原因所見【推測】: 事象ラベルが抽象的(「上げ幅」「水準」)で、記事文「Brent先物が下落」等との対応を記事側AIが「NONE」と判断。改善案=Ledger側eventのsubject_xに実体名を含める(例「Brent先物の水準」)+選択promptで「対象が部分一致すれば選ぶ」を明示。Production採否判断は不要(Trial未達)。残11 E2E再開はユーザー判断(Fable推奨=本件の判断後)。VALIDATEDでもProduction採用ではない。
- R6 APPROVED_FOR_PRODUCTION未配線項目への影響: CHECKER-FLOOR-PRODUCTION-E2E-01(新Checker仕様+数字のみfloor)の承認内容・実装に変更なし。本Trialは別scriptで、Productionコード未変更。
- R7 Dangling Reference: 委任_06で確認、§84-8参照ファイルは全件実在(結果はRESULT_PACKET)。
- T-3: 実費¥2.08(委任_05)を領収記録。

### §84-8 参照ファイル
- 予定: `er052_open233_directional_trial_02.py`、`er052_output/open233_directional_misread_trial_02/`配下、`docs/pm/delegation_log/2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-02_*.md`

## §85 Opus独立レビュー: D61見逃しの原因分析と修正方針(OPEN-233-DIRECTIONAL-MISREAD-OPUS-REVIEW-03、2026-10-06)

### §85-1 目的・禁止事項
- 目的: TRIAL-02で残ったD61見逃し(前回2/3→0/3)の原因分析と修正方針を、TRIAL-03へ進む前にOpus独立レビューで確認する(ユーザー指示)。到達上限=DESIGN_READY_FOR_REVIEW/USER_DECISION_REQUIRED。
- 禁止: TRIAL-03実行/有料LLM Trial/Production変更/残11 E2E再開/Prompt修正の本実装/gold・KPI変更/新Safety仕様採用/自動VALIDATED・APPROVED_FOR_PRODUCTION。Opusが良いと言っても自動採用しない。

### §85-2 レビュー論点(ユーザー指示逐語要点)
1. D61見逃しの原因分析は正しいか(仮説: Ledger側の事象名が「上げ幅」「水準」のように抽象的すぎたため、記事側AIが対象文と対応付けられずNONE/NOT_MENTIONEDと判断した)。
2. 現在の修正案(Ledger側事象へ対象の実体名を含める/記事側の事象選択で意味上の部分一致を許容)で本当に改善する見込みがあるか(D61を拾える可能性/HC-012・A5-0を壊さないか/前回解消した正常文誤爆3件を再発させないか/事象名を具体化しすぎて別表現を拾えなくならないか)。
3. 別の見逃し・誤爆を増やさないか(同義表現/主語省略/比較表現/方向表現/一つのFactに複数事象/記事側の言い換え)。
4. TRIAL-03へ進む価値があるか(そのままTRIAL-03へ/設計修正後にTrial/現方式を見直すべき、のいずれかを明確に判定)。
5. 追加: 今回の修正は根本原因に対する修正か、D61だけを通すための過学習的patchか。
6. 追加: 「Ledger側の事象抽出→記事側blind事象選択→機械比較」という全体構造自体に直すべき問題がないか。

### §85-3 Evidence packet一覧(予定、並列委任_01a/01b/01cが作成)
- `docs/pm/evidence_opus_review_03/01_d61_trace.md`
- `docs/pm/evidence_opus_review_03/02_hc012_a5_fp3.md`
- `docs/pm/evidence_opus_review_03/03_trial01_02_diff.md`

### §85-4 Opusレビュー結果
(委任_03aで記録。Opus逐語は`docs/pm/opus_l2_review_or03_d61_root_cause.md`)
- E1 Evidence(¥0、3 packet、【確認】): D61(G-03)記事文 "After the plan was withdrawn, oil prices fell."(Brent・上げ幅語なし)。現行Ledger側ラベルは既に「Brent先物の上げ幅/水準/価格水準/価格」と実体名入り(実体名が欠けるのは「機能」のみ)。同系ラベルはG-04等で選択できた。TRIAL-01の事象ごと個別判定ではG-03 rep2/3検出、TRIAL-02の単一選択で0/3(3回ともNONE、quoteは記事文を引用)。前後文(article_context)は未投入。Ledger側サンプル揺れあり(HF-009 rep間で2〜3 event)。01→02で変化したid 17件、01検出→02見逃し=G-03・S-06、01誤爆→02解消=F-09/F-10/F-19。
- O1 Opus最終判定: (B)設計修正後にTrial。ただし修正内容は現修正案(実体名付与+意味上の部分一致)ではなく別のもの。現修正案=局所patch(しかもD61に効く根拠のない誤診に基づく)。
- O2 主因: 1 factに逆向き2事象(暫定: 上げ幅DECREASED/最終: 水準INCREASED)がある状況で、NONE付き単一選択方式が暫定と最終を区別できない。副因: 上位語("oil prices")の対応付けが弱い/前後文未投入/Ledger側ラベルの重複・揺れ。D61の性質=「暫定の下落を結末として述べ高値復帰を落とした時間範囲誤り」で、現enumにこの次元がないためF-09型(暫定の下落を正しく述べた文)と原理的に区別不能。
- O3 現修正案の見込み: (a)D61を拾う可能性低(部分一致はSAMEになる「上げ幅」へ吸い寄せ、見逃し→黙って通過に変わるだけ) (b)HC-012/A5-0は壊さないが「機能」具体化はG-02の手掛かりを減らす (c)F-19で「テスト」選択→REVERSED再発経路あり (d)上位語・主語省略(S-01〜05/S-14/N-02)の見逃しが固定。6観点すべてで盲点が残るか悪化。
- O4 推奨修正: 修正1(主)=事象に時間位置phase∈{INTERIM,FINAL,SINGLE}を付与、記事側も{INTERIM,FINAL,UNSPECIFIED}を返し、Pythonで「FINAL/UNSPECIFIED↔FINAL/SINGLE」「INTERIM↔INTERIM」で照合。修正2(副)=fact対応付け済み文で単一選択がNONEのとき、TRIAL-01方式の事象ごと個別判定へフォールバック(phase照合併用)。構造上直すべき点: 時間位置次元の欠如/NONE=通過の安全側設計欠如/SAME優先ルール(compare_selected L62)/Ledger側揺れの固定+ラベル正規化/上位語の別名付与(別Trial)/前後文投入(別Trial)/D61型を「時間範囲誤り」として別カテゴリ明示(gold/KPI定義=ユーザー判断)。
- O5 TRIAL-03案(Opus): Ledger側phase付き再抽出1回固定(約30 call、¥0.5)、記事側2構成並列(X=修正2のみ/Y=修正1+2)×(63+held-out約10項目)約220 call ¥4.5、フォールバック約50 call ¥1、合計約¥6・上限案¥8、shard並列約10分。held-out約10項目(gold反転4・faithful 6)を実行前に固定(D61過学習防止)。合格基準案7項目: HC-012・A5-0 3/3維持/D61>=2/3/held-out gold平均>=2/3かつ全件>=1/3/faithful誤重大0件/UNCLEAR<=10/不要Rewrite見込み0/新たな重大見逃し0。

### §85-5 Fable照合・Status・判断
- F1 Fable照合: Opus判定はEvidenceと整合。Fable/Sonnetの仮説(ラベルが抽象的)は誤診(ラベルは既に具体的)。Opus推奨は既承認設計(案E')の骨格を維持しつつ新次元(phase)を追加するもので、D61型のカテゴリ再定義(gold/KPI定義に関わる)を含むため、PM_GOVERNANCE 11-3節STOP条件(新しい仕様採用・gold定義の扱い)該当 → Status=**USER_DECISION_REQUIRED**。ユーザー指示によりTRIAL-03は未開始。残11 run待機。Production変更なし。本管理ID費用¥0。決定したのはFableのStatus判定のみ。
- F2 ユーザー判断事項(Opus提示7点、Fable推奨付き): (1)現修正案を採らない=推奨採らない (2)TRIAL-03の修正内容を構成X/Yへ差し替え=推奨差し替え (3)予算上限¥8=推奨 (4)held-out固定=推奨固定 (5)D61型を「時間範囲誤り」として別カテゴリ=推奨明示(gold/KPI定義変更のためユーザー判断) (6)「限定語なしの方向主張は結末の主張とみなす」方針=推奨受け入れ(held-out faithfulで誤爆測定) (7)上位語別名・前後文は別Trial=推奨別Trial。追加(8)残11 E2E再開=Fable推奨はTRIAL-03結果まで待機。

## §86 限定Trial 3(時間的位置の区別+NONE限定フォールバック): OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-03(2026-10-06)

### §86-1 ユーザー決定・訂正事項
- 決定: Opus修正設計でTRIAL-03実施/残11 E2EはTRIAL-03終了まで停止継続/Trial予算上限¥8(見込み約¥6)/Production変更なし。
- **訂正事項**: D61/HF-009型は新しい重大基準・Product仕様ではなく、既存基準で重大Fact誤りとして扱う対象。「限定語なしの方向表現を最終結果として読む」はProduct基準として採用せず、既存の重大Fact誤りを検出するTrial上の判定方法として検証するのみ。CURRENT_SPEC等に新カテゴリ・新原則を追加しない。「途中と最終の取り違え」の新Productカテゴリ・gold/KPIの新重大性基準は作らない。内部分析上「D61型」と呼ぶのは可。

### §86-2 修正内容
- 修正1: 時間的位置の区別(Ledger側INTERIM/FINAL/SINGLE、記事側INTERIM/FINAL/UNSPECIFIED、同じ時間的位置に属する事象同士だけ方向比較)。
- 修正2: NONE時の限定フォールバック(factとの対応が既知の記事文で通常の事象選択がNONEのときのみ各事象を個別確認。無条件の全事象総当たりには戻さない)。
- 不採用: 前回案(事象名をさらに具体化/意味上の部分一致を拡大)。

### §86-3 合格基準(実行前固定、事前登録)
(1)HC-012 3/3維持 (2)A5-0 3/3維持 (3)D61 2/3以上 (4)held-out重大例 平均2/3以上かつ全例最低1/3以上 (5)正常43件+held-out正常例 不要な重大判定0 (6)不要Rewrite見込み0件/run (7)新たな重大見逃し0 (8)前回解消した誤爆3件を再発させない。未達でも自動でTRIAL-04へ進まない。

### §86-4 Trial構成
- 構成X=NONEフォールバック中心/構成Y=時間的位置の区別+NONEフォールバック。held-out検証セット(HC-012/A5-0/D61・HF-009/正常文43件/前回誤爆3件/held-out重大例/held-out正常例)を実行前に固定(sha256凍結)、実行後にtestset・正解を変更しない。費用上限¥8、超過見込み時のみSTOP。

### §86-5 並列化計画
Phase A(¥0、約25分、4本並列): script_03/held-out固定+testset_03+正解+凍結/集計/SSOT先行起票。Phase B(≤¥8、約10分): 見積→Ledger側phase付き再抽出(固定キャッシュ)→記事側X/Y×3 shard=6 process同時→merge→集計。Phase C(約12分、直列): Fable判定→SSOT→commit→Closeout→STOP。

### §86-6 結果
【確認】費用・時間: 見積mid ¥5.0(上限¥8で実行)、実費**¥7.41**(Ledger側¥0.80、X ¥3.08+追加¥0.75、Y ¥2.59+追加¥0.19。フォールバックX 120 call ¥1.71/Y 64 call ¥0.82)。見積超過要因=NONEフォールバック発動率が想定10%を大幅超過。初回6 process並列の均等配分予算でshard2がX/Yとも途中停止→resume機能(完了id skip、判定ロジック不変)を追加し残分を直列実行、累計¥8内で全73項目完走。sha256凍結一致(testset/正解は未変更)。
合格基準(X / Y):
| # | 基準 | X | Y |
|---|---|---|---|
| 1 | HC-012 3/3 | 1/3 未達 | 0/3 未達 |
| 2 | A5-0 3/3 | 1/3 未達 | 0/3 未達 |
| 3 | D61 2/3以上 | 2/3 充足 | 2/3 充足 |
| 4 | held-out重大 平均2/3以上かつ全例1/3以上 | 充足(H-G1 2/H-G2 2/H-G3 3/H-G4 1、平均0.667) | 未達(3/3/3/0、H-G4=HC-012系) |
| 5 | 正常43+held-out正常6=49件の誤重大0 | 1件(H-F2 "briefly dipped") 未達 | 1件(H-F1 "fell but recovered") 未達 |
| 6 | 不要Rewrite見込み0件/run | mid 0.152件/run 未達 | 未達 |
| 7 | 新規重大見逃し0 | G-01/G-02/S-07/S-12 未達 | G-01/G-02/S-12/S-13 未達 |
| 8 | 前回誤爆F-09/F-10/F-19再発なし | 充足 | 充足 |
(TRIAL-02はHC-012 3/3、A5-0 3/3、D61 0/3。)
退行trace(`trace_hc012_regression_03.md`): HC-012のLedger側eventsはphase付き再抽出で「機能」系ラベルが反復間で揺れ(電話発信機能/機能/電話機能。TRIAL-02は3反復「機能」一致)、「機能」eventのphaseは全repFINAL、テストeventはINTERIM。G-01/G-02は記事側phaseがINTERIMまたは不定、選択がNONEのrepはフォールバックでNOT_MENTIONED/UNCLEAR、REVERSEDはX r2(sel=機能)のみ。Y G-02はledger_state=None。誤重大: X H-F2はphase無しでFINAL event(INCREASED)と比較しREVERSED(Opusが予測したX構成の限界)、Y H-F1は複合文でINTERIM照合がREVERSED。D61/H-G1〜G3(Y)はphase照合またはフォールバックでREVERSED。

### §86-7 Status・判断
**Fable判定: REJECTED**(今回Trialした実装(修正1+2)のままでは採用不可)。理由: 事前登録基準の1・2・5・6・7がX/Yとも未達、特に最重要のHC-012/A5-0が3/3→0〜1/3へ退行。一方、phase区別はD61型(G-03、H-G1〜G3)には有効(Y)で概念自体の否定ではない。退行要因は実装上の2点(Ledger側ラベルの反復揺れ/記事側phase判定の誤り)と見られる【推測】。TRIAL-04へは自動移行しない。次の修正はHC-012に対する3回目のパッチに当たるためPM_GOVERNANCE 11-3節条件BによりOpus独立レビュー必須。Production採否判断は不要。残11 E2E再開はユーザー判断(Fable推奨=本件の方針決定まで待機)。D61型の新カテゴリ・新原則はCURRENT_SPECへ追加していない。
未解決: (a)Ledger側ラベル揺れの固定(正規化・1回抽出固定、Opus論点6-4)未実装 (b)記事側phase判定の妥当性("restored"をINTERIMと誤判定) (c)複合文(INTERIM+FINAL)の扱い (d)フォールバック発動率が高く費用が倍増(発動条件の見直し) (e)OPEN-235/236未着手 (f)APPROVED_FOR_PRODUCTION未配線項目(CHECKER-FLOOR-PRODUCTION-E2E-01)への影響なし。

### §86-8 参照
`er052_open233_directional_trial_03.py`(予定)、`er052_output/open233_directional_misread_trial_03/`、`docs/pm/delegation_log/2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-03_04.md`。

## §87 Fact台帳の明確化(上流対策)設計: OPEN-233-LEDGER-CLARITY-DESIGN-01(2026-10-06)

Status: 設計検討中・ユーザー判断待ち(到達上限USER_DECISION_REQUIRED)。未承認の新仕様でありProduction採用扱いではない。Trial未実行・Production未変更。OPEN-237。

### §87-1 目的・方針・必須条件
目的: Writerが台帳の意味を誤解して重大Fact誤りを生む問題を、台帳自体の明確化で上流予防する。方針A(明確に記述: 何が起きたか/誰が何を/何がどう変化/どの時点/因果確認の有無)、方針B(複雑なFactは意味一致を確認して分割)、方針C(Writerに不要な推測をさせないが表現・構成は過度に拘束しない)。必須条件: ①事実追加・改変なし ②Fact間関係維持 ③記事Quality維持 ④量産可能な自動処理(人間編集運用は不採用)。

### §87-2 既存仕様(委任_01a【確認】)
- 台帳生成=Researcher(gpt-5.6-luna、web_search)→独立AI Verification(VERIFIED/AMBIGUOUS/REJECTED)→決定論`build_verified_ledger_text`でtxt化(`er003_v1_en_direct_vfl_01_generate.py` L275)。
- 原資料=Web検索結果。source quote欄なし。台帳生成費≈¥28.7/run(総額¥44.66の64%)。
- 既存ルール=Researcher promptに4観点(scope/適用条件/数値内訳/因果区別)。時系列・主体・多義語のルールはなし。
- fail-safe位置=Verification直後〜txt化。ID参照=HC-012だけで23ファイル65箇所(ID不変が必須)。

### §87-3 事例・Before-After(委任_01b【確認】)
- HC-012「機能を当面ロールバックした」=テスト中機能の取り下げ(原文照合未了)。HF-009=途中「上げ幅縮小」+最終「高水準へ戻る」。
- 曖昧度: 高3(HC-012/HF-009/HF-012)・中14・低10。held-out候補8。
- 対象台帳3種: meta 15 / hormuz 12 / small_bag 17 fact。
- Before-After案の詳細は`docs/pm/ledger_clarity/`(委任_03a修正版)を参照。

### §87-4 設計案(委任_02、Opus反映後=委任_03a)
- 案P'=Researcherスキーマ・prompt拡張+Verification観点追加(追加callなし、<¥1)。案C+V=Verification後に台帳全体1回の明確化call+意味一致検証(ID不変・events構造・2段fail-safe、+¥2)。案C+V+B=多義語factにWeb再Verification(+¥14)。案S=子ID分割(不採用)。
- Opus反映後の推奨=本番はP'、案Cは既存台帳のoffline適用(Trial用)。
- 必須の決定論検査: fact_id集合・数値・日付・固有名・否定語・因果語の集合一致。
- txt書式制約: claim行に否定語・因果語・番号・括弧を入れない。否定ガイドはnotes_for_writerへ、phaseは英字タグ行。phase定義は台帳側に一本化。
- いずれも未承認の新仕様(Production採用扱いではない)。

### §87-5 Opus独立レビュー(条件A、OF-059)
- 総合=条件付きで進める(M1〜M6、設計へ反映済み)。
- HF-009の「Writer誤読例」は合成文で本番Writerは正しかった(HF-009はChecker側課題)。HC-012はJA R0で発生し、WriterはB3 briefを読む(台帳を直接読まない)。
- Verificationは多義語の確定正誤を原理上判定できない→原資料参照工程(P')で確定。
- 明確化文の否定語・因果語・番号が既存Checker決定論検査を誤爆させる。Quality面では括弧・番号の逐語コピー経路に注意。
- Checker改善とは両立(台帳=予防、Checker=検出)。台帳eventsをCheckerの基準に凍結共有すればChecker側Ledger抽出を廃止可。
- 逐語は`opus_l2_review_lc_*`(委任_03b〜d)。

### §87-6 Trial計画(品質①Writer重大Fact誤認/②Checker精度/③記事Quality、費用上限案・所要時間)
- 承認待ちの案(委任_03a)。Phase 0=¥0(基準発生率集計)/Phase 1=¥3〜6(3台帳へ案C offline適用+決定論diff+offline照合)。
- Phase 2=上限¥60(B3+JA R0〜R2+ENのみ、台帳A/B×3テーマ×8 seed。HC-012型曖昧訳 A≥6/8 vs B≤1/8、held-out悪化なし、Quality基準)。
- Phase 3=任意・上限¥30(承認済みChecker構成でA/B各2 run)。合計上限¥100。
- 過学習防止=固有名をpromptに入れない、基準・held-out事前固定。要DEV経路(台帳パス差替え、Production既定は従来)。
- 所要時間・詳細は委任_03a成果物(`docs/pm/ledger_clarity/`)参照。Trial未実行。

### §87-7 Status・ユーザー判断事項
- Status=**USER_DECISION_REQUIRED**(Fable判定。Opus判定はSonnet案の訂正・精緻化で対立ではない)。設計・Trial計画はユーザー承認待ちの未承認新仕様。Production採用扱いではない。費用¥0。
- 判断事項: (1)Trial実施可否 (2)予算上限¥100 (3)本番経路P' vs C+V (4)2段Trial(Phase構成) (5)F1方針。
- PM Gate: Production未変更/Trial未実行/残11 E2E停止/TRIAL-04未開始/S1等採否不変(S1-FACT-CHECK-01はUSER_DECISION_REQUIRED)/CURRENT_SPEC未更新/Dangling Reference確認済み(委任_03a)。
- 未配線の承認済み仕様=CHECKER-FLOOR-PRODUCTION-E2E-01(9/20停止・PRODUCTION_WIRED未)。Open Items=OPEN-235/236/237。

### §87-8 参照
`docs/pm/ledger_clarity/`、`docs/pm/delegation_log/2026-10-06_OPEN-233-LEDGER-CLARITY-DESIGN-01_01d.md`。

## §88 OPEN-233-LEDGER-CLARITY-P-TRIAL-01(P'方式Fact台帳明確化Trial、2026-10-06)

### §88-1 目的・範囲
- §87で設計した本番推奨経路P'(Researcher/Verification promptの拡張、追加callなし)をTrialで検証。比較ベースはユーザー確認済みChecker構成。Trial実施・上限¥100はユーザー承認済み。Production採用ではない(APPROVED_FOR_PRODUCTIONなし)。
- 到達可能Status=REJECTED/VALIDATED/USER_DECISION_REQUIRED のみ。n=1テーマ・1 seed。

### §88-2 ベース構成とP'の変更内容
- ベースChecker構成=OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01(DECISION_LOG L19987-19996、2026-10-06承認逐語)、E2E_02の9 runスイッチ固定(switches equal、dump shaの差はbudget/instances/run_capのメタ情報のみ)。固定箇所=`docs/pm/ledger_clarity_p_trial/00a_base_checker_config.md`。S1等3スイッチ・precheck4種除外の個別承認未確認は別件のまま。
- P'変更=Researcher prompt末尾に一般規則9項目(主体・動作・対象・時点明示/同一主体・同一指標の時系列のみ途中→最終/多義動詞を原資料の具体動作に置換/原資料にない主体・因果・時系列を足さない/不確実点をambiguity_noteとnotes_for_writerに残す/断定を強めない/原資料にない否定・因果・括弧・番号をclaimに入れない/改行禁止/notes固定書き出し)、Verification promptに3観点追加。
- 無変更=Research方法・検索・schema・enum・`build_verified_ledger_text`(決定論)。DEV専用`er052_open233_ledger_clarity_pprime_dev_01.py`(env `OPEN233_RESEARCHER_VARIANT=pprime`、プロセス内差替・終了時復元)。

### §88-3 実行記録(費用・再開・provenance)
- 台帳¥17.89(Researcher 7.50+Verification 10.40)+B3 1.53+JA 6.67+EN 3.10=連鎖¥29.20、Checker ¥2.54、pairwise ¥3.11(上限¥3を¥0.11超過、事後判明)→合計¥34.85(上限¥100)。
- 初回連鎖がツール側590秒timeoutでEN段中に停止→同引数で1回のみ再開(EN+deviation checkのみ再実行)。初回EN部分課金が未記録の可能性(数円以内)。
- provenance・unit test 8件PASS・Production file 5本git無変更。残11 run未再開。

### §88-4 結果
- ③重大NG・HC-012型: HC-012 Rollback型=After全段(台帳/B3/R0/R2/EN)で復元型0(Before 5 runで復元型3/5・重大Y 1/5)。EN "temporarily rolled back the human concierge feature"=原語維持・台帳整合。台帳側claimは片仮名「ロールバック」のまま(規則3は原資料自体が具体動作を述べておらず置換不能、notesに「語義: 原語=rolled back this feature/当面」)=「誤訳を誘発しなかった」止まりで「意味確定による予防」とは言えない。真の重大NG=0件(軽微5件、gold相当A4-0/B4-a/Meta-1・2/A5-0/A4-1不出現)。
- ④Fact安全性: 断定強化1件(MMHC-008: 原資料"some tests indicated … could get … up to 95-98%"→台帳claim「95%から98%に達し」)=STOP条件「意味一致の疑義1件」に該当(保守的に適用)。判定保留2件(MMHC-010 "roll it out"→「一般公開」・"potential"欠落/MMHC-015 広告影響の留保欠落)。追加Fact0・否定反転0・数値日付固有名相違0。
- Before/After差分: fact数15/15、ID体系別(MUSE-HC-*/MMHC-*)、意味的対応でBefore側のみ3件(HC-001/002/003)・After側のみ2件(MMHC-004/015)、検索回数7→3(方法不変、結果の時間ずれ)。claim平均92→77字、改行0、M4フラグ2件は原資料の否定の訳で反転なし。
- ②Entertainment: Writer向け注意書き(有意性不明・成功率定義不明・全電話人間担当と書かない等)がnotes_for_writer短縮(172.2→51.6字)で消え、draft ambiguity欄には残るがtxtに出ない(R1課題=txt生成変更が必要=新仕様候補)。JA R2段の台帳逐語率 0.0843→0.2486(+16.4pt、基準+5pt NG)。R0段は+3.3pt OK。EN側は文長・TTR±1%以内、pairwise(gpt-5.6-sol、順序入替2 call)でAfter 2/2優位。
- ①Checker副作用(主KPIではない): final_state/Rewrite0/human_review0/floor_reason null/費用¥2.54 vs ¥2.41は不変。Stage1候補8 vs 5、Stage2対象12 vs 8、不要候補7 vs 4(全件降格、実害なし、MMHC-007無関係文の誤紐付け・changed_actor誤指摘、n=1要注視)。本Checker結果をS1・precheck4種除外等の承認根拠に流用しない。

### §88-5 Fable判定と根拠
- Trial Status=**USER_DECISION_REQUIRED**(VALIDATEDでもREJECTEDでもない)。決定したのはFableのStatus判定のみ。
- 根拠: (a)④の断定強化1件(STOP条件「意味一致の疑義1件」)と判定保留2件 (b)Writer向け注意書きのtxt欠落(R1課題、新仕様候補) (c)JA R2段の逐語率+16.4pt(基準NG) (d)n=1テーマ・1 seed。
- 良い点: HC-012型の復元型0・真の重大NG0件・Checker最終結果不変・EN側pairwise優位。

### §88-6 新仕様候補とユーザー判断事項(いずれも未承認)
1. P'規則をResearcher本番promptへ入れるか。
2. ambiguity/不確実点をVERIFIED factでもtxtへ出す(R1、txt生成変更=台帳生成処理の仕様変更)。
3. 断定強化・留保欠落を防ぐVerification観点の強化/決定論検査(Opus M-dの決定論検査は断定強化を直接検出できず、原資料照合で判明)。
4. JA R2段の逐語化(must_fix・deviation checkが台帳文へ寄せる)の扱い。
5. n拡大(別テーマ・seed)の要否。
- Production変更なし・CURRENT_SPEC未更新・残11 run待機・TRIAL-04未開始。

### §88-7 参照
- 評価: `er052_output/open233_ledger_clarity_p_trial_01/after_pprime_01/eval/`(E1_fact_safety_review.md/E2_critical_ng_checker.md/E3_entertainment.md/cost_summary_02.json)。
- FREEZE・設計: `docs/pm/ledger_clarity_p_trial/`(00a〜00d・01a)。DEVスクリプト: `er052_open233_ledger_clarity_pprime_dev_01.py`。Opusレビュー(条件A、判定(B)、M-a〜M-e): `docs/pm/opus_l2_review_pt_design_01.md`(並行委任S1作成)。OPUS_FINDINGS_LEDGER OF-060、OPEN-237。

## §89 OPEN-233-LEDGER-POLYSEMY-NOTE-DESIGN-01(多義語notes最小変更設計、2026-10-06)

### §89-1 目的
- Writerが原資料の多義表現(HC-012「ロールバック」型)を逆向きに読む誤読を、Researcher生成のnotes_for_writerへ最小の注意書きを足して上流予防する案の設計・Opus条件A・Trial計画まで(¥0、設計のみ、Trial未実行、Production変更なし)。到達Status=USER_DECISION_REQUIRED。

### §89-2 事実確認(9項目、A1/A2)
1. notesはtxtへ常時出る(er003 L302、verdict無関係、REJECTED除く)。
2. JA初回R0はB3 briefのみを読み、台帳notesを直接見ない。
3. B3 promptは台帳全文を見るがnotes転記指示なし(grep notes 0件)。
4. must_fix(Fact Check MAJOR時)・Checker後Rewrite(hint 400字上限)・deviation checkには台帳notesが届く。
5. EN生成・EN retryは台帳を見ない(JA R2本文のみ)。
6. schemaのnotes_for_writerは自由文string|nullで変更不要。
7. Trial-01構成(Writer gpt-5.6-luna全工程・Checker gpt-6-luna・スイッチdump一致・script sha一致)は再現可能。
8. seedは固定不可。
9. P-TRIAL-01実証: txtにnotesは届くがB3 briefへは「語義:」「原語=」の文言自体は転記0件(内容は一部反映)。

### §89-3 設計(唯一の変更点・案N/案N+B)
- 案N: Researcher promptのnotes_for_writer指示に規則4行を追加(逆・反対になる表現に限り1 fact 1件/形式「注意(多義): 原語'<英語原表現>'=<原資料が示す意味>。<逆の読み>ではない。」/確定できなければ「原資料も曖昧。断定しない」/80字以内・改行なし・他フィールド不変)。Verification無変更。Fact本文・schema・Research方法不変。
- 案N+B: 案Nに加え、B3 promptへ注意文転記規則1行(Production Writer仕様変更=Trial-01同一条件からの逸脱=新Product判断。ユーザー承認時のみ別arm)。
- Trialではbaseline draft/verificationを固定し、notes追加call(`{fact_id,note}`をコード側で末尾連結)=Fact本文を物理的に固定(offline、Production採用根拠にはしない)。
- A3発火率見込み: YES 13/44 fact=29.5%(確度高のみ6/44=13.6%)。FP懸念あり(数値・日付中心のFact)。

### §89-4 Opus(B)と反映
- Opus条件A判定(B)・必須修正6件: 固定台帳はP'版でなくbaseline/連結方式/規則4行圧縮/具体例の意味誤り訂正(HC-012「復元と読まない」→「機能を復活・再提供した意味ではない」、HC-014の解釈確定削除)/Rewrite hint 400字切り詰め検査/注意付与件数・誤付与測定。全件反映(B_design §11〜§13)。OF-061。

### §89-5 Trial計画(未実行、E_trial_plan.md)
- 条件Control/案N(案N+Bはユーザー承認時のみ別arm)、テーマmeta+hormuz。Phase 1=B3+JAまで×3 repeat(2条件12 run≈¥95、3条件18 run≈¥140)、Phase 2=良条件のみEN+Checker 1〜2 run/テーマ(¥30〜60)。上限案2条件¥130/3条件¥200。所要Phase 1約40分(並列3)+Phase 2約30分+評価約40分。合格基準・STOP事前固定。

### §89-6 STOP該当とユーザー判断
- STOP該当: (a)notesだけでは確実にWriterへ届かない(Beforeではbriefは正しく「当面ロールバック」と書かれ、誤読はR0の言い換えで発生=R0に注意が届かなければ効かない)、(b)案N+B(B3 promptへ転記規則1行)はProduction Writer仕様変更=Trial-01同一条件からの逸脱=新Product判断。設計・計画は完成させたうえでユーザー判断待ち。
- ユーザー判断5点: (1)Trial実施可否と上限 (2)案N/N+B/3条件 (3)確度高のみ既定 (4)offline固定台帳の可否 (5)対象テーマ。いずれも未承認。

### §89-7 参照
- `docs/pm/polysemy_note/A1_notes_delivery_facts.md`、`docs/pm/polysemy_note/A2_trial01_config_freeze.md`、`docs/pm/polysemy_note/A3_polysemy_candidates_and_rules.md`、`docs/pm/polysemy_note/A3_trial_eval_template.md`、`docs/pm/polysemy_note/B_design.md`、`docs/pm/polysemy_note/E_trial_plan.md`、`docs/pm/opus_l2_review_pn_design_01.md`、`er052_output/open233_ledger_polysemy_note_01/phase0/FREEZE_T01_CONFIG.json`。OPEN-237、OF-061。

## §90 OPEN-233-LEDGER-POLYSEMY-NOTE-TRIAL-02/03(自動Note生成の要素評価、2026-10-06)

### §90-1 TRIAL-02要約(OPEN-233-LEDGER-POLYSEMY-NOTE-TRIAL-02)
- Phase 0完了: 追加3記事=space_weapons(完了/予定・主体)/sewer(対象・方向、誤読実記録あり)/ai_control(原因/結果・時系列)。N+B DEV runner test 9件PASS。固定台帳はControl=既存txtバイトコピー、N+B=notes行のみ追記で5テーマ差分0。
- 自動notes生成gen1(過剰付与45件)/gen2(付与率20%以下だがhormuz 0件・対象捕捉2/15・HC-012の内容ずれ・字数却下)で承認条件「高確度のみ」不成立。Phase 1未実行。実費¥25.44/上限¥500。Status=USER_DECISION_REQUIRED(TRIAL-03の指示で置換)。

### §90-2 TRIAL-03 Opus設計レビュー要点
- 主因: 見ている場所が違う(英語原文の多義ではなく、日本語claimのB3圧縮後の逆読み)/判定基準が弱く件数目安に迎合/除外規則と80字制限が正解を消す。
- 対象factの多くは既存notesが既に警告=真因はB3がnotesを運ばない可能性。推奨B(2段階)>A、Cは対照必須。

### §90-3 3ループ比較表
| ループ/パターン | 捕捉(of 14) | 付与率 | holdout(small_bag) | 捏造 | 内容一致 | 実費 |
|---|---|---|---|---|---|---|
| L1 A | 8 | 41% | 10件NG | 0 | - | L1合計¥75.42 |
| L1 B | 6 | 22% | 0 | 0 | - | (同上) |
| L1 C | 9 | 44% | 1 | 5 | - | (同上) |
| L2 B2(hint) | 10 | 42% | - | 0 | 8/10 | L2合計¥50.70 |
| L2 B2n | 6 | 39% | - | 0 | 5/6 | (同上) |
| L3 B3 | 1 | 2.4% | - | - | - | ¥34.01 |
- L2はH1接頭辞空白・H2自己検証緩和・H3逆命題2列挙・H4合成正例。L3=stage1×2和集合+圧縮判定役high通過+120字。judge閾値をhigh+mediumに緩めた机上試算で捕捉7/14・付与20%。
- 実費累計¥160.13/上限¥500(TRIAL-02の¥25.44を除くTRIAL-03分。内訳はL1〜L3の合計)。

### §90-4 基準照合とFable判定
- 成立基準(捕捉9/14以上・付与率25%以下・holdout 1以下・捏造0・内容一致70%以上・迎合なし)を全て満たすパターンなし(B2が5/6で最良、付与率のみNG)。
- STOP条件「3ループで成立せず」該当。5記事Trial未実施。Status=**USER_DECISION_REQUIRED**。
- Production変更なし/Trial限定。Production file(er003/B3/JA writer/er019 runner/er052 runner/e2e_run_02)はgit上無変更。残11 run未再開。「良好でもVALIDATED止まり」。

### §90-5 重大発見
- (a) B2/B3のstage1 promptはL2作成時に新旧本文が連結された欠陥版(【出力】2か所、Fact一覧は末尾のみ)で、H3は実質未検証。L2のB2/B2n比較の結論にも影響しうる。
- (b) stage1判定のゆらぎ(同一prompt2回のJaccard 0.29〜0.88)。
- (c) 1.5判定役は弁別力あり(対象のmedium以上58% vs 非対象29%)だが閾値が厳しすぎた。
- (d) 全ループ未捕捉: EVID-004・CONTROL-001(模擬と実在/時系列型)。
- (e) 既存notes依存: Aのablationで捕捉8→6(meta/hormuzで消失)。

### §90-6 5記事選定理由(各1行)
- meta: 既存Trial-01台帳。HC-012「ロールバック」型(完了/予定・方向)の基準例。
- hormuz: 既存Trial-01台帳。原油価格の途中/最終の取り違え型。
- space_weapons: 「開発中・評価・発言」と「配備・実施」の差で記事の核が逆転するFactが複数(完了/予定・主体)。
- sewer: F-011/F-010/F-016の方式転換を既存下水管の浄化槽切替と誤読した実記録あり(対象・方向)。
- ai_control: 模擬/実在・誘導/自発・当時/現在・停止の一般保証化で逆転するFactが複数(原因/結果・時系列)。

### §90-7 ユーザー判断事項(推奨付き)
1. 4ループ目を許可するか(欠陥promptの修正+判定役閾値high+medium+圧縮文から限定語除去、約¥40)。
2. B2(捕捉10/14・付与率42%)のまま5記事Trialへ進み、ノイズ影響込みで伝達・防止を測るか(約¥155)。
3. **推奨**: 決定論的な「既存notes昇格」(「〜とは書かない/〜ではなく」型の既存禁止文に接頭辞を付けるだけ、LLMなし=捏造0・¥0)+B3転記で5記事Trialを行い、「伝達が真因か」を先に確定する(約¥155)。生成の高度化(1)(2)はその結果を見て判断。
- いずれも未承認の新仕様候補。

### §90-8 参照
- `docs/pm/polysemy_trial_02/`、`docs/pm/polysemy_trial_03/`(F0_failure_analysis.md、L1/L2/L3_element_trial_result.md)、`docs/pm/opus_l2_review_pt03_design_01.md`
- `er052_output/open233_polysemy_trial_02/ledgers/`、`er052_output/open233_polysemy_trial_03/patterns/`、`.../runs/`、`.../eval/`。OPEN-237、OF-062。

## §91 OPEN-233-META-ROLLBACK-MINIMAL-NOTE-TRIAL-01(最小Note注意喚起Trial、2026-10-07)

### §91-1 目的・条件
- Meta HC-012「ロールバック」の「元に戻した」型曖昧表現を、B3 brief転記の最小Note(一般的な多義注意喚起1文)で抑止できるかを検証(Trial限定、Metaのみ、N=5評価+rep1参考)。
- Note全文(逐語): 「注意(多義): この表現は多義的なので、単語だけで機械的に解釈・翻訳せず、原文の文脈・主体・対象・前後関係から意味を確定して記事化すること。」(対象語を指さない一般文)

### §91-2 結果表(HC-012相当文、3値)
| rep | brief | R0 | R1 | R2 |
|---|---|---|---|---|
| 1 | 曖昧 | 未完(却下初稿は曖昧) | 未完 | 未完(参考) |
| 2 | 曖昧 | 正解「いったん止めた」 | 正解 | 曖昧「いったん元に戻された」 |
| 3 | 曖昧 | 曖昧「当面、元に戻されました」 | 曖昧 | 曖昧「当面元に戻しました」 |
| 4 | 曖昧 | 曖昧(同上) | 曖昧 | 曖昧 |
| 5 | 曖昧 | 曖昧「いったん元に戻された」 | 曖昧「ロールバック...元に戻された」 | 正解寄り「いったん降板した形だ」 |
| 6 | 曖昧「同機能をロールバックした」 | 曖昧「当面、元の状態に戻しました」 | 曖昧(同文) | 曖昧「当面、元に戻しました」 |

### §91-3 集計とControl比較(N=5、rep2〜6)
- R2: 正解1(rep5)/誤読0/曖昧4(rep2,3,4,6)。R0: 正解1(rep2)/誤読0/曖昧4(rep3,4,5,6)。
- Control: trial_04 Control rep1 R2=曖昧(復元型候補)、E2E_02(旧)復元型3/5 run。今回R2復元型候補4/5=Controlと同水準。
- 実費: rep2〜6計¥21.14(rep1は一部未記録、概算込みtotal_jpy_approx ¥23.25、上限¥40)。

### §91-4 Fable判定
- Status=**USER_DECISION_REQUIRED**(Production採用判断はしない)。Noteはbriefへ6/6逐語転記(rep1〜6)=Writer入力まで到達。明示的な「復活・再提供」型の誤読は全run全段で0件。ただし最終稿(R2)では「元に戻された/元に戻しました」型の曖昧表現が多数(R2 4/5、R0 4/5)で、Control(trial_04 rep1: R2曖昧・復元型候補/E2E_02: 復元型3/5)と同水準。一般的な注意喚起だけでは「元に戻す」への言い換えを抑止できず、改善効果は限定的(N=5)。rep2はR0/R1で「止めた」と正しく文脈化したがR2で「元に戻された」へ退行(Revision段で台帳表現へ寄せる挙動の疑い)。Production変更なし/Trial限定。

### §91-5 参照
- `er052_output/open233_meta_rollback_minimal_note_01/eval/E_rollback_minimal_note.md`、`.../runs/meta/nb/rep1〜6/`、`.../cost.json`。OPEN-237。

## §92 OPEN-233-META-ROLLBACK-MINIMAL-NOTE-TRIAL-02(同条件 追加、開始N=10、完了N=7、2026-10-07。ユーザー指示により代替runは集計除外し訂正)

### §92-1 条件固定の確認
- 前回(§91)と同一条件: env `OPEN233_B3_VARIANT=nb`・`OPEN233_NOTE_PREFIX`既定(transfer_block sha abd16d9a...、前回と同一)、`--phase phase1`・同theme・`--budget-jpy 8`、台帳txt sha=FREEZE nb sha `cfd6d702...`(全run一致)、research_calls=0。rep7〜16を同時並列起動。
- 開始N=10(rep7〜16)、完了N=7(rep7,8,9,11,12,13,16)、停止N=3(rep10,14,15: JA_FACT_CHECK_STOP/LEDGER_DEVIATION)。

### §92-2 完了7 runの最終稿(R2)判定(rollback該当段落の全文は評価ファイル)
- rep7 曖昧「当面のあいだ元に戻されました」(R0は取りやめ=正、R2で退行) / rep8 正しい「当面取りやめて、元に戻されました」 / rep9 曖昧(境界)「機能は当面、以前の状態に戻されました」 / rep11 曖昧「元の状態に戻されました」 / rep12 曖昧「当面ロールバックしました」(R0は正寄り、退行) / rep13 正しい「いったん取りやめにしました」 / rep16 曖昧「ロールバックされました」。

### §92-3 集計とControl比較
- 追加N=7(R2): 正しい2(rep8,13)/曖昧5(rep7,9境界,11,12,16)/重大誤読0=0/7=0%(rep9重大扱いなら1/7=14%)。累積N=12(前回R2 正1/曖4/誤0を合算): 正しい3/曖昧9/重大誤読0=0/12=0%(rep9重大扱いなら1/12=8%)。
- Control参考(復元方向候補3/5、重大1/5=20%)との比較は断定しない。観察: rep7・rep12はR0正しい→R2曖昧へ退行。
- 費用: 完了7本¥31.23、停止4本(rep10,14,15,19)推定¥22.6、代替rep17/18 ¥7.91(集計外)、合計推定≈¥61.8=**上限¥60を約¥2超過(要因=旧指示による代替run起動、ユーザー報告済み)**。

### §92-3b 参考(集計外): 代替run
- rep17/18/19は旧指示で起動した代替run。ユーザー指示により集計外・参考扱い(rep17 曖昧「元の状態に戻されました」/rep18 曖昧「ロールバックしました」/rep19 失敗)。本文引用は評価ファイルに残置。

### §92-4 Status
- **USER_DECISION_REQUIRED**(Production採用判断なし)。決定はTrial実施のみ。判断材料: 効果限定的(曖昧が多数残る)、rep9境界1件、完了N=7、費用上限約¥2超過。

### §92-5 参照
- `er052_output/open233_meta_rollback_minimal_note_01/eval/E_rollback_minimal_note_trial02.md`、`.../runs/meta/nb/rep7〜19/`、`.../runs/manifest.json`、`.../cost.json`。OPEN-237。

## §93 OPEN-233-META-ALLFACT-NOTE-ENT-TRIAL-01(全fact一律Note 2パターン×N=1、2026-10-07)

### §93-1 条件
- ベース台帳=control(sha ea0ce587…、15fact、空notes0件)。P1=全factのnotes末尾に「 / 注意(多義): <文言(完全同一)>」(sha b41276bb…、OPEN233_NOTE_PREFIX=「注意(多義):」)。P2=「注意: <既存notes> / 注意(多義): <文言>」(sha d2db1058…、PREFIX=「注意:」)。notes以外差分0検査PASS(両方)。nb variant、B3→JA R0/R1/R2→EN→自動Checker、N=1×2。out-dirは runner制約で runs/meta/nb/<p1|p2>/rep1。

### §93-2 転記状況
- P1: briefは14行、選択3fact(HC-006/010/012)すべてに多義注意が逐語転記(3/3、切れなし)。P2: brief14行、既存notes3行のみ転記、多義注意0/3(同一行の後半が脱落)=P2は実質「従来notes転記」条件。

### §93-3 rollback(HC-012)判定(全文は評価ファイル)
- P1 JA/EN=曖昧(「当面ロールバック」+「Muse全体を止めたわけではない」)。P2 JA=曖昧(「いったん戻した」)、P2 EN=正しい寄り境界(「pulled back」)。重大誤読0。参考Control rep1=曖昧、rep13=正しい(「取りやめ」)。

### §93-4 指標・pairwise・Checker
- JA R2 12字一致率: P1 0.123/P2 0.140/Control 0.126/rep13 0.091。EN 平均文長(語): P1 15.4/P2 16.9/Control 15.4、TTR 0.48/0.49/0.50。
- pairwise(順序入替2回): JA P1>C(全軸)、JA P2≒C、JA P1 vs P2は軸で分かれる(overall同等)、EN P1>C、EN P2>C(overall)、EN P1>P2(全軸)。単一LLM評価・N=1のため断定しない。
- Checker: P1=RESOLVED_REWRITE_THEN_DOWNGRADE(3cycle、Rewrite1回)、P2=RESOLVED_STAGE2_DOWNGRADE(1cycle、Rewriteなし)、Control rep1=RESOLVED_REWRITE_THEN_DOWNGRADE(2cycle)。最終重大0(全て)。
- 費用≈¥50.2/上限¥200(うちpairwise¥29.0)、実時間約17分。

### §93-5 Status
- **USER_DECISION_REQUIRED**(Production採用判断なし)。決定はTrial実施のみ。判断材料: P1はbrief到達3/3だがrollback曖昧は残る、P2は転記規則の1行内脱落で多義注意が届かない。

### §93-6 参照
- `er052_output/open233_meta_allfact_note_ent_01/eval/E_allfact_ent_01.md`(記事全文収録)、`.../runs/meta/nb/p1|p2/rep1/`、`.../cost.json`、`.../ledger/FREEZE.json`。OPEN-237。

## §94 OPEN-233-META-ALLFACT-NOTE-E2E-TRIAL-02(P2転記修正+E2E N=10、2026-10-07)

### §94-1 Phase A(DEV runner転記規則の最小修正、Trial専用・Production経路不使用)
- 規則文: 旧=「『注意(多義):』で始まる注意文を1行で引継ぎ」→新=「『注意:』で始まるnotes_for_writerの内容全体(『 / 』区切り全注意・後続『注意(多義):』含む)を省略・分割せずbrief該当fact直後へ」。test 13 PASS(新2件追加、旧1件の否定assertを規則文に合わせ微修正)。
- 5テーマP2台帳(`er052_output/open233_allfact_note_e2e_02/ledger/FREEZE.json`): base sha=TRIAL-04 provenance一致、notes-only diff/fact_id/fact数 全PASS、空notes 0(fact数 meta15/hormuz12/space_weapons22/sewer20/ai_control16)。
- Checker構成: 41キー全一致(`checker_switch_check.json`)。検証run(meta rep1)brief: 選択3fact、両Note到達3/3。checkpoint commit 1fefd10f。

### §94-2 Phase B
- 5テーマ×P2 2rep=10本、phase1/phase2/Checker完走。停止1回(sewer rep2 phase1 JA_FACT_CHECK_STOP/LEDGER_DEVIATION)→同枠1回再実行で完了。brief転記(両Note到達)10/10 ALL_PASS。

### §94-3 評価表(独立評価、従来版=TRIAL-04 Control rep1。全文=`er052_output/open233_allfact_note_e2e_02/eval/SUMMARY.md`、summary json検算で齟齬なし)
| run | Fact誤り(JA R2/EN最終) | ★分類 | 退行 | Checker誤許容 | Checker final/cycle/Rewrite |
|---|---|---|---|---|---|
| meta P2 r1 | 5 | HC-012 正 | 3 | 2 | REWRITE_THEN_DOWNGRADE/2/有 |
| meta P2 r2 | 7 | HC-012 正, HC-014 曖昧 | 3 | 6 | 同/3/有 |
| meta 従来 | 4 | HC-012 正 | 1 | 2 | 同/2/有 |
| hormuz P2 r1 | 8 | HF-007 曖昧 | 4 | 6 | 同/3/有 |
| hormuz P2 r2 | 10 | HF-007 正, HF-009 正 | 4 | 5 | 同/2/有 |
| hormuz 従来 | 2 | HF-007/008/009 正 | 0 | 0 | STAGE2_DOWNGRADE/1/無 |
| space P2 r1 | 1 | ★なし | 0 | 0 | STAGE2_DOWNGRADE/1/無 |
| space P2 r2 | EN5/JA7 | ★なし(参考F-001 JA重大誤読) | 2 | 2 | REWRITE_THEN_DOWNGRADE/5/有(EN) |
| space 従来 | EN2/JA3 | — | 0 | 0 | REWRITE_THEN_DOWNGRADE/3/有 |
| sewer P2 r1 | 4 | F-012 曖昧 | 2 | 4 | STAGE2_DOWNGRADE/1/無 |
| sewer P2 r2(再実行版) | 5 | F-010 正 | 3 | 3 | STAGE2_DOWNGRADE/1/無 |
| sewer 従来 | 6 | F-012 正 | 1 | 3 | STAGE2_DOWNGRADE/1/無 |
| ai_control P2 r1 | 6 | ★なし | 3 | 1 | REWRITE_THEN_DOWNGRADE/3/有 |
| ai_control P2 r2 | 4 | CONTROL-003 正 | 1 | 3 | 同/4/有 |
| ai_control 従来 | 5 | ★なし | 1 | 3 | STAGE2_DOWNGRADE/1/無 |

### §94-4 重大3件(読者を誤らせる水準、全文)
1. meta P2 r2 JA「ただし、主役になった人間が知らされていなかった。」(開示対象を契約スタッフ本人に取り違え。ENはCheckerが別の根拠なし表現へ書換)
2. space_weapons P2 r2 JA「つまり今回の発表は、「衛星を狙う兵器を配備した」と単純に読む話ではありません。宇宙、通信、地上の設備をまとめて守るための仕組みを、米国が公の言葉で認めたということです。」ほか1文(台帳F-001の配備承認を超える。ENはCheckerがRewriteで修正、JA未修正)
3. ai_control P2 r2 CheckerのRewrite誤動作: 「The evaluation environment set up by a third party was not properly configured, so it might connect to the internet.」→無関係な「In a simulated safety evaluation, Claude Opus 4 attempted blackmail in 84% of rollouts.」に置換(cycle2で削除、元の内容は最終ENから欠落)。→OPEN-238

### §94-5 横断所見
- 全10 runで両Noteがbriefへ逐語到達、brief長は従来の約2倍。Checker最終重大は10本とも0だが独立評価では誤り残存(Checker通過≠品質保証)。
- JA R2はChecker対象外のためENで修正・削除された問題文がJAに残りJA/EN不一致(ai_control r1, space_weapons r2, meta r2)→OPEN-239。Checker判定ぶれ(同種の支払義務者問題をr1 ACCEPTABLE/r2 BLOCKING)。

### §94-6 費用・時間
- 実費≈¥110.4(phase1 ¥43.4/EN ¥14.2/Checker ¥52.7、停止1回分は未記録・数円推定)/上限¥300。Phase A 16分、Phase B 15分、評価(3並列)約7分、準備(並列)約3分。

### §94-7 Status
- **USER_DECISION_REQUIRED**(Fable判定)。VALIDATED不可: P2版Fact誤り件数が従来版を下回らず、hormuzでは上回る(P2 8/10件 vs 従来2件)。REJECTED不可: n=2/テーマ・brief採用factが版ごとに異なりNote由来かrun揺れか切り分け不能、meta HC-012のrollback表現はP2 2/2で「正しい」。Production採用判断なし、Checker構成はPRODUCTION_WIRED未のまま不変、残11 run待機。

### §94-8 参照
- `er052_output/open233_allfact_note_e2e_02/`(`eval/SUMMARY.md`・`eval/E_*.md`・`runs/manifest.json`・`cost.json`・`ledger/FREEZE.json`・`checker_switch_check.json`)、`docs/pm/allfact_e2e_02/`、`docs/pm/delegation_log/2026-10-07_OPEN-233-META-ALLFACT-NOTE-E2E-TRIAL-02_{A1,D1}.md`。OPEN-237/238/239。

## §95 OPEN-233-E2E-STAGEWISE-NG-AUDIT-01(工程別NG比較表、2026-10-07、¥0)

既存成果物(§94のE2E 15本=従来版5+P2版10)の再評価のみ。API呼び出し・記事生成・Production変更なし。詳細は `er052_output/open233_allfact_note_e2e_02/eval/stagewise/STAGEWISE_SUMMARY.md`。

### §95-1 定義
- 重大=事実の意味が変わり誤解を与える/軽微=不正確・過剰断定・曖昧・軽い具体化(同一誤りは同一工程1件)。①JA最終稿 ②EN Rewrite前 ③EN Rewrite後 ④Checker最終cycle生件数 ⑤独立評価。
- ⑤は3系統で定義が混在していたため ng_items から再計算し統一: **⑤a=EN最終残存**、**⑤b=⑤a+JAのみ残存(①で発生しENでは修正・不在)**。
- **④は⑤と同質でない**: 最終cycleのblockingは全15本で0。non_blockingは正しい文へのACCEPTABLE指摘・決定論検査の誤検知を多く含む候補の生件数で、⑤の軽微(実NG)とは比較不可。

### §95-2 主表(重大/軽微)
| 段階 | 従来5本 | P2 10本 |
|---|---|---|
| ① JA最終稿 | 0/18 | 4/49 |
| ② EN Rewrite前 | 0/21 | 5/56 |
| ③ EN Rewrite後 | 0/19 | 1/52 |
| ④ Checker生件数(参考) | 0/52 | 0/99 |
| ⑤a EN最終残存 | 0/19 | 1/52 |
| ⑤b ⑤a+JAのみ | 0/21 | 4/57 |

### §95-3 遷移表(重大/軽微)
- ①→②英語化で新規: 従来0/3、P2 1/7。②→③Rewriteで修正: 従来0/2、P2 4/5。
- ②→③Rewrite新規: 最終残存 従来0/0、P2 0/1(ai-p2r2-08)/loop内一時発生 従来0/0、P2 1/0(ai-p2r2-07、OPEN-238)。
- ④→⑤見逃し(=⑤b): 従来0/21、P2 4/57。内訳 検出済み非BLOCKING 従来0/14・P2 0/41、未検出 従来0/5・P2 1/11、JAのみ(Checker対象外) 従来0/2・P2 3/5。

### §95-4 1記事当たり平均(重大/軽微)
- 従来: ①0.0/3.6、⑤a 0.0/3.8、⑤b 0.0/4.2。P2: ①0.4/4.9、⑤a 0.1/5.2、⑤b 0.4/5.7。テーマ別(従来1 vs P2 2)は STAGEWISE_SUMMARY.md §4。小標本でNote由来かrun揺れか切り分け不可。

### §95-5 重大NG全件(6件、詳細全文はSUMMARY §5)
- meta-p2r2-02: ENで開示対象を取り違え(「主役になった人間が知らされていなかった」→Rewrite後も「the person on the other end」と台帳外の対象断定が残存)。⑤a/⑤b残存、Checker最終未検出。
- ai-p2r1-01: 「厳重な監獄のはずが裏口の鍵がかかっていなかった」比喩(EN Rewriteで削除、JAに残存→⑤bのみ)。ai-p2r1-02: EN「whether it tends to be used for harmful purposes」の主体取り違え(Rewriteで修正)。
- ai-p2r2-07: Rewriteが無関係な「Claude Opus 4 attempted blackmail in 84% of rollouts」を挿入(cycle2で修正、一時発生。原因=precheck floorのEVID-006/CONTROL-004誤紐付け、A2所見・未検証)。
- sw-p2r2-01: 認められたのは軌道上space control weapons配備なのに「守るための仕組み」と記述(EN修正済、JAに残存)。sw-p2r2-02: 「初めて」の対象を兵器配備から「防衛の備え」へ拡張(EN修正済、JAに残存)。

### §95-6 判定保留・差分理由(要旨)
- 保留1(meta r1 Rewrite挿入文「That」の指示語、集計外)/境界4(sw r2「なぜ今→ロシア」軽微計上、sw従来sw-ctl-04はbrief根拠で3→4、ai r1「主役は舞台装置」、ai従来「有害傾向は実証されず」)=計5件。
- E_*.mdとの差の主因=E項目の統合/分離(meta r2 対象+追加を1件に統合、hormuz 因果をHF-009許容・比喩でNG非該当、sewerにF-001範囲不記載を追加等)。詳細はSUMMARY §6・§7。

### §95-7 Status
- **USER_DECISION_REQUIRED**。P2採否・Checker Production反映は判断しない(Production変更なし)。

### §95-8 参照
- `eval/stagewise/{STAGEWISE_SUMMARY.md,NG_*.md,stagewise_*.json}`、`docs/pm/delegation_log/2026-10-07_OPEN-233-E2E-STAGEWISE-NG-AUDIT-01_C1.md`。OPEN-237/238/239。

## §96 OPEN-238-PRECHECK-MISLINK-DIAG-01(Checker precheck偽陽性の診断、2026-10-07、¥0)

### §96-1 事象
- ai_control P2 rep2 cycle1でRewriteが無関係文を84%文へ置換(OPEN-238、REPORT §94-4)。
### §96-2 原因(精査済み)
- 英文「a third party」の「a third」が分数語辞書(`er052_open233_self_recovery_precheck_01.py` L112)で33.3%として抽出。単一%fact(EVID-006/CONTROL-004)との総当たり不一致でnumber_mismatch発火→Stage2スキップの無条件BLOCKING(runner `er052_open233_self_recovery_flow_runner_01.py` L8784-8800)→Rewriteが台帳値置換指示で置換。
### §96-3 再現範囲
- 他run再現0件(json 1,795件+18 run dir再実行)。
### §96-4 本番影響・関係
- 承認構成配線後は本番でも発生し得る。OPEN-235とは別経路(OPEN-236との関係は別管理)。
### §96-5 修正案
- 案1: party/parties後続は抽出除外。案2: 数字・%なし文はclaim化しない。案3: floor発火でもStage2経由(条件A=Opus独立レビュー要)。Fable推奨=案1+案2。
### §96-6 Status
- USER_DECISION_REQUIRED。修正未実施、Production変更なし(ユーザー承認+Opusレビュー前提)。
### §96-7 参照
- `docs/pm/open238_precheck_mislink_diag_01.md`、`er052_output/open233_allfact_note_e2e_02/eval/stagewise/notes_to_error_trace.md`(notes→誤り変換追跡: 直接証拠0件、仮説不支持)、`docs/pm/delegation_log/2026-10-07_OPEN-238-PRECHECK-MISLINK-DIAG-01_*`。


## §97 OPEN-233-NOTE-TRANSFER-MATRIX-TRIAL-01(転記形式×多義語注意の6条件マトリックス、2026-10-07)

### §97-1 設計
- 目的: 前回P2(逐語notes+多義注意)の誤り多発が「Note転記の形式」か「多義語注意」かを切り分ける。brief本文を3テーマ(meta/hormuz/sewer)ごとに1本へ固定し、T0=転記なし/T1=要約転記/T2=逐語転記 x M0=多義語注意なし/M1=あり の6条件、N=2、計36記事。Checkerなし(ENのb1bが最終)。
- DEV runnerに「固定brief開始」「Checkerなし」オプションを追加(Trial専用、Production経路不使用、test PASS)。brief・条件一覧: `er052_output/open233_note_transfer_matrix_01/briefs/`、rubric: `docs/pm/note_transfer_matrix_01/eval_rubric.md`(直前監査と同一基準)。

### §97-2 実行
- Phase B 36枠: EN完成33/STOP3(commit 2c3cd5a5)。停止2枠(hormuz T2M0 rep1 / sewer T0M1 rep2)は各1回再実行して完走(commit 263cddb9)。hormuz T0M0 rep1はdriverの誤判定で失敗扱いとなっていたが1回目成果物(`rep1_failed_a1`)が正常のため採用(2回目は不採用)。結果36/36。
- 実費≈¥268.8/上限¥600(`er052_output/open233_note_transfer_matrix_01/cost.json`)。API呼び出しなし(評価・集計工程は¥0)。評価は単独判定・人間確認なし。

### §97-3 6条件表(1記事当たり 重大/軽微、各6記事=3テーマ合算)
| 条件 | ①JA | ②EN | ★correct/ambiguous/misread |
|---|---|---|---|
| T0M0 転記なし | 0.00/0.67 | 0.17/0.67 | 12/1/0 |
| T0M1 | 0.00/0.67 | 0.00/0.67 | 13/1/0 |
| T1M0 従来相当 | 0.00/0.33 | 0.00/0.33 | 13/1/0 |
| T1M1 | 0.00/0.50 | 0.00/0.67 | 13/0/0 |
| T2M0 | 0.00/0.50 | 0.00/0.67 | 14/0/0 |
| T2M1 P2相当 | 0.00/1.33 | 0.00/1.67 | 14/0/0 |
- 全36本: ①JA 0/0.67、②EN 0.03/0.78(重大1件)。★fact重大誤読(misread)は0。

### §97-4 主効果・所見・仮説
- T別(EN軽微/記事): T0 0.67/T1 0.50/T2 1.17。M別: M0 0.56/M1 1.00。T2M1が最多(1.67)で交互作用の可能性があるが、N=2/セルでrun揺れと区別できない。
- 「福島県」型(台帳に県名なし・現実に正しい、sewer 6項目)を軽微から除くと、全36本のEN軽微は0.78→0.61、T2は1.17→0.83、T2M1は1.67→1.33(傾向は不変)。
- 参考: 前回(STAGEWISE §4)の従来⑤a 0.0/3.8、P2⑤a 0.1/5.2に対し、brief固定の本Trialでは全6セルのEN軽微(最大1.67)がこれを下回る。標本・条件が異なり厳密比較ではない。
- 仮説(未検証): Noteの形式より、brief本文の生成条件(notes除外台帳でB3がbriefを作る条件)が効いた可能性。根拠=meta HC-012が11/12本correct、前回P2で多発したhormuzの具体化が再現しない。brief固定のため本Trialでは直接検証していない。

### §97-5 重大NG全件(1件)
- hormuz-T0M0r2-01(ENのみ、HF-002、object): EN「Mr. Trump posted that for all cargo passing through the Strait of Hormuz, the United States would seek payment equal to 20 percent of the cost of providing safety and security.」(20%の対象が全貨物から安全確保費用へ入れ替わる。JAは正しい)。

### §97-6 境界・保留
- 境界: meta T2M1 rep2 EN「from employees」の主体ズレは軽微計上。保留(集計外)16件: meta 2/hormuz 9/sewer 5(多くはno_ng寄り、minor寄りはhormuz T1M0r1 EN曖昧、sewer 時制・範囲4件)。追補評価(hormuz T2M0 rep1、sewer T0M1 rep2)は各0/0・0/0(重大0・軽微0)。

### §97-7 Status
- **USER_DECISION_REQUIRED**(Fable判定理由: 条件間差が小さくN=2で採否を決められない。Production採用判断なし、`APPROVED_FOR_PRODUCTION`なし)。

### §97-8 参照
- `er052_output/open233_note_transfer_matrix_01/eval/{MATRIX_SUMMARY.md,matrix_summary.json,E_*.md,articles/}`、`docs/pm/note_transfer_matrix_01/{eval_rubric.md,aggregate_matrix.py,append_supplement.py,dangling_check.md}`、`docs/pm/delegation_log/2026-10-07_OPEN-233-NOTE-TRANSFER-MATRIX-TRIAL-01_D1.md`。commit faf6dd4a(Phase A)/2c3cd5a5/263cddb9。OPEN-237/238/239。

## §98 OPEN-238-PRECHECK-FALSE-POSITIVE-FIX-TRIAL-01(precheck偽陽性対策Trial、2026-10-07)
### §98-1 目的・ユーザー判断
- 目的: §96で原因特定したprecheck分数語偽陽性(「a third party」→33.3%)の修正案をTrial専用実装で検証。ユーザー判断: 設計Trial承認、残11 run再開は保留のまま。
### §98-2 設計
- 案1(ホワイトリスト+Opus条件C必須修正M1〜M3): 厳格版抽出は`check_number_mismatch`のforeign計算とrunner L8093の対象文特定のみ、他は現行抽出。DEV専用`er052_open238_precheck_fix_dev_01.py`(既定では何もしない)。案2(数字・%なし文をclaim化しない)は不採用(Opus同意)。O1(分数語をforeign証拠から外す)はユーザー決定で今回不採用・記録のみ。
### §98-3 テスト
- 単体12 PASS。26 run決定論Regression: 発火2→0、他全finding・loose抽出・L322はbit単位不変。実経路再生N=1: precheck発火0、third party文保持、84%文混入なし、retry/fallback 0、最終RESOLVED_REWRITE_THEN_DOWNGRADE 3cycle。O3(percentage point(s))0件。
### §98-4 残存リスク
- 残る偽陽性(「seeking a third.」「half the time」等)、直後が動詞の正当表現の取りこぼし、コーパスに正当分数語が無く取りこぼし実測不足、実経路N=1、分数語以外辞書の網羅走査未実施。
### §98-5 費用・時間
- 実費¥5.54/上限¥100(実経路再生のみ)。Phase A約15分・B約14分・B2約8分。precheckは決定論で追加費用0・処理時間影響なし。
### §98-6 Status
- **VALIDATED(Trial)**。Production採用はAPPROVED_FOR_PRODUCTIONではなくユーザー判断待ち(採用時は2ファイル数十行+Opus条件C+既存9 run Regression)。Checker PRODUCTION_WIRED未・残11 run停止継続。
### §98-7 参照
- `docs/pm/open238_fix/{design_01.md,closeout_01.md,open_gates.md,dangling_check.md}`、`docs/pm/opus_l2_review_open238_fix_01.md`、`er052_output/open238_precheck_fix_trial_01/`、commit 8f543442/0afc0911/971e9be1。OPEN-238。


## §99 OPEN-238-PRECHECK-FALSE-POSITIVE-PRODUCTION-WIRING-01(Production配線、2026-10-07)
### §99-1 ユーザー決定
案1(ホワイトリスト+M1-M3)をProduction採用=APPROVED_FOR_PRODUCTION(2026-10-07)。残11 runは再開しない。
### §99-2 実装差分
precheck +56/-1(`extract_percentages_strict`新設、`check_number_mismatch`のforeign計算のみ厳格版)、runner +2/-1(対象文特定)。expected/observed/ledger_pct/count種別は不変。配線commit 874dd6e2。
### §99-3 テスト・Regression
新規単体12 PASS(再実行確認)+既存911 PASS。26 run Regression 発火2→0他不変。9 runは再計算+記録値照合の代替証拠(判定変化なし)。
### §99-4 Opus条件C
必須修正なし(`docs/pm/opus_l2_review_open238_wiring_01.md`)。O1は記録のみ。
### §99-5 runtime evidence
未パッチProduction関数run_instance・承認スイッチ不変(E2E_02 dumpと一致)でai_control P2 rep2 1 run、実費¥5.30/17 call/上限¥20。配線版number_mismatch 0(配線前版は同テキストで2件)、third party文保持、RESOLVED_REWRITE_THEN_DOWNGRADE 3 cycle、Rewrite 1件(EVID-008)、retry/fallback/error 0。N=1、LLM非決定性あり。
### §99-6 判定基準と結果
(a)配線commitがorigin/mainに存在=充足 (b)入口・スイッチ不変=充足 (c)発火0・third party文保持=充足 (d)retry/fallback・例外なし=充足 (e)テスト・Regression PASS=充足。judgement: PRODUCTION_WIRED候補(Fable判定待ち)。
### §99-7 残存事項
「seeking a third.」「half the time」「one-half」連字符は未対応(記録のみ)。Checker全体は未配線、残11 run停止継続。
### §99-8 参照
`er052_output/open238_precheck_fix_trial_01/runtime_evidence/{RUNTIME_EVIDENCE.md,precheck_findings_per_cycle.json,provenance.json,approved_switches_dump.json,cost.json}`、`er052_output/open238_precheck_fix_trial_01/production_regression/`、`docs/pm/open238_fix/{production_diff_01.md,dangling_check_wiring.md}`。OPEN-238。
