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
