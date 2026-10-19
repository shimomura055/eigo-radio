# REGEN_PLAN_01(FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01 委任_06、2026-10-20。計画のみ。有料実行・Lock変更・copy実行は一切していない。実行は委任_07、①のFable照合後)

根拠のユーザー原文: `docs/pm/delegation_log/2026-10-20_FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_ROOT-CAUSE-WIRING-CLOSEOUT_USER.md` §5(L136-148付近)。
読取専用で確認した事実のみを記す。本計画の実行系コマンドは全て**未実行**。

## B-1 録音2 Human Review Lock解除の正規手順(特定のみ)
### 対象と現状
- 録音2 = run_e2e_04 の Std(`a2`) `full_story_part3_c1`(原稿 `…Melos drank, got onto his knees…`)。
- `er026_output/family_z_production_e2e_01/melos/run_e2e_04/a2/audit/review_lock_state.json`: `full_story_part3_c1.state=HUMAN_REVIEW_REQUIRED`、`canonical_text_sha256=b6d4377342693cf0925f2f9fbd89faf93c463d6d5b38bbd6c5052f3e62abccf8`、`final_status=STOPPED`、`cumulative_tts_attempts=3`。ファイルsha256=`6720ce80b7eedba9789dc190a431b030e20486b298a451479129e4d017fb3e19`(本委任の前後で一致を確認)。`a2/audit/human_approved_segments.json`は存在しない。
- 承認キーの検証(読取のみ): `run_e2e_04/a2/audit/tts_generation_results.json` の `segments.full_story_part3_c1.canonical_text`(=`text`)のsha256先頭12桁=`b6d437734269`、`n3_tts.tts_safe_news_en()`通過後も同一文(`==True`)。したがって承認キー(canonical_text)は「元の原稿`Melos drank`を含む文」= 上記tts_generation_resultsの`canonical_text`そのもの。

### 正規API(`er011_human_review_lock_01.py`の状態遷移)
| 遷移 | 関数 | 効果 | 今回の使用 |
|---|---|---|---|
| HUMAN_APPROVED | `er003_v1_n3_01_assemble.record_human_approval(out_dir, segment_key, canonical_text, approved_by="user")`(`er003_v1_n3_01_assemble.py:96`) | `<out_dir>/audit/human_approved_segments.json`へ`{segment_key:{canonical_text_sha256, approved_at, approved_by}}`を追記。`review_lock_state.json`は**変更しない**。`check_before_generation`(`er011:299`)は`_human_approved`(`er011:179`)=sha一致なら`status=HUMAN_APPROVED`(proceed=False、再生成には該当しない)。Z M2 Gate(`er063:1273`)も`cid in approvals`でOK扱い | **推奨(これのみ)** |
| REGENERATE_APPROVED | `approve_regenerate(out_path, text, approved_by="user")`(`er011:474`) | `review_lock_state.json`を更新(REGENERATE_APPROVED)し次の1回の再生成を許可 | **使わない**(run_e2e_04の同clipを再生成する目的がない。使うとLock sha256が変わる) |
- 引数(実行はしない・委任_07用の確定形):
  - `out_dir` = `er026_output/family_z_production_e2e_01/melos/run_e2e_04/a2`(level dir。`_human_approved`が`<level_out_dir>/audit/human_approved_segments.json`を読むため)
  - `segment_key` = `full_story_part3_c1`
  - `canonical_text` = 上記`tts_generation_results.json`の`segments.full_story_part3_c1.canonical_text`(**元の原稿**=Melos入り。Local Rewrite後の`He drank`文は渡さない=`record_human_approval` docstringの承認キー規定、ITEMS23 §10 条件3)
  - `approved_by` = 例 `user(2026-10-20 録音2 Human Review承認・FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01 ユーザー指示§4/§5)`(自由文字列。誰の承認かを明示)
- 実行形(委任_07用。ファイルから文を読み込み手入力ミスを避ける):
  ```
  C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -c "import json, er003_v1_n3_01_assemble as a; d='C:/Users/tensh/eigo-radio/er026_output/family_z_production_e2e_01/melos/run_e2e_04'; t=json.load(open(d+'/a2/audit/tts_generation_results.json',encoding='utf-8'))['segments']['full_story_part3_c1']['canonical_text']; a.record_human_approval(d+'/a2','full_story_part3_c1',t,approved_by='user(2026-10-20 録音2 Human Review承認・FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01 ユーザー指示4/5)')"
  ```
  実行後の検証(API 0): `human_approved_segments.json`の`full_story_part3_c1.canonical_text_sha256`=`b6d4377342693cf0925f2f9fbd89faf93c463d6d5b38bbd6c5052f3e62abccf8`、`check_before_generation(out_path,t,"en")["status"]=="HUMAN_APPROVED"`、`review_lock_state.json`のsha256=`6720ce80…`のまま(不変であることが正常)。
### 「録音2承認の記録」と「全再生成」の関係
- Lock/承認は**run単位**(`<level_out_dir>/audit/...`、`derive_segment_key`はtheme_id=run dir名を含む)。run_e2e_04の承認は新run `run_e2e_05` には**一切効かない**(承認ファイル・Lock stateは`copy_reusable_run_assets`のDENY: `human_approved_segments*.json`、`review_lock_state*.json`、`a2`/`b1b`丸ごと)。
- したがって扱いは: (a)録音2(run_e2e_04のStd part3_c1)は#116の正式クローズ記録としてHUMAN_APPROVEDを残す(ユーザー承認済み・再提示しない)、(b)新run `run_e2e_05` の全clipは新音声として**既存Gate(統一judge・Lock・M1/Tier3・LR・減速後再検証・Assembly Gate)で独立に判定**され、録音2の承認を引き継がない。ユーザー原文§5末尾の「①の解決に新たな仕様承認が必要となった場合は…STOP」は①側の条件(委任_05結果)。

## B-2 Std/Adv全TTS再生成の方式
### (i) 新run `run_e2e_05`と再利用/再生成の範囲
- runner = `er026_family_z_fiction_production_runner_01.py`(`Grep approved-budget-jpy`の該当runner)。`--regenerate-stage`は`ALL_STAGE_NAMES + kp_expl_b1b`のみで**TTS stage(`tts_b1b`/`tts_a2`)は選択肢にない**。TTSの再生成は「新run dirに既存TTS結果が無い」ことで成立する(= run_e2e_04を作った方式と同一)。
- 再利用(`er063.copy_reusable_run_assets`の許可リスト `REUSE_ALLOW_PREFIXES=("writer/","support/","key_phrases/")`・`REUSE_ALLOW_PATTERNS=("segment_plan_*.json","dialogue_attribution_*.json","speaker_table.md","provenance.json")`、`er063:632-639`): dry-runの結果(JPY0・読取のみ・何も作成していない)= **ALLOW 66 / DENY 306**。ALLOW内訳: `key_phrases/` 45・`writer/` 13・`support/` 3・top-level 5(`segment_plan_{a2,b1b}.json`・`dialogue_attribution_{a2,b1b}.json`・`speaker_table.md`)。= **writer / std_adjust / plan / support / kp は再利用**。
- 再生成(DENY): `a2/`・`b1b/`丸ごと(152+140 file、wav・`tts_generation_results.json`・`review_lock_state.json`・`narration`・`audit`・`key_phrases`導入済みasset)、`audit/`(run直下)、`cost_log.jsonl`・`e2e_stage_log.jsonl`・`run_launch_log.jsonl`等。= **`tts_b1b`・`tts_a2`は全clip(Dialogue/Narrator/KP/Preview/Comment/topic_intro/見出し等、run_e2e_04の実績 b1b 30 clip+a2 29 clip+各KP)を新規生成**。`stage_kp`の`install_kp_assets`は`key_phrases/`(ALLOW)から各levelへ再導入される(run_e2e_04と同じ流れ)。
- **`--regenerate-stage`は付けない**(support等は再利用が目的。run_e2e_04で付けた`support_a2`は当時の再生成のため。新runはrun_e2e_04のsupport/を継承する)。
- 作成コマンド(委任_07、dry-runで件数66/306を再確認後に`dry_run=False`):
  ```
  C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -c "import er063_family_z_audio_01 as a; r=a.copy_reusable_run_assets('er026_output/family_z_production_e2e_01/melos/run_e2e_04','er026_output/family_z_production_e2e_01/melos/run_e2e_05',dry_run=False); print(r['copied'],r['denied'])"
  ```
### T-2 7-5 の4点(計画として)
1. 差分再生成の可否: `--only-clips`で可能だが、ユーザー指示(§5)は**Std/Adv全TTSの意図的な全再生成**。差分再生成では「Advancedの`He drank`音声を元のMelos原稿の音声へ戻す」「全clipを現行のQA/Gate/設定で再評価する」を満たせないため全再生成を選ぶ。**(4)の「想定外の全再生成」に該当しない**(ユーザー明示指示)。
2. 既存の音声再利用キャッシュ: (a)run内再利用`generate_or_reuse_z`(`er063:709-735`)は**同一run dirの`tts_generation_results.json`のentry**(キー=canonical_text sha・role_style_version・voice・style sha・backend)が前提。新runにはDENYのため存在せず**再利用0**。(b)**Master Audio Store(`er006_output/master_audio_store_01`)**: Zの実TTS経路(`er063.real_generators` `:758-835`の`narrator/dialogue/charon_en/topic_intro/preview/ja_simple/kp_en`→`n3_tts.generate_a2_segment_with_slowdown`・`news_tail_fix`・`voice01`・`crosslevel`・`bvoices`・`_kp_en_two_stage`)は`ensure_key_phrase_english_component`/`ensure_all_shared_narration_*`(Master Storeを呼ぶ`er006_audio_cost_pilot_02_shared_narration`)を**呼ばない**(Grep: Z経路の`import er006_master_audio_store_01`は0件、`shared_narration.ensure_*`はLegacy A/B一括関数`er003_v1_n3_01_tts_generate.py:1077,1170,1218,1321`のみ)。よって同一文面の再利用は起きない。無効化の追加手段は不要(コード・設定の変更なし)。(c)`reuse_value_guard`/`rejudge_with_current_judge`は保存転写の再判定でありwavの再利用ではない。
3. 予算指定: `--approved-budget-jpy 80`(後述(iv))。
4. 上記の通り意図的であり、実行前STOP条件には該当しない。ただし**コピー後・runner起動前に**`stop_scope_check_01.py`を実行しrc=3なら中止。

### (ii) Advanced part3_c1が「He drank」で保存されている箇所と、新runで元原稿(Melos)から生成される根拠
- 「He drank」の保存箇所(run_e2e_04、実在):
  - `b1b/audit/tts_generation_results.json`(`segments.full_story_part3_c1`: `canonical_text`/`text`=Melos、`asr_text`=`…He drank…`、`audio_text_deviation.audio_text_after`=`…He drank, pushed himself onto his knees…`、diff `replace: 'Melos' -> 'He'`)・`b1b/audit/pass_with_warning_listening_list.json`・`b1b/audit/review_lock_state.json`・`b1b/audit/runtime_evidence_04C.json`・`b1b/narration/attempts/full_story_part3_c1_attempt4_englishstyleprefixwidemargin.json`(LR再TTSのattempt、`He drank`を送信)。音声(`b1b/narration/full_story_part3_c1.wav`)がLR後文の発音。
  - `a2`(Std)側にも同じLR(`Melos→He`)があった(`er011_output/attempt_history.jsonl`行15172)が、a2 part3_c1は減速後NG→HR Lockで`status=HUMAN_REVIEW_LOCKED`(③修正前)。
  - **`writer/provenance.json`(ALLOW=新runへ複製される)に`audio_text_deviations`が3件(b1b part3_c1×2・a2 part3_c1×1、いずれも`Melos→He`)**。`audio_text_deviations`を読む処理は書込み(`er063:1226-1233`)と初期化(`er062_family_z_writer_01.py:442`)と集約出力(`er063:1286,1364`)のみで、**判定・生成には使われない**(Grep全域: 読取でGate/TTS入力を変える箇所は0)。ただし新run `run_e2e_05` の最終監査記録に旧runの`He drank`履歴が混入して「Advancedに`He drank`が残った」と誤読される恐れがある。**推奨**: copy後・起動前に `run_e2e_05/writer/provenance.json` の `audio_text_deviations` を `[]` にリセットし、旧3件は run_e2e_05 のcopy記録(下記・記録項目)に退避する(データのみの編集。provenanceの検証対象はstage入出力のsha(`input_sha256`/`output_sha256`)でありこの配列ではない=`er062:439`のseed_sha256照合に影響しない)。この編集の可否は委任_07の指示(Fable判断)。
- 新runで元原稿(Melos)から生成される根拠:
  1. TTS入力の原稿は `segment_plan_{a2,b1b}.json`(ALLOW、run_e2e_04からcopy)の`text`/partsの本文→`ClipSpec.text`→`_norm_for_tts(spec)`(`er063:741-751`、`tts_safe_news_en`)。この`text`は**Writer成果物の元文(Melosを含む)**で、LRが書換えた文(`He drank`)は`tts_generation_results.json`の`audio_text_deviation`/`result["text"]`にのみ存在しplanには反映されない(実測: `run_e2e_04/segment_plan_b1b.json`は文字列`Melos drank`を含み`He drank`を含まない。narrator本文の元原稿shaはb1b=`b14691c4…`・a2=`b6d43773…`で、`tts_generation_results.json`のreuse_key/canonical_textと一致)。
  2. LR記録は run dir 名キーで分離: `er011_output/local_rewrite_recovery/<theme_id>/<level>/`(`crosslevel:433`、theme_id=run dir名)、`attempt_history.jsonl`のtheme_id、`review_lock_state.json`、`audio_text_deviation`(entryに保持)。新runのtheme_idは`run_e2e_05`で、run_e2e_04の記録は参照されない(DENY: `a2`/`b1b`/`audit`/`attempts`/`*snapshot*`)。
  3. 新規生成なので **LRが再び発火しない限り** Advancedは`Melos drank`でTTSされる。**LRが再発火すれば`He drank`になる**: 発火するかは①(Melos音韻同等性)の結果に依存(run_e2e_04では標準3回NGの後に発火)。①の判定が正しく機能していれば標準attemptでPASSしLR不到達の想定だが、保証はない。完了条件に「b1b/a2 part3_c1の`audio_text_deviation`が空であること(=Melos原稿のまま採用)」を入れ、LRが発火した場合は下記「LR発火時の取扱い」に従う。

### (iii) STOPセンチネル(26節)
- run_e2e_04を**凍結**するため、(1)B-1の承認記録を書いた**後**に `run_e2e_04/STOP` を設置する(前例: `run_e2e_03/STOP`、内容は `{"reason":"SUPERSEDED_BY_run_e2e_05 (Fable <日付>)","created_at":…,"note":"RUN_CLOSEDではない。…--mode real禁止。将来の正規解除は --clear-stop --reason のみ(Fable判断)"}`。設置はFable/委任_07の委任範囲。設置しても記録書込み(API 0)には影響しない。(2)`stop_scope_check_01.py --managed-id <ID> --run-dir er026_output/family_z_production_e2e_01/melos/run_e2e_05 --out <json>` を起動直前に実行(rc=0を確認。本委任の作業開始時にrun_e2e_04を対象に実行済み: rc=0、`2026-10-12_…STOP_NOTICE`は非適用)。(3)`er026_output/family_z_production_e2e_01/STOP_ALL`は触らない。

### (iv) 費用見積と出典
- 出典: `er026_output/family_z_production_e2e_01/melos/run_e2e_04/audit/cost_by_stage_04.json`(実測、`total_jpy_measured=46.1364`)。内訳: `tts_b1b`=26.24・`tts_a2`=19.5917(**TTS系合計45.83**)、`kp_gloss_person_repair`=0.0557・`support`=0.249(run_e2e_05では再利用のため**0**)、LLM全体=0.9019(うちLR候補生成/QAの`gpt-6-luna`を含む)。種別: TTS(gemini)22.58/ASR azure18.48/ASR openai4.18。calls: tts_a2=126。
- run_e2e_05の見積: TTS+ASR(全clip、run_e2e_04と同条件)≈ **JPY45.8**(clip数・方式が同じ)。変動要因: (a)run_e2e_04は part3_c1 の a2/b1b 各々で標準3NG+cooldown600秒+LR再TTSを含む(=最悪側の2 clip分を既に含む)ため、①が機能すれば減る方向。(b)他clipでの新規NG→retry/LR(1 clipあたり+約1〜5円、Azure ASR増)。想定レンジ **JPY40〜60**。
- 上限: `--approved-budget-jpy 80`(run_e2e_04と同一値、実績46.14に対し余裕1.7倍)。runnerのbudget guardはclip単位(`E2E_TTS_CLIP_EST_JPY=1.0`)で`spent+est>80`の前にSTOP(`FamilyZBudgetStop`)。ユーザー個別Cap・日次1,000円・案件300円はFable管理(本見積は案件300円以下、7-7の自律範囲内。日次残は委任_07起動前にFableが確認)。
- 定型上限文(T-3): 上限¥80(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。

### (v) 実行コマンド全文(絶対パス・実引数。起動は**1回のみ**、再起動は委任文が明示許可した場合のみ)
```
# 0. 作業ディレクトリ
cd C:\Users\tensh\eigo-radio
# 1. (B-1) 録音2承認記録 -> 上記B-1の実行形
# 2. run_e2e_04 STOP設置(Fable/委任_07の委任範囲)
# 3. 新run作成(上記の copy_reusable_run_assets dry_run=False)、必要ならprovenanceのaudio_text_deviationsリセット
# 4. 停止確認
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\tools\stop_scope_check_01.py --managed-id FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01 --run-dir C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_05 --out C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_05\stop_scope_check_fzaq7.json
# 5. dry-run(JPY0。plan・preflightのみ)
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er026_family_z_fiction_production_runner_01.py --run run_e2e_05 --mode dry-run --stage all
# 6. 実行(real)。TTS_EXECUTION_MODE=STANDARD(Batch不使用: 7-2のBatch例外条件に該当せず)
$env:TTS_EXECUTION_MODE='STANDARD'; C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er026_family_z_fiction_production_runner_01.py --run run_e2e_05 --mode real --stage all --approved-budget-jpy 80 --tts-execution-mode STANDARD
```
- `--story melos`は既定、`--regenerate-stage`なし、`--only-clips`なし。runnerは`seed_check→writer(reuse)→std_adjust(reuse)→plan(reuse)→support(reuse)→kp(reuse)→tts_b1b→tts_a2→provision_shell→gate→assemble→pages→page_verify`の順で一括(`E2E_STAGES`、`er026:826-827`)。runner自身が`_launch_guard`でRESTART_STORM/RUN_LOCKを管理。
- 失敗終了時の最終成果物の扱い: rc≠0なら`run_e2e_05`の部分成果物(narration、`tts_generation_results.json`、Lock state、`cost_by_stage`)を保全し、pages stage未達なら`user_test/family_z_melos_02/`は旧版のまま。再起動はせずFableへ報告(26節)。HR Lockが再発した場合は`--only-clips <clip>`再試行も新たな有料起動のためFable指示を待つ(run_e2e_04の経緯と同じ)。

### (vi) 完了条件
1. rc=0、`tts_b1b`・`tts_a2`が全clip OK(`tts_generation_results.json`の全entry `status=OK`、HR Lock 0。録音2承認はrun_e2e_05に無関係)。
2. `gate`(M1/M2 + 既存Gate)・`assemble`(Audio gate: VALIDATED/HUMAN_APPROVED のみ許可、`AUDIO_GATE_ALLOWED_STATUSES`)PASS、`pages`(`user_test/family_z_melos_02/`更新、API 0)、`page_verify`(local、`run_e2e_05/page_verify_local.json`、`user_page_standard_check=PASS`)。
3. 公開: `user_test/family_z_melos_02/`のcommit+push後、`https://shimomura055.github.io/eigo-radio/user_test/family_z_melos_02/`がHTTP 200(Pages反映は遅延し得るためcurl -I等で確認)。
4. Advanced part3_c1(`b1b`)の `audio_text_deviation` が空で、`asr_text`に`Melos`(またはQAが受理する同等発音)が含まれること。Std part3_c1も同様。**LR発火時の取扱い**: 発火した場合は(原稿が`He`等に書換わった事実を)ユーザー指示§5「Advancedの`He drank`は元のMelosを含む原稿に戻す」と照合してFableへ報告(自動で受理/拒否を再判断しない。既存のLR_REWRITTEN警告+試聴リスト運用に従う)。
5. 原稿の意味・構成が不変: `writer/`の各sha(r0/r1/r2/std、provenance output_sha256)と`segment_plan_*.json`のsha256がrun_e2e_04と一致。
6. 費用: `cost_by_stage`(`audit/cost_by_stage_05.json`相当)を集計して80以内を確認。

### (vii) 記録項目
- 発動した判定経路: 各clipの`asr_judgement`(PASS/PASS_WITH_WARNING/NG_BOTH、`reason_code`)、M1/Tier3/Eq Layerの発動、Secondary使用(`secondary_not_accepted`等)。
- 警告: `pass_with_warning_listening_list.json`(a2/b1b)の件数と内容、`LR_REWRITTEN`。
- LR発火: `er011_output/local_rewrite_recovery/run_e2e_05/`、`attempt_history.jsonl`(theme_id=run_e2e_05, action=`LOCAL_REWRITE_RECOVERY`)、`audio_text_deviation`、`local_rewrite_recovery.status`。**LRが発火した場合**: 各clipの`result["post_slowdown_expected_text_source"]`(`local_rewrite_text`/`canonical_text`)、減速後判定(`post_slowdown_classification`)、`A2_SLOWDOWN_REVERIFY`行 = ③の**修正後live evidence**(ITEMS23_WIRING_ASSURANCE_01 §3の不足項目(a))。発火しなければ「未観測」と記録。
- HR対象: `human_review_queue.jsonl`の新規行(`lock_canonical_text`/`expected_text_source`併記)、`review_lock_state.json`のHUMAN_REVIEW_REQUIRED、`z_adoption`。
- 費用・時間: stage別JPY、cooldown発生、壁時計時間。
- 旧runとの差分: run_e2e_04から継承した資産(copy計画json: ALLOW 66/DENY 306、`audio_text_deviations`リセットの有無と退避先)。

## B-3 ①(委任_05)との依存
- 委任_05が「範囲内修正あり」の場合は、**修正→当該modulesのRegression(per-file test + ITEMS23の2 test + 関連suite)→commit/push→(新構造ならOpus Gate判断はFable)→上記B-2のstep 1〜6**の順。修正後・起動前にRegressionを入れ、`run_e2e_05`のcopyは修正後HEADで作る(コピー自体はコード非依存だが、`dry-run`のpreflightとstop_scope_checkを修正後に行う)。
- 委任_05が「範囲外(新仕様が必要)」の場合は、ユーザー原文§5末尾に従い**B-2を実行せずSTOP**し、判断候補としてFableへ戻す(未承認仕様のまま再生成を強行しない)。
