# TRIAL_DESIGN_01: Family X Key Phrase選定・6モデル比較Trial 設計書(実行前に固定)

管理ID: FAMILY-X-KP-SELECTION-SIX-MODEL-COMPARISON-TRIAL-01 委任_01 / 作成: 2026-10-22(有料呼出の前に作成・固定)
Status: Trial(ユーザー承認済み)。**Production採用未承認**。Production(`er030_*`選定経路・Prompt template・`er006_model_routing_contract_01.py`・Validator・KP Store)は一切変更しない。Trial専用: `er098_kp_six_model_trial_01_*.py`、`er098_output/kp_six_model_trial_01/`、本ディレクトリのみ。
ユーザー原文: `docs/pm/delegation_log/2026-10-22_FAMILY-X-KP-SELECTION-SIX-MODEL-COMPARISON-TRIAL-01_USER.md`(指示1)、`..._PROMPT-ADJUST_USER.md`(指示2)。

## 0. 先行Trial/既存仕様の照合(21節 A既判断/B承認範囲内/C独立)
- 過去のKP関連Trial: `KEY-PHRASE-DB-BASED-SELECTION-DESIGN/TRIAL-01`・`KEY-PHRASE-DB-HYBRID-TRIAL-02/03`・`KEY-PHRASE-DB-HYBRID-FAMILY-X-PRODUCTION-WIRING-01`(`docs/pm/REPORT_LEDGER.md` L62/74/83/84/90)はDB shortlist+軽量prompt方式の設計比較で、モデルは`gpt-6-luna`系固定。**「同一Prompt(本文全文渡し)でKP選定を6モデル比較」した先例はない -> 区分C(現Production方式とは独立の新規比較、相違点を記録して実行)**。
- 現行Production KP選定: モデル`gpt-6-luna`(`er006_model_routing_contract_01.py:50 SUPPORT_MODEL`)、方式=M2P0 DB hybrid(`er030_key_phrase_db_hybrid_selector_01.py`、shortlist+軽量prompt+canonicalization、`APPROVED_FOR_PRODUCTION` 2026-10-16)。**本Trialはユーザー指定Prompt(本文全文渡し・shortlistなし・canonicalizationなし)であり、Production方式とは別物。モデル差とPrompt方式差を混同しない**(結果では「既存Production KP」行を方式差込みの参考として並置する)。
- 既存Production KPは`canonicalization`で原形化・短縮・「one's」化されるため、本Trialの厳密規則(一般化以外の活用形変更・語の抜き取りも変更とみなす)では一部が機械検証NGになる。これは**方式差の観測値であり、Production仕様違反ではない**(結果にそのまま記載)。

## 1. ユーザー要求と設計書の対応表(22節 開始前チェック、全項目)
| 要求 | 設計書の対応 | 実装/成果物 |
|---|---|---|
| 指示1 §1 目的(同一Prompt・同一本文、品質/遵守率/単価比較) | 3・4・5・6・7節 | run/validate/eval/Excel |
| §1 Status=Trial承認済み/Production未承認、既存Production不変 | 冒頭・9節 | Trial専用ファイルのみ、Production編集0 |
| §2 7記事x2レベル=14本文、版・出典記録、欠落は明示 | 2節(版表) | inputs/manifest.json、欠落=なし(14/14取得) |
| §3 6モデル固定、返却model ID記録、設定差記録 | 3節 | runs/<model>/*.json(model_returned)、Excel「条件・Prompt」 |
| §4 Prompt全文固定、調整は指示2に従い事後報告 | 4節 | inputs/prompt_fixed.txt(sha256記録)、TRIAL_RESULT 調整事後報告 |
| §5 84回、初回1回、品質理由の再生成禁止、技術的失敗は区別、並列、既存KP再生成禁止 | 3節・7節 | run.py(既存runs skip、再試行は技術的失敗のみ最大2回) |
| §6 Excel(比較表+品質評価サマリ+費用サマリ+検証詳細)、凡例 | 8節 | KP_MODEL_COMPARISON_01.xlsx(5シート) |
| §7A 機械検証(語数・5語超・本文一致・一般化span・自己申告不一致、無条件PASS禁止) | 5節 | validate.py -> validation.json |
| §7B 独立評価(自己評価のみ禁止、評価費用記録、主観と機械の区別) | 6節 | eval.py -> eval/ |
| §7 不合格結果を修正して載せない | 3節・5節 | 全結果をそのまま保存・掲載 |
| §8 費用(入出力token・単価・実費・記事セット単価・7記事合計・品質KP1件当たり・既存Production実費) | 7節 | paid_calls.jsonl、Excel「費用サマリ」 |
| §8 予算枠遵守/超過見込みSTOP | 7節 | cap-jpy 300(選定+評価+疎通の通算) |
| §9 最終報告1〜7、到達Status=VALIDATED/REJECTED/USER_DECISION_REQUIRED(候補) | 9節 | TRIAL_RESULT_01.md |
| §10 STOP条件(指定モデル不可なら置換せずSTOP) | 3節 | 全6モデル実在を無料models listで確認済み |
| 指示2 §1 軽微調整許可(意味・条件・優先順位・基準不変) | 4節 | 調整=データ区切りと見出しの追加のみ |
| 指示2 §2 全6モデル共通 | 4節 | 同一user message構築 |
| 指示2 §3 事後報告4項目 | 4節 | TRIAL_RESULT_01.md |
| 委任文: レベル名対応確認 | 2節 | `er019_family_x_audio_production_runner_01.py:742,1205`(b1b=Advanced、a2=Standard) |
| 委任文: 費用Guardrail Cap JPY300、300超は事前報告 | 7節 | ledger通算、pilot段階実行 |
| 委任文: T-0保存・SSOT・commit規定 | 10節 | docs/pm/delegation_log、OPEN_ITEMS、REPORT_LEDGER |

## 2. 入力(14本文、版表)
Standard=`a2`、Advanced=`b1b`(`er019_family_x_audio_production_runner_01.py:742`「Advanced(B1B)」、`:1205`「A2(Standard)」)。本文は各runの`article.md`をそのまま使用(タイトル見出し・`## In one line`節を含む)。コピーを`inputs/articles/`に保存。
旧記事G(ホルムズ海峡)もFamily Xのb3_diversity_trial_01 run_02(a2/b1b)であり、B1/A2等の旧レベル名ではない(Standard/Advanced相当、試聴page `user_test/flash_lite_family_x_02_hormuz`が参照するrun)。KPは`gpt-5.6-luna`世代(旧)の記録。
記事B(給料)は`run_pp_02`(再制作版・最新の正式経路版)を使用、`run_pp_01`も存在(使用せず)。記事Aは`run_v5_ms_01`本文+`run_m2p0_n01_01`のM2P0 KP(最新audio wiring)。記事EはMeta `run_regen_01`(`run_03`は旧、`run_sol61_01`は本文なし)。

| unit | 記事 | レベル | 本文path | commit | sha256(先頭16) | 文字数/語数 | KP/audio dir |
|---|---|---|---|---|---|---|---|
| A_Standard | コーヒー価格の高騰 | Standard(a2) | `er019_output/coffee_prices/run_v5_ms_01/a2/article.md` | d43ba59c4 | `a3cc7bb98af7526f` | 2370 / 443 | `er019_output/family_x_audio_production_wiring_01/coffee_prices__run_m2p0_n01_01` |
| A_Advanced | コーヒー価格の高騰 | Advanced(b1b) | `er019_output/coffee_prices/run_v5_ms_01/b1b/article.md` | d43ba59c4 | `d9b77190905d9060` | 2610 / 493 | `er019_output/family_x_audio_production_wiring_01/coffee_prices__run_m2p0_n01_01` |
| B_Standard | 給料が上がると、性格も変わる？ | Standard(a2) | `er019_output/paycheck_personality/run_pp_02/a2/article.md` | 352eb31db | `909684336e4da8c8` | 2756 / 463 | `er019_output/family_x_audio_production_wiring_01/paycheck_personality__run_pp_02` |
| B_Advanced | 給料が上がると、性格も変わる？ | Advanced(b1b) | `er019_output/paycheck_personality/run_pp_02/b1b/article.md` | 352eb31db | `5052ff7c21a25d5c` | 2868 / 472 | `er019_output/family_x_audio_production_wiring_01/paycheck_personality__run_pp_02` |
| C_Standard | 漫画のキャラクターとAIで会話(byUs) | Standard(a2) | `er019_output/manga_ai_chat_byus/run_byus_01/a2/article.md` | 78e780eaf | `50e75d8e2a892dbe` | 2804 / 515 | `er019_output/family_x_audio_production_wiring_01/manga_ai_chat_byus__run_byus_01` |
| C_Advanced | 漫画のキャラクターとAIで会話(byUs) | Advanced(b1b) | `er019_output/manga_ai_chat_byus/run_byus_01/b1b/article.md` | 78e780eaf | `fb37a0913ef48c45` | 2937 / 532 | `er019_output/family_x_audio_production_wiring_01/manga_ai_chat_byus__run_byus_01` |
| D_Standard | 退屈と攻撃性の関係 | Standard(a2) | `er019_output/boredom_aggression/run_bape_01/a2/article.md` | 513104fe2 | `d9552126bde988c6` | 3005 / 536 | `er019_output/family_x_audio_production_wiring_01/boredom_aggression__run_bape_01` |
| D_Advanced | 退屈と攻撃性の関係 | Advanced(b1b) | `er019_output/boredom_aggression/run_bape_01/b1b/article.md` | 513104fe2 | `b5733178c4d63e6e` | 3057 / 523 | `er019_output/family_x_audio_production_wiring_01/boredom_aggression__run_bape_01` |
| E_Standard | Meta関連の記事 | Standard(a2) | `er019_output/meta/run_regen_01/a2/article.md` | 33ec9ff44 | `2f8307ab1b98060d` | 2438 / 440 | `er019_output/family_x_audio_production_wiring_01/meta__run_regen_01` |
| E_Advanced | Meta関連の記事 | Advanced(b1b) | `er019_output/meta/run_regen_01/b1b/article.md` | 33ec9ff44 | `c6318609e9df7ffe` | 2531 / 458 | `er019_output/family_x_audio_production_wiring_01/meta__run_regen_01` |
| F_Standard | 中東情勢(イエメン・サウジアラビア) | Standard(a2) | `er019_output/middle_east_yemen_saudi/run_mey_02/a2/article.md` | 0b917eb44 | `d948d2c6570e6e5d` | 2560 / 438 | `er019_output/family_x_audio_production_wiring_01/middle_east_yemen_saudi__run_mey_02` |
| F_Advanced | 中東情勢(イエメン・サウジアラビア) | Advanced(b1b) | `er019_output/middle_east_yemen_saudi/run_mey_02/b1b/article.md` | 0b917eb44 | `2174f5dc038537fc` | 2704 / 450 | `er019_output/family_x_audio_production_wiring_01/middle_east_yemen_saudi__run_mey_02` |
| G_Standard | ホルムズ海峡関連(旧記事) | Standard(a2) | `er019_output/family_x_b3_diversity_trial_01/hormuz/run_02/a2/article.md` | e7311d37c | `e29b21c67f214039` | 2080 / 382 | `er019_output/family_x_audio_production_wiring_01/family_x_b3_diversity_trial_01/hormuz__run_02` |
| G_Advanced | ホルムズ海峡関連(旧記事) | Advanced(b1b) | `er019_output/family_x_b3_diversity_trial_01/hormuz/run_02/b1b/article.md` | e7311d37c | `5290325c6c663aff` | 2020 / 368 | `er019_output/family_x_audio_production_wiring_01/family_x_b3_diversity_trial_01/hormuz__run_02` |

(完全なsha256・KP path・KP sha256・既存KP選定実費は`inputs/manifest.json`)

## 3. 実行条件(公平性)
- モデル(固定): 1 `gpt-6-luna`(現行) / 2 `gpt-6.1-sol` / 3 `gemini-3.1-flash-lite` / 4 `gemini-3.5-flash-lite` / 5 `claude-haiku-5-5` / 6 `claude-sonnet-5-5`。無断置換しない。`models list`(無料)で全6 IDの実在を2026-10-22に確認済み。不可ならSTOP報告。
- 構成: system=なし、user=Prompt+データ(4節)の1メッセージのみ。温度・推論設定・thinkingConfig・出力形式指定(JSON mode等)は**送らない(各providerの既定値)**。max出力token=16000(全モデル同一、推論token込み)。OpenAI=Responses API、Anthropic=Messages API(raw HTTP)、Gemini=generateContent(raw HTTP)。
- 既定値の差(提供側の仕様。記録のみ): 推論モデルは既定で推論tokenを出力側に課金。Claudeは`thinking`未送信。実際の推論token数はusageに記録。
- 初回生成1回。再生成は**技術的失敗(timeout/HTTP 429・5xx/接続)のみ**同一入力で最大2回(記録)。品質理由・解析不能・5件未満・本文不一致では再生成しない。
- 並列: 最大12並列(provider混在)。既存`runs/<model>/<unit>.json`があるものはスキップ(誤再実行による再課金防止)。

## 4. 適用Prompt・調整の事後報告材料(指示2)
- Prompt本文=`inputs/prompt_fixed.txt`(sha256 `4360c9cccee8765543b7ecc8d7e9dc60f73754951803e86383e24ac286b6921d`)。ユーザー指示1 §4のPrompt本文を一字一句そのまま保存(Markdownの`**`も保持)。
- **変更前**: Promptは「以下の記事から…」で始まり、記事の渡し方は未規定。**変更後**: Prompt本文は**1字も変更せず**、末尾に区切りと見出しを付けて記事本文を後置: `<Prompt本文>` + 改行2 + `---` + 改行2 + `【記事本文】` + 改行 + `<article.md全文>`。
- **理由**: Promptは記事を別途渡す前提の文面で、本文の受け渡し位置が必要なため(指示2 §1「データ受け渡し方式との整合に必要な文言調整」の範囲)。
- **選定条件・品質基準への影響なし**: Prompt本文の文字列・順序・優先順位・基準は完全同一(`prompt_sha256`を全runへ記録し一致を検証)。追加したのは区切り線と見出し「【記事本文】」のみ。出力形式の指示は追加していない。全6モデル同一関数で構築。

## 5. 機械検証規則(validate.py、API 0)
- 語数=スペース区切り個数(`~`・`A`・`someone`も1語)。5語以内=1〜5語。6語以上=違反(出力されたものも採点対象に残す)。
- 候補の抽出: モデル出力テキストの番号付き行(なければ箇条書き行)から先頭の語句部分を取り、`**`・引用符・括弧内語数・説明を除去(Promptに形式指示を足さないため)。自己申告語数=「N語/N words」表記。解析不能は記録。
- 本文一致(正規化=大小文字・引用符種別・末尾句読点のみ。語境界あり):
  - `A_EXACT`: 本文中に連続部分列として存在 -> 確認済み(原文span・文字offset保存)。
  - `B_GEN_UNIQUE`: placeholder(`~`,`A`,`B`,`X`,`Y`,`someone`,`something`,`somebody`,`sb`,`sth`,`one's`,`oneself`及び所有格形)を可変長wildcard(1〜5語)にした照合で一意に原文spanを特定 -> 確認済み(置換前の原文span・各placeholderの原文を保存)。
  - `B_GEN_AMBIGUOUS`: 複数span該当 -> **要確認**(最初のspanを保存、確認済みには含めない)。
  - `NG_INFLECTION_ONLY`: 活用形・所有格代名詞のみ相違して本文にある(厳密規則=変更=NG。創作ではない区別のため別記録)。
  - `NG_NO_MATCH`: 言い換え/語の抜き取り/創作。 `NG_ONLY_PLACEHOLDER` / `NG_EMPTY`。
  - 無条件PASSは作らない。一般化の妥当性自体は6節の独立評価で別途判定(機械は存在確認のみ)。
- `strict_pass`(厳格版の機械合格)= 5語以内 AND 本文一致が確認済み AND セット内重複でない。
- 自己申告語数と実際の語数が異なる場合は違反ではなく`self_count_mismatch`として別記録。6件以上・5件未満・重複も記録。
- 既存Production KPにも同じ規則を適用(比較基準。方式差に注意)。

## 6. 独立評価(eval.py、有料)
- 評価モデル: `gpt-6.1-sol`と`claude-sonnet-5-5`(最新上位モデル原則 PM_GOVERNANCE 25節)の2系統。選定元と**異系統の評価=主評価**、同系統=参考。主評価の定義: OpenAI(Luna/Sol)・既存Production(Luna)の行=Claude評価、Claude(Haiku/Sonnet)の行=Sol評価、Gemini(2モデル)の行=2系統平均。同系統評価は「参考」列に併記。
- 方式: 各本文につき1回の評価で、7セット(6モデル+既存Production)をモデル名を伏せ・順序をシャッフル(seed=`er098:<unit>`、`eval/blind_map.json`)して提示。評価者には機械検証結果・自己申告語数・モデル名を渡さない。rubricはeval.pyの`RUBRIC`に固定。
- rubric(各候補0〜2): G=一般化の適切さ / V=上級者向け学習価値 / E=易しさの排除 / N=単位の自然さ、+ needs_generalization(bool)、セット単位 padding(bool)。候補スコア=(G+V+E+N)/8(0〜1)。
- **「品質を満たしたKP」の定義(閾値は実行前に固定)**: 厳格版=`strict_pass`のみ。総合版=厳格版 AND 主評価スコア>=0.75 AND G/V/E/Nのいずれも0でない。
- 本文一致・語数は機械検証が正、評価者の主観(G/V/E/N)は別列。主観評価と機械違反を混ぜない。
- 評価費用は選定費用と分けて`paid_calls.jsonl`(phase=eval)に記録。

## 7. 費用・見積・Guardrail
- 単価(USD/1M tokens、input/cached/output[thinking込み]、出典は`er098_kp_six_model_trial_01_common.py` `PRICES`およびExcel「条件・Prompt」): Luna 0.10/0.01/0.50 / Sol 2.00/0.10/10.00 / Gemini 3.1 Flash-Lite 0.25/0.025/1.50 / Gemini 3.5 Flash-Lite 0.30/0.03/2.50 / Haiku 5.5 0.10/0.01/0.50(prompt<=100k) / Sonnet 5.5 2.00/0.10/10.00。全6モデル単価は公式ページ(2026-10-22取得、raw html sha256を`PRICES`出典欄に記載)またはrepo登録値で確認済み(未確認モデルなし)。為替=USD_TO_JPY 160.0(`er009_n1_routing_governance_10_actual_model_cost.py:20`、プロジェクト既定値。実為替ではない)。
- 実費=APIが返したusage(input/output[推論込み]/cached)x上記単価。推定ではなく実測usageから算出。
- 事前見積(pilot前、中心値): 入力約1.9k token/呼出。出力(推論込み)の想定: Luna 4k / Sol 6k / G3.1 1.5k / G3.5 2k / Haiku 0.8k / Sonnet 0.8k -> 選定14本文分 約JPY194(Sol約143が支配的、Sol出力3k〜10kで約75〜230)。評価(Sol既定+Sonnet既定): 約JPY205。合計約400と**300超の可能性あり**。
- 対応: 段階実行。**Stage 1 = pilot(本文A_Standard x 6モデルの初回6回、84回の一部としてそのまま採用、見積約JPY14)** で実usageを取得 -> 見積を確定 -> 総額(選定+評価)が300以下なら続行。評価は費用抑制設定(Sol `reasoning.effort`を下げる・noteなしのコンパクトJSON)を事前に固定してから見積り、300超となる場合は有料呼出前にFableへ報告(7-7)。実行中も`paid_calls.jsonl`通算がCap(300)に達する見込みなら新規呼出を止める(run.py/eval.pyが通算でガード)。
- 日次(JST 2026-10-22): 既使用約JPY258+C-3進行中。本Trial見積は残(約620)の範囲内。

## 8. Excel(KP_MODEL_COMPARISON_01.xlsx、openpyxl 3.1.5既導入)
シート1「比較表」: 記事A->Standard->Advanced->B…順。各レベルに「既存Production」「1 gpt-6-luna」…「6 claude-sonnet-5-5」の行、列=KP1〜5、セル=「表現 (語数)」。機械検証判定で色分け(緑=確認済み、黄=要確認/活用形のみ差、赤=NG・5語超、灰=技術的失敗)、凡例付き。5件未満は空欄。シート2「品質評価サマリ」、シート3「費用サマリ」、シート4「検証詳細」、シート5「条件・Prompt」。

## 9. Production無変更・分離
Trial専用ファイルのみ新規作成。`er030_*`/`er006_model_routing_contract_01.py`/Prompt template/Validator/KP Storeは読取参照のみ(編集0)。TTS/ASR未使用、環境変数は変更しない。

## 10. SSOT・Git
OPEN_ITEMS(新規OPEN、自分の行のみ)・REPORT_LEDGER(1行)のみ編集。DECISION_LOG・CURRENT_SPEC・USER_DECISION_REGISTERは編集しない。commitは明示addのみ(`git add -A`禁止)、secret scan hits=0。
