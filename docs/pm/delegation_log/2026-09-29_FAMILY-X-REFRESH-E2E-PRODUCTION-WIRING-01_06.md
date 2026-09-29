## 管理ID

FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(Phase B / W4=Key Phrase 音声構造(両レベル共通骨格 Phrase → 中間 → Phrase、Advanced 中間=英語解説 Variant B)の Production 正式経路への配線、委任 _06)。一時ファイル `docs/pm/ACTIVE_TASK_RF4.md` / `docs/pm/RESULT_PACKET_RF4.md`(commitしない)。並行 Agent なし(W1 `8d906408`・W2 `2ecb0c64`・W3 `3fc45986`・SSOT `b51dc910` は完了・push 済み。`git pull --ff-only origin main` で最新化してから着手)。SSOT 4点+REPORT_LEDGER は編集権なし(文案のみ)。**削除・移動・`rm`・`git clean`・stash/rebase/reset/amend/force push 禁止**。未追跡ファイルは他Agent/ユーザーの作業物として扱う。push競合時は `git merge origin/main` のみ。APIキー本文表示禁止。

## 性質/到達上限Status/禁止事項

- 性質: ユーザー正式決定(2026-09-29、`APPROVED_FOR_PRODUCTION`、CURRENT_SPEC「Key Phrase 音声構造(Standard/Advanced 共通骨格)」小節・DECISION_LOG 記録済み)の Production 配線。到達上限 Status: `APPROVED_FOR_PRODUCTION`(配線完了、Opus L2+E2E Gate 判定待ち)。**Trial ではない**。
- 決定内容(逐語): 「Advanced: 英語 Phrase → 英語解説 → 英語 Phrase/Standard: 英語 Phrase → 日本語意味 → 英語 Phrase。両レベルで『Phraseを最初と最後にもう一度聞く』という同じ骨格にし、中間だけをレベル別に変える」。付帯条件(逐語): 「Advancedの英語解説音声は、採用済み Variant B」「最後の英語Phraseは、最初と同じcanonical Phraseを使用」「追加の別文言・別候補を作らない」「Standard側の既存構造を壊さず、対応関係を明確に保つ」「retry / fallback / cache / Master Storeでも、最初と最後のPhraseが同一canonical text・同一正式音源/生成条件になること」「Advancedで Phrase がもう1回再生される分について、追加生成 call が発生するのか、既存 Phrase 音源の reuse で済むのかを明示。reuse 可能なら量産 API コスト増として数えない」。
- Standard 側: CURRENT_SPEC「Key Phrases セクション構成」は既に「番号 → 英語 → 日本語訳 → 英語」(末尾 Phrase あり)。**まず現行 Production コードが実際にそうなっているか確認**し、そうなら Standard は無変更。末尾 Phrase が実装されていない/別 wav を再生成している場合は、先頭と同一 wav を参照する形へ最小修正(新規生成なし)し、その事実を REPORT に明記。
- Advanced 側: 現行の Advanced KP 組立(Phrase EN → 日本語意味 か、Phrase EN のみか、を確認)を、Phrase EN → 英語解説 → Phrase EN(先頭と同一 wav)へ変更。英語解説の **text 生成**は `KP-ADVANCED-EXPLANATION-TRIAL-02`(er041/er042)で `APPROVED_FOR_PRODUCTION` となった text 仕様(Prompt・語数・平易さ・禁止事項)を逐語転記(sha256 記録)し、Production KP 経路(KP 抽出後、Advanced 専用段)へ組み込む。**音声**は Variant B(`clear, precise, at a measured pace, without dragging`、`TRIAL-04` er046、voice Aoede、Flash-Lite)を `er033_tts_flash_lite_family_x_styles_01.py` の `KEY_PHRASE_EXPLANATION_EN` 定数(存在しなければ新設、文言は er046 の Variant B 逐語)経由で適用。Advanced に日本語意味 segment は入れない(決定どおり)。
- 費用: **上限¥0**(コード・テストのみ、LLM/TTS は mock。E2E 実測は次 Phase)。
- 禁止: 解説 Prompt・Variant B 文言の改変、別候補の追加、Standard 経路の構造変更、shell(固定 phrase)/Master Champion(W2)/可変 Role Style・cache version guard(W3)/新記事構造(W1)の変更、共有 TTS 層の意味変更(必要なら STOP)、`_generate_or_reuse_kp` の reuse 判定変更(拡張は可、既存挙動不変)。ユーザー向け表記は Standard/Advanced。

## 固定ブロック

E-1/D-1/G-1/F-1 標準。T-0: 本委任文を `docs/pm/delegation_log/2026-09-29_FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_06.md` へ逐語保存し `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-29_FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_06.md --json-out docs/pm/delegation_log/2026-09-29_FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_06.md_check.json` を実行し結果1行記録。T-2: TTS なし。T-3: API 支出なし。

## 実装

1. **現状確認**(REPORT に表で記録): Standard/Advanced それぞれの KP セクションの現行 segment 列(role 名・wav・生成関数・cache/Master key)、末尾 Phrase の有無と参照 wav。
2. **text**: KP 解説の Production 生成関数(例 `er019_family_x_kp_explanation_01.py` 新設、または既存 KP backend `er030_*` の Advanced 段)。入力=canonical Phrase(+文脈)、出力=解説 text+audit(prompt sha256、model、usage)。既存 Trial-02 の QA(語数・禁止語・Phrase 再掲の有無等)があれば Production validator として組み込み、NG 時は既存の技術 retry 方針(1 回)を踏襲。
3. **audio**: Advanced KP 組立を [phrase_en(rank) → explanation_en(rank) → phrase_en(rank) 再掲] に。再掲は **新 segment を生成せず、先頭と同じ wav path/同じ cache entry/同じ Master key を参照**(組立リストに同一ファイルを 2 回並べる)。`_generate_or_reuse_kp` の cache に explanation_en を追加(rank/role key)。retry / Local Rewrite / fallback / cache miss 再生成のいずれの経路でも「先頭と末尾が同一 wav」となるよう、組立段で常に同一 path を参照する実装にする(生成段で 2 回生成する設計にしない)。`tts_generation_results.json` の audit に `phrase_repeat_source="same_as_first"`(または同等)を記録。
4. **Audio Validation / player**: parts 一覧・player 行に explanation_en と再掲 Phrase を反映(再掲は同一 wav であることを表示 metadata で明示)。Standard 側の parts は不変。
5. **量産コスト(B)の明示**: Advanced 1 記事あたり追加 = LLM 解説生成 call 数(KP 件数分、例 5)+TTS explanation segment 数(例 5)。**Phrase 再掲の TTS call は 0**(reuse)であることを mock テスト(TTS 呼び出し回数 assert: Advanced KP セクションで phrase 生成は rank ごとに 1 回のみ)で証明し、REPORT に「量産 API コスト増として数えない」と記載。Standard 側の追加 call 0。
6. **テスト** `er019_family_x_kp_structure_wiring_01_test_01.py`(新規): Standard の列が [phrase_en, japanese_gloss, phrase_en(同一 wav)] で不変/Advanced の列が [phrase_en, explanation_en, phrase_en(同一 wav)]/Advanced に日本語意味 segment なし/再掲 wav が先頭と同一 path・同一 sha256/cache hit・cache miss・retry(mock で 1 回目失敗→2 回目成功)・fallback の各経路で先頭=末尾/explanation の style が Variant B 逐語・voice Aoede/解説 Prompt sha256 が er041/er042 と一致/TTS 呼び出し回数(phrase は rank ごとに 1 回)/W1〜W3 のテストが引き続き PASS。regression: `run_project_regression.py --pattern "er019*_test_*.py"`、`"er030*_test_*.py"`(該当時)、`"er033*_test_*.py"`、`"er041*_test_*.py"`/`"er042*_test_*.py"`/`"er046*_test_*.py"`(該当時)、`"er048*_test_*.py"` 全 PASS(pre-existing 失敗は根拠付きで W4 非起因を明記)。
7. **REPORT**: `FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_REPORT.md` へ §W4 追記(現状確認表、変更ファイル・行、Prompt/Style sha256、経路別の先頭=末尾証明、コスト B 明示、テスト結果、Opus L2 論点)。設計書 §9-W4 追記。

## 事前指定Read一覧

- `CURRENT_SPEC.md`: Grep `Key Phrase 音声構造|Key Phrasesセクション構成|Advanced Key Phrase 英語解説|Variant B` → 該当小節のみ
- `docs/pm/design_family_x_refresh_e2e_production_wiring_01.md`: §3(d)(KP 関連)、§9-W1〜W3
- `er019_family_x_audio_production_runner_01.py`: Grep `_generate_or_reuse_kp|phrase_en|japanese_gloss|key_phrase|kp_|rank|Aoede|KEY_PHRASE`
- `er033_tts_flash_lite_family_x_styles_01.py`: Grep `KEY_PHRASE|EXPLANATION`
- `er041_*.py`/`er042_*.py`: Grep `PROMPT|def build|word|forbid|explanation`(text 仕様の逐語元)
- `er046_*.py`: Grep `Variant B|measured pace|without dragging|voice|Aoede`
- `er030_*.py`(KP backend): Grep `def .*key_phrase|advanced|B1B|explanation`
- `er019_family_x_audio_plan_01.py`: Grep `key_phrase|kp|phrase_en|explanation`
- REPORT `KP-ADVANCED-EXPLANATION-TRIAL-02_REPORT.md` / `KP-ADVANCED-EXPLANATION-AUDIO-TRIAL-04_REPORT.md`: Grep `APPROVED|Variant B|Prompt|sha256`

## 実行コマンド全文

- `git pull --ff-only origin main`
- `.venv\Scripts\python.exe -m unittest er019_family_x_kp_structure_wiring_01_test_01 -v`
- `.venv\Scripts\python.exe run_project_regression.py --pattern "er019*_test_*.py"`(同様に er030/er033/er041/er042/er046/er048)
- `git diff --stat HEAD -- "er0*.py"`(本タスク由来のみ)

## SSOT追記文

RESULT_PACKET へ文案のみ(CURRENT_SPEC「Key Phrase 音声構造」小節の「配線済み(E2E Gate 待ち)」更新案、DECISION_LOG、REPORT_LEDGER)。

## Git

- add対象(path指定のみ、`git add -A` 禁止): 変更/新規 `er0*.py`、テスト、REPORT、設計書、delegation_log+`_check.json`。他 Agent 差分・未追跡ファイルは add しない。
- メッセージ: `FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01 (W4): Key Phrase音声構造を両レベル共通骨格(Phrase→中間→Phrase)へ配線、Advanced中間=英語解説(text仕様+Variant B/Aoede)、末尾Phraseは先頭と同一wavをreuse(追加TTS call 0)`、trailer `Management-ID: FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01`。`git push origin main`。

## 報告(RESULT_PACKET_RF4 + handback、目安30行)

現状確認表/変更箇所/Prompt・Style sha256/経路別の先頭=末尾証明/コスト B(call 数の内訳、再掲 0 call)/テスト・regression 結果/費用 ¥0/Opus L2 論点/commit hash・raw URL/STOP 有無。
