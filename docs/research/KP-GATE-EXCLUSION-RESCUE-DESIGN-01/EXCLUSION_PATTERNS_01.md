# EXCLUSION_PATTERNS_01: KP候補Gate除外パターンの棚卸し(既存ログのみ・API 0・2026-10-26)

構成: 第1部=手直しした要約(ユーザー指定の表+観点別の実在/不在)、第2部=`tools/kp_exclusion_inventory_01.py`の出力(全イベント)。第2部は同scriptの再実行で上書きされる(第1部を残す場合は退避)。データ: HR導入後(`kp_candidates.json` の `dropped[]`、13ファイル・14イベント。うちAI島は2レベル)と、HR導入前の全文選定(`fulltext_p2`)runの選定gate/canonicalization INVALID(`keywords_runtime_metadata.json`が`fulltext_p2`のX66・Z128 run-level、除外イベント81=同一記事の再実行による重複を含む)。A/B/C旧経路(er011_output、`kp_backend=strategy_l`)は27-7により集計から除外した(`er011_output`は34ファイル中`fulltext_p2`該当0)。X/Y/Z別の実績: HR導入後=X3/Y5/Z3(+Human NG 3)、HR導入前=X(CMU 3句・lexical have 1句)/Z(それ以外)。**Yの除外実績はHR導入後の5件のみ(Yの旧runは存在しない)**。

## 1. ユーザー指定の表(実在する除外パターン)

救済区分: **S1**=承認済み規則内で機械的(API 0)に救済可 / **S2**=新規則(ユーザー承認)があれば救済可の見込み / **困難**=救済困難(無理に救済しない)。

| 除外パターン | 実例(Family/run) | 現行の除外理由(原文要旨・実装) | 修正方法 | 救済可否 | 追加コスト |
|---|---|---|---|---|---|
| A. 5語上限超過(選定段) | `too soon to wave a flag`(X AI島 a2、6語)/`offered his hands for the chains`(Z melos、HR導入前) | 語数が1〜5語でない(`er105.validate_and_resolve:236-238`) | 本文連続の部分列に短縮(機械列挙は可、**どれが意味を保つかはAI/HR判断**)。`too`を落とすと意味反転(`soon to wave a flag`=「もうすぐ振る」)する例あり。ユーザー例`too soon to do`は本文に無い`do`を生成し語を削除=現行Rule7原則に反する新規則 | **S2**(段階2c)。HRに「短縮案(元: …)」を数案提示する形なら可。現行規則内の機械処理だけでは選べない | 列挙のみ0円。採用候補ごとにcanonicalization+gloss(既存Gate再適用)で約0.3〜0.6円/LLM call(同記事の実測3行: 0.322/0.526/0.563円) |
| B. 動詞の基本形化がguardで拒否 | `studied separately`(X AI島 a2)/`rang through`(Z melos R4)/`lost touch`・`pulling free`・`eased open`・`growing louder and louder`・`struck a match`(Z、HR導入前) | key('study separately'等)がdisplayと不一致かつspan内連続でない+基本形化例外もguard/閉表で不通過(`er003_kc:605-621`、`er105:662-691`) | **S1: 表層形のままrevert**(無変更=Rule7通過。`studied separately`は既存validatorで通過を机上確認)。原形化は閉表/guard拡張(新規則W2/W3)が必要 | **S1(表層形)**/原形はS2 | 0円(LLM不要)。canonicalization再実行1回(現行の除外後再実行)を省けるため-0.3〜0.6円 |
| C. LLMが範囲を拡張(Rule7) | `rose above`→LLM`rise above the other voices`、`held out`→LLM`hold out one's hands`(Z melos R3 b1b) | key_phraseがsource_spanを超えて拡張→Rule7違反(`er003_kc:605-621`) | **S1: 決定論再導出**(spanの各tokenを現行表の1対1置換候補に置換→validator+CMU通過のもの。`rise above`/`hold out`) | **S1** | 0円 |
| D. 人称一般化+動詞変化の複合 | `my blood went cold`→LLM`one's blood go cold`、`froze my blood`→`freeze someone's blood`、`my ears began to ring`(Z、HR導入前) | 動詞変化は先頭/to直後のみ(`er105:678`)、人称は閉表のみ | S1: 人称一般化だけ残す再導出(`one's blood went cold`)またはrevert。※`sure of myself`/`sentenced him to death`/`couldn't bring myself to…`は現行validatorでは既に通る(HR導入前世代の除外4件) | **S1**(4件は既に解消) | 0円 |
| E. 有限助動詞を含む | `have a say`・`had our eye on`・`have a big moment`(lexical have、X/Y)/`can't be helped`・`could not bear`・`were mocking me`(Z/Y) | 語形リスト`{is,are,was,were,has,have,had,will,would,can,could,should,may,might,must}`のtoken照合(`er003_key_words_min_unit.py:260`)。lexical動詞のhaveも拒否 | lexical haveを助動詞と区別する検査精緻化(**新規則**)。modal/進行形/受動の核を含む句は、縮約すると意味を失う | lexical have=**S2**/modal等=**困難** | 0円(検査の精緻化のみ) |
| F. 本文対応不備 | `catch their interest`(Y SNS)/`lose my trust in you`・`in his place`(Z、HR導入前) | 本文に連続一致しない(`er105:243-248`)=LLMの言い換え・創作 | 本文の近傍表現へ戻す手段が決定論ではない。曖昧一致で拾うと本文対応を失う | **困難** | - |
| G. CMU辞書未登録 | `redelivery fee`(Y)/`minaudière(s)`・`novelty minaudière`(X、HR導入前) | CMU未登録語(`er108`、CURRENT_SPEC.md:2001「LLM推測・代替合格は禁止」) | なし(代替合格を禁じる承認済み規則) | **困難(救済しない)** | - |
| H. 重複/包含/最大件数超過 | HR導入後の実績0件(`duplicate_of_top3`/`overflow`はコードに実在) | `er119_kp_candidates_01.py:81-83,94-98` | 対象外(設計上の正当な除外) | 対象外 | - |
| I. Human NG | 3件(X EV R2 `put in place`・`off the hook`、Z R4 `sentenced him to death`) | NG復活禁止(USER.md:97) | 救済しない | 対象外 | - |

## 2. ユーザーが挙げた観点ごとの「現行Gateに実在するか」

| 観点 | 実在? | 発生実績(HR導入後14イベント/HR導入前81イベント) |
|---|---|---|
| 5語上限の超過 | 実在(選定段) | 1 / 1(`offered his hands for the chains`) |
| 動詞の原形・辞書形への正規化不足 | 実在(Rule7+基本形化例外のguard/閉表) | 4(`studied separately`・`rang through`・`rose above`・`held out`)/ 27(Z。うち4は現行で通過済み) |
| 活用形・時制 | 独立検査は無い。Rule7内の基本形化(B)に含まれる | 上記に含む |
| 受動態 | **独立の検査は実在しない**(`be + 過去分詞`の見出し形は表層連続ならRule7を通る。`be studied separately`は机上でPASS) | 0(専用の除外なし) |
| 本文との対応不備 | 実在(選定段 `locate_phrase`、文境界またぎ検査も実在) | 1 / 2(文境界またぎは0) |
| 一般化の不足・過剰 | **Gateとしては実在しない**。意味保持はcanonicalization LLMのQA 12項目のflag(`qa_overall_status=REVIEW_REQUIRED`)で、除外ではなく`qa_fail`旗(AUTO対象外・Human選択可)として「残す」方式が既に実装済み(`er119_kp_candidates_01.py:293-300`) | 旗: 0 / 10(Z、3句) |
| 重複候補 | 実在(call2の前記3件との同一/包含、Redundancy QA=旗) | Gate除外0 / 0 |
| その他の実在条件 | 有限助動詞(E)・CMU未登録(G)・数値placeholder/旧形式precheck(`er105:213-222`)・Human NG(I)・最大5件超過(H) | E: 4 / 7句、G: 1 / 3句、数値placeholder: 0、overflow: 0 |

## 3. バケット集計(script出力の要約)

| 区分 | HR導入後(14) | HR導入前(81イベント・一意句) |
|---|---|---|
| Gate除外ではない(Human NG/QA旗) | 3 | 10(3句) |
| 現行validatorでは既に通る | 0 | 4句 |
| **S1 承認済み規則内・機械的救済** | **4**(X1・Z3) | 23イベント(12句、Z) |
| **S2 新規則があれば救済** | **3**(X2・Y1) | 5イベント(2句) |
| **困難** | **4**(Y4) | 39イベント(11句) |

HR導入後のGate除外11件(Human NG 3件を除く)のうち、S1=4(36%)、S2=3(27%)、困難=4(36%)。HR導入前は同一記事の再実行(tell-tale heart等)でイベントが重複するため、割合には「一意(Family,句)」を使う: Gate除外の一意句29のうちS1=12(41%)/S2=2(7%)/困難=11(38%)/現行validatorで既に通る=4(14%)。

## 4. 棚卸し対象外だった除外経路(Opus条件Aレビュー(C)、委任_02で追記。件数は分かる範囲、不明は「未集計」)

出典=`OPUS_REVIEW_01.md`(C)1〜4。上記§1〜§3の棚卸し(`kp_candidates.json`の`dropped[]`とpreHRのcanonicalization INVALID)に載らない/載りにくい経路。委任_02では観測のみで、救済はDESIGN_02のR1(トリガー拡張、手段はrevertのみ)とR3(観測のみ)の範囲に限る。

| # | 経路 | 位置 | 件数(分かる範囲) | 救済可否の所見 |
|---|---|---|---|---|
| 1 | `cmu_post_canon`による除外(canonicalization後のCMU再検査で落ちる句) | `er119_kp_candidates_01.py:264-266` | HR導入後のCMU_UNREGISTERED=1(Y `redelivery fee`、選定段か本段かは未区別)/preHR=3句(X)。**本段(post_canon)に限った件数は未集計** | 救済の位置がvalidateの前なので、ここで落ちる句は現設計では救済されない。displayへrevertすればCMUを通る場合に限り救える可能性(revert後のCMU再検査は必須)。`redelivery fee`型(display自体がCMU未登録)は救えない |
| 2 | 外側retry発動時の候補一覧ごとの置換(`dropped_all=[]`、Gate通過済みの良い候補も捨てる) | `er119_kp_candidates_01.py:334-341` | preHR `fulltext_p2` outer_retry_log 78件中25件で発動(32%、再実行を含み過大評価)/HR導入後13 level-runで0。**置換で捨てられたGate通過済み候補の件数は未集計** | 最大の破棄経路。救済では扱わず、R3(観測のみ)で`dropped`/inventoryへ記録する |
| 3 | canonicalization段の非Rule7構造違反(OF-X1=左端条件違反[`er003_key_words_canonicalization.py:600-605`]、canon段の語数>5、LLMが有限助動詞を混入) | 同`:599-620` | HR導入後: FINITE_AUX_TOKEN=4(X `had our eye on`、Y `have a say`・`can't be helped`×2。選定段起因かcanon混入かは未区別)。OF-X1違反/canon段語数>5の件数は未集計 | revertで救える可能性があるのにトリガーが「Rule7(基本形化)」に限定されている。DESIGN_02ではR1によりトリガーを「LLM keyが原因の構造違反全般」へ拡張(手段はrevertのみ=受理面不変)。ただし有限助動詞が本文(display)側にもある場合(`can't be helped`)はrevertでも救えない |
| 4 | call1(選定段)のgate失敗(`sc.run_key_phrase_selection`内のretry)で句が記録されずに消える | `er003_v1_n3_01_scaffold_generate.py`内 | **未集計**(dropped/inventoryに載らないため既存ログから数えられない) | 記録がなく件数不明。R3で観測のみ(記録)を追加する案。救済はしない |

---

# 第2部: script出力(全イベント)
# EXCLUSION_PATTERNS_01 (script出力部。API 0・read-only)

生成: `docs/research/KP-GATE-EXCLUSION-RESCUE-DESIGN-01/tools/kp_exclusion_inventory_01.py`。分類は現行Gateの理由原文の機械分類。

## HR(kp_candidates.json dropped): 除外イベント 14件

| 区分(class/sub) | イベント数 | 一意(Family,句)数 |
|---|---|---|
| CMU_UNREGISTERED | 1 | 1 |
| FINITE_AUX_TOKEN | 4 | 4 |
| HUMAN_NG_EXCLUDED | 3 | 3 |
| NOT_CONTIGUOUS_IN_TEXT | 1 | 1 |
| RULE7_NORMALIZATION/LEMMA_1TO1_REJECTED | 2 | 2 |
| RULE7_NORMALIZATION/LLM_EXPANDED_BEYOND_SPAN | 2 | 2 |
| WORDCOUNT_OVER5 | 1 | 1 |

### 救済区分(bucket)

| 区分 | イベント数 | 一意(Family,句)数 | 意味 |
|---|---|---|---|
| NOT_GATE | 3 | 3 | Gate除外ではない(Human NG=復活禁止 / QA旗) |
| S1_IN_SCOPE_MECHANICAL | 4 | 4 | 段階1: 承認済み規則内・機械的(API 0)で救済可(再導出 or 表層形revert。既存validator通過を机上確認) |
| S2_NEEDS_NEW_RULE | 3 | 3 | 段階2: 新規則(ユーザー承認要)があれば救済可の見込み |
| HARD | 4 | 4 | 救済困難(意味喪失・本文対応喪失・CMU必須Gate等) |

Family別bucket: X|NOT_GATE=2, X|S1_IN_SCOPE_MECHANICAL=1, X|S2_NEEDS_NEW_RULE=2, Y|HARD=4, Y|S2_NEEDS_NEW_RULE=1, Z|NOT_GATE=1, Z|S1_IN_SCOPE_MECHANICAL=3

Family別: X|FINITE_AUX_TOKEN=1, X|HUMAN_NG_EXCLUDED=2, X|RULE7_NORMALIZATION=1, X|WORDCOUNT_OVER5=1, Y|CMU_UNREGISTERED=1, Y|FINITE_AUX_TOKEN=3, Y|NOT_CONTIGUOUS_IN_TEXT=1, Z|HUMAN_NG_EXCLUDED=1, Z|RULE7_NORMALIZATION=3

## preHR(outer-retry全置換): 除外イベント 81件

| 区分(class/sub) | イベント数 | 一意(Family,句)数 |
|---|---|---|
| CMU_UNREGISTERED | 5 | 3 |
| FINITE_AUX_TOKEN | 36 | 7 |
| NOT_CONTIGUOUS_IN_TEXT | 2 | 2 |
| QA_REVIEW_REQUIRED(非除外・旗) | 10 | 3 |
| RULE7_NORMALIZATION/LEMMA_1TO1_REJECTED | 9 | 7 |
| RULE7_NORMALIZATION/PERSON_GENERALIZATION_REJECTED | 18 | 9 |
| WORDCOUNT_OVER5 | 1 | 1 |

### 救済区分(bucket)

| 区分 | イベント数 | 一意(Family,句)数 | 意味 |
|---|---|---|---|
| NOT_GATE | 10 | 3 | Gate除外ではない(Human NG=復活禁止 / QA旗) |
| NOW_PASS | 4 | 4 | 過去世代validatorの除外で、現行validatorでは既に通る |
| S1_IN_SCOPE_MECHANICAL | 23 | 12 | 段階1: 承認済み規則内・機械的(API 0)で救済可(再導出 or 表層形revert。既存validator通過を机上確認) |
| S2_NEEDS_NEW_RULE | 5 | 2 | 段階2: 新規則(ユーザー承認要)があれば救済可の見込み |
| HARD | 39 | 11 | 救済困難(意味喪失・本文対応喪失・CMU必須Gate等) |

Family別bucket: X|HARD=5, X|S2_NEEDS_NEW_RULE=4, Z|HARD=34, Z|NOT_GATE=10, Z|NOW_PASS=4, Z|S1_IN_SCOPE_MECHANICAL=23, Z|S2_NEEDS_NEW_RULE=1

Family別: X|CMU_UNREGISTERED=5, X|FINITE_AUX_TOKEN=4, Z|FINITE_AUX_TOKEN=32, Z|NOT_CONTIGUOUS_IN_TEXT=2, Z|QA_REVIEW_REQUIRED(非除外・旗)=10, Z|RULE7_NORMALIZATION=27, Z|WORDCOUNT_OVER5=1

## 実例(全イベント)

| era | Family | run | lv | stage | 句 | class/sub | bucket(note) | 理由(先頭110字) |
|---|---|---|---|---|---|---|---|---|
| HR | X | family_x_audio_production_wiring_01/ai_island_temple__run_ai_01/a2 | a2 | validate | `too soon to wave a flag` | WORDCOUNT_OVER5 | S2_NEEDS_NEW_RULE (部分列短縮(選定段。意味反転リスクあり=AI/HR判断)) | 語数が1〜5語でない(実際: 6語) |
| HR | X | family_x_audio_production_wiring_01/ai_island_temple__run_ai_01/a2 | a2 | canonicalization | `studied separately` | RULE7_NORMALIZATION/LEMMA_1TO1_REJECTED | S1_IN_SCOPE_MECHANICAL (表層形revert(基本形化は閉表/guard拡張[新規則]で可: study separately)) | key_phrase('study separately')がdisplay_phraseと一致せず、source_span('studied separately')内の連続部分文字列でもない(人称代名詞・所有格の一般 |
| HR | X | family_x_audio_production_wiring_01/part2_hr_evidence_01__run_r2/a2 | a2 | human_ng | `put in place` | HUMAN_NG_EXCLUDED | NOT_GATE | 除外指定の語句(Humanが不適切(NG)と指定: evidence R1: AI top1 NG登録(共有registry検証用)) |
| HR | X | family_x_audio_production_wiring_01/part2_hr_evidence_01__run_r2/b1b | b1b | human_ng | `off the hook` | HUMAN_NG_EXCLUDED | NOT_GATE | 除外指定の語句(Humanが不適切(NG)と指定: evidence R1: off the hook NG(共有registry検証)) |
| HR | X | family_x_audio_production_wiring_01/part2_hr_evidence_01__run_r2/b1b | b1b | validate | `had our eye on` | FINITE_AUX_TOKEN | S2_NEEDS_NEW_RULE (lexical have(語形リストが助動詞と区別しない)=Gate精緻化) | 有限助動詞を含む(既存canonicalization Validatorが拒否する形) |
| HR | Z | family_z_production_e2e_01/melos/run_p2_evidence_r3 | b1b | canonicalization | `rose above` | RULE7_NORMALIZATION/LLM_EXPANDED_BEYOND_SPAN | S1_IN_SCOPE_MECHANICAL (再導出:rise above) | key_phrase('rise above the other voices')がdisplay_phraseと一致せず、source_span('rose above')内の連続部分文字列でもない(人称代名詞・所有格 |
| HR | Z | family_z_production_e2e_01/melos/run_p2_evidence_r3 | b1b | canonicalization | `held out` | RULE7_NORMALIZATION/LLM_EXPANDED_BEYOND_SPAN | S1_IN_SCOPE_MECHANICAL (再導出:hold out) | key_phrase("hold out one's hands")がdisplay_phraseと一致せず、source_span('held out')内の連続部分文字列でもない(人称代名詞・所有格の一般化[閉じた語 |
| HR | Z | family_z_production_e2e_01/melos/run_p2_evidence_r4 | b1b | human_ng | `sentenced him to death` | HUMAN_NG_EXCLUDED | NOT_GATE | 除外指定の語句(Humanが不適切(NG)と指定: evidence R3: AI top1 NG(共有registry検証)) |
| HR | Z | family_z_production_e2e_01/melos/run_p2_evidence_r4 | b1b | canonicalization | `rang through` | RULE7_NORMALIZATION/LEMMA_1TO1_REJECTED | S1_IN_SCOPE_MECHANICAL (表層形revert(基本形化は閉表/guard拡張[新規則]で可: ring through)) | key_phrase('ring through')がdisplay_phraseと一致せず、source_span('rang through')内の連続部分文字列でもない(人称代名詞・所有格の一般化[閉じた語彙集合に |
| HR | Y | family_y_production_01/redelivery_fee/run_01 | a2 | validate | `it can’t be helped` | FINITE_AUX_TOKEN | HARD (法助動詞/進行形aux等。句の核であり縮約すると意味喪失) | 有限助動詞を含む(既存canonicalization Validatorが拒否する形) |
| HR | Y | family_y_production_01/redelivery_fee/run_01 | a2 | cmu | `redelivery fee` | CMU_UNREGISTERED | HARD (CMU必須Gate(代替合格禁止)) | CMU発音辞書に登録されていない語を含む(未登録語: redelivery。構成する全ての語がCMU辞書に登録された語句だけを選ぶ) |
| HR | Y | family_y_production_01/redelivery_fee/run_01 | b1b | validate | `can’t be helped` | FINITE_AUX_TOKEN | HARD (法助動詞/進行形aux等。句の核であり縮約すると意味喪失) | 有限助動詞を含む(既存canonicalization Validatorが拒否する形) |
| HR | Y | family_y_production_01/sns_age_limit/run_01 | b1b | validate | `have a say` | FINITE_AUX_TOKEN | S2_NEEDS_NEW_RULE (lexical have(語形リストが助動詞と区別しない)=Gate精緻化) | 有限助動詞を含む(既存canonicalization Validatorが拒否する形) |
| HR | Y | family_y_production_01/sns_age_limit/run_01 | b1b | validate | `catch their interest` | NOT_CONTIGUOUS_IN_TEXT | HARD (本文に無い(本文対応喪失)) | 本文に連続一致しない(変更・言い換え・創作) |
| preHR | X | family_x_audio_production_wiring_01/small_bag__run_f1fix_01/a2 | a2 | selector_gate(validate/CMU) | `minaudières` | CMU_UNREGISTERED | HARD (CMU必須Gate(代替合格禁止)) | CMU発音辞書に登録されていない語を含む(未登録語: minaudières。構成する全ての語がCMU辞書に登録された語句だけを選ぶ) |
| preHR | X | family_x_audio_production_wiring_01/small_bag__run_kpq_01/a2 | a2 | selector_gate(validate/CMU) | `minaudières` | CMU_UNREGISTERED | HARD (CMU必須Gate(代替合格禁止)) | CMU発音辞書に登録されていない語を含む(未登録語: minaudières。構成する全ての語がCMU辞書に登録された語句だけを選ぶ) |
| preHR | X | family_x_audio_production_wiring_01/small_bag__run_kpq_01/a2 | a2 | selector_gate(validate/CMU) | `novelty minaudière` | CMU_UNREGISTERED | HARD (CMU必須Gate(代替合格禁止)) | CMU発音辞書に登録されていない語を含む(未登録語: minaudière。構成する全ての語がCMU辞書に登録された語句だけを選ぶ) |
| preHR | X | family_x_audio_production_wiring_01/small_bag__run_kpq_02/a2 | a2 | selector_gate(validate/CMU) | `minaudière` | CMU_UNREGISTERED | HARD (CMU必須Gate(代替合格禁止)) | CMU発音辞書に登録されていない語を含む(未登録語: minaudière。構成する全ての語がCMU辞書に登録された語句だけを選ぶ) |
| preHR | X | family_x_audio_production_wiring_01/small_bag__run_kpq_02/a2 | a2 | selector_gate(validate/CMU) | `minaudières` | CMU_UNREGISTERED | HARD (CMU必須Gate(代替合格禁止)) | CMU発音辞書に登録されていない語を含む(未登録語: minaudières。構成する全ての語がCMU辞書に登録された語句だけを選ぶ) |
| preHR | X | family_x_audio_production_wiring_01/small_bag__run_f1fix_01/a2 | a2 | canonicalization | `have a big moment` | FINITE_AUX_TOKEN | S2_NEEDS_NEW_RULE (lexical have(語形リストが助動詞と区別しない)=Gate精緻化) | 有限助動詞が含まれている |
| preHR | X | family_x_audio_production_wiring_01/small_bag__run_jre_01/a2 | a2 | canonicalization | `have a big moment` | FINITE_AUX_TOKEN | S2_NEEDS_NEW_RULE (lexical have(語形リストが助動詞と区別しない)=Gate精緻化) | 有限助動詞が含まれている |
| preHR | X | family_x_audio_production_wiring_01/small_bag__run_kpq_01/a2 | a2 | canonicalization | `have a big moment` | FINITE_AUX_TOKEN | S2_NEEDS_NEW_RULE (lexical have(語形リストが助動詞と区別しない)=Gate精緻化) | 有限助動詞が含まれている |
| preHR | X | family_x_audio_production_wiring_01/small_bag__run_kpq_02/a2 | a2 | canonicalization | `have a big moment` | FINITE_AUX_TOKEN | S2_NEEDS_NEW_RULE (lexical have(語形リストが助動詞と区別しない)=Gate精緻化) | 有限助動詞が含まれている |
| preHR | Z | fz_essence_01/the_tell_tale_heart/1b_s1 | b1b | selector_gate(validate/CMU) | `were mocking me` | FINITE_AUX_TOKEN | HARD (法助動詞/進行形aux等。句の核であり縮約すると意味喪失) | 有限助動詞を含む(既存canonicalization Validatorが拒否する形) |
| preHR | Z | family_z_production_e2e_01/melos/run_aho4_z_h3 | a2 | selector_gate(validate/CMU) | `offered his hands for the chains` | WORDCOUNT_OVER5 | S2_NEEDS_NEW_RULE (部分列短縮(選定段。意味反転リスクあり=AI/HR判断)) | 語数が1〜5語でない(実際: 6語) |
| preHR | Z | family_z_production_e2e_01/melos/run_kpgm20_01 | a2 | selector_gate(validate/CMU) | `lose my trust in you` | NOT_CONTIGUOUS_IN_TEXT | HARD (本文に無い(本文対応喪失)) | 本文に連続一致しない(変更・言い換え・創作) |
| preHR | Z | family_z_production_e2e_01/melos/run_kpgm20_02 | a2 | selector_gate(validate/CMU) | `in his place` | NOT_CONTIGUOUS_IN_TEXT | HARD (本文に無い(本文対応喪失)) | 本文に連続一致しない(変更・言い換え・創作) |
| preHR | Z | family_z_production_e2e_01/the_tell_tale_heart/run_chunk_01 | b1b | selector_gate(validate/CMU) | `Could you have borne it` | FINITE_AUX_TOKEN | HARD (法助動詞/進行形aux等。句の核であり縮約すると意味喪失) | 有限助動詞を含む(既存canonicalization Validatorが拒否する形) |
| preHR | Z | family_z_production_e2e_01/the_tell_tale_heart/run_chunk_01 | b1b | selector_gate(validate/CMU) | `could have borne it` | FINITE_AUX_TOKEN | HARD (法助動詞/進行形aux等。句の核であり縮約すると意味喪失) | 本文に連続一致しない(変更・言い換え・創作) / 有限助動詞を含む(既存canonicalization Validatorが拒否する形) |
| preHR | Z | family_z_production_e2e_01/the_tell_tale_heart/run_p1_evidence_01 | a2 | selector_gate(validate/CMU) | `Could you bear that?` | FINITE_AUX_TOKEN | HARD (法助動詞/進行形aux等。句の核であり縮約すると意味喪失) | 本文に連続一致しない(変更・言い換え・創作) / 有限助動詞を含む(既存canonicalization Validatorが拒否する形) |
| preHR | Z | family_z_production_e2e_01/the_tell_tale_heart/run_p1_evidence_01 | b1b | selector_gate(validate/CMU) | `Could you have borne it` | FINITE_AUX_TOKEN | HARD (法助動詞/進行形aux等。句の核であり縮約すると意味喪失) | 有限助動詞を含む(既存canonicalization Validatorが拒否する形) |
| preHR | Z | family_z_production_e2e_01/the_tell_tale_heart/run_p1_evidence_01 | b1b | selector_gate(validate/CMU) | `could have borne it` | FINITE_AUX_TOKEN | HARD (法助動詞/進行形aux等。句の核であり縮約すると意味喪失) | 本文に連続一致しない(変更・言い換え・創作) / 有限助動詞を含む(既存canonicalization Validatorが拒否する形) |
| preHR | Z | family_z_production_e2e_01/the_tell_tale_heart/run_p1_evidence_02 | a2 | selector_gate(validate/CMU) | `Could you bear that?` | FINITE_AUX_TOKEN | HARD (法助動詞/進行形aux等。句の核であり縮約すると意味喪失) | 本文に連続一致しない(変更・言い換え・創作) / 有限助動詞を含む(既存canonicalization Validatorが拒否する形) |
| preHR | Z | family_z_production_e2e_01/the_tell_tale_heart/run_p1_evidence_02 | b1b | selector_gate(validate/CMU) | `Could you have borne it` | FINITE_AUX_TOKEN | HARD (法助動詞/進行形aux等。句の核であり縮約すると意味喪失) | 有限助動詞を含む(既存canonicalization Validatorが拒否する形) |
| preHR | Z | family_z_production_e2e_01/the_tell_tale_heart/run_p1_evidence_02 | b1b | selector_gate(validate/CMU) | `could have borne it` | FINITE_AUX_TOKEN | HARD (法助動詞/進行形aux等。句の核であり縮約すると意味喪失) | 本文に連続一致しない(変更・言い換え・創作) / 有限助動詞を含む(既存canonicalization Validatorが拒否する形) |
| preHR | Z | family_z_production_e2e_01/the_tell_tale_heart/run_p1_evidence_03 | a2 | selector_gate(validate/CMU) | `Could you bear that?` | FINITE_AUX_TOKEN | HARD (法助動詞/進行形aux等。句の核であり縮約すると意味喪失) | 本文に連続一致しない(変更・言い換え・創作) / 有限助動詞を含む(既存canonicalization Validatorが拒否する形) |
| preHR | Z | family_z_production_e2e_01/the_tell_tale_heart/run_p1_evidence_03 | b1b | selector_gate(validate/CMU) | `Could you have borne it` | FINITE_AUX_TOKEN | HARD (法助動詞/進行形aux等。句の核であり縮約すると意味喪失) | 有限助動詞を含む(既存canonicalization Validatorが拒否する形) |
| preHR | Z | family_z_production_e2e_01/the_tell_tale_heart/run_p1_evidence_03 | b1b | selector_gate(validate/CMU) | `could have borne it` | FINITE_AUX_TOKEN | HARD (法助動詞/進行形aux等。句の核であり縮約すると意味喪失) | 本文に連続一致しない(変更・言い換え・創作) / 有限助動詞を含む(既存canonicalization Validatorが拒否する形) |
| preHR | Z | family_z_production_e2e_01/the_tell_tale_heart/run_p2_evidence_r3 | a2 | selector_gate(validate/CMU) | `Could you bear that?` | FINITE_AUX_TOKEN | HARD (法助動詞/進行形aux等。句の核であり縮約すると意味喪失) | 本文に連続一致しない(変更・言い換え・創作) / 有限助動詞を含む(既存canonicalization Validatorが拒否する形) |
| preHR | Z | family_z_production_e2e_01/the_tell_tale_heart/run_p2_evidence_r3 | b1b | selector_gate(validate/CMU) | `Could you have borne it` | FINITE_AUX_TOKEN | HARD (法助動詞/進行形aux等。句の核であり縮約すると意味喪失) | 有限助動詞を含む(既存canonicalization Validatorが拒否する形) |
| preHR | Z | family_z_production_e2e_01/the_tell_tale_heart/run_p2_evidence_r3 | b1b | selector_gate(validate/CMU) | `could have borne it` | FINITE_AUX_TOKEN | HARD (法助動詞/進行形aux等。句の核であり縮約すると意味喪失) | 本文に連続一致しない(変更・言い換え・創作) / 有限助動詞を含む(既存canonicalization Validatorが拒否する形) |
| preHR | Z | family_z_production_e2e_01/the_tell_tale_heart/run_p2_evidence_r4 | a2 | selector_gate(validate/CMU) | `Could you bear that?` | FINITE_AUX_TOKEN | HARD (法助動詞/進行形aux等。句の核であり縮約すると意味喪失) | 本文に連続一致しない(変更・言い換え・創作) / 有限助動詞を含む(既存canonicalization Validatorが拒否する形) |
| preHR | Z | family_z_production_e2e_01/the_tell_tale_heart/run_p2_evidence_r4 | b1b | selector_gate(validate/CMU) | `Could you have borne it` | FINITE_AUX_TOKEN | HARD (法助動詞/進行形aux等。句の核であり縮約すると意味喪失) | 有限助動詞を含む(既存canonicalization Validatorが拒否する形) |
| preHR | Z | family_z_production_e2e_01/the_tell_tale_heart/run_p2_evidence_r4 | b1b | selector_gate(validate/CMU) | `could have borne it` | FINITE_AUX_TOKEN | HARD (法助動詞/進行形aux等。句の核であり縮約すると意味喪失) | 本文に連続一致しない(変更・言い換え・創作) / 有限助動詞を含む(既存canonicalization Validatorが拒否する形) |
| preHR | Z | family_z_production_e2e_01/the_tell_tale_heart/run_sf_prod_01 | a2 | selector_gate(validate/CMU) | `could not bear` | FINITE_AUX_TOKEN | HARD (法助動詞/進行形aux等。句の核であり縮約すると意味喪失) | 有限助動詞を含む(既存canonicalization Validatorが拒否する形) |
| preHR | Z | family_z_production_e2e_01/the_tell_tale_heart/run_sf_prod_01 | a2 | selector_gate(validate/CMU) | `could not bear another second` | FINITE_AUX_TOKEN | HARD (法助動詞/進行形aux等。句の核であり縮約すると意味喪失) | 有限助動詞を含む(既存canonicalization Validatorが拒否する形) |
| preHR | Z | family_z_production_e2e_01/the_tell_tale_heart/run_sf_prod_02 | a2 | selector_gate(validate/CMU) | `Could you bear that?` | FINITE_AUX_TOKEN | HARD (法助動詞/進行形aux等。句の核であり縮約すると意味喪失) | 本文に連続一致しない(変更・言い換え・創作) / 有限助動詞を含む(既存canonicalization Validatorが拒否する形) |
| preHR | Z | family_z_production_e2e_01/the_tell_tale_heart/run_sf_prod_02 | b1b | selector_gate(validate/CMU) | `Could you have borne it` | FINITE_AUX_TOKEN | HARD (法助動詞/進行形aux等。句の核であり縮約すると意味喪失) | 有限助動詞を含む(既存canonicalization Validatorが拒否する形) |
| preHR | Z | family_z_production_e2e_01/the_tell_tale_heart/run_sf_prod_02 | b1b | selector_gate(validate/CMU) | `could have borne it` | FINITE_AUX_TOKEN | HARD (法助動詞/進行形aux等。句の核であり縮約すると意味喪失) | 本文に連続一致しない(変更・言い換え・創作) / 有限助動詞を含む(既存canonicalization Validatorが拒否する形) |
| preHR | Z | _bak_pre04/a2/keywords_runtime_metadata.json | a2 | selector_gate(validate/CMU) | `could not bear another second` | FINITE_AUX_TOKEN | HARD (法助動詞/進行形aux等。句の核であり縮約すると意味喪失) | 有限助動詞を含む(既存canonicalization Validatorが拒否する形) |
| preHR | Z | outer_retry/attempt_1/keywords_runtime_metadata.json | a2 | selector_gate(validate/CMU) | `could not bear another second` | FINITE_AUX_TOKEN | HARD (法助動詞/進行形aux等。句の核であり縮約すると意味喪失) | 有限助動詞を含む(既存canonicalization Validatorが拒否する形) |
| preHR | Z | outer_retry/attempt_2/keywords_runtime_metadata.json | a2 | selector_gate(validate/CMU) | `could not bear another second` | FINITE_AUX_TOKEN | HARD (法助動詞/進行形aux等。句の核であり縮約すると意味喪失) | 有限助動詞を含む(既存canonicalization Validatorが拒否する形) |
| preHR | Z | outer_retry/attempt_3/keywords_runtime_metadata.json | a2 | selector_gate(validate/CMU) | `could not bear another second` | FINITE_AUX_TOKEN | HARD (法助動詞/進行形aux等。句の核であり縮約すると意味喪失) | 有限助動詞を含む(既存canonicalization Validatorが拒否する形) |
| preHR | Z | kp_try1/a2/keywords_runtime_metadata.json | a2 | selector_gate(validate/CMU) | `could not bear` | FINITE_AUX_TOKEN | HARD (法助動詞/進行形aux等。句の核であり縮約すると意味喪失) | 有限助動詞を含む(既存canonicalization Validatorが拒否する形) |
| preHR | Z | outer_retry/attempt_2/keywords_runtime_metadata.json | a2 | selector_gate(validate/CMU) | `could not bear` | FINITE_AUX_TOKEN | HARD (法助動詞/進行形aux等。句の核であり縮約すると意味喪失) | 有限助動詞を含む(既存canonicalization Validatorが拒否する形) |
| preHR | Z | mode_A/kp/keywords_runtime_metadata.json | ? | selector_gate(validate/CMU) | `could not bear` | FINITE_AUX_TOKEN | HARD (法助動詞/進行形aux等。句の核であり縮約すると意味喪失) | 有限助動詞を含む(既存canonicalization Validatorが拒否する形) |
| preHR | Z | outer_retry/attempt_2/keywords_runtime_metadata.json | ? | selector_gate(validate/CMU) | `could not bear` | FINITE_AUX_TOKEN | HARD (法助動詞/進行形aux等。句の核であり縮約すると意味喪失) | 有限助動詞を含む(既存canonicalization Validatorが拒否する形) |
| preHR | Z | outer_retry/attempt_3/keywords_runtime_metadata.json | ? | selector_gate(validate/CMU) | `could not bear` | FINITE_AUX_TOKEN | HARD (法助動詞/進行形aux等。句の核であり縮約すると意味喪失) | 有限助動詞を含む(既存canonicalization Validatorが拒否する形) |
| preHR | Z | mode_B/kp/keywords_runtime_metadata.json | ? | selector_gate(validate/CMU) | `vulture's` | QA_REVIEW_REQUIRED(非除外・旗) | NOT_GATE | 外側retryで不適合と確定済みの語句の再選択(前回の理由: canonicalization QAでFAIL(学習単位として不適切の疑い): qa_standalone_natural_unit, qa_no_resi |
| preHR | Z | outer_retry/attempt_2/keywords_runtime_metadata.json | ? | selector_gate(validate/CMU) | `vulture's` | QA_REVIEW_REQUIRED(非除外・旗) | NOT_GATE | 外側retryで不適合と確定済みの語句の再選択(前回の理由: canonicalization QAでFAIL(学習単位として不適切の疑い): qa_standalone_natural_unit, qa_no_resi |
| preHR | Z | mode_C/kp/keywords_runtime_metadata.json | ? | selector_gate(validate/CMU) | `in heaven and on earth` | QA_REVIEW_REQUIRED(非除外・旗) | NOT_GATE | 外側retryで不適合と確定済みの語句の再選択(前回の理由: canonicalization QAでFAIL(学習単位として不適切の疑い): qa_standalone_natural_unit, qa_no_resi |
| preHR | Z | mode_C/kp/keywords_runtime_metadata.json | ? | selector_gate(validate/CMU) | `vulture's` | QA_REVIEW_REQUIRED(非除外・旗) | NOT_GATE | 外側retryで不適合と確定済みの語句の再選択(前回の理由: canonicalization QAでFAIL(学習単位として不適切の疑い): qa_standalone_natural_unit, qa_no_resi |
| preHR | Z | mode_C/kp/keywords_runtime_metadata.json | ? | selector_gate(validate/CMU) | `metal catch` | QA_REVIEW_REQUIRED(非除外・旗) | NOT_GATE | 外側retryで不適合と確定済みの語句の再選択(前回の理由: canonicalization QAでFAIL(学習単位として不適切の疑い): qa_standalone_natural_unit, qa_no_resi |
| preHR | Z | outer_retry/attempt_2/keywords_runtime_metadata.json | ? | selector_gate(validate/CMU) | `in heaven and on earth` | QA_REVIEW_REQUIRED(非除外・旗) | NOT_GATE | 外側retryで不適合と確定済みの語句の再選択(前回の理由: canonicalization QAでFAIL(学習単位として不適切の疑い): qa_standalone_natural_unit, qa_no_resi |
| preHR | Z | outer_retry/attempt_2/keywords_runtime_metadata.json | ? | selector_gate(validate/CMU) | `metal catch` | QA_REVIEW_REQUIRED(非除外・旗) | NOT_GATE | 外側retryで不適合と確定済みの語句の再選択(前回の理由: canonicalization QAでFAIL(学習単位として不適切の疑い): qa_standalone_natural_unit, qa_no_resi |
| preHR | Z | outer_retry/attempt_3/keywords_runtime_metadata.json | ? | selector_gate(validate/CMU) | `in heaven and on earth` | QA_REVIEW_REQUIRED(非除外・旗) | NOT_GATE | 外側retryで不適合と確定済みの語句の再選択(前回の理由: canonicalization QAでFAIL(学習単位として不適切の疑い): qa_standalone_natural_unit, qa_no_resi |
| preHR | Z | outer_retry/attempt_3/keywords_runtime_metadata.json | ? | selector_gate(validate/CMU) | `vulture's` | QA_REVIEW_REQUIRED(非除外・旗) | NOT_GATE | 外側retryで不適合と確定済みの語句の再選択(前回の理由: canonicalization QAでFAIL(学習単位として不適切の疑い): qa_standalone_natural_unit, qa_no_resi |
| preHR | Z | outer_retry/attempt_3/keywords_runtime_metadata.json | ? | selector_gate(validate/CMU) | `metal catch` | QA_REVIEW_REQUIRED(非除外・旗) | NOT_GATE | 外側retryで不適合と確定済みの語句の再選択(前回の理由: canonicalization QAでFAIL(学習単位として不適切の疑い): qa_standalone_natural_unit, qa_no_resi |
| preHR | Z | fz_essence_01/the_tell_tale_heart/1b_s1 | b1b | canonicalization | `my ears began to ring` | RULE7_NORMALIZATION/PERSON_GENERALIZATION_REJECTED | S1_IN_SCOPE_MECHANICAL (再導出:one's ears began to ring) | key_phrase("one's ears begin to ring")がdisplay_phraseと一致せず、source_span('my ears began to ring')内の連続部分文字列でもない(人 |
| preHR | Z | family_z_production_e2e_01/after_twenty_years/run_sf_prod_01 | a2 | canonicalization | `lost touch` | RULE7_NORMALIZATION/LEMMA_1TO1_REJECTED | S1_IN_SCOPE_MECHANICAL (表層形revert) | key_phrase('lose touch')がdisplay_phraseと一致せず、source_span('lost touch')内の連続部分文字列でもない(人称代名詞・所有格の一般化[閉じた語彙集合による1対 |
| preHR | Z | family_z_production_e2e_01/after_twenty_years/run_sf_prod_01 | b1b | canonicalization | `couldn't bring myself to arrest` | RULE7_NORMALIZATION/PERSON_GENERALIZATION_REJECTED | NOW_PASS | key_phrase("couldn't bring oneself to arrest")がdisplay_phraseと一致せず、source_span("couldn't bring myself to arres |
| preHR | Z | family_z_production_e2e_01/after_twenty_years/run_sf_prod_01 | b1b | canonicalization | `lost touch` | RULE7_NORMALIZATION/LEMMA_1TO1_REJECTED | S1_IN_SCOPE_MECHANICAL (表層形revert) | key_phrase('lose touch')がdisplay_phraseと一致せず、source_span('lost touch')内の連続部分文字列でもない(人称代名詞・所有格の一般化[閉じた語彙集合による1対 |
| preHR | Z | family_z_production_e2e_01/after_twenty_years/run_sf_prod_01 | b1b | canonicalization | `couldn't bring myself to` | RULE7_NORMALIZATION/PERSON_GENERALIZATION_REJECTED | NOW_PASS | key_phrase("couldn't bring oneself to")がdisplay_phraseと一致せず、source_span("couldn't bring myself to")内の連続部分文字列でも |
| preHR | Z | family_z_production_e2e_01/after_twenty_years/run_sf_prod_01 | b1b | canonicalization | `struck a match` | RULE7_NORMALIZATION/LEMMA_1TO1_REJECTED | S1_IN_SCOPE_MECHANICAL (表層形revert) | key_phrase('strike a match')がdisplay_phraseと一致せず、source_span('struck a match')内の連続部分文字列でもない(人称代名詞・所有格の一般化[閉じた語 |
| preHR | Z | family_z_production_e2e_01/melos/run_jre_01 | b1b | canonicalization | `sentenced him to death` | RULE7_NORMALIZATION/PERSON_GENERALIZATION_REJECTED | NOW_PASS | key_phrase('sentence someone to death')がdisplay_phraseと一致せず、source_span('sentenced him to death')内の連続部分文字列でもない |
| preHR | Z | family_z_production_e2e_01/melos/run_jre_01 | b1b | canonicalization | `nearly abandoned you` | RULE7_NORMALIZATION/PERSON_GENERALIZATION_REJECTED | S1_IN_SCOPE_MECHANICAL (再導出:nearly abandoned someone) | key_phrase('nearly abandon someone')がdisplay_phraseと一致せず、source_span('nearly abandoned you')内の連続部分文字列でもない(人称代名 |
| preHR | Z | family_z_production_e2e_01/the_monkeys_paw/run_kpgm35_01 | a2 | canonicalization | `pulling free` | RULE7_NORMALIZATION/LEMMA_1TO1_REJECTED | S1_IN_SCOPE_MECHANICAL (表層形revert) | key_phrase('pull free')がdisplay_phraseと一致せず、source_span('pulling free')内の連続部分文字列でもない(人称代名詞・所有格の一般化[閉じた語彙集合による1 |
| preHR | Z | family_z_production_e2e_01/the_monkeys_paw/run_kpgm35_01 | b1b | canonicalization | `accepts no responsibility` | RULE7_NORMALIZATION/LEMMA_1TO1_REJECTED | S1_IN_SCOPE_MECHANICAL (表層形revert(基本形化は閉表/guard拡張[新規則]で可: accept no responsibility)) | key_phrase('accept no responsibility')がdisplay_phraseと一致せず、source_span('accepts no responsibility')内の連続部分文字列でも |
| preHR | Z | family_z_production_e2e_01/the_monkeys_paw/run_sf_prod_01 | a2 | canonicalization | `pulling free` | RULE7_NORMALIZATION/LEMMA_1TO1_REJECTED | S1_IN_SCOPE_MECHANICAL (表層形revert) | key_phrase('pull free')がdisplay_phraseと一致せず、source_span('pulling free')内の連続部分文字列でもない(人称代名詞・所有格の一般化[閉じた語彙集合による1 |
| preHR | Z | family_z_production_e2e_01/the_tell_tale_heart/run_chunk_01 | a2 | canonicalization | `growing louder and louder` | RULE7_NORMALIZATION/LEMMA_1TO1_REJECTED | S1_IN_SCOPE_MECHANICAL (表層形revert) | key_phrase('grow louder and louder')がdisplay_phraseと一致せず、source_span('growing louder and louder')内の連続部分文字列でもない |
| preHR | Z | family_z_production_e2e_01/the_tell_tale_heart/run_chunk_01 | b1b | canonicalization | `my blood went cold` | RULE7_NORMALIZATION/PERSON_GENERALIZATION_REJECTED | S1_IN_SCOPE_MECHANICAL (再導出:one's blood went cold) | key_phrase("one's blood go cold")がdisplay_phraseと一致せず、source_span('my blood went cold')内の連続部分文字列でもない(人称代名詞・所有格 |
| preHR | Z | family_z_production_e2e_01/the_tell_tale_heart/run_p1_evidence_01 | b1b | canonicalization | `my blood went cold` | RULE7_NORMALIZATION/PERSON_GENERALIZATION_REJECTED | S1_IN_SCOPE_MECHANICAL (再導出:one's blood went cold) | key_phrase("one's blood go cold")がdisplay_phraseと一致せず、source_span('my blood went cold')内の連続部分文字列でもない(人称代名詞・所有格 |
| preHR | Z | family_z_production_e2e_01/the_tell_tale_heart/run_p1_evidence_02 | b1b | canonicalization | `my blood went cold` | RULE7_NORMALIZATION/PERSON_GENERALIZATION_REJECTED | S1_IN_SCOPE_MECHANICAL (再導出:one's blood went cold) | key_phrase("one's blood go cold")がdisplay_phraseと一致せず、source_span('my blood went cold')内の連続部分文字列でもない(人称代名詞・所有格 |
| preHR | Z | family_z_production_e2e_01/the_tell_tale_heart/run_p1_evidence_03 | b1b | canonicalization | `my blood went cold` | RULE7_NORMALIZATION/PERSON_GENERALIZATION_REJECTED | S1_IN_SCOPE_MECHANICAL (再導出:one's blood went cold) | key_phrase("one's blood go cold")がdisplay_phraseと一致せず、source_span('my blood went cold')内の連続部分文字列でもない(人称代名詞・所有格 |
| preHR | Z | family_z_production_e2e_01/the_tell_tale_heart/run_p2_evidence_r3 | b1b | canonicalization | `my blood went cold` | RULE7_NORMALIZATION/PERSON_GENERALIZATION_REJECTED | S1_IN_SCOPE_MECHANICAL (再導出:one's blood went cold) | key_phrase("one's blood go cold")がdisplay_phraseと一致せず、source_span('my blood went cold')内の連続部分文字列でもない(人称代名詞・所有格 |
| preHR | Z | family_z_production_e2e_01/the_tell_tale_heart/run_p2_evidence_r4 | b1b | canonicalization | `my blood went cold` | RULE7_NORMALIZATION/PERSON_GENERALIZATION_REJECTED | S1_IN_SCOPE_MECHANICAL (再導出:one's blood went cold) | key_phrase("one's blood go cold")がdisplay_phraseと一致せず、source_span('my blood went cold')内の連続部分文字列でもない(人称代名詞・所有格 |
| preHR | Z | family_z_production_e2e_01/the_tell_tale_heart/run_sf_prod_01 | a2 | canonicalization | `froze my blood` | RULE7_NORMALIZATION/PERSON_GENERALIZATION_REJECTED | S1_IN_SCOPE_MECHANICAL (再導出:froze one's blood) | key_phrase("freeze someone's blood")がdisplay_phraseと一致せず、source_span('froze my blood')内の連続部分文字列でもない(人称代名詞・所有格の |
| preHR | Z | family_z_production_e2e_01/the_tell_tale_heart/run_sf_prod_01 | b1b | canonicalization | `eased open` | RULE7_NORMALIZATION/LEMMA_1TO1_REJECTED | S1_IN_SCOPE_MECHANICAL (表層形revert) | key_phrase('ease open')がdisplay_phraseと一致せず、source_span('eased open')内の連続部分文字列でもない(人称代名詞・所有格の一般化[閉じた語彙集合による1対1 |
| preHR | Z | family_z_production_e2e_01/the_tell_tale_heart/run_sf_prod_02 | b1b | canonicalization | `my blood went cold` | RULE7_NORMALIZATION/PERSON_GENERALIZATION_REJECTED | S1_IN_SCOPE_MECHANICAL (再導出:one's blood went cold) | key_phrase("one's blood go cold")がdisplay_phraseと一致せず、source_span('my blood went cold')内の連続部分文字列でもない(人称代名詞・所有格 |
| preHR | Z | outer_retry/attempt_1/canonicalization_runtime_metadata.json | a2 | canonicalization | `froze my blood` | RULE7_NORMALIZATION/PERSON_GENERALIZATION_REJECTED | S1_IN_SCOPE_MECHANICAL (再導出:froze one's blood) | key_phrase("freeze someone's blood")がdisplay_phraseと一致せず、source_span('froze my blood')内の連続部分文字列でもない(人称代名詞・所有格の |
| preHR | Z | outer_retry/attempt_1/canonicalization_runtime_metadata.json | a2 | canonicalization | `sure of myself` | RULE7_NORMALIZATION/PERSON_GENERALIZATION_REJECTED | NOW_PASS | key_phrase('sure of oneself')がdisplay_phraseと一致せず、source_span('sure of myself')内の連続部分文字列でもない(人称代名詞・所有格の一般化[閉じた |
| preHR | Z | outer_retry/attempt_2/canonicalization_runtime_metadata.json | a2 | canonicalization | `My ears began ringing` | RULE7_NORMALIZATION/PERSON_GENERALIZATION_REJECTED | S1_IN_SCOPE_MECHANICAL (再導出:one's ears began ringing) | key_phrase("one's ears begin ringing")がdisplay_phraseと一致せず、source_span('My ears began ringing')内の連続部分文字列でもない(人 |
| preHR | Z | outer_retry/attempt_2/canonicalization_runtime_metadata.json | ? | canonicalization | `froze my blood` | RULE7_NORMALIZATION/PERSON_GENERALIZATION_REJECTED | S1_IN_SCOPE_MECHANICAL (再導出:froze one's blood) | key_phrase("freeze someone's blood")がdisplay_phraseと一致せず、source_span('froze my blood')内の連続部分文字列でもない(人称代名詞・所有格の |
| preHR | Z | outer_retry/attempt_2/canonicalization_runtime_metadata.json | ? | canonicalization | `leaving no mark` | RULE7_NORMALIZATION/LEMMA_1TO1_REJECTED | S1_IN_SCOPE_MECHANICAL (表層形revert(基本形化は閉表/guard拡張[新規則]で可: leave no mark)) | key_phrase('leave no mark')がdisplay_phraseと一致せず、source_span('leaving no mark')内の連続部分文字列でもない(人称代名詞・所有格の一般化[閉じた語 |
| preHR | Z | outer_retry/attempt_2/canonicalization_runtime_metadata.json | ? | canonicalization | `My ears began ringing` | RULE7_NORMALIZATION/PERSON_GENERALIZATION_REJECTED | S1_IN_SCOPE_MECHANICAL (再導出:one's ears began ringing) | key_phrase("one's ears begin ringing")がdisplay_phraseと一致せず、source_span('My ears began ringing')内の連続部分文字列でもない(人 |
