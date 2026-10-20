# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01 委任_04(ユーザー正式決定①②の反映=XRFR全5方式REJECTED確定Closeout+背景Fact欠落関連Open Itemの整理Close+XRFR 委任_03委任文の逐語復元)。並行タスク: 同時刻に別agentが `FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-02 委任_01`(中東記事のResearch再実行〜音声化)を実行中。衝突回避のため本委任は **OPEN-416行・REGISTER #112行・`docs/research/FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-0*/`・`er019_output/`・`user_test/`に一切触れない**。ACTIVE_TASK.mdは本委任が開始直後にヘッダを先頭追記し、以後は再編集しない。

## 性質/到達上限Status/禁止事項
- 性質: SSOT整理・記録のみ。コード・Prompt・Production変更なし。有料API呼出なし。**費用/日次: JPY0**。
- 到達上限Status: XRFR=`REJECTED(全5方式、ユーザー2026-10-20正式決定)`で正式Close。C1(XRG/B3BG)=`REJECTED`で正式Close。「Research新観点(帰属・文脈保持)」提案=`不採用(ユーザー決定②により現行維持)`。
- 禁止: 新規Open Item起票(ユーザー決定②で明示禁止)/改善Trialの再開・設計/CURRENT_SPEC.mdの仕様本文変更(今回はSSOT整理のみ、仕様は不変)/OPEN-416・REGISTER #112・中東E2E関連ファイルへの接触/`git add -A`・`-u`・`stash`・`amend`・`rebase`・`reset --hard`・`checkout -f`・branch切替・新branch作成。
- Opus独立技術レビューGate(11-3): 非該当(設計・実装変更なし、記録のみ)。
- 時間見込み: 全体20〜30分(T-0 5分/SSOT編集15分/commit 5分)。並列化: 別agent(中東E2E-02)と並列。本委任内は直列(同一SSOTファイル編集)。
- 修正範囲(D-1/11-8): 範囲外=受理面・閾値・方式の新設/拡大。範囲内=ユーザー決定の記録とOpen Item整合(承認済み仕様との矛盾是正のみ)。

## 固定ブロック
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。本委任はTTSなし。

### T-0の実施方法(重要・逐語保存)
委任文は自分で打ち直さず(要旨化はT-0 FAIL)、転写JSONLから逐語抽出して保存する:
`.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-20_FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01_委任_04.md`
Nは最新のAgent tool-use(本委任文。先頭行が「# 委任文(Fable→sonnet-worker)」で管理IDに「委任_04」を含むもの)。同時刻に別のAgent委任(中東E2E-02 委任_01)が隣接indexにあるので取り違えないこと。保存後、保存ファイルに「委任_04」「XRFR全5方式REJECTED確定Closeout」が含まれることをGrepで確認し、sha256と文字数をRESULT_PACKETに記す。

## ユーザー指示(原文・2026-10-20。本委任は§1①②が対象。§1③は別委任)
以下をそのまま `docs/pm/delegation_log/2026-10-20_FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-02_USER.md` へ逐語保存する(先頭に `# ユーザー指示原文(2026-10-20)` と `管理ID: FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-02 / 関連: FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01 委任_04` の2行を付け、その後に原文を一字一句変えず置く。文字数・sha256をRESULT_PACKETへ)。

--- 原文ここから ---
# Family X Research Trial Closeout・中東記事Production再生成

## 1. ユーザー正式決定

以下3点を確定する。

### ① Researcher改善Trial：全5方式REJECTED

- A〜Eの5方式はすべて不採用。
- 現行Researcher／検証仕様を維持する。
- 追加Trialは実施しない。
- Trial CloseoutとSSOTを正式決定に合わせて更新する。

### ② 背景Fact欠落：現行維持・Open Item管理不要

- 背景Fact欠落について、現時点では新たな改善策を導入しない。
- この問題を理由に新規Open Itemを作成しない。
- 既存Open Itemに残っている同課題も、今回の決定と整合するよう整理・Closeする。
- 今後、実際に問題が再発した場合、対策に着手するかどうかはユーザーが判断する。
- Claude／Fableの独断で改善Trialを再開しない。

### ③ 中東記事：Researchから再実行し、音声完成まで進める

**現行Production仕様のまま、Researchから再実行する。**

重要な受入条件は、**攻撃主体（Ansar Allah／フーシ派）がB3の採用Factに含まれること**。

- B3が攻撃主体を採用した場合：そのままWriter → TTS → Audio QA → Assemblyまで進め、完成音声と試聴ページを作成する。
- B3が採用しなかった場合：その試行の音声化は行わず、Researchから再実行する。
- Research再実行は、**初回1回＋再試行最大2回＝合計最大3回**。
- 3回ともB3で攻撃主体が採用されなければSTOPし、原因・各試行の結果を報告する。
- 未承認のPrompt・仕様変更、手動Fact挿入、B3の採用Factの強制変更によって条件を満たしたことにしてはならない。

## 2. 実行時の留意点

- Research → Fact Ledger → B3 → Writer → 音声化の正式Production経路を使用する。
- 各試行で、Researcherが攻撃主体をFact化したか、Ledgerに登録されたか、B3が採用したかを区別して記録する。
- B3で攻撃主体が採用された時点で、Researchの追加試行は不要。
- 既存の品質Gateはすべて維持する。攻撃主体の採用だけで記事全体を無条件PASSにしない。
- Writer本文にも攻撃主体が正確に反映されていることを確認する。
- 既存の承認済みTTS仕様、retry／fallback／regeneration／resumeを維持する。
- 原稿のユーザー事前確認待ちは設けず、条件を満たせば音声完成まで連続実行する。
- 独立作業を並列化し、不要な待機・日付分割をしない。
- 予算は既存の個別承認枠と日次1,000円（JST）を遵守する。最大3回のResearchを含め費用を管理し、上限超過が見込まれる場合は超過前にSTOPする。

## 3. 完成条件・PM Gate

- 攻撃主体がB3の正式採用Factに含まれる。
- Writer本文にも正確に反映される。
- 全必須品質GateをPASSする。
- Standard／Advancedの対象音声が完成する。
- 完成音声・全文原稿・Key Phrasesを確認できる試聴ページを公開する。
- 正式Production経路のruntime evidenceを記録する。
- CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS／Gitを整合させる。
- Fableが実行証拠を確認し、独立評価する。

## 4. 最終報告

以下を簡潔に報告する。

1. **中東記事は完成したか／試聴URL**
2. Research試行回数（最大3回）と各回の結果
3. 攻撃主体のFact化 → Ledger登録 → B3採用 → Writer反映の証拠
4. Standard／Advancedの音声品質Gate結果
5. 実費、量産単価への影響、所要時間
6. Production経路・SSOT・Git反映状況
7. 未解決事項と必要なユーザー判断（ある場合のみ）

**今回の目的は、新しいResearch仕様を探索することではなく、現行の承認済みProduction仕様で、攻撃主体を正しく含んだ中東記事を完成させること。**

品質を守りながら、完成まで最短で進めること。
--- 原文ここまで ---

## KPI provenance欄
該当なし(KPI測定なし。既存Trial結果の最終ラベル確定のみ)。

## Opus台帳更新
`docs/pm/OPUS_FINDINGS_LEDGER.md`でXRFR/XRG(C1)関連の行(Grep `XRFR|FACT-RETENTION|C1_POSITIVE|BACKGROUND-GAP`)があれば、状態を`CLOSEOUT_CONFIRMED(ユーザー決定2026-10-20①②)`へ更新する。該当行がなければ「該当なし」と報告。

## 作業内容

### A. ACTIVE_TASK.mdヘッダ先頭追記(開始直後に1回のみ)
`docs/pm/ACTIVE_TASK.md`先頭に以下の書式(PM_BRIEF「ACTIVE_TASK固定ヘッダ」準拠)で1ブロック追記(既存内容は残す):
```
# ACTIVE_TASK(委任_04 [XRFR/XRG Closeout: ユーザー決定①②反映] 先頭追記 2026-10-20)
管理ID: FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01 委任_04 / Status: CLOSEOUT_SSOT_IN_PROGRESS(全5方式REJECTED確定・背景Fact欠落=現行維持・新規Open Item禁止)
UDR-blocking: なし。APPROVED未配線: なし。STOP条件: なし。費用JPY0。
並行: FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-02 委任_01(OPEN-416/#112は向こうの担当)。報告=docs/pm/RESULT_PACKET_XRFR4.md
```

### B. XRFR Closeout(①)
1. `docs/research/FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01/TRIAL_CLOSEOUT_01.md` 末尾に「## 最終ラベル(ユーザー正式決定 2026-10-20)」節を追加: A〜E全5方式=`REJECTED`(ユーザー決定①、原文=上記delegation_logファイル名+sha)、現行Researcher/検証仕様維持、追加Trial実施しない、Production変更0、Trial実費合計(既存Closeoutの実費行から転記、出典明記)。
2. `OPEN_ITEMS.md` OPEN-427行(Grep `^OPEN-427 \|` または `OPEN-427 \| \*\*FAMILY-X-RESEARCH-FACT-RETENTION`): 行頭Status角括弧を `[CLOSED・REJECTED(全5方式、ユーザー2026-10-20正式決定①)・Production変更0]` に置換し、行末に `【2026-10-20 Close】ユーザー決定①: A〜E全方式REJECTED・現行仕様維持・追加Trialなし(原文=docs/pm/delegation_log/2026-10-20_FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-02_USER.md §1①)。` を追記。履歴本文は削除しない。
3. `docs/pm/USER_DECISION_REGISTER_01.md` #127行(Grep `^- #127\(`): 区分を「判断済み 2026-10-20(全5方式REJECTED・現行維持・追加Trialなし)」へ更新(行頭の区分表記は既存行の書式に合わせる)。

### C. 背景Fact欠落関連Open Itemの整理Close(②)
原則: 新規Open Itemは作らない。既存行の整理のみ。
1. `OPEN_ITEMS.md` OPEN-425行(XRG根本原因調査): Status角括弧を `[CLOSED・原因特定済み(Researcher claim化段階で攻撃主体が脱落=帰属・背景保持の仕様空白)・改善策導入せず現行維持(ユーザー2026-10-20決定②)・C1=REJECTED・Research新観点提案=不採用]` へ置換し、行末に `【2026-10-20 Close】ユーザー決定②: 背景Fact欠落は現時点で新たな改善策を導入せず現行維持、本課題を理由とする新規Open Item起票禁止、再発時の対策着手はユーザー判断。Research新観点(帰属・文脈保持)の採用提案は不採用(XRFR方式Aで効果なし=OPEN-427)。` を追記。
2. `OPEN_ITEMS.md` OPEN-423行(B3BG/C1): Status角括弧を `[CLOSED・C1=REJECTED(陽性対照でも背景補完0/12、Fable確定)・B3正式仕様不変・ユーザー2026-10-20決定②で現行維持確定]` へ置換し、行末に `【2026-10-20 Close】C1最終ラベル=REJECTED。ユーザー決定②により背景Fact欠落への改善策は導入せず、本件Close。中東記事の扱いはOPEN-416(E2E-02)へ移管。` を追記。
3. `docs/pm/USER_DECISION_REGISTER_01.md` #123行・#125行: 区分を「判断済み 2026-10-20(決定②: 現行維持・C1 REJECTED・新規Open Item不要)」へ更新。**#112行は触らない**(別委任担当)。
4. `docs/research/FAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01/C1_POSITIVE_CONTROL_CLOSEOUT_01.md` 末尾に「## 最終ラベル(2026-10-20)」節: C1=REJECTED(Fable確定、ユーザー決定②で現行維持確定)、Research新観点提案=不採用、以後の改善Trial再開はユーザー判断のみ。
5. OPEN_ITEMS.md内に他にも「背景Fact欠落/背景補完/Research新観点」を未決として残している行がないかGrep(`背景Fact|背景補完|帰属・文脈保持|Research新観点`)し、OPEN-416/423/425/427以外にヒットした行はRESULT_PACKETに列挙するだけにして編集しない(Fableが判断)。

### D. DECISION_LOG.md追記
既存エントリ書式(Grep `^## ` で直近エントリの書式を確認)に合わせ、最新エントリとして1件追加:
タイトル `FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01 / FAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01 Closeout(ユーザー正式決定2026-10-20 ①②)`。本文: ①A〜E全5方式REJECTED・現行Researcher/検証仕様維持・追加Trialなし/②背景Fact欠落=現時点で改善策導入せず現行維持・新規Open Item起票禁止・既存OPEN-423/425/427をClose・再発時の対策着手はユーザー判断・Claude/Fable独断でのTrial再開禁止/C1=REJECTED/Research新観点提案=不採用/Production変更0/原文所在(ファイル名・sha256)。索引行がある形式なら索引も更新。

### E. REPORT_LEDGER.md
`docs/pm/REPORT_LEDGER.md`に本委任の行を既存書式で追記(管理ID・日付・内容=Closeout SSOT・費用JPY0・RESULT_PACKET_XRFR4)。

### F. XRFR 委任_03委任文の逐語復元(housekeeping)
`docs/pm/delegation_log/` でXRFR 委任_03のファイル(Grep `委任_03` かつ `FACT-RETENTION`)を特定。要旨版(T-0 FAIL)なら、同じextractツールで転写JSONLから該当Agent prompt(管理IDに「FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01 委任_03」を含み「方式B検索込み」等を含むもの。indexは `--index` を変えて探索するか、JSONLをGrepしてAgent tool-use行を特定)を逐語抽出し、要旨版を `*_SUMMARY_SUPERSEDED.md` へrenameせず**別名で残したまま**(`git mv`不要、既存ファイルは末尾に「※本ファイルは要旨版。逐語版=<新ファイル名>」を1行追記)、逐語版を `2026-10-20_FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01_委任_03_VERBATIM.md` として保存。sha256・文字数・抽出index・逐語版と要旨版の差(1行)をRESULT_PACKETへ。見つからなければ探索手順と結果を報告(創作禁止)。

## 事前指定Read/Grep一覧
- `OPEN_ITEMS.md`: Grep `^OPEN-(423|425|427) \|` → 該当行のみRead(長行。全文Read禁止)。
- `docs/pm/USER_DECISION_REGISTER_01.md`: Grep `^- #(123|125|127)\(` → 該当行。
- `DECISION_LOG.md`: Grep `^## ` head 5 → 直近エントリ1件の範囲Read(書式確認のみ)。
- `docs/pm/REPORT_LEDGER.md`: 末尾20行。
- `docs/research/FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01/TRIAL_CLOSEOUT_01.md`: Grep `実費|JPY` で費用行、末尾30行。
- `docs/research/FAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01/C1_POSITIVE_CONTROL_CLOSEOUT_01.md`: 末尾20行。
- `docs/pm/OPUS_FINDINGS_LEDGER.md`: Grep上記パターン。
- `docs/pm/RESULT_PACKET_XRFR3.md`: 費用行(Grep `JPY`)のみ。

## 実行コマンド全文
- T-0: 上記extractコマンド + `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-10-20_FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01_委任_04.md --json-out docs/pm/delegation_log/2026-10-20_FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01_委任_04_check.json`
- secret scan: `.venv\Scripts\python.exe tools/secret_scan_01.py --staged`(hits=0必須)
- sha256: `Get-FileHash <path> -Algorithm SHA256`

## Git(明示add対象・SSOT編集権あり)
本委任はOPEN_ITEMS.md(OPEN-423/425/427行のみ)・DECISION_LOG.md・USER_DECISION_REGISTER_01.md(#123/#125/#127のみ)・REPORT_LEDGER.md・上記docs/research 2ファイル・delegation_log 3ファイル・OPUS_FINDINGS_LEDGER.md(該当時)の編集権を持つ。CURRENT_SPEC.mdは編集しない。
並行agentとの共有プロトコル: 編集直前に`git status --porcelain <file>`と該当行の再Grepを行い、自分の担当行だけを編集し、編集後すぐに`git add <明示パス>`→commit。`index.lock`が存在したら30秒待って再試行(削除しない)。commit前に`git diff --cached --stat`で自分のファイルだけがstageされていることを確認(他agentの変更が混ざっていたら`git restore --staged <他のファイル>`で外す)。
commit 2回: (1) delegation_log 3ファイル+ACTIVE_TASKは除外(gitignore) `FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01 委任_04: ユーザー指示原文(E2E-02_USER)保存+委任_03逐語復元+T-0` (2) SSOT一式 `FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01 委任_04: ユーザー決定①②反映(XRFR全5方式REJECTED確定・OPEN-423/425/427 Close・REGISTER #123/#125/#127判断済み・DECISION_LOG)`。push先は直近commit 6e1efec39と同じ(`git branch --show-current`と`git log -1 --format=%D`で確認、branch切替・新規作成禁止)。push後、変更ファイルのraw.githubusercontent.com URLを列挙。

## 報告(docs/pm/RESULT_PACKET_XRFR4.md へ上書き作成)
1. T-0結果(保存パス・sha256・文字数・check PASS/FAIL reasons)。2. ユーザー原文保存(パス・文字数・sha256)。3. 編集したSSOT行の前後(Status角括弧の新旧)。4. C-5のGrepヒット一覧(編集せず)。5. 委任_03逐語復元の結果。6. commit hash・push結果・raw URL。7. 費用JPY0の確認。8. 判断候補(あれば)。Fableが最終判定する。