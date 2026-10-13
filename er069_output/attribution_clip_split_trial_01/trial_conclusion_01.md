# FAMILY-Z-ATTRIBUTION-CLIP-SPLIT-IMPROVEMENT-TRIAL-01 委任_01 結論 (Trial、Production無変更、採用判断なし)

Status: **USER_DECISION_REQUIRED**(VALIDATEDにしない理由は下記)。日付 2026-10-13。

## 1. 何を検証したか
- R1(原稿側・音声的条件): 固有名詞の語末が歯擦音のとき、直後に歯擦音始まりの語(said等)を置かない(別の発話動詞/代名詞へ)。
- R2(分割側): 引用に隣接するnarrator chunkの最小語数(固有名詞を含むtagは>=4語、それ以外>=3語を試作しきい値とする決定論lint、WARNのみ)。
- 交絡分離: 境界{ss=`NAME said`/nss=`NAME replied`} x 長さ{2/4/7語} x 名前{Melos, Brontes, Pelias=cmudict未収録 / Kallis=収録の対照} x level{Std[PD8+A2_SLOWER、減速前/6%減速後], Adv[PD8]} x 3take = 144 TTS call、216観測(OpenAI/Azure+PhraseList/faster-whisper-small)。

## 2. 結果(詳細表は results_summary_01.md / per_name_analysis_01.txt)
- 長さ効果(R2): **検出できず**。OOV 3名pooled、Production判定PASS(OR) L7 45/54 vs L2 45/54、OpenAI判定 19/54 vs 20/54、綴り一致(OpenAI) 14/54 vs 10/54 (p=0.49)。Melosでは L4(16/18) > L7(11/18) ≒ L2(9/18) と非単調=長さでは説明できない。
- s+s回避効果(R1): **名前依存**。
  - Melos: OR PASS 25/27 vs 11/27 (p=0.0001)、OpenAI判定 12/27 vs 3/27 (p=0.014)、Azure綴り 25/27 vs 7/27。長clip(L7)でも ss 2/9 vs nss 9/9(長くしてもs+sは救われない)。
  - Brontes/Pelias(Melosと違いPattern A[s脱落]や語尾Phrase Listで元から通る): Production判定PASSは改善なし(OR 52/54 vs 54/54、OpenAI 20/54 vs 25/54)。ただしOpenAI綴り一致(名前がそのまま書かれる率)は 17/54 vs 6/54 (p=0.0175)、whisper 19/54 vs 5/54 (p=0.002)でnss優位 = 音響的なs+s融合は名前によらず存在するが、Productionの判定がそれを吸収できる名前では通過率に出ない。
  - CMU収録の対照名Kallis: OpenAIは常に別綴り(Callis等)で綴り一致を測れず、Azure PASSは ss 24/27 vs nss 25/27 で差なし。
- 交互作用: 2x2(OOV pooled)の差の差=0.00(OR PASS)。長さ効果はs+sの有無によらずゼロ。
- Std減速: 減速前→後でOR 48/54→46/54、OpenAI 20/54→18/54 (わずかな低下、有意差なし)。Adv(減速なし) OR 48/54、OpenAI 22/54。Std/Adv間で結論は同じ。
- clip長: L2平均1.79秒 / L4 2.11秒 / L7 3.71秒。

## 3. 制約・交絡(断定しない点)
- 216観測は144音声。Std 72音声は減速前(raw)と減速後(slow6)の同一音声を両方観測しているため、観測は独立ではない。上記p値(Fisher、観測単位)は過小評価(実効標本は144音声以下)。傾向の目安としてのみ扱う。
- nss条件は動詞が`replied`(語頭r)で、`said`とは語自体が違う。「s+s融合」と「動詞の違い」は分離できていない(動詞ごとの効果は未検証。例: s始まりでない同義動詞`asked`/`answered`の追加比較、s+sを保つ別動詞`says`等が必要)。
- 名前はn=3 OOV+1対照。各名前x各セルは3take(pooledセルn=9で4以上を満たすが、名前別は3)。Melosは実は唯一の「Production判定が吸収できない」名前であり、一般化にはstem同音で吸収されない別の名前(例: 語幹が実在語と近い名)のサンプル追加が必要。
- Azure判定はPhrase List=[NAME]を付与した条件(Productionではledger登録名のみ)。BrontesとPelias(Azure 54/54)は「Phrase Listが綴りを誘導した」可能性を除外できない(決定的=忠実ではない)。
- post-slowdown cascade rescue(Tier3等)は副作用のため呼んでおらず、Production実運用では本結果より通りやすい可能性がある。
- 自然さは決定論チェック(語数・文数・平均文長・発話動詞の分布)と人間による読みのみ。LLM QA、聴感評価は未実施。

## 4. 机上適用(Melos原稿、before/after)は desk_apply_01.md
- Std a2 part1_c5 「Melos said.」(2語, ss) → 「Melos answered, looking straight at the ruler.」(7語, nss)。語数 408→413。clip数23のまま、lint指摘 1→0、固有名詞s+s境界(短clip内)1→0。
- Adv b1b part1_c5 同上 → 「Melos replied, holding the ruler’s gaze.」(6語)、part3_c5 「he whispered.」(2語) → 「he whispered, his voice breaking.」(5語)。clip数25のまま、lint指摘 2→0。
- いずれも保存済みclip計画を再現できた(regression True)後のafter。平均文長 8.87→8.98 / 6.79→6.91、発話動詞の分布は多様なまま。
- Melos part2_c1 (124語 clipの内部`Melos struck`)は長clip内のため対象外(Productionで既に通過)。

## 5. Status判定と根拠
- VALIDATED条件(R1またはR2がMelos以外の名前でも通過率を改善)を満たさない: R2は効果なし、R1はMelosでのみProduction判定通過率が改善、Brontes/Pelias/Kallisでは通過率に差が出なかった(ただし綴り一致率ではR1の効果が複数名で確認)。
- REJECTEDにもしない: R1はMelos(本件の実問題)で有意かつ大きい効果、他名でも音響的効果の痕跡があり、変更は小規模(Writer promptへの指針追加+決定論WARN lint)。
- → **USER_DECISION_REQUIRED**。仕様選択肢(推奨はRESULT_PACKET_SPLIT.mdの(8)参照)。

## 6. 次の一手(提案のみ、未実装)
1. R1の動詞選択を見る追加Trialで`replied`以外(`asked`/`answered`、あるいは`said`のまま名前を`he`等へ)と`says`を入れ、動詞効果とs+s効果を分離する(小規模、推定JPY10-20)。
2. 別の名前タイプ(語幹が実在語に近い語末s名)でR1の通過率効果を再確認する。
