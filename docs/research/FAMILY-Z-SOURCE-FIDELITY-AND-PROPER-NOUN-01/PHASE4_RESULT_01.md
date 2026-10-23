# PHASE4_RESULT_01 (委任_06、2026-10-23) 『開いた窓』完成候補02 -- STOP: tts_b1b で HR Lock 2clip(Bertie)

Status: PHASE4_STOPPED_AT_TTS_B1B(rc=2、有料run再起動なし)。tts_a2 / gate / assemble / pages / page_verify は未実行。比較試聴ページ(user_test/family_z_open_window_02/)は未作成。

## 実行したstage(run=the_open_window/run_sf_prod_01、--mode real、TTS_EXECUTION_MODE=STANDARD)
| stage | 結果 | 出典 |
|---|---|---|
| plan | OK(話者判定。Voice割当=vera Zephyr/framton Algieba/mrs_sappleton Kore/men Schedar、Narrator Aoede。voice_assignment.json) | run_sf_prod_01/voice_assignment.json, speaker_table.md |
| support | OK(Adv/Std Preview・Comment 3件。Std JA lint警告はLISTEN_INSTRUCTIONのみ=Gateでない。Vera=ヴェラが禁止名に当たらない。spoilerなし) | support/{b1b,a2}_support.json |
| kp | OK(Adv KP3件 give way / at a moment's notice / keep someone company、KP3V含め tts_b1b内でPASS) | key_phrases/, b1b/audit/tts_generation_results.json |
| tts_b1b | **STOP rc=2** FamilyZTtsClipFailedStop: full_story_part1_c14 / full_story_part3_c2 が STOPPED(HR Lock)。他 OK 36件 | console_p4_tts.txt:4 |
| tts_a2〜page_verify | 未実行 | - |

費用: 累計 37.20円(make_real_spent_fn(cost_log.jsonl)。内訳: Writer全段12.63[Phase 3]+plan/support/kp 1.52+tts_b1b 23.05)。上限100円内。所要: plan/support/kp 約2分15秒、tts_b1b 約17分(10分cooldown含む)。

## STOP原因(仮説→反証→再現)
- 事象: 2clip(Vera長台詞中の `'Bertie, why do you bound?'` と、men の `"Bertie, why do you bound?"`)が3回とも Primary(gpt-4o-mini-transcribe)・Azure とも `Birdie, why ...` と聞き取りNG。音声自体は発話者の意図どおり(「Bertie」)と推定、ASRが同音近似語(T/Dのflap)に倒れる。
- 判定経路: er103 PNAP(固有名詞発音アラーム受理)が `NO_PROPER_NOUN_EVIDENCE` で不受理 → NG_BOTH → HR Lock。再現(API 0): `er103_proper_noun_alarm_policy_01._noun_checks("bertie","birdie", canonical_text, ...)` → `('NO_PROPER_NOUN_EVIDENCE', {'token':'bertie'}, None)`(c14・part3_c2の両canonical_textで同一)。`bertie`はCMU収録(zipf 3.08、一般語ではない)、`birdie` zipf 3.26(<4.0=一般語でない)ため一般語ブロックではなく、**固有名詞証拠が無い**ことだけが原因。反証: Ledger surfaceに `bertie` を与えると `(None,'ledger',0.667)`=受理(同module)。
- 根拠となる設計: er103 `proper_noun_evidence`(OF-PNAP-P-02): CMU収録語の大文字始まりは、文頭・引用符/括弧/コロン直後では固有名詞の証拠にしない。`Bertie` は引用符直後(part3_c2は文頭)のため証拠が成立しない。Ledger(er006_output/pronunciation_ledger_01/ledger.json)に bertie/vera/framton は未登録。Perplexity 発音調査は401失敗(cost_log: full_story_part3_c2 perplexity success=False)。
- 判定: Validator不具合ではなく、承認済みPNAP方針(P-02, fail-closed)の想定外ケース(CMU収録の人名が引用符内・文頭に出る)。解決には (A)Ledgerへ `Bertie` をB階層人承認登録、(B)PNAPの証拠源にSeed登場人物名(source_essentials/keep_name)を追加(コード/仕様変更=承認要)、(C)HR Lock人手解除 のいずれかが必要で、いずれも本委任の「コード・仕様変更禁止」「有料run再起動禁止」の外。tts_a2(Std)も同一台詞のため同じ箇所でSTOPする見込み。

## 追加で判明した品質事項(Fable受入資料)
1. **最終種明かし文の音声が脚本と異なる**: full_story_part3_c12 `Inventing convincing stories at a moment's notice was Vera's speciality.`(canonical/脚本)が、ASRが米綴り `specialty` と聞き取りTRUE_CONTENT_MISMATCH(綴り差)×2→10分cooldown→Local Rewriteで音声は `... Vera's forte.`(audio_text_deviation: replace 'speciality.' -> 'forte.'、PASS_WITH_WARNING LR_REWRITTEN)。意味は保持だが音声と英語スクリプト表示が不一致。`speciality`/`specialty` の綴り差は OPEN-459(ASR同音/綴り異形)の受理対象外だった。出典=b1b/audit/tts_generation_results.json の segments/full_story_part3_c12、pass_with_warning_listening_list.json。
2. 固有名詞アラーム: `framton`→`frampton`(Primary/Secondary一致) 8箇所を受理(アラーム付き完成、HR 0)。`vera` は発音アラーム0件(ASRが正しく転写)。operator_alarm_report.md に「アラーム集計不一致(状態9件/報告8件)」の警告が出ている(9件目はSTOPPEDの`bertie`と推定、未検証)。
3. 会話速度v2: tts_b1b の `speed_profile` は dialogue 15件 `adv_dialogue_fast6 applied=True`、STOPPED 2件は applied=False(生成のみ)、narrator `adv_narrator_none`。Std側(減速なし)は未実行のため長さ比は未確認。
4. Preview/Comment(a): spoiler lint・矛盾なし(Adv: 'listen for how her story shapes what Framton thinks'、Std Comment2/3も結末を明かさない)。結末直前の付加文(b)は writer 段でCP記入済み(Phase 3)。

## 保存先
run_sf_prod_01/{console_p4_text.txt, console_p4_tts.txt, _stop_scope_check_p4*.json, b1b/audit/*, support/*, key_phrases/*, voice_assignment.json, cost_log.jsonl}。wav/mp3はcommitしない。

---
# 追記(委任_07、2026-10-23): Std tts_a2 先行実行結果・LR表示仕様
Status: PHASE4_STD_TTS_DONE_PENDING_USER_BERTIE(tts_a2 を1回だけ実行、JST 13:20-13:26、rc=2、再起動なし。Bertie以外のHR Lockなし)。他agent(Y Phase 3 TTS)が並走中のため30分待機後に開始(ACTIVE_TASK記録)。

## tts_a2 結果(run_sf_prod_01/a2、STANDARD、`console_p4_tts_a2.txt`)
| 項目 | 値 |
|---|---|
| OK / STOPPED | OK 37 / STOPPED 2(`full_story_part1_c14`・`full_story_part3_c2`。Adv b1bと同じ2clip) |
| HR Lock理由 | 両clip 3 attempt全てASR `Birdie`(Primary・Azure)。PNAP `NO_PROPER_NOUN_EVIDENCE`(Adv側と同一)。Bertie以外のHR Lock 0 |
| LR(Local Rewrite) | Std 0件。Adv `full_story_part3_c12`(speciality->forte)のみ(委任_06既報) |
| PASS_WITH_WARNING | Std 1件: `full_story_part1_c13` `Vera said more quietly.` ASR `Veera`(primary_pass+SECONDARY_CORROBORATED、警告付きPASS)。Adv側は委任_06の `part3_c12` LR_REWRITTEN |
| 固有名詞アラーム | Framton 8 segment(受理、HR 0)。a2は集計不一致警告なし |
| 費用 | tts_a2 約24.75円(Gemini TTS 52call/OpenAI ASR 67/Azure 25/Perplexity発音調査17[401失敗])。run_sf_prod_01 累計 **61.95円 / 上限100円**(`make_real_spent_fn`) |

## 結末文のASR
- Stdの実際の結末文は `Vera needed only seconds to invent a story people believed.`(`writer/std.md` 最終行 / `full_story_part3_c12`)。ASR(1 attempt)= `Vera needed only seconds to invent a story people believed.` 完全一致、LRなし、status=OK。
- 委任文の `Making up stories in seconds was Vera's special skill.` はU1 Trialの文(`U1_TRIAL_RESULT_01.md`)で、今回のrunのStdにはない(`Making up stories in seconds` は run_sf_prod_01 内に出現しない)。run_sf_prod_01のStd結末は上記の文。
- Adv: 結末文 `Inventing convincing stories at a moment's notice was Vera's speciality.` は ASRが `specialty` と聞き取り2回NG->cooldown->LRで音声は `forte`(Adv b1b part3_c12、attempts 4)。

## 会話速度v2 evidence(`speed_profile`)
- Std: dialogue 17clipが `std_dialogue_none`(applied=False)、narrator 16clipが `std_narrator_slow6`(applied=True、tempo 0.943、slowdown_ratio 1.048〜1.060)。
- Adv(委任_06既報+再集計): dialogue 15clip `adv_dialogue_fast6`(applied=True、tempo 1.06、ratio 0.943〜0.953)、2clip(STOPPED)は applied=False、narrator 16 `adv_narrator_none`。
- 長さ比: **Std脚本とAdv脚本は別文(Std調整後)で同一台詞の同一テキスト対がない**(33 clip全てdiff_text)ため、同一台詞の秒数比は取れない。語数ベース集計(OK clip):

| 区分 | n clip | 語数 | 秒 | 語/秒 |
|---|---|---|---|---|
| Std dialogue(none) | 15 | 177 | 78.5 | 2.254 |
| Adv dialogue(tempo1.06後) | 15 | 180 | 72.8 | 2.471 |
| Adv dialogue(tempo前に逆算) | 15 | 180 | - | 2.336 |
| Std narrator(slow6後) | 16 | 214 | 95.4 | 2.244 |
| Adv narrator(none) | 16 | 223 | 95.9 | 2.326 |
- 所見: Adv会話(tempo後)はStd会話より約9.6%速い(2.471/2.254)。Adv会話のtempo前(2.336)とStd会話(2.254)の差約3.6%は別文・別voice配分の差。Std narratorは減速で語/秒がAdv narratorより約3.5%遅い。方向は仕様(Std会話減速なし/Adv会話+6%/Std narrator-6%)どおり。

## LR表示仕様の確認(Adv part3_c12、API 0、変更なし)
- 試聴ページ(user-facing)のスクリプト表示は **LR後テキストではなく原稿(canonical_text)**: `er063_family_z_audio_01.py:1870`(`row["script"] = entry.get("canonical_text") ...`)->`_user_page_rows` :1933/:1957(`uc.script_block(g["script"])`)。assembleのgate結果も `"article_text_source": "canonical(原稿のまま)"`(:1645)。
- 内部確認ページ側のみ「Local Rewrite採用(音声は原稿から変更: replace: 'speciality.' -> 'forte.')」の注記行を出す(:1875-1876)。ユーザー向け標準ページ(`_user_page_rows`)にはこの注記は載らない(:1895-1897 docstring「内部情報は載せない」)。
- `audio_text_deviation` はProduction承認済み挙動として「監査記録のみ」: `er063:1442-1454`(provenance.audio_text_deviationsへ追記、再検証フックは2026-10-12ユーザー決定で撤去、blockingにしない)、`:1499-1508`(assembly時に deviations 列挙のみ)。
- 結論: 現行仕様のままだと完成ページには `speciality`(原稿)が表示され、音声は `forte`。**意図された仕様の挙動**(原稿を正とし、音声との差は監査/PASS_WITH_WARNING listing)。Melos等の実例: er026_output配下に `"audio_text_deviation_clips": ["..."]` が非空の保存例は検出されず(grep)。ユーザー試聴時に「音声と表示が違う」と受け取られる点は、必要ならFableが仕様候補として扱う(本委任では変更しない)。
- er109 v1(表記同値層)が `speciality`/`specialty` を扱わない根拠: `er109_asr_orthographic_equivalence_01.py:12-14`(「読み候補のCMU音素列が交わる場合のみ同値、音素が1つでも違えば同値にしない」)+ :17(許容辞書は閉じた記号・略語表のみ=綴り異形辞書を持たない)。実測(`_word_prons`): speciality=S P EH1 SH IY0 AE1 L IH0 T IY0 / specialty={S P EY1 SH AH0 L T IY0, S P EH1 SH AH0 L T IY0} で音素列集合が交わらず、fail-closedで非同値。
