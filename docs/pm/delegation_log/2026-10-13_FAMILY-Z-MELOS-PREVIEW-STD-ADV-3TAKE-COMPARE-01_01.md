## 管理ID

FAMILY-Z-MELOS-PREVIEW-STD-ADV-3TAKE-COMPARE-01 委任_01(初回)。前身: FAMILY-Z-STANDARD-PREVIEW-X-ALIGNMENT-01(commit 3168bbda/296931e4、`er070_*`)。並行タスク: FAMILY-XZ-M2P0-N01-PRODUCTION-WIRING-01 委任_02(`er030_*`/`er019_*`/`er063_*`/Coffee run dir/SSOT編集中の可能性)が稼働中。本委任はSSOT編集権**あり**ただし`OPEN_ITEMS.md`のOPEN-338行・`DECISION_LOG.md`末尾・`docs/pm/USER_DECISION_REGISTER_01.md`・`docs/pm/REPORT_LEDGER.md`に限定(`CURRENT_SPEC.md`/`PM_GOVERNANCE.md`は編集しない)。SSOT編集は最終工程で、直前に`git status --porcelain`で他agentの未commit変更を確認し、あれば60秒×5回待ち、残っていても自分の変更行のみ追記・自分の変更ファイルのみ明示add。一時ファイル: `docs/pm/ACTIVE_TASK_FZP3.md`/`docs/pm/RESULT_PACKET_FZP3.md`。出力: `er072_output/melos_preview_std_adv_3take_01/`、script `er072_melos_preview_std_adv_3take_01.py`。`.git/index.lock`存在時は30秒待ち×3回、commit前に`git fetch origin && git merge --ff-only origin/main`(不可なら`git pull --no-rebase`、conflict時は両追記保持)。

## 性質/到達上限Status/禁止事項

- 性質: Trial(比較生成のみ)。Standard 3 take+Advanced 3 take=LLM 6 call。
- 到達上限Status: `VALIDATED`/`REJECTED`/`USER_DECISION_REQUIRED`。Production採用・反映は禁止(結果報告でSTOP)。
- 費用: 上限¥5(Guardrail。gpt-6-luna 6 call×約¥0.15=約¥0.9見込み、単価出典`er006_model_routing_pricing_coverage_test_01.py` L50-52、USD/JPY=160)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。6 callを超える生成(lint retryを含む再生成)は禁止: lint NGのtakeはNGのまま記録し再生成しない。
- 禁止: 両Promptの一切の変更(Std=`er070_output/family_z_std_preview_x_alignment_01/prompt_after_01.txt`相当の統一Prompt[er070 scriptの組立関数を再利用、sha一致を検証]、Adv=現行`b1s.PREVIEW_ROLE`経路をProduction同一条件で)、Prompt調整・改善Trial、記事本文・Comment・KP再生成、TTS・音声化、Family Zの記事再生成・音声化(STOP維持)、Production code・Prompt編集、既存出力の再利用(6 takeは全て新規生成)、`git add -A`/`-f`、amend/rebase/force push、stash/clean/`reset --hard`/`checkout -f`、`.env`のsource・値表示、秘密値の出力、`*.wav`・telemetry・logのadd、`ACTIVE_TASK*.md`/`RESULT_PACKET*.md`のcommit、Melos run_e2e_02配下・Master Store・HR・attempt_history・telemetryへの書込、外部停止プロセスの再起動、監督ループ/`timeout`ラッパ。
- STOP確認義務: 開始時に`er026_output/family_z_production_e2e_01/`配下の`STOP_NOTICE`/`STOP`/`STOP_ALL`を確認し記録(旧記録は非適用)。
- Opus独立技術レビューGate判定: 非該当(比較生成のみ)。
- 時間見込み: 40〜60分。並列化: 他agentと並列。本委任内は生成6回を直列(rate limit・再現性)。
- 最新モデル原則: Production同一`gpt-6-luna`・reasoning effort high(例外理由=Production Preview生成との比較可能性)。応答model_id実測を記録。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。**委任文は本文全文をそのまま保存すること(要旨化・整形・圧縮は禁止)。**
T-2: TTSなし(該当なし)。
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`、ユーザー正式決定、費用上限[Cap]を伴う全委任で常時有効): 費用上限[Cap]は「暴走防止のためのGuardrail」であり、Cap到達=自動STOPではない。禁止事項/性質欄の費用上限記載は次の定型文に従う。「上限¥X(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。」

## ユーザー指示(原文)

(2026-10-13、管理ID FAMILY-Z-MELOS-PREVIEW-STD-ADV-3TAKE-COMPARE-01。全文)
「## 1. 目的 メロスのPreviewについて、StandardとAdvancedの出力を比較し、同じPromptでの生成のばらつき、および両レベル間の品質差を確認する。
## 2. 実施内容 Standard: 3回生成(Take1〜3)/Advanced: 3回生成(Take1〜3)/合計6回のLLM生成を実施する。使用Prompt: Standard: 直前の`FAMILY-Z-STANDARD-PREVIEW-X-ALIGNMENT-01`でTrialした、Family X Standard準拠の統一Prompt/Advanced: 現行Family Z Advanced Preview Prompt。両Promptとも一切変更しないこと。生成条件: メロスの既存Production原稿を使用する。既存のComment等、Preview生成に必要な入力をそのまま使用する。StandardとAdvancedそれぞれの正規の入力条件を維持する。各Takeは独立して生成する。既存の出力を再利用せず、新規に3回ずつ生成する。
## 3. 出力・評価 6件のPreview全文を、省略せず並べて報告する。あわせて以下を比較する。1.興味を引く導入になっているか 2.具体的な状況・問題を適切に提示できているか 3.あらすじ化していないか 4.ネタバレがないか 5.Comment 1・2との重複がないか 6.自然で聞きやすい文章か 7.Take間の品質のばらつき 8.StandardとAdvancedの構成・センスの違い。Advancedは英語、Standardは日本語で評価すること。単なる直訳の一致ではなく、Previewとしての役割と品質が両レベルで揃っているかを確認する。
## 4. 作業範囲・禁止事項 Production Prompt・codeは変更しない。新たなPrompt調整や改善Trialを行わない。記事本文、Comment、Key Phrase等は再生成しない。TTS・音声化は行わない。Family Zの記事再生成・音声化STOPを維持する。今回の結果を理由にProduction採用を独自判断しない。費用を記録し、想定外の課金や仕様上の問題が発生する場合はSTOPすること。
## 5. 最終報告 次の順序で報告すること。1.Standard Take1〜3の日本語全文 2.Advanced Take1〜3の英語全文 3.Standard・Advancedの比較評価 4.出力の安定性についての結論 5.費用・使用モデル・テスト結果 6.ユーザーが判断すべき事項。Trial終了時は`VALIDATED`/`REJECTED`/`USER_DECISION_REQUIRED`のいずれかに分類すること。最終的なPrompt採用・Production反映はユーザー判断待ちとし、結果を報告した時点でSTOPすること。」

## KPI provenance欄

6 take=`fresh`(Trial隔離、Production正式経路ではないがProduction同一条件)。比較参照の既存Preview(Std現行/er070 AFTER/Adv現行)=`reuse`。fresh Production初回path E2E値: No。

## Opus台帳更新

該当なし。

## 事前指定Read一覧

1. `er070_family_z_std_preview_x_alignment_01.py`(自作系。統一Promptの組立関数・Comment 1・2埋込・`build_support_prompt`経由の呼出・lint呼出を再利用)。`er070_output/family_z_std_preview_x_alignment_01/prompt_after_full_assembled_01.txt`(sha照合用)。
2. Adv Preview経路: `er062_family_z_writer_01.py` `Grep -n "def run_support_adv|PREVIEW_ROLE|b1s\.|comment_1|comment_2|preview"`→Adv Preview生成の組立(Prompt定数、Comment 1・2の渡し方、model/effort/developer message、lint)。`b1s`の実体ファイル(`Grep -rn "^PREVIEW_ROLE" --include=*.py`)の該当範囲。
3. 入力: `er026_output/family_z_production_e2e_01/melos/run_e2e_02/writer/std.md`、同`writer/adv.md`(または`b1b.md`等、Advの正本をGlobで確認)、同`support/a2_support.json`(Std Comment 1〜3・現行preview)、同`support/b1b_support.json`(Adv Comment・現行preview。ファイル名はGlobで確認)。読み取りのみ。
4. `er062_family_z_structure_01.py` `Grep -n "def lint_support_text"`→Std('ja')/Adv('en')のlint呼出方法。
5. `OPEN_ITEMS.md` `Grep -n "\*\*OPEN-338"`。`docs/pm/USER_DECISION_REGISTER_01.md`末尾+集計行(#42〜#43を確認)。

## 事前指定Grep一覧+追記位置・更新位置の手順

- `OPEN_ITEMS.md` OPEN-338行末に「【2026-10-13 FAMILY-Z-MELOS-PREVIEW-STD-ADV-3TAKE-COMPARE-01】Std統一Prompt×3/Adv現行×3の比較結果要約、Status、費用」を追記。
- `DECISION_LOG.md`末尾に本IDのエントリ(ユーザー指示要旨、6 take、評価要約、Status、費用、使用モデル。採用判断なし)。
- `docs/pm/USER_DECISION_REGISTER_01.md`: #42(Family Z Std Preview X整合)に本IDの結果参照を追記、新行#44(本ID、UDR)、集計再計算。`docs/pm/REPORT_LEDGER.md`: 行追加。

## 作業内容

1. **Std 3 take**: er070の統一Prompt(Family X準拠、置換4箇所)+Comment 1・2+std.md全文、Production同一条件(gpt-6-luna、effort high、developer message、`build_support_prompt`)で独立3回生成。送信prompt全文のshaがer070のものと一致することを検証(不一致なら生成前にSTOP)。各takeにlint(`lint_support_text(text,'ja','melos')`)。
2. **Adv 3 take**: 現行Family Z Advanced Preview経路(`run_support_adv`相当の組立: `b1s.PREVIEW_ROLE`逐語+Comment 1・2+Adv原稿)をProduction同一条件で独立3回生成。送信promptのshaを記録(Production経路で組み立てたものと同一であることをmockで検証)。lint(`'en'`)。
3. **評価**(`COMPARE_REPORT_01.md`): 6件全文(Std日本語3件・Adv英語3件、字数/語数・文数・lint結果付き)。比較参照として現行Production Std preview・Adv preview・er070 AFTERも併記。評価表(8観点: 興味喚起/具体的状況・問題の提示/あらすじ化/ネタバレ[結末・転換点・後半展開]/Comment 1・2重複[文単位・語彙単位]/自然さ[Stdは日本語として、Advは英語として]/Take間ばらつき[構成・長さ・焦点の差]/Std vs Advの構成・センス[Previewとしての役割と品質が揃っているか])。事実ベースで記述し、採用判断は書かない。
4. **安定性の結論**: 同一Promptでの3 takeの一貫性(焦点・構成・問題提示の有無・ネタバレ傾向)と、前回(er067/er070)の単発結果との整合。「抽象・評論調はPrompt構造由来か出力の揺れか」の切り分けを、断定せず証拠付きで記載。
5. Status分類(VALIDATED/REJECTED/USER_DECISION_REQUIRED)と根拠。state_guard(run_e2e_02配下・Production py 5本のsha256前後不変)。費用(`cost_01.json`、call単位、model_id実測)。
6. SSOT(上記手順)。

## 実行コマンド全文

```
.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-13_FAMILY-Z-MELOS-PREVIEW-STD-ADV-3TAKE-COMPARE-01_01.md --json-out docs\pm\delegation_log\2026-10-13_FAMILY-Z-MELOS-PREVIEW-STD-ADV-3TAKE-COMPARE-01_01_check.json
set PYTHONUTF8=1
.venv\Scripts\python.exe er072_melos_preview_std_adv_3take_01.py --mode verify --out-dir er072_output\melos_preview_std_adv_3take_01
.venv\Scripts\python.exe er072_melos_preview_std_adv_3take_01.py --mode generate --takes 3 --out-dir er072_output\melos_preview_std_adv_3take_01 --budget-jpy 5
.venv\Scripts\python.exe er072_melos_preview_std_adv_3take_01_test_01.py
.venv\Scripts\python.exe er062_family_z_writer_01_test_01.py
.venv\Scripts\python.exe tools\secret_scan_01.py --staged
```

## SSOT追記文

上記手順どおり(文案はRESULT_PACKETに転記)。CURRENT_SPECは無編集。

## Git(明示add対象・コミットメッセージ・trailer)

明示add: `er072_melos_preview_std_adv_3take_01.py`、`er072_melos_preview_std_adv_3take_01_test_01.py`、`er072_output/melos_preview_std_adv_3take_01/*.{md,txt,json}`、`docs/pm/delegation_log/2026-10-13_FAMILY-Z-MELOS-PREVIEW-STD-ADV-3TAKE-COMPARE-01_01.md`(+`_check.json`)、SSOT限定ファイル。コミット2つ: (1)「FAMILY-Z-MELOS-PREVIEW-STD-ADV-3TAKE-COMPARE-01 委任_01: Melos Preview Std統一Prompt×3/Adv現行×3 比較生成(6 call JPY<実費>、Status=<判定>、Production無変更・採用判断なし)」(2)SSOT。trailer `Managed-ID: FAMILY-Z-MELOS-PREVIEW-STD-ADV-3TAKE-COMPARE-01`。commit前にsecret_scan、`git status --porcelain`で意図外ファイル不在確認。push。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_FZP3.md`に(ユーザー指示§5の順): (1)Std Take1〜3の日本語全文(字数・文数・lint)、(2)Adv Take1〜3の英語全文(語数・文数・lint)、(3)比較評価表(8観点)+現行/er070との対比、(4)安定性の結論、(5)費用(call別・合計、model_id実測、単価出典)・回帰(件数)・state_guard・sha検証結果、(6)ユーザー判断候補(推奨付き、採用判断はしない)、Status、(0)check結果(全文保存)・STOP確認、(7)SSOT反映一覧、(8)commit hash+raw URL。`docs/pm/ACTIVE_TASK_FZP3.md`に固定ヘッダ。
