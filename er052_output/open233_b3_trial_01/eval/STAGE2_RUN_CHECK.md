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
