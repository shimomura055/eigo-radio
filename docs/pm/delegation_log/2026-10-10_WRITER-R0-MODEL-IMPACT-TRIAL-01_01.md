# 委任ログ: WRITER-R0-MODEL-IMPACT-TRIAL-01 委任_01(2026-10-10、Fable -> Sonnet)

ユーザー指示要旨(起票 2026-10-10):
- 目的: Fact Lock付きR0 Writerについて、R0モデル(gpt-6-luna / gpt-6.1-sol / gpt-6-astra)の違いがFact逸脱リスクに影響するかを確認。R0時点のみ。R1/R2/EN/Checker/Production wiringには進まない。
- テーマ: streaming_price(Disney+) / space_weapons / byd_recall の3つのみ。3モデルを同一Trial内で全て新規生成。Research・Fact Ledger・B3/注記版B3・Fact Lock Prompt・R0 Prompt・出力条件・後処理・Risk Flaggerは3モデル間で固定。Prompt最適化禁止。
- Risk Flagger: 既存のまま。件数を3件に固定せず全件保存(confidence・種類・対象文・対応Fact・理由)。confidenceは絶対評価に使わず分布のみ。既知例(Disney+理由不明断定/Reuters回答状況、宇宙兵器 秘密断定/1衛星->satellites、BYD 2件公告183,211台->1件化/数字対象範囲取り違え)の再発有無と新規逸脱を記録。
- 報告: 比較表(テーマxモデルFlag総数)、モデル別統計(総数/conf最小・最大・平均・中央値/種類別/R0費用/処理時間)、全Flag一覧。有用/誤検知は確定しない。優劣は確定しない。
- 費用: API費用はR0生成+Flaggerのみ。見積¥500以内ならそのまま実行可、超過見込みはSTOP。
- STOP条件: Prompt変更必要/Fact Lock仕様変更必要/Risk Flagger仕様変更必要/テーマ追加/500円超見込み/Production code変更必要/新Production仕様。
- Closeout: REJECTED/VALIDATED/USER_DECISION_REQUIRED。Production Prompt/routing/CURRENT_SPEC/Production Writerは変更禁止。

Fable補足: 出力先 er052_output/writer_r0_model_impact_trial_01/、Phase 1(事前登録、API禁止)->Phase 2(実行)->Phase 3(集計)、commit/pushはPhase 1完了時とPhase 3完了時。

Phase 1結果: er052_output/writer_r0_model_impact_trial_01/PREREGISTRATION_01.md。R0構造(a)、Flagger=D0+D2記事モード、見積約JPY295。
