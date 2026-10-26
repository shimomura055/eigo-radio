転記: Fable→sonnet-worker 委任_02、2026-10-26。Opus(opus-consultant)の出力を無改変で保存

# OPUS_REVIEW_01 — 条件A独立レビュー(FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01、実装前)

レビュー者: Opus(読み取り専用、API 0)。対象: DESIGN_01 / PREREGISTERED_CRITERIA_01 / BUDGET_PLAN_01 / INVENTORY_01 / `er118_fz_full_episode_trial_01.py`。結論: **設計の骨格(Production関数をimportしてTrial専用ディレクトリで実行+生成前の自己検証+sink差替え)は妥当。ただし下記M-1〜M-8を実装前に反映すること**。Production採用可否は判断しない。

## 必須修正(M)

**M-1 [論点①] NG/途中音声が組立入力に残る経路を断つ。**
- 根拠: 生成関数は出力先に書いてからASR判定する(`er012_b_family_voices_production_01.py:548`)。Adv外側ループは`<id>_original.wav`を上書きし、速度加工後の音声も書く(`er003_v1_n3_01_tts_generate.py:211-228`)。DESIGN_01 §3はこの出力先をProductionからcopyした`trial_run_dir/<lv>/narration/`にしている。このため上限到達でNGのclipは、NG音声で上書きされたまま通し版に入る(「欠番」にならない)。
- 修正: 生成はclipごとの別ディレクトリ(Round 2と同形 `…/gen/<cid>/<lv>/narration/<cid>.wav`)で行う。status==OKかつC2〜C4が成立したclipだけを`trial_run_dir`へcopyする。組立前に「dialogue wavのsha == 採用済みTrial結果のsha」をassertする。

**M-2 [論点①②] copyで残るProduction原音の`<id>_original.wav`を、全dialogue clipについてTrialディレクトリから削除する。**
- 根拠: Std(速度加工なし)は`_original`を作らない。そのためProduction原音の`_original.wav`が残る。
- 影響1: `verify_z_speed_profile`はStd会話で`_original`が残っていれば長さ比≈1を要求する(`er063_family_z_audio_01.py:1642-1669`)。C6が誤って不成立になる。
- 影響2: 解析側の「`_original`があればそれを原音とする」規則(`er118_fz_full_episode_trial_01.py:137-138,253-254`と同形)により、Trial clipの指標をProduction音声で測ってしまう。
- 修正: copy直後に削除する。Advは生成で新しく作られた`_original`だけを置く。testで「Trialディレクトリ内のdialogue `_original`のshaが、Productionのどのファイルとも一致しない」ことを確認する。

**M-3 [論点①C6] Trialの`tts_generation_results.json`を正しく作る。**
- 根拠1: copyしたentryの`path`はProduction narrationの絶対/相対パスである。Gateのhash照合はそのpathが存在すればそれを読む(`er003_v1_n3_01_assemble.py:213-217`)。dialogue entryを置き換え損ねると、GateはProduction音声を検査してPASSしてしまう。
- 根拠2: `verify_z_speed_profile`は`speed_profile`・`reuse_key.speed_profile`・`clip_kind`を要求する(`er063:1653-1661`)。
- 修正(1): dialogue entryは`a63.build_entry(spec, trial_out_path, result)`(`er063:1091-1158`)で作る。さらに`trial_style_sha256`/`trial_reuse_key`を追加フィールドとして付ける(build_entryの`style`は既定style shaを記録するため)。
- 修正(2): 非dialogue entryの`path`/`narration_path`も`trial_run_dir`へ書き換える。
- 修正(3): Productionの`human_approval_path(level_dir)`ファイルがあればcopyする。無いとHUMAN_APPROVED済みの地の文で誤blockする(`er003_v1_n3_01_assemble.py:480-488`)。
- test: 「Trial結果の全pathがOUT_ROOT配下」。

**M-4 [論点①] 書込ガードの実効範囲を正しく定義し、穴を塞ぐ。**
- (a) 前提の訂正: `safe_write`は本moduleの書込しか守らない。`run_assembly`(`er063:1894-1910`)、生成関数、review_lock(`er011_human_review_lock_01.py:172-176`)は内部で直接書く。呼出前に`run_dir`/`out_path`の`os.path.realpath`がOUT_ROOT配下であることをassertする(文字列prefix比較ではなく)。
- (b) copyは`shutil.copyfile`/`copy2`に限る。hardlink・symlink・junctionは禁止。copy後に全ファイルの`st_ino`(またはsha)がProduction側と別ファイルであることを確認する。hardlinkだと上書き時にProductionファイルが壊れる。
- (c) `a63.build_pages`は`pages_dir`既定値がProductionのメロスページ(`er063:1918,2107`)なので呼ばない。mp3化は`sf.write(..., format="MP3")`(`er063:1991`と同一)を、PAGE_ROOT配下の出力先へ直接行う。
- (d) mtime走査は`t.scan_repo_mtime`を使わない(除外先がRound 1のdir、`er118_fz_dialogue_context_tts_trial_01.py:825`)。OUT_ROOT/PAGE_ROOTを除外に入れた版を使う。

**M-5 [論点②] 「差はセリフclipのみ」をTrial組立そのもので検証する(自己検証だけでは不足)。**
- 根拠: `target_rms`はpreviewと`story_clips[0]`のRMSに依存する(`er063:1861`)。headroom安全弁は全編一律のscalarで掛かる(`er003_v1_n3_01_assemble.py:1001-1011`)。現状は4単位とも先頭story clipが地の文で、会話のpeakは0.95上限(`er003_b1_p9a_audio.py:459`)<閾値0.98のため、理論上は不変になる。
- 修正: Trial組立後に次の3点をassertし、どれか1つでも違えばSTOPする。
  1. `gain_report.target_rms`がProductionと一致する
  2. dialogue以外の全labelのgain値がProductionと一致する
  3. `headroom.scalar`が一致する
- 併せてC5(ii)「作動回数≦Production」をこのscalar一致へ置き換え、`story_clips[0]`が非dialogueであることをtestにする。

**M-6 [論点⑤] `use_case`が切り替えないRound 1/2 module(`t`)のグローバルに依存する関数を、本moduleから呼ばない。**
- 根拠: `_T_GLOBALS`(`er118_fz_full_episode_trial_01.py:73`)には次が無い: `OUT_DIR`/`GROUP_DIR`/`COST_LOG`/`PHASE1_GO_FILE`/`TARGETS`/`TARGET_IDS`/`MANAGED_ID`/`TRIAL_CAP_JPY`。このため次の関数はRound 1(賢者の贈り物)の設定のまま動く。
  - `t.generate_arm`: Round 1のcost log・cap・TARGETSを使う(`:850-935`)
  - `t.load_reviewed_notes()`の既定path(`:742-743`)
  - `t.snapshot_protected`/`protected_paths`: Magiのclip idを新作品のNARR_DIRで探す(`:676-686`)
  - `t.est_next_clip_jpy`: Stdでは存在しない`_original`を読む(`:846`)
  - `t.trial_reuse_key`: Round 1のMANAGED_IDが入る(`:428`)
  - `t._require_go`/`t._stop_check`: Round 1のID(`:660-673`)
- 修正: 純関数だけを許可listとして使う(extract_context/build_context_block/style_for_arm/build_prompt/tts_text_for/leakage_*/comparison_validity/analyze_wav/est_tts_jpy/capture_tts_requests/validate_emotion_items)。上記の関数は本module側に再実装する(`load_reviewed_notes`はpath明示で呼ぶ)。testでは、上記関数をmonkeypatchで例外化して本moduleの`gen`/`assemble`が通ることを確認する。

**M-7 [論点④] C2をProduction Gateと同じ水準に揃える。**
- 根拠: `t.verbatim_check`の`token_equal`は厳密一致である(`er118_fz_dialogue_context_tts_trial_01.py:564-568`)。Productionが合格とする判定(ORTHOGRAPHIC_EQUIVALENT_MATCH、CMU同音、Secondary救済、PASS_WITH_WARNING。INVENTORY_01でも3件)を不合格にする。blocking条件に使うと、ユーザー承認なしに品質基準を引き上げることになる(Charter原則1)。
- 修正: C2のblocking条件は「Production ASRカスケードの最終判定がPASS系、かつrepetition QA済み」とする。`token_equal`/`similarity`は観測値として全件報告する。
- C3(`leakage_final.flagged`)はTrial固有のリスクなのでblockingのまま維持してよい。ただしASRの幻聴による誤検出があり得るため、flagged時は「Fableが聴いて確認し、記録してから判定」の手順を事前登録する。

**M-8 [論点④] NG clipの扱いを生成前に固定する(現状は「代替方針はFable判断」と事後判断の余地が残っている、DESIGN_01 §2(a))。**
- 推奨案:
  - NG音声は絶対に採用しない(M-1)。
  - 通し版の該当箇所にはProduction原音を置く。ページとチャプターに「この箇所は現行音声」と明示する。欠番の無音は没入感の評価を壊すので採らない。
  - NG件数は「再生成率」と「NG率」の結果として報告する。
- Status写像: 「NG≦2 clip(全体の約4%以下)ならC1は記録付き成立としてユーザー試聴へ。超えたらREJECTED候補」のように閾値を観測前に書く。閾値の値はFableが決めてよいが、生成前に固定すること。

## 推奨(R)

**R-1 [①]** Productionの`<run>/`配下とpages dir全体をtree-hash(全ファイルのsha)でsnapshotする。`<lv>/audit/review_lock_state.json`と`er011_output/local_rewrite_recovery`を対象に含める。
- 注意: 作業ツリーでは保護store(attempt_history・HR queue・manifest・ledger)が既に変更中である。生成中に他のProduction runを並行起動しないことを起動条件に書く(誤STOPを防ぐため)。

**R-2 [①b]** Adv外側ループは、sink差替えと`er109_xz_scope_01.family_scope("Z")`+`er078_secondary_run_scope.with_secondary_run(<OUT_ROOT配下>)`の内側で呼ぶ(Round 2の`er118_fz_dialogue_context_tts_trial_01.py:935-937`と同形)。scopeが外れると、segment_idの導出や発音供給の挙動がProductionと変わる。
- 本生成前に、gen_fnを差し替えた無料のdry-run(API 0)で外側ループの書込先を実測する: append_attempt_history_event / _log_human_review / finalize→record_outcome の3経路。

**R-3 [②] TEXT同一性。** `tts_text_for`は`_pnap_supply`経由で、Z scope内では発音供給が有効になる(`er063_family_z_audio_01.py:871-882`、`er103_pronunciation_tts_supply_01.py:48,330-333`)。scope内で53 clipのTTS入力を計算し、Production実送信の入力(記録があれば。無ければ現行ledger copyで再現)と突き合わせる。差分があれば生成前にFableが判断する。特にメロスは前runの再利用で、供給機能の導入前に生成された可能性がある。

**R-4 [②a]** 自己検証の比較対象はProductionの組立wavでよい。ただし、公開mp3の長さがそのwavと一致することも確認する(メロスの速度仕様v2再処理で組立がstaleでないかの確認)。
- 試聴ページのProduction版は、自己検証で一致した再組立wavを、Trialと同じ`sf.write`でmp3化したものを使うと、エンコード経路が完全に揃う。
- 比較項目には`gain_report`と`headroom`のdict一致も加える。

**R-5 [②c] Adv外側ループの採用は妥当。** Production Advの会話も同じ外側ループで確定しているので、Trial vs Productionの生成条件はRound 2より揃う。文脈・感情付与方式(CONTEXT書式・EMOTION_DEVELOPER)は変わらない。Round 2との再生成率比較は条件が違う、と明記すれば足りる(既に§6にある)。

**R-6 [③] 費用会計。**
- (a) k(call/clip)と円は、`raw_usage_log.jsonl`のprovider別実績(TTS・OpenAI ASR・Azure)を正とする。`capture_tts_requests`はminimal_fallbackを過少計上し得る(`er118_fz_dialogue_context_tts_trial_01.py:841`)。
- (b) c_asrは定数0.032円ではなく、clip当たりのASR実費で測る。Advは生成ごとに速度前と速度後の2回+Secondaryが走り、ctxによるPrimary NG増加がAzure呼出を増やし得る。
- (c) k_prod=1.019は53 clipで再試行1件、しかもメロスは継承値で精度が低い。Round 2のbase arm(同一session・同一コード)の実測kも並べて、Δを幅(k_prod版/R2 base版)で示す。
- (d) 感情情報レビューの自動化費用は「未計上(要設計)」とし、0円扱いにしない。
- 規模感の参考: 1 call約0.4円×53なので、k_ctxが1.5でもΔは数円/set。70円/setに対する結論はk_ctxが極端でない限り変わりにくい。

**R-7 [④]**
- (a) `noise_band_r2.json`は生成前に作成し、そのshaをresult.jsonに記録する。PREREGISTERED_CRITERIA_01の改訂と同時に生成前にcommitし、時刻で固定を証明する。
- (b) N1は話者あたり3〜5 clipのCV比なので偶然で2倍を超えやすい。「フラグ率」を見出しにせず、両側の値を全件併記する(needs_listenのままでよい)。
- (c) N2(a)とN3は、Trial/Productionの両側を同じ段階の音声で測る。clip指標は加工前の原音、N3は組立後wav。
- (d) C6は上記M-2/M-3を入れれば無料(API 0)で実行できる見込みなので、「未実施=不成立」の厳しさは妥当。

**R-8 [⑤]**
- (a) `use_case`の復元はfinallyで安全。ただし単一thread前提なので、並列実行を禁止するassert(実行中flag)を入れ、例外時の復元をtestする。
- (b) `_production_voice_map`は同じ話者でVoiceが不一致でも黙って上書きする。testで「同一speakerの全clipが同一Voice」と、`king`→`dionysius`の明示alias経由で`voice_assignment.json`と一致することを確認する。
- (c) 方式関数を引数化する別moduleへの分離は今回不要。量産化の段階でM-6の許可listを基に行う。

**R-9** 本moduleの`_require_go`は上限を5円に固定している(`er118_fz_full_episode_trial_01.py:305`)。生成用にはscope=`Phase 1b`(上限100円)を別に設ける。Std会話にctxを付けるのは今回が初めて(Round 1/2はAdvのみ)なので、試行時のリスクとして明記する。

## 問題なし確認(OK)

- **OK-1**: 外側ループの書込先は、すべて呼出時点のmodule変数を参照している。具体的には`ATTEMPT_HISTORY_PATH`(`er011_human_review_lock_01.py:112,194-195`)、`HUMAN_REVIEW_LOG_PATH`(`er006_secondary_asr_01.py:481,523`)、Lock store(出力先からの導出、`er011:155-176`)。したがって`redirect_production_sinks`(`er113_fx_paragraph_chunk_trial_01.py:49-54,660-711`)と、OUT_ROOT配下の出力先で隔離できる。ledgerはcopyへ差し替えられ(`er113:678-685`)、`get_hint_for_text`は読取のみ。
- **OK-2**: `run_tts_stage`(`er063:1367`)を使わず生成関数を直接呼ぶので、Master Store・reuse key・manifestは触れない(論点①c)。
- **OK-3**: `run_assembly`の書込は`{run_dir}/{level}/assembly/`のみ(`er063:1894-1910`)。共有素材(intro/outro/notification mp3、chunk検査)は読取のみ。chunk plan再構成の誤りは、サンプル厳密一致の自己検証で検出できる(論点①d)。
- **OK-4**: 2作品×2レベルのセリフclipを1 takeだけ新規生成し、Production側は追加takeを作らない費用設計(期待25円/天井75円)は、承認枠内で目的に対して必要十分。

## 残リスク

- 「1 take vs 1 take」のため、clip個別の差は偶然と区別できない。効果判定はユーザーの通し試聴に依存する(設計どおり)。
- 外側ループの隔離は、R-2のdry-runと生成前後のsnapshotで実測されるまでは未実証。
- 他のagentやProduction runが並行して共有storeに書くと、snapshot差分が誤STOPになる(安全側の誤り)。
- 発音供給/ledgerの時点差によるTEXT差(R-3)が見つかった場合は、比較条件の扱いをFableが生成前に判断する必要がある。
