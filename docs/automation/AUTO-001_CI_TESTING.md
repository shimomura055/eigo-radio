# AUTO-001 CIテスト基盤

管理ID: AUTO-001-03B

このドキュメントは、AUTO-001ブランチ(`automation/AUTO-001-clean`)専用のローカルCIテスト基盤について説明する。

リポジトリルート直下の`TESTING.md`は**作成しない**。ローカル`main`側(ER-003)に同名ファイルが既に存在しており、将来ER-003の未pushコミットが`origin/main`へ統合される際に衝突する可能性があるため。同じ理由で`run_project_regression.py`という名前も使っていない(AUTO-001-03A §12参照)。

---

## 1. 目的

GitHub Actions導入前に、このブランチだけで再現可能なローカルCIテスト基盤を用意する。

* CI専用のクリーンなPython仮想環境で実行できる
* 依存関係が`requirements-ci.txt`として固定・再現可能
* 実APIを呼ぶスクリプトを誤って実行しない
* 新しいテストファイルが未分類のまま追加された場合に停止する
* WindowsローカルとLinux(将来のGitHub Actions)で同じ`scripts/run_ci_tests.py`を使える

---

## 2. Python 3.12を利用すること

このCIテスト基盤は **Python 3.12** を前提とする(AUTO-001-03Aの調査により、コード自体の構文要件は緩いが、依存パッケージの安定した動作を優先してこのバージョンを選定した)。

```powershell
py -3.12 --version
```

Python 3.12が無い場合は先にインストールすること。他のバージョン(ローカルのグローバル環境が3.14系であっても)へ勝手に切り替えない。

---

## 3. 仮想環境の作成方法

AUTO-001 worktree内に、CI専用の仮想環境`.venv-ci`を作成する。メイン開発worktree(`eigo-radio`)の`.venv`やグローバルPython環境は使わない。

```powershell
py -3.12 -m venv .venv-ci
```

`.venv-ci/`は`.gitignore`に登録済みで、Gitの追跡対象外。

---

## 4. 依存関係のインストール方法

```powershell
.venv-ci\Scripts\python.exe -m pip install -r requirements-ci.txt
```

（Linux/mac相当: `.venv-ci/bin/python -m pip install -r requirements-ci.txt`)

`requirements-ci.txt`は、CIテスト実行に必要な直接依存5件(`numpy`, `scipy`, `openai`, `python-dotenv`, `google-genai`)とその推移依存を`==`で完全ピンしたものであり、本番コード・実験スクリプト全体の依存関係を表すものではない(詳細はファイル冒頭のコメントを参照)。

---

## 5. テスト実行コマンド

```powershell
.venv-ci\Scripts\python.exe scripts\run_ci_tests.py
```

（Linux/mac相当: `.venv-ci/bin/python scripts/run_ci_tests.py`)

どちらのOSでも同じ相対コマンド`scripts/run_ci_tests.py`を使う。スクリプト自身の場所からrepository rootを解決するため、実行時のカレントディレクトリには依存しない。

終了コード: 全対象テスト成功時は`0`。manifest検証エラー、未分類ファイル、いずれかのテスト失敗時は`0`以外。

---

## 6. manifestの役割

`ci_test_manifest.json`は、リポジトリルート直下でファイル名に`test`を含む(大文字小文字を区別しない)`.py`ファイル全てを、`include`(CI対象)か`exclude`(CI対象外)のどちらか一方に**過不足なく**分類するための台帳である。

さらに、`excluded_test_ids`により、`include`されたファイル**内の特定のテストメソッドだけ**を個別に除外できる。ファイル全体を`exclude`にするのではなく、「そのファイルの大半は安全に実行できるが、特定の1メソッドだけがクリーンなCI環境では構造的に成功しない」場合に使う。各エントリには以下を必須で記録する。

| フィールド | 内容 |
|---|---|
| `test_id` | 正確なunittestテストID(`モジュール.クラス.メソッド`形式)。実際の収集結果から取得したものだけを登録する(推測で書かない) |
| `reason` | 除外理由 |
| `exclusion_type` | `LOCAL_ARTIFACT_REQUIRED`(git管理外のローカル成果物が必要) / `PLATFORM_NEWLINE_DIFFERENCE`(改行コード差異) / `OTHER` |
| `platform` | `ALL`(常時除外)、または`sys.platform`の値(例: `win32`)を指定した場合はそのプラットフォームでのみ除外 |
| `duration` | `PERMANENT` / `TEMPORARY` |
| `follow_up_id` | 解決を追跡するフォローアップ管理ID |
| `release_condition` | 将来この除外を解除できる条件 |

---

## 7. テストをincludeへ追加する条件

* `unittest.TestCase`ベースで、外部API(OpenAI/Gemini/Azure等)を実際には呼ばない(依存性注入によるモック関数を使う等)
* APIキー・ネットワーク接続を必要としない
* 大量の生成物やバイナリ成果物を新たに作らない
* Windows/Linux双方で実行できる

新しく追加される`er0*_test_*.py`のような安全な単体テストファイルは、このリストへ追加する(その時点で`ci_test_manifest.json`の`include`にエントリを足す)。

---

## 8. テストをexcludeへ追加する条件

* ファイル名に`test`を含むが、実際には実APIを呼ぶ疎通確認・生成スクリプトである
* `unittest.TestCase`を継承しておらず、モジュールレベルで実行文を持つ
* APIキー・ネットワークが実際に必要

該当する場合は`exclude`へ理由とともに登録する。**手動の除外リストを覚えておく必要はなく、`ci_test_manifest.json`が唯一の正とする。**

---

## 9. 実APIスクリプトをCIで実行しないこと

現在`exclude`に登録されている6件(`test_api.py`, `generate_test.py`, `tts_test.py`, `tts_test_azure.py`, `tts_test_openai.py`, `tts_style_test.py`)は、実際にOpenAI/Gemini/Azureへ接続する。`scripts/run_ci_tests.py`はincludeされたファイルしかimportしないため、これらのファイルはCI実行中に一切importされない。

---

## 10. 未分類テストがある場合に失敗する理由

命名規則で自動的に安全性を判定することはできない(ファイル名だけでは実APIを呼ぶかどうか判断できない)。そのため、ファイル名に`test`を含む新しいファイルが追加され、`ci_test_manifest.json`のどちらにも登録されていない場合、`scripts/run_ci_tests.py`は**テストを実行せずに即座に失敗する**。これにより、「未分類のまま安全でないスクリプトがCIで実行されてしまう」事故と、「新しいテストが気づかれずCI対象から漏れる」事故の両方を防ぐ。

---

## 11. Windowsでの実行例

```powershell
py -3.12 -m venv .venv-ci
.venv-ci\Scripts\python.exe -m pip install -r requirements-ci.txt
.venv-ci\Scripts\python.exe scripts\run_ci_tests.py
```

---

## 12. Linuxでの実行例

```bash
python3.12 -m venv .venv-ci
.venv-ci/bin/python -m pip install -r requirements-ci.txt
.venv-ci/bin/python scripts/run_ci_tests.py
```

`excluded_test_ids`の`platform: "win32"`指定は、Linux上では適用されない。したがって`er002_test_editorial_v1_1b.py`の該当テスト(改行コード起因のsha256不一致)は、Linux実行時には除外されず**実行対象に含まれる**。AUTO-001-03A/03BではLinux環境での実行を検証していないため、GitHub Actions導入時にこのテストが実際に成功するか必ず確認すること。Linuxでも失敗した場合は「Windows固有の問題」という仮説が誤りだったことになるため、原因を再調査すること。

---

## 13. requirements-ci.txtの更新方法

1. `.venv-ci`を作り直す(`py -3.12 -m venv .venv-ci`)
2. 直接依存5件(`numpy`, `scipy`, `openai`, `python-dotenv`, `google-genai`)をインストールする
3. `scripts/run_ci_tests.py`を実行し、全テストが成功することを確認する
4. `python -m pip list --format=freeze`の出力全体で`requirements-ci.txt`を置き換える(ファイル冒頭のコメント欄も更新する: 最終検証日など)
5. 別のクリーンな`.venv-ci`を作り直し、`pip install -r requirements-ci.txt`だけで同じ結果を再現できることを確認してから確定する

既存環境の`pip freeze`をそのまま流用しない。必ずクリーンな`.venv-ci`から作り直す。

---

## 14. 外部APIを呼ばないこと

`scripts/run_ci_tests.py`は以下の安全策を実装している。

* テストは常に子プロセス(worker)で実行され、その子プロセスの環境変数にだけ`OPENAI_API_KEY=ci-placeholder-not-a-real-key`という明らかに無効なダミー値を設定する。本物のAPIキーは一切使用しない。このダミー値は、`openai`ライブラリが「クライアント生成時にAPIキーが無いとエラーになる」制約を回避するためだけに存在し、実際の通信には使われない
* この環境変数は子プロセスの中だけで有効であり、runnerを実行した親プロセス(シェル)の環境変数を変更・汚染することはない
* 子プロセスは実行開始時に`socket.socket.connect` / `socket.socket.connect_ex` / `socket.create_connection`を差し替え、外部ネットワークへの接続試行を全てエラーとして検出する。接続が試みられた場合、そのテストは成功として扱われず、runner全体が失敗として終了する
* 除外(`exclude`)されたファイルはimportすらされない

---

## 15. GitHub Actions導入は次Stageであること

AUTO-001-03Bの時点では、GitHub Actionsワークフローは作成していなかった。`scripts/run_ci_tests.py`は、ローカル実行と将来のGitHub Actions実行の両方で同じコマンドが使えるように設計されている。

---

## 16. GitHub Actionsワークフロー(AUTO-001-04A、ローカル実装のみ・未検証)

`.github/workflows/ci-test.yml`として、AUTO-001-04Aで最小構成のワークフローファイルを作成した。**この時点ではGitHubへpushしておらず、GitHub Actions上での実行確認は行っていない。** 実際のLinux runner上での動作確認・push・実行結果の確認はAUTO-001-04Bで行う。

### トリガー

* `push`: ブランチ`automation/AUTO-001-clean`のみ
* `pull_request`: ベースブランチ`main`のみ
* `main`ブランチへの直接pushはトリガーにしていない

### 実行環境

* `ubuntu-latest`、Python `3.12`(明示指定、`3.x`のような曖昧指定はしていない)
* 複数OS・複数Pythonバージョンのmatrixは使用していない

### Linuxでの実行コマンド

```bash
python -m pip --version
python -m pip install -r requirements-ci.txt
python -m pip check
python scripts/run_ci_tests.py
```

Windows固有の`.venv-ci\Scripts\python.exe`は使用しない。ワークフロー内のPythonは`actions/setup-python`が用意するシステムPythonをそのまま使う(GitHub Actions上では専用venvを作らない)。

### Secrets・環境変数

このワークフローはGitHub Secretsを一切使用・参照しない。`OPENAI_API_KEY`等の環境変数もワークフロー側では設定しない。ダミーの`OPENAI_API_KEY`は、AUTO-001-03Bで実装済みの通り`scripts/run_ci_tests.py`が子プロセス内だけで自動的に設定する(§14参照)。ワークフロー側で本物・ダミーいずれのAPIキーも設定する必要はない。

### 権限・外部Action

* `permissions: contents: read`のみ
* 使用する外部Actionは`actions/checkout`・`actions/setup-python`のみで、いずれも完全なcommit SHAで固定し、対応するリリースタグをコメントで記録している(取得元: `https://api.github.com/repos/<owner>/<repo>/releases/latest`および`/git/refs/tags/<tag>`、確認日2026-07-27)

### 未検証・要確認事項(AUTO-001-FU-002、AUTO-001-04Bで解明)

AUTO-001-03Bでは`er002_test_editorial_v1_1b.py`の1テストを`platform: "win32"`としてWindows限定で除外していた(改行コード起因のsha256不一致、follow-up: `AUTO-001-FU-002`)。AUTO-001-04Bで初めてこのブランチをGitHubへpushし、Linux runner上で実行した結果、このテストIDが実行され、**`FileNotFoundError`で失敗した**(詳細は§17参照)。原因を調査した結果、AUTO-001-04B-R1でこの分類は誤りだったと判明し、修正した。

---

## 17. Linux初回CI結果とテスト分類の修正(AUTO-001-04B / AUTO-001-04B-R1)

### 17.1 Linux初回CI(AUTO-001-04B)の結果

初回push(commit `aca5610`)によるLinux CI実行(run [30247789518](https://github.com/shimomura055/eigo-radio/actions/runs/30247789518))は以下の通り。

| ステップ | 結果 |
|---|---|
| Checkout | 成功 |
| Set up Python 3.12 | 成功 |
| Show pip version | 成功 |
| Install CI dependencies(`requirements-ci.txt`) | 成功 |
| Check installed dependencies(`pip check`) | 成功 |
| Run CI tests | **失敗** |
| Verify no tracked file changes | 未実行(前段が失敗したためスキップ) |

依存関係のインストールと`pip check`はLinux上でも成功し、`requirements-ci.txt`の再現性が確認できた。テスト実行(463件収集後実行)のうち、唯一失敗したのは以下のテストだった。

* テストID: `er002_test_editorial_v1_1b.V1_1A_UntouchedTests.test_a01_v1_1a_run_artifacts_on_disk_unchanged_since_pm1`
* エラー: `FileNotFoundError`
* 不足ファイル: `er002_output/A01/v1_1a/editorial_brief.json`

### 17.2 原因調査(AUTO-001-04B-R1)

このテストIDは、AUTO-001-03Bで既にWindows限定除外(`AUTO-001-FU-002`、`PLATFORM_NEWLINE_DIFFERENCE`)として登録していたテストと**同一のテストID**だった。詳しく調べると、このテストは`er002_output/A01/v1_1a/_pm1_analysis/artifact_sha256.json`に記録された6ファイル分のsha256を記載順に検証するループになっており、次のように2つの独立した問題を含んでいた。

1. **1番目のエントリ**(`er002_output/A01/v1_1a_fixed_facts.json`、Git追跡対象): Windows実行環境の`git`設定(`core.autocrlf=true`)により、`.gitattributes`で`-text`指定されていないためチェックアウト時にLF→CRLF変換され、Windowsでは凍結済みsha256と不一致になっていた。**Linux CIではこの1番目のエントリのsha256比較は一致し、CRLF起因の不一致は発生しないことを確認できた**(`AUTO-001-FU-002`の仮説を裏付ける結果)。
2. **2〜4番目のエントリ**(`editorial_brief.json`, `manifest.json`, `raw_responses.json`): これら3ファイルはGit管理外のローカル実験成果物であり、クリーンチェックアウトには一切存在しない。Linux CIではCRLF問題を通過した後、この2番目のエントリで`FileNotFoundError`が発生した。

結論として、このテストは**Windows固有の問題ではなく、全プラットフォームで構造的に成功し得ない**(2〜4番目のエントリが恒久的にクリーン環境で存在しないため)。`ci_test_manifest.json`の当該エントリを、`PLATFORM_NEWLINE_DIFFERENCE`/`win32`/`TEMPORARY`から、既存の2件と同じ`LOCAL_ARTIFACT_REQUIRED`/`ALL`/`PERMANENT`(follow-up: `AUTO-001-FU-001`)へ修正した。

### 17.3 同種テストの監査結果

上記の修正にあたり、`*Unchanged*`/`*Untouched*`系のテストクラス全て(`V1_0_UntouchedTests`、`FactCheckerUnchangedFromR3Tests`、`J1ArtifactsUnchangedTests`、`R1ArtifactsUnchangedTests`、`R2ArtifactsUnchangedTests`、`FactCheckerUnchangedTests`、`WriterConditionsUnchangedFromR3Tests`、`R3ArtifactsUnchangedTests`、`A01FactMeaningUnchangedTests`、`MasterSha256UnchangedTests`)を監査したが、他に構造的にCI実行不能なテストは見つからなかった。該当するテストはいずれも、(a) `os.path.exists`+`skipTest`で正しくガードされているか、(b) 参照先がGit追跡対象のファイルであることを個別に確認した。

### 17.4 除外はPASSではないこと

`excluded_test_ids`による除外は、そのテストが「成功した」ことを意味しない。`scripts/run_ci_tests.py`は除外したテストIDを実行対象から外し、実行結果の集計(`testsRun`/`passed`等)にも含めない。除外はあくまで「クリーンなCI環境では判定不能・実行不能」という区分であり、対象テストの妥当性そのものを保証するものではない。

### 17.5 修正後の期待件数

修正後、`excluded_test_ids`は3件全てが`platform: "ALL"`(常時除外)となり、Windows限定除外は0件になった。そのため、**WindowsとLinuxの期待件数は同一**になる(AUTO-001-04A策定時点で想定していた「Windows 461件・Linux 462件」という差分は解消された)。

| 環境 | 収集 | 常時除外 | プラットフォーム限定除外 | 実行 |
|---|---|---|---|---|
| Windows | 465 | 3 | 0 | 462 |
| Linux | 465 | 3 | 0 | 462 |

### 17.6 AUTO-001-FU-002の状態

`AUTO-001-FU-002`(Windows改行コード問題の仮説)は、Linux CIにより**事実関係としては確認・裏付けが取れた**(Linuxでは該当エントリのsha256比較が一致する)。しかし、このテストID自体は`AUTO-001-FU-001`(ローカル成果物依存)として恒久的に除外されるため、`AUTO-001-FU-002`単体の解消(Windows側の改行コード対応)はCI合否には直接影響しない。将来`editorial_brief.json`等をfixture化してこのテストIDの除外を解除する場合は、`AUTO-001-FU-002`の対応(`.gitattributes`の改行方針整備等)も合わせて必要になる。

---

## 18. ER-003テストのCI統合(AUTO-001-04D-R1)

### 18.1 背景

PR #1マージ後、ローカル`main`がER-003関連57コミットとAUTO-001基盤の両方を含む状態になった。AUTO-001-03B時点の`ci_test_manifest.json`はER-003側のテストファイルをまだ知らず、CI実行時に「未分類のtest候補ファイル34件」として検証エラーになった。AUTO-001-04D-R1は、この34件を監査・分類し、安全なテストだけをCI実行対象へ統合する作業である。

### 18.2 監査の2段階構成(重要な教訓)

最初の静的監査(コードを実行せず、目視・grepのみで判定する段階)は、**テストファイル自身に書かれた文字列リテラルのパス**を中心に行った。この段階では34件全てが「ファイル単位ではinclude可能」と判定され、実際に外部API・実TTS・実MFA呼び出しを含む7件のテストIDだけを個別除外候補とした。

しかし、分類確定後に実際に`scripts/run_ci_tests.py`をクリーンな`.venv-ci`で実行したところ、**静的監査では見つからなかった10件の新規エラー**(`FileNotFoundError`)が発生した。原因は、テストファイル自身にはパス文字列が書かれておらず、テストが呼び出す**実装モジュール側の辞書定数**(`er003_natural_source.P1B_RAW_ARTICLE_PATHS`、`er003_b2_summary.B2_INPUT_PATHS`)を経由して、Git管理外の成果物ファイルを間接的に読み込んでいたためである。

この経験から得られた教訓:

* **静的監査(テストファイル内の直接参照のgrep)だけでは、テスト対象コードの安全性を確定できない。**
* 実装モジュール側のパス定数・fixture・setUp経由の間接参照は、テストファイル自身のgrepでは見つからない。
* そのため、分類は「静的監査」と「クリーンな`.venv-ci`での実際の実行確認」の**両方**に基づいて初めて確定する。分類後は必ず実際にCIを実行し、新たなエラーが出ないことを確認すること。

### 18.3 新設した`exclusion_type`(AUTO-001-04D-R1-P2)

既存の`LOCAL_ARTIFACT_REQUIRED`/`PLATFORM_NEWLINE_DIFFERENCE`/`OTHER`では、ER-003側で新たに見つかった除外理由を正確に表現できなかったため、以下2種類を追加した(`scripts/run_ci_tests.py`の`_VALID_EXCLUSION_TYPES`が唯一のsource of truth)。

#### `LOCAL_TOOLCHAIN_REQUIRED`

Git管理外または標準CI環境に存在しない、ローカル専用のツールチェーン・実行環境・外部コマンドへの`subprocess`呼び出しを必要とするテスト。例: `mfa_tool/`(micromamba root prefix + SudachiPy隔離環境)、MFA(Montreal Forced Aligner)本体。

**解除条件**: 必要なツールチェーンを再現可能かつ安全なCI fixture/専用環境として正式導入する、またはsubprocess呼び出しをモック化した純粋関数テストへ分離する。

#### `EXTERNAL_SERVICE_DEPENDENCY`

実外部サービス(Azure Speech、Google Cloud TTS、AWS Polly等)への接続、外部サービス用SDK、実認証情報(`.env`内のクラウド認証情報等)、ログイン状態(gcloud ADCログイン等)のいずれかを必要とするテスト。

**解除条件**: 実サービスを呼ばないモック/fake/contract testへ再設計する、または標準CIとは分離された明示的な手動実行環境で運用する。

**重要**: この分類は「Secretsを与えれば標準CIで実行してよい」という意味では**ない**。標準CIは引き続き、Secrets不使用・実外部API不使用・外部ネットワーク接続禁止の方針を維持する。

### 18.4 テストID単位で除外した17件

ファイル全体を`exclude`にはせず、以下17件だけを`excluded_test_ids`で個別除外した(該当ファイル内の他のテストは引き続きCI実行対象)。

**`LOCAL_TOOLCHAIN_REQUIRED`(2件、`mfa_tool/`依存)**

* `er003_test_b1_p4d_audio.SudachiTokenizeIntegrationTests.test_real_pattern_a_full_pipeline_matches_expected_key_expressions`
* `er003_test_b1_p5a_audio.AsrReadingNormalizeTests.test_real_sudachi_pipeline_normalizes_kanji_text`

**`EXTERNAL_SERVICE_DEPENDENCY`(4件、実外部API・実認証情報依存)**

* `er003_test_b1_p5a_audio.AzureTtsCallFnIntegrationTests.test_minimal_real_call_returns_pcm_and_metadata`
* `er003_test_b1_p5a_audio.CheckEngineAvailabilityTests.test_azure_speech_available_in_this_environment`
* `er003_test_b1_p5b_audio.CheckGoogleCloudTtsAvailabilityTests.test_real_check_reports_available_after_adc_login`
* `er003_test_b1_p5b_audio.CheckAwsPollyAvailabilityTests.test_real_check_reports_unavailable_with_reason`

**`LOCAL_ARTIFACT_REQUIRED`(11件、Git管理外のローカル成果物依存)**

* `er003_test_b1_p6b_audio.Chunk03RegressionSpliceTests.test_mfa_boundary_approach_succeeds_where_rms_failed`(直接参照。`chunk03_ja.wav`未追跡)
* `er003_test_b2_summary.P2AOfficialRecordTests.test_b2_body_text_untouched_by_p2a`(間接参照。`er003_b2_summary.B2_INPUT_PATHS`経由、`b2_version_raw.md`未追跡)
* `er003_test_b2_summary_p2c.ApprovalMetadataTests.test_b2_body_sha256_unchanged`(同上)
* `er003_test_natural_source.A01DiffTests`の4メソッド(間接参照。`er003_natural_source.P1B_RAW_ARTICLE_PATHS`経由、`translated_en_raw.md`未追跡)
* `er003_test_natural_source.A02Add03IdenticalTests`の2メソッド(同上)
* `er003_test_natural_source.SavedArtifactTests`の2メソッド(同上。同クラスの他メソッドは`skipTest`ガード済みだがこの2件のみガードなし)

follow-upはいずれも既存の`AUTO-001-FU-001`(ローカル成果物依存の解消)へ追加登録した。**除外は「PASSした」ことを意味しない**(§17.4と同じ原則)。

### 18.5 34ファイルの分類方針(確定)

* 34ファイルは**ファイル単位では全てinclude可能**(実装コードの構造上、外部API・subprocessの呼び出しは全てテストメソッド内に限定されており、モジュールレベルでの危険な実行は無い)。
* ただし、上記17件のテストIDには環境依存(ローカルツールチェーン・実外部サービス・ローカル成果物)があり、個別除外が必要である。
* 最終的な分類の妥当性は、静的監査(このセクション§18.2前段)と、クリーンな`.venv-ci`での実行確認(§18.2後段)の**両方**で担保されている。「34ファイル全て無条件に安全」という単純化した理解はしないこと。

### 18.6 AUTO-001-04D-R1後の期待件数(Windows)

`scripts/run_ci_tests.py`の集計結果(サマリdict)は`testsRun`/`failures`/`errors`/`skipped`/`wasSuccessful`の5キーのみで構成される(コード上のsource of truth: `scripts/run_ci_tests.py`内の`summary`辞書生成箇所)。「成功件数」に相当する独立したキーは存在しない。`testsRun`はPythonの`unittest.TestResult.testsRun`そのものであり、**skipされたテストも含めて加算される**(skipは`testsRun`の内訳であり、加算対象外の別集計ではない)。

| 項目 | 件数 |
|---|---|
| test候補ファイル | 51 |
| include | 45 |
| exclude(ファイル単位) | 6 |
| 収集テストメソッド数 | 1593 |
| テストID単位除外(常時、実行対象外) | 20(既存3件 + 今回17件) |
| testsRun(1593件収集から20件を実行対象外とした残り) | 1573 |
| うちskipped(testsRunの内訳、加算ではない) | 14 |
| failures | 0 |
| errors | 0 |
| wasSuccessful | True |

正確な言い方: **1593件収集し、20件をテストID単位で実行対象外とし、残り1573件を`testsRun`として処理した。そのうち14件は`os.path.exists`+`skipTest`ガードにより正常にskipされ、failuresは0件・errorsも0件だったため、suite全体は成功(`wasSuccessful=True`)した。** 「1573件成功」という表現は使わない(そのような集計値はrunner自身が出力していないため)。

Linux側の期待件数は未検証(AUTO-001-04Bと同様、GitHub Actions実行時に別途確認が必要)。
