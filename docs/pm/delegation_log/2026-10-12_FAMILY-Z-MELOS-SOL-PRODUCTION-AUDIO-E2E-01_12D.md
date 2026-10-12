# FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01 委任_12D 結果 (2026-10-12)
Status: tts_a2はclip失敗STOP(rc=2、起動1回、再起動なし)。HR試聴ページ作成済み。PRODUCTION_WIRED未達。HR採択・override・regenerate未実施(ユーザー試聴後)。
起動前確認: run_e2e_02/STOP・STOP_ALLなし(旧STOP_NOTICEはローカル記録として12Bと同扱い)、Z process無し。

## 1. gate修正(¥0)
- er063 `assert_tts_results_complete`: `local_rewrite_revalidation.verdict != "PASS"` による `LOCAL_REWRITE_NOT_REVALIDATED` 不採択を撤去。audio_text_deviation有りclipは採択し、`audio_text_deviations`(clip_id/before/after/diff_summary/verdict)を返し、`run_audio_gate`のgate_result_*.jsonにも記録。非OK clipは従来どおり不採択。
- test: er063 `test_m2_gate_passes_local_rewrite_not_required_and_lists_deviation` 追加。er063 47件OK、er026統合42件OK、er026 runner 21件OK、er062 64件OK(Comment3 test更新含む)。er026_family_z_stop_sentinel_test 16件中1件が実行ごとに別testで失敗(subprocess出力のcp932 decode/空stdout。gate/Comment3コード非関連、環境依存と判断。12A時は16PASS=要再確認)。

## 2. Std Comment3
- 規則: `limit_comment3_part` = Part3先頭25%(最低2段落)+到着・結末マーカー(arriv/reached the/city gate/square/sword/I'm back/fell against/held each other/embrac/forg/free both)該当段落以降を含めない(最低1段落)。両レベル共通、Z所有。
- 旧: メロスは、鎖に差し出された友の手を思い出します。友は約束を求めず、メロスを信じていました。岩の割れ目から水を飲んで立ち上がり、門で友の死を告げる鐘が鳴ると、剣が頭上に掲げられた友のもとへ走って戻ったと叫びます。
- 新(attempt1、lint違反0、1回で完了): メロスは、鎖を受け入れるために差し出された友人の手を思い出します。友人は、もう一度約束を求めずに彼を信じていました。岩の割れ目から水が少しずつ流れ、メロスはそれを飲んで立ち上がり、一歩ずつ進みます。
- 到着・再会・王の改心に言及なし。Preview/Comment1/2は逐語で再利用(同一確認済み)。B1 Comment3は現行維持(規則施行前生成)。

## 3. tts_a2結果(起動1回 18:22-19:11、rc=2)
- 39 clip(KP含む): OK 35 / 非OK(STOPPED, z_adoption=failed)4。attempt分布: 1回35 / 2回3 / 3回1。Std cooldown(600s)発火1回(part1_c5)。LR(audio_text_deviation)発火: a2は0件(b1bのpart3_c1のみ)。
- 非OK clip:
  - a2 comment_1(JA): ASR TRUE_CONTENT_MISMATCH x3(『メロス→メオス』、『三日間→3日間』等の表記差)
  - a2 full_story_part1_c1『Melos called across the hall,』: ASR "Mello's called across the hall."(固有名詞のみ)、TTS3回
  - a2 full_story_part1_c5『Melos said.』: ASR "Mello said."/Azure "Mellow said."(固有名詞のみ)、HR queue 18:35:29、fallback(gemini-2.5-pro-preview-tts)も同ASR
  - a2 full_story_part3_c3『His friend turned around, and Melos fell against him.』: ASR "...and mellows fell against him."(固有名詞のみ)
- model_id実測: narrator/comment/preview/KP/topic_intro/title=gemini-3.8-flash-lite-tts、dialogue 10clip=gemini-2.5-pro-preview-tts(OPEN-307)。
- 備考: tts_a2の4 clipはstage_tts仕様により停止。残stageは未実行。

## 4. HR試聴ページ
- URL: https://shimomura055.github.io/eigo-radio/user_test/family_z_melos_01/hr_review_01.html (掲載6 clip: b1b part1_c5[HR] / b1b part3_c1[LR逸脱 Melos->He] / a2 comment_1 / part1_c1 / part1_c5 / part3_c3)
- 生成: tools/build_family_z_hr_review_page.py(API0)。公開後のHTTP 200/mp3再生検証結果は末尾参照。

## 5. 費用
- run_e2e_02 実費JPY61.08(openai 23.25/gemini 22.33/asr 4.81/azure 10.69)。合算 約169.2/300(警告92/200未到達)。台帳: er026_output/family_z_production_e2e_01/melos/COST_LEDGER_MELOS_01.md 4節。

## 6. 残stage実行コマンド案(HR採択後。実行は別委任)
- HR採択: er003_v1_n3_01_assemble.record_human_approval(out_dir=.../run_e2e_02/<level>, segment_key=<clip>, canonical_text=..., approved_by=user)(試聴後のみ)。b1b/a2とも採択後はtts stageを再実行せず後続から:
- `.venv/Scripts/python.exe er026_family_z_fiction_production_runner_01.py --mode real --stage provision_shell --run run_e2e_02 --approved-budget-jpy 191.9 --warn-threshold-jpy 92 --ack-warn-threshold` -> `--stage gate` -> `--stage assemble` -> `--stage pages` -> `--stage page_verify`(各1回)。
- clipを再生成する場合は `--stage tts_a2 --only-clips <clip>`(review lock approve_regenerate必要、Std cooldown 10分、1 clip約JPY1-2)。JA comment_1のASR数値表記(三日間/3日間)はOPEN-308関連の別論点として判断要。

## 証跡
er026_output/family_z_production_e2e_01/melos/run_e2e_02/、同evidence_12D/(support_regen_stdout.log、tts_a2_stdout.log)、user_test/family_z_melos_01/
