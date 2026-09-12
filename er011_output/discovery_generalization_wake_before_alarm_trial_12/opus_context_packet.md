# Opus Context Packet — FAMILY-A-DISCOVERY-GENERALIZATION-WAKE-BEFORE-ALARM-NPLUS1-TRIAL-12 L2レビュー用

作成: `PM-TOKEN-EFFICIENCY-PHASE2-CONTEXT-PACKET-TRIAL-01`(After段階、2026-09-12、Sonnet作成)。
雛形: `docs/pm/templates/OPUS_CONTEXT_PACKET_TEMPLATE.md`。手順: `PM-TOKEN-EFFICIENCY-PHASE2-CONTEXT-PACKET-TRIAL-01_REPORT.md` 4節。
本packetは`docs/pm/PM_GOVERNANCE.md`・`.claude/agents/opus-consultant.md`の既存ルールを上書きしない。
**重要contextは省いていない**(元REPORTの要旨・実測値・行範囲を全て転記済み。元REPORT全文・SSOT全文は転記していない)。

対象タスク: `FAMILY-A-DISCOVERY-GENERALIZATION-WAKE-BEFORE-ALARM-NPLUS1-TRIAL-12_REPORT.md`(15,230字、124行、`er011_output/discovery_generalization_wake_before_alarm_trial_12/`)。

---

## (a) 論点(限定)

1. **再現性・一般化可能性**: Trial-12(睡眠/目覚まし)はTrial-11(タオル臭)と同じDiscovery Focus Module Part A単独条件で、記事レベル(Ledger準拠・Fact Checker PASS・保険文0・Local Rewrite 0)が「Trial-11より一段クリーン」に再現した。これはN=2×2レベルの観測として、Part Aの効果を一般化する証拠になるか、それとも題材依存(2テーマとも「身の回りの謎→機序説明」型)による見かけ上の再現に過ぎないか。(b)の対照アーム欠如・題材の型の類似性を踏まえて判定してほしい。
2. **観察10項目の結果解釈**(下記(b)の表を参照、必須論点チェックリスト`PM-TOKEN-EFFICIENCY-PHASE2-CONTEXT-PACKET-TRIAL-01_REPORT.md`2節に基づく。該当外なし、Support/Key Phraseも今回は成果物に含まれるため対象):
   - ①Full Story/Point構成: A2/B1Bとも成立と報告。tolerance逸脱(下記表)まで踏まえても「成立」と言えるか。
   - ②Pointの言い換え回避: Point Overlap QA PASS・retry 0回。QA PASSの額面どおりでよいか、実文面の言い換え重複が残っていないか。
   - ③Pointごとの発見差: cross_point_overlap比率A2 0.149/0.226、B1B 0.037/0.024(低)。これは実際に発見の質的差を裏付けるか、それとも指標が測れていない多様性(記事間の型の類似)を隠していないか。
   - ④保険文: 本文・Support/Comment/Previewとも0件(両レベル)。Trial-11 Opus L2レビュー論点1(a)は「保険文0は題材依存でほぼ説明できる」と指摘済み。同じ説明がTrial-12(睡眠領域、争いのある消費者向け助言なし)にも当てはまるか。
   - ⑤Ledger Deviation/Local Rewrite: 両レベルとも0件(Trial-11はB1Bで1サイクル発生)。Rewrite自体が発生しなかったため、Trial-11論点2で指摘された副作用(near-duplicate文・後続QA未通過)の再現有無は評価不能である点をどう扱うか。
   - ⑥Fact Checker: 両レベルとも一発PASS(Trial-11はB1Bで一時REVIEW_REQUIRED)。advisory 0件を「悪化なし」と見てよいか。
   - ⑦Point Overlap/Value QA: 両方PASS。Evidence Compressionでの数値具体性の逆転(Trial-11見落とし2で指摘)が今回も起きていないか、個別確認できているか。
   - ⑧Support/Key Phrase: 両レベルとも全PASSと報告(selection/canonicalization/redundancy)。Trial-11レビューでは明示的に扱われていない論点であり、今回はデータがある。QA PASSの中身(実際の重複・不自然さ)まで見ているか。
   - ⑨A2/B1成立性(**要注意**): (b)下段の実測表のとおり、Trial-12 A2 `point_one`は79語で**tolerance上限・target上限とも超過**(`exceeds_tolerance_upper=true`)、B1B `point_two`は64語で**target上限超過**(`exceeds_tolerance_upper=false`)。**Trial-12 REPORT本文(15,230字)はこの超過に一切言及していない**(全文中"tolerance"の語自体が登場しない)。これはTrial-11 Opus L2レビュー見落とし4(A2 Point One 71語のtolerance超過が報告書で無言及だった)と**同一パターンの見落としがTrial-12でも再現**していることを意味するか。
   - ⑩音声工程: 4.1節参照(下記(c)関連)。
3. **A2 `full_story_part1`のRepetition QA誤flag疑いのfailure mode位置づけ**: 別タスク`REPETITION-QA-INTENTIONAL-REPEAT-FALSE-POSITIVE-RECONCILE-03`が根本原因を特定済み(下記(c)参照、packet作成中に完了・追記)。既存の`RECONCILE-02`+`OPEN-121`実装(綴り小数two〜twelveの単語単体↔算用数字の同値化)は**今回のケースには構造的に無関係**であり、原因は(a)数値レンジ外("twenty-four"は承認済みレンジ2〜12の外)と(b)**より根本的なトークン境界の非対称性**(canonical側tokenizerがハイフン複合語"twenty-four-hour"を1トークンのまま扱うのに対し、ASR側word-level出力は"24"と"-hour"の2トークンに分割するため構造的に一致し得ない)の2つの独立したギャップの重なりと特定された。scratchpad prototypeで解消確認済み(既知true positiveは無変化)だが**Production未実装**(4項目のユーザー判断待ち)。この根本原因特定の正確性・一般化予見("時間・期間・年齢等の複合修飾語を含む今後の記事テーマで再発しうる")の妥当性を判定してほしい。
4. **N=2時点でProduction採用判断に持ち込むための不足材料**: Trial-11 Opus L2レビュー論点5(下記(c))は「対照アーム必須・題材の型分散・3テーマ×2条件×N=3=36本目安・¥1,100〜1,300推定」を示している。Trial-12はこの推奨設計に対し何を満たし、何を満たしていないか(対照アームは依然なし、題材はTrial-11と同じ「身の回りの謎解明」型で型分散も未達成である点を含めて判定してほしい)。
5. **新規結果/過去再掲/進行中の区別**: Trial-12 REPORT 10節の自己申告(新規結果=3節記事レベル観測全項目・4.1節Human Review Lock分析・5節cool-down観測・6節コスト実測・9節部分player設計、過去再掲=3節Trial-11列・4.6節Precheck一般論)が正確か。上記2⑨の見落とし再現は、この区別のどちらにも明示されていない点を含めて評価してほしい。

---

## (b) 主要数値表・要点(Sonnet REPORTからの転記、全文は渡さない)

### Trial-12 REPORT 要点(5行、原文転記)

1. Discovery Focus Module Part A単独条件は、新テーマ「なぜ目覚ましが鳴る直前に目が覚めることがあるのか?」でも記事レベル(Ledger→Writer→Fact Checker→Ledger Deviation→Point Overlap/Value QA→Support/Key Phrase)は**A2/B1B両方でPASS、Local Rewriteゼロ**という、Trial-11(タオル臭)より一段クリーンな結果になった。
2. Point One/Point Twoは両レベルとも意味的に異なる発見(A2: 予期的な生理反応の段階性 vs 睡眠段階とgrogginess、B1B: 概日リズムの精度限界 vs 自己覚醒の練習効果)であり、機械的なcross_point_overlap比率も低い(A2: 0.15/0.23、B1B: 0.04/0.02)。
3. 音声工程で**A2のsegment `full_story_part1`が既存Human Review Lock(3回連続NG→STOPPED)に到達**し、cool-down 20分観測フックの無人4回目試行もNGだった(自動採用なし、Production側無変更)。B1Bは全segment検証PASS・Assembly PASS・Gate PASS。
4. 費用は記事+Support+Audio合算で**¥141.55**(上限¥300以内)。
5. Closeout: **記事レベルはVALIDATED、音声レベル(A2のみ)はUSER_DECISION_REQUIRED**。Production採用はユーザー判断なしに行っていない。

### 観察項目ごとの結果表(Trial-12 REPORT 3節、原文転記)

| 観察項目 | Trial-12(wake-before-alarm) | Trial-11(towels、既出再掲) |
|---|---|---|
| Full Story/Point構成の自然な成立 | A2/B1Bとも成立(謎提示→機序説明→2つの異なる発見→限界の言及) | 同様に成立(既出) |
| PointがFull Storyの言い換えでないか | Point Overlap QA: A2/B1BともPASS、retry 0回 | 同じくPASS、retry 0回(既出) |
| Pointごとに異なる発見か | A2: 予期的生理反応の段階性 vs 睡眠段階とgrogginess(比率0.149/0.226)。B1B: 概日リズム精度限界 vs 自己覚醒練習効果(比率0.037/0.024) | 同様に低比率で異なる発見(既出) |
| 保険文・過剰注意文 | 本文0件・Support 0件、両レベル | 0件(既出) |
| Ledger Deviation | 0件(LEDGER_COMPLIANT)、両レベル | 0件(既出) |
| Local Rewrite | 発生なし(両レベル) | B1Bで1サイクル発生(Fact Checkerが3件未確認claim指摘→解消) |
| Fact Checker verdict | A2: PASS(1/1)、B1B: PASS(1/1) | A2: PASS、B1B: REVIEW_REQUIRED→Local Rewrite後PASS |
| Point Overlap/Point Value QA | 両方PASS、両レベル | 同様 |
| Support/Key Phrase | 両レベルともselection/canonicalization/redundancy全PASS | 同様 |
| A2/B1B両方での成立性 | 両方成立(記事レベル) | 同様 |
| 音声工程 | B1B完成・A2は1segmentがHuman Review Lock中につき部分player | 両方完成 |

### 定量比較表(word count / tolerance / near-duplicate、`comparison_vs_towels_trial_11.json`実測転記、**Trial-12 REPORT本文には未記載**)

| 項目 | Trial-12 A2 | Trial-12 B1B | Trial-11 A2(既出) | Trial-11 B1B(既出) |
|---|---|---|---|---|
| 総語数 | 302 | 357 | 294 | 419 |
| point_one語数 | 79 | 48 | 71 | 69 |
| point_one: exceeds_tolerance_upper | **true** | false | **true** | false |
| point_one: exceeds_target_upper | **true** | false | **true** | true |
| point_two語数 | 58 | 64 | 65 | 70 |
| point_two: exceeds_tolerance_upper | false | false | false | false |
| point_two: exceeds_target_upper | false | **true** | true | true |
| near_duplicate_sentence_pair_count | 1 | 2 | 0 | 1 |
| cross_point_overlap(P1 vs P2 / P2 vs P1) | 0.149 / 0.226 | 0.037 / 0.024 | 0.243 / 0.225 | 0.244 / 0.222 |
| insurance_sentence_hit_count | 0 | 0 | 0 | 0 |

**Sonnetによる注記(重要)**: Trial-12 A2 `point_one`(79語)は`exceeds_tolerance_upper=true`・`exceeds_target_upper=true`であり、Trial-11 A2 `point_one`(71語、同じく`exceeds_tolerance_upper=true`)と同じ超過パターンである。しかしTrial-12 REPORT本文(15,230字)はこれに一切言及していない。Trial-11 Opus L2レビュー「見落とし4」は、Trial-11 REPORTが同種の超過を報告していなかった点を指摘済みであり(下記(c))、**同一の見落としパターンがTrial-12でも再現している**ように見える。

### 費用5区分(Trial-12 REPORT 6節、原文転記)

| 区分 | 金額(¥) | 説明 |
|---|---|---|
| ①今回実測合計(Standard同期) | **141.55** | Ledger+記事生成78.98(researcher+verification 44.68含む)+Support/Audio 62.57(a2:34.07, b1b:25.93, other:2.57) |
| ②今回実測(公式script報告値) | 141.55 | ①と同値。unpriced_records=1件(azure)のみ開示、¥0計上 |
| ③量産想定(Batch適用時1記事見込み、机上換算・未実行) | 約114.65 | audio側gemini分(¥53.80)をBatch tier(Standardの50%)換算 |
| ④retry/Human Review由来の上振れ分(内数) | 5.07 | A2 full_story_part1の2回目attempt(¥2.60)+cool-down 4回目attempt(¥2.47) |
| ⑤参考: 通常運用相当分(①-④) | 136.48 | Human Review発生に伴う異常対応コストを除いた実質必要額 |

管理ID全体上限¥300に対し実測¥141.55(47.2%)、超過なし。

### runtime evidence: OPEN-145/121/146の発火記録(Trial-12 REPORT 4.3〜4.6、原文転記)

- **OPEN-121(数字↔数詞同値化、connected_speech_equivalence_layer)**: A2英語本文4segment全てで対象フラグ有効だったが、`connected_speech_info`は全attempt・全segmentで`null`(**非発火**)。数字↔数詞表記のASR不一致は本Trialでは発生しなかった。
- **OPEN-145(日本語ASR表記ゆれ層)**: A2/B1B両レベルの全日本語segmentで`reading_resolver_info`は全件`null`または未設定(**非発火**)。
- **OPEN-146(Ledger公式英語表記機構)**: 本テーマの検証済みFactは全て英語一次情報源で日本人名の英語表記対象が存在しないため、該当artifactは生成されておらず**想定どおり非発火**。
- **Directional Fact Precheck(参考、非ブロッキング層)**: A2/B1Bとも`overall_status=DIRECTION_REVIEW_REQUIRED`(Trial-11と同一値)。`conflicts`は全項目で空配列(機械的に比較不能なだけで新規矛盾はなし)。

### 音声工程 runtime evidence(A2 Human Review Lock、Trial-12 REPORT 4.1、原文転記)

- segment `full_story_part1`が標準2回attemptともRepetition QA(`method_a_ngram`)で `"24 -hour day."` の3語フレーズ重複を検出しNG(`verified=false`)。ASR文字起こし自体は正字一致(`NORMALIZED_MATCH`、`length_ok=true`)。
- 記事本文は「Light helps this clock match the 24-hour day.」「…usually matched a 24-hour day.」と意図的に同じ語句を2文にまたいで正当に2回使用(Point Overlap QA側`near_duplicate_sentence_pairs`でもratio 0.554で検出済みだが記事QA自体はPASS扱い)。TTS側Repetition QAがこの正当な語句再利用を誤検出した可能性がある(false-positiveの疑い、Trial-12 REPORT自身の記述)。
- 3回目(cool-down観測フックの無人4回目試行)も同じくNG。`review_lock_state.json`は`HUMAN_REVIEW_REQUIRED`(`final_status=STOPPED`)。Assembly: Gate OFF経路`BLOCKED`、Gate opt-in ON経路`SKIPPED_ASSEMBLE_NOT_PASS`。人的介入・承認代行は一切行っていない。
- cool-down観測(N=1): `requested_cooldown_seconds=1200.0`/`actual_wait_seconds=1200.006`、`params_hash`一致、4回目`fourth_attempt_result_status=NG`、`no_human_intervention=true`/`production_state_modified=false`/`auto_adopted_to_production=false`。

---

## (c) 必要なspec/code section(行範囲+必要最小の抜粋)

| ファイル | 行範囲 | この範囲が必要な理由 |
|---|---|---|
| `CURRENT_SPEC.md` | 794-810行(「## Discovery/Why(Pool型)」節、17行) | Discovery Focus Module(`DISCOVERY_FOCUS_MODULE_BLOCK`)の現行仕様状態(`VALIDATED(Trial)`止まり、Production採用案は2026-09-09ユーザー決定で不承認)を確認するため。要旨: Layer3 Focus ModuleはTrial-05でVALIDATED、Household Trial-07でREVIEW_REQUIRED率baseline比約5倍増加・Point多様性低下を確認、現行Production採用案は不承認のまま「再改善中」。保険文抑制Prompt制約案(Part B案1)は2026-09-10ユーザー決定でProduction不採用のまま、Part A単独運用でHuman Reviewにより目視修正・発生率観測する運用方針。 |
| `FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11-OPUS-L2-REVIEW-01_REPORT.md` | 全文25,234字中、要点(5-12行)+論点見出し5件(15,48,85,111,143行)+見落とし10件見出し(171-182行) | 前回Opus L2レビューとの継続性確認のため(同じレビュアーが同種の見落としを繰り返し指摘していないか)。要点5行: (1)保険文0件は題材依存でほぼ説明可、Part A効果の証拠にならない (2)REVIEW率はTrial-09/10の0/6から今回B1B 1/2へ悪化方向 (3)Ledger Deviation自動解消は事実面妥当だが副作用未記録 (4)Fact Checker advisory3件中1件はstale (5)A2 294語は問題でないがB1B 419語(soft上限420語)が外れ値。論点見出し: 論点1=N=1×2テーマの因果解釈誤りリスク(対照アーム欠如が最大の構造問題)、論点2=Ledger Deviation自動解消の妥当性、論点3=Fact Checker advisory重み、論点4=A2 294語の短さ、論点5=次のN増し設計への示唆。見落とし10件(見出しのみ): ①Fact CheckerがLocal Rewrite出力を見ない構造的blind spot、②Evidence Compressionの数値具体性逆転、③B1B 419語がsoft上限420語に接近、**④A2 Point One 71語がtolerance上限超過(報告書は無言及)**、⑤2テーマで「型」が酷似、⑥house phrase("quiet lesson")の他Trial再出現、⑦音声上の細かい重複2件、⑧comparison.html未生成、⑨保険文regexが独立caveat文を検出しない、⑩費用分離不可等の既知gap再確認。 |
| `FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11-OPUS-L2-REVIEW-01_REPORT.md` | 145-167行(論点5「採用判断に必要な最小の追加観測」全文) | 上記(a)論点4の判断材料。要旨: (1)対照アーム(baseline vs Part A)が最重要・必須 (2)題材の型を意図的に分散(争いのある消費者向けガイド記述テーマを最低1つ、Household/Towels以外の型を1つ以上) (3)規模目安=3テーマ×2条件×A2/B1B×N=3=36本、費用概算¥1,100〜1,300(比例推定) (4)観測指標6種(REVIEW率・保険文hit・caveat文カウント・Local Rewrite件数と語数差・tolerance逸脱記録・記事間の型重複) (5)多様性は目視artifact(comparison.html)必須、Trial-11は生成していない。避けるべき設計: 同種テーマの偏り、対照群なしのN増し、交絡した条件比較。 |
| `REPETITION-QA-INTENTIONAL-REPEAT-FALSE-POSITIVE-RECONCILE-02_REPORT.md` | 全文(冒頭要点1-5行、1-5節) | Trial-11タオルB1B `full_story_part2`("after two months"重複)で発見された、綴り小数(two〜twelve)→算用数字変換によるcanonical/ASR不一致バグの根本原因調査(2026-09-12、Fable委任1回目、¥0)。7件中2件独立記事で系統的再現(Discovery Trial-11+既存Production `pool_n4_supermarket`)。scratchpad prototypeで解決確認済み(既知true positiveは維持)。**この時点ではProduction未実装・USER_DECISION_REQUIRED**として提出された。 |
| `OPEN-121-REPETITION-QA-NUMBER-WORD-EQUIVALENCE-PRODUCTION-FIX-01_REPORT.md` | 1-17行(冒頭要点)+22-29行(実装詳細) | 上記RECONCILE-02の発見を受け、2026-09-12にユーザー承認を得てProduction実装済み(`er011_open121_repetition_qa_production_01.py`へ`_normalize_token_numeric_equiv()`追加、回帰テスト35件PASS、`PRODUCTION_WIRED`)。**辞書は"two"〜"twelve"の単語単体のみ**(29行)。**ハイフン複合数(twenty-four等)は対象外**だが、これは辞書の**完全トークン一致**(`_normalize_token_numeric_equiv()`が`_NUM_WORD_TO_DIGIT_EN.get(t, t)`で厳密キー一致のみ変換、`er011_open121_repetition_qa_production_01.py:385-390`)により自然に除外されるためであり、`(?<!-)`否定後読みとは無関係(`(?<!-)`は`er003_v1_n3_01_tts_generate.py:582`のTTS前処理側の別実装で、ER-010-NO9バグ再発防止用)。[2026-09-12訂正: Opus L2指摘] |
| `REPETITION-QA-INTENTIONAL-REPEAT-FALSE-POSITIVE-RECONCILE-03_REPORT.md` | 全文11,686字(2026-09-12、packet作成中に完了・追記) | Trial-12 A2 `full_story_part1`のRepetition QA誤flag根本原因調査(¥0)。canonical本文原文は"twenty-four-hour"(綴りのまま2回、`parts.json`)。根本原因は2つの独立ギャップ: (a)数値レンジ外(`_NUM_WORD_TO_DIGIT_EN`辞書はtwo〜twelve[2〜12]のみ、twenty-fourは対象外)、(b)**より根本的**にトークン境界の非対称性(canonical側`_normalize_tokens()`は`text.split()`で空白のみ分割するため"twenty-four-hour"が1トークンのまま残るが、faster-whisper word-level ASRは発話された"24-hour"を"24"と"-hour"の2トークンに分割する`_normalize_token()`はハイフンを除去対象外とするため、ASR側3-word span`["24","-hour","day"]`がcanonical側と構造的に一致し得ない)。offline実測で`_canonical_repeat_count`=0を再現し確認済み。scratchpad prototype(tens-ones-付属語の3分割ハイフン複合パターンのみに反応する狭い正規化)で解消確認(既知true positiveは無変化、無関係なハイフン複合語"hobby-based"等は無影響)。**Production未実装**(repoコード変更なし)。横断集計(9,832ファイル走査)で同型事例は今回1件のみだが、時間・期間・年齢等の複合修飾語を含む今後のテーマで再発しうる構造的failure modeと結論。4項目のユーザー判断(prototype実装要否・対象範囲・A-Family既存Production経路への影響評価・Human Reviewキュー対応方針)が未回答のまま。 |

---

## (d) Sonnet要約

Trial-12はTrial-11と同一のDiscovery Focus Module Part A単独条件を新テーマ(睡眠/目覚まし)で再現し、記事レベルはLocal Rewrite・Fact Checker advisory・保険文ともゼロという「よりクリーンな」結果を報告した。しかし定量データ(`comparison_vs_towels_trial_11.json`)を直接確認すると、Trial-11 Opus L2レビューが「見落とし」として指摘したA2 Point Oneのtolerance超過(71語)と同種の超過(79語)がTrial-12でも発生しており、かつTrial-12 REPORT本文はこれに一切言及していない。対照アーム(baseline)は依然として存在せず、題材も「身の回りの謎解明」型でTrial-11と類似しており、Trial-11レビューが要求した題材分散(争いのある消費者向け助言テーマ・異なる型)は満たされていない。音声工程ではA2 `full_story_part1`が既存Human Review Lockに到達し、記事本文が正当に2回使う"twenty-four-hour"という表現をRepetition QAが誤検出した。原因は`RECONCILE-03`(packet作成中に完了)により、既存の綴り小数(two〜twelve)↔算用数字修正(RECONCILE-02/OPEN-121)とは無関係な、トークン境界の非対称性(canonical側はハイフン複合語を1トークン扱い、ASR側は2トークンに分割)と特定された。scratchpad prototypeで解消確認済みだがProduction未実装であり、4項目のユーザー判断が必要な状態。

---

## (e) Progressive Disclosure手順(Opus向け)

> 上記(a)〜(d)で診断できない場合のみ、追加でファイルを読んでよい。ただし読む前に「読む理由」と「対象ファイル・行範囲」を1行で宣言し、診断結果の最後に「追加で読んだファイル一覧と概算文字数」を自己申告すること。無宣言での巨大ファイル全文読み込みは禁止。診断精度を優先し、必要な事実を省いてまで読込量を減らしてはならない。

### 追加読込の候補一覧

| ファイル | 概算サイズ | 何が分かるか |
|---|---|---|
| `FAMILY-A-DISCOVERY-GENERALIZATION-WAKE-BEFORE-ALARM-NPLUS1-TRIAL-12_REPORT.md` | 15,230字 | Trial-12の全文(本packetは要点を全て転記済みだが、9節player設計の詳細等、未転記の細部を確認したい場合) |
| `er011_output/discovery_generalization_wake_before_alarm_trial_12/comparison_vs_towels_trial_11.json` | 16,618字 | (b)の定量比較表の元データ全体(本文テキスト・全section内訳を含む) |
| `er011_output/discovery_generalization_wake_before_alarm_trial_12/a2/audit/tts_generation_results.json` | 未計測(数十KB規模) | A2全segmentのTTS/ASR attempt全履歴(Repetition QA method_d spectral結果等、4.1節に転記していない詳細) |
| `er011_output/discovery_generalization_wake_before_alarm_trial_12/a2/parts.json` | 数KB | A2記事本文全文(canonical text原文、"twenty-four-hour"表記の全出現箇所) |
| `FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11-OPUS-L2-REVIEW-01_REPORT.md` | 25,234字 | 前回Opus L2レビュー全文(論点1-5・見落とし10件の詳細根拠・引用行番号) |
| `REPETITION-QA-INTENTIONAL-REPEAT-FALSE-POSITIVE-RECONCILE-02_REPORT.md` | 約6,300字(概算) | Repetition QA綴り小数(two〜twelve単語単体)バグの根本原因調査全文 |
| `REPETITION-QA-INTENTIONAL-REPEAT-FALSE-POSITIVE-RECONCILE-03_REPORT.md` | 11,686字(本packetは要点を全て転記済みだが、6節prototype実装の詳細コード・7節ユーザー判断4項目の全文を確認したい場合) | ハイフン複合数詞のトークン境界非対称性バグの根本原因調査全文 |
| `OPEN-121-REPETITION-QA-NUMBER-WORD-EQUIVALENCE-PRODUCTION-FIX-01_REPORT.md` | 全文(概算数千字、冒頭部のみ本packetへ転記) | Production実装済み修正の全詳細(回帰テスト・遡及再判定の全内訳) |
| `OPEN_ITEMS.md` OPEN-142行 | 巨大単一ファイルの一部(該当行のみ) | Token効率化Phase 2プログラムの正式経緯(本packet自体の位置づけ確認用、Trial-12の技術判断には直接関係しない) |

---

## (f) 入力文字数の自己計測欄(Python `len()`実測)

- (a)論点セクション: 2,860字(見出し行含む、次見出し直前まで)
- (b)主要数値表・要点セクション: 5,122字
- (c)Production code/spec抜粋セクション: 3,606字
- (d)Sonnet要約セクション: 778字
- (e)Progressive Disclosure指示文(候補一覧含む): 1,666字
- (f)本セクション自体: 約520字(自己参照的な数値記載のため概算)
- packet合計文字数(本ファイル全体、Python `len()`実測): **約15,200字**(RECONCILE-03の確定情報を反映した最終版。この行自体の追記による数文字の誤差を含む概算)
- (参考)雛形自体の文字数(未記入状態): 2,637字
- (参考)Before代替値(`FAMILY-A-COMPLETION-A4-DISCOVERY-DESIGN-OPUS-REVIEW-01`のOpus実読込文字数): 135,397字
- (参考)本packet(約15,200字)はBefore代替値の約**11.2%**
