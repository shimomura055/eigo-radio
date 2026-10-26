## 管理ID

PM-SSOT-SYNC-04(FAMILY-Y-VOICE1-MALE7-TRIAL-01 委任_01の結果とFable判定、CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01 委任_02の中間結果をSSOTへ反映。API 0・JPY0)。並行タスク衝突確認: 並行Agent 2件あり。(a) CHUNK 委任_03(Z Std実装。`er117_*`/`er063_*`/`docs/research/CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01/`を編集・commit中)、(b) KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01 委任_01(`docs/research/KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01/`・`er124_*`を作成)。**SSOT編集権は本Agentのみ**が持つ(`OPEN_ITEMS.md`/`DECISION_LOG.md`/`docs/pm/REPORT_LEDGER.md`/`docs/pm/USER_DECISION_REGISTER_01.md`/`docs/pm/OPUS_FINDINGS_LEDGER.md`/`docs/pm/ACTIVE_TASK.md`)。`CURRENT_SPEC.md`は本委任では編集しない(Chunk節の是正はZ完了後の次回sync)。上記以外のファイル(コード・research dir)は編集しない。git index.lockが並行Agentと競合したら10秒待って再実行(最大3回)。

## 性質/到達上限Status/禁止事項

- 性質: SSOT転記(Closeout記録)。到達上限Status: 本委任自体は「転記完了」。転記する内容のStatusは下記Fable判定のとおり(格上げ禁止)。
- 禁止: Production/コード/Prompt変更、API支出、`CURRENT_SPEC.md`編集、`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・`git checkout -- <file>`。他Agent由来のworktree差分(CRLF全行差分・er117/er063等の未commit変更)を**巻き込まない**: 共有SSOTファイルは「HEAD blobを取り出し→自分のhunkだけ適用→その内容をstage」の方式(`git show HEAD:<path>`をscratchpadへ書き出し、自分の追記を加え、`git add`前に`git diff --cached --stat`で自分の追記行数のみであることを確認)。
- 費用/日次: JPY0。
- Opus独立技術レビューGate(11-3): 非該当(転記のみ)。
- 時間見込み: 全体約40分(照合10分/編集20分/commit・push10分)。並列化: なし(SSOT編集は直列ルール8-Y)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSなし)
T-2追記(2026-09-25、`NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02`、PM_GOVERNANCE.md 7-5、予算逸脱再発防止): TTSを伴う委任は実行前に(1)差分[変更箇所のみ]再生成が対象コード上で実際に可能か確認、(2)既存の音声再利用キャッシュの有無を確認、(3)`--budget`/`--budget-jpy`等が存在すればタスク固有の承認上限に合わせて明示、(4)想定外の全再生成と判明した場合はAPI実行前にSTOPし報告、の4点を必須とする。

T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-26_PM-SSOT-SYNC-04_DELEGATION_01.md` をN=649から順に試し、先頭が「## 管理ID」+「PM-SSOT-SYNC-04」で始まるものを採用(同時刻にKP Trial委任文も送られているため先頭一致を必ず確認。`--index -1`不可)。

## ユーザー指示(原文)

該当なし(Fable判定の転記。元のユーザー指示は`docs/pm/delegation_log/2026-10-26_FAMILY-Y-VOICE1-MALE7-TRIAL-01_USER.md`と`docs/pm/delegation_log/2026-10-26_CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01_USER.md`に保存済み)。

## Fable判定(転記する内容。文言はこのまま使う)

### A. FAMILY-Y-VOICE1-MALE7-TRIAL-01(OPEN-531更新)
- Trial Status: **VALIDATED(限定)_USER_DECISION_REQUIRED**(Production採用はユーザー承認のみ。自動格上げなし)。
- Fable最終推奨(独立評価): **Puck**(1名)。根拠: 事前固定の主要指標「文境界に対応しない≥1.0秒の停止」が全6 cellで0.00回/sample(Algieba 0.36 [0.23,0.59])、悪いtake率0%(Algieba 31%)、fresh take最終OK率24/24・ASR合格94%、最終音声に文中≥1秒が残る率8%(Orus 17%)。Orusも推奨条件を満たし区間が重なるため統計的に区別不能(位置非依存の全≥1秒ではOrus 0.38<Puck 0.49)だが、主要指標・悪いtake率・最終音声残存率でPuckが一貫して最良のため、Fableは1名としてPuckを推奨。限定事項: 声質・人物像・V2(Zephyr)/V3(Schedar)との聞き分けは機械評価不能で未評価(ユーザー試聴で確認)。PuckとOrusはいずれもFamily Z男性Voice表(CURRENT_SPEC.md:1563)に既出(Family間の重複は承認済み基準に含まれないが、情報として記録)。
- 実費276.13円(Guardrail 250円を26.1円超過、案件300円以内=7-7自律範囲。原因=Phase 2のAlgieba再生成連鎖(Repetition QA旗)、暴走でない。Fable許容)。新規100 take+再利用58 sample。重複生成2 take(約8円、結論不変)。
- 試聴ページ: `https://shimomura055.github.io/eigo-radio/user_test/family_y_voice1_male7_trial_01/index.html`(commit 6fb173355)。
- 新規OPEN(11-8分類「修正へ進む候補・非blocking」): Voice 1 Algiebaの新規生成でRepetition QA旗率72%・take最終OK率38%(平均2.31 attempt/take)=Voice 1の再生成コストが高い。Voice変更を採用しない場合でも調査候補。
- 分類: ユーザー判断事項=Voice 1のPuckへの変更採用(APPROVED_FOR_PRODUCTION)。採用提案時はOpus条件C判定を別途行う。

### B. CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01 委任_02(OPEN-532中間更新)
- Opus M1・R1〜R5=実装済み(commit d00f41c8b)、test 30件追加・回帰PASS、Adv不変(旧新バイト一致)。
- runtime evidence: X Std=EVIDENCE_COLLECTED(正式CLI、uk_train run_stdchunk_ev_01、10 chunk、6%減速比1.0568〜1.0600、0.2秒無音=4800サンプル整数一致、再起動時API 0回、実費6.20円)。Y Std/Adv=EVIDENCE_COLLECTED(複数段落dev入力・正式生成関数/Gate/組立をrunner同条件で直接呼出、実費1.77/1.50円)。**Yは現行本文契約(段落5固定・Voice本文1行)では正式CLIから構造的に不発火**(実記事run_01全8 segment `chunked:false`)。Z Std=未実装・未取得(委任_03進行中)。PRODUCTION_WIRED判定はZ完了後にFableが6行表で確定。
- 運用逸脱(記録): 実LLM呼出し0.0084円(R4 driver初版、遮断前実行)、X Std 1回目STOP後26秒で再起動(150秒規律違反、課金0)。
- Opus台帳OF-CHKW: M1・R1〜R5=IMPLEMENTED→EVIDENCED(d00f41c8b/c00a20ed9)、M2/M3/R6/R7=FABLE_DECIDED(Z委任_03へ引継ぎ中)。
- 実費9.48円(Cap 100)。

## KPI provenance欄

該当なし(転記のみ。各数値の出典=`docs/pm/RESULT_PACKET_YM7.md`・`docs/pm/RESULT_PACKET_CHKW2.md`・`docs/research/FAMILY-Y-VOICE1-MALE7-TRIAL-01/RESULT_01.md`・`docs/research/CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01/EVIDENCE_01.md`)。

## Opus台帳更新

`docs/pm/OPUS_FINDINGS_LEDGER.md`: Grep `OF-CHKW` → M1・R1〜R5の状態をEVIDENCED(commit d00f41c8b, c00a20ed9、EVIDENCE_01.md)へ、M2/M3/R6/R7は「FABLE_DECIDED(Z委任_03で実装中)」のまま日付追記。

## 事前指定Read一覧

- `docs/pm/RESULT_PACKET_YM7.md` 全文(転記元)
- `docs/pm/RESULT_PACKET_CHKW2.md` 全文(転記元。(9)にSSOT文案あり)
- `docs/pm/ACTIVE_TASK.md` 全文(10行)
- `docs/research/FAMILY-Y-VOICE1-MALE7-TRIAL-01/RESULT_01.md:1-20`(7名表の数値照合)
- `docs/research/FAMILY-Y-VOICE1-MALE7-TRIAL-01/BUDGET_LOG_01.md`: Grep `276|合計|Guardrail` → 該当行±5

## 事前指定Grep一覧+追記位置・更新位置の手順

- `OPEN_ITEMS.md`: Grep `^\| OPEN-531|OPEN-531` → 本体行のStatus/概要を上記Aで更新(履歴は`OPEN_ITEMS_HISTORY.md`方式に従い既存行の書式を踏襲)。Grep `OPEN-532` → 本体行に上記B中間更新(X Std/Y EVIDENCE_COLLECTED・Z未・判定はZ後)。Grep `OPEN-527` → 「Yは現行契約では正式経路で不発火(CHUNK委任_02実証)」を1文追記。新規OPEN: Grep `^\| OPEN-53[0-9]` で最大番号を確認し次番号(OPEN-533想定)でAlgieba Repetition旗率の件を起票(11-8分類を明記)。
- `DECISION_LOG.md`: Grep `^## 2026-10-26|2026-10-26 \|` で本日エントリの末尾を特定 → 2件追記(①Y male7 Trial結果+Fable推奨Puck+VALIDATED(限定)_UDR、②Chunk 委任_02 Opus M1/R1〜R5採用+X Std/Y evidence+Y構造的不発火の事実)。
- `docs/pm/USER_DECISION_REGISTER_01.md`: Grep `OPEN-531` → 既存エントリを更新(決めること=Voice 1をPuckへ変更するか/選択肢=Puck採用・Orus採用・Algieba維持/Fable推奨=Puck/根拠1行/試聴URL)。Grep `OPEN-532` → 「Std拡張は承認済み。Z完了後に判定報告」で現状維持。
- `docs/pm/REPORT_LEDGER.md`: 末尾形式を確認し、FAMILY-Y-VOICE1-MALE7-TRIAL-01(報告予定→Fable報告)・CHUNK委任_02(中間・報告予定)・KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01(受領・委任_01開始)を記録。
- `docs/pm/ACTIVE_TASK.md`: 全文を上書き(管理ID=並行3件[CHUNK委任_03/KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01委任_01/本sync]、Status、UDR-blocking=OPEN-526・527・529(区分2)・531(Puck推奨)、STOP条件=猿の手run_fzcw_e1_01残置のまま、QDC=当日約500円+進行中Chunk Z Cap60+KP Trial Cap80/1,000)。

## 実行コマンド全文

- 試聴URL到達確認: `powershell -Command "(Invoke-WebRequest -Uri 'https://shimomura055.github.io/eigo-radio/user_test/family_y_voice1_male7_trial_01/index.html' -UseBasicParsing -Method Head).StatusCode"`(200ならOK。404ならPages反映待ちとして記録し、5分後に1回だけ再試行)
- commit存在確認: `git log --oneline -1 6fb173355`・`git log --oneline -1 c00a20ed9`・`git branch -r --contains 6fb173355`(origin/mainに含まれること)
- HEAD blob取得例: `git show HEAD:OPEN_ITEMS.md > C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1\scratchpad\OPEN_ITEMS.head.md`(以後、自分の追記のみ加えて元pathへ書き戻し→`git add OPEN_ITEMS.md`→`git diff --cached --stat`で行数確認。worktreeに他Agent由来のCRLF全行差分がある場合はこの方式で回避)
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## SSOT追記文

上記「Fable判定」の文言をそのまま使う。

## Git(明示add対象・コミットメッセージ・trailer)

- add対象: `OPEN_ITEMS.md`、`DECISION_LOG.md`、`docs/pm/USER_DECISION_REGISTER_01.md`、`docs/pm/REPORT_LEDGER.md`、`docs/pm/OPUS_FINDINGS_LEDGER.md`、`docs/pm/delegation_log/2026-10-26_PM-SSOT-SYNC-04_DELEGATION_01.md`(+`_check.json`)。`docs/pm/ACTIVE_TASK.md`・`RESULT_PACKET_*`はgitignored(addしない)。
- commit message: `PM-SSOT-SYNC-04: Y Voice1 男性7Voice Trial結果(Fable推奨Puck、VALIDATED(限定)_UDR、OPEN-531/新規OPEN)・Chunk Std委任_02中間(X Std/Y EVIDENCE_COLLECTED、Y構造的不発火、OPEN-532/527)のSSOT反映(API 0)`
- trailer: `Delegation: PM-SSOT-SYNC-04/01`
- push: `git push origin HEAD:main`(non-ffなら`git fetch origin`→`git merge --no-edit origin/main`→push。競合はSTOPし報告)。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_SSOT4.md`に: (0)T-0結果、(1)更新したSSOT行(ファイル:行、前後の差分要約)、(2)試聴URL到達結果、(3)commit存在確認結果、(4)`git diff --cached --stat`の行数(自分の追記のみであることの証拠)、(5)commit hash・push結果・raw URL(OPEN_ITEMS.md/DECISION_LOG.md/USER_DECISION_REGISTER_01.md)、(6)RESULT_PACKET必須4行(既存仕様整合/未承認機能の既定値=該当なし/失敗終了時の最終成果物/撤去・残置)+「判定整合: 重大NG=<なし|あり>」1行、(7)一覧外Read。最終報告は10行以内の要約を末尾に。