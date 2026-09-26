# Recon: Advanced Vocab v2 Production組み込み方式(W-1)

管理ID: ADVANCED-VOCAB-V2-PRODUCTION-RESTORE-01

## 1. Production Advanced正式経路

- 生成本体: `er003_v1_n3_01_advanced_adaptation_generate.py::generate_advanced_adaptation()`。
  `build_prompt(ja_article_text)`で単一のuser messageを構築し、
  `vfl01.run_writer_with_technical_retry(client, prompt, max_attempts=2, model=..., developer=...)`
  へ渡す。
- 呼び出し元: `er012_e_family_entertainment_two_level_runner_01.py::run_writer_stage()`が
  `adv_gen.generate_advanced_adaptation(ja_text, client=client)`を呼ぶ。

## 2. retry/fallback/regenerationが同一promptを使うことの確認

- **構造Gate retry**: `vfl01.run_writer_with_technical_retry()`は`for attempt in
  range(1, max_attempts+1)`ループ内で毎回同一の`user_message`(=`build_prompt()`の戻り値、
  1回だけ構築されループ外で固定)を`run_writer_no_search()`へ渡す。プロンプトの再構築は
  行わない(er003_v1_en_direct_vfl_01_generate.py L410-431)。
- **Ledger deviation MAJOR時の再生成**: `er012_e_family_entertainment_two_level_runner_01.py`
  `run_writer_stage()`内、`dev_status == "LEDGER_DEVIATION"`の場合、
  `adv_gen.generate_advanced_adaptation(ja_text, client=client)`を**再度呼び出す**
  (同じ関数、同じ`ja_text`→同じ`build_prompt()`出力)。2回目もMAJORならSTOP(本文を手で
  直さない、既存Gate通り)。
- **fallback**: `er006_model_routing_contract_01.PROCESS_MODEL_MAP`に
  `NATURAL_ENGLISH_ADAPTATION`のfallbackモデル定義は無い。`fallback_detected`は
  観測フラグのみで、モデル切替や別プロンプトへの分岐は存在しない。
- 結論: **build_prompt()内にv2語彙ルールを埋め込めば、初回生成・構造retry・
  deviation再生成のすべてで自動的に同一ルールが適用される**。追加の配線は不要。

## 3. Standard v5の組み込み方法(参照実装)

`er003_v1_n3_01_standard_a2_generate.py`は、Prompt定数`STANDARD_A2_PROMPT_V5`内に
語彙ルール段落(「Prefer words within roughly the 6,000 most common English words.
If a word is clearly outside that range, replace it when a simpler natural
alternative exists. Do not force a replacement if it makes the sentence less
natural or changes the meaning. Proper names are excluded from this rule.
Essential technical terms may remain when a simpler equivalent would lose
important meaning.」)をハードコードし、`STANDARD_A2_PROMPT_SHA256`でPrompt全文の
sha256をimport時にfail-closedでassertしている(定数がずれたらimport自体が失敗)。
候補語リストや順位算出は行わず、モデル自身の語感・知識に依存する(直接生成、
改稿passではない)。

## 4. 組み込み方式の選択肢(i) vs (ii)

| | (i) Adaptation promptへ行追加 | (ii) Adaptation後に順位リスト付き改稿pass追加 |
|---|---|---|
| コスト | 追加API呼び出しなし(既存1回のAdaptation呼び出しのまま) | 記事ごとに追加1回のLLM呼び出し(wordfreq順位算出はローカルで¥0だが、改稿pass自体は課金対象) |
| QCD(品質) | Trial-01/fix01のように個別語の順位・判定理由をモデルへ明示しないため、モデル自身の頻度感覚に依存。Standard v5(6,000語ライン)も同型でこれまで`VALIDATED`実績あり | Trial(v1/v2)は実際に個別candidate語(concierges/onstage等)へ順位付き判断を明示して行っており、より`Trial`実績に忠実。ただしTrialはcandidate語をあらかじめ人間/スクリプトが選定して渡す設計であり、Production自動経路でcandidate語を自動選定する処理は未実装 |
| Trialとの整合 | 部分的(ルール文言はTrialのprompt文言だが、個別candidate語の順位提示は行わない) | Trialの実施形態(改稿pass、順位リスト提示)そのもの |
| 配線の複雑さ | 最小差分(Standard v5と同型のprompt定数追加のみ) | 新規stage追加(wordfreq順位算出→candidate語抽出→改稿prompt生成→追加API呼び出し→構造再検証)が必要 |
| retry/fallback整合 | 既存retry機構がそのまま効く(上記2節) | 新規stageの構造retryを別途設計する必要がある |

## 5. 暫定判断

**(i)で実装を進める。** 理由: Standard v5と同型が最小差分であり、ユーザー指示の
「v2仕様へ戻す」という文言に対応する最短経路。(ii)の要否(順位リスト付き改稿pass
が実際にQCDを改善するか)は、次回以降の通常Production Runでの観察後に判断する
(本タスクのスコープ外、OPEN_ITEMSへ残置)。

この判断は暫定であり、Fable/ユーザーが(ii)を正式に要求する場合は別管理IDで
改めて設計・実装する。
