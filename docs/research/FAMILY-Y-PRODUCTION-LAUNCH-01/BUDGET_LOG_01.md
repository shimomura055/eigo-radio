# BUDGET_LOG_01: Family Y Production立上げ 実費記録(委任_03、2026-10-25 JST)

管理ID: FAMILY-Y-PRODUCTION-LAUNCH-01。Cap **170円**(Fable自律枠、7-7。BUDGET_PLAN_03/04)。実費の出典=各runの`cost_log.jsonl`をrunnerと同じ関数(`er019_family_x_audio_production_runner_01.compute_cost_jpy_so_far`、`pricing_snapshot.json`)で換算(`cost_by_stage.json`)。

## 1. 累計

| 区分 | 実費(円) | 備考 |
|---|---|---|
| 02A(M-1較正5.97+M-2書換えevidence 8.38) | 14.347 | 既支出 |
| 02B/02C | 0 | API 0 |
| 03 Part A(結線・test) | 0 | API 0・偽client・socket遮断 |
| 03 E-3(SNS年齢制限、`sns_age_limit/run_01`) | **82.7182** | 完走 |
| 03 E-1(宅配案B、`redelivery_fee/run_01`) | **32.0715** | a2でHR Lock、未完走 |
| **Y立上げ累計** | **129.137** | Cap 170円に対し残 **40.863円**。超過なし |

本日(JST)の開発費累計(`docs/pm/tools/daily_dev_cost_01.py`、E-3/E-1完了後)=1,153.29円+ツール未捕捉(er110 Round 2)94.28円=**1,247.57円**/日次1,500円(超過なし。他案件の並行消費を含む)。

## 2. E-3(SNS、82.7182円)stage別

| stage | 円 | 内訳 |
|---|---|---|
| text | 59.0809 | Voice生成(Sol high×3)12.97、UNMAPPED再生成(Sol×3)14.92、Closing生成(Sol high×1、reasoning約10,876tok、268秒)21.99、人物紹介(Sol×2)4.79、Lead(Sol×1)2.61、出典付番(luna×9)1.53、構造タグ0.09、Voice/Closing/Lead紹介Gate(luna)約0.33 |
| translate | 0.6433 | luna×2 |
| support | 0.3415 | luna×8 |
| kp(候補生成+gloss+確定後) | 3.35 | luna(候補生成〜Redundancy QA、gloss整合) |
| tts_b1b | 8.5980 | Gemini TTS 20 + ASR |
| tts_a2 | 10.7040 | Gemini TTS 21 + ASR + azure fallback |

## 3. E-1(宅配、32.0715円)stage別
text 0.117(Lead+紹介補助判定1+案B判定1、luna)/ translate 0.47 / support 0.42 / kp 2.81 / tts_b1b 10.88(925秒)/ tts_a2 17.37(939秒、`preview`と`y_voice_1`が上限3回消費後にHR Lock)。launch3(Lock確認の再起動)は新規API 0・追加費用0。

## 4. 予算ガード・見積との差
- 見積(BUDGET_PLAN_03/04): E-1 27〜39、E-3 69〜93(通常Y記事)。実測: E-3 82.7円(範囲内)、E-1 32.1円(Lockまで。完走していれば35円前後の想定)。
- 警告閾値(run単位100円)に未到達。ガードによるSTOPなし。
- **量産単価**: 通常Y記事の実測原価82.7円(目標70円に対し+12.7円)。主因: UNMAPPED再生成3/3(14.92円)とClosing生成(21.99円)。削減余地の評価は品質判断を伴うため本委任では実施せず(EVIDENCE_01 §5-2)。
- 為替・単価: `pricing_snapshot.json`(2026-08-17取得)。cached_tokens割引・flex/Batchの可否は今回も未確認(cost_logのcached_input_tokens=0)。
