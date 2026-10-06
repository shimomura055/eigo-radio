## 管理ID

OPEN-233-FLOOR-SELECTIVITY-OPTIMIZATION-01(委任_02a: Opus条件Aレビューの保存と設計doc §10訂正追記のみ。¥0。委任_02はAPI側中断で未着手)。並行タスクなし。git操作・SSOT編集はしない(次の委任_02bで実施)。

**作業方式(必須)**: 書き出しはすべて`Write`/`Edit`ツールで行い、Bashのheredoc/echoでファイルを書かない。1回のWrite/Editは1セクション(目安40行以内)に小分けし、長文を1回で出力しない。説明・思考は最小限。T-0の委任文保存は、本委任文のうち「## Opusレビュー本文(保存用)」セクションを除いた部分を逐語保存し、同セクションは「(保存先ファイル `docs/pm/opus_l2_review_open233_floor_selectivity_01.md` を参照)」と1行で置き換えてよい。

## 性質/到達上限Status/禁止事項

- 性質: 記録のみ。本管理IDの最終Status(Fable確定): **USER_DECISION_REQUIRED**。
- 禁止: コード変更/Prompt変更/Production変更/有料API/gold変更/設計案採否の「決定」記述/git操作/SSOT(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/`docs/pm/REPORT_LEDGER.md`/REPORT/`docs/pm/PM_GOVERNANCE.md`/`docs/pm/OPUS_FINDINGS_LEDGER.md`)・`docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md`の編集。
- 書き込み先: `docs/pm/opus_l2_review_open233_floor_selectivity_01.md`(新規)、`docs/pm/design_open233_floor_selectivity_01.md`(末尾§10追記のみ)、`docs/pm/RESULT_PACKET_FLOOR.md`(末尾に委任_02a結果を追記)、`docs/pm/delegation_log/2026-10-06_OPEN-233-FLOOR-SELECTIVITY-OPTIMIZATION-01_02a.md`(+`_check.json`)。
- 費用: ¥0。
- Opus独立技術レビューGate(PM_GOVERNANCE 11-3)該当判定: 条件A該当・レビュー実施済み(本委任はその記録)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し(本委任は上記「作業方式」の例外規定に従う)、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果をRESULT_PACKETへ1行記録する(FAILでも作業は継続)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`): TTSを伴う委任は`TTS_EXECUTION_MODE=STANDARD`を明示する。本委任はTTSなし。
T-2追記(2026-09-25、`NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02`、PM_GOVERNANCE.md 7-5): TTS実行前4点確認。本委任はTTSなし。
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`): 本委任は¥0のためCap定型文は適用対象外。

## ユーザー指示(原文)

> STOP条件: 正当6件を守りながら半分以下へ減らす見込みが立たない／新しいSafety原則の追加が必要／gold定義変更が必要／有料Trialが必要／Production仕様変更が必要。勝手に実装・Trialへ進まないこと。

## KPI provenance欄

該当なし(記録のみ)。

## Opus台帳更新

本委任では台帳を編集しない(委任_02bで実施)。

## Fable判断(doc §10と保存ファイル末尾に逐語で記す)

「Fable判断(2026-10-06、Opus条件Aレビュー後): Status=USER_DECISION_REQUIRED。根拠: (1)Sonnet案(最有望=案2+案5、根本原因=floor側の重大性判定不在)とOpus(根本原因=Stage 1 `changed_*`フラグ生成側のabsence/contra混同、案1/5は正規表現による個別当て込みで過適合、案4は正当2件を失いうる、推奨=RECLASSIFY-02区分のfloor発火条件への流用>cite-to-fire>Stage 1 prompt補正)で重要な結論が対立。(2)Fable検証【確認】: hold-out(rep30、集計md L69)で案1はneg3 gold(時期floor・LLM非BLOCKING)を非強制=見逃し(案1 6/6維持はin-sample限定)/集計scriptの`assign_cause`(L207-215)に原因(iii)分岐がなく(iii)=0は構造的/doc §5のNo.21記述は表(No.23)と不一致。(3)案1〜5・cite-to-fireのいずれも承認済み線引きOPEN-233-A1-PROD(`APPROVED_FOR_PRODUCTION`・未配線、時期のみverify・比較/主体/数字/否定は決定論維持)の変更に当たりユーザー承認事項=ユーザー指定STOP条件『Production仕様変更が必要』に該当。(4)floor側のみの精緻化で正当6件を守りつつ半減する見込みは、in-sampleでは案1/5=14件だがhold-outで1件見逃しのため未確立。Fable評価: Opusの根本原因指摘(フラグ生成側)と順序(RECLASSIFY-02評価→¥0段階0→設計確定→ユーザー承認→有料段階1)を妥当と判断し、ユーザーへ提示。Production未変更、有料Trial未実施、gold不変。」

## Opusレビュー本文(保存用)

(保存先ファイル `docs/pm/opus_l2_review_open233_floor_selectivity_01.md` を参照)

## 事前指定Read一覧

1. `docs/pm/design_open233_floor_selectivity_01.md`: Grep `^## ` →見出し一覧のみ(§10追記位置=末尾)。
2. `docs/pm/RESULT_PACKET_FLOOR.md`: 末尾10行(追記位置)。

## 事前指定Grep一覧+追記位置・更新位置の手順

- 設計doc末尾に「## §10 Opus条件Aレビュー後の訂正・Fable判断(2026-10-06)」を3回のEditに分けて追記: (a)訂正3点[§4/§5「案1は6/6維持」はin-sample限定、hold-outで案1はneg3 goldを非強制(集計md L69)/§2の(iii)=0は`assign_cause`に分岐がないための構造的0/§5のNo.21はNo.23の誤り、案2で追加確認へ回る正当はNo.5とNo.23、実際に危険はNo.5のみ]、(b)Opus推奨代替案1〜3と順序(上記(5)(6)の要約)、(c)Fable判断全文。既存本文は書き換えない。
- `docs/pm/RESULT_PACKET_FLOOR.md`末尾に「## 委任_02a結果」(T-0結果、作成ファイル、§10追記の有無)を追記。

## 実行コマンド全文

1. 上記Write/Edit(小分け)。
2. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-06_OPEN-233-FLOOR-SELECTIVITY-OPTIMIZATION-01_02a.md --json-out docs\pm\delegation_log\2026-10-06_OPEN-233-FLOOR-SELECTIVITY-OPTIMIZATION-01_02a.md_check.json`
3. git操作なし。

## SSOT追記文

なし(委任_02bで実施)。

## Git

git操作なし。SSOT編集権なし。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_FLOOR.md`末尾へ: 1. T-0結果。2. 作成・追記ファイルと行数。3. 一覧外Read理由。最終報告は3行以内。
