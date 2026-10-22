FABLE-DELEGATION-MARKER: FAMILY-Z-VOICE-PRODUCTION-WIRING-01-CLOSEOUT-委任_03-20261023

# 委任_03(小): Family Z Voice配線のFable受入(PRODUCTION_WIRED)をSSOTへ反映(費用0・Production変更なし)

## T-0
- 委任文逐語保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-23_FAMILY-Z-VOICE-PRODUCTION-WIRING-01_委任_03.md`(N≈313〜323、先頭行MARKER一致確認)。
- 別agent(ASR-HOMOPHONE 委任_04)が並行してSSOTを編集中。各ファイルは編集直前に`git status`→再Grep→自分の行のみ編集→即`git add <file>`+commit(index.lockは30秒待機)。`docs/pm/ACTIVE_TASK.md`はFZVW行だけ更新。

## Fable受入判定(2026-10-23、そのまま記録する)
FAMILY-Z-VOICE-PRODUCTION-WIRING-01: **PRODUCTION_WIRED(Family Z)**。根拠=受入条件7項目を照合: (1)正式Voice表`FAMILY_Z_DIALOGUE_VOICE_POOL`・割当関数`assign_dialogue_voices`・`STORY_VOICE_ROSTER`・`voice_assignment.json`(commit 654bc9fe3) (2)『開いた窓』A2 47clip/B1B 46clip全OK、shared_gate PASS、Pages `user_test/family_z_open_window_01/` 公開・公開側実再生 index36/36・standard55/55・advanced53/53・console error 0 (3)新規test 14+5、全回帰 collected 6,901/passed 6,891/failed 0/errors 0 (4)Store keyに`speaker_voice`、旧Voice(Erinome/Charon)dialogue clip 0 (5)メロス整合: pin維持・成果物無変更、差分(dionysius→Schedar、selinuntius→Fenrir、再生成11clip・約3〜6円)を記録 (6)SSOT・commit 654bc9fe3/79e9b4310/bdf25b42f/beabf61b7/b7b6d07d8 push済み (7)費用 約53.26円(出典 cost_log.jsonl)、300円以内。
付随事項(事実として記録、提案ではない): Validator是正79e9b4310(数値語変換が接続詞`and`を巻き込む不具合、全Family共有、保存12,506件で挙動変化0)はFable承認済み(11-8不具合是正)。HR Lock(a2 full_story_part1_c10)はFable明示権限で正規操作`approve_regenerate`により解除(転写3回完全一致・Validator不具合起因)。『開いた窓』の発音アラーム「Framton」(A2 5/B1B 8箇所)はPNAP仕様の「アラーム付き完成」、Ledger未登録(事後試聴・必要ならユーザー判断で登録、現時点で判断は求めない)。

## 作業
1. OPEN_ITEMS: OPEN-430・OPEN-428のStatusを`PRODUCTION_WIRED(Family Z、Fable受入2026-10-23)`へ(履歴は残す)。『開いた窓』が`USER_LISTENING_PENDING`(ユーザー試聴待ち)であることを明記。
2. DECISION_LOG: Fable受入エントリ1件。
3. CURRENT_SPEC: Family Z Voice項のStatus行をPRODUCTION_WIREDへ。
4. USER_DECISION_REGISTER: #129/#131の判断済み行に「配線完了(PRODUCTION_WIRED)」を追記。『開いた窓』試聴PASS/NGを新規の未回答項目として登録(URL付き)。
5. REPORT_LEDGER 1行、ACTIVE_TASK FZVW行をCLOSED(試聴待ち)へ。
6. commit(明示add、secret_scan `--staged` hits=0)、`git push origin HEAD:main`。
7. 報告: 変更ファイルとraw URL、commit hash、「判定整合: 重大NG=あり/なし」。