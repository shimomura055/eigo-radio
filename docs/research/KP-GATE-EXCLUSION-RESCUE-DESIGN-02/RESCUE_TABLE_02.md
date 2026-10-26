# RESCUE_TABLE_02: 除外11件(+Human NG 3件)の救済表(Opus M1〜M4/R1〜R6反映後の再実証)

管理ID: KP-GATE-EXCLUSION-RESCUE-DESIGN-02 委任_02 / 2026-10-26。根拠データ=`rescue_eval_08.json`(各事例の`rows`/`decision`/`final_check`/`hr_flags`)・`final_table_02.json`・`judge_06〜08.json`(候補は委任_01と同一のため再利用)・`judge_headword_01.json`(M4)・`monotonicity_02.json`・`old_vs_new_02.json`・`have_probe_02.json`・`contraction_probe_02.json`・`idiom_closed_table_01.json`。
「Gate再検証」=既存validator(`validate_canonicalization_item`、allow_inflection_normalization=True・original_span・role_ok_poss=最終Gateと同一引数)+CMU+選定gate+既存候補との包含/重複。委任_01(RESCUE_TABLE_01)との差は末尾「差分」。

## 1. 11件

| # | 元候補 | 除外原因 | 修正候補 | 検証結果(Gate再検証/LLM評価) | 救済可否 | 規則変更の要否(区分) | HR旗 |
|---|---|---|---|---|---|---|---|
| 1 | X a2 `too soon to wave a flag` | 6語(上限5語) | **`too soon`**(連続部分列、演算子`too`+被演算子`soon`保持)。代替: `wave a flag`(意味changed)。A2 `too soon to do`は区分2・非推奨(§3) | validator/CMU/選定gate PASS・重複なし。LLM(文章枠)adopt系3/3・意味narrowed | **救済可(狭めた2語)** | 救済フロー新設=**区分2**(採用推奨) | 意味縮小の可能性・低価値の可能性(2語以下/程度語が中心)・元句と本文の文を併記 |
| 2 | X a2 `studied separately` | guardが副詞後続を拒否(承認文に無い内部条件) | **`study separately`**(LLM提案そのまま) | 区分1規則是正後 validator/CMU/選定gate PASS。M1の語幹検査: `separate`(CMU実在)・-ly名詞表に無い。LLM 3/3 same/good。実データ315種で誤受理0 | **救済可(通常フロー)** | **区分1**(副詞guard、M1の語幹検査+除外表が前提) | なし |
| 3 | X b1b `had our eye on` | 有限助動詞(`had`)。語彙動詞 | `have our eye on` | 役割判定(M2後)で`had`=lexical。validator/CMU/選定gate PASS・重複なし。LLM 3/3 | **救済可(通常フロー)** | **区分1**(語彙have、M2の敵対的test前提。fulltext経路限定) | なし |
| 4 | Z b1b `rose above` | LLMが許可素材外の語を付加(`rise above the other voices`) | **`rise above`**(窓内部分) | 規則是正なしで validator/CMU/選定gate PASS・重複なし。LLM 2/3 adopt(1回reject) | **救済可(M1窓内再導出)** | 救済フロー新設=**区分2**(採用推奨) | LLMが補った語(`the other voices`)を破棄・gloss再整合(本文の意味) |
| 5 | Z b1b `held out` | 同上(`hold out one's hands`) | **`hold out`** | 同上。LLM 3/3 | **救済可(M1窓内再導出)** | **区分2**(採用推奨) | 目的語(`one's hands`)破棄・**多義の可能性**(`hold out`単独の主な意味は「耐える」。gloss再整合は本文の「差し出す」) |
| 6 | Z b1b `rang through` | `rang`が過去形専用表に無い | **`ring through`** | 表補完(R3: `lay/wound/ground/bore`等を除外)後 validator/CMU/選定gate PASS。LLM 3/3 | **救済可(通常フロー)** | **区分1**(閉表補完) | なし |
| 7 | Y a2 `it can’t be helped` | 有限助動詞(`can`)。主語`it`を持つ完全文 | **`can’t be helped`**(主語を除く連続部分列。閉表収載) | 閉表例外後 validator/CMU/選定gate PASS。完全文のままは例外対象外。LLM 3/3 | **救済可** | **区分2**(2-B 慣用句閉表27件+選定段の主語除去。縮約形R5と同時提示) | 修正済み・QA未再判定 |
| 8 | Y a2 `redelivery fee` | CMU未登録語`redelivery` | なし(`re`+`delivery`と分解可能だが代替合格にしない) | 分解は両部分CMU登録だが、推測による代替合格に当たる | **救済しない(推奨)** | **区分2・非推奨**(CMU規則の受理面拡大。2026-10-22規則の趣旨に反する) | - |
| 9 | Y b1b `can’t be helped` | 有限助動詞(`can`) | `can’t be helped`(無変更) | #7と同じ | **救済可** | **区分2**(2-B) | 修正済み・QA未再判定 |
| 10 | Y b1b `have a say` | 有限助動詞(`have`)。語彙動詞 | `have a say`(無変更) | 役割判定(M2後)lexical。validator/CMU/選定gate PASS。LLM 3/3 | **救済可(通常フロー)** | **区分1** | なし |
| 11 | Y b1b `catch their interest` | 本文に連続一致しない(本文は`catches their interest`) | 選定=`catches their interest`→key=`catch their interest` | 再アンカー窓が一意。選定gate/原形化validator/CMU PASS。LLM 3/3 | **救済可(D1再アンカー)** | 救済フロー新設=**区分2**(採用推奨) | 修正済み・QA未再判定・gloss再整合 |

Human NG 3件(`put in place`/`off the hook`/`sentenced him to death`): **区分3**(ユーザーの明示判断。救済経路でも`match_ng`が迂回不可)。

## 2. 最終区分(11件)

| 区分 | 件数 | 内訳 | 比率 |
|---|---|---|---|
| **区分1**(承認済み規則への準拠修正。M1/M2/R3前提) | 4 | #2・#3・#6・#10 | 36% |
| **区分2・採否推奨**(救済フロー/慣用句例外) | 6 | #1・#4・#5・#11(救済フロー本体)、#7・#9(慣用句閉表) | 55% |
| **区分2・非推奨** | 1 | #8 `redelivery fee` | 9% |
| **区分3**(11件内) | 0 | (Human NG 3件は11件外) | 0% |
| 付随(11件外の選択肢) | - | A2 `too soon to do`=**区分2・非推奨・意見付き**(委任_01の区分3推奨から移動、M4) | - |

期待救済率(再計算): HR導入後11件=区分1が4(36%)、区分2推奨まで10件(91%)。導入前一意句25種(現行で通る4を除く)=区分1が5(20%)、区分1+2が17(68%)、区分3が8(32%)。委任_01と同値(M1〜M3は誤受理を塞ぐ是正で、実データの救済対象は減らさなかった)。

## 3. A2 `too soon to do`(M4。11件外)

| 枠組み | 結果 |
|---|---|
| 前回: 自然な英文として適切か(`judge_06〜08`) | reject 3/3(全8回では7回reject) |
| 今回: 学習者向け辞書の見出し形として適切か(`judge_headword_01`、3回、gpt-6-luna、0.224円) | **adopt 3/3**(grammar_pattern_with_slot、学習価値good、意味generalized)。陰性対照`soon to do`はreject 3/3 |

AI意見=**非推奨を維持**(理由は評価ではなく承認済み規則との関係: 本文に無い語`do`/比喩(wave a flag)の学習価値が消える/本文の連続部分列`too soon`で代替できる)。品質水準の最終判断はユーザー(ユーザー自身の例)。採用する場合の条件案=パターン見出し旗・元句と本文の文を併記・gloss再整合必須・AUTO不可。

## 4. 委任_01(RESCUE_TABLE_01)との差分
- 11件の最終区分は同一。変更点は(1)A2を区分3推奨→区分2非推奨、(2)#1のHR旗(意味縮小/低価値)、(3)#4・#5の旗(窓外tail破棄・多義)、(4)慣用句例外の根拠を「辞書見出し(17,389件)に一致」→「レビュー済み閉表27件」、(5)区分1の根拠にM1(語幹検査+除外表)/M2(分詞表・量化詞・限定詞+名詞+分詞)の敵対的testを追加。
- 検証結果の再現: `rescue_eval_08.json`の11件のdecision(category/final_key/final_display/rescuable)は`rescue_eval_07.json`と同一(差は#7/#9のmethod文言のみ)。
