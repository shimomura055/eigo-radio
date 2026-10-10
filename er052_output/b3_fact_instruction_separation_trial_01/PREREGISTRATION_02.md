# PREREGISTRATION_02(確定版。結果を見る前に固定。PREREGISTRATION_01を置換)

管理ID: B3-FACT-INSTRUCTION-SEPARATION-ROOTFIX-TRIAL-01 委任_03 Phase 2。確定日 2026-10-10。**本書の確定後に有料APIを呼ぶ。結果を見ての基準変更・Prompt修正・再実行は禁止**(技術retryのみ可)。
Production code / Production Prompt / CURRENT_SPEC は変更しない。後段AI(新Checker・二重チェック・A-B統合・多数決・補正AI)は追加しない。

## 1. 腕・テーマ・入力
- テーマ: 正式9(問題5=semiconductor_earnings, small_bag, space_weapons, hormuz, central_bank_mortgage / 正常系4=meta, byd_recall, openai_copyright, streaming_price)。台帳(`g0_real_annotation_01/<slug>/shared/ledger.txt`)・topic(同`topic.txt`)は凍結。実行時にsha256を記録。Research/Ledgerは再実行しない。
- **C0** Control-frozen: 既存`brief_original.md`(各1、LLM 0)。
- **C1** Control-fresh: 現行Production B3(`er019_family_x_storyline_b3_fact_selection_01.run_storyline_b3_selection`を未改変import、model=`vfl01.MODEL`、effort=`vfl01.REASONING_EFFORT`)で同台帳から再生成、9テーマ×2rep=18 call。
- **D** 決定論assemble(`b3sep_build_01.py`)。**既存B3 callの`selected_fact_ids`を使い、`selected_fact_brief`出力は無視**。入力は C0+C1(27通りのid集合)。変種: D-min(claimのみ)、D-full(claim+scope+conditions)。Dtag(台帳の`[AMBIGUOUS - …]`タグ原文をFact行頭に保持)は比較用preview(E10/E1のみ)。LLM 0。
- **A'** B3 PromptのTrialコピー(`b3sep_b3_aprime_01.py`、差分は`PROMPT_DIFF.md`の3箇所のみ)で9テーマ×2rep=18 call。Factsは出力`selected_fact_brief`、制約は決定論転記。後段補正は足さない。
- 腕D'(Prompt削除)は実施しない。B3 Prompt(Production)は変更しない。
- 使用モデル: B3 = `gpt-6-luna`(Production B3と同一条件。gpt-6世代の最新だが最上位系かは未確認)。R0(E9) = `gpt-6-luna`(effort=high、Trial同一Prompt)。requested/returned model不一致はSTOP。

## 2. Fact組立の確定規則(D)
1. **Fact行**: 1 fact=1行`- {claim}`(出典リンク`([host](url))`除去)。並び順は**B3の`selected_fact_ids`順**(台帳順ではない)。
2. **AMBIGUOUS(R1)**: 台帳タグが`AMBIGUOUS`のfactは、Fact行末に決定論の固定限定文「この点は確定していない。」を付与。`ambiguity_note`は制約側へ。
3. **制約ブロック(R5)**: 見出し`Writerへの注意(事実ではありません)：`の下に、`- 事実{N}について：{notes_for_writer}`(逐語、リンク除去のみ)。Nは制約が対応するFact行の1始まり番号(=後工程の【事実N】番号と一致)。**台帳ID(HF-006等)は出さない。【】は使わない。** `ambiguity_note`は同形式で追記。
4. **D-full(R4)**: Fact行に`（範囲：{scope}。条件：{conditions}）`を追記。scope/conditionsのテキストが指示調検出器(`b3sep_build_01.IMP`)に該当する場合は**Fact側に入れず**、制約側へ`事実{N}の範囲/条件について：…`として回す。
5. **連結(R2)**: `compose_news_field(facts_text, constraints_text)`の**1関数**だけがR0ニュース欄を作る(Facts + 空行 + 制約ブロック。P-out)。evidence JSONの`selected_fact_brief_text`欄は維持し中身を決定論のFacts部にする。制約は`writer_constraints_text`、連結結果は`writer_news_field_text`に置く(DESIGN_02.md参照)。
6. 数値印(【中核数値】/【周辺数値】)は本Trialでは付与しない(未解決課題。E7で明記)。

### D-min / D-full の採用候補規則(E5に基づく)
D-fullを「採用候補」とするのは次を**全て**満たすとき。満たさなければD-min(同点・差が小さい場合もD-min)。
 (i) E5の「台帳根拠あり欠落語」の27組合計が、D-minより**max(10語, D-min欠落の15%)以上少ない** (ii) D-fullのFacts部でE1検出0 (iii) D-full Facts総文字数がD-minの**1.7倍以下**(¥0 previewで1.61倍=C0 ids 9テーマで測定済み) (iv) 人間目視で、D-full追加情報が事実の範囲・条件であり指示調を含まない。
E9にはこの規則で選ばれた1変種のみを流す。

## 3. 評価(決定論スクリプト`b3sep_eval_01.py`+人間目視。LLM判定を使わない)
共通: 全角英数→半角(NFKC)。数字トークン=`\d[\d,\.]*`、固有名詞/語彙トークン=NFKC後の`[一-龥ァ-ヶーA-Za-z0-9]{3,}`連続。
- **E1 命令文漏れ**: Facts部の各文(「。」区切り)を検出器`IMP`で判定(`trace_5themes.json`の手作業ラベル10件に対する再現率10/10を先に確認[確認済み])。**C1・A'の全Facts文は人間が全件目視**し、A'の目視は腕名を伏せたblind表(C1/A'/Dを混ぜ、乱数ID、対応表は別ファイル)で行う。合格: D=27出力で0件。A'=18出力中17以上で0件、残りは内容が許容される事実限定かを目視判定。C1/C0は発生率の測定(合否なし)。
- **E2 notes継承**: 採用factの`notes_for_writer`が制約ブロックに**文字列完全一致**で存在する割合(リンク除去後)。D・A': 100%。C0/C1は、briefに各notesの12字以上の一致があるかで測定。
- **E3 数値・日付**: 採用factの`claim`中の数字トークンが、Facts部(+制約)に全て存在する割合、かつFacts部に台帳(選定fact全欄)にない数字トークンが無いこと。D: 100%。A': 95%以上(欠落・新数字は全件列挙し重大度を目視)。
- **E4 主体・因果・時系列**: (a)claimの固有名詞トークンの包含率 (b)因果接続語(ため/から/により/受け/原因/理由/ことで)の出現数がclaim合計より増えていないか (c)日付出現順がclaimと同じか。D: 全て差0。A': 差分全件目視、意味を変える差分0。問題5テーマは全差分目視。
- **E5 情報欠落(C0/C1比)**: 各controlのFacts語彙トークンのうち、新Facts+制約に無いものを「欠落語」とし、(1)選定factの台帳全欄に根拠あり(=Fact情報の欠落) (2)選定外factの台帳にのみ根拠 (3)台帳に無い(B3の言い換え・新規) に分類。台帳根拠ありFact情報の欠落は0が理想、残りは人間が重大度判定。
- **E6 乾式組立(全消費経路、R2)**: Trial moduleの出力から次の全経路で同じ入力が組めることを、**Production codeを読むだけ・unmodifiedの関数呼び出しのみ**で示す: (a)R0ニュース欄(`jaw.build_original_prompt`、`fl.build_r0_block`、R0テンプレートshaがProduction一致、制約ブロックがちょうど1回) (b)er019 entertainment runner L159/174/339/361相当(`selected_fact_brief_text`をrun_ja_writerへ渡す経路) (c)er012_e再生成経路L740-772/L1185相当(`fact_evidence.get("selected_fact_brief_text")`) (d)W-1系`annotated_json_from`/`md_facts_of_json`(runner L225-239)・`dryrun_annotate`・dev fixture adapter(`er052_open233_polysemy_nb_dev_01.parse_brief_md`と`parse_brief_md`の同一性)・`parse_brief_md`。加えて Fact行に`【`が無い、`【事実N】`数==Fact行数。全項目PASS。1つでも不一致はSTOP。
- **E7 注記LLM不要化(報告のみ・合否なし)**: 【事実N】→台帳ID対応の決定論化の実証(D出力の行番号==fact_idのmapが機械的に取れ、`dryrun_annotate`+期待値計算が通る)。数値印の種類/概念付与は未解決と明記。
- **E8 コスト・時間・複雑性**: 実測¥(cost logger)、B3 latency、assembler/eval LOC、追加LLM call(D=0, A'=0)。B3 1 call¥が現行(C1)比+20%を超えない(A')。
- **E9 Writer R0乾式(有料、ON)**: 6テーマ(問題5+byd_recall) × {D(規則2.で選ばれた変種、C0のids), C0 brief} × R0 1回 = 12 call。**R0のみ**(R1/R2/Astraなし、JA Fact Check呼出なし=`full_ledger_text=None`)。Fact Lock R0 Prompt = Production同一(`fl.apply_factlock_patches`)。両腕とも同じ`dryrun_annotate`で【事実N】を付与(数値印なし=両腕共通の限界)。測定: (1)制約行への【事実N】付与の有無 (2)制約文の記事転記(制約文と記事の10字以上の逐語一致) (3)台帳ID(`ID_RE`)・台帳内部語(Ledger/台帳/notes/事実ではありません/「事実Nについて」)の記事への漏出 (4)AMBIGUOUS限定(「確定していない」等)の記事反映 (5)BYD型(notesが新たに届く)での挙動 (6)音声化禁止記号Gate(`safety.detect_prohibited_symbols(…,"ja")`)該当数 (7)R0既存自己検証(タグ整合: 使用タグ⊆Fact番号集合、`assert_no_tag_leak`)PASS率 (8)R0冒頭復唱`detect_r0_echo` (9)HF-007型「Ledger上では…」の逐語転記有無。目安合格: D腕で(1)=0、(3)=0、(7)=100%、(6)がC0以下、(2)がC0を超えない。全文は目視。
- **E10 AMBIGUOUS保持**: 選択されたAMBIGUOUS Factについて、(a)Fact行に固定限定文、(b)`ambiguity_note`が制約側にある、の両方がWriter入力に存在する割合。D: **100%**。A'/C0/C1は限定の有無を12字一致または目視で測定(合否なし)。

## 4. 判定ルール
- D「Trial限定のVALIDATED候補」: E1・E2・E3・E4・E6・E10を満たし、E5の台帳根拠ありFact情報の欠落が(人間判定で)許容範囲、E9の目安合格、STOP条件非該当。
- A'同候補: E1(17/18)・E3・E4・E6、後段補正AI不要。従わなければ不採用。
- どちらも満たさない場合REJECTED。いずれもProduction採用は人間ユーザーのみ。**VALIDATEDでもProduction実装へ進まない**(`APPROVED_FOR_PRODUCTION`ではない)。

## 5. 費用・Cap・STOP
- Cap **累計¥60**(B3 36 call 約¥18〜22 + E9 12 call 約¥15 + 再試行余裕)。**最初のB3 call実測後に再見積**し、超える見込みならSTOP。台帳`cost_ledger_b3sep_01.jsonl`(call単位、`row_cost_usd`と同じ単価表)。
- 技術retryのみ(B3は既存の1回retry)。結果を見ての再実行禁止。
- STOP: cap超過見込み / B3入力が過去Trialと意味的に異なる(台帳sha不一致) / 新LLM工程が必要 / Research・Ledger仕様変更が必要 / 評価script不具合 / 危険な結果を見てPrompt修正したくなった場合 / model不一致。

## 6. 検出器・過学習の注意
`IMP`は`trace_5themes.json`の10件を見て作った(PREREGISTRATION_01から)ため過学習の可能性がある。そのためC1・A'は人間全件目視。D-fullの振り分けにも同じ検出器を使うため、検出漏れの指示調がFact側に残る可能性は目視で確認する。
## 7. 並列化
C1/A'(各18 call)は台帳・topic凍結のため条件同一性を保てる。テーマ単位の複数processで並列実行(process別ログ→親が合算)。最初の1 callのみ直列(実測再見積のため=Cap確認)。E9はE5に基づく変種選択に依存するため直列。
## 8. 成果物の保存先
`er052_output/b3_fact_instruction_separation_trial_01/`: `runs/<arm>/<theme>/rep<n>/`、`eval/`、`cost_ledger_b3sep_01.jsonl`、`HUMAN_CHECK_B3SEP_01.md`、`RESULT_01.md`、DESIGN_02.md、PROMPT_DIFF.md。
