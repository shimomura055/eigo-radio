# 委任_06: AUW(ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01)— 15必須受入条件のevidence対応表と、実音声runtime evidenceの取得

場所: `C:\Users\tensh\eigo-radio`、branch `feat/auw-unified-asr-01`(HEAD 2ac5899e9)。main禁止(委任_07)。禁止git操作: `add -A`/`-f`/`stash`/`reset --hard`/`checkout -f`/`clean`/`rebase`/`amend`/`force push`。**費用上限: 本委任の有料API合計 JPY 50**(TTS/ASR/Azure実呼出。超過見込みが出た時点で実行を止め報告。1呼出ごとに`raw_usage_log`/cost loggerへ記録されることを事前確認し、記録されない経路は実行しない)。test実行は通信遮断plugin付き、**実音声evidenceの実行だけ**遮断を外した専用コマンドで行い、両者を混ぜない。

## T-0
委任文を`docs/pm/delegation_log/2026-10-16_ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01_06.md`へ保存、checker→`_check.json`(FAILでも継続)。stop_scope_check rc=0。

## 事前指定参照
- ユーザー原文(`..._01.md`): 15必須受入条件、L112-117 Regression基準、L97、STOP条件。
- IMPLEMENTATION_02b/03/04/05.md(03 §9-4 API-0再現 Melos 26/27・M1 20/21、差分`Melos_said_L2_adv_t1_raw__segNone`、05: KP3回化増分)。
- 既存evidence: er077_output、er026_output/family_z_production_e2e_01/melos、er019_output/family_x_audio_production_wiring_01、er011_output/attempt_history.jsonl、er006_output/master_audio_store_01、er025_output telemetry。「12/12」出典はGrep特定。
- HR Lock: er011_human_review_lock_01(迂回・解除しない)。

## やること
A. 受入条件対応表(15条件、既存evidence/本委任実音声/未充足に分類。test PASSだけで充足と書かない)。
B. EN回帰(実音声): er077のMelos said clip集合に新adapterで実Primary→必要なら実Secondary(Azure)。Melos said verified数/M1受理数/誤受理0/PASS_WITH_WARNING件数/Secondary呼出数・重複0/費用。12/12構成特定できれば同構成で一致を示す。27/27・21/21に届かない場合clip単位理由。
C. JA(実音声): 既存JA run(coffee_prices等)の数値含むsegmentで実Primary→NGなら実Secondary再判定を1 run。値ガード挙動(EQUAL/DIFF/AMBIGUOUS)記録。誤受理0。
D. PASS_WITH_WARNING→試聴リスト(実音声): audit/pass_with_warning_listening_list.jsonとページ節に載ることを実run出力で示す。
E. A2減速後判定・Dialogue・KP3回: 実音声で各1件、asr_judgement書込・重複呼出0・Secondary障害時NG_SECONDARY_UNAVAILABLE(mock障害可)。KP3回目はmock evidenceのみと正直に記載。
F. 費用試算(attempt_history.jsonlから。KP3回化・JA UNCERTAIN再生成増分、Secondary 4→1削減分併記、15-9の70円目標)。
G. 静的監査最終snapshot(phase post_wiring、deferred 0、pending 0)。
H. RUNTIME_EVIDENCE_06.md(er058_output/unified_all_roles_production_wiring_01/)+evidence群を明示add→secret_scan --staged hits=0→commit→push(branch)。message: `ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01 委任_06: 15受入条件対応表+実音声runtime evidence(EN Melos回帰/JA値ガード/PASS_WITH_WARNING試聴リスト/A2・Dialogue・KP)+費用試算。main無変更、JPY <実額>`。

## STOP条件
重大誤PASS(数値・否定差の採用)1件でも/誤受理>0/HR Lock抵触/費用JPY50超過見込み/品質悪化。

## 報告様式(受入記録5項目)
(1)当初目的=ユーザー原文15条件・Regression基準・L97を逐語引用(ファイル:行) (2)成果物 (3)証拠(出力path・件数・費用実額[出典ログ:行]) (4)15条件ごとの充足/未充足 (5)判定(材料のみ、宣言しない)。加えて逸脱・委任_07申し送り(OF-AUW-08 R+許容集合縮小、値等価の実装位置、撤去/残置一覧、KP3回化)。
