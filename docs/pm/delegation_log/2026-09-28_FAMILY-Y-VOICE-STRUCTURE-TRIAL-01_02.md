## 管理ID

FAMILY-Y-VOICE-STRUCTURE-TRIAL-01 の Trial 記録の SSOT 反映+CURRENT_SPEC 残存「判定待ち」表記の確認。¥0、コード変更なし。一時ファイル `docs/pm/ACTIVE_TASK_SSOT4.md` / `docs/pm/RESULT_PACKET_SSOT4.md`(commitしない)。**SSOT編集権: 本タスクのみ**(直列化ルール。他Agentは現在なし)。開始時・commit直前に `git status --porcelain CURRENT_SPEC.md DECISION_LOG.md OPEN_ITEMS.md docs/pm/REPORT_LEDGER.md` で他差分なしを確認。

## 性質/到達上限Status/禁止事項

Trial記録(Status `USER_DECISION_REQUIRED`、Fable判定済み)。CURRENT_SPECへFamily Y仕様は追加しない(Trialのため)。禁止: コード変更、`git add -A`、履歴書き換え。E-1/D-1/G-1: 再読なし、Grep→範囲Read、git出力最小化。F-1: 退避不要。T-0: 本委任文を `docs/pm/delegation_log/2026-09-28_FAMILY-Y-VOICE-STRUCTURE-TRIAL-01_02.md` へ保存し `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-28_FAMILY-Y-VOICE-STRUCTURE-TRIAL-01_02.md --json-out docs/pm/delegation_log/2026-09-28_FAMILY-Y-VOICE-STRUCTURE-TRIAL-01_02.md_check.json`、結果1行記録。T-2: TTSなし。T-3: ¥0。

## 事前指定Read一覧

- `docs/pm/RESULT_PACKET_FY1.md`:30-42(SSOT追記案)
- `FAMILY-Y-VOICE-STRUCTURE-TRIAL-01_REPORT.md`:170-186(§10 status案)
- `CURRENT_SPEC.md`:825-835、:1520-1528(残存「判定待ち」表記2箇所、NEWS-VOCAB-LEVEL行・KEY-PHRASE-DB-HYBRID行)
- `docs/pm/REPORT_LEDGER.md`: Grep `KEY-PHRASE-DB-HYBRID` 行群(各IDのStatus)

## 事前指定Grep一覧+追記位置・更新位置の手順

1. `docs/pm/REPORT_LEDGER.md` 新行: `FAMILY-Y-VOICE-STRUCTURE-TRIAL-01 | Trial | USER_DECISION_REQUIRED(Fable判定、2026-09-28) | FAMILY-Y-VOICE-STRUCTURE-TRIAL-01_REPORT.md | commit d2bacf9c | Opus発火なし`(既存列構成に合わせる)。
2. `DECISION_LOG.md` 末尾: 新規エントリ「## FAMILY-Y-VOICE-STRUCTURE-TRIAL-01: Family Y Voice構造改善Trial(2026-09-28)」: ユーザー指示要旨(Fact Selection/Voice Fact Assignment/Angle先決め/Fact is context, not script/Family X既存R1→R2流用/Family B既存Voice重複対策流用)、使用記事(Family B ai_hiring_3v Standard)、流用した正式名称(Family X「Storyline決定+B3 Fact選定」、Family X R1→R2 Revision指示文逐語+previous_response_id連鎖[JA専用Fact Check/記号チェックは英語Voiceへ適用不可のため未適用、Fable事後承認]、Family B `run_overlap_monitoring_3v`/`run_analytical_leakage_check_3v`)、結果(前段は機能・情報不足なし・fact重複0/R1→R2でFamily B Leakage Check fail-field 2→3→11と悪化、LLM rubric単独は逆に改善と判定し乖離)、Fable判定 `USER_DECISION_REQUIRED`、ユーザー判断待ち論点(R1→R2の扱い[Trial-02: 最小制約1文+Leakage Check must-fix gate/見送り/打ち切り]、評価方法のLeakage Check必須併用)、費用¥5.90、Production採用は未決。
3. `OPEN_ITEMS.md` 新規(次番号から): (a)「Family X R1→R2 Entertainment RevisionとFamily Y Voice Fact抑制方針の構造的緊張(Trial-01で実測、対処はユーザー判断待ち)」、(b)「Voice系評価でLLM rubric単独評価のバイアス(既存Family B Leakage Check併用の必須化、ユーザー判断待ち)」、(c)「Family X Fact Ledger形式とFamily B系Verified Fact Ledger形式の非互換(Trial内使い捨てアダプタのみ、恒久アダプタのProduction化要否)」。Status いずれも OPEN。
4. 残存表記確認: `CURRENT_SPEC.md` の「判定待ち」2箇所(830行付近 NEWS-VOCAB-LEVEL、1524-1525行付近 KEY-PHRASE-DB-HYBRID)について、該当管理IDを特定し、(i) `KEY-PHRASE-DB-HYBRID-SOURCE-REFERENCE-CONTRACT-PRODUCTION-WIRING-01` または `KEY-PHRASE-DB-HYBRID-FAMILY-X-PRODUCTION-WIRING-01`(いずれもFable判定 `PRODUCTION_WIRED` 済み、根拠 commit `48bd7dd4`/`8c2da18e`)に属する残存表記なら `PRODUCTION_WIRED` 表記へ同期、(ii) `KEY-PHRASE-4PLUS1-TOPIC-PHRASE-PRODUCTION-01` や NEWS-VOCAB-LEVEL 等の未判定IDなら**無変更**とし、RESULT_PACKETに「ID・行・現状文言・据え置き理由」を記録。

## Git

add対象: SSOT 4点+delegation_log+`_check.json`。コミット: `FAMILY-Y-VOICE-STRUCTURE-TRIAL-01: Trial記録をSSOTへ反映(USER_DECISION_REQUIRED)+CURRENT_SPEC残存表記同期`、trailer `Management-ID: FAMILY-Y-VOICE-STRUCTURE-TRIAL-01`。`git push origin main`。

## 報告

適用箇所/新規OPEN番号/残存表記の判定結果/差分所有者確認/commit hash/raw URL(4 SSOT)。
