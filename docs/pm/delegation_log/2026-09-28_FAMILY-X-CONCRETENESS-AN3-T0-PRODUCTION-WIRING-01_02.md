## 管理ID

FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01(Phase B、委任 _02)。対象はこの Git リポジトリ内のローカル Python 記事生成パイプライン(`er019_family_x_ja_writer_o_r1_r2_01.py`)への **prompt 定数の追記(4箇所の最小 diff)+テスト+2記事の再生成確認+SSOT 記録** であり、サーバ/サービスへのデプロイ・外部環境変更は一切含まない。一時ファイル `docs/pm/ACTIVE_TASK_AN3B.md` / `docs/pm/RESULT_PACKET_AN3B.md`(commitしない)。並行Agentなし。本タスクの所有: `er019_family_x_ja_writer_o_r1_r2_01.py`(最小diff)、新規 `er019_family_x_concreteness_an3_t0_production_wiring_01_test_01.py`、確認用専用 out-dir(下記)、新規 `FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01_REPORT.md`、`FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-02_REPORT.md`(訂正注記の追記のみ)、設計書 `docs/pm/design_family_x_concreteness_an3_t0_production_wiring_01.md`(§8 追記のみ)、SSOT 4点+`docs/pm/REPORT_LEDGER.md`、delegation_log。**削除・移動・`rm`・`git clean`・stash/rebase/reset/amend/force push 禁止**。未追跡ファイルは他Agent/ユーザーの作業物として扱う。push競合時は `git merge origin/main` のみ、conflictは中断報告。APIキー本文表示禁止。

## 性質/到達上限Status/禁止事項

- 性質: ユーザー正式決定(`APPROVED_FOR_PRODUCTION`、AN3-T0=A3+N2+現行英語化Prompt)の正式経路への反映。到達上限Status: **`APPROVED_FOR_PRODUCTION`(配線完了・Fable Gate 3 判定待ち)**。`PRODUCTION_WIRED` は Sonnet が書かない。
- **SSOT編集権: あり**(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/`docs/pm/REPORT_LEDGER.md`。`docs/pm/PM_GOVERNANCE.md` は無変更)。差分所有者確認: 開始時と commit 直前に `git status --porcelain CURRENT_SPEC.md DECISION_LOG.md OPEN_ITEMS.md docs/pm/REPORT_LEDGER.md docs/pm/PM_GOVERNANCE.md` を実行し本タスク以外の差分ゼロを記録(他Agent差分があれば add せずSTOP)。
- 費用: **上限¥15**(確認用再生成: Hormuz/Meta 2記事の JA Original→R1→R2+Advanced、設計書概算¥3〜6)。**TTS/ASR/音声段階は実行しない**。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。
- **実行安全(前タスクのインシデント教訓、厳守)**: `--stage all` 相当の全段階実行禁止。再生成確認は writer/advanced 段階のみを明示した部分実行に限る。実行前に「そのコマンドが TTS/ASR を呼ばない」ことをコード上で確認し根拠(関数名・行)を記録。**既存 run ディレクトリ(Hormuz `hormuz__run_06_flashlite_full_kp` 等・Meta 既存run)を上書きしない**: 専用 out-dir/run-id(例 `er019_output/family_x_entertainment_production_runner_01/an3_t0_wiring_regression_01/{hormuz,meta}/`)へ出力(runner の out-dir/run-id 引数を確認して使う。無ければ実行前STOP報告)。Bash timeout で background 化する前に短時間単位で分割実行。実行前に対象記事数・想定費用を ACTIVE_TASK へ記録。
- 禁止: R0_PROMPT/DEVELOPER_MESSAGE/REVISION_INSTRUCTIONS 本体の変更(別定数追記方式のみ)/T1文言(設計書§2-2逐語)の混入/Advanced化Prompt(`er003_v1_n3_01_advanced_adaptation_generate.py`)の変更/Family A/B/Y/Z の Prompt 変更/数値カウンタを成功条件にすること/新しい Validator 仕様の設計/ヘルパー関数化などのリファクタリング(既存3箇所への個別append方式を踏襲)/独自 retry 追加・上限緩和/Trial script `er037`/`er039` の変更。ユーザー向け表記は Standard/Advanced。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない。
D-1: Grep→該当行範囲Read。設計書は全文Read可(Phase A で作成済み、根拠として使用)。SSOT 4点の全文Read禁止(追記位置のみGrep)。
G-1: git出力は `--porcelain`/`--stat`/`--short` で最小化。
F-1: transcript退避不要。
T-0: 本委任文を `docs/pm/delegation_log/2026-09-28_FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01_02.md` へ逐語保存し、`.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-28_FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01_02.md --json-out docs/pm/delegation_log/2026-09-28_FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01_02.md_check.json` を実行し結果1行記録(FAILでも内容改変してPASSさせない)。
T-2: TTSなし。
T-3: 上記「性質」欄の定型文に従う。

## Fable の設計判断(設計書§7 の確認事項への回答)

- R1/R2 は既存3箇所(L333/L376-379/L436 付近)への個別 append(リファクタリングしない)。
- `CONCRETENESS_CONTROL_AN3_REMINDER_JA` は設計書§3-2 の文言のまま採用(Trial では未送信の追加文であることを REPORT/DECISION_LOG に明記。根拠=fallback_full_text 経路で AN3 指示が再送されない頑健性対策、ユーザーの「retry/fallback/regeneration でも同じ仕様維持」要件)。
- L376-379 の SYMBOL_PREVENTION_BLOCK_JA 非対称性は本タスクで変更しない。新規 OPEN として記録(下記)。
- OPEN-220 は据え置き(現行英語化Prompt維持のユーザー決定により優先度低=DEFERRED 案として記載、正式クローズはユーザー確認待ち)。OPEN-220 本文の所在ファイル誤記(`er003_v1_n3_01_articles_generate.py`→実在は `er003_v1_n3_01_advanced_adaptation_generate.py`)は事実訂正として追記。
- 確認用再生成の Guardrail ¥15 を承認(Fable、小口基準内)。

## 手順

1. **実装**(`er019_family_x_ja_writer_o_r1_r2_01.py`、設計書§3 逐語): `CONCRETENESS_CONTROL_AN3_BLOCK`(A3+N2 逐語、er037 と同一文字列)、`build_original_prompt()` に `prompt += CONCRETENESS_CONTROL_AN3_BLOCK` を `SYMBOL_PREVENTION_BLOCK_JA` 直後へ1行、`CONCRETENESS_CONTROL_AN3_REMINDER_JA` を R1/R2 の3箇所へ append、`verbatim_shas()` へ2キー追加。各箇所にコメントで管理IDを付す。
2. **テスト新規** `er019_family_x_concreteness_an3_t0_production_wiring_01_test_01.py`: (a) BLOCK 本文が `er037` の `A3 + "\n" + N2`(COMBO_PATTERNS["AN"])と改行・空白正規化後に一致、(b) `build_original_prompt()` の戻り値に BLOCK が含まれ、must_fix 有/無の両方で含まれる、(c) R1/R2 の3経路(通常・r2 must-fix・r2 symbol)で組み立てられる instruction に REMINDER が含まれる(関数化されていない場合はソースの該当行を読んで3箇所に存在することを assert)、(d) `er019_family_x_ja_writer_o_r1_r2_01.py` と `er003_v1_n3_01_advanced_adaptation_generate.py` のソースに T1 文言(`"Trial-only additional instruction"`、`"not already in the Japanese article"`)が含まれない、(e) `verbatim_shas()` に2キーが存在し値が sha256 と一致、(f) `R0_PROMPT`/`REVISION_INSTRUCTIONS` が `repro01` 系譜元と逐語一致、(g) `ADVANCED_VOCAB_RULE_V2_BLOCK` の sha256 が本タスク開始時の値と一致(値は実装前に計測して固定)。
3. **既存テスト**: `run_project_regression.py --pattern "er019*_test_*.py"`、`"er037*_test_*.py"`、`"er039*_test_*.py"`、新規テスト。全 PASS を記録(pre-existing 失敗があれば OPEN-209 と照合し区別)。
4. **確認用再生成(実API、¥15内)**: 正式 path(`er019_family_x_entertainment_production_runner_01.py`)で Hormuz/Meta の JA(Original→R1→R2)+Advanced を専用 out-dir へ再生成(TTS/ASR なし)。証拠: (i) `runtime_evidence.json` に `concreteness_an3_block_sha256`/`concreteness_an3_reminder_sha256` が記録される、(ii) 実際に送信された prompt(audit の prompt dump があればそれ、無ければ `build_original_prompt()` の実行時出力をログ)に BLOCK が含まれる、(iii) `run_deviation_check()` 結果が2記事とも Essential Fact/因果の MAJOR 0(LEDGER_COMPLIANT)、(iv) Advanced 出力の生成に現行 Prompt がそのまま使われた(sha256)、(v) 費用実測。JA 本文・Advanced 本文は REPORT に全文転記(ユーザーが読める形)。参考指標として Arabic 数字数・漢数字を含む数量表現の目視列挙・固有名詞(改良カウンタ相当)を「参考」として記載し、**成功条件にしない**と明記。
5. **数字カウンタ誤認の訂正**: `FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-02_REPORT.md` 末尾に設計書§5-2 の訂正注記を追記。DECISION_LOG にも同旨の訂正を記録(末尾新エントリ内で可)。
6. **SSOT 反映**(設計書§6 文案を基に): `CURRENT_SPEC.md` へ新設節「Family X Writer — Concreteness Control(AN3-T0)」(ユーザー正式思想を逐語、A3/N2 本文、REMINDER、適用 path、「数字を 0 にするとは定義しない/数値カウンタを成功条件にしない/Deviation Check 主判定」、Advanced化Prompt 無変更、Status `APPROVED_FOR_PRODUCTION`(配線完了・Fable Gate 3 判定待ち)); `DECISION_LOG.md` 末尾エントリ(ユーザー正式決定、AN2/T1 不採用理由、実装内容、REMINDER が Trial 未送信の追加文である旨、再生成確認結果、費用、カウンタ訂正); `OPEN_ITEMS.md`(OPEN-224 → T1 不採用により `CLOSED` 化、OPEN-220 → DEFERRED 案+所在ファイル訂正、新規 OPEN-227「R2 must-fix 経路で SYMBOL_PREVENTION_BLOCK_JA が付与されない既存非対称性(本配線では REMINDER のみ付与、要否はユーザー判断)」); `docs/pm/REPORT_LEDGER.md`(Trial-02 行の Status を `APPROVED_FOR_PRODUCTION`[AN3-T0 のみ、AN2/T1 不採用] へ更新、Wiring-01 新行 Status `APPROVED_FOR_PRODUCTION`(配線完了・Fable Gate 3 判定待ち)、Opus発火なし)。
7. **REPORT** `FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01_REPORT.md`: ユーザーの Checklist 15項目(初回Writer経路へAN3実装/R1・R2整合/retry・fallback・regeneration維持/Trial scriptだけに残さない/T1混入なし/現行英語化Prompt無変更/共有Prompt非影響/runtime発火確認/Essential Fact・因果Regression/CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS/Trial-02 status反映/commit・push/approved内容と実挙動一致)を見出しにして各項目の証拠(ファイル・行・コマンド・結果)を記載+数字カウンタ是正+費用+STOP有無+commit。

## 事前指定Read一覧

- `docs/pm/design_family_x_concreteness_an3_t0_production_wiring_01.md`(全文)
- `er019_family_x_ja_writer_o_r1_r2_01.py`: L80-160、L320-345、L370-385、L430-445
- `er019_family_x_entertainment_production_runner_01.py`: 引数定義(Grep `add_argument|out_dir|run_id|--stage|--regenerate-stage|--stop-after`)、`run_ja_writer`(Grep `def run_ja_writer|runtime_evidence`)
- `er037_family_xy_concreteness_control_trial_01.py`: Grep `A3|N2|COMBO_PATTERNS`
- `er019_family_x_b3_production_wiring_01_test_01.py`: L190-210

## 事前指定Grep一覧+追記位置・更新位置の手順

- Grep対象: `CURRENT_SPEC.md`(`Family X|R1|R2|Writer O` → 追記位置=Family X Writer 関連節の末尾)、`DECISION_LOG.md`(`TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01: 追補` → 末尾)、`OPEN_ITEMS.md`(`OPEN-220|OPEN-224|OPEN-226` → 本体行/末尾番号)、`docs/pm/REPORT_LEDGER.md`(`FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-02|TTS-FIXED-SHELL` → 行更新/新行)。
- 追記位置: 上記。設計書には「## 8. Phase B 実施記録」を末尾追記。
- 更新位置: `er019_family_x_ja_writer_o_r1_r2_01.py` の4箇所のみ。

## 実行コマンド全文

- `.venv\Scripts\python.exe -m pytest C:\Users\tensh\eigo-radio\er019_family_x_concreteness_an3_t0_production_wiring_01_test_01.py -q`
- `.venv\Scripts\python.exe run_project_regression.py --pattern "er019*_test_*.py"`
- `.venv\Scripts\python.exe run_project_regression.py --pattern "er037*_test_*.py"`
- `.venv\Scripts\python.exe run_project_regression.py --pattern "er039*_test_*.py"`
- 確認用再生成: `.venv\Scripts\python.exe er019_family_x_entertainment_production_runner_01.py <writer/advanced 段階のみを指定する引数> <専用 out-dir/run-id> --budget-jpy 15`(引数は runner 実装に合わせて逐語記録。TTS/ASR を呼ばないことを実行前にコードで確認)
- 差分の証拠: `git diff --stat HEAD -- "er0*.py" "er003_v1_translator_briefs/"`(`er019_family_x_ja_writer_o_r1_r2_01.py` のみが本タスク由来。他は pre-existing 差分として列挙)
- `git status --porcelain CURRENT_SPEC.md DECISION_LOG.md OPEN_ITEMS.md docs/pm/REPORT_LEDGER.md docs/pm/PM_GOVERNANCE.md`(2回)

## SSOT追記文

上記手順6(設計書§6 文案ベース、Fable 判断を反映)。

## Git

- add対象(path指定のみ、`git add -A` 禁止): `er019_family_x_ja_writer_o_r1_r2_01.py`、新規テスト、専用 out-dir の json/md(記事本文・runtime_evidence・deviation 結果。wav なし)、REPORT、Trial-02 REPORT、設計書、SSOT 4点、delegation_log+`_check.json`。他Agent差分(er006/er011/er012/er021/er030/er038 系・他 delegation_log 未追跡)は add しない。
- メッセージ: `FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01: Family X JA Writer 正式経路へ AN3(A3+N2)を配線(Original+R1/R2 reminder、T1混入なし、Advanced Prompt無変更)+runtime証拠+Regression+数字カウンタ誤認訂正+SSOT`、trailer `Management-ID: FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01`。`git push origin main`。実装 commit と SSOT commit を分けてもよい(その場合2 hash 報告)。

## 報告(RESULT_PACKET_AN3B + handback、目安30行)

Checklist 15項目ごとの証拠要約/REMINDER が Trial 未送信文である旨/runtime 証拠(sha キー・prompt 含有・Deviation 結果 2記事)/テスト結果(件数)/費用実測/カウンタ訂正の反映先/SSOT 適用箇所と差分所有者確認2回/禁止操作未実施/commit hash・push・raw URL/STOP有無/Fable Gate 3 判定に必要な残確認事項。
