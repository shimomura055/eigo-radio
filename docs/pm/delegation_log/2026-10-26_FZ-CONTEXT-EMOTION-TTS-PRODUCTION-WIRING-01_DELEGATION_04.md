## 管理ID

FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01 委任_04(Closeout: Fable判定PRODUCTION_WIREDのSSOT反映=CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS/OPUS台帳/UDR/REPORT_LEDGER+ACTIVE_TASK。API 0)。並行Agent: (1)KP-GATE-EXCLUSION-RESCUE-DESIGN-02 委任_03(**CURRENT_SPEC.md:1997付近のKP節を自hunkで編集中**。本委任はCURRENT_SPECのZ音声/セリフTTS節のみ編集し、commit前に`git fetch origin`+最新HEAD blobへ自hunk適用) (2)CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01 委任_02/_03(er117/er019/er121/er063+研究dir) (3)Y男性7Voice Trial。本委任の所有=SSOT 6ファイルの自hunk、`docs/pm/ACTIVE_TASK.md`、`docs/research/FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01/CLOSEOUT_01.md`、`docs/pm/delegation_log/2026-10-26_FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01_DELEGATION_04*`、`docs/pm/RESULT_PACKET_FZCW4.md`。コード編集なし。

## 性質/到達上限Status/禁止事項

- 性質: 転記のみ。Fable判定を正確に転記(Sonnetは判定を変えない)。
- Fable判定(転記内容): **FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01 = PRODUCTION_WIRED(Family Z限定・Std/Adv、2026-10-26)**。根拠: ユーザー承認(APPROVED_FOR_PRODUCTION 2026-10-26)/設計Opus条件A(M-1〜M-10/R-1〜R-2採用)/実装test 93 PASS・既存失敗集合不変・X/Y/B/C golden一致/runtime evidence E-1〜E-6 Std/Adv全PASS(実TTS・実ASR・実Gate、melos、実費40.31円)/正式初回経路(E-1注入0、dialogue 21 clip全てctx)/後続経路(E-2 fallback・cooldown 600.001秒・E-3 cooldown中kill→再開で重複TTS 0・E-4 3回NG→TERMINAL_NG+HR Lock+rc=2停止・4回目なし・E-5 1回目NG→2回目即時PASS・E-6 Adv減速後NG→外側ループ継続)/SSOT反映=本委任。Fable許容: D-1(作品を猿の手→melosへ変更: 猿の手seedのprovenance不一致でrunnerが課金前停止したため。証拠価値は作品非依存、melosは複数話者を含む)、E-4のSTOP形態(stage例外rc=2+HR Lock=既存runner仕様、sentinelなし)、D-2 driver修正2点(Production不変)。開示事項: D-3 自発RESTART_STORM(猿の手`run_fzcw_e1_01`にSTOP/RESTART_STORM_LOCK残置、run dir限定、未解除=Fable判断で解除不要[当該run dirは使用しない])/M-3(i)シナリオ(Adv minimal_fallback併発)は未観測・現行は安全側STOP/実音声の聴取評価は未実施(自動QAのみ)/Z dialogueにLocal Rewrite未配線(3回NG→HR Lock/STOP直行、ユーザー原文後段を満たす。LR新設は別承認事項)/量産単価影響=TTS区分+0.59円(+2.1%)+notes LLM 0.27円/セット≒+0.9円/セット(猿の手Z総原価46.82→約47.7、推定・1作品1回)。
- 禁止: コード編集/Git禁止操作(`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・`reset --hard`・`checkout -f`・`git checkout -- <file>`)。共有SSOTは**HEAD blob+自hunkのみ**(`git diff --cached --stat`で確認、CR 0)。
- 費用/日次: JPY0。時間見込み30〜40分。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2: TTSなし。T-3: Capなし(JPY0)。

委任文保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index 647 --out docs\pm\delegation_log\2026-10-26_FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01_DELEGATION_04.md`(先頭が「## 管理ID」+「FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01 委任_04」でなければ643〜660を順に試す)→check実行。

## ユーザー指示(原文)

`docs/pm/delegation_log/2026-10-26_FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01_USER.md` §7「以下を更新する。CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS/必要な設計・runtime evidence/Git commit／push。今回の正式採用をFamily Z専用仕様として記録する。旧方式は3回目のFallbackとして利用できるよう維持し、新方式が後続経路で参照されない等のDangling Referenceを防ぐ。」「**すべてのGate条件を満たして初めてPRODUCTION_WIREDと判定する。**」

## 事前指定Read一覧

1. `docs/research/FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01/DESIGN_02.md` §J(CURRENT_SPEC文案)、`EVIDENCE_01.md` §1〜§5、`COST_01.md`、`SHARED_LEDGER_01.md`、`docs/pm/RESULT_PACKET_FZCW3.md`。
2. `CURRENT_SPEC.md` Grep `Family Z|セリフ|dialogue|ER-011|a2減速`→Z音声節の挿入位置(:1615付近のZ E2E節、またはZ音声仕様節)。
3. `OPEN_ITEMS.md` Grep `OPEN-528|OPEN-516|OPEN-511`。`DECISION_LOG.md` 先頭30行。`docs/pm/OPUS_FINDINGS_LEDGER.md` Grep `OF-FZCW`。`docs/pm/USER_DECISION_REGISTER_01.md` Grep `OPEN-528`。`docs/pm/REPORT_LEDGER.md` 末尾10行。`docs/pm/PM_BRIEF.md` Grep `ACTIVE_TASK固定ヘッダ`。

## 事前指定Grep一覧+追記位置・更新位置の手順

- CURRENT_SPEC.md: Z音声仕様節に新節「Family Z セリフTTS 文脈・感情付き方式+Fallback(2026-10-26ユーザー正式採用、PRODUCTION_WIRED)」をDESIGN_02 §J文案にevidence値(cooldown実測、TTS回数、費用、E-1〜E-6結果、melos)を補完して追加。内容: 対象(Z dialogue Std/Adv、X/Y不適用)/試行列(ctx→ctx即時→600秒cooldown→従来方式、総3回、以後STOPPED→HR Lock→STOP。Z dialogueにLocal Rewriteは未配線)/感情notes正式経路(Trial同一Prompt・モデル、決定論検査で自動受理[Trial目視を工程置換]、level単位1 call、失敗は1回再試行後に技術STOP[再開可])/fallback時はCONTEXT完全除外(従来promptとバイト一致)/状態の永続化・再開・明示再生成の判別/M-3=(ii)(実TTS 3回超えず、稀ケースは安全側HR)/X/Y/B/C不変(hook=None golden)/Dangling Reference防止(旧方式参照の残置)/量産単価影響/既知事項(M-3(i)未観測、聴取未実施、LR未配線)。既存のZ E2E節のStatus行に「セリフTTS=ctx方式PRODUCTION_WIRED(2026-10-26)」を1文追記。
- OPEN_ITEMS.md: OPEN-528行末に「委任_03 Phase 2 E-1〜E-6 Std/Adv全PASS(melos、実費40.31円、逸脱D-1〜D-3開示)。委任_04 Fable判定=**PRODUCTION_WIRED**(2026-10-26)。残: M-3(i)観測・聴取評価・LR新設はユーザー判断事項(非blocking)」。OPEN-516/511に「→OPEN-528でProduction採用・配線完了」1文。
- DECISION_LOG.md: 新規エントリ「2026-10-26 | FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01 委任_04(Fable判定) | Z文脈・感情付きTTS+Fallback=PRODUCTION_WIRED(Z限定・Std/Adv)。根拠=…(上記要約)。D-1 melos代替・E-4 STOP形態・D-3 RESTART_STORM残置を許容/開示。」
- OPUS_FINDINGS_LEDGER.md: OF-FZCW-M-1〜M-10/R-1/R-2をEVIDENCED→CLOSEOUT_CONFIRMED(M-3は(ii)採用・(i)未観測を注記、M-10はE-1〜E-6で充足)。前回のOF-FZFE-M-1〜M-8/R-1〜R-9(全編Trial)のうちProduction設計へ引き継いだ項目にCLOSEOUT参照を1行。
- USER_DECISION_REGISTER_01.md: OPEN-528を「判断済み→配線完了(PRODUCTION_WIRED 2026-10-26)」へ。非blocking判断候補(LR新設、M-3(i))を「Deferred」区分へ。
- REPORT_LEDGER.md: 2026-10-26 FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01=PRODUCTION_WIRED報告(本転記後Fable報告予定)。
- ACTIVE_TASK.md: 固定ヘッダで上書き(管理ID=本件 委任_04/APPROVED未配線=なし(OPEN-528→WIRED)、Chunk Std(OPEN-532、X/Y evidence中・Z実装中)、KP区分1(OPEN-529適用中)/UDR-blocking=OPEN-526・527・529(区分2)・531(Y Voice)・532(Std拡張判断は承認済みのため除外)/当日費用=2026-10-26 約260(216+Z Phase 2 40.31+KP 0.22+α)+進行中(Y Trial Cap 250・Chunk Cap 100)/1,000)。
- `docs/research/FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01/CLOSEOUT_01.md`: Gate条件チェックリスト(正式経路/後続経路/runtime evidence/test/SSOT・Git/ユーザー承認)と各証拠の所在、残Open Item。

## 実行コマンド全文

- 共有SSOT hunk限定commit: `git fetch origin`→`git show origin/main:<file> > %TEMP%\<name>_head.md`(最新HEAD基準。並行AgentのCURRENT_SPEC hunkが先にpushされていればそれを含む)→自hunk適用→`git hash-object -w`→`git update-index --cacheinfo 100644,<blob>,<file>`→`git diff --cached --stat`(自hunkのみ)。
- secret grep: `git diff --cached | findstr /R /C:"sk-[A-Za-z0-9]" /C:"AIza[A-Za-z0-9_-]" /C:"BEGIN PRIVATE KEY"`。

## SSOT追記文

上記Grep節のとおり。

## Git(明示add対象・コミットメッセージ・trailer)

- SSOT編集権: あり(CURRENT_SPEC.md[Z節のみ]/DECISION_LOG.md/OPEN_ITEMS.md/docs/pm/OPUS_FINDINGS_LEDGER.md/docs/pm/USER_DECISION_REGISTER_01.md/docs/pm/REPORT_LEDGER.md、各自hunk)。
- 明示add: 上記6ファイル(自hunk)、CLOSEOUT_01.md、delegation_log+check.json。
- commit: `git commit -m "FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01 委任_04: Fable判定PRODUCTION_WIRED(Z限定・Std/Adv)のSSOT反映(CURRENT_SPEC新節・DECISION_LOG・OPEN-528・Opus台帳CLOSEOUT・UDR・報告台帳、API 0)"`→`git push origin HEAD:main`(non-fast-forwardは`git fetch origin`→`git merge --no-edit origin/main`→再push。競合は両方残してSTOP)。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_FZCW4.md`: (0)T-0 (1)各SSOT追記行(行番号・全文) (2)自hunk証拠 (3)CLOSEOUT_01チェックリスト結果 (4)commit/push・raw URL (5)懸念。要約5行以内。