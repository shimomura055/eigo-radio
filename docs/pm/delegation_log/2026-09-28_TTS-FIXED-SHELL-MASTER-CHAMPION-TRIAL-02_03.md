## 管理ID

TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-02(SSOT反映のみ、委任 _03)。一時ファイル `docs/pm/ACTIVE_TASK_CH2S.md` / `docs/pm/RESULT_PACKET_CH2S.md`(commitしない)。並行: 別Sonnet 1件(Task 3 `er044_*`/`user_test/tts_variable_role_style_trial_02/`、SSOT 編集権なし)→ 触れない。**削除・移動・`rm`・`git clean`・stash/rebase/reset/amend/force push 禁止**。自タスクの所有ファイル(SSOT 3点+REPORT_LEDGER+delegation_log)以外に触れない。未追跡ファイルは他Agent/ユーザーの作業物として扱う。push競合時は `git merge origin/main` のみ、conflictは中断報告。

## 性質/到達上限Status/禁止事項

- 性質: SSOT反映(記録のみ)。コード・Prompt・CURRENT_SPEC・PM_GOVERNANCE は変更しない。API支出なし(上限¥0)。
- **SSOT編集権: あり**(`DECISION_LOG.md`/`OPEN_ITEMS.md`/`docs/pm/REPORT_LEDGER.md`。`CURRENT_SPEC.md`・`docs/pm/PM_GOVERNANCE.md` は無変更)。現在SSOT編集権を持つAgentは本タスクのみ。差分所有者確認: 開始時と commit 直前に `git status --porcelain CURRENT_SPEC.md DECISION_LOG.md OPEN_ITEMS.md docs/pm/REPORT_LEDGER.md docs/pm/PM_GOVERNANCE.md` を実行し本タスク以外の差分ゼロを記録(他Agent差分があれば add せずSTOP)。
- 禁止: `VALIDATED`/`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED` と書かない(Status `USER_DECISION_REQUIRED`[Fable判定])。Champion を決めない。APIキー本文表示禁止。ユーザー向け表記は Standard/Advanced。DECISION_LOG.md は CRLF 改行のため、Edit が失敗する場合は Python で CRLF を明示して追記(前例あり)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)

E-1/D-1/G-1/F-1 標準(SSOT 全文Read禁止)。
T-0: 本委任文を `docs/pm/delegation_log/2026-09-28_TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-02_03.md` へ逐語保存し、`.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-28_TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-02_03.md --json-out docs/pm/delegation_log/2026-09-28_TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-02_03.md_check.json` を実行し結果1行記録。
T-2: TTSなし。T-3: API支出なし。

## 事前指定Read一覧

- `docs/pm/RESULT_PACKET_CH2.md`(SSOT文案、参考)
- `TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-02_REPORT.md`: Grep `Style|STOPPED|cost|F0|## 13` → 該当範囲(根拠)

## 事前指定Grep一覧+追記位置・更新位置の手順

- `docs/pm/REPORT_LEDGER.md`: Grep `KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-03` → 直後に新行。
- `DECISION_LOG.md`: Grep `KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-03` → 末尾に新エントリ。
- `OPEN_ITEMS.md`: Grep `OPEN-222|OPEN-223` → 本体行に追記。

## 反映内容(Fable確認済み事実)

commit `7f01bad1`+`29d1b0c3`(本体)、`df96c37c`(修正1回目)、push済み。固定 phrase 10件(EN 9+JA 1)で A=現行 Production Master のコピー再利用(¥0)、B/C=新規生成。Style 全文: group1(welcome/preview_intro/key_phrases_intro)B・C=「natural, clear, conversational」(現行と同一文言で2回生成)、group2(full_story_intro)B・C=「natural, clear, conversational, unhurried pace, with a brief pause before continuing」、group3(num_one〜num_five、5個セット一括)B=「calm, steady, declarative tone, even volume and pace across the set, ending each word with a clear falling pitch, stated plainly, never rising like a question」/C=「measured, matter-of-fact delivery, consistent energy and tempo for every word, plain falling pitch at the end, spoken as a flat statement, not a question」、group4(point_explanation JA)B=「自然な抑揚をつけて、はっきりと落ち着いた調子で話す」/C=「やわらかい自然な抑揚で、簡潔かつ丁寧に伝える」。結果: A 10/10 OK、B 7/10(STOPPED: num_one/num_three/num_four、ASR text は「一」「三」「四」等の CJK 数字)、C 9/10(STOPPED: num_three「三」)。welcome/preview/key_phrases/full_story_intro/point_explanation は全候補 drift なし。簡易 F0 proxy では現行 Baseline(A)の num_four/num_five が上昇終止(疑問形っぽさ)判定となり、ユーザー指摘と方向一致。修正1回目で ASR 未合格 attempt 12件の音声を「人間確認用・Production 登録不可」section として試聴ページへ追加(新規生成なし、¥0)。費用合計 ¥1.54(Guardrail ¥40)。Regression 17/17。Production Master Store・code・Prompt 無変更(Trial Store 隔離)。Pages 7項目確認 PASS(headless Edge、`<audio>` 43件)。共有ログ `er011_output/attempt_history.jsonl` への追記(OPEN-223 同型)。Opus発火なし。Fable判定 `USER_DECISION_REQUIRED`(phrase ごとの Champion 選定待ち)。試聴: https://shimomura055.github.io/eigo-radio/user_test/fixed_shell_champion_trial_02/index.html

1. `docs/pm/REPORT_LEDGER.md`: 新行(Status `USER_DECISION_REQUIRED`[Fable判定]、commit `7f01bad1`/`29d1b0c3`/`df96c37c`、Opus発火なし、REPORT名)。
2. `DECISION_LOG.md` 末尾に1エントリ `TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-02: Trial記録(2026-09-28)`: 上記を簡潔に。「Champion 選定・Production 配線はユーザー判断後に別管理ID」「固定 phrase は Task 3(可変 Role Style)の比較表から除外(ユーザー指示)」を明記。
3. `OPEN_ITEMS.md`: OPEN-222 本体行へ「2026-09-28追記(TRIAL-02): 全く新しい2種の style 文言でも num_three(B/C)・num_one/num_four(B)が3 attempt 不合格、ASR text は CJK 数字(一/三/四)。style 非依存の極短数字語限界の考察を追加裏付け。未合格 attempt 音声は人間確認用に試聴ページへ公開(Production 登録不可のまま)。現行 Baseline の num_four/num_five に上昇終止の疑い(F0 proxy)」を追記。OPEN-223 本体行へ「TRIAL-02 でも attempt_history.jsonl 追記(同型)」を1行追記。新規 OPEN は作らない。

## 実行コマンド全文

- `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-28_TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-02_03.md --json-out docs/pm/delegation_log/2026-09-28_TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-02_03.md_check.json`
- `git status --porcelain CURRENT_SPEC.md DECISION_LOG.md OPEN_ITEMS.md docs/pm/REPORT_LEDGER.md docs/pm/PM_GOVERNANCE.md`(2回)

## SSOT追記文

上記「反映内容」のとおり。

## Git

- add対象(path指定のみ、`git add -A` 禁止): `DECISION_LOG.md`、`OPEN_ITEMS.md`、`docs/pm/REPORT_LEDGER.md`、delegation_log+`_check.json`。
- メッセージ: `TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-02: Trial記録をSSOTへ反映(USER_DECISION_REQUIRED、OPEN-222/223追記)`、trailer `Management-ID: TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-02`。`git push origin main`。

## 報告(RESULT_PACKET_CH2S + handback、目安20行)

適用箇所/T-0結果1行/差分所有者確認2回/未実施の禁止操作/commit hash・push結果/raw URL(3ファイル)/注意点。
