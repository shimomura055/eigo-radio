FABLE-DELEGATION-MARKER: FAMILY-Z-VOICE-PRODUCTION-WIRING-01-委任_02-20261023

# 委任_02: 『開いた窓』run_e2e_01 の再開(Fable明示許可1回)→QA→assemble→Pages公開→受入資料

## 0. T-0
1. 委任文逐語保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-23_FAMILY-Z-VOICE-PRODUCTION-WIRING-01_委任_02.md`(Nは約312〜322、先頭行MARKER一致を確認)。
2. `check_delegation_prompt.py`結果はRESULT_PACKETに記録(FAILでもブロックしない)。
3. `docs/pm/ACTIVE_TASK.md`: 別agent(ASR-HOMOPHONE 委任_04、er109配線)が並行中で同ファイルを更新する。編集直前に再読込し、FZVW行(管理ID行〜QDC行)だけを更新。**有料run開始直前にFZVW行へ「有料run進行中(開始時刻)」を明記し、終了後に「有料run終了(時刻)」へ更新する**(別agentはこの行を見てProduction .pyの本線反映とZ runtime runを待機する)。

## 1. Fable判断(委任_01の報告に対する受入)
- **Validator是正(commit 79e9b4310)は承認**: 承認済み規則(数値語→数字変換)の不具合是正。`and`を hundred/thousand/million 直後のみ数値語列とする修正で、保存12,506件の前後比較がPASS→NG 0・NG→PASS 0(A/B/C含め挙動変化0の実測)。先例d9e36f54aと同じ11-8不具合是正の扱い。巻き戻せば本件HR Lockが再発するため現状維持。SSOT(CURRENT_SPEC不具合修正追記、DECISION_LOG、OPEN_ITEMS該当行)に「不具合是正・全Family共有・保存データ挙動変化0」を事実として記載すること(A/B/Cへの展開提案ではない)。
- **HR Lock(a2 full_story_part1_c10、Vera/Zephyr)の解消はFable明示権限で許可**: 根拠=3回ともOpenAI/Azureの転写が原文と完全一致しており、Lockの原因は上記Validator不具合(音声品質の問題ではない)。**既存のHR Lock解除操作(`er011_human_review_lock_01.approve_regenerate` 相当の正規CLI/関数)で、`approved_by="fable:FZVW-02:validator_fix_79e9b4310"`を記録して解除**する。Lockファイルの直接編集・人工entry・Gate迂回は禁止。解除操作の証跡(lock recordの前後、`audit`記録)を保存。
- **有料runの再開を1回だけ明示許可**(PM_GOVERNANCE 26-2(c))。コマンド: `python er026_family_z_fiction_production_runner_01.py --story the_open_window --run run_e2e_01 --mode real --stage all --approved-budget-jpy 300 --warn-threshold-jpy 200 --tts-execution-mode STANDARD`(完了clipは再利用、c10のみ再生成の見込み)。再開前に`docs/pm/delegation_log/*STOP_NOTICE*`・`<run>/STOP`・`er026_output/family_z_production_e2e_01/STOP_ALL`の不在確認(rc=0)。再開後に再びrc≠0で止まった場合は**再起動せず**、原因・証拠・選択肢を報告して終了。
- 費用: 本委任分の見込み約2〜5円(c10再生成+QA)。累計(委任_01分52.45円+本委任)が300円以内であることを確認。本日累計は約52.5円/1,000円。

## 2. 直列化(重要)
- 再開前に、別agentのZ runtime run(melos、`er026_output/family_z_production_e2e_01/melos/run_aho*`等)やX run(`er019_output/family_x_audio_production_wiring_01/*aho*`)が走っていないことを`Get-Process python`のcommand lineで確認する(走っていれば終了まで待機、5分間隔、最大30分)。
- 走行中は他runを起動しない。終了後にACTIVE_TASKのFZVW行を「有料run終了」に更新。

## 3. 範囲(やること)
1. HR Lock解除(上記の正規操作)→run再開(1回)→tts_a2完了→gate→assemble→Pages生成。
2. Pages: 新ディレクトリ `user_test/family_z_open_window_01/`(`family_z_melos_02`・`family_z_melos_jre_01`は上書き禁止)。commit/push後にHTTP 200・Playwright実再生検証(全audio)・既存の`user_test_page_standard_check_01`相当の検査。
3. 発音アラーム「frampton」5箇所(Framton Nuttel): PNAP仕様どおり「アラーム付き完成」として扱い、`operator_alarm_report.md`等の既存出力を確認して報告(新規判断は求めない。ASR転記が`frampton/crampton`になるのは既知の固有名詞型で、Ledger登録済みかどうかを確認して記載)。
4. 受入資料: `docs/research/FAMILY-Z-VOICE-PRODUCTION-WIRING-01/RUNTIME_EVIDENCE_01.md`(Voice割当=voice_assignment.json・speaker_table、各Voiceのclip数、QA結果、HR Lock解消の証跡、Pages URL+再生検証、費用出典、メロス整合確認の差分表と再生成見積[委任_01の(7)を転記]、Validator是正の前後比較)。
5. SSOT: OPEN-430/428のStatus候補を`WIRED_PENDING_FABLE`(Fable受入後にPRODUCTION_WIREDへ)、CURRENT_SPEC Family Z Voice項に『開いた窓』割当・run・Pagesを追記、DECISION_LOG(HR Lock解消のFable判断・Validator是正承認)、REPORT_LEDGER。commitは論理単位、明示add、`git push origin HEAD:main`、secret_scan `--staged` hits=0。`er006_output/master_audio_store_01/manifest.json`・`reuse_telemetry.jsonl`は他変更が混在しているためstageしない(従来どおり)。
6. 共有SSOTファイルは編集直前`git status`→自分の行のみ→即commit(index.lockは30秒待機)。

## 4. 禁止
- 有料runの2回目以降の起動、別名ラッパ・監督ループ、STOP/HR Lock迂回、Lockファイル直接編集、人工entry。
- melos音声・受入済みpageの変更。新Voice Trial・仕様変更。Validator等の追加Production修正(新たな不具合を見つけた場合は修正せず報告)。

## 5. 報告(docs/pm/RESULT_PACKET_FZVW2.md、同内容を最終報告で)
(1)Status候補 (2)HR Lock解消の操作と証跡 (3)run再開結果(再生成clip数、QA、gate、assemble) (4)Pages URL+再生検証数値 (5)発音アラーム(frampton)の扱い (6)費用(出典、委任_01+_02合計) (7)commit・raw URL・SSOT (8)未解決・残件 + RESULT_PACKET 4行 + 「判定整合: 重大NG=あり/なし」。