# RUNTIME_EVIDENCE_01(FAMILY-X-COFFEE-NEW-TONE-PRODUCTION-E2E-01 委任_07、2026-10-11、Phase 2 実run)

結論: **Advanced=完成、Standard=HUMAN_REVIEW停止(full_story_part2)**。累計費用 JPY 20.73 / 上限 JPY 50(41.5%)。モデルは全て最新世代/Production正式モデル(EN=gpt-6-luna、TTS=gemini-3.8-flash-lite-tts、ASR=gpt-4o-mini-transcribe+Azure補助、RF=gpt-6-luna+gemini-3.5-flash-lite)。旧/下位モデルは不使用。

## 1. 実行コマンドと入力
- run dir: `er019_output/coffee_prices/run_e_tone_01/`(委任_05 builderで構成、`ja_writer/revision2.md` sha 742e7b6a…=マスター、`runtime_evidence.json` sha 241c0401…=書換え前と同一、git非管理)
- entertainment: `er019_family_x_entertainment_production_runner_01.py --slug coffee_prices --out-dir er019_output/coffee_prices/run_e_tone_01 --stage all --stop-after standard --budget-jpy 30 --approved-quality-master <repo>/docs/quality/ja_quality_masters/coffee_prices/E_master_meta.json`(日本語のWriter/B3/Research再実行なし。`research_ledger`/`storyline_b3`/`ja_writer/revision2.md`は既存再利用、ログ「[U-1] APPROVED_QUALITY_MASTER accepted」)
- audio: `er019_family_x_audio_production_runner_01.py --slug coffee_prices --run run_e_tone_01 --stage scaffold|tts|assemble|player --tts-backend speech_metadata_flash_lite`(Advanced/Standard両方をscaffold、tts→a2(both)→b1b、assemble/playerはb1bのみ)。TTS実行方式=Batch(Production既定)。出力: `er019_output/family_x_audio_production_wiring_01/coffee_prices__run_e_tone_01/`

## 2. U-1受理(案b)検証
| 項目 | 結果 |
|---|---|
| 受理記録 `ja_writer/approved_master_acceptance.jsonl` | 本runで1行追記(ファイル計2行: 1行目=委任_05乾式検証[課金前]、2行目=本run)。checks全PASS、decision_ref=ユーザー決定①(案b)、runner_git_head=1b35eb90 |
| `ja_writer/runtime_evidence.json` sha | 不変 `241c0401a8c74a416e75c31c7f3ae3303ada607ffead8b0057a3ec4b9edabeae`(chain_method=MAQ_TRIAL_W-1のまま) |
| `revision2.md` sha | `742e7b6a7fe43f1bd8e6106f…`(マスターsha) |
| ja_source記録 | `cost.json`/`entry_point`に `approved_quality_master:coffee_prices@742e7b6a7fe4` |
| Writer/B3/Research再実行 | なし(raw_usage_logにresearch/writer/b3 stage無し。stage=advanced/standard/risk_flagのみ) |

## 3. 各段のactual model_idと費用(JPY、登録単価)
| 段 | 実model_id(raw_usage_log) | 呼出 | 費用 |
|---|---|---|---|
| EN Advanced翻案 | gpt-6-luna (stage=advanced) | 2 | 0.26 |
| EN Standard | gpt-6-luna (stage=standard) | 1 | 0.24 |
| Risk Flagger A3/A4 (b1b, a2) | gpt-6-luna + gemini-3.5-flash-lite | 各4(計8) | 2.44(合計、Queue保存成功、issues b1b=5 / a2=4) |
| (entertainment計 = Advanced 0.26 + Standard 0.24 + RF 2.43) | | | **2.93** |
| 支援文scaffold(preview/comment/topic_intro/in_one_line/KP) | gpt-6-luna (stage=scaffold) | 16 | 2.26 |
| TTS | gemini-3.8-flash-lite-tts (Batch、voice Aoede/Charon) | 64 | 8.64 |
| ASR | gpt-4o-mini-transcribe(+azure-speech-stt補助8) | 69 | 4.68 |
| Local Rewrite等 | gpt-6-luna (stage=tts) | 7 | 0.84 |
| (audio計) | | | **16.43** |
| 実fallback probe(Step 2) | TTS gemini-3.8-flash-lite-tts / ASR gpt-4o-mini-transcribe | 8 | **1.37** |
| **合計** | | | **20.73 / 50** |

## 4. role × style 適用結果(speech_metadata.style、実送信値。`tts_generation_results.json` style_prefix/attempts_log.style_source)
| level | role | voice | style | 結果 |
|---|---|---|---|---|
| Standard | japanese_title / preview / comment_1-4 | Aoede | **J2(承認逐語)** | 全OK(各1試行) |
| Standard | KP日本語意味(rank1-5) | Aoede | **J2** | 全OK |
| Standard | full_story_part1/part3 | Aoede | **F1_5+減速連結(承認逐語+A2減速指示)** | OK(各1試行) |
| Standard | full_story_part2 | Aoede | F1_5+減速 | **STOPPED(Human Review)** §6 |
| Standard | topic_intro / in_one_line / KP英語 | Aoede | 従来値(`brief, clear, engaging…`/`concise, clear, landing…`/`Speak the following short phrase…`)=対象外role | OK |
| Advanced | preview / comment_1-4 | Charon | **E2_UPBEAT(承認逐語)** | 全OK(comment_2のみ5試行、§5) |
| Advanced | full_story_part1-3 | Aoede | **F1_5(承認逐語)** | 全OK(各1試行) |
| Advanced | topic_intro / in_one_line / KP英語・解説 | Charon/Aoede | 従来値(対象外role) | OK |
(`style_source`: 対象roleは全て `approved_role_style:*`。対象外roleは `caller_override:unrecognized`=識別helperが承認3 style以外を示すだけの表示名で、旧値のまま。)

## 5. fallback・再生成・Human Review
- **fallback発火: 1回**(Standard full_story_part2、attempt4=`minimal_fallback`)。`style_source=approved_role_style:EN_FULLSTORY_F1_5`、`tts_model_id=gemini-3.8-flash-lite-tts`、style_prefix先頭は承認F1.5逐語(旧`natural, clear, conversational`ではない)=委任_06の「fallbackでも承認Style維持」を実run確認。ただしfallback音声もASR TRUE_CONTENT_MISMATCHで不合格。
- Local Rewrite回復: Advanced comment_2(標準3回TRUE_CONTENT_MISMATCH→10分cool-down(600.003s)→Local Rewrite(canonical_text_before_local_rewrite保持)→attempt1 NORMALIZED_MATCH合格、style_source=EN_COMMENT_E2_UPBEAT)。Standard full_story_part2はLocal Rewrite文面でも不合格(§6)。
- 再生成回数(累積TTS試行): Advanced 合計試行 comment_2=5、他全segment=1。Standard full_story_part2=4(標準2+fallback1+LR再TTS1)、num_three=3、num_two=3(3回目でNORMALIZED_MATCH合格)、他=1。
- SCG(OPEN-258)発火: JA segmentのscg_infoはattempts_log内に記録(全segmentが1試行で合格したためSCG発火による救済なし)。
- 上限遵守: 同一segment総試行上限(標準2+fallback1)・cool-down・Human Review Lockは独自回避なし。

## 6. Human Review到達segment(ユーザー/Fable判断要)
1. **Standard `full_story_part2`**: `HUMAN_REVIEW_REQUIRED`(`a2/audit/review_lock_state.json`、`er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`に2行追記[15:19:10, 15:35:44])。全attempt ASR=TRUE_CONTENT_MISMATCH/ASR_VALIDATION_UNCERTAIN(原稿 "showed coffee cost 6.1% more" を音声が "show coffee costs / showed coffee costs" 等に読み分け、"2 numbers"→"two numbers"の数詞展開差を含む)。試行音声は `a2/narration/attempts/full_story_part2_attempt*_*.wav|json`(wavはgit非管理、ローカル保存)。**tone(承認F1.5+減速)に起因する品質劣化とは断定できない**: 同一テキストが標準2回・fallback(承認Style)・LRとも同種ASR不一致=本文の数詞/時制の読み分けに由来する可能性が高い。承認(REGENERATE_APPROVED等)は人間のみ。
2. **Standard shell `num_three`(Master Store由来)**: `HUMAN_REVIEW_REQUIRED`(3回とも ASR='三' TRUE_CONTENT_MISMATCH、OPEN-222の極短語言語ドリフト既知事象)。原因はnarration shellが**Master Storeから再利用されず再生成されたこと**: worktreeのMaster Store音声(`er006_output/master_audio_store_01/audio/*.wav`はgit非管理)が未配置で `cache_miss_reason=stored_audio_file_missing`(telemetry)。→ 是正(worktree限定): manifest/telemetryを`git checkout`で復元し、主ツリーのaudio wavをworktreeへ`cp`(新規は`-n`、再生成で上書きされた同一master_id 9件のみ主ツリー原本で上書き+sha照合)。KP英語5件は本runの新規生成のためmanifestへ追記。Advancedは復元後に実行し **shell 9件すべて `reused=True`(Champion再利用)**。Standardのshell(a2/narration内)は復元前の再生成版が残っており、Standard再開時は再利用に置換される。
3. Advanced: Human Review到達なし(全segment RESOLVED)。

## 7. 技術QA(既存Audio Validation Gate・Assemble Gate)
Advanced: tts_generation_results全segment `asr_verified=True`、review_lock全RESOLVED、key_phrase_source_gate=PASS(5/5)、assemble OK(duration 291.26s、clipping=False、peak 0.92035、headroom safety valve 未適用[threshold 0.98]、gain_report/timeline.json 出力済み)。Standardはassemble未実施(Human Review解消待ち)。
