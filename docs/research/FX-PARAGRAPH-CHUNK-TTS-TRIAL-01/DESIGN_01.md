# DESIGN_01 (FX-PARAGRAPH-CHUNK-TTS-TRIAL-01 Phase 1、API 0・Production変更0)

状態: 設計+無料準備のみ。**Phase 2(有料TTS/ASR)はOpus条件Aレビュー後のFable Goまで開始しない**(`er113_output/fx_paragraph_chunk_trial_01/PHASE2_GO.json`が無ければscriptが起動拒否)。
原文: `docs/pm/delegation_log/2026-10-25_FX-PARAGRAPH-CHUNK-TTS-TRIAL-01_USER.md`。既存仕様照合: `EXISTING_SPEC_CHECK_01.md`。

対象: Family X『英国の電車マナー』**Advanced = `b1b`**(委任文の『Advanced(A2)』は誤り。a2=Standard。EXISTING_SPEC_CHECK §0)。

## 1. 構成(DEV専用、Production fileの編集0)

| 物 | path | 備考 |
|---|---|---|
| DEV script | `er113_fx_paragraph_chunk_trial_01.py`(新規) | Production moduleはimportして呼ぶのみ。出力は `er113_output/fx_paragraph_chunk_trial_01/` と `user_test/fx_paragraph_chunk_trial_01/` のみ |
| unit test | `er113_fx_paragraph_chunk_trial_01_test_01.py` | 14件PASS(API 0。fake TTS注入のdry-runで『Production store不変』も確認) |
| A側(読取専用) | `er019_output/family_x_audio_production_wiring_01/uk_train_speaker_playback__run_nws_02/b1b/` | 変更・書込み禁止。before/afterでtree sha256を比較 |
| 出力 | `er113_output/fx_paragraph_chunk_trial_01/` | `chunk_plan_01.json` `a_side_measure_01.json` `a_boundary_gaps_01.json` `rebuild_check_01.json`(Phase 1生成済み)、Phase 2で `gen/` `sinks/` `raw_usage_log.jsonl` `gen_result_01.json` ほか |
| 試聴ページ | `user_test/fx_paragraph_chunk_trial_01/index.html` + `audio/*.mp3` | Phase 2後に生成(Phase 1はtemplate生成関数`build_page`を実装・A側のみでスモーク確認済み、B欄は『Phase 2で生成』) |

## 2. 段落分割規則

- 根拠: `b1b/parts.json` は記事を『段落境界で決定論的に3分割』済み(`paragraph_count=10, boundary_i=4, boundary_j=7`)。各part内の段落区切りは空行(`\n\n`)。
- 規則: `re.split(r"\n[ \t]*\n+")` → 空段落除去。分割後 `"\n\n".join(paras)==part` を検証(非可逆なら停止)、chunk総数==`paragraph_count`(=10)を検証。
- 結果(`chunk_plan_01.json`): part1=4(63/14/30/43語)、part2=3(58/52/42語)、part3=3(34/53/39語)。計10 chunk(A=3 segment)。**最短chunkはp1_2の14語**(約5秒。文脈なし短文のTTS品質は評価項目)。

## 3. A/B条件の同一性(対応表。差異は★)

| 項目 | A(記録) | B(chunk) | 同一? |
|---|---|---|---|
| 元文章 | `parts.json` part1/2/3 | 同じtextを段落分割(可逆検証) | 同一(分割のみ) |
| TTS入力整形 | `tts_safe_news_en(part)`→`_pnap_supply`。出力に改行なし | 段落ごとに同じ関数。**' '連結が全体適用と完全一致**(test) | 同一(Aは段落区切り情報なしの1続き文、Bはそれを段落で切るだけ) |
| TTS関数 | `news_tail_fix.generate_news_narration_wide_margin` | **同じ関数を直接呼ぶ**(`disfluency_qa=False`, `enable_repetition_qa=True`, `enable_connected_speech_equivalence_layer=connected_speech_enabled_for("full_story_partN")`, `enable_pronunciation_resolver=True`, `tts_backend="speech_metadata_flash_lite"`) | 同一 |
| model/voice | `gemini-3.8-flash-lite-tts` / Aoede(`tts_generation_results.json`) | 同左(関数内で解決) | 同一(最新モデル原則の例外理由=A/B条件同一性) |
| Style | style_profile `fx_20261017` FULL_STORY(『Speak directly to one listener with warmth…』、速度指示なし) | **A記録のstyle_prefix文字列をそのまま`style_prefix_override`へ**(sha256=`3a680861e4d9…`==`style_base_sha256`を実行時検証、`a_style_prefix()`) | 同一 |
| 速度指示/後処理 | なし(b1bは減速なし) | なし | 同一 |
| TTS実行mode | STANDARD(raw_usage_log記録) | `TTS_EXECUTION_MODE=STANDARD`で起動(Phase 2手順) | 同一 |
| role Gate適用 | segment_id=`full_story_partN` → role=FULL_STORY | 出力pathを `…/gen/<arm>_<chunk_id>/b1b/narration/full_story_partN.wav` とし**segment_idを同一**にする → resolve_narrative_role=FULL_STORY | 同一(これを崩すとASR judge/Connected Speech/Semantic Equivalenceが非適用になるため必須) |
| 入力長に依存するGate | `max_len=len(text)+15`等は関数内で入力ごとに計算 | 同じ(chunkごと) | 同一規則(★chunkが短いため絶対許容は小) |
| ★ chunk間文脈 | part全体を1 callで読む(段落をまたぐ抑揚の連続) | 各段落は独立call(前後文脈なし) | **差異(これが検証対象)** |
| ★ 無音の入り方 | 段落間の間はTTSが内部生成(A実測: 段落境界gap 平均0.62秒[ASR gap 6点、artifact 0.0を除く]、文境界 平均0.545秒) | chunk前後にtrim marginが残置(約0.24–0.35秒×2)+C/Z先例0.5秒gap(B)/追加なし(B0) | 差異(接続方式。評価対象) |
| ★ 音量 | partに1 gain(part1 1.1026/part2 1.2960/part3 1.1873) | chunkごとに同target_rms(0.09149)へgain | 差異(承認済み適用単位=独立TTS出力ごと) |
| ★ review-lock store / telemetry sink | Production path | DEV dirへ向ける(§7) | 差異(Production非汚染のため) |
| ★ 固有名詞RET表 | Production run | `XProvider(DEV dir)`で記事なし→縮退して表なし(A実績もsupply_applied=[]、count 0) | Phase 2 preflightで確認(想定: 影響なし) |
| ★ take | 承認済み1 take(既に確定) | 新規take(TTSは非決定) | 差異。**take間ノイズを見積もるため分散基準armを提案(§6, §8)** |

## 4. 接続・音量方式(承認済み方式の再利用のみ。独自加工なし)

1. 生成: 各chunkは生成関数内で自動trim(0.35秒マージン上限、実残置~0.24–0.32秒)。
2. 音量: `normalize_chunk_to_target(chunk, target_rms=0.09149)` = `compute_gain_for_target_rms(max_peak=0.95)`(A側`gain_report.json`の値をそのまま使用。他segmentのgainが変わらない)。**適用単位=独立TTS出力(=段落chunk)** — Family A/B/C/X/Zの全segmentが各独立TTS出力ごとに同一target_rmsへ個別適用される既存仕様(CURRENT_SPEC:2099)の素直な延長。
3. 段落間無音: **B = 0.5秒**(Family C/Z承認済み story clip接続 `er013_family_c_production_runner_01.py:670`、narrator→narrator)。**B0(参考) = 追加無音0**(trim marginのみ。同じ音声から無料生成)。独自の新ポーズ秒数は導入しない。既存に『本文内段落間ポーズ』の定義は無い(EXISTING_SPEC_CHECK #4)ため、先例のある値を採用。0.5秒を足すと『見かけ減速』が増えるため、B0で切り分ける。
4. 結合: `np.concatenate`のみ(crossfade・重ね合わせなし)。24kHz monoで結合→`mono_24k_to_stereo_target`(Productionと同じ順序)。
5. B全体(Advanced通し): `rebuild_full_episode(b_part_stereo)` = Production runnerの `load_family_x_b1_sources → apply_family_x_b1_gain → build_family_x_b1_timeline → assemble_with_timeline → apply_headroom_safety_valve` をそのまま通し、本文3 segmentだけB版へ差替え。**検証済み(Phase 1、`rebuild_check_01.json`)**: Aを同経路で再構築した結果が完成wavと同長(13,480,336 samples)・最大差5.7e-5(wav量子化)・Production store/A dir変更0。
6. 診断(試聴物ではない): 『part単位1 gain』だった場合のchunk間音量差、境界の音量ジャンプ(dB。前chunk末尾1秒RMS vs 次chunk先頭1秒RMS)、chunkごとのpeak頭打ち有無(post-RMS)。

## 5. Production書込み隔離(Phase 2の安全装置)

- **path構造でreview-lock store(`<level>/audit/review_lock_state.json`)をDEV dirへ**(`derive_segment_key`は出力pathから逆算するため)。
- プロセス内override(Production fileは編集しない): `er011_human_review_lock_01.ATTEMPT_HISTORY_PATH`、`er006_secondary_asr_01.HUMAN_REVIEW_LOG_PATH`、`er021…TELEMETRY_LOG_PATH`(+`append_telemetry_log`はpath既定引数が定義時束縛のため関数ごとwrapperで差替え)、`er025…TELEMETRY_PATH` → `redirect_production_sinks()` context manager。終了時に必ず復元(test済)。
- 費用ログ: `cl.install(er113_output/.../raw_usage_log.jsonl)`(Production run dirのlogへ書かない)。
- before/after sha256: `PROTECTED_STORES`(attempt_history, human_review_queue, er021/er025 telemetry, master_audio_store manifest/reuse_telemetry, pronunciation ledger, cost_summary)+ tree(A run dir、公開ページ`uk_train_speaker_playback_e2e_02`)。**1つでも変化したら即STOP・事実報告**(OPEN-490同様、telemetry書換え差分はstageしない)。
- Phase 1実績: unit testのfake注入dry-run(Production関数と同じscope decoratorを通す)とA再構築で `protected_changed=[]`。
- 残リスク(Phase 2 preflightで再確認): 上記以外のsink(例: `pronunciation_ledger` negative_cache)。before/after snapshotが検知網。Master Audio Storeは本文segmentでは使われない(KP/shared narration用)。

## 6. 評価計画(新しい品質基準を追加しない。既存Gate+ユーザー原文§6)

### ① 音声品質
- 既存Gate(A本文に現に適用されるもの)を**各chunkにそのまま適用**(上記3の関数内で実行): ASR一致(OpenAI primary→必要時Azure)、Repetition QA(本文のみ)、Connected Speech、固有名詞resolver、retry≤3。chunkごとに `status / audio_classification / attempts / repetition_qa_checked` を `gen_result_01.json` に記録。
- 結合後partの確認(**ローカルのみ・無料**): faster-whisper(small)でword timestampsを取り、台本とdifflib整列して (i) 欠落/重複語(境界での語欠け・二重)、(ii) 境界gap分布、を機械確認。結合後partへRepetition QA関数(ローカル、store書込みなしをdry-runで確認してから)を適用。有料ASRは再呼出しない(chunkが各々PASS済み=可逆分割なので結合textも一致)。
- 人間試聴の観点(ユーザー原文§6①): 発音の正確性 / 抑揚・リズムの自然さ / 声質・話し方の一貫性(**過去P6B不合格理由=chunk間の声質差**を最重点) / chunk接続時の不自然な変化 / 段落全体の聞きやすさ。ページに観点リストを載せる。
- 判定は数値Gateではなく、既存Gate結果+ユーザー試聴。Fableの独立評価(原文§9)は、計測値・Gate結果・波形/RMS診断を根拠に行う。

### ② 速度(実発話速度 と ポーズ増による見かけの減速 の分離)
- 語数=`count_primary`(既存Coffee Advanced WPM計測と同定義)。ポーズ=-40dB/20ms frame、≥300ms/≥500ms(既存`measure_wpm_01.py`の定義を**転記**。そのscriptは末尾に無条件`main()`があり、importすると走ってファイルを書くため。転記版と原本関数の数値一致を`test_measure_defs_match_original_source`で機械確認)。
- 指標: `total_wpm`(語数/全長=聴感上の速度)、`articulation_wpm_500/300`(語数/(全長−≥500/300ms無音合計)=実発話速度に近い)、`mid_pause`の個数・合計・平均・最大、Δ全長 = Δ発話時間(実速度)+Δ無音時間(ポーズ)の分解。
- 比較単位: 本文1/2/3、本文全体(1+2+3、間1.0秒、A/B同一)、B/B0/Aの3系統。
- 参考(A実測、`a_side_measure_01.json`): part1 total 168.3 / art500 183.5 WPM、part2 192.1 / 213.6、part3 194.1 / 210.9、本文計(428語)139.92秒 total 183.5 / art500 201.3。A内でもpart間で total WPM が168〜194と大きくばらつく → **take間・内容間ノイズが大きい**。単一takeのA/B差は慎重に解釈する必要がある(分散基準arm、§8)。
- A側の段落境界の自然な間(`a_boundary_gaps_01.json`、ローカル):段落境界gap(ASR語gap) 0.50/0.84/0.72/0.46/0.66/0.54秒(+整列不能0.0が2点)→平均約0.62秒、文境界平均0.545秒(n=26)。→ B0(trim margin残置のみ≈0.5–0.6秒)はAに近い、B(+0.5秒)は境界が約1.0秒となり**約0.4秒長い**見込み → 『見かけの減速』になる。Opus論点(a)(c)。

### ③ QCD
| 項目 | A(本文3 segment) | B(chunk 10本) | 備考 |
|---|---|---|---|
| TTS call数(1 take、retry0) | 3 | 10 | A raw_usage_log: b1bの本文はTTS 1回/segment |
| TTS費用 | 出力~3,500 tok(140秒×25tok/s)×$6/M×160 ≈ **3.4円** + 入力 | 同(出力tokenは音声秒数に線形)+ 入力overhead 7 call×~50tok ≈ **+0.03円** | 単価: pricing_snapshot.json `gemini-3.8-flash-lite-tts` Standard in $0.5/M, out $6.0/M(25tok/s)。A実測1call part1: out 1,308 tok/in 189 tok=1.27円 |
| ASR(primary OpenAI) | 3 call ≈ 0.7円(1call 0.2〜0.25円: part1 in523/out176) | 10 call、token総量は音声秒数に線形→ **ほぼ同額(~0.7円)** | `gpt-4o-mini-transcribe` in $1.25/M out $5.0/M |
| Azure secondary | 非primary-PASS時のみ($1/音声h=140秒で最大6.2円) | 同 | chunkが短いほどsecondary対象音声秒数は減る可能性 |
| 所要時間 | A part1 TTS 8.3秒+ASR 2.0秒(1 attempt) | 直列10 call。音声秒数線形+call固定overhead → +10〜20秒/take見込み | 実測はPhase 2で記録(raw_usage_log elapsed) |
| retry影響 | 失敗時はpart全体(40–53秒)を再生成 | 失敗時は該当段落のみ再生成 → 再生成単価は低下、ただしchunk数分だけ『どこか1本が失敗』確率は増 | 実測attempt数で比較 |
| 量産単価換算 | — | 採用時のΔ ≈ Advanced本文で**+0.03〜0.1円/記事**(TTS入力overhead+ASR call overheadのみ)。retry実測次第で±。70円/記事セット目標に対して影響は無視可能な見込み(実測で確定) | StandardにもB方式を適用する場合は別途 |

## 7. 予算(Phase 2見積。Fable設定の上限50円、300円以下=自律枠)

| arm | 内容 | 通常 | 最悪(全chunkがattempt3まで+Azure全件) |
|---|---|---|---|
| **B_r1(必須)** | 段落chunk 10本 | TTS 3.5 + ASR 0.7 = **約4.2円** | 4.2×3 + Azure 6.2 ≈ 19円 |
| A_r2(提案) | 現行方式(part全体3 call)の再生成=**Aのtake間ノイズ基準** | 約4.2円 | 約19円 |
| B_r2(提案) | Bの再take=**Bのtake間ノイズ基準** | 約4.2円 | 約19円 |
| 合計(3 arm) | | **約12.6円** | 上限50円でCap停止(`compute_cost_jpy_so_far`がCap到達で後続chunkを開始しない) |

- 推奨: 3 arm(約13円)。理由=Aのpart間total WPMが168〜194とばらつくため、単一takeのB-A差はノイズと区別できない。最小構成はB_r1のみ(約4.2円)。
- 単価の出典: `er005_output/cost_baseline_01/pricing_snapshot.json`(USD_JPY=160は`er019_family_x_audio_production_runner_01.py` と同一)。推定式は`estimate_tts_jpy/estimate_asr_jpy`、A実測1 callとの一致をtest済み。
- 運用(`PM_GOVERNANCE.md` 26節): 有料runは**1 launch**(`gen --arms B_r1 A_r2 B_r2`を1コマンドで直列実行。arm間で停止しない/失敗で自動継続しない)。起動前に`tools/stop_scope_check_01.py`(rc=3で中止)、script内でも再実行。起動間隔150秒以上・5分3回(RESTART_STORM)に触れないよう**再起動はFable許可がある場合のみ**。background起動時はPIDを記録。`TTS_EXECUTION_MODE=STANDARD`。API失敗/原因不明rc≠0が2回で即STOP。STOP/STOP_ALLの削除・回避なし。
- 現在までの費用: **0円**(`BUDGET_LOG_01.md`)。

## 8. 試聴ページ設計 `user_test/fx_paragraph_chunk_trial_01/index.html`

- CSS・table構造は既存Family X試聴ページ(`user_test/uk_train_speaker_playback_e2e_02/index.html`)を再利用。
- 行: 本文1 / 本文2 / 本文3(各 A | B | B0参考 | Script) / 本文全体(A|B|B0) / Advanced通し(A|B)。mp3は`user_test/…/audio/`のみ(追跡可)。
- 比較表: WPM(total/articulation)・ポーズ・境界音量差・Gate結果・TTS call数・費用・所要時間・Fable独立評価。観点リスト(原文§6①)。
- 状態表示: 『Trial(Production採用ではありません)』。公開済み完成ページ・音声は不変。
- 分散基準arm(A_r2, B_r2)の音声は既定でページに載せず、WPM比較表のノイズ幅としてのみ使用(ユーザーが希望すれば追加)。

## 9. 撤退・STOP条件・Production不変の保証

- STOP: STOP_NOTICE/STOP/STOP_ALL適用、`PHASE2_GO.json`なし、Cap(50円)到達、Production store/A dir/公開ページのsha256変化、chunkの`status!=OK`(既存retry上限3消化後)→後続armへ進まず停止しFableへ報告(自動再実行しない)、外部停止process。
- 撤退: B全chunkがGate PASSしない、または過去P6B同様のchunk間声質差が確認された場合は**REJECTED**として報告(Trial終了。追加の磨き込みはしない)。Production採用へ自動移行しない(ユーザー判断)。
- Production不変: commit前に `git status` / `git diff --cached --name-status` でDEV script・test・docs・`er113_output`のjson・`user_test/fx_paragraph_chunk_trial_01/`以外の差分0を確認。wav/raw_usage_log/STOP/lock/ACTIVE_TASK/RESULT_PACKETは追跡しない。Production code/Prompt/flag/閾値変更0、Production出力dir書込み0(Phase 1実測: A dir・公開ページ・保護store変化0)。
- 新規flagなし(DEV scriptは独立実行。Production到達経路に入る未承認機能なし)。

## 10. Phase 2 手順(Go後)

1. `PHASE2_GO.json`(`managed_id`,`cap_jpy`,`approved_by`,`arms`)をFableが作成 → 2. stop check → 3. `TTS_EXECUTION_MODE=STANDARD .venv\Scripts\python.exe er113_fx_paragraph_chunk_trial_01.py gen --arms B_r1 A_r2 B_r2`(1 launch) → 4. `compute_b_artifacts`でB(0.5s)/B0(0s)を組立・計測(API 0) → 5. ローカルfaster-whisperで結合part確認 → 6. `build_page`でページ生成 → 7. Fable独立評価・Closeout(VALIDATED/REJECTED/USER_DECISION_REQUIRED)。
