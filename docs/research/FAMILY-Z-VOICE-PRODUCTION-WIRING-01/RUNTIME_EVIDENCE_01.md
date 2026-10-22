# FAMILY-Z-VOICE-PRODUCTION-WIRING-01 RUNTIME_EVIDENCE_01(委任_01+委任_02)

作成: 2026-10-23。run=`er026_output/family_z_production_e2e_01/the_open_window/run_e2e_01/`(以下R)。

## 1. Voice割当(R/voice_assignment.json、R/speaker_table.md)
| 人物 | 性別 | 順位 | Voice | A2 clip数 | B1B clip数 |
|---|---|---|---|---|---|
| vera | 女 | 1 | Zephyr | 10 | 10 |
| framton | 男 | 1 | Algieba | 2 | 2 |
| mrs_sappleton | 女 | 2 | Kore | 4 | 4 |
| men(夫・弟達) | 男 | 2 | Schedar | 2 | 2 |
Narrator=Aoede(A2 narrator16+intro/title/preview/comment 6、B1B narrator16)。Charon=B1B topic/preview/comment 5+shell 7(既存Advanced補助枠。登場人物dialogueにCharon 0)。旧Voice(Erinome/Charon dialogue)clip 0。出典=R/a2|b1b/audit/tts_generation_results.json(clip_kind×voice集計、segments A2 47/B1B 46 全てOK)。

## 2. HR Lock解消(Fable明示権限、委任_02)
- 原因: ASR Validatorが接続詞"and"を数値語列へ巻込み(commit 79e9b4310で是正)。Primary/Secondaryとも転写は原文一致(R/a2/narration/attempts/*c10_attempt{1,2,3}*.json)。
- 操作: `er011_human_review_lock_01.approve_regenerate(out_path, text, approved_by="fable:FZVW-02:validator_fix_79e9b4310")`(正規関数のみ、lock file直接編集・人工entryなし。text=lock記録hash 13d837f7…と一致する正規化text)。
- 証跡: R/audit_hr_lock_release_fzvw02.json(before: HUMAN_REVIEW_REQUIRED/STOPPED、after: REGENERATE_APPROVED、check_before_generation=proceed+consuming_regenerate_approval)。er011_output/attempt_history.jsonl に action=REGENERATE_APPROVED_GRANTED(2026-10-23T07:27:02)。
- 結果: resume後 c10 は attempt 1/1 で NORMALIZED_MATCH(verified=True)、状態OK。

## 3. run再開(1回、rc=0)
コマンド: `python er026_family_z_fiction_production_runner_01.py --story the_open_window --run run_e2e_01 --mode real --stage all --approved-budget-jpy 300 --warn-threshold-jpy 200 --tts-execution-mode STANDARD`(console=R/console_fzvw_02.txt)。seed_check〜page_verifyの全13 stage完了。再生成clip=1(a2 full_story_part1_c10のみ、他は再利用)。gate: A2 shared_gate=PASS、B1B shared_gate=PASS(audio_text_deviation 0、KP vote evidence 3/3)。assemble: A2 full 325.31秒、B1B full 298.82秒。tts_a2 elapsed 16.9s。起動前stop_scope_check=rc0(_stop_scope_check_fzvw_02/03.json)、他python run走行なし(Win32_Process確認)。

## 4. Pages・再生検証
URL(HTTP 200確認): https://shimomura055.github.io/eigo-radio/user_test/family_z_open_window_01/index.html / standard.html / advanced.html(commit beabf61b7)。
公開Pages上のPlaywright実再生(R/page_verify_public.json、er026_fz_play_verify_17.py): index audio36 plays_ok36 / standard 55・55 / advanced 53・53、plays_failed 0、http>=400 0、console error 0、seek_ok_all=True、file://なし、level label漏れなし。ローカル検査(R/page_verify_local.json): user_page_standard_check overall=PASS(seek_ok_allはlocal headlessで3 page false=melos run_jre_01のlocal検査と同様の既知挙動、公開側はTrue)。family_z_melos_02/family_z_melos_jre_01は無変更。

## 5. 発音アラーム(framton / Framton Nuttel)
A2 framton x5、B1B framton x8(いずれも「アラーム付き完成」、HR 0、制作停止なし)。ASR転記=frampton/crampton(Primary crampton含む、Secondaryは全てframpton)。固有名詞型の既知パターン。Pronunciation Ledger(er006_output/pronunciation_ledger_01/ledger.json)にFramton entryは未登録(no_ledger_entry_or_not_planned、供給なし)。出典=R/a2|b1b/audit/operator_alarm_report.md・pronunciation_alarms.json。新規判断は求めない。

## 6. 費用(出典=R/cost_log.jsonl compute_cost_jpy_so_far、stage log)
run累計JPY71.02(うち先行writer/std 17.76)。委任_01分 約52.45、委任_02分 約0.81(70.211→71.0213、c10 1clip+ASR)。合計 約53.26円(300円以内)。当日累計約53.3円/1,000。

## 7. メロス整合確認(委任_01(7)転記)
| 人物 | 現行(pin) | 規則適用値 | 差 |
|---|---|---|---|
| melos | Algieba | Algieba | 同一 |
| dionysius(king) | Charon | Schedar | 差 |
| selinuntius(friend) | Erinome | Fenrir | 差 |
再生成対象(run_jre_01実clip): Adv dionysius4+selinuntius2、Std dionysius3+selinuntius2=計11 clip(+再assembly/新Pages)、見積約3〜6円。メロスは2026-10-21 U:§7で完成版不変のためpin維持(STORY_VOICE_PINS、MelosPinTest)。規則へ揃えるかはユーザー承認事項(今回不要)。melos音声・family_z_melos_02は無変更。

## 8. Validator是正の前後比較(commit 79e9b4310、承認済み規則の不具合是正 11-8、Fable承認済み)
er109_b_fix_before_after_01.py(api0)で保存12,506件: PASS->NG 0 / NG->PASS 0 / 不変12,506。全Family共有Validatorだが挙動変化0(A/B/C展開提案ではない)。test: er006_cardinal_and_conjunction_test_01 5件。
