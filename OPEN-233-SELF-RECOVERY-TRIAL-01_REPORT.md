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
