# sound_effect_position_analysis.md — 効果音位置の分析(候補提示のみ、判断はしない)

**前提**: 本分析はUSER_DECISION_REQUIRED。現行`CURRENT_SPEC.md`の
DECIDED仕様(ER-003-A2-AUDIO-01以降無変更)は「Comment前後の効果音:
専用効果音は入れない(ポーズのみ)」であり、本分析はこのDECIDEDを
変更するものではない。将来的にユーザーが効果音導入を検討する場合の
候補材料として提示するのみで、Production module・Promptへの実装は
一切行っていない。

## 現行の音声構造(既存DECIDED仕様、変更なし)

- Point One/Point Two直前に専用Notification音
  (`universfield-new-notification-07-210334.mp3`、A2/B1共通)が既に
  ある(Comment用SEとは別物)。
- ポーズ: 「ポイント解説」→Preview 0.7秒、Point One→Point Two 0.8秒、
  In One Line→Outro 0.8秒、A2 Comment(英語→日本語)1.0秒、A2 Comment
  (日本語→英語)0.8秒。
- Comment前後には専用効果音なし(ポーズのみ)。

## 3記事の構成比率(`structure_ratio.md`)を踏まえた観察

- 4本(small_bag A2/B1B、meta A2/B1B)すべてでPoint2が全体の21〜26%と
  最大の比率だった。Point構造(Point One/Two)は既に専用Notification音
  という区切りを持っており、他のsegment境界より「音声上の区切り」が
  すでに強い。
- Comment(C1〜C4)は4本とも合計で全体の17〜24%程度で、記事間の比率の
  崩れは大きくなかった(観察範囲内では安定)。
- 本文1+本文2の合計比率は記事間で最大約10ポイントの差があった
  (meta記事の方が本文が長い)。

## 候補案(判断はしない、材料の提示のみ)

(a) **どの位置なら安定するか**: 観察された4本では、Preview→本文1の
境界とPoint2→C4の境界が、全記事で構成比率のブレが比較的小さい位置
だった(Point構造の前後はNotification音で既に区切られているため、
それ以外で「毎回ほぼ同じ役割を果たす境界」を挙げるなら、Preview直後
[本編開始]とOutro直前[全編終了]が候補になる)。

(b) **記事Volume(語数・比率)が変動しても破綻しないか**: 本文1/本文2の
比率は記事間で最大10ポイント変動しており、本文の内部(本文1と本文2の
間)に固定の効果音を置く設計は、記事によって「本文全体の何%地点か」が
安定しない。一方、Preview直後・Outro直前のような「segment種別の境界」
(本文の何%地点かではなく、どのsegmentが終わったか)を基準にする設計
であれば、語数変動の影響を受けにくいと考えられる。

(c) **後半に偏らないか**: Point2が4本とも最大比率(21〜26%)を占めて
いるため、既存のPoint Notification音は結果として「後半寄りの位置」に
すでに来ている。仮にComment前後へも効果音を追加する場合、C1〜C3
(前半〜中盤)にも同程度の頻度で置かないと、既存のPoint Notification音
と合わせて後半に音が偏る可能性がある(観察に基づく懸念点、断定ではない)。

(d) **Point1/Point2前後が適切か**: Point1/Point2前後は既にNotification音
で区切られており、仮にComment用の効果音を新設する場合、Point
Notification音と役割が重複しないよう「Comment用は別音源・別音量」に
するか、あるいはPoint前後には追加しない、という切り分けが考えられる
(判断はしない、選択肢の提示のみ)。

## 結論

本分析は候補の整理のみであり、効果音導入の可否・位置の決定は行わない
(USER_DECISION_REQUIRED)。
