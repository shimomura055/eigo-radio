# KEYPHRASE-JA-GLOSS-NO-PARENTHETICAL-PROD-WIRING-01

管理ID: KEYPHRASE-JA-GLOSS-NO-PARENTHETICAL-PROD-WIRING-01(+
OPEN-112-TREND-THEME2-B-FINAL-AUDIO-RERUN-02、別Report)

対象: Key Phrase日本語gloss(選定Prompt`b1_p2_keywords_l_prompt_
template.txt`、A2/B1共有)へ「括弧内に別訳・専門用語・補足を併記しない」
趣旨の短い1句を追加し、`PRODUCTION_WIRED`まで配線した。ユーザーが
2026-09-06に`APPROVED_FOR_PRODUCTION`と正式決定(意味を変えず、
blacklist化しない条件)。

## 0. 全Checklistサマリ

| チェック | 結果 |
|---|---|
| Production正式初回経路への反映 | 完了(下記1節) |
| retry/fallback/regeneration整合 | 完了(下記2節) |
| Validator整合 | 完了(下記2節) |
| Prompt文言テスト(新規1件+既存) | 完了・PASS 50/50(下記3節) |
| プロジェクト全体回帰 | 完了・既知の無関係failureのみ(下記4節) |
| Runtime evidence(Theme 2 A2/B1、Trial-12記事) | 完了・両レベルとも構造Validator通過・括弧0件(下記5節) |
| SSOT更新 | 完了(下記6節) |

**PRODUCTION_WIRED可否の自己判定: 可。**

## 1. 発生源・背景

`OPEN-112-TREND-THEME2-B-FINAL-AUDIO-RERUN-01`で、Theme 2(若者の旅行、
B条件)A2・B1が独立に同じ語("median")を選定候補とし、日本語glossへ
括弧書き補足(B1「データの真ん中の値（中央値）」、A2「真ん中の値
（中央値）」)を含めた。既存の構造Hard Requirement Validator
(`er003_key_words_min_unit.py::validate_min_unit_selection`、
`_JA_GLOSS_PARENTHETICAL_RE`、無変更・既存ルール)がこれを検出し
`KEY_WORDS_STRUCTURE_INVALID`と判定、選定ステージは`max_attempts=1`
(既存仕様、自動再選定なし)のためcanonicalization以降のいずれにも
到達せずSTOPした。同Reportは、直前配線
(`KEYPHRASE-JA-GLOSS-NATURALNESS-PROD-WIRING-01`)の「学習者が聞いて
すぐ分かる平易な現代日本語にする」指示が、専門用語に対してモデルへ
平易な説明+元の専門語を両方残そうとする傾向をn=2で誘発した可能性を
参考情報として報告した(調査・修正は当時未実施)。

## 2. 実装内容

### 2.1 選定Prompt(`er003_v1_translator_briefs/b1_p2_keywords_l_prompt_template.txt`、A2/B1共有)

事前調査で、A2/B1本番経路(`er003_v1_n3_01_scaffold_generate.py`
`run_key_phrase_selection()`→`er003_b1_p2_keywords.py::load_prompt_
template()`、Iran01/B1 Scaffold/A2 KP Select等の他の生成スクリプトも
すべて同一の`bk.load_prompt_template()`を使用)が実際に読み込む
Promptファイルはこの1ファイルのみであることをgrep監査で確認した
(`b2_key_words_production_l_prompt_template.txt`は`er003_key_words_
production.py::load_production_prompt_template()`経由でテスト専用
[`er003_test_p2i_production.py`]からのみ呼ばれ、現行A2/B1本番経路
からは呼ばれていない)。canonicalization Prompt
(`b1_p2_keywords_canonicalization_prompt_template.txt`)はja_gloss/
japanese_glossを一切生成せず素通しするのみ(Prompt本文に「Listening
Blocker Ranking自体はこの工程の対象外」と明記済み、コード読解でも
確認)であるため変更していない。

既存の自然さ基準パラグラフ(「日本語グロスは、辞書的に正しいだけで
なく…」)の直後へ、新パラグラフとして以下の2文を追加した(原文
一字一句):

> 「日本語グロスには、括弧（　）を使って別の訳し方・専門用語・補足
> 情報を書き添えないでください。音声だけで聞いてそのまま意味が伝わる、
> 平易な言い換えだけの一文にしてください。」

特定語の列挙はしていない(blacklist化していない)。既存の規約A(漢数字
化)・規約B(「…」等placeholder禁止、「～」「〜」は許容)・数値
placeholder型回避の1文・自然さ基準パラグラフはいずれも無変更のまま
維持した。

### 2.2 Validatorとの整合

既存の構造Validator(`_JA_GLOSS_PARENTHETICAL_RE`、全角/半角括弧検知、
`er003_key_words_min_unit.py`)は無変更のまま維持した。本Prompt追加は
このValidatorが拒否する前にモデル側で自発的に括弧併記を回避させる
目的の追加安全弁であり、Validator自体を緩和・置換するものではない
(Prompt文言による確率的な誘導であり、決定的な機械判定は引き続き
Validatorが担う)。

## 3. retry/fallback/regeneration整合の確認方法

`er003_v1_n3_01_scaffold_generate.py::run_key_phrases()`をコード確認
した。Key Phrase Set Redundancy QAがNGの場合、`run_key_phrase_
selection()`(内部で毎回`bk.load_prompt_template()`を呼ぶ)を最大
`KEY_PHRASE_REDUNDANCY_RETRY_MAX`(=2)回まで再実行する設計であり、
選定・retryとも同一の`PROMPT_TEMPLATE_PATH`定数(改訂済みの同じ
ファイル)を毎回読み込む。選定の構造不適合自体(`KEY_WORDS_STRUCTURE_
INVALID`)は`max_attempts=1`のためこの選定呼び出し自体はretryしない
(既存仕様、RERUN-01が実際に踏んだ経路)が、次回の記事生成では常に
改訂済みPromptが使われる。A2側(`er003_v1_iran01_a2_generate.py`ほか)
も同じ`er003_b1_p2_keywords.py`の関数を再利用するため、A2/B1両方に
改訂が及ぶ(既存アーキテクチャを踏襲)。今回のRuntime evidence(5節)
自体でも、B1で"median"が実際に再選定され、改訂済みPromptの効果で
括弧なしのgloss「真ん中の値」を返したことを実証した。

## 4. Prompt regression

- 新規単体テスト1件`test_template_contains_parenthetical_gloss_
  prohibition`(`er003_test_b1_p2.py`)を追加。追加文言の主要語句
  (「括弧」「書き添えないでください」)の存在、既存規約(「聞いてすぐ
  意味を理解できる」「漢数字」「使ってもかまいません」)の維持を同
  テスト内で確認。
- `er003_test_b1_p2.py`50件全PASS(既存49件+新規1件)。
- `run_project_regression.py`: 変更後collected=2110・passed=2107・
  failed=3・errors=0。`git stash`でPrompt/テスト変更を一時退避した
  baselineでもcollected=2109・passed=2106・failed=3で、失敗3件
  (`er003_test_bad.FixtureTests.test_case_0`[意図的なself-check
  fixture]・`er003_test_p2j_investigate`のOPEN-77既知meta-test集計
  3件)がbaseline/candidateで完全に同一であることを確認した(新規
  failureゼロ)。

## 5. Runtime evidence

`er011_kp_ja_gloss_no_parenthetical_prod_wiring_01.py`(root新規)に
より、Theme 2 B1・A2(いずれもTrial-12記事、`er011_output/open112_
trend_theme2_b_a2_b1_text_trial_12/{b1b,a2}_run01/article.md`。
RERUN-01が使用したTrial-13 article.mdとdiffで内容一致を確認済み)を
入力に、Production正式経路(`sc.run_key_phrases`、無変更のProduction
関数を直接呼び出し、選定→canonicalization→Key Phrase Set Redundancy
QA。TTS/ASR/Assemblyは対象外)をそれぞれ1回実行した。出力先:
`er011_output/kp_ja_gloss_no_parenthetical_prod_wiring_01/`。

| level | selection | canonicalization | redundancy_qa |
|---|---|---|---|
| b1b | `KEY_WORDS_STRUCTURE_PASS` | `CANONICALIZATION_REVIEW_REQUIRED`(継続許容ステータス、`run_key_phrases`の設計上STOPではない) | `REDUNDANCY_PASS` |
| a2 | `KEY_WORDS_STRUCTURE_PASS` | `CANONICALIZATION_REVIEW_REQUIRED` | `REDUNDANCY_PASS` |

両レベルとも、以前のRERUN-01のような`KEY_WORDS_STRUCTURE_INVALID`は
再発しなかった。

### (a) 構造Validator通過・括弧なしの確認

選定5件×2レベル=10件のja_glossすべてに全角/半角括弧が一切含まれな
かった(`any_parenthetical_in_selection=false`、両レベル)。
canonicalization後のjapanese_gloss/japanese_gloss_ttsも選定時の値と
完全に同一のまま(canonicalizationはja_glossを変更しないという既存
仕様どおり)。

### (b) 平易さの確認(直前配線[KEYPHRASE-JA-GLOSS-NATURALNESS-PROD-
WIRING-01]の出力との比較)

**B1**(今回、RERUN-01 STOP時の出力との比較を含む):

| rank | 英語Key Phrase | 今回のgloss | 備考 |
|---|---|---|---|
| 1 | self-directed travel | 自分で行き先や過ごし方を決める旅行 | 平易・括弧なし |
| 2 | control over time | 時間の使い方を自分で決めること | 平易・括弧なし |
| 3 | median | 真ん中の値 | RERUN-01時点「データの真ん中の値（中央値）」→今回は括弧補足なしの言い換えのみ |
| 4 | too broad a label | 広すぎるくくり | 平易・括弧なし |
| 5 | gap between | 二つのものの間にある差 | 平易・括弧なし |

**A2**(今回):

| rank | 英語Key Phrase | 今回のgloss | 備考 |
|---|---|---|---|
| 1 | at their own pace | 自分のペースで | 平易・括弧なし |
| 2 | the new normal | 新しい当たり前 | 直前配線と同一表現を維持 |
| 3 | less about adding nights | 泊数を増やすことが中心ではない | 平易・括弧なし |
| 4 | not the same picture | 同じ傾向ではない | 平易・括弧なし |
| 5 | policy task | 政策として取り組む課題 | 平易・括弧なし |

A2は今回"median"を選定しなかった(選定は非決定的なLLM選択のため、
同一記事でも実行ごとに候補が変わりうる。B1側で"median"型の再現を
確認できたため、比較目的としては十分と判断した)。いずれのglossも
音読して自然な現代日本語であり、直訳調・硬い報道語・専門語の残存は
確認されなかった(目視確認、直前配線水準を維持)。

### (c) "median"型専門語の訳され方

B1 rank3の"median"は、今回「真ん中の値」という平易な言い換えのみで
表現され、RERUN-01時点の「データの真ん中の値（中央値）」から専門語
併記部分(「（中央値）」)が消え、構造Validatorを通過した。これは
本タスクの追加文言(「括弧を使って別の訳し方・専門用語・補足情報を
書き添えない」)が意図どおりに機能した直接的な実例である。

### 実費

選定+canonicalization+Redundancy QA計6件のLLM呼び出し(`gpt-5.6-luna`)、
実測usage(input 13,928 tokens・output 25,131 tokens)×
`er005_output/cost_baseline_01/pricing_snapshot.json`公式単価
(input $0.20/1M、output $1.20/1M)で実費$0.0329(約¥5.3、$1=¥160換算)。
TTS/ASRは実行していない。

## 6. Production変更なし範囲の確認

`er003_key_words_min_unit.py`(Validator)・`er003_key_words_
canonicalization.py`(canonicalization)・`er003_v1_n3_01_scaffold_
generate.py`(選定/canonicalization/redundancy QA呼び出しフロー)は
いずれも無変更。変更はPromptテキストファイル1件
(`b1_p2_keywords_l_prompt_template.txt`)のみ。

## 7. SSOT更新箇所

- `CURRENT_SPEC.md`: 「Key Phrase」節へ新規行「Key Phrase日本語gloss
  の括弧内別訳・専門用語・補足の併記禁止(選定Prompt)」を追加
  (`PRODUCTION_WIRED`)。
- `DECISION_LOG.md`: 新規エントリ`## KEYPHRASE-JA-GLOSS-NO-
  PARENTHETICAL-PROD-WIRING-01`を追加(背景・実装・retry整合確認方法・
  テスト/回帰・Runtime evidence・Production変更なし範囲・根拠レポート)。
- `OPEN_ITEMS.md`: OPEN-112行の末尾へ本タスクの追記(RERUN-01が発見した
  事象への対策として`PRODUCTION_WIRED`まで配線したこと、後続の
  Theme 2完成音声追加1回再実行[RERUN-02]への言及)を追加。OPEN-112本体
  (Discovery/Engagement/News Ledger等の未決3論点)の状態は変更せず
  引き続き`USER_DECISION_REQUIRED`のまま。

## 8. approved specと実装の一致確認

- 追加文言はユーザー承認条件(「括弧内に別訳・専門用語・補足を併記しない
  趣旨の短い1句を追加する。意味を変えず、blacklistにしない」)どおり、
  2文(1つの新パラグラフ)にとどめ、特定語の列挙はしていない。
- 既存の自然さ基準・規約A/B・数値placeholder回避文はいずれも変更して
  いない(意味を変えていないことを4節のテストで機械的に再確認)。

## 9. 今回実施しなかったこと

Validator側の変更(既存`_JA_GLOSS_PARENTHETICAL_RE`はそのまま維持)、
canonicalization Promptへの変更(ja_glossを生成しないアーキテクチャの
ため不要)、B2レベルの選定Prompt(`b2_key_words_production_l_prompt_
template.txt`、テスト専用で本番経路から呼ばれないため対象外)への
変更、LLM追加QAの新設、既存corpusの一括gloss再生成、TTS実行(本
Reportの範囲では選定LLM呼び出しのみ、TTSは別Report
`OPEN-112-TREND-THEME2-B-FINAL-AUDIO-RERUN-02_REPORT.md`側)。

## 10. 証跡

- `er003_v1_translator_briefs/b1_p2_keywords_l_prompt_template.txt`
  (変更対象Promptファイル)
- `er003_test_b1_p2.py`(新規テスト1件)
- `er011_kp_ja_gloss_no_parenthetical_prod_wiring_01.py`(Runtime
  evidence取得script)
- `er011_output/kp_ja_gloss_no_parenthetical_prod_wiring_01/b1b/gloss_evidence_summary.json`
- `er011_output/kp_ja_gloss_no_parenthetical_prod_wiring_01/a2/gloss_evidence_summary.json`
- `er011_output/kp_ja_gloss_no_parenthetical_prod_wiring_01/b1b/key_phrases/keywords_canonicalized.json`
- `er011_output/kp_ja_gloss_no_parenthetical_prod_wiring_01/a2/key_phrases/keywords_canonicalized.json`
- `er011_output/kp_ja_gloss_no_parenthetical_prod_wiring_01/raw_usage_log.jsonl`
- `er011_output/kp_ja_gloss_no_parenthetical_prod_wiring_01/overall_summary.json`
- 発見元Report: `OPEN-112-TREND-THEME2-B-FINAL-AUDIO-RERUN-01_REPORT.md`

## 11. 懸念

- Prompt文言による誘導であり決定的Validatorではないため、遵守は確率的
  である(既存Validatorが最終的な安全弁として引き続き機能する)。今回の
  Runtime evidence(B1/A2各1回)では悪化事例が確認されなかったが、サンプル
  数は少ない。
- canonicalization_statusは両レベルとも`CANONICALIZATION_REVIEW_
  REQUIRED`だった(`run_key_phrases`の既存設計上、STOPではなく継続許容
  ステータス)。この状態自体は本タスクの変更に起因するものではなく既存
  仕様であり、内容(japanese_gloss等)には異常が無いことを5節で確認
  済みだが、後続工程(人間確認)での取り扱いは既存運用のまま変更していない。
