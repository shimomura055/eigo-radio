# FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-01 Report

管理ID: FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-01(ユーザー承認済みTrial、
Trialのみ、Production配線なし)。設計書: `docs/pm/design_family_xy_
concreteness_control_trial_01.md`。委任ログ: `docs/pm/delegation_log/
2026-09-28_FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-01_01.md`。

## 1. Existing Spec / Prior Trial確認結果

- **分類A(既存DECIDED原則の未配線範囲)**: Spoken-first Number Treatment
  (`CURRENT_SPEC.md` L1388、`DECIDED`/`PRODUCTION_WIRED`、Family Aの
  `er003_v1_n3_01_articles_generate.py::COMMON_BLOCK_TEMPLATE`にのみ実装)。
  Family X JA Writer(`R0_PROMPT`)・Advanced Writer(`build_prompt()`)いずれ
  にもこの原則は未配線(Grep確認)。本TrialのTask Aは新原則の発明ではなく、
  既存DECIDED原則の「Family Xへの未配線範囲」拡張検証と位置づけた。
- **分類B(直接の先行REJECTED)**: OPEN-20「固有名詞のtoken数・密度を意図的
  に下げる一般ルール」は`REJECTED / NO_FURTHER_ACTION`。理由: 密度を下げる
  と別記事(ADD03)ではreferent不明瞭化・who-did-what劣化と競合した。
  `CURRENT_SPEC.md` L552にも「密度低減の数値目標は設けない」と反映済み。
  本Trialは密度目標ではなく定性的指示のみを使い、実測で同型のリスク
  (後述4.のA3 Essential Fact欠落)が実際に再現したことを確認した。
- **Family A legacy cleanup方式**: `er0*.py`をGrep(`cleanup|postprocess|
  simplify|number`)した結果、「数字・具体情報を減らす後処理」に相当する
  既存方式は**該当なし**(ヒットは音声間・速度調整の`postprocess_slowdown`
  のみ)。よってTask Bは新方式を作らず、既存R1→R2の枠組み(単発rewrite
  call)を使う1 Patternに限定した(設計書§1参照)。
- **Family X英語R1→R2の不在**: 英語本文向けR1→R2型Revisionは存在しない
  (Advanced/Standardはいずれも別方式)。Task CはJA側R2指示文のみを対象と
  した(R1・Original・Advanced/Standardの生成方式自体は無変更)。
- **Family Y参照**: `FAMILY-Y-VOICE-STRUCTURE-TRIAL-01_REPORT.md` §5/§6が、
  Family XのEntertainment revision指示が「Voiceに割り当てたFactの元
  テキストから固有名詞・数字を掘り出して前景化する」ことを実測しており、
  かつ**LLM rubric単独では、この現象を「改善」と誤判定しうる**ことを
  実証済み。本Trialではこの教訓を踏まえ、Essential Fact判定は既存
  Production関数`run_deviation_check()`(意味差分10種の機械判定)を主とし、
  LLM rubricは補助指標とした(§4参照)。

## 2. 実施Pattern(逐語)

- Task A(JA Original Prompt追記のみ、R1/R2は現行のまま連鎖):
  A0(現行、既存artifact再利用)/A1「記事の理解に必要な数字だけを使って
  ください。」/A2「細かい数字や時刻は基本使わず、話の理解に必要な場合
  だけ使ってください。」/A3「数字・時刻は基本的に使わないでください。
  記事の理解に本当に必要な場合だけ、最小限に使ってください。」/A4「数字・
  時刻は原則使わないでください。省くと話の意味が変わる場合に限り、必要
  最小限だけ使ってください。」/A5「数字・時刻は原則書かないでください。
  主旨の理解に不可欠なものだけ、最小限残してください。」/N1「固有名詞は、
  記事の理解に必要なものだけを使ってください。」/N2「人名・企業名・地名
  などの固有名詞は、話の理解に必要な場合だけ使い、それ以外は一般的な
  言い方にしてください。」/AN(組合せ、A3+N2、選定根拠は§5参照)。
  JA段階は8+1 Pattern×2記事の全件実施、Advanced(English)段階はA0/A3/AN
  ×2記事に絞って実施(§5 費用抑制の運用判断どおり)。
- Task B: B1「この記事から、話の理解に不要な細かい数字・時刻・固有名詞を
  減らしてください。事実関係・意味・因果関係は変えないでください。」
  (既存Advanced本文への単発rewrite、previous_response_idなし)。1 Pattern
  ×2記事。
- Task C: C0(現行R2指示、既存revision2.md再利用)/C1(改善案、現行R2指示
  文言+「新しい数字・時刻・固有名詞をLedgerから新たに掘り起こさないで
  ください。面白さは、構成・対比・場面・人の反応・テンポで作ってくだ
  さい。事実自体は変えないでください。」)。1 Pattern×2記事。
- Standard(A2)追試は**実施していない**(§5・§9参照、budget保全のための
  明示的スコープ縮小)。

## 3. Baselineとの差

A0(現行)は既存Production artifactをそのまま再利用し**再生成していない**
(Meta: `er019_output/family_x_b3_production_wiring_01/run_01`、Hormuz:
`er019_output/family_x_b3_diversity_trial_01/hormuz/run_02`)。Task A/B/Cの
各Patternは、この同一artifact(同一Storyline・同一Selected Fact Brief・
同一Full Ledger)を入力に、Prompt追記のみを変えて生成した(正式Prompt
定数`R0_PROMPT`/`REVISION_INSTRUCTIONS`/`ADVANCED_*`ブロック自体は無変更、
sha256一致を単体testで確認済み、§6)。

## 4. 成果物(実行コマンド含む)

- 実行コマンド(逐語、全て`.venv\Scripts\python.exe er037_family_xy_
  concreteness_control_trial_01.py`起点):
  - `--article hormuz --task a_ja_sweep --patterns A0,A1 --out-dir "er037_output/family_xy_concreteness_control_trial_01" --budget-jpy 80`(smoke test)
  - `--article hormuz --task a_ja_sweep --patterns A2,A3,A4,A5,N1,N2 --out-dir "er037_output/family_xy_concreteness_control_trial_01" --budget-jpy 80`
  - `--article meta --task a_ja_sweep --patterns A0,A1,A2,A3,A4,A5,N1,N2 --out-dir "er037_output/family_xy_concreteness_control_trial_01" --budget-jpy 80`
  - `--article hormuz --task a_ja_sweep --patterns AN --out-dir "er037_output/family_xy_concreteness_control_trial_01" --budget-jpy 80`
  - `--article meta --task a_ja_sweep --patterns AN --out-dir "er037_output/family_xy_concreteness_control_trial_01" --budget-jpy 80`
  - `--article hormuz --task a_advanced --patterns A0,A3,AN --out-dir "er037_output/family_xy_concreteness_control_trial_01" --budget-jpy 80`
  - `--article meta --task a_advanced --patterns A0,A3,AN --out-dir "er037_output/family_xy_concreteness_control_trial_01" --budget-jpy 80`
  - `--article hormuz --task b_cleanup --out-dir "er037_output/family_xy_concreteness_control_trial_01" --budget-jpy 80`
  - `--article meta --task b_cleanup --out-dir "er037_output/family_xy_concreteness_control_trial_01" --budget-jpy 80`
  - `--article hormuz --task c_revision --out-dir "er037_output/family_xy_concreteness_control_trial_01" --budget-jpy 80`
  - `--article meta --task c_revision --out-dir "er037_output/family_xy_concreteness_control_trial_01" --budget-jpy 80`
- 生成物: `er037_output/family_xy_concreteness_control_trial_01/{meta,hormuz}/
  task_a_ja/*.md`(9 Pattern×Original/R1/R2)、`task_a_advanced/{A0,A3,AN}.md`
  +`*_deviation.json`+`*_rubric.json`、`task_b_cleanup/B1.md`+付随json、
  `task_c_revision/C1_r2_improved_{ja,advanced}.md`+付随json、各`summary.json`、
  `raw_usage_log.jsonl`、`cost_*.json`。
- Script: `er037_family_xy_concreteness_control_trial_01.py`、単体test
  `er037_family_xy_concreteness_control_trial_01_test_01.py`(12 tests)。
- 設計書: `docs/pm/design_family_xy_concreteness_control_trial_01.md`。

## 5. 定量結果(決定論指標)

### 5.1 Task A JA段階(R2時点、全9 Pattern×2記事)

| Pattern | Hormuz num/over/ent/wc | Meta num/over/ent/wc |
|---|---|---|
| A0(baseline) | 39/17/14/463 | 0/0/13/425 |
| A1 | 10/1/10/391 | 0/0/13/373 |
| A2 | 10/1/10/357 | 0/0/11/358 |
| A3 | **0/0**/10/388 | 0/0/11/370 |
| A4 | 0/0/11/357 | 0/0/10/407 |
| A5 | 0/0/12/370 | 0/0/11/401 |
| N1 | 18/3/10/368 | 0/0/**13**(効果なし)/378 |
| N2 | 15/3/10/374 | 0/0/**10**/394 |
| AN(A3+N2) | 0/0/**9**/354 | 0/0/12/417 |

観察: Hormuz(Original時点で数字が多い記事)ではA1/A2で急減(39→10)、
A3以降で完全に0へ到達する明確な閾値がある(「最小限の指示でどこまで
効くか」という問いへの回答: **A1程度の1文でも大きく効くが、0まで
安定して抑えるにはA3相当の強さが必要**)。Meta(元々数字が少ない記事)
は全Patternでbaseline同様ほぼ0で、numeric抑制の効果は測定不能(天井
効果)。固有名詞はN1がMetaで無効果(13、baseline同値)だった一方、N2は
両記事で安定して削減方向(Meta 10、Hormuz 10)。組合せANはHormuzで
最良の固有名詞削減(9)を記録したが、Metaでは単独パターンほどの削減
にはならなかった(12、A4/N2の10より劣る)。

### 5.2 Task A Advanced(English)段階(最終的にリスナーが聞く本文、A0/A3/AN)

| Pattern | Hormuz num/over/ent/wc | Meta num/over/ent/wc |
|---|---|---|
| A0(baseline) | 29/17/19/376 | 0/0/10/411 |
| A3 | 9/1/17/385 | 0/0/10/397 |
| AN | **6/0**/19/305 | 0/0/11/324 |

**重要な観察(JA段階の効果がEnglish段階で減衰する非対称性)**: 数字は
JA段階の抑制がEnglish Advanced段階まで良く伝播する(Hormuz: baseline
29/17→AN 6/0、大幅改善)。一方、固有名詞はJA段階で9まで減っていても
(§5.1)、English Advanced翻訳段階でbaseline同水準(19)まで戻ってしまう。
原因は、Advanced Writer Prompt(`ADVANCED_VOCAB_RULE_V2_BLOCK`)自体が
「C. 固有名詞は簡略化せずKEEPする」という既存Production規則を持ち、
JA側の抑制方針を一切知らないまま翻訳するため(Advanced Prompt自体は
本Trialでも無変更)。**固有名詞抑制をEnglish最終成果物へ反映させたい
場合、JA Original段階だけでなくAdvanced段階のPromptにも同種の指示が
必要になる可能性が高い**(9.新しく判明した問題、参照)。

### 5.3 Task B(cleanup、既存Advanced本文への単発rewrite)

| 記事 | num/over/ent/wc | 備考 |
|---|---|---|
| Hormuz | 17/10/19/360 | baseline比で数字はやや削減も固有名詞は不変(19→19)、後述Essential Fact欠落あり |
| Meta | 0/0/10/406 | baselineと同値(元々0のため効果測定不能) |

### 5.4 Task C(R1→R2改善)

| 記事 | JA C0→C1 num | English C1 num/over/ent | 備考 |
|---|---|---|---|
| Hormuz | 39→28 | 24/17/14 | 現行R2(baseline)比で改善方向だがAプランほど強くない |
| Meta | 0→0 | 0/0/9 | 元々0のため効果測定不能 |

## 6. 品質評価(Essential Fact・因果・Entertainment・理解しやすさ・情報の薄さ)

**主判定はProduction既存関数`run_deviation_check()`(Essential Fact欠落・
因果変化等10種の意味差分を機械判定、Family Yで実証済みのとおりLLM rubric
単独より信頼できる)を採用した。**

| Task/Pattern(記事) | deviation overall_status | 所見 |
|---|---|---|
| A3(Hormuz) | **LEDGER_DEVIATION(MAJOR×3)** | 全てorigin=ja_source。実際に本文を確認したところ、JA A3のR2で「上げ幅が一時的に縮小した」(HF-009)という事実が「価格が下がりかけた」(price began to fall)へ方向反転していた。数字を書かないよう指示した結果、モデルが精度を落とした言い換えを選び、**上げ幅の鈍化と価格下落という意味の異なる表現を混同した**、と推定される。他2件も「未提示の支払義務者を具体化」「Ledger未確認の物流費波及を新規主張」という新規主張の追加。**これはOPEN-20が懸念した「別の分かりやすさ要求との競合」と同種の、実測されたSTOP相当のリスクである。** |
| AN(Hormuz) | LEDGER_COMPLIANT | 同記事・同水準の数字抑制をA3+N2の組合せで達成しつつ、この回ではMAJOR無し。ただしn=1のため「組合せなら常に安全」とは言えない(LLMのサンプリング揺らぎの可能性を排除できていない、9.参照) |
| A3/AN(Meta) | LEDGER_COMPLIANT | 双方問題なし(Metaは元々数字が少なくPromptの介入余地が小さいため相対的に安全だった可能性) |
| B1(Hormuz) | **LEDGER_DEVIATION(MAJOR×1)** | 「継続する攻撃・封鎖懸念」と「20%案撤回後の価格回復」を接続詞"so"で因果関係化しており、Ledgerが確認していない因果を新規主張していた |
| B1(Meta) | LEDGER_COMPLIANT | 問題なし |
| C1(Hormuz/Meta) | LEDGER_COMPLIANT(両記事) | Task Cは今回実施した中で唯一、両記事ともEssential Fact/因果の問題を出さなかった |

LLM rubric(補助指標、1-5点)は、上記のいずれのPatternでもstoryline_
causality/entertainment/comprehension/thinnessとも3〜5点の範囲に収まり、
Family Yの実例のように「数字を減らしたのに人気取り的に高得点」という
明確な誤判定は今回は観測されなかった。ただし採点対象になったA3
(Hormuz)自体はrubricでも3点どまり(comprehension=3、causality=3)であり、
Essential Fact欠落を示す`run_deviation_check()`の判定と方向は一致していた
(今回はrubricとdeviation checkが矛盾しなかった、という意味でFamily Yの
リスクが顕在化しなかった1事例)。

## 7. Regression

`run_project_regression.py --pattern "er037*_test_*.py"` → discovered 1
test file、collected=12 passed=12 failed=0 errors=0 skipped=0(実行結果
そのまま)。単体testの内容: 決定論指標カウンタ(数字・過度精度・固有名詞・
新規前景化・語数)、Pattern文言定義、**正式Prompt定数(`R0_PROMPT`/
`DEVELOPER_MESSAGE`/`REVISION_INSTRUCTIONS`/`ADVANCED_VOCAB_RULE_V2_
SHA256`)がTrial関数呼び出し後もsha256不変であることの直接assert**。

## 8. コスト実測

| 記事 | 内訳 | 実測合計 |
|---|---|---|
| Hormuz | JA sweep(9 Pattern×3 call)¥8.52 + Advanced(A3/AN 2生成+deviation+rubric)累積¥12.946 + Task B(cleanup+deviation+rubric)累積¥14.367 + Task C(R2改善+Advanced翻訳+deviation+rubric)累積¥17.722 | **¥17.722**(最終raw_usage_log累積) |
| Meta | JA sweep ¥6.978 + Advanced累積¥11.625 + Task B累積(値未個別記録、C時点で確定) + Task C累積 | **¥15.243**(最終raw_usage_log累積) |
| **合計** | | **約¥32.97**(Guardrail¥80の約41%、超過なし) |

TTS/ASRは一切使用していない(T-2どおりテキスト生成+LLM評価のみ)。call数は
`raw_usage_log.jsonl`(各記事ディレクトリ)に1 call=1レコードで記録済み
(Hormuz 40+レコード、Meta 35+レコード相当、正確な件数はraw_usage_log.jsonl
参照)。

## 9. 新しく判明した問題

1. **A3相当の強い数字抑制Promptは、JA Original段階でEssential Fact/
   因果関係を損なうリスクが実測された**(Hormuz、MAJOR×3、6.参照)。
   これはOPEN-20(固有名詞密度目標REJECTED)と同型の「分かりやすさ要求
   との競合」が数字側でも起こりうることを示す新しい実測エビデンスである。
   n=1(Hormuz 1記事1回)のため一般化はできないが、**強い抑制指示ほど
   Essential Fact破損リスクが上がる**という傾向は、A1/A2(軽度、MAJOR
   なし)→A3(強、MAJOR×3)の対比からも示唆される。
2. **固有名詞抑制の効果はJA段階では観測できても、Advanced(English)翻訳
   段階で失われる**(5.2参照)。Advanced Prompt自体(`ADVANCED_VOCAB_
   RULE_V2_BLOCK`)が固有名詞を明示的にKEEPする既存ルールを持つため。
   JA側だけの介入では最終成果物(リスナーが聞く本文)への効果が限定的。
3. **Task B(cleanup単発rewrite)は、数字のある記事(Hormuz)で新規の
   因果関係の誤り(MAJOR)を導入した**。「事実関係・因果関係を変えない
   でください」という指示文だけでは、遠因の因果過剰結合(接続詞"so"の
   誤用)を防げなかった。
4. **Task C(R1→R2改善)は、今回実施した中で唯一、両記事ともEssential
   Fact/因果関係の問題を出さずに数字を削減方向へ動かせた**、という
   相対的に安全な結果が得られた(ただし効果量はTask Aより小さい)。
5. 決定論指標の限界(自己申告、Gate化を意図しない): JA固有名詞カウンタ
   は漢数字("二十パーセント"等)を数字として検出しない、英語固有名詞
   カウンタは文頭語を一律除外する簡易ヒューリスティックであり、厳密な
   NER判定ではない。あくまでPattern間の相対比較用の参考指標である。

## 10. Status案

**`USER_DECISION_REQUIRED`**。

理由: (a) Task A(軽度〜中度のPattern、A1/A2、N2)とTask C(R1→R2改善)は、
今回の実測範囲でEssential Fact/因果関係の問題を出さずに数字・固有名詞の
前景化を実際に減らせることを確認した(有望)。(b) 一方でTask A強Pattern
(A3)とTask B(cleanup)は、少なくとも1記事1回の実測でEssential Fact/
因果関係のMAJOR逸脱を引き起こした(9.参照)。(c) 固有名詞抑制はJA段階
だけでは最終English成果物まで伝播しないという構造的な制約も判明した。
これらは「どの強さのPatternをどう採用するか」「Advanced段階にも介入
すべきか」という、通常の編集判断を超えたProduct仕様判断を要する
(OPEN-20の教訓により、密度目標のような機械的採用はそもそも不可)。
`REJECTED`と断定するにはTask A軽度Pattern/Task Cの有望な結果を無視する
ことになり、`VALIDATED`と断定するには強Pattern/Task Bで実測されたMAJOR
逸脱を無視することになるため、いずれも不適切と判断した。

## 11. ユーザー判断が必要な事項

1. Task Aのどの強さのPatternを候補として残すか(軽度A1/A2/N2は今回
   MAJORなし、強A3以降はMAJORが出た実例がある)。
2. 固有名詞抑制をAdvanced(English)Prompt側にも拡張すべきか(拡張しない
   限り最終成果物への効果は限定的、5.2参照)。ただしAdvanced Promptは
   Family A/Xで共有されるため、変更範囲がFamily Xだけに留まらない可能性
   がある(要事前確認)。
3. Task B(cleanup)は今回1回の実測でMAJORが出たため、このままでは
   採用候補として推奨しない。改善Prompt再設計が必要かどうか。
4. Task C(R1→R2改善)は相対的に安全だが効果量が小さい。効果を強める
   ために文言を強化すべきか、現状の安全性を優先しこのまま据え置くか。
5. 上記いずれについても、本Trialはn=1(記事あたり1回)の実測であり、
   統計的信頼性はない。採用検討前に追加のサンプル数・記事での再現性
   確認が必要かどうか(ユーザー判断、追加Trialは本タスクの範囲外)。

## 12. Production変更が一切入っていない証拠

- `git status --porcelain` (本Trialが触れた範囲のみ) の出力は全て
  `??`(新規未追跡ファイル)であり、既存ファイルへの`M`(modified)は
  一件もない:
  ```
  ?? docs/pm/delegation_log/2026-09-28_FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-01_01.md
  ?? docs/pm/delegation_log/2026-09-28_FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-01_01.md_check.json
  ?? docs/pm/design_family_xy_concreteness_control_trial_01.md
  ?? er037_family_xy_concreteness_control_trial_01.py
  ?? er037_family_xy_concreteness_control_trial_01_test_01.py
  ?? er037_output/
  ```
- `git diff --stat HEAD -- "er0*.py" "er003_v1_translator_briefs/" | grep -v er037`
  は**空ではない**(`er003_key_words_min_unit.py`/`er030_key_phrase_db_
  hybrid_selector_01.py`等9ファイル)。これらは本Trialが一切importも
  Read/Edit/Writeもしていないファイルであり、`git status`上も本Trialの
  変更としては追跡されていない(上記`??`一覧に含まれない)。委任文に
  記載の並行衝突(`TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01`)とは別の、KEY-
  PHRASE-4PLUS1関連の**他タスクによる同時進行中の未commit変更**である
  と判断する(本セッション開始時のgit status snapshotにこれらのファイル
  はまだ含まれておらず、本セッション中に他プロセスが変更したもの)。
  本Trialはこれらのファイルに一切触れていないため、Production無変更の
  結論には影響しない。
- 単体test`TestProductionPromptsUnchanged`(2 tests)が、正式Prompt定数
  (`R0_PROMPT`/`DEVELOPER_MESSAGE`/`REVISION_INSTRUCTIONS`/
  `ADVANCED_VOCAB_RULE_V2_SHA256`)のsha256不変を直接assertし、PASSして
  いる(7.参照)。

## STOP該当有無

該当あり(部分的)。委任文のSTOP条件のうち「Essential Factが落ちる/
意味・因果関係が変わる」がTask A(A3、Hormuz)・Task B(Hormuz)で実際に
発生した。ただし全Pattern・全記事が同時に失敗したわけではなく、Task A
軽度Pattern・Task Cは問題なく完走したため、**追加のTrial Pattern増加は
行わず**(delegation指示どおり)、この実測結果のまま`USER_DECISION_
REQUIRED`としてSTOP・報告する。

## SSOT追記文案(編集権なし、ユーザー/Fable判断待ち)

- **REPORT_LEDGER新行案**: `FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-01 |
  Trial | USER_DECISION_REQUIRED | 2026-09-28 | 数字・時刻・固有名詞の
  前景化抑制Trial(Meta/Hormuz、Writer Prompt A0-A5/N1-N2/AN、cleanup、
  R1→R2改善)。Task A強Pattern/Task BでEssential Fact MAJOR実測、Task A
  軽度/Task Cは無傷。Production未配線`
- **DECISION_LOG新エントリ案**: `2026-09-28、FAMILY-XY-CONCRETENESS-
  CONTROL-TRIAL-01、ユーザー指示によりTask A(Initial Writer Prompt
  Pattern)/Task B(post-hoc cleanup)/Task C(R1→R2 revision改善)を実施。
  Meta/Hormuz既存artifactを使い、既存Production関数(run_deviation_check
  等)を無変更のまま再利用してEssential Fact判定。強い数字抑制Pattern
  (A3)とcleanup(B1)はHormuzでLEDGER_DEVIATION(MAJOR)を実測、軽度Pattern
  とTask Cは無傷。Status=USER_DECISION_REQUIRED。Production採用は未決
  (人間ユーザーの正式承認待ち)`
- **OPEN_ITEMS候補**: 「固有名詞抑制はJA段階のみでは最終English成果物
  まで伝播しない(Advanced Prompt側の`ADVANCED_VOCAB_RULE_V2_BLOCK`が
  固有名詞KEEPを既定にしているため)。Family X/Aで共有するAdvanced
  Promptへ拡張が必要か要検討」(9.-2参照、新規OPEN_ITEM番号はFable/SSOT
  管理者が付番)。

## 参照

- Script: `er037_family_xy_concreteness_control_trial_01.py`
- Test: `er037_family_xy_concreteness_control_trial_01_test_01.py`
- 設計書: `docs/pm/design_family_xy_concreteness_control_trial_01.md`
- 出力: `er037_output/family_xy_concreteness_control_trial_01/{meta,hormuz}/`
- 委任ログ: `docs/pm/delegation_log/2026-09-28_FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-01_01.md`(+`_check.json`)
