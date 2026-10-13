# COST_ESTIMATE_01 (Coffee 1記事=Std+Adv、委任_02のFamily X音声化。本委任の費用=JPY0)

為替・単価の出典を明記。**推定値**(請求画面未確認)。未確認は「未確認」。USD/JPY=160(`er057_tone_trial_final_build_03.py:33`、`er019_family_x_audio_production_runner_01.py:1677 USD_JPY=160.0`)。

## 1. 単価出典

| 項目 | 単価 | 出典 |
|---|---|---|
| TTS `gemini-3.8-flash-lite-tts` Standard | 入力 $0.5/1Mtok、出力 $6.0/1Mtok(音声出力25tok/秒) | `er005_output/cost_baseline_01/pricing_snapshot.json`(source_url `https://ai.google.dev/gemini-api/docs/pricing`)、`er057_tone_trial_final_build_03.py:34 PRICE_IN, PRICE_OUT=0.5, 6.0`。Batch単価($0.25/$3.0)は**使わない**(T-2: STANDARD明示) |
| KP LLM `gpt-6-luna` | 入力 $0.10 / cached $0.01 / 出力 $0.50(/1Mtok) | `er009_n1_routing_governance_10_actual_model_cost.py:30`、`er006_model_routing_contract_01.py:50 SUPPORT_MODEL` |
| ASR `gpt-4o-mini-transcribe` | 入力 $1.25 / 出力 $5.0(/1Mtok) | `er057_tone_trial_final_build_03.py:35`(Trial推定式: 10tok/秒入力、出力=字数/4) |
| Azure Secondary ASR | 単価の直接出典は**未確認**。実績: Coffee最終組立で2呼出・音声計99.9秒=約JPY4.4(約JPY0.044/秒) | `docs/pm/delegation_log/2026-10-12_FAMILY-X-COFFEE-FINAL-AUDIO-ASSEMBLY-01_02.md`(実績値。単価式は未確認) |

## 2. 実績・推定(根拠付き)

### 2-1 KP再生成(LLM、gpt-6-luna)

- Trial実測(`er064_output/kp_integrated_opt_01/round1/cost_r1.json`、M2P0 Coffee): Std 1 job(選定+canonicalization/QA)=JPY0.76〜0.96(3 run)、Adv=JPY0.84〜0.94(3 run)。→ 期待値 Std 約0.9 + Adv 約0.9 = **約JPY1.8**(Round1の保守見積`EST std 1.185/adv 0.938`、`er064_kp_int_01_run.py:30`)。
- retry最悪(選定gate 2回x Redundancy retry 2回=3周): Std/Adv各最大約JPY3(1周約1.0x2回x…の保守上限)→ **約JPY6**。ハード上限=`KP_ARTICLE_COST_CAP_JPY=15`/記事(`er030_..._selector_01.py:79`)、超過でSTOP。
- M2は追加LLM呼出なし(`ROUND1_REPORT_01.md` §2)。Wiktionary照会は無料(公開API、時間のみ: 約43秒/記事x2)。
- Adv KP英語解説text(`er019_family_x_kp_explanation_01`、gpt-6-luna): 単価は上記だが実績呼出費用は**未確認**(推定JPY1未満、cost_logで実測)。

### 2-2 KP音声(TTS)

- Adv KP英語解説音声(P3 style、5件): 実績約JPY1.5(`FAMILY-X-COFFEE-FINAL-V5-PRODUCTION-WIRING-01_02.md`「想定費用 約JPY1.5」、前回Adv tts再実行)。
- KP英語phrase・日本語gloss(Std/Adv x 5件 x 2種=20 clip程度): clip単価の**直接実績は未確認**。短尺(2〜3秒、約60〜75出力token+入力)なら出力$6/Mtok換算で約JPY0.06〜0.1/take、検証ループ(`generate_key_phrase_component_verified`最大4 attempt)込みで**約JPY0.2〜0.3/clip(概算)**。20 clip → **期待約JPY4、最悪約JPY8**(未確認単価に基づく概算)。

### 2-3 Full Story(N01、Std/Adv x part1-3)

- Trial実測: N01 Std part1(117語)= 入力143tok/出力1,119〜1,173tok → TTS **JPY1.09〜1.14/take**、ASR(Trial推定)JPY0.22/take(`er057_coffee_tts_style_h_speed_05_listen/gen04/generation_log_04.jsonl`、`trimmed 44.8〜46.6秒`)。
- 語数(`er057_output/coffee_v5_pause_01/tts_input_texts.json`): Std 412語(117/161/134)、Adv 462語(131/179/152)。語数比で換算:
  - Std 1 pass: TTS 約3.8 + ASR(生成後)約0.8 + ASR(6%減速後の再検証)約0.8 = **約5.4**
  - Adv 1 pass: TTS 約4.3(語数比換算。Advは速いため過大見積り側) + ASR約0.9 = **約5.2**
  - 1 pass合計 **約JPY10.6**。
- retry: 標準経路2回+fallback1回(通算上限`PRODUCTION_MAX_TTS_ATTEMPTS=3`、`er011_human_review_lock_01.py:80`、減速後取り直しも同上限を共有=OPEN-270)。期待retry係数1.3(Coffee v5実績: comment_1の1回再生成等、少数)→ **期待約JPY13.8**、最悪(全segment 3回)→ TTS+ASR **約JPY32**。
- Azure Secondary(Tier3、ASR_VALIDATION_UNCERTAINのみ): 0〜2呼出 → **0〜約JPY6**(実績約4.4/2呼出ベース、単価式は未確認)。

## 3. 合計(Coffee 1記事=Std+Adv、Family X)

| シナリオ | KP LLM | KP音声 | Full Story(N01)TTS+ASR | Azure | 合計 |
|---|---|---|---|---|---|
| 期待 | 約1.8 | 約4(+解説約1.5) | 約13.8 | 0〜6 | **約JPY21〜27** |
| 最悪(retry上限) | 約6 | 約8(+解説約4.5) | 約32 | 約6 | **約JPY57** |

- 再利用するもの(再生成不要・費用なし): IN_ONE_LINE、Std Preview/Comment1-4(R2、承認済み)、shell/固定音声、japanese_title等(M2P0・N01の影響を受けない。同一text・同一styleのため`_generate_or_reuse`で再利用)。Comment/Previewを再生成する場合は追加費用が発生する(本見積に含めず、X-2確認事項)。
- 15-8(Production 1生成セット総原価)形式の表: 本件はCoffee 1記事の**部分再生成(KP+Full Story)**でありFamily Xの「1生成セット総原価」ではない。共通Research/Ledger・Writer費は本見積に含まない(既存生成物を再利用)。正式な1生成セット総原価は別途量産時に報告。

## 4. 上限提案

- `--budget-jpy 80`(runner Budget Guard、`er019_family_x_audio_production_runner_01.py` `assert_budget_ok`、既定150を明示的に下げる)、runごとのsoft stop JPY60(最悪見積約57に近づいた時点で停止し報告)。KP LLMは既存`KP_ARTICLE_COST_CAP_JPY=15`/記事を維持。
- 再生成が必要になった場合(Std/Adv全part再実行)の追加見込み約JPY14〜(期待)。上限を超える場合は停止してFableへ報告(自動継続しない)。
- 為替・単価変動、未確認のKP短clip単価・Azure単価はcost_logの実測で置換し、委任_02報告に実績を記載する。
