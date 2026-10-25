# DESIGN_01 — 改善方式(文脈+感情)の設計 / DEV実装(FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01 委任_01、API 0)

> 注(委任_02、2026-10-25): §2のStyle追記ブロック全文例・§3のfallback文・§6のleakage検査は、Opusレビュー反映で**§9の通り改訂済み**。§2/§3/§6の旧記述は履歴として残置(現行仕様は §9 と `er118_...py`、事前登録は `PREREGISTERED_CRITERIA_02.md`)。

実装: `er118_fz_dialogue_context_tts_trial_01.py`(DEV/Trial専用)、test: `er118_fz_dialogue_context_tts_trial_01_test_01.py`(21 test PASS、API 0)。`py`ではなく`.venv/Scripts/python.exe`で実行。
到達上限: VALIDATED(Production採用・実装は対象外)。Production file / Prompt / flag / 再利用仕様の変更0。

## 1. ①と②の定義(差は『Styleへの文脈・感情情報の追加』のみ)

| | ①現行 | ② 改善 |
|---|---|---|
| 本文(TEXT TO SPEAK) | `_norm_for_tts(clip.text)`(引用符つき) | **逐語同一**(testで区画ごと一致を検証) |
| Voice / model / 実行mode / speech config / 生成関数 / ASR・Gate | 同一(§4) | 同一 |
| STYLE区画 | `ENGLISH_STYLE_PREFIX`(sha `add26d27…`、1842字)そのまま | ①の文字列 + 空行 + **CONTEXTブロック**(下記)。①の文字列は1文字も変えない(testで`startswith`検証) |

CONTEXTブロックはStructured Separation(`build_tts_prompt`)のSTYLE区画の内側に置く。STYLE区画は『読み上げ禁止・演出の説明のみ』と明示された既存区画で、CONTEXTブロック自身にも「このブロックのどの語も読まない」を冒頭と末尾に明記する(二重)。TEXT TO SPEAKは当該セリフのみ(testで『対象セリフ本文がCONTEXTに含まれない』『TEXT区画=整形後の本文のみ』を検証)。

## 2. ②のStyle追記ブロック(全文例: `full_story_part2_c7`、感情欄はPhase 1のLLM出力が入る。Phase 0の例は`<LLM:…>`プレースホルダ)

```
CONTEXT FOR THIS ONE LINE (delivery reference only. Do NOT read, quote, or paraphrase anything in this CONTEXT block aloud. Only the TEXT TO SPEAK section is spoken.)
Speaker of this line: Della.
Speaker's state of mind: <LLM: speaker_state>          # Phase 1: gpt-6-luna、根拠引用つき、最大30語
Scene: <LLM: scene>                                    # Phase 1: 最大25語
Narration just before: "By seven, dinner was nearly ready. Della had curled her short hair, but she kept returning to the mirror."
Spoken line after: Della: "I sold it, Jim. I couldn't let Christmas come without giving you something. It'll grow again!"
Narration just after: "she whispered."
Stage direction in the story (manner of speaking or acting): "Della had curled her short hair, but she kept returning to the mirror." / "she whispered."
Use this only to choose a natural tone, pace, and energy for this one line, as a good audiobook reader would. Keep the delivery natural and believable: let the feeling described above come through in the voice, without theatrical over-acting and without adding any emotion beyond what is described. Do not read any word of this CONTEXT block.
```
(`How this line answers the previous one: …`行は直前セリフがあり、LLMが返答関係を根拠つきで述べられた場合のみ入る。`Spoken line before:`行は直前セリフが範囲内にある場合のみ。)全8件の決定論部分は`er118_output/.../phase0/selection.json`の`context`、例示は`phase0/style_example_part2_c7.json`。

## 3. 感情・文脈情報の作成方法(指示の要件への対応)

指示: 既存の文章・構造化データを最大限活用し不要なLLM呼出を避ける。

**(a) 決定論(LLM 0)で作る項目**: 話者表示名(`SPEAKER_DISPLAY`)/直前2・直後1セリフ(`segment_plan`)/直前直後の地の文/演出語を含む文(語彙regexで抜く。文は原文逐語)。『相手の発言への反応』の素材(直前セリフ)も決定論で同梱。感情語彙の創作はこの段では一切無い。
**(b) LLMで作る項目(1 call、全8件一括、gpt-6-luna、JSON schema)**: 話者の感情・心理状態(≤30語)、場面(≤25語)、直前セリフへの応答の仕方(≤25語、無ければ空)。理由: 『悲しみと希望が混じった静かな祈り』のような**状態の言語化**は決定論では作れず、手書き(Fable/Sonnet)は再現性が無いため。
 - 入力は(a)の項目のみ(`emotion_user_message`、約4,000字)。Prompt(developer)全文は`er118_fz_dialogue_context_tts_trial_01.py::EMOTION_DEVELOPER`、schemaは`EMOTION_SCHEMA`。**prompt+schema sha256=`d014efea023a3c01d1a6b2b81122b5ed335fa2d1d5e6e91b7374fb8aa47f2523`**(`emotion_prompt_sha()`)。入力message(Phase 0時点の8件)sha256先頭=`7f7a72854597`。
 - 創作防止(決定論検査 `validate_emotion_items`、LLM再呼出なし): 根拠引用(evidence)が当該文脈の原文(対象セリフ・前後セリフ・前後の地の文)に**逐語一致**しない→項目破棄/語数超過→破棄/文脈原文に無い固有名詞(文中の大文字語)を含む→破棄/`has_explicit_cue=false`→中立fallback文(`EMOTION_FALLBACK_STATE`)。破棄・fallback時は感情欄を中立文に置換し、`status`(ACCEPTED/NO_EXPLICIT_CUE/DISCARDED)と理由を保存する。Madame『Twenty dollars.』は感情の明記が無いため、中立(対照)になることを期待している。
 - 費用: 入力約1.2k token・出力約1k token(推測)→ 約0.3〜0.5円。`run_emotion_llm`はGO・STOP確認後にのみ1回実行し、raw応答・検査結果・費用を`llm/emotion_notes.json`に保存。

## 4. 生成条件の同一性(確認方法つき)

| 条件 | ①の実績 | ②で同一にする方法 | 検証 |
|---|---|---|---|
| model | gemini-2.5-pro-preview-tts | `p9a.ENGLISH_MODEL_NAME`(生成関数内) | requestログの`model`を保存・照合 |
| mode | STANDARD(同期) | `capture_tts_requests`が`TTS_EXECUTION_MODE=STANDARD`をTrial processに限り設定 | requestログの`tts_execution_mode` |
| Voice | Zephyr/Kore/Algieba | `voice_assignment.json`→`tts_voice()` | testで①の実Voiceと全8件一致 |
| speech config / sampling | `language_code=en-us`+prebuilt voice、temperature未指定 | 同一call関数(`make_tts_call_fn_for_model`)を既存`make_batch_tts_call_fn`経由で通す | requestログの`speech_config`/`temperature=None`を保存。①の実行時request記録は無い(Productionが保存しない)ため**コード経路の同一性**で担保 |
| 生成関数・ASR・Gate・retry | `generate_voice_body_wide_margin`(最大3回、ASR cascade、Repetition QA) | 同関数を`style_prefix_override`のみ変えて呼ぶ。`er109 family_scope("Z")`+`with_secondary_run`で包む(run scope同一) | result.jsonに`attempts_log_n`/`asr_judgement`保存 |
| 本文 | 同一 | `_norm_for_tts` | testで①②TEXT区画一致 |
| 速度加工 | Advはatempo=1.06を後段で適用 | ②は**加工前の原音**を①の`*_original.wav`と比較(試聴ページも両方とも加工前・同一target_rms) | 試聴は『速度加工前同士』(最終公開音声の速度は①②共通に後から掛けられるため差の要因にならない) |

**残る交絡**: (i) ①は2026-10-24の過去takeで、②は今回の新規take。TTSは同一入力でもtake毎に揺れるため、差のうち『Style効果』と『take揺れ』を分離できない。→ **対照arm `base`(①と同一のstyleで新規1 take、8件、約4〜5円)**をPhase 1で提案する(`gen --arm base`。Fable判断・予算内)。(ii) モデルの更新有無は外部要因で、対照armが同時に検出する。

## 5. 生成・記録(`generate_arm`)

- 1セリフ=1 call(retryはProduction既定の通算最大3回まで。通常1)。各セリフ: `gen/<arm>_t<take>/<clip>/request_full.json`(**実際に送ったprompt全文・prompt sha256・model・voice・speech_config・mode・temperature(未指定)・http timeout**。Productionが保存しない点を補う)と`result.json`(期待promptとの一致フラグ、ASR、classification、attempts、trim、Trial用reuse key、所要時間)。
- 停止条件: 1clipが`status!=OK`で打ち切り(自動再実行なし)、個別Cap(`PHASE1_GO.json cap_jpy`≤30)到達でSTOP、arm/GO無しは起動拒否、protected(Production音声/results/各store)のsha256が変化したらsummaryに`STOP`。
- 副作用隔離: `redirect_production_sinks(OUT_DIR/sinks)`(attempt履歴・HR queue・telemetry・Ledgerコピー・Local Rewrite出力先をTrial dirへ)。

## 6. 検証(`analyze`系関数、API 0。Phase 1生成後に実行)

1. 本文が正確に発話: Production ASR(生成関数内)の転写を`verbatim_check`(トークン一致・類似度)で再照合。
2. **余分な文脈の読み上げ(leakage)**: `leakage_check` = 転写の語数超過(>3語)/CONTEXT専用語(`context, stage, narration, speaker, scene, state, spoken, reference, block, delivery, audiobook, theatrical`が本文に無いのに出現)/CONTEXT文との3〜5語連続一致(本文内の一致は除外)。Productionの長さ検査(本文+15字)は小さな混入を通すため別途必要。
3. 長さ・RMS・F0範囲(p10-p90半音)・話速・最長中間無音(`analyze_wav`。無音は`er113.measure_wav`の既存実装)。**これらは粗い機械指標で、感情の自然さの代替ではない(聴感はユーザー)**。
4. 既存品質検査: Repetition QA等は生成関数内で①と同条件に適用済み(result.jsonに保存)。
5. 発音悪化: ASR一致+固有名詞(Della/Jim)の転写、ユーザー試聴。
6. ①②のtarget_rms統一→mp3化(`export_mp3`、target_rms=Magi Adv実組立の0.08425、`compute_gain_for_target_rms(max_peak=0.95)`)。

## 7. 試聴ページ

`user_test/fz_dialogue_context_trial_01/index.html`(noindex)。8枚のカード=日本語の場面説明/話者・カテゴリ/英文/前後の会話(折りたたみ)/**A 現行・B 改善の再生ボタンを同じ行に並置**(ワンクリックで切替)。開発者向け詳細(Style全文・ASR・leakage・機械指標)は`dev_details.html`へ分離。Phase 0では②欄は『未生成(Phase 1で生成)』表示でダミー音声を置かない(testで検証)。①のmp3(8本)は生成済み(既存音声のtarget_rms統一のみ、API 0)。**Phase 0ではユーザーに提示しない**(②未生成のため。作業ツリーにuntrackedで保持し、Phase 1完了後に生成・提出)。

## 8. 将来のProduction化時に必要になる変更(参考。本Trialでは実装しない)

`build_reuse_key`のdialogueにcontext/style hash追加(再利用仕様の変更=ユーザー承認+Opus条件A)/文脈・感情抽出のrun段組込み/leakage検査のGate化(新Gate=ユーザー承認)。DEV結果がVALIDATEDでもこれらは採用判断後。

## 9. 改訂履歴(委任_02、2026-10-25。Opus独立レビュー `OPUS_REVIEW_01.md` の M1〜M6・R1〜R4 反映。LLM・TTS未観測)

事前登録は `PREREGISTERED_CRITERIA_02.md` で置換。以下が01からの差分(実装 `er118_fz_dialogue_context_tts_trial_01.py`、test 43件PASS)。

| ID | 反映内容 | 実装箇所 |
|---|---|---|
| M1 | `leakage_check` を difflib アライメント方式へ差替え(余分token連続長≥2、またはCONTEXT専用語に該当でflagged、余分token有で needs_listen)。全attemptのASRを検査し `leakage_any_attempt`/`leakage_final` を分離。base armにも適用。単語境界(token単位)。長さ補助フラグ(>1.4×median[①,base]かつ+0.6秒超) | `leakage_check` / `leakage_all_attempts` / `length_listen_flag` |
| M2 | NO_EXPLICIT_CUE/DISCARDED/None のとき `Speaker's state of mind` 行自体を出さない。旧 `EMOTION_FALLBACK_STATE`(「deliver it plainly」=平板化指示)を撤去 | `validate_emotion_items` / `build_context_block` |
| M3 | CONTEXT_HEAD/TAIL をOpus差分の文言で逐語置換。演出文の逐語行を撤去し `Manner words from the narration: ...` 行のみ。会話タグ(小文字始まり5語以下の文)は逐語で入れない。前後セリフは引用符なしで `Spoken line before (said by X; not part of this line): ...` | `CONTEXT_HEAD`/`CONTEXT_TAIL`/`build_context_block`/`is_dialogue_tag` |
| M4 | 事前登録02(Status 3値写像、(d)補助、clip別主指標、完全分離、3/5・1以下、逆向き記録) | `PREREGISTERED_CRITERIA_02.md` / `evaluate_trial` |
| M5 | `comparison_valid`(final instruction_type≠minimal_fallback かつ最終実送信prompt shaが期待値一致)、`n_tts_calls_undercount_possible`、1 clipがNGでも中断せず続行(中断はcap・protected diff・STOP通知のみ) | `comparison_validity` / `generate_arm` |
| M6 | `EMOTION_DEVELOPER` に rule 8〜10 追加、強度語(語幹)deny→`DISCARDED(intensity_word)`、`llm/emotion_review.json`(Fable判定 accept/discard。未設定だとctx armの有料生成を拒否) | `EMOTION_DEVELOPER`/`INTENSITY_STEMS`/`load_reviewed_notes` |
| R1 | 3armを同一セッションで `ctx_t1 → base_t1 → ctx_t2` 連続実行(`gen-session`)。TTS model名を記録(SDK応答のmodel_versionはProduction wrapperがbytesのみ返すため取得不能=base armの①との差で検出する旨を記録) | `run_session` / `SESSION_ORDER` |
| R2 | **可能**。速度加工は純関数 `er008_a2_postprocess_slowdown_01.apply_a2_slowdown(src,dst,pct)`(ffmpeg atempo、API 0)で、Production Adv会話が使うpct=`er063.Z_ADV_DIALOGUE_SLOWDOWN_PCT`(atempo=1.06)をそのまま呼べる。試聴の主音声は最終相当音声(加工後ASR再検証なしは限界として報告) | `make_final_equivalent` |
| R3 | er113のrepo全体mtime走査(`scan_new_files`)を流用(除外dirに本Trial出力先を追加)。結果は各armのsummaryに記録(suspiciousの扱いはFable) | `scan_repo_mtime` |
| R4 | 試聴ページ: 音量注記、A/B/A'/B'の名称、各カードにLLM出力(状態・場面)の日本語短い要約欄(`emotion_review.json` の `summary_ja`、accept時のみ表示) | `build_page` |

最終 EMOTION_DEVELOPER sha256 = `035b54ff44b28d645e831cd0266c47fd2691f0268d606de0a0bea3d6ecd39cab`(`emotion_prompt_sha()`[schema込み]=`8bc8c816d5187ff060c438bce09b03e21492c7e44806241763631e55db291dce`)。
任意O1(A/B伏せ切替・決定論のみarm②')は今回不採用(②の効果確認後に別検討)。
