# OPEN333_E4_PREREGISTERED_01(E4=便乗PASS是正・E4-N=E3副作用の整合化の事前登録。JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_13、2026-10-26)
評価script実行より前に固定。基準は結果を見て緩和しない(厳格化のみ可。変更時は末尾に改訂記録を追記)。OPEN333_PREREGISTERED_01/02.mdは変更しない。

## 0. 凍結物と比較基準
- 比較基準(HEAD) = **E3適用済みのProduction**(`er011_ja_asr_variant_layer_01.py` の `CANDIDATE_E_FULL_DIFF_CHECK=True`/`CANDIDATE_E_VALUE_GUARD_CHECK=True` のまま。委任_12のようにFalse固定にしない)。評価開始時のgit HEAD=`81e70d4f0`(E3適用commit `7953f5969`を含む)。
- proto_05 `proto_open333_fix_05.py`(E3v3+E4、凍結) sha256 `af9f8b60a092a781ab0d9115e16ea3a2e8e9da3444c2352d4138301b856925b8`(arm `F05_E4`=mode E3V_E4)。proto_04 sha256 `34047670d79935ec63854f2d25d173a890d8001bd88398e76f5569685e668dc8`(E3v3、凍結)。
- proto_06 `proto_open333_fix_06.py`(E3v3+E4+E4-N) sha256 `e05123e4f974b83577c20fe0318c12f66f0e597c91444b7c719209ce00a0caea`(arm `F06_E4`/`F06_E4N`/`F06_E4_E4N`)。proto_06はHEADの上に重ねる(HEADのE3拒否はそのまま、E4/E4-Nだけを追加)。
- 評価script `eval_open333_api0_06.py` sha256 `dc7db65c972bca12bf32ba1d7b50067145599815c3d18d3bd7036d9a4123ad02`。
- 追加負例・対照 `sweep_cases_open333_e4_02.py` sha256 `54a36cd7b454cdb9580dcd4fe1b1d345fb08924aed274b23fb20d57ad278a5c6`(ひらがな濁点差の負例[前回未検証]、乗り物なし数値entry、E4-Nが拒否のままであるべき混在型)。既存 `sweep_cases_open333_e4_01.py`(sha `1b4ea6df48e111cb41c19fbb9875280a03f75073bd20c08f2e5c99783e1b8096`、凍結)と `sweep_cases_open333_02.py`(M-3 40件、凍結)も使用。
- 母集団: 実データ+合成負例1,327行 / M-3 sweep 40 / 旧v2 sweep 29 / E4行(既存170+追加) / Secondary対(保存+全Primary転写)。

## 1. 各案の定義(PASS集合は広がらない。拒否または即PASS→Cascadeへの振替のみ)
- E4: Candidate Eが救済(PASS)する直前、`protected.content_diffs` に `cascade_eligible` 差分(entity_like=両側カタカナ/略語のreplace、phonetic_uncertain=濁点/半濁点のみ差のreplace)が1つでも残れば、PASSにせず既存の `_cascade`(= `ASR_VALIDATION_UNCERTAIN`、B/C/D-1と同じ返し方)を返す。
- E4-N: 数値entryでE3が『説明できない非数値差』を理由にEを拒否(`return None`→TRUE_CONTENT_MISMATCH)するとき、説明できない差が**全て** cascade_eligible(protected_check_jaと同じ述語)で、かつ値ガードがEQUAL/NO_VALUES/AMBIGUOUS なら、拒否ではなく `_cascade` を返す。1件でも非cascade差・値ガードDIFF/UNKNOWN・helper例外があれば従来どおり拒否。
- 新しい受理クラス・新しい分岐先は作らない。Cascade後の判定(統一judge P1/P2/P3、Secondary許容集合=EXACT/NORMALIZED、ORTHOGRAPHIC_VARIANT_CONFIRMED)は既存のまま。

## 2. 用語と指標
- Cascade行き = 統一judgeのP3到達(判定audit `p3_entry` が非null)。API 0ではAzureがstubのため最終stateは `NG_SECONDARY_UNAVAILABLE` になる。保存Secondary転写がある行は、その転写をAzure応答として注入した最終判定も併記する(注入=評価用stub、ネットワーク呼出なし)。
- 遷移種別(HEADとの比較、全件): 不変 / PASS→Cascade / 拒否→Cascade(HEADが即NG[Cascadeを経ない]だったもの) / 同種内変化(ラベル・reasonの表記変化のみ) / 違反(非PASS→PASS、PASS→即NG、Cascade→即NG)。
- 費用: Cascade 1回 0.2667円(`OPEN333_EVAL_02.md`と同じ)。

## 3. 合格基準(E4、E4+E4-N それぞれ。E4N単独armは参考)
- K1 単調: 非PASS→PASSが全母集団・全armで0件。
- K2 方向: 『PASS→即NG』『Cascade→即NG』(違反)も0件(E4/E4-Nは Cascadeへ戻す変更のみで、新たな即NGを作らない)。
- K3 固有名詞負例: 合成負例(neg 110 + ひらがな濁点差 neg_hira)の**PASSが0**(HEADの便乗PASS数は開示。前回 96/110)。実データの負例系(N1/N3/SYN)のPASS数はHEADから増えない。到達しなかった(Eに入らない)行は『未到達』として件数開示し、合格の分母に含めない。
- K4 実データ(1,327行): HEADから変わる行を**全件**列挙し、(a)本物の読み違い疑い/(b)正常音声のCascade送り に区別。負例以外のHEAD PASSのうち PASS→Cascade になる割合 ≤ 1.0%(前回E4=0.59%)。超えたら全件目視し正常音声の過大なCascade送りなら不合格。
- K5 ctrl・範囲外: ctrl(名は同一・乗り物のみ)は変化0。out_of_scope(乗り物なし数値entryのcascade差=Eに到達しない)はHEADと完全一致。
- K6 E4-N(E4_E4N / E4N arm): (i) 正常な等価表記(cost)の数値entryで、HEADが『即NG』(Cascadeを経ない)になっていた行が、Cascade行きになる(即NGの残りが0)。(ii) `e4n_keep_reject`(cascade差+しわ→すわ型の説明不能差が混在)は**HEADと完全一致**(Cascadeへ振替えない)。(iii) 値ガードDIFFの行は変化0。
- K7 Secondary受理: 保存Secondary対・全Primary転写Secondary対のいずれも、受理(SCG_PASS・orth確認)の変化が0。ラベル変化は全件開示。
- K8 一致: HEAD(E3適用済み)が前回評価のE3V結果と1,327行で不一致0(= protoとProductionの前提一致)。`F05_E4` と `F06_E4` の判定keyが全行で一致。
- K9 保存Secondary転写がある行(Cascade到達の有無を問わず): 転写注入後の最終判定で、非PASS→PASSが0、PASS→非PASS(= HEAD PASSが転写不一致でNGになる)は全件開示。
- K10 決定性: 2回実行でoutput jsonのsha256が一致。
- K11 API 0・費用0円: socket guardでネットワーク接続を例外化。LLM/ASR/TTS呼出0。Production fileは未変更。

## 4. 採否の事前ルール(Fable判断材料。Production適用は別委任)
- E4: K1〜K5・K7〜K11を満たせば『適用推奨』。K4の(b)正常音声のCascade送りが想定より多い場合は費用(0.2667円×件数)と品質(読み違い遮断)を併記して提示。
- E4-N: E4の合格に加え K6 を満たし、かつ実データで『PASS→非PASS』『非PASS→PASS』が0なら『適用可(整合化、PASS集合不変)』。実データのHEAD差が0件でも、承認済み仕様(非数値entryと同じCascade扱い)との整合のため推奨は妨げない。ただし実害が合成のみの場合は『実害なし・整合化』と明記する。
- 見送り推奨条件: K1/K2/K3/K5/K6(ii)/K7のいずれかが破れる、または別機構(P2のA4 C2同形異音除外など)との衝突が判明した場合。

## 5. 開示すべき限界
- Cascade(Azure)の結果はAPI 0では再現できない。『Cascade行き』は費用・件数の見込みであり、最終PASS/NGは保存Secondary転写のある行のみ実測。
- 母集団の実データは771+493既存転写で、本番頻度の推定は参考値。ひらがな濁点差は前回評価に負例が無く、本評価で初めて測る。
- 乗り物(封鎖/風さ等)は`sweep_cases_open333_e4_01.py`の5種類のみ。

## 6. 改訂記録
(なし。評価実行前に凍結。)
