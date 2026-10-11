# FAMILY-X-COFFEE-FINAL-LISTENING-TONE-TRIAL-01 委任_04(2026-10-12、Advanced KP英語へのK2適用)
範囲: Advanced Key Phrase英語5件へのK2適用・Advanced最終試聴版再組立・ページ更新・OPEN-280解消。Trial限定、Production/Master Store/manifest/telemetry/CURRENT_SPEC変更なし、共通Styleは`APPROVED_FOR_PRODUCTION`ではない。詳細証跡: `er057_output/coffee_final_listening_tone_trial_01/part_final/`(`*_04`)。

1. 何が問題だったか: 委任_03でAdvancedのKey Phrase(lag/price tag/show up/come down/come with)がStandardと異なるためK2音声が未生成で、Advanced KP英語だけ旧Styleのままだった(OPEN-280)。
2. 何を変更したか: (a) Standard K2と同一Prompt(prompts_B.md K2逐語、style sha先頭12=9d905cfe6c04、Standard分と一致)・model `gemini-3.8-flash-lite-tts`(応答model_version実測=同名)・Voice Aoede・speech_metadata方式でKP英語5件を各1回生成(全件初回合格、retry 0)。(b) 委任_03 assemblerを無改変で使いAdvanced完成版を再組立(KP5 roleのみ差替え、他24 roleのsha不変)。(c) `final_v2/`の一覧・Advanced単独ページとAdvanced mp3・KP区間mp3を更新(Standardは音声不変、説明文のみ共通文言を更新)。(d) OPEN-280 CLOSE、DECISION_LOG追記、REPORT_LEDGER更新。
3. 何が改善されるか: ユーザー指示「Key Phrases: K2・M2」がStandard/Advanced両方の試聴版に反映された。
4. リスク・注意: 新規low候補1件(Advanced KP2内3.06秒 spec_jump)は試聴確認要。共通Styleは未承認のまま(Production採用は人間のみ)。K2の効果はAdvanced日本語意味(M2)がなく英語解説のため、Advanced KP block全体の聴感は要試聴。

## 結果
- 実費: 約JPY0.15(概算0.3。5 call、prompt 14tok/candidates 152tok、`cost_actual_04.json`)。Trial累計 約JPY23.45(委任_03時点約23.3+今回)。請求画面は未確認。
- QA(`qa_04.json`): Advanced 288.45秒、peak 0.95935(<=0.98)、clipping 0、headroom安全弁未発動、wav/timeline/mp3長一致、内部1秒超の無音はKP4の1.02秒のみ。
- 異音再検知(`ANOMALY_RECHECK_04.md`、閾値不変): 新K2 5件=候補0。Advanced完成版=新規medium以上0、新規low 1(KP2内3.06秒)。自動検知のみで再生成せず。
- assembler回帰: 委任_03の`regression_check_03.json`(既存音声のみ組立=既存完成版byte-identical)を再利用(assembler不変)。
- 公開: commit d1973d45(静的ファイルのみ)、Pages 200、Playwright実再生 52/52・27/27・25/25、Gate 7 (a)〜(n) PASS(`PLAY_EVIDENCE_04_final_v2.md`)。
- Production不変: Master Store manifest/reuse_telemetry/human_review_queue/attempt_history/telemetry各種/ledgerのsha256が前後一致(`production_sha_before_04.txt`/`production_sha_after_04.txt`)。CURRENT_SPEC差分なし。
- 試聴URL(一覧): https://shimomura055.github.io/eigo-radio/user_test/coffee_tone_trial_01/final_v2/index.html / Advanced: https://shimomura055.github.io/eigo-radio/user_test/coffee_tone_trial_01/final_v2/advanced/index.html

## 成果物
`er057_tone_trial_final_kp_adv_04.py`(生成)、`er057_tone_trial_final_build_04.py`(組立/QA)、`er057_tone_trial_final_recheck_04.py`、`er057_tone_trial_final_page_04.py`、`part_final/`{`kp_adv_k2/`、`final_04/`、`generation_log_04.jsonl`、`cost_actual_04.json`、`assembly_manifest_04_final.json`、`qa_04.json`、`anomaly_recheck_04.json`、`adv_provenance_diff_04.json`、`STYLE_APPLICATION_EVIDENCE_04.md`、`SEGMENT_PROVENANCE_04.md`、`ANOMALY_RECHECK_04.md`、`PLAY_EVIDENCE_04_final_v2.md`、`pages_play_evidence_04.json`、`play_verify_04.py`、`production_sha_*_04.txt`}。
