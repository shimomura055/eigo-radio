# AUTO-001-06-02-02 半自動Implementer(MVP-1.5)接続契約

管理ID: AUTO-001-06-02-02

本ドキュメントは、AUTO-001-06-01で生成されるtask bundle(`AUTO-001-TASK-BUNDLE-V1`、`scripts/implementer_launcher.py`)を人間経由でClaude Codeへ渡す半自動MVP-1.5について、入力envelopeと計画結果(plan result)の契約・検証基盤を定義する。

MVP-1.5でClaude Codeが行うのは「入力検査」と「実装計画の提示」だけである。コード変更・worktree/branch作成・git操作・GitHub write・Implementerの自動起動は一切行わない。

---

## 1. 全体像

```
task bundle(AUTO-001-TASK-BUNDLE-V1)
        │  (Launcherが生成、人間がartifactをダウンロード)
        ▼
execution envelope(新規、本タスクで追加) ── 人間が作成し、task bundleと共にClaude Codeへ渡す
        │
        ▼
Claude Code(MVP-1.5: 入力検査 + 計画のみ)
        │
        ▼
plan result(新規、本タスクで追加) ── Claude Codeが返す機械可読な計画結果
        │
        ▼
人間が承認するまでコード変更は一切行われない(stop_point: PLAN_ONLY)
```

task bundle・execution envelope・plan resultは互いに別のJSONファイルであり、1つに統合しない。task bundleの決定性(AUTO-001-06-01で確認済みのbyte単位再現性)を壊す変更は一切行っていない。

---

## 2. execution envelope

`docs/automation/schemas/implementer_execution_envelope.schema.json`

task bundleを受け取った人間が、Claude Codeへ渡す直前に作成する、実行ごとのmetadata。`additionalProperties: false`、全17 field必須。

| field | 型/制約 |
|---|---|
| `schema_version` | string, semver(`^[0-9]+\.[0-9]+\.[0-9]+$`)、初版`"1.0.0"` |
| `logical_task_key` | string, `^[0-9a-f]{64}$`(§4参照) |
| `execution_id` | string, `^exec_[0-9a-f]{12}_a[1-9][0-9]*_[A-Za-z0-9]{8,32}$`(§5参照) |
| `attempt` | integer, minimum 1 |
| `repository` | string, `owner/repo`形式 |
| `base_sha` | string, 小文字hex40桁(envelope作成時に改めて取得した値。task bundleの`generated_from_main_sha`をそのまま信用しない) |
| `issue_number` | integer, minimum 1 |
| `management_id` | string, non-empty |
| `task_bundle_schema_version` | string, `const: "AUTO-001-TASK-BUNDLE-V1"` |
| `task_bundle_sha256` | string, 小文字hex64桁(task bundleファイルの実byte列から計算) |
| `task_bundle_file` | string, `const: "task_bundle.json"` |
| `prohibited_paths` | array of string, minItems 1, uniqueItems true(glob pattern、§6参照) |
| `prohibited_operations` | array, minItems 1, uniqueItems true, 固定enum20種(§6参照)、辞書順必須 |
| `timeout_seconds` | integer, minimum 1, maximum 86400 |
| `stop_point` | string, `const: "PLAN_ONLY"` |
| `expected_output` | string, `const: "PLAN_RESULT_JSON"` |
| `human_approval_required` | boolean, `const: true` |

---

## 3. plan result

`docs/automation/schemas/implementer_plan_result.schema.json`

Claude Codeがコード変更前に返す機械可読JSON。`additionalProperties: false`、全21 field必須。MVP-1.5のplan resultは「受理され、計画が完了した」場合の形だけを表現する(拒否系は§8のValidationResultでのみ表現し、plan resultとしては表現しない)。

| field | 型/制約 |
|---|---|
| `schema_version` | string, semver、初版`"1.0.0"` |
| `execution_id` | envelopeと同じpattern。envelope.execution_idと一致必須 |
| `attempt` | integer, minimum 1。envelope.attemptと一致必須 |
| `logical_task_key` | envelope.logical_task_keyと一致必須 |
| `management_id` | envelope.management_idと一致必須 |
| `input_task_bundle_sha256` | Claude Codeが実際に読んだtask bundleのSHA-256の自己申告(echo)。envelope.task_bundle_sha256と一致必須 |
| `input_base_sha` | Claude Codeが前提としたbase SHAの自己申告(echo)。envelope.base_shaと一致必須 |
| `connection_decision` | string, `const: "ACCEPTED"` |
| `execution_status` | string, `const: "PLAN_COMPLETED"` |
| `next_action` | string, `const: "HUMAN_APPROVAL_REQUIRED"` |
| `summary` | string, minLength 1 |
| `current_problem_understanding` | string, minLength 1 |
| `implementation_plan` | array of string, minItems 1 |
| `proposed_changed_files` | array、各要素`path/change_type(added\|modified\|deleted\|renamed)/purpose/service_spec_impact(NONE\|POSSIBLE\|YES\|UNKNOWN)`。path重複禁止。`claude_implementation_report.schema.json`の`changed_files`と同一の型を使用(§9) |
| `proposed_test_plan` | array of string, minItems 1 |
| `prohibited_change_detected` | boolean, `const: false` |
| `missing_information` | array of string |
| `unresolved_items` | array of string |
| `risks` | array of string |
| `human_confirmation_items` | array of string |
| `generated_at` | string, RFC3339のうちUTC(Z終端)のみ許容 |
| `self_reported` | boolean, `const: true` |

MVP-1.5では`connection_decision`/`execution_status`/`next_action`/`prohibited_change_detected`/`self_reported`がすべて固定値であるため、AUTO-001-06-02-01の監査で提案していた`allOf`/`if`/`then`による条件付きcross-field検証は不要になった(値が1通りしかないため条件分岐が意味を持たない)。これはより単純な設計であり、意図的な簡略化である。

---

## 4. logical_task_key

repository・issue_number・management_id・task_bundle_sha256から決定的に生成する、同一タスクを識別するキー。

```python
logical_task_key = sha256(
    canonical_json_bytes([repository, issue_number, management_id, task_bundle_sha256])
).hexdigest()
```

- `canonical_json_bytes`は`json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))`(UTF-8エンコード、末尾改行なし)。
- `scripts/implementer_launcher.py`の`canonical_json_bytes()`と**同一の直列化規則**だが、そちらは`dict[str, Any]`専用の型注釈になっているため、本モジュール(`scripts/implementer_connection_contract.py`)は同一規則を持つ4行の関数を独立して持つ(Launcher本体をimportせず、両モジュールを疎結合に保つための意図的な複製)。
- `TASK_BUNDLE_SCHEMA_VERSION_CONST`(本モジュール)が`scripts.implementer_launcher.TASK_BUNDLE_SCHEMA_VERSION`と一致し続けることは、テスト(`LauncherNoDriftTests`)で確認する。
- 実装は`build_logical_task_key()`(`scripts/implementer_connection_contract.py`)。同一入力から常にbyte単位で同一の64桁小文字hex文字列を返すことをテストで確認済み。

---

## 5. execution_id

```
exec_{logical_task_keyの先頭12文字}_a{attempt番号}_{8〜32文字の英数字}
```

- 正規表現: `^exec_[0-9a-f]{12}_a[1-9][0-9]*_[A-Za-z0-9]{8,32}$`
- envelope単体の検証時に、次の内部整合性を追加で検査する(intra-document cross-field):
  - `exec_`の直後12文字が、同じenvelopeの`logical_task_key`の先頭12文字と一致すること。
  - `_a`の直後の数値が、同じenvelopeの`attempt`と一致すること。
- 自動生成機能は実装していない(生成主体は人間、またはMVP-1.5より後で導入されるツール)。
- task bundle本体には一切含めない(AUTO-001-06-01の決定性を壊さない)。

### attemptの単調増加について

- `attempt`はschema上「1以上の整数」としてのみ制約されている(§2)。
- 想定運用は、同一`logical_task_key`に対する再試行のたびに、人間が1、2、3…と手動で増加させることである。
- MVP-1.5には永続的なexecution record store が存在しないため、ある`attempt`の値が本当に「その`logical_task_key`における前回の値より大きい」ことを機械的に保証する手段はない。単調増加は**運用上の約束であり、コードによる強制ではない**。
- `attempt`は再試行回数を表す識別情報の一部にすぎず、それ自体は重複起動防止(duplicate detection、§8参照)の機構ではない。
- この制約は、将来execution record store(実行履歴を永続化する仕組み)を導入する際に解決すべき候補の1つとして記録する。

---

## 6. prohibited_paths / prohibited_operations とpolicy検査

### prohibited_operations(固定enum、20種、辞書順)

```
AMEND, BRANCH_CREATE, BRANCH_DELETE, COMMENT_WRITE, CREDENTIAL_MODIFICATION,
FILE_WRITE, FORCE_PUSH, GIT_COMMIT, GIT_PUSH, GIT_STAGE, ISSUE_WRITE,
LABEL_WRITE, MAIN_DIRECT_CHANGE, MERGE, PR_CREATE, REBASE, SECRET_ACCESS,
WORKFLOW_DISPATCH, WORKTREE_CREATE, WORKTREE_DELETE
```

envelope.prohibited_operationsの配列順序は辞書順(Pythonの文字列比較順)であることを、JSON Schemaの`enum`とは別にPython側で追加検査する(JSON Schema自体には配列要素の順序を制約する標準的な語彙がないため)。

**重要な設計上の限界**: `prohibited_operations`はMVP-1.5では**宣言的な契約要素**であり、plan resultには「実際に行った操作」を記録するfieldが存在しないため、自動検証はしていない。人間がClaude Codeとのやり取りの中で、これらの操作が実際に行われていないことを確認する運用に依存する。

### prohibited_paths(glob pattern)とpolicy検査

`proposed_changed_files[].path`が`prohibited_paths`のいずれかのglob patternに一致した場合、`validate_plan_result()`は`REJECTED_POLICY`を返す。

- 外部ライブラリを追加せず、Python標準ライブラリの`fnmatch.fnmatchcase()`を使用する(`fnmatch.fnmatch()`ではなくcase版を使うのは、`fnmatch()`が`os.path.normcase()`でOS依存の大文字小文字正規化を行うため、Windows上のテスト実行とLinux上のGitHub Actions実行とで判定結果が変わってしまうことを避けるため)。
- path separator(区切り文字)は、比較前にWindows(`\`)・POSIX(`/`)いずれも`/`へ正規化する。
- 大文字小文字は`fnmatchcase()`によりcase-sensitiveに扱う(OSのデフォルト規則に依存しない)。
- パストラバーサル対策として、正規化後のpathを`/`で分割し、`..`という要素が1つでも含まれる場合は、`prohibited_paths`との一致とは無関係に無条件で`REJECTED_POLICY`(`POLICY_PATH_TRAVERSAL`)とする。

**glob照合の既知の限界(MVP-1.5)**: `fnmatch`は一般的なglobライブラリ(shellのglobや`pathlib.Path.glob`等)と異なり、`*`がpath separatorを含めて任意の文字列に一致する(`fnmatch.translate('*')`は`.*`相当になる)。すなわち`fnmatch`の内部では`*`と`**`が区別されず、どちらを書いても実質的に「区切りをまたいで何にでも一致する」パターンとして扱われる。一般的なglob実装が持つ「`*`は単一階層のみ、`**`は複数階層(再帰的)に一致する」という厳密な階層意味は、本契約の`prohibited_paths`では**保証されない**。これはMVP-1.5における既知の限界であり、コードの挙動を変更する対応は行っていない。運用上は、`prohibited_paths`に書いたパターンが意図より広く一致する可能性があることを踏まえて設計・レビューする必要がある。

---

## 7. cross-document検査とdecisionの優先順位

`scripts/implementer_connection_contract.py`は2つの検証エントリポイントを提供する。

- `validate_envelope(envelope, *, task_bundle_raw_bytes, task_bundle)`: envelope単体のschema検証 → task bundleとのsource一致検査 → task bundleとのhash一致検査、の順。
- `validate_plan_result(plan_result, *, envelope)`: plan result単体のschema検証 → envelopeとのsource一致検査 → envelopeとのhash一致検査 → policy検査、の順。

いずれも**fail-closed**であり、ある段階でエラーが見つかった時点で後続の検査は行わずに停止する。優先順位は以下の通り固定する。

```
SCHEMA > SOURCE > HASH > POLICY
```

- **SCHEMA**: 単一文書内の構造的な不正(required欠落・型不一致・enum/const不一致・pattern不一致・min/maxItems違反・uniqueItems違反・additionalProperties違反)、およびenvelope自身のexecution_id/logical_task_key/attemptの内部整合性(§5)。
- **SOURCE**: 文書間の同一性の不一致(repository・issue_number・management_id・execution_id・attempt・logical_task_keyが一致しない)。
- **HASH**: 文書間のハッシュ/echo値の不一致(task bundleの実byte hash、plan resultが自己申告するinput_task_bundle_sha256/input_base_sha)。
- **POLICY**: `prohibited_paths`/パストラバーサルによる変更予定ファイルの禁止。

envelope↔task bundleのcheck項目: repository / issue_number / management_id / task_bundle_schema_version / task bundle実ファイルSHA-256 / logical_task_key(実際のtask bundle内容から再計算した値との一致)。

plan result↔envelopeのcheck項目: execution_id / attempt / logical_task_key / management_id / input_task_bundle_sha256 / input_base_sha。

---

## 8. validation result契約

拒否系はplan resultとしては表現せず、`ValidationResult`という別の型でのみ表現する。

```python
@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    connection_decision: str
    error_codes: tuple[str, ...]
    error_messages: tuple[str, ...]
```

`connection_decision`(`ConnectionDecision` enum):

```
ACCEPTED, REJECTED_SCHEMA, REJECTED_HASH, REJECTED_SOURCE, REJECTED_POLICY
```

`REJECTED_DUPLICATE`はAUTO-001-06-02-01の監査で候補として提示したが、本タスクの指示により**予約値としても追加していない**(`Decision.WOULD_BLOCK_DUPLICATE`のような未到達enumメンバーとしての存在すら持たせない)。これはLauncherの設計方針とは異なる、本タスク固有の意図的な決定である。

**duplicate detection(重複起動防止)について明記する**: MVP-1.5では、重複起動防止の実処理は一切実装していない。`ConnectionDecision`のenumに`REJECTED_DUPLICATE`が存在しないことはその直接的な帰結である。`logical_task_key`・`execution_id`・`attempt`はあくまで「同一タスク・同一試行を識別するための情報」であり、これらのfieldが存在すること自体は重複起動を検出・防止する機構ではない(例えば同じ`task_bundle_sha256`に対して複数のenvelope/execution_idを人間が並行して作成すること自体を防ぐ仕組みはない)。二重実行の回避は、現時点では完全に人間の運用(同じタスクに対して複数の実行を同時に走らせない、という人間の注意)に依存している。Implementerの自動起動へ進む場合は、本タスクとは別のタスクで、重複起動防止の実処理を設計・実装する必要がある。

---

## 9. 既存schemaとの関係

`claude_implementation_report.schema.json`・`openai_review_result.schema.json`は**一切変更していない**(git diffで確認、後述)。

- `proposed_changed_files`の各要素は、`claude_implementation_report.schema.json`の`changed_files`と**同一の型**(`change_type`: `added|modified|deleted|renamed`、`service_spec_impact`: `NONE|POSSIBLE|YES|UNKNOWN`)を用いる。
- `self_reported: true`固定という表現は、`claude_implementation_report.schema.json`の`self_reported`と同じ意味・同じ固定値を踏襲する。
- `risks`/`human_confirmation_items`をstring配列とする形も、既存2schemaの対応fieldと型を一致させている。
- `generated_at`のdate-time表現は`openai_review_result.schema.json`の`reviewed_at`と同じ考え方(ISO 8601)だが、本タスクでは「UTC(Z終端)のみ」というより厳密なサブセットに限定した(既存2schemaの`reviewed_at`は`format: date-time`のみでタイムゾーンを限定していないが、これは既存schemaへの変更ではなく、新規schema側だけの独自の制約である)。

---

## 10. 手書きJSON Schemaサブセットの実装範囲

`jsonschema`パッケージは`requirements-ci.txt`に存在せず、本タスクでも追加していない。`scripts/implementer_connection_contract.py`は、`issue_preflight_validator.py`と同様に、JSON Schemaの**全機能ではなく必要なサブセットだけを手書きで実装**している。

### 実装した範囲

- `required`(必須fieldの欠落検知)
- `additionalProperties: false`相当(全field必須構成のため、required集合以外のkeyをすべて未知fieldとして拒否)
- `type`(string/integer/boolean/array/objectの判定。`bool`が`int`のサブクラスである点はintegerチェックで明示的に除外)
- `enum`/`const`
- `pattern`(正規表現、`re.match`)
- `minimum`/`maximum`(integer)
- `minLength`(string)
- `minItems`/`uniqueItems`(array)
- cross-field(envelope内部のexecution_id整合性、plan result↔envelopeの文書間整合性)
- RFC3339 UTC(Z終端、小数秒任意)の正規表現ベースの検証

### 対応していない主なJSON Schema機能

- `$ref`によるschema分割・参照
- `oneOf`/`anyOf`/`not`
- `patternProperties`
- `prefixItems`(tuple validation)
- `contains`
- 汎用的な`format`検証(date-time以外のformat、例: `uri`、`email`)
- `multipleOf`
- 文字列の`maxLength`
- 配列内オブジェクトの特定subfieldだけを対象とした一意性制約(例: `proposed_changed_files[].path`の重複禁止)。JSON Schemaの`uniqueItems`はitem(オブジェクト全体)の完全一致しか判定できず、`path`というsubfieldだけを取り出した一意性は表現できない。
- 正式なJSON Schemaの`$schema`/`$id`解決やmeta-schema検証

**`proposed_changed_files`のpath一意性についての補足**: `implementer_plan_result.schema.json`の`proposed_changed_files`は、`description`内に「path重複禁止」という契約を文章で明記しているが、これはJSON Schemaの構造的な制約(`uniqueItems`等)としては表現していない。実際の重複検知は、`scripts/implementer_connection_contract.py`の`_validate_plan_result_schema()`内でPythonコードとして追加実装している(`SCHEMA_CHANGED_FILES_DUPLICATE_PATH`)。つまり本契約は「schemaファイルの説明文」と「Pythonバリデータの追加制約」の組み合わせによって実現されており、schemaファイル単体(を将来`jsonschema`等の汎用ライブラリで読み込んだ場合)だけではpath重複を検出できない。これは実装不良ではなく、**意図したschema/validator間の差異**である。

`docs/automation/schemas/implementer_execution_envelope.schema.json`・`implementer_plan_result.schema.json`自体は正式なJSON Schema(draft 2020-12)の構文で記述しており、将来`jsonschema`ライブラリ等で読み込むこと自体は可能だが、本タスクのPythonバリデータはこれらのファイルを実行時に読み込んで解釈する汎用インタプリタではなく、**同じ内容を意味的に一致させて手書きしたもの**である(`SchemaJsonFilesShapeTests`で、schemaファイルの`required`集合とPythonバリデータの`_ENVELOPE_REQUIRED_FIELDS`/`_PLAN_RESULT_REQUIRED_FIELDS`が一致することだけを確認しており、両者の完全な意味的同一性を機械的に保証するものではない)。

---

## 11. 想定利用フロー(MVP-1.5、実装はしない)

1. 人間がLauncher workflowのartifactからtask bundle(`task_bundle.json`)をダウンロードする。
2. 人間が`base_sha`(改めて取得した`origin/main`のSHA)・`execution_id`・`attempt`等を含むexecution envelopeを作成する。
3. 人間がtask bundleとenvelopeをClaude Codeへ渡す。
4. Claude Codeは`validate_envelope()`相当の検査を経て(または人間が事前に検査した結果を踏まえて)、計画を作成し、plan resultを返す。
5. 人間が`validate_plan_result()`でplan resultを検査し、`ACCEPTED`であることを確認した上で、内容を目視でも確認する。
6. 人間が実装着手を承認する場合、次のタスク(MVP-1.5より後)で初めてworktree作成・実装・テスト・commitへ進む。

本タスクではこのフロー自体のworkflow化・自動化は行っていない。

---

## 12. 安全境界

- `scripts/implementer_launcher.py`・`.github/workflows/*`・既存2schema(`claude_implementation_report.schema.json`/`openai_review_result.schema.json`)は変更していない。
- 本モジュールはGitHubへの読み書き、Claude Code/Implementerの起動、git操作(worktree/branch/commit/push)を一切行わない。受け取ったdictを検証し、結果を返すだけの純粋関数群である。

### commitしない実ファイル

リポジトリへ**commitしないもの**:

- 実際のGitHub Issueから生成されたtask bundle(`task_bundle.json`実体)
- 実際のexecution envelope(具体的なIssue番号・repository・base_sha等を含むもの)
- 実際のplan result(具体的な実装計画・変更予定ファイルを含むもの)
- 実際の`execution_id`を含む実行成果物一般
- 実行ログ

commit対象となるのは、schema(`docs/automation/schemas/*.schema.json`)・example(`docs/automation/examples/*.example.json`、架空のmanagement ID `AUTO-999-DEMO01`を用いたもの)・設計文書・validator(`scripts/implementer_connection_contract.py`)・test(`auto001_test_implementer_connection_contract.py`)・`ci_test_manifest.json`だけである。

---

## 13. 公式フルテストrunnerの確認状況

### 事実

- `python scripts/run_ci_tests.py`を実行したところ、manifest検証エラーで停止した。
- エラー内容: `除外指定されたテストIDが収集結果に存在しません(存在しないテストIDが登録されている可能性があります): er002_test_ja_master_imitation.PdfBenchmarkStatusTests.test_pdf_copy_sha256_matches_source`
- 本タスクの変更を一切含まない別worktree(`eigo-radio-auto-001-clean`)でも、同一worktreeで同じコマンドを実行したところ、**文言が完全に一致するエラー**が発生した。
- `scripts/run_ci_tests.py`の内部関数(`load_manifest`・`validate_manifest_structure`・`discover_candidate_files`・`classify_files`・`collect_test_ids`)を、上記エラーが発生する`compute_exclusions`より手前まで個別にread-only実行したところ、新規テストファイル`auto001_test_implementer_connection_contract.py`は収集処理で76個のテストIDとして認識された(全体の収集テストID数916件のうちの76件)。
- AUTO-001関連の`auto001_test_*.py`9ファイルを`python -m unittest`で合同実行した結果、906件全てが成功した(exit code 0)。
- `ci_test_manifest.json`ベースの公式フルテストrunnerが、`er002_test_*.py`(ER-002)等を含む全体スイートとして成功することは、**ローカル環境では未確認のまま**である。

### 未確認の仮説

- 上記manifest検証エラーの原因は、PDFベンチマークの生成物(何らかのローカルファイル)がこの環境に存在しないことである可能性がある。
- ただし、この原因の特定・調査自体は本タスク(AUTO-001-06-02-02)の対象範囲外であり、実施していない。

「既存環境要因であることが確定した」とは判断していない。上記はあくまで、本タスクの変更が原因ではないことを示す再現性の確認と、未確認のまま残る事実・仮説の区別である。
