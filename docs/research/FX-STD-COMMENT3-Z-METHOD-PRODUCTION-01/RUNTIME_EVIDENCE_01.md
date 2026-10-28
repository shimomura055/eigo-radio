# RUNTIME_EVIDENCE_01: X Std Comment 3 Z方式 — 両経路の実API/実音声evidence(委任_02、M-4)

管理ID: FX-STD-COMMENT3-Z-METHOD-PRODUCTION-01。配線commit=`84a61fba7`。使用モデル: support LLM=`gpt-6-luna`(`_a2_support_model()`=本番ライン既定。評価用途ではなく本番経路のためCharter 25節の「最新原則」対象外)、TTS=`gemini-3.8-flash-lite-tts`(Aoede、`speech_metadata_flash_lite`)、ASR=`gpt-4o-mini-transcribe`。

## 1. 初回生成経路(正式関数`run_family_x_a2_scaffold`、scratch、公開物に不使用)
実行: `docs/research/FX-STD-COMMENT3-Z-METHOD-PRODUCTION-01/evidence_first_path_01.py`(AI島partsを入力に`runner.run_family_x_a2_scaffold`を実API 1回)。出力=`evidence_first_path/`(`first_path_summary.json`、`first_path_comment3_prompt_audit.json`、`a2_support_texts.json`、`audit/a2_support_generation.json`。`raw_usage_log.jsonl`は不追跡)。
- LLM呼出=**5回**(preview/C1/C2/C3/C4各1。C3はlint1回で合格=retry 0)。全status=OK。stdoutにC3は`Z方式 FX-STD-COMMENT3-Z-V1`と表示。
- C3のprompt: `a2gen.COMMENT_2_ROLE`で始まる=True、`【これから聞く本文(後半)】\nThe researchers also erased …`を含む=True、`went down`=含まない、`Even so`=含まない。
- C3 response_id=`resp_0b7b3f3c017dd1b0006ae1eaa1f88487d0a81274e940c57432`、model=`gpt-6-luna`。他: C1=`resp_0760e29b…`、C2=`resp_047edb8e…`、C4=`resp_067e6329…`、Preview=`resp_07445dc2…`。
- `comment3_z_audit`: method_version=FX-STD-COMMENT3-Z-V1、mode=**Z_EXCERPT**、role_sha256=`0268c9f1deac…`、passed_excerpt_sha256=`c0326dc10ccc…`、part3_sha256=`2452fe36b64f…`、lint_retry_count=0、final_status=OK、attempt[0]にtext/response_id/model/prompt_sha256(`f6a83ef238…`)。
- 生成C3(初回経路、参考): 「島がリセットされても、AIのメモは残り、経験したAIは塔作りでよりよい結果を出しました。では、AIの記憶からある方法を消すと、何が起きるのでしょうか。」
- 費用: ¥0.32。

## 2. 再生成経路(AI島Standard、公開候補)
コマンド(1起動): `er019_family_x_audio_production_runner_01.py --slug ai_island_temple --run run_form_prod_01 --stage scaffold --level a2 --regenerate-support comment_3`(rc=0、LLM 1回、費用 ¥0.05)。
- **入力parts(R-6)**: `er019_output/ai_island_temple/run_form_prod_01/a2/article.md`の3分割にLR台帳overlay(`er132`)を適用=`lr_overlay_applied=True`(`AIs sent`→`AI agents sent`の1語。公開本文と一致)。input_parts_sha256 part1=`e618131cbe51…`/part2=`456988779b3a…`/part3=`2452fe36b64f…`(base部は`audit/a2_support_generation.json`の`comment_3.comment3_z_audit.input_parts_source`に両方保存)。
- **prompt全文**: `audit/a2_support_generation.json`の`comment_3.prompt`(2531字)。`COMMENT_2_ROLE`で始まる=True、`【これから聞く本文(後半)】\nThe researchers also erased a way to “throw rocks to get more blocks” from one AI’s memory.`を含む=True、`went down`=なし、`Even so`=なし(Part 3は第1文のみ渡る。Part 3の結果文以降は不渡)。
- response_id=`resp_0907239a0a8fede9006ae1ead848f087d08552de271b3e7d87`、model=`gpt-6-luna`。`comment3_z_audit`: mode=Z_EXCERPT、lint_retry_count=0、final_status=OK、passed_excerpt_sha256=`c0326dc10ccc…`(初回経路と同一)、part3_sha256=`2452fe36b64f…`、role_sha256=`0268c9f1deac…`。
- **C3 Before**(旧X C3役割文・Part1+2のみ): 「島は毎時間元に戻りますが、AIのメモは残り、島で経験したAIは新しい課題でよい結果を出しました。続いて、経験やメモがAIの次の行動にどうつながるのかに注目してください。」
- **C3 After**(Z方式): 「島は毎時間リセットされても、メモに残した経験は次の課題に役立ちました。では、学んだ方法を一つ消されたAIでも、その経験は役立つのでしょうか。」
- **他4キーsha不変**(書込み前後assert PASS。`ai_island_support_before_01.json`に更新前の全文・sha): preview `e9d5831b…`、comment_1 `4e088359…`、comment_2 `406e2f02…`、comment_4 `a3a84dbd…` — いずれも同一。`audit/a2_support_generation.json`はpreview/comment_1/comment_2/comment_4の元記録を保持、旧comment_3は`comment_3_history`、旧版は`*.before_c3_regen.json`へ退避。KP・Part 2・study_text・parts.jsonは未変更(testでdir内容固定)。
- R-5(C2×C3の非blocking重複メモ): 日本語4-gram一致12件(`されても`/`しょうか`/`でしょう`/`のでしょ`/`の経験は`/`の課題に`/`リセット`系)。**C2は「島での経験は、その後の課題に役立ったのでしょうか」の問い、C3は同じ「経験が課題に役立った」を事実として回収してから別の問い(方法を消した場合)を立てる**構図で、C2とC3の回収点が近い。Gateにはしない。Fableの目視受入で重複の程度を確認(試聴に支障と判断される場合のみユーザーへ進言)。
- Part 3先取りなしの確認(M-4): (i)7記事の切り出し表=`WIRING_DESIGN_02.md`、(ii)C3 After本文は「方法を消す」(Part 3第1文)を問いに用い、Part 3の結果(塔の平均数が下がった)・留保(Even so…)・数値は含まない、(iii)lint合格(WITHHELD_NUMBER/TERM/CONCLUSION_WORD/STRUCT_LABELなし)。lintは渡していない部分しか見ないため、先取りなしの最終確認はFableの目視。

## 3. TTS(comment_3のみ)・ASR
`--stage tts --level a2 --only-segments comment_3`(rc=0)。
- 送信パラメータ(`audit/tts_generation_results.json` segments.comment_3): model=`gemini-3.8-flash-lite-tts`、voice=`Aoede`、tts_backend=`speech_metadata_flash_lite`、call_count=**1**、retry_count=0、style_prefix=Std support JA(J3、「温かみと親しみのあるニュースナレーターとして、…問いかけは穏やかに読み、語尾を大きく跳ね上げないでください。…」)、入力text=C3 After(読み補正による変更なし: `reading_safety_changed_text=False`)。
- wav: `…/a2/narration/comment_3.wav` sha256=`b337a98aa94866a7…`、14.43秒、clipping_detected=False。
- ASR(`gpt-4o-mini-transcribe`、primary): 「島は毎時間リセットされても、メモに残した経験は次の課題に役立ちました。 では、学んだ方法を一つ消されたAIでも、その経験は役立つのでしょうか。」→ **audio_classification=NORMALIZED_MATCH、asr_judgement.state=PASS(primary_pass)**、asr_verified=True、value_guard=EQUAL、HR Lock `comment_3`=**RESOLVED**(status=OKで確定、HR Lockにならず)。
- 他音声の引継ぎ: `validation_inheritance`により他セグメント(topic_intro/japanese_title/preview/comment_1/2/4/full_story_*/in_one_line)は`reused_from_previous_run=True`で再TTSなし。narration wav sha(comment_1 `3fce41aa1e15bab8`/comment_2 `a4a5024f350835a8`/comment_4 `b8d51eb8262c57dd`/preview `9a785098a71ea61e`)は更新前後で不変。費用: TTS+ASR ¥0.25。

## 4. 正式assemble・page
- `--stage assemble --level a2`(rc=0、1起動、TTS/LLMなし): `run_summary_assemble.json` status=OK、assembled wav sha256=`7f98b73e70c5258c6158b0f6c3976f7e28809b9360e593440c29dfbfa29e51f6`(327秒。更新前331秒)。`style_profile_gate.json` status=PASS・blocked=[]・warnings=[LR_APPLIED(AIs→AI agents、full_story_part1_k2。既知=UD-2)]。
- 候補ページ: 標準builder`er019_family_x_listening_page_01.py --slug ai_island_temple --run-name run_form_prod_01 --web <scratch>`の出力を`user_test/family_x_ai_island_form_01_candidate_b7_01/`へ反映。**変更ファイルは3つのみ**=`index.html`・`audio/ai_island_temple_standard.mp3`(通し)・`audio/std_18.mp3`(comment_3クリップ)。**`adv_00〜21.mp3`・`ai_island_temple_advanced.mp3`の全23件はbyte同一**(sha照合、Advは不変)。index.htmlの差分=C3本文・Std通し長(331→327秒)・C3以降のStd区間の開始秒(223.8→220.3、286.3→282.8、306.3→302.8、324.6→321.1)のみ(`SequenceMatcher`で確認、Advの表・学習項目・LR赤4件は不変)。
- page_verify(local Playwright、`evidence_page/page_verify_local_01.json`): HTTP200、audio 47/47再生、console error 0、4xx 0、file scheme 0、旧LR注記0、LR赤4(`rpt_lr`)・⏸10(`chunk_marks`)・fallback 0。candidate sha256: index `ac3fd71d…`、std_18.mp3 `6323e844…`、ai_island_temple_standard.mp3 `24d6a78b…`。

## 5. 費用内訳
初回経路evidence ¥0.32 + C3再生成 ¥0.05 + TTS/ASR ¥0.25 = **¥0.62**(上限¥30、AI島run累計 36.94→37.24 JPY)。

## 6. Pages反映後の実測(2026-10-28 12:53 UTC、push 664443842/1502e25ca後)
URL=https://shimomura055.github.io/eigo-radio/user_test/family_x_ai_island_form_01_candidate_b7_01/ 。HTTP200、配信bytesのsha256(先頭16桁)が`git show HEAD:`のblobと全件一致: index.html `743d6fd06a0cb947`(git blob。作業ツリーのCRLF差のみ)、audio/std_18.mp3 `6323e844…`(新comment_3)、audio/ai_island_temple_standard.mp3 `24d6a78b…`(新通し)、Adv側(ai_island_temple_advanced.mp3 `bafe5938…`/adv_00 `fd00cf85…`/adv_21 `089a7f3c…`)とStd未変更クリップ(std_00 `4d21cc91…`)は更新前と同一。配信直後に旧版が返った(別workerのpush連続によるPages deploy cancel/queueで約12分遅延)が、最終的に新版へ切替わったことを確認。
