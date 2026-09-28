# FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-01 設計書

管理ID: FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-01(ユーザー承認済みTrial、Production配線なし)。

## §1 Existing Spec Check(実装着手前の必須確認)

### 分類

- **分類A(既に正式決定・Production配線済みの近接原則がある。今回はその「未適用範囲」への拡張検証)**:
  Spoken-first Number Treatment(`CURRENT_SPEC.md` L1388、`DECIDED`・`PRODUCTION_WIRED`、
  ER-003-A2-B1-N3-01 §14)。Importance(ANCHOR/SUPPORTING/DISPENSABLE)×Exactness
  (EXACT_REQUIRED/APPROXIMATE_OK/DIRECTION_ONLY)の2軸で「精度自体に意味のない数字」を
  丸め・概数化してよい、という原則が**Family A(Cross-level A2/B1/B2、
  `er003_v1_n3_01_articles_generate.py::COMMON_BLOCK_TEMPLATE`)には既に実装済み**。
  ただし実装箇所を確認した結果、Family X(Entertainment News)のJA
  Writer(`er019_family_x_ja_writer_o_r1_r2_01.py::R0_PROMPT`)にもAdvanced English
  Writer(`er003_v1_n3_01_advanced_adaptation_generate.py::build_prompt()`、Family
  X/Family A両方が共有する`generate_advanced_adaptation()`)にも、この原則は
  **一切含まれていない**(Grep確認、両ファイルに「数字」「概数」「ANCHOR」
  「EXACT_REQUIRED」等の一致なし)。よって本Trial Task Aは、新しい原則の発明ではなく、
  **既存DECIDED原則の「未配線範囲」(Family X)への適用可否を確認するTrial**と位置づける。
- **分類B(既に一度REJECTED判定が出ている、直接の先行Trial)**: OPEN-20
  (`[ER-003-A2-STRUCT-02] 固有名詞のtoken数・密度を意図的に下げる一般ルール`、
  `REJECTED / NO_FURTHER_ACTION`)。結論: 固有名詞のtoken数・密度を機械的に下げる
  一般ルールは、A01では固有名詞が減った一方、ADD03ではTrumpを明示的主語にした結果
  増加し、「誰が何をしたかを明確にする」「referentを明確にする」「spoken-firstに
  する」という**別の分かりやすさ要求と競合する**ことが判明した。結果、
  **数量目標・密度目標は設けず、記事理解上の必要性で通常の編集判断により決める**、
  という方針が確定している(`CURRENT_SPEC.md` L552のCEFR比較表にも
  「密度低減の数値目標は設けない(REJECTED、通常の編集判断に委ねる)」として反映済み)。
  **本Trialへの影響**: 固有名詞Pattern(N1/N2)を「数を減らすノルマ」として設計しては
  ならない。OPEN-20と同じ理由で不合格になる可能性が高い。本Trialでは、N1/N2を
  「密度目標」ではなく「理解に不要な固有名詞だけを避ける」という**定性的**指示に
  限定し、評価でも「単純に固有名詞が少ないほど良い」を採用しない(delegation指定の
  評価原則どおり)。REJECTED再現の兆候(referent不明瞭化・who-did-what劣化)が出た
  Patternは、たとえ数値が減っていても品質評価で不合格とする。
- **分類C(Family Xに既存名称があり、そのまま流用する箇所)**: 「Storyline決定+
  B3 Fact選定」(`er019_family_x_storyline_b3_fact_selection_01.py`)、Fact Ledger
  (`[VERIFIED] fact_id:`形式)、JA Original→R1→R2
  (`er019_family_x_ja_writer_o_r1_r2_01.py::run_ja_writer_o_r1_r2()`、
  `REVISION_INSTRUCTIONS`)、Advanced(Natural English Adaptation、
  `er003_v1_n3_01_advanced_adaptation_generate.py::generate_advanced_adaptation()`、
  Family X/Aで共有)、Ledger Deviation Check
  (`er003_v1_en_direct_vfl_01_generate.py::run_deviation_check()`、Essential
  Fact欠落・因果変化等10種の意味差分検出)。これら正式名称・関数をそのまま
  importして使う(新規実装・新名称は作らない)。

### Family A legacy 後処理(cleanup)方式の有無(Task B事前確認)

`er0*.py`全体をGrep(`cleanup|postprocess|simplify|number`、大小無視)した結果、
ヒットしたのはTTS発話速度調整(`a2_postprocess_slowdown`等、"postprocess"は
音声の間・速度調整を指す既存語彙)のみで、**「数字・具体情報を減らす後処理/
cleanup」に相当する既存方式はFamily A(legacy含む)に存在しない**(該当なし)。
OPEN-20の結論(密度目標のREJECTED)とも整合する(密度を下げる機械的処理自体が
一度否定されているため、そのための後処理も作られていない)。

**方針(Fable指定どおり)**: 新方式は作らず、既存R1→R2の枠組み(previous_
response_id連鎖、`call_with_previous_response_id()`、無変更import)を使い、
「削減指示のみ」の最小Pattern1つに限定する。Task Bは、既存Advanced本文
(`b1b/article.md`、production artifactそのまま)に対する**1回だけの単発
rewrite call**として実装し(新しい多段パイプラインは作らない)、Essential
Fact/Storyline維持を`run_deviation_check()`で確認する。

### Family X英語R1→R2の不在確認(Task C事前確認)

英語本文向けのR1→R2型Entertainment Revisionは存在しない(Advanced=Natural
English Adaptation、Standard=A2簡略化のみで、いずれもR1→R2型revisionでは
ない)。**Family XのR1→R2はJA本文にのみ存在する**
(`er019_family_x_ja_writer_o_r1_r2_01.py::REVISION_INSTRUCTIONS`)。Task Cは
このJA R1→R2の**R2指示文のみ**を対象にする(R1指示文・Original・Advanced/
Standardの生成方式自体は変更しない)。

### Family Y参照(数字・固有名詞前景化の実測先行証拠)

`FAMILY-Y-VOICE-STRUCTURE-TRIAL-01_REPORT.md` §5/§6: Family XのEntertainment
revision指示(「もっと/さらにエンターテインメント性の高い記事に修正してください」)
をVoice記事へ適用したところ、R2が「Voiceごとに割り当てたFactの元テキストから、
より詳細な固有名詞・数字を掘り出して前景化した」ことを実測(例:
「CVS Health」「HireVue」「Affectiva」「91%のHRリーダーが...」「Hilton」
「IBM」等がR2で新規に前景化)。**重要な追加観察**: LLM rubric 1callだけでは
この現象をBefore→R1→R2の「単調な改善」と誤判定したが、Family B既存の
field単位QA(`run_analytical_leakage_check_3v`、`leak_numbers_foreground`等)は
同じ箇所を明確にFAILと判定しており、**LLM rubric単独への依存はミスリードの
リスクがある**ことが実証されている。本Trialでは、`run_deviation_check()`
(意味差分の10種類を機械的に判定、モデルの自己申告に依存しない設計)を
Essential Fact/因果維持の主判定とし、Entertainment性・一度聞いての理解
しやすさ・情報の薄さのLLM rubric(1 call)は**補助指標**として扱う
(Family Yの教訓を踏まえた設計判断)。

## §2 対象記事・入力データの特定

| 記事 | source_dir | selected_storyline | Full Ledger | JA R1(revision1.md) | JA R2(revision2.md) | 既存Advanced(b1b/article.md) |
|---|---|---|---|---|---|---|
| Meta | `er019_output/family_x_b3_production_wiring_01/run_01` | `storyline_b3/fact_selection_evidence.json::selected_storyline` | `research_ledger/verified_fact_ledger.txt` | `ja_writer/revision1.md` | `ja_writer/revision2.md` | `b1b/article.md`(+`b1b/audit/deviation_check.json`を既存Essential Fact判定として再利用) |
| Hormuz | `er019_output/family_x_b3_diversity_trial_01/hormuz/run_02` | 同上 | 同上 | 同上 | 同上 | 同上 |

新規記事生成は行わない。Storyline/B3 Fact選定・Research/Ledger作成は再実行しない
(既存artifactをそのまま入力として使う)。

## §3 Trial script構成(`er037_family_xy_concreteness_control_trial_01.py`)

- 既存Production関数のimport(無変更): `er019_family_x_ja_writer_o_r1_r2_01`
  (`R0_PROMPT`/`DEVELOPER_MESSAGE`/`REVISION_INSTRUCTIONS`/`SYMBOL_PREVENTION_
  BLOCK_JA`/`build_original_prompt`/`call_fresh`/`call_with_previous_response_id`/
  `WRITER_MODEL`/`WRITER_EFFORT`)、`er003_v1_n3_01_advanced_adaptation_generate`
  (`build_prompt`/`ADVANCED_DEVELOPER`)、`er003_v1_en_direct_vfl_01_generate`
  (`run_deviation_check`/`deviation_audit_record`/`get_client`)、
  `er019_family_x_entertainment_production_runner_01`
  (`compute_stage_cost_breakdown`、cost集計の再利用)、`er005_cost_logger`
  (`install`、raw usage記録)。
- Pattern文言はTrial script内の定数として定義し、Original Promptまたは
  R2 revision指示へ**追記のみ**(既存定数`R0_PROMPT`/`REVISION_INSTRUCTIONS`
  自体は書き換えない、`.replace()`等での改変もしない)。
- CLI: `--article {meta,hormuz} --task {a,b,c} --patterns <comma list>
  --out-dir <dir> --budget-jpy <float>`。
- 決定論的指標(API不要): `count_numeric_tokens()`(`\d+`連続、時刻`H:MM`/
  日付/%/小数を別カウントでも重複集計する「過度な精度」カウンタ)、
  `count_proper_nouns_en()`(英語: 文頭以外の大文字始まり語、機能語
  stoplist除外)、`count_katakana_roman_entities_ja()`(日本語: カタカナ
  3文字以上の連続、ローマ字表記の企業名/人名相当)、`diff_new_tokens()`
  (前段階テキストに存在せずLedger原文には存在するが本文に新規出現した
  token集合、fabrication検出ではなくforeground検出)、`word_count()`。
- LLM評価: `run_deviation_check()`(Essential Fact欠落・因果変化の主判定、
  既存Production関数そのまま)+ 1 rubric call(Storyline/因果維持・
  Entertainment性・一度聞いての理解しやすさ・情報の薄さ、各1〜5+根拠引用、
  Trial専用の新規プロンプトだが「数字が少ないほど高得点」にしないことを
  developer messageで明示)。
- 出力: Pattern毎に生成text(.md)・決定論指標(.json)・LLM評価(.json)、
  `summary.json`/`summary.md`(Pattern×記事の比較表)。

## §4 実行Pattern(A0基準は既存artifact再利用、再生成しない)

Task A(JA Original Prompt追記、既存R1/R2 instructionは無変更のまま連鎖):
A0(baseline、既存`ja_writer/revision2.md`+`b1b/article.md`をそのまま使用、
再生成なし)/A1〜A5(数字・時刻抑制、ユーザー指定5文言)/N1・N2(固有名詞
抑制、ユーザー指定2文言)/AN(A・N最良1組み合わせ、A1〜A5・N1・N2の
JA段階の結果を見てから選定)。

Task B(既存Advanced本文への単発cleanup rewrite、1 Pattern限定):
B1「この記事から、話の理解に不要な細かい数字・時刻・固有名詞を減らして
ください。事実関係・意味・因果関係は変えないでください。」(削減指示のみ、
新方式を作らない)。

Task C(JA R2 revision指示のみ差し替え、R1までは既存`revision1.md`を再利用):
C0(現行R2指示、既存`revision2.md`をそのまま使用、再生成なし)/C1(改善案、
「新しい数字・時刻・固有名詞をLedgerから新たに掘り起こさないでください。
面白さは、構成・対比・場面・人の反応・テンポで作ってください。事実自体は
変えないでください。」)。

## §5 費用抑制の運用判断(Trial限定)

実測コスト(Meta run_01 `cost.json`): `ja_original`≈¥0.235、`ja_r1`≈¥0.243、
`ja_r2`≈¥0.26(JA 1chainで約¥0.74)、`advanced`≈¥7.84(生成+deviation
check込み)。この実測値に基づき、Task Aの決定論指標比較はJA段階(安価、
8 Pattern×2記事で約¥12)を主として全Pattern実施し、Advanced(English)
段階への展開(1 Patternあたり約¥8)は、JA段階の結果から**最有力Pattern
(AN、1件)のみ**を2記事で実施する(Standard(A2)への追試は本Trialでは
実施しない、budget保全のためのスコープ縮小として報告する)。Task B/Cは
各1 Patternのみのため全額Advanced実行する。合計見積り: 約¥60〜75
(§6実測値で確定)。Production既定`reasoning_effort`はJA Writer呼び出しに
限り既存`WRITER_EFFORT`("high")をそのまま使う(Family X既存関数の挙動を
変えないため)。LLM rubric(Trial専用新規呼び出し)のみ`effort="medium"`を
明示指定する(Family Yと同じ費用抑制判断)。
