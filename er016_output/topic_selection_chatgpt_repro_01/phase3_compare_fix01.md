# Phase 3 FIX-01: Reference比較(訂正後、スクリプト出力+Sonnet事実記述、主観評価なし)

本ファイルはFIX-01(Step D検証ルールから`url_in_citations`条件を削除し、
Step Eを再実行した結果)に対する比較である。Step A〜C(探索・選定・Hook
生成)は初回と完全に同一(`stepA_1〜8.json`/`stepB_selected.json`/
`stepC_hooks.json`は無変更)。自動計算部分は`phase3_compare_fix01.json`
を参照。初回(8件)版との比較は各節末尾に1段落で付記する。

## 0. Reference非混入検査(contamination_check)

`prompts/`配下のPhase 2該当ファイル(stepA_1〜8, stepB_select, stepC_hooks,
stepE_final, stepE_final_fix01)を機械走査した結果、キーワードヒットが
3件あった(`ローソン`→stepB_select.json、`米中首脳会談`→stepE_final.json、
`米中首脳会談`→stepE_final_fix01.json)。

**手動確認の結果、いずれもReference本文の注入によるものではない**:
- `ローソン`ヒット・`米中首脳会談`ヒット(stepE_final.json分): 初回
  phase3_compare.md 0節と同一の説明(C057・C027はLunaが独立発見した
  実在候補)。
- `米中首脳会談`ヒット(stepE_final_fix01.json分): FIX-01のStep E入力
  (Step D fix01通過35件の候補リスト)にC027が含まれていたため
  (`prompts/stepE_final_fix01.json`はStep Eへの入力全体を保存する仕様)。
  C027自体はStep A(検索)段階でLunaが独立発見した候補であり、Reference
  本文からの注入ではない(C027はEuronews記事"The Trump-Xi summit: Why
  Europe has so much at stake"の実urlを持つ実在候補)。なお、C027は
  Step D fix01は通過したが、Step E fix01の**最終20件には選ばれなかった**
  (Lunaの判断、下記1節参照)。

**結論: 注入によるcontaminationは無し(初回と同じ結論)。**

## 1. Luna最終20件(FIX-01) × Reference20件: Topic重複表(Sonnet手動判定)

| Luna final candidate(FIX-01) | Reference # | 判定 | 根拠(1語) |
|---|---|---|---|
| C023(国連総会、Trump/Guterres対立) | #2(AI企業トップが国連安保理でAI議論) | 類似話題 | AI・国連(但し具体的な会議体・登壇者が異なる: C023はUN総会文脈でのTrump/Guterresの対立、Reference#2はUN安保理でのAltman/Amodei氏の説明という異なるイベント。初回と同一判定) |
| C004(台風後の水害拡大) | なし | 無関係 | — |
| C020(AIチャットボットと制裁対象メディア) | なし | 無関係 | — |
| C047(香り付き清掃製品・ナノ粒子) | なし | 無関係 | — |
| C009(夜行新幹線) | なし | 無関係 | — |
| C033(脳細胞遺伝子解析) | なし | 無関係 | — |
| C081(久米の五枝のマツ) | なし | 無関係 | — |
| C097(セガ・ソニック映画) | なし | 無関係 | — |
| C018(トルコ投資ファンド不正) | なし | 無関係 | — |
| C028(原油価格・米イラン協議) | なし | 無関係 | — |
| C035(光原子時計) | なし | 無関係 | — |
| C032(MIT昆虫サイズ飛行ロボット) | なし | 無関係 | — |
| C073(富士山頂17年間) | なし | 無関係 | — |
| C013(エミュー逃走) | なし | 無関係 | — |
| C014(J:COM通信障害) | なし | 無関係 | — |
| C044(ショウガと片頭痛) | なし | 無関係 | — |
| C034(地球の自転速度) | なし | 無関係 | — |
| C083(うるま市体育館AI) | なし | 無関係 | — |
| C007(高市連立) | なし | 無関係 | — |
| C019(EUカラス氏・ホルムズ海峡) | なし | 無関係 | — |

**重複件数: 同一話題0件、類似話題1件(#2)、無関係19件。**

**初回(8件)版との差**: 初回はC027(米中首脳会談)が最終選定に残り
Reference#3と「同一話題」に分類されたが、FIX-01ではStep D通過候補が
9件→35件に増えたことでLunaの選択肢が広がり、C027はStep Eで**選ばれ
なかった**(dedupe_group上の重複制約は無く、Lunaが多様性を優先して
他の20件を選んだ結果)。結果として、Reference20件との重複は初回の
「同一1件+類似1件」から「同一0件+類似1件」に減少した。

## 2. Step A生プール(114件)内包含チェック

Step A〜Cは無変更のため`candidates_raw.json`(114件)は初回と同一であり、
自動ヒューリスティックの結果(`step_a_pool_inclusion_heuristic`)も
初回と同一(信頼性が低いことも初回同様。手動キーワード照合の結果も
初回phase3_compare.md 2節と同じ: Reference20件中、文字列レベルで
確認できた同一話題はReference#3(Trump-Xi summit、C027)の1件のみ)。
**FIX-01でもこの母集団(114件)自体は変わっていない**ため、この節の
結論は初回から変化なし。

## 3. Hook形式判定(`classify_hook_format`ルール適用結果)

- Luna最終20件(FIX-01): 0/20が`question_ification`、20/20が
  `reinterpretation`
- Reference20件: 20/20が`reinterpretation`(初回と同一)
- Phase 4(b)(d)固定入力比較: 20/20が`reinterpretation`(初回のまま、
  再実行なし)

**初回(8件)版との差: 分類結果に変化なし(8/8→20/20とも全件
reinterpretation)。** 判定ルールの限界(「でしょうか」終止で両者を
判別できない)も初回と同じ。

## 4. 分布比較

- Lunaカテゴリ分布(最終20件): AI/Tech4, Hard News3, Science3, Health2,
  Lifestyle2, Business/Economy2, Environment1, Entertainment1, Other1,
  Consumer1
- Luna日本人距離分布(最終20件): 近い8, 中4, 遠い8
- Luna俗っぽさ件数(category∈{Consumer,Entertainment,Other}または
  summary_jaに「コンビニ/SNS/話題/商品/グッズ」を含む): 3/20
- Reference俗っぽさ件数(type_tagsに「俗/SNS/コンビニ」を含む): 4/20
  (初回と同一、Reference側は不変)
- Reference距離ラベル・source媒体情報: 無し(初回と同じ理由で比較不可)

**初回(8件)版との差**: 初回はLuna最終8件が全件AI/Tech・Business/
Economy・Hard News(sublane 2・3由来)に偏っていたが、FIX-01では
sublane 1(国内一般)・3(AI/Tech/Science)・4(健康)・6(ライフスタイル)・
7(エンタメ)由来の候補も選ばれ、カテゴリが10種類に分散した。俗っぽさ
件数も0/8→3/20(比率でも上昇)へ改善した。**これはStep Dの
url_in_citations機械除外がsublane 2・3以外の候補を排除していたことの
直接的な帰結であり、除外ルール撤回によりStep Eが元々の多様な母集団
(35件、8サブレーン中複数由来)から選定できるようになったことを示す。**

## 5. url_in_citations記録(参考、失格には使用せず)

Step D fix01では`url_in_citations`の値は`stepD_verify_fix01.json`の
各resultに引き続き記録されているが、失格理由には一切使用していない
(コード上`apply_citation_rule=False`により`url_not_in_citations`理由は
一度も追加されない)。`raw_responses/stepA_<n>.json`のsources件数
(sublane別: 1=0件,2=14件,3=13件,4=0件,5=0件,6=0件,7=0件,8=0件)は
初回と同じ(Step Aを再実行していないため)。
