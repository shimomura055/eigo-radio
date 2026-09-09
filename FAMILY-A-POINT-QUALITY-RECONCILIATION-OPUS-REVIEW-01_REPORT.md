# FAMILY-A-POINT-QUALITY-RECONCILIATION-OPUS-REVIEW-01 報告書

## 0. メタ情報

- **管理ID**: FAMILY-A-POINT-QUALITY-RECONCILIATION-OPUS-REVIEW-01
- **区分**: Opus設計レビュー(Lane A、News/Discovery Point品質整理の
  Reconciliation)。診断目的のOpus委任(PM_GOVERNANCE 11節の上限「Opusは
  診断目的で最大1回まで」に該当)。
- **エスカレーション区分**: L2(Fable判断によりOpusへ委任)。
- **HIGH判定理由(Fable委任文の記載に基づく)**: 先行するSonnet横断整理
  (`FAMILY-A-POINT-QUALITY-CONTROL-RECONCILIATION-GATE-01_REPORT.md`)が
  提示した中核的な因果連鎖(もぐらたたきが主因/Focus ModuleがRole収束を
  引き起こす等)を、Opusが実データ・コードで否定した。News(A3-UDR-3)/
  Discovery(D2-UDR-1)のProduction採用可否という以降の判断の土台が
  変わるため、新規Trial発注前の事後再集計(本タスク、段階1)を最優先と
  判定された。
- **Opus消費**: 約100,000トークン・処理時間372秒(Fable委任文記載)。
- **本セクションの位置づけ**: 以下§1はFableが受領したOpus最終メッセージ
  全文の**Fable転記の要旨**である(委任文に「Fableが受領したOpus最終
  メッセージ全文はFableの会話ログにあり、本委任文には要旨のみ記載」と
  明記されている)。本Sonnetタスクはこの要旨を改変せず構造化して転記する
  だけであり、Opusの原文そのものではない。原文全文はFableの会話ログに
  存在する。

---

## 1. Opusレビュー要旨(Fable転記、観点1〜9)

**観点1(構造図の評価)**: `FAMILY-A-POINT-QUALITY-CONTROL-RECONCILIATION-
GATE-01_REPORT.md`の一枚の構造図(Point品質関与14仕組み)自体は妥当。
ただし§3-Iの因果連鎖(「Trial-07のRole収束はFocus Module起因」)と§4の
原因分解、§2-3の根本原因推定に誤りがある。

**観点2(もぐらたたき仮説とoverlap指標)**: baseline 18 attempt中17で
lexical flag(もぐらたたきは主因ではない、flagされ続けているだけ)。
overlap_ratioの分母は「Point内の異なり内容語数」(26〜36語程度)であり、
1語の増減で約0.037動く。閾値0.40は分布の中央付近にあり、暫定閾値として
の妥当性根拠が薄い。Focus側の改善はPoint長の交絡(Focus条件でPointが
短くなっている可能性)によるものかもしれない。value単独NG時にもoverlap
診断を無条件構築する実装(2/2の事例で次attemptに新規lexical flagが発生)
は誤診断のリスクがある。推奨(未承認候補): 診断の条件分岐、閾値・分母の
再検討、Loop Budgetの再評価。

**観点3(Role Planning再計画)**: Role Planning再計画はDiagnostic結果
(lexical/value NG理由)を一切受け取らない「盲目の再抽選」であり、しかも
診断sectionより後ろに「必ず従うこと」という診断より強い命令形で連結
されている。整理候補1(Role Planning一本化)はTrend Synthesisで
`PRODUCTION_WIRED`のprompt書き換えを伴うため非推奨。

**観点4(Trial-07 Role収束の因果不在)**: Trial-07のRole収束は、Focus
ModuleがRole Planningへ到達する経路が存在しない(Role PlanningはFocus
Moduleを一切受け取らない、hint未接続)ため、Focus Moduleを直接の原因と
説明できない。Focus Module本文自体もmyth-correctionを明示的に指示して
いない。整理候補4(複数提示)はTrend Synthesisで既に実装済みのパターンで
あり不要。多様性を測るなら既存のPoint本文指標(cross_point_overlap、
既に毎回計算されているが未使用)を使うべき。

**観点5(Ledger-bounded interpretation)**: Ledger-bounded interpretationの
不一致という指摘自体は妥当だが、「Role収束経由」という説明部分のみ誤り。
最小変更はWriter側だが、既存の断定回避規則がなぜ効いていないかの確認が
先。Fact Checker閾値変更はFact Safety緩和でありUDR(A'転用不可)。

**観点6(G1語彙プライミング仮説)**: G1修正(OPEN-112-DIAGNOSTIC-RETRY-
POINT-BODY-REGRESSION-FIX-01)が語彙プライミングとして働いた可能性(baseline
P2 ratio 0.339→0.458)。¥0再集計を先に行い、残差が残ればN=10のA/B Trial
(¥60〜80)が必要。

**観点7(段階分け)**: 段階1((a)〜(e))を最優先、段階2は段階1の結果を見て
設計する。段階1と段階2で共通化できる部分がある。

**観点8(Dangling Reference/廃止候補)**: Danglingな参照なし。整理候補1は
Trend Synthesisの既存配線と競合するため不採用寄り。廃止候補となる仕組み
はなし。value単独NG時の診断構築を条件分岐すること自体は妥当な改善候補。

**観点9(UDR一覧)**: 閾値・分母の変更、Fact Safety緩和を伴う変更、
多様性とのトレードオフ判断(段階1完了後に判断)、Trend Focus Module改稿、
FACT-03は、いずれも本レビューの自律範囲外でUDR(ユーザー承認必要)。
自律範囲は段階1の再集計と報告までに限定する。

段階1の再集計結果・判定は`FAMILY-A-POINT-QUALITY-STAGE1-RECOMPUTATION-
01_REPORT.md`(root、別ファイル)を参照。
