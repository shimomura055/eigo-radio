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

## 最終ラベル・ユーザー決定(2026-10-21、委任_02)
- Status: **CLOSED**(Trial終了・Production採用見送り・将来再検討は保存済み結果から)。ユーザー指示原文=`docs/pm/delegation_log/2026-10-21_FAMILY-X-WRITER-DETECTIVE-WORD-AVOIDANCE-TRIAL-01_CLOSEOUT_USER.md`。
- Fable最終ラベル(試験評価。消さずに保持): **Pattern C = `VALIDATED`**(n=1/Pattern、過去R2の『探偵』出現率約8%[2/24]のため抑制効果の統計的証明ではない。機械判定CANDIDATE_MACHINE:Cと一致)、**Pattern B = `NOT_VALIDATED`**(Entertainmentは高いが、Ledgerにない因果関係の創作1件[『In response to these threats』]を観測。追加指示との因果は未確定)、**Pattern A = `REJECTED`**(発射主体の帰属欠落1件を観測、初回はJA記号QA STOP。追加指示との因果は未確定)。
- ユーザー正式決定(2026-10-21): (1)Pattern A/B/Cすべて、今回のProduction採用を見送る。(2)A:不採用。(3)B:不採用。(4)C:VALIDATED評価は試験結果として保持するが、Production採用は見送り。(5)現行Writer Prompt・Production経路は変更しない。追加Trial・再生成は実施しない。ユーザーはDetectiveという単語を避けたい意向自体を撤回していない(今回の比較結果だけでは改善効果と副作用を十分に評価できないため、現行仕様を維持)。
- 結果の解釈(ユーザー原文§2、観測として記録・相関を因果として扱わない): ①Detective出現はA/B/Cとも0件。ただし各Patternの生成は1回のみで、追加指示による安定的な抑制効果が実証されたとは言えない。②事実面の観測: Aは攻撃主体の帰属欠落、BはLedgerにない因果関係の創作、Cは重大誤り0件・軽微な懸念3件。A/Bの重大誤りが追加指示によって発生したかどうかは未確定。③文章品質の観測: CはLLM評価が最も高かったが、人間の通読では説明的・反復的な文章になっていた。この特徴がPattern Cの指示が原因かどうかは未確定。
- A/Bの品質不合格は、今回の観測結果として保持する。
- Production Writer非変更の確認(委任_02 S2、API 0): 対象5file(`er053_family_x_factlock_ja_writer_01.py`・`er003_v1_n3_01_advanced_adaptation_generate.py`・`er003_v1_n3_01_standard_a2_generate.py`・`er019_family_x_entertainment_production_runner_01.py`・`er003_v1_en_direct_vfl_01_generate.py`)について、`git log 65a1080d5^..HEAD`空・`git diff --stat 65a1080d5^ HEAD`空・作業tree `git status --porcelain`空。Prompt sha固定を含む既存test3本(er003 standard、er053、er019 an3 wiring)を実行: 81 PASS・1 FAIL(`test_w1_rf_queue_contract_referenced_only_by_entertainment_runner_after_c2`。Trial harness群[er082/er083/er086]がProduction moduleをimportすることに対する静的参照検査で、Production Prompt/コード変更によるものではない。本Closeoutでは未修正、判断はFable)。
- 再利用索引: `REUSE_INDEX_01.md`(入力・Prompt・出力・評価の対応表)。
