# CASE_ANALYSIS_01: Gate除外11件の一件ずつ再調査(原因究明)

管理ID: KP-GATE-EXCLUSION-RESCUE-DESIGN-02 委任_01 / 2026-10-26 / DEV(Production非変更)・API 0(原因究明部分)。
前回(KP-GATE-EXCLUSION-RESCUE-DESIGN-01)の「11件中4件救済可能・残り7件は不可」という分類は**結論として固定しない**。11件をすべて、(1)元の本文 (2)AIの提案 (3)除外の直接原因 (4)原因となる規則・コード条件 (5)その条件のユーザー承認履歴 (6)実害か過剰除外か (7)修正可能性、の順に再調査した。証跡=`rescue_eval_07.json`(各事例の`rows`/`decision`/`final_check`)、`final_table_01.json`。Human NG 3件(`put in place`/`off the hook`/`sentenced him to death`)は§4。

## 0. 先に分かったこと(横断所見)

1. **除外11件のうち、承認済み規則に照らして「規則の意図に反する過剰除外・実装の不整合」と言えるのは4件**(`studied separately`・`had our eye on`・`have a say`・`rang through`)。いずれも、承認文(P-04原文・DECISION_LOG・OPEN-152)に無い内部条件、承認文どおりに動かない閉表、語形リストの機械適用が原因。
2. **「有限助動詞」の語形リストは、承認済みP-04(3)と自己矛盾**している。P-04(3)は`has/had→have`を不規則表に入れる(`OPUS_REVIEW_COND_A_01.md:118-123`、`er105:590 _FUNCTION_VERB_FORMS`)が、変換後の`have …`は同じ語形リスト(`er003_key_words_min_unit.py:260`、`er003_key_words_canonicalization.py:216,439,627`)で必ず不通過=承認済み変換が一度も成立しない(dead path)。X事前世代の`have a big moment`(key)も同じ経路で除外されている。
3. 残り7件は「規則違反だから不可」ではない。**7件すべてに、既存validatorを同一引数で通る救済形が実際に存在した**(§各件、`final_check`)。ただし受理面の変更または新しい後処理工程を要するため、ユーザー判断(区分2)になる。`redelivery fee`だけは救済形が存在しても承認済みCMU規則の趣旨(未登録語を推測で合格させない)に反するので、非推奨(§9)。
4. 付随発見(不具合候補、本委任では修正せず記録のみ): 有限助動詞判定の語トークン化(`_WORD_TOKEN_RE=[A-Za-z][A-Za-z'-]*`)は曲線アポストロフィ`’`で語を分割する。`can’t`は`can`+`t`として助動詞判定されるが、ASCIIの`can't`は1語で判定表に無く**通過する**(`isn't`/`won't`も同様)。同じ句が綴り記号の違いだけで通過/不通過になる。→ DESIGN_01 §8 新規OPEN候補(本委任では修正しない=Gateを厳しくする方向のため)。

## 1. X(AI島 a2) `too soon to wave a flag`

| 項目 | 内容 |
|---|---|
| 元の本文 | "Even so, it is too soon to wave a flag and say, “Play and get smarter—proof complete!”" |
| AIの提案 | call2(Prompt 2-V)が6語の`too soon to wave a flag`を返した |
| 直接原因 | 語数が1〜5語でない(実際: 6語)。`er105_kp_fulltext_selector_01.py:225-` `validate_and_resolve`(語数検査、`KP_WORDS_MAX`) |
| 規則・コード条件 | 1〜5語 = `CURRENT_SPEC.md:1962`(`DECIDED`、ER-003-KP-02-R1・2026-08-08)、最小学習単位の強制=`er003_key_words_min_unit.py:3-9`(ER-003-P2G・2026-07-21) |
| 承認履歴 | 承認済み(`DECIDED`)。1〜5語は変更していない |
| 実害か過剰除外か | **規則どおりの正当な除外**(提案が6語)。ただし「捨てるしかない」わけではない。元句の連続部分列で本文対応を保ったまま5語以内にできる(本文に無い語を使わない) |
| 修正可能性 | 可。決定論で連続部分列を列挙→否定・程度語の作用域を壊す案を禁止→既存selection gate+CMU→LLM評価で選ぶ。結果(LLM評価を8回実施。judge_01〜08): `too soon`は評価できた7回すべてadopt系で意味は「narrowed」(狭まるが壊れない)。`wave a flag`は8回中7回「意味changed」(『時期尚早』が消え字義の旗振りに読める)、`too soon to wave`は目的語欠落で「changed」。ユーザー例の`too soon to do`(本文に無い`do`)は8回中7回reject(不自然/意味変化)→PATTERN_DESIGN_01 A2 |

## 2. X(AI島 a2) `studied separately`

| 項目 | 内容 |
|---|---|
| 元の本文 | "These two results need to be studied separately." |
| AIの提案 | canonicalizationで`study separately`(過去分詞→原形。正しい) |
| 直接原因 | Rule7拒否: 「key_phrase('study separately')がdisplay_phraseと一致せず…」。原形化の許可窓に入る前に`_token_pair_ok`が`_guard_ok`で偽 |
| 規則・コード条件 | `er105_kp_fulltext_selector_01.py:662 _guard_ok`: 変換対象の**直後**が`_GUARD_DET`(:614)か`_GUARD_PARTICLE`(:618)でなければ原形化しない。`separately`は副詞で両表に無い |
| 承認履歴 | **承認文なし=実装判断**。P-04原文(`OPUS_REVIEW_COND_A_01.md:118-123`)は「動詞の活用形の変換は、先頭トークンかtoの直後に限る」のみ。`CURRENT_SPEC.md:1997`も同じ。guardは配線commit `84d9a6412`(2026-10-22)でコメント`er105:570-575`(V+名詞は基本形化しない)と共に入った。OPEN-530(文書是正)で記録済み |
| 実害か過剰除外か | **過剰除外**。guardの目的(P-04が防ぎたい`heated debate→heat debate`型=形容詞化分詞+名詞の誤変換)は、直後が副詞(`studied separately`)の場合には当たらない。副詞が続く分詞は動詞用法 |
| 修正可能性 | 可(区分1)。guardに「副詞後続」を、三重検査(LLM提案語・CMU実在・前方活用生成一致)つきで追加。`study separately`が通常フローで通る。実データ311種で誤受理0・既受理の取りこぼし0 |

## 3. X(part2_hr_evidence R2 b1b) `had our eye on`

| 項目 | 内容 |
|---|---|
| 元の本文 | "The case had started before the suspect we had our eye on even appeared." |
| AIの提案 | call2が`had our eye on`を返した(語彙動詞`have`の過去形+所有格) |
| 直接原因 | 「有限助動詞を含む(既存canonicalization Validatorが拒否する形)」。`er105:213 _legacy_form_reasons`→`kc._contains_finite_auxiliary` |
| 規則・コード条件 | `_FINITE_AUX_WORDS`={is,are,was,were,has,have,had,will,would,can,could,should,may,might,must}(`er003_key_words_min_unit.py:260-261`、`kc:216`で再利用、判定=`kc:439-441`、validator内=`kc:627`)。語形の一致のみで、用法(助動詞か語彙動詞か)を見ない |
| 承認履歴 | 元の意図=ER-003-P2G(2026-07-21、commit `1bb4c156a`)「完全文・節・時制付き動詞句を決定的validatorで拒否」(`er003_key_words_min_unit.py:3-9`)。2026-09-14に語彙動詞haveの誤検知として既に発覚(`DECISION_LOG.md:7408`、`OPEN-152`、`OPEN_ITEMS.md:328`、`USER_DECISION_REQUIRED`/Non-blocking、Validator未修正)。**P-04(3)は`has/had→have`を承認**(`OPUS_REVIEW_COND_A_01.md:122-123`)=変換後の`have …`が同じリストで落ちるため承認済み変換は成立しない |
| 実害か過剰除外か | **過剰除外**(誤判定)。`had our eye on`は完全文でも節でもない語彙動詞句(定型表現、Wiktionary慣用句`have an eye on`系)。全文選定の表層形は`took`/`pushed`等の時制付き動詞を既に許している=「時制付き」だけでは排除理由にならない |
| 修正可能性 | 可(区分1)。助動詞判定を語形→役割判定へ(§PATTERN_DESIGN C)。`have our eye on`(原形)も通る |

## 4. Human NG 3件(`put in place`・`off the hook`・`sentenced him to death`)

| 項目 | 内容 |
|---|---|
| 直接原因 | ユーザーがHuman Reviewで明示NG(evidence runの共有registry検証) |
| 規則・承認履歴 | NG復活禁止(`docs/pm/delegation_log/…KP-HUMAN-REVIEW…_USER.md:97`相当、`er119_kp_candidates_01.py:288-293`のmatch_ngはselection_phraseとused_formの両方を照合) |
| 判定 | **区分3(救済しない)**。ユーザーの明示判断を覆す救済は設計しない |

## 5. Z(melos run_p2_evidence_r3 b1b) `rose above`

| 項目 | 内容 |
|---|---|
| 元の本文 | "At the wedding, his sister's laughter rose above the other voices." |
| AIの提案 | canonicalizationで`rise above the other voices`(4語。displayは`rose above`の2語) |
| 直接原因 | Rule7拒否: key(4語)が`display_phrase`と不一致で、`source_span('rose above')`内の連続部分文字列でもない。LLMが**許可された素材(source_span)の外の語**`the other voices`を足した |
| 規則・コード条件 | `er003_key_words_canonicalization.py:576-620`(`validate_canonicalization_item`のRule7)。原形化はdisplay内の連続窓の1対1置換のみ(`er105:812 find_inflection_window`)。canonicalization template規則2「source_spanから必要最小限の語だけ復元」(source_spanが`rose above`だけなので復元元が無い) |
| 承認履歴 | Rule7=ER-003-KP-02(2026-08-08)、原形化例外=P-02(2)(3)/KPFT 委任_02(2026-10-22) |
| 実害か過剰除外か | 提案の**一部が許可範囲外(実害)で、残りは正しい**。`rise`への原形化は正しく、`rose`は過去形専用表にある(`er105:577`)ので、窓内の`rise above`なら現行Gateを通る |
| 修正可能性 | 可。LLMが付加した窓外の語(`the other voices`)だけを捨て、窓内の語は**LLMが提案した`rise above`をそのまま採る**(新語形を作らない=前回M1)。Wiktionary句動詞見出し(`rise above`)に存在 |

## 6. Z(melos run_p2_evidence_r3 b1b) `held out`

| 項目 | 内容 |
|---|---|
| 元の本文 | "…he could speak, his friend held out his hands for the chains." |
| AIの提案 | `hold out one's hands`(display=`held out`の2語に対しkey 4語) |
| 直接原因 | #5と同型(範囲拡張。`his hands`は`source_span('held out')`の外) |
| 規則・承認 | #5と同じ。`held`は曖昧不規則表(`er105:584`)にあり、直後`out`が不変化詞(`_GUARD_PARTICLE`)なので窓内の`hold out`は通る |
| 実害か過剰除外か | #5と同じ(一部が範囲外。残りは正しい) |
| 修正可能性 | 可。窓内の`hold out`を採る(Wiktionary見出し`hold out`あり)。LLMが意図した`one's hands`は失う=glossは再整合が必須(`hold out one's hands`の「両手を差し出す」が`hold out`に残らないように) |

## 7. Z(melos run_p2_evidence_r4 b1b) `rang through`

| 項目 | 内容 |
|---|---|
| 元の本文 | "Melos's voice rang through the hall." |
| AIの提案 | `ring through`(正しい原形化) |
| 直接原因 | Rule7拒否。`rang`が過去形専用表に無く、`_verb_base_candidates('rang')`(規則活用の接尾辞規則)も空 |
| 規則・コード条件 | `er105:577-583 _PAST_ONLY_IRREGULAR`(29語) |
| 承認履歴 | P-04原文「過去形専用の不規則形(gave/took等)は曖昧さが無いため直後条件を課さない」=不規則形一般を承認。表の語は例示的で閉じていない |
| 実害か過剰除外か | **過剰除外(閉表の網羅漏れ)**。同種の漏れは`irregular_gap_01.json`で51語(過去形専用)+20語(曖昧過去形)+35語(過去分詞)。`ring through`はWiktionary句動詞見出しにも存在 |
| 修正可能性 | 可(区分1)。表の補完。曖昧語は`bound`のみ除外(OPEN-476=DEFERRED、`er105:834-835`で`bound to→bind to`は拒否が仕様)。実データ311種で新規受理は`rang through`・`thrown into it`・`studied separately`のみ(誤受理0) |

## 8. Y(redelivery_fee run_01 a2/b1b) `it can’t be helped` / `can’t be helped`

| 項目 | 内容 |
|---|---|
| 元の本文 | "I guess it can't be helped."(a2)/"…and I guess it can't be helped."(b1b) |
| AIの提案 | a2は`it can’t be helped`(完全文)、b1bは`can’t be helped`(主語なし) |
| 直接原因 | 有限助動詞を含む(`can`)。曲線アポストロフィで`can`+`t`に分割されるため(§0の付随発見4) |
| 規則・コード条件 | #3と同じ語形リスト(`can`) |
| 承認履歴 | #3と同じ。意図は「完全文・節・時制付き動詞句」の排除 |
| 実害か過剰除外か | 判断が分かれる。`it can’t be helped`は主語を持つ**完全文**で原意図に当たる。`can’t be helped`は節の断片だが、日本語の「仕方がない」に対応する**固定表現**でWiktionary慣用句見出し(`it can't be helped`)に存在。法助動詞を外すと意味が壊れる(`be helped`は意味喪失、前回確認済み) |
| 修正可能性 | 可(区分2)。**辞書見出し(Wiktionary idioms)の核に一致する句だけ**を法助動詞例外にする。完全文は例外にせず、主語`it`を除いた連続部分列(`can’t be helped`、本文の連続部分列)だけを通す(原意図を維持) |

## 9. Y(redelivery_fee run_01 a2) `redelivery fee`

| 項目 | 内容 |
|---|---|
| 元の本文 | "A redelivery fee is extra money paid by the person getting the package." |
| 直接原因 | CMU発音辞書に`redelivery`が無い(`er108_kp_cmu_lexicon_gate_01.py` R2) |
| 規則・承認履歴 | ユーザー正式指示(2026-10-22、`2026-10-22_KP-QUALITY-IMPROVEMENT-2ITEMS-PRODUCTION-01_USER.md:56-63`)「CMU辞書に登録されていない語を、LLMの推測や外部辞書の発音で代替して合格扱いしない」。`CURRENT_SPEC.md:2001`。契機=`minaudière`(TTS発音不良) |
| 実害か過剰除外か | 規則の趣旨(未登録語は発音を保証できない)に**適合した除外**。ただし`redelivery`=`re`+`delivery`(両方CMU登録、予測音素`R EY1`+`D IH0 L IH1 V ER0 IY0`)と分解できるため、「構造的に救える」余地はある |
| 修正可能性 | 規則の趣旨に反するため**救済しない(区分2・非推奨)**。分解可能という理由での合格は「推測による代替合格」に当たる。採用するなら、実TTS音声のASR一致(実音声での発音確認)を要件にする案(§DESIGN代替案)。頻度が低く(HR導入後12 level-runで1件)、他候補で補えるので非採用を推奨 |

## 10. Y(sns_age_limit run_01 b1b) `have a say`

| 項目 | 内容 |
|---|---|
| 元の本文 | "I want to have a say in what I can use and how I use it." |
| 直接原因 | #3と同じ(`have`が語形リストに該当) |
| 判定 | **過剰除外(語彙動詞have)**。Wiktionary慣用句見出し`have a say`に存在。#3と同じく区分1で通常フローを通る |

## 11. Y(sns_age_limit run_01 b1b) `catch their interest`

| 項目 | 内容 |
|---|---|
| 元の本文 | "I don’t think it’s okay to let them use whatever catches their interest." |
| AIの提案 | call2が原形の`catch their interest`を選定結果として返した(本文は`catches their interest`) |
| 直接原因 | 「本文に連続一致しない(変更・言い換え・創作)」(`er105:225-` `locate_phrase`の逐語一致) |
| 規則・承認履歴 | ユーザー指示(2026-10-22)「本文中に存在する表現を選ぶ条件を維持」(`…_USER.md:61`)、Prompt 2/2-Vの逐語要求 |
| 実害か過剰除外か | 提案は**形式違反**(原形で返した)だが、意味・語は本文に1対1で対応する(`catches→catch`は承認済みの活用形→基本形)。本文に無い語・言い換えではない |
| 修正可能性 | 可。承認済みの原形化validator(`find_inflection_window`)を**逆向き**に使い、「その句が合法な正規化形になる本文窓」を探して表層形へ戻す。窓が一意(`catches their interest`)なら採用。新しい受理基準は作らない |

## 12. 同種の除外(他にないか)

HR導入前の一意句29(`inventory_01.json`)を同じ手順で処理した(`final_table_01.json`)。パターン別:

| パターン | 11件内 | 導入前29内 | 例 |
|---|---|---|---|
| 副詞/量化詞/補語/名詞の後続でguardが原形化を拒否 | 1 | 6 | `accepts no responsibility`・`leaving no mark`(量化詞)、`pulling free`・`eased open`・`growing louder and louder`(補語)、`lost touch`(V+名詞) |
| 閉表の網羅漏れ(過去形) | 1 | 2 | `struck a match`(`struck`)、`froze my blood`(`froze`) |
| 語彙動詞haveの誤判定 | 2 | 1 | `have a big moment`(key側、`had/having→have`の自己矛盾) |
| LLMの範囲拡張 | 2 | 0 | |
| 人称一般化とlemmaの同時要求がロールで食い違う | 0 | 4種(別に現行で既に通る4種) | `my ears began to ring`・`my blood went cold`・`nearly abandoned you` |
| 語数超過 | 1 | 1 | `offered his hands for the chains` |
| 本文不一致(原形で返した) | 1 | 2 | `lose my trust in you`→本文`lost my trust in you`(再アンカー可)、`in his place`(窓なし) |
| 法助動詞/進行形auxが句の核 | 2 | 6 | `could not bear`・`Could you have borne it`・`were mocking me` |
| CMU未登録 | 1 | 3 | `minaudière(s)`(アクセント付きの外来語=分解不能) |

全件の個別結果は`final_table_01_auto.md`/`RESCUE_TABLE_01.md`。
