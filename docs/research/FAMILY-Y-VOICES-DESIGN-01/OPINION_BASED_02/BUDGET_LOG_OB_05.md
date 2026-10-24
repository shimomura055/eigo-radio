# BUDGET_LOG_OB_05 (委任_25: 再配達テーマ R0 run_01 の費用台帳)

作成: 2026-10-24。区分は『情報収集・整理』『R0生成』『再生成』『照合・Gate』『評価』を分けて記録する(ユーザー原文§7)。

## 1. 本委任の支出(LLM API。`raw_usage_log.jsonl`/`raw_usage_log_gate.jsonl`の実績)

| 区分 | 内容 | 費用(円) | 備考 |
|---|---|---|---|
| 情報収集・整理 | 本委任では行っていない(委任_24で完了、LLM API 0) | 0.000 | `BUDGET_LOG_OB_04.md` §1 |
| データ修正(OF-Y8-01〜05) | Sheet・test・文書の修正 | 0.000 | API 0 |
| R0生成(gpt-6.1-sol) | 3 Voice生成(`ypl_ob_voice_1` 5.238 + `ypl_ob_voice_3`の2 call 8.051。後者がV2とV3の生成[並行生成のstageタグ上の記録のずれ、推定]) | 13.289 | 合計は正しい |
| 再生成(UNMAPPED、各Voice1回まで) | One Voice 6.592 + Another Voice 4.068(初回UNMAPPED: V1 2文・V2 1文・V3 0文) | 10.660 | 既存規則どおり。上限内 |
| 出典照合(gpt-6-luna) | map1(3 Voice)・map2(V2)・final_map(3 Voice) | 1.260 | |
| 構造タグ(luna) | structure1(発火なし、構造再生成0) | 0.137 | |
| **run_01 小計** | | **25.344** | 上限30円の内(`BUDGET_APPROVED.json` cap_jpy=30, runs=1)。所要約209秒 |
| Leakage Gate(後追い) | runnerが累計22円超で`SKIPPED_BUDGET`にしたため、同一委任内で判定1回(luna)。`PASS`(flagged 0、書換0、本文不変) | 0.145 | `raw_usage_log_gate.jsonl`(別file)。`gate_status_original`をstate.json・run_status.jsonに保存 |
| 評価(Fable判定資料・出典対応表の作成) | `aggregate_04.py`・`build_provenance_04.py`はローカル正規表現のみ | 0.000 | agent目視はLLM API外 |
| test | 30件(03)+ er110_family_y_*_test_01 全体163件。fake clientのみ | 0.000 | `--paid`なし |
| **本委任の合計** | | **25.489円** | run_01 25.344 + Gate後追い 0.145。再起動0回、run起動1回のみ |

## 2. 10-24(JST)の日次確認
| 項目 | 金額(円) | 出典 |
|---|---|---|
| 日次累計(把握分、委任文§2) | 約433 | 委任文 |
| 本委任 | 25.489 | 上記 |
| **把握分の合計** | **約458.5** | 日次1,000円以内(余裕約541円)。他案件の並行支出は含まない |

起動前確認: `tools/stop_scope_check_01.py`(managed-id FAMILY-Y-VOICES-DESIGN-01)を run起動前とGate後追い前の2回実行、いずれもrc=0(非停止)。証跡=`er110_output/family_y_opinion_based_03/stop_check_run01_start.json`・`stop_check_run01_gate.json`。

## 3. 量産単価の見込み(測定できた分と未測定の分)
| 内訳 | 再配達(今回) | SNS run_03(前回) | 備考 |
|---|---|---|---|
| 情報収集・整理(LLM API) | 0(人手=agent閲読約25分。LLM化した場合は未測定、委任_24の仮置き10〜25円/記事) | 0 | 検索API・LLM化の費用は未測定 |
| R0生成(sol) | 13.289 | 13.637 | ほぼ同水準 |
| 再生成(UNMAPPED) | 10.660 | 8.731 | **今回の方が高い**(V1・V2の2 Voiceで発火。V1は再生成単価6.592円と高い) |
| 照合・構造タグ | 1.397 | 約1.2 | |
| Leakage Gate(後追い) | 0.145 | 0.109 | |
| **R0側の合計** | **25.489** | 23.776 | 差+1.7円(主に再生成の単価差) |

- 所見: 1テーマ(3 Voice)のR0側費用は約24〜25.5円で、2テーマ(SNS・再配達)で安定した水準。70円/記事セット目標との関係は、情報収集・整理のLLM化費用が未測定のため**現時点では判断できない**(収集のLLM化費用が20〜40円を超えなければ範囲内に収まる見込みだが、根拠のある数字ではない=未測定)。
- 費用低減の候補(未実装・Fable判断): 再生成単価の高い項目(今回V1の再生成6.6円)は、UNMAPPEDの原因が『経験欄を使い切らない/意見を長く言い直す』場合にSheetの項目数を絞れば減る可能性(仮説、未検証)。
