# FABLE_EVAL_01 — FX-PARAGRAPH-CHUNK-TTS-TRIAL-01 Fable独立評価(2026-10-25、委任_02成果、API 0)
- 客観面: 全Gate PASS(ASR一致・Repetition QA)、HR Lock 0、条件差異chunk 0、mp3 22本の公開確認、Production store/承認済み音声/公開ページのsha256不変、Opus条件A必須修正M1〜M4反映済み。
- 速度: 実発話が約7%遅い(A→B_r1 全長+10.1秒のうち発話区間+7.7秒、段落境界gap+2.6秒。B0は+6.6秒で境界gapはAと同等)。段落10対×4組すべて同方向・art300同方向のため断定可。見かけの減速ではない。
- 接続・音量: 境界音量差はB最大5.8dB(承認済みAのpart境界7.8〜8.3dBより小)、peak頭打ち0、語欠け・二重なし。
- 音質改善・声質の一貫性(過去P6B不合格理由)は機械指標で代替せず、ユーザー試聴で判断。
- 費用: Trial実費13.89円/上限50円。採用時Advanced本文あたり約+0.30円(+7.5%)、所要+約6秒。
- Status(Fable): USER_DECISION_REQUIRED(試聴判断)。VALIDATED/REJECTEDはユーザー試聴後に確定。Production採用は含まない。
- 推奨: 声質の一貫性に違和感がなければB0(追加ポーズなし)を採用方向で設計(ポーズ構造をAと同等に保ったまま実発話の減速を得られ、コスト増が小さい)。違和感があれば不採用。採用時は配線設計→Opus条件C→ユーザー承認。
- 限界: 標本A 2take/B 2take、word timestamp精度限界、mtime走査が並行agentの書込みで誤検知(実害なし)。
