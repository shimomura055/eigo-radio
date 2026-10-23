FABLE-DELEGATION-MARKER: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01-委任_17-POSSESSOR-ROLE-REP2-CAP25-20261023

# FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_17: 委任_16(rep2再現性確認)を**上限25円**で実行(Fable判断: 案1採用。実測単価0.28〜0.29円/callに基づく。KP案件累計≈227→≈251円、7-7の300円内)。内容・手順・禁止事項は委任_16の委任文 `docs/pm/delegation_log/2026-10-23_FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01_委任_16.md` のとおり(上限のみ25円へ改定)。

追加指示:
- 開始前に `daily_dev_cost_01` で当日(JST)累計を確認。10-23なら上限1,400円、10-24以降なら1,000円。他案件の進行中予約枠(Family Y Phase B 180円、Family Z『二十年後』100円)を差し引いても25円が収まることを確認して記録。収まらなければSTOPしFableへ。
- 実行: `py er112_kp_gm_trial_04_poss.py run --arms a1_c --reps 2 --cap <見込み>` と `--arms a1r_c --reps 2 --cap <見込み>` を別processで順次(または並列可、cap検査は発行前累計+見込み)→`score`で集計。
- 成果物: `TRIAL_04/POSS_REP2_01.md`(arm×rep、誤り数、role一致、INVALID/REVIEW_REQUIRED、修復発火、非所有格key同一率、rep間一致率、ノイズ基準=C0A rep1 vs rep2、`pumps its fist`型・`close around me`の扱い、所見[VALIDATED候補を支持するか])、`poss_runs/*/rep2/`。
- 委任文逐語保存 `..._委任_17.md`(MARKER一致)。ACTIVE_TASK KP行へ「委任_17 rep2実行(≤25円)」追記(自分の行のみ)。他agent編集中ファイル(`FABLE_BLIND_RESULT_04.md`、`REPORT_FABLE_04.md`、`TRIAL_RESULT_04.md`末尾、OPEN-474)には触れない。
- secret scan 0件→`git diff --cached --name-status`→`git commit --only -- <path…>`→`git push origin HEAD:main`。完了したら主要数値とcommit hashのみ報告。

(注: 委任_16の委任文ファイルはrepo上に存在しなかったため、本委任文本文と既存runnerの仕様に基づき実行。)
