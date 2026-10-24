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
