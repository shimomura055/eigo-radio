# CURRENT_PIPELINE_01: 現行KP候補生成パイプライン(3+5)のファイル:行付き一覧
KP-PHRASE7-WORD5-PRODUCTION-01 委任_01 / 2026-10-27 / read-only・API 0・JPY0。照合は本日のworking tree(コード無編集)。

## 0. 結論(設計に効く事実)
1. **X/Y/Z全6経路(Std/Adv)の候補生成はただ1箇所に集約**されている: `er119_kp_wiring_01.py:59 run_kp_with_review` -> `:69 kcand.make_generate_fn`(`er119_kp_candidates_01.py:536`) -> `generate_candidates:276` -> `_generate_candidates_impl:283`。呼出点: X=`er019_family_x_audio_production_runner_01.py:802`、Y=`er121_family_y_runner_01.py:561 _kp_review_step`(wiring呼出:572)、Z=`er026_family_z_fiction_production_runner_01.py:1971 _kp_review_step`(wiring呼出:1992)。委任文の「X=er019:452/Y=er121:562/Z=er026:1974」は行番号が古い(関数名は一致)。7+5の配線点は`_generate_candidates_impl`の1箇所でX/Y/Z/Std/Advに同時に効く(Std/Advの差は`source_level/process`引数[A2_SUPPORT/B1_SUPPORT]とAUTOのvocab規則のみ)。
2. Std/Adv別の生成関数は存在しない。`level`は`wiring:67`で`source_level, process`へ写されるだけ。
3. 候補doc(`kp_candidates.json`)が存在すれば**再生成しない**(resume): `er119_kp_human_review_01.py:1303-1334 ensure_kp_review`(`cands is None or review is None or status==RESELECT`のときだけ`generate_fn`)。

## 1. call1(Prompt 2・3件)
| 項目 | 場所 |
|---|---|
| Prompt 2本文(逐語固定) | `er105_kp_fulltext_selector_01.py:51-65 PROMPT_2_TEXT`、sha `:71 PROMPT_2_SHA256`(`a12896f4…`) |
| 件数定数 | `er105:33 KP_COUNT_MAX=3`, `:34 KP_COUNT_MIN=1`, `:35 KP_WORDS_MAX=5`(語数上限=フレーズ内語数) |
| attempt loop | `er105:456 run_selection_gate`(`:38 MAX_ATTEMPTS=2`)。attempt内で**1件でもitem不適合(validate/CMU/除外句再選択)なら全件を機械診断noteつきで再選定**(`:511-526`)。最終attemptのみ「CMU未登録のみ」「外側retry除外句のみ」が原因のitemを落としてshortfall確定(`er108:244 apply_cmu_to_validation`、`er105:397 apply_exclusions`)。それ以外の不適合が残れば`status=INVALID` |
| 件数検査 | `er105:230-231`(`validate_and_resolve`が`1<=n<=KP_COUNT_MAX(3)`を`reasons`に積み`ok=False`にする) |
| JSON schema | `er105:74-92`(phrase/word_count。**reason_jaなし**) |
| 呼出関数 | `er105:538 run_fulltext_selection` <- `er003_v1_n3_01_scaffold_generate.py:354 _run_key_phrase_selection_fulltext`(telemetry`:358-364`) <- `sc.run_key_phrase_selection(kp_backend="fulltext_p2")`(`_generate_candidates_impl:292 select_fn`既定、`:317`呼出) |
| 出力metadata | `er105:555-581 keywords_runtime_metadata.json`(`attempts_detail[-1].cmu_excluded/exclusion_dropped`を補完計数が読む=`er119_kp_backfill_01.py:56 read_call1_dropped`) |
| reason_ja | call1は返さない(`_generate_candidates_impl:342 reason_ja=""`) |
| 選定段の救済 | `er105:245-267`(H2、`generate_candidates`文脈内のみ有効=`er125.rescue_context`) |

## 2. call2(Prompt 2-V・最大5件)
| 項目 | 場所 |
|---|---|
| Prompt 2-V | `er119_kp_prompt_2v_01.py:21-36`(Prompt 2から冒頭文と条件6だけ置換)、sha `:35 PROMPT_2V_SHA256_PINNED=e1d5349c…`(import時assert) |
| 最大件数 | `:19 SELECTOR_2V_MAX_ITEMS=5` |
| message | `:63 build_user_message`(Prompt+本文+`ALREADY_DELIMITER`+「すでに選ばれた表現」+任意note) |
| schema | `:40-60`(phrase/reason_ja/word_count) |
| 実行・item gate | `er119_kp_candidates_01.py:46 run_vocab_selection`: validate(`:86`)/`duplicate_of_top3`(同一・包含、`:95-96`、比較先=call1の`display_phrase`、`:41 _containment`)/除外指定(`:100`)/CMU(`:104`)/overflow(`:111`)。attemptは最大`ft.MAX_ATTEMPTS`(2)で技術/parse失敗のみ再試行。**内容でattemptを繰り返さない**(item単位dropped) |
| 失敗時 | `status=FAILED` -> `_generate_candidates_impl:332-337`が外側retryへ |

## 3. 候補組立(Gate連鎖)
`_generate_candidates_impl:338-365`: originals=call1全件+call2 kept、`_screen_human_ng:170`、`_gate_chain:183`(canonicalization最大3回[`MAX_CANON_RERUN=2`]・CMU post-canon`:224`・記号`:227`・人称整合[Z]`:232`・SRC D1[Z]`:237`・Human NG`:256`・`kind`付与`:253`・救済旗`er125.annotate_candidate:271`)。`ai_rank`は**call1順->call2順の通し連番**(`:366-368`)。`gate_dropped`(`:369`)。

## 4. 補完(KP-GATE-DROP-BACKFILL、既定ON)
- 配線位置: `:371-382`(ai_rank付番後・Redundancy QA前)。flag: `er119_kp_backfill_01.py:25 backfill_enabled`(`EIGO_KP_BACKFILL`、既定ON)。
- 計数: `count_exclusions:99`(E=dropped stageのうち`overflow`以外、phrase_key重複除去、現存候補と同句は除く。**`duplicate_of_top3`(含有語除外)もEに数える**)。`kind_of_phrase:30`(スペース無し1語=word)。
- **上限定数**: `plan_quota:124`は`cap=rv.KP_CANDIDATE_MAX(8)`からの総room(`candidates:467`)と`BACKFILL_MAX_CALL_ITEMS=5`(`backfill:19`)で`N=min(E, room, 5)`。**種類別上限(フレーズ/単語)は存在しない**(種類別なのは`pick_backfill:132`のE_phrase/E_word quotaのみ)。
- 発動条件: `_run_backfill:464-469` = `E_total>=1 かつ 現存候補>=1 かつ room>=1`。**「初回が上限未満であること」自体は発動条件ではない**(承認原文と一致)。
- 補完Prompt: Prompt 2-Vを再利用し除外noteを後置(`:479-480`)。包含比較先は常にcall1(M-5)。補完は1回・失敗は初回候補で続行(`:529-533`)。
- 外側retry: 補完ON時は`n_auto<3 and gate_dropped`脚を撤去(`:410`)。残るのは候補0件・技術失敗。
- 出力doc: `:425-432`(`prompt_ids/prompt_sha256`={call1,call2}、`shortfall=len(cands)<rv.KP_CANDIDATE_MAX`、`shortfall_detail:438`[cap/missing/E_total/backfilled/unfilled_by_kind]、`backfill`記録)。

## 5. 救済(KP-GATE-EXCLUSION-RESCUE、既定ON)
`er125_kp_rescue_production_01.py`(708行)。`er125.rescue_context`(`candidates:279`)内のみ有効。H1/H2=`er105`選定段、H3=`er003_v1_n3_01_scaffold_generate.py`canonicalization段、H4=`candidates:255,271`(NG照合・旗)。7+5でも**単語にも現行どおり**適用(単語は慣用句辞書・5語以内規則の対象外=救済の対象になりにくい)。

## 6. HR・AUTO・Adv vocab
- 定数: `er119_kp_human_review_01.py:52 KP_CANDIDATE_MAX=8`, `:53 KP_FINAL_MAX=3`, `:54 VOCAB_COUNT_MAX=5`, `:63-65 SLOT_RULES`(kp<=3 / vocab<=5)。
- AUTO: `:536 auto_select`: ai_rank順に`auto_eligible`・非NG・非redundancyを走査、`kp=chosen[:3]`、`vocab=chosen[:5] if level=="b1b"`(`:553-554`)。**KPを含む**先頭5件。
- 依頼書: `:1204 render_request_md`(全候補の表。AI推奨印はAUTO規則の結果。件数に上限文言なし)、`:1189 _backfill_summary_line`。
- 確定: `:932 finalize_kp`(確定集合のRedundancy QA再適用`:963-975`)、`:886 _final_items`(候補docのitemをコピー)。
- `KP_CANDIDATE_MAX`の参照: `candidates:429,443,467,580`のみ(+test 2箇所)。

## 7. 選定フォームv3への受渡し(読み取りのみ。編集は並行Agent)
`docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/tools/export_form_data_01.py`: `:23 kind_of`(doc`kind`優先)、`:137 phrases[:7]/words[:5]`に既に分割(**7/5枠は既にフォーム側仕様**)、`:107-125 shortfall_note_ja`(`sd.get('cap', 8)`の既定8が残る=12への更新が必要)、`:144 overflow`枠。読み取る項目: used_form/japanese_gloss/source_sentence/reason_ja/kind/origin/ai_rank/auto_eligible/human_selectable/flags/rescue要約、doc単位`backfill`/`shortfall`/`shortfall_detail`/`prompt_sha256`/`model_id`。**7+5の候補docはこの契約のまま通る**(追加項目のみ必要)。

## 8. Family差
- X: `src_fn=None, person_repair_fn=None`(`er019:802`)。
- Y: `src_fn=None, person_repair_fn=None`(`er121:572`)。possessor_roles/A-1(OPEN-484)のY実走evidenceは未確認(非blocking、7+5配線とは独立)。
- Z: `src_fn=kcand.make_z_src_fn`(SRC D1)+`person_repair_fn`(`gloss`フラグ有効時、`er026:1985-1990`)。補完でもGate連鎖に同一適用(`candidates:502`、R-5で出力dir分離)。
- 本文: X/Y=各レベルのarticle本文、Z=`canonical_article_text`(`er026:1296 canonical_article_text`)。生成関数は同一。
