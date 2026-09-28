## 管理ID

KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-03(SSOT反映のみ、委任 _02)。一時ファイル `docs/pm/ACTIVE_TASK_KA3S.md` / `docs/pm/RESULT_PACKET_KA3S.md`(commitしない)。並行: 別Sonnet 2件(Task 2 `er043_*`/`user_test/fixed_shell_champion_trial_02/`、Task 3 `er044_*`/`user_test/tts_variable_role_style_trial_02/`、いずれも SSOT 編集権なし)→ これらのファイルに触れない。**削除・移動・`rm`・`git clean`・stash/rebase/reset/amend/force push 禁止**。自タスクの所有ファイル(SSOT 4点+REPORT_LEDGER+delegation_log)以外に触れない。未追跡ファイルは他Agent/ユーザーの作業物として扱う。push競合時は `git merge origin/main` のみ、conflictは中断報告。

## 性質/到達上限Status/禁止事項

- 性質: SSOT反映(記録のみ)。コード・Prompt・PM_GOVERNANCE は変更しない。API支出なし(上限¥0)。
- **SSOT編集権: あり**(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/`docs/pm/REPORT_LEDGER.md`。`docs/pm/PM_GOVERNANCE.md` は無変更)。現在SSOT編集権を持つAgentは本タスクのみ。差分所有者確認: 開始時と commit 直前に `git status --porcelain CURRENT_SPEC.md DECISION_LOG.md OPEN_ITEMS.md docs/pm/REPORT_LEDGER.md docs/pm/PM_GOVERNANCE.md` を実行し本タスク以外の差分ゼロを記録(他Agent差分があれば add せずSTOP)。
- 禁止: 音声 Style の Trial 結果を `VALIDATED`/`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED` と書かない(Status `USER_DECISION_REQUIRED`[Fable判定])。text 仕様の `APPROVED_FOR_PRODUCTION` は **ユーザー正式決定(2026-09-28)として記録**するが、`PRODUCTION_WIRED` とは書かない(配線未実施)。ユーザー判断事項を決めない。APIキー本文表示禁止。ユーザー向け表記は Standard/Advanced。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない。D-1: Grep→該当行範囲Read。SSOT の全文Read禁止。G-1: git出力最小化。F-1: transcript退避不要。
T-0: 本委任文を `docs/pm/delegation_log/2026-09-28_KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-03_02.md` へ逐語保存し、`.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-28_KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-03_02.md --json-out docs/pm/delegation_log/2026-09-28_KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-03_02.md_check.json` を実行し結果1行記録。
T-2: TTSなし。T-3: API支出なし。

## 事前指定Read一覧

- `docs/pm/RESULT_PACKET_KA3.md`(SSOT文案、参考)
- `KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-03_REPORT.md`: Grep `Style|cost|asr_verified|Pages` → 該当範囲(根拠)
- `KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-TRIAL-02_REPORT.md`: §3(94-106行、B 解説文5件の逐語)

## 事前指定Grep一覧+追記位置・更新位置の手順

- `CURRENT_SPEC.md`: Grep `Key Phrase|japanese_gloss|KEY_PHRASE_EXPLANATION_EN|Advanced` → Key Phrase 節の末尾に小節を追記。
- `DECISION_LOG.md`: Grep `FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01` → 末尾に新エントリ。
- `OPEN_ITEMS.md`: Grep `OPEN-221` → 本体行に追記。
- `docs/pm/REPORT_LEDGER.md`: Grep `KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-TRIAL-02` → 当該行の Status 更新+直後に TRIAL-03 新行。

## 反映内容(Fable確認済み事実)

(a) **ユーザー正式決定(2026-09-28)**: Advanced Key Phrase の英語解説 **text 仕様**(TRIAL-02 の B 候補: 同一英語 Phrase+平易な英語解説、TRIAL-01 の explanation_en 仕様文を逐語再利用、語数上限15語目安、新規Fact追加なし)は `APPROVED_FOR_PRODUCTION`。**Production wiring は未実施**(別管理IDでユーザー判断後に実施)。`KEY_PHRASE_EXPLANATION_EN` Role は Production 未実装のまま。
(b) TRIAL-03(音声 Style のみ): commit `484c233e`(push済み)。Hormuz 既存5 Phrase・B 解説文を逐語使用(再生成・再選定なし)。Before=「clear, precise, explanatory」(er041 既存音声を style metadata 一致確認のうえ reuse、新規0件)/After=「clear, precise, unhurried」(5件新規、Production 同一関数、Trial Store 隔離、同期実行)。After 5件 asr_verified=True、retry 0、drift なし。費用 ¥0.73(上限¥10)。Regression 16/16。Production code/Prompt/Key Phrase 選定/DB Hybrid/Production Master Store 無変更。Pages 7項目確認(HTTP 200、headless Chrome DOM、省略表記0件、Style 全文表示、audio 15件、mp3 15件 200+デコードOK、Style metadata 一致)。Opus 発火なし。Fable判定 `USER_DECISION_REQUIRED`(ユーザー試聴で Before/After を選ぶ)。試聴: https://shimomura055.github.io/eigo-radio/user_test/kp_advanced_explanation_audio_trial_03/index.html

1. `CURRENT_SPEC.md`: Key Phrase 節に小節「Advanced Key Phrase 英語解説(text 仕様)— Status: APPROVED_FOR_PRODUCTION(2026-09-28 ユーザー正式決定、配線未実施)」を追記: 仕様の要点(同一英語 Phrase+平易な英語解説、仕様文の出典=`KEY-PHRASE-LEVEL-SPEC-TRIAL-01` explanation_en 定義、15語目安、新規Fact追加なし、決定論チェック3種は Gate 候補[未確定])、`KEY_PHRASE_EXPLANATION_EN` 音声 Style はユーザー試聴待ち(TRIAL-03)、Production 配線は別管理ID。既存の「Advanced=英語句+日本語意味」の現行記述は **変更せず**、「現行 Production は日本語意味のまま」と併記。
2. `DECISION_LOG.md` 末尾に1エントリ `KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-03: text仕様のユーザー正式採用(APPROVED_FOR_PRODUCTION、未配線)+音声Style Before/After Trial記録(2026-09-28)`: (a)(b) を簡潔に。
3. `OPEN_ITEMS.md`: OPEN-221 本体行へ「2026-09-28追記: text 仕様はユーザー正式採用(APPROVED_FOR_PRODUCTION、配線未実施)。音声 Style は TRIAL-03 で Before/After を作成しユーザー試聴待ち。配線は別管理ID」を追記。新規 OPEN は作らない。
4. `docs/pm/REPORT_LEDGER.md`: TRIAL-02 行の Status を `APPROVED_FOR_PRODUCTION(text仕様、未配線)` へ更新、直後に TRIAL-03 新行(`USER_DECISION_REQUIRED`[Fable判定]、commit `484c233e`、Opus発火なし、REPORT名)。

## 実行コマンド全文

- `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-28_KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-03_02.md --json-out docs/pm/delegation_log/2026-09-28_KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-03_02.md_check.json`
- `git status --porcelain CURRENT_SPEC.md DECISION_LOG.md OPEN_ITEMS.md docs/pm/REPORT_LEDGER.md docs/pm/PM_GOVERNANCE.md`(2回)

## SSOT追記文

上記「反映内容」のとおり。

## Git

- add対象(path指定のみ、`git add -A` 禁止): `CURRENT_SPEC.md`、`DECISION_LOG.md`、`OPEN_ITEMS.md`、`docs/pm/REPORT_LEDGER.md`、delegation_log+`_check.json`。
- メッセージ: `KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-03: 英語解説text仕様のユーザー正式採用(APPROVED_FOR_PRODUCTION、未配線)+音声Style Trial記録をSSOTへ反映`、trailer `Management-ID: KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-03`。`git push origin main`。

## 報告(RESULT_PACKET_KA3S + handback、目安20行)

適用箇所/T-0結果1行/差分所有者確認2回/未実施の禁止操作/commit hash・push結果/raw URL(4ファイル)/注意点。
