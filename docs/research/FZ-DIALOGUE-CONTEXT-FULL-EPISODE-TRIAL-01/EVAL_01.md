# EVAL_01 — 全編通しTrial 機械評価(FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01 委任_04、2026-10-26 JST)

性質: 解析のみ(API 0・TTS 0)。事前登録は `PREREGISTERED_CRITERIA_01.md` + `_02.md`(§6の観測後改訂1件を含む)をそのまま適用。**機械評価はユーザー試聴の代替ではない**(到達上限=Status候補+ユーザー試聴待ち)。
出典: `er118_output/fz_full_episode_trial_01/{analysis_all.json,<work>/<level>/{analysis.json,assemble_result.json}}`、`noise_band_r2.json`(sha256 `f720991856bd547c6a9387b12835360fbba2f220bee15cadea1fc1ef8c9adbd3`、更新なし)。
試聴ページ: https://shimomura055.github.io/eigo-radio/user_test/fz_full_episode_trial_01/index.html (noindex。4単位すべて掲載。メロスStdには比較条件注記とNG箇所の「現行音声」明示)。

## 1. C1〜C7(作品×レベル)

| 条件 | 猿の手 Std | 猿の手 Adv | メロス Std | メロス Adv |
|---|---|---|---|---|
| C1 NG件数(≤2で記録付き成立) | 0 | 0 | **1**(part3_c10) | 0 |
| C2 Production ASR PASS系+repetition QA(採用clip) | 15/15 | 17/17 | 9/9 | 11/11 |
| C3 leakage_final.flagged / any_attempt | 0 / 0 | 0 / 0 | 0 / 0(NG clipは転写が正解文でleakage無) | 0 / 0 |
| C4 comparison_valid(採用clip) | 成立 | 成立 | 成立(NG clipはNG数に計上) | 成立 |
| C5(i) 組立自己検証(生成前) | 成立 | 成立 | 成立 | 成立 |
| C5(ii) M-5 | 成立(scalar 1.0=1.0) | 記録付き成立(−0.030 dB、M-5(3)改訂) | **不成立**(−0.158 dB、条件(iii)超過0.058 dB) | 成立(scalar 0.96345082完全一致) |
| C5(iii) 通しpeak≤0.99 | 0.9531 | 0.9799 | 0.9799 | 0.9799 |
| C6 `run_audio_gate` shared_gate | PASS | PASS | PASS | PASS |
| C7 隔離(Z run/page全ファイル不変・store汚染0・mtime Z hit 0・isolation) | 成立 | 成立 | 成立 | 成立 |
| 通しの長さ Trial / 現行 | 307.9s / 301.8s | 298.6s / 291.2s | 305.5s / 301.9s | 295.3s / 293.1s |

- C2のProduction ASR判定は最終status OK=全PASS系。観測値`token_equal=false`: 猿の手Std part2_c4(類似度0.857)、猿の手Adv part2_c6(0.833)、猿の手Adv part3_c3 "Herbert!"(0.0、`PASS_WITH_WARNING`)。Productionが合格とする判定のためblockingにしない(M-7)が、**試聴で確認すべき箇所**。
- C6: 猿の手Stdの`audio_text_deviation_clips=[full_story_part1_c10]`はセリフ外clip(Trial不介在、Production同一音声)。
- C7生成後再確認(委任_04): Z run dir(`run_sf_prod_01`/`run_e2e_06`)・公開page(`family_z_monkeys_paw_01`/`family_z_melos_02`)の`git status`差分は、`family_z_melos_02`の未追跡3項目(10/22作成の既存ファイル。本Trial起因でない)のみ。委任_04開始以降のmtimeでZ production hit 0。

## 2. Status候補(事前登録02 §3写像、単位別)

| 単位 | 機械状態 | Status候補 |
|---|---|---|
| 猿の手 Std | C5〜C7成立・NG0・保留0 | **PHASE1B_DONE_USER_LISTENING_PENDING** |
| 猿の手 Adv | C5(ii)は改訂M-5(3)の記録付き成立・NG0・保留0 | **PHASE1B_DONE_USER_LISTENING_PENDING**(M-5(3)改訂適用) |
| メロス Std | **C5(ii)不成立**(NG1は閾値内) | **REJECTED候補(比較条件不成立)** |
| メロス Adv | C5〜C7成立・NG0・保留0 | **PHASE1B_DONE_USER_LISTENING_PENDING** |

**メロスStdの性質**: 方式の品質欠陥ではなく、比較条件ガードの不成立。原因clip part3_c4(同一本文)のctx生成takeは24k→48k変換後peakが0.998(Production 0.958)で、Production安全弁(閾値0.98・全編一律scalar)が**Trialでのみ**作動し、Trial全体が−0.158 dB(0.9819)になる。非dialogue clipの相対音量・gain・target_rmsは不変。聴感上の影響は小さいと見込まれるが、**事前登録を再改訂しない**(Fable案B)ためREJECTED候補とし、4単位すべてをユーザー試聴に提示する。機械Statusは「ユーザー判断待ち」を覆さない(VALIDATEDとは言わない)。

## 3. N指標(両側全件併記。自然ゆれ目安=`noise_band_r2.json`)

自然ゆれ(Round 1/2 24ペア |ln比|): 話速 中央値0.159/90%点0.255、F0中央値 0.115/0.315、F0幅 0.234/0.496、RMS 0.160/0.276、長さ 0.051/0.200、最大ポーズ 0.126/0.598。

### N1 話者内ばらつき(Trial側 / Production側。`unstable_speaker`は補助)
| 単位 | 話者(n) | 話速CV T/P | F0中央値SD(半音) T/P | unstable |
|---|---|---|---|---|
| 猿の手Std | morris(4) | 0.187 / 0.127 | 2.66 / 2.69 | - |
| | mr_white(5) | 0.177 / 0.290 | 4.00 / 4.41 | - |
| | mrs_white(3) | 0.302 / 0.331 | 1.68 / 1.14 | - |
| 猿の手Adv | morris(5) | 0.173 / 0.300 | 3.79 / 4.77 | - |
| | mr_white(5) | 0.270 / 0.329 | **6.78 / 3.85** | - |
| | mrs_white(3) | 0.494 / 0.385 | 3.04 / 1.11 | **要試聴** |
| | visitor(3) | 0.150 / 0.172 | 0.82 / 0.74 | - |
| メロスStd | king(3) | 0.021 / 0.082 | 0.88 / 2.43 | - |
| | melos(5) | 0.170 / 0.234 | 4.95 / 4.39 | - |
| メロスAdv | king(4) | 0.086 / 0.173 | 3.87 / 5.17 | - |
| | melos(5) | 0.155 / 0.310 | 5.77 / 4.74 | - |

読み: 話速CVは11話者中9でTrial側が小さい(増は猿の手Std morris 0.187 vs 0.127、猿の手Adv mrs_white 0.494 vs 0.385の2件)。F0 SDは猿の手Adv mr_white(6.78 vs 3.85)・mrs_white(3.04 vs 1.11)・メロスAdv melos(5.77 vs 4.74)で大きい=感情で動く想定内だが「同一人物の演技の一貫性」の試聴注目点。話者あたり3〜5 clipのためCV比は偶然で動きやすい。

### N2 速度・長ポーズ(Trial側にのみ出た/範囲外のclip全件)
| clip | 単位 | 内容 |
|---|---|---|
| part2_c8 mr_white "You didn't see him, and I'm afraid of what might return." | 猿の手Std | 新規長ポーズ0.83s(現行0.35s)、長さ3.90→6.12s(1.57倍)、話速186→125wpm。needs_listen |
| part2_c11 mrs_white "He's our son!" | 猿の手Adv | 話速124→70wpm(0.56倍、0.6倍未満)、長さ1.45→2.57s。needs_listen |
| part3_c4 melos "I almost left you to die," | メロスStd | 新規長ポーズ0.73s(現行0)、長さ2.34→4.13s(1.76倍)。**同clipが上記peak原因clip**。needs_listen |
メロスAdv: N2フラグ0件。

### N3 地の文→セリフの境界段差(Trial−Production > +3 dB の境界 / 全境界、adoptedのみ)
猿の手Std 4/26、猿の手Adv 6/30、メロスStd 2/20、メロスAdv 8/22(計20/98)。最大差: メロスStd part3_c8 step_out +9.64 dB、猿の手Adv part1_c11 step_in +6.0 dB、メロスAdv part3_c10 +5.4/+5.3 dB。全一覧は`<work>/<level>/analysis.json` の `N3.rows[*].*.over_3db`。**「地の文→セリフの切替」の試聴注目点**(段差が大きい箇所は上記N3表の clip)。

### N4 感情あり/なし別 |ln比|中央値(感情ACCEPTED群 / NO_EXPLICIT_CUE群)
- 猿の手Std: 話速0.160/0.149、F0中央値0.051/0.113、F0幅0.255/0.236、RMS 0.200/0.037(n=10/5)
- 猿の手Adv: 話速0.089/0.214、F0中央値0.225/0.139、F0幅0.091/**0.838**、RMS 0.157/0.168(n=9/8)
- メロスStd: 感情あり全10(なし群n=0)、メロスAdv: 話速0.082/0.068、F0中央値0.159/0.340、F0幅0.521/0.366、RMS 0.225/0.187(n=5/6)
- 事前予測「感情ありのほうが大きい」は**一貫せず**(RMS・F0幅で一部のみ成立、猿の手Advでは感情なし群のF0幅が最大)。効果の有無は試聴が決める。

### N5 初回成功率・再生成・k_ctx(`raw_usage_log.jsonl`基準)
| 単位 | clip | TTS call | k_ctx | 初回OK | 再生成/NG |
|---|---|---|---|---|---|
| 猿の手Std | 15 | 15 | 1.000 | 15 | 0 |
| 猿の手Adv | 17 | 17 | 1.000 | 17 | 0 |
| メロスStd | 10 | 13 | 1.300 | 8 | part1_c8=2 call(Production ASR cascadeの内部2試行目でPASS)、part3_c10=3 call→NG |
| メロスAdv | 11 | 11 | 1.000 | 11 | 0 |
| 計 | 53 | 56 | **1.057** | **51/53(96.2%)** | NG1・内部retry成功1・Trialレベルの再生成0 |
(委任文の「初回OK52・NG1」は実測と1差。実測=初回OK51、内部2試行目でOK 1、NG 1。Production実績k_prod=1.019、Round 2 base arm実測k=1.083(26call/24clip)。)

### N6 時間
生成wall: 猿の手Std 138.7s / Adv 149.6s / メロスStd 122.8s / Adv 104.8s、合計515.9s(clipあたり平均9.7s=9.25/8.80/12.28/9.53)。起動間隔≥150秒の運用待機は除く。組立+解析+ページ(API 0)は1単位あたり数十秒〜1分。

## 4. 費用(R-6、実測)・70円/set評価

- **実Trial支出(Phase 1b)25.581円/100円**: TTS 24.158(56 call、0.431円/call)、ASR openai 1.283、Azure 0.140。clipあたり0.483円。Phase 0(感情LLM)は別途1.011円。
- **量産想定Δ/set**(感情情報LLM 2 call=0.27円込み、ASR増分込み、Δ=ctx方式−現行base方式):
  | 作品 | k_prod=1.019版 | Round 2 base k=1.083版 | 70円に対する比 |
  |---|---|---|---|
  | 猿の手 | +2.57円 | +1.80円 | 2.6〜3.7% |
  | メロス | +3.26円 | +2.74円 | 3.9〜4.7% |
  → **幅 +1.8〜+3.3円/set(70円比 2.6〜4.7%)**。主因はctx style付与によるTTS call単価上昇(+約0.08円/call)で、k_ctxの寄与は小さい。
- **70円/set維持可否**: 現行Z set単価が70円ちょうどなら71.8〜73.3円となり**70円は維持できない(超過+1.8〜3.3円)**。現行単価に同額以上の余裕があれば維持可能。現行Z単価はTrial対象外のため本評価は未確認。
- **感情情報レビューの自動化費用は未計上(要設計)**: 現状Fableによる感情情報acceptレビューを0円と見なしていない。自動化する場合の追加費用は含まれていない。
- 単位あたり時間(量産想定): 感情情報LLM 1 call 12〜26秒、ctx生成は clip直列で単位あたり105〜150秒(現行base生成との差は未計測)。

## 5. 開示

### 観測後改訂(1件): M-5(3)
`PREREGISTERED_CRITERIA_02.md` §6参照(commit 131294298、メロス生成前)。改訂時点で**観測済み**: 猿の手Std/Advの生成・採用判定(32/32初回OK)、猿の手Stdの組立と機械指標、猿の手Advの組立でのscalar不一致(−0.030 dB)。**未観測**: メロス生成・組立・猿の手Advの機械指標・ユーザー試聴。改訂条件(iii)(0.1 dB以内)はメロスStdで0.058 dB超過し、**2回目の改訂は行わず**事前登録どおりC5(ii)不成立とした。

### 解析実装上の補正(1件・Statusに影響なし)
委任_03の実装は`C4_all_comparison_valid`を全clipで評価しており、NG clip(comparison_valid=false)がC4不成立としてStatus判定に二重計上される。事前登録02 §3は「`n_ng`の定義にcomparison_valid==falseを含め、NG件数閾値で判断」とするため、Status判定用に`C4_adopted_comparison_valid`(採用clipのみ)を追加した(全clip版`C4_all_comparison_valid`も残して報告)。メロスStdの最終Status(REJECTED候補)は不変。観測後の実装解釈であることを開示する。

### 交絡
1. ヘッドルーム係数差2件: 猿の手Adv −0.030 dB(Trial part2_c10 peak 0.9834 vs Prod 0.9505)、メロスStd −0.158 dB(Trial part3_c4 0.998 vs Prod 0.958)。いずれも全編一律・相対音量不変。
2. NG 1件(メロスStd part3_c10 king/Charon "How can a man win such trust?"): ASR転写は3試行とも正解文だがProduction ASR cascadeで不合格(C1/C2/C4)。通し版は**Production原音**を置換。ページに「現行音声」を明示。
3. Std会話へのctx付与は今回が初(Round 1/2はAdvのみ)。Advは速度後ASR再検証を含む(Round 2より厳格)ため、再生成率の直接比較は不可。
4. メロスの`full_story_part1_c4`(両レベル)はProduction側が前run再利用で、再利用元の生成時入力が現行と同一である保証がない(DESIGN_02 R-3)。
5. 通し全体の秒数・各セリフの開始時刻はTrialでセリフ長が変わるためずれる。

## 6. ユーザー試聴の論点(機械で代替しない)
§4 A/Bの全項目。特に **⑥同一人物の演技の一貫性**(猿の手Adv mr_white/mrs_white、メロスAdv melos)、**④地の文→セリフの切替**(N3上位: メロスStd part3_c8、猿の手Adv part1_c11、メロスAdv part3_c10 ほか)、**⑧不自然な速度変化・長ポーズ**(猿の手Std part2_c8、猿の手Adv part2_c11、メロスStd part3_c4)、C2観測値の読み違い疑い(猿の手Std part2_c4、猿の手Adv part2_c6・part3_c3)。メロスStdは比較条件(全体−0.16 dB)に留意して聴く。

## 7. 機械評価と試聴評価の区別
本書のC/N指標は「条件成立・分布・外れ値・安定性の観測」であり、セリフの感情適合・没入感・自然さの改善は**判定していない**。VALIDATED(限定)/REJECTEDの最終判断はユーザー通し試聴後。

## 8. Fable評価欄
(空欄 — Fableが独立評価を記入)
