# FAMILY-Z-ATTRIBUTION-CLIP-SPLIT-IMPROVEMENT-TRIAL-01 委任_02 結論 (Trial、Production無変更、採用判断なし)

日付 2026-10-13。設計 plan_02.md、結果 results_summary_02.md / results_02.json。

## 結果(要因分離)
- 判定: **s+s融合が主因(Melos型の名前で)。`said`固有ではない。**
- Melos(語末s、cmudict未収録): OR PASS 非s動詞群{replied,answered,asked} 35/36 vs s始まり群{said,says,sighed} 10/36 (Fisher p<0.0001、観測単位=過小評価)。said 4/12、says 4/12、sighed 2/12 と **said以外のs始まり動詞でも同様に低い**(said以外 6/24 vs said 4/12、p=0.70=差なし)。非s動詞3語はいずれも11-12/12で動詞間差が小さい。
- 転写の典型: s始まり動詞では `Mello said`/`Mellow says`/`Mellow side`(語末sが脱落または次語へ吸収)、非s動詞では `Melos replied`/`Mellos answered`。
- 委任_01との再現: Melos said OR 4/12(旧2/9)、replied 12/12(旧7/9)、Brontes said/replied 9/9 同士。方向・大きさとも再現(replied は今回の方がやや高い)。
- Brontes(語末s、cmudict未収録): Production判定OR PASSは s群27/27 vs 非s群26/27 で差なし。OpenAI綴り一致のみ s群0/27 vs 非s群20/27(p<0.0001)=音響的融合は存在するが、Production判定(stem同音吸収等)が吸収する(委任_01と同じ名前依存)。
- Phrase Listなし(Production初出名に近い条件、Melos x 全take): Azure単独PASS said 1/12 vs replied 8/12、OR(OpenAI or Azure[PLなし]) 1/12 vs 8/12。Phrase Listあり(Azure 4/12 vs 12/12)より全体に低い=Phrase Listが綴りをかなり誘導している(ledger未登録の初出名ではさらに通りにくい)。
- 減速: Melos s群 OR raw 4/12 -> slow6 3/12、非s群 12/12 -> 12/12。Adv s群 3/12 / 非s群 11/12。Std/Adv間で結論は同じ。

## 限界
- 観測は126、独立音声は84(Std 36音声は減速前後を両方観測)。Fisher p値は過小評価。Melos s群は3動詞x2level x4take=24音声(同一テキスト・同一voiceの繰り返し)。
- OpenAI PASS(Production判定の一次)は非s群でもMelos 7/36と低く、通過は主にAzure+Phrase List(ledger登録名のみ)に依存。Productionでledger未登録の初出名はPLなし条件に近く、非s動詞でも8/12程度(下限側)。
- `sighed` は `side` と聞き違えやすい別要因を含む。`says` は現在形。動詞の語彙・意味の違いは完全には統制されていない(s始まり動詞3語、非s動詞3語のみ)。
- 名前はMelos(吸収されない型)とBrontes(吸収される型)の2名のみ。他の語末s名への一般化はn=2名。
- 自然さ・聴感評価は未実施(決定論チェックと机上のみ)。

## R1/R2 記述の更新
- R2(最小語数ルール): 委任_01で効果未検出のまま変更なし。本armでも2語固定でnss側は通過(Melos 35/36)=短さは主因でない。実装不要候補。
- R1(原稿側ルール): 「attribution動詞の選択」ではなく**「語末が歯擦音の固有名詞の直後に、歯擦音始まりの語(said/says/sighed等)を置かない」**へ修正(動詞固有ではなく音の連続が原因)。適用はWriter promptへの指針+決定論WARN lint(委任_01のdesk_apply参照)。非s動詞(replied/answered/asked)で語順を保てる。ただしBrontes型の名前ではPass率が変わらないため、効果が出るのはMelos型の名前のみ。

## Status
**USER_DECISION_REQUIRED**(維持)。事前登録した問い(長さ vs s+s vs 動詞)は分離完了=s+s融合が主因。ただしVALIDATED(R1がMelos以外の名前でも通過率を改善)の条件は満たさず、Production採用は人間ユーザー判断。REJECTEDでもない(Melosで大きく再現)。
