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

今回のAUTO-001-03Bでは、GitHub Actionsワークフローは作成していない。`scripts/run_ci_tests.py`は、ローカル実行と将来のGitHub Actions実行の両方で同じコマンドが使えるように設計されているが、`.github/workflows/*.yml`の追加、GitHub Secretsの登録、PR時の自動起動等は次Stage(AUTO-001-04以降)で扱う。
