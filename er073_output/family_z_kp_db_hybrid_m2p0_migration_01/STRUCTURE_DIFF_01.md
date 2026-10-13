# STRUCTURE_DIFF_01 (FAMILY-Z-KP-DB-HYBRID-M2P0-MIGRATION-TRIAL-01 委任_01 Phase 1, JPY0)

Trial。Production無変更。証跡: phase1/ (shortlist_*.json, selector_message_*.txt, phase1_summary.json)。出典はすべて読み取り確認済み(行番号は2026-10-13時点)。

## 1. 構造差表

| 項目 | Family Z現行(Strategy L) | Family X(DB Hybrid + M2 + P0) |
|---|---|---|
| 入口 | `er026 stage_kp` -> `w62.run_kp_stage(kp_fn=w62.run_kp_with_outer_retry)` (er062 L931/L971) | `scaffold.run_key_phrases(kp_backend="db_hybrid")` -> `run_key_phrase_selection` -> `_run_key_phrase_selection_db_hybrid_with_fallback` (er003 scaffold L293/L509/L700) |
| 選定への入力 | 本文**全文**(タイトル行除去済み`canonical_article_text`)をP0テンプレートに埋込 | 本文は送らない。Python側でn-gram+Idiom DB+Wiktionary照会+M2供給->shortlist(約24-25件)を作り、候補ID付き一覧+SENTENCE REFERENCEのみ送る |
| Prompt | `b1_p2_keywords_l_prompt_template.txt`(B1文言のまま、Z/Level共通) + Z限定の外側retry汎用note(所有格回避) | 同じテンプレートの静的部(`extract_static_instructions`、本文差込以降を除去) + Family X guidance(`_FAMILY_X_SOURCE_REFERENCE_SELECTION_GUIDANCE`) + 候補行 |
| 選定の自由度 | LLMが自由記述でdisplay_phrase/source_span/source_sentenceを生成 | LLMは候補ID(enum)のみ。source_span/sentenceはPython側で決定論復元 |
| モデル/設定 | `routing.require_model(process=A2_SUPPORT/B1_SUPPORT)` = `gpt-6-luna` | 同じ(`routing.require_model(process,...)`、run_db_hybrid_selection L541相当) |
| 4+1役割(topic1+important4) | あり(テンプレートに記載) | あり(同テンプレ+backup_itemによる機械置換) |
| Level別 | Std(a2, `writer/std.md`)とAdv(b1b, `writer/r2.md`)を別々に実行(本文が異なる) | 同じ入口をLevel毎に呼べる。Level別のロジック差なし(processでモデル解決のみ) |
| 選定後Validator | `p2g.validate_min_unit_selection`相当 -> `run_key_phrase_canonicalization`(Rule7等) -> Redundancy QA -> symbol gate | 同一module(gate内`p2g.validate_min_unit_selection`、canonicalization、Redundancy QA、symbol gateはZの外側retryがそのまま呼ぶ) |
| Rule7 INVALID | 発生(OPEN-310: LLMが人称代名詞を`someone`へ一般化し`source_span`と不一致。Melos Std 3 attempt中2回INVALID) | 候補はsource_spanの実在n-gram由来で、display_phraseは候補canonical_form。ただしcanonicalization LLM段は共通なので完全には消えない(Trialで測定) |
| retry/fallback | Z限定外側retry(canonicalization INVALID時のみ、通算3回、`Z_KP_OUTER_RETRY_MAX`)+Redundancy NG時`KEY_PHRASE_REDUNDANCY_RETRY_MAX` | X: DbHybridFailure -> Strategy Lへfallback(`fallback_allowed`=Falseのときのみ停止)、`KP_ARTICLE_COST_CAP_JPY`(既定¥15)で累積コストSTOP、shortlist_cacheでretry時の再照会回避 |
| 費用(実測) | Melos run_e2e_02 kp段: 13 call(KP選定+canon+redundancy+explanation) JPY5.35、616秒(Std 3 attempt+Adv 1 attempt) [`cost_log.jsonl` stage=kp、er009 pricingで再計算] | X参考: 選定1call約JPY0.29-0.40(er064 cost_r1.json)。canon/redundancyはZと共通。Wiktionary照会(M2)追加: 単独185秒(Lemon)、4並列で176秒(phase1実測。委任文の「約43秒」とは乖離) |
| 処理時間 | 1 attempt約40-70秒(LLM) | LLM 1 call約30-40秒 + M2供給(Wiktionary照会、8 API call、約45-176秒) |
| Family X固有の前提 | - | guidance文言はNews専用語なし(「記事理解・再利用価値の高い重要な名詞・専門用語・複合語」「[重要な単語・単語群候補]」等。「専門用語」のみNews色)。Points/In One Lineへの依存なし(KP stageは本文のみ入力)。タイトルは`# 見出し`から取得(Zのcanonical本文はタイトル除去済み、Phase1実測でタイトルの有無はshortlistを変えない=Topic行1行のみ) |
| Family Z固有 | 台詞(引用符内)・固有名詞(Melos等)・物語の比喩が主 | 候補生成はIdiom DB/n-gram/Wiktionary辞書ヒットが前提。物語の比喩・台詞由来表現(`pulled him under`、`far bank`、`in your place`)が辞書にヒットしない可能性。固有名詞は候補化しない(Phase1実測: Melosを含む候補なし) |
| telemetry書込 | `er030_output/kp_backend_telemetry_01/telemetry.jsonl`(strategy_lも1行) | 同左(Trialでは`_log_kp_backend_telemetry`をno-op化) |

## 2. `family_profile="family_z"`のNotImplementedError位置と最小差分

- 発生箇所: `er030_key_phrase_db_hybrid_source_reference_contract_01.py` L62 `SUPPORTED_FAMILY_PROFILES = ("family_x",)`、`_check_family_profile_supported`(L65)、`_selection_guidance_for_family`(L199-203)。呼出し元: selector L483(冒頭fail-closed)、contract gate L573、`build_lightweight_user_message` L225。
- **Production実装の最小差分(未実装・未承認)**:
  - 案1a(推奨候補): `family_profile`の追加は不要。Zからも`family_profile="family_x"`(既定)で呼ぶ。guidance逐語のためNotImplementedErrorに触れない。Telemetryのfamily名が"family_x"で記録される点だけ要判断(観測性)。
  - 案1b: `SUPPORTED_FAMILY_PROFILES`に"family_z"を追加し、`_selection_guidance_for_family`が同じ定数を返す(2箇所の追記のみ、guidance差分ゼロ)。telemetryにfamily_zが残る。共有module編集のため、N01/M2P0 Wiring委任(別sonnet-worker)と同一ファイル競合しうる(本委任では編集しない)。
  - Z側配線: `w62.run_kp_with_outer_retry`の`select_fn`へ`functools.partial(sc.run_key_phrase_selection, kp_backend="db_hybrid", shortlist_cache=...)`を渡す(`select_fn`引数は既存)。`er026 stage_kp`は`ctx.hooks.get("kp_fn")`を注入点として既に持つ。**Production module編集は不要**で配線できるが、Zのstage_kp/w62.run_kp_stageを変更する場合はer062/er026の編集=別承認。
  - Zの`Z_KP_GENERIC_NOTE`(所有格回避、OPEN-310暫定)は`diagnostic_note`として選定メッセージ末尾に追記される。DB Hybridでも同じ経路で付く(Trial armはこれを維持。OPEN-310回避の継続要否は別判断)。

## 3. Phase 1 実測(オフライン、M2供給+メッセージ組立のみ、LLM無し)

phase1/phase1_summary.json参照。4並列、Wiktionary照会は各記事8 API call(candidates_checked 369-388)。

| 原稿 | shortlist | phrase | important | word | 予約枠(reserved) | 所要 |
|---|---|---|---|---|---|---|
| Melos Std(title有/無) | 25 | 19 | 1 | 5 | blocked his way / remember its exact / ordered his death | 176秒(4並列) |
| Melos Adv | 25 | 16 | 4 | 5 | stained his feet / see her wedding / out his hands | 177秒 |
| Lemon L11(別原稿、title=The Lemon on the Books) | 24 | 16 | 3 | 5 | all my worries / catch my breath | 185秒(単独) |

- 現行Strategy L最終KP(Std): pull someone under / in your place / lose trust in someone / hold out / far bank。(Adv): sentence someone to death / current / hold out / seize / abandon。
- **shortlistに存在するのは`held out`のみ**(Std/Adv共通、Strategy Lの`hold out`に対応)。`pulled him under` `far bank` `in your place` `lost my trust in you` `sentence ... to death`は候補に無い。DB Hybrid + M2P0は、shortlistが物語の比喩・台詞由来表現を持たないため、選定段の前に取りこぼしが発生する構造的リスクが実測で確認された(最終KPの評価はPhase 2で実施)。
- 予約枠(M2の(a)(b2))は`ordered his death` `blocked his way` `remember its exact`等、断片的で学習価値の低い候補を供給しており、News向けに設計された(a)(b2)ルールがFictionの文では価値の高い慣用表現を拾えない/断片を拾う兆候。
- Lemon L11でも同様: `catch my breath`(予約枠、良質)以外は`books on` `to go` `and all` `one side`等の断片・低価値候補が多く、`fruit shop` `green coat`等の名詞句がimportant枠。

## 4. 補足(Phase 1所見)

- 時間: M2供給のWiktionary照会は単独実行でも約185秒/記事/Level(委任文記載の約43秒より大幅に長い)。Strategy L比で処理時間が増える主因。
- Zの`Z_KP_OUTER_RETRY_MAX=3`は`select_fn`引数でDB Hybridへ差し替え可能(Production module無編集で配線可、`shortlist_cache`でretry時の再照会は回避)。
