# EVIDENCE_Z_01(Family Z。コピーdir実測)

コピー元: `er026_output/family_z_production_e2e_01/melos/run_p2_evidence_r3` → `er128_output/evidence_01/z/run_kcp2b_ev_z_01`(junction `er026_output/family_z_production_e2e_01/melos/run_kcp2b_ev_z_01`。終了時にjunctionのみ撤去)。KP reviewは b1b のみ(a2は旧runでレコード無し=legacy)。

| # | 手順 | 結果 | 証跡 |
|---|---|---|---|
| 0 | 旧run G1(b1b) | PASS | z/00_legacy_g1_b1b.txt |
| a | payload(KP3+vocab…+文法 g50e12a388f)→`confirm --from-form --actor evidence` | rc=0。文法1件のsidecar+record。G1 PASS | z/01_confirm_form_b1b.txt |
| a | `--stages kp --mode real`(実run) | rc=0。Redundancy QA 1 call(`gpt-6-luna`)¥0.0596。stop_scope_check rc=0 | z/03_stage_kp.txt |
| a | `--stages provision_shell,gate,assemble,pages,page_verify --pages-dir <copy>/pages_ev --approved-budget-jpy 20`(1起動) | rc=0。追加費用0(spent_jpy 5.7398のまま)。G1〜G4・ページverify通過。所要約198秒 | z/04_stages_gate_to_page_verify.txt |
| b | 改変マトリクス | G1 英語/日本語訳/vocab訳/category/assets copy訳、G2 TTS英語、G3 Part 1行、G4 解説全文/日本語訳/選定文 → すべてBLOCK。復元後PASS | z/10_tamper_matrix.{txt,json} |
| b' | 実runner `--stages provision_shell,gate` に assets copy 訳の改変を載せる | rc=2(Z runnerの既存STOP写像)。`load_level_inputs(b1b)` で `CONFIRMED_CONTENT_INTEGRITY_VIOLATION(b1b): … 確定=誰かを水中に引きずり込む 観測=…改変`。費用0 | z/11_realrunner_tamper_gate.txt |
| c | resume / STALE再バインド / ISSUE(実`ensure_kp_review`、`zr.canonical_article_text(writer/r2.md)`) | resume=FINALIZED(Redundancy QA 0回)、再バインド=revision 1→2・G1 PASS、ISSUE=PENDING・不変 | z/20_ops.{txt,json} |
| c | `--regenerate-stage part2_cand_b1b`(実runner) | rc=2。`CONFIRMED_CONTENT_LOCKED … ユーザー確定済みの文法があります(candidate_id=['g50e12a388f'])。変更は revoke のみ`。API 0(cost_log不変)・レコード不変。runnerが`part2_failed.json`を書くので evidence_runs/z/12_part2_failed.json へ退避 | z/12_regen_part2_cand.txt |
| c | `--regenerate-stage kp_b1b` | **未実施**: 同一runを300秒内に3回起動(gate改変/part2再生成/kp_b1b)したため RESTART_STORM(`<copy>/STOP`)が自己発動。STOPは解除していない(解除はFable/ユーザーのみ)。再finalize相当は関数レベル(`confirm-revise`/`restore`の単体test、02A)で確認済み | z/13_regen_kp_b1b.txt |
| d | 操作ガード | すべて LOCKED | z/20_ops.txt |
| f | Part 2 MODEL patch | extract 0 / explain 0、凍結 frozen:39ca140a69483f6d、explanation不変 | z/30_part2_model_patch.json |
| g | 公開URL G3(read-only): `…/user_test/family_z_melos_kphr_evidence_r3/advanced.html`(HTTP 200) | BLOCK: 公開ページのKP訳は「水中に引きずり込む」(旧)、コピーの候補doc訳は「誰かを水中に引きずり込む」。旧公開ページと現docの差を検出(ユーザー確定のあるrunでは起きない種類) | z/50_public_g3.txt |
| h | Std「～」gloss(実Z 3 run: the_monkeys_paw/run_sf_prod_01、the_open_window/run_e2e_01、after_twenty_years/run_sf_prod_01) | 表示用gloss=「～をつかむ」等、TTS入力(canonical_text)は不変 | z/40_m2b_std_display.txt |

モデル/routing: Redundancy QA=`gpt-6-luna`(OpenAI Responses)。Part 2は既存解説の凍結(新規生成なし)。TTSは今回の枠では実行せず(gate〜page_verifyは既存音声を検査)。
費用: ¥0.0596(Redundancy QA)。所要: kp約33秒、gate〜page_verify約198秒。
**限界(判断候補)**: Z/Yの`_stage_precheck`は`g.cand_stage_input_sha`(抽出signature込み)で照合するため、確定済み文法でmodelだけ変えると親sha不一致STOPになる不具合を発見し、`cand_input_sha`で是正(test追加)。実run上のMODEL変更STOPの再現は実施していない(単体testとfunction-level evidenceのみ)。
