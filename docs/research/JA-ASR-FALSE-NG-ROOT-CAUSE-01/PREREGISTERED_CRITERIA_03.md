# PREREGISTERED_CRITERIA_03(v2用。委任_04、2026-10-25。基準は`PREREGISTERED_CRITERIA_02.md`と同一、対象をv2へ)
## 0. 凍結
- 凍結対象=**v2** `docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/proto_reading_compare_02.py` sha256(全体)=`bcb042c651f05c7801b382e51b802a870e1240892d3ae65efc6cdbbca27c6144`。再評価の実行前に凍結(評価コード`eval_api0_v2_01.py`作成・実行より前にv2を固定。評価中・後にv2を変更していない)。
- v1(`8799aa60fed66e2d…`)は不変・REJECTED。v2のv1からの差分=V2-1の1点(`DESIGN_02.md`§1にunified diff)。
- 評価データ=v1と同一(N-1 150[+構造的同一1]・N-3 30[`n3_clips_01.json`]・P-3 NG pool 150転写・P-4 421ユニーク・月題12転写・Melos preview)。新規転写・新規TTS・新規API 0。**注記**: N-3 30 clipはv1の不合格(N3-21)を露呈したデータであり、v2の修正はN3-21が属する一般型(Secondary値のみ一致×不規則読み)への規則で個別ID特例ではないが、同一データでの再評価である点を限界として明記する(未知データでの汎化は未確認)。
## 1〜7. 基準(02の再掲・変更なし。対象のv1→v2読替のみ)
1. 増分誤PASS=0(N-1 150+N-3 30、Primary層案A+A4(a)込み。構造的同一の扱いは02§1)。既存誤PASSは報告のみ。
2. 非回帰: P-4で回帰0、既存PASSの判定・ラベル不変(421ユニーク/現行PASS334)。
3. 誤NG削減: P-1 attempt2=PASS。P-3 flip全件に「不当」=0。ENGINE_reading_difference=0または個別正当化。
4. 最終ANDゲート/警告継承: v2経路でも`JA_PRON_EQUIVALENT`・`JA_NUMERIC_IRREGULAR_READING`が残る(Primary側コードパス不変)。
5. HR発生率増加0(P-4回帰0で担保)。
6. 費用: v2再評価は有料API 0(追加費用0円)。Phase 3全体Cap ¥60以内(実費約5.6円/保守側29.65円)に変化なし。
7. 到達上限=**VALIDATED**(限定)。Production無変更。配線はユーザー正式採用後(Phase 4は本再評価の対象外)。
## 8. 事前登録写像(Status)
- 基準1〜6を全て満たす → 「v2=VALIDATED(限定)候補」(効果が限定的である点[月題12転写中1件救済・A4(a)は不規則読みを除外]を併記)。最終Statusは Fable。
- 増分誤PASSが1件でも出る → v2不合格→v3再凍結。
- 緩和(基準変更)は禁止。厳格化は可。
