# TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-01_REPORT

管理ID: TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-01(Trial、Production実装なし)

## 1. Existing Spec / Prior Trial確認

- 対象: `er006_audio_cost_pilot_02_shared_narration.py`(canonical text定義、`FIXED_ENGLISH_TEXTS`
  9件+`FIXED_JAPANESE_TEXTS_A2_ONLY`1件=**計10件**)、`er006_master_audio_store_01.py`
  (`MasterAudioKey`/`EQUALITY_FIELDS`/`get_or_generate`)、Production manifest
  (`er006_output/master_audio_store_01/manifest.json`、read-only)。詳細な仕様表・実測manifest突合は
  `docs/pm/design_tts_fixed_shell_master_champion_trial_01.md` §1-1〜1-4。
- 棚卸し結果: `er019_family_x_audio_production_runner_01.py`の`ensure_all_shared_narration_b1/a2`が
  参照する定数のみが「全記事共通かつ文言固定」のTTSであり、上記10件で全数(追加の固定TTSは見つからず)。
- 既存Production manifest実測(read-only): 対象10件は全て`v1`(2.5 Pro系/structured_separation、
  `asr_verified`未記録)・`v1` flash-lite(古style、`asr_verified=True`)・`v2_flash_lite_short_style`
  (現行Flash-Lite Baseline、**num_two/num_three含め全9 EN件`asr_verified=True`**)の3層で既に登録済み。
- 過去Trial(`TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01`、Task B)実測: 同じFlash-Lite・Charon・B1B経路で
  NUMBER_LABEL style("brief, clear, neutral")を使ったnum_two/num_threeが3attempt全て言語ドリフト
  (CJK)でHuman Review Lock到達済み(`OPEN-222`)。本Trialは、この既知失敗の再現にAPIを消費しない設計
  方針を採った(設計書§1-5)。

## 2. 実施内容

新規script`er040_tts_fixed_shell_master_champion_trial_01.py`(生成)+
`er040_tts_fixed_shell_master_champion_trial_01_page_01.py`(mp3変換・比較ページ生成)+
`er040_tts_fixed_shell_master_champion_trial_01_test_01.py`(15 unit test、実API無し)を新規作成。
Production関数(`shared_narration.ensure_fixed_english_segment`/`ensure_fixed_japanese_segment`、
`voice01.generate_charon_english`/`generate_charon_japanese`)をそのままTrial Store経由で呼び、
JA側styleの差し替えは既存precedent(`er011_final26_runtime_evidence_01.py`と同一手法、
`voice01.p9a.JAPANESE_STYLE_PREFIX`の一時モンキーパッチ+finally復元)を踏襲した。

実行コマンド(逐語):
```
TTS_EXECUTION_MODE=STANDARD .venv/Scripts/python.exe er040_tts_fixed_shell_master_champion_trial_01.py \
  --candidates A,B,C --out-dir "er040_output/tts_fixed_shell_master_champion_trial_01" \
  --trial-store "er040_output/tts_fixed_shell_master_champion_trial_01/master_store" --budget-jpy 40
```
実行1回目、`ensure_candidate_b_english`等の出力先ディレクトリ未作成によりwelcome生成後に
`FileNotFoundError`でクラッシュ(TTS 1件分の軽微な無駄呼び出し、7 input tokens、実害僅少)。
`os.makedirs`追加で修正し2回目を実行、正常完了。テストは`.venv\Scripts\python.exe -m unittest
er040_tts_fixed_shell_master_champion_trial_01_test_01`(pytest未インストールのため代替、
`run_project_regression.py --pattern "er040*_test_*.py"`でも15/15 PASS確認済み)。

## 3. Candidate設定

| Candidate | 定義 | 対象範囲 |
|---|---|---|
| A(Baseline) | Production既存Master(`v2_flash_lite_short_style`、既にasr_verified=True)をread-onlyで再利用。新規TTS/ASR呼び出しなし | 10/10 |
| B(Role style) | Flash-Lite + `docs/pm/design_tts_all_spoken_role_style_trial_01.md`§3のRole style短文(PROGRAM_SECTION_INTRO/KEY_PHRASE_INTRO/FULL_STORY_INTRO/NUMBER_LABEL) | 8/10(num_two/num_three除外、既知失敗回避) |
| C(2.5 Pro系) | `tts_backend="structured_separation"`(既定・style override無し) | 10/10(num_two/num_threeも含め新規生成) |

詳細は設計書§3。

## 4. 成果物

- 試聴比較ページ: `user_test/fixed_shell_champion_trial_01/index.html`
  (公開URL: https://shimomura055.github.io/eigo-radio/user_test/fixed_shell_champion_trial_01/index.html 、
  `curl -sI`で200確認済み)
- Trial結果JSON: `er040_output/tts_fixed_shell_master_champion_trial_01/champion_trial_results.json`、
  `comparison_data.json`
- 音声: mp3 30件(phrase×candidate、`lameenc`使用、ffmpeg/pydub不在のため既存precedent
  [`er003_v1_b1_p3y_generate.py`等]と同じ判断枠組みでpure-python encoderを採用)+One→Five連結mp3 3件
  (候補ごと)。総サイズ約844KB(50MB閾値内、commit前STOP不要)。

## 5. 品質評価(機械判定分、主観評価はユーザー試聴待ち)

### 5-1. 全体結果(10 phrase × 3 candidate)

| Candidate | OK | STOPPED | SKIPPED(既知失敗) |
|---|---|---|---|
| A | 10/10 | 0 | 0 |
| B | 7/10 | 1(num_one、**新規発見**) | 2(num_two/num_three) |
| C | 9/10 | 1(num_three、**新規発見**) | 0 |

### 5-2. One〜Five統一感(揃い)の定量比較

| Candidate | OK件数 | duration範囲(max-min) | RMS範囲(max-min) |
|---|---|---|---|
| A | 5/5 | 0.33秒(0.64〜0.97s) | 4.68dB(-24.32〜-19.64) |
| B | 2/5(num_four/five のみ) | 0.09秒 | 3.45dB |
| C | 4/5(num_three欠落) | 0.44秒 | 2.82dB |

**Candidate Aのみが5/5全件揃った完全セット**。Candidate Cはvolumeの揃いはAよりやや良いが
num_threeが欠落(3attempt全てTRUE_CONTENT_MISMATCH、後述§9)。Candidate Bは2/5のみで
One→Five連続再生としては不完全。

### 5-3. ASR一致・drift有無
Welcome/preview_intro/key_phrases_intro/full_story_intro/point_explanationはA/B/C全て
`asr_text`が原文と一致(drift無し)。数字語(num_one〜five)のみ、候補・語ごとに個別のドリフト発生
(§9で詳述)。

### 5-4. ユーザー試聴待ち項目
声色・テンポ・Role差の自然さ、JA style「簡潔に、はっきりと」の自然さ、Candidate B/Cの英語style
("warm, brief, welcoming"等)がProduction既存style("natural, clear, conversational")と比べて
聴感上どうか、は機械判定不可のためユーザー試聴が必要。

## 6. Regression

- `.venv\Scripts\python.exe -m unittest er040_tts_fixed_shell_master_champion_trial_01_test_01 -v`:
  15/15 PASS(初回12件+追加3件)。
- `run_project_regression.py --pattern "er040*_test_*.py"`: `collected=15 passed=15 failed=0 errors=0`。
- `test_master_audio_key_distinguishes_style_versions`: Production既存2種(v1/v2_flash_lite_
  short_style)+本Trial新設(`trial_ch1_role_style_v1`)の3keyが全て異なる`master_audio_id`を持つ
  ことをPASS確認(誤reuse無し)。
- `test_trial_master_audio_store_restores_*`: モンキーパッチが正常時・例外時とも必ず復元される
  ことをPASS確認。

## 7. コスト実測

合計**¥3.61**(実API、gemini ¥3.44 + openai_asr ¥0.16)。Guardrail¥40以内(9%未満)。
Candidate A(10件)は新規API呼び出し0(既存Master再利用のみ)。ディレクトリ未作成バグによる
welcome再実行1回分(7 input tokens)を含む。num_one(Candidate B)・num_three(Candidate C)は
3attempt上限まで実行され通常の失敗コストに含まれる(異常retryではなく既存安全装置内)。

## 8. 再利用可能性・量産コスト削減概算

Family X 1記事(B1B+A2)あたりの固定phrase呼び出しは、既存`level=None`共有key設計により
**既に**B1B側生成分をA2側が無条件reuseしている(追加TTS呼び出し0)。したがって「Champion化」
自体による記事単位の限界削減効果は、新テーマ立ち上げ時ではなく**将来Role style更新等でstyle_
instruction_versionを変える度に必要な再生成イベント**が基準になる: 対象10 phrase(EN 9+JA 1)を
Role styleへ全面移行しようとした場合、TTS+ASR実測コストは¥3.61程度(本Trialで実測)だが、
**本Trialにより「素朴な全面移行はnum_one/two/threeで高確率に失敗しHuman Review Lockを誘発する」
ことが¥3.61の支出で事前に判明した**。これにより、量産環境でのブラインドなRole style全面切替
(Human Review Lock発生→手動対応→記事公開遅延というコスト)を回避できる可能性が高い。

## 9. 新規発見

1. **Candidate B(Role style)のnum_oneが新規に3attempt全てASR検証失敗(STOPPED)**
   (`er040_output/.../champion_trial_results.json`candidates.B.num_one.attempts_log)。attempt1
   `asr_text`=CJK1文字(TTS_FAILURE)、attempt2=`"1"`(TRUE_CONTENT_MISMATCH、"One."ではなく数字表記
   でも不一致扱い)、attempt3=CJK1文字(TTS_FAILURE)。従来num_two/num_threeのみが既知失敗だったが、
   **num_oneも同じRole style文言("brief, clear, neutral")で同様の不安定性を示すことが判明**した
   (OPEN-222の対象語をnum_one含む3語へ拡張すべき可能性、§11)。
2. **Candidate C(既存2.5 Pro系/structured_separation)のnum_threeも3attempt全て不合格**
   (candidates.C.num_three.attempts_log、asr_text="Free"→CJK1文字→CJK1文字、全てTRUE_CONTENT_
   MISMATCH)。**Flash-Liteを使わない既存2.5 Pro系バックエンドでも、num_threeの言語ドリフト類似の
   不安定性が再現した**。これはOPEN-222の考察(「Flash-Lite固有ではなく極短context-free単語一般の
   限界の可能性」)を裏付ける追加evidence。
3. Candidate C num_twoは3attempt中2回(`"二"`, `"두"`=韓国語表記)がCJKドリフトし、3回目
   (`"2"`)でようやく合格した。**Production既定backend(2.5 Pro系)でも数字語は非決定的に不安定**
   であり、既存Flash-Lite Baseline(Candidate A、num_two/three含め全件1回で安定)の相対的な優位性
   を示すデータになった。
4. mp3変換用`ffmpeg`/`pydub`が本環境に存在しなかったが、`lameenc`(pure python、pip既導入済み)で
   代替でき、既存precedent(`er003_v1_b1_p3y_generate.py`等の「エンコーダ無ければwavのまま」判断)
   を発展させ、今回は問題なくmp3化できた(将来のPages配布Trialでも`lameenc`を選択肢に追加できる)。
5. `er011_human_review_lock_01.ATTEMPT_HISTORY_PATH`(`er011_output/attempt_history.jsonl`、モジュール
   グローバルの共有固定path)へ、本Trial実行分(num_one/num_two/num_three関連の3attempt)が追記された
   ことをmtime確認で検出した(既存Task B[`TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01`]のOPEN-223と同型の
   既知限界、本Trialでも意図的には隔離していない。delegationがMaster Audio Storeのみ隔離を明示
   していたため)。一方`er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`は本Trial
   実行前後でmtime不変(=正式Human Review Lockキューへの新規登録は無し、STOPPED止まり)。両ファイル
   とも本Trialのcommit対象には含めない(§12)。

## 10. Trial status案

**USER_DECISION_REQUIRED**(ユーザー試聴+Champion選定待ち)。補助的所見(機械判定のみ、順位付け):
- welcome/preview_intro/key_phrases_intro/full_story_intro/point_explanation: A/B/C全て`asr_verified`
  相当のOK、drift無し。声色・style自然さの選定はユーザー試聴必須。
- num_one〜five(One〜Fiveセット): **Candidate A(現行Production Baseline)が唯一の完全5/5セット**。
  Candidate B/Cは各1語ずつ新規失敗を出しており、機械判定上はAが現時点で最も安全な選択。

## 11. USER_DECISION_REQUIRED(phraseごとのChampion選択)

phraseごとに`user_test/fixed_shell_champion_trial_01/index.html`でA(Baseline)/B/Cを試聴し、
Championを選んでください(選定後もProduction wiringは別管理IDで実施予定、本Trialでは配線しない)。
- welcome/preview_intro/key_phrases_intro/full_story_intro/point_explanation: 3候補とも定量的には
  問題なし、声色・雰囲気で選択。
- num_one/num_two/num_three: Candidate Aのみ全件成功。B/Cは新規失敗を含むため、**現時点ではA継続を
  推奨**(ユーザー最終判断)。
- num_four/num_five: 3候補とも成功、揃いで選択可。

SSOT追記案(OPEN_ITEMS.md新規行、ユーザー承認後にFableが正式反映):
> **OPEN-XXX**: num_one(Flash-Lite + Role style"brief, clear, neutral")が新規にHuman Review Lock相当
> の3attempt全滅を起こした(2026-09-28`TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-01`)。従来OPEN-222は
> num_two/num_threeのみを対象としていたが、本Trialでnum_oneも同型の不安定性を示すことが判明した
> (`er040_output/tts_fixed_shell_master_champion_trial_01/champion_trial_results.json`
> candidates.B.num_one)。加えて、既存2.5 Pro系backend(structured_separation)でもnum_threeが同型の
> 不安定性(3attempt全滅、`candidates.C.num_three`)を示し、num_two相当も3attempt中2回CJKドリフトの
> 後3回目で合格した(`candidates.C.num_two`)。Flash-Lite固有ではなく数字語一般の限界の可能性が
> 一段と強まった。`OPEN` / Production非影響(現行Baselineは全件asr_verified=True)。

## 12. Production変更ゼロの証拠

```
$ git diff --stat HEAD -- "er0*.py" "er003_v1_translator_briefs/" "er006_output/master_audio_store_01/" | grep -v er040
 er006_output/master_audio_store_01/manifest.json   | 696 +++++++++++++++++++++
 .../master_audio_store_01/reuse_telemetry.jsonl    |  78 +++
 er038_tts_all_spoken_role_style_trial_01.py        | 169 ++++-
 ...8_tts_all_spoken_role_style_trial_01_test_01.py |  88 +++
```
上記4件は**本Trial開始前から既に存在していた他タスクの差分**(mtime確認: manifest.json/
reuse_telemetry.jsonlは2026-09-28 16:24:14更新、本Trialの実API実行は同日17:2x台。er038系2件は
並行Sonnet[Task B追補]の所有物、本Trialは一切編集していない)。本Trialのcommit対象からは
`er006_output/master_audio_store_01/`・`er038_*`を明示的に除外する(下記Git参照)。Production Store
への書き込みは、Trial実行中一貫してモンキーパッチにより`er040_output/.../master_store/`へ隔離され
ていたことを、`trial_master_audio_store()`のcontext manager実装+regression test(`test_trial_
master_audio_store_restores_*`)で確認済み。

## Git

- add対象: `er040_tts_fixed_shell_master_champion_trial_01.py`、
  `er040_tts_fixed_shell_master_champion_trial_01_page_01.py`、
  `er040_tts_fixed_shell_master_champion_trial_01_test_01.py`、
  `er040_output/tts_fixed_shell_master_champion_trial_01/champion_trial_results.json`、
  `comparison_data.json`(json/md、wavはcommitしない)、
  `user_test/fixed_shell_champion_trial_01/`(mp3/html)、本REPORT、
  `docs/pm/design_tts_fixed_shell_master_champion_trial_01.md`、delegation_log 2件。
- 除外(意図的): `er006_output/master_audio_store_01/*`(他タスク由来、Production SSOT)、
  `er038_*`(他Sonnet所有)、`er040_output/.../master_store/`(wav、`.gitignore`の`*.wav`規則で
  自動除外)、`raw_usage_log.jsonl`(実API課金明細、個人情報無しだが本体REPORTへ実測値を転記済み
  のため非commit判断)、`er011_output/attempt_history.jsonl`・
  `er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`(共有append-only監査ログ、
  §9-5開示のとおり他タスクの未commit差分と混在するため非commit)。

commit hash: `8047392c0bb686ecaae391d470408a9d0b284364`(push origin/main成功、fast-forward、
競合なし)。

Raw URL(代表ファイル):
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er040_tts_fixed_shell_master_champion_trial_01.py
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er040_tts_fixed_shell_master_champion_trial_01_page_01.py
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er040_tts_fixed_shell_master_champion_trial_01_test_01.py
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/docs/pm/design_tts_fixed_shell_master_champion_trial_01.md
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-01_REPORT.md
