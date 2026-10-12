# COST LEDGER: Family Z Melos (FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01)

作成: 2026-10-12(委任_11)。課金0で作成(既存cost_log.jsonlの再集計のみ)。
集計元: `er026_output/family_z_production_e2e_01/melos/run_e2e_01/cost_log.jsonl`(479行)を
`er019_family_x_audio_production_runner_01.compute_cost_jpy_so_far`(pricing_snapshot単価、160JPY/USD)で再計算。
`cost_log.jsonl`自体にJPY列は無い(別途OPEN起票)。集計結果: `evidence_11/cost_aggregate_run_e2e_01.json`。
予算: 本E2E追加API費用の上限 JPY300、警告 JPY200(2026-10-12ユーザー決定)。

## 1. run_e2e_01 累計(旧仕様run、2026-10-12)

| 項目 | JPY | 備考 |
|---|---|---|
| 累計 | 108.11 | e2e_stage_log最終 spent_jpy_cumulative=108.1056 と一致 |
| provider別 | openai 38.73 / gemini 37.00 / openai_asr 6.65 / azure 25.73 | |

### stage別(JPY、call数)
| stage | JPY | calls | 内訳 |
|---|---|---|---|
| writer(R0/R1/R2) | 7.30 | 3 | openai gpt-6.1-sol |
| validate_b1b | 0.21 | 1 | openai(原作保持Validator。撤廃) |
| std_adjust | 23.04 | 1 | openai gpt-6.1-sol(266秒、1回) |
| validate_a2 | 0.18 | 1 | openai(同上。撤廃) |
| plan | 0.51 | 6 | 分割選択+話者判定(luna) |
| support | 0.84 | 10 | Preview/Comment(Comment3再生成含む) |
| kp | 4.22 | 14 | KP(Strategy L、外側retry含む) |
| tts_a2 (Std) | 22.20 | 193 | gemini 14.38(77) / azure 4.89(7) / asr 2.83(95) / openai(LR等) 0.10(14) |
| tts_b1b (Adv) | 49.60 | 250 | gemini 22.62(105) / azure 20.84(24) / asr 3.81(108) / openai(LR等) 2.32(13) |

### 旧仕様で無効となった分(2026-10-12のユーザー仕様修正により再利用不可)
- **TTS(委任_10の再起動で重複生成された分を含む): 約 JPY71.8**(tts_a2 22.20 + tts_b1b 49.60)。
  うち、再起動により同一clipを再生成した重複分(Gemini TTSの重複call 100件)は約 JPY20.3
  (tts_a2 7.93 + tts_b1b 12.41。純粋な無駄)。初回生成相当分は約 JPY51.5。
  TTS進捗は a2 25/41 segment+KP、b1b 36/40 segment+KP(約60%、完走していない)。
- 文章系(writer/std_adjust/plan/support/kp)約 JPY36.1 と、Validator呼出 約 JPY0.39(`validate_b1b` 0.21 + `validate_a2` 0.18)は
  原稿語数目標(280-420)の変更により原稿自体が再生成対象となるため、全て無効扱い(再利用しない)。
- 別枠: 委任_04Aのer061 calibration実呼出 約 JPY4(run_e2e_01のcost_logには含まれない。委任文の記載値)。Validatorは撤廃のため無効。
- 結論: run_e2e_01の累計 JPY108.1(+別枠 約4)は**全額sunk cost(再利用不可)**。以降の再生成費用は予算 JPY300 の残枠から出る。

### 事故との関係
委任_10のagentがSTOP NOTICE(ユーザー仕様変更)を知らずに監視killを障害と誤認し、監督ループ(sup.sh)・別名ラッパで旧仕様TTSを再起動し続けた結果、
36.3(kp完了時点)→108.1 の約 JPY72 が追加支出された。詳細: `docs/pm/delegation_log/2026-10-12_FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01_STOP_NOTICE.md`、`..._10.md`、`PM_GOVERNANCE.md` 26節(再発防止)。

## 2. 新仕様での再生成見積(run_e2e_02想定、すべて**見積**。実行は委任_12以降・ユーザーの予算判断後)

前提: 原稿は Adv/Std とも 約350語(280-420)。Validator stage廃止(0円)。Std段落不一致は再生成せずWARN+独自分割。
KP外側retry(最大3)・TTS clip checkpoint(中断時の再課金防止)は維持。モデルは run_e2e_01 と同一(writer=gpt-6.1-sol、他=gpt-6-luna、TTS=gemini-3.8-flash-lite-tts系、ASR=gpt-4o-mini-transcribe、Secondary=Azure)。

### 2-1. 文章系(旧実測を新語数比で補正)
| stage | 旧実測 JPY | 新見積 JPY | 根拠 |
|---|---|---|---|
| writer(R0-R2) | 7.30 | 5-7 | 出力語数 約480→約350(推論token主体のため比例しきらない) |
| std_adjust | 23.04 | 17-23 | 1call。推論token主体で語数比例は弱い。**自動再生成なし**(段落不一致でも1回のみ) |
| plan | 0.51 | 0.5 | 同等 |
| support | 0.84 | 0.8-1.2 | Comment3再生成が入る場合は上限 |
| kp | 4.22 | 2.5-4.5 | 外側retryが最大3回まで走る場合は上限 |
| validate | 0.39 | **0** | stage撤廃 |
| **文章系 計** | 36.1 | **約 26-36(中央30)** | |

### 2-2. TTS(Adv+Std 両レベル、ASR Primary/Azure Secondary含む)
旧初回生成相当分は 82 segmentで 約51.5(≒0.63/segment、うちAzure Secondary約25.7が大きい)。
新仕様の全segment数は、Story clip数が約25%減り、固定clip(Preview/Comment/KP/intro等)を合わせて 約190 segment(Adv+Std)と見る。

| シナリオ | TTS 見積 JPY | 前提 |
|---|---|---|
| 仮定A(LR/cool-downなし、再起動なし) | 約 55-70 | 初回生成のみ。Azure Secondaryの呼出頻度は旧と同程度 |
| 仮定B(旧同様にLocal Rewrite発火+cool-down) | 約 75-95 | LR発火(旧: b1bで2件)、再TTS、Azure Secondary増、Human Review Lock再実行分を含む |

### 2-3. 合計と予算
| シナリオ | 再生成合計 JPY | run_e2e_01累計 108.1 を含めた総額 | JPY200警告 | JPY300上限 |
|---|---|---|---|---|
| A(文章中央30 + TTS 55-70) | 約 85-100 | 約 193-208 | **到達境界(TTS後半で到達)** | 余裕あり |
| B(文章36 + TTS 75-95) | 約 111-131 | 約 219-239 | **到達する(TTS中盤〜後半)** | 余裕あり(約60-80残) |

### 2-4. JPY200警告到達の見込みと注意
- **新規run(run_e2e_02)単体の費用が約85-131**になる見込み。これに旧run累計108.1(sunk)を足すと、警告閾値 JPY200 に**確実に近づく/到達する**。
- **重要な運用リスク**: er026 のBudget guardは `<run>/cost_log.jsonl`(run単位)の累計しか見ない。run_e2e_02 は新規dirのため、
  guard上の累計は0から始まり、旧run分108.1を含まない。何もしなければ「run単体で200まで進める」ことになり、E2E全体ではJPY300上限(108.1+新規)を超過し得る
  (仮定B+再試行が重なると 108+200=308)。委任_12では次のいずれかを要確認(Fable/ユーザー判断): ①`--approved-budget-jpy`を残枠(300-108.1≒191)に下げて実行する、②`--warn-threshold-jpy`を90前後にして警告=旧run含め200とする、
  ③旧累計を含む機構を別途実装する(今回は実装せず。OPEN起票)。上記①が追加実装なしで最も安全。
- 予算判断の目安: 見積A/Bのいずれも JPY300 上限には収まるが、不具合による再試行(特にTTS再起動)が1回でも入ると JPY200超過の可能性が高い。
  再試行は委任文で回数を明示許可した範囲のみ(PM_GOVERNANCE 26節)。

## 3. run_e2e_02 開始前(委任_12B, 2026-10-12)
- 開始前累計 JPY108.1(run_e2e_01)。approved-budget 191.9 / warn 92。Z Style表キーにP8なしをdry-runで確認(Coffee P8非適用)。
- 停止時点(17:54 JST、rc=2、tts_b1bでSTOP): run_e2e_02 実費 JPY39.32 (openai 23.11 / gemini 9.28 / asr 1.42 / azure 5.52)。合算 147.4 / 300。LR/cool-down発火なし(未確認分あり)。再起動なし。

## 4. 委任_12D(2026-10-12): Comment3再生成 + tts_a2
- run_e2e_02 実費合計(cost_log集計, compute_cost_jpy_so_far): **JPY61.08**(openai 23.25 / gemini 22.33 / openai_asr 4.81 / azure 10.69)。12B停止時39.32 -> +21.76(Comment3再生成の小額 + tts_a2)。
- 合算(run_e2e_01 108.1 + run_e2e_02 61.08)= **約169.2 / 300**。警告92(run単体)未到達、200未到達。tts_a2はrc=2(clip失敗STOP)、起動1回(Comment3再生成の`--stage support`起動は別)。
- 残stageを最後まで実行した場合の追加見込みは小額(gate/assemble/pages/page_verifyはAPIなし)。HR clipの再生成を承認する場合は1 clipあたり約JPY1-2、Std cooldown(10分)あり。

## 5. 委任_03(FAMILY-Z-MELOS-PROPER-NOUN-ASR-ROOT-CAUSE-01、2026-10-12)
- 反例ASR(Phrase List誘導型、TTSなし): **約JPY3.71**(Azure 3.45 / OpenAI ASR 0.25、`asr_root_cause_01/reeval_cost_log.jsonl`の75行目以降。見積JPY1を超過)。
- 正規QA再生成(part1_c1 + part3_c3、起動1回): run_e2e_02 実費 61.08 -> **62.00**(+JPY0.92、各1回生成)。
- Opus任意改善: JPY0。
- 累計(Melos E2E): run_e2e_01 108.11 + run_e2e_02 62.00 + 再評価(委任_01 約11 + 本委任 3.71) = **約184.8 / 300**。警告92(run単体)未到達、残枠 約115。
