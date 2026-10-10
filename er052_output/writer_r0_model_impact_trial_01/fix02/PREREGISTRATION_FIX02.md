# PREREGISTRATION_FIX02: WRITER-R0-MODEL-IMPACT-TRIAL-01-FIX02(Phase 2実行前に固定、2026-10-10)

性質: Trial/DEV。Production変更なし、`APPROVED_FOR_PRODUCTION`なし、採用判断なし。優劣は書かない。本書作成時点のFIX02 API支出=JPY 0(Phase 1はAPI非呼び出し)。Flagger費用上限: FIX02全体JPY 30(見積約JPY 18〜20)。

## 1. 対象12本(3テーマ x 4源)
Fable判断(確定): 「前回R0」= FACTLOCK-ASTRA-E2E-TRIAL-01 new腕 `runs/<theme>/new/new_writer/r0.md`(`ja_writer/original.md` とsha一致、gpt-6-luna、Fact Lock付き、前回Trialが評価したR2と同一生成runのR0)。old腕 `ja_writer/original.md`(旧Writer構成、Fact Lockなし)は本比較に含めない(保存はされている: streaming 1cc983b6 / space f29bb0e9 / byd 129cfc9a)。
注意: 前回R0と今回Luna R0は同じFact Lock構成・同じモデル(gpt-6-luna)の別生成物であり、両者の差は生成ごとのばらつきを含む(事実の注記であり評価ではない)。
| cell | R0 path | article sha256 | stage | 生成モデル |
|---|---|---|---|---|
| streaming_price/prev_r0 | `er052_output/factlock_astra_e2e_trial_01/runs/streaming_price/new/new_writer/r0.md` | `0ccbef5f6046ae140faa3b929d4a5e4c557998726e0a66bf7d218933dc6687d1` | R0(生成直後) | gpt-6-luna (FACTLOCK-ASTRA-E2E-TRIAL-01 new腕 r0_meta.json、Fact Lock付き、Fact Check前の生成物) |
| streaming_price/gpt-6-luna | `er052_output/writer_r0_model_impact_trial_01/r0/streaming_price/gpt-6-luna.md` | `fa1f100432aca08737808adae8a6b442fb60891dcbaa8a0239922ae020935b33` | R0(生成直後) | gpt-6-luna (WRITER-R0-MODEL-IMPACT-TRIAL-01 今回生成) |
| streaming_price/gpt-6.1-sol | `er052_output/writer_r0_model_impact_trial_01/r0/streaming_price/gpt-6.1-sol.md` | `3f1e51b9291a8912685453686d2db80453d037820709b8a55194df7d89143e8e` | R0(生成直後) | gpt-6.1-sol (WRITER-R0-MODEL-IMPACT-TRIAL-01 今回生成) |
| streaming_price/gpt-6-astra | `er052_output/writer_r0_model_impact_trial_01/r0/streaming_price/gpt-6-astra.md` | `795b6e54461cb0173e30c509a5a37ee26cfa69f51cfba7c2cb480e6abc87ebb4` | R0(生成直後) | gpt-6-astra (WRITER-R0-MODEL-IMPACT-TRIAL-01 今回生成) |
| space_weapons/prev_r0 | `er052_output/factlock_astra_e2e_trial_01/runs/space_weapons/new/new_writer/r0.md` | `bd23cb0ea9570a6604329e694fe2f60e77a0d08f27d1be78c1ef45af0ddb09f9` | R0(生成直後) | gpt-6-luna (FACTLOCK-ASTRA-E2E-TRIAL-01 new腕 r0_meta.json、Fact Lock付き、Fact Check前の生成物) |
| space_weapons/gpt-6-luna | `er052_output/writer_r0_model_impact_trial_01/r0/space_weapons/gpt-6-luna.md` | `bf6ed54449c92c3e6398b231ea73233e3fc790844cdc4447e57324592aba0441` | R0(生成直後) | gpt-6-luna (WRITER-R0-MODEL-IMPACT-TRIAL-01 今回生成) |
| space_weapons/gpt-6.1-sol | `er052_output/writer_r0_model_impact_trial_01/r0/space_weapons/gpt-6.1-sol.md` | `007094fa4886e21be69f9bf8e62a1a0bf9af541a96c70a29b83d549af22bb8d2` | R0(生成直後) | gpt-6.1-sol (WRITER-R0-MODEL-IMPACT-TRIAL-01 今回生成) |
| space_weapons/gpt-6-astra | `er052_output/writer_r0_model_impact_trial_01/r0/space_weapons/gpt-6-astra.md` | `347d29d358a02a2a0136b6a3fa5c0c528edb64a9ac1ca1f6fd45609e0834727b` | R0(生成直後) | gpt-6-astra (WRITER-R0-MODEL-IMPACT-TRIAL-01 今回生成) |
| byd_recall/prev_r0 | `er052_output/factlock_astra_e2e_trial_01/runs/byd_recall/new/new_writer/r0.md` | `0c69dd9b19038ffd61e616ca48de5336485e4d1aafc00ccdafc8968347f8b499` | R0(生成直後) | gpt-6-luna (FACTLOCK-ASTRA-E2E-TRIAL-01 new腕 r0_meta.json、Fact Lock付き、Fact Check前の生成物) |
| byd_recall/gpt-6-luna | `er052_output/writer_r0_model_impact_trial_01/r0/byd_recall/gpt-6-luna.md` | `be9698720f673509f19b626b53484d2bd2a2c845ab3f01c537c5d0ca8eded2b5` | R0(生成直後) | gpt-6-luna (WRITER-R0-MODEL-IMPACT-TRIAL-01 今回生成) |
| byd_recall/gpt-6.1-sol | `er052_output/writer_r0_model_impact_trial_01/r0/byd_recall/gpt-6.1-sol.md` | `01a69eb92c4cf647de3b835033f133e1896bb2304a8dfaf4b28b30e7ed465c4f` | R0(生成直後) | gpt-6.1-sol (WRITER-R0-MODEL-IMPACT-TRIAL-01 今回生成) |
| byd_recall/gpt-6-astra | `er052_output/writer_r0_model_impact_trial_01/r0/byd_recall/gpt-6-astra.md` | `aa9e462f013a63200b81ad54bc5debc189c719d6ad8f11d1cc8c54a1745d4662` | R0(生成直後) | gpt-6-astra (WRITER-R0-MODEL-IMPACT-TRIAL-01 今回生成) |

## 2. 台帳(完全台帳方式。FIX01-A r0_fix01_driver.py と同一)
| テーマ | 台帳path | sha256 | 見出し数 |
|---|---|---|---|
| byd_recall | `er052_output/factlock_astra_e2e_trial_01/runs/byd_recall/new/research_ledger/verified_fact_ledger.txt` | `06ae3dca98cd237a3bf4ab8b3a58b3e8103ff7761662a5868ba0f46c9b67dafd` | 11 |
| space_weapons | `er052_output/factlock_astra_e2e_trial_01/runs/space_weapons/new/research_ledger/verified_fact_ledger.txt` | `f172a253f24b99d66cf0ffbe187857dddb3f6e3fa6cc1186700942519f4a6868` | 22 |
| streaming_price | `er052_output/factlock_astra_e2e_trial_01/runs/streaming_price/new/research_ledger/verified_fact_ledger.txt` | `11eb38bd8532096c2ad11569ab06ea3e4fd1e113f001a52d6a6ee789e9481ce3` | 7 |
- 方式: `ledger_restore_01._HDR` を `^\[(?P<st>[A-Z_]+)(?:\s+-\s+[^\]]*)?\]\s+(?P<id>[^\s:]+):\s*(?P<text>.*)$` にprocess内のみ差替え(detectors配下無変更)。driverが assert: 受領Fact数 == 台帳見出し数(上表) かつ sha一致(記事・台帳)。不一致なら当該セルを実行せず(API前にassert停止)STOP報告。
- 4源(prev_r0/Luna/Sol/Astra)は同一テーマで同一台帳ファイルを使う(sha同一)。

## 3. Flagger条件(既存、変更なし)
- D0(`d0_directional.py` 決定論)+D2(`prompts_flagger.d2_system()` 記事モード、`gpt-6.1-sol`、effort=medium)。D2rank不使用。detectors配下5ファイルsha(FIX01-Aと同一): prompts_flagger `730bc55f...3e0c` / run_flagger `0962b6e4...f675` / flagger_lib `4cb071ff...a2da` / d0_directional `972634b4...4583` / ledger_restore `7e465e5b...d17de`(実行直前に再計算し照合)。D2 system prompt sha `b8dacc147009a13b`(raw log request.systemから照合)。
- 文分割: `run_flagger_01._split_sentences`(前回と同一)。R0は再生成しない(今回R0 9本は既存 `r0/<theme>/<model>.md`、前回R0は上表path)。
- 再試行: 失敗時は同条件で最大1回、記録。
- D2 prompt出力仕様(`COMMON_OUT`、引用): 「出力はJSON1個のみ(前後に説明文を付けない): {"flags":[{"sentence_id":"<sid>","type":"<タイプ名>","fact_ids":["<fact_id>"],"confidence":0.0-1.0,"severity":"重大|非重大","question":"人間向けの確認質問を日本語1文"}]} Flagが無ければ {"flags":[]}。...」。`d2_system()`: 「疑いが小さくても重大の可能性が少しでもあれば低めの確信度(0.1〜0.4)で出してよい(人間に見せるかどうかは後で確信度の閾値で決める)。明らかに台帳どおりの文は出さない。」 => confidence 0.1〜0.4の低確信Flagも出力させる仕様であることを確認(上位3強制はしない)。

## 4. 集計定義(事前固定)
- Flag = `union_flags(D0 flags, D2 flags)` の文単位(sentence_id, type)ユニーク件数(FIX01-A/RESULT_01と同定義。D0 gate_only は和集合に入れず「D0参考件数」として別掲)。
- 閾値別件数: confidence >= 0.10 / 0.20 / 0.30 / 0.50 の件数(各セル)と最大confidence(Flag無しは「-」)。R0源別合計・閾値別合計も出す。
- 全Flag一覧: confidence降順。各Flagのconfidence/種類/該当文/対応Fact/理由(question)を `flags/<theme>/<source>.json` に保存。
- 比較条件同一性の機械確認: 12セルで 台帳sha(テーマ内一致)・D2 prompt sha・Flaggerモデル/effort・Fact数==見出し数・文分割コード・attempts を一覧化。FIX01-A Disney+ 結果(Luna/Sol/Astra = 0/0/0)との一致を今回Luna/Sol/Astra Disney+と照合(同一記事・同一条件の再実行)。
- 使用モデル欄: Flagger gpt-6.1-sol(最新世代最上位系)、R0生成モデル(各セル)。

## 5. STOP条件
Fact数assert不一致 / FIX02費用がJPY 30超見込み / Flagger本体(detectors配下)変更が必要。該当時は実行せず報告。
