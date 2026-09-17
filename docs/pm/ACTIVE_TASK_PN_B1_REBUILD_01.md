# ACTIVE_TASK: USER-TEST-PERSONALIZED-NEWS-B1-REBUILD-01-FIX-01

管理ID: USER-TEST-PERSONALIZED-NEWS-B1-REBUILD-01-FIX-01(ユーザー試聴Feedback修正)
親管理ID: USER-TEST-PERSONALIZED-NEWS-B1-REBUILD-01(GATE_PASS→USER_DECISION_REQUIRED到達済み)
Status: IN_PROGRESS
Lock: docs/pm/locks/audio_stage.lock 取得済み(2026-09-17T12:32:18Z)
最終報告: docs/pm/RESULT_PACKET_PN_B1_REBUILD_01.md(累積更新、末尾「## FIX-01」節)
Budget cap: 本管理ID累計上限¥500(既使用¥361.22、残≈¥139、本FIX-01での追加分に注意)
到達目標Status: GATE_PASS → USER_DECISION_REQUIRED(USER_TEST_READYにしない)

## 工程チェックリスト
- [x] T-0 delegation log + check
- [x] lock取得
- [x] 事前指定Read一式(RESULT_PACKET/audio.py/article.md/parts.json/
      tts_generation_results.json/audio_validation.json/er008_disfluency_qa_18.py/
      er003_v1_n3_01_assemble.py/user_test_page_e2e_check.py/PM_GOVERNANCE 9-12・Gate7(n))
- [ ] canonical article.md(r8_attempt1)へ1.Hook/2.Voice A heading/3.Voice A本文削除を適用
- [ ] 人物整合(Hook→Voice A→Voice B)確認、manual wording adjustmentの要否判断
- [ ] grep証跡: 旧文言/旧代名詞の残存なし(Voice Bの"her feed"は維持)
- [ ] Analytical Leakage Check 2V(7項目)offline再実行
- [ ] Ledger Deviation Checker offline再実行(Writer再生成なし、MAJOR 0件を確認)
- [ ] Comment/Preview旧文言引用なし確認(再生成不要の想定)
- [ ] 全14segment+Key Phrase音声(EN/JA)をaudio/b1_2v_fix01/で再生成
      (Production primitive、er012_personalized_news_b1_rebuild_01_audio.py)
- [ ] QA: local faster-whisper verbatim transcribe(er008_disfluency_qa_18)
- [ ] QA: 波形解析(click/pop/無音/境界RMS急変/音量揺れ、audit_fix01/audio_qa.json)
- [ ] 重点確認A-E(do not want接続部/Sometimes接続/he has/his/Erinome女性維持)
- [ ] Assembly/Gate再実行(duration/peak/clipping/Audio Validation Gate)
- [ ] player.html確認
- [ ] Browser E2E(user_test_page_e2e_check.py 5項目+seek+error=null+script一致+layout)
- [ ] A2 sha256 before/after diff確認(無変更証跡)
- [ ] SSOT反映: DECISION_LOG(FIX-01エントリ+予算¥500更新)/ARTIFACT_REGISTRY/
      RESULT_PACKET累積更新
- [ ] Dangling Reference Check
- [ ] Git commit/push(明示add、git add -A禁止、wav禁止、mp3可)
- [ ] lock解除
- [ ] 到達Status確認: GATE_PASS→USER_DECISION_REQUIRED(USER_TEST_READYにしない)

## STOP条件(再掲)
Script修正に新Product判断要/Voice A・B立場変更要/Ledger claim変更要/
全TTS再生成後も複数箇所で異音・切断残存/voice変更要/A2影響不可避/
新blocking issue/予算¥500超過見込み/git conflict。
