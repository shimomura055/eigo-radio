## 管理ID

TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01(SSOT反映のみ。本管理IDの実装系Sonnet委任は上限到達済みだが、本委任は記録のみの別区分。委任 _06)。一時ファイル `docs/pm/ACTIVE_TASK_RS5.md` / `docs/pm/RESULT_PACKET_RS5.md`(commitしない)。並行Agentなし。**削除・移動・`rm`・`git clean`・stash/rebase/reset/amend/force push 禁止**。自タスクの所有ファイル(SSOT 3点+delegation_log)以外に触れない。未追跡ファイルは他Agent/ユーザーの作業物として扱う。push競合時は `git merge origin/main` のみ、conflictは中断報告。

## 性質/到達上限Status/禁止事項

- 性質: SSOT反映(記録のみ)。コード・Prompt・CURRENT_SPEC・PM_GOVERNANCE は変更しない。API支出なし(上限¥0)。
- **SSOT編集権: あり**(`docs/pm/REPORT_LEDGER.md` / `DECISION_LOG.md` / `OPEN_ITEMS.md` の3点のみ。`CURRENT_SPEC.md`・`docs/pm/PM_GOVERNANCE.md` は無変更)。現在SSOT編集権を持つAgentは本タスクのみ。
- 禁止: Status を `VALIDATED`/`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED` と書かない(`USER_DECISION_REQUIRED`[Fable判定]のまま)。ユーザー判断事項を決めない。PM_GOVERNANCEへの新ルール記載はしない(提案はFableがユーザーへ出す)。APIキー本文表示禁止。ユーザー向け表記は Standard/Advanced(A2/B1Bは内部表記としてのみ併記可)、TTS実行は 同期実行/バッチ実行。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない。
D-1: Grep→該当行範囲Read。SSOT 3点の全文Read禁止。
G-1: git出力は `--porcelain`/`--stat`/`--short` で最小化。
F-1: transcript退避不要。
T-0: 本委任文を `docs/pm/delegation_log/2026-09-28_TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01_06.md` へ逐語保存し、`.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-28_TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01_06.md --json-out docs/pm/delegation_log/2026-09-28_TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01_06.md_check.json` を実行し結果1行記録(FAILでも内容改変してPASSさせない)。
T-2: TTSなし。T-3: API支出なし。

## 事前指定Read一覧

- `TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01_REPORT.md`: §13〜§15(Grep `### 13-|## §14|## §15|### 14|### 15` → 該当範囲、根拠として使用)
- `docs/pm/REPORT_LEDGER.md`: Grep `TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01` → 既存行
- `DECISION_LOG.md`: Grep `TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-01: Trial記録` → 末尾位置
- `OPEN_ITEMS.md`: Grep `OPEN-222|OPEN-223|OPEN-225` → 本体行・末尾番号

## 反映内容(Fable確認済み事実)

commit: `132828cb`(追補=reuse実装+インシデント)、`105ec62d`(修正2回目=evidence再紐付け)、`5f84c670`(修正3回目=試聴ページ整合)。いずれもpush済み。
(a) 追補: Advanced(B1B)共有narration num_two/num_three を Production Master Audio Store(read-only)の ASR verified 済み既存Master(`75d64a8e14e3b8592db99a5a`/`410e12ebe93da7a797860b89`、`FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]` style、TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-02由来)から `--reuse-production-master num_two,num_three` でコピー再利用(¥0、sha256一致、Production Store無変更、Human Review Lock状態無変更)。ユーザー指示「Two./Three.は毎回再生成せず既存合格Masterをreuse」に適合。
(b) インシデント(事後開示): 動作確認で `--stage all` を実行し、Trial script が shell 層以外に cache を持たない single-run 設計だったため、Advanced の Key Phrase 10 segment+主記事 9 segment が意図せず再生成(実費 ¥30.80、Guardrail ¥5 の約6.2倍)。Bash timeout で background 化し検知が遅れ、`raw_usage_log.jsonl` で検出後に process 強制終了。Production Master Store・Human Review Lock 共有キューは sha256/mtime で不変。pre-incident の wav は git 管理外のため復元不可。既存Gate(`verify_episode_audio_validation_gate`、ASSET_HASH_MISMATCH)が Advanced full assembly を正しくブロック(回避せず)。Sonnet は STOP して選択肢提示。
(c) 修正2回目(Fable判断、ユーザー基準「小口APIは事前確認不要」内): 新規TTS 0件(gemini 行数 85→85 実測)で、14 segment は再生成時の中間 attempt file(sha256一致)の実測ASR結果を再紐付け、KP JA 5 segment は既存Production検証関数で ASR 再検証(openai_asr +5、¥0.06)。Gate PASS → `--stage assemble` のみで Advanced full assembly → `hormuz_advanced_trial.mp3`(4分56秒)→ ページ更新。Regression 16/16。
(d) 修正3回目(¥0、API 0件): 個別プレビュー mp3 21件を現音声から再変換(96kbps、既存ページとの一貫性優先で128k指示から変更)、テーブルの num_two/num_three を OK(reuse由来)へ更新。
(e) 本追補の合計費用 ¥30.87。本管理IDの実装系Sonnet委任は初回+修正3回の上限到達。Fable判定 `USER_DECISION_REQUIRED`(ユーザー試聴待ち)は変わらず。Opus発火なし。

1. `docs/pm/REPORT_LEDGER.md`: 既存 `TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01` 行を更新(Status `USER_DECISION_REQUIRED` 維持、commit に `132828cb`/`105ec62d`/`5f84c670` を追加、備考に「追補: 既存合格Master reuse+コスト超過インシデント事後開示(¥30.87)、Advanced full 試聴可」)。
2. `DECISION_LOG.md` 末尾に1エントリ `TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01: 追補(既存合格Master reuse)+Guardrail超過インシデントの事後開示(2026-09-28)`: 上記 (a)〜(e) を簡潔に。原因(single-run設計+`--stage all`での動作確認+timeout background化)、Production実害なし、pre-incident wav復元不可、Gateが正常動作、再発防止案は「動作確認は部分stage実行のみ・`--stage all`禁止を委任文に固定」「再生成を伴うstage実行前に対象segment数・想定費用を記録」「Trial scriptの再実行guard(既存合格音声の再生成防止)は OPEN-226 で追跡」と記載し、正式ルール化はユーザー判断待ちと明記。
3. `OPEN_ITEMS.md`: 新規 **OPEN-226**「Trial/Production runner の再実行時に既存合格音声を再生成しない guard(冪等性)の要否。TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01 追補で `--stage all` 再実行により Advanced 19 segment が意図せず再生成され ¥30.80(Guardrail ¥5 超過)。現状 shell 層のみ Master Store cache、記事本文・Key Phrase は run ごと再生成が設計。Production runner でも同型リスクの有無を要確認。`OPEN`」。OPEN-222 本体行へ「2026-09-28追記: Trial上は Production 既存合格Master の reuse で num_two/num_three を OK 化(Role style 音声の数字語不安定性自体は未解決)」を追記。
4. 差分所有者確認(必須): 開始時と commit 直前の2回、`git status --porcelain CURRENT_SPEC.md DECISION_LOG.md OPEN_ITEMS.md docs/pm/REPORT_LEDGER.md docs/pm/PM_GOVERNANCE.md` を実行し、本タスク以外の差分ゼロを記録。他Agent差分があれば add せず STOP。

## 実行コマンド全文

- `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-28_TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01_06.md --json-out docs/pm/delegation_log/2026-09-28_TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01_06.md_check.json`
- `git status --porcelain CURRENT_SPEC.md DECISION_LOG.md OPEN_ITEMS.md docs/pm/REPORT_LEDGER.md docs/pm/PM_GOVERNANCE.md`(2回)

## SSOT追記文

上記「反映内容」のとおり。

## Git

- add対象(path指定のみ、`git add -A` 禁止): `docs/pm/REPORT_LEDGER.md`、`DECISION_LOG.md`、`OPEN_ITEMS.md`、`docs/pm/delegation_log/2026-09-28_TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01_06.md`、同 `_check.json`。SSOT編集権: あり(上記3点)。
- メッセージ: `TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01: 追補(既存合格Master reuse)+Guardrail超過インシデント事後開示をSSOTへ反映(OPEN-226新設、OPEN-222追記)`、trailer `Management-ID: TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01`。`git push origin main`。

## 報告(RESULT_PACKET_RS5 + handback、目安20行)

適用箇所/T-0結果1行/差分所有者確認2回/未実施の禁止操作/commit hash・push結果/raw URL(3 SSOT)/注意点。
