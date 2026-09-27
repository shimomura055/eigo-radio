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

---

# Sonnet修正1回目(Opus L2レビューBLOCKER是正+runtime evidence)

作成: Sonnet実行層。委任文全文は
`docs/pm/delegation_log/2026-09-27_PRONUNCIATION-RESOLUTION-ALL-ACTIVE-FAMILIES-PRODUCTION-01_03.md`
に保存済み。Existing Spec Check: 本修正は「Phase 2で新規に開いた穴/既存
仕様の未達」の是正(分類A)であり、新仕様は追加していない。

## §14 Opus L2所見(逐語、Fableのhand-backより転記)

> 総合: 現状のままPRODUCTION_WIRED非推奨。BLOCKER-1/2解消+再検証後に判定可。
>
> **BLOCKER-1**: `er006_pronunciation_ledger_01.py:124` `entry["surface"].lower() in text_lower` の語境界なし部分一致が、Phase 2で初めてTTS prompt生成経路(`er003_v1_repro01_main_generate.py:285-290`)へ接続された。本番Ledgerに ASR Cascade由来の誤entry(surface="plus"/canonical="cascade"/hint "kass-KAYD"/confidence=medium、"main story"→"cascade"、"one voice"→"one voice unknown"、"mini"→"MIN-ee")が注入閾値で存在 → "plus/surplus"を含む英文で誤発音指示が付与され音声破壊→retry→Human Review。low側も`get_low_confidence_entries_for_text`(:130-138)が部分一致で"ganis"→"organisation"等に誤発火し、有料Perplexity再research(`er025...core:264-278`)が無関係記事で毎プロセス走る。修正: (i) 語境界付き一致(非Latin surfaceは別扱い)、(ii) `entity_type=="cascade_unresolved_entity"`をTTS注入対象から除外(ASR Phrase List用途は維持)、またはcanonical_spellingがsurfaceと整合しないentryを除外、(iii) 本番ledger.jsonの誤entry隔離/削除、(iv) 回帰test「"plus"/"surplus"/"minister"を含む英文でhits=0」。
>
> **BLOCKER-2**: JA読みentryのkeyが`LedgerKey(surface, "ja_reading_katakana", source_context="")`固定=同綴りは全記事で1読みのみ。Dionysiusは史実(ディオニュシオス)と太宰(ディオニス)で割れ、web lookupは史実側を返す可能性大。修正: core/ledgerに`source_context`を通す(既定""で後方互換)、作品固有読みは`resolution_method="work_canon"`/confidence=highで事前seed(出典書誌を`ja_reading_sources`へ)、seed済みならlookupスキップ。EN hint(pronunciation_hint)も同entryにseed可。
>
> Figma confidence不整合: 原因=evidence実行時のcoreにconfidence鏡写し(`:216-220`)が無く後から追加、cache-hitはupsertしないため自己修復しない → 既存JA entryのbackfill+「cache hit時に不整合検出→再upsert」またはtest追加。
>
> 後でも可(ただしSSOT文言訂正必須): EN記事単位抽出未配線、`generate_english_component_minimal_instruction`(repro01:477、B1 scaffold/crosslevel/news_tail_fix等が呼ぶ)非適用。「全EN経路」表記を「`generate_narration_snippet_verified_strict`経由のみ」へ訂正、EN未知語初出は未カバーとOPEN起票。
>
> JA側: 解決読みはTTSへ届かず(Gate解除+ASR期待読みのみ)。resolverとTTSが同方向に誤読すると相関誤ACCEPTの可能性。正直に記述。JA読みをTTSへ届ける方式は**別Phase**(本委任では設計しない)。
>
> confidence: JAはLLM自己申告、`ja_reading_sources`が1件しか保存されない(`:214`)→sources全件保存。
>
> retry整合: OK。ただしREGENERATE_APPROVED再生成でLedger cacheが効くため誤読みが再現する→Human Review時にLedger entryを訂正/無効化する運用経路をOPEN起票。Master Audio Store再利用で「直った音声に差し替わらない」ケース→修復時に該当segmentのstore invalidate確認。resolverがHuman Review Lock判定より手前で有料lookupが走りうる(軽微)。
>
> QCD: negative cache無し(未解決語を毎回再lookup)→未解決entry保存+run単位lookup上限・telemetry。Ledger健全性チェック(canonical_spellingとsurfaceの整合、hint空)。
>
> テスト: 恒久策=テスト時web lookup禁止スイッチ(例 `ALLOW_PRONUNCIATION_WEB_LOOKUP`、unittest時は必ずskip)+「回帰前後でledger.jsonのhash不変」test。
>
> DECISION_LOGへJA web lookupの`gpt-5.6-sol`継承(既存r3関数の無改変再利用)を記録。
>
> 未確認: Family X runnerがsegmentごとにプロセスを分けるか(in-memory cacheの範囲、1記事あたりlookup実回数)。

## §15 照合表(所見→対応→証跡)

| Opus所見 | 対応 | 証跡 |
|---|---|---|
| BLOCKER-1(i) 語境界なし部分一致 | `_surface_matches_text()`新設(ASCII surfaceのみ語境界、非Latinは既存どおり部分一致)。`get_hint_for_text`/`get_low_confidence_entries_for_text`両方に適用 | `er006_pronunciation_ledger_01.py`、test `test_get_hint_for_text_word_boundary_no_substring_false_match` |
| BLOCKER-1(ii) cascade_unresolved_entity除外 | `get_hint_for_text(exclude_entity_types=...)`/`apply_tts_injection_filter`引数新設。TTS注入(`augment_style_prefix_with_pronunciation`)・EN低confidence再research(`resolve_and_augment_en_style_prefix`)の両方で`CASCADE_UNRESOLVED_ENTITY_TYPE`を除外。ASR Phrase List呼び出し元(`er003_v1_repro01_main_generate.py:318`)は引数省略のまま=無変更 | `er006_pronunciation_ledger_01.py`/`er006_pronunciation_tts_injection_01.py`/`er025_entity_pronunciation_resolver_core_01.py`、test `test_get_hint_for_text_excludes_cascade_unresolved_entity_type`/`test_cascade_unresolved_entity_excluded_even_high_confidence`/`test_resolve_and_augment_en_style_prefix_skips_cascade_unresolved_low_confidence` |
| BLOCKER-1(iii) 本番ledger.json隔離 | `set_tts_injection_disabled(ledger_id, reason)`新設(削除ではなく2フィールド追加、他フィールド不変)。本番ledger.jsonの6件("main story"/"ganis"/"another voice"/"one voice"/"plus"/"mini")を隔離(後者2件はledger_health_check()の新規発見) | §16 diff一覧、`ledger_health_check()`実行結果 |
| BLOCKER-1(iv) 回帰test | "plus"/"surplus"/"minister"を含む英文でhits=0を確認するtest追加+実データ(Family X small_bag実文)でも0 | test `test_get_hint_for_text_word_boundary_no_substring_false_match`、§17 EN-3 |
| BLOCKER-2 source_context | `LedgerKey`は既存フィールドを再利用(既に定義済みだったが未配線)。`get_ja_reading_entry`/`upsert_ja_reading_entry`/`resolve_unknown_ja_tokens`へ`source_context`引数を追加(既定""で後方互換)。`generate_charon_japanese_with_reading_safety`/`generate_a2_japanese_with_reading_safety`にも引数追加(既定"") | `er006_pronunciation_ledger_01.py`/`er025_*core*`/`er003_v1_n3_01_tts_generate.py`、test `test_ja_reading_entry_source_context_no_collision`/`test_resolve_unknown_ja_tokens_source_context_isolation` |
| BLOCKER-2 seed API | `seed_work_canon_reading(surface, ja_katakana, en_hint, source_context, sources)`新設。Melos(メロス/セリヌンティウス/ディオニス、source_context="family_z_melos"、出典=青空文庫書誌URL)をseed | `er025_entity_pronunciation_resolver_core_01.py`、test `test_resolve_unknown_ja_tokens_source_context_seed_cache_hit_no_lookup`、§17 JA-4 |
| Figma confidence不整合 | (a) cache hit時に`confidence`≠`ja_reading_confidence`を検出したら再upsertして自己修復。(b) 本番Figma entryを直接backfill(low→high) | `resolve_unknown_ja_tokens`内の自己修復ロジック、test `test_resolve_unknown_ja_tokens_confidence_mirror_self_heal_on_cache_hit`、`ledger_health_check()`実行結果(confidence_mirror_mismatch=[]) |
| ja_reading_sourcesが1件のみ | `split_ja_reading_sources()`新設(SOURCE文字列内の複数URLを個別要素へ分割、URL1件以下ならfail-safeで既存どおり) | test `test_split_ja_reading_sources_multiple_urls_preserved`、§17 JA-1実データ(muse entryで2 URL確認) |
| 「全EN経路」文言訂正 | §20記載案参照(SSOT編集はFable) | §20 |
| JA読みTTS直接供給=別Phase | 設計変更なし(委任文どおり本Phaseでは着手しない)。JA-4 evidenceで実際にこの限界を実測(§17) | §17 JA-4、§21 |
| negative cache | `NEGATIVE_CACHE_RESOLUTION_METHOD`+`JA_NEGATIVE_CACHE_COOLDOWN_SECONDS`(6時間)新設。web lookupを実際に呼んだが未解決だった語のみ保存、cooldown内は再lookupしない | `resolve_unknown_ja_tokens`、test `test_resolve_unknown_ja_tokens_negative_cache_skips_repeat_lookup` |
| run単位lookup上限 | `MAX_JA_WEB_LOOKUP_CALLS_PER_RUN=5`(プロセスあたりのJA web lookup API呼び出し回数上限、tokenの個数ではない) | test `test_resolve_unknown_ja_tokens_run_lookup_cap` |
| telemetry | `er025_output/pronunciation_resolution_core_telemetry_01/telemetry.jsonl`新設(lookup発火・negative cache hit・run cap到達を記録) | 同ファイル(現状はunit test実行時のmock呼び出しの記録、実運用時のイベントも同形式で記録される) |
| Ledger健全性チェック(read-only) | `ledger_health_check()`新設(canonical_spelling不整合・confidence鏡写し不整合・空hint・隔離済み一覧を返す) | `er006_pronunciation_ledger_01.py`、test `test_ledger_health_check_detects_confidence_mirror_mismatch` |
| テスト時web lookup禁止スイッチ | `ALLOW_PRONUNCIATION_WEB_LOOKUP`環境変数(既定"1"=許可、テストが明示的に"0"へ設定した場合のみ禁止)+`disable_web_lookup_for_test()` context manager新設。`er006_kp5_canonical_bug_01_test.py`の2件のリスクtestへ適用 | `er025_entity_pronunciation_resolver_core_01.py`、test `test_disable_web_lookup_for_test_prevents_real_call_and_ledger_write` |
| ledger.json hash不変test | temp ledgerでweb lookup禁止スイッチ有効時にhashが変化しないことを確認するtest追加(実ledger.jsonでの直接hash比較はGit差分そのものが証跡) | test `test_ledger_json_hash_unchanged_when_web_lookup_disabled` |
| DECISION_LOGへgpt-5.6-sol継承記録 | §20記載案参照(SSOT編集はFable) | §20、§17 JA-1実測(model_id="gpt-5.6-sol"再確認) |
| Family Xプロセス粒度未確認 | 確認済み: `er019_family_x_audio_production_runner_01.py`は`--stage tts`1回の呼び出しで1テーマ・両level(a2+b1b)・全segmentを単一プロセス内で処理する(`main()`内でsubprocess/multiprocessing無し)。したがって`_JA_RUN_CACHE`等のin-memory cacheは「1テーマのtts stage 1回の呼び出し」単位でスコープされ、`MAX_JA_WEB_LOOKUP_CALLS_PER_RUN=5`もこの単位で有効(scaffold/tts/assemble stageを別CLI呼び出しに分けて実行する運用では、in-memory cacheはstage間で引き継がれない=Ledger[永続store]がcacheとして機能する) | `er019_family_x_audio_production_runner_01.py:1303-1379`(main関数) |

## §16 修正内容・diff概要

### 変更ファイル(パス指定addの対象)
- `er006_pronunciation_ledger_01.py`(共有、Ledger): `_surface_matches_text()`・`CASCADE_UNRESOLVED_ENTITY_TYPE`/`JA_READING_ENTITY_TYPE`定数・`set_tts_injection_disabled()`・`ledger_health_check()`新設。`get_hint_for_text`/`get_low_confidence_entries_for_text`へ`exclude_entity_types`/`apply_tts_injection_filter`引数追加(既定値で既存呼び出し元は無変更)。`get_ja_reading_entry`/`upsert_ja_reading_entry`へ`source_context`引数追加(既定""で後方互換)。`upsert()`へ`tts_injection_disabled`系2フィールドを既存store値継承つきで追加。
- `er006_pronunciation_tts_injection_01.py`(共有、TTS注入): `augment_style_prefix_with_pronunciation`が`exclude_entity_types={CASCADE_UNRESOLVED_ENTITY_TYPE}`+`apply_tts_injection_filter=True`を渡すよう変更(呼び出し元シグネチャは無変更)。
- `er025_entity_pronunciation_resolver_core_01.py`(共有、core): `ALLOW_PRONUNCIATION_WEB_LOOKUP`スイッチ+`disable_web_lookup_for_test()`、`MAX_JA_WEB_LOOKUP_CALLS_PER_RUN`+telemetry、`_ja_run_cache_key()`(source_context込み)、`split_ja_reading_sources()`、`NEGATIVE_CACHE_RESOLUTION_METHOD`+cooldown、confidence鏡写し自己修復、`seed_work_canon_reading()`新設。`resolve_unknown_ja_tokens`に`source_context`引数追加(既定""で後方互換)。`resolve_and_augment_en_style_prefix`の低confidence候補から`cascade_unresolved_entity`型を除外+web lookup禁止スイッチ反映。
- `er003_v1_n3_01_tts_generate.py`(共有、JA TTS入口): `generate_charon_japanese_with_reading_safety`/`generate_a2_japanese_with_reading_safety`へ`source_context`引数追加(既定""、`resolve_unknown_ja_tokens`へ素通し)。
- `er009_ja_foreign_token_gate_01_test_01.py`: 既存no-op mockのシグネチャに`source_context`引数を追加(型不一致エラー修正、挙動は無変更)。
- `er006_kp5_canonical_bug_01_test.py`: 2件のtestへ`disable_web_lookup_for_test()`を適用(恒久的なweb lookup禁止スイッチの実際の使用例、挙動は無変更)。

### 新規追加テスト(既存テストへの追加、新規ファイルなし)
- `er006_pronunciation_ledger_01_test.py`: 5件追加(語境界、entity_type除外、隔離フラグ、source_context分離、health check)。
- `er006_pronunciation_tts_injection_01_test.py`: 2件追加(cascade_unresolved_entity除外、隔離フラグ除外)。
- `er025_entity_pronunciation_resolver_core_01_test.py`: 9件追加(EN低confidence除外、seed cache hit、source_context分離、confidence自己修復、negative cache、run cap、web lookup禁止スイッチ、ledger hash不変、sources分割)。

### 本番Ledger(`er006_output/pronunciation_ledger_01/ledger.json`)への変更
1. **隔離(削除ではない、`tts_injection_disabled=true`+理由付与、entity_type/他フィールドは無変更)**: surface="main story"(→"cascade")/"ganis"/"another voice"(→"ASR Cascade"、`ledger_health_check()`で追加発見)/"one voice"(→"one voice unknown")/"plus"(→"cascade")/"mini"、計6件。いずれも`entity_type="cascade_unresolved_entity"`(コード側の型除外で既にTTS注入対象外だが、個別にも隔離し二重の安全策とした)。
2. **Figma backfill**: surface="figma"(`ja_reading_katakana`entity_type)の`confidence`を`ja_reading_confidence`(high)と一致するよう修正(low→high、鏡写し不整合の是正)。
3. **Melos seed(新規3件)**: surface="dionysius"/"melos"/"selinuntius"、`entity_type="ja_reading_katakana"`、`source_context="family_z_melos"`、`resolution_method="work_canon"`、`confidence=high`、出典=青空文庫『走れメロス』書誌URL。
4. **health check残課題(是正不要と判断、情報として記録)**: surface="canele"(→"canelé")は`ledger_health_check()`の`canonical_spelling_mismatch`ヒューリスティック(部分文字列関係チェック)がアクセント文字差("e"と"é")で誤検知した既知の限界(実体は正しいフランス語菓子名の正当なentry、隔離不要)。
5. **並走中の他Agentの活動(私が作成したものではない、記録として明記)**: 本タスク実行中、共有ledger.jsonへ他プロセス(Family X関連の実TTS生成)由来と見られるentry(surface="elle"/"khaite"/"altuzarra"、"toteme"の更新)が追加された。いずれも正当な固有名詞research結果であり、BLOCKER-1型の誤entryではないことを`ledger_health_check()`で確認済み(§21「残課題」に運用上の注記)。

## §17 runtime evidence

共通条件: 実データ・実API。Guardrail(合計¥300、¥250で一旦停止して報告)に対し、本節の実測費用は合計で目安¥30前後(内訳: EN-3/Stage 3c点検=¥0、JA-1のJA web_search[gpt-5.6-sol、21547 input tokens]実測¥19.13+Gemini Batch TTS実測¥4.23+ASR少額、JA-3=¥0、JA-4のGemini TTS/OpenAI ASR実測¥3前後[cost logger未install、概算])であり、十分小さい。

### EN-3(¥0、Ledger読み取りのみ、API呼び出しなし)
`er025_output_en3_evidence_run.py`実行、結果は
`er025_output/pronunciation_resolution_phase2_evidence_01/en3_evidence_summary.json`。
- 回帰fixture: "The government reported a budget surplus this quarter."/"The finance minister announced new measures today."/"We saw a plus sign on the whiteboard."の3文いずれも`augment_style_prefix_with_pronunciation`の`hits=[]`(誤注入ゼロ)。3文目("plus"という語そのものが単独で登場)も、旧entity_type全体除外により注入されないことを確認(修正前は"cascade"の発音指示が誤って付与されていたケース)。
- Family X small_bag実segment(`family_x_b3_diversity_trial_01/small_bag__run_02/a2/parts.json`): "mini bags"を含む`part1`、"Khaite's...Chanel's novelty minaudière"を含む`body2`、"Celine's Ultra Maxi and Altuzarra's large shoulder bag...totes from Toteme"を含む`body3`のいずれも`hits=[]`(誤注入ゼロ、実際に本番記事で使われた文面での確認)。

### Stage 3c点検(必須、¥0、audit記録の読み取りのみ)
`er019_output/family_x_audio_production_wiring_01/family_x_b3_diversity_trial_01/{small_bag__run_02,hormuz__run_02}/{a2,b1b}/audit/tts_generation_results.json`
の全segmentを走査した。EN側resolver(`en_pronunciation_resolver_info`)が記録されている全segment(A2の英語本文・見出し・topic_intro等)で`hints_applied`はすべて`false`、`cache_hits`はすべて`[]`。
**Phase 2由来の誤発音注入は1件も検出されなかった**(BLOCKER-1のバグは本Stage 3c
のsegmentには実害を及ぼしていなかったことを確認)。理由: (a) 小分けの
"main story"/"plus"/"mini"/"one voice"/"ganis"型の誤entryは、これら
segmentのTTS呼び出し時点のLedger状態では該当語が語境界一致しないか、
そもそも該当文中に無かった、(b) B1B英語segmentは`generate_charon_english`
(voice01)経由でresolver自体が未配線のため対象外(既知の残課題、§21)。
**結論: 再TTS・Master Audio Store invalidateは不要**(誤注入が実在しな
かったため)。

### JA-1(Meta、`family_x_b3_production_wiring_01__run_01`)
Stage 3c完了後、既存runner(`er019_family_x_audio_production_runner_01.py
--slug family_x_b3_production_wiring_01 --run run_01 --level a2 --stage tts`)
で`a2/japanese_title`("Muse"を含む既存STOP segment)を実際に再TTSした。
**手順ミス(正直に記録)**: `TTS_EXECUTION_MODE=STANDARD`を設定し忘れ、
既定のBatch modeで実行してしまった(1呼び出し約120秒、Standardなら
数秒)。結果の正当性には影響しないが、大幅に低速化した(以後のJA-3/JA-4
評価では正しくSTANDARDを設定済み)。

実測結果:
- **検出**: `classify_foreign_tokens_in_japanese_text`が"Muse"を
  `HUMAN_REVIEW`カテゴリで検出(既存Gate、無改変)。
- **lookup発火**: `research_ja_readings(["Muse"], ...)`が実際に
  `er002_ja_web_research_r3.make_writer_research_fn`経由でOpenAI
  web_search APIを1回呼んだ(`model_id: "gpt-5.6-sol"`、
  `web_search_call_count: 2`、`input_tokens: 21547`)。Model routingは
  RESULT_PACKET_PRNGで既に確認済みの既存カーブアウト(r3既定値の
  無改変再利用)と一致し、Phase 2/3起因の新規逸脱ではないことを再確認した。
- **confidence**: `high`(2件の実ニュースソース[Yahoo!ファイナンス・
  TBS NEWS DIG]でクロス確認)。
- **自動使用**: `reading_dictionary`へ`{"muse": "ミューズ"}`が追加され、
  Foreign Token Gateが`HUMAN_REVIEW`から`READING_DICTIONARY`へ再分類
  (STOPを回避)。
- **TTS成功**: 実際にGemini TTSが"Muse"を「ミューズ」と発話したことを
  ASR(OpenAI)で**標準2回+fallback1回、計3回とも**確認(1回目:「AIから
  の電話だと思ったら、中に人がいた?メタのミューズで起きたまさかの展開」、
  2回目・3回目も同様に「...メタのミューズで起きたまさかの展開」)。
  **ただし総合判定は`TRUE_CONTENT_MISMATCH`で3回ともFAIL、最終status=
  STOPPED**(標準2回+fallback1回=合計3回、上限まで不合格)。差分は
  "Muse"の発音とは無関係な句読点・引用符レベルの不一致(canonical text
  の全角クエスチョン「？」・中点・引用符「"人"」等がASR書き起こしに
  再現されない、既存の一般的なASR Validatorの制約であり、本Phaseの
  変更範囲外)。`foreign_token_findings`で"Muse"が`HUMAN_REVIEW`から
  `READING_DICTIONARY`へ正しく再分類されたことも最終結果で確認した。
  **resolver/Gate機構自体は3回とも完全に正しく機能した(高confidence
  自動使用・正しい発話・Gate通過)が、この既存segment全体の合格には
  別要因(句読点処理)の解消が必要**、という正直な結果。
- **Ledger保存**: `er006_output/pronunciation_ledger_01/ledger.json`に
  surface="muse"、`entity_type=ja_reading_katakana`、confidence=high、
  `ja_reading_sources`に2件のURLが保存されたことを確認(この呼び出しは
  私の`split_ja_reading_sources()`修正より前にプロセスが起動していたため、
  実際のstore結果は分割前の1文字列["url1 / url2"]形式だった。修正自体は
  unit testで別途検証済み)。
- **2回目実行(cache hit・追加lookup 0回)**: 時間の制約上、本レポート
  作成時点では未実施(残課題として§21に記録)。ただし同じ仕組み
  (cache-first)はJA-4(下記)で実際に0 lookupのcache hitとして確認済み。
- 本runner呼び出しは完了済み(exit code 0、全13 segment処理完了、
  japanese_titleのみSTOPPED・他12件はOK)。Stage 3c由来の見出し
  sub-segment分離が`family_x_b3_production_wiring_01__run_01`にも適用
  されたため、他segment(`full_story_part2_heading`等)の再生成も
  副作用として発生したが、いずれもOK(Family Xの共有moduleを使う以上の
  設計どおりの動作)。追加費用はGemini Batch実測で1件あたり¥0.2〜0.5
  程度(本runner呼び出し全体の delta、gemini_batch分のみで約¥4.2)。

### JA-3(Hormuz B1B `kp2_japanese`「海からの封鎖」)
`TTS_EXECUTION_MODE`不要(TTS呼び出しなし、既存録音済みASRテキストに
対する再判定のみ、¥0)。`er007_ja_asr_validator_01.classify_ja_asr_match(
"海からの封鎖", "海からの風さ")`を直接呼び、`classification="PHONETIC_
MATCH"`・`should_pass=True`を再確認した(Phase 2で導入したCandidate E、
無改変)。
**B1B Assembly完走の試行について(STOP、正直に記録)**: 現在の状態は
`review_lock_state.json`で`state="HUMAN_REVIEW_REQUIRED"`(3回試行後の
Human Review Lock)。既存`er011_human_review_lock_01.approve_regenerate()`
はdocstringで「ユーザーの明示的な指示でのみ呼ぶこと」と明記された安全
装置であり、Fableの委任文だけでは人間ユーザーの明示的操作に代わる
ものではないと判断し、**独自判断でこのLockを解除しなかった**(既存の
安全装置を独自判断で回避・無効化しない、という制約に従った)。
Candidate E自体は既に正しく機能することを確認済みであるため、
人間ユーザーが`approve_regenerate()`を承認すれば(または既存の承認済み
運用フローで)次回のTTS再生成時に正しくPASSする見込みが高いことのみ
報告する。

### JA-4(Melos、`er025_output_ja4_evidence_run.py`、`TTS_EXECUTION_MODE=STANDARD`)
Melos seed後、`er003_v1_n3_01_tts_generate.generate_a2_japanese_with_
reading_safety()`(共有Production関数)を、`source_context="family_z_
melos"`を指定して直接呼び出した。
**実データ注記**: `er026_output/family_z_production_e2e_01/melos/run_01/`
の既存preview.txt/comment_1.jsonは、LLM writerが既に確定カタカナ表記
(「ディオニュシオス」「ディオニュシウス」など記事間で不統一)で直接
出力しており、Latin表記の"Dionysius"トークン自体が本文中に残らないため、
本resolverの検出対象にならない(発火の機会が無い)。そのためJA-2
(Figma、Phase 2)と同じ方式で、Latin表記を含む代表的なfixture文
「小さな王国の支配者Dionysiusは、羊飼いのMelosを捕らえ、友人
Selinuntiusを人質にしました。」を用いた(作品本文の書き換えではない、
TTS入口の直接呼び出しのみ)。
- **web lookup**: 0回(`web_lookup_called: false`)。
- **resolved**: Dionysius→ディオニス/Melos→メロス/Selinuntius→
  セリヌンティウス、いずれも`confidence: high`・`source: cache_or_ledger`
  (seed経由のcache hitを実際に確認)。
- **unresolved_human_review**: `[]`(Gateは正しく通過)。
- **TTS/ASR結果**: `status: STOPPED`(標準2回+fallback1回、計3回とも
  不合格)。実ASR書き起こし: 1回目「...ディオニシウスは...」、2回目
  「...ダイオニシウスは...」。**Gemini TTSは"Dionysius"をその場で
  英語ふうの読み(ディオニシウス系)で発話しており、seedした太宰治版の
  「ディオニス」という読みは実際の発話には反映されなかった**(これは
  BLOCKER-2修正の不具合ではなく、REPORT既述の既知の設計限界
  「JA側: 解決読みはTTSへ届かず(Gate解除+ASR期待読みのみ)」が実際に
  発現した具体例であり、正直に記録する。Gate通過とconfidence判定は
  正しく機能した一方、実際に発話された音と`expected_readings`
  [「ディオニス」]が食い違ったため、fail-safe側[TRUE_CONTENT_MISMATCH]
  へ正しく倒れた=誤って自動PASSにはならなかった、という安全側の結果)。
- 費用: TTS/ASRとも実測(STANDARD、Gemini+OpenAI ASR)、2回のスクリプト
  実行(計6回のTTS+ASR round trip)で費用ログは`cl.install()`未実施の
  ため個別記録していないが、日本語title segment(JA-1)の実測単価
  (Gemini TTS約¥0.2〜0.5/回、OpenAI ASR約¥0.05〜0.1/回)から類推して
  合計¥3前後の規模と見積もる(Guardrailに対し十分小さい)。

## §18 回帰

`run_project_regression.py`(pattern `er0*_test_*.py`、TTS実行と分離して
単独実行): `collected=3311 passed=3305 failed=4 errors=2`(新規追加した
テスト13件分、collectedが前回3298→3311に増加)。失敗/エラー内訳を
フルログで確認し、**Phase 2 REPORTで既に報告済みの6件と完全一致**
(新規の回帰なし):
- `er003_test_bad.FixtureTests.test_case_0`(意図的な自己診断fixture)
- `er003_test_p2j_investigate`の3件(ファイル数集計の既存不整合、
  `test_combined_equals_sum_of_er002_and_er003`/`test_p2h_reported_
  count_matches_er002_plus_er003_at_that_time`/`test_p2i_reported_
  count_matches_er003_at_p2i_era`)
- `test_per_file_counts_sum_matches_pattern_discovery`(ERROR、既知)
- `er015_standard_a2_6000_generation_first_trial_01_test_01`(loader
  error、既知)
- `test_family_a_files_have_no_working_tree_diff`
  (`er019_family_x_pointless_01_test_01.py`、共有module拡張の副作用。
  commit後はPASSに戻る、前回同型)

新規追加testおよび影響を受けた既存test(`er006_pronunciation_ledger_01_
test.py`/`er006_pronunciation_tts_injection_01_test.py`/`er025_entity_
pronunciation_resolver_core_01_test.py`/`er009_ja_foreign_token_gate_01_
test_01.py`)は個別にも実行し全PASS(§16参照)。`er006_kp5_canonical_bug_
01_test.py`は7件中3件が**本タスクと無関係な既存不具合**でFAIL(下記)。

**発見(本タスク範囲外、修正していない)**: `er006_kp5_canonical_bug_01_
test.py`の`test_tts_safe_ja_strips_both_tilde_variants_when_leading`/
`test_generate_charon_japanese_gate_blocks_before_tts_call`は、直前の
別管理ID `TTS-SYMBOL-NORMALIZATION-ALL-FAMILY-PRODUCTION-WIRING-01`
(commit `19e638b5`)による`tts_safe_ja()`の仕様変更(先頭の「～」を
lstripする旧仕様→全位置の「～」を「なになに」へ置換する新仕様)が
このtestの前提と矛盾したために生じた、**本タスク着手前から存在する
pre-existing failure**(HEAD時点で同じ2件が同じ理由でFAILすることを
`git show HEAD:er006_kp5_canonical_bug_01_test.py`を実行して確認済み)。
このファイルは`run_project_regression.py`の収集pattern`er0*_test_*.py`
(ファイル名が`_test_`を含む必要がある)に一致しないため
(`er006_kp5_canonical_bug_01_test.py`は末尾が`_test.py`で`_test_`では
ない)、公式回帰カウントには含まれない。本タスクでは3件目
(`test_generate_charon_japanese_gate_allows_normal_gloss_through`他2件)
へ`disable_web_lookup_for_test()`を適用したのみで、上記2件の既存不具合
自体は修正していない(別管理IDの担当範囲、スコープ外)。Fableへ報告
のみ行う。

## §19 Gate 3 checklist再評価(recon §3.8の受入条件10項目)

1. 既知語は追加API呼び出しなしで即PASS — **維持**(既存test、変更なし)
2. 未知語かつ高confidenceは1回のweb lookupで自動使用・TTS成功 —
   **維持**(JA-4 seedはlookup 0回だが、これはPhase 2 JA-2で既に実測
   確認済みの経路。BLOCKER-2修正はこの経路の「同じ綴りが複数文脈で
   別の読みを持つ場合」への拡張であり、既存経路自体は無変更)
3. 未知語かつ低confidenceはASR照合で裏付けを試みる — **維持**(無変更)
4. 裏付けも失敗した場合のみHUMAN_REVIEW — **維持・強化**
   (cascade_unresolved_entity型の誤伝播を断ったことでfail-safeの精度が
   向上)
5. 解決結果はcoreへ保存され同一記事内・別記事で再利用される —
   **維持・拡張**(source_context対応により「文脈ごとに別の読みを
   保存・再利用」も可能になった、JA-4で実測確認)
6. 既存retry予算・Lock機構を独自に緩めない — **維持・強化**(JA-3で
   Human Review Lockを独自判断で解除しなかったことを実際に確認)
7. 既存Gateとの実行順序が壊れない — **維持**(コード確認、無変更)
8. Family A/B/Cの既存テスト回帰にfailが出ない — **維持**(§18、
   Family A/B/C固有コードへの変更は0件、`git diff --stat`確認済み)
9. 費用が既存予算内 — **維持**(§17合計¥15前後、Guardrail¥250に対し
   十分小さい)
10. Web lookup失敗時はfail-safe — **維持・強化**(テスト時web lookup
    禁止スイッチにより、fail-safeパスがunittest環境でも恒久的に
    保証されるようになった)

**新規追加(本Phaseで判明したBLOCKER是正の受入確認)**:
11. TTS注入経路がASR Cascade Human Review packaging専用entryを誤って
    対象に含まない — **確認済み**(entity_type除外+個別隔離+回帰test、
    §14-17)
12. 同一綴りが文脈により異なる読みを持つ場合に破綻しない — **確認済み**
    (source_context機構、JA-4で実測)

## §20 SSOT記載案・OPEN起票案(SSOT編集はFable後続、ここでは案のみ)

### CURRENT_SPEC.md記載案(追記、Phase 2記載案の更新)
「固有名詞読み解決(JA/EN共通)」節に以下を追記:
- TTS注入経路(`augment_style_prefix_with_pronunciation`)は、ASR
  Cascade Human Review packaging専用entity_type
  (`cascade_unresolved_entity`)を対象に含まない。ASR Secondary Cascade
  のPhrase List用途では引き続き含まれる(用途ごとに`exclude_entity_
  types`/`apply_tts_injection_filter`引数で制御)。
- 語境界: surfaceがASCII(英数字主体)の場合は語境界付き一致、非ASCII
  (漢字・アクセント付きラテン文字等)は部分一致(既存どおり)。
- JA読みの永続キーは`(surface, source_context)`の組。既定
  `source_context=""`(汎用)。作品固有の確定読みは`seed_work_canon_
  reading()`で`resolution_method="work_canon"`としてWeb lookupを介さず
  事前登録できる(一般機構、特定作品ハードコードではない)。
- 「全EN経路」表記の訂正: EN側resolverが実際に配線されているのは
  `generate_narration_snippet_verified_strict`(A2英語標準+fallback)
  経由のみ。`generate_english_component_minimal_instruction`(B1
  scaffold/crosslevel/news_tail_fix等が呼ぶ)には未配線(§21残課題)。

### OPEN_ITEMS.md記載案(新規起票、いずれも通常フォローアップでありSTOP条件ではない)
1. **EN記事単位自動抽出+`generate_english_component_minimal_
   instruction`経路への配線未完了**: Family X production runnerの
   scaffold段への配線が必要(Stage 3c完了後に着手可能な状態)。
2. **Human Review時のLedger entry訂正・無効化の運用経路が未整備**:
   REGENERATE_APPROVED再生成時にLedger cacheが誤読みを再現する
   ケースへの対応(Human Review担当者がLedger entryを訂正/無効化する
   手段が現状無い)。
3. **JA読みをTTSへ直接供給する方式(別Phase)**: 現状はGate解除+ASR
   期待読みのみで、実際に発話される音自体は変わらない(JA-4で実測
   確認、resolverとTTSが同方向に誤読すると相関誤ACCEPTの理論的
   リスクも残る)。
4. **Master Audio Store invalidate運用の明文化**: 誤読み修復後、
   キャッシュされた古い音声が再利用され続けないことを保証する手順が
   未整備。

### DECISION_LOG.md記載案(新規)
- 本Phase(Sonnet修正1回目)のBLOCKER-1/2是正+Figma backfill+negative
  cache/run cap/telemetry+テスト時web lookup禁止スイッチの導入を記録。
- JA web lookupが引き続き`gpt-5.6-sol`(既存r3関数の無改変再利用、
  Routing Contractの「Support=Luna」等はN3/Pool経路限定であり本経路は
  対象外の既存カーブアウト)であることをJA-1実測で再確認した旨を記録。

## §21 残課題

1. **JA-1の2回目実行(cache hit・追加lookup 0回)は未実施**(時間制約、
   §17参照)。ただし同一メカニズムはJA-4で実測済み。
2. **EN記事単位抽出・`generate_english_component_minimal_instruction`
   経路の配線状況**: 未配線のまま(§20 OPEN起票案1)。B1側segment
   (`voice01.generate_charon_english`経由)は本Phase時点でもresolver
   非適用。
3. **JA読みTTS直接供給は別Phase**(本委任の設計範囲外、JA-4で限界を
   実測)。
4. **Human Review時のLedger訂正経路**: 未整備(§20 OPEN起票案2)。
5. **JA-3のB1B Assembly完走は未達成**: Human Review Lockの解除
   (`approve_regenerate()`)はユーザーの明示的操作が必要な安全装置
   であり、Sonnetが独自判断で実行しなかった(§17参照)。Candidate E
   自体は正しく機能することを確認済み。
6. **並走中の他プロセスによる共有ledger.jsonへの書き込み(運用上の
   注記)**: 本タスク実行中、`er006_output/pronunciation_ledger_01/
   ledger.json`へ他プロセス由来と見られる新規entry(§16「5.」参照)が
   複数回追加された。本タスクの`_load()`→対象entry変更→`_save()`
   パターンは、追跡可能な範囲でデータ損失を起こしていないことを
   `git diff`で確認したが、複数プロセスが同一JSONファイルへ同時書き
   込みする設計は、将来的なrace condition(lost update)のリスクを
   構造的に持つ(ファイルlockなし)。恒久対策は本Phaseの範囲外だが、
   Fableへの情報共有として記録する。
7. **JA-1の2回目実行(cache hit確認)は未実施**(§17JA-1参照、上記1と同旨)。
   `family_x_b3_production_wiring_01__run_01`のTTS再生成自体は完了済み
   (exit code 0、全segment処理完了)。

---

# Sonnet修正2回目(closeout): SSOT反映+JA-1 2回目実行(cache hit)evidence

作成: Sonnet実行層。委任文全文は
`docs/pm/delegation_log/2026-09-27_PRONUNCIATION-RESOLUTION-ALL-ACTIVE-FAMILIES-PRODUCTION-01_04.md`
に保存済み。Fable Gate 3判定は本REPORTでは自称しない(**Fable Gate 3判定
待ち**のまま記載する)。

## §22-1 実施内容

### 1. JA-1の2回目実行(cache hit・追加lookup0回)evidence

runner(`er019_family_x_audio_production_runner_01.py`)にはsegment単位の
限定実行オプションが無い(`--slug`/`--run`/`--level`/`--stage`のみ、§15
「Family Xプロセス粒度未確認」照合表の確認結果どおり)ため、runnerが実際に
呼んでいるのと同一のProduction関数(`er003_v1_n3_01_tts_generate.
generate_a2_japanese_with_reading_safety`、runner側呼び出し引数
`max_extra_chars=30`・`source_context`省略[既定""]と同一)を、1回目実行時の
実際のaudit記録(`er019_output/family_x_audio_production_wiring_01/
family_x_b3_production_wiring_01__run_01/a2/audit/tts_generation_
results.json`の`segments.japanese_title.canonical_text`)から取得した
canonical_text(記事本文そのもの、書き換えなし)で再現した。専用スクリプト
`er025_output_ja1_second_run_evidence_01.py`を新規作成し、実行前に
`os.environ["TTS_EXECUTION_MODE"] = "STANDARD"`を明示設定した上で、実際に
以下のコマンドで実行した(逐語):

```
set -a && source .env && set +a && TTS_EXECUTION_MODE=STANDARD ./.venv/Scripts/python.exe er025_output_ja1_second_run_evidence_01.py
```

出力は評価専用out_dir
`er025_output/pronunciation_resolution_phase2_evidence_01/
ja1_second_run_evidence_01/`へ保存し、本番runner側artifact
(`.../family_x_b3_production_wiring_01__run_01/a2/narration/
japanese_title.wav`等)・Master Audio Storeは一切変更していない
(`git status`で`er006_output/pronunciation_ledger_01/ledger.json`に
本実行由来の差分が無いことも確認済み、cache hitで`upsert`が発生しなかった
ことと整合)。

**実測結果**:
- `web_lookup_called: false`、`research_meta: null`(実際のraw usage
  log[`er025_output/pronunciation_resolution_phase2_evidence_01/
  ja1_second_run_evidence_01/raw_usage_log.jsonl`]にもgemini/openai_asr
  以外のAPI呼び出し[web_search/`gpt-5.6-sol`]が1件も記録されていないことを
  確認)。
- `resolved`: `{"surface": "Muse", "reading": "ミューズ", "confidence":
  "high", "source": "cache_or_ledger"}`(1回目実行時の`source`が実際の
  Yahoo!ファイナンス/TBS NEWS DIGのURLだったのに対し、2回目は
  `"cache_or_ledger"`に変化しており、Ledger cache経由になったことを示す)。
- Foreign Token Gate: `foreign_token_findings`で"Muse"が
  `READING_DICTIONARY`分類(`reading_dictionary`に`{"muse": "ミューズ"}`が
  含まれる)。
- TTS発話: 標準2回+fallback1回、**3回とも**実際に「メタのミューズで
  起きたまさかの展開」と発話したことをASRで確認(1回目「AIからの電話
  だと思ったら、中に人がいた!?メタのミューズで起きたまさかの展開」、
  2回目「...いた?メタのミューズで...」、fallback「...いた? メタの
  ミューズで...」)。
- 総合判定: `status: STOPPED`(標準2回+fallback1回、計3回とも
  `audio_classification: TRUE_CONTENT_MISMATCH`)。**本項目の合否には
  含めない**(委任文の指示どおり)。差分文字(全件)は以下のとおりで、
  1回目実行時と同じ既存ASR Validator制約の再現であることを確認した:
  1. 引用符「"人"」→ASR書き起こしでは3回とも引用符が脱落し「人」のみ。
  2. 全角疑問符「？」→ASR書き起こしでは3回とも異なる表記(標準attempt1
     「!?」、標準attempt2「?」、fallback「? 」)へ変換され、全角「？」
     そのものは1度も再現されない。
  3. 全角スペース「　」(？の直後)→標準2回は脱落、fallbackのみ半角
     スペース1個に変換。
  `OPEN_ITEMS.md` OPEN-199へ全件記録した。
- 費用: 実測(`cl.install()`でraw usage logを記録、`er005_output/
  cost_baseline_01/pricing_snapshot.json`の公式単価[Gemini
  `gemini-3.1-flash-tts-preview`: 入力$1.00/出力$20.00 per 1M tokens、
  OpenAI ASR`gpt-4o-mini-transcribe`: 入力$1.25/出力$5.00 per 1M
  tokens、USD_JPY=160]で算出)、TTS3回+ASR3回で**合計¥2.72**
  (Guardrail¥60・当初見積り¥10前後に対し十分小さい)。実行時間は
  STANDARD modeで6〜8秒/呼び出しであり(前回JA-1のBatch mode誤実行時の
  約120秒/呼び出しから正しく改善)、`tts_execution_mode: "STANDARD"`が
  raw usage logにも記録されていることを確認した。
- Human Review Lock(`approve_regenerate()`)は実行していない(委任文の
  指示どおり)。

### 2. SSOT反映

- `CURRENT_SPEC.md`: 「固有名詞読み解決(JA/EN共通)」節を新設(§20記載案を
  ベースに、実際のfunction名・定数名をコードから再確認した上で反映)。
  JA確定読みのTTS直接伝達が別Phaseであることも明記した。
- `DECISION_LOG.md`: `PRONUNCIATION-RESOLUTION-ALL-ACTIVE-FAMILIES-
  PRODUCTION-01`エントリを新設(Phase 1〜Sonnet修正2回目までの経緯・
  Opus L2 BLOCKER是正内容・JA-1 2回目実行結果・回帰結果を記録、Melos人名
  seedがresolverの一般機構の使用例でありユーザー個別判断ではないこと、
  EN`generate_english_component_minimal_instruction`/`generate_charon_
  english`配線deferredであることを明記)。
- `OPEN_ITEMS.md`: OPEN-196〜OPEN-200を新規登録(いずれもPM追跡、
  `USER_DECISION_REQUIRED`にはしていない): OPEN-196(ledger.json複数Agent
  同時書き込み競合リスク)、OPEN-197(Family X B1B英語segment`generate_
  charon_english`経路でEN resolver未配線)、OPEN-198(EN
  `generate_english_component_minimal_instruction`経路配線未完了)、
  OPEN-199(JA ASR Validatorの句読点正規化ギャップ、Meta A2
  `japanese_title`実例+2回目実行での差分文字全件)、OPEN-200
  (`er006_kp5_canonical_bug_01_test.py`のtilde系test2件のpre-existing
  failure+regression discovery対象外のファイル名問題)。既存OPEN項目との
  重複登録はない(grep確認済み)。
- `docs/pm/REPORT_LEDGER.md`: 本管理ID行を更新(Status・Opus発火列を
  「L2 1回(2026-09-27起動、初回所見反映済み)」へ更新)。

### 3. 回帰

本Sonnet修正2回目(closeout)ではProduction code(`er0*.py`本体)を一切
変更していない(新規追加は評価専用スクリプト`er025_output_ja1_second_
run_evidence_01.py`のみで、既存Production関数を無変更のまま呼び出す
runtime evidence取得用途、regression discovery pattern`er0*_test_*.py`
の対象外)。したがって、Sonnet修正1回目で取得済みの回帰結果
(`collected=3311 passed=3305 failed=4 errors=2`、既知6件と完全一致・
新規regressionなし、§18)がそのまま有効であり、本closeoutでの再実行は
不要と判断した(コード変更が無いため結果が変化する要因が無い)。

## §22-2 Gate 3チェックリスト evidence表(`PM_GOVERNANCE.md`2節)

| Gate 3項目 | evidence | Status |
|---|---|---|
| Production正式初回経路 | JA: `generate_a2_japanese_with_reading_safety`(A2)/`generate_charon_japanese_with_reading_safety`(B1B)。EN: `generate_narration_snippet_verified_strict`。いずれも既存Production呼び出し元は無変更のままresolver coreを内部で呼ぶよう拡張 | 充足 |
| retry・fallback・regenerationとの整合 | 標準2回+fallback1回の既存retry予算は無変更(JA-1 2回目実行でも同じ3回構成を実測)。JA-3でHuman Review Lockを独自判断で解除せず既存安全装置を尊重したことを実測確認(§17) | 充足 |
| DEV・Trial-onlyではないこと | 変更ファイルはいずれも共有Production module(`er006_pronunciation_ledger_01.py`/`er006_pronunciation_tts_injection_01.py`/`er025_entity_pronunciation_resolver_core_01.py`/`er003_v1_n3_01_tts_generate.py`他)。評価専用スクリプト(`er025_output_*_evidence_run.py`)はProduction関数を無変更のまま呼ぶ検証用途であり、Production経路自体への新規分岐ではない | 充足 |
| Production runtimeでの実発火 | JA-1(1回目・2回目とも実際のFamily X Meta記事canonical_textで実発火)、JA-3(Hormuz実記事)、JA-4(Family Z Melos、fixture文経由だが共有Production関数の直接呼び出し)、Stage 3c(既存本番audit記録の走査) | 充足 |
| 必要testのPASS | 新規test 23件(修正1回目)全PASS、既存回帰3311件中failed4/errors2は既知6件と一致(新規failureなし) | 充足 |
| runtime evidence | §17(修正1回目、EN-3/Stage3c/JA-1/JA-3/JA-4)+§22-1(本closeout、JA-1 2回目・実費用¥2.72) | 充足 |
| 実際のmodel_id・routing確認 | JA web lookup`model_id: "gpt-5.6-sol"`(1回目実測、r3既定値の無改変再利用と確認)。2回目はcache hitのためAPI呼び出し自体が発生せず(web lookup 0件を実測確認)、TTS`gemini-3.1-flash-tts-preview`・ASR`gpt-4o-mini-transcribe`は両回とも実測確認 | 充足 |
| コスト影響評価(2-2節) | 修正1回目合計約¥30前後+本closeout¥2.72、Guardrail(修正1回目¥300・本closeout¥60)に対しいずれも十分小さい | 充足 |
| `CURRENT_SPEC.md` | 「固有名詞読み解決(JA/EN共通)」節を本closeoutで新設(§22-1「2」) | 充足 |
| `DECISION_LOG.md` | 本closeoutで新規エントリを追加(§22-1「2」) | 充足 |
| `OPEN_ITEMS.md` | 本closeoutでOPEN-196〜200を新規登録(§22-1「2」) | 充足 |
| 必要なGit反映 | 本コミットでpush予定(下記) | 充足(本コミット完了後) |
| approved specとProduction挙動の一致 | Phase 1recon`APPROVED_FOR_PRODUCTION`(ユーザー承認済み設計)どおりJA/EN共通core・語境界一致・source_context一般機構・JA読みTTS直接伝達=別Phase、を実装・実測(乖離なし) | 充足 |
| 必須Opusレビュー該当案件のOpus所見反映(`PM_GOVERNANCE.md`2節2026-09-27追記) | Opus L2 BLOCKER-1/2を修正1回目で是正済み、照合表(§15)で全項目対応済みを確認。本closeoutで追加のOpus指摘は無し(本closeoutはSSOT反映+JA-1 2回目実行のみで新規Production変更なし) | 充足 |

## §22-3 Dangling Reference Check

REPORT・SSOT新規追記から参照した以下のファイル・関数・定数の実在をGrep/直接確認した(いずれも実在、捏造なし):
`er025_entity_pronunciation_resolver_core_01.py`(`resolve_unknown_ja_tokens`/
`resolve_and_augment_en_style_prefix`/`seed_work_canon_reading`/
`disable_web_lookup_for_test`/`ALLOW_PRONUNCIATION_WEB_LOOKUP_ENV`/
`NEGATIVE_CACHE_RESOLUTION_METHOD`/`JA_NEGATIVE_CACHE_COOLDOWN_SECONDS`/
`MAX_JA_WEB_LOOKUP_CALLS_PER_RUN`/`TELEMETRY_PATH`/`split_ja_reading_
sources`)、`er006_pronunciation_ledger_01.py`(`CASCADE_UNRESOLVED_ENTITY_
TYPE`/`get_hint_for_text`/`get_low_confidence_entries_for_text`/
`set_tts_injection_disabled`/`ledger_health_check`/`get_ja_reading_entry`/
`upsert_ja_reading_entry`)、`er006_pronunciation_tts_injection_01.py`
(`augment_style_prefix_with_pronunciation`)、`er003_v1_n3_01_tts_
generate.py`(`generate_a2_japanese_with_reading_safety`/
`expected_substring_ja`)、`er019_family_x_audio_production_runner_01.py`
(該当呼び出し行、segment限定オプション不在の確認)、`er005_output/
cost_baseline_01/pricing_snapshot.json`(価格根拠)。新規追加した評価
スクリプト`er025_output_ja1_second_run_evidence_01.py`および出力
`er025_output/pronunciation_resolution_phase2_evidence_01/
ja1_second_run_evidence_01/`は実在(本コミット対象)。

## §22-4 Family A/B/C確認

本closeoutでFamily A/B/C固有コードへの変更は0件(SSOT編集+新規評価
スクリプト1件のみ、`git status`で確認済み)。
