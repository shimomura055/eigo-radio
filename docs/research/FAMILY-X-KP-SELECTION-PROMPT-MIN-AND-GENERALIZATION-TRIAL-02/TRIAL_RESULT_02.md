# TRIAL_RESULT_02: Key Phrase 最小化Prompt 5モデル比較(Trial①) + 一般化工程分離(Trial②)

2026-10-22 / FAMILY-X-KP-SELECTION-PROMPT-MIN-AND-GENERALIZATION-TRIAL-02 委任_01 / Production無変更・Production採用は未承認(Trial専用)
Excel: `docs/research/FAMILY-X-KP-SELECTION-PROMPT-MIN-AND-GENERALIZATION-TRIAL-02/KP_PROMPT_MIN_GEN_COMPARISON_02.xlsx`(6シート)。証跡: `er101_output/kp_prompt_min_gen_trial_02/`(runs/ gen/ eval/ validation.json summary.json t2_mechanical.json paid_calls.jsonl)。設計・対応表: `TRIAL_DESIGN_02.md`。

## 1. Trial①: 新Promptで学習ポイントの最小化は改善したか
結論(事実): **語数は全5モデルで短縮した**(平均語数、前回KP6M同モデル→今回): Luna 3.61→3.14 / Gemini3.1 FL 4.06→3.23 / Gemini3.5 FL 3.57→2.88 / Haiku5.5 4.04→3.19 / Sonnet5.5 3.89→2.87。5語の候補比率も減少(例: Sonnet 16/70→4/70、Haiku 21/69→7/70)。**3観点(V/E/N、前回と同文言)の評価は概ね横ばい**(下表)で、学習価値が大きく落ちた兆候はない。ただしLunaはV(学習価値)が主評価で1.26→1.06、V/E/N平均0.671→0.629と低下しており、短縮による学習価値の低下の可能性を示す(別バッチ評価の参考値)。
- 前回の『長すぎる』例の追跡(`summary.json` `example_tracking`):
  - `think up what happens next`(前回Luna/Gemini3.1/Sonnet、C_Standard): 今回Luna=`think up`(2語)、Sonnet=`think up`(2語)。Gemini3.1は別の選定(`keep those ideas only`等)で該当なし。**期待どおり短縮**。
  - `formal agreements with their creators`(前回Luna、C_Advanced): 今回Luna=`through formal agreements`(3語、本文一致)。前置詞`through`が残るが5語→3語。
  - `alone caused the different results`(前回Luna、D_Standard): 今回Luna=`alone caused the different results`(5語・**変化なし**)。例示の期待形`caused different results`は本文に連続しない(`the`を除くと不連続)ため、本文一致必須のTrial①では出せない。Trial②でも`alone caused different results`(`the`削除のみ、原形化なし=`caused`残り)で、期待形に達していない。
- 注意: 新旧の最小化観点(C/U/S/X)は新設のため、**旧出力を同基準で採点していない**(予算内で旧セットの再評価をしない設計。TRIAL_DESIGN_02.md 1節)。したがって『最小化の質が旧より何点上がった』とは言えず、改善の客観証拠は語数分布・例示追跡・今回の絶対スコア(下表C/U/S/X)である。

## 2. Trial①: モデル別の品質・指示遵守率・記事セット単価
(分母=候補数。厳格合格=5語以内+本文厳密一致[大小文字・引用符・末尾句読点のみ正規化]+重複なし。記事セット=Standard+Advanced=2本文)

| モデル | 候補数 | 厳格合格率 | 活用形差NG | 言い換え/創作NG | Prompt逸脱(placeholder) | 5件未満セット | 全件合格セット | 選定費用/記事セット(JPY) |
|---|---|---|---|---|---|---|---|---|
| 1 gpt-6-luna | 70 | 69/70=98.6% | 1 | 0 | 0 | 0 | 13/14 | 0.258 |
| 2 gemini-3.1-flash-lite | 70 | 62/70=88.6% | 3 | 4 | 1 | 0 | 7/14 | 0.227 |
| 3 gemini-3.5-flash-lite | 69 | 67/69=97.1% | 2 | 0 | 0 | 1(正当な4件) | 13/14 | 0.336 |
| 4 claude-haiku-5-5 | 70 | 70/70=100% | 0 | 0 | 0 | 0 | 14/14 | 0.335 |
| 5 claude-sonnet-5-5 | 70 | 70/70=100% | 0 | 0 | 0 | 0 | 14/14 | 5.102 |

5語以内は全70/70/69/70/70で全候補遵守(5語超0)。自己申告語数との不一致(別記録): Luna 1 / Gemini3.1 2 / Gemini3.5 3 / Haiku 0 / Sonnet 1(ハイフン複合語の数え方等)。

| モデル | 平均語数 今回(前回) | V/E/N平均(0-1) 今回(前回・同定義別バッチ・参考) | 最小化4観点平均(C/U/S/X、0-1、今回のみ) | 主C | 主U | 主S | 主X | 主評価者 | padding率(主) |
|---|---|---|---|---|---|---|---|---|---|
| Luna | 3.14(3.61) | 0.629(0.671) | 0.766(参考=同系統Sol 0.786) | 1.43 | 1.46 | 1.40 | 1.84 | Sonnet | 64% |
| Gemini3.1 FL | 3.23(4.06) | 0.650(0.645) | 0.771 | 1.58 | 1.49 | 1.40 | 1.70 | Sol+Sonnet平均 | 71% |
| Gemini3.5 FL | 2.88(3.57) | 0.685(0.682) | 0.822 | 1.68 | 1.57 | 1.50 | 1.83 | Sol+Sonnet平均 | 71% |
| Haiku5.5 | 3.19(4.04) | 0.669(0.688) | 0.843(参考=同系統Sonnet 0.896) | 1.81 | 1.51 | 1.50 | 1.91 | Sol | 86% |
| Sonnet5.5 | 2.87(3.89) | 0.717(0.712) | 0.895(参考=同系統Sonnet 0.907) | 1.90 | 1.70 | 1.66 | 1.90 | Sol | 64% |

- 比較の注意(評価方法の変更点): (1)旧rubricのG(一般化の適切さ)は新Promptに一般化条項がないため除外。(2)C/U/S/Xは今回新設で前回スコアと合算しない。(3)V/E/N平均は前回summary.jsonの主V/E/Nから同定義で再計算した参考値で、前回と同一バッチではない(評価対象セットの構成が5セットvs7セット)。(4)主評価者は選定元と異系統のため、Luna=Sonnetのみ、Haiku/Sonnet=Solのみ、Gemini=2者平均で、モデル間の絶対値は評価者差の影響を受ける(参考の同系統値は順位がほぼ同じ)。(5)padding率が高いのは評価者が『5件を埋めるために価値の低い候補が含まれる』と判断する割合で、前回既存Productionは93%。
- 厳格不合格の内訳: Luna=`passed the baton`(活用形差) / Gemini3.1=`has an unseen clock`,`one contest altogether`,`stretch … too far`,`gave back their gains`(NG_NO_MATCH、うち後者は草稿訂正後の最終形), `look into`,`boredom became fuel for`,`look closely at`(活用形差), `take something too far`(placeholder逸脱) / Gemini3.5=`boredom became fuel`,`see others suffer`(活用形差)。
- 出力の乱れ(Prompt非遵守の観測): Gemini3.1(3セット)・Gemini3.5(3セット)で、6語以上の草稿や取り消しを出力本文に含む(「6語以上は出力禁止」への逸脱)。Luna/Haiku/Sonnetは0。

## 3. Trial②: Luna + 一般化工程でどの程度改善したか
Before=Trial①のLuna出力14本文70件そのまま(再選定なし)。一般化=`claude-haiku-5-5`(返却ID一致、14呼出)。Before一致・件数・番号の機械検証=70/70一致、再選定0、5語以内70/70。
- **変更されたのは70件中16件(23%)**。変更内容: 原形化2(rolled back→roll back, brushed aside→brush aside)、固有対象の除去/置換9(US削除, that→something, the story→something, a story→something, this→something, its削除2, you→someone, the削除1)、過剰変更・疑義5(pumps their fist, raw materials, concierge service, hand the baton to someone, country-led。下記4・5節)。
- 評価者2系統(Sol/Sonnet)の判定: 一般化の適切さ 両者PASS 44/70(63%)、学習ポイント維持 両者PASS 68/70、自然さ 両者PASS 69/70。『3項目全PASS+5語以内』=44/70(63%)。
- **最大の課題=適用漏れ**: 『要変更』と2者一致で判定されたのが29件、うち未変更のまま残ったのが15件(適用漏れを2者が指摘22件[いずれか]/17件[両者])。ほとんどが**過去形・三単現・-ing形の原形化漏れ**(`pushed prices up`,`comes with costs`,`passed the baton`,`pulled back`,`gave back`,`took a sharp turn`,`goes beyond the evidence`,`refuses to stay down`,`thinking up`等)。Haikuは自分で『過去形を維持』と理由を書いて残す例もある(G_Advanced `gave back`)。
- ユーザー例示のうちTrial②の対象とした`agreements→agreement`は未変更(`through formal agreements`は2者とも『変更不要』と判定=複数形のままで可という評価)、`caused→cause`は未達(`alone caused different results`、`caused`が残り2者が適用漏れと指摘)。
- 意味変化: いずれか3件/両者2件。過剰変更: いずれか4件/両者3件。追加語(機械): 4件(`materials`,`service`,`to`,`country-led`)。

## 4. 代表的なBefore/After
| 区分 | Before(Luna) | After(Haiku) | 評価 |
|---|---|---|---|
| 良い(削除) | appear in US shop prices | appear in shop prices | 2者PASS(US除去) |
| 良い(置換) | dismiss this by saying | dismiss something by saying | 2者PASS |
| 良い(原形化) | rolled back / brushed aside | roll back / brush aside | 2者PASS |
| 良い(置換) | none other than you | none other than someone | 2者PASS |
| 漏れ | pushed prices up / passed the baton / took a sharp turn | 変更なし | 2者とも原形化漏れ |
| 漏れ | alone caused the different results | alone caused different results | theは除去したがcausedが残る(2者が漏れ指摘) |
| 過剰/意味変化 | keep raw beans in stock | keep raw materials in stock | 2者NG(beans→materialsで具体性・意味が変わる) |
| 過剰/意味変化 | human concierge feature | human concierge service | 2者NG(不要な語の置換) |
| 過剰(追加語) | hands the baton | hand the baton to someone | 2者NG(`to someone`追加) |
| 疑義 | pumps its fist | pumps their fist | Sol:原形化漏れ、Sonnet:意味変化・過剰(its→their) |

## 5. 一般化の失敗・過剰変更・適用漏れ(件数は2評価者の判定)
適用漏れ いずれか22/70・両者17/70 / 過剰変更 いずれか4・両者3 / 意味変化 いずれか3・両者2 / 不自然 いずれか1(Sonnet: 1件、両者0) / 追加語(機械)4。詳細行=Excel「T2 一般化Before-After」「T2 検証詳細」。失敗は主に『原形化の適用漏れ』と『beans→materials等の語の置換(someone/something以外の追加語)』の2系統。

## 6. 既存Productionとの品質・費用比較(事実。方式差の注記: 今回=記事全文渡し、既存=DB hybrid shortlist+canonicalization。直接の優劣比較ではない)
- 品質: 既存Production(前回KP6M測定)は同一本文14で厳格合格47/70(活用形差21含む、厳密規則では不利な方式差)、V/E/N平均0.550(前回評価)。今回Luna新Prompt: 厳格合格69/70、V/E/N平均0.629(別バッチ参考値)。2工程方式(Luna+Haiku一般化)は『一般化の適切さ』両者PASS 63%、原形化漏れが多く、現状のHaiku+初期Promptでは一般化工程の品質は十分とは言えない。
- 費用(実測、1記事セット=Std+Adv): 今回Luna新Prompt選定 0.258円 + Haiku一般化 0.183円 = **0.441円**。既存Production KP選定(selector+canonicalization実測)=1.828円。評価費用は運用に含まれない(Trial費用)。為替=USD/JPY 160(プロジェクト既定、実為替ではない)。

## 7. Fable独立評価とTrial終了Status
### 7. Fable独立評価・Trial終了Status(2026-10-22)
- 分類: **Trial①=`VALIDATED`**(最小化Promptの有効性は確認。Production採用ではない)。**Trial②=`REJECTED`(今回構成=Claude Haiku 5.5+初期一般化Prompt)**。2工程方式という考え方自体は閉じない(下記C)。
- Trial①の根拠: 5モデルすべてで平均語数が短縮(Luna 3.61→3.14、Sonnet 3.89→2.87等)し、5語超0件・本文一致も維持(Luna 69/70、Haiku/Sonnet 70/70)。例示3件のうち`think up what happens next→think up`はLuna/Sonnetで達成、`formal agreements with their creators→through formal agreements`(Luna)は改善方向、`alone caused the different results`は期待形が本文に連続して存在しないため本文一致必須の条件下では原理的に不可能(Trial②/原形化の領域)。留意: Lunaの学習価値V(前回と同観点)は1.26→1.06へ低下しており、短縮と引き換えに価値がやや下がった可能性がある(評価者のぶれ[前回実測 平均絶対差0.11]の範囲内で断定不可)。
- Trial②の根拠: 変更16/70に対し原形化の適用漏れが17〜22/70(両評価者一致17)、過剰変更4、意味変化3、許容外の語の追加4(`materials`/`service`/`to`/`country-led`)。一般化の適切さ両者PASSは44/70(63%)。「変更すべきものを変え、不要なものを維持する」という要件を満たしていない。なお**原形化(canonicalization)は既存Production(DB hybrid方式)に既に工程として存在し**、今回の漏れの大半は既存工程が担っている種類の処理である。従って「新たに一般化LLMを1工程追加する」より、「最小化条件を既存のProduction経路(shortlist→選定→canonicalization)に入れて検証する」方が、既存仕様との整合・費用・リスクの面で合理的。
- 既存Productionとの比較の読み方: 今回Luna(厳格合格69/70、V/E/N 0.629、0.258円+一般化0.183円)と既存(47/70、0.550、1.828円)は方式が異なる(全文渡し vs DB hybrid+canonicalization)。既存の厳格合格の低さの大半は意図した原形化によるもの。費用差は方式差(shortlist・canonicalizationの呼出)を含む。
- Fable推奨(ユーザー判断A/B/Cは別件として整理):
  - **A(選定モデル変更)=現行gpt-6-luna維持を推奨。** Sonnet 5.5は最良だが費用約20倍。Claude Haiku 5.5は2回のTrialで一貫してLuna以上(遵守100%、最小化0.843 vs 0.766、価値0.669 vs 0.629)で費用もほぼ同等(0.335 vs 0.258円/セット)だが、差は評価者のぶれの範囲内で、かつProductionにAnthropic APIという新しいProvider依存を追加する実装・運用コストが発生する。品質差が実証されるまで切替は不要。
  - **B(選定・一般化の2工程方式の正式採用)=今回構成では不採用を推奨。** 適用漏れ・過剰変更が多く、原形化は既存工程で担える。
  - **C(次の一手)=「最小化条件(新Prompt第3条)を現行Production経路のPromptに組み込み、同一14本文・Lunaで現行方式と比較する小規模Trial」を推奨(見積は事前に算出、前回規模より小さい見込み)。** 採用判断はその結果で行う(Prompt変更はユーザー承認事項)。
- Closeout: Production/Prompt/Validator/モデル構成は無変更。再現情報=TRIAL_DESIGN_02.md+`er101_*`+paid_calls.jsonl。Opus条件Cレビューは採用提案時に実施。

## 8. 追加報告
### 8-1. 次に必要なユーザー判断(判断候補。事実材料のみ、推奨はFable)
- 判断A『選定モデルを変更すべきか』(判断候補、区分D=真に新しい判断): 材料=最小化Promptでの厳格合格率はHaiku/Sonnet 100%、Luna 98.6%、Gemini3.5 97.1%、Gemini3.1 88.6%。Sonnetは最小化・学習価値の主評価が最良だが選定費が約20倍(5.10円/セット vs Luna 0.26円)。Lunaの新Promptでの学習価値V低下(1.26→1.06)はある。OPEN-445の判断(#145、現行Luna維持推奨)は未回答。
- 判断B『選定・一般化の2工程方式を正式採用すべきか』(判断候補、区分D): 材料=現状のHaiku+初期Promptは適用漏れ22/70で品質不足の兆候。改善余地=原形化を明示する一般化Prompt、より上位の一般化モデル、またはルールベースの原形化(0円)の併用。いずれも新仕様/新Trial範囲になるため本委任では未実施。
### 8-2. Prompt調整の事後報告
- Trial①: 変更前=Prompt本文のみ、変更後=Prompt本文は1字も変更せず末尾に『\n\n---\n\n【記事本文】\n』+本文を後置(KP6Mと同一)。理由=本文受け渡し位置。影響なし(prompt_sha256 6a5d2052...が全70run同一)。
- Trial②: 変更前=一般化Prompt本文のみ、変更後=本文の後に『\n\n---\n\n【Key Phrase一覧】』+番号付きKey Phrase(各項目に『本文中の該当文(参考情報)』を全70件同一形式で付与)+『【出力形式(受け渡し用の指定)】JSON配列のみ、{no,before,after,reason}、入力と同順・同件数』。理由=パースと対応追跡、固有名詞・this/its等の依存判断材料。一般化Promptの条件は不変(sha256 43635944...)。文脈文を付けたことで一般化の判断が変わりうる(付けない条件との比較はしていない)。
### 8-3. 抽出(パース)の手動補正(モデル出力は無改変・記録のみ補正)
n2/A_Standard 3番目=草稿7語→『修正→in the ring』を採用 / n2/G_Advanced 3番目=草稿6語→『gave back their gains』 / n3/D_Standard=番号重複の取消項を除く5件の確定リスト / n4/A_Advanced=表(本文該当箇所付き)を選定結果としてグループ0を採用。以上4件。他は自動抽出(前回と同じパーサ)。
### 8-4. 技術的失敗
選定: n5(Sonnet)/G_Advancedで1回ConnectTimeout→同一入力で再試行1回成功(再試行1/70)。他0。一般化・評価の失敗0、JSONパース失敗0。
### 8-5. 費用実測(出典: APIが返したusage x 単価。為替160)
選定 43.806円(Luna 1.805 / Gemini3.1 1.590 / Gemini3.5 2.354 / Haiku 2.343 / Sonnet 35.715)、一般化 1.283円(Haiku 14呼出)、独立評価 143.188円(T1: Sol 45.821+Sonnet 57.544、T2: Sol 15.212+Sonnet 24.611)。**Trial合計 188.278円**(台帳`paid_calls.jsonl`と一致、Cap300円の63%)。当日(JST 2026-10-22)日次累計=既使用約482円+本Trial 188.3円=約670円(Stage 2 Trial Guardrail分は別途)。
### 8-6. 分類候補(最終分類はFable)
- Trial①: `VALIDATED`(比較Trial有効。5モデル70/70選定成功、本文sha一致、返却ID一致、語数短縮は全モデルで確認、モデル別の遵守率差あり)。
- Trial②: 一般化工程は技術的に成立(対応追跡70/70)したが、品質は初期Prompt+Haikuで未達(適用漏れ主体)。『2工程方式の採否』は`USER_DECISION_REQUIRED`候補(区分D)、または改良Trial後に再判断。Production採用の推奨はFable。
### 8-7. 再現(実行コマンド)
```
.venv\Scripts\python.exe tools/stop_scope_check_01.py --managed-id FAMILY-X-KP-SELECTION-PROMPT-MIN-AND-GENERALIZATION-TRIAL-02 --run-dir er101_output/kp_prompt_min_gen_trial_02 --out docs/pm/delegation_log/2026-10-22_KPMG1_stop_check.json   (rc=0 x3)
.venv\Scripts\python.exe er101_kp_prompt_min_gen_trial_02_run.py --out er101_output/kp_prompt_min_gen_trial_02 --manifest er098_output/kp_six_model_trial_01/inputs/manifest.json --cap-jpy 300
.venv\Scripts\python.exe er101_kp_prompt_min_gen_trial_02_validate.py
.venv\Scripts\python.exe er101_kp_prompt_min_gen_trial_02_gen.py
.venv\Scripts\python.exe er101_kp_prompt_min_gen_trial_02_eval.py --phase both --cap-jpy 300
.venv\Scripts\python.exe er101_kp_prompt_min_gen_trial_02_excel.py
```
