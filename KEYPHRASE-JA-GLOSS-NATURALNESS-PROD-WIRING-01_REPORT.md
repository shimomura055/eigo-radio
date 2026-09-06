# KEYPHRASE-JA-GLOSS-NATURALNESS-PROD-WIRING-01

管理ID: KEYPHRASE-EN-TTS-ROOTCAUSE-AND-JA-GLOSS-NATURALNESS-PROD-01 /
問題2(日本語gloss自然さの軽量対策[選択肢a]のProduction配線)

対象: Key Phrase日本語gloss(`japanese_gloss`)の自然さ(学習者が聞いて
すぐ理解できる平易な現代日本語、直訳調・硬い漢語/報道語の回避)を、選定
Promptと`CURRENT_SPEC.md`のHuman Review基準へ`PRODUCTION_WIRED`まで配線
した。ユーザーが2026-09-06に選択肢a(Prompt1〜2文追加+Human Review基準
1文追加。LLM追加QA・Validator新設・blacklist・過去397件の再生成は
行わない)を`APPROVED_FOR_PRODUCTION`と正式決定。

## 0. 全Checklistサマリ

| チェック | 結果 |
|---|---|
| Production正式初回経路への反映 | 完了(下記1節) |
| Prompt regression(既存+新規) | 完了・PASS 49/49(下記3節) |
| Runtime evidence・品質比較(Theme 2 B1/A2各1回) | 完了・悪化事例なし(下記4節) |
| プロジェクト全体回帰 | 完了・既知の無関係failureのみ(下記5節) |
| SSOT更新 | 完了(下記6節) |
| approved specと実装の一致確認 | 完了(下記7節) |

**PRODUCTION_WIRED可否の自己判定: 可。**

## 1. 実装内容

### 1.1 選定Prompt(`er003_v1_translator_briefs/b1_p2_keywords_l_prompt_template.txt`、A2/B1共有)

既存の「選ぶ表現は必ず本文中の実表現(source_span)に対応させ、短く自然な
日本語グロスを付けてください。」の直後へ、新しいパラグラフとして以下の
2文を追加した(原文一字一句):

> 「日本語グロスは、辞書的に正しいだけでなく、日本人の英語学習者が聞いて
> すぐ意味を理解できる、自然で平易な現代日本語にしてください。直訳調や、
> 「常態」「是正」のような過度に硬い報道語・漢語、一般的な学習者には
> 伝わりにくい表現は避けてください。」

例示語は「常態」「是正」の2語のみ(blacklist化していない、独立した禁止
語リストは作っていない)。既存の規約A(漢数字化)・規約B(「…」等
placeholder禁止、「～」「〜」は許容[KEYPHRASE-DISPLAY-TTS-SEPARATION-
PROD-WIRING-01で許容済み])・数値placeholder型回避の1文はいずれも無変更。
canonicalization Prompt(`b1_p2_keywords_canonicalization_prompt_template.txt`)は
`japanese_gloss`を一切生成しない(診断済みのアーキテクチャ)ため変更して
いない。

### 1.2 Human Review基準(`CURRENT_SPEC.md`「QA / Human Review」節)

新規行「Key Phrase日本語glossの自然さ(Human Review基準)」を追加し、以下
の1項目を明文化した:

> 「日本語glossが、自然で平易かつ学習者が直感的に理解できる表現か。
> 意味が正しくても、不自然な直訳・過度に硬い表現・一般的でない訳語なら
> Review対象。」

機械的Validator・blacklistは新設していない(引き続き人間の主観判断)。

## 2. retry/fallback/regeneration整合の確認方法

`er003_v1_n3_01_scaffold_generate.py::run_key_phrases()`のretryループを
コード確認した: Key Phrase Set Redundancy QAがNGの場合、
`run_key_phrase_selection()`(内部で毎回`bk.load_prompt_template()`を呼ぶ)
を最大`KEY_PHRASE_REDUNDANCY_RETRY_MAX`(=2、`POINT_OVERLAP_ARTICLE_
RETRY_MAX`をそのまま踏襲)回まで再実行する設計であり、選定・retryとも
同一の`PROMPT_TEMPLATE_PATH`定数(改訂済みの同じファイル)を毎回読み込む。
A2側(`er003_v1_iran01_a2_generate.py`ほか)も同じ`er003_b1_p2_keywords.py`
の関数を再利用するため、A2/B1両方に改訂が及ぶ(診断・直前配線タスクで
確認済みのアーキテクチャを踏襲)。今回のRuntime evidence自体でも、A2の
1回目実行でRedundancy QAが実際にNGとなり、retry機構が発火して2回目の
選定で改訂済みPromptから再度合格したことを実際に観測した(4節参照)。
既存の安全装置(Redundancy QA retry上限・Human Review Lock・Audio
Validation Gate)はいずれも変更・回避していない。

## 3. Prompt regression

- 新規単体テスト1件`test_template_contains_gloss_naturalness_guidance`
  (`er003_test_b1_p2.py`)を追加。追加文言の主要語句(「聞いてすぐ意味を
  理解できる」「直訳調」「報道語」)の存在、既存規約A/B文言(「漢数字」
  「使ってもかまいません」)の維持を同テスト内で確認。
- `er003_test_b1_p2.py`49件全PASS(既存48件+新規1件)。
- 他のテストファイルはこのPromptファイルを直接参照していないことを
  grep確認済み(影響範囲はこの1ファイルのみ)。

## 4. Runtime evidence・品質比較

`er011_kp_ja_gloss_naturalness_prod_wiring_01.py`により、Theme 2 B1・A2
(いずれもTrial-12記事、`open112_trend_theme2_b_a2_b1_text_trial_12/
{b1b,a2}_run01/article.md`)を入力に、Production正式経路(`sc.run_key_
phrases`、無変更のProduction関数を直接呼び出し、選定→canonicalization
→Key Phrase Set Redundancy QA、TTSは実行せずLLM小額呼び出しのみ)を
それぞれ1回実行した。出力先: `er011_output/kp_ja_gloss_naturalness_
prod_wiring_01/`。

- B1: 初回で`KEY_WORDS_STRUCTURE_PASS`・`CANONICALIZATION_PASS`・
  `REDUNDANCY_PASS`。
- A2: 初回選定でRedundancy QAが実際にNG(「quiet split」と「new normal」
  の概念重複を検知)となり、既存retry機構が発火して選定からやり直し
  (retry 1/2)、2回目で`REDUNDANCY_PASS`に到達(既存retry機構の正常動作
  を実データで再確認)。

### 品質比較表(直前配線KEYPHRASE-DISPLAY-TTS-SEPARATION-PROD-WIRING-01の出力との比較)

**B1**(旧Prompt出力、`er011_output/kp_display_tts_separation_prod_
wiring_01/b1b/`):

| rank | 英語Key Phrase | 旧gloss |
|---|---|---|
| 1 | median | 中央値 |
| 2 | two different speeds | 二つの異なる進み方 |
| 3 | self-directed travel | 自分主導の旅行 |
| 4 | interest-led plans | 興味に沿った計画 |
| 5 | emerging preference | 形成されつつある志向 |

**B1**(新Prompt出力、本タスク):

| rank | 英語Key Phrase | 新gloss |
|---|---|---|
| 1 | two different speeds | 動き方が二つに分かれている |
| 2 | control over time | 時間を自分で決められること |
| 3 | too broad a label | ひとくくりにするには広すぎる呼び方 |
| 4 | self-directed travel | 自分で決める旅行 |
| 5 | not a completed shift | まだ完全な転換ではない |

**A2**(旧Prompt出力、`er011_output/open117_keyphrase_display_tts_
separation_trial_02/a2/`):

| rank | 英語Key Phrase | 旧gloss |
|---|---|---|
| 1 | median of 2 nights | 宿泊数の中央値は二泊 |
| 2 | new normal | 新しい当たり前 |
| 3 | at one's own pace | 自分のペースで |
| 4 | month off | 一か月の休み |
| 5 | not fully match | ～と完全には一致しない |

**A2**(新Prompt出力、本タスク):

| rank | 英語Key Phrase | 新gloss |
|---|---|---|
| 1 | quiet split | 目立たない分かれ |
| 2 | the new normal | 新しい当たり前 |
| 3 | hobby-focused travel | 趣味を中心にした旅行 |
| 4 | a full month off | 丸一か月の休み |
| 5 | median | 中央値 |

### 観察

選定は非決定的(LLMが毎回異なる候補を選ぶ)ため、旧・新Promptの厳密な
同一Key Phrase比較はごく一部に限られる。

- 共通選定された「self-directed travel」: 旧「自分主導の旅行」(「主導」
  というやや硬めの漢語)→新「自分で決める旅行」(平易な言い切り)。
  依頼文が懸念していた方向性(硬い漢語を避ける)に沿う変化を確認した。
- 「new normal」/「the new normal」: 旧・新とも「新しい当たり前」で一致。
  直前配線が既に自然だった訳語を今回のPrompt追加でも損なっていない。
- その他の新規gloss(「動き方が二つに分かれている」「ひとくくりにする
  には広すぎる呼び方」「目立たない分かれ」「趣味を中心にした旅行」等)
  は、いずれも音読して自然な現代日本語であり、硬い報道語・直訳調は
  含まれていない(目視確認)。
- 学習価値(意味の明確さ等)の劣化は確認されなかった。
- **遵守は確率的である**ことを明記する(Prompt文言による誘導であり
  決定的Validatorではない。今回のサンプル[B1/A2各1回、Redundancy QA
  retryを含む]で良好だったことは将来のあらゆる選定での再現を保証しない)。

## 5. プロジェクト全体回帰

`run_project_regression.py`: collected=2104、passed=2101、failed=3、
errors=0。残り3件(`er003_test_bad.FixtureTests.test_case_0`、
`er003_test_p2j_investigate.CollectionCountTests.test_combined_equals_
sum_of_er002_and_er003`、`er003_test_p2j_investigate.
ReconciliationArithmeticTests.test_p2h_reported_count_matches_er002_
plus_er003_at_that_time`、`test_p2i_reported_count_matches_er003_at_
p2i_era`)は、本タスクの変更ファイル(選定Prompt・`er003_test_b1_p2.py`)
を`git stash`で除去したbaselineでも同一の失敗が再現することを確認済み
(既知の無関係failure: `er003_test_bad`の意図的self-check fixture、
`er003_test_p2j_investigate`のOPEN-77既知meta-test集計バグ)。新規failure
は0件。

## 6. SSOT更新箇所

- `CURRENT_SPEC.md`: 「Key Phrase」節へ新規行「Key Phrase日本語glossの
  自然さ基準(選定Prompt)」、「QA / Human Review」節へ新規行「Key Phrase
  日本語glossの自然さ(Human Review基準)」を追加(いずれも
  `PRODUCTION_WIRED`)。ファイル冒頭「最終更新」チェーンにも要約を追加。
- `DECISION_LOG.md`: 新規エントリ`## KEYPHRASE-JA-GLOSS-NATURALNESS-
  PROD-WIRING-01`を追加(背景・前提訂正・実装内容・retry整合確認方法・
  品質比較・回帰・状態・今回実施しなかったこと)。ファイル冒頭「最終
  更新」チェーンにも要約を追加。
- `OPEN_ITEMS.md`: 新規`OPEN-118`を登録し即`RESOLVED / PRODUCTION_WIRED`
  (診断Report §末尾のSSOT登録案を土台に、実装完了後の状態へ更新)。
  OPEN-117行の末尾へ、OPEN-118への正式クロスリファレンスを追記(既存
  「別Open Item候補として結果待ち」という記述との整合)。LLM追加QA導入
  は「必要性が実データで確認された場合の別Trial」として`USER_DECISION_
  REQUIRED`のまま残した。ファイル冒頭「最終更新」チェーンにも要約を追加。

## 7. approved specと実装の一致確認

- 選定Prompt追加文言は、ユーザー承認文言(「辞書的に正しいだけでなく、
  日本人の英語学習者が聞いてすぐ意味を理解できる、自然で平易な現代
  日本語にする。直訳調、過度に硬い報道語・漢語、一般的な学習者に意味が
  伝わりにくい表現は避ける」)の趣旨を1〜2文で反映し、例示は最大1〜2語
  (「常態」「是正」)に留め、個別NGワード列挙・blacklist化を主対策にして
  いない(承認条件どおり)。
- Human Review基準追加文言は、ユーザー承認文言(「日本語glossが、自然で
  平易かつ学習者が直感的に理解できる表現か。意味が正しくても、不自然な
  直訳・過度に硬い表現・一般的でない訳語ならReview対象」)を一字一句
  そのまま`CURRENT_SPEC.md`へ追加した。
- LLM追加QA・自然さValidator新設・blacklist追加・過去397件のgloss一括
  再生成・個別語(「新常態」「new normal」)の個別手修正・TTS実行は、
  いずれも実施していない(禁止事項どおり)。

## 8. 今回実施しなかったこと

LLM追加QA(canonicalization QAまたは選定QAへの自然さ判定項目の追加)、
自然さ判定用の新規機械的Validator、個別NGワードのblacklist化、既存
corpus(397件)の一括gloss再生成、個別語(「新常態」等)の手修正、TTS実行、
B2レベルの選定Prompt(`b2_key_words_production_l_prompt_template.txt`)
への変更(指示範囲外)。LLM追加QA導入は、実データで悪化例が確認された
場合の別Trialとして`USER_DECISION_REQUIRED`のまま残す。

## 9. 証跡

- `er011_kp_ja_gloss_naturalness_prod_wiring_01.py`(Runtime evidence
  取得script)
- `er011_output/kp_ja_gloss_naturalness_prod_wiring_01/run_summary.json`
- `er011_output/kp_ja_gloss_naturalness_prod_wiring_01/b1b/key_phrases/keywords_canonicalized.json`
- `er011_output/kp_ja_gloss_naturalness_prod_wiring_01/a2/key_phrases/keywords_canonicalized.json`
- `er011_output/kp_ja_gloss_naturalness_prod_wiring_01/b1b/audit/run_key_phrases_result_summary.json`
- `er011_output/kp_ja_gloss_naturalness_prod_wiring_01/a2/audit/run_key_phrases_result_summary.json`
  (A2のRedundancy QA NG→retry 1/2発火の記録を含む)
- `er011_output/kp_ja_gloss_naturalness_prod_wiring_01/raw_usage_log.jsonl`
- 比較対象(直前配線の出力、既存artifact、無変更): `er011_output/
  kp_display_tts_separation_prod_wiring_01/b1b/key_phrases/
  keywords_canonicalized.json`、`er011_output/open117_keyphrase_
  display_tts_separation_trial_02/a2/key_phrases/keywords_
  canonicalized.json`
- `er003_test_b1_p2.py`(新規テスト1件)
- 診断根拠: `KEYPHRASE-JA-GLOSS-NATURALNESS-DIAGNOSTIC-01_REPORT.md`

## 10. 懸念

- Prompt文言による誘導であり決定的Validatorではないため、遵守は確率的
  である(3節・4節参照)。今回のB1/A2各1回(A2はRedundancy QA retryを
  1回含む)のサンプルでは悪化事例が確認されなかったが、サンプル数が
  少なく、将来の低頻度な逸脱を機械的に検知する手段は今回導入していない
  (診断が指摘した構造的空白そのものは、Prompt/Human Reviewの2層のみで
  埋めており、Validator層は引き続き空白のままである)。
- Human Review基準は人間の主観判断に依存し続けるため、量産時に見落とさ
  れるリスクは残る(診断・ユーザー承認の前提どおり)。
