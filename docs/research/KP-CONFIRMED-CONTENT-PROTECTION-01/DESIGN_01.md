# DESIGN_01: 確定内容の不変性(Confirmed Content Protection)設計(KP-CONFIRMED-CONTENT-PROTECTION-01 委任_01、2026-10-27、到達上限=DESIGN_READY・Opus条件A対象)

承認根拠(正本): ユーザー追加指示②④ `docs/pm/delegation_log/2026-10-27_LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01_USER_02.md:16-29,37-41`(「選定確定後、AIによる自動書換え・再選定・別訳への置換は禁止」「確定内容に品質上の問題が見つかった場合は、黙って変更せず、修正案を提示して再確認を求める」「既存の品質Gateは維持」)。現行事実は`CURRENT_FLOW_01.md`、変更し得る箇所は`RISK_MAP_01.md`(以下R-nn)。

## 0. 設計の骨子(1段落)
ユーザーが確定した内容を**値として凍結した1つの確定レコード**(`confirmed_selection.json`)にし、それを**唯一の不変入力**とする。確定後の各工程は(1)レコードから読む(再導出・再生成しない)か(2)自分の成果物がレコードと一致することを**fail-closed**で検査する。不一致は2種に分ける: **INTEGRITY_VIOLATION**(成果物がレコードからずれた=パイプライン不具合。AIがレコード値へ復元してよい=ユーザーの確定を守る操作)と、**CONFIRMED_CONTENT_ISSUE**(確定内容そのものに品質上の問題。AIは黙って直さず、修正案を提示してユーザー再確認を求める。確定の更新はユーザー確認済みの`revision`追加のみ)。検査は既存の全consumer入口(`require_final_consistent`、`verify_selection_matches_outputs`、Part 2の`require_fresh_part2`)に**1関数として差し込む**ので、X/Y/Zの配線点は共通核1箇所+薄い呼出3箇所に収まる。

## 1. 保護するフィールドの定義(protected / reference / derived)
| 区分 | 項目 | 扱い |
|---|---|---|
| **protected**(内容shaの対象。変更=違反) | 各KP/Word: `candidate_id`・`category`(1/2/3)・`used_form`・`display_phrase`・`key_phrase`・`japanese_gloss`(表示用訳)・`japanese_gloss_tts`(TTS読み上げ用、`kwc.convert_display_gloss_to_tts_text` er003_key_words_canonicalization.py:251の決定論変換結果)。文法: `candidate_id`・`sentence`・`explanation_md`(解説全文)・`translation_ja` | レコードに値で保存 |
| **reference**(保持するが確定内容と区別。USER_02 ③「AIの選定理由は確認用情報として保持し、確定した英語・日本語訳・解説本文と区別」) | `ai_reason_ja`・`ai_rank`・`flags`・`rescue`情報・`comment`(自由コメント) | レコードにあるが内容shaに**入れない**。変更しても違反ではない |
| **derived**(確定内容から作る派生物。保護対象外だが入力は確定値であることを担保) | Adv KP英語解説(LLM、R-18)・Part 1の`explanation_ja`・引用文日本語訳(R-19)・TTS音声・ページHTML | 入力がレコード値と一致することだけを検査。派生物自体の再生成は許可(signature一致でreuse) |
- `japanese_gloss_tts`はTTS専用の読み変換(KEYPHRASE-DISPLAY-TTS-SEPARATION承認済み)。ユーザーに見せる訳は`japanese_gloss`。レコードは両方を保存し、G1で両方一致を要求(欠落時の導出`resolve_key_phrase_ja_gloss_tts` er003_v1_n3_01_tts_generate.py:581もレコード値と同値であることを検査)。

## 2. 確定レコード(a)
### 2-1. スキーマ `eigo_radio_confirmed_selection_v1`(記事×レベルに1つ)
```
{ "schema": "eigo_radio_confirmed_selection_v1", "revision": 1,
  "article": {"family":"x|y|z","slug":"..","level":"a2|b1b","text_sha256":".."},
  "origin": {"kind":"form_submission|hr_cli|auto_declared",
             "form_schema":"eigo_radio_selection_result_v2(並行委任DATA_MODEL_02で確定。未作成の間はv1+候補doc参照で代替)",
             "form_payload_sha256":"..", "candidates_sha256":"..", "review_selection_signature":".."},
  "confirmed_by": {"actor":"user|auto_declared|pipeline_frozen", "attestation":"form_submit|cli --by <名>|declare-absent", "user_ref":"..", "at":"ISO"},
  "items": [ {"candidate_id":"p_..", "category":1, "slot":"kp|vocab|display_only", "used_form":"..", "display_phrase":"..", "key_phrase":"..",
              "japanese_gloss":"..", "japanese_gloss_tts":"..", "gloss_status":"CANDIDATE_VALUE|HUMAN_RESOLVED",
              "source_sentence_id":"S6", "reference": {"ai_reason_ja":"..", "ai_rank":1}} ],
  "grammar": [ {"candidate_id":"..", "sentence":"..", "para":3, "title":"..", "construct_ja":"..",
                "explanation_md":"..全文..", "translation_ja":"..", "explanation_source":"form_displayed|stepB_generated_frozen"} ],
  "unconsumed": [ {"ref":"candidate_id|grammar_id", "category":3, "reason":"CATEGORY3_NO_CONSUMER|STD_CATEGORY2_NO_SLOT|GRAMMAR_OVER_MAX(2>1)"} ],
  "comment": "..", "content_sha256": "sha(protected fields のみ、正規化JSON)",
  "history": [ {"revision":1,"at":"..","event":"confirmed|revised|restored|revoked","by":"..","reason":"..","prev_content_sha256":".."} ] }
```
- `category`: ①=1(`slot=kp`、現行`selection.kp`)、②=2(`slot=vocab`=Advのvocab\kp)、③=3(`slot=display_only`、**現行Productionの消費者なし**=R-25)。①∪②=現行`vocab`(`KP ⊂ vocab`、`validate_selection:515-523`と整合)。
- `unconsumed[]`: 現行Productionが消費できない選択(③全件、Stdの②/③、文法2件目以降)を**黙って捨てずに**保存し、取込時に「現行Productionで未使用」を明示表示(R-25/26/27)。消費側を新設するかはユーザー判断(判断候補、本設計はブロックしない)。
- `explanation_source`: `form_displayed`=ユーザーが見た解説全文(確定内容、`confirmed_by.actor=user`)/`stepB_generated_frozen`=HR CLI経路でStep B生成後に凍結(ユーザー未閲覧。以後は変更しない=R-09対策のみ。ユーザー再確認要求の対象外)。

### 2-2. 置き場(正本性)
- **正本**: `<kp_dir>/confirmed_selection.json`(X=`<run>/<lv>/key_phrases/`、Y/Z=`<run>/key_phrases/<lv>/`)。理由: 既存の`kp_human_review.json`/`kp_selection_final.json`と同居し、`discover_kp_dirs`(`er119_kp_human_review_01.py:1264`)と全consumer入口(`require_final_consistent(kp_dir,...)`)が追加引数なしで到達できる。
- **ミラー**: `<run>/<lv>/audit/confirmed_selection.json`(委任文の指定位置)。生成時に同時書込、G1で正本とsha一致を要求(片方だけの改変を検出)。Zの文法はb1bレコードの`grammar[]`のみ(Stdは空配列)。
- 不変条件: レコードの`revision`は**ユーザー確認済み操作**(`confirm`/`confirm-revise`/`revoke`、`--by`必須、`er119_kp_human_review_cli_01.py`に追加)だけが増やす。runner/AIは書換不可(runnerから呼べるのは`load`と`verify`のみ)。

### 2-3. 生成経路(g: 現行HR CLI互換を含む)
| 経路 | 生成 | 内容の出所 |
|---|---|---|
| フォーム送信(将来) | `confirm --from-form <payload.json>`: payloadを`validate`(候補doc `candidates_sha256`一致・各termが候補の`used_form`と一致・訳が候補`japanese_gloss`と一致・累積上限)し、内部で`op_select`(既存検証を全て通す: Redundancy/NG/gloss_hr_pending/qa_fail)を呼んでreviewを`REVIEWED`にし、その結果からレコード生成 | 英語・訳=**候補doc値**(フォームの表示値と一致を検証。不一致=フォームが古い=BLOCK)。解説全文=フォーム送信値 |
| 現行HR CLI `select` | `op_select`の末尾(または`finalize_kp`直後)で`confirm_from_review()`が自動生成。category=kp->1、vocab\kp->2、③なし | 候補doc値。`origin.kind=hr_cli`、`actor=user`(REVIEWED)/`auto_declared`(UNREVIEWED_AUTO_ADOPTED) |
| 既存run(レコード無し、review有り) | G1初回通過時に**候補doc+reviewから**遅延生成(artifactからは作らない)し、artifactを突合。ずれていれば即INTEGRITY_VIOLATION | 候補doc |
| 旧run(review無し) | 生成しない。G1は従来どおり何もしない(R-28) | - |
- 現行HR CLI(`select`)でもフォーム未使用時に同じ保護が効く(要件(g))。AUTO(`declare-absent`)は`actor=auto_declared`: パイプライン内不変は検査するが、ユーザー確定ではないので`CONFIRMED_CONTENT_ISSUE`の再確認要求は出さず、QA NGの繰上げ(R-16)は従来通り。

## 3. fail-closedな一致検査Gate(b)
すべて例外`ConfirmedContentIssue`(`KpReviewInconsistent`のサブクラス)を送出する。X/Y/Zの既存`except KpReviewInconsistent`(X`:3544`、Y`:515-525`、Z`:1521`ほか)が**そのままSTOP(rc=3)**にするので、runner側の例外処理は変更不要。
| Gate | 位置 | 検査 |
|---|---|---|
| **G0** | `finalize_kp`直後(`er119_kp_human_review_01.py:932`の末尾)と`confirm` | 書いたkp/vocab/final jsonがレコードと一致(items・訳・category集合) |
| **G1** | `require_final_consistent:1044`の末尾に1行追加(=X`:3537`、Y`:515`、Z`:1512`の全消費者入口が自動で通る=TTS/Gate/assemble/pages前) | レコードと(i)`kp_selection_final.json`の署名・selection (ii)`keywords_canonicalized.json`(正)の各item(`used_form/display_phrase/key_phrase/japanese_gloss/japanese_gloss_tts`)(iii)`vocab_confirmed.json`(Adv)(iv)Y/Zのassets copy(`assets_json`引数で渡す、R-07)(v)レコードとミラーのsha一致(vi)`unconsumed`の存在を依頼書に再掲。`source_reference_contract`等のprotected外の付与は許容(R-15) |
| **G2** | `verify_selection_matches_outputs:1118`にJA検査追加 | TTS結果: `english.text/canonical_text==used_form`(既存)+`japanese_meaning.canonical_text==japanese_gloss_tts`・`display_gloss==japanese_gloss`(X`:2136,2141`、Z/Yの同等record)/Part 1 `meaning_in_text_ja==japanese_gloss`(`er003_kp_general_explanation_01.py:394`) |
| **G3** | 同関数のpage検査 | ページHTML(unescape)にStdは`used_form`と`japanese_gloss`の両方(X`:2925`の`EN:/JA:`行)、Advは`used_form`+Part 1行の`meaning_in_text_ja`。文法ブロックは既存`verify_outputs`+`result.explanation_md==record.explanation_md` |
| **G4** | Part 2: `er120_part2_wiring_01.py:83 finalize_stage`と`er120:1228 require_fresh_part2` | レコードに`grammar[]`があれば**Step Bを呼ばずレコードの`explanation_md`/`translation_ja`を結果として採用**(`explain_signature`は`frozen:<record.content_sha256>`、model/prompt/`ref_ja`変更で失効しない)。`ref_ja`不一致は再生成ではなく`CONFIRMED_CONTENT_ISSUE`(Part 1訳との整合の修正案)。選定文が本文の逐語spanであること・candidate_id一致は既存検査を維持 |
- 既存Gate(Redundancy QA、`gloss_hr_pending`、`qa_fail`の`--accept-qa-fail`、SRC D1、gloss未評価STOP、Source Consistency等)は**無変更**。本設計は追加検査のみ。

### 3-1. 2種類の違反と処理
| 種別 | 例 | AIの動作 | 出力 |
|---|---|---|---|
| **INTEGRITY_VIOLATION** | artifactの`japanese_gloss`がレコードと違う(R-01の上書き、手編集、copy漏れ、古いstale) | BLOCK。原因工程を記録。**復元は明示コマンド`confirm-restore`のみ**(レコード値でartifactを再書込。ユーザーの確定を守る操作なので`--by`はAI/運用者可、`history`に`restored`を記録)。自動復元はしない(黙って直さない) | `<kp_dir>/confirmed_content_issue.json`+`.md`(field・confirmed・observed・原因stage・次コマンド) |
| **CONFIRMED_CONTENT_ISSUE** | 確定訳に人称不整合(R-01の検出)、本文変更で確定表現が逐語一致しない(R-03)、確定集合がRedundancy QA NG(R-17)、解説と参考訳の不整合(R-10) | BLOCK。**確定内容は変更しない**。修正案(提案値・根拠・影響範囲)を提示し、ユーザー再確認を依頼 | 同jsonに`proposal[]`。依頼書(`kp_human_review_request.md`/統合`review_request.md`)の先頭に「確定内容の確認依頼」節。再確認=`confirm-revise`(ユーザー確認済み、`revision+1`)。却下=現状維持を再確認(`confirm --keep`) |
- 待機はKP Human Reviewと同じ`KP_REVIEW_PENDING`(rc=4、失敗ではなく待機、有料の後続へ進まない)として扱う案(Opus論点)。INTEGRITY_VIOLATIONはrc=3(STOP)。

## 4. 工程別契約(c)(d)
1. **finalize/Redundancy QA差戻し(R-17)**: 既存挙動(`PENDING_REVIEW`差戻し)は維持。差戻し前に旧確定を`history`へ保存し、依頼書にNGペアと旧確定の併記(修正案提示)。AI自動の差替えはしない(既存挙動と同じ)。
2. **retry/fallback/resume(R-20)**: TTS retry・ENGLISH_LOCKは`used_form`固定、変更なし。resumeは保存候補+reviewの読戻し(API 0)の後にG1。**読み戻した旧候補docと確定の不一致**(候補shaがレコードの`origin.candidates_sha256`と異なる)はINTEGRITY_VIOLATION(旧docを黙って採用しない)。
3. **gloss人称整合の確定後実行(R-01)**: Z `_gloss_person_gate:1882`は、レコードがあるitemでは`select_person_mismatches`の結果を**修復せず**`CONFIRMED_CONTENT_ISSUE`にする(proposalにはalign結果を載せる場合のみ有料1call〜¥0.06、既定は検出理由のみ=費用0)。レコード無し(旧run/AUTO除く)は従来どおり。X/Yに同gateは無い。
4. **`resolve_gloss`/手動gloss(R-02)**: 確定後の訳変更は`confirm-revise --item <cid> --gloss "<新訳>" --by <user>`に一本化(`op_resolve_gloss:803`はPENDINGのみ可のまま、確定後は`ga.resolve_gloss`直接呼出の後にG1がBLOCKして`confirm-revise`を案内)。
5. **STALE/再選定/`--regenerate-stage`(R-03/04)**: `ensure_kp_review:1315`の退避**前**に`protect_on_stale()`を呼ぶ。新本文で確定表現を既存validator(`validate_and_resolve`のverbatim一致、API 0)で再検証し、**全て成立=レコードを新`text_sha256`へ再バインド(`revision+1`、内容sha不変、候補は再生成しない)**/**一部不成立=BLOCK+修正案**(旧候補doc内の同種代替、または該当スロットだけの補完を提案。有料呼出は提案段階では行わない)。`op_reselect`は確定レコードがあると`--revoke-confirmation --reason`を要求(履歴に`revoked`)。`--regenerate-stage kp_<lv>`は確定済みreviewを再利用する現行挙動を維持し、再finalize後にG0。
6. **Part 2(R-09/10/11)**: 確定時点で`explanation_md`を保存(form経路=フォーム表示全文、HR CLI経路=Step B生成直後に凍結)。以後`finalize_stage`はレコードを採用(G4)。prompt/model更新は**新規記事から**効く(既存確定には効かない)。文法の`reselect/reextract`はR-04と同様に明示`revoke`が必要。
7. **LR・本文ハイライト・ページ(e)(R-22/23/24)**: (7a)KP segment(`kp\d+_(en|ja)`)がLR非対象のままであることをtestで固定(`er020:128-130`)。(7b)LRは本文narrationの送信文のみ変更し、書面(canonical_text/ページscript)は不変=KPの確定英語/訳には触れない。LR採用後の`audio_text_deviation`(Z`er063_family_z_audio_01.py:1228`、他は`local_rewrite_recovery`)が確定KPの本文出現位置と重なる場合は**警告記録**(`lr_overlaps_confirmed`、BLOCKしない)=LRの7 Gateは変更しない(Opus論点: LR候補選定に保護spanを追加して重なる候補を落とす強化を入れるか)。(7c)本文ハイライト/③本文意味表示は将来の消費者。入力はレコードのみ、出現位置は既存`kp_mapping`方式(完全一致/mapping_type分類、`CURRENT_SPEC.md:2718-2724`)で決定論に求め、`unresolved`(本文に対応なし)は**BLOCK+修正案**(推測補完しない)。(7d)ページはG3で確定訳が表示されることを検証。
8. **救済・補完(R-12/13/14)**: 確定後に呼ばれない(候補生成内)。確定レコードがある状態で候補生成が走る経路(STALE/revoke後)は、確定済みitemを`excluded`ではなく**`pinned`入力**として`generate_fn`へ渡し、候補listに先頭固定で含める(再導出・置換しない)。実装は`make_generate_fn`に`pinned_items`引数を足す小変更(既定None=従来動作)。

## 5. 既存Gate・A/B/C・flag(f)
- 既存Gate不変: 上記3-末尾。新検査は**AND追加**であり緩和なし(既存のretry/fallback/STOP/HRQ/RESTART_STORM/Gateを迂回・無効化しない)。
- A/B/C不変: 新moduleは`er119_kp_confirmed_content_01.py`。`er119_isolation_test_01.py`の`ALLOWED`(X/Z/Yランナーのみ`er119_`をimport)に追加し、A/B/Cは通らないことを既存isolation testで固定。共有関数`sc.run_key_phrases`は無変更(sha固定test維持)。
- flag: `EIGO_KP_CONFIRMED_PROTECTION`、**既定ON**(承認済み仕様=USER_02 ②、kill switch=`0`のみ・無効化時はstdoutに明示WARN+`confirmed_protection_disabled.json`を残す)。単一読取関数`protection_enabled()`のみが読み、mode/引数/設定dictから迂回不可。起動script・`.env`でOFFへ変える運用はしない。DefaultOnIsolation相当のtest: (i)フラグ未設定でレコードが作られGateが効く (ii)`=0`で従来出力とバイト同一 (iii)A/B/Cのimport 0。OPEN_ITEMS記録は「承認済み・既定ON・Opus条件Aレビュー後に実装」(SSOT編集権は本委任にないため文案のみ)。
- X/Y/Z配線点: 共通核(`er119_kp_human_review_01.py`のG0/G1/G2/G3、`er119_kp_confirmed_content_01.py`新設)+薄い呼出追加: X(`verify_selection_matches_outputs`呼出に既にレコード渡し不要)、Y/Z(`_assert_kp_review_consistent`に`assets_json=`引数1つ)、Z(`_gloss_person_gate`冒頭に1分岐)、Part 2(`er120_part2_wiring_01.finalize_stage`)。ランナー別の追加ロジックは最小。

## 6. 非機能・費用
- G0〜G3は決定論・API 0・読込のみ(JSON数個)。`protect_on_stale`の逐語再検証もAPI 0。有料はproposal生成を明示要求した時のみ(<=¥0.06/件)。X/Y/Z・Std/Advの追加時間はms〜十数ms。
- 失敗終了時の最終成果物: BLOCK時は`confirmed_content_issue.json/.md`と`confirmed_selection.json`(不変)が残り、確定値は守られたまま。部分的に壊れた公開物は作られない(G1がTTS/assemble/pages前)。

## 7. 実装計画(委任_02以降の案、本委任では実装しない)
- 委任_02-A(API 0): `er119_kp_confirmed_content_01.py`(schema・build・verify・issue・restore・revise・protect_on_stale・flag)+G0/G1/CLI+test(§TEST_PLAN T1〜T12)。
- 委任_02-B(API 0): G2/G3/G4(Part 2採用)+`_gloss_person_gate`分岐+`pinned_items`+LR警告記録+X/Y/Z薄い呼出+test。
- 委任_03(Family別evidence): 1記事ずつX/Y/Z、確定レコードを置いて後続工程を実走(§EVIDENCE_PLAN、見積<=¥10/Family)。
- 並行委任(フォーム側)へ依頼する項目: 送信JSONに`candidates_sha256`・各項目の`candidate_id`・`japanese_gloss`・`explanation_md`全文を含める(=DATA_MODEL_02)。取込側は本設計の`confirm --from-form`。
- 順序: Opus条件A -> 委任_02-A/B(直列可、同一ファイル競合のため) -> 委任_03(X/Y/Z並列)。

## 8. 未決・判断候補(本設計はブロックされない)
1. ③(本文意味表示)・Stdの②/③・文法2件目に消費者がない(R-25/26/27)。レコードには保存し`unconsumed`として明示。消費側を作る/件数を拡張するのは**新仕様=ユーザー判断**(フォーム側委任の判断候補と同根)。
2. フォーム確定とHR(KP/文法Human Review)承認の関係: 本設計はフォーム確定->`op_select`相当でreview=`REVIEWED`にする(新たな承認Gateを作らない)。フォーム確定をHR承認と等価とみなすのは既存`op_select`の`--by`(人間操作者)要件の運用解釈であり、**承認の意味付け**はFableが11-7/PM_GOVERNANCEで確認すること。
3. INTEGRITY_VIOLATIONの`confirm-restore`をAI単独で実行してよいか(本設計は「確定値への復元=ユーザー確定を守る操作」として可としたが、Opus論点)。
