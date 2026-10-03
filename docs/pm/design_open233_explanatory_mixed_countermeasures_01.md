# Checker引用への説明文混入: 原因の深掘りと対策案の設計(委任_56、OPEN-233-SELF-RECOVERY-TRIAL-01)

性質: 分析・設計のみ(コード・Prompt・SSOT・既存docは変更していない。LLM/API呼び出しなし、費用¥0)。採用判断はしていない。
この後、FableがOpus独立レビュー(必須)→Fable再評価→ユーザー提示を行う。
検証スクリプト・結果: `er052_output/open233_explanatory_mixed_offline_check_01/`(`check_01.py`、`results_01.json`、`cases_01.csv`、`fixtures_snapshot_01.json`)。
略記: 「混入」=Checkerの`claim_in_article`に、記事の逐語引用以外(説明文・位置ラベル・つなぎ)が混ざったもの。「現行照合」=`_resolve_claim_string`(L0〜L5・L4・label_only、`VS_MATCH_EXT=ON`)。

## 0. 先頭の結論

1. **混入は「引用部分が必ず引用符で囲まれ、説明部分は必ず引用符の外」という規則的な形**だった(13行全部、非BLOCKING 5行も同じ)。したがって、Prompt・schemaを変えずに後段だけで分離できる余地が大きい(案P)。
2. **前回の配列方式で検出が落ちた原因は、1つに特定できない**。記録で支持されるのは「引用を『語句だけ』に狭める指示でfact_idの付き方が動いた」「`violation_spans`が『他の箇所』の置き場を奪い、`same_fact_id_locations`が39→23件に減った」の2点。一方「検出数そのものが減った」は支持されない(MAJOR総数は両腕24件で同じ)。差は統計的にも揺れと区別できない(Fisher検定 p≈0.3)。**だからこそ、Checkerを変えない案Pは検出性能に影響しないことが構造上保証される**。
3. 346行の再生で、**案P(追加方式)が現行で確定していた範囲を変えた例は0件**(確定不能→確定の13件は全て説明文混入の行)。12件(実質13行、後述)は案P-strict+Qで12行が意図どおりの範囲で採用、1行(U12)だけ人間確認のまま。
4. 推奨(Fableが最終判断): **案P-strict(+Q)**。追加LLM呼び出しなし・非決定性なし・既存の確定には触れない追加方式。「見送り(案T)」は推奨しない(原因は特定でき、副作用が小さい安全網があるため)。Prompt追記(案R)は、前回の分析が「Prompt追記が主犯候補」を排除できていないため、Pで足りなければ次に検討する(測定に約¥65〜130)。
5. 実際の発生頻度は現行構成では低い(後述1-3)。Pは「頻度が高いから」ではなく「¥0で安全網になるから」の案である。

## 1. 作業1: 原因の深掘り

結論: 13行は全て「引用符で囲まれた逐語」+「引用符の外の説明/位置/つなぎ」の形。実LLM出力は全てRecheckで、その時点のRecheck出力schemaには『他の箇所』の置き場が無かった(8件中7件)。出典: 委任_45 §2-1、`claims_detail_01.csv`、`results_01.json`の`a_table`。

件数の注記: 委任_45・53の「12件」は`unverified35`の12行。今回346行を再生すると`explanatory_mixed`は**13行**(U02の固定fixture再生がiter8でもう1行、借用本文の補助集計分)。独立なChecker出力は9件(U01・U02[原本1]・U06・U08・U09・U10・U11・U12・U13)。

### 1-1. 混入パターンの型化(文字列の構造)

引用符の種類は全て曲線二重引用符 “ ” または 「 」(直線引用符・単一引用符は0件)。

| 型 | 文字列の構造 | 該当(行) | 引用部分は引用符で囲まれているか | 説明部分の位置 |
|---|---|---|---|---|
| T1 | [“引用A”]+[Checkerの語]+[“引用B”] | U01(1) | 囲まれている(2つとも) | 引用符の外(「Meta’s test」) |
| T2 | [“引用A”]+[日本語の接続語+位置語]+[「引用B」] | U02(5=原本1+固定fixture再生4。iter8の借用1を含む) | 囲まれている(“ ”と「 」が混在) | 外(「および冒頭の」) |
| T3 | [“引用”]+[説明文1文。未引用の別箇所を名指し/広い範囲を示唆] | U06(1)・U11(1) | 囲まれている | 外(文として説明) |
| T4 | [位置+says]+[“引用A”]+[and+位置+says]+[“引用B”] | U08(1) | 囲まれている | 外 |
| T5 | [“引用A”]+[, reinforced by the headline]+[“引用B”] | U09(1) | 囲まれている | 外 |
| T6 | [位置ラベル:]+[“引用”] | U10(1) | 囲まれている | 外(「Headline:」) |
| T7 | [“引用A”];[“引用B”]+[(括弧の位置語)] | U12(1)・U13(1)。U13は引用ごとに(headline)(one-line summary) | 囲まれている | 外(括弧) |

参考(委任_45 §2-4の非BLOCKING 5行、今回の再生では`Crude oil also passes through it.`はL5で確定するため確定不能は6行): 「[裸の語句;]+[“引用”]」(語句が記事に逐語で存在)・「[“A”]+and the description of this as a+[“B”]」・「[Headline: “A”; also, “B”]」・「[“A”](in the passage stating …)」×2・「[“引用全体が言い換え”]」(混入ではなく言い換え1)。

`same_fact_id_locations`(Recheck出力の列挙欄)の記録上の14件(`results_01.json`の`d_dropped_same_fact_locations`、全てcycle2〜3のRecheck出力で、現行配線では展開されない): 位置ラベル+引用(「Paragraph 5: “…”」等)7、位置だけ(「Paragraph 7」「Paragraph 5」)2、位置ラベルだけの引用(“In one line”単独・“In one line”: “…”)3、日本語の正常文1、引用符で囲まれた逐語1。同じ「ラベル+引用」の型が、列挙欄にも出ている。

### 1-2. なぜ「出力形式10件・Prompt2件」か(再整理)

結論: 委任_53の分類(出力形式10・Prompt2)は、文字列構造から見ても妥当。ただし「出力形式」と「Prompt」は実験で切り分けられていない(Prompt未指示と形式の欠落は同じ失敗の両面)。

| 欠落 | 対応する型 | 行 |
|---|---|---|
| (a) 複数箇所を1つの単一文字列でしか表せない | T1・T2・T4・T5・T7 | U01・U02×5・U08・U09・U12・U13 = 10行(委任_53の「出力形式10」+iter8借用) |
| (b) 「他の箇所」の置き場はあるが使い方の指示がない | T3(U11) | U11(Recheck出力にsame_fact_id_locationsはあり、本文の引用+説明文で別箇所を指しつつ、同じ欄にも6件書いた)。委任_53は「出力形式」。私は「(a)と(c)の両方」と見る。分類の数は変えない |
| (c) `claim_in_article`の中身の書き方(逐語引用だけ)の指示がない・位置の説明の置き場がない | T3(U06)・T6(U10) | U06・U10 = 2行(委任_53の「Prompt2」) |

分類変更なし。補足: 現行Prompt(`DEVIATION_PROMPT_TEMPLATE`、`er003`502〜541行)に`claim_in_article`の書き方の記述はなく、schema(`DEVIATION_JSON_SCHEMA`、454〜493行)は`claim_in_article: {"type":"string"}`の単一文字列。

### 1-3. 初回CheckerとRecheckの違い

結論: 混入は**Recheckにほぼ限られる**(K1のRecheck 137行中13行=9.5%、Stage 1初回は327行中4行で、その4行は固定fixtureの再生=独立1件)。Stage 1の生LLM出力(委任_53の対照腕18call・25件の指摘)では0件。Recheckだけで起きる理由は、記録から次の3つが言える(因果の証明ではない)。

| 観点 | 事実(出所) |
|---|---|
| 件数 | K1・Recheck 137行中13行(うちBLOCKING 8・非BLOCKING 5)。K1・Stage 1初回 327行中4行(U02の固定fixture再生)。委任_53 Stage 1(対照腕25件・K2展開含む62件)は0件(`claims_detail_01.csv`、`results_01.json`) |
| 「他の箇所」の置き場 | Stage 1初回のPromptには`SAME_FACT_ID_ENUMERATION_INSTRUCTION`(他の箇所を逐語で列挙せよ)があり、schemaにも欄がある。**Recheckの出力schemaに`same_fact_id_locations`が入っていたのはiter7・iter8・rep11以降のみ**(iter5・iter6・rep7〜10のRecheck出力にはキー自体が無い)。キー無しの期間のK1・Recheck 87行中12行が混入(13.8%)。キー有りの期間は50行中1行(U11、2.0%)、Fisher検定 p=0.031。ただし時期の交絡あり(実装の他の変更も同時に入っている) |
| Recheck特有の入力 | `build_prior_issues_instruction`(`er003`678〜693行)は前周回の指摘を`index=i: fact_id=… | claim_in_article=… | issue=… | explanation=…`で再提示し、各項目の解消を`prior_issues_resolved`で答えさせる。委任_42より前は`claim_in_article`欄に**前周回の生のclaim文字列**がそのまま入った。実LLM出力の8件のうち、U10の前周回(=U09)とU13の前周回(=U12)は**混入した文字列そのもの**(実機Promptの内容は記録上の再構成、`call_log`に生Promptは無い)。8件中2件は前周回の混入文字列をエコーした可能性がある |
| Recheckの指示文に位置の説明を促す文言 | **無い**(`build_prior_issues_instruction`は「個別に解消されたか判定し`prior_issues_resolved`として記録」と言うのみ。`run_recheck`の追記はV4A、関連Fact ID、発生源、prior_issuesのみ)。位置を促す文言はないが、Recheckは「残っている・広がった箇所」を書く性質があり、複数箇所を1つの`claim_in_article`に詰める動機が生まれる(推測) |
| 出力の傾向 | 引用符つきの比率はStage 1が51%、Recheckが65%。引用符2つ以上の複数断片はStage 1が3.7%(12/327)、Recheckが8.8%(12/137) |

なお現行構成に近いiter8・rep11〜21(K1のRecheck 35行。rep22は対象データ外)では`claim_in_article`の混入は0件。混入は`same_fact_id_locations`欄(rep20・rep21の14件)へ移っている(1-1)。

### 1-4. 分離に必要な情報は既に出力内にあるか(13行)

結論: 13行全てで、(i)引用部分は引用符で区切られ、(iii)引用符内だけを取り出すと記事に逐語(L0〜L5)で一致する。(ii)説明文が指す別箇所の逐語が同じ指摘にあるのはU11だけ(rep9のU12・U13のRecheck出力にはキーがない)。

| 行 | (i)引用符で区切られているか | (ii)別箇所の逐語が同じ指摘のsame_fact_id_locationsに入っているか | (iii)引用符内だけを取り出すと記事に逐語で一致するか |
|---|---|---|---|
| U01 | はい(2つ) | 該当なし(別箇所の名指しなし) | 2つとも一致(各1箇所、L0) |
| U02(5行) | はい(“”と「」) | iter8の1行のみキー有り(2件、追加の名指しはなし) | 2つとも一致(L0) |
| U06 | はい | 説明文の「The opening」は引用の所在と同じ冒頭段落。キーなし | 一致(L0) |
| U08 | はい(2つ) | 該当なし | 2つとも一致(L0)。見出しは前半を引用 |
| U09 | はい(2つ) | 該当なし | 2つとも末尾句読点付き→L5で一致 |
| U10 | はい | 該当なし | 末尾ピリオド付き→L5で一致 |
| U11 | はい | **入っている**(6件。見出しとin one lineの逐語を含む) | 一致(L0) |
| U12 | はい(2つ) | キーなし | 2つとも一致(L0) |
| U13 | はい(2つ) | キーなし | 2つとも一致(L0) |

### 1-5. 前回方式(violation_spans)で検出性能が落ちた理由(最重要)

結論: **単一の原因は特定できない**。n=3で、検出12/18→8/18・false PASS 1/15→4/15の差は統計的に揺れ(対照どうしの一致率0.67)と区別できない(Fisher検定 p=0.32、0.33)。記録で支持される仮説は2つ(H1のfact_id付与のずれ、H5の置き場の競合)、支持されない仮説は2つ(H2順序、H3長さ)、判定不能は1つ(H4揺れ)。出所: `er052_output/open233_checker_spans_format_compare_01/calls/*.json`をPythonで集計。

**Prompt差**(生Promptは保存されておらずsha256のみ。コードから構成): 対照と処置のPrompt全文は、V4A本文・関連Fact ID・発生源・`SAME_FACT_ID_ENUMERATION_INSTRUCTION`までが同一で、処置だけ**末尾に`VIOLATION_SPANS_INSTRUCTION`(1,145文字、runner約1203行)を追記**。入力トークン平均は対照6,682→処置7,480(+798、+12%)。追記は最後(直近)の指示で、10項目超の規則(引用は語句だけでよい/前後の語を足して1箇所に/位置の説明は入れない/見出し・冒頭・In one lineは別要素/離れた複数箇所は別要素/特定不能は空配列)を含む。

**Schema差**(`build_deviation_schema_with_spans`の出力を実測、`required`と`properties`は同じ順):
- 対照: `claim_in_article`, `issue`, `severity`, `changed_fact`〜`unsupported_new_claim`(10個), `explanation`, `related_fact_id`, `origin`, `qualifier_present`, `qualifier_text`, `ledger_field_basis`, `observation_consistent`, `matched_notes_id`, `same_fact_id_locations`
- 処置: 先頭の`claim_in_article`を除き、末尾に`violation_spans`を追加(`...matched_notes_id`, `same_fact_id_locations`, `violation_spans`)。つまり**処置では先頭が`issue`になり、引用が最後に書かれる**。

**実際の出力差**(25件の指摘ずつ、18 call):

| 指標 | 対照 | 処置 |
|---|---|---|
| 指摘の総数 / MAJOR / MINOR | 25 / 24 / 1 | 25 / 24 / 1 |
| 推論トークン平均 / 出力トークン平均 | 4,318 / 4,723 | 4,355 / 4,762 |
| 指摘0件のcall(BLOCKING対象のある記事15call中) | 0 | 3(hormuz×2、meta×1) |
| `issue`平均文字数 / `explanation` | 132 / 129 | 177 / 157 |
| 引用の長さ(対照=claim平均、処置=要素平均) | 88文字 | 63文字(最短11) |
| 配列要素数(処置): 1/2/3/4個の指摘数 | - | 17/4/2/2 |
| `same_fact_id_locations`の総件数 | 39 | 23 |

**落ちたfactの逐語**(処置腕の出力):
- **HF-009(hormuz) 3/3→1/3**: 処置のcall 1と3は**`{"deviations":[]}`(完全な空)**。推論トークンは1,211と1,241(同記事の対照は4,297〜5,307)。MINORでも別factでもなく、そのfactに触れていない。call 2は`["Oil prices did not fall across the whole market after the plan was withdrawn."]`で対照と同じ文。
- **MUSE-HC-006(safety_A4) 3/3→2/3**: 処置のcall 2は、対照が`MUSE-HC-006`として出した文`Through Muse, trained human contract workers made some calls and completed the exchanges with users.`を、**`MUSE-HC-004`・`["with users."]`(11文字)**として出した。同じ箇所を別のfact_idに付けた。
- **MUSE-HC-012(meta) 2/3→1/3**: 処置のcall 1は**MINOR**(`["users could not know.","They could not tell if it was AI or a person.","They enjoyed AI’s convenience, but a human was on the other end.","They did not realize it."]`の4要素)、call 3は**空**。call 2はMAJORで検出。同call 2は別に`MUSE-HC-011`(`["…"×2]`)を追加。
- 新たに処置腕でだけ出たfact: `MUSE-HC-004`(2件)・`MUSE-HC-011`(1件)。

**仮説と記録の突き合わせ**

| # | 仮説 | 記録 | 判定 |
|---|---|---|---|
| H1 | 「語句だけ引用」の指示が注意を狭め、fact_idの付き方が動く | 引用が88→63文字に短縮、「with users.」(11文字)がHC-006ではなくHC-004へ。ただし**MAJOR総数は24件で同じ**で、検出数が減ったのではなく、付いたfact_idが変わった | **一部支持**(fact_id付与のずれ。検出数低下までは支持されない) |
| H2 | `claim_in_article`を先頭から外し「まず引用してから判断する」順序が崩れた | 引用が最後に書かれる順序は事実。しかしhormuzの空2callは**推論1.2k tokens(隠れた推論)の段階で「指摘なし」が決まっており、出力フィールドの順序より前**。issueが長くなった(+34%)のは順序よりも「どの語句が問題かはissueに書く」指示の影響とみえる | **支持されない**(検出落ちの説明にならない)。出力のスタイル変化としては支持 |
| H3 | 追記の長さがV4Aの限定語確認などの指示を薄めた | 入力+12%・末尾追記は事実。推論/出力トークンの平均は対照とほぼ同じ(4,318対4,355)。ただしhormuzの空2callは推論が極端に短い | **集計では支持されない**が、個別callでは排除できない |
| H4 | 揺れの範囲内 | 対照どうしの一致率20/30=0.67、処置どうし19/33=0.58。検出p=0.32、false PASS p=0.33、HF-009 p=0.40。n=3 | **排除できない(支持も否定もできない)** |
| H5(追加) | `violation_spans`と`same_fact_id_locations`が「他の箇所」の置き場として競合した | `same_fact_id_locations`が39→23件(-41%)。配列要素が2〜4個の指摘が8/25件。K2展開を含むMAJOR総数も59→44(-25%)。**他の箇所の取りこぼしを減らす目的に反する副作用で、記録で支持される** | **支持される** |

つまり委任_53の方式は、Checkerの見る範囲を変える(Prompt追記)・引用の置き場を変える(schema)の両方をいっぺんに行っており、検出低下の原因を分けられない。**Prompt・schemaの追加が検出を動かし得る**ことは、H1とH5が示している。Checkerを変えない案P・Qは、この問題を構造上回避する(Checkerの出力は1字も変わらない)。

### 1-6. 後段で決定論的に処理できる範囲と、fail-safe

結論: Prompt・schemaを変えずに後段だけで取り出せるのは「引用符で囲まれた断片が全て記事に一意に逐語一致し、かつ引用符の外の残りが記事の文字列ではない」場合。取り出せない場合は、再推測せず確定不能(人間確認)のままにする。

| 型 | 取り出せる条件 | 取り出せない条件(確定不能のまま) |
|---|---|---|
| T1・T2・T4・T5・T7(複数断片+説明/位置) | 全断片が記事に「ちょうど1箇所」(L0〜L3・L5・単語境界)。外の残りが記事に逐語で存在しない(存在しても1〜2語以下は説明語として捨てる) | 断片が記事に無い(言い換え・省略記号 U05)、断片が2箇所以上に一致、残りに記事の3語以上の逐語、引用符が閉じていない |
| T3(断片1+説明文) | 断片1つが一意。説明文が記事に無い | 説明文が名指しした見出し/In one line/冒頭に、どの断片も重ならない(「宙に浮いた位置語」。U11・U12)。→ 案P-strict: 確定不能、案Q: 同じ指摘の`same_fact_id_locations`で裏付けられれば補う |
| T6(位置ラベル+断片) | ラベルが記事に無い | 断片が構造ラベル(「In one line」)だけ(`label_only`) |
| 引用符なし | (なし) | 現行照合で確定しなければ確定不能(`p_no_quote`)。再推測しない |

既存L4(曲線引用符の断片分割)との関係: L4は「断片2つ以上、残りが接続語・句読点だけ」のときのみ確定する。案Pは**L4の条件を緩める**(断片1つも可、残りは「記事に逐語で存在しない文字列」なら何でも捨てる)ので、L4の一般化ではあるが厳密には条件緩和であり、緩めた部分(残りの文字列を捨てること)の安全性が論点になる。ガードは「残りが記事の3語以上の逐語なら不採用」「宙に浮いた位置語があれば不採用/補完」。

## 2. 作業2: 対策案の設計

結論: 案Pの運用形(P-strict、必要ならQ)が、検出性能への影響がなく、追加呼び出しも非決定性もない。案R・Sは検出性能を動かし得る(1-5)。案Tは安全だが、混入行が人間確認へ回り続ける。出所: 本節は設計。数値は第3節。

### 案P(ユーザー候補案): 後段で断片を取り出す(Prompt・schema不変)

- 処理: 現行照合で確定不能(`explanatory_mixed`または`mismatch`)になった文字列にだけ、(1)引用符(“ ” 「 」 『 』 直線の"…")で囲まれた断片を全て取り出す、(2)各断片を同じ言語の本文で既存の照合(L0〜L3・L5・単語境界)により「ちょうど1箇所」に確定、(3)引用符の外の残りの各区間が記事に逐語で存在しないことを確認(接続語・構造ラベルは例外、**3語(日本語は8文字)以上が逐語で存在すれば確定不能**。1〜2語は偶然の一致(例: 「headline」)として説明語扱い)、(4)全断片が確定し残りが全て非記事のときだけ採用、(5)引用符なしは確定不能のまま。
- 追加方式の理由: 現行照合で確定する文字列は一切処理を変えない(`multi_match`・`label_only`・空・本文なしも現行のまま)。346行の再生で「P先行」(先にPを試す)でも結果は同一だったが、追加方式のほうが構造上安全。
- 変更箇所: `_resolve_claim_string`(2026-10-03時点で`er052_open233_self_recovery_flow_runner_01.py`3194行付近)の最後の`explanatory_mixed`/`mismatch`の分岐に新関数を追加(約60行+テスト約10件)。`resolve_violation_spans`の呼び出し9箇所は無改修。Trial専用スイッチ(既定OFF)で配線する。
- 初回/Recheck/retry/fallback: 全て`resolve_violation_spans`を通るので同じ扱い。`prior_issues`へ渡す確定範囲(`claim_span_text`)が清浄になるため、混入文字列が次のRecheckへエコーされる経路も断てる(1-3)。
- fail-safe: 1断片でも確定不能なら全体が確定不能(人間確認、`violation_span_unverified`)。
- 追加LLM呼び出し: なし。非決定性: なし。
- 課題: 説明文が名指しした別箇所を取りこぼす(部分採用)恐れ。→P-strict。

### 案P-strict(推奨する運用形)

案Pに、「説明文が名指しした見出し/In one line/冒頭に、どの断片も重ならないものが残るなら確定不能(fail-closed)」を加える。説明文は**範囲を広げるためには読まず、「断片だけでは足りない可能性」を検出して拒否するためだけに読む**。13行中11行が採用、2行(U11・U12)は確定不能のまま人間確認。

### 案Q(案P-strict+同じ指摘の`same_fact_id_locations`による補完)

案P-strictに加え、名指しされた見出し/In one lineが、**同じdeviationの`same_fact_id_locations`に逐語で入っているとき**に限り、記事の構造(見出し行・`## In one line`直下)として範囲へ補う。
- 別AIの引用ではなく、**同じChecker呼び出しの別欄**(Checkerが自分で書いた逐語)なので、ユーザー方針「別AIの引用でRewrite対象を決めない」と矛盾しない。名指しされた要素(見出し/In one line)は、記事の構造から一意に決まる。
- 補完の対象は、説明文が名指しした要素に限る。`same_fact_id_locations`の全件を足すわけではない(U11では6件のうち2件だけ補う)。
- 現行のRecheckは`enable_fact_id_enumeration=False`で展開しない。Stage 1の列挙経路では、同じ要素はK2として別claimに展開済み(U11の`k2_siblings`は6件)なので、Qの追加価値は列挙が無効なときに限られる。
- 変更箇所: `annotate_claim_span_identity`(同3320行付近)でdeviation(`dev["same_fact_id_locations"]`)を渡せる位置に補完処理(約40行)。`_resolve_claim_string`だけでは`dev`を持たないため、案Pより変更が広い。
- 案Q'(裏付けなしで構造だけで補う)は、説明文の語(headline等)から範囲を広げることになるので**推奨しない**(再推測に近づく。Opus・ユーザー論点)。

### 案R: Prompt最小追記のみ(schema不変)

- 内容: 「`claim_in_article`には記事本文からの逐語引用だけを入れ、位置の説明や理由は`issue`へ。複数箇所なら引用符で区切って並べる」の1〜3行。
- 前回方式との違い: `claim_in_article`は外さない(順序不変)、配列にしない(`same_fact_id_locations`と競合しない)、「語句だけでよい」は入れない(H1を避ける)。
- 検出性能への影響の見込み: **不明**。1-5でH3(追記の長さ)は個別callで排除できず、H1・H5は避けられるがH3・H4は残る。
- 確認に必要な規模: 前回と同じ検出率(0.67→0.44の差)をα=0.05・検出力80%で見分けるには、記事×call単位で約77(Fisher近似、n=3の記事内相関を無視)。6記事×13回×2腕=156 call、**約¥65**(¥0.42/call)。相関を考えると¥130程度。Recheck側(混入の実例が全てRecheck)を測るにはさらに追加。
- 効果: 混入の発生自体を減らすが、既に出た混入を処理する安全網にはならない。

### 案S: Recheckだけに手当て

- S1: Recheck出力の混入だけに案P-strictを適用(出所別の厳格化)。混入13行は全てRecheckだが、Stage 1の生出力でも原理的に起き得るので、Stage 1を除外する利点は小さい(P-strictはStage 1でも現行確定に触れない)。→ 実質は案P。
- S2: Recheckの`same_fact_id_locations`の指示を足す(`enable_fact_id_enumeration=True`)。委任_35で、cycleごとに検出対象が増える(2→12→5)ため意図的にOFFにした経緯があり、独断で戻さない。
- S3: `prior_issues`の`claim_in_article`欄を確定範囲にする(委任_42で実装済み。案Pが混入文字列を確定させれば清浄な範囲が渡る)。

### 案T: 現状維持(確定不能は人間確認)

比較の基準線。安全だが、混入行が人間確認に回る。13行/346行(3.8%)。

### 案U: 引用符の付与をPromptで強制するだけ

不要。混入は既に全て引用符で囲まれており、足りないのは「引用符の外に何を書くか」の規則。実質は案Rに含まれる。

### 案V(参考): 前回方式の再試行
「語句だけ引用」の指示を外した配列方式。H5(置き場の競合)が残るため推奨しない。

### 比較表

| 軸 | 案P-strict | 案P-strict+Q | 案R | 案S1 | 案T |
|---|---|---|---|---|---|
| 検出性能を落とさないか | 影響なし(Checker不変) | 影響なし | **不明**(要測定) | 影響なし | 影響なし |
| false PASSを増やさないか | 増やさない | 増やさない | 不明 | 増やさない | 増やさない |
| Human Reviewを増やさないか | 減る(13行中11行が採用) | 減る(12行) | 減る見込み | 減る | 現状 |
| 不要Rewriteを増やさないか | 部分採用なし(宙に浮いた位置語は拒否) | 同左(補完は裏付け付き) | 不明 | 同左 | 増えない |
| 再推測による誤範囲 | 無(引用は逐語、説明文は拒否のみに使用) | 無(同じChecker出力の別欄) | 無 | 無 | 無 |
| 実装の複雑さ | 小(約60行) | 中(約100行、dev受け渡し) | 小(Promptのみ) | 小 | なし |
| 初回/Recheck/retry/fallbackの整合 | 全経路一致(照合の1箇所) | 同左 | Stage 1とRecheckで別Promptを揃える必要 | 同左 | 一致 |
| コスト | ¥0 | ¥0 | 測定に約¥65〜130 | ¥0 | ¥0 |
| 非決定性 | なし | なし | あり(LLM出力) | なし | なし |
| 13行のうち解消できる件数 | 11(U11・U12は確定不能のまま) | 12(U12のみ残る) | 発生を減らす(件数は未測定) | 11〜 | 0 |
| Production配線時のリスク | 低(追加方式、現行確定に触れない) | 低〜中 | 中(Prompt変更=Checker性能に波及) | 低 | なし |

## 3. 作業3: ¥0オフライン検証(`check_01.py`)

結論: 346行で現行確定の範囲が変わる・外れる例は0件。13行中、案P-strictで11行、案P-strict+Qで12行が意図どおりの範囲で採用された。委任_53の対照腕18callは62件の指摘全てが現行で確定済みで、案Pは何も変えない。出所: `results_01.json`。

自己検証: `check_01.py`の現行照合のコピー(`VS_MATCH_EXT=ON`)が、委任_49の再生(`er052_output/open233_match_ext_replay_01/cases_01.csv`のON側)と346行全件で一致(不一致0件、`selfcheck_vs_replay49`)。合成記事10件の安全性テストも全て期待どおり(`synthetic_tests`、複数一致・閉じ忘れ・入れ子・記事の逐語を外に持つ文字列・構造ラベルだけの引用などは全て確定不能)。

### (a) 13行: 取り出した断片と、意図との一致(目視は私)

| 行 | 断片(逐語、前後略) | 残り(捨てた説明/位置) | P-strict | Q | 意図との一致(目視) |
|---|---|---|---|---|---|
| U01 | `A call came from an AI agent. … It was a person.` / `produced exactly this kind of surprise.` | `Meta’s test` | 採用(2箇所) | - | **一致**(冒頭段落と次段落の文。第2断片はChecker自身が文の後半だけを引用) |
| U02×5 | `That was what people thought as they spoke.` / `people who thought they were speaking with AI were actually speaking with human staff` | `および冒頭の` | 採用(2箇所) | - | **一致** |
| U06 | `That was what people thought as they spoke.` | `The opening also presents the call as one people believed was from an AI.` | 採用(1箇所) | 補完なし | **概ね一致だが不確実**(説明文は冒頭段落全体を示唆する可能性。決定論では判別不能) |
| U08 | `I Thought It Was an AI Call—But There Was a Person Inside?` / `A call came from an AI agent. That was what it seemed.` | `The headline says` / `and the opening says,` | 採用(2箇所) | - | **一致** |
| U09 | `Meta had run a test that caused exactly this surprise` / `We Thought It Was AI—But There Was a Person Inside Meta’s Muse`(L5で末尾句読点を除去) | `reinforced by the headline` | 採用(2箇所) | - | **一致** |
| U10 | `We Thought It Was AI—But There Was a Person Inside Meta’s Muse`(L5) | `Headline:` | 採用(1箇所) | - | **一致** |
| U11 | `Oil prices moved briefly, then returned to a high level.` | `The headline and one-line summary also state this more broadly …` | **確定不能**(宙に浮いた位置語: headline・one_line) | **採用(3箇所)**: 見出し`The Fee Plan Leaves, But High Oil Prices Stay`・本文の文・in one line`The fee plan vanished, but oil prices stayed high as tensions around the Strait of Hormuz continued.`(same_fact_id_locationsが裏付け) | P単独は一部のみ。**Qは一致** |
| U12 | `Oil prices moved briefly, then returned to a high level` / `oil prices stayed high` | `(also reflected in the headline).` | **確定不能**(headline) | 補えず確定不能(rep9のRecheck出力に`same_fact_id_locations`が無い)。Q'なら見出しを構造から補い一致 | P単独は一部のみ |
| U13 | `High Oil Prices Stay` / `oil prices stayed high` | `(headline);` / `(one-line summary).` | 採用(2箇所) | - | **一致**(「headline」は記事に1語だけ偶然あるが、説明語として捨てる) |

感度: 「残りを記事の文字列とみなす最小語数」を1にすると、U13が確定不能になる(1語の偶然一致で拒否)。2〜6では13行すべて採用(悪化は全て0件、`sensitivity_min_words`)。3語を既定にした。

### (b) BLOCKING 346行全体(委任_49の再生表と同じ形式)

現行(`VS_MATCH_EXT=ON`)は確定320行・確定不能26行(説明文混入13+その他13。その他13は数値検査の文字列(K3)12行とU05(省略記号)1行)。

| 遷移 | P(lenient) | P-strict | P-strict+Q | P-strict+Q' |
|---|---|---|---|---|
| 確定→確定(同じ範囲) | 320 | 320 | 320 | 320 |
| **確定→確定不能** | **0** | **0** | **0** | **0** |
| **確定→確定(範囲が変わった)** | **0** | **0** | **0** | **0** |
| 確定不能→確定 | 13 | 11 | 12 | 13 |
| 確定不能→確定不能(理由が変わった) | 0 | 2 | 1 | 0 |
| 確定不能→確定不能(同じ) | 13 | 13 | 13 | 13 |

**現行で正しく確定していた範囲が変わる・外れる例は0件**(全件逐語で報告する対象なし)。「P先行」(先にPを試すストレステスト)も確定→確定不能0・範囲変化0。確定不能のまま残る13件は混入ではなく、数値検査の文字列12件(引用符なし、`p_no_quote`)とU05(省略記号で記事に無い断片、`p_fragment_not_in_article`)。

### (c) 委任_53の対照腕(現行形式の実LLM出力、18 call)
対象は62件(指摘25件+K2展開37件)。**62件全てが現行で確定済み**で、案Pは何も変えない(P・P-strict・Q・Q'全てで確定→確定(同じ範囲)62)。引用符を含む指摘は4件(全体を“ ”で囲んだ形で、L1で確定済み)。Stage 1の生LLM出力に説明文混入は出ていない(委任_53の結論と一致)。

### (d) 参考
- 非BLOCKINGの確定不能(K1): 現行(ON)で6行。うち4行が全ての方式で確定(「Headline: “A”; also, “B”」「“A” and the description of this as a “B”」「“…” (in the passage stating …)」×2)。確定不能のまま2行: 「The human backup plan; “…”」(外の語句が記事に3語以上の逐語で存在するため拒否。意図どおりの安全側)と、言い換え1行(`The price movement seemed to show …`、断片が記事に無い)。
- `same_fact_id_locations`の14件(参考、Recheck出力で現行では展開されない): 案Pで5件が新たに確定(「Paragraph beginning “People asking Muse to call”」「Paragraph 5: “…”」×2「Paragraph 8: “…”」「In one line: “…”」)、現行で既に確定する2件(引用符で囲まれた逐語1件と日本語の正常文1件。L1等で逐語に一致するのに、`expand_same_fact_id_locations`が生の文字列の部分文字列かで弾いている形)。位置ラベルだけの引用`“In one line”`系3件は構造ラベルのため`label_only`で確定不能のまま(誤って見出しを範囲にしない)。「Paragraph 5」「Paragraph 7」の位置だけの2件と、省略記号「…」を含む引用2件(記事に無い文字列)も確定不能のまま。
- 副次的な観察: `expand_same_fact_id_locations`の「逐語の部分文字列」条件を、現行照合で確定するかに置き換えるだけで、引用符で囲まれた列挙の取りこぼしが減る。本委任では実装しない(新しい仕様候補、報告のみ)。

## 4. 作業4: 自己点検とOpusへの論点

### 4-1. 「見送り以外の合理的な手段を十分検討したか」(ユーザー指示§8)

結論: 検討した。見送り(案T)は、原因が特定でき、副作用が小さく、QCD上も合理性があるので推奨しない。

| 案 | 検討した根拠 | 見送りの4条件(原因特定不能/複数案で改善なし/副作用大/QCD合理性なし)への該当 |
|---|---|---|
| P | 13行全て型化でき、引用は引用符で囲まれ、取り出し後は記事に逐語一致。346行で悪化0 | 該当せず |
| P-strict/Q | 宙に浮いた位置語を拒否/裏付け付き補完。12/13行を意図どおり採用 | 該当せず |
| R | 発生源を減らせるが、検出への影響が測れない(H3・H4が残る)。約¥65〜130 | 副作用が不明。測定コストはあるが排除条件ではない |
| S | S1は実質P、S2は委任_35の判断を覆す | 該当せず |
| T(見送り) | 13行が人間確認に回り続けるが、安全 | 原因は特定できており、4条件のどれにも当たらないので推奨しない |

### 4-2. 私の推奨と、推奨しない理由(Fableが最終判断)

- **推奨: 案P-strict**(追加方式、現行確定には触れない)。さらに裏付けのある補完まで含める案Qは、Recheck列挙が無効なときのU11型に効くので、追加価値と実装の広さ(`dev`受け渡し)を見て判断。
- 推奨しない: 案P(lenient。部分採用の恐れ)、案Q'(説明文の語から範囲を広げる)、案R(検出影響が測れず、Pで足りなければ次)、前回方式の再試行(H5)、案T単独。
- 注意: 混入の実際の頻度は現行構成では低い(1-3)。Pは安全網であり、効果の大きさで正当化する案ではない。

### 4-3. Opusに見てほしい論点

ユーザー指示の§7(10項目)の本文は本委任に含まれていない(委任文では§4〜6のみ引用)。下は私が立てた論点で、§7との対応づけはFableが照合してください。

| # | 論点 | 材料の場所 |
|---|---|---|
| 1 | 案PはL4の条件緩和であり、「残りを捨てる」ことが再推測にあたらないか | 1-6、案P |
| 2 | 残りが記事の3語以上の逐語なら拒否するガードの十分性、語数の閾値(感度1〜6) | 案P、(a)の感度、合成テスト3 |
| 3 | 宙に浮いた位置語の拒否(P-strict)が、説明文を「読む」ことで再推測に近づかないか(範囲拡張には使わず拒否のみ) | 案P-strict |
| 4 | 案Qの補完(同じdeviationの別欄、構造要素に限定)が「別AIの引用で決めない」方針と整合するか。Q'は不可とする判断 | 案Q |
| 5 | U06のように、説明文が断片より広い範囲を示唆する場合の扱い(決定論で判別不能) | (a)U06 |
| 6 | 「前回の検出低下の原因は特定不能、Checkerを変えない案Pなら回避」という整理の妥当性。H1〜H5の評価 | 1-5 |
| 7 | 案Pの採用が`prior_issues`の入力(確定範囲)を清浄にし、Recheckの混入のエコーを断つという副次効果 | 1-3、案P |
| 8 | `expand_same_fact_id_locations`の「逐語の部分文字列」条件が、引用符つきの正常な列挙を捨てている件(新しい仕様候補) | (d)、3(d)の副次的な観察 |
| 9 | 346行で悪化0の再生が、混入13行の少数サンプルに依存する点。新しい混入型への汎化 | 3(b)、合成テスト |
| 10 | Production配線時の位置(`_resolve_claim_string`の末尾)と、既存の安全装置(label_only・multi_match・fail-closed)との整合 | 案P、3(b) |

### 4-4. 確認できたことと推測の区別

- 確認できたこと(記録・コード・再生): 混入の型、全て引用符で囲まれていること、346行の再生結果、委任_53の呼び出し単位の統計、Recheckの`same_fact_id_locations`キーの有無、Recheckの指示文の中身、スキーマの順序。
- 推測(私の見立て): U11が(a)と(c)の両方であるという分類、Recheckが複数箇所を詰める動機、エコーの影響(8件中2件は前周回が混入文字列だった事実のみ確認、因果は未確認)、H1の因果。
- 未確認: 実機Promptの全文(記録されていない)、時期の交絡(1-3のFisher検定は交絡あり)、案Rの検出への影響。

## 5. 作成物と制約

- 作成: `docs/pm/design_open233_explanatory_mixed_countermeasures_01.md`(本書)、`er052_output/open233_explanatory_mixed_offline_check_01/`の4ファイル。
- 変更なし: runner・Prompt・テスト・SSOT・既存doc。`er052_open233_self_recovery_flow_runner_01.py`と`er052_open233_self_recovery_stage2_*.py`は委任_55が編集中のため、runnerを`import`するスクリプトは使わず、`check_01.py`は標準ライブラリのみ。
- LLM/API呼び出し: なし(¥0)。git操作: なし。
