# KEYPHRASE-JA-GLOSS-NATURALNESS-DIAGNOSTIC-01

管理ID: KEYPHRASE-DISPLAY-TTS-SEPARATION-PROD-AND-JA-GLOSS-DIAGNOSTIC-01 / サブタスクC
種別: **DIAGNOSTIC(read-only)**。Production Prompt・Validator・blacklist・実装は一切変更していない。
HEAD(本タスク開始時点、`git show HEAD:<path>`で読んだ基準commit): `6f57a84d48b053db9b674d1310bdc8c7d0ad500b`
並行Lane A(サブタスクA+B)対象ファイル(`er003_key_words_canonicalization.py`、`er003_v1_n3_01_tts_generate.py`等)は作業ツリーの編集途中版を見ておらず、本Reportもそれらを一切編集していない。

## 最重要の前置き(前提の訂正)

タスク前提「A2 Key Phrase "new normal" のglossが『新常態』となった」を実データで検証した結果、**この前提は誤り**であることが判明した。

- `er011_output/open117_keyphrase_display_tts_separation_trial_02/a2/key_phrases/keywords_canonicalized.json`(rank2、"new normal")の`japanese_gloss`は一貫して**「新しい当たり前」**(選定工程での初回出力、canonicalizationはpass-throughのため無変更)。
- `a2/audit/kp_display_tts_map.json`のdisplay_gloss/tts_textも**「新しい当たり前」**。
- `a2/narration/meaning_2.wav`(この語の日本語音声)のASR結果も**「新しいあたりまえ」**(PHONETIC_MATCH、OK)で、`OPEN-117-KEYPHRASE-DISPLAY-TTS-SEPARATION-TRIAL-02_REPORT.md`の結果表(98-99行目)にもこの通り記録されている。
- 「新常態」という文字列は、`a2/audit/tts_generation_results.json`・`review_lock_state.json`内で**kp2の英語音声(ENGLISH Component、"new normal"を英語で発話させる試行)がSTOPPEDした際のASR書き起こしテキスト**としてのみ登場する。これは既存Report自身が明記する通り「OPEN-117の変更(gloss側)とは無関係な、既存の英語Key Phrase TTS言語ロック問題」(ASRが英語音声のはずの発話を日本語「新常態」として書き起こした、モデル側が英訳を試みて発話した現象)であり、タスク依頼文でも「別問題」と扱われていた事象そのものである。
- つまり、この特定事例において**日本語gloss生成Prompt・canonicalization・Validatorは正しく機能し、既に「新しい当たり前」という自然な訳語を採用していた**。「新常態」は一度もgloss/display/TTS用テキストとして確定していない。

この訂正を踏まえ、以下は依頼文の「問題クラス」自体(辞書的に正しいが硬い・直訳調・学習者に伝わりにくい訳語が生成されうる構造的リスク)への診断として回答する(個別事例の再発防止ではなく、構造診断)。

## 1. 現行Production Promptに「自然さ」指示は存在するか

存在するが、**きわめて薄い**。日本語gloss(`japanese_gloss`/`ja_gloss`)を生成する唯一の地点は選定Prompt`er003_v1_translator_briefs/b1_p2_keywords_l_prompt_template.txt`(B1・A2共通、`er003_b1_p2_keywords.py`/`er003_v1_iran01_a2_generate.py`が同一関数を再利用。`CURRENT_SPEC.md`220行目で確認済み)。

該当文言(HEAD版、原文引用):
> 「選ぶ表現は必ず本文中の実表現(source_span)に対応させ、短く自然な日本語グロスを付けてください。」
> 「日本語グロスには「～」「〜」「…」のようなプレースホルダー記号を一切使わないでください。動詞句などで目的語を省略した言い方にしたい場合は、日本語として自然な言い切りの形(例: 「～を示す」ではなく「示す、指し示す」)へ書き換えてください。日本語グロスに数字を含める場合は、算用数字(1、2、3…)ではなく漢数字(一、二、三…)で書いてください。」

「短く自然な」という一語と、placeholder禁止時の書き換え例で「自然な言い切りの形」という語が出るのみ。**「学習者向け・平易・直訳調を避ける・硬い漢語/報道語を避ける・聞いてすぐ理解できる」に相当する明示的な基準・具体例は一切ない**。canonicalization Prompt(`b1_p2_keywords_canonicalization_prompt_template.txt`)は`japanese_gloss`を一切扱わない(`key_phrase`という英語側の正規化のみが対象、`CURRENT_SPEC.md`220行目のアーキテクチャ上の発見と一致)。retry/fallback(Key Phrase Set Redundancy QA、`er011_key_phrase_set_redundancy_qa_01.py`)も再選定時に同じPromptを再利用するのみで、自然さ基準は変わらない。B2は別テンプレート(`b2_key_words_production_l_prompt_template.txt`)で今回の調査範囲外(未確認)。

2026-09-06付`CURRENT_SPEC.md`220行目に記録された直近の規約A/B追加(規約A=漢数字化、規約B=placeholder禁止と言い切り形への書き換え)は、いずれも**表記規則**であり、自然さ・平易さ・語彙の硬さは対象にしていない。規約Cの検討記録にもこの観点はない。

## 2. 「new normal」の実経路(訂正後の事実関係)

1. 選定Prompt(Trial-02時点のTrial用コピー、`audit/keywords_l_trial_prompt_template.txt`)で選定・gloss生成: model_id `gpt-5.6-luna`(`raw_usage_log_open117_trial02.jsonl`、stage `keyphrase_a2`、3 attempts、Redundancy QA retryによるもの)。→ `japanese_gloss: "新しい当たり前"`。
2. Trial-02のPromptはHEAD版と**1点だけ差分**があった: placeholder(「～」)の扱いがTrial限定で緩和されていた(表示用/TTS用分離検証のため)。差分はplaceholder規約のみで、自然さ関連の文言差はない(`diff`で確認済み)。
3. canonicalization工程(`er003_key_words_canonicalization.py`相当のTrialアダプタ)は`japanese_gloss`を変更せず"新しい当たり前"のままpass-through(`keywords_canonicalized.json`で確認)。
4. `kp_display_tts_map.json`でdisplay_gloss/tts_textとも"新しい当たり前"のまま確定。
5. 日本語音声(`meaning_2.wav`、model_id `gemini-3.1-flash-tts-preview`)は"新しい当たり前"を正しく読み上げ、ASR "新しいあたりまえ"でPHONETIC_MATCH・OK。
6. 英語Component(`kp2_en`、"new normal"を英語で読ませる別トラック、model_id `gemini-2.5-pro-preview-tts`)のみ、4回(Minimal2+English Lock2)ともASRが「新常態」と書き起こしTTS_FAILUREで全滅、`review_lock_state.json`上`HUMAN_REVIEW_REQUIRED`。これはgloss生成・canonicalizationとは無関係な英語TTSの言語ロック不具合。

## 3. Validator/QA/Human Reviewの守備範囲

- `er003_key_words_min_unit.py::validate_min_unit_selection()`(A2/B1共通の本番validator)の`ja_gloss`関連チェックは: (a) 日本語文字を含むか、(b) 括弧書き補足を含まないか(音声で不自然なため、ER-009-N1由来)、(c) 空でないか、の3点のみ。**意味の自然さ・平易さ・硬さ・直訳調は一切判定していない**(コード実装確認済み、`er003_key_words_min_unit.py` 306-443行)。
- Key Phrase Set Redundancy QA(`er011_key_phrase_set_redundancy_qa_01.py`)は5件相互の意味重複のみを判定、`japanese_gloss`は文脈情報として渡すだけで自然さは判定しない。
- canonicalization QAの12項目(`qa_standalone_natural_unit`等)はすべて**英語`key_phrase`側**の基準であり、日本語glossは対象外。
- Human Review/最終試聴(`CURRENT_SPEC.md`「QA / Human Review」節)は、ASR一致・発音品質・固有名詞発音の扱いを中心に規定されており、**訳語の自然さ・学習者にとっての分かりやすさを判定基準として明文化した箇所は見つからなかった**(全文検索で該当なし)。つまり現状、gloss自然さの最終防波堤は「選定モデル自身の『短く自然な』という緩い自己申告」と「たまたま人間が試聴時に違和感を覚えて指摘する」偶発的フィードバックのみであり、SSOT上の恒久ルールとしては存在しない。

## 4. 過去の類似事例(代表例)

- 既存corpusの`japanese_gloss`/`ja_gloss`値(重複除去397件、grep調査)を硬い漢語・報道語調の語彙(常態/是正/措置/促進/抑制/顕在化/転換/移行/継続性/徹底/施策等)で機械的に抽出したところ、明確な該当は僅少だった: 「AIが人間を超え、予測不能になる転換点」(“tipping point”系、`er003_output`配下)、「規則を徹底させる」の2件のみ検出(いずれも文脈上は許容範囲内、"新常態"ほど硬いとは言い切れない)。
- タスク依頼文で例示された「OPEN-103『default』『shift』」を確認したところ、**OPEN-103は日本語gloss自然さの事例ではない**。`DECISION_LOG.md`/`CURRENT_SPEC.md`216行目によれば、OPEN-103はGemini TTSが英単語"default"を安定して英語として発音できない(日本語カタカナ「デフォルト」・中国語「默认」・誤スペル等に化ける)という**英語発音の技術的不具合**であり、`DEFERRED / NON-BLOCKING`。gloss訳語の話ではない。「shift」というKey Phraseは全corpus内(`keywords_canonicalized.json`等)で検索したが1件も見つからなかった。
- 上記より、依頼文で示唆された過去事例の一部は誤認/記憶違いだった可能性が高い。今回grep調査した範囲では、「辞書的に正しいが不自然・硬い」という明確な実例は、今回の"new normal"を含め**production確定データの中では確認できなかった**(サンプルは網羅的LLM再判定ではなく語彙パターンgrepのみで、見落としの可能性は残る)。

## 5. 原因分類

**A(Prompt不足)を主因、E(複合、潜在的)を将来リスクとして併記する。**

- 今回具体的な悪化事例(「新常態」が実際にgloss/表示/TTSとして確定した例)は見つからなかったため、「Bのプロンプトはあるが効いていない」は**現時点のデータでは支持されない**。
- 一方、Prompt文言自体は「短く自然な」という1語のみで、学習者向け平易さ・直訳調回避の具体的基準を欠いており(A)、Validator/QAは形式チェックのみで自然さを一切見ておらず(C)、Human Reviewにも自然さの明文基準がない(D)。つまり**現状は「たまたま今回はモデルが自然な訳語を選んだ」という運任せの状態**であり、Prompt・Validator・Human Reviewのいずれの層にも自然さを担保する仕組みがない、という構造的な空白(A+C+Dの複合的な「未整備」)がリスクとして存在する。これは「効いていない」のではなく「そもそも判定軸が存在しない」という点で、実際に悪い出力が出た場合に検知・是正する手段がないことを意味する。

## 6. 同種再発リスク(粗い見積)

- 今回のgrep調査(397件の既存gloss)では明確な該当が0〜2件と少なく、モデル(選定Prompt使用時のLLM)は現状でも大半のケースで自然な訳語を選んでいる可能性が高い。
- ただし判定は選定モデル依存であり、決定的な安全装置(Validator/Human Review基準)が無いため、**モデル変更・記事テーマの変化・低頻度の硬い直訳が生成される確率は今後もゼロではない**。頻度は「稀だが構造的に検知不能」という評価が最も正確(発生率を数値化できる実測データは無い)。

## 提案(実装しない、提示のみ)

### 提案1: Promptの改善
現行Promptは「短く自然な日本語グロス」という一文のみで、直訳調・硬い報道語・学習者理解容易性への言及がない(効かなかったのではなく、そもそも書かれていない)。改善案の趣旨: 「辞書的に正しいだけでは不十分。日本人学習者が聞いてすぐ理解できる、自然で平易な現代日本語を使う。直訳調・硬い報道語・不自然な漢語は避ける」を、既存の規約A/B(数字・placeholder)と同じ形式で1〜2文追加する案。

### 提案2: 方式の選択肢と評価
- **Prompt onlyだけ**: コスト最小・実装リスク最小だが、Validatorが存在しないため実際に改善したか客観的に確認できない(今回のような「実は問題なかった」ケースと「実際に悪化した」ケースを区別する手段がない)。
- **Prompt + 軽量QA追加**(canonicalization QAまたは選定QAへ「学習者向け自然さ」項目を追加、LLM 1回判定): 検知力は上がるが、追加LLM呼び出しコスト(記事あたりKey Phrase5件×判定1回、既存Redundancy QA程度の規模感)とretry設計(既存`KEY_PHRASE_REDUNDANCY_RETRY_MAX`等の枠組みへ乗せるか新設するか)の検討が必要。既存の3回/4回retry上限設計との整合を要する。
- **Human Review基準強化**: 実装コストは最小(SSOT文書更新のみ)だが、属人的判断に依存し続け、量産時に見落とされるリスクが残る。
- **複合(Prompt改善+軽量QA+Human Review基準明文化)**: 最も頑健だが、Production Prompt変更・新Validator実装・SSOT更新の3点セットとなり、実装・検証コストが最大。

**Fable向け推奨**: 今回は具体的な悪化実例が確認できなかったため、緊急対応の必要はないと考えられる。ただし構造的な空白(自然さを判定する仕組みが皆無)は事実であるため、優先度は高くないが「Prompt改善(提案1)+ Human Review基準への一文追加」程度の軽量な複合案から始め、実データで悪化例が確認された場合にQA追加を検討する、という段階的アプローチが妥当と考える。

**ユーザー判断が必要な点**:
1. 依頼文の前提(「new normal→新常態」)が実データと異なっていたことの確認・受領。
2. Prompt文言の追加自体をAPPROVED_FOR_PRODUCTIONとするか(内容は上記提案1の趣旨)。
3. Validator/QA追加のコスト(追加LLM呼び出し)を許容するか、Prompt onlyで様子見するか。

## Closeout

**DIAGNOSTIC / VALIDATED**(タスク前提の事実誤認を含め診断完了。Production Prompt・Validator・実装は無変更)。

### SSOT登録案(新Open Item候補、文案)

> OPEN-XXX[Key Phrase日本語glossの自然さ担保が構造的に未整備]: 現行Production(選定Prompt`b1_p2_keywords_l_prompt_template.txt`)は日本語gloss生成に「短く自然な」という一文以外の自然さ基準を持たず、Validator(`validate_min_unit_selection`)・Redundancy QA・Human Review基準のいずれも訳語の平易さ・直訳調回避を判定しない(KEYPHRASE-JA-GLOSS-NATURALNESS-DIAGNOSTIC-01で確認)。同診断で検証対象とした「new normal→新常態」はタスク依頼文の前提誤り(実際のgloss確定値は一貫して「新しい当たり前」、「新常態」は無関係な英語TTS言語ロック不具合のASR書き起こしのみ)であり、現時点で悪化実例は確認されていない。ただし判定軸自体が存在しないため将来的な低頻度発生を検知できない構造は残る。Prompt文言追加案・軽量QA追加案は`USER_DECISION_REQUIRED`。

---

証跡パス(主要):
- `er011_output/open117_keyphrase_display_tts_separation_trial_02/a2/key_phrases/keywords_canonicalized.json`
- `er011_output/open117_keyphrase_display_tts_separation_trial_02/a2/audit/kp_display_tts_map.json`
- `er011_output/open117_keyphrase_display_tts_separation_trial_02/a2/audit/tts_generation_results.json`(kp2_english attempts 1-4、asr_text="新常態"、TTS_FAILURE)
- `er011_output/open117_keyphrase_display_tts_separation_trial_02/a2/audit/review_lock_state.json`
- `er011_output/open117_keyphrase_display_tts_separation_trial_02/raw_usage_log_open117_trial02.jsonl`
- `OPEN-117-KEYPHRASE-DISPLAY-TTS-SEPARATION-TRIAL-02_REPORT.md`(98-102行目、173-180行目)
- `CURRENT_SPEC.md` 220行目(日本語グロスPrompt規約A/B、`PRODUCTION_WIRED`)
- `er003_key_words_min_unit.py`(299-443行、validatorのja_gloss判定範囲)
- `er011_key_phrase_set_redundancy_qa_01.py`
- `DECISION_LOG.md`(OPEN-103関連エントリ、`default`発音不具合)
