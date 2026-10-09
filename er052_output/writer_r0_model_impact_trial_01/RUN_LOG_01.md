# RUN_LOG_01: 実行履歴・条件同一性チェック(機械照合)

## 1. 実行履歴
- Phase 1(API 0円): 入力点検・Prompt組立(dry-run)・PREREGISTRATION_01.md作成 -> commit 988733b3(push済)。
- Phase 2-1: R0 9本を9プロセス同時並列(`r0_trial_driver_01.py r0`、epoch開始 1791587309)。全9本 1試行で成功、再試行0、失敗0。
- Phase 2-2: Risk Flagger(D0 + D2記事モード)9セルを9プロセス同時並列(`r0_trial_driver_01.py flag --max-yen 30`)。全9セル valid_json=True、形式再呼び出し0、transient再試行0。
- Phase 3: `aggregate_01.py`・`runlog_01.py`で集計(API 0円)。

## 2. R0 試行履歴
| テーマ | モデル | 試行数 | ok | response_id | model_id | ts |
|---|---|---|---|---|---|---|
| streaming_price | gpt-6-luna | 1 | True | resp_013720ebefd3d841006ac973f21f9487d08b2da69ca011769c | gpt-6-luna | 2026-10-10T08:08:32 |
| streaming_price | gpt-6.1-sol | 1 | True | resp_0fd63b22d62e4603006ac973f217cc87d085d5ebc0c5b662ed | gpt-6.1-sol | 2026-10-10T08:08:32 |
| streaming_price | gpt-6-astra | 1 | True | resp_0ef9cedf197dc4df006ac973f247ec87d08ef3eff70cb0dbbc | gpt-6-astra | 2026-10-10T08:08:32 |
| space_weapons | gpt-6-luna | 1 | True | resp_0b05e2842af37525006ac973f226e887d081d88938c0361930 | gpt-6-luna | 2026-10-10T08:08:32 |
| space_weapons | gpt-6.1-sol | 1 | True | resp_073ff1a646333928006ac973f23aec87d0beac96403a69b7ba | gpt-6.1-sol | 2026-10-10T08:08:32 |
| space_weapons | gpt-6-astra | 1 | True | resp_0ed97b05ebfe76b3006ac973f239f887d0abf4e09ea0d851a3 | gpt-6-astra | 2026-10-10T08:08:32 |
| byd_recall | gpt-6-luna | 1 | True | resp_07f795767286105a006ac973f23b0c87d09b0f42e255e533e1 | gpt-6-luna | 2026-10-10T08:08:32 |
| byd_recall | gpt-6.1-sol | 1 | True | resp_012819e924d45a2e006ac973f27a9887d08b650b99dc1a3b86 | gpt-6.1-sol | 2026-10-10T08:08:32 |
| byd_recall | gpt-6-astra | 1 | True | resp_0cfb68a66bab13ea006ac973f2120c87d098c0bbdc9aa56286 | gpt-6-astra | 2026-10-10T08:08:32 |

model_id不一致(要求名と応答`model`欄): 0件

## 3. 比較条件の同一性チェック(機械照合の結果)

- streaming_price: R0 Prompt sha 3モデル一致=True (37a6174bbd5ac24a、事前登録manifestと一致=True) / 入力メタ(brief・台帳sha・effort・developer message・FactLockブロックsha)一致=True / Fact Check・must-fix未実行(全セル共通)=True
- space_weapons: R0 Prompt sha 3モデル一致=True (29d462e94970cefb、事前登録manifestと一致=True) / 入力メタ(brief・台帳sha・effort・developer message・FactLockブロックsha)一致=True / Fact Check・must-fix未実行(全セル共通)=True
- byd_recall: R0 Prompt sha 3モデル一致=True (c2d7b29f39460410、事前登録manifestと一致=True) / 入力メタ(brief・台帳sha・effort・developer message・FactLockブロックsha)一致=True / Fact Check・must-fix未実行(全セル共通)=True
- Risk Flagger D2 system prompt sha: 全9セルで一致=True (b8dacc147009a13b)。想定値(PREREGISTRATION: b8dacc14...)と一致=True
- Flaggerモデル: 全9セルで {'gpt-6.1-sol'}、effort={'medium'}、応答model_id={('gpt-6.1-sol',)}。
- streaming_price: Flagger台帳sha 3セル一致=True、入力Fact数(Flagger受領)={5}
- space_weapons: Flagger台帳sha 3セル一致=True、入力Fact数(Flagger受領)={22}
- byd_recall: Flagger台帳sha 3セル一致=True、入力Fact数(Flagger受領)={11}
- driver sha256(実行時=現在): ab25f13de0f44f68d6056d7c46225f765b9d0213a75399699872c1c23cb725ac、事前登録時: ab25f13de0f44f68d6056d7c46225f765b9d0213a75399699872c1c23cb725ac -> 一致=True
- 全条件同一(R0 Prompt・入力・Flagger prompt): True

## 4. Production/既存ファイル無変更の確認

- `er019_family_x_ja_writer_o_r1_r2_01.py`: 追跡ファイルの変更=0件
- `er052_factlock_writer_trial_01_run.py`: 追跡ファイルの変更=0件
- `er052_factlock_astra_e2e_runner_01.py`: 追跡ファイルの変更=0件
- `er006_model_routing_contract_01.py`: 追跡ファイルの変更=0件
- `er005_output/cost_baseline_01/pricing_snapshot.json`: 追跡ファイルの変更=0件
- `CURRENT_SPEC.md`: 追跡ファイルの変更=0件
- `er052_output/writer_dev_risk_flagger_01/detectors`: 追跡ファイルの変更=0件 (untracked既存: 4件、本Trial起因ではない)
- `er052_output/factlock_astra_e2e_trial_01`: 追跡ファイルの変更=0件

(`git status`は本Trial着手前から別タスク由来の未追跡/変更ファイルを含む。上記は本Trialで触れていないこと[追跡ファイル変更0件]の確認。)

## 5. 発見事項
- streaming_price台帳のF01・F07(`[AMBIGUOUS - ...]`見出し)が既存Flaggerのパーサで読み飛ばされ、Flaggerの入力は5/7件(RESULT_01.md冒頭)。Flagger側の修正は行っていない。
- 並列9本実行のため処理時間はAPI負荷を含む。費用は usage x pricing_snapshot.json(Standard)の算出値(請求ダッシュボード照合は未実施)。