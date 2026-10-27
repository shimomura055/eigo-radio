# FORM_RESELECT_01 V3フォーム変更(文法枠の新仕様+確定済みKPロック)

公開URL: https://shimomura055.github.io/eigo-radio/user_test/selection_form_v3/?a=ai_island_temple__a2 (Standard) / `?a=ai_island_temple__b1b` (Advanced)
(記事選択の先頭2枠が AI島 Standard / Advanced)

## 変更(user_test/selection_form_v3/**のみ)
1. 文法枠(全記事共通UI): Top 1・Top 2の最大2件のみ表示(rank順。3位以降は非表示)。ラジオ方式=常に最大1件、「適切な候補なし(0件)」を明示選択、2件同時は構造的に不可(`setGrammar`の2件目は拒否、旧保存状態で2件選択済みなら未決定へリセットしメッセージ表示)。文法名+解説全文(pre-wrapで改行表示)。
2. 新仕様データ(`grammar_spec`有り=AI島)は、文法が**未決定のままでは送信/コピー不可**(旧フォームの0件を新フォームの確定0件として引き継がない。0件は「適切な候補なし」の明示選択が必要)。旧形式データ(grammar_spec無し・文法候補0の他記事)は従来どおり送信可。
3. 確定済み記事モード(`kp_confirmed`有り): KP/KW 10件は区分別に表示のみ(チェック・上限UI非表示、「確定済み」バッジ、正式訳表示)。送信payloadの`selection`は確定10件を逐語でそのまま含め(旧保存状態の選択は無視)、`kp_confirmed.locked=true`を付す。文法だけ選択可。
4. payload追加項目(additive): `limits.grammar=1`/`grammar_presented_max=2`、`selection.grammar[].rank/rank_label`、`grammar_status`(user_selected_one|user_selected_none|pending_reselection)、`grammar_decision{state,presented[],selected_candidate_id}`、`kp_confirmed{}`。
5. データ(`data/ai_island_temple__{a2,b1b}__prod.json`): `kp_confirmed`(10件+payload sha)・`grammar_spec`・`grammar`=Top2のみ。ツール: `tools/apply_new_grammar_spec_aif2.py`(検証: Top2=候補doc top_ids=rank1/2、解説全文=事前生成物と逐語+sha再計算)。

## 旧規則の撤去・残置
撤去: UI `gch>=2`(最大2件)・`文法 n/2`表示・`GRAMMAR_MAX=2`・チェックボックス方式。残置: 旧形式データの`setGrammar`API(チェック方式。上限1に更新)。委任_01の`tools/browser_check_aif1.mjs`は旧仕様(文法2件選択)前提のため**superseded**(後継=`tools/browser_check_aif2.mjs`)。`verify_form_data_aif1.py`の文法id照合はTop2仕様へ更新。
