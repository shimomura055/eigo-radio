# PROCEDURE_01: 合同runtime evidence 当日手順書(2026-10-23 JST実施用)

管理ID: JOINT-RUNTIME-EVIDENCE-PREP-01 委任_01(2026-10-22作成、API 0・JPY0の準備のみ)。対象: OPEN-450(PNAP)/OPEN-451(KP3V)/OPEN-454(KPFT)。
目的: Family X 1 run + Family Z 1 run で、固有名詞アラーム(PNAP)・KP 3-ASR多数決(KP3V)・KP全文選定+3件化(KPFT)の3件の発火証拠を**同時に**収集する。
集計script: `er106_joint_runtime_evidence_01.py`(read-only、test 37件PASS=`er106_joint_runtime_evidence_01_test_01.py`)。
凡例: 【確定】=本日の現行コード/設計書で確認済み、【要確認】=配線完了後(10-23朝)に実装結果で確認・差し替える箇所。

## 0. 準備時点(2026-10-22 夕)の状態と、手順書が依存する前提
- PNAP: 配線済み(別agent作業中・未commit差分あり)。X(`pnap_evidence_01__small_bag__run_02`、Khaite 1件・供給記録2件)は本日実行済み。Z(`melos/run_pnap_01`)は3 clipで**アラーム0件**。
- KP3V(`er104`)・KPFT(`er105`): 設計・未配線moduleまで。本手順書のKP3V/KPFT部分は、配線完了(両者のcommit)が前提。**配線未完了なら10-23の合同runは開始しない**(§1-1の判定)。
- 期待キーは設計書から取り`er106`の`EXPECTED_*`定数に集約済み。10-23に実装結果と食い違えば、`er106`は推測補完せず`MISSING`と出す(§6に差し替え対象一覧)。

## 1. 事前チェック(i)
### 1-1. コード状態(全部満たすまで有料runを開始しない)
```
git fetch origin && git status --short          # 他agentの未commit差分が残っていないこと(特にer019/er026/er063/er006/er003/er078/er103-105)
git log --oneline -8                             # PNAP/KP3V/KPFT 配線commitが全て入っていること
```
- 判定: (a) PNAP・KP3V・KPFTの配線commitが3つ揃っている (b) `git status`で上記Production .pyに未commit差分が無い。満たさない場合は走らせずFableへ報告(実行中のコードと証拠の対応が取れなくなるため)。
- 旧識別子の残存(情報): `.venv\Scripts\python.exe er106_joint_runtime_evidence_01.py --dangling-grep --out-md <path>`(runなしでは`--x-run-dir`省略可)。撤去対象(`dual_pass_required`等・旧db_hybrid経路)がProduction .pyに残っていれば配線が未完了。※`kp_dual_check`/`kp_dual_gate`系は設計§16-1 P-05で**維持**(撤去対象ではない)。

### 1-2. 全回帰(PASSを確認してから)
```
.venv\Scripts\python.exe -m unittest er106_joint_runtime_evidence_01_test_01 er103_proper_noun_alarm_policy_test_01 er103_pnap_wiring_test_01 er104_kp_three_asr_vote_01_test_01 er104_kp_three_asr_vote_01_test_02 er104_kp_vote_wiring_test_01 er105_kp_fulltext_selector_01_test_01
```
- 上記に加え各設計書の「Regression」節の既存群(PNAP設計§9: er006_secondary_asr系/er078_asr_unified_*/er011_human_review_lock/er097/er094/er026_family_z_*/er063_family_z_*/er019_*/inheritance系、KP3V設計§8、KPFT設計§10: er003_test_*/er019_*test*/er026_*test*/er062*/er063*/er030*)を実行し、件数とPASSを`RESULT_PACKET`へ記載する。モジュール名は**実装完了後に確認**(KP3V/KPFTの配線testは10-23朝時点の実在名に差し替え)。
- 1つでもFAILなら有料run開始を止めて原因を切り分け(委任範囲内で自律修正可。修正後に再回帰)。

### 1-3. STOP・予算・環境
```
.venv\Scripts\python.exe tools/stop_scope_check_01.py --managed-id JOINT-RUNTIME-EVIDENCE-01 --run-dir <X out_dir> --out docs/research/JOINT-RUNTIME-EVIDENCE-01/stop_check_x.json ; echo rc=$?
.venv\Scripts\python.exe tools/stop_scope_check_01.py --managed-id JOINT-RUNTIME-EVIDENCE-01 --run-dir <Z out_dir> --out docs/research/JOINT-RUNTIME-EVIDENCE-01/stop_check_z.json ; echo rc=$?
dir /b docs\pm\delegation_log\*STOP_NOTICE*   &   dir er026_output\family_z_production_e2e_01\STOP_ALL
```
- rc=0 のみ続行。**rc=3は新規API呼出をせず停止して報告**。NOTICE本文を自分で解釈しない。helperが実行できない場合は全`*STOP_NOTICE*`・`<run>/STOP`・`STOP_ALL`を適用とみなす(26-2)。STOPセンチネルの削除・回避禁止。有料run開始の直前にも再実行する(X・Z各1回)。
- `TTS_EXECUTION_MODE=STANDARD`: Xは環境変数(`set TTS_EXECUTION_MODE=STANDARD`。BATCHでないこと。`.env`で暗黙にBATCH指定されていないか`findstr TTS_EXECUTION_MODE .env`)、Zは`--tts-execution-mode STANDARD`(既定)。
- 日次予算: `.venv\Scripts\python.exe docs/pm/tools/daily_dev_cost_01.py --date 2026-10-23 --repo-root . --ledger docs/pm/REPORT_LEDGER.md` で当日使用額を確認(2026-10-22の使用はREPORT_LEDGER 498行=約887円[1,500円例外日]、`daily_dev_cost_01`のログ集計では約428円と出典で差がある。10-23は上限1,000円に戻る別日)。本手順の上限合計(§3)≤約110円 + 当日他作業の使用額 が1,000円以内であること。超過見込みなら実行前にFableへ報告。
- 26-2の遵守: 自分が起動したprocessが外部停止された/原因不明のrc≠0が2回続いたら**再起動せず即STOPして報告**。再起動は委任文が明示した回数のみ。監督ループ・別名ラッパ作成禁止。Zは`RUN_LOCK.json`(二重起動rc=4)と**RESTART_STORM(同一runを5分に3回起動で自動STOP)**があるため、Zは`--stage all`の1回起動を基本とし、dry-run(`--mode dry-run`は起動に数えない)で先に確認する。

### 1-4. 共有ログ前状態の保存(§5の前後確認用、API 0)
```
.venv\Scripts\python.exe er106_joint_runtime_evidence_01.py --x-run-dir <X out_dir> --z-run-dir <Z out_dir> --snapshot-out docs/research/JOINT-RUNTIME-EVIDENCE-01/run_20261023/pre_snapshot.json
```
保存内容: HR queue(英語・日本語)行数、`attempt_history.jsonl`行数、Ledger本体sha、Ledger sidecar(`negative_cache.json`)、Master Audio Store `manifest.json`のentry数と妥当性、STOPセンチネル一覧。**他agentの同時作業で共有ログが増える可能性があるため、増分は「このrunのrun dir名/パスを含む行」だけを帰属判定に使い、帰属不能な増分は別カウント(情報)にする**(`er106`が実装済み)。

## 2. 起動コマンド案(ii)
共通: 新run dirを使い、旧runのdirは変更しない。X・Zとも`levels=a2,b1b`(Std/Adv両方)。

### 2-1. Family X(coffee_prices本文再利用)
入力記事は旧`er019_output/coffee_prices/run_v5_ms_01`(読取専用。**`--slug coffee_prices --run run_v5_ms_01`のまま`--out-dir`だけ新規**にする=旧runのdirを書き換えない。【確定】`er019:2651 source_dir=er019_output/{slug}/{run}`、`--out-dir`は`derive_out_dir`で別指定可=CLI help)。同本文の既存完成run(sha一致)=`coffee_prices__run_m2p0_n01_01`(a2 `a3cc7bb98af7`/b1b `d9b77190905d`、narration 33/29 wav、両level組立済み)。
```
set TTS_EXECUTION_MODE=STANDARD
set OUT=er019_output/family_x_audio_production_wiring_01/coffee_prices__run_jre_01
rem (1) plan(API 0): parts.json/segment_plan.jsonを新out_dirへ作る
.venv\Scripts\python.exe er019_family_x_audio_production_runner_01.py --slug coffee_prices --run run_v5_ms_01 --out-dir %OUT% --stage plan --level both
rem (2) support文面(Preview/Comment等)を m2p0 run からコピー(API 0。ファイル名: a2/a2_support_texts.json, b1b/b1_support_texts.json)
copy ...\coffee_prices__run_m2p0_n01_01\a2\a2_support_texts.json %OUT%\a2\  &  copy ...\coffee_prices__run_m2p0_n01_01\b1b\b1_support_texts.json %OUT%\b1b\
rem (3) KP stageのみ(全文選定+3件化。KPFT/KP3Vの入口)。--scaffold-only kp は support 成果物が out_dir に無ければSTOP
.venv\Scripts\python.exe er019_family_x_audio_production_runner_01.py --slug coffee_prices --run run_v5_ms_01 --out-dir %OUT% --stage scaffold --scaffold-only kp --level both --budget-jpy 60 --tts-backend speech_metadata_flash_lite
rem (4) TTS(KP音声3-ASR投票・PNAP供給/アラームが動く段) -> (5) 組立 -> (6) player
.venv\Scripts\python.exe er019_family_x_audio_production_runner_01.py --slug coffee_prices --run run_v5_ms_01 --out-dir %OUT% --stage tts --level both --budget-jpy 60 --tts-backend speech_metadata_flash_lite
.venv\Scripts\python.exe er019_family_x_audio_production_runner_01.py --slug coffee_prices --run run_v5_ms_01 --out-dir %OUT% --stage assemble --level both --budget-jpy 60
.venv\Scripts\python.exe er019_family_x_audio_production_runner_01.py --slug coffee_prices --run run_v5_ms_01 --out-dir %OUT% --stage player --level both
```
- 【要確認】(a) `--style-profile`: 新out_dirの既定は`fx_20261017`(正式既定)。旧coffee runは`coffee_n01_r2_p3_e1`/`coffee_final_v5`(Coffee限定profile)のため**Store keyが異なり非KP segmentは再利用されず再生成**(+約23円、BAPE E2E audio実績23.22円。KPFT設計§11の「非KP再利用なら≈15円/再生成なら≤40円」の後者)。正式既定profileでの証拠を優先して**既定profileを推奨**(Cap内)。旧profile(`--style-profile coffee_n01_r2_p3_e1`)で再利用して費用を下げる選択肢もあるが、正式既定経路での証拠にならない。(b) 配線後の`--stage scaffold --scaffold-only kp`の挙動(support文面の要否・Xの外側retry新設・`STALE`退避・`kp_stage_failed.json`/rc=3)。(c) X試聴ページ: runnerの`--stage player`は`player.html`(KP行は`kp_by_rank`駆動で3件表示、コード変更不要=KPFT設計§9)。ユーザー試聴の標準`index.html`のbuilderは**Xに汎用scriptが無い**(`er019_bape_page_04.py`/`er071_coffee_m2p0_n01_page_04.py`は各記事固有)。10-23は`player.html`を`--x-page`でer106に渡し、標準`index.html`が必要なら実装担当に確認(未確定)。
- `--stage all`で1発にしない理由: scaffoldでsupport文面がLLM再生成され(約2円)コピーした文面と食い違い、後段のStore再利用・比較条件が崩れる。KP stageだけ新backendで動かし、他は固定する。
- 並列化の単位: X内は直列(stage依存)。

### 2-2. Family Z(melos複製)
旧完成run(例 `er026_output/family_z_production_e2e_01/melos/run_e2e_06`。**最新のPRODUCTION_WIRED runはFableに確認**)を新run dir `run_jre_01`へ複製する(キー設計: 複製対象=`writer/` `support/` `segment_plan_*.json` `dialogue_attribution_*.json` `speaker_table.md`、非複製=`key_phrases/` `a2/` `b1b/` `cost_log.jsonl` `e2e_stage_log.jsonl` `run_launch_log.jsonl` `STOP*` `RUN_LOCK.json` `page_verify_local.json` `gloss_alignment_flag.json`。`run_pnap_01`がこの複製方式の先例=【確定】`writer/provenance.json`のsha一致でseed/writer/std_adjust/plan/supportはreuse)。
```
.venv\Scripts\python.exe er026_family_z_fiction_production_runner_01.py --story melos --slug melos --run run_jre_01 --mode dry-run
rem 出力のstage別 resume 欄で writer/std_adjust/plan/support が「provenance sha一致で再利用」であること。「新規実行」ならSTOP(LLMでWriterが走り費用が増える)
.venv\Scripts\python.exe er026_family_z_fiction_production_runner_01.py --story melos --slug melos --run run_jre_01 --mode real --stage all --approved-budget-jpy 45 --tts-execution-mode STANDARD
```
- stage順(【確定】`E2E_STAGES`): kp → tts_b1b → tts_a2 → provision_shell → gate → assemble → pages → page_verify(KPFT/KP3V/PNAPは kp・tts_*で発火。以降は組立・ページの証拠)。kpのみ先行させたい場合は`--stage kp`単独→HR等を確認→`--stage all`(同stageは`ensure_stage`が再利用)だが、**起動回数が5分に3回に達するとRESTART_STORMでSTOP**されるため連続起動は避ける。
- 【要確認・要判断(B相当、Fable)】**試聴ページの出力先**: `build_real_context`は`STORY_REGISTRY["melos"]["e2e_pages_dir"]`=`user_test/family_z_melos_02`(ユーザー受入済みページ)を既定にする(`er026:239,907`)。`--stage all`(pagesステージ)は**このdirを上書き**し得る。対処案: (1)実行前に`user_test/family_z_melos_02`を退避コピー (2)runner側に`--pages-dir`相当の指定が実装されたかを確認(CLIには現状無い) (3)`--stop-after assemble`で止めpagesは別途。上書きしてよいかを実行前にFableが決める。
- Zの外側retry/stale退避・`FamilyZE2EStop`(`FAMILY_Z_KP_NOT_PASSED`等)は【確定】既存。新backend用の変更は10-23朝に確認。

### 2-3. 2 process 並列実行の条件
- 満たす条件(【確定】): 別run dir・別raw_usage_log(X=`<out>/raw_usage_log.jsonl`、Z=`<run>/cost_log.jsonl`)・別HR Lock(`<level>/audit/review_lock_state.json`)・別RUN_LOCK(Zのみ)・STOP確認はrun単位。KP stage(LLMのみ、Store非使用)とWhisper preflightは並列可。
- **TTS stage(X `--stage tts` と Z `tts_b1b`/`tts_a2`)の同時実行は推奨しない**(競合する同一ファイル=直列化の明確な理由、8-X): `er006_output/master_audio_store_01/manifest.json`は**lock無し・非atomic write**(`er006_master_audio_store_01.py:78-88`: 呼出のたびloadして全体をsaveする)。2 processが同時に走ると(a)更新消失(b)部分書込をもう片方がloadして`JSONDecodeError`、が起き得る。(b)は「原因不明rc≠0」を誘発して26-2のSTOP条件に当たる。共有Ledger(`ledger.json`)・`human_review_queue.jsonl`/`attempt_history.jsonl`(追記)も同系統の共有。X・ZともStoreを使う(Xはfixed shell/KP K2 store、Zは【要確認】)。
- 推奨タイムライン: `[X KP stage ‖ Z kp stage]`(並列) → `[X tts→assemble→player]` → `[Z tts_b1b→tts_a2→…→page_verify]`(Z開始はX tts終了後)。Z単独の実測=tts_b1b 345秒+tts_a2 322秒+page_verify 178秒(`run_e2e_06/e2e_stage_log.jsonl`)。Xは`m2p0`実績でtts数分/level。→ 全体の目安 約40〜55分(完全並列なら約25分短縮できるが競合リスクを取る)。並列にする場合は`er106`の`store_manifest`チェック(§5)と、先に`manifest.json`のバックアップ(コピー)を取り、`valid_json_after=False`または`entries_decreased=True`なら競合として報告する。**どちらにするかの最終判断はFable**(速度D vs 競合リスク)。
- CPU: faster-whisper smallは割れた時だけ(約2秒/clip)、各processで1ロード。重い並列時のCPU競合は未計測(KP3V設計§4)。

### 2-4. PNAPの補助run(任意、自然発火しなかった場合)
- 自然発火の見込みは低い: coffee本文の固有名詞はBrazil/Vietnam/Reuters/Chicago(多くCMU収録語)、melos本文の人名は文頭語が中心(`Melos said.`型でM1後のHRは3イベント/9日)。KP音声は対象外(PNAP設計§1-5)なのでKP語では発火しない。
- (a) X Khaite供給のmini-run(要否: **推奨=実施**。PNAP evidenceは本日10-22実行分がKP3V/KPFT配線前のコード状態のため、合同コード状態で供給(`Khaite->Kate`)・アラーム記録・非露出が壊れていないことを1回だけ確認する):
  `docs/research/PROPER-NOUN-PRONUNCIATION-ALARM-POLICY-PRODUCTION-01/runtime_evidence_x_01.py <新out_dir> full_story_part2`(正式runnerのTTS段関数を直接呼ぶPNAP先例。runner main/scaffold/RF/assembleは含まない)。素材=`er019_output/family_x_audio_production_wiring_01/pnap_evidence_01__small_bag__run_02`相当(Khaite入り`full_story_part2`)。見積≤10円(1 segment×最大3 attempt×1.3円≒4円+Stage1調査はLedger/否定キャッシュ済みなら0。Ledgerのkhaite entryは委任_03でユーザー承認のB階層人承認登録済み[`human_approved=True`/`tts_respelling=Kate`、REPORT_LEDGER 500行]=供給はこの登録に依存)。
- (b) Zのアラーム: 先例`run_pnap_01`は`--only-clips full_story_part1_c1,full_story_part1_c5,full_story_part3_c3`(3 clip)で**0件**。同一素材の反復はPNAP設計§10が禁止(自然発火しなければ**別素材**)。Z側の別素材(例: 別story)は実run素材が未整備のため**未確定→Fable判断**。それまでZのPNAPは「正式経路が同adapterを通る(test固定)+合同runで0件(エラーなし)」の事実だけを記録し、発火証拠は未確認として報告する(PRODUCTION_WIREDには不足、と明示)。

## 3. 期待費用(iii)(JPY、案件ごとに300円以下=7-7によりAI自律範囲。日次1,000円(JST 10-23)内)
| 項目 | 見積(上限) | 根拠 |
|---|---|---|
| X run(KP chain≈1.4 + TTS/ASR全segment。非KP再生成想定) | ≤40 | KPFT設計§11: BAPE E2E audio実績23.22円+KP chain/音声約3円。再利用できれば≈15円 |
| Z run(kp + tts_b1b/a2 + page_verify) | ≤40 | `run_e2e_06`実績27.58円(Store再利用が効けば下がる)。`--approved-budget-jpy 45`(runner guard、上限300) |
| Khaite供給mini-run(X、§2-4(a)) | ≤10 | 1 segment×3 attempt×1.3円+Stage1調査0(Ledger/キャッシュ済み) |
| PNAP別素材の追加(Z、要判断) | ≤20(予約) | PNAP設計§10: 最大3 clip×3 attempt×1.1円≒10円+余裕。実施はFable判断後 |
| **合計** | **≤約110円** | PNAP Cap100 / KP3V Cap10(追加API 0=Whisperはローカル、実費0を期待) / KPFT X≤40・Z≤40 のCap内に収まる(重複計上しない: 同じ2 runが3件の証拠を兼ねる) |
- KP3V追加費用: Whisper=ローカル¥0。割れ時のAzure追加呼出なし(従来dualと同数)。実測は`er106`(d)の`kp_audio_english:asr_azure`/`...:asr_openai`と旧5件runの比で確認。
- 超過見込み(300円超・日次1,000円超過・個別Cap超過)は実行前にSTOPして報告。分割して境界を回避しない。
- 1記事セット単価の推定: `er106`(d)の`total_jpy`(X: Std+Adv 2level=1セット)。KP関連=`kp_chain`+`kp_audio_*`。旧5件との比較は同じ集計を旧run(X: `paycheck_personality__run_pp_02`、Z: `melos/run_e2e_06`)に実行した結果(`legacy_baseline_check_01.md`: X total 15.45円/KP関連1.49円、Z total 27.58円/KP関連1.52円)と、1KPあたり単価×(5→3)で比較。設計の推定=約-4.8円/セット(KPFT設計§13)。**実測値で置換して報告**(推定を実測と書かない)。

## 4. 収集→er106集計→報告項目へのマッピング(iv)
### 4-1. 実行後の収集(全て読取専用・API 0)
```
.venv\Scripts\python.exe er106_joint_runtime_evidence_01.py ^
  --x-run-dir %OUT% --x-source-dir er019_output/coffee_prices/run_v5_ms_01 --x-page <player.html or index.html> ^
  --z-run-dir er026_output/family_z_production_e2e_01/melos/run_jre_01 --z-page <Zのpages dir>/index.html ^
  --snapshot-in docs/research/JOINT-RUNTIME-EVIDENCE-01/run_20261023/pre_snapshot.json --check-stop --dangling-grep ^
  --out-json docs/research/JOINT-RUNTIME-EVIDENCE-01/run_20261023/joint_evidence.json --out-md docs/research/JOINT-RUNTIME-EVIDENCE-01/run_20261023/joint_evidence.md
```
- stage途中・失敗時でも同じコマンドで走る(MISSINGとして出る)。**各stage完了ごとに実行して`joint_evidence_after_<stage>.json`を保存**すると、後段の失敗でも前段の証拠を失わない(§5-2)。
- 出力先は既存の`docs/research/JOINT-RUNTIME-EVIDENCE-01/`(新しい証跡置き場を作らない)。run dirのログのうち秘密が混入し得るデバッグログはcommitしない(26-X、`tools/secret_scan_01.py --staged`でhits=0確認)。
- `er106`のステータス語: OK / NG / MISSING(期待キー/成果物なし。実装側の名称差か未配線) / NOT_FIRED(自然発火せず) / MANUAL(機械判定不能) / INFO。**NOT_FIRED・MISSING・MANUALは「証拠なし」であり合格ではない**。

### 4-2. PNAP(原文§5の9確認 / §8の8項目報告)
| 項目 | er106の根拠 | 人手で足す証拠 |
|---|---|---|
| 確認1 発音情報取得・TTS供給 | PNAP-1/1b(results内supply記録、`supply_applied`、Ledger `evidence_tier`/`human_approved`/`tts_respelling`) | Khaiteなどの供給前後の綴り(operator_alarm_report.md) |
| 確認2 不一致→アラーム記録+制作継続 | PNAP-0/2/2b(`audit/pronunciation_alarms.json`と`operator_alarm_report.md`、必須項目の欠落なし) | 該当wav聴取(任意) |
| 確認3 HRに回らない | PNAP-3(HR queue/attempt_history新規行[このrun帰属]=0、Lock全RESOLVED) | pre_snapshotとの差分 |
| 確認4 ASR/retry/fallback/regen/resume整合 | PNAP-4(segments status)+KPFT-8/KP3V-5 | 同stage再実行時にアラームが保持されること(継承。必要時のみ) |
| 確認5 固有名詞以外は従来どおり | PNAP-5(`hr_residual`)・PNAP-8(KP segmentにALARMが付かない) | 既存回帰test |
| 確認6 完成報告まで引継ぎ | PNAP-6(`consistency.match`)+runner標準出力の「固有名詞発音アラーム報告」節 | RESULT_PACKETへ貼付 |
| 確認7 一般リスナー非露出 | PNAP-7(公開ページに`PASS_WITH_PRONUNCIATION_ALARM`/`アラーム付き`等なし) | `tools/user_test_page_standard_check_01.py --page ...` |
| 確認8 Regression/Validator/test | PNAP-9(MANUAL) | §1-2の結果 |
| 確認9 X/Z双方runtime | PNAP-J(X・Z双方で発火) | Z未発火なら未確認と明記 |
| 報告1〜8 | 1 Status=Fable / 2 改善例=supply_applied(Khaite->Kate)/ 3 HRなし完成=PNAP-2/3 / 4 表示例=operator_alarm_report.md貼付 / 5 品質維持=PNAP-5/8+回帰 / 6 単価・速度=er106(d) / 7 受入・SSOT=Fable / 8 未解決=NOT_FIRED項目 | |

### 4-3. KP3V(原文§5の9確認 / §7の8項目報告)
| 項目 | er106の根拠 | 備考 |
|---|---|---|
| 確認1 割れた場合のみWhisper | KP3V-1/1b(split=P!=S、`whisper_called`、I1違反=割れなしで発火) | 表: `(b)`の行一覧(state/row/P/S/W) |
| 確認2 2/3 PASSで正常終了 | KP3V-2(`PASS_VOTE_2OF3`) | 行: P+W / S+W。S+Wは事後試聴リスト区分(設計§16-1 P-03)。**2/3 PASSのwavは聴取してPASS妥当性を確認**(誤PASS検査) |
| 確認3 2/3 NGは従来NG | KP3V-3 | 最終採用wavがNG stateでないこと(KP3V-4) |
| 確認4 Whisper error/未利用でPASSにしない | KP3V-4(I1-I7)/4b(small/int8)/1c(preflight記録) | preflightの記録名は【要確認】 |
| 確認5 retry/fallback/regen/resume | KP3V-5(reused vote・attempts) | |
| 確認6 Store再利用にも新判定 | KP3V-6(`reused=True`のentryが新version`kp_vote_check_v1`) | 再利用が一度も起きなければNOT_FIRED(設計§9: 旧Z KP entryを再利用点6へ通す) |
| 確認7 解説・その他音声に影響なし | KP3V-7(英語phrase以外にvote証跡が付かない) | |
| 確認8 PNAPとの範囲整合 | PNAP-8(KP segmentにALARMなし) | |
| 確認9 X/Z双方runtime | KP3V-9/J(X・Zいずれかで発火で足りる=設計§16-1 P-06。双方未発火は不成立) | 設計P-06: 発火が観測できなければ「Xで観測+Zが同adapterを通るtest固定+Z runで`kp_vote_check_v1`記録」を事実として記録 |
| 報告2 think up/blurt/take part新旧判定 | **offline既存資産**=`docs/research/KP-THREE-ASR-MAJORITY-PRODUCTION-01/stored_audio_reeval_02.json`(設計§16-2) | 合同runでは再計算しない |
| 報告3 Whisper正式runtime発火 | KP3V-1b/J | |
| 報告4 誤PASSなし | KP3V-4+2/3 PASS wavの聴取 | |
| 報告5 追加コスト・時間・再生成削減 | er106(d)+vote `whisper.ms`(あれば) | 旧5件runとの1KP単価比 |

### 4-4. KPFT(原文§6の12確認 / §8の9項目報告)
| 確認項目 | er106 ID | 判定方法 |
|---|---|---|
| 1 全文直接選定 | KPFT-1 | `keywords_runtime_metadata.json`の`kp_backend_used=fulltext_p2`、`key_phrases_db_hybrid`不在、(X)entry_pointの`kp_backend_used_by_level` |
| 2 actual model ID=Luna | KPFT-2 | metadata `model_id=gpt-6-luna`(`response.model`照合済みの値)+raw_usage_logのselection行 |
| 3 正式Prompt 2 | KPFT-3 | `prompt_sha256=a12896f4…`(設計§2で固定) |
| 4 最大3件 | KPFT-4 | `keywords_canonicalized.json`のitems 1〜3(2以下は`shortfall`記録つきで許容) |
| 5 本文外/6語以上不採用 | KPFT-5 | 各`source_span`が本文(X: source article.md、Z: `writer/r2.md`/`std.md`)に連続一致、<=5語 |
| 6 原形化・一般化 | KPFT-6 | 変更されたKPの一覧(span→used_form、reason)。**聴取/目視で妥当性確認**(INFO) |
| 7 後段(意味/解説/音声/ASR/組立) | KPFT-7 | KP音声status、Std=日本語意味/Adv=英語解説、timeline KP数一致、再生順の間接検査(`key_phrase_N`長が 2×英+第3 以上、+5秒以内) |
| 8 retry/fallback/regen/resume | KPFT-8 | selection/canon/redundancy/outer回数が上限内、`STALE`・`m2_fallback`なし |
| 9 Dangling Reference | KPFT-9 | `--dangling-grep`(撤去識別子0件。維持名は情報) |
| 10 Regression/Validator/test | KPFT-10(MANUAL) | §1-2 |
| 11 X/Z双方runtime | KPFT-11 | 両family |
| 12 SSOT/Git | KPFT-12(MANUAL) | Fable |
| 報告2 切替証拠 | KPFT-1 | 旧backendは`db_hybrid`(旧run `paycheck`/`coffee`のmetadata)との対比 |
| 報告3 Luna/Prompt適用 | KPFT-2/3 | |
| 報告4 3件化 | KPFT-4 | |
| 報告5 原形化・後段整合 | KPFT-6/7 | |
| 報告6 retry/Store/resume | KPFT-8, KP3V-6 | |
| 報告7 品質・速度・単価 | er106(d)+旧5件比 | |
- 再生順(Std 英→日→英 / Adv 英→英解説→英): 【確定】`er003_b1_p9a_audio.py:423-440 build_key_phrase_block`は「番号→英→第3→英」。er106は**間接検査**(timelineの`key_phrase_N`長)のみ。**直接確認は人が先頭KPを実際に再生**(試聴)する。

## 5. 失敗時の切り分け(v)
### 5-1. どの配線由来かを特定する観点
| 症状 | 由来の特定観点 | 見る場所 |
|---|---|---|
| KP stageで停止(`kp_stage_failed.json`/rc=3、`FAMILY_Z_KP_NOT_PASSED`) | **KPFT**: `keywords_runtime_metadata.json`の`final_status`・`attempts_detail`(parse/検証不適合/model不一致)、`outer_retry/attempt_n`、`*.STALE_attempt*` | `<kp_dir>/` |
| KP音声がHR/技術STOP(`NG_WHISPER_UNAVAILABLE`/`NG_SECONDARY_UNAVAILABLE`/`NG_PROTECTED_DISSENT`) | **KP3V**: `kp_vote_check`の`vote_state`・`whisper.error`、Whisper preflight記録、circuit | `tts_generation_results.json` key_phrases[n].english |
| 固有名詞segmentでHR/NG継続(アラームにならない) | **PNAP**: alarmの`R_*`不受理理由(`hr_residual`の「境界外」件数)、`p3_entry`、`pronunciation_alarm`監査block | `audit/pronunciation_alarms.json` |
| KP stageは通るがTTSでKPが3件未満/5件のまま | KPFTの後段件数語(Std/Adv解説・組立)の取りこぼし、`_merge_checkpoint`刈り込み(Z)。`kp_dir`のitems数 vs `results.key_phrases`数 | er106 KPFT-4/7 |
| 全体の`JSONDecodeError`/`manifest.json`破損 | 並列TTSによるStore競合(§2-3) | `pre_snapshot`との`store_manifest` |
| Page/Gateが落ちる | Z page_verify、Audio Validation Gate(KP数を5固定で見ていないか=KPFT設計§10(6)) | `page_verify_local.json`、`gate_result_*.json` |
- **flagを切って再実行する切り分けはしない**(PNAP/KP3Vのrollback定数をOFFにするとProduction挙動の変更になり、有料run再実行=26-2の再起動禁止にも当たり得る)。切り分けは(1)run artifactの読取(2)API 0のreplay(保存転写の再判定、`calibrate_replay_02.py`、`er104_stored_audio_reeval_02.py`)で行う。
- 原因不明のrc≠0が2回続く/外部停止 → 再起動せずSTOP報告(26-2)。再起動が必要なら委任文の許可回数内のみ。

### 5-2. 「失敗しても他2件の証拠を無駄にしない」分離案
1. **process分離**: X・Zは別process・別run dir・別ログ。片方の失敗がもう片方のartifactを壊さない(STOPセンチネルはrun単位で作られるので、他方は継続可。ただしSTOP_ALLは全Z)。
2. **stage単位で証拠が確定する構造**: KPFTの証拠はKP stage完了時点(`keywords_*.json`)、KP3Vの証拠はTTS stageのKP音声完了時点(`tts_generation_results.json`のvote)、PNAPのアラームはhookの`finally`でSTOPや途中失敗でも出力される(PNAP設計P-08)。後段(assemble/pages)の失敗は前段の証拠を消さない。
3. **stageごとに`er106`を実行し保存**(`joint_evidence_after_<stage>.json`、読取のみ・費用0)。最終集計で後段がMISSINGでも、前段時点の証拠が残る。
4. **失敗件だけ先送り**: KPFT失敗(KP stage)でX/Zが止まった場合でも、KP3V/PNAPの証拠を取るには「既存の3件KP runの再利用」ではなく同run継続が必要で、KP stageが通らないとTTSに進めない。そのため**KP stageだけを先行確認(§2-3の並列タイムライン前半)し、KPFT失敗がTTS開始前に判明するようにする**(TTS費用を投じる前にKPFT起因の失敗を検出)。
5. 技術STOP(Whisper不可等)でKP3Vだけが止まった場合: 同run内の他segment(PNAP対象の英語ナレーション)はKP英語と独立なので、`--only-segments`/`--only-clips`で非KPのTTSを先に完了させ、PNAP証拠を確保してからKP英語を再開する(再開はresume=同stage再実行。起動回数は委任文の許可内)。

## 6. 設計書で未確定(10-23に実装結果で差し替える期待キー/手順)
- KPFT: (a) Xの`--scaffold-only kp`+`kp_stage_failed.json`の最終ファイル名・Xの外側retry新設の出力先(`outer_retry/attempt_n`か)(`EXPECTED_KPFT_METADATA_KEYS`はer105の現行meta=`er105:449-456`。配線で別名になれば差替え) (b) 原形化(Q1)の結果fieldの名称(`normalization_reason`の値) (c) gloss生成の成果field(`japanese_gloss`以外か) (d) `shortfall`以外の件数不足記録 (e) 3件化後のX/Zの件数語(Redundancy/解説)の記録場所。
- KP3V: (a) `kp_vote_check`の容器名(設計§16-1 P-05: 容器名`kp_dual_check`は維持、`version=kp_vote_check_v1`で区別。`er106`は両方を探索) (b) Whisper preflightの記録先(`WHISPER_PREFLIGHT_RX`がrun dir直下のjson/log/txtを探索。名称は未確認) (c) Whisper`ms`(処理時間)の記録位置 (d) judge auditの`vote`ブロックの最終キー(`EXPECTED_VOTE_AUDIT_KEYS`) (e) 再利用6点のtelemetry名。
- PNAP: (a) アラーム記録の`final_state`/`models`キー(現行実装で確認済みだが配線後再確認) (b) X/Zの`pronunciation_alarm_audit`埋込位置(summary) (c) `supply_applied`の件数と`results`内`supply_map`の位置(`SUPPLY_KEYS`)。
- 共通: (a) X試聴ページ(標準`index.html`)のbuilder (b) Z pagesの出力先(既存`user_test/family_z_melos_02`上書き問題) (c) Xのstyle profile(既定`fx_20261017` vs Coffee限定) (d) Z複製元run (e) Z PNAP発火素材。

## 7. 時間見込み(8-X、10-23当日)
| 工程 | 所要 |
|---|---|
| 事前チェック(git/回帰/STOP/予算/snapshot) | 約15〜25分(全回帰の実行時間に依存。2,339件系で数分〜十数分) |
| KP stage(X ‖ Z並列) | 約5〜8分 |
| X tts→assemble→player | 約15〜20分(BAPE/coffee実績: tts数分/level) |
| Z tts_b1b→tts_a2→…→page_verify | 約15分(`run_e2e_06`実測: 345+322+178秒+KP 約1分) |
| 集計(er106 stageごと+最終) | 約2〜3分 |
| 報告(RESULT_PACKET・SSOT・commit) | 約20〜30分 |
| 合計(X→Z直列TTS) | **約1時間45分〜2時間15分**。完全並列(Store競合リスクを取る場合)は約1時間20分〜1時間45分。KP3V/PNAPの自然発火待ち・別素材追加runがあれば+20〜40分 |
