# BUDGET_LOG_01(FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_01)

| 項目 | 値 |
|---|---|
| API call数 | 1(再送・再生成なし) |
| model_id(要求/実際) | gpt-6-luna / gpt-6-luna(response.model一致) |
| response_id | resp_02ca57d26220c021006adc7fbdb61c87d08dc91d938c2d5720 |
| reasoning設定 | 指定なし(provider default、Production KP段と同条件)。reasoning_tokens=1,255 |
| input_tokens(うちcached) | 1,751(0) |
| output_tokens(うちreasoning) | 2,529(1,255)。可視出力は約1,274 token |
| 費用 | $0.00144 = **約0.230円**(¥160/$) |
| 所要 | 24.7秒 |
| 上限 | 5円に対し0.23円(4.6%) |
| 日次 | 本委任0.23円。日次1,000円内 |

生データ: `usage_01.json`。計算: 1,751×0.10/1e6 + 2,529×0.50/1e6 = $0.0001751 + $0.0012645。

## Trial-02(委任_03、2026-10-24)
| 項目 | 値 |
|---|---|
| API call数 | 1(再送・再生成なし) |
| model_id(要求/実際) | gpt-6-luna / gpt-6-luna |
| response_id | resp_0c8c1b184b407ae2006adc9cf3524487d08855a14b71e0a14b |
| input / output(reasoning) | 1,842(cached 0) / 1,773(555) |
| 費用 | $0.001071 = **約0.171円**(¥160/$)。Trial-01(0.230円)比 -26% |
| 所要 | 16.8秒(Trial-01 24.7秒) |
| 上限 | 5円に対し0.17円。日次1,000円内 |

生データ: `usage_02.json`。計算: 1,842×0.10/1e6 + 1,773×0.50/1e6。

## Trial-03(委任_05、2026-10-25)
| 項目 | 値 |
|---|---|
| API call数 | 17(Before 2 + After初版03 3 + 03b 3 + 03bR2 3 + 03c 3 + 03cR2 3。再送・失敗0。03bR2/03cR2は同Promptの再標本=選定の安定性確認) |
| model_id | gpt-6-luna / gpt-6-luna(全call一致、Trial-01/02と同一) |
| Trial追加実費 | 合計 **4.905円**(¥160/$)。上限10円の49%。内訳: Before(02B)0.43 / 03初版0.82 / 03b 0.94 / 03bR2 0.89 / 03c 0.83 / 03cR2 0.99 |
| 所要 | 各15〜38秒(3〜6並列で1 launchずつ、計5 launch)。最終版03cは約20〜38秒/call(Trial-02は16.8秒) |
| 日次 | 本委任4.9円。日次1,000円内 |
| 再起動 | 0 |

### Production採用時の量産費用(別掲)
最終版(03c)の1 call: input約2.6k / output約2.2〜3.9k token(reasoning 1.2〜2.0k)= 約0.22〜0.35円(平均約0.31円)。Trial-02(0.171円)比 約+0.14円/記事セット(Advancedの学習解説テキスト1 callのみ、Standardは対象外)。70円/記事セット目標に対し約0.4%。Part 2の指示増(選定理由・仕組み・比較・焦点の出力項目)でoutputが約1.6倍に増えたことが主因。reasoning指定の有無・出力項目の削減で下げる余地はあるが、品質を優先し今回は調整せず。
生データ: `usage_02B_*.json` `usage_03*_*.json`(prompt_sha256・response_id・token内訳を含む)。


## Trial-03追補(委任_06、2026-10-25)
| 項目 | 値 |
|---|---|
| API call数 | 5(03d: 賢者1、開いた窓2、イグ・ノーベル賞2。1 launch。再送・失敗0、再起動0) |
| model_id | gpt-6-luna / gpt-6-luna(全call一致) |
| 追補実費 | **1.376円**(¥160/$。内訳: gift 0.342 / ig_nobel 0.248・0.308 / open_window 0.258・0.219)。個別上限3円の46% |
| Trial-03累計(委任_05+追補) | 4.905 + 1.376 = **6.281円**(Trial-03上限は委任_05の10円に対し63%、追補上限3円は別枠) |
| FAMILY-Z-STUDY-TEXT-TRIAL-01 全体累計 | Trial-01 0.230 + Trial-02 0.171 + Trial-03 6.281 = **約6.68円** |
| STOP確認 | `tools/stop_scope_check_01.py` launch前 rc=0(stop=false、`stop_check_06.json`) |
| 日次 | 本委任1.4円。日次1,000円内 |

### 量産費用(03d)
1 call平均 約0.275円(0.219〜0.342円)/記事セット(Advanced学習解説テキストのみ)。Trial-02比 +約0.10円、70円目標の約0.4%。
生データ: `usage_03d_*.json` `usage_03dR2_*.json`。


## Trial-04(委任_09、2026-10-25)
| 項目 | 値 |
|---|---|
| API call数 | 36(1 launch。完成6セット[3作品×r1/r2、各P1α・Step A・Step B・Part 3/4]=24 call + β腕P1 6 call + Step A追加[r3/r4] 6 call。再送・失敗0、再起動0) |
| model_id | gpt-6-luna / gpt-6-luna(全call一致。最新世代の推奨系) |
| Trial-04実費 | 合計 **4.0605円**(¥160/$)。内訳: 完成6セット2.746円 / β腕P1 0.478円 / Step A追加(R5) 0.836円。委任_09上限20円の20%(安全線18円未到達) |
| 所要 | launch全体 約70秒(9並列job)。1記事セットのクリティカルパス 平均38.0秒(32〜47秒、P1∥Step A→Step B∥Part 3/4) |
| STOP確認 | `tools/stop_scope_check_01.py` launch前 rc=0(`stop_check_09.json`・`stop_check_09b.json`) |
| 日次 | 本委任4.06円。2026-10-25の既往Trial実費合計(ACTIVE_TASK記載414.66円)に加算して約418.7円、日次1,000円内 |
| FAMILY-Z-STUDY-TEXT-TRIAL-01 累計 | Trial-01 0.230 + 02 0.171 + 03 6.281 + 04 4.061 = **約10.74円** |

### 量産費用(Trial-04、α腕)
1記事セット(Advanced学習解説テキスト、4 call): 平均 **0.458円**(0.398〜0.507円)。Trial-03(03d)の約0.275円比 +0.18円(+66%)、70円/記事セット目標の約0.65%。Part 2が0件なら3 call(Step B不要)。Standardは対象外。
増加要因: 呼出の分割(P1・Step A・Step Bで入力トークン合計 約5.3〜5.6k、03dは約2.7k)と、Step Aの候補検討reasoning。呼出削減の案(Part 3/4をStep Aと同一call等)は品質判定後の別判断。
生データ: `usage_04*.json`(prompt_sha256・response_id・token内訳を含む)。


## Trial-05(委任_10、2026-10-25)
| 項目 | 値 |
|---|---|
| API call数 | 18(Step A'のみ。開いた窓6・イグ6・賢者3・猿の手3。1 launch、再送・失敗0、再起動0)。Step B(6 call予定)は新規call拒否で未実行 |
| model_id | gpt-6-luna(全call一致。最新世代の推奨系) |
| Trial-05実費 | **9.1115円**(¥160/$)。平均0.506円/call(0.288〜0.770)。**委任上限8円を1.1115円超過**。原因: 新規call拒否線(Step A' 累計6.8円)を呼出開始時の累計で判定し、9並列のため実費確定前に全18 callが開始した(Opus見込み0.2〜0.3円/callを大きく超えた単価見積り誤りも要因) |
| 所要 | launch全体139.5秒(1 callは29〜90秒) |
| STOP確認 | `tools/stop_scope_check_01.py` launch前 rc=0(`stop_check_10.json`・`stop_check_10b.json`) |
| 日次 | 本委任9.11円。2026-10-25の既往Trial実費(約418.7円)に加算して約427.8円、日次1,000円内 |
| FAMILY-Z-STUDY-TEXT-TRIAL-01 累計 | 10.74 + 9.1115 = **約19.85円** |
生データ: `usage_05_*_stepA5_*.json`。


## 案件累計上限の引き上げ(2026-10-25、委任_11)
Fable引き上げ、2026-10-25、理由=Opus条件B推奨の3回目(Trial-06)実施。案件累計上限 20円 → **35円**(300円以下のFable自律範囲、日次1,000円内)。累計(Trial-05まで)約19.85円 + 本委任上限14円 = 最大約33.85円。本委任(委任_11)の上限=14円(Step A'' 18 call + Step B 約6 call)。
費用ガードは予約方式へ改修(`run_trial_06.py` `Budget`)。Trial-05の上限超過(8円に対し9.11円)は呼出開始時点の累計判定が原因。

## Trial-06(委任_11、2026-10-25)
| 項目 | 値 |
|---|---|
| API call数 | 18(Step A''のみ。6作品×N=3。1 launch、再送・失敗0、再起動0)。Step B(約6 call)は事前登録の終了条件により未実行 |
| model_id | gpt-6-luna(全call一致。最新世代の推奨系) |
| Trial-06実費 | **8.855円**(¥160/$)。平均0.492円/call(0.298〜0.762)。本委任上限14円の63%、Step A''上限12.6円の70%。予約方式ガード: 最大予約合計12.53円(上限12.6円内)で上限超過0 |
| 所要 | launch全体149.0秒(1 callは平均52.3秒、最大76.8秒) |
| STOP確認 | `tools/stop_scope_check_01.py` launch前 rc=0(`stop_check_11.json`) |
| 日次 | 本委任8.86円。2026-10-25の既往Trial実費(約427.8円)に加算して約436.7円、日次1,000円内 |
| FAMILY-Z-STUDY-TEXT-TRIAL-01 累計 | 19.85 + 8.855 = **約28.71円**(引き上げ後の案件上限35円の82%) |
生データ: `usage_06_*.json`(prompt_sha256・response_id・token内訳)。


## 案件累計上限の引き上げ(2026-10-25、委任_12)
Fable引き上げ(委任文記載)、2026-10-25、理由=ユーザー承認のTrial-07(Part 2 最大1件方式)。案件累計上限 35円 → **50円**(300円以下のFable自律範囲、日次1,000円内)。累計(Trial-06まで)約28.71円 + 本委任上限12円 = 最大約40.71円。本委任(委任_12)の追加API上限=**12円**(Step A'' 上限10.8円 + Step B 1.2円)。費用ガードは予約方式(`run_trial_07.py`が`run_trial_06.Budget`を再利用)。
