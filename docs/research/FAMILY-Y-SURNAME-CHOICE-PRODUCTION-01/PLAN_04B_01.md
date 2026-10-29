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
