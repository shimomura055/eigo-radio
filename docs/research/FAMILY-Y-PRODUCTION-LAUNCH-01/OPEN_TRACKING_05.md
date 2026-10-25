# OPEN_TRACKING_05 (委任_06、2026-10-25)

| ID候補 | 内容 | 11-8分類 | 次の一手 |
|---|---|---|---|
| YPL6-O1 | Repetition QA D'が長尺Y Voice(E-1宅配)で閾値0.6秒の境界(0.60-0.83)に張り付き連続flag | ユーザー判断要の可能性(D: 閾値/文境界Chunk=新仕様。OT-42同根) | Fable判断。閾値は変更せず |
| YPL6-O2 | ER-020 identify_ng_span がハイフン付きASR転写を正規化せずNG span化し、QAのみ失敗の文でR0本文の語を書換え(redeliveries->repeat deliveries) | 修正へ進む(B: 既存の表記正規化仕様との不整合=不具合)。別委任(ER-020) | Y側はGateがBLOCKし実害なし。X/Zで同条件発生し得る |
| YPL6-O3 | a2 preview(JA)「思いどおり/思い通り」誤NG(OPEN-517型。07Aは救済側でない) | 修正へ進む(別委任: 案β適用待ち) | OPEN-517/522-524で追跡 |
| YPL6-O4 | y_style_gateは音声statusを検査しない(PASS表示≠音声OK)。EVIDENCE_01「b1b完成」は誤記 | 実害なし(assemble AVGで止まる) | 必要ならgate強化を別委任 |
| YPL6-O5 | UNMAPPED再生成の個別理由が未保存(U-1) | 修正へ進む(text core所有の別委任) | COST_ANALYSIS_01 |
| YPL6-O6 | pending_bannerの再開コマンドが`py`(venv外でgoogle.genai無し) | 実害なし(運用注記) | OPERATIONS追記 |
| YPL6-O7 | 監査ログtheme_idがrun名で、E-3/E-1が同一idで混在 | 実害なし | 記録 |
| YPL6-O8 | Y Cap管理: 委任_05較正費の未算入 | 運用(Fable) | 実累計約166.85円 |
