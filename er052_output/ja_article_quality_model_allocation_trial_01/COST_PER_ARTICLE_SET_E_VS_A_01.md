# COST_PER_ARTICLE_SET_E_VS_A_01: E案(B3/R0/R1/R2=gpt-6.1-sol)での1記事セット費用見積

管理ID: FAMILY-X-JA-MODEL-ALLOCATION-SOL61-PRODUCTION-WIRING-01 委任_03 / 2026-10-11 / read-only(課金API 0、コード・SSOT変更なし)。為替 **USD/JPY 160固定**(ログに為替の記録値はなく、cost.json・audio runnerが`USD_JPY=160.0`で計算。`er005_output/cost_baseline_01/pricing_snapshot.json`)。Sol単価=pricing_snapshot gpt-6.1-sol $2/$10(DEV/評価用登録、promotional期限は未確認)。

## 1. 「1記事セット」の定義
Family X正式構成 = **Standard(A2) + Advanced(B1B) の2 Level**。日本語記事(R2)は両Levelの共通原稿。含む工程: Research/Fact Ledger → B3 → 決定論producer → R0/R1/R2 → Advanced EN・Standard EN → Risk Flagger 4条件×2 Level → Review Queue → 支援文(Comment/Preview/Key Phrase/解説。scaffold) → KP選定(db_hybrid) → TTS → ASR/音声QA → Assembly → Player。出典: `er019_output/coffee_prices/run_l3_01`(Research〜Queue)+`er019_output/family_x_audio_production_wiring_01/coffee_prices__run_l3_01`(scaffold〜Player)。E案で変わるのはB3/R0/R1/R2のみ。他工程(Luna/Gemini/TTS/ASR)は不変。

## 2. 工程別内訳(円)
区分: 実測=ログ/cost.jsonの値、推定=根拠を併記。「対象」は集計に使った記事数/run数。

| 工程 | モデル・単価出典 | 実測/推定 | 対象 | coffee Production実測(A案) | E案での値 |
|---|---|---|---|---|---|
| Research | gpt-6-luna + web_search(12回、約1.6円/回) | 実測 | coffee 1 run | 21.96 | 同左(不変) |
| Fact Ledger | gpt-6-luna + web_search(14回) | 実測 | coffee 1 run | 24.88 | 同左 |
| B3 | A: luna / E: gpt-6.1-sol | 実測 | E=3記事 | 0.70 | 平均8.62(META 7.11/coffee 11.53/hormuz 7.21) |
| producer | 決定論 | 実測 | - | 0 | 0 |
| R0 | A: luna / E: sol | 実測 | 同上 | 0.54 | 平均7.48(8.37/6.74/7.33) |
| R1 | A: astra / E: sol | 実測 | 同上 | 18.16 | 平均2.89(2.20/4.18/2.28) |
| R2 | A: astra / E: sol | 実測 | 同上 | 19.66 | 平均3.65(3.87/4.48/2.59) |
| **JA 4段合計** | | 実測 | | **39.07** | **平均22.63(META 21.55/hormuz 19.42/coffee 26.94)** |
| Advanced EN | gpt-6-luna | 実測 | 3 run(coffee/META/semi、cost.json) | 0.35 | 平均0.32(0.26-0.35) |
| Standard EN | gpt-6-luna | 実測 | 同3 run | 0.38 | 平均0.41(0.23-0.63) |
| Risk Flagger(4条件×2 Level=8 call) | luna + gemini-3.5-flash-lite | 実測 | 同3 run | 2.42 | 平均1.79(1.11-2.42) |
| Review Queue | 決定論 | 実測 | - | 0 | 0 |
| 支援文(Comment/Preview/KP解説)+KP選定 | scaffold: gpt-6-luna 22-25 call(KP選定は`db_hybrid`でLLM費用なし) | 実測 | 2 run(coffee/META) | 3.46 | 3.5(3.46/3.58) |
| TTS | gemini-3.8-flash-lite-tts batch | 実測 | 2 run | 8.08 | 8.0(8.08/7.83、retry込み) |
| ASR/音声QA | gpt-4o-mini-transcribe(snapshot単価)+Luna cascade | 実測 | 2 run | 4.25 | 4.25-5.6(META はLuna cascade 1.42含む) |
| Azure STT fallback / Perplexity | azure $1/音声時間、perplexity sonar | **未計測**(ログにcostなし=0円計上) | META 17 call+1 call | 0 | 推定 Azure約1.9円(elapsed合計41.6秒を音声長の上限とみなす)、sonar 約2円以下(単価snapshot未登録) |
| Assembly / Player | 決定論 | 実測 | - | 0 | 0 |
| 技術QA(clipping/repetition/disfluency等) | 決定論+上記ASR | 実測 | - | 含む | 含む |
| 音声合計(scaffold+TTS+ASR) | | 実測 | coffee/META | 15.80 | 平均16.39(15.80/16.99) |

検算: coffee cost.json 89.055 = Research 21.96+Ledger 24.88+JA 39.065+EN 0.73+RF 2.42(丸め差あり)。audio 15.80=openai 3.55+gemini 8.08+asr 4.16(delegation_log RISK-FLAGGER-WIRING-01_14と一致、raw_usage_logをpricing_snapshot単価で再計算して一致)。META regen: cost.json 38.46(Ledger再利用、Research/Ledger 0)+audio 16.99(Azure/Perplexity除く)。semiconductor devconfirm 34.96(Ledger再利用、音声なし)。

## 3. 4つの数字のうち(1)(2)(E案、1セット=A2+B1B)
Research/Ledger費用はテーマ依存が大きいため、(a)Ledger再利用(Research 0)、(b)Research込み(coffee実測46.84)、(c)Research込み(過去10 runの中央値25.54)の3列で示す。

| | (a) Ledger再利用 | (b) Research込み(coffee実測) | (c) Research込み(中央値) |
|---|---|---|---|
| **(1) 通常時、retryなし** | **37.9**(JA 22.63+EN 0.73+RF 1.79+音声12.77) | 84.8 | 63.5 |
| **(2) 現実的平均(retry期待値込み)** | **41.5**(音声は実測平均16.39) | 88.4 | 67.1 |

(1)の音声12.77は**推定**: 実測音声費用から、retry分(ユニーク音声ファイル数に対する余剰TTS/ASR call)を除いて算出(coffee 13.75、META 11.78の平均)。
(2)のretry実績(実測、直近Production runの音声): 余剰TTS call率=ユニークfile比 coffee 7/37(19%)、META 18/39(46%、Azure fallback 17 callを併用)、プール33%(25/76)。上限は`PRODUCTION_MAX_TTS_ATTEMPTS=3`(er020)。Local Rewrite等のLuna cascade call: coffee 9 call/0.09円、META 14 call/1.42円。記号QA再実行: 走査16 run(Astra 7/Luna 5/Sol 3含む)で0件(0%、RESULT_02)=期待値0。ただしN小のため保守側(rule of three上限19%)×(R0+R2再実行11.13)=最大約2.1円を(2)へ上乗せし得る(その場合(a)=43.6)。EN再生成(structure retry)は3 run×2 level=0/6。retry実測平均の加算分は音声+3.6円(16.39-12.77)。
retry率に含めない運用事例: Standard単独再生成(coffee 1.49円、1回)、TTS単独再実行(coffee 4.09円、1回)。

**Research+Ledger(実測、円)**: coffee 46.84。参考(theme依存の幅): b3_wiring run_01 28.74、gpt6_wiring run_02 16.55、open233 17.89、stage_r Trial 6 run(byd 12.97/central_bank 22.33/inbound_tourism 56.82/openai_copyright 31.83/semiconductor 14.88/streaming 34.46)。10 run: 最小12.97・中央値25.54・平均28.33・最大56.82(うち9 runは旧Trial/別wiringでモデル構成未精査=参考値)。

## 4. (3) 費用が高くなるケース(推定、E案、(a)基準からの加算)
| ケース | 加算 | 根拠 |
|---|---|---|
| Research/Ledger長文・多検索 | coffee 46.84→最大56.82で+約10(Research単位で12.97-56.82の幅) | 上記10 runの実測 |
| R2再実行1回(記号QA、E) | +3.6(最大+4.48) | E R2実測。Writer側上限は既存機構どおり1回 |
| R0〜R2再生成(B3再利用) | +14.0 | E平均 R0 7.48+R1 2.89+R2 3.65 |
| JA 4段全再生成 | +22.6 | E平均 |
| Sol出力token増(保守cap) | JA 4段が最大約50(+27.4) | Phase3 coffee Eの保守cap=50(RESULT_02、実測26.94の約1.9倍) |
| ASR/TTS fallback上限(全segmentが3 attempt) | 音声 約32.8(実測平均比+16.4) | coffee 34.5、META 31.0(per-call実測単価×ユニークfile×3+Luna cascade 2倍)。実際は全segmentが上限に達しない |
| Local Rewrite複数(10 segment程度) | +約2.7 | TTS+ASR 1 attempt約0.27円/segment×10(推定) |
| RF再実行/Flag多(Flag多は人間Review Queue、課金はRF呼出回数) | +1.8(再実行1回) | RF平均1.79、8 call |
| EN regen(Advanced+Standard) | +0.7 | 0.32+0.41 |
| **全部乗せ上限(Research最大)** | **約145**((a)基準で約88) | 56.82+JA 50+EN 1.46+RF 3.58+音声32.77。同時発生しにくい上限値(推定) |

## 5. (4) 旧A案 vs 新E案
A案 実測平均 ¥37.36(META 35.645+coffee 39.065の2記事)、E案 3記事平均 ¥22.64(META 21.55/hormuz 19.42/coffee 26.94、本表は丸めで22.63)。

| 比較 | A案 | E案 | 差額 | 削減率 |
|---|---|---|---|---|
| JA 4段(依頼の比較: A 2記事平均 vs E 3記事平均) | 37.36 | 22.64 | -14.72 | **-39.4%** |
| 同一記事比較 META | 35.64 | 21.55 | -14.09 | -39.5% |
| 同 coffee | 39.07 | 26.94 | -12.12 | -31.0% |
| 同 hormuz(A新規実測29.945) | 29.95 | 19.42 | -10.53 | -35.2% |
| JA 4段 3記事平均(A 34.88 vs E 22.63) | 34.88 | 22.63 | -12.25 | -35.1% |
| **1セット全体 (a) Ledger再利用・retry込み実測平均** | 56.3(A:37.36+EN 0.73+RF 1.79+音声16.39) | 41.5 | -14.7 | **-26%** |
| 1セット全体 (b) Research込み(coffee実測46.84) | 103.1 | 88.4 | -14.7 | -14% |
| 1セット全体 (c) Research込み(中央値) | 81.8 | 67.1 | -14.7 | -18% |
| 参考: coffee実run(Production実測総額) | 104.86(89.06+15.80) | 92.73(JA段差し替え推定) | -12.1 | -11.6% |

1セット全体の削減額は約12〜15円で、JA部分の35〜39%削減は全体では約12〜26%に薄まる(Research/Ledgerと音声が不変のため)。

感度(仮定、根拠なし): Sol単価が上がった場合、JA 4段のE案がA案37.36と並ぶ単価倍率は約1.65倍。参考として旧世代gpt-5.6-solの登録単価は現行6.1-solの2倍($4/$20、promotional脚注あり)。6.1-solに同種の期限があるかは未確認。

## 6. 未計測・要確認
1. Azure STT実請求(Azure fallback 17 call、ログにcostなし=0円計上。上記は音声長上限からの推定約1.9円)。Perplexity sonar費用(snapshot単価なし)。
2. gpt-6.1-solのpromotional期限・期限後単価(未確認)。
3. thinking/reasoning token計上差: ログoutput_tokensはreasoning込み(COST_VERIFICATION_01)。Solでの請求上の扱いは実請求との突合未実施。
4. Research/Ledger費用のテーマ依存(coffee 46.84は10 runの上位2位、中央値25.54)。旧Trial runのモデル構成は未精査。
5. Sol出力tokenの変動: E実測はN=3(1テーマ1回)。同一入力の複数回試行がなくrun間分散は未測定。
6. retry率の標本: 音声2 run(coffee/META)のみ、記号QA再実行0/16。META runの高retry(46%)は個別事象の可能性。
7. 為替はUSD/JPY 160固定(実勢未反映)。OpenAI/Gemini実請求書との突合は未実施(ログ値からの再計算)。
8. E案のProduction配線後(routing contract・単価登録後)の実run未実施。本見積はTrial 3記事のJA段実測+既存Production run実測の合成。
