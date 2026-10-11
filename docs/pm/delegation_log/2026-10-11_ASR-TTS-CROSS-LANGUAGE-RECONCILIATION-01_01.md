# ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01 委任_01 (2026-10-11、Sonnet実行層、日本語側)

範囲: 日本語の現行仕様一覧、g8「ガス->カス」調査、日本語オフライン比較、例外分類(暫定)。read-only・有料API未使用(API未使用)。Production/Prompt/Validator/Routing/SSOT無変更。英語側は並行agentの担当で重複調査せず。
成果物: er056_output/asr_tts_cross_language_reconciliation_01/(JA_SPEC_SURVEY_01 / SPEC_COMPARISON_TABLE_DRAFT_01 / G8_GAS_KASU_INVESTIGATION_01 / JA_OFFLINE_COMPARISON_01 / JA_EXCEPTION_CLASSIFICATION_DRAFT_01 / ja_offline_replay_01.json)、er056_ja_scg_offline_replay_01.py。

## 主要な発見(確定)
- g8のPrimary NG直接原因は「熟->じく」(読み欠落)で、SCGが除外されたのは同一発話内の「ガ->カ」がentity_like(カタカナ率ヒューリスティック)と判定されたため(SEC L200-201)。単独のガス/カスは旧Cascade経由でAzure確認される。C1は旧承認(SPEC L1998 entity-likeはSecondaryへ)と逆向きで、ユーザー個別承認の逐語なし。
- 除外を外してもPhase 0 C群の誤PASSは0/5(CURRENT/NO_C1/HARD_ONLY/ALL全て)。濁点誤りを含む実標本は0で、濁点でAzureが原稿語へ丸めるリスクは未測定。
- 日本語のminimal fallback(3回目)はrole style(J3)を渡さずstyle不連続。履歴の成功率36.8%(19中7、選択バイアスあり)。
- 気付いた新規仕様候補(未承認・実装なし): 否定の活用ギャップ(来なかった)、C1の挿入/脱落取りこぼし(メタ->メタン)。
- 追加Trial案(未実行): 濁点最小対40クリップ約9〜10円、HR実segmentへのSCG再計算約3〜8円。
