## 管理ID

FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(Phase C / E2E Meta run_03=Meta を Production 正式経路のみで完成 podcast+試聴ページまで、委任 _13)。前委任 _12(Hormuz run_03 は Standard 段で STOP、ユーザー指示により **Hormuz は deferred / non-blocking として保留**、evidence 保持)を引き継ぐ。一時ファイル `docs/pm/ACTIVE_TASK_RFE4.md` / `docs/pm/RESULT_PACKET_RFE4.md`(commitしない)。並行 Agent: 後続で GPT-6 Trial 準備の read-only 整理(出力先 `docs/pm/gpt6_trial_preparation_01.md`)が起動される可能性あり → 同ファイルに触れない。SSOT 4 点+REPORT_LEDGER は編集権なし(文案のみ)。**削除・移動・`rm`・`git clean`・`git stash`・rebase/reset/amend/force push 禁止**。未追跡ファイルは他タスク由来として触らない。push 競合時は `git merge origin/main` のみ。**APIキーは環境変数のみ、key 本文を表示・log・commit・報告に書かない**。

## 性質/到達上限Status/禁止事項

- 性質: 目的は「**Family X の Production 経路そのものが完成しているかを、Hormuz 以外の記事(Meta)で確認する**」こと。Production 正式経路のみ、Trial ではない。到達上限: Meta × Standard/Advanced の Gate 結果を evidence 付きで報告(`PRODUCTION_WIRED` 判定は Fable Gate 3)。
- **ユーザー指示(逐語厳守)**: 「Hormuz は一旦保留。Standard 側 must-fix 追加ルールは今回は実装しない/JA 再生成回数も増やさない/Checker Prompt / severity / origin 判定は変更しない/Hormuz の run_03 evidence は保持」「Meta でも Checker 由来の新しい細かな境界問題が出た場合、延々と暫定仕様を追加しないでください」「既承認の案B は有効のままで構いません」。
- **STOP 基準(逐語)**: 「既存承認済み retry 範囲で解消しない/新しい Checker 仕様判断が必要/Checker の根本問題に踏み込む必要がある」場合は STOP して報告。**Checker の追加対処を勝手に設計・実装しない**。加えて: 承認済み仕様との矛盾/未承認 Prompt 変更/Standard・Advanced の意図しない非対称/共有 TTS 層の意味変更/予算超過/構造 Gate NG が retry 後も残る/KP 解説 text-gate NG が残る/ASR 3 attempt 到達 STOPPED が残る(Local Rewrite は既存方針 1 回まで)。
- **費用 Guardrail**: 全体上限 ¥300(本管理ID 累計 ≈ ¥16.40 を含む)。Meta: JA Writer O(案B 込み)¥40、EN writer ¥30、scaffold ¥50 / tts ¥150 / assemble ¥10。発火前に「対象 segment 数・想定 call 数・retry 上限・想定費用・Guardrail」を記録。
- **実行規律**: `--stage all` 禁止、`TTS_EXECUTION_MODE=STANDARD` 明示、コマンド全文逐語記録、`--tts-backend speech_metadata_flash_lite` 必須(`--allow-legacy-backend` 禁止)、`er012_e` は `--stage ledger`/`--stage writer` のみ、Master Store は reuse のみ、Trial 出力流用禁止、コード・Prompt・style 変更禁止、試聴リンクは GitHub Pages のみ、ユーザー向け表記 Standard/Advanced。Hormuz の artifact(run_01〜03)は一切触らない。

## 固定ブロック

E-1/D-1/G-1/F-1 標準。T-0: 本委任文を `docs/pm/delegation_log/2026-09-29_FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_13.md` へ逐語保存し `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-29_FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_13.md --json-out docs/pm/delegation_log/2026-09-29_FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_13.md_check.json` を実行し結果 1 行記録。T-2: `TTS_EXECUTION_MODE=STANDARD`、コマンド逐語記録。T-3: 上記 Guardrail。

## 手順(Meta のみ。REPORT §W6 run_03 手順・§W5 E2E-PLAN・§E2E run_03 の Hormuz 実行ログを踏襲)

0. 事前確認(¥0): `git pull --ff-only`、`git stash list`、`git status --short | head`、Production 側 `grep -n "再び増やさない" er0*.py` 0 件。Meta の `run_03/`(前委任で research_ledger・storyline_b3 複製済み・sha256 確認済み、`storyline_b3/fact_selection_evidence.json` 存在確認済み)を使用、案B armed を確認。
1. JA 生成(Production JA 経路、`--budget-jpy 40`): `verbatim_shas`・記号 0・段落数 ≥3 を記録。
2. Writer 段(`er012_e --stage ledger`(reuse)→ `--stage writer --budget-jpy 30`): Advanced → Deviation Check(ja_source MAJOR なら案B 自動発動 1 回、translation MAJOR は既存 must-fix 1 回)→ Standard → 構造 Gate → 3 分割 → In One Line → Comment1〜4 → KP 抽出。`ja_recheck_used` 等を記録。
3. Audio 段: `--stage scaffold` → `--stage tts` → `--stage assemble` → `--stage player`(`--run run_03 --level both`)。
4. **Gate**(Meta × Standard/Advanced、evidence 付き表): `docs/pm/ACTIVE_TASK.md` Gate 13 項目+Opus 9 項目(REPORT §W5)+**ユーザー指定 Gate 3 項目**: Production wiring(`entry_point.json` の runner/backend/stage 履歴、Trial ファイル未使用)/runtime evidence(全 segment の `tts_model_id`・`voice`・`style_prefix` 実文字列、reuse 経路は `master_audio_key`、`style_version` 一致)/Standard・Advanced 双方完成/J3・E2(japanese_title/preview/comment/full_story/in_one_line/KP 日本語意味)/Champion(固定 shell 10 件 `reused=True`・`master_audio_id` W2 表一致・TTS call 0)/新記事構造(body1/2/3 段落境界、Comment1〜4 組立順、Heading Readout 不在、In One Line)/KP 構造(Advanced: Phrase → 英語解説(Variant B、Aoede)→ 同一 Phrase[phrase_repeat = english の同一 path/sha256]、Standard: Phrase → 日本語意味(J3)→ 同一 Phrase)/AN3-T0(JA Prompt sha256、reminder 不在)/retry・fallback・regeneration(発生経路と回数、案B 発動有無)/pronunciation resolver 適用/Audio Validation Gate PASS(ASSET_HASH_MISMATCH 0)/player(2 episode 行、Style 全文)/Dangling Reference Check(`HEADING_READOUT`・`NG_ACCEPTED_AFTER_RETRY`・旧 split・旧 KP 構造の参照が Production 経路と audit に無い)。
5. **試聴ページ** `user_test/family_x_refresh_e2e_01/index.html`(Meta × Standard/Advanced の 2 episode を完成分として掲載。Hormuz は「Advanced writer 段まで完成・Standard 段 STOP(deferred、OPEN-233)」と明記し音声なし。完成 mp3 プレーヤー+segment 別プレーヤー、各 segment の Style Prompt **全文実表示**、model/voice、reuse 元 master_audio_id、案B 発動有無、Standard/Advanced 表記)→ commit・push → **Pages 公開確認 7 項目**(HTTP 200/headless Edge or Chrome DOM dump/`(existing 6-role value, unchanged)` 0 件/Style Prompt 全文実表示/audio player 存在/mp3 200+decode/表示 Style と metadata 一致)。Pages 反映待ち最大 10 分。
6. 費用: A 実測(Meta 段階別+累計 ≈ ¥16.40 合算)/B 差分(記事あたり LLM call・TTS segment の増減を実測 call 数で裏付け: KP 解説 +1 LLM +5 TTS、Phrase 再掲 0、Heading Readout −2、Master reuse 0、Comment 4 本化、案B 発動時のみ +¥5〜6)。
7. REPORT §E2E に「Meta run_03」追記(事前確認、実行ログ要約、Gate 表、Pages 7 項目、費用 A/B、Closeout 10 項目充足表[SSOT 未反映と明記])、設計書 §9-E2E。RESULT_PACKET へ SSOT 文案(Hormuz deferred 記録、OPEN-233 への Hormuz run_01〜03 evidence 追記、OPEN-228 CLOSED/SUPERSEDED、OPEN-230、各仕様 PRODUCTION_WIRED 同期案=Fable Gate 3 後。**Hormuz 未完が Gate 3 条件のどれに抵触するかを事実として列挙**=条件緩和はしない)。

## 実行コマンド全文(逐語記録。<slug>=meta、run_03)

- 事前: `git stash list`、`git status --short | head -20`、`grep -n "再び増やさない" er0*.py`
- JA/writer/audio: REPORT §W6 run_03 手順と §W5 E2E-PLAN 行 657〜660(`--slug meta --run run_03`、`TTS_EXECUTION_MODE=STANDARD`、上記 budget)
- Pages: `curl -sI https://shimomura055.github.io/eigo-radio/user_test/family_x_refresh_e2e_01/index.html`、headless DOM dump、mp3 `curl -sI`+decode

## Git

- add 対象(path 指定のみ): `er019_output/family_x_refresh_e2e_01/meta/run_03/**`(audit json・parts・player・完成 mp3、wav は既存方針)、`user_test/family_x_refresh_e2e_01/**`、REPORT、設計書、delegation_log+`_check.json`、本 E2E 由来 telemetry。commit: Meta 完成時+試聴ページ。メッセージ例 `FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01 (E2E Meta run_03): Meta Standard/Advanced をProduction正式経路で完成(Gate evidence付き)`、trailer `Management-ID: FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01`。push。

## 報告(RESULT_PACKET_RFE4 + handback、目安50行)

事前確認/案B 発動有無/Meta × Standard/Advanced の Gate 表(13+9+ユーザー指定、PASS/FAIL/evidence)/STOPPED・retry・Local Rewrite/Pages 7 項目/試聴 URL(GitHub Pages)/費用 A 実測(段階別・累計)・B 差分/Closeout 10 項目充足/Hormuz 未完が抵触する Gate 3 条件の列挙/commit hash・raw URL/STOP 有無と理由。
