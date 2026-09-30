# Opus L2 Review #3 — OPEN-233-SELF-RECOVERY-TRIAL-01

管理ID: OPEN-233-SELF-RECOVERY-TRIAL-01
日付: 2026-09-30
種別: L2 #3 (read-only)
runtime evidence: `claude-opus-5[1m]`(system prompt記載のまま、推測なし。
ユーザー指定の`claude-opus-5-5`はClaude Code 2.1.272未対応のため、
利用可能な最新Opusで実行)

以下、Opus L2レビュー#3の全文を一字も変えず保存する。

=== Opus L2 レビュー #3 全文 ===
## 0. runtime evidence
自認モデル名=Opus 5 (1M context) / exact model ID=`claude-opus-5[1m]`(system prompt記載のまま、推測なし) / knowledge cutoff=2026年5月。read-onlyで実施、編集・実行・API呼び出しなし。ユーザー指定の`claude-opus-5-5`は未使用(Fable報告のとおり利用可能な最新Opusで実行)。

---

# 論点1. R3'の「Safety側誤降格2件」(A2A3-1 / A4-2)

【所見】**2件とも rubric の穴ではなく、較正harnessの正解ラベル(ground truth)の欠陥です。** しかも「粗いbundle」という説明より深刻で、**同一評価セット内で同じ内容のclaimに矛盾するラベルが付いています。**

1. 正解ラベルの作り方が循環参照です。A2A3/A4/A5群の正解ラベルは人間が付けたものではなく、**Stage 1 (V4A) の過去出力で`severity_final=="BLOCKING"`だったdeviationを機械的に全部BLOCKINGとみなしたもの**です。つまり「Safety側誤降格0件」という受入条件は、事実上**「Stage 2はStage 1に一度も反対してはならない」**という条件になっています。これは今回のユーザー指示(Stage 1の過剰検出を自然な解釈基準で是正する)と正面から矛盾し、この条件が達成されないのは当然です。

2. A2A3-1の内容は、同じ評価セットで**ACCEPTABLE**が正解とされているB1-bと実質同一です。
   - A2A3-1: "with its distant danger reaching gasoline prices and the cost of moving goods through crude oil."(HF-006)
   - B1-b(正解=ACCEPTABLE): 「原油価格が高い状態が続けば、ガソリンや輸送費など、私たちの身近な価格にも影響する。」
   同じ「原油高→ガソリン・輸送費」を、片方はACCEPTABLE正解、片方はBLOCKING必須としています。ユーザーNG列挙(人物・数字・出来事・具体的行動の追加/意図断定/逆因果/actor・number・negation・comparison・timeの重大変更/メカニズム捏造)のどれにも該当しません。**私の独立判定: A2A3-1はBLOCKINGであるべきでない(QUALITY相当)。R3'のQUALITY判定が正しく、正解ラベルが誤り。**

3. A4-2: "One helper meant one more person handling private data."(MUSE-HC-010)。V4Aの理由は逐語で「可能性を確定的な結果に変えています」= **certainty強化**です。ユーザーNG5項目にcertaintyは含まれず、委任_12で`changed_certainty`をfloorから外した方針そのものです。同じMUSE-HC-010を扱うB4-bは正解QUALITYです。**私の独立判定: A4-2もBLOCKINGであるべきでない。R3'のQUALITY判定が正しい。**

【Evidence】
- `C:\Users\tensh\eigo-radio\er052_open233_self_recovery_stage2_calibration_01.py:361-372`(A2A3/A4/A5の正解ラベル自動生成: `devs = [dv for dv in v4a["parsed"]["deviations"] if dv.get("severity_final") == "BLOCKING"]` → 全件 `correct_label="BLOCKING"`)
- 同ファイル `:278-279`(B1-b 正解ACCEPTABLE)、`:313-317`(B4-b 正解QUALITY)
- `C:\Users\tensh\eigo-radio\er051_output\open233_checker_trial_01\trial_02\step1\A2A3\V4A\run_1.json:99,112-113`
- `C:\Users\tensh\eigo-radio\er051_output\open233_checker_trial_01\trial_02\step1\A4\V4A\run_1.json:67,80-81`
- `C:\Users\tensh\eigo-radio\er052_output\open233_self_recovery_r3_natural_calibration_01\summary_r3prime_natural_calibration.json:10-13,566-602`

【Safetyリスク】低。2件とも実害claimではない。**むしろ危険なのは逆方向**で、「誤降格0件」を目標に据え続けると、達成のためにrubricを機械的にfail-closed側へ寄せる圧力が生まれ、論点2のB4-d退行のような副作用を今後も再生産します(実際に今回それが起きています)。

【Cost影響】直接は0。ただしこの誤ったSafety基準がR3'採用を招き、R3'が正常記事へ不要Rewriteを1件生んでいます(論点3、neg1で約¥1.73/instance)。

【推奨案(優先順位)】
1. **(最優先・¥0)** A2A3/A4/A5群の正解ラベルを、V4A出力の機械コピーではなくNG(a)〜(e)に照らした人手ラベルへ置き換える。最低限、A2A3-1とA4-2の2件をQUALITYへ再ラベルする(§7-0-iter4の再ラベル作業がB1-c/B4-dで止まっており、Safety群に適用漏れ)。
2. 「Safety側誤降格0件」という受入条件を、**「Safety-critical claim(A2A3-0 / A4-0 / A4-1 / A5-0 / A5-1 / Meta-1 / Meta-2 / hormuz-HF009 / B3 / B4-a)の降格0件」**という明示リストへ限定し直す。全群一律ではなく、claimを名指しする。
3. rubricへ足す文は**不要**(穴ではないため)。追加するならR3'の是正ではなく論点2の緩和のみ。

【USER_DECISION_REQUIRED該当】非該当(Trial内の評価ラベル修正、Production不変)。

---

# 論点2. B4-d退行(R3 vs R3' の最終採否)

【所見】**B4-d退行はランダムなブレではなく、R3'追記1が構造的に引き起こした必然です。** そして**R3'追記2はユーザー自身が許容例として挙げた表現を撃っています。**

- R3'追記1(逐語): 「Ledgerが確認していない人物の内心・信念・認識…を、状況から推測できるからといって確定した事実として述べている場合。」
- B4-d: "Meta had run a test that produced exactly this kind of surprise."(= 人が実際に**驚いた**と述べる)→ **「驚き」は内心**なので、追記1に素直に該当してしまいます。素のR3ではB4-dはQUALITY 2/2(正解一致)でしたが、R3'で2/2 BLOCKINGへ反転しました。
- R3'追記2(逐語): 「…それを『**市場全体**』『価格全般』のようなより広い対象・範囲へ一般化して述べている場合」→ ユーザーが許容例として明示した「**市場が**海上リスクを重視したから価格が戻った」型(=B1-c)に構文的に当たります。実測でもB1-cは素のR3でQUALITY 2/2(正解)だったのが、R3'で1/2 BLOCKINGへ不安定化しました。

【Evidence】
- `C:\Users\tensh\eigo-radio\er052_open233_self_recovery_stage2_calibration_01.py:161-175`(R3'追記本文)、`:307-309`(B4-d claim本文)
- `summary_r3_natural_calibration.json:110-120`(B4-d: QUALITY/QUALITY)、`:435-441`(B1-c: QUALITY/QUALITY)
- `summary_r3prime_natural_calibration.json:107-121`(B4-d: BLOCKING/BLOCKING)、`:55-70`(B1-c: BLOCKING/QUALITY)

【B4-dの独立判定】ユーザー基準に照らすと**QUALITY**です。Ledger(MUSE-HC-006)は「訓練された契約スタッフがMuse経由の一部の電話を担当するテストを実施」を確認済みで、「そういうテストがあった」という出来事自体は追加されていません。追加されているのは「(利用者が)驚いた」という反応の断定=certainty/内心の強化であり、新しい人物・数字・出来事・具体的行動ではありません。**「出来事の追加」には当たらない**と判断します。

【どちらの誤りが学習者にとって重大か】
- R3の誤り(Meta-1/Meta-2/hormuz-HF009/A4-1の降格): **重大**。Brent先物だけの観測を「市場全体/原油価格全般」へ広げる、開示がなかった件で「利用者はAIだと思っていた」と断定する——これは英語学習者が事実として誤って覚える種類の誤りです。
- R3'の誤り(B4-d/B1-c/neg1の過剰BLOCK): **重大度は低いが実害は発生済み**。読み物の掴み(hook)を破壊し、記事を平板化します(論点3・6に実物Evidence)。

【推奨(優先順位)】**R3'を捨ててRに戻すのでも、R3'をそのまま使うのでもなく、R3'の2追記を「原則で」狭めたR3''を推奨します。** 例示ではなく原則で書く、最小の2文:

1. 追記1の置き換え案:「他者の内心を断定する記述のうち、**それが『知らされていたか/同意していたか/誤認していたか』という開示・認識の有無そのものを事実として述べる場合**はBLOCKINGとする。驚き・関心・安心などの一般的な感情や反応の描写にとどまり、誰が何をしたかという事実関係を変えないものはQUALITYとする。」
2. 追記2の置き換え案:「**Ledgerが特定の指標・銘柄・期間について観測した数値や値動き**を、より広い対象(市場全体・価格全般など)の**観測事実**として述べ替える場合はBLOCKINGとする。市場参加者や読者が何を重視していたと**みられる**かという見方・関心の記述は、これに当たらない。」

これにより A4-1(利用者の誤認の断定)・Meta-1/Meta-2・hormuz-HF009(観測値のscope拡大)はBLOCKINGのまま、B4-d(驚き)・B1-c(市場の見方)はQUALITYに戻ります。**追加コスト¥0(rubric文言のみ)**。ただし再較正1回(26 call、実績¥3.8〜4.1)が必要です。

【USER_DECISION_REQUIRED該当】非該当。ただし委任_12は「1回限りの再較正」枠を使い切っているため、**再較正をもう1回行う承認**はFable/ユーザー判断事項です。

---

# 論点3. 正常記事の不要Rewrite 44.4%(4/9)の層別特定

【所見】**4件の発生層はバラバラで、うち少なくとも1件は「不要」ではありません。実質は2〜3件(22〜33%)で、44.4%は過大報告です。**

| instance | BLOCKING確定層 | Evidence | 私の独立判定 |
|---|---|---|---|
| neg1_meta_b3prod_a2 | **Stage 2 R3'(floor不発)**。追記1(内心=surprise)が発火 | `summary_flow_runner.json:3722-3761`(`"floor_reason": null`, `llm_materiality: BLOCKING`) | **不要**(B4-dと同一claim族) |
| neg2_meta_refresh_a2 | **Stage 2 R3'(floor不発)**。追記1(利用者の認識)が発火 | 同`:3960-3999`(`floor_reason: null`) | **不要寄り**。開示がなかったことはLedger確認済みで、「知らなかった」は自然な導出。ただし「enjoyed the ease of AI」は装飾 |
| neg3_hormuz_prodrunner_b1b | **deterministic floor: changed_time**(LLM判定に関わらず強制) | 同`:4109`(`"floor_reason": "deterministic_floor:changed_time"`) | **境界**。「continued」を「returned」にした点は軽微な矛盾。重大なtime変更ではない |
| neg5_hormuz_div_a2 | **Stage 2 R3'(floor不発、因果`So`)** | 同`:4305-4344` | **不要ではない**。この文はB3(正解BLOCKING、NG(d)逆方向因果)と**同一文**。§12-2の再ラベル表自身がB3をBLOCKING維持と決めている |

**neg5の正解ラベル矛盾(重要)**: neg5でRewriteされたclaimは "Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14. So the flashy 20% plan left the stage." で、B3のclaim(`er052_open233_self_recovery_stage2_calibration_01.py:297-302`、正解BLOCKING)と同一文です。したがって**neg5を「不要Rewrite」に数えるのは、プロジェクト自身の再ラベル表と矛盾**します。

**もう1つの測定妥当性の問題**: 較正(作業B)とフロー実測(作業C)は同一rubric・同一model・同一入力構造(Stage 2へはclaim_text/local_context/origin/related_fact_idのみ渡り、Stage 1のissue/explanationは渡らない=anchoringなし。`er052_open233_self_recovery_flow_runner_01.py:571-597`、`er052_open233_self_recovery_stage2_calibration_01.py:210-227`)にもかかわらず、**neg2は較正でACCEPTABLE 2/2、フローでBLOCKING。neg5は較正でACCEPTABLE 2/2、フローでBLOCKING。** つまりStage 2判定は同条件でもrun間で反転します(n=3で2:1)。§12-3の「Stage2由来5claim」はこの不安定性の実運用再現であり、rubric較正の数値がフローへ転移しないことを意味します。

【Safetyリスク】不要Rewriteは直接のSafety低下ではありませんが、**Rewriteが新たな逸脱を生む経路**があるため間接的リスクです。iter4では`rewrite_new_precheck_findings_total=0`(iter3は4件)で、この点は改善しています(`summary_flow_runner.json:182`)。

【Cost影響】4件の合計 ¥1.7296+¥0.9404+¥0.6304+¥0.5052 = **¥3.81**(全体¥28.56の13.3%)。neg2/neg3はRewriteしたうえでStage 4へも行くため二重の損失です。

【推奨案(優先順位・最も安い順)】
1. **(¥0、最優先)** 論点2のR3''(2文の原則置換)。これ**だけ**でneg1は解消見込み(B4-dと同一族)、neg2も追記1の縮小で解消見込み。→ 4件中2件が消える。
2. **(¥0)** floorの精密化を「Stage 1のフラグが立っている」ではなく「**Stage 1が矛盾するLedgerの具体値(numeric_value / date_or_period / 明示claim文)を名指しできている場合のみ**」へ限定する。現行floorはLLMが立てたフラグを無審査で絶対化しており、§4-3が謳う「Ledgerとの矛盾が機械的に一意」という前提を満たしていません(neg3がその実例: `ledger_field_basis`は`ledger_fact`で具体フィールド不明、HF-009に矛盾する日付・期間はない)。→ neg3が消える。実装は`apply_floor()`(`er052_open233_self_recovery_flow_runner_01.py:562-568`)に条件を1つ足すだけ。**ただしこれはSafety装置の緩和方向**なので、採否はユーザー判断を仰ぐべきです(下記UDR参照)。合成変異fixture(safety_er009_*)はLedger値を直接書き換えているため、この条件でもfloorは全件発火し続ける見込みです。
3. **(¥0)** 「Stage 2にStage 1を反証する権限をfloor外categoryで与える」案は、**現行実装で既にそうなっています**(floor不発時はStage 2のQUALITY/ACCEPTABLEがそのまま通る)。追加不要。むしろ必要なのは**Stage 2判定の安定化**であり、そのための最小策は「Stage 2でBLOCKING、かつfloor不発、かつclaimがnegative/Normal群」の場合のみ**同一Stage 2を2回呼んで両方BLOCKINGのときだけRewriteへ進む(2-of-2 requirement)**。追加費はStage2単価(≈¥0.2)×BLOCKING claim数のみで、記事あたり+¥0.2程度。安定化効果は大きいはずです(neg2/neg5とも2:1で割れている)。
4. Stage 1 (V4A)側のseverity規則変更は**非推奨**。Stage 1はProduction資産であり、Trial内で触ると比較可能性を失います。

【自然な解釈なのにBLOCKした件数(私の判定)】**9件中2件が明確(neg1、neg2)、1件が境界(neg3)。= 22%〜33%。報告の44.4%は neg5 の誤計上により過大。**

【USER_DECISION_REQUIRED該当】推奨案2(floor条件の精密化)は**7条件④「既存安全装置の無効化・変更」に該当します**。Trial内部の実装であってもfail-closed装置の緩和なので、ユーザー承認を得てから実施すべきと判断します。推奨案1・3は非該当。

---

# 論点4. neg2/neg3 の unconfirmed → Stage 4

【所見】**追加1 callの再確認は既に実装済みで、2件とも再確認でも解消できていません。** 原因は「表記の不一致」ではなく、**指摘されたclaimが記事の別の箇所に残っている(B1/A4型のmulti-location問題)**である可能性が高いです。

- 実装: `er052_open233_self_recovery_flow_runner_01.py:1586-1601`(overall_status=LEDGER_COMPLIANTかつall_prior_issues_resolved=Falseのとき確認callを1回追加)→ `:1617` で`unconfirmed_after_reverify`。neg2/neg3とも`recheck_confirm_all_prior_issues_resolved: false`(`summary_flow_runner.json:4044-4046, 4154-4156`)。総call数は各4(確認call込み)。
- neg3の実物を読むと、Rewriteされたのは記事末尾の「In one line」1文だけで、**H1見出し "The 20 Percent Fee Plan Is Withdrawn—But Oil Prices Quickly Return" と本文の "the numbers quickly regained their earlier strength" / "events continuing at the same time do not simply disappear" は無編集のまま残っています**(`summary_flow_runner.json:4150`)。つまりprior issueは実際に未解消です。Checkerは正しい。
- 一方で**Checker出力自体が内部矛盾**しています: `overall_status = LEDGER_COMPLIANT`(逸脱なし)なのに `prior_issues_resolved = false`(前回指摘は未解消)。flowはこの矛盾を毎回fail-closedで処理しており、本来は矛盾の正体を確かめるべき箇所です。
- prior_issues promptは**旧claim文・issue・explanationしか渡さず、「どこをどう直したか」を渡していません**(`er003_v1_en_direct_vfl_01_generate.py:678-693`)。

【Safetyリスク】現状の挙動は**安全側で正しい**ため、ここを単純に緩めるのは危険です。「delete型は機械検証でresolved扱い」案は、neg3のように**別箇所に同じ主張が残っているケースを取り逃がす**ので採用すべきではありません(neg3が反例)。

【Cost影響】確認call1回 ≈ ¥0.2/件。現状は2件で約¥0.4の純損(結局Stage 4行き)。

【推奨案(優先順位)】
1. **(¥0、最優先)「cite-or-release」**: 確認callのschemaに `remaining_sentence`(未解消と判断する根拠として、**現在の記事本文中に実在する文をそのまま引用**)を必須項目として足す。引用文が現記事に実在すればStage 4へ(正しい)、実在しなければresolved扱い。fail-closedを緩めず、根拠のない未解消を機械的に排除できます。既存の確認callにフィールドを足すだけなので追加call数0。
2. **(低コスト)** prior_issues instructionに **Rewrite前後の対象文ペア**(before→after)を添える。モデルが消えた文を探し回る必要がなくなり、判定精度が上がります。追加call数0、入力token微増のみ。
3. **(設計)** neg3の真因はmulti-location(§11-9(a)の「fact_id単位マルチ箇所一括Rewrite」)。これはiteration 5のスコープとしては大きく、Rewrite品質リスク(論点6)も増やすため、**iteration 5では見送り、Phase 2設計課題**とすることを推奨します。
4. **非推奨**: 「delete型は機械検証でresolved」「prior_issuesの表記をRewrite後の文へ更新」——どちらもneg3型の実在する未解消を隠します。

【USER_DECISION_REQUIRED該当】推奨案1・2は非該当(fail-closedを緩めず、判定根拠を厳格化する方向)。推奨案3は仕様拡大のため該当し得る。

---

# 論点5. S1-U の維持

【所見】**新許容線の下でもS1-Uは正当です。ただし救っているのは1種類の欠陥だけで、それはもっと安く獲れる可能性があります。**

- S1-Uの真陽性2件(`bgroup_B2_hormuz` / `hormuz_run02_advanced`)は、いずれも**同じ欠陥**でした: Ledger(HF-009)がBrent先物についてのみ確認している値動きを、"crude oil prices stayed high" と**原油価格全般へ拡大**した記述。R3'追記2(=論点2で私が原則化を提案した条項)が正面から捉える、真のBLOCKINGです。B2群の較正claim(正解QUALITY)とは別のclaimなので、混同はありません。
  - Evidence: `summary_flow_runner.json:2199-2221`(B2、`s1u_additional_block_label: "true_positive"`)、`:3632-3654`(hormuz_run02_advanced)、`:387-390`
- 偽陽性3件(neg4/neg6/neg7)は**Stage 2が安価に降格**して止めており、Rewriteにもescalationにも至っていません(`summary_flow_runner.json:4173, 4405, 26-90 quality_claims`)。
- コスト実態: `s1u_variant.extra_cost_jpy = 2.9661`、`screen_used_count = 7` → **¥0.424/screen、7/29 instanceでのみ発火**。反実仮想の総差額は¥4.1622(下流Rewrite費込み、全体の14.6%)。**記事単位では約¥0.18/記事**で、論点提示の「¥0.9/記事固定」よりかなり小さい実測です(Evidence: `summary_flow_runner.json:107-113, 346, 378`)。

【Safetyリスク】外すと、この2件は「escalationにも上がらない静かな見逃し」になります(§12-4の指摘は正しい)。

【Cost影響】¥0.18/記事は+¥3/記事Capに対して無視できる規模。

【推奨案(優先順位)】
1. **維持**(Trial既定として)。費用対効果は実測で裏付けられています。
2. **(¥0、併走推奨)** 救っている欠陥が単一クラス(観測値のscope拡大)なので、**決定論的なlexical pre-check**(Ledgerのfactが特定指標[Brent/先物/特定期間]に限定されているのに、記事が"oil prices"/"the market"/"prices in general"等の広域語を使っている箇所を機械検出)をiteration 5で¥0試作し、S1-Uの2件を再現できるか比較する。再現できればS1-Uを「Advanced段のみ」へ縮小、または廃止できます。
3. 「effort medium + 2 call union」は委任_11の作業Cで既に比較済み(採否条件未達)。**再検討の価値は低い**。

【USER_DECISION_REQUIRED該当】非該当(Trial内既定の維持。Production defaultの変更は別途ユーザー判断)。

---

# 論点6. Phase 2 前条件と読み物品質

## 6-A. 前回提示4条件の充足状況

| 条件 | 判定 | 根拠 |
|---|---|---|
| (i) 機構起因Escalation 0〜1/29 | **境界・未達寄り** | 機構起因2件(neg2/neg3、`unconfirmed_after_reverify`)。ただしneg3は実質multi-location(angle起因)とも読めるため1〜2件 |
| (ii) negative Stage 4 = 0 かつ読み物品質確認 | **未達** | negative Stage 4 = 2件。読み物品質は下記6-Bのとおり**劣化を確認** |
| (iii) JA/EN乖離閉鎖 | **改善したが未閉鎖・かつ§12で未報告** | iter4: `ja_en_equivalence_fail_count = 0`(iter3はFAIL 1)、REVIEW_REQUIRED 6/9。`rewrite_new_precheck_findings_total = 0`(iter3は4件)。**この改善はREPORT §12に一切書かれていません**(報告漏れ、Evidence: `summary_flow_runner.json:181-187`) |
| (iv) 測定是正 | **未達(重大)** | **iter4のフロー実測はinstanceあたりn=1に戻っています**(29 instance_results、`_n2`は0件)。iter3の§11-4は「fresh-mode 3件すべてでsample1とsample2のfinal_stateが一致しなかった」と実証済みで、そこからn=1へ戻しています。したがって「real_run Escalation 16.67%→0%」という§12-3の目玉改善は、**run間分散の範囲内で説明でき、改善の証明になっていません**。しかも real_run 6件のうち3件はstage1_mode=reuse(固定artifact)です |

**これが最大の指摘です**: §12-3の差分表(STAGE4 5→3、real_run 16.67%→0%、loop_rate 0.31→0.28)は、すべてn=1同士の比較です。iter3自身が「単発runのEscalation率・recall率は測定として不十分」と結論づけた直後に、その測定方式へ戻っています。

## 6-B. 読み物品質(Rewrite前後の実文を読んだ一次所見)

読み比べページのHTMLではなく、証跡jsonの`en_text_before_rewrite`/`after`を直接読んで判断しました。**決定論的指標(文数・hedge語数・段落数)は今回の劣化をほぼ検出できていません。**

1. **掴み(hook)の破壊 — neg1、最も深刻**
   - before: `# We Thought It Was AI—But There Was a Person Inside Meta's Muse` / 「Ring, ring. A call seemed to come from an AI agent. But as the conversation went on, the voice was not AI at all. It was a person.」
   - after: `# Meta Tested Human-Handled Calls Through Muse` / 「Meta tested having trained contract workers make some calls through Muse.」
   - タイトルと冒頭3文(記事のストーリー装置そのもの)が消え、プレスリリース調の1文に置換されました。`degradation_candidate: true`は立っていますが、検知理由は文数-3のみで、**失われたものの本質(物語の入口)を表していません**。Evidence: `summary_flow_runner.json:3801-3802`
2. **同内容の段落が2つ並ぶ重複欠陥 — neg1 cycle 2**
   - after本文に「Meta tested having trained contract workers make some calls through Muse.」の直後に「Meta had tested having trained human contractors handle some calls made through its AI agent Muse.」が続きます。**ほぼ同一内容の段落が連続**しており、明白な編集事故です。cycle 2の`degradation_candidate`は**false**(文数・段落数・hedge数がすべて変化なしのため)。Evidence: `summary_flow_runner.json:3933`
3. **接続の破断 — neg2**
   - 「People who asked Muse to make a call might think AI was doing it.」と「If this was not explained clearly, users could not know if it was AI or a person.」を削った結果、段落が **"But sometimes, a human was speaking instead."** という**先行文のない逆接**で始まります。`degradation_candidate: false`。Evidence: `summary_flow_runner.json:4040`
4. **CEFRレベルの上昇(学習コンテンツとして逆行) — neg3 / neg5 / B2 に共通**
   - neg3(A2想定)の「In one line」: before「The fee plan left the stage, but the events driving oil prices—and the prices themselves—quickly returned.」→ after「After the announcement replacing the fee plan, Brent futures briefly pared gains before returning to near pre-announcement highs; concerns about attacks, the blockade and tanker safety continued.」
   - B2: after「…Brent futures briefly **pared their gains** after the announcement before returning to near their **pre-announcement high levels**.」
   - `pared gains` / `pre-announcement highs` は金融記事の語彙で、A2/B1学習者向けの一行まとめとして明らかに過剰です。**Rewriteは正確性を上げる代わりに、系統的に語彙難易度を上げ、1文を長くしています。** これらは全件`degradation_candidate: false`。Evidence: `summary_flow_runner.json:4150, 2262, 4385`

**結論(読み物品質)**: 現在の品質劣化検出(文数/段落数/hedge語数/タイトル変更)は、**今回実際に起きた4種類の劣化(hook喪失・重複段落・接続破断・語彙難化)のうち3種類を検出できていません**。§12-8が挙げる「劣化候補12件」は大半がSafety群のfloor経由であり、**本当に読み物として壊れた実例(neg1 cycle2の重複、neg2の破断、neg3/neg5/B2の語彙難化)は候補リストに入っていません**。品質指標そのものが未検証です。

## 6-C. Phase 2 の最小設計と残¥248の配分(提案)

**現時点でPhase 2(Production相当10〜20記事)へ進むのは時期尚早と判断します。** 理由: (a) 改善の証明がn=1比較に依存、(b) 読み物品質の劣化が実在し検出器が機能していない、(c) rubricがユーザー許容線と2箇所で衝突している。

仮に前条件を満たした後の最小設計案(参考):
- 記事数10(Advanced/Standard両方=20 instance)、**n=2必須**(iter3の実証により単発は不可)。
- Stage 1モデルA/B(gpt-5.6-luna Production vs gpt-6-luna Trial)は**Phase 2の主目的に含めず、別の小規模shadowへ切り出す**(混ぜると原因分離ができない)。
- 記事単位Cap計測は既存`article_level.aggregates`で可(実装済み、worst ¥2.924)。
- shadow(Production記事に対して判定のみ行いRewriteを適用しない)を先に5記事だけ回し、BLOCKING率と読み物影響の事前見積りを取る。

残¥247.84の配分案:
- iteration 5(rubric R3''再較正 26 call + フロー29 instance × n=2): 約¥40〜70
- 読み物品質評価の作り直し(人手読み比べ、API ¥0〜5)
- Phase 2 shadow(5記事): 約¥20
- Phase 2 本番(10記事 n=2): 約¥60〜80
- 予備: 残り

---

# 論点7. 報告の信頼性(抜き取り照合)

instance jsonおよびsummary_flow_runner.jsonと§12の記載を5点照合しました。

| # | 報告値 | 実測json | 判定 |
|---|---|---|---|
| 1 | STAGE4 3件(safety_A4 / neg2 / neg3) | `final_state`走査で STAGE4_ESCALATION は該当3件のみ。`final_stop_count: 3`、`stage4_reason_breakdown: {cycle_limit_exhausted:1, unconfirmed_after_reverify:2}` | **一致** |
| 2 | 群別 safety 1/12・b_group 0/4・meta 0/2・hormuz 0/4・negative 2/7、real_run 0/6 | `group_escalation_rates`(`:114-145`)と一致。各instanceのfinal_stateからも再構成一致(12+4+2+4+7=29) | **一致** |
| 3 | 不要Rewrite 4/9=44.4%(neg1/neg2/neg3/neg5) | `unnecessary_rewrite`(`:190-200`)と一致。Normal群2=hormuz_run03_advanced(ACCEPTABLE_STAGE1、Rewrite 0)/meta_run03_advanced(STAGE2_DOWNGRADE、Rewrite 0)で整合 | **数値は一致。ただし分子の妥当性に問題(論点3のneg5誤計上)** |
| 4 | escalation_zero_breakdown 25/20(quality_pass 5、unconfirmed 0)、worst記事¥2.924、worst instance safety_A4 ¥4.2956 | `:20-25`、`:179`、`:1877` と一致 | **一致** |
| 5 | R3 誤降格5件(Meta-1/Meta-2/hormuz-HF009/A2A3-1/A4-1)、一致率82.61%(38/46);R3' 2件(A2A3-1/A4-2)、80.43%(37/46);作業B ¥7.8974 | `summary_r3_natural_calibration.json:9-20` / `summary_r3prime_natural_calibration.json:7-18` と完全一致 | **一致** |

**発見した報告上の齟齬(いずれも軽微、または報告漏れ)**:
- §12-4の「追加費¥4.1622」は**反実仮想の総差額**(下流Rewrite費込み)で、S1-U screen自体の費用は`extra_cost_jpy = 2.9661`です。両者が別物であることは§12に書かれていません。
- **§12にJA/EN等価QAとRewrite由来逸脱QAの結果が記載されていません**(実測では FAIL 0件、REVIEW 6/9、新規precheck finding 0件 = いずれもiter3から改善)。改善の取りこぼし報告です。
- **§12-3の差分表がn=1同士の比較であることが明記されていません**(論点6(iv))。

【総じて】数値集計そのものは**instance jsonと一致しており、改竄・計算誤りは検出されませんでした**。問題は数値の正確さではなく、**分子の定義の妥当性(neg5)と、単発サンプル比較であることの未明示**です。

---

# 【総合】

## iteration 5 の最小変更セット(コスト昇順、すべて¥0の実装+再較正費のみ)

1. **[必須・¥0]** 較正セットの正解ラベル是正: A2A3-1 と A4-2 を QUALITY へ再ラベル。「Safety側誤降格0件」の受入条件を、名指しした Safety-critical claim 10件の降格0件へ限定。(論点1)
2. **[必須・¥0実装+再較正26 call ≈ ¥4]** R3'の2追記を**例示から原則へ書き換えたR3''**(論点2に文案)。「内心の断定」は開示・認識の有無に限定、「scope一般化」は観測値に限定し、市場の見方の記述を除外する。
3. **[推奨・記事あたり+¥0.2程度]** negative/Normal群かつfloor不発でStage 2がBLOCKINGのとき、**Stage 2を2回呼び 2-of-2 でのみRewriteへ進む**(判定の非決定性対策。neg2/neg5はいずれも2:1で割れている)。(論点3-3)
4. **[必須・¥0]** 確認callへ `remaining_sentence` 必須項目を追加する **cite-or-release**(fail-closedを緩めず、根拠なき未解消を排除)。(論点4-1)
5. **[必須・¥0]** 品質劣化検出の作り直し: (a)連続段落の類似度による**重複検出**、(b)段落先頭の**孤立逆接語**検出、(c)Rewrite前後の**平均文長・難語率**比較、(d)タイトル・第1段落の変更は常にフラグ。現行4指標は実害3種を取りこぼしています。(論点6-B)
6. **[必須・実測]** フロー29 instanceを **n=2** で再実行し、差分表をn=2同士で比較し直す(iter3の実証に従う)。概算 ¥55〜60(iter4 ¥28.56 の約2倍)。
7. **[保留]** floorの「Ledger具体値の名指し必須」化(neg3対策)は**ユーザー承認待ち**とする。
8. **[見送り]** fact_id単位マルチ箇所一括Rewrite(neg3/B1/A4の真因)はPhase 2設計課題へ。

概算: iteration 5 総額 **¥60〜70**(残¥247.84に対して十分)。

## Phase 2 へ進んでよいか

**現時点では進むべきでない**と判断します。前条件4つのうち、(ii)negative Stage 4=0と読み物品質は未達、(iv)測定是正は**後退**しています。(i)は境界、(iii)は改善したが未閉鎖かつ未報告です。特に「real_run Escalation 0%」という最も心強い数字が単発サンプルであり、iter3の実測(3/3でsample間不一致)がこれを直接否定しています。この状態でProduction相当10〜20記事へ進むと、¥60〜80を使って再び「n=1の運」を測ることになります。

## 率直な到達見立て

- **良い方向に進んでいます。** iter4でSTAGE4が5→3、記事worst ¥2.924(Cap内)、Rewrite由来の新規逸脱0件、JA/EN FAIL 0件、そして現行Production STOP実例(hormuz_run02_advanced)がRewriteで解消——これらは本物の前進です。ユーザーの許容線の再設計そのものも正しい判断だったと思います。
- **ただし残っている壁は2つで、性質が違います。**
  - 壁1(解けそう): rubricの言葉づかい。R3'はユーザーの許容線を2箇所で踏み越えており、原則へ書き直せば不要Rewriteの半分は消える見込みです。iteration 5で対処可能。
  - 壁2(構造的): 「1つのclaimが記事の複数箇所に散らばる」問題(B1/A4/neg3/hormuz_run03_standard)。段落単位ローカルRewriteという設計選択の限界であり、rubric調整では解けません。ここは**fact_id単位の一括Rewrite**を設計に入れるか、「この型は人間Escalationでよい」と割り切るかの**ユーザー判断**が要ります。KPI「Escalation 0」を字義通り達成するなら前者が必要で、それはRewrite範囲を広げる=読み物品質リスクを上げる方向です。
- **最も過小評価されているリスクは読み物品質です。** 「Escalation 0」に最適化すればするほど、記事は「安全だが読み物として痩せた」方向へ寄ります。neg1の実例(タイトルと冒頭のRing, ring.が消え、同内容の段落が2つ並ぶ)は、Fact的には完全に正しくなったが英語学習コンテンツとしては明確に劣化した、という典型です。**この軸をKPIに入れない限り、フローは「壊れていないことに気づけない」まま進みます。**
- 到達見立て: iteration 5(上記1〜6)で不要Rewrite率は22%→10%前後、機構起因Escalation 0〜1/29は現実的と見ます。Phase 2着手はiteration 5の n=2 実測後が妥当です。予算残¥247.84はこの計画に対して十分です。

## USER_DECISION_REQUIRED(7条件)該当まとめ
- **④既存安全装置の無効化・変更に該当**: iteration 5 推奨7(deterministic floorの発火条件を「Ledger具体値の名指しがある場合のみ」へ限定)。実施前にユーザー承認が必要と判断します。
- **その他(ループ上限/Production採用/仕様拡大/Production・既存証跡変更/予算超過/3連続APIエラー)は非該当**。
- なお、Opus診断はループ上限(管理IDあたり1回)の枠組み上、本件が#3である点はFable側で上限管理をご確認ください(私からは判断しません)。
- 参考: 委任_12は「1回限りの再較正」枠を使い切っているため、**R3''の再較正をもう1回実施する承認**はFable/ユーザー判断事項です。

## 入力範囲について
今回の診断に必要な事実は、指定された範囲(REPORT §12、design §4-3/§9-2、er052 iter4・R3較正の証跡json、flow_runner/stage2 calibrationのコード)で充足できました。追加で読んだのは、判定に不可欠だった `er051_output/open233_checker_trial_01/trial_02/step1/{A2A3,A4}/V4A/run_1.json`(A2A3-1/A4-2の実claim本文)と `er003_v1_en_direct_vfl_01_generate.py:678-705`(prior_issues promptの中身)です。読み比べページHTMLは開いていませんが、同じ内容の一次データ(証跡jsonのRewrite前後全文)を直接読んでいるため、読み物品質の所見に欠落はありません。
=== Opus L2 レビュー #3 全文 ここまで ===
