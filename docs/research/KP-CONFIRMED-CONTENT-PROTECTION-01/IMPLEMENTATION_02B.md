# KP-CONFIRMED-CONTENT-PROTECTION-01 委任_02B 実装記録(IMPLEMENTATION_02B)

状態: IMPLEMENTED + EVIDENCE_COLLECTED(上限)。PRODUCTION_WIRED かどうかはFable判断。実装・testはAPI 0。evidenceは有料(COST_01.md)。
前提: 承認済み追加指示②(確定内容を黙って変えない)・④(確定内容は後工程で変更不可)。DESIGN_02.md(02A)に準拠。

## 1. 実装一覧(file:line は 2026-10-27 時点)

| 項目 | 実装 | 場所 |
|---|---|---|
| M8 STALE再バインド | 出典文(と文法の選定文)が新本文に逐語で残れば、候補doc.text_sha256 → candidates_sha256 → review署名 → レコード を API 0 で連鎖更新(revision+1、履歴 `rebound_text`)。残らなければISSUE(確定内容は不変、`confirmed_content_issue.json`)。照合は NFKC・曲線引用符→直線・空白正規化(大文字小文字は保持) | `er128_kp_confirmed_content_01.py` `stale_or_rebind`(:670)、`_norm_ws`(:634付近)。呼出=`er119_kp_human_review_01.py:1371` `ensure_kp_review`(REBOUND=候補/review再読込、ISSUE=PENDING `confirmed_content_issue`) |
| G2/G3 | `verify_outputs`: G2=TTS recordの英語=used_form、Std日本語=`japanese_gloss_tts` または `convert(japanese_gloss)`(`text`が無ければ`canonical_text`)。G3=Std: 表示用glossが公開ページ(`gloss_page_paths`/`page_paths`/同dir `index.html`)に出ること、Adv: Part 1が描画されているときPart 1行(`meaning_in_text_ja`)と描画。actor=autoのgloss差はWARNのみ。違反はG1と同じ2例外 | `er128:742` `verify_outputs`。呼出=`er119_kp_human_review_01.py:1229` `verify_selection_matches_outputs`(AND追加) |
| G4 + M6 Part 2凍結 | 確定レコードのある文法は `confirmed_grammar.json`(sidecar。`kp_dir_rel`)+ `confirmed_grammar_frozen.json`(`frozen:<sha16>`。出所=`stepB_generated_frozen` または `form_displayed`)。`require_fresh_part2` は extract/explain/ref_ja signature の代わりに frozen sha と 逐語span+candidate_id で判定。`--regenerate-stage part2_cand_b1b`・再抽出・別候補選定は `guard_grammar` で拒否(revoke必須)。`ref_ja` は新poolが記録の`translation_ja`(解説全文の【日本語訳】)と異なる場合のみISSUE。G4=Part 2結果が確定した文法・解説全文・日本語訳と一致 | `er128:862-979`(`load_frozen_grammar`/`freeze_*`/`verify_part2`:937/`guard_grammar`:964/`pool_ref_ja_issue`:979)、`er120_part2_grammar_production_01.py`(`frozen_sha_of`:1112、`result_from_frozen`:1147、`require_fresh_part2(frozen=)`)、`er120_part2_wiring_01.py`(`_translate_cc`:45、`finalize_stage`:118-131、`require_final`:172-182、`verify_outputs`:195-199)、`er119_grammar_review_01.py`(`ensure_grammar_review`:174付近、`_rebind_grammar_text`:115、`op_decide/op_ng/op_unng`のguard:280/323/352) |
| Z/Y 来歴の据え置き(02B中に発見した不具合の是正) | Z/Yの `part2_cand_b1b` stageの input_sha には抽出signature(model・Prompt)が入るため、確定済み文法でmodelだけ変えても親sha不一致STOPになり、かつ`--regenerate-stage`はrevoke必須で拒否される=解消不能。確定済み文法で候補docの本文shaが現本文と一致する場合に限り、記録済みinput_shaを据え置く(`cand_input_sha`) | `er120_part2_wiring_01.py` `cand_input_sha`、`er026_family_z_fiction_production_runner_01.py:1605-1617`、`er121_family_y_runner_01.py:831-843` |
| M2-b Y/Z Std「日本語の意味」 | 表示は確定した表示用`japanese_gloss`(「～」)。TTS入力(`japanese_gloss_tts`→`canonical_text`)は不変 | `er063_family_z_audio_01.py:2540`、`er121_family_y_audio_01.py:1505` |
| Z `_gloss_person_gate` | 確定項目のmismatchは修復LLMを呼ばずISSUE → `FamilyZKpReviewPending`(reason=`confirmed_content_issue`) | `er026_family_z_fiction_production_runner_01.py:1909`、`er128:998` `person_gate_issue` |
| LR警告 | er020のLR発火後に確定KPとの重なりを `<run>/<lv>/audit/confirmed_kp_lr_overlap.json` へ記録(LRの挙動・採用は不変。`sys.modules.get`で取得=er020はer128をimportしない) | `er020_tts_retry_local_rewrite_01.py:829,837` `_note_confirmed_kp_overlap`、`er128:1027` `lr_overlap`、`:1053` `note_lr_fired`、`:625` `register_active_kp_dir` |
| 単一アクセサ | `part1_items` と `public_study_html` は `er128.load_verified_items(kp_dir, level, which="part1")`/`verify_items_against_record` 経由(G1通過+Part 1入力が確定レコードと一致してから返す) | `er128:1078,1122`、`er119_kp_human_review_01.py:1163`、`er120_part2_wiring_01.py` `public_study_html` |
| actor=evidence | `confirm --from-form --actor evidence`。記録に「EVIDENCE_RUN(ユーザー確定ではない…)」を明記。保護の強度はuserと同じ(`ENFORCING_ACTORS`) | `er128:1163` `cmd_from_form`、CLI `--actor` |

## 2. 契約(単一アクセサ)
- KP/vocab/Part 1行を後工程へ渡す入口は `load_verified_items`/`verify_items_against_record` のみ。レコード無し(旧run)・保護OFF・取消済みは従来どおり(レコード無しはread-onlyのlegacy drift WARN)。
- 例外は2種のみ(G1と共通): INTEGRITY(`ConfirmedContentIntegrityViolation` ⊂ `KpReviewInconsistent`、rc=3相当)、ISSUE(`ConfirmedContentIssue` ⊂ `KpReviewNotConfirmed`、rc=4)。操作ガードは `ConfirmedContentLocked`。
- Part 2(Std/Advとも文法はAdvのみ): `_translate_cc` が INTEGRITY→`Part2Stale`(STOP)、ISSUE→`Part2NotConfirmed`(待機)へ写像。

## 3. 隔離(Production安全性)
- 既定値: `EIGO_KP_CONFIRMED_PROTECTION` は既定ON(承認済み仕様。唯一の読取点=`er128.protection_enabled()`、`=0`のみOFF)。02B追加分も同flagの背後(OFF時は全て従来動作: `grammar_state`=None、`stale_or_rebind`=None、`verify_outputs`=何もしない、`person_gate_issue`=何もしない)。
- A/B/C・共有moduleは er128 をimportしない(isolation test PASS)。lazy import は `rv._cc()` 経由。
- 既存Gate(Redundancy QA・gloss HR・SRC D1・Source Consistency・RESTART_STORM等)は無変更。新検査はAND追加のみ。
- 撤去した規則・testなし(`REMOVAL_RESULT_01.md`)。変更した既存test期待値: 02Aの `test_text_change_with_user_record_stops_before_paid_generation` のみ(本文変更で出典文が残る場合は再バインドになる=承認済みM8の帰結。出典文を変えるfixtureに変更し、ISSUEで停止することを維持)。

## 4. test(API 0)
- 新規 `er128_kp_confirmed_content_02b_test_01.py`: 32 test(M8再バインド・出典文変更ISSUE・引用符正規化・G2/G3・M6凍結/MODEL変更/revoke必須/ref_ja ISSUE・Z来歴据え置き・Z人称ISSUE・M2-b Y/Z表示・LR警告・単一アクセサ・Y stage_kp G1 runtime mock・actor=evidence)。
- 実行結果は `RESULT_PACKET_KCP2B.md` §2。

## 5. 未解決・限界(判断候補は RESULT_PACKET_KCP2B.md §5)
- Yの既存コピーdirでは runner段階(tts_b1b/gate/pages)へ進めない(`style_profile.json`未作成の旧run+Part 1/Part 2無し)。runner経由の改変STOP(rc)はX・Zで実測、Yは関数レベル(G1〜G3、実artifact)+mock runtime testで実測。
- Zの `--regenerate-stage kp_b1b` の実行は、同一runを300秒内に3回起動して RESTART_STORM(copyのSTOP)が自己発動したため未実施(STOPは解除していない)。
