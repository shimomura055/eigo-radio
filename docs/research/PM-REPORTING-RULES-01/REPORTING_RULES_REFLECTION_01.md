# PM-REPORTING-RULES-01 報告・表示運用ルール反映記録(2026-10-28、API 0)

原文: `docs/pm/delegation_log/2026-10-28_FZ-TELL-TALE-HEART-NARRATOR-VOICE-01_USER_02.md` §2・§3。正本=`docs/pm/PM_GOVERNANCE.md` 12-14(新設)。

## 反映先
- PM_GOVERNANCE 12-14(新設・決定①〜⑤逐語趣旨+最終報告形式+worker最終応答はFable向け)
- CLAUDE.md compact復帰手順(8)直後へ1行 / sandwich-pm.md・sonnet-worker.md末尾へ追記 / ACTIVE_TASK報告運用欄(既存行7で記載済み、変更なし)
- SSOT: DECISION_LOG末尾、USER_DECISION_REGISTER_01、OPEN-571

## 矛盾整理(既存行は書き換えず、見出し直後に「→2026-10-28以降は12-14が優先」を挿入)
| 旧記載 | 旧内容 | 整理 |
|---|---|---|
| 9-8-1 | 先行・途中報告にもマーカー | 途中報告自体を行わない。ユーザーへ出す報告のマーカーは不変 |
| 12-2 | 報告可能になれば即時報告(Trial終了・artifact完成等) | 即時は12-14④の例外事由に限定。通常はタスク完了報告1件 |
| 12-3 | 未回答の他報告を次報告時に再掲 | 廃止。当該タスク完了報告の「必要なユーザー判断」欄に限定 |
| 12-4/12-4-1/12-11 | フルレポート累積再掲 | 廃止(簡潔形式)。分割worker報告を未統合で出さない点は維持 |
| 12-5 | closeごとのNext Action/Reminder | 完了報告の判断欄の範囲に限定。12-6(勝手な仕様決定禁止)不変 |
| 12-9 | 他作業完了待ち報告保留禁止 | 12-14③(別タスク待ちまとめ禁止)と整合。例外の即時報告義務不変 |
| 12-12 | 累積再掲・REPORT_LEDGER | 累積再掲廃止、「REPORT存在≠報告済み」は維持 |
| 9節候補6(未回答再掲)・7(Next Action)・3節項目15〜18 | 注記なし(12-14が優先と12-14本文に明記) | 同上 |
弱めていないもの: 11節STOP条件・7-9予算・26節STOP・27-3判断候補・9-8マーカー・Fable受入・SSOT/Git/Gate(12-14④⑤に統合)。

## Claude Code表示抑制の確認(ローカル確認のみ、公式docsはWeb取得せず)
- `~/.claude/settings.json`: permissions.defaultMode/model/autoUpdatesChannel/themeのみ。表示抑制系の設定なし。`.claude/settings.local.json`: permissions.allowのみ。
- `claude --help`: ツール呼出表示を隠すオプションは確認できず。`-p/--print`(非対話)は最終応答のみ出力するが、対話セッション(`claude --agent sandwich-pm`)の運用を変えるため採用提案はしない。
- 結論: 対話TUIが自動表示するツール呼出(`Write(...)`等)はClaude Code実行環境の仕様で、Claude側(モデル出力)からは抑制不可。設定変更の提案: なし(該当設定を確認できないため)。Claude側が制御できる範囲(委任文・Worker経過・テストログ・進捗文をメッセージ本文へ出さない)は12-14で規定済み。Ctrl+O等の表示切替はユーザー側UI操作。※公式docsの最新設定は未参照のため、将来設定が追加された場合は再確認。
