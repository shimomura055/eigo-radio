# RESULT: FACTLOCK-WRITER-REDESIGN-TRIAL-01 委任_16 ASTRA-REVISE-MATRIX-02 (2026-10-08)

Status: MEASURED(人間確認待ち)。Production変更なし。VALIDATED/APPROVED_FOR_PRODUCTION未宣言。

## 実費・所要
- 総額 約¥64.92(**astra単価は未登録のため gpt-6-sol x2.5 の推定**、USD/JPY=160)= astra生成8本 ¥60.21(推定)+ ミニバッグR0生成(luna実測x登録単価)¥1.39 + JA FC 10本 ¥1.33 + (ii) 10本 ¥2.00(1本0.2円概算)。上限¥80内。トークン(生成8本): input 5991 / cached 0 / output 13855(うちreasoning 7996)。
- 所要: 準備〜全評価・集計まで約10分(16:12〜16:20)。R0生成約100秒、astra生成は4系列並列で約2分、評価は記事ごとに約70秒。

## R0 の採用/生成経緯
- ホルムズ: 既存 `er052_output/factlock_writer_trial_01/runs/hormuz/control/b2__factlock__r1/ja_writer/original.md`(manifest completed、選択規則どおり)。SHA original.md 169f06a48f4357e18e5b657d3c432f765af92ec58a6b710b76f8cc8429fada54、strip_tags後 R0.md c9ee84e0b965d79719cb50d238f7ccddc75412d1ec4b2580726a4a618ac18fd7(`with_tags`のstripと一致確認済み)、台帳 9bd6834e...、B3 brief 4ed19d37...(注記版 briefs/hormuz/b2 と同SHA)。
- ミニバッグ: E2E `er052_output/gpt6_wiring_e2e_01/run_02/` の台帳(SHA 0cc8ca3f...)・B3 brief(SHA 55bb9ba3...)から Fact Lock v1手順で新規生成(`astra_revise_matrix_02/tools/gen_r0_small_bag.py`。Production関数 `run_ja_writer_o_r1_r2` の Original段を gpt-6-luna で実行し、R1呼び出し直前で打ち切り。R1/R2のAPI未呼出)。ログ `r0_small_bag/R0_RUN.json`。Writer 1 call、JA FC(Full Ledger)= LEDGER_COMPLIANT MAJOR 0/MINOR 0、**must-fix 不要**、STOPなし。タグ照合(測定のみ): 17文中9文タグ、数値不一致0。R0 SHA 88ba339d8517d6787e9a8ca272b3fbae26a9c0be07472b954df33e31e474e1b0。
- 注記: 元briefのSelected Factsは箇条書きでなく1段落だったため、文境界で3事実に分け【事実N】を付与(本文は逐語)。数値注記は中核2(2026年9月・2026年10月)・周辺2(Fall 2026・2026年)。この加工は実行層(Sonnet)の判断。

## 10本の指標表(X=ユーザーPromptのみ=系列A、Y=熟練編集者=系列B)
| 記事 | 本 | MAJOR | MINOR | 新規主張(ii) | 字数 | 段落 | 1文段落 | 問い | ダッシュ | 台帳外数値 | 記号Gate(raw/P1) | 費用(推定円) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ホルムズ | R0 | 0 | 0 | 0 | 772 | 6 | 0 | 1 | 0 | 0 | 0/0 | - |
| ホルムズ | X_R1 | 0 | 0 | 0 | 822 | 8 | 0 | 1 | 0 | 0 | 0/0 | 9.52 |
| ホルムズ | X_R2 | 0 | 0 | 0 | 909 | 8 | 0 | 1 | 1 | 0 | 0/0 | 7.02 |
| ホルムズ | Y_R1 | 0 | 0 | 0 | 916 | 9 | 1 | 0 | 0 | 0 | 0/0 | 6.67 |
| ホルムズ | Y_R2 | 0 | 0 | 2 | 977 | 10 | 0 | 0 | 0 | 0 | 0/0 | 7.46 |
| ミニバッグ | R0 | 0 | 0 | 0 | 754 | 7 | 0 | 0 | 0 | 0 | 0/0 | - |
| ミニバッグ | X_R1 | 0 | 0 | 0 | 905 | 7 | 0 | 3 | 0 | 0 | 0/0 | 8.29 |
| ミニバッグ | X_R2 | 0 | 0 | 1 | 875 | 7 | 0 | 4 | 0 | 0 | 0/0 | 8.50 |
| ミニバッグ | Y_R1 | 0 | 0 | 0 | 987 | 10 | 0 | 3 | 0 | 0 | 0/0 | 6.70 |
| ミニバッグ | Y_R2 | 0 | 0 | 0 | 950 | 16 | 2 | 5 | 1 | 0 | 1/1(「……」) | 6.04 |
meta(委任_15)の既存値は `eval/SUMMARY_MATRIX_02.md` に併記(再評価なし)。記事x段x系列表・MAJOR/MINORカウント表も同ファイル。

## FC 指摘全文
- **MAJOR・MINOR とも全10本で 0件**(全て LEDGER_COMPLIANT)。`eval/HUMAN_CHECK_MATRIX_02.md` は「該当なし」(主体・因果・否定型のMINORも0)。
- 参考((ii)、FCとは別系統): ホルムズ Y_R2「伝えられているのは、料金案と、それを別の案件に置き換えるという発言まで。」(報道内容をそれだけに限る根拠なし)、同「貿易や投資が実際にまとまった、という話ではない。」(案件が未成立との事実は一覧にない)、ミニバッグ X_R2「そのミニバッグ、採用理由は「荷物が入る」より「目に入る」。」(採用理由を視覚的な注目と断定)。FCはこれらを指摘していない(不在・未成立を述べる型の取り逃し可能性、人間確認対象)。

## 重大候補・人間確認結果の記録(API 0円)
- 新規の重大候補(FC由来)はなし。
- SSOT記録済み: meta X/R2(ASTRA-REVISE-MATRIX-01)、Trial B 候補1=重大(翻訳段由来)・候補2=軽微、候補1の検査通過状況(EN deviation check 2層・Checker 見逃し)。記録先 DECISION_LOG(本日分エントリ)、REPORT §107追記+§108、OPEN-243。

## 成果物パス
- ユーザー提示: `er052_output/factlock_writer_trial_01/astra_revise_matrix_02/USER_PACK_02.md`(記事ごと 元記事/X-R2/Y-R2 の3本、系列開示、R1・FC非掲載)。
- 設計 `.../astra_revise_matrix_02/DESIGN.md`、評価 `.../eval/{SUMMARY_MATRIX_02,HUMAN_CHECK_MATRIX_02,COST_MATRIX_02}.md`。

## COST 要点
Astra R1のみ(推定円): ホルムズ X 9.52 / Y 6.67、ミニバッグ X 8.29 / Y 6.70。R1+R2: ホルムズ X 16.54 / Y 14.13、ミニバッグ X 16.79 / Y 12.75(4系列平均15.05)。旧Luna R1+R2実費: ホルムズ ¥0.603(raw_usage_log実測)、ミニバッグ ¥0.446(E2E run_02 cost.json)。置換時の純増は約+¥12.3〜¥16.4。1セット換算(現行約¥52 Standard/約¥43 Batch に加算、総増): R1のみ +¥6.7〜¥9.5、R1+R2 +¥12.8〜¥16.8(合計 約¥65〜¥69 / Batch基準 約¥56〜¥60)。astra単価は推定。

## 新規 OPEN
OPEN-243(翻訳段(EN化)で生じる事実NGと EN deviation check / Checker の見逃し、Status=OPEN、対策未着手。Opus独立レビュー(条件D相当)は起票時点で未依頼)。

## check_delegation_prompt
`docs/pm/delegation_log/2026-10-08_FACTLOCK-WRITER-REDESIGN-TRIAL-01_16.md_check.json`(stdout保存、status=FAIL、必須セクション欠落[性質/事前指定Read一覧/事前指定Grep一覧/実行コマンド全文]・固定ブロックラベル欠落[E-1,D-1,G-1,F-1]。FAILでも続行の指示どおり)。

## 逸脱・未解決点
- 実行はすべて指示どおり。逸脱: (1) ミニバッグ briefのSelected Facts 3事実化と数値注記は実行層判断(上記)。(2) R0のR1打ち切りは Production関数への実行時patch(BaseException)で実現、ファイル編集なし。(3) check_delegation_prompt は FAIL(委任文の形式要件、実行には影響なし)。(4) (ii)費用は1本0.2円の概算。
- 人間確認待ち: USER_PACK_02.md の盲検読み(面白さ)。

## commit / raw URL
- commit ee19bacb(push済み origin/main)。
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/factlock_writer_trial_01/astra_revise_matrix_02/USER_PACK_02.md
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/factlock_writer_trial_01/astra_revise_matrix_02/eval/SUMMARY_MATRIX_02.md
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/factlock_writer_trial_01/astra_revise_matrix_02/eval/COST_MATRIX_02.md
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/factlock_writer_trial_01/astra_revise_matrix_02/eval/HUMAN_CHECK_MATRIX_02.md
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/factlock_writer_trial_01/astra_revise_matrix_02/DESIGN.md
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/OPEN_ITEMS.md
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/DECISION_LOG.md
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/docs/pm/REPORT_LEDGER.md
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/docs/pm/delegation_log/2026-10-08_FACTLOCK-WRITER-REDESIGN-TRIAL-01_16_result.md
