## 管理ID

FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(Phase C / E2E=Hormuz・Meta × Standard・Advanced を Production 正式経路のみで完成 podcast+試聴ページまで生成、委任 _09)。一時ファイル `docs/pm/ACTIVE_TASK_RFE.md` / `docs/pm/RESULT_PACKET_RFE.md`(commitしない)。並行 Agent なし(`git pull --ff-only origin main`、HEAD は `42c8093a` 以降)。SSOT 4点+REPORT_LEDGER は編集権なし(文案のみ。Closeout の SSOT 反映は Fable Gate 3 判定後に別委任)。**削除・移動・`rm`・`git clean`・`git stash`・rebase/reset/amend/force push 禁止**。未追跡ファイルは他Agent/ユーザーの作業物として扱う。push 競合時は `git merge origin/main` のみ。**APIキーは環境変数のみ、key 本文を表示・log・commit・報告に書かない**。

## 事前確認(着手前、¥0)

- `git stash list` を実行し結果を逐語記録。**空でない場合は pop/drop/apply せず**、その事実を REPORT と handback に記録して続行(stash は前委任 W5 が使用した可能性があり、内容の扱いはユーザー判断)。
- `git status --short | head -50` で未追跡・未 commit 差分を記録(触らない)。
- E2E-PLAN(REPORT `FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_REPORT.md` §W5「E2E-PLAN」行 653〜692)と Gate(`docs/pm/ACTIVE_TASK.md` の Gate 13 項目・STOP 条件・Closeout 10 項目)を Read。

## 性質/到達上限Status/禁止事項

- 性質: 承認済み仕様を配線済みの **Production 正式経路のみ** で実行する E2E。Trial ではない。到達上限 Status: 各記事×レベルの Gate 結果を evidence 付きで報告(`PRODUCTION_WIRED` 判定は Fable Gate 3、`APPROVED_FOR_PRODUCTION` はユーザーのみ)。
- **費用 Guardrail**: 全体上限 **¥300**(Phase A 概算 A ≈ ¥150〜250)。記事×レベルごとに E2E-PLAN の段階別 `--budget-jpy`(scaffold ¥50 / tts ¥150 / assemble ¥10)を厳守。writer 段(LLM)は記事ごとに上限 ¥30 を目安に記録。**累計が ¥300 に達したら以降の段階を発火せず STOP** し、そこまでの結果を報告。実行前に「対象 segment 数・想定 call 数・retry 上限・想定費用・Guardrail」を記事×レベルごとに RESULT_PACKET に記録してから発火(E2E-PLAN の数値を転記)。
- **実行規律**: `--stage all` 禁止(段階個別)。`TTS_EXECUTION_MODE=STANDARD`(同期実行)を明示し、実行コマンド全文を逐語記録。`--tts-backend speech_metadata_flash_lite` 必須(`--allow-legacy-backend` 使用禁止)。`er012_e_family_entertainment_two_level_runner_01.py` は `--stage ledger` / `--stage writer` のみ。**1 記事ずつ完結**(Hormuz を Standard/Advanced とも完成 → Gate → 次に Meta)。Production Master Store は reuse のみ(登録・削除・上書き禁止)。既存の良好な音声(固定 shell Master、KP Master)は reuse し再生成しない。
- **STOP 条件**(該当時は以降を発火せず報告): 承認済み仕様との矛盾/新しい Product 判断が必要/未承認 Prompt 変更が必要/Standard・Advanced の意図しない非対称/共有 TTS 層の意味変更が必要/予算超過/KP explanation の text-gate が OK 以外の rank が retry 後も残る(Opus 項目 4)/構造 Gate NG が retry 後も残る/ASR cascade 3 attempt 到達で STOPPED segment が残る(Local Rewrite は既存 Production 方針の範囲で 1 回まで可、それでも残れば STOP)。
- 禁止: コード・Prompt・style の変更(E2E 中にバグを見つけたら STOP して報告。修正は別委任)、Trial 出力の流用による「見せかけの完成」、`file:///`・raw URL を試聴リンクにすること(試聴リンクは `https://shimomura055.github.io/eigo-radio/...` のみ)、ユーザー向け表記に A2/B1/B1B を使うこと(Standard/Advanced)。

## 固定ブロック

E-1/D-1/G-1/F-1 標準。T-0: 本委任文を `docs/pm/delegation_log/2026-09-29_FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_09.md` へ逐語保存し `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-29_FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_09.md --json-out docs/pm/delegation_log/2026-09-29_FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_09.md_check.json` を実行し結果1行記録。T-2: `TTS_EXECUTION_MODE=STANDARD`(同期実行)、コマンド逐語記録。T-3: 上記 Guardrail(全体 ¥300、段階別 budget-jpy)。

## 手順(記事ごと: Hormuz → Meta)

1. **JA 入力**: `er019_output/family_x_refresh_e2e_01/<slug>/input/article_ja.md`(W1 で機械検証済みの er039 AN3-T0 セル、provenance.json あり)。sha256 が W1 記録と一致することを確認(不一致なら STOP)。
2. **Writer 段**(LLM): Production 正式経路(`er019_family_x_entertainment_production_runner_01.py` または `er012_e ... --stage ledger` → `--stage writer`、E2E-PLAN の記載に従う。JA 記事は再生成せず入力として与える。JA Writer O を再実行しない)。出力: 忠実英訳(Advanced)、Standard A2、3 分割、In One Line、Comment1〜4、KP 抽出、Deviation Check(MAJOR → must-fix retry 1 回)。構造 Gate(title/In One Line/heading 混入)の status を記録。
3. **Audio 段**: `--stage scaffold` → `--stage tts` → `--stage assemble` → `--stage player`(E2E-PLAN のコマンド逐語、`--level both`)。各段の実行コマンド・所要時間・費用(`raw_usage_log`/budget 実測)を記録。
4. **Gate**(記事×レベルごと、evidence 付き表): `docs/pm/ACTIVE_TASK.md` の Gate 13 項目 + Opus 9 項目(REPORT 行 682〜692)。特に: `entry_point.json.tts_backend`、可変 segment 全件+KP 中間全 rank の `style_prefix` 実文字列(J3/E2/Variant B)、固定 shell 10 件 `reused=True`・`master_audio_id` が W2 表と一致・TTS call 0、Advanced 全 rank の `phrase_repeat` = english 同一 path/sha256、`explanation_status_from_text_gate=="OK"` 全 rank、`style_version` 一致、parts.json の title 非空・heading 混入なし・段落数 ≥3・in_one_line 非空、Audio Validation Gate PASS、ASR 結果、完成 mp3 の存在・長さ。
5. **試聴ページ**: `user_test/family_x_refresh_e2e_01/index.html`(記事×レベル 4 episode、完成 mp3 プレーヤー+segment 別プレーヤー、各 segment の Style Prompt 全文実表示(省略・`(existing …)` プレースホルダ禁止)、model/voice、reuse 元 master_audio_id、learning level は Standard/Advanced 表記)。commit・push 後、**Pages 公開確認 7 項目**(HTTP 200/実ブラウザ headless Edge or Chrome の DOM dump/`(existing 6-role value, unchanged)` 0 件/Style Prompt 全文実表示/audio player 存在/mp3 200+decode 再生可能/表示 Style と metadata の Style 一致)を実施し evidence を記録。Pages 反映待ちは最大 10 分、curl で確認。
6. **費用**: A(本 E2E の一回限り費用、記事×レベル×段階の実測表、累計)/B(Production 量産時の継続コスト差: 記事あたりの LLM call・TTS segment 数の増減。KP 解説 +1 LLM call +5 TTS、Phrase 再掲 0、Heading Readout −2 segment、Master reuse 0、Comment 4 本化の差分)。実測 call 数で裏付け。
7. **REPORT**: `FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_REPORT.md` へ §E2E 追記(事前確認結果、記事×レベルごとの実行ログ要約、Gate 表、Pages 7 項目、費用 A/B、STOP 有無、Closeout 10 項目の充足状況表[SSOT 反映は未実施と明記])。設計書 §9-E2E 追記。RESULT_PACKET へ SSOT 文案(OPEN-228 CLOSED/SUPERSEDED、OPEN-230、AN3-T0・J3/E2・Champion・KP 構造・新構造の `PRODUCTION_WIRED` 同期案=Fable Gate 3 後に反映)。

## 実行コマンド全文(逐語記録すること。<slug>=hormuz / meta、<run>=run_01)

- 事前: `git stash list`、`git status --short`
- E2E-PLAN 行 657〜660 のコマンド(`--slug <slug> --run <run> --level both`、`TTS_EXECUTION_MODE=STANDARD` を環境変数で明示)
- writer: E2E-PLAN の記載に従う(`--stage ledger`/`--stage writer`)
- Pages: `curl -sI https://shimomura055.github.io/eigo-radio/user_test/family_x_refresh_e2e_01/index.html`、headless ブラウザ DOM dump(`msedge --headless --dump-dom <url>` 等)、mp3 `curl -sI`+`ffprobe`/decode

## Git

- add 対象(path 指定のみ): `er019_output/family_x_refresh_e2e_01/**`(audit json・parts・player・完成 mp3。wav は既存方針に従う、大容量なら json/mp3 のみ)、`user_test/family_x_refresh_e2e_01/**`、REPORT、設計書、delegation_log+`_check.json`、telemetry の変更(`er006_output/master_audio_store_01/reuse_telemetry.jsonl` 等、本 E2E 由来の追記のみ)。他 Agent 差分・未追跡ファイルは add しない。
- 記事ごとに commit(Hormuz 完了時、Meta 完了時)+試聴ページ commit。メッセージ例 `FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01 (E2E): Hormuz Standard/Advanced をProduction正式経路で完成(Gate evidence付き)`、trailer `Management-ID: FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01`。push。

## 報告(RESULT_PACKET_RFE + handback、目安45行)

事前確認(stash/status)/記事×レベルごとの Gate 表(13+9、PASS/FAIL/evidence)/STOPPED segment・retry・Local Rewrite の有無/Pages 7 項目/試聴 URL(GitHub Pages)/費用 A 実測(段階別・累計)・B 差分/Closeout 10 項目の充足状況/commit hash・raw URL/STOP 有無と理由。
