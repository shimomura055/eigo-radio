# RESULT_PACKET ASR-FLAP-T-PRODUCTION-WIRING-01 委任_02(2026-10-31、実装・検証。PRODUCTION_WIRED判定=Fable)
- 実装: er139_flapt_equivalence_01/er139_flapt_provenance_01(新規)+既存最小加算。flag既定ON(literal)、親flag=er109。量産単価+0。開発実費約0.49円(Cap15円)。
- 検証: 新規72 test PASS / 既存67 file回帰=新規失敗0(変更後失敗集合は変更前の部分集合) / 保存11,181転写replay: 出自なし・Puck|proはOFFと0行差、救済71行(bertie→birdie 61, latter→ladder 10)、誤救済0、writer/rider救済0 / 保存attempt正式再判定: FX4 latter→Ladder救済、Z Bertie→Birdie 3/4救済、出自なし/未確認/flag OFF/scope外はNG。
- BATCH実run: X Adv(Aoede|gemini-3.8-flash-lite-tts)・Z Adv(Fenrir|fl, Algieba|gemini-2.5-pro-preview-tts+1.06x子登録)・Z Std(Aoede|fl+6%子登録)。sidecar生成clip 6/6=100%。自然なFlap転写は未発生(発火は保存attempt再判定+adapter実経路testで確認)。
- 未実施: Y runner / X Std runner専用の実run(共有leaf+scope unit+他実runで到達実証)。
(1) 既存仕様整合: CURRENT_SPEC.md:1864(ASR収束を根拠にしない)、er109_xz_scope_01(第3層、最終AND無変更)、原文:28/71、DESIGN_01 §2-11、voice_probe_03。
(2) 未承認機能の既定値: 本機能は承認済み・既定ON(FLAP_T_EQUIVALENCE_ENABLED=True、AST testで固定)。A/B/C・scope外・親flag OFFはno-op(test PASS)。
(3) 失敗終了時成果物: 失敗終了なし。X初回runはsource dir欠落でbilling前停止(ev02/x_run_console_try1_prebilling_stop.log)→複製後再実行成功。最終成果物=EVIDENCE_02.md+ev02/。出自なしの既存音声は適用外(fail-closed)で目的要件(承認範囲の救済のみ)に適合。原文要求(既定ON・X/Y/Z配線・誤救済防止)に沿う。
(4) 撤去・残置: 撤去規則なし(新規層追加のみ)。Opus3-2項3(vote_check_from_auditの包み)は不採用。残存: er109 PRODUCTION_SCOPE_IMPORTERS更新のみ。
判定整合: 重大NG=なし
判断候補(根拠付き): (i) 表slow6_confirmedは未強制(Fable指示「None/6.0=確認済み」に従う)。(ii) 環境起因の既存回帰失敗が25件(OPEN-501記載の4件より多い。変更前後で不変、C=現タスクと独立)。(iii) Voice表sha変更で過去救済音声のStore再利用がblockされる(仕様)。
詳細: docs/research/ASR-FLAP-T-PRODUCTION-WIRING-01/EVIDENCE_02.md
