## 管理ID

`NEWS-HOOK-POLICY-DECISION-01`(初回委任)。並行タスクなし。一時ファイルは標準名`docs/pm/ACTIVE_TASK.md`/`docs/pm/RESULT_PACKET.md`を上書きしてよい(ヘッダの「APPROVED未配線」に`NEWS-ITERATIVE-R2-PRODUCTION-WIRING-01`、「UDR-blocking」に`NEWS-ENTERTAINMENT-PRODUCTION-LINE-TRIAL-01`(Ledger調達方法のユーザー判断待ち)を保持)。

## 性質/到達上限Status/禁止事項

- 性質: ユーザー正式決定のSSOT記録(DECISION_LOG/OPEN_ITEMS)+Hook関連Trial 2件のcloseoutエントリ作成。API呼出なし(¥0)。コード変更なし。
- 禁止事項: Production code・Prompt・Router・Search・Writerを変更しない。Side output Hookの配線を行わない(要件の記録のみ)。追加Hook Trialを行わない。`CURRENT_SPEC.md`は下記の誤字修正1箇所以外変更しない。`git add -A`/`stash`/`amend`禁止。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。

## ユーザー指示(原文)

(2026-09-24、管理ID `NEWS-HOOK-POLICY-DECISION-01`。全文を以下に転記し、delegation_logへそのまま保存すること)

> 今回のHook関連Trialを踏まえ、ユーザー判断を以下で正式確定する。
> ## 1. 正式表示: 当面、Newsの正式表示Hook/見出しとしては、**2回目Revision後のR2タイトルをそのまま使用する。** 別Hook Generatorの出力を正式表示には使わない。
> ## 2. 比較観測用Hook: 今後、新しいNews記事を生成する際は、**R2完成後にLunaで比較観測用Hookを1本生成する。** これはProduction正式Hookではなく、Side outputとして扱う。用途は`R2 Title vs Luna Hook`の比較観測・蓄積。以下には使わない: UI正式表示/Audio正式Hook/Production記事の合否判定/Validator判定/fallback条件。Hook生成に失敗しても、記事生成自体は成功扱いとする。
> ## 3. Hookモデル判断: `NEWS-R2-TO-HOOK-TRIAL-01`により、Topic概要→Hook より R2完成記事→Hook の方が明確に改善するEvidenceが得られた。特に、R2入力ではLunaでも採用可能〜Reference級に到達するケースが確認されたため、**Sol/TerraのProduction採用判断はいったん保留する。** 以前の「Sol第一候補」は、Topic概要→Hook方式を前提とした評価なので、現時点ではProduction model選定根拠として確定しない。
> ## 4. Status整理: Hook生成順序`R2完成記事→Hook`→`VALIDATED`。正式表示`R2 Titleを使用`→ユーザー正式決定。Luna Side Output観測`R2後にLuna Hookを1本生成し比較保存`→ユーザー正式決定。Luna Hookを正式表示へ採用→未承認。Sol/Terra Production採用→保留。
> ## 5. 記録: DECISION_LOG/OPEN_ITEMS/必要であればHook関連Trialのcloseoutへ反映。特に、Luna Hook Side Outputは「正式Hook機能」ではなく「比較観測用」であることを明確に残す。Sol/Terra比較については`DEFERRED / HOLD`として管理し、未処理USER_DECISION_REQUIREDとして毎回再掲し続けない状態へ整理してよい。
> ## 6. Production wiringについて: Side output Hookを量産Lineへ追加する場合も、Main article pathと分離/failure non-blocking/正式出力を変更しない/R2 Titleを正式表示として維持/Hook Prompt・model・outputをログ保存 とする。ただし、現在進行中のNews Writer/R2 Production Trialを邪魔しないこと。Side output実装が別変更を必要とする場合は、勝手に配線せずSTOPして報告。
> ## 7. 今後の判断材料: 今後の記事ごとに最低限 R2 Title/Luna Hook/どちらが良かったか/Hookが明確に改善したか/主語消失・答え先出し等の失敗有無 を蓄積する。十分な記事数が集まった段階で R2 Titleだけでよいか/Luna Hookを正式採用する価値があるか/Sol・Terraを再検討する必要があるか を改めて判断する。今回の判断だけを根拠に追加Hook Trialを自動実施しないこと。

## 事前指定Read一覧

- `DECISION_LOG.md`: 行440-452(索引末尾、最終索引行の書式)、Grep `^## NEWS-ITERATIVE-R2-PRODUCTION-WIRING-01`→そのエントリ全体(直近エントリ書式に倣う)、末尾(`tail -c 2000`相当、最終エントリ位置)。
- `OPEN_ITEMS.md`: 行323-324(OPEN-174/175の列構成)、末尾の最終OPEN番号(Grep `^\| OPEN-1\d\d` -o で最大番号を確認。新規は最大+1)。
- `CURRENT_SPEC.md`: 行828のみ(誤字「連鎈」の位置確認。Grep `連鎈`)。
- `NEWS-HOOK-MODEL-COMPARISON-01_REPORT.md`: Grep `§G|§H|Fable記入|Fable分類待ち`→該当行(空欄の位置)。
- `NEWS-R2-TO-HOOK-TRIAL-01_REPORT.md`: Grep `§E|§F|Fable記入|Fable分類待ち`→該当行。
- `docs/pm/PM_BRIEF.md`: 行151-175(ACTIVE_TASKヘッダ書式)。

## 事前指定Grep一覧+追記位置・更新位置の手順

1. **DECISION_LOG.md**(索引末尾へ3行、本体末尾へ3エントリ。直近エントリ書式に倣う):
   - エントリ1 `## NEWS-HOOK-POLICY-DECISION-01: News正式表示Hook=2回目revision後タイトル(R2 Title)をそのまま使用、R2完成後にLunaで比較観測用Hookを1本Side output生成(正式Hookではない)、Sol/Terra採用はDEFERRED/HOLD(ユーザー正式決定、2026-09-24)`。内容: 上記ユーザー指示1〜7を項目ごとに記録(原文引用可)。Status整理(4節)をそのまま表で。Side output要件(6節)を「配線時の必須条件」として明記し、配線は`NEWS-ITERATIVE-R2-PRODUCTION-WIRING-01`の設計判断後に別途行う(本エントリでは配線しない)。蓄積項目(7節)。関連: `NEWS-HOOK-MODEL-COMPARISON-01`/`NEWS-R2-TO-HOOK-TRIAL-01`/`TOPIC-SELECTION-CHATGPT-REPRO-01-CONT-02`(Hook部分)/OPEN-176(下記)。
   - エントリ2 `## NEWS-HOOK-MODEL-COMPARISON-01: Hook 2段生成(Topic概要→面白い見方→短いHook)のLuna/Terra/Sol同一条件比較(Reference 20素材、Reference Hook非混入)、VALIDATED(Trial)、Sol/Terra採用は保留`。内容(Fable評価の要約、REPORT §Gへも同文を記入): 条件(H3 Prompt逐語流用、effort medium、6 call、`response.model`実値6/6一致、非混入検査137文字列検出0)/結果: Fable判定 Reference級/採用可能/弱い = Luna 3/3/14、Terra 6/7/7、Sol 7/8/5(採用可能計 6・13・15 /20)/モデル別特徴: Luna=短いが見出しの疑問文化に留まる・読点で2句を継ぐ不自然形が頻出、Terra=一段深い見方への移行が最多だが素材離れ・素材外補完あり、Sol=会話的自然さと具体保持の両立だが長め・口語の癖・断定気味/3モデルともReferenceの「具体場面化」には届かず(Prompt側の余地)/cost: Luna ¥0.74(月額¥22)、Sol ¥20.41(月額¥612)、Terra単価UNKNOWN(tokenのみ記録)/latency 3モデルとも20件一括40秒前後/Fable推奨(当時)=Sol第一候補→**本日`NEWS-HOOK-POLICY-DECISION-01`によりSol/Terra採用はDEFERRED/HOLD、Luna Side output観測へ移行**/Status `VALIDATED`(Trial)、Production採用なし/dataset保存 `docs/pm/topic_selection_user_eval_dataset.json`/commit `fd0d82a1`。
   - エントリ3 `## NEWS-R2-TO-HOOK-TRIAL-01: 2回目revision完成記事(R2)を入力にしたHook生成のLuna/Terra/Sol比較(3記事)、VALIDATED(Trial)、生成順序「R2完成記事→Hook」の優位を確認`。内容(REPORT §E/§Fへも同文を記入): 条件(入力=テーマ文+R2全文のみ、Prompt逐語[REPORT §0参照]、9 call独立、`response.model`9/9一致、非混入177文字列検出0)/結果: 比較可能な2記事(AI電話・旅行荷物)×3モデル=6/6で旧方式(Topic概要→Hook)より改善。旧方式で最弱のLunaがR2入力でReference級(AI電話「AIに任せた電話、実は人間が話していたら？」)/下水道は3モデルとも失敗(R2記事の中心が比喩[洗濯機/大動脈]のためHookが比喩を持ち込み主語「下水道」が消えた。R2タイトル「"合併"するのは町じゃない？下水道の大引っ越し作戦」の方が優れる)/R2タイトルは3/3で既にHook級の材料を持つ/Q1改善=はい(6/6)、Q2具体場面=2/3で増加、Q3 Lunaで十分=R2記事が具体場面・逆転を含む場合は十分、Q4差=ほぼ消える(簡潔さのみ)、Q5原因=第一にR2記事の内容差、第二にPrompt(主語明示・答え先出し抑制の条件なし)、Model差は最小/観察: R2由来Hookは記事の答えを先に明かしがち(Reference"問いだけ"型と性格差)/cost Luna ¥0.19(1 Hook ¥0.063)、Sol ¥3.18(¥1.06)、Terra UNKNOWN、latency 1 Hook 2〜3秒/Fable推奨=生成順序はR2後、モデルはLunaで足りる可能性→**本日`NEWS-HOOK-POLICY-DECISION-01`で正式表示=R2 Title、Luna Hook=比較観測用Side outputと決定**/Status `VALIDATED`(Trial)/commit `8f2d246e`。
2. **OPEN_ITEMS.md**: 末尾(最大番号の次)へ1行追加。`OPEN-176 | **News Hook: R2 Title(正式表示)vs Luna Side output Hook(比較観測用)の蓄積とSol/Terra再検討(DEFERRED/HOLD)**(2026-09-24起票、`NEWS-HOOK-POLICY-DECISION-01`、ユーザー正式決定)`。内容: 正式表示=R2 Title/Side output=R2完成後にLunaで1本、正式Hook機能ではなく比較観測用、UI正式表示・Audio正式Hook・合否判定・Validator・fallbackに使わない、失敗しても記事成功扱い/配線時必須条件(Main article pathと分離・failure non-blocking・正式出力不変・R2 Title維持・Prompt/model/outputログ保存。別変更が必要ならSTOP)/蓄積項目(R2 Title/Luna Hook/どちらが良かったか/明確に改善したか/主語消失・答え先出し等の失敗有無)/再判断trigger(十分な記事数が集まった段階で R2 Titleだけでよいか/Luna Hook正式採用の価値/Sol・Terra再検討 を判断。追加Hook Trialを自動実施しない)/Sol/Terra比較=`DEFERRED / HOLD`(毎回のUSER_DECISION_REQUIRED再掲対象から外す)。Status列 `OPEN / MONITORING(Sol/Terra: DEFERRED/HOLD)`。関連: DECISION_LOGの上記3エントリ、`docs/pm/topic_selection_user_eval_dataset.json`、OPEN-175(復唱監視)。
3. **CURRENT_SPEC.md** 行828: 「連鎈」→「連鎖」の誤字修正のみ(他は無変更)。
4. **REPORT 2件**: `NEWS-HOOK-MODEL-COMPARISON-01_REPORT.md` §G/§Hの`[Fable記入]`/`[Fable分類待ち]`を上記エントリ2の内容で置換。`NEWS-R2-TO-HOOK-TRIAL-01_REPORT.md` §E/§Fを上記エントリ3の内容で置換。
5. Dangling Reference確認: 追記文中の管理ID・OPEN番号・path・commit SHAが実在すること(Grep/Glob/`git cat-file -e`)。

## 実行コマンド全文

```
cd C:\Users\tensh\eigo-radio
.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\NEWS-HOOK-POLICY-DECISION-01.md --json-out docs\pm\delegation_log\NEWS-HOOK-POLICY-DECISION-01.md_check.json
git cat-file -e fd0d82a1 && git cat-file -e 8f2d246e && echo SHA_OK
git status --short
git diff --stat
```

## SSOT追記文

上記「事前指定Grep一覧」1〜3のとおり(既存書式に合わせて記述)。

## Git(明示add対象・コミットメッセージ・trailer)

明示add: `DECISION_LOG.md`、`OPEN_ITEMS.md`、`CURRENT_SPEC.md`、`NEWS-HOOK-MODEL-COMPARISON-01_REPORT.md`、`NEWS-R2-TO-HOOK-TRIAL-01_REPORT.md`、`docs/pm/delegation_log/NEWS-HOOK-POLICY-DECISION-01.md`、同`_check.json`。
メッセージ: `NEWS-HOOK-POLICY-DECISION-01: News正式表示Hook=R2 Title、Luna Hookは比較観測用Side output、Sol/Terra採用はDEFERRED/HOLD(ユーザー正式決定)をDECISION_LOG/OPEN-176へ記録、Hook Trial 2件closeout、CURRENT_SPEC誤字修正、Production変更なし`
trailer: `Management-ID: NEWS-HOOK-POLICY-DECISION-01`
push後、`git rev-parse HEAD`と`git status --short`を記録。

## 報告(RESULT_PACKET項目)

0. T-0結果。
1. DECISION_LOG: 索引追加行番号(3行)、本体エントリ開始行番号(3件)。
2. OPEN-176の行番号と、Status列の文字列。
3. CURRENT_SPEC行828の修正前後(該当語のみ)。
4. REPORT 2件の記入箇所(行範囲)。
5. Dangling Reference確認結果。
6. `git status --short`(意図外混入なし)、commit SHA、push結果。
7. 一覧外Read/Grepの理由(あれば)。
8. 懸念(あれば)。
