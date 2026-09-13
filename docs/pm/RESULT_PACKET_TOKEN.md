管理ID: PM-TOKEN-EFFICIENCY-STATUS-MEASUREMENT-02
Status: COMPLETED(read-only現状把握のみ、実装・SSOT編集・Git操作・API呼び出しなし、¥0)
詳細: `PM-TOKEN-EFFICIENCY-STATUS-MEASUREMENT-02_REPORT.md`(root新規)

## 主要数値(要約)
- E-1/D-1/G-1適用開始2026-09-12、F-1前倒し更新2026-09-13(`PM_GOVERNANCE.md`
  1279-1294行実測)。A-1(Consolidation統合)はREJECTED済み(既存)。
- same-file reread率: 全Agent合算37.8%(Phase1原本)とSonnet単体タスク内限定
  27.8%(Before,N=18)は**別指標**(範囲混同注意)。After合算(既存Trial2件+
  本測定2件、N=4)は31.0%で、Beforeを下回らず改善の実測なし。
- 直近10委任(2026-09-12〜13): 委任文平均3,352.7字/中央値3,123字、
  subagent_tokens平均205,695/中央値202,750(Before全254件平均144,056より高いが
  カテゴリ偏り[Production配線・Trial系]による交絡、悪化と断定不可)。
- 定型比率: 直近10件で完全一致行(閾値>=2)6.3%(既存union4.78%と同水準)。
  短縮ラベル「E-1/D-1/G-1」自体は直近10件に0件出現、実質的言い回しでの言及は
  9〜10件に存在。
- **重要な新発見**: `subagent_tokens`は全ターン累積usageではなく最終ターン
  usage合計とほぼ一致(実測2件99.97%・99.86%一致)。同2件の全ターン累積は
  49,466,043 token(167.2倍)・6,620,586 token(45.0倍)。既存全報告
  (254件36,590,141token等)は`subagent_tokens`基準のため、実際の延べ処理量は
  記載値より大幅に大きい可能性(N=2、要追加検証)。
- F-1遵守: `docs/pm/transcripts/`非0バイト1/3、直近10委任の非0バイト転記は
  2/10(20%)のみ。徹底されていない。
- haiku-worker実績: セッション全体で言及1件のみ(増加なし)。

## 判定材料(判定はFableが確定)
- E-1/F-1: 評価不足〜効果不十分(数値上は改善が見えない)。D-1: 新規baseline
  取得のみ(全文read率47〜50%)、Before比較値なし。G-1: 効果小(元々寄与小)。
- 主要浪費源Top3: (1)累積context再処理(cache_read、tool_uses数にほぼ比例)、
  (2)Production配線タスクの対象コード読込量(31〜63%)、(3)同一task内reread
  (27.8%〜31.0%で高止まり)。
- 週次Claude Max寄与見込み: 方法A(既存`subagent_tokens`基準)16.2M〜42.7M
  token/週。方法B(新発見の倍率106倍を反映、精度低・未検証)17億〜45億token/週相当。

## 費用
¥0(API呼び出し・Git操作・SSOT編集・コード変更なし)。

## Next Action(提示のみ、判断はFable/ユーザー)
1. `subagent_tokens`の定義(最終ターンusage近似)を前提に、既存報告群の解釈を
   訂正すべきか判断が必要。
2. F-1手順の失敗原因(直近10件で80%が0バイト)の追加調査要否。
3. E-1効果不十分の扱い(継続/見直し/追加Trial)の判断。
