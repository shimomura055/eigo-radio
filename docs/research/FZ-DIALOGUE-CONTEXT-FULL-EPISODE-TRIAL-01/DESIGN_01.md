# DESIGN_01 — 全編通しTrial(セリフ全件ctx新規生成 + 地の文再利用 + DEV隔離の通し組立)

管理ID: FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01 / 性質: Trial(DEV専用経路、Production採用は未承認、到達上限=VALIDATED(限定)/REJECTED/USER_DECISION_REQUIRED)。
ユーザー原文: `docs/pm/delegation_log/2026-10-26_FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01_USER.md`。方式の正本: Round 1/2 `docs/research/FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01/{DESIGN_01,DESIGN_02,PREREGISTERED_CRITERIA_02,OPUS_REVIEW_01}.md`。
本書は設計のみ(本委任_01では組立・生成コードを書かない)。実装は Opus条件Aレビュー(`OPUS_REVIEW_REQUEST_01.md`)反映後の委任_02。

## 0. 既存仕様との整合(照合したファイル:行)

| 項目 | 照合先 | 結論 |
|---|---|---|
| ctx方式(CONTEXT区画書式・EMOTION_DEVELOPER rule 1〜10・leakage・ASR検査) | `er118_fz_dialogue_context_tts_trial_01.py:241-282`(EMOTION_DEVELOPER/SCHEMA)、`:342-396`(CONTEXT_HEAD/TAIL・build_context_block)、`:513-572`(leakage_check・verbatim_check) | **無変更で import 再利用**(`er118_fz_full_episode_trial_01.py` は module globals を作品×レベルへ切り替えるだけ) |
| 現行style・Voice・速度 | `er063_family_z_audio_01.py:58-60`(Z_ADV_DIALOGUE_SPEEDUP_TEMPO=1.06)、`:917-929`(dialogue: Adv=外側ループ+atempo1.06、Std=速度後処理なし)。各clipの `style.effective_style_prefix_sha256 == add26d27…`(= `t.EXPECTED_BASE_STYLE_SHA`)を4単位の全53 clipで一致確認(`inventory.json` `all_base_style_sha_match=true`) | ctx styleは現行 `ENGLISH_STYLE_PREFIX` + CONTEXT追記のみ。Voice=Production結果の実Voice、速度=Std無し/Adv atempo1.06(承認済み速度仕様v2を変更しない) |
| Production組立 | `er063_family_z_audio_01.py:1831-1899`(`run_assembly`: gain→sequence→assemble_with_timeline→headroom→wav+timeline)、`:1810-1829`(`build_z_sequence`)、`er026_family_z_fiction_production_runner_01.py:2389-2392`(呼出) | **同一関数をimportして入力dirだけ差し替える**(§3)。無音長・gain・headroom規則は関数内部でProductionと同一 |
| Production sink隔離 | `er113_fx_paragraph_chunk_trial_01.py:49-63,660-700`(`redirect_production_sinks`/`PROTECTED_STORES`)、Round 2 `generate_arm`(`er118_fz_dialogue_context_tts_trial_01.py:935`) | 生成時に同一の隔離を適用(§3) |
| retry上限 | `er003_v1_n3_01_tts_generate.py:434-479`(`generate_with_a2_slowdown_outer_loop`、通算3回=`PRODUCTION_MAX_TTS_ATTEMPTS`) | Trialも同一上限。上限を独自に変更しない |

## 1. 対象と生成単位

- 4単位(作品×レベル): 猿の手 Std(a2)/Adv(b1b)、メロス Std/Adv。セリフ合計 **53 clip**(`INVENTORY_01.md`)。未制作レベルは追加しない。
- 各clip 1 take(通し版の評価が目的。take間ばらつきは「同一話者内ばらつき」で代替観測、§5)。
- 猿の手 Adv のRound 2生成8 clipは**流用しない**(新規生成。Trial専用key[managed_id・take・style sha]と別pathに出力し、Round 2出力とは分離)。メロスは全件新規。
- **地の文側は全て再利用**: story narrator clip、Intro/Welcome/Topic/Preview/Key Phrase/Comment/Outro(= Production run `<lv>/narration/` と共有素材)。

## 2. セリフ生成(委任_02)

(a) ctx生成: Round 2と同じ `bvoices.generate_voice_body_wide_margin(text, out_path, voice, style_prefix_override=style)` を直接呼ぶ(`t.generate_arm` と同じ)。
   - style = `t.style_for_arm("ctx", ctx, note)`、note = Phase 1aの感情情報にFableがaccept/discardを付けたもの(`load_reviewed_notes(require_review=True)`相当を作品×レベルで)。
   - **Adv**: Production(`er063:917-928`)と同じ `n3_tts.generate_with_a2_slowdown_outer_loop(clip_id, text, out_path, lambda max_attempts: bvoices.generate_voice_body_wide_margin(text, out_path, voice, max_attempts=max_attempts, style_prefix_override=style), slowdown_pct=Z_ADV_DIALOGUE_SLOWDOWN_PCT)`。速度atempo1.06・**速度後ASR再検証・通算3回上限**もProductionと同じ。Round 2では速度後ASRを行わなかった(`make_final_equivalent`)ため、本Trialで品質Gate(ユーザー原文§4C「既存の必須音声品質Gate」)を満たすため Production と同一の外側ループに揃える(方式の変更ではなく検査の厳格化。CONTEXT書式・感情付与方式は不変)。
   - **Std**: 速度後処理なし(`std_dialogue_none`)で `generate_voice_body_wide_margin(..., style_prefix_override=style)` を1回呼出(内部retryはProduction既定)。
   - NG時の再生成は上記関数の既存retry上限内のみ。回数(`tts_generations_used`・attempts_log)をclipごとに記録。1 clipのNGでrun全体を中断せず記録して続行(Round 2 Opus M5と同じ)。上限到達でNGのclipは、その事実を記録し、通し版では**Production原clipで代替せずに欠番として報告**(代替すると「全件新規」要件と比較条件が崩れるため。代替方針はFable判断)。
(b) 同一人物の一貫性: **方式変更なし**。CONTEXTに話者名(`Speaker of this line:`)は既に含む。新規指示は足さない。評価は§5の話者内ばらつき指標で観測する(Voiceは話者ごとに固定=Production実Voice)。
(c) 費用会計: `raw_usage_log.jsonl`(`er005_cost_logger`)をTrial専用に1ファイル(`er118_output/fz_full_episode_trial_01/raw_usage_log.jsonl`)。clip別cost・attempt数・elapsed_sを`result.json`へ。

## 3. DEV隔離の全編組立(Opus条件A論点①②の中心)

**入力dirを複製して差し替える。Productionのdir・store・manifestへ書かない。**

```
er118_output/fz_full_episode_trial_01/<work>/<level>/run/        # trial_run_dir(Productionの <run>/ と同じ形)
   <level>/narration/     # Production run <level>/narration/ を copy(地の文・shell・KP・Comment等)。
                          # dialogue clip だけ Trial版(速度加工後wav、<clip_id>.wav)で上書き。
   <level>/audit/tts_generation_results.json   # Production結果をcopy(chunk plan解決用)。dialogue segmentはTrial結果で置換
   <level>/assembly/Family_Z_<story_key>_<level>.wav + timeline.json   # run_assembly の出力先(= trial_run_dir 配下)
```
- 組立: `a63.run_assembly(trial_run_dir, level, story_clips, kp_items, story_key=…, kp_third=…, chunk_plans=…)`(Productionの呼出 `er026_…runner:2391` と同一引数)。`story_clips`/`kp_items`/`chunk_plans` は Production run のファイルから同じ決定論で再構成(`load_level_inputs` の読取部分と同じ手順。Production dirは読取のみ)。無音長(0.2/0.5/0.8/1.0等)・clip単位gain(target_rms)・headroom safety valveは `run_assembly` 内部=**Production規則そのもの**。
- **組立ハーネスの自己検証(API 0、Trial生成前に実施)**: trial_run_dir に **Productionの原dialogue clipをそのまま入れて**同じ `run_assembly` を実行し、(i)timelineのpart列と各duration (ii)wavのサンプル差(最大絶対差)を、Production組立 `…/assembly/Family_Z_*.wav` と比較。一致でなければ、組立入力の再構成が異なると判断して**生成前にSTOP**(Trial差の原因へ組立違いが混ざらないようにする)。
- **Productionに書かないことの保証(多層)**:
  1. 書込先は全て `OUT_ROOT=er118_output/fz_full_episode_trial_01/` と `PAGE_ROOT=user_test/fz_full_episode_trial_01/`。専用の `safe_write(path)` が書込直前に絶対パスが両root配下であることを `assert`(違反はSystemExit)。`run_assembly` は `{run_dir}/{level}/assembly` にのみ書くため(`er063:1841,1893-1905`)、run_dirにtrial_run_dirを渡す限りProduction dirに触れない。
  2. 生成時は `t113.redirect_production_sinks(f"{OUT}/sinks")`(attempt_history・human_review_log・telemetry・Ledger・Local Rewrite出力をDEV側へ)。out_pathを `…/<level>/narration/<id>.wav` 形にするため review_lock_state も Trial側 `…/<level>/audit/` に作られる(`er011_human_review_lock_01.py:139,156`)。
  3. 生成前後で `PROTECTED_STORES`(attempt_history・HR queue・telemetry・Master Store manifest・reuse_telemetry・ledger 等、`er113:55-63`)と、**Production runのdialogue/narration wav・tts_generation_results・timeline・公開mp3・公開html**のsha256をsnapshotし、差分が1件でもあればSTOP(Round 2の `snapshot_protected` / `protected_diff` と同形に拡張)。`scan_repo_mtime` も併用。
  4. test(接続試行0): (i)safe_writeがProduction pathを拒否 (ii)trial_run_dirがProduction runと別である (iii)組立入力の差分がdialogue clipのみ (iv)`gen`/`assemble`はPHASE1_GO.json無しで拒否 (v)Round 1/2 test 54件PASS維持。
- Production版の通し音声は**再生成しない**。公開済み `user_test/family_z_<work>_0x/<audio_standard|audio_advanced>/<Prefix>_<lv>_full.mp3` を参照(`INVENTORY_01.md` で4本とも実在確認済み)。Trial版の通しmp3は、同じ書出し関数(`build_pages` が使うmp3変換)でTrial wavから作る。**公開物の上書き禁止**: Trial版は新規 `user_test/fz_full_episode_trial_01/` のみ(公開Production pageのファイルは更新しない。snapshot差分で確認)。
- 比較条件の差(明示): 同一=地の文音声・Intro/Preview/KP/Comment/Outro・無音規則・gain規則(clip単位)・headroom・Voice・速度仕様・現行style本体。**差=セリフclip音声のみ**。副作用として(1)セリフのclip単位gainはTrial音声のRMSから再計算される (2)Trialセリフの長さが異なるため通し全体の秒数・各セリフの開始時刻はずれる (3)セリフの合格基準はProductionと同じASRカスケード。
- 未確定リスク(Opusに確認を依頼): `generate_with_a2_slowdown_outer_loop` が `review_lock` / HR log に書く先が `redirect_production_sinks` で完全に隔離されるか(Round 2は外側ループを使わなかったため、この関数の隔離は未実証)。実装時に sink redirect 下で呼び、Production store のsha不変を実測してから本生成する。

## 4. 試聴ページ(`user_test/fz_full_episode_trial_01/`、noindex、PAGE_NOTICE)

- `index.html`(2作品×2レベルの案内)と作品ページ(各ページ内にStandard/Advanced節)。各レベルに:
  1. **Trial版 通し再生**(文脈・感情付きセリフ) 2. **Production版 通し再生**(公開済みmp3の複製を新規dirに置く=Production公開物は変更しない) 3. セリフごとの個別A/B(Production原音 vs Trial、速度加工後の最終相当) 4. セリフ本文+前後文脈(`extract_context` の決定論部)+感情情報の日本語要約 5. Standard/Advancedの区別(ユーザー向け表記はStandard/Advanced、内部A2/B1ラベルを出さない)。
- 通し再生に「セリフ位置のチャプター(timeline由来の開始秒)」を付け、Trial/Productionを同じセリフ番号へジャンプして比較できるようにする(ユーザー原文§3「通しで聴いたとき」+「セリフごと」を1ページで)。
- 音量差の注意書き(Round 2と同様)。「機械指標=開発側の参考、最終はユーザー試聴」と明記。Production採用でないこと、既存音声は差し替えていないことを明記。

## 5. 評価(`PREREGISTERED_CRITERIA_01.md` で観測前に固定)

機械指標は事前登録02の指標を流用し、本Trial固有の3指標を観測前に定義。Status写像は C(基本品質)優先。A(表現・没入感)とB(安定性の聴感)は人手評価項目として列挙し機械で代替しない。詳細は同書。

## 6. 実行順(委任_02)と並列化

1. [API 0・Opus待ちと並行可] 組立ハーネス実装+自己検証(Production原clipで再組立→Production wavと一致確認)、評価script、ページbuilder、test。※組立コード自体はOpus条件Aの対象なので、Opus反映前にProduction経路へ接続しない(DEV専用ファイル内で実装するのみ)。
2. Fable: 感情情報レビュー(accept/discard、`EMOTION_CANDIDATES_01.md`)→ `emotion_review.json` 4件。
3. 有料生成: 4単位を `TTS_EXECUTION_MODE=STANDARD` で。同時起動は避け、単位間の間隔≥150秒(Round 2委任_05の27秒間隔は逸脱だったため)。1単位=1起動、再起動しない。起動前に `stop_scope_check`。Guardrail 100円(T-3定型文)。
4. 解析(API 0): ASR逐語一致・leakage・指標・組立・通しmp3・ページ・Production snapshot差分。
5. 評価・Fable独立評価・費用/時間の実測集計・量産想定増分(`BUDGET_PLAN_01.md` §3の式へ代入)。
