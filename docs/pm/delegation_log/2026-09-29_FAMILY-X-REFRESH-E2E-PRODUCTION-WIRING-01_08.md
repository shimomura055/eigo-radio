## 管理ID

FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(Phase B / W5=Opus L2 所見の是正(BLOCKER-1+MAJOR-1〜4)+Standard KP 日本語意味への J3 配線+E2E 前 ¥0 Gate、委任 _08)。一時ファイル `docs/pm/ACTIVE_TASK_RF5B.md` / `docs/pm/RESULT_PACKET_RF5B.md`(commitしない)。並行 Agent なし(`git pull --ff-only origin main` で最新化、HEAD は `cd7b8e50` 以降)。**SSOT 4点(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS)は本タスクが編集権を持つ(直列化: 他 Agent なし)**。**削除・移動・`rm`・`git clean`・stash/rebase/reset/amend/force push 禁止**。未追跡ファイルは他Agent/ユーザーの作業物として扱う。push 競合時は `git merge origin/main` のみ。APIキー本文表示禁止。

## 性質/到達上限Status/禁止事項

- 性質: ユーザー判断(2026-09-29)により、BLOCKER-1/MAJOR-1〜4 は「既承認仕様から一意に決まる実装是正」(USER_DECISION_REQUIRED ではない)。Standard KP 日本語意味への J3 適用は **正式決定 `APPROVED_FOR_PRODUCTION`**(Standard 正式構造 = 英語 Phrase → 日本語意味(J3) → 同じ英語 Phrase/Advanced = 英語 Phrase → 英語解説(Variant B) → 同じ英語 Phrase)。到達上限 Status: `APPROVED_FOR_PRODUCTION`(Gate 3 完了までは `PRODUCTION_WIRED` と書かない)。
- 費用: **上限¥0**(mock/regression/static のみ)。
- **STOP 条件**: 新しい Product 仕様や未承認 Prompt 変更が必要になった場合のみ STOP(ユーザー指示逐語)。それ以外は最後まで実施。
- 禁止: J3/E2/Variant B/解説 Prompt/忠実英訳 Prompt/A2 Prompt の文言変更(Gate 追加は Prompt 変更ではないので可)、共有 TTS 層(`er003_b1_p9a_audio.py` 等)の既定挙動変更、Family A/B/C/Z の経路変更、W1〜W4 の承認済み構造の変更、`--stage all` の使用。ユーザー向け表記は Standard/Advanced。

## 固定ブロック

E-1/D-1/G-1/F-1 標準。T-0: 本委任文を `docs/pm/delegation_log/2026-09-29_FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_08.md` へ逐語保存し `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-29_FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_08.md --json-out docs/pm/delegation_log/2026-09-29_FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_08.md_check.json` を実行し結果1行記録。T-2: TTS なし。T-3: API 支出なし。

## 実装(Opus 所見の逐語は REPORT `FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_REPORT.md` 行 459〜548。各「最小是正案」に従う。逸脱は理由記録)

### A. BLOCKER-1: KP 英語解説の fail-closed
`er019_family_x_audio_production_runner_01.py`(:726-736 付近)と `er019_family_x_kp_explanation_01.py`(:275-298): text-gate status が `OK` 以外(`NG`/`NG_ACCEPTED_AFTER_RETRY`/`NG_PHRASE_MISMATCH`/parse 失敗)の rank は **TTS を呼ばず**、`kp_results[rank]["explanation"]` に `status="STOPPED"`+reason(text-gate status・NG 理由)を記録。`NG_ACCEPTED_AFTER_RETRY` という「採用」ステータスは廃止(retry 1 回後も NG なら `NG` のまま STOPPED)。既存 `verify_episode_audio_validation_gate` が `kp{rank}_explanation=STOPPED` で assembly を block し、既存 `record_human_approval()` 経路で人間承認可能であることをテストで確認。空文字を TTS へ渡す経路を排除。

### B. MAJOR-1: KP explanation cache guard
`_generate_or_reuse_kp()`(:421-428)に `expected_text` と `style_version` 判定を追加: role="explanation" では cached の text/canonical_text と現 `explanation_text` の一致、かつ `cached.get("style_version") == FAMILY_X_VARIABLE_ROLE_STYLE_VERSION` を reuse 条件に(可変 segment の `_generate_or_reuse` と同一方針)。english role(used_form 変化)にも text 一致 guard を適用(Opus 推奨)。`explanation_text` を canonical text として audit に明示記録。既存テスト `er019_family_x_kp_structure_wiring_01_test_01.py:391-427` を新挙動に更新(理由コメント)。W3 の shell 固定 phrase の reuse 判定は不変。

### C. MAJOR-2: Standard 構造 Gate の対称化
`split_family_x_article_text_v2()`(`er003_v1_n3_01_scaffold_generate.py:185-243`)に構造検査を持たせ、両レベル共通で: (1) `^#\s+` の title 行必須(欠落なら status NG、title="" のまま OK を返さない)、(2) `## In one line` 必須(RuntimeError ではなく status NG)、(3) body 内に Markdown heading 行(`^#{1,6}\s`)混入禁止。`_family_x_ensure_split_or_paragraph_retry()`(`er012_e_family_entertainment_two_level_runner_01.py:293-315`)がこの NG を捕まえ、既存方針(retry 1 回、must-fix 相当の指示)で Standard/Advanced 対称に retry。retry 後も NG なら既存 deviation 方針と同様に STOP(課金後クラッシュではなく明示 STOP 記録)。`generate_family_x_standard_a2_no_heading()` の parse gate を Advanced(`_FAMILY_X_TITLE_BODY_RE`)と対称化。N-2(must-fix ヘッダが Fact Safety/日本語記事言及で Standard に不整合)は段落 retry 用の文言を Standard 向けに最小修正(Prompt 本文は不変、retry 指示ブロックのみ。**これは既存 must-fix 指示の整合修正であり新 Prompt ではない**が、変更前後の文言を REPORT に併記)。

### D. MAJOR-3: TTS backend fail-fast
`er019_family_x_audio_production_runner_01.py`: (1) tts stage 開始前に `tts_backend == "speech_metadata_flash_lite"`(承認済み正式 backend)でなければ Production E2E を開始せず RuntimeError(明示メッセージ)+`entry_point.json` に backend を記録。legacy backend は Trial/regression 用途の明示 opt-in flag(例 `--allow-legacy-backend`)がある場合のみ許可(既存テストの互換維持のため)。(2) KP 解説 style(`:733` の `KEY_PHRASE_EXPLANATION_EN` 無条件適用)を `_role_style()` と同じ backend gate に揃える。

### E. MAJOR-4: OPEN-228 旧 gate の非 writer 到達経路の封鎖
`er012_e_family_entertainment_two_level_runner_01.py`: `--stage` の choices を `ledger/writer` に限定(または scaffold/tts/assemble/player/all を選ぶと「Family X は `er019_family_x_audio_production_runner_01.py` を使う」旨の RuntimeError で fail-fast)。`run_scaffold_stage()` → `sc.run_theme_scaffold()` → 旧 `split_article_text()` の経路が Family X から到達不能であることをテスト(AST または呼び出し試験)で証明し、OPEN-228 CLOSED 根拠文(「旧 gate は残置、Family X 新経路からは到達しない(er012_e の非 writer stage は封鎖済み)」)を成立させる。

### F. Standard KP 日本語意味への J3 配線(正式決定)
`er019_family_x_audio_production_runner_01.py`(:951-956 付近、japanese_meaning 生成)に `style_prefix_override=_role_style_ja()`(japanese_title/preview/comment と同一関数・同一 backend gate)を渡す。確認項目(ユーザー指示逐語、各々テストで証明): 「Standard KP 日本語意味の Production 正式 initial path」「retry / fallback / regeneration」「cache reuse」「style/version guard」「実際の runtime style evidence」「他の日本語 Role への意図しない波及がないこと」。KP japanese role の reuse は B の text guard+style_version guard に含める。runtime evidence は `tts_generation_results.json` の該当 segment に `style_prefix` 実文字列(J3)が記録されること(mock で検証、E2E で実測)。Advanced には japanese_meaning segment がないことを再確認。

### G. MINOR の同梱(コード最小)
- N-7: `EXPLANATION_JSON_SCHEMA` の minItems/maxItems を `len(items)` から導出(5 固定廃止)。
- N-8a: er040/er043 凍結スクリプトが旧シグネチャで再実行不能になった事実を REPORT §W2 補遺に記録(TODO にしない)。
- N-8b: REPORT §W2 の「shared_narration を参照するのは Family X のみ」を「47 ファイルが import、Production runner も呼ぶが、`tts_backend` gate による version 固定で他 Family は不変」へ訂正。
- N-4: Master Store reuse 返り値に `key.as_dict()`(model/voice/style_instruction_id/version/canonical_text)を追加(`er006_master_audio_store_01.py:115-133`、追加のみ・既存キー不変)→ Gate 6 の追跡を join 不要に。
- N-1/N-3(解消)/N-5/N-6/N-9 は REPORT に「E2E 実測/後追い」と分類し、N-5/N-9 は OPEN_ITEMS 新設候補として文案(新設は SSOT 反映時に実施可)。

### H. E2E 前 ¥0 Gate(ユーザー指示の 6 項目、REPORT に表で evidence)
(1) BLOCKER 解消 (2) MAJOR-1〜4 解消 (3) J3 正式配線確認(Title/preview/comment/KP 日本語意味の 4 経路すべて `_role_style_ja()`)(4) dangling reference なし(削除・改名した関数/定数/status 名の参照残り 0 件を Grep で証明、`NG_ACCEPTED_AFTER_RETRY`・`HEADING_READOUT` 参照等)(5) retry / fallback 整合(6) Standard/Advanced の意図しない非対称なし(segment 列・parts・Audio Validation・player の対比表)。加えて Opus「E2E で実測確認すべき項目」9 件を **E2E Gate チェックリスト**として REPORT に転記し、E2E 実行手順書(§E2E-PLAN)を固定: 実行コマンド全文(`--tts-backend speech_metadata_flash_lite`、`--stage` 個別、段階別 `--budget-jpy`、`TTS_EXECUTION_MODE=STANDARD`)、対象 segment 数・想定 call 数・retry 上限・想定費用・Guardrail(記事×レベルごと)、`er012_e` は `--stage writer` のみ、`--stage all` 禁止。

### I. テスト
新規 `er019_family_x_opus_l2_fixes_01_test_01.py`(A〜G 各項目の mock テスト)+既存テスト更新。regression: `run_project_regression.py --pattern "er019*_test_*.py"`、`"er012*_test_*.py"`、`"er003*_test_*.py"`、`"er006*_test_*.py"`、`"er033*_test_*.py"`、`"er045*_test_*.py"`、`"er048*_test_*.py"` 全 PASS(pre-existing 失敗は根拠付きで非起因明記)。

### J. SSOT 反映(本タスクで実施、決定の逐語記録)
- CURRENT_SPEC: 「Key Phrase 音声構造」小節へ「Standard 日本語意味に J3 適用(2026-09-29 正式決定、`APPROVED_FOR_PRODUCTION`、配線済み・Gate 3 待ち)」を追記、Standard 正式構造 `英語Phrase → 日本語意味(J3) → 同じ英語Phrase`/Advanced `英語Phrase → 英語解説(Variant B) → 同じ英語Phrase` を明記。「可変 segment Role Style」小節の J3 適用範囲に KP 日本語意味を追加。
- DECISION_LOG: 新エントリ(決定逐語: 「Standard Key Phrase の日本語意味にも J3 を適用」+ Opus BLOCKER/MAJOR は既承認仕様から一意に決まる実装是正として扱う旨)。
- OPEN_ITEMS: OPEN-228 は **まだ CLOSED にしない**(E2E Gate 後に Fable 判定)が、封鎖完了と CLOSED 根拠文案を追記。N-5/N-9 を新 OPEN として登録(番号は既存最大+1)。
- `PRODUCTION_WIRED` とは書かない。

## 事前指定Read一覧

- REPORT 行 459〜548(Opus 所見)、設計書 §3・§9
- 上記 A〜F の各ファイル該当行(Grep 起点: `NG_ACCEPTED_AFTER_RETRY|_generate_or_reuse_kp|explanation|japanese_meaning|_role_style_ja|tts_backend|structured_separation|KEY_PHRASE_EXPLANATION_EN|split_family_x_article_text_v2|_family_x_ensure_split_or_paragraph_retry|run_scaffold_stage|choices=|EXPLANATION_JSON_SCHEMA|def reuse|master_audio_id`)
- テスト: `er019_family_x_kp_structure_wiring_01_test_01.py`、`er019_family_x_new_structure_wiring_01_test_01.py`、`er019_family_x_variable_role_style_wiring_01_test_01.py`

## 実行コマンド全文

- `git pull --ff-only origin main`
- `.venv\Scripts\python.exe -m unittest er019_family_x_opus_l2_fixes_01_test_01 -v`
- `.venv\Scripts\python.exe run_project_regression.py --pattern "er019*_test_*.py"`(同様に er012/er003/er006/er033/er045/er048)
- `grep -n "NG_ACCEPTED_AFTER_RETRY" er0*.py`(0 件を期待)
- `git diff --stat HEAD`(本タスク由来のみ)

## Git

- commit は 2 つに分ける: (1) コード+テスト+REPORT+設計書+delegation_log、メッセージ `FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01 (W5): Opus L2是正(KP解説fail-closed、KP cache text/version guard、Standard構造Gate対称化、TTS backend fail-fast、er012_e非writer stage封鎖)+Standard KP日本語意味へJ3配線+E2E前¥0 Gate・E2E手順書`;(2) SSOT 3 ファイル、メッセージ `FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01: SSOT反映(Standard KP日本語意味J3=APPROVED_FOR_PRODUCTION、Opus是正5件の実装記録、OPEN-228封鎖根拠、新OPEN登録)`。いずれも trailer `Management-ID: FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01`、path 指定 add、push。

## 報告(RESULT_PACKET_RF5B + handback、目安40行)

A〜G の変更箇所(ファイル:行)/H の 6 項目 Gate 表(evidence 付き)/E2E 手順書の所在と段階別コマンド・費用計画/テスト・regression 結果/dangling reference 0 件の証拠/SSOT 更新箇所/費用 ¥0/commit hash 2 件・raw URL/STOP 有無(新 Product 仕様・未承認 Prompt 変更が必要になった場合のみ)。
