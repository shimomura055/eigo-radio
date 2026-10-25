# PART1_WIRING_SPEC_CHECK_01(Part 1「Vocabulary & Expressions」案α Production Wiring Phase 0: 既存経路調査)

管理ID: FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_13 / 日付: 2026-10-25 / API 0円・Production file編集0(読取専用)
Status: **APPROVED_FOR_PRODUCTION(配線設計中・未配線)**。PRODUCTION_WIREDではない。ユーザー原文=`docs/pm/delegation_log/2026-10-25_FAMILY-Z-STUDY-TEXT-TRIAL-01_USER_05.md`(Part 1は:10-15, 28-54, 56-)。委任文=`..._DELEGATION_13.md`(index 530)。
調査時点のHEAD=`e5ebe03bb`。追跡済み(tracked)の`.py`に未commit差分なし(`git status`で` M`/`M `の.pyは0。`??`のuntracked .pyのみ)。以下のfile:行はこの時点の値(並行agent[FZ-SOURCE-ESSENCE 委任_04等]が編集すると行番号が動く。実装委任の冒頭で再照合すること)。
参照ファイルのblob sha(実装前の再照合用、`git hash-object`): er026 runner=`cc05ce0c9`、er019 audio runner=`2e3901cde`、er003 scaffold=`bbca86f4f`、er062 writer=`84790c21c`、er063 audio=`c2ce68722`、er_user_listening_page_common_01=`a8f653193`、er006 routing=`b7efce7a5`。

## 0. 結論(先に)
1. **現行Productionに「Part 1(語彙・表現の日本語解説)」を生成する箇所は存在しない**(置換対象なし)。`Vocabulary & Expressions`・`実用性を重視した解説`・`英語学習テキスト`を`*.py`/`*.md`(docs/research・delegation_log・`.claude`除く)でGrepした該当は`DECISION_LOG.md`(Trial記録)のみ。Trial-03の03d方式も、それ以前の方式も、Productionには配線されていない(ADOPTION_NOTE_04 §1「Productionに存在しない」と一致)。→ **新しい独立段の追加**であり、旧Part 1生成コード・Prompt・testの撤去対象は0。
2. 現行ProductionのKey Phrase表示は「英語/日本語の意味(+Advancedは英語での説明)」の表(Z=`er063_family_z_audio_01.py:1957-1975`、X player=`er019_family_x_audio_production_runner_01.py:2144`)。Advancedの「英語での説明」=`kp_explanations.json`(音声用の短い英語定義、`er019_family_x_kp_explanation_01.py`)で、**日本語の一般解説(Part 1)とは別成果物**。置換せず並存させる(役割が異なる。DESIGN_04 §1)。
3. **「本文引用英文の日本語訳」は既存の承認済み方式では解決できない**(§5)。X/Zとも、KP itemが持つのは英語の`source_sentence`のみで、日本語訳の生成元(LLM/辞書/Writer対応)はどこにも無い。→ 新しい有料生成工程(または訳欄を出さない仕様)が必要=ユーザー判断事項(`判断候補`、後述)。
4. Part 1の「ユーザー向け出力の置き場」は現行に無い(§3)。Zには共通のページbuilder(`build_pages`)があるが、Xには共通builderが無く(per-article page script + runner内部`player.html`)、Xのユーザー向けページ組込みは別扱い(DESIGN_01 §9)。

## 1. 現行のKey Phrase確定点と下流(X/Z別)
### 1-1. 共通KP段(X/Z共通・正式backend)
| 項目 | 場所(file:行) | 備考 |
|---|---|---|
| KP確定の入口 | `er003_v1_n3_01_scaffold_generate.py:875` `run_key_phrases(..., kp_backend="fulltext_p2")` | X/Z共通の外側retry(`run_kp_with_outer_retry`)へ振り分け(:884-890)。最後にgloss HR報告を1回(:894-906) |
| 全文選定backend | 同:348 `FULLTEXT_BACKEND_ID="fulltext_p2"`、:351 `_run_key_phrase_selection_fulltext` | 最大3件。fail-closed(旧経路へfallbackしない) |
| canonicalization+gloss再整合 | 同:475 `run_key_phrase_canonicalization`(hook=:502-505 `postprocess_possessor_roles`、gloss=:526-545) | `keywords_canonicalized.json`(:551)を書く。`japanese_gloss`/`used_form`/`source_sentence`/`gloss_alignment_status`を持つ |
| gloss(本文中の意味) | `er003_key_words_gloss_alignment.py:95`(`japanese_gloss`)、:128 `NEWGEN_MEANING_FIELDS=("meaning_in_text_en","naive_ja","naive_ja_conveys")` | 「本文で使われている語義」を表す設計。Part 1の解説LLMには渡さない(`meaning_in_text_en`も) |
| 引用英文 | KP item `source_sentence`(Zは`er026_family_z_src_posthoc_01.py`のSRC D1で決定論復元・逐語保証[:44-45,255,278]、Xは全文選定`fulltext_exact_v1`) | 日本語訳フィールドは存在しない(実item dump: `er026_output/.../the_tell_tale_heart/run_sf_prod_02/key_phrases/b1b/keywords_canonicalized.json`) |
| 解説用の表現形 | `er019_family_x_kp_explanation_01.py:145` `explanation_phrase(item)`=全文選定itemは`used_form`(基本形化後) | Trial-04の英語表現(`hand down`/`catch one's breath`等)と同じ基本形。Part 1の入力もこれを使う |

### 1-2. Family Z(正式経路`er026_family_z_fiction_production_runner_01.py`)
- stage順(:1128) `seed_check, writer, std_adjust, plan, support, kp, tts_b1b, tts_a2, provision_shell, gate, assemble, pages, page_verify`。
- `stage_kp`(:1692): b1b→a2の順に`w62.ensure_stage(prov, f"kp_{lv}", _sha(text), ...)`(:1719)→HRゲート(:1716)・人称整合関所(:1726)・SRC D1(:1731)→`install_kp_assets`(:1732)。続けてb1bのみ`kp_expl_b1b`(Advanced音声用英語解説)を`ensure_stage(prov, "kp_expl_b1b", sig, ...)`(:1776)。sigは`explanation_phrase`の並び(+glossあれば`gloss`・SRCあれば`source_sentence`を含む、:1747-1761)。**失敗は`FamilyZE2EStop`(:1773 `FAMILY_Z_KP_EXPLANATION_NOT_OK`)でTTS前に停止**。
- resume/regenerate: `er062_family_z_writer_01.py:690 ensure_stage`(出力+entry+input_sha一致=reuse / input_sha不一致=`FamilyZProvenanceMismatchStop` / stale=明示`--regenerate-stage`必須 / regenerate=置換+子孫stale化)。`DEPENDENTS`(:64-67)に`kp_expl_b1b`は無く、`--regenerate-stage`の選択肢は`ALL_STAGE_NAMES`(:68)+`E2E_KP_EXTRA_REGEN_NAMES=("kp_expl_b1b",)`(runner:1134)。KP再生成でsigが変わると`kp_expl_b1b`は**自動再生成されず`ProvenanceMismatch`でSTOP→`--regenerate-stage kp_expl_b1b`が必要**(既存の安全側仕様)。
- ページ: `stage_pages`(:1897)→`er063_family_z_audio_01.py:1985 build_pages`→`_user_page_rows`(:1918)でKP行を`uc.kp_block(heads, cells)`(Advancedは`["英語","日本語の意味","英語での説明"]`、:1957-1966)。標準適合check=`er_user_listening_page_common_01.py:140 check_page`(C3 KP=class`kp`のtable、2列以上、:201-208)。`stage_page_verify`(:1930)でも必須。
- budget guard: `_guard(ctx, name, est_jpy)`(例:1766)。LLM client=`ctx.llm_client`、test hook=`ctx.hooks.get("expl_call_fn")`。

### 1-3. Family X(正式経路`er019_family_x_audio_production_runner_01.py`、Entertainment入口は`er019_family_x_entertainment_production_runner_01.py`でStandard生成までで停止しKP/audio/pageは持たない)
- `scaffold` stage: `run_theme_scaffold`(:387)で各level(b1b→a2)に対し本文3分割→support→`sc.run_key_phrases(...kp_backend="fulltext_p2", stop_run_dir=out_dir)`(:443)。PASS系以外は`kp_stage_failure_status`(:357)→`kp_stage_status`をresultへ記録(:477)→`main()`が`rc=3`(:2706-2717)で後段へ進めない。
- `tts` stage: Advanced KP英語解説は`_resolve_kp_explanations_text`(:1069)で**signature(`explanation_phrase`並び[+gloss_signature])が前回と一致すればreuse、1件でも違えば全件再生成**(Zと違い自動)。cacheは`tts_generation_results.json`の`key_phrase_explanations_text`。
- 再実行経路: `--stage scaffold`の再実行(KPは毎回`run_key_phrases`)、`--scaffold-only kp`(KP再生成は1レベル1回、:398-411)。Local Rewrite等で本文が変われば`source_dir`の`article.md`が変わりscaffoldからやり直す。HR(gloss未解決)はscaffoldを止めず、消費側(`_assert_no_gloss_alignment_hr`:1767、`_build_level_table`:2233)で止める。
- ページ: Xの共通ユーザー向けpage builderは無い(CURRENT_SPEC 2927: 「Family X側ページ生成[`er019_bape_page_04.py`等・X runner `player` stage]は無変更」)。runner内部`build_player_html`(:2280)のKP行はAdvanced=`EN: / EXPLANATION: / EN (repeat)`(:2177)。

## 2. 現行の品質検査・意味整合性確認の所在(維持対象。Part 1は変更しない)
- KP qa 12項目(canonicalization)、Redundancy QA(`run_key_phrase_redundancy_qa`:557)、gloss再整合・HR(`er003_key_words_gloss_alignment.py`)、人称・指示対象整合関所(Z `_gloss_person_gate`:1726)、SRC D1(Z)。**これらはKP確定までの検査で、Part 1はその後段に置くだけ**(「既存のKey Phrase選定・日本語意味確定工程を不要に変更しない」)。
- Part 1自体に新しいValidator/Checkerは**新設しない**(DESIGN_04 §7、ADOPTION_NOTE_04 §5。構造parse検査のみ)。ユーザー原文§2「既存の品質検査や意味整合性の確認は維持」=上記を指す。解説と本文中の意味(gloss)の矛盾(例: `at a moment's notice`の即応寄り)は、Trial-04でユーザーが把握済み・追加Trial不要と判断済み。

## 3. 「ユーザー向け出力」の現行の置き場
| 出力 | Z | X |
|---|---|---|
| 完成ページ(ユーザー試聴) | `pages/index.html`(`build_pages`、標準フォーマット`uc.render_standard_page`)。KP表=3列(Adv) | per-article page script(`er019_*_page_*.py`等、runnerの外)。runner内部は`player.html` |
| Part 1(確定KP+本文中の意味+引用英文+日本語訳+解説) | **無い** | **無い** |
→ Part 1は新しい成果物。最小設計=`study_text/part1_vocabulary_expressions.{json,md}`をrun配下に出力(X/Z共通)+Zは`build_pages`のAdvanced節へ表示block追加(DESIGN_01 §9)。標準適合checkの拡張を伴うためOpus論点に含める。

## 4. TrialとProductionの仕様差分表(案α)
| 項目 | Trial-04(`run_trial_04.py`) | Production(提案) | 差分の扱い |
|---|---|---|---|
| Prompt | `P1_HEAD`+「# 解説する英語表現」+`P1_BODY`(:74 `p1_prompt(kps,"alpha")`)。PROMPT_04.md §1 | **同一(バイト一致)**。`_prompt_04_<work>_p1a.txt`3件との一致をtestで固定 | 差分なし(新Prompt改善はしない) |
| 入力 | KPの英語表現のみ(本文・あらすじ・gloss・引用文・作品名なし。dry-runで混入0確認) | 同。`explanation_phrase(item)`=`used_form`のみ。型を`list[str]`に限定し、gloss/引用/本文はコード上受け取れない | 構造とtestで保証(DESIGN_01 §3) |
| 件数 | 3KP固定(Trial) | 1〜3件(Production全文選定は最大3、shortfallで1〜2もあり得る) | Promptは番号付き列挙で件数に依存しない。N=1,2のtestを追加 |
| モデル | `gpt-6-luna`を直接指定(`responses.create(model="gpt-6-luna", input=[user])`、推論effort指定なし、:294) | `routing.require_model("KEY_PHRASE_GENERAL_EXPLANATION", SUPPORT_MODEL)`(=`gpt-6-luna`、`er006_model_routing_contract_01.py:50,126`)。応答model不一致はfallbackせずSTOP | モデル同一。routing経由に変更(Production標準)。最新世代原則(25節)と整合: SUPPORT_MODELは現行最新の推奨系Luna |
| API形式 | `client.responses.create(model, input=[{"role":"user","content":prompt}])`、Markdown出力 | 同形式・同パラメータ(reasoning effort/JSON schema/developer messageを**追加しない**=Trial条件維持) | 差分なし |
| 出力形式 | `### N. <表現>`+自然文Markdown。`parse_p1`(:194)はN個の番号見出しを要求 | 同。加えて**見出しの表現が入力と一致**することを構造検査(Trialは番号のみ)。parse失敗は技術retry1回→STOP | 軽微な安全強化(判定器でなく構造保証。既存`kp_explanations`の「parse失敗retry1回」踏襲) |
| 表示名 | 「5 解説」(旧「実用性を重視した解説」は不使用) | 「解説」 | 差分なし |
| 本文中の意味(2項) | Production `japanese_gloss`を確定値として表示 | 同(`keywords_canonicalized.json`の現在値を**描画時に**読む。HR未解決glossは出さない) | 差分なし(glossはHR解決後の値に自動追従) |
| 引用英文(3項) | `source_sentence`(本文逐語) | 同+描画時に本文との逐語照合(決定論assert。LLMなし) | 軽微な安全強化 |
| 日本語訳(4項) | 03d標本の訳を`INPUT_04.json`に**固定流用**(評価対象外) | **生成元なし=未解決**(§5) | **ユーザー判断事項** |
| 呼出 | P1:1 call/作品(+Part 2〜4は別) | b1b(Advanced)のみ1 call/記事セット。Part 2〜4は含まない(Part 2は未採用・保留) | Part 1のみ配線 |
| retry | なし(失敗は例外停止) | 技術retry1回(parse/構造)→`KpGeneralExplanationError`→X/Z既存のfail-closed STOP | 既存`generate_kp_explanations`と同方針 |
| 実費(実測) | 6 call平均**0.0775円/call**(範囲0.0689〜0.0889円、`usage_04a_*`、input 686〜688・output 724〜974token、10.8〜13.5秒) | 同(+記録) | §DESIGN_01 §10 |
| 来歴記録 | `usage_*.json`(model/prompt_sha256/token/cost) | audit(model_id/prompt_sha256/input_sha256/response_id/cost)を成果物と同階層に保存 | 追加(Production要件) |

## 5. 「本文引用英文の日本語訳」の生成元の再調査(結論)
- 調査範囲: `CURRENT_SPEC.md`(Grep `引用英文|英文の日本語訳|本文の日本語訳|対訳|source_sentence_ja|sentence_ja`=0件)、全`*.py`(`source_sentence_ja|sentence_ja_translation|translate_sentence`=0件)、実item dump(`source_sentence`のみ、訳フィールド無)、`keywords_canonicalized.json`の`gloss_alignment`(`naive_ja`/`meaning_in_text_en`はKP表現の訳であり引用文の訳ではない)。
- Z: 原文は英語(Writerは英語本文のみ。日本語本文なし)。日本語は`japanese_title`とKP gloss程度で、文単位の日本語訳は存在しない。
- X: Writerは日本語原稿(`ja_writer/revision2.md`)→忠実英訳(`generate_family_x_faithful_translation`、CURRENT_SPEC:1413)。日本語原稿は存在するが、**KP引用英文と日本語原稿の文対応を作る工程は無い**(新規アライメントが必要)。
- A/B/Cの`user_test/translations/*/translation_ja.json`(CURRENT_SPEC:2675-2680)は旧Familyの節単位訳でX/Zと無関係かつ生成スクリプトが追跡対象に無い(開発対象外27-7)。
- **結論: 既存の承認済み方式では解決不可**。選択肢はDESIGN_01 §11(T1専用翻訳call推奨/T2訳欄なし/T3解説LLMと兼用=却下)。新しい有料生成工程・品質仕様=**未承認の新仕様→ユーザー判断事項**(分類D、`判断候補`)。実装は訳以外(1〜3,5項)を先行でき、訳欄はT1/T2の判断待ちで固定する。
