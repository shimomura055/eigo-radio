## Opus必須レビュー(11-3 条件C、短縮): OPEN-333 E4/E4-N

**総合判定: 条件付き同意。** E4のみをProductionに適用し、E4-Nは見送る、というFableの暫定判断を支持する。適用前に入れるべき修正はM-1の1点(必須)で、M-2〜M-4は試験と監視の補強。採用可否はFableとユーザーが判断する。

### 論点1(既存`_cascade`の再利用と1箇所の変更で足りるか): 同意(M-1を条件とする)
- **足りる理由。** Candidate B/C/D-1は全文の読みを比較するので、カタカナ差が残っていれば一致しない。差分spanだけを見て、そのうちnon-cascadeだけを検査しているのはE(`er011:366-369`)だけである。したがって便乗PASSの穴はE分岐に限られ、変更は1箇所で足りる。
- **新しいPASS経路は開かない。** コードで次の5点を確認した。
  - Secondary(Azure)の受理は`SCG_PASS_CLASSIFICATIONS=("EXACT_MATCH","NORMALIZED_MATCH")`(`er007_ja_secondary_asr_01.py:83`)のままで変わらない。
  - `ORTHOGRAPHIC_VARIANT_CONFIRMED`は開かない。`primary_orth_ok`(`:624`)と`_orthographic_reading_confirmed`(`:372`)は、non-cascade差が1つでもあればFalseを返す。E4の結果は、Eが救ったnon-cascade差を必ず含む。
  - D-2の引き上げ(`_is_pure_phonetic_uncertain_cascade`、`er011:522`)も同じ理由で開かない。
  - `_numeric_value_equivalence`(`:515`)はTRUE_CONTENT_MISMATCHにしか適用されないので、E4のUNCERTAINには効かない。
  - Secondary転写の判定(`:347`、`:646`)も同じ`classify`を通る。そこで変わるのはPHONETIC_MATCH→UNCERTAINだけで、どちらも受理されない。評価のK7(受理変化0)と整合する。
- **ANDゲートの比較。** PASS経路の最終ANDゲート(値DIFF・否定差でNG)とNG経路のP1(`er078:641-644`、値DIFF・否定差の短絡)は、同じ`pvg`/`pneg`で判定する。P3で受理した後も、Secondary側の値ガード`svg`がかかる。
- **数値entryの注意点。** 数値entryでE4が発火すると、`protected_diff`(値ガードがNO_VALUESでnumber_mismatchesがある行。TCM時だけ計算)は計算されない。ただしHEADではこの行はPrimary PASSだった(最終ゲートはNO_VALUESを通す)。HEADより厳しくなる方向なので許容できる。
- **M-1(必須): fail-closedの例外処理は、E3の拒否判定(`_rej`、`:376-379`)を囲まないこと。**
  - try/exceptで`_cascade`へ逃がす範囲は、cascade_diffsの計算と記録だけに限定する。
  - 理由: E3の例外や拒否が`_cascade`に変わると、本来TCMになる行がUNCERTAINになる。これは実質E4-Nと同じで、A4(同形異音除外)を迂回する緩和になる。
  - 試験(h)「順序」に「E3 helperが例外を出したときは`_cascade`ではなく`return None`(TCM)になる」を追加する。

### 論点2(E4後のUNCERTAINでA4 signalsが計算されない): 同意
- E4で戻す行は、HEADではSecondaryを通らずPASSしていた。E4後に最終PASSになれるのは、Azureが原稿とEXACT/NORMALIZEDで一致した場合だけで、そのときもPASS_WITH_WARNING(事後試聴の対象)になる。最終PASSの集合はHEADの部分集合に収まるので、A4を迂回する新経路ではない。
- 非数値entryで「カタカナ差だけ」の場合も、既存の`:501`経路で同じ扱い(A4を計算しない)になっている。E4はこれと揃える是正である。
- **E4の範囲外の観察(ブロッカーではない)。** Candidate Eのchar単位の候補総当たりは、同形異音(今日→こんにち等)でもPASSし得る。これはE本体の承認済み挙動で、A4はTCMにしか効かない。E4はこの点を変えない。別件として認識しておけばよい。

### 論点3(E4-N見送り): 同意
- 44行すべてがHEADで`p2_exclusion:A4_C2_HOMOGRAPH`だった。E4-Nの実効はA4の解除であり、ユーザーが採用した安全条件に触れる。実データへの影響は0なので、見送りが妥当。
- A4を維持する変形は、実効が30行のラベル変更だけになる。不要という整理に同意する。
- 再検討の条件は適切。1点だけ付け加えると、再検討するときの論点は「E4-Nを入れるか」ではなく「A4(数値entryのTCM時)を見直すか」というユーザー判断(判断候補D)として立てるべきである。

### 論点4(範囲はcascade_eligible全般か、entity_like限定か): 同意(全般でよい)
- 承認済み仕様の文言どおりであり、B/C/D-1の濁点差→`_cascade`とも一貫する。
- ひらがなの濁点差は前段の全文判定(`:440`)で先にCascadeへ回るため、過剰にCascadeへ送る実害は確認されていない。
- opcodeの分断で偽の濁点差が出てCascadeに送られる可能性は理論上あるが、影響は費用だけで品質は下がらない。実測でも4/676に収まっている。

### 論点5(監視と`is_entity_like_mismatch_ja`の副作用): 条件付き同意(M-2、M-3)
- **M-2: 監視の指標を広げる。** Azure一致率だけでは足りない。E4で発火したセグメントについて、最終的にどうなったかを集計に入れる。
  - 区分: PASS_WITH_WARNING / 再生成後にPASS / 再生成上限に到達してHRまたはSTOP。
  - 理由: ヴェラ→ベラのような表記慣習の差は、Azureも同じように転写して再生成しても直らない可能性が高い。その場合、NG_BOTHが続いてHRに行き着く。
  - この挙動は、カタカナ差だけの行では既にHEADでも起きている既存の挙動で、E4の欠陥ではない。ただし費用と納期への影響はこの形で出る。
  - 報告条件に「E4で発火した行がHRに到達したら1件でも報告」を追加する。その場合の正しい対処は、E4をrollbackすることではなく、表記正規化(ユーザー承認が必要な別件)を検討することだと事前に明記しておく。
- 1runで3件超なら報告、という閾値はそのままでよい(固有名詞が繰り返される記事では件数がまとまって出る点に留意)。
- `is_entity_like_mismatch_ja`がFalseになる件は、統一judgeの経路では使われていないので、許容してよい。docstringかCURRENT_SPECに1行注記しておく。

### 論点6(適用計画の欠け): 概ね十分(M-3、M-4を追加)
- **M-3: 構造的な遮断を明示的なunit testにする。** 評価の集計で間接的に確認するだけでなく、次の3点を直接固定する。
  - E4の結果に対して`_orthographic_reading_confirmed`がFalseを返す。
  - `try_upgrade_voicing_cascade`がNoneを返す。
  - `_numeric_value_equivalence`がNoneを返す。
- **M-4: 数値entryでE4が発火した行(合成のcost num 1件の型)のE2E試験を足す。** 統一judgeにAzure stubを注入し、次を確認する。
  - Azure EXACT → PASS_WITH_WARNING。
  - 値を誤ったSecondary転写 → PASSにならない(`svg`が効く)。
- 一致確認の`off≡head`では、`asr_judgement`に新しいfieldが出ないこと(key集合が一致すること)も比較対象に含める。

### 参照ファイル
- `C:\Users\tensh\eigo-radio\er011_ja_asr_variant_layer_01.py`(304-306、366-384、513-551)
- `C:\Users\tensh\eigo-radio\er007_ja_asr_validator_01.py`(391-399、407-514、517-527)
- `C:\Users\tensh\eigo-radio\er007_ja_secondary_asr_01.py`(83、347-357、361-383、511-530、567-604、624-657)
- `C:\Users\tensh\eigo-radio\er078_asr_unified_judge_01.py`(148、179-189、601-655)
- `C:\Users\tensh\eigo-radio\docs\research\JA-ASR-FALSE-NG-ROOT-CAUSE-01\proto_open333_fix_06.py`(67-92。protoはwrapper方式なので、Production側でinline化したときの例外処理範囲がM-1の論点になる)
