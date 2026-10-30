# INCIDENT 2026-10-30 SUB04 junction越し git restore

## 事実
- SELECTION-UI-BATCH-AND-VOCAB-AUDIO-01 委任_04の別workerが、sparse worktreeから NTFS junction 経由で主作業ツリー(C:\Users\tensh\eigo-radio)の er019_output / er121_output / er026_output を参照し、`git restore --source=HEAD --worktree`(origin/main 0e952617c)で追跡済み約12,439件を21:35:22-49に書換え。その後、主HEAD(6ca3a5055)と内容が異なる22件を `git checkout HEAD --` で主HEAD版へ戻した(古い版)。
- 未commitのローカル変更は検知不能。untracked(??)ファイルはrestoreの対象外のため無傷。

## 影響調査(2026-10-30 本件の調査)
- 現在junctionは主・wt_n5・wt_sub・ejh03b・ejhpushのいずれにも無い(fsutil reparsepoint: 非reparse)。21:50以降の主ツリー3dirへの書込なし。
- 主ツリーの3dirの追跡済みファイルは全てHEAD版に一致(CRLF無視、diff HEAD=0)。origin/main(72fc4d936)との差分は202件: M 22(主HEAD旧版へ退行) / A 180のうち174は主ツリーにuntrackedで存在しorigin版と同一(無傷)、6は主ツリーに無い。
- 03B(ENDUSER-EN-JA-LINKED-HIGHLIGHT-01 委任_03B)の成果(vocab_audio.json・mp3・tts_generation_results・review_lock_state・raw_usage_log・cost_log)は別worktree(ejh03b)で作成されbcddcf0c3としてorigin/mainにcommit済み。主ツリーの未commit成果ではなかった。Y姓/Z雪女/⑭のvocab_audio、Z雪女cost_log(37行、全worktree一致)は欠落なし。
- 退行していた22件: er019 FX4各run(ai_chat・meta_waddle⑨・moon・untidiness)のa2/b1b audit/tts_generation_results.json・review_lock_state.json・raw_usage_log.jsonl・meta a2 run_summary_assemble.json・meta entry_point.json、er121 redelivery_fee/run_style_fix_01/b1b tts_generation_results.json、surname_choice/run_02/cost_log.jsonl。⑨は承認前の古いSTOPPED状態に退行していた。
- 主ツリー内に無かった6件(⑨ b1b: fx4h_user_approval_record_kpv3_vocab_extra_english.json、human_approved_segments.json、review_lock_state.pre_fx4h_adopt_backup.json、tts_generation_results.pre_fx4h_adopt_backup.json、vocab_b1b_3.mp3、enduser_sync_cache/ja_generated.json)。主ツリーはorigin最新(85commit)に未追従だったため元から無かった可能性が高い。

## 復旧
- 上記22+6=28件を `git checkout origin/main -- <path>` で復元(index非ステージ、sha一致28/28確認)。API/TTS/ASR 0。
- 復元不能: 事故時点の主ツリーにのみ存在した「追跡済みファイルへの未commit変更」(HEADと内容が異なる状態)は事故で検知不能。調査上、03B/⑨/FX4/ECH/KPN5の各packetが示す成果は全てorigin/mainにあり、欠落を示す証拠なし。公開物(user_test/*)への影響なし(3dir以外は無変更)。監査記録の欠落も確認されず。

## 防止策(案)
1. junction/symlinkで主ツリーのer*_output等をsparse worktreeへ接続しない。
2. `git restore --source=... -- .` や広いpathspecのrestore/checkoutを主ツリーに対して実行しない。必要なら対象pathを列挙し、実行前に `git status --porcelain` を保存して差分を取る。
3. sparse worktree運用: worktreeは独立checkoutし、成果は当該worktreeでcommit→origin/main経由で主ツリーへ取り込む。主ツリーのパスを直接書換えない。
4. 主ツリーは長期遅延するため、作業前に `git fetch` と主HEADとorigin/mainの距離を確認する。
