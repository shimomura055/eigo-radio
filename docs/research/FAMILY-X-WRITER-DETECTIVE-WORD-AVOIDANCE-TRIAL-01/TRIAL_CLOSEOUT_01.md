# TRIAL_CLOSEOUT_01: Writer「Detective」単語回避 Trial(委任_01、2026-10-21)

- 性質: Trial(新Prompt候補`TRIAL`、到達上限`VALIDATED`)。最終ラベルはFable。Production採用はユーザーの別途明示承認。Production Writerの Prompt・コード・実行経路は変更なし。
- 機械判定: **`CANDIDATE_MACHINE:C`**(事前固定規則 TRIAL_DESIGN_01 §5。A=NOT_CANDIDATE[新規の帰属欠落1]、B=NOT_CANDIDATE[新規の因果創作1]、C=CANDIDATE)。
- 比較ページ: https://shimomura055.github.io/eigo-radio/user_test/writer_detective_trial_01/index.html
- 結果表・全データ: `COMPARISON_RESULT_01.md`、`er086_output/writer_detective_avoidance_trial_01/eval/results.json`、判定生応答`eval/judgment_*.json`、実Prompt`{A,A_rerun1,B,C}/prompt_dump/`。

## 結果要約
| | Baseline | A | B | C |
|---|---|---|---|---|
| detective(Adv/Std本文) | 2/2(JA R2『探偵』2) | 0/0 | 0/0 | 0/0 |
| Entertainment平均 Adv/Std(LLM,1-5,2回) | 2.7/2.9 | 2.9/3.4 | 3.7/3.8 | 4.3/3.9 |
| 新規の重大事実誤り(Sonnet通読) | (基準) | 1(第2段落で発射主体を自己断定、帰属欠落) | 1(『In response to these threats』因果創作) | 0(境界MINOR: 『other side's bases』) |
| Writer実費JPY | 13.275 | 13.742(+初回STOP分14.221) | 14.086 | 11.847 |

- 追加指示は6工程(R0・R1・R2・Advanced英訳・Advanced IOL・Standard)の実Promptに入ったことをprompt_dumpで確認(`contains_pattern_text`すべてtrue)。追加API呼出0(Prompt文字数増のみ)、モデル・工程・retry設定はBaselineと同一。
- Baselineの『探偵』はR2(`USER_TMPL`のEntertainment Revision)で初めて導入(R0・R1は0)。A/B/CはR0〜R2すべて探偵0。
- 重要な限界: ①n=1/Pattern。Production過去のFamily X JA R2(`ja_writer/revision2.md`)24件中の『探偵』出現は2件(約8%)で、n=1でdetective=0でも追加指示の効果の統計的証明にはならない(本Trialの確認事項は『単語を消しつつ品質を保てるか』)。②Pattern Aの初回はProduction JA記号QAがSTOP(R2が『配役表』形式で全角コロンを含み再実行後も残存)。同一条件で1回再生成(A_rerun1)し評価。③EntertainmentのLLM判定はluna単独で、Baselineの比喩過多を強く減点する傾向がある。実聴者の好みとは一致しない可能性があり、実読はBaseline・Bが『遊び心のある語り』、Cが『平明で説明的(やや反復)』という印象(Sonnet所見)。④RFは実行していない(共有review_queueを汚さないため)。Baseline Standardの既知の帰属RF候補s11と同種の指摘がLLM判定にも出た。

## Sonnet所見の順位(推奨はFable)
1位C(機械判定の唯一の候補。事実面が最も堅い、Entertainment LLM最高、不自然な演出5.0。ただし『面白さ』はBaselineの遊び心より平明で、ユーザー目的『面白さの維持』の観点では要ユーザー確認。追加指示が最長で複雑)/2位B(Entertainmentは高く語り口がBaselineに近いが、事実の因果創作1件で候補外)/3位A(最短指示だが、発射主体の帰属欠落1件。Aは初回STOPも発生)。同等ならA<B<Cで指示が短い方を優先する規則だが、A・Bは事実面で候補外のため該当しない。

## 追加検証の判断候補(未実施)
- 効果の統計的確認: 効果判定が必要なら、Baselineで『探偵』が出たR1生出力(`ja_writer/factlock/r1.raw.md`)を入力にR2だけをPatternあり/なしで複数回再生成(R2のみ約JPY3/回)。Production採用提案前の判断材料。現時点では未実施(委任の『最小限の比較』『追加生成しない』に従う)。
- 判定: 分類C/D(新たな実験設計の判断)=Fable判断。

## Production採用時に必要な事項(提案ではなく整理)
- 注入点は6つ: ①`er053_family_x_factlock_ja_writer_01.build_r0_prompt`末尾 ②`USER_TMPL`末尾(R1/R2) ③`er003_v1_n3_01_advanced_adaptation_generate.build_family_x_faithful_translation_prompt`指示ブロック末尾 ④`build_family_x_in_one_line_prompt` ⑤`er003_v1_n3_01_standard_a2_generate.build_family_x_no_heading_prompt`。変更規模=Prompt文字列への1文追記(C案は約420文字)を5関数。Production Promptの直接編集になるため、11-7の限定例外(新コード経路+flag)は適用外で、ユーザー正式承認後の通常Production変更。
- 既存sha固定(`verbatim_shas`、STANDARD_A2_PROMPT_SHA256等)・golden fixture・DefaultOffテストの更新が必要。Opus条件C(重要変更のProduction採用提案前)該当の可能性あり=Fable判断。
- 量産単価: 追加API呼出0、入力token微増のみ(C案で数十token/呼出×6、実費差は誤差)。今回の実費差(C 11.85〜B 14.09)はPattern起因ではなく生成のばらつき。
- 禁止語リストは新設していない。類似語(investigat/clue/mystery/magnifying glass/推理/虫眼鏡)はBaselineにのみ出現し、A/B/CのAdvanced/Standardでは0件(観測のみ)。
