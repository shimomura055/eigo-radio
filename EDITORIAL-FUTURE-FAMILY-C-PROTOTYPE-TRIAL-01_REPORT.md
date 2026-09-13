# EDITORIAL-FUTURE-FAMILY-C-PROTOTYPE-TRIAL-01_REPORT.md

管理ID: EDITORIAL-FUTURE-FAMILY-C-PROTOTYPE-TRIAL-01
性質: 新Family C(Future、独立経路、1人ナレーター)の¥0試作・offline検証→
費用見積→上限¥300内での記事生成Trial。**Production採用・配線の承認では
ない**(Gate 1判定材料のみ)。既存Production経路(A-Family/B-Family)・
並行中のDiscovery Trial成果物・SSOT本文は無変更。Git操作は行っていない
(成果物は本ファイル・`er013_*`新規ファイル・`er013_output/`のみ)。
Status: **VALIDATED(Trial完走、Gate 1判定材料あり)**。

## 0. ユーザー確定判断(原文、再確認不要)

冒頭の管理ID仕様に転記済み(「Future: 既存のA-Familyへの新型追加案は
採用せず…」「Futureで記事生成Trialが必要なら、費用上限300円で実施して
構いません…」)。

## 1. 出発点

`EDITORIAL-FUTURE-ARTICLE-DESIGN-01_REPORT.md`(推奨案は当初「案A:
A-Family新型」だったが、ユーザー最終決定により**案C(Family C、独立
経路)**へ変更)、`er013_future_article_design_draft_01.md`(Ledger 3層
規約・Future Focus Module文面draft)を出発点として、Family Cを新規実装
した。

## 2. 実装ファイル一覧(全て新規、既存ファイル無編集)

| ファイル | 役割 |
|---|---|
| `er013_family_c_future_ledger_01.py` | 3層Ledgerスキーマ(`[PRESENT_FACT]`/`[FUTURE_ASSUMPTION]`/`[IMAGINED_FUTURE]`)。Layer1は既存Verified Fact Ledgerをタグで囲むのみ(無変更)。Layer2/3はLLM1回で生成、`based_on`/`grounded_in`のgrounding検証関数を含む。 |
| `er013_family_c_future_writer_01.py` | Family C独立Writer Prompt構築+生成。A-Family共通Prompt(Main Story/Point One/Point Two/In One Line固定)・B-Family(複数Voice前提)のどちらにも依存しない。`[[IMAGINED: <timeframe>]] ... [[/IMAGINED]]`マーカー規約を定義。 |
| `er013_family_c_future_qa_01.py` | マーカー抽出・Layer1限定テキスト生成(Fact Check/Deviation Check向けプレースホルダ化)・マーカー除去(読者向け本文)・heuristic一次スクリーニング(現在事実紛れ込み/枠外未来断定)・新設Future Framing QA(LLM、Layer2/3専用)。 |
| `er013_family_c_future_qa_test_01.py` | offline(¥0)unit test 22件。`run_project_regression.py`(pattern: `er0*_test_*.py`)から自動探索される。 |
| `er013_family_c_future_trial_01_run.py` | Trial driver(実API呼び出し)。stage: `ledger`/`layer23`/`a2`/`b1`/`evaluate`/`cost`。既存Production関数(後述)をimportし無改変で呼び出す。 |
| `er013_output/family_c_future_trial_01/` | 実行成果物一式(research/a2/b1/comparison.md/index.html)。 |

### 既存Production関数の再利用(import・無改変)

- `er003_v1_en_direct_vfl_01_generate`(vfl01): `get_client`/`MODEL`/
  `REASONING_EFFORT`/`build_researcher_prompt`/`build_verification_prompt`/
  **`run_deviation_check`(既存Ledger Deviation Checker、`hook_aware`既定
  False=Trial呼び出し、Production側の`hook_aware=True`とは別呼び出し)**。
- `er002_ja_web_research_r3`(r3): `build_fact_check_prompt`/
  `make_fact_checker_fn`/**`run_fact_checker_with_gates`(既存Fact
  Checker A'。内部で`parse_and_validate_fact_check_output`まで適用済みの
  `(parsed, final_status, attempts_detail, model_id, response_id,
  search_usage, sources)`を返す)**。
- `er010_ledger_local_rewrite_09`(rewrite09): `split_sentences`/
  `locate_target_sentence`/`extract_point_context`/**`rewrite_ng_item`**/
  `apply_rewrites`(既存Local Rewrite、無改変。**cycle上限のみProduction
  [3]より保守的な1へ制限**=安全側の変更であり緩和ではない。上限まで
  解決しなければNG_REVIEW_REQUIREDとし、人手レビューへ回す)。
- `er006_model_routing_contract_01`(routing): `require_model
  ("WRITER_FACT_CHECK", ...)`(Fact Checker A'呼び出し時のみ、既存
  Approved Modelを使用)。
- `er005_cost_logger`: `install`/`logging_context`(既存費用計測)。

Layer2/3生成・Future Framing QAは新設のTrial専用process(既存
`PROCESS_MODEL_MAP`に未登録)のため、`routing.require_model()`は使わず
Trial-11等の前例と同様に`vfl01.MODEL`(Approved Model
`gpt-5.6-luna`と同一値)を直接指定した(SSOT routing契約ファイルへの
新規process登録・改変は行っていない)。

## 3. offline検証結果(¥0、API呼び出しなし)

`.venv/Scripts/python.exe -m unittest er013_family_c_future_qa_test_01 -v`
→ **22 tests, OK**(marker抽出・balance検証・reader本文のマーカー除去・
Layer1プレースホルダ化で想像内容が漏れないこと・現在事実紛れ込み
heuristic・枠外未来断定heuristic・Ledger grounding検証・3層Ledger組立て・
Writer Prompt構築+レベル別guidance+不正レベルでの`ValueError`、を検証)。

## 4. A/B-Family無影響確認

- `run_project_regression.py --pattern "er013_*_test_*.py"` →
  collected=22 passed=22 failed=0。
- `run_project_regression.py`(default全件、pattern `er0*_test_*.py`)→
  **collected=2484 passed=2481 failed=3**。失敗3件は本Trialと無関係な
  既存の履歴カウント照合テスト(`er003_test_p2j_investigate.py`の
  `test_combined_equals_sum_of_er002_and_er003`等、過去のtest総数
  スナップショットとの照合が長期的なファイル増加でズレる既知の性質の
  もの。差分は2484 vs 1823のような大きな乖離であり、本Trialで追加した
  22件のtestとは無関係)。本Trialの新規ファイルはA-Family/B-Family/
  Discoveryのどのファイルもimport・改変していないため、影響経路は
  存在しない(静的にも確認済み)。

## 5. 費用見積(実行前、作業B)

実測前の見積: Research+Ledger Verification(既存実測パターン
¥55〜60)+Layer2/3整理(LLM1回、軽量)+Writer A2/B1各1本+Fact Checker
A'(Layer1のみ)+Ledger Deviation(Layer1のみ)+Future Framing QA(新設)+
Local Rewrite retry余裕、合計¥300以内に収まると判断(Family Cのpipeline
はA-Family Production runnerの`run_one_pattern`[Point Role Planning/
Point Overlap QA/Directional Fact Precheckを含む重い経路]を使わず、
Web検索を要する呼び出しがFact Checker A'の1箇所[記事あたり]のみに
限定されるため、既存Trial実績[Towels Trial-11、Research+Verification
¥55.47]よりも軽量になると判断)。

**baseline(現行A-Family共通Prompt+同テーマ)は追加しないと判断した
(2記事構成)**。理由: (1)費用上限ではなく、独立経路プロトタイプという
スコープを厳密に保つため(baseline生成には`prod_gen.run_one_pattern`
[Point Role Planning等]の追加呼び出しが必要になり、Family C独立設計の
検証という本Trialの目的に対して不要な複雑性を追加する)、(2)ユーザー
指示は「baselineあり/なし」を実施可否の判定に委ねており、¥300以内で
必要なQA(Layer1厳格チェック+Framing QA+retry余裕)は2記事構成で
十分に保てると判断したため。

判定: **実施可(記事生成Trialへ進行)**。

## 6. 実施結果(作業C)

テーマ: 「家庭用ロボットと家事」(home robots and housework、ユーザー
確定)。Research(新規、web_search 12クエリ)→Verification→3層Ledger
(Layer1: CONFIRMED 21件/AMBIGUOUS 1件/REJECTED 2件、Layer2:
FUTURE_ASSUMPTION 3件、Layer3: IMAGINED_FUTURE 3件[around 2030/2035/
2040]、grounding issue 0件)→Family C記事(A2/B1、各1本)→QA。

### 実費(実測、5区分)

| 区分 | 金額(円) | 内訳 |
|---|---|---|
| Research(Researcher) | 24.81 | web_search 12クエリ含む |
| Ledger Verification | 34.23 | web_search含む |
| Layer2/3整理(新設) | 0.50 | LLM1回、web_search無し |
| Writer(A2+B1) | 2.47 | A2 1.63(marker再試行なし、1回で成功)+B1 0.84 |
| QA(Fact Checker A'+Ledger Deviation+Local Rewrite+Future Framing QA) | 78.82 | A2: Fact Check 53.41(技術retry分含む延べ3回)+Deviation 0.76+1.97+Local Rewrite 0.62+Framing QA 0.37=57.13。B1: Fact Check 19.84+Deviation 1.29+Framing QA 0.58=21.71 |
| **合計(実測)** | **140.83** | 上限¥300、API呼び出し件数=17件、unpriced_records=0 |

比較用: `docs/pm/RESULT_PACKET_FC.md`にも要約を記載。詳細ログは
`er013_output/family_c_future_trial_01/raw_usage_log.jsonl`/
`cost_summary.json`。

### QA結果サマリ

| level | Fact Checker A'(Layer1) | Ledger Deviation(Layer1) | Local Rewrite | Future Framing QA(Layer2/3) | overall_status |
|---|---|---|---|---|---|
| A2 | REVIEW_REQUIRED | LEDGER_COMPLIANT(cycle後) | 1 cycle発火、MAJOR 1件を1回のrewriteで解消 | PASS(5項目全て0件) | **NG_REVIEW_REQUIRED** |
| B1 | PASS | LEDGER_COMPLIANT(rewrite不要) | 発火なし | PASS(5項目全て0件) | **PASS** |

- A2のFact Checker A' REVIEW_REQUIRED理由(捏造ではなく精度上の指摘):
  (1)IFR統計「more than 2 million units」を記事側が「more than 2.1
  million」と強めた、(2)異なる2つのYouGov調査(2025年5月/2025年2月)の
  数値を、調査時期・調査差の注記なしに並置、(3)研究の直接結論ではなく
  記事側の要約解釈である旨の指摘、(4)Mobile ALOHAの実演(50回デモ後の
  特定課題自律実行)を「一般家庭で汎用的に家事を遂行」と読める記述。
  いずれも**Layer1(枠外の現在事実文)に対する指摘であり、想像パッセージ
  [Layer2/3]は判定対象から明示的に除外されていた**(Fact Checker自身が
  notesで「Around 2030、Around 2035、Around 2040の想像上の場面は判定
  対象から除外しました」と明記)。ルーティング設計(Layer1のみを渡す)が
  意図通り機能したことの実証でもある。
- A2のLocal Rewrite実例: MAJOR判定文
  `"Cords, small objects, and pet waste could still stop it."`
  (Ledgerは障害物回避**試験の対象**にしたことのみ保証、実際に「止めた」
  という結果までは保証していない、`unsupported_new_claim`)を、1回の
  rewrite試行で
  `"Cords, pet waste, and bowls remained among the obstacles used to
  assess its avoidance."`へ書き換え、再チェックでLEDGER_COMPLIANTを
  確認(`er013_output/family_c_future_trial_01/a2/local_rewrite_log.json`)。
  既存Local Rewrite(er010)がFamily Cの独立本文に対しても無改変で正しく
  機能することを確認できた。

### 評価表(0〜2点、主観・該当文引用は`comparison.md`本体に記載)

| 観点 | A2 | B1 |
|---|---|---|
| 面白さ(わくわく/不安の強度) | 2 | 2 |
| Futureらしさ | 2 | 2 |
| Discovery/Trend化していないか | 2 | 1(製品スペック列挙[LG CLOiD等]がA2よりやや前面化) |
| 事実と想像の区別(Future Framing QA基準) | 2(0件) | 2(0件) |
| throughline | 2 | 2 |
| 1ナレーターの自然さ | 2 | 2 |
| 時間軸の明示 | 2 | 2 |
| **合計** | **14/14** | **13/14** |

該当文引用・全文は`er013_output/family_c_future_trial_01/comparison.md`
(Markdown、全文比較)および`index.html`(閲覧用)を参照。

## 7. 残る問題・限界(STOPには該当しないが記録)

1. **A2はFact Checker A'がREVIEW_REQUIREDのため、人手レビューなしで
   このままProduction採用相当とは扱えない**(Gate 1材料としては
   「安全装置が正しく検出・記録した」実例であり、Trial自体は成功と
   評価する。「安全≠成功」原則どおり、精度指摘を無視して合格扱いに
   していない)。
2. Local RewriteのProduction上限(3 cycle)に対し、Trial向けに1
   cycleへ保守的に制限した。今回はA2の1件のMAJORが1 cycle目の1回の
   rewrite試行で解決したため上限には未到達だったが、より多くのMAJORが
   出るテーマでは1 cycle上限がすぐに人手レビューへ回す方向に働く
   (安全側だが、Production採用時にはcycle数の再検討が必要)。
3. heuristic一次スクリーニング(現在事実紛れ込み検出・枠外未来断定
   検出)は正規表現ベースであり、今回の実データで偽陽性が2件観測された
   (B1の"not proof that such robots will quickly become common"、A2の
   "The fear is that people will start...will..."のいずれも、
   hedge語が検出windowの外にあったため誤検出。実際にはFuture Framing
   QA[LLM]が正しくPASS判定しており、heuristicは補助信号として機能した
   [ブロッキングではない]ため実害はなかったが、精度改善の余地がある)。
4. B1で製品スペック列挙(LG CLOiD等)がやや前面化する傾向を確認(評価表
   参照)。Prompt側で「製品名・仕様の列挙を避け、場面・意味を優先する」
   指示を強化する余地がある。
5. 読者向け本文(マーカー除去後)に、マーカー除去箇所で空行が2行連続
   する軽微な整形上のアーティファクトが残る(内容には影響しないが、
   Audio化する場合は事前のクレンジングが必要)。
6. baselineなし(2記事)で実施したため、「Family C固有の効果」対
   「同一テーマをA-Family共通Promptで書いた場合」の直接比較データは
   本Trialにはない(§5の理由により意図的に対象外とした判断であり、
   別途必要になれば追加Trialで対応可能)。

## 8. Gate 1判定材料

- 独立経路(Family C)は既存A/B-Family・Discoveryへ无影響のまま新設
  できることを実装+回帰で確認した。
- 3層Ledgerルーティング(Layer1のみ既存Fact Checker A'/Ledger
  Deviation Checkerへ、Layer2/3のみ新設Future Framing QAへ)は、
  実データで意図通り機能した(Fact Checkerが想像パッセージを自ら除外
  したことを明記、Local Rewriteが枠外のみを対象に正しく発火・解決)。
  既存の安全装置(Gate)を独自に緩和していない。
- B1は全QA(Fact Checker A'/Ledger Deviation/Future Framing QA)を
  PASSし、A2はLayer1の精度指摘によりREVIEW_REQUIRED(捏造ではなく
  表現の強さ・出典の粒度に関する指摘)。
- 主観評価は面白さ・Futureらしさ・throughline・1ナレーターの自然さ・
  時間軸の明示の5項目で両レベルとも満点、Discovery/Trend化回避は
  A2が満点・B1がやや劣る(製品スペック列挙)。
- 費用は上限¥300に対し実測¥140.83(約53円/¥1000未満の余裕率47%)。

Status: **VALIDATED**(Trial完走、Gate 1材料あり)。Production採用
(`APPROVED_FOR_PRODUCTION`)の可否はユーザー判断待ち。

## 9. SSOT追記文案(編集していない、ユーザー承認後の反映用)

`CURRENT_SPEC.md`への追記案(未反映、案のみ):

> ## Family C(Future、独立経路、Trial検証済み)
> `EDITORIAL-FUTURE-FAMILY-C-PROTOTYPE-TRIAL-01`(2026-09-13)で、
> A/B-Familyとは独立したFuture(未来を描く記事)経路を試作した。3層
> Ledger(`[PRESENT_FACT]`/`[FUTURE_ASSUMPTION]`/`[IMAGINED_FUTURE]`)+
> `[[IMAGINED: ...]]`マーカーによるLayerルーティングで、Layer1のみ
> 既存Fact Checker A'/Ledger Deviation Checkerへ、Layer2/3のみ新設
> Future Framing QAへ振り分ける設計。実装ファイル: `er013_family_c_
> future_ledger_01.py`/`er013_family_c_future_writer_01.py`/
> `er013_family_c_future_qa_01.py`。**Production未配線**(Trial止まり、
> `APPROVED_FOR_PRODUCTION`ではない)。

`DECISION_LOG.md`への追記案(未反映、案のみ):

> 2026-09-13 EDITORIAL-FUTURE-FAMILY-C-PROTOTYPE-TRIAL-01:
> Familyc(Future)独立経路を¥0試作+offline検証(22 test)後、テーマ
> 「家庭用ロボットと家事」でA2/B1各1本の記事生成Trialを実施(実費
> ¥140.83、上限¥300)。B1は全QA PASS、A2はFact Checker A'が
> REVIEW_REQUIRED(精度指摘、捏造なし)。3層Ledgerルーティングが
> 実データで意図通り機能したことを確認。Production採用は別途ユーザー
> 判断。

## 10. 成果物一覧

- 本ファイル(root)
- `er013_family_c_future_ledger_01.py` / `er013_family_c_future_writer_01.py`
  / `er013_family_c_future_qa_01.py` / `er013_family_c_future_qa_test_01.py`
  / `er013_family_c_future_trial_01_run.py`(全て新規)
- `er013_output/family_c_future_trial_01/`(research/a2/b1/cost_summary.json
  /comparison.md/index.html)
- `docs/pm/RESULT_PACKET_FC.md`
