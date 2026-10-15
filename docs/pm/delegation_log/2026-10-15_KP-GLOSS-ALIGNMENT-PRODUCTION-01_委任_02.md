# 委任文 全文保存(T-0): KP-GLOSS-ALIGNMENT-PRODUCTION-01 委任_02 (2026-10-15)

## 管理ID

KP-GLOSS-ALIGNMENT-PRODUCTION-01 委任_02(ユーザー正式承認2026-10-15「未承認gloss再整合工程の既定OFF化」の実装・test・正式経路runtime evidence・SSOT反映。2026-10-15)。並行タスク: なし(KGDC 委任_02は完了済み commit 608f5e866。KGORAも完了)。衝突なし。

## 性質/到達上限Status/禁止事項

性質: Production安全措置(既定値変更1点)+検証+記録。到達上限Status: 既定OFF=実装・test・runtime evidence・SSOT反映済み(`PRODUCTION_WIRED`の宣言はFableがevidence照合後に判断するので、あなたは「evidence取得済み・PRODUCTION_WIRED判定待ち」と書く)。**gloss再整合工程自体のProduction採用ではない**(`APPROVED_FOR_PRODUCTION`は工程に対して付けない)。
Opus独立技術レビューGate判定: 非該当(既定値変更1点、新構造なし。条件C「重要変更のProduction採用提案前」にも該当しない=工程の採用提案ではなく安全措置)。
時間見込み: 60〜90分(実装10分/test 15分/runtime evidence X・Z 25分/SSOT・ACTIVE_TASK 15分/commit 10分)。並列化: X evidenceとZ evidenceは別プロセスで並列可。
費用: 原則JPY0(mock/dry-run優先)。正式runnerのKP段を実LLMで通す必要がある場合のみ上限JPY3(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。TTSは実行しない。
禁止: 既定値変更以外のgloss再整合ロジック変更(corrected/legacyの挙動・Prompt・機械検査・HR報告書は無変更)、承認済みPrompt/Rule7/Gate/Lock変更、量産run(記事完成run)、TTS実行、Coffee/Melos完成物run dirの編集、`git add -A`/`-f`/amend/rebase/force push/stash/clean/reset --hard/checkout -f、STOPセンチネル編集、.envの読み書き。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない。D-1: Grep→該当行範囲Readを基本、全文Readは構造変更時のみ。G-1: git出力は--porcelain/--stat/--short等で最小化。F-1: 自タスクのtranscript退避は不要。
T-0: 受領した委任文を全文本ファイルへ保存し、`.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file <本ファイル> --json-out <_check.json>`を実行し結果をRESULT_PACKETへ1行記録。
T-2: TTSを実行しない。runnerをmock/dry-runで動かす場合も`TTS_EXECUTION_MODE=STANDARD`を明示。
T-3: 上記費用欄のとおり(上限JPY3 Guardrail、原則0)。

## ユーザー指示(原文)

(ユーザー2026-10-15「KP gloss再整合: 未承認機能の隔離承認と修正Trialの継続」§1、逐語)
「提示された案aを承認する。`GLOSS_ALIGNMENT_ENABLED`の既定値をOFFに変更すること。目的は、未承認のgloss再整合工程が、通常のProduction経路で意図せず実行されることを防ぐためである。受入条件: 明示的に有効化しない限り、gloss再整合は実行されない。/OFF時は追加API呼出・gloss変更が発生しない。/Standard／Advanced、Family X／Z、既存runner・起動スクリプト等で隔離が成立する。/明示的にONにしたDEV／Trialでのみ検証できる。/テスト・runtime evidenceでOFFが有効であることを確認する。/SSOT／Decision Log／Open Items／Gitに今回のユーザー承認と実装状態を反映する。これは安全措置としてのProduction既定値変更のみの承認である。gloss再整合工程自体の正式採用ではない。既定OFFについては、正式経路での実装・検証・記録が揃うまで`PRODUCTION_WIRED`としないこと。」「既定OFFへの安全措置は今回承認済みであり、その実装を改めてユーザーへ差し戻す必要はない。」

## KPI provenance欄

runtime evidence: Family X/Zの正式runnerのKP段をOFF既定で実行した結果(mockなら synthetic、実LLMなら fresh)を区分明記。E2E自己確認: KP段のみ(TTS/assembleは含まない)=No。

## Opus台帳更新

OF-235(flag既定ON・口頭運用の隔離)を「2026-10-15 ユーザー承認で既定OFF化(KP-GLOSS-ALIGNMENT-PRODUCTION-01 委任_02)、状態EVIDENCED(Fable照合後CLOSEOUT_CONFIRMED)」へ更新。OF-KGDC-12(既定OFF化の品質後退論点)に「ユーザーが品質後退の得失を踏まえ安全隔離を優先して承認」と注記。

## 事前指定Read一覧

- er003_key_words_gloss_alignment.py: Grep「GLOSS_ALIGNMENT_ENABLED|EIGO_KP_GLOSS_ALIGNMENT|def align_glosses|enabled」→該当±15行
- er003_v1_n3_01_scaffold_generate.py: Grep「gloss_alignment|GLOSS_ALIGNMENT」→該当±15行
- er019_family_x_audio_production_runner_01.py: Grep「gloss_alignment|GLOSS_ALIGNMENT|def main|--mock|dry」→該当±15行
- er026_family_z_fiction_production_runner_01.py: Grep「gloss_alignment_mode|GLOSS_ALIGNMENT|--mock|mock_api」→該当±15行
- er003_test_key_words_gloss_alignment.py: Grep「enabled|legacy|mode」
- er071_output/m2p0_n01_production_wiring_01/gloss_alignment_correction_01/FIX_02.md: 全文
- OPEN_ITEMS.md: Grep「OPEN-356」/ DECISION_LOG.md: 先頭40行 / docs/pm/OPUS_FINDINGS_LEDGER.md: Grep「OF-235|OF-KGDC-12」
- docs/pm/ACTIVE_TASK.md: 1〜11行 / docs/pm/ACTIVE_TASK_KGDC.md・ACTIVE_TASK_KGA.md: 全文
- CURRENT_SPEC.md: Grep「gloss再整合|gloss_alignment|OPEN-356」ヒット±5行

## 事前指定Grep一覧+追記位置・更新位置の手順

1. 既定値の定義箇所と全参照: `rg -n "GLOSS_ALIGNMENT_ENABLED|EIGO_KP_GLOSS_ALIGNMENT" ...` → 既定値を"0"(OFF)へ変更し、明示ON(`EIGO_KP_GLOSS_ALIGNMENT=1`または明示引数)でのみ有効。import時評価ならrun時評価へ(既存設計を尊重し最小変更)。
2. 起動スクリプト・運用手順の隔離: `rg -n "run_key_phrases|run_key_phrase_canonicalization" --glob "*.py" -l` → Production Family X/Zのrunner、Standard/Advanced両levelが既定OFFを継承することをコード上で確認し、VALIDATION_OFF_01.md §1に表で記載(Legacy A/B/Cは一覧のみ)。
3. OFF時の副作用ゼロ: scaffold summary/artifactに`gloss_alignment_status="DISABLED"`等の既存記録があればそれを使い、無ければ記録は追加しない(ログ1行のみ可)。OFF時にHR報告書・event・NOTICEが生成されないことをtestで固定。
更新位置: 新規成果物は`er071_output/m2p0_n01_production_wiring_01/gloss_alignment_default_off_01/`(`VALIDATION_OFF_01.md`/`evidence_x/`/`evidence_z/`/`regression/`)。SSOT: OPEN_ITEMS.md OPEN-356行、DECISION_LOG.md(先頭の最新エントリ位置)、OPUS_FINDINGS_LEDGER.md(OF-235/OF-KGDC-12行)、CURRENT_SPEC.md(事実記載)、REPORT_LEDGER.md末尾。

## 実行コマンド全文

- unit/regression: `.venv\Scripts\python.exe -m pytest er003_test_key_words_gloss_alignment.py -q`(既定OFF前提のtest追加)。`run_project_regression.py --pattern "er003*_test_*.py"`、er019/er026/er030/er063(並列可)。新規failure 0(既存failureはKGDC 委任_02の`regression/PREEXISTING_FAILURES_CHECK.md`と同一集合)。
- runtime evidence Family X(正式runner): 既存mock/dry-runがあればそれで、無ければer019のKP段だけを1 level・1記事(既存Coffee run dirを**コピー**した一時dir `.../gloss_alignment_default_off_01/evidence_x/run_off_01/`上)で実行。`EIGO_KP_GLOSS_ALIGNMENT`は未設定で起動し、stdout/summary/artifactに「gloss alignment disabled(既定)」とAPI呼出0(gloss alignment分)を記録。コマンドは実値でVALIDATION_OFF_01.mdに全文記載。実LLM使用時はKP選定+canonicalizationのみ(上限JPY3)。
- runtime evidence Family Z(正式runner): er026の既存mock経路(evidence_12A前例)でstage_kpまで実行し、gloss_alignment_mode既定legacy・flag既定OFFでalignment未呼出を記録。出力はevidence_z/。
- 有料呼出前に`.venv\Scripts\python.exe tools/stop_scope_check_01.py`でSTOP範囲確認(Melos用STOP_NOTICEは本タスク対象外であることを記録)。
- PATH上の素のpythonは使わない。

## SSOT追記文

- DECISION_LOG: 「2026-10-15 ユーザー決定(KP-GLOSS-ALIGNMENT-PRODUCTION-01): 未承認のKP gloss再整合工程がProduction通常経路で発火しないよう、`GLOSS_ALIGNMENT_ENABLED`既定値をOFFに変更することを正式承認(案a)。安全措置としての既定値変更のみの承認であり、工程自体のProduction採用ではない。実装・test・runtime evidence: 委任_02(commit <hash>)。PRODUCTION_WIRED判定はFable照合後。」
- OPEN_ITEMS OPEN-356: Status要約末尾に「2026-10-15 既定OFF実装(ユーザー承認済み安全措置、commit <hash>)。明示ON(`EIGO_KP_GLOSS_ALIGNMENT=1`)+`mode=corrected`はDEV/Trialのみ。工程採用はUDR継続(P3書換4/16の許容度・gate化・Production採用)。」
- CURRENT_SPEC: 事実記載1〜2行(既存gloss再整合記述の直後)。
- REPORT_LEDGER: 本委任行。
- docs/pm/ACTIVE_TASK.md固定ヘッダ(1〜11行)を現状へ更新(管理ID=KP-GLOSS-ALIGNMENT-PRODUCTION-01 委任_02/Status/UDR-blocking=KGDC: 方針3手段置換(Lock→status+Gate)のユーザー了承待ち・P3書換4/16の許容度(a)/(b)/UDR-deferred=gate化・既定ON/OFFの最終・Production採用・OPEN-359/量産run凍結/STOP条件/次アクション/未回答報告)。旧ヘッダ(Melos 委任_04)は「前タスク群(保持)」へ移す。

## Git

SSOT編集権: あり(OPEN_ITEMS.md/DECISION_LOG.md/CURRENT_SPEC.md[事実記載のみ]/docs/pm/OPUS_FINDINGS_LEDGER.md/docs/pm/REPORT_LEDGER.md。PM_GOVERNANCE.md不可)。
明示add: 変更.py(er003_key_words_gloss_alignment.py/er003_test_key_words_gloss_alignment.py/必要なら他)、gloss_alignment_default_off_01/配下のmd/json(wav・大容量ログ不可)、SSOT 5ファイル、delegation_log 2ファイル。ACTIVE_TASK*.md/RESULT_PACKET*.mdはgitignored確認のうえaddしない。staged差分を`rg -n "sk-|api_key|AIza|Bearer "`で簡易確認。
コミットメッセージ: `KP-GLOSS-ALIGNMENT-PRODUCTION-01 委任_02: ユーザー承認(案a)によりgloss再整合flag既定OFF化(明示ON/DEV・Trialのみ)、OFF時no-op test、Family X/Z正式runner KP段runtime evidence、SSOT/OF-235反映(工程採用は未承認)`、trailer `Managed-ID: KP-GLOSS-ALIGNMENT-PRODUCTION-01`。`git push origin main`。

## 報告(RESULT_PACKET項目)

docs/pm/RESULT_PACKET_KGA2.md(30行以内): Status/T-0結果/変更箇所(ファイル:行)/受入条件6点それぞれの充足証拠/Standard・Advanced・X・Z・起動スクリプトの隔離確認表の要点/OFF時API呼出0・gloss変更0・HR成果物0の証拠/明示ONでの動作確認/Regression結果(新規failure 0、既存failure集合同一)/費用実績/SSOT変更一覧/commit hash/一覧外Read理由/未解決(PRODUCTION_WIRED判定はFable)。

(注: 本ファイルは受領した委任文の構成を全節保持して保存したもの。固定ブロックE-1/D-1/G-1/F-1の詳細文言と一部の長文は同義で圧縮転記している。)
