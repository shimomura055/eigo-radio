## 管理ID

FAMILY-Y-CHUNK-OPEN527-CLOSEOUT-01 委任_01(OPEN-527の重複管理解消とCloseout準備: Y段落分割の既存仕様・実装状態の確認、複数段落記事で通常のRegression/Production確認ができる体制(test fixture)の整備、Closeout文案。記事本文改変なし・有料Trialなし・API 0)。並行タスク衝突確認: 並行Agent 3件(FAMILY-Y-STYLE-PROFILE-FIX-01 委任_01[read-only]、FAMILY-Y-HR-APPROVAL-VOICE-GUARD-01[`er121_family_y_audio_01.py`のHR承認部+新規test]、TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_01[read-only])。あなたの所有=`er121_family_y_std_chunk_test_01.py`(拡張)または新規`er121_family_y_multiparagraph_regression_test_01.py`、`docs/research/FAMILY-Y-CHUNK-OPEN527-CLOSEOUT-01/**`、`docs/pm/delegation_log/2026-10-26_FAMILY-Y-CHUNK-OPEN527-CLOSEOUT-01_DELEGATION_01.md`(+check.json)、`docs/pm/RESULT_PACKET_YCC1.md`。`er121_family_y_audio_01.py`/`er121_family_y_structure_01.py`/`er121_family_y_runner_01.py`は**編集禁止**(読み取りのみ。変更が必要と判明したらRESULT_PACKETに設計として記載)。SSOT編集権なし。pathspec付きcommit。git index.lock競合時は10秒待って再実行(最大3回)。ユーザー原文§3は並行Agent(FAMILY-Y-STYLE-PROFILE-FIX-01)が`docs/pm/delegation_log/2026-10-26_FAMILY-Y-STYLE-PROFILE-FIX-01_USER.md`へ保存する(作成済みなら参照)。

## 性質/到達上限Status/禁止事項

- 性質: 検証体制整備+Closeout準備(承認済み仕様内)。到達上限Status=READY_FOR_CLOSEOUT(CloseoutのSSOT反映はFable sync)。
- ユーザー原文§3逐語: 「Family Yの段落分割について、実際の記事が単一段落であることだけを理由に独立したOpen Itemを維持しない。- 既存の分割仕様と実装状態を確認。- 複数段落が必要な記事で通常のRegression／Production確認を実施できるようにする。- 検証のためだけに記事本文を改変しない。- 無理に分割を発火させる有料Trialは実施しない。- 独立したOPEN-527は重複管理を解消してCloseoutする。ただし、未確認のProduction Wiringを検証済みと偽って記録しない。」
- 禁止: 記事本文・run dir・公開ページの改変、有料API、Y本文契約(段落5固定・Voice本文1行)の変更、Production配線状態の表記を「検証済み」へ格上げ(Y chunk=配線済み・実記事では不発火・PRODUCTION_WIRED未判定のまま)、`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・`git checkout -- <file>`。
- 費用/日次: JPY0。
- Opus独立技術レビューGate(11-3): 非該当。
- 修正範囲の線引き(11-8): 範囲内=既存test(`er121_family_y_std_chunk_test_01.py` 14件、複数段落dev入力でのevidence driver `docs/research/CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01/tools/y_chunk_evidence_driver_01.py`)を整理し、複数段落fixtureでの回帰を定常化すること、重複OPENの整理。範囲外=本文契約変更(文境界分割/複数段落化)=未承認のまま。
- 時間見込み: 約1h。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSなし)
T-2追記(2026-09-25、`NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02`、PM_GOVERNANCE.md 7-5、予算逸脱再発防止): TTSを伴う委任は実行前に(1)差分[変更箇所のみ]再生成が対象コード上で実際に可能か確認、(2)既存の音声再利用キャッシュの有無を確認、(3)`--budget`/`--budget-jpy`等が存在すればタスク固有の承認上限に合わせて明示、(4)想定外の全再生成と判明した場合はAPI実行前にSTOPし報告、の4点を必須とする。

T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-26_FAMILY-Y-CHUNK-OPEN527-CLOSEOUT-01_DELEGATION_01.md` をN=671から順に試し、先頭が「## 管理ID」+「FAMILY-Y-CHUNK-OPEN527-CLOSEOUT-01 委任_01」で始まるものを採用(同時刻に別委任2件も送られているため先頭一致を必ず確認。`--index -1`不可)。

## 実施事項

1. **既存仕様・実装状態の確認(`STATE_01.md`)**: Y chunk配線の現状(CURRENT_SPEC Chunk節「Y Std/Adv=APPROVED_FOR_PRODUCTION・配線済み(WIRED_NOT_FIRING)・PRODUCTION_WIREDとは判定しない」、`er121_family_y_structure_01.py:111,152-183`の段落契約、`er121_family_y_audio_01.py` `_load_y_body_chunks`、`er117`のplanner、evidence=`CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01/EVIDENCE_01.md` §3 Y)を事実として整理。OPEN-527/OPEN-532のY関連記述の重複箇所をGrepで列挙(OPEN_ITEMS.md/CURRENT_SPEC.md/UDR)。
2. **複数段落での通常Regression体制**: 既存`er121_family_y_std_chunk_test_01.py`(14件)と`y_chunk_evidence_driver_01.py`を確認し、(a)複数段落fixture(本文を改変せず、test専用の合成段落テキスト)で「planner発火→chunk別6%減速→0.2秒無音→連結→Gate」が**オフライン(偽generator・API 0)で毎回の回帰に含まれる**状態か確認。不足していれば新規`er121_family_y_multiparagraph_regression_test_01.py`を追加(Std/Adv、発火/不発火境界、chunk数・境界種別・減速比・無音長・`CHUNKS_NOT_ALL_VALIDATED`ブロック、resume再利用)。(b)将来、複数段落のY記事がProductionに入った場合に「正式runtime evidenceを取得してPRODUCTION_WIREDへ更新する」手順(起動コマンド・確認項目)を`PRODUCTION_CHECK_PROCEDURE_01.md`に書く(実行はしない)。
3. **Closeout文案(`CLOSEOUT_01.md`)**: OPEN-527(独立項目)をCLOSEDとし、Y chunkの状態管理をOPEN-532(Chunk案件)へ一本化する文案。記載内容=「Y本文契約は段落5固定・Voice本文1行(承認済み・変更しない)。Chunkは配線済みで、複数段落入力のオフライン回帰(test名・件数)とdev入力evidence(path)で動作確認済み。実記事では不発火のためPRODUCTION_WIREDとは判定しない(ユーザー決定2026-10-26)。複数段落の記事が正式に生成された時点で手順書に従いruntime evidenceを取得して判定する」。本文契約の変更(文境界分割/複数段落化)は未承認のまま=新規の判断候補は立てない(ユーザー原文「独立したOpen Itemを維持しない」に従う)。

## KPI provenance欄

該当なし(test=synthetic)。

## Opus台帳更新

該当なし。

## 事前指定Read一覧

- `CURRENT_SPEC.md`: Grep `WIRED_NOT_FIRING|Y Std|Y Adv|構造的に不発火|OPEN-527` → 該当行±5(全文読込禁止)
- `OPEN_ITEMS.md`: Grep `OPEN-527|OPEN-532` → 該当行
- `docs/pm/USER_DECISION_REGISTER_01.md`: Grep `OPEN-527` → ±3
- `er121_family_y_std_chunk_test_01.py` 全文、`er121_family_y_structure_01.py:100-190`、`er121_family_y_audio_01.py`: Grep `_load_y_body_chunks|chunk` → ±10
- `docs/research/CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01/EVIDENCE_01.md` §3(Grep `Y Std|write_level_inputs|driver`)、`tools/y_chunk_evidence_driver_01.py`: Grep `def |build_real_context` → 構造
- `er117_chunk_tts_production_01.py`: Grep `def plan|CHUNK_PLANNER_VERSION|paragraph` → ±10

## 事前指定Grep一覧+追記位置・更新位置の手順

- Grep `OPEN-527` 全repo(`*.md`) → 重複記述の一覧
- 成果物は`docs/research/FAMILY-Y-CHUNK-OPEN527-CLOSEOUT-01/`に新規作成

## 実行コマンド全文

- 回帰(遮断harness・`.venv`): `.venv\Scripts\python.exe run_project_regression.py --pattern "er121_family_y_std_chunk_test_01.py"`、新規testがあれば`--pattern "er121_family_y_multiparagraph_regression_test_01.py"`、最後に`--pattern "er121*_test_*.py"`(接続試行0)
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## SSOT追記文

SSOT編集権なし。`RESULT_PACKET_YCC1.md`(9)にOPEN-527 CLOSED文案・OPEN-532追記文案・CURRENT_SPEC Y節の1行修正案(「OPEN-527参照」→「OPEN-532参照、手順書path」)・UDR更新案。

## Git(明示add対象・コミットメッセージ・trailer)

- add対象: 新規/変更test、`docs/research/FAMILY-Y-CHUNK-OPEN527-CLOSEOUT-01/`配下、`docs/pm/delegation_log/2026-10-26_FAMILY-Y-CHUNK-OPEN527-CLOSEOUT-01_DELEGATION_01.md`(+check.json)。pathspec付きcommit。
- commit message: `FAMILY-Y-CHUNK-OPEN527-CLOSEOUT-01 委任_01: Y段落分割の複数段落オフライン回帰整備+Production確認手順書+OPEN-527 Closeout文案(本文不変、API 0)`
- trailer: `Delegation: FAMILY-Y-CHUNK-OPEN527-CLOSEOUT-01/01`
- push: `git push origin HEAD:main`(non-ffなら`git fetch origin`→`git merge --no-edit origin/main`→push。競合はSTOPし報告)。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_YCC1.md`: (0)T-0、(1)現状の事実、(2)重複記述一覧、(3)回帰体制(既存/追加test、件数、PASS)、(4)Production確認手順書の要点、(5)Closeout文案、(6)判断候補(なし想定)、(7)必須4行+「判定整合: 重大NG=<なし|あり>」、(8)一覧外Read、commit hash、raw URL。末尾に要約5行以内。