FABLE-DELEGATION-MARKER: PM-GIT-INDEX-HYGIENE-STALE-STAGED-FAMILY-Y-20261023

# Git index衛生(API 0): 他agent由来で共有indexに残っているstaged変更3件の意図を確認し、安全に整理する。

## 対象(`git status --porcelain` で確認)
- `docs/research/FAMILY-Y-VOICES-DESIGN-01/TRIAL_02/ITERATION_LOG_01.md`(MM: staged変更+未staged変更)
- `docs/research/FAMILY-Y-VOICES-DESIGN-01/TRIAL_02/PLAY_VERIFY_02.md`(D: staged削除)
- `er110_output/family_y_persona_trial_01/audio/it2/play_verify.json`(staged削除)

## 手順
1. `git diff --cached --stat` と `git diff --cached -- <各path>` で内容を確認。`git log -3 --format='%h %s' -- <path>` で直近commitを確認。
2. 意図の確認(read-only): `docs/pm/delegation_log/2026-10-23_FAMILY-Y-VOICES-DESIGN-01_委任_0[89]*.md`、`..._委任_1[01]*.md`、`docs/pm/RESULT_PACKET_FYT[5678].md`、`TRIAL_02/TRIAL_02_RESULT_01.md`/`TRIAL_03/*` に、PLAY_VERIFY_02.md や it2/play_verify.json を「削除/移動/改名した」という記録があるかGrep。TRIAL_03配下にPLAY_VERIFY_03/04/05があることは既知(TRIAL_02の記録を置き換える意図かは不明)。
3. 判断ルール:
   - 削除の意図が記録で確認でき、かつHEADの当該ファイルが他文書から参照されていない(Grep)場合: 削除+ITERATION_LOGの変更を、内容確認のうえ `git commit --only -- <3 path>`(message: "FAMILY-Y TRIAL_02: 記録整理(他agentのstaged変更を確認のうえcommit)")で確定し push。
   - 意図が確認できない、または参照が残る場合: `git restore --staged -- <3 path>` でunstageし、削除されたファイルは `git restore -- <path>` で作業ツリーへ復元(HEAD内容)。ITERATION_LOG_01.md は作業ツリーの変更を保持したままunstageのみ(内容は消さない)。その後、ITERATION_LOG_01.md の作業ツリー差分が記録として妥当(Family Y Trial_02の履歴追記)なら、それだけを `git commit --only -- docs/research/FAMILY-Y-VOICES-DESIGN-01/TRIAL_02/ITERATION_LOG_01.md` で commit し push。
4. 結果を `docs/pm/delegation_log/2026-10-23_PM-GIT-INDEX-HYGIENE_委任_01.md`(委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py ...`、MARKER一致)と同ファイル末尾の「実施結果」節に記録し、同commitに含める(別commitでも可)。

## 禁止
`git add -A/-u/-f`、amend、rebase、force push、stash、clean、reset --hard、checkout -f、一時index禁止。上記3 path以外に触らない。内容の編集をしない。完了したら、採った分岐(確定/復元)・根拠・commit hash・最終 `git status --porcelain` のstaged行が0であることを報告。

## 実施結果(2026-10-23)
- 採った分岐: 復元(unstage)。削除の意図を示す記録は委任_08/09/10/11・RESULT_PACKET_FYT5〜8・TRIAL_02_RESULT_01・TRIAL_03配下に無く、RESULT_PACKET_FYT5.md:3,14とTRIAL_02_RESULT_01.md:128がPLAY_VERIFY_02を参照中のため。
- staged ITERATION_LOG_01.mdは旧文面(費用節の簡略版)で、作業ツリーはHEAD内容と同一(差分なし)だったため、unstageのみでcommit対象なし。PLAY_VERIFY_02.mdとit2/play_verify.jsonはHEAD内容を作業ツリーへ復元。
- 最終: staged行0。内容の編集なし。
