## 管理ID

FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(Phase C / E2E 再開=JA_RECHECK_REQUIRED STOP を既存仕様どおり「JA 側の再確認」で処理し、JA 記事を Production 正式 JA 経路で生成して継続、委任 _10)。前委任 _09(commit `f13660f6`)の STOP を引き継ぐ。一時ファイル `docs/pm/ACTIVE_TASK_RFE2.md` / `docs/pm/RESULT_PACKET_RFE2.md`(commitしない)。並行 Agent なし(`git pull --ff-only origin main`)。SSOT 4点+REPORT_LEDGER は編集権なし(文案のみ)。**削除・移動・`rm`・`git clean`・`git stash`・rebase/reset/amend/force push 禁止**。未追跡ファイル(444 件)は他タスク由来として触らない。push 競合時は `git merge origin/main` のみ。**APIキーは環境変数のみ、key 本文を表示・log・commit・報告に書かない**。

## Fable 判定(前提)

- 前委任の STOP は既存 Production 仕様(`er012_e_family_entertainment_two_level_runner_01.py:266-275,388-398`: Advanced deviation MAJOR のうち origin=ja_source があれば English を盲目的に再生成せず JA 側の再確認を要求)どおりの fail-closed 動作であり、**新しい Product 判断ではない**。「JA 側の再確認」の Production 正式手段は、JA 記事を Production 正式 JA 経路(`er019_family_x_entertainment_production_runner_01.py` → JA Writer O `er019_family_x_ja_writer_o_r1_r2_01.py`、AN3-T0=A3+N2 配線済み・reminder 除去済み・R1/R2・Verified Fact Ledger 照合)で生成し直すこと。前委任で入力に使った er039 Trial セルは「同一 Ledger で過去 COMPLIANT、今回 MAJOR」と再現性を欠くため **E2E 入力から外す**(Trial 成果物の流用をやめ、Production 経路のみで完結させる=本管理ID の趣旨に合致)。
- 同一入力での Deviation Check 再実行による「判定のブレ待ち」は行わない(Gate の意味を損なう)。判定の非決定性は OPEN 候補として文案化する(下記)。
- ユーザー指示: 「E2E 実行中に新しい Product 判断が発生した場合のみ STOP」。JA 生成後も Advanced 側で ja_source MAJOR が再発した場合は、本当に JA/Ledger 側の問題であり Product 判断(記事内容)に踏み込むため STOP。

## 性質/Guardrail/禁止(前委任 _09 と同じ、差分のみ記す)

- 費用 Guardrail: 全体上限 **¥300**(前委任消費 ≈ ¥1 を含む累計)。JA Writer O は記事あたり上限 ¥30(R1/R2 含む、事前に想定 call 数を記録)。段階別 `--budget-jpy`(scaffold ¥50 / tts ¥150 / assemble ¥10)は据え置き。累計 ¥300 到達で以降を発火せず STOP。
- 実行規律: `--stage all` 禁止、`TTS_EXECUTION_MODE=STANDARD`(同期実行)明示、`--tts-backend speech_metadata_flash_lite` 必須、`--allow-legacy-backend` 禁止、`er012_e` は `--stage ledger`/`--stage writer` のみ、1 記事ずつ完結(Hormuz → Meta)、Master Store は reuse のみ、コード・Prompt・style の変更禁止(バグ発見時は STOP)。
- STOP 条件: 前委任と同じ+「JA 生成後も Advanced deviation で ja_source MAJOR が再発」「JA Writer O の R2 後も Ledger 逸脱が残る」。
- 試聴リンクは GitHub Pages のみ、ユーザー向け表記は Standard/Advanced。

## 固定ブロック

E-1/D-1/G-1/F-1 標準。T-0: 本委任文を `docs/pm/delegation_log/2026-09-29_FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_10.md` へ逐語保存し `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-29_FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_10.md --json-out docs/pm/delegation_log/2026-09-29_FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_10.md_check.json` を実行し結果1行記録。T-2: `TTS_EXECUTION_MODE=STANDARD`、コマンド逐語記録。T-3: 上記 Guardrail。

## 手順(記事ごと: Hormuz → Meta)

0. **JA 経路の事前確認(¥0)**: `er019_family_x_entertainment_production_runner_01.py` の JA 生成が `build_original_prompt()`(`CONCRETENESS_CONTROL_AN3_BLOCK` 含む)を使い、`grep -n "再び増やさない" er0*.py` が 0 件、`verbatim_shas()` に `concreteness_an3_block_sha256` が含まれることを確認・記録。想定 call 数(Original+R1+R2+deviation check)と費用を記録してから発火。既存 Ledger(前委任で reuse した `NEWS-FAMILY-X-B3-FACT-SELECTION-PRODUCTION-WIRING-01` 由来)をそのまま使う(Ledger 再生成しない)。
1. **JA 生成**: Production 正式 JA 経路で `er019_output/family_x_refresh_e2e_01/<slug>/run_02/` に JA 記事を生成。JA 側 Deviation Check が LEDGER_COMPLIANT(または R2 で解消)であること、`verbatim_shas`・記号正規化 0 違反・段落数 ≥3 を記録。前委任 run_01 の MAJOR claim(「oil prices are linked to gasoline prices and transportation costs」)相当が新 JA に含まれるか、含まれるなら Ledger に対応 fact があるかを記録(STOP 判断の材料)。
2. **Writer 段**: `er012_e ... --stage ledger`(reuse)→ `--stage writer`(run_02)。Advanced 忠実英訳 → Deviation Check(MAJOR→must-fix retry 1 回、ja_source なら STOP)→ Standard A2 → 構造 Gate(title/In One Line/heading 混入)→ 3 分割 → In One Line → Comment1〜4 → KP 抽出。
3. **Audio 段**: `--stage scaffold` → `--stage tts` → `--stage assemble` → `--stage player`(E2E-PLAN 行 657〜660 のコマンド逐語、`--run run_02 --level both`)。
4. **Gate**(記事×レベル、evidence 付き表): `docs/pm/ACTIVE_TASK.md` Gate 13 項目+Opus 9 項目(REPORT 行 682〜692)。前委任 _09 の REPORT §E2E の Gate 表を「未到達」から実測へ更新。
5. **試聴ページ** `user_test/family_x_refresh_e2e_01/index.html`(4 episode、完成 mp3+segment 別、Style Prompt 全文実表示、model/voice、reuse 元 master_audio_id、Standard/Advanced 表記)→ commit・push → Pages 公開確認 7 項目(HTTP 200/headless ブラウザ DOM dump/`(existing …)` 0 件/Style 全文/player 存在/mp3 200+decode/表示 Style と metadata 一致)。
6. **費用**: A 実測(記事×レベル×段階、JA 生成含む、累計。前委任 ≈ ¥1 を合算)/B 差分(記事あたり LLM call・TTS segment の増減を実測 call 数で裏付け: KP 解説 +1 LLM +5 TTS、Phrase 再掲 0、Heading Readout −2、Master reuse 0、Comment 4 本化)。
7. **REPORT**: `FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_REPORT.md` §E2E に「再開(run_02)」を追記(Fable 判定の要旨、JA 生成の evidence、Gate 表、Pages 7 項目、費用 A/B、Closeout 10 項目充足表[SSOT 未反映と明記])。設計書 §9-E2E 追記。RESULT_PACKET へ SSOT 文案: OPEN 新設候補「Deviation Check judge の run 間非決定性(同一 Ledger・同一 JA で COMPLIANT→MAJOR、evidence=run_01 `advanced_attempt1.json` vs er039 `AN3-T0_deviation.json`)」、OPEN-228 CLOSED/SUPERSEDED、OPEN-230、各仕様の `PRODUCTION_WIRED` 同期案(Fable Gate 3 後)。

## 実行コマンド全文(逐語記録。<slug>=hormuz / meta、run_02)

- 事前: `git stash list`、`git status --short | head -20`、`grep -n "再び増やさない" er0*.py`
- JA: `er019_family_x_entertainment_production_runner_01.py` の JA 生成コマンド(引数は同ファイルの `--help`/既存 REPORT `FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01_REPORT.md` の regression 実行例に従う。`--budget-jpy 30`)
- writer: `.venv\Scripts\python.exe er012_e_family_entertainment_two_level_runner_01.py --slug <slug> --run run_02 --stage ledger` → `--stage writer --budget-jpy 30`(実引数は `--help` で確認し逐語記録)
- audio: E2E-PLAN 行 657〜660(`--run run_02`)
- Pages: `curl -sI https://shimomura055.github.io/eigo-radio/user_test/family_x_refresh_e2e_01/index.html`、headless ブラウザ DOM dump、mp3 `curl -sI`+decode

## Git

- add 対象(path 指定のみ): `er019_output/family_x_refresh_e2e_01/**`(run_02 の audit json・parts・player・完成 mp3。wav は既存方針)、`user_test/family_x_refresh_e2e_01/**`、REPORT、設計書、delegation_log+`_check.json`、本 E2E 由来の telemetry 追記。記事ごとに commit(Hormuz 完了、Meta 完了、試聴ページ)。メッセージ例 `FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01 (E2E run_02): Hormuz Standard/Advanced をProduction正式経路(JA生成含む)で完成(Gate evidence付き)`、trailer `Management-ID: FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01`。push。

## 報告(RESULT_PACKET_RFE2 + handback、目安45行)

事前確認/JA 生成 evidence(verbatim_shas・deviation・記号・段落数、MAJOR claim の扱い)/記事×レベルの Gate 表(13+9)/STOPPED・retry・Local Rewrite の有無/Pages 7 項目/試聴 URL(GitHub Pages)/費用 A 実測(累計)・B 差分/Closeout 10 項目充足/commit hash・raw URL/STOP 有無と理由。
