# COST_01(JA-ASR-V2-BETA-PRODUCTION-WIRING-01 委任_02A)

## 1. 結論
- **実費の見積合計 約¥5.9**(ASR約¥5.6 + 既存LLM[Reading Resolver/実体表NER]上限約¥0.3)。委任上限¥20(ASRのみ)・見積¥16に対し約3割。日次上限¥1,000(JST)・案件見積300円以下の個別承認枠の範囲内。**Gemini TTS費用は0**(偽TTS=保存wavコピー)。
- 全有料phaseの前に`tools/stop_scope_check_01.py`をrc=0で確認(`stop_check_*_paid.json`)。再起動・自動再試行ラッパなし(各phaseは手動で1回ずつ起動。途中で原因が分かった失敗のみ修正後に再実行=下表)。

## 2. 内訳(実測のraw usage log + 監査recordからの集計。再計算: `tools/cost_summary_01.py`)
| 実走 | OpenAI ASR(`gpt-4o-mini-transcribe`) | Azure Speech(`azure-speech-stt`) | gpt-6-luna(既存LLM) | Azure費用(監査record `cost.est_jpy`合計) |
|---|---|---|---|---|
| (初回E1。`init_logger`未設定で異常終了) | 1(ログ無し) | 0 | 0 | 0 |
| E1 draw1 | 6 | 4 | 0 | ¥1.2445 |
| E1b draw2 | 6 | 1 | 2 | ¥0.3111 |
| E1c draw3 | 6 | 3 | 0 | ¥0.9778 |
| E2 run1(旧版harness。出力は上書き) | 4 | 0 | 1 | ¥0 |
| E2 run2(superseded) | 4 | 1 | 5 | ¥0.3111 |
| E2 run3(STOPPED例。失敗経路) | 5 | 0 | 3 | ¥0 |
| **E2 run4(最終。X/Y/Z全PASS_W)** | 5 | 2 | 5 | ¥0.6222 |
| E3(負例。2回実走) | 6 | 0 | 0 | ¥0 |
| **合計** | **43** | **11** | **15** | **約¥3.47** |

- OpenAI ASR単価の見積: 実wav平均6.7秒 x (¥0.045/6秒) = **約¥0.050/呼出** -> 43呼出 約¥2.16。
- Azureは監査recordの`cost.est_jpy`(`ceil(秒) x $/h x ¥/$`、unified judgeの式)の実測合計。raw usage logの`azure_stt_strict_scg`は11件で、監査record上のAzure呼出数(E1 4 + E1b 1 + E1c 3 + E2 run2 1 + run4 2 = 11)と**一致**。
- gpt-6-luna 15呼出(合計 約5.4k入力/0.7k出力token)は、Reading Resolver(既存・日本語の不一致時)と実体表NER(既存・X/Y/Z完了hook内)で、**新方式の費用ではない**(従来から同条件で発生)。単価の公表値がrepoに無いため上限として約¥0.3と見積。
- **β追加Azure費用(M-2)**: βが発火した行のAzure費用は、監査record(`cost.azure_calls=1`・`azure_seconds`・`est_jpy`)とrun単位`RunState.est_jpy_total`/`secondary_calls`が全行で一致(E1: 全行、E2 run4: X・Y ともに ¥0.3111 = RunState 0.3111)。同一wavのβ追加呼出は`SecondaryCache`をshaで共有し、重複課金なし(単体test `test_t_d3_beta_azure_call_is_shared_by_sha_cache_no_duplicate_cost`)。

## 3. 量産単価への影響(目安、70円/記事セット目標に対する)
- 新方式の追加Azure呼出は、β発火時のみ最大1回/attempt(約¥0.27〜0.36)。発火条件は『Primaryの数字崩れが観測形で、precheckが通る場合』に限られ、precheckで不要な場合はAzureを呼ばない(`test_t_b5_...`)。
- 実測: E1(月タイトル6本 x 3 draw=18判定)でAzureが呼ばれたのは8判定(従来からあるSecondary確認を含む)。うち**新方式のβ起因は2判定**(draw1 reselect a1・draw3 reselect a2)。E2 run4ではβ起因2件(X・Y。各 ¥0.3111)、Zはv2(Azure 0)。
- 新方式は誤NG(従来のreject)を減らすため、**再生成(TTS+ASR)回数の削減側にも働く**(PASS_Wは1 attemptで終了し再試行しない)。量産単価への正味影響は実記事での測定が必要(本IDでは新規測定しない。目標70円/セットへの懸念は無い規模=Std日本語4 Sectionのみが対象)。
