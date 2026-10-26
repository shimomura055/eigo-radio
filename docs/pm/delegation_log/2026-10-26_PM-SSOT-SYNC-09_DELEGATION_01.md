## 管理ID

PM-SSOT-SYNC-09(TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01 委任_02 統合報告の結果とFable判定のSSOT反映。API 0・JPY0)。並行タスク衝突確認: 並行Agent 2件(KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01 委任_01、FAMILY-Y-REDELIVERY-FEE-FINAL-PUCK-01 委任_02)。いずれもSSOT編集権なし。**SSOT編集権は本Agentのみ**(`OPEN_ITEMS.md`/`DECISION_LOG.md`/`docs/pm/REPORT_LEDGER.md`/`docs/pm/USER_DECISION_REGISTER_01.md`/`docs/pm/ACTIVE_TASK.md`)。`CURRENT_SPEC.md`は本委任では編集しない(調査結果の仕様反映はユーザー判断後)。git index.lock競合時は10秒待って再実行(最大3回)。pathspec付きcommit。

## 性質/到達上限Status/禁止事項

- 性質: SSOT転記。到達上限Status: 転記完了。
- 禁止: Production/コード変更、API支出、`CURRENT_SPEC.md`編集、`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・`git checkout -- <file>`。編集前に`git diff HEAD --stat -- <path>`で差分なしを確認(差分があればHEAD blob+自hunk方式)。
- 費用/日次: JPY0。
- Opus独立技術レビューGate(11-3): 非該当(転記)。
- 時間見込み: 約35分。並列化: なし。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSなし)
T-2追記(2026-09-25、`NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02`、PM_GOVERNANCE.md 7-5、予算逸脱再発防止): TTSを伴う委任は実行前に(1)差分[変更箇所のみ]再生成が対象コード上で実際に可能か確認、(2)既存の音声再利用キャッシュの有無を確認、(3)`--budget`/`--budget-jpy`等が存在すればタスク固有の承認上限に合わせて明示、(4)想定外の全再生成と判明した場合はAPI実行前にSTOPし報告、の4点を必須とする。

T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-26_PM-SSOT-SYNC-09_DELEGATION_01.md` をN=664から順に試し、先頭が「## 管理ID」+「PM-SSOT-SYNC-09」で始まるものを採用(`--index -1`不可)。

## ユーザー指示(原文)

該当なし(Fable判定の転記。調査指示原文=`docs/pm/delegation_log/2026-10-26_TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01_USER.md`、後続指示§3・§4=`…FAMILY-Y-VOICE-TABLE-PRODUCTION-WIRING-01_USER.md`)。

## Fable判定(転記する内容)

**TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01 = AUDITED(2026-10-26、調査完了。Production変更なし)**。結論=「大部分は整合、完全ではない」。星取表①49行(LR○22/×26/TTSなし1、総4=28/総3=20、A36/B2/C10)、②22行(A12/B1/C7/TTSなし2)、findings 23件(U-01〜U-23)。成果物=`docs/research/TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01/{REPORT_01,Y_F01_STYLE_PROFILE_CHECK_01,FAMILY_X_01,FAMILY_Y_01,FAMILY_Z_01,COMMON_CORE_01}.md`、`consolidated_01.json`(commit 7e2351b8c/60e48c2ce/b1ef7ee2f/3ce145a6a)。

Fable 11-8判定(転記):
- **U-05 Zセリフ(dialogue)のLRなし** → OPEN-528 Deferred(1)を **USER_DECISION_REQUIRED** へ(事実: ユーザー承認による除外ではなく、既存LRが無い状態でFable判断J-1がHR/STOP直行を選択[DESIGN_02.md:6,61]、Opus同調[OPUS_REVIEW_01.md:63-70]。ユーザー原文FZ:30,32,36,136は「NG→既存のLocal Rewrite処理へ」。ユーザーは2026-10-26後続指示で状態を認識し採否を保留。ctx導入後3回NG実績0、legacy時代3回STOPPED 6件、LRで救えたかは未検証。選択肢=A LR新設[3回NG後に書換え→再TTS1回、Opus条件A、設計案DESIGN_01.md:122]/B 現状維持[HR/STOP])。Fable推奨=**B 現状維持(当面)**(理由: ctx方式導入後に3回NGの実績が0件で便益が未確認、セリフの書換えは話者の台詞自体を変えるため品質リスクがnarratorより大きい。実績が出た時点で再検討)。
- **U-03 非ASR起因NG(disfluency/Repetition QA単独NG)でcooldown 600秒後にLRが`NO_NG_SPAN`で不発→HR**(X/Y/Z横断。実走: X Adv comment_4 2026-10-26、Y Voice 1 Algieba旗率72%) → 新規OPEN **USER_DECISION_REQUIRED**(選択肢=a 現状維持/b 非ASR起因NGはcooldown省略[2026-09-26「固定10分・短縮禁止」決定と衝突]/c LRを非ASR起因NGへ拡張[新仕様・未検証])。Fable推奨=**b'=「LRの発動可否を判定してからcooldownに入る」順序是正**(事実: 現行はcooldown→LR判定の順で、LR不発が確定している場合も10分待つ。これは「最終attempt前cooldown」の趣旨[API負荷緩和・再生成品質]を変えずに待ち時間だけを省く案だが、2026-09-26決定の文言「固定10分」との整合はユーザー判断)。推奨理由=Delivery短縮(1件10分)で品質影響なし。
- **U-15 Y runnerのStyle profile `default`固定**(設計DESIGN_01.md:84・台帳SPEC_LEDGER_03.md:60 YL-A01=APPLY・DEV Trial er110:40は`fx_20261017`継承、Production runner `er121_family_y_runner_01.py:37`は`default`、承認記録・除外記録とも0件、runtime run_01は基底6-role Style・PD06/S3/E1/K2/P8-KP/P7未使用) → 新規OPEN(11-8=**B疑い・修正へ進む候補・重要度高**)。Fable判定=**B(仕様と実装の乖離)として是正対象。ただし適用時期はユーザー判断**(redelivery_fee完成版は現行runner[default]で制作中=現行公開版と同条件。是正すると全Y音声の再生成が必要[Voice 2/3再利用不成立、run_01 tts実績約28円+再試行]。選択肢=①次のY新規記事から是正[redelivery_fee完成版はdefaultのまま]/②redelivery_fee完成版も是正して再生成)。Fable推奨=①(理由: ユーザーが試聴済みの現行版と同条件を保ち、Voice 1変更の効果を単独で評価できる。費用も最小)。
- **U-01 LR再入(OPEN-376 D-B4)**: 仕様「2回目LRなし」(ITEMS23_REWRITE_CONDITION_AND_SCRIPT_REF_01.md:28)に対し実装はLR再TTSが`enable_connected_speech_equivalence_layer=True`のまま`__wrapped__`を呼び再入可(深さ2の実記録3件) → Fable 11-8判定=**B(承認済み仕様との不一致)・修正へ進む**(再入ガード1箇所=意味変更ではない)。OPEN-376のラベルを「仕様判断要」→「修正へ進む(Fable判定2026-10-26)」へ。
- **U-06 Z `topic_intro_en`が5 roleに解決されずcooldown・LR非適用**(B・低) → 新規OPEN(修正へ進む)。
- **U-02 LR再TTSのStyle脱落**(OPEN-312/274) → 既存へ追記のみ(Deferred継続)。
- **U-04 HR queue登録契機の不整合**(OPEN-376 D-B5+Y-F04) → OPEN-376へ追記。
- **U-12 cooldownがSTOP sentinelを見ない(単発sleep)** → OPEN-376へ「確認項目」として追記(SDK入口guardの有無確認後に起票要否)。
- **U-16 Y GateのLR成功BLOCK**(C) → OPEN-312へ追記。
- **U-08 Adv KP英語解説・shell固定英語のLRなし**(C・低・記録済みrunで失敗0) → OPEN-528へ「LR対象外の記録なし部位」として1行追記(新規起票なし)。
- **U-10/U-11 旧記述残存**(CURRENT_SPEC:2873/2954/2963、er121_audio:17、er019:1212-1213) → OPEN-532へ追記(文書同期は次回CURRENT_SPEC編集時)。
- A(承認済み合理的差異)として確定: 日本語LRなし(2026-10-15:148,160)、KP phrase LRなし(2026-09-26・2026-10-15:161)、Std「標準2+minimal1」vs Adv「同一Style3回」(2026-10-21決定)、X runnerにRUN_LOCK/RESTART_STORMなし(PM_GOVERNANCE 26-4)。
- 2026-10-19決定(「両ASR合意」削除・初回→最大2回再生成→なおNGならRewrite)はX/Y/Z英語ナレーション全部位で実装一致。実行コード残存0件。
- 用語統一: F-Tech(技術救済)、F-Style(Std/日本語3回目)、F-Prompt(Z dialogue ctx→legacy)。

## KPI provenance欄

該当なし(転記。出典=`docs/pm/RESULT_PACKET_TRA2.md`、`REPORT_01.md` §5/§8/付録B)。

## Opus台帳更新

該当なし。

## 事前指定Read一覧

- `docs/pm/RESULT_PACKET_TRA2.md`: Grep `OPEN起票|付録B|^\(9\)|^## 10` → ±40(起票・追記文案)
- `docs/research/TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01/REPORT_01.md`: Grep `付録B|## 5|U-0[1-6]|U-1[256]` → 該当行±5(文案の正確な表現)
- `docs/pm/ACTIVE_TASK.md` 全文

## 事前指定Grep一覧+追記位置・更新位置の手順

- `OPEN_ITEMS.md`: Grep `^\| OPEN-53[0-9]` → 最大番号(OPEN-535まで既存)→ 新規OPEN-536(U-03、USER_DECISION_REQUIRED)、OPEN-537(U-15、修正へ進む候補・高・適用時期ユーザー判断)、OPEN-538(U-06、修正へ進む・低)。Grep `OPEN-528` → Deferred(1)をUSER_DECISION_REQUIRED(Fable推奨B)へ+U-08追記。Grep `OPEN-376` → ラベル変更(U-01)+U-04/U-12追記。Grep `OPEN-312` → U-02/U-16追記。Grep `OPEN-274|OPEN-525|OPEN-533` → 付録Bの追記文案を転記。Grep `OPEN-532` → U-10/U-11追記。
- `DECISION_LOG.md`: 本日末尾に1件(AUDITED+Fable 11-8判定一覧+推奨)。
- `docs/pm/USER_DECISION_REGISTER_01.md`: 新規エントリ3件(①Zセリフ LR新設要否[推奨B現状維持]、②非ASR起因NGの扱い[推奨b'順序是正、2026-09-26決定との整合確認]、③Y Style profile是正の適用時期[推奨①次記事から])。各々=決めること/背景/選択肢と影響/推奨と根拠/参照path。
- `docs/pm/REPORT_LEDGER.md`: TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01=Fable報告予定(2026-10-26)、本件。
- `docs/pm/ACTIVE_TASK.md`: 上書き(並行=KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01 委任_01(JPY0)、FAMILY-Y-REDELIVERY-FEE-FINAL-PUCK-01 委任_02(Cap30)、UDR-blocking=OPEN-526・527・529(区分2は採用済み→配線中に更新)・534・536・537・528(1)、STOP条件=猿の手run_fzcw_e1_01残置、QDC=当日約552円+進行中≤36/1,000)。

## 実行コマンド全文

- `git diff HEAD --stat -- OPEN_ITEMS.md DECISION_LOG.md docs/pm/REPORT_LEDGER.md docs/pm/USER_DECISION_REGISTER_01.md`(編集前)
- `git diff --cached --stat`
- Secret grep: `git diff --cached -- OPEN_ITEMS.md DECISION_LOG.md docs/pm/REPORT_LEDGER.md docs/pm/USER_DECISION_REGISTER_01.md | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## SSOT追記文

上記Fable判定の文言+RESULT_PACKET_TRA2/REPORT_01付録Bの文案を使う。

## Git(明示add対象・コミットメッセージ・trailer)

- add対象: `OPEN_ITEMS.md`、`DECISION_LOG.md`、`docs/pm/USER_DECISION_REGISTER_01.md`、`docs/pm/REPORT_LEDGER.md`、`docs/pm/delegation_log/2026-10-26_PM-SSOT-SYNC-09_DELEGATION_01.md`(+`_check.json`)。pathspec付きcommit。
- commit message: `PM-SSOT-SYNC-09: TTS Retry/Fallback/LR棚卸しAUDITED反映(Fable 11-8判定: OPEN-528(1)/新規OPEN-536=UDR、OPEN-537 Y Style profile=B是正候補、OPEN-538、OPEN-376=修正へ進む、OPEN-312/274/525/533/532追記、UDR 3件、API 0)`
- trailer: `Delegation: PM-SSOT-SYNC-09/01`
- push: `git push origin HEAD:main`(non-ffなら`git fetch origin`→`git merge --no-edit origin/main`→push。競合はSTOPし報告)。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_SSOT9.md`: (0)T-0、(1)編集前状態、(2)更新行(ファイル:行)、(3)`git diff --cached --stat`、(4)commit hash・push・raw URL(OPEN_ITEMS.md/DECISION_LOG.md/USER_DECISION_REGISTER_01.md)、(5)必須4行+「判定整合: 重大NG=<なし|あり>」、(6)一覧外Read。末尾に要約5行以内。