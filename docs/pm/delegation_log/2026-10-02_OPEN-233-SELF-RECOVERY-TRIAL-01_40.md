## 管理ID

`OPEN-233-SELF-RECOVERY-TRIAL-01`(委任_40: **記録の保存とcommitのみ**。Opus独立レビュー結果の逐語保存、委任_39の設計書のcommit、記録欄の更新。¥0。実装・Trial・設計変更なし)。並行タスクなし。

## 性質/到達上限Status/禁止事項

- 性質: 記録保存(ドキュメントのみ)。Opus独立技術レビューGate(PM_GOVERNANCE 11-3)の該当判定: 非該当(ドキュメント更新)。保存対象のレビュー自体は条件A・B+ユーザー明示指示によるもの。
- 到達上限Status: `USER_DECISION_REQUIRED`のまま(変更しない)。
- 費用: ¥0(API・TTS・Trial・Opus起動なし。T-3非該当)。
- 禁止事項:
  - 実装しない・Trialを回さない・Production正式pathを変更しない。`*.py`・Prompt・テストに触れない。
  - Opusレビュー本文を一字も変えない(冒頭ヘッダと末尾のFable評価のみ指定文言で付ける)。
  - 委任_39の設計書`docs/pm/design_open233_violation_span_handoff_01.md`は編集せずそのままcommit。`design_open233_self_recovery_flow_01.md`・`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`・`CURRENT_SPEC.md`・`DECISION_LOG.md`・`PM_GOVERNANCE.md`は編集しない。
  - `OPEN_ITEMS.md`はOPEN-233行の次Actionセル末尾への追記のみ。
  - `git add -A`/`stash`/`amend`/force push禁止。既存の未commit変更(`er0XX_output/`配下)・無関係の未追跡ファイルには触れない・addしない。

## 固定ブロック

E-1/D-1/G-1/F-1/T-0/T-2適用(本委任はTTSを伴わない。T-1・T-3は非該当)。T-0の保存先は本ファイル。

## ユーザー指示(原文、抜粋、2026-10-02)

Claudeが設計案を作ったら実装前にOpusへ独立レビューさせる/Opusの意見をそのまま採用せずFableが一致点・相違点・最終推奨案・採用理由・残るリスクを整理/今回は設計再検討+Opusレビュー+最終推奨案の提示まで。実装・Trialは行わない。StatusはUSER_DECISION_REQUIRED。Production正式path変更禁止。OPEN-233は設計+Opusレビュー結果が出た時点で一度ユーザーへ報告し、実装・Trialへ進まない。

## 事前指定Read一覧

(下記に事前指定Read・Grepを併記)

## 事前指定Grep一覧+追記位置・更新位置の手順

- Read: `opus_l2_review_open233_self_recovery_04.md`1〜12行、`REPORT_LEDGER.md`表ヘッダ・末尾、`OPEN_ITEMS.md`のOPEN-233次Actionセル末尾、`ACTIVE_TASK.md`1〜25行。
- Grep: `git status --porcelain=v1`で委任_39の未追跡ファイル確認、`git ls-files docs/pm/delegation_log | grep -c "_check.json"`。
- 追記・更新: (1)新規`docs/pm/opus_l2_review_open233_self_recovery_05.md`、(2)`REPORT_LEDGER.md`表末尾へ1行(管理ID=`OPEN-233-SELF-RECOVERY-TRIAL-01(委任_38〜40: 受け渡し再設計+Opus独立レビュー)`、初回正式報告=済、ユーザーFeedback=未、累積再掲=Y、Opus発火=L2)、(3)`OPEN_ITEMS.md` OPEN-233行の次Actionセル末尾へ2026-10-02追記(設計案とOpusレビュー完了、ユーザー判断待ち4点、実装・Trial未着手)、(4)`ACTIVE_TASK.md`・`RESULT_PACKET.md`を上書き(addしない)。

## 保存する本文

`docs/pm/opus_l2_review_open233_self_recovery_05.md`に逐語保存(冒頭ヘッダ+Opus返答逐語+末尾Fable PM評価の3部構成。本文はここでは省略)。

## 実行コマンド全文

1. `git status --porcelain=v1 | grep -v '^??'`
2. Read/Grep→ファイル作成・追記
3. 逐語確認(先頭行・末尾行が各1回、目印行`<<<OPUS_REVIEW_BEGIN`/`OPUS_REVIEW_END>>>`が含まれない、見出し9つが存在)を`grep -c`で確認
4. T-0: `python docs/pm/tools/check_delegation_prompt.py --file <本ファイル> --json-out <本ファイル>_check.json`
5. `git diff --stat`、`git diff -- OPEN_ITEMS.md | grep -c '^-[^-]'`
6. Git

## Git

- SSOT編集権: あり(`OPEN_ITEMS.md`[OPEN-233行追記のみ]・`docs/pm/REPORT_LEDGER.md`)。`DECISION_LOG.md`へは追記しない。
- 明示add対象(1ファイルずつ): 設計書、opus_l2_review_..._05.md、委任_39 `.md`/`_result.md`、委任_40 `.md`、`_check.json`(従来追跡のため`_39.md_check.json`・`_40.md_check.json`)、`OPEN_ITEMS.md`、`REPORT_LEDGER.md`。
- コミットメッセージ: `OPEN-233-SELF-RECOVERY-TRIAL-01: 受け渡し再設計の設計案(委任_39)とOpus独立レビュー#5を保存、未実装・未Trial・USER_DECISION_REQUIRED据え置き(委任_40)`
- trailer: 94106529形式(Management-ID+Co-Authored-By)。commit後`git push origin main`。エラー・競合はSTOP。

## 報告

(1)作成・変更ファイル一覧、(2)逐語確認結果、(3)REPORT_LEDGER・OPEN_ITEMSの追記箇所、(4)T-0結果1行、(5)commitハッシュ・push結果・`git show --stat HEAD`、(6)raw.githubusercontent.com URL、(7)指示どおりにできなかった点。
