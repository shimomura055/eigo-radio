## 管理ID

FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(Phase B / W2=固定フレーズ Champion の Production Master Store 正式登録、委任 _02)。一時ファイル `docs/pm/ACTIVE_TASK_RF2.md` / `docs/pm/RESULT_PACKET_RF2.md`(commitしない)。並行: 別Sonnet 1件(W3: `er019_family_x_audio_production_runner_01.py`/`er003_b1_p9a_audio.py`/`er003_v1_sing01_voice01_generate.py`/`er003_v1_sing01_news_tail_fix.py`/`er003_v1_sing01_point_headings_aoede.py` を編集中)→ これらに触れない。SSOT 4点+REPORT_LEDGER は編集権なし(文案のみ)。本タスクの所有: `er006_audio_cost_pilot_02_shared_narration.py`(shell style 解決・version)、`er006_master_audio_store_01.py`(必要最小限)、新規登録スクリプト `er048_fixed_shell_champion_master_registration_01.py`(+`_test_01.py`)、`er006_output/master_audio_store_01/`(**Production Master Store: 追加登録のみ、既存 entry の削除・上書き禁止**)、`er048_output/`、REPORT `FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_REPORT.md` の §W2(新規作成、他 W は後で追記)、設計書 §9-W2 追記、delegation_log。**削除・移動・`rm`・`git clean`・stash/rebase/reset/amend/force push 禁止**。未追跡ファイルは他Agent/ユーザーの作業物として扱う。push競合時は `git merge origin/main` のみ。APIキー本文表示禁止。

## 性質/到達上限Status/禁止事項

- 性質: ユーザー正式決定(固定フレーズ 10 phrase の Champion、`APPROVED_FOR_PRODUCTION`)の Production Master Store への登録と、Standard/Advanced 双方の正式経路がその Master を reuse する配線。到達上限 Status: `APPROVED_FOR_PRODUCTION`(登録・配線完了、Opus L2+Gate 判定待ち)。
- **Champion(逐語、再 Trial 禁止)**: welcome=A(現行 Production Master 継続=新規登録不要、reuse 継続)/preview_intro=C/key_phrases_intro=C/full_story_intro=C/num_one=C/num_two=B/num_three=B take1(`er047` RETRIAL-01)/num_four=C/num_five=B take1(`er047`)/point_explanation=B。B/C は `er043` TRIAL-02 の候補。model=gemini-3.8-flash-lite-tts、voice=Charon(不変)。Three/Five の take1 は ASR 合格素材。
- 費用: **上限¥5**。原則 ¥0(既存 Trial Store の wav・ASR evidence を Production Store へ登録)。Store の登録 API が「新規 ASR 検証」を必須とする場合のみ、Champion 音声に対する ASR 再検証(TTS なし)を許容。TTS 生成は禁止(暴走疑い時は STOP)。費用は **A(一回限り)** として記録。
- **実行安全**: `--stage all` 禁止。Production Store への書込は登録スクリプト経由のみ(manifest の既存 entry を書き換えない、append/新 key のみ)。作業前後の manifest を sha256 と entry 数で記録し、差分が「追加 entry のみ」であることを証明。
- 禁止: model/voice/style 文言の変更、新しい style の創作、Trial 出力の canonical text と Production canonical text の不一致を黙って通すこと(不一致なら STOP)、Family A/B/C 側 shell 経路の挙動変更(Family X 以外が同じ shell 関数を使う場合は影響を評価し、共通 Master として全 Family が新 Champion を reuse するのが設計意図=ユーザー指示「共通 Master」。Family Z も同じ Store を使う)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)

E-1/D-1/G-1/F-1 標準(設計書 `docs/pm/design_family_x_refresh_e2e_production_wiring_01.md` §3(c) は全文 Read 可)。
T-0: 本委任文を `docs/pm/delegation_log/2026-09-29_FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_02.md` へ逐語保存し、`.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-29_FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_02.md --json-out docs/pm/delegation_log/2026-09-29_FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_02.md_check.json` を実行し結果1行記録。
T-2: TTS なし(ASR 再検証が必要な場合のみ `TTS_EXECUTION_MODE=STANDARD` 明示、`--budget-jpy 5`)。T-3: 上記「性質」欄の定型文に従う。

## 設計要点(設計書 §3(c) を根拠に実装。逸脱する場合は理由記録)

1. **Champion 素材の特定**: `er043_output/tts_fixed_shell_master_champion_trial_02/`(candidate B/C の wav・`champion_trial_results.json` の style_prefix_used/model/voice/asr 結果)、`er047_output/tts_fixed_shell_number_three_five_retrial_01/`(B take1 の wav・ASR 結果)。各 phrase の canonical text が Production の shared narration 定義(`er006_audio_cost_pilot_02_shared_narration.py` の固定文言)と **逐語一致**することを確認(不一致なら STOP)。sha256 を記録。
2. **Store key の再構築**: Trial 側 key(`level="retrial01_take{N}"` 等)は使わず、Production の `EQUALITY_FIELDS`(canonical_text/voice/tts_model_id/style_instruction_id/version/language/level=None 等)で key を構築。**Champion は phrase ごとに style 文言が異なる**(C 系統の "natural, clear, conversational"、full_story_intro の pace 付き、num 系の group3 B/C、point_explanation の JA B)ため、shell 層に **phrase 別 Champion style map**(例 `SHELL_CHAMPION_STYLE_BY_PHRASE` と新 version `SHELL_..._STYLE_INSTRUCTION_VERSION = "v3_champion_01"`)を導入し、runtime の key 計算が登録 key と一致するようにする(Flash-Lite -02 の BL-1 教訓: version bump なしでは旧 Master が cache hit し続ける)。welcome は現行 Master のまま=welcome の style/version は現行値を維持し、新 version は welcome 以外に適用(または welcome も同 version で現行 wav を再登録。いずれか、根拠を記録)。
3. **登録**: 登録スクリプトで Trial wav を Production Store の所定パスへコピー(read-only)し、manifest へ新 entry を追加(asr_verified=True、evidence=Trial の ASR 結果+source path+sha256+由来 commit `7f01bad1`/`fa37cd85`)。Store API に検証必須条件があれば ASR 再検証のみ実施(¥5 内)。
4. **配線確認(¥0)**: Family X runner の shell 生成経路が **API を呼ばず** 新 Master を reuse することを、Store lookup のみを行うドライラン/単体テスト(モックで TTS 呼び出しが 0 回であることを assert)で確認。Standard/Advanced 双方(`level=None` 共有)。Family Z 等、同じ shell 関数を使う他 Family があれば同様に reuse されることを記録。
5. **テスト** `er048_..._test_01.py`: Champion 10 件の key が manifest に存在/style map の文言が er043/er047 の `style_prefix_used` と逐語一致/model・voice 不変/旧 version の Master が新 version の lookup で hit しない/welcome が現行 Master のまま/TTS 呼び出し 0 回で reuse。既存 `er006*_test_*`・`er019*_test_*`・`er033*_test_*` の regression PASS(更新が必要な既存テストは理由コメント付き)。
6. **REPORT §W2**: 対応表(phrase→candidate→source wav sha256→style 全文→model/voice→新 key/version→manifest entry)、manifest 前後(sha256・entry 数・追加 entry のみの diff)、テスト結果、費用(A)、Opus L2 論点(shell 層の version bump の影響範囲、他 Family への波及)。

## 事前指定Read一覧

- `docs/pm/design_family_x_refresh_e2e_production_wiring_01.md`: §3(c)、§5
- `er006_audio_cost_pilot_02_shared_narration.py`: Grep `STYLE_INSTRUCTION_VERSION|_resolve_shell|_make_english_key|_make_japanese_key|FALLBACK|canonical`
- `er006_master_audio_store_01.py`: Grep `EQUALITY_FIELDS|def register|verified|manifest|def lookup|def get_or_generate`
- `er043_output/tts_fixed_shell_master_champion_trial_02/champion_trial_results.json`、`er047_output/.../*.json`(Grep `style_prefix_used|wav|asr|model|voice|take1`)
- `er006_output/master_audio_store_01/manifest.json`: Grep `canonical_text|style_instruction`(現行 entry の構造)

## 事前指定Grep一覧+追記位置・更新位置の手順

- Grep対象: 上記。更新位置: `er006_audio_cost_pilot_02_shared_narration.py`(style map/version)、`er006_master_audio_store_01.py`(必要時のみ最小)、Production manifest(追加のみ)、REPORT §W2(新規ファイル作成)、設計書 §9-W2。

## 実行コマンド全文

- `.venv\Scripts\python.exe er048_fixed_shell_champion_master_registration_01.py --dry-run`(登録計画の表示、書込なし)→ `--apply`(逐語記録)
- `.venv\Scripts\python.exe -m unittest er048_fixed_shell_champion_master_registration_01_test_01 -v`
- `.venv\Scripts\python.exe run_project_regression.py --pattern "er006*_test_*.py"`(同様に er019/er033/er048)
- manifest 前後: `certutil -hashfile er006_output/master_audio_store_01/manifest.json SHA256`+entry 数(Python)
- `git diff --stat HEAD -- "er0*.py"`(本タスク由来=er006 2 ファイル+er048)

## SSOT追記文

RESULT_PACKET へ文案のみ(CURRENT_SPEC「固定フレーズ Champion」小節の更新案[登録完了・version・reuse 経路]、DECISION_LOG、OPEN-222 更新案[Champion 確定・登録、数字語の ASR 限界は Master 化で運用上解消]、REPORT_LEDGER)。

## Git

- add対象(path指定のみ、`git add -A` 禁止): `er006_audio_cost_pilot_02_shared_narration.py`、`er006_master_audio_store_01.py`(変更時)、`er048_*`、`er006_output/master_audio_store_01/manifest.json`+新 Master の wav/json(Store の既存 commit 方針に従う。wav が非 commit 方針なら json のみ)、REPORT、設計書、delegation_log+`_check.json`。他Agent差分(W3 の 5 ファイル、er045/046/047 等)は add しない。
- メッセージ: `FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01 (W2): 固定フレーズChampion 9件をProduction Master Storeへ正式登録(phrase別Champion style map+version bump、welcomeは現行Master継続、TTS 0回でreuse)`、trailer `Management-ID: FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01`。`git push origin main`。

## 報告(RESULT_PACKET_RF2 + handback、目安30行)

対応表の要約/manifest 前後の証拠/reuse ドライラン結果(TTS 0 回)/テスト・regression 結果/費用(A)/Opus L2 論点/commit hash・raw URL/STOP 有無(canonical 不一致等)。
