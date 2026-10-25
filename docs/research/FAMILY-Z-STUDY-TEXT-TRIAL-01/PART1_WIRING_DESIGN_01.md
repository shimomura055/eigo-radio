# PART1_WIRING_DESIGN_01(Part 1「Vocabulary & Expressions」案α Production配線設計)

管理ID: FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_13(Phase 0: 設計のみ、API 0・Production file編集0) / 日付: 2026-10-25
Status: **APPROVED_FOR_PRODUCTION(ユーザー2026-10-25、原文=`docs/pm/delegation_log/2026-10-25_FAMILY-Z-STUDY-TEXT-TRIAL-01_USER_05.md`:10-54)・配線設計中・未配線**。PRODUCTION_WIREDではない。本設計はOpus条件Aレビュー(`PART1_WIRING_OPUS_REVIEW_REQUEST_01.md`)後に実装委任へ進む。
前提調査=`PART1_WIRING_SPEC_CHECK_01.md`(現行に置換対象のPart 1生成は無く、新しい独立段の追加。訳の生成元は既存仕様に無い)。

## 0. 設計の要点
| 項目 | 内容 |
|---|---|
| 追加するもの | 新規module `er003_kp_general_explanation_01.py`(X/Z共通)。KPの**英語表現(`explanation_phrase(item)`=`used_form`)だけ**を入力に、1 callで全KP(1〜3件)の日本語一般解説を生成する純関数+resume用resolver+決定論の出力組立 |
| 呼出点 | KP確定後・TTS前の**各Familyの1箇所**: Z=`stage_kp`のb1b `kp_expl_b1b`直後に新stage `kp_part1_b1b`(`ensure_stage`)。X=`run_theme_scaffold`のb1bでKP PASS確認後(+再実行用に`--stage study_text`)。両者とも同じmoduleの同じ関数を呼ぶ(一貫性) |
| 対象level | Advanced(b1b)のみ(Trial-04はAdvanced。Standard[a2]へは拡張しない=新仕様) |
| 既存工程の変更 | KP選定・canonicalization・gloss整合・Redundancy QA・HR・SRC D1・kp_expl(音声用英語解説)は**無変更**。変更するProduction fileは「呼出点の追加」と登録(routing表・Zの再生成名)に限る |
| LLM | `gpt-6-luna`(`routing.SUPPORT_MODEL`)、Trial-04と同一Prompt(バイト一致をtest固定)・同一API形式(user messageのみ・effort指定なし・Markdown出力) |
| 失敗時 | 技術retry1回(parse/構造)→なお失敗なら**fail-closed STOP**(旧方式へのfallback無し=旧方式が存在しない。空欄で続行もしない)。TTS前に止まるため無駄な音声費用を出さない |
| 新規の未承認仕様 | **「本文引用英文の日本語訳」の生成元のみ**(§11)。ユーザー判断事項として分離。それ以外は承認済み仕様(案α)の配線で新仕様を含まない |

## 1. 全体フロー(X/Z)
```
[既存] KP選定→canonicalization→gloss整合→Redundancy QA→(Z: HR関所→人称関所→SRC D1→install) ──→ keywords_canonicalized.json(確定)
                                                                                                │
[既存] kp_expl_b1b(音声用英語解説, Zのみstage_kp内/XはTTS段)                                    │
[新規] Part 1 解説生成  ← 入力: [explanation_phrase(it) for it in items] だけ ─────────────────┘
        └─ key_phrases/b1b/kp_general_explanations.json(LLM結果+audit+phrases_signature) ※キャッシュ兼証跡
[新規・決定論] 組立(描画時): 現在のkeywords_canonicalized.json(used_form/japanese_gloss/source_sentence)
        + kp_general_explanations.json(解説) + [訳(§11 T1採用時のみ)]  →  study_text/part1_vocabulary_expressions.{json,md}
        └─ Z: build_pagesのAdvanced節に表示block / X: player.html Advanced節に表示block
[既存] TTS → Gate → Assembly → pages
```
- 解説生成は本文(`text`)に一切依存しない(入力が表現のみ)。したがって本文のRegen/Local Rewriteで**KPの表現が変わらなければ再生成しない**。引用英文・本文中の意味は描画時に現在値を読むので、本文変更・gloss更新(HR解決)に自動追従する。

## 2. 実装箇所と関数(a)
新規 `er003_kp_general_explanation_01.py`(`er003_*`のKP系列に置き、X/Z/将来Yが同一moduleを呼ぶ。Z専用/X専用の分岐を作らない):
| 関数/定数 | 役割 |
|---|---|
| `MODEL_ROUTING_PROCESS="KEY_PHRASE_GENERAL_EXPLANATION"`、`MODEL=routing.SUPPORT_MODEL` | `er006_model_routing_contract_01.py:126`付近の`PROCESS_MODEL_MAP`へ1行登録(`KEY_PHRASE_ADVANCED_EXPLANATION`[音声用英語解説]とは別processにして原価・routing監査を分離) |
| `PROMPT_HEAD`/`PROMPT_BODY`/`PROMPT_TEMPLATE_SHA256` | `run_trial_04.py`の`P1_HEAD`/`P1_BODY`(:74周辺)を**逐語コピー**(docs/researchをimportしない)。sha固定+`_prompt_04_{gift,ig_nobel,open_window}_p1a.txt`とのバイト一致test |
| `build_prompt(phrases: list[str]) -> str` | 引数は表現リストのみ。`"\n# 解説する英語表現\n"`+`"{i}. 英語表現: {phrase}"`の列挙+BODY |
| `validate_phrases(phrases)` | 各表現: 英字・空白・`'`/`’`/`-`/`.`のみ、1〜8語、最大60字、CJK/改行/制御文字を含まない。違反は`ValueError`(**課金前に拒否**) |
| `generate_general_explanations(phrases, *, call_fn=None, client=None, process=None) -> dict` | 検証→`routing.require_model`→1 call→parse(`### N. <表現>`見出しがN個・番号連続・**見出し表現が入力と正規化一致**・各本文が日本語を含み一定長以上)→失敗なら**技術retry1回**→なお失敗で`KpGeneralExplanationError`。応答model≠期待modelは`KpGeneralExplanationError`(fallbackしない)。戻り値`{"items":[{"rank_index","phrase","explanation_ja"}...],"audit":{...}}` |
| `generate_for_kp_items(items, *, call_fn=None, client=None)` | 呼出側用の薄いwrapper。`[explanation_phrase(it) for it in items]`だけを抽出して上記へ(gloss/source_sentence/meaning_in_text_en/display_phraseの参照は**この関数内に書かない**) |
| `phrases_signature(items) -> str` | `sha256(json.dumps([explanation_phrase(it)...]))`。**表現文字列と順序のみ**(gloss・引用文・本文shaを含めない=設計上の意図) |
| `resolve_general_explanations(items, cached, *, call_fn=None, client=None)` | X用のresume resolver: cachedのsignature一致なら`reused_from_previous_run=True`で再利用、不一致なら再生成(`_resolve_kp_explanations_text`[X runner:1069]と同型) |
| `assemble_part1(kp_items, explanations, translations, article_text) -> list[dict]` | 決定論。§4。LLMなし |
| `render_markdown(rows)` / `render_html_block(rows)` | `.md`とページ用HTML片(`class='study'`。`kp`classは使わない) |

呼出点(Production fileへの変更はここだけ。実装委任で行う):
- **Z** `er026_family_z_fiction_production_runner_01.py` `stage_kp`のb1b `kp_expl_b1b`(:1776)直後に`ensure_stage(prov, "kp_part1_b1b", sig, f"{ctx.out_dir}/key_phrases/b1b/kp_general_explanations.json", runner, regenerate=ctx.regenerate_stage=="kp_part1_b1b")`を追加。`_guard(ctx,"kp_part1_b1b",0.5)`、`E2E_KP_EXTRA_REGEN_NAMES`(:1134)へ`"kp_part1_b1b"`追加。失敗は`FamilyZE2EStop("FAMILY_Z_KP_GENERAL_EXPLANATION_NOT_OK: ...")`。`stage_pages`(:1897)の`build_pages`前に組立+`study_text/`出力。
- **X** `er019_family_x_audio_production_runner_01.py` `run_theme_scaffold`(:387)のb1bでKP PASS確認後(`_fail is None`、:451以降)に`resolve_general_explanations`→`<level>/key_phrases/kp_general_explanations.json`保存。失敗は既存の`kp_stage_status`機構(:477, `main()`:2706-2717で`rc=3`)に`KP_PART1_FAILED(<理由>)`を載せる。再実行用に`--stage study_text`(KP再選定せず既存`keywords_canonicalized.json`から同関数を呼ぶ。API=Part 1の1 callのみ)。`build_player_html`(:2280)のAdvanced節に組立blockを追加。
- 共通: `er006_model_routing_contract_01.py`の`PROCESS_MODEL_MAP`へ1行。`er063_family_z_audio_01.py` `build_pages`(:1985)/`_user_page_rows`(:1918)+`er_user_listening_page_common_01.py` `render_standard_page`(:50)へ**任意引数**`study_html`(未指定=従来とバイト同一)。

## 3. 入力隔離の保証(b)
多層で保証する(1層でも破れたら下の層で止まる):
1. **型**: 公開APIは`phrases: list[str]`のみ。本文・gloss・引用文・作品名は引数として受け取れない(`inspect.signature` testで固定: `build_prompt`の引数=`["phrases"]`)。
2. **値**: `validate_phrases`(英語表現の形のみ許可、CJK・改行・長文を課金前に拒否)。`used_form`は基本形化済みで固有名詞・人称は一般化済み(例 `sharpen someone's senses`)。
3. **抽出点の単一化**: `generate_for_kp_items`だけがitem dictに触れ、取り出すのは`explanation_phrase(it)`のみ。`japanese_gloss`/`source_sentence`/`meaning_in_text_en`/`display_phrase`/`naive_ja`の文字列は同関数に存在しない(静的grep test)。
4. **実行時リーク検査(fail-closed)**: 送信直前に、渡されたKP items全件の`source_sentence`・`japanese_gloss`・`meaning_in_text_en`・`naive_ja`が組立済みPromptに**部分文字列として含まれない**ことを確認(含めば`KpIsolationViolation`でSTOP、API呼出前)。表現そのものが引用文の一部であることは正常なので、検査対象は「引用文全体」「gloss全体」(長さ≥ 表現長+4)。
5. **audit**: `input_sha256`(表現リスト)と`prompt_sha256`を成果物と同階層に保存(後から「何を渡したか」を再現可能)。Promptがモジュール定数+表現列挙だけで決まるため、`prompt_sha256==sha256(build_prompt(phrases))`がtestで検証できる。
6. **test**: Draft `part1_wiring_tests_draft_01.py` B1/B2/B3/B4(Section Aは実行済み: Trial Promptに gloss・引用文・訳が含まれないこと 3 passed)。
- 残るリスク(明示): 表現自体が文脈語を含む場合(例 `bound to the protein`)は入力に残る。これはKP選定の仕様(Trial-04でも同じ入力)で、本配線では変更しない。

## 4. 出力の組合せ(c)
ユーザー原文§2「確定済みKey Phrase、本文中の意味、本文引用英文、日本語訳、解説」→Trial-04の並びを踏襲:
| 項 | 内容 | 出所(Production) |
|---|---|---|
| 1 英語表現 | `used_form`(確定KP) | `keywords_canonicalized.json` |
| 2 日本語の意味(本文中での意味) | `japanese_gloss` | 同(HR未解決/未評価glossは出さずSTOP: `collect_unresolved`/`collect_unevaluated`) |
| 3 本文中の英文 | `source_sentence` | 同。**組立時に`article_text`(正規化)との逐語照合を決定論assert**(不一致はSTOP。LLMなし) |
| 4 英文の日本語訳 | §11の結論待ち | (T1採用時のみ) |
| 5 解説 | `explanation_ja` | `kp_general_explanations.json` |
- ラベル: 「解説」(旧「実用性を重視した解説」は使わない)。節見出しは`Vocabulary & Expressions`(ページ上は`Part 1`の番号を出さない。Part 2〜4は未採用のため、存在しない番号を参照しない=Dangling防止。`.md`ファイル名は`part1_vocabulary_expressions`)。
- 保存: `<run>/study_text/part1_vocabulary_expressions.json`(行dict、キー順=`english_expression, meaning_in_text_ja, source_sentence, source_sentence_ja, explanation_ja`)と`.md`。Z `stage_pages`・X `player`段で毎回再組立(gloss更新・本文更新に追従)。
- 表示(§9): Z=index.htmlのAdvanced節、X=runner内部player.html。

## 5. 再生成制御(d)
キー: **`phrases_signature`=`explanation_phrase`の並びのsha(表現文字列と順序のみ)**。本文sha・gloss・引用文はキーに含めない(解説は本文非依存。含めるとHR解決のたびに無駄な再生成が起きる)。
| 事象 | Z(`ensure_stage` `kp_part1_b1b`) | X(`resolve_general_explanations`) |
|---|---|---|
| 初回 | 生成→entry+出力+sha保存 | 生成→`kp_general_explanations.json` |
| resume(同一KP表現) | `ensure_stage`が出力sha・input_sha一致でreuse(API 0) | signature一致でreuse(API 0)、`reused_from_previous_run=True` |
| gloss更新(HR解決/再整合) | 表現不変→reuse(再描画で新glossを反映) | 同 |
| 本文のRegen/Local Rewrite後にKP**表現が同一** | reuse | reuse |
| KP**表現が変化**(KP再選定/`--regenerate-stage kp_b1b`/外側retryで別KP) | `input_sha`不一致→**`FamilyZProvenanceMismatchStop`でSTOP→`--regenerate-stage kp_part1_b1b`を明示**(`kp_expl_b1b`と同じ既存の安全側規則。自動再生成しない) | signature不一致→**自動で再生成**(Xの`_resolve_kp_explanations_text`と同じ既存挙動) |
| KP順序のみ変化 | 同上(順序もsigに含む=番号と解説の対応を守る) | 同上 |
| `--regenerate-stage kp_part1_b1b`(Z) | 明示再生成・置換・来歴更新 | `--stage study_text`再実行(signature不一致or`--force`相当は不要:resolverが判断) |
| 旧KP(Part 1導入前の既存run)をresume | `kp_part1_b1b`のentry無し+出力無し→生成(API 1 call) | cache無し→生成 |
- X/Zの挙動差(Z=明示再生成STOP / X=自動再生成)は**既存の`kp_expl`系の挙動をそのまま踏襲**したもの(新たな非対称は作らない)。Opusレビュー論点(c)。
- KP選定の外側retry(最大3回+Redundancy NG再選定)は**Part 1の前**で完結する。Part 1はretryループの内側に入れない(失敗でKP選定をやり直さない)。KP stageがSTOPしたらPart 1は実行されない。
- 訳(T1採用時)のキャッシュキー=`sha256(source_sentence+前後文)`(本文が変わって引用文脈が変われば再生成)。

## 6. retry/fallback(e)(既存仕様に従う。新挙動なし)
- 技術retry: **parse/構造検査の失敗に限り1回**(`generate_kp_explanations`の`retried_for_parse`[`er019_family_x_kp_explanation_01.py:258`以降]と同方針)。QA起因の再生成ループは作らない(QA/Validatorを新設しない=DESIGN_04 §7)。
- API例外(ネットワーク/rate limit): openai clientの既定retryに任せ、追加ラッパは作らない(Charter 3の独自retry禁止)。例外はstage失敗として伝播。
- なお失敗: **fail-closed STOP**(Z `FamilyZE2EStop`、X `kp_stage_status=KP_PART1_FAILED(...)`→rc=3)。自動採用・空欄続行・旧方式fallbackはしない(旧方式が無く、「安全≠成功」原則とも整合)。
- 「Part 1失敗でも音声エピソードは継続し、学習テキストだけ欠落」させる非blocking案は**新しい挙動**になるため採らない。必要ならユーザー判断事項(現時点では判断候補なし。厳格側=既存`kp_expl`のSTOPと同じで、TTS前に止まるため費用損失も最小)。
- 予算: Zは`_guard`(推定0.5円)、Xは`budget_check`。再起動は委任文が許可した回数のみ。

## 7. runtime evidence(f)
audit(`kp_general_explanations.json`内`audit`)に必須記録: `process`、`model`(**応答の実model_id**)、`prompt_sha256`、`input_sha256`+`phrases`、`response_ids`、`calls[]`(usage・cost_jpy・elapsed)、`retried_for_parse`、`reused_from_previous_run`、`generated_at`。Zは`provenance.json`のentry(`input_sha256/output_sha256`)も。
証跡文書(実装委任で作成): `PART1_WIRING_EVIDENCE_01.md`=X/Zそれぞれの(1)model_id=`gpt-6-luna`(2)`prompt_sha256`==固定値(3)入力=KP表現のみ(リーク検査PASSの記録)(4)routing(5)解説After全文+同一表現のTrial-04出力との比較(Before=Trial-04出力/本文引きずり無し・核の意味先頭を目視確認)(6)費用実測(7)reuse/再生成の発火(同一KPでAPI 0、表現変更でAPI 1)。

## 8. Validator/Regression/Integration test計画(g)
実装後に`er003_kp_general_explanation_01_test_01.py`へ移す(雛形=`part1_wiring_tests_draft_01.py`、Section A実行済み3 passed、B/C 16件はmodule待ちskip、D 3件は統合):
- 入力隔離(B1-B4)、Prompt逐語一致(B2、3作品)、signature(B5)、resume/再生成(B6)、retry上限1回(B7)、見出し不一致(B8)、model不一致STOP(B9)、audit(B10)、routing(B11)、組立5項順・逐語assert・HR/未評価glossのSTOP(C1-C3)。
- 統合(D): Z mock modeで`kp→kp_part1_b1b`が`tts_b1b`より前に走り、失敗時にTTS未着手でSTOP/resumeでreuse/表現変更でProvenanceMismatch STOP/`--regenerate-stage kp_part1_b1b`で復旧。X mockで`run_theme_scaffold`b1bのみ呼出・a2は呼ばれない・失敗でrc=3・`--stage study_text`。A/B/C(strategy_l)経路でPart 1 moduleが呼ばれない(API 0・出力不変)。`build_pages`は`study_html`未指定でバイト同一(既存page testのスナップショット)+指定時`check_page` PASS+`_INTERNAL_RE`非該当。
- 既存Regression: `run_project_regression.py`全体(直近collected=7061 passed=7045 failed=6[他agent起因]を基準に、自分起因failed=0を確認)。routingの列挙testへの影響(`er009_n1_routing_governance_10_pricing_table_open251_test.py:12`等が明示リスト参照)を実装時に確認。
- **E2E 1記事ずつの発火証拠計画と費用**(Z/Xの完成済みrun artifactを再利用。新規記事生成・TTS・Gateなし):
  - Z: 完成済みrun(例 `er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_sf_prod_02`)を新run名へコピーし、公式CLIで`--mode real --stage kp`(KP stageはensure_stageでreuse=API 0、`kp_part1_b1b`が発火=Luna 1 call)。mock modeでpages+page_verify(published dirに触れない)。費用≈**0.08円**(+T1採用時0.03円)。
  - X: 完成済みrunの`keywords_canonicalized.json`を持つout_dirで公式CLI`--stage study_text`(KP再選定なし)=Luna 1 call≈**0.08円**。
  - 追加: reuse/再生成の発火確認は同一run再実行(API 0)と表現1件差し替えコピー(1 call 0.08円)。
  - 合計見積 **約0.3〜0.4円**(300円閾値・日次1,000円に対し無視できる。承認済みScope内の自律実行範囲)。実publishedページの更新(既公開ページへのblock追加)は公開作業のためFable判断(§9)。

## 9. 表示・組込み(Z/X)
- Z: `uc.render_standard_page`のlevel dictに任意キー`study_html`を追加し、Advanced節のscript表の後ろに`<section class='study'>`を描画。`study_html`未指定の既存呼出はバイト同一。`check_page`のC3(`table.kp`)・C4(`_INTERNAL_RE`)に触れないclass/文言にする。`stage_pages`で`study_text/`も出力。Standard節には出さない。
- X: runnerの`player.html`のAdvanced節に同blockを追加。**Xのユーザー向け公開ページは共通builderがなくper-article page script**(CURRENT_SPEC 2927)のため、そこへの組込みは本配線の範囲外=別OPEN候補(非blocking・修正へ進む[次委任]、§12)。
- ページ標準フォーマット(Gate 7補足(a)〜(n))の変更ではなく**任意blockの追加**として扱う。標準適合checkの拡張要否はOpus論点(f)。

## 10. 追加原価/セットと処理時間(j)
| 項目 | 実測/見積 | 出典 |
|---|---|---|
| Part 1 LLM 1 call(3KP) | **0.0775円/set**(6 call平均。例 gift r1: input 686・output 886[reasoning 211]token・0.000512USD=0.0819円、¥160/$) | `usage_04a_r{1,2}_p1_*.json` |
| 量産単価への影響 | 70円比 **約0.11%** | 計算 |
| T1採用時の訳call(見積) | +約0.03円(input≈300・output≈300token想定、未実測) | 推定。Trial-04 P1の1/3程度 |
| 合計(T1込み) | 約0.11円/set(約0.16%) | |
| 処理時間 | +11〜13.5秒(Z/X直列。Trial実測)。`kp_expl_b1b`と並列化すれば≈0秒だが複雑化するため当面直列(音声TTS数分に対し小) | `usage_04a_*`の`elapsed_sec` |
- 追加原価はX/Zの記事セットごとに計測する(audit `calls[].cost_jpy`+cost logger `logging_context(article_id,"kp_part1")`でstageタグ付与)。
- モデル: `gpt-6-luna`はTrial-04と同一・現行`SUPPORT_MODEL`(最新世代推奨系、`PM_GOVERNANCE` 25節の最新モデル原則と整合。本番ラインのモデル選定を変えない)。Sol系への引上げは品質基準変更のため行わない。

## 11. 「本文引用英文の日本語訳」の結論(k)
- **既存の承認済み方式で解決不可**(`PART1_WIRING_SPEC_CHECK_01.md` §5)。X/Zとも文単位の英→日訳の生成元・フィールドが無い。ZはWriter英語のみ、Xは日本語原稿があるが文対応工程なし。
- 選択肢(QCD付き):
  | 案 | 内容 | Q | C | D | 備考 |
  |---|---|---|---|---|---|
  | **T1(推奨)** | 専用の小さな翻訳call(Luna、b1b KP引用英文のみを逐語訳。入力=引用英文+前後1文[指示語解決用、本文から決定論取得]。**解説LLMとは別call・別入力**。出力JSON。失敗は同様にfail-closed) | Trial-03/04の項目4(Luna生成、ユーザー確認済みの出力形)と同種。新規品質仕様=逐語に忠実な自然訳 | +約0.03円/set | 並列実行で+0秒 | 新しい有料生成工程=**ユーザー判断必須**(原文§2:52-54) |
  | T2 | 訳欄を出さない(項4省略) | ユーザー指定の出力構成を満たさない | 0 | 0 | 原文§2の出力構成からの変更=ユーザー判断必須 |
  | T3 | 解説LLMに引用文も渡して訳させる | 入力隔離を破る(案αの根幹に反する) | 0 | 0 | **却下** |
  | T4 | Xのみ日本語原稿から文対応を取る | Zは不可・X専用の新アライメント工程が必要 | 中 | 中 | **却下**(X/Z一貫性なし) |
- 推奨T1。ただし**未承認の新工程のため実装しない**。ユーザー判断が出るまでの進め方: 実装委任は項1/2/3/5(解説生成・stage・組立・表示)を先行し、項4は`translations`引数(None許容)で枠だけ用意、**未決のままPRODUCTION_WIREDとは呼ばない**(受入条件の出力構成が満たされないため)。判断候補の分類=D(新しい有料生成工程・新品質仕様)。

## 12. Dangling Reference対策(h)・SSOT更新案(i)
| 対象 | 扱い |
|---|---|
| 旧Part 1生成コード/Prompt/test | **存在しない**(Grep 0)。撤去対象なし |
| Trial資産(`run_trial_04.py`/`PROMPT_04.md`/`_prompt_04_*`/`INPUT_04.json`/OUTPUT_04) | DEV資産として残置。Productionはimportしない(test: `er003_kp_general_explanation_01.py`内に`run_trial_`/`docs/research`の文字列が無い) |
| `DESIGN_04.md §1`・`ADOPTION_NOTE_04.md §1,§4`の「Productionに存在しない/配線未承認」 | 配線完了時に末尾へ「PART1_WIRING_*で配線済み」の1行追記(原文は消さない=履歴) |
| `kp_expl_b1b`(音声用英語解説)/`kp_explanations.json` | 無変更・並存(役割違い) |
| `E2E_KP_EXTRA_REGEN_NAMES`(Z:1134)・routing表・Zの`--regenerate-stage`choices | 追加(`kp_part1_b1b`、`KEY_PHRASE_GENERAL_EXPLANATION`) |
| `A/B/C`(strategy_l) | 無変更・非適用(27-7)。test固定 |
| 将来Y | Yの正式入口新設時にOPEN-484と同様の受入条件として追記(Y Trial scaffoldはKP共通moduleを呼ぶのみ。本配線はYに自動適用されない) |
SSOT更新案:
- `CURRENT_SPEC.md`: 実装委任でFamily X/Z共通「学習テキスト Part 1」節を新設(仕様=案α、入力隔離、再生成キー、fail-closed、費用)。**本委任では本文変更しない**。
- `DECISION_LOG.md`: 本委任で最小追記済み(Part 1 APPROVED_FOR_PRODUCTION・配線設計Phase 0)。
- `OPEN_ITEMS.md`: OPEN-497へStatus追記+**新規OPEN-512**(下)。
  - **OPEN-512 「FAMILY-XZ-STUDY-TEXT-PART1-PRODUCTION-WIRING-PENDING-01」[承認済み・未配線、PRODUCTION_WIREDと呼ばない]**: 分類=**修正へ進む**(次委任=Opus条件Aレビュー後の実装)。解消条件=ユーザー原文§2の受入条件1〜9。
  - 付随(11-8分類): (i) 引用英文の日本語訳の生成元=**ユーザー判断要**(T1/T2、分類D)。(ii) Xのper-article公開ページへのPart 1組込み=**修正へ進む**(次々委任、非blocking)。(iii) 既公開Zページ(例: 告げ口心臓)へのblock追加と再公開=**Fable判断**(公開作業、UDR #193の再公開と同時実施が合理的)。(iv) Standard(a2)へのPart 1拡張=新仕様のため**実装しない・実害なし**(必要ならユーザー判断)。(v) gloss核意味の質(例 `at a moment's notice`の即応寄り)=ADOPTION_NOTE_04 §3の既存判断候補(分類C、現タスクと独立・追加Trial不要とユーザー明示)。


---
# 追補(委任_14、2026-10-25): Opus条件Aレビュー反映(M1〜M4・実装時必須1〜10)・M3(ii)描画停止・X公開ページ・CURRENT_SPEC記載案
Opus結果の逐語=`PART1_WIRING_OPUS_REVIEW_01.md`(判定=条件付きで実装へ進んでよい)。以下§13〜§17が§1〜§12への修正・追記で、**矛盾する場合は本追補が優先**。

## 13. 実装前必須M1〜M4の反映(設計修正)
| ID | §1〜§12の旧記述 | 修正後(実装する内容) |
|---|---|---|
| M1 | §2 X失敗を`kp_stage_status=KP_PART1_FAILED`でrc=3(KP失敗markerと同系) | **KP失敗と分離**。専用marker `<out>/<level>/key_phrases/kp_part1_failed.json`(`KP_PART1_FAILED_MARKER`)。Part1失敗時は`kp_stage_status`を使わず、scaffold結果に`part1_stage_status`を載せ`main()`がrc=3・メッセージに**`--stage study_text`**を案内(scaffold再実行=support/KP再生成を明示的に非推奨)。`--stage study_text`成功でmarker削除。`study_text`実行前に「KP PASS・`kp_stage_failed.json`なし・gloss HR/未評価なし」を確認(STOP)。`--scaffold-only kp`も同じ呼出点を通る |
| M2 | §2 生成点は各Familyの1箇所のみ | **使う側のfail-closed確認**を追加。Z=`load_level_inputs`(b1b)(TTS/Gate/Assembly共有)と`stage_pages`。X=`tts`/`assemble`/`player`の入口(既存`_kp_stage_failed_markers`確認の隣)。確認=(a)`kp_general_explanations.json`が存在 (b)保存済み`phrases_signature`==現在KPの`phrases_signature`。不一致/欠落はSTOP+次コマンド(Z=`--regenerate-stage kp_part1_b1b`または`--stage kp`、X=`--stage study_text`)。共通関数`require_fresh_general_explanations(items, doc, *, next_command)` |
| M3 | §11 訳はNone許容で項目1/2/3/5を先行配線 | **(ii)採用**: 訳欄(`source_sentence_ja`)は`null`+`translation_status: "PENDING_USER_DECISION"`で**生成・保存まで**行い、**ページ(index.html / X player.html)への描画は止める**。描画有効化条件=run-time条件「訳欄の判断記録`docs/pm/decisions/part1_translation_decision.json`が存在し`decision`が`T1`または`T2`」。環境変数・flag・関数引数・設定dictではONにできない(読取関数`translation_decision_record()`が唯一の入口、記録pathはmodule定数)。T2=訳欄なしで描画、T1=全行`source_sentence_ja`が非nullでなければSTOP(T1訳call未実装の間は描画不可=fail-closed)。判断記録が無い間はページ出力がバイト同一(DefaultOffIsolation test) |
| M4 | §2 入力=`explanation_phrase(it)` | `explanation_phrase`は使わない。**Part 1専用の厳格版`strict_phrase(item)`**: `fulltext_source_ref`が真かつ`used_form`が空でない文字列でなければ`KpGeneralExplanationInputError`(課金前STOP)。`display_phrase`へのfallback禁止。`phrases_signature`・`generate_for_kp_items`・`assemble_part1`すべて同関数経由 |

## 14. 実装時必須1〜10の反映(対応表)
| # | 実装内容 |
|---|---|
| 1 | 見出し照合は`normalize_heading`(NFKC・`*`/括弧/引用符除去・`’`→`'`・小文字・空白圧縮)を両辺へ適用。**表示見出し=入力`used_form`**(LLM見出しは使わない)。本文判定=「CJKを含み30字以上」(Trial-04実出力6件で較正: 最短の本文でも約60字、全6件とも充足。較正結果はEVIDENCE_01) |
| 2 | リーク検査は可変部(列挙部)のみ: `build_prompt(phrases) == HEAD+"\n# 解説する英語表現\n"+列挙+"\n"+BODY`の決定論再構成をassert、列挙部にCJKなし、item内の全文字列値(入れ子も汎用収集、`used_form`等の表現そのものと同一/部分文字列になるものは除外)が列挙部に含まれない(含めば`KpIsolationViolation`、API前) |
| 3 | `validate_phrases`: 拒否=空/CJK/改行・制御文字/60字超/10語超/Prompt区切りに使う`#`始まり。許可=英字(アクセント付き含む)・数字・空白・`' ’ - . , / ( ) & :`等。**実データ較正**: 全`keywords_canonicalized.json`(fulltext_source_ref付き1792件)の`used_form`が全件通ること(testで固定、最大35字・5語) |
| 4 | study blockは`<section class='study'>`+`<h3>`+`<div>`/`<dl>`のみ(`<table>`・`<h2>`不使用)。LLM出力はHTMLエスケープ後に`**`→`<b>`、`*`→`<i>`、段落`<p>`。ラベル=「本文中の意味」「本文の英文」「日本語訳」(T1/T2判断後・コロン無し)「解説」(禁止regex非該当)。生成時にも`\(A2\)\|\(B1\)\|B1B\|English:\|英語:\|EN:\|日本語:\|JA:`を解説文へ適用し構造失敗(=retry対象)にする |
| 5 | `er006` `PROCESS_MODEL_MAP`へ`KEY_PHRASE_GENERAL_EXPLANATION`1行、`er054_..._test_01.py`の`LATER_APPROVED_PRODUCTION_KEYS`へ追加、`er009_..._open251_test.py`の`TABLE_PATH_PROCESSES`確認、`er053_cost_aggregate_01_test_01.py`はcommit前の作業ツリーでFAILするため実行順序に注意(commit後に確認) |
| 6 | Zのmock/dry-runでhook(`part1_call_fn`)が無ければ実APIを呼ばず`FamilyZE2EStop`(`_person_repair_factory`と同型)。実callは既存SDK入口のcost logger(`cl.install`)経由で`cost_log.jsonl`/`raw_usage_log.jsonl`に載り、Zは`_guard(ctx,"kp_part1_b1b",0.5)`、Xは`budget_check`。Xの`--stage study_text`は`cl.logging_context(slug,"kp_part1")`で包む |
| 7 | signature=`sha256(json.dumps({"phrases":[strict_phrase…rank昇順],"prompt_sha256":PROMPT_TEMPLATE_SHA256,"model":MODEL}))`(X/Z共通)。Zの`ensure_stage`のinput_shaにもこのsignatureを使う。ensure_stageのentry fieldsへ`model/prompt_sha256/cost_jpy/retried_for_parse/response_ids`を載せる |
| 8 | 逐語照合は`er003_key_words_min_unit._normalize_for_match`(NFKC・引用符統一・空白圧縮・小文字=KP選定/SRC D1/KP source gateが使う既存基準)で`source_sentence ⊂ article_text`を確認(新ロジックを作らない)。Z=`canonical_article_text`後の本文、X=`article.md`本文 |
| 9 | STOPメッセージに次コマンドを明記: Z `kp_expl_b1b`不一致→`--regenerate-stage kp_expl_b1b`の後に`--stage kp`、`kp_part1_b1b`不一致→`--regenerate-stage kp_part1_b1b`(`FamilyZProvenanceMismatchStop`を包んでhintを付ける)。X→`--stage study_text`(scaffold再実行は非推奨と明記) |
| 10 | E2E前事前確認: 複製runの`kp_expl_b1b`がreuse(ProvenanceMismatchなし)・人称関所CLEAN(修復call・artifact書換なし)であることを`--dry-run`/読取で確認してから`--stage kp`を実行(EVIDENCE_01に記録) |

## 15. 影響範囲(Opus推奨の反映)
- `DEPENDENTS`へ`kp_b1b→kp_part1_b1b`は**追加しない**(Opus推奨どおり)。Z=明示再生成/X=自動再生成の差は`kp_expl`系と同型。
- gloss更新・HR解決では再生成しない(解説入力は表現のみ、glossは描画時に現在値)。
- Advanced(b1b)のみ。ユーザー報告で「Advancedのみ表示」と明記する。
- Standard(a2)・A/B/C(strategy_l)・Y: 無変更・非適用。

## 16. Xユーザー向け公開ページの扱い(委任_14 Fable判断(4))
- Xのユーザー向け公開ページは共通builderが無くper-article scriptで作られる(`er_user_listening_page_common_01`を使うのはZ/Yのみ。root直下にX用の共通page builderは存在しない)。本配線は**runner内部の`player.html`のAdvanced節**に同じ`render_html_block`を差し込む(描画条件はZと同じ=判断記録あり)ところまで実施。
- per-article scriptへの組込みは、同一module経路の最小追加では実現できない(builder新設またはX公開pageをcommonへ移行する別タスクになる)ため、**X=`WIRED_EXCEPT_USER_PAGE`**として報告し、PRODUCTION_WIREDとは呼ばない。見積は結果報告(RESULT_PACKET_FZST14)に記載。

## 17. CURRENT_SPEC記載案(Opus要旨をそのまま採用)
節名「Family X/Z 学習テキスト Vocabulary & Expressions(Advancedのみ)」。案α採用・入力=確定KPの`used_form`のみ・生成はKP確定後TTS前に1 call(`KEY_PHRASE_GENERAL_EXPLANATION`=gpt-6-luna、Trial-04 Promptとバイト一致)・再生成キー=表現・順序・Prompt sha・model・使う側で存在と最新性確認・技術retry1回→fail-closed・表示=KP/本文中の意味/本文引用英文(逐語照合)/訳(T1/T2判断に従う=**判断待ち・描画停止中**)/解説・費用約0.08円/set・時間+約11〜14秒。
