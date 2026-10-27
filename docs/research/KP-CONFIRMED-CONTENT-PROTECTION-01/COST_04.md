# COST_04(委任_04、Z Standard KCP evidence)
- runner台帳(`melos/run_kcp4_ev_z_01` の spent): コピー時 5.6802 → 最終 8.3515 = **+JPY 2.6713**(内訳: L3 kp/Part2候補+Redundancy QA 約0.35[5.6802→6.0321]、L5 KP音声5clip再生成+ASR 約0.65[6.0321→6.6793]、L6 `full_story_part2_c1` 2chunk再生成 約1.67[6.6793→8.3515]、L4/L7=0)。
- 別途: `grammar-pregen`(b1b Step B 1件。CLI記載約0.3円/件。runner台帳には載らない)≒JPY 0.3。
- 合計 約JPY 3.0。Cap JPY 30 の約10%。案件見積300円以下かつ承認済みScope内(7-7)。日次1,000円は他agent分含め超過見込みなし。
- 見込み(≤¥5)に対し、KP音声のみは約0.65。part2_c1再生成(+1.67)は旧run単一clip→Std chunk planner差分によるもので、KCP起因ではない。
