# EVIDENCE_RESULT_04 Family Z Standard(a2) 確定内容保護 実run evidence(委任_04、2026-10-27)

actor は全て `evidence`(runtime evidence用。ユーザー確定ではない)。user_ref=`docs/pm/delegation_log/2026-10-27_KP-CONFIRMED-CONTENT-PROTECTION-01_DELEGATION_04.md`。使用モデル: 全LLM call `gpt-6-luna`(最新)、TTS `gemini-3.8-flash-lite-tts`、ASR `gpt-4o-mini-transcribe`+`azure-speech-stt`。証跡: `evidence_runs/z3/`。

## go/no-go(起動前に判定。結論=GO)
- 来歴定義 `er062_family_z_writer_01.py:66-70` `DEPENDENTS`: `std_adjust -> [plan_a2, kp_a2, part2_cand_a2]`、`kp_a2` は子孫なし。`mark_stale_descendants`(同:669)は DEPENDENTS だけを辿るため、**kp_a2 の確定→finalizeでstale化される下流は無い**。Full Story TTS(`tts_a2`)は来歴チェーン(`ALL_STAGE_NAMES`:71-72)に存在しない。
- TTS再利用は `generate_or_reuse_z`(`er063_family_z_audio_01.py:845-`)の reuse_key(正規化本文+style version+voice+style prefix+backend)一致。KP finalizeは Full Story clip の reuse_key を変えない。→ Full Story TTSはstaleにならない構成。KP音声(kp{n}_en/_ja)のみ再生成。
- `--only-clips` で TTS 生成対象をKP clip 6件に限定(費用の上限を機械的に制限)。

## 使用run
コピー元 `melos/run_p2_evidence_r3`(Zのa2=旧run互換・TTS有り、KCP sidecar無し)を `melos/run_kcp4_ev_z_01` へコピー(STOP/lock/stop_check/pages_evidence/STALE退避/*.logは除外)。a2のKP候補は KP75 evidence の `melos/run_kp75_ev_01/key_phrases/a2`(候補doc phrase4+word4、本文sha `efba2a23` = r3のstd.mdと一致[sha256 `6a47e9d774fc`])を差し込み、旧a2 KPは `_legacy_a2_key_phrases_r3/` へ退避。委任文の「7+5形式」は候補docに7phrase+5wordが揃うものが無く(kpbf=phrase7のみ・kp75=4+4)、**候補生成の再実行はせず**kp75のphrase4+word4を使用(確定要件の3/2/2を満たす)。

## 経路表(Z Standard)
| 段 | 結果 | 証跡 |
|---|---|---|
| G0 確定 a2 | payload v2(①KP3: `p_37c58c930b` pull someone under / `p_a31a016ed7` lose one's trust in someone / `p_6bd48ea268` without asking for another promise、②`demand`,`shepherd`、③`Silence`,`exact`)を `confirm --from-form --grammar-pending --actor evidence` → rev1 確定。Std仕様どおり ②は `STD_CATEGORY2_NO_SLOT`・③は `CATEGORY3_NO_CONSUMER` で unconsumed に記録(消費されない)。文法は pending | z3/payload_a2.json, 01_confirm_form_a2.txt |
| 文法 a2 | runnerの `part2_cand_a2` 抽出(L3内)の結果=候補0 → `confirm --grammar-from-form`(grammar[])で **0件確定**(`NO_CANDIDATE_UNREVIEWED`、rev2)。確定KPは不変 | z3/06_confirm_grammar_a2.txt |
| 付帯 b1b | (同runのAdvを通すため)`grammar-pregen`(g50e12a388f)後に from-form 確定 | z3/03_*, 02_* |
| kp stage(G1入口 finalize) | L1(`--run`にpath指定誤り、API 0・rc=2)→L2 `kp_a2: 親sha不一致`(確定が後から入ったためinput署名が変わる=KCP3所見D1と同じ。API 0・rc=2)→L3 `--regenerate-stage kp_a2`(確定済みreviewからの再finalize。選び直し無し)で a2 finalize、assets=確定3件。続けて `part2_b1b` 親sha不一致(rc=2、案内どおり)→L4 `--regenerate-stage part2_b1b` rc=0 | z3/04a, 05, 07 |
| finalize LLM 0 | L4(Part 2 finalize)前後で `cost_log.jsonl` 41→41行。L3の追加3行は `part2_cand_a2`(候補抽出1)+`kp`(Redundancy QA 2)で、確定集合の再finalize自体はLLMなし | z3/_usage_lines_before_L4.txt |
| TTS(KP音声のみ) | L5 `tts_a2 --only-clips kp1..3_en/_ja` rc=0。wav sha差分は kp1_ja/kp2_en/kp2_ja/kp3_en/kp3_ja の5件のみ(kp1_enは同じ語句のため再利用)。kp4/kp5・Full Story他clipは不変 | z3/08, 09_wav_diff_after_tts.txt |
| Full Story音声 | **変化したのは `full_story_part2_c1` のみ**(Std chunk planner `chunk_tts_v1_x_paragraph_z_r1_20261025` が旧run単一clip(Oct12)を2 chunk要求に変えたため、L6で `--only-clips full_story_part2_c1` により再生成。**KCP/KP finalizeとは無関係**。新規Z Std記事では最初から同planner)。part1(c1-c11)・part3(c1-c11)・intro/shell・comment・japanese_title 等の wav sha は全て不変 | z3/12_wav_changed_list.txt, _a2_narration_wav_sha_before/after_tts2.txt |
| G1〜G3 実runner通し | L7 `--stages provision_shell,gate,assemble,pages,page_verify`(1起動)rc=0、追加LLM/TTS 0(spent 8.3515のまま)。a2のTTS KP件数3=確定3(旧runの`OUTPUT_MISMATCH`が発生しない=KCP3 Z Stdの未観測を解消) | z3/13_stages_provision_to_page_verify.txt |
| page_verify | `kp_selection_verified a2: ok=true legacy=false`、signature `c63b6917…`、kp=確定3件、vocab=[](Stdは②なし)。b1bも ok=true legacy=false | run/page_verify_local.json |
| 確定不変 | `confirmed_selection.json`(a2)は文法確定後(L4前)からTTS・assemble・pages・page_verify・改変マトリクス全後まで `cmp` 同一 | z3/_confirmed_selection_a2_before_*.json |
| G1 単体 | `require_final_consistent` a2 PASS / b1b PASS | z3/14_g1_a2.txt |
| 改変マトリクス(a2、コピーdir。必ず元へ戻して再検証) | G1: kp英語/日本語訳 BLOCK(INTEGRITY rc=3)・category変更 BLOCK(KpReviewInconsistent)。G2: baseline PASS・TTS record英語/日本語 BLOCK。G3: baseline PASS・**`standard.html`のみ改変はPASS(止まらない)**(KCP3 D3と同じ既知: 検査はindex+standardの両ページを見る設計)。両ページ同時改変は BLOCK(INTEGRITY、z3/21で確認)。全復元後 baseline PASS、wav/確定レコードはバイト同一に復帰 | z3/20_tamper_matrix.{txt,json}, 21_g3_pages_a2.txt |
| G3 ページ表示 | 確定japanese_gloss3件(人を水中に引き込む/さらに約束を求めずに/自分が誰かを信じる気持ちを失う)が `standard.html`・`index.html` の両方に表示。今回の3件は「～」を含まないため M2-b(「～」表示と「なになに」TTS入力の分離)の該当表示は本runでは再現せず(02B `z/40_m2b_std_display.txt` で実測済み) | z3/21_g3_pages_a2.txt |
| ガード実証(API 0) | 確定後の a2 で `reselect`/`ng --ng`/`select`/`declare-absent --user-ref`/`grammar-select omit` が全て `ConfirmedContentLocked`(REFUSED)。`confirm-revise` は `--user-ref` 無しだと CliError(必須)。実行後 `confirmed_selection.json`/`kp_human_review.json` sha不変 | z3/10_guard_ops_a2.txt, _guard_before/after.txt |
| phrase_repeat | Z a2のTTS recordには `phrase_repeat` 項目が存在しない(X/Y専用)→G2は English/Japanese の record 一致で検査(上記BLOCK) | - |

## 起動履歴(RESTART_STORM回避。全体間隔5分前後、同一run 5分内3回なし)
L1 12:47:18(rc=2 引数誤り・API0)/L2 12:52:26(rc=2 親sha不一致・API0)/L3 12:58:22 kp_a2再finalize(a2 finalizeは完了、続くpart2_b1b親sha不一致でrc=2停止・API追加0)/L4 13:03:56 part2_b1b再finalize(rc=0)/L5 13:09:22 KP TTS(rc=0)/L6 13:15:59 part2_c1 TTS(rc=0)/L7 13:21:47 通し(rc=0)。全起動前に `stop_scope_check_01.py`(rc=0)。rc≠0はいずれも原因判明(引数誤り・来歴親sha不一致=想定内)で、原因不明のrc≠0は0回。

## 6経路Status(KCP)
| 経路 | KCP evidence | 出典 |
|---|---|---|
| X Std/Adv | EVIDENCE | 委任_03 EVIDENCE_X_02 |
| Y Std/Adv | EVIDENCE | 委任_03 EVIDENCE_Y_02 |
| Z Adv | EVIDENCE | 委任_03 EVIDENCE_Z_02 |
| **Z Std** | **EVIDENCE(本委任。実runnerでKP finalize→KP音声のみ再生成→gate〜page_verify通過)** | 本書 |
全6経路で runtime evidence 取得済み。ただし到達上限は EVIDENCE(PRODUCTION_WIRED判定はFable/ユーザー)。

## 限界(隠さず記録)
- 本runのa2は旧run(r3)のFull Story音声(他clip不変)を再利用した「コピーdir上のevidence」であり、Z Std新規記事のend-to-end生成ではない。新規記事では最初から確定→finalize→TTSの順になる(本runでは後から確定を入れたため `--regenerate-stage kp_a2` が必要になった。KCP3 D1と同じ事情で、未確定の新規記事では発生しない)。
- 候補doc形式は phrase4+word4(7+5形式の完全な候補docは無い)。
- 文法a2は候補0(ZERO)。1件採用のZ Std実run観測は無い(Z Advでの観測は委任_03/GPG05)。
