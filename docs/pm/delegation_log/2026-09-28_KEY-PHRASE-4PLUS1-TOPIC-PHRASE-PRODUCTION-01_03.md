管理ID: KEY-PHRASE-4PLUS1-TOPIC-PHRASE-PRODUCTION-01(paperworkのみ: Opus L2所見の逐語保存。**所見の実装・コード/Prompt変更・SSOT 4点[CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS/REPORT_LEDGER]編集はしない**。SSOT編集権なし[別Agentが保持中]。¥0)。一時ファイル `docs/pm/ACTIVE_TASK_KPO2.md` / `docs/pm/RESULT_PACKET_KPO2.md`(commitしない)。E-1/D-1/G-1: 再読なし、Grep→範囲Read、git出力最小化。T-0: 本委任文を `docs/pm/delegation_log/2026-09-28_KEY-PHRASE-4PLUS1-TOPIC-PHRASE-PRODUCTION-01_03.md` へ保存し `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-28_KEY-PHRASE-4PLUS1-TOPIC-PHRASE-PRODUCTION-01_03.md --json-out docs/pm/delegation_log/2026-09-28_KEY-PHRASE-4PLUS1-TOPIC-PHRASE-PRODUCTION-01_03.md_check.json`、結果1行記録。作業: `KEY-PHRASE-4PLUS1-TOPIC-PHRASE-PRODUCTION-01_REPORT.md` 末尾へ「## §12 Opus L2設計レビュー所見(逐語、2026-09-28)」を**追記のみ**(冒頭注記「本節はFableが受領したOpus L2所見の逐語転記。所見反映はユーザー判断待ち、未実装」)。以下を一字一句そのまま転記(要約・改変禁止):

---(逐語ここから)---
＃ Opus L2設計レビュー: KEY-PHRASE-4PLUS1-TOPIC-PHRASE-PRODUCTION-01(commit 0e6744e0)

読み取り専用で実施(コード/SSOT/Prompt無編集、テスト・API実行なし)。渡された論点1〜6に必要な範囲は揃っており、追加ファイル要求はありません。

## 総評

- ユーザー正式決定との一致: 良好。Promptには例示語・固有名詞優先・出現回数・難易度・CEFR・カテゴリ優先等の独自Product ruleが混入していない。4+1は「出力構造の契約」としてのみ検証され、選定基準の新設ではない。Strategy Lは全面置換されていない。
- 後段Gateへの無影響: 実コードで確認済み(下記N5)。音声・Assembly・既存UIへの漏れはない。
- **BLOCKER: 0件。** ただしSHOULD_FIX 7件(うちS3は「回帰0件」というGate 3判定材料の記載不正確、S1は今回新設した主要リスクの観測性欠落)があり、これらの是正後にGate 3判定するのが妥当という所見です(判定はFable/ユーザー)。

---

## SHOULD_FIX

**S1. Strategy L telemetryで「role構成不成立」がまさにその瞬間だけ観測不能**
`C:\Users\tensh\eigo-radio\er003_v1_n3_01_scaffold_generate.py:240` は `role_counts=_role_counts_from_items(result.get("original_items"))` を渡すが、`original_items` は同ファイル285-289行で **status==PASS のときだけ** 設定される。よってrole不成立(INVALID)時は `role_counts: null` になる。実データで確認: `er030_output/kp_backend_telemetry_01/telemetry.jsonl:63,68`(melos_a2のINVALID 2行がいずれも `role_counts: null`)。DB Hybrid側は `parsed` から算出するためINVALIDでも内訳が残る(`er030_key_phrase_db_hybrid_selector_01.py:566-567`)ので、経路間で観測性が非対称。
最小修正: `_run_key_phrase_selection_strategy_l` が既に271-272行で計算している `role_counts` を戻り値へ載せ、240行を `result.get("role_counts")` に変更(2行)。可能なら同経路にもrole起因INVALIDの識別タグを1つ追加。

**S2. evidence実行がProduction telemetryへ `synthetic: false` で記録されている**
`er035_kp_4plus1_topic_phrase_evidence_01_run.py:124` は `sc.run_key_phrases(...)` に `synthetic` を渡していない。結果、評価用9件+**人工的に候補プールを枯渇させたforced_fallback記事**が本番実績として記録された(`telemetry.jsonl:67` = `fallback_reason_code: "SHORTLIST_TOO_SMALL"`, `synthetic: false`)。`synthetic` フラグは前回のOpus L2所見(B1)でまさにこの区別のために新設されたもの。fallback率・KP失敗率はProduction監視指標なので汚染は実害あり。
最小修正: evidence script側で `synthetic=True` を渡す(Production module変更不要)。既に書かれた10行は書き換えず、REPORT/OPENに「article_id接頭辞 `KP_4PLUS1_EVIDENCE_01_` の行はevidence起源」と明記。

**S3. 「回帰0件」の記載が自己計測と不一致(Gate 3判定材料)**
`KEY-PHRASE-4PLUS1-TOPIC-PHRASE-PRODUCTION-01_REPORT.md:177-186` は編集前 `failed=6`、編集後 `failed=7` と自ら記録しながら「委任文の既知baseline(failed=7)と完全一致、新規機能regressionは0件」と結論している。実際には**変更前に通っていたテスト1件が今は落ちている**。原因は件数照合meta-test(`er003_test_p2j_investigate.py:69-82`、combined pattern `er0*_test_*.py` の総数と prefix別 `er003_test_*.py` の合計の一致を検証)で、新規テストのファイル名 `er003_key_words_min_unit_4plus1_test_01.py` はcombined patternに一致するがprefix patternには一致しないため不変条件が崩れる。
最小修正: (a)新規テストを既存命名規約 `er003_test_key_words_min_unit_4plus1_01.py` へrename(両patternに一致し不変条件が回復、回帰suiteからも外れない)、または(b)meta-test側を更新。いずれにせよREPORT §8の記載は「編集前6→編集後7、差分1件は件数照合meta-test」へ是正が必要。Fableは現状の「回帰0件」をそのままGate 3の充足根拠にしないでください。

**S4. 既知のまま壊れているTrial testが回帰網に掛からない**
`er034_key_phrase_db_hybrid_source_reference_contract_trial_06_test.py:189` は `for field in p2g._ITEM_REQUIRED_FIELDS: assertIn(field, restored_item)` を回すが、同ファイル174-185行のfixtureに `key_phrase_role` が無いため実行すれば必ずFAILする(REPORT §8も自認)。default regression pattern は `er0*_test_*.py`(`run_project_regression.py:40`)で `..._test.py` 終端のこのファイルを拾わないため、放置すると将来の実回帰と区別できない不発弾になる。
最小修正: 当該fixture dictへ `"key_phrase_role": "important"` を1行追加(挙動非依存)。編集を避けるなら `OPEN_ITEMS.md` へ「意図的に古いTrial test」として登録。

**S5. 同じschema・同じ5件validatorを共有する別Promptが4+1非対応のまま**
`er003_key_words_production.py:44` の `b2_key_words_production_l_prompt_template.txt` には今回の追記が無い(全29行確認)。このテンプレートは同じ `_ITEM_SCHEMA_PROPERTIES`(role必須)と `expected_item_count=5`(4+1集計検証が有効)を共有するため、もし再利用されると5件すべてimportantになり `KEY_WORDS_STRUCTURE_INVALID` を繰り返す構造。現状は過去のgrep監査どおりテスト専用で本番未使用(`DECISION_LOG_HISTORY.md:6532`)なので実害なしと判断できるが、無記載のままは危険。
最小修正: 同一段落を追記するか、`er003_key_words_production.py:44` 付近へ「test専用・4+1契約非対応(本番経路は `b1_p2_keywords_l_prompt_template.txt`)」の1行コメント。

**S6. 追記文言が既存優先順位を「部分的に再掲」している**
`er003_v1_translator_briefs/b1_p2_keywords_l_prompt_template.txt:25`。残り4個の基準として6項目を再掲しているが、テンプレート9行目「音声で一度だけ聞いたときに処理できるかを最優先」・13行目「透明表現は記事上重要でも優先度を下げる」は再掲に含まれない。部分再掲は重み付けの微妙な変質を招きうる(Important 4枠の基準を変えないというユーザー要求に対するリスク)。同じ一文中の「候補区分(重要な単語・単語群/phrase・idiom・phrasal verb/word)」はDB Hybrid固有の区分名であり、候補プールを持たないStrategy L(Standard/Advanced両レベル・Fiction)では指示対象が存在しない。
最小修正: 「残り4個は、上記の基準に従って選んでください(key_phrase_role="important")」と参照形にする(新ruleを足さず語数も減る)。区分名の列挙は「候補の種類・区分」と一般化するか、DB Hybrid側guidanceへ寄せる。

**S7. 記載不整合(小)**: REPORT §2「既存test 5ファイルのfixture」/`CURRENT_SPEC.md:1501`「既存test 5ファイル」に対し、`key_phrase_role` を含む既存testは実測4ファイル(`er003_test_key_words_min_unit.py` / `er003_test_p2i_production.py` / `er003_test_b1_p2.py` / `er030_key_phrase_db_hybrid_source_reference_contract_01_test.py`)。件数を4へ是正。

---

## NOTE

**N1. Family Xでは「role不成立」が新しいfallback発火原因になる(分岐は新設されていないが意味論は増えた)。** `er030_key_phrase_db_hybrid_selector_01.py:606-619` の通り、statusと `fallback_allowed` 既定値は無変更でF-3どおりだが、結果としてrole不成立はDB Hybrid→Strategy L全文方式(本文全体をLLMへ送る、より高価な経路)への切替を1件増やす。今回の4件では未発生。識別タグ `detail_reason_code` は `validation_reasons`(トップレベル)のみをgrepしており、per-itemのenum不正は `item_reasons` に入るため取りこぼす(614行)。必要なら `item_reasons` も見る1行追加で揃う。

**N2. Redundancy QA発火率の増加は観測されていない(REPORT欠落の比較を補完)。** 同一4記事の4+1導入前実績は `er030_output/family_x_kp_source_reference_contract_evidence_01/{meta_a2,meta_b1b,hormuz_a2,hormuz_b1b}/evidence_summary.json:15` で `redundancy_retry_attempts` = 0/1/0/1 = **2/4**、今回は3/4(`er035_output/kp_4plus1_evidence_01/summary.json`)。n=4では有意差なし。REPORT §6観点5にこのbaseline比較を追記すると評価が締まります。

**N3. 2軸guidanceの実効的な相互作用。** DB Hybrid側 `er030_key_phrase_db_hybrid_source_reference_contract_01.py:172-173`「5個のうち少なくとも1個は[重要な単語・単語群候補]区分から」は、今回のtopic項目1件で満たされ得る(実測4件中3件のtopicがimportant_noun区分由来、evidence観点7)。つまりimportant役割4件がphrase/word区分だけで構成される余地が生じた。文言変更は新Product rule相当なのでユーザー判断事項として提示するのが妥当(現状のまま運用も可、Important 4件の品質劣化は未観測)。

**N4. B2研究10件経路。** schemaはrole必須化されたが研究版Prompt群(`b2_key_words_min_unit_*` / `research10_*`)には説明がない。strict modeのenum制約により値自体は常に妥当、集計検証は `er003_key_words_min_unit.py:485` で5件経路に限定されガード済み(設計どおり)。ただし研究版のroleは無意味なラベルなので、将来の集計で4+1データとして混ぜないこと。

**N5. 後段Gate無影響性は実コードで確認済み(論点4)。** canonicalization prompt(`er003_key_words_canonicalization.py:206-214`)とRedundancy QA prompt(`er011_key_phrase_set_redundancy_qa_01.py:114-118`)はいずれもフィールドwhitelistで組むため `key_phrase_role` はどのLLM入力にも入らない。TTS読み上げ原稿は `er003_b2_key_words.py:419-430` が `order`/`display_phrase`/`ja_gloss` のみ参照。source gateは `rank`/`used_form`/`source_span`/`source_sentence` のみ。canonicalization passthroughは存在時のみ引き継ぐ条件付き(`er003_key_words_canonicalization.py:624-627`)で旧artifact後方互換。`kp_auxiliary_candidates.json` は `key_phrases/key_phrases_db_hybrid/` 配下(`er030_key_phrase_db_hybrid_selector_01.py:650`)でAssembly/TTSの参照集合外。

**N6. 補助候補データの性格づけは妥当だが配信面は未決。** 各要素に `verification_status: "unverified_reference_candidate"`、ファイル先頭に「validator/canonicalization/source gate未通過の未検証参考候補」noteがあり、品質保証済み5件と構造的に区別可能(良い設計)。一方で中身はStage1候補dictそのままで本文由来の語・文ID等を含むため、将来クライアントへ配る場合は「記事の一部を外部へ出す」ことになる点をUI決定時に併せて判断する必要あり。

**N7. 定数の二重管理(低リスク)。** 判定は `expected_item_count == p2g.PRODUCTION_ITEM_COUNT_UNCHANGED`(5)、呼び出し側は `prod.PRODUCTION_ITEM_COUNT`(5)。将来枠数が片方だけ変わると4+1検証が**黙って無効化**される(失敗ではなく不検査)。両者は既存testで5に固定されているため現状の実害なし。等価性testを1件足すと安全。

**N8. evidenceの読み方(論点5)。** 9件でTopic選定は全件が中心質問に整合し固有名詞偏りゼロ、Important 4件は旧Production 5件と概念重複3〜5/5で劣化兆候なし、という結論は資料から妥当に読める。ただし(a)Topic該当性判定はモデルの自己申告理由の転記+Sonnetの主観であり独立評価ではない(1〜2記事はユーザー目で確認する価値あり)、(b)F-1が本来懸念した「1回だけ出現する一般語だが理解の前提」ケースは**観測されておらず、反証もされていない**(観測されたのは人工的に候補を枯渇させたforced_fallback、すなわち別事象)。F-1は「evidenceにより解消」ではなく「未観測のまま継続」と扱うのが正確です。

---

## ユーザー判断が必要な項目(整理)

1. **Strategy L経路のretry緩和**(最重要)。現状 `er003_v1_n3_01_scaffold_generate.py:262-265` が `max_attempts=1` 固定(4+1導入前からの既存挙動)で、role不成立は即失敗・`run_key_phrases` も再試行しない(melos_a2で実観測)。4+1は制約を1つ増やすため初回失敗率は上がる方向。影響はFiction/legacy/Family X fallback経路で、失敗時は当該レベルのKPが生成されずAssembly前でSTOP(不正データの混入ではなく手動再実行コスト)。選択肢: (a)現状維持、(b)この経路のみ `max_attempts=2` へ(worst case 選定call +1回、¥1前後/記事)、(c)role不成立に限り再試行。※既存Production既定値は元々2(`MAX_PRODUCTION_RETRY_ATTEMPTS`)で、1固定はこの経路の独自指定。
2. **F-1対処**: 候補プールが薄い記事でTopic該当語がStage1に存在しない場合の扱い(現状=Strategy Lへ委ねる/無対処)。新候補生成ロジックは未実装のままが設計方針と整合。
3. **F-4 runner-up契約**: Strategy L側の5枠外候補を出す新出力契約の要否(OPEN-211に登録済み)。
4. **UI件数・配置**: 未定のまま(新規UIなし)。
5. (任意)N3の「重要語区分から最低1件」をimportant役割4件側の条件に読み替えるか。

## Gate 3への所見(判定はFable/ユーザー)

仕様一致・共通schema伝播・失敗経路の合流・後段Gate無影響・cost(¥4.84、Guardrail比6%)は確認できました。一方で「回帰0件」の記載は実測と不一致(S3)、新設リスクの観測性に欠落(S1)、Production telemetryにevidence混入(S2)、既知FAILテスト残置(S4)があります。いずれも小修正(合計十数行、API支出ゼロ、Production挙動不変)で解消できる範囲なので、S1〜S5を反映した上でGate 3判定に進むのが安全だと考えます。Production採用可否の宣言は行いません。
---(逐語ここまで)---

Git: REPORT+delegation_log+`_check.json` のみpath指定add、メッセージ `KEY-PHRASE-4PLUS1-TOPIC-PHRASE-PRODUCTION-01: Opus L2所見(BLOCKER 0/SF 7/N 8)を逐語保存(§12)`、trailer `Management-ID: KEY-PHRASE-4PLUS1-TOPIC-PHRASE-PRODUCTION-01`、push origin main。他Agent差分(SSOT 4点等)は一切addしない。RESULT_PACKETに commit hash・raw URL。
