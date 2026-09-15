# 委任文 — USER-TEST-AUDIO-HUMAN-REVIEW-FIX-02-FAMILYC

## 管理ID

USER-TEST-AUDIO-HUMAN-REVIEW-FIX-02-FAMILYC(Family C / Home robots 修正版episode v2)
並行タスク衝突確認: 並行してTrend A2(`er014_output/.../trend/`)、Discovery
(`.../discovery/`)、Voices(`.../voices/`、er012_*)が走る。本タスクは
`er013_output/family_c_episode_trial_09/`配下(新規`home_robots_v2/`)と
新規`er013_family_c_episode_trial_09b_run.py`/
`er013_family_c_episode_trial_09b_test_01.py`のみを書く。Trial-09 v1成果物
(`home_robots/`)は無変更で保持。Git・SSOT・ACTIVE_TASK・RESULT_PACKET.mdを
触らない。共有資産(master audio store等)への書き込みは既存経路が自動で
行う分のみ。RESULT_PACKETは`docs/pm/RESULT_PACKET_FIX02_FAMILYC.md`(新規)。

## 性質/到達上限/Status/禁止事項

- 性質: Trial(Family C)。ユーザー試聴評価: Story本文は良好、episodeとしては
  未完成(Intro/Outro/Title読み上げ不足、効果音不足、Key Phrase表示文と
  音声の不一致、Comment不足・表示と音声不一致、母親発話がnarrator音声の
  まま、Family A相当の体裁不足)。現Trial-09をそのまま完成episodeとして
  VALIDATED扱いしない。修正版v2を作成し再試聴へ回す。最大Status:
  VALIDATED。Production採用禁止。B1/B2は生成しない(A2相当1レベルのみ)。
- Story本文は不変(reader_facing_article.txt)。article_normalized.txtが
  v1と同一であることをsha256で確認・記録。
- 1-1 Intro/Outro/Title/Pause/効果音: Family A正式Production episode構成を
  可能な限りそのまま流用。新しいFamily C専用演出・新規SFX設計は禁止。
  流用元をfamily_a_reuse_map.mdに記録。
- 1-2 Key Phrase音声整合: 表示文/canonical/TTS input/実音声ASRの4者を
  全5件再照合。本文は変更しない、既存TTS normalizationのみで一致させる。
- 1-3 Voice構成(3役): Narrator(Aoede)/Robot(Charon)/Motherを最低限分離。
  Motherは既存4Voice Trialの女性系Voice。Mayaの分離は任意判断。
- 1-4/1-5 Comment 4件: C1=導入部、C2=story_009/010間、C3=story_017/018間、
  C4=Story終了後。設計原則(説明しすぎない/ネタバレしすぎない/研究記事化
  しない/理解補助/流れを壊さない)。
- 1-6 Assembly: 既存assemble_with_timeline/apply_headroom_safety_valve/
  verify_episode_audio_validation_gateを再利用。Audio Validation→
  article/audio consistency→player/display/audio consistency→mp3化→
  標準player再生成。
- なぜv1が完成と報告できたか原因分析必須。新Validatorは追加しない。
- 費用上限: 90円。
- 禁止: Story本文変更/Key Phrase本文変更/新規SFX・演出設計/新Voice探索/
  B1・B2生成/Production(er003/er006/er011/er012)コード変更/Gate緩和/
  approve_regenerate()呼び出し/Git commit・push/.gitignore変更/
  pip install/run_project_regression.pyへ_testを含まないglob/PATH上の
  素python。
- STOP条件: Family A構成流用に新Production仕様が必要/Gate緩和が必要/
  Story本文変更が必要/費用上限超過見込み/技術的にWeb配信不可。

## 固定ブロック

E-1/D-1/G-1/F-1/T-0/T-1(通常運用のとおり)。T-0: 委任文を
docs/pm/delegation_log/<管理ID>.mdへ保存しcheck_delegation_prompt.pyを実行、
結果をRESULT_PACKETへ記録。

## 事前指定Read一覧(7項目)

1. RESULT_PACKET_FC9.md全文、episode_spec.md全文
2. er013_family_c_episode_trial_09_run.py全文
3. home_robots/{segments.json,keywords_canonicalized.json,
   audio_validation.json,support_ja.md,preview.txt}全文、
   audit/tts_generation_results.jsonをgrep
4. Family A正式構成(CURRENT_SPEC.md grep、er003_v1_n3_01_assemble.py grep、
   er003_b1_p9a_audio.py grep、er011_output完成episode実例Glob)
5. 4Voice Trial(er012_*.py/er003_*.py grep)
6. audio_review_player.py grep
7. er003_v1_iran01_a2_generate.py grep(run_support_text)

## 事前指定Grep一覧+追記位置・更新位置の手順

- 出力: `er013_output/family_c_episode_trial_09/home_robots_v2/{article_normalized.txt,
  family_a_reuse_map.md, speaker_map.json, key_phrase_consistency.json,
  comments_ja.md, comment_placement.json, comment_consistency.json,
  segments.json, audio/, assembled/, audio_validation.json,
  article_audio_consistency.json, player_display_audio_consistency.json,
  player.html, web/*.mp3, web/segments/*.mp3, web_delivery.json,
  cost_summary.json, raw_usage_log.jsonl}`、`spec/episode_spec_v2.md`
  (v1との差分のみ)。新規`er013_family_c_episode_trial_09b_run.py`、
  `er013_family_c_episode_trial_09b_test_01.py`。
- Grepパターン(4Voice Trial): `4v|four_voice|4voice|voice_d|Kore|Leda|
  Zephyr|female` in `er012_*.py`・`er003_*.py`(ルート直下)。
- Grepパターン(Family A構成): CURRENT_SPEC.md `Intro|Outro|SFX|jingle|
  効果音|pause|間|Topic intro|Title読み|セクションタイトル|A2.*構成|
  B1.*構成`。er003_v1_n3_01_assemble.py `^def |sfx|SFX|jingle|intro|outro|
  pause|silence|A2_SHARED|B1_SHARED|timeline`。er003_b1_p9a_audio.py
  `^def |sfx|SFX|jingle|pause`。
- 追記位置: RESULT_PACKET_FIX02_FAMILYC.mdの新規作成のみ(既存SSOTへの
  追記は行わない、本タスクではSSOT編集自体を行わない)。

## 実行コマンド全文

(すべて `C:\Users\tensh\eigo-radio` で実行)

1. `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\USER-TEST-AUDIO-HUMAN-REVIEW-FIX-02-FAMILYC.md --json-out docs\pm\delegation_log\USER-TEST-AUDIO-HUMAN-REVIEW-FIX-02-FAMILYC_check.json`
2. `.venv\Scripts\python.exe er013_family_c_episode_trial_09b_run.py --budget-jpy 90`
3. `.venv\Scripts\python.exe run_project_regression.py --pattern "er013_family_c_episode_trial_09*_test_*.py"`
4. `Select-String -Path er013_output\family_c_episode_trial_09\home_robots_v2\player.html -Pattern "file:///|C:\\" | Measure-Object -Line`
5. `git check-ignore -v er013_output/family_c_episode_trial_09/home_robots_v2/web/episode.mp3`

## 報告

docs/pm/RESULT_PACKET_FIX02_FAMILYC.mdへ16項目(Status/Family A流用表/
Key Phrase4者照合表/Voice構成/Comment照合表/Assembly順序/Audio
Validation結果/consistency結果/本文不変sha256/duration・mp3一覧/なぜv1が
完成と報告できたか/費用/model_id/Open Item候補/commit候補一覧/T-0結果)。
