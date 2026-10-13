# ROUND1_REPORT_01: KP統合最適化 Round 1(広く比較)
管理ID: FAMILY-X-KP-INTEGRATED-OPTIMIZATION-TRIAL-01 委任_01 / 日付2026-10-13 / Trial専用(Production code/Prompt/DB無変更、音声生成なし) / **採用判断なし**
Status案: **USER_DECISION_REQUIRED**(Round 1の結果は「供給側(M2)が最大効果、Prompt側(P1-P4)は単独でも統合でもP0を超えず、一部は悪化」。VALIDATED/APPROVED_FOR_PRODUCTION/PRODUCTION_WIREDではない。Round 2方針の選択はFable/ユーザー判断)
使用モデル: **gpt-6-luna**(選定・canonicalization・Redundancy QAすべて。全257 callのmodel_idが`gpt-6-luna`)。最新世代の最上位か: Production KP選定の`SUPPORT_MODEL`と同一で、PM_GOVERNANCE 25節の例外「Production比較可能性」(委任文指定)。最上位系モデルでの検証は未実施。
n=3/セル(他記事n=2)の小標本。差が1-2 runの比較は有意ではない(方向の目安)。

## 0. 実行実績・費用・時間
| 項目 | 値 |
|---|---|
| 費用(実測) | **JPY80.7198 / Round1上限100**(ハードストップ95に未達)。本Trial累計 80.72 / 300 |
| 見積 vs 実績 | 事前見積(保守: Std1.185/Adv0.938) 80.67 に対し実績 80.72。Stage別: Stage1 32.78(見積38.21)、Stage2 32.81(見積38.21)、Stage3 15.14(見積16.98)。Stage2を6組合せに拡張した分を含む |
| job / call | 88 job(Coffee 72 + meta/hormuz 16)、257 call(選定88 + canonicalization/QA 169)、自動retryなし、外部停止0、rc=0、起動はStageごとに各1回(再起動0) |
| 1 job費用 | Coffee平均 約0.90(P0 0.90 / P1 0.90 / P2 0.90 / P3 1.00 / P4 0.90)。最大job <2.5(上限未達) |
| 所要時間 | 3 Stage合計の実時間約28分(6並列。Stage1 約10分 / Stage2 約10分 / Stage3 約5分)。job平均98秒(選定+QA) |
| tokens | 選定call: 入力326,566 / 出力453,656 / reasoning 314,431。QA: 入力494,347 / 出力437,493 / reasoning 247,837(`cost_r1.json`) |
| Production state | `state_guard_r1.json`: 8ファイルのsha256が実行前後で全Stage不変(`unchanged_after_stage1/2/3` = true) |
| 忠実性 | M0P0の完全PromptがProduction実run `keywords_selector_prompt.txt` とバイト一致(coffee Std/Adv、meta Std/Adv)。M0P0=前回Phase2のC0、M1P0(Adv)=前回C1とsha一致。meta/hormuzのM0P0基準は前回Phase2のC0(n=3)を再利用(Prompt sha一致を`baseline_reuse_check_r1.json`で確認、再実行せず) |
| test | `er064_kp_int_01_test_01.py` 22件PASS(`test_results_r1.txt`): Production .py無変更、P0=Production逐語、6指標順序行逐語、Coffee語句不在(Prompt全文・Trialコード文字列)、アンカーはeval専用、token<=現行、sha整合、M0/M1が前回固定shortlistと一致、M3はM2に`match:`を足すだけ、cost/state整合 |

## 1. 前提の訂正(重要)
委任文は「(a)placeholder照合+(c)予約枠でpumps its fist→pump one's fistを回収可能(Phase Bで確認)」としていたが、実測では**(a)単独はCoffee Std/Adv(v5)で新規ヒット0件**だった(Wiktionary DBに`pump one's fist`見出しが無いため。Phase B報告にも「Coffee v4への新規ヒットは0件」とある。回収できたのは(b2)ルール所有格3-gram+(c)予約枠のV3構成)。よってM2は **(a)placeholder + (b2)ルール所有格3-gram + (c)予約枠(cap3)** で定義した(追加LLM呼出なしは維持)。ほか1点を決定論的に追加: 句読点をまたぐ3-gram(`news, your wallet`型)は本文の空白連続一致で除外(Phase Dの決定論検証と同種)。`be behind price increases`は(a)でも(b2)でも供給できず、**どのMパターンでも候補に無い**(供給不足。(b1)LLM補助抽出が必要=未承認)。

## 2. A. 機械抽出パターン(¥0、10記事・各M0-M3)
定義: M0=現行(Production再生) / M1=guarded(照会予算拡大+precision guard+U2包含整理+U3断片注釈) / M2=M1+(a)placeholder+(b2)ルール3-gram+(c)予約枠cap3(候補末尾に追加、cap15の外側) / M3=M2+候補行へ`| match: exact|inflected|term|placeholder|pattern`(辞書一致の確かさ。語彙表のみ/ヒューリスティック候補には付けない)。M4(cap・整列の別案)は、Coffeeで機械側の失敗要因がcap・整列にない(アンカー到達はcapで落ちていない)ため作成しない(R2で必要なら)。
固定shortlist(実タイトル): `shortlists_r1.json`(sha256 `2d9eaaecc083b141…`、`shortlists_r1.sha256.txt`)。M0/M1は前回の`shortlists_fixed_02.json`とrows完全一致(test)。
| 項目 | M0 | M1 | M2 | M3 |
|---|---|---|---|---|
| 候補数(10記事平均) | 22.7 | 23.3 | 24.0 | 24.0 |
| 候補行token(平均、tiktoken) | 1655 | 1714(+59) | 1746(+91) | 1789(+134) |
| Coffee Std/Adv候補数 | 26 / 32 | 26 / 33 | 28 / 34 | 28 / 34 |
| shortlist構築時間(snapshot再生) | 秒未満 | 秒未満 | 秒未満(ルール照合は誤差) | 同左 |
| Wiktionary実照会時間(前回実測) | 約10秒/記事(2call) | 約43秒/記事(8call、429待ち込み) | M1と同じ+0秒 | 同左 |
アンカー到達(候補に届くか、`screening_r1.json`):
- Std: 記事に存在するアンカー7件のうち、M0/M1は`pump one's fist`が**候補に無い**(断片`pumps`(word)のみ)、`push prices up`は断片`prices up`(phrasal_verb)のみ(LLMが表示で`push prices up`へ拡張)。M2/M3で`pumps its fist`がfull到達。残り(roasting/raw beans/on a regular basis/right away/take time)は全Mでfull到達。
- Adv: M0は`time lag`が候補に無い(`lag`単独のword)。M1以降でfull到達(U1予算拡大+U2整理)。M2以降で`pumps its fist`full到達。`be behind price increases`は全Mで未到達。
`take time`型(`take time`/`right away`/`on a regular basis`)は全Mで削除せず残す(testで固定)。選定側で下位評価に任せる。
誤除外(M0→M1でshortlistから消えたもの): Coffee Adv `at that`/`of a`(U3閉クラス)/`lag`(U2、time lagに包含)、meta Adv `inappropriate`/`negotiate`、semi Adv `calculator`、smallbag `clearer`/`luggage`/`runway`/`lip`、hormuz `crude`(包含)、meta/semi Std `of a`。うちmeta Adv `inappropriate`は基準M0P0で2/3採用されていた語で、M1/M2の候補からは外れる(誤除外の可能性。R2で確認)。M1の追加は`want to`(Coffee Adv/semi)、`close to`、`call it`、`take care`、`be wrong`、`report card`等で、精度は混在(`want to`型は低価値)。
M2の予約枠(ルール雑音): Coffee Std `pumps its fist`/`imagine your usual`、Adv `pumps its fist`、semi Std `match its forecast`/`make your eyes`、semi Adv `made your eyelids`、smallbag Std `among its fall`。目視で妥当と言えるのはpump/matchの2-3件(精度は低い)。ただし**Coffeeの全M2/M3 36 runで予約枠から選ばれたのは`pumps its fist`のみ(12回)**で、雑音候補は一度も選ばれず、候補数増(+2〜+3)とtoken増(+約90)の費用だけが出る。

## 3. B. 選定Prompt P0-P4(¥0設計、`prompts_r1.json`にsha・token・逐語)
各P1-P4は一から書き直した全文。共通の契約ブロック(Production gateが要求する出力契約): 日本語グロス段落、出力ルール(候補ID・surface_echo・backup)、6指標の順序行(逐語)、注釈説明文(contains:/contained_in:/fragment_risk/match:)。Coffee語句はtestで不在確認。出力schemaはProduction同一(追加フィールドなし)。
| P | 設計の核 | token(Std/Adv、text-only。現行1402) |
|---|---|---|
| P0 | Production現行逐語 | 1402 / 1402 |
| P1 | 学習価値(初見の困難x学習後の価値)を見積もり候補どうしを比較 | 1274 / 1291 |
| P2 | 意味が構成語の足し算にならない表現(慣用句・比喩・句動詞/連語を同等)を明確に優先。辞書登録だけでは優先しない。筆者独自の創作比喩はTopic可・Important不可。Topicのために良いImportantを減らさない | 1324 / 1341 |
| P3 | 候補を点数化せず比較し、仮選定後に「枠に値するか」「より価値の高い候補が残っていないか」で入れ替え確認。Topic/Importantを別々に比較 | 1278 / 1295 |
| P4 | P1-P3の要点を簡潔に統合 | 1197 / 1214 |
6指標対応表と矛盾チェックは`static_eval_r1.md`(要点: ユーザー選定基準は既存6指標の「見方」を補う位置づけで順序は不変。P2のImportant制約と契約「重要語区分から1個」の軽い緊張、M3注釈が高優先の暗示にならないか、は実測で確認)。**未承認の優先順位変更をProduction仕様と混同しない**: P1-P4はTrial専用で採用判断なし。

## 4. C. スクリーニングと実行組合せ
20組合せ(4M x 5P)→有料12組合せ(`plan_r1.md`、事前登録)。除外: M3P0(P0は`match:`注釈を説明せず未説明ラベルを渡す条件になる)。M1をP1-P4と組まない(M2がM1の上位、Coffeeでは予約枠の有無だけの差)。**事前登録からの変更(Stage1の結果を見たうえでStage2実行前に記録)**: Stage2を`M0P1,M0P3,M0P4,M2P4`の4組合せから`M0P1,M0P3,M0P4,M2P1,M2P3,M2P4`の6組合せへ拡張し、M(M0/M2) x P(P0-P4)の2x5要因配置を完成(M2P2はStage1実施済み)。Stage3(meta/hormuz、n=2)は事前登録規則で機械選択: **M2P0とM2P3**(`stage3_plan_r1.json`)。meta/hormuzではM2=M1(予約枠0件)。Coffee実行: 機械のみ(M1P0,M2P0)/Promptのみ(M0P1-P4、M0P2)/統合(M2P1-P4,M3P4)+基準M0P0、n=3 x Std/Adv。

## 5. D. 評価
アンカー評価は`anchors_r1.json`(評価専用ファイル。Prompt/shortlist builder/runnerから参照しないことをtestで確認)。score = run内の最終5件に含まれるアンカー(full一致)の重み(13-rank)の合計。上限(記事に存在するアンカーのtop5)はStd 37、Adv 47。順位に基づく簡易スコアであり、アンカー外の有用表現は評価しない(定性は§5-3、5-4)。

### 5-1. M x P 比較表(Coffee、Std+Adv合算。機械のみ/Promptのみ/統合)
| combo | 分類 | score合計(Std+Adv、上限84) | pump採用 | time lag採用(Adv) | 低優先枠/run | sel PASS | 全gate PASS(canon PASS+Red PASS) | Jaccard | 費用/job | reasoning tok(選定)/job |
|---|---|---|---|---|---|---|---|---|---|---|
| M0P0 | 基準 | 47.0 | 2/6 | 0/3 | 1.33 | 6/6 | 5/6 | 0.55 | 0.87 | 2854 |
| M1P0 | 機械のみ(guarded) | 51.3 | 1/6 | 3/3 | 1.83 | 6/6 | 6/6 | 0.63 | 0.87 | 2922 |
| M2P0 | 機械のみ(+供給) | 71.3 | 6/6 | 3/3 | 1.17 | 6/6 | 5/6 | 0.68 | 0.89 | 2992 |
| M0P1 | Promptのみ | 37.0 | 0/4 | 0/1 | 1.17 | 4/6 | 4/6 | 0.33 | 0.78 | 3772 |
| M0P2 | Promptのみ | 37.7 | 0/6 | 0/3 | 1.33 | 6/6 | 4/6 | 0.59 | 0.93 | 3608 |
| M0P3 | Promptのみ | 38.3 | 0/6 | 0/3 | 1.17 | 6/6 | 3/6 | 0.70 | 1.04 | 4185 |
| M0P4 | Promptのみ | 36.0 | 0/4 | 0/3 | 0.83 | 4/6 | 1/6 | 0.39 | 0.86 | 3880 |
| M2P1 | 統合 | 45.3 | 0/6 | 3/3 | 1.00 | 6/6 | 5/6 | 0.79 | 0.92 | 3901 |
| M2P2 | 統合 | 56.7 | 2/6 | 3/3 | 1.33 | 6/6 | 5/6 | 0.79 | 0.94 | 3016 |
| M2P3 | 統合 | 62.0 | 4/6 | 3/3 | 0.67 | 6/6 | 6/6 | 0.59 | 0.93 | 3782 |
| M2P4 | 統合 | 47.3 | 0/6 | 3/3 | 1.00 | 6/6 | 4/6 | 0.60 | 0.94 | 3910 |
| M3P4 | 統合(+注釈) | 49.5 | 0/5 | 3/3 | 1.25 | 5/6 | 3/6 | 0.83 | 0.96 | 3504 |
読み取り(n=3、方向の目安):
- **機械のみ**: M1P0は`time lag`供給で Adv 3/3(基準0/3、`lag`断片3/3)。M2P0は`pumps its fist`供給でpump 6/6(基準2/6)、score 47.0→71.3(上限84)。**最大の改善は供給側(M2)**。M1の低優先枠は1.83/runと基準(1.33)より悪化(Std 2.67)。
- **Promptのみ(M0)**: P1-P4は全て基準を下回る(36.0〜38.3 vs 47.0)。供給されない項目(time lag/pump)には届かず、さらにP1/P4はselection INVALIDが増えた(P1 Adv 2/3、P4 Std 2/3。理由はそれぞれ「日本語グロスに括弧書き」「normalization_noteが空」)。`pumps`(word断片)からのLLM拡張(基準で2/6)も全P・全条件で0になった。
- **統合(M2)**: P0が最良(71.3)、P3が次点(62.0、pump 4/6、低優先枠0.67/runで全条件中最少)、P2 56.7(pump 2/6: Advで0/3)、P4 47.3 / P1 45.3(pump 0/6)。M3P4(注釈あり)49.5はM2P4(注釈なし)47.3と同程度(M3P4はStd selection INVALID 1/3を含む)=**`match:`注釈の効果は確認できず**。
- **P1/P4でpumpが0/6になった理由(仮説、未検証)**: Production現行の「比喩・感情表現を同格の候補として扱う」文をP1/P2/P4が書き直しで落とし、代わりに「再利用価値」「他の記事でも使える」「透明表現を下げる」を強調したため、`wallet pumps its fist`型の擬人的比喩が「記事固有の言い回し」寄りに評価された可能性。P3だけ4/6残ったのは、比較と入れ替え確認の枠組みで候補が残ったため(同)。

### 5-2. アンカー表現の候補到達/選定(採用回数/有効run数、[R]=full到達 [r]=断片のみ [x]=候補に無し)
### アンカー採用回数 Coffee STD (full一致、n=3、分母=有効run数)
| アンカー | M0P0 | M1P0 | M2P0 | M0P1 | M0P2 | M0P3 | M0P4 | M2P1 | M2P2 | M2P3 | M2P4 | M3P4 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 pump one's fist | 2/3 [r] | 0/3 [r] | 3/3 [R] | 0/3 [r] | 0/3 [r] | 0/3 [r] | 0/1 [r] | 0/3 [R] | 2/3 [R] | 2/3 [R] | 0/3 [R] | 0/2 [R] |
| 3 push prices up | 3/3 [r] | 2/3 [r] | 3/3 [r] | 1/3 [r] | 3/3 [r] | 2/3 [r] | 1/1 [r] | 1/3 [r] | 3/3 [r] | 3/3 [r] | 3/3 [r] | 2/2 [r] |
| 7 roasting | 0/3 [R] | 1/3 [R] | 1/3 [R] | 3/3 [R] | 0/3 [R] | 2/3 [R] | 0/1 [R] | 3/3 [R] | 1/3 [R] | 1/3 [R] | 1/3 [R] | 1/2 [R] |
| 8 raw beans | 3/3 [R] | 3/3 [R] | 3/3 [R] | 3/3 [R] | 3/3 [R] | 3/3 [R] | 1/1 [R] | 3/3 [R] | 3/3 [R] | 3/3 [R] | 3/3 [R] | 2/2 [R] |
| 9 on a regular basis | 1/3 [R] | 3/3 [R] | 2/3 [R] | 3/3 [R] | 3/3 [R] | 3/3 [R] | 1/1 [R] | 3/3 [R] | 3/3 [R] | 3/3 [R] | 3/3 [R] | 2/2 [R] |
| 11 right away | 3/3 [R] | 3/3 [R] | 2/3 [R] | 1/3 [R] | 1/3 [R] | 1/3 [R] | 0/1 [R] | 0/3 [R] | 0/3 [R] | 0/3 [R] | 0/3 [R] | 0/2 [R] |
| 12 take time | 2/3 [R] | 2/3 [R] | 1/3 [R] | 0/3 [R] | 1/3 [R] | 0/3 [R] | 0/1 [R] | 0/3 [R] | 2/3 [R] | 0/3 [R] | 1/3 [R] | 1/2 [R] |
[R]=候補にfull到達 [r]=断片のみ到達 [x]=候補に無い

### アンカー採用回数 Coffee ADV (full一致、n=3、分母=有効run数)
| アンカー | M0P0 | M1P0 | M2P0 | M0P1 | M0P2 | M0P3 | M0P4 | M2P1 | M2P2 | M2P3 | M2P4 | M3P4 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 pump one's fist | 0/3 [x] | 1/3 [r] | 3/3 [R] | 0/1 [x] | 0/3 [x] | 0/3 [x] | 0/3 [x] | 0/3 [R] | 0/3 [R] | 2/3 [R] | 0/3 [R] | 0/3 [R] |
| 2 be behind price increases | 0/3 [x] | 0/3 [x] | 0/3 [x] | 0/1 [x] | 0/3 [x] | 0/3 [x] | 0/3 [x] | 0/3 [x] | 0/3 [x] | 0/3 [x] | 0/3 [x] | 0/3 [x] |
| 4 time lag | 0/3(+断片3) [r] | 3/3 [R] | 3/3 [R] | 0/1(+断片1) [r] | 0/3(+断片1) [r] | 0/3(+断片3) [r] | 0/3(+断片3) [r] | 3/3 [R] | 3/3 [R] | 3/3 [R] | 3/3 [R] | 3/3 [R] |
| 5 show up | 3/3 [R] | 3/3 [R] | 3/3 [R] | 1/1 [R] | 3/3 [R] | 3/3 [R] | 3/3 [R] | 3/3 [R] | 3/3 [R] | 3/3 [R] | 3/3 [R] | 3/3 [R] |
| 6 come down | 3/3 [R] | 3/3 [R] | 3/3 [R] | 1/1 [R] | 3/3 [R] | 3/3 [R] | 3/3 [R] | 3/3 [R] | 3/3 [R] | 3/3 [R] | 3/3 [R] | 3/3 [R] |
| 7 roasting | 0/3 [R] | 0/3 [R] | 0/3 [R] | 0/1 [R] | 0/3 [R] | 0/3 [R] | 0/3 [R] | 0/3 [R] | 0/3 [R] | 0/3 [R] | 0/3 [R] | 0/3 [R] |
| 8 raw beans | 2/3 [R] | 0/3 [R] | 0/3 [R] | 0/1 [R] | 0/3 [R] | 0/3 [R] | 0/3 [R] | 0/3 [R] | 0/3 [R] | 0/3 [R] | 0/3 [R] | 0/3 [R] |
| 9 on a regular basis | 0/3 [R] | 0/3 [R] | 0/3 [R] | 0/1 [R] | 0/3 [R] | 0/3 [R] | 0/3 [R] | 0/3 [R] | 0/3 [R] | 0/3 [R] | 0/3 [R] | 0/3 [R] |
| 10 hold on | 1/3 [R] | 3/3 [R] | 2/3 [R] | 1/1 [R] | 2/3 [R] | 3/3 [R] | 2/3 [R] | 3/3 [R] | 3/3 [R] | 1/3 [R] | 2/3 [R] | 3/3 [R] |
| 11 right away | 1/3 [R] | 0/3 [R] | 0/3 [R] | 0/1 [R] | 1/3 [R] | 0/3 [R] | 0/3 [R] | 0/3 [R] | 0/3 [R] | 0/3 [R] | 0/3 [R] | 0/3 [R] |
| 12 take time | 0/3 [R] | 0/3 [R] | 0/3 [R] | 0/1 [R] | 0/3 [R] | 0/3 [R] | 0/3 [R] | 0/3 [R] | 0/3 [R] | 0/3 [R] | 0/3 [R] | 0/3 [R] |
[R]=候補にfull到達 [r]=断片のみ到達 [x]=候補に無い
`take time`型(アンカー9-12)の枠占有(run平均、5枠中): 基準 Std 2.0 / Adv 0.67、M2P0 Std 1.67 / Adv 0.67、M2P3 **Std 1.0 / Adv 0.33**、M2P2 Std 1.67 / Adv 1.0。P3だけが低優先枠を明確に減らした(Std: `on a regular basis`は3/3残るが`right away`/`take time`が0/3)。他のPは現行並み(`on a regular basis`は新Prompt下でむしろ増加: M0P1-P3/M2P1-P4でStd 3/3)。`right away` Std: 基準3/3 → M2のP1-P4で0/3(改善)。`take time` Advは全条件0/3。
創作比喩のImportant混入(`in the ring`/`hidden clock`/`unseen clock`/`flash to a new price`等): **全条件で0**(Coffee v5のM0-M3のshortlistにそれらの候補が存在しないため、測定上の0。前回ABC(v4+V2 shortlist)の6/12とは入力が異なる。P2の創作比喩規則の効果は本Round1では測れていない)。Topic: Std `raw bean(s)` 基本3/3、Adv `time lag`(M1以降)/`lag`(M0)/`price tag`/`retail prices`(P2-P4のM0)。

### 5-3. 候補に存在したのに選ばれなかった有用表現
- `pumps its fist`(M2/M3で候補にfull到達): P0で6/6採用だが、P1 0/6、P4 0/6(M3P4と合わせ0/11)、P2 Adv 0/3。不採用のrunでは代わりに`on a regular basis`、`based on`、`feel like`(基本連語)や複合名詞(`price tag`)が選ばれた(`analysis_r1.md`の各run)。
- `time lag`(M1以降のAdv): 採用3/3で問題なし。
- Adv `comes with`: 新Prompt下でほぼ毎run採用(基準でも1/3)。学習価値は中程度。
- Std `roasting`: P1(M0/M2)で3/3採用されるが、重要語として入る(価値の高い順位は`pumps its fist`/`push prices up`より下のはずだが、P1ではM2でも`pumps its fist`が0/3)。

### 5-4. 最終5件の全文
全条件xrunの最終5件(層1: gate前の選定生出力のdisplay_phrase、`I`=important、`T`=topic、`<>`は候補表層、backup。Stage2以降はbackup記録あり、Stage1は未記録)は`analysis_r1.md`(全36グループ)。代表を以下に抜粋(Coffee、基準M0P0・機械のみM2P0・統合M2P3・M2P2)。
**coffee_std_M0P0**
- run1: I:pump one's fist<pumps> / T:raw-bean / I:push prices up<prices up> / I:right away / I:on a regular basis | backup=None score=33 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
- run2: T:raw-bean / I:right away / I:take time / I:push prices up<prices up> / I:based on | backup=None score=18 | canon=CANONICALIZATION_INVALID red=None
- run3: T:raw bean<raw-bean> / I:pump one's fist<pumps> / I:right away / I:push prices up<prices up> / I:take time | backup=None score=30 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
**coffee_std_M2P0**
- run1: T:raw bean<raw-bean> / I:pump one's fist<pumps its fist> / I:push prices up<prices up> / I:right away / I:on a regular basis | backup=None score=33 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
- run2: I:pump its fist<pumps its fist> / T:raw-bean / I:push prices up<prices up> / I:on a regular basis / I:take time | backup=None score=32 | canon=CANONICALIZATION_INVALID red=None
- run3: I:pump one's fist<pumps its fist> / T:raw bean<raw-bean> / I:roasting / I:right away / I:push prices up<prices up> | backup=None score=35 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
**coffee_std_M2P3**
- run1: T:raw bean<raw-bean> / I:push prices up<prices up> / I:pump one's fist<pumps its fist> / I:be based on<based on> / I:on a regular basis | backup=take time<take time> score=31 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
- run2: T:raw bean<raw-bean> / I:pump one's fist<pumps its fist> / I:push prices up<prices up> / I:on a regular basis / I:price tag | backup=based on<based on> score=31 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
- run3: T:raw bean<raw-bean> / I:push prices up<prices up> / I:roast / I:based on / I:on a regular basis | backup=price tag<price tag> score=25 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
**coffee_std_M2P2**
- run1: I:push prices up<prices up> / I:on a regular basis / I:feel like<feels like> / I:take time / T:raw bean<raw-bean> | backup=None score=20 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
- run2: I:push prices up<prices up> / I:pump one's fist<pumps its fist> / I:on a regular basis / I:take time / T:raw bean<raw-bean> | backup=None score=32 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
- run3: I:pump one's fist<pumps its fist> / I:push prices up<prices up> / T:raw bean<raw-bean> / I:roast<Roasting> / I:on a regular basis | backup=None score=37 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
**coffee_adv_M0P0**
- run1: T:lag / I:show up / I:come down / I:raw beans / I:hold on | backup=None score=23 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
- run2: T:lag / I:show up / I:come down / I:raw beans / I:right away | backup=None score=22 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
- run3: T:lag / I:show up / I:come down / I:price tag / I:come with<comes with> | backup=None score=15 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
**coffee_adv_M2P0**
- run1: T:time lag / I:show up / I:come down / I:price tag / I:pump one's fist<pumps its fist> | backup=None score=36 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
- run2: T:time lag / I:show up / I:come down / I:pump one's fist<pumps its fist> / I:hold on | backup=None score=39 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
- run3: T:time lag / I:come down / I:show up / I:pump one's fist<pumps its fist> / I:hold on | backup=None score=39 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
**coffee_adv_M2P3**
- run1: T:time lag / I:show up in<show up> / I:come down / I:hold on / I:come with<comes with> | backup=right away<right away> score=27 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
- run2: T:time lag / I:show up / I:come down / I:come with costs<comes with> / I:pump one's fist<pumps its fist> | backup=roasting<Roasting> score=36 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
- run3: T:time lag / I:show up in<show up> / I:pump one's fist<pumps its fist> / I:come down / I:retail prices | backup=insiders<insiders> score=36 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
**coffee_adv_M2P2**
- run1: T:time lag / I:show up / I:come down / I:come with<comes with> / I:hold on | backup=None score=27 | canon=CANONICALIZATION_PASS red=REDUNDANCY_NG
- run2: I:show up / I:come down / I:hold on / T:time lag / I:come with<comes with> | backup=None score=27 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS
- run3: I:show up / I:come down / T:time lag / I:come with<comes with> / I:hold on | backup=None score=27 | canon=CANONICALIZATION_PASS red=REDUNDANCY_PASS

「最終5件全体として学習価値が上がったか」の所見:
- **Adv**: 上がった(M1以降で`time lag`がTopicに入り、M2で`pump one's fist`も入る)。M2P0のrun: T:time lag / show up / come down / pump one's fist / hold on or price tag。score 20→38/47。
- **Std**: M2P0は`pump one's fist`/`push prices up`/`raw bean`(Topic)を3/3で揃え、score 27→33.3/37。ただし`right away`/`on a regular basis`/`take time`がなお1.67枠を占める(基準2.0)。P3だけが低優先枠を1.0まで減らしたが、`pump one's fist`は2/3に落ち(score 29/37)、`based on`/`price tag`が入る。
- **Prompt単独の改善は見られず**、一部(P1/P4)は悪化。Std低優先枠の完全な解消はどの条件でも達成していない。

### 5-5. 安定性(Jaccard、有効run間、n=3)
Coffee: 基準0.55、M2P0 0.68、M2P2/M2P1 0.79、M3P4 0.83、M0P1 0.33(有効1-3)、M0P4 0.39(有効1-3)。Prompt単独では安定性は改善せず、供給が揃ったM2下で高くなる傾向。アンカー簡易スコアが高い条件(M2P0 0.68、M2P3 0.59)の安定性は中程度。

### 5-6. 層2: gate(選定能力と分離して集計、Production gate関数)
| P | run数 | 選定INVALID | canonicalization INVALID | REVIEW | Redundancy NG | 全gate PASS |
|---|---|---|---|---|---|---|
| P0 | 26 | 0 | 3 | 0 | 1 | 22 |
| P1 | 12 | 2 | 1 | 0 | 0 | 9 |
| P2 | 12 | 0 | 0 | 0 | 3 | 9 |
| P3 | 20 | 0 | 1 | 0 | 3 | 16 |
| P4 | 18 | 3 | 1 | 1 | 5 | 8 |
(本Roundの88 jobをPの種類別に集計。run数の合計=88。基準C0再利用12 runsは含まない。「全gate PASS」=選定PASS+canonicalization PASS+Redundancy PASS)
- **選定INVALID**はP1(2/12: 日本語グロスに括弧書き)とP4(3/18: normalization_noteが空)に集中、P0/P2/P3は0。Productionは`MAX_PRODUCTION_RETRY_ATTEMPTS=2`で再試行するため、Productionでは再試行対象だが、短縮Promptの契約遵守劣化(費用・時間の増加)を示す。
- **canonicalization INVALID 6件**(88 run中): 全て「表示語がsource_spanを超えて拡張される」サブクラス(`raw-bean prices`、`based on interviews`、`come with costs`、`give back gains`、`crude futures`)。**Rule7予測INVALID 35組(所有格代名詞系)の該当は0件**。`pump`項目は15回出現し、canonicalizationで14回PASS(`pump one's fist`、理由は`inherit_selection_normalization` 12 / `generalize_person_dependent_reference` 2。ただし1件のINVALIDは同一run内の別項目`raw-bean prices`が原因で、pump項目は`pump its fist`のまま確定せず)。活用形戻し+person置換の同時変化によるINVALID(Phase B予測)は、選定LLMが最初から`pump one's fist`/`pump its fist`と基本形で出したため顕在化しなかった(予測の安全の証拠ではない)。新サブクラスの発生率は6/88(6.8%)でOPEN-310への追記候補(報告のみ)。
- **Redundancy NG**: Advで`lag`/`time lag`と`show up`を同時選定すると「同じ遅れ表現」としてNG(9件: `lag`+`show up` 6、`time lag`+`show up` 3)。P2-P4で顕著(M0P4 3/3、M0P3 2/3、M3P4 2/3)。選定能力ではなくQA判定との相互作用。hormuzは基準でもNG(`give back`/`pull back`)で、Promptでは解消しなかった。
- ja_gloss括弧違反はP1のINVALID 2件のみ。

### 5-7. 他記事(meta/hormuz、参考。Stage3 = M2P0 / M2P3、n=2。基準M0P0は前回Phase2 C0 n=3の再利用)
- hormuz: M2P0 StdはRedundancy PASS 2/2(基準は`give back`/`pull back`/`take back`の重複でNG 2/2)、`center stage`はAdvでM2P0 1/2(基準2/3)。M2P3は`give back gains`/`take back a plan`の表示拡張が出る(canonicalizationの拡張INVALIDリスク。今回M2P3ではPASS、M2P0 Advで`give back gains`/`crude futures`が1件INVALID)。`sea blockade`はTopic維持。
- meta: M2P0は`concierge`を概ね維持(Std 1/2・Adv 2/2、基準Std 3/3・Adv 1/3)、`contract workers`/`behind the scenes`/`no way`/`unintentionally`維持。M2P3は`concierge`が0/4(Std/Adv)となり`inappropriate`(形容詞)/`take care of`が入る(前回Phase 2のC2と同傾向)。**metaで悪化の兆候(P3)**。
- 他記事ではM2=M1のため、効果はPromptの差に限られる。n=2のため断定しない。

## 6. 失敗要因の分類とRound 2方針案
| 要因 | 該当 | 根拠 |
|---|---|---|
| **供給不足** | `be behind price increases`(全M未到達)、`pump one's fist`(M0/M1は断片のみ→M2で解決)、`time lag`(M0→M1で解決) | §2、§5-2 |
| 選定順位 | Std `on a regular basis`/`right away`/`take time`の低優先枠(P3以外は改善なし)、P1/P4/P2(Adv)での`pumps its fist`の不採用(候補に存在) | §5-1〜5-3 |
| 正規化 | 表示語のsource_span超え拡張INVALID 6/88(Rule7新サブクラス)。所有格系35組は顕在化せず | §5-6 |
| 不安定 | Jaccard 0.3〜0.8。P1/P4のselection INVALID(契約遵守の劣化)。Redundancy NG(lag+show up) | §5-5、5-6 |
| 契約/Prompt設計 | 「比喩・感情表現を同格」文を落とした書き直しがpumpを不利にした可能性(未検証仮説) | §5-1 |
Round 2方針案(Fable判断を待つ。採用ではなく検証案):
1. **機械側はM2を基本に固定**(予約枠cap3、`match:`注釈は効果未確認のため外す)。雑音候補(選ばれない)の費用は小さい。10記事の¥0評価でM2の精度(ルール候補の目視ラベル)を測り、必要なら雑音抑制(動詞形の語尾制約等)を検討。
2. **`be behind price increases`型の供給**: 現状の機械手段(a/b2/c)では供給不能。(b1)LLM補助抽出をTrial専用の上限参照として1条件追加するか、供給不足のまま許容するかを要判断(Production採用は未承認、USER_DECISION_REQUIRED候補)。
3. **Prompt**: P3を土台に再設計(P5)。①「比喩・感情表現を同格」をProduction逐語に近い形で復活し、定着表現の比喩的・擬人的使用は定着表現として扱う(創作比喩の定義を「筆者独自に作った言い回し」に限定)、②`on a regular basis`型の低優先を落とす手がかり(「基本的でレベル既知」)をレベル文で強調、③normalization_note/グロスの契約遵守を保つ短い再確認文、④P3の入れ替え確認手順は維持。P1/P4は単独不採用(契約遵守劣化・pump喪失)。
4. **Redundancy**: `lag`+`show up`の同時選定がNGになるのはQA側の挙動。選定Promptに「同じ現象を表す表現を同時に選ばない」を足すか、QA判定を変えるかは別判断(Production gate変更は禁止範囲)。まずPromptで測る。
5. 追加の評価: Coffee v5以外の記事(semi/smallbag等)でM2の雑音とP3/P5の挙動を確認(Coffee以外のアンカーは無いため定性評価と層2のみ)。
**Round 2費用見積(案、Fable配分JPY100内)**: Coffee 5条件(M0P0再掲、M2P0、M2P3、M2P5、M2P5+b1上限参照) x Std/Adv x n=3 = 30 job ≒ 29、他記事(meta/hormuz/semi/smallbag) x 2条件(M2P0, M2P5) x Std/Adv x n=2 = 32 job ≒ 30、(b1)抽出 ≒ 2、合計 約61(上限100内、1 job 約0.92〜0.95)。Round 1は80.72で配分100内に19.28の余裕(R3/予備へ繰越可否はFable判断)。

## 7. 副次的な発見・制約・訂正
- 前提訂正(§1): placeholder照合単独ではpumpを回収できない(DB未収録)。回収は(b2)+(c)。
- 計測の制約: Stage1の`backup_item`は記録されていない(gate結果に露出しないため)。Stage2以降はrunnerが選定callの生出力`output_text`を保存(`runs/*/job_result.json`の`usage.selection[*].output_text`)。この差以外にStage間のコード差は無い(Stage2の組合せ拡張を除く)。
- Stage2を6組合せへ拡張(§4、事前登録の変更を実行前に`plan_r1.md`へ記録)。
- 簡易スコアはユーザー提示のCoffeeアンカーのみで、アンカー外の有用表現(`comes with`/`based on`等)や他記事の質は評価しない。`on a regular basis`などはアンカー評価では低優先だが、A2学習者への価値が低いとは限らない(ユーザー基準の範囲)。
- 6指標のProduction優先順位は変更していない。P1-P4・M2/M3・注釈はいずれもTrial専用で`APPROVED_FOR_PRODUCTION`ではない。
- 発見した仕様候補(実装せず報告のみ): ①Rule7のsource_span超え拡張サブクラス(OPEN-310追記候補) ②QAのlag/show up重複判定 ③M1の誤除外語(`inappropriate`等) ④Wiktionary照会のオフライン索引化(前回提案、OPEN-337候補) ⑤(b1)供給のUSER_DECISION_REQUIRED。

## 8. 成果物(`er064_output/kp_integrated_opt_01/round1/`)
`ROUND1_REPORT_01.md`(本書)、`prompts_r1.json`(P0〜P4逐語・token・sha)、`shortlists_r1.json`(+`.sha256.txt`、M0-M3 x 10記事)、`screening_r1.json`、`static_eval_r1.md`、`plan_r1.md`(事前登録+変更記録)、`cost_estimate_r1.json`、`cost_r1.json`(全257 call)、`state_guard_r1.json`、`stage{1,2,3}_summary_r1.json`、`stage3_plan_r1.json`、`prep_stage{1,2,3}_r1.json`、`runs/`(88 job)、`analysis_r1.{json,md}`、`report_tables_r1.md`、`anchors_r1.json`(評価専用)、`baseline_reuse_check_r1.json`、`test_results_r1.txt`。
コード: `er064_kp_int_01_{machine,prompts,run,eval,analyze,screen,stage3_select,report_tables,test_01}.py`(前回Trialコードを流用)。委任ログ: `docs/pm/delegation_log/2026-10-13_FAMILY-X-KP-INTEGRATED-OPTIMIZATION-TRIAL-01_01.md`。
