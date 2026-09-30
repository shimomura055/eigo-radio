# 委任ログ: OPEN-233-SELF-RECOVERY-TRIAL-01 委任_21(2026-10-01)

## 1. 委任内容(要旨)

rep11で判明した3欠陥の是正+微小Trial rep12(広いTrialは含めない)。
Guardrail¥10(実装¥0、rep12≤¥8)。

## 2. rep11で判明した課題(Fable照合)

(1) `bgroup_B3`がJA fail-openガードの誤発火により2/2でSTAGE4へ回った
(KPI後退)。(2) 局所QA fastpathが3委任連続で実call成功0件。(3)
`neg1_meta_b3prod_a2`で新規claim(MUSE-HC-006)のRewriteが未分析のまま
発生。(4) `hormuz_run03_standard`のfresh Stage1がreuse fixtureと異なる
検出結果(recall miss)になる非決定性。

## 3. A-1是正: JAガードの言語判定(¥0)

`bgroup_B3`実データを調査した結果、`source_article_text`(fixture上は
「JA」フィールド)が実際には英語であり、`ja_fail_open_guard`が無条件で
使っていた`split_ja_sentences`(句点。！？のみ)が機能せず全文が1文として
扱われ、些細な1語変更(`so`→`while`)でも「本文の残り全部が消失した」と
いう粗い誤検知を生んでいたことを特定した。`is_predominantly_ja`(新設、
¥0決定論、JA文字比率閾値15%)でJA/非JA判定を行い、分割器(JA=`split_ja_
sentences`/非JA=既存EN分割器`split_sentences_generic`)を切替える是正を
実装した。いずれの分割器でも1文以下にしか分割できない場合は
`indeterminate=True`を返し違反判定をせず(ガード不発火)、呼び出し側は
これを理由に局所QA fastpathを許さず全文Recheckへ倒す(STAGE4直行には
しない)。

## 4. A-2是正: 局所QA locate真因の特定(¥0)

`meta_run03_standard` sample1 cycle1(rep11)の実データを精査し、真因を
特定した: rewrite_hint中の引用断片(`extract_quoted_fragment`)がそもそも
2文にまたがる場合、E1(1語水準)Rewrite後の`after_fragment`(needle)も
2文のまま維持されるが、`find_sentence_context`は`split_sentences_
generic`が返す単一文の要素としか照合しておらず、2文分のneedleはどの
要素とも一致せず`revised_sentence_not_locatable_in_context`で毎回skip
していた。needleを同じ分割器で分割した文数kのウィンドウ照合(exact
containment→SequenceMatcher閾値0.85)を追加した(k=1の既存経路は無変更)。

## 5. A-3: neg1 MUSE-HC-006の分析(コード変更なし)

Ledger fact(`full_ledger.json`のMUSE-HC-006)・claim原文・Stage1/Stage2
判定根拠・floor不該当(既存`disclosure_gap_negative_inference_
downgrade`は否定形専用で本claimの肯定形物語展開には非該当)を確認し、
Hook専用Stage2 rubric(§4-14)のtie-break境界上にある真のdisputed事例と
判定した。section_type/stage2_route=hookでHook専用Stage2の対象内で
あり、対象外だったための誤判定ではない。rubric・floor条件のコード変更は
行わない。

## 6. A-4: Stage1非決定性の記録

`hormuz_run03_standard`のfresh Stage1(rep11)がACCEPTABLE_STAGE1(recall
miss)だったのに対し、reuse fixture(rep9/rep10)は同一記事でBLOCKING
(HF-009検出)だった非決定性を事実として記録。是正はPhase 2課題として
OPEN_ITEMSへ持ち越す。

## 7. unittest(202/202 PASS)

新規6件(`TestJaFailOpenGuardLanguageAware`3件+`TestFindSentenceContext
MultiSentenceNeedle`3件)+既存196件=計202件全PASS(`.venv/Scripts/
python.exe -m unittest er052_open233_self_recovery_flow_runner_01_
test_01`、regressionなし)。いずれもrep11実データ(`bgroup_B3`・
`meta_run03_standard`)を逐語fixtureとして使用。

## 8. rep12実測(限定4 instance×n=2、¥1.7384/Guardrail¥8内)

`OUT_DIR_REP12`・`BUDGET_STATE_PATH`(`budget_state_c233y_21.json`)を
rep12専用へ明示設定、`TOTAL_BUDGET_JPY=8.0`。CLI:
`--groups=b_group,meta,negative --instance_ids=bgroup_B3,bgroup_B1,
meta_run03_standard,neg1_meta_b3prod_a2 --n_runs=2`(`hormuz_run02_
standard`は`build_target_instances`に存在しないため、reuse Stage1・
ラダー①〜③候補の代替として`bgroup_B1`を選定)。**8/8 instance-run
完走・API error 0件・false PASS 0/8**(rep11に続き2回連続)。

- `bgroup_B3`: `ja_fail_open_guard`は2/2とも`ok=true`(誤検知0件、A-1
  是正確認)。ただし2/2ともSTAGE4_ESCALATIONへ到達しており、これは別の
  既存・正当な条件((g)`short_section_no_window`[section_type=
  in_one_line]+(h)`ja_en_equivalence_not_pass`[verdict=REVIEW_
  REQUIRED])によるfail-closedであることを確認した(誤検知は解消したが
  人間確認は別理由で残存、false PASSではない)。
- `meta_run03_standard`: 局所QA fastpathが2/2とも実際にAPI call成功
  (`local_qa_fastpath_success: true`)、全文Recheckを省略した(Trial
  全体[委任_09〜_21、rep7〜rep12]を通じて初めての実call成功実例、
  local_qa 1 call¥0.0356 vs 同runのstage1_recheck平均¥0.0646/call)。
- `neg1_meta_b3prod_a2`: 2/2とも`RESOLVED_STAGE2_DOWNGRADE`(Rewrite
  不要)。rep11(2/2 BLOCKING)と結果が入れ替わり、A-3のdisputed判定を
  実測面から裏付けた。
- `bgroup_B1`: 2/2とも`RESOLVED_STAGE2_DOWNGRADE`(Rewrite不要)。

設計書§4-17(§4-19指定だが実採番§4-16の次として§4-17、既存前例踏襲)・
§6-7(A-1追記)・§6-10(A-2新設)を追加。REPORT§21を追加(§0対応表/
§21-1〜§21-4是正内容/§21-5 rep12実測/§21-6コスト/§21-7 Gate 9項目/
§21-8 STOP条件・Status)。DECISION_LOG・OPEN_ITEMS・ACTIVE_TASK更新。

## 9. Gate 9項目充足表(rep11からの変化)

充足5/部分3/未充足0(rep11後)→**充足6/部分3/未充足0**(rep12後)。
項目1(局所QA基本形)・項目8(全文Check削減)が新たに改善。詳細
REPORT§21-7。

## 10. 費用

実装A-1/A-2: ¥0(追加API callなし)。rep12: **¥1.7384**(8
instance-run、Guardrail¥8内)。本委任合計: **¥1.7384**。Phase累計
(前回まで¥338.5278)+本委任¥1.7384=**¥340.2662**。Phase残額
(**上限¥500**のうち)=**¥159.7338**。

## 11. STOP条件・USER_DECISION_REQUIRED該当確認

¥10超え見込み(該当せず、¥1.7384)/API error 3連続(該当せず、0
error)/Production・既存証跡変更(該当せず、`git diff --stat`で確認)/
USER_DECISION_REQUIRED6条件(該当せず、neg1 disputed判定・rubric
tie-break文言明確化・Stage1非決定性は判断材料として提示)/開始前
チェック未反映(0件)/最小修正1回後もFAIL(該当なし、rep12は1回で
8/8完走)/Safety-critical 10claim・Safety 12がBLOCKINGでなくなった
(該当せず)/false PASS 1件以上(**該当せず、0/8**)。

## 12. Status

`A1_A2_FIXED_A3_ANALYZED_REP12_8_OF_8_COMPLETE_FALSE_PASS_ZERO_
LOCAL_QA_FIRST_SUCCESS`(rep11で判明した3欠陥のうちA-1・A-2をコード
修正、A-3をコード変更なしで分析完了。rep12実行で局所QA fastpathの
実call成功を初めて実測し全文Recheck省略を確認。false PASS 0/8
[rep11から2回連続]。29 instance全量の広いTrial着手はFable/ユーザー
判断待ち)。
