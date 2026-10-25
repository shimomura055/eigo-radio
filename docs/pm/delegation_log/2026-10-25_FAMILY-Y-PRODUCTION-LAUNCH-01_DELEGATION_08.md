# 委任_08｜FAMILY-Y-PRODUCTION-LAUNCH-01 E-1 a2 `y_voice_1` 減速版の正式ASR再検証(Gate代替の撤回)

## 背景(Fableから)
委任_07(commit `9247c34b8`、`docs/pm/RESULT_PACKET_YPL7.md`・`docs/research/FAMILY-Y-PRODUCTION-LAUNCH-01/E1_HUMAN_REVIEW_01.md`)は、a2 `y_voice_1` の採用候補(attempt5、`NORMALIZED_MATCH`)に採用時必須の6%減速を掛けた音を試聴用に用意し、減速後のASR再検証を「ユーザー試聴承認で代替」(`er121_e1_hr_adopt_r0_01.py:123` に `post_slowdown_asr_recheck="NOT_RUN: …"`)とした。
**Fable判断: この代替は認めない。** 既存の正式経路(例: `er063_family_z_audio_01.py:1302` の `asr_recheck="unified_judge(apply_a2_slowdown_postprocess)"`)では減速後にASR再検証を行う。Human試聴承認はD'(反復検査)境界のNGに対する承認であり、減速後ASR再検証の省略を正当化しない。正式経路どおり再検証を行い、結果を記録する。

## やること
1. Y a2 の正式経路で減速後ASR再検証がどこで行われるか(`er121_family_y_audio_01.py` と共通核 `apply_a2_slowdown_postprocess`/unified_judge)を確認し、E-1 `er121_output/family_y_production_01/redelivery_fee/run_01/` の a2 `y_voice_1` attempt5 の減速版(試聴ページに置いた `a2_y_voice_1_slowed6pct.mp3` の元wav。無ければ同じ手順で生成し sha256 を記録)に対して、**同じ関数・同じ判定設定**でASR再検証を実行する(有料、見積1円未満、上限3円)。有料run=`.venv\Scripts\python.exe`。起動前: `py tools/stop_scope_check_01.py --managed-id FAMILY-Y-PRODUCTION-LAUNCH-01 --run-dir er121_output/family_y_production_01/redelivery_fee/run_01 --out er121_output/family_y_production_01/redelivery_fee/run_01/stop_check_ypl8.json`(rc=3なら停止)、`py docs/pm/tools/daily_dev_cost_01.py` 表示値+94.28円が1,480円未満であること。起動は1回。
2. 結果(判定・label・転写・model_id・費用・wav sha256)を `E1_HUMAN_REVIEW_01.md` に追記し、`er121_e1_hr_adopt_r0_01.py` の `post_slowdown_asr_recheck` を「実測結果の参照(ファイルpath+判定)」に置き換える。再検証がPASS(ASR一致)でない場合は、`--apply` が a2 `y_voice_1` を採用できないよう(rc=2)にする。NOT_RUN代替の分岐は撤去。testを更新(PASS時採用可/非PASS時rc=2)。
3. 試聴ページ `user_test/family_y_production_redelivery_fee_01/listening/index.html` の a2 `y_voice_1` 欄に、減速後ASR再検証の結果を1行追記(試聴mp3は差し替えない。sha一致を確認)。
4. 再検証の記録はrun_01の判定ファイルを改変せず、別ファイル(例 `run_01/a2/hr_adopt_prep/y_voice_1_slowed_asr_recheck.json`)に置く。wavは追跡しない。
5. Git: 対象pathのみ `git commit --only` → `git push origin HEAD:main`(non-fast-forwardなら fetch→`git merge --no-edit origin/main`→push、競合は両方残しSTOP)。禁止=`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・`git checkout -- <file>`。secret grep 0件。他agent(KP HR evidence: er019/er026/er062/er119/er120系; JA ASR 委任_11: JA-ASR docs)のファイルは触らない。
6. 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-25_FAMILY-Y-PRODUCTION-LAUNCH-01_DELEGATION_08.md`(直近既知index=602付近。603以降を試し、先頭行が「# 委任_08｜FAMILY-Y-PRODUCTION-LAUNCH-01」のものだけ採用)。

## 報告(`docs/pm/RESULT_PACKET_YPL8.md`+最終報告)
再検証結果(判定/転写/model_id/費用)、adoptスクリプトの変更、test結果、commit sha、raw URL、Y累計(166.85+本委任)/200円、日次実累計、RESULT_PACKET 4行+判定整合行。`approved_by="user"` は付けない。