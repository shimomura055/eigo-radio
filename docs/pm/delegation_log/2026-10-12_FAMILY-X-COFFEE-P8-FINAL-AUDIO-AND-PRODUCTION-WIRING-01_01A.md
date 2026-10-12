# FAMILY-X-COFFEE-P8-FINAL-AUDIO-AND-PRODUCTION-WIRING-01 委任_01A 報告 (2026-10-12)
状態: v4作成・公開・Playwright実再生PASS(再生成立のみ)。音声品質はユーザー試聴待ち。Trial隔離、PRODUCTION_WIRED/APPROVED表記なし、SSOT未編集。
試聴: https://shimomura055.github.io/eigo-radio/user_test/coffee_final_v4/ (standard/ , advanced/ あり)
生成: Full Story 6本(Std3/Adv3)全て attempt1 でPrimary ASR採択(Secondary/HR未発生、再生成0)。gemini-3.8-flash-lite-tts / Aoede / P8 sha 3eadf4f6f788... / canonical原稿sha v3一致。
 std1 NORMALIZED_MATCH, std2 NUMERIC_EQUIVALENCE_MATCH, std3 NUMERIC_EQUIVALENCE_MATCH, adv1 NORMALIZED_MATCH, adv2 NORMALIZED_MATCH, adv3 HIGH_SIMILARITY_SAFE。Std 6%減速 ratio 約1.0596。
 注: 「既存A2減速指示」はv3実装(PD8逐語+生成後6%減速、追加句なし)に合わせP8逐語+6%減速とした。
速度(Full Story合計、v4/v3): Std 全体162.2/166.0 WPM(-2.3%)、発話177.0/190.5(-7.1%)、Part別 145.5/171.0/168.6。Adv 全体180.7/183.2(-1.4%)、発話190.0/193.6(-1.9%)、Part別 166.9/192.2/180.8。通し尺 Std 317.683s(v3 314.172)、Adv 317.07s(v3 314.97)。
Gate: peak Std 0.9572 / Adv 0.98(headroom valve発動、原因=再利用KP5 peak0.9846、scalar0.9953)、clipping 0、wav=timeline=mp3長一致、減速比OK。変更roleはFull Story 3件/Levelのみ(他27/26 role sha不変)。検知器 medium/high 0件(両Level)。
異音3件: 同箇所の検知なし(Adv P1/P3)、Std P2は同付近にspec_jump low 1件(33.6s、要聴感)。再生成せず。詳細 KNOWN_ANOMALY_COMPARE_V4.md。
実費: JPY9.48(上限30)、Azure 0。Coffee累計 約JPY133.9(未集計項目除く)。請求画面未確認。
残リスク: Std発話WPMがv3比-7.1%で遅い(P8の効果とPart2/3の間差)。KP5由来のAdv headroom valve。Std Part2 33.6s spec_jump low。聴感は未確認。
証跡: er057_output/coffee_final_v4/ (BUILD_PLAN_V4, STYLE_APPLICATION_EVIDENCE_V4, PRODUCTION_DIFF_V4, MEASUREMENTS_V4, PLAY_EVIDENCE_V4_01, COST_LEDGER_COFFEE_01)
raw: https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er057_output/coffee_final_v4/STYLE_APPLICATION_EVIDENCE_V4.md
