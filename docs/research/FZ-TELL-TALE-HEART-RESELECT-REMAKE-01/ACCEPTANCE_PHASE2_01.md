# ACCEPTANCE_PHASE2_01(FZ-TELL-TALE-HEART-RESELECT-REMAKE-01 委任_03、2026-10-28、受入検証・API 0)

結論: **Production完成(技術Gate全PASS)。ユーザー最終試聴は未実施(PASS未取得)**。本委任での有料API呼出は0(runner Phase 2の実費19.9447円のみ)。Local Rewrite採用0、本文・確定選定・文法0件は無変更。

対象run: `er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_reselect_01`(以下R)。完成ページ: `user_test/family_z_tell_tale_heart_reselect_01/{index,standard,advanced}.html`。

## 0. 優先確認2点(Fable追記)
### 優先1: Adv KP2 `kp2_en`の`[TECHNICAL_STOP] Secondary ASR障害`
- 結論: **最終`kp2_en.wav`は検証済みで採用。未検証組込みではない。再実行不要(有料API再起動0)**。
- 根拠: (a) attempt1/2(`b1b/narration/attempts/kp2_en_attempt{1,2}_custom60ebc452.json`、06:44:08/06:44:11)はPrimary(openai_asr)=`mock` EXACT_MATCHだがSecondary(Azure)が`NG_SECONDARY_UNAVAILABLE`で`verified:false`。(b) その後、同ループは約3分後(06:47:16)にattempt3(`..._attempt3_custom31eb2f72.json`、route=custom_31eb2f72)を生成し、Primary `mock` EXACT_MATCH+Secondary Azure `Mock.` NORMALIZED_MATCH(`unified_judge_state:PASS`)で`verified:true`。(c) `b1b/audit/tts_generation_results.json` key_phrases[2].english: `status:OK`、`sha256=e8c29484…`(=現行`kp2_en.wav`のsha256と一致)、`asr_judgement.state=PASS, reason_code=dual_agreed`、`kp_dual_check.ok=true`(Primary/Secondary/Whisperとも保護差分なし)、`z_adoption=adopted`。(d) kp2_en後もstageは継続(narration 06:47〜06:49のfull_story clip生成、tts_a2、gate…page_verify全実行、runner rc=0)。`[TECHNICAL_STOP]`行はer078_secondary_run_scope_01.py:56のstage末尾の事象サマリ出力(`events=2`=attempt1/2のSECONDARY_UNAVAILABLE2件、`circuit_open=False`=circuit未発動)であり、停止状態のまま組込まれたことを示さない。`restartable:True`(er078_secondary_run_scope_01.py:36)は「そのclipが技術STOP entryになった場合に再実行で再開できる」の意味で、本件は当該entryが最終resultsに残っていない(全b1b 28 entry status=OK、technical_stop=0、a2 29 entry OK)。
- Secondary不通の恒常化はなし(attempt3でAzure応答、cost_logでazure 8件success)。仕様上の迂回(Primary単独PASS)は行っていない。

### 優先2: `b1b/narration/full_story_part1_c3_original.wav`
- 結論: **Local Rewriteではない。Z速度仕様v2の減速/増速後処理で保全された原音**。
- 根拠: attempt `full_story_part1_c3_attempt1_englishstyleprefixwidemargin.json`(route=english_style_prefix_wide_margin、`verified:true`、max_attempts 3、`tts_mode:ctx`、`dialogue_tts_policy:fz_ctx_v1`、sha256=`ee6422b8…`)。results: `speed_profile={version:z_speed_v2, profile:adv_dialogue_fast6, applied:true, tempo:1.06, original_sha256:ee6422b8…(attempt sha256と一致), source:generated}`、`slowdown_ratio:0.9484`、`slowdown_applied:true`、`local_rewrite_recovery:null`/`local_rewrite_diff:null`、`audio_text_deviation:null`。gate_result_04C.json `z_speed_profile.clips.full_story_part1_c3`: `adv_dialogue_fast6, original_seconds 1.531, ratio 0.9488, range [0.93,0.96], ok`。ファイルサイズ73,530B→69,798B(比0.949)も整合。他clipに`_original`が無いのはAdv narratorが`adv_narrator_none`(後処理なし)のため。Std側`full_story_part1_c3`は`std_dialogue_none`。
- 他の仕様: Adv dialogue「Who's there?」のみ増速(tempo1.06)=承認済みv2仕様どおり。

### 注意事項: attempt JSONの「UTF-8で読めない」
- 結果: **破損なし**。`R/*/narration/attempts/*.json` 48ファイルすべてUTF-8でjson.load成功(a2+b1b)。`kp2_en_attempt2_custom60ebc452.json`はASCIIのみ(非ASCII 0行、先頭`7b 0d 0a`)。0xa4はFableの読取時の既定エンコーディング(cp932)または別ファイル(em-dash等を含むresults系JSON)の読取りに起因すると推定(`PYTHONUTF8`/`-X utf8`でread可)。影響なし。ただしWindowsでの本件JSON読取は`encoding='utf-8'`を明示すること。

## 1. runner結果(USER_03 §5-2前提)
- `console_phase2.txt`末尾 `rc=0`、`spent_jpy: 19.9447`(Phase 2のみ。runner起動 `--approved-budget-jpy 60`)。stage順 kp→tts_b1b→tts_a2→provision_shell→gate→assemble→pages→page_verify 全実行(`e2e_stage_log.jsonl`、provision_shell 0.2s/gate 0.7s/assemble 1.7s/pages 10.2s/page_verify 102.7s)。
- 費用: Phase 2=19.9447円、本案件累計=4.08(委任_01)+0.79(委任_02 probe)+19.94=**約24.81円/Cap150円**(残約125.2円)。cost_log(Phase 2、111行): gemini-3.8-flash-lite-tts 39件(Std+Adv TTS)、gemini-2.5-pro-preview-tts 2件(dialogue 2 clip)、gpt-4o-mini-transcribe(Primary ASR)49件、azure-speech-stt(Secondary)8件、gpt-6-luna 13件(解説生成・NER)、全success。
- STOP sentinel: `er026_output/family_z_production_e2e_01/STOP_ALL`・`R/STOP`とも不在。RESTART_STORM: なし(本stageは1起動。`py`での1回目はAPI前rc=2で費用0)。失敗stage: なし。`[TECHNICAL_STOP]`は一過性(優先1)。
- `stage_kp`はKP確定済み(`confirmed_selection.json`)を読み、`kp_review_status=REVIEWED`+署名(Std `3a0fb396…`、Adv `65f30a34…`)を`writer/provenance.json`へ記録(本文sha不変)。

## 2. 確定内容一致検証(§5-2)
- 方法: `R/key_phrases/{a2,b1b}/confirmed_selection.json`(live rev1、`confirmed_by.actor=user/form_submit`)の全itemと完成`index.html`を突合(Python照合、API 0)。
- Std(a2、本文sha `66da3226…`、候補集合sha `196a84f8…`):
  - ①: make one's blood turn cold=人をぞっとさせる(lk1「made my blood turn cold」)/raise one's voice=声を大きくする(lk1「raised my voice」)/groan=うめく(lk1「groaned」)
  - ②: rush at someone=人に向かって突進する(lk2「rushed at him」)/go on talking=話し続ける(lk2「went on talking」)
  - ③: pulse=脈(lk3「pulse」、`ul.lk-meaning`「pulse ＝ 脈」)
  - 英語・日本語訳・区分とも逐語一致。decorated_elements=6/candidates=6(g3 PASS)。
- Adv(b1b、本文sha `0c71c2f0…`、候補集合sha `41261214…`):
  - ①: sharpen someone's senses=人の感覚を研ぎ澄ます(lk1「sharpened my senses」)/mock=ばかにする(lk1「mocking」)/hideous=ひどく気味の悪い(lk1「hideous」)
  - ②: blood went cold=恐怖で血の気が引く(lk2)/never stir=少しも身じろぎしない(lk2「never stirred」)
  - ③: Not a mark=跡ひとつない/motionless=じっと動かない/fastening=留め具/shriek=甲高い叫び声(lk3、`lk-meaning`4件)
  - 逐語一致。decorated_elements=9/candidates=9(g3 PASS)。
- 文法: 両level `confirmed_grammar.json` count=0(`eigo_radio_confirmed_grammar_v2`、sidecar sha Std `74577a69…`/Adv `10fc03a8…`)。ページの`Grammar & Sentence Structure`は両levelとも解説0件で、既存仕様のZERO文言「今回の本文には、このPartで特に取り上げる難所となる構文はありませんでした。」のみ表示(index.html、Std/Adv各1箇所)。文法解説の生成・音声なし。
- 差替え・追加: なし(ページの学習項目は5件+③のみ、`data-hl`付きハイライトはStd 6/Adv 9=確定itemと同数)。
- er128 G0〜G4(`page_verify_local.json`): `kp_selection_verified` a2/b1b `ok:true,legacy:false`(署名一致)、`learning_items_verified` a2/b1b `g3.status=PASS,problems=[]`、`part2_verified` a2/b1b OK(`part2_blocks:1`=ZERO文言1ブロック)。`key_phrase_source_gate.json` a2/b1b `status:PASS total 3 present 3 missing []`。個別のG0/G1/G2/G4結果ファイルは本runにはなく、runnerのfail-closed通過(rc=0、INTEGRITY停止なし)で代替確認。

## 3. 解説・ハイライト(§5-3)
- ①②: 両levelで同形式(「本文中の意味/本文の英文/日本語訳/解説」)の詳細日本語解説(解説は近接表現との違い・用法を含む4〜6文)を5件ずつ表示。例(Std ①): 「『人の血を凍らせる』というイメージから…近い表現の scare someone よりも、恐怖が強く…」。
- ①のみKP音声: tts_resultsのkey_phrasesは3件(kp1〜3、Std=en+ja、Adv=en+explanation_en)。②・③の音声なし。page_verify `(e)_kp_rows:3`。
- ③: 短い訳のみ(`ul.lk-meaning`、例「pulse ＝ 脈」「Not a mark ＝ 跡ひとつない」)。
- ハイライトCSS実物(index.html `<style>`): `.lk1,.lk2,.lk3{font-size:inherit;color:inherit;background:none}` / `.lk1{font-weight:700;text-decoration-line:underline;text-decoration-style:double;…}`(太字+二重下線) / `.lk2{font-weight:700;text-decoration-line:underline;text-decoration-style:solid;…}`(太字+下線) / `.lk3{font-weight:inherit;text-decoration-line:underline;text-decoration-style:solid;…}`(下線のみ)。DOM例: `<strong class="lk1" data-hl="p_c4e00460ea">made my blood turn cold</strong>`、`<strong class="lk2" data-hl="p_c4ac049763">rushed at him</strong>`、`<span class="lk3" data-hl="p_8439fc486b">pulse</span>`。色=inherit、サイズ=inherit、背景=none(マーカーなし)=SLOT-23仕様。凡例(`lk-legend`)あり。

## 4. 音声検査(§5-4)
- Voice(`voice_assignment.json` APPROVED_FOR_PRODUCTION 2026-10-23): Narrator=Aoede、old_man=Algieba、officer=Schedar(本文に発話なし、未使用)。実績: Std/Adv full_story narrator=Aoede、dialogue「Who's there?」=Algieba(両level)。Std topic_intro/preview/comment=Aoede、Adv=Charon(固定仕様どおり)。
- Style: model=gemini-3.8-flash-lite-tts(narrator/KP)、dialogueはgemini-2.5-pro-preview-tts(Z dialogue)。Z narrator style PD06、dialogue `fz_ctx_v1`(文脈・感情付き、`dialogue_tts_policy:fz_ctx_v1,tts_mode:ctx`、1回目で採用)、KP K2、style_version `z_v2_pd8_r2_e1_e2up_k2_m2_kpx_20261012`。Style actual gate(`style_actual_vs_approved.json`): a2 PASS strict checked 20/20、b1b PASS strict 19/19、blocked/warnings 0、missing_required_roles []。
- 速度仕様v2(`gate_result_04C.json z_speed_profile`): Std narrator `std_narrator_slow6`(ratio 1.0534〜1.0597)、Std dialogue `std_dialogue_none`、Adv narrator `adv_narrator_none`、Adv dialogue `adv_dialogue_fast6`(0.9484、範囲[0.93,0.96])。全clip ok。
- Chunk(`chunk_plan_*.json`、planner `chunk_tts_v1_x_paragraph_z_r1_20261025`): Std part2_c1=[60,69]語、part3_c1=[68,71]語。Adv part2_c1=[58,62]、part3_c1=[65,61]。計画どおり(AUDIO_PHASE1_01と一致)、親clipは結合してassemble。
- ASR(Primary gpt-4o-mini-transcribe/Secondary Azure): a2/b1b とも全clip `PASS`、`PASS_WITH_WARNING`0・NG0・warning_labels空(`pass_with_warning_listening_list.json` count 0)。KP英語6件は`dual_agreed`(Primary+Secondary一致+Whisper)、他はprimary_pass。kp_vote_audit: checked 3/with_vote_evidence 3/blocking false。固有名詞発音アラーム0、HR残0、review_lock topic_intro RESOLVED。
- 統一TTS retry/Fallback: Std attempts全clip 1回。Adv attempts 1回のみ、**例外=kp2_en(3 attempt: Secondary不通×2→180秒待機後の第3attempt採用、上記優先1)**。`cooldown_occurred`はdialogue 0(kp2_enのcooldownは統一retry内、HR Lock投入なし、`tts_generations_used`上限内)。Fallback(従来方式)使用0、`audio_text_deviation_clips=[]`。固定asset系7 clip(welcome/preview_intro/key_phrases_intro/full_story_intro/kp1〜3_number、Charon)はattempts 0(固定Master再利用)。

## 5. 本文=音声(§5-5)
- Local Rewrite採用: **なし**(全clip確認)。`local_rewrite_recovery`(null)8箇所、`local_rewrite_diff`(null)39箇所、`RESOLVED_BY_LOCAL_REWRITE`/`LR_REWRITTEN`の出現0(a2/b1b audit・narration全体Grep)、`local_rewrite_recovery`ファイル0。attempt JSON 48件にも該当なし。よってUD-1に基づく当該部STOPは発動せず。
- 公開本文とTTS入力: `gate_result_04C.json` `article_text_source:"canonical(原稿のまま)"`、`audio_text_deviation_clips:[]`、`audio_text_deviations:[]`(両level)。writer正本: `R/writer/std.md` sha256=`b94c730552ef103e…`、`r2.md`=`e11b84dd2be5a60a…`、いずれも固定正本`run_sf_prod_02/writer/{std,r2}.md`と`cmp`一致(本文無変更)。`writer/provenance.json`の差分はKP stage記録(`kp_review_status`/署名)のみ(本文sha不変)。

## 6. page_verify・公開(§5-6)
- `R/page_verify_local.json`: 全page http 200、`user_page_standard_check.overall=PASS`、(a)〜(n)(全編音声/preview/comment3/story6/kp3行/seek buttons/voice labels/TTSモード明記/音声と台本同行/no file:///no A2・B1ラベル)PASS、plays_failed []、console_errors []。`seek_ok_all:false`は旧`run_chunk_01`の同ファイルでも同値(headless環境のseek判定)で本案件固有でない既知挙動。音声: Std 25/Adv 24 audio、index 33。
- 試聴URL(push後に200確認、下記): `https://shimomura055.github.io/eigo-radio/user_test/family_z_tell_tale_heart_reselect_01/index.html`(Std/Advとも掲載)・`standard.html`・`advanced.html`。
- 既存公開dir `user_test/family_z_tell_tale_heart_01`・`family_z_tell_tale_heart_chunk_01`: `git status`で変更なし(未変更)。

## 7. 残る判断事項
- ユーザー最終試聴・正式承認(PASS未取得、先取りしない)。
- 本委任で新たな判断候補なし(D-1=文法0件はUSER_03で確定済み。UD-1はLRなしにつき不発動)。
- 軽微(修正へ進む/実害なし分類): OPEN-568は既存。新規OPENなし。
