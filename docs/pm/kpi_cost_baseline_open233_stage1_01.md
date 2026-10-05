# KPI Cost基準点(iii)の書面固定(OPEN-233 Stage 1 ループ2、委任_11、Trial前、¥0)

管理ID OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01。根拠: Opus#17 §6(`opus_l2_review_open233_stage1_loop2_17.md`)、Fable評価4(`design_open233_stage1_loop2_01.md` §9)。**本書は有料Trial(委任_12)の実行前に固定する。Trialの結果を見て基準点を動かさない。** 基準点は実質KPI定義のため、ユーザー確認事項(最終報告に掲載)。Fableは保守側(iii)で進める。`APPROVED_FOR_PRODUCTION`ではない。

## 1. 定義(iii)
追加費用 = 「新Stage 1フローを配線した後のProduction 1記事の総費用」 − 「現行Production 1記事の総費用」。同じ記事種別・同じ構成で比べる。
- 差し引いてよい部品: 配線計画上、新フローにより**実際に取り除かれると示せる部品**のみ。具体的には現行の英語Stage 1(V4A Ledger逸脱check)の実費。
- 差し引いてはいけないもの: JA検査の費用、モデル世代差(gpt-5.6-luna→gpt-6-luna)による削減。これらを本設計の手柄にしない。

## 2. 差し引き可否の根拠
- 現行Stage 1(vfl01 `run_deviation_check`、V4A prompt)は新Stage 1(3'-R+5-lite/5-V)が置換する(Trial設計の前提、Stage 2は不変)。
- (ii)の2.77(`agg_production_baseline_cost_01.py`)は、stage名に"check"/"must_fix"を含むcallの合算で、実体はJA原稿の検査(`ja_original_check`等)、モデルはgpt-5.6-luna(単価がgpt-6-lunaの約2倍)、meta run_03が重複行(実質n=7)。英語Ledger逸脱検査の置換対象ではない。→使わない。
- V4A実費の既存usage集計(`er052_output/open233_kpi_recovery_02_offline_01/agg_v4a_stage1_actual_cost_01.{py,json,md}`): **Production 1記事分としては特定不能**。参考としてTrial/回帰runのdeviation系stageはgpt-5.6-lunaで¥0.25〜1.98(n=1〜6)、gpt-6-luna単価換算で¥0.12〜0.84。確定値でないため、(iii)の計算では「0.12〜0.55」の範囲を仮置きし、推定であることを明記する。実費の確定は、Production配線前のE2Eで現行側usageを同一run内で取得して行う。

## 3. (i)(ii)(iii)の対応表
| 基準点 | 追加費用の定義 | 採否 |
|---|---|---|
| (i) rep24基準 | 新Stage 1+Stage 2費用 − rep24基準0.44 | 参考(旧ループ1判定の基準) |
| (ii) 2.77 | 総費用 − (check+must_fixの合算2.77) | 不採用(JA検査・モデル世代・重複行が混在) |
| (iii) | 新フロー配線後Production − 現行Production、差し引きはV4A実費のみ | **採用(Trial前固定)** |

換算式(Opus#17 §6、推測): (iii) = (i) + 0.24 − V4A実費。0.24はrep24基準への換算分(Opus値、再検証していない)。

## 4. 見込みの再計算(NORMAL、rep30単価。委任_10の数値の流用、**推測**)
Stage 1+Stage 2負荷。S0はループ2設計書§4のrep24 add。別案1はOpus#17 §9の「Stage 1 ¥2.04→1.1〜1.4(r3 medium+r5-V medium/low、つまりG適用込み)」と(B)案aの−0.41を適用。V=0.12〜0.55。

| 構成 | (i) 追加 | (iii) 追加(V=0.55〜0.12) | +¥2判定 |
|---|---|---|---|
| S0 現行 | +4.18 | +3.87〜+4.30 | 未達 |
| 別案1(G適用込み) | +2.83〜+3.13 | +2.52〜+3.25 | 未達(境界より上)見込み |
| 別案1でG不成立(high) | 算出根拠なし | - | 未算出(r5-Vのhighでの費用は未測定) |

見込みは未実測で、Trial(委任_12)で置き換える。KPI +2に届かない見込みなら、Opus#17 §7の通り、G・r5-Vを試し切った後に構造的両立不能の判定(iii基準で+¥2超)を行う。
