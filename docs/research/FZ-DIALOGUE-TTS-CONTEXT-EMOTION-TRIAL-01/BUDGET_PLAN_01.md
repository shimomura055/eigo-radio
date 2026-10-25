# BUDGET_PLAN_01 — 費用見積(FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01 委任_01、API 0)

- 上限: **追加API費用30円**(Trial固有、他案件の予算流用不可)。超過見込みはSTOP。Phase 0の実費=0円(API 0)。
- 為替160円/$(`er113_fx_paragraph_chunk_trial_01.py`/既存runner同一。先行調査は150円で約0.28円/call)。単価出典: `er005_output/cost_baseline_01/pricing_snapshot.json`(gemini-2.5-pro-preview-tts Standard 入力$1/M・出力$20/M、音声25 token/秒)。見積は`er118_..._01.py::est_tts_jpy`/`est_asr_jpy`、per-clip内訳は`er118_output/.../phase0/selection.json`ではなく`py er118_fz_dialogue_context_tts_trial_01.py plan`の標準出力と下表。
- 見積は入力token=文字数/4.5の近似。LLMとASRの単価は既存値の流用で、実費はPhase 1で`raw_usage_log.jsonl`から確定する。

## 1. 見積(円)

| 項目 | call数 | 見積(円) | 備考 |
|---|---|---|---|
| 感情情報LLM(gpt-6-luna、全8件一括) | 1 | 0.5(上限見込み1.0) | 入力約1.2k token・出力約1k token(推測) |
| ② TTS 1 take(8件) | 8 | **3.2**(1 clipあたり0.26〜0.79、平均0.40) | プロンプト約3,200字+音声1.7〜7.9秒。part3_c2(7.9秒)が最大0.79円 |
| ② 生成時ASR(Production生成関数内) | 8 | 保守的に2.0(典型は0.3前後) | `est_asr_jpy`は入力530/出力180 tokenの保守値 |
| **②1 take 合計(LLM込み)** | | **約5.7〜6** | |
| ② 2 take目(任意) | 8 | +5.2 | Phase 1でFable判断 |
| 対照arm `base`(①と同一style・新規1 take、8件) | 8 | +4.7(TTS 2.7+ASR 2.0) | take揺れとStyle効果の分離用(推奨) |
| retry予備(Production既定の最大3回のうち失敗時のみ。TTS分の+50%) | — | +3.0〜3.5 | 通常は0 |

| 構成 | 合計(保守) | 上限30円に対する余裕 |
|---|---|---|
| (A) ②1 take のみ | 約6(retry予備込み約7.5) | 22円 |
| (B) ②2 take | 約11.5(同約14) | 16円 |
| (C) **②2 take+対照①' 1 take(推奨案)** | 約16(同約19.5) | 10.5円 |

Cap超過見込み無し。生成関数は`PHASE1_GO.json`の`cap_jpy`(≤30)を超える前に各clip前でSTOPする。Phase 1着手時にFableが`PHASE1_GO.json`(managed_id/cap_jpy/arms)を置く。**案件見積300円以下・承認済みScope・個別Cap内(PM_GOVERNANCE 7-7)**なので追加のユーザー費用承認は不要。日次1,000円(JST)は他案件の当日実績を合算して確認する(Fable)。

## 2. 将来の量産単価への影響の概算(Production採用された場合の仮定。採用は未決)

- 追加TTS入力: CONTEXTブロック約900〜1,100字(≈200〜250 token)/call → 入力$1/Mで+約$0.0002=約**+0.03〜0.06円/call**(per-clip差の実測推定: 8件で+0.47円→+0.06円/件)。
- 追加LLM: 作品あたり感情情報1 call(約0.3〜0.5円、Advのdialogue clip数に依らずほぼ一定)。
- Z作品のdialogue clip数は1〜19(Adv。Open Window 17、After Twenty Years 19、Monkey's Paw 17、Magi 8、Melos 11)。1作品(Adv+Stdの2レベル)で**概算+1〜3円/作品**。目標70円/記事セットに対し+約1.5〜4%。ただしZ作品はVoicesのような70円目標の対象とは別の単価体系の可能性があり、正確な比較は採用判断時に別途算出する。
- retryが増える場合(leakage→再生成)はその分上振れ。Trialで`attempts`・leakage率を測り、Phase 1の結果に基づいて再見積する。
