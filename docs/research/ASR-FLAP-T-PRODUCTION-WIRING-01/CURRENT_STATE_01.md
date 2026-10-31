# ASR-FLAP-T-PRODUCTION-WIRING-01 委任_01 CURRENT_STATE_01(調査・API 0・Production code変更0)

作成: 2026-10-31。基点=origin/main `92a4e79c3`(一時worktree)。ユーザー原文=`docs/pm/delegation_log/2026-10-31_ASR-FLAP-T-PRODUCTION-WIRING-01_USER.md`(逐語保存、以下「原文:行」)。
Trial成果の根拠=`docs/research/ASR-FLAP-T-EQUIVALENCE-TRIAL-01/`(DESIGN_01/CLOSEOUT_02/VOICE_PROBE_02、`tools/flapt_equivalence_proto_01.py`+test)。実行は`C:/Users/tensh/eigo-radio/.venv`のpython(CMU辞書`pronouncing`/`cmudict 1.1.3`)。

## 1. Trial成果の再確認(再実行)
- `flapt_equivalence_proto_01_test_01.py` **36 passed**(今回再実行)。
- **Opus M1(tokenizer数字)の実害を再現**: Trial protoの`tokens()`は`[A-Za-z]+`のみで数字を落とす。実測(今回): `evaluate("The latter 13 option","The ladder 30 option")`=**RESCUE**、`("I paid $13 for the latter","I paid $30 for the ladder")`=**RESCUE**(値13/30の差を見ずに通る)。Primaryの最終ANDゲートは値DIFFを残すが、KP票経路は値ガード解除済み(`er104_kp_three_asr_vote_01.py:266`系、2026-10-22保護解除)でflap層が唯一の砦になるため、**Trial protoをそのまま移植してはならない**(M1必須)。
- 実音声: probe 191 clip(通常155+Std減速36)、13 (Voice,path)組合せ全てFLAP_DEMONSTRATED、T_SPELLED 0(`VOICE_PROBE_02.md`2節)。保存ASR 6,979転写/現行NG 1,336(`stored_census_02.json`)でRESCUEは latter→ladder・bertie→birdie のみ、誤救済0。

## 2. Opus実装前修正 M1〜M6 の現状(`CLOSEOUT_02.md`7-8節。全て**未実装**=委任_02で実装。設計は`DESIGN_01.md`3節)
| M | 内容 | 現状 |
|---|---|---|
| M1 | tokenizer: 数字・記号もtoken、flap対置換後の全token完全一致 | 未実装。Trial protoは上記のとおり数字を落とす(実測RESCUE)。Production tokenizerは`er109_asr_orthographic_equivalence_01.py:274-281`の`_TOKEN_RE`(num/money/time/ord/frac/word/sym) |
| M2 | voice/path受渡し | 未設計→本設計(DESIGN_01 3節)。現状 `er109_xz_scope_01.py:149 decision()` にvoice引数なし、呼出元は下記3節のとおり全てvoiceを持たない、`_evaluate_cached`:125のcache keyにもvoiceなし |
| M3 | label/version | 未実装。`ORTHO_WARNING_LABELS`:33は`{ORTHO_NEGATION_WORD_HOMOPHONE, ORTHO_NON_REPRESENTATIVE_VARIANT}`のみ。`decision()`は`eq.version != LAYER_VERSION`でNoneを返す(:149以降)ためflap専用versionを返すには分岐追加が必要 |
| M4 | 静的Voice表 | 未実装(Trialは`voice_probe_02.json`の`allowlist_proposal`のみ) |
| M5 | 追加probe(約¥20) | 未実施 |
| M6 | CMU sha・Whisper票・親子flag | 未実装。`cmudict 1.1.3`(`pronouncing`はこれを使用) |

## 3. 既存ASR同音救済・Connected Speech救済の実装位置(Flap層の第3層としての接続点)
| 層 | 位置 | Flapとの関係 |
|---|---|---|
| CMU 1:1同音(完全一致)/PNMH/Tier1/Tier3/CMU alternate/M1 | `er006_preprod_hardening_01_validation.py:821-846,1115,1148,1360`、`er008_asr_variant_hardening_15_homophone_en.py:197` | 先に評価。latter(T)/ladder(D)は別音素で不成立 |
| Connected Speech Equivalence(OPEN-122、flapping_intervocalic) | `er011_connected_speech_equivalence_layer_production_01.py:125-131` | 語末脱落型+独立ASR corroboration必須+A2/B1本文のみ。語中t/dは対象外=**重複・競合なし**(Flap層はこれを変更しない) |
| er109(表記違い同音、UKUS第2層) | `er109_xz_scope_01.py:149 decision()`(scope∈{X,Z,Y}∧flag=`is_active_for_run`:92) | **Flap層の接続点**。er109が`equivalent=False`のときだけ後段に評価(P1: 既存の勝敗は不変) |
| 呼出点(全て`decision()`経由) | Primary `er006_secondary_asr_01.py:1135-1142`、Secondary `:1207-1211`(`_secondary_fn`:1188)、KP票 `er104_kp_three_asr_vote_01.py:246-259 _classify`/`:287-289 make_voter`、judge側`er078_asr_unified_judge_01.py:386-399(primary unlock)/:405-421(secondary precheck)/:428-443(_ortho_mark_votes)/:786-796(secondary)`、X再構築 `er019_family_x_validation_inheritance_01.py:323-340`、HR再判定 `er109_hr_lock_rejudge_01.py` | 全て同一`decision()`へ集約されるので**新規call siteを増やさず**第3層を足せる。Voice受渡しだけが新規(DESIGN_01 3節) |
| 最終ANDゲート(値DIFF/否定差) | `er078_asr_unified_judge_01.py:73-77`(`APPROVED_EQUIVALENCE_BASES`)、`er109_xz_scope_01.py:255 explain_protected` | ORTHO_BASISは基底に**入れない**(=ゲートをskipさせない)。flap decisionの`eq.version`が`LAYER_VERSION`と異なれば`explain_protected`は`decision_not_equivalent_or_version_mismatch`でFalse=値/否定差を解除しない(M3の構造保証) |
| 警告の後続保持 | `er078_pass_with_warning_registry_01.py:61`(`judgement.warnings`から導出)、`er078_reuse_value_guard_01.py:85-92`(ortho/UKUS寄与音声のStore再利用ガード) | ラベルが`asr_judgement.warnings`に載れば事後試聴リストへ流れる(ORTHO_*専用の登録先は無く汎用)。Store再利用ガードは`ortho_contributed`(`orthographic_equivalence.applied`)で既にflap救済音声も捕捉できる(flag OFF/scope外へ再利用させない)。Flap専用の追加ガードは設計(DESIGN_01 6節) |

## 4. X/Y/Z runnerのASR判定呼出とVoice情報の到達経路
- 判定入口は全て`er006_secondary_asr_01.evaluate_attempt_with_cascade[_detail]`(:874、wav shaは`_AzureShared.sha`=:972)に収束する。EN leaf側の呼出元(非test・非Trial): `er003_v1_n3_01_tts_generate.py:146`(減速後再検証)/`er003_v1_crosslevel_audio_02_common.py:554`/`er003_v1_repro01_main_generate.py:378`/`er003_v1_sing01_news_tail_fix.py:280`/`er003_v1_sing01_point_headings_aoede.py:129`/`er003_v1_sing01_voice01_generate.py:314`/`er012_b_family_voices_production_01.py:590`(Z dialogue。B兼用だがscope外では短絡)/`er096_kp_dual_pass_01.py:120`/`er104_kp_vote_reuse_01.py:123`。**どの呼出元もVoice/modelをjudgeへ渡していない**(grep: er006/er078/er104のjudge関連に`voice`語なし)。
- runner scope(`er109_xz_scope_01.family_scope`): X=`er019_family_x_audio_production_runner_01.py:1663,2037`、Z=`er063_family_z_audio_01.py:1630`、Y=`er121_family_y_audio_01.py:555,645`(Y追加は`APPROVED_SCOPES`=`{"X","Z","Y"}`:`er109_xz_scope_01.py:26`)。
- **Voiceの実送信値の決定点**: `er002_gemini_client.effective_voice()`(:54、送信と記録の単一決定関数)。Z narratorは`voice_override`スコープ(`er063_family_z_audio_01.py:1129`)で置換。実際にAPIに載る値は**SDK境界**で独立記録されている(`er005_cost_logger.py:171-224 _patch_gemini`の`tts_voice_sent`+`model_id`、Standard同期)。Batch(Production既定`TTS_EXECUTION_MODE=BATCH`、`er006_batch_tts_wiring_01.py:255-340`)は`make_batch_tts_call_fn(model_name,voice_name)`が両値を保持し、成功時`_resolve_single_item`:207が`model_name, voice_name`を知る。leafは結果dictに`voice`/`model`を記録(`er003_b1_p9a_audio.py:288`)、attempt JSONにも保存(`voice_census_01.json`の根拠、sha`audio_sha256`付き: `phase3_rejudge_02.json`)。
- TTS経路(`voice_census_01.json`、EN attempt数): **X**=flash-lite{Aoede 748, Charon 210}+2.5-pro{Aoede 137, Charon 58}(後者は旧/structured_separation)。**Y**=flash-lite{Aoede 148, Algieba 48, Charon 37, Schedar 17, Zephyr 22, Puck 5}。**Z**=2.5-pro{Algieba 136, Zephyr 73, Charon 52, Schedar 44, Erinome 28, Kore 28, Orus 21, Fenrir 14, Puck 13, Aoede 4}+flash-lite{Aoede 711, Charon 93, Fenrir 25}(Narrator/KP等)。Z計画Voice: 男性1 Algieba/2 Schedar/3 Fenrir/4 Orus/5 Puck、女性1 Zephyr/2 Kore/3 Leda/4 Sulafat/5 Erinome(`CURRENT_SPEC.md:1566-1567`)。Std/Advの差はmodel/style/速度後処理のみでVoice差なし。
- 速度後処理: Std A2は6%減速(`er008_a2_postprocess_slowdown_01.py`、既存probeで維持確認済み)。**Z Adv dialogueは約6%高速化**(`er063_family_z_audio_01.py:60 Z_ADV_DIALOGUE_SLOWDOWN_PCT=-5.66`=tempo 1.06)で、これは**未probe**(追加確認項目、API実費≈¥0.05×数clip)。

## 5. retry/fallback/regeneration/resume経路(Flapは各attempt判定にPASSを1つ加えるのみ)
- retry/fallback(標準2→minimal 1、KP 4回構成、`er127_tts_block_policy_01` 3回+180秒+LR block): 各attemptが`evaluate_attempt_with_cascade*`を通る。Flap救済があればそのattemptで`verified`となりループ終了=回数・上限は不変(増えない)。
- Local Rewrite: LR後の再TTSは書換え後文をcanonicalに再judge(`er003_v1_crosslevel_audio_02_common.py:554`の`_run_a2_minimal_fallback_attempt`が`attempt_ctx`のscript_version="v1"で呼ばれる)。Flap層は同一規則で再評価。
- resume(`er127`の`stub_row`/n_started永続化): 判定済みattemptは再judgeされないのでprovenance台帳は不要。**例外**: 保存音声の再judge(`er019_family_x_validation_inheritance_01.py:323-340`、`er109_hr_lock_rejudge_01.py`)は台帳が空=既定で不適用(従来と同じNG)。attempt JSONの`voice`/`model`/`audio_sha256`から台帳を復元するhelperで限定的に有効化する(DESIGN_01 3-4)。
- Master Audio Store再利用: `er078_reuse_value_guard_01.py:85-92`が`ortho_contributed`寄与音声を `not is_active_for_run()` でblock。Flap救済音声は`orthographic_equivalence.applied`を持つため同ガードに自動で乗る(flap専用のvoice表sha不一致ガードは追加。DESIGN_01 6節)。
- 既存のbaseline失敗(今回再現): `er109_wiring_golden_test_01.py` 3件+他1件が**origin/main `92a4e79c3`で既に失敗**(OPEN-501 ER109-WIRING-GOLDEN-TEST-3FAIL-ATTRIBUTION-01。34行がscope Xで署名変化)。**配線後は「失敗集合がbaselineと同一」を回帰基準にする**(新規失敗0)。他agentの`baseline_fail_ids.txt`(244行)も同種の既存失敗を含む。

## 6. 未probeのVoice/TTS経路一覧(fail-closed。DESIGN_01 4節で追加probe対象に)
Trial許可リスト案=15組合せ(Aoede/Charon/Algieba/Puck/Schedar/Zephyr/Fenrir|fl、Orus/Kore/Erinome/Sulafat/Leda/Iapetus|pro、Schedar|pro・Zephyr|pro[保存記録のみ])。Production実使用のうち**未probeまたは独立probe未了**:
| 組合せ | 使用Family | attempt数 | 状態 |
|---|---|---|---|
| Zephyr\|pro | Z(女性1) | 73 | probeは較正2 clipのみ(INDETERMINATE)。許可根拠はBertie保存記録のみ=**Opus注1循環** |
| Schedar\|pro | Z(男性2) | 44 | 同上(許可根拠=Bertie保存記録のみ) |
| Algieba\|pro | Z(男性1) | 136 | 未probe |
| Charon\|pro | X旧/Z | 58+52 | 未probe |
| Aoede\|pro | X旧/Z | 137+4 | 未probe |
| Fenrir\|pro | Z(男性3) | 14 | 未probe |
| Puck\|pro | Z(男性5) | 13 | 未probe |
| Z Adv dialogue 1.06x速度 | Z | - | 速度後処理版は未probe(ASRのみで可) |

Kore\|fl等は使用実績0で不要。Iapetus\|proは9/12 clip(判定には十分、`VOICE_PROBE_02.md`4節3)。flash-lite側はX/Y/Zの使用Voiceが全てprobe済み。

## 7. 許可リスト根拠の循環
- 循環あり(要解消): Zephyr\|pro・Schedar\|proの許可根拠=「Bertie→Birdieの保存転写」であり、同時に削減効果(約¥21)の根拠でもある(Opus注1/2)。独立probe(M5)で解消する。
- 循環なし: 他13組合せはVoice probe(語リスト固定・独立clip生成・3系統ASR)が根拠で、救済対象の本番segmentとは別事象。許可条件は「d綴り転写が実在=Flap層が必要な事象がそのVoiceで起こりうる」(`VOICE_PROBE_02.md`4節1)であり、Voiceのアクセント断定ではない。
- 追加の構造的注意: 許可リストを本番ASR結果で拡張する自動学習は**行わない**(それこそ循環)。表は人手でprobe証跡のshaを付けて更新する静的ファイル(DESIGN_01 4節)。

## 8. 再利用可能な資産と不要なAPI実行の回避
| 資産 | 再利用 | 用途 |
|---|---|---|
| Trial 36 test(`flapt_equivalence_proto_01_test_01.py`)+`case_results_01.json` | 移植・差分parity | Production moduleのunit testへ(P01-P12/N01-N18/X01-X03/U01/V1)。数字token・値差のM1回帰を追加 |
| 保存ASR 6,979転写/NG 1,336(`stored_census_02.json`、`flapt_stored_census_01.py`) | API 0 | 正式判定経路(`decision()`)でreplay: RESCUEが2語のみ・誤救済0の再確認 |
| 実音声191 clip(`probe_02*/wav/`、main tree側ローカル、shaで同定。worktreeには存在しない) | 再ASRなし(転写は`results.jsonl`に保存済み) | 保存転写をproduction judgeにreplay(Voice=probe記録のvoice/modelを台帳へ注入) |
| ⑨ Meta `latter→Ladder`のattempt(`phase3_rejudge_02.json`: attempt1 Aoede flash-lite、OpenAI「Ladder」/Azure「Ladder.」、wav sha付き) | API 0 | 正式adapter(`evaluate_attempt_with_cascade_detail`)に保存転写をinject(`vote_whisper_fn`注入等)して発火証拠 |
| Z Bertie→Birdie 保存attempt(Zephyr/Schedar\|pro) | API 0(独立probe後に許可) | 同上。許可リスト確定前は**不適用であることの反例**としても使える |
| `tools/flapt_voice_probe_02.py`(Production leaf呼出のみ) | 追加probe | 7組合せ(DESIGN_01 4節) |
