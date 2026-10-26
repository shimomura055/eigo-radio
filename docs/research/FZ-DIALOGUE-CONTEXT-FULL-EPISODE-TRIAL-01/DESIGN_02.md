# DESIGN_02 — DESIGN_01 へのOpus条件Aレビュー(M-1〜M-8 / R-1〜R-9)反映差分

管理ID: FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01 / 委任_02(2026-10-26)。性質: Trial(DEV専用)。DESIGN_01は骨格(Production関数をimportしてTrial専用dirで実行 + 生成前の自己検証 + sink差替え)として維持し、本書は差分のみ。
実装: `er118_fz_full_episode_trial_01.py`(§4-1〜4-10)、test: `er118_fz_full_episode_trial_01_test_01.py`。レビュー原文: `OPUS_REVIEW_01.md`(無改変転記)。

## 0. Fable判断(委任文より、生成前に固定)

- M-1〜M-8: **全て採用**。M-8のNG clip方針: NG音声は採用しない。通し版の該当箇所はProduction原音を置き、ページ・チャプターに「この箇所は現行音声(Trial生成NG)」と明示。**NG≦2 clip(53中)ならC1は記録付き成立としてユーザー試聴へ、3 clip以上ならREJECTED候補(方式不安定)としてFableへ報告(ページは作る)**。
- M-7: C2のblockingは Production ASRカスケード最終判定PASS系 + repetition QA済み。`token_equal`/`similarity`は観測値。C3 flagged時はFable聴取確認の手順を事前登録(PREREGISTERED_CRITERIA_02 §2)。
- R-3(TEXT同一性)で差分が見つかった場合: 発音供給ヒントのみ(綴り同一)なら現行scopeのTTS入力を使い交絡として明記して継続 / 語自体が違えばSTOP。→ **結果: 差分なし**(§3 R-3)。
- R-9: scope=Phase 1b・上限100円のGOを別に設ける(`_require_go(scope, max_cap)`、Phase 1aの5円と混ぜない)。**Std会話へのctx付与は今回が初めて**(Round 1/2はAdvのみ)であることを試行リスクとして明記。
- M-5の3点assert不一致はSTOP(Production汚染ではなく比較条件崩れとして報告)。

## 1. 必須修正(M)の反映

| ID | 反映内容(実装位置) | 検証 |
|---|---|---|
| M-1 | 生成はclipごとの別dir `…/<work>/<lv>/gen/<cid>/<lv>/narration/<cid>.wav`(`gen_wav_path`)。`adopt_decision`(status OK + repetition QA + comparison_valid + leakage保留なし)を満たすclipだけを `build_run_dir(adopted=…)` が `trial_run_dir` へ copy。組立前に dialogue wav の sha == result.json の `wav_sha256` == entry.sha256 を assert(`assemble_case`) | test `test_adopted_only_and_sha_assert` |
| M-2 | `build_run_dir` が採用clipのProduction `<cid>.wav`/`<cid>_original.wav` を除去し、Advは生成で新しく作られた `_original` のみ置く | test `test_original_wav_not_production` |
| M-3 | dialogue entryは `a63.build_entry(spec, trial_out_path, result)`(`gen_case`)+ `trial_style_sha256`/`trial_reuse_key` を付加。非dialogue entryの `path`/`narration_path`/`original_path` を `_rewrite_paths` で trial_run_dir に書換え。`human_approved_segments.json` と `key_phrases/` をcopy。`verify_isolation` で結果の全pathがOUT_ROOT配下であることを確認 | test `test_results_paths_under_out_root` |
| M-4 | (a) `assert_out_root`/`assert_writable` は `os.path.realpath`+`commonpath`(prefix比較でない)。run_assembly/生成/review_lockの呼出前に run_dir・out_path に適用 (b) `safe_copy` は `shutil.copyfile` のみ、dstがsymlink/nlink>1ならSTOP、copy後 `samefile` を検査、`verify_isolation` が全ファイルのhardlink/同一ファイルを検査 (c) `a63.build_pages` は呼ばず、`mp3_from_wav` が `sf.write(..., format="MP3")` をPAGE_ROOT配下へ直接書く (d) `scan_repo_mtime` は OUT_ROOT/PAGE_ROOT を除外に入れた版(Round 1のdirではない) | test `test_realpath_guard`, `test_safe_copy_*` |
| M-5 | `compare_to_production(identical=False)` が target_rms一致 / dialogue以外の全labelのgain一致 / headroom.scalar一致 / `story_clips[0]`が非dialogue を判定。`assemble_case` は不一致でSTOP | test `test_m5_*`、4単位の自己検証 |
| M-6 | 本moduleが呼ぶ `t.*` は純関数の許可list(`extract_context/build_context_block/style_for_arm/build_prompt/leakage_*/comparison_validity/analyze_wav/est_tts_jpy/capture_tts_requests/validate_emotion_items/load_reviewed_notes[path明示]/sha_*/save系/read_mono/f0_stats` 等)のみ。`generate_arm/snapshot_protected/protected_paths/est_next_clip_jpy/trial_reuse_key/_require_go/_stop_check/scan_repo_mtime` は呼ばず、`gen_case/prod_snapshot/est_next_clip_jpy/trial_reuse_key/_require_go/_stop_check/scan_repo_mtime` を本module側に再実装 | test `test_no_forbidden_round2_calls`(monkeypatchで例外化して gen/assemble が通る) |
| M-7 | `adopt_decision` と PREREGISTERED_CRITERIA_02 §1(C2)・§2(C3 flagged手順)。`verbatim_check` は `verbatim_observation` として全件記録するだけ | test `test_adopt_decision_*` |
| M-8 | PREREGISTERED_CRITERIA_02 §3(NG≦2)。ページ/チャプターに「この箇所は現行音声(Trial生成NG)」。Production原音は `build_run_dir` が残す | test `test_ng_clip_uses_production_audio` |

## 2. 推奨(R)の反映

| ID | 反映 |
|---|---|
| R-1 | `prod_snapshot`: 2作品のProduction run dir全体・公開page dir全体を**全ファイルsha**(tree-hash)、共有storeは `t113.snapshot_protected`(`<lv>/audit/review_lock_state.json` は run dir 全体に含まれる、`er011_output/local_rewrite_recovery`はPROTECTED_TREES)。共有store差分は `store_contamination` で本Trial出力先のmarkerの有無により『本Trial由来(汚染)』『他agent由来』に帰属。生成中は他のProduction runを起動しない |
| R-2 | **実測済み**(§3)。Adv外側ループは sink差替え + `family_scope("Z")` + `with_secondary_run` の内側(`gen_case`、`dryrun_sinks`) |
| R-3 | **実測済み**(§3)。`text_identity_case` |
| R-4 | `selfcheck_case`: 公開mp3長と再組立wavの長さ差、gain_report/headroom dict一致。Production版試聴mp3は再組立wavを Trial と同じ `mp3_from_wav` でmp3化 |
| R-5 | Adv外側ループ採用(Production Advと同じ)。Round 2との再生成率比較は条件が違うと報告に明記 |
| R-6 | 費用は `raw_usage_log.jsonl`(provider別)を正とする。clip別は累積の差分(`cost_jpy_clip`)。Δ/set幅(k_prod版 / Round 2 base版)。感情レビュー自動化費用は『未計上(要設計)』 |
| R-7 | `noise_band_r2.json` を生成前に作成(sha256は PREREGISTERED_CRITERIA_02 §4)。N1両側併記、N2/N3は同段階で測定 |
| R-8 | `use_case` 再入禁止assert + finally復元。voice map一致test |
| R-9 | `_require_go(scope, max_cap)`: Phase 1a=5円 / Phase 1b=100円を分離 |

## 3. 生成前の実測結果(API 0、実行は本委任)

- **自己検証(M-5/C5(i)/R-4)**: 4単位とも Production原clipで再組立 → Production組立wavと**サンプル完全一致**(wav_max_abs_diff=0.0、timeline part列・gain_report・headroom dict一致)、C6 Gate PASS、公開mp3長差0.0秒。`er118_output/fz_full_episode_trial_01/<work>/<lv>/selfcheck.json`。
- **R-2 dry-run**(`dryrun_sinks.json`、netblock harness下で接続試行0): 猿の手 Adv の外側ループ(gen_fn・ASRをstub、3回NG)で、(1) `append_attempt_history_event` → `sinks_dryrun/sink_er011_…ATTEMPT_HISTORY_PATH.jsonl`(OUT_ROOT配下) (2) `finalize→record_outcome` → `dryrun/<cid>/<lv>/audit/review_lock_state.json`(OUT_ROOT配下、state=HUMAN_REVIEW_REQUIRED) (3) `_log_human_review` → `sinks_dryrun/sink_er006_…HUMAN_REVIEW_LOG_PATH.jsonl`(OUT_ROOT配下)。**(3)は外側ループ内では発火しなかった**(Secondary cascadeを無効化したdry-runのため `detail.human_review_required` が立たない)ので、同じredirect下で同関数を直接1回プローブして書込先を実測。Production run dir・公開page・共有store全て差分0、Z mtimeヒット0。
- **R-3 TEXT同一性**(`text_identity.json`): 53 clipすべてで `a63._norm_for_tts`(Production関数)と `t.tts_text_for` が一致。発音供給(PNAP)の効果が掛かるclipは**0件**(scope内=scope外)。数字表記変換(three→3 等)は既存の `tts_safe_news_en` による通常の整形で、Productionと同一関数。**差分なし → R-3分岐は発動せず**。残る限界: Productionの実送信入力は未保存のため『現行ledger/コードでの再現値』との比較で、メロス2 clip(`full_story_part1_c4`、両レベル)はProduction側が前run再利用(`reused_from_previous_run`)なので、再利用元の生成時入力が現行と同一である保証はない(交絡として報告)。

## 4. 実行順序(委任_02、依存と並列)

1. 本書+事前登録02+OPUS_REVIEW_01+コード+test+noise_band を**生成前にcommit**(時刻固定)。
2. 起動前: daily cost / STOP確認 / `PHASE1_GO.json`(Phase 1b・100円・approved_by=Fable(委任_02、ユーザー2026-10-26全編Trial承認))。
3. 生成4単位を直列(猿の手 Std → Adv → メロス Std → Adv)、起動間隔≥150秒。生成待ちの間に解析script・ページbuilderを準備。
4. 組立(API 0)→ 解析 → ページ → 評価。
