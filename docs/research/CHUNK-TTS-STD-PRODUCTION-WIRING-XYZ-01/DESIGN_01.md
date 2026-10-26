# DESIGN_01 — Standard(6%減速)×Chunk分割(+0.2秒)の合成設計と X/Y 配線(Z は設計のみ)

管理ID: CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01 委任_01(2026-10-26)。前提=ユーザー正式承認(APPROVED_FOR_PRODUCTION 2026-10-26、原文=`docs/pm/delegation_log/2026-10-26_CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01_USER.md` §2「Standardを除外することは認めない」)。要求項目=`SPEC_LEDGER_01.md`。基準commit=`bb578265c`。
過去のOpus指摘(`docs/research/FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01/OPUS_REVIEW_01.md`)でStdにも維持する点は§9。

## 1. 結論(要点)
1. **合成方式は委任文の既定方針どおり**: 『chunkごとに既存の減速処理をそのまま適用 → 減速後のchunk wavを、減速対象外の0.2秒(正確に4800サンプル@24kHz)の無音で連結』。連結後減速は採らない。新規の後処理・閾値・補正係数は**導入していない**(減速率6%・`apply_a2_slowdown_postprocess`・減速後ASR再検証・通算TTS3回の予算は無変更)。Opus条件Aの「実装前待ち不要」条件(DELEGATION本文)に適合 → そのまま実装した。
2. 既存の減速検証(減速後ASR再検証=統一judge、共有Gate `_segment_missing_mandatory_a2_slowdown`、Zの`verify_std_english_slowdown`)が**chunk単位でも成立する**ことをコードで確認した(§3)。成立しない箇所は無かった(STOP事由なし)。ただし**共有Gateはchunk idを知らない**ため(`A2_SLOWDOWN_TARGET_SEGMENTS`にchunk idが無い)、chunkの減速欠落を見逃す穴があり、X/Yの組立前Gateへ追加検査を足した(§4)。
3. X Std・Y Stdを実装(IMPLEMENTED_PENDING_EVIDENCE)。Z Stdは設計のみ(§6、実装は次委任。`er063`は読取のみ)。
4. 実Y記事は各Voice 1段落のためY Std/Advとも分割0(不発火=正常)。複数段落入力での発火は合成入力のtestで示し、正式runtimeは次委任(§7)。

## 2. 合成方式の詳細(Std chunk)
```
親(例 full_story_part1, 3段落)
  plan_x_part(既存・無変更) → chunk k1,k2,k3 (段落境界、boundary_kind=paragraph)
  各chunk kj について(直列・chunk順):
     n3_tts.generate_a2_segment_with_slowdown(tts_input_j, narration/<kj>.wav, first_words(text_j),
         style_prefix_override=Std style[減速instruction込み], disfluency_qa=False,
         enable_connected_speech_equivalence_layer=…, enable_repetition_qa=True, tts_backend)
       = 通常ペースTTS(標準→fallback) → narration/<kj>_original.wav 退避 → atempo 6% → 減速後ASR再検証(統一judge)
         → 減速後NGなら通算TTS3回の残予算で取り直し → 最終NGは finalize_a2_slowdown_final_ng(Lock/HR queue、chunk id単位)
  親wav = compose_raw_pcm([k1.wav, k2.wav, k3.wav])   # 減速後chunk wav + 4800サンプルの無音×(n-1)、PCM16バイト一致
  親集約entry: er117.refresh_parent_status(既存) + std_parent_slowdown_fields(全chunk減速済みのときだけ slowdown_applied=True)
  組立: compose_gained_parent(既存・無変更): chunk別scalar gain → 0.2秒pad → 連結 → 48kHz stereo
```
- **ポーズ0.2秒の保持**: 無音は減速**後**に挿入するため減速されない(testで`parent[len(k1):len(k1)+4800]==0`を整数サンプルで固定)。連結後に減速する方式は、全体(ポーズ込み)が約6%伸びて合成長検査(Σchunk+4800×(n−1))が成立せず、ポーズも正確な4800サンプルではなくなる(実ffmpeg測定: 連結後減速のゼロ連続長=4569サンプル≠4800、`er117_std_chunk_wiring_test_01.py::test_slowdown_after_concat_breaks_the_exact_0_2s_pause_invariant`)→採らない。
- **既知の性質(仕様変更ではない)**: chunk間の可聴ポーズ = 前chunk末尾の保持margin + 0.2秒 + 次chunk先頭の保持margin。Stdではmarginも減速で約6%伸びる(Advは伸びない)。追加ポーズ自体は承認どおり0.2秒。既存Adv chunk実測(`uk_train_speaker_playback__run_chunk_01` 10 chunk)のmarginは各側0.16〜0.35秒(境界あたり合計約0.4〜0.7秒)なので、Stdの差は境界あたり約0.02〜0.04秒(合計margin×6%)。Phase 2で`trim_info`の実測から報告する(Opusに重点確認させたい点)。
- 費用の性質: 追加LLM call 0。TTS総文字数・ASR総音声長は不変で、chunk数分のcall数が増える(X Std 3 part→最大10 chunk)。chunk単位の取り直しは部分的な再生成で済む(本文修正時に変わるのは1 chunkのみ)。

## 3. 既存の減速検証がchunk単位で成立する根拠(コード確認)
| 項目 | 確認 | 場所 |
|---|---|---|
| segment名の制約 | `generate_a2_segment_with_slowdown`は`out_path`から`name`を導出するだけで、`A2_SLOWDOWN_TARGET_SEGMENTS`への所属を要求しない。`apply_a2_slowdown_postprocess(name,…)`は`{name}_original.wav`を退避し`{name}.wav`を差し替えるだけ | `er003_v1_n3_01_tts_generate.py:194-250,331-432` |
| 減速後ASR再検証 | `_post_slowdown_unified_judge(…, segment_id=name)`。role gating(`resolve_narrative_role`)はchunk id(`full_story_part{n}_k{j}`/`y_*_k{j}`)をFULL_STORYへ解決済み(import時自己検査 `er019`:91-96、Y: `_assert_chunk_roles`) | `er019:91-96`、`er121…audio:278-285` |
| 語数・尺の下限 | 減速本体`apply_a2_slowdown`に語数/尺の下限なし(`atempo=1/1.06`、有効範囲assertのみ)。最短chunk実例=8語(Std実データ `boredom_aggression__run_bape_01/a2` part1 k4=8語)。比率検査は±1.03〜1.09で、3桁丸めの尺でも3秒級chunkで安全 | `er008_a2_postprocess_slowdown_01.py:32-58`、`er003_v1_n3_01_assemble.py:_A2_SLOWDOWN_ORIGINAL_RATIO_*` |
| 通算TTS3回 | `review_lock.PRODUCTION_MAX_TTS_ATTEMPTS`をchunk(=segment)単位で使う。上限回避なし | `er003…tts_generate.py:358-` |
| Lock/HR | `review_lock.record_outcome(out_path,…)`はout_path(=chunk wav)単位。chunk id単位の承認がそのまま効く | `er011_human_review_lock_01.py`(Opus I-3/共有Gate) |
| ✘ 穴(補った) | 共有Gate `_segment_missing_mandatory_a2_slowdown(name,…)`は`name not in A2_SLOWDOWN_TARGET_SEGMENTS`なら即False=chunk idの減速欠落を検知しない。また親(`full_story_part1/2`)はchunk化で`slowdown_applied`も`_original.wav`も持たず誤ブロックされる | `er003_v1_n3_01_assemble.py:239-290,490` |

## 4. Gate設計(共有Gateは無変更、追加検査で補う。回避ではない)
- **親**: `er117.std_parent_slowdown_fields`で『全chunkが`slowdown_applied is True`かつ記録された減速前後長の比∈[1.03,1.09]のときだけ`slowdown_applied=True`』を集約(`slowdown_basis`に根拠を残す)。1つでも欠ければFalse → 共有Gateの`MISSING_MANDATORY_A2_SLOWDOWN`で親がブロックされる。親wavは減速後chunkの生連結なので、この集約は事実と一致する。
- **chunk**: X=`er019._x_std_chunk_slowdown_blocked`(`stage_assemble_family_x_a2`でStyle gate・共有Gateより前)、Y=`er121.check_std_slowdown(results, plans)`(chunk化したsegmentは**親ではなく全chunk**を検査。親の集約値だけで通さない)。人間承認(`record_human_approval`)は共有Gateのstatusにしか効かないため、減速欠落は人間承認でも迂回できない(testで固定)。
- **比率レンジ**は共有Gateの`_A2_SLOWDOWN_ORIGINAL_RATIO_MIN/MAX`の複製(1.03/1.09)で、一致をtestで固定。減速後ASRの合否は共有Gate(VALIDATED/HUMAN_APPROVED)の責務で、減速検査では見ない(人間承認済みchunkを誤ブロックしない)。
- 共有module(`er003_v1_n3_01_assemble.py`・`er003_v1_n3_01_tts_generate.py`)は**編集していない**(後者は並行Agent[FZ]の領域)。

## 5. 共通規則 er117 の扱い(レベル条件)
| 項目 | 現状 | 本委任 | 次委任 |
|---|---|---|---|
| `plan_x_part/plan_x_parts`(X/Y planner) | レベル条件なし(元からStd/Advを区別しない。除外は呼出側=`er019`関数配置・`er121 CHUNK_TTS_Y_LEVELS`) | **無変更**(規則・`CHUNK_PLANNER_VERSION`不変=Advの旧cache/resume/goldenを壊さない) | — |
| `plan_z_clip`の`level != "b1b"`(`er117:143-144`) | Zの除外条件 | **撤去しない**(Z側の減速合成=`er063`が未配線のまま発火させないため) | 撤去+`er063:598`の`level == "b1b"`撤去を同時に(§6) |
| `attach_chunk_meta` | Adv用 | `level=None`既定でAdvバイト同一。`level="a2"`のときだけ`level`/`std_slowdown_composition`を追加 | Zも同じ引数を使う |
| 新規(X/Y共用) | — | `std_chunk_slowdown_violations`/`std_parent_slowdown_fields`/`drop_cached_std_chunks_without_slowdown`/`evidence_record`のStd項目(Adv entryには出ない) | Zが再利用 |

## 6. Z Std設計(実装は次委任。`er063`は本委任で読取のみ)
Zの`er063_family_z_audio_01.py`(並行Agentが編集中のため行番号は目安。実装時に再確認)変更点:
1. `:598` `cp.get("chunked") and kind == "narrator" and level == "b1b"` → `level in ("b1b","a2")`。同時に `er117.plan_z_clip`/`plan_z_level` のレベル条件(`er117:143-144`)を撤去(**同一委任で同時に**。片方だけだとChunkedなplanがSpecに展開されない/逆にplanだけ発火する)。
2. Std narratorの生成関数は既に`n3_tts.generate_a2_segment_with_slowdown`(`er063:1010`)で、chunk ClipSpec(kind=narrator, level=a2)はそのまま**chunk単位の6%減速**になる(新規処理なし)。dialogue(Std減速禁止)はchunk対象外(`kind == "narrator"`条件を維持)。
3. 親集約entryの表示(`_z_chunk_parent_display` `:636` `"slowdown_applied": None`)を、a2では`chunk_tts.std_parent_slowdown_fields`で集約(X/Yと同じ)。
4. 速度Gate: `verify_std_english_slowdown`(`:1722-`)は`_CLIP_ID_RE.fullmatch`で**chunk idを除外**している。`_CLIP_OR_CHUNK_ID_RE`へ広げ(R2のGate箇所のみ許可の方針に沿う)、chunk entryに`slowdown_applied`/比率を要求し、**chunk化された親は集約値で判定**する。`verify_z_speed_profile`のStd narrator分岐(chunk idは既にR2で対象)との二重判定にならないよう確認。
5. `build_reuse_key`の`chunk_tts`追加(`:820-823`)はStdにも同じ(旧Std非chunk keyはバイト不変)。reuseは`slowdown_applied`証跡のないcacheを拒否(`drop_cached_std_chunks_without_slowdown`の適用)。
6. `er026` `…:2308`の`plan_z_level(story_clips, paras, level)`は既にlevelを渡している。`for_tts=False`の`effective_plan`(legacy互換)はStdにも効く。
7. test: `er117_z_chunk_wiring_test_01.py:130-132,202`(Std不変の固定)を『Stdはnarrator>100語でchunk化、dialogue不変、Adv不変』へ書換え。Zの実run(tell_tale 129/139語・melos 134語・gift_of_the_magi 122語の100語超narratorが4 clip残存)を対象にgolden(`planner_fixture_01.json`のStd版)を追加。
8. 注意: 原文「約70語を目安」はchunkサイズの目安で、実装の閾値100語・`k=ceil(語数/100)`と整合する(`SPEC_LEDGER_01.md`§1の照合注記)。次委任でFableが再照合。

## 7. Phase 2 runtime evidence計画(次委任。本委任は実行しない)
| 対象 | 入力 | 正式経路・run | 発火証拠 | 公開物 |
|---|---|---|---|---|
| X Std | 既存Std `a2/`(例 `er019_output/family_x_audio_production_wiring_01/coffee_prices__run_fxpw_01_s3prod/a2`、3 part=最大10 chunk)を新規out-dirへ複製(入力dirを汚さない) | `TTS_EXECUTION_MODE=STANDARD .venv\Scripts\python.exe er019_family_x_audio_production_runner_01.py --slug <slug> --run <新規run> --level a2 --stage tts --only-segments full_story_part1,full_story_part2,full_story_part3 --budget-jpy 20` → `--stage assemble` | `audit/chunk_plan_a2.json`(分割位置)、`audit/chunk_tts_evidence_a2.json`(chunk数・chunkごとのattempt/fallback/LR/減速率/ASR)、`audit/chunk_tts_assembly_a2.json`(0.2秒のepisode内offset・gain・peak cap)、TTS call数(cost log)、`verify_raw_parent` | 変更なし(新規out-dir) |
| Y Std/Adv | 合成の複数段落dev入力(Voice 2〜3段落)を新規run dirへ。実記事は1段落のため不発火であることを併せて記録(`chunk_tts_decision.json` `chunked:false,paragraphs:1`) | Y runner `tts_a2`/`tts_b1b`(複数段落segmentのみ`--only-segments`)→`gate`→`assemble` | `chunk_tts_decision.json`(適用level・分割)、`chunk_tts_evidence_{a2,b1b}.json`、`chunk_tts_assembly_{a2,b1b}.json`(gap offset、`gap=0.2秒`)、`y_style_profile_gate.json` PASS | 公開済みY記事・試聴ページは不変 |
| Z Std | tell_tale 129/139語narrator 1〜2 clip(次委任のZ実装後) | Z runner `--stages provision_shell,gate,assemble,pages,page_verify`を**1起動**(OPEN-480) | Z `chunk_tts_evidence_a2.json`、`verify_std_english_slowdown`のchunk判定 | 新規run id |
- 判定の区別: **不発火**(段落1つ=plan `chunked:false`)と**配線漏れ**(複数段落なのにchunk entryが無い/`chunk_plan_a2.json`が無い/Gate未発火)を`chunk_plan_*.json`の`reason`と`paragraphs`で区別して報告する。
- 未取得のGate 3必須条件は6行表の「runtime」列に「未取得」と明記する(RESULT_PACKET)。

## 8. 一貫性マトリクス(初回/retry/fallback/regeneration/resume、X/Y Std)
| 経路 | 挙動 | 根拠 |
|---|---|---|
| 初回生成 | planに従いchunkごとに減速付き生成。親は最後に集約。KP等は従来 | `_generate_x_body_part_chunked_a2`/`_generate_y_body_segment_chunked_a2` |
| retry | chunkごと通算TTS3回(標準→fallback→減速後NGの取り直し)、cap回避なし | 既存`generate_a2_segment_with_slowdown`を無変更で呼ぶ |
| fallback | chunk単位。`fallback_used`は既存Style gate(`STD_FALLBACK_USED_OR_UNKNOWN`)がchunkごとに検査 | `m3_assembly_gate`/`y_style_gate`はchunk entryを列挙(親は対象外=M1) |
| regeneration | 同一本文・同一版でplanが変わればSTOP(`reconcile_saved_plan`、`chunk_plan_a2.json`)。planner版が違うchunkは破棄(I1)。本文が変われば当該chunkだけ再生成 | testあり |
| resume | OK chunkは再利用(再課金なし)。減速証跡のないcache chunkは再利用しない(`drop_cached_std_chunks_without_slowdown`)。`--only-segments <親>`は全chunkへ展開、`_k`個別指定も可 | testあり |
| 失敗継続 | chunk失敗後も後続chunkを生成(R1)。親は`CHUNKS_NOT_ALL_VALIDATED`(共有Gateの承認参照対象外=親idの承認で迂回不可) | testあり |
| legacy | 本方式導入前のStd結果(親entryのみ・chunk entryなし)は従来経路のまま再組立可(X: `effective_plan`、公開済みepisodeを壊さない)。tts stageは常にchunk化 | testあり |

## 9. 過去Opus指摘のうちStdでも維持する点(`OPUS_REVIEW_01.md`)
M1(Style gateはchunkを列挙・親は対象外)=Xは`_chunk_names_for`がレベル非依存で既にStdに効く/Yは`y_style_gate`の`plans`をa2にも計算。M2(親は失敗時も常に書く・planのchunk id一覧からstatus導出)=`refresh_parent_status`共用。I1(planner_version不一致cache破棄)=`drop_stale_chunk_entries`。I2(gain式の一本化)=`compose_gained_parent`にp9a関数を渡す。I4(import時のrole自己検査)=既存のまま。I5(`--only-segments`の`_k`)=Stdも許可に更新(`_k`は本文partにのみ。誤指定は引き続き拒否)。I7(親の表示項目)=`_x_chunk_parent_display`共用。I8(整数サンプル合成長検査・`verify_raw_parent`)=Std組立でも実行。R1(失敗後も後続chunk)=維持。I10(回帰はclean worktree)=`git worktree`(HEAD)で前後比較を取得(`FIX_01.md`)。

## 10. SSOT文案(RESULT_PACKET再掲・SSOT編集は本委任で行わない)
- CURRENT_SPEC「Family X・Z Advanced地の文/本文のchunk TTS」節(`CURRENT_SPEC.md:2939` 付近)の**対象**行を次へ是正: 「対象: Family X・Y・Zの**Standard/Advanced双方**(ユーザー正式承認2026-10-26 APPROVED_FOR_PRODUCTION。Std除外は認められない)。Std = chunkごとに既存の6%減速(`generate_a2_segment_with_slowdown`)を適用 → 0.2秒無音を減速後に挿入して連結。Std X/Y=IMPLEMENTED_PENDING_EVIDENCE(正式runtime evidence未取得)、Z Std=DESIGN_READY」。2920行のStatus「Y/Z対象外」「対象外: Standard(a2)…Family Y」の記述も同様に是正。
- DECISION_LOG: 「2026-10-26 ユーザー正式承認(APPROVED_FOR_PRODUCTION): Chunk分割はX/Y/ZのStd/Adv双方に適用。Std除外はユーザー承認なき設計判断でありPM Gate・承認管理の不備と認定、是正。再発防止=対象レベルを狭める場合はユーザー承認必須。Phase 1a: X/Y Std配線実装(chunk別6%減速→0.2秒→連結、IMPLEMENTED_PENDING_EVIDENCE)。Opus条件A: 合成方式が既定方針(新規後処理・閾値なし)のため実装前待ち不要と判定、レビュー依頼文は`OPUS_REVIEW_REQUEST_01.md`」。
- OPEN-532更新: Status を「ユーザー判断待ち」から「承認反映済み・X/Y Std=IMPLEMENTED_PENDING_EVIDENCE、Z Std=DESIGN_READY、Phase 2 runtime evidence未取得」へ。残件: Z Std実装(次委任)、runtime evidence(X Std/Y Std・Adv/Z Std)、Y実記事の不発火(OPEN-527の文境界/本文契約はユーザー判断待ちのまま=本件で追加承認されていない)。分類=修正へ進む(同一案件の後続委任で着手)。
