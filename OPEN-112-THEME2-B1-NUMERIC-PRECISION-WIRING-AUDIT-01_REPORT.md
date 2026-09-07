# OPEN-112-THEME2-B1-NUMERIC-PRECISION-WIRING-AUDIT-01 実行報告

**種別: 読み取り専用の診断調査。コード・SSOT・出力ファイルの編集、TTS/LLM API呼び出し、
Git操作はいずれも実施していない。**

## 1. 結論(先出し)

**分類: 1(配線済みかつAI判断)。ただし、実際に承認済み完成音声(rerun_03)へ使われた
本文テキストは、承認済みNumeric Precision原則の「レベル非依存の既定強化ブロック」
(2026-09-07配線)より前(2026-09-05生成)のテキストであり、その強化ブロックを配線した
Production経路へ同一素材を通し直すと、実際に25.2%→about 25%・44.7%→about 45%へ
丸められることを実データで確認した。**すなわち、「未配線」ではないが、「配線済みの
より弱い版」で生成された既存テキストが、その後の配線強化を反映しないまま承認済み
完成音声として残っている、という状態である。

## 2. 仕様の正式ID・原文・適用スコープ

正式仕様は2段階で存在する。

### 2-1. 土台(2026-09-04配線、ER-011-NO18-EVIDENCE-COMPRESSION-A-PRODUCTION-WIRING-AND-FINAL-CANDIDATE-AUDIO-21R)

`er003_v1_n3_01_evidence_compression_editor.py::LISTENER_FRIENDLY_NUMERIC_PRECISION_BLOCK`
(Production Evidence Compression Editor、方式C)。原文(抜粋):
> 残す価値があると判断した数値について、意味(比較方向・story上の大きさ・閾値・解釈・
> 値同士の区別)が変わらない場合のみ、より単純な概数を優先してよい。小数の機械的削除は
> 禁止、丸めが意味のある差・閾値・小規模測定・解釈・区別を損なう場合は小数を保持する。
> …This is a judgment rule, not a mechanical one.

適用スコープ: `er003_v1_n3_01_articles_generate.py::run_one_pattern()`(Writer初回生成
+ Diagnostic Full Retry双方から共通で呼ばれる単一のEditor呼び出し箇所)経由で、A2/B1
双方の本文全section(Main Story・Point One・Point Two等)に適用される。CEFR別分岐なし。

### 2-2. 強化ブロック(2026-09-07配線、ER-011-PREVIEW-ROLE-AND-NUMERIC-PRECISION-PRINCIPLE-PRODUCTION-WIRING-01、ユーザー`APPROVED_FOR_PRODUCTION`)

`er003_v1_n3_01_evidence_compression_editor.py::NUMERIC_PRECISION_LEVEL_INDEPENDENT_DEFAULT_BLOCK`
(既存ブロックの直後に挿入、既存ブロックは書き換えず補強)。原文(タスク背景に引用された
文言と完全一致、確認済み):
> 原則: 聞き取りやすさを優先し、意味を損なわない範囲では概数を基本とする。小数点以下を
> 保持するのは、その精度自体が記事の意味・比較・判断に必要な場合に限る。通常は次のように
> 概数化することが既定である: 25.2% → about 25%、44.7% → about 45%、89.6% → about 90%。
>
> 小数点以下を保持してよい例: 閾値の前後が論点になっている場合(例えば49.5%と50.5%の
> ように、僅差自体が意味を持つ場合)、年次変化・比較差を精密に扱う必要がある場合、
> 小数を落とすと記事の意味・結論が変わってしまう場合。
>
> This default applies equally regardless of CEFR level (A2/B1/B2). There is no
> level-specific numeric precision rule.

同一文言(日本語1文)がWriter共通Prompt`er003_v1_n3_01_articles_generate.py::
COMMON_BLOCK_TEMPLATE`「Spoken-first原則(数字の扱い)」C項にも実コードとして存在する
ことを確認した(下記grep結果)。
```
C. Exactnessが不要な場合は丸めてよい。聞き取りやすさを優先し、意味を損なわない範囲では
   概数を基本とする(例: 25.2%→about 25%、44.7%→about 45%、89.6%→about 90%)。小数点
   以下を保持するのは、その精度自体が記事の意味・比較・判断に必要な場合に限る(…)。
   この既定はCEFRレベル(A2/B1/B2)に関わらず共通であり、レベル別の別ルールではない。
```

適用スコープ: 2-1と同一経路(A2/B1双方の本文全section)。News/Trend/Editorial型で
出し分けるコード分岐は存在しない(`er003_v1_n3_01_evidence_compression_editor.py`・
`er003_v1_n3_01_articles_generate.py`はジャンル非依存の共通モジュール)。CURRENT_SPEC.md
110行目も「CEFR別の簡略化ルールなし」と明記しており、本文への適用範囲がPreview限定である
という記述はどこにも無い(Preview分量原則とNumeric Precision原則は同じ2026-09-07タスクで
一緒に配線されたが、別々の仕様であり、Numeric Precisionは元々本文向けの既存ルールの補強)。

## 3. 結論の根拠(タイムライン、実データで確認)

| 日時 | 出来事 |
|---|---|
| 2026-09-04 | ER-011-NO18-EVIDENCE-COMPRESSION-A-PRODUCTION-WIRING-AND-FINAL-CANDIDATE-AUDIO-21R(commit `ca3f4a6`)。Pattern A + Listener-Friendly Numeric Precision(2-1)をProduction配線。 |
| 2026-09-05 23:48 | Theme 2 B1 article.md 生成(`er011_output/open112_trend_theme2_b_full_audio_trial_13/b1b/article.md`、mtime確認済み)。この時点で2-1のみが有効な仕様。Editorが25.2%/44.7%を保持する判断をした。 |
| 2026-09-06 20:38 | rerun_02(commit `7579d3f`)。article.mdはtrial_13と`diff`完全一致(bit-for-bit、テキスト再生成なし)。 |
| 2026-09-07 09:22 | ER-011-PREVIEW-ROLE-AND-NUMERIC-PRECISION-PRINCIPLE-PRODUCTION-WIRING-01(commit `046c2ab`)。強化ブロック(2-2)を配線。ユーザー`APPROVED_FOR_PRODUCTION`。 |
| 2026-09-07 19:59 | rerun_03(commit `f2a4f9f`、「配線後Production pathでPASSしたFSP1を組み込みTheme 2 B1をrerun_03へ再Assembly」)。article.mdはtrial_13/rerun_02と`diff`完全一致(テキスト再生成なし、FSP1[false start]音声segmentの差し替えと再Assemblyのみ)。 |

すなわち「配線後」という表現は、rerun_03のcommitメッセージが指すFSP1(narration
false start)修正の配線を指しており、Numeric Precision強化ブロックの配線とは無関係。
**rerun_03の本文テキストはNumeric Precision強化ブロック配線より前(2026-09-05)に
生成されたまま一度も再生成されていない。**

Numeric Precision強化ブロック配線タスク自身のRuntime evidence
(`er011_output/preview_role_numeric_precision_wiring_01/numeric_precision_evidence.json`)
で、**trial_12のB1 pre-editor原稿(rerun_03と同一Fact由来の同一草稿)を、強化ブロック
入りの実Production関数`run_lossless_editor()`へ実際に1回通し直した結果**:
- `Men aged 29 and under put solo travel at 25.2%` → `about 25%`
- `hobby-focused travel showed a similar pattern` → `was also about one quarter`
- `44.7% were still interested` → `about 45% were still interested`
と、ユーザーが望む方向(25%/45%程度)に実際に丸められることを確認した。

同じ実データで、この再実行は数値以外の言い回しにも変化(non-deterministic judgment
ruleのため、"seem to want more room" vs "seem to want trips with more room"等)を
伴うことを`diff`で確認した(下記5-3参照、修正方式の判断材料)。

## 4. 小数点数値の一覧(rerun_03 article.md / parts.json、実データ)

| 値 | section(segment) | Ledger元データ |
|---|---|---|
| 25.2% | Point One本文(`point_one_body`、narration `point_one.wav`) | F-202、日本交通公社「Z世代の暮らしと旅」調査2025、男性29歳以下「ひとり旅」25.2%(一次資料が小数第1位まで開示) |
| 44.7% | Point Two本文(`point_two_body`、narration `point_two.wav`) | F-202、同調査、女性29歳以下「有名な観光地を巡る」44.7% |
| 1.8 nights(参考、丸め対象外として本文で維持) | Main Story本文(`part1`) | 別調査(Jalan系、平均泊数)。ユーザー質問の対象ではないが本文に残る小数として記載。本タスクではNumeric Precision違反の指摘対象としていない(値自体が小さく閾値未満のため丸めが困難、かつユーザー指摘は25.2%/44.7%の2件) |

参考として、同一Ledgerの他の値のうち、記事本文で既に近似値表現になっているもの:
- 約90%/約80%(F-203、観光庁調査。**一次資料自体が「約」付きの概数**であり、
  Editorが丸めたのではなくLedger原本の精度をそのまま保持している。Fact fidelity上
  正しい挙動であり、Numeric Precision原則の対象外)
- 24.3%(F-202、男性「趣味を深める旅行」)→ B1本文では"showed a similar pattern"
  へPattern A圧縮済み(数値自体が本文から消えている、25.2%とは別の扱い)

A2側(参考、別Fact Ledger deviation対象外): 同一Fact(25.2%/44.7%)はA2記事では
`about 25%`/`about 45%`へ既に丸められていることを`OPEN-112-THEME2-AUDIO-REVIEW-FIX-02
-PREVIEW-NUMERIC_REPORT.md`で確認済み(2026-09-07調査時点の既存Production出力)。

## 5. 修正案(実装はしていない)

### 5-1. 選択肢A: 手動・決定的な文字列置換(最小変更)

`point_one_body`の"25.2%"→"about 25%"、`point_two_body`の"44.7%"→"about 45%"のみを
直接置換する。Editorの再判断は経由しない。
- 影響範囲: TTS再生成が必要なのは`point_one.wav`・`point_two.wav`の2segmentのみ
  (article.md自体は上記2箇所だけの文字列置換、他のsegmentは無変更)。
- 長所: 他の文言(part1/part2等)への副作用が一切ない、コスト最小。
- 短所: 「Editorの判断」を経由しない機械的な書き換えであり、既存の「Evidence
  Compression Editorはjudgment rule」という設計思想からは外れる(Production標準
  経路としては例外的な扱いになる)。この手法を採るかはFable/ユーザー判断が必要。

### 5-2. 選択肢B: Evidence Compression Editorの再実行(強化ブロック入りProduction関数)

同一の`b1_pre_editor_text`(Writerの生成物、既存の`er011_output/
open112_trend_theme2_b_a2_b1_text_trial_12/research/`に保存済みの草稿と同一のはず、
要確認)を、強化ブロック入りの`run_lossless_editor()`へ再度通す。
- 実データで既に25.2%→about 25%・44.7%→about 45%への丸めを確認済み(上記3節)。
- ただし同じ実データで、Editorの非決定性により`part1`("seem to want more room" vs
  "seem to want trips with more room")・`part2`("plan to spend" vs "are planning
  to spend")のような無関係な言い回しの揺れも同時に発生することを確認した。
  - この場合、影響segmentは`point_one`・`point_two`だけでなく`full_story_part1`
    (`part1`+`part2`を含むsegment、要ファイル構成確認)にも及ぶ可能性があり、
    再TTS対象が増える。
  - Editorは非決定的なため、この特定の再実行結果(diffで確認したもの)がそのまま
    採用されるとは限らず、実際に採用する場合は再度Fact Checker・Ledger Deviation
    Checker・Directional Fact Precheckを記事全体に対して再実行する必要がある
    (既存Gate、独自の省略はしない)。

### 5-3. 影響範囲

- A2: 修正不要(既にabout 25%/about 45%で承認済みProduction出力)。
- B1: `point_one`・`point_two`(選択肢A)、または追加で`full_story_part1`相当の
  segment(選択肢Bで言い回しが変わった場合)。
- News/Editorial型: 本タスクでは未調査(Theme 2 B1[Trend Synthesis]のみを対象と
  した委任範囲のため、他ジャンルへの遡及調査は実施していない。ただしコード上は
  ジャンル分岐が無いモジュールのため、理論上は同じ状況が他ジャンルの既存完成音声にも
  起こりうる。これは推測であり、本タスクでは確認していない)。

### 5-4. 既存test・回帰実行

- 選択肢Aは新しいコード変更を伴わないため、`run_project_regression.py`への影響は
  想定されない(article.mdはコードではなくデータであり、regression対象外)。ただし
  TTS/ASR/Ledger Deviation等の既存Production Gateは、選択肢A/Bいずれの場合も
  当該2(〜4)segmentに対して通常どおり実行する必要がある(既存の安全装置を
  独自判断で回避しない)。
- 選択肢Bの場合、`er011_no18_evidence_compression_a_precision_21r_test_01.py`
  (Editor Promptのverbatim一致・順序を確認する既存テスト)は無関係(Prompt自体は
  変更しないため無風)。

### 5-5. 再生成要否・概算費用

- 選択肢Aの場合: TTS再生成は`point_one`・`point_two`の2segmentのみ + 既存ASR
  Validator/Ledger Deviation Checker等の再実行(該当2segmentの範囲、または記事全体
  への再Ledger Deviation Checkは既存運用に従う)。既存事例の類似コスト実績
  (OPEN-121 Production配線Runtime evidenceでの`full_story_part1`単体再生成実測
  ¥3.64、Evidence Compression Editor 1回の実測input_tokens=3276/output_tokens=1081
  ≒ 数円〜十数円)から類推すると、**概算で数円〜数十円程度**(TTS 2segment分 +
  Gate再実行分)。その後、既存音声パーツ(不変segment)とbyte-for-byte再利用しての
  再Assembly(2026-09-04配線のByte-for-byte reuse方式、CPUのみ、追加コストなし)。
- 選択肢Bの場合: 上記に加えEvidence Compression Editor呼び出し1回(数円)+
  影響segment増加時のTTS追加分 + Fact Checker・Ledger Deviation Checker・
  Directional Fact Precheckの記事全体再実行(いずれも既存の低コストLLM呼び出し、
  各数円〜十数円程度)。**概算で数十円〜百円未満程度**(いずれも推定、実測ではない)。
- どちらの場合も、完成音声全体(351〜358秒相当)の全segment再TTSは不要(既存の
  segment単位byte-for-byte reuse方式が機能する前提)。

## 6. USER_DECISION_REQUIRED候補の論点

1. **選択肢A(決定的な文字列置換)を許容するか、選択肢B(Editor再実行、非決定的な
   副次的言い回し変化を許容)を採るか**。前者はコスト最小・副作用ゼロだが
   「Editorの判断を経由しない」という点で既存のjudgment-rule設計から外れる例外。
   後者は設計思想に忠実だが、無関係な言い回し変化・追加segment再TTS・記事全体の
   Gate再実行というコスト増を伴う。
2. **OPEN-112-THEME2-AUDIO-REVIEW-FIX-02-PREVIEW-NUMERIC_REPORT.md(c)で既に提示
   されていた論点(CEFRレベル間で数字粒度が偶然割れる、SSOTに明文の意図なし)は、
   今回の強化ブロック配線(2026-09-07)で実質的に解消済みか、それとも別論点として
   残るか**。強化ブロックは「レベル非依存の既定」を明文化したが、Editor自体は
   引き続き非決定的なjudgment ruleであるため、将来別記事で同種の逆転(過去のように
   B1側だけ小数を残す)が起こらない保証はない。この選択肢1/2/3(現状維持/レベル別
   明文化/記事内一貫性ルール)は、当時提案されたままOPEN_ITEMS.mdへ未登録であり、
   登録するか・どの選択肢を採るかはユーザー判断が必要。
3. **既に承認済みの他の完成音声(Theme2 B1以外、過去に生成された全record)に、
   同様の「強化ブロック配線前の古いテキスト」が残っている可能性**があるかは本
   タスクの委任範囲外のため未調査。もし遡及的な一括点検が必要と判断される場合は
   別タスクとして切り出す必要がある(本タスクでは実施していない)。

## 7. 参照ファイル一覧

- `ER-011-PREVIEW-ROLE-AND-NUMERIC-PRECISION-PRINCIPLE-PRODUCTION-WIRING-01_REPORT.md`
- `OPEN-112-THEME2-AUDIO-REVIEW-FIX-02-PREVIEW-NUMERIC_REPORT.md`
- `ER-011-NO18-EVIDENCE-COMPRESSION-A-PRODUCTION-WIRING-AND-FINAL-CANDIDATE-AUDIO-21R_REPORT.md`(ファイル自体は未読、DECISION_LOG.md記載で内容確認)
- `CURRENT_SPEC.md`(110行目、207行目、352行目)
- `DECISION_LOG.md`(該当2026-09-04/2026-09-07エントリ)
- `er003_v1_n3_01_evidence_compression_editor.py`(`LISTENER_FRIENDLY_NUMERIC_PRECISION_BLOCK`57行目〜、`NUMERIC_PRECISION_LEVEL_INDEPENDENT_DEFAULT_BLOCK`121行目〜、218-219行目で連結)
- `er003_v1_n3_01_articles_generate.py`(`COMMON_BLOCK_TEMPLATE`「Spoken-first原則(数字の扱い)」243-252行目、`run_one_pattern()`)
- `er011_output/open112_trend_theme2_b_final_audio_rerun_03/b1b/article.md`・`parts.json`
- `er011_output/open112_trend_theme2_b_final_audio_rerun_02/b1b/article.md`(diff一致確認)
- `er011_output/open112_trend_theme2_b_full_audio_trial_13/b1b/article.md`(diff一致確認、生成元)
- `er011_output/open112_trend_theme2_b_a2_b1_text_trial_12/b1b_run01/audit/evidence_compression_editor_raw.json`(生成当時のEditor出力そのもの)
- `er011_output/open112_trend_theme2_b_a2_b1_text_trial_12/research/theme2_verified_fact_ledger_CORRECTED_trial12.txt`(F-202/F-203原文)
- `er011_output/preview_role_numeric_precision_wiring_01/numeric_precision_evidence.json`(強化ブロック入りEditorを同一草稿へ再実行した実データ)
- git commit: `ca3f4a6`(2026-09-04、土台配線)、`046c2ab`(2026-09-07 09:22、強化ブロック配線)、`7579d3f`(2026-09-06 20:49、rerun_02)、`f2a4f9f`(2026-09-07、rerun_03、FSP1差し替えのみ)
