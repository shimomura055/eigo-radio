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

## 委任_07更新(2026-10-25)
| ID | 更新 | 27-3分類/11-8 |
|---|---|---|
| YPL6-O1 | OPEN-525として登録(共通module D'短ラグ検査の長尺Voice境界flag)。閾値0.6秒・Y向け新Gateは採らない。E-1の3 segmentはHuman Review経路(ユーザー試聴)で判断=E1_HUMAN_REVIEW_01.md | D(ユーザー判断候補・急がない)/ユーザー判断要 |
| YPL6-O2 | **本委任で是正**(`identify_ng_span`が既存の`_is_compound_spacing_only_span`を再利用。ハイフン/複合語分かち書き差のみのspanをNG spanにしない)。test追加。Productionでの別run実証は未(是正後はCLOSE候補、commit sha=RESULT_PACKET_YPL7) | B 承認範囲内/修正へ進む→完了 |
| YPL6-O3 | OPEN-517/333系で追跡(案β適用待ち)。E-1 a2 previewはユーザー試聴承認(同型事象の1件) | C 現タスクと独立/修正へ進む(別委任) |
| YPL6-O4 | 実害なし(記録のみ) | 実害なし |
| YPL6-O5 | 修正へ進む(別委任・text core所有)。OPEN-520に参照 | B/修正へ進む |
| YPL6-O6 | 実害なし(運用注記。E1_HUMAN_REVIEW_01.mdの再開コマンドは`.venv\Scripts\python.exe`表記) | 実害なし |
| YPL6-O7 | 実害なし(記録) | 実害なし |
| YPL6-O8 | Y Cap 200円へ更新(Fable、7-7。BUDGET_PLAN_04 §6)。runner定数は170のまま | 運用(Fable) |
