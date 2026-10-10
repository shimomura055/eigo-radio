# FAMILY-X-TTS-ASR-ROOTCAUSE-01 委任_21 (2026-10-11)

- 依頼元: Fable。目的: META Advanced(B1B) "Muse" ASR不一致の過去対策棚卸し+根本原因+再発防止案(read-only)。
- 実施(Sonnet): ログ/コード/SSOT Grep調査、`get_hint_for_text`のread-only再現、ローカルfaster-whisper(無料)で既存wav再転写。課金API 0回、コード・SSOT・音声変更なし。
- 成果物: `er053_output/family_x_tts_asr_rootcause_01/MUSE_ASR_RCA_01.md`、`docs/pm/RESULT_PACKET_ASR_21.md`(ローカル)。
- 要点: (1) "Some Muse calls"の/m/連結で独立3ASR(OpenAI/Azure/ローカルwhisper)が"use"と聴取。(2) Ledgerのcascade_unresolved_entity(MYOOZ)は設計上TTS注入から除外(Opus L2 BLOCKER-1)。(3) comment_2のLocal Rewrite全滅は`er020 validate_candidate_is_full_segment`の先頭15文字一致チェックが文頭の問題語で過剰拒否(7 Gate自体は候補1/2/4が全PASS)。(4) 分類: 適用範囲外+承認済み仕様の実装欠陥、配線漏れなし。
- 提案(未実装): A1欠陥修正、B1音韻衝突Lint等。新仕様は人間ユーザー承認前提。新規OPEN登録2件を提案(未登録)。
- STOP: 新規仕様判断(B1/B2/B4)とA2(Opus L2決定の緩和)はFable/ユーザー判断待ち。
