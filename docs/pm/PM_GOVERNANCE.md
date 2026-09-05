# PM_GOVERNANCE — PM運用規則(正式SSOT)

**管理ID: PM-HANDOFF-CHATGPT-001-CLOSEOUT-SSOT-01**
**最終更新: 2026-09-06(PM-GOVERNANCE-REPORT-FORMAT-AND-AUTONOMOUS-GIT-05で
ユーザー向け報告フォーマットを番号対応する5構造[現在の状態/未解決問題/
次にやること/ユーザー判断/補足・技術詳細]へ改訂し[9節]、通常の安全な
commit/pushをClaude側が自律実行する運用[10節]を新設、1節の責任分担を
整合)。2026-09-06(PM-GOVERNANCE-AGENT-WAIT-AND-DUPLICATE-LAUNCH-RULE-04で
待機中Agentの再開リスク・同一管理IDへの多重起動禁止・前面同期待機原則を
Agent並列起動の原則[8節]へ追記)。2026-09-05(PM-GOVERNANCE-USER-FACING-EXPLANATION-STYLE-03でユーザー向け
説明スタイルの原則[9節]を追加。PM-GOVERNANCE-PARALLEL-AGENT-POLICY-02でAgent並列起動の原則[8節]を追加。
PM-GOVERNANCE-TTS-MODE-CONFIRMATION-01でTTS方式明示・確認原則[7節]を追加)**

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
  Production採用、明示defer承認、破壊的操作・Production採用判断を含む
  commit/push等、10節が定める例外時のcommit/push判断を行う。
- **Fable(sandwich-pm)**: PM判断、タスク定義(目的・受入条件・STOP条件)、
  sonnet-workerへの委任、Gate 7による報告受入判定、UDR・上限到達時の
  STOPとユーザー報告を行う。自分で編集・実装・Git操作をしない。
  Production採用・`APPROVED_FOR_PRODUCTION`付与を代行しない。10節が定める
  通常の安全なcommit/pushはsonnet-workerへ委任して自律実行させ、例外条件に
  該当する場合のみユーザー判断を仰ぐ。
- **sonnet-worker**: 調査・実装・テスト・SSOT更新・Git操作(Fable委任範囲内。
  10節が定める通常の安全なcommit/pushは自律実行する)・詳細報告を行う。
  Agentを起動しない。Production採用・Status格上げを独自判断しない。
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

## 8. Agent並列起動の原則

- 原則は1タスクずつ進める。ただし、対象ファイル・出力先(`er0XX_output/`配下の
  ディレクトリ、Report、script、SSOT)が重ならず、相互依存のない独立タスクで
  あれば、Fableの判断で複数sonnet-workerを並列起動してよい。
- 並列時の必須条件:
  1. `docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md`は同時に1タスクだけが
     使用する。他の並列タスクはこの2ファイルへ触れず、最終メッセージで
     報告する(またはFableが委任文で明示的に割り当てる)。
  2. Git操作を含むタスクは、並列タスクの生成物をstageしない
     (ファイル名指定の`git add`のみ、`-A`禁止)。
  3. 同一の管理ID・同一の出力先に対する並列起動は禁止する。
  4. 各タスクのループ上限(Sonnet合計2回等)は管理IDごとに独立して数える。
- Agent Teamsは引き続き不使用。opus-consultantの並列起動は行わない
  (診断は1回限り)。
- 経緯: 2026-09-05、Trial-13(OPEN-112-TREND-THEME2-B-A2-B1-FULL-AUDIO-TRIAL-13)
  稼働中にPM_GOVERNANCE明文化・Git反映を並行実施した際、ユーザーが原則を
  (b)(独立タスクであればFable判断で並列起動可)へ緩和する決定をした。

**待機中Agentの再開リスクと同一管理IDへの多重起動禁止(2026-09-06追記)**:

- バックグラウンド待機(sleep・ポーリング・「通知を待つ」)を仕掛けたAgentは、
  セッションが終了したように見えても後から自動再開しうる。Fableはこれを
  「終了済み」とみなさない。
- 同一管理ID・同一出力先へ追加のAgentを起動しない(既存条件3の再確認・強化)。
  既存Agentの終了(担当プロセスの終了と最終報告の受領)を確認する前に、
  代替Agentを投入しない。
- Agentの待機は前面同期(foregroundの`sleep`等、結果を待ってから次へ進む形)を
  原則とし、バックグラウンド待機で自セッションを終了しない。Fableは委任文で
  これを明示する。
- 上記は「ファイル・出力先が重ならない独立タスクの並列」を制限するものではない。
  禁止されるのは同一タスク(同一管理ID・同一出力先)への多重関与である。
- 経緯: 2026-09-05〜06、Trial-13で待機中Agentの自動再開により同一管理IDへ
  複数Agentが関与し、一時ファイル・Reportの上書き競合と重複TTSが発生した
  ことを受けたユーザー指示(2026-09-06)。

## 9. ユーザー向け報告フォーマットとPMとしての説明原則(USER-FACING REPORT FORMAT)

Fableがユーザーへ報告・説明する際は、Sonnetの技術レポートをそのまま転記しない。
Fableの役割は、証拠を失わずに「ユーザーが判断しやすい言葉」へ翻訳することである。

### 9-1. 報告の基本構造(5構造)

ユーザー向け報告は、原則として以下の5構造で書く。

1. **現在の状態** — 最初に1〜3文で現在地を平易に説明する。内部経緯・
   Agent回数・path・process詳細等はここに詰め込まない。
2. **未解決問題** — 1, 2, 3…と番号付きで列挙する。1項目1論点とし、
   ユーザーが理解できる言葉を優先する。
3. **次にやること** — 未解決問題と同じ番号で対応させる(未解決問題1→
   次にやること1)。対応関係が分からない独立TODO列挙は禁止する。
   Claude側で自律実行できるものはユーザー判断を求めず実行してよい。
4. **ユーザー判断** — 必要な場合のみ記載する。未解決問題に紐づく場合は
   同じ番号を使う(問題1→ユーザー判断1)。独立した判断事項は「その他の
   ユーザー判断」として分ける。原則としてFable/PMの推奨案と短い推奨理由を
   必ず添える。ただしユーザー本人の主観評価そのもの(例: 実際に音声を
   聞いて自然か)が必要な場合は推奨不要。
5. **補足・技術詳細** — 必要な場合のみ最後に置く。commit SHA・path・
   runtime evidence・token・model_id・詳細ログ等はここへ分離し、判断に
   不要なら本文へ出しすぎない。

重要: 「結論」「重要ポイント」「ユーザー判断」を独立に羅列する旧形式は
原則使わない。「次にやること」がどの問題に対応しているか分からない報告は
禁止する。

### 9-2. PMとしての説明原則

- まず現在地を簡潔に示す。
- 1段落1論点。長い一文や複数論点の詰め込みを避ける。
- Sonnetのraw report・log・path一覧をそのまま貼らない。
- 「問題 → 次の対応 → 必要なら判断」の順で説明する。
- ユーザー判断が不要なら質問しない。必要なら何を決めるのかを明確にする。
- 推奨できる場合は推奨案を示す(9-1の4参照)。
- 不確実な事項は断定せず、UNKNOWN / UNVERIFIED / 推定を区別する。
- 「安全になった」「テストが通った」だけで成功と表現せず、ユーザー価値・
  分かりやすさ・面白さ・量産性・再発性への影響も必要に応じて説明する。
- ユーザーが「簡潔に」と言った場合は、現在の状態+未解決問題+ユーザー判断
  だけに圧縮する。
- ユーザーが追加詳細を求めた場合にのみ、補足・技術詳細を展開する。
- Fable自身の説明が複雑になった場合は、最後に1行で「要するに」を付ける。
- 可能なら、悪い例より良い例を優先して示す。

本原則はFableのユーザー向け報告に適用する。Sonnet/OpusからFableへの報告
(`RESULT_PACKET.md`・ER/OPEN Report)は従来どおり証跡・原文を省略せず詳細に
記録する(証跡はSSOT/Report側に残し、ユーザー向け説明で圧縮する)。

- 経緯: 2026-09-05、Trial-11〜13の一連の報告でSonnetの技術レポートに近い
  長文報告が続き、ユーザーの判断負荷が高かったことを受けたユーザー指示に
  より新設(PM-GOVERNANCE-USER-FACING-EXPLANATION-STYLE-03)。
- 経緯: 2026-09-06、Trial-11〜13期間の報告が長く判断しにくかったこと・
  commit確認の往復がボトルネックだったことを受け、旧「推奨フォーマット」
  (結論/重要ポイント/問題/ユーザー判断/技術詳細)を、番号対応する5構造
  (現在の状態/未解決問題/次にやること/ユーザー判断/補足・技術詳細)へ
  置き換えるユーザー方針確定により改訂(PM-GOVERNANCE-REPORT-FORMAT-AND-
  AUTONOMOUS-GIT-05)。

## 10. commit / push運用

- 通常のcommit/pushは、原則としてClaude側(Fable→sonnet-worker)が適宜
  自律実行し、毎回ユーザーへ確認しない。Claude側で責任を持って、作業
  区切り・SSOT更新・Report更新・必要なGit反映を忘れずに実行する。
- ただし以下のいずれかに該当する場合は、実行前にユーザー判断を求める。
  1. commit/pushによってユーザー判断結果が変わりうる場合
  2. Production採用判断を含む場合
  3. rollback・force push・history rewrite等の破壊的操作を伴う場合
  4. merge conflict等で複数の意味ある選択肢がある場合
  5. どの変更を正式採用するかユーザー判断が必要な場合
  6. 意図しないファイルを含む可能性がある場合
  7. 既存のユーザー承認内容と矛盾する可能性がある場合
  8. その他、Claude側だけで安全に確定できない場合
- 上記に該当しない通常の安全なcommit/pushは自律実行し、結果だけを簡潔に
  報告する。
- 既存の運用(8節「ファイル名指定の`git add`のみ、`-A`禁止」、`CLAUDE.md`
  「Git運用ルール」の履歴書き換え等[amend・rebase・force push]は必ず
  ユーザーに確認する)は本節と矛盾せず、そのまま維持する。
- 経緯: 2026-09-06、通常commit/pushのたびにユーザー確認を挟む運用が
  ボトルネックになっていたことを受けたユーザー方針確定
  (PM-GOVERNANCE-REPORT-FORMAT-AND-AUTONOMOUS-GIT-05)。

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
- 2026-09-05(PM-GOVERNANCE-PARALLEL-AGENT-POLICY-02): 「8. Agent並列起動の
  原則」を新設。従来の「ユーザーの指示なしに複数Agentを並列起動しない」を、
  対象ファイル・出力先が重ならない独立タスクであればFableの判断で並列起動
  可へ緩和し、一時ファイル(`ACTIVE_TASK.md`/`RESULT_PACKET.md`)の衝突回避・
  Git stage分離・同一管理ID/出力先への並列起動禁止・ループ上限の独立計算を
  必須条件として明記した(文書編集のみ、コード・Prompt変更なし)。Trial-13
  稼働中にPM_GOVERNANCE明文化を並行実施した実運用を受けたユーザー決定(b)。
- 2026-09-05(PM-GOVERNANCE-USER-FACING-EXPLANATION-STYLE-03): 「9.
  ユーザー向け説明スタイル(USER-FACING EXPLANATION STYLE)」を新設。
  Fableのユーザー向け報告は結論先出し・重要点3〜5点・技術詳細は必要時のみ
  末尾に分離するという原則15項目と推奨フォーマットを明文化し、
  Sonnet/OpusからFableへの報告(`RESULT_PACKET.md`・ER/OPEN Report)は
  従来どおり証跡・原文を省略せず詳細に記録することを併記した(文書編集のみ、
  コード・Prompt変更なし)。Trial-11〜13の報告でユーザーの判断負荷が
  高かったことを受けたユーザー指示による新設。
- 2026-09-06(PM-GOVERNANCE-AGENT-WAIT-AND-DUPLICATE-LAUNCH-RULE-04):
  「8. Agent並列起動の原則」へ「待機中Agentの再開リスクと同一管理IDへの
  多重起動禁止」を追記。バックグラウンド待機(sleep・ポーリング等)を仕掛けた
  Agentはセッション終了に見えても自動再開しうるためFableは「終了済み」と
  みなさないこと、同一管理ID・同一出力先への追加Agent起動禁止(既存終了確認前の
  代替投入禁止)、Agentの待機は前面同期を原則としバックグラウンド待機で
  自セッションを終了しないこと、これらは独立タスクの並列可の方針を制限
  するものではなく禁止対象は同一タスクへの多重関与であることを明記した
  (文書編集のみ、コード・Prompt変更なし)。既存の箇条書き・独立タスク並列可の
  方針は削除・改変していない。2026-09-05〜06、Trial-13で待機中Agentの
  自動再開により同一管理IDへ複数Agentが関与し、一時ファイル・Reportの
  上書き競合と重複TTS(約¥4)が発生したことを受けたユーザー指示(2026-09-06)。
- 2026-09-06(PM-GOVERNANCE-REPORT-FORMAT-AND-AUTONOMOUS-GIT-05): 「9.
  ユーザー向け説明スタイル」を「9. ユーザー向け報告フォーマットとPMとしての
  説明原則」へ改訂し、旧「推奨フォーマット」(結論/重要ポイント/問題/
  ユーザー判断/技術詳細)を、番号対応する5構造(現在の状態/未解決問題/
  次にやること/ユーザー判断/補足・技術詳細)へ置き換えた(9-1)。従来の
  説明原則15項目のうち5構造と矛盾しないもの(1段落1論点・raw report転記
  禁止・UNKNOWN/UNVERIFIED/推定の区別・安全≠成功・簡潔要求時の圧縮・
  追加詳細要求時のみ展開・「要するに」・良い例優先等)は「PMとしての
  説明原則」(9-2)として維持した。「10. commit / push運用」を新設し、
  通常の安全なcommit/pushは原則としてClaude側(Fable→sonnet-worker)が
  自律実行し、破壊的操作・Production採用判断を含む・意図しないファイル
  混入の可能性等の例外時のみユーザー判断を求める運用を明文化した。
  1節の責任分担を、ユーザー=「破壊的操作・Production採用判断を含む
  commit/push等10節が定める例外時の判断」、Fable/sonnet-worker=「10節が
  定める通常の安全なcommit/pushは自律実行」へ整合させた。既存8節の
  「ファイル名指定の`git add`のみ、`-A`禁止」・`CLAUDE.md`「Git運用
  ルール」の履歴書き換え等の確認原則は無変更のまま維持(文書編集のみ、
  Productionコード・Prompt変更なし)。Trial-11〜13期間の報告が長く
  判断しにくかったこと、commit確認の往復がボトルネックだったことを
  受けたユーザー方針確定(2026-09-06)。
