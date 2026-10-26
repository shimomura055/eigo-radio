# COST_01 — Phase 2 実費(2026-10-26、委任_03)

計測=各run dirの`cost_log.jsonl`を`er019.compute_cost_jpy_so_far`で集計(`evidence_01.json`の`cost_jpy_from_cost_log`)。強制NG由来の費用は量産単価ではなく**開発費**に計上。

| E | run | 実費(円) | TTS呼出(gemini-2.5-pro-preview-tts) | 備考 |
|---|---|---|---|---|
| E-1 | run_fzcw_e1_01(Std+Adv) | 28.17 | 22(dialogue 21+自然retry 1) + flash-lite 56(非dialogue) | ASR openai 102/azure 26+1、gpt-6-luna 6 call(notes 2+他4) |
| E-2 | run_fzcw_e2_a2_01 | 1.89 | 3 | |
| E-2 | run_fzcw_e2_b1b_01 | 1.85 | 3 | |
| E-3 | run_fzcw_e3_a2_01 | 1.95 | 3(kill前2+再開後1) | |
| E-4 | run_fzcw_e4_a2_01 | 1.88 | 3(4回目なし) | |
| E-4 | run_fzcw_e4_b1b_01 | 1.91 | 3(4回目なし) | |
| E-5 | run_fzcw_e5_a2_01 | 1.27 | 2(kill前1+再開後1) | |
| E-6 | run_fzcw_e6_b1b_01 | 1.39 | 2 | |
| 合計 | | **40.31** | | 見積 期待約49/保守62/天井80、Guardrail 200に対し約20% |

課金前に落ちた起動(猿の手のseed provenance不一致、Part1/Part2/keywords不足、driver bug)は**API 0・JPY 0**(cost_log行なし。`kp_part1_b1b`再生成も`FamilyZProvenanceMismatchStop`で実行前に停止)。

## E-1の量産単価換算(15-8「Production 1生成セット総原価」のZ行)

15-8標準表にZ行は未定義。本評価はE-1の**TTS区分(区分: tts_b1b+tts_a2)のみ**を実測し、text区分(writer/std_adjust/plan/support/kp)は実行していない(melosは既存text資産copy)。したがって総原価の置換は推定である。

| 項目 | 現行(ctx前) | E-1(ctx後) | 差 |
|---|---|---|---|
| 猿の手 run_sf_prod_01 全体(e2e_stage_log) | ¥46.82(writer 11.23 / std_adjust 8.14 / plan 0.42 / support 0.44 / kp 1.41 / tts_b1b 11.78+0.16 / tts_a2 13.24) | — | — |
| melos TTS区分(同一text・legacy方式) `run_p2_evidence_r3` | tts_b1b 12.76 + tts_a2 14.82 = **27.58** | `run_fzcw_e1_01` 合計 **28.17**(うちnotes LLM 0.27[Std 0.119+Adv 0.149]) | **+0.59(+2.1%)** |

- 増分の内訳(推定): notes LLM +0.27、自然retry 1回(a2 part3_c10)のdialogue TTS+ASR約+0.3〜0.5(run間の自然分散を含む)。同一textの比較でも別runの生成揺らぎがあるため、増分は±1円程度の幅で読む。
- 猿の手の総原価への当てはめ(推定): ¥46.82 + 約0.6 ≒ **¥47.4/セット**(目標70円に対し約23円の余裕)。+¥1/セット以上の基準(15-8)には**届かない**見込み。ただし実測は1作品(melos)・1回のみ。
- 区分1〜6の実測更新(DESIGN/BUDGET_PLAN_02の区分): ①notes LLM=¥0.27/セット(実測。見積数円未満) ②ctx dialogue TTS=従来と同回数(21 clip、model・回数不変) ③自然retry=+1 TTS(1/21) ④fallback(forced)=開発費のみ(量産時は発生率次第で追加) ⑤再開=重複TTS 0(E-3/E-5) ⑥その他(Gate/assemble/API 0)=0。
- 量産単価影響の予測: +¥0.6/セット程度(現行→予測 約46.8→47.4/目標70円)。

## 当日費用
2026-10-26 JST: 既使用約¥214(開始時)+本委任実費¥40.31+Y Voice Trial実費(別管理)/ 日次1,000円。
