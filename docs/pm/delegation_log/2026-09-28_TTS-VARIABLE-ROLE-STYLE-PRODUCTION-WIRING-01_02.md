## 管理ID

TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01(Phase B=実装+runtime証拠+Regression+SSOT、委任 _02)。対象はこのリポジトリ内のローカル Python 音声生成パイプラインの style 定数・引数追加(最小 diff)であり、サーバ配備等は含まない。一時ファイル `docs/pm/ACTIVE_TASK_VW1B.md` / `docs/pm/RESULT_PACKET_VW1B.md`(commitしない)。並行: 別Sonnet 3件(Task 1 `er045_*`/`user_test/no_heading_trial_01/`、Task 2 `er046_*`/`user_test/kp_advanced_explanation_audio_trial_04/`、Task 3 `er047_*`/`user_test/fixed_shell_three_five_retrial_01/`、いずれも SSOT 編集権なし)→ 触れない。本タスクの所有: `er003_b1_p9a_audio.py`(ja 分岐 1 行)、`er003_v1_n3_01_tts_generate.py`(2 関数の引数追加)、`er033_tts_flash_lite_family_x_styles_01.py`(E2 値更新+`FAMILY_X_ROLE_STYLE_JA`)、`er019_family_x_audio_production_runner_01.py`(`_role_style_ja()` と A2 preview/comment_1-4 の配線)、関連既存テスト(E0 リテラル assertion の更新)、新規 `er019_family_x_variable_role_style_wiring_01_test_01.py`、専用 out-dir、新規 `TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01_REPORT.md`、設計書 §8 追記、SSOT 4点+REPORT_LEDGER、delegation_log。**削除・移動・`rm`・`git clean`・stash/rebase/reset/amend/force push 禁止**。未追跡ファイルは他Agent/ユーザーの作業物として扱う。push競合時は `git merge origin/main` のみ、conflictは中断報告。APIキー本文表示禁止。

## 性質/到達上限Status/禁止事項

- 性質: ユーザー正式決定(JA=J3、EN=E2、`APPROVED_FOR_PRODUCTION`)の正式経路への反映。到達上限Status: **`APPROVED_FOR_PRODUCTION`(配線完了・Opus L2 レビュー+Fable Gate 3 判定待ち)**。`PRODUCTION_WIRED` は書かない。
- **SSOT編集権: あり**(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/`docs/pm/REPORT_LEDGER.md`。`docs/pm/PM_GOVERNANCE.md` 無変更)。現在SSOT編集権を持つAgentは本タスクのみ。差分所有者確認: 開始時と commit 直前に `git status --porcelain CURRENT_SPEC.md DECISION_LOG.md OPEN_ITEMS.md docs/pm/REPORT_LEDGER.md docs/pm/PM_GOVERNANCE.md` を実行し本タスク以外の差分ゼロを記録(他Agent差分があれば add せずSTOP)。
- 費用: **上限¥20**(確認用再生成: Hormuz Standard JA 5 segment+Advanced EN 6 segment 程度+Standard EN 2 segment、設計書概算¥10)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし報告。
- **実行安全(厳守)**: `--stage all`・TTS 全段階再実行禁止。対象 segment を明示した部分実行のみ。実行前に ACTIVE_TASK へ「対象 segment 一覧/想定 call 数/retry 上限(既存)/想定費用/Guardrail」を記録。**既存 Production run ディレクトリを上書きしない**(専用 out-dir、例 `er019_output/family_x_audio_production_wiring_01/variable_role_style_wiring_regression_01/hormuz/`)。Production Master Store の `manifest.json` は sha256 で作業前後不変(shell は reuse のみ、新規 Master 登録なし)。`reuse_telemetry.jsonl` の追記が起きる場合は開示。Bash timeout 前に segment 単位で分割実行。
- **Fable の設計判断(設計書 §7 論点への回答)**: (1) **JA(J3)の backend ゲートは EN 6-role と同一**=`--tts-backend speech_metadata_flash_lite` 明示時のみ有効、既定 backend は従来挙動のまま(Trial の J3 音声は Flash-Lite で検証されたため。既定 backend への拡張は Flash-Lite 既定化の別判断に委ねる)。(2) J3 は Trial(er044)と同じ **置換方式**(長文 `JAPANESE_STYLE_PREFIX` を J3 に置換)。(3) 適用範囲: JA=Family X Standard の preview/comment_1〜4 のみ(japanese_title・Key Phrase JA・固定 phrase は対象外)。EN=`FAMILY_X_ROLE_STYLE_EN` の TOPIC_INTRO/FULL_STORY/IN_ONE_LINE を E2 へ値更新(Role 定数は level 非依存のため Standard EN にも及ぶ。Standard の slower 指示との重畳は Regression で実測し REPORT に記載)。PREVIEW/COMMENT/HEADING_READOUT の EN Role は無変更。(4) 共有関数の既定値は None=従来挙動(Family A/B/C 無影響)。
- 禁止: 固定 phrase(shell)経路の変更、Master Store の変更、Key Phrase 系 Style の変更、新仕様の創作(J3/E2 は逐語)、数値 WPM 指定、リファクタリング。ユーザー向け表記は Standard/Advanced、TTS実行は 同期実行/バッチ実行。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)

E-1/D-1/G-1/F-1 標準(設計書は全文Read可。SSOT 全文Read禁止)。
T-0: 本委任文を `docs/pm/delegation_log/2026-09-28_TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01_02.md` へ逐語保存し、`.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-28_TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01_02.md --json-out docs/pm/delegation_log/2026-09-28_TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01_02.md_check.json` を実行し結果1行記録。
T-2: 確認用再生成は `TTS_EXECUTION_MODE=STANDARD`(同期実行)明示、`--tts-backend speech_metadata_flash_lite`、`--budget-jpy 20`、Production Store manifest 不変。
T-3: 上記「性質」欄の定型文に従う。

## 手順

1. **実装**(設計書 §3 (a)〜(e) 逐語): p9a ja 分岐の対称化(`style_prefix_override or JAPANESE_STYLE_PREFIX`)、`generate_a2_japanese_with_reading_safety`/`_with_fallback` に `style_prefix_override: str | None = None`(fallback 経路不変)、`er033` に `FAMILY_X_ROLE_STYLE_JA`(J3 逐語)+E2 値更新(3 Role)+`style_instruction_version` 相当の識別子があれば bump、`er019` に `_role_style_ja()`(backend ゲートは EN と同一条件)と A2 preview/comment_1〜4 への配線。各箇所に管理ID コメント。**runtime evidence**: `p9a.generate_narration_snippet` 戻り値に `style_prefix`(実文字列)を追加し、既存 audit(`tts_generation_results.json`)へ記録されることを確認。
2. **テスト**: 新規 `er019_family_x_variable_role_style_wiring_01_test_01.py`: (a) `FAMILY_X_ROLE_STYLE_JA` が er044 の J3 と逐語一致、E2 3 Role が er044 の E2 と逐語一致、(b) 既定 backend では JA style override が None(従来 PREFIX)である、Flash-Lite 明示時のみ J3、(c) `generate_a2_japanese_with_reading_safety` の既定呼び出しが従来と同一の prefix を渡す(モック)、(d) shell 固定 phrase の style 解決関数が本変更の影響を受けない(逐語不変)、(e) Key Phrase 系 Role 無変更、(f) fallback 経路が override を保持/または不変(設計どおり)。既存テスト(er033/er019/er038/er044 系の E0 リテラル assertion)は期待値更新のみ(理由をコメント)。`run_project_regression.py --pattern "er033*_test_*.py"`、`"er019*_test_*.py"`、`"er038*_test_*.py"`、`"er044*_test_*.py"`、新規テスト。全 PASS(pre-existing 失敗は OPEN-209 と照合)。
3. **確認用再生成(¥20内)**: Hormuz を専用 out-dir で、Standard JA(preview/comment_1〜4)・Advanced EN(topic_intro/full_story_part1〜3/heading/in_one_line)・Standard EN(full_story_part1/in_one_line、slower 重畳の実測)を **segment 指定の部分実行**で生成(TTS のみ、記事 text 再生成なし、shell は Store reuse)。証拠: audit の `style_prefix`/model/voice が J3/E2 と一致、ASR/drift 結果、retry 回数、費用実測、Production manifest sha256 不変。
4. **REPORT**: ユーザー Checklist を見出しに(初回 Production path/retry/fallback/regeneration/Local Rewrite 等の後続経路/fixed Master との競合なし/Trial 専用 script だけに残っていない/runtime evidence/actual model・voice・style metadata/ASR・drift/Regression/CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS/Git)。各項目に証拠(ファイル・行・コマンド・結果)。Fable 設計判断(backend ゲート、置換方式、適用範囲)を明記。Opus L2 論点(設計書 §7)を再掲。
5. **SSOT**(設計書 §6 文案ベース): `CURRENT_SPEC.md` の「可変 segment Role Style(J3/E2)— APPROVED_FOR_PRODUCTION(未配線)」小節(commit `d1ddf454` で追加済み)を「配線完了・Opus L2/Fable Gate 3 判定待ち」に更新し、適用範囲・backend ゲート・runtime evidence を追記(Status 文言は `APPROVED_FOR_PRODUCTION(配線完了、PRODUCTION_WIRED 判定待ち)`)。`DECISION_LOG.md` 末尾エントリ(実装内容、Fable 設計判断、Regression 結果、費用)。`OPEN_ITEMS.md`: OPEN-229 を「最小導入済み(Flash-Lite 明示時のみ)、既定 backend への拡張は Flash-Lite 既定化判断に従属」として更新(CLOSE は Fable Gate 3 後)、OPEN-201 追記。`docs/pm/REPORT_LEDGER.md`: WIRING-01 新行(`APPROVED_FOR_PRODUCTION(配線完了・L2/Gate 3 判定待ち)`、commit、Opus 発火=Phase B 後に L2 予定)。
6. 設計書 §8「Phase B 実施記録」追記。

## 事前指定Read一覧

- `docs/pm/design_tts_variable_role_style_production_wiring_01.md`(全文)
- `er003_b1_p9a_audio.py`: Grep `style_prefix_override|JAPANESE_STYLE_PREFIX|ENGLISH_STYLE_PREFIX|def generate_narration_snippet`
- `er003_v1_n3_01_tts_generate.py`: Grep `def generate_a2_japanese_with_reading_safety|def generate_a2_japanese_with_fallback`
- `er033_tts_flash_lite_family_x_styles_01.py`(全文)
- `er019_family_x_audio_production_runner_01.py`: Grep `_role_style|_resolve_shell_english_style_prefix_override|generate_a2_japanese|comment_|preview|tts_backend|speech_metadata_flash_lite`
- `er044_tts_variable_spoken_role_style_trial_02.py`: Grep `J3|E2|PATTERNS`

## 事前指定Grep一覧+追記位置・更新位置の手順

- `CURRENT_SPEC.md`: Grep `可変 segment Role Style|J3|E2` → 当該小節を更新。
- `DECISION_LOG.md`: Grep `PM-USER-DECISIONS-2026-09-28-AUDIO-TRIALS-SSOT-01` → 末尾に新エントリ。
- `OPEN_ITEMS.md`: Grep `OPEN-229|OPEN-201` → 本体行更新。
- `docs/pm/REPORT_LEDGER.md`: Grep `TTS-VARIABLE-SPOKEN-ROLE-STYLE-TRIAL-02` → 直後に新行。

## 実行コマンド全文

- `.venv\Scripts\python.exe -m unittest er019_family_x_variable_role_style_wiring_01_test_01 -v`
- `.venv\Scripts\python.exe run_project_regression.py --pattern "er033*_test_*.py"`(同様に er019/er038/er044)
- 確認用再生成: `TTS_EXECUTION_MODE=STANDARD .venv/Scripts/python.exe er019_family_x_audio_production_runner_01.py <segment 指定の部分実行引数> --tts-backend speech_metadata_flash_lite --out-dir "<専用 out-dir>" --budget-jpy 20`(runner の引数を確認して逐語記録。segment 指定ができない場合は runner を回さず、runner が使う生成関数を Trial と同様に直接呼ぶ小スクリプトで代替し、その旨を明記)
- `git diff --stat HEAD -- "er0*.py"`(本タスク由来=上記 4 ファイル+テスト。他は pre-existing として列挙)
- Production Store: `sha256sum er006_output/master_audio_store_01/manifest.json`(前後)
- `git status --porcelain CURRENT_SPEC.md DECISION_LOG.md OPEN_ITEMS.md docs/pm/REPORT_LEDGER.md docs/pm/PM_GOVERNANCE.md`(2回)

## SSOT追記文

上記手順 5。

## Git

- add対象(path指定のみ、`git add -A` 禁止): 変更 4 ファイル+更新した既存テスト+新規テスト、専用 out-dir の json/md(wav 非commit)、REPORT、設計書、SSOT 4点、delegation_log+`_check.json`。他Agent差分(er045/046/047 系、他 delegation_log 未追跡、er006 store 等)は add しない。
- メッセージ: `TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01: 可変segmentのRole Style(JA=J3/EN=E2)を正式経路へ配線(Flash-Lite明示時、固定Master非影響、共有関数は既定値で従来挙動)+runtime証拠+Regression+SSOT`、trailer `Management-ID: TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01`。`git push origin main`。実装 commit と SSOT commit を分けてもよい。

## 報告(RESULT_PACKET_VW1B + handback、目安30行)

Checklist 各項目の証拠要約/Fable 設計判断の適用結果/runtime 証拠(style_prefix・model・voice、segment 別)/ASR・drift・retry/費用実測/テスト結果/Production Store 不変の証拠/SSOT 適用箇所と差分所有者確認2回/禁止操作未実施/commit hash・push・raw URL/STOP有無/Opus L2 に渡す論点(設計書 §7 の再掲+実装で新たに気づいた点)。
