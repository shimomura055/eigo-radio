# TRACK_B_EVIDENCE_01 — 生成・重複判定の共通module `er134_nuance_explanation_01` (NUANCE-EXPLANATION-PRODUCTION-WIRING-01 委任_02A、2026-10-29)

Status: 実装済み(未配線)。Production runner・HR・フォーム・表示からは呼ばれない(Track A/02Bの範囲)。Prompt v3.1の実機検証は `PROMPT_V3_VERIFY_01.md`。VALIDATED/APPROVED_FOR_PRODUCTION/PRODUCTION_WIREDの付与なし。
正本: ユーザー原文 §2A/B・§3・§5、`WIRING_DESIGN_01.md`(§3 schema・§4・§5)、`OPUS_REVIEW_01.md`(M-1〜M-10・R-1〜R-16、Fable判断で全件採用)。

## 1. 関数境界(`er134_nuance_explanation_01.py`)

| 関数 | 役割 | LLM | 備考 |
|---|---|---|---|
| `build_inputs(family, article_id, title, level, paragraphs, kp_cands, grammar_items, provisional_ids=None, std_part1=True)` | 暫定選定(`rv.auto_select`のvocab最大5件)+提示pool(`presented_pool`)+文法Top2を組立。`pool_identity_sha`・`grammar_identity_sha`・`text_sha256`(=`er120.text_sha256`)を付与 | 0 | level必須・既定値なし。暫定idがpool外=`NuanceInputError`(推測補完なし) |
| `presented_pool(kp_cands)` | exporter(`export_form_data_01.convert`)と同じ提示集合: `ai_rank`順、`phrase[:cbk.phrase]+word[:cbk.word]`(DEFAULT_CAP=12=7+5。docの`shortfall_detail.cap_by_kind`優先) | 0 | 実exporterと突合するtestで固定(M-4) |
| `derive_focus_terms(expression)` | `A vs B` / `A / B` / `A ↔ B`を各側の主表現に分割。引用符・末尾記号除去、重複除去 | 0 | Promptに`focus_terms`は無い(M-8)。LLM出力の`focus_terms`は無視 |
| `structural_check(expression, pool)` | 段1(決定論)。自動NG=主表現が項目の句と**一致**、または複数語の項目句が主表現に**連続して丸ごと含まれる**。それ以外の語共有は`shared`(段2ヒント+HR表示用) | 0 | 所有格/someone/屈折を正規化。`verdict=fail`は**暫定選定**に自動NGがあるときのみ(pool項目への自動NGは`pool_conflicts`側) |
| `quote_check(quote_en, body)` | 本文の**連続した1〜2文**の逐語部分文字列、段落またぎ不可。引用符/空白差は吸収し本文側の文字列を返す | 0 | 曲がった引用符の規則は文法の`_qn`と同じ(parity test) |
| `generate_candidate(inputs, call_fn)` | Prompt v3.1で1 call(+技術retry1回)。配列/複数件/必須欠落/explanation長範囲外/引用不一致=不正 | 1(+1) | `learning_value_self_rating != "high"`は決定論で0件(R-9) |
| `judge_overlap(inputs, cand, stage1, judge_fn)` | 別Prompt・別call。提示pool全件+文法Top2を`K1..Kn/G1..Gm`で提示、`items[{id,same,why(trueのみ)}]`+`closest`。**欠落・重複・余分・非boolはJSON不正**→retry1回→`ok=False` | 1(+1) | 生成側の`differs_from_kp_word_ja`/`criteria_check`/自己評価は渡さない(R-8) |
| `decide(inputs, cand, stage1, judge)` | `overlap_check`を**決定論**で算出(LLMのverdict欄は無い)。`pass`/`fail`(暫定選定のどれかがsame_focus)/`unverified`(必須NGなしで段2不能)。pool項目のsame_focus=`pool_conflicts`、文法=`grammar_conflicts`(警告のみ。verdictに影響しない)、語共有のみ=`shared_terms`(`stage2_pass`付き) | 0 | `against[]`=提示pool全件+文法Top2(M-4) |
| `run_candidate(inputs, call_fn, judge_fn, budget_guard)` | N1中核(保存なし)。生成→段1→(段1failなら判定を省略)→段2→decide。技術失敗は例外にせず`FAILED_TECHNICAL` | 1〜4 | 次点繰上げ・再生成・自動補充の関数/引数は存在しない(A-7。test済) |
| `ensure_spec(study_dir, level, new_review)` | N0。`nuance_spec.json`の発行は**新規KP review作成時**(`new_review=True`)だけ(M-2)。既存は不変(冪等)。無く`new_review=False`=LEGACY | 0 | 発行条件の判定自体(新規review作成フック)はTrack A |
| `candidate_stage(study_dir, inputs, ..., auto_adopted=False)` | N1(保存あり)。LEGACY/AUTO採用=生成0。resumeは`text_sha256`・`pool_identity_sha`・`grammar_identity_sha`・`provisional_ids`・prompt shaが一致でAPI 0再利用(M-3: `candidates_sha256`は再利用判定に使わない)。不一致=旧docを`nuance_candidate.STALE_<sha8>.json`へ退避(削除しない)。`FAILED_TECHNICAL`はresumeで自動再試行1回まで(R-5) | 0〜4 | `nuance_failed.json`も書く |
| `candidate_sha256(c)` | HR提示/確定の照合キー。`expression/focus/explanation_ja/quote_en/quote_ja/focus_terms`の正規化(引用符直線化・空白圧縮)jsha | 0 | U-11 |

routing: `er006_model_routing_contract_01.PROCESS_MODEL_MAP` に `NUANCE_EXPLANATION` / `NUANCE_OVERLAP_JUDGE`(いずれも`SUPPORT_MODEL`=gpt-6-luna、追加のみ)を登録。LLM呼出は全て`routing.require_model(process, MODEL)`経由。応答model不一致=`NuanceModelContractError`(retry/fallbackなし、STOP)。`budget_guard(process, prompt, attempt)`の例外・`ModelContractViolation`・`KeyboardInterrupt`は伝播(STOP)。API障害・JSON不正・引用不一致・判定不能は非ブロッキング(`FAILED_TECHNICAL`、本物の0件`NO_CANDIDATE`と区別)。

## 2. schema最終版(`nuance_candidate.json`、`schema="nuance_candidate_v1"`。WIRING_DESIGN §3 + §3.3 + Opus修正。追加のみ)

最上位: `schema, family, article_id, level(表示名), level_key(a2|b1b), generated_at, status(CANDIDATE|NO_CANDIDATE|FAILED_TECHNICAL), candidate(null|object), no_candidate_reason, kp_word_basis, text_sha256, model, prompt_sha, judge_prompt_sha, generation{prompt_sha256, rejected_candidates, model_reason_ja}, usage{input_tokens, output_tokens, cost_jpy, n_calls, calls[{process, attempt, response_model, usage, response_id, elapsed_sec, cost_jpy}]}`。条件付き: `failed_technical{kind, detail}`(kind = `api_error|gen_json_invalid|quote_mismatch|overlap_unverified`)、`rejected_candidate_audit{candidate, overlap_check|reason}`(重複NG・低評価・判定不能で破棄した候補。HR・ページには出さない)、`resume_attempts`。
`no_candidate_reason`: `model_returned_none | self_rating_not_high | overlap_ng | auto_adopted_no_human_review | failed_technical:<kind>`。
`kp_word_basis`(`status="provisional"`): `items[]`(暫定選定の表現)、`provisional_ids[]`、`pool_ids[{id,kind}]`(提示pool全件+文法Top2〔kind=grammar〕)、`candidates_sha256`(HR提示時のフォーム鮮度確認用)、`pool_identity_sha`・`grammar_identity_sha`(確定後・再利用の判定用。M-3)。
`candidate`(CANDIDATEのみ): `expression, focus, focus_terms[](決定論導出), explanation_ja, quote_en(本文側の逐語), quote_ja, learning_value_self_rating("high"のみ到達), generation_meta{differs_from_kp_word_ja, criteria_check, learning_value_reason_ja}(監査用。判定には渡さない), overlap_check, pool_conflicts[candidate_id], grammar_conflicts[candidate_id](警告), shared_terms[{item_id,item,term,shared[],stage2_pass}], candidate_sha256`。
`overlap_check`: `verdict(pass|fail|unverified), stage1_structural{verdict, matched[], shared_terms[]}, stage2_llm{verdict(pass|fail|skipped|unverified), model, closest{item_id,label,why}}, reason(決定論の日本語), against[{item_id,item,kind(phrase|word|grammar),provisional,same_focus,source(stage1_auto|stage2|stage1_auto+stage2|none),note,stage2_judged}], pool_conflicts, grammar_conflicts, shared_terms, required_conflicts`。
WIRING_DESIGN §3からの差分(全て追加・意味変更): ①`overlap_check.verdict`に`unverified`(判定不能。候補はHRに出さず`FAILED_TECHNICAL`)、②`stage2_llm.reason`を`overlap_check.reason`(決定論)へ一本化し`closest`を追加、③`against[].kind`に`grammar`を追加、`same_focus`の出所`source`を追加、④`grammar_conflicts`/`shared_terms`/`pool_identity_sha`/`grammar_identity_sha`/`judge_prompt_sha`/`failed_technical`/`resume_attempts`を追加、⑤`candidate.generation_meta`で生成側の自己申告を隔離。

## 3. Opus修正・Fable判断との対応

| 項目 | 実装 | test |
|---|---|---|
| F-1/R-1 文法はハードNGにしない | `decide`: 文法のsame_focusは`grammar_conflicts`(警告)のみ。verdict不変 | test_u7, プローブp4 |
| F-2/R-2 段1自動NG=一致 or 複数語KPの連続包含、他は段2ヒント | `structural_check`、`shared_terms.stage2_pass` | test_r2_* (`can't be helped`⊂`I guess it can't be helped`、`was linked to`/`weak link`) |
| M-4 per_item全件・verdict決定論・against=提示pool全件+文法 | `_parse_validate_judge`、`decide`、`presented_pool`(exporter parity) | test_m4_* |
| M-8 入力形・`focus_terms`はPromptに入れない | `build_inputs`、`build_gen_prompt` | test_m8_*、`PROMPT_V3_VERIFY_01.md` |
| M-9 引用=連続1〜2文の逐語、引用符正規化=文法と同規則 | `quote_check`、`_qn`/`_SENT_RE` parity | test_m9_* |
| R-8 判定は別Prompt・自己申告を渡さない・入れ替えテスト・closest | `PROMPT_JUDGE` | test_r8_*、プローブ6件 |
| R-9 Stdの除外理由を「文法コーナーの領域」へ、語用はStdでも可、`mid`は決定論0件 | `PROMPT_GEN`条件3、`generate_candidate` | test_r9_* |
| R-10 圧縮形出力・process2件追加・費用記録 | `PROMPT_JUDGE`出力、routing、`usage.calls[]` | test_r10_* |
| OK-4/R-5 fail-closed・非ブロッキング・本物の0件と区別 | `FAILED_TECHNICAL`、`resume_attempts` | test_r15_*、test_failed_technical_resume_* |
| M-2 N0は新規review作成時のみ | `ensure_spec(new_review=...)` | test_u16 |
| M-3 確定後/再利用のbinding | `pool_identity_sha`、`_stale_reasons`(`candidates_sha256`を使わない) | test_resume_reuse_and_stale_archive |
| 禁止事項(Part 4・2件以上・自動補充・見出し「Deeper Understanding」) | Prompt/関数に存在しない | test_u12、test_no_human_review_substitute_functions |
| (Opus M-1/M-5/M-6/M-7/M-10、R-3/R-4/R-6/R-7/R-11〜R-16) | **本Trackの範囲外**(runner配線・表示・検証・evidence手順。Track A/02B) | - |

## 4. テスト結果

- 新規 `er134_nuance_explanation_01_test_01.py`: **45 test 全PASS**(mock LLM、API 0、実output dirへ書込なし)。U-1〜U-16(U-14=AUTO採用/U-15=LEGACY/U-16=N0を含む)+M-4/M-8/M-9/R-2/R-8/R-9/R-10/R-15 該当。実exporter(`export_form_data_01.convert`)とのpool parity、文法(`er120`)との`_qn`/`_SENT_RE`/`LEVELS`/`text_sha256` parityを含む。
  実行: `.venv\Scripts\python.exe -m unittest er134_nuance_explanation_01_test_01 -v`(または pytest)。
- 隣接regression(関連13ファイル): **279 passed / 2 failed**。2件とも**本委任と無関係の既存failure**(①は変更前の実行で同一failureを確認、②は`er121_family_y_*`のimportが原因で`er134`は違反リストに入っていない): ①`er054_family_z_story_pool_trial_02_test_01::test_production_keys_unchanged`(`FAMILY_Y_*` routing keys 11件が閉集合に無い。Y Production立上げ由来)、②`er119_isolation_test_01::test_only_x_z_runners_import_er119`(`er121_family_y_*`の4 moduleが許可リストに無い)。本委任で追加した許可/閉集合更新は、`NUANCE_EXPLANATION`/`NUANCE_OVERLAP_JUDGE`(er053 NEW_KEYS、er054 LATER_APPROVED_PRODUCTION_KEYS、er009 TABLE_PATH_PROCESSES)と、`er119_isolation_test_01`のALLOWEDへ`er134_nuance_explanation_01.py`の追加のみ。
- 実機(有料): Prompt v3.1を8 levelで実行(7候補・1件0件、FAILED_TECHNICAL 0)、プローブ6/6一致。詳細・費用 ¥3.325 = `PROMPT_V3_VERIFY_01.md`。

## 5. Track A/02Bへの引継ぎ(実装済みのcontractと未実装の接続点)

- 実装済み(呼べばよい): `build_inputs` / `candidate_stage`(N0 `ensure_spec`は新規review作成フックから`new_review=True`で)/ `candidate_sha256` / `pool_identity_sha` / `derive_focus_terms` / 出力docの`overlap_check`・`pool_conflicts`・`grammar_conflicts`・`shared_terms`(HR画面の「語の共有あり」/警告表示用)/ `status`(`FAILED_TECHNICAL`は「候補なし(技術失敗)」と区別して表示)。
- 未実装(本Track外): N2 `confirm_check`(確定した①②の全idが`against[].item_id`に含まれることの被覆検査〔M-4〕と`pool_conflicts`交差のISSUE)、N3 `finalize_stage`/`require_final`、フォーム/exporter/`cmd_from_form`、描画、page_verify、DEPENDENTS/STAGE_EST、`ZERO_P2`の撤去。`against[]`には提示pool全件の`item_id`が入るので、N2の被覆検査はそれを参照すればよい。
- Y/Zの`kp_candidates.json`はrun直下の`key_phrases/<lv>/kp_candidates.json`、Xは`<lv>/key_phrases/kp_candidates.json`、文法候補は`er120_part2_wiring_01.study_dir_for`のstudy dir配下(`grammar_candidates.json`の`candidates[:2]`が提示Top2。`form_grammar_bundle`の`items`〔id/title/example/rank〕を渡してもよい)。

## 6. Production安全性(CLAUDE.md・sonnet-worker 11-7)

- 新module `er134`はどのrunner・HR・フォーム・表示からもimportされない(02A時点)。API呼出は`generate_candidate`/`judge_overlap`が呼ばれたときだけで、import時・`build_inputs`時には`client`も触らない(test済)。環境変数・設定dict・modeによるON経路は存在しない(`os.environ`/`getenv`不使用をtestで固定)。未承認の既定動作化なし。
- routing contractに2 keyを追加したが、参照元がTrack A配線までない(DEFAULT_OFFではなく「未配線」)。既存keyの値は不変(HEAD比較test PASS)。
- 既存のretry/fallback/Gate(`routing.require_model`、技術retry1回、STOP通知、予算guard)を迂回しない。
