# DESIGN_02: 確定内容の不変性(Confirmed Content Protection)設計 改訂版(KP-CONFIRMED-CONTENT-PROTECTION-01 委任_02A、2026-10-27)

DESIGN_01(commit 17385f5f9)にOpus条件Aレビュー(`OPUS_REVIEW_01.md`、M1〜M9全件採用・Fable照合済み)を反映した版。差分は `[M-n]` で印を付ける。承認根拠(正本)=ユーザー追加指示② `docs/pm/delegation_log/2026-10-27_LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01_USER_02.md:16-29,37-41`(確定後のAI自動書換え・再選定・別訳置換の禁止、問題は黙って変更せず修正案提示+再確認、既存Gate維持)。
実装範囲: 第1段(委任_02A)=共通核+G0/G1+操作ガード+CLI+Y/Z stage_kp G1。第2段(委任_02B)=G2〜G4・Part 2凍結(M6)・Y/Zページ表示是正(M2-b)・STALE再バインド(M8)・LR警告記録・Z `_gloss_person_gate`のISSUE化。下表の「段」列を参照。

## 0. M1〜M9 対応表
| ID | 指摘 | 採用内容 | 段 | 実装位置 |
|---|---|---|---|---|
| M1 | Y/Z stage_kpに確定後〜有料派生物生成の間のG1が無い | Y/Z stage_kpの全level install直後・解説LLM前に`_assert_kp_review_consistent(ctx, lv, "stage_kp_post_install")`を1行ずつ追加(Zは`_gloss_person_gate`/`_src_gate`/installの後)。G1へ`assets_json`(assets copy)を渡す | 02A | `er121_family_y_runner_01.py` stage_kp、`er026_family_z_fiction_production_runner_01.py` stage_kp、両`_assert_kp_review_consistent` |
| M2-a | `japanese_gloss_tts`はprotectedにしない | protected=`japanese_gloss`(表示値)のみ。`japanese_gloss_tts`は派生物契約: `artifact.tts == record.derived.japanese_gloss_tts(確定時の値)` または `== convert(record.japanese_gloss)`(現行converter)。converter版を`derived.converter_id`に記録。Yの`canonical_text`はG2(02B)で同契約 | 02A(契約・G1)/02B(G2のTTS record側) | `er128` `_item_diffs`、`converter_id()` |
| M2-b | Y/Z Stdページが「日本語の意味」欄にTTS用textを表示 | Y/Z Stdページ表示を`japanese_gloss`に是正し、G3は表示用glossで検査。承認済み仕様(CURRENT_SPEC:458-469 表示用/TTS用分離)との不一致=バグ是正(Fable判断) | 02B | `er121_family_y_audio_01.py:1504`、`er063_family_z_audio_01.py:2538` |
| M3 | 例外クラスの矛盾(rc=3 vs rc=4) | ISSUE=`ConfirmedContentIssue(KpReviewNotConfirmed)` rc=4(依頼書先頭に『確定内容の確認依頼』節)。INTEGRITY=`ConfirmedContentIntegrityViolation(KpReviewInconsistent)` rc=3。操作拒否=`ConfirmedContentLocked(KpReviewError)`。Zの`_gloss_person_gate`内送出は`FamilyZKpReviewPending`へ写像(02B) | 02A(クラス・既存`except KpReviewNotConfirmed`で自動rc=4)/02B(Z gate分岐) | `er119_kp_human_review_01.py` 例外節 |
| M4 | AI操作者による再選定経路 | live+actor=userのレコードがあれば`op_select`(`--accept-ai`含む)/`op_reselect`/`op_ng`/`op_unng`/`op_resolve_gloss`/`add_declaration`(declare-absent)を拒否し`confirm-revise`/`revoke`を案内。`confirm-revise`/`revoke`は`--user-ref`(存在するファイル)必須。`--by`は認証でないため | 02A | 各op冒頭の`_cc().guard(...)`、`er128.cmd_revise/cmd_revoke` |
| M5 | 改ざん耐性の錨 | (a)フォームpayload原文を`confirmed_selection_source/rev<N>_payload.json`に逐語保存+G1でsha検証 (b)G1で「レコード保護フィールド==候補doc値」を毎回検証(正本=候補doc+review、レコード=確認行為の上乗せ情報) (c)historyをhash chain化(`prev_entry_sha256`/`entry_sha256`)。`user_note_sha256`でコメント改変検出。正規化はsort_keysのみ(Unicode正規化なし)。`kind`保存・照合。文法は`<study_dir>/confirmed_grammar.json`へ分離し`confirmation_id`で束ねる | 02A | `er128` `_problems_self`/`_cand_diffs`/`_form_source_problems`/`_grammar_problems` |
| M6 | Part 2凍結はStep Bだけでは不足(extract_signature/MODEL) | 確定レコードのある文法は`require_fresh_part2`をextract/explain両signatureの代わりに`frozen:<sha>`+選定文の逐語span+candidate_id一致で判定。`--regenerate-stage part2_cand_b1b`/reextractはrevoke必須。`ref_ja`不一致は「poolの値がレコード`translation_ja`と異なる場合のみISSUE」。`translation_ja`は`explanation_full`の【日本語訳】節から決定論抽出 | 02B | `er120_part2_grammar_production_01.py`、`er120_part2_wiring_01.py` |
| M7 | 旧run互換: G1での遅延生成を採用しない | 検証関数は書込みしない(診断ファイルのみ)。機能有効化前に確定した旧runは**read-only検証**でずれをWARN+`confirmed_content_legacy_drift.json`。保護下に置くのは`confirm --adopt-existing`(差分提示→`--apply`)。G0も、成果物が既に現行のidempotent再実行ではレコードを作らない | 02A | `er128` `_legacy_drift`/`on_finalize_pre_write`/`cmd_from_review(adopt_existing)` |
| M8 | STALE再バインドの基準と対象 | 基準=各確定itemの`source_sentence`(と文法の選定文・段落)が新本文に逐語存在。再バインド対象=レコード+候補docの`text_sha256`→`candidates_sha256`→review署名→再finalize(API 0)の連鎖。分岐は`ensure_kp_review`の退避処理より前。満たさなければISSUE。02Aでは**有料の候補再生成・確定物退避より前に止めるprecheck(ISSUE待機)**のみ実装し、自動再バインドは02B | 02A(precheck)/02B(再バインド) | `er119_kp_human_review_01.py ensure_kp_review`先頭、`er128.stale_issue` |
| M9 | pinned_itemsは到達経路が無い | **削除**(実装しない。必要になれば別設計)。`er119_kp_candidates_01.py`は触らない(7+5との競合なし) | - | - |

## 1. 保護区分
| 区分 | 項目 | 扱い |
|---|---|---|
| protected(content_sha256対象) | 各item: `candidate_id`・`kind`(phrase/word)・`category`(1/2/3)・`slot`(kp/vocab/display_only)・`used_form`・`display_phrase`・`key_phrase`・`japanese_gloss`(ユーザーが見て確定した表示値。フォームの`ja_gloss`と逐語一致) | レコードに値で保存。変更=INTEGRITY(actor=user)。actor=autoは英語・区分のみBLOCK、gloss差はWARN(既存の人称整合repair等の正当な事後修復を妨げない) |
| derived(契約つき) | `japanese_gloss_tts`(=決定論変換`kwc.convert_display_gloss_to_tts_text(japanese_gloss)`)、Yの`canonical_text`、Adv解説、Part 1の`explanation_ja`・引用訳、TTS音声、ページHTML | `convert(record.gloss)`または確定時記録値と一致する限り許容。別訳への置換はBLOCK。converter版(`derived.converter_id`)を記録。境界=(1)文字列を入力とする決定論的な読み変換 (2)音声(TTS)入力にだけ使用 (3)表示面に出さない |
| reference | `ai_reason_ja`・`ai_rank` | sha対象外 |
| ユーザー記述 | `comment` | `user_note_sha256`で改変検出(パイプラインは消費しない) |

## 2. 確定レコード `eigo_radio_confirmed_selection_v1`
```
{ schema, revision, state: live|reconfirm_required|revoked,
  confirmation_id: "cf_<payload sha16>"(フォーム) | "cr_<content sha16>",
  article{family,slug,level,text_sha256},
  origin{kind: form_submission|hr_cli|auto_declared|adopt_existing, form_schema, form_schema_version, form_payload_sha256, source_revision,
         candidates_sha256, review_selection_signature, user_ref},
  confirmed_by{actor: user|auto, attestation, by, user_ref, at},
  items[{candidate_id, kind, category, slot, used_form, display_phrase, key_phrase, japanese_gloss, gloss_status, source_sentence_id,
         derived{japanese_gloss_tts, converter_id, matches_converter}, reference{ai_reason_ja, ai_rank}}],
  unconsumed[{candidate_id, kind, category, used_form, japanese_gloss, reason: CATEGORY3_NO_CONSUMER|STD_CATEGORY2_NO_SLOT}],
  grammar{path_rel, sidecar_sha256, count, explanation_source[]}(任意),
  comment, user_note_sha256, content_sha256, record_sha256,
  history[{revision, at, event, by, reason, user_ref, content_sha256, prev_entry_sha256, entry_sha256, extra?}] }
```
- 区分: ①=category1/slot=kp(`selection.kp`)、②=category2/slot=vocab(Adv `vocab\kp`)、③=category3(現行に消費者なし→`unconsumed`で保存し黙って捨てない)。件数上限は`SLOT_RULES`・`validate_selection`(`op_select`経由)から読む(定数決め打ちなし。7+5対応)。
- **正本**: `<kp_dir>/confirmed_selection.json`(X=`<run>/<lv>/key_phrases/`、Y/Z=`<run>/key_phrases/<lv>/`)。**ミラー**: `<run>/<lv>/audit/confirmed_selection.json`(全文一致をG1で要求)。**payload原文**: `<kp_dir>/confirmed_selection_source/rev<N>_payload.json`。**文法**: `<study_dir>/confirmed_grammar.json`(`confirmation_id`で束ねる、sidecar sha)。
- 不変条件: レコードの書込みは CLI(`er128` の`confirm`/`confirm-revise`/`revoke`/`restore`)と finalize直前のG0のみ。runnerは`load`/`verify`のみ。ユーザー確定の変更は`--user-ref`付きのCLIだけ。
- 値の出所(M5b): 全て**候補doc**(`kp_candidates.json`、自己sha保護)から取る。フォームの訳は候補docの値と逐語一致を検証(不一致=ISSUE)。`confirm-revise`は候補doc→review候補sha→レコード→確定物を連鎖更新し「レコード==候補doc」の不変条件を保つ。

## 3. 生成経路
| 経路 | 生成 | 備考 |
|---|---|---|
| フォーム送信 | `confirm --from-form <payload.json> --run --level --by --user-ref`: v2 payload(`article.candidates_sha256`必須・各item`candidate_id`/`kind`/`term`/`ja_gloss`/`ja_gloss_status=official`)を候補docと照合→`op_select`(既存検証を全て通す)→レコード+payload原文+(文法)sidecar | termでの対応付けはしない。`ja_gloss_status!=official`・訳/英語の不一致・sha欠落/不一致=`CONFIRMED_CONTENT_ISSUE`(修正案、確定しない)。③/Stdの②は`unconsumed` |
| HR CLI select | `finalize_kp`直前のG0が自動生成(actor=user、REVIEWED)。または`confirm --from-review`で先行生成 | finalize後のRedundancy QA NGで`reconfirm_required`にするにはfinalize前のレコードが要るため、HR CLI経路は`confirm --from-review`を使う(フォーム経路は送信時点で作成済み) |
| AUTO(`declare-absent`) | G0が`actor=auto`で生成 | ユーザー確定ではない。ISSUE再確認の対象外。英語・区分は不変検査 |
| 旧run(機能有効化前に確定) | 作らない(read-only WARN)。`confirm --adopt-existing`で明示 | M7 |

## 4. 検査Gate
- **G0**(`finalize_kp`): 成果物を(再)書込みする場合に限り、書く前にレコードを作成/照合し(`on_finalize_pre_write`)、書いた直後に成果物==レコードを検査(`on_finalize_post_write`)。user確定済みレコードと異なる確定集合のfinalize=INTEGRITY。auto→user/autoの繰上げ・再確認はrevision+1で履歴に残す。
- **G1**(`require_final_consistent`末尾、全消費者入口): (i)レコード自己整合(record_sha・hash chain・content_sha・user_note_sha・ミラー全文一致・payload原文sha・文法sidecar) (ii)`origin.candidates_sha256`/`text_sha256`/`review_selection_signature`==review (iii)確定集合==review.selection (iv)**レコード保護値==候補doc値**(M5b) (v)レコード==成果物(kp/vocab/assets copy)の保護フィールド(英語はactor問わず、glossはactor=userのみBLOCK)+派生物契約。レコード無し=read-only WARN。`state=revoked`は保護なし、`reconfirm_required`はISSUE。単一アクセサ`load_verified_items(kp_dir, level, which)`: 今後の消費者(ハイライト等)はG1を通してから返すこのアクセサだけを使う契約。
- **G2/G3/G4**: 02B(TTS record・Part 1行・ページHTMLの日本語検査、Part 2凍結)。G2の補足(Opus): Master Store再利用TTS recordは`text`等を持たないことがある→`display_gloss`欠落はcanonical_text側で比較し誤BLOCKを避ける。G3のPart 1行検査はPart 1が描画されたときに限定。

## 5. 違反の2分類と例外(M3)
| 種別 | 例外 | rc | 出力 |
|---|---|---|---|
| INTEGRITY_VIOLATION | `ConfirmedContentIntegrityViolation(KpReviewInconsistent)` | 3(STOP) | `confirmed_content_issue.json/.md`(field・確定値・観測値・次の一手) |
| CONFIRMED_CONTENT_ISSUE | `ConfirmedContentIssue(KpReviewNotConfirmed)` | 4(ユーザー待機) | 同`.json/.md`+依頼書`kp_human_review_request.md`先頭に『確定内容の確認依頼』節(`request_notice`)。例: 本文変更(STALE precheck)、フォームの訳不一致/非正式訳、Redundancy QA NG、restore時に人間操作の痕跡 |
| 操作拒否 | `ConfirmedContentLocked(KpReviewError)` | CLI rc=2(REFUSED) | `confirm-revise`/`revoke`を案内 |
- X/Y/Zの既存`except KpReviewNotConfirmed`(X `:3538`、Y `:521`、Z `:1520`)が自動でISSUE=rc=4・INTEGRITY=STOPにする(runner側例外処理は変更不要)。`ensure_kp_review`内のSTALE precheckは`KpReviewPending`相当(`state: PENDING, pending.reason=confirmed_content_issue`)で返し、既存の待機経路(Y/Zのpending一括送出、rc=4)に載せる。

## 6. 操作ガードと変更・復元(M4、O-3)
- 拒否(live+actor=user時): `select`/`--accept-ai`/`reselect`/`ng`/`unng`/`resolve-gloss`/`declare-absent`。actor=auto・`reconfirm_required`・`revoked`・レコード無しでは従来どおり(事後Review=AUTOからuserへの更新を含む)。
- `confirm-revise --gloss <candidate_id>=<新訳> --user-ref --reason`(ユーザー確認済みの訳の修正): 候補docのitem(`japanese_gloss`・`japanese_gloss_tts`=決定論変換・`HUMAN_RESOLVED`)→review候補sha→レコードrevision+1(旧訳を`history.extra`に保存)→確定物を`REVISE_SUPERSEDED`へ退避→API 0で再finalize(final_qa PASS済みなら呼出なし。必要時は次回runner起動に委ねる)。選定集合の変更は`revoke`→再選択。
- `revoke --user-ref --reason`: `state=revoked`(履歴は残る)。以後は通常の選定操作が可能。
- `restore --by --reason`(INTEGRITYの復元。AI単独可): 条件 (i)確定後のreview履歴に人間操作が無い(あればISSUEに格上げ) (ii)復元内容を結果に列挙(完了報告に必須) (iii)候補doc自己sha・`origin.candidates_sha256`一致(不一致=ISSUE) → 確定物を`RESTORE_SUPERSEDED`へ退避→候補docから再finalize。Zは次回runnerで`_src_gate`/install/G1が再実行される。フィールド単位のパッチはしない。
- Redundancy QA NG(finalize時): 既存どおりPENDINGへ戻す。レコードがあれば`reconfirm_required`+history+ISSUE(旧確定を保存、依頼書先頭に節)。AI自動差替えなし。

## 7. 工程別契約(DESIGN_01 §4 の変更点のみ)
- resume/regenerate/retry: DESIGN_01どおり(M8前提)。`--regenerate-stage kp_*`は確定済みreviewを再利用。
- STALE(本文変更): 02A=ユーザー確定済みレコードがあれば**退避・有料再生成の前**にISSUE待機(`stale_issue`)。取消(`revoke`)後は従来のSTALE再生成。02B=基準「確定itemの`source_sentence`・文法の選定文/段落が新本文に逐語存在」で自動再バインド(レコード+候補doc`text_sha256`→`candidates_sha256`→review署名→再finalizeをAPI 0で連鎖。派生物=Z SRC D1・Part 1引用は再計算)、不成立=ISSUE。空白差だけではcanonical化でshaが変わらない可能性があるため、evidenceは「出典文以外の1語変更(再バインド成立)」と「出典文の変更(ISSUE)」の2ケース。
- Z `_gloss_person_gate`(R-01): 02Bでレコード有り(actor=user)なら修復せずISSUE(`FamilyZKpReviewPending`へ写像)。02Aでは修復後のartifactをG1がINTEGRITYで止める(確定値は守られる。レコードは不変、`restore`で復元可)。
- Part 2(M6): 02B。`explanation_full`をレコード(sidecar)に凍結、`frozen:<sha>`判定。
- LR/ハイライト: DESIGN_01 §4-7どおり(LR対象外のKP segmentをtestで固定、LRの保護span追加は承認済みOPEN-540統一仕様の変更になるため不採用、警告記録のみ=02B)。将来のハイライト(③)は`load_verified_items`経由、unresolvedはBLOCK+修正案。
- 救済・補完・gloss再整合・人称整合: 確定後に呼ばれない(Opus確認)。**pinned_itemsは実装しない(M9)**。

## 8. flag・隔離・運用ルール
- `EIGO_KP_CONFIRMED_PROTECTION`、**既定ON**(承認済み仕様USER_02②・④)。唯一の読取点=`er128.protection_enabled()`(`=0`のみOFF)。`er119_kp_human_review_01.py`・X/Y/Z runnerには環境変数読取なし(testで固定)。OFF時はstderr WARN+`confirmed_protection_disabled.json`。**kill switchの運用ルール**: ユーザー指示がある場合のみ、`user_ref`付きで使う。起動script・`.env`でOFFにしない。
- A/B/C: `er128`はcore/CLIからの遅延importのみ。A/B/C・共有module(`sc.run_key_phrases`等)は非接触(isolation testで固定)。
- 既存Gate(Redundancy QA・gloss HR・SRC D1・Source Consistency・RESTART_STORM等)は無変更。新検査はAND追加のみ。

## 9. 費用・失敗終了時の最終成果物
- 02Aは全て決定論・API 0・JPY0。`confirm-revise`/`restore`の再finalizeもAPI 0(Redundancy QAが未実施の場合のみ次回runnerのQA 1 call)。
- 失敗終了時: INTEGRITY/ISSUEとも確定レコード・ミラー・候補doc・review・payload原文は不変のまま残り、`confirmed_content_issue.json/.md`に差分と次の一手が出る。TTS/assemble/pagesの前で止まるため部分的に壊れた公開物は作られない。

## 10. 未決・判断候補(02Aの実装はブロックされない)
1. (a)文法解説の「ユーザー確定」: 現行フォームでは文法解説が全記事「未生成」でStep Bは確定後生成→`explanation_source=stepB_generated_frozen`(ユーザー未閲覧)。見せてから確定させるには提示前にStep B生成(約¥0.3×候補数、工程順変更=新仕様)。**既出UDR-FORM-1と同一**のため新規提示しない。
2. (b)Y/Z Std「日本語の意味」欄の表示(M2-b): CURRENT_SPEC:458-469で「表示用`japanese_gloss`/TTS用`japanese_gloss_tts`、表示用フィールドはTTSへ渡らない」が承認済み→現状は承認済み仕様との不一致=バグ是正(Fable判断、委任_02B)。
3. ③・Stdの②・文法2件目の消費者は無い(`unconsumed`で保存・明示)。消費側新設は新仕様=ユーザー判断(フォーム側委任の判断候補と同根)。

---
## 付録(委任_02B 実装後の確定事項。2026-10-27)

1. **単一アクセサの契約**: KP/vocab/Part 1行を後工程へ渡す入口は `er128.load_verified_items(kp_dir, level=, which="kp"|"part1")` と `verify_items_against_record` のみ。`part1_items`・`public_study_html` はこれを通す(G1通過+Part 1入力と確定レコードの英語/訳の一致を確認してから返す)。レコード無し/保護OFF/取消済み=従来動作。
2. **actor=evidence**: runtime evidence専用。`confirm --from-form --actor evidence` で作り、記録に「EVIDENCE_RUN(ユーザー確定ではない…)」を明記。`ENFORCING_ACTORS=(user, evidence)` により保護の強度はuserと同じ(gloss差もBLOCK。autoのみWARN)。本番のユーザー確定とは区別される。
3. **M6 Part 2凍結の設計**: sidecar `confirmed_grammar.json`(`kp_dir_rel`でKPの確定レコードに結合、sha自己整合)+ `confirmed_grammar_frozen.json`(`frozen:<sha16>`。出所=`stepB_generated_frozen` または `form_displayed`)。凍結がある間、extract/explain/ref_ja signature は判定に使わず frozen sha+逐語span+candidate_id で判定。`--regenerate-stage part2_cand_b1b`・再抽出・別候補選定・NG/UNNGは `guard_grammar` で拒否(revoke必須)。本文変更は選定文が逐語で残れば `_rebind_grammar_text` でAPI 0再バインド、残らなければISSUE(`Part2Stale`)。
4. **M8照合の正規化**: 出典文の逐語照合は NFKC・曲線引用符→直線・空白正規化(大文字小文字は保持)。候補docの`source_sentence`が直線引用符に正規化されるため。
5. **来歴の据え置き(Z/Y)**: `part2_cand_b1b` の input_sha に抽出signature(model)が入るため、確定済み文法でmodelだけ変えると親sha不一致STOP(かつ`--regenerate-stage`はrevoke必須で拒否=解消不能)になる。確定済み文法かつ候補docの本文sha一致の場合に限り記録済みinput_shaを据え置く(`er120_part2_wiring_01.cand_input_sha`)。
6. **ISSUEの扱い(Z `_gloss_person_gate`)**: 確定項目のmismatchは修復LLMを呼ばず `FamilyZKpReviewPending`(reason=`confirmed_content_issue`)。
7. **LR**: 保護spanは追加しない(OPEN-540統一仕様の変更になるため)。重なりは `audit/confirmed_kp_lr_overlap.json` に記録のみ。
