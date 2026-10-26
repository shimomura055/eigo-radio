# OPEN_TRACKING_02 — OPEN-528 追跡(委任_02時点)

| 項目 | 分類 | 内容 |
|---|---|---|
| OPEN-528本体 | 修正へ進む | Phase 1実装完了=IMPLEMENTED_PENDING_EVIDENCE。次=Phase 2 runtime evidence(EVIDENCE_PLAN_02) |
| J-1 Local Rewrite未配線 | ユーザー判断要(判断候補D) | Z dialogueにLR未配線。3回NG->HR Lock/STOPで要件充足。LR新設は新仕様=別承認 |
| M-3(i)案 | ユーザー判断要(判断候補) | 外側ループの行数会計をpolicy基準に変更(Advのminimal_fallback併発時に従来方式へ到達可)。既存A2予算規則の変更のため未実施。現行(ii)は安全側STOP |
| lazy notes timing | 実害なし(開示) | notes LLM失敗STOPはlevelの最初のdialogue生成時(M-7の「TTS前」をlevel単位で満たす。TTSは未実行) |
| crash窓 | 実害なし(開示) | `after_attempt(verified)`と`finish`の間のms級crashはn+1再生成(費用のみ、3回上限は維持) |
| 新規run既定ON | Fable判断 | policy既定`fz_ctx_v1`。Phase 2 evidence前に新規runで有効化するか(ロールバック=`Z_DIALOGUE_CTX_POLICY_DEFAULT`) |
| env_stub | 実害なし | システムpyにgenai/pykakasi無しのため試験専用stub追加(Production無影響) |
