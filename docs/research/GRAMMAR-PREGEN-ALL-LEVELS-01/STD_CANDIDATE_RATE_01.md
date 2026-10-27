# STD_CANDIDATE_RATE_01 Standard(a2)本文での文法候補率の計測(GRAMMAR-PREGEN-ALL-LEVELS-01 委任_02S、2026-10-27)

目的: 「Std本文でも文法候補が出るか」を実測する(Opus O-2)。事実の報告のみ。Prompt/閾値/model/辞書の変更案は出さない(Std向けlevel差込=D-a(2)は別承認事項)。

## 1. 方法(Production関数を無変更で使用)
- DEV script `docs/research/GRAMMAR-PREGEN-ALL-LEVELS-01/tools/std_candidate_rate_01.py`。`er120_part2_grammar_production_01.extract_candidates`(Step A'' + 決定論のTier順位付け)を、コミット`438ac1b22`版(並行Agent 委任_02が作業ツリーのer120を編集中のため固定。blob sha256 `4017eaf171dc…`)のまま`git show`で読み込み実行。Production/Prompt/閾値/辞書は無編集。Step B(解説生成)は不実行。
- Prompt sha256 `51912fe1e242…`(STEPA_PROMPT)不変、model=`gpt-6-luna`(`routing.SUPPORT_MODEL`、応答modelも一致=契約検査PASS)、技術retry発火0(15 call全て1発で構造検査PASS)。
- 本文の取り出しは各Family runnerと同一関数: X=`paragraphs_from_article_md(a2/article.md)`、Y=`ys.canonical_body(translate/a2.md).split("\n\n")`、Z=`canonical_article_text(writer/std.md).split("\n\n")`。
- 生データ: `std_rate_out/summary.json`(8本)、`std_rate_out/probe_source_runs/summary.json`(出所run特定用3本)、`std_rate_out/probe_repeat/summary.json`(再実行4 call)、`cand_*.json`(候補doc全文)。`raw_usage_log.jsonl`は不追跡(add対象外)。
- STOP確認: `tools/stop_scope_check_01.py --managed-id GRAMMAR-PREGEN-ALL-LEVELS-01` rc=0(`std_rate_out/_stop_scope_check_02s.json`)。単発scriptのため起動規律(監督loop・再起動)は非該当。

## 2. 結果(主表: 委任指定の8本。各1 call)
| # | Family | 本文(出所) | 語数 | 段落 | LLM返却feature | 適格(候補) | Tier/分類 | 費用JPY | 所要s |
|---|---|---|---|---|---|---|---|---|---|
| 1 | X | AI島寺院(`er019_output/ai_island_temple/run_kp75_ev_01/a2`) | 452 | 8 | 2 | **1** | T1 HEAVY(他1件=TV=LOW除外) | 0.376 | 43.4 |
| 2 | X | UK列車(`.../uk_train_speaker_playback/run_kp75_ev_01/a2`) | 415 | 10 | 2 | **2** | T1 CLEFT, T2 INV | 0.323 | 36.3 |
| 3 | X | コーヒー(`.../coffee_prices/run_l3_01/a2`) | 456 | 9 | 1 | **1** | T1 CMP | 0.374 | 56.3 |
| 4 | Y | SNS年齢制限(`er121_output/.../sns_age_limit/run_01/translate/a2.md`) | 653 | 5 | 2 | **2** | T1 HEAVY x2 | 0.315 | 29.0 |
| 5 | Y | 再配達(`.../redelivery_fee/run_style_fix_01/translate/a2.md`、公開済み系) | 666 | 5 | 2 | **2** | T1 CMP, T1 HEAVY | 0.359 | 40.3 |
| 6 | Z | 走れメロス翻案 "Before the Last Light"(`er026_output/.../melos/run_e2e_06/writer/std.md`) | 408 | 29 | **0** | **0** | - | 0.156 | 18.4 |
| 7 | Z | After Twenty Years "The Promise"(`.../after_twenty_years/run_sf_prod_01/writer/std.md`) | 443 | 28 | 1 | **1** | T1 CMP | 0.247 | 36.7 |
| 8 | Z | The Open Window(`.../the_open_window/run_sf_prod_01/writer/std.md`) | 422 | 29 | **0** | **0** | - | 0.174 | 15.0 |

- 8本: 候補合計9、**平均1.13件/本**。Family別: **X 1.33(1,2,1) / Y 2.0(2,2) / Z 0.33(0,1,0)**。
- **0件率: 2/8=25%(いずれもZ)**。Z内では2/3。
- 費用: 8本合計**JPY2.32**(平均0.29/本、範囲0.156-0.376)。入力約3.5-3.7k tok、出力1.2k(0件)-4.0k tok。

## 3. 追加プローブ(出所run特定用。委任の8本枠とは別・上限JPY7内)
| Family | 本文(出所) | 候補 | 費用JPY | 備考 |
|---|---|---|---|---|
| X | coffee_prices Part 2 evidence `part2_hr_evidence_01/run_r1/a2`(X evidence元run候補。sha`41bc054e`) | **1**(T2 INV "Here is the key point.") | 0.205 | Tier1なしでTier2のINVのみが適格 |
| Z | The Monkey's Paw "The Last Wish"(`the_monkeys_paw/run_sf_prod_01`) | **0**(featureは1件だがTV=LOW) | 0.288 | |
| Z | The Gift of the Magi(`the_gift_of_the_magi/run_sf_prod_01`) | **1**(T1 POSTMOD "Wise men called the magi brought gifts on the first Christmas.") | 0.341 | 他1件=TV=LOW除外 |
| 再実行 | Z melos Std x2 / Z Open Window x1 / X AI島 x1(同一本文) | melos 0,0(計0,0,0)/ Open Window 0(計0,0)/ **AI島 3**(初回1) | 0.088/0.125/0.111/0.404 | 同一本文でもXは1→3と変動(LLM出力の揺れ)。Z 0件は再現 |
- 追加プローブ+再実行の合計 JPY1.56。**全体の実費合計 JPY3.885**(15 call、上限JPY7の56%)。

## 4. Advanced既存実測との比較(COST_ESTIMATE_01 §1: 既存Adv候補数 X 3.0 / Y 2.3 / Z 0.73)
| Family | Adv(既存実測) | Std(本計測、記事単位) | 差 |
|---|---|---|---|
| X | 3.0(n=3記事: 2/3/4) | **1.25**(n=4: 1,2,1,1。AI島のみ再実行で3も観測) | 約-1.75 |
| Y | 2.3 | **2.0**(n=2) | 約-0.3 |
| Z | 0.73(実質n=2) | **0.4**(n=5作品: 0,1,0,0,1) | 約-0.3 |
- 記事単位の0件率: 全体3/11=27%(いずれもZ)、X 0/4、Y 0/2、Z 3/5。
- n小(Y n=2、同一本文でも変動あり)。傾向のみ、母集団の保証ではない。

## 5. 難度不一致の所見(事実のみ。変更提案はしない)
- 現行Step A''は本文を「Advancedレベル」「日本語話者の学習者(B1〜B2相当)」と明示(`er120_part2_grammar_production_01.py:55`、`:59`「レベル: Advanced」)、`LEVEL="Advanced"`(:42、コメント「Standard(a2)への拡張は新仕様=行わない」)、Step Bも「B1〜B2相当」(:118)。Std(a2)本文はA2向けに書かれた本文(語数408-666)を、この文言のまま分類している。
- 観測: (a) Zの3/5作品でLLMがfeature自体を0件で返す(Z melos 3/3, Open Window 2/2)=適格条件で落ちたのではなく抽出の段階で0。(b) 適格条件`teaching_value=HIGH`で落ちたfeatureは3件(X AI島1、Z Magi 1、Z Monkey's Paw 1。理由`TV=LOW`)。(c) 採用された候補文の例は平易な文を含む: "Here is the key point."(X、INV Tier2)、"Wise men called the magi brought gifts on the first Christmas."(Z、POSTMOD)、"It was higher than in the same month a year earlier."(X、CMP)。長文・複雑文の例: Y HEAVY "Setting an age when children can use social media also brings up another question: how much can they turn to adults after they start?"。(d) 11記事の初回候補11件の分類はHEAVY 4 / CMP 3 / INV 2 / CLEFT 1 / POSTMOD 1。
- 上記はいずれも「現行Promptをそのまま使った場合の実測」であり、Prompt差込・閾値緩和の効果は未試験(別承認事項、D-a(2)の材料のみ)。
