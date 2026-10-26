# IMPL_PLAN_01: 実装差分計画(委任_02用。本委任ではコード無編集)
KP-PHRASE7-WORD5-PRODUCTION-01 委任_01 / 2026-10-27。前提: `DESIGN_01.md`のFable設計判断D1〜D6確定後、**Opus条件A review(`OPUS_REVIEW_REQUEST_01.md`)実施後**に着手。実装は**単一の機能commit系列**(R0=git revert 1手順で戻せるよう、Prompt差替・上限・補完改訂を連続commitにしてrevert範囲を明示)。

## 1. 変更ファイル一覧(所有境界を明記)
| # | ファイル | 変更 | 規模 |
|---|---|---|---|
| F1 | `er119_kp_p7w5_prompts_01.py`(**新規**) | P7_TEXT(`ft.PROMPT_2_TEXT`からreplace生成、sha`2e930193…`をassert)、W5PRIME_TEXT(Trial W5の補足1行置換、sha案`187f1b87…`をassert)、`KP_PHRASE_MAX=7/KP_WORD_MAX=5`、`build_p7_message/build_w5_message/prefix_intact`、`PROMPT_IDS` | 約120行 |
| F2 | `er105_kp_fulltext_selector_01.py` | `validate_and_resolve(selected, units, *, max_items=KP_COUNT_MAX)`(`:225,230-231`)、`apply_exclusions(..., max_items=…)`(`:397,423-424`)、`build_user_message(…, prompt_text=None)`/`prompt_prefix_intact(…, prompt_text=None)`(`:109,117`)、`run_selection_gate(…, prompt_text=None, max_items=None, parse_fn=None)`(`:456`)、`run_fulltext_selection`の同引数と`prompt_id/sha`のmetadata(`:538,555`)、`build_exclusion_note(excluded, *, limit=3)`(`:388`)、`build_original_items`でresolved→itemへ`reason_ja`passthrough(`:281`)。**既定値=従来動作(Prompt 2本文・sha・3件は不変)** | 約60行 |
| F3 | `er119_kp_candidates_01.py` | (i)既定select_fn=新`select_p7`(`:292,317`)。(ii)`run_vocab_selection`(`:46`)にkeyword-only `prompt_text/ build_message/ prefix_check/ max_items/ single_word_only`(既定=2-V従来動作)。W5'経路で`single_word_only=True`(D3)。(iii)`:330`のcall2をW5'で呼ぶ。(iv)`:342`のreason_ja空文字→`it.get("reason_ja","")`。(v)組立後の種類別cap強制(`overflow_kind`、`:366`前)。(vi)`:425-432`doc: `prompt_ids/prompt_sha256`をP7/W5'へ、`shortfall_detail`に`cap_by_kind/missing_by_kind`追記(`:438`)。(vii)`_run_backfill`(`:456`): 種類別quota、フレーズ=P7/単語=W5'の最大2 call(並列)、結合した1回の`_gate_chain`、補完単語×全フレーズのcontainment、`backfill.prompts`追記。(viii)`candidate_doc_from_items`(mock用、`:553`)は`origin_split`据置 | 約150行 |
| F4 | `er119_kp_backfill_01.py` | `plan_quota`を種類別上限(`phrase_cap=7, word_cap=5`、現存種類別件数)へ(`:124`)、`BACKFILL_MAX_CALL_ITEMS`撤去/再定義(`:19`)、`NOT_COUNTED_STAGES`に`overflow_kind`追加(`:20`)、`count_exclusions`のkind判定を`not_single_word`でword固定(`:99,117`)、`not_triggered_record`のreason(`no_room`は種類別) | 約40行 |
| F5 | `er119_kp_human_review_01.py` | `KP_CANDIDATE_MAX 8->12`(`:52`)のみ(+`KP_PHRASE_MAX/KP_WORD_MAX`の再export不要)。`auto_select`・`render_request_md`・`finalize_kp`は**無変更**(D2 a) | 1行 |
| F6 | `er106_joint_runtime_evidence_01.py` | `:45`のコメントで旧run専用と明記+P7 sha許容(`:813`) | 数行 |
| F7 | test群(`TEST_PLAN_01.md`) | 下記 | 新規約60+改訂約30 |
| F8 | `docs/research/KP-PHRASE7-WORD5-PRODUCTION-01/*`(IMPLEMENTATION_01.md, evidence) | 実装記録 | - |
| F9 | SSOT(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/`HISTORY_INDEX.md`/`ER-*_REPORT`該当) | 委任_02以降でFable指示の範囲 | - |

**触れないファイル**: `er005_*`/A/B/C系・`er003_v1_n3_01_scaffold_generate.py`(`run_key_phrase_selection`の`fulltext_p2`分岐=legacy経路。select_p7はscを経由せず`er105.run_fulltext_selection`を直接呼ぶ)、`er125`(救済)、`er108`(CMU)、canonicalization/gloss template、`er019/er121/er026`のrunner、`er120`(文法)、`user_test/selection_form_v3/**`、`export_form_data_01.py`/`build_data_01.py`。

## 2. 並行Agent所有ファイルとの境界(**委任_03でフォーム側へ引継ぎ**)
| 項目 | 内容 | 担当 |
|---|---|---|
| H1 | `export_form_data_01.py:112 sd.get('cap', 8)`の既定を12へ、`shortfall_detail.cap_by_kind/missing_by_kind`の表示追記(任意) | 委任_03(フォーム側Agent) |
| H2 | 7+5候補doc(12件)をexport→フォームJSONに通す結合検証(`phrases<=7, words<=5, overflow=0`)。本件のevidence docを入力に提供 | 委任_03(本件は候補docパスを渡す) |
| H3 | 送信schema v2(日本語訳・区分・文法解説全文・コメント)との整合 | 並行Agent(a)の委任_02 |
本委任・委任_02では上記ファイルを**読むのみ**。

## 3. 実装順序(並列可能単位を明示)
依存: F1→F2→F3(select_p7)→F4/F3(backfill)。F5は独立。
- **Wave 0(並列)**: (a)F1新module+pin test、(b)F2 er105のkeyword-only引数追加+既存er105 test回帰(挙動不変の確認)、(c)F5 1行+既存test更新。互いに別ファイル。
- **Wave 1(直列、F3/F4は同一ファイル系)**: F3-(ii)(iii)(iv) call2/call1統合 → golden固定(下記) → F3-(v)(vi) cap/doc → F4+F3-(vii) 補完改訂。
- **Wave 2(並列)**: test作成(補完×種類別、DefaultOn、isolation、E2E mock)とEVIDENCE準備(run dirコピー・stop確認helper)はWave 1実装中に先行できる。
- **Wave 3**: 全test→全回帰(`run_project_regression.py`、実装commit後)→evidence(`EVIDENCE_PLAN_01.md`)→SSOT→Fable受入。
- R-6の教訓継承: **`_gate_chain`は触らない**。改訂前のHEADで13 scenario相当の候補docをgolden固定し、7+5実装後も「Gate連鎖は同一入力→同一出力」を確認(Prompt差替以外の副作用検出)。

## 4. 関数別変更の具体
1. `select_p7(text, work, article_id, source_level, process=None, diagnostic_note=None, kp_backend=None, **kw) -> dict`(F1またはF3): `er105.run_fulltext_selection(…, prompt_text=P7_TEXT, max_items=7, parse_fn=p2v.parse_selection, make_call_fn=lambda m: p2v.make_vocab_selector_fn(m, model=ft.resolve_model(process)))`。戻り値は`sc.run_key_phrase_selection`と同形(`status/parsed/model_id/original_items/kp_backend_used/kp_attempts/shortfall`)。`kp_backend_used="fulltext_p7"`。telemetry(`sc._log_kp_backend_telemetry`)は`sc`のprivateのため、**`er003`を触らず**同等のtelemetryを`select_p7`内で呼ぶか、telemetry欠落が`kp_backend_telemetry`集計に影響しないかを実装前に確認(Opus論点)。注入`select_fn`(test/mock)は従来どおり優先。
2. `run_vocab_selection`の拡張: 既定引数のまま呼べば現行と同一。W5'経路は`prompt_text=W5PRIME_TEXT, build_message=build_w5_message, prefix_check=…, max_items=5, single_word_only=True`。`single_word_only`で`validate`後・`duplicate_of_top3`前に`count_words!=1`→`dropped(stage="not_single_word")`(D3)。
3. `_generate_candidates_impl`: `vocab_call_fn`既定None時のW5'呼出(現行はNoneで`p2v.make_vocab_selector_fn`直呼び→W5'のmessage builder経由)。`doc["prompt_ids"]={"call1":"kp_prompt_p7","call2":"kp_prompt_w5"}`、`prompt_sha256`同様。
4. 種類別cap強制: `cands`確定直後(`ai_rank`付番前)に`kind`別件数を数え、超過をdroppedへ(`overflow_kind`)。付番はその後。
5. `_run_backfill`: `counts=bf.count_exclusions`→`plan=bf.plan_quota(counts, n_phrase, n_word)`→`quota_phrase>0`ならP7補完、`quota_word>0`ならW5'補完(`concurrent.futures`、`contextvars.copy_context().run`でrescue_context/`_person_repair_subdir`を引継ぎ)→結合originals→`_gate_chain`(1回)→dedupe(R-3+単語×フレーズcontainment)→`pick_backfill`(種類別quota)。stop_checkは呼出前に1回。例外処理(R-8)は現行維持。
6. `shortfall`: `len(cands)<rv.KP_CANDIDATE_MAX`(=12)。

## 5. 旧ルール・旧検査の撤去/残置(Charter 8)
- 撤去: `BACKFILL_MAX_CALL_ITEMS=5`による上限(`backfill:19,128`)と`cap=KP_CANDIDATE_MAX`単一上限でのroom計算(`candidates:467`)→種類別上限へ置換。「補完は2-V(混在)」の記述(`candidates:9-10`のdocstring, `DESIGN_02`は履歴として不変)。
- 残置: Prompt 2/2-V本文・pin test・`run_vocab_selection`の2-V既定・legacy `run_kp_with_outer_retry`(`er003:753`)。実装後Grepで未参照を確認、撤去はD1確定後の別判断。
- 実装後に残存Grep: `Grep "KP_CANDIDATE_MAX|BACKFILL_MAX_CALL_ITEMS|PROMPT_2V_TEXT|PROMPT_2_TEXT|SELECTOR_2V_MAX_ITEMS|8件|最大8|TOP 8"`(コード・docstring・test・依頼書文言)で旧3+5/8件の記述の取りこぼしを確認(`er119_kp_candidates_01.py:2`の"TOP 8"見出し・`er026:2012`のコメント"候補(最大8)"等)。

## 6. 完了条件(委任_02)
全unit/golden/DefaultOn/isolation test PASS、既存回帰(failed 0/errors 0、HEAD既存失敗は区別記録)、API 0でのmock E2E(X/Y/Z×Std/Adv、`kp_generate_fn`注入)PASS。実API evidenceは委任_03。
