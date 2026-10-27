# EVIDENCE_X_02(Family X Adv=b1b。コピーdirで実測。委任_03)

コピー元: `er019_output/family_x_audio_production_wiring_01/part2_hr_evidence_01__run_r1`(b1b: TTS済み・Part 1/Part 2・assembled あり。source_dir `er019_output/part2_hr_evidence_01/run_r1`)。
コピーdir(**repo外**): `C:\Users\tensh\kcp3_evidence_copies_20261027\x_adv`。Xのrunnerは `--out-dir` を持つため junction 無しで動いた(`--slug part2_hr_evidence_01 --run run_r1 --out-dir <コピー>`)。**TTSは再生成していない**(`--stage tts` 不使用。`raw_usage_log.jsonl` は125行のまま=API 0)。

| # | 手順 | 結果 | 証跡(`evidence_runs/x2/`) |
|---|---|---|---|
| 0 | 旧run G1 | PASS | 00_legacy_g1_b1b.txt |
| a | payload v2(KP3+vocab2+文法`g064ddb76fb`)→`confirm --from-form --actor evidence` | rc=0、revision 1。G1 PASS(Xは署名のずれ無し) | 01_confirm_form_b1b.txt, 02_g1_after_confirm_b1b.txt |
| a | `--stage study_text --level b1b` | rc=0。Part 1(解説・訳)と Part 2 は `reused:True`(API 0) | 03_stage_study_text.txt |
| a | `--stage assemble --level b1b` | rc=0、API 0 | 04_stage_assemble_b1b.txt |
| a | `--stage player --level b1b` | rc=0(G1・G2/G3・G4通過)、API 0 | 05_stage_player_b1b.txt |
| b | 改変マトリクス | G1: 英語/訳/vocab訳/category → BLOCK。G2: TTS英語 → BLOCK。G3: Part 1行 → BLOCK。G4: 解説全文/日本語訳/選定文 → BLOCK。復元後PASS | 10_tamper_matrix.{txt,json} |
| b' | 実runner: b1b KP訳artifactを改変→`--stage player` | **rc=3** `CONFIRMED_CONTENT_INTEGRITY_VIOLATION(b1b) … 確定=先物価格 観測=先物価格改変`、次の一手=`restore`。API 0 | 11_realrunner_tamper_player.txt |
| c | resume / STALE再バインド / STALE ISSUE | FINALIZED(生成API 0)/ revision 1→2・G1 PASS / PENDING・不変 | 20_ops.{txt,json} |
| d | 操作ガード | 全て LOCKED | 20_ops.txt |
| P7 | KP英語解説(Adv `explanation`)と復唱(`phrase_repeat`)の整合 | 実record: `english`/`phrase_repeat` の `canonical_text` は確定英語と一致、`explanation` はその英語句の定義文(例: `futures price` → "a price set now for buying or selling something at a later date")。**発見(D2)**: `phrase_repeat`(復唱)を改変してもG2が止めなかった → 同一委任内で是正(`verify_outputs`に`phrase_repeat`検査を追加。test 2件) | 12_p7_explanation_consistency.txt |

## 結論(X Adv)
b1b の `study_text`/`assemble`/`player` は確定後も API 0 で通り、改変は G1〜G4 で止まる(runnerは`player`でrc=3)。KP英語解説は確定英語を元に生成されるため整合している(解説の文面そのものは生成物でG2の検査対象外=設計どおり)。`--regenerate-stage` はXに無い(Part 2再抽出は関数レベルでrevoke必須、02B確認済み)。
