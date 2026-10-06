# OPEN-233-FLOOR-SELECTIVITY-OPTIMIZATION-01 設計分析(委任_01c、¥0、read-only)

Status上限: USER_DECISION_REQUIRED / DESIGN_READY_FOR_REVIEW(最終分類はFable/ユーザー)。コード・Prompt・Production・gold定義は不変。本docは決定ではなく材料。Opus独立技術レビューGate条件A該当(決定論/LLM役割分担変更、実装前)=Fableが別途依頼。

正本データ: `er052_output/open233_floor_selectivity_offline_01/floor_fire_analysis_01.md`(以下「集計md」、script `.py`/`.json`同階層)。下表は集計mdの転記。

## 0. 前提・provenance
- 35件と24/6/5ラベル: reuse(RCA `docs/pm/rca_open233_e2e_neg7_human_review_01.md` §6の【推測】ラベル、Sonnet判定。Fable/ユーザー未確認)。ラベルは正解ではなく暫定。
- floor発火理由・LLM判定・S1: frozen(E2E保存出力)。案別件数: replay推計(in-sample、¥0)。LLM追加確認の結果は未測定。E2E自己確認: No。
- 「floor」=runner `apply_floor`(機械Safety)。5フラグ(`FLOOR_FLAGS`: changed_actor/number/negation/comparison/time)+因果floor(`changed_causality_floor`)+Tier0補助(`tier0:aux:issue_actor`)。
- 上位原則(`design_open233_self_recovery_flow_01.md` §0-1): 「英語学習者に記事の本質について重大な誤解を与えるものだけを止め、それ以外はできるだけ元記事を守る」。floorはこの原則上、「重大性」を判定する能力を持たない。

## 1. 35件のカテゴリ別内訳
LLM判定=後段AI(Stage 2)の判定。複合flagは延べ計上(合計35超)。

| カテゴリ | 延べ発火 | 正当 | 不要 | 判断不能 | LLM判定(重大/軽微/問題なし) | 単独/複合 |
|---|---|---|---|---|---|---|
| 主体(changed_actor) | 6 | 2 | 2 | 2 | 1/1/4 | 6/0 |
| 数字(changed_number) | 4 | 3 | 1 | 0 | 2/1/1 | 4/0 |
| 否定(changed_negation) | 5 | 0 | 5 | 0 | 0/1/4 | 3/2 |
| 比較(changed_comparison) | 14 | 0 | 13 | 1 | 0/1/13 | 10/4 |
| 因果(changed_causality_floor) | 1 | 0 | 1 | 0 | 0/0/1 | 1/0 |
| 時期(changed_time) | 8 | 1 | 6 | 1 | 1/3/4 | 6/2 |
| その他(tier0:aux:issue_actor) | 1 | 0 | 0 | 1 | 0/0/1 | 1/0 |

全体LLM判定: ACCEPTABLE(問題なし)25/QUALITY(軽微)6/BLOCKING(重大)4。unsupported_new_claim併発34/35、Stage1 sub_reasons全件model。

【確認】正当6件の内訳(No.): 数字3件(9,10,21)、主体2件(5,22)、時期1件(23)。うちLLM自身が重大判定=4件(9,10,22,23)、floorだけが重大化=2件(5,21、LLMは軽微)。
【確認】比較14件は正当0・不要13・判断不能1。否定5件は正当0。比較+否定=19延べ発火が単独で最大の誤爆源。

### 誤爆の典型パターン(逐語、集計md No.)
- 比較(修辞・比喩): No.4 "The more useful a service is, the less it should hide the pe..."、No.26 "It was like an AI-led play with a hidden supporting actor."、No.28 "A service that seemed simple now looked like a mystery story..."、No.31 "That uncertainty turned convenience into a mystery."(いずれも元記事の事実比較ではなく規範・比喩。LLM=問題なし)
- 否定(不在の言い換え): No.2 "The issue was not that humans made the calls themselves."、No.29 "No large information leak was confirmed."、No.32 "The company did not stop Muse itself."(LLM=問題なし/軽微)
- 時期(つなぎ語・一般文): No.13 "But this was where the problem began."、No.18 "And this was where the concern began."、No.17 "They will want to know if it is AI or human."(【推測】事実時期の変更ではなく語彙・文脈一致での発火。発火機構の個別確認は未実施)
- 主体(導入・言い換え): No.24 "Imagine asking AI to book a haircut."、No.25 "So it sounds like a simple story: you make a request, and AI..."(元記事の主体を変えていない導入文。判断不能/不要)
- 因果: No.33 "...you make a request, and so..."(Tier0語彙 "so" の接続語一致のみ)
- 正当の例: No.9/10(数字floor、LLM重大)、No.22(主体: "On July 13, Trump posted that all cargo..."、LLM重大)、No.23(時期: "The fee plan left the stage, but the events driving oil pric..."、LLM重大)。

## 2. 誤爆の主因(「後段機械Safety単体」の分析)
不要24件の原因割付(集計md): (i)Stage 1フラグ不整合 17件/(ii)種別は妥当だが重大性判定欠如 6件/(iv)Tier0語彙 1件/(iii) 0件。判断不能5件は別枠。

- 【確認】`apply_floor`(runner L2432)は5つの`changed_*`のいずれかtrueなら、LLM(Stage 2)の判定に関係なくBLOCKINGへ上書きする。重大性(誤解を与える程度)の判定を持たない。floor「単独起因」の強制重大は35件中31件(LLM自身がBLOCKINGは4件のみ)。
- 【確認】(i)17件: Stage 1が付けたchanged_*フラグ自体が文の実態と不整合(例: 比較・否定フラグが付いたが元記事に対応する事実比較・否定がなく、`issue_type=absence_only`)。floorはこのフラグを検証せず信頼して重大化する(フラグ無検証上書き)。
- 【確認】(ii)6件: 種別(主体/数字等)の変化自体は実在するが、誤解の重大性判定が無く、LLMが「問題なし」と判定していても強制重大。
- 【確認】(iv)1件: 因果floorがTier0語彙("so")の接続語一致のみで発火。
- 【確認】LLM判定は問題なし25/軽微6/重大4。floor発火後のLLM再判定・追加確認は`FLOOR_VERIFY_MODE`既定offでは存在せず、time_only(Trial専用)でも時期のみ。比較・主体・数字・否定は決定論のみ(`FLOOR_VERIFY_DETERMINISTIC_ONLY_FLAGS`、委任_61)。

### Checker候補過多とは独立である根拠
- 【確認】「候補が多かった」ことは35件の分母を作るが、不要24件の原因は分母の大きさではなく、(a)フラグ不整合を検証せず上書き、(b)重大性判定の不在、(c)語彙一致による発火、というfloor固有の機構である。Checker候補を何件に絞っても、発火した候補のうち不要率は同じ機構で生じる(floor発火35件中、floor固有の欠陥で説明できる不要は(i)+(ii)+(iv)=24件=不要全件)。
- 【確認】unsupported_new_claim併発34/35: Stage 1が同時に新規主張検出も出しており、floor発火の大半はStage 1出力品質に依存する。ただしこれはCheckerの問題であってfloorの上書き機構の問題とは別で、双方に対策が必要。
- 【推測】floorを精密化してもStage 1のフラグ不整合は残る。(i)の対策は「フラグを検証してから重大化」であり、検証者(LLM/S1)なしの決定論のみでは(i)の完全除去は困難。

## 3. 設計案比較(replay、in-sample、35件、¥0。LLM追加確認の結果は未測定)
RCA §8是正案の対応(C=floor_verifyを時期以外へ拡張、D=Stage 1 promptで修辞・比喩を対象外、G=軽微なfloorをQUALITY扱い)で「A/B/C分類」を行う。ここでの分類は既存是正案との対応づけであり、採否ではない。

| 案 | 内容 | 想定強制重大 | 正当6の行き先 | 追加確認へ | 非重大化 |
|---|---|---|---|---|---|
| 0 現行 | 5フラグ+因果+Tier0、即BLOCKING | 35(floorのみ起因31) | 強制6 | 0 | 0 |
| 1 条件精緻化維持 | 発火条件を絞り即BLOCKING維持 | 14(floorのみ10) | 強制6 | 0 | 21 |
| 2 確定のみ強制+他は追加確認 | 14のうち決定論で確定したものだけ強制 | 8(floorのみ5) | 強制4/追加確認2(No.5,23) | 27 | 0 |
| 3 トリガーのみ(重大判定しない) | floorは追加確認トリガーのみ | 0(最終BLOCKING=LLM自身の4) | 追加確認6 | 35 | 0 |
| 4 floor撤廃+既存S1 | floor廃止、既存Stage 2第2意見(S1)へ | 4(LLM自身) | LLM自身BLOCKING4/S1へ2(No.5,21) | 31 | 0 |
| 5 段階化 | 案1+非重大化の一部を追加確認 | 14(floorのみ10) | 強制6 | 3 | 18 |

案1/5の「非重大化」=floor強制を外しStage 2のLLM判定へ戻す(判断不能5のうち案1は2件が戻り3件が強制、案5は1件戻り/1件追加確認/3件強制)。判断不能5件の行き先は案2では追加確認4/強制1、案3/4では全件追加確認。

### 3-1. 各案の評価(定性)
| 観点 | 案0 | 案1 | 案2 | 案3 | 案4 | 案5 |
|---|---|---|---|---|---|---|
| Safety | 最大(過剰) | 現行同等(6維持) | 追加確認で降格する余地=見逃しリスク | LLM/S1依存。決定論の下限なし | 決定論下限なし。Stage 2のB3 mis-downgrade履歴あり | 案1同等+低リスク |
| 不要Rewrite削減 | 0 | 大(不要24→5) | 大(不要24→3強制) | 最大 | 大 | 中〜大 |
| コスト | 基準 | ¥0増 | 追加確認27件、S1実績¥0.028/claimなら約¥0.8/35件(推計) | 同35件約¥1(推計) | 31件約¥0.9(推計) | 3件のみ |
| 実装複雑性 | - | 小(条件分岐のみ) | 中(確定判定+確認経路) | 中 | 小〜中(floor無効化) | 小〜中 |
| 運用安定性 | 安定(過剰) | 条件が「語彙・構造」依存、新fixtureで再発の可能性 | 確認経路の失敗・API障害時のfail-closed要 | 同左 | 同左 | 案1と同等 |
| 正当6維持 | 6/6 | 6/6(in-sample) | 4確定+2は確認次第 | 確認次第 | 4+2確認次第 | 6/6 |
| RCA対応 | - | D近傍(Stage 1側でなくfloor側の絞り込み。新規) | C(+時期以外へ拡張) | G/C混合 | G近傍 | D/C混合 |
| 条件A(Opusレビュー) | - | 該当(判定ルール変更) | 該当 | 該当 | 該当 | 該当 |

関連Opus台帳(`docs/pm/OPUS_FINDINGS_LEDGER.md`参照のみ): OF-021(因果は決定論floor対象外、CAUSAL_FLOOR採用)、OF-016/OF-022(F3: Stage 1非検出だとfloor/precheckが走らない=floor配線)、OF-005(D*は穴を閉じない=三層構造)、OF-014/OF-017(台帳Grep一致のみ、内容未確認)。案3/4はOF-016/022のfloor配線方針と整合を再確認する必要あり【推測】。

DECISION_LOG参照(見出し行のみ): L18373(委任_60: `FLOOR_VERIFY_MODE`既定OFF、案1実装)、L18434(委任_61: 時期のみへ縮小、`comparison_time`廃止)、L19054/19072(Tier 1確認役=floor_verifyの一般化、Tier 1'=S1)。委任_58のF1「CLEARED自動解放」は廃止済み。因果floorの目録拡張(inventory)はREJECTED、known6のみ。

### 3-2. 条件の具体設計(案1/2/5の材料)
入力はreplay上の観察。条件はfixture(35件)への当てはめであり、一般化は未検証。
- 比較(14発火・正当0): 削る/限定。「追加確認へ回す」を基本とし、即重大は維持しない。単独で13件不要。限定条件の候補: Ledger側の事実と数値の比較が実在するときだけ【推測】(`floor_verify_comparison_numbers`/`floor_verify_fact_numbers`相当の決定論は既存、runner L2953/2973)。
- 否定(5・正当0): 限定または追加確認。`absence_only`で発火しているものはフラグ不整合の疑いが高い【確認】(No.2,6,29,32)。
- 時期(8・正当1): 既存の`FLOOR_VERIFY_MODE=time_only`が既に追加確認対象(Trial専用)。決定論のCONFIRMED(factブロックに日付・時刻・期間が無い)を残す価値は高い(維持方向にのみ働く)。
- 主体(6・正当2): 「追加確認トリガー」へ。ただし正当2件(No.5,22)のうちNo.22はLLM自身が重大、No.5はLLM軽微=floor/S1依存。決定論で主体名の集合が元記事に無い固有名詞へ変わった場合のみ強制を残す案(案2の「確定」)。
- 数字(4・正当3): 決定論で残す価値が最も高い。数値不一致はLedger照合で機械確定でき、正当3/4(75%)で最高精度【確認】。
- 因果(1・正当0)/Tier0補助(1・判断不能1): 語彙一致のみ。追加確認トリガー化。
- 全体: 「検出したら即重大」→「追加確認トリガー」へ移すべき条件=比較・否定・因果・Tier0補助。決定論で残す価値が高い条件=数字、時期のCONFIRMED(factブロック不在)、主体の確定ケース。

## 4. 半減・1/3(約12件以下)の達成見込み(in-sample。out-of-sample未検証)
| 案 | 強制重大 | 半分以下(<=17) | 1/3(<=12) | 正当6(強制のまま) |
|---|---|---|---|---|
| 1 | 14 | 達成 | 未達(14>12、約40%) | 6/6 |
| 2 | 8 | 達成 | 達成(約23%) | 4/6強制+2追加確認 |
| 3 | 0 | 達成 | 達成 | 0/6強制(全6追加確認) |
| 4 | 4 | 達成 | 達成 | 4/6はLLM自身+2はS1 |
| 5 | 14 | 達成 | 未達 | 6/6 |

- 【確認】replay上は案1/5で半分以下、案2/3/4で1/3以下。正当6を「強制重大のまま」維持できるのは案1/5のみ(6/6)。
- 【推測】案2/3/4が正当を守れるかは、追加確認の判定精度に依存する。正当6のうちNo.5/21(LLM軽微)は追加確認でBLOCKINGへ戻せるかが鍵。LLM追加確認は未実測(`FLOOR_VERIFY_MODE=time_only`の比較・方向で方向反転が解放された履歴=委任_61)。
- 【推測】案1は条件が35件への当てはめ(in-sample)なので、真の削減率は不確実。数字・主体・時期固有の語彙に依存するため、新記事で再発しうる。
- 【確認】ラベルがRCAの【推測】(Fable/ユーザー未確認)である点が全推計の前提。

## 5. 最有望案(Sonnet所見)と限定Trial案
【推測】最有望: 案2(数字・時期CONFIRMED・主体確定のみ強制、他は追加確認)を、案5の段階化(追加確認の失敗時fail-closed)と組み合わせる方向。根拠=半減(35→約8)で1/3到達、正当6のうち4件は決定論で確定強制を維持、残り2件(No.5/21の一部)は追加確認で守る余地がある。案1単独は正当6/6維持だが1/3未達で、条件が35件への当てはめのため不確実。案3/4は決定論の下限が無くなり、Safetyの根拠が追加確認一本になる。
ただし案2〜4は`APPROVED_FOR_PRODUCTION`済みfloor線引きの変更に当たる(§7)ため、ユーザー承認なしには進めない。

### 限定Trial案(提案のみ。開始しない)
1. 段階0(¥0): E2E保存9 run+段階A保存データでの追加replay。案2の「確定/追加確認」判定条件を固定した上で、35件以外のfloor発火・非発火claimでの再計算(out-of-sample近似、正当の取りこぼし有無)。費用¥0。
2. 段階1(有料、ユーザー承認要): 追加確認対象claim(27件相当)を実LLM確認へ。S1実績¥0.0281/claim(161件)から約¥0.8〜1.5(2回確認で2倍想定)。fresh E2E全体は8run実績¥39.4(うちfloor_verify ¥0.81)が参考で、概算上限はFable/ユーザー決定。
3. 測定項目案(新KPIではない): 強制重大件数/正当6の最終BLOCKING数/不要Rewrite件数/追加確認の降格件数と降格の正当性/コスト。
4. STOP条件案: 正当6のいずれかが最終的に非BLOCKINGになる/追加確認のAPI失敗率が高い/ラベルの再確認で正当件数が変わる/案が`FLOOR_VERIFY_DETERMINISTIC_ONLY_FLAGS`以外のSafety原則追加を要する。

## 6. unresolved
- 判断不能5件(No.11,12,24,30,35)の扱い: 案ごとに行き先は計算済みだが、正当/不要の確定ラベルがない。Fable/ユーザーの確認が必要。
- 24/6/5ラベル全体がSonnet推測(Fable/ユーザー未確認)。ラベルが変わると全案の数値が変わる。
- out-of-sample未検証(35件=E2E保存9 runのみ、案1の条件は当てはめ)。
- 追加確認のLLM精度は未測定。
- Stage 1フラグ不整合(17件)の根本対策(RCA D、Stage 1 prompt)は本docの範囲外で、別途ユーザー承認要。

## 7. APPROVED_FOR_PRODUCTION(未配線)項目への影響
- 【確認】`OPEN_ITEMS.md` L727 `OPEN-233-A1-PROD`: 「時期のみの追加確認(時期`changed_time`のみ2回確認で解放、比較/方向/主体/数値/否定は決定論維持)」が`APPROVED_FOR_PRODUCTION`(ユーザー決定[5回目]2026-10-04、単体確認PASS、`PRODUCTION_WIRED`ではない=approved-but-unwired)。実装は`FLOOR_VERIFY_FLAGS=("changed_time",)`/`FLOOR_VERIFY_DETERMINISTIC_ONLY_FLAGS`(runner L2759/2761)。委任_58〜61の線引きに該当。
- 案0: 影響なし(現行維持)。
- 案1/5: 決定論の内部条件の精緻化。線引き(どのフラグが決定論維持か)の変更には当たらないが、floorの条件変更はA1-PRODの前提(比較/主体/数値/否定は決定論維持)を狭めるため、【推測】Fable/ユーザーの解釈確認が必要。
- 案2/3/4: 比較・主体・数字・否定を「決定論維持」から追加確認/撤廃へ移す=承認済み線引きの変更。ユーザー承認(新決定)なしには実装・Trial不可。委任_61で方向反転が解放された履歴(比較を決定論に戻した経緯)との整合も要確認。
- 他のapproved-but-unwired項目(`OPEN-233-A1-PROD`の他構成要素、`OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01`等)への直接影響は本docの範囲では無し。本doc自体は何もProductionへ配線しない。

## 8. Dangling Reference確認(runner `er052_open233_self_recovery_flow_runner_01.py`で実在確認)
| 名前 | 行 |
|---|---|
| `FLOOR_FLAGS` | L779 |
| `apply_floor` | L2432 |
| `apply_floor_cited` | L2486 |
| `FLOOR_VERIFY_MODE`(既定off)/`FLOOR_VERIFY_MODE_OFF`/`_TIME_ONLY` | L403/L400/L401 |
| `FLOOR_VERIFY_FLAGS` | L2759 |
| `FLOOR_VERIFY_DETERMINISTIC_ONLY_FLAGS` | L2761 |
| `floor_verify_target`/`floor_verify_confirmed`/`run_floor_verify_call`/`floor_verify_evaluate` | L2868/L2984/L3007/L3058 |
| `CAUSAL_FLOOR`(既定False)/`CAUSAL_FLOOR_VOCAB`("known6") | L3254/L3261 |
| `STAGE2_SECOND_OPINION`/`stage2_second_opinion_eligible`/`apply_stage2_second_opinion`/`S1_MATERIALITY_RANK` | L3255付近/L4026/L4045/L4023 |
全て実在。Dangling Referenceなし(本docが新規に作る参照名はなし)。

## 9. STOP条件該当判定(事実のみ)
- 正当6件を守りながら半分以下へ減らす見込み: in-sampleで案1/5が6/6維持かつ14件(40%)=該当せず(見込みあり、out-of-sample未検証)。
- 新Safety原則追加が必要: 案1/5は不要【推測】。案2〜4は線引き変更で、新Safety原則ではなく承認済み線引きの変更(§7)。
- gold定義変更: 不要(gold・Safety-critical定義は不変)。
- 有料Trial: 段階0は¥0。LLM追加確認の実測(案2〜4の検証)は有料Trialが必要(ユーザー承認要)。
- Production仕様変更: 案2〜4は承認済み線引きの変更を伴う(§7)。案1/5はfloor条件の変更でProduction配線時の仕様に影響しうる。

## §10 Opus条件Aレビュー後の訂正・Fable判断(2026-10-06)

(詳細: docs/pm/opus_l2_review_open233_floor_selectivity_01.md。既存本文§0〜§9は書き換えない。)

### §10-(a) 訂正3点
1. §4/§5「案1は6/6維持」はin-sample限定。hold-out(rep30、集計md L69)で案1はneg3 gold(時期floor・LLM非BLOCKING、SC gold b1b)を非強制=見逃し。
2. §2の原因(iii)=0は、集計scriptの`assign_cause`(L207-215)に原因(iii)の分岐がないための構造的な0であり、実際に(iii)が無いことを示すものではない。
3. §5のNo.21はNo.23の誤り。案2で追加確認へ回る正当はNo.5とNo.23(集計md L24, L36, L54)。No.23はLLM BLOCKINGのため`floor_verify_target`対象外(runner L2878)で残り、実際に危険なのはNo.5のみ。

### §10-(b) Opus推奨代替案と順序(要約)
根本原因はStage 1 `changed_*`フラグ生成側(absenceとcontradictionの混同)で、floor側は二次的。Opusは案1/5(正規表現による個別当て込み、過適合)と案4(正当2件を失いうる)を非推奨とした。推奨の優先順:
1. RECLASSIFY-02区分をfloor発火条件に流用(時期以外は「Ledger食い違い」候補でだけ発火、新LLM処理不要)。
2. cite-to-fire(変更されたLedger記述の逐語引用を要求、実在を決定論検証)。
3. Stage 1 prompt補正(RCA案D、recall測定要)。
順序: RECLASSIFY-02評価→段階0(¥0: 35件との突合、`apply_floor_cited`反実仮想集計、SC gold/hold-outのgold取りこぼし0を最優先、11件ラベル確認)→設計確定→ユーザー承認→有料段階1。ユーザー承認要=floor発火条件の変更すべて/Stage 1 prompt・schema変更/有料Trial。承認不要=時期の承認済みverify流用・¥0 replay。

### §10-(c) Fable判断
「Fable判断(2026-10-06、Opus条件Aレビュー後): Status=USER_DECISION_REQUIRED。根拠: (1)Sonnet案(最有望=案2+案5、根本原因=floor側の重大性判定不在)とOpus(根本原因=Stage 1 `changed_*`フラグ生成側のabsence/contra混同、案1/5は正規表現による個別当て込みで過適合、案4は正当2件を失いうる、推奨=RECLASSIFY-02区分のfloor発火条件への流用>cite-to-fire>Stage 1 prompt補正)で重要な結論が対立。(2)Fable検証【確認】: hold-out(rep30、集計md L69)で案1はneg3 gold(時期floor・LLM非BLOCKING)を非強制=見逃し(案1 6/6維持はin-sample限定)/集計scriptの`assign_cause`(L207-215)に原因(iii)分岐がなく(iii)=0は構造的/doc §5のNo.21記述は表(No.23)と不一致。(3)案1〜5・cite-to-fireのいずれも承認済み線引きOPEN-233-A1-PROD(`APPROVED_FOR_PRODUCTION`・未配線、時期のみverify・比較/主体/数字/否定は決定論維持)の変更に当たりユーザー承認事項=ユーザー指定STOP条件『Production仕様変更が必要』に該当。(4)floor側のみの精緻化で正当6件を守りつつ半減する見込みは、in-sampleでは案1/5=14件だがhold-outで1件見逃しのため未確立。Fable評価: Opusの根本原因指摘(フラグ生成側)と順序(RECLASSIFY-02評価→¥0段階0→設計確定→ユーザー承認→有料段階1)を妥当と判断し、ユーザーへ提示。Production未変更、有料Trial未実施、gold不変。」
