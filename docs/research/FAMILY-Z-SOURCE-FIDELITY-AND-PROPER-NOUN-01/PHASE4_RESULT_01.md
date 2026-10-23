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
