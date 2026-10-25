# EVIDENCE_01 (FZ-DIALOGUE-TTS-CONTEXT-EMOTION-INVESTIGATION-01 委任_01、read-only・API 0・Production変更0・新規TTS 0)

凡例: [確認済み: path] = 実ファイル/実行記録/コードを読んで確認。[推測] = 確認できていない推論。
runtime evidence 取得方法: `tts_generation_results.json`・`attempts/*.json`・`segment_plan_*.json`・保存済みwavを読むのみ。prompt再構成は Production関数(`er003_b1_p4c_audio.build_tts_prompt` / `er003_b1_p9a_audio.ENGLISH_STYLE_PREFIX` / `er003_v1_n3_01_tts_generate.tts_safe_news_en`)を`.venv`でimportして文字列を組むだけ(ネットワーク・API呼出なし)。

## 0. 最重要の前提(TTSへ送った入力全文は保存されていない)

- [確認済み: `er026_output/family_z_production_e2e_01/the_open_window/run_sf_prod_01/b1b/narration/attempts/*.json`] attemptsには `attempt_number/route/segment_id/model/voice/asr_text/audio_classification/verified/...` のみで、**TTSへ送ったprompt全文は含まれない**。`tts_generation_results.json` にもprompt全文なし(`style.effective_style_prefix_sha256` のみ)。`STYLE INSTRUCTIONS` 文字列をOpen Window run dir全体にgrepしても0件。
- したがって「実際にTTSへ送られた入力全文」は**保存なし**。以下は(a)実行時に記録されたsha256と(b)Production関数による再構成の一致で裏付けた**再構成**。
  - [確認済み] 各dialogue clipの `style.effective_style_prefix_sha256 = add26d27a79c2cbee982eb5ddc32616b8294494a316b973215c94cccc76ede26`(Open Window/Magiの全dialogue clip同一)。`er002_common.build_style_prefix()`(1842字)のsha256を今回計算した結果が**完全一致**。= 実行時に送られたstyle部は下記1842字と同一と確認。
  - [確認済み: `er012_b_family_voices_production_01.py:519-520`] `prompt = p4c.build_tts_prompt(text, style_prefix_override or p9a.ENGLISH_STYLE_PREFIX)`。Zのdialogueは`style_prefix_override`を渡さない(`er063_family_z_audio_01.py:730-735` `style_text_for(dialogue)=None`、`:853-865` dialogue関数)ため、既定`ENGLISH_STYLE_PREFIX`(= `er003_b1_p4_audio.py:66` → `er002_common.build_style_prefix()`)。
  - [確認済み] text部は `n3_tts.tts_safe_news_en(spec.text)`(`er063:815-818`)後。下記の例のtextはこの変換で不変(引用符`"…"`を含んだまま送られる)。`_pnap_supply`(固有名詞綴り置換)は固有名詞を含まないclipでは影響なし。
  - [確認済み] model = `gemini-2.5-pro-preview-tts`(`tts_generation_results.json` `model_ids_measured`、attempts `tts_model_id`)。narratorは別model `gemini-3.8-flash-lite-tts`。

## 1. TTSへ送られる1 callの完全構造(再構成。全例共通。style部は全dialogue clip同一)

(例1のclipで`.venv`再構成した全文。prompt_chars=2294、prompt_sha256先頭=8c917f335f2be3f5)

```
The message below has two clearly separated sections.

=== STYLE INSTRUCTIONS (meta-guidance only — do not speak this section aloud, it only describes how to perform the reading in the next section) ===
TTS the following complete story in natural, engaging English.

Speak directly to one interested listener rather than announcing to a large crowd.

Create a natural emotional arc that follows the meaning already present in the script. Let the energy, weight, and pace rise or fall when the story itself changes. Do not add excitement, sadness, urgency, or drama that is not supported by the words.

Carry the meaning naturally across sentence boundaries. Do not reset your pitch, energy, or rhythm after every sentence. Group related sentences into complete thoughts, while keeping important contrasts and turning points clear.

Treat the narration as one continuous program, even when it is generated in separate sections.

Read every title, section heading, and subsection heading exactly as written. Never skip, paraphrase, shorten, or silently absorb a heading into the following text.

Do not shout, sound like a movie trailer, become gloomy or sleepy, or use a distant and overly formal newsreader style.

Give the narration a noticeably animated, emotionally present, and expressive delivery.

Use a clearly wider vocal range, stronger emphasis on important words and turning points, and more distinct rises and falls in energy.

Make the listener feel that the story matters and that you genuinely want them to keep listening.

Keep the narration moving with confident momentum, including during explanatory passages. Avoid becoming passive, flat, or overly restrained.

Allow the most important moments, contrasts, and conclusions to land with clear emotional impact.

Use stronger expression than Level 1, but vary the intensity across the story. Do not stay at maximum intensity throughout.

Do not shout, force emotion, exaggerate feelings that are not present in the script, or sound like a sports commentator or movie trailer.
=== END STYLE INSTRUCTIONS ===

=== TEXT TO SPEAK (speak this section aloud exactly as written, and nothing else — do not speak anything from the STYLE INSTRUCTIONS section above) ===
"Please let him still think I'm pretty,"
=== END TEXT TO SPEAK ===
```

- 観察([確認済み]、上記文字列から): style部は「完全な**物語全体**をTTSせよ」「文境界をまたいで意味を運べ」「感情の弧は**台本にすでにある意味**に従え」という**地の文ナレーション用の汎用文**。**セリフ専用ではなく、話者名・感情・場面・相手・直前直後の文は一切含まない**。「台本」として渡るのは`TEXT TO SPEAK`の**当該1セリフのみ**。
- retry経路: attempt 1〜3は同一prompt(`er012_b_family_voices_production_01.py:518-520`のループ内で毎回同じ`build_tts_prompt(text, style)`)。TTS技術失敗/発話区間検出失敗時のみ`generate_voice_body_minimal_fallback`(`:541`、定義`:451-479`)へ落ち、その場合のstyleは`MINIMAL_INSTRUCTION_PREFIX`=「Speak the following text aloud naturally and clearly, in a warm podcast announcer voice. Do not add, omit, or change any words.」(`er003_v1_repro01_main_generate.py:538-541`)で**感情指示はさらに無くなる**。実績: 全run集計(§5)でdialogue clip 415記録中 minimal_fallback使用0件。

## 2. 例1: 感情が強いセリフ — 『賢者の贈り物』 Advanced `full_story_part2_c7`(Della)

物語位置: 髪を売り、Jimの時計用チェーンを買い、帰宅後Jimを待つ場面。Della が「どうか今も私をきれいだと思わせて」と祈る。
台本上の演出情報はこの**直後の別clip**にある: `part2_c8` narrator「she whispered.」。

[確認済み: `er026_output/family_z_production_e2e_01/the_gift_of_the_magi/run_sf_prod_01/segment_plan_b1b.json`]

| 位置 | clip | 話者 | Voice | text(clip全文または冒頭) |
|---|---|---|---|---|
| 前 | part2_c6 | narrator | Aoede | At the first touch of the scissors, Della shut her eyes. For two hours afterward, she hurried from shop to shop. Finally, she found it: a simple platinum watch chain. ... |
| **対象** | **part2_c7** | della | **Zephyr** | `"Please let him still think I'm pretty,"` |
| 後 | part2_c8 | narrator | Aoede | she whispered. |

実TTS入力(再構成): §1の全文(style部1842字 + `"Please let him still think I'm pretty,"`)。**前後のclip(c6=髪を切る場面、c8=she whispered)はTTS入力に含まれない**(送られるのは上の1セリフのみ)。「whispered(ささやき)」という演出情報は別clip(c8、narratorのAoede)にしか無く、c7のTTSは知らない。

生成結果: [確認済み: `…/the_gift_of_the_magi/run_sf_prod_01/b1b/audit/tts_generation_results.json` `full_story_part2_c7`] model=gemini-2.5-pro-preview-tts / voice=Zephyr / attempt 1回(`english_style_prefix_wide_margin`) / classification=NORMALIZED_MATCH / verified=True / ASR text=`Please let him still think I'm pretty.` / judge=PASS / speed_profile=adv_dialogue_fast6(生成後に約6%高速化)/ dur=2.439秒 / 再利用でない。**Gate(ASR一致・値/否定ガード)は「正しい語が読まれたか」しか見ない。ささやき・祈りの感情の有無は判定対象外**。

機械指標(粗い。値は[確認済み]、解釈は[推測]。ささやきか否かは**人手試聴必要**):
- 保存wav `…/b1b/narration/full_story_part2_c7_original.wav`(高速化前の原音): 話速3.44語/秒(Della 6本中2位)、RMS -15.5 dBFS(Della 6本中**最大**)、F0中央値214Hz。→ ささやきなら「低音量・低速」が期待されるのに対し、機械指標は**逆方向**(速め・大きめ)。ただし全clipのpeakが0.70に揃っておりRMSの絶対比較には限界(§6)。結論は[推測]: 少なくとも「ささやき」は反映されていない可能性が高い。ユーザー試聴での確認が必要。

## 3. 例2: 相手への返答・掛け合い — 『開いた窓』 Advanced `part1_c4`(Vera)→`part1_c5`(Framton)

[確認済み: `er026_output/family_z_production_e2e_01/the_open_window/run_sf_prod_01/segment_plan_b1b.json`](最終版=2026-10-23ユーザー最終試聴PASS済みの公開物と同じrun)

| 位置 | clip | 話者 | Voice | text |
|---|---|---|---|---|
| 前 | part1_c3 | narrator | Aoede | said Vera, her fifteen-year-old niece. |
| **質問** | **part1_c4** | vera | **Zephyr** | `"Do you know much about her?"` |
| **返答** | **part1_c5** | framton | **Algieba** | `"Almost nothing,"` |
| 後 | part1_c6 | narrator | Aoede | he admitted. Vera glanced towards the French window, which stood wide open to the lawn. |
| 次 | part1_c7 | vera | Zephyr | `"Her great tragedy happened three years ago today."` |

実TTS入力(再構成。prompt_chars: c4=2283 sha256先頭eeadb30caac74528 / c5=2271 sha256先頭74b4d240eb972947): style部は§1と同一、`TEXT TO SPEAK`はそれぞれ `"Do you know much about her?"` / `"Almost nothing,"` のみ。**c5(返答)のTTS入力にc4(質問)は無い。c4のTTS入力にも「見知らぬ客に探りを入れる少女の質問」という情報は無い**。「he admitted(認めた)」はc6(narrator)にあり、c5には渡らない。

生成結果: [確認済み: `…/the_open_window/run_sf_prod_01/b1b/audit/tts_generation_results.json`] c4: Zephyr, attempt1 NORMALIZED_MATCH verified, PASS, 1.867秒。c5: Algieba, attempt1 NORMALIZED_MATCH verified, PASS, 1.717秒。2 clipは**別々のAPI呼出**で、互いのwav・text・感情を参照していない。組立時に`c4 → 0.2秒無音 → c5 → 0.2秒無音 → c6(narrator)`の順で連結される([確認済み: `er013_family_c_production_runner_01.py:665-670` dialogue後0.2秒/narrator後0.5秒、各clipを個別にtarget RMSへgain)。

機械指標(原音): c4 話速4.39語/秒・F0中央値245Hz(音程幅 約11.2半音)、c5 話速1.56語/秒・F0中央値111Hz(別Voice男声なので比較不可)。**返答が質問に「間」や「食い気味」で応じているかは機械指標では測れない**。clip間の物理間隔は固定0.2秒(話の内容・感情に依らず一定)= 掛け合いのテンポは**組立で一律**、TTS側では制御されない([確認済みコード])。

## 4. 例3: 同じ人物の感情が場面で変化 — 『賢者の贈り物』 Advanced の Della(Zephyr、全6セリフ)

[確認済み: `…/the_gift_of_the_magi/run_sf_prod_01/segment_plan_b1b.json` と `…/b1b/audit/tts_generation_results.json`]

| clip | 場面(台本の地の文から) | text | prompt構造 | 原音の機械指標(話速語/秒, RMS dBFS, F0中央値Hz, 音程幅半音) |
|---|---|---|---|---|
| part2_c2 | 髪を売りに店へ。不安・決意 | `"Will you buy my hair?"` | style同一 / 前後なし | 3.72, -18.9, 190, 4.6 |
| part2_c5 | 髪を切る直前。急かす | `"Cut it quickly, please."` | 同 | 2.06, -17.5, 213, 12.7 |
| part2_c7 | 帰宅後、Jimを待つ。祈り・ささやき(c8「she whispered.」) | `"Please let him still think I'm pretty,"` | 同 | 3.44, -15.5, 214, 7.0 |
| part3_c2 | Jimへ告白(必死/健気) | `"I sold it, Jim. I couldn't let Christmas come without giving you something. It'll grow again!"` | 同 | 2.31, -19.6, 304, 13.6 |
| part3_c4 | 涙ながらの笑顔(c3「smiling through tears」)で「髪はすぐ伸びる」 | `"My hair grows quickly."` | 同 | 2.67, -16.3, 234, 9.3 |
| part3_c6 | 喜び・高揚。チェーンを見せる | `"Look! Isn't it perfect? Give me your watch."` | 同 | 2.34, -17.2, 289, 8.4 |

観察([確認済み]=表の値、解釈=[推測]):
- **全6 clipで style部のsha256は同一(add26d27…)**。場面・感情の違いを示す情報は、各clipの`TEXT TO SPEAK`の**台詞の語彙・記号(`!`,`?`,`Jim`等)だけ**。
- F0中央値は190→304Hzと変動(最大差 約8半音)しており、モデルが**台詞そのものの内容・句読点から**ある程度抑揚を変えている[確認済み値]。ただしこれが「場面の感情(不安/切迫/喜び)」と対応する保証は無い。part3_c2(告白)が最も高くpart3_c6(喜び)が次、など台詞の`!`や語彙に引きずられた変動の可能性[推測]。
- part3_c4「My hair grows quickly.」(涙ながらの笑顔)は文脈なしでは単なる事実陳述の短文。感情の手掛かりは台詞に無く、前の地の文(part3_c3)にしかない[確認済み]。→ 文脈なしで涙混じりの笑顔を演じられる根拠は無い[推測]。聞こえ方は**人手試聴必要**。
- 感情変化の「連続性」(不安→喜び)は、各clipが独立生成のため**生成側では担保されない**[確認済み: 独立API呼出]。

## 5. 全Z正式run横断のretry/再生成の実績(集計) [確認済み]

スキャン: `er026_output/family_z_production_e2e_01/*/run_*/{a2,b1b}/audit/tts_generation_results.json`(mock/_preserve/STALE除く)の `clip_kind=="dialogue"`。
- dialogue clip記録数 415、うち複数attempt 10(いずれも全attemptが`english_style_prefix_wide_margin`=**同一prompt**、`minimal_fallback`使用0)。
- 複数attemptの例: Open Window run_sf_prod_01 b1b part1_c2(`ASR_VALIDATION_UNCERTAIN`→`NORMALIZED_MATCH`)、Monkey's Paw part3_c1(同)、Melos複数run(`NORMALIZED_MATCH` verified=False→True)。
- 結論: retryは「**同じ入力(同じstyle・同じ当該セリフ)で撮り直すだけ**」。文脈/感情の追加入力は無い。

最終作品(分割単位)の統計 [確認済み: `segment_plan_{b1b,a2}.json` 各作品の最終run]:
- dialogue clip数(Adv/Std): Open Window 17/17、Magi 8/8、Monkey's Paw 17/15、After Twenty Years 19/18、Tell-Tale Heart 1/1、Melos 11/10。合計 Adv 73 / Std 69。
- **dialogue clipの語数中央値は4〜8語**、3語以下がAdv 16/Std 5。複数段落/複数引用にまたがるdialogue clip=**0**(全作品)。

## 6. 備考(限界)

- 機械指標はF0・RMS・話速のみの粗い自前実装(YIN簡易版)。感情の自然さの代替にはならない。**聴感評価は人手試聴必要**(本調査ではAI側に聴取手段が無く、音声を聴いていない)。
- 全clip原音のpeakが0.70に揃っている([確認済み])ため、各clipの絶対音量の比較は参考値。さらに組立時に各clipは個別にtarget RMSへgainされる(`er063_family_z_audio_01.py:1764-1770` `gs`、`er013_family_c_production_runner_01.py:663-664`)ため、**最終音声では「ささやき=小さい声」等の音量差は設計上ほぼ消える**[確認済みコード]。
- 例3の「場面」記述は台本(segment_plan)の地の文からの要約。原典の感情との一致は試聴・原典照合が必要。
- ユーザー試聴用wav: 例1 `er026_output/family_z_production_e2e_01/the_gift_of_the_magi/run_sf_prod_01/b1b/narration/full_story_part2_c6.wav, c7.wav, c8.wav`、例2 `er026_output/family_z_production_e2e_01/the_open_window/run_sf_prod_01/b1b/narration/full_story_part1_c3.wav〜c6.wav`、例3 Della `…/the_gift_of_the_magi/run_sf_prod_01/b1b/narration/full_story_part2_c2,c5,c7 / part3_c2,c4,c6.wav`。
