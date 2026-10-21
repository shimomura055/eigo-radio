# Trial結果 TRIAL_RESULT_02(委任_03: 判断LLMのLuna化 + Ledger整合性N増し検証。ユーザー§9の1〜10の順)

管理ID: FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01 委任_03 / 2026-10-22
ユーザー原文: `docs/pm/delegation_log/2026-10-22_FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01_LUNA-NINC_USER.md`(本文3,588字、sha256[本文のみ]=4bb9d28325b5fab1ed7323fb7f5aced03dfd5c511f003a0680666cbdca0e7330)
設計: `TRIAL_DESIGN_02.md`(有料実行前commit a0209458c) / 前回: `TRIAL_RESULT_01.md` / 証跡: `er090_output/b3_core_number_rounding_trial_02/`(`evidence/`)
実装(Trial専用・Production無改変): `er090_b3_core_number_rounding_trial_02_{dataset,labels,run,p2,p2eval,audit,inject,analysis,structural,test_01}.py`(unit test 12件 + Trial_01の18件=30件PASS)
最終Statusは付けない(Fable判定)。**Production採用・配線なし**(git diff HEAD = 0: factlock writer / producer / Risk Flagger / production runner / routing / contract / Prompt block)。

使用モデル(25節): 丸め判断=`gpt-6-luna`(実response.model一致、下位系。**ユーザー指示による原価低減Trialが明確な例外理由**)/ 比較基準=`gpt-6.1-sol`(リポジトリ内の現行最上位系)/ Writer R0〜R2=`gpt-6.1-sol`(現行Production、実response.model記録)/ 英訳・RF・旧LDC=現行Production構成(Luna、Gemini 3.5 Flash Lite)。価格は`er005_output/cost_baseline_01/pricing_snapshot.json`の正式単価(Luna USD0.1/0.5 per MTok、Sol 6.1 USD2/10)、USD/JPY=160(`efam.USD_JPY`)。

## 1. Sol対Luna: 丸め判断の品質・原価・処理時間
同一Prompt(Trial_01の`build_judge_user_prompt` byte一致を4記事中3記事で確認。semiのSol基準だけv1 Promptだったため**Sol v2を1回再実行して公平化**)・同一schema・同一V1〜V7。Prompt/判定基準の意味は変更していない。変えたのは判断LLMのmodelとeffortだけ。
| | モデル/effort | 1call原価(実測) | 1call時間 | 4記事評価セット正解(strict事前ラベル A/E n=15) | 全18記事(strict n=63) |
|---|---|---|---|---|---|
| Sol | gpt-6.1-sol high | **JPY3.65**(14.61/4call) | 28.5s | 12/15 | (全記事は未実施) |
| Luna high | gpt-6-luna high | JPY0.23 | 23.7s | 12/15 | - |
| Luna medium | 同 medium | JPY0.18(18記事平均0.13) | 15.9s | 13/15 | 54/63・54/63(2rep) |
| **Luna low(採用候補)** | 同 low | **JPY0.12(18記事平均0.11)** | **7.5s(18記事平均5.7s)** | 14/15・13/15・11/15(3rep) | 56/63・54/63・54/63(3rep) |
- **原価はSol比 約97%減(3.65→0.12)、時間は約74%減(28.5s→7.5s)**。品質は「事前ラベル正解率でSolと同等(4記事評価セットで12/15 同士、Luna low 11〜14/15)」。誤りの中身は同型(semiの`167億ドル→約170億ドル`/`54％→約50％`/`約348億ドル→約350億ドル`をSolも丸めた)=Luna固有の劣化ではない。
- Luna lowの追加処理はなし(effortの最適化のみ、Prompt/出力項目は無変更)。Lunaで必要十分(Solと同等・費用97%減)に達したため**追加のmodel探索は停止**(ユーザー§8)。
- 再現性: Luna low/medium計5runで71概念中、判断が割れたのは15概念(21%、Luna low/medium計5run)。割れた概念は主に`634`/`1,332`(標本数)/`9.59％`/`83.30ドル`/`295億ドル`/BYD台数。Sol 1回の判断(Trial_01)でも粗さが揺れた(UDR #135 D3)のと同傾向。

## 2. 検証規模(独立記事数・Fact数・丸め対象数を区別)
| 項目 | 数 |
|---|---|
| 独立記事(distinct Ledger) | **18**(テーマ単位では15: coffee×2/ai_control×2/mey×2が同テーマ別Ledger) |
| 採用Fact(選定済み) | **75** |
| 機械選定された中核数値 concept / 表記 | **71 / 75**(周辺数値は判定対象外) |
| 人工fixture | **0**(7カテゴリが実中核数値で充足) |
| Luna判断が「丸め可」にした concept(Luna low 1run目) | 14/71(20%)。3run=14/16/15 |
| Writer含むPhase 2 | 4記事 x 3arm(Control/Control2/After)=**12 arm**、Luna丸め指定 concept = 7件(4記事)、うち**Writerが実際に使った指定概数=2件**(paycheck`最大約13万5千人`、hormuz`約10％`)。boredom/semiはWriterが指定概数も標本数も記事に使わなかった |
- カテゴリ充足(`evidence/coverage.json`、機械分類・重複該当あり): C1大きな人数/金額16、C2小数/割合/精度28、C3閾値/限定語/近接比較14、C4日付/回数/小数量23、C5同一Factの複数数値54、C6既に「約」9、C7同形で適否が分かれる対5組。
- **サンプル偏り(正直に)**: 事前ラベルA(丸めるべき)=5・E=58・B(境界)=8。機械選定の中核数値は大半が日付・小整数・閾値・価格・率で、「丸めるべき」実例は少ない(Aの正解率は粗い推定)。Phase 2は4記事・Writer 1サンプル/arm(+Control 2サンプル)で、統計的結論ではなく**構造的検証+観測**。Phase 2の記事選定規則(luna_low 1run目でAPPROX>=1の記事から多様性優先4本)は事前に`run`に固定。

## 3. 丸めるべき/丸めてはいけない数値の正解率
**事前登録ラベル(strict、判断前にcommit、LLM非開示。`..._labels.py`)** と **事後再ラベル(post-hoc v2)** の両方を報告(事後再ラベルは事前ラベルを置換しない):
| 指標(Luna、全18記事) | strict(n=A5+E58) | post-hoc v2(n=A5+E49、O=任意9・B除外) |
|---|---|---|
| 最終判断の正解(V1〜V7後) | low 56/54/54、medium 54/54 (/63) | low 53/53/51、medium 53/54 (/54) |
| **過剰丸め(Eを丸め可)** final | low 6/8/7、medium 8/9 | **low 0/0/1、medium 0/0** |
| 丸め漏れ(Aを厳密に) | low 1/1/2、medium 1/0 (/5) | 同 |
| LLM素の過剰丸め(V後ではない) | low 17/20/17 (/58) | - |
| V3/V7による降格で誤って阻止したA | **0**(全run) | - |
- **決定論検証V1〜V7は有効に作動**: 素の判断で17〜20件(low)ある過剰丸めのうち、V3(通常四捨五入)/V7等で10〜12件が最終までに降格(例: `0.0630→約0.063`、`3%→3%`、`0.0630`のV7[同Factの0.0589と衝突])。Aを誤って阻止した例は0。
- **strictラベルと承認済み既定の食い違い(重要)**: 過剰丸めの大半は`6.1%→約6%`/`8.7%→約9%`/`5.98％→約6％`/`9.59％→約10％`/`7.29ドル→約7.3ドル`で、事前ラベルでは私がE(厳密)と置いたが、承認済みの`NUMERIC_PRECISION_LEVEL_INDEPENDENT_DEFAULT_BLOCK`(`er003_v1_n3_01_evidence_compression_editor.py:121-131`)は「小数%は概数が既定(25.2%→約25%、44.7%→約45%)」と定める。つまり**strictラベルが承認済み既定より厳しかった**(ラベル側の問題。モデル側の誤りではない)。これらをO(任意)としたpost-hoc v2では過剰丸めは0〜1件。
- **真に問題のある丸め判断(モデル誤り・V1〜V7が止められないもの)**: ①`14(原告数)→約10`(low rep3の1回、相対誤差28.6%、V3は「通常四捨五入」で通過)②`約2.6％→約3％`(既に概数の再丸め、15.4%、5run中5回)③`約348億→約350億`・`167億→約170億`(既に概数/CEO丸め値の再丸め、相対誤差<2%で意味は不変だが承認規定が無い境界)④`54％→約50％`(粗い1桁丸め)。①②は相対誤差10%上限(提案V8、**未採用**)で阻止可能: 保存済みLuna判断90件の丸めのうち10%超は6件のみ(①1件+②5件)、正解の丸め(A)を阻止するのは0件(`evidence/label_v2_analysis.json`)。V8は新しい品質基準にあたるため**提案のみ**。

## 4. Fact Lock / Risk Flagger / Ledger Deviation Checker(LDC)の検査結果
(`evidence/phase2_summary.json`、`evidence/structural_diff_02.json`)
| | Control(1) | Control(2、再生成) | After(Luna丸め) |
|---|---|---|---|
| Writer STOP(記号QA/TagLeak/Provenance)・再生成retry | 0 / 0 (4記事) | 0 / 0 | **0 / 0** |
| 決定論数値監査 規則(5)違反トークン(JA R2+Adv+Std) | 1 | 2 | 2 |
| 〃 指定概数を使った記事 | - | - | 2/4記事(paycheck/hormuz)。指定外丸め・周辺数値の混入 0 |
| `【概数表記】`等のタグ漏れ | 0 | 0 | **0**(4記事 x JA/Adv/Std) |
| Risk Flagger flag数(Advanced+Standard 計) | 14 | 25 | 27 |
| 〃 うち丸め数値を含む文へのflag | - | - | **0 / 27** |
| LDC(旧、Trial専用参考) deviation数 / MAJOR | 2 / 2 | 15 / 11 | 10 / 9 |
| 〃 `changed_number` | 0 | 0 | **0** |
| 実コスト(4記事計、Writer+EN+RF+LDC) | JPY61.7 | JPY69.0 | JPY61.3 |
- **規則(5)の例外は指定中核数値にしか効いていない**: Afterの規則(5)違反2件はsemiのEN `29.6 billion`(JA R2は`295億9,100万`で厳密、英訳段が`29.591 billion`を3桁表示にした)で、**Controlの再生成(2)にも同じ違反が出る**=丸め指定とは無関係の英訳段の表示揺れ(相対差0.03%、意味不変)。Control(1)のboredom JAには`２組`(中核数値外の数字を書く規則5違反)が出た=Writer揺れ。
- **Risk Flaggerは確率的で、Control同士でも14↔25と大きく揺れる**(同一入力・同一条件の再生成のみの差)。Afterの27はControl(2)の25の範囲。丸めに起因するflagは0。RFは非Blocking(`er053_risk_flagger_production_01.py:7`、runner:305-345)で、停止はしない。
- **旧LDCのPASS/FAILだけでは運用可否を判断しない**(ユーザー指示)。LDCもControl内で2→15と揺れ、`changed_number`は丸め指定の有無に関わらず全arm 0。

## 5. 真のFact NG・Checker誤NG・見逃し(ユーザー§5の4区分)
| 区分 | 件数 | 具体例・原因・再現性・影響 |
|---|---|---|
| ① 丸めで実際にFactの意味が変わったNG(Writerまで到達) | **0** | Phase 2で使われた指定概数は2件: `最大134,515人→最大約13万5千人`(JA/Adv/Std全段で`最大`と「解析ごとに異なる」保持、LDC changed_number=false、RF flagなし)/`9.59％→約10％`(`rose about 10%`、RF flagなし)。再現性: Phase 2は1回ずつ |
| ①' 判断段のNG(Writerへ未到達) | 判断段で1件(後述) | `14→約10`(low rep3の1回)は意味を変える丸めだが、V1〜V7を通過した。Phase 2対象外のため下流影響は未検証。Production採用時は無防備(V8類の防止策が必要) |
| ② 丸めは正しいがCheckerが誤ってNG | **0**(Production RF/旧LDC)、**1種**(Trial専用の数値監査) | 数値監査が`29.6 billion`を「指定外丸め」と判定(英訳段の表示揺れ、真のNGではない)。RF/LDCは丸め文を誤NGにしていない |
| ③ 丸め以外のWriter生成揺れによるNG | 複数 | RF flag数14↔25(Control同士)、LDC 2↔15(同)、boredom JA`２組`、semi`29.6 billion`(Control(2)にも) |
| ④ NGにすべき数値変更をCheckerが見逃し | **見逃し: RF 0件/7、旧LDC 1件/7(M3)** | **既知NG注入テスト**(`evidence/injection_test.json`): After Advancedに7種を注入: 値ずれ(+11%/2倍)・限定語/変動の欠落・閾値反転(以上→以下)・方向反転(rose→fell)・厳密値変更(20%→30%)・指定外丸め(11件→約10件)。**RFは7/7を検出(M3`11→約10`は信頼度0.30と低く、基線ノイズと区別しにくい)**。旧LDCは6/7(M3を見逃し)。※検出=Human Review対象flagであり、ProductionのRFは停止しない |
- 影響評価: 丸めの導入で新たに「止まる」経路は無い(RF非Blocking、Writer STOPは記号QA/TagLeak/Provenanceで丸めと無関係)。**ただし `【概数表記】` の漏れは検知されない**: ProductionのTAG_LEAK_REは`概数表記`を含まず、`w1.assert_no_tag_leak`に漏れた本文を渡すとPASSし`clean_ja_for_next`も除去しない(実関数で確認、API 0)。今回の漏れ実測は0/4(Trial_01も0)だが、漏れるとTTSにそのまま読まれる(無音の品質リスク。停止ではない)。Production採用時は`TAG_LEAK_RE`/`MARK_RE`への追加が必要(= Production Validatorの変更なので提案のみ。Trial_01 S5と同一)。

## 6. Control比のProduction停止率・retry・Human Review増減見込み
- **停止率**: 0/12 arm(Control 8、After 4)。0/n の片側95%上限はn=12で22%、After 4本のみで53% → **サンプルでは「頻繁に止まる」兆候なし、ただし小標本のため上限は緩い**。構造的には丸めは新しいSTOP経路を持たない(RF非Blocking、Writer STOPの発火条件は丸めと無関係)。
- **retry**: Writer記号QA再生成/R2 rerun = 0/12。
- **Human Review(RF flag)増分**: After − Control(1) = +13(27−14)、After − Control(2) = +2(27−25)。Control(1)→Control(2)で既に+11。**増分は再生成揺れの範囲内で、丸めに起因するflagは0/27**。HR増加の見込みは「丸めに起因する増分は観測されず」と判断(ただし統計検出力は低い)。
- 見込み(量産): 丸め判断が「丸め可」にする中核数値は約20%(14/71)、その約3割をWriterが実際に使った(2/7)。使われなかった指定は影響0。使われた場合のリスクは「`14→約10`」型の判断誤りと`【概数表記】`漏れ(上記)。

## 7. B3既存機能・Writerへの情報伝達の不変性(API 0、`evidence/structural_diff_02.json`)
- Phase 2の4記事: B3出力・Ledger・storyline_b3の全ファイルsha(8〜16ファイル)が dataset == Control(1) == Control(2) == After で**完全一致**。注記md/sidecar/manifestの契約検証`validate_annotated_b3`が全armでPASS。
- Control(1)/(2)の実使用R0 Promptは`build_r0_prompt`再構成と**byte一致**(=Control=現行Production同等)。AfterのR0 Promptは再構成と一致し、**差分は追記2〜4行(指定概数行)+規則8の1項のみ、削除行0**。
- 概数可0件のoverlay(18記事中10記事)ではWriter Promptが従来とbyte一致(DefaultOffIsolation相当)。Production module 7ファイルのgit diff = 0。中核数値の件数・順序・対象・Fact選定は不変(再実行していない)。

## 8. NG発生時の根本原因と、品質を下げない対策案
| 原因 | 根拠 | 区分 | 対策案(いずれもProduction未適用・承認要) |
|---|---|---|---|
| 判断の過剰丸め(小数%・既に概数の再丸め) | 過剰丸めの大半がstrictラベル側の過厳(承認済み既定は小数%を概数が既定) | 丸め粒度の不適切さ/ラベル不一致 | ユーザー判断D3: 粒度方針(小数%を既定で概数にするか、既に概数の値を再丸めしてよいか)を明文化。モデルの問題ではない |
| `14→約10`型の意味変更を伴う丸め | low rep3の1回(V1〜V7通過) | Lunaの丸め判断の誤り | 提案V8: 丸めの相対誤差10%上限(保存済み90件中6件を阻止、正しい丸めの阻止0)。**新品質基準のため承認要**。誤PASSリスク: 10%以内の意味変更は通る。QCD: 追加原価0(決定論) |
| 指定概数の不使用/揺れ(Writerが指定を使わない) | 使用2/7、判断の割れ15/71 | Writerへの伝達・追従 | 影響は「丸めの効果が出ない」のみ(品質は劣化しない)。効果の薄さ=D4価値判断 |
| `【概数表記】`漏れが無検知 | 実関数で確認 | Fact Lockの例外処理の問題 | S5: `TAG_LEAK_RE`/`MARK_RE`へ`概数表記`追加(Production Validator変更=承認要)。誤PASSリスク: 追加により既存の正当な本文で誤停止する可能性は極小(タグ語のため) |
| 英訳段の表示丸め(`29.6 billion`) | Control(2)にも出現 | 後続R1/R2・英訳工程による変化(丸め無関係) | 対策不要(相対差0.03%・意味不変)。数値監査側で表示精度を許容する案は検討余地 |
| RF/LDCの確率的揺れ | Control同士で14↔25 | Checkerの誤判定ではなくノイズ | 運用: HR増分はControl揺れ幅と比較して評価 |
- Checkerの判定緩和・基準引下げは行っていない。

## 9. 1記事セットあたりの追加原価・処理時間(実測)
- **Luna low: 追加JPY約0.12/記事(0.11〜0.13、18記事平均)、追加処理時間 約5.7〜7.5秒**。Sol(前回)はJPY3.65/28.5秒だったので、**+5.2%→+0.17%(70円/記事セット比)に低減**。
- Writer/英訳/RF側の追加原価は観測できず(After W1+EN平均12.6 vs Control(1)13.0、Control(2)14.3=揺れの範囲)。Prompt追記は約3行(約150token)のため<JPY0.01。
- 本案件の実費合計: **JPY217.39**(judge Sol 3.80・Luna 11.67・Phase 2 12 arm 192.0[Control 61.7/Control(2) 69.0/After 61.3]・注入テスト9.93)。案件見積JPY300以内。日次(2026-10-22 JST、`daily_dev_cost_01.py`)adopted=JPY213.61〜(開始時6.32)で1,000円以内。出典=各`raw_usage_log.jsonl`+`er053_cost_aggregate_01.compute_stage_cost_breakdown_multi`(`pricing_snapshot.json`)。
- 設計時見積(JPY210〜230)に収まった。Control(2)を追加(+69.0)したのは「Writer揺れ」を分離するための事前見積内の判断。

## 10. Fable独立評価・最終Status・Production採用に必要なユーザー判断
Fable欄(2026-10-22 Fable判定・逐語記入):

**Trial2の分類: `VALIDATED`(条件付き)。管理IDのStatusは引き続き`USER_DECISION_REQUIRED`(UDR #135を更新)。** `APPROVED_FOR_PRODUCTION`ではなく、Production採用・配線はユーザー正式承認が必須。

**何が確認できたか(Fable)**
- Luna化: 判断品質はSolと同等(誤りの型も同じ)、1件あたり費用約97%減(JPY3.65→0.12)、時間約74%減。Prompt・判定基準・V1〜V7は無変更。探索停止は妥当。→ 目的1は確認できた。
- N増しFact整合: 独立18記事・Fact 75・中核数値71(人工fixture 0)で7カテゴリ充足。Writerまで到達した「丸めで意味が変わったNG」0、停止0/12、retry 0/12、Risk Flaggerの丸め由来flag 0/27、旧LDC changed_number 0、注入テスト7種はRFが7/7検出。B3・Ledger・storylineのshaは全arm一致、Promptの差分は追記のみ、概数0件の記事ではPromptがbyte一致。→ 「丸めで量産が頻繁に止まる」兆候はない。

**留保(Fable)**
1. 判断段の実害候補1件: `14(原告数)→約10`がV1〜V7を通過した。相対誤差約29%で、Writerが使えばFactの規模が変わる。提案V8(相対誤差10%上限)は保存判断90件で6件を阻止し正しい丸めの阻止0。**採用する場合はV8を必須条件とする**(基準の引下げではなく追加の安全網)。
2. 正解率の読み方: 事前登録のstrictラベルでは54〜56/63(過剰丸め6〜9)。承認済み既定(小数%は概数が既定、`er003_v1_n3_01_evidence_compression_editor.py:121-131`)へ整合させた事後ラベルv2では51〜54/54。v2は事後の再ラベルであり、粒度の正解はユーザー定義(D3)に依存するため、v2の数値を単独で品質証明に使わない。
3. 価値の大きさ: 指定概数をWriterが実際に使ったのは7件中2件。聞き取り評価は未実施。効果は限定的で、採用の是非は原価ではなく「聞き手向けの数値表現を品質として求めるか」の判断。
4. 標本: Writer段は4記事・各arm 1〜2サンプル。Control同士でもRF flag 14↔25、LDC 2↔15と揺れており、Human Review増分の検出力は低い。0/12は「頻繁な停止がない」ことの弱い証拠であり、統計的証明ではない。
5. 無音の品質リスク: `【概数表記】`タグは`TAG_LEAK_RE`/`assert_no_tag_leak`の対象外(実関数で確認)。漏れればTTSがそのまま読む。実測漏れ0だが、**採用時はS5(MARK_RE/TAG_LEAK_REへの追加)を必須条件とする**。
6. 判断LLM(Luna)とRisk Flagger(Luna系を含む)の同系列バイアスは残る。注入テストで検出7/7だが、`11件→約10件`は信頼度0.30と低い。

**費用(出典付き)**: 本案件実費JPY217.39(judge Sol 3.80/Luna 11.67、Phase2 12arm 192.0、注入テスト9.93。案件見積300円以内、設計時見積210〜230)。`daily_dev_cost_01.py --date 2026-10-22`のadopted値はJPY213.61で、本日の実費合計(本案件217.39+PNMH Trial 6.32=223.71)と約10円の差がある(集計範囲の違いと推定、未確認)。日次1,000円以内。

**Fable推奨(Production採用判断=ユーザー)**: 前回(#135)の推奨「保留」の主因だった原価(+4〜6%)はLuna化で+0.17%まで下がり、量産停止の兆候も観測されなかった。したがって推奨を**「(ア)採用方向で最小仕様を確定」へ更新**する。条件=V8必須・S5必須・粒度方針を承認済み既定(小数%は概数)+相対誤差10%以内+既に概数の値は再丸めしない、で固定・judge=Luna low。採用方向が選ばれた場合、Production実装前にOpus独立レビュー(11-3条件C、S1〜S7+V8+S5の設計)を入れ、その後に実装・Regression・runtime evidenceへ進む(設計レビューまでは追加費用0)。価値が限定的(使用2/7)であることを踏まえ「(イ)保留」も合理的であり、ユーザーの品質定義に従う。

分類候補(Sonnet材料。最終はFable): **`USER_DECISION_REQUIRED`**(根拠: Luna化による品質同等・原価97%減は確認できたが、Production採用にはD1〜D4の正式判断が必要。`REJECTED`にする根拠は無い。`VALIDATED`ラベルはFableが付与)。
判断候補(Fableがラベル付与):
- D1(承認済み仕様の変更): Fact Lock数字規則(5)への【概数表記】例外追加(前回と同じ・未解決)。
- D2(原価): Luna low化でJPY+0.12/記事(+0.17%)。採否と、judge model(Luna low vs medium)の選定。
- D3(品質水準): 丸め粒度方針(小数%は概数が既定=承認済み既定の確認、既に概数/CEO丸め値の再丸め可否、1桁丸めの可否)と、提案V8(丸めの相対誤差10%上限)の採否。
- D4(価値): 指定概数をWriterが実際に使ったのは2/7。聞き取り効果は未評価(音声評価なし)。
- D5(Production Validator変更): `TAG_LEAK_RE`/`MARK_RE`へ`概数表記`追加(S5)。
残存課題: Phase 2は4記事・Writer 1〜2サンプル/arm。RFは確率的でHR増分の検出力は低い。事前ラベルAが少ない(5件)。判断LLM(Luna)とRF(Luna A3/A4+Gemini)が同モデル系列を含むバイアス。聞き取り評価・TTS・ASRは対象外。
SSOT整合: CURRENT_SPEC.md:1730(Spoken-first)/:2096(Listener-Friendly)、DECISION_LOG.md:14388/:20533、`er003_v1_n3_01_evidence_compression_editor.py:121-131`、OPEN-437と整合(矛盾なし、D1のみ要承認)。CURRENT_SPEC/DECISION_LOGは変更していない。
