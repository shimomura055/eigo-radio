# PM_GOVERNANCE — PM運用規則(正式SSOT)

**管理ID: PM-HANDOFF-CHATGPT-001-CLOSEOUT-SSOT-01**
**最終更新: 2026-09-05(PM-GOVERNANCE-TTS-MODE-CONFIRMATION-01でTTS方式明示・確認原則[7節]を追加)**

**このファイルはPM運用規則(Gate・Closeout Check等)の正式SSOTである。**
正式仕様(記事・音声・生成パイプラインそのものの仕様)は引き続き
`CURRENT_SPEC.md`が正本であり、このファイルはそれを置き換えない。
決定履歴は`DECISION_LOG.md`、未決事項は`OPEN_ITEMS.md`が正本のまま。

本ファイルはユーザー承認済みのPM運用原則4点
(PM-HANDOFF-CHATGPT-001-CLOSEOUT-SSOT-01、2026-09-05、
ChatGPT旧PMからの引き継ぎ照合PM-HANDOFF-CHATGPT-001の結果を受けてユーザーが
正式化を決定した)を記載する。`CLAUDE.md`・`docs/pm/PM_BRIEF.md`からは
本ファイルへの短い参照のみを行い、全文を重複させない。

---

## 1. 責任分担(Fable / Sonnet / Opus / ユーザー)

- **ユーザー**: 最終事業判断、仕様の正式採用(`APPROVED_FOR_PRODUCTION`)、
  Production採用、明示defer承認、commit/push承認を行う。
- **Fable(sandwich-pm)**: PM判断、タスク定義(目的・受入条件・STOP条件)、
  sonnet-workerへの委任、Gate 7による報告受入判定、UDR・上限到達時の
  STOPとユーザー報告を行う。自分で編集・実装・Git操作をしない。
  Production採用・`APPROVED_FOR_PRODUCTION`付与を代行しない。
- **sonnet-worker**: 調査・実装・テスト・SSOT更新・Git操作(Fable委任範囲内)・
  詳細報告を行う。Agentを起動しない。Production採用・Status格上げを
  独自判断しない。
- **opus-consultant**: 読み取り専用の診断(原因・選択肢・影響範囲)を行う。
  実装・編集・Git・Production採用判断をしない。診断後にSonnetを
  自動再実行しない。
- ループ上限(Sonnet合計2回・差し戻し1回・Opus1回)は`CLAUDE.md`が正本であり、
  ここでは参照のみ行う。

## 2. PM Gate 1〜7

- **Gate 1 — Trial Closeout**: Trial終了時に`REJECTED` / `VALIDATED` /
  `USER_DECISION_REQUIRED`のいずれかへ分類する。`VALIDATED`はProduction採用
  ではない。`USER_DECISION_REQUIRED`ならユーザー判断または明示deferまでSTOPする。
- **Gate 2 — User Decision**: `VALIDATED`→`APPROVED_FOR_PRODUCTION`は
  ユーザー正式採用時のみ行う。Fable/Sonnet/Opusが独自判断で承認しない。
- **Gate 3 — Production Wiring Checklist**: `APPROVED_FOR_PRODUCTION`後、
  以下すべてが完了するまで`PRODUCTION_WIRED`としない: Production正式初回経路 /
  retry・fallback・regenerationとの整合 / DEV・Trial-onlyではないこと /
  Production runtimeでの実発火 / 必要testのPASS / runtime evidence /
  実際のmodel_id・routing確認(必要時) / `CURRENT_SPEC.md` /
  `DECISION_LOG.md` / `OPEN_ITEMS.md` / 必要なGit反映 /
  approved specとProduction挙動の一致。
- **Gate 4 — Dangling Reference Check**: Production code / Prompt / retry等が
  未承認・未実装・Trial-only仕様を参照していないかを確認する。
  **定義の正本は`CURRENT_SPEC.md`の既存「Dangling Reference Check」
  (ER-010-N1-SPEC-LIFECYCLE-PRODUCTION-GATE-04、2026-08-31導入)であり、
  本ファイルはそれを参照するのみで全文を再掲しない。**
- **Gate 5 — Open Item Review**: closeout時に、未処理の
  `USER_DECISION_REQUIRED` / 未採否の`VALIDATED` / 未配線の`APPROVED_FOR_PRODUCTION` /
  未報告Trial / Open Item漏れの有無を確認する。
- **Gate 6 — 次工程前PM確認**: 次の実装・Trial・Production作業に着手する前に、
  未処理UDR / APPROVED未配線 / SSOT漏れ / 無断追加Trial /
  DEV・Trial誤認が無いかを確認する。
- **Gate 7 — 実務報告の受入判定**: Sonnet/Opus等の「完了」「Production反映済み」
  「動作確認済み」という報告をそのまま採用せず、Production正式path /
  runtime evidence / test / approved specとの一致 / retry・fallbackとの整合 /
  QCD(品質・コスト・納期)副作用をFableが受入判定する。

## 3. PM Closeout Mandatory Check(PM Closeout時の確認事項)

主要タスクをcloseする前に、最低限以下を確認する。1件でも未処理なら
無条件に「完了」としない。

1. Trial statusが分類済みであること
2. UDRが提示済みであること
3. 正式採用項目が追跡済みであること
4. `APPROVED_FOR_PRODUCTION`→`PRODUCTION_WIRED`の完了確認
5. initial/retry/fallbackの整合確認
6. runtime evidenceの取得
7. `CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`との整合
8. 未報告Trialが無いこと
9. 無断deferが無いこと
10. 次タスクへの持ち越し事項が明示されていること

## 4. 「1記事ずつ完結させる」原則と例外

正式採用された仕様は、対象記事のProduction正式経路へ配線し、必要な
test/runtime/SSOT/Gitまで完了するまで次の記事へ進めないことを原則とする。
Trial-only条件を最終候補記事に使った場合、記事close前に正式採否と
Production配線状態を必ず整理する。

**例外(2026-09-05ユーザー訂正で明記)**: 未配線・未採否の論点について、
次の5条件を**すべて**満たす場合に限り、その論点の解消を待たずに次の記事・
次工程へ進めてよい。

1. ユーザーが明示的にdeferを承認したこと
2. non-blockingであること(記事のProduction正式経路・完成には影響しない)を
   確認したこと
3. `OPEN_ITEMS.md`でStatusと未完了内容を追跡していること
4. `APPROVED_FOR_PRODUCTION`の取消しではないこと
5. 後続作業が未配線項目を誤って完了扱いしないこと

したがって、OPEN-83のように明示deferされた項目は、適切に追跡されていれば
プロジェクト全体を停止させない。Fable/Sonnet/Opusが自ら「non-blockingだから
進めてよい」と判断して適用してはならない。

## 5. deferの成立条件

- deferはユーザーの明示承認によってのみ成立する。Fable/Sonnet/Opusは
  「defer候補」を提示できるが、deferを決定できない。
- 成立したdeferは`OPEN_ITEMS.md`該当行および`DECISION_LOG.md`に
  「ユーザーが明示deferした」ことが分かる形で記録する(記録が無いdeferは
  無断deferとみなし、Closeout Check項目9に抵触する)。
- deferは`APPROVED_FOR_PRODUCTION`の取消しではない。APPROVED済み・未配線の
  項目をdeferした場合、APPROVED未配線項目としてGate 5/6で追跡を継続する。
- deferされた項目は、次工程がその項目の完了を前提にしてはならない
  (Gate 6で確認する)。
- 「今後個別判断する」と指定された項目はdeferではなく未決
  (`USER_DECISION_REQUIRED`維持)として区別する。

## 6. 「安全になっただけでは成功としない」原則

Fact Safetyやoverclaim修正で安全になっても、記事の面白さ・分かりやすさ・
Storytelling・Entertainment性・ユーザー価値が明確に劣化していないかを
確認する。「安全になったから成功」と自動判定しない。

## 7. TTS方式(Batch API / Standard同期)の明示・確認原則

- TTS生成を含むタスク定義(`docs/pm/ACTIVE_TASK.md`・Fableからsonnet-workerへの
  委任文)には、使用するTTS方式(Batch API / Standard同期)を必ず明記する。
  Production標準はBatch API(正本は`CURRENT_SPEC.md`「Gemini TTS実装方式
  (Batch API)」であり、本ファイルへは全文を複製しない)。
- タスク定義にTTS方式の明記がない場合、Fableは着手前に必ずユーザーへ確認する。
  Sonnet/Opusは方式が不明なまま生成に着手せず、STOPしてFable経由でユーザーへ
  確認を求める。
- 方式の切り替え(Batch→Standard等)や1エピソード内での方式混在は、ユーザーの
  明示承認がある場合に限り行い、Production忠実性への影響(Production経路と
  異なる条件で得た結果である旨)・所要時間・コスト差を必ずReportへ記録する。
  Production call site自体の変更はこの原則の対象外(別途Gate 3の対象)。
- タスク着手前に、選択したTTS方式に応じたおおよその所要時間・コストの見込みを
  ユーザーへ提示する。
- 経緯: 2026-09-05、Trial-13(OPEN-112-TREND-THEME2-B-A2-B1-FULL-AUDIO-TRIAL-13)
  でタスク定義にTTS方式が明記されず、所要時間の見込み共有が漏れたことを受けた
  ユーザー指示により新設。

---

## 変更履歴

- 2026-09-05(PM-HANDOFF-CHATGPT-001-CLOSEOUT-SSOT-01): 新設。PM Gate 1〜7・
  PM Closeout Mandatory Check・1記事ずつ完結(例外含む)・安全≠成功を
  ユーザー承認のうえ正式化。ChatGPT旧PM引き継ぎ資料(PM-HANDOFF-CHATGPT-001)の
  照合結果(`docs/pm/PM-HANDOFF-CHATGPT-001_REPORT.md`)がCHATGPT_ONLY_CANDIDATEと
  分類していた4項目(Gate体系・Closeout Check名称・1記事完結原則・安全≠成功原則)を
  正式に採用したもの。
- 2026-09-05(PM-HANDOFF-CHATGPT-001-CLOSEOUT-SSOT-01、Fable差し戻しによる
  Sonnet修正): ユーザー訂正指示に基づき見出し構成を再編(1.責任分担/2.PM Gate/
  3.PM Closeout Mandatory Check/4.1記事ずつ完結/5.deferの成立条件/
  6.安全≠成功)。新設項目として「1. 責任分担(Fable/Sonnet/Opus/ユーザー)」・
  「5. deferの成立条件」を追加し、「4. 1記事ずつ完結」の例外条件を3件から
  ユーザー指定の5件へ修正(既存3件に「`APPROVED_FOR_PRODUCTION`の取消しでは
  ないこと」「後続作業が未配線項目を誤って完了扱いしないこと」を追加)。
  既存A〜D節(現2〜3・4・6節)の内容自体は変更していない。
- 2026-09-05(PM-GOVERNANCE-TTS-MODE-CONFIRMATION-01): 「7. TTS方式
  (Batch API / Standard同期)の明示・確認原則」を新設。Trial-13
  (OPEN-112-TREND-THEME2-B-A2-B1-FULL-AUDIO-TRIAL-13)でTTS方式未明記により
  所要時間の見込み共有が漏れたことを受けたユーザー指示により、タスク定義への
  方式明記・未明記時のユーザー確認・混在時の記録・着手前の見込み提示を
  正式化した(文書編集のみ、コード・Prompt変更なし)。
