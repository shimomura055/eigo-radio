# WIRING_DESIGN_06: 課題① X2p(本文での意味を確定する段)のProduction配線設計案(Opus条件Cレビュー用。**実装しない**)

管理ID: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_29 / 2026-10-24 / 設計のみ(Production .py・template・test・er112コード変更0、API 0)
承認状態: **未承認**(VALIDATED候補。採否は人間ユーザー。`ADOPTION_PROPOSAL_01.md`)。11-7の限定例外は**適用しない**: 既存Production Prompt(`build_user_message_corrected`)・schemaの直接編集に近い領域を扱うため、**ユーザー`APPROVED_FOR_PRODUCTION`の後にのみ実装**する(それまでTrialはDEV `er112_kp_gm_trial_05.py`内のみ)。
行番号は作業ツリー現行(2026-10-24)基準。並行の課題②(possessor_roles、canonicalization段、WIRING_DESIGN_05)とは別commit・別test・別責務(②は`er003_key_words_canonicalization.py`/`er105`/templateが中心、本件は`er003_key_words_gloss_alignment.py`が中心)。

## 0. 設計の骨格(要点)
1. **新規生成経路専用の別builder + 別schema + 別developer message を新設**し、既存の `build_user_message_corrected`・`NEW_GENERATION_TEXT`・`PERSON_CONSTRAINT_TEXT`・`DEVELOPER_MESSAGE`・`GLOSS_ALIGNMENT_JSON_SCHEMA` は**一字も変えない**(A/B/C・Z repair・混在batchの出力はbyte-identical)。変更は新builderの追加と、gate内の分岐1箇所。
2. 分岐条件: 当該callの `pending` が**全件** `is_fulltext_gloss_missing`(current gloss=null かつ `fulltext_source_ref`付き)のときだけ新builder。1件でも違えば、そのcall全体を現行builder(`meaning_stage=SKIPPED_NOT_ALL_NEWGEN` を記録)。
3. 追加LLM call 0、retry上限(`MAX_GLOSS_ALIGNMENT_ATTEMPTS=2`)不変、item単位retry・`prior`(前回却下理由)の再提示も維持。
4. 配線順: A-1/②とは独立(同一ファイル`er003_key_words_gloss_alignment.py`だが、②はgloss module非接触)。revert単位=本件の単一commit。

## 1. 変更表(Production側。採用後にのみ実装)
| # | 場所(現行行) | 変更 | 備考・理由 |
|---|---|---|---|
| G-1 | `er003_key_words_gloss_alignment.py` 新定数 `NEWGEN_DEVELOPER_MESSAGE`(新規、:79付近) | DEV Trialで使用した `M_DEVELOPER` 相当「英語学習教材のKey Phraseに付ける日本語グロスを書いてください。」 | 現行 `DEVELOPER_MESSAGE`(:79「…意味に過不足なく一致させてください」)は不変。**注意**: TrialのB0は現行DEVELOPER、X2pは`M_DEVELOPER`で比較しており、developer文の差もX2pの効果に含まれる(§5) |
| G-2 | 同 新関数 `build_user_message_newgen_meaning(targets, article_text, rules, prior)`(新規、:566-627の直後) | Trialの `build_x_message("X2p", ...)` を移植。構成=`X_HEAD`(「このkey_phraseが【記事本文】のこの箇所で実際に表している意味を…」)+(人称項目があれば)`PERSON_CONSTRAINT_TEXT`の**文脈限定句置換版**+`X_NEWGEN`(source_sentenceと前後文脈は語義と用法を決めるために使う)+`X2P_MEANING`(meaning_in_text_en→naive_ja→naive_ja_conveys→gloss)+`X_OUTRULES`+承認済みgloss規則+対象項目+記事本文。**`prior_block`(previous_attempt_rejected)をTrialが省略していたので移植時に追加必須** | 文脈限定句の置換3箇所: (i) :620「key_phrase単体で他の文脈でも再利用できる自然な訳にし、本文固有の固有名詞・文脈の追加はしない」→`X_HEAD`の「本文でのこの箇所の意味…固有名詞・数値・この記事だけの出来事は入れない」、(ii) :337-338 `NEW_GENERATION_TEXT`の「source_sentenceは…どの語義かを選ぶためだけに」→`X_NEWGEN`、(iii) :326-327 `PERSON_CONSTRAINT_TEXT`の「source_sentenceは…人称の指示対象を決めるためには使わない」→「source_sentenceと前後の文脈は語義と用法を決めるために使い、人称の指示対象を決めるためには使わない」。いずれも**新builder内の置換のみ**で、既存定数は不変 |
| G-3 | 同 判定の参考例(:618-619「fall into」) | **新builderには含めない**(新規生成はcurrent=nullで判定ステップ自体が不要。Trialも除外していた)。既存builder内は不変 | 字義寄りの訳を手本とする原因候補(`ROOT_CAUSE_04.md` 0-R)だったが、**既存builder(Z repair・混在batch)には残る** = 原因候補は残置される(§3) |
| G-4 | 同 `NEWGEN_JSON_SCHEMA`(新規) | `GLOSS_ALIGNMENT_JSON_SCHEMA`(:82-114)をdeepcopyし、`current_gloss_consistent`の後・`japanese_gloss`の**前**に `meaning_in_text_en`(string)・`naive_ja`(string)・`naive_ja_conveys`(enum yes/partly/no)を挿入。`required`に全部追加(Trial `x_schema("X2p")` と同一)。Production必須欄(`rank`/`current_gloss_consistent`/`japanese_gloss`/`qa_reflects_all_key_phrase_words`/`reasoning`/`added_word_mappings`)は全て維持。schema name=`key_phrase_gloss_alignment_corrected_newgen` | 欄の**順序が生成順**(gloss前に意味決定)。`strict: true`のため後方互換は不要(新規生成専用) |
| G-5 | 同 `validate_item_corrected`(:629-686)に `newgen: bool=False` 引数 | newgen時のみ: (a) `meaning_in_text_en`/`naive_ja`が非空文字列、`naive_ja_conveys`がenum内、でなければ `reasons`に追加(理由コード `meaning_stage_fields_invalid`)。(b) **record-only**(不合格にしない): `gloss==naive_ja`(アンカリング)・`naive_ja_conveys`の値・gloss文字数/naive_ja比を `out`に記録。既存の検査(括弧/数字/…/音声化禁止記号/人称整合/qa PASS/added_word_mappings)は全て不変 | (b)を合否に使うと新たなHR(人間確認)率を生むため、Trial実績(`gloss==naive_ja` 0/85、validate互換85/85)に基づき**初期はrecord-only**とし、運用データで判断 |
| G-6 | 同 `run_alignment_gate_corrected`(:696-) | `pending`全件が`is_fulltext_gloss_missing`のとき、`msg = build_user_message_newgen_meaning(...)`・`fn = make_factory_for(msg)`(**ファクトリ契約は不変**)を使い、schema/developerはmessage冒頭のマーカー(例 `<!--NEWGEN_MEANING_V1-->`)で`make_alignment_fn`(:399)が選ぶ(選択肢Pとして推奨)。validateは`newgen=True`。それ以外は現行どおり | **選択肢P(推奨)**: `make_alignment_fn(msg, ...)` がmsgマーカーを見てschema/developerを切替。caller側(`_align_factory(msg)`、Z `_person_repair_factory`、mock/hook `gloss_align_factory(msg)`)の契約変更0。欠点=暗黙結合。**選択肢Q**: factory契約を`factory(msg, *, variant=None)`へ拡張(明示的だが全caller・test・hookの改修が必要)。Opusに判断を求める |
| G-7 | 同 `apply_alignment_corrected`(:766-) | `gloss_alignment`記録に `meaning_stage`(`{applied: true, meaning_in_text_en, naive_ja, naive_ja_conveys}`、または`SKIPPED_NOT_ALL_NEWGEN`)を**追記のみ**(監査用)。TTS/表示へは出さない(`japanese_gloss`と`japanese_gloss_tts`のみ従来どおり) | `meaning_in_text_en`を後段(Adv説明等)へ渡す案は**仕様候補**であり本設計に含めない(Fable報告のみ) |
| G-8 | 同 `align_glosses`(:813-)の `gloss_alignment_runtime_metadata.json` | `meaning_stage`(applied/skipped)・schema/developerのsha・`rules_sha256`(既存)を追記 | 後検証・revert確認用 |
| G-9 | 承認済みgloss規則(`b1_p2_keywords_l_prompt_template.txt`の抽出) | **変更0**(rules sha不変)。ただしTrialは `preflight(True)["rules"]` を使用、Production全文選定itemは `rules_fulltext`(数値placeholder回避段落を含む、:826-830)を使う → §6のevidenceで `rules_fulltext` 版を必ず実測 | 差を評価外のまま配線しない |

## 2. 呼出点・経路ごとの適用/非適用(選択と理由)
| 経路 | 呼出元 | current gloss | 適用 | 理由 |
|---|---|---|---|---|
| X/Z/Y 新規生成(全文選定由来) | `scaffold.run_key_phrase_canonicalization` → `align_glosses`(`er003_v1_n3_01_scaffold_generate.py:539`。Zも`er026`が`scaffold`経由で同関数を使う[`er026:44,65`]。実装時に再確認) | null | **適用** | Trial対象。全itemが`fulltext_source_ref`付き |
| retry(attempt 2) | `run_alignment_gate_corrected`内 | null(未採用item) | **適用**(`prior`再提示込み) | pendingは新規生成itemのみ |
| 混在batch(null + current gloss有) | 同上 | 混在 | **非適用**(call全体を現行builder、`SKIPPED_NOT_ALL_NEWGEN`を記録) | X2pは全項目null専用の指示。混在の挙動は**未検証**。全文選定の1記事内のitemは全てnullで始まるため通常は発生しない(発生しうるのはA/B/C凍結経路の再整合等) |
| Z repair(人称整合関所) | `er026_family_z_fiction_production_runner_01.py:1552` `align_glosses(... only_ranks=ranks)` | あり(生成済み) | **非適用(推奨)** | 人称だけの修復で意味再生成は目的外。適用すると生成済みglossの意味が変わる副作用。ただし**現行builderのfew-shot(G-3)・文脈限定句は残る**ため、repairで字義寄りに書き戻すリスクは理論上残る(未観測)。代替案=repair時にも新builderの意味欄だけを足す(未検証、追加Trial要) |
| 既存記事 | - | - | **自動再生成しない** | 新規生成のみ。再生成はユーザー指示時に既存手順で |
| A/B/C旧ライン(凍結) | `scaffold`共有だが`fulltext_source_ref`なし | あり/なし | **非適用** | `is_fulltext_gloss_missing`(:270-273)が偽 → 分岐に入らない。担保=§4 WC-05とGrep(`fulltext_source_ref`の設定側は`er105_kp_fulltext_selector_01.py`/`er003_key_words_canonicalization.py`のみ) |
| resume/HR解決 | `resolve_gloss`(:1045-)・`_load_gloss_hr_resume` | HR済み | **非適用** | 人間確定glossは不変 |

## 3. 副作用・残リスク(Opusに評価を求める事項の素材)
- **N層(通常表現)の説明文化・文脈取り込み過ぎ**: 通常54KPで35/54の文字列が変化。THIN 2件は「文脈を取り込み過ぎて意味が狭い」型。再利用性の低下(`add up`→「つじつまが合わない」等)は設計原則変更の帰結。
- **developer文・規則・文脈限定句の複合変更**: 効果の因子分離は不十分(X1[句置換のみ]は有意差なし、X2→X2pは規則追加)。Productionでの再現性は1 rep(R)+1 rep(Stage 2)のみ。
- **推論token増**: reasoning 304→1,343/call。上限超過・タイムアウト・空応答率の増加の有無は、Trial 85出力では観測されなかったが(validate互換85/85)、Production件数では未確認。
- **model/effort**: Trialは gpt-6-luna effort=high。Productionの`routing.SUPPORT_MODEL`/`process`(`A2_SUPPORT`/`B1_SUPPORT`)が同一であることを実装時に再確認(`make_alignment_fn`の`reasoning_effort="high"`既定は一致)。
- **few-shot「fall into」の残置**(既存builder): Z repair・混在batchには残る。削除はA/B/C・Z repairの出力を変えるため本件では行わない(別Trial)。

## 4. test計画(WC。実装時)
新規 `er003_test_kp_gloss_meaning_stage_01.py`(既存 `er003_test_key_words_gloss_alignment.py`・`er003_test_kp_gloss_alignment_wiring.py`・`er003_test_kp_gloss_alignment_stop_paths.py`・`er003_test_kp_gloss_person_alignment.py` は変更せず回帰として全PASSを確認):
| ID | 内容 |
|---|---|
| WC-01 | **不変性(DefaultOffIsolation相当)**: 全itemが`fulltext_source_ref`なし/current gloss有のとき、生成messageが現行とbyte-identical(`er071_output/m2p0_n01_production_wiring_01/gloss_alignment_production_wiring_01/golden/make_alignment_request_golden_01.py`のgolden照合)、schema=現行`GLOSS_ALIGNMENT_JSON_SCHEMA`、developer=現行 |
| WC-02 | 新規生成(全件null+`fulltext_source_ref`)で新builder・新schema・新developerが選ばれ、欄順=`current_gloss_consistent`→`meaning_in_text_en`→`naive_ja`→`naive_ja_conveys`→`japanese_gloss`、Production必須欄が全部schemaに存在 |
| WC-03 | 文脈限定句が新messageに**含まれない**(「他の文脈でも再利用できる」「語義を選ぶためだけ」の不在をassert)かつ「本文のこの箇所」の句が含まれる。承認済みgloss規則の抽出文(`rules`/`rules_fulltext`)がそのまま含まれる |
| WC-04 | 混在batch(null+current有)で現行builderが使われ`SKIPPED_NOT_ALL_NEWGEN`が記録される |
| WC-05 | A/B/C形のitem(`fulltext_source_ref`なし)で新経路が一切呼ばれない(builder/schema呼出回数0) |
| WC-06 | retry時に`prior`(previous_attempt_rejected)が新messageに再掲される、attempt上限2不変、unresolvedはHR(`FAILED_HUMAN_REVIEW_REQUIRED`)になる。新経路失敗が現行builderへ暗黙フォールバックしない |
| WC-07 | validate: 新欄欠落/enum外→INVALID、`gloss==naive_ja`/conveysはrecord-onlyで合否不変、括弧・算用数字・人称整合・qa・mappingの既存検査が新経路でも同一に働く |
| WC-08 | Z repair(`only_ranks`、current有)は現行builder(新経路0回) |
| WC-09 | 既存フラグ `EIGO_KP_GLOSS_ALIGNMENT` OFFで従来どおり`DISABLED`・API呼出0(kill switchは本件でも唯一) |
| WC-10 | `make_alignment_fn`(選択肢P採用時)のマーカー判定: マーカー無しmessageは現行schema/developerのまま |
| WC-11 | 回帰: 既存gloss alignment関連test群全PASS、全回帰 failed 0/errors 0の維持を実行時に記録 |

## 5. 評価の十分性(現状の限界。Opus論点素材)
- **1 rep**(R・held-out・Stage 2)。Rはhard-core 4KPのみ(n=12出力)。held-outは10KP(ZのF型は母集団2件)。Stage 2のB0は既存Trial_04の2rep(同条件の新規B0ではない)。
- **Fable単独評価**(Sonnet Judgeなし)。control再判定の一致率 7/10(不一致3件はすべて緩い方向)→ PASSの一部は緩め判定の余地。
- **X2p設計はR結果を見た後に調整**(THIN対策)。gating基準もX2p確定値を見た後に是正(開示済み)。過学習(hard-core 4KPへの適合)の可能性は、held-out・Stage 2が独立に悪化0〜2であることで一部のみ担保。
- developer文(`M_DEVELOPER`対`DEVELOPER_MESSAGE`)・`rules`対`rules_fulltext`・`include_numeric_rule`差の影響は未分離。

## 6. runtime evidence計画(実装後。X/Z正式KP段、新規TTS 0)
1. DEV注入text(過去Production記事の本文+`original_items`を注入、`inject_z_a2_cli.py`/`harness_kgcpw_01.py`の形)で、X経路(`scaffold.run_key_phrase_canonicalization`)・Z経路(`er026` stage_kp)の**正式KP段**を実行。`rules_fulltext`で実測。API費用は2経路x記事数(gloss callのみ、見積各0.2〜0.5円)。TTS・assemble・公開0。
2. 確認項目: 新経路選択(`gloss_alignment_runtime_metadata.json`の`meaning_stage`)、validate通過率、HR率、`gloss`のFable確認(R hard-core型KPを含む記事)、A/B/C形入力で新経路0、Z repair経路は現行builder、所要時間(wall-clock)・reasoning_tokens・単価の実測(本資料の見積の再測定)。
3. 失敗時の最終成果物: gate unresolvedは従来どおり `FAILED_HUMAN_REVIEW_REQUIRED`(KP維持、旧gloss維持、HR報告)。新経路固有の失敗(空応答等)も既存のTECHNICAL_FAILED/PARSE_FAILEDとしてattemptを消費し、上限2後HR。

## 7. flag・revert・SSOT
- **flag**: 新規flagは設けない(推奨)。理由: 採用後は既定ON(Production Promptの変更)であり、既存の `EIGO_KP_GLOSS_ALIGNMENT`(:42、既定ON、OFFでgloss再整合全体停止)が唯一のkill switchのまま。flagを増やすと二重経路・A/B不一致のリスク。**Opus判断素材**: 緊急退避用に「新経路のみOFFにして現行builderへ戻す」既定ONのenvを置くか(置くと配線が1経路増える)。いずれにせよ起動script/.env等で暗黙にONにしない。
- **Trial中のProduction到達性**: 現状 `er112_kp_gm_trial_05.py` はDEV専用でProductionからimportされない。Production moduleは未編集(`TRIAL_05/production_hash_start.txt`と`production_hash_end.txt`は一致)。採用までflag/配線は**存在しない**(未承認機能のProduction既定値=「経路なし」)。
- **revert単位**: 本件の単一commit(`er003_key_words_gloss_alignment.py`・新test・SSOT)。`git revert`1手順で現行に戻る(既存builder/schema/定数は不変のため)。
- **CURRENT_SPEC更新箇所**(採用後): `CURRENT_SPEC.md`のKP gloss再整合節(2787〜2793行付近、`er003_key_words_gloss_alignment.py`、OPEN-356/KGCPW)に「新規生成(全文選定由来)のglossは、`meaning_in_text_en`→`naive_ja`→`naive_ja_conveys`の3欄を先に出力して本文での意味を確定してから書く。**設計原則『key_phrase単体で他の文脈でも再利用できる訳』を『本文のこの箇所での意味を表す訳』へ変更**(ユーザー承認事項)」と追記。承認済みgloss規則(`b1_p2_keywords_l_prompt_template.txt`抽出文、CURRENT_SPEC 1973-1977)自体は不変。OPEN-474・DECISION_LOGも更新。
- **ユーザー承認事項の明示**: 上記の設計原則変更はProduction挙動の意味的変更に当たる(CLAUDE.md「人間に判断を求める」: 承認済み仕様・Writer/Prompt原則の変更)。VALIDATEDになっても、この点を含めてユーザーが採否を決める。

## 8. 本設計が決めていない事項(Fable/Opusへ)
Z repair経路への適用可否(推奨=非適用だが未検証の代替あり)、選択肢P/Q、緊急退避flagの要否、record-only項目(`gloss==naive_ja`)の将来のgate化、`meaning_in_text_en`の後段活用(仕様候補)、A/B/C・Z repairに残る few-shot「fall into」(原因候補)の扱い。
