# COST_01 — 委任_03 runtime evidenceの費用・単価影響・制作時間差分

管理ID: TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_03 / 作成: 2026-10-27 00:48 JST

## 1. 実費(raw_usage_logの`compute_cost_jpy_so_far`集計。全run dir合算)

| 区分 | 実費(円) |
|---|---|
| 採用case(最終evidence)の合計 | 73.62 |
| superseded/中断/smokeのrun(driver不備・自然逸脱・LR不成立の再実行分) | 12.98 |
| **委任_03の総実費** | **86.6** |
| 個別Cap(¥280)に対して | 30.9% |

Family別(採用/全体): X=29.02/36.97、Y=32.17/34.25、Z=12.44/15.39。
provider別(全体): {"openai": 9.37, "gemini": 42.8, "openai_asr": 8.62, "azure": 25.92}。
BUDGET_PLAN §3のLean保守見積200.2円/天井297.8円に対し、実費は上記。日次1,000円(JST)に対し本委任は86.6円で、他の並行作業分を含めても¥950以内の見込み(他agentの同日支出は本agentからは未確認)。**暴走(同一原因の連続再実行)なし**。再実行はすべて原因を特定した上で1回ずつ(§3)。

## 2. case別実費(採用evidence。E-S6は再起動後の累計)

| case | 実費(円) | provider内訳(円) |
|---|---|---|
| X-Adv-1 | 0.759 | {"openai": 0.04, "gemini": 0.4, "openai_asr": 0.08, "azure": 0.24} |
| X-Adv-2 | 1.304 | {"openai": 0.44, "gemini": 0.53, "openai_asr": 0.1, "azure": 0.24} |
| X-Adv-3c | 2.021 | {"openai": 0.59, "gemini": 0.8, "openai_asr": 0.16, "azure": 0.47} |
| X-Adv-4 | 0.973 | {"openai": 0.03, "gemini": 0.4, "openai_asr": 0.08, "azure": 0.46} |
| X-Adv-6 | 1.789 | {"openai": 0.31, "gemini": 0.81, "openai_asr": 0.17, "azure": 0.5} |
| X-Adv-7 | 0.684 | {"gemini": 0.38, "openai_asr": 0.1, "azure": 0.21} |
| X-Adv-8 | 0.695 | {"gemini": 0.37, "openai_asr": 0.1, "azure": 0.23} |
| X-Adv-9 | 0.413 | {"gemini": 0.33, "openai_asr": 0.09} |
| X-Adv-10 | 0.324 | {"gemini": 0.1, "openai_asr": 0.05, "azure": 0.18} |
| X-Adv-11 | 0.414 | {"gemini": 0.13, "openai_asr": 0.06, "azure": 0.22} |
| X-Adv-12 | 0.746 | {"openai": 0.04, "gemini": 0.38, "openai_asr": 0.08, "azure": 0.25} |
| X-Adv-13 | 0.36 | {"openai": 0.03, "gemini": 0.27, "openai_asr": 0.05} |
| X-Adv-14 | 1.607 | {"openai": 0.04, "gemini": 0.89, "openai_asr": 0.18, "azure": 0.5} |
| X-Adv-14b | 1.672 | {"openai": 0.04, "gemini": 0.91, "openai_asr": 0.18, "azure": 0.54} |
| X-Adv-15 | 0.343 | {"openai": 0.04, "gemini": 0.26, "openai_asr": 0.05} |
| X-Adv-16 | 1.851 | {"openai": 0.32, "gemini": 0.84, "openai_asr": 0.17, "azure": 0.51} |
| X-Std-1 | 0.767 | {"openai": 0.03, "gemini": 0.4, "openai_asr": 0.08, "azure": 0.25} |
| X-Std-1b | 0.471 | {"openai": 0.03, "gemini": 0.25, "openai_asr": 0.04, "azure": 0.15} |
| X-Std-2 | 1.142 | {"openai": 0.3, "gemini": 0.51, "openai_asr": 0.1, "azure": 0.23} |
| X-Std-3 | 2.203 | {"openai": 0.54, "gemini": 0.79, "openai_asr": 0.15, "azure": 0.72} |
| X-Std-4 | 0.804 | {"openai": 0.04, "gemini": 0.42, "openai_asr": 0.11, "azure": 0.23} |
| X-Std-5 | 1.868 | {"openai": 0.33, "gemini": 0.84, "openai_asr": 0.2, "azure": 0.5} |
| X-Std-6 | 0.238 | {"openai": 0.03, "gemini": 0.17, "openai_asr": 0.04} |
| X-Std-7 | 0.237 | {"openai": 0.03, "gemini": 0.16, "openai_asr": 0.04} |
| X-Std-8 | 0.393 | {"gemini": 0.12, "openai_asr": 0.05, "azure": 0.22} |
| X-Std-9 | 0.523 | {"gemini": 0.17, "openai_asr": 0.07, "azure": 0.29} |
| X-Std-10 | 0.744 | {"openai": 0.03, "gemini": 0.4, "openai_asr": 0.08, "azure": 0.24} |
| X-Std-11 | 0.265 | {"openai": 0.03, "gemini": 0.19, "openai_asr": 0.04} |
| X-Std-12 | 1.175 | {"openai": 0.03, "gemini": 0.81, "openai_asr": 0.33} |
| Y-Adv-1 | 1.152 | {"openai": 0.48, "gemini": 0.41, "openai_asr": 0.08, "azure": 0.19} |
| Y-Adv-2 | 0.409 | {"gemini": 0.22, "openai_asr": 0.07, "azure": 0.12} |
| Y-Adv-3 | 0.411 | {"gemini": 0.13, "openai_asr": 0.05, "azure": 0.23} |
| Y-Adv-4 | 7.058 | {"openai": 0.37, "gemini": 2.76, "openai_asr": 0.6, "azure": 3.34} |
| Y-Adv-4b | 8.558 | {"openai": 0.44, "gemini": 3.8, "openai_asr": 0.8, "azure": 3.52} |
| Y-Adv-5 | 0.282 | {"openai": 0.03, "gemini": 0.22, "openai_asr": 0.04} |
| Y-Std-1 | 1.323 | {"openai": 0.22, "gemini": 0.62, "openai_asr": 0.11, "azure": 0.37} |
| Y-Std-2 | 0.325 | {"openai": 0.04, "gemini": 0.16, "openai_asr": 0.04, "azure": 0.09} |
| Y-Std-2b | 0.494 | {"openai": 0.05, "gemini": 0.18, "openai_asr": 0.04, "azure": 0.23} |
| Y-Std-3 | 0.318 | {"gemini": 0.1, "openai_asr": 0.05, "azure": 0.17} |
| Y-Std-4 | 4.827 | {"openai": 0.02, "gemini": 2.65, "openai_asr": 0.55, "azure": 1.6} |
| Y-Std-4b | 6.539 | {"openai": 0.02, "gemini": 2.64, "openai_asr": 0.74, "azure": 3.13} |
| Y-Std-5 | 0.218 | {"openai": 0.03, "gemini": 0.16, "openai_asr": 0.03} |
| Y-Std-6 | 0.255 | {"openai": 0.03, "gemini": 0.2, "openai_asr": 0.04} |
| Z-Adv-1 | 1.065 | {"openai": 0.26, "gemini": 0.45, "openai_asr": 0.09, "azure": 0.27} |
| Z-Adv-2 | 1.22 | {"openai": 0.03, "gemini": 1.13, "openai_asr": 0.07} |
| Z-Adv-3 | 1.282 | {"openai": 0.03, "gemini": 1.21, "openai_asr": 0.04} |
| Z-Adv-3b | 1.512 | {"openai": 0.03, "gemini": 1.39, "openai_asr": 0.09} |
| Z-Adv-4 | 0.633 | {"openai": 0.18, "gemini": 0.29, "openai_asr": 0.05, "azure": 0.11} |
| Z-Adv-5 | 0.464 | {"gemini": 0.24, "openai_asr": 0.07, "azure": 0.15} |
| Z-Adv-6 | 0.452 | {"gemini": 0.14, "openai_asr": 0.06, "azure": 0.25} |
| Z-Adv-8 | 0.218 | {"openai": 0.01, "gemini": 0.17, "openai_asr": 0.03} |
| Z-Std-1 | 2.499 | {"openai": 0.55, "gemini": 1.09, "openai_asr": 0.22, "azure": 0.64} |
| Z-Std-2 | 1.513 | {"openai": 0.2, "gemini": 1.27, "openai_asr": 0.05} |
| Z-Std-4 | 0.199 | {"gemini": 0.11, "openai_asr": 0.02, "azure": 0.07} |
| Z-Std-5 | 0.377 | {"gemini": 0.12, "openai_asr": 0.05, "azure": 0.21} |
| Z-Std-6 | 0.702 | {"openai": 0.2, "gemini": 0.3, "openai_asr": 0.06, "azure": 0.14} |
| Z-Std-7 | 0.133 | {"openai": 0.01, "gemini": 0.11, "openai_asr": 0.02} |
| Z-Std-8 | 0.169 | {"openai": 0.01, "gemini": 0.14, "openai_asr": 0.03} |

## 3. superseded / 中断 / smoke のrun dir(費用は上記総額に計上済み)

| Family | run dir | 区分 | 実費(円) |
|---|---|---|---|
| X | `coffee_prices__run_tru_ev_aborted2_x_adv_3` | superseded/中断/smoke | 0.344 |
| X | `coffee_prices__run_tru_ev_aborted2_x_std_3` | superseded/中断/smoke | 0.355 |
| X | `coffee_prices__run_tru_ev_smoke1_x_std_1` | superseded/中断/smoke | 0.743 |
| X | `coffee_prices__run_tru_ev_superseded_x_adv_10` | superseded/中断/smoke | 0.0 |
| X | `coffee_prices__run_tru_ev_superseded_x_adv_11` | superseded/中断/smoke | 0.0 |
| X | `coffee_prices__run_tru_ev_superseded_x_adv_7` | superseded/中断/smoke | 0.0 |
| X | `coffee_prices__run_tru_ev_superseded_x_adv_8` | superseded/中断/smoke | 0.0 |
| X | `coffee_prices__run_tru_ev_superseded_x_std_1` | superseded/中断/smoke | 1.001 |
| X | `coffee_prices__run_tru_ev_superseded_x_std_2` | superseded/中断/smoke | 1.157 |
| X | `coffee_prices__superseded2_tru_ev_x_adv_10` | superseded/中断/smoke | 0.292 |
| X | `coffee_prices__superseded2_tru_ev_x_adv_11` | superseded/中断/smoke | 0.403 |
| X | `coffee_prices__superseded2_tru_ev_x_adv_7` | superseded/中断/smoke | 0.715 |
| X | `coffee_prices__superseded2_tru_ev_x_adv_8` | superseded/中断/smoke | 0.691 |
| X | `coffee_prices__superseded2_tru_ev_x_std_8` | superseded/中断/smoke | 0.526 |
| X | `coffee_prices__superseded2_tru_ev_x_std_9` | superseded/中断/smoke | 0.508 |
| X | `coffee_prices__superseded_tru_ev_x_adv_16` | superseded/中断/smoke | 1.214 |
| X | `coffee_prices__superseded_tru_ev_x_std_8` | superseded/中断/smoke | 0.0 |
| X | `coffee_prices__superseded_tru_ev_x_std_9` | superseded/中断/smoke | 0.0 |
| Y | `run_tru_ev_aborted1_y_adv_1` | superseded/中断/smoke | 0.278 |
| Y | `run_tru_ev_aborted1_y_std_1` | superseded/中断/smoke | 0.251 |
| Y | `run_tru_ev_aborted2_y_adv_3` | superseded/中断/smoke | 0.29 |
| Y | `run_tru_ev_aborted2_y_std_1` | superseded/中断/smoke | 1.257 |
| Z | `run_tru_ev_aborted2_z_adv_2` | superseded/中断/smoke | 1.076 |
| Z | `run_tru_ev_aborted2_z_std_5` | superseded/中断/smoke | 0.238 |
| Z | `run_tru_ev_superseded_z_adv_2` | superseded/中断/smoke | 1.569 |
| Z | `run_tru_ev_superseded_z_std_2` | superseded/中断/smoke | 0.029 |
| Z | `run_tru_ev_superseded_z_std_4` | superseded/中断/smoke | 0.039 |

再実行の理由: (1) driver不備(KP caseのno-op label不一致・KP style_profile記録欠落・Z ctx slot意味・JA wrapper引数・Z clip id・LR置換語[先頭語`Listen`でLR候補QA不合格]) (2) Y generator decorator位置ずれ(Production軽微欠陥の是正、Y全case再実走) (3) 自然逸脱(③が実ASRでNG)の再実行(X-Std-1b/X-Adv-14b/Y-Std-2b/Y-Std-4b/Y-Adv-4b)。

## 4. 量産単価(70円/記事セット)への影響の実測更新

実測の限界費用(強制NG条件下の平均。評価・注入の費用を含む上限寄りの値):
- **1 attempt(TTS+ASR[openai+azure])**: 約 ¥0.353(全採用caseのTTS 184回、gemini ¥35.44+openai_asr ¥7.22+azure ¥22.21)。
- **LR 1回(gpt-6-luna、識別+書換え+QA等のLLM呼出の合計)**: 約 ¥0.282/回(LR実行19回、openai計 ¥5.36)。LR後のTTS最大3回は上記attempt単価。

BUDGET_PLAN §4の推定「+0〜1円/セット」の更新: 回数が増える箇所は**LRあり部位でLR発動かつ①'NG時の最大+2 attempt**のみ(約¥0.71/件)。発動頻度は本evidenceでは強制NGのため測定不可(BUDGET_PLAN §4の実績頻度[③到達 約1〜2%、JA 6.9%]を使うと、記事あたり ≒ ¥0.1〜0.5 程度で、**+1円/セット未満の推定は維持**)。LRなし部位(JA・KP・KP解説・Z会話)は試行回数が不変(3回/KPは4回)で、待機が増えるだけで費用は増えない(実測: X-Std-6/X-Adv-1/Z-Std-2のTTS=3)。

## 5. 制作時間差分(実測)

- 実180秒待機: 51回、最小179.972秒〜最大180.000秒(`cooldown_core`の実`sleep`)。旧(1ブロック600秒)に対し**−420秒/ブロック**(英語LR部位)。日本語・KP・KP解説・Z legacy・Z冒頭英語は**新規に+180秒/イベント**(③到達時のみ)。
- case別wall time(採用evidence):

| シナリオ | case数 | 平均秒 | 最小 | 最大 |
|---|---|---|---|---|
| E-C1 | 1 | 39 | 39 | 39 |
| E-N | 6 | 13 | 8 | 25 |
| E-S0 | 1 | 21 | 21 | 21 |
| E-S1 | 17 | 212 | 190 | 318 |
| E-S2a | 7 | 269 | 218 | 369 |
| E-S2b | 7 | 447 | 421 | 481 |
| E-S3 | 4 | 204 | 194 | 223 |
| E-S4 | 8 | 200 | 192 | 218 |
| E-S7 | 1 | 212 | 212 | 212 |
| E-STOP | 2 | 54 | 51 | 56 |
| E-X5 | 1 | 19 | 19 | 19 |

E-N(正常系)は平均約13秒=**待機・追加生成なし**。E-S1(③到達)は約200秒=180秒待機+TTS/ASR。E-S2b(LR+2待機)は約450秒(旧は最低でも600秒×2に近い待機が必要)。
