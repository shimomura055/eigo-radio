# 5記事Trial評価表(OPEN-233-LEDGER-POLYSEMY-NOTE-TRIAL-04、記入前・DEV、VALIDATEDでもProduction採用ではない)
ラベル基準: er052_output/open233_prod_e2e_01/labeling_guide_01.md(重大度1-1・禁止§3)とdocs/pm/polysemy_trial_02/P0c_eval_template.md の3値定義。新基準は追加しない。
段別ラベル: 忠実/逆転/曖昧。brief転記: 逐語/意味維持/欠落/改変。Y/N列はY/N。
## 1 記事x条件(slug: meta, hormuz, space_weapons, sewer, ai_control / 条件: control, nb)
| slug | 条件 | (1)必要Fact自動特定(Y/N) | (2)不要FactへのNote過剰付与(件) | (3)Note正確性(Y/N) | (4)捏造(件) | (5)B3転記 | (6)R0 | R1 | R2 | EN | (7)重大誤読防止 | (8)新誤断定(件) | (9)留保欠落(件) | (10)説明過多/不自然(件) | (11)Story/Ent | 備考 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
(10行: 5記事x2条件。controlは(1)〜(5)をN/A、(6)以降のみ記入)
## 2 判定の定義
- (1)必要Fact自動特定: 事前指定の対象fact_id(P0a 6節)をNote付与対象として自動で捕捉したか。全件=Y、1件でも漏れ=N(漏れfact_id列挙)。
- (2)過剰付与: 対象fact_id以外で付いたNoteの件数(確度高でない/誤読リスクなしと人が判断したもの)。0が目標。
- (3)Note正確性: Note文が台帳の当該factの意味(scope/conditions/notes)と一致=Y。取違え・強化・弱化が1件でもN。
- (4)捏造: 台帳に無い具体的事実・数値・主体・動機がNoteにある件数。
- (5)B3転記: Note→B3 brief。逐語/意味維持/欠落/改変(欠落・改変は(7)の失敗要因として記録)。
- (6)Writer保持: R0/R1/R2それぞれの対象fact該当文を忠実/逆転/曖昧で判定。R1/R2で忠実→逆転に退行したら備考へ。
- (7)重大誤読防止: Controlで逆転型が出た箇所がN+Bで出ない=防止成功。Controlで逆転型が出ていない記事は「比較不能(悪化なしのみ)」と記入し、N+Bで逆転が出たら悪化=FAIL。
- (8)新誤断定: 台帳より断定が強い文(断定強化)。N+BがControlより増えたら悪化。
- (9)留保欠落: 台帳の限定・留保(予定/評価/模擬/当時等)の落ち。N+B<=Controlが目標。
- (10)説明過多/不自然: Note由来の注釈的・解説的で会話として不自然な文の件数。
- (11)Story/Entertainment: 決定論指標(文長・TTR・JA逐語率)+pairwise(N+B vs Control)。劣る率<=25%かつ4軸いずれも過半数でない=許容(前回基準流用)。
- EN/Checker(任意・Phase 2): EN段ラベル、Checker最終状態(候補数・blocking数・Rewrite回数)はControl比で悪化なしを確認。承認根拠にしない。
## 3 Meta専用: rollback経路(必須。ここが失敗なら他4記事が良好でも単純VALIDATEDにしない)
対象: MUSE-HC-012(+HC-014)の「ロールバックした」。Before参照: E2E_02で復元型誤読3/5。
| 項目 | control | nb |
|---|---|---|
| 自動捕捉(Y/N) | | |
| Note全文(逐語貼付) | N/A | |
| Note内容Gate(PASS/FAIL) | N/A | |
| brief転記(逐語/意味維持/欠落/改変) | N/A | |
| R0(忠実/逆転/曖昧) | | |
| R1 | | |
| R2 | | |
| EN | | |
| 誤読防止判定(防止成功/比較不能/失敗) | | |
Note内容Gate: 「取り下げ」「機能のない状態」「復活再提供ではない」の3点が保持されていればPASS。「全体停止のみ」「復元ではない」の表現はFAIL。
Meta総合: 自動捕捉Y かつ Note Gate PASS かつ brief転記が逐語/意味維持 かつ R0/R2が忠実 かつ Controlの実誤読が防止できた、の全てを満たすとき成功。1つでも欠けたら失敗(他4記事が良好でもVALIDATEDにしない、USER_DECISION_REQUIREDで報告)。
## 4 判定
Status(VALIDATED/REJECTED/USER_DECISION_REQUIRED): ____ / STOP該当: ____
