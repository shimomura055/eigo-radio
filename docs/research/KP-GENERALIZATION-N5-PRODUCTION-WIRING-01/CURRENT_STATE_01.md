# CURRENT_STATE_01: KP一般化N5方式のProduction配線 現状調査(KP-GENERALIZATION-N5-PRODUCTION-WIRING-01 委任_01、2026-10-30、API 0・Productionコード変更0)

原文=`docs/pm/delegation_log/2026-10-30_KP-GENERALIZATION-N5-PRODUCTION-WIRING-01_USER.md`(逐語保存済み。:7-9 採用方式B=N5/APPROVED_FOR_PRODUCTION/PRODUCTION_WIRED目標、:21 D/E1L/E4/N2再判断不要、:59 新Gate・Prompt改善禁止)。
基点=origin/main 89343d65e。調査はread-only(Trial dirのkpg04_*・Production er*・llm_cache replay[API 0・cache hit確認])。未確認は「未確認」と明記。
Trial 03 = `docs/research/KP-GENERALIZATION-MEANING-PRESERVATION-TRIAL-03/`(以下 T3)。Trial 01/02 = `docs/research/KP-GENERALIZATION-CHUNK-VALUE-TRIAL-01|02/`(以下 T1/T2)。既存の現状整理=`T1/CURRENT_STATE_01.md`(本書はそれを再利用し、N5固有部とfile:lineを補う)。

## 0. 結論(要点)
1. **正式Productionの単一合流点が存在する**: X/Y/Zの正式runnerは全て `er119_kp_wiring_01.run_kp_with_review` → `er119_kp_candidates_01.make_generate_fn` → `generate_candidates` → `_generate_candidates_impl` を通る(X `er019_family_x_audio_production_runner_01.py:997`、Y `er121_family_y_runner_01.py:583`、Z `er026_family_z_fiction_production_runner_01.py:2218`)。初回・外側retry・補完(backfill)・Human NG再選定round・resume(保存済み候補doc読戻し)は全てこの関数群の内側。一般化(原型化)工程は `_gate_chain` 内の `canon_fn`(既定=`sc.run_key_phrase_canonicalization`、`er119_kp_candidates_01.py:209,366-368`)の1点で、初回(`:430`)と補完(`:641`)が共通に呼ぶ。
2. **Trial 03のN5は「一般化だけ」ではなく B1過剰生成→SEL(塊価値判定)→pick(cap7)→GEN5→VER5→CHK5(全件) の連鎖**(`T3/kpg04_methods.py` run_N と `ARMS["N5"]`)。Production現行の「P7選定→canonicalization(規則1〜5・QA12項目)→gloss再整合」とは**工程単位で一対一に置換できない**(§4の表)。配線設計(DESIGN_01.md)の最大論点。
3. **Productionに旧D/E1L/E4/N2/kpg系の参照は無い**(§5のGrep結果)。Dangling候補は `user_test/kp_generalization_trial_02|03/index.html`(Trial比較ページ、非Production)のみ。
4. **N5移植に必要だが現Productionに無い依存**: (a) NLTK WordNetデータ(Trialは `T1/nltk_data`[untracked・11MB]。SELのPromptにも「WordNet複合語見出し」ヒントが入る)、(b) `gemini-3.8-flash`(VER5)と `gpt-6.1-sol`(CHK5)のKP用routing名、(c) `gemini-3.8-flash`の `pricing_snapshot.json` 単価(`er005_output/cost_baseline_01/pricing_snapshot.json` に未登録。gpt-6.1-sol・gpt-6-lunaは登録あり)。

## 1. 正式Production経路(KP候補生成・一般化)の関数と呼出順(file:line)
| # | 工程 | 実装(file:line) | モデル/Prompt | 備考 |
|---|---|---|---|---|
| 1 | 入口 | `er119_kp_wiring_01.py:60` run_kp_with_review(X/Z共通、Yも使用) → `rv.ensure_kp_review`(`er119_kp_human_review_01.py:1628`) | - | resume=保存候補doc(本文sha一致)の読戻し・再生成なし(`:1639-1700`、API 0) |
| 2 | 候補生成入口 | `er119_kp_candidates_01.py:348` generate_candidates(`er125.rescue_context`内) → `:355` _generate_candidates_impl | - | 全Family共通 |
| 3 | call1 フレーズ選定 | `:390` select_fn=`select_p7`(`:306`) → `er105.run_fulltext_selection`(MAX_ATTEMPTS=2 `er105_kp_fulltext_selector_01.py:38`) | gpt-6-luna(`er105:36` SELECTION_MODEL_ID、`resolve_model :348-357`でA2_SUPPORT/B1_SUPPORTのみ許可)、P7 Prompt(sha固定`er119_kp_p7w5_prompts_01.py:42-44`) | 最大7件・本文一致/1〜5語/CMU/除外句/救済(H1/H2)の各Gate |
| 4 | call2 単語選定 | `:403` run_vocab_selection(spec=W5') | luna、W5'(`p7w5.py:71`) | 1語のみ(not_single_word)、最大5 |
| 5 | Human NG再照合 | `_screen_human_ng`(`:186`) | API 0 | NG一致はdropped(stage=human_ng) |
| 6 | **一般化(原型化)+意味付与** | `:430` `_gate_chain`(`:199`) → `:209` **canon_fn**(= `sc.run_key_phrase_canonicalization`、`er003_v1_n3_01_scaffold_generate.py:475-`。救済有効時 `rescue=True` partial `er119_kp_candidates_01.py:366-368`) | luna(`routing.require_model(process, SUPPORT_MODEL)`)、fulltext版テンプレ(`er003_v1_translator_briefs/b1_p2_keywords_canonicalization_fulltext_prompt_template.txt`)、schema=`kc.CANONICALIZATION_JSON_SCHEMA_FULLTEXT` | 規則1〜5(文脈限定語除去/意味補語復元/人称one's・someone's/lemma化/指示語)。出力=key_phrase・QA12項目・possessor_roles。決定論validate=`kc._is_valid_fulltext_normalization`(`er003_key_words_canonicalization.py:529`)、merge=`kc.merge_canonicalization_result`(`:830-`、used_form=key_phrase) |
| 6b | gloss再整合 | canon関数内 `gloss_align.align_glosses`(`er003_key_words_gloss_alignment.py:1022`、対象選定`:217` select_alignment_targets=KPが表示候補より語を足した/kp_extends_beyond_candidate) + 人称整合(`:275-361`)・全文glossの新規生成(`:340` is_fulltext_gloss_missing) | luna、承認済みgloss規則 | kill switch `EIGO_KP_GLOSS_ALIGNMENT`(既定ON、`:43`) |
| 6c | 救済(rescue) | `er125_kp_rescue_production_01.py`(H1 助動詞例外/H2 選定段/H3 canon段 revert・M1再導出+QA再判定+gloss強制再整合/H4 annotate) | luna(H3のQA再判定1 call) | kill switch `EIGO_KP_RESCUE`(既定ON `:48`)。`generate_candidates`実行中のみ有効(contextvar `:59`) |
| 7 | 後段Gate | `_gate_chain`内 `:222-300`: CMU post-canon・記号・人称整合(Z)・SRC D1(Z)・Human NG(used_form照合)・presentable filter(`rv.presentation_blockers` `er119_kp_human_review_01.py:521-546`、qa_overall_status==PASS必須=fail-closed) | cmu/決定論 | 品質基準(QA12項目)は不変(spec①) |
| 8 | 種類別cap | `:441` `_enforce_kind_caps`(`:331`)(フレーズ7/単語5) | - | |
| 9 | 補完(backfill) | `:447` `_run_backfill`(`:566`) → 同じ `_gate_chain`(`:641`)、P7/W5'を種類別に1回 | luna | kill switch `EIGO_KP_BACKFILL`(既定ON `er119_kp_backfill_01.py:19`)。初回合格候補は入替えない |
| 10 | Redundancy QA | `:466` redundancy_fn(アラームのみ) | luna | |
| 11 | **難易度4段階付与(hook)** | `:498-515` `dg.apply_to_candidates`(`er119_kp_difficulty_01.py:187`、1 generate=1 call、fail-open=`unknown`) | luna(`:152-156`でroutingとSELECTION_MODEL_ID一致を検査) | 入力=`used_form`(`:72`)。Gateではない(除外・並替えなし) |
| 12 | 候補doc | `:506-` doc(prompt_ids/sha、model_id、candidates、dropped、backfill、difficulty_grading)→ `rv.save_candidates`(`:1055`) | - | `candidates[*].item`=merged item(§1下表) |
| 13 | Human Review | `rv.ensure_kp_review` → HR依頼書/選定フォームv3: `docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/tools/export_form_data_01.py:164-176`(term=`used_form`、meaning_ja/ja_gloss=`japanese_gloss`、excerpt=`source_sentence`、selection_phraseがtermと異なれば併記)、`user_test/selection_form_v3/` | - | AI選定理由欄は画面非表示(`reason_ja`は内部保持) |
| 14 | 確定 | `rv.finalize_kp`(`er119_kp_human_review_01.py:1241`)が `<kp_dir>/keywords_canonicalized.json` を書く唯一の場所 | - | auto_select(`:705`)=HR回避時の決定論 |
| 15 | 後続 | KP英語音声=`item["used_form"]`(`er003_v1_n3_01_tts_generate.py:1277,1428`、`tts_safe_kp_en(used_form)`)、KP一般解説=`used_form`のみ(`er003_kp_general_explanation_01.py:130-132`)、日本語意味=`japanese_gloss`(+`japanese_gloss_tts`)、本文ハイライト=`source_span`(`er_learning_highlight_01.py:263`)、本文出典検査=`er003_v1_n3_01_assemble.py:394-410` | - | **「表示形(音声)=used_form」「本文根拠(ハイライト)=source_span」は既存の2フィールドで既に分離されている** |

### データ受渡しの既存field名(N5の3 fieldとの対応)
| N5(Trial `pack` `T2/kpg03_methods.py:265`) | Production既存field | 備考 |
|---|---|---|
| `display_form`(一般化表示形) | `used_form`(=`key_phrase`。`kc.merge_canonicalization_result`で同値) | 音声・フォーム・難易度・NG照合(used_form_key)・解説が参照 |
| `span`/`source_span`(本文根拠) | `source_span`(ハイライト/出典検査)・`selection_phrase`(candidate_id生成元`rv.candidate_id_for`、NG照合`rv.match_ng :372`)・`display_phrase`(選定時の表層形) | NG履歴のcandidate_idはselection_phrase基準なので一般化後も互換。T1 CURRENT_STATE_01の未確認事項(NG照合と旧used_form)は本調査で解消: `match_ng`はcandidate_id/phrase_key/used_form_keyのいずれか一致=exact |
| `gloss_ja` | `japanese_gloss` | gloss gate(`GLOSS_OFFICIAL_GATES`)・`gloss_alignment_status`と連動 |
| `source_sentence` | `source_sentence`/`source_sentence_id` | |
| `source_sense_ja`/`headword_frame`/`frame_change`/`reconcile`/`flags`/`check`/`reverted`/`display_form_pre_*` | (Productionに無い=新規監査field) | 追加fieldは後段が無視する見込み。合流点でpassthroughが必要か未確認(DESIGN 3-4) |

## 2. retry/fallback/regeneration/resume の分岐(旧方式へ戻りうる箇所の網羅)
| 分岐 | 実装(file:line) | 現状(N5未配線) | 設計上の要点 |
|---|---|---|---|
| 初回 | `_generate_candidates_impl :430` → `_gate_chain :209` | canon_fn1点 | |
| 外側retry(技術失敗/候補0) | `:385-` while、`MAX_CANON_RERUN=2`(`:42,206-`)、補完ON時は候補0件・技術失敗のみ | 同じ `_gate_chain` | N5のcall失敗(技術失敗→retry、ModelContract違反/STOP→伝播)を既存`bf.is_propagating_exception`と整合 |
| 補完(backfill) | `:447` → `_run_backfill :641` → `_gate_chain` | canon_fn共通 | 補完で追加探索された候補にもN5が掛かる設計にする |
| 再選定round(Human NG) | `rv.ensure_kp_review :1678-1699` generate_fn(round_no, ng_entries) | 同上 | |
| resume(保存候補doc読戻し) | `rv.ensure_kp_review :1639-1647`(API 0、provenance driftはlogのみ) | **読戻しのみ=再生成しない**。旧方式で作られた既存docはそのまま残る | docにgeneralization方式markerを付け、marker無docをresumeでlog検出(停止しない)する案 |
| 本文変更(STALE) | `:1663-1676` SUPERSEDEDへ退避→再生成 | 同上 | |
| X: 非Production互換分岐 | `er019...:1000-1002` `sc.run_key_phrases(kp_backend!=fulltext_p2)`(test/Trial用。`kp_backend`既定`fulltext_p2` `:901`) | **旧canonを使う(N5を通らない)** | 正式runnerの既定では到達しない。到達不能のreachability test or 明示ガードが必要 |
| 旧一般経路 `sc.run_key_phrases(fulltext_p2)`→`run_kp_with_outer_retry`(`er003_v1_n3_01_scaffold_generate.py:900-`) | 旧runのresume・復帰用(`er125 :57-`コメント「旧経路では発火しない」) | 旧canon | 正式runner(X/Y/Z)からは呼ばれない。A/B/C・Trial・migration(er073)は対象外 |
| Y/Z mock注入 | `gen_hook`/`generate_hook`(`er121:583`、`er026:2218`) | N5を通さない | test専用であること(DefaultOff型testで確認) |

## 3. 品質検査・Human Review・救済・gloss整合の現行契約(N5が満たすべき下流条件)
- **presentable filter**(`rv.presentation_blockers :521-546`、spec①、version `presentable_v1_2026-10-29` `:514`): item.qa_overall_status==`PASS`(欠落/未知はfail-closed)、救済canonicalization候補はQA再判定PASS+gloss再整合REALIGNED、gloss gate正式(`GLOSS_OFFICIAL_GATES`)・japanese_gloss非空。**N5が出力するitemがこの契約(qa/qa_overall_status/gates.gloss)をどう満たすかが配線の中核**(DESIGN_01 3-3)。
- **QA12項目**(`kc.QA_FIELDS :71-100`): standalone_natural_unit / no_residual_context_word / meaning_or_usage_unchanged / reusable_other_context / traceable_contiguous_span / listening_blocker_value_preserved / standalone_comprehensibility / not_over_minimized / context_sufficiency / core_meaning_preserved / no_semantic_role_loss / person_reference_generalized。Trial 03のN5はこれらを**実行していない**(T3 run_N にcanonicalizationなし)。
- **決定論validator**: Production=`kc._is_valid_fulltext_normalization`(key_phraseは「display_phraseと同じ/文脈限定語除去/source_span内連続部分/規則3〜5の1対1置換」のみ許容=**something/someone化・目的語DROPは許容外**)。Trial N5=`T1/kpg01_validate.display_check`(核語がsource_span語の語形違い・順序一致・placeholder規則)+`G.assemble`。別物(T1 CURRENT_STATE_01.md:41「別のvalidatorが必要」)。
- **gloss整合**: `select_alignment_targets`(`:217`)は `key_phrase` が `display_phrase` より語を足した/`kp_extends_beyond_candidate` のitemが対象。N5のdisplay_formはDROP/SLOTで**語を減らす/置換する**方向のため対象に入るかは未確認(DESIGN 3-5)。人称整合(`:275-361`)は `someone/one's` 形に対し日本語の具体人称語(彼/彼女…)を検出して再整合・HR接続=N5の `hear someone out` と日本語訳に直接効く既存仕様。
- **救済(er125)**: 選定段H1/H2は `validate_and_resolve`(P7/W5'出力の本文一致Gate)の救済で、N5の入力候補(P7出力)側に作用。canon段H3(`finalize_rescued_items`)はcanon関数の内側=canon_fn置換時の扱いが論点。
- **Human NG**: `rv.match_ng :372`(candidate_id/phrase_key/used_form_key exact、部分列=similar)。一般化後のused_form(例 `hear someone out`)でNG照合されるが、過去NG(旧used_form `hear it out`)はcandidate_id(selection_phrase基準)で引き続きexact一致(互換)。
- **難易度4段階**: `used_form`を見て付与(`er119_kp_difficulty_01.py:72`)。N5後の最終候補集合に1回。Trial SEL内の`difficulty`(advanced/upper_intermediate/easy)は**並び順(pick)にだけ使う別概念**で、4段階表示とは無関係(混同しない)。
- **HR画面・exporter**: term=`used_form`、`selection_phrase`と異なれば併記(`export_form_data_01.py:164-176`)=一般化形と本文根拠の両方を既にユーザーへ見せる構造がある(フォーム変更は不要の見込み。未確認: v3 UIが`selection_phrase`を表示する箇所)。

## 4. Trial 03 N5 確定版 と 現行Production(PROD arm)の工程単位の差分
N5 = `T3/kpg04_methods.py` の `ARMS["N5"] = run_N(gen="g5", ver="v5", check="all", tag="N5")`(chk_model既定=`SOL`)。`run_N` の工程順: `M3.collect` → `M3.select(mode=span)` → `M3.pick(cap=7)` → `generalize5` → `verify5` → `run_check(scope=all)`。`L.RETRY_LOG`をlogに保存。
| 工程 | 現行Production(PROD) | N5(Trial確定版) | 差分・Production側の対応先 |
|---|---|---|---|
| 候補源 | P7 call1(luna、`select_p7`、Gate: 本文一致/CMU/除外/救済)。W5' call2(単語) | `M3.collect`(`T2/kpg03_methods.py:133-153`): **P7保存doc(kind=phrase, origin call1/backfill)のselection_phrase+sentence** ∪ **B1過剰生成**(gpt-6-luna, `prompt_B1(text, n=14)`=`T1/kpg01_methods.py:78-`、max_out 6000、`V.span_in_text`のみで本文一致確認、FRAG除外、span包含dedupe) | B1は**新規LLM call**(約¥0.16/レベル)。B1出力はCMU/救済Gate未通過=Production Gateとの順序要設計。W5'(単語)はN5の対象外(Trial未検証) |
| 塊価値判定 | なし(P7条件3〜5の難易度中心。T1 CURRENT_STATE_01.md:10-12) | **SEL**(luna、`M3.select(mode='span')`、`prompt_S3`+`CHUNK_DEFS_V3`+`EXTRA_RULES_V3`、schema `kp_rank3`、max_out 7000、effort既定)。`keep = keep and cls=='C' and not passive_fragment`。`pick`=keep済みをdifficulty順(advanced→upper→easy、易しいものは**除外せず後ろ**)にsort・span包含/display_form重複除去・cap7 | E1L(ユーザー再判断不要。N5の上流として採用済み扱い。DESIGN 2-2で確認事項化)。SELプロンプトに**WordNet複合語ヒント**(`V.wn_multiword`)が入る=WordNet依存 |
| 一般化 | canonicalization(規則1〜5、luna) | **GEN5**(luna、`generalize5`、max_out 9000): token分類CORE/SLOT_*/DROP+source_sense_ja→arg_notes→headword_frame→frame_change→tokens→gloss_ja。`G.assemble`で決定論組立、`reconcile`(SAME/SLOT_TYPE_OVERRIDDEN/SLOT_INSERTED/FRAME_MISMATCH)、`V.display_check`。SEL理由は**GENへ渡さない**(アンカー除去) | Productionの規則1〜5・QA12・possessor_rolesと**別物**。置換するか前置/後置するかが設計論点 |
| 検証 | canon内QA12(同一call)+決定論validator | **VER5**(gemini-3.8-flash、`think_budget=0`、max_out 6000、`verify5`): verdict OK/FIX/REJECT、meaning_preserved、frame_preserved、argument_type_ok。FIXは`fix_drops_content`(M2)でslot/CORE語を削るものを不採用。`meaning_preserved=false`/`frame_preserved∈FRAME_BAD`/`arg_type_ok=false`(FIXなし)→`revert_to_span`(M1:形をlemma化した本文の形へ、**訳も本文語義へ**。訳が取れず形が変わるなら除外) | 別系列(gemini)=新routing必要 |
| 別系列独立検査 | なし | **CHK5**(gpt-6.1-sol、`effort='low'`、max_out 3500、`run_check(scope='all')`): 全候補を局所文脈(前後1文)のみで検査。relation SAME/MODIFIER_DROPPED_OK→(訳修正あれば採用)、GLOSS_MISMATCH→fix_gloss_ja採用/無ければ本文語義へrevert、SENSE_SHIFT/ARG_TYPE_SHIFT/FRAME_SHIFT→(validator通過+訳あり+slot/CORE語を削らない場合のみfix採用/それ以外はrevert、revert不能なら除外) | N5固有。約¥2.3/レベル(sol)が単価の主因 |
| gloss | P7のja_gloss→ga再整合 | GEN5 gloss_ja→VER5 fix_gloss→CHK5 fix_gloss。revert時は PROD_GLOSS(同一span既存gloss)>VER5.source_sense_ja>GEN5.source_sense_ja>sense_note_ja(`span_gloss`) | ProductionのgaをN5 gloss確定後に走らせるか=設計論点 |
| 決定論flag | なし | `flag_item`/`FLAGS_V1`(hash `3bba7ad2cc6a`)はN5ではlog用(scope=allのため選別に使わない) | 記録のみ。移植は監査用 |
| 出力 | merged item(used_form/key_phrase/QA12/japanese_gloss/...) | `pack`(source_span/display_form/gloss_ja/...) | field対応は§1の表 |
| Gate | CMU/記号/人称(Z)/SRC D1(Z)/Human NG/presentable/Redundancy | **Trial N5には無い**(display_checkのみ) | N5出力を既存`_gate_chain`後段へ通す(新Gate追加ではなく既存Gateの適用) |
| Cap/予算/ledger | 各runnerの`_guard`+cost logger | Trial専用(`kpg04_llm`: `KPG4_CAP`、M10予約、JSON途切れ時max_out×1.6を1回、`KPG4_SALT`) | Production移植対象外(Productionの予算guard・cost loggerを使う)。ただし**JSON途切れ再試行(×1.6を1回)は挙動の一部**=移植要否を設計で明記 |

Opus M1〜M10のうちコード上の反映点: M1=`revert_to_span`/`revert_form`/`span_gloss`、M2=`fix_drops_content`+verify5/run_checkの不採用経路、M3=VER入力から塊理由を除外(`prompt_B4_noreason`、`prompt_V5`)、M9=`_norm_hw`/`reconcile`/`FLAGS_V1`凍結、M10=`kpg04_llm._reserve`(Trial Cap専用)、M4〜M8=probe/評価側(`score_gloss`・`PROBE_BATCH=7`等。Production移植対象外、回帰fixtureの採点にのみ利用)。

### Prompt/設定の実測sha(Trial確定版、本調査で算出。Production移植後の回帰testで固定する値)
`prompt_*`は固定ダミー入力(本文=`[[BODY]]`、候補1件)での全文sha256先頭16桁。
| 要素 | sha256[:16] | 備考 |
|---|---|---|
| B1 prompt(`prompt_B1("[[BODY]]")`) | 97dd3c281a2858f3 | schema e52f403cf3b4760f |
| SEL prompt(`prompt_S3(..., 'span')`、候補`hear it out`) | 2db6e53eb2050bcd | `CHUNK_DEFS_V3+EXTRA_RULES_V3`=01e9e31a9f2eb6d1、schema `kp_rank3`=36612de032fba6b4 |
| GEN5 prompt(`prompt_G5`) | 1838b5151ca06780 | `GEN5_EXTRA`=a4252120a6254001、`GEN2_RULES`=32f51f3552ab3497、schema `kp_gen_tokens5`=e158613928975289 |
| VER5 prompt(`prompt_V5`) | e138983c54987c5d | `VER5_HEAD+VER5_ADD`=1483f97b92a40be9、schema `kp_verify5`=1164d51aa0682719 |
| CHK5 prompt(`prompt_C5`) | 26109d1d85088d65 | `CHK5_RULES`=b10a6edca5ed9737、schema `kp_check5`=c5a05fed55bf59ea |
| FLAGS_V1_HASH | 3bba7ad2cc6a | |
| モデル(requested) | LUNA=gpt-6-luna(B1/SEL/GEN5)、GEM=gemini-3.8-flash(VER5)、SOL=gpt-6.1-sol(CHK5) | `T2/kpg03_methods.py:20`。actual model_idは各stage metaに記録(N5結果JSONで確認: B1/SEL/GEN5=gpt-6-luna、VER5=gemini-3.8-flash、CHK5=gpt-6.1-sol) |
| 呼出パラメータ | B1 max_out6000 / SEL 7000 / GEN5 9000 / VER5 6000(think_budget=0) / CHK5 3500(effort=low) | OpenAI=Responses API json_schema strict(`T1/kpg02_llm.py` call) |

費用(結果JSONのstage meta実測): untidi_a2 N5=B1 0.16+SEL 0.27+GEN5 0.36+VER5 0.80+CHK5 2.30=¥3.88/レベル(jwst_m_b1b ¥3.82、melos_a2 ¥3.42)。Trial報告値の平均¥3.14/レベル・約¥6.28/セット。**既存P7+canon置換による相殺は未確認**(現行canonの1 call費用はTrial台帳に無い)。
Trial N5の**cache replay(API 0)で再現可能**: `KPG4_CAP=0`で `ARMS["N5"]` を untidi_a2 / jwst_m_b1b / melos_a2 に実行→全stageがcache hit(items=7、有料call 0)を本調査で確認。cacheは `T1/kpg01_work/llm_cache/`(688件・3.1MB・**untracked**)。回帰fixtureにはこのraw応答を必要分だけ抽出してコミットする必要がある(DESIGN 4)。

### 原文§4Aの回帰対象のTrial N5記録値(`T3/kpg04_work/results/*__N5.json`)
| 対象 | 記録(span → display_form / check / flags) |
|---|---|
| hear it out | untidi_a2・untidi_b1b: `hear it out`→`hear someone out`、chk=SAME、flags=PERSONIFIED_THING/PERSON_OVERRIDE/PRONOUN_SLOT |
| take points away from | untidi_a2: →`take something away from`、chk=GLOSS_MISMATCH(訳をfix_gloss_jaで修正して採用)。untidi_b1b: `taking points away`→`take points away`(FIX_REJECTED/VER_FLAG、reverted=True=本文の形へ戻し) |
| keep one's eye on | melos_a2: `kept his eyes on them`→`keep one's eye on`、chk=SAME、flags=FRAME_MISMATCH/PRONOUN_SLOT(**境界例**) |
| set a lower limit→set a limit | jwst_m_b1b: chk=MODIFIER_DROPPED_OK、flags=CONTENT_DROPPED(許容) |
| took an unexpected turn→take a turn | jwst_m_a2/b1b: chk=MODIFIER_DROPPED_OK(許容) |
| 日本語訳が旧語義のまま残る防止 | GLOSS_MISMATCH→fix_gloss_ja/本文語義へrevert(`run_check`の経路) |
| 良質候補を失わない | T3 stats(`T3/kpg04_work/stats_*.md`): 確定誤り0/80、境界4件、未見6レベル0/30 |
(日本語訳の本文は結果JSONからfixtureへ取り込む。本書では割愛)

## 5. 旧D/E1L/E4/N2等のProduction参照・検査(Dangling候補)
- Grep(`kpg0[1-4]|E1L|KP-GENERALIZATION-CHUNK|KP-GENERALIZATION-MEANING-PRES`)を `*.py` / `tools/*.py` に実行 → **該当0件**(Production code・toolsに旧Trial参照なし)。
- 該当あり(非Production): `user_test/kp_generalization_trial_02/index.html`・`.../trial_03/index.html`(Trial比較ページ)のみ。公開済みのまま残すか撤去かはDESIGN 6で整理案。
- Production内の「SEL/塊判定」相当: **無し**(P7条件3〜5のみ)。したがってN5採用に伴い削除すべき旧D/E1L検査は現行Productionに存在しない。**整理対象は「N5配線後に不要化しうるProduction既存部」**(置換されるcanonicalization規則・QA12項目の扱い)だが、承認済みGate/spec①の変更に当たりうるためDESIGN 3-3で判断候補化。
- SSOT側の旧記述: `OPEN_ITEMS.md` OPEN-621(Trial 02)・OPEN-623(Trial 03)のStatus/判断待ち表記、`USER_DECISION_REGISTER_01.md` #227/#228。本委任で #228 は解消・OPEN-623 は N5=APPROVED_FOR_PRODUCTION を追記済み。#227(TRIAL-01の採用判断)は未更新=DESIGN 7のSSOT整理案に含める。

## 6. 未確認事項(実装前に確認)
1. 現行canonicalizationの1レベルあたり費用(N5置換時の相殺額)。
2. N5出力をQA12/ga/救済と接続する際、Trial N5の件数・品質(確定誤り0/80)が維持されるか(QA12がN5形を追加で落とす率)。
3. selection form v3 UIが `selection_phrase`(本文根拠)を表示するか(`user_test/selection_form_v3/` の表示箇所)。
4. B1過剰生成候補が既存の本文一致Gate(`ft.validate_and_resolve`)・CMU Gateを通せるか(Trialは`span_in_text`のみ)。
5. gemini-3.8-flashのProduction呼出基盤(既存の`FAMILY_X_RF_GEMINI`=gemini-3.5-flash-lite[`er053_risk_flagger_production_01.py`]と同じSDK経路を使えるか)。
