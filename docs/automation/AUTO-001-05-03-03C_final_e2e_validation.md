# AUTO-001-05-03-03C 最終E2E検証記録

管理ID: AUTO-001-05-03-03C-DOC-01

本ドキュメントは、AUTO-001-05-03-03C(read-only plannerとController App writerの`issues:labeled`統合)の実装・修正・実GitHub E2E検証の経緯を、恒久的な記録として1件のMarkdownへ集約するものである。Issue #12・#14を将来Closeした後も、何をどのRunで確認したかを追跡できるようにすることを目的とする。

**本文書の性質について**: 記載内容は「事実」「推定」「最終判断」の3種類に分かれる。

- **事実**: Run ID・Issue番号・PR番号・commit SHA・ジョブ結論(success/failure/skipped)など、GitHub Actions REST API(read-only、認証なし)またはローカル`git log`で本ドキュメント作成時に直接確認したもの。
- **推定**: ログ・API応答からは直接得られないが、コードとGitHub Actionsの仕様から高い確度で導いた原因分析(§4・§5の「原因」に相当する部分)。
- **最終判断**: 上記の事実・推定を踏まえた合否判定(§7等)。

各節でこの3種類が区別できるよう、事実には検証方法を併記する。

---

## 1. 対象範囲と経緯の概要

AUTO-001-05-03-03Cは、検証済みのread-only planner(`scripts.issue_agent_planner`)とController App writer(`scripts.controller_label_writer` / `scripts.controller_block_writer`)を、`issues:labeled`実イベントへ統合するタスクである。実装(PR #11)の後、実GitHub E2E検証(E1〜E5)の過程で2件の不具合(R5・R6)が発見され、いずれも修正・再検証まで完了した。

本ドキュメントは、この一連の実装・修正・検証の全体像を記録する。

---

## 2. 前提: 最終mainとPull Request

### 2.1 最終main

| 項目 | 値 |
|---|---|
| 最終main SHA | `a5757ee026ccb67e8917bf91ded67da1bb1b897b` |
| 検証方法 | 本ドキュメント作成時に`git fetch origin && git rev-parse origin/main`で確認(事実)。`git log --oneline --graph`で下記PRのmerge commitと親子関係も併せて確認済み |

### 2.2 主なPull Request

| PR | 内容 | 主なcommit | merge commit | 検証状態 |
|---|---|---|---|---|
| #11 | 03C統合workflowの実装 | `568e626`(初期実装)、`b2af4a8`(R1)、`8e21adb`(R2)、`9f9b0aa`(R3)、`a8d683f`(R4) | `bbf717b7ac422f46ac15d941c6f729917bd8e904` | `git log`で親子関係を確認済み(事実) |
| #13 | reusable writerへのIssue番号型変換修正(R5) | `9f408b9f58b90e9835a038164cf46069f0f457cd`(R5変更commit) | `8e6831e052d493306ca6b1121db8a43295aabfbb` | `git log`で確認済み(事実) |
| #15 | managed comment NOOP経路修正(R6) | `3a6e3d091e7b84175aec85d2cba2744615999631`(R6変更commit) | `a5757ee026ccb67e8917bf91ded67da1bb1b897b` | `git log`で確認済み(事実) |

`git log --oneline --graph`の抜粋(事実、本ドキュメント作成時に実行):

```text
*   a5757ee Merge pull request #15 from shimomura055/automation/AUTO-001-05-03-03C-R6
|\
| * 3a6e3d0 fix: treat managed comment MATCHES as NOOP instead of false state-change (AUTO-001-05-03-03C-R6)
|/
*   8e6831e Merge pull request #13 from shimomura055/automation/AUTO-001-05-03-03C-R5
|\
| * 9f408b9 fix: convert issue_number to number type for reusable writer calls (AUTO-001-05-03-03C-R5)
|/
*   bbf717b Merge pull request #11 from shimomura055/automation/AUTO-001-05-03-03C
|\
| * a8d683f fix: reject empty contract_version on all paths with explicit sentinels (AUTO-001-05-03-03C-R4)
| * 9f9b0aa fix: contract_version gate never fired because called-workflow github.event_name is the caller's original event (AUTO-001-05-03-03C-R3)
| * 8e21adb refactor: make 03A/03B reusable workflows, remove writer duplication from integrated.yml (AUTO-001-05-03-03C-R2)
| * b2af4a8 fix: treat writer-contract mismatch and unknown decisions as Failure (AUTO-001-05-03-03C-R1)
| * 568e626 feat: integrate read-only planner and Controller App writer into issues:labeled (AUTO-001-05-03-03C)
|/
```

### 2.3 fixture Issue

| 用途 | Issue |
|---|---|
| 正常系(agent:ready → agent:working) | #12 |
| 不正系(agent:ready → agent:blocked) | #14 |

---

## 3. 実GitHub E2E検証記録(E1〜E5)

各RunのRun ID・event種別・conclusion・関連ジョブのconclusionは、GitHub Actions REST API(`GET /repos/.../actions/runs/{id}`および`.../jobs`、read-only・認証なし)で本ドキュメント作成時に直接確認した(事実)。decision・comment件数・ラベル状態など、job summary相当のより細かい値は、実行時に作業者が確認した記録に基づく。

### 3.1 E1: readyなし・非書き込み

| 項目 | 値 |
|---|---|
| Issue | #12 |
| Run ID | `30668602144` |
| API確認 | workflow=`AUTO-001 Controller App Integrated Write`, event=`workflow_dispatch`, conclusion=`success`(事実) |
| decision | `WOULD_BLOCK_STATE` |
| writer_start | Skipped |
| writer_block | Skipped |
| Controller App token | 生成なし |
| Issue変更 | なし |
| 判定 | **合格** |

### 3.2 E2: 正常系START

| 項目 | 値 |
|---|---|
| Issue | #12 |
| Run ID | `30674229799` |
| API確認 | workflow=`AUTO-001 Controller App Integrated Write`, event=`issues`, conclusion=`success`, head_sha=`8e6831e...`(R5マージ後、事実) |
| decision | `WOULD_START` |
| writer_start | Success |
| writer_block | Skipped |
| contract version確認 | Success |
| Controller App token生成 | Success |
| agent:working追加 | Success |
| agent:ready削除 | Success |
| comment | なし |
| 最終ラベル | agent:workingのみ |
| branch／commit／PR変更 | なし |
| 判定 | **合格** |

### 3.3 E3: 不正系CREATE

| 項目 | 値 |
|---|---|
| Issue | #14 |
| 元Run ID | `30674862054` |
| API確認 | workflow=`AUTO-001 Controller App Integrated Write`, event=`issues`, conclusion=`success`, head_sha=`8e6831e...`(事実) |
| decision | `WOULD_BLOCK_PREFLIGHT` |
| 契約違反 | 1件 |
| error code | `ACCEPTANCE_CRITERIA_MISSING` |
| writer_block | Success |
| comment action | CREATE |
| agent:blocked追加 | Success |
| agent:ready削除 | Success |
| managed comment | 1件 |
| 最終ラベル | agent:blockedのみ |
| 判定 | **合格** |

#### 3.3.1 自己誘発安全停止

`issues:labeled`トリガーは、writerによるラベル変更自体も新たな`labeled`イベントとして発火する。この自己誘発イベントが誤って書き込みへ進まないことを確認した。

| 項目 | 値 |
|---|---|
| Integrated Write Run ID | `30674881683` |
| API確認 | conclusion=`success`。jobs: `plan`=success, `writer_block`=skipped, `writer_start`=skipped(事実、job一覧をAPIで直接確認) |
| decision | `NOT_APPLICABLE` |
| writer action | NONE |
| token生成 | なし(writer_start/writer_block双方がskippedのため、token生成stepに到達しない) |
| conclusion | Success |

| 項目 | 値 |
|---|---|
| read-only dry-run Run ID | `30674881580` |
| API確認 | workflow=`AUTO-001 Agent Planner Dry-Run`, event=`issues`, conclusion=`success`(事実) |
| decision | `NOT_APPLICABLE` |
| GitHub変更 | なし |

### 3.4 E4初回: NOOP不合格(R6で修正対象となった不具合の実再現)

| 項目 | 値 |
|---|---|
| Run ID | `30676777164` |
| API確認 | workflow=`AUTO-001 Controller App Integrated Write`, event=`issues`, conclusion=`failure`。jobs: `plan`=success, `writer_block / block_check`=**failure**, `writer_start`=skipped(事実、job一覧をAPIで直接確認) |
| result | Failure |
| write outcome | `STATE_CHANGED_BEFORE_WRITE` |
| 実際のcomment状態 | count=1, state=MATCHES |
| token生成 | Skipped |
| GitHub write | なし |
| 判定 | 安全停止(token生成前の停止)自体は合格。NOOP機能は**不合格** |

**原因(推定、§5のR6原因分析と同一)**:

- ラベル遷移状態(`PRECONDITION_STATE`)とmanaged comment状態を分離していなかった
- MATCHES(canonical一致)を誤って状態変化として扱った
- NOOP分岐が存在しなかった(CREATE/UPDATEの二択のみ)

**対応**: R6(PR #15)でNONE/MATCHES/STALEをCREATE/NOOP/UPDATEへ明示分類し、state・count・comment IDの真の変化だけを競合として拒否するよう修正した(詳細は§5)。

### 3.5 E4-R1: NOOP成功(R6修正後の再検証)

| 項目 | 値 |
|---|---|
| Issue | #14 |
| Run ID | `30685174978` |
| API確認 | workflow=`AUTO-001 Controller App Integrated Write`, event=`issues`, conclusion=`success`。jobs: `plan`=success, `writer_block / block_check`=**success**, `writer_start`=skipped(事実、job一覧をAPIで直接確認)。head_sha=`a5757ee...`(R6マージ後) |
| decision | `WOULD_BLOCK_PREFLIGHT` |
| comment action | NOOP |
| comment write API | SKIPPED |
| POST／PATCH | 未実行 |
| write outcome | `WRITE_SUCCEEDED` |
| managed comment一致 | true |
| 最終comment件数 | 1 |
| 最終ラベル | agent:blockedのみ |
| 判定 | **合格** |

### 3.6 E5: UPDATE成功

| 項目 | 値 |
|---|---|
| Issue | #14 |
| 03B直接手動Run ID | `30686068393` |
| API確認 | workflow=`AUTO-001 Controller App Block Check`, event=`workflow_dispatch`, conclusion=`success`。jobs: `block_check`=success(事実、job一覧をAPIで直接確認)。head_sha=`a5757ee...` |
| precondition | `COMMENT_UPDATE_REQUIRED` |
| comment action | UPDATE |
| comment write API | EXECUTED |
| 更新前comment ID | `5148504789` |
| 更新後comment ID | `5148504789`(同一) |
| 更新後error code | `MISSING_REQUIRED_CONTENT` |
| 対象section | テスト観点 |
| managed comment件数 | 1 |
| 最終ラベル | agent:blockedのみ |
| branch／commit／PR変更 | なし |
| 判定 | **合格** |

E5で使用したfixture本文は、事前にAUTO-001-05-03-03C-E5-PREで、実際のIssue #14の状態(read-only GET)に対し`classify_precondition()`を直接実行して`COMMENT_UPDATE_REQUIRED`(comment_id維持のままSTALE→UPDATE対象)になることをローカルで確認済みのものである。

---

## 4. R5で発見した問題と修正

### 4.1 現象(事実)

| 項目 | 値 |
|---|---|
| 失敗Run ID | `30669056610` |
| API確認 | jobs: `plan`=success、`writer_block`に相当するjobがjob一覧に一切出現しない(`writer_start`はskippedとして出現するのとは対照的)。conclusion=`failure`(事実、当時の診断セッションでAPIを直接確認済み) |
| 現象 | planは成功。実行対象のreusable writer(03A/03B)がrunner開始前に失敗。jobログなし。Issue書き込みなし |

### 4.2 原因(推定)

- plan jobのjob output(`needs.plan.outputs.issue_number`)は、GitHub Actions上では常に文字列型
- 呼び出し先(03A/03B)の`workflow_call.inputs.issue_number`は`type: number`で宣言
- この型不一致により、reusable workflow呼び出し(`uses:`)自体がrunner起動前に(job/step/ログを一切残さず)失敗した

GitHub側の内部実装の詳細ログは取得できておらず、上記は事象と公式ドキュメント記載の仕様から導いた高信頼度の推定である。

### 4.3 修正(PR #13、事実)

- plan jobのclassify stepで、issue_numberが厳密な正の整数文字列(`^[1-9][0-9]*$`)であることを事前検証し、空文字列・0以下・小数・数字以外はすべてfail-closedに拒否
- writer_start/writer_blockの`with:`側で、検証済み文字列を`fromJSON()`でnumber型へ変換してから03A/03Bへ渡す
- STARTとBLOCKの両経路に同一の修正を適用

---

## 5. R6で発見した問題と修正

### 5.1 現象(事実、§3.4のE4初回と同一事象)

- 既存managed commentがcanonical内容と一致(MATCHES)している状態を、writerが誤って`STATE_CHANGED_BEFORE_WRITE`として書き込み前に停止した(Run `30676777164`)
- comment write stepにNOOP経路が存在せず、CREATEとUPDATEの二択しかなかった

### 5.2 原因(推定)

`classify_precondition()`の「agent:readyのみ・agent:blockedなし」分岐が、managed comment状態を一切確認せず常に`NEEDS_WRITE`を返していた。呼び出し側のworkflowは「`NEEDS_WRITE`ならcommentは`NONE`のはず」と決め打ちしており、既存のcanonical一致commentを検出すると無条件に状態変化とみなしていた。安全停止(token生成前の停止)自体は正しかったが、判定根拠が誤っていた。

### 5.3 修正(PR #15、事実)

- ラベル遷移状態(`PRECONDITION_STATE`)とmanaged comment状態(`MANAGED_COMMENT_STATE`/`MANAGED_COMMENT_COUNT`/`COMMENT_ID`)を分離
- managed comment状態からcomment_actionを決定的に導出:
  - `NONE` → `CREATE`
  - `MATCHES` → `NOOP`
  - `STALE` → `UPDATE`
- 書き込み直前に再取得した状態と、precondition時点の状態(state・count・comment ID)を比較し、真に変化した場合だけ`STATE_CHANGED_BEFORE_WRITE`として拒否する
- comment write stepにNOOP分岐を追加し、comment_action=NOOPの場合はPOST/PATCHのいずれも呼ばない。ラベル遷移(agent:blocked追加・agent:ready削除)と最終comment確認は、NOOPの場合も省略しない

§3.4(E4初回)・§3.5(E4-R1)で、この修正が実GitHub上で機能することを確認済み。

---

## 6. 最終確認済み経路

```text
agent:ready
├─ 契約正常
│  └─ agent:working追加
│     └─ agent:ready削除
└─ 契約違反
   └─ agent:blocked追加
      ├─ commentなし → CREATE
      ├─ canonical一致 → NOOP
      └─ 古いcomment → UPDATE
         └─ agent:ready削除
```

上記経路のうち、CREATE(§3.3 E3)・NOOP(§3.5 E4-R1)・UPDATE(§3.6 E5)・agent:working経路(§3.2 E2)・非書き込み経路(§3.1 E1、§3.3.1自己誘発安全停止)のすべてを、実GitHub Issueイベントまたは03B直接手動実行で確認済みである(事実)。

---

## 7. 最終判定

**AUTO-001-05-03-03Cの対象範囲は、実GitHub E2Eを含めて合格とする。**

確認済み(事実に基づく最終判断):

- read-only planner
- 正常系writer(03A、agent:working経路)
- 不正系writer(03B、agent:blocked経路)
- reusable workflow呼び出し(統合workflowからの03A/03B呼び出し)
- contract version確認
- Controller App token生成境界(token生成前のfail-closed停止を含む)
- Issue番号型契約(R5修正、job output文字列 → number型変換)
- CREATE／NOOP／UPDATE(R6修正、managed comment状態に基づく分岐)
- 自己誘発イベント(writer自身のラベル変更が発火する`issues:labeled`)の安全停止
- secret／token値の非表示(job summary・ログへの非出力)
- branch／commit／PRの非生成

---

## 8. 非対象範囲・未実装

以下は03Cでは未実装であり、動作確認済みとは記載しない。

- Claude Codeの自動起動
- 実装agentの起動
- branch自動作成
- commit／push自動化
- Pull Request自動作成
- Contents write
- Implementer App
- OpenAIレビュー
- 自動merge

---

## 9. 残存する軽微な改善候補

管理ID: `AUTO-001-05-03-03C-OBS-01`

### 9.1 内容

03B直接手動UPDATE時(§3.6 E5に相当)のjob summaryで、

```text
write outcome: COMMENT_UPDATE_REQUIRED
```

と表示される。これは処理**開始時**の分類状態(precondition結果)であり、最終結果ではない。実際の処理はSuccessで、以下の通りである。

| 項目 | 値 |
|---|---|
| comment action | UPDATE |
| comment write API | EXECUTED |
| comment write outcome | reason_code=NONE |
| managed comment一致 | true |

### 9.2 評価

機能不良ではない(実際の処理結果はSuccessであり、`write outcome`欄の表示だけがprecondition時点の分類コードをそのまま流用しているために誤解を招きやすい)。将来、summary項目名を「initial state」等へ整理する改善候補として記録する。

**本文書(DOC-01)の追加ではworkflowコードを変更しない。** OBS-01の対応は別タスクとする。

---

## 10. 検証方法に関する補足

本ドキュメント作成時に、以下をread-only(認証なし・GitHub write API不使用)で独立に確認した。

- `git fetch origin` / `git rev-parse origin/main` / `git log --oneline --graph`(§2の最終main・PR merge commit・親子関係)
- `GET /repos/shimomura055/eigo-radio/actions/runs/{run_id}`(全8件のRun IDについて、workflow名・event種別・conclusion・head_shaを確認)
- `GET /repos/shimomura055/eigo-radio/actions/runs/{run_id}/jobs`(§3.3.1・§3.4・§3.5・§3.6のjob単位のconclusionを確認)

上記で確認した範囲において、本文書記載のRun ID・conclusion・head_shaに転記ミスは見つからなかった。decision・comment件数・ラベル状態など、job summary本文相当のより詳細な値は、各Run実行時に作業者が確認した記録に基づいており、本ドキュメント作成時に個別のログ全文までは再取得していない。
