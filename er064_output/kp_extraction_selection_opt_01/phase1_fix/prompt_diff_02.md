# prompt_diff_02: 改善Prompt短縮版(C2のPromptそのものを差し替え。別条件にしない)

Trial専用。Production Prompt/schema/builder無変更。API呼出なし(JPY0)。token=tiktoken `o200k_base`近似(gpt-6-lunaの実tokenizerではない、相対比較用)。
全文(After): `prompt_after_02.txt` / 見本(Coffee v5候補入り完成形): `specimen_after_std_v5_02.txt`・`specimen_after_adv_v5_02.txt` / token: `token_measure_02.json` / 生成: `er064_kp_opt_01_prompt_build_02.py`。Before全文は `../phase1_b/prompt_before_01.txt`(現行)、01版After全文は `../phase1_b/prompt_after_01.txt`。

## 1. token(目標: 現行と同等以下 = Std<=2,755 / Adv<=3,127)

| | 現行(Before) | 01版After | **02版After** | 02 vs 現行 | 02 vs 01版 |
|---|---|---|---|---|---|
| Std user全文(v5候補入り) | 2,755 | 3,043 | **2,587** | **-168 (-6.1%)** | -456 |
| Adv user全文(v5候補入り) | 3,127 | 3,431 | **2,977** | **-150 (-4.8%)** | -454 |
| Prompt文のみ(候補を除く、Std) | 1,402 | 1,689 | 1,233 | -169 | -456 |
| Prompt文のみ(Adv) | 1,402 | 1,705 | 1,252 | -150 | -453 |
| output schema | 1,113 | 1,185 | **1,113**(Production同一) | 0 | -72 |

目標達成(現行以下)。なお実Phase 2のC2は `alt_precision_guarded` の候補行(現行比 平均+約51token)が入るため、実際の入力は上記から+約51token(それでも現行以下)。「現行を超える部分」は無いため、削れない部分の列挙は不要。

## 2. 02版After 段落別token(Std)
冒頭タスク文58 / 【判断の基準】87 / 同格・透明表現70 / **定着度+既知基本連語(統合)131** / 【学ぶ単位】204 / 【役割】190 / 【日本語グロス】222 / 出力のルール 7+112+49+44+58。Level差(Std 31 / Adv 49 token)。

## 3. 01版(Phase 1-B After)からの短縮箇所(委任_02 M3)
| 指示 | 変更 | 効果(概算・段落別の実測ではない) |
|---|---|---|
| (a) 定着度タイブレークと既知基本連語の優先度低下 | 2段落(約190tok)を1段落131tokへ統合。「同程度の候補どうしでは、定着した自然な表現(慣用句・自然なコロケーション・句動詞・本文で基本義と異なる意味の表現)を、構成語どおりの基本連語やこの記事だけの言い回しより優先」+「区分名(idiom等)やevidenceラベルだけでは選ばず、CEFR等級だけでも判断しない」+Level差1文 | 約-60 |
| (b) 【出力のルール】区分3行 | 区分3行を1文に統合(「5件は必ず候補一覧から選び、新表現を作らない。重要語区分から少なくとも1個、残りはphrase区分を優先、word区分は不足時のみ」)。末尾に **「この区分の優先は、質が同程度のときの補充規則です」**(同格 vs 区分優先の残存矛盾を1文で位置づけ) | 約-60 |
| (c) 【役割】topic段落 | 半分程度に縮約。「判断基準は『これを知らないと…か、知っていると…か』」の重複2文と、人名・企業名…の列挙を1文へ | 約-90 |
| (d) グロス規則 | 01版の統合形(1段落)を維持。制約の取りこぼしなし(testで漢数字・括弧・「…」を確認)。**ja_gloss機械検査(括弧・算用数字・「…」・数値穴埋め形)をPhase 2に入れ、グロス統合の副作用を確認** | 維持 |
| (e) 例示 | `take care`例示(take careよりtake care of)を削除。例は`rateよりinterest rate`のみ(一般語、Coffee語句なし) | 約-12 |
| schema | `established_or_article_specific`欄を削除(Fable判断)。schemaはProduction同一(`schema_identical_to_production=true`) | -72(schema) |
| (f) Level文 | 各1文のみ(Std:日常で頻出する基本的な句は既知。Adv:基本義と異なる意味の句動詞/文脈で意味が変わるコロケーションは同列に評価) | 句点1つ(test) |
| 学ぶ単位 | 注釈の説明をrows側ラベルに統一(M1): `` `contains: Cn` はCnを含む、`contained_in: Cn` はCnの一部 `` | 日本語ラベル「含む:Cn」を廃止 |

**変更していないもの**: 【判断の基準】の6指標順序行(逐語、test T2で1回出現を確認)、developer message、候補セクション形式、backup_item契約、Rule7/canonicalization/gate、retry。6指標の順序行は変えていないため、Opus再レビュー対象の変更はない。

## 4. M1: 注釈ラベルの統一(選択と理由)
- 選択: **Prompt側をrows側(英語ラベル)に合わせた**。rows側は既存の候補行の書式(`id:`/`candidate:`/`type:`/`occ:`/`evidence:`/`sentence:`)と同じ英語key形式で、行の形式を変えると、現行Prompt(C0/C1)と同じ書式の行に日本語だけが混ざる。ラベル文字列は `er064_kp_opt_01_upstream_core.py` の定数(`LABEL_CONTAINS="contains:"`、`LABEL_CONTAINED="contained_in:"`、`LABEL_FRAGMENT="fragment_risk"`)に一本化し、rows生成とPromptの両方がこの定数を参照する。
- test: Promptが `contains: Cn`/`contained_in: Cn` を参照していること、旧「含む:」が残っていないこと、10記事x4構成のrowsに現れる注釈ラベルが全てPromptで説明済みであること(Phase 2の6記事ではfragment_riskはrowsに出現しない=0件、test)。
- **C1(現行Prompt+改善shortlist)の注意**: 現行Promptは注釈の意味を一切説明しない。そのためC1では、Coffee等の一部の行末に `| contains: Cn` / `| contained_in: Cn` の注釈が説明なしで渡る(Coffee Std/Adv、smallbag、semiで出現。meta/hormuzは0件)。C1で観測される差には「shortlistの差」に加えて「説明のない注釈が行に付いたことの影響」が含まれる(Phase 2計画書に明記)。

## 5. 残存する矛盾・未対処(報告)
- 「同格 vs 区分優先」: 区分優先を「質が同程度のときの補充規則」と1文で位置づけた(Prompt側で対処済み)。
- 「5語上限 vs 完結したまとまり優先」(`putting the two figures in the ring`は6語): **抽出側(方式2)の問題**であり、Prompt側では対処しない(計画書に注記)。
- OPEN-J(Std「B1」固定): 01版と同じくTrial専用ではStdの「B1」を除去している。C2の効果帰属には含まれる。
