管理ID: LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01(LR・Fallback横断仕様の正式採用・Production Wiring。原文=docs/pm/delegation_log/2026-10-28_LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01_USER.md)
Status: **2026-10-28 ユーザー正式決定受領(APPROVED_FOR_PRODUCTION: UD-1 LR後英文を表示本文へ反映/UD-2 AI島 AI agents・AI systems/UD-3 正常LR・Fallbackのみの停止・HR要求を解除、最終Human報告=LR赤・Fallback濃青・資料限定)。Phase A完了(W1-W4+INTEGRATION_01)→Opus条件A完了(OPUS_REVIEW_01、M-1〜M-10全採用)→Phase B進行中: 委任_06(B1 final_adoption+M-4)/委任_07(B0/B2 er129台帳)並列実行中。次波=委任_08(B4分類核+差分監査)/09(B5報告生成器)/10(B3 overlay・parity Gate準備)→統合配線commit(1 commit: parity Gate・M3/Y/Z切替・overlay・Z注記撤去・B6)→B7既公開是正→B8 evidence→SSOT/受入**
進行中: 委任_06/07(Phase B wave1)。完了: 委任_01〜05、Opusレビュー。成果物=docs/research/LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01/
次: Fable統合→SSOTへユーザー決定を登録(委任_05)→Opus条件Aレビュー→Phase B実装(並列: 本文反映/Gate/報告資料/記録)→test→runtime evidence(保存run再評価+最小有料)→既公開4件是正→Fable受入→SSOT/Git→最終報告(原文§12の10項目)
STOP条件: 注記の制作本文・TTS・ASR・公開本文・KP表示・Prompt混入禁止/試行回数・待機・Fallback Style・LR範囲・ASR基準・Voice/速度・確定内容保護は不変/品質Gateの弱体化禁止(正常LR/Fallbackのみの停止解除に限定)/A/B/C音声方式の置換禁止/確定内容と衝突する本文変更はSTOP/予算: 設計・Gate・表示はAPI 0、runtime検証は最小・日次1,000円内
UDR-blocking: 告げ口心臓=ユーザー最終試聴待ち(blockingではない)。UDR-MONKEY-1据置
報告運用(2026-10-28ユーザー決定 PM-REPORTING-RULES-01): 中間報告なし・ツール/委任/worker経過の表示なし・タスク単位で完了報告1件・例外(重大品質/安全・予算超過見込み・ユーザー判断事項・明示STOP・重大Blocker)のみ即時。Voice案件=Schedar→Fenrirへ修正(USER_02)
QDC: 2026-10-28当日 約20円消費(告げ口心臓Phase 2)。本案件Phase A=API 0
前案件: LR-FALLBACK-M3-CROSS-FAMILY-AUDIT-01(OPEN-565、SSOT同期済み、UD-1〜3は本案件で決定)/FZ-TELL-TALE-HEART-RESELECT-REMAKE-01(完成版公開・ユーザー最終試聴待ち、commit 2a3248621)

===== 並行案件 =====
管理ID: FZ-TELL-TALE-HEART-RESELECT-REMAKE-01(『告げ口心臓』学習項目V3再選定・本文音声再制作・完成版公開。原文=docs/pm/delegation_log/2026-10-27_FZ-TELL-TALE-HEART-RESELECT-REMAKE-01_USER.md)
Status: **2026-10-28 委任_03完了: Phase 2 runner rc=0(実費19.94円・累計約24.81円/Cap150円)・受入検証全PASS(①②③逐語一致/文法0件/Style・ASR・速度v2・Chunk/LR採用0/本文=固定正本無変更/page_verify PASS)・SSOT同期済み。Production完成、ユーザー最終試聴待ち(PASS未取得)。完成版=https://shimomura055.github.io/eigo-radio/user_test/family_z_tell_tale_heart_reselect_01/index.html、受入=ACCEPTANCE_PHASE2_01.md**。(旧) 2026-10-28 ユーザー選定受領(原文=…_USER_03.md)→照合コードPASS(Std/Adv、候補ID・候補集合sha・本文sha一致、文法0件確定)→confirm済み(rev1)→Phase 2 runner起動中(kp,tts_b1b,tts_a2,provision_shell,gate,assemble,pages,page_verify、--pages-dir user_test/family_z_tell_tale_heart_reselect_01、approved 60円)**。(旧) **第1報済み・ユーザー選定待ち(SYNC-28反映済み: 文法0件=正常動作、D-1/D-2判断候補、OPEN-503/568、累計4.87円)**。(旧) 委任_01完了(第1報): 本文固定(run_sf_prod_02)・新run run_reselect_01でV3候補生成(Std9/Adv9、文法0件)・フォーム公開、実費4.08円。ユーザー選定待ち(rc=4)。本文音声はKP確定後(runner入口制約)。報告=docs/pm/RESULT_PACKET_FZTTR1.md
進行中: なし(委任_03完了、commit反映済み)
次: ユーザー最終試聴待ち。(旧)runner完了→Fable受入(①②③/文法0/Gate/ASR/Style/Chunk/LR有無/本文=音声/page_verify)→SSOT同期→最終報告(原文§5の9項目)。LR採用segmentがあればUD-1未決のため該当部STOP
STOP条件: 学習項目のAI独断確定禁止/本文変更禁止/LR採用segmentは完成版へ進めず報告/Cap ¥150
QDC: Cap ¥150(Phase 1見積は委任_01 BUDGET_PLAN_01)
