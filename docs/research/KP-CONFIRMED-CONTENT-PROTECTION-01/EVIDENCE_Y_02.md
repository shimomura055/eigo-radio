# EVIDENCE_Y_02(Family Y。現行runner世代のrunのコピーdirで実測。委任_03)

コピー元: `er121_output/family_y_production_01/redelivery_fee/run_style_fix_01`(現行runner世代: `audit/style_profile.json`あり。a2/b1bのTTS record・Part 1/Part 2・Adv KP解説あり。HR Lock残=preview未承認のまま。**HR Lockは解除していない**)。
コピーdir: `er121_output/family_y_production_01/redelivery_fee/run_kcp3_ev_y_01`(STORM自己発動のためSTOP保持・以後使用せず)と `run_kcp3_ev_y_02`(実測の本体)。runnerの固定run root(`RUN_ROOT=er121_output/family_y_production_01`)へ**junction無し**で実コピーを置いて動いた(runnerはrun root直下しか見ない)。完了時に `C:\Users\tensh\kcp3_evidence_copies_20261027\y\` へ退避(gitに載せない)。
`cost_log.jsonl` はコピー後に空にして(原本は `cost_log_copied_origin.jsonl`へ退避)、本委任の実費だけが残るようにした。

| # | 手順 | 結果 | 証跡(`evidence_runs/y2/`) |
|---|---|---|---|
| 0 | 旧run G1(レコード無し) | a2/b1b とも PASS | 00_legacy_g1_*.txt |
| a | payload v2(a2: KP3 / b1b: KP3+vocab2+現行Adv Part 2の文法1件 `g1de62b0de2`)→`confirm --from-form --actor evidence` | a2/b1b rc=0、revision 1。確定後の直後は `KP_FINAL_SIGNATURE_MISMATCH`(finalize前)→kp stageで解消 | 01_confirm_form_*.txt, 06_confirm_form_*.txt(y_02), 02_g1_*.txt |
| a' | **発見**(下記D1): 自動採用(UNREVIEWED_AUTO_ADOPTED)のrunへ後から確定を入れると `kp_a2/kp_b1b` の来歴 input_sha(=sha(本文\|review署名))が変わり、`--stage kp` が `FamilyZProvenanceMismatchStop: kp_b1b: 親sha不一致` でSTOP(rc=2、API 0) | 確定がkp stage前に入っていた状況を再現するため、コピーの来歴entryのinput_shaだけを現在値へ付け替え(`tools/kcp3_ev_y_rebind_01.py`。出力shaは触らない) | 03_stage_kp_L2_provmismatch.txt, 03a_prov_rebind.txt, 06a_prov_rebind.txt |
| a | `--stage kp --mode real`(y_02) | rc=0。Redundancy QA(`gpt-6-luna`)×3 = ¥0.3168。G1 PASS | 07_stage_kp.txt |
| b | `--stages gate`(y_01) | rc=2 `FAMILY_Y_GATE_BLOCK`: a2 `preview` セグメントの `JA_STYLE_ACTUAL_UNMEASURED` / `STYLE_BASE_SHA_MISMATCH_OR_MISSING`。**保護とは別理由**(原本runが preview 未承認・HR Lock残のため)。`_assert_study_ready`(Part 1/2の確定との一致)は通過後の停止 | 04_stages_gate_to_page_verify.txt, 04a_gate_summary_y01_L4.json |
| b | `--stages assemble,pages,page_verify`(y_02) | **rc=0**。assemble a2/b1b OK、pagesで`pages/index.html`(Std+Adv)生成、page_verify `ok:true violations:[]`、`kp_selection_verified.b1b legacy:false ok:true`、`part2_verified OK`。追加費用0(spent 0.3168のまま) | 08_stages_assemble_to_page_verify.txt, 08a/08b |
| c | 改変マトリクス(実artifact・y_02) | a2 G1: 英語/訳/category/assets copy訳、G2: TTS英語/日本語、G3: ページ訳 → すべてBLOCK。b1b G1: 英語/訳/vocab訳/category/assets copy、G2: TTS英語、G3: Part 1行、**G4: 解説全文/日本語訳/選定文** → すべてBLOCK。復元後PASS | 10_tamper_matrix.{txt,json} |
| c' | 実runner: b1b のKP訳artifactを改変→`--stage kp` | **rc=2** `FAMILY_Y_KP_REVIEW_STOP(b1b): CONFIRMED_CONTENT_INTEGRITY_VIOLATION … (G0) 確定=人にとって納得がいく 観測=…改変`、API 0。`restore`(API 0)で復旧(`confirmed_content_issue.json`→`.resolved`、旧artifactは`*.RESTORE_SUPERSEDED_1.json`に退避) | 11_rt1_tamper_kp_assets.txt, 11a/11b |
| c' | 実runner: `pages/index.html` の a2 KP訳を別訳へ→`--stage page_verify` | **rc=2** `FAMILY_Y_KP_SELECTION_OUTPUT_MISMATCH(a2): … G2/G3 … p_9f42c71603.japanese_gloss(ページ表示) 確定=努力する 観測=(ページに表示されていない)`。API 0。`restore`で復旧 | 12_rt2_tamper_page_verify.txt, 12a/12b |
| c' | 実runner: `study_text/part2_result.json` の解説全文を改変→`--stage pages` | **rc=2** `FAMILY_Y_PART2_NOT_READY(stage_pages): Part 2の解説が凍結した確定解説(frozen:c397bd981fa5389b)と一致しません`(G4)。API 0 | 13_rt3_tamper_part2_pages.txt |
| d | resume / STALE再バインド / STALE ISSUE(実`ensure_kp_review`、本文=`ys.canonical_body(translate/<lv>.md)`) | a2・b1b とも resume=FINALIZED(生成API 0)、再バインド revision 1→2・content_sha不変・G1 PASS、ISSUE=PENDING `confirmed_content_issue`・レコード不変 | 20_ops.{txt,json} |
| e | 操作ガード(select/reselect/ng/resolve-gloss/declare-absent/再confirm) | a2・b1b とも全て `CONFIRMED_CONTENT_LOCKED` | 20_ops.txt |
| f | `--stage kp --regenerate-stage part2_cand_b1b`(実runner) | **rc=2** `CONFIRMED_CONTENT_LOCKED: … 変更は revoke のみ`。API 0(cost_log 3行のまま)・確定レコード/文法sidecar不変。runnerが `part2_failed.json` を書く(D4) | 14_regen_part2_cand_b1b.txt, 14a_part2_failed.json |
| f | `--stage kp --regenerate-stage kp_b1b`(実runner) | **未観測**: 並行Agentの`er120_part2_grammar_production_01.py`編集(GRAMMAR-PREGEN-ALL-LEVELS-01)と同時刻に起動したため `TypeError: resolve_candidates() missing … 'level'` で停止(rc=2、API 0、確定レコード不変)。本委任の欠陥ではない(D6)。他AgentのWIPが落ち着いた後の再試行は§末尾 | 15_regen_kp_b1b.txt |

## 結論(Y)
- Std(a2)・Adv(b1b)とも、現行runnerの `kp → assemble → pages → page_verify` が確定後に API 0 で通る。確定後の改変は、runner経由で G0/G1(kp stage)・G2/G3(page_verify)・G4(pages) の各段で rc=2 のSTOPになり、関数レベルのマトリクスでも全項目がBLOCKした。
- `gate` stage は保護の外側の理由(preview HR Lock)でSTOP(Y run固有。保護は関与しない)。
- 未観測: gate stage通過後の保護(HR Lock未解除のため。**HR Lockは解除しない**)、`--regenerate-stage kp_b1b`(上記)。
