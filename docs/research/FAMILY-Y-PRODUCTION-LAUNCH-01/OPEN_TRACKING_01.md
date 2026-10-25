# OPEN_TRACKING_01: Family Y Production立上げ — Closeout確認項目と未完了事項の追跡(Phase 0)

管理ID: FAMILY-Y-PRODUCTION-LAUNCH-01 委任_01 / 2026-10-25。正本の追跡先は`OPEN_ITEMS.md`(**OPEN-520新規**、OPEN-463/484に統合追記)。本書は委任文§11のCloseout確認項目を、適用対象・Status・残作業・解消条件付きで一覧化したもの(新しい管理場所ではない)。分類は11-8(修正へ進む/ユーザー判断要/実害なし)。

| ID | 区分 | 項目 | 適用対象 | 現Status(2026-10-25) | 残作業 | 解消条件 | 追跡先 | 11-8分類 |
|---|---|---|---|---|---|---|---|---|
| OT-01 | 承認済みY未配線 | Y正式Production入口の新設 | Y | 入口なし(`production_reachable=False`) | `er121_*` runner・test・evidence(DESIGN_01) | 受入12項目+E-1完了 | OPEN-520/484 | 修正へ進む(委任_02〜) |
| OT-02 | 承認済みY未配線 | KP一般化(所有格possessor_roles+A-1)のY正式KP段 | Y | X/Z=WIRED_PENDING_FABLE、Y Trial scaffoldのみ効く | Y正式KP段が`sc.run_key_phrase_canonicalization`(hook付き)を通る | OPEN-484 (a)〜(f)すべて | OPEN-484 | 修正へ進む |
| OT-03 | 承認済みY未配線 | Part 1「Vocabulary & Expressions」(Adv) | Y Adv | X/Z=PRODUCTION_WIRED | stage 8直後に接続、`part1_items`をHRと共有 | Y AdvページにPart 1表示+訳工程call記録 | OPEN-512/484 | 修正へ進む |
| OT-04 | 承認済みY未配線 | 共通音声仕様(Style profile・Std減速・AUW・QA・TTS記号・固有名詞・KP vote等 = 台帳YL-A01〜A23) | Y | Yは未着手 | 台帳『適用』行ごとにY runnerの配線+test | 各行の完了証拠が揃う | OPEN-520+`spec_ledger_01.json` | 修正へ進む |
| OT-05 | 承認済みY未配線 | PNAP(OPEN-450)・er109(OPEN-459)のscopeに"Y"追加 | Y(共有module) | scope=X/Zリテラル(`er103...:42`、`er109_xz_scope_01.py:25`) | 最小編集+A/B/C・X/Z不変test(Opus条件Aの対象) | Y runでscope活性・既存署名43,033件不変 | OPEN-450/459/520 | 修正へ進む(開示事項。承認原文はX/Z) |
| OT-06 | 承認済みY未配線 | routing key `FAMILY_Y_*` とpricing | Y | 0件 | `er006`にkey追加(別agent編集中=最小編集) | actual model_id==routing==期待、未登録model fail-closed | OPEN-520 | 修正へ進む |
| OT-07 | 承認済みY未配線 | Closing一般化のProduction移植・案B固定注入・Lead/紹介・注意書き・In One Line廃止 | Y | DEV Trialのみ | YL-C04〜C09の実装 | sha一致test・`closing_record.json`・E-1/E-3 | OPEN-520 | 修正へ進む |
| OT-08 | VALIDATED未決 | 実在意見ベースVoice生成方式のProduction採用範囲(VALIDATED限定、2テーマ) | Y | 判断待ち(B: Fable確認) | Launch原文/要旨で採用範囲を確認。公開前宿題を引継ぐ | Fable確認記録 | OPEN-520/463 | 実害なし(承認範囲内と読める。確認のみ) |
| OT-09 | VALIDATED未決 | 公開前宿題: V1根拠がR2+(個人ブログ/note等、再利用許諾なし)のみ・TBS権利確認・目視照合1名・V2単一出典例外 | 宅配/SNS | OPEN | 許諾取得or出典置換。公開判断の時点で提示 | 権利確認記録 | OPEN-463/484 | 修正へ進む(公開前) |
| OT-10 | VALIDATED未決 | 男性2声(V1 Algieba/V3 Schedar)の聞き分け(音声段の宿題) | 宅配E2E | 機械指標のみ(F0差はAdvでほぼ同一) | E-1の聴取。必要なら割当見直しはユーザー判断 | ユーザー試聴所見 | OPEN-463 | ユーザー判断要(試聴後) |
| OT-11 | VALIDATED未決 | Closing一般化Round 2既知課題(Gate FAIL率25〜50%、選定の並び順依存5/6、テーマ内多様性低、単価high平均19.2円) | Y(新規記事) | 記録のみ(Prompt 02で立上げ) | 運用実績(gate_history)で再評価。Prompt 03/Gate文言はOT-20/21 | 実績n増+ユーザー判断 | OPEN-463/520 | 実害なし(既知・記録済み。ブロックしない) |
| OT-12 | 進行中 | KP HR(OPEN-518, er119)・文法HR(TOP 2) | X/Y/Z | 実装中(別agent) | Yは接続点。I/F確定後に結線。HRあり/なしevidence(E-2) | Y runでHR両経路 | OPEN-518/484(g) | 修正へ進む(依存待ち) |
| OT-13 | 進行中 | Part 2文法解説+Trial-08選定(OPEN-519, er120) | X/Z(Y Adv) | module完成・runner未接続 | 接続点。Adv限定・0件許容 | Y Adv runでPart 2生成または0件記録 | OPEN-519/484 | 修正へ進む(依存待ち) |
| OT-14 | 進行中 | JA ASR誤NG根治(OPEN-515/517) | 共通ASR | Trial中(案A) | 採用後にY JA segmentで確認。Y側の追加実装を避ける構造 | ユーザー正式採用+共通module配線 | OPEN-515 | 修正へ進む(別案件) |
| OT-15 | 進行中 | Std part3減速ガード(OPEN-466)・Repetition QA単複偽陽性(OPEN-469) | 共有 | OPEN | Yは既存HR Lock手順で受ける | 別案件の判断 | OPEN-466/469 | 実害なし(Y E2Eで発生した場合のみ顕在) |
| OT-16 | 進行中 | Style profile engine横断化(OPEN-415) | X/Y/Z | OPEN | Z方式(定数参照+drift test)を推奨、Opus条件Aで確認 | Y runのstyle記録がprofile一致+drift test | OPEN-415 | 修正へ進む |
| OT-17 | 将来反映 | 未承認のため**先行採用しない**: Closing Prompt 03、Gate文言変更、Closing medium化、Tier内順位改善、会話速度v2のY適用、JA ASR案A | Y | 未承認 | 承認時に台帳行を更新しYへ適用 | ユーザー正式採用 | 台帳YL-F04〜F07 | 実害なし(未承認の保管) |
| OT-18 | 将来反映 | 意見収集(Theme Package作成)の自動化・量産単価の再評価 | Y | 現状は人手約25分(LLM 0円) | 別案件で費用実測+仕様判断 | 別案件起票 | OPEN-520 | ユーザー判断要(新仕様。今回は着手しない) |
| OT-19 | 将来反映 | 量産単価の目標超過(通常Y記事 約69〜93円、中央81円 > 70円) | Y | 見込み | 実測後に原価低減案を提示(承認事項は独断採用しない) | 実測+ユーザー判断 | BUDGET_PLAN_01 | 実害なし(目標超過の見込み開示。ブロックしない) |
| OT-20 | 判断待ち固有差分 | Gate文言(`leak_tension_reverts_to_research`肯定側=旧B骨格)の扱い(G-1/G-2) | Y(Closing Gate) | **ユーザー判断候補D** | 実績取得後に1件として提示 | ユーザー判断 | PROMPT_GATE_ALIGNMENT_01 §6 | ユーザー判断要 |
| OT-21 | 判断待ち固有差分 | Chunk TTSのY Voice長文パートへの適用(承認原文X/Zのみ) | Y | 判断待ち(B: Fable確認) | Y初回は非適用。聴取所見があればY用Trial提案 | 聴取結果 | 台帳YL-B08 | 実害なし(先行採用しない) |
| OT-22 | Prompt・Gate未解決 | I-1〜I-4(既存run_gate運用・切り口付加・gate_history・固定本文は書換え禁止STOP)の実装 | Y | 設計済み | `er121_family_y_production_01.py`に実装+test | test PASS+E-1/E-3のgate_history | OPEN-520 | 修正へ進む(承認済み範囲内) |
| OT-23 | DEV/Trial専用機能 | **Productionへ移植しない**: DEV予算skip(Gate SKIPPED_BUDGET)、`patched_*`モジュール差替え、alias segment ID、Trial名前空間のMaster store、`--paid`+BUDGET_APPROVED.json、`@xr.fx_iol.family_x_in_one_line_scope()`(In One Line scope) | Y | DEVに残置 | 移植しないことをtest(Grep固定)で保証。DEVは無変更 | Production moduleにこれらの識別子が無い | OPEN-520 | 修正へ進む |
| OT-24 | Dangling Reference | 参照整合: 台帳の`tracking`/OPEN番号/pathが実在、`er121_*`の被参照、docs内pathの実在、旧alias ID・Aoede直書き・in_one_line参照の残置0(Production側) | Y | 未検証(実装後) | Closeoutでgrep(DESIGN_01 §11) | Grep 0件 | OPEN-520 | 修正へ進む |
| OT-25 | 未反映SSOT | SSOT反映: ①OPEN-520新規+OPEN-463/484追記+DECISION_LOGエントリ(本委任で実施) ②CURRENT_SPEC「共通仕様のFamily別配線Status表」のY列更新とY節新設(**実装・evidence後**) ③PM_GOVERNANCE Closeout項目33(**提案文のみ、Fable承認待ち**) ④USER_DECISION_REGISTER(Fable) | 全体 | ①のみ完了 | ②③④は上記条件で別途 | 各反映のcommit | OPEN-520 | 修正へ進む(③はFable判断) |

- OT-08/OT-21は27-3のB(承認範囲内で自己解決、Fable確認)。OT-20のみ**真に新しいユーザー判断(D)**で、立上げを止めない。OT-10は試聴後のユーザー判断、OT-18は新仕様(着手しない)。
- 完了条件の全体像: OT-01〜07・22〜24が揃い、OT-12〜13の接続点が結線され、E-1〜E-5が完了した時点で`PRODUCTION_WIRED`の検討(判定はFable、ユーザー最終試聴PASSは別Status)。
