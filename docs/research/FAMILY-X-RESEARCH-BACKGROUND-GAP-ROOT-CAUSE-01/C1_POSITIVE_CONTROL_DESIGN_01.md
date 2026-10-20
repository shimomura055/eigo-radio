# C1_POSITIVE_CONTROL_DESIGN_01(C1陽性対照Trial設計。FAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01 委任_02、API 0)

- Status: `C1_EVAL_RETRACTED_POSITIVE_CONTROL_DESIGN_READY_PENDING_FABLE`(本委任の到達上限)。Trial全体の到達上限=`VALIDATED`(Production採用はユーザーのみ)。有料実走は本委任ではしない(委任_03、Fable照合後)。
- 根拠: ユーザー決定2026-10-20(`docs/pm/delegation_log/2026-10-20_FAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01_USER.md` §3 C1 Trial評価是正と追加検証、§4 Writer伝達、§5 最小構成)。C1仕様文(補助指示)は前Trial(`lib.CANDIDATE_NOTES["C1"]`、sha256 `592a13b317d97975…`)を**無改変で使う**。
- 目的: C1は『必要な背景Factを見つけて追加する』核心機能が一度も実証されていない(前Trial 7 call・追加0件)。**Ledgerに背景Factが実在し、通常のB3では選ばれず、追加すべきFactを事後に明確に判定できる**条件(陽性対照)で、C1の核心機能とその副作用(過剰補完・誤帰属・ストーリー性)を検証する。「追加しなかった」結果を成功扱いしない。

## 1 E-1 既存仕様との整合・混同防止(照合したファイル:行)
| 対象 | 照合 | 本Trialでの扱い |
|---|---|---|
| B3採用Fact下限2件 | `CURRENT_SPEC.md:1171`、`OPEN_ITEMS.md` OPEN-420(行932) | **不変**。C1が追加する『背景補完Fact』は下限2件に**算入しない**(前Trial M2、`COMMON_GUARD`文言)。判定は`analyze_selection`の`core_selected_ids`/`min2_met_only_via_supplement`。「下限2件(必須の最小採用)」と「背景補完Fact(任意の追加)」は別概念 |
| 契約V5 / `rules_sha256` | `er053_b3_annotation_contract_01.py:22,219-236`(V5=Selected Facts全行がFACT_LINE_RE一致・番号1..K連続・【事実N】タグのみ)、`er053_b3_deterministic_producer_01.py:708`(`rules_sha256()`) | producer・契約は無変更。追加Factを含む産物も契約検証V1-V10を通ること、`rules_sha256`が不変(`525f2309…`、run_mey_01の`annotation_manifest.json`と一致)であることを`eval.trace_writer_path`で機械確認 |
| B3正式Production仕様(Prompt・schema・4テスト) | `er019_family_x_storyline_b3_fact_selection_01.py`(DEVELOPER_MESSAGE/FACT_TEST_DEFINITIONS_JA/schema)、前Trial TRIAL_DESIGN_01 §3 | **不変**(import再利用、Production 5 moduleのgit diff 0行をtest化: `test_no_env_switch_no_runner_import_and_production_unchanged`)。baselineの送信Promptは`b3.build_user_prompt`とバイト同一、C1はその末尾に補助指示を追記するだけ(testで機械証明) |
| 前Trial VALIDATED(範囲限定) | `TRIAL_CLOSEOUT_01.md` §X(2026-10-20是正節) | 評価撤回済み。確認済み=不必要な追加をしない/不足を記録/ストーリー性維持、未検証=核心機能 |
| REJECTED方式 | TRIAL_DESIGN_01 §7(Select-then-Verify/再選定は費用相殺でREJECTED) | 再導入しない(追加callは作らない。callが増えるのは既存の下限2件再評価のみ) |
| Writer伝達機構の新設 | ユーザー§4(不足メモの伝達機構新設を優先しない) | 新設しない。追加Factが**既存の決定論producer→W-1入力経路**で届くかのみ検証。schema/producer変更が必要と判明した場合は実装せず報告 |

## 2 陽性対照・陰性対照の構成(事前固定。探索の詳細=`C1_LEDGER_CANDIDATE_SCAN_01.md`)

| ID | 役割 | Ledger | 期待core(追加すべき) | 期待ok(追加しても可) | 期待外(追加=過剰補完) |
|---|---|---|---|---|---|
| PC1_hormuz | 陽性 | 既存`family_x_b3_diversity_trial_01/hormuz/run_01`のLedger(12件、sha 83b2a09b、無改変) | **HF-006**(7/13のBrent上昇9.59%と、米国の対イラン海上封鎖・ホルムズ経由エネルギー輸送への懸念との関連。Storylineの『高値に戻った』の前提) | なし | 他の未採用Fact全て(特にHF-004/005/010/011の数値系、HF-012のWTI、HF-008) |
| PC2_mey_positive | 陽性 | `test_ledger_mey_positive_01.txt`(run_mey_01のF01〜F11無改変+実在一次資料のF12〜F14、構成=§3) | **F12**(攻撃主体の帰属=アンサール・アッラー、国連特使の安保理発言と声明) | F13(紅海・海上交易路・エネルギー市場との接続の評価)、F14(UN News要約: 9月のフーシ派攻勢・米イラン戦争の波及) | F01〜F11のうちBaseline観測範囲(F04,F05,F11)外の追加(例: F09/F10を『攻撃主体』の回答にする誤用) |
| NC1_coffee | 陰性 | 既存`coffee_prices/run_l3_01`のLedger(19件、sha a2146bc5、無改変) | なし(追加0が正解) | なし | 追加Fact全て(未採用に背景風Fact 005/006/007/011/012/013が多数あり過剰補完を誘う) |

選定理由と4条件の充足は`C1_LEDGER_CANDIDATE_SCAN_01.md` §2。前Trial(er083)の中東Ledger 11件は背景Factが無いため陽性対照にならない(PC2はその11件に実在Factを足したもの)。補欠: Muse(L6、Storyline文が前提を内包し欠落が成立しないため陽性にしない)。

## 3 陽性対照Ledger PC2の構成記録(実在の検証済みFactのみ)
追加Factは、国連の公式文書(無料HTTP取得、2026-10-20 UTC、HTTP 200)に**書かれている内容のみ**。引用は取得HTMLの本文と**逐語一致を機械照合**済み(`er083_c1_positive_control_01_build_ledger.py`、`quote_check`全true)。架空の主張なし。

| Fact | 内容(日本語要約) | 区分 | 出典(媒体・URL・日付・取得時刻UTC) | 原文引用(要旨) |
|---|---|---|---|---|
| F12 | 特使は、アンサール・アッラーがサウジの民間・エネルギー施設への攻撃を行ったと述べ(アブハ・リヤド空港の最近の攻撃を含む)、10月11日の声明でも継続攻撃をアンサール・アッラーによるものとして非難し停止を求めた | 誰が(E_core) | S1: 国連DPPA、特使発言全文 `https://dppa.un.org/en/press-releases/special-envoy-for-yemens-remarks-to-the-security-council-as-delivered`(2026-10-09、取得01:03:02)/ S4: OSESGY特使声明 `https://osesgy.unmissions.org/en/news/statement-by-un-special-envoy-for-yemen-hans-grundberg-on-latest-attacks-against-saudi`(2026-10-11、取得01:13:11) | S1「Ansar Allah has also carried out attacks against civilian and energy infrastructure in the Kingdom of Saudi Arabia, including recent attacks against Abha International Airport and King Khalid International Airport in Riyadh, which killed and injured civilians.」S4「I strongly condemn the continuing attacks against civilian infrastructure in the Kingdom of Saudi Arabia by Ansar Allah, including the latest attack on 10 October against King Khalid International Airport in Riyadh…」 |
| F13 | 特使の評価: アンサール・アッラーによるサウジ関連の商船への紅海での脅威が、海上交易路の支配をめぐるより広い対立とエネルギー市場の逼迫と絡み合いつつある。中東の不安定とイエメンの動きが相互に影響 | 何の流れ(E_ok、評価。動機の断定ではない) | S1 | 「…These threats are becoming enmeshed with the broader confrontation over control of maritime trade routes and the stresses on the international energy market.」等 |
| F14 | UN News要約: 9月に始まったフーシ派の攻勢が12年の戦争を激化、米イラン戦争の波及、サウジ空港・エネルギー施設への越境ミサイル・ドローン攻撃が同週も継続 | 何の流れ(E_ok、編集要約) | S3: 国連ニュース `https://news.un.org/en/story/2026/10/1168559`(2026-10-09、取得01:03:12) | 「a Houthi offensive launched in September has sharply escalated the 12-year-long war…」等 |

- **VERIFIED付与の根拠**: 一次資料の原文に直接記載(DIRECTLY_STATED)。Production Verifier(LLM)ではなく本Trial作成者が原文と照合した結果(`verification_caveat`に明記)。F13・F14は評価/編集要約であり、帰属(特使の評価、UN Newsの要約)を`conditions`・`notes_for_writer`に明記。原文は動機を述べておらず、Factも動機を主張しない。
- **混入防止**: `is_test_ledger=true`・`test_origin`・`production_use=禁止`をJSONに付与。txtはProduction書式(ヘッダ無し)で`er083_output/c1_positive_control_01/test_ledgers/`のみ。Production run dir・`er019_output`へは書かない。F01〜F11はbyte無改変(testで`startswith`検査)。
- **委任_01との突合せ点**: S2(DPPA news)=run_mey_01のF01の出典URLと同一、S4=F11の出典URLと同一。いずれの原文も攻撃主体を明記する一方、Ledgerの F01・F11 は主体名を含まない(= Research/Ledger化段階の欠落、原因特定は委任_01)。取得記録: `test_ledger_mey_positive_01.json` の `sources`・`source_html_sha256`。
- **PC2の弱点(判断材料)**: F12は本来F11・F01の出典に書かれていた内容で、BaselineのB3もF12を『誰が』として自然に選ぶ可能性がある(その場合`NONDISCRIMINATING`、PC1で判別)。「Baselineで選ばれない」はPC1が強い(8 runで不採用)。

## 4 条件・call数・実行手順(最小構成)
- 条件: {baseline(追記なし=Production同一Prompt), C1}×Ledger{PC1, PC2, NC1}×sample 2 = **B3 12 call**(`c1_posctrl_matrix_01.json`)。sample 2はB3の非決定性の対処(前Trialでbaselineが F04↔F05 に揺れた)。モデル=Production B3のrouting値(`gpt-6.1-sol`、最新世代・Production同一。前Trial実測)、effort high、temperature指定なし。
- 並列化: 12セルは独立。セル単位でプロセス起動(`--cells <ledger:cond:sample>`、各自のcost_log)。直列化理由なし。壁時間≈2分(前Trial実測、最長117秒)。
- Writer W-1: **陽性LedgerでC1セルが期待coreを採用した場合のみ**、そのC1セル1本とbaselineセル1本(同Ledger)=最大4本。既存`er083_b3_background_fact_trial_01_writer_probe.py`(Production `run_w1_writer`をそのまま呼ぶ、契約検証V1-V10は課金前)。陰性LedgerのW-1は不要(追加0なら記事は同一経路)。
- 実走コマンド(委任_03、Fable照合後): `python er083_c1_positive_control_01_run.py --design docs/research/FAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01/c1_posctrl_matrix_01.json --out er083_output/c1_positive_control_01 --cells <ledger:cond:sample> --budget-jpy 12 --paid-run-approved-by-fable`(セル毎)→`er083_c1_positive_control_01_eval.py`(0円)→盲検パック→別processで採点。`--paid-run-approved-by-fable`が無いと有料実走を拒否する(test済み)。

## 5 事前固定の判定基準(実走前に固定。実走後の変更禁止)
**評価6項目(ユーザー§3)と判定方法**
| # | 項目 | 判定方法 | 基準 |
|---|---|---|---|
| 1 | 必要な背景Factを正しく追加するか | **機械**(`judge_ledger`): 陽性LedgerでC1セルの採用IDが期待coreを含む(sample毎)、かつ`【背景補完】`マーカー付き | 2/2 sample=`POS_ADDED_2of2`。1/2=`POS_PARTIAL`(不安定)、0/2=`POS_NOT_ADDED`。Baselineも全sampleで期待coreを採用した陽性Ledgerは`NONDISCRIMINATING`(C1の効果と分離不能、判定から除外し他Ledgerで判定) |
| 2 | 不必要なFactを追加しないか | **機械**: extras = 期待core/ok以外の`【背景補完】`、および(Baseline観測∪過去実績)外のマーカー無し追加。陰性は追加0 | 全Ledgerでextras=0、陰性=`NEG_PASS`。1件でも過剰補完の指摘。陰性での追加は`NEG_FAIL`=REJECTED候補 |
| 3 | 中心Storyline・エンタメ性を維持するか | **盲検rubric**: 前Trial R1_BLIND(軸1: 維持/軽微低下/低下)。同一Ledgerのbaseline記事とC1記事をA/Bに伏せて比較 | C1が『維持』(同等以上)。『軽微低下』=トレードオフ(判断候補)。『低下』=問題 |
| 4 | 選定した背景Factが既存のWriter入力経路に反映されるか | **機械・決定論**(`trace_writer_path`): 採用ID→`annotation.json` facts[].ledger_ids→契約検証V1-V10 PASS→`rules_sha256`不変(V5)。本文使用はキーワード(参考値)+盲検で確認 | trace全項目PASS。契約FAIL=Writer到達不可(schema/producer変更要否を報告、実装しない) |
| 5 | 記事として実際に理解しやすくなるか | **盲検rubric**: 読者テスト。Ledgerを見せず記事のみで質問に答える。PC1=「撤回後もBrentが高値だった背景は?」、PC2=「サウジ施設への攻撃は誰によるものか(誰の発言か)?」 | 正答が記事にあるのがC1記事のみ(または両方でC1が明確)=改善。baselineと同等=改善なし(核心機能の便益未確認) |
| 6 | 誤帰属・根拠のない因果・過剰な網羅化が無いか | **盲検rubric**(文ごとのチェックリスト、許容0): 帰属元(国連特使の発言/UN News要約)の保持、動機の創作なし(F12は動機を述べない)、F13/F14の評価を事実として断定しない、別事案のFact(F09/F10)から主体を結ばない、追加Factが記事の焦点を奪わない | 違反0。1件でも問題(REJECTED候補、修正再検証の対象) |

**盲検の厳密化(前Trialの限界の是正)**: 前Trialは採点者=実行者で、同一コマンドで候補名入りの機械表も生成された。本Trialは (a) パックは`eval --blind-pack`がA/B化し`blind_key.json`は別ファイル、(b) 採点は**別process(別Agent/別session)**で、渡すのは盲検パック・Ledger本文・本rubricのみ(機械表・条件名・trial_metaは渡さない)、(c) 各項目3回独立判定(割れたら低い方)。

**最終ラベルの事前固定**
- **VALIDATED(候補)**: 判別可能な陽性Ledger(NONDISCRIMINATING除く、最低1件)の全てが`POS_ADDED_2of2` ∧ 陰性`NEG_PASS` ∧ extras=0かつ`flags`なし(`MIN2_ONLY_VIA_SUPPLEMENT`/`OVER_MAX_SELECTED`/`CORE_ADDED_WITHOUT_MARKER`/`B3_MIN2_STOP`) ∧ Writer到達trace PASS ∧ 項目5=改善 ∧ 項目3=維持 ∧ 項目6=違反0。→ Fableが`VALIDATED`と分類(Production採用は未承認)。
- **REJECTED(提案)**: 判別可能な陽性が全て追加0(`POS_NOT_ADDED`)、または陰性で追加(`NEG_FAIL`)、かつ原因分析と承認範囲内の修正再検証でも改善見込みなし。
- **修正再検証(委任範囲内、R3)**: `POS_NOT_ADDED`/`POS_PARTIAL`/項目6違反の場合、`fact_tests[].reason`・`recheck_note`から原因を分析し、承認範囲・予算内で補助指示の合理的な修正と再検証を1周(別途Cap)。新構造にならない文言修正は再レビュー不要、構造変更はOpus Gate(11-3)。
- **判断候補**: トレードオフ(例: 追加は成功したが項目3が軽微低下)、schema/producer変更が必要と判明、新仕様・品質基準の変更が必要な場合。**『追加しなかった』を成功としない**(`overall`は判別可能な陽性で追加0なら`REJECTED_CANDIDATE_MACHINE`を返し、VALIDATEDにならない。test済み)。

## 6 盲検rubric(前Trial R1_BLIND流用、差分のみ)
前Trial `TRIAL_DESIGN_01.md` §4(軸1〜5)を流用。本Trialでの対応: 軸1=項目3、軸2(判定の正しさ)=項目1・2(機械)で代替、軸4(事実性・中立性)=項目6、軸5(汎用性)は仕様文不変のため`lib.generalization_report()`が全候補`[]`であることの確認のみ(test済み)。読者テスト(項目5)は本Trialで追加。

## 7 費用見積・Cap案
| 工程 | 内容 | 期待 | Cap案 |
|---|---|---|---|
| R1 | B3 12 call(前Trial実測 7 call=60.722円→平均8.67円/call。lib見積は7.6) | 12×8.67=**104円**(lib見積91円) | 125円(再評価・技術retry余裕: 前Trial実績は両方0) |
| R2 | W-1最大4本(前Trial実測 11.951/10.957円) | 最大4×11.5=**46円**(C1がcoreを採用した陽性Ledgerのみ) | 55円 |
| R3 | 修正再検証1周(必要時のみ、B3×4+W-1×1) | 0〜約47円 | 別Cap(Fable設定) |
| 合計(R1+R2) | | **約150円** | **180円** |

- 委任文の目安(60〜90円、B3≈2〜4円/call)は前Trial実測(8.67円/call、TRIAL_CLOSEOUT_01 §6)と乖離するため、**実測を採用**して見積を上方修正した(判断材料)。実走中は`BudgetGuard`がセル毎に停止。
- 7-7判定: 案件合算(R1+R2 Cap 180)≤300円。R3追加でも≤240円。当日: 既使用49.70円(PLW 委任_02bが最大+200)+本Trial約150円≒400円で日次1,000円以内。承認区分C(承認済みScope・個別Cap内、新仕様なし)。
- 最小縮小案(必要時): 陰性Ledgerのbaselineをsample 1のみ(−1 call)、W-1をC1×baseline各1本に絞る等で約110円。判定の分離性(Baselineの揺れ)を落とすため非推奨。
- 時間: R1壁時間≈2分、R2≈3分、eval 0、盲検採点≈10分。全体≈30分。
- THEME_TAG=`C1_POSCTRL_01`(B3段)。W-1はProduction側のtheme(`FAMILY_X_FACTLOCK_W1_PRODUCTION_01`)が付くが、費用集計(`cost_summary_tree`)はthemeで絞らず実API行を全て数える。

## 8 Opus_Iとの差分(Fableが再レビュー要否を判断する材料)
Opus_I(前Trial設計レビュー、条件A、GO_WITH_CHANGES、`OPUS_REVIEW_I_01_VERBATIM.md`)は『補助指示がストーリー選定を侵食しないか』『不可欠の操作的定義』『Writer・producer契約との整合』『Ledger欠落時の挙動(論点3)』等を審査し、論点3で『陽性対照が無い。VALIDATEDの範囲を非侵食・欠落時の不補完・帰属動機の区別に限定せよ』と明記した。
| 項目 | 前Trial(Opus_I対象) | 本Trial | 新構造か |
|---|---|---|---|
| C1補助指示文 | `CANDIDATE_NOTES["C1"]`(sha 592a13b3…) | **同一(無改変)** | 否 |
| 処理フロー | Production `run_storyline_b3_selection`に追記のみ | 同一(import再利用)。callを増やさない | 否 |
| schema/producer/契約 | 不変 | 不変(V5 `rules_sha256`不変をtraceで機械確認) | 否 |
| 新規要素 | — | (1)陽性/陰性対照のLedger構成(評価データ。仕様でない) (2)機械判定`judge_ledger`/`overall`(評価コード) (3)読者テスト・盲検の厳密化 | 否(評価系のみ) |
| Opus_Iの未解決事項 | 論点3: 陽性対照なし | **本Trialが解消対象** | — |

結論(案): 設計は**Opus_Iの延長で新構造ではなく、再レビュー不要**(11-3条件A非該当)。ただし(a)R3で補助指示の文言修正が構造変更に当たる場合は条件A、(b)同じ問題へ2回修正しても再発する場合は条件B、(c)Production採用提案前は条件C。要否の最終判断はFable。

## 9 リスク・限界
1. **陽性判定の主観性**: 期待coreは実走前に固定したが、『Storylineの理解に不可欠』自体はLLM判断。PC1のHF-006は『撤回と市場反応』テーマの周辺に位置し、C1が「欠いていない」と判断する可能性がある(それが真の挙動なら『不補完』は誠実な結果だが、陽性対照としては`POS_NOT_ADDED`で原因分析の対象)。
2. **PC2の非判別リスク**: F12が強いFactで、BaselineのB3も選ぶ可能性(→`NONDISCRIMINATING`)。PC1の結果と合わせて判定。
3. **n=2/条件**: 微小な効果は検出不能。判定は大きな効果(2/2 vs 0/2)に限定。
4. **dry-run(合成応答)は実LLMの挙動の根拠ではない**。経路(producer・契約・trace・eval)のみの確認。
5. **『背景補完』ラベルは`reason`先頭の転用**(前Trialと同じ)。本番化にはschema変更が必要(ユーザー承認事項、本Trialでは実装しない)。
6. 『補完Factが末尾に来てWriterが補足扱いにする』リスク(前Trial §3)は、PC1/PC2のW-1で初めて観測する。
