# CHECKLIST_M1_01(M1 OOV複数発音候補、Production Wiring Checklist 14項目、2026-10-14)

判定: **配線済み・隔離runner runtime evidence取得済み・`PRODUCTION_WIRED`は付与しない**(未充足: 5部分・11部分・14)。M1のStatusはF1(OPEN-340)とは別に評価(UDR #55)。

| # | 項目 | 判定 | 証跡 |
|---|---|---|---|
| 1 | 正式初回経路 | 充足: `er006_secondary_asr_01.py`のPrimary#1/P2/S1/S2/forced-secondaryに配線(`m1_enabled`既定True、en-US限定)。er003 L146 rescue・dialogue/point_headingsは共有cascade経由(runnerで`segment_id=None`相当も確認) | commit 94fb0c03、`WIRING_PATCH_02.md` |
| 2 | retry/fallback/regen整合 | 充足: retry上限・Gate・予算は無変更。M1は判定層のみで再試行・API呼出を追加しない。候補集合はsegment最初の試行前に凍結 | wiring test 22件、`regression_01/` |
| 3 | Trial専用実装に依存しない | 充足: `er006_m1_multi_candidate_01.py`はProduction module(`er077_*`はevidence scriptのみでProduction経路から非参照) | module、grep |
| 4 | Regression/Validator/integration test PASS | 充足(既知失敗1): M1 68・配線22・F1 39(pytest)・er077 14・er011_b1 26等PASS。er006系43件中1失敗(`er006_model_routing_pricing_coverage_test_01`、Family Z model key未更新=M1と無関係) | `regression_01/` |
| 5 | 正式経路でのruntime発火 | **部分(未充足)**: 隔離evidence runnerが実Production cascade(`evaluate_attempt_with_cascade_detail`)を実音声36観測で通し、M1受理21件を確認(JPY3.3435)。**自然発生のProduction記事run(KP/本文)でのM1発火は未取得** | `EVIDENCE_RUN_01.md`、`clip_results.json` |
| 6 | actual model_id/routing | 充足: primary=gpt-4o-mini-transcribe、secondary=Azure Speech(phrase list)、TTS=gemini-3.8-flash-lite-tts(Aoede)を`runner_execute.json`に記録 | `runner_execute.json` |
| 7 | CURRENT_SPEC更新 | 充足(M1節を追記) | CURRENT_SPEC |
| 8 | DECISION_LOG更新 | 充足(D-2'限定置換・UDR #52-55整理を記録) | DECISION_LOG |
| 9 | OPEN_ITEMS更新・整理 | 充足(OPEN-339更新、OPEN-354/355起票) | OPEN_ITEMS |
| 10 | commit/push/merge | 充足見込み(明示add・secret scan・Managed-ID trailer。結果はRESULT_PACKET_SNSR) | git log |
| 11 | 承認内容とProduction挙動の一致 | **部分(未充足)**: 承認(複数の合理的発音候補のいずれか1つで音韻整合、綴りのみ根拠は不可、上限6、F1内側)と一致する挙動を確認(C2のみ。C3/後付け候補0、非音素一致・content残差は却下)。**C1(CMU全異読)の実機発火は未観測**、Ledger confidence=lowのみの受理 | `EVIDENCE_RUN_01.md` §2-3 |
| 12 | Dangling Referenceなし | 充足: 新規参照(`CHECKLIST_M1_01.md`/`EVIDENCE_RUN_01.md`/`STOP_SCOPE_RULE_01.md`/`evidence_01/*.json`)は実在ファイルのみ | ls確認 |
| 13 | UDR #52〜55整理 | 充足: #52/#54/#55=判断済み、#53=既存承認範囲内(OPEN-340のF1仕様と実装が一致、限定方向のみ)。『異議がなければ承認』扱いなし | USER_DECISION_REGISTER_01 |
| 14 | 共有state/Ledger不変・telemetry隔離 | 充足: 共有state 8ファイルmd5 before/after一致、Ledger md5=snapshot、telemetryはrun dir内のみ。ただし**Ledger自動/人手エントリ区別フィールド(OPEN-339)は未決**でlow信頼自動エントリ起因の受理を事後監視する運用のみ → 区別フィールド未決は未充足扱いとして`PRODUCTION_WIRED`宣言前に判断 | `runner_execute.json` |

## 未充足
- #5: 自然発生Production runでのM1発火evidence。
- #11: C1(CMU全異読)実発火の未観測。
- #14(注記): Ledger由来low信頼エントリの区別フィールド要否判断(OPEN-339の新規OPEN項目2)。
最終受入(`PRODUCTION_WIRED`宣言)はFableがChecklist全充足を確認してから。
