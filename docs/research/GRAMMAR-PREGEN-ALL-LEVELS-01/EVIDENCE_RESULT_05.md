# EVIDENCE_RESULT_05 全6経路の実run evidence(委任_05、2026-10-27)

actor は全て `evidence`(runtime evidence用。ユーザー確定ではない。user_ref=`docs/pm/delegation_log/2026-10-27_GRAMMAR-PREGEN-ALL-LEVELS-01_DELEGATION_05.md`)。モデルは全call `gpt-6-luna`(現行Production契約=最新)。音声・TTS再生成 0(tts stageは1回も起動していない)。証跡: `evidence_runs/{y,z,x}/`(各ファイル名は下表)。

## 使用run(新コピー。GPG05A/05B以降の形式へ合わせるためAdv側の旧v1 Part 2成果物を `_orig_b1b_part2_v1_aside/` へ退避して再開)
| 経路 | コピー元 | コピー先 | 退避理由 |
|---|---|---|---|
| X Std/Adv | `er019_output/family_x_audio_production_wiring_01/part2_hr_evidence_01__run_r1` | `...__run_gpg5_x_01`(source: `er019_output/part2_hr_evidence_01/run_gpg5_x_01`) | Adv: 旧v1 Part 2(2件世代)。Std: 元々Part 2無し |
| Y Std/Adv | `er121_output/family_y_production_01/redelivery_fee/run_style_fix_01` | `run_gpg5_y_01`(**STOP保持・以後使用せず**、下記) | Adv: 旧v1 auto採用(HRなし)。Auto採用reviewのままだとTop2の事前生成が走らずTop2採用を実証できないため |
| Z Std/Adv | `er026_output/family_z_production_e2e_01/melos/run_p2_evidence_r3` | `run_gpg5_z_01` | Adv: 旧v1。r4(ZERO)は不使用(本runのStdがZEROを再現) |

## 実証項目 x 経路
| 項目 | X Std(a2) | X Adv(b1b) | Y Std(a2) | Y Adv(b1b) | Z Std(a2) | Z Adv(b1b) |
|---|---|---|---|---|---|---|
| (i) Top1/Top2のみ提示(`03_presented_*.json`, `03_grammar_explanations_*.json`) | 候補1(提示1) | 候補1 | **候補2(Top1 g31f4b39e68/Top2 g5b0e3d12cb、items=2)** | **候補2(Top1 g1de62b0de2/Top2 g938cd4b23a、items=2)** | 候補0 | 候補1(提示1) |
| (ii) 1件採用(`06_payload_*`, `07_confirm_*`, `11_confirmed_selection_*`) | Top1 gddf816bb8f | Top1 g241d45439e | Top1 g31f4b39e68(確定済み) | **Top2 g938cd4b23a(非Top1)確定済み** | - | Top1(=唯一) g50e12a388f |
| (iii) 0件omit | - | - | - | - | **ZERO(NO_CANDIDATE_UNREVIEWED、`11_part2_result_a2_ZERO.json`)** | - |
| (iv) 2件指定の拒否(API 0) | - | - | **CLI: `Part2ReviewError`(rc=2、`05_cli_two_ids_reject.txt`)、from-form: `CONFIRMED_CONTENT_ISSUE` rc=4(件数2>1、`05_form_two_items_reject.txt`/`05_form_two_items_issue_record.json`)** | - | - | - |
| (v) finalize LLM 0(usage行数前後) | **5->5**(`08_usagelines_before_finalize.txt`) | 同左 | 未実施(STOP) | 未実施(STOP) | cost_log part2系は cand/expl のみ(finalize後に増加なし) | 同左 |
| (vi) ページ Std節/Adv Part 1直後に文法ブロック1、`verify_outputs(level, html_text=節)` | PASS(`12_player_sections.txt`) | PASS(Part 1が文法の前) | 未実施 | 未実施 | page_verify `part2_verified` std blocks=1(「構文なし」ブロック、`12_page_verify_local.json`) | adv blocks=1 |
| (vii) KCP G0〜G4 + `confirmed_grammar_frozen.json` | G1 PASS(`10_g1_a2.txt`)+frozen(`11_confirmed_grammar_frozen_a2.json`)。G4はplayerのverify_outputs | 同左(b1b) | confirm済み(sidecar `confirmed_grammar.json`)。G1はfinalize前のため `KP_FINAL_SIGNATURE_MISMATCH`(想定内、`10_g1_*.txt`)。frozen未 | 同左 | **対象外**: a2のKPは旧run互換(`_kp_legacy_run`)でreview無し。KCP sidecarは作っていない(下記限界) | G1 PASS(`10_g1_b1b.txt`)+frozen(`11_confirmed_grammar_frozen_b1b.json`)+kp_selection_verified/part2_verified OK |
| (viii) 凍結後model名変更 `require_final`->Part2Staleにならない(API 0、`gpg5_frozen_model_change_01.py`) | PASS(`09_frozen_model_change_a2.txt`) | PASS(`..._b1b.txt`) | 未実施(frozen未) | 未実施 | - | PASS(`09_frozen_model_change_b1b.txt`) |
| (ix) 費用 | 下記COST_05 | | | | | |
| (x) HR actor | evidence | evidence | evidence | evidence | (HRなし: 候補0) | evidence |

## 発生事象
1. **Y RESTART_STORM(私の運用ミス)**: `run_gpg5_y_01` を 12:01:47 / 12:04:17 / 12:06:20 の3起動(273秒内。直前の2回は150秒間隔は守ったが「5分3回」を超えた)。`--stage kp`(確定後の再開)が `FAMILY_Z_RESTART_STORM` で rc=3、`STOP` 作成(中身は `evidence_runs/y/13_STOP_RESTART_STORM_kept.json`)。API 0。Yの run を新名でコピーして継続する案は STOPの回避に当たると判断(自動判定でも拒否)し実施せず、STOPは**削除せず保持**。解除(`--clear-stop`)はFable/ユーザー権限。残作業: finalize、assemble/pages/page_verify、(v)(vi)(vii)(viii)。
2. 起動間隔: X `study_text` finalize(12:26:00)の次の `player`(12:27:41)は101秒間隔で、150秒基準を満たしていない(同一run 5分3回は満たす。全体基準の私の逸脱として記録。実害なし: 他Agent runnerは停止済みを確認)。
3. Z: 退避したAdvの Part 2 を再抽出するため `--regenerate-stage part2_cand_b1b`(確定前・許可)を1回使用(最初の抽出は候補0、再抽出で1件)。`part2_b1b`(finalize)は旧entryのinput_sha不一致のため `--regenerate-stage part2_b1b` が必要(runnerの案内どおり。LLM 0)。**Y finalizeも同様に必要になる見込み**。
4. X: 候補は各1件(Top2無し)。Top2/2件系の実証はY Std/Adv(確定まで)のみ。Zは設計上最大1件。

## 限界(隠さず記録)
- Y: finalize以降(ページ・frozen・(v)(vi)(vii-frozen)(viii))は**未観測**。Top1/Top2提示・Top2採用・2件拒否は観測済み。
- Z Std(a2): 旧run互換KPのためKCP sidecarなし(0件はreview=`NO_CANDIDATE_UNREVIEWED`のまま前進)。Z Stdの0件ページ(「構文なし」1ブロック)は観測。
- X 0件経路はAI島(`ai_island_temple__run_form_prod_01`、commit d05729316: Std/Adv とも REVIEWED 0件確定・`part2_result.status=ZERO`)の参照のみ。
- 2件採用は新仕様で禁止(旧「2件採用」の実証は不要)。
