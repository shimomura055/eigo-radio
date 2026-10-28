# OPUS_REVIEW_REQUEST_01(条件A 独立技術レビュー依頼の下書き。JA-ASR-FALSE-NG-ROOT-FIX-02 委任_01B。Fableが送付要否を判断)
目的: 日本語ASRの『正常音声がNGになる』誤NGを減らす改善方式(案R)について、**実装・Trial前の設計の独立レビュー**を依頼する。Productionは変更しない。ユーザー承認範囲(user原文§1: v2/β/P-1は正式採用保留、今回のTrial成功はProduction採用を意味しない)。

## 添付(必読)
`DESIGN_PROPOSAL_01.md`(候補比較・推奨案R)、`EVAL_UNIFIED_01.md`(6音声×方式、負例の増分誤PASS)、`RESIDUAL_NG_ANALYSIS_01.md`、`PREREGISTERED_01.md`。プロト: `JA-ASR-FALSE-NG-ROOT-CAUSE-01/proto_reading_compare_02.py`(v2)、`b_light_proto_02.py`(β)、`docs/research/JA-ASR-FALSE-NG-ROOT-FIX-02/eval_unified_01.py`(統一ハーネス)。

## 論点(絞る。これ以外は不要)
1. **推奨案の誤PASSリスク**
   - v2: 音素列が原稿と同一な同音異表記(月の詩は/死は/氏は/市は+正しい値)を救済する。『音声としては原稿と同じ音』なので増分誤PASSは区別不能という整理(事後分類)は妥当か。他に区別不能でない誤PASS経路は無いか。
   - v2のPrimary側に不規則読みガードが無く、『今日は一日中雨→ついたち中雨』がPASS_Wになる(増分1型)。ガード追加+Production判定へのフォールバックで十分か。
   - β: Primary数値garble(d×10^k断片+残り)をSecondary値証人で救済。最悪露出(Secondary=原稿そのもの)で増分2行。Secondaryが原稿値を返しPrimaryがgarbleした場合の誤PASS経路(実際の音声が別値)は残るか。
   - (ii) ASR再試行(best-of-N): 負例のdraw分布が無い状態で、誤PASS増加はN倍以内と見てよいか。N3 30 wav×4 draw(概算¥0.7)の実測設計で足りるか。
2. **一般化**: 『月のしわ』固有でない汎用規則として成立しているか(助詞は→わ/へ→え、桁区切り、数詞断片、同音異表記)。『超→こえ』(訓読み+送り仮名)の辞書拡張(v-c)をどの条件(両engine一致、C2同形異音の除外)なら安全と見るか。
3. **既存Gateとの干渉**: F1+F2(READING_MATCH最終Gate)、E3/E4(Candidate E)、A7、C2、P1/P2との相互作用。v2ラベルがREADING_MATCH非該当である点の妥当性。回帰0(1706行)で足りるか。
4. **Human Review条件**: 残余(reselect a3=2エンジンが『スギノ』、ms_03 a1=『こえ』読み)を機械確定できない場合の条件付きPASS/個別試聴の条件設計。PASS_WITH_WARNING(試聴必須)をPASSと別扱いにする運用で、『警告付きPASSを無条件PASSと同一視しない』(ユーザー§6)を満たすか。

## 期待する出力
各論点について『問題なし/修正要/不可』+根拠。**新しいGateの増設が必要か、既存運用で足りるか**も明示。Opusレビュー後のProduction採用はユーザーのみが承認する(Opusレビュー自体はユーザー承認Gateではない)。
