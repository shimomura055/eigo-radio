# VERIFY_01 — ユーザー原文§3/§4 検証(根拠=evidence_01.json、BUILD_01、EVIDENCE_01)
| # | 項目 | 結果 | 根拠 |
|---|---|---|---|
| 1 | Voice 1 actual voice=Puck | PASS | a2/b1b `voice`=`y_tts_voice_requested`=Puck、`voice_assignment.json` voice_1=Puck(run_01はAlgieba)。cost_log TTS呼出5行(model gemini-3.8-flash-lite-tts、STANDARD) |
| 2 | 現行TTSモデル/Style/速度/Retry | PASS | model/backend/`style_version=v3_j3_kp_meaning_and_explanation_guard`=現行。Std 6%減速(比1.0597)。各attempt=1(retry/fallback未発火) |
| 3 | ASR/発音/内容一致/Repetition | PASS | ASR PASS(Std 数値等価、Adv EXACT)、Repetition QA flagged=False、pronunciation alarm 0、y_style_profile_gate PASS、共有Audio Validation Gate PASS(assemble到達) |
| 4 | 長ポーズ | 文中>=1.0秒=0 | Std y_voice_1に文境界1.09秒が1回(max 1090 ms)、Adv 0(max 860 ms)。EVIDENCE_01 |
| 5 | 速度/音量/peak | PASS | Std減速8本、peak 0.866/0.867 clipping無し |
| 6 | Adv Comment 2完全除外 | PASS | Adv timeline 43要素・`comment_2` 0件、`support_texts.json` 0件、ページAdv節 0件、mp3 adv_00〜23+full(Comment 2音声参照なし)。`parts.json`/`final_manifest.json`の`comment_2`は`removed_by_spec`の除外記録(Std側の`support_segments.a2`のComment 2は維持)。旧comment_2.wavはdisk残置だが未使用 |
| 7 | 前後の接続 | PASS | 順序 Intro, Notification 1-3, Comment 1, Full Story(Lead/Voice 1-3+導入), Comment 3, Closing。timeline隙間/重なり a2/b1b とも0(evidence_01.json `*_timeline_gaps=[]`)。Std 47要素・Comment 2維持 |
| 8 | KP/解説/HR確定内容の一致 | PASS | text/translate/support/key_phrases/study_text/kp_review_modeがrun_01とsha一致。KP/Vocab/文法Part 2は人間確定ではなく`UNREVIEWED_AUTO_ADOPTED`のまま前回公開版と同一内容を再利用(a2 preview承認のみ人間確定の再利用) |
| 9 | 旧Voice/Comment 2が復活しない | PASS | `er121_family_y_audio_01.py:191-214 voice_guard_cached`(Voice不一致entryを破棄)、`:185 removed_by_spec`、同引数再起動(L2)でAPI 0・Voice 1 wav sha不変・旧Algieba cache非使用。run_01はAlgieba、ev runはPuck |
| 10 | 他segment再利用 | PASS | 67本sha不変、変更は3 wav(Voice 1とStd原音)のみ |
| 11 | 公開ページ整合 | PASS | 全audio参照52件存在、未参照mp3 0、`v1cand`/`Algieba`/`listening/` 0、通し再生(main_standard/main_advanced)・パート別・確定スクリプト・KP/解説(Key Phrase記載11)掲載、page_verify ok |
| 12 | URL到達 | PASS | `https://shimomura055.github.io/eigo-radio/user_test/family_y_production_redelivery_fee_02/index.html` HTTP 200(push後約2分、404が約2.5分続いた後に反映)。std_full/adv_full/std_18/adv_16/adv_23/std_25 mp3 HTTP 200。旧`_01`も200(保持) |
未実施: 実際の耳による試聴・ブラウザ実再生(ユーザー最終試聴待ち)。
