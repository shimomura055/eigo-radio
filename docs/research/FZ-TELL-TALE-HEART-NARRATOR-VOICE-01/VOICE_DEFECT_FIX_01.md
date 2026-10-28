# FZ-TELL-TALE-HEART-NARRATOR-VOICE-01 委任_03 不具合調査・修正(2026-10-28)

状態: **修正完了・部分再生成済み(b1b全narrator+a2先頭2clip)。再生成run=予算guard(WARN_THRESHOLD)で途中停止。残りa2 5clip+後段(provision_shell/gate/assemble/pages/page_verify)は未実行=Fable判断待ち。** 候補ページは旧(Aoede版)のまま。

## 1. 真因(API 0、file:line)
- `er063_family_z_audio_01.py` real_generators `narrator()`(修正前L1017-1027)は`spec.voice`を一切使わず、共有leaf(`news_tail_fix.generate_news_narration_wide_margin` / `n3_tts.generate_a2_segment_with_slowdown`)へ呼出。
- leafは英語narratorの送信Voiceを固定定数`p9a.VOICE_NAME`(=Aoede、`er003_b1_p9a_audio.py:133`)から取る(`news_tail_fix.py:228`、`p9a._make_english_call_fn`:192、`crosslevel`、`repro01:338,632`)。`ClipSpec.voice`を受ける引数が共有leafに存在しない。
- `ClipSpec(voice=Fenrir)`・`tts_generation_results.voice`・`reuse_key.voice`・chunk_plan記載は全て**計画/記録値**でAPI送信値ではなかった。attempt JSONの`"voice": "Aoede"`は`p9a.VOICE_NAME`=**実送信値そのもの**(ラベルではなかった)。
- Z既定Narrator=Aoede=leaf定数だったため構造的欠陥が不可視だった。dialogueは別経路(`bvoices.generate_voice_body_wide_margin(text,out,spec.voice)`→`make_batch_tts_call_fn(..., voice_name)`)でspec.voiceを送るため正常。
- 追加で発見した同種の穴: `er127.with_block`のblock progress fingerprintにVoiceが無い(Style/backend/policyのみ)。旧DONE progressがVoice違いでresume再利用され得る。
- 追加で発見した再利用の穴: 誤記録entry(Fenrir key・Aoede音声)が`tts_generation_results.json`にあり、そのまま再実行すると「Fenrirで再利用済み」として0 APIで通る。

## 2. 実音声の証拠(f0、`evidence/f0_pre_fix_01.csv` `f0_midrun_after_fix_01.csv` `f0_pooled_midrun_01.csv`、tools/f0_measure_01.py・f0_pooled_01.py)
方法: 自己相関f0(numpy、librosa未導入)、voiced frameのp10/p25/median/p90。参照=Y男声Trial実音声(Fenrir/Algieba)、Aoede=run_reselect_01。
- 修正前「Fenrir版」narrator(Std 4clip pool中央値172Hz、Adv 180Hz)はAoede(run_reselect_01 Std 178Hz)とp10~p90ともほぼ同一=**音声はAoedeだった**(sha差は非決定TTSで証拠にならない)。clip別でも「Fenrir版」旧と Aoede版の差は±10Hz内。
- 修正後Adv narrator(再生成4clip pool)は p10=116.8/p25=132.2(旧142.9/160.0、Aoede 144.1/156.9)、Fenrir参照(p10 103.9/p25 114.1)方向へ低音側が約25Hz移動。中央値は160Hz(旧180)。
- 注意: narrator Styleは抑揚が大きくf0中央値の絶対値は参照試験(別Style)と直接比較できない。f0は「Aoedeと同一ではなくなった」ことの客観指標であり、単独で「Fenrir」を断定しない。断定はSDK境界のtts_voice_sent記録(下記)+attempt JSON+f0の3点一致で行う(再生成済みb1bはtts_voice_sent導入前=attempt JSONとf0のみ)。
- dialogue(old_man=Algieba)は既存clip(part1_c3)で再利用・sha不変だが、短い(voiced 57-67 frame)ためf0は参考値(中央値~190Hz)。dialogueの送信Voiceは経路上spec.voiceを渡す(上記file:line)ため修正対象外。

## 3. 修正(最小・既定動作不変)
- `er002_gemini_client.py`: `voice_override(voice)` contextmanager + `effective_voice(voice_name)`。scope内でのみ「既定Narrator Voice(Aoede)で送ろうとした呼出」を指定Voiceへ置換。`build_speech_config`(batch/standard/p7a全共通)に配線。環境変数・flag・引数で外部からONにできない(Z narrator()のみがscopeを張る)。
- `er006_batch_tts_wiring_01.make_batch_tts_call_fn`/`er033..make_speech_metadata_call_fn`/`make_speech_metadata_batch_call_fn`(Z本番backend): factory先頭で解決(送信値・batch telemetry記録値を一致)。
- `er063` `narrator()`: `with gclient.voice_override(spec.voice)`で生成呼出全体(retry/fallback/LR/減速後再検証/resume)を包む。Style・回数・待機・ASR・速度は不変。Aoede narrator(Melos等)はno-op。
- 記録: `news_tail_fix`(3)/`crosslevel`(2)/`repro01`(2)/`p9a`(1)の`"voice"`を`gclient.effective_voice(...)`に(attempt JSONが実送信値を記録=OPEN-572是正)。
- `er127.with_block`: override Voice(Aoede以外)のときのみfingerprintへvoice追加(override無し=従来fingerprint不変、別Voice旧progressを再利用しない)。
- `er005_cost_logger._patch_gemini`: SDK境界の実request configから`tts_voice_sent`をcost_logのTTS行へ独立記録(additive、text呼出に付かない)。
- test: `er063_z_narrator_voice_override_test_01.py`(11件OK: (a)fake genai clientが受けたrequestのvoice名=Fenrir [standard/batch factory/p7a] (b)scope外・他Voice(Charon/Algieba)不変・env/flagで有効化不可 (c)Std/Adv narrator全attempt同一Voice+例外後scope復帰+fingerprint (d)attempt記録サイトがVOICE_NAME直書きでない+cost_log独立記録)。既存回帰: er003_v1_n3 std/adv 27+28 / er033 36 / er127 123 / er019 runner 53+std_chunk 18 / er063 speed_v2 31 / er011 mode_switch wiring OK。
- 既存失敗2件(本修正由来でない): (1)`er063_z_std_chunk_test_01`の凍結golden(tell_tale narrator voice=Aoede)が前委任のFenrir化で陳腐化→golden比較でnarrator voiceのみ`narrator_voice_for`一致確認に修正(他key成分は凍結値一致のまま) (2)`er063_family_z_audio_01_test_01.test_preview_comment_kp_styles`は共有`human_review_queue`に残存する`x/a2/kp1_en` HUMAN_REVIEW_REQUIRED(2026-10-28 09:18、他task/試験が作成)でkp_enが0 APIになる環境汚染(clean worktree HEADではPASS)。

## 4. 再生成の状況(有料、1起動)
- 退避: narrator 9clip/level(chunk+親)のwav・`_original`・attempt・tts_block_progress・results entryを`run_voice_fenrir_01/{a2,b1b}/audit/legacy_voice_mislabel/`へ(MANIFEST.json、85件、results旧版保存、削除/上書きなし。`tools/retire_mislabeled_narrator_01.py`)。非narrator40wav shaは`evidence/non_narrator_sha_before.txt`。
- 起動1回(PID 2332→終了): tts_b1b完了(narrator 7chunk+親、attempt JSON voice=Fenrir)・tts_a2はpart1_c1/c2再生成後、`FamilyZBudgetStop: WARN_THRESHOLD spent=18.27+est 2.00 > limit 20.00`でAPI前に停止。原因=`--approved-budget-jpy 20`は**run累計**(前回10.2258含む)に対する値で、私の指定ミス。実費(本起動)=¥8.04(16.1886-10.2258=5.96[b1b]+2.08[a2 2clip])。
- 再起動は委任文の許可(1起動)を超えるため実施せず。残り見積≈¥3.4(a2 5clip)。再起動案=同一argvで`--approved-budget-jpy 30`(累計基準。本委任の増分は合計≈¥11.4でCap¥40内)。

## 5. 受入判定の漏れ分析(事実)
| 段 | 何を根拠にしたか | 何が欠けたか |
|---|---|---|
| 前回worker検証(委任_01) | `tts_generation_results.voice`/`reuse_key.voice`=Fenrir、chunk_plan記載、voice_assignment.json、registry test(`narrator_voice_for`) | いずれも計画値/自己記録(`ClipSpec.voice`をそのまま書き写す)。API送信値・実音声を見ていない。mockはspec.voiceがClipSpecに入ることまでで、leafがspec.voiceを使うかを検証していない |
| 前回worker検証 | attempt JSON `voice: Aoede`が存在 | 報告に出さず(voice欄を「再生成clipのvoice=Fenrir」とresults側のみで記述) |
| 前回Fable受入 | attempt JSON voice=Aoedeを「leaf定数のラベル」と解釈 | 解釈の裏取りなし(leafの`"voice": p9a.VOICE_NAME`が**送信に使う同じ定数**であることをfile:lineで追わなかった)。矛盾する観測を、コード追跡なしに「記録の癖」と片付けた |
| 構造 | cost_log(`er005`)にVoice欄が無く、STANDARD実行ではbatch telemetryもVoiceを残さない | API送信パラメータの独立記録が存在しなかった(本委任でtts_voice_sentを追加) |
| 構造 | 既定Narrator=Aoede=leaf定数のため、Z全storyで不可視だった | Aoede以外のnarrator pinを置いた初のケースで顕在化 |
| 判定語 | PRODUCTION_WIRED/Production完成 | 「配線された=設定値が書かれた」と「実音声が変わった」を区別しない判定語だった |

再発防止(必要十分の案。Gate追加の要否はFable判断):
1. Voice/Style/話者変更の受入は3点一致を必須: (i)API送信パラメータの独立記録(`cost_log.jsonl`の`tts_voice_sent`、batch時はbatch telemetryのvoice) (ii)実音声の客観指標(f0分布を参照voiceと比較。`tools/f0_*`) (iii)計画/記録値(results/reuse_key)。(i)と(iii)がclip単位で不一致=重大NG。(ii)がAoede帯と区別できなければ「未確認」。
2. 矛盾する観測(attempt JSONのvoice≠計画)を「ラベル」と解釈して受入する場合は、該当値の送信への関与をfile:lineで追った記録を必須とする(追えない=受入不可)。
3. testはSDK境界(`client.models.generate_content`に渡るconfig)を捕捉する形に統一(本委任のtestを雛形に。`ClipSpec`に入った=送信されたの推定をtestで置換しない)。
4. 実装(本委任で完了): attempt JSONのvoice=`effective_voice`(送信と同一関数)、cost_logの独立記録、block progress fingerprintへのvoice。Gate追加(例: 受入時に`tts_voice_sent`集計と計画voiceを機械照合する`voice_acceptance_check`)は案のみ=Fable判断。
