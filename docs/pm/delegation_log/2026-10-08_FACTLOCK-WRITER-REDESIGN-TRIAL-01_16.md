管理ID: FACTLOCK-WRITER-REDESIGN-TRIAL-01 委任_16(ASTRA-REVISE-MATRIX-02: ホルムズ+ミニバッグの2記事で Fact Lock R0 → Astra R1→R2 を X/Y 2系列、評価、SSOT記録、未処理の人間確認結果記録とOPEN起票)。日付 2026-10-08。ユーザーGo取得済み(2026-10-08「OKです。提示は元記事＋XYのR2のみでよいです(R1は不要)。Goお願いします。」)。

## 予算・制約
- API予算 上限 ¥80(見込み約¥60)。超過見込みで生成を止めて報告。astra 単価は routing contract 未登録のため、全トークンを記録し推定単価(gpt-6-sol 2.00/0.20/10.00 USD/1M × 2.5、USD/JPY=160)で円換算。推定である旨を全費用表に明記。
- Production コード(er019_*/er006_*/er012_*/er003_* 等)・CURRENT_SPEC.md は変更しない。
- `git add -A` 禁止。個別 add。`_private/` は add しない。
- 委任文(このメッセージ全文)を一字一句そのまま `docs/pm/delegation_log/2026-10-08_FACTLOCK-WRITER-REDESIGN-TRIAL-01_16.md` に保存し、`docs/pm/tools/check_delegation_prompt.py --file <path>` を実行して結果を記録(FAILでも続行)。
- 結果は `docs/pm/RESULT_PACKET.md` と `docs/pm/delegation_log/2026-10-08_FACTLOCK-WRITER-REDESIGN-TRIAL-01_16_result.md` の両方に書く。
- 実行環境は委任_15 と同じ `.venv\Scripts\python.exe`。委任_15 のツール `er052_output/factlock_writer_trial_01/astra_revise_matrix_01/tools/{run_matrix.py,make_report.py}` を再利用・拡張してよい(新出力先に書くこと)。

## 試験設計(委任_15 と同一条件、記事を2本追加)
- 出力先: `er052_output/factlock_writer_trial_01/astra_revise_matrix_02/`(`DESIGN.md`、`runs/<article>/{A,B}/r{1,2}.md` と `.response.json`、`usage_log.jsonl`、`eval/`、`USER_PACK.md`、`_private/`)。
- 系列A(=X、ユーザーPromptのみ): developer/system メッセージなし。系列B(=Y、熟練編集者): developer = Step 1 F2 文を `step1_chat_repro_01/conditions.json` から逐語。
- 各段 user メッセージ(共通): `以下の記事:\n\n{前段本文}\n\n事実は変えずにエンターテイメント性をもっと上げた記事にReviseください。長さは800〜1000字程度でお願いします。`
- モデル `gpt-6-astra`、reasoning は委任_15 と同一。R1 入力 = R0、R2 入力 = R1 出力。`previous_response_id` 不使用。記号禁止リストなし。R3 は実施しない。
- 記事1「ホルムズ」: Fact Lock v1 の既存 R0 を使う。選択規則: `er052_output/factlock_writer_trial_01/runs/hormuz/control/b2__factlock__r1/ja_writer/original.md` が存在し run が completed ならそれ。無ければ b1→b3→b4 の順で completed の最初の run(r1 優先)。inline タグ `【事実N】` は委任_15 と同じ `strip_tags` で除去。採用パス・SHA・台帳・B3 brief を記録。
- 記事2「ミニバッグ」: 本日の全6-luna E2E `er052_output/gpt6_wiring_e2e_01/run_02/` の台帳(`research_ledger/verified_fact_ledger.txt`)と B3 brief(`storyline_b3/selected_brief.md`)を入力に、**Fact Lock v1 と同一の R0 手順**で R0 を新規生成する(モデル gpt-6-luna、Fact Lock v1 の R0 プロンプト・注記版 brief 作成(中核/周辺の数値注記)・タグ付け・JA Fact Check(Full Ledger、MAJOR→must-fix 1回→STOP)を `er052_factlock_writer_trial_01_run.py` の R0 経路で再現。R1/R2 は走らせない)。生成した R0 のタグ除去後本文を起点にする。STOP した場合は理由を報告して記事2は中止(記事1は続行)。
- 並列: 記事×系列の4系列を並列可(最大4プロセス)。段内は逐次。

## 評価(R0/R1/R2 × 2系列 × 2記事、R0 は記事ごとに共通 → 計10本)
1. JA Fact Check 全台帳(gpt-6-luna、委任_15 と同一呼び出し): MAJOR/MINOR 件数と各指摘(NG文・台帳行・理由)。
2. 決定論指標: 字数、段落、1文段落、問い、ダッシュ、Markdown残存、記号Gate(計測のみ、該当記号と件数)、台帳外数値。
3. R0 比の新規具体主張(ii)。
4. `eval/HUMAN_CHECK_MATRIX_02.md`: FC MAJOR と、MINOR のうち主体・因果・否定の型を3行形式(NG文・台帳・理由)で列挙。
5. `eval/SUMMARY_MATRIX_02.md`: 記事×段×系列の表。委任_15 の meta 結果も同じ表形式で併記(再評価はしない、既存値を転記)。
6. `eval/COST_MATRIX_02.md`: 記事・系列ごとの R1 / R1+R2 の推定円、旧 Luna R1+R2 実費との差(ホルムズは同 run の raw_usage_log 実測、ミニバッグは E2E run_02 の cost.json の ja_r1+ja_r2)、1セット換算(現行約¥52/¥43 基準)。

## ユーザー提示パック `USER_PACK_02.md`
- 記事ごとに **R0(元記事)、X-R2、Y-R2 の3本**を全文掲載(計6本)。**系列は開示**(X=ユーザーPromptのみ、Y=熟練編集者 と明記)。Markdown 除去後の本文、冒頭に字数。R1 は載せない。FC 結果は載せない(別表)。

## 未処理の記録(同梱、API¥0)
A. 本日のユーザー人間確認結果を SSOT に記録:
   - ASTRA-REVISE-MATRIX-01(meta): ユーザー判定「Xの方がよく、コストの兼ね合いもあるのでR2が落としどころ」(X=系列A ユーザーPromptのみ)。
   - Trial B 評価パックの重大候補: 候補1 `baseline/meta/b3/r1` EN「in one case in which Meta was asked to negotiate internet and cable bills」(台帳 MUSE-HC-011: 依頼者はMeta従業員)= **ユーザー判定 重大**、翻訳段由来。候補2 `all6/space_weapons/b2/r1`「配備が確認されたことと…」= **ユーザー判定 軽微**、R1/R2段で断定が強まった型。
   - 候補1 の検査通過状況(Fable確認済み、証跡): EN deviation check `.../b3__baseline__r1/b1b/audit/deviation_check.json` は当該文を MINOR(changed_number のみ、changed_actor=false、origin=translation)、overall LEDGER_COMPLIANT。Checker(OPEN-233、gpt-6-luna、E2E02と同一スイッチ)`.../b3__baseline__r1/checker/runs/meta_run03_advanced.json` は当該文を Stage 1 が別事実(MUSE-HC-010、negation_polarity_mismatch)の理由で候補化、Stage 2 一次 QUALITY → second opinion ACCEPTABLE で confirmed_downgrade=true、final_state=RESOLVED_REWRITE_THEN_DOWNGRADE(PASS系)、当該文は出力に残存。= **EN検査・Checker の2層が重大を見逃した実例**。
   - 記録先: `DECISION_LOG.md`(本日分エントリ)、`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`(§107 に人間確認結果の追記、または新§)。
B. 新規 OPEN 項目を `OPEN_ITEMS.md` に起票(番号は既存の最大+1、本体行3,000字以内): 件名「翻訳段(EN化)で生じる事実NGと EN deviation check / Checker の見逃し」。内容: 発生例(候補1 重大、Fact Lock セル EN 軽微6件中3件が翻訳由来、EN末尾要約文の付け足し、複数形化、訳語選択)、見逃し構造 (a) EN検査の分類器が主体入替を「数」に誤分類 (b) Checker が正しい文を別理由で候補化し Stage 2 が別論点を審査して格下げ、現行の守り(6-luna EN検査の厳格化、O3観測 最初の10記事)、対策検討は Checker 設計変更を含むため条件D相当で Opus レビュー対象(起票時点では未依頼)。Status: OPEN(対策未着手)。
C. `docs/pm/REPORT_LEDGER.md` 更新。

## SSOT・Git
- REPORT に新§(§107 の次): 本委任の設計・10本の指標表・FC 指摘・費用・Status=MEASURED(人間確認待ち)。
- DECISION_LOG に本日分エントリ(ユーザー指示逐語「ホルムズ海峡の記事でXYそれぞれR2までで良いので、同じセンスで記事を作り…XYは開示してOK…軽微・重大のカウントも」「もう一記事…バリエーションのある記事」→ Fable推薦 small_bag をユーザー承認、「提示は元記事＋XYのR2のみ」)。
- 個別 `git add`(`astra_revise_matrix_02/` から `_private/` を除く、SSOT: REPORT/DECISION_LOG/OPEN_ITEMS/REPORT_LEDGER、delegation_log の委任文・check・result)。`git status` で混入確認後 commit(例: 「FACTLOCK-WRITER-REDESIGN-TRIAL-01 ASTRA-REVISE-MATRIX-02: hormuz+small_bag Fact Lock R0→Astra R1-R2 X/Y MEASURED(FC MAJOR x/x)、人間確認結果記録(meta X/R2、候補1重大・候補2軽微)、OPEN-24x 翻訳段NG+検査見逃し起票、REPORT §xxx、実費¥xx(astra単価推定)」)、`git push origin main`。conflict/エラー時は中断して報告。

## result に書くこと
実費(推定注記)、所要時間、R0 の採用/生成経緯(ホルムズのパス・SHA、ミニバッグの R0 生成ログ・JA FC 結果・must-fix 有無)、10本の指標表、FC 指摘全文、重大候補、USER_PACK_02.md のパス、COST の要点、新規 OPEN 番号、commit hash と raw URL(https://raw.githubusercontent.com/shimomura055/eigo-radio/main/<path>)、check_delegation_prompt 結果、未解決点・逸脱。
