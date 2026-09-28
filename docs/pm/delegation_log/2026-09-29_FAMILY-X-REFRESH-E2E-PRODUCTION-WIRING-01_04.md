## 管理ID

FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(Phase B / W1=新記事構造(途中Heading廃止・忠実英訳・段落境界3分割・Comment1〜4・In One Line・Heading Readout撤去)の Production 正式経路への配線+JA 入力(er039 AN3-T0 セル)の機械検証、委任 _04)。一時ファイル `docs/pm/ACTIVE_TASK_RF1.md` / `docs/pm/RESULT_PACKET_RF1.md`(commitしない)。並行 Agent なし(W2 `2ecb0c64`・W3 `3fc45986` は完了・push 済み。`git pull`(ff)で最新化してから着手)。SSOT 4点+REPORT_LEDGER は編集権なし(文案のみ)。**削除・移動・`rm`・`git clean`・stash/rebase/reset/amend/force push 禁止**。未追跡ファイルは他Agent/ユーザーの作業物として扱う。push競合時は `git merge origin/main` のみ。APIキー本文表示禁止。

## 性質/到達上限Status/禁止事項

- 性質: ユーザー正式決定(`APPROVED_FOR_PRODUCTION`、DECISION_LOG に記録済み)の Production 配線。到達上限 Status: `APPROVED_FOR_PRODUCTION`(配線完了、Opus L2+E2E Gate 判定待ち)。**Trial ではない**。
- 決定済み構造(逐語、再設計禁止): 途中 Heading(h3)を廃止/日本語記事 → 忠実英訳(er045 `FAMILY-X-TRANSLATION-SEGMENTATION-NO-HEADING-TRIAL-01` の faithful translation Prompt を逐語採用)/段落境界で body1/2/3 に決定論的 3 分割(er045 の分割アルゴリズム)/音声順 Comment1 → body1 → Comment2 → body2 → Comment3 → body3 → Comment4 → In One Line/Heading Readout 撤去/In One Line は短い一文(er045 v2 の brevity guide、**語数目標は目安であり絶対上限にしない=語数超過で FAIL にしない**)/既存 Deviation Check → MAJOR 時 must-fix retry 1 回 維持。Standard/Advanced 両方に同じ構造。AN3-T0 = A3+N2 は Original(JA)側のみ、reminder なし(変更しない)。
- 費用: **上限¥0**(本 W1 はコード・テスト・入力検証のみ。LLM/TTS 呼び出しは mock。E2E 実測は次 Phase)。有料呼び出しが必要と判明したら STOP。
- 禁止: er045 の Prompt 文言変更(逐語転記・sha256 記録)、`split_article_text()`(他 Family 共用)の既存挙動変更(**新関数 `split_family_x_article_text_v2()` を追加し Family X 経路のみ切替**)、Family A/B/C/Z の経路変更、shell/KP/Master 経路の変更、W2/W3 で入れた `SHELL_CHAMPION_*`・`FAMILY_X_VARIABLE_ROLE_STYLE_VERSION`・style_prefix evidence の変更、TTS 共通層の意味変更(共有 TTS 層に触る必要が出たら STOP)。ユーザー向け表記は Standard/Advanced。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)

E-1/D-1/G-1/F-1 標準。
T-0: 本委任文を `docs/pm/delegation_log/2026-09-29_FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_04.md` へ逐語保存し、`.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-29_FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_04.md --json-out docs/pm/delegation_log/2026-09-29_FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_04.md_check.json` を実行し結果1行記録。
T-2: TTSなし。T-3: API支出なし(¥0)。

## 実装(設計書 `docs/pm/design_family_x_refresh_e2e_production_wiring_01.md` §3(a)(b)・§4 を根拠。逸脱は理由記録)

1. **忠実英訳 Prompt の Production 化**: er045 の faithful translation Prompt 定数(`er045_*.py`)を Production writer 経路(`er019_family_x_entertainment_production_runner_01.py` → `er012_e_family_entertainment_two_level_runner_01.py::run_writer_stage()` の EN 生成段)へ逐語転記または import(import なら er045 が Trial 専用ファイルであることに注意=Production から Trial ファイルを import しない方針なら `er019_family_x_translation_prompts_01.py` 等の Production 定数ファイルへ転記し sha256 で同一性テスト)。Deviation Check → MAJOR 時 must-fix retry 1 回は er045 で Production 同等として実施した経路を Production へ組込み(既存 `run_writer_with_technical_retry`/`validate_point_structure` の h3_count==2 判定は新構造では不要になるため、Family X 経路では h3 非依存の新 validator へ置換。他 Family の validator は不変)。
2. **3 分割**: `er003_v1_n3_01_scaffold_generate.py` に `split_family_x_article_text_v2()` を追加(er045 の決定論的段落境界 3 分割を移植、単体テストで er045 の Hormuz/Meta 出力と同一分割になることを確認)。Family X 経路の `split_article_text()` 呼び出しを v2 へ切替。**intro ≥2 段落 RuntimeError(OPEN-228 の gate)は Family X 新経路では到達不能**になることをテストで証明(旧 gate は削除せず、Family X 経路から外すだけ)。
3. **Advanced 側**: `er003_v1_n3_01_advanced_adaptation_generate.py` の Advanced adaptation が新構造(Heading なし・body1/2/3)を入力として受け、段落の merge/reorder(ARM3)を行っても **3 分割が段落境界で成立する**よう、Advanced 出力に対しても同じ v2 split を適用(Advanced adaptation Prompt 自体は変更しない。段落数が 3 未満になった場合の扱いは設計書 §3(b) に従い、無ければ「must-fix retry 1 回 → それでも不足なら STOP(E2E で顕在化)」として実装し、Standard/Advanced の非対称にならないことを記録)。
4. **音声側**(`er019_family_x_audio_production_runner_01.py`、W3 の変更は保持): Heading Readout segment の生成・組立を Family X 経路から撤去(`FAMILY_X_ROLE_STYLE_EN["HEADING_READOUT"]` 定数は削除せず未使用として残す)。組立順を Comment1 → body1(full_story_part1)→ Comment2 → body2 → Comment3 → body3 → Comment4 → In One Line へ(前段の welcome/preview/KP/full_story_intro は現行どおり)。`verify_episode_audio_validation_gate`/Audio Validation の parts 一覧を新構造(heading 不在、comment_4 追加、body 3 分割)へ更新。Comment 4 本(Comment1〜4)の生成経路が Standard/Advanced 双方に存在することを確認。`resolve_narrative_role()` 等 Connected Speech が full_story_part1/2/3 を引き続き認識することをテスト。
5. **JA 入力の機械検証(¥0)**: `er039_output/family_xy_concreteness_control_trial_02/{hormuz,meta}/cells/AN3-T0_ja.md` について、(a) sha256、(b) 生成時 Prompt が現行 Production `build_original_prompt()` と同一構成(`concreteness_an3_block_sha256` 等 `verbatim_shas()` の一致、reminder 文字列 `再び増やさない` 不在)、(c) `AN3-T0_deviation.json` が LEDGER_COMPLIANT、(d) `SYMBOL_PREVENTION` 準拠(記号正規化チェック関数で 0 違反)、(e) 段落数 ≥3(v2 split が成立)を検証し、結果を REPORT §W1 に表で記録。**すべて満たせば E2E の JA 入力として採用可**、1 つでも不成立なら STOP(再生成の要否はユーザー判断)。E2E 用の入力配置先パス(例 `er019_output/family_x_refresh_e2e_01/{hormuz,meta}/input/article_ja.md`+provenance.json)へコピー(元ファイルは不変)。
6. **テスト** `er019_family_x_new_structure_wiring_01_test_01.py`(新規): Prompt sha256 同一性/v2 split が er045 出力と一致/OPEN-228 gate 到達不能/Advanced 出力の v2 split と retry 分岐/Heading Readout 不在・comment_4 存在・組立順/Audio Validation parts/Connected Speech role 認識/In One Line 語数超過で FAIL しない/Standard・Advanced の段構成対称性。既存 regression: `run_project_regression.py --pattern "er019*_test_*.py"`、`"er012*_test_*.py"`、`"er003*_test_*.py"`(pre-existing 失敗は OPEN-209 と照合し W1 非起因を明記)、`"er045*_test_*.py"`、`"er033*_test_*.py"`、`"er048*_test_*.py"` 全 PASS。
7. **REPORT**: `FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_REPORT.md` へ §W1 を追記(W2 節の後、W3 は別ファイル `_REPORT_W3.md` のまま=統合は E2E 後)。変更ファイル・行、Prompt sha256、split 一致証拠、JA 入力検証表、テスト結果、費用 ¥0、Opus L2 論点(Advanced 段落数不足時の分岐、h3 validator 置換の他 Family 非影響、旧 gate の残置)。設計書 §9-W1 追記。

## 事前指定Read一覧

- `docs/pm/design_family_x_refresh_e2e_production_wiring_01.md`: §3(a)(b)、§4、§9-W2/W3(完了内容の把握)
- `er045_*.py`: Grep `PROMPT|def split|IN_ONE_LINE|brevity|def .*deviation|MAJOR|must_fix`
- `er003_v1_n3_01_scaffold_generate.py`: Grep `def split_article_text|RuntimeError|intro|validate_point_structure|h3`
- `er012_e_family_entertainment_two_level_runner_01.py`: Grep `def run_writer_stage|split_article_text|run_writer_with_technical_retry|advanced_adaptation`
- `er003_v1_n3_01_advanced_adaptation_generate.py`: Grep `ARM3|reorder|merge|build_must_fix_block|def generate`
- `er019_family_x_audio_production_runner_01.py`: Grep `HEADING_READOUT|heading|comment_|full_story_part|in_one_line|verify_episode_audio_validation_gate|parts|_role_style_ja|style_version`
- `er019_family_x_entertainment_production_runner_01.py`: Grep `run_writer_stage|split|advanced|deviation`
- `er019_family_x_ja_writer_o_r1_r2_01.py`: Grep `def verbatim_shas|concreteness_an3_block_sha256|SYMBOL_PREVENTION|REMINDER`
- `er039_output/family_xy_concreteness_control_trial_02/{hormuz,meta}/cells/`: `AN3-T0_ja.md`(全文可、短い)、`AN3-T0_deviation.json`、provenance/prompt sha を含む json(Grep `sha256|reminder|prompt`)
- `er020_tts_retry_local_rewrite_01.py` / Connected Speech: Grep `def resolve_narrative_role|full_story_part`(**読むだけ、編集しない**=Family Z 側の所有予定)

## 事前指定Grep一覧+追記位置・更新位置の手順

- Grep対象: 上記。更新位置: `er003_v1_n3_01_scaffold_generate.py`(関数追加のみ)、`er012_e_family_entertainment_two_level_runner_01.py`(Family X 分岐)、`er003_v1_n3_01_advanced_adaptation_generate.py`(split 適用・retry 分岐、Prompt 不変)、`er019_family_x_entertainment_production_runner_01.py`、`er019_family_x_audio_production_runner_01.py`、新規 Production 定数ファイル(必要時)、新規テスト、REPORT §W1、設計書 §9-W1、delegation_log。

## 実行コマンド全文

- `git pull --ff-only origin main`
- `.venv\Scripts\python.exe -m unittest er019_family_x_new_structure_wiring_01_test_01 -v`
- `.venv\Scripts\python.exe run_project_regression.py --pattern "er019*_test_*.py"`(同様に er012/er003/er045/er033/er048)
- `certutil -hashfile er039_output\family_xy_concreteness_control_trial_02\hormuz\cells\AN3-T0_ja.md SHA256`(meta も)
- `grep -n "再び増やさない" er0*.py er039_output/family_xy_concreteness_control_trial_02/*/cells/*`
- `git diff --stat HEAD -- "er0*.py"`(本タスク由来のみ)

## SSOT追記文

RESULT_PACKET へ文案のみ(CURRENT_SPEC「Family X 記事構造」小節の更新案[新構造=Production 配線済み(E2E Gate 待ち)、旧 h3 構造は廃止]、OPEN-228 の CLOSED/SUPERSEDED 文案[新構造で gate 到達不能]、OPEN-230 更新案、DECISION_LOG)。

## Git

- add対象(path指定のみ、`git add -A` 禁止): 上記更新位置のファイル、新規テスト、REPORT、設計書、delegation_log+`_check.json`、E2E 入力配置先(`er019_output/family_x_refresh_e2e_01/*/input/*`)。他 Agent 差分・未追跡ファイルは add しない。
- メッセージ: `FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01 (W1): 新記事構造(途中Heading廃止・忠実英訳・段落境界3分割・Comment1〜4・Heading Readout撤去)をFamily X Production経路へ配線、OPEN-228 gateを新経路から除外、er039 AN3-T0セルをE2E JA入力として機械検証`、trailer `Management-ID: FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01`。`git push origin main`。

## 報告(RESULT_PACKET_RF1 + handback、目安35行)

変更箇所/Prompt sha256/split 一致証拠/OPEN-228 gate 到達不能の証明/Advanced 段落数不足時の分岐/JA 入力検証表(hormuz/meta × (a)〜(e))/テスト・regression 結果/費用 ¥0/Opus L2 論点/commit hash・raw URL/STOP 有無。
