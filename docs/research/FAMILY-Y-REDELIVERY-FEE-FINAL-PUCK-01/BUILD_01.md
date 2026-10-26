# BUILD_01 — 完成版の組立・公開手順(委任_02)
## 1. run dirの選択: 選択肢A(`run_voice_puck_ev_01`をそのまま完成版runとして採用)
run dir: `er121_output/family_y_production_01/redelivery_fee/run_voice_puck_ev_01`(以下ev run)。選択肢B(run_01 in-place)は不要。Aの整合確認(a)〜(h)を全て満たしたため。
| 項目 | 結果 | 根拠 |
|---|---|---|
| (a) inputs同一 | OK | scratch比較(非wav・非log): `text`20/`translate`2/`support`2/`key_phrases`48/`study_text`9/`a2,b1b/key_phrases`/`kp_review_mode.json`/`study_text_slots.json`がrun_01とsha一致。差分は`voice_assignment.json`(voice_1 Algieba→Puck)のみ。evidence_01.json `inputs_identical_counts`/`inputs_diffs` |
| (b) KP宣言scope | OK | `kp_review_mode.json`の`scope.run`はrun_01絶対path(ev runでは不一致)。ただし宣言の読取は`er119_kp_human_review_01.py:1315 ensure_kp_review`(kp stage)のみ。gate/assemble/pages/page_verifyは`er121_family_y_runner_01.py:908 _assert_study_ready`(確定済みfinalの存在・最新性照合)で、実際にgate/assemble/pages/page_verifyが全てPASSで完走(rc=0) |
| (c) HR確定内容 | OK | KP/study_text/support/kp_review_modeがrun_01とsha一致。a2 preview承認(`human_approved_segments.json`の`preview`)はrun_01と等価、y_voice_1承認は複製せず(Puck新音声はstatus=OK) |
| (d) Adv timeline | OK | `b1b/audit/timeline.json` 43要素、`comment_2` 0件、`removed_by_spec.b1b.comment_2` |
| (e) actual voice | OK | a2/b1b y_voice_1=Puck(`voice`/`y_tts_voice_requested`)、y_voice_2=Zephyr、y_voice_3=Schedar |
| (f) hr_adopt_prep | OK | ev runに`hr_adopt_prep`無し。公開ページに`v1cand`/`Algieba` 0件 |
| (g) Std減速 | OK | a2の`slowdown_applied=True`が8本(y_lead/y_intro_1-3/y_voice_1-3/y_closing) |
| (h) Chunk不発火 | OK | `a2/audit/chunk_plan_a2.json`に`"chunked": true` 0件(`paragraphs=1<2`)、results内chunk key 0 |
run_01と旧公開`user_test/family_y_production_redelivery_fee_01/`は無変更(git status空)。※`run_01/pages/audio/`のuntracked表示は本委任前からの既存。
## 2. 起動表(環境`TTS_EXECUTION_MODE=STANDARD`、共通引数`--mode real --slug redelivery_fee --run run_voice_puck_ev_01 --theme-package docs/research/FAMILY-Y-VOICES-DESIGN-01/OPINION_BASED_02/THEME_DATA_02.json --reuse-manifest docs/research/FAMILY-Y-PRODUCTION-LAUNCH-01/theme_packages/redelivery_fee_reuse_01.json --approved-budget-jpy 30 --tts-execution-mode STANDARD`)
| 起動 | 開始(JST) | 間隔 | stage引数 | rc | API |
|---|---|---|---|---|---|
| STOP確認 | 17:5x | - | `stop_scope_check_01`(`stop_check_02.json`) | 0(非停止) | 0 |
| L1 | 17:57:10 | (前回17:36:26から約21分) | `--stages gate,assemble,pages,page_verify` | 0 | 0(spent 2.511不変) |
| L2(再起動確認) | 18:00:11 | 181秒 | `--stages tts_b1b,tts_a2,gate,assemble,pages,page_verify --only-segments y_voice_1` | 0 | 0(cost_log 5行不変、wav sha不変) |
ログ: ev run `console_launch7.log`/`console_launch8.log`(追跡対象外)。5分内3起動なし。
## 3. 公開
runnerのpages出力先は`<run>/pages`固定(`er121_family_y_runner_01.py:160-172`)。`pages/`(index.html+audio 52 mp3)を`user_test/family_y_production_redelivery_fee_02/`へ複製(diff -rq差分なし)。旧`_01`は保持。listening/(Algieba候補)は含まない。
URL: https://shimomura055.github.io/eigo-radio/user_test/family_y_production_redelivery_fee_02/index.html
## 4. 旧版との差(ページ本文の機械diff)
Voice 1の台本は不変。差分は秒数表記(Std 347→342秒、Adv 321→316秒)、Chunk注記の文言、停止マーカー位置(Puck音声の実測)、Adv Comment 2の行の消滅、Voice 1聴き比べ(Algieba候補)節の消滅のみ。
