# 管理ID

USER-TEST-AUDIO-COMPLETION-01-DISCOVERY(Discovery / Why can silence feel uncomfortable?: B1B Key Phrase人手選定+A2/B1B音声化+Web試聴player)
並行タスク衝突確認: 並行して Family C(er013)、Trend(`.../trend/`)、Voices(`.../voices/`、er012_*)が走る。本タスクは`er014_output/four_type_observation_01/discovery/`配下のみを書き、Git・SSOT・ACTIVE_TASK・RESULT_PACKET.mdを触らない。共有資産への書き込みは既存経路が自動で行う分のみ。RESULT_PACKETは`docs/pm/RESULT_PACKET_UT_DISCOVERY.md`(新規)。

## 性質/到達上限Status/禁止事項

- 性質: (A) B1B Key Phraseを**人手選定**で完成、(B) 完成済みcanonical article(A2 `discovery/a2/article.md`=`reader_facing_article.txt`、B1B `discovery/b1b/article.md`=`reader_facing_article_b1b.txt`)+Key Phraseを既存正式audio completion経路でA2/B1双方の完成episode+Web試聴playerまで仕上げる。記事本文を変更しない。
- **(A) B1B Key Phrase人手選定(ユーザー判断確定)**: 条件=canonical B1B本文に実際に存在する連続spanから5件選ぶ/既存Key Phrase仕様(Strategy L=Listening Blocker Ranking、standalone natural unit、残余文脈語なし、意味保持、他文脈で再利用可、B2本文照合可、5件間で冗長でない、英語→日本語gloss(表示用/TTS用分離))に準拠/**「have agency」は採用しない**(既存Validatorが語彙動詞haveを有限助動詞として誤検知するため。本文を書き換えて回避しない)/**既存Validatorを変更しない**/選定理由を各phraseに記録。手順: B1B最終本文を読み、候補8〜10件を列挙→有限助動詞ブロックリスト(is/are/was/were/has/have/had/will/would/can/could/should/may/might/must)を含むspanを除外→Listening Blocker価値順に5件確定→既存canonicalization+Redundancy QA(`er003_key_words_canonicalization`、`run_key_phrases`内部の該当関数を「選定済み5件を入力として」呼べる既存関数があればそれで実行。無ければ選定LLM段階をスキップし、canonicalization/gloss/Redundancy QAの既存関数を直接呼ぶ最小driverを書く。Validator自体は無変更)→`key_phrases/b1b/keywords_canonicalized.json`(既存形式)を確定。出力に`selection_mode: "manual_user_decision_2026-09-14"`と選定理由・除外理由(have agency)を`key_phrases/b1b/manual_selection_rationale.md`へ記録。旧試行は`key_phrases/b1b_old_attempts/`へ退避(既に存在すればそのまま)。
- **(B) 音声化**: 経路調査を先に実施: A-Family A2/B1B既存完成経路の実例=`er011_output/family_a_completion_a2_trend_end_to_end_01/`。生成scriptをGlob `er011_family_a_completion*.py`/`er011_*end_to_end*.py`で特定。Discovery Focus S2記事(`er003_discovery_focus_staged_production_01`で生成、Point構造)に対しその経路が使えるか確認し、gapがあれば新仕様を作らず既存資産で最小接続(`discovery/run_discovery_audio_completion.py`)。A2/B1Bそれぞれ: Key Phrase(A2は既存`key_phrases/a2/`を使用、B1Bは(A)の結果)、Preview/Comment等の既存level仕様要素(既存経路が生成するもの)、TTS(既存retry/fallback、A2 slowdown等)、Assembly(Intro/Outro/SFX)、Audio Validation Gate(緩和禁止)、完成episode WAV+配信用MP3(既存変換手段優先、Grep `mp3|ffmpeg|pydub` in ルート`*.py`、無ければffmpeg、pip install禁止)、標準Audio Review Player再利用(**相対パス参照のみ**、Title/level/完成episode/segment表判別可、A2とB1Bは別player `discovery/audio/a2/player.html`・`discovery/audio/b1b/player.html`)、記事⇔音声一致確認(`article_audio_consistency.json`)、gitignore確認・mp3<50MB。予定URL形式: player=`https://raw.githack.com/shimomura055/eigo-radio/main/er014_output/four_type_observation_01/discovery/audio/a2/player.html`、直接音声=`https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er014_output/four_type_observation_01/discovery/audio/a2/web/episode.mp3`(B1Bも同様)。
- 費用: `discovery/audio/cost_summary_audio.json`(Key Phrase B1B canonicalization/gloss LLM、Preview・Comment LLM、TTS、その他を分離、level別)、`discovery/production_set_cost.json`更新(Discovery Production 1生成セット総原価=既報¥463.27+Key Phrase B1B人手選定分+音声化追加費、差分明記、50:50配賦なし)。
- 費用上限: ¥160(Key Phrase B1B gloss/QA ≈¥5、A2+B1B音声化)。段階ごとに次段階見込み込みで事前判定。
- 禁止: 記事本文変更/Validator変更/have agency採用/Fact Checker再実行/Gate緩和/retry上限変更/新player仕様/Production(er003/er006/er011)コード変更/`.gitignore`変更/pip install/Git commit・push/`run_project_regression.py --pattern`に`_test`を含まないglob/PATH上の素`python`。
- STOP条件: 新Production仕様が必要/Gate緩和が必要/canonical記事変更が必要/費用上限超過見込み/技術的にWeb配信不可。STOP時は「何を試したか/何が残ったか/ユーザーに必要な判断」を提示。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

---
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
---

## ユーザー指示(原文)

> 今回は完成を急ぐため、B1B Key Phraseは人手で別Phraseを選定して完成する。既存Validatorが誤検知するhave agencyは今回は採用しない。条件: canonical B1B本文に実際に存在するphraseから選ぶ/既存Key Phrase仕様に準拠/have agencyを避けるためだけに本文を書き換えない/既存Validatorを今回変更しない/選定理由を記録/Validator false positive問題はOpen Item化する。Key Phrase確定後、完成済みA2/B1B記事+Key Phraseを用いて、既存正式audio completion経路で、TTS/A2 slowdown等/Comment・Preview等既存仕様/Assembly/Audio Validation/完成episode/Web試聴playerまで進める。A2/B1双方をユーザーが試聴できる状態にする。

## 事前指定Read一覧

1. `er014_output/four_type_observation_01/discovery/b1b/article.md` 全文(人手選定に必須)。
2. `er014_output/four_type_observation_01/discovery/key_phrases/a2/keywords_canonicalized.json` L1-60(既存出力形式)。
3. `er003_v1_n3_01_scaffold_generate.py`: Grep `^def run_key_phrases|^def run_key_phrase_selection|^def run_canonicalization|^def run_keyphrase_redundancy|^def validate_min_unit_selection|FINITE_AUX|auxiliar` → 段階分離と「選定済み入力」を受ける関数の有無のみ。
4. `er003_key_words_canonicalization.py`: Grep `^def ` → 入口のみ。
5. Glob `er011_family_a_completion*.py`、`er011_*end_to_end*.py` → Grep `^def |argparse|add_argument|editorial_mode|level|out_dir|run_key_phrases|assemble|verify_episode_audio_validation_gate|player` → 入口・引数・段階構成のみ。
6. `er011_output/family_a_completion_a2_trend_end_to_end_01/`: Glob `**/*.json`(ファイル名一覧)。
7. `CURRENT_SPEC.md`: Grep `A2 slowdown|A2.*speed|Intro|Outro|SFX|Audio Validation Gate|Discovery Focus S2` → 該当行のみ。
8. `audio_review_player.py`: Grep `^def |src=|relative|title|level` → 引数のみ。
9. `er014_output/four_type_observation_01/discovery/production_set_cost.json` 全文。
10. `.gitignore`: Grep `wav|mp3|er014|output|audio`。

## 事前指定Grep一覧+追記位置・更新位置の手順

- `discovery/key_phrases/b1b/`(確定、既存形式)+`manual_selection_rationale.md`。
- driver `discovery/run_discovery_audio_completion.py`(新規、既存関数の最小接続、budget_jpy=160、level a2/b1b)。出力: `discovery/audio/a2/{key_phrases/,tts/,assembled/,audio_validation.json,player.html,web/episode.mp3,web/segments/*.mp3,article_audio_consistency.json}`、`discovery/audio/b1b/`同構成、`discovery/audio/cost_summary_audio.json`、`discovery/audio/web_delivery.json`、`discovery/production_set_cost.json`更新、`progress_log.md`1行追記。

## 実行コマンド全文

(すべて `C:\Users\tensh\eigo-radio` で実行)
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\USER-TEST-AUDIO-COMPLETION-01-DISCOVERY.md --json-out docs\pm\delegation_log\USER-TEST-AUDIO-COMPLETION-01-DISCOVERY_check.json`
2. Key Phrase B1B: `.venv\Scripts\python.exe er014_output\four_type_observation_01\discovery\finalize_key_phrases_b1b_manual.py`(本タスクで作成、選定5件をscript内に固定。全文コマンド記録)
3. 音声化: `.venv\Scripts\python.exe er014_output\four_type_observation_01\discovery\run_discovery_audio_completion.py --level a2` → `--level b1b`
4. 確認: `Select-String -Path er014_output\four_type_observation_01\discovery\audio\*\player.html -Pattern "file:///|C:\\" | Measure-Object -Line`(0件)
5. `git check-ignore -v er014_output/four_type_observation_01/discovery/audio/a2/web/episode.mp3`
(回帰不要: Productionコード変更なし。)

## SSOT追記文

本タスクではSSOTを編集しない。RESULT_PACKETにOPEN-135末尾追記案(Key Phrase B1B人手選定完成・音声化完成・総原価)、新規Open Item案「Key Phrase Validatorが語彙動詞have/hasを助動詞として誤検知」(症状・再現・影響・Production変更なし)を記載。

## Git(明示add対象・コミットメッセージ・trailer)

本タスクではGit操作を行わない。RESULT_PACKETに「commit対象候補一覧(サイズ付き)」を列挙。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_UT_DISCOVERY.md`に: 1) 最終Status(Key Phrase B1B/A2音声/B1B音声)、2) 人手選定B1B Key Phrase 5件(phrase/gloss/出典文/選定理由)、除外候補と理由(have agency含む)、canonicalization/Redundancy QA結果、3) 使用した既存経路とgap/最小接続、4) Preview/Comment等の生成要素一覧、5) TTS(call数、retry/fallback、slowdown適用値)、6) Audio Validation結果(A2/B1B)、7) 完成episode duration、8) 記事⇔音声一致確認、9) mp3一覧・player相対参照確認・予定URL・gitignore確認、10) 費用: Key Phrase B1B分、音声化追加費(level別)、**Discovery Production 1生成セット総原価=¥463.27+追加=¥xx.xx**、11) model_id/TTS model、12) Open Item案(Validator誤検知)、13) commit対象候補一覧、14) T-0・事前指定外Read・STOP有無。

## Fable自己チェック(送信前)

- [x] Read一覧に行範囲/Grepパターンあり
- [x] 追記位置手順あり
- [x] コマンドに引数実値あり
- [x] 禁止事項・費用上限あり(¥160)
- [x] 並行タスク衝突回避あり(discovery/配下限定・Git操作なし)
