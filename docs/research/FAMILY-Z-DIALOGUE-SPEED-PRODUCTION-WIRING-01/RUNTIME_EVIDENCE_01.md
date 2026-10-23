# RUNTIME_EVIDENCE_01: Family Z 会話速度仕様v2 Production Wiring(FAMILY-Z-DIALOGUE-SPEED-PRODUCTION-WIRING-01 委任_01、2026-10-23)

Status: WIRED_PENDING_FABLE(コード配線・test・既存2作品4組の正式経路再処理・公開差替え・実再生まで完了。`PRODUCTION_WIRED`はFable受入後)。
ユーザー原文=`docs/pm/delegation_log/2026-10-23_FAMILY-Z-DIALOGUE-SPEED-PRODUCTION-WIRING-01_USER.md`(4組Trial B採用=APPROVED_FOR_PRODUCTION、OPEN-462/UDR #159判断済み)。

## 1. 速度仕様v2(level×kind)と実装(Family Zのみ)
| level | kind | 速度処理 | speed_profile | 実装 |
|---|---|---|---|---|
| Std(a2) | Narrator | 6%減速(従来) | `std_narrator_slow6` | `n3_tts.generate_a2_segment_with_slowdown`(無変更) |
| Std(a2) | Dialogue | **なし(旧6%減速を撤去)** | `std_dialogue_none` | `er063_family_z_audio_01.py:852-853`(plain `generate_voice_body_wide_margin`) |
| Adv(b1b) | Narrator | なし(従来) | `adv_narrator_none` | `news_tail_fix.generate_news_narration_wide_margin`(無変更) |
| Adv(b1b) | Dialogue | **生成後約6%高速化(atempo=1.06)** | `adv_dialogue_fast6` | `er063:842-851` -> `n3_tts.generate_with_a2_slowdown_outer_loop(slowdown_pct=-5.660377)` -> `apply_a2_slowdown_postprocess(slowdown_pct=)` -> `er008.apply_a2_slowdown`(Trial Bと同一関数・係数) |

- 表の定義=`er063:56-70`(`Z_SPEED_PROFILE_VERSION=z_speed_v2`、`speed_profile_name`)。共有`er003_v1_n3_01_tts_generate.py`の変更は`slowdown_pct`のoptional引数追加のみ(:196/:225-228/:435/:460)。未指定(X/A/B/C)は従来と同一の呼出(`apply_a2_slowdown(original,out)`、test `OuterLoopPassThroughTest`で固定)。
- clip記録: `build_entry`が`speed_profile`(version/profile/applied/tempo/pct/original_sha256/source)を`tts_generation_results`へ記録(`er063:998 build_speed_profile_record`)。二重適用防止: 後処理は常に`_original.wav`退避→原音から1回(`apply_a2_slowdown_postprocess`の既存設計)、移行は`_original.wav`が残っていれば原音へ戻してから適用。
- Store/再利用key: **方式=keyにversionを含める**(原音統一+再適用方式は後処理の位置・保存形態を変えるため採らない=設計停止条件の回避)。会話clipの`reuse_key`へ`speed_profile=z_speed_v2:<profile>`を追加(`er063:726-738`)。Narrator/Preview/KP等のkeyは不変。旧仕様(減速済みStd会話・未処理Adv会話)の保存音声はkey不一致で再利用されない(`prune_cached_to_plan`・`generate_or_reuse_z`、test `test_legacy_dialogue_entry_is_not_reused_as_new_spec`)。
- 旧entryの移行(TTS再生成0): `migrate_legacy_dialogue_speed`(`er063:1234`、`run_tts_stage`の前処理=1326)。Std=退避済み`_original.wav`へ戻す(旧減速wavは`audit/legacy_speed_backup/`へ退避、ASR呼出0)/Adv=原音へ正式後処理(統一judge ASR再検証)を1回適用、NGは原音へ戻して再生成経路へ。
- Gate整理: `verify_z_speed_profile`(`er063:1546`)を`run_audio_gate`に追加=Std会話の減速残存・Adv会話の高速化漏れ/二重適用(wav/original長さ比0.93〜0.96)・Adv Narratorへの誤処理をSTOP。`verify_std_english_slowdown`はStd Narratorのみに限定(:1523)。共有assemble:273の`A2_SLOWDOWN_TARGET_SEGMENTS`はZのclip id(`full_story_partN_cK`)に一致せずZ非影響・無変更。`FAMILY_Z_ROLE_STYLE`の`DIALOGUE_STD.style_label`(歴史的名称`+post6%`)は、run単位Style記録のRECORD_MISMATCH(既存run・進行中runのSTOP)を避けるため不変とし、理由をコードコメントに記録。
- runner: `--stages a,b,c`(E2E順に正規化、`--stage`併用不可)を追加。既存run後段だけを1起動で再実行(5分3起動のRESTART_STORMを避ける)。

## 2. 正式経路での実動作(既存2作品、TTS再生成はKP1英語1件のみ=既存Gate起因、下記注)
実行コマンド(Production runner正式経路、`--mode real`): `er026_family_z_fiction_production_runner_01.py --story <melos|the_open_window> --run <run_e2e_06|run_e2e_01> --mode real --stages tts_b1b,tts_a2,provision_shell,gate,assemble --approved-budget-jpy <100|120>`、続けて`--stages pages,page_verify`。ログ=`er026_output/family_z_dialogue_speed_wiring_01/{melos,open_window}_run_01.log`・`*_pages_01.log`。元runの旧成果物は`<run>/STALE_speed_v1_20261023/`(assembly・results・gate・page_verify)、旧公開ページは`er026_output/family_z_production_e2e_01/_pages_backup_speed_v1_20261023/`へ退避(削除なし)。

| 作品×level | 会話clip: 新wav==Trial B wav(sha) | Narrator/Preview/Comment/shell: 旧wavとsha一致 | 通しwav(組立)==Trial B通しwav(sha) | 通し長さ 旧->新 |
|---|---|---|---|---|
| メロス Std | 10/10 | 28/28 | **一致** | 303.923 -> 301.925 s |
| メロス Adv | 11/11 | 28/28 | 不一致(下記KP1) | 294.780 -> 293.083 s |
| 開いた窓 Std | 18/18 | 29/29 | **一致** | 325.307 -> 319.749 s |
| 開いた窓 Adv | 18/18 | 28/28 | **一致** | 298.824 -> 293.701 s |

- 会話clipの長さ比(Adv): メロス0.9442〜0.9515、開いた窓0.9434〜0.9521(Trial B 0.943±0.01範囲内)。Std会話=原音そのもの(wav sha==`_original.wav` sha)。
- 注(非対象の変動1件、既存Gate起因): メロスAdvのKP1英語`sentence someone to death`のみ、再利用時に既存のKP3V reuse gate(`kp_vote_reuse_ok` S1、`s1_vote_ng:NG_BOTH`、fail-closed)が旧clipを不合格とし、同gateの正規retry(TTS 2回、`PASS_DUAL`)で再生成された。KP1の長さ1.88s->1.96s(+0.08s、通しに2か所で計+0.16s)。これが「メロスAdv通しwavがTrial Bと不一致」の唯一の原因。他のKP(メロスStd・開いた窓Std/Adv、メロスAdvのKP2-5)はsha不変。Gate・retry上限は迂回していない。
- 速度後のASR: **Adv会話29clip全て正式経路の統一judgeで再検証**(Primary=OpenAI。メロス11/11 `PASS(primary_pass)`、開いた窓17 `PASS`+1 `PASS_WITH_WARNING(secondary_confirmed)`=`full_story_part3_c4`、Trialのローカルwhisperでも同clipが警告対象で劣化ではない)。判定recordの`audio_sha256`==新wav sha(全clip)。詳細=`er026_output/family_z_dialogue_speed_wiring_01/adv_post_speed_asr_01.json`。Std会話は音声が原音と同一(sha一致)のため再検査不要(原音は生成時にASR検証済み、Trial Bの`asr_qa_B.json`と同一音声)。
- gate: 4組とも`gate_result_04C.json`の`shared_gate=PASS`、`z_speed_profile`=全story clip ok。比較JSON=`er026_output/family_z_dialogue_speed_wiring_01/compare_{melos,open_window}.json`。
- 組立後QA(`qa_assembled_01.json`): 4本ともclip 0・NaNなし・peak<=0.98・最長無音<=1.58s・sequence_orderが旧と一致(メロスStd 43/Adv 44、開いた窓Std 52/Adv 51 piece)。

## 3. 新規生成経路(first-production path)の実動作
`--mode real --stages tts_b1b,tts_a2 --only-clips full_story_part1_c4`を新規run(`melos/run_dsw_evidence_01`)で実行(費用0.67円、ログ=`gen_path_evidence_01.log`)。
- Std会話(Algieba): TTS 1回、`slowdown_applied=None`、`speed_profile=std_dialogue_none/applied=False`、`_original.wav`なし、reuse_keyに`z_speed_v2:std_dialogue_none`。
- Adv会話(Algieba): TTS 1回、ASR 2回(生成時+高速化後)、`slowdown_applied=True`、`speed_profile=adv_dialogue_fast6/tempo=1.06/source=generated`、wav/original長さ比0.9485(2.2488s/2.3710s)、reuse_keyに`z_speed_v2:adv_dialogue_fast6`。

## 4. test・回帰
- 新規`er063_family_z_speed_v2_test_01.py` 24件(level×kind表、Trial Bと同一pct、実ffmpegで長さ比、X既定呼出がpct引数なし・6%と同一byte、reuse_key、旧entry非再利用、generator配線[Std=plain/Adv=outer loop+pct]、Gate違反検知[Std減速残存・Adv未処理/二重適用・Adv Narrator誤処理]、run_tts_stageのspeed_profile記録・resume再生成0、Std/Adv移行[idempotent・中断復帰で二重適用なし・ASR NG時は原音復元]、`--stages`)。意図的に更新した既存test期待値(旧仕様をassertしていたもの): er063_family_z_audio_01_test_01(Std会話の6%減速post処理/Adv fakeの高速化)・er026_family_z_e2e_integration_test_01(Std会話の`slowdown_applied`)。
- `run_project_regression.py`(単独実行)・pytest系は`REGRESSION_*`欄(本ファイル末尾で確定値を追記)。

## 5. 費用
前述の正式経路再処理(メロス+開いた窓)=cost_log差分で約1.62円(メロス1.107円[ASR 13+Azure 12、KP1 TTS 2回含む]+開いた窓0.512円[ASR 18+Azure 1])、新規生成経路evidence=0.668円。合計約2.3円(出典=runnerの`spent_jpy`差分: メロス27.576->28.683、開いた窓71.021->71.533、dsw_evidence 0->0.668)。TTS再生成=KP1英語2call(既存gate起因)+evidence 2call(新規run)。追加の速度探索Trialなし。

## 6. 非変更の確認
Voice割当・Prompt・Style・台詞・本文・順序・効果音/BGM: 上記sha一致(Narrator等28/28、29/29、28/28)、sequence_order一致。『開いた窓』の本文・台詞は未変更(作品全体は`USER_LISTENING_PENDING`+原作忠実性[OPEN-465]未解決のまま、CLOSEDにしない)。

## 7. 回帰結果(確定値、commit b3defe8f8時点・単独実行)
- `run_project_regression.py`: collected=6925 passed=6915 failed=0 errors=0 skipped=10(`regression_summary_01.json`)。経過: 初回(速度仕様実装直後)はX共有関数への誤kwarg混入を検出して11 error(er026/er058、`generate_a2_segment_with_slowdown`へ誤って`slowdown_pct`を渡していた=修正済み)、2回目はコメント編集が未commitでtracked-diff guard 1 fail、3回目で0/0。
- pytest系別枠(er078*/er103/er104*/er105/er106/er108/er109): 984 passed, 0 failed(初回3 failedは旧仕様期待値[er078 wiring_05のStd/Adv会話入替]と、速度配線で実体が変わった旧fixture run[er106 legacy run_e2e_06→未再処理run_e2e_05]の意図的更新)。
