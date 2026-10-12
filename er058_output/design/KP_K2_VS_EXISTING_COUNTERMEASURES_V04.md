# KP_K2_VS_EXISTING_COUNTERMEASURES_V04: Key Phrase K2と現行対策の逐語比較・統合案・Trial D(委任_04D作成、委任_05Bで表現修正、2026-10-12。v01は`KP_K2_VS_EXISTING_COUNTERMEASURES_01.md`として残す)

**v04での修正(M5c、Opus総合レビュー)**: Trial Dの「V4でK2の効果が薄れた」という表現は撤回し、**「V3(簡潔)とV4(完全)の長さ・連結傾向の差は、n=1・差0.1〜0.2秒のため区別不能」**へ修正した(平均長: V1 1.29s / V2 1.39s / V3 1.49s / V4 1.28s。V2〜V4の差は各語1回の生成の揺らぎの範囲を超えると言えない。「raw bean->Robin」転写もV1/V4で出たが、ASR転写差であり聞こえ方は未確認)。**KP 2段目(English Lock)救済実績**(2026-09-01以降294 call中4件=1.4%)は`UNIFIED_FLOW_SPEC_V04.md` 9-1。

状態: 設計+Trial(Production未変更)。K2の正式変更はしていない。統合案はTrialのみ。採否はユーザー。
使用モデル(Trial D): TTS=`gemini-3.8-flash-lite-tts`(Production同一、Aoede、`speech_metadata.style`、Standard同期DEV。**本番ライン候補の性能確認=例外種別2。最新原則上の評価モデルではなく、Production比較のため同一条件**)。ASR=Primary OpenAI(Production同一の`routing.transcribe`、`gpt-4o-mini-transcribe`相当、逐語prompt付き)。ローカルwhisper small(Production同一のdisfluency QA実装)。評価LLMなし。
証跡: `er058_output/kp_english_lock_trial_01/`(`prompts_D.md`、`results_gen.jsonl`、`eval_D.json`、`cost_actual_D_tts.json`、`COST_ESTIMATE_D_01.md`、`raw/*.wav`)、試聴ページ`user_test/kp_english_lock_trial_01/index.html`。スクリプト: `er058_kp_english_lock_trial_01.py`、`er058_kp_english_lock_trial_page_01.py`。

---

## 1. Prompt全文(逐語)

### 1-1. 現行Production(Primary段、`KEY_PHRASE_MINIMAL_INSTRUCTION_PREFIX` = CORE + FUNCTION_WORD_REDUCTION、1076文字・185語)
```
Speak the following short phrase aloud naturally and clearly, in a warm podcast announcer voice, exactly once. Say only this phrase — do not add explanations, examples, introductions, or any other commentary, and do not add, omit, or change any words. Say it as one natural phrase, not as separate words read one at a time. Make sure the very last sound of the phrase is actually spoken, not trailed off into silence, and do not over-emphasize or exaggerate any single sound.

In natural spoken English, short function words such as articles ("a", "an", "the") are usually spoken briefly and without stress, connecting smoothly into the word that follows, while the main content word carries the natural stress of the phrase. If the phrase contains such a function word, keep it light and unstressed, and let it flow naturally into the following word, rather than pronouncing it as its own separate, stressed beat. Do not omit or drop the function word — only make it light and unstressed, not silent, and do not let this affect how clearly the rest of the phrase is spoken.
```
- Fallback段(English Lock) = 上記 + `Pronounce the phrase specifically as an English word or phrase, using English pronunciation throughout — not as a Japanese, Chinese, or other non-English reading of it.`

### 1-2. K2(`part_BCD/prompts/prompts_B.md`、332文字・57語)
```
Say the phrase as one single, smoothly connected chunk of meaning, as if the words belong together and are not read one by one. Keep the pitch movement small and continuous across the whole phrase. Say only this phrase, exactly once, without adding, omitting, or changing any words, and make sure the final sound is actually spoken.
```

---

## 2. 逐語比較(項目別。判定: ○=K2で同等以上、△=弱体化、×=欠落、+=K2で追加)
現行の各節とK2の対応。

| # | 現行の文言(逐語) | K2での対応(逐語) | 判定 | 説明 |
|---|---|---|---|---|
| 1 | "Speak the following short phrase aloud **naturally and clearly**" | なし("Say the phrase") | × | 「自然に・明瞭に」の明示が消える |
| 2 | "in a **warm podcast announcer voice**" | なし | × | 声質の方向づけが消える(Voiceは`Aoede`指定で別に固定されるが、トーン指示は無くなる) |
| 3 | "**exactly once**" | "exactly once" | ○ | 同等(反復防止の基本) |
| 4 | "Say only this phrase — do not add **explanations, examples, introductions, or any other commentary**" | "Say only this phrase"(列挙なし) | △ | 追加説明・前置き・例示の禁止が1語に圧縮。短い語句での「指示文の読み上げ/余計な発話」の防止力が下がる可能性(Trialでは0件、n=1) |
| 5 | "do not add, omit, or change any words" | "without adding, omitting, or changing any words" | ○ | 同等 |
| 6 | "Say it as one natural phrase, not as separate words read one at a time" | "as one single, smoothly connected chunk of meaning, as if the words belong together and are not read one by one" | ○(+) | **一体感はK2の方が具体的**で強い |
| 7 | "Make sure the very last sound of the phrase is actually spoken, **not trailed off into silence**" | "make sure the final sound is actually spoken" | △ | 語末子音の保持は残るが、「消え入りを避ける」の明示が消える(対策②の核) |
| 8 | "**do not over-emphasize or exaggerate any single sound**" | "Keep the pitch movement small and continuous across the whole phrase" | △ | 直接の禁止文は無いが「音程の動きを小さく連続」で**間接的に**過剰強調を抑える(別の手段)。単一音の過剰強調防止の明示は欠落 |
| 9 | FUNCTION_WORD_REDUCTION(冠詞・機能語を弱く短く、次の語へ連結、省略はしない) | なし | **×** | **対策②(冠詞弱形、Trial 26で採用、「a catch」問題)が完全欠落**。K2は一体感で間接的に近づくが明示的でない |
| 10 | (English Lock, Fallback段のみ)"Pronounce the phrase specifically as an English word or phrase … not as a Japanese, Chinese, or other non-English reading" | なし | × | English Lock欠落(ただし現行の初回段にも無い=Fallback専用) |
| 11 | (K2のみ)"Keep the pitch movement small and continuous across the whole phrase" | あり | + | 抑揚の暴れ・語尾上がりの抑制に効く可能性 |

### 対策①②③ごとの評価
- **①ASR対策**(逐語ASR指示`KEY_PHRASE_EN_ASR_NO_TRANSLATE_PROMPT`、非ラテン文字時のSecondary再確認`enable_non_latin_cascade`): **ASR側の機構でありTTS Promptと独立**。K2を採用してもコード上は影響なし(確定、`generate_key_phrase_component_verified`が`asr_prompt`/`enable_non_latin_cascade`を渡す構造)。Trial Dでも使用(Primary ASRに逐語prompt)。**維持される**。ただしK2側のTTSはEnglish Lock(項目10)が無いため、「TTSが日本語/中国語読みで発話してしまう」ケースの予防が弱くなる(実害は今回n=1で観測なし、過去の翻訳的書起こしはASR側の誤りとTTSの誤りが混在しており、`KEYPHRASE-EN-TTS-ROOTCAUSE-DIAGNOSTIC-01`では英語TTSは正しく発話していた=確認済み)。
- **②TTS Prompt対策**: 語末子音保持=△(7)、冠詞/機能語の弱形=**×(9)**、一体感=○(+)(6)、過剰強調・繰返し防止=△(3○、8△)。**K2単体は②を完全には満たさない**(特に9)。
- **③生成後QA**(部分反復・言い直し検知=`disfluency_qa=True`、local whisper): Prompt非依存で維持。Trial Dで実行(反復0/32)。

**結論(項目別)**: K2は「自然さ(一体感・小さく連続した抑揚)」を上げる狙いの短いPromptで、現行の**冠詞弱形・過剰強調禁止・語末の消え入り防止・追加発話禁止の列挙・English Lock・トーン指示**を持たない。「弱体化」(△)3件、「欠落」(×)4件。K2を単独で現行に置換するのは、対策②のうち冠詞弱形を失うため**不可(統合が必要)**。

---

## 3. 統合案(K2の自然さを壊さない設計)
方針: K2の2文(一体感+音程)を**先頭に置いて変更しない**。不足分(冠詞弱形・過剰強調・語末・English Lock)を短い文で後ろへ足す。逐語流用できる既存承認文は流用し新文言を最小化。

### 3-1. 簡潔版(V3、580文字・97語。現行の約54%)
```
Say the phrase as one single, smoothly connected chunk of meaning, as if the words belong together and are not read one by one. Keep the pitch movement small and continuous across the whole phrase, with no single sound over-emphasized. Keep small function words such as "a", "an", "the" light and unstressed, flowing into the next word but still audible. Pronounce it as English throughout, not as a Japanese or Chinese reading. Say only this phrase, exactly once, without adding, omitting, or changing any words, and make sure the final sound is actually spoken, not trailed off.
```
追加分: 過剰強調防止(K2第2文へ句として結合)、冠詞弱形(圧縮)、English Lock(圧縮)、"not trailed off"。省略: warm podcast announcer、explanations/examples列挙。

### 3-2. 完全版(V4、1103文字・186語。現行とほぼ同長)
K2全文 + 空行 + 現行`FUNCTION_WORD_REDUCTION_SUFFIX`(逐語) + 現行`KEY_PHRASE_ENGLISH_LANGUAGE_LOCK_SUFFIX`(逐語)。**新文言なし**(K2+既存承認文2つの連結)。省略: "over-emphasize"と"trailed off"の明示、explanations列挙。

### 3-3. 長さ比較
| 版 | 文字数 | 語数 | 備考 |
|---|---|---|---|
| V1 現行Minimal | 1076 | 185 | |
| V2 K2 | 332 | 57 | |
| V3 簡潔統合 | 580 | 97 | K2+4要素(圧縮) |
| V4 完全統合 | 1103 | 186 | K2+既存2文(逐語) |
参考: 現行English Lock段=1076+約200文字(約1280文字)。

### 3-4. 不足の補い状況(再判定)
| 項目 | V2 K2 | V3 簡潔 | V4 完全 |
|---|---|---|---|
| 1 naturally and clearly | × | × | × |
| 2 warm announcer | × | × | × |
| 4 explanations列挙 | △ | △ | △ |
| 7 not trailed off | △ | ○ | △(final soundのみ) |
| 8 過剰強調防止 | △ | ○ | △ |
| 9 冠詞弱形 | × | ○(圧縮) | ○(逐語) |
| 10 English Lock | × | ○(圧縮) | ○(逐語) |
未補完: 1・2(トーン方向づけ)。warm/clearlyを足す場合は「K2の自然さ」と競合するかを聴感で確認要(Trial 04Eの対象)。

---

## 4. Trial D結果(8語x4版、各1回、32 call)
語(選定理由): new normal・default(過去に日本語/中国語の翻訳的書起こし、ASR false rejection)、cashless(false rejection残存)、work-life balance(長め)、raw bean(Coffee最終試聴で異音)、push prices up(Coffee Standard KP)、a catch(冠詞aが強く長くなった語)、price tag(Coffee Advanced KP、語末子音)。

### 4-1. 自動評価(Primary ASR: Production同一`classify_asr_match`+length_ok、非ラテン、反復QA)
| 版 | Primary PASS | EXACT_MATCH | 非ラテン文字 | 隣接反復(local whisper) | 余分な語 | ASRが`?`付与 | 平均長 |
|---|---|---|---|---|---|---|---|
| V1 現行 | 8/8 | 1 | 0 | 0 | 0 | 1(a catch:「A catch?」) | 1.29s |
| V2 K2 | 8/8 | 2 | 0 | 0 | 0 | 0 | 1.39s |
| V3 簡潔統合 | 8/8 | 0 | 0 | 0 | 0 | 0 | 1.49s |
| V4 完全統合 | 8/8 | 1 | 0 | 0 | 0 | 0 | 1.28s |
- **全32件がPrimary PASS、翻訳的書起こし(非ラテン)0、反復0、余分な語0**。今回の8語(過去にASR誤りが出た語を含む)は、4版とも自動検証では差が出なかった(**自動評価の識別力は低い**、耳の評価が必須)。
- 「Robin」: local whisper(参考)が`raw bean`を**V1とV4で「Robin.」**、V2とV3で「Raw Bean」と転写(n=1、各語1回)。raw beanの「語の連結(raw+bean→Robin)」がV1/V4で起きている可能性を示唆するが、ASR転写差であり実際の聞こえ方は試聴で確認(Primary ASRは4版とも`raw bean`で合格)。
- 長さ: V2/V3はV1/V4より約8〜15%長い(単語がまとまってゆっくり=K2の効果と一致する傾向)。**V4(長いPrompt)とV1は長さが近い(1.28s対1.29s)**が、V2(1.39s)・V3(1.49s)との差は0.1〜0.2秒で、**各語1回のn=1では生成の揺らぎと区別できない**(v01は「K2の効果が薄まった可能性」としたが、v04で撤回)。
- 費用: TTS 35 call(3回は技術失敗retry)、usage実測 約JPY1.1。ASR(OpenAI Primary)は使用量が返らないため概算約JPY0.5。**合計約JPY1.6(事前概算JPY3.2、上限JPY10)**。`prompt_tokens`は35 callで100(1 callあたり約3=原稿のみ。styleがprompt_tokensに計上されていない=Prompt長は少なくとも**表示上のtoken費用に影響しない**。請求画面は未確認)。

### 4-2. Prompt肥大化の影響(評価軸)
| 軸 | 評価方法 | 結果 |
|---|---|---|
| 自然さ・リズム・語尾・強調・明瞭さ・一体感 | **試聴(ユーザー/Fable)**。ページに4版を並べた | 未判定(本書は自動評価のみ。聴感は人間確認が必要) |
| 一体感の機械指標 | 長さ・語の連結(local whisper) | V2/V3がまとまり傾向。V4はV1に近い |
| 明瞭さ | Primary ASR | 差なし(全PASS) |
| 語尾上がり | ASRの`?`付与 | V1のみ1件。ピッチ解析(librosa等)は環境未導入のため未実施 |
| 簡潔統合の可能性 | V3 vs V4 | V3は(語数が現行の約半分で)K2に近い長さ(1.49s)で、冠詞弱形・過剰強調防止・English Lockを含められる。V4(完全版)は現行と同じ長さ(1.28s)。**V3とV4の差は0.1〜0.2秒でn=1では区別不能**(v01の「V4でK2の効果が薄れた」は撤回)。どちらが良いかは**聴感確認と複数回の再現が必要** |

### 4-3. 限界(確定/推測の分離)
- 確定: 32件のPrimary ASR・反復・非ラテンの結果、長さ、費用実測(TTS)。
- 推測(v04: 撤回): 「長いPromptがK2の効果を薄める」は各語1回の観測で、統計的な優劣は言えない。**区別不能**と表現する。
- 未実施: 自然さの聴感評価、ピッチ解析、English Lock単独(現行Fallback段=Minimal+Lock)との直接比較(V4はK2+現行2文であり、現行Fallbackとは別物)、同一条件の複数回生成による再現性。
- Secondary(Azure)は呼んでいない(Trial D範囲外、費用)。

## 5. 推奨(提案のみ)
1. **K2単独のProduction採用は不可**(冠詞弱形など対策②の欠落、2章)。
2. 統合する場合は**簡潔版(V3)を第一候補にTrial続行**(聴感+同一条件の複数回)。完全版(V4)との優劣は**n=1・差0.1〜0.2秒のため区別不能**(v01の「K2の利点が薄れる可能性」は撤回)。
3. KP 3回単一Prompt(`UNIFIED_FLOW_SPEC_V03.md` 3章)のPは、当面**現行Minimal(P-a)またはV3の聴感確認後に決定**。
4. K2/V3を使う場合はMaster Storeのstyle version更新が必要(既存KP音声は再利用不可、再生成コスト)。
