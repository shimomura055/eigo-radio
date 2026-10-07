# human_review_pack (OPEN-233-CONTROL-CHECKER-POLYSEMY-PRODUCTION-PATH-TRIAL-01) テンプレ

ユーザー確認用。評価完了後にPM側が `<<...>>` を実ファイル本文で置換し、`er052_output/open233_control_checker_polysemy_trial_01/eval/HUMAN_REVIEW_PACK.md` に出力する(台帳fact・記事該当文は原文のまま。要約・加工しない)。冒頭に「重大/Rollback判定は評価インスタンスの単独判定(確認前)」と明記する。MAP開封(条件結合)は全員分の評価が揃ってから。

## 収録対象(preregistration_01.md 6節「人間確認が必要な件」の定義に従う。1件=1ブロック)
- (H1) 重大NGと判定された全件(severity=major、または pending で leaning=major)
- (H2) Metaの Rollback(MUSE-HC-012)判定の全件(10記事 x JA R2 / EN Checker前 / EN最終、ただしnot_selectedは除く)
- (H3) 評価者間不一致(評価者 vs rollback_X の3値ラベル不一致、重大判定ありの記事の再評価との不一致)
- (H4) Checker Rewrite由来の新規NG(after_new_ng=major の全件、minorは件数のみ)

## raw URL規約
`https://raw.githubusercontent.com/shimomura055/eigo-radio/main/<repo相対パス>`。commit・push済みのファイルのみURLを載せる。

## 件ブロック(1件1ブロック。H番号-連番)
### #<H番号-NN> <slug> <code> (<種別: major|rollback|disagreement|rewrite_new_ng>)
- 台帳該当fact(原文): `<<fact_id と本文、notes_for_writer(あれば)>>`
- 記事該当文(原文): JA R2「<<該当文>>」 / EN Checker前「<<該当文>>」 / EN最終「<<該当文>>」(該当するもののみ)
- 評価インスタンスの判定: <<severity または rollback 3値、kind、根拠1文>>
- (H3のみ)もう一方の判定: <<...>>
- (H4のみ)Checker変更前→変更後: <<before>> → <<after>>
- 記事全文URL: JA <raw URL> / EN最終 <raw URL>
- **質問**: <<その文は読者に誤った理解を与えますか? 以下から選択: 重大(意味が変わる) / 軽微(曖昧・過剰断定) / 問題なし。rollback の場合は: 『機能が提供されない』と読める / 曖昧(どちらにも読める) / 『機能が復活した』と読める>>
- ユーザー回答欄: (  )

## 末尾(PM記入)
- 総件数(H1/H2/H3/H4別)、ユーザー回答後に preregistration の指標①②⑤を確定値に更新する旨。
- Production変更: なし / API費用: ¥0(評価のみ)
