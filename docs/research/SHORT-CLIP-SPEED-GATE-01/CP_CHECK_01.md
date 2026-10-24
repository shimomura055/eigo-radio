# CP_CHECK_01 (SHORT-CLIP-SPEED-GATE-01 委任_01、2026-10-24) X/Y/Zの速度処理・Gate所在の現状確認

ユーザー正式採用(APPROVED_FOR_PRODUCTION、UDR #181: 原音1.5秒未満=長さ比0.90〜1.00、1.5秒以上=0.93〜0.96、1.5秒ちょうど=従来)。原文=docs/pm/delegation_log/2026-10-24_SHORT-CLIP-SPEED-GATE-01_USER.md。

| Family | 速度処理 | 『wav/原音の長さ比』Gate | 判定 |
|---|---|---|---|
| Z | Adv会話=生成後atempo 1.06高速化(`z_speed_v2`、`er063_family_z_audio_01.py` `speed_profile_name`)、Std会話=処理なし、Std Narrator=6%減速 | `verify_z_speed_profile`(er063:1560)の Adv会話 `ADV_DIALOGUE_RATIO_MIN/MAX`(0.93/0.96)。呼出=`run_audio_gate`(er063:1658)のみ。`run_audio_gate`の呼出=Z runner gate stage(`er026_family_z_fiction_production_runner_01.py:1821`)と runtime evidence script(`er078_auw_runtime_evidence_06b.py:323`) | **適用対象(実装済)** |
| X | 会話clipなし(ニュース記事)。Std英語segmentのみ6%減速(`n3_tts.generate_a2_segment_with_slowdown`) | 同等のGateなし。共有assemble(`er003_v1_n3_01_assemble.py:235`)にあるのは『Std 6%減速の証跡有無』判定の比1.03〜1.09(減速=比>1、別目的・別仕様)。Adv会話高速化の比Gateは存在しない | **対象Gateなし(適用不要)** |
| Y | DEV/Trial専用。音声TrialはXの共有narration/segment経路を呼ぶ(`er110_family_y_audio_trial_01.py:33,373`)。Z `z_speed_v2`の会話高速化・`verify_z_speed_profile`は呼ばない | 比Gateなし。Y正式Production入口は未存在(`y_entry_point.json` production_reachable=False、OPEN-484) | **対象Gateなし(適用不要)・Y Production未実装** |

結論: 本Gateが存在するのはFamily Zのみ。共通処理は`adv_dialogue_ratio_range(original_seconds)`1関数(er063)。X/Yは同等Gate自体が無いためPRODUCTION_WIREDとは呼ばない(対象外として記録)。将来Y/Xが会話高速化v2を採用する場合は同関数を使う旨をOPEN-484へ記録。
