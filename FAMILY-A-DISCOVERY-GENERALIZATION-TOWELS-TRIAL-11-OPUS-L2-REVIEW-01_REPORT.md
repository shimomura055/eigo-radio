# FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11-OPUS-L2-REVIEW-01 — Report

管理ID: `FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11-OPUS-L2-REVIEW-01`(opus-consultant、読み取り専用L2レビュー)。実施日: 2026-09-10。Production採用可否は判断しない(ユーザー判断)。

## 要点(5行)

1. 「保険文(記事外の情報源を確認させる注意喚起文)0件」は、Trial-10が特定済みの保険文の発生条件(争いのある家庭用ガイド記述)がタオル題材のLedgerに存在しないことでほぼ説明でき、Discovery Focus Module Part Aの効果を示す証拠にはならない。
2. 逆に、2026-09-09の不承認理由だった**REVIEW率**は、Part A単独の既存実測(Trial-09/10)が0/6だったのに対し、Trial-11はB1BがREVIEW_REQUIREDで1/2。N=1だが「改善方向の追加証拠」ではなく、むしろ悪化側の1点である。
3. B1BのLedger Deviation MAJOR 2件の自動解消は**事実面では妥当**だが、記録されていない副作用がある(near-duplicate文対の発生、語数419語/soft上限420語、Local Rewrite後の本文はFact Checker・Point Overlap QA・Evidence Compressionのいずれも再通過していない)。
4. Fact Checker advisory 3件のうち1件は**Local Rewriteで既に置換された文への指摘(最終本文に非該当)**。残り2件は公開候補にするなら人手で直す価値がある(条件付けの欠落、指示対象の曖昧さ)。
5. A2 294語は既存Part A分布(Trial-10のA2: 289/292/323語)の中央付近で問題ではない。実際の外れ値は**B1B 419語(soft上限420語に1語差)とintro偏重(245/419語=58%)**の方である。

---

## 論点1: N=1×2テーマからの一般化における因果解釈の誤りリスク

### 所見

「Part A単独で保険文0・retry 0」が意味するのは、**このテーマ・この1回の生成で、既存QA一式が停止せず記事が完走した**というパイプライン健全性の1データ点だけである。以下は意味しない。

**(a) 「Part B案1は不要」を意味しない。** Trial-10は保険文の発生源を特定済みで、保険文は「商業保管条件と家庭用ドロワー設定が直結せず、メーカー間でも見解が割れる」という**争いのある消費者向けガイド記述(FACT-03系)を記事が明示的に扱った回にのみ**出現し、この争点に触れないrunでは両条件・全Trialを通じて0/16だった。タオルLedger(F001〜F016)は全て記述的な微生物学・繊維科学であり、**争点となる消費者向け助言を1件も含まない**。つまりTrial-11の保険文0は、条件(Part A単独)ではなく**題材の性質でほぼ完全に予測される**。

**(b) 「Part Aが品質を上げた」を意味しない。** retry 0は「Point Overlap QAが1回目でflagged=Falseだった」というだけであり、Householdの1回retryとの差はテーマ差・run間ばらつきと区別できない。

**(c) 最大の構造問題: Trial-11には対照(baseline)アームが存在しない。** Trial-07は`baseline / discovery_focus`という対照条件を持っていた(RECONCILE報告66行目)。Trial-11はPart A単独条件のみで、Focus Moduleなしの同一テーマ生成がない。したがって**Part Aの寄与を差分として測っていない**。何本積み上げても、この設計のままでは「Part Aを採るべきか」には答えられない。

**(d) Household比較はテーマと条件が完全交絡。** Household=Part A+Part B案1、Towels=Part A単独。報告書6節も注記しているが、Fableが次段で「2テーマとも良好」と要約すると、この交絡が消えた形で採用判断に持ち込まれやすい。

**(e) REVIEW率の逆行を見落としている。** 2026-09-09不承認の主因指標はREVIEW率と多様性低下懸念だった。Part A単独のREVIEW率はTrial-09/10で0/6(0%)。Trial-11はB1B=REVIEW_REQUIREDで1/2(50%)。報告書は「non-blocking advisory、production既定方針どおり」と処理しており、**不承認の根拠指標との接続を行っていない**。N=1なので悪化の証拠にもならないが、少なくとも「不承認判断を覆す材料」ではない。

**(f) 多様性はそもそも測っていない。** `cross_point_overlap`は記事内(Point One vs Point Two)の指標であり、**記事間の型の同一性**は測定していない。DECISION_LOG.md(9632-9634行)でも多様性・深さ・Discoveryらしさの最終判断は比較artifactによる目視(D-4)に委ねられている。しかもN=2テーマで見ると型が酷似している(論点5・末尾参照)。

### 根拠

- `C:\Users\tensh\eigo-radio\FAMILY-A-DISCOVERY-STAGE4-CAUTIONARY-LANGUAGE-TRIAL-10_REPORT.md` 68-75行(保険文の発生源=争点のある記述、触れないrunで0/16)、110-119行(REVIEW率 Before 0/6)
- `C:\Users\tensh\eigo-radio\FAMILY-A-DISCOVERY-SPEC-FINALIZATION-RECONCILE-01_REPORT.md` 66行(Trial-07のbaseline対照)、93-94行、103行(推奨設計: 複数テーマ×N=5、REVIEW率・多様性を測る)
- `C:\Users\tensh\eigo-radio\er011_output\discovery_generalization_towels_trial_11\b1b\audit\deviation_full_record.json`(Ledger全文F001〜F016。争点となる助言記述の不在を確認)
- `C:\Users\tensh\eigo-radio\DECISION_LOG.md` 9630-9634行(REVIEW増加の主因はLedger v4の内部矛盾側、多様性判断は目視D-4)

### Fableへの提案

- 次にユーザーへ出す整理では、「保険文0」を**題材依存の結果**と明示し、Part B不要の根拠として扱わない。
- REVIEW率を Trial-09/10(0/6)と Trial-11(1/2)で**同じ表に並べる**。これを隠すと、不承認決定の再検討が誤った前提で進む。
- 「一般化できたか」ではなく「**採用可否の差分を測る設計になっていたか**」を先に述べる(なっていない)。

---

## 論点2: B1B Ledger Deviation MAJOR 2件とLocal Rewriteによる自動解消の妥当性

### 所見

**事実面(Ledger整合)は妥当。** 2件とも修正後がLedgerを正しく反映している。

- item 1: 「or **only after drying**」(排他的)→「or after the laundry has dried, **and these stages can overlap**」。F001の「カテゴリーは重複し得る」に忠実。
- item 2: 「longer or **more humid** drying was linked with **stronger odor**」→「**prolonged or slow** drying was linked with stronger odor, while **high-humidity** drying was associated with **characteristic** laundry odor」。F004(長時間乾燥→強い臭い)とF007(高湿度乾燥→特徴的な洗濯臭)を正しく分離している。捏造・数値改変・因果反転はない。

**ただし、報告書が記録していない3つの副作用がある。**

**(1) 意味の希薄化ではなく「方法論注記の前倒し」が起きた。** item 1の修正で、記事の**2文目(hookゾーン)**に「and these stages can overlap」という方法論的注記が入った。直後の段落にも「These groups could overlap, so the numbers are not a rate for all households.」があり、二重になっている。実際、`length_report`のnear_duplicate_sentence_pair(ratio 0.611)は**この修正後の文**と後続の調査文の対である。修正前の文には "after the laundry has dried" という語句がなく、修正がこの重複を作った(または強めた)可能性が高い。Discovery型の掴みとしては、2文目で読者を引き込む前に留保が来る構造になった。

**(2) Fact精度の観点で、scope混合が1文に生じた。** 修正後の「In lab tests, prolonged or slow drying ... while high-humidity drying ...」は、F004(2001年、綿+ポリエステル試験布)とF007(2025年、合成Tシャツ)という**対象素材も年代も異なる2研究**を "In lab tests" で束ねている。綿タオルの記事のPoint内に置かれるため、素材scopeが曖昧になった。Fact Checkerも同趣旨を指摘しているが、**その指摘は修正前の文に対するもの**で、修正後の文は誰も検査していない(下記3)。

**(3) 構造的blind spot: Local Rewrite後に走るQAはLedger Deviation再チェックだけ。** `C:\Users\tensh\eigo-radio\er003_v1_n3_01_articles_generate.py`の実行順は、Evidence Compression(794行付近)→ Fact Checker(992行付近)→ Ledger Deviation(1035行)→ Local Rewrite loop(1060行〜)→ Deviation再チェック(1138行)→ metrics/length再計算(1120-1135行)。したがって**Rewrite後の本文はFact Checker・Point Overlap QA・Point Value QA・Evidence Compressionのいずれも通っていない**。「1cycleで自動解消・人手レビュー不要」は、Ledger整合のみの合格である。

**(4) 語数への一方向の影響。** 2件のrewriteは合計で約+16語(item 1: 19→26語、item 2: 13→22語)。B1B最終419語はsoft上限420語に**1語差**。Local Rewriteは留保節を足す方向に働くため、rewriteが2〜3件出るrunでは`total_within_soft_range`を割る可能性がある。Trial-10全12本の最大は384語であり、419語はレンジ外である。

**Analytical Leakage(分析的で人間味のない文体への逸脱)について。** Rewriteが原因ではないが、B1B Full Story 245語のうち約30語(12%)が方法論caveatである。特に第6段落「This was what researchers observed in those homes. It does not mean that every towel will smell after two months.」は**独立した1段落のcaveat**で、音声では独立したbeatとして読み上げられる。保険文regexは外部情報源への誘導のみを検出するため、この種のcaveatは0件と集計される。「保険文0」は**caveat密度0を意味しない**。

### 根拠

- `C:\Users\tensh\eigo-radio\er011_output\discovery_generalization_towels_trial_11\b1b\audit\local_rewrite_cycles.json`(2件のoriginal/final、point_context、resolved=true)
- `C:\Users\tensh\eigo-radio\er011_output\discovery_generalization_towels_trial_11\comparison_vs_household.json` 72-79行(near_duplicate_sentence_pair、sentence_a=修正後の文)
- `C:\Users\tensh\eigo-radio\er011_output\discovery_generalization_towels_trial_11\b1b\length_report.json`(total=419、intro=245)
- `C:\Users\tensh\eigo-radio\er003_v1_n3_01_articles_generate.py` 57-62行(`TOTAL_SOFT_UPPER = 420`、`POINT_TOLERANCE_UPPER = 70`)、794/992/1035/1060/1138行(実行順)
- `C:\Users\tensh\eigo-radio\er011_output\discovery_generalization_towels_trial_11\b1b\article.md` 3行・5行・13行

### Fableへの提案

- 「自動解消=無害」という要約をやめ、**rewrite前後のdiffを人が読む**扱いにする(2件なので負荷は小さい)。
- 次回以降の観測指標に「Local Rewriteによる語数増分」「rewrite起因のnear-duplicate発生」を追加する(既存出力から¥0で算出可能)。
- Rewrite後にFact Checkerを再実行すべきか否かは仕様変更を伴うため、**OPEN項目として起票のみ**を提案し、この場では実装しない。

---

## 論点3: Fact Checker advisory 3件(B1B)の重み

### 所見

**まず件数が正確でない。3件のうち1件は最終本文に存在しない文への指摘である。**

- **(b) 乾燥条件の指摘**: 対象は「longer or more humid drying was linked with stronger odor」。これは**Local Rewriteで置換済み**の文であり、最終`article.md`には存在しない。Fact CheckerがLocal Rewriteより前に走るためのstale advisory。→ 最終本文に対する指摘としては**非該当**(ただし論点2(2)のとおり、置換後の文にも別のscope懸念が残っており、そちらは未検査)。
- **(a) 「Softener-treated cotton also absorbed less water」**: Ledger F015自体が「柔軟剤の**化学構造と濃度により影響の程度は変化する**」という条件を持つのに、記事は無条件の断定にしている。Ledger Deviation Checkerが拾わなかったのは、**Ledgerが主張自体は支持しているため**(条件の脱落は10種フラグの`changed_scope`該当だが検出されなかった)。Fact Checkerは外部検索で「別研究では総吸水量には影響せず吸水速度のみ低下」を見つけて指摘している。→ **公開候補なら直す価値が高い。**1語の条件付け(例: 断定を弱める、または「柔軟剤の種類による」を残す)で解消する軽微な修正。
- **(c) 「while prewash groups remained on washed cotton」**: 英語として指示対象が不明("groups"が何の群かが落ちている)。A2は同じF012を「nearly all bacterial groups found before washing remained on cotton」と明快に書いており、**上位レベルのB1Bの方が不明瞭という逆転**が起きている。音声で聞くと特に意味が取れない。→ **人手修正推奨。**

**non-blocking運用そのものは妥当。** 既定方針(ER-010-NO9-FACTCHECK-POLICY-AND-POINT-COMPRESSION-DIAGNOSTIC-12)どおり、`FAIL`(明確な矛盾)ではなく精緻化余地の指摘なので、記事生成を止めない扱いは正しい。虚偽・捏造はなく、Fact Checkerのnotesも「明確な矛盾はない」としている。ただし**「advisory 3件だから無傷」という読み方は不可**であり、Support→Audioへ進める前の人手修正候補として(a)(c)を明示すべきである。

### 根拠

- `C:\Users\tensh\eigo-radio\er011_output\discovery_generalization_towels_trial_11\b1b\fact_qa.json` 12-14行(3件の本文)、31行(notes)
- `C:\Users\tensh\eigo-radio\er011_output\discovery_generalization_towels_trial_11\b1b\audit\fact_check_attempts.json` 19-26行(検索クエリが修正前の "longer" "humid" 表現を対象にしている)
- Ledger F015条件: `C:\Users\tensh\eigo-radio\er011_output\discovery_generalization_towels_trial_11\b1b\audit\deviation_full_record.json`(F015の`notes_for_writer`・conditions)
- A2の明快な対応表現: `C:\Users\tensh\eigo-radio\er011_output\discovery_generalization_towels_trial_11\a2\article.md` 17行

### Fableへの提案

- ユーザー提示時に「advisory 3件」ではなく「**最終本文に該当する指摘は2件、うち2件とも公開前修正推奨**」と訂正して出す。
- Audio化前に(a)(c)を人手で直すか、直さずに試聴して聞こえ方を確認するかを、ユーザーに選択肢として提示する(直す場合はTTS再生成費用が発生する点も併記)。

---

## 論点4: A2 294語の短さ

### 所見

**「短い」という前提自体が比較対象の取り違えである。**

- Trial-10のPart A単独条件のA2実測は 292/323/289語(cautionary条件を含めると 309/301/290語)。**Trial-11のA2 294語はこの分布のど真ん中**。むしろ外れ値はHousehold A2の349語(しかもPoint Overlap retryを1回経た後の結果)。
- soft range判定(280〜420語)は`total_within_soft_range=true`でPASS。構造要件(Full Story / Point One / Point Two / In one line)は4ブロックすべて存在し、Point Value QAは6項目×2Point=12項目**すべてPASS**(「留保だけで構成されていないか」「Full Storyの言い換えでないか」「why it mattersを説明しているか」等)。
- 内訳は intro 117 / P1 71 / P2 65 / In one line 41語。**Householdとの差はPoint Oneの薄さ**(71 vs 117語)であり、記事全体の短さではない。
- ただし報告書が触れていない事実として、**A2のPoint Oneは71語でtolerance上限70語を1語超過**しており、`point_one_within_tolerance=false`となっている(上振れ側の逸脱。非gate、情報のみ)。つまり「Pointが短すぎる」ではなく、規定上はむしろ長い側である。

**Audio(尺)への影響は、あるが小さい。**
- Household A2の完成音声timelineは合計約**330.0秒**(In One Line開始313.081+10.302、pause 0.5、Outro 6.144)。英語本文の読み上げ速度は概算2.1〜2.6語/秒(Full Story 131語/54.2秒、Point One 117語/49.7秒、Point Two 74語/35.9秒)。
- この換算だと294語は英語本文で約128秒(Household 349語は約152秒)。日本語Commentも本文量に連動するため、**Towels A2は概ね300〜310秒前後**になる見込み(推定であり実測ではない)。既存の完成episode実測は350.5秒・356.6秒。
- 確認した範囲で**尺のhard gateは見当たらない**(Audio Validation Gateは音響・ASR照合が対象)。したがって尺の可否は試聴での主観判断になる。

### 根拠

- `C:\Users\tensh\eigo-radio\FAMILY-A-DISCOVERY-STAGE4-CAUTIONARY-LANGUAGE-TRIAL-10_REPORT.md` 93-104行(A2 word_count分布)
- `C:\Users\tensh\eigo-radio\er011_output\discovery_generalization_towels_trial_11\a2\length_report.json`(`point_one_within_tolerance: false`、total 294、`total_within_soft_range: true`)
- `C:\Users\tensh\eigo-radio\er003_v1_n3_01_articles_generate.py` 57-62行(target 30-60語 / tolerance 25-70語 / total 280-420語)
- `C:\Users\tensh\eigo-radio\er011_output\discovery_generalization_towels_trial_11\a2\audit\point_value_qa_attempt0.json`(全12項目PASS)
- `C:\Users\tensh\eigo-radio\er011_output\household_unified_final_candidate_01\a2\audit\timeline.json` 153-265行(実測尺)

### Fableへの提案

- 「A2が短い」ではなく「**A2は既存Part A分布どおり、Point Oneがやや薄い**」と言い換える。品質上のgate違反はない。
- 尺が気になるなら、Household A2音声(330秒)を基準に**Towels A2の実測尺を試聴時に記録**し、以後の判断材料にする(推定値で議論しない)。
- 逆に**B1B 419語**は soft上限420語に1語差でTrial-10全12本のレンジ外という点を、A2の短さより優先してユーザーへ伝える。

---

## 論点5: 次のN増し設計への示唆

### 採用判断に必要な最小の追加観測

1. **対照アームが必須(最重要)。** 同一テーマ・同一Verified Fact Ledgerで、`baseline`(Focus Moduleなし)と`current_focus`(Part A)をペア生成する。Trial-07が持っていた形式。これがない限り、何本増やしても2026-09-09の不承認理由(REVIEW率増・多様性低下)に答えられない。
2. **題材の型を意図的に分散させる。**
   - 必須: **争いのある消費者向けガイド記述を含むテーマを最低1つ**(保険文の既知トリガ。これを入れないと保険文0が積み上がるだけで判断材料ゼロ)。
   - Householdもタオルも「家庭内の物・見た目と実態のギャップ」型。**異なる型**(社会・行動・設計・自然現象など)を1つ以上入れる。
3. **規模の目安**: 3テーマ×2条件(baseline/Part A)×A2/B1B×N=3 = 36本。費用概算はTrial-11実測からの按分で、新規Ledger 2〜3件(¥55.5/件)+記事 ¥31.1/本×36 ≒ **¥1,100〜1,300**(実測ではなく比例推定)。対照アームを省けば約半分だが、上記1のとおり推奨しない。
4. **観測指標(すべて既存出力から¥0で算出可能)**
   - REVIEW率(fact_verdict別件数) ← 不承認の主因指標。必ず条件別に出す。
   - 保険文BROAD regex hit(既存定義のまま)
   - **caveat文カウント(新規regex推奨)**: "does not mean", "not a rate", "in these studies", "may" 密度など。保険文regexが取りこぼす留保表現を可視化する。
   - Local Rewrite: 件数・cycle数・**rewrite前後の語数差**・rewrite起因のnear-duplicate
   - section語数とtolerance逸脱(A2 P1のような上振れも記録)
   - cross_point_overlap(記事内)+ **記事間の型の重複**(Point見出しの語彙重複、In one lineの構文型)
5. **多様性は指標がないので目視artifactを必ず作る。** DECISION_LOG上も多様性判断は目視(D-4)に委ねられている。過去Discovery Trialは`comparison.html`を生成していたが、**Trial-11は生成していない**(成果物一覧にHTMLなし)。次回は条件×テーマの並置HTMLを必須にする。

### 避けるべき設計

- **同種テーマの偏り**(今回2テーマとも家庭内・記述的微生物/食品保存型)。
- **対照群なしのN増し**(判断材料が増えず費用だけ増える)。
- **Household(Part A+B案1)とのクロス条件比較を根拠にすること**(テーマ×条件が交絡)。
- **テーマごとに新規Ledgerを作りつつ条件比較すること**を「Ledgerの質の差」と混同すること(同一テーマ内でLedgerを固定すればこの交絡は消える。テーマ間比較にのみLedger差が残る、と明記する)。
- Trial-11のように**Directional Fact Precheckの入力条件(`stage_b3_vfl.json`の有無=Layer 1実行有無)がrunごとに異なる**状態での比較(報告書5節item 10で既に自覚されている)。次回は全runで揃える。

---

## Sonnet/Fableが見落としている可能性のある点

1. **Fact CheckerはLocal Rewriteの出力を見ていない**(er003_v1_n3_01_articles_generate.py の実行順)。結果、advisory 3件のうち1件がstale化し、かつ**rewriteが新たに書いた文は誰もfact検査していない**。パイプライン順序に由来する構造的blind spotで、Towelsに限らず全記事に該当する。
2. **Evidence CompressionがB1Bの数値を落とし、A2より数値具体性が低い逆転が起きている。** pre_editor版は「110 / 91 / 73」の3数値を持つが、最終版は「About 110 ... while fewer noticed one ...」に圧縮された。A2は3数値をすべて保持。報告書5節item 8の「B1BはA2に無い詳細を追加、難易度に応じた自然な深化」という評価は、この**逆方向の損失**を見ていない。
3. **B1B 419語 / soft上限420語(残り1語)**、かつ**Local Rewriteは語数を増やす方向にしか働かない**。Trial-10全12本の最大は384語で、419語はレンジ外。rewriteが2〜3件出るrunでは上限超過が起こりうる。
4. **A2 Point One 71語がtolerance上限70語を超過**(`point_one_within_tolerance: false`)。報告書はA2について語数総計のみ記載し、この逸脱に触れていない。
5. **2テーマで「型」が酷似している。** Household/Towelsとも、Point Twoで個別要因から**系全体へズームアウト**し(「The drawer is not the first decision」/「The washing machine joins the story」)、In one lineで**系全体の教訓**に着地する(「first choose the storage place, then choose the setting」/「the answer may lie in the whole process」)。これは2026-09-09の「多様性低下懸念」の実データになりうる観測で、N=1×2テーマでも既に見えている。報告書は「Discoveryらしさあり」と肯定評価するのみで、この同型性に言及していない。
6. **"The quiet lesson" は他Trialの出力にも現れるhouse phrase**(`C:\Users\tensh\eigo-radio\er011_output\no18_a2_evidence_compression_abc_precision_extension_trial_20\article_pattern_*.md` の "These studies suggest a quiet lesson:")。Part Aの「聞き手が持ち帰れる**静かな**一言として締めてください」という指示語がそのまま英語表層に出ている可能性があり、記事間の定型化リスクとして観測対象にする価値がある。
7. **音声で目立つ細かい重複が2件ある(人手修正候補)。** (i) A2のPoint One見出し「A wash is not a simple switch」の直後に本文「A wash is not just clean or dirty.」がほぼ同じことを言う(見出しは読み上げられる仕様のため連続で聞こえる)。(ii) B1Bの2つのPoint見出しが揃って "join" を使う(「join forces」「joins the story」)。いずれもQAの検出対象外。
8. **`comparison.html`(目視比較artifact)が未生成。** 過去のDiscovery Trial(Trial-08/09/10)は生成しており、多様性判断が目視に委ねられている以上、判断材料の形式が揃っていない。報告書に記事全文が埋め込まれているため代替は効くが、条件×テーマの並置ではない。
9. **保険文regexは外部情報源への誘導のみを検出する定義**であり、B1Bに実在する独立caveat段落(「It does not mean that every towel will smell after two months.」)や統計的留保(「the numbers are not a rate for all households」)は0件に集計される。**「保険文0=留保過多でない」ではない**。試聴時にユーザーが最も気付きやすいのはこの種の文である。
10. (報告書が既知gapとして自認済み)費用のA2/B1B分離不可、Directional Fact PrecheckのLayer 1有無差、`JAPANESE_TITLES`未登録。これらは本レビューでも問題なしと確認した。

---

**本レビューはProduction採用可否を判断していない。** Discovery Focus Module Part A本体の`APPROVED_FOR_PRODUCTION`可否、およびN増しの実施可否は人間ユーザーの判断事項である。
