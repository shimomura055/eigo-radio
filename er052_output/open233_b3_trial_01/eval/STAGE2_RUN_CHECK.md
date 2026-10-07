# STAGE2_RUN_CHECK (OPEN-233-B3-BRIEF-STRUCTURE-TRIAL-01 委任_A5、2026-10-07)

## 旧driver停止
- A5着手時(15:37)にdriver_stage2相当のプロセスがpsに存在 -> logs/STOP作成(15:37:48) -> 15:38:16確認時点でdriver/runnerのpythonは0件(ユーザー停止操作が反映済み)。killしたPIDは watch_stage2.py 2件(23388, 9264)のみ(watcherがSTOPを書くため)。driver/runnerへのStop-Processは不要。STOPは再開前に削除。

## 棚卸し(再開前、60 run)
- COMPLETE 7 / RERUN 2(hormuz V0 b3, space_weapons V0 b1: phase1途中停止)/ NOT_STARTED 51。brief 60本は全て存在(sent_match: 全60本 n_sent=1かつ一致、exit=completed)。V0 b3/b4等の追加briefは既に生成済みで不足brief生成は不要(¥0)。
- RERUN 2件はrun単位で削除(eval/deleted_A5.json)。再実行前JSON: eval/inventory_before.json(A4時点)。

## 再開: 単層4並列(ThreadPoolExecutorのみ、xargs無し) 15:40:09-16:16:55
- driver_stage2.py: 並列4、メモリエラー(1455/MemoryError/OSError)で 4->2->1 自動降格、guard(累計/1run>15円/連続失敗3/STOPファイル)追加。
- 結果: 完了 28(新規) + 既存7 = 35/60、停止2(hormuz V3 b1, meta V5 b3)、STOP marker停止23(V5/V6の未着手分+再実行待ち)。driver: consec_fail>=3でSTOP。

## 停止原因(インフラではなくWriter内部Gate)
- hormuz V3 b1: phase2 Advanced deviation MAJOR未解決 -> JA_RECHECK_REQUIRED(2回とも)
- meta V5 b1/b2: phase2 Advanced deviation STOP(a1) / V5 b3: JA_FACT_CHECK_STOP(Original/R2とも、LEDGER_DEVIATION) 2回。V5 b4はphase2待ちでguard停止。
- いずれもProduction既存のSTOP安全装置の発火。Gate回避はしていない。V5(fact数増)でMAJOR deviationが連続した可能性(解釈は評価委任以降)。
- WinError 1455 / MemoryError: 再発0(runs/_logs全件grep)。降格発動0。

## メモリ実測(eval/mem_samples.csv、15秒間隔、148点)
- 同時python 最大12(4 run x launcher+実体+子)。1プロセス最大 WorkingSet 約298MB / Private(Commit)約1233MB。
- 空き物理メモリ最小 約4.2GB、空きコミット(仮想)最小 約8.97GB(TotalVirtual 約30.1GB)。「1プロセス最大x2(約2.5GB)」を常に上回る -> 降格不要。

## 再開後の棚卸し(eval/inventory_after_A5.json)
- COMPLETE 35 / RERUN 4(V3 hormuz b1, V5 meta b2, b3, b4) / NOT_STARTED 21(V5 meta b1・hormuz b1-4・space_weapons b1-4、V6 全12)。V5 meta b1はw1_failed_a1のみ。
- 失敗退避dir w1_failed_a1 は7件(A4/A5共通、消さず保持)。

## 費用(オンディスク実測)
- briefs 66件(V2 6含む)85.14円(段階1の55.49円を含む。段階2追加分29.65円)/ w1 38件189.87円(完了35件179.39円、平均5.13円、最大12.29円)/ w1_failed 5件24.03円。
- 合計(段階1含む)約299.04円。クラッシュ前の復元不能分は不明(推定10-20円)。累計約299-320円(上限500、STOP480未到達)。

## 委任_A6/A6b(2026-10-07 16:23-17:06)
- A6(16:23-16:51): 21 run処理。完了14(V5 meta b1, hormuz b2-4, space b1-4、V6 meta b1-4, hormuz b1-3 の一部)・WRITER_GATE_STOP 1(hormuz V5 b1: JA_FACT_CHECK_STOP/LEDGER_DEVIATION、2回)。V5 hormuz b3は1回目Gate STOP→再試行で完了。その後ネット切断(openai.APIConnectionError / ENOTFOUND)でV6 hormuz b4・space_weapons b1-4がinfra失敗し、連続失敗guard(consec_fail=6)が発火→STOP。発火理由=ネット切断(Gate由来ではない)。
- A6b手順0: driver/runnerは0件(memmon重複2系統のみ→停止して1本起動)。driver_stage2.pyの編集は完了・構文OK・DRYRUN正常。infra失敗5 runのw1/w1_failed_a1を削除(eval/deleted_A6b.json、失効cost ¥4.66)、logs/STOP削除、CUM_EST0=405.6に更新、同枠再実行(16:59-17:06)。
- A6b結果: 5 run全て完了(reruns 0、consec_fail 0、STOPなし)。
- 最終(eval/inventory_after_A6b.json): COMPLETE 55 / WRITER_GATE_STOP確定 5(V3 hormuz b1: Advanced deviation MAJOR->JA_RECHECK_REQUIRED、V5 meta b2: Advanced deviation MAJOR、V5 meta b3: JA_FACT_CHECK_STOP、V5 hormuz b1: JA_FACT_CHECK_STOP(LEDGER_DEVIATION)、V5 meta b4: A5でphase1後にGate停止・再試行対象外指示)。条件別: V0 12/12, V1 12/12, V3 11/12(hormuz b1欠), V5 8/12(meta b2,b3,b4・hormuz b1欠), V6 12/12。テーマ別欠: meta 3(全V5)、hormuz 2(V3 b1,V5 b1)、space 0。Gate種別: Advanced deviation/JA_RECHECK系 2(+b4不明1)、JA_FACT_CHECK_STOP 2。
- メモリ(A6/A6b、eval/mem_samples.csv 172点): 同時python最大12、Private最大約1.29GB/プロセス、空き物理最小約3.7GB、空きコミット最小約8.7GB。WinError 1455/MemoryError再発0、降格0。
- 費用(オンディスク実測): brief 85.14 + w1 296.42(58dir) + w1_failed 28.31 = 409.87円。A6+A6b実費≈110.8円(299.04->409.87)。+復元不能推定20 +削除分4.66 -> 累計約¥434.5(上限500、STOP480未達)。1 run最大¥12.29(上限15未達)。
- infra失敗: ネット切断5 runのみ(削除・再実行済み)。Writer内部Gate緩和・無効化なし、Production変更なし。
