# Trial結果 TRIAL_RESULT_01(ユーザー§8の1〜9の順)

管理ID: FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01 委任_01 / 2026-10-21
ユーザー原文: `docs/pm/delegation_log/2026-10-21_FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01_USER.md`(本文3,604字、sha256[本文のみ]=eda27195c7fee0fd3f271d141916d67902f58568e9a0af8abd6195fd02958985)
設計: `TRIAL_DESIGN_01.md` / 事前Gate: `PRIOR_TRIAL_GATE_01.md` / 証跡: `er090_output/b3_core_number_rounding_trial_01/`(`evidence/`に集計)
実装(Trial専用・Production無改変): `er090_b3_core_number_rounding_trial_01_overlay.py`(純関数)/`_run.py`(実行)/`_evidence.py`(集計)/`_test_01.py`(18件PASS)
最終Statusラベルは付けない(Fable判定)。**Production採用・配線なし**(Production module/Prompt/routingのsha無改変、`git status`でProduction .pyの変更0)。

## 1. 過去Trial調査結果(否定的事例の有無)
**STOP該当の否定的結果なし**(詳細=`PRIOR_TRIAL_GATE_01.md`)。承認済みの丸め仕様(Spoken-first Number Treatment CURRENT_SPEC.md:1730、Listener-Friendly Numeric Precision :2096、DECISION_LOG.md:14388「丸めはChecker側でNG扱いしない」)は、判断基準としてそのままPromptへ逐語引用した。設計制約として3点を織り込んだ: (a) Fact Lock Writer数字規則(5)は丸め・「約」追加を禁止(ユーザー承認済み・PRODUCTION_WIRED)=今回は規則(5)への狭い例外化が必要、(b) Family X Productionには旧Fact Checker/LDCは無く(2026-10-10撤去)検査はRisk Flagger=LDCはTrial専用に既存関数で実行、(c) 注記md/sidecarは契約sha検証対象=無改変でoverlayを別ファイル化。

## 2. Trial結果と最終Status(材料)
- 実行: 判断LLM 計9call(v1 Prompt 5call=形式指示不足の改善前、v2 Prompt 4call。semiはv1結果を再利用)、Writer(After)・Writer(Control)・Advanced/Standard(After)・LDC 7call・RF 8call・意味差分judge 4call。
- 機能は目的どおり動作: 記事Aの`最大134,515人`/`134,515人`(中核数値C2)をB3段後の丸め判断が`APPROXIMATE_OK`と判定→Writerへ伝達→JA R0/R1/R2・Advanced・Standardの全段で指定表記が使われ、他の中核数値(11件・3回以上)は厳密値のまま。
- 未解決/要判断(第9項): ①Production適用は承認済み規則(5)の例外化、②判断LLMの実測費用が見積(JPY0.3〜1)を大きく超過、③概数の粗さ(13万 vs 13万5千)がrun毎に揺れ、④Writer出力の「数値以外の差」は再生成揺れと分離できない。
- 判定整合/STOP: なし。Guardrail JPY100に対し実費JPY80.76(超過なし)。

## 3. 丸めたケース・丸めなかったケースのBefore/After
### 3-1 記事A(Writer再生成あり、After=丸め判断あり、Control=概数情報なし再生成、Before=既存Production run)
| 段 | Before(既存Production) | Control(同一Prompt再生成) | After(丸め判断あり) |
|---|---|---|---|
| JA R2 | 「分析によって人数は異なりますが、**最大134,515人**のデータが使われました。…**3回以上**調べた調査」 | 「人数は分析によって異なるが、**最大134,515人**。」(3回以上の記載なし) | 「対象者は**最大約13万人**で、人数は調べる性格の特徴によって異なる。…**3回以上**測定していた。」 |
| Advanced | "as many as **134,515** people" | (EN未生成) | "included **up to about 130,000** people, though the number varied depending on which personality trait was being studied" |
| Standard | "up to **134,515**" + "The number of people was not the same in every study." | (EN未生成) | "included **up to about 130,000** people. The number varied with the personality trait being studied." |
- 「11件/11 studies」「3回以上/at least three times」は全てAfterでも厳密値のまま。`0.0630`はBefore/After共にWriterが記事に採用せず。「最大」(up to)と「解析ごとに人数が異なる」はJA/EN全段で保持。

### 3-2 丸め判断のみのケース(`evidence/judge_table.json`)。期待ラベルは判断前に`TRIAL_DESIGN_01.md`で固定しLLMへ非開示
| # | 出典 | 数値 | 事前ラベル | 判断LLM(v2 high) | 最終(検証後) | 概数(最終) |
|---|---|---|---|---|---|---|
| A1 | 記事A F04 | 最大134,515人/134,515人 | APPROX | APPROX | APPROX | 最大約13万人/約13万人(medium run: 約13万5千人) |
| A2 | 記事A F04 | 11件 | EXACT | EXACT | EXACT | - |
| A3 | 記事A F07 | 3回以上 | EXACT | EXACT | EXACT | - |
| A4 | 記事A F08 | 0.0630 | EXACT | **APPROX(約0.063)** | **EXACT**(V3+V7が降格) | - |
| X1 | coffee F02 | 4.30(米ドル超) | EXACT | EXACT | EXACT | - |
| X2 | coffee F02 | 2025年2月 | EXACT | EXACT | EXACT | - |
| X3 | boredom F06 | 1,332 | APPROX | APPROX | APPROX | 約1,300 |
| X5 | boredom F05/F06 | 5分 / 最大50 | EXACT | EXACT/EXACT | EXACT | - |
| X4(境界) | semiconductor F2 | 295億9,100万ドル | APPROX | APPROX | APPROX | 約300億ドル |
- 事前ラベル9件(境界含む)と最終判断の一致=9/9。ただし**LLM素の判断は8/9**(A4のみ不一致)で、A4はLLMがAPPROXと答えたが決定論検証で降格し最終EXACTになった。
- 判断の安定性(同一記事A、4run): C1/C4=常にEXACT、C2=常にAPPROX(粗さが揺れる: v1×2=13万5千+説明文付き[形式違反]、v2 high=13万、v2 medium=13万5千)、C5(0.0630)=3/4がEXACT、1/4がAPPROX(降格)。
- ラベル未登録の判断(参考。人手adjudicationなし): 9.14→約9.1、41%→約40%、634→約600、167億ドル→約170億ドル(Ledgerが既にCEO丸め値)、221％→約220％、54％→約50％、約348億ドル→約350億ドル(Ledger値が既に約付き)、3%/10セント刻み=EXACT。**54%→約50%、約348億→約350億は「既に概数のFactをさらに丸める」「粗い(有効1桁)丸め」であり、承認済み条件(意味・比較・閾値を損なわない)の範囲で通常の四捨五入だが、ユーザーが望む粒度かは未確認**(第9項)。

## 4. B3の数値判断とWriterへの伝達結果
- 判断LLMの出力(記事A、v2 high、`judge/A_rep1/overlay.json`): C2のみAPPROX、reason「重要なのは大規模な解析標本であることで、1人単位の精度は結論や証拠の解釈を左右しない。最大という限定と、解析ごとに参加者数が異なる条件は維持する」、根拠Fact=F04、該当条件=Spoken-first/Listener-Friendlyの「意味・比較・閾値を変えない範囲で概数」。
- Writer R0 Promptの差分(`evidence/structural_diff_evidence.json`の`r0_prompt_diff_added_lines`): 「Writerへの注意」ブロックへ2行追記(`- 事実2について：【概数表記】「最大134,515人」は「最大約13万人」と書いてよい。書く場合はこの表記に限り、他の丸め方や別の数字にはしない。`ほか1行)+規則8を1項追記のみ。削除行0。
- 伝達結果: R0本文=「最大約13万人」→R1→R2→Advanced→Standardで全段維持(上表)。欠落・重複・誤適用: 指定表記以外の丸め(例: 13万5千)=0、EXACT数値(11件・3回以上)の誤丸め=0、周辺数値の混入=0、`【`/「概数」の出力漏れ=0(`r0_meta.json` marks_echoed=0、全文grep)。
- 検証による安全網の作動: v1 PromptでLLMが`approx_surface`に説明語を足した(例「最大約13万5千人（解析ごとに参加者数は異なる）」)→V4が全件降格(fail-closed)。Prompt形式指示を直したv2で解消。v2でLLMが0.0630を`約0.063`(末尾の0を落とすだけ=丸めでない)と答えたケースもV3/V7が降格。

## 5. Fact選定・中核数値選定・その他のB3情報が不変である証拠
(`evidence/structural_diff_evidence.json`、API 0)
- 採用Fact ID・件数・順序: Before=After=[F02,F04,F07,F08,F15](B3は再実行せず`storyline_b3`/`research_ledger`の16ファイルをbyte copy、全sha一致=`all_b3_ledger_files_equal: true`)。
- 中核数値の対象・件数・順序: Before=After=[C1:11件, C2:{最大134,515人,134,515人}, C4:3回以上, C5:0.0630]。sidecar numbers/facts完全一致。注記md sha一致、契約検証`validate_annotated_b3`が複製に対してPASS(=注記・sidecar・manifest無改変)。producer rule_version=deterministic_v2.0不変。
- storyline・Fact本文・writer_constraints(既存部分): 完全一致。Writer入力の差分=追記2行+規則8のみ(`r0_prompt_diff_limited_to_overlay_and_rule8: true`、削除0)。
- Beforeの入力再現: 既存Production runのR0 Promptを再構成したshaが`r0_meta.json:r0_prompt_sha256`(c55bb432…)と一致、Control実使用Promptも同sha=ControlはProduction同等。
- 概数可0件のとき: Writer Promptは従来とバイト一致(test `test_exact_only_prompt_byte_identical` PASS=DefaultOffIsolation相当)。
- Production module sha: `er053_family_x_factlock_ja_writer_01.py` = a81bf9ae…(Production entry_point記録と一致)。

**限界(正直な記述)**: Writerの自然言語出力(JA/EN)は再生成毎に変わる。ブラインド意味差分judge(`semdiff/`): After vs Before=NUMBER_EXPRESSION差1件(minor)+FACT_CONTENT差(年齢調整追記・測定条件の書き分け等、minor中心。P4のStandardのみmajor 2件=「人数差の単位」「年齢調整の追記」でどちらも採用Fact範囲内)+構成/比喩差。**同種のFACT_CONTENT差は丸め情報なしのControl vs Beforeにも出ており(major 3件、Controlは「3回以上」を落とす等)、数値表現以外の変化は丸め判断が原因とは言えず、再生成のばらつき**。つまり「数値表現以外に変化がない」はWriter出力では証明できず、構造的に証明できるのは「入力差分が丸め情報に限定されること」まで。

## 6. Fact Safetyの検査結果(`check/`, `semdiff/`)
| 対象 | LDC(既存関数、hook_aware=True) | 備考 |
|---|---|---|
| After Advanced | LEDGER_COMPLIANT、deviation 0 | changed_number=false |
| After Standard | LEDGER_COMPLIANT、deviation 0 | changed_number=false |
| After JA R2 | LEDGER_DEVIATION 1件(MAJOR, changed_causality) | 見出し「収入が増えると、まじめになる？」の因果の問い。**数値とは無関係**。Control JA/Before JAはCOMPLIANTで、Writer再生成のhook文差 |
| Before Advanced(基準) | LEDGER_DEVIATION 1件(MAJOR, changed_scope、比喩文) | 既存Production記事の既存逸脱(数値無関係) |
| Before Standard / Before JA / Control JA | LEDGER_COMPLIANT | |
- **7検査すべてで`changed_number`=false**。「約13万人」は元値134,515の通常の四捨五入(有効3桁135,000でなく有効2桁130,000)で、Ledger Deviation Checker v2が数値逸脱と判定しないこと(CURRENT_SPEC.md:2096の既知結果)を本記事でも再確認。
- Risk Flagger(Production検査、非Blocking、4条件): After Advanced=flag 0、After Standard=3件(信頼度0.38/0.34/0.70: いずれも「3回以上」文、勤勉性の文、「お金が性格を変えるとは言っていない」文で、**概数化した人数の文はflagされず**)。Before既存RF=Advanced 1件/Standard 4件。丸めによるRF増加なし(RFは確率的で同一入力でも変動)。
- 単なる文字列差分と意味が変わるFact差分の区別: 文字列差「134,515→約13万人(-3.4%)」は、LDC(changed_number=false)・意味差分judge(NUMBER_EXPRESSION、severity=minor、「Yも採用Factの134,515人の概数として妥当」)・決定論検証V3(通常四捨五入)の3者が意味差でないと一致。Fact Safety上のNGなし。
- 旧Fact Checker(各段の台帳照合)は2026-10-10にProductionから撤去済みのため実行不能(`er053_c2_old_checker_removal_test_01.py`)。LDCとRFで代替。

## 7. 仕様変更案(追加・変更箇所)
最小構成(Productionへ適用する場合のdiff見積。今回は未適用):
| # | 箇所 | 内容 | 規模 |
|---|---|---|---|
| S1 | 新規 `er053_b3_core_number_rounding_01.py`(仮名) | 判断Prompt(承認済み3ブロックを`er003_v1_n3_01_evidence_compression_editor`から逐語import)・JSON schema・決定論検証V1〜V7・overlay生成。Trial実装=`er090_..._overlay.py` 366行 | 新規約250行(Trial実装を流用) |
| S2 | `er019_family_x_entertainment_production_runner_01.py:466`(`run_annotation_producer(out_dir)`の直後) | `run_core_number_rounding(client, out_dir)`を1行呼出、`storyline_b3/rounding_overlay.json`を書く(契約sha対象外の新規ファイル)。失敗時=overlay空(no-op、非Blocking)で従来Prompt | +約8行 |
| S3 | `er053_family_x_factlock_ja_writer_01.py:331`(`news_text = annotated.news_field_text`)と:350(`build_r0_prompt`) | overlayがあれば「Writerへの注意」ブロックに追記行を足し、Promptへ規則8を1項追記。overlay shaを`runtime_evidence`へ記録 | +約25行 |
| S4 | `runner:294` `load_reused_ja_text` の来歴照合 | overlay shaも来歴に含める(stale検知、U-1と同型) | +約5行 |
| S5 | `er053_family_x_factlock_ja_writer_01.py:98,102` `MARK_RE`/`TAG_LEAK_RE` | `【概数表記】`をWriter出力の漏れ検査・除去対象へ追加(Production TTSへ漏れる安全網。Trialでは漏れ0を確認のみ) | +2行 |
| S6 | test | DefaultOffIsolation(overlay無し=従来Promptとバイト一致)、V1〜V7、構造diff、漏れ検査。Trial testの流用 | 約150行 |
| S7 | CURRENT_SPEC/DECISION_LOG | Fact Lock数字規則(5)の例外(【概数表記】指定のみ、Writer自身の丸めは引き続き禁止)、B3段後の丸め判断(判断基準=Spoken-first/Listener-Friendly承認文言) | 記録のみ |
追加するPrompt文(Trialで使用した原文): 追記行=`- 事実{n}について：【概数表記】「{exact}」は「{approx}」と書いてよい。書く場合はこの表記に限り、他の丸め方や別の数字にはしない。` / 規則8=`8. 「Writerへの注意」に【概数表記】として指定された数字は、規則5の例外として、指定された表記で書けます(書くかどうかは文脈次第です)。指定のない数字は規則5のとおり、丸めたり「約」「およそ」を足したりしません。` 規則5本文・B3 Prompt/schema・producer・契約・R1/R2 Promptは無変更。
QCD見積(実測):
- 追加LLM: 1call/記事(gpt-6.1-sol)。**実測JPY4.30(effort high、記事A、入力3,869tok/出力1,911tok)、JPY2.95(medium、出力1,068tok)**。設計時見積(JPY0.3〜1)は過小。70円/記事に対し **+4.2%〜+6.1%**。所要+19〜55秒(直列)。
- 品質: 記事A 1本・Writer1サンプルでの効果は「人数1箇所が聞き取りやすくなる」のみ。聞き取り評価(音声)は未実施。
- 費用削減候補(未検証): effort low、`reason`/`approved_condition`出力の削除(出力-約35%)、判断対象が0件/全て日付・閾値の記事での省略、より安価なmodel(未Trial)。

## 8. QCD(今回のTrial)
- 品質: 事前Gate・構造不変・伝達・Fact Safetyは上記のとおり。弱点=判断LLMの粒度揺れとA4型のflip(決定論検証で救済)、Writer出力の差分切り分け不能。
- 実行時間(API待ち実測): 判断LLM 1call=19〜55秒、Writer R0〜R2=223〜234秒(After/Control並列)、Advanced+Standard約2分、LDC+RF約3分・意味差分judge約3分(並列)。
- Trial費用: **JPY80.76**(見積JPY35〜45を超過。超過要因=意味差分judge JPY16.83[見積2→過小]、判断LLM計JPY35.70[v1 Prompt失敗分JPY21.95を含む]、Control Writer JPY13.50、After Writer+EN JPY11.24、LDC/RF JPY3.49)。Guardrail JPY100以内、日次はS0の306円→387円(日次1,000円以内)。内訳=`evidence/cost_by_stage.json`。
- 量産単価: 上記+JPY2.95〜4.30/記事(要判断)。

## 9. 残存課題とProduction採用に必要なユーザー判断
判断候補(Fableがラベル付与):
- D1(承認済み仕様の変更): Fact Lock数字規則(5)「丸め・約の追加禁止」(CURRENT_SPEC/DECISION_LOG:20533, ユーザー承認)への【概数表記】例外の追加。本機能の前提であり、Productionでは必ずユーザー承認が必要。(区分: D 新しい判断)
- D2(原価): +JPY2.95〜4.30/記事(+4〜6%)を許容するか、削減Trial(effort/出力/model)を先に行うか。(区分: D。量産単価70円目標との関係)
- D3(品質水準): 概数の粗さの下限(130,000か135,000か)、既に概数のFact(約348億・167億)や有効1桁への丸め(54%→50%)を許すか。承認済み条件は「意味・比較・閾値を損なわない範囲で通常の四捨五入」とだけ定め粒度は未規定。独自に追加していない。(区分: D)
- D4(価値): 記事A 1本では「中核4件中1件が聞き取りやすくなる」効果で、聞き取り評価は未実施。採用可否の価値判断。
残存技術課題: ①n=1記事・Writer 1サンプル(再生成揺れ)②意味差分judge/判断LLMは同一モデル系列(gpt-6.1-sol)でバイアス残存。使用モデル=Production同一(比較目的)。最新性: リポジトリ内の最新上位モデル(`er006_model_routing_contract_01.py`)で、ベンダー公式ページ確認は未実施=未確認③V7などの追加検証は承認済み条件の機械化であり新基準ではないが、Productionでは設計レビュー要④Review Queue/RFでの運用観測は未実施。
SSOT整合: CURRENT_SPEC.md:1730,1177,2096,DECISION_LOG.md:14388,20533,20547、OPEN_ITEMS(OPEN-126,100)と整合確認(矛盾なし、D1のみ要承認の例外)。CURRENT_SPEC/DECISION_LOGは変更していない(採用判断後)。
