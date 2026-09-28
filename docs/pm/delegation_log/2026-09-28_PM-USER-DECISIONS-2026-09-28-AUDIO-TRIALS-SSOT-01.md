## 管理ID

PM-USER-DECISIONS-2026-09-28-AUDIO-TRIALS-SSOT-01(SSOT反映のみ)。一時ファイル `docs/pm/RESULT_PACKET_UD1.md`(commitしない)。並行: 別Sonnet 4件(Task 1 `er045_*`、Task 2 `er046_*`、Task 3 `er047_*`、Task 4 設計書。いずれも SSOT 編集権なし)→ 触れない。**削除・移動・`rm`・`git clean`・stash/rebase/reset/amend/force push 禁止**。自タスクの所有ファイル(SSOT 4点+REPORT_LEDGER+delegation_log)以外に触れない。未追跡ファイルは他Agent/ユーザーの作業物として扱う。push競合時は `git merge origin/main` のみ、conflictは中断報告。

## 性質/到達上限Status/禁止事項

- 性質: ユーザー正式決定(2026-09-28)の記録。コード・Prompt・PM_GOVERNANCE は変更しない。API支出なし(上限¥0)。
- **SSOT編集権: あり**(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/`docs/pm/REPORT_LEDGER.md`。`docs/pm/PM_GOVERNANCE.md` 無変更)。現在SSOT編集権を持つAgentは本タスクのみ。差分所有者確認: 開始時と commit 直前に `git status --porcelain CURRENT_SPEC.md DECISION_LOG.md OPEN_ITEMS.md docs/pm/REPORT_LEDGER.md docs/pm/PM_GOVERNANCE.md` を実行し本タスク以外の差分ゼロを記録(他Agent差分があれば add せずSTOP)。
- 禁止: `PRODUCTION_WIRED` と書かない(すべて未配線)。ユーザー決定にない判断をしない。APIキー本文表示禁止。ユーザー向け表記は Standard/Advanced。DECISION_LOG.md は CRLF(Edit 失敗時は Python で CRLF 明示追記)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)

E-1/D-1/G-1/F-1 標準(SSOT 全文Read禁止)。
T-0: 本委任文を `docs/pm/delegation_log/2026-09-28_PM-USER-DECISIONS-2026-09-28-AUDIO-TRIALS-SSOT-01.md` へ逐語保存し、`.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-28_PM-USER-DECISIONS-2026-09-28-AUDIO-TRIALS-SSOT-01.md --json-out docs/pm/delegation_log/2026-09-28_PM-USER-DECISIONS-2026-09-28-AUDIO-TRIALS-SSOT-01_check.json` を実行し結果1行記録。
T-2: TTSなし。T-3: API支出なし。

## 事前指定Read一覧

- `user_test/fixed_shell_champion_trial_02/index.html`(全文、read-only。表の列順から 左/中/右 → A/B/C の対応を確定する)
- `er043_output/tts_fixed_shell_master_champion_trial_02/champion_trial_results.json`(Grep `style_prefix_used|model|voice` → 採用候補の実 style・model・voice)
- `TTS-VARIABLE-SPOKEN-ROLE-STYLE-TRIAL-02_REPORT.md` §4(J3/E2 逐語)
- `docs/pm/design_tts_variable_spoken_role_style_trial_02.md` §4-4(TOPIC_INTRO E2 逐語)

## 事前指定Grep一覧+追記位置・更新位置の手順

- `docs/pm/REPORT_LEDGER.md`: Grep `AUDIO-STYLE-TRIAL-03|MASTER-CHAMPION-TRIAL-02|VARIABLE-SPOKEN-ROLE-STYLE-TRIAL-02|AN3-T0-PRODUCTION-WIRING-01` → 各行の Status 更新。
- `DECISION_LOG.md`: Grep `TTS-VARIABLE-SPOKEN-ROLE-STYLE-TRIAL-02: Trial記録` → 末尾に新エントリ。
- `OPEN_ITEMS.md`: Grep `OPEN-221|OPEN-222|OPEN-228|OPEN-229` → 本体行追記。
- `CURRENT_SPEC.md`: Grep `Role Style|6-role|固定|shared narration|Key Phrase` → 該当節末尾に「APPROVED_FOR_PRODUCTION(未配線)」小節を追記。

## 反映内容(ユーザー正式決定、2026-09-28。Fable 転記)

(A) **KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-03**: 「clear, precise, unhurried」は遅すぎたため **不採用**。「clear, precise, explanatory」との中間を TRIAL-04 で探索(進行中)。REPORT_LEDGER の TRIAL-03 行 Status を `REJECTED(unhurried は遅すぎる、ユーザー判断。中間案は TRIAL-04)` へ更新。text 仕様の `APPROVED_FOR_PRODUCTION`(未配線)は変わらず。
(B) **TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-02 の Champion(ユーザー決定)**: 試聴ページの列位置で welcome=左、preview_intro=右、key_phrases_intro=右、full_story_intro=右、num_one=右、num_two=中、num_four=右、point_explanation=中。**index.html の列順から 左/中/右 を A/B/C に確定し(例: 左=A[現行 Production Master]、中=B、右=C)、phrase ごとに candidate ID・実 style 全文・model・voice を対応表として記録**。列順が曖昧なら「要ユーザー確認」と明記して記録(推測で確定しない)。num_three/num_five は `TTS-FIXED-SHELL-NUMBER-THREE-FIVE-RETRIAL-01` で再Trial(進行中、モデル・voice・基本 Style 思想は採用品と同一条件)。Status: 8 phrase の Champion=`APPROVED_FOR_PRODUCTION`(Master 登録・配線は未実施、別管理ID)。welcome=左が A(現行 Master)なら「現行 Master 継続」と記録。
(C) **TTS-VARIABLE-SPOKEN-ROLE-STYLE-TRIAL-02**: 日本語=**J3**、英語=**E2**(FULL_STORY/IN_ONE_LINE/TOPIC_INTRO)を `APPROVED_FOR_PRODUCTION`(未配線)。配線は `TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01`(Phase A 設計中)。固定 Master phrase には適用しない。J3/E2 の文言は逐語で CURRENT_SPEC に記載(REPORT §4/設計書 §4-4 から転記)。
(D) **FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01 / OPEN-228 の扱い**: AN3-T0 は採用済み(実装済み、`APPROVED_FOR_PRODUCTION`、Gate 3 保留)。**OPEN-228 を単独で先行修正しない**。順序=1. `FAMILY-X-TRANSLATION-SEGMENTATION-NO-HEADING-TRIAL-01`(見出し廃止+3分割 Trial、進行中)→ 2. ユーザー採用判断 → 3. 採用なら新構造に合わせて split/Gate/retry 整理 → 4. AN3-T0 の Production Wiring 完了(`PRODUCTION_WIRED`)。OPEN-228 本体行と DECISION_LOG に記録。REPORT_LEDGER の Wiring-01 行備考に「Gate 3 保留(OPEN-228、順序はユーザー決定)」を追記。

1. `docs/pm/REPORT_LEDGER.md`: (A)(B)(C)(D) の各行 Status/備考を更新。新行は作らない(進行中 Trial の行は各 Trial の SSOT 反映で追加)。
2. `DECISION_LOG.md` 末尾に1エントリ `PM-USER-DECISIONS-2026-09-28-AUDIO-TRIALS-SSOT-01: ユーザー正式決定4件(2026-09-28)`: (A)〜(D) を簡潔に、(B) は対応表を含める。
3. `OPEN_ITEMS.md`: OPEN-221 追記(unhurried 不採用、TRIAL-04 へ)、OPEN-222 追記(One/Two/Four の Champion 確定、Three/Five は RETRIAL-01)、OPEN-228 追記((D) の順序)、OPEN-229 追記(J3 採用、WIRING-01 で最小導入予定)。新規 OPEN は作らない。
4. `CURRENT_SPEC.md`: (i) Role Style 関連節の末尾に小節「可変 segment Role Style(J3/E2)— Status: APPROVED_FOR_PRODUCTION(2026-09-28 ユーザー正式決定、配線未実施)」(J3/E2 逐語、適用範囲、固定 phrase 除外、現行 Production は従来どおりと併記)。(ii) 固定 phrase/shared narration 関連節の末尾に小節「固定フレーズ Champion — Status: APPROVED_FOR_PRODUCTION(未配線)」(対応表の要点: phrase → candidate → style 全文 → model/voice、num_three/num_five は再Trial 中)。既存記述は変更しない。

## 実行コマンド全文

- `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-28_PM-USER-DECISIONS-2026-09-28-AUDIO-TRIALS-SSOT-01.md --json-out docs/pm/delegation_log/2026-09-28_PM-USER-DECISIONS-2026-09-28-AUDIO-TRIALS-SSOT-01_check.json`
- `git status --porcelain CURRENT_SPEC.md DECISION_LOG.md OPEN_ITEMS.md docs/pm/REPORT_LEDGER.md docs/pm/PM_GOVERNANCE.md`(2回)

## SSOT追記文

上記「反映内容」のとおり。

## Git

- add対象(path指定のみ、`git add -A` 禁止): SSOT 4点、delegation_log+`_check.json`。
- メッセージ: `PM-USER-DECISIONS-2026-09-28-AUDIO-TRIALS-SSOT-01: ユーザー正式決定4件(unhurried不採用/固定フレーズChampion/J3・E2採用/OPEN-228の順序)をSSOTへ反映(全て未配線)`、trailer `Management-ID: PM-USER-DECISIONS-2026-09-28-AUDIO-TRIALS-SSOT-01`。`git push origin main`。

## 報告(RESULT_PACKET_UD1 + handback、目安25行)

冒頭: 左/中/右 → A/B/C の確定結果と根拠(列順)、対応表。以降: 適用箇所/T-0結果/差分所有者確認2回/未実施の禁止操作/commit hash・push結果/raw URL(4ファイル)/注意点(曖昧箇所があれば「要ユーザー確認」として列挙)。
