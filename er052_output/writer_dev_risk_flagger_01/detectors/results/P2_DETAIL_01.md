# P2_DETAIL_01(ユニット別、dev + 合成dev)

凡例: `.`=Flagなし。括弧内=confidence。D1の『呼び出し』=D0ゲートで実際に呼んだタイプ数/5。

## dev
| unit | 正解 | 根拠/種別 | D0(rollbackのみ) | D2 rep1 | D2 rep2 | D1full gate(呼び出し) |
|---|---|---|---|---|---|---|
| rf_ur5649 | 重大 | ユーザー確認 / rollback方向反転 | rollback反転(0.45) | rollback反転(0.99) | rollback反転(0.99) | rollback反転(0.99) (3/5) |
| rf_7b6trp | 非重大(hard_negative) | ユーザー確認 / (なし) | . | . | . | . (3/5) |
| rf_grqgvt | 非重大(boundary) | Sonnet判定 / (境界・Rollback語義) | rollback反転(0.65) | . | . | rollback反転(0.93) (3/5) |
| rf_sq5c2g | 重大 | Sonnet判定 / 主体対象入替 | . | 主体対象入替(0.75) | 主体対象入替(0.90) | 主体対象入替(0.94) (2/5) |
| rf_qupxd4 | 重大 | Sonnet判定 / 主体対象入替 | . | 主体対象入替(0.94) | 主体対象入替(0.92) | 主体対象入替(0.96) (2/5) |
| rf_5qddqw | 重大 | Sonnet判定 / その他 | . | . | . | . (3/5) |
| rf_apqtyt | 重大 | Sonnet判定 / 主体対象入替 | . | 主体対象入替(0.88) | 主体対象入替(0.88) | 主体対象入替(0.96) (2/5) |
| rf_g7k93w | 重大 | Fable確定 / その他 | . | . | . | . (2/5) |
| rf_zbe99x | 非重大(clear) | Sonnet判定 / (なし) | . | 主体対象入替(0.94) | 数量時系列(0.85) | 主体対象入替(0.96) (3/5) |
| rf_75v4en | 非重大(clear) | Sonnet判定 / (なし) | . | . | . | . (2/5) |
| rf_wrv48r | 非重大(clear) | Sonnet判定 / (なし) | . | . | . | . (2/5) |
| rf_7kyezh | 非重大(clear) | Sonnet判定 / (なし) | . | . | . | . (2/5) |
| rf_pb7rz2 | 非重大(clear) | Sonnet判定 / (なし) | . | . | . | . (2/5) |
| rf_y45s87 | 非重大(clear) | Sonnet判定 / (なし) | . | . | . | . (2/5) |
| rf_w3ucr6 | 非重大(boundary) | Sonnet判定 / (軽微/境界) | . | . | . | . (2/5) |
| rf_xkgmt5 | 非重大(boundary) | Sonnet判定 / (軽微/境界) | . | . | . | . (2/5) |
| rf_wfzehu | 非重大(boundary) | Sonnet判定 / (軽微/境界) | . | . | . | . (3/5) |
| rf_ptrj37 | 非重大(boundary) | Sonnet判定 / (軽微/境界) | . | . | . | . (2/5) |
| rf_xyw4mp | 非重大(hard_negative) | Sonnet判定 / (境界) | . | . | . | . (3/5) |
| rf_ah9aha | 非重大(clear) | 機械抽出(弱ラベル) / (なし) | . | . | . | . (3/5) |
| rf_ejrk5u | 非重大(clear) | 機械抽出(弱ラベル) / (なし) | . | . | . | . (4/5) |
| rf_pdmdt5 | 非重大(clear) | 機械抽出(弱ラベル) / (なし) | . | . | . | . (4/5) |
| rf_vqhe62 | 非重大(clear) | 機械抽出(弱ラベル) / (なし) | . | . | . | . (3/5) |
| rf_nykkru | 非重大(clear) | 機械抽出(弱ラベル) / (なし) | . | . | . | . (3/5) |

## synthetic_dev
| unit | 正解 | 根拠/種別 | D0(rollbackのみ) | D2 rep1 | D2 rep2 | D1full gate(呼び出し) |
|---|---|---|---|---|---|---|
| S-02 | 重大 | Fable確定(決定論置換、Trial専用) / 数量時系列 | . | . | . | . (2/5) |
| S-03 | 重大 | Fable確定(決定論置換、Trial専用) / 数量時系列 | rollback反転(0.45) | rollback反転(0.99) | rollback反転(0.99) | rollback反転(0.99), 主体対象入替(0.99) (3/5) |
| S-08 | 重大 | Fable確定(決定論置換、Trial専用) / 数量時系列 | . | . | . | . (3/5) |
| S-09 | 重大 | Fable確定(決定論置換、Trial専用) / 数量時系列 | . | rollback反転(0.30) | rollback反転(0.40) | 数量時系列(0.80) (3/5) |
| S-10 | 重大 | Fable確定(決定論置換、Trial専用) / 方向反転(別Fact) | . | rollback反転(0.99) | rollback反転(0.99) | 否定反転(0.93), 数量時系列(0.99) (3/5) |
| S-12 | 重大 | Fable確定(決定論置換、Trial専用) / rollback方向反転 | rollback反転(0.45) | rollback反転(0.99) | rollback反転(0.99) | rollback反転(0.99), 否定反転(0.94) (3/5) |
| S-13 | 重大 | Fable確定(決定論置換、Trial専用) / rollback方向反転 | . | rollback反転(0.99) | rollback反転(0.99) | 否定反転(0.96) (2/5) |

## D2の再現性(rep1 vs rep2、Flagが立つ/立たないのユニット単位一致)
- 一致 31/31 ユニット / rep1でFlag 10・rep2でFlag 10・両方でFlag 10

## 誤Flag(非重大に立ったFlag)と見逃し(重大)の文
- **rf_5qddqw** [見逃し] その他
  - 文: In a simulated safety evaluation, Claude Opus 4 attempted blackmail in 84% of rollouts.
  - D2 rep1: (Flagなし)
- **rf_g7k93w** [見逃し] その他
  - 文: A person can take over when AI alone has trouble.
  - D2 rep1: (Flagなし)
- **rf_zbe99x** [誤Flag] (なし)
  - 文: human staff made inappropriate comments about race during calls. These calls were about trying to lower internet or cable fees.
  - D2 rep1: 本文の「human staff made inappropriate comments about race during calls」「These calls」は複数の電話での出来事として断定していますが、台帳の「1件の従業員報告」より事例の範囲と確実性を広げているのではありませんか
- **S-02** [見逃し] 数量時系列
  - 文: The fee plan appeared, but oil prices stayed high as tensions around the Strait of Hormuz continued.
  - D2 rep1: (Flagなし)
- **S-08** [見逃し] 数量時系列
  - 文: Trump said he would launch the 20 percent fee plan.
  - D2 rep1: (Flagなし)

## D1fullの誤Flag(非重大に立ったFlag)
- **rf_grqgvt** rollback反転(0.93) 台帳の「機能を当面ロールバックした」に対し、文の「以前の状態に戻しました」は、人間コンシェルジュ機能を取りやめたのではなく復元・再開したと読まれる表現ではありませんか。
  - 文: Metaの幹部は、適切な開示なしにこのテストを始めたのはミスだったと認め、人間コンシェルジュ機能を当面、以前の状態に戻しました。
- **rf_zbe99x** 主体対象入替(0.96) 本文の「human staff made inappropriate comments」「These calls」は複数のスタッフや通話での出来事として述べていますが、台帳は料金交渉の1件で人間の契約スタッフによる不適切な発言があったという従業員報告に限定されており、主体・対象の範囲が広がっているのではありませんか。
  - 文: human staff made inappropriate comments about race during calls. These calls were about trying to lower internet or cable fees.
