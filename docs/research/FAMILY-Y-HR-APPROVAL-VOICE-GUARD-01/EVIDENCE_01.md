# EVIDENCE_01 (OPEN-535) - 詳細は evidence_01.json / evidence_cli_after.json / evidence_before_approvals.json

- 新規test 16件PASS(`er121_family_y_hr_approval_guard_test_01.py`): Voice不一致→不適用+再生成要求 / Voice一致→維持・resume重複生成0 / 記録欠落・矛盾→不適用 / 非Y承認(preview等)不変 / chunk承認は親Voiceで判定 / 新形式y_binding(Voice・Style) / Gate(asm._segment_gate_status)が旧承認を使わない / stamp不正刻印STOP / 共有er011の署名・照合不変 / 接続試行0。
- 回帰: er121* 330件(328 pass/1 skip/1 fail=並行Agentの未追跡testのCRLF planner、無関係)、er011* 292 PASS、er019* 595件(594 pass/1 fail=R4 Hunk Classifier、変更前から赤)、er063* 130 PASS。
- 正式経路(runner CLI `--mode mock`、偽generator・API 0): 旧Algieba承認を残したrun複製で、`--regenerate-stage tts_a2 --only-segments y_voice_1`起動 → 承認はquarantineへ退避(Algieba->Puck)・previewは維持・y_voice_1のみ1回の(mock)TTS・entry Puck刻印。修正前同状態は`check_before_generation`が`HUMAN_APPROVED`で0 call skip。
- 実TTS: 使用せず(費用 0円)。
- 注意: `run_hrguard_ev_01_mock`はmock起動3回/300秒でRESTART_STORMのSTOPが自動作成された(scratch dirのみ・API 0・STOPは削除せず放置)。
