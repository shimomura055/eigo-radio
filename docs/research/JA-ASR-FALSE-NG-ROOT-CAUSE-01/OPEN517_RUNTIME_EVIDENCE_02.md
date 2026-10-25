# OPEN517_RUNTIME_EVIDENCE_02(OPEN-517 F1+F2 Family別 正式runtime証拠の更新。JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_10、2026-10-25)
事実と推測を分ける。Statusの語は**Fable受入判定の転記**(Zは委任_09時点で受入済み、Xは本書の証拠に基づく同基準の適用をFableが指示済み)。基準commit: 07A `5e50613f5`=21:56:35 / R-5 `58cbf7786`=22:36:33 / 本run時HEAD `fb768a357`(22:48:41、5e50613f5の子孫を確認済)。
## 1. 3行表
| Family | run dir | 起動時刻 | commit後か | final_gate適用 | r5.f1 | r5.f2(enabled/fired) | 523/524 | DEMOTE | NG化 | model_id | HR Lock | 事実ベースStatus候補 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **X** | `er078_output/open517_runtime_evidence_01/x_one_clip_01/a2`(自分の1 clip。X正式経路=er019 `_generate_or_reuse`+`n3_tts.generate_a2_japanese_with_reading_safety`[backend=speech_metadata_flash_lite・style=FAMILY_X_ROLE_STYLE_JA・secondary_run_scope・er109 family_scope("X")]) | 22:54:11(pid 20036、HEAD=fb768a357) | はい(5e50613f5より32分後、58cbf7786より18分後) | `applied=True`・`value_guard=NO_VALUES`・`reason_code=primary_pass`。**primary.equivalence_basis=READING_MATCH(label=PHONETIC_MATCH、原稿『分かりました』と読点↔転写『わかりました』・読点なし。値は無しでNO_VALUES)が基底承認に使われず最終Gate評価を受けた** | `reading_match_primary_pass=true`・`final_gate_rejected=false`・`demoted_p3=false`・rollback定数=true | **enabled=true / fired=false**(置換対象なし) | 0/0 | 0 | 0 | Primary `openai_asr/gpt-4o-mini-transcribe`(cost_log locale ja)+TTS `gemini-3.8-flash-lite-tts`。Secondary不呼出(`secondary.called=false`) | なし(PASS 1 attempt) | Zと同基準を満たす: **PRODUCTION_WIRED(Fable受入2026-10-25)** |
| **Z** | `er078_output/open517_runtime_evidence_01/z_one_clip_02/a2`(委任_09。内容は`OPEN517_RUNTIME_EVIDENCE_01.md`) | 22:37:53 | はい | `applied=True`、comment_3=READING_MATCHで最終Gate評価 | `reading_match_primary_pass=true`・rejected=false | enabled=true / fired=false | 0/0 | 0 | 0 | 同上 | なし | PRODUCTION_WIRED(Fable受入2026-10-25) |
| **Y** | `er121_output/family_y_production_01/*`(並行agent B。読取専用) | JA判定のcommit後artifactなし | — | 旧コード(`final_gate.applied=False`)のみ | — | — | — | — | — | — | — | コード配線完了(`er121_family_y_audio_01.py:530,540`が同じ`generate_a2_japanese_with_reading_safety`)・runtime未確認(委任_06 E-1で回収) |
## 2. Xの既存artifact(並行agent A・読取専用)の確認結果
- `part2_hr_evidence_01__run_r1/a2` japanese_title(JA wav 22:30:35、5e50613f5の後=F1/F2コード下、R-5は未commit作業ツリー): `final_gate.applied=True`・`r5` あり。ただし`primary.label=NORMALIZED_MATCH`(表層一致)で**READING_MATCHではなく**、`f2.enabled=false`。よってREADING_MATCH最終Gateの証拠には使えない(経路通過のみ)。同run他のJA segmentは21:17〜21:46生成(commit前)で`r5`なし。
- `part2_hr_evidence_01__run_r2/a2` comment_2/3/4・KP meaning_1/2: READING_MATCHに`final_gate.applied=True`あり(F1下の評価)だが、起動が5e50613f5より前でR-5前。採用せず(委任_09の整理どおり)。
- commit後の他のX JA判定artifactは確認できなかった(er019/er026/er062/er119/er120配下で21:56:35以降に更新された`tts_generation_results`はrun_r1/r2とY dirのみ)。このため(ii)の1 clip実run(下記)で補った。
## 3. 有料run(自分)
- 1 clip(`ja_asr_ev_x_comment_3`。X part2_hr_evidence_01 run_r2の comment_3 と同一原稿)。スクリプト=`docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/open517_x_one_clip_evidence_01.py`。実費=**0.531円**(cost_log集計、上限5円)。起動前: stop_scope_check rc=0(`x_one_clip_01/stop_check_10.json`)、`daily_dev_cost_01.py`表示1,231.49円+94.28円+上限5円=1,330.77円<1,480円。起動は1回のみ(間隔規則は該当せず。rc=0、再起動なし)。
- 補足(事実): 1 attemptでPASS。リトライ0、HR Lock入りなし、`approved_by="user"`付与なし。wav/raw_usage_log/lockは追跡しない。
## 4. tally(`open517_first_run_tally_01.py`。集計出力=`x_one_clip_01/tally_x.json`・`../tally_z_10.json`)
| 対象 | attempts | READING_MATCH | F1 NG化(a) | DEMOTE(b) | HR Lock(c) | F2 fired(d) | r5 f2 enabled | 523/524(e) | alert |
|---|---|---|---|---|---|---|---|---|---|
| X(x_one_clip_01) | 1 | 1 | 0 | 0 | 0 | 0 | 1 | 0/0 | false |
| Z(z_one_clip_02+z_one_clip) | 4 | 1 | 0 | 0 | 0 | 0 | 1 | 0/0 | false |
## 5. 限界(推測と区別)
- 事実: X・ZともF1最終Gate(READING_MATCHにも値ガード適用)とF2経路通過(enabled=true)が正式runtimeで確認できた。F1 NG化・DEMOTE・F2 fired・523/524の**実事例は正式runtimeで0件**(API 0評価でのみ確認)。サンプルはREADING_MATCH合計2件と小さい。
- 運用: 以後の正式runごとに`open517_first_run_tally_01.py`で監視。DEMOTEが1runで3件超ならFableへ即報告(rollback定数=`er078_asr_unified_judge_01.READING_MATCH_FINAL_GATE`)。
