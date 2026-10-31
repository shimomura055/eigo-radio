# JA-GLOSS-QUALITY-ALARM-TRIAL-01 検証セット (EVAL_SET_01)

管理ID=JA-GLOSS-QUALITY-ALARM-TRIAL-01 / OPEN-636 / 委任_01 / 2026-10-31。API 0(決定論構築)。
生成: `tools/build_eval_set_01.py` → `eval_set/{items.json, articles.json, summary.json, ITEM_LIST.md}`。再生成は決定論(入力はgit管理下のファイルのみ)。
**個別辞書・特定語の例外ルールは設計に入れない。** 本セットは評価データであり、検査機構の入力には「表現/訳/英文/前後文/記事全文/level」だけを使う。

## 1. 件数(目標との対比)

| 層 | ラベル | dev | held-out | 計 | 目標 |
|---|---|---|---|---|---|
| T1 ユーザー指摘/HR修正した訳 | 問題(確定) | 4 | 4 | **8** | T1>=8 ✓ |
| T3 合成の重大誤訳 | 問題(確定) | 12 | 10 | **22** | (合成件数を明示) |
| T2 HR承認済み・修正なし | 正常(推定) | 38 | 33 | **71** | 正常>=60 ✓ |
| T4 判断が割れうる訳 | **ラベル保留(Fable裁定欄)** | 7 | 7 | **14** | - |
| 合計 | | 61 | 54 | **115** | |

- 問題=T1+T3=**30**件(目標>=25 ✓)、正常=71件(>=60 ✓)。
- held-out=54/115=**47%**(>=40% ✓)。分割は**記事単位**(同じ記事・同じ文脈がdevとheld-outに跨らない)。held-out記事=X: jwst_mystery_emission_line・moon_shrinking_reselect、Y: surname_choice、Z: yuki_onna。dev記事=X: ai_chat_sponsored・meta_waddle・untidiness、Y: redelivery_fee、Z: in_a_grove・melos。X/Y/Zともdev・held-outの両方を含む。
- Family/level内訳(T1|T2|T3|T4): X Std 4|18|6|6、X Adv 4|17|6|6、Y Std 0|5|1|0、Y Adv 0|10|3|0、Z Std 0|9|2|0、Z Adv 0|12|4|2(summary.json by_tier_family_level)。

## 2. ラベルの出典(層別)

### T1 ユーザーが指摘・修正した訳(問題確定、8件)
| id | 表現→現訳 | 出典 | 重大度(案) | split |
|---|---|---|---|---|
| JAQ-T1-045 | verdict→結論(Adv) | ユーザー原文§3 / OPEN-630(本文は裁判の比喩、適切な訳は評決) | major | dev |
| JAQ-T1-039 | verdict→結論(Std) | 同上(同じ記事・同じ文のStandard側) | major | dev |
| JAQ-T1-114 | things left out→省かれたもの | ユーザー原文§3 / OPEN-631 J4。修正前の訳は FX-UNTIDINESS-COMMENT4-JA-GLOSS-FIX-01/ev01/retranslate/old_entry.json。本文は『出しっぱなしのもの』 | major | dev |
| JAQ-T1-106 | charge→非難(Std) | ユーザー原文§3(裁判のたとえ。罪状/容疑の含み) | major | dev |
| JAQ-T1-035 | culprit→原因(Adv) | ユーザー原文§3 | minor | held-out |
| JAQ-T1-107 | radius→中心から外側までの長さ(Adv) | ユーザー原文§3(定訳『半径』の定義文化) | minor | held-out |
| JAQ-T1-108 | equivalent width→光の線の特徴を表す幅 | **HR修正記録**(confirmed_selection.json history gloss_before→『等価幅』、2026-10-30) | minor | held-out |
| JAQ-T1-109 | equivalent width→スペクトル線の強さを示す等価幅 | 同上(修正前の別版) | minor | held-out |

- 実質的には**6種類の表現**(equivalent widthは同一表現の修正前2版)。T1の「ユーザー修正の記録」が残っているのはequivalent widthのみで、他はユーザーが原文・OPENで指摘した例(会話上の指摘)。HR記録からの追加探索(er*_output/**/confirmed_selection.json の gloss_before)では他に1件も見つからなかった(探索結果はこの1表現のみ)。**T1がこれ以上増えない=実ユーザー指摘データの量的限界**であり、T3(合成)で補う。
- 偏り: T1はすべてFamily X。Y/Zにはユーザー指摘の例が記録上ない(限界として報告)。
- 重大度は本agentの案。severityの正解は評価の主指標でなく、major/minorの区別は参考(重大誤訳検出の集計用)。

### T2 HR承認済み・修正なし(正常・推定、71件)
公開済み10記事・18 level の学習項目84件(JA-GLOSS-NUANCE-01 data/published_glosses_01.json、origin/main user_test/*/enduser/data/article.json)から、T1(3件: verdict2・culprit)とT4(10件)を除いた71件。公開ページ=ユーザーのHR承認を経ている。**「正常」は推定**(誤りがあってもユーザーが気づかなかった可能性)。警告が出たT2項目は、評価時にFable(またはユーザー)がブラインド裁定し、『警告が妥当(=実は問題)』なら問題へ、そうでなければ誤警告として記録する(TRIAL_PLAN_01.md §5)。裁定でラベルを変えた記録は残し、閾値の調整には使わない。

### T3 合成の重大誤訳(問題確定、22件)
T2の承認済み正常訳を、**意味の異なる訳へ人手で置換**したもの(tools/build_eval_set_01.py の T3_SPECS)。反意(助言を受け入れる→助言を無視する)、別義(medium 霊媒師→中くらいの大きさ)、別概念(prosecutor 検察官→弁護士)、状態の反転(widowed 配偶者を亡くした→離婚した)など。**ペア設計**: 置換元の正常訳も T2 に残している(同じ文脈で正常/誤訳の対が存在)。T3は検出が易しいので、Precision/Recallは必ず「T3を含む集計」と「T3を除く(実データのみ)集計」を別々に報告する。dev12・held-out10(置換元の記事のsplitに従う)。
置換の偏り: 反意・別義が中心で、「軽い言い換えで意味が変わる」型は少ない(その型はT1/T4で見る)。

### T4 判断が割れうる訳(ラベル保留、14件)
agent(本調査者)が事前所見を付けた境界例(complications→複雑な要素、frustrate→いら立たせる[探偵のたとえ]、porous、puzzling、exception、shepherd、insulation、campaign、errand[記録に文脈なしで3件脱落]など)。事前所見は **ラベルではない**。**Fable裁定欄**(eval_set/items.json の `fable_ruling` を委任_02で追加。値=problem/normal/exclude)を埋めるまで、PrecisionにもRecallにも**含めない**。警告の有無は参考表示(T4の警告率)として報告する。

## 3. 各項目のフィールド(eval_set/items.json)
`id, tier, split, label, severity, expression, current_ja, sentence_en, context_before(前2文), context_after(後2文), article_key, level, family, existing_explanation_ja(公開項目のみ), existing_sentence_ja, source, note, synthetic_of, sentence_found_in_article, item_kind`。記事全文は `articles.json[article_key][std|adv]`(英語のみ、115件で参照)。文の位置検索はsentence_found_in_article=全件True。
注意: 記録由来の項目(T1 charge/radius/equivalent width、T4の一部)の記事全文は gloss_alignment_prompt.txt の【記事本文(参考)】(生成時に実際に渡した入力と同一)。

## 4. 限界(正確に報告するため)
1. 正常71件は『HR承認済みで修正されなかった』という推定。
2. 実ユーザー指摘(T1)は8件・6表現・すべてX。Precisionの信頼区間は広い(例: 実データのみで警告TP=6/FP=1ならWilson 95% 0.49〜0.97程度)。→TRIAL_PLAN_01.md §4で区間つきで報告する。
3. 合成T3は検出が易しく、Recallの上振れ要因。
4. 公開済み記事の学習項目はKP/vocab 5件×levelで、候補12件全体(提示される非選定候補)を含まない。HR現場の入力(候補12件/level)の分布とは完全には一致しない。→委任_02で、記録(newgen_records_all_01.json、449件)から候補由来の追加正常項目(文脈つき)を加えるかをFableが判断できる(費用0)。
5. T1の語(verdict/culprit/charge/radius/things left out)は、ユーザー原文の代表例であり、devで検査方式を調整するときに「個別に当てにいく」ことを避ける。**これらを個別辞書・例外ルール・Promptの例示語にしない。** Promptには特定の語や訳語を一切書かない(DESIGN_OPTIONS_01.md §0)。

## 5. 項目一覧
eval_set/ITEM_LIST.md(自動生成。T1/T3/T4/T2の全115件)。

## 6. 検査バッチ(eval_set/batches.json、41バッチ)と運用プール
- **同じ表現を1バッチに2回入れない**(T3の誤訳版と置換元の正常訳、equivalent widthの2版が同居すると、検査者が両者を見比べて有利になるため)。view A=T3以外の全項目(正常・T1・T4の採点はAのみ)、view B=T3+T1の2版目+置換元でない正常項目(filler、Bでは採点しない)。dev 22バッチ(A13+B9)・held-out 19バッチ(A10+B9)。送信項目はdev 83・held-out 77(filler含む)。
- **有病率の問題**: 本セットは問題30/115=約26%で、実運用(推定3〜10%、未確定)より高い。ラベル付きセットのPrecisionだけでは運用での『的中率』を過大評価する。→ TRIAL_PLAN_01.md §2-1。
- **運用プール(未ラベル)**: `user_test/selection_form_v3/data/*__prod.json` 27ファイル・261候補(X144・Y41・Z76)=実際にHRへ出た12候補/level。検査して**警告が出た項目だけをブラインド裁定**し、実際の有病率でのPrecisionを測る(委任_02。費用約¥3.9)。このプールの記事本文は gloss_alignment_prompt.txt と公開article.jsonから取得できる(取得可否は項目ごとに委任_02の冒頭で確認)。
