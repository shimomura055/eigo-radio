# TEST_TRIAGE_01 — 既存テスト8件の失敗原因確定(SELECTION-UI-OCCURRENCE-COUNT-01 委任_03、2026-10-31)

ユーザー指示(2026-10-31 §2①)「変更前との比較で原因を確定。今回の変更が原因なら修正、固定値が古いだけなら現行承認仕様と整合させ更新、環境・資材なら是正して再実行」。AI API 0円。

## 方法(ベースライン比較)
- 変更前 = commit `3d4d8ef7c`(委任_01の直前。出現回数の変更を含まない)を、**現行と同じsparse構成の別worktree**(`wt_cnt_base`)に展開し、同一testを実行。現行 = `origin/main` + 本委任の修正。
- 結果: 現行sparse環境で失敗した8件は、**変更前(3d4d8ef7c)でも同じ失敗集合**(基本的に同一の失敗点)。今回の出現回数の変更を**唯一の原因とする失敗は0件**。ただし新規追加したsynthetic data `occ_userfive__*`(出現回数の表示確認用、candidate_idが`demo_*`)が候補docと突合するtestに混ざった点だけは「今回変更起因(想定外の混入)」で、除外対象として明示した(下表#1)。
- 環境差の根拠: (a) sparse worktreeに無かった資材(`docs/research/KP-CANDIDATE-PHRASE7-WORD5-TRIAL-02/`・`**/key_phrases/*/kp_candidates.json`・`data/nltk_data/`・`er005_output/cost_baseline_01/`・`er003_output/a2_p1_r3/`)をsparseに追加(いずれもorigin/mainでtracked)。(b) Windowsの`core.autocrlf=true`でdata/参照HTMLがCRLFで展開されsha(LF基準)が不一致 → LFで展開し直して比較(本番・公開Pagesのblobは無変更)。(c) 4つの`run_kp75_ev_01/**/kp_candidates.json`は**git未追跡**だった(メインtreeにだけ存在)→ 元のpathのままgit追跡化(8 file)。

## 8件の分類(`form1_selection_form_v3_test_01.py`)
| # | test | 原因(観測値) | 分類 | 変更前(3d4d8ef7c)でも失敗か | 対応 | 結果 |
|---|---|---|---|---|---|---|
| 1 | test_candidate_id_kind_and_sha_match_source_docs_verbatim | `assertEqual(len(files),10)`: 現行38件/変更前28件(記事追加で固定値10が古い)。さらに(a)jwst・surname_choiceの`candidates_sha256`・kindがsource docと不一致(sourceが書き出し後に更新: jwst=⑭KP表現調整[FAMILY-X-SELECTED-4委任_03]、surname_choice=run_02再生成[FY-SURNAME-CHOICE委任_04D]。フォームは選定時点のsnapshotを正とし、復元はd6/c8で照合する仕様)、(b)`occ_userfive__*`はsyntheticでcandidate_idが`demo_*` | 固定値が古い + 資材ドリフト(仕様上正常) + (b)のみ今回の追加物 | はい(28!=10。ドリフトも同一) | 下限≥10のみ検査・全fileの逐語照合は全件に課す。`SOURCE_DRIFT_STEMS`(jwst/surname)は**「実際にshaが異なること」を逆に固定**して免除(新たな不一致はFAIL)。syntheticは`SYNTHETIC_STEMS`で除外 | PASS |
| 2 | test_form_data_reuses_existing_gloss_and_reason_verbatim | `FileNotFoundError`: `run_kp75_ev_01/**/kp_candidates.json`がgit未追跡(メインtreeにのみ存在) | 環境・資材(未commit) | はい | 8 fileを元のpathのままgit追跡化(commit `d086921fc`)。sparseに`**/key_phrases/*/kp_candidates.json`追加 | PASS |
| 3 | test_kp75_form_data_cap12_kind_cap_and_reason_verbatim | (a)FileNotFound(同上) (b)`assertIn("run_kp75_ev_01", path)`が後続記事(fx4/occ/yo_prod等は別run dir)で偽 (c)surname_choice `old-fashioned about it` のkindドリフト(#1と同根) | 資材 + 固定値が古い | はい | (b)は当初4記事(ai_island/uk_train/redelivery/melos)のみに適用、(c)はドリフト免除(#1)。cap12/7+5/理由逐語/ja_gloss official は全件に適用のまま | PASS |
| 4 | test_monkeys_paw_data_matches_trial02_result | `FileNotFoundError`: `docs/research/KP-CANDIDATE-PHRASE7-WORD5-TRIAL-02/RESULT_02.md`がsparseに無い | 環境(sparse) | はい | sparseに追加(trackedの資材) | PASS |
| 5 | test_no_placeholder_grammar_in_formal_data | (a)`PermissionError`: `data/batches/`(directory)を`open()`していた(SELECTION-UI-BATCH導入[2026-10-30]後のtest想定漏れ。変更前でも同じ)(b)`meta_waddle_world__b1b__prod.json`の**文法解説本文**に「過去完了形」が出る(仮データではなく正式な解説の語。placeholderの判定対象は文法名`title`) | test想定漏れ + 判定対象の取り違え | はい(a) | (a)subdirectoryをskip (b)文法`title`だけを検査 | PASS |
| 6 | test_reference_html_unmodified | 参照HTMLのsha: 作業ツリー`640084a1…`(CRLF展開) vs 期待`13ef9085…`。`git show HEAD:…|sha256`=`13ef9085…`(**blobは無改変**) | 環境(autocrlf) | はい | LFで展開し直して再実行 | PASS |
| 7 | test_er128_restore_module_if_present | `RestoreError d6=5770fd`: nodeが作業ツリーの生バイトでd6、er128がLF正規化でd6。dataがCRLFで展開されていたため不一致(`stat`: 23048B[CRLF] vs 22530B[LF]) | 環境(autocrlf) | LF展開では変更前と同じくPASS | LFで展開 | PASS |
| 8 | test_restore_roundtrip_matches_buildStructured_and_detects_tamper | 復元に**試作proto06**を使用。proto06は「解説末尾`=====`」規則(正式er128の仕様)を持たず、`ai_island_temple__b1b`の文法「what節主語」を拒否。また正式er128のpayloadは`rank`/`rank_label`を保持(現行仕様)でtestが比較から除いていなかった | test古い(試作と正本の乖離) | はい | 復元・改変検出を**正式er128**(`self.ref`)へ。`rank/rank_label`は双方から除外して比較 | PASS |

結果: `form1_selection_form_v3_test_01.py` **22 passed**(変更前の同一環境でも修正前は4 failed[LF展開後]、現行も同じ4件=出現回数が原因の失敗0)。

## 関連の追加確認(「er128 restore test 3 errors」ほか)
- `er128_form_readable_restore_test_01.py` 3 errors(`TestEndToEndRealConfirm`)= `WordNetの資材が見つかりません`(`data/nltk_data/corpora/wordnet.zip`はorigin/mainでtrackedだがsparse外。メインtreeには存在しない)→ **環境**。sparseに`/data/`を追加 → **83 passed, 49 subtests**(変更前も同一83 passed)。
- `er138_wiring_test_01.py`/`er136_nuance_abolition_test_01.py` 24 failed(sparse環境のみ)= `FileNotFoundError er005_output/cost_baseline_01/pricing_snapshot.json`・`er003_output/a2_p1_r3/…`(sparse外)→ **環境**。sparse追加で **58 passed**(変更前も同一)。N5 Trial(他Worker担当)のコードは未編集。
- 回帰(現行): er140 count 64+export 15=`79 passed`、node `selection_form_logic_test_01.js` **ALL PASS 92**、er119_hr_selection_flow/kp_backfill/kp_difficulty/er128_*grammar_v2 は変更前と同一結果。
- 原因未確定の失敗: **なし**。
