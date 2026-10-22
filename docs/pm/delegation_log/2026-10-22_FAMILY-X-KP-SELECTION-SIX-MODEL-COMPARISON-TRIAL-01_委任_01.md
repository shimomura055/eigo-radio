FABLE-DELEGATION-MARKER: KP6M-TRIAL-RUN-委任_01-20261022

# 委任(FAMILY-X-KP-SELECTION-SIX-MODEL-COMPARISON-TRIAL-01 委任_01: Family X Key Phrase選定・6モデル比較Trialの一括実行[抽出→84回選定→機械検証→独立評価→Excel→SSOT]。ユーザー承認済みTrial。Production採用未承認。Trial専用実装のみ・Production経路無変更)

## 管理ID
FAMILY-X-KP-SELECTION-SIX-MODEL-COMPARISON-TRIAL-01 委任_01(新規管理ID。並行タスク: 別agentが`FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01 委任_08 [C-3]`(記事A run_pp_02の音声化・試聴ページ・SSOT記録)を実行中。衝突回避は§0参照)。

## 性質/到達上限Status/禁止事項
- 性質: 比較Trial(Trial専用実装)。到達上限Status: `VALIDATED`/`REJECTED`/`USER_DECISION_REQUIRED`の**候補**まで(最終分類はFable。`VALIDATED`でもProduction採用ではない)。
- Opus独立技術レビューGate(PM_GOVERNANCE 11-3): **非該当**(Trial専用harnessであり、Productionの構造・処理フロー・Prompt・モデル・Validatorを変更しない。将来の採用提案時に条件Cで別途レビュー)。
- 修正範囲(11-8): 本委任は不具合修正ではない。Production側(`er030_*`選定経路・Prompt template・`er006_model_routing_contract_01.py`・Validator・KP Store)の編集は範囲外。Trial専用script(`er098_kp_six_model_trial_01_*.py`)と`docs/research/FAMILY-X-KP-SELECTION-SIX-MODEL-COMPARISON-TRIAL-01/`・`er098_output/kp_six_model_trial_01/`の新規作成のみ範囲内。
- 時間見込み(8-X): 全体約3〜4時間。内訳: 本文・既存KP・既存実費の抽出45分 / 見積確定10分 / 84回選定(6モデル並列、各モデル内も並列可)20分 / 機械検証+独立評価45分 / Excel+TRIAL_RESULT 60分 / SSOT・commit 20分。並列化: 6モデルの選定呼出は並列(provider別rate limit内、失敗時は同一入力で技術的再試行のみ可・品質理由の再生成禁止)。抽出と評価rubric・Excel雛形は選定実行中に先行作成する。直列化理由があるのは「見積確定→有料呼出」(予算Gate)のみ。
- 費用/日次: 当日(JST 2026-10-22)既使用 約JPY258(出典: RESULT_PACKET_B3RD3 217.39 / PNMH4 6.32 / PNMH7 1.61 / APCA3 4.46 / B3RD6 27.77 / PNMH 委任_07 0.35)+C-3進行中(Guardrail JPY120、未確定)。残 約JPY620(C-3未計上)。本委任見積: **実行前に14本文の実トークン数×6モデルの確認済み単価で算出する**(概算: 選定84回 約100k入力+推論込み出力、独立評価 約100回。目安JPY100〜250)。Guardrail(T-3) **Cap JPY300**: 到達だけで自動STOPしないが、**事前見積がJPY300を超える場合は有料呼出を開始せず報告**(7-7: 案件見積300円超は事前費用承認)。実行中に累計がCapを超える見込みになったら有料呼出を止めて途中結果を保存・報告。改善見込み: 高。承認区分: **C(承認済みScope内・見積300円以下の前提。超過見込み=B)**。単価が未確認のモデルは「未確認」と表記し、推定単価を費用表の確定値として使わない(実課金usageは必ず記録)。
- 禁止: `git add -A/-u/-f`、amend、rebase、force push、stash、clean、reset --hard、checkout -f。commit前`.venv\Scripts\python.exe tools/secret_scan_01.py --staged` hits=0。push=`git push origin HEAD:main`(local `work/post-merge-01`)。`docs/pm/ACTIVE_TASK.md`/`RESULT_PACKET_*.md`は一時ファイル(gitignore、force-add禁止)。SSOT全文読込禁止。作業treeの他人の未commit差分(`er0XX_output/*`、`er011_output/attempt_history.jsonl`等)を混ぜない。有料runの再起動禁止(26節)、開始前にSTOPセンチネル(`STOP`/`STOP_ALL`ファイル)を確認。PATH上の素の`python`禁止(`.venv\Scripts\python.exe`)。**指定6モデルのいずれかがAPIで呼べない(model ID不存在・鍵なし・権限なし)場合は、他モデルへ無断置換せず、呼べたモデル分の結果を保存したうえでSTOP報告**(ユーザー指示§10)。品質が悪い結果の再生成禁止(§5)。不合格結果の修正掲載禁止(§7)。既存Production KPの再生成禁止。

## 0. 運用ルール・並列注意
- 共有ファイル(`OPEN_ITEMS.md`/`DECISION_LOG.md`/`docs/pm/REPORT_LEDGER.md`/`docs/pm/USER_DECISION_REGISTER_01.md`/`docs/pm/ACTIVE_TASK.md`)はC-3 agentも編集する。編集前に必ず`git status`→該当行を再Grep→自分の行だけ編集→即`git add <file>`+commit。`index.lock`は30秒待って再試行。C-3の作業dir(`er019_output/paycheck_personality/run_pp_02/`、`user_test/paycheck_personality_e2e_02/`)は**読み取りのみ**。
- 本Trialは全てTrial専用。TTS/ASRは使わない(テキストのみ)。`TTS_EXECUTION_MODE`は無関係だが環境変数を変更しない。

## 1. ユーザー原文(2026-10-22、逐語。2通をそれぞれ本文無改変で保存: `docs/pm/delegation_log/2026-10-22_FAMILY-X-KP-SELECTION-SIX-MODEL-COMPARISON-TRIAL-01_USER.md`(指示1)、`docs/pm/delegation_log/2026-10-22_FAMILY-X-KP-SELECTION-SIX-MODEL-COMPARISON-TRIAL-01_PROMPT-ADJUST_USER.md`(指示2)。各々文字数とsha256[本文のみ]をRESULT_PACKETに記録)

### 指示1
---
# Claude Code指示：Family X Key Phrase選定・6モデル比較Trial

## 1. 目的・Status

Family Xの記事を対象に、**同一Prompt・同一本文で6モデルのKey Phrase選定品質、指示遵守率、量産単価を比較する。**

特に以下を評価する。

- 本文に存在しない表現を創作しないか
- 5語以内を正確に守るか
- 一般化を適切に実施できるか
- 上級者にふさわしい学習価値があるか
- 5件を無理に埋めず、適切な候補を選べるか

Status：**Trial承認済み／Production採用未承認**

既存ProductionのPrompt・モデル・選定方式は変更しない。

## 2. 対象記事

Family Xの既存6記事に旧記事「ホルムズ海峡」を追加する。

| No. | 記事 |
|---|---|
| A | コーヒー価格の高騰 |
| B | 給料が上がると、性格も変わる？ |
| C | 漫画のキャラクターとAIで会話（byUs） |
| D | 退屈と攻撃性の関係 |
| E | Meta関連の記事 |
| F | 中東情勢（イエメン・サウジアラビア） |
| G | ホルムズ海峡関連（旧記事） |

各記事についてStandard／Advancedの正式制作済み英語本文を使用する。

**7記事×2レベル＝14本文。**

旧ホルムズ海峡記事がFamily X以外の形式である場合も、既存本文を比較用に使用する。記事の再制作は行わない。

Repoから原文・既存Production Key Phrase・記事識別子を取得し、使用した版と出典を記録する。記事やレベルが取得できない場合は、推測で補完せず欠落を明示する。

## 3. 比較モデル（6モデル・固定）

| No. | モデル | API model ID |
|---|---|---|
| 1 | GPT-6 Luna（現行） | `gpt-6-luna` |
| 2 | GPT-6.1 Sol | `gpt-6.1-sol` |
| 3 | Gemini 3.1 Flash-Lite | `gemini-3.1-flash-lite` |
| 4 | Gemini 3.5 Flash-Lite | `gemini-3.5-flash-lite` |
| 5 | Claude Haiku 5.5 | `claude-haiku-5-5` |
| 6 | Claude Sonnet 5.5 | `claude-sonnet-5-5` |

以上をTrial対象として固定する。モデルの無断変更は禁止。

各APIの返却model IDを記録し、指定モデルで実行されたことを確認する。

処理条件はモデル間の公平性を重視し、可能な限り統一する。温度・推論設定などの差異や制約があれば記録する。

## 4. 適用Prompt（全文固定・改変禁止）

以下の記事から、英語上級者が学ぶ価値のある単語・フレーズ・表現・イディオムを5つ選んでください。

**以下の順序で処理し、上位条件を優先してください。**

1. **本文一致（絶対条件）**：本文中の連続した語句だけを抜き出す。一般化以外の変更・言い換え・追加・創作は禁止。
2. **5語以内（絶対条件）**：一般化後の語数をスペース区切りで正確に数える。6語以上は出力禁止。
3. **一般化**：固有名詞や特定の人物・物事を指す部分は、意味と文法を保って `~`、`A/B/someone/something` 等に置き換える。一般化できる場合は必ず行う。
4. **上級者向けの学習価値**：上級者でも学ぶ価値のある語彙・イディオム・慣用表現を優先する。
5. **易しい表現の除外**：基本語だけで構成され、字面どおりに意味が分かる表現や、上級者なら知っている易しい表現は除外する。
6. **5件選定**：条件を満たす候補から5件選ぶ。適切な候補が不足する場合のみ5件未満とし、数合わせはしない。

**出力直前に各候補を本文と照合し、一般化以外の改変がないこと、5語以内であることを再確認してください。語数も併記してください。**

---

Prompt本文は一字一句変更せず、全モデルに同じ本文を渡す。

なお、Trial用の出力解析やValidatorは別処理として実装してよい。モデル別のPrompt最適化は行わない。

## 5. Trial実行

- 6モデル×14本文＝最大84回の選定。
- 1モデル・1本文につき初回生成1回を原則とする。
- 品質上の失敗も比較結果なので、選定結果が悪いことを理由に自動再生成しない。
- API障害など技術的失敗は、品質結果と区別して記録する。
- 独立したAPI呼び出しは、レート制限と費用管理の範囲内で並列実行する。
- 既存ProductionのKey Phraseは比較用に取得するだけとし、再生成しない。

## 6. Excel出力形式

ユーザー提示の画像に準拠し、**同じ記事・同じレベルでモデル別の結果を横並び比較できるExcelファイル**を作成する。

基本構造：

- 記事A → Standard → Advanced → 記事B → Standard → Advanced … の順。
- 各レベル内に「既存Production Key Phrase」「モデル1〜6」の行を配置。
- 横軸をKey Phrase 1〜5とする。
- 各セルに英語表現と語数を記載。
- 5件未満の場合は残りを空欄とする。
- 既存Productionの表現は変更せず掲載する。

**追加シート**

1. 品質評価サマリ：モデル別・記事別の指示遵守率、違反内容、選定品質
2. 費用サマリ：モデル別の実費、記事セット単価、7記事セット合計
3. 検証詳細：各候補の本文根拠、原文位置、語数、一般化内容、判定結果

Excelファイルを開くだけで、モデル間の違いを比較できる状態とする。

## 7. 品質検証

**A. 機械検証**

- 語数をスペース区切りで再計算。
- 5語超の違反を検出。
- 本文中の連続した語句との対応を確認。
- 一般化部分と原文の対応を確認。
- 各モデルが自己申告した語数と実際の語数の不一致を記録。

一般化を含む本文一致については、置換前の原文spanを保存する。単純一致検査ができないものは無条件PASSにしない。

**B. 選定品質評価**

- 一般化すべき箇所を適切に一般化したか
- 上級者向けの語彙・慣用表現として価値があるか
- 易しすぎる表現が混入していないか
- フレーズが不自然・中途半端に切られていないか
- 5件を無理に埋めていないか

共通の評価基準でモデル間を比較し、主観的評価と機械的違反を区別する。

評価用AIが必要な場合は、選定元モデルに自己評価だけをさせず、独立した評価方法を使用する。評価費用も記録する。

**重要：不合格結果もTrial成果として保持し、修正してから比較表へ載せることは禁止。**

## 8. 費用・QCD

モデルごとに以下を記録する。

- 入力トークン
- 出力トークン（課金対象の思考トークン等を含む）
- 適用API単価
- 実際のAPI課金費用
- 1記事セット（Standard＋Advanced）当たりの選定費用
- 7記事セット合計
- 品質を満たしたKey Phrase 1件当たりの費用

既存ProductionのKey Phrase選定実費についても、取得可能なusage／cost記録から確認する。実測と推定を混同しない。

費用より品質を優先する。ただし不要なretry、追加生成、評価工程の過剰化を避ける。

承認済みの開発予算枠を遵守し、予算上限超過の見込みがあればSTOPする。

## 9. 結果報告・Trial Closeout

最終報告には以下を含める。

1. Excel比較ファイルへのアクセス方法
2. モデル別の本文一致・5語以内の遵守率
3. 一般化と上級学習価値の比較
4. 代表的な良い選定・悪い選定の実例
5. モデル別の実費・記事セット単価
6. 現行Lunaから変更する価値があるかというPM向け考察
7. Fableによる独立レビュー・Trial Closeout

**到達可能Status：`VALIDATED`／`REJECTED`／`USER_DECISION_REQUIRED`。**

`VALIDATED`でもProduction採用を意味しない。

Productionモデル・Prompt・選定ロジック・Validatorの変更は行わない。Trial専用実装と正式経路を分離する。

必要なTrial成果物、評価結果、費用記録をRepoへ保存し、Git反映と再現に必要な情報を報告する。

## 10. 進め方・STOP条件

既存仕様・過去Trial・正式Production経路を事前に確認する。ただし今回の独立した比較Trialに不要な調査・作業は行わない。

既存の仕組みを最大限再利用する。

**品質を守りながら、最短時間・必要十分な開発費で一括完了すること。**

技術的な軽微な問題は委任範囲内で自律解決する。未承認の仕様変更、重大な品質・安全問題、予算超過、指定モデルを使用できない場合など、承認境界に該当する場合のみSTOPして報告する。

Trial終了後はFableの独立評価を経て、ユーザーが6モデルの品質・費用を比較し、Production採否を判断できる状態まで仕上げること。
---

### 指示2
---
## Claude Codeへの追加指示：Trial Promptの軽微な調整許可

先ほどのKey Phrase選定・6モデル比較Trial指示について、Prompt固定条件を以下のとおり補足します。

**1. 調整許可範囲**

Prompt冒頭の「以下の記事から」など、Productionのデータ受け渡し方式や実行環境との整合に必要な文言調整は許可します。

ただし、**Promptの意味・選定条件・優先順位・品質基準は一切変更しないこと。**

**2. モデル間の公平性**

調整後のPromptは全6モデルに共通適用し、モデルごとに選定条件を変更しないこと。

**3. 変更報告**

軽微な調整について事前承認は不要です。

ただし、Trial終了時に以下を事後報告してください。

- 変更前の文言
- 変更後の文言
- 変更理由
- 選定条件・品質基準への影響がないことの確認

**4. その他**

上記以外のTrial条件・評価方法・STOP条件は、先ほどの指示から変更しません。

不要な確認・作業停止を行わず、承認範囲内で自律的にTrialを進めてください。
---

## 2. Fableの事前確認(あなたが再照合し、ズレがあれば開始前に報告)
- 現行Production KP選定: モデル=`gpt-6-luna`(`er006_model_routing_contract_01.py:50 SUPPORT_MODEL`)、方式=M2P0 DB hybrid(`er030_key_phrase_db_hybrid_selector_01.py`、shortlist+軽量prompt、`APPROVED_FOR_PRODUCTION` 2026-10-16、CURRENT_SPEC ~L1984)、KP選定優先順位=A方式(現行Prompt、CURRENT_SPEC ~L1229/L1253)。本Trialはこれらを変更しない。Trialの選定方式はユーザー指定Prompt(本文全文渡し)であり、Production方式とは別物である点を結果に明記する(モデル差とPrompt方式差を混同しない)。
- 単価の既知: `er009_n1_routing_governance_10_actual_model_cost.py:30,34`に`gpt-6-luna`(0.10/0.01/0.50 USD/M)・`gpt-6.1-sol`(2.00/0.10/10.00)。他4モデル(`gemini-3.1-flash-lite`/`gemini-3.5-flash-lite`/`claude-haiku-5-5`/`claude-sonnet-5-5`)の単価はrepo内`pricing_snapshot.json`等を探し、見つからなければ「未確認」と表記(推定単価を確定費用に使わない。実課金tokenは必ず保存)。`gemini-3.5-flash-lite`はProduction routing(`FAMILY_X_RF_GEMINI`)で使用実績あり=Geminiクライアントは既存。Anthropic APIは`er052_output/writer_dev_risk_flagger_01/meta_rollback_crossmodel_01/xm_driver.py`・`pre_sorter_blind_trial_01/model_check.py`に呼出実績あり(鍵名・クライアント生成はそこを参照。鍵の値を出力・保存しない)。
- 既存仕様/過去Trial照合(21節A/B/C): 過去のKP関連Trial(KP優先順位ABC `er064`、`no way`最小修正、KP DB hybrid設計、kp_english_lock、kp_advanced_explanation)を`docs/pm/REPORT_LEDGER.md`/`OPEN_ITEMS.md`を管理ID名でGrepして確認し、「KP選定の複数モデル比較」が過去に実施済みか(A/B/C)を1行で記録。過去に同種比較がある場合も本Trialは中止せず、相違点を記録して続行(ユーザー承認済みTrial)。
- 公平条件: 全モデルで同一system/user構成(systemは空または共通1行のみ)、温度・推論設定は**各providerの既定値**を使う(モデル別最適化禁止)。既定値を指定できない/強制される差(例: 推論tokenの有無、temperature固定)はそのまま記録。max_output_tokensは全モデル同一(不足で切れない十分な値、例4096。推論モデルは推論分込みで足りる値)。出力形式指示はPrompt本文に追加しない(Promptは固定)。解析は出力テキストから行い、解析不能はその旨を記録(解析のためにPromptへ形式指示を足したい場合は指示2の「実行環境との整合に必要な文言調整」に当たるかを慎重に判断し、足す場合は意味・条件・基準不変で全モデル共通、Before/After/理由/影響なし確認を報告に残す)。
- 語数の数え方(機械検証): 一般化後の文字列をスペース区切りで分割した個数(`~`・`A/B`・`someone`等も1語)。モデル自己申告との不一致は違反ではなく「不一致」として別記録。
- 本文一致(機械検証): (a)生の候補が本文中に連続部分列として存在(大小文字・末尾句読点の正規化のみ許容)→PASS。(b)一般化を含む場合はplaceholder(`~`,`A`,`B`,`someone`,`something`,`sb`,`sth`等)を可変長wildcardにした正規表現で本文を検索し、一意にマッチした原文spanを保存→PASS(原文span付き)。複数マッチは最初のspanを保存しつつ「要確認」、マッチなしはNG(創作/言い換え)。(c)どちらでも確認できないものを無条件PASSにしない。
- 独立評価(§7B): 選定元モデルによる自己評価のみを根拠にしない。方式=全84結果を**選定元と異なる評価モデル**で共通rubric(5観点、各0〜2点等)採点する。評価モデルは最新上位モデル原則(25節)に従い、`gpt-6.1-sol`と`claude-sonnet-5-5`の2系統で全行を採点し、選定元と同系統の評価は「参考」、異系統の評価を「主評価」とする(両方が異系統の行は平均)。評価費用を選定費用と分けて記録。評価rubricは`TRIAL_DESIGN_01.md`に固定してから実行。
- 「品質を満たしたKP」の定義(§8最終項): 厳格版=機械検証PASS(本文一致PASS∧5語以内)のみ、総合版=厳格版∧主評価が閾値以上(閾値は設計書で先に固定)。両方を出す。
- 記事の版: 正式制作済み(ユーザー受入済みまたは最新の正式経路完成版)の英語本文を使う。記事B「給料が上がると、性格も変わる？」はC-3が`run_pp_02`(再制作版)を完成させつつあり、旧`run_pp_01`も存在する。**run_pp_02の本文が存在すればrun_pp_02を使用**(最新の正式経路版。pp_01の存在も記録)。レベル名の内部対応(Family Xの内部dir名とStandard/Advancedの対応)はrunner(`er019_family_x_entertainment_production_runner_01.py`等)のコード・各runの`entry_point.json`/metadataで**確認してから**ラベル付けし、推測で付けない。記事G「ホルムズ海峡」は旧形式(候補: `er002_v1_2m_fact_registry/ADD03_hormuz.json`系のER-003 ADD03、`user_test/flash_lite_family_x_02_hormuz/`)で、レベル名がB1/A2等の可能性がある。旧記事はレベル名をそのまま記録し、Standard/Advanced欄に「相当」と明記(無ければ欠落と明記)。
- 既存Production KPの取得元: 各runの KP成果物(Store/`keywords*`/`kp*` json、assembled scriptのKey Phrase欄)。既存KP選定実費は各runの`raw_usage_log.jsonl`/`cost.json`からKP選定step(er030 selector呼出)のusageだけを抽出(抽出条件を明記。抽出できない記事は「未確認」)。

## 3. 実行内容
1. 開始前チェック(22節): 指示1 §1〜§10・指示2の全要求を列挙し、設計書(`TRIAL_DESIGN_01.md`)のどこで満たすかの対応表を作る(未反映1件でも有料呼出禁止)。STOPセンチネル・予算・6モデルの疎通(各1回の極小呼出、費用計上)を確認。疎通不可モデルがあれば§性質の禁止事項どおりSTOP報告(呼べる分の実行はFable判断待ち、開始しない)。
2. 抽出(API 0): 14本文(記事A〜G×2)・既存Production KP・記事識別子・版(run dir、commit、ファイルpath、sha256)を`er098_output/kp_six_model_trial_01/inputs/manifest.json`へ。欠落は明示。
3. 見積確定(API 0): 実トークン数(tokenizer概算可)×確認済み単価で見積→JPY300以下なら続行、超なら有料呼出前に報告。
4. 選定実行(有料): `er098_kp_six_model_trial_01_run.py`。84回、provider並列。各呼出で request/response全文・返却model ID・usage(入力/出力/推論/キャッシュ)・設定(温度・推論設定・max tokens)・所要時間・技術的失敗を`runs/<model>/<article>_<level>.json`へ保存。技術的失敗(timeout/5xx/429)は同一入力で最大2回まで再試行し回数を記録、品質理由の再生成は禁止。
5. 機械検証(API 0): `er098_kp_six_model_trial_01_validate.py`。§2の規則で候補ごとに 語数/自己申告語数/5語以内/本文一致種別(a/b/NG/要確認)/原文span/位置(文字offset)/一般化内容を`validation.json`へ。
6. 独立評価(有料): `er098_kp_six_model_trial_01_eval.py`。§2の方式。rubric・prompt・返却model ID・usage・費用を保存。
7. Excel(API 0): `docs/research/FAMILY-X-KP-SELECTION-SIX-MODEL-COMPARISON-TRIAL-01/KP_MODEL_COMPARISON_01.xlsx`(openpyxl。未導入なら`.venv\Scripts\python.exe -m pip install openpyxl`、導入した事実を報告)。シート1「比較表」=記事A→Standard→Advanced→記事B…の順、各レベル内に「既存Production」「1 gpt-6-luna」…「6 claude-sonnet-5-5」の行、横軸KP1〜5、セル=「表現 (語数)」、機械検証NGセルは塗り分け(凡例をシート内に置く)、5件未満は空欄。シート2「品質評価サマリ」(モデル別・記事別の本文一致率/5語以内率/自己申告不一致数/件数/主評価平均/違反内容)、シート3「費用サマリ」(モデル別 入出力token・推論token・単価(出典)・実費JPY・記事セット単価・7記事セット合計・厳格版/総合版の品質KP1件当たり費用・既存Production実費[実測/未確認])、シート4「検証詳細」(候補ごと: モデル/記事/レベル/候補/語数/自己申告/本文一致種別/原文span/位置/一般化内容/主評価・参考評価/判定)、シート5「条件・Prompt」(適用Prompt全文、調整Before/After/理由/影響なし確認、各モデルの設定差、返却model ID一覧、使用本文の版表)。
8. `TRIAL_RESULT_01.md`(同dir): ユーザー§9の1〜7の順(7はFable記入欄を空ける。6はPM向け考察の**材料**として事実ベースで書き、採否の推奨はFableが付ける)。加えて: 開始前チェック対応表/Prompt調整の事後報告(指示2 §3の4項目)/公平条件と差異/技術的失敗一覧/費用実測(出典・為替出典)と日次累計/良い選定・悪い選定の実例(各モデル最低1つずつ、本文根拠付き)/分類候補(`VALIDATED`/`REJECTED`/`USER_DECISION_REQUIRED`)と根拠。`TRIAL_DESIGN_01.md`に設計(rubric・閾値・検証規則・見積)を実行前に固定。
9. SSOT: `OPEN_ITEMS.md`に新規OPEN(直近番号をGrepで確認し次番号、例OPEN-444)「FAMILY-X-KP-SELECTION-SIX-MODEL-COMPARISON-TRIAL-01」Status `TRIAL_DONE_PENDING_FABLE`(Production採用未承認)。`docs/pm/REPORT_LEDGER.md`行追加。DECISION_LOGは書かない(採用判断はユーザー)。`docs/pm/USER_DECISION_REGISTER_01.md`は触らない(Fableが後で判断事項を起票)。T-0保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-22_FAMILY-X-KP-SELECTION-SIX-MODEL-COMPARISON-TRIAL-01_委任_01.md`(Nは jsonl 内で `FABLE-DELEGATION-MARKER: KP6M-TRIAL-RUN-委任_01-20261022` を含むAgent tool_useの0始まり通番、262前後。保存後に先頭行のマーカーで一致確認)。`check_delegation_prompt.py`実行(見出し不一致FAILは既知の偽陽性)。
10. commit→push→到達確認。`docs/pm/ACTIVE_TASK.md`先頭に固定ヘッダ(PM_BRIEF書式)。`docs/pm/RESULT_PACKET_KP6M1.md`へ報告。

## 事前指定Read一覧
- `er006_model_routing_contract_01.py:40-60`(Production KPモデル)、`er009_n1_routing_governance_10_actual_model_cost.py:20-60`(単価表)
- `er030_key_phrase_db_hybrid_selector_01.py:1-60, 389-460`(現行方式の把握・Prompt templateのload元`bk.load_prompt_template()`の所在確認のみ。編集禁止)
- `er052_output/writer_dev_risk_flagger_01/meta_rollback_crossmodel_01/xm_driver.py`(Anthropic/Gemini/OpenAI呼出の既存実装。鍵名の参照のみ)
- `er019_output/family_x_audio_production_wiring_01/manga_ai_chat_byus__run_byus_01/entry_point.json`、同dirの本文・KP成果物(レベル名対応の確認)
- `docs/pm/delegation_log/2026-10-22_PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01_委任_04.md`(Trial委任の体裁・RESULT_PACKET 4行の例)

## 事前指定Grep一覧+追記位置・更新位置の手順
- 記事run dirの特定: Glob `er019_output/**/entry_point.json`、`user_test/{coffee_*,paycheck_personality_e2e_0*,manga_ai_chat_byus_e2e_01,boredom_aggression_bape_e2e_01,meta_regen_01_asr_check,middle_east_yemen_saudi_e2e_02,flash_lite_family_x_02_hormuz}/`。Meta記事は`OPEN_ITEMS.md`で`Meta`をGrepし正式run(ユーザー受入版)を特定。
- 単価: Glob `**/pricing_snapshot*.json`、Grep `gemini-3.1-flash-lite|claude-haiku-5-5|claude-sonnet-5-5|gemini-3.5-flash-lite` in `*.json`/`*.py`/`docs/**/*.md`。
- 過去Trial: Grep `KP-IDIOM-PRIORITY|KEY-PHRASE-DB|kp_english_lock|KP-NO-WAY|モデル比較` in `docs/pm/REPORT_LEDGER.md`(headのみ)。
- OPEN番号: Grep `^\| OPEN-44[0-9]|OPEN-44[0-9]` in `OPEN_ITEMS.md` → 最大+1を新番号。追記位置=OPEN-443の直後行。
- REPORT_LEDGER: 末尾の`- 2026-10-22 |`行群の直後に1行追加。

## 実行コマンド全文
- 疎通/実行/検証/評価/Excel: `.venv\Scripts\python.exe er098_kp_six_model_trial_01_run.py --out er098_output/kp_six_model_trial_01 --manifest er098_output/kp_six_model_trial_01/inputs/manifest.json --cap-jpy 300`(引数名は実装に合わせ、実行した全コマンドを実値でRESULT_PACKETへ記録)
- secret scan: `.venv\Scripts\python.exe tools/secret_scan_01.py --staged`
- 回帰(Production無変更の確認、任意最小): `.venv\Scripts\python.exe run_project_regression.py --pattern "er030*_test*.py"`

## SSOT追記文
- OPEN_ITEMS(新規行): `| OPEN-4xx | FAMILY-X-KP-SELECTION-SIX-MODEL-COMPARISON-TRIAL-01 | 2026-10-22 | TRIAL_DONE_PENDING_FABLE | Family X KP選定の6モデル比較Trial(ユーザー承認済みTrial、Production採用未承認)。同一Prompt(ユーザー固定文、調整=<あれば1行>)・14本文(7記事×2レベル、版=inputs/manifest.json)・6モデル固定。結果=本文一致率/5語以内率/主評価平均/実費(モデル別、要約1行)。Excel=docs/research/FAMILY-X-KP-SELECTION-SIX-MODEL-COMPARISON-TRIAL-01/KP_MODEL_COMPARISON_01.xlsx。Production/Prompt/Validator無変更。Fable独立評価待ち。 |`(列構成は既存行に合わせる)
- REPORT_LEDGER: `- 2026-10-22 | FAMILY-X-KP-SELECTION-SIX-MODEL-COMPARISON-TRIAL-01 委任_01 | 6モデル×14本文=<n>回選定+独立評価、機械検証(本文一致/5語以内/自己申告差)、Excel 5シート、実費JPY<x>(出典paid_calls)。TRIAL_DONE_PENDING_FABLE、Production無変更。`

## Git(明示add対象・コミットメッセージ・trailer)
- SSOT編集権: `OPEN_ITEMS.md`・`docs/pm/REPORT_LEDGER.md`のみ可(自分の行だけ)。`CURRENT_SPEC.md`/`DECISION_LOG.md`/`docs/pm/PM_GOVERNANCE.md`/`docs/pm/USER_DECISION_REGISTER_01.md`は編集不可。
- add対象: `er098_kp_six_model_trial_01_*.py`、`er098_output/kp_six_model_trial_01/**`(鍵・個人情報なしを確認。responseに鍵が混入しないこと)、`docs/research/FAMILY-X-KP-SELECTION-SIX-MODEL-COMPARISON-TRIAL-01/**`、`docs/pm/delegation_log/2026-10-22_FAMILY-X-KP-SELECTION-SIX-MODEL-COMPARISON-TRIAL-01_*`、`OPEN_ITEMS.md`、`docs/pm/REPORT_LEDGER.md`。
- commit message例: `KP6M 委任_01: Family X KP選定6モデル比較Trial(同一Prompt・14本文・84選定+独立評価、機械検証、Excel 5シート、実費JPY<x>)、Production/Prompt/Validator無変更、TRIAL_DONE_PENDING_FABLE`。段階commit可(抽出→実行→Excel/SSOT)。

## 報告(RESULT_PACKET_KP6M1.md)
ユーザー§9の1〜7順(7はFable欄、6は事実材料)。加えて: 開始前チェック対応表/疎通結果と返却model ID/公平条件・設定差/Prompt調整の事後報告4項目/使用本文の版表(記事×レベル→path・commit・sha256、欠落)/既存Production KPの出典と実費(実測か未確認か)/機械検証の集計(モデル別 本文一致率・5語以内率・自己申告不一致・要確認件数)/独立評価の集計(主評価・参考評価)/良い・悪い実例/費用実測(選定・評価・疎通を分け、出典・為替出典、日次累計)/技術的失敗一覧/分類候補と根拠/RESULT_PACKET 4行((1)既存仕様整合 (2)未承認機能の既定値 (3)成果物 (4)撤去・残置)/実行コマンド全文/raw URL(TRIAL_RESULT_01.md、xlsx)。判断候補は`判断候補`と表記(USER_DECISION_REQUIREDラベルはFableのみ)。