# TEST_PLAN_01: 確定内容の不変性test計画(KP-CONFIRMED-CONTENT-PROTECTION-01 委任_01、2026-10-27)

方針: 受入=「確定後に英語・日本語訳・区分・解説が不変」。全て決定論・API 0(`er119_test_support_01.py`のfixture流用、新規test: `er119_kp_confirmed_content_test_01.py`)。**不整合な出力を期待値としてassertするtestは書かない**(変更試行はBLOCK/例外を期待値とする)。DESIGN_01の節参照。

| ID | 目的 | 手順(変更試行) | 期待 |
|---|---|---|---|
| T1 | レコード生成(HR CLI経路) | fixtureでselect->finalize | `confirmed_selection.json`が正本+ミラーに生成、`content_sha256`再計算一致、category: kp=1/vocab\kp=2、`actor=user` |
| T2 | レコード生成(フォーム経路) | v2風payload(候補doc由来)を`confirm --from-form` | 各項目の英語・訳が候補doc値と一致、`op_select`の既存検証を通る。訳をpayloadで改変=BLOCK(フォームが古い) |
| T3 | G1: 英語改変 | `keywords_canonicalized.json`の`used_form`を1語変更 | `ConfirmedContentIssue`(INTEGRITY)、`require_final_consistent`がraise、X/Y/Zの入口(関数を直接呼ぶ)でrc=3相当 |
| T4 | G1: 日本語訳改変 | `japanese_gloss`/`japanese_gloss_tts`を別訳へ(IDは同じ) | 同上(現行は素通り=R-06の回帰test。現行コードでは失敗することを先に確認) |
| T5 | G1: assets copy乖離(Y/Z) | 正は不変、assetsのglossだけ変更 | BLOCK(R-07) |
| T6 | G1: ミラー不一致 | audit側レコードのsha改変 | BLOCK |
| T7 | G2/G3: 出力 | TTS結果の`japanese_meaning.canonical_text`・Part 1 `meaning_in_text_ja`・ページHTMLのJAを改変 | BLOCK(JA欠落/相違) |
| T8 | R-01: 人称整合 | レコードありitemに人称不整合glossを注入して`_gloss_person_gate`相当を実行(モックfactory、呼出回数を計測) | **修復呼出0回・artifact不変**、`CONFIRMED_CONTENT_ISSUE`+proposal。レコードなし(旧run)は従来どおり修復される(回帰) |
| T9 | R-03: STALE | 本文を変更して`ensure_kp_review`(生成関数のモックで呼出回数計測) | (a)確定表現が新本文で全て逐語一致=生成関数呼出0、レコード再バインド(`revision+1`、`content_sha256`不変)(b)1表現が不一致=BLOCK+proposal、確定値不変 |
| T10 | R-04: reselect | レコードあり状態で`op_reselect`(`--revoke-confirmation`なし) | 拒否。付けると履歴に`revoked`、runnerからは呼べない(runnerのreselect呼出をGrepで0) |
| T11 | resume | 確定後に候補doc/reviewを読み戻すresume(保存候補のsha一致/不一致) | 一致=API 0・内容不変。候補shaがレコードの`origin.candidates_sha256`と異なる=BLOCK(旧docの黙った採用なし) |
| T12 | `--regenerate-stage kp_*` | Y/Zの`ensure_stage(regenerate=True)`経路で確定済みreviewあり | 候補生成関数呼出0、確定物の`content_sha256`不変 |
| T13 | R-09/10: Part 2 | レコードに`grammar[]`あり。(a)STEPB prompt sha/MODEL定数をpatch (b)Part 1訳poolを変更 して`finalize_stage`/`require_fresh_part2` | 解説生成関数(モック)呼出0、`result.explanation_md`==レコード全文。(b)は再生成ではなく`CONFIRMED_CONTENT_ISSUE` |
| T14 | R-17: Redundancy QA差戻し | 確定集合がQA NGになるモック | 既存挙動(PENDING差戻し)を維持、旧確定が`history`に保存、依頼書に旧確定+NGペア。AIによる自動差替えなし |
| T15 | R-16: AUTO | `declare-absent`経路でQA NG繰上げ | 従来どおり繰上げ(UNREVIEWEDは再確認不要)。レコードは`actor=auto_declared`で繰上げ後の値に整合 |
| T16 | R-12/13: 救済・補完は確定後に呼ばれない | 確定後にresume/regenerate-stage/G1を通し、er125/backfill関数をspyで計測 | 呼出0回 |
| T17 | R-22: LR | `resolve_narrative_role("kp1_en")`等がLR非対象(None/KEY_PHRASE)であること、LR採用の`audio_text_deviation`と確定KP出現位置が重なる合成caseで`lr_overlaps_confirmed`警告が記録されBLOCKしないこと | 非対象維持、警告記録 |
| T18 | R-25/26/27: unconsumed | ③を含む/Stdで②を含む/文法2件のpayload | `unconsumed[]`に保存、取込時に明示、黙って捨てない。KP slot数・Adv vocab<=5は既存検証を維持 |
| T19 | restore/revise | T3/T4の違反後 `confirm-restore` / `confirm-revise --by` | restore=レコード値でartifact再書込、`history`にrestored。revise=ユーザー指定値で`revision+1`、`content_sha256`更新、旧値が`history`に残る。`--by`なしは拒否 |
| T20 | flag既定ON/Isolation | (i)env未設定でGateが有効 (ii)`EIGO_KP_CONFIRMED_PROTECTION=0`で従来出力とバイト同一+WARN (iii)`er119_isolation_test_01.py`に新moduleを追加し、A/B/Cからimportされない (iv)`sc.run_key_phrases`のsha固定test維持 | PASS |
| T21 | 旧run互換 | review/レコード無しの旧runを各consumerで処理 | 従来どおり(何もしない)、API 0、出力不変(golden比較) |
| T22 | 既存test回帰 | `er119_kp_human_review_01_test_01`・`er119_kp_human_review_cli_01_test_01`・`er119_kp_human_review_outputs_test_01`・`er119_x_wiring_test_01`・`er119_z_wiring_test_01`・`er120_part2_*test`・`er119_isolation_test_01`・`er020_*test`・`er011_human_review_lock_01_test_01` | 全PASS(撤去・変更したtestがあれば識別子を報告) |

撤去/残置: 現行でIDのみを比較している検査(`require_final_consistent`のcandidate_id集合)は**残置**(新検査を追加するのみ)。旧ルールの撤去は想定しない(Grep: 撤去対象0)。
