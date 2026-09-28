## 管理ID

FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(Phase B / W3=Japanese Title の J3 統一・cache version guard・runtime evidence(Opus L2 MAJOR-1/2/3・MINOR-A 是正)、委任 _03)。一時ファイル `docs/pm/ACTIVE_TASK_RF3.md` / `docs/pm/RESULT_PACKET_RF3.md`(commitしない)。並行: 別Sonnet 1件(W2: `er006_audio_cost_pilot_02_shared_narration.py`/`er006_master_audio_store_01.py`/`er048_*`/Production Master Store を編集中)→ これらに触れない。SSOT 4点+REPORT_LEDGER は編集権なし(文案のみ)。本タスクの所有: `er019_family_x_audio_production_runner_01.py`、`er003_b1_p9a_audio.py`、`er003_v1_sing01_voice01_generate.py`、`er003_v1_sing01_news_tail_fix.py`、`er003_v1_sing01_point_headings_aoede.py`、`er019_family_x_variable_role_style_wiring_01_test_01.py`(拡張)、REPORT `FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_REPORT.md` の §W3(W2 が同 REPORT を作成中のため、**自分の節は別ファイル `FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_REPORT_W3.md` に書き、統合は後続に委ねる**)、設計書 §9-W3 追記(設計書は W2 も追記するため、追記は末尾に自節のみ・push 競合時は merge)、delegation_log。**削除・移動・`rm`・`git clean`・stash/rebase/reset/amend/force push 禁止**。未追跡ファイルは他Agent/ユーザーの作業物として扱う。push競合時は `git merge origin/main` のみ。APIキー本文表示禁止。

## 性質/到達上限Status/禁止事項

- 性質: ユーザー正式決定の反映(Japanese Title も J3 系統へ統一=追加 Trial 不要)+Opus L2 所見(逐語は `TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01_REPORT.md` §Opus L2)の MAJOR-1/2/3・MINOR-A・MINOR-B 是正。到達上限 Status: `APPROVED_FOR_PRODUCTION`(Opus L2+Gate 判定待ち)。
- 費用: **上限¥0**(コード・テストのみ。runtime evidence の実測は後続の E2E で取得するため、本 W3 では有料再生成を行わない)。
- 禁止: J3/E2 文言の変更、shell(固定 phrase)経路・Key Phrase 経路の変更、共有関数の既定挙動変更(既定 None=従来)、W2 所有ファイルへの変更。ユーザー向け表記は Standard/Advanced。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)

E-1/D-1/G-1/F-1 標準。
T-0: 本委任文を `docs/pm/delegation_log/2026-09-29_FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_03.md` へ逐語保存し、`.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-29_FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_03.md --json-out docs/pm/delegation_log/2026-09-29_FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_03.md_check.json` を実行し結果1行記録。
T-2: TTSなし。T-3: API支出なし。

## 実装(Opus 所見の最小是正案に従う、逐語は REPORT §Opus L2 を参照)

1. **MAJOR-1 / Japanese Title**: `er019_family_x_audio_production_runner_01.py` L764-770 付近の japanese_title 生成に `style_prefix_override=_role_style_ja(...)`(preview/comment と同一関数・同一 backend ゲート)を渡す。Advanced(B1B)に日本語 Title 相当 segment があるか確認し、あれば同様に統一(なければ「該当なし」を記録)。
2. **MAJOR-3 / cache version guard**: `er019_family_x_audio_production_runner_01.py` に `FAMILY_X_VARIABLE_ROLE_STYLE_VERSION = "v2_j3_e2_title"`(値は設計判断で可、意味が分かる文字列)を新設し、`tts_generation_results.json` のトップレベルへ保存。`_load_cached_tts_results`/`_generate_or_reuse` で、cache の version が現行と不一致または欠落なら **可変 segment**(japanese_title/topic_intro/preview/comment_*/full_story_*/heading/in_one_line)の reuse を行わない(shell 固定 phrase・Key Phrase の reuse 判定は変更しない)。共有層に触れない。
3. **MAJOR-2 / runtime evidence(Advanced 英語経路)**: `er003_v1_sing01_voice01_generate.py`/`er003_v1_sing01_news_tail_fix.py`/`er003_v1_sing01_point_headings_aoede.py` の戻り値 dict へ `style_prefix`(実際に渡した最終文字列)・`tts_model_id`・`voice` が無ければ追加(既存キーは変更しない、追加のみ)。runner の audit(`tts_generation_results.json`)へ伝播することを単体テスト(モック)で確認。
4. **MINOR-A / 既定時ラベル化**: `er003_b1_p9a_audio.py` の `style_prefix` 記録を、`style_prefix_override` 指定時は実値、既定時は `"<default:ENGLISH_STYLE_PREFIX>"`/`"<default:JAPANESE_STYLE_PREFIX>"` に(Opus 案どおり。200 字 truncate は不採用)。上記 3 の 3 ファイルも同方針。
5. **MINOR-B**: REPORT_W3 に「runner 配線=単体テスト、style 反映=E2E 実測」の 2 段構成である旨を明記(E2E は後続)。
6. **テスト**(`er019_family_x_variable_role_style_wiring_01_test_01.py` 拡張または新規): japanese_title に J3 が渡る(Flash-Lite 明示時)/既定 backend では None/cache version 不一致で可変 segment が reuse されない・一致で reuse される・shell と KP の reuse 判定は不変/3 ファイルの戻り値に evidence キーが存在し値が渡した文字列と一致/既定時ラベルが記録される。既存 regression: `run_project_regression.py --pattern "er019*_test_*.py"`、`"er003*_test_*.py"`(該当があれば)、`"er033*_test_*.py"`、`"er044*_test_*.py"` 全 PASS(pre-existing 失敗は OPEN-209 と照合)。
7. AN3 reminder 不在の再確認(ユーザー指示 4): `grep -n "再び増やさない" er0*.py`(Production 側 0 件)、`er019_family_x_ja_writer_o_r1_r2_01.py` の R1/R2・must-fix・symbol・fallback 経路に `CONCRETENESS_CONTROL_AN3_REMINDER` が無いことを Grep で確認し REPORT_W3 に記録(変更なし)。

## 事前指定Read一覧

- `TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01_REPORT.md`: Grep `MAJOR-1|MAJOR-2|MAJOR-3|MINOR-A|MINOR-B` → 該当範囲
- `er019_family_x_audio_production_runner_01.py`: Grep `japanese_title|_role_style_ja|_generate_or_reuse|_load_cached_tts_results|tts_generation_results|FAMILY_X_VARIABLE`
- `er003_b1_p9a_audio.py`: Grep `style_prefix|def generate_narration_snippet`
- `er003_v1_sing01_voice01_generate.py` / `er003_v1_sing01_news_tail_fix.py` / `er003_v1_sing01_point_headings_aoede.py`: Grep `style_prefix_override|return \{|instruction_type|model|voice`
- `er019_family_x_variable_role_style_wiring_01_test_01.py`(全文)

## 事前指定Grep一覧+追記位置・更新位置の手順

- Grep対象: 上記。更新位置: 所有 5 ファイル+テスト、REPORT_W3(新規)、設計書末尾 §9-W3。

## 実行コマンド全文

- `.venv\Scripts\python.exe -m unittest er019_family_x_variable_role_style_wiring_01_test_01 -v`
- `.venv\Scripts\python.exe run_project_regression.py --pattern "er019*_test_*.py"`(同様に er003/er033/er044)
- `grep -n "再び増やさない" er0*.py`
- `git diff --stat HEAD -- "er0*.py"`(本タスク由来=所有 5 ファイル+テスト。W2 所有ファイルは含まれないこと)

## SSOT追記文

RESULT_PACKET へ文案のみ(CURRENT_SPEC「可変 segment Role Style」小節の更新案[japanese_title 含む、cache version、runtime evidence の範囲=Advanced 英語経路も記録]、OPEN-229 更新案、DECISION_LOG)。

## Git

- add対象(path指定のみ、`git add -A` 禁止): 所有 5 ファイル、テスト、REPORT_W3、設計書、delegation_log+`_check.json`。W2 の差分・他 Agent 差分は add しない。
- メッセージ: `FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01 (W3): Japanese TitleへJ3統一+可変Role Styleのcache version guard+Advanced英語経路のruntime evidence+既定時ラベル化(Opus L2 MAJOR-1/2/3・MINOR-A是正)`、trailer `Management-ID: FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01`。`git push origin main`。

## 報告(RESULT_PACKET_RF3 + handback、目安25行)

変更箇所(ファイル・行)/テスト・regression 結果/reminder 不在の確認結果/費用(¥0)/Opus L2 論点(残存: MINOR-C の SSOT 文言は SSOT 反映時)/commit hash・raw URL/STOP 有無。
