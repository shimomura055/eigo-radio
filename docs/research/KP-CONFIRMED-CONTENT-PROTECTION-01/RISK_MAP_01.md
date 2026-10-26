# RISK_MAP_01: 確定後に確定内容が自動変更され得る箇所(KP-CONFIRMED-CONTENT-PROTECTION-01 委任_01、2026-10-27、read-only・API 0)

判定: **変更する**=現行コードで確定後に内容が変わり得る / **条件付き**=ある条件で変わる / **しない**=構造的に変わらない(根拠付き)。「対策」はDESIGN_01の節。保護対象=英語表現(used_form/display_phrase/key_phrase)・日本語訳(japanese_gloss / japanese_gloss_tts)・区分(①②③)・文法(選定文/construct/解説全文/訳)。

| ID | 箇所(ファイル:行) | 事実 | 判定 | 対策 |
|---|---|---|---|---|
| R-01 | Z `_gloss_person_gate` `er026_family_z_fiction_production_runner_01.py:1882-1930`(呼出`:2060`付近 stage_kp内、ensure_stage後) | 不定人称の英語KPに具体人称語のglossがあると、`ga.align_glosses(only_ranks)`で**`japanese_gloss`を再生成し`keywords_canonicalized.json`へ上書き**(`:1913-1916`)。確定署名は変わらず(署名はID集合)ので通過する | **変更する(確定訳を置換)** | DESIGN §4-3: 確定レコードがあるitemは**修復せず**`CONFIRMED_CONTENT_ISSUE`(修正案=align結果を提示のみ)。候補段階では`gloss_hr_pending`旗で確定不能(`er119_kp_candidates_01.py:265`、`validate_selection:518`)なので、通常は到達しない=到達は異常 |
| R-02 | `ga.resolve_gloss` `er003_key_words_gloss_alignment.py:1255`(Human手動、artifact上書き) | 確定後にgloss HRを手動解決すると`keywords_canonicalized.json`のglossが変わる。署名不変 | **条件付き(Human操作)** | §4-4: 上書きを`confirm-revise`(再確認)経由に統一。確定レコードと不一致のまま通れない(G1) |
| R-03 | `ensure_kp_review` STALE `er119_kp_human_review_01.py:1315-1329` | 本文sha変更で確定review・確定物をSUPERSEDEDへ退避し候補を**全再生成**。旧確定内容の再検証・引継ぎなし | **変更する(確定が消え別候補になり得る)** | §4-5: 確定レコードあり -> 新本文で全確定表現を逐語再検証(同じvalidator)。全て成立=引継ぎ(revision+1、内容不変)/一部不成立=BLOCK+修正案(該当表現と旧候補doc内の代替) |
| R-04 | 再選定 `op_reselect:677` + `ensure_kp_review:1330-1347` | Human明示の`reselect`で新round候補が生成、旧確定物を退避 | **条件付き(Human明示のみ。自動では起きない)** | §4-5: `reselect`は確定レコードの失効(revision履歴にevent)を伴う明示操作としてのみ許可。AI/runnerからは呼べないことをtest |
| R-05 | `finalize_kp` `er119_kp_human_review_01.py:932-1019` | 署名が同じなら本名ファイルを書き直さない(idempotent)が、**署名が違えば候補docの値で再生成**。内容(gloss)は署名に入るcandidates_sha経由でのみ間接的に守られる | **条件付き** | §3-b G0: finalize時に確定レコードとitem内容を突合。不一致=BLOCK |
| R-06 | `require_final_consistent:1044-1084`・Y`:515`・Z`:1512` | 検査は**candidate_id集合**のみ。`used_form`/`japanese_gloss`/`japanese_gloss_tts`の改変は素通り | **穴(検出しない)** | §3-b G1: 内容比較(下記フィールド)を追加。全consumer入口に既配線なので**実装は1関数** |
| R-07 | Y/Zの`install_kp_assets`(Y`:500`、Z`:1485`) | 正(`key_phrases/<lv>/`)->assets(`<lv>/key_phrases/`)の**copy**。copy後に片方だけ書換えられても検出できない(ID集合のみ照合) | **穴** | G1で正とassetsの両方を確定レコードと内容比較 |
| R-08 | `verify_selection_matches_outputs:1118-1180` | TTS結果は英語textのみ、Part 1は`english_expression`のみ、ページは`used_form`の部分文字列のみ。**日本語訳・区分は未比較**。TTS日本語意味の`canonical_text`/`display_gloss`(X`:2136,2141`)も未比較 | **穴** | §3-b G2/G3: JA比較を追加(`japanese_meaning.canonical_text == japanese_gloss_tts`、`display_gloss == japanese_gloss`、Part 1 `meaning_in_text_ja == japanese_gloss`、ページJA) |
| R-09 | Part 2 Step B再生成 `er120:1098 explain_signature` / `finalize_part2:1170` / `er120_part2_wiring_01.py:83` | 解説は**確定後に生成**。`explain_signature`にSTEPB prompt sha・MODEL・`ref_ja`が入るため、prompt/model更新やPart 1訳pool変更で次のfinalizeに**解説が再生成**(確定解説全文が変わる) | **変更する(条件: prompt/model更新、Part 1訳変化)** | §4-6: 確定レコードに`explanation_md`全文+`translation_ja`+sha。レコードがあればStep Bを呼ばず**レコードの全文を結果として採用**。再生成が要るならBLOCK+提案 |
| R-10 | `require_fresh_part2:1276` の `ref_ja` 不一致 -> `Part2Stale`(次の一手=再生成) | Part 1訳が変わると文法側が古い扱いになり、再生成を促す | **条件付き** | §4-6: 確定解説がある場合は`ref_ja`不一致を再生成ではなく`CONFIRMED_CONTENT_ISSUE`(整合の修正案提示)に変える |
| R-11 | Part 2 reselect/reextract(`op_decide`、`er119_grammar_review_01.py:223`、MAX_RESELECT=2) | Human明示のみ | 条件付き(Human明示) | R-04と同じ |
| R-12 | 救済(er125) `er125:290,394,429,536` | `scaffold_generate.py:564-565`のcanonicalization内=**候補生成内でのみ呼ばれ、確定後の経路に無い**。`reverify_persisted_rescue:681`は検証のみ | **しない(確定後は再導出しない)**。ただし再生成(R-03/R-04)経由では候補を丸ごと置換 | R-03/R-04の対策で担保。evidence: 確定後にer125の関数が呼ばれないことをmock呼出カウント0で確認 |
| R-13 | 補完(`_run_backfill:456`)・外側retry(`kcand:182-368`) | 候補生成内。外側retry/補完は`ensure_kp_review`が`generate_fn`を呼ぶ場合(初回/RESELECT)だけ | **しない(確定後)** / 再生成経由は R-03/R-04 | 同上 |
| R-14 | gloss再整合(候補段階、`ga.align_glosses`) | 同上。確定後の唯一の再実行はR-01 | R-01に集約 | R-01 |
| R-15 | SRC D1(Z)`_src_gate:1781` `srcz.gate` | `source_reference_contract`を**付与**(英語/glossの文字列は変えない)。曖昧は推測補完せずSTOP | **しない(付与のみ)**。ただしitem書換えが入るのでevidenceで`used_form`/`japanese_gloss`不変を確認 | G1の比較対象は保護フィールドのみ(contract付与は許容) |
| R-16 | `auto_select`のAUTO繰上げ(`finalize_kp:965-985`) | `UNREVIEWED_AUTO_ADOPTED`限定でQA NGの候補を除外して次候補へ | **条件付き(AUTO限定)** | AUTOはユーザー確定ではない。確定レコードは作るが`confirmed_by=auto_declared`(保護は「パイプライン内不変」のみ、ユーザー再確認要求は不要)。ユーザー確定(REVIEWED)にはこの経路は適用されない(`:988-995`で差戻し)ことを維持 |
| R-17 | Redundancy QA NG時の差戻し `finalize_kp:988-995` | Human確定集合がQA NGなら`PENDING_REVIEW`へ戻し`selection={}`、再選択要求 | **しない(黙って変更せず再確認要求)=品質Gate維持の正しい挙動** | §4-1: 差戻しの前に旧確定を`superseded_confirmations[]`へ保存し修正案(NGペア)を依頼書へ提示。既存Gateは無変更 |
| R-18 | Adv KP英語解説(LLM、X`:1670-1692`ほか) | `phrases_signature`+`gloss_signature`一致でreuse、変われば5件再生成。入力はitem(確定)。出力は**派生物**(ユーザーが確定した対象ではない) | 入力が不変なら**しない**(signature一致でreuse) | 保護対象外(派生)。ただし入力(used_form/gloss)が確定値であることをG1で担保 |
| R-19 | Part 1 `explanation_ja`(LLM)・引用文日本語訳(別doc) | 派生物。USER_02 ②の保護対象に含まれない(英語表現・日本語訳[gloss]・区分・文法解説) | しない(入力確定済み) | 保護対象外と明記。ただし判断候補: フォームで見せていない文を「確定内容」と誤認させない |
| R-20 | TTS retry/fallback(minimal -> ENGLISH_LOCK、`repro01_main_generate.py:713-896`) | `used_form`固定でTTS再生成のみ。テキストは書換えない | **しない** | G2でTTS結果のtextを確定と照合(既存+JA追加) |
| R-21 | HR Lock `er011_human_review_lock_01.py:333` | canonical_textが変わると**new version扱い**で再生成可。ロックの番人はテキスト改変を止めない | 間接リスク(R-01/R-06でテキストが変われば新テキストで生成が走る) | G1を**TTS前**に置く(全consumer入口)。ロックのkeyとcanonical_text shaは確定レコードのsha(後述)と同一テキストを指す |
| R-22 | LR `er020:756`・`er063_family_z_audio_01.py:1228` | KP segment(`kp\d+_(en|ja)`)はLR非適用(`er020:128-130`)。LRは本文narrationの**送信文のみ**を書換え、記事本文/ページscriptは不変(`audio_text_deviation`に記録) | **しない(KP自体)**。本文のKP出現位置の読み上げ文は変わり得る(音声のみ、書面は不変) | §4-7: KP segmentがLR非対象のまま(test)+LR後の`audio_text_deviation`と確定KP出現位置の重なりを**警告記録**(blockはOpus論点) |
| R-23 | 本文ハイライト(`unified.html`/`kp_mapping.json`、Production外) | `matched_text`は本文に追従(`CURRENT_SPEC.md:2718-2724`: 一覧の見出し語と本文表記が乖離しても本文優先)。**確定した英語表現を変えず本文一致を探す設計**だが、unresolved(対応不能)の扱いは未規定 | 現行Production X/Y/Zに該当処理なし(§CURRENT_FLOW 8) | §4-7: 将来の消費者はレコードのみを入力にし、本文一致不能=BLOCK+修正案 |
| R-24 | ページ生成(X`_build_level_table:2922-2925`、Z`build_pages`、Part 1ブロック`assemble_part1:394-396`) | テンプレートは`item.used_form`/`item.japanese_gloss`を使用(確定物から) | 入力が確定物なら**しない**。入力が改変されたら素通り(R-06) | G1+G3 |
| R-25 | 区分②/③の保存先 | `review.selection`は`kp`/`vocab`のみ。③は**保存先も消費者もない**。フォームの`meaning_display`を取り込むと現行では黙って捨てられる | **穴(情報欠落)** | §3-a: レコードに`category`(1/2/3)を保存。③は`consumer:none`を明示(捨てずに保持、取込時に「③は現行Productionで未使用」を表示)。判断候補 |
| R-26 | Std(a2)の②/③ | vocabはAdv専用(`validate_selection:515`)。フォームでStdに②を選んでも黙って落ちる | **穴(黙って落ちる)** | §3-a: Stdの②/③は`UNCONSUMED_CATEGORY`としてレコードに保存し取込時に明示(黙って捨てない)。判断候補 |
| R-27 | 文法(フォーム最大2件 vs Production確定1件、`er120:50,902`) | フォーム2件選定を現行は表現できない(`DATA_MODEL_01.md:6`) | **穴(件数不一致)** | §3-a: レコードは配列`grammar[]`だが、現行消費者は1件。2件目は`UNCONSUMED`として保存。判断候補(新仕様: 最大2件化) |
| R-28 | 旧run互換(review/レコード無し) | 旧runはreview無しで従来経路。レコード無し=保護対象なし | **しない(旧run)** | G1はレコード/reviewが無ければ従来通り(legacy compat、`require_final_consistent:1054`と同じ) |

## 要約(変更し得る箇所)
- **現行コードで確定後に内容が変わり得る**: R-01(Z人称整合のgloss上書き)、R-03(STALEで確定消失)、R-09(Part 2解説の再生成)。
- **条件付き(Human明示操作 / 異常系)**: R-02/R-04/R-05/R-10/R-11/R-16/R-21/R-22。
- **検出の穴(変わっても通る)**: R-06/R-07/R-08(内容比較の欠如)、R-25/R-26/R-27(区分・件数の取りこぼし)。
- **構造的に変わらない(根拠あり)**: R-12/R-13/R-14/R-15/R-17/R-18/R-19/R-20/R-24(入力確定時)/R-28。
