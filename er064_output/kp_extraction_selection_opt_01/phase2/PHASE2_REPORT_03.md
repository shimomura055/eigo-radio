# PHASE2_REPORT_03: KP抽出・選定改善 Phase 2 最小有料Trial + 量産コスト試算
管理ID: FAMILY-X-KP-EXTRACTION-SELECTION-OPTIMIZATION-01 委任_03 / 日付2026-10-13 / Trial専用(Production code/Prompt無変更) / 採用判断なし
Status案: **USER_DECISION_REQUIRED**(方式1のshortlist部分=Coffee Advで効果確認[n=3、部分VALIDATED相当]、方式1のPrompt部分[C2]=未達・再設計候補、方式2=一部のみ測定、方式3=未測定)。VALIDATED/APPROVED_FOR_PRODUCTION/PRODUCTION_WIREDではない。
使用モデル: **gpt-6-luna**(Production同一。最新モデル原則の例外理由=Production比較可能性。cost_03.jsonの全121 callが`gpt-6-luna`)。reasoning effort等はProduction既定(selector factoryそのまま)。

## 0. 実行実績・費用
| 項目 | 値 |
|---|---|
| job数 | 42(C0 18 / C1 3 / C2 18 / C2' 3)、n=3、自動retryなし |
| LLM call数 | 121(選定42 + canonicalization/QA 79) |
| **累計費用(実測)** | **JPY36.2331 / 上限50**(停止規則48・見積44.58に対し約-8.3) |
| 最大1job / 最大1call | JPY1.2585(<2.5) / JPY0.7352 |
| Stage別 | Stage1(Coffee 18job)15.7803 → Stage2(meta 12)+9.9173=25.6976 → Stage3(hormuz 12)+10.5355=36.2331。各Stage前に「累計+見積≦48」を確認(28.7/38.6)。 |
| 起動 | 各Stage 1回のみ(再起動0、外部停止0、rc=0)。`timeout`/監督ループ/自動retryなし。起動前に`phase2/STOP`・`STOP_ALL`不在を確認 |
| Production state | `state_guard_03.json`: 8ファイル(cost_baseline/HR queue/Master Store manifest・reuse_telemetry/ledger/attempt_history/er021・er025 telemetry)のsha256が実行前後で**全Stage不変** |
| 忠実性確認 | C0の完全Promptが**Production実runの`keywords_selector_prompt.txt`とバイト一致**(coffee Std/Adv、meta Std/Adv)。C2 Promptが`specimen_after_*_v5_02.txt`とバイト一致(coffee Std/Adv)。**hormuz C0はProduction実runが旧方式のため照合不能**(現行構成の再生) |
| C2'の注釈 | V2 shortlist(Phase D成果物)は`contains:`/`contained_in:`注釈を生成しない既存builder出力のまま**注釈なし**で実行(builderで安全に付与する経路は未整備のため付与せず)。よってC2'は「注釈なし条件」(C2 Promptは注釈の説明文を含むが対象行が無い) |
コード: `er064_kp_opt_01_phase2_run_03.py`(runner)/`_analyze_03.py`/`_agg_03.py`。証跡: `phase2/`(`runs/*/job_result.json`、`selector_prompt.txt`、`cost_03.json`、`stage{1,2,3}_summary_03.json`、`analysis_03.{json,md}`、`agg_cost_03.json`、`prep_stage1_03.json`、`state_guard_03.json`)。

## 1. 層1: gate前のselector生出力(5件全文は`analysis_03.md`に全表)
### 1-1. 受入判定
| # | 受入 | 結果(n=3/セル、小標本) | 判定 |
|---|---|---|---|
| 1 | `time lag`選定(Coffee Adv) | C0 0/3(候補に無く`lag`単独3/3)、**C1 3/3、C2 3/3**(全てTopic)、C2' 0/2有効(`lag`単独1) | **改善**。ただし効果はshortlist由来(現行PromptのC1でも3/3)で、Prompt改善固有ではない |
| 2 | 記事独自比喩のImportant混入 | 方式1は測定不能(候補に無い)。測れる範囲: Coffee AdvのImportant 4枠×有効run: C0'(ABC-A) 2/12(`in the ring`2/3) → **C2' 0/8**。C0'(ABC-A) Stdは6/12(`two numbers in the ring`3、`its own hidden clock`3)だがC2' Std未実施(予算) | **方向は改善(Adv)**、Stdは未検証。n小 |
| 3 | `take time`/`right away`型の枠占有(Std) | C0 5/15枠(take time1、right away2、on a regular basis2) → C2 5/15枠(take time2、on a regular basis3、right away0)。Adv両方0 | **未改善**(`right away`は消えたが`on a regular basis`等が同数入る) |
| 4 | 断片回避 | 方式1は測定不能。観測: `lag`単独 C0 3/3 → C1/C2 0/6(`time lag`化)、C2' 1/2。`be behind`単独選択0、`in the ring`選択はC2'で0(C0' Advは2/3) | 部分的に改善傾向(測定不能部分あり) |
| 5 | Std/Adv双方 | Adv: `time lag`改善。Std: `push prices up`維持(3/3→3/3)、Topic `raw bean(s)`維持、`pump one's fist` 2/3→0/3、低優先枠5→5(不変)、`roasting`/`feel like`/`be based on`が入る | **Advのみ改善、Stdは横ばい** |
| 6 | meta/hormuzで悪化なし | meta: C2で`concierge` Std 3/3→0/2(有効run)、`bargain` 2→1、Adv `contract workers` 3/3→1/2(+単数形Topic 1)。代わりに`inappropriate`/`take care of`が入る。hormuz: `center stage` Std 0/2→3/3・Adv 2/3→3/3(改善)、`sea blockade`はTopicが`Brent crude`へ置換(同等の良ラベル)、`give back gains` 6/6(後述の表示拡張) | **metaで悪化の兆候あり(n=2有効)、hormuzは同等〜改善** |
| 7 | Topic/Important役割の妥当性 | 有効job全てTopic 1件。C2のTopic: Coffee Std `raw beans`3/3、Adv `time lag`3/3、hormuz `Brent crude`/`sea blockade`、meta `contract workers`。記事独自比喩のTopic採択は方式1では出ず(測定不能) | 所見のみ(悪化なし) |
| 8 | gate・費用 | §2・§3 | §2・§3参照 |

### 1-2. 付随所見(新発見、報告のみ。実装・採用しない)
- **表示拡張**: LLMは候補より長い`display_phrase`を書くことがある(`gave back`→`give back gains`、`pumps`→`pump one's fist`、`prices up`→`push prices up`、`comes with`→`come with costs`、`Taken Back`→`take back a plan`)。C2 Prompt(【学ぶ単位】)は拡張を増やした(hormuz `give back gains` 6/6、C0は0/6)。従来「方式1では測定不能」とした`push prices up`/`give back gains`/`pump one's fist`は、実際にはこの拡張で出現する。ただし拡張語(`gains`/`costs`/`a plan`)が記事内のsource_spanに無い点は`inherit_selection_normalization`で通過する。
- 未ラベル所見: Coffee Advで`hold on`が有効11 job中10 jobで採択(記事内の発話引用由来と思われる。期待ラベル未登録)。ユーザー確認事項。
- C2は選定出力token(reasoning)が約+34%(4,345 vs 3,234/job)。
- Jaccard平均(n=3、有効run間): Coffee Std C0 0.31→C2 0.59、Coffee Adv C0 0.78→C1 0.67→C2 0.51(`come with`/`show up in prices`等の揺れ)、meta Adv C2 0.25(有効2)、hormuz Std 0.67→0.62、Adv 0.78→0.67。安定性は一貫した改善なし。

## 2. 層2: gate別(選定能力と分離して集計)
| 条件 | 選定INVALID | canonicalization INVALID | Redundancy NG / 分母(canon通過) | 全gate PASS |
|---|---|---|---|---|
| C0(18) | 1(hormuz Std) | **2**(meta Std・meta Adv) | 5 / 15 | 10/18 |
| C1(3) | 0 | 0 | 0 / 3 | 3/3 |
| C2(18) | **2**(meta Std・meta Adv) | **0** | 6 / 16 | 10/18 |
| C2'(3) | 1(Coffee Adv) | 0 | 0 / 2 | 2/3 |
- 選定INVALID 4件の原因(Production gateが検出): `normalization_note`が空(C0 hormuz Std、C2 meta Std)、グロスに括弧書き(C2' Coffee Adv。D12グロス統合の副作用ではなく既存gateが捕捉)、有限助動詞(C2 meta Adv)。Productionは`MAX_PRODUCTION_RETRY_ATTEMPTS=2`で再試行するため、本Trial(retryなし)の失敗はProductionでは1回目再試行の対象。
- canonicalization INVALID 2件(いずれC0): 表示語(`no way to know`/`the other end`)がsource_span(`no way`/`other end`)外へ拡張されRule7(source_spanに無い辞書形を作らない)に違反。**Rule7予測INVALID 35組(所有格代名詞系)には1件も該当しない**=予測外の新サブクラス。一方C2では同種の拡張(`no way to know`、`give back gains`等)が`inherit_selection_normalization`でPASSしており、validator判定が出力揺れに依存する(OPEN-310へ追記)。所有格系35組は、本42 jobでは該当候補が選ばれず顕在化せず(未検証であり安全の証拠ではない)。
- Redundancy NGは**hormuzの全有効job(C0 5/5、C2 6/6)**で発生(`give back`と`pull back`の意味重複)。条件差ではなく記事×候補構造に起因し、選定能力ではなくQAの結果。Redundancy QAの分母はcanonicalization通過job(INVALIDはQA未実行)。
- ja_gloss機械検査(括弧・算用数字・「…」・数値穴埋め形): 有効38 jobで**検出0**(グロス統合D12の副作用は今回の範囲で検出されず。n小)。

## 3. 量産コスト・時間試算(実測usageから再推計)
実測: 1 job = 選定1call + canonicalization/Redundancy QA 約2call。単価gpt-6-luna(`pricing_snapshot.json`経由、USD/JPY=160)。
| 項目 | 現行(C0) | 方式1(C2: guarded+新Prompt) | 方式2(Pkg E: LLM補助抽出)追加分 | 方式3 |
|---|---|---|---|---|
| KP工程 円/Level(実測平均) | Std 0.837 / Adv 0.836 | Std 0.898 / Adv 0.867(+約5.5%) | C2'実測0.765(Adv、n=3、無効1含む)+抽出0.116〜0.25/Level(Phase D実測: 抽出18call平均0.116、M1 6call平均0.250) | **未測定**(定義のみ。新規実測なし) |
| Std+Adv 1セット | 1.673 | 1.765 | +0.23〜0.50(抽出を両Levelに発火した場合) | — |
| 1,000セット | **JPY1,673** | **JPY1,765**(+92) | 発火率0%: 1,765 / 25%: 1,823〜1,890 / 50%: 1,881〜2,015 / 100%: 1,997〜2,265 | — |
| retry1回込み推定(1,000セット) | 約1,766(選定INVALID 1/18≒5.6%) | 約1,961(2/18≒11%) | — | — |
| 追加LLM call/job | 基準(選定1+canon/QA約2) | 同(1+1.78) | +1(抽出)/発火Level | — |
| API時間/job(6並列実測) | 選定53s+QA46s | 選定67s(+14s)+QA41s | 抽出+18〜39s | — |
| Wiktionary照会時間 | 約10秒/記事(2call) | 拡大: 約43秒/記事(8call、429待ち込み。+33秒)。**オフライン索引化なら約0秒**(提案、OPEN-337候補) | 同左+抽出 | — |
| 品質(Trial) | Adv `time lag`0/3、Std低優先枠5/15 | Adv `time lag`3/3、Std低優先枠5/15不変、meta悪化兆候、選定出力token+34% | Important創作比喩 Adv 2/12→0/8(Std未検証) | — |
- retry込み推定は観測の選定INVALID件数1件と2件の差に基づく(統計的に有意でない)。
- 方式2の発火条件案: 「shortlist内に定着語(辞書hit)が少ない/記事独自の比喩が疑われる(`fragment_risk`注釈候補が多い、Wiktionary未登録の連続2〜3語が多い)場合のみ抽出を呼ぶ」。誤判定時の品質リスク: 誤不発火=創作比喩がImportant候補に残る(現状どおり)、誤発火=費用と時間の増加のみ(+JPY0.12〜0.25/Level)でも品質は下がらない見込み。発火条件自体は未検証案。
- 品質改善1件あたりの追加費用: Adv `time lag`採択 0/3→3/3は+JPY0.03/job(C2)〜+0.16/job(C1、n=3の揺れ)で実質ほぼ0。Std低優先枠は改善0件のため費用対効果なし。Important創作比喩の除去(Adv)は抽出1call分+JPY0.12〜0.25/Level。
- TTS等を含む総製造原価への影響: PM_GOVERNANCE 15-8のFamily X総原価は`¥xx`のテンプレートのままSSOT内で確定値を確認できず、比率は算出不能(本Trialでは未確認)。KP工程の絶対増分(上表)のみ。
- 1,000セット費用はKP工程のみ(記事Writer・TTS・ASR等を含まない)。

## 4. 将来採用時の反映範囲(整理のみ、採用していない)
初回Production選定(shortlist builder・候補行builder・選定Prompt静的部/guidance)、選定retry(`MAX_PRODUCTION_RETRY_ATTEMPTS=2`の再試行が同一Prompt/shortlistを使うこと)、fallback(Strategy L全文選定=Primary失敗時の別経路)、validator/canonicalization(Rule7の表示拡張扱い)は、いずれも採用承認後に別委任でコード確認が必要(本Trialでは未確認)。schema(出力項目)は不変で、`established_or_article_specific`欄は使っていない。OPEN-151(Voices Writer可変化、APPROVED_FOR_PRODUCTION・未配線)は別件で本件と依存関係なし。KP選定の改善はAPPROVED_FOR_PRODUCTIONではなく、Productionコード・Promptへの配線は0件。

## 5. 制約・限界
- n=3/セル。meta/hormuzのC2は選定INVALIDにより有効run数が2〜3。C1はCoffee Advのみ、C2'はCoffee Advのみ(Std未検証)。方式1+方式2併用(guarded+V2の統合shortlist)は未検証。
- Production state不変は前後sha一致で確認。hormuz C0はProduction実runと照合不能。
- 6並列実行のため所要秒は単独実行より長めの可能性。
