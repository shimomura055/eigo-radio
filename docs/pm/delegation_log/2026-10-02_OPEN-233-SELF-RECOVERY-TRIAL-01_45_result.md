<!-- 抽出元transcript: agent-adde5e36bfe4009ab.jsonl(subagents配下。指定の.outputは0バイトで抽出不能だったため同内容のsubagent transcriptを使用)。抽出日時: 2026-10-02T21:37:24。本文(最後のassistantメッセージ)は改変していない。 -->

# 委任_45 報告: Checker引用の特定不能35件の原因分類・対策設計・Prompt変更の効果見積もり

(read-only分析。コード・SSOT・設計書・ACTIVE_TASK・RESULT_PACKETは未編集、git add/commit/pushなし、LLM呼び出しなし、¥0)

## 1. 結論(10行以内)

1. 35行(13種類、32 run)を目視で分類した。内訳は **C1(言い換え)0行、C2(句読点差)22行/3種類、C3(説明文混在)12行/9種類、C4(省略記号の中略)1行/1種類、C5 0行**。委任_41の「言い換え・要約21行」は類似度による診断の誤りで、実体はC2(文を節の途中まで引用し、末尾の句読点を替えただけ。語は一字も違わない)。
2. 22行(C2)は、Checker文字列の末尾の句読点を除くだけで記事内ちょうど1箇所に一致する(20行は固定fixture1件の再生)。Promptなしで解消でき、文字単位の同値変換として扱える見込み。
3. 12行(C3)は断片そのものは全て逐語で、混入しているのは位置ラベルやChecker自身の説明文だけ。ただし説明文が**未引用の別箇所(見出し・in one line)を指す**例が2種類あり、断片だけ採ると範囲を縮める。受け取り側だけでは解消できない。
4. 影響で重要なのは件数より中身。現行の対象が意図と一致していたのは24行(C2・C4中心)。**C3の10行は複数箇所のうち1箇所しか直せておらず(目視)、7行がStage 4、3行は降格で終了**。次周回で取りこぼした箇所を同factで再指摘した例が多い(§3)。
5. 新方式(確定不能=人間確認)にすると、現行解消の22 runが人間確認へ回る。C2の同値変換を入れると**22→4 run**(U02の3 run+U05の1 run)。
6. 直近(rep17〜21、iter8)の確定不能は0件(strict)。借用本文の補助集計で、最新29件横断(iter8 s1)に1行(U02、固定fixture)が出る程度。
7. 実LLMのCheckerが返した8行(Recheck)は全てC3。固定fixture由来の27行とは性質が違い、独立なChecker出力は13種類のみ。
8. Prompt変更の必要性は**中程度**。C3(複数箇所)の取りこぼしに対応する唯一の手段だが、直近の発生は0件。**委任_42の限定Trialと29件横断の再確認を見てから判断**を推奨。
9. 設計案は、Trial専用追記だけで`violation_spans`(文字列配列)を**唯一の情報源**にするD-2を推奨(Opus #5の二重化回避を満たす)。Prompt文案は§5。逐語化の効果は**見積もりであり実測ではない**。前例(`same_fact_id_locations`)は明示指示でも約6%逸脱した。
10. 実装前に、Checker出力契約の変更としてOpus独立レビュー(条件A)が必要。ユーザーSTOP条件への該当は現時点でなし(§7)。

## 2. A: 原因分類

### 2-1. 13種類の表(Checker文字列は逐語、〔〕は私の注記)
各行の末尾は「行数/run数・記事・言語・段階」。「固定fixture再生」は固定Stage 1出力の再利用で、独立サンプルではない。

**U01** `“A call came from an AI agent. That was what it seemed. But while the conversation continued, the voice on the other end was not AI. It was a person.” Meta’s test “produced exactly this kind of surprise.”`
- 記事: 冒頭段落「Ring, ring... A call came from an AI agent. That was what it seemed. But while the conversation continued, the voice on the other end was not AI. It was a person.」と次段落「Meta had run a test that produced exactly this kind of surprise.」
- 差分: 断片2つとも逐語で各1箇所。間のChecker自身の語「Meta’s test」だけが記事にない。言い換えなし。
- 区分: **C3b**(説明文+断片2つ以上)、副C4(隣り合う2段落の結合)。
- 1行/1 run、bgroup_B4(iter5 s1)、EN、Recheck cycle2(実出力)。

**U02** `“people who thought they were speaking with AI were actually speaking with human staff”および冒頭の「That was what people thought as they spoke.」`
- 記事: 「So people who thought they were speaking with AI were actually speaking with human staff.」と冒頭「An AI called. That was what people thought as they spoke.」
- 差分: 断片2つとも逐語で各1箇所。つなぎが日本語の「および冒頭の」(=接続語+位置語)で、英語の引用に日本語が混入。
- 区分: **C3b**、副C4(離れた2箇所)。
- 4行/4 run(iter5 s1・s2、iter6 s1・s2)、safety_A4、EN(つなぎのみJA)、Stage 1初回(固定fixture再生)。

**U03** `“Trump’s proposed Hormuz fee vanished overnight.”`
- 記事(in one line): 「Trump’s proposed Hormuz fee vanished overnight, but crude oil prices stayed high as tensions and tanker fears remained.」
- 差分: 「overnight」で止め、読点を引用符内のピリオドに替えた。末尾句読点のみの差。
- 区分: **C2**(文の途中で終了を伴う)。
- 1行/1 run、bgroup_B2_hormuz(iter5 s2)、EN、Stage 1初回(固定fixture再生)。

**U04** `Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14, so the flashy 20% plan left the stage.`
- 記事(in one line): 同文が「…left the stage, but the chart only pulled back briefly before recovering: …」と続く。
- 差分: 「left the stage」で止め、読点をピリオドに替えた。
- 区分: **C2**。
- 1行/1 run、bgroup_B3(iter5 s2)、EN、Stage 1初回(固定fixture再生)。

**U05** `“attacks by the United States and Iran ... continued”`
- 記事: 「At the same time, attacks by the United States and Iran, a sea blockade, and concerns about tanker safety continued.」
- 差分: 「...」が「, a sea blockade, and concerns about tanker safety」を省略(同一文内)。前後の断片は逐語だが、「continued」単独は記事内に2箇所ある(診断: 前断片1箇所+後断片2箇所)。
- 区分: **C4b**(省略記号で中略)。
- 1行/1 run、hormuz_run03_advanced(iter5 s2)、EN、Stage 1初回(固定fixture再生)。

**U06** `“That was what people thought as they spoke.” The opening also presents the call as one people believed was from an AI.`
- 記事: 冒頭「An AI called. That was what people thought as they spoke. But a human appeared from behind the scenes.」
- 差分: 断片は逐語で1箇所。続く文はChecker自身の説明文(記事の文ではない)。「also」「The opening」が、断片より広い冒頭段落全体を指している可能性がある。
- 区分: **C3a**(説明文+断片1つ)。
- 1行/1 run、safety_A4(iter5 s2)、EN、Recheck cycle2(実出力)。

**U07**(20行) `Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14, so the flashy 20% plan left the stage, but the chart only pulled back briefly before recovering.`
- 記事(in one line): 同文が「…before recovering: the policy turn and the oil chart’s “not over yet” movement happened on the same day.」と続く。
- 差分: 「recovering」で止め、コロンをピリオドに替えた。要約ではなく、記事文の逐語の前半+句読点替え。
- 区分: **C2**。
- 20行/20 run(iter6・iter7・rep7〜13・rep16の各s1・s2)、bgroup_B3、EN、Stage 1初回(固定fixture再生で、独立なChecker出力は1件)。

**U08** `The headline says “I Thought It Was an AI Call—But There Was a Person Inside?” and the opening says, “A call came from an AI agent. That was what it seemed.”`
- 記事: 見出し「# I Thought It Was an AI Call—But There Was a Person Inside? Meta’s Unexpected Muse Test」の前半と、冒頭「A call came from an AI agent. That was what it seemed.」
- 差分: 断片2つとも逐語で各1箇所。説明文は位置ラベルのみ(The headline says / and the opening says,)。
- 区分: **C3b**、副C4(見出しと冒頭)。
- 1行/1 run、bgroup_B4(iter6 s1)、EN、Recheck cycle3(実出力)。

**U09** `“Meta had run a test that caused exactly this surprise,” reinforced by the headline “We Thought It Was AI—But There Was a Person Inside Meta’s Muse.”`
- 記事: 「Meta had run a test that caused exactly this surprise.」と見出し「# We Thought It Was AI—But There Was a Person Inside Meta’s Muse」(見出しに末尾ピリオドなし)。
- 差分: 1つ目は読点を引用符内に付加、2つ目は記事にない末尾ピリオドを付加。つなぎ「reinforced by the headline」は説明文。
- 区分: **C3b**、副C2(2断片とも末尾句読点が差)。
- 1行/1 run、neg1_meta_b3prod_a2(iter6 s1)、EN、Recheck cycle2(実出力)。

**U10** `Headline: “We Thought It Was AI—But There Was a Person Inside Meta’s Muse.”`
- 記事: 見出し全文と一致(末尾ピリオドなし)。
- 差分: 位置ラベル「Headline:」と末尾ピリオドの付加。ラベルが指す範囲は断片と同じ見出し全体。
- 区分: **C3a**(位置ラベル+断片1つ)、副C2。
- 1行/1 run、neg1_meta_b3prod_a2(iter6 s1)、EN、Recheck cycle3(実出力)。

**U11** `“Oil prices moved briefly, then returned to a high level.” The headline and one-line summary also state this more broadly as a claim about oil prices generally.`
- 記事: 本文「Oil prices moved briefly, then returned to a high level.」、見出し「The Fee Plan Leaves, But High Oil Prices Stay」、in one line「The fee plan vanished, but oil prices stayed high as tensions around the Strait of Hormuz continued.」
- 差分: 断片は逐語で1箇所。説明文が見出しとin one lineの2箇所を**引用せず位置だけ**で指す。同指摘の`same_fact_id_locations`には両箇所の逐語文が入っていた(別欄なら逐語で返せている)。
- 区分: **C3a**、副C4(未引用の追加箇所)。
- 1行/1 run、hormuz_run03_standard(iter7 s2)、EN、Recheck cycle2(実出力)。

**U12** `“Oil prices moved briefly, then returned to a high level”; “oil prices stayed high” (also reflected in the headline).`
- 記事: 本文の同文(ピリオドを除いた部分)と、in one line内「oil prices stayed high」。
- 差分: 断片2つとも逐語で各1箇所。「(also reflected in the headline)」は未引用の見出しを指す説明文。
- 区分: **C3b**、副C4。
- 1行/1 run、hormuz_run03_standard(rep9 s1、cycle2、k=1)、EN、Recheck(実出力)。

**U13** `“High Oil Prices Stay” (headline); “oil prices stayed high” (one-line summary).`
- 記事: 見出し「The Fee Plan Leaves, But High Oil Prices Stay」の末尾と、in one line内「oil prices stayed high」。
- 差分: 断片2つとも逐語で各1箇所。括弧内の位置ラベルは実際の位置と一致。
- 区分: **C3b**、副C4。
- 1行/1 run、hormuz_run03_standard(rep9 s1、cycle3)、EN、Recheck(実出力)。

### 2-2. 区分別の件数(行/ユニーク)
| 区分 | 行 | ユニーク | 該当 |
|---|---|---|---|
| C1 言い換え | 0 | 0 | なし |
| C2 大小文字・句読点 | 22 | 3 | U03、U04、U07 |
| C3 説明文混在 | 12 | 9 | C3a(断片1つ+説明文・位置ラベル)3行/3種類=U06・U10・U11、C3b(断片2つ以上+説明文)9行/6種類=U01・U02・U08・U09・U12・U13 |
| C4 複数箇所の結合 | 1 | 1 | U05(省略記号)。副区分としてC3の6種類(U01・U02・U08・U11・U12・U13)にも該当 |
| C5 その他 | 0 | 0 | なし |
| 合計 | 35 | 13 | 主区分の合計は検算一致 |

副区分はC4が6種類、C2が2種類(U09・U10)。

### 2-3. 委任_41の内訳との差
- 「言い換え・要約21行」は実体がC2(U07 20行+U04 1行)。類似度が高かったのは、前半が逐語一致する文だったため。
- 「その他1行」(U03)もC2。
- 説明文混在12行(断片2つ以上+説明文9、断片1つ+説明文3)、省略記号1行は一致。
- C1(語の置換・要約・翻訳)は、この35行には**1件もない**。

### 2-4. 参考(件数のみ)
- **非BLOCKINGの確定不能7行**: C1が1(「The price movement…」は記事の「But its price movement…」の冒頭語を置換)、C2が1(「Crude oil also passes through it.」は記事が「…it, so trouble…」と続く)、C3が5(5行とも断片は逐語。位置ラベルや説明の括弧、「also,」等が混在)。
- **K2で捨てられた`same_fact_id_locations`14件**:
  - C3が9(位置のみ「Paragraph 5」「Paragraph 7」2、位置+断片7)。
  - 位置ラベルを引用した3件(`“In one line”`単独1、`“In one line”: “…”`2)は、現行L1/L4で**見出しの文字列に一致して「確定」扱いになる**(誤って見出しを範囲にしかねない)。Opus論点。
  - 残り2件は、有効な日本語文1と、引用符付きで逐語の英語1。

## 3. B: 影響の実態

**現行の最終結果(32 run)**:
- 解消(RESOLVED_REWRITE)18、解消+降格(RESOLVED_REWRITE_THEN_DOWNGRADE)4、Stage 4が10。
- 記事別は、B3 21 run、safety_A4 4、hormuz_run03_standard 2、B4 2、neg1 1、B2_hormuz 1、hormuz_run03_advanced 1。

**現行の対象が意図と一致していたか(目視、各行の書き換え前後の差分と次周回の再指摘で判定)**:
- 一致24行: C2のU03・U04、C4のU05、C3のU06(広め)、U07の20行。U07は「so」の文が直されており、issueが「so」を明記しているので一致。
- 一部のみ10行(7種類): 複数箇所のうち**1箇所しか直していない**。
  - U01は冒頭段落のみ。
  - U02(4行)は本文の文のみで、冒頭が未修正。4/4 runで次周回に冒頭を同fact(MUSE-HC-012)で再指摘した。
  - U08は冒頭のみで、見出し未修正。
  - U09は1つ目のみで、次周回で見出しだけが単独で再指摘された。
  - U11は見出しが未修正。
  - U12は本文のみで、次周回でin one lineと見出しが再指摘された。
  - U13はin one lineのみで、見出しが未修正。
- 判定不能1行: U10。最終周回で書き換え未実行(cycle_limit_exhausted)。
- 一部のみ10行の最終状態は、Stage 4が7行、降格で終了が3行(U02)。**一致した24行のうち、Stage 4の4行はJA側の別原因(ja_deviation_unresolved、rep11・rep12のB3)**。
- Stage 4の10 runは、複数箇所の取りこぼし関与が6、JA側が4。
- この対応は、取りこぼしと結果の関連であり、因果の証明ではない。

**人間確認へ回るrun数**:
- 新方式(確定不能=人間確認)のままなら、現行解消の22 run(18+4)が人間確認へ回る(委任_41と一致)。
- C2の同値変換を入れると、人間確認が増えるのは**4 run**(U02の3 run+U05の1 run)。U05の中略規則も入れれば3 run。
- Stage 4の10 runは現行から変わらない。

**時期別**:
- iter5〜7(古い固定データ中心): 17行/15 run。
- rep7〜16: 18行/17 run。
- rep17〜21とiter8は**0件**。最新29件横断(iter8 s1)も0件。
- 借用本文の補助集計(同一fixtureのcycle1本文を借用、主集計外)では、iter8 s1のsafety_A4(U02、固定fixture)が1行加わり36行になる。

**独立性**:
- 固定fixture再生が27行(独立なChecker出力は5種類)、Recheckの実出力が8行(8種類)。
- 実出力のRecheckで確定不能が8/58=13.8%。8行は全てC3。

## 4. C: 原因ごとの対策比較

線引き: 文字単位の同値変換=Checkerが書いた文字そのものを、記法の差だけ吸収して照合すること(書いた語を落とす・足すことは含まない)。再推測=似ていることを根拠に範囲を選ぶこと、または書かれていない範囲を補うこと。

| 区分 | (i)機械的照合 | (ii)Prompt出力形式 | (iii)Checker返し直し | (iv)人間確認 |
|---|---|---|---|---|
| C2(22行/3種類) | **可(同値変換)**。両端の句読点`. , ; : ! ? 。、`を除いて記事内ちょうど1箇所一致。診断で3/3種類、U07は20/20行で1箇所。範囲は文の途中までの節になるので、Opus #5の文単位スナップを併用。副作用: 短い断片は多箇所一致→不一致扱い(安全側) | 見込める(癖)。ただし(i)で足りるので不要 | 不要 | 不要。22行の人間確認増を0にできる |
| C3a 断片1つ+説明文(U06・U10・U11) | **不可**。断片だけだと説明文が指す広い範囲を縮める(U06は段落全体の可能性、U11は未引用の2箇所)。U10だけは断片=見出し全体で縮まないが、一般化できない | 配列で返させれば解消見込み。U11は他2箇所を別要素で返す必要(別欄では返せていた) | 可。+1call。説明文を除き逐語のみで返し直させる | 既定。件数は少ない(3種類) |
| C3b 断片2つ以上+説明文(U01・U02・U08・U09・U12・U13) | 位置ラベルだけのU02・U08・U13は2断片を確定できるが、ラベル語彙の判断が必要で再推測寄り(Opus #5 修正案1は「つなぎ語・句読点のみ」に限定)。U01(Meta’s test)・U09(reinforced…)・U12(未引用の見出し)は不可 | **見込める(中〜高)**。断片は全て逐語なので、足りないのは「つなぎを入れず別要素に分ける」という指示だけ | 可。+1call、非決定 | 既定。9行/6種類 |
| C4 省略記号(U05) | 条件付き可。「A ... B」を「Aの先頭〜Aの後の最初のBの末尾」と読む標準解釈で、同値変換とは言い切れない(Opus判断) | 見込める(1件のみ、確度低) | 可 | 既定 |
| C1(実測0行。参考で非BLOCKINGに1行) | 不可(言い換えは再推測) | 見込める | 可 | 既定 |

(iii)の注意:
- 別AIの引用による救済(ユーザー不採用)とは異なり、同じChecker自身への再依頼。
- 追加call(+1)と費用が発生する。過去実測の`stage1_recheck`は平均¥0.32(n=298、中央値¥0.27、最大¥0.96)、設計書記載の¥0.526(n=10)を上限の目安とする。
- 再出力も揺れる(非決定)。
- 効果は未測定。

検出漏れ・false PASS・出力失敗への副作用:
- (i)は対象特定だけで判定には触れず、増えるリスクなし。
- (ii)(iii)は出力形式を変えるため、検出が揺れうる(§5)。

## 5. D: 逐語Prompt変更の効果見積もりと設計案

### 5-1. 前提の確認
- 現行Checkerの`DEVIATION_PROMPT_TEMPLATE`(er003 502〜541)は、`claim_in_article`の書き方に**一切指示がない**(schema 464行も単なる`{"type": "string"}`)。13.4%はこの状態の数値。
- 本Prompt末尾は「厳密な文言一致は求めません」(Ledger対記事の話)で、引用の逐語化とは別の話だが、追記で明記しないと混同する恐れがある。
- Recheckで使うTrial追記(er051 V4Aブロック)は「前後1〜2文の限定語」まで見るよう指示している。Checkerが引用と注釈を同じ文字列に混ぜる癖(`qualifier_text`も「引用+括弧の説明」)と整合する。仮説であり測定していない。
- Trial専用の追記は、runnerの`SAME_FACT_ID_ENUMERATION_INSTRUCTION`(1119〜1126)・`build_deviation_schema_with_enumeration`(1129〜1135)・`build_recheck_schema`(1468〜)・`run_recheck`(1499〜1508)と同じ手口で、er003・Production pathに触れずに実現できる(設計書§2-1の確認と一致)。

### 5-2. 解消が見込めるか(見積もり。実測ではない)
- **見込める**:
  - U01、U02、U08、U09、U12、U13(断片は全て逐語で、混入物はつなぎ・位置ラベルのみ)。
  - U03、U04、U07(C2。ただし(i)で足りるので不要)。
  - U10(位置ラベルのみ)。
- **条件付き・不明**:
  - U06: 範囲が冒頭の1文か段落全体かをCheckerが選び直す必要がある。
  - U11: 他2箇所を同じ欄で逐語に返せるか未測定(別欄では返せていた)。
  - U05: 1件のみで確度が低い。
- **見込みにくい**: 今回の13種類には「特定の1文に定まらない含意だけの指摘」はなかった。ただしU06・U11は範囲が曖昧な型に近い。逐語を強制したとき起こりうることは3通り。(a)1文だけ選ぶ→範囲が縮み、次周回で再指摘(現行と同じ)。(b)段落全体を引用→書き換え量が増える。(c)指摘自体を控える→**検出漏れ**。
- 前例(`same_fact_id_locations`は「exact verbatim substring」と明示したのに`"Paragraph 7"`等を返した):
  - 採用213に対し14件逸脱で約6%(重複を除いた近似)。
  - 14件は全て位置の説明や位置ラベルで、rep19〜21の実出力側に集中する。
  - 構造化出力でも逐語率は100%にならない前提で、受け取り側の完全一致照合は必須。

### 5-3. 設計案の比較
| 案 | 内容 | 単純さ | 既存コードへの影響 | 検出への影響リスク | 固定fixture互換 |
|---|---|---|---|---|---|
| D-1 | `claim_in_article`の書き方だけ指定(単一文字列)。複数箇所は表現できない。改行区切り規約(D-1b)は、区切り記号を守らない恐れ | 最小 | schema不変 | 小 | 完全互換 |
| **D-2** | Trial側schemaで`violation_spans`(文字列配列)を新設し唯一の情報源にする。`claim_in_article`は**コードが配列から組み立てる**(Checkerには配列だけを書かせる) | 中 | runnerのlocal schema(`build_recheck_schema`等)と、`claim_in_article`を読む箇所(runnerに14箇所)が対象。配列から`claim_in_article`を組み立てて既存処理に渡す | 中(出力負荷。測定要) | 固定fixtureには配列がない。段階0のアダプタが`claim_in_article`から配列を復元し、内部表現を`spans`に統一 |
| D-2b | 配列と`claim_in_article`の両方を書かせて一致を検査 | 中 | 同上 | 中 | 同上 |
| D-3 | 配列の各要素を`{location_kind, quote}`にする(location_kindは見出し/冒頭/本文/in_one_lineの列挙) | 大 | schema・処理とも増える | 中 | 同上 |

推奨はD-2。D-2bは二重化でOpus #5の指摘に反する。D-3は位置の構造化に有利だが、位置はissueで足りるので今は不要。Trial schemaで`claim_in_article`を外す際の影響範囲(runnerの読み取り箇所、`classify_parsed_result_trial`等)は未確認で、実装委任で要確認。

**Stage 1初回とRecheckで共通の扱い**: `same_fact_id_locations`(他箇所の列挙)と`violation_spans`は概念が重なる。1つの列にまとめるかはOpus論点(§7)。

### 5-4. Prompt文案(Trial専用追記ブロック、実装はしない)
```
【追加指示: 違反箇所の逐語引用(Trial専用。判定基準は変えない)】
この指示は「違反箇所の書き方」だけに関するものです。どの箇所をdeviationとして報告するか、severityや10種類のフラグの判定基準は変えないでください。ここでいう逐語は【検証対象の記事】本文からの引用であり、Ledgerとの文言一致の話ではありません。
各deviationについて、"violation_spans"(文字列の配列)に、その逸脱に該当する箇所を、記事本文から一字一句そのまま引用してください。要約・言い換え・勝手な結合は禁止です。複数箇所なら、別々の原文範囲として、箇所ごとに別の配列要素にしてください。
- 各要素は、記事本文をそのままコピーした文字列にします。語の置換・語順変更・省略(…や...)・翻訳・要約はしません。
- 文の一部だけが問題でも、その語句を含む文全体(文頭から文末まで、記事のとおり)を引用してください。どの語句が問題かはissueに書いてください。
- 大文字・小文字、句読点、アポストロフィ、ダッシュ、空白を変えないでください。文末の句読点を補ったり別の記号に替えたりしないでください(記事で「,」や「:」が続くところを「.」で終えない)。引用符(“ ”)で囲まないでください。見出しは先頭の「#」を除いた文字列で引用してください。
- 位置の説明(「見出し」「冒頭」「段落5」「…で始まる段落」など)、あなた自身の説明文、接続語(and / および 等)を、各要素に入れないでください。位置や理由はissue・explanationに書いてください。
- 見出し・冒頭文・"In one line"が同じ事実を主張しているなら、それぞれ別の要素として、本文のとおりに引用してください。
- 離れた複数箇所は1つの文字列につなげず、別々の要素にしてください。間にある逸脱でない文は含めないでください。連続した複数文が1つの逸脱を構成する場合に限り、記事のとおり連続した1要素にしてください。
- 該当箇所を記事本文の特定の文字列として指せない場合(記事全体の含意など)は、violation_spansを空配列にし、issueにその理由を書いてください。推測で引用を作らないでください。引用できないことを理由に、deviationの報告を省略しないでください。
```
後段の扱い:
- 空配列は「範囲不明」として**人間確認**(fail-closed)にする。
- 配列の各要素は完全一致照合し、不一致・複数箇所一致は確定不能として人間確認。
- Rewrite対象の決定、Stage 2への表示、prior_issues、同一判定は、すべて`spans`から作る。

### 5-5. 必要性の判定: **中程度**
根拠:
- 高くない理由: 確定不能は直近(rep17〜21、iter8、最新29件横断)で0件。13.4%の大半(27行)は固定fixtureの再生で、うち22行はPromptなしの同値変換で解消できる。
- 低くない理由: C3(複数箇所)は、現行で取りこぼしが実際に起きている型。実LLMのRecheck 8行は全てC3(13.8%)で、新方式で人間確認へ回る形になる。K2の捨て14件にも位置説明が多い。
- 判断のタイミング: 委任_42で実装中の受け渡し修正の限定Trialと、29件横断の再確認を見てから決める。判断材料は、新方式の受け取り側(同値変換込み)の下で、実出力のBLOCKINGの確定不能率がどれだけ残るか、そのうちC3がどれだけか。

## 6. E: 限定確認の設計(実行しない)

**比較対象**:
- 既存記録をそのまま対照にはしない。実装コード版やPromptが当時と違い、揺れと混ざるため。**同条件・同時期に取り直した現行Promptのarm(対照)と、新Promptのarm(処置)**を比較する。
- 5項目の測り方:
  - 特定不能率: 新方式(同値変換込み)での確定不能 ÷ BLOCKING指摘数。素の逐語率(正規化なし)も併記。
  - 検出漏れ: 設計書§7の正解ラベルでBLOCKINGとされるfact(B3のHF-007、B4-a、hormuz HF-009、A4、A5、Safety12の9種など)を、BLOCKINGで検出できなかった率。Safety対照は1件でも対照にない見逃しが出たら止める。
  - false PASS: 正解がBLOCKINGの記事で、Checkerの結果が全MINOR/空になった率(Stage 1単体)。全フローでの最終PASSは第3段階で見る。
  - 出力失敗: JSON/schema失敗、API失敗、MAJORなのに`violation_spans`が空の率。
  - Human Reviewへの影響: 処置armの出力を受け取り側にかけてStage 4/人間確認に回る割合を、オフラインで再計算(追加callなし)。第3段階で実フローも確認。

**対象記事と回数**:
- 問題記事8種類(bgroup_B3、bgroup_B4、bgroup_B2_hormuz、safety_A4、hormuz_run03_standard、hormuz_run03_advanced、neg1_meta_b3prod_a2、meta_run03_standard)+ Safety対照11種類(safety_er009×9、A5、A2A3)=19記事。
- 第1段階: Stage 1初回を19記事×2arm×n=3 = 114 call。費用概算は¥0.359×114≈**¥41**(単価範囲¥0.14〜0.66)。
- 第2段階: Recheck文脈(記録済みの記事本文+prior_issues)20件×2arm×n=3 = 120 call。¥0.322×120≈**¥39**。
- 第3段階(第1・2段階で問題なければ): 問題記事のうち代表6種類×2arm×n=2 = 約24フロー。過去実測の1 instanceあたり平均¥0.5〜4.5(安全A4が¥4.49、hormuz_run03_standardが¥1.46など)から**¥50〜80**。
- 合計は概算¥130〜160で、¥600の上限内。

**Stage 1の非決定性とPrompt変更の影響の区別**:
- 同じ記事・同じLedgerを固定し、対照armと処置armを交互に取る。
- 対照どうし(対照A対対照B)のfactレベルの検出一致率を先に測り、揺れの幅とする。処置と対照の差がこの揺れを明確に超えたときだけ「Prompt変更の影響」とみなす。
- 比較は`claim_in_article`の文字列ではなくfact_id単位で行う。

## 7. ユーザーSTOP条件への該当可能性、Opusに特に見てほしい論点

**STOP条件**: 現時点で該当なし。Production正式pathは変更せず、新しいProduct原則・Safety原則の変更もなく、¥600超過もない。ただし`violation_spans`のProduction採用は別途`APPROVED_FOR_PRODUCTION`の人間承認が必要(Trial範囲外)。

**Opusに見てほしい論点**:
1. C2の同値変換(両端の句読点除去+文単位スナップ)を「文字単位の同値変換」として認めてよいか。範囲は文の途中までの節になる。
2. C4の省略記号「A ... B」の決定論的解釈を同値変換とみなすか。
3. C3で位置ラベルだけ(U02・U08・U13)の分解を許すか。ラベル語彙の判断が再推測寄りになる。縮小リスク(U06・U11・U12)とのバランス。
4. 位置ラベルを引用符で囲んだ文字列(`“In one line”`等)が、現行L1/L4で見出しの文字列に一致して誤って確定する問題(K2の3件)。
5. D-2(配列のみ)対D-1b(改行区切り)。`same_fact_id_locations`との重複を、1つの列に統合するか。
6. C3の複数箇所を人間確認に回す代わりに、複数範囲を一度に渡す書き換え(Opus #5の修正案4)と組み合わせる前提でよいか。

## 8. 検算結果、限界・未確認

**検算**:
- 独立実装の照合で再抽出した結果は、BLOCKING確定不能35行・13種類・32 runで、委任_41のCSVと完全一致(差0)。非BLOCKINGも7行で一致。
- 区分の合計は35行・13種類。
- 13種類の記事該当箇所は、スクリプトが記事に逐語で実在することを確認済み(転記ミスなし)。U07は全20行でも確認済み。
- 補助集計(借用本文)では36行(iter8 s1のsafety_A4が加わる)。

**限界・未確認**:
- 現行の対象が意図と一致していたかは、書き換え前後の差分と次周回の再指摘からの目視判定。U03・U04・U05は古いfixtureでissueの記録がなく、claim文字列と記事から推測。
- 取りこぼしとStage 4の関連は、因果の証明ではない(Rewrite出力の揺れ、JA側の問題も重なる)。
- 独立なChecker出力は13種類のみ。実出力は8行と少なく、比率には幅がある。
- Prompt変更の効果は見積もりであり、実測ではない。逐語率・検出精度への影響は未測定。
- 配列schemaへの変更が、runnerの`claim_in_article`の全読み取り箇所に与える影響は未確認(実装時に要確認)。
- 委任_42が編集中のrunnerは、修正前コピー(e0ae8de0)で読んだ。現行と挙動が異なる可能性がある。

## 9. 読んだファイル、T-0、作成ファイル

**読んだファイルと行範囲**:
- `er052_output/open233_handoff_log_aggregation_01/aggregate_01.py`: 1〜341、385〜634(Read)、938〜950(sed)。
- `claims_detail_01.csv`: Pythonで該当35行+非BLOCKING7行を抽出。
- 修正前runner(`git show e0ae8de0:`で一時ディレクトリへ出力): 1105〜1190、1460〜1512。
- `er003_v1_en_direct_vfl_01_generate.py`: 450〜604。
- `er051_open233_checker_trial_variant_01.py`: 170〜255。
- `docs/pm/design_open233_violation_span_handoff_01.md`: 98〜201、433〜450、529〜553。
- `docs/pm/opus_l2_review_open233_self_recovery_05.md`: 14〜22、38〜42、59〜92(+Grepで位置特定)。
- `docs/pm/design_open233_self_recovery_flow_01.md`: 3395〜3452。
- 各instance JSON: スクリプトで該当周回の記事本文・指摘フィールド・Stage 2・rewrite_records・call_logのみ抽出(全文Readなし)。

**一覧外の追加Read**:
- `er003_v1_en_direct_vfl_01_generate.py` 655〜715(prior_issues指示と`RELATED_FACT_ID_INSTRUCTION`の確認)。
- `er051` 262〜284(Trial schemaの組み立て、Grep -A)。
- `results_01.json`の一部(D、scope、K2K3、run_info、supplement)をPythonで抽出。
- 一時ディレクトリの診断スクリプト(リポジトリ外)。

**T-0**: `docs/pm/delegation_log/2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_45.md`を保存し`check_delegation_prompt.py`を実行。**PASS**(reasonsなし、警告2件はTTSという語を文中で触れただけの誤検知)。初回は見出し名の不一致でFAILだったため、見出しを直して再実行しPASS。受領文は全文ではなく要約保存。

**作成ファイル(未追跡、git add/commitなし)**:
- `C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_45.md`
- `C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_45.md_check.json`
- `C:\Users\tensh\eigo-radio\er052_output\open233_handoff_log_aggregation_01\classify_unverified_01.py`(標準ライブラリのみ、既存モジュールをimportしない)
- `C:\Users\tensh\eigo-radio\er052_output\open233_handoff_log_aggregation_01\unverified35_classification_01.csv`(35行、列に目視判定を含む)

リポジトリ外の一時ファイル(スクリプト・修正前runnerのコピー)は、Claude Codeのscratchpadディレクトリにある。