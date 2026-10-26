## 管理ID

PM-SSOT-SYNC-11(ユーザー決定2026-10-26「Family XYZ TTS Retry・Fallback・Local Rewrite統一・Production Wiring」APPROVED_FOR_PRODUCTIONの受領記録と、それにより解決したユーザー判断事項(OPEN-528(1)/OPEN-536)の更新。API 0・JPY0)。並行タスク衝突確認: 並行Agent 2件(KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01 委任_02、TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_01[設計・read-only])。いずれもSSOT編集権なし。**SSOT編集権は本Agentのみ**(`OPEN_ITEMS.md`/`DECISION_LOG.md`/`docs/pm/REPORT_LEDGER.md`/`docs/pm/USER_DECISION_REGISTER_01.md`/`docs/pm/ACTIVE_TASK.md`)。`CURRENT_SPEC.md`は本委任では編集しない(統一仕様の正式反映は配線後)。pathspec付きcommit。git index.lock競合時は10秒待って再実行(最大3回)。

## 性質/到達上限Status/禁止事項

- 性質: SSOT転記。到達上限Status: 転記完了。
- 禁止: Production/コード変更、API支出、`CURRENT_SPEC.md`編集、`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・`git checkout -- <file>`。編集前に`git diff HEAD --stat -- <path>`で差分なしを確認(差分があればHEAD blob+自hunk方式)。
- 費用/日次: JPY0。
- Opus独立技術レビューGate(11-3): 非該当(転記)。
- 時間見込み: 約25分。並列化: なし。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSなし)
T-2追記(2026-09-25、`NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02`、PM_GOVERNANCE.md 7-5、予算逸脱再発防止): TTSを伴う委任は実行前に(1)差分[変更箇所のみ]再生成が対象コード上で実際に可能か確認、(2)既存の音声再利用キャッシュの有無を確認、(3)`--budget`/`--budget-jpy`等が存在すればタスク固有の承認上限に合わせて明示、(4)想定外の全再生成と判明した場合はAPI実行前にSTOPし報告、の4点を必須とする。

T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-26_PM-SSOT-SYNC-11_DELEGATION_01.md` をN=669から順に試し、先頭が「## 管理ID」+「PM-SSOT-SYNC-11」で始まるものを採用(`--index -1`不可)。

## ユーザー指示(原文)

ユーザー決定原文は並行Agent(TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_01)が`docs/pm/delegation_log/2026-10-26_TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01_USER.md`へ保存する(作成済みならGrepで引用。未作成なら以下の要点逐語を使う):
- 「**Status：APPROVED_FOR_PRODUCTION** **到達目標：対象Family・音声部位すべてでPRODUCTION_WIRED**」
- 基本フロー: 「1. 通常StyleでTTS① → NG 2. 同じStyleでTTS② → NG 3. **180秒（3分）待機** 4. Fallback Styleに切り替えてTTS③ → NG 5. LRありの場合：問題箇所を1回だけ書き換え、①〜④と同じ3回構成で再生成する 6. LR後もNGならHuman Review／STOP 7. LRなしの場合：最初のTTS③がNGならHuman Review／STOP」「LRあり：最大6回の品質再生成、待機最大2回＝計360秒。LRなし：最大3回の品質再生成、待機最大1回＝180秒。LRは最大1回。LR後に再度LRへ入る再帰処理は禁止。」
- 部位別表: XYZ Std英語本文・Comment等=短文Style/LRあり/6回、XYZ Adv英語=短文Styleを新たに適用/LRあり/6回、Zセリフ(文脈・感情方式)=従来Dialogue Style/LR現状なし/3回、XYZ Std日本語=日本語短文Style/LRなし/3回、KP英語=ENGLISH_LOCK/LRなし/4回維持(通常2回NG後に180秒待機)、Adv KP英語解説(音声が存在する経路)=短文Style適合性確認・不可なら同一Style/LR現状なし/3回、Z冒頭英語=短文Style/LRあり/6回。
- §3「**Family Zのセリフ**：文脈・感情Styleを2回、3分待機後に従来Dialogue Styleを1回。LRは今回追加しない。」「**Family Zの冒頭英語**：未分類によるFallback・LR未適用を解消し、共通仕様を適用する。」
- §4「既存のLR再入（OPEN-376）とStyle脱落（OPEN-312等）を、今回の共通化で解消する。」「ASR一致でも繰り返し・言い淀みQAでNGとなるケースを適切に扱い、LRが適用不可能な場合の無益な後続処理を避ける。ただし、品質NGの再試行フローや180秒待機を勝手に省略しない。」「日本語・Key Phrase英語・Zセリフ等、今回LRなしとした部位へ独断でLRを追加しないこと。」
- §5「旧10分待機、旧3回／4回の数え方、旧LR後1回、Advの技術エラー時のみのStyle切替など、今回置換された条件が正式経路やValidatorに残らないよう確認する。」「モデルやVoiceそのものの変更は今回のScopeに含めない。」
- §8「ユーザーが決定済みの仕様について、再承認を求めないこと。」

## Fable判定(転記する内容)

- 新規OPEN(OPEN-540想定、11-8分類=承認済み仕様のProduction配線[修正へ進む]): 「TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 | Family XYZ TTS Retry・Fallback・LR統一 | Status=APPROVED_FOR_PRODUCTION(2026-10-26)_DESIGN_IN_PROGRESS | 到達目標=全Family・全部位PRODUCTION_WIRED | 要点=①②同一Style→180秒→③Fallback Style、LRあり部位はLR1回+同じ3回構成(最大6回・待機最大2回)、LRなし部位は3回(KP英語のみ4回維持+通常2回後180秒)、Zセリフ=ctx2→180秒→従来Dialogue 1(LRなし)、Z冒頭英語=共通仕様へ是正、Adv英語=3回目に短文Style、旧600秒・旧回数・LR後1回・Adv技術エラー時のみ切替は撤去、OPEN-376/312を共通化で解消 | 工程=設計(委任_01)→Opus条件A→実装→Family別runtime evidence→Fable受入→SSOT | 関連=OPEN-376/312/274/528/536/538/525」。
- OPEN-528 Deferred(1)(Zセリフ LR新設要否): **ユーザー決定(2026-10-26)=今回LRは追加しない(現状維持)** → USER_DECISION_REQUIRED解除・CLOSED(決定)。cooldownは600→180秒へ(統一案件で実装)。
- OPEN-536(非ASR起因NG→cooldown後LR不発→HR): **ユーザー決定(2026-10-26)=品質NGの再試行フロー・180秒待機は省略せず、LRが適用不可能な場合の無益な後続処理を避ける(③NG後にLR適用可否を判定し不可なら即HR)** → USER_DECISION_REQUIRED解除、「修正へ進む(統一案件OPEN-540で実装)」へ。
- OPEN-376(LR再入)/OPEN-312(Style脱落)/OPEN-538(Z topic_intro_en): 統一案件(OPEN-540)で解消予定と追記。
- OPEN-537(Y Style profile適用時期): 変更なし(ユーザー判断待ち継続。統一案件のScope外=「Voiceの既定Styleそのものを無断変更しない」)。
- DECISION_LOG 1件: ユーザー決定の要点(上記逐語)+Fableの工程計画+解決したUDR 2件。
- UDR: UDR-TRA-1(Zセリフ LR)=決定済み(現状維持)、UDR-TRA-2(非ASR起因NG)=決定済み(待機省略せず・LR不可なら即HR)、UDR-TRA-3(Y Style)=継続。新規UDRなし(再承認を求めない)。
- REPORT_LEDGER: ユーザー決定受領(TTS統一)、TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_01開始、本件。
- ACTIVE_TASK: 上書き(並行=KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01 委任_02(Cap40)、TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_01(JPY0)→Opus→委任_02、UDR-blocking=OPEN-526・527・529(配線中)・534・537・539(試聴)、STOP条件=猿の手run_fzcw_e1_01残置、QDC=当日約552円+KP≤40/1,000。TTS統一evidenceは見積後に承認区分判定[300円超なら事前費用承認])。

## KPI provenance欄

該当なし。

## Opus台帳更新

該当なし(統一案件のOpus起票はレビュー後)。

## 事前指定Read一覧

- `docs/pm/ACTIVE_TASK.md` 全文
- `docs/pm/delegation_log/2026-10-26_TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01_USER.md`(存在すれば): Grep `APPROVED_FOR_PRODUCTION|180秒|LRは今回追加しない|省略しない|再承認` → ±2

## 事前指定Grep一覧+追記位置・更新位置の手順

- `OPEN_ITEMS.md`: Grep `^\| OPEN-5[34][0-9]` → 最大番号(OPEN-539まで既存想定)→ 新規OPEN-540。Grep `OPEN-528` → Deferred(1)の更新。Grep `OPEN-536|OPEN-376|OPEN-312|OPEN-538|OPEN-537` → 上記のとおり追記/更新。
- `DECISION_LOG.md`: 本日末尾に1件。
- `docs/pm/USER_DECISION_REGISTER_01.md`: Grep `UDR-TRA-1|UDR-TRA-2|UDR-TRA-3` → 更新。
- `docs/pm/REPORT_LEDGER.md`: 末尾に3行。
- `docs/pm/ACTIVE_TASK.md`: 上書き。

## 実行コマンド全文

- `git diff HEAD --stat -- OPEN_ITEMS.md DECISION_LOG.md docs/pm/REPORT_LEDGER.md docs/pm/USER_DECISION_REGISTER_01.md`(編集前)
- `git diff --cached --stat`
- Secret grep: `git diff --cached -- OPEN_ITEMS.md DECISION_LOG.md docs/pm/REPORT_LEDGER.md docs/pm/USER_DECISION_REGISTER_01.md | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## SSOT追記文

上記Fable判定の文言とユーザー逐語を使う。

## Git(明示add対象・コミットメッセージ・trailer)

- add対象: `OPEN_ITEMS.md`、`DECISION_LOG.md`、`docs/pm/USER_DECISION_REGISTER_01.md`、`docs/pm/REPORT_LEDGER.md`、`docs/pm/delegation_log/2026-10-26_PM-SSOT-SYNC-11_DELEGATION_01.md`(+`_check.json`)。pathspec付きcommit。
- commit message: `PM-SSOT-SYNC-11: TTS Retry/Fallback/LR統一 ユーザー決定(APPROVED_FOR_PRODUCTION)受領=OPEN-540起票、OPEN-528(1)/536はユーザー決定で解決、OPEN-376/312/538は統一案件へ統合、UDR更新(API 0)`
- trailer: `Delegation: PM-SSOT-SYNC-11/01`
- push: `git push origin HEAD:main`(non-ffなら`git fetch origin`→`git merge --no-edit origin/main`→push。競合はSTOPし報告)。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_SSOT11.md`: (0)T-0、(1)編集前状態、(2)更新行、(3)`git diff --cached --stat`、(4)commit hash・push・raw URL(OPEN_ITEMS.md/DECISION_LOG.md/USER_DECISION_REGISTER_01.md)、(5)必須4行+「判定整合: 重大NG=<なし|あり>」、(6)一覧外Read。末尾に要約5行以内。