# FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11 — Report

管理ID: `FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11`(**Trial扱い、
Production採用なし**)。実施者: Sonnet(sonnet-worker、Fable委任)。
実施日: 2026-09-10。同期実行のみ(バックグラウンド待機・二重起動なし)。
並列稼働中の他タスク(SSOT反映/News Ledger拡充Trial/3V配線)の領域
(`docs/pm/ACTIVE_TASK.md`・`RESULT_PACKET.md`・`OPEN_ITEMS.md`・
`DECISION_LOG.md`・`CURRENT_SPEC.md`・`ARTIFACT_REGISTRY.md`・Production
Prompt・Productionコード)は一切編集していない。Household最終候補
artifact(`er011_output/household_unified_final_candidate_01/`)は比較のため
読み取り専用で再分析したのみで、一切変更していない。Git操作は行っていない。

## エグゼクティブサマリー(10行以内)

Discovery Focus Module(Discovery/Why型記事用Prompt拡張)のPart A本体のみ
(保険文抑制のPart B案1は不使用)を、Household(冷蔵庫クリスパー)とは
別テーマ「洗濯したのに、なぜタオルは臭うことがあるのか?」でN=1検証した。
新規Verified Fact Ledger(査読論文15件、CONFIRMEDのみ)を作成し、A2/B1B各1本
を既存QA一式(Point Role Planning/Value QA/Overlap QA+retry/Fact Checker/
Ledger Deviation/Directional Fact Precheck)を無変更で通した。両レベルとも
最終status=OK、Point Overlap記事全体retry=0回、保険文検出(regex)=0件。
B1BのみLedger Deviation MAJORが2件検出されたが、既存Local Rewrite機構が
1cycleで自動解消(人手レビュー不要)。Fact Checkerはfact_verdict=A2:PASS/
B1B:REVIEW_REQUIRED(いずれもnon-blocking advisory、production既定方針
どおり)。Household最終候補との比較では、Part A単独でも保険文0件・
Overlap値が同水準という結果が得られたが、**N=1であり一般化の確証には
不十分**。Production採用は行っていない(Gate 1=VALIDATED相当)。

## 1. Reconciliation Check(PM_GOVERNANCE 2-1)実施記録

- `er011_household_unified_final_candidate_01_run.py`(Household一本化
  最終候補)を確認し、`prod_gen.build_common_block`/`build_prompt`/
  `run_one_pattern`という同一経路(既存Production関数を無変更で直接呼ぶ)を
  踏襲した。
- `er011_discovery_stage4_cautionary_language_trial_10.py`のPart A単独
  (`current_focus`)条件は、`er011_discovery_stage3_rule_adjustment_
  trial_09.py`(t9)の`CURRENT_FOCUS_BLOCK`を一字一句不変のまま再利用して
  いることを確認した。本Trialも同じ`CURRENT_FOCUS_BLOCK`を無変更でimportし、
  Part B文言(`cautionary_clause`、「取扱説明書」「メーカーの案内」等の語を
  含む1文)は一切追加していない(Gate 4静的確認で機械的に確認、後述)。
- `er011_news_stage3_new_theme_ledger_trial_09.py`(News Trial-09)が新テーマ
  Verified Fact Ledgerを作成した手順(`vfl01.build_researcher_prompt(topic=)`
  /`build_verification_prompt(topic, ledger_parsed)`というtopic引数を明示的
  に渡せる既存関数を使い、`vfl01.run_researcher`/`run_verification`と同一の
  client呼び出し構造をtopicだけ差し替えて再現、VERIFIED[CONFIRMED]のみへ
  フィルタしAMBIGUOUS/REJECTEDは除外)を踏襲した。
- Household固有のVerified Fact Ledger v5はHousehold(冷蔵庫クリスパー)専用
  であり、タオル臭テーマには使えないため、新規Ledgerを作成した(2節)。
- 重複・競合・実装漏れは確認されなかった(新規Trialとして着手)。

## 2. 新規Verified Fact Ledger作成(タオル臭テーマ)

Researcher(Web検索あり)→独立Verification→CONFIRMED(VERIFIED)のみへ
フィルタ、という既存経路(vfl01関数を無変更で直接呼ぶ)で作成した。

- Research方式: `vfl01.build_researcher_prompt(topic=RESEARCH_QUESTION_JA)`で
  「洗濯したのに、なぜタオルは臭うことがあるのか?」という研究質問(結論を
  先取りしない、原因を限定しない中立的な問い)をResearcherへ渡し、Web検索
  (`tools=[{"type": "web_search"}]`、14クエリ)で調査させた。
- Researcher出力: 16件のFact下書き(査読論文・PubMed/PMC/MDPI掲載研究、
  家庭用洗濯機の細菌叢調査、繊維科学の実験室モデル等)。
- Verification結果: VERIFIED=15件、AMBIGUOUS=1件、REJECTED=0件。
  News Trial-09と同一方針(全件CONFIRMED、未検証は載せない)により、
  AMBIGUOUS 1件は本Ledgerから除外し、VERIFIED 15件(F001〜F016、F014欠番=
  Verificationで別factへ統合されずAMBIGUOUS判定となり除外)のみを採用。
- 保存先: `er011_output/discovery_generalization_towels_trial_11/research/
  verified_fact_ledger.txt`(各factにfact_id・claim・scope・conditions・
  numeric_value・causal_strength・出典[タイトル+URL]・notes_for_writerを
  明記、CONFIRMED-onlyフィルタ後)。構造化データは同ディレクトリの
  `verified_fact_ledger_structured.json`。
- 主な出典(査読論文): *A Comprehensive View of Microbial Communities in the
  Laundering Cycle*(MDPI, 2022)/ *Smells Like Teen Spirit—A Model to
  Generate Laundry-Associated Malodour In Vitro*(MDPI, 2021)/ *The
  Bacterial Life Cycle in Textiles is Governed by Fiber Hydrophobicity*
  (PMC, 2021)/ *Analysis of biofilm and bacterial communities in the towel
  environment with daily use*(PMC, 2023、日本26世帯6か月縦断調査)/
  *Bacterial Exchange in Household Washing Machines*(2015)/ *Bacterial
  communities in domestic washing machines associated with user-perceived
  odours*(2026)等。
- Writer用topic(`TOWELS_TOPIC_JA`): Ledger確定後、F008/F009/F010(繊維内
  バイオフィルム形成+26世帯6か月縦断研究)のみを要約して作成(Ledgerに
  無い新しい主張・数字は追加していない)。Household THEMES["household"]
  ["topic"]と同型のstyle(数文+出典注記)。

## 3. Gate 4静的確認

`er011_output/discovery_generalization_towels_trial_11/audit/
gate4_check.json`: **PASS**。Production関数(`THEMES`/`build_common_block`/
`build_prompt`/`A2_KAI1_INSTRUCTION`/`B1_B_DIRECT_INSTRUCTION`/
`run_one_pattern`/`POINT_OVERLAP_ARTICLE_RETRY_MAX`)が再定義・monkeypatch
されていないこと、`{editorial_type_module_block}`placeholderが存在する
こと、使用したブロックが`t9.CURRENT_FOCUS_BLOCK`とbyte単位で完全一致する
こと(Part A本体無変更)、Part B文言(「取扱説明書」を含む句)が含まれて
いないことを機械確認した。

## 4. 記事生成結果(A2/B1B各1本)

既存経路のまま(Point Role Planning/Value QA/Point Overlap QA/Diagnostic
Full Retry[Loop Budget 2]/Fact Checker/Ledger Deviation Checker[Hook-aware]/
Local Rewrite/Evidence Compression/Directional Fact Precheck)。

| Level | 最終status | fact_verdict | ledger_status(最終) | Point Overlap記事全体retry | word_count(compute_metrics) | 保険文(regex) | Local Rewrite | Directional Fact Precheck |
|---|---|---|---|---|---|---|---|---|
| A2 | OK | PASS | LEDGER_COMPLIANT(0件) | 0回(上限2) | 294 | 0件 | 実行なし | DIRECTION_REVIEW_REQUIRED(conflicts=0) |
| B1B | OK | REVIEW_REQUIRED(advisory) | LEDGER_COMPLIANT(0件、Rewrite後) | 0回(上限2) | 419 | 0件 | 1 cycle・2件・両方resolved・human_review=0件 | DIRECTION_REVIEW_REQUIRED(conflicts=0) |

両レベルとも自己判断による再抽選(N追加)は行っていない。記事全文は
`er011_output/discovery_generalization_towels_trial_11/{a2,b1b}/article.md`。

### A2記事全文(`article.md`)

```
# Why a Clean Towel Can Still Smell

Here is the strange part of laundry: a towel can come out of the washer, dry, and still smell like damp cloth.

This pattern appeared in a 2022 survey of 359 households. People reported laundry smells at different stages: 110 households reported a smell before washing, 91 while the laundry was still wet after washing, and 73 after drying. These groups could overlap.

A separate study followed new cotton towels in 26 Japanese households for six months. Smell and a dull look appeared after two months. Researchers also found a growing sticky layer inside the towel threads, especially in the lengthwise threads.

So the mystery is not only what the washing machine removes. It is also what may stay hidden inside the fabric.

### When the fabric changes the route

Cotton and polyester do not behave in the same way. In a lab model, polyester held more skin oil and more bacteria tightly. Cotton held more water, and some bacteria stayed active after drying. In both fabrics, bacteria inside the threads could build a sticky layer that was hard to wash away. So no single fabric alone predicts odor: cotton may keep moisture, while polyester may hold more oil and bacteria.

### A wash is not a simple switch

A wash is not just clean or dirty. At 30 or 40 degrees without bleach, some bacteria survived and moved between fabrics. Active-oxygen bleach reduced more microbes in 30 minutes. At 60 degrees, all tested microbes were reduced. In five home washing machines, nearly all bacterial groups found before washing remained on cotton after a 30-degree cycle without bleach. The same mild process may therefore leave the same problem.

## In one line…

A towel can smell after washing because its fabric and the washing process may leave different ways for bacteria to remain. The quiet lesson is that the answer may lie in the whole process, not simply in repeating the same wash.
```

### B1B記事全文(`article.md`、Local Rewrite適用後の最終版)

```
# Why a Clean Towel Can Still Smell

A towel can come out of the wash looking clean, then give off a wet-cloth or old-rag smell. That smell may be noticed before washing, while the fabric is still wet after washing, or after the laundry has dried, and these stages can overlap.

A 2022 survey asked 359 households about laundry odors. About 110 reported a smell before washing, while fewer noticed one in wet laundry after washing or after the laundry had dried. These groups could overlap, so the numbers are not a rate for all households. But they show that the wash cycle does not always mark the end of the story.

Why can the smell return? In laboratory models using cotton and polyester, bacteria linked with skin oil and sweat could move into the fibers and build a sticky layer called a biofilm. That layer was difficult to remove with ordinary washing, and odor could remain after the wash.

In another cotton-cloth model, a particular combination of three bacteria produced a stronger and longer-lasting wet-cloth smell than single bacteria or other combinations.

A separate six-month study followed new cotton towels in 26 Japanese households. Smell and dullness were already observed after two months. During the study, biofilm structures were seen mainly around the towels' lengthwise threads. The layer's components and the number of bacteria that could be grown in the lab also increased over time.

This was what researchers observed in those homes. It does not mean that every towel will smell after two months.

### When fabric and drying join forces

There is another twist: drying and fabric type work together. In lab tests, prolonged or slow drying was linked with stronger odor, while high-humidity drying was associated with characteristic laundry odor. Polyester held more skin oil and more strongly attached bacteria, while cotton held more water; some bacterial activity continued after drying. Softener-treated cotton also absorbed less water. So the same detergent routine can end differently on different fabrics.

### The washing machine joins the story

Washing is an exchange, not a reset. In tests, bacteria survived and moved between fabrics during bleach-free washing; bleach-containing conditions reduced them more. In five household machines, bacteria moved among water, clothes, and machine surfaces, while prewash groups remained on washed cotton. Machine parts also carried many bacteria. Another comparison found no clear link between total bacterial makeup and machine odor. The towel may be one part of the system.

## In one line…

A clean-looking towel can carry a longer history. In these studies, recurring odor was linked not just to the towel, but to the meeting point of fabric, moisture, bacteria, and the washing system around them.
```

### Local Rewrite詳細(B1Bのみ、cycle 1で全件解消)

| # | 検出フラグ | 元の文(NG) | 修正後 | resolved | human_review |
|---|---|---|---|---|---|
| 1 | changed_fact | "That smell may appear before washing, while the fabric is still wet after washing, or **only after drying**."(「乾燥後のみ」という排他的表現がF001の「重複しうる」記述と矛盾) | "...or after the laundry has dried, **and these stages can overlap**." | True(1回目のattemptで解消) | False |
| 2 | changed_fact, changed_comparison | "longer or more humid drying was linked with **stronger odor**"(湿度が強いほど臭いが強い、という比較をLedgerが直接支持していない) | "prolonged or slow drying was linked with stronger odor, while high-humidity drying was associated with characteristic laundry odor"(比較を分離) | True(1回目のattemptで解消) | False |

Fact Checker(B1B、REVIEW_REQUIRED、non-blocking advisory、3件):(a)柔軟剤
処理綿の吸水性低下の一般化に条件差がある可能性、(b)乾燥条件の強さと臭気の
関係の出典が記事内で明示されていない、(c)"prewash groups remained on
washed cotton"という表現の指示対象が曖昧、の3点。いずれも虚偽・捏造の
指摘ではなく、記述の精緻化余地の指摘(Production既定方針により
non-blocking、記事生成継続)。

## 5. 確認項目10点への回答

1. **Discoveryらしさ/「へえ」があるか**: あり。A2「the mystery is not only
   what the washing machine removes...also what may stay hidden inside the
   fabric」、B1B「A clean-looking towel can carry a longer history」等、
   「見た目は綺麗でも繊維内部に何かが残っている」という予想外の切り口を
   Full Storyで提示している。
2. **Full StoryとPointの役割分離**: 分離できている。Full Storyは
   「臭いの発生パターン(いつ臭うか)+26世帯6か月研究の意外な結果(2か月で
   既にバイオフィルム)」という謎の提示に専念し、Point Oneは素材の物理特性
   (綿とポリエステルの違い)、Point Twoは洗濯プロセス・洗濯機自体(温度・
   漂白剤・機械内の細菌交換)という、Full Storyとは異なる切り口で解説して
   いる。
3. **Point One/Twoの切り口**: 明確に異なる因果メカニズム。P1=繊維の物性
   (疎水性・吸水性の違いによる細菌付着・保持の差)、P2=洗浄プロセスそのもの
   (温度・漂白剤有無・洗濯機内での細菌交換)。B1BのP1はさらに柔軟剤による
   吸水性低下を追加、P2は洗濯機のニオイの有無と細菌総量の相関が弱いという
   意外な知見を追加しており、A2よりやや踏み込んだ切り口になっている。
4. **Point同士の多様性**: `cross_point_overlap`(既存Point Overlap QAの
   出力そのもの、新指標は計算していない)は A2: P1→P2=0.243/P2→P1=0.225
   (flagged=False)、B1B: P1→P2=0.244/P2→P1=0.222(flagged=False)。
   Household最終候補(A2: 0.196/0.289、B1B: 0.183/0.25、いずれもflagged=
   False)と同程度の範囲。
5. **Fact Safety(Fact Checker結果・創作0か)**: A2はfact_verdict=PASS、
   unsupported_specific_claims=0件。B1Bはfact_verdict=REVIEW_REQUIRED
   (3件、4節参照)だが、いずれも虚偽の創作ではなく精緻化余地の指摘であり、
   Production既定方針どおりnon-blocking advisoryとして扱われた(記事は
   status=OKで完走)。
6. **Ledger Deviation**: A2は0件(retry・Local Rewrite発火なし)。B1Bは
   Writer初回出力でMAJOR 2件を検出したが、既存Local Rewrite機構(cycle 1、
   1回のattemptで両方resolved)により最終的に0件・LEDGER_COMPLIANTに到達。
   人手レビューは発生しなかった(4節の表参照)。
7. **Point Value/Overlap QA(結果・overlap値)**: 両レベルとも1回目の
   Point Overlap QAでflagged=Falseとなり、記事全体retry(Loop Budget上限2)
   は0回で完了した(Household A2は1回retryが発生していたのに対し、本Trial
   は両レベルとも0回)。Point Value QA(意味的な新規性判定)もNGは検出されて
   いない(`audit/point_value_qa_attempt0.json`参照)。
8. **A2/B1B整合(Cross-Level Consistency)**: 両レベルとも同一の中核発見
   (繊維内バイオフィルム形成+洗濯プロセス・洗濯機自体の関与)を軸にしており、
   一貫性がある。B1BはA2に無い詳細(3菌種混合実験、柔軟剤による吸水性低下、
   洗濯機のニオイと細菌総量の弱い相関)を追加しており、難易度に応じた自然な
   深化になっている。
9. **不自然な保険文・説明書的表現**: 既存BROAD regex(`(?:check|consult|
   ask|see|refer to|look at|read|follow)[^.!?]{0,80}(?:instructions?|
   manuals?|guides?|guidelines?|manufacturers?|makers?|professionals?|
   experts?|labels?|packagings?|packages?)`、Trial-10 comparison script/
   Household最終候補と同一定義)による検出は**A2=0件、B1B=0件**。記事全文の
   目視確認でも、「取扱説明書を見てください」「メーカーに確認してください」
   のような聞き手への外部情報源確認の呼びかけは見当たらない。**注記**:
   Part B案1(cautionary_constrained、保険文抑制の追加Prompt制約)を使わない
   Part A単独条件でも、本テーマ・N=1では保険文が発生しなかった。ただしN=1
   かつ1テーマのみであり、Part A単独で保険文が構造的に発生しないと断定する
   根拠にはならない(既存SSOT`FAMILY-A-DISCOVERY-SPEC-FINALIZATION-
   RECONCILE-01_REPORT.md`が指摘するとおり、Part A単独でのREVIEW率・保険文
   頻度はHouseholdの過去N=3検証[Trial-09]でも観測されており、本Trialの
   N=1結果はそれと矛盾しないが追加の確証も与えない)。
10. **retry挙動(発火回数・理由・解消)**: Point Overlap記事全体retryは
    両レベルとも0回(上限2)。Local Rewriteは B1Bのみ1cycle・2件発火し、
    いずれも1回のattemptで自動解消(human_review_required=0件)。
    Directional Fact Precheck(暫定機構、ER-008-DIRECTIONAL-FACT-
    PRECHECK-08)は両レベルともoverall_status=DIRECTION_REVIEW_REQUIREDと
    なったが、機械判定できる`conflicts`は両レベルとも**0件**(「片方にのみ
    方向表現があり機械的に一致/不一致を判定できない」という助言のみ、
    non-blocking)。**測定条件の違いに関する注記**: 本Trialは News
    Trial-09の手順に倣い`research/stage_b3_vfl.json`を作成したため、
    Directional Fact PrecheckのLayer 1(`vfl_internal_claim_vs_conditions`)
    まで実行された。一方、Household最終候補側にはこのファイルが存在しない
    ため、Layer 1はスキップされ、Layer 2(`ledger_vs_script`)のみが実行され
    ていた(結果PASS)。したがって「towelsの方がDIRECTION_REVIEW_REQUIREDが
    多い」という見かけ上の差は、記事の質の差ではなく**測定条件(Layer 1の
    有無)の差によるもの**であり、両方とも実際の方向反転(conflicts)は
    検出されていない。

## 6. Household最終候補(HOUSEHOLD-UNIFIED-FINAL-CANDIDATE-01)との比較

Household最終候補のarticle出力(`er011_output/
household_unified_final_candidate_01/{a2,b1b}/`、cautionary_constrained
条件=Part A+Part B案1)を、本Trialと同一の`t9.analyze_run()`(無変更)で
読み取り専用のまま再分析し(Household側artifactは一切変更していない)、
比較可能な指標を得た。詳細JSON:
`er011_output/discovery_generalization_towels_trial_11/
comparison_vs_household.json`。

| 指標 | Towels A2(Part A単独) | Towels B1B(Part A単独) | Household A2(Part A+B案1) | Household B1B(Part A+B案1) |
|---|---|---|---|---|
| status | OK | OK | OK | OK |
| fact_verdict | PASS | REVIEW_REQUIRED(advisory) | PASS | PASS |
| ledger_status(最終) | LEDGER_COMPLIANT | LEDGER_COMPLIANT | LEDGER_COMPLIANT | LEDGER_COMPLIANT |
| Point Overlap記事全体retry | 0 | 0 | 1 | 0 |
| word_count(compute_metrics) | 294 | 419 | 349 | 369 |
| 保険文(regex) | 0件 | 0件 | 0件 | 0件 |
| near_duplicate_sentence_pair | 0 | 1(ratio 0.611) | 1(ratio 0.558) | 2(ratio 0.582/0.641) |
| cross_point_overlap(P1→P2/P2→P1) | 0.243/0.225 | 0.244/0.222 | 0.196/0.289 | 0.183/0.25 |
| Local Rewrite item数 | 0 | 2(全件resolved) | 0 | 0 |

**注意**: Household側は`cautionary_constrained`(Part A+Part B案1)条件、
本Trialは`current_focus`(Part A単独)条件であり、**Focus Module条件が
異なる**。本表は「同じFocus Module条件での新旧比較」ではなく、「異なる
テーマ・異なるFocus Module条件間でも、既存QA一式が同様に機能し、記事が
完走するか」を確認するための参考比較である。保険文0件という結果が両条件
共通だったことは、Part B案1が無くても保険文が出ない場合があるという1点の
観測にとどまり、Part B案1の必要性についての結論を出すものではない。

## 7. 費用

実測合計 **¥117.72**(上限¥150以内、見込み¥30〜80に対しては上振れ。
主因はLedger作成のWeb検索コスト、下記内訳参照)。

| 段階 | 費用(JPY) | 内訳 |
|---|---|---|
| Ledger作成(Researcher+Verification、Web検索14クエリ) | ¥55.48 | openai(gpt-5.6系、web_search_call込み) |
| 記事生成(A2+B1B合計) | ¥62.24 | openai(Writer/Point Role Planning/Value QA/Overlap QA/Evidence Compression/Fact Checker/Ledger Deviation/Local Rewrite/Directional Fact Precheck) |
| **合計** | **¥117.72** | unpriced_records=0、全19レコード |

**既知の制約**: A2とB1Bの記事生成コストは、実装上同一のtheme_tag
(`THEME_ID`)でログしたため、レベル別(A2 vs B1B)には分離できていない
(合計のみ)。次回同種Trialでは、Household最終候補スクリプトと同様
theme_tagにlevelを含める改善が可能(non-blocking、本Trialの結論には
影響しない)。記録: `er011_output/discovery_generalization_towels_trial_11/
cost_summary.json`・`raw_usage_log.jsonl`。

## Gate 1分類

**VALIDATED相当(Trial範囲、N=1)**。A2/B1Bとも記事生成〜既存QA一式まで
完走し、GATE_BLOCKED/HUMAN_REVIEW_REQUIREDの発動なし(Local Rewriteは
既存Loop Budget内で自動解消、human_review_required=0件)。Production採用
(`APPROVED_FOR_PRODUCTION`)は行っていない。一般化の確証にはN増し(複数
テーマ)が必要(既存SSOT`FAMILY-A-DISCOVERY-SPEC-FINALIZATION-
RECONCILE-01_REPORT.md`の推奨どおり)。

## Production採用判断に必要な材料が揃ったか/次のN増しの推奨

**揃っていない(ユーザー判断)**。本Trialは「Household以外の新テーマで
Part A単独が機能するか」というN=1の初回データ点を提供したのみであり、
`FAMILY-A-DISCOVERY-SPEC-FINALIZATION-RECONCILE-01_REPORT.md`が推奨した
「複数テーマ×N=5程度」には遠く及ばない。今回の結果(保険文0件・記事完走・
Fact Safety維持)はPositiveだが、N=1では偶然の可能性を排除できない。
次のN増しを行う場合の推奨(ユーザー判断が必要な提案であり、本Trialでは
実施していない):
- 追加テーマ2〜3件×A2/B1B各N=2〜3程度で、保険文発生率・Point Overlap
  retry率・Local Rewrite発火率のばらつきを見る。
- costは本Trial実測(Ledger¥55.48+記事生成¥62.24=¥117.72/テーマ)を
  ベースに按分見積り可能。

## 既知gap

- `JAPANESE_TITLES`辞書へのタイトル登録は本Trialでは行っていない
  (Support/Audioを実施しないため不要。実施する場合は既存前例[FAMILY-A-
  COMPLETION-A2-TREND-END-TO-END-01]と同様のgapが発生する想定、
  OPEN-137継続既知gap)。
- A2/B1Bの費用分離ができていない(7節既知の制約)。
- Directional Fact Precheckの測定条件差(Layer 1有無)による見かけ上の
  ステータス差(5節item 10注記)。

## Dangling Reference Check

- `editorial_mode="discovery_why"`: 本Trialでも**未定義のまま**使用して
  いない(build_common_blockへ`editorial_type_module_block`を直接渡す方式
  のみを使用、registry登録は行っていない。既存SSOTのOPEN-135/138行の
  「未登録の想定名」という記述と矛盾しない)。
- `current_focus`: `FAMILY-A-DISCOVERY-STAGE4-CAUTIONARY-LANGUAGE-
  TRIAL-10`固有のTrial条件名であり、CURRENT_SPEC.mdの正式仕様名ではない
  (Trial限定の名称、本Reportでも同義で使用)。
- `Verified Fact Ledger`(タオル臭テーマ): 本Trialで新規作成した独自
  Ledgerであり、CURRENT_SPEC.mdやOPEN_ITEMS.mdに版番号としての記載はない
  (Household v5とは独立、混同しないこと)。
- `Point Role Planning`・`Point Value QA`・`Diagnostic Full Retry`・
  `Local Rewrite Loop`・`Directional Fact Precheck`: いずれもCURRENT_
  SPEC.md本体に定義済みの既存Production機構(無変更で使用)。

## QCD(品質/費用/納期)

- **品質**: Production既存関数を無変更で直接呼ぶ経路のみを使用(Gate 4
  静的確認PASS)。分析はHousehold最終候補と同一の`t9.analyze_run()`を
  流用し比較可能性を担保した。
- **費用**: 実測¥117.72(上限¥150以内)。
- **納期**: 単一セッション内で完了(2026-09-10)。

## 成果物一覧

- `er011_discovery_generalization_towels_trial_11_run.py`(root、新規、
  既存Production関数を無変更で直接呼ぶorchestrationのみ)
- `FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11_REPORT.md`(本ファイル)
- `er011_output/discovery_generalization_towels_trial_11/`
  - `research/`(`fact_ledger_draft.json`/`fact_ledger_verification.json`/
    `verified_fact_ledger.txt`/`verified_fact_ledger_structured.json`/
    `stage_b3_vfl.json`)
  - `audit/gate4_check.json`
  - `{a2,b1b}/article.md` / `run_summary.json` / `metrics.json` /
    `length_report.json` / `fact_qa.json` / `ledger_deviation.json` /
    `point_overlap_qa.json` / `point_overlap_article_retry_log.json` /
    `analysis.json` / `audit/`(prompt.txt・writer_attempts.json・
    point_role_planning_initial.json・point_value_qa_attempt0.json・
    fact_check_attempts.json・directional_fact_precheck.json、B1Bのみ
    local_rewrite_cycles.json・local_rewrite_results.json)
  - `comparison_vs_household.json`
  - `cost_summary.json` / `raw_usage_log.jsonl` / `e2e_run_summary*.json`

読み取りのみで参照した既存ファイル(いずれも変更していない):
`er011_household_unified_final_candidate_01_run.py`、
`er011_discovery_stage4_cautionary_language_trial_10.py`、
`er011_discovery_stage3_rule_adjustment_trial_09.py`、
`er011_news_stage3_new_theme_ledger_trial_09.py`、
`er003_v1_n3_01_articles_generate.py`、`er003_v1_en_direct_vfl_01_generate.py`、
`HOUSEHOLD-UNIFIED-FINAL-CANDIDATE-01_REPORT.md`、
`FAMILY-A-DISCOVERY-SPEC-FINALIZATION-RECONCILE-01_REPORT.md`、
`docs/pm/PM_BRIEF.md`、`docs/pm/PM_GOVERNANCE.md`、
`er011_output/household_unified_final_candidate_01/{a2,b1b}/`配下の
既存artifact(analyze_run再分析のための読み取りのみ)。
