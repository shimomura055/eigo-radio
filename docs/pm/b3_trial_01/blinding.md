# 評価の匿名化手順(M5、OPEN-233-B3-BRIEF-STRUCTURE-TRIAL-01、Opus条件Aレビュー反映)

目的: 評価者に条件(V0〜V6)・b/w rep・期待順位を見せず、パス/ファイル名/NG IDからの推測を防ぐ。

## 作成(決定論)
`python er052_output/open233_b3_trial_01/tools/make_blind_copies.py [--seed 20261007] [--what briefs|articles|both]`
- 記事: `runs/<slug>/nb/<V>/b<i>/w<j>/{ja_writer/original.md,revision1.md,revision2.md,b1b/article.md}` を `eval/blind/<slug>/<code>/` に同じ相対名でコピー(R0=original、R2=revision2、EN=b1b/article.md)。codeはテーマ名を残し、variantは `sha256(seed|キー)` 由来の固定乱数4文字(紛らわしい文字を除く)。
- brief: `eval/blind/<slug>/_briefs/<bcode>/selected_brief.md`(bcodeも同様。brief_review用)。
- 対応表 `eval/blind/MAP.json`(code -> variant/b3_rep/writer_rep/bcode)は **集計(aggregate_b3.py)まで評価者に渡さない**。同じseed・同じ入力なら再実行しても同一(再現性)。
- 記事評価者の入力は `eval/blind/<slug>/<code>/` のみ(+台帳、★fact一覧、rubric)。`runs/` 配下、`MAP.json`、`design_01.md`、`brief_features.json` は読まない。
- NG IDは `<slug>-<code>-NN`(variantを含めない)。出力は `eval/articles/<slug>_<code>.json`(slug+codeのみ記入。variant/b/wはスキーマ上書かない)。
- 評価順はランダム(評価者はcodeの辞書順逆順など固定の規則で並べる。条件順に評価しない)。

## brief_review(別インスタンス)
- brief評価は **記事評価者とは別インスタンス** が、匿名brief(`_briefs/<bcode>/`)に対してのみ行う(記事本文・記事評価結果は見せない)。
- 単位=「箇条書き1項目、または句点区切り1文」(Storyline行は文ごとに1単位)。省略単位数(台帳にある主体・対象・数値の掛かる先がbriefで落ちている単位)と全単位数を記録し、件数と率の両方を出す。
- 未提示事項は `docs/pm/b3_trial_01/unprovided_checklist_<slug>.md` の項目ごとに stated(true/false)を記録。評価者が対象事項を自分で決めない。
- 出力: `eval/brief_review/<slug>_<bcode>.json`(article_schema.json の x-brief_review_file 参照)。
- 限界(正直な記録): V5形式のbriefは `[fact_id]`/逐語形式が見えるため、brief評価者にはvariantの一部が推測され得る(V5は今回実行しない)。

## 集計
`aggregate_b3.py --map eval/blind/MAP.json`(既定で `<in親>/blind/MAP.json`)。MAPで記事・briefのcodeをvariantに解決する。評価者は集計完了まで見ない。
