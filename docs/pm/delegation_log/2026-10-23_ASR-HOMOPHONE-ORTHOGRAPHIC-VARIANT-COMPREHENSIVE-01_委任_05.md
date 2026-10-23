FABLE-DELEGATION-MARKER: ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01-委任_05-20261023

# 委任_05: er109配線の補完(Z正式TTS段のruntime evidence・`three↔3:00`型の是正)とFable受入Closeout

## T-0
1. 委任文逐語保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-23_ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01_委任_05.md`(N≈319〜329、先頭行MARKER一致確認)。
2. `docs/pm/ACTIVE_TASK.md`: 別agent(FAMILY-Z-STD-DIALOGUE-SPEED-AB-TRIAL-01)が並行中。編集直前に再読込し、OPEN-459行だけ更新。有料run直前に「有料run進行中(時刻)」、終了後「有料run終了(時刻)」。

## 1. Fable判断(委任_04報告の受入評価)
- X ①: 正式経路(runner a2/b1b、scope=X)の実行+本番adapterでの実Azure呼出により `Pump 1's fist`→`ORTHOGRAPHIC_EQUIVALENT_MATCH` PASS、HR Lock済みattempt 2件→PASS_WITH_WARNING(S+W)、誤転写は NG_BOTH維持、保存43,033署名でPASS→NG 0。**受入可**。
- X ②(`no↔know`): 配線点は①と同一で、決定的検証はtestで確認済み。実音声発火は未観測。**受入可(未観測を開示)**。発火目的の記事生成はしない。
- Z ①②: 保存wavのscope内再判定とKP段は確認済みだが、**Z runnerの正式TTS段(`run_tts_stage`=scope入口)が配線後に一度も実行されていない**(restart storm sentinelで停止)。これを補完するまで受入保留。
- 是正が必要な点(承認済み安全条件「発音が異なる表現を同値にしない」に反する可能性): 報告された `three↔3:00` が既存ルール`number_spoken_form`でPASSし得る件。音声が「three o'clock」で正解が`three`なら発音が異なるため同値にしてはならない。**承認範囲内の不具合是正として自律修正**する(新仕様ではない)。

## 2. 作業
### A. `three↔3:00`型の是正(er109内、fail-closed)
1. `er109_asr_orthographic_equivalence_01.py`の`number_spoken_form`(および類似の時刻・通貨・単位を含む表記規則)で、コロン付き時刻形式(`3:00`、`3:15`)、`o'clock`、`a.m./p.m.`等の**発話に追加語を伴う表記**は、相手側にも対応する語(`o'clock`/`fifteen`等)が存在する場合にのみ同値とし、裸の数詞(`three`)とは同値にしない。曖昧なら非同値(fail-closed)。
2. 負例test追加(`three`↔`3:00` NG、`three o'clock`↔`3:00` PASS[既存挙動が許す範囲]、`three fifteen`↔`3:15`、`3`↔`3:00` NG)。`pairs_02`等の既存評価データで、この是正によりPASS→NGとなる組を列挙(件数・内容)。保存43,033署名の再比較でPASS→NGが出た場合は、その行の音声/転写を確認し「誤PASSだった(是正が正しい)」か「正当なPASS」かを判定して報告(正当なPASSを壊す場合は是正方法を狭める)。
3. VALIDATION_02の「B/C境界(時刻・セント)3件」との整合を確認し、関連記述を更新。

### B. Z正式TTS段のruntime evidence(Fable明示許可1回)
1. run `er026_output/family_z_production_e2e_01/melos/run_aho4_z_h3` のSTOP(restart storm由来)を、`--clear-stop --reason "FABLE-AUTH 委任_05: restart storm was caused by agent launch errors (missing prerequisites), cause identified, one additional launch authorized by Fable"` で解除(PM_GOVERNANCE 26-5、Fable権限。`audit_stop_sentinel.jsonl`に記録されることを確認)。STOP_ALLやSTOP NOTICEが無いことを確認(rc=0)。
2. **別agent(速度A/B Trial)が有料TTSを実行中でないことを確認**(`Get-Process python`のcommand line、ACTIVE_TASKの該当行)。実行中なら終了まで待機(5分間隔・最大30分)。
3. `--stage tts_b1b`(KP 3clipのみ、既存条件: `TTS_EXECUTION_MODE=STANDARD`、`--approved-budget-jpy`既定)を**1回だけ**起動。再びrc≠0なら再起動せず報告。見込み≈3〜4円。
4. 証拠: Z runnerのTTS段でscope=Zが有効(`is_active_for_run()`/vote auditの`ortho_scope=Z`、`ortho_layer_version`)、KP3V票の判定記録、Store再利用時のguard記録、PASS→NGなし、HR/STOP状態。表記差の自然発火は未観測なら「未観測」と明記。
5. melos受入済みpage・成果物は無変更。

### C. 回帰・SSOT・Closeout(A・Bがクリーンな場合)
1. 新規/更新test全PASS、`run_project_regression.py`単独実行で failed 0/errors 0、pytest系別枠PASS、署名比較の再実行(no-scope/rollbackバイト一致、X/Z ONでPASS→NG 0[Aの是正で正当化されたNGを除き、その場合は一覧を添付])。
2. Fable受入判定をSSOTへ反映: OPEN-459=**PRODUCTION_WIRED(Family X/Z、①②別、Fable受入2026-10-23)**。開示事項: X ②実音声未観測/Z ①②の表記差自然発火未観測/本文でのortho発火未観測/J-2(B不具合修正のA/B/C波及は10-22承認済み是正・現状維持)/rollback時のStore再生成費用性質/`three↔3:00`是正。CURRENT_SPEC Status行、DECISION_LOG受入エントリ、OF-AHO-W-M01〜M13・P-06/10/11の最終Status、USER_DECISION_REGISTER #156へ配線完了追記、REPORT_LEDGER。
3. A/Bのいずれかがクリーンでない場合は`WIRED_PENDING_FABLE`のまま理由を書いて報告(自分で格上げしない)。
4. commitは論理単位(是正+test / Z evidence / SSOT)、明示add、secret_scan `--staged` hits=0、`git push origin HEAD:main`。共有SSOTは編集直前`git status`→自分の行のみ→即commit。

## 3. 禁止
- A/B/Cファイルの編集、`--scope`の追加、Lock/STOPの直接編集(正規`--clear-stop`以外)、有料runの2回目起動、発火目的の記事生成、Production受入済み成果物の変更。

## 4. 報告(docs/pm/RESULT_PACKET_AHO5.md、同内容を最終報告で)
(1)`three↔3:00`是正の内容・影響(PASS→NG一覧と判定) (2)Z TTS段runtime evidence要約(観測/未観測) (3)テスト・回帰・署名比較数値 (4)費用(出典、委任_04の約3.1円との合計) (5)SSOT反映結果(OPEN-459最終Status) (6)commit・raw URL (7)残件 + RESULT_PACKET 4行 + 「判定整合: 重大NG=あり/なし」。