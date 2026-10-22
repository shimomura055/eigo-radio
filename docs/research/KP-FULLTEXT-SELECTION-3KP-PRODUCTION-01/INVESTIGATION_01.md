# INVESTIGATION_01: KP全文選定(Prompt 2・Luna)+3件化 現状調査・5件前提の影響範囲

管理ID: KP-FULLTEXT-SELECTION-3KP-PRODUCTION-01 委任_01 / 2026-10-22 / 調査のみ(Production未編集・API 0・JPY0)
ユーザー原文: `docs/pm/delegation_log/2026-10-22_KP-FULLTEXT-SELECTION-3KP-PRODUCTION-01_USER.md`(7,212文字・sha256 `978e28102c4425dfb5cbcb48572e341bb8e32c2e3d33e4568f62773dc3b12c3d`)

## 0. 最重要の発見(Fable事前整理とのズレ。設計の前提を変えるもの)

| ID | 発見 | 根拠(file:行) | 設計への影響 |
|---|---|---|---|
| **F-1** | **Family Zは候補DB方式を使っていない**。Zの現行KP選定は**Strategy L(shortlistなし全文選定、LLMがsource_span/文を自由記述)**で、DB Hybrid/M2P0は**Xのみ**。Zは文ID/spanを選定後にPythonが付与するD1(`z_sentence_id_posthoc_v1`)方式 | `er062_family_z_writer_01.py:1015-1023`(`run_kp_stage`=`scaffold.run_key_phrases`既定`kp_backend="strategy_l"`)、`er026_family_z_fiction_production_runner_01.py:886,1488`、CURRENT_SPEC:1691(M2P0=Zは対象外)、:1977(D1)、:1984 | Zの変更は「DB撤去」ではなく**「Strategy L Prompt(4+1・5件)→Prompt 2(3件)への置換」**。Xが「DB Hybrid/M2P0→全文」。両者の共通点=最終的に`sc.run_key_phrase_selection`の新backend値1つ |
| **F-2** | **「原形化」(動詞を基本形へ等)を担う既存の後段工程は存在しない**。現行は**選定Prompt自体が基本形への整形を指示**し(`b1_p2_keywords_l_prompt_template.txt`:7「動詞表現は本文の時制を残さず、原則として基本形へ直してください」)、canonicalizationは「display_phraseの時制・単複・語順を戻さない」(canon template:5,13)+Rule7(`validate_canonicalization_item`: key_phraseがdisplay_phrase一致か**source_span内の連続部分文字列**か**人称一般化**のいずれか)。Prompt 2は「本文の語句を変更しない」ため、**全文選定ではdisplay_phrase=本文表層形(pushed prices up / gave back some gains)**になり、現行canonicalizationは基本形化(push prices up)を**Rule7で拒否する**(INVALID→retry) | `er003_key_words_canonicalization.py:487-535`、`er003_v1_translator_briefs/b1_p2_keywords_canonicalization_prompt_template.txt:5,13`。TRIAL_RESULT_02 §8-1判断B(原形化は新Trial/新仕様範囲)・TRIAL_DESIGN_02:29 | ユーザー文「既存の原形化・一般化工程は維持・再利用」は、**一般化(人称one's/someone's置換)=canonicalization Rule3は既存**だが**原形化は既存工程として存在しない**。設計で**canonicalizationへ「原形化(語形の基本形化)」を追加**する必要(IMPLEMENTATION_DESIGN §4-2)。承認済み品質(KPは基本形)を**維持する**ための追加であり品質基準の変更ではない、と整理(Opus確認) |
| **F-3** | **gloss(日本語意味)は選定LLMが生成していた**(Prompt 2は意味を出力しない)。Std「日本語意味」・Advanced英語解説の入力(`japanese_gloss`)・Z/XのKP gate・人称整合関所がすべてglossに依存 | `er003_key_words_canonicalization.py:707-775`(`japanese_gloss=original.get("ja_gloss")`)、`er003_key_words_gloss_alignment.py:147-162,253-259`(再整合の対象は「KPが候補に語を追加」「人称一般化」のitemのみ=gloss無しitemは対象外) | 全itemのglossを**後段で新規生成**する必要。既存gloss再整合工程(承認済みgloss規則を実行時抽出して再利用、item単位retry2・HR)を**「gloss無し=生成対象」に拡張**して再利用(設計§4-3)。旧selection template(`b1_p2_keywords_l_prompt_template.txt`)は**gloss規則の抽出元として残置が必須**(`load_approved_gloss_rules`)=削除不可 |
| **F-4** | **候補ID/source span契約は、X専用の`source_reference_contract`キーが真だとcanonicalizationの案A'窓拡張とgloss監査フラグが発火する** | `er003_key_words_canonicalization.py:230-249`(`expand_dangling_source_span`: `source_reference_contract`が真のitemのみ)、`:692-704`、`:762`(passthrough) | 全文選定itemには**このキーを付けない**(別キー`fulltext_source_ref`)。文ID/spanは選定時に決定論確定(Python)。Z D1 gate(`srcz.gate`)は`source_sentence`=unit全文なので`exact`解決でそのまま冪等に通る |
| **F-5** | **Z D1の「曖昧(複数文に出現)→STOP」規則を全文選定へそのまま持ち込むと破綻する**: 保存済みLuna実出力70語句のうち**14/70(20%)が複数文に出現**(conscientiousness/retail prices/refueling support等)。3件選定なら**約49%の単位で1件以上が曖昧STOP** | `/tmp`解析(本書§5-3、`er026_family_z_src_posthoc_01.resolve_item`を70語句に適用) | 全文選定では「同一表層語句が複数文にある」=曖昧ではなく同一学習語句。**先頭出現を決定論採用**し`occurrence_count`/`occurrence_sentence_ids`/`resolution_method=fulltext_exact_first_of_N`を記録(設計§3-3、Opus確認) |
| **F-6** | **既存の構造Validatorが、Prompt 2が許容する形を拒否する**: 保存済みLuna 70語句中**2/70(2.9%)が有限助動詞を含む**(`the stage is set`/`stretch what was said`)。既存canonicalization Validator(`:531`)は有限助動詞を拒否=後段でINVALID確定 | `er003_key_words_min_unit.validate_display_phrase_form`、`canonicalization.py:531-533` | 選定段でprecheck→retry(API費用の無駄な後段呼出を避ける)。**ルール自体は変更しない**(承認済み構造Validator。Opus確認事項Q4) |
| **F-7** | **canonicalization INVALID時の旧KP残存(KPMP B1)**はXにあり、全文選定+最小化圧力で発生確率が上がる(Trial-03のArm Bで2/14単位=14%がcanonicalization INVALID) | TRIAL_RESULT_03 §2(`er019_family_x_...runner:411-414`)、`er003_v1_n3_01_scaffold_generate.py:889-893`(INVALID時は即return・外側retryなし)、`er062:1055-1101`(Zのみ外側retry3回) | Xにも**canonicalization INVALID外側retry(通算3回、Zと同数)**を追加し、最終失敗時は旧attemptのKP成果物を`*.stale`へ退避(fail-closed、設計§5-2) |
| **F-8** | **canonicalization Promptは選定を「Listening Blocker Ranking」と記述し、QA項目にも`qa_listening_blocker_value_preserved`がある**。Prompt 2選定(上級者向け学習価値)とは前提が異なり、QAが不要なFAIL(REVIEW_REQUIRED)を出しうる。Promptには「5件の順位・選定そのものは変更しない」も残る | canon template:1,32,44、`canonicalization.py:76` | X/Z全文選定用に**canonicalization template複製(fulltext版)**を用意(旧templateはA/B/C用に無変更)。schema/QA項目名は不変 |
| **F-9** | **X/Zはstageの再利用で旧5件artifactを黙って使う設計**(Z `ensure_stage` sig=本文sha、Xは`_kp_already_generated`)。新コードでも過去run(5件)は変更されず可変長で読める=過去成果物は不変(要件OK)。ただし**同一run dirで`--regenerate-stage kp_*`して5→3へ縮む場合、Zの`_merge_checkpoint`(er063:1089-1094)が旧rank4,5のTTS結果を保持しうる** | `er063_family_z_audio_01.py:1082-1094` | 設計§6: cached `key_phrases`を現KP rank集合へ刈り込む1関数+test |

## 1. 現行経路図(file:行)

### 1-1 Family X(正式初回)
```
er019_family_x_audio_production_runner_01.py:378 run_theme_scaffold(kp_backend="db_hybrid")           ← 既定値
  :418 kp_dir = {level_out_dir}/key_phrases / :439 sc.run_key_phrases(article_text, kp_dir, article_id, level, process=B1_SUPPORT|A2_SUPPORT, kp_backend)
er003_v1_n3_01_scaffold_generate.py:802 run_key_phrases  (gloss_align.preflight / HR notice)
  :836 _run_key_phrases_impl: for attempt in 0..KEY_PHRASE_REDUNDANCY_RETRY_MAX(=2):
    :869 run_key_phrase_selection(kp_backend="db_hybrid") → :577 _run_key_phrase_selection_db_hybrid_with_fallback
         → er030_key_phrase_db_hybrid_selector_01.run_db_hybrid_selection (M2P0候補供給=m2_supply/Wiktionary、shortlist cache、候補ID契約、4+1 role)
         → DbHybridFailure で Strategy L fallback(:351、M2不発火=ユーザー報告必須 :537 build_m2_fallback_record)
    :889 run_key_phrase_canonicalization(:683) → kc.run_canonicalization_gate → kc.merge_canonicalization_result
         → gloss_align.align_glosses(:755, 既定ON)  → keywords_canonicalized.json 書込(:742)
    :896 run_key_phrase_redundancy_qa(:748, num_items可変) + 記号検出(:907) → NG時は選定からやり直す
  :446 kp_stage_failure_status(:352): run_status∈(NG_REVIEW_REQUIRED,OUTER_RETRY_EXHAUSTED,KP_ARTICLE_COST_CAP_EXCEEDED) or canon非PASS → FamilyXKPStageFailed(fail-closed,marker)
後段: KP source gate(er003_key_phrase_source_gate_01: source_span/source_sentenceが本文に実在) → TTS(kp{rank}_en/ja or explanation) → ASR(er096 dual→KP3V予定) → assemble(rank駆動) → 試聴ページ
```
### 1-2 Family Z(正式初回)
```
er026_family_z_fiction_production_runner_01.py:1470 stage_kp: for lv in (b1b,a2):
  :1488 w62.run_kp_stage(lv,text,out_dir,slug,kp_fn=_kp_fn_for_ctx) → er062:1015 → fn= er062:1055 run_kp_with_outer_retry
      select_fn=sc.run_key_phrase_selection(kp_backend既定"strategy_l"=Strategy L全文) → canon_fn → redundancy_fn、canonicalization INVALIDのみ外側retry(通算Z_KP_OUTER_RETRY_MAX=3)、
      Z_KP_GENERIC_NOTE(所有格代名詞を避ける注意)を毎回selection promptへ付加
  :1497 _gloss_hr_gate / :1503 _gloss_person_gate / :1506 collect_unevaluated / :1509 _src_gate(Z D1, er026_family_z_src_posthoc_01.gate) / :1510 install_kp_assets
  :1520-1555 Adv英語解説(kexp.generate_kp_explanations、sigはdisplay_phrase+gloss+source_sentence_id)
後段: load_level_inputs(:1557) → er063.build_level_plan(kp_items可変) → TTS → gate → assemble → pages
```
### 1-3 契約・後段依存(新経路が壊してはいけないもの)
| 下流 | 読むフィールド | 全文選定での充足方法 |
|---|---|---|
| canonicalization入力 | `rank, display_phrase, source_span, source_sentence`(`kc.build_user_message:293`) | 全て選定時に決定論確定 |
| canonicalization出力merge | `ja_gloss/japanese_gloss`(:728)、passthrough(`source_reference_contract`等)(:759-770) | gloss=None→後段生成(F-3)。`source_reference_contract`は付けない(F-4) |
| gloss再整合 | `key_phrase, display_phrase, japanese_gloss, source_sentence` | 対象選定に「gloss無し」を追加 |
| KP source gate (a) | `source_span`/`source_sentence`が現行本文に実在 | 原文スライス=実在保証 |
| Z D1 gate | `source_sentence_llm or source_sentence`+`source_span` → 文ID | unit全文=`exact`解決 |
| Adv英語解説 | `rank, display_phrase, source_sentence, japanese_gloss` | 同左 |
| Store key / TTS reuse | `used_form`のTTS正規化テキスト+profile(rank非依存) | 件数と無関係に再利用可 |
| 4+1 role (`key_phrase_role`) | `validate_min_unit_selection`(5件経路のみ)、canonicalization passthrough | Prompt 2はrole出力なし=**全文選定ではrole概念を持たない**(§4-4) |

## 2. 5件前提の全箇所と分類(Production到達・X/Z関連。網羅Grep: `kp[1-5]_|PRODUCTION_ITEM_COUNT|== 5|range(5)|num_five|5件|5個|5つ|five|[:5]|ranks`等をX/Z関連module 60ファイルに適用+全rank駆動箇所を手読み確認)

凡例: **C**=X/Z経路を3へ定数化/置換 **V**=既に可変長(変更不要・要test) **D**=文言/docstring/Prompt内の件数語のみ更新 **R**=X/Z経路から撤去 **K**=A/B/C共有の旧経路として無変更で残置(開発対象外・27-7) **T**=test更新/追加

| # | 箇所(file:行) | 内容 | 分類 | 処置 |
|---|---|---|---|---|
| 1 | `er003_key_words_production.py:37,78-79,152,161,175` | `PRODUCTION_ITEM_COUNT=5`、Strategy L schema min/maxItems=5、validator expected=5 | K | A/B/C共有。X/Zは新backendで経由しない |
| 2 | `er003_key_words_min_unit.py:57,498` | `PRODUCTION_ITEM_COUNT_UNCHANGED=5`、4+1(topic=1/important=4)集計検証 | K | 同上。X/Zでは到達しない(Prompt 2はrole無し) |
| 3 | `er003_v1_translator_briefs/b1_p2_keywords_l_prompt_template.txt:1,25` | 「ちょうど5個」「5個のうち1個はtopic」 | K+残置 | A/B/C用。**X/Zではgloss規則の抽出元として必須残置**(F-3) |
| 4 | `er003_v1_n3_01_scaffold_generate.py:296-348` | `run_key_phrase_selection`のbackend分岐 | C | 新値`fulltext_p2`を追加(X/Z)。`db_hybrid`値を**撤去**(R, #5) |
| 5 | `…scaffold_generate.py:577-680,537-575` + `er030_key_phrase_db_hybrid_selector_01.py`/`m2_supply_01`/`source_reference_contract_01`/telemetry/M2 fallback notice | DB Hybrid/M2P0選定・Strategy L fallback・M2 fallback報告 | R | X経路から撤去(Production到達ゼロ化)。`er030_key_phrase_db_hybrid_core_01.build_sentence_units`(文分割。Z D1も使用)は**残置**。履歴/Trialスクリプトは無変更 |
| 6 | `…scaffold_generate.py:836-923`(`_run_key_phrases_impl`) | `KP_ARTICLE_COST_CAP_JPY`判定(db_hybrid限定)、canonicalization INVALIDで即return | R+C | cap分岐撤去、全文backend用にcanonicalization外側retry(通算3)+stale退避を追加(F-7) |
| 7 | `er019…runner:378-470,2722-2731` | `kp_backend="db_hybrid"`既定、`m2_fallback_events`、`kp_backend_used_by_level` | C+R | 既定`fulltext_p2`。m2_fallback系(summary/notice/stdout)撤去 |
| 8 | `er019…runner:372` `_kp_already_generated` | 検出名に`key_phrases_db_hybrid` | C | 新成果物名に更新(`--scaffold-only kp`の1回制約) |
| 9 | `er019…runner:1574,1859` | 共有shell音声`num_one..num_five`を全読込 | V(+D) | rank駆動のため動作は3件で正常。読込をkp件数に限定(任意) |
| 10 | `er003_v1_n3_01_assemble.py:670-680,868-880` | `num_names[rank-1]`/`[i]`(rank駆動) | V | 3件→one..threeのみ使用。test追加 |
| 11 | `…assemble.py:387` `derive_a_family_required_structure` | `key_phrase_ranks:5` | K | A-Family専用。X/Z(er019/er026/er063)は呼ばない(Grep確認) |
| 12 | `er063_family_z_audio_01.py:1405-1413` | `NUMBER_ASSET_SOURCES`5件、`provision_shell_assets(kp_count=5)`既定 | V+C | 呼出(er026:1641)は`len(kp_items)`渡し済み。既定引数5を必須引数化 |
| 13 | `er063…:1453,535-545,1576` | KPブロック・clip plan(rank駆動) | V | test追加 |
| 14 | `er063…:1082-1094` `_merge_checkpoint` | 旧rankのTTS結果を保持 | C | 現KP rank集合へ刈り込み(F-9) |
| 15 | `er026…:1641,1885` | `len(kp_items)`(V)/mockの`[:5]`(C) | V/C | mock候補3件に |
| 16 | `er026…:1470-1555` stage_kp | rank駆動。`E2E_STAGE_EST_JPY["kp"]=10.0`見積 | V+D | 見積は過大側のまま許容(任意で更新) |
| 17 | `er062_family_z_writer_01.py:1015-1100` | `run_kp_stage`(Strategy L記述)、`Z_KP_GENERIC_NOTE`(代名詞回避注意) | C | 新backendを渡す。generic noteは全文backendでは付けない(Prompt 2逐語。設計§5-3) |
| 18 | `er019_family_x_kp_explanation_01.py:69,90,239` | 英語解説Promptの件数語「5 Key Phrases」「x5」、docstring「5件(4+1構成)」 | D | 件数をf-string化(n)。PROMPT_SHA256のTrial-02逐語性は5件版で維持+n置換のtest。schemaは既にlen(items)導出(:124-136) |
| 19 | `er011_key_phrase_set_redundancy_qa_01.py:3-12,35` | developer message「Key Phrase 5件」(本文templateは`{num_items}`可変) | D | `{num_items}`化。1件(shortfall)時のペア0件の扱いをtest |
| 20 | `canonicalization templates`(`b1_p2_keywords_canonicalization_prompt_template.txt:44`) | 「5件の順位・選定そのものは変更しない」、Listening Blocker記述 | D(+F-8) | X/Z用fulltext版templateを新設(旧はA/B/C用に無変更) |
| 21 | `er003_key_words_gloss_alignment.py:253-259,573-630` | 再整合対象にgloss無しが含まれない | C | 「`fulltext_source_ref`付きでgloss無し」を生成対象に追加。消費側にも「gloss欠落」STOPを追加(kill switch OFF時の無gloss素通り防止) |
| 22 | `er019_family_x_style_profile_01.py:637-655`、`er019_family_x_validation_inheritance_01.py`、`er096_kp_dual_pass_01.py:281-289` | results.key_phrases[rank]走査(rank駆動) | V | test追加。KP3Vが置換予定(§7) |
| 23 | `er019_family_x_kp_en_k2_store_01.py`(Master Audio Store key A/B) | key=TTS正規化テキスト+style+version(rank・件数非依存) | V | 変更不要。同一表現は件数に無関係に再利用 |
| 24 | `er_user_listening_page_common_01.py:190`(`len(rows)>=5`)、`er063:1580-1640`、`er019:2150-2175` | 試聴ページの行数下限・KP行(rank駆動) | V | `>=5`は**全行数**(Preview/Comment/Full Story等)で、KP件数ではない(3KPでも≧10行)。KP表示はrank駆動。test追加 |
| 25 | `er003_audio_tts_asr_safety.py:668`(`_INTERNAL_LABEL_ORDINAL_WORDS` One…Five)、`tts_generate.py:949`(数字語辞書) | 内部ラベル/数詞検出辞書 | K | 検出辞書でありKP件数前提ではない |
| 26 | CURRENT_SPEC:1953-1956(「件数 5件/記事」`DECIDED`、Strategy L/Canonicalization記述)、:1975(4+1)、:1982-1984(M2P0)、DECISION_LOG該当 | SSOT上の旧仕様 | SSOT | 「X/Z限定で全文選定・3件・roleなしに置換。A/B/Cは旧仕様のまま」を追記(追記文案はRESULT_PACKET) |
| 27 | Tests(5件fixtureを持つX/Z系): `er019_family_x_audio_production_runner_01_test_01.py`(3箇所)、`er019_family_x_fx_20261016_wiring_01_test_01.py`(14)、`er019_family_x_kp_structure_wiring_01_test_01.py`(6)、`er019_family_x_opus_l2_fixes_01_test_01.py`(13)、`er019_family_x_style_profile_01_test_01.py`(6)、`er019_test_family_x_completion_02_integration.py`(5)、`er026_family_z_e2e_integration_test_01.py`(9)、`er063_family_z_audio_01_test_01.py`(9)、`er096_*_test`(2) | 5件fixtureはrank駆動の可変長挙動のテストとして**残して有効**(後方互換の証明)。3件版を追加 | T | 5件fixtureは後方互換回帰として残置+3件/2件/1件fixtureを追加。db_hybrid系test(`er030_*_wiring_01_test`/`m2_*_test`/`er073_*_test`)は撤去対象(R)として配線時にRETIRE |
| 28 | 過去記事・保存音声・Store既存entry | 5件のKP・音声 | 不変 | 再生成しない(可変長で読めるため)。新run dirのみ3件 |
| 29 | `er026_family_z_fiction_production_runner_01.py:866-891,2054`(legacy `--stage keyphrase` `run_keyphrase_stage`、process=None Strategy L) | 正式E2E(stage_kp)と別のlegacy CLI。Strategy L・5件でZのProduction到達経路になりうる | C/R | 新backendへ付替えまたは撤去(設計§6) |

集計: C=9 / R=3(主要) / D=4 / V=11 / K=5 / T=2群 / SSOT=1 / 不変=1。**旧5件前提でX/Z経路に残るもの=D・Cを処置すれば0**(K=A/B/C共有旧経路は27-7により無変更で残置し、X/Zからは到達しない)。

## 3. retry/fallback/regeneration/resumeの現状(新方式での整合方針は設計書§5)

| 機構 | 現状(file:行) | 新方式との整合 |
|---|---|---|
| 選定retry | Strategy L: `MAX_PRODUCTION_RETRY_ATTEMPTS=2`(er003_key_words_production.py:164、技術失敗/hard requirement不適合のみ)。DB Hybrid: 内部attempts+cost cap | er105: 同じ上限2、同じ対象(技術/parse/検証) |
| Redundancy/記号NG retry | `KEY_PHRASE_REDUNDANCY_RETRY_MAX`(=POINT_OVERLAP_ARTICLE_RETRY_MAX=2)(scaffold:781)。selection→canon→redundancyを再実行。diagnostic_noteをpromptへ付加 | 同じループを共用。noteは**Prompt 2本文の後ろ**に後置(逐語性保持) |
| canonicalization INVALID | Xは即return(F-7)/Zは外側retry通算3(er062:1031) | X/Z同数(3)に統一(X追加) |
| Fallback | XはDB→Strategy L fallback(M2不発火=ユーザー報告必須)。Zなし | **撤去**(候補DB前提を取り除く趣旨)。失敗=stage失敗(fail-closed)。Opus確認 |
| fail-closed | X: `kp_stage_failure_status`+marker `kp_stage_failed.json`(er019:347-361,446-)、Z: `FamilyZE2EStop`(stage_kp:1491-1494) | 共用。新status文字列は既存と同値(`KEY_WORDS_STRUCTURE_INVALID`等) |
| regeneration | X `--scaffold-only kp`(KP再生成は1レベル1回、`_kp_already_generated`)、Z `--regenerate-stage kp_<lv>` | 検出名を更新(#8)。成果物ディレクトリ名変更に追随 |
| resume | X: stage単位、Z: `ensure_stage`(本文sha provenance)+gloss HR snapshot(`_load_gloss_hr_resume`) | 旧5件artifactは可変長で読める。同一run dirの5→3再生成はstale rank刈り込み(F-9) |
| Store再利用 | key=TTS正規化テキスト+profile | 件数無関係に再利用可(#23) |

## 4. 参照した既存仕様(整合確認の一覧)
CURRENT_SPEC:596,645-651(KP選定: Strategy L+Canonicalization、A2は自本文から選定)、:839(Standard=6,000語ライン、KPで学習補助)、:1691(M2P0=X固有、Z対象外)、:1953-1956,1966-1973(Canonicalization・人称一般化・DB Hybrid)、:1974-1977(候補ID契約・Z D1)、:1975(4+1)、:1986-2000(KP音声構造: Std=英→日本語意味→英/Adv=英→英語解説→英)、:2509(KP選定・正規化=gpt-6-luna)。TRIAL_RESULT_02 §8、TRIAL_RESULT_03 §2・§5・§7(第3条追加REJECTED=現行DB経路への追加であり、今回のユーザー採用決定[Prompt 2全文選定]とは別事項)。

## 5. 実測根拠(API 0・保存データのみ)
### 5-1 保存Luna出力の機械検証(`er101_output/.../runs/n1_gpt-6-luna` 14単位×5=70語句、5件版Promptでの出力)
- 本文連続一致 69/70(不一致1: E_Standard `passed the baton`=本文に無い→設計の機械検証でretry対象になる実例)、語数≤5は70/70、平均3.14語。
- 有限助動詞を含む形 2/70(F-6)。人称代名詞/所有格を含む 7/70(`pumps its fist`等→canonicalization Rule3で一般化される経路)。
### 5-2 品質面の根拠(Standard/Advanced)
Standard 7単位35語句は全単位5件選定された(`pumps its fist` / `keep raw beans in stock` / `think up` / `take over`等)。条件がより厳しい3件選定でStandardが「候補不足」になる可能性は低い(LEVEL_SPEC_CHECK_01.md)。
### 5-3 複数文出現(F-5)
`resolve_item`(Z D1)を70語句に適用: ambiguous 14 / unresolved 1 / 一意 55。`conscientiousness`(B)、`retail prices`(A_Adv)、`weakly linked`(B)、`refueling support`(F)、`sea blockade`(G)ほか。
### 5-4 3件化のTTS/ASR呼出削減(Family X paycheck run_pp_02 raw_usage_log、5KP×2レベル)
API呼出行114のうちKP segment 48(42%)=KP1件あたり約4.8呼出(Gemini batch TTS 18、OpenAI ASR 18、Azure ASR 9、OpenAI responses 3)。3件化で**全体の呼出約17%減、KP関連は40%減**(推定、費用ではなく呼出数比)。出典: `er019_output/family_x_audio_production_wiring_01/paycheck_personality__run_pp_02/raw_usage_log.jsonl`。
