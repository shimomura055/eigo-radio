# EVIDENCE_01 — X Std / Y Std・Adv の正式runtime evidence(委任_02、2026-10-26 JST 16:11〜16:28)

Status候補(事実のみ。PRODUCTION_WIRED判定はFable): X Std=EVIDENCE_COLLECTED / Y Std=EVIDENCE_COLLECTED(複数段落dev入力で正式生成関数が発火。**現行本文契約では正式CLI経由では構造的に不発火**) / Y Adv=EVIDENCE_COLLECTED(同条件) / X Adv・Z Adv=既存evidence(`FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01/RUNTIME_EVIDENCE_01.md`、本委任で回帰なし=Adv不変の機械確認[§6]) / **Z Std=未実装・未取得(次委任)**。
使用モデル: TTS=`speech_metadata_flash_lite`(gemini-3.8-flash-lite-tts、Production承認backend、モデル比較なし)、ASR=gpt-4o-mini-transcribe(+Azure STT)、`TTS_EXECUTION_MODE=STANDARD`。評価用の新旧モデル比較ではなく承認済み方式の配線確認(最新モデル原則25節の対象外)。

## 1. Family×レベル表(runtime列は実測値)
| Family×Level | 入力 | 経路 | 分割位置/chunk数/語数 | 0.2秒 | chunk別減速 | TTS call | 再利用 | Gate | 費用 | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| X Std | 既存Std記事『英国の電車マナー』`uk_train_speaker_playback__run_nws_02`(旧方式Std結果)を新規out-dir `…__run_stdchunk_ev_01`へ複製(`--out-dir`で新規。source=run_nws_02は読取のみ) | 正式runner CLI `--stage tts --level a2`→`--stage assemble --level a2` | Part1 4=[66,14,31,34] / Part2 3=[56,49,42] / Part3 3=[35,52,36]、計10 chunk、全て`boundary_kind=paragraph` | 親wav=減速後chunk wav+**ちょうど4800サンプル(0.2秒)の完全無音**(整数サンプル一致3/3)。組立後wav内の0.2秒gap 7箇所を実測(長さ0.200秒、gap内max|x|=0.00034≒48kHz変換のring) | 全10 chunkで`slowdown_applied=True`、比 1.0568〜1.0600(基準1.03〜1.09) | Gemini TTS **11回**(10 chunk+Part2 chunk2の取り直し1回)、ASR 22回(chunkごとに減速前+減速**後**の再検証) | **同引数で`--stage tts`を再起動→新規API 0回**(raw_usage_log 34行→34行、費用6.20円→6.20円、全chunk `reused_from_previous_run=True`)。既存非本文segment(KP/日本語等)も再利用 | style_profile_gate=PASS(21 checked)、共有Gate・追加Std chunk減速Gate PASS、assemble `status=OK` 321.869秒 | 6.20円(gemini 3.91/openai_asr 1.57/azure 0.72) | EVIDENCE_COLLECTED |
| Y Std | 実Y run `redelivery_fee/run_01`を新slug `redelivery_fee_stdchunk_ev`/`run_ev_01`へ複製し、`y_voice_2`に**文境界で空行2つ**を挿入したdev入力(`parts.json`、本文は空白差以外同一を検証) | 正式な生成関数`ya.generate_y_a2_segments`+正式Gate`ya.y_style_gate`+正式組立`ya.assemble_level`(runnerと同条件のbuild_real_context。**CLIを使えない理由は§3**) | `y_voice_2` 3 chunk=[54,67,36]語、他7 segmentは1段落(不分割) | 親wav=chunk連結+4800サンプル無音(整数一致)、組立後gap 2箇所0.200秒(gap内max|x|=0.0) | 3 chunkとも`slowdown_applied=True`、比 1.0585〜1.0595 | Gemini TTS 3回、ASR 6回(各chunk 2回) | (resume・再利用0確認は X Std で実施) | `y_style_profile_gate`=PASS、assemble OK 350.374秒 | 1.77円(うちNER 0.01) | EVIDENCE_COLLECTED(複数段落dev入力) |
| Y Adv | 同上(b1b) | 同上 | `y_voice_2` 3 chunk=[55,63,37]語 | 親wav整数一致、gap 2箇所0.200秒(gap内max|x|=0.00034) | (Advは減速対象外) | Gemini TTS 3回、ASR 3回(減速後再検証なし) | — | PASS、assemble OK 326.8秒 | 1.50円 | EVIDENCE_COLLECTED(複数段落dev入力) |
| X Adv | 既存(uk_train run_chunk_01) | 既存 | 10 chunk | 実測済み | — | — | — | — | — | PRODUCTION_WIRED(従来)。本委任で**不変を機械確認**(§6) |
| Z Adv | 既存 | 既存 | — | — | — | — | — | — | — | PRODUCTION_WIRED(従来)。`er063`未編集 |
| Z Std | — | 未実装 | — | — | — | — | — | — | — | **次委任**(DESIGN_02 §3-§4) |

## 2. 実Y記事の不発火(事実の記録)
`er121_output/family_y_std_chunk_evidence_01/real_article_non_fire_record.json`(= `docs/research/…/evidence/y_std/real_article_non_fire_record.json`): 実Y記事`redelivery_fee/run_01`のStd/Adv全8 segmentを現行plannerへ読取りだけで通すと全て`chunked:false, paragraphs:1`(`reason=paragraphs=1<2`)。既存の決定記録: b1b=`chunk_tts_decision.json`(`chunked:false, paragraphs:1`)、a2=2026-10-26以前の旧記録(`not_applied_reason`あり、当時Standardは分割対象外)。**追加費用0**。

## 3. 構造的理由(Opus論点6の具体化・Fable向け重要事項)
Yの正式runner `stage_tts()`(`er121_family_y_runner_01.py:970-`)は毎回 `ya.write_level_inputs()` で `<level>/parts.json` を**記事本文(translate/<level>.md)から再生成**する。記事は `split_y_article()`(`er121_family_y_structure_01.py:152-183`)が『段落5固定、Voice段落=紹介行+本文1行』を要求し、本文に空行を足すと `Y_ARTICLE_PARAGRAPH_COUNT: 段落が5でありません(=6)` で契約違反STOPになる(実演: `real_article_non_fire_record.json`)。よって:
1. 現行の本文契約では、**正式CLI(`--stage tts_a2/tts_b1b`)から複数段落のsegmentを入力する手段がない**=Y Std/AdvのChunk配線は「配線済み・現行契約では発火経路に到達しない」(Opus論点6どおり)。
2. 本委任のevidenceは、runnerが`stage_tts`内で呼ぶ**正式な生成関数・Gate・組立**を、runnerと同じ条件(`build_real_context`=STOP確認・RESTART_STORM/RUN_LOCK・予算guard・cost logger・STANDARD・only_segments_scope・同一guard)で直接呼ぶdriver(`tools/y_chunk_evidence_driver_01.py`)で取得した。バイパスしたのは`write_level_inputs`(parts.jsonの再生成)だけで、新しい処理・Gate回避はない。公開dir・run_01は無変更。
3. これは仕様候補ではなく承認済み仕様の到達性に関する**事実の報告**(Y本文契約の変更=Voice本文を複数段落可にする、は未承認のまま。OPEN-527)。`判断候補`: 無し(分類=ユーザー判断要の新規論点ではなく、既存OPEN-527・承認文『実記事が1段落のため不発火ならその事実を記録する』で既判断=A既判断)。

## 4. 境界の可聴無音(Opus論点1の実測。Gateにはしていない)
定義: 前chunk末尾の無音+0.2秒+次chunk先頭の無音(閾値|x|≤100/32768≒-50dBFS)。`measure/*.json`。
| 対象 | 境界数 | 可聴無音 平均(最小〜最大) | Std推定(`_original.wav`の末尾/先頭無音×1.06+0.2秒)との差 |
|---|---|---|---|
| X Std(uk_train Std記事) | 7 | **0.743秒**(0.654〜0.815) | 実測−推定 = −0.028〜−0.003(平均−0.014)。推定は実測よりわずかに長め(閾値判定の差)=margin×1.06の見立てと整合 |
| X Adv(uk_train Adv記事、別本文) | 7 | 0.666秒(0.564〜0.726) | — |
| Y Std(dev入力 `y_voice_2`) | 2 | 0.647秒(0.635〜0.659) | 推定との差 −0.008/−0.014 |
| Y Adv(dev入力、訳文が異なる) | 2 | 0.634秒(0.619〜0.648) | — |
- Std−Advの差: X +0.076秒、Y +0.014秒。**Xは本文が異なる(Std/Advは別記事)ため同一境界の比較ではなく、本文差の分散を含む**。Yは同一Voice・近い語数。差の方向はmargin×1.06(各側0.16〜0.37秒が約6%伸びる=0.02〜0.04秒)と整合し、**追加ポーズ自体は全境界でちょうど0.2秒**(pad区間は全て完全無音、整数サンプル一致)。承認範囲内(Opus論点1、補正なし)。
- pad端の段差・クリック: 全境界でpad直前/直後5ms窓のmax|x|≤25/32768(0.00076)、境界サンプル間の最大|Δx|≤9、padは全て0。**段差・クリックなし**(`measure/x_std_run_stdchunk_ev_01.json` boundaries[].peak_*/step_*)。

## 5. 費用(旧方式Std runとの比較)
- 新方式X Std: 6.20円(10 chunk、11 TTS call、うち取り直し1)。
- 旧方式(run_nws_02のStd本文3 part、全part再生成相当を同単価換算で推定): 約16.1円(gemini 約9.0/asr 約2.7/azure 約4.4)。旧方式はpart単位の取り直し(8 TTS call・生成音声370秒)に対し新方式はchunk単位(11 call・生成音声162秒)で、**取り直しの再生成範囲が狭い**ため。ただし旧runの取り直し回数は偶然差を含むため、**構造的な削減量としては主張しない**(`measure/x_std_cost_compare_old_vs_new.json`の方法=新runの実費をproviderごとのtoken/音声秒で按分。旧runに個別cost記録なし)。
- 追加LLM call 0(本番経路)。量産単価への影響は、call数増(chunkごと)に対しASR課金が音声長比例のため限定的(X Std実測で旧推定を下回る)。

## 6. Adv不変(R4)
- 旧(bb578265c worktree)と現ツリーで同一driver(mock生成器)を実行し、**X Advのresults json(正規化)・narration wav全て・chunk plan・evidence・gain report・timeline・合成wav、Y Advの単一段落/複数段落両方のresults・narration wav・chunk plan・gain/timeline・合成wavがバイト一致**(`adv_invariance/compare_result.json` `audio_and_results_byte_identical_all=true`)。差分は`chunk_tts_decision.json`の`approval_ref`/`note`の注記文言2点のみ(監査表示、音声無関係)。golden=`golden/y_b1b_chunk_tts_decision_golden_01.json`。
- `git diff bb578265c`の各差分箇所を関数単位に機械分類(`adv_invariance/hunk_classification.json`): UNCLASSIFIED=0。共有(a2とAdvの両方を扱う)関数7件(MANUAL_REVIEWED)の人手レビュー理由を記載(M1/R3(c)はAdvにも効く意図的是正だが正常入力ではno-op)。

## 7. 取得できなかった/未確認の事項
- Z Std: 未実装のためruntime未取得(次委任)。
- Y: 正式CLI経由の発火は不可能(§3)。
- X/Yとも「同一記事のAdv実測との差」はXで本文が異なる別記事比較(§4注記)。
- 公開済み音声・manifest・公開ページは一切変更していない(新規out-dir/新slugのみ)。
