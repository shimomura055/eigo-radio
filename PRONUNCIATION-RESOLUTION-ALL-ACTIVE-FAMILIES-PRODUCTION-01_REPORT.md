# PRONUNCIATION-RESOLUTION-ALL-ACTIVE-FAMILIES-PRODUCTION-01_REPORT (Phase 2)

作成: Sonnet実行層。Status起点=`APPROVED_FOR_PRODUCTION`(ユーザー承認済み設計)。
`PRODUCTION_WIRED`判定はFableが行う(本REPORTでは自称しない)。

---

## 1. 現在の状態

Phase 1 recon(`docs/pm/recon_pronunciation_resolution_01.md`)で確認された
「未知語→即HUMAN_REVIEW(JA)」「Ledger/Researchはあるが未配線(EN)」という
2つの根本ギャップに対し、共通core新設・両言語への配線・JA読み照合の補強を
実装し、日英それぞれで実データ/実APIによるruntime evidenceを取得した。
Family X(Meta記事)でのJA-1のみ、並走中のFamily X Stage 3c未完了
(`docs/pm/RESULT_PACKET_FXA4.md`未生成)のため未実施(下記6節)。

## 2. 現行仕様(Phase 1 recon要約、変更なし)

- JA: `DEFAULT_JA_READING_DICTIONARY`(静的・手動追加のみ)+ Foreign Token
  Gate。未登録語は無条件でTTS呼び出し前にHUMAN_REVIEW。
- EN: `extract_proper_nouns`/`research_pronunciations`/Pronunciation
  Ledger/`augment_style_prefix_with_pronunciation`は実装済みだが、
  Production初回TTS経路からは一度も呼ばれていなかった(reactiveなHuman
  Review直前のみ発火、TTSへフィードバックしない設計)。

## 3. 発見した不足(Phase 1に加え、本Phaseの実装・実測で新たに判明)

1. (既知、recon記載どおり)JA側に汎用解決パイプライン・web lookup・
   confidence概念が存在しない。EN側はパイプラインはあるが未配線。
2. **JA ASR読み照合の表層依存バグ(実データで確認)**: `海からの封鎖`
   (canonical)/`海からの風さ`(ASR)で、既存A2 Reading Resolver(LLM)が
   複合語の2文字目以降を文脈なしの孤立読みで再構成してしまい、実際には
   同じ読み(ふうさ)であるにもかかわらず3回連続STOPPEDになっていた
   (`er011_a2_reading_resolver_01._resolve_side`の既知の設計限界)。
3. **既存Ledgerのcase-sensitivity bug(実行時に発見)**: `get_hint_for_text`
   がcase-sensitive一致だったため、reactive lookup由来のentry(surfaceが
   小文字保存、例`"toteme"`)が、本文中の実際の表記(`"Toteme"`)と一致せず、
   EN側を配線しても発火しない状態だった。
4. **回帰試験の副作用(実行時に発見)**: 既存`er009_ja_foreign_token_gate_
   01_test_01.py`の`WiringStopsBeforeTtsCallTests`は「実際のAPI呼び出しは
   発生しない」ことを明言したテストだが、JA resolver配線後は無mockで
   実行すると実際にOpenAI web_searchを呼び、本番Ledgerへ書き込んでいた
   (fixture "Gloobargaxxx" 経由、実測で確認・修正済み)。

## 4. 実施した仕様改修

- Fable設計判断1〜8(委任文記載どおり)を採用。3.9節の3件はユーザーへ
  上げず委任文の指示どおり確定済み(再掲しない)。
- 追加のFable権限内実装判断(通常のモジュール分割・統合順序の裁量、
  ユーザー判断は不要と判断):
  - `er003_audio_tts_asr_safety.py`自体は無改変とし(recon 3.10案からの
    差分)、呼び出し元(`er003_v1_n3_01_tts_generate.py`)側でresolver
    coreを先に呼び、`reading_dictionary`引数を拡張して渡す設計に変更。
    既存Gate関数のシグネチャ・内部ロジック・17件超の既存testへの影響を
    完全にゼロにできるため。
  - EN側「記事レベルでの`extract_proper_nouns()`自動発火」は本Phase未配線
    (残課題、12節)。理由: 自然な配線点はFamily X production runnerだが、
    並走Agent(Stage 3c)との衝突回避のため対象外。代わりに、Ledger
    cache-hit注入(追加API費用ゼロ)と、既存low-confidence entryの
    再research(1プロセス内1回まで)の2つを配線した。

## 5. 実装内容

### 新規モジュール
- `er025_entity_pronunciation_resolver_core_01.py`: JA/EN共通core。
  `confidence_gate()`(high/medium/low → AUTO_USE/ASR_BACKED/HUMAN_REVIEW)、
  `resolve_unknown_ja_tokens()`(JA、cache→Ledger→web lookup[r3.make_
  writer_research_fn再利用]→reading_dictionary動的追加)、
  `resolve_and_augment_en_style_prefix()`(EN、Ledger cache-hit注入+
  low-confidence再research)。
- `er025_entity_pronunciation_resolver_core_01_test.py`: 7 unit test
  (confidence_gate、JA高/低confidence分岐、JA未知語0件時の非発火、
  EN cache-hit時のAPI非発火、EN低confidence再research+同一プロセス内
  dedupe、EN無該当時の非変更)。全PASS(mock使用、API呼び出し0)。

### 既存ファイルの拡張(既存シグネチャ・戻り値schema維持)
- `er006_pronunciation_ledger_01.py`: schema拡張(`ja_reading_katakana`
  等5フィールド、既定値で後方互換)、`get_low_confidence_entries_for_
  text`/`get_ja_reading_entry`/`upsert_ja_reading_entry`新設、
  `get_hint_for_text`と新設関数のsurface一致をcase-insensitive化(3節
  bug修正、一致範囲が広がる方向のみの変更)。
- `er003_v1_n3_01_tts_generate.py`: B1/A2 JA両関数で、Foreign Token Gate
  呼び出し直前にresolver coreを呼び、`reading_dictionary`を拡張。
- `er003_v1_repro01_main_generate.py`: `generate_narration_snippet_
  verified_strict`(EN標準+fallback共通、Key Phrase Component含む全EN
  経路)で、retryループ開始前に1回だけresolverを呼びstyle_prefixを拡張。
  全return path(OK/ASR_VALIDATION_UNCERTAIN/STOPPED)へ
  `en_pronunciation_resolver_info`を記録。
- `er007_ja_asr_validator_01.py`: `_reading_dictionary_token_diff`の
  Latin単一トークン限定を撤廃し、非Latin(漢字/カタカナ)スパン全体が
  `expected_readings`キーと完全一致する場合も対象に追加(既存Latin単一
  トークン判定は無変更)。
- `er011_ja_asr_variant_layer_01.py`: **Candidate E新設**(漢字候補読み
  [pykakasi内蔵辞書]の決定的総当たり、LLM不要、¥0)。既存LLM resolver
  (`READING_RESOLVED_MATCH`)より先に、より安価に同じ結論へ到達できる
  ケースを捕捉する。false accept対策として、適用は「かな正規化後の
  完全一致」のみ、組合せ数上限(64)超過時はfail-safeで諦める。
- `er009_ja_foreign_token_gate_01_test_01.py`/`er011_no18_connected_
  speech_reading_resolver_wiring_08_test.py`: 3節で発見した副作用/挙動
  変化に対応する最小限のtest修正(いずれもコメントで理由を明記)。

### 5-1. Gemini TTS発音指定方法の事実確認(委任文6番、HTTP GET実施済み)

`https://ai.google.dev/gemini-api/docs/speech-generation`(取得日時:
2026-09-27、ページ内`Last updated 2026-09-24 UTC.`と明記)をHTTP GETし
逐語確認した。現行Production model(`gemini-2.5-pro-preview-tts`[EN]/
`gemini-3.1-flash-tts-preview`[JA]、`er003_b1_p9a_audio.py:135,137`で
確認)はこのページの「Migration guide」節で「if you are migrating from
`gemini-3.1-flash-tts-preview` or earlier Gemini TTS models to Gemini
3.8 TTS」と名指しされている旧世代モデルであり、本ページは主に新世代
(Gemini 3.8 TTS、`speech_metadata`構造化annotation方式)を前面にした
内容へ更新済みだった。

**事実(逐語引用)**: 発音制御に関する機構は、ページ全体を通じて
"Turn-level delivery (`speech_metadata.style`): Put sustained delivery
attributes—such as emotion, prosody, overall pace, or delivery
style—into the style field" と "Point-in-time events (inline tags):
Put momentary non-speech vocal bursts, breaths, or pauses inline inside
the transcript using angle brackets (`<cough>`, `<breath>`, `<sigh>`,
`<short pause>`)" の2種類のみで、IPA・phonetic respelling・SSML的な
発音直接指定タグは一切記載が無い(`pronunciat`/`phonetic`/`IPA`/`SSML`
でのgrep結果、該当は本文中の使用例0件)。旧世代(現行Production)の
plain-text style instruction方式についても、Migration guide内で
"Unlike earlier preview models where stage directions were embedded in
plain text" と明記されており、現行実装(`build_tts_prompt(text,
style_prefix)`によるstyle_prefix自然文注記)がまさにこの「旧方式」に
一致することを確認した。

**結論**: 公式機構(構造化されたIPA/発音指定タグ)は現行Productionモデル
・新世代モデルのいずれにも**存在しない**(「未確認」ではなく確認済みの
不在)。既存の自然文style instruction方式(`augment_style_prefix_with_
pronunciation`)を維持する設計判断は妥当。

## 6. 日本語側runtime evidence

| # | fixture | 結果 |
|---|---|---|
| JA-1 | Meta記事(Family X) | **未実施**。並走Family X Stage 3c完了未確認
  (`docs/pm/RESULT_PACKET_FXA4.md`未生成、委任文の代替条件により60分待機
  後に理由記録)。 |
| JA-2 | 合成fixture「多くのデザイナーがFigmaを使って…」(辞書未登録の
  実在企業"Figma") | 検出→web lookup発火(`r3.make_writer_research_fn`、
  実API)→confidence=high(PR TIMES記事を情報源として確認)→自動使用→
  TTS成功(status=OK, asr_verified=True)→Ledger保存(`figma`
  entity_type=`ja_reading_katakana`)→**2回目実行でcache hit・追加
  lookup 0回**(`web_lookup_called: false`)を実測確認。証跡:
  `er025_output/pronunciation_resolution_phase2_evidence_01/ja2_evidence_
  summary.json` |
| JA-3 | Hormuz B1B Key Phrase 2「海からの封鎖」(canonical) vs
  「海からの風さ」(実ASR、3回連続STOPPEDだった実例) | Candidate E新設後、
  `classify_ja_asr_match`が**PHONETIC_MATCH**を返すことを確認(¥0、LLM
  呼び出しなし)。負例3件(「封鎖」→「解放」、「五時」→「後で」、
  「反落」→「半額」)はいずれも従来どおりTRUE_CONTENT_MISMATCHのまま
  (false accept増加なし)。既存regression(er007 39fixture、er011
  open145 regression、er011 no18 15項目)は全PASS(2件の分類ラベル変化
  [READING_RESOLVED_MATCH→PHONETIC_MATCH]をtest側で許容へ更新、
  should_pass=Trueである点は不変)。 |

## 7. 英語側runtime evidence

| # | fixture | 結果 |
|---|---|---|
| EN-1 | 既存Ledger low-confidence実例(`toteme`/`kallmeyer`、実データ:
  `er014_output/user_test_news_light_01/tiny_bags/a2`由来の実文
  "…very large bags appeared at Celine, Altuzarra, Toteme, Stella
  McCartney, and Kallmeyer.") | pre_tts配線後、resolverが発火し
  (`low_confidence_retry_attempted: true`)、Perplexityへ再research
  (実API、$0.00595)。**結果は正直にconfidence="low"のまま**(音声一次
  情報源が実在しないため、fail-safeどおり自動注入なし)。TTS/ASRは
  ASR_VALIDATION_UNCERTAIN(既存ASR Cascadeの対象、本タスクの変更範囲
  外)。証跡: `er025_output/.../en1_evidence_summary.json` |
| EN-2 | 略語fixture「OPEC announced new production targets…」
  (頭字語読みか単語読み"OH-pek"か曖昧) | 既存(無改変)`extract_proper_
  nouns`+`research_pronunciations`で事前投入(記事レベル自動抽出は残課題、
  12節)→confidence=medium→pre_tts cache-hit注入
  (`hints_applied: true`、style_prefixへ"OPEC is pronounced
  approximately OH-pek"相当を追記)→TTS成功→ASR照合PASS
  (`EXACT_MATCH`)。証跡: `er025_output/.../en2_evidence_summary.json` |

各evidenceのmodel_id・routing・費用・latencyは各`*_evidence_summary.json`
+`raw_usage_log*.jsonl`に記録済み(API key/秘密情報は含まない)。合計費用
は上記2件のPerplexity実測($0.00595×1回)+Gemini TTS数回+ASR数回で、
既存Trial実測(TTS-SYMBOL-NORMALIZATION実測¥5.93)と同程度以下の規模
(¥250予算に対し十分小さい、詳細は生ログ参照)。

## 8. Regression

`run_project_regression.py`(3298件、discovery pattern `er0*_test_*.py`)
をTTS実行と分離して単独実行: `collected=3298 passed=3292 failed=4
errors=2`。内訳:
- 既知・無関係(OPEN-192 pre-existing 3件相当): `er003_test_bad.
  FixtureTests.test_case_0`(意図的な自己診断fixture)、
  `test_combined_equals_sum_of_er002_and_er003`、
  `test_p2h_reported_count_matches_er002_plus_er003_at_that_time`、
  `test_p2i_reported_count_matches_er003_at_p2i_era`
  (`er003_test_p2j_investigate.py`、ファイル数集計の既存不整合)。
- 既知(er015相当): `er015_standard_a2_6000_generation_first_trial_01_
  test_01`(loader error)、
  `test_per_file_counts_sum_matches_pattern_discovery`。
- **本タスク起因、想定内**: `test_family_a_files_have_no_working_tree_
  diff`(`er019_family_x_pointless_01_test_01.py`)。共有module
  (`er003_v1_n3_01_tts_generate.py`)の拡張がFamily Aにも及ぶことを検知
  する既存testで、Fable設計判断7で事前に許容された挙動(9節参照)。
新規追加の`er025_*`単体testおよび影響を受けた既存test
(`er006_pronunciation_ledger_01_test.py`/`er006_pronunciation_tts_
injection_01_test.py`/`er007_ja_asr_validator_01_test.py`/
`er009_ja_foreign_token_gate_01_test_01.py`(26件)/`er011_no18_
connected_speech_reading_resolver_wiring_08_test.py`/`er011_open145_ja_
asr_variant_production_wiring_01_regression_run.py`)は個別にも実行し
全PASS。

## 9. Family X/Y/Zへの反映状況

Family X: 共有TTS入口(`er003_v1_n3_01_tts_generate.py`/`er003_v1_
repro01_main_generate.py`)経由で自動的に適用される(Family X固有コード
は無変更、共有moduleをimportするのみ)。Family Y: 未着手のため対象外。
Family Z: 未実装のため、`CURRENT_SPEC.md`「Family Z」節への「新設時は
本resolverを必須適用」の記載案は10節参照(SSOT編集はFableに委ねる)。

## 10. Family A/B/Cを変更していないことの確認

`git diff --stat`で本タスクにより変更されたファイル一覧(全てのFamily
A/B/C固有ファイル[`er012_b_family_voices_*`本体、`er013_family_c_*`
本体等]は0件、含まれるのは共有module 5件+新規module 2件+testファイル
3件のみ):

```
 er003_v1_n3_01_tts_generate.py       (共有、JA TTS入口)
 er003_v1_repro01_main_generate.py    (共有、EN TTS入口)
 er006_pronunciation_ledger_01.py     (共有、Ledger)
 er007_ja_asr_validator_01.py         (共有、JA ASR Validator)
 er011_ja_asr_variant_layer_01.py     (共有、JA ASR追加層)
 er007_ja_asr_validator_01_test.py
 er009_ja_foreign_token_gate_01_test_01.py
 er011_no18_connected_speech_reading_resolver_wiring_08_test.py
 er025_entity_pronunciation_resolver_core_01.py       (新規)
 er025_entity_pronunciation_resolver_core_01_test.py  (新規)
```

上記共有moduleはFamily A(legacy)とも共用のため、Family Aの回帰test
(`er019_family_x_pointless_01_test_01.py::test_family_a_files_have_no_
working_tree_diff`)が「Family Aファイルに無コミットの差分がある」と
検知する(8節)。これは「共有moduleの拡張」であり、`er012_b_family_
voices_production_01.py`/`er013_family_c_*`本体等のFamily A/B/C固有
コードへの変更は0件(`git diff --stat`確認済み、実際に変更ファイル一覧
に含まれない)。

## 11. SSOT・Decision Log・Open Items・Git(記載案、SSOT編集はFable後続)

- `CURRENT_SPEC.md`記載案: 「固有名詞読み解決(JA/EN共通)」節を新設し、
  `er025_entity_pronunciation_resolver_core_01`の役割・confidence基準・
  Family Z新設時の必須適用を明記。
- `OPEN_ITEMS.md`記載案: 「EN側article-level自動抽出の未配線」(12節)を
  新規Open Itemとして起票(STOP条件ではない、通常のフォローアップ)。
- `DECISION_LOG.md`記載案: 本Phase 2実装のFable設計判断1〜8(委任文
  記載どおり)+追加実装判断(5節)を記録。
- Git: 本Phase専用の変更/新規ファイルのみpath指定でadd予定
  (`git add -A`禁止、他Agent進行中ファイル[`CURRENT_SPEC.md`/
  `OPEN_ITEMS.md`/`er019_family_x_*`/`er019_output/*`等]は一切触れない)。

## 12. 残課題

1. **EN側article-level自動抽出の未配線**: `extract_proper_nouns()`を
   記事完成後に自動的に1回呼ぶ配線(recon 3.3節の理想形)は、Family X
   production runnerへの変更が必要だが、並走Agent(Stage 3c)との衝突
   回避のため本Phaseでは実施しなかった。現状は(a)既存Ledger cache-hit
   注入(追加API費用ゼロ)と(b)既存low-confidence entryの1プロセス内
   1回までの再research、の2経路のみ配線済み。新規の未知語(Ledger未
   登録)がEN記事に初出した場合、本Phaseの配線だけでは自動解決されない
   (JA側のような「未知語検出→即web lookup」に相当する経路が無い)。
   次のFamily X関連タスクで、Stage 3c完了後にrunner側へ`extract_proper_
   nouns()`の呼び出しを追加することを推奨。
2. **JA-1(Meta記事)runtime evidence未実施**: 上記6節のとおり。
3. Perplexity/OpenAI web_searchのJA/EN比較Trial(recon 3.9-2、ユーザー
   判断候補とされていたがFableが前者[r3]/後者[Perplexity]採用済みの
   ため通常実装の範囲、追加検証は任意)。

## 13. ユーザー判断が本当に必要な事項のみ(STOP条件該当のみ)

**なし**。信頼できる読み/発音が決定できない場合は既存どおりHUMAN_REVIEW
/低confidence非注入のfail-safeへ自然に倒れており、複数候補の自動選択
不能、有料API/ライセンス判断、既存Production仕様との衝突、大きな
Architecture変更のいずれにも該当しない。12節の残課題は通常のフォロー
アップであり、ユーザー判断を要するSTOP条件ではない。

---

## Gate 3 チェックリスト(recon §3.8の受入条件10項目)

1. 既知語(辞書/Ledger登録済み)は追加API呼び出しなしで即PASS —
   **確認済み**(JA-2 run2、EN-2のcache-hit注入)
2. 未知語かつ高confidence解決可能な語は1回のweb lookupで自動使用・
   TTS成功 — **確認済み**(JA-2 run1)
3. 未知語かつ低confidenceはASR照合で裏付けを試みる —
   **構造上確認済み**(低confidenceは自動注入せず既存ASR経路へ、EN-1で
   再研究試行を実測)
4. 裏付けも失敗した場合のみHUMAN_REVIEW — **確認済み**(unit test、
   既存Gate無改変により継続動作)
5. 解決結果はcoreへ保存され同一記事内・別記事で再利用される —
   **確認済み**(JA-2 run1→run2 cache hit)
6. 既存retry予算(3回)・既存Lock機構を独自に緩めない — **確認済み**
   (`review_lock`/`PRODUCTION_MAX_TTS_ATTEMPTS`等は無変更、resolverは
   retry loop開始前の入力生成にのみ関与)
7. 既存Gate(Symbol Normalization等)との実行順序が壊れない — **確認済み**
   (コード確認: Normalizer→resolver→Foreign Token Gateの順)
8. Family A/B/Cの既存テスト回帰にfailが出ない — **1件の想定内差分のみ**
   (8/10節参照、Family A/B/C固有コードへの変更は0件)
9. 費用が既存予算内(¥250上限目安) — **確認済み**(7節参照、実測は
   予算に対し十分小さい)
10. Web lookup失敗時はfail-safe(既存HUMAN_REVIEWへ) — **確認済み**
    (`research_ja_readings`の例外処理、unit test)
