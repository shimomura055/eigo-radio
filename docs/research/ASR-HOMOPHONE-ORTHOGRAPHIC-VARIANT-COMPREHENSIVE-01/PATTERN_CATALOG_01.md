# PATTERN_CATALOG_01(ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01 委任_01、2026-10-22。API 0・Production無編集)

生成: `er109_pattern_catalog_md_01.py`(入力=`pattern_probe_01.json`=`er109_pattern_probe_01.py`の実行結果)。ユーザー例示は下限であり、本表は体系的な洗い出し(数/所有格・短縮形/同音異綴/語境界/略語・記号/ハイフン・句読点・大小/ASR自動整形)の代表例149件。

## 凡例
- 判定列は、本文P=本文role(FULL_STORY)のProduction相当経路(`classify_asr_match(segment_id)`+同音救済+**非KPの最終ANDゲート**[承認済みequivalence_basisは本物のjudgeと同じくskip])、KP-P=Key Phrase(`kp1_en`)のP/S票相当、Whisper票=`er104._classify`。M1/CS Equivalence/Tier3は再現していない(wav/Azure/凍結候補が要るため。近似層でありここでの対象外)。
- **er109**=提案層(未配線プロトタイプ)。CMU音素列(ストレス無視)と閉じた記号・略語表で同値判定。未登録語・解析不能・欠落/付加は同値にしない(fail-closed)。
- 分類: **A**=既存で対応済み(全経路PASS)、**B**=既存承認仕様の不具合(承認済み規則の意図する範囲なのに、実装/層間の不整合や到達不能でNG。自律修正可・次委任)、**B/C境界**=承認文言の再確認が必要、**C**=新規救済範囲(Trial->VALIDATED->ユーザー採用判断。**C-KP**=本文は既存Tier1でPASSだがKP/Whisper票はTier1非適用[承認済み仕様]のため不合格、KPへの拡張=新規救済範囲)、**D**=発音が異なる/ユーザー不採用の口語縮約 -> 同等にしない(負例、NGのまま)、**E**=CMU辞書の限界・未対応記号で判定不能(同値化しない=残存偽NG)。
- 偽PASSリスク欄は設計案(DESIGN_PROPOSAL_01.md §3)の負例評価を参照: 提案層による新規誤同値は負例35(カタログ)+KP 3,049+本文3,749(機械生成)で**0**。

## 集計
- 正例(同一発音、n=114): 本文P(最終ゲート後) 82、KP-P 68、Whisper票 68、**er109 107**
- 負例(発音が異なる、n=35): 既存の誤PASS 1(N30: 値は同じで読みだけ違う=承認済み値等価)、**er109の誤同値 0**
- 分類件数: A=67, B=5, B/C境界=3, C=20, C-KP=14, D=35, E=5


## 表
| ID | 区分 | 期待文 / ASR転写 | 本文P(最終ゲート後) | KP-P | Whisper票 | er109 | 分類 | 根拠・対策 |
|---|---|---|---|---|---|---|---|---|
| N01 | number | `one` / `1` | PASS(NUMERIC_EQUIVALENCE_MATCH) | NG | NG | 同値(all_diff_spans_phoneme_e) | C-KP | 本文はTier1(5role限定)でPASS。Key Phrase/Whisper票はTier1非適用(承認済み仕様: CURRENT_SPEC.md:2159)のため不合格 -> KPへの適用拡張=新規救済範囲 |
| N02 | number | `pump one's fist` / `Pump 1's fist.` | NG | NG | NG | 同値(all_diff_spans_phoneme_e) | C | ユーザー必須例。`one's`はTier1/値ガードでliteral1語、`1's`はnumber atom=対応なし→DIFF(AZURE_ITN_IMPACT_01 §2)。KPは保護解除済みでもclassify_asr_matchが数字<->語を同値化しない(val:313 単独oneは変換しない+Tier1はKey Phrase非適用) |
| N03 | number | `the right one` / `the right 1` | PASS(NUMERIC_EQUIVALENCE_MATCH) | NG | NG | 同値(all_diff_spans_phoneme_e) | C-KP | 本文はTier1(5role限定)でPASS。Key Phrase/Whisper票はTier1非適用(承認済み仕様: CURRENT_SPEC.md:2159)のため不合格 -> KPへの適用拡張=新規救済範囲 |
| N04 | number | `two apples` / `2 apples` | PASS(NUMERIC_EQUIVALENCE_MATCH) | PASS | PASS | 同値(all_diff_spans_phoneme_e) | A | 既存で対応済み(全経路PASS) |
| N05 | number | `twelve years` / `12 years` | PASS(NUMERIC_EQUIVALENCE_MATCH) | PASS | PASS | 同値(all_diff_spans_phoneme_e) | A | 既存で対応済み(全経路PASS) |
| N06 | number | `twenty-eight days` / `28 days` | PASS(NUMERIC_EQUIVALENCE_MATCH) | PASS | PASS | 同値(all_diff_spans_phoneme_e) | A | 既存で対応済み(全経路PASS) |
| N07 | number | `one hundred and five` / `105` | PASS(NUMERIC_EQUIVALENCE_MATCH) | PASS | PASS | 同値(all_diff_spans_phoneme_e) | A | 既存で対応済み(全経路PASS) |
| N08 | number | `one thousand two hundred` / `1,200` | PASS(NUMERIC_EQUIVALENCE_MATCH) | PASS | PASS | 同値(all_diff_spans_phoneme_e) | A | 既存で対応済み(全経路PASS) |
| N09 | number | `two million people` / `2 million people` | PASS(NUMERIC_EQUIVALENCE_MATCH) | NG | NG | 同値(all_diff_spans_phoneme_e) | C-KP | 本文はTier1(5role限定)でPASS。Key Phrase/Whisper票はTier1非適用(承認済み仕様: CURRENT_SPEC.md:2159)のため不合格 -> KPへの適用拡張=新規救済範囲 |
| N10 | number | `third place` / `3rd place` | PASS(NUMERIC_EQUIVALENCE_MATCH) | PASS | PASS | 同値(all_diff_spans_phoneme_e) | A | 既存で対応済み(全経路PASS) |
| N11 | number | `the twenty first century` / `the 21st century` | NG(NORMALIZED_MATCH) | PASS | PASS | 同値(all_diff_spans_phoneme_e) | B | 承認済みの複合序数正規化(val._convert_compound_ordinal_words)でclassifyはPASSなのに、非KPの最終ANDゲートの値atom(er021 _tier1_atoms)が`twenty first`を20+literalと解釈し`21st`と値DIFF→NG_PROTECTED(実judgeで再現)。層間不整合の不具合 |
| N12 | number | `in twenty twenty four` / `in 2024` | PASS(NUMERIC_EQUIVALENCE_MATCH) | NG | NG | 同値(all_diff_spans_phoneme_e) | C-KP | 本文はTier1(5role限定)でPASS。Key Phrase/Whisper票はTier1非適用(承認済み仕様: CURRENT_SPEC.md:2159)のため不合格 -> KPへの適用拡張=新規救済範囲 |
| N13 | number | `in nineteen ninety` / `in 1990` | PASS(NUMERIC_EQUIVALENCE_MATCH) | NG | NG | 同値(all_diff_spans_phoneme_e) | C-KP | 本文はTier1(5role限定)でPASS。Key Phrase/Whisper票はTier1非適用(承認済み仕様: CURRENT_SPEC.md:2159)のため不合格 -> KPへの適用拡張=新規救済範囲 |
| N14 | number | `in two thousand and five` / `in 2005` | PASS(NUMERIC_EQUIVALENCE_MATCH) | PASS | PASS | 同値(all_diff_spans_phoneme_e) | A | 既存で対応済み(全経路PASS) |
| N15 | number | `the nineties` / `the 90s` | NG | NG | NG | 同値(all_diff_spans_phoneme_e) | C | 年代`90s`/`nineties`はTier1の列挙外(列挙: 数値/通貨/%/年/時刻/分数/ローマ数字/略語) |
| N16 | number | `three point five` / `3.5` | PASS(NUMERIC_EQUIVALENCE_MATCH) | PASS | PASS | 同値(all_diff_spans_phoneme_e) | A | 既存で対応済み(全経路PASS) |
| N17 | number | `zero point five` / `0.5` | PASS(NUMERIC_EQUIVALENCE_MATCH) | NG | NG | 同値(all_diff_spans_phoneme_e) | C-KP | 本文はTier1(5role限定)でPASS。Key Phrase/Whisper票はTier1非適用(承認済み仕様: CURRENT_SPEC.md:2159)のため不合格 -> KPへの適用拡張=新規救済範囲 |
| N18 | number | `one half` / `1/2` | PASS(NUMERIC_EQUIVALENCE_MATCH) | NG | NG | 同値(all_diff_spans_phoneme_e) | C-KP | 本文はTier1(5role限定)でPASS。Key Phrase/Whisper票はTier1非適用(承認済み仕様: CURRENT_SPEC.md:2159)のため不合格 -> KPへの適用拡張=新規救済範囲 |
| N19 | number | `three quarters` / `3/4` | PASS(NUMERIC_EQUIVALENCE_MATCH) | NG | NG | 同値(all_diff_spans_phoneme_e) | C-KP | 本文はTier1(5role限定)でPASS。Key Phrase/Whisper票はTier1非適用(承認済み仕様: CURRENT_SPEC.md:2159)のため不合格 -> KPへの適用拡張=新規救済範囲 |
| N20 | number | `at five thirty` / `at 5:30` | NG | NG | NG | 同値(all_diff_spans_phoneme_e) | B/C境界 | Tier1は『時刻』を謳うが`five thirty`<->`5:30`は未パース(_tier1_atomsがfive=literal/30=number)。承認文言の再確認要(Fable) |
| N21 | number | `at five o'clock` / `at 5:00` | NG | NG | NG | 同値(all_diff_spans_phoneme_e) | B/C境界 | Tier1『時刻』の`o'clock`<->`5:00`未パース。同上 |
| N22 | number | `at eight a m` / `at 8 a.m.` | PASS(NORMALIZED_MATCH) | PASS | PASS | 同値(all_diff_spans_phoneme_e) | A | 既存で対応済み(全経路PASS) |
| N23 | number | `thirty percent` / `30%` | PASS(NUMERIC_EQUIVALENCE_MATCH) | PASS | PASS | 同値(all_diff_spans_phoneme_e) | A | 既存で対応済み(全経路PASS) |
| N24 | number | `30 percent` / `30%` | PASS(NUMERIC_EQUIVALENCE_MATCH) | PASS | PASS | 同値(all_diff_spans_phoneme_e) | A | 既存で対応済み(全経路PASS) |
| N25 | number | `five dollars` / `$5` | PASS(NUMERIC_EQUIVALENCE_MATCH) | PASS | PASS | 同値(all_diff_spans_phoneme_e) | A | 既存で対応済み(全経路PASS) |
| N26 | number | `five dollars and fifty cents` / `$5.50` | NG | NG | NG | 同値(all_diff_spans_phoneme_e) | B/C境界 | Tier1『通貨』の`$5.50`<->`five dollars and fifty cents`未パース(セント語)。同上 |
| N27 | number | `ten euros` / `€10` | PASS(NUMERIC_EQUIVALENCE_MATCH) | NG | NG | 同値(all_diff_spans_phoneme_e) | C-KP | 本文はTier1(5role限定)でPASS。Key Phrase/Whisper票はTier1非適用(承認済み仕様: CURRENT_SPEC.md:2159)のため不合格 -> KPへの適用拡張=新規救済範囲 |
| N28 | number | `minus five` / `-5` | PASS(NUMERIC_EQUIVALENCE_MATCH) | NG | NG | 同値(all_diff_spans_phoneme_e) | C-KP | 本文はTier1(5role限定)でPASS。Key Phrase/Whisper票はTier1非適用(承認済み仕様: CURRENT_SPEC.md:2159)のため不合格 -> KPへの適用拡張=新規救済範囲 |
| N29 | number | `two's company` / `2's company` | NG | NG | NG | 同値(all_diff_spans_phoneme_e) | C | 数詞+'s(`2's`/`two's`)。one's<->1's と同型 |
| N30 | number | `a hundred dollars` / `$100` | PASS(NORMALIZED_MATCH) | PASS | PASS | 非同値(phoneme_differs) | D | 値は同じだが読み(a hundred/one hundred)が違う。既存はPASSさせる(承認済み値等価)。同等にするかではなく現状維持 |
| N31 | number | `I have two cats` / `I have to cats` | PASS(HOMOPHONE_MATCH_NUMBER_EXCEPTION) | PASS | PASS | 同値(all_diff_spans_phoneme_e) | A | 既存で対応済み(全経路PASS) |
| N32 | number | `four people` / `for people` | PASS(HOMOPHONE_MATCH_NUMBER_EXCEPTION) | PASS | PASS | 同値(all_diff_spans_phoneme_e) | A | 既存で対応済み(全経路PASS) |
| N33 | number | `one person` / `won person` | PASS(HOMOPHONE_EQUIVALENT) | PASS | PASS | 同値(all_diff_spans_phoneme_e) | A | 既存で対応済み(全経路PASS) |
| X01 | neg_number | `two` / `three` | NG | NG | NG | 非同値(phoneme_differs) | D | 発音が異なる/ユーザー不採用の口語縮約 -> 同等にしない(負例) |
| X02 | neg_number | `2 apples` / `3 apples` | NG | NG | NG | 非同値(phoneme_differs) | D | 発音が異なる/ユーザー不採用の口語縮約 -> 同等にしない(負例) |
| X03 | neg_number | `ten` / `100` | NG | NG | NG | 非同値(phoneme_differs) | D | 発音が異なる/ユーザー不採用の口語縮約 -> 同等にしない(負例) |
| X04 | neg_number | `in 1990` / `in 1999` | NG | NG | NG | 非同値(phoneme_differs) | D | 発音が異なる/ユーザー不採用の口語縮約 -> 同等にしない(負例) |
| X05 | neg_number | `3.5` / `35` | NG | NG | NG | 非同値(phoneme_differs) | D | 発音が異なる/ユーザー不採用の口語縮約 -> 同等にしない(負例) |
| X06 | neg_number | `$5` / `5%` | NG | NG | NG | 非同値(phoneme_differs) | D | 発音が異なる/ユーザー不採用の口語縮約 -> 同等にしない(負例) |
| X07 | neg_number | `thirteen` / `thirty` | NG | NG | NG | 非同値(phoneme_differs) | D | 発音が異なる/ユーザー不採用の口語縮約 -> 同等にしない(負例) |
| X08 | neg_number | `fifteen` / `fifty` | NG | NG | NG | 非同値(phoneme_differs) | D | 発音が異なる/ユーザー不採用の口語縮約 -> 同等にしない(負例) |
| X09 | neg_number | `the 3rd` / `the 4th` | NG | NG | NG | 非同値(phoneme_differs) | D | 発音が異なる/ユーザー不採用の口語縮約 -> 同等にしない(負例) |
| X10 | neg_number | `1,000` / `1.000` | NG | NG | NG | 非同値(phoneme_differs) | D | 発音が異なる/ユーザー不採用の口語縮約 -> 同等にしない(負例) |
| X11 | neg_number | `at 5:30` / `at 5:13` | NG | NG | NG | 非同値(phoneme_differs) | D | 発音が異なる/ユーザー不採用の口語縮約 -> 同等にしない(負例) |
| C01 | contraction | `it's` / `its` | PASS(NORMALIZED_MATCH) | PASS | PASS | 同値(surface_equal_after_norm) | A | 既存で対応済み(全経路PASS) |
| C02 | contraction | `they're here` / `their here` | NG | NG | NG | 同値(all_diff_spans_phoneme_e) | C | they're/their/there: 承認済み同音救済は内容語1:1のみ(stopwordは対象外 val:742)。contraction展開は展開後に既存が一致する場合のみ |
| C03 | contraction | `they're here` / `there here` | NG | NG | NG | 同値(all_diff_spans_phoneme_e) | C | 同上 |
| C04 | contraction | `you're right` / `your right` | NG | NG | NG | 同値(all_diff_spans_phoneme_e) | C | 同上(you're/your) |
| C05 | contraction | `who's there` / `whose there` | NG | NG | NG | 同値(all_diff_spans_phoneme_e) | C | 同上(who's/whose) |
| C06 | contraction | `let's go` / `lets go` | PASS(NORMALIZED_MATCH) | PASS | PASS | 同値(surface_equal_after_norm) | A | 既存で対応済み(全経路PASS) |
| C07 | contraction | `I'm here` / `I am here` | PASS(TRANSCRIPT_STYLE_NORMALIZED_MATCH) | PASS | PASS | 同値(all_diff_spans_phoneme_e) | A | 既存で対応済み(全経路PASS) |
| C08 | contraction | `it's here` / `it is here` | PASS(TRANSCRIPT_STYLE_NORMALIZED_MATCH) | PASS | PASS | 同値(all_diff_spans_phoneme_e) | A | 既存で対応済み(全経路PASS) |
| C09 | contraction | `I can't go` / `I cannot go` | PASS(TRANSCRIPT_STYLE_NORMALIZED_MATCH) | PASS | PASS | 同値(all_diff_spans_phoneme_e) | A | 既存で対応済み(全経路PASS) |
| C10 | contraction | `o'clock` / `oclock` | PASS(NORMALIZED_MATCH) | PASS | PASS | 同値(surface_equal_after_norm) | A | 既存で対応済み(全経路PASS) |
| C11 | contraction | `John's book` / `Johns book` | PASS(NORMALIZED_MATCH) | PASS | PASS | 同値(surface_equal_after_norm) | A | 既存で対応済み(全経路PASS) |
| C12 | contraction | `I can't go` / `I can go` | NG | NG | NG | 非同値(phoneme_differs) | D | 発音が異なる/ユーザー不採用の口語縮約 -> 同等にしない(負例) |
| C13 | contraction | `he's here` / `his here` | NG | NG | NG | 非同値(phoneme_differs) | D | 発音が異なる/ユーザー不採用の口語縮約 -> 同等にしない(負例) |
| C14 | contraction | `I don't know` / `I do know` | NG | NG | NG | 非同値(phoneme_differs) | D | 発音が異なる/ユーザー不採用の口語縮約 -> 同等にしない(負例) |
| C15 | contraction | `I won't go` / `I want go` | NG | NG | NG | 非同値(phoneme_differs) | D | 発音が異なる/ユーザー不採用の口語縮約 -> 同等にしない(負例) |
| C16 | contraction | `I want to go` / `I wanna go` | NG | NG | NG | 非同値(outside_approved_multiwo) | D | 発音が異なる/ユーザー不採用の口語縮約 -> 同等にしない(負例) |
| C17 | contraction | `I'm going to go` / `I'm gonna go` | NG | NG | NG | 非同値(outside_approved_multiwo) | D | 発音が異なる/ユーザー不採用の口語縮約 -> 同等にしない(負例) |
| C18 | contraction | `because it works` / `'cause it works` | NG | NG | NG | 非同値(phoneme_differs) | D | 発音が異なる/ユーザー不採用の口語縮約 -> 同等にしない(負例) |
| H01 | homophone | `wait here` / `weight here` | PASS(HOMOPHONE_EQUIVALENT) | PASS | PASS | 同値(all_diff_spans_phoneme_e) | A | 既存で対応済み(全経路PASS) |
| H02 | homophone | `grey sky` / `gray sky` | PASS(HOMOPHONE_EQUIVALENT) | PASS | PASS | 同値(all_diff_spans_phoneme_e) | A | 既存で対応済み(全経路PASS) |
| H03 | homophone | `colour` / `color` | PASS(NORMALIZED_MATCH) | PASS | PASS | 同値(all_diff_spans_phoneme_e) | A | 既存で対応済み(全経路PASS) |
| H04 | homophone | `whisky` / `whiskey` | NG | NG | NG | 同値(all_diff_spans_phoneme_e) | B | 承認済み同音救済(ER-008-15)が1語テキストでは到達不能: val:1133 のratio<0.4判定(TTS_FAILURE)が同音判定(val:1193)より先。KP英語の12.6%(83/660)が1語 |
| H05 | homophone | `he passed` / `he past` | PASS(HOMOPHONE_EQUIVALENT) | PASS | PASS | 同値(all_diff_spans_phoneme_e) | A | 既存で対応済み(全経路PASS) |
| H06 | homophone | `a flour mill` / `a flower mill` | PASS(HOMOPHONE_EQUIVALENT) | PASS | PASS | 同値(all_diff_spans_phoneme_e) | A | 既存で対応済み(全経路PASS) |
| H07 | homophone | `right now` / `write now` | PASS(HOMOPHONE_EQUIVALENT) | PASS | PASS | 同値(all_diff_spans_phoneme_e) | A | 既存で対応済み(全経路PASS) |
| H08 | homophone | `see the sea` / `sea the sea` | PASS(HOMOPHONE_EQUIVALENT) | PASS | PASS | 同値(all_diff_spans_phoneme_e) | A | 既存で対応済み(全経路PASS) |
| H09 | homophone | `no way` / `know way` | NG | NG | NG | 同値(all_diff_spans_phoneme_e) | C | 否定語noの同音異表記(know)。『発音同一=同等』を適用すると否定保護との関係でユーザー判断(Opus Q) |
| H10 | homophone | `analyze data` / `analyse data` | NG | NG | NG | 非同値(incomparable(CMU未登録/解析不能) | E | analyseがCMU未登録=判定不能(fail-closed)。対策=CMU補完辞書/Ledger(別判断) |
| H11 | homophone | `the theatre` / `the theater` | PASS(HOMOPHONE_EQUIVALENT) | PASS | PASS | 同値(all_diff_spans_phoneme_e) | A | 既存で対応済み(全経路PASS) |
| H12 | homophone | `a licence` / `a license` | PASS(HOMOPHONE_EQUIVALENT) | PASS | PASS | 同値(all_diff_spans_phoneme_e) | A | 既存で対応済み(全経路PASS) |
| H13 | homophone | `judgement` / `judgment` | NG | NG | NG | 同値(all_diff_spans_phoneme_e) | B | 同上(1語テキスト) |
| H14 | homophone | `the tyre` / `the tire` | NG | NG | NG | 非同値(phoneme_differs) | E | tyre(T AY1 R)とtire(T AY1 ER0)がCMU音素表記上で不一致=CMU限界。同値化しない(残存偽NG) |
| H15 | homophone | `he learned` / `he learnt` | NG | NG | NG | 非同値(phoneme_differs) | D | 発音が異なる/ユーザー不採用の口語縮約 -> 同等にしない(負例) |
| H16 | homophone | `it burned` / `it burnt` | NG | NG | NG | 非同値(phoneme_differs) | D | 発音が異なる/ユーザー不採用の口語縮約 -> 同等にしない(負例) |
| H17 | homophone | `my mum` / `my mom` | NG | NG | NG | 非同値(phoneme_differs) | D | 発音が異なる/ユーザー不採用の口語縮約 -> 同等にしない(負例) |
| H18 | homophone | `aluminium` / `aluminum` | NG | NG | NG | 非同値(phoneme_differs) | D | 発音が異なる/ユーザー不採用の口語縮約 -> 同等にしない(負例) |
| H19 | homophone | `wait` / `weight` | NG | NG | NG | 同値(all_diff_spans_phoneme_e) | B | 同上(1語テキスト) |
| H20 | homophone | `take part` / `take tart` | NG | NG | NG | 非同値(phoneme_differs) | D | 発音が異なる/ユーザー不採用の口語縮約 -> 同等にしない(負例) |
| H21 | homophone | `the affect` / `the effect` | PASS(HOMOPHONE_EQUIVALENT) | PASS | PASS | 同値(all_diff_spans_phoneme_e) | A | 既存で対応済み(全経路PASS) |
| H22 | homophone | `better then that` / `better than that` | NG | NG | NG | 非同値(phoneme_differs) | D | 発音が異なる/ユーザー不採用の口語縮約 -> 同等にしない(負例) |
| H23 | homophone | `a ship` / `a sheep` | NG | NG | NG | 非同値(phoneme_differs) | D | 発音が異なる/ユーザー不採用の口語縮約 -> 同等にしない(負例) |
| H24 | homophone | `three men` / `tree men` | NG | NG | NG | 非同値(phoneme_differs) | D | 発音が異なる/ユーザー不採用の口語縮約 -> 同等にしない(負例) |
| H25 | homophone | `very good` / `berry good` | NG | NG | NG | 非同値(phoneme_differs) | D | 発音が異なる/ユーザー不採用の口語縮約 -> 同等にしない(負例) |
| H26 | homophone | `a cat` / `a cut` | NG | NG | NG | 非同値(phoneme_differs) | D | 発音が異なる/ユーザー不採用の口語縮約 -> 同等にしない(負例) |
| H27 | homophone | `increase` / `decrease` | NG | NG | NG | 非同値(phoneme_differs) | D | 発音が異なる/ユーザー不採用の口語縮約 -> 同等にしない(負例) |
| H28 | homophone | `the word` / `the world` | NG | NG | NG | 非同値(phoneme_differs) | D | 発音が異なる/ユーザー不採用の口語縮約 -> 同等にしない(負例) |
| M01 | multiword | `a lot of` / `alot of` | PASS(NORMALIZED_MATCH) | PASS | PASS | 同値(all_diff_spans_phoneme_e) | A | 既存で対応済み(全経路PASS) |
| M02 | multiword | `every one of them` / `everyone of them` | PASS(NORMALIZED_MATCH) | PASS | PASS | 同値(all_diff_spans_phoneme_e) | A | 既存で対応済み(全経路PASS) |
| M03 | multiword | `in to the room` / `into the room` | PASS(NORMALIZED_MATCH) | PASS | PASS | 同値(all_diff_spans_phoneme_e) | A | 既存で対応済み(全経路PASS) |
| M04 | multiword | `work out daily` / `workout daily` | PASS(NORMALIZED_MATCH) | PASS | PASS | 同値(all_diff_spans_phoneme_e) | A | 既存で対応済み(全経路PASS) |
| M05 | multiword | `may be` / `maybe` | PASS(NORMALIZED_MATCH) | PASS | PASS | 同値(all_diff_spans_phoneme_e) | A | 既存で対応済み(全経路PASS) |
| M06 | multiword | `all right` / `alright` | NG | NG | NG | 同値(all_diff_spans_phoneme_e) | B | 承認済みPNMH-01多語同音(er094)が短文で到達不能(同じratio<0.4) |
| M07 | multiword | `by us` / `buy us` | NG | NG | NG | 同値(all_diff_spans_phoneme_e) | C | stopword(by)を含む同音。PNMH-01は固有名詞ByUs型。一般語by/buyは対象外 |
| M08 | multiword | `ice cream` / `I scream` | NG | NG | NG | 非同値(phoneme_differs) | C | ice cream/I scream型(oronym)は承認済み多語同音条件(1:n・単一文字token禁止)の外。er109も同値にしない=新規救済範囲(ユーザー判断) |
| M09 | multiword | `some time` / `sometime` | PASS(NORMALIZED_MATCH) | PASS | PASS | 同値(all_diff_spans_phoneme_e) | A | 既存で対応済み(全経路PASS) |
| M10 | multiword | `a part` / `apart` | PASS(NORMALIZED_MATCH) | PASS | PASS | 同値(all_diff_spans_phoneme_e) | A | 既存で対応済み(全経路PASS) |
| M11 | multiword | `under way` / `underway` | PASS(NORMALIZED_MATCH) | PASS | PASS | 同値(all_diff_spans_phoneme_e) | A | 既存で対応済み(全経路PASS) |
| M12 | multiword | `per cent` / `percent` | PASS(NORMALIZED_MATCH) | PASS | PASS | 同値(all_diff_spans_phoneme_e) | A | 既存で対応済み(全経路PASS) |
| M13 | multiword | `any one` / `anyone` | PASS(NORMALIZED_MATCH) | PASS | PASS | 同値(all_diff_spans_phoneme_e) | A | 既存で対応済み(全経路PASS) |
| M14 | multiword | `take part` / `take apart` | NG | NG | NG | 非同値(phoneme_differs) | D | 発音が異なる/ユーザー不採用の口語縮約 -> 同等にしない(負例) |
| M15 | multiword | `cannot` / `can not` | PASS(NORMALIZED_MATCH) | PASS | PASS | 非同値(phoneme_differs) | A | cannot<->can not: 承認済みdespaced規則/negation_diff正規化で対応済み(er109は不要) |
| A01 | abbrev | `the U.S. economy` / `the US economy` | PASS(NORMALIZED_MATCH) | PASS | PASS | 同値(surface_equal_after_norm) | A | 既存で対応済み(全経路PASS) |
| A02 | abbrev | `the AI model` / `the A.I. model` | PASS(NORMALIZED_MATCH) | PASS | PASS | 同値(surface_equal_after_norm) | A | 既存で対応済み(全経路PASS) |
| A03 | abbrev | `FBI agent` / `F.B.I. agent` | PASS(NORMALIZED_MATCH) | PASS | PASS | 同値(surface_equal_after_norm) | A | 既存で対応済み(全経路PASS) |
| A04 | abbrev | `FBI agent` / `F B I agent` | PASS(NORMALIZED_MATCH) | PASS | PASS | 同値(all_diff_spans_phoneme_e) | A | 既存で対応済み(全経路PASS) |
| A05 | abbrev | `rock & roll` / `rock and roll` | NG | NG | NG | 同値(all_diff_spans_phoneme_e) | C | `&`<->and: 記号読み未対応(承認済みは通り種別略語のみ val:77) |
| A06 | abbrev | `two plus two` / `2 + 2` | NG | NG | NG | 同値(all_diff_spans_phoneme_e) | C | `+`<->plus |
| A07 | abbrev | `twenty degrees` / `20°` | NG | NG | NG | 同値(all_diff_spans_phoneme_e) | C | `°`<->degrees |
| A08 | abbrev | `Tom vs. Jerry` / `Tom versus Jerry` | NG | NG | NG | 同値(all_diff_spans_phoneme_e) | C | `vs.`<->versus |
| A09 | abbrev | `Mr. Smith` / `mister Smith` | PASS(PROPER_NOUN_ENTITY_ARPABET_CONFIRMED) | PASS | PASS | 同値(all_diff_spans_phoneme_e) | A | 既存で対応済み(全経路PASS) |
| A10 | abbrev | `Dr. Lee` / `doctor Lee` | NG | NG | NG | 同値(all_diff_spans_phoneme_e) | C | `Dr.`<->doctor |
| A11 | abbrev | `St. Louis` / `Saint Louis` | NG | NG | NG | 同値(all_diff_spans_phoneme_e) | C | `St.`<->Saint(承認済みはstreet->st方向のみ) |
| A12 | abbrev | `Main Street` / `Main St.` | PASS(NORMALIZED_MATCH) | PASS | PASS | 同値(all_diff_spans_phoneme_e) | A | 既存で対応済み(全経路PASS) |
| A13 | abbrev | `OK` / `okay` | NG | NG | NG | 同値(all_diff_spans_phoneme_e) | C | OK<->okay(1語はratio<0.4でも不達) |
| A14 | abbrev | `etc.` / `et cetera` | NG | NG | NG | 同値(all_diff_spans_phoneme_e) | C | etc.<->et cetera |
| A15 | abbrev | `the TV show` / `the television show` | NG | NG | NG | 同値(all_diff_spans_phoneme_e) | C | CMU辞書のtv変種=television(辞書quirk)。TTSの実読みは音声依存。要Opus確認 |
| A16 | abbrev | `e.g. this` / `for example this` | NG | NG | NG | 非同値(phoneme_differs) | D | 発音が異なる/ユーザー不採用の口語縮約 -> 同等にしない(負例) |
| A17 | abbrev | `a 3D model` / `a three D model` | PASS(NUMERIC_EQUIVALENCE_MATCH) | PASS | PASS | 同値(all_diff_spans_phoneme_e) | A | 既存で対応済み(全経路PASS) |
| A18 | abbrev | `5G network` / `five G network` | PASS(NUMERIC_EQUIVALENCE_MATCH) | PASS | PASS | 同値(all_diff_spans_phoneme_e) | A | 既存で対応済み(全経路PASS) |
| A19 | abbrev | `Wi-Fi` / `wifi` | PASS(NORMALIZED_MATCH) | PASS | PASS | 同値(surface_equal_after_norm) | A | 既存で対応済み(全経路PASS) |
| A20 | abbrev | `COVID-19` / `COVID nineteen` | PASS(NUMERIC_EQUIVALENCE_MATCH) | PASS | PASS | 同値(all_diff_spans_phoneme_e) | A | 既存で対応済み(全経路PASS) |
| A21 | abbrev | `20 degrees Celsius` / `20°C` | NG | NG | NG | 非同値(phoneme_differs) | E | `°C`(単位記号)未対応 |
| A22 | abbrev | `Jan. 5` / `January 5` | NG | NG | NG | 非同値(phoneme_differs) | E | 月名略語(Jan.)未対応(月名と通常語の衝突) |
| A23 | abbrev | `the US` / `the us` | PASS(NORMALIZED_MATCH) | PASS | PASS | 同値(surface_equal_after_norm) | A | CMUのus変種(Y UW EH S)と既存の大小無視により国名US/代名詞usは既存で同一視(承認済み挙動)。注意事項としてOpusへ |
| P01 | punct | `well-being` / `wellbeing` | PASS(NORMALIZED_MATCH) | PASS | PASS | 同値(surface_equal_after_norm) | A | 既存で対応済み(全経路PASS) |
| P02 | punct | `well-being` / `well being` | PASS(NORMALIZED_MATCH) | PASS | PASS | 同値(all_diff_spans_phoneme_e) | A | 既存で対応済み(全経路PASS) |
| P03 | punct | `e-mail` / `email` | PASS(NORMALIZED_MATCH) | PASS | PASS | 同値(surface_equal_after_norm) | A | 既存で対応済み(全経路PASS) |
| P04 | punct | `co-operate` / `cooperate` | PASS(NORMALIZED_MATCH) | PASS | PASS | 同値(surface_equal_after_norm) | A | 既存で対応済み(全経路PASS) |
| P05 | punct | `T-shirt` / `t shirt` | PASS(NORMALIZED_MATCH) | PASS | PASS | 同値(all_diff_spans_phoneme_e) | A | 既存で対応済み(全経路PASS) |
| P06 | punct | `state-of-the-art` / `state of the art` | PASS(NORMALIZED_MATCH) | PASS | PASS | 同値(all_diff_spans_phoneme_e) | A | 既存で対応済み(全経路PASS) |
| P07 | punct | `Hello, world.` / `hello world` | PASS(NORMALIZED_MATCH) | PASS | PASS | 同値(surface_equal_after_norm) | A | 既存で対応済み(全経路PASS) |
| P08 | punct | `the shortcut—fruit` / `the shortcut fruit` | PASS(NORMALIZED_MATCH) | PASS | PASS | 同値(surface_equal_after_norm) | A | 既存で対応済み(全経路PASS) |
| P09 | punct | `“Low” on one side` / `low on one side` | PASS(NORMALIZED_MATCH) | PASS | PASS | 同値(surface_equal_after_norm) | A | 既存で対応済み(全経路PASS) |
| P10 | punct | `ice-cream` / `ice cream` | PASS(NORMALIZED_MATCH) | PASS | PASS | 同値(all_diff_spans_phoneme_e) | A | 既存で対応済み(全経路PASS) |
| P11 | punct | `Apple` / `apple` | PASS(NORMALIZED_MATCH) | PASS | PASS | 同値(surface_equal_after_norm) | A | 既存で対応済み(全経路PASS) |
| T01 | asr_itn | `gonna` / `going to` | NG | NG | NG | 非同値(outside_approved_multiwo) | D | 発音が異なる/ユーザー不採用の口語縮約 -> 同等にしない(負例) |
| T02 | asr_itn | `um, I think so` / `I think so` | NG | NG | NG | 非同値(one_side_empty(欠落・付加は同値に) | D | 発音が異なる/ユーザー不採用の口語縮約 -> 同等にしない(負例) |
| T03 | asr_itn | `twenty twenty-four` / `2024` | PASS(NUMERIC_EQUIVALENCE_MATCH) | NG | NG | 同値(all_diff_spans_phoneme_e) | C-KP | 本文はTier1(5role限定)でPASS。Key Phrase/Whisper票はTier1非適用(承認済み仕様: CURRENT_SPEC.md:2159)のため不合格 -> KPへの適用拡張=新規救済範囲 |
| T04 | asr_itn | `okay then` / `OK then` | NG | NG | NG | 同値(all_diff_spans_phoneme_e) | C | OK<->okay |
| T05 | asr_itn | `dr. Lee said` / `Dr Lee said` | PASS(NORMALIZED_MATCH) | PASS | PASS | 同値(surface_equal_after_norm) | A | 既存で対応済み(全経路PASS) |
| T06 | asr_itn | `nine to five` / `9 to 5` | PASS(NUMERIC_EQUIVALENCE_MATCH) | PASS | PASS | 同値(all_diff_spans_phoneme_e) | A | 既存で対応済み(全経路PASS) |
| T07 | asr_itn | `one on one` / `1 on 1` | PASS(NUMERIC_EQUIVALENCE_MATCH) | NG | NG | 同値(all_diff_spans_phoneme_e) | C-KP | 本文はTier1(5role限定)でPASS。Key Phrase/Whisper票はTier1非適用(承認済み仕様: CURRENT_SPEC.md:2159)のため不合格 -> KPへの適用拡張=新規救済範囲 |
| T08 | asr_itn | `number one` / `No. 1` | PASS(NUMERIC_EQUIVALENCE_MATCH) | NG | NG | 非同値(phoneme_differs) | E | `No. 1`(番号略語)は否定語noと衝突するためer109は未対応。本文はTier1でPASS(KPは非適用) |
| T09 | asr_itn | `the one percent` / `the 1%` | PASS(NUMERIC_EQUIVALENCE_MATCH) | NG | NG | 同値(all_diff_spans_phoneme_e) | C-KP | 本文はTier1(5role限定)でPASS。Key Phrase/Whisper票はTier1非適用(承認済み仕様: CURRENT_SPEC.md:2159)のため不合格 -> KPへの適用拡張=新規救済範囲 |
| T10 | asr_itn | `one by one` / `1 by 1` | PASS(NUMERIC_EQUIVALENCE_MATCH) | NG | NG | 同値(all_diff_spans_phoneme_e) | C-KP | 本文はTier1(5role限定)でPASS。Key Phrase/Whisper票はTier1非適用(承認済み仕様: CURRENT_SPEC.md:2159)のため不合格 -> KPへの適用拡張=新規救済範囲 |


## カタログ外(代表を実測せず、設計上の扱いだけを記す)
| 型 | 例 | 扱い |
|---|---|---|
| 範囲・ハイフン付き数 | `10-20 minutes`/`ten to twenty` | er109は解析不能(number_unparsed)=同値にしない。`to`/`through`の読みが一意でないため新規救済しない |
| 長い数字列・電話番号・桁0始まり | `555-0123` | 解析不能(long_digit_string_ambiguous/number_leading_zero)=同値にしない |
| 日付(スラッシュ・月名略語) | `3/4/2026`/`Jan. 5` | 未対応。月名略語は通常語と衝突(may/mar/sat)。C候補(要判断)かE |
| ローマ数字 | `Henry VIII` | 既存Tier1(5 role)。er109は対象外 |
| 単位記号 | `20°C`/`m²` | `km`/`lb(s)`/`oz`/`mph`は表にあるが`°C`等は未対応(E) |
| 省略・口語 | `gonna`/`wanna`/`'cause`/`y'all`/`kinda` | 発音が異なる(CMU)=D。`want to`<->`wanna`は2026-09-07ユーザー不採用 |
| filler除去・言い直し | `um, I think` | 脱落=発音一致ではない。既存disfluency QAの管轄でD |
| 国名/代名詞 `US`/`us` | `the US` / `the us` | CMUのus変種(Y UW EH S)と既存の大小無視で既存が同一視(承認済み挙動、Opus注意事項) |
| CMU音素表記の差 | `tyre`/`tire`(R vs ER) | E: 辞書限界。同値にしない(残存偽NG)。補完辞書は別判断 |
| 固有名詞の表記ゆれ | `Kristie`/`Christie` | 既存G9(代表発音のみ・entity_like)を尊重。er109は固有名詞(canonical側大文字始まり)を代表発音のみで比較 |
| 4桁を年と読むか数と読むか | `2024` | 年読み(twenty twenty four)と基数読み(two thousand ...)の両候補のどれか一致で同値 |
