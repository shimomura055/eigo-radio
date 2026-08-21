# ER-006-MODEL-ROUTING-CONTRACT-01(追補)完了報告: API境界のFail-Closed強化

前回のER-006-MODEL-ROUTING-CONTRACT-01完了後、以下2点のギャップを指摘された:
(1) `require_model()`はモジュールimport時に一度だけ計算した値を使い回しており、
「API call直前」ではなかった。(2) leaf関数(`run_writer_with_technical_retry`等)
自体の既定値は旧Sol系譜のままで、新しいcallerがSSOTを迂回して直接これらの関数を
呼んだ場合、それを検出する仕組みが無かった。本タスクはこの2点を修正した。
新規有料API呼び出しは¥0(変更・testのみ)。

## 1. Production API boundaryでmodel未指定がFAILする証拠

[er006_model_routing_contract_01_boundary_test.py](https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er006_model_routing_contract_01_boundary_test.py)
で、本番コードが実際に使っているのと**全く同じ呼び出し式**(例:
`vfl01.run_writer_with_technical_retry(client, prompt, model=routing.require_model("B1_WRITER", routing.WRITER_MODEL))`)
を、SSOTの`WRITER_MODEL`を`None`/空文字へ一時的に汚染した状態で実行し、
「偽のclient(`FakeClient`、`responses.create`が呼ばれたら例外を送出する)」が
一度も呼ばれずに`ModelContractViolation`が先に送出されることを確認した
(Writer/Deviation Check/B1 Support/Key Phrase Selectorの4境界で確認)。

## 2. Sol指定がFAILする証拠

同じ`FakeClient`方式で、SSOTを`"gpt-5.6-sol"`へ一時的に汚染した状態でも同様に
確認した(Writer/Writer Fact Check/Deviation Check/B1 Support/Key Phrase
Selectorの5境界)。未知model(`"gpt-99-unknown"`)でも同様。

全10ケースいずれも`FakeClient.responses.create`は**一度も呼ばれなかった**
(=実際のAPIには絶対に到達しない状態を実証)。

## 3. 新規callerがSSOTを迂回できない仕組み

[er006_model_routing_contract_01_static_audit.py](https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er006_model_routing_contract_01_static_audit.py)
を全面改訂した。前回版は「既知の正しい行がまだそこにあるか」を確認するだけ
だったが、今回は**正規表現でleaf関数呼び出しパターンそのものをスキャン**する
方式へ変更した:

- 対象4ファイル(`er003_v1_n3_01_articles_generate.py`・
  `er003_v1_n3_01_scaffold_generate.py`・`er006_pool_pilot_01_support.py`・
  `er006_pool_pilot_01_research.py`)内の、`run_writer_with_technical_retry`/
  `run_deviation_check`/`make_fact_checker_fn`/`run_support_text`/
  `make_selector_fn`/`make_canonicalization_fn`への**全ての**呼び出し箇所を
  検出する(現在15件)。
- 各呼び出しに`model=`引数があり、かつその呼び出し直前400文字以内に
  `routing.require_model(`(またはそれを内部で呼ぶ既知のwrapper関数)への
  参照があることを検証する。
- **self-test**を同梱: 「modelなし」「Solを直書き」「正しくSSOT経由」の
  3パターンの偽コードを実際にこの検出ロジックへ通し、前者2つは正しく違反
  検出、後者は正しく非違反と判定されることを確認している(=検出ロジック
  自体が機能することの証明)。

これにより、**将来誰かが対象4ファイルへ新しいWriter/Support呼び出しを追加した
場合、SSOT経由のmodel指定を伴わなければこのtestがFAILする**(実際に、この
仕組みを作る過程で、Key Phrase Selector/Canonicalizationの2箇所がこの検査に
最初はひっかかり、修正が必要だった。詳細は5章)。

## 4. 既存legacy/translation経路への影響有無

**影響なし。** 各leaf関数の既定値(`model: str = MODEL`、Sol系譜)は一切変更
していない。実際に確認した:

```
run_writer_no_search              default model = gpt-5.6-sol
run_writer_with_technical_retry   default model = gpt-5.6-sol
run_deviation_check               default model = gpt-5.6-sol
b1s.run_support_text              default model = gpt-5.6-sol
a2gen.run_support_text            default model = gpt-5.6-sol
r3.make_fact_checker_fn           default model = gpt-5.6-sol
WRITER_MODEL(根本定数、無変更)     = gpt-5.6-sol
```

Translation pipeline・CEFR/spoken-first系の過去の実験タスク等、`model=`を
明示せず呼び出す30以上の既存呼び出し元は、今回のリファクタでも一切触れて
おらず、従来通りSolのまま動作する。

## 5. Regression test結果

| Test | 内容 | 結果 |
|---|---|---|
| [er006_model_routing_contract_01_test.py](https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er006_model_routing_contract_01_test.py) | Positive/Negative/Provider/Fallback(前回作成分) | 全PASS |
| [er006_model_routing_contract_01_static_audit.py](https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er006_model_routing_contract_01_static_audit.py) | SSOT迂回防止(今回全面改訂) | production call site 15件 + negative 4件 + self-test 3件、全PASS |
| [er006_model_routing_contract_01_boundary_test.py](https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er006_model_routing_contract_01_boundary_test.py) | API boundary fail-closed実証(今回新規) | 10ケース全PASS |
| er006_pool_pilot_01_ledger_test.py | 既存regression(前タスク分) | PASS(影響なし確認) |
| er006_preprod_hardening_01_validation_test.py | 既存regression(前タスク分) | 13件全PASS(影響なし確認) |

**今回の改修過程で実際に検出・修正したギャップ**: static auditを実装する
過程で、`run_key_phrase_selection`/`run_key_phrase_canonicalization`が
`model`引数(呼び出し元が事前計算した値をただ受け取るだけ)を取っており、
「このスコープ内でSSOT検証している証拠」が呼び出し側にしか無かったことが
判明した。`process`引数(`"B1_SUPPORT"`/`"A2_SUPPORT"`)を受け取り、関数内部で
`routing.require_model(process, routing.SUPPORT_MODEL)`を呼ぶ形へ変更し、
呼び出し元(`run_theme_scaffold`・`er006_pool_pilot_01_support.py`)も
`process=`を渡す形へ更新した。これにより検証がAPI call直前のこの関数内で
完結するようになった。

**あわせて実施した変更**: `er003_v1_n3_01_articles_generate.py`と
`er003_v1_n3_01_scaffold_generate.py`で、モジュールレベルに事前計算していた
`_WRITER_MODEL`/`_B1_SUPPORT_MODEL`等の変数を廃止し、各API呼び出しの
引数へ`routing.require_model(...)`を直接inlineで埋め込む形(または
`_b1_support_model()`/`_a2_support_model()`/`_writer_process()`という、
呼ばれる都度fail-closed検証を行う小さなヘルパー関数経由)へ変更した。

## 6. 新規API Cost

**¥0。** コード変更・regression test・static audit・boundary testのみで
完結させた(boundary testは`FakeClient`を使い、実際のAPIには一切到達しない
設計)。

## 受入条件チェック

| # | 内容 | 状況 |
|---|---|---|
| 1 | Production API boundaryでmodel未指定がFAILする証拠 | ✅ 1章 |
| 2 | Sol指定がFAILする証拠 | ✅ 2章 |
| 3 | 新規callerがSSOTを迂回できない仕組み | ✅ 3章 |
| 4 | 既存legacy/translation経路への影響有無 | ✅ 4章(影響なし) |
| 5 | Regression test結果 | ✅ 5章(全PASS) |
| 6 | 新規API Cost=¥0 | ✅ |

## リスク・注意点

- static auditの検出範囲は、正規表現による構文パターンマッチであり、
  完全な静的型検査ではない(極端に凝った書き方で回避される可能性はゼロでは
  ない)。ただし今回のcodebaseの実際のコーディングパターンに対しては、
  self-testで実証した通り機能する。
- boundary testはSSOTの値を`unittest.mock.patch.object`で一時的に汚染して
  確認しており、実際の本番実行環境の状態を変更するものではない(test関数の
  実行後は自動的に元の値へ復元される)。
- CURRENT_SPECのサービス仕様変更なし。前回タスクの決定(Writer/Support系を
  Lunaに固定)自体はそのまま維持している。
