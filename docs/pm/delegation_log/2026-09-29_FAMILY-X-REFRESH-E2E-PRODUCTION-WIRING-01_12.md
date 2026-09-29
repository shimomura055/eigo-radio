## 管理ID

FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(Phase C / E2E run_03=案B 有効で Hormuz → Meta を Production 正式経路のみで完成 podcast+試聴ページまで、委任 _12)。前委任 _10(run_02 STOP)・_11(W6 案B 配線、commit `0171cb5c`/`77aa8873`)を引き継ぐ。一時ファイル `docs/pm/ACTIVE_TASK_RFE3.md` / `docs/pm/RESULT_PACKET_RFE3.md`(commitしない)。並行 Agent なし(`git pull --ff-only origin main`)。SSOT 4 点+REPORT_LEDGER は編集権なし(文案のみ。Closeout SSOT は Fable Gate 3 後に別委任)。**削除・移動・`rm`・`git clean`・`git stash`・rebase/reset/amend/force push 禁止**。未追跡ファイルは他タスク由来として触らない。push 競合時は `git merge origin/main` のみ。**APIキーは環境変数のみ、key 本文を表示・log・commit・報告に書かない**。

## 性質/到達上限Status/禁止事項

- 性質: 承認済み仕様(新記事構造/AN3-T0/J3・E2/Champion 10 件/KP 構造・解説 Variant B/Standard KP J3/Opus 是正 5 件/案B)を配線済みの **Production 正式経路のみ**で実行する E2E。Trial ではない。到達上限: 記事×レベルの Gate 結果を evidence 付きで報告(`PRODUCTION_WIRED` 判定は Fable Gate 3)。
- **費用 Guardrail**: 全体上限 **¥300**(本管理ID 累計 ≈ ¥6.05 を含む)。記事ごと: JA Writer O(案B 差し戻し込み)上限 ¥40、EN writer 上限 ¥30、段階別 `--budget-jpy`(scaffold ¥50 / tts ¥150 / assemble ¥10)。**累計 ¥300 到達で以降を発火せず STOP**。各発火前に「対象 segment 数・想定 call 数・retry 上限・想定費用・Guardrail」を記録(REPORT §W5 E2E-PLAN の数値を転記)。
- **実行規律**: `--stage all` 禁止(段階個別)。`TTS_EXECUTION_MODE=STANDARD`(同期実行)明示、コマンド全文逐語記録。`--tts-backend speech_metadata_flash_lite` 必須、`--allow-legacy-backend` 禁止。`er012_e` は `--stage ledger`/`--stage writer` のみ。**1 記事ずつ完結**(Hormuz を Standard/Advanced とも完成 → Gate → Meta)。Production Master Store は reuse のみ。Trial 出力の流用禁止(JA は Production JA 経路で生成)。コード・Prompt・style の変更禁止(バグ発見時は STOP)。試聴リンクは GitHub Pages のみ。ユーザー向け表記 Standard/Advanced。
- **STOP 条件**: 承認済み仕様との矛盾/新しい Product 判断が必要/未承認 Prompt 変更が必要/Standard・Advanced の意図しない非対称/共有 TTS 層の意味変更が必要/予算超過/案B の JA 差し戻し 1 回後も ja_source MAJOR(fail-closed STOP、2 回目の JA 再生成は禁止)/構造 Gate NG が retry 後も残る/KP 解説 text-gate が OK 以外の rank が残る/ASR cascade 3 attempt 到達で STOPPED が残る(Local Rewrite は既存 Production 方針で 1 回まで)。STOP 時はそこまでの evidence を commit して報告。

## 固定ブロック

E-1/D-1/G-1/F-1 標準。T-0: 本委任文を `docs/pm/delegation_log/2026-09-29_FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_12.md` へ逐語保存し `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-29_FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_12.md --json-out docs/pm/delegation_log/2026-09-29_FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_12.md_check.json` を実行し結果 1 行記録。T-2: `TTS_EXECUTION_MODE=STANDARD`、コマンド逐語記録。T-3: 上記 Guardrail。

## 手順(記事ごと: Hormuz → Meta。REPORT §W6 の run_03 手順・§W5 E2E-PLAN に従う)

0. **事前確認(¥0)**: `git stash list`(空を期待、非空なら触らず記録)、`git status --short | head`、Production 側 `grep -n "再び増やさない" er0*.py` 0 件、`run_03/` ディレクトリが未使用。**案B の有効化条件**(`<out-dir>/storyline_b3/fact_selection_evidence.json` の存在)を満たすよう、run_02 の `storyline_b3/`(an3_t0_wiring_regression 由来、同一トピック・sha256 記録)を run_03 へコピーし、案B が armed であることを起動ログ/`entry_point.json` で確認・記録。Ledger は既存 reuse(¥0)。
1. **JA 生成**(Production JA 経路 `er019_family_x_entertainment_production_runner_01.py` → JA Writer O、`--budget-jpy 40`): Original → Fact Check(must-fix 1 回)→ R1 → R2 → Fact Check。`verbatim_shas`(`concreteness_an3_block_sha256`)、記号 0 違反、段落数 ≥3 を記録。
2. **Writer 段**(`er012_e --stage ledger`(reuse)→ `--stage writer --budget-jpy 30`、run_03): Advanced 忠実英訳 → Deviation Check。**ja_source MAJOR が出た場合は案B が自動発動**(JA must-fix 差し戻し → JA 再生成 1 回 → 再 Fact Check → 再英訳 → 再 Deviation Check)。`ja_recheck_used`・差し戻した deviations・再生成後の判定を記録。translation MAJOR は既存 must-fix retry 1 回。Standard A2 → 構造 Gate(title/In One Line/heading 混入)→ 3 分割 → In One Line → Comment1〜4 → KP 抽出。
3. **Audio 段**: `--stage scaffold` → `--stage tts` → `--stage assemble` → `--stage player`(E2E-PLAN のコマンド逐語、`--run run_03 --level both`)。各段のコマンド・所要時間・費用実測。
4. **Gate**(記事×レベル、evidence 付き表): `docs/pm/ACTIVE_TASK.md` Gate 13 項目+Opus 9 項目(REPORT §W5 転記)+**ユーザー指定 Gate 3 確認項目**: 新 3 分割構造(body1/2/3 段落境界、parts.json)/Comment1〜4 の存在と組立順(Comment1→body1→Comment2→body2→Comment3→body3→Comment4→In One Line)/Heading Readout 撤去(segment 不在)/AN3-T0(JA Prompt の `concreteness_an3_block_sha256`、reminder 不在)/Standard・Advanced 双方完成/Advanced KP = `Phrase → 英語解説 → 同じ Phrase`(phrase_repeat が english と同一 path/sha256)/Standard KP = `Phrase → 日本語意味(J3) → 同じ Phrase`(japanese_meaning の `style_prefix` が J3 実文字列)/Variant B(explanation の `style_prefix` 実文字列・voice Aoede)/Fixed Master Champion(固定 shell 10 件 `reused=True`・`master_audio_id` が W2 表と一致・TTS call 0)/J3・E2(japanese_title/preview/comment/full_story/in_one_line の `style_prefix` 実文字列)/actual model・voice・style(全 segment の `tts_model_id`・`voice`・`style_prefix`、reuse 経路は `master_audio_key`)/cache guard(`style_version` 一致)/retry・fallback・regeneration(発生の有無と経路、Local Rewrite 使用の有無)/pronunciation resolver(適用ログ)/Audio Validation Gate PASS(ASSET_HASH_MISMATCH 0)/Production 正式 path(`entry_point.json` の runner・backend・stage 履歴、Trial ファイル未使用)/player(4 episode 行、Style 全文表示)/Dangling Reference Check(`HEADING_READOUT`・`NG_ACCEPTED_AFTER_RETRY`・旧 split 関数・旧 KP 構造への参照が Production 経路と audit に残っていないこと)。
5. **Meta** も同様(1〜4)。
6. **試聴ページ** `user_test/family_x_refresh_e2e_01/index.html`(4 episode: Hormuz/Meta × Standard/Advanced、完成 mp3 プレーヤー+segment 別プレーヤー、各 segment の Style Prompt **全文実表示**(省略・プレースホルダ禁止)、model/voice、reuse 元 master_audio_id、案B 発動有無、Standard/Advanced 表記)→ commit・push → **Pages 公開確認 7 項目**(HTTP 200/headless Edge or Chrome の DOM dump/`(existing 6-role value, unchanged)` 0 件/Style Prompt 全文実表示/audio player 存在/mp3 200+decode 再生可能/表示 Style と metadata の Style 一致)。Pages 反映待ち最大 10 分。
7. **費用**: A 実測(記事×レベル×段階、JA 生成・案B 差し戻し込み、本管理ID 累計 ≈ ¥6.05 と合算)/B 差分(記事あたり LLM call・TTS segment の増減を実測 call 数で裏付け: KP 解説 +1 LLM +5 TTS、Phrase 再掲 0、Heading Readout −2、Master reuse 0、Comment 4 本化、案B 発動時のみ JA 再生成+再英訳 ≈ +¥5〜6)。
8. **REPORT**: `FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_REPORT.md` §E2E に「run_03」を追記(事前確認、案B 発動記録、記事×レベルの実行ログ要約、Gate 表[13+9+ユーザー指定]、Pages 7 項目、費用 A/B、Closeout 10 項目充足表[SSOT 未反映と明記])。設計書 §9-E2E 追記。RESULT_PACKET へ SSOT 文案(OPEN-228 CLOSED/SUPERSEDED、OPEN-230、各仕様の `PRODUCTION_WIRED` 同期案、案B の PRODUCTION_WIRED 同期案=Fable Gate 3 後)。

## 実行コマンド全文(逐語記録。<slug>=hormuz / meta、run_03)

- 事前: `git stash list`、`git status --short | head -20`、`grep -n "再び増やさない" er0*.py`
- JA/writer/audio: REPORT §W6「run_03 の実行手順」と §W5 E2E-PLAN 行 657〜660 のコマンド(`--run run_03`、`TTS_EXECUTION_MODE=STANDARD` を環境変数で明示、`--budget-jpy` は上記上限)
- Pages: `curl -sI https://shimomura055.github.io/eigo-radio/user_test/family_x_refresh_e2e_01/index.html`、headless ブラウザ DOM dump、mp3 `curl -sI`+decode

## Git

- add 対象(path 指定のみ): `er019_output/family_x_refresh_e2e_01/**/run_03/**`(audit json・parts・player・完成 mp3。wav は既存方針)、`user_test/family_x_refresh_e2e_01/**`、REPORT、設計書、delegation_log+`_check.json`、本 E2E 由来の telemetry 追記。記事ごとに commit(Hormuz 完了、Meta 完了、試聴ページ)。メッセージ例 `FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01 (E2E run_03): Hormuz Standard/Advanced をProduction正式経路(案B有効)で完成(Gate evidence付き)`、trailer `Management-ID: FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01`。push。

## 報告(RESULT_PACKET_RFE3 + handback、目安50行)

事前確認/案B 発動の有無と記録(記事ごと)/記事×レベルの Gate 表(13+9+ユーザー指定 20 項目、PASS/FAIL/evidence パス)/STOPPED・retry・Local Rewrite の有無/Pages 7 項目/試聴 URL(GitHub Pages)/費用 A 実測(段階別・累計)・B 差分/Closeout 10 項目充足/commit hash・raw URL/STOP 有無と理由。
