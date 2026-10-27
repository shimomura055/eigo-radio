# EVIDENCE_X_01(Family X。コピーdir実測)

コピー元: `er019_output/family_x_audio_production_wiring_01/part2_hr_evidence_01__run_r1`(source_dir `er019_output/part2_hr_evidence_01/run_r1`)→ `er128_output/evidence_01/x/part2_hr_evidence_01__run_r1`。KP選定は既存のREVIEWED。レコードはactor=evidence。

| # | 手順 | 結果 | 証跡 |
|---|---|---|---|
| 0 | 旧run G1(レコード無し) | PASS(legacy drift WARNのみ) | x/00_legacy_g1_b1b.txt |
| a | payload(v2, schema_minor:1)→`confirm --from-form --actor evidence`(a2: KP3 / b1b: KP3+vocab2+文法1) | rc=0。revision 1。a2 content_sha a2cf956beadc / b1b d26076fa8400 | x/01_confirm_form_*.txt, payload_*.json |
| a | 確定後 G1 | PASS | x/02_g1_after_confirm_*.txt |
| a | `--stage tts --level a2`(実TTS 9 chunk再生成、Gemini TTS+ASR) | 完了(¥7.39)。`--budget-jpy 10`は累計(コピーした旧usage含む25.52)判定のため完了後にBUDGET_GUARDで停止(a2 TTSは完了済み) | x/03_stage_tts.txt |
| a | `--stage assemble --level a2` | rc=0・費用0 | x/04_stage_assemble_a2.txt |
| a | `--stage player --level both` | rc=0(G1・G2/G3・G4通過) | x/05_stage_player.txt |
| b | 改変マトリクス(コピー上で1件ずつ書換え→検査→必ず復元) | G1 英語/日本語訳/vocab訳 → INTEGRITY、category(reviewのKP集合変更)→`KpReviewInconsistent`(rc=3系)、G2 TTS英語/日本語、G3 ページ訳/Part 1行、G4 解説全文/日本語訳/選定文 → すべてBLOCK。復元後baseline PASS | x/10_tamper_matrix.{txt,json} |
| b' | 実runnerで改変STOP: kp日本語訳を書換え→`--stage player --level a2` | **rc=3**。`[STOP] CONFIRMED_CONTENT_INTEGRITY_VIOLATION(a2) … 確定=過去最高に達する 観測=過去最高に達する改変`、次の一手(restore)が出る。費用0 | x/11_realrunner_tamper_player.txt |
| c | resume / STALE再バインド / STALE ISSUE(実`ensure_kp_review`、実本文、generate_fn=呼べば失敗) | a2・b1bとも resume=FINALIZED・レコード不変、再バインド=revision 1→2・content_sha不変・G1 PASS、ISSUE=PENDING `confirmed_content_issue`・レコード不変(a2は曲線引用符を含む本文で、照合の不具合を検出→是正) | x/20_ops.{txt,json} |
| d | 操作ガード select/reselect/ng/resolve-gloss/declare-absent/再confirm | すべて `CONFIRMED_CONTENT_LOCKED` | x/20_ops.txt |
| f | Part 2 MODEL patch(`g.MODEL`差替) | 凍結なし従来検査=Part2Stale(対照)。凍結あり=require_final PASS、`candidate_stage` READY(generated=false)、finalize reused、explanation不変、extract/explain LLM呼出0。保護OFF対照(使い捨てコピー)=再抽出に進む(ModelContractViolation) | x/30_part2_model_patch.json |

使用モデル/routing: TTS=Gemini `gemini-3.8-flash-lite-tts`(speech_metadata_flash_lite、voice Aoede)、ASR=OpenAI(primary)+Azure(secondary)。Part 2は新規生成なし(既存の解説を凍結)。
費用: ¥7.39(gemini 3.68 / azure 2.23 / openai_asr 1.49)。所要: tts stage 約146秒、assemble 数秒、player 約15秒。
限界: Part 2解説は`stepB_generated_frozen`(出所=Step B生成結果の凍結。ユーザーがフォームで解説全文を見て確定した値ではない=DESIGN_02 §10(a))。
