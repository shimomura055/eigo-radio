# KP4「take part」問題音声の是正(FAMILY-X-MANGA-AI-CHAT-BYUS-KP4-TAKE-PART-REMEDIATION-01 委任_01、2026-10-21)

性質: 既存の承認済み音声品質基準に基づく不具合修正(ユーザー実施承認済み)。Productionコード・Prompt・閾値・Validator変更なし。Task B(ASR 3方式比較)とは独立。
ユーザー原文: `docs/pm/delegation_log/2026-10-21_KP4-REMEDIATION-AND-ASR-THREE-WAY-TRIAL_USER.md`(5,204字、本文sha256 80362b65dc8149d7fe11559e6603922901ab377db1f27adffe95b14c738ad735)。

## 1. 問題音声の無効化結果
- 対象: Std(a2)KP4 `take part`、旧`kp4_en.wav` sha256 675cd6b1aec9865acbdb411b588672d9cc963b936bb4a35bb2d8158cb4172186。Master Store entry id `0714639d351b47c34b4d4103`(key A=`key_phrase_english_component_k2`/`v2_margin030+k2.9d905cfe6c04`/primary)。
- 手段: 既存の`reuse_blocked` mark機構(`er078_reuse_value_guard_01.py:40-42` guard_entry、`er006_master_audio_store_01.py:116-134` get_or_generateが再生成へ回し旧音声を`audio/_reuse_blocked/`へ退避)を、該当entry 1件にだけ付与(`er092_kp4_remediation_01.py invalidate`)。**Store/KP/runnerのProductionコード変更0行**(新規機構不要)。manifest変更entry数=1(`changed entries: ['0714639d…']`をassert)。他entryは不変。
- 旧音声は削除せず改名保存: `a2/narration/kp4_en.invalid_20261021.wav`(sha 675cd6b1…2186、Task Bが問題音声として再利用)、`a2/narration/attempts/kp4_en_attempt1_custom60ebc452.invalid_20261021.{wav,json}`、Store側`er006_output/master_audio_store_01/audio/_reuse_blocked/0714639d…_invalid_20261021_preserved.wav`(+get_or_generateの自動退避)。
- 影響範囲: 旧sha 675cd6b1…を持つ音声ファイルは全リポジトリで本runのa2 KP4のみ(Grep確認。b1b KP4=fa9f7dda…は別key=別音声、他記事のkp4_en.wavもsha相違)。他記事・他segment・Advへの伝播なし。

## 2. 再生成音声の品質判定
- Production KP経路(`generate_key_phrase_component_verified`相当の`ensure_key_phrase_english_component_styled`、`--stage tts --only-segments kp4_english`)で再生成: 新sha256 e440550160713cf8cb80e0b5598393e0bb3148f74c74ff33a5d643943b70466f、1.12秒、`status=OK`、`cache_miss_reason=reuse_value_guard_blocked`(旧entryが再利用されず新規TTS)、K2 primary 1回でOK(retry 0、fallback_used=False、Review Lock `cumulative_tts_attempts=2`[旧1+新1]・RESOLVED、HR queue到達なし)。
- 既存Validator判定: Primary(gpt-4o-mini-transcribe)=「Take part.」NORMALIZED_MATCH PASS、disfluency QA(ローカルfaster-whisper small)転写=「Take  part.」(旧音声は「Take  Tarte.」)。判定基準・閾値の変更なし。
- 観測(Production判定には不使用、`er088_kp_asr_dual_pass_trial_01.py`をenv上書き[ER088_OUT/SRC_WAV/EXPECTED_SHA/N_TRIALS、既定値は従来通り]で再利用、出力`er092_output/kp4_remediation_01/observe/`):

| 音声 | Primary(OpenAI) | Azure(Phrase List空) | Whisper small | 両方PASS必須(force_secondary) |
|---|---|---|---|---|
| 旧 675cd6b1(Trial-01、10回) | 3/10 "part"、他は"Tart"系 | 10/10 "Take Tart" | 10/10 "Take Tarte" | 旧Trial記録: 多数NG |
| 新 e4405501(3回) | 3/3 "Take part." | 3/3 "Take part." | 3/3 "Take  part." | 3/3 PASS(force_secondary_agreed) |

3方式ともに新音声は「take part」側。ただしこれはASR観測であり、**実際の発音の確定ではない**(試聴は人間)。試聴ページ: `user_test/kp4_take_part_compare_01/index.html`(新旧並置)。

## 3. 差し替え結果
- `a2/narration/kp4_en.wav` = 新音声。再assemble(`--level a2 --stage assemble`、Audio Validation Gate/M3通過、`run_summary_assemble.json status=OK`、Std通し 321.85秒[旧322.21])。
- 試聴ページ`user_test/manga_ai_chat_byus_e2e_01/`再生成(`er019_byus_page_01.py`): 変更ファイル=`audio/std_12.mp3`(KP4)・`audio/BYUS_Standard_e2e_01.mp3`(通し)・`audio/std_24.mp3`(Outro、通し尺短縮による切出し位置のずれ)・`index.html`(尺表記)。Adv全mp3・他std mp3はsha不変(git status)。
- sha不変の証拠(runディレクトリ全wav/mp3の前後比較): 変化したのは`a2/assembled/Family_X_Audio_A2_MANGA_AI_CHAT_BYUS.wav`(9d46e7ef…→28752a77…)のみ。Adv(b1b)の全wav/assembled、他KP・Full Story・Supportのwavはsha不変。

## 4. Master Store・正式音声・retry/fallback/resumeの整合
- Store: 同一key(master id `0714639d…`)のentryが新音声で更新(qa_evidence.sha256=e4405501…、asr_text="Take part."、`reuse_blocked`なし、created_at 2026-10-21T20:54:31)。旧entryは再生成のため上書き=旧音声は`_reuse_blocked/`へ退避済み。telemetry: `reuse_blocked_by_value_guard`→`generated`の2イベント。以後のkey A hitは新音声のみを返す。
- 正式音声: results `key_phrases.4.english.sha256`=`narration/kp4_en.wav`の実sha=Store sha=e4405501…(一致)。
- resume/fallback: 同コマンド(`--stage tts --only-segments kp4_english`)を再実行 -> `reused_from_previous_run=True`、`raw_usage_log.jsonl`行数122->122(API 0)、sha不変。fallback(key B ENGLISH_LOCK)は今回未使用(K2 primary 1回でOK)。4試行構成(Minimal2+Lock2)・Review Lock会計に変更なし。

## 5. runtime evidence / Regression / 費用
- Regression: `er006_master_audio_store_01_test.py` 7 / `er078_asr_unified_wiring_06c_test_01.py` 44(`test_c_master_audio_store_honours_reuse_blocked_mark`を含む) / `er019_family_x_kp_structure_wiring_01_test_01.py` 36 / `er019_family_x_fx_20261016_wiring_01_test_01.py` 72(K2 store) 全PASS。`tools/stop_scope_check_01.py` rc=0(stop=false)、作業開始時・終了時。
- 費用: 再生成=Gemini TTS Batch 1回 cost_jpy 0.016(`raw_usage_log.jsonl`)+OpenAI ASR 1回(55in/5out token、約0.01円)+ローカルWhisper 0円。観測3回のAPI推定0.31円(`observe/timing.json` est_jpy_api)。合計約0.4円(Guardrail JPY30以内)。注意: TTS実行モードは環境変数未設定のrunner既定でBATCHだった(委任文はSTANDARD指定。同一モデル・同一Prompt・費用はBatchの方が低く、品質への影響なし。所要133秒)。
- 追加ファイル: `er092_kp4_remediation_01.py`(無効化script)、`er088_kp_asr_dual_pass_trial_01.py`(env上書きのみ追加、既定値不変)。

## 6. 完了Statusと未処理事項
- 技術的には、問題音声の無効化・再生成・既存QA通過・差替え・整合・Regression完了。ASR 3方式の観測は全て新音声で「take part」側。**ユーザーによる発音の最終試聴確認は未**(記事全体の最終試聴PASSとも別)。PRODUCTION_WIRED可否の最終判定はFable。
- 残り: Store内EN 333件中29件(8.7%)の「Primary PASS×ローカルWhisper不一致」は本件の対象外(Task B/ユーザー判断)。Task B(新ASR構成)は未採用でProduction変更なし。
