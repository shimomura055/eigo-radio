# KEYPHRASE-EN-TTS-ROOTCAUSE-DIAGNOSTIC-01

**管理ID**: KEYPHRASE-EN-TTS-ROOTCAUSE-AND-JA-GLOSS-NATURALNESS-PROD-01 / 問題1
**Lane**: Lane A / Key Phrase(DIAGNOSTIC、Production変更・English lock変更・retry追加・Key Phrase選定回避の実装は一切なし)
**対象**: `er011_output/open117_keyphrase_display_tts_separation_trial_02/a2/` A2 Key Phrase 2位「new normal」英語Component(`kp2_en`)。Minimal instruction 2回+English Language Lock 2回(計4回)がすべてASR「新常態」でTTS_FAILURE。
**証跡コード基準**: 全コード引用は `HEAD` (`15a8b71ba333f3fb6e1138fa0d21a69a5fd04302`、2026-09-06 16:42:37 +0900)。作業ツリーの該当ファイルは全て `git status --porcelain` で無変更(HEADと同一)を確認済み。

---

## 1. TTSへ実際に渡したraw input(attempt別、原文)

Batch API (`gemini_batch`, `batches.create`) には各TTS呼び出しの完全なpromptテキストはローカルログに保存されない(`raw_usage_log_open117_trial02.jsonl`はtoken数のみ記録、prompt本文は非保存)。以下は**HEAD版コードから同一入力で再構成した値**であり、実ログの原文ではない(明記)。テキスト自体は静的定数+`text="new normal"`の単純連結のみで、乱数・LLM生成を含まないため再構成は決定的。

生成関数: `p4c.build_tts_prompt(text, style_prefix)` (`er003_b1_p4c_audio.py:78`)

```
The message below has two clearly separated sections.

=== STYLE INSTRUCTIONS (meta-guidance only — do not speak this section aloud,
it only describes how to perform the reading in the next section) ===
{style_prefix}
=== END STYLE INSTRUCTIONS ===

=== TEXT TO SPEAK (speak this section aloud exactly as written, and nothing
else — do not speak anything from the STYLE INSTRUCTIONS section above) ===
new normal
=== END TEXT TO SPEAK ===
```

**Attempt 1-2(Minimal instruction)**: `style_prefix = KEY_PHRASE_MINIMAL_INSTRUCTION_PREFIX`(`er003_v1_repro01_main_generate.py:480`、=`KEY_PHRASE_MINIMAL_INSTRUCTION_CORE_TEXT`[:438]+`FUNCTION_WORD_REDUCTION_SUFFIX`[:461])
```
Speak the following short phrase aloud naturally and clearly, in a warm podcast
announcer voice, exactly once. Say only this phrase — do not add explanations,
examples, introductions, or any other commentary, and do not add, omit, or change
any words. Say it as one natural phrase, not as separate words read one at a time.
Make sure the very last sound of the phrase is actually spoken, not trailed off
into silence, and do not over-emphasize or exaggerate any single sound.

In natural spoken English, short function words such as articles ("a", "an",
"the") are usually spoken briefly and without stress, connecting smoothly into
the word that follows, while the main content word carries the natural stress
of the phrase. If the phrase contains such a function word, keep it light and
unstressed, and let it flow naturally into the following word, rather than
pronouncing it as its own separate, stressed beat. Do not omit or drop the
function word — only make it light and unstressed, not silent, and do not let
this affect how clearly the rest of the phrase is spoken.
```

**Attempt 3-4(English Language Lock)**: `style_prefix = KEY_PHRASE_ENGLISH_LOCK_INSTRUCTION`(`:494`、=Minimal instruction全文+以下を追加[`:489`])
```
Pronounce the phrase specifically as an English word or phrase, using English
pronunciation throughout — not as a Japanese, Chinese, or other non-English
reading of it.
```

**確認できた事実**: 4回とも「TEXT TO SPEAK」節に含まれるのは英語 `new normal` のみ。日本語gloss「新しい当たり前」「新常態」という文字列はこのリクエストのどこにも存在しない(STYLE INSTRUCTIONS節にも英語のみ)。**Aによる取り違え(TTS input/field取り違え)は、このリクエスト組み立て段階では発生していない**。

---

## 2. TTS条件表

| 項目 | Attempt 1-2(Minimal) | Attempt 3-4(English Lock) |
|---|---|---|
| model | gemini-2.5-pro-preview-tts | 同左 |
| voice | Aoede | 同左 |
| 実行方式 | Gemini Batch API(`client.batches.create`、Standard同期ではない) | 同左 |
| language/locale指定 | プロンプト内に明示的なlanguage指定なし(自然言語instructionのみ) | 同左+「英語として発音せよ、日本語/中国語等の読みにするな」という明示指定 |
| safety_margin_seconds | 0.30秒(`KEY_PHRASE_TRIM_SAFETY_MARGIN_SECONDS`) | 同左 |
| disfluency_qa | True(既定) | 同左 |
| surrounding context | STYLE INSTRUCTIONSとTEXT TO SPEAKをStructured Separationで明示分離。TEXT TO SPEAKは`new normal`単独、他のcontext(記事本文・日本語gloss)は一切含まれない | 同左 |
| input_tokens(実測、raw_usage_log) | 316 | 350(English Lock追加文分だけ増加、想定と整合) |
| 生成音声duration | 1.251秒→1.391秒 | 1.411秒→1.451秒(最終) |
| duration anomaly判定 | 発生せず(閾値超過なし、STOPPEDにならず生成自体は成功) | 同左 |

Minimal/English Lock間の差分は「English Lockのみ追加された1文」だけで、`new normal`という読み上げ対象テキスト自体は4回とも完全に同一。

---

## 3. 実音声の所在とplayer URL、再ASR結果(EN/JA両方、raw)

**実音声の所在**: `generate_narration_snippet()`(`er003_b1_p9a_audio.py`)は毎attemptで同一`out_path`(`kp2_en.wav`)を上書きする設計のため、**ディスク上に現存するのはAttempt 4(English Lock、2回目、最終)の音声のみ**。Attempt 1-3の音声は上書きにより消失しており、復元不能(確認不能と明記)。Master Audio Storeにも登録されていない(`ensure_key_phrase_english_component`は`status=="OK"`の場合のみStoreへ登録する設計のため、4回ともASR不合格でStore未登録)。

コピー先: `er011_output/kp_en_tts_rootcause_diagnostic_01/kp2_en_attempt4_english_lock_2_final.wav`
Player: `file:///C:/Users/tensh/eigo-radio/er011_output/kp_en_tts_rootcause_diagnostic_01/player.html`

**再ASR(本Diagnosticで新規に実行、2026-09-06、同じwavファイル)**:

| ASR | Provider/Model | language指定 | Raw出力 |
|---|---|---|---|
| (a) 英語ASR(Production Primaryと同一関数) | OpenAI `gpt-4o-mini-transcribe` | `en` | **「新常態」**(元のProduction結果と完全再現) |
| (b) 日本語ASR | Azure Speech STT(連続認識) | `ja-JP` | **「New normal。」**(英語表記のまま認識。文末の「。」はAzure ja-JP認識が発話終端に自動付与するもの) |

客観的手がかり: 英語言語指定のASRが日本語漢字を返し、日本語言語指定のASRが英語のローマ字表記(しかも意図した`new normal`にほぼ一致する綴り)を返すという、直感に反する組み合わせが確認された。ただしAgentは音声を聴けないため、実際にどう聞こえるかの断定はしない(ユーザー試聴が必要)。

---

## 4. 元のASR raw output・Cascade段・ASR設定

元のProduction実行(`er011_output/.../a2/audit/review_lock_state.json`、`tts_generation_results.json`)より:

| Attempt | Instruction | ASR raw text | classification | verified |
|---|---|---|---|---|
| 1 | Minimal | 新常態 | TTS_FAILURE | False |
| 2 | Minimal | 新常態 | TTS_FAILURE | False |
| 3 | English Lock | 新常態 | TTS_FAILURE | False |
| 4 | English Lock | 新常態 | TTS_FAILURE | False |

**ASR routing**(`er006_asr_provider_routing_01.py`): English/Japaneseとも Primary = OpenAI `gpt-4o-mini-transcribe`(`language="en"`をAPIへ渡す)。`generate_narration_snippet_verified_strict`(`er003_v1_repro01_main_generate.py:210-263`)は`asr_language="en-US"`で`routing.transcribe()`を1回呼び、その結果(`asr_text`)をそのままログへ記録・分類に使う。

**Cascade段**(`er006_secondary_asr_01.py::evaluate_attempt_with_cascade_detail`): Cascade(Primary#2→Secondary Azure等)が追加実行されるのは、一次分類が`ASR_VALIDATION_UNCERTAIN`かつ「entity-like/homophone-candidateの不一致」に限定される場合のみ。今回の一次分類は`TTS_FAILURE`(token類似度<0.4の著しい不一致)であり、この条件に該当しないため、**Cascadeは4回とも一切起動していない**(`steps`は`primary_1`のみ)。つまり「新常態」はOpenAI Primary ASR単体の一発の出力であり、Azure Secondaryを経由した結果ではない。

`classify_asr_match()`(`er006_preprod_hardening_01_validation.py:707-781`)の`TTS_FAILURE`は「全体類似度が著しく低く、TTS生成自体の異常(hallucination/missing speech)が疑われる」場合に付与される分類であり、Validator実装自体にバグがあってこの分類になったわけではない(canonical="new normal"のtokenとASR="新常態"のtokenは言語が異なり類似度がほぼ0になるのは計算として正しい)。

---

## 5. field lineage表

| 段階 | 値 | ファイル・キー |
|---|---|---|
| Key Phrase選定 source_span | `new normal` | `a2/key_phrases/keywords_canonicalized.json` items[rank=2].source_span |
| key_phrase/used_form(英語) | `new normal`(無変更) | 同上 .key_phrase / .used_form |
| japanese_gloss(日本語表示・meaning用) | `新しい当たり前` | 同上 .japanese_gloss |
| TTS用テキスト正規化(英語) | `tts_safe_kp_en("new normal")` → `new normal`(無変更、ハイフンなし・複合語override非該当) | `er003_v1_n3_01_tts_generate.py:584-588` |
| 英語Component呼び出し | `shared_narration.ensure_key_phrase_english_component(tts_gen.tts_safe_kp_en(used_form), ".../kp2_en.wav")` | `er011_open117_keyphrase_display_tts_separation_trial_02.py:410-411` |
| TTS request(TEXT TO SPEAK節) | `new normal`(英語のみ) | 本Report §1(再構成) |
| 生成音声 | `kp2_en.wav`(Attempt4のみ現存) | `a2/narration/kp2_en.wav` |
| ASR出力(English routing) | `新常態`(4回とも同一) | `a2/audit/review_lock_state.json`["kp2_en"].last_attempts_log / `tts_generation_results.json`["key_phrases"]["2"]["english"] |
| Validator分類 | `TTS_FAILURE`(verified=False) | 同上 |
| 日本語gloss側(完全に別経路) | `新しい当たり前` → `tts_gen.generate_a2_japanese_with_reading_safety` → `meaning_2.wav` → ASR「新しいあたりまえ」→ `PHONETIC_MATCH`(OK) | `tts_generation_results.json`["key_phrases"]["2"]["japanese_meaning"] |

`新常態`という文字列は、選定・canonicalization・TTS request・field定義のどこにも一度も存在しない。ASR出力として初めて現れる。「新しい当たり前」(日本語gloss)とも文字列として一致しない(意味は近いが表記は別物)。

---

## 6. 分類と根拠

**F(証跡不足で断定せず。ただしC[実音声はTTSが正しく発話しているがASRが意味変換して日本語相当語を出力]が最有力候補、B[TTS自身が意味変換して発話]も完全には排除できない)**。

根拠:
- A(TTS input/field取り違え)は§1で明確に否定できる(4回ともTEXT TO SPEAK節は英語`new normal`のみ、日本語glossは一切混入していない)。
- D(prompt/context/language指定が日本語発話を誘発)も、English Lock instruction追加後も同一結果(「新常態」)が変わらなかったことから、可能性は低いと評価する(排除はしない)。
- C側を支持する客観的手がかり: 本Diagnosticの再ASRで、Azure(ja-JP指定)が同じ音声を「New normal。」という**英語の綴りのまま**認識した(Azureのja-JP認識器が外来語をカタカナ化せずローマ字のまま返すのは通常の挙動ではなく、音そのものが英語`new normal`に近いことを示唆する一つの手がかり)。一方でOpenAI(en指定)は独立した再実行でも同じ「新常態」を再現しており、単発の乱数的誤りではなく高い再現性がある。
- B側を完全に排除できない理由: TTS自体が発話した内容をAgentは直接確認できず、Azureの認識結果も絶対的な正解ではない(Azure自身が誤認識している可能性もゼロではない)。
- 最終的な発話内容の断定にはユーザーによる実試聴が必要(タスク指示どおり、Fに留める)。

---

## 7. OPEN-103との同型性の評価

OPEN-103(No.9 A2 Key Phrase 2「default」)は事前に「前提としない」よう指示されていたため、実際の記録を確認したうえで評価する。

- OPEN-103では複数Trialにわたり、ASRが**「デフォルト」(日本語カタカナ、音訳)**・**「默认」(中国語、意味変換)**・**「defaut」(英語だが誤スペル)**と、試行ごとに異なる失敗モードを示した(`OPEN_ITEMS.md` OPEN-103行、Trial 19/20-R2/21参照)。
- 本件「new normal」は、4回全て**「新常態」という同一の漢字表記**(音訳ではなく、英語には存在しない意味のまとまった訳語)を一貫して返しており、単発の音訳ゆれではない。
- 共通点: どちらも「孤立した短い英語Key Phraseに対し、Production ASR(OpenAI gpt-4o-mini-transcribe、language=en指定)が非英語(日本語/中国語)の文字列を返す」という広いカテゴリに属する。OPEN-103でも「默认」という意味変換の実例が既に記録されており、本件の「新常態」はこの意味変換パターンと類似する。
- 相違点: OPEN-103の主要因はduration anomaly(想定の2〜2.5倍の異常な発話長)だったが、本件は4回とも通常の長さ(1.2〜1.5秒)でduration anomalyは一度も発生していない。したがって「短い孤立語→instruction:text比率の不均衡→hallucination」というOPEN-103のTTS_INSTRUCTION_LEAK_LIKELY仮説がそのまま当てはまるかは不明(text:instruction比率は本件でも同様に大きいが、症状[異常長]は再現していない)。
- 結論: **同型と断定しない**。カテゴリ(短い英語Key PhraseでASRが非英語文字列を返す)は共通するが、具体的な失敗パターン(一貫した意味変換 vs 音声長異常+複数モードの音訳/意味変換混在)は異なる。

---

## 8. 未確定事項

1. 実際にTTSが発話した内容(「ニューノーマル」系の音か、それ以外か)はユーザー試聴でのみ確定できる。
2. OpenAI `gpt-4o-mini-transcribe`が`language="en"`指定にもかかわらず日本語(または中国語由来)の意味変換的な文字列を返す挙動の内部メカニズムは、Provider側のブラックボックスであり本Diagnosticでは特定できない。
3. Attempt 1〜3の音声は上書きにより消失しており、4回とも同一の発話だったか(4回とも同じ音の可能性)は確認できない(Attempt4のみ確認対象)。
4. 「新常態」がなぜ選ばれたか(他の訳語ではなく)は不明。

---

## 9. 対策が必要な場合の候補(実装しない、ユーザー判断事項)

- ユーザーが実試聴のうえ、実音声が「ニューノーマル」系の英語発話であると判断した場合: OPEN-103の`default`と同様、machine validatorはFAILのまま、ユーザー承認によるone-off fixed asset採用という前例があり、同種の対応が選択肢になりうる。
- 実音声が本当に非英語的発話だった場合: OPEN-103同様、恒久課題(Provider variance)として`DEFERRED`管理する前例がある。
- いずれもユーザー判断事項であり、本Diagnosticでは実装・推奨の優先順位付けを行わない。

---

## 10. cost(再ASR分)

- 英語ASR再実行(OpenAI `gpt-4o-mini-transcribe`、1.45秒音声): 数十秒あたり1円未満の単価、実質無視できる金額(1回)。
- 日本語ASR再実行(Azure Speech STT、1.45秒音声): Azure S0単価(約$1/時間)換算で1円未満(1回)。
- 合計: 1円未満(既存のraw_usage_logへは本Diagnosticの呼び出し方では記録していない別セッション実行のため、正確な円換算値は本Reportのみに記録)。追加のTTS呼び出しは一切行っていない。

---

## 11. Production変更なし確認

- Production関数(`generate_key_phrase_component_verified`/`ensure_key_phrase_english_component`/`generate_narration_snippet_verified_strict`/`classify_asr_match`/ASR routing等)はいずれも無変更(読み取りのみ)。
- 書き込みは本Report(root)と`er011_output/kp_en_tts_rootcause_diagnostic_01/`(既存`kp2_en.wav`のコピー1件+`player.html`)のみ。
- Key Phrase選定・English lock・retry上限等のロジック・定数は一切変更していない。
- `docs/pm/ACTIVE_TASK.md`・`RESULT_PACKET.md`・Key Phrase関連module・Prompt・SSOTには触れていない。
