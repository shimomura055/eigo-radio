# CURRENT_FLOW_01: 確定内容(英語表現・日本語訳・①②③区分・文法解説)が通る現行フロー(KP-CONFIRMED-CONTENT-PROTECTION-01 委任_01、2026-10-27、read-only・API 0)

照合は全て本日のworking tree(コード無編集)。「HR」は2種類あり混同しない: (A)**KP/文法Human Review**(`er119_*`、内容の選定・確定=本件の保護対象の出所)、(B)**Human Review Lock**(`er011_human_review_lock_01.py`、TTS segmentのcanonical_text sha単位の再生成ロック)。

## 0. 用語と現行のslot対応(①②③ <-> 現行Production)
- フォームv3の区分(`user_test/selection_form_v3/form_logic.js:7,69`): ①Key Phrase(<=3) / ②追加解説(①+②<=5) / ③本文意味表示(①+②+③<=12) / 文法(<=2、独立枠)。出力は`selection{key_phrase[],extra_explanation[],meaning_display[],grammar[]}`(`LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01/DATA_MODEL_01.md:4`)。
- 現行Production slot(`er119_kp_human_review_01.py:63 SLOT_RULES`, `:536 auto_select`, `:476 validate_selection`): `kp`(<=3、KP音声の本体) / `vocab`(Advanced専用、KPを含む<=5、Part 1 "Vocabulary & Expressions"の対象。`:515-523`で`KP ⊂ vocab`、Stdでvocab指定はエラー)。文法=Advanced専用・確定は1件(`er120:50 TOP_N=2`は候補数、`:902 select_from_candidates`)。
- 対応: ①=`kp`、①+②=`vocab`(Adv)、**③=現行Productionに対応slotなし**(Production builderに本文inline表示処理なし、§8)。Standard(a2)の②/③も対応slotなし(vocabはAdvのみ)。文法はフォーム最大2件、Productionは最大1件(`DATA_MODEL_01.md:6`で既出の差)。

## 1. 確定の入口(現行) -> 将来
| 経路 | 場所 | 確定される内容 |
|---|---|---|
| 現行: HR CLI `select` | `er119_kp_human_review_cli_01.py:68` -> `er119_kp_human_review_01.py:601 op_select` | candidate_idの集合のみ(`review.selection={kp:[cid..],vocab:[cid..]}`、`:659`)。**英語表現・日本語訳は候補doc(`kp_candidates.json`)側の値を参照するだけで、確定時点の値を複製保存しない** |
| 現行: 明示宣言AUTO | `ensure_kp_review :1360-1377`(`auto_select`) | 同上(UNREVIEWED_AUTO_ADOPTED。ユーザー確定ではない) |
| 現行: 文法 | `er119_grammar_review_01.py:223 op_decide` / `er120:961 finalize_review_record` | choice(top1/top2/omit..)とcandidate_id。**解説本文は確定後にStep Bで生成**(`er120:1105 generate_explanation`、`er120_part2_wiring_01.py:83 finalize_stage`) |
| 将来: フォーム -> ChatGPT -> Claude -> 取込 | (未実装。並行委任`LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01`) | 英語・日本語訳・区分・文法解説全文・自由コメント(USER_02 ③) |

## 2. KP: 候補生成から確定物まで(X/Y/Z共通核)
1. 単一入口`er119_kp_wiring_01.py:run_kp_with_review` -> `er119_kp_human_review_01.py:1292 ensure_kp_review`。呼出点: X=`er019_family_x_audio_production_runner_01.py:802`、Y=`er121_family_y_runner_01.py:_kp_review_step`(stage_kp:583)、Z=`er026_family_z_fiction_production_runner_01.py:1971 _kp_review_step`(stage_kp:2003)。
2. 候補生成(`er119_kp_candidates_01.py`): call1/call2 -> `_gate_chain:183`(canonicalization・救済H3[er125]・gloss再整合・人称整合`:232`・SRC D1[Z]) -> 候補組立(`:265 flags.gloss_hr_pending`) -> 補完`_run_backfill:456`(KP-GATE-DROP-BACKFILL)。**救済/補完/gloss再整合/人称整合は全てこの候補生成内で、確定前に完了する**(確定後に呼ぶ経路は§4-5の例外のみ)。
3. 確定: `op_select`(REVIEWED)/`auto_select`(UNREVIEWED_AUTO_ADOPTED) -> `finalize_kp:932`が確定集合のRedundancy QA(M-8)を通し、`_final_items:886`で**候補doc由来のitemをコピー**して`keywords_canonicalized.json`(kp)・`vocab_confirmed.json`(Adv)・`kp_selection_final.json`を書く。署名`selection_signature`(`:558`)=sha(text_sha,candidates_sha,selection IDs,NG,status)。**idempotent**: 署名が同じなら本名ファイルは再書込しない(後段のgloss修復を壊さない設計)。
4. 配置: X=`<run>/<lv>/key_phrases/`直接。Y/Z=`<run>/key_phrases/<lv>/`(正)から`install_kp_assets`(Y`:500`、Z`:1485`)が`<run>/<lv>/key_phrases/keywords_canonicalized.json`へ**copy**(下流Gateの参照先)。
5. 消費側の整合検査`require_final_consistent:1044`: status前進可・署名再計算・`keywords_canonicalized.json`/`vocab_confirmed.json`の**candidate_id集合**==selection・NG交差0。呼出: X=`runner:3537`(stage study_text/tts/assemble/player/all)、Y=`_assert_kp_review_consistent:515`、Z=`:1512`(tts/gate/assemble/pages各所)。**item内容(used_form・japanese_gloss・japanese_gloss_tts)は比較しない**(IDの一致のみ)。Y/Zのassets copyもID集合のみ照合(Z`:1527-1535`、Y`:530-536`)。

## 3. 確定後に参照される箇所(英語表現 / 日本語訳)
| 参照点 | 場所 | 使う値 |
|---|---|---|
| KP英語TTS | X`:2112,2125-2136`、`er003_v1_repro01_main_generate.py:713-896`(minimal -> ENGLISH_LOCK各2回、`expected_text=used_form`) | `item.used_form`(固定文。LR対象外、§6) |
| KP日本語意味TTS(Std) | X`:2112 resolve_key_phrase_ja_gloss_tts`(`er003_v1_n3_01_tts_generate.py:581`)、`:2141 display_gloss=item["japanese_gloss"]` | **TTS用`japanese_gloss_tts`(決定論変換済み、欠落時は`japanese_gloss`から導出)**。表示用`japanese_gloss`とは別フィールド |
| Adv KP英語解説(LLM生成) | X`:1670-1692`(`phrases_signature`+`gloss_signature`一致ならreuse、1件でも変われば5件再生成) | `explanation_phrase(item)`・`source_sentence`・`japanese_gloss`(LLM入力) |
| Part 1(Vocabulary & Expressions) | `er003_kp_general_explanation_01.py:364 assemble_part1`、入口は`part1_items:1087`(vocab_confirmed正) | `english_expression=strict_phrase(item)`、`meaning_in_text_ja=item.japanese_gloss`、LLM生成の`explanation_ja`、引用文の日本語訳(別doc) |
| 試聴ページ(Std KP行) | X`:2922-2925`(`EN: used_form<br>JA: japanese_gloss`)、Zは`a63.build_pages`(`stage_pages:2398`) | `used_form`、`japanese_gloss` |
| 出力整合検証 | `verify_selection_matches_outputs:1118` | 比較は**英語のみ**: TTS結果のKP英語text、Part 1の`english_expression`、ページHTMLに`used_form`が部分文字列で存在。**日本語訳・区分・解説は比較しない** |

## 4. 確定後に再実行/再生成され得る工程(retry/fallback/resume/regenerate/救済/補完/再選定/gloss再整合)
1. **resume**: `ensure_kp_review`は保存済み候補+reviewを読み戻し(本文sha一致時)、生成関数を呼ばない(`:1330`条件に該当しない)。確定済みは`finalize_kp`がidempotentで通る。Zの`_load_gloss_hr_resume:1723`は署名一致時のみgloss HR snapshotを復元。
2. **STALE(本文sha変更)**: `ensure_kp_review:1315-1329`が旧candidates/review/確定物を`SUPERSEDED`へ退避し候補を**再生成**。確定内容の引継ぎ検討なし(NGのみ保持)。
3. **再選定**: `op_reselect:677`(Human明示)のみで`RESELECTION_REQUESTED` -> `ensure_kp_review:1330-1347`が新round候補を生成。自動では起きない。
4. **`--regenerate-stage kp_<lv>`**: Yは`ctx.regenerate_stage`、Zは`_regen_for:1283`+`ensure_stage(regenerate=...)`。KP stageのrunner内は`_kp_review_step`(確定済みreviewを再利用、再選定しない)。Z `_kp_legacy_run:1932`は旧run(review無し)のみ再利用。
5. **確定後に走るgloss/文の変更経路**: (a)Z `_gloss_person_gate:1882`(`stage_kp`の`ensure_stage`後)が不定人称なのに具体人称語を含むitemの**`japanese_gloss`を`ga.align_glosses`で再生成し`keywords_canonicalized.json`を上書き**(`:1913-1916`)。(b)`ga.resolve_gloss:1255`(Human手動のgloss確定、artifact上書き)。(c)Z `_src_gate:1781`(SRC D1。`source_reference_contract`の付与、曖昧はSTOP)。(d)`finalize_kp`のAUTO繰上げ(UNREVIEWED限定)。(e)Redundancy QA NG時の`PENDING_REVIEW`差戻し(Human確定は`selection={}`へリセットして再選択要求=黙って別候補へ差替えはしない)。
6. **救済(er125)/補完(KP-GATE-DROP-BACKFILL)/gloss再整合/人称整合**: 全て候補生成内(§2-2)。確定後の再実行経路は、(2)STALE/(3)再選定で候補が再生成される場合のみ。**確定済みitemを再導出する経路は現行に存在しない**が、再生成時に確定済みitemを入力として渡す仕組みもない(候補全体を置換)。
7. **Part 2(文法)**: 候補抽出(Step A'')はKP候補生成と同じ待機点の前(Z`_part2_cand_step:1596`、Y`:823`、X`run_part2_candidates_x:655`)。確定後、`finalize_stage`(`er120_part2_wiring_01.py:83`)が**Step Bで解説を生成**(0/1 call、cached_resultの`explain_signature`一致なら再利用)。`explain_signature`(`er120:1098`)= sha(item, candidate_id, **STEPB_PROMPT_SHA256**, **MODEL**, **ref_ja**)。従って(i)Step Bのprompt/model更新、(ii)Part 1訳pool(`ref_ja`)の変化、のどちらでも次のfinalizeで**解説が再生成され得る**。`require_fresh_part2:1228`は`result.ref_ja != lookup_ref_ja(pool)`(`:1276`)で`Part2Stale`(次の一手=再生成)。
8. **retry/fallback(TTS)**: KP英語は`used_form`固定のminimal -> ENGLISH_LOCK。日本語意味はgloss_tts固定。いずれも**テキストを書き換えない**(音声再生成のみ)。

## 5. Human Review Lock(er011)
- `er011_human_review_lock_01.py`: segment単位・canonical_text sha(`_text_hash:116`)をキーに`check_before_generation:300`/`record_outcome:358`/`approve_regenerate:475`。**canonical_textが変わると『new version』として再生成を許可**(`:333`)=テキストが変われば旧ロックは効かない。つまりKPのtext(`used_form`/`japanese_gloss_tts`)が確定後に変わると、ロックをすり抜けて新テキストで生成が走る。保護はテキストがここへ届く前(上流)で行う必要がある。
- 終端NGはHRQへ(`TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01`、`88b1a5173`)。内容選定のHR(A)とは独立。

## 6. Local Rewrite(LR)
- `er020_tts_retry_local_rewrite_01.py:130 _KEY_PHRASE_PATTERN`、`:144 resolve_narrative_role`、`:756 run_local_rewrite_recovery`。**KP segment(`kp\d+_(en|ja)`)はCS/LRの明示的な非適用**(`:122-130`、ユーザー承認2026-09-26)。LR対象は本文narration(FULL_STORY/COMMENT等)。
- LRは**TTSへ送る文**を書き換える(`resolve_expected_text_after_local_rewrite:835`が"実際に再TTSへ送った文"を返す)。Zでは`audio_text_deviation`(before/after、`er063_family_z_audio_01.py:1228`)に記録。**記事本文(canonical_text/ページのscript)は書き換えない**。KP自体(used_form/gloss)はLRの入力に含まれないが、LR候補生成はKP出現位置を知らない(`er020`内のGrep `key_phrase|kp`は上記patternのみ)。

## 7. 救済(er125)/補完(er119_backfill)
- `er125_kp_rescue_production_01.py`: `rescue_selection_item:290`/`rescue_canonicalization_item:394`/`postprocess_rescue:429`/`finalize_rescued_items:536`は全て`er003_v1_n3_01_scaffold_generate.py:564-565`(canonicalization内)から呼ばれる=候補生成内。確定後の読戻しは`reverify_persisted_rescue:681`(候補docの検証用)のみ。
- 補完: `er119_kp_backfill_01.py`、`_run_backfill:456`=候補生成内。確定済み候補を変更しない(追記のみ)。

## 8. 本文ハイライト・公開ページ
- Production X/Y/Zのページbuilder(X`build_player_html:3022`、Z`a63.build_pages`、Y同系)に**本文inlineのKP下線/ハイライト処理は見当たらない**(`er0*`非test/非trial pyのGrep `highlight|<mark|kp-hl|underline`: KP用は0件、他はTrial/別用途)。KP表示はscript表のKP行(`EN:/JA:`、X`:2922-2925`)、AdvのPart 1ブロック(`study_html`)、Z/Yのindex.html。
- 旧`user_test/unified.html`の`applyKeyPhraseHighlight`(`CURRENT_SPEC.md:2718`、`user_test/unified.html:227`)は`kp_mapping.json`(`docs/pm/tools/phase_d_kp_mapping_regen.py`生成)に依存。**X/Y/Zの現行Productionがこの経路を使うかは未確認**(Production runnerのGrep `unified.html|kp_mapping`該当0件)。フォームの③(本文意味表示)は将来の消費者で、現行にない。
- 既存の出力整合検証: X`:3684`(player.html)、Z`stage_page_verify:2443`(`verify_selection_matches_outputs`+`_verify_part2_outputs:1685`)、Y`:1138`。

## 9. 小結(何が既に保護され、何が穴か)
- 既に固い: 確定物の**ID集合**・署名・本文sha(STALE)・Part 2の`require_fresh_part2`(確定<->候補<->結果<->md<->html)・英語の出力整合。
- 穴(RISK_MAP_01で詳細): (1)内容(日本語訳/gloss_tts/display)がID集合検査から漏れている (2)確定後の`_gloss_person_gate`/`resolve_gloss`が訳を書換え得る (3)STALE/再選定で確定内容が引継がれず消える (4)区分(②/③)の保存先がreviewに無く③は消費者もない (5)文法解説は確定後生成でprompt/model/ref_ja変更により再生成され得る (6)LRはKP出現位置を知らない(本文の話で確定KPそのものではない) (7)フォームの日本語・解説全文が「確定時点の値」として保存されていない。
