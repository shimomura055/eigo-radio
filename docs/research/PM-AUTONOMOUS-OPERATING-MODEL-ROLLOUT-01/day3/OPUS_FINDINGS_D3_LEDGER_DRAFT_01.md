# OPUS_FINDINGS_D3_LEDGER_DRAFT_01: Opus条件A所見OF-D3-01〜15の台帳行(草案。SSOT未反映)
管理ID: PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01 / Day3 Phase2 委任_F2 / 2026-10-15
性質: `docs/pm/OPUS_FINDINGS_LEDGER.md`(11-5)への追記案。**本委任では台帳本体は編集しない**(KGCPWが編集中)。本体への追記は委任_F3。原文は`OPUS_REVIEW_D3_01_VERBATIM.md`(逐語)。形式は台帳ヘッダ10列(ID/日付/Opus#/区分/指摘要旨≤40字/Fable採否/反映(委任#)/Evidence/Closeout確認/Status)に合わせた。ID番号は台帳本体の最大ID+1との衝突を、追記時(F3)にGrepで確認すること。
Status「IMPLEMENTED_F2」は、`PM_GOVERNANCE.md`/`CLAUDE.md`/`PM_BRIEF.md`へ反映済み(F2のcommit後)、Agent定義・テンプレ・SSOT・盲検リプレイ検証は未了(F1/F3/G)であることを示す草案上の表記。台帳の既存状態へは追記時に`IMPLEMENTED`として遷移させる(Evidenceは行番号で、F2のcommitで固定した版を基準とする)。
採用時の目的との照合1行(11-5)は、各行のFable採否欄の末尾に付した。

| ID | 日付 | Opus# | 区分 | 指摘要旨(≤40字) | Fable採否 | 反映(委任#) | Evidence | Closeout確認 | Status |
|---|---|---|---|---|---|---|---|---|---|
| OF-D3-01 | 2026-10-15 | ROLLOUT Day3 Phase1 Opus条件A | BLOCKER | A9が「副作用→STOP」(2026-09-09)を自律解決側へ緩和 | 採用(目的照合: 副作用STOPを維持し、失敗[目的未達]のみ11-6対象) | 委任_F2: A9是正文+11-6「維持する境界」に副作用STOP | PM_GOVERNANCE.md:1927(A9)、:2417付近(11-6維持する境界) | 未 | IMPLEMENTED_F2 |
| OF-D3-02 | 2026-10-15 | 同上 | MAJOR(M1) | 無益反復の歯止めの穴(「中」の書き続け等) | 採用(a)(b)(c)(d)。(e)=check_delegation_promptのWARNは任意でF1判断(目的照合: 回数をSTOP条件にせず進捗で止める) | 委任_F2: 11-6「無益反復の歯止め」+QDC記録の費用欄 | PM_GOVERNANCE.md:2411(歯止め)、QDC記録欄(:2407付近) | 未 | IMPLEMENTED_F2+F1(e=check_delegation_prompt.py WARN実装、test3件、2026-10-15 F1) |
| OF-D3-03 | 2026-10-15 | 同上 | MAJOR(M2) | L3を条件B・任意レビューで実質回避できる | 採用(目的照合: L3後の人間判断を維持) | 委任_F2: 11-6にL3/条件B区分文。sandwich-pm.mdへの同文はF1 | PM_GOVERNANCE.md:2421 | 未 | IMPLEMENTED_F2(sandwich-pm.md未) |
| OF-D3-04 | 2026-10-15 | 同上 | MAJOR(M3) | 原則4「回数はSTOP条件にせず」の範囲が広すぎ | 採用(目的照合: Production retry上限・26-2(c)等を弱めない) | 委任_F2: 11-6適用範囲宣言+CHARTER_DRAFT_04の原則4是正文。Charter挿入はF1 | PM_GOVERNANCE.md:2423、day3/CHARTER_DRAFT_04.md §2 #3 | 未 | IMPLEMENTED_F2(Charter挿入=F1) |
| OF-D3-05 | 2026-10-15 | 同上 | MAJOR(M4) | U3'潜在迂回路の中間状態・受入前検出の扱いが未定義 | 採用(Fable判断: 発火/有効配線の範囲を広げず、潜在迂回路=SUSPENDED。ユーザー原文の解釈を含むため最終報告で確認を求める。目的照合: 検出・報告の動機を損なわない) | 委任_F2: 11-7(3状態・受入前検出は違反でない・違反でない検出も1行記録・失効時の既存OFFコードはSTOP報告でユーザー判断) | PM_GOVERNANCE.md:2435-2442 | 未 | IMPLEMENTED_F2(OPEN_ITEMS状態行・flag突合test=F3) |
| OF-D3-06 | 2026-10-15 | 同上 | MAJOR(M5) | 盲検リプレイの答え漏洩・git履歴共有・push/API安全・汎化限界 | 採用(目的照合: 検証の妥当性を担保) | 委任_F2: 11-7/7-9/15-9から事例固有語を除く(新設節のGrep 0)。盲検設計の改訂はday3/DAY3_IMPLEMENTATION_PLAN_02_ADDENDUM.md | 新設4節の事例語Grep 0(RESULT_PACKET_ROLL3F2.md)、ADDENDUM §2 | 未 | IMPLEMENTED_F2(盲検環境構築=委任_G) |
| OF-D3-07 | 2026-10-15 | 同上 | 論点3(U2-Q1) | 回答までの11-4サイクル計上・B10注記 | 採用(目的照合: 11-4を独断で緩和しない) | 委任_F2: 11-6「他規定との関係」+11-4直後の注記(11-4本文は逐語不変) | PM_GOVERNANCE.md:2425、:2388 | 未 | IMPLEMENTED_F2 |
| OF-D3-08 | 2026-10-15 | 同上 | MINOR(A8/A5) | A8「守ること」の読み誤り/A5のL3後条件の欠落 | 採用(目的照合: 8項目すべて維持) | 委任_F2: A8=「8項目はすべて維持。1と6は語句のみ修正」。A5(sandwich-pm.md)はF1 | PM_GOVERNANCE.md:1786-1790 | 未 | IMPLEMENTED_F2(A5=F1) |
| OF-D3-09 | 2026-10-15 | 同上 | MINOR(U5①〜④) | 7-7/7-9の優先関係・安価な代替・新規runの定義・ベースライン | 採用(目的照合: 品質を下げる安価化をしない、比較義務を合理化) | 委任_F2: 7-7末尾+7-9本文+15-9ベースライン。Open Item文案=ADDENDUM §3 | PM_GOVERNANCE.md:865・869、15-9 :3009 | 未 | IMPLEMENTED_F2(Open Item=F3) |
| OF-D3-10 | 2026-10-15 | 同上 | U5-Q1 | TTS判定のBatch換算は未配線なら実態より低い | 採用(Fable判断。7-4の「量産=Batch前提」は変更せず判定の表示方法のみ。最終報告でユーザーに1行確認。目的照合: 70円判定が実態より楽観にならない) | 委任_F2: 15-9判定値 | PM_GOVERNANCE.md:3007 | 未 | IMPLEMENTED_F2(ユーザー確認待ち) |
| OF-D3-11 | 2026-10-15 | 同上 | MINOR(Charter) | 第3項「超過見込みを含む」がハード停止と誤読される | 採用(目的照合: 7-6の「到達で自動STOPしない」と整合) | 委任_F2: CHARTER_DRAFT_04 第3項 | day3/CHARTER_DRAFT_04.md §2 #4 | 未 | IMPLEMENTED_F2(Charter挿入=F1) |
| OF-D3-12 | 2026-10-15 | 同上 | MINOR(A1) | CLAUDE.md A1置換文が長くCharterと重複 | 採用(目的照合: 改訂時のずれを防ぐ) | 委任_F2: CLAUDE.md A1を短文化 | CLAUDE.md:59-65 | 未 | IMPLEMENTED_F2 |
| OF-D3-13 | 2026-10-15 | 同上 | 論点7 | 7-8の2「未承認の次Trialを独自判断で開始しない」とU2の関係 | 採用(目的照合: 承認範囲外を独断で開始しない) | 委任_F2: 11-6「他規定との関係」に1句 | PM_GOVERNANCE.md:2425 | 未 | IMPLEMENTED_F2 |
| OF-D3-14 | 2026-10-15 | 同上 | 追加所見 | 2026-10-05指示との照合記録/複数セッション並行の日次超過/MODEL_ROUTING_TRIAL_LOGの旧記述 | 採用(目的照合: 過度な停止条件を独自に追加していないことの記録) | 委任_F2: 7-9に1句+11-6に1句。残存リスクはRESULT_PACKET_ROLL3F2.md。MODEL_ROUTING_TRIAL_LOGは許容リスト(履歴) | PM_GOVERNANCE.md:863、:2425、7-9確認義務(:867) | 未 | IMPLEMENTED_F2 |
| OF-D3-15 | 2026-10-15 | 同上 | 論点9 | 欠けている単位(中立化・flag突合test Open Item・70円ベースライン Open Item・台帳登録・3状態) | 採用(目的照合: 受入条件A〜Eの機械的担保) | 委任_F2: 3状態/中立化/本ドラフト。Open Item文案=ADDENDUM §3 | 本ファイル、ADDENDUM §3 | 未 | IMPLEMENTED_F2(Open Item起票・台帳本体=F3) |
