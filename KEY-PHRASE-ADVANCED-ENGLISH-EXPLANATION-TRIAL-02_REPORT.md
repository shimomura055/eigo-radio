# KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-TRIAL-02_REPORT.md

管理ID: `KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-TRIAL-02`
実行者: Sonnet(サンドイッチ委任、Task D初回)
性質: Trial(Product仕様確認、text優先)。到達上限Status:
`USER_DECISION_REQUIRED`(ユーザー確認前、Production配線へ進まない)。
Production採用・配線は行っていない。

証跡格納先: `er041_output/key_phrase_advanced_english_explanation_trial_02/
hormuz/`(`inputs_resolved.json`, `candidate_a.json`,
`outputs/b_explanation.json`, `outputs/rubric.json`,
`match_results.json`, `summary.json`/`summary.md`,
`audio_summary.json`, `audio_raw_usage_log.jsonl`, `audio/*.wav`)
確認ページ: `user_test/kp_advanced_explanation_trial_02/index.html`
設計書: `docs/pm/design_key_phrase_advanced_english_explanation_trial_02.md`

---

## §1 Existing Spec / Prior Trial確認

過去`KEY-PHRASE-LEVEL-SPEC-TRIAL-01`(`KEY-PHRASE-LEVEL-SPEC-TRIAL-01_
REPORT.md`)のREJECT主因はPhrase選定Prompt v1側(4セット全FAIL、想定
一致5/20、Topic Word未選択、レベル配分不安定、同REPORT 340行「REJECTED
(Trial Prompt v1)。ユーザーの選定方針そのものではなく、方針をPromptに
落とした第1版が狙いのPhraseを再現できなかった」)。Advanced英語解説
自体は同REPORT §7.2で「語数はいずれも目安15語以内に収まっている(最大
12語)」「意味の正しさ(目視): 10件すべて、日本語で見ても英文の意味と
して誤りは見当たらなかった」と実測記録され、問題視されていない。

前回Prompt(`er017_key_phrase_level_spec_trial_01.py`
`ADVANCED_USER_TEMPLATE` 196行)のexplanation_enフィールド定義文
「a short, simple English explanation of the meaning — one sentence,
plain words, easier than the phrase itself; not a dictionary
definition. Example style: "raise privacy concerns" -> "to make people
worry about how personal information is used or protected"」を、本
Trialのscript内で`EXPLANATION_EN_SPEC_SENTENCE`として逐語保持し、
新Promptに埋め込んだ(regression testで前回Prompt定数の部分文字列で
あることを機械検証、§6参照)。語数上限`MAX_WORDS=15`も前回実測ベース
でそのまま流用(新規に決めた閾値ではない)。

OPEN-221(`OPEN_ITEMS.md` 404行)は本Trialが対応する未決事項そのもの:
「Advanced Key Phrase音声に既存の英語解説トラックが存在しない」
「`KEY_PHRASE_EXPLANATION_EN`実装には新規KP解説テキスト生成が必要」。
`TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01`(Task B)は`KEY_PHRASE_
EXPLANATION_EN`のstyle定義のみ用意し、実音声生成は「新規Key Phrase
解説テキストの創作はscope外」として意図的に見送っていた
(`er038_tts_all_spoken_role_style_trial_01.py` 73-77行)。本Trialが
その解説テキストの創作を担当する。

## §2 実施内容

Hormuz(`er019_output/family_x_audio_production_wiring_01/
family_x_b3_diversity_trial_01/hormuz__run_06_flashlite_full_kp/b1b/
key_phrases/keywords_canonicalized.json`)の既存確定済みAdvanced Key
Phrase 5個(`give back` / `sea blockade` / `stand at center stage` /
`take a sharp turn` / `recover the cost`)をそのまま使用(再選定・記事
再生成なし)。

1. `cmd_inputs`: 5 Phrase・`source_sentence`・`japanese_gloss`をそのまま
   Candidate Aとして保存(LLM不使用)。
2. `cmd_run`: B解説(5 Phraseまとめて1 call、`gpt-5.6-luna`、
   reasoning effort=medium、json_schema strict、fallback無し・retry無し)
   + rubric評価(1 call、7観点×5 Phrase)。
3. `cmd_evaluate`: `wordfreq.zipf_frequency`による語数・難度チェック
   (前回ロジック移植)+新規Fact混入検出(新設、source_sentence/phrase
   に無い大文字語頭語・数字トークンを検出)。
4. `cmd_assemble`: `summary.json`/`summary.md`に集約。
5. `cmd_audio`(任意、実施): Task B(`er038_tts_all_spoken_role_style_
   trial_01.py`)の`TRIAL_ROLE_STYLE_EN["KEY_PHRASE_EXPLANATION_EN"]`と
   `trial_master_audio_store`をimportで流用。Phrase EN音声・JA意味音声
   (A用)は既存Hormuz artifact(`narration/kp{rank}_en.wav` /
   `kp{rank}_ja_charon.wav`)を**コピーのみで再利用**(新規生成なし)。
   B用の英語解説音声のみ5 segment新規生成
   (`er003_v1_repro01_main_generate.generate_narration_snippet_
   verified_strict`を`KEY_PHRASE_EXPLANATION_EN` styleで直接呼び出し、
   Trial専用Store隔離、`TTS_EXECUTION_MODE=STANDARD`明示)。5件とも
   `status=OK`(retry無し)。

実行コマンド全文:
```
.venv/Scripts/python.exe er041_key_phrase_advanced_english_explanation_trial_02.py \
    --source-dir "er019_output/family_x_audio_production_wiring_01/family_x_b3_diversity_trial_01/hormuz__run_06_flashlite_full_kp/b1b" \
    --out-dir "er041_output/key_phrase_advanced_english_explanation_trial_02/hormuz" \
    --budget-jpy 20

TTS_EXECUTION_MODE=STANDARD .venv/Scripts/python.exe er041_key_phrase_advanced_english_explanation_trial_02.py \
    --audio \
    --source-dir "er019_output/family_x_audio_production_wiring_01/family_x_b3_diversity_trial_01/hormuz__run_06_flashlite_full_kp/b1b" \
    --out-dir "er041_output/key_phrase_advanced_english_explanation_trial_02/hormuz" \
    --trial-store "er041_output/key_phrase_advanced_english_explanation_trial_02/master_store" \
    --tts-backend speech_metadata_flash_lite --budget-jpy 20
```

## §3 Candidate(5 Phrase × A/B、実際の出力、転記)

| # | phrase | source_sentence | A: 日本語意味(現行/既存確定値) | B: 英語解説(新規生成) |
|---|---|---|---|---|
| 1 | give back | Brent crude futures briefly gave back some of their gains. | 上がった分をいったん吐き出す | to lose some of an earlier gain |
| 2 | sea blockade | Reuters linked that rise to concern about a US sea blockade of Iran, planned for the next day, and energy shipments through the Strait of Hormuz. | 海からの封鎖 | the act of stopping ships from entering or leaving by sea |
| 3 | stand at center stage | For the moment, only a large number stood at center stage. | 注目の中心にある | to be the main focus of attention |
| 4 | take a sharp turn | Then the story took a sharp turn. | 事態が急に変わる | to change suddenly and significantly |
| 5 | recover the cost | The aim was to recover the cost of US efforts to keep the strait safe. | かかった費用を回収する | to get back the money spent on something |

Phraseは5件ともA/Bで完全同一(既存Hormuz確定値をそのまま使用、
`test_phrase_identity_a_equals_b_and_equals_source`で機械検証)。

## §4 成果物

- 確認ページ: `user_test/kp_advanced_explanation_trial_02/index.html`
  (5 Phrase × A/B並列表+決定論指標+rubric7項目+音声再生[Phrase EN共通/
  A: JA意味音声/B: EN解説音声])
- GitHub Pages 200確認: `curl -sI
  https://shimomura055.github.io/eigo-radio/user_test/kp_advanced_
  explanation_trial_02/index.html` → 結果は§9のcommit/push後に実施
  (本REPORT作成時点ではpush前、RESULT_PACKETで最終ステータスを報告)。

## §5 品質評価

### 5.1 決定論指標(`match_results.json`、`wordfreq.zipf_frequency`)

| # | phrase | 解説語数 | 上限15語以内 | phraseより難しい語 | 新規Fact候補 |
|---|---|---|---|---|---|
| 1 | give back | 7 | OK | lose, earlier, gain | なし |
| 2 | sea blockade | 11 | OK | なし | なし |
| 3 | stand at center stage | 7 | OK | focus | なし |
| 4 | take a sharp turn | 5 | OK | なし | なし |
| 5 | recover the cost | 8 | OK | なし | なし |

全5件が語数上限内、新規Fact混入は0件(source_sentenceに無い固有名詞・
数字なし)。「phraseより難しい語」が1-3語出ている件があるが、前回Trial
(§7.2)でも同種の傾向(`come in`の解説で4語すべてがphraseより難しい
zipf)が観測されており、本Trialの傾向は前回よりむしろ少ない。

### 5.2 LLM rubric(7観点、1〜5+根拠、5 Phrase平均)

| # | phrase | 英語のみ理解 | 難易度 | 長さ | Phraseより易しいか | 再利用性 | 記事非依存 | 意味正確性 | 平均 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | give back | 5 | 4 | 5 | 4 | 5 | 5 | 5 | 4.71 |
| 2 | sea blockade | 5 | 4 | 5 | 5 | 5 | 5 | 5 | 4.86 |
| 3 | stand at center stage | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5.00 |
| 4 | take a sharp turn | 5 | 4 | 5 | 4 | 5 | 5 | 5 | 4.71 |
| 5 | recover the cost | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5.00 |

根拠付きの詳細は`outputs/rubric.json`とPagesページに全文掲載。
rubric平均は全5件4.7以上(自己評価LLMによる一次スクリーニングであり、
最終判断はユーザー試聴・確認に委ねる)。

### 5.3 ユーザー確認待ち項目

- 音声(Phrase EN共通再利用・JA意味音声再利用・EN解説新規音声)の実際の
  聞こえ方(発音・間・自然さ)。
- B解説文が「辞書的すぎない/記事文脈に依存しすぎない/日本語訳の直訳に
  なっていない」という定性基準をユーザー自身の感覚で満たすか。
- Standard/Advanced表記でユーザーに提示した際の分かりやすさ。

## §6 Regression

- `.venv/Scripts/python.exe -m unittest
  er041_key_phrase_advanced_english_explanation_trial_02_test_01 -v`:
  13/13 PASS(前回Prompt定数の部分文字列一致、MAX_WORDS根拠、新規Fact
  検出ヘルパー4ケース、Production Key Phrase選定モジュール非import、
  Production Master Store path非参照、実行済み出力に対するPhrase同一性
  ・語数上限・新規Fact0件の実測検証)。
- `.venv/Scripts/python.exe run_project_regression.py --pattern
  "er041*_test_*.py"`: `collected=13 passed=13 failed=0 errors=0
  skipped=0`。

## §7 Cost

| stage | call数 | cost_jpy |
|---|---|---|
| b_explanation(text) | 1 | 0.0576 |
| rubric(text) | 1 | 0.2388 |
| audio(B解説5 segment新規生成) | 5 | 0.6029 |
| **合計** | 7 | **0.8993** |

上限¥20に対し約4.5%の使用。fallback検出なし、retryなし
(`meta.fallback_detected=false`, `meta.retried=false`)。

## §8 再利用可能性

- explanation_enの仕様文・語数上限は前回Trialの実測結果をそのまま
  再利用でき、Prompt自体の再設計コストはゼロだった。
- Task B(`er038`)のRole style定義・Trial Master Store隔離
  contextmanagerを1行importで流用でき、音声化の追加実装コストは
  低かった(新規に書いたのはB解説音声5 segment生成の呼び出しのみ)。
- 既存Phrase EN音声・JA意味音声をコピーのみで再利用できたため、A側の
  音声化コストはゼロ(新規TTS呼び出しなし)。
- 今後Production化する場合、本Trialのdeterministicチェック
  (語数上限・zipf難度比較・新規Fact検出)はそのままGate候補として
  再利用可能と考えられる(Fable/ユーザー判断)。

## §9 新規発見

- 新規Fact混入検出ヘルパー(大文字語頭語+数字トークンの単純ヒューリス
  ティック)は実測5件で誤検出0件だったが、固有名詞を含む一般的な英語
  解説(例: 国名を含む一般論)では誤検出しうる簡易ロジックである点は
  留意事項として記録する(本Trialの5件では該当なし)。
- rubric平均が5件とも4.7以上と高く、前回Trialが示唆した「Advanced
  英語解説そのものは問題ではない」という仮説と整合する結果が得られた。

## §10 Trial Status(案)

`USER_DECISION_REQUIRED`。Sonnetは`VALIDATED`を自己宣言しない
(delegation指示どおり)。

## §11 USER_DECISION_REQUIRED

1. B(Advanced候補: 同一英語Phrase+平易な英語解説)を、将来
   `KEY_PHRASE_EXPLANATION_EN`実装のtext仕様として採用する方向で
   さらに検証を進めてよいか(Production採用はユーザーのみが判断)。
2. `user_test/kp_advanced_explanation_trial_02/index.html`の音声試聴後、
   発音・自然さに問題がないか。
3. 語数上限`MAX_WORDS=15`・新規Fact検出ロジックを、今後の本格Prompt
   設計時の参考値として引き継いでよいか。

## §12 Production変更ゼロの証拠

`git diff --stat HEAD -- "er0*.py" "er003_v1_translator_briefs/"
"er006_output/master_audio_store_01/" | grep -v er041` の結果は
`er038_tts_all_spoken_role_style_trial_01.py`(並行Task B、本Trialは
未変更・import読み取りのみ)と`er006_output/master_audio_store_01/
manifest.json`/`reuse_telemetry.jsonl`(並行タスクによる既存差分、
mtime確認で本Trial実行[17:33以降]より前の16:24時点の変更であることを
確認済み)のみで、本Trialによる差分はゼロ。`--audio`実行時も
`trial_master_audio_store`contextmanagerでProduction Store定数を一時
上書きし、実行後に必ず復元する既存パターン(Task Bと同じ)を使用した。

---

## §13 STOP有無

STOPなし。予算超過・異常retry・scope外処理は発生しなかった。ユーザー
試聴・確認待ちで本Sonnetの作業は完了とする。
