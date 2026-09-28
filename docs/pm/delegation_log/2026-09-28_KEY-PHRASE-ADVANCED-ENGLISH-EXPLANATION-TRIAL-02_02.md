## 管理ID

KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-TRIAL-02(SSOT反映のみ、委任 _02)。一時ファイル `docs/pm/ACTIVE_TASK_KE2S.md` / `docs/pm/RESULT_PACKET_KE2S.md`(commitしない)。並行: 別Sonnet 2件(Task C `er040_*`/`user_test/fixed_shell_champion_trial_01/`、Task B追補 `er038_output/`/`user_test/tts_all_role_style_trial_01/`)→ これらのファイルに触れない。**削除・移動・`rm`・`git clean`・stash/rebase/reset/amend/force push 禁止**。自タスクの所有ファイル以外に触れない。未追跡ファイルは他Agent/ユーザーの作業物として扱う。push競合時は `git merge origin/main` のみ、conflictは中断して報告。

## 性質/到達上限Status/禁止事項

- 性質: SSOT反映(記録のみ)。コード・Prompt・CURRENT_SPEC・PM_GOVERNANCE は変更しない。API支出なし(上限¥0、API呼び出しが必要になったらSTOP)。
- **SSOT編集権: あり**(`docs/pm/REPORT_LEDGER.md` / `DECISION_LOG.md` / `OPEN_ITEMS.md` の3点のみ。`CURRENT_SPEC.md`・`docs/pm/PM_GOVERNANCE.md` は無変更)。本セッションで現在SSOT編集権を持つAgentは本タスクのみ。
- 禁止: Trial結果を `VALIDATED`/`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED` と書かない(Status は `USER_DECISION_REQUIRED`[Fable判定])。ユーザー判断事項を決めない。新仕様を書かない。APIキー本文の表示・log・commit禁止。ユーザー向け表記は学習レベル=Standard/Advanced(A2/B1/B1Bは内部表記としてのみ併記可)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない。
D-1: Grep→該当行範囲Readを基本とし、SSOT 3点の全文Readは禁止(追記位置の特定に必要な範囲のみ)。
G-1: git出力は `--porcelain`/`--stat`/`--short` で最小化。
F-1: transcript退避不要。
T-0: 受領した本委任文を `docs/pm/delegation_log/2026-09-28_KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-TRIAL-02_02.md` へ逐語保存し、`.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-28_KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-TRIAL-02_02.md --json-out docs/pm/delegation_log/2026-09-28_KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-TRIAL-02_02.md_check.json` を実行し結果1行記録(FAILでも内容改変してPASSさせない)。
T-2: TTSなし。
T-3: API支出なし。

## 反映内容(事実は `KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-TRIAL-02_REPORT.md` と `docs/pm/RESULT_PACKET_KE2.md` 末尾のSSOT文案を根拠にする。文案は参考であり、下記Fable指定を優先)

事実(Fable確認済み): commit `3d86edd9`(push済み)。Hormuz既存Advanced Key Phrase 5件(give back / sea blockade / stand at center stage / take a sharp turn / recover the cost、再選定なし、A/BでPhrase完全同一を機械検証)。A=現行(英語句+日本語意味)、B=同一英語句+平易な英語解説(前回 `KEY-PHRASE-LEVEL-SPEC-TRIAL-01` の explanation_en 仕様文を逐語再利用、語数上限15語は前回実測値踏襲)。決定論指標: 5/5 語数上限内、新規Fact混入0件、wordfreq zipf で「phraseより難しい語」が3/5件に1〜3語(give back: lose/earlier/gain、stand at center stage: focus)。LLM rubric 7観点 平均4.71〜5.00。音声: A側は既存Hormuz音声をコピー再利用(新規生成なし)、B側の英語解説のみ5 segment を Flash-Lite で新規生成(Task B `er038` の `KEY_PHRASE_EXPLANATION_EN` style と Trial専用Store をimport流用、`TTS_EXECUTION_MODE=STANDARD`、Production Master Store 無変更)。費用 合計¥0.90(text ¥0.30 + audio ¥0.60、上限¥20)。Regression 13/13 PASS。Production code/正式Prompt/CURRENT_SPEC/Key Phrase選定ロジック 無変更。Opus発火なし。Fable判定 `USER_DECISION_REQUIRED`。ユーザー判断待ち3点: (1) Bの方向で仕様検証を継続するか (2) 音声(発音・自然さ)の試聴結果 (3) MAX_WORDS=15・新規Fact検出ロジックを今後の参考値として引き継ぐか。確認ページ: https://shimomura055.github.io/eigo-radio/user_test/kp_advanced_explanation_trial_02/index.html

1. `docs/pm/REPORT_LEDGER.md`: 既存行の書式(Grep `TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01` で直近Trial行の書式を確認)に合わせ、Trial-02 の新行を追加(Status `USER_DECISION_REQUIRED`[Fable判定]、commit `3d86edd9`、Opus発火なし、REPORT名)。
2. `DECISION_LOG.md` 末尾に1エントリ `KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-TRIAL-02: Trial記録(2026-09-28)`: 上記事実を簡潔に(目的=前回REJECT主因のPhrase選定Prompt v1を除外し解説言語のみisolated比較、結果、費用、Production無変更、ユーザー判断待ち3点)。「`KEY_PHRASE_EXPLANATION_EN` は引き続きProduction未実装」「Production採用はユーザーのみが判断」を明記。新規Fact検出ヒューリスティック(大文字語頭語+数字)の限界は本エントリ内に1行で記録(新規OPENは作らない)。
3. `OPEN_ITEMS.md`: OPEN-221 の本体行に追記(Trial-02で解説テキスト候補5件+B側音声を作成、決定論指標5/5 OK・rubric 4.7以上、Production未実装のままユーザー判断待ち、REPORT参照)。新規OPENは作らない。

## 差分所有者確認(必須)

開始時と commit 直前の2回、`git status --porcelain CURRENT_SPEC.md DECISION_LOG.md OPEN_ITEMS.md docs/pm/REPORT_LEDGER.md docs/pm/PM_GOVERNANCE.md` を実行し、本タスク以外の差分がゼロであることを確認して記録する。他Agentの差分があれば `git add` せずSTOPして報告。他並行タスクの未commit差分(er006/er011/er012/er021/er030/er038/er040系、他delegation_log未追跡ファイル群)には触れない。

## Git

- add対象(path指定のみ、`git add -A` 禁止): `docs/pm/REPORT_LEDGER.md`、`DECISION_LOG.md`、`OPEN_ITEMS.md`、`docs/pm/delegation_log/2026-09-28_KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-TRIAL-02_02.md`、同 `_check.json`。SSOT編集権: あり(上記3点)。
- メッセージ: `KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-TRIAL-02: Trial記録をSSOTへ反映(USER_DECISION_REQUIRED、OPEN-221追記)`、trailer `Management-ID: KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-TRIAL-02`。`git push origin main`。

## 報告(RESULT_PACKET_KE2S + handback、目安20行)

適用箇所(ファイル・行付近・要旨)/T-0結果1行/差分所有者確認2回の結果/未実施の禁止操作の明示/commit hash・push結果/raw URL(3 SSOTファイル)/注意点(ユーザー未回答論点は未解決のまま)。
