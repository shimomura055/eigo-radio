# RESULT_PACKET — EDITORIAL-FUTURE-FAMILY-C-HOME-ROBOTS-EPISODE-SPEC-TRIAL-09

Status: **VALIDATED**(Trial、Production採用・配線は行っていない)
Gate 1分類: 完成episode候補として成立(音声Validation Gate PASS、ユーザー試聴待ち)

## 1) 採用した完成episode構造(segment一覧)

topic_intro_en → topic_intro_ja → preview_ja → key_phrase_1〜5 →
story(段落0〜9、支流入り) → support_1_ja → story(段落10〜33) →
support_2_ja。詳細は9)参照。A-Family Point One/Two構造は不使用、
ひと続きのStoryとして音声segmentのみ分割。

## 2) 既存A/B仕様から再利用したもの

`generate_narration_snippet_verified_strict`(narrator TTS、EN/JA共通)、
`generate_charon_english`(robot voice)、`generate_key_phrase_component_verified`
(Key Phrase英語、Primary+Fallback retry構成)、`run_key_phrases`(選定→
canonicalization→redundancy QA)、`japanese_gloss_tts`分離仕様、
`compute_gain_for_target_rms`/`mono_24k_to_stereo_target`/`silence_stereo`/
`build_key_phrase_block`(音量・音声組立primitive)、
`assemble_with_timeline`/`apply_headroom_safety_valve`/
`verify_episode_audio_validation_gate`(Assembly・Gate)、
`audio_review_player.py`(標準player、PM-GOVERNANCE-AUDIO-REVIEW-PLAYER-
STANDARD-FORMAT-11準拠)、B1/A2共有Charon番号読み上げ資産
(`num_one_charon.wav`〜`num_five_charon.wav`、runtime実測を受けて追加採用)。

## 3) Family C専用で新規に必要だったもの(Trial専用実装)

(1) 記事からsegmentを構築するorchestration(`er013_family_c_episode_trial_09_run.py`、
Family C固有の物理構造のため)、(2) 引用符検出による2-voice分割ロジック、
(3) Preview/Support 1・2のrole instruction文言、(4) TTS-safe時刻表記変換
(`tts_safe_time_reading_en`、"7:00"→"seven"、runtime実測で発見した問題への対応)。

## 4) Preview完成文

「暮らしの多くを整えてくれる家のロボットと暮らすマヤは、毎日を楽に過ごしています。
けれど、母親とのこれからを考える中で、自分で選ぶことの意味を、じっくり考える
ことになります。」(2文・約95字、結末・中心の問いの答えは明かさない)

## 5) Key Phrase完成候補(英/日本語gloss/位置)

| Rank | 英語(used_form) | 日本語gloss | 音声内位置(開始秒) |
|---|---|---|---|
| 1 | preference | 本人の希望 | 20.84s |
| 2 | belong to someone | その人自身のものである | 28.58s |
| 3 | comfort | 楽で心地よいこと | 36.50s |
| 4 | care house | 介護施設 | 44.29s |
| 5 | awake | 自分の意志に目覚めている | 52.70s |

選定はStrategy L+Canonicalization+Redundancy QA(既存関数)を実際にHome
robots記事へ適用した結果(REDUNDANCY_PASS)。

## 6) 日本語support完成文

- Support 1(段落9→10の間、転換点直前): 「けれど、ある夜、マヤはロボットにも
  簡単には決められない問いに、初めて向き合うことになります。」
- Support 2(物語終了直後): 「あなたなら、何も決めなくてよい毎日と、自分で
  迷って選ぶ毎日のどちらを選びますか。」(結論を言い換えない問いかけ型)

## 7) Voice・TTS方式(比較表+採用理由)

episode_spec.md 6節に4候補比較表あり。採用: **2-voice(narrator=Aoede、
robotの直接発話のみCharon)**。ロボット発話は本文中わずか6箇所+UI 1箇所
のみで、物語後半で沈黙していく展開と声の使用頻度が自然に一致する
(Core Provocation[便利さが人間から選択を奪う]と結びついた最小差別化)。
番号読み上げのみ、runtime実測(後述10・15)を受けてCharon共有資産へ変更。

## 8) UI表示文の読み上げ方法(比較+採用)

candidateは episode_spec.md 7節参照。採用: **robot/system voice(Charon)
がそのまま読む**(意味の省略なし、`**`記号のみ除去)。

## 9) segment一覧(実測タイムライン、開始秒)

topic_intro_en(0.0s)/topic_intro_ja(2.25s)/preview_ja(4.59s)/
key_phrase_1〜5(20.84〜59.5s)/story_001〜009(60.13〜124.4s、段落0〜9)/
support_1_ja(125.47s)/story_010〜018(133.79〜247.2s、段落10〜33)/
support_2_ja(249.23s)。全体尺257.82秒(4分18秒)。詳細行数・段落対応は
`segments.json`参照。

## 10) player・audioの相対パス

- player: `er013_output/family_c_episode_trial_09/home_robots/player.html`
- 完成episode音声: `er013_output/family_c_episode_trial_09/home_robots/assembled/family_c_home_robots_trial_09.wav`(48MB)
- 個別音声(38件): `er013_output/family_c_episode_trial_09/home_robots/audio/`(11MB)
- 仕様書: `er013_output/family_c_episode_trial_09/spec/episode_spec.md`

commit後にFableがGitHub raw URLを付与する想定(本タスクではGit操作を行っていない)。

## 11) A2・B1提案(現在の契約の事実+QCD表)

事実: Home robots記事はA2レベルのみで生成済み(`er013_family_c_future_writer_08.py`
prompt本文で確認)。語数実測429語(許容300〜420語を超過、Trial-08時点の
既知事実、本タスクでは未修正)。QCD表はepisode_spec.md 9節参照。
**提案(USER_DECISION_REQUIRED)**: まずA2 1レベルで3本(Home robots/
The future of memory/Digital twins of ourselves)を揃えユーザー検証を
優先し、B1追加要否はその後判断する(B1追加はWriter新規手順を要し、
本タスクの「Writer改善禁止」範囲と抵触しうるため)。

## 12) Fact Safety構成

CURRENT FACT 0件を維持(記事本文は無変更)。本Trialが新規生成した
Preview/Key Phrase gloss/Support 1・2はいずれも「新しい設定・事実を
追加しない」役割指示を明記。既存3層Fact Safety・Fact Checker・Ledger
Deviation CheckerはFamily Cフィクションに元々Verified Fact Ledgerが
存在しないため本Trialでは呼び出していない(Production変更なし、
不要なCheckerを新規に追加呼び出しもしていない)。詳細episode_spec.md 10節。

## 13) 開発・Trial費(API別+5区分、TTS分離)

実測合計(推定合算、方法論は14)参照): **¥96.30**(上限¥133.99以内、
目安¥80は超過=想定超過理由はKey Phrase選定の構造的再試行4回+TTS/ASR
問題2種の発見・修正のための追加試行、いずれもデバッグ起因)。

| 区分 | 推定額 |
|---|---|
| Key Phrase選定パイプライン(LLM: 選定/canonicalization/redundancy QA、6回中4回目で成功) | ¥41.40 |
| 物語本文TTS(narrator 18件、"7:00"読み修正の再試行3回分を含む) | ¥18.90 |
| Preview/Support LLM生成(3件) | ¥14.40 |
| Key Phrase英語Component TTS(5件) | ¥5.40 |
| topic_intro/preview/support TTS(5件) | ¥4.50 |
| Key Phrase日本語gloss TTS(5件) | ¥4.50 |
| Key Phrase番号TTS(修正前、Aoede新規生成の試行錯誤分) | ¥7.20 |
| Key Phrase番号(修正後、Charon共有資産再利用) | ¥0(追加コストなし) |

TTS/LLMとも正確なtoken単位usageは既存Production wrapper関数の戻り値に
含まれず(関数を編集しない制約のため)取得不能。既存precedent
(¥0.524/call・¥0.88/call)を根拠に安全側単価(TTS¥0.9/call、LLM¥1.8/call)
で推定した合算値であり、正確な実測ではないことを明記する。

## 14) 将来のProduction 1生成セット総原価(推定)

**¥45〜55(推定)**。内訳(定常状態、デバッグ起因の再試行を除く場合):
Key Phrase選定(1回で成功する場合、3 LLM call)≈¥5.4、Preview/Support LLM
(3 call)≈¥5.4、TTS一式(topic_intro 2+preview 1+support 2+story約18+
Key Phrase英語5+日本語gloss5=33 call)≈¥30、番号読み上げ¥0(共有資産)、
Assembly/Gate/player¥0(API不使用)。未確定要素: (a)記事ごとにstory
segment数が変動する、(b)Key Phrase選定の構造的失敗率(本記事[会話文
主体]で6回中4回失敗という高い頻度が観測された、原因は未確定[Open
Item候補、15)参照])、(c)正確なtoken単位コストではなく推定値。

## 15) 残る問題

- Key Phrase選定Production Validator(`validate_min_unit_selection`、
  `source_sentence`のB2本文照合)が、会話文主体のFamily C記事で高頻度
  (観測6回中4回)に構造的不合格になった。原因はLLMが引用符の境界を
  実際の本文とわずかに異なって抽出すること・finite auxiliary混入等で、
  News/Discovery等の会話文が少ない記事では起きにくい失敗モードと
  推測される。既存Validator自体は正しく機能しており(fail-closed)、
  今回は既存の正式入口を再度呼ぶ(選定やり直し)ことで解決したが、
  Family C(小説・会話文主体)の量産時にはこの再試行コストが繰り返し
  発生しうる。Open Item候補として記録(Validator変更はPMの承認が必要)。
- 短い単独英単語(Key Phrase番号"Three."/"Five.")のTTS/ASRで、CJK
  スクリプトへの誤書き起こしが発生する既知の不安定性(CURRENT_SPEC.md
  「`default`個別例外」と同種)がFamily Cでも再現した。既存共有Charon
  資産への切替で回避したが、根本原因(TTSが単独短語で言語をドリフト
  させる)は引き続き未解明(Open Item、Production全体のgap)。
- A2語数超過(429語、許容300〜420語)はTrial-08由来の既知事実で未修正。

## 16) Gate 1判定材料

音声Validation Gate: **PASS**(`FAMILY_C_TRIAL_09`レベル、opt-in
required_structureなし)。全23 narrationセグメント+15 Key Phraseサブ
セグメント、status=OK(38/38)。retry/fallback発生あり(15)参照、いずれも
既存安全装置の範囲内で解消、独自バイパスなし。完成音声はclipping無し
(peak=0.918、headroom safety valve不適用=元々閾値以内)。

## 17) USER_DECISION_REQUIRED一覧

1. A2/B1構成(11節): まずA2 1レベルで3本検証を提案。
2. Key Phrase選定Validatorの会話文主体記事での失敗率(15節)への
   対応要否(Family C固有のprompt調整等、Production変更が必要な場合は
   別タスクでの検討を提案)。
3. UI表示文読み上げ(Charon採用)・人物名ルール(episode_spec.md 8節、
   暫定案で妥当性確認のみ、恒久ルール化の要否)。

## 18) Status・Gate(分類)

Status: **VALIDATED**(Trial上限どおり、Production採用・配線なし)。
Gate 1(音声Validation Gate、機械的): PASS。Gate 2以降(ユーザー試聴・
Production採用判断)はユーザー確認待ち。

---

## Audio Validation Gate結果

PASS(`er013_output/family_c_episode_trial_09/home_robots/audio_validation.json`)。

## retry/fallback発生有無

あり。(a) Key Phrase選定: Production正式入口`run_key_phrases()`を
最大6回まで再試行できるよう設計(既存の1回限り仕様[`run_key_phrase_
selection`内部max_attempts=1]を回避せず、入口を再度呼ぶだけ)、6回中
4回目で構造的PASSに到達。(b) TTS: `generate_narration_snippet_verified_
strict`/`generate_charon_english`/`generate_key_phrase_component_verified`
いずれも既存の標準retry上限(3回、Key Phrase英語は最大4回)の範囲内で
動作、上限到達時はSTOPPEDとして記録しGateがfail-closedでBLOCKした
(2回発生: story_001[時刻表記読み修正で解消]、kp3/kp5_number[共有
資産切替で解消])。いずれも既存の安全装置(TTS試行回数上限・Audio
Validation Gate)を独自に緩和・回避していない。

## commit対象候補ファイル一覧(サイズ込み)

| パス | サイズ | 種別 |
|---|---|---|
| `er013_family_c_episode_trial_09_run.py` | 48K | 新規script |
| `er013_family_c_episode_trial_09_test_01.py` | 12K | 新規test |
| `er013_output/family_c_episode_trial_09/spec/episode_spec.md` | 20K | 仕様書 |
| `er013_output/family_c_episode_trial_09/home_robots/assembled/family_c_home_robots_trial_09.wav` | 48M | 完成episode音声 |
| `er013_output/family_c_episode_trial_09/home_robots/audio/*.wav`(38件、`.ok`markerは除外可) | 11M | 個別音声 |
| `er013_output/family_c_episode_trial_09/home_robots/player.html` | 16K | player |
| `er013_output/family_c_episode_trial_09/home_robots/key_phrases/` | 68K | Key Phrase中間成果物 |
| `er013_output/family_c_episode_trial_09/home_robots/audit/` | 37K | Gain/Headroom/Gate audit |
| `er013_output/family_c_episode_trial_09/home_robots/{preview.txt,support_ja.md,segments.json,article_normalized.txt,cost_summary.json,audio_validation.json,raw_usage_log.jsonl}` | 各数KB〜16K | 中間・報告成果物 |
| `docs/pm/delegation_log/EDITORIAL-FUTURE-FAMILY-C-HOME-ROBOTS-EPISODE-SPEC-TRIAL-09.md`+`_check.json` | 数K | T-0記録 |

合計 約59MB(音声2種が大半)。

## T-0結果

PASS(`docs/pm/delegation_log/EDITORIAL-FUTURE-FAMILY-C-HOME-ROBOTS-EPISODE-SPEC-TRIAL-09_check.json`、reasons無し)。

## 事前指定外Read(理由付き)

- `er005_stage7_cost_compute.py`(`record_cost`/`usd_to_jpy`の実装確認): 事前指定外。
  理由: 開発・Trial費の正確な算出可否を確認するため参照したが、既存
  Production wrapper関数がtoken usageを戻り値に含まないため実際には
  利用できず、precedent値からの推定方式を採用した(1行超の説明で恐縮だが
  費用報告の正確性に関わるため経緯を残す)。
- `audio_review_player.py`全文: 事前指定Read一覧では「Glob→`^def `」の
  入口確認のみ指示されていたが、標準player生成に実際に必要な定数
  (CSS/JS文字列等)も含めて全文Readした(player.html生成に必須のため)。
- `er011_human_review_lock_01.py::save_tts_attempt_audio`一部: STOPPED
  segmentの診断のため参照(事前指定外、デバッグ目的)。

## STOP有無

なし(費用上限内で完走、Gate PASSに到達)。
