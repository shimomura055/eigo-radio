# IMPLEMENTATION_DESIGN_01: KP全文選定(Prompt 2・Luna)+最大3件化 X/Z共通Production配線設計

管理ID: KP-FULLTEXT-SELECTION-3KP-PRODUCTION-01 委任_01 / 2026-10-22 / 到達Status: `APPROVED_FOR_PRODUCTION_DESIGN_PENDING_OPUS`(Production既存ファイル未編集=`PRODUCTION_WIRED`ではない)
前提: `INVESTIGATION_01.md`(F-1〜F-9、5件前提28箇所の分類)、`LEVEL_SPEC_CHECK_01.md`(衝突なし・区分B)。ユーザー原文=`docs/pm/delegation_log/2026-10-22_KP-FULLTEXT-SELECTION-3KP-PRODUCTION-01_USER.md`。
未配線module: `er105_kp_fulltext_selector_01.py`(+`_test_01.py` 32件PASS、API 0)。

## 0. 設計の一覧と、Opus条件Aに答えてほしい点

### 0-1 方針(1行)
`sc.run_key_phrase_selection`に新backend値`fulltext_p2`を1つ追加し(X/Z共通)、選定段だけを`er105`へ置換する。後段(canonicalization → gloss再整合 → Redundancy QA → Z D1 gate → 音声 → 組立)は**既存を再利用**し、**全文選定で不足する3点だけを最小に補う**: (a)gloss生成(F-3) (b)原形化(F-2) (c)canonicalization INVALIDの外側retry(F-7)。旧DB Hybrid/M2P0経路はGate 3後に撤去(rollback可能性のため2 commit)。

### 0-2 Opusへの確認事項(重要度順)
| Q | 内容 | 設計案 | 懸念 |
|---|---|---|---|
| **Q1** | **原形化の担い手**(F-2): 既存に原形化工程は無く、旧経路は選定Promptが担っていた。Prompt 2では本文表層形が来る | canonicalization(fulltext版template)に「語形の基本形化」を追加し、validatorに**活用形→基本形の1対1トークン置換のみ許す決定論判定**を追加(`er105.is_valid_inflection_normalization`、プロトタイプ+test済み。人称一般化の閉じた語彙表思想と同じ)。fulltext由来itemのみ(A/B/C不変) | 承認済みRule7の拡張(品質は維持=KPが基本形である既存要件を保つ追加)。代替=(B)Trial-02の一般化Prompt(Haiku)を新規後段化=保存データで`pumps their fist`/`raw materials`等の誤変換あり、新Trial範囲 (C)表層形のまま(KPの基本形要件を黙って落とす=不可) |
| **Q2** | 同一表層語句が複数文に出る場合(F-5: 14/70=20%) | Z D1の「曖昧→STOP」ではなく**先頭出現を決定論採用**(`fulltext_exact_first_of_N`+`occurrence_*`記録)。同一語句=同一学習対象でglossの語義選択にのみsource_sentenceを使う | Z D1(#109)の曖昧STOP規則との整合: D1は「LLM自由記述文の事後特定」用で、本件は選定語句が本文と完全一致している別状況。D1 gateは`exact`解決で冪等に通る |
| **Q3** | Prompt 2逐語性: ①構造化出力schema(`{items:[{phrase,word_count}]}`、maxItems=3、Prompt本文は不変)②再選定時のnoteは本文の**後ろ**に後置 ③Zの`Z_KP_GENERIC_NOTE`(所有格代名詞回避)は全文backendでは付けない | ①自由文表をheuristic parseするTrialのparser(手動補正4/70)をProductionに入れない ②③Prompt本文を1字も変えない | ①schemaは「Promptの変更」に当たらないか(Trialは自由文。構造化で遵守率が変わる可能性はruntime evidenceで確認) |
| **Q4** | 既存の有限助動詞Validator(canonicalization:531、min_unit)はPrompt 2が許す形(`the stage is set`=2/70)を拒否する | ルール自体は不変。選定段でprecheckし、不適合はretry(後段のAPI費用を使う前)。2回とも不適合ならstage失敗(fail-closed) | 承認済み構造Validatorの維持。Prompt 2との軽微な不整合(約3%/語句)をretryで吸収する設計で妥当か |
| **Q5** | **Strategy L fallbackの撤去**(「候補DB前提を取り除く」趣旨) | 全文選定の失敗=retry上限2→stage失敗(fail-closed、旧KP黙示採用なし)。Xの「M2不発火時のStrategy L fallbackは許可・報告必須」(CURRENT_SPEC:1984付近)も対象消滅 | 全文選定が連続失敗するとKP stageが止まる(Zは元々同じ)。fallback先=旧Strategy L(5件・4+1)は3件仕様と矛盾するため置かない |
| **Q6** | gloss生成をgloss再整合工程の拡張で行う(F-3) | `select_generation_targets`に「`fulltext_source_ref`付きでgloss無し」を追加、`validate_item_corrected`はcurrent無しの場合の矛盾判定を緩和、消費側に「gloss欠落STOP」を追加(kill switch OFF時に無glossのままTTSへ進まない) | 承認済みgloss規則(実行時抽出・item retry2・HR)を再利用するので品質は同一。工程を共有する分、既存関門(Z `_gloss_person_gate`/X TTS関所)がそのまま効く |
| **Q7** | canonicalization templateの複製(fulltext版) | Listening Blocker前提・「5件」記述を、Prompt 2の学習価値前提・件数中立へ。schema/QA項目名は不変。旧templateはA/B/C用に無変更 | QA項目名`qa_listening_blocker_value_preserved`の意味が「学習価値維持」へ読み替わる(名称変更は影響が広いため見送り) |
| **Q8** | XにZと同じcanonicalization INVALID外側retry(通算3回)を追加+stale退避 | `_run_key_phrases_impl`の全文backend分岐内で実施。Z `run_kp_with_outer_retry`は無変更で新backendを渡すだけ | KPMP B1(旧KP残存)の恒久修正を兼ねる。Xの共有関数を触るがbackend値で限定 |

## 1. 新経路の全体図(X/Z共通)
```
[記事全文(level本文)] ─ er105.build_user_message(Prompt 2逐語 + "\n\n---\n\n【記事本文】\n" + 本文 [+ 再選定時のみ本文の後ろにnote])
   ↓ Luna(gpt-6-luna) 1回/レベル。routing contract(process=B1_SUPPORT|A2_SUPPORT→SUPPORT_MODEL)で確定、response.model照合
   ↓ 構造化出力 {"items":[{"phrase","word_count"}]} maxItems=3
 er105.parse_selection(厳密JSON。自由文heuristicなし)
   ↓ er105.validate_and_resolve: 本文連続一致(表記ゆれ=大小文字/アポストロフィ/ダッシュ/空白のみ吸収)・1〜5語・1〜3件・重複なし・
   ↓   有限助動詞precheck(F-6)・文境界またぎ不可 → 原文スライス=source_span、文ID/sentence=build_sentence_units(Z D1と同一分割)、先頭出現採用(Q2)
   ↓ 不適合/解析失敗/技術失敗 → 同一messageで再試行(上限MAX_ATTEMPTS=2。旧Strategy Lと同値) → 上限で KEY_WORDS_STRUCTURE_INVALID/PARSE_FAILED/TECHNICAL_GENERATION_FAILED(fail-closed)
 original_items = [{rank, display_phrase(=source_span), source_span, source_sentence, source_sentence_id, ja_gloss=None, fulltext_source_ref, ...}]
   ↓ (既存) run_key_phrase_canonicalization: fulltext版template、Rule3人称一般化(既存)+原形化(新・Q1)、Rule7、QA 12項目
   ↓ (既存+拡張Q6) gloss再整合: 全itemが「生成対象」→ 承認済みgloss規則・人称整合・括弧/数字禁止・item retry2・HR
   ↓ (既存) Redundancy QA(num_items可変)+記号検出 → NGなら選定からやり直し(KEY_PHRASE_REDUNDANCY_RETRY_MAX=2、noteは本文後置)
   ↓ keywords_canonicalized.json(最大3 item)
 以降: X=KP source gate→TTS→ASR→組立→試聴 / Z=gloss HR gate→人称整合関所→D1 gate→install→Adv解説→TTS→組立→試聴(いずれも既存・rank駆動)
```

## 2. `er105_kp_fulltext_selector_01.py`(実装済み・未配線)
- `PROMPT_2_TEXT`: ユーザー逐語(`USER.md` §2の2本の`---`間)。test `test_prompt_matches_user_original_verbatim`が原文ファイルから抽出して**一字一句比較**。sha256=`a12896f485604f32efd52cb159d2615733c0eca262725af78db0b4f1c9a3dc9a`をtestで固定(変更はユーザー明示承認)。`prompt_prefix_intact()`で送信直前にassert。
- 本文受け渡し区切り`"\n\n---\n\n【記事本文】\n"`はTrial KP6M/TRIAL-02/03と同一(TRIAL_RESULT_02 §8-2)。
- `KP_COUNT_MAX=3`(件数の単一の置き場)、`KP_WORDS_MAX=5`、`SELECTION_MODEL_ID="gpt-6-luna"`、`MAX_ATTEMPTS=2`、`BACKEND_ID="fulltext_p2"`。
- `resolve_model(process)`: process∈{B1_SUPPORT,A2_SUPPORT}以外は`FulltextSelectionError`(即停止)、`routing.require_model`の解決結果が`gpt-6-luna`でなければ停止。実API時のみ使用。`make_selector_fn`は`response.model != 要求model`で`ModelMismatchError`(技術的失敗扱い)。
- reasoningはprovider default・developer messageなし(Trial KP6M/TRIAL-02/03と同条件)。
- 戻り値は旧`_run_key_phrase_selection_strategy_l`互換(`status`=旧と同値`KEY_WORDS_STRUCTURE_PASS`等、`parsed={"items":…}`[Z外側retryが参照]、`original_items`、`model_id`、`kp_backend_used`)+`shortfall`(3件未満の記録)。成果物: `keywords_selector_prompt.txt`、`keywords_runtime_metadata.json`(prompt sha・actual model ID・attempts・shortfall)。
- 1〜2件はPrompt 2「適切な候補が不足する場合のみ3件未満」に従い許容(`shortfall=true`をtelemetry)。0件・4件以上・非JSON・本文不一致・6語以上・重複は不適合。

## 3. 契約調整

### 3-1 候補ID/source span契約(F-4)
- 全文選定itemに`source_reference_contract`は**付けない**(付けると`expand_dangling_source_span`[案A'窓拡張、`canonicalization.py:230`]・`kp_extends_beyond_candidate`[:692]が候補ID方式前提で誤発火)。代わりに`fulltext_source_ref="fulltext_exact_v1"`(下流の読取は無い=参照用)。test `test_no_candidate_id_contract_key`/`test_compatible_with_existing_canonicalization_input_and_merge`で`expand_dangling_source_span`が不変を確認。
- source_span=本文の原文スライス。KP source gate(a)(`er003_key_phrase_source_gate_01`: 本文実在)を構造的に満たす。`source_sentence`=`build_sentence_units`のunit全文(Z D1と同一)。Z D1 gateは`resolve_item`で`exact`(unit全文一致)→冪等に通る(配線後に統合testで確認)。
- 候補IDフィールド(`source_candidate_id`/`surface_echo`/`candidate_mismatch_suspected`)・`key_phrase_role`はitemに存在しない。canonicalizationのpassthroughは「存在する場合のみ引き継ぐ」(`canonicalization.py:759-770`)ため欠落で無害(旧artifact互換の既存挙動)。

### 3-2 複数文出現(Q2)
先頭出現を採用し`resolution_method=fulltext_exact_first_of_N`、`occurrence_count`、`occurrence_sentence_ids`を記録。実測14/70(20%)がこのケース=Z D1の曖昧STOP規則(複数一致→STOP)をそのまま使うと3件選定の約49%の単位でSTOPする(INVESTIGATION F-5)。

### 3-3 本文一致の定義(「絶対条件」の機械検証)
大文字小文字・アポストロフィ/引用符の種類・ダッシュの種類・連続空白のみ吸収(正規表現、語境界あり)。語の変更・並べ替え・活用変更・文境界またぎは不一致。語数はスペース区切り(Prompt 2の定義どおり。ハイフン語は1語)。LLM申告語数は実語数と不一致でも非ブロッキング記録(`declared_word_count_mismatch`)。

### 3-4 構造Validatorとの整合(F-6)
`_legacy_form_reasons`が既存canonicalization Validatorの`_contains_finite_auxiliary`を**再利用**(再実装なし)。選定段のprecheck不適合=retry。ルール変更なし。

## 4. 後段の調整(最小・既存再利用)

### 4-1 canonicalization接続
`run_key_phrase_canonicalization`: `original_items`に`fulltext_source_ref`があるとき、(i)fulltext版template(`b1_p2_keywords_canonicalization_fulltext_prompt_template.txt`新設。旧templateはA/B/C用に無変更)を使い、(ii)validatorへ`allow_inflection_normalization=True`を渡す。他の呼出(A/B/C)は引数既定False=バイト同一。schema・QA 12項目名・REVIEW_REQUIRED運用は不変。`kp_extends_beyond_candidate`は契約キー無しでFalse→gloss監査フラグは立たない(窓拡張なしのため正しい)。

### 4-2 原形化(Q1。F-2)
- fulltext版templateに「key_phraseは辞書の見出し形(動詞は原形、名詞は単数が自然な場合は単数)にしてよい。この場合normalization_reason=`lemma_normalization`」を追加。他のルール(最小十分・冠詞/限定詞・人称一般化・Meaning Preservation)は旧templateのまま。
- validator追加: `validate_canonicalization_item`に`allow_inflection_normalization`(既定False)。Trueのとき、Rule7不適合でも`er105.is_valid_inflection_normalization`(**1対1トークン置換・語数不変・各トークンが活用形→基本形候補[suffix規則+閉じた不規則表]または人称一般化の閉じた表**)に合えば受理。`raw beans→raw materials`、`concierge feature→service`、`the story→something`等の**別語置換・語追加は拒否**。
- プロトタイプ実績(test 2件): 受理=`pushed prices up→push prices up`/`gave back some gains→give back some gains`/`took a sharp turn→take a sharp turn`/`pumps its fist→pump one's fist`/`hands the baton→hand the baton`等10例、拒否=Trial-02のHaiku一般化の誤変換(`keep raw materials in stock`/`human concierge service`/`moving something forward`/`blurted something out`/`hand the baton to someone`/`pumps their fist`)。
- 「原形化」を新たにLLM Promptだけに任せない(決定論validatorで機械保証する)ことで、Trial-02で見えたHaiku一般化の品質問題(22/70適用漏れ・誤変換)を避ける。

### 4-3 gloss生成(Q6。F-3)
- 選定段は`japanese_gloss=None`を返す(Prompt 2は意味を出力しない)。merge時`japanese_gloss_tts=""`(`convert_display_gloss_to_tts_text(None)`は""を返す。test確認)。
- `gloss_alignment.select_generation_targets`: `it.get("fulltext_source_ref") and not it.get("japanese_gloss")`を生成対象に追加(旧経路itemはgloss常在=不変)。`build_user_message_corrected`は`current_japanese_gloss=null`を「current無し・新規生成」と明記する1文を追加。`validate_item_corrected`は`cur`が空の場合に限り「consistentと同gloss/異gloss」矛盾判定を適用しない(他の検査[括弧/数字/…/記号/人称語突合/qa]は全て適用)。
- 生成gloss規則=承認済み選定Promptのgloss段落を**実行時抽出して再利用**(`load_approved_gloss_rules`。複製しない)→**旧`b1_p2_keywords_l_prompt_template.txt`は削除不可**(INVESTIGATION F-3、残置の理由をファイル先頭コメントとOPEN_ITEMSに明記)。モデル=`SUPPORT_MODEL`(Luna)、item retry2、失敗=HR(`FAILED_HUMAN_REVIEW_REQUIRED`)で既存関所が停止。
- 消費側: `select_consumer_unevaluated`に「`fulltext_source_ref`付きでgloss無し」を追加(kill switch `EIGO_KP_GLOSS_ALIGNMENT=0`でgloss未生成のままTTS/組立へ進むのを防止。fail-closed)。
- 費用: 全3 itemを1 batch callで生成(旧は対象0〜2 item)。+約0.1円/レベル。

### 4-4 role(4+1)の扱い
全文選定itemは`key_phrase_role`を持たず、roleに依存する検査(`validate_min_unit_selection`の4+1集計、`topic_requirement_satisfied_via_backup`、DB Hybridのbackup置換、telemetryの`role_counts`)はX/Z経路に現れない。旧validator/schema/templateはA/B/C用に無変更(INVESTIGATION #1-#3)。

### 4-5 件数語を含むPrompt/文言(D分類。件数語のみの置換、判断基準は不変)
- `er019_family_x_kp_explanation_01.py:69,90`: `For each of the 5 Key Phrases below` / `x5` → 実件数n(f-string)。`PROMPT_SHA256`(Trial-02逐語性の証拠)は5件版で算出し続け、n=5置換が元文と一致するtestで逐語性を維持。schemaは既にlen(items)導出。
- `er011_key_phrase_set_redundancy_qa_01.py:35` developer message「Key Phrase 5件」→`{num_items}件`。`num_items=1`(shortfall)時のペア0件でQAをskipするかの動作確認testを追加。
- canonicalization template「5件の順位…」はfulltext版で件数中立化(Q7)。

## 5. retry / fallback / regeneration / resume の整合

### 5-1 retry階層(上限は全て既存値を踏襲。独自増減なし)
| 階層 | 上限 | 対象 | 備考 |
|---|---|---|---|
| 選定(er105) | 2回(`MAX_ATTEMPTS`) | 技術失敗・parse・検証不適合 | 旧Strategy L `MAX_PRODUCTION_RETRY_ATTEMPTS=2`と同値 |
| canonicalization | 2回(既存`MAX_CANONICALIZATION_RETRY_ATTEMPTS`) | 技術/構造不適合 | 既存 |
| gloss再整合 | item毎2回(既存) | 既存 | 既存 |
| Redundancy/記号NG | 2回(`KEY_PHRASE_REDUNDANCY_RETRY_MAX`) | 選定からやり直し(noteは本文後置) | 既存ループを共用 |
| canonicalization INVALID外側 | 通算3回(Z既存`Z_KP_OUTER_RETRY_MAX`)、**Xに新設**(Q8) | `CANONICALIZATION_*`以外のstatus | 全文選定+最小化圧力でINVALID頻度が上がる見込み(Trial-03のArm B 2/14単位)への対策。Zは既存関数のまま |
- **最悪呼出数の上限**(旧`KP_ARTICLE_COST_CAP_JPY=15`[db_hybrid限定]の代替): 選定 = 外側3 ×(Redundancy 1+2)× 選定2 = 最大18回/レベル ≒ 18×約0.2円=約3.6円/レベル<旧cap。cap判定コードは撤去し、上限は回数で担保(各階層の回数は定数)。

### 5-2 fail-closed・stale退避(KPMP B1の恒久修正を兼ねる)
外側retryのattemptごとに`keywords_canonicalized.json`を`outer_retry/attempt_n/`へ退避(Z既存`_copy_attempt_artifacts`方式)。**最終失敗時**は直近attemptが書いた`keywords_canonicalized.json`を`keywords_canonicalized.STALE_attempt{n}.json`へ改名し、本名のファイルを残さない(後段が旧KPを読めない)。`kp_stage_failure_status`(X)/`FamilyZE2EStop`(Z)は既存のまま作動(新status文字列は既存値)。

### 5-3 Zの`Z_KP_GENERIC_NOTE`
Prompt 2逐語のため全文backendでは付けない(`run_kp_with_outer_retry(generic_note="")`)。代名詞を含む断片の問題は、canonicalization Rule3(人称一般化・既存)と外側retry(通算3)で処理する。再選定時のnote(Redundancy NG等の機械診断)は**本文の後ろ**に後置し、Prompt本文は不変(`prompt_prefix_intact`がattemptごとに確認)。

### 5-4 Fallback
**撤去**(Q5)。全文選定の失敗はretry上限→stage失敗。旧Strategy Lは5件・4+1仕様でありX/Zの3件仕様と矛盾するため置かない。X `m2_fallback`系(summary/notice/stdout/telemetry)も対象消滅で撤去(§7)。

### 5-5 regeneration / resume
| 経路 | 現状 | 変更 |
|---|---|---|
| X `--scaffold-only kp`(1レベル1回) | `_kp_already_generated`が`keywords_runtime_metadata.json`/`keywords_canonicalized.json`/`key_phrases_db_hybrid`を検出(er019:369-375) | 検出名を新成果物へ(`key_phrases_db_hybrid`削除、`STALE`ファイルも検出に追加) |
| Z `--regenerate-stage kp_<lv>` / `ensure_stage` | provenance=本文sha。再生成時は`run_kp_stage`を再実行 | 変更なし。HR snapshot復元(`_load_gloss_hr_resume`)も不変 |
| Z TTS checkpoint | `_merge_checkpoint`が旧rankの結果を保持(F-9) | 現KP rank集合へ刈り込む関数を追加+test(5→3縮小時) |
| 過去run(5件) | 可変長で読める | **変更しない・再生成しない**(再利用時はartifactそのまま) |
| X resume(tts以降) | `results.key_phrases`は現kp_itemsから構築(er019:740,753,1039) | 変更不要。test追加 |

## 6. 件数の置き場・可変長化・配線点(X/Z)
- 置き場: `er105.KP_COUNT_MAX=3`のみ。X/Zモジュールは必要箇所でimport。旧共有定数(`prod.PRODUCTION_ITEM_COUNT=5`等)はA/B/C用に不変。KPが3件未満(shortfall)でも全下流がrank駆動で動くことをtestで保証(1/2/3件)。
- 配線点の差分案:

| 対象 | 差分 |
|---|---|
| `er003_v1_n3_01_scaffold_generate.py` | (1)`run_key_phrase_selection`に`kp_backend=="fulltext_p2"`分岐(→`er105.run_fulltext_selection`+telemetry 1行[model_id/attempts/shortfall/prompt sha]) (2)`_run_key_phrases_impl`: 全文backend時のcanonicalization外側retry+stale退避、`KP_ARTICLE_COST_CAP`判定は全文backendでは使わない (3)`run_key_phrase_canonicalization`: fulltext item検出時にtemplate/validator引数を切替 (4)docstringの「5件」文言 |
| `er003_key_words_canonicalization.py` | `validate_canonicalization_item/response`に`allow_inflection_normalization`(既定False)。`er105.is_valid_inflection_normalization`をimport(または同関数を本moduleへ移設) |
| `er003_key_words_gloss_alignment.py` | §4-3(対象選定・message・validate緩和・消費側STOP) |
| `er003_v1_translator_briefs/` | fulltext版canonicalization template新設(旧は無変更)、旧selection templateは残置(gloss規則抽出元) |
| `er019_family_x_audio_production_runner_01.py` | `run_theme_scaffold`既定`kp_backend="fulltext_p2"`、m2_fallback keys撤去、`_kp_already_generated`、entry_pointの`kp_backend_used_by_level`は維持(値=`fulltext_p2`)、共有shell音声(num_*)読込を`len(kp_items)`に限定(任意) |
| `er062_family_z_writer_01.py` | `run_kp_stage`が`select_fn=functools.partial(sc.run_key_phrase_selection, kp_backend="fulltext_p2")`と`generic_note=""`を渡す(`run_kp_with_outer_retry`本体は無変更) |
| `er026_family_z_fiction_production_runner_01.py` | stage_kp無変更。mock候補3件。legacy `run_keyphrase_stage`(`--stage keyphrase`、process=None Strategy L)は**新backendへ付替えまたは撤去**(5件のProduction到達経路を残さない) |
| `er063_family_z_audio_01.py` | `provision_shell_assets`の`kp_count`既定5を必須引数化、`_merge_checkpoint`刈り込み |
| `er019_family_x_kp_explanation_01.py` / `er011_key_phrase_set_redundancy_qa_01.py` | §4-5 |

## 7. 撤去一覧(Gate 3後の別commit。Dangling Reference 0を受入条件とする)
| 撤去対象 | 識別子 | 残存確認Grep |
|---|---|---|
| X DB Hybrid/M2P0選定経路 | `_run_key_phrase_selection_db_hybrid_with_fallback`(scaffold:577-680)、`run_key_phrase_selection`のdb_hybrid分岐、`KP_ARTICLE_COST_CAP_JPY`判定(scaffold:875-885)、`er030_key_phrase_db_hybrid_selector_01.py`/`_m2_supply_01.py`/`_source_reference_contract_01.py`(Production到達なしを確認の上、ファイルは履歴・Trial用に残置可=import元ゼロにする) | `rg "kp_backend=\"db_hybrid\"|run_db_hybrid_selection|db_hybrid_with_fallback" er019* er026* er062* er063* er003_v1_n3_01_scaffold*`が0件 |
| Strategy L fallback(X) | `strategy_l_fallback`、`build_m2_fallback_record`、`format_m2_fallback_stdout`、`write_m2_fallback_notice`、runner `m2_fallback*`キー、`M2_RELATED_FALLBACK_REASON_CODES` | 同上+`rg "m2_fallback" er019* er026*`が0件 |
| X既定値 | er019:380 `kp_backend: str = "db_hybrid"` | Grep 0件 |
| 4+1(X/Z) | X/Zがrole依存検査を通らない=到達不能(旧validator自体はA/B/C用に残置) | X/Zモジュールに`key_phrase_role`参照が無いこと |
| 旧test | `er030_key_phrase_db_hybrid_family_x_production_wiring_01_test.py`、`er030_*_m2_fallback_notice_01_test_01.py`、`er030_*_m2_supply_01_test_01.py`、`er073_family_z_kp_db_hybrid_m2p0_migration_01_test_01.py`等(X Productionのdb_hybrid到達を前提とするもの) | RETIRE一覧をOPEN_ITEMSに記録(識別子つき) |
| **残置(撤去しない)** | `b1_p2_keywords_l_prompt_template.txt`(gloss規則抽出元)、`er030_key_phrase_db_hybrid_core_01.build_sentence_units`(Z D1・er105が使用)、旧Strategy L/4+1(A/B/C) | 残置理由をファイル先頭コメント+OPEN_ITEMSへ |
- 2 commit構成: **commit 1**=新backend配線+既定切替(旧経路はコード上残る→`kp_backend`既定値を戻すだけでrollback可)。**commit 2**=Gate 3(X/Z runtime evidence PASS)後に旧経路撤去+旧test RETIRE。

## 8. Store / KP3V(`er104`)・PNAP(`er103`)との整合
- **Store**: key=TTS正規化テキスト+style+version(rank・件数・選定方式に非依存。`er019_family_x_kp_en_k2_store_01.py`)。同一表現は3件化後も再利用可。Store manifest/既存entryは変更しない。
- **KP3V**(別管理ID KP-THREE-ASR-MAJORITY-PRODUCTION-01、置換対象=`er096_kp_dual_pass_01`のKP音声判定): 本件は「件数・選定のみ」。判定仕様はKP3V設計に従う。衝突候補(同一ファイルの別領域): `er019 runner`(KPFT=scaffold部:369-470・2722-2731 / KP3V=KP音声生成部:726-770、Store field `kp_dual_check→kp_vote_check`、X default key `+dual1→+vote1`)、`er063`(KPFT=:1405-1413・:1082-1094 / KP3V=`generate_or_reuse_z`のKP音声判定)。**領域は重ならない**が同一ファイルのため、配線時は`git status`→該当行再Grep→自分の行だけ→即commitの共有SSOT手順+配線順は独立(どちらが先でも可)。3件化でKP判定のASR呼出は40%減(INVESTIGATION §5-4)。
- **PNAP**(固有名詞アラーム、KP対象外): 衝突候補=`er019 runner`のtts stage入口(:990/:1388)、`er026 main`(:2060-2120)、`er063.run_tts_stage`入口、TTS供給点。KPFTのscaffold/KP stageとは別領域。KP英語フレーズは固有名詞アラームの対象外(PNAP設計)のため相互作用なし。

## 9. 試聴ページ・完成報告
rank駆動(INVESTIGATION #22-#24): X `er019:2150-2175`(`kp_by_rank`・`idx`)、Z `er063:1580-1640`(`kp_rows`)、共通`er_user_listening_page_common_01`(KP表・行数下限`>=5`は全行数でKP件数ではない)。**コード変更不要**。runtime evidenceで3件表示を確認し、完成報告にStandard/Advancedの3件(英語・日本語意味/英語解説・本文位置)を並記。過去ページ(5件)は無変更。

## 10. test計画
| 区分 | 内容 | 状態 |
|---|---|---|
| unit(実施済み・32件PASS) | Prompt 2逐語=USER.md一致/sha固定/旧5件文言なし、parse(厳密・自由文拒否)、本文照合(大小文字・アポストロフィ・ダッシュ・語境界・文またぎ)、検証(6語/4件/重複/創作/有限助動詞/0件)、先頭出現、declared_wc非ブロッキング、original_items契約(契約キー無し・窓拡張不発・canonicalization入力/merge/validate互換)、gate(retry/parse fail/invalid fail-closed/model mismatch/shortfall)、成果物・process/Luna照合、未配線(Production参照ゼロ)、保存Luna 70語句のreplay、原形化validatorプロトタイプ(受理10/拒否8) | PASS |
| 配線時追加(予定) | (1)DefaultOffIsolation相当: **A/B/C(`kp_backend="strategy_l"`既定)がバイト同一出力**(旧出力fixture回帰) (2)canonicalization: fulltext item→基本形化受理、別語置換拒否、A/B/Cでallow=False (3)gloss: gloss無しitem全件が生成対象、current無しの矛盾判定緩和、kill switch OFFでSTOP (4)X scaffold: 3/2/1件fixtureで`kp_stage_failure_status`・marker・外側retry・stale退避 (5)Z: `run_kp_with_outer_retry`+新backend、D1 gate冪等、legacy stage付替え (6)下流rank駆動: 組立(num_one〜three)/TTS plan/style gate M3/dual audit/ページ行/`_merge_checkpoint`刈り込み (7)explanation/redundancyの件数語 (8)5件fixture既存testの回帰(後方互換) (9)Dangling Reference Grep test(撤去識別子0件) | 次委任 |
| 回帰 | 既存`er003_test_*`/`er019_*test*`/`er026_*test*`/`er062*`/`er063*`/`er096*`/`er030*`(撤去分除く)全件。実行コマンドと件数を配線RESULTへ | 次委任 |

## 11. runtime evidence計画・見積(翌JST日=2026-10-23に実施。本日の既使用約878円との合算を避ける)
| 項目 | 内容 |
|---|---|
| X | 既存Family X記事1本(推奨 `coffee_prices`: `er019_output/coffee_prices/run_v5_ms_01/{a2,b1b}/article.md`の本文、Writer再実行なし)をKP stageから再実行 → 3KP → gloss → TTS(KP segmentのみ新規、非KP segmentは既存run由来でsha照合再利用)→ ASR → 組立 → 試聴ページ。新run dir(旧run無変更)。確認項目=USER.md §6の12項目(actual model ID `gpt-6-luna`、Prompt sha、3件以内、本文一致、原形化後KP、gloss、Adv解説、音声順序、retry/resume、Store hit、Dangling 0) |
| Z | Family Z 1本(melos。`er026_output/family_z_production_e2e_01/…`の最新PRODUCTION_WIRED runの本文・support・planを新run dirへ複製、`stage kp → tts_b1b → tts_a2 → provision_shell → gate → assemble → pages → page_verify`) |
| 見積(円) | KP chain(選定0.14〜0.2+canonicalization+gloss生成+Redundancy)≒0.7円/レベル×2=約1.4円。KP音声: 12clip(Std 3×(英+日本語意味)+Adv 3×(英+解説))×(TTS+ASR)≤1.0円/clip(Z E2E guard単価)=≤12円、Adv解説≈0.3円。**非KP segmentを再利用できれば X≈15円(上限20円)**、再生成になる場合は+約23円(BAPE E2E audio実績23.22円)で**上限40円**。**Z同様(≤20〜40円)。合計≤80円**(各ケース300円以下=7-7自律範囲、日次1,000円内)。上限を超える見込みなら実行前にSTOPして報告 |
| 失敗時の最終成果物 | KP stageが止まった場合: `kp_stage_failed.json`(X)/`FamilyZE2EStop`+`outer_retry/attempt_n`・`*.STALE_*`が最終成果物。旧KPが黙って採用されない |

## 12. ロールバック手順
commit 1(新backend配線+既定切替)のみで運用中に問題が出た場合: (a)`run_theme_scaffold`の既定`kp_backend`と`run_kp_stage`のselect_fnを旧値へ戻す(旧db_hybrid/Strategy L経路はcommit 2までコード上に残る)、または(b)`git revert <commit1>`。commit 2(撤去)後は`git revert`で撤去前へ戻す。過去記事・保存音声・Storeは無変更のため影響なし。

## 13. 量産単価・品質・速度への影響(推定。実測は配線後)
| 項目 | 変化(1記事セット=2レベル) | 根拠 |
|---|---|---|
| KP選定chain | 約-0.9円: 旧(Luna選定+canonicalization+gloss+Redundancy)Trial-03 Arm A 1.164円/レベル→新 約0.7円/レベル。選定0.418→約0.15円、後段は3/5件分に縮小、gloss全件生成+0.1円 | TRIAL_RESULT_03 §5、TRIAL_RESULT_02 Luna選定1.805円/14呼出 |
| 音声(TTS/ASR) | KP音声が約40%減。BAPE E2E audio実績23.22円×KP呼出比42%×(2/5)≒**-3.9円/セット** | raw_usage_log呼出数比(INVESTIGATION §5-4)=費用比の近似 |
| 解説生成(Adv) | 5→3件(1 call、微減) | schema len(items)導出 |
| 合計 | **約-4.8円/セット(70円目標の約7%)** ※推定 | 配線後に実測で置換 |
| 速度 | Wiktionary照会/shortlist構築(M2: `m2_lookup_seconds`)が消える。KP 1レベルのLuna呼出1回(約17秒、Trial実測)+後段 | Trial-02 A_Advanced 16.9秒 |
| 品質 | 本文一致・語数・件数は機械保証。原形化は決定論validatorで保証(Q1)。学習価値はユーザー決定のPrompt 2に従う(比較は行わない) | — |

## 14. 時間見込み(8-X)・並列化
配線委任(次): 約5〜6時間 = canonicalization/gloss拡張+test 2h、scaffold/X/Z配線+test 2h、件数語・可変長test 1h、SSOT/撤去準備 1h。並列化: (i)canonicalization+gloss拡張(共有module)と(ii)X/Z runner配線は**独立**(ファイル分離)で先行可能、(iii)Zの`_merge_checkpoint`刈り込みとtest、(iv)fulltext template作成は(i)と並行。runtime evidenceはXとZを**2 processで並列実行**可(別run dir・別台帳)。直列の理由=実APIは翌JST日のみ。

## 15. 11-7限定例外との関係
本件はユーザー`APPROVED_FOR_PRODUCTION`済みのため、フラグ(既定OFF)なしでProductionへ配線する。未承認機能の混入はない。ただし**Q1の原形化validator拡張**は新しい判定ロジックであり、承認済みRule7を変えるため、Opusレビュー(Q1)でGOを得てから配線する(fulltext item限定・A/B/C不変で影響範囲を限定)。
