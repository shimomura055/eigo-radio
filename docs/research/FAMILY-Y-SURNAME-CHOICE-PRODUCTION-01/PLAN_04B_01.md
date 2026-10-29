# 04B 手順案(委任_04A調査結果。run_02への適用は未実施。2026-10-29)

原文=`docs/pm/delegation_log/2026-10-29_FAMILY-Y-SURNAME-CHOICE-PRODUCTION-01_USER_02.md`。04Aは調査のみ(run_02無変更・runner無編集)。

## A. V1紹介文の差替え(ユーザー指示の個別是正。一般化方式の採否とは独立)
### A-1 波及(file:line)
- JA紹介文=`text/lead_intro/intros_final.json`→`text/article_assembled.md`→`text/article_ja.md`(`render_y_article`、runner:357)。英語版はJA記事の英訳(runner:405-440 `stage_translate`、translate_b1b入力sha=ja全文sha[:416]、translate_a2=ja+adv英文[同:416])。**再翻訳すると本文(Voice発言)の英語も変わる(LLM非決定)ため不可**=紹介行だけを差替える。
- 本文shaへの束縛(紹介行は`canonical_body`の1段落に結合される: `er121_family_y_structure_01.py:242-247`):
  - `kp_<lv>`入力sha=`sha(canonical_body|KP署名)`(runner:669)、`support_<lv>`=`sha(text)`(runner:495)、`tts_<lv>`=`_tts_input_sha`(runner:1157-1164: 英文全文sha・a2はJA全文sha含む)、`part2_cand/part2_<lv>`=paragraphs(=canonical_body)(runner:884-890,968-985)。
  - 確定内容保護: `kp_candidates.json.text_sha256`・`confirmed_selection.json.article.text_sha256`・文法/ニュアンス確定(`er128_kp_confirmed_content_01.py:581-583 verify_g1`)。
- 来歴の固定: `ensure_stage`(`er062_family_z_writer_01.py:721-`)は『出力ファイルshaが来歴と違う=固定された本文が変更された』でSTOP、親sha不一致でSTOP。**手でtranslate/*.mdを書換えると全段STOP**。`rebind_confirmation_input`(:696)は『署名だけ変化・本文不変』にしか使えない。
- 既存の承認済み機構でカバーされる部分: **確定KP/文法/ニュアンスの本文再バインドは既存**(`er128_kp_confirmed_content_01.py:780 stale_or_rebind`: 確定itemの出典文が新本文に逐語で存在すれば候補doc.text_sha256→candidates_sha256→review署名→確定レコードをAPI 0で連鎖更新=REBOUND。呼出=`er119_kp_human_review_01.py:1667`)。V1紹介行は確定KP/Part 1/文法の出典文に使われていない(Grep済み)ためREBOUND可能。
- **既存機構でカバーされない部分(要新規)**: 「承認済みの紹介行差替えに伴う text/translate_*/support_*/kp_*/tts_*/part2_* の来歴(provenance.json)再バインド」(本文の手動パッチ用の仕組みはYに無い。`--reuse-manifest`のintros_fileを差替えて再実行する案は、`text`stageを`--regenerate-stage`で再実行→子孫stale→`translate`のLLM再翻訳を招くため不採用)。`--reuse-manifest`(y_reuse_v1)はJA記事のintros再束縛まで(JA側のみ)で、Std/Adv英語の再束縛はできない。部分regen(`--regenerate-stage tts_<lv>`)は音声clipの再生成だけ。
### A-2 推奨手順(Y専用・API 0の使い捨てtool `apply_intro_patch_surname_choice_01`、先行例=`docs/research/HR-SELECTION-FLOW-QA-FIRST-AND-REDUNDANCY-NONBLOCKING-01/tools/apply_user_decision_surname_choice_01.py`の様式。run_02固定・V1固定・任意文字列拒否)
1. 前提: 並行Workerの`pages,page_verify`/End User page配線の完了を待つ(同一run_02、Cap・lock競合回避)。`tools/stop_scope_check_01.py`でSTOP確認。
2. tool(--dry-runあり): 対象`text/lead_intro/intros_final.json`の`voice_1`、`text/article_ja.md`/`article_assembled.md`、`translate/b1b.md`・`translate/a2.md`の**V1紹介行のみ**を差替え。検証=旧→新で差分がV1紹介行の1行だけ(他の全行byte一致)、Production `check_intro`・補助Gate(`run_leadintro_gate`、luna1回≒¥0.1)、`ys.check_y_article(lang='ja'/'en')`、新EN紹介行が既存の契約(AI告知なし・IOLなし[Std:`ys.y_no_iol_must_fix`])を満たす。
3. 来歴の再バインド(同toolまたは追加関数): `text`(output sha)・`translate_b1b/translate_a2`(input/output sha)・`support_b1b/a2`(input sha=`sha(text)`)・`tts_b1b/a2`(`_tts_input_sha`再計算)・`part2_cand_*/part2_*`(paragraphs)の`input_sha256`/`output_sha256`を、**期待する旧値と一致する場合のみ**新値へ付け替え、`entry['rebinds']`に履歴(理由・user_ref・旧/新sha・api_calls=0)を残す(`rebind_confirmation_input`と同形式)。子孫をstale化しない。
4. `--stage kp`(同じ引数)を再実行: `stale_or_rebind`でKP/文法/ニュアンス確定をREBOUND(API 0)。`kp_b1b/kp_a2`の入力shaはtool側で新(text|署名)へ再バインド。Part 1(KP等)は入力=KP集合でありtext非依存→再生成なし。
5. TTS: `--stages tts_b1b,tts_a2,gate,assemble,pages,page_verify` を**1起動**(OPEN-480)。`_generate_or_reuse`は`canonical_text`一致のOK clipを再利用するため、**新規生成は`y_intro_1`のAdv/Std 2 clipのみ**(`--only-segments y_intro_1`で明示可。`er121_family_y_audio_01.py:99 _ONLY_OK_RE`にy_intro_[1-3]あり)。StdはTTS→6%減速→減速後ASR。V2・V3紹介行・全Voice本文・KP・Comment等は再利用(API 0)。
6. 検証: 全segmentのcanonical_text・wav shaが差替えclip以外で不変(byte一致)、tts_generation_results、Review Lock、style_actual_vs_approved、pagesのV1紹介行、End User page再生成(別Workerの配線に従う)、本文(Voice発言・Lead・Closing)の不変Grep。
### A-3 費用見込み
- TTS 2 clip(Adv≒¥1、Std≒¥1.5。ASR・減速後ASR含む、最悪¥2/clip=runner:38 TTS_CLIP_EST_JPY)≒¥2.5〜4 + 補助Gate≒¥0.1。**合計≈¥3〜5**。
- 設計に新規コード(来歴再バインドtool)を含むため、CLAUDE.md Opus独立レビューGate条件A(新しい構造・処理フローの設計)に該当 → 実装前にOpus独立レビュー推奨(Fable判断)。

## B. `taking offense` → `take offense`(Adv KP rank1。a2に該当KPなし)
### B-1 事実確認
- 本文の綴りは**offense**(米式)。出現: `translate/b1b.md`「…accepted my decision without taking offense」(1箇所、前置詞`without`+動名詞=文法上必須の形)。**本文は維持**。a2本文には`offense`が無く、Std KPにも無い(変更はAdvのみ)。
- KP確定: `key_phrases/b1b/confirmed_selection.json`(live、form_submission、user_ref=…USER_HR_01.md)、candidate_id=`p_85cbe0223d`(selection_phrase/used_form/display_phrase/key_phrase=`taking offense`、source_span=`taking offense`)。
- **原因(重要な発見)**: canonicalization LLMは最初`take offense`を提案していた(`keywords_canonicalized.json` item1 `rescue.canonicalization.llm_key_phrase`)が、`kc.validate_canonicalization_item`(`er003_key_words_canonicalization.py:575-`)が拒否→REVERT_SURFACEで`taking offense`へ戻された。拒否理由=原形化は`er105_kp_fulltext_selector_01.py:696-701 _guard_ok`が『動詞の直後が限定詞/代名詞/不変化詞/前置詞』のときだけ許し、`take`+裸の名詞目的語(`offense`)は対象外(`take offense<-taking offense`=False、`make decisions<-making decisions`=False、`take off<-taking off`=True。04Aで実測)。意図的な保守設計(`heated debate->heat debate`拒否等)のため、規則の拡張は承認済み仕様の変更(区分2)=触らない。
### B-2 最小手順案(先行例=a2 `old-fashioned about it`→`old-fashioned`の`apply_user_decision_surname_choice_01.py`[requalify→confirm、attestation=user_instruction_transcription])
1. `er128_kp_confirmed_content_01.py revoke --run <run_02> --level b1b --by <名> --user-ref <USER_02 §5> --reason …`(確定の取消。ユーザー指示に基づく操作)。
2. 新tool `apply_user_decision_surname_choice_02`(b1b固定・旧`taking offense`→新`take offense`固定・任意文字列拒否): 候補`p_85cbe0223d`のitemを差替え(`key_phrase`/`used_form`=`take offense`、`display_phrase`/`source_span`=`taking offense`のまま、`normalization_reason=lemma_normalization`、`changed_from_display_phrase=true`)。先行toolのゲートを再適用(CMU辞書・記号検出・word_count・`ft._recompute_item_fields`・gloss整合[`force_gloss_realign`]・QA12項目再判定[luna]・候補全体Redundancy QA・`presentation_blockers`)。**例外は1点のみ**: `validate_canonicalization_item`の動詞+裸名詞の原形化guardを、ユーザーの明示承認(原文§5)を根拠に当該1句に限り免除し、免除をitemと確定レコードに記録(`user_approved_exception`)。一般規則の受理面は広げない。
3. 再確定: 旧readableのpayloadでrank1のみ新句に差替え→`confirm`と同じ内部関数で確定(その他の選定[KP2・3、Part 1、文法、ニュアンス]は維持)。
4. 成果物の再生成(Adv b1bのみ): `keywords_canonicalized`再出力→`kp_b1b`来歴(署名変更のみ=`rebind_confirmation_input`)、`kp_expl_b1b`(英語解説、入力phrase変化で`--regenerate-stage kp_expl_b1b`、LLM≒¥0.3)、`kp_part1_b1b`/`kp_part1_ja_b1b`(Part 1行の`english_expression`=take offense。引用文は不変。≒¥0.5〜1)、TTS: `kp1_en`・`kp1_explanation`の2 clip(`kp1_japanese_meaning`=gloss`気を悪くする`は不変・再利用)、gate/assemble/pages/page_verify。
5. 本文の綴り・Highlight: ハイライトは`source_span`(`taking offense`)で解決される(`er_learning_highlight_01.py:261`)ため本文の該当語はそのまま強調。見出し(KP表示)・説明・音声は`take offense`に整合。**本文`without taking offense`は不変**。
### B-3 影響・費用
- 影響範囲=Adv KP rank1の表示/音声/解説/Part 1行のみ。KP2・3、Std全体、全Voice本文は不変。Regression=確定レコード以外のKP/文法/ニュアンス確定のsha不変、TTS再利用clip byte一致。
- 費用≈ QA再判定・Redundancy QA ¥1 + 解説 ¥0.3 + Part 1 ¥1 + TTS 2 clip ¥3〜4 ≈ **¥5〜7**。A(¥3〜5)と合わせ **04B総額≈¥8〜12**(1起動のTTS段にまとめる)。
- 備考: 04Bでは単一の`--stages kp,tts_b1b,tts_a2,gate,assemble,pages,page_verify`起動にまとめられる(KP確定tool実行→来歴再バインド→1起動)。

## C. runner Cap(170円)
- `er121_family_y_runner_01.py:32 APPROVED_BUDGET_MAX_JPY = 170.0` は**定数**(CLI引数ではない)。`E2EBudget.__init__`(:127-128)が`approved_jpy > 定数`を`YBudgetStop`、:1661 mock ctxも同定数を使用。`--approved-budget-jpy`は定数以下のみ受理。
- 200円への引上げ手順(04Bで実施する場合。runner編集は04Aでは禁止): (1)`:32`を`200.0`、コメントへ『委任_04A 7-7自律範囲、Fable判断』を追記 (2)`er121_family_y_runner_text_wiring_test_01.py:33-37 test_cap_is_170_and_above_is_refused`を200/200.01へ更新(関数名・docstring[:3]も) (3)`BUDGET_PLAN_03.md §1`へ追記 (4)実行は`--approved-budget-jpy 200 --ack-warn-threshold`。
- **ただしrun_02のcost_log実績は¥48.75**(`er121_output/.../run_02/cost_log.jsonl`、compute_cost_jpy_so_far)で、04Bの総額≈¥8〜12を足しても約¥60(warn閾値100円未満)。**04BのためのCap引上げは不要**(別目的で再実行が増える場合のみ)。

---
# Opus反映(M1〜M8)と04B実装・リハーサル結果(委任_04B、2026-10-29。run_02本体は無書込・runner/Production module編集0)

実装(新規のみ): `tools/apply_v1_intro_patch_01.py`(A。紹介行差替え+来歴)/`tools/apply_user_decision_surname_choice_02.py`(B。take offense)/`tools/test_apply_surname_choice_tools_01.py`(unit test 36件、API 0)。
リハーサルはrun_02を`scratchpad/rr*`へ複製(複製のRUN_LOCK.jsonは本体のPID 804の写しのため削除。STOP確認は複製に対し`stop_scope_check_01.py`でrc=0)して実施した。

## M1〜M8の反映(file:line。tools/配下)
- M1 `apply_v1_intro_patch_01.py:101-102` DECLARED_CHANGED/DECLARED_STALE、`:467 rewrite_provenance`。tts_b1b/tts_a2は付替えず`downstream_stale`へ(リハーサルで`gate`/`assemble`=`FAMILY_Y_STAGE_NOT_FRESH`でSTOP、`tts_b1b`=`stale(親の再生成後)`でSTOPを実測)。
- M2 `:309 oracle`(runnerの`R._sha`/`ys.canonical_body`/`g.cand_stage_input_sha`/`g.final_stage_input_sha`/`p2w.cand_marker`で再計算)、`:344 plan_provenance`(旧値が記録値と一致することを確認)、`:337 check_declared`(変わるentry集合==宣言集合でなければSTOP)。text段の入力shaは紹介文に依存しない(theme package+reuse manifestのみ。runner:358)ため`text`はoutput shaのみ付替え。
- M3 `:378 kp_precheck`(読取のみで確定item6件・文法・ニュアンス引用の逐語残存を新本文で検査)→main内`cc.stale_or_rebind`(REBOUND)→新署名取得→期待旧値`sha(旧text|旧sig)`一致時のみ付替え→`kp_<lv>_result.json`の署名・sha検査(`kp_result_json_check`)→runnerの`stage_kp`(API 0)でG1を通し、確定物(keywords_canonicalized/vocab_confirmed/final)がsha系を除き退避版と内容一致(`finals_equal_ignoring_sha`=6件すべてequal)。`kp_<lv>_result.json`自体は凍結出力のため旧署名を埋め込んだまま(entryの入力shaと署名のみ新値)。
- M4 `:67 TARGETS`(5ファイルの旧file sha・行番号・旧行/新行・行数)、`:171 build_patched`、`:211 check_article_invariants`(split_y_articleでtitle/lead/全voice body/V2・V3紹介/closing不変、supportに父親/father無し、Std KP3文がa2に逐語残存)。
- M5 `:454 _event`(tool_id・USER_02のpath+file sha・§2・旧/新行とsha・`output_origin=human_patched_line`・旧LLM response_idが新出力を生成していない旨・api_calls=0)。適用済み再実行は`NO_OP_ALREADY_APPLIED`(リハーサルで確認)、別variantで適用済みなら拒否。
- M6 `:414 backup_run`/`:435 restore_run`/`:139 _write_atomic`(一時ファイル+os.replace)。provenanceはfile変更・KP REBOUND・part2 marker書換えの後(検証のstage_kp前)に1回のatomic書込。失敗時は領域ごと全復元(fixed2の失敗リハーサル後、baselineとの差分0ファイルを実測)。先に複製でAPI 0工程を通した。
- M7 `:241 check_new_lines`: 固定ENをtranslate段と同じ`ys.check_y_article(en)`(b1b/a2とも ok)+Std決定論検査`std_gen.run_checks`(checks_failed=[]、numbers_missing/added=[])、JA固定行は`check_intro`(theme spec。ok、34字)+Trial補助Gate(luna)PASS記録(`er121_output/family_y_intro_trial_01/surname/v1_gate_result.json`REC)を参照(本toolで再実行しない=API 0)。
- M8 `apply_user_decision_surname_choice_02.py:123 deterministic_gates`: 免除はtool内の閉じた定数ペア(p_85cbe0223d, `taking offense`→`take offense`)のRule7不合格だけ(他の理由があれば拒否)。免除は候補item(`requalified.exemption`)・確定レコードorigin.transcription・rescueメタ(`rescue.user_instruction`)に記録。Production側に汎用免除の参照は足していない(Production module編集0)。他の全ゲート(CMU・記号・Human NG・gloss再整合[ALIGN_PASS]・QA 12項目全PASS・候補全体Redundancy QA・presentation_blockers)は再適用して合格。順序はA→B(revoke→requalify→confirm→再生成)。

### M8 grep(used_form/key_phrase/display_phraseを『本文に含まれる』前提で使う処理)
- ハイライト解決: `er_learning_highlight_01.py:263-264,278`は`source_span`(=本文表層`taking offense`)と`source_sentence_id`で特定。`used_form`は表示用のみ(:253,333)。→ B適用後も`_resolve_highlights_or_stop`が通る(リハーサルで実測)。
- Part 1: `er003_kp_source_sentence_ja_01.py:86`は`source_sentence`だけを読む。`er003_kp_general_explanation_01.py:130`はused_form(基本形)を入力。引用文は不変。
- 解説・TTS・ページは設計上`used_form`(基本形)を使う(`er019_family_x_kp_explanation_01.py:145-151 explanation_phrase`、`er019_family_x_audio_production_runner_01.py:1986-1997`、`er121_family_y_audio_01.py:1574-1581`)。本文表層(display_phrase)と異なるのは既存の基本形化(`push prices up`等)と同じ扱い。
- G2/G3: `er128_kp_confirmed_content_01.py:883-886`(TTS英語/復唱==used_form)、`:919`(Part 1行をused_formで引く)。TTS再生成後に`take offense`で一致する見込み(Part 1行のenglish_expressionは`take offense`に更新済みをリハーサルで確認)。G2/G3の最終確認はTTS後の04C(TTS未実行のため)。
- 完全には確認できないもの(04Cで確認): G2(`gate`)のphrase_repeat記録、page_verify G3、ページ見出しの`take offense`表示。通らなければ回避せずSTOP報告。

## リハーサルで判明した事項(設計への影響。tool内に対処を実装済みのものと、Fable判断が要るもの)
1. **[判断候補D] Std V1のEN文数**: 旧a2のV1紹介は3文、M7固定文は2文。a2本文の文番号S<n>が以降すべて1つずれ、a2の候補doc/確定レコード/Part1等の`source_sentence_id`が本文とずれる→`_resolve_highlights_or_stop`が`HL_SENTENCE_MISMATCH`(a2の10件)でSTOP(tts/pages/page_verifyの前提)。M7固定文(`--std-variant fixed2`、既定)はこのGateで安全にSTOPし全復元される(リハーサルで実測)。文数を保つ案`--std-variant split3`=`The first speaker is a man. He took his wife’s last name. He lives with his family at his wife’s parents’ home.  `(3文、行末空白2つ)だとA→B→TTS前提すべて通る(実測)。split3は旧Stdの3文構成と同じ文体・事実(sheet範囲)で、Fable未決定のため既定にしていない。**04Cはsplit3採用(推奨)かfixed2維持(候補docのsentence_id全面再採番=新設計が必要)の決定が前提**。
2. **Part 2(文法)結果の古さ**: 本文変更で`part2_result.json`が『古い』になり`_assert_study_ready`が`FAMILY_Y_PART2_NOT_READY`でSTOP(TTS前提)。A toolが`--regenerate-stage part2_<lv>`相当(再finalizeのみ・LLM 0・再抽出なし)をlevel別に単一regenで順に実行(`part2_refinalize`)。part2_result/confirmed_grammar(_frozen)/mdは、sha系・confirmation_id・`reused_from_previous_run`を除き内容一致を確認。
3. **part2_<lv>の入力shaは本文shaを含み、文法review署名も本文shaを含む**ため、M3の文法REBOUND(`er119_grammar_review_01._rebind_grammar_text`)をA toolが先に実行し、その署名でpart2_<lv>を付替える(runnerのstage_kp内では先に`part2_<lv>`の親sha不一致でSTOPするため)。
4. **kp_<lv>来歴付替えの順序**(B): 内容が変わる確定(used_form変更)では、runnerの`_rebind_kp_on_confirmation`の条件『現在のKP assetsが新しい確定と一致』を満たすため、assets install(`R.install_kp_assets`)を先に行う必要がある(`kp_prepare`)。Aは内容不変(署名のみ変化)なので従来どおり。
5. **部分再生成(B。ユーザー原文§5『他のKey Phrase・学習項目は変更しない』)**: runnerの`kp_expl_b1b`/`kp_part1_b1b`再生成は全itemを作り直す。実測でKP2/KP3の英語解説文とPart 1の全5行の文言が変わった(例: `trying to control someone or something`→`trying to keep something or someone`)。これはKP2/KP3の解説音声の作り直しと『他の項目の変更』を招く。toolに`PartialRegen`(`:387`。変わったrank=1だけLLM生成し、他は前回の承認済み出力を保持。runnerの`_ensure`・来歴・stale化はそのまま。audit.partial_regenerationに記録。Production module編集0)を実装。結果: kp_explanations rank2・3 identical、Part 1 rows 2-5 identical、rank1のみ更新。KP1英語解説文は旧と同一(LLMが同じ文を返した)ため`kp1_explanation`のwavは再利用できる。**これは新しい処理構造(部分再生成shim)のためOpus条件A該当の可能性=Fable判断**。
6. **`--only-segments`のsegment ID**: 許可は`kp<n>_english|explanation|japanese_meaning`(`er121_family_y_audio_01.py:102`)。Fable決定のM1文面の`kp1_en`は不可、正しくは`kp1_english`。
7. **pagesステージはTTSのstaleを確認しない**: `gate`/`assemble`/`tts_*`は`downstream_stale`でSTOPするが、`pages`単独は実行できてしまう(`page_verify`が`G3HL_BODY_CHANGED`でSTOP)。04Cは必ず`tts_a2,gate,assemble,pages,page_verify`を1起動で(OPEN-480)。並行Workerのpages実行がA適用後に走らないよう、A適用はRUN_LOCK無し確認後(toolは`st.acquire_run_lock`を取得)。
8. **リハーサル中に直した実装欠陥(Bで5回、Aで複数回の失敗→いずれも全復元。LLM費用はB失敗分も発生)**: rescue候補のQA/gloss記録(presentation_blockers: 救済メタを本toolの再判定結果で更新)/kp_b1b付替え順序(上記4)/cost_logは追記のみで復元対象外(費用記録を消さない)/Aのpart2・sentence_id・auditファイル。
9. **再生成が必要なsegmentの特定(読取専用 `tts_regeneration_plan`)**: baseline=なし → A適用後={b1b:[y_intro_1], a2:[y_intro_1]} → A+B適用後={b1b:[kp1_english, y_intro_1], a2:[y_intro_1]}。kp2・kp3・kp1_explanation・他の全segmentはcanonical_text一致でwav再利用(TTS 3 clipのみ)。

## 04C手順(run_02本体へ適用。すべてFable/ユーザー判断後。費用≈¥5〜7、Cap: run_02実績¥48.75+≈¥7=約¥56で170内)
前提: (a) 上記1のStd V1 EN文数の決定(split3推奨)。(b) 並行WorkerがEnd Userページ配線のrun_02使用を終えている(`er121_output/family_y_production_01/surname_choice/run_02/RUN_LOCK.json`が無い/PID死亡)。(c) `.venv\Scripts\python.exe tools/stop_scope_check_01.py --managed-id FAMILY-Y-SURNAME-CHOICE-PRODUCTION-01 --run-dir er121_output/family_y_production_01/surname_choice/run_02 --out <json>`がrc=0。(d) 5の部分再生成shimのFable判断。
```
set PYTHONUTF8=1
# A: 紹介行差替え+来歴(API 0)。dry-run -> apply
.venv\Scripts\python.exe docs\research\FAMILY-Y-SURNAME-CHOICE-PRODUCTION-01\tools\apply_v1_intro_patch_01.py --dry-run --std-variant split3
.venv\Scripts\python.exe docs\research\FAMILY-Y-SURNAME-CHOICE-PRODUCTION-01\tools\apply_v1_intro_patch_01.py --by <名> --std-variant split3 --report <json>
# B: take offense(LLM実績≈¥1.2。revoke -> requalify -> confirm -> 部分再生成)。dry-run -> apply
.venv\Scripts\python.exe docs\research\FAMILY-Y-SURNAME-CHOICE-PRODUCTION-01\tools\apply_user_decision_surname_choice_02.py dry-run --by <名>
.venv\Scripts\python.exe docs\research\FAMILY-Y-SURNAME-CHOICE-PRODUCTION-01\tools\apply_user_decision_surname_choice_02.py apply --by <名> --budget-jpy 9 --report <json>
# TTS 起動1(Adv。M1(1)。kp1_explanationは文が同一のため再利用=--only-segmentsに含めても生成0)
.venv\Scripts\python.exe er121_family_y_runner_01.py --mode real --slug surname_choice --run run_02 --theme-package docs/research/FAMILY-Y-SURNAME-CHOICE-PRODUCTION-01/theme_packages/surname_choice_package_01.json --reuse-manifest er121_output/family_y_production_01/surname_choice/run_01/reuse_r0/reuse_manifest.json --approved-budget-jpy 170 --ack-warn-threshold --stages tts_b1b --regenerate-stage tts_b1b --only-segments y_intro_1,kp1_english,kp1_explanation
# TTS 起動2(Std -> 完成段。M1(2))
.venv\Scripts\python.exe er121_family_y_runner_01.py --mode real --slug surname_choice --run run_02 --theme-package docs/research/FAMILY-Y-SURNAME-CHOICE-PRODUCTION-01/theme_packages/surname_choice_package_01.json --reuse-manifest er121_output/family_y_production_01/surname_choice/run_01/reuse_r0/reuse_manifest.json --approved-budget-jpy 170 --ack-warn-threshold --stages tts_a2,gate,assemble,pages,page_verify --regenerate-stage tts_a2 --only-segments y_intro_1
```
(Z完成段の`provision_shell`指定(OPEN-480)はY runnerのSTAGESに存在しない: Yのstageは`seed_check,text,translate,support,kp,tts_b1b,tts_a2,gate,assemble,pages,page_verify`。上記が1起動で完結する。)
04C検査項目: (1) tool report: `result=APPLIED`、`tts_regeneration_plan`=A後{b1b:[y_intro_1],a2:[y_intro_1]}・B後はb1bに`kp1_english`が加わる (2) 全segmentの`canonical_text`==現本文/KP確定、差替えsegment(b1b: y_intro_1, kp1_english / a2: y_intro_1)以外の**wav sha一致**(退避前後比較) (3) `gate`(Y style gate+Std減速確認+G2: TTS英語・phrase_repeat==used_form)・`assemble`(Audio Validation)通過 (4) `page_verify`: G3ハイライト(HL_SENTENCE_MISMATCHなし)、Part 1 rowの`take offense`、ページのV1紹介行(新)、`father/父親`/`taking offense`(KP見出し・解説・Part 1行)のGrep0(本文`without taking offense`は残る) (5) 本文(Voice発言・Lead・Closing・V2/V3紹介)のsha不変、KP2・3/Part 1他行/文法の不変(tool report `retained_items_check`・`finals_equal_ignoring_sha`) (6) `final_manifest.json`のstage_entries、cost_log加算(≈¥5〜7)。
撤回: 各toolは失敗時に退避から全復元。成功後に戻す場合は`_backup_<tool>_<日時>`(run_02の親dir)から領域ごと復元(cost_logは追記のみ=戻さない)。
