# PM_GOVERNANCE — PM運用規則(正式SSOT)

**管理ID: PM-HANDOFF-CHATGPT-001-CLOSEOUT-SSOT-01**
**最終更新: 2026-09-06(PM-FABLE-SONNET-REVIEW-LOOP-03でFable↔Sonnetレビュー
往復上限を「Sonnet合計最大2回」から「初回+最大3回(合計最大4回)」へ変更し、
FableのEditorial/PM Gatekeeper原則を明文化した新設11節を追加)。2026-09-06(PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-01でTTS方式の
決定基準を「正式リリース前=Standard同期/正式リリース後の実量産=Batch API」へ
統一し7節を7-1〜7-3へ再編)。2026-09-06(PM-GOVERNANCE-LOCAL-FILE-LINK-RULE-07でユーザーへの
試聴・閲覧依頼は`file:///C:/Users/tensh/eigo-radio/...`形式のURLで提示する
ことを9-2へ追加)。2026-09-06(PM-GOVERNANCE-ADAPTIVE-REPORTING-06でユーザー向け
報告フォーマットの5構造[現在の状態/未解決問題/次にやること/ユーザー判断/
補足・技術詳細]を、固定必須から必要な項目だけを選ぶ候補セクション制
[adaptive reporting]へ改訂[9節])。2026-09-06(PM-GOVERNANCE-REPORT-FORMAT-AND-AUTONOMOUS-GIT-05で
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
- ループ上限は11節を正本とする(`CLAUDE.md`・`PM_BRIEF.md`は参照のみ)。

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

### 7-1. 方式の決定基準(リリース前=Standard同期/リリース後の実量産=Batch API)

【最重要ルール】TTS方式は「Production相当かどうか」ではなく「正式リリース前か、
正式リリース後の実量産か」で決める。

- **正式リリース前**: 原則すべて**Standard同期**を使用する。含む: DEV /
  Trial / 診断 / Production相当テスト / 量産相当テスト / Production正式
  経路を使ったruntime確認 / A2・B1等の完成候補生成 / Production wiring後の
  実データ確認 / 回帰確認 / 少数・複数記事の量産模擬。ユーザーが
  「Production相当で作って」「量産相当で確認して」「正式経路で生成して」と
  指示しても、正式リリース前である限りTTSはStandard同期とする。これらの
  表現を、TTS方式までBatchに合わせる指示とは解釈しない。
- **正式リリース後**: 決済・配信その他の導線が整い、実ユーザー向け
  サービスとして正式リリースされた後の実際の量産生成では**Batch API**を
  使用する(正式リリース後の実量産における正式TTS方式。正本は
  `CURRENT_SPEC.md`「Gemini TTS実装方式(Batch API)」であり、本ファイルへは
  全文を複製しない)。
- **重要な区別**: Production正式コード/Production正式経路とTTS実行方式は
  別概念である。正式リリース前は「Production正式コード+Production正式
  routing+Production正式Validator+Standard同期TTS」でruntime確認して
  よい。Standard同期を使ったことだけを理由に「Production正式経路では
  ない」と判断しない。「Production相当だからBatch」という誤解が起きない
  よう、この基準を明記する。

### 7-2. 例外(Batchを使ってよい場合と記録)

正式リリース前でも、以下のいずれかに該当する場合に限りBatchを使ってよい。

1. Batch API固有の挙動そのものの検証が目的である場合
2. StandardとBatchの差異確認自体がテスト目的である場合
3. ユーザーが明示的に「Batchで確認」と指定した場合
4. FableがBatchでなければ検証目的を満たせないと判断した場合

この場合、Batchを使う理由を簡潔にReportへ記録する。

### 7-3. 明示・確認原則(既存)

- TTS生成を含むタスク定義(`docs/pm/ACTIVE_TASK.md`・Fableからsonnet-workerへの
  委任文)には、使用するTTS方式(Batch API / Standard同期)を必ず明記する。
  既定は7-1のとおり、正式リリース前はStandard同期。
- タスク定義にTTS方式の明記がない場合、Fableは着手前に必ずユーザーへ確認する。
  Sonnet/Opusは方式が不明なまま生成に着手せず、STOPしてFable経由でユーザーへ
  確認を求める。
- 方式の切り替え(Standard→Batch等)や1エピソード内での方式混在は、ユーザーの
  明示承認がある場合に限り行い、Production忠実性への影響(Production経路と
  異なる条件で得た結果である旨)・所要時間・コスト差を必ずReportへ記録する。
  Production call site自体の変更はこの原則の対象外(別途Gate 3の対象)。
- Standard同期の指定は環境変数`TTS_EXECUTION_MODE=STANDARD`で行う(monkeypatch
  不要、`er006_batch_tts_wiring_01.py::make_batch_tts_call_fn()`内の分岐、
  ER-011-TTS-EXECUTION-MODE-SWITCH-PRODUCTION-WIRING-01、`PRODUCTION_WIRED`、
  正本は`CURRENT_SPEC.md`「Gemini TTS実装方式(Batch API)」行)。
- タスク着手前に、選択したTTS方式に応じたおおよその所要時間・コストの見込みを
  ユーザーへ提示する。
- 経緯: 2026-09-05、Trial-13(OPEN-112-TREND-THEME2-B-A2-B1-FULL-AUDIO-TRIAL-13)
  でタスク定義にTTS方式が明記されず、所要時間の見込み共有が漏れたことを受けた
  ユーザー指示により新設。
- 経緯: 2026-09-06(PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-01)、Phase 2
  (OPEN-117-KEYPHRASE-DISPLAY-TTS-SEPARATION-TRIAL-02)がBatchで長時間化した
  (1件91〜167秒、retry発生時はさらに積み重なる)ことを受け、「正式リリース前は
  原則Standard同期・正式リリース後の実量産はBatch API」という決定基準
  (7-1)・例外(7-2)を新設した。

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
  4. 各タスクのループ上限(11節)は管理IDごとに独立して数える。
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

### 9-1. 候補セクションと選択基準(adaptive reporting)

ユーザー向け報告は、以下5つを固定必須の見出しとして毎回すべて埋めるのでは
なく、「候補セクション」として扱い、その回答の目的に応じて必要な項目だけを
組み合わせて使う(adaptive reporting)。「レス」と「報告」で別フォーマットに
分けるのではなく、本節1つの共通ルールでFableがそのつど必要な分量を判断する。

1. **現在の状態** — 現在地・実行状況をユーザーへ伝える必要がある場合のみ
   使う。1〜3文で平易に説明する。内部経緯・Agent回数・path・process詳細等は
   ここに詰め込まない。
2. **未解決問題** — ユーザーが認識・管理すべき未解決事項がある場合のみ
   使う。単なる作業中のレスでは不要。使う場合は1, 2, 3…と番号付きで列挙し、
   1項目1論点とする。`USER_DECISION_REQUIRED`に該当する事項がある場合は、
   このセクションを省略せず必ず明示する(隠さない。9-2参照)。
3. **次にやること** — 今後の作業をユーザーへ知らせる意味がある場合のみ
   使う。直前の指示をそのまま実行開始しただけなら省略できる。未解決問題と
   同時に使う場合は同じ番号で対応させる(未解決問題1→次にやること1)。
   対応関係が分からない独立TODO列挙は禁止する。Claude側で自律実行できる
   ものはユーザー判断を求めず実行してよい。
4. **ユーザー判断** — 本当に必要な場合のみ使う。Claude/Fable側で安全に
   判断・実行できる事項について形式的に判断を求めない。未解決問題に紐づく
   場合は同じ番号を使う(問題1→ユーザー判断1)。独立した判断事項は「その他の
   ユーザー判断」として分ける。原則としてFable/PMの推奨案と短い推奨理由を
   必ず添える。ただし試聴・感覚評価などユーザー本人の主観判断そのものが
   本体の場合(例: 実際に音声を聞いて自然か)は推奨不要。`USER_DECISION_
   REQUIRED`に該当する場合はこのセクションも省略しない。
5. **補足・技術詳細** — commit SHA・path・runtime evidence・token・
   model_id・詳細ログ等がユーザーの理解・判断に必要な場合のみ最後に置く。
   不要なら省略する。

最重要原則: 「テンプレートを埋めるために見出しを出す」ことは禁止する。
5項目を毎回すべて出す固定必須構造ではなく、回答の目的に応じて必要最小限の
セクションだけを使う。例えば、指示を受けて作業に着手した直後のレスは
「現在の状態」だけでよい(例文: 「ご指示を反映して、A2音割れの追加計測と
Key Phrase Validator修正の隔離Trialを並列で開始しました。同音語は厳密な
完全同音のみPASS候補として検証します。Production変更はまだ行っていません。」)。
一方、Trial closeoutや複数問題を伴う診断報告では、必要な候補セクションを
展開する。「次にやること」がどの問題に対応しているか分からない報告(対応
関係不明な独立TODO列挙)は本節でも引き続き禁止する。

### 9-2. PMとしての説明原則

- 1段落1論点。長い一文や複数論点の詰め込みを避ける。
- Sonnetのraw report・log・path一覧をそのまま貼らない。
- 「問題 → 次の対応 → 必要なら判断」の順で説明する(結論・現在地を先に示す)。
- 必要なら何を決めるのかを明確にする(9-1の4「ユーザー判断」の選択基準・
  推奨付き原則を参照)。
- `USER_DECISION_REQUIRED`に該当する事項を隠さない。判断が必要な場合は
  9-1の該当セクションを省略せず明示する。
- 不確実な事項は断定せず、UNKNOWN / UNVERIFIED / 推定を区別する。
- 「安全になった」「テストが通った」だけで成功と表現せず、ユーザー価値・
  分かりやすさ・面白さ・量産性・再発性への影響も必要に応じて説明する。
- ユーザーが「簡潔に」と言った場合は、その時点で使っている候補セクションを
  さらに絞り込む(現在の状態+未解決問題+ユーザー判断など必要最小限へ)。
- ユーザーが追加詳細を求めた場合にのみ、補足・技術詳細を展開する。
- Fable自身の説明が複雑になった場合は、最後に1行で「要するに」を付ける。
- 可能なら、悪い例より良い例を優先して示す。
- ユーザーへ試聴・閲覧を依頼するローカル成果物(音声player・html・音声
  ファイル等)は、必ず `file:///C:/Users/tensh/eigo-radio/<相対パス>` 形式の
  URL(Ctrl+クリックで開ける)で提示する。パスのみの記載や`SendUserFile`等
  での送付は行わない(2026-09-06ユーザー指示)。sonnet-workerのReport/
  RESULT_PACKETにも同形式で記載させる。

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
- 経緯: 2026-09-06、単純な指示へのレスでも固定5構造の全項目を出すと冗長で
  分かりづらいというユーザー判断により、5構造を「毎回全部埋める固定必須
  構造」から「必要な項目だけを選ぶ候補セクション」(adaptive reporting)へ
  改訂。情報を減らして隠す変更ではなく、不要なセクション表示を省略して
  読みやすくするものであり、`USER_DECISION_REQUIRED`を省略しないことは
  9-1・9-2で明示している(PM-GOVERNANCE-ADAPTIVE-REPORTING-06)。

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

## 11. Fable↔Sonnetレビュー往復の上限とGatekeeper原則

**管理ID: PM-FABLE-SONNET-REVIEW-LOOP-03(2026-09-06ユーザー決定)**

Fable↔Sonnetのレビュー往復上限を、従来の「Sonnet委任は合計最大2回
(初回+修正1回)」から「初回+Fableが必要と判断した場合の修正・再生成
指示最大3回(1管理IDあたりSonnet実行は合計最大4回)」へ変更する。この
上限は今後の通常の実装・Trial・記事生成・品質改善タスクに恒久的に適用する。

**意味**: 初回Sonnet成果物の後、Fableが必要と判断した場合、最大3回まで
FableからSonnetへ修正・追加確認・再生成指示を出してよい。

**目的**:
- ユーザー意図とのズレをFableが吸収する
- 軽微なズレのたびに毎回ユーザーへ差し戻さない
- ユーザーへ提示する前に完成度を上げる
- FableのPM/Editorial Gate機能を強化する

**守ること(8項目)**:
1. 3回使い切ることを目的にしない
2. 1回で十分なら1回で止める
3. `USER_DECISION_REQUIRED`をSonnetだけで解決しない
4. 仕様変更・Production採用判断はユーザーへ戻す
5. 新しい仕様候補を勝手に追加しない
6. STOP条件に該当したら往復回数が残っていてもSTOPする
7. 同一問題を意味なく反復しない
8. QCD(品質・コスト・納期)上、追加往復の価値が低い場合は早めに
   ユーザーへ報告する

**Gatekeeper原則(Gate 7の補足)**: Fableは単なる受取役ではなく、Sonnet
成果物をユーザー意図・受入条件と照合するEditorial/PM Gatekeeperとして
動く。ズレがあれば、ユーザーへ出す前にSonnetへ修正指示を返す。

**不変の項目**: Opus診断1回上限、Agent Teams不使用、Agent並列起動の原則
(8節)はいずれも変更しない。

**経緯**: 2026-09-06、Lane B(EDITORIAL-B-FAMILY-VOICES-TRIAL-03)で
ユーザー意図とのズレが生じたことを受け、Fableが往復の中でズレを吸収
できるようにする目的でユーザーが決定した(PM-FABLE-SONNET-REVIEW-LOOP-03)。

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
- 2026-09-06(PM-GOVERNANCE-ADAPTIVE-REPORTING-06): 「9-1. 報告の基本構造
  (5構造)」を「9-1. 候補セクションと選択基準(adaptive reporting)」へ
  改訂し、5構造(現在の状態/未解決問題/次にやること/ユーザー判断/補足・
  技術詳細)を「毎回全部埋める固定必須構造」から「その回答の目的に応じて
  必要な項目だけを選ぶ候補セクション」へ変更した。各セクションの選択基準
  (現在地・実行状況を伝える必要がある場合のみ/ユーザーが認識・管理すべき
  未解決事項がある場合のみ/今後の作業を知らせる意味がある場合のみ/本当に
  必要な場合のみ/判断に必要な場合のみ)を明記し、番号対応(未解決問題→
  次にやること→ユーザー判断)・推奨案付き原則・`USER_DECISION_REQUIRED`を
  省略しないことは維持した。「レス」「報告」で別フォーマットに分けず、
  1つの共通ルールでFableが必要量を調整する。9-2は9-1と重複する項目
  (「まず現在地を簡潔に示す」「推奨できる場合は推奨案を示す」等)を
  9-1側へ寄せて整理し、`USER_DECISION_REQUIRED`を隠さない旨を明文化した
  項目を追加した(内容は削除せず統合)。`.claude/agents/sandwich-pm.md`
  「## 報告」節の参照も候補セクション制へ更新した(文書編集のみ、
  Productionコード・Prompt変更なし)。単純な指示へのレスでも固定5構造の
  全項目を出すと冗長で分かりづらいというユーザー判断により新設。情報を
  減らして隠す変更ではなく、不要なセクション表示を省略して読みやすく
  するもの。
- 2026-09-06(PM-GOVERNANCE-LOCAL-FILE-LINK-RULE-07): 「9-2. PMとしての
  説明原則」へ、ユーザーへ試聴・閲覧を依頼するローカル成果物(音声player・
  html・音声ファイル等)は必ず`file:///C:/Users/tensh/eigo-radio/<相対パス>`
  形式のURL(Ctrl+クリックで開ける)で提示し、パスのみの記載や
  `SendUserFile`等での送付は行わない旨の箇条書きを追加した(sonnet-worker
  のReport/RESULT_PACKETにも同形式で記載させる)。ユーザーのクライアントで
  パス記載や`SendUserFile`では試聴用ファイルが開けなかったことを受けた
  2026-09-06ユーザー指示による新設(文書編集のみ、コード・Prompt変更なし)。
- 2026-09-06(PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-01): 「7. TTS方式
  (Batch API / Standard同期)の明示・確認原則」を7-1(方式の決定基準)・
  7-2(例外)・7-3(明示・確認原則、既存内容)へ再編し、TTS方式は
  「Production相当かどうか」ではなく「正式リリース前か、正式リリース後の
  実量産か」で決めるという基準を新設した。正式リリース前(DEV/Trial/診断/
  Production相当テスト/量産相当テスト/Production正式経路を使ったruntime
  確認/A2・B1等の完成候補生成/Production wiring後の実データ確認/回帰確認/
  少数・複数記事の量産模擬を含む)は原則すべてStandard同期を既定とし、
  「Production相当で作って」等の指示をTTS方式までBatchに合わせる指示とは
  解釈しないことを明記した。正式リリース後の実ユーザー向けサービスとしての
  実際の量産生成はBatch API(正式方式)のまま維持し、旧「Production標準は
  Batch API」という記述を「正式リリース後の実量産の正式方式」へ言い換えた。
  Batchを使ってよい例外4点(Batch固有挙動の検証/Standard・Batch差異確認
  自体がテスト目的/ユーザー明示指定/Fableが必要と判断)とその記録義務を
  7-2として新設した。Production正式コード/Production正式経路とTTS実行
  方式は別概念であり、正式リリース前でも「Production正式コード+
  Production正式routing+Production正式Validator+Standard同期TTS」で
  runtime確認してよいこと、Standard同期の使用だけを理由に「Production
  正式経路ではない」と判断しないことを明記した。既存の7-3(タスク定義への
  方式明記・未明記時のユーザー確認・切り替え混在時の記録・着手前の所要
  時間/コスト見込み提示)は内容を維持した(文書編集のみ、コード・Prompt
  変更なし)。2026-09-06、Phase 2(OPEN-117-KEYPHRASE-DISPLAY-TTS-
  SEPARATION-TRIAL-02)がBatch APIの実測待ち時間(1件91〜167秒)により
  長時間化したことを受けたユーザー決定。
- 2026-09-06(PM-FABLE-SONNET-REVIEW-LOOP-03): 「11. Fable↔Sonnetレビュー
  往復の上限とGatekeeper原則」を新設。Fable↔Sonnetのレビュー往復上限を
  「Sonnet委任は合計最大2回(初回+修正1回)」から「初回+Fableが必要と
  判断した場合の修正・再生成指示最大3回(合計最大4回)」へ恒久的に変更し、
  1節の参照・8節条件4の括弧をこの11節へ整合させた。3回使い切ることを
  目的にしない・1回で十分なら1回で止める・`USER_DECISION_REQUIRED`を
  Sonnetだけで解決しない・仕様変更/Production採用判断はユーザーへ戻す・
  新しい仕様候補を勝手に追加しない・STOP条件該当時は往復回数が残って
  いてもSTOPする・同一問題を意味なく反復しない・QCD上価値が低い場合は
  早めにユーザーへ報告する、という8項目の遵守事項を明記した。あわせて
  「Fableは単なる受取役ではなく、Sonnet成果物をユーザー意図・受入条件と
  照合するEditorial/PM Gatekeeperとして動き、ズレがあればユーザーへ出す
  前にSonnetへ修正指示を返す」ことをGate 7の補足として明記し、
  `.claude/agents/sandwich-pm.md`の手順4・6・上限到達時の記述を整合させた。
  Opus診断1回上限・Agent Teams不使用・8節のAgent並列起動の原則は変更して
  いない(文書編集のみ、コード・Prompt変更なし)。2026-09-06、Lane B
  (EDITORIAL-B-FAMILY-VOICES-TRIAL-03)でユーザー意図とのズレが生じたことを
  受けたユーザー決定。
