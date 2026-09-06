# OPEN-117-KEYPHRASE-DISPLAY-TTS-SEPARATION-TRIAL-02 (Phase 2)

管理ID: OPEN-117-KEYPHRASE-DISPLAY-TTS-SEPARATION-TRIAL-02(Phase 2)
種別: Trial(ユーザー承認済み、2026-09-06)。**Production本体(コード・Prompt・
スキーマ)は無変更。** Production関数はそのまま使い、表示用/TTS用の分離
ロジックだけをTrial側アダプタ(`er011_open117_keyphrase_display_tts_
separation_trial_02.py`)で挟んだ。
Phase 1(VALIDATED、`OPEN-117-KEYPHRASE-DISPLAY-TTS-SEPARATION-TRIAL-01_
REPORT.md`)は低レベルTTS関数を直接呼ぶ隔離Trialだったが、Phase 2は
Theme 2(若者の旅行、B条件)のA2/B1で、**Key Phrase選定から完成音声
Assemblyまでを、量産時と同じProduction正式経路+Trialアダプタ**で確認した。

## 0. Closeout分類

**分離方式(表示用gloss→TTS用テキストへの規則変換、文頭/読点直後の
「～」「〜」→「なになに」)自体は、Production正式経路(選定Prompt→
canonicalization→Master Audio Store経由TTS→ASR Cascade検証)の中で
`VALIDATED`(A2 rank5「not fully match」で実証、後述2節)。**

ただし、本Runでは**B1・A2とも Episode Assembly が Audio Validation Gate
によりブロックされ、完成した1本のepisode音声は生成されていない**
(`USER_FINAL_AUDIO_REVIEW_REQUIRED`に未到達)。2つの独立した原因
(いずれもD4に従いoverride・fallback追加・上限緩和は行わずSTOP)によるもので、
いずれもOPEN-117の分離方式そのものの欠陥ではない(詳細は4節):

- B1 rank2: 表示用glossに含まれる「～」が、本Trialの規則変換の対象範囲
  (文頭・読点直後)**外**の位置(パーセント表記の一部)にあり、意図どおり
  変換されずPlaceholder Gateで正しくSTOPPED(想定内の境界事例)。
- A2 rank2: OPEN-117と無関係な既存の英語Key Phrase TTS/ASR問題(TTSが
  英語の代わりに日本語で発話)でSTOPPED(pre-existing flakiness)。

したがって全体のCloseoutは **`USER_DECISION_REQUIRED`**
(分離方式自体はVALIDATEDだが、Production採用に向けては5節の変換規則の
適用範囲、および完成音声取得のためのA2 rank2再生成承認[human
`REGENERATE_APPROVED`]について、ユーザー判断が必要)。

`APPROVED_FOR_PRODUCTION`・`PRODUCTION_WIRED`はいずれも該当しない
(本タスクでは判定しない)。

## 1. 実施内容・入力

- 本文(article.md): Trial-12 (`er011_output/open112_trend_theme2_b_a2_b1_
  text_trial_12/{b1b_run01,a2_run01}/article.md`)を、Trial-13経由で
  byte一致確認の上コピーして使用(無変更)。
- Support(Preview/Comment1-4)・parts.json: Trial-13の保存済みartifact
  (`er011_output/open112_trend_theme2_b_full_audio_trial_13/{level}/
  {parts.json, {level}_support_texts.json}`)をそのまま再利用(再生成
  しない。理由: LLM呼び出しは非決定的で、再生成するとcanonical_textが
  変わりReview Lockキャッシュが無効化されるため)。
- Key Phrase: **A2/B1とも新仕様下で新たに選定した**(手作業での部分差し
  替えは行っていない)。

### 選定Prompt(Trialコピー)

Production選定Prompt(`er003_v1_translator_briefs/b1_p2_keywords_l_prompt_
template.txt`)を実行時にメモリ上でコピーし、gloss側のplaceholder禁止規約
のうち**「～」「〜」だけ**を明示的に許可する1文へ差し替えた(str.replace
による単一箇所の機械的置換、差分が1箇所だけであることをコードで検証)。
「…」は禁止のまま維持し、規約A(算用数字禁止・漢数字使用)・英語
`key_phrase`側の規約・他の選定基準はすべて無変更。ファイル自体は書き換え
ていない(Production側`b1_p2_keywords_l_prompt_template.txt`は無変更)。

`sc.run_key_phrase_selection()`自体がtemplate引数を外部化していない
(内部で`bk.load_prompt_template()`を無引数のまま呼ぶ)ため、この工程に
限り、`bk.build_user_message`/`bk.make_selector_fn`/`prod.run_production_
selection_gate`(いずれもProduction関数、無変更)を直接同じ手順で呼ぶ
薄いTrial限定wrapper(`trial_run_key_phrase_selection`)を用意した
(monkeypatchは使用していない)。canonicalization・redundancy QAは
`sc.run_key_phrase_canonicalization`/`sc.run_key_phrase_redundancy_qa`
(Production関数)をそのまま呼んだ。

## 2. A2/B1 Key Phrase 5件×(表示用/TTS用/ASR原文/分類/attempts)、原本との比較

原本(Trial-13、規約B[全面禁止]下での選定):

| Level | Rank | 原本 key_phrase | 原本 japanese_gloss |
|---|---|---|---|
| B1 | 1 | story with two different speeds | 2つの異なる速さで進む状況 |
| B1 | 2 | room for one's own pace | 自分のペースで過ごせる余地 |
| B1 | 3 | median of about two nights | 中央値は約2泊 |
| B1 | 4 | point to | ～を示す、～を指し示す |
| B1 | 5 | emerging preference | 現れつつある好み・傾向 |
| A2 | 1 | at one's own pace | 自分のペースで |
| A2 | 2 | median | 中央値 |
| A2 | 3 | room to choose | 選べる余地・自由 |
| A2 | 4 | not fully match | 完全には一致しない |
| A2 | 5 | month off | 1か月丸ごとの休み |

本Trial(Trialコピー選定Prompt下での**新規選定**、5件とも入れ替わった):

| Level | Rank | key_phrase | 表示用gloss | TTS用テキスト | 変換 | EN音声 | JA音声 | ASR書き起こし | 分類 | attempts |
|---|---|---|---|---|---|---|---|---|---|---|
| B1 | 1 | median | 中央値 | 中央値 | なし | OK | OK | 中央地 | PHONETIC_MATCH | 1 |
| B1 | 2 | put solo travel at | ソロ旅行を～％とする | ソロ旅行を～％とする(未変換、範囲外) | なし | OK | **STOPPED** | (TTS未呼出) | (placeholder gate) | 0 |
| B1 | 3 | two different speeds | 異なる二つの進み方 | 異なる二つの進み方 | なし | OK | OK | 異なる二つの進み方 | EXACT_MATCH | 1 |
| B1 | 4 | self-directed travel | 自分主導の旅行 | 自分主導の旅行 | なし | OK | OK | 自分主導の旅行 | EXACT_MATCH | 1 |
| B1 | 5 | interest-led plans | 興味を軸にした計画 | 興味を軸にした計画 | なし | OK | OK | 興味を軸にした計画 | EXACT_MATCH | 1 |
| A2 | 1 | median of 2 nights | 宿泊数の中央値は二泊 | 宿泊数の中央値は二泊 | なし | OK | OK | 宿泊数の中央値は2泊。 | NORMALIZED_MATCH | 1 |
| A2 | 2 | new normal | 新しい当たり前 | 新しい当たり前 | なし | **STOPPED** | OK | 新しいあたりまえ | PHONETIC_MATCH | 1(JAのみ、ENは4回STOP) |
| A2 | 3 | at one's own pace | 自分のペースで | 自分のペースで | なし | OK | OK | 自分のペースで | EXACT_MATCH | 1 |
| A2 | 4 | month off | 一か月の休み | 一か月の休み | なし | OK | OK | 1か月の休み。 | NORMALIZED_MATCH | 1 |
| A2 | 5 | not fully match | ～と完全には一致しない | **なになにと完全には一致しない** | **あり** | OK | OK | 何々と完全には一致しない。 | PHONETIC_MATCH | 1 |

**A2 rank5が本Trialの主目的(先頭「～」→「なになに」変換)の唯一の完全
成功例**(表示用は辞書的な「～と完全には一致しない」のまま保持し、TTS用
テキストだけ「なになにと完全には一致しない」へ変換、Production標準経路
[`generate_a2_japanese_with_reading_safety`、Aoede、Master Audio Store
非対象のKey Phrase日本語meaning経路]でattempt1一発PASS)。Phase 1
(Trial-13 kp4_ja由来の対照Bケースなど)と整合する結果。

**選定結果自体が10件中2件しか「～」を含まなかった**(規約Bを緩めても、
モデルが実際に「～」表記のglossを選ぶ頻度は今回のサンプルでは低かった)。
うち1件(B1 rank2)は変換対象範囲外(パーセント表記のmid-string「～」)
だったため、今回の1回の実行では「変換ルールが実際に発火した」ケースは
1件のみに留まる(サンプル数が少ない点は5節で明記)。

canonicalization QA `REVIEW_REQUIRED`(自動不採用・人間確認後に採用可の
既存運用のまま、無視できない項目ではない):
- B1 rank2「put solo travel at」: 数値補語が`source_span`外にあり
  復元できないため、単独提示では意味理解に限界がある(`qa_standalone_
  natural_unit`等4項目FAIL)。**この英語key_phrase自体が「数値の穴埋めが
  必要な不完全な動詞句」であり、日本語gloss側の「～％」placeholderは
  この不完全さの反映**という関連性がある(偶然ではない)。
- A2 rank3「at one's own pace」: 人称代名詞一般化(`their`→`one's`)に
  伴い、`key_phrase`が`source_span`内の連続文字列でなくなったため
  `qa_traceable_contiguous_span`のみFAIL(既存の標準的なQAパターン、
  Trial-13でも同型の判定が発生済み)。

Key Phrase Set Redundancy QA: B1・A2とも`REDUNDANCY_PASS`(重複ペア0件、
retry不要、初回選定で完結)。

証跡: `er011_output/open117_keyphrase_display_tts_separation_trial_02/
{b1b,a2}/audit/kp_display_tts_map.json`(表示用↔TTS用対応表)、
`{b1b,a2}/audit/tts_generation_results.json`(ASR/attempts詳細)、
`{b1b,a2}/key_phrases/keywords_canonicalized.json`(選定結果全項目)。

## 3. 再利用segment数・新規TTS数・skip logicの動作

- B1: 本文13segment(topic_intro/preview/comment_1-4/point_one_heading/
  point_two_heading/full_story_part1/full_story_part2/point_one/
  point_two/in_one_line)をTrial-13から**再利用**(生成関数を一切
  呼ばず、review_lock RESOLVED確認+canonical text sha256一致検証
  [独立ソース[article.md/parts.json/support texts]から再構成した期待値
  との一致]の上でwav+tts_generation_resultsエントリをコピー)。
- A2: 本文14segment(B1の13 + japanese_title)を同様に再利用。
  japanese_titleのみ、記事本文以外に独立ソースが無いためTrial-13記録値を
  信頼(`TRUSTED_FROM_TRIAL13_RECORD`として明示的にログ)。
- 検証結果: **B1 13/13、A2 14/14 すべて`VERIFIED_MATCH`(またはtitleは
  信頼扱い)、hash不一致による再利用拒否は0件**(`{level}/audit/tts_
  generation_results.json`のsegments、reuse_reportに記録)。
- 再TTS数: **0件**(13/14 segment×2levelとも生成関数呼び出し自体を
  skip、実際にAPIコストがraw_usage_log上も発生していないことを確認)。
- Key Phrase(選定が変わるため常に新規生成): 英語Component10件+日本語
  gloss/meaning10件=20件を新規呼び出し(うち成功18件、STOPPED 2件
  [上記2節])。
- Commentが Key Phrase内容に依存するかの確認: `PREVIEW_ROLE`(B1)は
  「Preview・**Key Phrases**に続いてMain Story…」という**構造上の
  言及のみ**で、実際のKey Phrase文言(gloss等)は一切渡していない
  ことをコード読解で確認(`er003_v1_b1_scaffold_01_generate.py`)。
  Comment 1〜4のcontext_blockも`parts['part1']/part2`/Point見出しの
  みで、Key Phraseへの参照は無い。**依存なし、Comment/Preview再利用は
  安全**と判断した。

## 4. Gate/Lock停止の有無

両方とも発生した。D4に従い、いずれもoverride・fallback追加・上限緩和は
行っていない。

- **B1 rank2「put solo travel at」日本語gloss**: canonical_text=
  `ソロ旅行を～％とする`(TTS用変換規則の対象外の位置に「～」が残存)。
  `generate_charon_japanese_with_reading_safety`内部の
  `detect_gloss_placeholder_notation`ゲートが`found_chars=['～']`を
  検出し、TTS API呼び出し自体を行わずSTOPPED(review_lock storeにも
  記録されない、事前ゲートのため)。**ゲートが正しく機能した**(既存
  OPEN-117-KEYPHRASE-TILDE-GATE-RECHECK-01の結論と整合)。
- **A2 rank2「new normal」英語Component**: 4回(Minimal instruction
  2回+English Language Lock 2回)ともASRが日本語「新常態」("new
  normal"の意味そのものの日本語)として書き起こし、`TTS_FAILURE`分類で
  全滅。`review_lock_state.json`に`kp2_en: HUMAN_REVIEW_REQUIRED`として
  記録された。OPEN-117の変更(gloss側placeholder規約)とは無関係な、
  既存Production側の英語Key Phrase TTS/ASR経路の問題。

いずれもAssembly側の`verify_episode_audio_validation_gate`が
`EPISODE_BLOCKED_BY_AUDIO_VALIDATION`として検知し、B1・A2それぞれ独立に
`RuntimeError`で停止した(D4のとおり、片方が止まっても他方は独立して
試行され、実際に両方とも独立に実行・独立に停止した)。

## 5. Assembly結果

**両レベルとも完成音声なし**(`assembled/`ディレクトリは作成されたが
空、`run_summary_assemble.json`も生成されていない)。総尺・安全弁適用・
file:// URLはこのRunでは提供できない。

代わりに、生成できたKey Phrase音声(英語8件+日本語9件、計17件のwav)と
再利用した本文27segment(B1 13+A2 14)を試聴できるplayerを用意した:

`file:///C:/Users/tensh/eigo-radio/er011_output/open117_keyphrase_display_tts_separation_trial_02/player.html`

(A2/B1それぞれのKey Phrase表[key_phrase英語音声/表示用gloss/TTS用
テキスト/日本語音声/ASR書き起こし/分類/attempts/status]、STOPPED segment
は「音声なし」と明記。episode全体の完成音声が無い理由も明記)。

## 6. retry/fallback/regeneration整合評価

- **B1 rank2(placeholder gate STOP)**: このSTOPは`voice01.generate_
  charon_japanese`(review_lock guard・retry cascade本体)へ到達する
  **前**の事前チェックで発生するため、既存のTTS retry(標準2回+
  fallback1回、計3回)・ASR Cascade・review_lockのいずれとも衝突しない
  (それらの対象にすら入らない)。この停止は**テキスト内容に対する
  決定的な判定**であり、同じテキストで再試行しても常に同じ結果になる
  (retry予算を無駄に消費しない設計。既存仕様のまま)。
- **A2 rank2(英語KP TTS/ASR STOP)**: 既存の`generate_key_phrase_
  component_verified`(Primary 2回+Fallback[English Language Lock]2回、
  計4回)を全て消費した上でreview_lockが`HUMAN_REVIEW_REQUIRED`へ遷移
  した。これは既存Production仕様どおりの正常な終端状態であり、
  `REGENERATE_APPROVED`(人間の明示操作)が無い限り追加のTTS/ASR呼び出し
  はブロックされる(本Trialでは行っていない、D4)。
- **Master Audio Store cache identity**: 英語Key Phrase Component
  (`ensure_key_phrase_english_component`)は`canonical_text=used_form`
  (英語key_phraseそのもの)をキーに使っており、**表示用/TTS用分離の
  影響を受けない**(gloss側[日本語]のみを分離対象にしているため)。
  日本語Key Phrase glossはMaster Audio Store非対象([`generate_charon_
  japanese_with_reading_safety`/`generate_a2_japanese_with_reading_
  safety`はStore経由ではなく都度生成・review_lockのみでguard])のため、
  今回の分離は既存のcache identity設計と矛盾しない。
- **選定retry(Key Phrase Set Redundancy QA)**: 今回は両レベルとも
  初回選定で`REDUNDANCY_PASS`となり、retry(最大2回)は発火しなかった
  (発火時の経路自体はProduction関数`sc.run_key_phrase_canonicalization`/
  `sc.run_key_phrase_redundancy_qa`をそのまま使うため、Trialアダプタが
  介在するのは選定[Prompt差し替え]の1点のみで、retry構造自体への影響は
  無い設計)。
- 結論: **既存のretry/fallback/regeneration機構との矛盾は確認されな
  かった**。分離方式(TTS用テキストへの規則変換)は、既存の安全装置
  (placeholder gate・review_lock・Audio Validation Gate)の手前・内部
  いずれとも整合し、ゲートを弱める効果は無い(むしろ、変換対象外の
  「～」[B1 rank2]をそのままゲートへ通す設計により、ゲートの実効性は
  維持されている)。

## 7. Production採用時に必要な変更一覧(Phase 1からの更新)

Phase 1 Report 5.2節の一覧に対し、Phase 2の実データで以下を追記・確認する。

1. **選定Prompt**: Phase 1では未検証だった「規約Bの一部だけを緩める」
   実装方法が、Phase 2で1文の機械的置換として成立することを確認した。
   Production採用時は、この1文をどう最終化するか(現状のTrial文言の
   まま採用/文言調整)がユーザー判断。
2. **Canonicalization**: `keywords_canonicalized.json`のschema拡張
   (`japanese_gloss`表示用+新フィールドTTS用)は依然未実装(Phase 2でも
   実装していない、read-only経路のみ確認)。
3. **Master Audio Store**: 6節のとおり、英語Key Phrase Componentは
   分離の影響を受けないことをPhase 2の実データで確認した(Phase 1の
   read-only推測を裏付け)。日本語gloss側はStore非対象のため、
   `canonical_text`引数として渡す値を表示用からTTS用へ変更するだけで
   足りる(Phase 1の推測どおり)。
4. **変換規則の適用範囲(Phase 2新規発見)**: 「文頭・読点直後の
   「～」「〜」→「なになに」」という規則変換は、**verb+目的語省略型**
   (「～を示す」等)には有効だが、**数値placeholder型**(「～％」のような
   パーセント・数量の穴埋め)には対応しない(B1 rank2で実例確認)。
   Production採用時は、(a)数値placeholder型は変換規則の対象外のまま
   Gateでブロックし続ける(Key Phrase選定側で数値付き表現を避けるよう
   規約側で誘導する)か、(b)変換規則自体を拡張する(例:
   「～％」→「何パーセントか」等)かの選択がユーザー判断として必要。
5. **review_lock/Assembly**: Phase 2で実際にProduction正式経路
   (`generate_charon_japanese_with_reading_safety`/`generate_a2_
   japanese_with_reading_safety`/`stage_assemble_b1`/`stage_assemble_
   a2`)を無変更のまま通したところ、review_lock・Audio Validation Gate
   とも設計どおりに動作することを確認した(6節)。追加のコード変更は
   不要と判断する。

## 8. cost

本タスク実費(Production標準経路、`er005_cost_logger.install()`経由):

```
total_usd: 0.0571 (約9.14円)
  openai::responses.create (選定+canonicalization+redundancy QA、6 call): $0.0411
  gemini_batch::batches.create (Key Phrase TTS、18 call): $0.01491
  openai_asr::audio.transcriptions.create (ASR、18 call): $0.0011
```

計測: `er011_open117_keyphrase_display_tts_separation_trial_02_cost_
compute.py`(Trial-01と同じBatch tier単価補完パターン)。

Theme 2累計(Trial-11〜17・OPEN-117 Phase 1・本Phase 2、概算): 約
¥125(既存記録)+ ¥9.14(本タスク)= **約¥134**。上限¥1,000に対し余裕
あり(D6条件に抵触せず)。

## 9. Production変更なしの確認

- `er003_v1_translator_briefs/b1_p2_keywords_l_prompt_template.txt`
  (選定Prompt本体): 無変更(Trialコピーはメモリ上の文字列のみ)。
- `er003_v1_translator_briefs/b1_p2_keywords_canonicalization_prompt_
  template.txt`: 無変更。
- `er003_b1_p2_keywords.py`/`er003_key_words_production.py`/
  `er003_key_words_canonicalization.py`/`er011_key_phrase_set_
  redundancy_qa_01.py`: 無変更(直接呼び出しのみ、monkeypatchなし)。
- `er003_v1_n3_01_scaffold_generate.py`/`er003_v1_n3_01_tts_generate.py`/
  `er003_v1_n3_01_assemble.py`: 無変更。
- `er003_audio_tts_asr_safety.py`(placeholder gate本体): 無変更。
- `er011_human_review_lock_01.py`: 無変更。
- `er006_master_audio_store_01.py`/`er006_audio_cost_pilot_02_shared_
  narration.py`: 無変更。
- `keywords_canonicalized.json`スキーマ: 無変更(表示用フィールドのみ、
  TTS用フィールドの追加は未実装)。
- `CURRENT_SPEC.md`: 無変更。
- monkeypatch: 使用していない。
- status格上げ: なし。

## 10. Git

commit hash・push結果は、他の並行タスクとの競合回避のためRESULT_PACKET.md
および最終応答に記載する。

## 11. 証跡

- Trial script: `er011_open117_keyphrase_display_tts_separation_trial_02.py`
- Cost計算script: `er011_open117_keyphrase_display_tts_separation_trial_02_cost_compute.py`
- 出力: `er011_output/open117_keyphrase_display_tts_separation_trial_02/`
  (`{b1b,a2}/key_phrases/*`、`{b1b,a2}/audit/{kp_display_tts_map.json,
  tts_generation_results.json,review_lock_state.json}`、
  `{b1b,a2}/narration/*.wav`、`player.html`、
  `raw_usage_log_open117_trial02.jsonl`、
  `cost_summary_open117_trial02.json`、`trial02_summary.json`)
- Player: `file:///C:/Users/tensh/eigo-radio/er011_output/open117_keyphrase_display_tts_separation_trial_02/player.html`
