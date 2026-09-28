## 管理ID

PM-USER-DECISIONS-2026-09-28-CONSOLIDATION-SSOT-02(SSOT反映のみ)。一時ファイル `docs/pm/RESULT_PACKET_UD2.md`(commitしない)。並行: 別Sonnet 1件(Task 1 修正 `er045_*`/`user_test/no_heading_trial_01/`、SSOT 編集権なし)+Opus 読み取り専用レビュー 1件 → 触れない。**削除・移動・`rm`・`git clean`・stash/rebase/reset/amend/force push 禁止**。自タスクの所有ファイル(SSOT 4点+REPORT_LEDGER+PM_GOVERNANCE+delegation_log)以外に触れない。未追跡ファイルは他Agent/ユーザーの作業物として扱う。push競合時は `git merge origin/main` のみ、conflictは中断報告。

## 性質/到達上限Status/禁止事項

- 性質: ユーザー正式決定(2026-09-28)と完了 Trial の記録。コード・Prompt は変更しない。API支出なし(上限¥0)。
- **SSOT編集権: あり**(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/`docs/pm/REPORT_LEDGER.md`/`docs/pm/PM_GOVERNANCE.md`[8節 (h) のみ])。現在 SSOT 編集権を持つ Agent は本タスクのみ。差分所有者確認: 開始時と commit 直前に `git status --porcelain CURRENT_SPEC.md DECISION_LOG.md OPEN_ITEMS.md docs/pm/REPORT_LEDGER.md docs/pm/PM_GOVERNANCE.md` を実行し本タスク以外の差分ゼロを記録(他Agent差分があれば add せずSTOP)。
- 禁止: `PRODUCTION_WIRED` と書かない。ユーザー決定にない判断をしない。解消済み事項を `USER_DECISION_REQUIRED` と書かない。APIキー本文表示禁止。DECISION_LOG.md は CRLF(Edit 失敗時は Python で CRLF 明示追記)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)

E-1/D-1/G-1/F-1 標準(SSOT 全文Read禁止、Grep→該当範囲)。
T-0: 本委任文を `docs/pm/delegation_log/2026-09-28_PM-USER-DECISIONS-2026-09-28-CONSOLIDATION-SSOT-02.md` へ逐語保存し、`.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-28_PM-USER-DECISIONS-2026-09-28-CONSOLIDATION-SSOT-02.md --json-out docs/pm/delegation_log/2026-09-28_PM-USER-DECISIONS-2026-09-28-CONSOLIDATION-SSOT-02_check.json` を実行し結果1行記録。
T-2: TTSなし。T-3: API支出なし。

## 事前指定Read一覧(文案の根拠)

- `docs/pm/RESULT_PACKET_AN3D.md`(reminder 削除の SSOT 文案)
- `KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-04_REPORT.md` §11(SSOT 文案)
- `TTS-FIXED-SHELL-NUMBER-THREE-FIVE-RETRIAL-01_REPORT.md` §15(SSOT 文案)
- `docs/pm/PM_GOVERNANCE.md`: Grep `\(h\)|git clean` → 8節 (h) の現行文

## 事前指定Grep一覧+追記位置・更新位置の手順

- `CURRENT_SPEC.md`: Grep `Concreteness Control|AN3|REMINDER|再び増やさない` → AN3-T0 小節から reminder 記述を削除し「AN3 は Original 側のみ(Trial-02 と同一条件)」に是正。
- `docs/pm/PM_GOVERNANCE.md`: Grep `(h)` → 8節 (h) の「正式ルール化はユーザー判断待ち」を削除し、正式ルールとして確定(下記文言)。
- `DECISION_LOG.md`: Grep `TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01` → 末尾に新エントリ(1 本にまとめてよい、見出しは管理ID)。
- `OPEN_ITEMS.md`: Grep `OPEN-220|OPEN-221|OPEN-222|OPEN-225|OPEN-227` → 各本体行更新。
- `docs/pm/REPORT_LEDGER.md`: Grep `AN3-T0-PRODUCTION-WIRING-01|AUDIO-STYLE-TRIAL-04|NUMBER-THREE-FIVE-RETRIAL-01` → 行更新/新行。

## 反映内容(ユーザー正式決定 2026-09-28、Fable 転記)

(1) **R1/R2 reminder 不採用・削除**(commit `54739a9d`/`8d9ef6c6`): 理由=Trial-02 では Original 生成時に AN3(A3+N2)を追加し R1/R2 は既存 Revision 指示のみだった。未 Trial 追加仕様のため正式経路から削除、AN3 は Original 側のみ(Trial-02 と同一条件)。CURRENT_SPEC の AN3-T0 小節を是正(reminder 記述削除、verbatim_shas のキーも削除済みと記載)。OPEN-227 の文言から「本配線では REMINDER のみ付与」を削除(非対称性の記録は維持)。REPORT_LEDGER の Wiring-01 行備考に「reminder 削除済み(ユーザー決定)」を追記。Status は `APPROVED_FOR_PRODUCTION`(Gate 3 は OPEN-228 の順序に従い保留)。
(2) **PM_GOVERNANCE 8節 (h) 正式採用**: 文言を「委任 Agent は、自タスク外のファイル・差分を削除してはならない。`rm`/`git clean` 等により、他 Agent・他タスク・未 commit 作業を消してはならない。並列 Agent 環境では、diff ownership 確認/自タスク外差分を触らない/不明な未 commit 差分を勝手に cleanup しない、を徹底する(2026-09-28 ユーザー正式採用)」に確定。DECISION_LOG に記録。
(3) **origin/main 先行 commit**: `19065b87`/`686934d3`/`3cd361c0`(`user_test/tts_all_role_style_trial_01/` 周辺)はユーザーの ChatGPT セッションから直接 GitHub へ入れた正当な試聴ページ修正。不明な第三者変更として扱わない旨を DECISION_LOG に記録。
(4) **OPEN-220 → `DEFERRED`**(Status 欄を更新。理由=現行英語化 Prompt 維持・英語側への追加抑制なし、はユーザー決定済み。再度 USER_DECISION_REQUIRED にしない)。
(5) **OPEN-225(`a2_jt_debug.json`)→ ユーザー判断対象外**: Status を `CLOSED(ユーザー判断対象外。Production/Regression/runtime evidence に必要と判明した場合のみ技術課題として Claude 側が報告)` に更新。
(6) **固定フレーズ Champion 対応**: 既に commit `d1ddf454` で機械確定・記録済み(左=A/中=B/右=C)。再確認不要である旨を DECISION_LOG の同エントリに 1 行追記。
(7) **KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-04 記録**(commit `650df8d8`/`dc75d598`): 中間 3 案 A=「clear, precise, at a slightly relaxed pace」B=「clear, precise, at a measured pace, without dragging」C=「clear, precise, carefully paced for understanding, without slowing down」、model gemini-3.8-flash-lite-tts/voice Aoede、15 件 OK・retry 0・drift なし、duration は Before < A≈B < C < unhurried、費用 ¥2.02、Regression 21/21、Production 無変更、Pages 7 項目 PASS。Status `USER_DECISION_REQUIRED`(Fable 判定、試聴で A/B/C 選択待ち)。REPORT_LEDGER 新行、DECISION_LOG、OPEN-221 追記(REPORT §11 文案を使用)。
(8) **TTS-FIXED-SHELL-NUMBER-THREE-FIVE-RETRIAL-01 記録**(commit `fa37cd85`/`59105faa`): 採用済み One(C)/Two(B)/Four(C)と同 model(Flash-Lite)・同 voice(Charon)・同 Style 系統(B/C 既存定数)で Three/Five 各 4 take、16 take 中 OK 7(Three: B-take1/B-take4/C-take2、Five: B-take1/C-take2/C-take3/C-take4)、不合格 9(極短数字語の既知パターン)は人間確認用として掲載、費用 ¥1.69、Regression 19/19、Production Store 無変更、Pages 7 項目 PASS。Status `USER_DECISION_REQUIRED`(take 選択待ち)。REPORT_LEDGER 新行、DECISION_LOG、OPEN-222 追記(REPORT §15 文案を使用)。
(9) **TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01 の commit `9edfdc5f` に `Management-ID:` trailer が欠落**(Sonnet の付け忘れ、amend/force push は禁止のため未修正)。DECISION_LOG に事後開示として 1 行記録(履歴書き換えはしない)。

## 実行コマンド全文

- `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-28_PM-USER-DECISIONS-2026-09-28-CONSOLIDATION-SSOT-02.md --json-out docs/pm/delegation_log/2026-09-28_PM-USER-DECISIONS-2026-09-28-CONSOLIDATION-SSOT-02_check.json`
- `git status --porcelain CURRENT_SPEC.md DECISION_LOG.md OPEN_ITEMS.md docs/pm/REPORT_LEDGER.md docs/pm/PM_GOVERNANCE.md`(2回)

## SSOT追記文

上記「反映内容」のとおり。

## Git

- add対象(path指定のみ、`git add -A` 禁止): SSOT 4点、`docs/pm/PM_GOVERNANCE.md`、delegation_log+`_check.json`。
- メッセージ: `PM-USER-DECISIONS-2026-09-28-CONSOLIDATION-SSOT-02: ユーザー整理6件(reminder削除/PM_GOVERNANCE(h)正式採用/先行commit正当/OPEN-220 DEFERRED/OPEN-225対象外/Champion対応確定)+TRIAL-04・RETRIAL-01記録をSSOTへ反映`、trailer `Management-ID: PM-USER-DECISIONS-2026-09-28-CONSOLIDATION-SSOT-02`。`git push origin main`。

## 報告(RESULT_PACKET_UD2 + handback、目安25行)

適用箇所(9 件それぞれ)/T-0結果/差分所有者確認2回/未実施の禁止操作/commit hash・push結果/raw URL(5ファイル)/注意点。
