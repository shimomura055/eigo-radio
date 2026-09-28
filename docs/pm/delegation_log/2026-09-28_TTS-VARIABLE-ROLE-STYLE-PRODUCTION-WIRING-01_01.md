## 管理ID

TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01(Phase A=設計・既存仕様確認のみ、委任 _01)。一時ファイル `docs/pm/ACTIVE_TASK_VW1.md` / `docs/pm/RESULT_PACKET_VW1.md`(commitしない)。並行: 別Sonnet 4件(Task 1 `er045_*`、Task 2 `er046_*`、Task 3 `er047_*`、SSOT反映Agent[SSOT 4点+REPORT_LEDGER 編集中])→ 触れない。SSOT は Grep のみ(編集権なし)。本タスクの所有: 新規 `docs/pm/design_tts_variable_role_style_production_wiring_01.md`、delegation_log。**Phase A では Production code・Prompt・SSOT・Trial script を一切変更しない(設計書のみ)。API 支出 上限¥0。削除・移動・`rm`・`git clean`・stash/rebase/reset/amend/force push 禁止。未追跡ファイルは他Agent/ユーザーの作業物として扱う。push競合時は `git merge origin/main` のみ。APIキー本文表示禁止。**

## 性質/到達上限Status/禁止事項

- 性質: Production Wiring の Phase A(設計)。**ユーザー正式決定: 日本語=J3、英語=E2、`APPROVED_FOR_PRODUCTION`**(`TTS-VARIABLE-SPOKEN-ROLE-STYLE-TRIAL-02`)。Phase A 完了時点では `APPROVED_FOR_PRODUCTION`(未配線)のまま。`PRODUCTION_WIRED` は Phase B 後の Fable Gate 3 判定のみ。共有 TTS 層の変更を含むため、Phase B 実装後に Opus L2 レビュー(Mandatory)を予定。
- 適用範囲(ユーザー指示): 日本語=J3 の実際の Style 文言をそのまま、対象となる可変日本語 segment へ適用(固定 Master phrase には適用しない)。英語=E2 を FULL_STORY/IN_ONE_LINE/Trial で E2 対象になっていた可変英語 Role(TOPIC_INTRO)へ整合して配線。
- 禁止: 新仕様の創作(Trial の文言を逐語使用)、固定 phrase(Master)への適用、Family A 等の共有経路の挙動変更(既定値で従来挙動を維持する設計にする)、数値 WPM 指定。ユーザー向け表記は Standard/Advanced、TTS実行は 同期実行/バッチ実行。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)

E-1/D-1/G-1/F-1 標準。
T-0: 本委任文を `docs/pm/delegation_log/2026-09-28_TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01_01.md` へ逐語保存し、`.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-28_TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01_01.md --json-out docs/pm/delegation_log/2026-09-28_TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01_01.md_check.json` を実行し結果1行記録。
T-2: TTSなし。T-3: API支出なし。

## Phase A の作業(設計書)

1. **Trial 文言の逐語抽出**: `er044_tts_variable_spoken_role_style_trial_02.py` から J3・E2(FULL_STORY/IN_ONE_LINE/TOPIC_INTRO)の最終 style 文字列を逐語抽出(生成結果 json の `style_prefix_used` と一致することも確認)。
2. **Existing Spec Check(Grep 先・行を記録)**: (a) 英語: `er033_tts_flash_lite_family_x_styles_01.py` の `FAMILY_X_ROLE_STYLE_EN`(現行 E0 文言・Role 一覧・`FAMILY_X_ROLE_STYLE_EN_FALLBACK`)、`er019_family_x_audio_production_runner_01.py` の `_role_style`/`_role_style_slower`/`A2_SLOWER_PACE_INSTRUCTION`(Standard の EN に slower 指示や 6% post-process があるか、E2 との重畳の扱い)、Role→segment の対応(topic_intro/full_story_part1〜3/heading/in_one_line/comment_* が EN で使う Role)。(b) 日本語: `er003_b1_p9a_audio.py` の `JAPANESE_STYLE_PREFIX` と `generate_a2_japanese_with_reading_safety`(style override パラメータ不在=OPEN-229)、その呼び出し元一覧(`er0*.py` 全体を Grep `generate_a2_japanese_with_reading_safety|JAPANESE_STYLE_PREFIX`)→ Family A/B/Y/Z 等の共有状況、Family X runner が JA segment(preview/comment_1〜4、他にあれば列挙)を生成する箇所。(c) 固定 Master phrase(shell)経路が別定数(`er006_audio_cost_pilot_02_shared_narration.py`、Flash-Lite short style)であり、本配線の影響を受けないことの根拠。(d) `er006_master_audio_store_01.py` の `EQUALITY_FIELDS`/`style_instruction_id`/`version`(可変 segment は Store 対象外か、reuse telemetry への影響)。(e) retry/fallback/regeneration/Local Rewrite/segment 再生成/`--regenerate-stage` の各 path が同じ style 解決関数を通るか(表)。(f) `CURRENT_SPEC.md`(Grep `Role Style|6-role|JAPANESE_STYLE_PREFIX|落ち着いた|Standard.*slower|OPEN-201`)、OPEN-201/229/221/222/223/226。
3. **最小 diff 案(逐語)**: 英語=`FAMILY_X_ROLE_STYLE_EN` の FULL_STORY/IN_ONE_LINE/TOPIC_INTRO を E2 文言へ更新(または version 付き新定数+切替。既存テストへの影響を評価)。日本語=Family X の可変 JA segment に J3 を渡す最小経路(例: `generate_a2_japanese_with_reading_safety` に `style_prefix_override: str | None = None` を追加し既定 None で従来の `JAPANESE_STYLE_PREFIX` を維持=他 Family 無影響、Family X runner の JA 呼び出し箇所のみ J3 定数を渡す。J3 が長文 PREFIX を **置換**するのか **併記**するのかは Trial-02 の実装(`er044`)がどうしたかを確認し、Trial と同一にする)。定数名案・挿入位置・影響ファイル一覧。**固定 phrase・Key Phrase(KP EN/JA/英語解説)は対象外**であることを明記(KP 英語解説の Style は別 Trial 中)。
4. **runtime evidence 案**: 既存 audit(`tts_generation_results.json` の `style_prefix_used`、model/voice metadata、`runtime_evidence.json`)で J3/E2 の実文字列・model・voice が記録されることの確認、無ければ最小追加案。
5. **Regression 計画(Phase B)**: Hormuz の Standard JA 可変 segment(preview/comment_1〜4)+Advanced EN(topic_intro/full_story_part1〜3+heading/in_one_line)を専用 out-dir で再生成(TTS のみ、`--stage all` 禁止、対象 segment 明示)、ASR/drift、費用概算(Trial-02 実測 ¥20.71/24 segment を根拠)、既存テスト(er033/er019/er038/er044 系)への影響と更新方針、固定 Master の reuse が変わらないこと(manifest 不変)の確認方法。
6. **SSOT 文案**(Phase B で反映): CURRENT_SPEC(Role Style 節: J3/E2 逐語、適用範囲、固定 phrase 除外)、DECISION_LOG、OPEN-229(JA Role Style 機構=本配線で最小導入)、OPEN-201 追記、REPORT_LEDGER 行案。
7. **リスク・Opus L2 論点候補**: 共有関数変更の後方互換、Family A への無影響の証明方法、J3 と長文 PREFIX の関係、E2 と Standard slower 指示の重畳、Master Store の style version 混線、テスト更新の正当性。

## 事前指定Read一覧

- `er044_tts_variable_spoken_role_style_trial_02.py`: Grep `J3|E2|JAPANESE_STYLE_PREFIX|style_prefix|def generate_ja|def generate_en`
- `er033_tts_flash_lite_family_x_styles_01.py`: 全文(短い想定)
- `er019_family_x_audio_production_runner_01.py`: Grep `_role_style|A2_SLOWER|generate_a2_japanese|comment_|preview|JAPANESE_STYLE`
- `er003_b1_p9a_audio.py`: Grep `JAPANESE_STYLE_PREFIX|def generate_a2_japanese_with_reading_safety`
- `er006_master_audio_store_01.py`: Grep `EQUALITY_FIELDS|style_instruction`
- `docs/pm/design_tts_variable_spoken_role_style_trial_02.md`: §2/§4

## 事前指定Grep一覧+追記位置・更新位置の手順

- Grep対象: 上記+`CURRENT_SPEC.md`/`OPEN_ITEMS.md`(Grep のみ)。
- 追記位置: 設計書(新規)。更新位置: なし。

## 実行コマンド全文

- `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-28_TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01_01.md --json-out docs/pm/delegation_log/2026-09-28_TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01_01.md_check.json`
- `git status --porcelain -- "er0*.py" CURRENT_SPEC.md`(本タスク由来の差分なし)

## SSOT追記文

設計書 §6 に文案のみ。

## Git

- add対象(path指定のみ): 設計書、delegation_log+`_check.json`。SSOT編集権なし。
- メッセージ: `TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01: Phase A 設計書(J3/E2 の逐語・既存経路・最小diff案・Regression計画・Opus L2論点)`、trailer `Management-ID: TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01`。`git push origin main`。

## 報告(RESULT_PACKET_VW1 + handback、目安30行)

J3/E2 逐語/Existing Spec Check 結果(共有状況・固定 phrase 非影響・path 表)/最小 diff 案/runtime evidence 案/Regression 計画と費用/リスク・L2 論点/commit hash・raw URL/STOP 候補。
