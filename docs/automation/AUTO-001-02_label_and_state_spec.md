# AUTO-001-02 ラベルと状態遷移の仕様

管理ID: AUTO-001-02

本ドキュメントは、Issue/Pull Requestに付与するラベルの意味と、それらの間の状態遷移を定義する。
今回はラベルと状態遷移の**仕様のみ**を定義し、GitHub上へのラベル作成・GitHub Actionsによる自動付与は行わない（非対象範囲）。

---

## 1. 前提

* ラベルは `Issue`（`agent:ready` 等の着手系）と `Pull Request`（`agent:review` 以降のレビュー系）の両方に用いる。1つのタスク（管理ID）の進行に伴い、Issue側とPR側それぞれに該当ラベルが付与されることを想定する。
* 初期MVPでは、`agent:changes-required` になったタスクをClaude Codeが自動的に再着手することはない。人間が状況を確認し、`agent:working` へ戻す操作（または同等の指示）を行って初めて再着手する。
* すべてのラベルは、対応する状態が「誰の判断で始まり」「誰の判断で終わるか」を明確にするために存在する。人間が付与すべきラベルをAIが自己判断で付与してはならない。

---

## 2. ラベル定義

### `agent:ready`

| 項目 | 内容 |
| --- | --- |
| 意味 | Issueの内容が確定し、Claude Codeが着手してよい状態 |
| 誰が付けるか | 人間 |
| 誰が外すか | Claude Code（着手時、`agent:working` へ遷移する際に外す） |
| 次に遷移可能な状態 | `agent:working` |
| 許可される処理 | Claude Codeによる着手判断、実装計画の検討 |
| 禁止される処理 | このラベルが無い状態でのClaude Codeによる実装着手 |
| 人間確認 | 付与時に必要（Issue内容が実装可能なレベルで確定していることの確認） |

### `agent:working`

| 項目 | 内容 |
| --- | --- |
| 意味 | Claude Codeが実装作業を行っている状態 |
| 誰が付けるか | Claude Code |
| 誰が外すか | Claude Code（`agent:review` へ遷移する際、または `agent:blocked`/`agent:failed` へ遷移する際に外す） |
| 次に遷移可能な状態 | `agent:review`、`agent:blocked`、`agent:failed` |
| 許可される処理 | コード変更、テスト実行、featureブランチへのcommit・push、Pull Request作成 |
| 禁止される処理 | mainへの直接push、自動マージ、人間確認が必要な項目の自己判断での省略 |
| 人間確認 | 不要（ただし異常時は `agent:blocked`/`agent:failed` へ遷移し人間へ報告） |

### `agent:review`

| 項目 | 内容 |
| --- | --- |
| 意味 | 実装が完了し、レビュー（CI・OpenAIレビュー・人間レビュー）待ちの状態 |
| 誰が付けるか | Claude Code（Pull Request作成時） |
| 誰が外すか | レビュー結果に応じて次状態へ遷移する主体（`human:approved` の場合は人間、`agent:changes-required`/`human:review-required` の場合はレビュー実施主体） |
| 次に遷移可能な状態 | `human:approved`、`agent:changes-required`、`human:review-required`、`agent:blocked` |
| 許可される処理 | CIテストの実行、OpenAIレビューの実行、人間によるコードレビュー |
| 禁止される処理 | この状態のPRを人間の承認なしにマージすること |
| 人間確認 | 状態そのものは自動遷移可だが、最終的に `human:approved` へ進むには必ず人間の確認を要する |

### `agent:changes-required`

| 項目 | 内容 |
| --- | --- |
| 意味 | レビュー（CIまたはOpenAIレビュー）の結果、修正が必要と判定された状態 |
| 誰が付けるか | CI（テスト失敗時）、またはOpenAIレビュー結果が `CHANGES_REQUIRED` の場合にレビュー実施主体 |
| 誰が外すか | 人間（修正内容を確認し再実行を許可する場合） |
| 次に遷移可能な状態 | `agent:working`（人間が再実行を許可した場合のみ） |
| 許可される処理 | 人間によるレビュー内容の確認 |
| 禁止される処理 | Claude Codeによる自動的な再着手（初期MVPでは行わない）、このラベルのままでのマージ |
| 人間確認 | 必要（人間が再実行を許可するまで `agent:working` へは戻らない） |

### `human:review-required`

| 項目 | 内容 |
| --- | --- |
| 意味 | 主観判断・サービス仕様変更など、人間の判断が必須な状態 |
| 誰が付けるか | OpenAIレビュー（判定 `HUMAN_REVIEW` の場合）、またはPRテンプレートで「サービス仕様変更あり」等が明記されている場合にレビュー実施主体 |
| 誰が外すか | 人間 |
| 次に遷移可能な状態 | `human:approved`（人間が承認した場合）、`agent:changes-required`（人間が却下し修正を求める場合） |
| 許可される処理 | 人間による内容確認・試聴・目視確認等 |
| 禁止される処理 | このラベルが付いた状態をAIが自動的に `human:approved` へ進めること |
| 人間確認 | 必須 |

### `human:approved`

| 項目 | 内容 |
| --- | --- |
| 意味 | 人間が最終確認し、マージ可能と判断した状態 |
| 誰が付けるか | 人間 |
| 誰が外すか | 人間（マージ完了後にクローズ、または差し戻しが必要になった場合に `agent:changes-required` 等へ再遷移させつつ外す） |
| 次に遷移可能な状態 | （マージをもって完了。差し戻しが必要になった場合のみ `agent:changes-required`） |
| 許可される処理 | 人間によるマージ操作 |
| 禁止される処理 | AIによる自動マージ |
| 人間確認 | 必須（ラベル付与そのものが人間確認の記録） |

### `agent:blocked`

| 項目 | 内容 |
| --- | --- |
| 意味 | 前提不足・入力不備等により、Claude Codeが処理を継続できない状態（実装対象の情報不足、想定外のブランチ状態、conflict等） |
| 誰が付けるか | Claude Code（異常検知時） |
| 誰が外すか | 人間（状況を確認し、Issue/PRを修正した上で外す） |
| 次に遷移可能な状態 | `agent:working`（人間が前提を整え、再着手を許可した場合） |
| 許可される処理 | 人間による状況確認・Issue/PR内容の修正 |
| 禁止される処理 | Claude Codeによる自動的な再着手 |
| 人間確認 | 必須 |

### `agent:failed`

| 項目 | 内容 |
| --- | --- |
| 意味 | 実行時エラー・テスト失敗の継続等、処理そのものが失敗して終了した状態 |
| 誰が付けるか | Claude Code（実行が異常終了した場合） |
| 誰が外すか | 人間（原因を確認し、再実行を許可する場合） |
| 次に遷移可能な状態 | `agent:working`（人間が再実行を許可した場合） |
| 許可される処理 | 人間によるログ・エラー内容の確認 |
| 禁止される処理 | Claude Codeによる自動的な再実行 |
| 人間確認 | 必須 |

---

## 3. 状態遷移図

```mermaid
stateDiagram-v2
    [*] --> agent_ready: 人間がIssue内容を確定
    agent_ready --> agent_working: Claude Codeが着手

    agent_working --> agent_review: 実装完了・PR作成
    agent_working --> agent_blocked: 前提不足・想定外状態を検知
    agent_working --> agent_failed: 実行時エラー・テスト失敗が継続

    agent_review --> human_approved: レビューPASS・人間が承認
    agent_review --> agent_changes_required: CI失敗 または レビューCHANGES_REQUIRED
    agent_review --> human_review_required: 主観判断・サービス仕様変更等
    agent_review --> agent_blocked: レビュー中に異常を検知

    agent_changes_required --> agent_working: 人間が再実行を許可

    human_review_required --> human_approved: 人間が承認
    human_review_required --> agent_changes_required: 人間が却下・差し戻し

    agent_blocked --> agent_working: 人間が前提を整え再着手を許可
    agent_failed --> agent_working: 人間が原因確認の上、再実行を許可

    human_approved --> [*]: マージ完了
```

---

## 4. 状態遷移の要件（テキスト表現）

正常系（最短経路）:

```
agent:ready → agent:working → agent:review → human:approved
```

修正が必要な場合:

```
agent:review → agent:changes-required → (人間の再実行許可) → agent:working
```

人間判断が必要な場合:

```
agent:review → human:review-required
```

（その後 `human:review-required → human:approved` または `human:review-required → agent:changes-required`）

異常時:

```
(任意の自動処理状態: agent:working または agent:review) → agent:blocked または agent:failed
```

---

## 5. 初期MVPでの制約

* `agent:changes-required` からClaude Codeが自動的に再実行されることはない。人間が修正内容を確認し、再実行を許可した時点で初めて `agent:working` へ遷移する。
* `agent:blocked` / `agent:failed` からの復帰も同様に、人間の確認・許可が前提となる。
* いかなる状態からも、AIの判断のみで `human:approved` へ遷移することはない。
* マージ操作そのものは常に人間が行う。

---

## 6. Issue Form・Pull Requestテンプレートとの対応

* Issue Form（`.github/ISSUE_TEMPLATE/agent_task.yml`）の「管理ID」は、本仕様のラベルが付与される対象（Issue/PR）を横断して同一タスクを識別するために用いる。
* Issue Formの「受入条件」欄で定義される条件ID（`AC-01` 等）は、Pull Requestテンプレートの「受入条件ごとの結果」表、および `claude_implementation_report.schema.json` / `openai_review_result.schema.json` の `criterion_id` と対応する。
* Issue Formの「サービス仕様変更の可能性」で「あり」または「不明・要判断」が選ばれた場合、対応するPRは `agent:review` から自動的に `human:approved` へは進めず、`human:review-required` を経由する運用とする。
