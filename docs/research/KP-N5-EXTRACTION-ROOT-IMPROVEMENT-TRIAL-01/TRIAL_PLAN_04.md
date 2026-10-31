# TRIAL_PLAN_04 Phase 3b 事前登録(KP-N5-EXTRACTION-ROOT-IMPROVEMENT-TRIAL-01 委任_02、2026-10-31)

`TRIAL_PLAN_02`/`TRIAL_PLAN_03`の追補。Phase 3(fresh 8反復、`ev02/eval_p3_pick.json`)の結果を見たうえで、**未観測のfresh draw**に対する1アームだけを実行前に固定する。基準・判定規則はTRIAL_PLAN_02のまま。

## 0. Phase 3の観測(動機)
- pick-level S3(両表現同時、fresh 8反復): A9 slate 3/8(`put away` 8/8・`in the way` 3/8)、A10 区間分散 4/8(`put away` 4/8・`in the way` 7/8)、A12 見出し句除外 2/8、A7'(rerank)3/8(`in the way` 8/8・`put away` 3/8)、A4/A4d(型昇格)0/8(`put away` 8/8・`in the way` 0/8)。**全アーム<7/8**。
- **相補性**: A4d(型昇格順)は`put away`を、A7'(価値rerank順)は`in the way`を安定して残すが、1つの順位付けでは両立しない(`put away`=易しい句動詞、`in the way`=固定表現で、価値の種類が違う)。cap感度(参考A11、R1d): cap 10でも≤5/7。
- 以上は、**2つの順位付けを統合する**(単一基準の微調整ではなく、工程構成として2つの独立な順位の合議)が次の別方向であることを示す。

## 1. 追加アーム(実行前固定、パラメータ調整なし)
- **A13 順位統合(Reciprocal Rank Fusion、API 0)**: E2プールのkeep済み候補全件について、順位1=R1d順(型昇格+決定論tie、`pick_R1d`と同じキー)での位置、順位2=A7'のrerank(1 call、TRIAL_PLAN_02 §2-6と同一Prompt)が返した全候補の順序での位置(欠落はR0d順で末尾補完)。スコア = 1/(60+順位1) + 1/(60+順位2)(RRFの慣習値k=60、**固定・調整しない**)。スコア降順(tie=順位1)で`n5.pick`と同じ重複除去を適用して上位7件。rerank失敗時はR1dへフォールバック(記録)。Prompt・規則に表現名・出現回数を含まない。
- 比較のため同じ反復でA0・A2d・A4d・A7'も再計算(fresh draw 2回目の再現確認)。他のアーム(A1/A5/A6'/A8/A9/A10/A12)はPhase 3までに不合格が確定または別方向のため実行しない。

## 2. 反復・判定
- fresh: `untidi_b1b` rep 10〜13(N=4)+`untidi_a2` rep 8〜11(N=4)=8反復(**Phase 1/3の反復に適用しない**)。
- **A13のpick-level S3(両表現同時)≥7/8**なら、段階評価規則どおり A13とA0の最終候補にGEN5/VER5/CHK5を実行し、S2・N1〜N7・S4を評価、held-out(surname_b1b/moon_b1b/melos_a2 各N=2、新規draw)を実行して側作用を測る。**<7/8なら**これ以上の同種実行はせず、TRIAL_PLAN_02 §5-3に従い **USER_DECISION_REQUIRED**(回数を使わないアームで最低達成条件を達成不能)として報告する。
- 費用見込み: fresh 8反復≈¥12。A13合格時のみ+GEN約¥15+held-out約¥9。累計は止め線¥120内に収まる見込み(現在¥56)。
