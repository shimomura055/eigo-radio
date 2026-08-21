# ER-006-MODEL-ROUTING-CONTRACT-01 完了報告

残り17トピックへは進んでいない。新規有料API呼び出しは¥0(監査・コード修正・test・
既存ログのCost再計算のみで完結させた)。

## 0. 最初に回答(19章の質問に対する要約)

1. **Production各工程の最終Model一覧**: 6章参照。Query Planning/Topic Selection/
   Evidence Pack/VFL/Verification/Support Fact Checkは元々Luna。B1/A2 Writer・
   Writer Fact Check・B1/A2 Support(Key Phrase含む)は今回Sol→Luna。Exception
   Search=Perplexity、TTS=Gemini、ASR=Azureは変更なし。
2. **仕様と実装が不一致だった工程一覧**: 4章の監査テーブル参照。ただし【重要】節の
   とおり、これは「仕様からの逸脱」ではなく「Writer/Support系をLunaにするという
   明文化された決定がこれまで一度も存在しなかった」ことが判明した。
3. **Solが使われていた全箇所**: 5章。
4. **なぜSolが混入したのか**: 5章。「混入」ではなく、ER-002/003時代からの一貫した
   original designだった。
5. **修正後、SolがProductionから0件になった証拠**: 8章(Static Audit、16件PASS)。
6. **Model RoutingのSingle Source of Truth**: [er006_model_routing_contract_01.py](https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er006_model_routing_contract_01.py)。
7. **規定外modelを使えない仕組み**: `require_model()`/`require_provider()`
   (fail-closed、7章)。
8. **fallback時もmodelが変わらない証拠**: 9章(fallback経路=prompt/戦略の
   fallbackのみ、model切替は無い設計を確認)。
9. **Runtime telemetryのmodel記録例**: 10章(ER-006-POOL-PILOT-COST-ROOTFIX-01時点
   で既にactual model_idを記録していたことを確認)。
10. **Regression test結果**: 全テストPASS(11章)。
11. **Static audit結果**: 全16件PASS(8章)。
12. **Historical Actual Spend**: ¥2,639.6(6episode合計、変更なし)。
13. **Approved Routingなら6episodeはいくらだったか**: ¥883.8(Counterfactual)。
14. **Sol混入による追加損失額**: ¥1,755.8。
15. **B1 Full Clean Episode Cost**: ¥37.9(Approved Routing想定)。
16. **A2 Full Clean Episode Cost**: ¥43.4(Approved Routing想定)。
17. **残り17 Topicへ進める状態か**: 断定しない。Model Routingは今回確定したが、
    Lunaでの記事・Support品質は未検証(13章)。
18. **CURRENT_SPEC変更内容**: 「Model Routing Contract」セクションを新設(14章)。
19. **新規API実行額**: ¥0。

---

## 【重要】前提の訂正: 「Sol混入」ではなく「Luna化の決定が一度もされていなかった」

作業開始時点でのタスク前提は「Writer/Support系は本来Lunaを使う予定だったのに実際は
Solが使われていた」というものだった。コードの依存関係を全て遡って調査した結果、
**この前提は事実と異なる**ことが判明した。

- Writer/Support系(B1/A2 Writer・Writer Fact Check・Deviation Check・B1/A2
  Support・Key Phrase選定/正規化)は、`er002_ja_free_markdown_restore.py`の
  `WRITER_MODEL = "gpt-5.6-sol"`という**単一のhardcoded literal**(コードベース
  全体でこれが唯一の直書き)に、20以上のファイルが`X_MODEL = Y.X_MODEL`という
  連鎖的な参照で依存しており、**ER-002/003時代から一貫してSolを使う設計**だった。
- Luna(`gather_topic.py`の`MODEL_SEARCH`)は元々Query Planning/Topic Selection
  (調査・選定フェーズ)専用として設計されており、ER-005より前から存在する。
- Writer/Support系をLunaにするという決定は、`CURRENT_SPEC.md`・`DECISION_LOG.md`
  のいずれにも見つからなかった。ER-005-WRITER-COST-QUALITY-01/SUPPORT-COST-
  QUALITY-01は、Lunaへ切り替えた場合のCost試算のための**未検証の実験的
  reimplementation**であり、その報告書自身が「Lunaで実際に同等品質の出力が
  得られるかは検証していません」と明記していた。

つまり、ER-006-POOL-PILOT-COST-ROOTFIX-01で「Sol混入」と呼んだ現象の正体は、
(1) 私自身のCost集計スクリプトがWriter/Support呼び出しを一律Luna単価で計算する
バグを持っていたこと、と(2) Writer/Support系のModel Routingを正式にLunaへ決定
するかどうかが、これまで一度も明文化されていなかったこと、の**2つの別々の
問題**だった。

この事実を提示した上でユーザーに確認したところ、**「ER-005での方針に整合させる
形で、Writer/Support系を正式にLunaへ固定する」という決定を今回下す**旨の回答を
得た。本タスクはこの決定に基づき実装している。詳細は
[DECISION_LOG.md](https://raw.githubusercontent.com/shimomura055/eigo-radio/main/DECISION_LOG.md)
の`ER-006-MODEL-ROUTING-CONTRACT-01`エントリを参照。

## 1〜3. 監査方法

`gpt-5.6-sol`・`gpt-5.6-luna`・model指定・default/fallback/環境変数由来modelを
コードベース全体(43ファイルが`gpt-5.6-sol`を参照)から検索し、各参照が
production(N3/Pool pipeline)から到達可能かどうかを、実際のimport連鎖を1つずつ
辿って確認した。

## 4. 監査結果一覧

| Process | Intended | Actual(修正前) | Source | Status(修正前) |
|---|---|---|---|---|
| Query Planning | Luna | Luna | `gather_topic.py::MODEL_SEARCH` | MATCH |
| Topic Selection | Luna | Luna(未実行、Pool Topic Selectionは0円) | 同上 | MATCH(N/A) |
| Web Search | Perplexity | **OpenAIの`web_search`組み込みtool**(Sol call内) | `er002_ja_web_research_r3.py::tools=[{"type":"web_search"}]` | AMBIGUOUS(後述) |
| Source Retrieval | No LLM | No LLM(手動URL取得) | - | MATCH |
| Evidence Pack | Luna | Luna | `er006_pool_pilot_01_research.py` | MATCH |
| VFL | Luna | Luna | 同上 | MATCH |
| Verification | Luna | Luna | 同上 | MATCH |
| Exception Search | Perplexity | Perplexity(`/search`エンドポイント) | 同上 | MATCH |
| B1 Writer | Luna | **Sol** | `vfl01.MODEL = r3.WRITER_MODEL` | VIOLATION→修正済 |
| A2 Writer | Luna | **Sol** | 同上 | VIOLATION→修正済 |
| Writer Fact Check | Luna | **Sol** | `r3.FACT_CHECKER_MODEL = WRITER_MODEL` | VIOLATION→修正済 |
| B1 Support | Luna | **Sol**(Comment/Preview/Key Phrase) | `b1s.MODEL = vfl01.MODEL`, `bk.SELECTOR_MODEL`連鎖 | VIOLATION→修正済 |
| A2 Support | Luna | **Sol** | `a2gen.MODEL = vfl01.MODEL` | VIOLATION→修正済 |
| Support Fact Check | Luna | Luna(自前実装で最初からLuna) | `er006_pool_pilot_01_support.py::run_support_fact_check` | MATCH |
| Script Assembly | No LLM | No LLM | - | MATCH |
| TTS | Gemini | Gemini `gemini-2.5-pro-preview-tts` | `er002_common.py::MODEL_NAME` | MATCH |
| ASR / Audio QA | Azure | Azure STT | `er003_b1_p4_audio.py::get_full_text_via_azure_stt_continuous` | MATCH |
| Final Assembly | No LLM | No LLM | - | MATCH |

**Web Searchについての注記(AMBIGUOUS)**: ルーティング表の「Web Search: Perplexity」
は、私自身のResearch層(Evidence Pack構築前のSource収集)を指していると解釈できるが、
実際に稼働しているのは**production Fact CheckerがOpenAI純正の`web_search`tool**を
Sol呼び出し内で使うという、別の、より古い設計だった。これは元々の設計であり
「drift」ではないため、Perplexityへの置き換えは行っていない(Fact Checker自体の
仕組みを変えることになり、スコープ外の大規模変更のため)。この解釈の是非は
別途確認が必要な場合はご指摘いただきたい。

**発見された副産物**: `er002_gemini_client.py`に`gemini-3-flash-preview`という
第3のGemini modelを使う`make_qa_call_fn`/`make_qa_text_call_fn`が存在するが、
現在のN3/Pool production経路(`generate_key_phrase_component_verified`等)は
Azure STTのみを使っており、このGemini-QA関数は**呼び出されていない
(production未到達のdead code)**ことを確認した。

## 5. Sol使用箇所の全件記録

| Process | file/function | なぜSolだったか | 導入時期 | fallback/standard | Pool以外への影響 |
|---|---|---|---|---|---|
| B1/A2 Writer | `er003_v1_en_direct_vfl_01_generate.py::run_writer_no_search` | ER-002/003 original design(唯一の根本定数) | ER-002(本セッション以前) | standard | hanshin/health/household含む全テーマ |
| Writer Fact Check | `er002_ja_web_research_r3.py::make_fact_checker_fn` | 同上(`FACT_CHECKER_MODEL = WRITER_MODEL`) | 同上 | standard | 同上 |
| Deviation Check | `er003_v1_en_direct_vfl_01_generate.py::run_deviation_check` | 同上 | 同上 | standard | 同上 |
| B1 Support | `er003_v1_b1_scaffold_01_generate.py::run_support_text` | 同上 | 同上 | standard | 同上 |
| A2 Support | `er003_v1_iran01_a2_generate.py::run_support_text` | 同上 | 同上 | standard | 同上 |
| Key Phrase Selector | `er003_key_words_production.py::make_production_selector_fn` | 同上(`SELECTOR_MODEL`連鎖) | 同上 | standard | 同上 |
| Key Phrase Canonicalization | `er003_key_words_canonicalization.py::make_canonicalization_fn` | 同上 | 同上 | standard | 同上 |

いずれも「fallbackとして高価なmodelへ自動昇格した」のではなく、**standard経路
そのものが最初からSol設計**だった(9章参照、fallback経路はprompt変更のみで
model切替は元々発生していない)。

## 6. Approved Model一覧(修正後)

[CURRENT_SPEC.md > Model Routing Contract](https://raw.githubusercontent.com/shimomura055/eigo-radio/main/CURRENT_SPEC.md)
に正式記載した(14章参照)。

## 7. Fail-Closed Model Contract

[er006_model_routing_contract_01.py](https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er006_model_routing_contract_01.py):
`require_model(process, model)`/`require_provider(process, provider)`が、
規定外・未知・未指定(None/空文字)いずれもAPI call実行**前**に
`ModelContractViolation`を送出する。

## 8. 本番配線+Static Audit

**配線方針(最小侵襲)**: 各leaf関数(`run_writer_no_search`等)の**既定値は変更せず**、
`model`引数を新規追加した(後方互換)。Production entry point
(`er003_v1_n3_01_articles_generate.py::run_one_pattern`、
`er003_v1_n3_01_scaffold_generate.py::run_b1_scaffold/run_a2_scaffold/
run_key_phrases`)だけが、SSOTから取得したmodelを明示的に渡す。これにより、
この契約の対象外とした30以上の他の呼び出し元(Translation pipeline・過去の
CEFR/spoken-first実験タスク等)は一切変更されず、Sol既定値のまま動作する
(過度な大規模refactorを避けるため)。

**Static Audit**([er006_model_routing_contract_01_static_audit.py](https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er006_model_routing_contract_01_static_audit.py)、
16件全PASS): production到達可能な各呼び出し箇所にroutingを経由した明示的
model指定が存在すること(12件)、および同箇所に素の`"gpt-5.6-sol"`が復活して
いないこと(4件)を確認した。

## 9. Fallbackの性質確認

Support/Writer/Key Phraseのfallback経路(`generate_a2_japanese_with_fallback`
等)を確認したところ、いずれも「standard prompt失敗時にminimal instruction
promptへ切り替える」という**prompt戦略のfallback**であり、**modelそのものの
切替は一度も発生していない**ことを確認した(コメントにも「声・モデルは変えない」
と明記されている箇所複数)。TTS/ASRについても同様、provider切替のfallbackは
存在しない。

## 10. Runtime Telemetry

ER-006-POOL-PILOT-COST-ROOTFIX-01の時点で、`raw_usage_log.jsonl`は既に
API呼び出し時の実際の`model_id`(SDKレスポンスから取得、料金表からの推測ではない)
を記録していたことを確認した。ER-006-POOL-PREPROD-HARDENING-01で追加した
`segment`フィールドと合わせ、`topic_id`(theme)/`stage`(process)/`segment`/
`attempt`/`model_id`/`provider`/`cost`が1レコードに揃っている。

## 11. Model Contract Regression Test

[er006_model_routing_contract_01_test.py](https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er006_model_routing_contract_01_test.py)
実行結果(全PASS):
- Positive: 11 process全てでApproved Model(Luna)がPASS
- Negative(Sol): 11 process全てで`ModelContractViolation`
- Negative(未知model): 3 process(代表)で`ModelContractViolation`
- Negative(未指定 None/空文字): 3 process(代表)×2パターンで`ModelContractViolation`
- Provider(Perplexity/Gemini/Azure): 規定外6ケース中3ケースが正しくFAIL、3ケースが
  正しくPASS
- Fallback: `vfl01`の3関数が全てmodel override引数を受け付けることを確認

## 12. Static Audit Test

8章参照。

## 13. Cost再計算

[er006_model_routing_contract_01_cost_recompute.py](https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er006_model_routing_contract_01_cost_recompute.py)
(新規有料API呼び出しなし、既存ログのみ使用)。

### 6episode

| | 金額 |
|---|---:|
| Historical Actual Spend(実際に支払った、書き換えない) | **¥2,639.6** |
| Counterfactual(Approved Luna Routingだった場合) | **¥883.8** |
| Sol使用による超過Cost | **¥1,755.8** |

**面白い後日談**: 実はこのCounterfactual値(¥883.8)は、ER-006-POOL-PILOT-01の
最初の報告で(バグにより)報告していた金額と完全に一致する。つまり最初の報告は
「Sol実費用」としては誤りだったが、偶然にも「Approved Luna Routingだったら
いくらだったか」という値としては正しかった、という経緯だとわかった。

### stage別内訳

| Stage | Historical Actual | Counterfactual | 超過分 |
|---|---:|---:|---:|
| Writer(Fact Check/Deviation Check込み) | ¥1,844.3 | ¥301.1 | ¥1,543.2 |
| Support(Key Phrase/Fact Check込み) | ¥223.0 | ¥10.3 | ¥212.6 |
| Research(元々Luna、影響なし) | ¥12.0 | ¥12.0 | ¥0 |
| TTS/ASR(元々Gemini/Azure、影響なし) | ¥560.4 | ¥560.4 | ¥0 |

### 1episode(Full Clean Episode Cost、Approved Routing想定)

| | B1 | A2 |
|---|---:|---:|
| 平均 | **¥37.9** | **¥43.4** |

旧Baseline(¥46〜48/episode)と比較すると、Approved(Luna)Routingを前提にすると
Clean Costは**同等かむしろ低い**(ER-006-POOL-PILOT-COST-ROOTFIX-01の当初の
「Clean Costは上昇していない」という結論は、Approved Routing前提であれば
正しかったことになる)。

### 3 Topic(Pair Production Clean Cost)

平均 **¥81.3**(B1+A2合算、Approved Routing想定)。

## 14. Documentation

- [CURRENT_SPEC.md](https://raw.githubusercontent.com/shimomura055/eigo-radio/main/CURRENT_SPEC.md):
  「Model Routing Contract」セクションを新設。
- [DECISION_LOG.md](https://raw.githubusercontent.com/shimomura055/eigo-radio/main/DECISION_LOG.md):
  `ER-006-MODEL-ROUTING-CONTRACT-01`エントリを追加(経緯・ユーザー決定・変更範囲・
  未検証事項を明記)。
- Single Source of Truth: [er006_model_routing_contract_01.py](https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er006_model_routing_contract_01.py)

## 15. 受入条件チェック

| # | 内容 | 状況 |
|---|---|---|
| 1 | Production全工程のModel一覧 | ✅ 4章 |
| 2 | Intended/Actual差分 | ✅ 4章 |
| 3 | Sol使用箇所全件特定 | ✅ 5章 |
| 4 | SolがProduction経路から除去 | ✅ 8章(N3/Pool production entry point限定、5章の理由により対象外箇所は残存) |
| 5 | 各OpenAI工程がLunaに固定 | ✅ 6章 |
| 6 | 規定外modelはAPI call前にFAIL | ✅ 7・11章 |
| 7 | model未指定もFAIL | ✅ 11章 |
| 8 | fallbackで別modelへ切替しない | ✅ 9章(元々切り替えていなかったことを確認) |
| 9 | Providerも規定外へ切替しない | ✅ 7・11章 |
| 10 | Runtime logにactual model_id | ✅ 10章(既に記録済みだったことを確認) |
| 11 | Cost loggerがactual model_id使用 | ✅ 10章(ROOTFIX-01で修正済み) |
| 12 | Model Contract regression test PASS | ✅ 11章 |
| 13 | Production reachable codeのstatic audit PASS | ✅ 8章 |
| 14 | Historical Actual/Counterfactualを分離 | ✅ 13章 |
| 15 | 6episodeのLuna前提Cost再計算 | ✅ 13章 |
| 16 | CURRENT_SPEC/DECISION_LOG更新 | ✅ 14章 |
| 17 | 新規API Cost ¥0 | ✅ |

## 16. リスク・注意点

- **最大の注意点**: Lunaでの記事・Support品質は本タスクでは検証していない。
  次に実際にWriter/Support(hanshin/health/householdの再生成、または残り17
  Pool topicのいずれか)を動かした際の出力品質を確認する必要がある。
- 「Sol使用=違反」ではなく「Luna化の決定が今回初めて明文化された」という
  経緯を、関係者間で共有しておくことを推奨する(前提の誤解が今後も再発しない
  ように)。
- 配線はN3/Pool production entry pointに限定した。Translation pipeline等、
  スコープ外とした呼び出し元は引き続きSolを使う(意図的、5章参照)。
- Web Searchの「Perplexity」規定とFact Checkerの実際の「OpenAI web_search tool」
  使用には解釈のズレがある(4章)。Fact Checker自体の仕組み変更はスコープ外の
  大規模変更と判断し、今回は変更していない。

## 17. 次のステップについて

このModel Routing Contract整備をもって停止する。残り17トピックへの本番投入は、
Lunaでの実際の記事・Support品質を確認してから判断することを推奨する。
