FABLE-DELEGATION-MARKER: PNPS-STAGE1-E2-委任_05-20261022

# 委任(PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02 委任_05 [E-2]: 固有名詞発音取得 Stage 1(承認済み・判定基準不変)のProduction配線・Regression・runtime evidence・SSOT。Opus条件(S1-01〜10、論点B/E/F)反映済み設計に従う。費用上限JPY10。`PRODUCTION_WIRED`判定はFable)

## 0. 運用ルール・並列注意(重要)
- 他agent稼働中: (C-3)記事A再制作=Family X Production runnerを実走中(text→TTS→ASR→組立)。あなたのProduction編集(`er006_secondary_asr_01.py`の最終slot調査周辺・`er006_pronunciation_ledger_01.py`)は新しいprocessから即座に読まれるため、**編集は十分にtest済みのコードを短時間で一括適用**し、適用直後に回帰test(secondary_asr_01_test/er096 wiring/er094/backcompat_07/m1_wiring)を回して壊れていないことを確認する。C-3の成果物(`er019_output/paycheck_personality/run_pp_02/`、`user_test/paycheck_personality_e2e_02/`)には触れない。
- 編集対象: `er006_secondary_asr_01.py`(`_resolve_unresolved_entity_for_review`内側+stub `ambiguity_note`)、`er006_pronunciation_ledger_01.py`(`upsert`素通し3キー、統一lookup呼出)、`er097_*`、関連test、Ledger data(`mini`隔離=OPEN-436の枠、backup必須)、`er006_output/`のsidecar(新規)、PNPS docs、SSOT行。共有ファイル編集前に `git status` → 該当行を再Grep → 自分の行だけ編集 → 即 `git add <file>` + commit。`index.lock`は30秒待って再試行。`git add -A/-u/-f`、amend、rebase、force push、stash、clean、reset --hard、checkout -f 禁止。secret_scan hits=0。push=`git push origin HEAD:main`。一時ファイルはforce-add禁止。SSOT全文読込禁止。他人の未commit差分(`er011_output/attempt_history.jsonl`等)を混ぜない。
- **孤立した未commit差分の整理**: `OPEN_ITEMS.md`(OPEN-441行付近)と`docs/pm/REPORT_LEDGER.md`に他agent由来の未commit差分が残っていると報告がある。`git diff`で内容を確認し、完了済みagentの正当なSSOT行(OPEN-441ラベル更新/REPORT_LEDGER行)であれば本委任のcommitに含めて由来を報告、不明なものは触らず報告。
- 有料工程(最終slot調査1回≈5.4円、実URL取得)は**Ledger/sidecar pathを一時コピーへ差し替えて**実施(架空語をProduction Ledgerへ登録しない)。STOPセンチネル確認後に実施。

## 1. 前提
- 設計書 `docs/research/PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02/STAGE1_IMPLEMENTATION_DESIGN_01.md`(Opus反映済み、commit e260b0278)、module `er097_pronunciation_supply_stage1_01.py`(test 56件PASS)、効果測定 `stage1_effect_measure_02_result_e1b.txt`。
- Opus条件(採用済み): S1-01(開示: 判定ロジック・閾値・自動PASS条件は不変、Ledger蓄積は減る方向にのみ変わり得る3経路)/S1-02(副作用は`_resolve_unresolved_entity_for_review`内側のみ、mockが`None`でもstub動作、既存test[設計書§2列挙]のmock隔離不変)/S1-03(例外安全、済)/S1-06(stub `ambiguity_note`を省略理由別に)/S1-08(定数1個`PRON_SUPPLY_STAGE1_ENABLED`、Production側定数+旧関数保持、全ON/全OFFのみサポート)/S1-09(upsert素通し3キーは渡されたentryにある場合のみ、キー無し呼出のバイト一致test)/S1-10(sidecarはgit管理)/論点B(`mini`をOPEN-436の枠で隔離、前後のPhrase List差分と判定差分0を記録)/論点E(一時コピーpathで実調査1回・実URL取得、4,032ペア差分0は回帰確認に留まると明記、「自然発生は未観測」を残事項)/論点F(命名=「出典ページ照合(弱い確認)」、キー`source_page_check_v1`)。
- ユーザー承認(2026-10-22): Stage 1実施。判定基準・自動PASS条件は変更しない。

## 2. 作業
1. **基準線**: 配線前に設計書§2列挙の既存test群を実行し結果を保存(baseline)。
2. **配線(一括適用)**: 設計書どおり関数内側へ。シグネチャ・戻り値形は不変。Production側定数`PRON_SUPPLY_STAGE1_ENABLED=True`(既定ON=承認済み)、OFFで旧挙動バイト一致。stub `ambiguity_note`理由別。Ledger `upsert`素通し(S1-09)。sidecar path(`er006_output/pronunciation_negative_cache_01.json`等、git管理)。
3. **`mini`隔離**: OPEN-436の隔離手順に従いLedgerの一般語entry `mini`を隔離(backup・理由記録)。前後でPhrase List生成差分(保存canonical文95種)と判定差分0(保存転写再判定)を記録。
4. **Regression**: baselineと同一test群+er097 56件+新規配線test(ON/OFFバイト一致、mock `None`時stub動作、一般語除外で調査不呼出、否定記録で不呼出、統一lookup命中、HR表示キー追加、Ledger upsertバイト一致)+4,032ペア再判定差分0(回帰確認)+Family X/Z実関数へのmock注入で発火(X=`er019_family_x_audio_production_runner_01.py`経由の`evaluate_attempt_with_cascade_detail`、Z=`er063`経由、ともに最終slot NG→調査経路でStage 1の分岐が記録されること)。全PASS。
5. **runtime evidence(有料・最小)**: 一時コピーpathで、(a)辞書外語1語の最終slot調査1回(実API、≈5.4円)→Ledger登録→`source_page_check_v1`の実URL取得・照合→HR表示の階層行、(b)同語の再実行で調査不呼出(否定記録またはLedger命中、API 0)、(c)一般語で調査不呼出(API 0)。費用実測(出典)。
6. **SSOT**: CURRENT_SPECへ新節「固有名詞発音情報の供給 Stage 1(否定記録/統一lookup/一般語除外/HR階層表示/出典ページ照合[弱い確認]、配線点、rollback定数、判定不変の保証と間接影響3経路の開示、Status=`WIRED_PENDING_FABLE`)」+1837(B)に「Stage 1は表示・管理のみでPASS根拠にしない」注記。DECISION_LOG(配線記録)。OPEN-441→`STAGE1_WIRED_PENDING_FABLE / STAGE2_PLAN_V4_PENDING_FABLE`。OPEN-436に`mini`隔離追記。REPORT_LEDGER。PLAN_SUMMARY Scope台帳。
7. T-0保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-22_PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02_委任_05.md`(Nは jsonl 内で `FABLE-DELEGATION-MARKER: PNPS-STAGE1-E2-委任_05-20261022` を含むAgent tool_useの0始まり通番、261前後)。
8. commit(配線+Regressionで1回、evidence+SSOTで1回)→push→到達確認。`docs/pm/ACTIVE_TASK.md`先頭に固定ヘッダ。`docs/pm/RESULT_PACKET_PNPS5.md`へ報告(ユーザー§7 Aの順: 何を改善したか/不要調査がどれだけ減ったか[保存データ: 一般語6/18語の初回調査、否定記録・統一lookupは過去データで発火0]/判定基準不変の証拠[ON/OFFバイト一致・判定差分0・呼出位置]/X/Z配線・検証状況/QCD効果・SSOT・Git・Status案。+`mini`隔離結果+Opus条件充足表+費用実測+RESULT_PACKET 4行+raw URL)。

## 3. 禁止
合否判定基準・自動PASS条件・Prompt(research Prompt含む)の変更、架空語のProduction Ledger登録、C-3成果物への接触、KP dual/多語/数値丸めのコード変更、費用上限超過、Stage 2の実装。