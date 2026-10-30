# SELECTION-UI-BATCH-AND-VOCAB-AUDIO-01 委任_02C 証跡(Vocabulary & Expressions 掲載項目の英語音声=生成側、2026-10-30)

範囲=生成側(er137 + X/Y/Z runner配線 + 既存Gate)。End Userページ側(er135 build / rev01-g再生UI)は別委任で本委任では未編集。基点=origin/main 72e4152f7。

## 1. 方式(DESIGN_01 4節 + Opus M6/M7)
- M7: 全掲載項目を**単体mp3**にする。KPと重複する項目は既存`kp<rank>_en.wav`(KP stageで生成・ASR検証・Gate済み・sha不変)を**mp3変換して再利用=TTS 0**。KPでない②追加解説だけ新規に英語音声を作る。
- ②の音声: 役割`vocab_extra_english`を`_generate_or_reuse_kp`に追加(`_KP_ENGLISH_ROLES`、X runner :1318)。KP英語と**同一の生成関数**(`_kp_english_generate_fn`: KP3V 3-ASR多数決・Master Audio Store key・K2 style・既存retry/fallback)・Whisper事前確認・値ガード・KP3V再利用ゲートを通る。新stageなし(KP音声段の直後の1呼出)。
- M6: 掲載項目は全件音声必須=fail-closed。結果は`tts_generation_results.json`のtop-level`vocab_extra`(`{"v<n>": {"vocab_extra_english": entry}}`)に保存し、既存`asm.verify_episode_audio_validation_gate`が`kpv<n>_vocab_extra_english`としてKP音声と同じ規則(VALIDATED/HUMAN_APPROVED以外・disfluency QA欠落・sha不一致=EPISODE_BLOCKED)で検査する(er003_v1_n3_01_assemble.py:507-519)。キーが無い結果(A/B/C・旧run・②無し)は従来と同一。
- 新flag無し・Prompt/閾値/Style/retry上限は不変(承認済み仕様の配線=DefaultOff対象外)。

## 2. 配線(file:line、origin/main基点の作業木)
| 経路 | 生成 | 保存 | Gate/export |
|---|---|---|---|
| X (er019 runner) | `_generate_vocab_extra_segments` :2369、b1b呼出 :1826、a2呼出 :2261 | results `**({"vocab_extra":…})` :1843 / :2276 | Assembly入口`load_family_x_b1/a2_sources`で既存Gate後に`_vx_gate_hook` :2440 / :2808 |
| Y (er121_family_y_audio) | `xr._generate_vocab_extra_segments`(X共通関数) :636(b1b) / :752(a2) | `_finish_results(..., vocab_extra=)` :756-769 | `load_y_sources`で既存Gate後に`xr._vx_gate_hook` :1067 |
| Z (er063 + er026 runner) | er026 `load_level_inputs`が②を`vocab_specs`(kind=kp_en・role KP_EN)にして :2584-2588、`run_tts_stage(vocab_specs=)` :2624 → er063 `_run_vocab_extra_specs` :1767(`generate_or_reuse_z`=KP英語と同一契約) | results `vocab_extra` :1742、checkpoint/merge :1475-1613 | `run_audio_gate(vocab_specs=)` M2存在assert(er063 :2095)+共有Gate、`stage_gate`で`gate_hook` er026 :2656 |
- 共通core=er137_vocab_extra_audio_01.py(`find_kp_dir`/`split_vocab`/`generate_extras`/`assert_results_complete`/`export_level`/`gate_hook`/`apply_to_article`/`validate_article`)。置き場の違い(X=`<level>/key_phrases`、Y/Z=`<run>/key_phrases/<level>`)で②が黙って0件になる事故を`find_kp_dir`で防止(実走で発見・是正、testあり)。
- resume=API 0: 前回resultsのOK entryを`_generate_or_reuse_kp`/`generate_or_reuse_z`の再利用ガード経由で再利用(test: 生成関数が呼ばれたらfail)。

## 3. article.json 出力形(UI委任=rev01-g が読む schema。`enduser_article_v1`への**加法**フィールド)
`levels[std|adv].vocab[i].audio`(全掲載vocab項目に必須、1件でも欠ければ`apply_to_article`が`VocabAudioIncomplete`で停止):

    {"kind": "standalone", "file": "audio/vocab_<a2|b1b>_<n>.mp3", "dur": <秒,>0>, "sha256": "<mp3 sha256 hex64>"}

- `file`は`enduser/`直下からの相対(既存`audio/`)。mp3実体は`<run>/<level>/vocab_audio/vocab_<lv>_<n>.mp3`、索引=同dir`vocab_audio.json`(schema `vocab_audio_v1`: `complete`/`errors`/`items[{vocab_index,candidate_id,term,source(kp_reuse|vocab_extra_generated|vocab_extra_store_reused|vocab_extra_resume_reused),file,dur,sha256,wav_sha256,gate_status,tts_status}]`)。
- 付与と検査の公開API: `er137.apply_to_article(article, {"a2": doc, "b1b": doc})`(heading正規化一致で対応付け)、`er137.validate_article(article, public_dir)`(audio欠落・file不在・sha不一致を列挙)。**er135側の最小組込み(UI委任へ)**: schemaの`_S_VOCAB`に`audio`(上記4キー)を追加、`build_enduser`でrun_dirの`<lv>/vocab_audio/vocab_audio.json`を読み`apply_to_article`→mp3を`enduser/audio/`へコピー→`verify_consistency`で`validate_article`。本委任ではer135を編集していない(他Worker領域のため)。**この組込みが入るまで、公開済み/新規article.jsonへの`audio`は実際には付かない**(生成側は完了)。
- 再生UI(rev01-g): `button.vplay`→`new Audio`/共有Audio要素で`audio.file`を再生(KP/②とも同じ単体mp3なので区間指定不要)。

## 4. test(mock、課金0)
`er137_vocab_extra_audio_01_test_01.py` 22件PASS: 確定5項目(月のしわAdv実record)がKP3+②2に分かれ②だけ生成(KP wav・vocab_confirmed・確定recordのsha不変)/resume API 0/KP3V再利用ゲートと Whisper事前確認が新役割にも掛かる/gloss HR待ち=STOPPED entry・API 0/vocab_confirmed無し=キー無し/Y配置の探索/TTS失敗=Gate EPISODE_BLOCKED(`kpv5_vocab_extra_english=STOPPED`)・export STOP・`apply_to_article` STOP(音声なし掲載を作らない)/Human Review承認で該当segmentのみ通過/results欠落=Assembly前STOP/idempotent・wav改変検知/Z: specがKP英語契約・planに混ぜない・resume API 0・失敗がstage statusとM2 gateに出る/3 runnerの配線grep。
既存回帰: 影響範囲(X/Y/Z runner・er063・Gate)の関連test 約70モジュールを実走し、失敗モジュールは**変更前(origin/main)と同一の失敗集合**(er019_family_x_pointless 1, variable_role_style 4, er026_e2e_integration 12, er063_audio 4, er063_style_actual_gate 25, er121_text_core系ほか=全て事前不具合、件数一致を差分で確認)。Gate関連(er008_audio_validation_gate_05等)はPASS。

## 5. 実TTS runtime evidence(コピーrun、元run不変)
元run(X月のしわreselect_01・Y再配達run_style_fix_01・Z メロスkcp4_ev_z_01・Z雪女run_yo_prod_01)の**1,373ファイルのsha256が実走前後で完全一致**(差0)。コピーrunで実TTS(Cap ¥50固定・引上げなし)。実走コマンド=`ev02c/`のsub02c_*.py(環境shim経由で本番runner/関数をそのまま呼ぶ)。
| Family | level | 掲載 | KP再利用(TTS0) | ②新規生成 | ②Store hit | ASR(生成時 KP3V) | 実費 |
|---|---|---|---|---|---|---|---|
| X 月のしわ(コピー: moon_shrinking__run_vocab_ev_02c_01) | Std(a2) | 4 | 2 | 1 (shrinkage) | 1 (work out) | PASS | 合計¥0.326 |
| X 月のしわ | Adv(b1b) | 5 | 3 | 2 (over its entire history[ENGLISH_LOCK fallback経由でOK]、puzzling) | 0 | PASS | (同上) |
| Z 雪女(コピー: yuki_onna/run_vocab_ev_02c_01) | Std(a2) | 5 | 3 | 2 (get what you deserve, mist) | 0 | PASS(mist=PASS_VOTE_2OF3/PASS_WITH_WARNING、下記) | 合計¥0.4465 |
| Z 雪女 | Adv(b1b) | 5 | 3 | 2 (take shelter, go no farther) | 0 | PASS | (同上) |
| Y 再配達(コピー: redelivery_fee/run_vocab_ev_02c_02、元=run_style_fix_01) | Adv(b1b) | 5 | 3 | 2 (when it suits someone=生成 / end up receiving=Store hit) | 0 | PASS(PASS_DUAL/judge PASS、ASR 'When it suits someone.' / 'end up receiving.') | 実費¥0.1359(Cap ¥3) |
| Y 再配達 | Std(a2) | - | - | - | - | 対象外: 元run(run_style_fix_01)に`key_phrases/a2/vocab_confirmed.json`が無い(Y StdはPart 1未確定)=②無しは従来どおりキー無し | 0 |
- Master Audio Store: 全②entryに`master_audio_id`/`master_audio_key`登録(ev02c/*/_vocab_extra_results.json)。Store hit 1件(work out)はAPI 0。cost logger: 実segment名`vocab_extra<n>_english`/`vocab_extra_<n>_en`で記録(ev02c/*/usage_log_this_run.jsonl、gemini/openai_asr/azure)。
- 出力: 掲載vocab全件(X Std4+Adv5、Z Std5+Adv5)の単体mp3+`vocab_audio.json complete=true`。公開済みarticle.jsonのコピーへ`apply_to_article`→`validate_article(public_dir)`=違反0(ev02c/*/enduser/article_audio_report.json)。同じ公開済み(audio無し)articleは`validate_article`で全件`AUDIO_MISSING`=現状は音声なし掲載である事実の確認。1件欠落させると`apply_to_article`が停止(fail-closed実演)。
- 独立ASR(公開用mp3そのものを別ASR=ローカルfaster-whisper mediumで転写): 19件中18件一致(ev02c/asr_check_mp3.json)。不一致1件=Z Std `mist`→`missed`(同音語。生成時の本番ASRはopenai'MEST'/azure'Missed.'/whisperでPASS_VOTE_2OF3=既存規則でPASS_WITH_WARNING扱い。`mist`と`missed`は同発音のため音声欠陥とは言えないが、**ユーザー試聴は任意で推奨**)。
- 実費合計(X+Z)¥0.772。本日累計(daily_cost 2026-10-29T15:00:00基準、並行Worker全体)=開始時¥346.0 → 終了時¥392.8(うち本委任¥0.77)。
- 追加量産単価(実測): 1記事セット(Std+Adv)あたり ¥0.33(X、②4件中Store hit1)〜¥0.45(Z、②4件全生成)=**約¥0.3〜0.5/記事セット(目標70円の0.5〜0.65%)**。Store hit率が上がれば更に下がる。保存・配信はmp3 数KB×4〜10でPages無料枠内=増分0。

### 4-Y. Y再配達の実TTS証跡(委任_02C-2、2026-10-30)
- 新コピーrun `er121_output/family_y_production_01/redelivery_fee/run_vocab_ev_02c_02`(元=run_style_fix_01の全414ファイルshaが実走前後で一致)。1起動(Y runner `--stages tts_b1b --regenerate-stage tts_b1b --approved-budget-jpy 3`、`--theme-package`/`--reuse-manifest`/STANDARD指定、本番関数 er121 audio -> `xr._generate_vocab_extra_segments`)。STOP/RESTART_STORMなし。
- 掲載5件=KP再利用3(sit right with someone / take the trouble / on top of)+②追加2(when it suits someone=新規生成、end up receiving=Master Audio Store hit)。Gate(`ya.load_y_sources`=既存Audio Validation Gate+er137 gate hook)=GATE_PASS、`vocab_audio.json complete=true errors=[]`。
- 生成時ASR: 2件とも kp_dual_check vote=PASS_DUAL/judge=PASS(row P+S)。Master Audio Store: master_audio_id 928b5e08...(生成)/30fde2c9...(hit)。cost logger: `vocab_extra4_english` gemini 1 + openai_asr 1 + azure 1(hitの項目は0 call)。`tts_generation_results.json`の`vocab_extra`に v4/v5。
- 公開済みarticle(user_test/family_y_production_redelivery_fee_03)のコピーへ`apply_to_article`->`validate_article(public_dir)`=違反0、原articleは5件`AUDIO_MISSING`(=現状音声なし掲載の確認)、1件欠落でfail-closed STOP。独立ASR(公開mp3、ローカルfaster-whisper medium)=5/5一致。
- 証跡: ev02c/y_redelivery_fee/(b1b_vocab_extra_results.json / b1b_vocab_audio.json / usage_log_this_run.jsonl / asr_check_mp3.json / enduser/)。実費¥0.1359、本日累計(daily_cost 2026-10-29T15:00:00基準・並行Worker全体)¥392.8->¥392.9(開始時と本委任後)。Y追加量産単価=約¥0.14/記事セット(Adv、②2件中Store hit 1)。
- 起動規則違反の記録(前委任02C): Worker自身がYコピーrun(run_vocab_ev_02c_01)を300秒に3回起動(1回目=theme-package引数漏れ、2回目=find_kp_dir是正前、3回目)し、RESTART_STORM STOPを自作した。STOPは解除せず記録として残置(run_vocab_ev_02c_01/STOP、元runへの影響なし)。本委任02C-2では新コピーrunで、引数をparser検証(API 0)してから1起動のみ実施。補足: 本委任でも最初のコピー元を誤り(run_01、audit/style_profile.json無し)Style固定記録のM2 STOP(rc=2、API 0、課金なし)を1回出した(別dir[scratchへ退避済み]、約90秒後に正しいコピー元run_style_fix_01の新dirで1起動)。dirが別のためRESTART_STORM対象外だが、150秒間隔の運用目安は守れていない。

## 6. 失敗経路(最終成果物まで)
TTS失敗(STOPPED)→(既存retry/fallback=KP英語と同一)→Gate: `EPISODE_BLOCKED_BY_AUDIO_VALIDATION: …kpv5_vocab_extra_english=STOPPED`でAssembly中止(Z: stage_ttsが`FamilyZTtsClipFailedStop`、M2存在assertがSTOP)→Human Review承認(`human_approved_segments.json`、本文sha一致)でその項目だけ通過→`export_level`は未承認/欠落でcomplete=false・strictでSTOP→`apply_to_article`でSTOP。すなわち**音声欠落項目を掲載したまま通す経路は無い**(testで固定、最終成果物=Assemblyされない/article.jsonが作られない)。

## 7. 残課題・限界(正直に)
1. Y実TTSは委任_02C-2で実走済み(4-Y節)。前委任の起動規則違反(3起動/300秒)と自作STOPの経緯も4-Y節に記録(STOPは残置)。Y StdはPart 1未確定(vocab_confirmed無し)のため②対象外。
2. er135のarticle.json組込み(3節)は未実施(UI委任)。生成側成果物(mp3+`vocab_audio.json`+`apply_to_article`/`validate_article`)は完成。
3. 公開済み記事のバックフィル(Y再配達・Y姓・X月reselect・Z メロス/雪女等)は未実施(別途。Storehit/resumeで低コスト、上記単価)。進行中のX4記事・Y姓Std等は次回tts stage実行で自動(tts未実行runは`assert_results_complete`がAssembly前にSTOPして案内)。
