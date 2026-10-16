## 管理ID

`ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01` 委任_13(A3[length NG]是正の実装: 設計D1+Opus条件Aレビュー指摘A3R-01〜09の反映、unit/呼出元/静的test、最小実音声[Azureのみ]、SSOT、commit/push)。並行: 委任_12(main dir `C:\Users\tensh\eigo-radio` で有料evidence実行中。**main dirのファイルを編集しないこと**)。**本委任は専用worktreeで作業する**: `git -C C:\Users\tensh\eigo-radio worktree add C:\Users\tensh\eigo-radio-a3 -b work/a3-01 origin/main`(失敗時は理由を記録しFableへ報告して中止)。Python/pytestは `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe` を絶対パスで使い、cwdはworktree。mainへの反映は最後に: worktreeで`git fetch origin; git merge origin/main`(競合があれば自己解決せず中止報告)→SSOT追記→commit→`C:\Users\tensh\eigo-radio-crbn`で`git pull --ff-only origin main; git merge --no-ff work/a3-01 -m "merge work/a3-01 (AUW 委任_13 A3是正)"; git push origin main`(rejected時は`pull --ff-only`→再試行最大3回)。終了後worktreeは残置(Fableが次委任で撤去指示)。

## 前委任(委任_11)の受入記録(Gate 7、A3部分)
- 当初目的(A-2逐語): 「**Primaryの差が大きいという理由だけでSecondaryを省略したり、Secondaryの正当なPASSを拒否したりしない。**」「7. 数値・否定などの明確な重大内容差、独立音声品質QAは維持する。」
- 最終成果物: A3是正は条件付きSTOP s4で保留(設計案D1=`IMPLEMENTATION_11.md`§3、呼出元10箇所・7ファイル一覧、保存データ集計: 統一judge記録中のA3作用0件)。
- 証拠: `er078_asr_unified_judge_01.py:121,138`(A3)、`er006_secondary_asr_01.py:920`(EN ctxのlength_ok既定True)、呼出元一覧。
- 一致・不一致: A3はPrimary転写由来のlengthで、Secondary正当PASSを拒否しうる=A-2太字と不整合(未是正)。
- 判定: 是正はFable判断で実施(Opus条件Aレビュー済み、新ユーザー判断なし)。QDC: 改善見込み高/API ≤JPY1/次=本委任。

## 性質/到達上限Status/禁止事項
- 性質: ユーザー承認済み仕様(A-2)への実装修正(Production判定フロー・呼出元10箇所)。到達上限Status: `A3_FIXED_PENDING_FABLE`。`PRODUCTION_WIRED`は書かない。
- 禁止: `git add -A`/`-f`、amend、rebase、force push、stash、clean、`reset --hard`、`checkout -f`、main dirのファイル編集、HR Lock変更、A-6(Secondary障害)挙動変更、length閾値の意味変更(正規化長への切替・新gate追加)、音声長/文字数比の新gate、β期待値変更、`force_secondary`拡大、TTS生成(実音声はAzureのみ・既存wav利用)、Opus指摘の無断不採用(採用しない場合は理由を記録)。
- 条件付きSTOP: (s7)呼出元が10箇所を超える/legacy・Trial scriptとの区別がつかない箇所がある→一覧を作り、Production 10箇所以外は静的testの除外listに載せて続行、不明なら記録してFableへ。(s8)merge競合→中止報告。
- Opus独立技術レビューGate(11-3): 条件A **実施済み**(A3R-01〜09、Fable採否=全件採用)。原文はjsonlから機械抽出して保存(Sonnetは本文を読まなくてよい)。
- 時間見込み: 150〜200分(実装90・test 60・実音声10・SSOT/Git 30)。並列化: unit test先行可。
- 費用/日次: 当日既使用 約JPY57+委任_12(≤34)/本委任 ≤JPY1(Azure 2〜4回)/改善見込み 高/承認区分: C。
- T-3定型文: 「上限¥2(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。」

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSなし)
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`、ユーザー正式決定、費用上限[Cap]を伴う全委任で常時有効): 費用上限[Cap]は「暴走防止のためのGuardrail」であり、Cap到達=自動STOPではない。(定型文は「性質」欄)

T-0保存先(worktree内): `docs/pm/delegation_log/2026-10-16_ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01_13.md`(**全文**)。

## ユーザー指示(原文)
`docs/pm/delegation_log/2026-10-16_AUW-FAMILY-C-DQI-USER-INSTRUCTION.md`「# A.」A-2(#2・#7・太字)・A-3「固有名詞差・類似度0.4未満**等**」・A-7。

## Opus指摘の反映要件(A3R-01〜09、Fable採否: 全件採用)
- **R1(A3R-01 MAJOR)** EN 6箇所(`er003_v1_crosslevel_audio_02_common.py:361`、`er003_v1_repro01_main_generate.py:355`、`er003_v1_sing01_news_tail_fix.py:206`、point_headings、`er003_v1_sing01_voice01_generate.py:255`系、Family B:557)もJA 4箇所も、呼出元の`max_len`(余裕文字数10/15/20/30/40/60で異なる。LR後v1は書き換え後の文で計算した`retts_max_len`)を`attempt_ctx`経由でjudgeへ渡す。judge内で`len(text)+15`等を固定再計算しない。
- **R2(A3R-02 MAJOR)** 「Primary内容PASS+length NG」はjudgeでP3へ降格(`primary_length_ng`、AMBIGUOUS降格と同形)しSecondaryへ回す。合意時はPASS_WITH_WARNING(`force_secondary_agreed`の無警告PASSにしない)。Primary length計測は`gate_text`(adopted_text)基準。
- **R3(A3R-03 MAJOR)** 安全ラッチ: `ctx.max_len is None`なら従来挙動(JAはA3除外/ENは従来)、max_lenがあるときだけA3を外して再評価。helper `final_length_ok`はfail-closed(置換条件=`asr_judgement`存在∧state PASSING∧`audit["length"]["adopted_from"]=="secondary"`∧`adopted_ok is True`。それ以外はPrimaryのlength_okを返す)。静的testでProduction 10箇所が`max_len`を渡し`verified_content and length_ok`形が残っていないことを保証(legacy/Trial scriptは明示除外list)。
- **R4(A3R-04)** (c)案(judgeでTrue上書き)は不採用。
- **R5(A3R-05)** `er007_ja_secondary_asr_01.py:664-665`の`length_not_ok`診断文・`:538`docstring更新。A3除外前提の旧挙動固定testの棚卸し(α更新、β不変)。
- **R6(A3R-06)** attempt logに`final_length_ok`追加(Primary `length_ok`は残す)。audit `length{primary_len,secondary_len,max_len,adopted_from,adopted_ok,surface_len(参考)}`。
- **R7(A3R-07)** Secondary救済時にPrimary超過が大きい場合、additiveなwarning label `PRIMARY_LENGTH_EXCESS`を付与(受理条件不変)。試聴リスト導出に載ること。
- **R8(A3R-08)** OPEN-388の「過短/過長」→「過長(上限のみ)」に訂正(行内追記)。
- **R9(A3R-09)** A3ルールは表から削除せずmodule定数(env/flagではない)で無効化(rollback容易化)。Secondary障害露出増は記録のみ。
- 実装時確認: `n3:630`の`detect_duration_anomaly`がJA minimal fallback(n3:720、voice01:567)にも効いているか確認し記録(効いていなければR7の重要度を上げ、OPEN候補として記録。新gate追加はしない)。
- disfluency/repetition gateのANDは順序含め不変(#7維持)。

## KPI provenance欄
unit/呼出元/静的test: `synthetic`。実音声(最小2 clip、Azureのみ): 正例=既存合格wav+Primary転写を「原稿+max_len超の尾部」へ差し替えるmock→実Azureで受理+length OK; 負例=既存wav 2本をローカル連結した音声に片方の原稿→実AzureでNG_BOTH。`reuse`(wav)+`fresh`(Azure)。E2E自己確認: No。

## Opus台帳更新
`OF-AUW-A3R-01`〜`-09`を追加(RAISED→FABLE_DECIDED(採用)→IMPLEMENTED/EVIDENCED)。`OF-AUW-U1R-04`→IMPLEMENTED。追記のみ。

## 事前指定Read一覧
- `er058_output/unified_all_roles_production_wiring_01/IMPLEMENTATION_11.md` §3(D1・呼出元10箇所一覧)。
- `er078_asr_unified_judge_01.py` L115-140、L215-230(`AttemptCtx`)、L360-370(gate_text)、L380-410(降格・P2除外)、L485-500(Secondary受理)。
- `er006_secondary_asr_01.py` L130-150、L915-955、L970-1015。`er007_ja_secondary_asr_01.py` L535-540、L610-615、L660-667、L739-749。
- 呼出元: `er003_v1_crosslevel_audio_02_common.py` L81、L166、L343-381、L408; `er003_v1_repro01_main_generate.py` L199、L292、L346-390、L808、L822; `er003_v1_n3_01_tts_generate.py` L303、L630、L661、L716-748、L786、L1221-1307; `er003_v1_sing01_news_tail_fix.py` L137、L160-219; `er003_v1_sing01_voice01_generate.py` L482、L505-583; point_headings(Grep `verified_content and length_ok`)L120-135; Family B(Grep同)L540-560。
- `er078_pass_with_warning_registry_01.py` L24-32。`er003_audio_tts_asr_safety.py` L189-203。
- `OPEN_ITEMS.md` Grep `OPEN-388 `。

## 事前指定Grep一覧+追記位置・更新位置の手順
1. Opus原文保存: `C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1\subagents\agent-a4328351a0244471f.jsonl`(無ければ`tasks\a4328351a0244471f.output`、それも空ならセッションjsonlのtask-notification本文)から、scratchpad抽出script(`.venv\Scripts\python.exe -I`、「# Opus独立技術レビュー: AUW A3」を含む最後のassistant text)で `er058_output/unified_all_roles_production_wiring_01/OPUS_REVIEW_A3_01_VERBATIM.md` へ逐語保存(sha256・文字数)。**Read toolで開かない**。
2. 全repo `*.py` Grep `verified_content and length_ok`/`length_ok and`/`and length_ok` → Production 10箇所+legacy/Trial一覧(除外list根拠)。
3. SSOT(merge origin/main後に追記): `CURRENT_SPEC.md`統一ASR判定仕様節に「A3是正(2026-10-16 委任_13): length判定はSecondary受理時に採用転写(Secondary)で再評価。Primary内容PASS+length NGもSecondaryへ降格。呼出元10箇所は`max_len`をjudgeへ渡し最終ANDは`final_length_ok`(fail-closed)。安全ラッチ=max_len未指定の呼出元は旧挙動。rollback=module定数。」`DECISION_LOG.md`委任_13エントリ。`OPEN_ITEMS.md` OPEN-388行内追記(是正済み・過長のみ・Fable判定待ち)。`REPORT_LEDGER.md`。Opus台帳。`CLOSEOUT_PLAN_07.md`§4-dに15条件表(委任_13時点: 条件1・2の残なし[A3是正済み]、15=Fable)。`RUNTIME_EVIDENCE_06.md`§19(A3実音声2 clip・audit length記録)。ACTIVE_TASK(gitignore、main dir側はFableが別途)。

## 実行コマンド全文
手順0: `git -C C:\Users\tensh\eigo-radio worktree add C:\Users\tensh\eigo-radio-a3 -b work/a3-01 origin/main; cd C:\Users\tensh\eigo-radio-a3; git status --porcelain --branch`。`C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe tools\stop_scope_check_01.py --managed-id ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01 --run-dir er058_output\unified_all_roles_production_wiring_01\evidence_13`(dir先行作成)rc=0。
手順1(実装): judge(A3ラッチ・降格・再評価・audit・warning label・module定数)、adapters(EN/JA ctxにmax_len)、呼出元10箇所(max_len渡し+`final_length_ok`置換、disfluency/repetition不変)、JA診断文、新規test `er078_asr_unified_wiring_13_test_01.py`(unit 11項目+呼出元10 mock+静的+試聴リスト導出)、α棚卸し。
手順2(test、API 0、netguard=`C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1\scratchpad\netguard.py`をPYTHONPATHに): `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -m pytest -p netguard <中核17 file+er078_asr_unified_wiring_10/11/13_test_01.py+er078_asr_unified_backcompat_07_test_01.py+呼出元に対応する既存test[er003/er012/er019/er063系の該当file]> -q -p no:cacheprovider`。期待: 新規失敗0(koro 2件は既知OPEN-391)。静的監査(15 passed+script差分空。judge/adapterの呼出増があればallowlist更新をphase付きで記録)。`er020_*ProductionModuleUnchanged`はcommit後に再実行。
手順3(実音声、Azureのみ): `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe er078_auw_runtime_evidence_13.py a3_pos --out er058_output\unified_all_roles_production_wiring_01\evidence_13\a3_pos --budget-jpy 2 --execute` と `a3_neg`(既存wav連結)。費用meter・STOPセンチネル。
手順4(SSOT・Git): `git fetch origin; git merge origin/main`(競合→s8)→SSOT追記→secret scan(`--paths`)hits=0→`git add <変更したProduction file群> er078_asr_unified_wiring_13_test_01.py er078_auw_runtime_evidence_13.py <更新α test> er058_output/unified_all_roles_production_wiring_01/IMPLEMENTATION_13.md er058_output/unified_all_roles_production_wiring_01/OPUS_REVIEW_A3_01_VERBATIM.md er058_output/unified_all_roles_production_wiring_01/RUNTIME_EVIDENCE_06.md er058_output/unified_all_roles_production_wiring_01/CLOSEOUT_PLAN_07.md er058_output/unified_all_roles_production_wiring_01/evidence_13 CURRENT_SPEC.md DECISION_LOG.md OPEN_ITEMS.md docs/pm/REPORT_LEDGER.md docs/pm/OPUS_FINDINGS_LEDGER.md docs/pm/delegation_log/2026-10-16_ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01_13.md docs/pm/delegation_log/2026-10-16_ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01_13_check.json` → `git commit -m "ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01 委任_13: A3 length是正(Secondary転写で再評価・Primary PASS+length NGの降格・呼出元10箇所max_len渡し・fail-closed・安全ラッチ、Opus A3R-01〜09反映、JPY <実費>)"` → crbnでmainへ`--no-ff` merge→push → 手順2末尾のer020再実行(crbnまたはworktreeでmain HEAD)。

## SSOT追記文
Grep手順3(実値置換)。

## Git(明示add対象・コミットメッセージ・trailer)
SSOT編集権: あり(追記のみ)。main dirは触らない。本番state file・他委任fileはaddしない。

## 報告(RESULT_PACKET項目)
worktree内 `docs/pm/RESULT_PACKET_AUW13.md`(gitignoreなら内容を報告本文にも): 1 T-0・Opus原文保存sha256 / 2 実装差分(ファイル:行、R1〜R9対応表、10箇所のmax_len値一覧、除外list) / 3 test結果(unit 11・呼出元10・静的・中核・er020) / 4 実音声2 clip結果(audit length記録) / 5 `detect_duration_anomaly`のJA minimal fallback適用確認 / 6 SSOT・merge commit・push・secret scan / 7 逸脱 / 8 費用実測・所要 / 9 受入記録5項目(当初目的=A-2逐語/最終成果物[失敗終了時含む]/証拠/一致・不一致/判定)。`PRODUCTION_WIRED`は宣言しない。
