# OPUS_REVIEW_REQUEST_01 — 独立技術レビュー依頼(条件A: 新しい処理フロー設計、実装・有料生成の前)

管理ID: FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01 委任_01 / 依頼元: Fable(sandwich-pm)→ Opus。根拠: PM_GOVERNANCE 11-3 条件A(DEV隔離での全編組立=新しい処理フロー)。
**レビュー対象はコードではなく設計**(コードは本委任で未実装)。TTS生成は未実施。コードの読取対象は下記のとおり。結論は「重大/必須修正(M)/推奨」で。

## 1. 背景(3行)
ユーザー原文(`docs/pm/delegation_log/2026-10-26_FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01_USER.md`): Round 1/2のA/B Trialで文脈・感情付きTTSは「場面によって良くなっている感じはある。ただ、ばらつきも大きい」。次段階として『猿の手』『走れメロス』をStd/Advで、**セリフ全件をctx方式で新規生成**し、地の文は既存音声を再利用して**最初から最後まで通して聴けるTrial版**を作る(Production公開物は上書きしない)。
Round 1/2の方式(CONTEXT書式・EMOTION_DEVELOPER・leakage・ASR検査)は**変更しない**。今回新しいのは、(1)全セリフ53 clip規模の生成 (2)Productionの組立関数を使ったDEV隔離の通し組立 (3)通し評価と量産原価の算式。

## 2. 読むファイル(必要箇所のみ)
- 設計: `docs/research/FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01/{DESIGN_01,PREREGISTERED_CRITERIA_01,BUDGET_PLAN_01,INVENTORY_01}.md`
- 実装済み(Phase 0のみ): `er118_fz_full_episode_trial_01.py`(`configure_case` / `inventory` / `budget` / `llm`)
- 組立: `er063_family_z_audio_01.py:1810-1899`(`build_z_sequence`/`run_assembly`)、`er026_family_z_fiction_production_runner_01.py:2389-2392`、dialogue生成 `er063:917-929`、外側ループ `er003_v1_n3_01_tts_generate.py:434-479`
- 隔離: `er113_fx_paragraph_chunk_trial_01.py:49-63,660-720`(`redirect_production_sinks`/`PROTECTED_STORES`)、`er011_human_review_lock_01.py:139-156`
- 方式の過去レビュー: `docs/research/FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01/OPUS_REVIEW_01.md`(M1〜M6)

## 3. 論点(5つに絞る)

**① DEV隔離の全編組立でProduction汚染が起きない設計か**(最重要)
- 設計: Production runの `<lv>/narration/`・`audit/tts_generation_results.json` をTrial専用 `trial_run_dir` に **copy** し、dialogue wavだけTrial版で上書き→`a63.run_assembly(trial_run_dir, …)` を Production と同一引数で呼ぶ。書込先は `{trial_run_dir}/{level}/assembly/` のみ。多層防御= `safe_write` assert / `redirect_production_sinks` / 生成前後のsha256 snapshot(保護store+Production run音声・結果・timeline+公開mp3/html)/ test。
- 問い: (a)`run_assembly` と下位(`asm.assemble_with_timeline`・`chunk_tts`・`p9a`)が trial_run_dir 以外(共有asset以外)へ書く経路は無いか。(b)`generate_with_a2_slowdown_outer_loop`(Adv生成の外側ループ)が `review_lock`(`append_attempt_history_event`)・HR log・`finalize_a2_slowdown_final_ng` で書く先が `redirect_production_sinks` で完全に隔離されるか(Round 2はこの関数を使っておらず**未実証**。実装時にsink redirect下で呼び、保護storeのsha不変を実測する計画)。(c)Master Store / reuse key / manifest に触れない保証として、`run_tts_stage` を使わず生成関数を直接呼ぶ方針(Round 2と同じ)で十分か。(d)chunk plan(Advの長い地の文)の再構成を `load_level_inputs` を使わず Productionファイルから再構成する設計の安全性(組立自己検証が検出できるか)。

**② 比較条件の同一性**(地の文再利用・無音/gain規則)
- 設計: 差はセリフclipの音声のみ。無音長・clip単位gain・headroom・Voice・速度(Std無し/Adv atempo1.06)はProduction関数内部の規則そのもの。生成前に**Production原clipで再組立→Production wavとtimeline/サンプル一致**を確認する自己検証を置く。
- 問い: (a)この自己検証で足りるか(Melosは速度仕様v2再処理後でrun_e2e_06の組立wavが最新か、公開mp3は別途書出しのため比較基準をどのwavに置くべきか)。(b)Trialセリフの長さ違いで通し秒・チャプター位置がずれる点と、clip単位gainによりセリフ音量がTrial側で再計算される点を、評価の交絡としてどう扱うか(ページ併記以外に必要か)。(c)Adv生成に Production と同じ外側ループ(速度後ASR再検証つき)を使い、Round 2の「速度加工は後付け・ASRなし」から変えることの是非(比較条件の勝手な変更になるか、品質Gate準拠か)。

**③ 費用会計**(実Trial支出 vs 量産想定原価、再生成の扱い)
- 設計: `BUDGET_PLAN_01.md` §3 の算式 `Δ/set = Σ n×[(k_ctx−k_prod)(c_base+c_asr) + k_ctx(c_ctx−c_base)] + 2c_llm`。k_prod=1.019(54 call/53 clip)、k_ctxは実測。Trial見積=期待25円/保守31円/天井75円(全て300円以下)。
- 問い: 算式に漏れ(速度後ASRの追加call、Azure secondary、感情情報のレビュー工数=量産では自動化が必要な点)はないか。k_prodをProduction attempt実績から取る妥当性(メロスは前run再利用のため実績が1.0に偏る恐れ)。base armを作らず Production 実績と比較する設計で、再生成コストの増分を公平に推定できるか。

**④ 事前登録指標の妥当性**
- 設計: `PREREGISTERED_CRITERIA_01.md` — Status判定は基本品質C1〜C7のみ(blocking)。機械の効果指標は観測のみ。新規N1(話者内ばらつき: 2倍超かつ絶対増分)・N2(clip内無音>700ms、速度0.6〜1.6倍外)・N3(境界RMS段差+3dB)・N4(感情強弱別)。自然ゆれはRound 2のProduction vs base差を固定。
- 問い: (a)閾値(2倍/+0.05CV/+1.0半音、700ms、0.6〜1.6、+3dB)は観測前の定義として妥当か。(b)Take 1回のみ・Production 1 takeとの比較で、N1〜N3が偶然差を過大評価しないか。(c)C6(`run_audio_gate`のtrial_run_dir適用)の可否と、「未実施=不成立扱い」の厳しさは適切か。

**⑤ 既存 er118 との責務分離**
- 設計: 新規 `er118_fz_full_episode_trial_01.py`(DEV専用)が `er118_fz_dialogue_context_tts_trial_01.py` を import し、**module globalsを書き換えて**(`t.LEVEL`/`t.PLAN_PATH`/`t.SPEAKER_DISPLAY`/`t.EMOTION_DEVELOPER`/`t.voice_map` 等)再利用する。既存ファイルは無変更。
- 問い: globals書換えは Round 1/2 の挙動を壊さないか(import順・並行利用)。このままの責務分離でよいか、方式関数だけを引数化した別モジュールへの分離が必要か。メロスの `t.voice_map` をProduction結果の実Voiceから取る上書き(plan側speaker `king` と voice_assignment側 `dionysius` が異なるため)の妥当性。

## 4. 前提・制約(再確認不要)
- Production Prompt・TTS設定・音声生成方式・Gate・閾値・reuse key・flagは変更しない。新flagなし。Production採用は人間ユーザーのみ(本Trialの到達上限はVALIDATED(限定)/REJECTED/USER_DECISION_REQUIRED)。
- 感情情報LLM(Phase 1a)は設計と独立のため先行実施済み(Round 2と同一方式、4 call、上限5円、結果は `EMOTION_CANDIDATES_01.md`)。生成(Phase 1b)は本レビュー反映後。

## 5. 回答形式のお願い
各論点について 判定(問題なし/修正推奨/必須修正)、根拠(ファイル:行)、必須修正の具体案。最後に必須修正一覧。
