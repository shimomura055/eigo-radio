# Opus短縮レビュー依頼(条件C: 重要変更のProduction適用前)— OPEN-333系 E4(便乗PASS是正)とE4-N
依頼元: Fable(JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_13成果)。レビュー対象はProduction適用**計画**で、Production変更は未実施。前回レビュー(`OPUS_REVIEW_01_OPEN333.md` 論点5/R-4)の続きなので、E3の議論の再確認は不要。
読むもの(この順、短縮): `OPEN333_E4_DESIGN_01.md`(§1・§4)→ `OPEN333_E4_EVAL_01.md`(§1・§2・§3.1・§6)→ `OPEN333_E4_APPLY_PLAN_01.md`(§1・§2)。Production読取: `er011_ja_asr_variant_layer_01.py:289-306,366-384`、`er007_ja_secondary_asr_01.py:361-383,551-604`、`er078_asr_unified_judge_01.py:639-662`、P2除外表A4=`:148`。

## 論点(3〜5。各点で『同意/修正/反対』と根拠を)
1. **E4は『既存`_cascade`の再利用+Candidate E分岐の`_pass`直前1箇所』で足りるか**。cascade_eligible判定は`protected.content_diffs`をそのまま使い再計算しない(`protected_check_ja`の述語と必ず一致)。Primary PASS→Primary UNCERTAINにしたとき、統一judgeでP1(値DIFF/否定)・P3の扱いが、E3後の数値entryと非数値entryの双方で承認済み仕様どおりか。Primary PASSが受けていた『最終ANDゲート』がNG経路ではP1で同等に働くか(`er078:639-650`)。
2. **E4後のUNCERTAINがA4(同形異音除外)を計算しない構造**(`is_tcm=False`のため`signals`を作らない、`er007_ja_secondary_asr_01.py:567-604`)は、E4で戻した行について許容できるか。Eが救った同音差が同形異音候補(今日/こんにち等)でも、HEADでは(Secondaryを経ず)PASSしていたため、Secondary確認付きになる分は厳格化であり、A4を迂回する新経路にはならない、という理解で良いか。
3. **E4-Nの扱い**。評価でE4-Nの実効=『数値entryのA4_C2_HOMOGRAPH除外の解除』(44/44行がHEAD NG_EXCLUDED/A4)と判明し、実データ影響0・最終PASSの到達可能性が広がるため見送り推奨。この整理で妥当か。A4維持の変形は『ラベル変更のみ』になり不要、で良いか。再検討の条件(正式runで数値entry A4即NGの正常音声が実際に出た場合)は適切か。
4. **E4の範囲(cascade_eligible全般 vs entity_like限定)**。ひらがな濁点差の便乗PASSは50件でHEAD PASS 0(再現せず)で、実測上は差が無い。承認済み安全条件が両方を明記しているため全般を採る方針は妥当か(過剰なCascade送りの懸念は無いか)。
5. **監視と受入れ**。`candidate_e_cascade_return`の1run 3件超でFable報告、最初の3〜5 runでAzure一致率(PASS_WITH_WARNING/NG_BOTH)を実測、の方針で再生成増(上限+0.59pt)を追えるか。診断関数`is_entity_like_mismatch_ja`が混在diffsでFalseになる副作用(統一judge経路では未使用)の扱いで良いか。

## 事前に開示する限界
Cascade後のAzure一致率は未測定(補足の注入確認のみ)。乗り物5種・名前16種の合成。実データの該当は4行(0.59%)で頻度推定は粗い。
