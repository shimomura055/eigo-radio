# AUTO-001-03A CIテスト基盤・依存関係の現状調査

管理ID: AUTO-001-03A

本ドキュメントは調査と設計のみを目的とし、CIワークフロー・依存関係ファイル・テストrunnerの実装は含まない。

---

## 1. 調査対象コミットと前提

| 項目 | 値 |
|---|---|
| 作業worktree | `C:\Users\tensh\eigo-radio-auto-001-clean` |
| ブランチ | `automation/AUTO-001-clean` |
| 調査時HEAD | `5ae1ec6c2c168701e63e2a21a0e5bdcbef3ada3a`(AUTO-001-02完了直後、`8016193`を含む) |
| ベースブランチ・ベースコミット | `origin/main` / `d769d31dda4a60699eca0756858ed6d0cc527591` |
| `origin/main`との関係 | HEADは`origin/main`の2コミット先行・0コミット遅れ(AUTO-001-02の2コミットのみ) |
| `git status` | クリーン(調査開始時点) |
| AUTO-001以外の差分 | `git diff --stat origin/main..HEAD`はAUTO-001-01/02で追加した8ファイルのみ |
| 前提 | ER-003側の未pushコミット(ローカル`main`、57コミット程度)はこのブランチの履歴に含まれていない。本調査でもcherry-pick・checkout・マージのいずれも行っていない |

`TESTING.md`・`run_project_regression.py`はこの起点には存在しない(AUTO-001-02の調査で確認済み、§12で改めて評価する)。

---

## 2. 現在のテスト一覧

`git ls-files`でリポジトリ全体を確認した結果、"test"を含むファイル名は24件。このうちPythonファイルは16件で、以下の2グループに分かれる。

### 2.1 `er0*_test_*.py`パターンに一致するファイル(10件)

すべて`unittest.TestCase`ベース。

| ファイル | 行数 | テストクラス数 | 主な対象モジュール |
|---|---|---|---|
| `er002_test_common.py` | 1420 | 23 | `er002_common`, `er002_ab_anonymize`, `er002_runner`, `er002_rerun_bundle`, `er002_s3_config`, `er002_script_adapter`, `er002_v1_freeze` |
| `er002_test_editorial.py` | 598 | 14 | `er002_editorial_common`, `er002_editorial_runner`, `er002_editorial_angle_adapter`, `er002_gemini_client`(間接) |
| `er002_test_editorial_v1_1b.py` | 379 | 7 | `er002_editorial_common`, `er002_v1_1b_freeze`, `er002_v1_1b_fixtures` |
| `er002_test_ja_article_generation.py` | 286 | 9 | `er002_ja_article_generation`, `er002_ja_web_research_r3` |
| `er002_test_ja_free_markdown_restore.py` | 384 | 13 | `er002_ja_free_markdown_restore`, `er002_ja_master_imitation` |
| `er002_test_ja_free_markdown_restore_r2.py` | 342 | 13 | `er002_ja_free_markdown_restore_r2` |
| `er002_test_ja_master_imitation.py` | 529 | 13 | `er002_ja_master_imitation`, `er002_v1_2m_freeze` |
| `er002_test_ja_web_research_r3.py` | 682 | 13 | `er002_ja_web_research_r3` |
| `er002_test_ja_web_research_r4.py` | 582 | 18 | `er002_ja_web_research_r4`, `er002_ja_article_generation` |
| `er002_test_v1_2m_d1.py` | 297 | 14 | `er002_ja_master_imitation` |

外部API利用・生成物・依存関係(静的インポート解析および該当箇所の目視確認による):

| 項目 | 結果 |
|---|---|
| テストファイル自身が`openai`/`google`等を直接import | 0件(AUTO-001-01調査時と同じ) |
| **間接import(テスト対象モジュール経由)** | **10件全て**が`numpy`・`scipy`・`openai`・`python-dotenv`を間接的に要求。`er002_test_editorial.py`のみ追加で`google-genai`を要求(§8で詳細) |
| 実行時に実APIを呼ぶか | 呼ばない。API呼び出しが必要な箇所は、実クライアントではなく`call_fn`引数へ渡した自作の`mock_xxx`関数(依存性注入)で置き換えられている(`unittest.mock`はほぼ未使用で、DIパターンが主) |
| APIキーの必要性 | テスト実行時点では不要(クライアント生成は関数内で遅延実行されており、テストはそこへ到達しない設計)。ただし対象モジュールの**import自体**には上記パッケージのインストールが必須 |
| ファイル生成の有無 | `tempfile`使用箇所(`er002_test_common.py`、`er002_test_ja_master_imitation.py`)はOS一時ディレクトリのみに書き込み、リポジトリ内は変更しない |
| ネットワーク利用 | なし(`requests`/`urlopen`/`httpx`/`socket`のいずれも未使用。コード中の`https://example.com`等はテスト用の固定文字列) |
| 音声・画像・大容量成果物への依存 | `.wav`等のバイナリはリポジトリに存在しない(`.gitignore`対象)。参照する成果物は`er002_output/`等配下のJSON/テキストで、合計約2.0MB・205ファイル |
| Windows固有機能への依存 | コード本体には無し。`.venv/Scripts/python.exe`という実行例はdocstring内のコメントのみ(§11で詳細) |
| Linux GitHub Actionsランナーでの実行可能性 | コード上の障害は確認されなかった。ただし外部パッケージ未インストールのためこの調査環境では実行確認できていない(§13・§14) |
| CI標準セットへ含めるべきか | 10件とも該当(§3) |

### 2.2 `er0*_test_*.py`に一致しないPythonファイル(6件)

| ファイル | 実体 | 外部API | APIキー | ネットワーク |
|---|---|---|---|---|
| `test_api.py` | OpenAI Chat Completions APIへの疎通確認スクリプト。モジュールレベルで即座に`client.chat.completions.create(...)`を実行 | 呼ぶ(実行するだけで課金・ネットワークが発生) | 必要 | あり |
| `generate_test.py` | 記事生成の本番/実験runner(v9.0) | 呼ぶ | 必要 | あり |
| `tts_test.py` | Gemini-TTS音声生成スクリプト | 呼ぶ | 必要 | あり |
| `tts_test_azure.py` | Azure AI Speech音声生成スクリプト | 呼ぶ | 必要 | あり |
| `tts_test_openai.py` | OpenAI TTS音声生成スクリプト | 呼ぶ | 必要 | あり |
| `tts_style_test.py` | STYLE_PREFIX比較用の軽量ハーネス(`tts_test.py`相当を再利用) | 呼ぶ | 必要 | あり |

いずれも`unittest.TestCase`を継承しておらず、`if __name__ == "__main__"`ガードなしでモジュールレベルの実行文を持つものもある(`test_api.py`)。「テスト」を名前に含むが実体は手動API疎通確認・生成スクリプトであり、回帰テストスイートの対象ではない。

---

## 3. CI標準セット候補

`er0*_test_*.py`パターンに一致する現在の10ファイルすべてを標準セット候補とする。

```text
er002_test_common.py
er002_test_editorial.py
er002_test_editorial_v1_1b.py
er002_test_ja_article_generation.py
er002_test_ja_free_markdown_restore.py
er002_test_ja_free_markdown_restore_r2.py
er002_test_ja_master_imitation.py
er002_test_ja_web_research_r3.py
er002_test_ja_web_research_r4.py
er002_test_v1_2m_d1.py
```

理由: いずれも`unittest.TestCase`形式、実APIを呼ばない設計(依存性注入によるモック)、ネットワーク・APIキー不要、生成物は一時ディレクトリのみ、リポジトリ変更なし。ER-001向けの`er0*_test_*.py`形式テストは現時点で存在しない(AUTO-001-01の調査と一致)。

---

## 4. CIから除外するテスト

```text
test_api.py
generate_test.py
tts_test.py
tts_test_azure.py
tts_test_openai.py
tts_style_test.py
```

---

## 5. 除外理由

| ファイル | 除外理由 |
|---|---|
| `test_api.py` | モジュールレベルで実OpenAI APIを呼ぶ。import(実行)しただけで課金・ネットワークアクセスが発生し、CI環境にAPIキーが無ければ即失敗する |
| `generate_test.py` | 記事生成の実行スクリプト。回帰テストではなく生成物を作るための本番/実験ツール |
| `tts_test.py` / `tts_test_azure.py` / `tts_test_openai.py` | いずれも実音声合成APIを呼ぶ生成スクリプト。APIキー必須、音声ファイル(バイナリ)を生成する |
| `tts_style_test.py` | `tts_test.py`相当のロジックを再利用し実API呼び出しを行う比較ハーネス |

これら6件は`er0*_test_*.py`という命名規則に従っていないため、§7で推奨する収集方式(グロブパターンによる自動探索)では**自動的に**除外される。手動の除外リストを別途保守する必要はない。

---

## 6. テスト収集方式の比較

| 方式 | 誤って実APIテストを実行するリスク | 新しいテストの追加漏れ | 保守性 | Windows/Linux互換性 | 実行結果の分かりやすさ | GitHub Actionsとの相性 | 外部依存の少なさ |
|---|---|---|---|---|---|---|---|
| ①`python -m unittest`でモジュール明示列挙 | 低い(列挙したものしか実行しない) | **高い**(新規テスト追加時に列挙の更新漏れが起こりやすい。ER-003-P2Jで実際に発生した対象範囲の食い違い〈P2H 1032件 vs P2I 660件〉の原因もこの方式) | 低い(列挙リストの保守が必要) | 良好 | 良好(明示的) | 普通 | 良好(stdlibのみ) |
| ②`unittest discover`+ファイル名パターン | **低い**(命名規則に従わないファイルは自動的に対象外。§5の6件が実証済み) | **低い**(命名規則に従えば新規ファイルは自動的に対象へ含まれる) | **高い**(パターン文字列1つの保守のみ) | 良好(`pathlib.Path.glob`はクロスプラットフォーム) | 良好(`--json-summary`等と組み合わせ可能) | **良好**(単一コマンド・単純な終了コード) | 良好(stdlibのみ) |
| ③専用runnerスクリプト | ②に準ずる(②のロジックをラップする前提) | ②に準ずる | 高い(discover呼び出し・終了コード・JSON出力を1箇所に集約できる) | 良好(自身の場所からrepository rootを解決すれば実行ディレクトリに非依存) | **高い**(collected/passed/failed/skippedを構造化して報告できる) | **高い**(exit codeとJSON summaryをCIのstep outputへ渡しやすい) | 良好(stdlibのみで実装可能) |
| ④manifest(対象ファイル一覧)を別ファイルに記載 | 低い | 高い(①と同様、manifestの更新漏れリスクがある) | 低い(命名規則で代替可能な情報を二重管理することになる) | 良好 | 普通 | 普通 | 良好 |
| ⑤pytest等の外部テストランナー導入 | 低い | 低い(discoveryはpytestも同等に可能) | 高い機能を持つが新規の外部依存が増える | 良好 | 高い | 高い | **低い**(新規パッケージ導入が必要。現状10ファイル全てが`unittest.TestCase`で書かれておりpytest固有機能は使っていない) |

比較結果: 本リポジトリはすでに全テストが`unittest.TestCase`で統一されており、命名規則(`er0*_test_*.py`)だけで実API呼び出しスクリプトと単体テストを機械的に分離できることが§2.1/§2.2で実証されている。①(手動列挙)は既知の実績として不具合を起こしており不採用。④(manifest)は命名規則で代替可能な情報を二重管理するだけで、③に対する優位性がない。⑤(pytest)は新規の外部依存を増やすだけで現状のテストコードに対する明確な利点がない。

---

## 7. 推奨するテスト入口

**②(`unittest discover` + `er0*_test_*.py`パターン)を③(専用runnerスクリプト)でラップする方式**を推奨する。

* discoveryパターン: `er0*_test_*.py`(固定・変更不要)
* 実行方法: `python <runner>.py`
* runnerの責務: repository root解決 → `unittest.TestLoader().discover()`実行 → 収集数0件は失敗扱い → 終了コード(0=成功、非0=失敗) → `--json-summary`オプションで結果をJSON出力(CI連携用)
* 除外対象の管理: 命名規則のみで行い、手動の除外リストは持たない

この設計は、後続コミットに存在する`run_project_regression.py`(ER-003-P2K/P2L)と機能的に同じ考え方だが、**そのままコピーはせず、AUTO-001側で独立して新規実装する**(理由は§12・§15で詳述)。

---

## 8. 必要なPython依存関係

### 8.1 現在の実行環境で確認された事実

調査環境(`python --version` = `3.14.6`、実行ファイル: `C:\Users\tensh\AppData\Local\Python\pythoncore-3.14-64\python.exe`、venvではないグローバル環境、`pip list`の出力は`pip`のみ)には、`numpy`・`scipy`・`openai`・`google`(google-genai)・`boto3`・`python-dotenv`のいずれもインストールされていない。

### 8.2 静的インポート解析による分類

Python標準の`ast`モジュールで、各テストファイルが再帰的にimportするローカルモジュール(`er00*.py`)を辿り、到達する外部パッケージを機械的に集計した(実行時のバージョン確認ではなく、ソースコード上のimport文からの静的解析)。

| 区分 | パッケージ | 根拠 |
|---|---|---|
| Python標準ライブラリ(インストール不要) | `os`, `sys`, `json`, `re`, `io`, `time`, `math`, `glob`, `shutil`, `tempfile`, `subprocess`, `unittest`, `dataclasses`, `typing`, `types`, `inspect`, `hashlib`, `wave`, `array`, `html`, `random`, `unicodedata`, `platform`, `datetime`, `pathlib`, `argparse`, `__future__` 等 | 全10ファイルのimport文を確認 |
| **CIテスト実行に必須(10ファイル全て)** | `numpy`, `scipy`, `openai`, `python-dotenv`(`import dotenv`) | `er002_common.py`(numpy/scipy)、`er002_editorial_angle_adapter.py`(openai/dotenv)等がモジュールトップレベルでimportしており、10ファイルすべてが直接または間接にこれらへ到達する(静的解析で確認済み。§8.3に個別結果を記載) |
| CIテスト実行に必須(10ファイル中1ファイルのみ) | `google-genai`(`from google import genai`) | `er002_test_editorial.py`が`er002_gemini_client`を直接importするため |
| 本番コード実行に必須 | `numpy`, `scipy`, `openai`, `python-dotenv`, `google-genai` | 上記と同じパッケージ群。本番実行時はさらに有効なAPIキー(`OPENAI_API_KEY`, `GEMINI_API_KEY`等)とネットワーク接続が必要になるが、パッケージ自体はCIテスト実行時と同一 |
| 外部API実行時のみ必要 | `azure-cognitiveservices-speech`相当(`import azure...`) | `tts_test_azure.py`(§5で除外)のみが使用。CI標準セットには含まれない |
| 実験スクリプトだけで必要 | 上記`azure`系。`google-genai`・`openai`・`numpy`・`scipy`・`dotenv`も`er001b*.py`系の実験スクリプト(ER-001の話者比較実験群)から使われているが、これらは本番コード側でも使用するパッケージと重複しており、実験専用の追加パッケージは無い | `er001b*.py`は今回のCI標準セットにもAUTO-001-02の対象にも含まれない。パッケージ選定への影響は無い |
| 現在の`origin/main`には不要 | `boto3` | リポジトリ全体を検索したが、`boto3`のimportは1件も存在しない。AUTO-001-01の調査記録(§5)にあった「`boto3`等」という記述は、モジュール名`er002_s3_config.py`から連想された推測であり、実際には同ファイルはS3関連の設定値を保持するのみでboto3を呼び出していない。**本ドキュメントでこの認識を訂正する** |

### 8.3 テストファイルごとの内訳(静的解析結果)

| テストファイル | 到達する外部パッケージ |
|---|---|
| `er002_test_common.py` | dotenv, numpy, openai, scipy |
| `er002_test_editorial.py` | dotenv, **google**, numpy, openai, scipy |
| `er002_test_editorial_v1_1b.py` | dotenv, numpy, openai, scipy |
| `er002_test_ja_article_generation.py` | dotenv, numpy, openai, scipy |
| `er002_test_ja_free_markdown_restore.py` | dotenv, numpy, openai, scipy |
| `er002_test_ja_free_markdown_restore_r2.py` | dotenv, numpy, openai, scipy |
| `er002_test_ja_master_imitation.py` | dotenv, numpy, openai, scipy |
| `er002_test_ja_web_research_r3.py` | dotenv, numpy, openai, scipy |
| `er002_test_ja_web_research_r4.py` | dotenv, numpy, openai, scipy |
| `er002_test_v1_2m_d1.py` | dotenv, numpy, openai, scipy |

**構造上の注意点**: `openai`・`google-genai`クライアントは関数内で遅延生成される設計(`client = OpenAI()`は関数の中)だが、`from openai import OpenAI`等のimport文自体はモジュールのトップレベルにある。同様に`er002_common.py`の`numpy`/`scipy`もトップレベルimportである。そのため「実際にはAPIを呼ばないテストだから、パッケージも不要」という判断はできない。**importが通るかどうかの時点で、これら5パッケージが必須になる。**

---

## 9. 推奨する依存関係管理方式

比較した候補と評価は以下の通り。

| 候補 | 評価 |
|---|---|
| `requirements.txt`(全体を1本化) | 現状、本番コード・実験スクリプト・CIテストの依存関係が明確に分離整理されていないため、いきなり全体を1本化すると`azure`等CIに不要なパッケージも含めてしまうリスクがある |
| `requirements-ci.txt`(CI専用の最小セット) | **採用を推奨**。§8で機械的に特定した5パッケージ(`numpy`, `scipy`, `openai`, `python-dotenv`, `google-genai`)だけに限定でき、レビューしやすい。既存の生成スクリプト群(実験・本番生成)の依存関係整理は別スコープとして切り離せる |
| `pyproject.toml` | 将来的な移行先として妥当だが、本リポジトリはこれまでパッケージング設定を一切持っておらず、ビルドシステム・バージョニング等の追加検討事項を伴う。CIを動かすためだけに導入するには過剰 |
| 複数ファイルへの分離(例: `requirements-ci.txt` + `requirements-audio.txt` + `requirements-experimental.txt`) | 将来的にAUTO-001の対象範囲がCI以外(本番実行環境の依存関係整理等)へ広がった場合には有効だが、§8.2の分析の通り現時点では「CI用」と「本番用」のパッケージ集合がほぼ完全に一致しており、分離のメリットが薄い |
| 当面は依存関係ファイルを作らない | CIを導入する以上、再現可能なインストール手順が必須であり、この案は採用できない |

**推奨: `requirements-ci.txt`をAUTO-001-03Bで新規作成し、CIテスト実行に必要な最小パッケージ(5件)だけをピン留めする。** 全体最適化(本番生成コード全体の依存関係整理、`azure`等の扱い)は、AUTO-001の対象範囲外として別タスクに切り出す。

既存環境全体の`pip freeze`をそのまま採用する案は、本調査環境にこれらのパッケージが1つもインストールされていないため、そもそも採用不可能である(§8.1)。

バージョン固定方針: CI再現性を優先し、`==`による完全一致ピンを推奨する。具体的なバージョン番号は、AUTO-001-03B実装時点でのインストール確認と併せて決定する(本調査ではパッケージを1つもインストールしていないため、現時点で動作確認済みの具体的なバージョン番号を提示できない)。

---

## 10. Pythonバージョン方針

### 10.1 コードが要求する構文上の最低バージョン

静的に確認した限り、`match`文・walrus演算子(`:=`)・`@dataclass(slots=True)`等、3.10以降でなければ動作しない構文は使用されていない。

`list[str]`のようなbuiltin generics(3.9+相当の構文)や`int | None`のようなUnion構文(3.10+相当の構文)は複数箇所で使われているが(`er002_ab_anonymize.py`, `er002_common.py`, `er002_editorial_common.py`等8ファイル)、**これらを使う全てのファイルに`from __future__ import annotations`が付与されている**ことを確認した。この宣言があるファイルでは、アノテーションは実行時に評価されず文字列として保持されるため、構文的な下限バージョンを引き上げない(古いPythonでも構文解析自体は通る)。

したがって、コード自体が要求する構文上の最低バージョンは実質的に**Python 3.7相当**(`from __future__ import annotations`が使えるバージョン)まで下げられるが、これは形式的な下限であり、実運用上の判断材料としては§10.2を優先すべきである。

### 10.2 実運用上の推奨

| 項目 | 内容 |
|---|---|
| 現在のローカルPythonバージョン | 3.14.6(2026年時点の最新に近いバージョンとみられる) |
| GitHub Actions候補バージョン | `actions/setup-python`でインストール可能な安定版(例: 3.11・3.12系)を推奨。3.14系は登場から日が浅く、`numpy`/`scipy`等のホイール提供状況が不安定な可能性がある(本調査では未検証) |
| 最低対応バージョンを固定できる根拠 | コード構文自体には強い制約がない(§10.1)ため、下限は「利用する外部パッケージ(numpy・scipy・openai・google-genai)が公式にサポートする最低バージョン」で決まる。本調査ではこれらのパッケージを1つもインストールしていないため、正確な最低サポートバージョンはAUTO-001-03Bでのインストール確認時に確定させる必要がある |
| 複数バージョンでのCIが必要か | **不要と判断する**。本アプリケーションはライブラリとして配布されるものではなく、単一の実行環境(ローカル+GitHub Actions)で動けばよいプロダクトコードである。初期MVPでは単一バージョンのみを対象とし、不要なmatrixは導入しない方針を維持する |

---

## 11. WindowsとLinuxの差異

| 項目 | 内容 |
|---|---|
| コード内のWindows固有パス | 10件のテストファイル、および到達する本番モジュールに`C:\`、`os.sep`直接比較、`ntpath`等の使用は確認されなかった |
| パス結合方法 | `os.path.join`または`/`区切りの文字列リテラルを使用しており、`os.path.join`使用箇所はクロスプラットフォームで問題ない。文字列リテラルの`/`区切りはWindows・Linux双方で有効なパス区切りとして機能する |
| docstring内の実行例 | 10ファイス全てに`.venv/Scripts/python.exe -m unittest <module> -v`というWindows venv構造前提のコメントが残っている。コードではなくコメントのため実行に影響はないが、AUTO-001-03BでTESTING.md相当のドキュメントを新規作成する際は、Linux向けの表記(単に`python`、または`.venv/bin/python`)に読み替える必要がある |
| `subprocess`経由の外部コマンド呼び出し | `er002_test_common.py`が`git check-ignore`をsubprocessで呼び出している。GitHub Actionsの標準ランナー(Ubuntu)には`git`がプリインストールされており、`actions/checkout`でリポジトリを取得していれば問題なく動作する見込み(実機での動作確認は未実施) |
| 改行コード(`.gitattributes`) | `er002_v1_2m_masters/`・`er002_v1_2m_restore_briefs/`配下の一部ファイルに`-text`(改行変換無効)が指定されており、現在の7テストファイルが`hashlib`でsha256整合性を検証している。`-text`はプラットフォームに関係なくgitに解釈されるため、Linux runnerでも同じ設定が有効になり、`core.autocrlf`のようなOS依存設定に左右されにくい設計になっている。ただし本調査ではLinux環境での実際のcheckout・sha256一致は検証していない(§14) |
| 総合評価 | コードレベルでのWindows/Linux互換性リスクは低いと判断する。ドキュメント表記の読み替えのみ対応すれば、CI導入の技術的障害にはならない見込み |

---

## 12. 後続runnerの評価

`TESTING.md`・`run_project_regression.py`は、ローカル`main`の`7032643`(ER-003-P2K)で新規追加され、`1f9475c`(ER-003-P2L)で`TESTING.md`が改訂されている。指示に従い、`git show 90d7bb9:<path>`で読み取り専用抽出し(worktree外の一時ファイルへ出力、`checkout`・`copy`・`cherry-pick`は行っていない)、内容を評価した。

### 12.1 `run_project_regression.py`(128行)の評価

| 評価項目 | 内容 |
|---|---|
| ER-003固有の内容を含むか | モジュール冒頭のコメント(12行程度)に「ER-003-P2K」「ER-003-P2J」という管理ID、および過去の不具合(P2H 1032件 vs P2I 660件の対象範囲食い違い)の経緯説明が含まれる。**コードの実装本体(関数群)自体はER-002/ER-003いずれにも固有の処理を持たない汎用的なロジック**(`resolve_repo_root`, `discover_test_files`, `count_tests_in_suite`, `build_summary`, `run`, `main`) |
| `origin/main`に存在しないテストを参照するか | `DEFAULT_PATTERN = "er0*_test_*.py"`という変数値自体はER-002/ER-003を問わず汎用的なパターンで、このAUTO-001ブランチでもそのまま使える(現状では`er002_test_*.py`10件だけにマッチする)。コード内にer003固有のパスやモジュール名のハードコードは無い |
| 現在のAUTO-001ブランチでそのまま利用可能か | 技術的には(ファイルをコピーするだけなら)動作すると見られるが、**冒頭コメントがER-003-P2J/P2Kという、このブランチの履歴に存在しないコミットを前提に説明されており、読者が混乱する**。また「対象: `er002_test_*.py`(ER-002) + `er003_test_*.py`(ER-003)」という説明文言は、現状`er003_test_*.py`が0件であるこのブランチの実態と合わない |
| 汎用部分だけを再設計する価値があるか | ある。self-locating repo root、discover+globパターンによる収集、0件検出時の失敗扱い、`--json-summary`によるCI連携という設計方針自体は優れており、AUTO-001でも踏襲する価値がある(§7の推奨に反映済み) |
| そのままコピーすべきでない理由 | (1) ER-003側の未pushコミットの成果物であり、AUTO-001-03Aの非対象範囲である57コミットの内容を実質的に持ち込むことになる。(2) コメント中の「ER-003-P2J/P2K」等の経緯説明が、このブランチの履歴やドキュメント体系と整合しない。(3) 「ER-002 + ER-003」という現状と異なるscope説明を含んだまま導入すると、AUTO-001側のCIドキュメントとして不正確になる |
| 新規に独立実装した方がよいか | **推奨する**。同じ設計思想(discover+glob、self-locating root、exit code規約、`--json-summary`)を踏襲しつつ、ER-003関連の経緯コメントを含まない、AUTO-001の実際のscope(現状は`er002_test_*.py`のみ)に即したコメントで書き直す |

### 12.2 `TESTING.md`(67行)の評価

| 評価項目 | 内容 |
|---|---|
| ER-003固有の内容を含むか | 「Historical test evidence vs. current project-wide regression(ER-003-P2L)」という節がまるごとER-003-P2J/P2L固有の内容(`er003_output/p2j/`、`er003_test_p2j_investigate.py`、過去の件数P2H=1032件等)。「Scope」節も「対象: `er002_test_*.py`(ER-002) + `er003_test_*.py`(ER-003)」という記述を含む |
| `origin/main`に存在しないテストを参照するか | 上記の通り、`er003_test_*.py`・`er003_output/p2j/`・`er003_test_p2j_investigate.py`はいずれもこのAUTO-001ブランチに存在しない |
| 現在のAUTO-001ブランチでそのまま利用可能か | 不可。「Historical test evidence」節はこのブランチに存在しないテストクラス・成果物を前提としており、そのまま導入すると存在しないものを参照するドキュメントになる |
| 汎用部分だけを再設計する価値があるか | ある。「Reporting rules」節(targeted testsとproject-wide regressionを分離して報告する、collected件数とpassed件数を混同しない、手動列挙を証跡として使わない等の禁止事項)は、ER-002/ER-003を問わず有効な一般原則であり、AUTO-001版でも採用する価値が高い |
| そのままコピーすべきでない理由 | `run_project_regression.py`と同様。ER-003固有の節を含んだまま導入すると、存在しないテスト・成果物を参照する不正確なドキュメントになる |
| 新規に独立実装した方がよいか | **推奨する**。「Command」「Scope」「Reporting rules」の骨格は踏襲しつつ、「Historical test evidence」節はAUTO-001の対象外として除外し、Scopeの説明を現状(`er002_test_*.py`のみ)に合わせて書き直す |

### 12.3 総合結論

両ファイルは**参考資料としては価値が高いが、正式仕様としてそのまま採用しない**。AUTO-001-03Bでは、これらの設計思想(自動探索・self-locating root・exit code規約・JSON summary・targeted testsとproject-wide regressionの分離)を踏襲した上で、ER-003固有の経緯・scope記述を含まない形で独立に新規実装することを推奨する。

---

## 13. 実行した安全なテスト

以下の条件を満たす範囲で試験実行を行った。

* 使用したPython: `python --version` → `Python 3.14.6`、実行ファイル `C:\Users\tensh\AppData\Local\Python\pythoncore-3.14-64\python.exe`(システムのグローバル環境、venvではないことを`sys.prefix == sys.base_prefix`で確認)
* 本worktree内に新規venvは作成していない
* メイン開発worktree(`C:\Users\tensh\eigo-radio`)の`.venv`は参照していない(パス的にも別ディレクトリであり、上記の通りグローバル環境を使用)
* パッケージのインストールは一切行っていない(`pip list`はインストール前・後とも`pip`のみ)

実行内容: `python -m unittest <module> -v`で3ファイル(`er002_test_ja_web_research_r4`, `er002_test_ja_article_generation`, `er002_test_common`)のimportを試行した。いずれも**依存パッケージ不足によるImportErrorで即座に失敗**した(トレースバックで到達不能を確認)。

```text
er002_test_ja_web_research_r4 → ModuleNotFoundError: No module named 'dotenv'
er002_test_ja_article_generation → (同じ er002_ja_free_markdown_restore 経由の連鎖、dotenv不足で失敗)
er002_test_common → ModuleNotFoundError: No module named 'numpy'
```

実行前後で`git status --porcelain`はいずれも変化なし(tracked/untrackedファイルへの影響なし)を確認した。

---

## 14. 実行できなかったテスト

**§3で候補とした10ファイル全て**が、現在の調査環境では実行できなかった。

理由: §8で機械的に特定した通り、10ファイル全てがimport時点で`numpy`・`scipy`・`openai`・`python-dotenv`(うち`er002_test_editorial.py`はさらに`google-genai`)を必要とするが、現在の調査環境にはこれらが1つもインストールされていない。指示によりパッケージインストールを行っていないため、実行を無理に行わず、上記3ファイルでの代表的な失敗確認に留めた。

この制約は本調査の対象範囲(調査・設計のみ)においては許容されるが、**AUTO-001-03Bで`requirements-ci.txt`を作成し、実際にパッケージをインストールした環境で全10ファイルの実行成功を確認する作業が別途必要**である。

---

## 15. AUTO-001-03Bの実装案

| 項目 | 内容 |
|---|---|
| 作成または変更すべきファイル | (1) `requirements-ci.txt`(新規、§9) (2) `run_project_regression.py`相当のrunnerスクリプト(新規・独立実装、§7・§12) (3) `TESTING.md`相当のドキュメント(新規・独立実装、AUTO-001の実態に即したScope記述、§12) (4) `.github/workflows/ci-test.yml`(AUTO-001-01設計書§14の案をベースに新規、AUTO-001-03Bの範囲かAUTO-001-04以降にするかは要判断、§16) |
| CI標準テストコマンド | `python run_project_regression.py`(ファイル名は§16のユーザー判断事項) |
| CI対象テストの選定方法 | `unittest discover`+`er0*_test_*.py`グロブパターン(手動列挙・manifestは使わない) |
| 除外対象の管理方法 | 命名規則による自動除外のみ。手動の除外リストは持たない(§5・§6) |
| 使用するPythonバージョン | 3.11または3.12系を推奨(単一バージョン、matrix化しない)。正式決定はAUTO-001-03Bでのインストール確認と合わせて行う(§10) |
| 依存関係ファイルの形式 | `requirements-ci.txt`(pip形式のフラットなファイル、`pyproject.toml`は見送り、§9) |
| 最初に固定するパッケージ | `numpy`, `scipy`, `openai`, `python-dotenv`, `google-genai`(5パッケージ、§8) |
| バージョン固定方針 | `==`による完全一致ピン。具体的なバージョン番号はAUTO-001-03Bでのインストール確認時に決定(現時点では未検証のため提示できない) |
| ローカルでの実行方法 | `pip install -r requirements-ci.txt` → `python run_project_regression.py` |
| GitHub Actionsでの実行方法 | `actions/checkout` → `actions/setup-python`(バージョン固定) → `pip install -r requirements-ci.txt` → `python run_project_regression.py --json-summary <path>` |
| 想定実行時間 | 10ファイル・軽量なロジック検証中心と推測されるが、本調査ではパッケージ未インストールのため実測できていない。AUTO-001-03Bでの実行確認時に実測することを推奨 |
| 失敗時の停止条件 | 終了コード非0(収集0件、または1件でも失敗/エラー)をCI失敗として扱う。§7の設計を踏襲 |

---

## 16. ユーザー判断が必要な項目

* **`run_project_regression.py`/`TESTING.md`という名称をAUTO-001側でも踏襲するか、別名にするか**: 独立実装するとしても、ER-003側の未pushコミットが将来`origin/main`へマージされた際、同名ファイルが存在すると内容の突き合わせ・コンフリクト解消が必要になる。「将来の合流を見据えて同一名称・同一インターフェースにする」か「衝突回避のため別名(例: `run_ci_tests.py`)にする」かはプロダクト運用上の判断であり、本調査では決定していない
* **Pythonバージョンの正式決定**: 3.11系か3.12系か、あるいは他のバージョンにするかは、AUTO-001-03Bでの実際のパッケージインストール確認(numpy/scipy/openai/google-genaiの対応状況)を踏まえてユーザー承認のもとで決定する必要がある
* **各パッケージの具体的な固定バージョン番号**: 本調査ではパッケージを1つもインストールしていないため提示できない。AUTO-001-03Bでインストール確認を行いながら決定することを推奨するが、その際の許容バージョン範囲(最新安定版を使うか、特定の枯れたバージョンを使うか)はユーザー判断が必要
* **`.github/workflows/ci-test.yml`をAUTO-001-03Bに含めるか、AUTO-001-04以降に分離するか**: 依存関係ファイル・runnerの実装と、実際にGitHub Actions上で動かす実装は、レビュー粒度の観点で分離した方が安全な可能性がある
* **`azure`等、CI標準セットに含めないパッケージを含む生成スクリプト群(`tts_test*.py`等)の依存関係整理**: 今回のAUTO-001-03Aでは対象外としたが、いずれ本番運用の依存関係整理が必要になった際に、別タスクとして着手するかどうかの判断が必要
* **ER-001向け回帰テストの不在**: AUTO-001-01時点から未解消。ER-001関連のCI対象テストをどうするかは引き続き未確定

---

## 17. リスク

* パッケージを1つもインストールしていないため、§8の依存関係リストはソースコードの静的解析に基づく**理論上必要なパッケージの集合**であり、実際にインストール・実行して初めて判明する不足(間接依存のサブパッケージ、OS別ホイールの有無等)がある可能性がある。AUTO-001-03Bでの実インストール確認が必須
* Python 3.14という非常に新しいローカル環境と、CIで使う想定のPython 3.11/3.12系との間に差異があり、ローカルでの動作確認とCIでの動作が一致しない可能性がある
* `-text`指定によるsha256整合性テスト(§11)は、実際にLinux runner上でcheckoutして初めて安全性を確定できる。本調査はコード・設定の点検のみで、実機検証は行っていない
* 命名規則(`er0*_test_*.py`)による自動除外は、将来何者かが実API呼び出しを含むスクリプトをこの命名規則に**誤って**合わせてしまった場合に、安全装置として機能しなくなるリスクがある(ドキュメント上の運用ルールとして明記する必要がある)
* `run_project_regression.py`/`TESTING.md`を独立実装することで、将来ER-003側の同名ファイルが`origin/main`へマージされた際に、2つの異なる実装の統合作業が発生する可能性がある(§16)

---

## 18. 工数見積もり

AUTO-001-03B(`requirements-ci.txt`・runnerスクリプト・`TESTING.md`相当ドキュメントの新規実装、パッケージインストールによる実動作確認)は、本調査で対象ファイル・依存パッケージ・設計方針がほぼ具体化されているため、**1日程度**を見積もる。GitHub Actionsワークフロー本体の実装(§16で分離可否が未確定)を含める場合は、追加で半日〜1日程度を見込む。
