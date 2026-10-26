## 管理ID
FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01 委任_02(2026-10-26 JST、Phase 1b: Opus条件Aレビュー反映(M-1〜M-8必須、R採用分)→Fable感情レビュー結果の転記→無料dry-run(R-2)→セリフ53 clip生成(4単位直列)→DEV隔離の全編組立→試聴ページ公開→機械評価・費用/時間評価→報告)。並行: FAMILY-Y-FEEDBACK-COMMENT2-PAUSE-01 委任_03(`er121_*`・`user_test/family_y_*`・共有SSOT所有)。**本委任は共有SSOT(`OPEN_ITEMS.md`/`CURRENT_SPEC.md`/`DECISION_LOG.md`/`docs/pm/ACTIVE_TASK.md`/`docs/pm/REPORT_LEDGER.md`/`docs/pm/USER_DECISION_REGISTER_01.md`)を編集しない**(追記文案をRESULT_PACKETへ)。所有=`docs/research/FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01/`、`er118_fz_full_episode_trial_01.py`(+test)、`er118_output/fz_full_episode_trial_01/`、`user_test/fz_full_episode_trial_01/`、`docs/pm/delegation_log/2026-10-26_FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01_DELEGATION_02.md`、`docs/pm/RESULT_PACKET_FZFE2.md`。Round 1/2 module `er118_fz_dialogue_context_tts_trial_01.py`は原則無編集(M-6で純関数のみ利用)。生成中は他のProduction runを起動しない(R-1注意。Y委任_03の再組立/候補生成と時間が重なる場合、snapshot差分が出た箇所はY run dir配下かを確認し、Z Production dirに差分がなければ継続可)。gitは`git commit --only <paths>`。

## 性質/到達上限Status/禁止事項
- 性質: Trial(DEV専用)。到達上限: Status候補(事前登録写像)+Fable評価欄空欄+ユーザー試聴待ち。Production採用・Production公開物上書き・既存音声差替え禁止。
- 禁止: Production Prompt/TTS設定/方式/Gate/閾値/reuse keyの変更、Round 1/2の文脈・感情付与方式の変更、事前登録の結果後変更(生成前の改訂はM-7/M-8/R-7反映として可。commit時刻で固定)、NG音声の採用、`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・`git checkout -- <file>`。
- 費用上限: 上限¥100(Guardrail、scope=Phase 1b。見積 期待25円/保守31円/天井75円)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。
- Opus独立技術レビューGate: 条件A実施済み(本委任で反映)。再レビュー不要(設計骨格は妥当との結論)。
- 時間見込み: 全体2.5〜3時間(Opus反映+test 60、dry-run 10、生成4単位 約25(各5分+間隔150秒)、組立・自己検証 15、解析・ページ 25、評価・docs 25、Git 10)。並列化: 生成4単位は直列(cost log・Cap判定の整合)。解析scriptとページ雛形は生成待ちの間に準備。
- 費用/日次: 当日既使用JPY約81(出典: RESULT_PACKET_FZFE1。Y委任_03が並行で6〜10円消費見込み。起動前に`py docs/pm/tools/daily_dev_cost_01.py`で実測)/残約900/本委任見積JPY25〜31(天井75)/改善見込み中/承認区分: C(ユーザー承認済みTrial、300円以下)。
- 前委任QDC・受入(Gate 7): 委任_01=棚卸53 clip・見積・設計・事前登録・Opus依頼・感情情報53件(1.01円、test 67 PASS、commit 32a773453)→Fable受入ACCEPTED(Phase 0)。当初目的(原文逐語)=「作品ごとに、新規生成したセリフ音声を既存の地の文音声と組み合わせ、**最初から最後まで通して聴けるTrial版**を作成する。」判定整合: 重大NG=なし/主因=なし/是正対象=なし/STOP理由=なし/提示=Phase 1bへ。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。
T-2追記(2026-09-25、`NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02`、PM_GOVERNANCE.md 7-5、予算逸脱再発防止): TTSを伴う委任は実行前に(1)差分[変更箇所のみ]再生成が対象コード上で実際に可能か確認、(2)既存の音声再利用キャッシュの有無を確認、(3)`--budget`/`--budget-jpy`等が存在すればタスク固有の承認上限に合わせて明示、(4)想定外の全再生成と判明した場合はAPI実行前にSTOPし報告、の4点を必須とする。
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`、ユーザー正式決定、費用上限[Cap]を伴う全委任で常時有効): 費用上限[Cap]は「暴走防止のためのGuardrail」であり、Cap到達=自動STOPではない。禁止事項/性質欄の費用上限記載は次の定型文に従う。「上限¥X(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。」旧来の「上限¥X、超えそうなら実行前STOP」のみの記載(継続条件・STOP条件の書き分けが無いもの)は使用しない。既存7-5(4)「想定外の全再生成が判明したらAPI実行前にSTOP」は本T-3の「暴走疑い時のSTOP」に該当する条件として維持する(置き換えではない)。ユーザー承認済みの総予算・個別run上限・STOP条件を優先し、Fable/Workerが独自に過度に厳しい停止条件を追加しない(2026-10-05)。

## ユーザー指示(原文)
`docs/pm/delegation_log/2026-10-26_FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01_USER.md`(逐語保存済み)。§2「セリフ音声をすべて文脈・感情付き方式で新規生成」「文脈情報を実際の発話本文に混入させない」「前回Trialの文脈・感情付与方式を基本とし、比較条件を勝手に変更しない」、§3「Production公開物をTrial版で上書きしないこと」、§4 C「既存の承認済み品質基準を変更しないこと」、§5の7項目、§6「予算内で最も効率的に実施」、§7の1〜8。

## Fable感情レビュー結果(53件、EMOTION_CANDIDATES_01.md全件読了)
- **全53件 accept**(猿の手 Std 15/Adv 17、メロス Std 10/Adv 11)。DISCARDはなし。NO_EXPLICIT_CUE 19件は規則どおり状態行なし。
- 観察(記録のみ、変更不要): 猿の手 Std part3_c1「visibly unsteady」(地の文は「his voice was shaking」=聴覚的手がかりで「visibly」は軽い推測)、猿の手 Adv part1_c15「quietly hopeful」(地の文「with a smile」からの軽い推測)。いずれも地の文の逐語引用がCONTEXTに併記され、強度語denyも通過しているため許容。Round 2と同じclipの処理と整合。
- `summary_ja`はEMOTION_CANDIDATES_01の「場面(日本語)」に沿う事実ベースの短文であればSonnet下書きのままで可(原文にない感情語を足さない)。

## Fable判断(Opusレビューへの採否。詳細はOPUS_REVIEW_01.mdへ転記する本文を参照)
- M-1〜M-8: **全て採用**(実装前に反映)。
- M-8のNG clip方針(Fable決定、生成前に事前登録へ固定): NG音声は採用しない。通し版の該当箇所はProduction原音を置き、ページ・チャプターに「この箇所は現行音声(Trial生成NG)」と明示。NG≦2 clip(53中)ならC1は記録付き成立としてユーザー試聴へ、3 clip以上ならREJECTED候補(方式不安定)としてFableへ報告(ページは作る)。
- M-7: C2のblocking条件はProduction ASRカスケードの最終判定PASS系+repetition QA済み。`token_equal`/`similarity`は観測値として全件報告。C3 flagged時はFable聴取確認の手順を事前登録(生成後flaggedが出たらRESULT_PACKETに列挙し、採用保留のまま報告)。
- R-1〜R-9: 採用。R-3(TEXT同一性)で差分が見つかった場合: 差分が発音供給(PNAP)ヒントのみで語の綴りが同一なら「現行scopeで計算したTTS入力」を使い交絡として明記して継続、語自体が違うならSTOPして報告。R-9: scope=Phase 1b・Guardrail 100円のGOを別に設ける。Std会話へのctx付与が初回である旨を明記。
- M-5の3点assert不一致はSTOP(Production汚染ではなく比較条件崩れとして報告)。

## Opusレビュー本文(`docs/research/FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01/OPUS_REVIEW_01.md`へ**逐語で**転記すること。先頭に「転記: Fable→sonnet-worker 委任_02、2026-10-26。Opus(opus-consultant)の出力を無改変で保存」の1行を付ける)
```
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
```

## KPI provenance欄
TTS/ASR/leakage/指標=fresh(本委任生成分)。Production版=reuse(既存Production音声・組立wav)。E2E自己確認: No(Trial)。

## Opus台帳更新
`docs/pm/OPUS_FINDINGS_LEDGER.md`は共有SSOTではないが他agentとの競合回避のため本委任では編集せず、M-1〜M-8/R-1〜R-9の状態遷移(RAISED→FABLE_DECIDED→IMPLEMENTED)の追記文案をRESULT_PACKETへ。

## 事前指定Read一覧
- `docs/research/FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01/{DESIGN_01,PREREGISTERED_CRITERIA_01,BUDGET_PLAN_01,INVENTORY_01}.md`(全文、短い)、`docs/pm/RESULT_PACKET_FZFE1.md`(全文)
- `er118_fz_full_episode_trial_01.py`(全文、自作module)、`er118_fz_dialogue_context_tts_trial_01.py`: Opus指摘の行(`:73,137-138,253-254,305,428,564-568,660-686,742-743,825,841,846,850-935`)
- Opus指摘の根拠行(必要箇所のみ): `er012_b_family_voices_production_01.py:548`、`er003_v1_n3_01_tts_generate.py:211-228`、`er063_family_z_audio_01.py:871-882,1091-1158,1642-1669,1861,1894-1910,1918,1991,2107`、`er003_v1_n3_01_assemble.py:213-217,480-488,1001-1011`、`er011_human_review_lock_01.py:112,155-176,194-195`、`er113_fx_paragraph_chunk_trial_01.py:49-54,660-711`、`er109_xz_scope_01.py`(family_scope)、`er078_secondary_run_scope.py`(with_secondary_run)
- 各`er118_output/fz_full_episode_trial_01/<work>/<level>/llm/emotion_review.json`

## 事前指定Grep一覧+追記位置・更新位置の手順
1. OPUS_REVIEW_01.md転記(逐語)→`DESIGN_02.md`(新規: M/R反映の差分、Fable判断[M-8方針・R-3分岐・R-9 GO分離]を明記)→`PREREGISTERED_CRITERIA_02.md`(新規: M-7のC2、M-8のNG閾値NG≦2、M-5のC5(ii)置換、R-7(a)の`noise_band_r2.json`sha、C3 flagged時手順。**生成前にcommit**し時刻固定)。
2. 実装: M-1(clip別gen dir→OK+C2〜C4成立のみcopy、組立前sha assert)、M-2(`_original`削除+test)、M-3(`build_entry`+trial fields、非dialogue pathの書換、human_approvalのcopy、全pathがOUT_ROOT配下test)、M-4(realpath assert、copyfileのみ+inode/sha別ファイル確認、build_pages不使用、mtime走査の除外先修正)、M-5(組立後3点assert+story_clips[0]非dialogue test)、M-6(純関数許可list、他は本moduleへ再実装、monkeypatch test)、M-7、M-8、R-2(scope内呼出+無料dry-run)、R-4(公開mp3長一致確認、Production版mp3も同一`sf.write`経路)、R-6(raw_usage_log正、c_asr実測、k幅表示、レビュー自動化費用=未計上)、R-7、R-8(並列禁止flag、voice map test)、R-9(GO scope分離)。test全件PASS(Round 1/2 54件維持)、遮断harness下で接続試行0。
3. 感情レビュー転記: 全53件`fable_decision=accept`、`summary_ja`確認。
4. 起動前: `py docs/pm/tools/daily_dev_cost_01.py`、`py tools/stop_scope_check_01.py --managed-id FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01 --run-dir er118_output/fz_full_episode_trial_01 --out er118_output/fz_full_episode_trial_01/stop_check_委任_02.json`(rc=3なら停止)、R-1 snapshot、R-2 dry-run(API 0)で書込先3経路がOUT_ROOT配下であることを実測(そうでなければ生成せずSTOP)、R-3 TEXT同一性(差分はFable分岐どおり)、自己検証(Production原clipで再組立→wav/timeline/gain_report/headroom一致。不一致なら生成せずSTOP)。`PHASE1_GO.json`をscope=Phase 1b・cap_jpy=100・approved_by="Fable(委任_02、ユーザー2026-10-26全編Trial承認)"で作成。
5. 生成: 4単位(monkeys_paw a2→b1b→melos a2→b1b)を各1起動・直列、起動間隔150秒以上(Get-Date記録)、同一コマンド5分3回禁止、外部停止・原因不明rc≠0が2回続いたらSTOP。`TTS_EXECUTION_MODE=STANDARD`明示。各単位後に実費(raw_usage_log)を`BUDGET_LOG_01.md`へ。
6. 組立(API 0): 単位ごとにtrial_run_dir構築(M-1〜M-4)→`run_assembly`→M-5 assert→C6 Gate→R-4 mp3化→生成後snapshot差分0(Y委任_03由来の差分はY dir配下かを確認し区別)。
7. 解析・ページ(API 0): C1〜C7判定(作品×レベル別)、N1〜N6観測、R-7(b)(c)、§5の7項目(実Trial支出 vs 量産想定増分Δ/set、k_ctx実測、初回成功率、NG件数、再生成回数、時間)。試聴ページ`user_test/fz_full_episode_trial_01/index.html`(+作品別ページ可): Trial版通し/Production版通し(同一経路mp3)、セリフ個別A/B、本文+前後文脈+`summary_ja`、Std/Adv区別、NG箇所の「現行音声」明示、noindex・PAGE_NOTICE、Round 1/2ページへのリンク。`py -I tools\user_test_page_standard_check_01.py`は記事用のためrc≠0でも可(結果と理由を記録)。公開URL=`https://shimomura055.github.io/eigo-radio/user_test/fz_full_episode_trial_01/index.html`。
8. `EVAL_01.md`・`TRIAL_RESULT_01.md`(§7の1〜8に対応、Status候補=事前登録02写像、Fable評価欄空欄、ユーザー試聴の論点、機械評価と試聴評価の区別)。
9. 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-26_FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01_DELEGATION_02.md`(Nは627前後、`--index -1`不可、「FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01 委任_02」を含むもの)。

## 実行コマンド全文
- `py docs/pm/tools/daily_dev_cost_01.py`
- `py tools/stop_scope_check_01.py --managed-id FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01 --run-dir er118_output/fz_full_episode_trial_01 --out er118_output/fz_full_episode_trial_01/stop_check_委任_02.json`
- `$env:PYTHONPATH="netblock_harness_01"; .venv\Scripts\python.exe -m pytest er118_fz_full_episode_trial_01_test_01.py er118_fz_dialogue_context_tts_trial_01_test_01.py -q`
- dry-run: `$env:PYTHONUTF8=1; .venv\Scripts\python.exe er118_fz_full_episode_trial_01.py dryrun-sinks --work monkeys_paw --level b1b`(サブコマンド名は実装に合わせ、全コマンドを引数実値でRESULT_PACKETに記録)
- 自己検証: `$env:PYTHONUTF8=1; .venv\Scripts\python.exe er118_fz_full_episode_trial_01.py selfcheck --work monkeys_paw --level a2`(4単位)
- 生成: `$env:PYTHONUTF8=1; $env:TTS_EXECUTION_MODE="STANDARD"; .venv\Scripts\python.exe er118_fz_full_episode_trial_01.py gen --work monkeys_paw --level a2`(以下 b1b、melos a2、melos b1b)
- 組立・ページ: `$env:PYTHONUTF8=1; .venv\Scripts\python.exe er118_fz_full_episode_trial_01.py assemble --work <w> --level <lv>` / `... analyze --work <w> --level <lv>` / `... page-all`
- `python docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-10-26_FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01_DELEGATION_02.md --json-out docs/pm/delegation_log/2026-10-26_FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01_DELEGATION_02.md_check.json`
- secret grep: `git grep -n -I -E "(sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}|BEGIN (RSA|OPENSSH) PRIVATE KEY)" -- docs/research/FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01 er118_fz_full_episode_trial_01.py er118_fz_full_episode_trial_01_test_01.py user_test/fz_full_episode_trial_01`

## SSOT追記文(編集せず文案のみ)
- OPEN_ITEMS新規行案(FZFE1文案を更新): Status=<PHASE1B_DONE_USER_LISTENING_PENDING | REJECTED候補>、実費、C1〜C7結果、NG件数、Δ/set、試聴URL、Opus M-1〜M-8反映済み。
- OPEN-516行末追記案(FZFE1文案どおり)。
- DECISION_LOG案: 「2026-10-26 FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01 委任_01/02: ユーザー承認の全編通しTrial(猿の手・走れメロス、Std/Adv、セリフ53 clip ctx新規生成、地の文再利用、DEV隔離組立、Opus条件A反映)。実費<x>円。Production変更0。Status候補=<…>、最終はユーザー通し試聴。」

## Git(明示add対象・コミットメッセージ・trailer)
- 事前登録固定commit(生成前): `docs/research/FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01/{OPUS_REVIEW_01,DESIGN_02,PREREGISTERED_CRITERIA_02}.md`、`er118_fz_full_episode_trial_01.py`(+test)、`er118_output/fz_full_episode_trial_01/noise_band_r2.json`(小さければ)。
- 完了commit: `docs/research/FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01/{EVAL_01,TRIAL_RESULT_01,BUDGET_LOG_01}.md`、`user_test/fz_full_episode_trial_01/`(html・mp3のみ)、`docs/pm/delegation_log/2026-10-26_FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01_DELEGATION_02.md`(+_check.json)。wav/raw_usage_log/PHASE1_GO/STOP/snapshot/RESULT_PACKET不追跡。
- メッセージ案: 「FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01 委任_02: Opus条件A M-1〜M-8反映、事前登録02固定(生成前)」/「… 委任_02: 猿の手・メロス Std/Adv セリフ53 clipをctx方式で生成しDEV隔離で全編組立・試聴ページ公開(実費x円/100円、Production変更0)」
- `git commit --only <paths>`→`git push origin HEAD:main`(non-fast-forwardなら fetch→`git merge --no-edit origin/main`→push、競合は両方残しSTOP)。SSOT編集権: なし。

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_FZFE2.md`。「現在の状態/何をやったか/何が分かったか/何が残ったか/判断候補/補足」+RESULT_PACKET 4行+判定整合行。必ず含める: M/R反映の対応表、dry-run書込先実測、R-3結果、自己検証結果、起動時刻・各単位実費(raw_usage_log正)・累計/100・日次、C1〜C7(作品×レベル)、NG件数と扱い、N1〜N6、§5の7項目(Δ/set幅・k_ctx・初回成功率・時間)、70円/set維持可否の評価、公開URL、Status候補、ユーザー試聴の論点、SSOT/Opus台帳文案、commit/push・raw URL、check結果。