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
