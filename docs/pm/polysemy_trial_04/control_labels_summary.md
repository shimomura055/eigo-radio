# Control(Before)段別ラベル横断(TRIAL-04 P4e、¥0、推測ラベル・Fable未確認、DEVでありProduction仕様ではない)
詳細: er052_output/open233_polysemy_trial_04/runs/<slug>/eval/E_<slug>_control.md
## 1 記事×対象fact×段(忠実/逆転/曖昧/未採用)
| slug | 対象fact | brief | R0 | R1 | R2 |
|---|---|---|---|---|---|
| meta | HC-012 ロールバック | 忠実 | 忠実 | 曖昧(復元型候補) | 曖昧(復元型候補・強) |
| meta | HC-014 | 未採用 | - | - | - |
| hormuz | HF-009 縮小→戻る | 忠実 | 忠実 | 忠実 | 忠実 |
| space_weapons | F-001/F-002/F-011 | 忠実 | 忠実 | 忠実 | 忠実 |
| space_weapons | F-009/F-007 | 未採用 | - | - | - |
| sewer | F-011/F-010/F-016 | 未採用 | - | - | - |
| sewer | F-012 喜多方(代替) | 忠実 | 忠実 | 忠実 | 曖昧(冒頭「長い管から家ごとの浄化槽へ」) |
| ai_control | EVID-006/004/CONTROL-001 | 未採用 | - | - | - |
| ai_control | CONTROL-002 3条件 | 忠実 | 欠落 | 逆転 | 忠実 |
## 2 逆転型の発生数
- 確定の逆転型: ai_control R1の1件(「三つが特定の環境でそろい」=3条件が成立したと読める、台帳は「現システムが満たす所見ではない」)。他4記事は0。
- 曖昧(逆転寄り候補): meta R1/R2(「元に戻す」型)計2、sewer R2冒頭1。
- P0a指定の対象factのうちbrief採用はmeta HC-012・hormuz HF-009・space_weapons F-001/F-002のみ。sewer/ai_controlの指定factはbrief未採用=N+B側で「比較不能」になり得る(sewerは代替F-012、ai_controlは代替CONTROL-002で評価)。
## 3 Meta rollback経路(Control)
- brief「…2026年9月22日までに人間コンシェルジュ機能をロールバックした」=忠実(「当面」欠落)
- R0「ロールバックしました。Muse全体を停止したわけではありません。」=忠実
- R1「いったん元に戻しました」=曖昧(復元型候補)
- R2「ロールバックしました。…元に戻されたのは、人間スタッフが電話を担当する機能です」=曖昧(復元型候補・強、要Fable確認)
- 復元・以前の状態に戻す型表現: R1,R2の2段。Before参照(E2E_02復元型3/5)と同種。
## 4 候補件数(記事別 新誤断定/留保欠落/説明過多、軽微含む)
meta 0/3/2、hormuz 2/2/1、space_weapons 1/1/2、sewer 3/2/3、ai_control 0(逆転に計上)/1/3。計 6/9/11。
## 5 決定論指標(JA逐語率 R0/R2、文数 R0/R1/R2)
meta 0.109/0.126、22/26/27 | hormuz 0.117/0.182、18/22/22 | space 0.020/0.056、18/23/28 | sewer 0.000/0.061、18/28/27 | ai_control 0.000/0.018、22/23/23
