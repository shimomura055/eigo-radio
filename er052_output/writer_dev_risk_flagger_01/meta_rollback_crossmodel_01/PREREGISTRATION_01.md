# PREREGISTRATION_01: WRITER-RISK-FLAGGER-META-ROLLBACK-CROSSMODEL-01(Phase 1、2026-10-10、課金API呼び出し0件)

Trial/DEVのみ。Production・CURRENT_SPEC・Promptは変更しない。以下は実行前の登録であり、結果を見た後の変更・再実行はしない。

## 1. 目的
前タスク(META-ROLLBACK-CHECK-01, RESULT_01.md)で現行A3/A4(gpt-6.1-sol)が NOT_DETECTED だった META実在稿の方向反転文 s23「The company also restored the human concierge feature to the way it had been before, at least for now.」(台帳MUSE-HC-012はrollback/一時撤回)を、**モデルだけ**差し替えた8条件で検出できるかを、A3/A4 各1回で見る(モデル依存性の確認のみ)。Prompt改善・仕様提案は目的外。

## 2. 8条件とactual model_id(models listは無料エンドポイントで実在確認、2026-10-10)
置換なし。全8条件とも指定名に対応するIDがAPI上に存在し、利用可と判断(READY。ただし実呼び出しで403/404等が出た場合はその条件をUNAVAILABLEとして理由記録し、他は続行)。

| # | 指定名 | model_key | actual model_id | 同名の別候補(採用せず) | Thinking設定(本Trial) |
|---|---|---|---|---|---|
| 1 | Gemini 3.5 Flash-Lite | gemini35fl | `gemini-3.5-flash-lite` (version 3.5-flash-lite-07-2026) | gemini-3.1-flash-lite 等(別世代) | Provider既定(docs: On=minimal、確認済み)。thinkingConfig送らない |
| 2 | Gemini 3.8 Flash | gemini38f | `gemini-3.8-flash` | gemini-3.6/3.7-flash(別世代) | Provider既定(docs: On=medium、確認済み)。送らない |
| 3 | DeepSeek V4 Flash | dsflash | `deepseek-flash`(=DeepSeek-V4.1-Flash。旧名deepseek-v4-flashは公式で引退・同モデルへ転送) | - | **`thinking:{type:disabled}` を明示**(既定がenabledのため。docs確認済み) |
| 4 | DeepSeek V4 Flash Thinking | dsflash_think | `deepseek-flash`(同一ID、別IDではない) | - | `thinking:{type:enabled}` を明示、effort既定(high、models list記載)。確認済み |
| 5 | Claude Haiku 4.5 | haiku45 | `claude-haiku-4-5-20251001`(日付付きのみ列挙。`claude-haiku-5-5`は別モデルで不採用) | - | thinking未送信(Haiku 4.5はenabled/disabled選択式、省略時の既定=OFFと理解するがdocsでの明示確認は**未確認**) |
| 6 | Claude Sonnet 5 | sonnet5 | `claude-sonnet-5`(`claude-sonnet-5-5`は別モデルで不採用) | - | thinking/effort未送信。Sonnet 5はadaptive/disabledのみ対応(models list確認済み)。省略時にthinkingが働くか否かは**未確認**(実行後のresponseのthinkingブロック有無で事後記録) |
| 7 | Luna | luna | `gpt-6-luna` | gpt-5.6-luna(別世代) | 前回と同一(reasoning effort=medium) |
| 8 | Sol | sol | `gpt-6.1-sol` | gpt-6-sol, gpt-5.6-sol(別) | 前回と同一(effort=medium) |

## 3. 価格(推測なし。公式ページHTTP 200取得 2026-10-10 04:50 UTC。USD/JPY=160)
USD/1M tokens(input / cached input / output)。保存先 `xm_prices_01.json`。
- Gemini 3.5 Flash-Lite 0.30 / 0.03 / 2.50(出力にthinking込み)、Gemini 3.8 Flash 0.75 / 0.075 / 3.75(2026-12-31まで、2027-01-01以降 1.50/7.50): https://ai.google.dev/gemini-api/docs/pricing
- DeepSeek `deepseek-flash` Standard=Peak 0.30 / 0.006 / 1.20(Off-peak半額。thinking/非thinking同一単価): https://api-docs.deepseek.com/quick_start/pricing(既存登録 pricing_snapshot.json 2026-10-09と一致)
- Claude Haiku 4.5 1.00 / 0.10 / 5.00、Claude Sonnet 5 2.00 / 0.20 / 10.00: https://platform.claude.com/docs/en/about-claude/pricing(「4.7以降は新tokenizerで約30%多いtoken」の記載あり。Sonnet 5が該当するかは未確認、高位見積で吸収)
- Luna 0.10 / 0.01 / 0.50、Sol 2.00 / 0.10 / 10.00: https://developers.openai.com/api/docs/pricing(既存登録と一致)
- 既存リポジトリ登録: er005_output/cost_baseline_01/pricing_snapshot.json(2026-10-09更新)にLuna/Sol/DeepSeekのみ。Claude/Gemini(テキスト)の登録は無かったため本タスクで `xm_prices_01.json` に別登録(既存snapshotは変更しない)。

## 4. 同一条件(前回と同一。sha一致確認済み、dry-run)
- 記事 `er019_output/meta/run_03/b1b/article.md` sha256 `cab7f5f3a147b3944558b738fdcb8888f5c754267d47cf177a9438f3d400b327`(29文、s23=対象文)
- 完全台帳 `er019_output/meta/run_03/ledger/verified_fact_ledger.txt` sha256 `6e271bb24fdf3a587bd803d80cec5d32aaaaeb047ca3389c1597283aa3719db4`(15件、見出し=parsed)
- A3 system prompt sha256 `9d9950428419c3af824cc5b8676a4b564f96aeb87657c547d418cc86ef3538e9` / A4 `c87b95e5bcf1b5c266b8978c5688849eb339a6087efbcaf56bb7399ed128ef01`(再計算で一致)
- user message sha256 `88bcf14b4dba255b2e5323a95c3edb4e8464421fd49dabf08c52ce6b3b4fc73c`(A3/A4共通)。前回raw(runs/d2_gpt-6.1-sol_rb_A3/A4_raw.jsonl)のrequest.system/userと**文字列完全一致**(dry-run assertで確認)
- 英語splitter・0件許容・TopNなし・出力JSON schema・validate_flags・retry機構(format再試行1回/transient再試行2回)・max出力8000・effort=medium(OpenAI系のみ)すべて前回と同一コード経路
- 追加差分(Provider必須のみ): Anthropic=`max_tokens`/`anthropic-version`ヘッダ、Gemini=`contents/systemInstruction/generationConfig.maxOutputTokens`形式、DeepSeek=`thinking`明示(1,2条件の区別に必須)、JSON modeは全Providerで使わない(前回OpenAIもJSON modeなし)。temperature/seed/response_format/reasoning_effort(DeepSeek)は送らない
- dry-run生成物: `dry_run/<model_key>/A3_request.json, A4_request.json`、`dry_run/dry_run_report_01.json`

## 5. Blind性
前回結果・Human評価・方向反転(rollback/restore)を示唆する文言はPromptにも入力にも与えない。台帳・記事は前回と同一(台帳に既にあるrollback記述のみ)。

## 6. 実行規則
各条件×A3/A4 **1回のみ**(R.run_llm内の自動format再試行1回/transient再試行は前回同一機構として許容、attemptsを記録)。結果を見た再実行・追加run・失敗条件の別モデル置換は禁止。1run上限JPY8、台帳累計上限JPY40(超過で停止)。結果保存: `runs/<model_key>/A3.json, A4.json`(raw response含む)、`cost_ledger_xm_01.jsonl`。前タスクディレクトリ(meta_rollback_check_01/, post_en_trial_01/)には書き込まない。

## 7. 主要指標(機械的整理基準)
対象文s23(Union: A3/A4別)の検出と方向反転認識。
- **Yes**: s23をFlagし、reason(question)が「台帳はrollback/撤回/保留なのに本文はrestore/復元と書いている」趣旨を明示
- **Partial**: s23をFlagしたが理由が方向反転を明示しない
- **No**: s23未検出、または別問題のみ
Closeout語彙(条件ごと): DETECTED(A3/A4の少なくとも一方がYes)/ PARTIALLY_DETECTED(Yesなし、Partialあり)/ NOT_DETECTED / UNAVAILABLE(理由記録)。
(Yes/Partialの境界の機械判定はreasonの語(rollback/撤回/保留/restore/復元等)の有無を一次基準とし、人間確認はしない。)

## 8. 今回(Phase 1)やらないこと(11項目)
1. 課金API呼び出し(生成/チャット補完)を行わない 2. Production変更 3. CURRENT_SPEC変更 4. Prompt変更・Providerごとの最適化 5. 前タスク結果の再解釈・再実行 6. Human評価・Blind packet化 7. A5/A6・強制TopN・Rewrite・再生成・STOP処理の追加 8. Astra等8条件以外のモデル追加 9. pip install(RESTで実装) 10. SSOT(DECISION_LOG/OPEN_ITEMS等)の更新(Phase 2結果後にFable判断) 11. 配線(PRODUCTION_WIRED)・採用判断

## 9. Status不変更
A3+A4英訳後配置=VALIDATED。R0後/翻訳後Hard STOP除去=APPROVED_FOR_PRODUCTION。新Writer+Checkerなし+A3/A4+Human Review=APPROVED_FOR_PRODUCTION。いずれも未PRODUCTION_WIRED。本Trialの結果で変わらない。

## 10. 費用見積(estimate_01.json、前回実測 A3 in5060/out692・A4 in5210/out632基準。2call=A3+A4)
| model_key | 低位 | 中央 | 高位(JPY) |
|---|---|---|---|
| gemini35fl | 0.71 | 1.02 | 3.87 |
| gemini38f | 1.51 | 2.03 | 6.46 |
| dsflash | 0.57 | 0.75 | 1.43 |
| dsflash_think | 0.57 | 0.75 | 2.20 |
| haiku45 | 2.01 | 2.70 | 5.40 |
| sonnet5 | 4.02 | 5.40 | 17.24 |
| luna | 0.20 | 0.27 | 0.54 |
| sol | 4.02 | 5.40 | 10.79 |
| **合計** | **13.60** | **18.32** | **47.92** |

低位=入力x0.9・出力x0.5、中央=前回実測と同トークン、高位=入力x1.35(tokenizer差)・出力x3(thinking既定ON条件は4000tokを下限)。thinkingの出力tokenは不確実性が最大で、実測は中央を下回る可能性もある(前回のPre-Sorter Trialでも見積が過大だった)。再試行が各1回発生した場合は最悪約2倍。
