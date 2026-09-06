# OPEN-112-TREND-THEME2-B-FINAL-AUDIO-RERUN-01

管理ID: OPEN-112-TREND-THEME2-B-FINAL-AUDIO-RERUN-01
種別: Trial音声の完成試行(ユーザー承認済み、2026-09-06「A/BのProduction
wiring完了後、Theme 2のA2/B1完成音声を1回だけ再実行してよい」)。
到達Status: **`USER_DECISION_REQUIRED`(打ち切り)**。A2/B1とも完成音声
なし。Production変更なし。

## 0. 結論(先出し)

本文/Preview/Comment(A2 14 segment・B1 13 segment)のTrial-13再利用は
実装したが、**実行には至らなかった**。A2・B1とも、Key Phrase再選定の
最初の段階(既存Production構造Validator、`validate_min_unit_selection`、
`er003_key_words_production.py`)で**独立に同一パターンの
`KEY_WORDS_STRUCTURE_INVALID`**となり、この選定ステージは仕様上
retryなし(`max_attempts=1`、`er003_b1_p2_keywords.py`docstring
「自動再選定・自動再実行は行わない」)のため、canonicalization以降・
本文reuse・TTS・Assemblyのいずれにも到達せずSTOPした。D4(override・
fallback追加・上限緩和・手動unblock・再選定・場当たり修正の禁止)に
従い、再実行は行っていない(承認された「1回」を使用済み)。

## 1. 何が起きたか

A2・B1とも、Key Phrase選定候補5件中1件が"median"(統計用語)で、
日本語グロスに**括弧書きの補足**を含んでいた:

- B1 rank4: `median` → `データの真ん中の値（中央値）`
- A2 rank5: `median` → `真ん中の値（中央値）`

既存の構造Hard Requirement Validator(`er003_key_words_production.py`
経由の`p2g.validate_min_unit_selection`、KEYPHRASE-DISPLAY-TTS-
SEPARATION-PROD-WIRING-01/KEYPHRASE-JA-GLOSS-NATURALNESS-PROD-WIRING-01
より前から存在する既存ルール、本タスクでは無変更)がこれを検出:

> 「日本語グロスに括弧書きの補足が含まれている(音声だけで意味が成立
> する自然な表現にすること)」

この選定ステージ(`sc.run_key_phrase_selection`)は`max_attempts=1`で
呼ばれており(`er003_v1_n3_01_scaffold_generate.py`)、構造不適合時に
その場でretryする設計にはなっていない。`sc.run_key_phrases`の外側
retryループ(最大2回)はKey Phrase Set Redundancy QAがNGだった場合の
みを対象とし、選定自体の構造不適合時は即座に結果を返す(コード読解で
確認、`if sel["status"] != "KEY_WORDS_STRUCTURE_PASS": return {...}`)。
したがって両レベルとも1回の選定試行のみでSTOPした(既存仕様どおりの
正常な終端状態、retry予算を無駄に消費しない設計)。

**新しい発見(参考情報、実装はしていない)**: 両レベルが独立に同じ語
("median")を選び、同じ失敗パターン(括弧補足)を示したことから、
2026-09-06配線のKey Phrase日本語gloss自然さ規約(KEYPHRASE-JA-GLOSS-
NATURALNESS-PROD-WIRING-01、「学習者が聞いてすぐ分かる平易な現代日本語
にする」)が、"median"のような専門用語に対して、モデルが平易な説明
(「真ん中の値」)と元の専門用語(「中央値」)を両方残そうとする傾向を
誘発した可能性がある(既存の括弧禁止ルールとの相互作用、n=2のみで
一般化はできない)。これは新しいUser Decision候補であり、本タスクの
スコープでは調査・修正のいずれも行っていない。

## 2. 実装内容(実行はSTOPしたが、コードは完成・検証済み)

`er011_open112_trend_theme2_b_final_audio_rerun_01.py`(root)を新規
作成した。構成:

1. **本文/Preview/Comment再利用**(`prepare_level_inputs`/
   `reuse_non_kp_segments`/`_expected_canonical_text`): Phase 2
   Trial-02アダプタ(`er011_open117_keyphrase_display_tts_separation_
   trial_02.py`)のロジックをほぼそのまま踏襲。Trial-13の
   `article.md`/`parts.json`/support textsをコピーし、独立に再構成
   した期待canonical textとのsha256一致・review_lock RESOLVED状態を
   検証したうえでwav+`tts_generation_results.json`エントリを再利用
   する設計(**未実行**、Key Phrase段でSTOPしたため到達せず)。
2. **Key Phrase再選定**: Trial-02とは異なり、選定Promptの
   Trialコピー・書き換えは行わず、`sc.run_key_phrases`(Production
   関数、無変更)を直接呼ぶ(HEAD=f624a5c時点で表示用/TTS用分離・
   数値placeholder回避・gloss自然さ基準がいずれも選定Prompt本体へ
   配線済みのため)。
3. **Key Phrase音声生成**: `tts_gen.resolve_key_phrase_ja_gloss_tts`
   (Production関数、`japanese_gloss_tts`優先・欠落時のみ規則変換
   フォールバック)でTTS用テキストを解決し、
   `shared_narration.ensure_key_phrase_english_component`/
   `tts_gen.generate_charon_japanese_with_reading_safety`(B1)/
   `tts_gen.generate_a2_japanese_with_reading_safety`(A2)を直接呼ぶ
   設計(**未実行**)。
4. **STOPPED音声保全**(`preserve_stopped_audio_evidence`): Key
   Phrase英語/日本語生成のいずれかがSTOPPED等になった場合、関数が
   返った時点でdisk上に残る最後のattempt音声をコピー保全する設計
   (**未発火**、Key Phrase音声生成自体に到達しなかったため)。
   既知の制約として、Production側のretry loopは同一out_pathへ
   attemptごと上書きするため、上書き前の中間attempt音声を遡って
   復元することはできない(スクリプト内コメントに明記)。
5. Assembly(`asm.stage_assemble_b1`/`asm.stage_assemble_a2`、
   Production関数、無変更)呼び出し(**未実行**)。

TTS_EXECUTION_MODE=STANDARD(Standard同期)を設定済み(ただしTTS呼び
出し自体が発生しなかったため、raw_usage_log上もTTS API call・
`tts_execution_mode`記録は0件)。

## 3. 実行結果

```
b1b: status=STOP_KEY_PHRASE_PIPELINE_FAILED
     selection_status=KEY_WORDS_STRUCTURE_INVALID
     canonicalization_status=None(未実行) redundancy_qa_status=None(未実行)
a2:  status=STOP_KEY_PHRASE_PIPELINE_FAILED
     selection_status=KEY_WORDS_STRUCTURE_INVALID
     canonicalization_status=None(未実行) redundancy_qa_status=None(未実行)
```

両レベルとも、reuse_non_kp_segments・Key Phrase音声生成・Assembleの
いずれも呼び出されていない(コード上の分岐で`canonicalization is
None`の時点でreturnするため)。

## 4. Key Phrase候補5件×2レベル(選定はされたが構造Validatorで不採用、TTS未実行)

参考情報として、STOPした選定試行が実際に返した5件(表示用gloss、
TTS用テキストの解決・TTS/ASRはいずれも未実行)を記録する。

| Level | Rank | key_phrase(display_phrase) | 日本語gloss(ja_gloss) |
|---|---|---|---|
| B1 | 1 | two different speeds | 考えと予定の進み方が違うこと |
| B1 | 2 | interest-led plans | 興味を中心に組んだプラン |
| B1 | 3 | self-directed travel | 自分の希望で組み立てる旅行 |
| B1 | 4 | median | データの真ん中の値**（中央値）** ← 括弧補足で構造Validator FAIL |
| B1 | 5 | gap between | ～の間にある差 |
| A2 | 1 | less about adding nights | 泊数を増やすことが中心ではない |
| A2 | 2 | at their own pace | 自分のペースで |
| A2 | 3 | become the new normal | 新しい当たり前になる |
| A2 | 4 | not fully match | 完全には一致しない |
| A2 | 5 | median | 真ん中の値**（中央値）** ← 括弧補足で構造Validator FAIL |

英語Component/TTS用gloss/ASR書き起こし/分類/attempts/新Validatorラベル
発火は、いずれもTTS呼び出し自体が発生しなかったため**該当なし**。

## 5. 再利用segment数・新規TTS数

- 本文/Preview/Comment再利用(A2 14 segment・B1 13 segment): **0件
  実行**(コードは実装済みだが、Key Phrase段でSTOPしたため到達せず)。
- 新規TTS: **0件**(Key Phrase・本文とも、TTS API呼び出しは1件も
  発生していない。raw_usage_log.jsonlに`api`フィールドが
  `responses.create`[選定LLM]の2件のみ存在し、TTS/ASR関連の
  エントリは0件であることを確認)。

## 6. Gate/Lock停止の有無

**発生した(両レベルとも独立に)**。D4に従い、override・fallback
追加・上限緩和・手動unblock・再選定・場当たり修正は一切行っていない。

- 停止箇所: Key Phrase選定の構造Hard Requirement Validator
  (`p2g.validate_min_unit_selection`、`er003_key_words_production.py`
  経由、既存・無変更)。
- 原因: B1 rank4・A2 rank5がいずれも"median"を選び、日本語glossに
  括弧書き補足(「（中央値）」)を含めたため、既存ルール(「日本語
  グロスに括弧書きの補足が含まれている」)に抵触。
- retry: この選定呼び出し(`sc.run_key_phrase_selection`)は
  `max_attempts=1`(既存Production仕様、docstring「自動再選定・
  自動再実行は行わない」)。`sc.run_key_phrases`の外側retry
  (最大2回)はRedundancy QA NGの場合のみ対象で、選定構造不適合には
  適用されない(コード読解で確認)。
- 「new normal」型(英語Key PhraseのASRが非英語文字列を返す)は
  **今回は発生していない**(TTS呼び出し自体に到達しなかったため)。
- 保全すべきattempt音声: **無し**(TTS呼び出し自体が発生していない
  ため、`stopped_audio_evidence`ディレクトリは作成されなかった)。
  原文(rawの選定JSON全体)・ASR raw出力に相当する情報は、いずれも
  `{level}/key_phrases/keywords_runtime_metadata.json`の
  `attempts_detail[0]`(`item_reasons`含む)に完全な形で保存されて
  いる。

## 7. 完成音声

**なし**。A2・B1とも`assembled/`ディレクトリは作成されていない
(Assembleステージ自体が呼び出されていない)。総尺・clipping・
安全弁適用・file:// URLはいずれも提供できない。player.htmlも
(試聴可能な素材が無いため)作成していない。

## 8. 新Validator/分離方式の発火実績

**発火なし**(TTS呼び出し自体に到達しなかったため)。表示用/TTS用
分離(`japanese_gloss`/`japanese_gloss_tts`)は、構造Validatorで
不採用となった5件のcanonicalization自体が実行されていないため、
`japanese_gloss_tts`フィールドの値も生成されていない
(`keywords_canonicalized.json`は作成されなかった)。

## 9. cost

```
本タスク実費(Production標準経路、er005_cost_logger経由、選定LLM 2件のみ):
  keyphrase_b1b (gpt-5.6-luna, responses.create): $0.00905
  keyphrase_a2  (gpt-5.6-luna, responses.create): $0.01152
  合計: $0.02057 (概算 ¥3.3、$1=¥160換算)
```

TTS/ASR呼び出しは0件のため上記LLM選定費用のみ。Theme 2累計(Trial-11〜
17・OPEN-117 Phase 1/2・KEYPHRASE-DISPLAY-TTS-SEPARATION/KEYPHRASE-JA-
GLOSS-NATURALNESS Prod Wiring・本タスク、既存記録+今回): 約¥134
(既存記録)+ ¥3.3(本タスク)= **約¥137**。上限¥1,000に対し余裕あり。

計測: 上記raw_usage_log.jsonlの実測usage×`er005_output/cost_baseline_
01/pricing_snapshot.json`公式単価。

## 10. Production変更なしの確認

- `er003_v1_n3_01_scaffold_generate.py`/`er003_key_words_production.py`
  /`er003_b1_p2_keywords.py`/`er003_key_words_canonicalization.py`/
  `er003_v1_n3_01_tts_generate.py`/`er003_v1_n3_01_assemble.py`/
  `er006_audio_cost_pilot_02_shared_narration.py`/
  `er011_human_review_lock_01.py`/`er003_audio_tts_asr_safety.py`:
  いずれも無変更(すべて直接呼び出しのみ、monkeypatchなし)。
- `er003_v1_translator_briefs/b1_p2_keywords_l_prompt_template.txt`:
  無変更(読み込みのみ)。
- `CURRENT_SPEC.md`: 無変更。
- monkeypatch: 使用していない。
- status格上げ: なし(A2/B1とも完成音声に到達していないため
  `USER_FINAL_AUDIO_REVIEW_REQUIRED`は該当なし)。

## 11. 今回実施しなかったこと

- 選定Promptの調整(括弧禁止ルールと自然さ規約の相互作用への対処)は
  行っていない(User Decision待ち、5節参照)。
- 再選定・再実行(承認された「1回」を使い切ったため、本タスクの
  スコープでは実施しない)。
- 本文/Preview/Comment reuse・Key Phrase音声生成・Assemblyの実行
  (Key Phrase選定段でSTOPしたため到達せず)。

## 12. 証跡

- Adapter script: `er011_open112_trend_theme2_b_final_audio_rerun_01.py`
- 出力: `er011_output/open112_trend_theme2_b_final_audio_rerun_01/`
  (`rerun01_summary.json`、`{a2,b1b}/key_phrases/{keywords_selector_
  prompt.txt,keywords_runtime_metadata.json}`、`{a2,b1b}/audit/
  run_key_phrases_result_summary.json`、`raw_usage_log.jsonl`)
- 実行ログ:
  `C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\
  bde7fde1-1f90-4f48-949b-1feadb194863\scratchpad\rerun01_run.log`
  (セッション一時領域、恒久証跡は上記er011_output配下)

## 13. 次にユーザーが判断すること

- (a) この選定結果を「1回」の消化とみなし、本タスクをここで打ち切る
  (現状の判断)。
- (b) 括弧補足ルールと自然さ規約の相互作用について、選定Promptへの
  追加ガイダンス(例:「専門用語を選ぶ場合、平易な言い換えのみを使う
  か、専門用語のみを使うかのどちらかにし、両方を括弧で併記しない」)
  を検討する追加タスクを別途承認するか。
- (c) 別のKey Phrase候補セットが得られることを期待して、改めて
  「1回」の再実行を承認するか(その場合も同じ構造Validatorが同じ
  理由で再度発火する可能性は排除できない、n=2の再現からやや高い
  可能性があると考えられる)。
