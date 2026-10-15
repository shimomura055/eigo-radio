# FAMILY-C-JA-TTS-PRODUCTION-FIX-01 委任_01 調査・是正設計書 (2026-10-16, read-only, API 0, JPY 0)

到達Status: `FIX_PLAN_READY`(実装は委任_02以降)。本書の作成以外にコード・SSOT・既存ファイルの編集、Git操作は一切していない。使用したer番号: `er079`(`er0*_output`の最新は`er077_output`。`er078`はAUWのpy群で`er078_output`ディレクトリ自体は無く、`er079_output`は未使用だったため採用)。

注: 本FamilyはLegacy/Backup Family C。`CURRENT_SPEC.md:1553-1560`(Family体系、2026-09-27)は「Family A/B/C向けに新規実装を行わない」(条件2)としているが、本件は2026-10-16にユーザーが明示承認した「既存Production不具合の是正」(指示B)であり、新機能追加・最新仕様への追従ではない。DECISION_LOGには「Legacy Family Cへの例外的是正」と明記する(第10節の文案)。

## 1. 不具合の確定

### 1-1. en固定の正確な箇所
`er013_family_c_production_runner_01.py`
- L374-392 `tts_call_for_voice(voice, text, out_path, label, budget, voice_tts_names)`: **`language`引数が存在しない**。narrator分岐が `L389: repro01.generate_narration_snippet_verified_strict(text, "en", out_path, expected_substring)`、費用記録 `L390: {"language": "en"}` と固定。
- L484-504 `run_simple_narrator_asset(name, text, language, ...)`: **`language`引数を受け取るのに使わない**(デッドパラメータ)。L500 `tts_call_for_voice("narrator", text, out_path, name.removesuffix(".wav"), budget, {})` へ渡していない。呼出側は L807-808 `"en"`(topic_intro_en)、L815-816 `"ja"`(japanese_title)、L830-831 `"ja"`(preview_ja)。
- L584-649 `run_comments_stage_a2`: L641 `tts_call_for_voice("narrator", text, out_path, f"comment_{n}_ja", budget, {})` -- JA Commentも同じen固定の入口。
- 正しく言語を扱っている箇所(変更不要): L436 `get_or_run_asr`(`asr_lang = "en-US" if language == "en" else "ja-JP"`)、L753-757 Comment後のASR診断(`"ja"`)。つまり**ASR診断側はJA対応済み、TTS生成側のみen固定**。

### 1-2. 06dで失敗した実エラー
- `er058_output/unified_all_roles_production_wiring_01/evidence_06d/cja/c_out/a2/audio/comment_1_ja.wav.debug.json`: `status: STOPPED`、`reason: 3回試行してもASR検証(内容+長さ)に合格しませんでした`、attempt 1/2/3 とも「生成音声長(16.89/15.29/16.37秒)が、テキスト量から見積もった妥当な上限(5.50秒)を超えています」(ASRへ送らず破棄)。
- 同 `.../evidence_06d/cja/runner_execute.json`: `main: RuntimeError: COMMENT_TTS_FAILED(comment_1): {'status': 'STOPPED', ...}`(`er013...:645` の `raise RuntimeError(f"COMMENT_TTS_FAILED(comment_{n}): {r}")`)。
- 機序: language="en"のp9a経路が日本語文を英語基準の長さ見積(`max_len`/秒数上限)で判定するため、日本語音声(約16秒)が「見積超過」で破棄され、ASR前に落ちる。`ja`のValidator(`ja_secondary`)は一度も働かない(`RUNTIME_EVIDENCE_06.md:339`)。

### 1-3. 生成経路図(関数呼出列、現状)
```
main (er013...:1052)
 -> run_full_generation (L652)
     [Story]   tts_call_for_voice(seg.voice, tts_text)  L729 -> narrator:"en"固定(L389) / device:charon_english(L396) / その他:generate_voice_body_wide_margin(L407)
     [Comment] run_comments_stage_a2 (L584) -> tts_call_for_voice("narrator", ja_text)  L641 -> "en"固定  <-- 不具合
     [topic_intro_en] run_simple_narrator_asset(...,"en") L807 -> tts_call_for_voice("narrator") L500 -> "en"(結果的に正しい)
     [japanese_title] run_simple_narrator_asset(...,"ja") L815 -> tts_call_for_voice("narrator") L500 -> "en"固定 <-- 不具合(languageを捨てる)
     [preview_ja]     run_simple_narrator_asset(...,"ja") L830 -> 同上 <-- 不具合
     [welcome/preview_intro/key_phrases_intro/full_story_intro] provision_fixed_wav_asset (L453) -> TTSなし(既存資産コピーのみ)
     [Key Phrase] reuse_from必須でcopytree(L842) -> TTSなし
```

### 1-4. 「同じ問題が及ぶSection」全列挙
| Section | 経路 | 言語 | 現状 | 影響 |
|---|---|---|---|---|
| Comment 1/2/3 (JA, A2) | L641 | ja | en固定 | 新規TTS不能(06d実測) |
| japanese_title (A2) | L815-816 | ja | en固定(languageを捨てる) | 新規TTS不能(Commentの後段のため06dでは未到達) |
| preview_ja (A2) | L830-831 | ja | en固定 | 新規TTS不能 |
| topic_intro_en | L807-808 | en | en(正しい) | 影響なし(回帰対象) |
| Story (narrator/device/その他voice) | L729 | en | en(正しい) | 影響なし(回帰対象) |
| welcome/preview_intro/key_phrases_intro/full_story_intro | L833-840 | - | TTS無し | 対象外 |
| Key Phrase | L841-865 | - | TTS無し(reuse_from必須) | 対象外(reuse_fromのstale問題は第4節の汎用ガードの射程) |
| B1 Comment/Preview | L796-803 | - | `B1_COMMENT_CONTENT_NOT_PROVIDED`/`NotImplementedError`で停止(runner未対応) | 対象外 |

JA Voiceはrunner側に指定箇所が無く、`p9a.generate_narration_snippet(text, language, ...)`が`language=="ja"`で`JAPANESE_MODEL_NAME`(`er003_b1_p9a_audio.py:137`)+`VOICE_NAME`(同:133、"Aoede")を選ぶ。

## 2. Family C正式仕様の照合(`CURRENT_SPEC.md`)
- `CURRENT_SPEC.md:1047-1124`(Family C節)に**日本語Section(Comment/Title/Preview)のTTS Voice・言語パラメータ・ASR Validatorの規定は無い**(仕様に記載なし)。Comment本文の言語は仕様B「必要なものだけ簡潔な日本語(2〜3文・80〜110字程度)で提供する」(L1071-1073付近)のみ。Story TTSは「`tts_call_for_voice()`経由で既存Production関数(narrator=`generate_narration_snippet_verified_strict`、device=`generate_charon_english`、その他は…`generate_voice_body_wide_margin`)へ分岐し、いずれも内部にASR検証+attempt cascadeを内包する」(L1099-1105付近)。resume: 「`.ok`+`tts_text`のsha256一致判定(`resumable_reuse()`)」、regeneration: 「`--only-segments <id>...`が該当segmentのwav/.ok/metaのみ削除して強制再生成する(`purge_segment_outputs()`)」(同節)。
- 実装上の既存正式値(参考。**決定ではなく候補**):
  - **候補A(Trial-11/12でユーザー試聴OK・VALIDATED済みの呼出パターン)**: `repro01.generate_narration_snippet_verified_strict(text, "ja", out_path, text[:20])`。`er013_family_c_episode_trial_11_memory_run.py:561-571 tts_narrator(text, out_path, language, ...)`、JA Commentは同:779 `tts_narrator(txt, path, "ja", f"comment_{n}_ja", budget)`、Trial-12は`er013_family_c_episode_trial_12_twins_run.py:706`。Voice=p9a既定 Aoede / model=`gemini-3.1-flash-tts-preview` / ASR=`ja_secondary.evaluate_attempt_ja_with_cascade`(`er003_v1_repro01_main_generate.py:372-387`、ER-007 JA全文Validator+Cascade。AUW 委任_04でunified_judge adapter化済み)。**runner冒頭コメント`er013...:28-39`が「Trial-11/12でVALIDATED済みの呼び出しパターンをそのまま踏襲」と明記**しており仕様整合が最も高い。
  - **候補B(他Family X/B/legacy A/Zの標準A2 JA leaf)**: `er003_v1_n3_01_tts_generate.generate_a2_japanese_with_reading_safety`(`:785`、使用例 `er012_b_family_production_runner_01.py:1768-1770`、`er019_family_x_audio_production_runner_01.py:1270`)。Voice=Aoede(同)+ `tts_safe_ja`・placeholder Gate・Pronunciation resolver・fallback/slowdown。Trial-11/12の承認パターンとは異なる経路で、Family Cへ持ち込むと「Family Cへの新規実装」(条件2)に近づくため、**本件では非推奨**。
- AUW観点: 候補Aでも`verified_strict`の`language=="ja"`分岐が`ja_secondary.evaluate_attempt_ja_with_cascade`(統一judge adapter、`attempt_ctx`付き)を通るため、JA Comment/Title/Previewは**AUW 委任_04/05で配線済みの統一ASR判定・PASS_WITH_WARNING・HR Lock**の対象になる(新しい配線は不要)。

## 3. 静的監査の制約
Family C runnerの`get_or_run_asr`(L429-440)は診断のみ。`er078_asr_unified_wiring_static_audit_01.py:482-491 test_post_wiring_family_c_asr_is_diagnostic_only`が「runnerソースに`evaluate_attempt*|classify_asr_match|classify_ja_asr_match|unified_judge`が現れない」「`asr_verified`が現れない」を強制する。**修正はrunner内にこれらの語を書かない**。

## 4. reuse_from整合

### 4-1. 現行の再利用判定キー
- Story: 既存`{audio_dir}/{id}.wav`+`.ok`+`.ok.meta.json`の`tts_text_sha256`が現行`tts_text`のsha256と一致 -> resume(L719、L325-357 `resumable_reuse`)。
- reuse_from: `src = {reuse_from}/audio/{name}`の**存在のみ**で`_copy_with_ok`(L303-312)し、直後に`resumable_reuse`(L723-724 / L496-497 / L635-636)。**キーは「同名ファイルの有無」だけで、原稿(text)の同一性は検査していない。**

### 4-2. 旧音声が新原稿に紐づく具体的条件(コード上の欠陥)
1. `_copy_with_ok`(L303-312)は`wav`と`.ok`だけを複製し、**`.ok.meta.json`を複製しない**(`.ok`が無ければ捏造する: L310-312)。
2. `resumable_reuse`のmeta欠如分岐(L349-355)は「レガシー.ok(Trial由来コピー)」として**現行textのsha256とwavのsha256でmetaを新規に書き**(`upgraded_from_legacy_ok: true`)`REUSED_EXISTING_FILE`を返す。**旧wavが現行textの音声である証拠は一切検査しない。** 実例: `er013_output/family_c_production/memory/a2/audio/comment_1_ja.wav.ok.meta.json`が`"upgraded_from_legacy_ok": true`。
3. よって`reuse_from`に同名wavがある限り、textが変わっても必ず「再利用」になる。06d実測(`RUNTIME_EVIDENCE_06.md:339,370`、`cja_attempt1/2`): LLM再生成した新Commentに旧wavが紐づいた。
4. **regenerationが無効化される**: `--only-segments comment_N`は`purge_segment_outputs`(L704-708)でaudio_dirのwav/.ok/metaを消すが、`run_comments_stage_a2`のreuse_from分岐(L632-636)には強制再生成判定が無く(Storyは L720 `not force_regen`で保護)、purge直後にreuse_fromから旧wavが再コピーされ新textの音声として採用される(cja_attempt1が実証)。
5. 副次: `_copy_with_ok`は`dst`が既に存在すると`wav`はコピーしないが`.ok`は`src`のもの(無ければ捏造)を付ける(L305-312)ため、無関係な既存`dst` wavを有効化しうる。
6. ローカルresume(reuse_fromなし)でも、`.ok`はあるがmetaが無いwavは現行textに無条件で紐づく(L349-355)。
7. 監査上の副作用: `to_audit_entry`(L410-425)は再利用時に`canonical_text`=現行text・`disfluency_checked: True`固定を記録するため、古い音声に新原稿が紐づいた状態が監査記録上「正」に見える。

### 4-3. `.ok.meta.json`非複製の影響(AUW `asr_judgement`含む)
`mark_ok`(L360-371)は`asr_judgement`(AUW 委任_05、PASS_WITH_WARNING継承用)を`meta`にだけ保存する。reuse_fromでmetaを複製しないため、**元のWARNING record(`asr_judgement`)は引き継がれず、PASS_WITH_WARNING事後試聴リストに載らなくなる**(`RUNTIME_EVIDENCE_06.md:370` F4)。`resumable_reuse`L336-348はmetaがあれば継承する設計なので、metaを複製すれば自動で継承される。

### 4-4. 最小是正案
(a) `_copy_with_ok`(L303): `src+".ok.meta.json"`が存在すれば併せて複製(既存dstは上書きしない)。
(b) **reuse_from専用の検査関数を新設**: `reuse_from_candidate(reuse_from, name, audio_dir, expected_text_sha, canonical_text)` -> `dict|None`。
   - src wavが無ければ`None`。
   - srcに`.ok.meta.json`があり`tts_text_sha256 != expected_text_sha`なら`None`(コピーしない=旧wavがaudio_dirに入らない)。
   - srcにmetaが無い場合は`{reuse_from}/audit/tts_generation_results.json`の該当entryから「`sha256(canonical_text)==expected` かつ 記録`sha256==sha256_file(src)`」が揃う場合のみ可、揃わなければ**`None`(再生成)**。(同ファイルは`run_full_generation`がL674-676で既に読込んでいる`prev_audit`と同一。)
   - 全条件を満たした場合のみ`_copy_with_ok`(meta込み)+`resumable_reuse`。
(c) `resumable_reuse`(L325): metaに`wav_sha256`があり実wavのsha256と不一致なら`None`(wav差替え検出)。meta欠如のレガシー分岐(L349-355)は**ローカルresume後方互換のため維持**(既存test `er013_family_c_production_test_01.py:271-280`を壊さない)。reuse_from経由は(b)の入口ガードで弾かれる。
(d) `run_comments_stage_a2`(L632): 強制再生成対象(`comment_N` in `only_segments`)はreuse_fromコピーを行わない(Story L720と同じ扱い)。
(e) 3つの呼出点(L496 / L632 / L720)を(b)へ置換。

### 4-5. AUW `er078_reuse_value_guard_01`との関係(重複実装しない)
`er078_reuse_value_guard_01.guard_entry`は`resumable_reuse`L342-348で「`meta.asr_judgement`あり」の時にだけ呼ばれ、保存転写と現行canonical_textの**値/否定差**を再判定する。**metaが無い(reuse_from経由)場合は発火せず**、さらに「textのsha256が変わったか」は見ない。本件の是正は(1)metaを複製して既存guardを有効化し、(2)text hash照合を追加するもので、guardのロジックは複製・変更しない(責務分離)。

## 5. 最小修正案

### 5-1. 「単なる`"en"`->`"ja"`置換で足りるか」の判定: **足りない**
- `tts_call_for_voice`に`language`引数が無く、`run_simple_narrator_asset`は受けた`language`を捨て、Commentは`"ja"`を渡す経路自体が無いため、言語修正だけで**最低3箇所(L374/L500/L641)**。
- さらに言語修正だけでは、JAが新規生成可能になっても、reuse_from下に旧JA wavがあれば新textに旧wavが紐づく問題が残る(B-2「単一行の修正だけで品質・再利用整合を確認せず完了としない」に該当)。よって第4節(a)-(e)を最小セットで同梱する。新Voice採用・Validator新設・Writer変更などの過度な改修は行わない。

### 5-2. 変更ファイル:行と擬似diff
`er013_family_c_production_runner_01.py`
```
L374  def tts_call_for_voice(voice, text, out_path, label, budget, voice_tts_names, language: str = "en") -> dict:
L389- r = repro01.generate_narration_snippet_verified_strict(text, "en", out_path, expected_substring)
L389+ r = repro01.generate_narration_snippet_verified_strict(text, language, out_path, expected_substring)
L390  budget.add(... {"status":..., "language": language, "fn": ...})
L394+ (device / その他voice分岐の前) if language != "en": raise RuntimeError("NON_EN_LANGUAGE_NOT_SUPPORTED_FOR_VOICE: ...")  # 黙った英語化を防ぐ
L500  r = tts_call_for_voice("narrator", text, out_path, name.removesuffix(".wav"), budget, {}, language=language)
L641  r = tts_call_for_voice("narrator", text, out_path, f"comment_{n}_ja", budget, {}, language="ja")
L303  _copy_with_ok: meta複製を追加
 +    def reuse_from_candidate(...)   # 4-4(b)
L325  resumable_reuse: wav_sha256不一致 -> None
L496-498 / L632-637 / L720-725: reuse_from分岐を reuse_from_candidate(...) 経由へ置換、Commentはforced時スキップ
```
`tts_call_for_voice`の既定`language="en"`により、既存の呼出(Story、topic_intro_en)は引数が完全同一で挙動不変。

### 5-3. 英語Sectionへの非影響の論証
Story(L729)とtopic_intro_en(L807)は`language`未指定(既定"en")のため`generate_narration_snippet_verified_strict(text, "en", ...)`と引数が完全一致。device/その他voiceの分岐は不変(`language != "en"`の防御は到達しない)。`get_or_run_asr`(L429)は不変。reuse_fromガードは言語に依存しないが、**text sha256とmetaが一致するときは従来どおり再利用**(不変textの英語Story/topic_intro_enはAPI 0のまま)。再利用が止まるのは「textが変わった/由来が証明できない」場合のみ(意図した安全側)。

### 5-4. retry/fallback/regeneration/HR Lock/試聴リストとの整合
- retry/fallback: JAは`verified_strict`内蔵のattempt cascade(`review_lock.PRODUCTION_MAX_TTS_ATTEMPTS`、通算3回目cool-down、`ja_secondary`のSecondary Cascade)を通る。Family C独自のretryを持たない構造は不変。AUWの`secondary_run_scope.circuit_open()`(L380-383)は`tts_call_for_voice`入口で言語に依らず適用される。
- regeneration: `--only-segments comment_N`でCommentがreuse_fromから復活しなくなる(4-4(d))。`japanese_title`/`preview_ja`は`purge`対象リスト(L706-708)に無く`--only-segments`で再生成できない既存制約は非対象(新機能になるため)。ただし旧text残存はreuse_from検査で弾かれる。
- HR Lock/試聴リスト: `verified_strict`のJA分岐は`asr_judgement`を返し、`mark_ok`がmetaへ保存、`to_audit_entry`が載せるので、AUW 委任_05のPASS_WITH_WARNING試聴リスト(`pww_registry`)に自動で乗る。最終NGは既存HR Lock/Queueへ入る。reuse時は4-3のとおりmeta複製により`asr_judgement_inherited`が維持される。
- 費用: JA clipも1 TTS callとして`budget.add`される(`check_before`は言語に依らず`TTS_CALL_EST_JPY`=0.9)。

## 6. test計画

### 6-1. 既存testの影響(α)
`.venv\Scripts\python.exe -m pytest -p no:cacheprovider --collect-only -q er013_family_c_production_test_01.py`: 39 tests collected(実行はしていない)。
- 影響なし見込み: `er013_family_c_production_test_01.py:271-298`(resumable_reuse: レガシー分岐を維持)、`:360-390`(`tts_call_for_voice`のdispatch: 既定`language="en"`)。
- 要確認: `er078_asr_unified_wiring_06c_test_01.py:382-395`(`test_c_c_runner_resumable_reuse_guard`)・`:470-482`、`er078_asr_unified_wiring_05_test_01.py:730-747`(meta/wav_sha256継承。(c)のwav_sha256不一致->Noneは`:746`の`or {}`と整合)。
- `er078_asr_unified_wiring_static_audit_01.py:482-491`: runnerソースに判定語を書かない(関数名・コメントにも`evaluate_attempt`/`classify_asr_match`/`unified_judge`を含めない)。
- 他呼出元: `er063_family_z_audio_01.py:1286`は`build_family_c_episode_sequence`のみ使用(本修正は触れない)。

### 6-2. 新規test(β、`er013_family_c_production_test_01.py`へ追記、または新規`er013_family_c_ja_tts_fix_test_01.py`。API 0、mock)
1. JA言語選択: `run_comments_stage_a2`のTTS呼出で`verified_strict`が`language="ja"`で呼ばれる。`run_simple_narrator_asset("japanese_title.wav",...,"ja")`/`preview_ja`が`"ja"`、`topic_intro_en`は`"en"`。Story narratorは`"en"`のまま(英語回帰)。
2. device/その他voiceで`language="ja"`を渡すとRuntimeError(黙った英語化の防止)。
3. reuse_from誤紐づけ防止: reuse_from側wav+`.ok`+meta(旧text sha)・新textで`reuse_from_candidate`==None -> TTS mock呼出あり、旧wavがaudio_dirに残らない。
4. reuse_from同一text: meta複製・`asr_judgement_inherited`維持・TTS mock呼出0。
5. meta無し+由来記録あり/不一致/無しの3ケース(不一致・無しは再生成)。
6. `--only-segments comment_1`でreuse_fromから旧Comment wavが復活しない。
7. `_copy_with_ok`が既存dst wavへ無関係な`.ok`を付けない。
8. `resumable_reuse`のwav_sha256不一致 -> None。
9. 統合: `run_full_generation`をTTS/ASRをmockして実行し、全音声entryで`meta.tts_text_sha256 == sha256(audit canonical_text)`が成立する不変条件、英語Storyは再利用でAPI 0。
10. 静的: 既存`test_post_wiring_family_c_asr_is_diagnostic_only`がPASSのまま。
- 実行(実装委任で): `.venv\Scripts\python.exe -m pytest -p no:cacheprovider er013_family_c_production_test_01.py er078_asr_unified_wiring_05_test_01.py er078_asr_unified_wiring_06c_test_01.py er078_asr_unified_wiring_static_audit_01.py -q`

## 7. runtime evidence計画(Production正式経路、委任_02で実行。本委任では未実行)
- 入口: `er013_family_c_production_runner_01.py main`(Production正式entry)。AUW 06dの隔離harness(`er078_auw_runtime_evidence_06d.py:205-243 run_cja`、`er077_m1_oov_multi_pronunciation_01_evidence_runner.apply_isolation`)と同一パターンの新規harness `er079_family_c_ja_evidence_01.py`を作る。`run_cja`が使う`b.begin`はAUWの費用台帳(`cap_remaining`)を参照するため、本件は独自の費用meterを持たせる。**書込先は隔離**(HR queue / attempt_history / Master Store / telemetryを`er079_output/family_c_ja_tts_production_fix_01/evidence_02/<part>/`へ。Production state fileは変更しない)。KPI provenance: `production_formal_path`(fresh)。
- 入力: `er058_output/unified_all_roles_production_wiring_01/evidence_06b/crun/c_out`(`C_SRC`、`comments_ja.md`あり)。
- **Run A(JA新規TTS、5 clip)**: reuse_srcを`ignore_patterns("comment_*_ja*","japanese_title*","preview_ja*","web","assembled")`で複製(`comments_ja.md`は残るため**LLM 0 call**)、`--only-segments`なし。期待: Comment1-3・japanese_title・preview_jaがJAで新規生成、`ja_secondary`でOK/PASS_WITH_WARNING。確認: 各wav秒数(Commentが`status OK`)、`asr_judgement`、Segment構造(`segments.json`/assembled)、英語Story/topic_intro_enが再利用でAPI 0。
- **Run B(誤再利用防止の実体確認、1 clip)**: reuse_srcは完全複製(旧JA wav+meta含む)、`comments_ja.md`の`Comment 1`だけ文面を変更。期待: Comment1のみ新規TTS(旧wav不使用、metaの`tts_text_sha256`が新text)、Comment2/3は再利用(API 0)、旧wavがaudio_dirに残らない。
- **Run C(回帰、API 0)**: Memory A2の既存出力を複製した隔離dirで全再利用の再実行を行い、episode wavのsha256が既存(Trial-11承認済み、`CURRENT_SPEC.md`の「sha256完全一致[316.569秒]」)と一致すること。
- コマンド全文(Run A例。Run B/Cはpart名のみ変更):
  ```
  cd C:\Users\tensh\eigo-radio
  $env:TTS_EXECUTION_MODE = "STANDARD"
  .venv\Scripts\python.exe tools\stop_scope_check_01.py --managed-id FAMILY-C-JA-TTS-PRODUCTION-FIX-01 --run-dir er079_output\family_c_ja_tts_production_fix_01\evidence_02\ja_new --out er079_output\family_c_ja_tts_production_fix_01\evidence_02\ja_new\stop_check_pre.json   # rc=3なら実行しない
  .venv\Scripts\python.exe er079_family_c_ja_evidence_01.py ja_new --execute --budget-jpy 8
  ```
  (harness内部で`C.main()`を`--config <隔離dir>/article_config.json --level a2 --budget-jpy 25`で呼ぶ。runner内部guardはTTS 0.9/ASR診断 0.3 JPYの保守見積のため`--budget-jpy 25`が必要で、06d `cja_attempt0`は`--budget-jpy 8`でguardが早期停止した実績[`RUNTIME_EVIDENCE_06.md` F6]。実費上限はharnessのMeter hard_stop[`--budget-jpy 8`]が担保する。)
- STOPセンチネル配置先: `er079_output\family_c_ja_tts_production_fix_01\evidence_02\<part>\STOP`(および既存の全`*STOP_NOTICE*`/`STOP_ALL`。自分で削除しない)。
- 見積JPY(推定、根拠付き): TTS 1 clipの単価は2系統ある。(i)`DESIGN_01 §9`の推定 JPY0.062/clip(`RUNTIME_EVIDENCE_06.md:113`)。(ii)06d `cja`の実測 約JPY4.12/9 attempt(約JPY0.46/attempt、同:320、JA約16秒音声)。保守的に(ii)を採用し1 clipあたり1〜3 attempt: Run A = 5 clip x 0.46 x (1〜3) = 約JPY2.3〜6.9(期待約JPY3)、Run B = 1 clip = 約JPY0.5〜1.4、Run C = ASR cache hitならJPY0。OpenAI ASR JPY0.0094/call(同:113)、Azure SecondaryはPrimary NG時のみ JPY0.0444/秒。**合計期待約JPY4、上限(hard_stop)はRun A JPY8 + Run B JPY3 = JPY11**。承認区分C(承認済みscope内)。
- 所要時間: Run A 約8-15分(TTS 5 clip + ASR + Assembly + MP3化)、Run B 約3-5分、Run C 約3分。Run A/B/Cは入出力dirが独立なので並列可(同一API rate limitのためAUW cool-down[通算3回目600秒]に当たる場合のみ直列)。
- リスク: Run Aは`run_full_generation`の末尾(Assembly/Audio Validation Gate/mp3/web)まで走る。06b `crun`で同経路は完走実績あり(`RUNTIME_EVIDENCE_06.md:169`)。

## 8. 新しい仕様判断の要否(B-3のSTOP条件該当有無)
**なし(承認範囲内で実装可)**。新Voice採用なし(候補AはTrial-11/12でユーザー試聴OKのVoice/経路[p9a既定Aoede、`verified_strict ja`]をそのまま使う)、音声品質基準・Validator閾値の変更なし、Comment内容仕様の変更なし。例外: JA経路を候補Aではなく候補B(標準A2 JA leaf)にする場合は「Family Cへの新規実装」(条件2)に近づくため、その場合のみFable/ユーザー判断が必要(本書は候補A推奨)。

## 9. 新規発見の独立問題(OPEN候補、記載のみ)
- N1: `japanese_title.wav`/`preview_ja.wav`は`--only-segments`による再生成対象リスト(L706-708)に含まれない。新機能扱いのため本件では非対象。
- N2: `to_audit_entry`(L410-425)は再利用時に`disfluency_checked: True`を固定で書く(再利用元の記録を見ていない)。監査表示のみで判定には使われていない。
- N3: `resumable_reuse`のレガシー分岐(meta欠如、L349-355)はローカルresumeで依然「無条件紐づけ」。reuse_from経路は是正するが、本分岐の削除は既存test(`er013_family_c_production_test_01.py:271`)と後方互換に影響するため非対象。
- N4: `tts_call_for_voice`の`expected_substring = text[:20]`(L388)は`verified_strict`で旧フィールド扱い(記録のみ)。実害なし。
- N5: `to_audit_entry`はreuse時、reuse元のASR/判定が無い場合の扱いが「OK」固定。上記N2と同根。

## 10. 次委任用のSSOT追記文案(本委任では編集しない)
### OPEN_ITEMS.md OPEN-372 Status更新文
`[ユーザー承認済み既存Production不具合是正・実装中/検証待ち]`: 2026-10-16ユーザー指示B(FAMILY-C-JA-TTS-PRODUCTION-FIX-01)により是正承認。`tts_call_for_voice`へ`language`引数を追加し、JA Comment/JA title/preview_jaを`verified_strict(...,"ja")`(Trial-11/12 VALIDATED済みの呼出パターン、Voice=Aoede)で生成、reuse_fromはtext sha256/meta/由来記録で照合し、旧音声が新原稿に紐づかないようにする。完了条件(runtime evidence・Validator/Regression/integration test PASS・Dangling Reference Check)未充足の間は`PRODUCTION_WIRED`としない。AUW統一ASR判定とは別件。
### DECISION_LOG.md 新規節案「FAMILY-C-JA-TTS-PRODUCTION-FIX-01」
2026-10-16、ユーザー指示B「既存Production不具合の是正承認」。対象はLegacy/Backup Family C(`CURRENT_SPEC.md`「Family体系(2026-09-27)」条件2「Family A/B/C向けに新規実装を行わない」)だが、本件は新機能追加・最新仕様への追従ではなく、既に承認済みのFamily C仕様(Comment日本語化、Trial-11/12 VALIDATED済みの呼出パターン)が`tts_call_for_voice`のen固定とreuse_fromの旧音声紐づけで動作しない不具合の是正であるため、**例外的是正**として許可された。新Voice採用・品質基準変更・Comment内容仕様変更なし(必要になれば別途ユーザー判断)。AUW統一ASRとは別件。
### CURRENT_SPEC.md Family C節(L1047-1124)への追記案
「**日本語Section(Comment 1-3・japanese_title・preview_ja)のTTS**: `tts_call_for_voice()`は`language`引数を持ち、日本語Sectionは`language="ja"`で`generate_narration_snippet_verified_strict`(Voice=Aoede、ASR=ER-007 JA全文Validator+Cascade)を呼ぶ。**reuse_from**: コピー元のtext sha256(`.ok.meta.json`、無い場合は`audit/tts_generation_results.json`の由来記録)が現行原稿と一致する場合のみ再利用し、不一致・由来不明は再生成する。`--only-segments comment_N`でreuse_fromから旧音声が復活しない。」

## 11. 受入記録(5項目)
1. 当初目的: ユーザー指示B-1/B-2(`docs/pm/delegation_log/2026-10-16_FAMILY-C-JA-TTS-PRODUCTION-FIX-01_01.md`に逐語)。本委任の範囲は調査・是正設計(read-only)。
2. 最終成果物: 本書 `er079_output/family_c_ja_tts_production_fix_01/INVESTIGATION_01.md`。
3. 証拠: コード行(第1・4節)、06d debug.json・runner_execute.json(第1-2)、memory/a2 meta(第4-2)、Trial-11/12呼出(第2)、`pytest --collect-only` 39 tests。
4. 一致/不一致: 第1-8節に記載。仕様未記載=JA Voice名(Trial実績をもって候補A)。
5. 判定: `FIX_PLAN_READY`(実コード・実音声での検証は委任_02)。

## 訂正(FCJ 委任_02、Opus FCJ-05 / R5)
5-4節の「通算3回目cool-down」は誤り。cool-downは`cooldown_total_budget`が渡された場合のみ作動し、Family Cは渡さない(`tts_call_for_voice`は`verified_strict`を`cooldown_total_budget`なしで呼ぶ)ため、**Family C JA経路にcool-downは適用されない**。cool-downの追加は本是正の範囲外(Legacy Family Cへの新規実装になるため行わない)。
