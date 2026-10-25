# BUDGET_LOG_01 (委任_27: 再配達音声化Trialの費用台帳。実費はraw usage logで確定)

作成: 2026-10-25。為替USD/JPY=160(pricing_snapshot.json)。有料launchは**4回**(ja 1・english 1・scaffold 1・audio[tts+assemble] 1)、同一コマンドの再起動0、STOP通知0、原因不明のrc≠0 0回。権利照合・ページ・QA集計はAPI 0。

## 1. 工程別の実費(円)
| 工程 | stage/内容 | 実費 | 見積(BUDGET_PLAN_01) | 備考 |
|---|---|---|---|---|
| リード生成 | `yr_lead` gpt-6.1-sol high 1 call(再生成0) | 1.076 | 0.8〜1.6 | |
| Tension+Closing生成 | `yp_tension` gpt-6.1-sol high 1 call(出力5,525 token=推論込み、再生成0) | **9.374** | 1.2〜2.4 | **見積の約4〜8倍**。原因=persona版`generate_tension`の既定effort=high(出力5.5k token)。リードは568 in/559 out token。Cap内だが見積外れ(下記§3) |
| Tension Leakage Gate | `yr_tension_gate_leak1` luna high 1判定(PASS、書換0) | 0.136 | 0.3〜2.8 | |
| (小計 日本語) | raw_usage_log.jsonl | 10.587 | | |
| 英訳 | 忠実英訳+In One Line+A2簡易化(UNTAGGED=X共有関数内のcall) | 1.037 | 1.5〜3.0 | 段落数retry 0 |
| 英訳 監視Leakage | `yr_s3_leak_b1b/a2` luna high 2 call(記録のみ) | 0.538 | 0.6 | 両levelフラグ0 |
| scaffold | Comment1〜3/Preview/タイトル/KP選定・Canonicalization(UNTAGGED 1.111)+gloss alignment(0.404) | 1.515 | 3.0〜5.0 | 見積より低い |
| 音声 | TTS(gemini batch 8.27)+ASR(OpenAI 4.55+Azure 6.88+その他0.02)、Adv 9.83+Std 9.89 | **19.72** | 15〜25 | retry 1回(Adv V2: 意味反転『wrong→right』をASR検査が検出して再生成)のみ。Local Rewrite・fallback・HR 0 |
| 組立・ページ・QA | ffmpeg/numpy/Playwright | 0 | 0 | |
| **本Trial 合計** | | **33.40** | 22.4(最大40.4) | 案件Cap55円・見積300円以下(7-7)内 |

## 2. 日次(2026-10-25 JST)
| 時点 | 日次累計(`daily_dev_cost_01.py`) |
|---|---|
| 着手時(10:57) | 721.68 |
| Phase 0後(11:10) | 735.47 |
| 全有料run完了後(12:50頃) | **831.30**(本Trial 33.40円+並行agent分の増加を含む) |
- 日次1,000円未満(残168.7円)。本Trialによる超過なし。

## 3. 見積差と量産単価への示唆
- 見積差: Tension+Closingが9.37円(見積1.2〜2.4円)と最大の外れ。理由=推論effort=highの出力トークン(5,525)。Opus確認済みの既存関数の既定値を継承したため変更せず実行(Style/Gate基準は変えない方針)。**量産時の削減余地**: effort=medium化の効果は未測定(本Trialでは追加Trialを行わない=磨き込み禁止)。判断候補ではなく、Production設計時(OPEN-484)の検討材料。
- 1セット総額の目安: R0側 25.489円(委任_25 BUDGET_LOG_OB_05)+本Trial 33.40円 = **約58.9円**(情報収集・整理のLLM化費用は未測定[人手25分、LLM 0円]のため含まない。RFは今回未実施)。70円/セット目標に対し、情報収集のLLM化が約11円以下なら目標内、それを超えると目標超過。
- 内訳の構成: 日本語補完(リード+Tension)10.6円、英語化+scaffold 4.1円、音声19.7円。音声(Std+Adv各約10円)が支配的で、X/Zと同水準。
