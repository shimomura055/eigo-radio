# RESCUE_TABLE_01: 除外11件(+Human NG 3件)の救済表

管理ID: KP-GATE-EXCLUSION-RESCUE-DESIGN-02 委任_01 / 2026-10-26。根拠データ=`rescue_eval_07.json`(各事例の`rows`/`decision`/`final_check`)・`final_table_01.json`・`judge_06〜08.json`。
列はユーザー指定の6列+「なぜ救済できる/できないか」。**救済率だけを結論にしない**(個別の理由が結論)。検証結果の「Gate再検証」=既存validator(`validate_canonicalization_item`、allow_inflection_normalization=True・original_span・role_ok_poss=最終Gateと同一引数)+CMU+選定gate(本文連続一致・1〜5語・有限助動詞・数値)+既存候補との包含/重複。「LLM評価」=gpt-6-luna×3回(06〜08、同一プロンプト)の採用可/回数。区分の定義は委任文のとおり。

## 1. 11件

| # | 元候補 | 除外原因 | 修正候補 | 検証結果 | 救済可否 | 規則変更の要否 |
|---|---|---|---|---|---|---|
| 1 | X a2 `too soon to wave a flag` | 6語(上限5語)。Prompt 2-Vの規則違反=正当な除外 | **`too soon`**(元句の連続部分列。演算子`too`と被演算子`soon`を保持)。代替案: `wave a flag`(意味changed)・`flag`(reject)・`too soon to do`(区分3推奨) | selection gate PASS・CMU PASS・既存5候補と重複なし。LLM評価: adopt系3/3(strict2)、意味narrowed。比較: `wave a flag`=意味changed(8回中7回)、`too soon to do`=reject(8回中7回) | **救済可(狭めた2語)**。学習価値の最終判断はHR | 受理面は不変だが、**選定段の短縮後処理の新設=区分2**(救済フロー本体の採否)。ユーザー例`too soon to do`は区分3推奨(後述) |
| 2 | X a2 `studied separately` | Rule7: `_guard_ok`が直後の副詞`separately`を許可しない(承認文に無い内部条件) | **`study separately`**(LLMの提案そのまま) | 現行Gate=不通過 → guard(副詞後続)是正後 validator PASS・CMU PASS・選定gate PASS。三重検査(LLM提案語・CMU・前方活用一致`studied∈forms(study)`)。LLM評価3/3 same/good。実データ315種で誤受理0 | **救済可(通常フロー、救済フロー不要)** | **要・区分1**: guardに副詞後続を追加(最小flag=`adverb`)。境界判定をFableへ(下記) |
| 3 | X b1b `had our eye on` | 有限助動詞(`had`)。語形リストが用法を見ない | `had our eye on`(表層)/**`have our eye on`**(原形。P-04(3)の`had→have`) | 役割判定後 validator PASS・CMU PASS・選定gate PASS・重複なし。LLM評価3/3 same/good | **救済可(通常フロー)** | **要・区分1**: 有限助動詞を語形→役割判定へ(fulltext経路のみ) |
| 4 | Z r3 `rose above` | LLMが許可素材外の語を付加(`rise above the other voices`、source_spanは`rose above`のみ) | **`rise above`**(LLM提案の窓内部分。`the other voices`を捨てる) | validator PASS(規則是正なし)・CMU PASS・選定gate PASS・重複なし。LLM評価adopt系3/3。Wiktionary句動詞見出しに一致 | **救済可(救済フロー M1再導出)**。gloss再整合必須 | 規則は不変。**救済フロー新設=区分2** |
| 5 | Z r3 `held out` | 同上(`hold out one's hands`、`his hands`は窓外) | **`hold out`** | 同上。Wiktionary見出し`hold out`(idioms/phrasal verbs) | **救済可(救済フロー M1)**。`one's hands`を失うためgloss再整合必須 | **区分2**(救済フロー) |
| 6 | Z r4 `rang through` | `rang`が過去形専用表に無い(閉表の網羅漏れ) | **`ring through`**(LLM提案そのまま) | 現行=不通過 → 表補完後 PASS(最小flag=`past`)。LLM評価3/3 same/good。表補完前の代替=表層`rang through`(revert) | **救済可(通常フロー)** | **要・区分1**: 閉表の補完(51語+曖昧20語+分詞35語、`bound`除外) |
| 7 | Y a2 `it can’t be helped` | 有限助動詞(`can`)。主語を持つ完全文でもある | **`can’t be helped`**(主語`it`を除く本文の連続部分列。Wiktionary慣用句`it can't be helped`の核) | 例外適用後 validator PASS・CMU PASS・選定gate PASS。LLM評価3/3 same/good。完全文のままでは例外の対象外 | **救済可** | **区分2**: 慣用句(辞書見出しの核)に限る法助動詞例外+選定段の主語除去(新規) |
| 8 | Y a2 `redelivery fee` | CMU未登録語`redelivery` | なし(`re`+`delivery`と分解は可能だが合格にしない) | 分解: 両部分CMU登録、予測音素`R EY1`+`D IH0 L IH1 V ER0 IY0`。ただし**推測による代替合格**に当たる | **救済しない(推奨)** | 救済するにはCMU規則の受理面拡大=**区分2・非推奨**(下記) |
| 9 | Y b1b `can’t be helped` | 有限助動詞(`can`) | `can’t be helped`(無変更) | #7と同じ(例外適用後PASS)。LLM評価3/3 | **救済可** | **区分2**(#7と同じ慣用句例外) |
| 10 | Y b1b `have a say` | 有限助動詞(`have`)。語彙動詞 | `have a say`(無変更) | 役割判定後 PASS。Wiktionary見出し`have a say`。LLM評価3/3 | **救済可(通常フロー)** | **要・区分1**(#3と同じ) |
| 11 | Y b1b `catch their interest` | 本文に連続一致しない(原形で返した。本文は`catches their interest`) | 選定を**`catches their interest`**(本文の表層)へ戻す → 続くcanonicalizationで`catch their interest` | 再アンカー窓が一意。選定gate PASS・原形化validator PASS(`catches→catch`は承認済み)・CMU PASS。LLM評価3/3 same/good | **救済可(救済フロー D1)** | 規則は不変。**救済フロー新設=区分2** |

### 参考: Human NG 3件(11件に含めない)
| 元候補 | 除外原因 | 修正候補 | 救済可否 | 規則変更 |
|---|---|---|---|---|
| X `put in place` / X `off the hook` / Z `sentenced him to death` | ユーザーのHuman Review NG | なし | **救済しない=区分3**(ユーザーの明示判断。救済経路でも`match_ng`が迂回不可) | 不要 |

## 2. 11件の最終分類(根拠つき)

| 区分 | 件数 | 内訳 | 比率(11件) |
|---|---|---|---|
| **区分1**(承認済み規則への準拠修正。通常フローを通す) | 4 | #2 `studied separately`・#3 `had our eye on`・#6 `rang through`・#10 `have a say` | 36% |
| **区分2・採否推奨**(救済フロー/受理面の拡大。ユーザー判断) | 6 | #1 短縮・#4 `rose above`・#5 `held out`・#11 `catch their interest`(以上=救済フロー本体)、#7/#9 `can’t be helped`(慣用句例外) | 55% |
| **区分2・非推奨**(救済すると承認済み規則の趣旨に反する) | 1 | #8 `redelivery fee` | 9% |
| **区分3**(救済すべきでない) | 0 | (11件内)。付随: Human NG 3件・A2`too soon to do` | 0% |

- 前回の分類(4件救済可・3件新規則・4件不可)から変わった点: 前回「不可」とした`catch their interest`(本文に無い)は**再アンカーで救える**と判明、`it can’t be helped`/`can’t be helped`(法助動詞=不可)は**辞書見出しの核だけ例外にする設計で救える**、`too soon to wave a flag`(新規則・意味反転リスク)は**演算子保持の短縮で救える**。`rose above`/`held out`は前回「再導出でrevert」だったが、LLM提案の窓内部分(`rise above`/`hold out`)を採る形がDEVで実証できた(前回は机上)。
- 期待救済率(救済フロー採用の場合): 11件のうち10件(91%)に既存Gate通過の救済形がある。区分1だけ(規則是正)なら4件(36%)。比較用に、HR導入前の一意句29(現行で既に通る4件を除く25)では 区分1=5(20%)・区分2=12(48%)・区分3=8(32%) → 区分1+2で17/25(68%)。

## 3. 区分2の個別判断材料(要約。詳細はDESIGN_01 §5)

| 案 | 修正例 | メリット | 品質リスク | 代替 | QCD影響 | 推奨 |
|---|---|---|---|---|---|---|
| 救済フロー本体(M1窓内再導出・再アンカー・短縮) | `rose above→rise above`・`catches their interest`・`too soon` | 候補が減らない(11件のうち4件)。本文対応・既存Gateは不変 | 候補が原形でない/狭まる。gloss・QA再判定が必要 | 現行(除外のまま)。外側retryで別候補 | gloss再整合約0.53〜0.56円/件。HR導入後12 level-runで該当5件=約0.23円/level-run(70円の<1%)。速度影響はgloss 1 callのみ | **採用推奨**(AUTO不可・HR経路限定・既定OFF) |
| 慣用句の法助動詞例外(辞書見出しの核のみ) | `can’t be helped` | 日本語「仕方がない」に対応する高価値表現を残せる | 例外の根拠が外部辞書。完全文は通さない | 現行どおり除外 | API 0。辞書(Wiktionary見出し約1.7万件)をvendoring要 | **採用可(推奨・条件付き)**。辞書データのライセンス確認が条件 |
| 辞書裏付けguard(V+名詞の原形化) | `lost touch→lose touch` | 導入前29種中1種(V+名詞) | 辞書依存。POS誤判定の余地 | 表層形のまま(revert)で候補に残す | API 0 | **保留推奨**(revertで足りる) |
| CMU未登録語の分解合格 | `redelivery fee` | 1/12 level-run | TTS発音不良(`minaudière`の再来)。承認済み趣旨に反する | 非採用。または実TTS音声のASR一致を要件化 | TTS+ASRの追加費用が候補単位で発生 | **非推奨** |
| スロット一般化 | `too soon to do` | 枠(`too soon to + V`)を残せる | 比喩の消失・不自然・本文に無い語。独立評価でreject | A1(`too soon`) | - | **非推奨(区分3推奨)** |

## 4. 補足: HR導入前の一意句29(同種の除外)
自動生成表=`final_table_01_auto.md`。パターン別集計と代表例はCASE_ANALYSIS_01 §12。
