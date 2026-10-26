## 管理ID

FAMILY-Y-HR-APPROVAL-VOICE-GUARD-01 委任_01(OPEN-535: Voice/Style変更後に旧Human Review承認が再利用され得る問題の自律修正=原因究明→修正→Regression→正式経路確認。承認済み範囲内の不具合修正)。並行タスク衝突確認: 並行Agent 3件(FAMILY-Y-STYLE-PROFILE-FIX-01 委任_01[read-only設計]、FAMILY-Y-CHUNK-OPEN527-CLOSEOUT-01[read-only+chunk test]、TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_01[read-only])。あなたの所有=`er121_family_y_audio_01.py`(HR承認照合・`y_tts_voice_requested`刻印部のみ)、`er011_human_review_lock_01.py`(必要最小限。共通moduleのため変更は後方互換・既定挙動不変で、X/Zに影響しないことをtestで固定)、新規`er121_family_y_hr_approval_guard_test_01.py`、`docs/research/FAMILY-Y-HR-APPROVAL-VOICE-GUARD-01/**`、`docs/pm/delegation_log/2026-10-26_FAMILY-Y-HR-APPROVAL-VOICE-GUARD-01_DELEGATION_01.md`(+check.json)、`docs/pm/RESULT_PACKET_YHG1.md`。既存run dir(`run_01`/`run_voice_puck_ev_01`)・公開dirは変更禁止(読み取りのみ)。SSOT編集権なし。pathspec付きcommit。git index.lock競合時は10秒待って再実行(最大3回)。ユーザー原文は並行Agent(FAMILY-Y-STYLE-PROFILE-FIX-01)が`docs/pm/delegation_log/2026-10-26_FAMILY-Y-STYLE-PROFILE-FIX-01_USER.md`へ保存する(§2が本委任の原文。作成済みなら参照)。

## 性質/到達上限Status/禁止事項

- 性質: 承認済み仕様(HR承認scope=「this single segment / this attempt only」)と実装の乖離是正(11-8範囲内)。到達上限Status=FIXED+EVIDENCE_COLLECTED(PRODUCTION_WIRED判定はFable)。
- 禁止: 新仕様の追加、正常な再利用・resumeを壊す変更、有料APIの多用(正式経路確認は最小。見積5円以下)、`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・`git checkout -- <file>`。
- ユーザー原文§2逐語: 「Voice変更時に旧Voiceに対するHuman Review承認が不適切に再利用され得る問題を修正する。原因究明→修正→Regression→正式経路確認まで自律実施。Voice・Style変更後の旧承認流用を防止。正常な再利用やresumeを壊さない。ユーザーに技術的な選択肢を逐一提示しない。承認済み範囲で完成まで進め、必要なruntime evidenceとSSOT／Git反映を行うこと。」
- 費用: 上限¥10(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。
- 費用/日次: 当日既使用約JPY563/残約JPY437/本委任見積JPY0〜5(正式経路確認はAPI 0のdry-run/偽generator中心。実TTSが必要なら1 segment 1回まで)/改善見込み高/承認区分: C。
- Opus独立技術レビューGate(11-3): 非該当(不具合修正、新フローなし)。
- 修正範囲の線引き(11-8): 範囲内=承認記録のscope(segment+attempt)どおりに照合条件へVoice(とStyle prefix)を含める是正、Regression、正式経路確認。範囲外=HR方式の変更、承認UIの新設。
- 時間見込み: 約1.5h(原因究明20分/修正+test 40分/正式経路確認20分/文書化10分)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。
T-2追記(2026-09-25、`NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02`、PM_GOVERNANCE.md 7-5、予算逸脱再発防止): TTSを伴う委任は実行前に(1)差分[変更箇所のみ]再生成が対象コード上で実際に可能か確認、(2)既存の音声再利用キャッシュの有無を確認、(3)`--budget`/`--budget-jpy`等が存在すればタスク固有の承認上限に合わせて明示、(4)想定外の全再生成と判明した場合はAPI実行前にSTOPし報告、の4点を必須とする。
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`、ユーザー正式決定、費用上限[Cap]を伴う全委任で常時有効): 費用上限[Cap]は「暴走防止のためのGuardrail」であり、Cap到達=自動STOPではない。禁止事項/性質欄の費用上限記載は次の定型文に従う。「上限¥X(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。」旧来の「上限¥X、超えそうなら実行前STOP」のみの記載(継続条件・STOP条件の書き分けが無いもの)は使用しない。既存7-5(4)「想定外の全再生成が判明したらAPI実行前にSTOP」は本T-3の「暴走疑い時のSTOP」に該当する条件として維持する(置き換えではない)。ユーザー承認済みの総予算・個別run上限・STOP条件を優先し、Fable/Workerが独自に過度に厳しい停止条件を追加しない(2026-10-05)。

T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-26_FAMILY-Y-HR-APPROVAL-VOICE-GUARD-01_DELEGATION_01.md` をN=671から順に試し、先頭が「## 管理ID」+「FAMILY-Y-HR-APPROVAL-VOICE-GUARD-01 委任_01」で始まるものを採用(同時刻に別委任2件も送られているため先頭一致を必ず確認。`--index -1`不可)。

## 実施事項

1. **原因究明**: `docs/research/FAMILY-Y-REDELIVERY-FEE-FINAL-PUCK-01/PLAN_01.md`の重大所見(`er011_human_review_lock_01.check_before_generation`が旧承認残存で`proceed=False HUMAN_APPROVED`を返しTTS/ASRを0 callでスキップ、承認照合がcanonical text shaのみでVoiceを見ない、`er121_family_y_audio_01.py` HEAD行492/606が`y_tts_voice_requested`を無条件刻印、承認記録`ypl7_user_approval_record_y_voice_1.json`のscope=「this single segment / this attempt only」)を一次情報で再確認し、X/Z経路にも同じ構造があるか(`er019`/`er063`の承認照合箇所)を調べる(X/Zの修正は本委任では行わず、該当すれば報告)。
2. **修正(最小・fail-closed)**: Y経路で、承認記録の照合キーに「text sha+voice(+style prefix sha)」を含める。承認記録にvoice情報が無い旧記録は「当該attemptのvoice/styleが現要求と一致する場合のみ有効」とし、一致を判定できない(記録欠落)場合は承認を適用せず通常生成へ進む(=旧承認を流用しない)。`y_tts_voice_requested`の刻印は実際にTTSへ渡したvoiceと一致する場合のみ(承認スキップ時は旧entryのvoiceを保持し、要求voiceと不一致ならSTOP/再生成)。`er011`共通moduleを触る場合は新引数既定Noneで既定挙動不変。承認記録の新規書込みにはvoice/style/modelを含める(将来の照合用)。
3. **Regression**: 新規test(旧承認+Voice不一致→承認不適用・再生成/旧承認+Voice一致→適用[正常再利用]/承認記録voice欠落→不適用/a2 previewの既存承認は影響なし/resume・regenerationで重複生成なし/X/Zの既定挙動不変)、er121回帰全件、er011/er019/er063の関連testPASS、接続試行0。
4. **正式経路確認(API 0〜最小)**: `run_voice_puck_ev_01`を書き換えず、scratchへ複製したrun dirに**旧Algieba承認を意図的に残した状態**を作り、正式CLI(`er121_family_y_runner_01.py --mode real … --only-segments y_voice_1`)を偽generator/dry-run(課金なし)で起動して「承認が適用されず生成が要求されること」を観測。実TTSが必要な場合は1 segment 1回(≤2.5円)まで。起動間隔150秒・5分3回禁止・`TTS_EXECUTION_MODE=STANDARD`。
5. **成果物**: `docs/research/FAMILY-Y-HR-APPROVAL-VOICE-GUARD-01/{ROOT_CAUSE_01,FIX_01,EVIDENCE_01}.md`、`evidence_01.json`。

## KPI provenance欄

正式経路確認=production_formal_path(scratch複製run、偽generator)/実TTSを使った場合はfresh。E2E自己確認: 部分(承認照合段のみ)。

## Opus台帳更新

該当なし。

## 事前指定Read一覧

- `docs/research/FAMILY-Y-REDELIVERY-FEE-FINAL-PUCK-01/PLAN_01.md`: Grep `重大所見|HUMAN_APPROVED|S3|y_tts_voice_requested|scope` → ±15
- `er011_human_review_lock_01.py:280-360`、Grep `def check_before_generation|human_approved_segments|sha256|scope` → ±15
- `er121_family_y_audio_01.py:470-520,590-620`、Grep `check_before_generation|human_approved|y_tts_voice_requested|voice_guard_cached` → ±15
- `er019_family_x_audio_production_runner_01.py`・`er063_family_z_audio_01.py`: Grep `check_before_generation|human_approved_segments` → ±10(構造比較のみ)
- `er121_output/family_y_production_01/redelivery_fee/run_01/a2/audit/human_approved_segments.json`、`ypl7_user_approval_record_y_voice_1.json`(Glob後)=記録形式の確認(読み取りのみ)
- `docs/pm/PM_GOVERNANCE.md`: Grep `approve_regenerate|HR Lock|Human Review Lock` → 該当節(承認scopeの正本)

## 事前指定Grep一覧+追記位置・更新位置の手順

- Grep `human_approved_segments` 全repo(`*.py`) → 承認照合の全呼出元
- 成果物は`docs/research/FAMILY-Y-HR-APPROVAL-VOICE-GUARD-01/`に新規作成

## 実行コマンド全文

- 回帰(遮断harness・`.venv`): `.venv\Scripts\python.exe run_project_regression.py --pattern "er121*_test_*.py"`、`--pattern "er011*_test_*.py"`、必要に応じ`--pattern "er019*_test_*.py"`・`--pattern "er063*_test_*.py"`(承認照合関連のみ抽出可。使ったコマンドを全文記録)
- 正式経路確認: scratch複製は`C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1\scratchpad\yhg_run\`配下に作成し、runnerの`--run`/`--out-dir`相当でそこを指す(引数は`--help`で実値確認。run dirを`er121_output`配下に作る必要がある場合は`run_hrguard_ev_01`として新規作成し、公開・run_01・ev_01は不変)
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## SSOT追記文

SSOT編集権なし。`RESULT_PACKET_YHG1.md`(9)にOPEN-535更新文案(FIXED+evidence、X/Z該当有無)・CURRENT_SPEC HR承認scope節の追記案・DECISION_LOG案。

## Git(明示add対象・コミットメッセージ・trailer)

- add対象: `er121_family_y_audio_01.py`、(変更時)`er011_human_review_lock_01.py`、`er121_family_y_hr_approval_guard_test_01.py`、`docs/research/FAMILY-Y-HR-APPROVAL-VOICE-GUARD-01/`配下、`docs/pm/delegation_log/2026-10-26_FAMILY-Y-HR-APPROVAL-VOICE-GUARD-01_DELEGATION_01.md`(+check.json)。pathspec付きcommit。
- commit message: `FAMILY-Y-HR-APPROVAL-VOICE-GUARD-01 委任_01: OPEN-535 旧HR承認のVoice/Style不一致流用を防止(承認scope=segment+attempt+voiceで照合、記録欠落は不適用、正常再利用維持、test、正式経路確認)`
- trailer: `Delegation: FAMILY-Y-HR-APPROVAL-VOICE-GUARD-01/01`
- push: `git push origin HEAD:main`(non-ffなら`git fetch origin`→`git merge --no-edit origin/main`→push。競合はSTOPし報告)。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_YHG1.md`: (0)T-0、(1)原因(一次情報:行、X/Z該当有無)、(2)修正内容(差分:行、既定挙動不変の根拠)、(3)test・回帰(件数・接続試行0)、(4)正式経路確認の観測(コマンド全文・結果・費用)、(5)正常再利用・resumeが壊れていない証拠、(6)SSOT文案、(7)判断候補(なし想定)、(8)必須4行+「判定整合: 重大NG=<なし|あり>」、(9)一覧外Read、commit hash、raw URL。末尾に10行以内の要約。