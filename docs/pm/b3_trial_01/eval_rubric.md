# eval_rubric (OPEN-233-B3-BRIEF-STRUCTURE-TRIAL-01)

MATRIX-01 rubric(`docs/pm/note_transfer_matrix_01/eval_rubric.md`)を継承。判定基準(重大/軽微・工程・退行・★3分類・ID共有・保留)は変更なし。変更点は1節(条件)、★fact対象(4節)、ID形式(5節)、参照パス(7節)、追加9節(brief品質記録)のみ。

評価基準は直前監査(OPEN-233-E2E-STAGEWISE-NG-AUDIT-01、`er052_output/open233_allfact_note_e2e_02/eval/stagewise/STAGEWISE_SUMMARY.md` §0)と同一。変更なし。

## 1. 条件
評価者には条件(variant)を開示しない(匿名コード、`blinding.md`)。条件定義・期待順位は評価者が読まない。テーマ meta/hormuz/space_weapons ごとに24匿名記事(計72)。Checkerなし(ENのb1bが最終)。

## 2. 重大/軽微の定義(監査と同一文言)
- 重大NG: 事実の意味が変わり読者に誤った理解を与える(主体・対象の入れ替わり/方向・状態の逆転/台帳にない事実の断定で理解が変わる/否定の反転)。
- 軽微NG: 意味は逆転しないが不正確・過剰断定・曖昧・対象範囲の曖昧さ・台帳未提示事項の軽い具体化。
- 同一誤りは同一工程1件(JA/EN共通でID共有)。

## 3. 工程
- s1_ja = ①JA最終稿(`ja_writer/revision2.md`、R2)
- s2_en = ②EN(`b1b/article.md`。Checkerなしのためこれが最終)
- ③R0->R2退行(regressions) = R0(`ja_writer/original.md`)では正しい/該当NGなしだった箇所が、R1/R2の修正工程で新たにNG(重大/軽微)になったもの(R0に同種NGがあり形を変えただけのものは退行に数えない。R0にあって R2で直ったものは退行ではない)。R1(`revision1.md`)は経過確認用。
- 1NG項目のstageは {s1, s2} それぞれ true/false(その工程のテキストに存在するか)。severityは1項目につき1つ。

## 4. ★fact 3分類(direction_facts)
対象: `docs/pm/allfact_e2e_02/theme_fact_watchlist.md` の★印fact(meta HC-012/HC-014、hormuz HF-007/HF-009(HF-008/HF-011も記録のみ)。space_weapons は★なし: 参考として F-001/F-002/F-011/F-013 の範囲限定を direction_facts に記録してよい(件数は参考扱い))のうち、その記事が扱った(選択した)もの。
- correct: 台帳notes_for_writerの方向・限定どおり(JA/ENいずれも)
- ambiguous: 誤りとは言えないが方向・限定が曖昧/読者が誤読しうる(軽微NGに対応しうる)
- misread: 方向・状態・主体が逆転/取り違え(重大NGに対応)
- not_selected: 記事が扱っていない(件数集計に含めない)
- 文脈判定: 文単独でなく前後の文脈で判定する。「元に戻した」「ロールバック」等の語がある、だけで重大にしない(例 HC-012は「サービス全体停止」と読ませれば誤読、「人間コンシェルジュ機能の当面のロールバック」と読めれば正しい)。JA/ENで分かれる場合は悪い方を採用し、notesに記す。
- misread/ambiguousの場合は対応するng_itemsを必ず起票し、fact_idで結ぶ。

## 5. 同一誤りのID共有・ID規則
- JAとENで同じ誤りは1項目(stage.s1/s2を両方true)。ENで新規なら s1=false,s2=true。JAにのみあれば s1=true,s2=false。
- ID形式(M5変更): `<slug>-<code>-NN`(codeは匿名記事コード。variantを含めない。例 meta-k7f2-03)。
- kind: subject|object|scope|time|negation|causal|added_fact から1つ。別factの限定語・条件・範囲を連結したことに由来する誤りは cross_fact=true(H2集計)。
- stage は {s0,s1,s2}(M3追加: s0=R0=修正前原稿 ja_writer/original.md に存在)。stages.s0_r0 の件数は stage.s0=true の件数と一致させる。R0はR2より前の原稿なので、R0にあってR2で直ったものも s0=true,s1=false で記録する。

## 6. 判定保留
- 重大/軽微の境界で確信が持てないもの、文章品質のみ(事実の意味変化なし)のものは `pending` に {id,text,reason,leaning} で記し、件数集計には含めない(境界でどちらかに倒す場合は軽微に計上し notes に明記)。

## 7. 評価者が参照するファイル
- 記事(匿名コピー): `er052_output/open233_b3_trial_01/eval/blind/<slug>/<code>/{ja_writer/original.md(R0), ja_writer/revision1.md, ja_writer/revision2.md(R2), b1b/article.md(EN)}`。`runs/`配下とMAP.jsonは読まない。
- brief: 記事評価者は読まない(brief_reviewは別インスタンス、9節)
- 台帳: `er052_output/open233_polysemy_trial_02/ledgers/<slug>/control/research_ledger/verified_fact_ledger.txt`(notes_for_writer含む)
- ★fact一覧: `docs/pm/allfact_e2e_02/theme_fact_watchlist.md`
- 書式例: `er052_output/open233_allfact_note_e2e_02/eval/stagewise/NG_meta.md`、定義: `.../STAGEWISE_SUMMARY.md` §0
- 評価者は研究brief/Note内容を他条件の評価に流用しない。条件(variant)は評価者に開示されず、集計時にMAPで結合する。

## 8. 1記事の評価手順
1. 台帳を読み、★factと各factのnotes_for_writerを把握する。
2. R2(JA最終)を文単位で台帳と照合 -> s1のng_items起票、★factを3分類。
3. EN(b1b)をR2と台帳に照合 -> 継続(s1=s2=true)/EN新規(s2のみ)/ENで解消(s1のみ)を整理。
4. R0を読み、R2との差分でR0->R2退行(R0が正しかった箇所の新規NG)を判定、regressionsに計上。
5. article JSONを schema どおり出力。stages.s1_ja/s2_en/regressions の件数は ng_items から一致させる(aggregate_matrix.py が検算する)。
6. 判定は台帳と本ルーブリックのみで行い、人間確認なしの単独判定である旨をnotesに残す。

## 9. brief品質の記録項目(M5/M6で改訂。記事評価者は記入しない)
brief_reviewは**別インスタンス**が匿名brief(`eval/blind/<slug>/_briefs/<bcode>/`)に対して `eval/brief_review/<slug>_<bcode>.json` へ記録する(手順 `docs/pm/b3_trial_01/blinding.md`、委任文 `eval_assignment.md` B)。件数集計の判定には使わず記録のみ。
- 評価単位: 箇条書き1項目、または句点で区切った1文(Storyline行は文ごとに1単位)。
- `units_total` / `omitted_units` / `omitted_rate`(件数と率の両方): 台帳にある主体・対象・数値/率の掛かる先が、briefの単位で省略または不明になっているもの。台帳自体が曖昧な箇所は数えず notes に記す。
- `cross_fact_qualifier`: 別factの限定語・修飾語が1単位内で連結されているか(true/false)。
- `unprovided_checklist_hits`: `unprovided_checklist_<slug>.md`(台帳から事前作成、fact本文/numeric_scopeに「未提示/不明/示されていない/確認できない」とある事項のみ。「〜とは書かない」型notesは対象外)の各項目について、briefが明記しているか。評価者が対象事項を自分で決めない。
