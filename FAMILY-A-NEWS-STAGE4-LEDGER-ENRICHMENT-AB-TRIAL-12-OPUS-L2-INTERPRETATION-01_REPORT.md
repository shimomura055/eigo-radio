# FAMILY-A-NEWS-STAGE4-LEDGER-ENRICHMENT-AB-TRIAL-12-OPUS-L2-INTERPRETATION-01_REPORT

管理ID: PM-CLOSEOUT-CONSOLIDATION-74-USER-ANSWERS-2026-09-11-02
日付: 2026-09-11
種別: opus-consultant出力、読み取り専用、Fable経由でSonnetが転記(内容の改変・要約禁止、原文のまま保存)

---

<<<OPUS_OUTPUT_BEGIN>>>
## 要点(5行)
1. **Trial-12(A/B)だけを見て「fact供給量が主因」と判断するのは危険**。同じ出力ディレクトリに**未報告のTrial-12b(条件C/D、12 run分の完成artifact)**が既に存在し、その結果は「fact数」説をほぼ否定している(`er011_output\news_ledger_enrichment_ab_trial_12\{leaveout_c,twofact_d}\_combo_results\`)。
2. 最終NG率は fact 5件=83.3% → 7件=**33.3%** → 10件=**83.3%** → 12件=33.3% と**fact数に対して単調でなく**、FACT-12/13(伊原の2打数2安打・モンテロ10号)の有無だけで完全に説明できる。
3. 一方、**「fact供給を増やすと初回attemptのPoint Value QA flagが消える」は極めて強い**(条件A 6/6 flagged vs 拡充3条件 0/18、Fisher p≈1.5e-5、完全分離)。anchor衝突・Gate overlap低下も3条件で再現。
4. **Fact Checker FAILは拡充の副作用ではなく「露出」**。日本人選手名のローマ字表記誤り(伊原陵人=公式 Takato Ihara)は条件A記事にも出現しているが、条件AはOverlap Gateで先に落ちてFact Checkerへ到達しなかっただけ(打ち切り=censoringによる見かけ上の差)。
5. 従って正式判断は「A/BのN増し」ではなく、**(a)打ち切られた記事へのFact Checker単独適用(~¥25)と(b)別の周辺fact2件による条件E(~¥90)** を先に取るのが費用対効果最大。仕様変更はすべて候補であり採用可否はユーザー判断。

## 論点1: 証拠の強さ ——「fact供給量が主因」とは言えない。「どのfactか」が主因
### 4条件の実測(各n=6、A2×3+B1B×3。A/Bは報告済み、C/Dは artifact から直読)
| 条件 | usable fact | 初回attempt Value QA flag | anchor衝突平均 | Gate overlap平均 | lexical起因NG | Fact Checker到達 | うちPASS | **最終NG率** |
|---|---|---|---|---|---|---|---|---|
| A(現行) | 5 | **6/6** | 1.5 | 0.4497 | 4/6 | 1 | 1 | **83.3%** |
| D(A+FACT-12/13) | 7 | **0/6** | 0.0 | 0.348 | 1/6 | 5 | 4 | **33.3%** |
| C(A+FACT-08/09/10/11/14) | 10 | **0/6** | 0.167 | 0.336 | 1/6 | 5 | **0** | **83.3%** |
| B(全部) | 12 | **0/6** | 0.0 | 0.370 | 1/6 | 5 | 4 | **33.3%** |
根拠: A/Bは`FAMILY-A-NEWS-STAGE4-LEDGER-ENRICHMENT-AB-TRIAL-12_REPORT.md`継続実行節および`...\final_analysis_summary.json`。C/Dは`...\leaveout_c\_combo_results\*.json`・`...\twofact_d\_combo_results\*.json`(`final_ng`/`fact_verdict`/`retry_attempts`/`anchor_conflict_count`)。初回attempt Value QAは各run`point_overlap_article_retry_log.json`の attempt=0 の`value_qa_flagged`。
### 代替説明の照合
- **(A) fact数が主因** → **棄却寄り**。10件のCが5件のAと同じ83.3%。fact数と最終NG率は単調でない。
- **(B) 「選べる余地(fact利用率)」が主因** → **不十分**。Cのfact利用率は0.2〜0.5でDの0.43〜0.57と同水準、なのに結果は正反対。
- **(C) anchor衝突回避が本質** → **部分的に正しいが最終NGは説明しない**。C/D/Bすべてで衝突はほぼ消え(1.5→0〜0.17)、Gate overlapも0.45→0.34〜0.37に下がる。しかしCの最終NG率は下がらなかった。つまり**衝突回避はoverlap経路にのみ効き、記事全体の合否は別経路(Fact Check)で決まる**。既存監査の「anchor衝突と最終NGの相関はr=0.10のみ」(`FAMILY-A-NEWS-STAGE4-EVIDENCE-ALLOCATION-AUDIT-01_REPORT.md` L34)と完全に整合。
- **(D) 「非headline角度の周辺factが1つでもPointごとに供給されるか」が主因** → **もっとも整合的**。FACT-12/13は(i)見出し(スコア・佐藤輝HR)と重ならない人物軸、(ii)Point One/Twoへ1件ずつ自然に分かれる、(iii)新規固有名詞をほぼ増やさない。条件B/Dの全OK runでPoint Oneが必ずFACT-12を掴んでいる(`all_results_so_far.json` の enriched 全run:P1 anchor に FACT-12)。
- **(E) 統計的強さ** — A vs B の最終NG率 Fisher p=0.242 は変わらず非有意。A vs (B+D)プールでも p≈0.13。**唯一の強い分離は初回attempt Value QA(6/6 vs 0/18、p≈1.5e-5)**。報告書が「初めて有意」とした pooled Gate指標 p=0.0039 は条件操作とNG/OKの交絡(報告書 継続実行節3、L412-415)に加え、Gate指標そのものがNG判定式であるためトートロジーに近く、判断材料としては弱い。
**結論(解釈)**: 支持されるのは「**Ledgerに非headline角度の周辺factを供給すると、Point生成の逼迫(Value QA flag・anchor衝突・overlap)が構造的に解消する**」までで、「fact供給量を増やせば記事の合否が良くなる」は支持されない。

## 論点2: 新NGモード ——「拡充の副作用」ではなく「打ち切りの解除(unmasking)」
### 構造的か単発か → **構造的だが原因はfact数でなくfactの種類と、既存の潜在欠陥**
1. **潜在欠陥の露出**: 条件A記事にもローマ字誤りは出ている。`...\a2\current\run3\article.md`・`...\b1b\current\run2\article.md` は "Rihito Ihara"、`...\b1b\current\run1\article.md` は "Ryoto Ihara"。公式は Takato Ihara(`...\leaveout_c\b1b\run2\fact_qa.json` の contradictions)。条件AでFact Checkerに到達した唯一の1本(`...\b1b\current\run3\article.md`)は**たまたま下の名前を書かなかった**ためPASSしている。つまり条件AのFact Checker成績「PASS×1」は、5本が手前で落ちたことによる**打ち切りバイアス**の産物。
2. **fact"種類"依存**: Fact Checker到達分の非PASS率は C **5/5(4 FAIL+1 REVIEW_REQUIRED)** vs D 1/5、B 1/5。CだけがFACT-09/10(木下・ドリス・岩崎・及川など救援4投手名、回別失点内訳)を含む。**Ledgerが日本語表記のみで英語表記を持たないため、固有名詞を増やすfactを足すほどWriterのローマ字創作リスクが線形に増える**。
3. **拡充fact自身の記述品質**: D の FAIL 1件(`...\twofact_d\a2\run1\fact_qa.json`)はFACT-13「来日2年目で自身初の2桁本塁打」の年次を記事が取り違えたもの。報告書3節が明記した「新規factはconfidence中・URL人手未検証」(L96-104)の限界が実データで表面化した2例目。
### Fact Checker側で新たに必要な**観測項目**(仕様ではない、¥0〜低コストで既存artifactから取れる)
1. `contradictions`の**類型タグ**: (a)人名ローマ字/表記ゆれ、(b)年次・序数、(c)数値、(d)評価的表現。現状は自由文のみ(`fact_qa.json`)。
2. **記事中の固有名詞がLedgerに英語表記として存在するか**の突合率(Writer補完語率)。今回の全FAILの主因がここに集中している。
3. **打ち切り率の併記**: 「Fact Checker verdict分布」は必ず「到達n/総n」とセットで記録する。今回の条件Aのように到達1/6では verdict 比較は成立しない。
4. `web_search_call_count` と verdict の関係(検査強度のばらつき。C runは6〜7回、AのPASS runは4回)。同一記事でも検査深度によりPASS/FAILが揺れる可能性の観測。
5. **FACT-ID別FAIL寄与**(どの追加factを参照したrunがFAILしたか)。今回はFACT-09/10/13に集中。

## 論点3: N増し設計 —— A/Bの単純N増しは推奨しない
前提: 記事1本の実測単価は条件A(早期NG)¥4.2〜5.3、フルパス¥7.9〜16.3(`...\cost_summary.json`)。新規Ledger調査は¥148.6/回。
### 推奨案(合計見込み **¥85〜125**、¥200〜300枠内)
- **(1) 打ち切り解除の測定(見込み¥15〜25)**: 既に生成済みで**Fact Checkerへ到達しなかった記事7本**(条件A 5本、C 1本、B/D各1本)に、既存Fact Checker関数を単独適用する。新規記事生成なし、Production無改変、既存`article.md`を入力にするだけ。これで「条件Aの真のfact誤り率」が初めて測れ、論点2の"新NGモード"問題が**推測から測定に変わる**。最も費用対効果が高い。
- **(2) 条件E(見込み¥70〜100)**: 条件A + **FACT-11(佐藤輝28号の球種)/FACT-14(順位・ゲーム差)** の2件のみ(usable 7件、Dと同数)。既存enriched Ledgerからの機械抜粋のみで**新規research費用¥0**。「Dの効果は特定fact(12/13)固有か、それとも"非headline角度の周辺factが2件あること"か」を直接分離する。Trial-12bと同じharnessでN=6。
判定基準の目安(参考): Eの最終NG率が33%前後 → 「周辺factが2件あること」が本質(一般化可能)。83%前後 → FACT-12/13固有(一般化不可、Production方針としては弱い)。
### 代替1案(合計見込み **¥250前後**)
- **Hanshin型以外への一般化**: 別試合のbox-score型題材で新規Ledgerを調査(¥148.6)し、A'(現行相当)vs D'(+周辺fact2件)を各N=3で比較(¥100)。一般化可能性は直接わかるが、**論点2の打ち切りバイアスを解消しないまま**N増しするため、結論の解釈可能性は推奨案より低い。予算上限にも近い。
**非推奨**: A/Bの単純N増し(N=6→12など)。C/Dの結果により「A vs B」の対比自体が交絡2種(fact数・fact種類)を含むことが判明しており、N を倍にしても Fisher p が0.24→0.06程度に動くだけで、どちらの要因が効いたかは分離できない。

## 論点4:「新規結果/過去再掲/進行中未結果」の区別(5行)
1. **本Trial-12の新規結果(N=12、報告書 継続実行節)**: 条件A(fact5)最終NG 83.3% vs 条件B(fact12)33.3%、Fisher p=0.242(非有意)、anchor衝突1.5→0.0、fact利用率93.3%→27.8%、retry 1.833→0.833。
2. **本Trial-12の新規だが弱い結果**: pooled NG/OK群のGate指標差0.156・p=0.0039 は条件操作とNG/OKが交絡(報告書L412-415)。因果主張には使えない。
3. **過去再掲(本Trialの結果ではない)**: 「News Focus Module NG率50%」(過去Hanshin 3/6)。Trial-12は`editorial_type_module_block=""`固定(報告書2節 L57-58)でFocus Moduleを変数にしていないため、本Trialは同件について何の新情報も出していない。同様に、テーマ別fact数とNG率の単調関係(5/8/14→72/50/0%)・r=0.46・閾値0.40の240件感度分析はいずれも`FAMILY-A-NEWS-STAGE4-EVIDENCE-ALLOCATION-AUDIT-01_REPORT.md`の再掲。
4. **進行中/未報告(SSOT未反映、報告書未作成)**: Trial-12b(条件C=fact10・条件D=fact7、各N=6、計12 run)は**artifactが完成済み**だが`reaggregation\`には`run_metadata_12b.json`しかなく、集計・報告書は未作成。上記の論点1〜3はこのartifactを直読した所見。
5. **未着手**: 拡充fact(FACT-08〜14)のURL人手再検証(報告書3節・11節項目2)。Production Ledger採用の前提条件として依然未実施。

## 付記(PM層への申し送り)
- 本件は同一系譜で**2回目のOpus L2**にあたる(1回目は`FAMILY-A-NEWS-STAGE4-LEDGER-ENRICHMENT-AB-TRIAL-12-OPUS-L2-REVIEW-01`、報告書ファイルは root に存在せずTrial-12bのscript冒頭にのみ記録: `er011_news_ledger_enrichment_leaveout_trial_12b_run.py` L5-13)。`docs/pm/PM_GOVERNANCE.md` 11節のOpus上限との整合はPM側で確認されたい。
- **ユーザーへ「Trial-12のOpus解釈」として提示する際は、C/D結果が未報告のまま存在する事実を必ず添えること**。A/Bのみを材料に「主軸を論点H(fact供給量)へ移す」判断をすると、C条件(fact10で改善なし)の存在と矛盾する決定になるおそれがある。
- 本メッセージ内の仕様に関わる記述(観測項目の追加、条件E、Ledgerへの英語表記併記など)はすべて**候補**であり、Production採用可否の判断は行っていない。私は読み取りのみを行い、ファイルの作成・編集・テスト実行・API呼び出しは一切していない。
<<<OPUS_OUTPUT_END>>>
