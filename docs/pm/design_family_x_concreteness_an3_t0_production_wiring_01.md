# design_family_x_concreteness_an3_t0_production_wiring_01.md

管理ID: FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01(Phase A、委任 _01)
Status: Phase A(設計のみ)。本ファイル自体を含め、Production code・Prompt・
SSOT・Trial scriptは一切変更していない(新規ファイル作成のみ)。

## 0. ユーザー正式思想(逐語)

「細かい数字・時刻・過度な精度は極力使わず、記事理解に本当に必要な数字だけ
最小限残す。固有名詞も同様に、理解上必要なものだけ残す。」
**「数字を0にする」とは絶対に定義しない。** AN2よりAN3を選んだ理由は「0件
だから」ではなく「実本文で必要情報を残しながら不要な具体性をより強く落とせ
たため」。到達上限Status: Phase A完了時点で`APPROVED_FOR_PRODUCTION`(未配線)
のまま。`PRODUCTION_WIRED`はPhase B後のFable Gate 3判定のみ。

## 1. Existing Spec Check

### 1a. Family X Production JA初回Writer経路(実際の関数名・呼び出し順)

正式Production runner(実際に発火するentry point、Grep確認済み)は
`er019_family_x_entertainment_production_runner_01.py`である。
`er019_family_x_audio_production_runner_01.py`は既にja_writer出力ディレクトリ
を**読むだけ**(音声組み立て段階、`{source_dir}/ja_writer/runtime_evidence.json`
参照)であり、JA Writerそのものを呼び出さない(委任文の想定と異なる、訂正)。

呼び出し順(entertainment_production_runner_01.py):

| stage | 関数/モジュール | ファイル |
|---|---|---|
| storyline_b3 | `b3.run_storyline_b3_selection()` | `er019_family_x_storyline_b3_fact_selection_01.py` |
| writer | `jaw.run_ja_writer_o_r1_r2()`(→`run_ja_writer()`ラッパー) | `er019_family_x_ja_writer_o_r1_r2_01.py` |
| advanced | `efam.run_writer_stage(..., only="advanced")` → `adv_gen.generate_advanced_adaptation(ja_text, ...)` | `er012_e_family_entertainment_two_level_runner_01.py` → `er003_v1_n3_01_advanced_adaptation_generate.py` |
| standard | `efam.run_writer_stage(..., only="standard")` | 同上(standard生成) |

`run_ja_writer_o_r1_r2()`内のPrompt構築は次の**2箇所のみ**に集約されている
(全経路がこの2関数/パターンを通る、実コード確認済み):

1. **Original**: `build_original_prompt(storyline_line, selected_fact_brief_text, must_fix=None, full_ledger_text=None)`
   (L134-151)。通常初回呼び出し(L237)・Fact Check MAJOR時のmust-fix再生成
   (L263-265)・音声記号must-fix再生成(L306)の**3呼び出し全てが同一関数**を通る。
2. **R1/R2**: `REVISION_INSTRUCTIONS[stage_key] + SYMBOL_PREVENTION_BLOCK_JA`という
   同一パターンが**3箇所**で個別に組み立てられている(関数化されていない、
   既存コードの実態):
   - L333: 通常r1/r2ループ(`for stage_key in ("r1", "r2")`)
   - L376-379: R2 Fact Check MAJOR時のmust-fix再生成
     (`REVISION_INSTRUCTIONS["r2"] + "\n\n" + build_must_fix_block(...)`、
     SYMBOL_PREVENTION_BLOCK_JAはこの1箇所のみ**含まれていない**、後述4-3参照)
   - L436: R2音声記号must-fix再生成
     (`REVISION_INSTRUCTIONS["r2"] + SYMBOL_PREVENTION_BLOCK_JA + "\n\n" + ...`)

retry/fallback/regeneration経路の整理:

| 経路 | 通過する関数/パターン | AN3ブロック追加後に自動反映されるか |
|---|---|---|
| 通常Original | `build_original_prompt()` | される(1箇所に追記のみ) |
| Original Fact Check must-fix retry(1回) | `build_original_prompt()` | される(同一関数) |
| Original 音声記号must-fix retry(1回) | `build_original_prompt()` | される(同一関数) |
| 通常R1/R2(previous_response_id連鎖) | L333パターン | される(該当箇所へ追記すれば) |
| R2 Fact Check must-fix retry(1回) | L377パターン(SYMBOL_PREVENTION_BLOCK_JA無し) | される(該当箇所へ個別追記が必要、後述3-2) |
| R2 音声記号must-fix retry(1回) | L436パターン | される(該当箇所へ個別追記が必要) |
| previous_response_id失敗時のfallback_full_text | 上記いずれかのinstruction文字列をそのまま使用、`DEVELOPER_MESSAGE + "以下の記事:\n\n{prev_text}\n\n{instruction}"`で再送 | instructionにAN3/reminderを含めていれば伝わる。**ただしprev_text自体にはAN3文言は含まれない**(会話履歴ではなくテキストのみ引き継ぐ) |
| Runner `--regenerate-stage writer` | `run_ja_writer()`→`run_ja_writer_o_r1_r2()`を再実行 | される(同一関数を通る、既存artifact再利用ロジックの対象外) |
| Advanced化(English) | `adv_gen.generate_advanced_adaptation(ja_text, ...)`、入力はJA記事全文のみ | **対象外**(意図的に無変更、後述3-4) |
| Local Rewrite / segment再生成 | Family X JA Writer段階には該当する専用ロジックが存在しない(Grep`local_rewrite|Local Rewrite`は`entertainment_production_runner_01.py`に0件) | 該当なし |

通らない経路: 無し(JA Writer段階の全生成・全retry・全regenerateは
`build_original_prompt()`または3箇所のR1/R2パターンのいずれかを通る)。
ただし**3箇所への個別追記が必要**(関数化されていないため、1箇所修正では
不十分。次善策としてヘルパー関数化も可能だが、Phase Aでは既存コード
スタイル[SYMBOL_PREVENTION_BLOCK_JAと同型の3箇所append]を踏襲し、
最小diffを優先する案を推奨、詳細§3)。

### 1b. Prompt定数の共有有無

`er0*.py`全体をGrepした結果、`R0_PROMPT`/`REVISION_INSTRUCTIONS`/
`DEVELOPER_MESSAGE`を参照するのは以下10ファイルのみ:
`er019_family_x_ja_writer_o_r1_r2_01.py`(定義元)、その直接test群
(`_test_01.py`、`b3_production_wiring_01_test_01.py`、
`entertainment_production_runner_01_test_01.py`)、Trial群
(`er037_family_xy_concreteness_control_trial_01.py`とそのtest、
`er039_family_xy_concreteness_control_trial_02.py`、
`er036_family_y_voice_structure_trial_01.py`とそのtest)、および
系譜元のTrial(`er015_news_original_baseline_repro_01.py`、
`er015_news_iterative_entertainment_trial_01/02.py`、
`er015_family_x_writer_fact_selection_trial_01.py`、他2件)。

**結論: R0_PROMPT/REVISION_INSTRUCTIONSはFamily X専用であり、Family A/B/Y/Z
の他Production Writerとは一切共有されていない**(Family Yは
`er036_family_y_voice_structure_trial_01.py`でこれをTrialとして「流用」を
試みたのみで、Production Family Y Writerは別に存在する)。よってOriginal/
R1/R2側の変更はFamily X 1系統に閉じる。

一方、Advanced化(English)の`ADVANCED_VOCAB_RULE_V2_BLOCK`
(`er003_v1_n3_01_advanced_adaptation_generate.py`)は、Production呼び出し元を
Grepすると`er012_e_family_entertainment_two_level_runner_01.py`
(`efam.run_writer_stage()`、Family Xのentertainment 2-level runnerが使用)の
**1経路のみ**であった。OPEN-220は当該ファイルを`er003_v1_n3_01_articles_
generate.py`(Family A/X共有と記載)としているが、本タスクのGrepでは
`ADVANCED_VOCAB_RULE_V2_BLOCK`は`er003_v1_n3_01_advanced_adaptation_
generate.py`にのみ存在し、`articles_generate.py`には存在しなかった
(**軽微なファイル名参照の不一致の可能性、事実として報告のみ、本タスクでは
訂正しない**)。いずれにせよ本設計では**Advanced Promptを一切変更しない**
ため、この共有関係の真偽はAN3-T0配線の安全性に影響しない(§3-4)。

### 1c. CURRENT_SPEC.mdとの衝突判定(OPEN-20)

OPEN_ITEMS.md OPEN-20(逐語): 「固有名詞のtoken数・密度を意図的に下げる
一般ルール」は`REJECTED / NO_FURTHER_ACTION`。理由(逐語)「A01では固有
名詞が減った一方、ADD03ではTrumpを明示的主語にした結果増加し、『誰が
何をしたかを明確にする』『referentを明確にする』『spoken-firstにする』
という別の分かりやすさ要求と競合することが判明。**数量目標・密度目標は
設けず**、記事理解上の必要性で通常の編集判断により決める」。

**判定: 衝突しない**。根拠: (1) OPEN-20が却下したのは「token数・密度を
下げる**一般ルール**」であり、かつ「**数値目標**(密度%等)」である。
A3(「数字・時刻は基本的に使わないでください。記事の理解に本当に必要な
場合だけ、最小限に使ってください」)・N2(「人名・企業名・地名などの
固有名詞は、話の理解に必要な場合だけ使い、それ以外は一般的な言い方に
してください」)はいずれも**定性的な編集方針指示**であり、数値目標(N件
以下、密度X%以下等)を一切含まない。(2) OPEN-20はA2(CEFR)全記事構造への
「一般ルール」化を却下したものであり、Family X(Entertainment)のOriginal
Writer 1箇所への定性的指示追加という本タスクのスコープとは対象が異なる。
(3) 「誰が何をしたかを明確にする」等の競合要求は、A3/N2文言自体が
「記事の理解に本当に必要な場合だけ」「話の理解に必要な場合だけ」という
必要性による除外を明記しており、OPEN-20が指摘した対立を文言レベルで
回避する設計になっている。STOP不要と判定する。

CURRENT_SPEC.md「Spoken-first Number Treatment」(L1388)は`ER-003-A2-
B1-N3-01`、適用対象は「A2/B1双方(3ジャンルで運用確認)」であり、これは
Family A系(A2/B1レベル区分、`er003_v1_n3_01_articles_generate.py`系統)の
仕組みである。Family Xは別のPrompt定数・別のWriter経路(§1a)であり、
コード上の共有・競合は無い。CURRENT_SPEC.mdに「Family X Writer」専用の
数字・固有名詞に関する既存記述は見つからなかった(Grep`Family X.*数字|
Family X.*固有名詞`0件)。よって本タスクはCURRENT_SPEC.mdへの**新規追記**
であり、既存記述の**上書き・矛盾**ではない。

### 1d. DECISION_LOG.md/OPEN_ITEMS.md該当エントリ

OPEN-217/218(Family Y Voice文脈のR1→R2緊張、Non-blocking、Family Y側の
論点として据え置き)、OPEN-220(固有名詞抑制のJA→Advanced非伝播、本設計
§3-4で対応方針を明記)、OPEN-224(T1がHormuz/Meta各1件MAJOR、T1不採用の
根拠、本設計§6でCLOSE案)を確認済み(逐語は委任文記載の通り、DECISION_LOG.md
側は同一管理ID配下に対応するTrial-01/02のDecisionエントリが存在する
[Grep`FAMILY-XY-CONCRETENESS-CONTROL-TRIAL`]、詳細な転記は割愛しGrep
確認のみに留める、D-1規約)。

## 2. Trial資産の逐語抽出

### 2-1. A3/N2(er037_family_xy_concreteness_control_trial_01.py)

```
A3 = "数字・時刻は基本的に使わないでください。記事の理解に本当に必要な場合だけ、最小限に使ってください。"
N2 = "人名・企業名・地名などの固有名詞は、話の理解に必要な場合だけ使い、それ以外は一般的な言い方にしてください。"
COMBO_PATTERNS["AN"] = A3 + "\n" + N2   # = AN3の実体
```

**Trialでの注入位置**: Originalステージの**み**。
`run_ja_original_with_pattern()`(L226-235)で
`jaw.build_original_prompt(...)`の戻り値(=Production同一のOriginal prompt)
へ`"\n\n" + pattern_text(pattern_id)`を**追記**して1回call。R1/R2
(`run_ja_chain_for_pattern()`L246-255)は`jaw.REVISION_INSTRUCTIONS["r1"/"r2"]`
を**無改変のまま**previous_response_id連鎖で使用しており、AN3文言は
R1/R2では再送していない(Originalでの指示が会話履歴を通じて継承される
設計。Trial-02実測でHormuz/Meta両記事ともR2までArabic数字0を維持)。

### 2-2. T0/T1(er039_family_xy_concreteness_control_trial_02.py、混入禁止対象)

T0=「現行英語化Prompt」= Production `adv_gen.build_prompt()`をそのまま
1回call(追記なし)。T1(逐語、Trial限定・**Production混入禁止対象**):

```
T1_SUPPRESSION_SUFFIX = (
    "\n\n[Trial-only additional instruction -- not part of the production "
    "prompt]\n"
    "Do not add any number, time, or proper noun (a person's name, a "
    "company or product name, or a place name) that is not already in the "
    "Japanese article above. Where the Japanese article uses a general or "
    "vague expression instead of a specific number, time, or name, keep "
    "that expression general in the English version as well. Do not use "
    "this instruction as a reason to remove facts, numbers, times, or "
    "names that ARE already stated in the Japanese article."
)
```

T1は`adv_gen.build_prompt()`の出力(Production Advanced Prompt出力)に
Trial側でのみ連結する英語側抑制指示であり、**Production
`ADVANCED_VOCAB_RULE_V2_BLOCK`自体は無改変**。Hormuz AN3-T1・Meta
AN2-T1で各1件MAJOR Deviationを出しており(OPEN-224)、**本配線では
一切使用しない**(AN3-**T0**のみを配線する、ユーザー正式決定通り)。

## 3. 配線設計(最小diff案)

### 3-1. Original prompt: 新規定数`CONCRETENESS_CONTROL_AN3_BLOCK`

`er019_family_x_ja_writer_o_r1_r2_01.py`へ、既存`SYMBOL_PREVENTION_
BLOCK_JA`(L83-95)と同じ設計パターン(R0_PROMPT自体は不変、build時に
別途追記)で以下を追加する案:

```python
# FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01: Trial(er037/er039)の
# A3+N2(AN3)を逐語で移設。R0_PROMPT自体は無変更、build_original_prompt()で
# 別途追記する(SYMBOL_PREVENTION_BLOCK_JAと同型パターン)。
CONCRETENESS_CONTROL_AN3_BLOCK = (
    "\n\n数字・時刻は基本的に使わないでください。記事の理解に本当に必要な場合"
    "だけ、最小限に使ってください。\n"
    "人名・企業名・地名などの固有名詞は、話の理解に必要な場合だけ使い、それ"
    "以外は一般的な言い方にしてください。"
)
```

`build_original_prompt()`(L134-151)への追記(既存`prompt +=
SYMBOL_PREVENTION_BLOCK_JA`の直後、L148の次に1行追加、それ以外は無変更):

```python
prompt += SYMBOL_PREVENTION_BLOCK_JA
prompt += CONCRETENESS_CONTROL_AN3_BLOCK   # ← 追加(この1行のみ)
if must_fix:
    prompt += "\n\n" + build_must_fix_block(must_fix, full_ledger_text or "")
```

この1関数のみの変更で、通常Original・Fact Check must-fix retry・音声記号
must-fix retryの**3経路すべて**へ自動的に反映される(§1a表の通り、全て
同一関数を通るため)。

### 3-2. R1/R2 instruction: 新規定数`CONCRETENESS_CONTROL_AN3_REMINDER_JA`

ユーザー要件「R1/R2で数字・固有名詞を再前景化しない既存方針との整合」に
対応するため、R1/R2でも短いreminder文を追記する案(Trial-01ではR1/R2に
追記せず previous_response_id連鎖のみで0件を維持できたが、**fallback_
full_text経路[previous_response_id失敗時]ではprev_textのみが渡され、
AN3指示の文言自体は再送されない**ため、fallbackに対する頑健性を高める
目的で追加を推奨する):

```python
CONCRETENESS_CONTROL_AN3_REMINDER_JA = (
    "この修正で、すでに減らした細かい数字・時刻や固有名詞を、記事理解に"
    "必要でない限り再び増やさないでください。"
)
```

追記箇所(3箇所、SYMBOL_PREVENTION_BLOCK_JAと同型の個別append。既存コード
が関数化されていないため、L333/L377/L436の3箇所すべてに追記が必要):

- L333: `instruction = REVISION_INSTRUCTIONS[stage_key] + SYMBOL_PREVENTION_BLOCK_JA + CONCRETENESS_CONTROL_AN3_REMINDER_JA`
- L376-379: `r2_must_fix_instruction = (REVISION_INSTRUCTIONS["r2"] + CONCRETENESS_CONTROL_AN3_REMINDER_JA + "\n\n" + build_must_fix_block(...))`
  (**注**: この箇所は現状SYMBOL_PREVENTION_BLOCK_JAも含まれていない
  既存の非対称性がある。AN3 reminderを追加する場合、この既存の非対称性
  自体は本タスクのスコープ外として無変更のまま報告する[§9])
- L436: `r2_symbol_instruction = (REVISION_INSTRUCTIONS["r2"] + SYMBOL_PREVENTION_BLOCK_JA + CONCRETENESS_CONTROL_AN3_REMINDER_JA + "\n\n" + ...)`

**Advanced化Promptは無変更と明記**(§3-4)。

### 3-3. retry/fallback/regenerationの通過確認(まとめ)

§1a表の通り、Family X JA Writer段階の全生成経路(通常・Fact Check
must-fix・音声記号must-fix・previous_response_id失敗時fallback・
`--regenerate-stage writer`)は、上記2定数を追加する4箇所
(`build_original_prompt()`内1箇所+R1/R2パターン3箇所)を必ず通る。
通らない経路は無い。DEV/Trial script(`er037`/`er039`)自体は本配線の
対象外(Production module側`er019_family_x_ja_writer_o_r1_r2_01.py`の
変更のみで足り、Trial scriptは無変更のまま据え置く)。

### 3-4. Advanced化Prompt: 無変更

`adv_gen.generate_advanced_adaptation(ja_article_text, ...)`
(`er003_v1_n3_01_advanced_adaptation_generate.py` L424)の入力は
JA記事全文のみであり、`ADVANCED_VOCAB_RULE_V2_BLOCK`(L144)を含む
Advanced Prompt自体は本タスクで**一切変更しない**。OPEN-220が指摘する
「JA段階抑制がAdvanced English側で再前景化しうる」リスクは、AN3-T0配線
後も未解消のまま残る(Trial-02実測ではJA=EN=7[改良カウンタ]で新規固有
名詞追加は確認されなかったが、n=2記事のみであり一般化はしない)。
Advanced Prompt側拡張は本設計のスコープ外、OPEN-220として据え置く
(§6)。

### 3-5. runtime evidence案

既存の仕組み: `run_ja_writer()`(runner側L185-)が
`result["verbatim_shas"]`(=`jaw.verbatim_shas()`)を`runtime_evidence.json`
へ保存済み(R0_PROMPT/DEVELOPER_MESSAGE/r1・r2 instructionのsha256)。
最小追加案: `verbatim_shas()`(L102-108)の戻りdictへ2キーを追加する。

```python
def verbatim_shas() -> dict:
    return {
        "r0_prompt_sha256": sha256_text(R0_PROMPT),
        "developer_message_sha256": sha256_text(DEVELOPER_MESSAGE),
        "r1_instruction_sha256": sha256_text(REVISION_INSTRUCTIONS["r1"]),
        "r2_instruction_sha256": sha256_text(REVISION_INSTRUCTIONS["r2"]),
        "concreteness_an3_block_sha256": sha256_text(CONCRETENESS_CONTROL_AN3_BLOCK),      # 追加
        "concreteness_an3_reminder_sha256": sha256_text(CONCRETENESS_CONTROL_AN3_REMINDER_JA),  # 追加
    }
```

これにより既存の`runtime_evidence.json`保存経路(無改変)がそのまま
AN3ブロックのsha256もaudit証跡として記録する(新しい保存機構は作らない、
既存仕組みへの追記のみ)。

## 4. R1→R2整合の現状・Regression設計

### 4-1. R1→R2整合の現状

REVISION_INSTRUCTIONS(逐語、無変更予定)には数字・固有名詞への言及が
一切無い(「エンターテインメント性の高い記事に修正」のみ)。既存では
再前景化を明示的に禁じる文言が無い。§3-2の`CONCRETENESS_CONTROL_AN3_
REMINDER_JA`追記が、ユーザー要件「既存方針との整合」への対応案となる。

### 4-2. sha256不変assertテストへの影響(訂正: 破壊されない)

委任文は「Prompt定数sha256不変assertの既存テストが意図的に失敗する
ことへの対処方針」を求めていたが、**本タスクのGrep調査の結果、想定と
異なる良い結果が判明した**。実在するテストは以下2種類:

1. `er037_family_xy_concreteness_control_trial_01_test_01.py` L85-101:
   `jaw.R0_PROMPT`のsha256を**テスト実行前後で比較**する自己整合性
   チェック(Trial実行がProduction定数を書き換えていないことの確認)。
   固定の期待値ハッシュとの比較ではないため、R0_PROMPT自体の値が
   将来変わっても、その値が実行中に変化しない限りPASSし続ける。
2. `er019_family_x_b3_production_wiring_01_test_01.py` L200:
   `assertEqual(jaw.R0_PROMPT, repro01.R0_PROMPT)`(系譜元Trialとの
   逐語一致確認)。

**§3-1/3-2の設計(R0_PROMPT/REVISION_INSTRUCTIONS自体を無変更のまま、
別定数を追記する)を採用する限り、上記2テストは無改修のままPASSし続ける**
(SYMBOL_PREVENTION_BLOCK_JA追加時と同型のため、既に前例あり)。仮に
将来R0_PROMPT/REVISION_INSTRUCTIONS自体へAN3文言を直接組み込む設計へ
変更する場合のみ、テスト2の期待値更新(=系譜元Trialとの意図的な差分を
明示する正当な変更)が必要になる。**本設計では別定数方式を推奨するため、
テスト破壊は発生しない見込み**。

### 4-3. Regression計画(Phase B)

- 既存`vfl01.run_deviation_check()`(Ledger Deviation Check、
  `LEDGER_COMPLIANT`/`LEDGER_DEVIATION`)を**主判定**として使う(既存の
  JA Fact Check機構、Family X Productionに既配線済み、`full_ledger_text`
  渡し時に自動発火)。
- Hormuz・Metaの2記事について、Production正式path
  (`er019_family_x_entertainment_production_runner_01.py --stage writer
  --regenerate-stage writer`)でJA(Original→R1→R2)+Advanced(English)を
  再生成し、TTSは行わない(`--stop-after advanced`)。
- 判定基準: Essential Fact・因果関係のMAJOR Deviation 0件(2記事とも)。
  既存の1回must-fix retry→STOP機構(§1a)はそのまま使う(独自の追加retry
  や上限緩和は行わない)。
- 想定費用: Trial-02実測(AN3/AN2×T0/T1、JA+EN、rubric評価込み)が
  Hormuz¥8.768+Meta¥8.088=**合計約¥16.9/8セル**(1記事あたり4セル
  =AN3-T0/T1・AN2-T0/T1)。Phase B RegressionはT0のみ・1パターン
  (AN3-T0)・rubric評価なし(Deviation Check主判定のみ)のため、Trial-02
  の1/4セル相当以下と概算し、**2記事合計で概ね¥3〜6程度**を上限目安と
  する(実測ベースの精密見積りではなく概算、実行前にFable/ユーザーへ
  確認しGuardrail設定を推奨)。

## 5. 数字カウンタの誤認是正(設計のみ)

### 5-1. 事実確認

`er037_family_xy_concreteness_control_trial_01.py` L140:
`_DIGIT_RE = re.compile(r"\d+")` — **Arabic数字(0-9)のみ**を検出する
正規表現であり、漢数字(一二三四五六七八九十百千万億等)は一切マッチ
しない。`count_numeric_tokens()`(L165-169)はこの`_DIGIT_RE`の
findall結果件数を`numeric_token_count`として返す。

実データ確認(本タスクでGrep実施、
`er039_output/family_xy_concreteness_control_trial_02/hormuz/cells/
AN3-T0_ja.md`): 「七月」「十三日」「二割」「八十五ドル」「一バレル」
という漢数字表現が実際に本文中に存在することを確認した(委任文が
挙げた実例と一致)。すなわち`FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-02_
REPORT.md` L122「JA数字はAN3が両記事で0」という記述は、**Arabic数字
カウントのみで0**であり、実本文には漢数字による数量表現が複数残存
している。「AN3は記事から数字を完全に除去した」という意味ではない
(ユーザーの「数字を0にするとは絶対に定義しない」という方針と、実際の
出力結果は一致している。誤っていたのは**カウンタの表現・報告文言**
であり、AN3自体の生成品質ではない)。

### 5-2. REPORT/SSOT訂正文案

`FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-02_REPORT.md`および対応する
DECISION_LOG.mdエントリへ、以下の訂正注記を追記する案(Phase Bで反映):

> **訂正注記(2026-09-28、FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-
> WIRING-01で判明)**: 上記「JA数字はAN3が両記事で0」は、
> `count_numeric_tokens()`の`_DIGIT_RE = r"\d+"`がArabic数字のみを
> 検出する実装であったことによる。漢数字(七月十三日・二割・一バレル
> 八十五ドル等)は本カウンタでは計測されておらず、実本文には理解に
> 必要な数量表現が残存している。「AN3は数字0」という表現は不正確で
> あり、正しくは「Arabic数字表記は0、漢数字は本Trialでは未計測」と
> 訂正する。AN3採用の根拠は「0件だから」ではなく「実本文で必要情報を
> 残しながら不要な具体性をより強く落とせたため」であり、この結論
>自体は変わらない。

### 5-3. Production QAカウンタの推奨

Grep(`Number Treatment|spoken_first|count_numbers` in `er0*.py`)の
結果、Family X Production側に数値カウンタを用いたQA/Gateは存在しない
(既存の「Spoken-first Number Treatment」はFamily A系[A2/B1]の別仕組み、
§1c)。**推奨: 本配線ではArabic/漢数字を問わず、数値カウンタを成功条件
にしない**。§4-3の通り`run_deviation_check()`(Essential Fact・因果関係
のMAJOR Deviation 0件)を主判定とする。Arabic数字・漢数字・パーセント等
の日本語表記・日付・金額を統一的に扱う数値検出Validatorが将来的に必要
かどうかは、**本タスクでは設計せず、必要性のみを報告する**(該当する
場合はFable/ユーザーが新規スコープとして判断)。

## 6. SSOT文案(Phase Bで反映、Phase Aでは編集しない)

### CURRENT_SPEC.md追記案(新設「Family X Writer — Concreteness Control
(AN3-T0)」節)

> **Status**: 2026-09-28ユーザー正式決定によりAPPROVED_FOR_PRODUCTION。
> Family X JA Original Writer Prompt(`build_original_prompt()`)へ、
> 数字・時刻・固有名詞に関する定性的な抑制指示(AN3=A3+N2、Trial-01/02
> `FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-01/02`から逐語移設)を追加する。
> ユーザー正式思想(逐語): 「細かい数字・時刻・過度な精度は極力使わず、
> 記事理解に本当に必要な数字だけ最小限残す。固有名詞も同様に、理解上
> 必要なものだけ残す。」**「数字を0にする」とは定義しない**。英語化
> (Advanced)側の抑制追記(T1)はMAJOR Deviationを誘発したため不採用
> (T0=現行英語化Promptのまま無変更)。Production QAとして数値カウンタ
> を成功条件にしない(Arabic/漢数字とも計測せず、既存Ledger Deviation
> Checkを主判定とする)。OPEN-20(固有名詞密度の数値目標REJECTED)とは
> 対象が異なり非衝突(定性的指示 vs 数値目標)。

### DECISION_LOG.md文案

> **FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01**(2026-09-28、
> ユーザー正式決定): AN3-T0(JA側A3+N2定性抑制+現行英語化Promptのまま)
> をFamily X Production JA Writerへ`APPROVED_FOR_PRODUCTION`。AN2・T1
> (英語化Trial限定抑制追記)は不採用。`FAMILY-XY-CONCRETENESS-CONTROL-
> TRIAL-02_REPORT.md`の「JA数字はAN3が両記事で0」はArabic数字専用
> カウンタによる表現であり、漢数字は未計測だった旨を訂正して記録する。

### OPEN_ITEMS.md文案

- OPEN-224: T1不採用(Hormuz/Meta各1件MAJOR)により`CLOSED`(Production
  では使用しない、追加検証不要)案。
- OPEN-220: 現行Advanced Prompt(`ADVANCED_VOCAB_RULE_V2_BLOCK`)を維持
  する決定(§3-4)により`DEFERRED`(Advanced側拡張要否は引き続き
  ユーザー判断待ち、優先度低)案。
- OPEN-217/218: Family Y側の論点のため無変更のまま据え置き。

### docs/pm/REPORT_LEDGER.md行案

- `FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-02` → Status欄に
  「AN3-T0のみ`APPROVED_FOR_PRODUCTION`(2026-09-28)」を追記。
- 新規行: `FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01`(Phase A
  完了、Phase B[実装+Regression]待ち)。

## 7. リスク・Fable/ユーザー確認事項

1. **R1/R2の3箇所個別追記という設計上のfragility**: 既存コードが
   `REVISION_INSTRUCTIONS[stage_key] + SYMBOL_PREVENTION_BLOCK_JA`
   パターンを関数化せず3箇所に重複記述している(既存の設計、本タスクの
   問題ではない)。AN3 reminderも同型で3箇所へ個別追記する必要があり、
   将来第4のretry経路が追加された場合に追記漏れが起きるリスクがある。
   Phase Bで`build_r1_r2_instruction(stage_key, must_fix_block="")`の
   ようなヘルパー関数へリファクタリングするか(diffがやや大きくなる)、
   既存パターンを踏襲するか(diff最小だが重複4箇所)は、Fable/ユーザー
   判断を推奨する。
2. **L376-379の既存非対称性**(R2 Fact Check must-fixにSYMBOL_
   PREVENTION_BLOCK_JAが含まれていない)は本タスク発見の既存挙動であり、
   本タスクのスコープ外として無変更のまま報告する。AN3 reminder追加の
   際にこの既存非対称性へ倣うか(SYMBOL_PREVENTION_BLOCK_JA同様に
   reminderも入れない)、逆にこの機会に両方追加して是正するかは要判断。
3. **OPEN-220は未解消のまま残る**(JA側抑制がAdvanced英語化で再前景化
   しうるリスク自体は、本配線では対応しない、意図的な§3-4のスコープ
   限定)。
4. **共有Prompt影響**: §1bの通りOriginal/R1/R2はFamily X専用でありFamily
   A/B/Y/Z への影響はゼロ。Advanced Promptは無変更のため同じくゼロ。
   OPEN-220記載の「Family A/X共有」ファイル名参照とGrep実態の不一致
   (§1b)はSSOT側の軽微な修正候補として報告のみ(本タスクでは訂正しない)。
5. **費用**: Phase B Regression概算¥3〜6(§4-3)。実行前にFable/ユーザー
   へ確認しGuardrail設定を推奨(T-3=API支出上限¥0はPhase Aのみ、Phase B
   では別途承認が必要)。
6. **STOP候補**: 本Phase Aでは衝突・矛盾は検出されなかった(§1c)ため
   STOP対象なし。Phase B実装着手の可否自体はFable/ユーザー承認を要する。

## 8. Phase B 実施記録(委任_02、2026-09-28)

### 8-1. 実装

`er019_family_x_ja_writer_o_r1_r2_01.py`へ§3設計通り4箇所を実装した
(逐語一致、diff最小、既存パターン[SYMBOL_PREVENTION_BLOCK_JAと同型]を
踏襲、ヘルパー関数化なし)。`CONCRETENESS_CONTROL_AN3_BLOCK`は
`build_original_prompt()`のSYMBOL_PREVENTION_BLOCK_JA直後へ1行追加。
`CONCRETENESS_CONTROL_AN3_REMINDER_JA`はR1/R2の3箇所(通常r1/r2ループ・
R2 Fact Check must-fix・R2音声記号must-fix)全てへ追加した。§7-2の
L376-379既存非対称性(SYMBOL_PREVENTION_BLOCK_JA非含有)は変更せず、
REMINDERのみ追加(OPEN-227として新規記録)。`verbatim_shas()`へ2キー
追加。

### 8-2. テスト

新規`er019_family_x_concreteness_an3_t0_production_wiring_01_test_01.py`
(17件、全PASS)。既存regression: `er019*_test_*.py`(143件PASS、新規17件
含む)、`er037*_test_*.py`(12件PASS)、`er039*_test_*.py`(17件PASS)。
R0_PROMPT/REVISION_INSTRUCTIONS/ADVANCED_VOCAB_RULE_V2_BLOCKいずれも
系譜元・既存固定sha256と逐語一致を再確認、テスト破壊なし(§4-2の予測
通り)。

### 8-3. 確認用再生成(実API)

専用out-dir
`er019_output/family_x_entertainment_production_runner_01/an3_t0_wiring_regression_01/{hormuz,meta}/`
(既存run上書きなし)。research_ledger/storyline_b3は既存Production run
(`er019_output/family_x_b3_diversity_trial_01/hormuz/run_02`、
`er019_output/family_x_b3_production_wiring_01/run_01`)から複製した
上でrunnerのreuseロジックにより無課金で再利用し、writer/advanced段階の
みを正式path(`er019_family_x_entertainment_production_runner_01.py
--stage writer --stop-after writer`、続けて`--stage advanced
--stop-after advanced`)で実API実行した(TTS/ASR段階は本runnerに実装
自体が存在しないためコード上呼ばれない、§1a・本ファイルimport文で
確認済み)。

結果: Hormuz/Meta ともJA(Original→R1→R2)は既存Fact Check機構により
最終的に`LEDGER_COMPLIANT`(Hormuz original 1発PASS・r2は既存1回
must-fix retryでMAJOR解消、Meta original 1回must-fix retryでMAJOR
解消・r2は1発PASS)。Advanced(English)もMeta 1発`LEDGER_COMPLIANT`、
Hormuzは1回目PASS判定後に別の構造チェック(後述8-4)でクラッシュ、
2回目は既存Advanced deviation must-fix retryでMAJOR解消後
`LEDGER_COMPLIANT`。`runtime_evidence.json`に
`concreteness_an3_block_sha256`/`concreteness_an3_reminder_sha256`が
2記事とも記録され、`jaw.verbatim_shas()`の値と一致した。費用実測
合計¥14.031(Hormuz¥8.822+Meta¥5.209、上限¥15内)。

### 8-4. 新規発見(本タスクのスコープ外、修正せず報告のみ)

Hormuz Advanced生成で、`er003_v1_n3_01_advanced_adaptation_generate.py`
側の構造Gate(`h3_count==2`の`validate_point_structure()`、
`run_writer_with_technical_retry()`内でmax_attempts=2の自動retry付き)
はPASSしたが、その**後段**の`er012_e_family_entertainment_two_level_
runner_01.py: run_writer_stage()`が呼ぶ
`er003_v1_n3_01_scaffold_generate.py: split_article_text()`の
「Main Story(タイトル直後、最初の###見出し前の導入部)は段落数2以上」
というチェックに2回連続で失敗した(`RuntimeError`、自動retry機構なし、
未捕捉のままクラッシュ)。Meta側は1発でこのチェックもPASSしたため、
AN3固有の系統的問題と断定はできない(n=1の偶発的な生成ばらつきの
可能性が高い、JA記事自体はHormuz/Meta双方とも段落数・情報量は既存
baselineと近い)。この構造チェックはparts.json(TTS音声化準備専用の
成果物、`er019_family_x_audio_production_runner_01.py`のみが消費)の
生成失敗に留まり、article.md本文・Fact Check・Prompt sha256などの
本タスク証拠には影響しない。本タスクでは新規Validator/retry機構を
追加しないという禁止事項に従い、**修正は行わず新規OPEN候補として
報告のみ**とする(Fable/ユーザー判断)。

## 9. ユーザー決定によるR1/R2 reminder削除(委任_04、2026-09-28)

### 9-1. 経緯

§3-2で設計した`CONCRETENESS_CONTROL_AN3_REMINDER_JA`(R1/R2の3箇所への
reminder追記)は、「fallback_full_text経路での頑健性向上」という設計上の
配慮から追加した独自仕様であり、Trial-02(`er039`)のAN3-T0セル実測では
使われていなかった(Trial-02の実際の構成はOriginal側へのAN3追加のみ、
R1/R2は既存Revision指示のみ)。ユーザーはこれを「未Trial追加仕様の
Production混入」と判断し、Production正式経路から外すことを決定した
(2026-09-28)。

### 9-2. 変更内容

`CONCRETENESS_CONTROL_AN3_REMINDER_JA`定数と、§3-2で追記した3箇所
(通常r1/r2ループ・R2 Fact Check must-fix・R2音声記号must-fix)の
reminder追記を削除し、Phase B以前(commit `b814f241`)の逐語へ復元した。
`verbatim_shas()`から`concreteness_an3_reminder_sha256`キーを削除した。
§3-1の`CONCRETENESS_CONTROL_AN3_BLOCK`(Original側)は無変更のまま
維持する(ユーザー決定「AN3はOriginal側のみに戻す」に対応)。

### 9-3. Checklist項目「R1/R2で数字・固有名詞を再前景化しない既存方針との
整合」(§3-2の要件文)の再評価

§3-2時点ではreminder追加によりこの要件へ対応する設計としていたが、
この対応方法自体が未Trial仕様だったため撤回した。現在の充足基準は
「Trial-02と同一条件(R1/R2は既存Revision指示のみで追加reminderなし)」
であり、この基準での充足を委任_04のregressionテスト(`R1R2NoReminder
ThreeLocationsTests`)で機械的に確認した。詳細はREPORT §16参照。

### 9-4. §3-3(retry/fallback/regenerationの通過確認)への影響

§3-3で述べた「全生成経路は2定数を追加する4箇所を必ず通る」という設計は、
削除後は「Original側1定数(`CONCRETENESS_CONTROL_AN3_BLOCK`)を追加する
1箇所(`build_original_prompt()`)のみを必ず通る」に修正される。R1/R2は
reminderを含まないPhase B以前の経路へ戻ったため、fallback_full_text
経路を含め、R1/R2側でAN3関連の追加処理を経由する箇所は無くなった。

### 9-5. runtime evidenceの扱い

§8-3で記録したruntime evidence(Phase B時点、reminderあり構成)は削除
せずそのまま保持する。reminder削除後のR1/R2の挙動はTrial-02
(`er039`、AN3-T0セル)の実測と同一条件であるため、新たなAPI再生成は
行わない(詳細・費用¥0の理由はREPORT §16参照)。
