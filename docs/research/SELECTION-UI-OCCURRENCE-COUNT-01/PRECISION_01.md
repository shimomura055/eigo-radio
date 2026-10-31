# PRECISION_01 — 出現回数集計 occ-v1 の既存データでの精度検証(API 0)

管理ID: SELECTION-UI-OCCURRENCE-COUNT-01 / OPEN-632 / 委任_01。集計規則は `DESIGN_01.md` §2、試作は `tools/occurrence_count_01.py`。
全ヒット(人手確認可能な一覧)は `evidence/` に出力済み。**API費用0円・既存run dir/data JSONの読み取りのみ・Production無変更**。

## 1. 再現コマンド(リポジトリroot、`.venv\Scripts\python.exe`)

```
T=docs/research/SELECTION-UI-OCCURRENCE-COUNT-01/tools ; EV=docs/research/SELECTION-UI-OCCURRENCE-COUNT-01/evidence
py $T/run_precision_01.py     --root . --extra-root <main tree> --out $EV   # 全member全ヒット(hits_all.tsv)・項目別件数(counts.tsv)・不変条件(invariants.json)
py $T/oracle_nearmiss_01.py   --root . --extra-root <main tree> --out $EV   # 取りこぼし監査(緩い基準, nearmiss.tsv)
py $T/crosscheck_enduser_01.py --root . --extra-root <main tree> --out $EV  # 公開済みenduser pageとの突合
py $T/run_wide_scan_01.py     --root . --extra-root <main tree> --out $EV   # 全候補doc(126件)の非exactヒット全件
py $T/pos_audit_01.py         --evidence $EV                                # 品詞割れ(NLTK=評価専用)
py $T/run_user5_cases_01.py   --root . --extra-root <main tree> --out $EV   # ユーザー指定5表現
py -m unittest $T/occurrence_count_01_test_01.py                            # 単体test 30件
```
`<main tree>` = `C:\Users\tensh\eigo-radio`(Git未追跡のrun dir〔ai_island/uk_train/melos/redelivery_fee等〕の読み取り専用参照。無変更)。

## 2. 対象データ

| 項目 | 値 |
|---|---|
| member data JSON | `user_test/selection_form_v3/data/*__*prod.json` 27件(batch `twotier-a/b`・`sub04-a/b/c` のmember全種+追加) |
| 項目数 | 261(Phrase 138 / Word 123)。うち本文が読めず集計不能 8(`monkeys_paw__b1b`=replay経路でrun dirなし)。**評価対象253項目** |
| Family x 水準 | X: a2 66 / b1b 78、Y: a2 19 / b1b 22、Z: a2 31 / b1b 45(項目数)。**X/Y/Z x Standard/Advanced の6水準全てを含む** |
| 区分の取得 | 全区分取得 218 / Comment・Preview未取得 35(redelivery_fee・melos=KP-only evidence run) / 全未取得 8 |
| 広域走査 | 全候補doc 126件(X/Y/Z・過去run含む)・955項目(非exactヒットの全件確認用) |
| 公開ページ照合 | 公開済みenduser page 10ディレクトリ x 2水準 = 20ページ・195項目 |

## 3. 結果(数値)

### 3-1. ヒット総数(253項目)
| | 件数 |
|---|---|
| 確定ヒット | **335**(exact 328 / lemma(活用形) 7) |
| 判定保留(加算しない) | **3**(revlemma 3: `veil`(←veiled)、`bother`・`bothers`(←bothered)) |
| 区分別(確定335) | Story 296 / In One Line 26 / Comment 7 / Preview 3 / Title 3 |
| 項目別の合計回数 | 0回 2項目(いずれもtitleのみ) / 1回 212 / 2回 21 / 3回 8 / 4回 5 / 5回 2 / 6回 1 / 7回 1 / 11回 1 |
| 2区分以上に出る項目 | 17項目 |

実用上の意味: 84%(212項目)は「1回」(その候補の選定元の出現のみ)。回数が情報になるのは複数回出る39項目(15%)で、ここの正確さが信頼性の中心(下記の全件確認はこの39項目+保留・活用形を含む41項目を対象にした)。

### 3-2. 誤カウント(FP)の監査
| 監査 | 方法 | 結果 |
|---|---|---|
| 非exactの確定ヒット全件 | 7件を文脈つきで全件確認 | **誤り 0**(`supplements`×3、`charging`×3〔`charge`〕、`shrieked`〔`shriek`〕=同一語の活用形) |
| 複数回出現する項目の全ヒット | 41項目・126ヒット(確定123)を文脈で全件確認 | **誤り 0**(同一語・同一用法) |
| 単独ヒット項目(212) | 各項目のヒット=その候補が選定された本文の1箇所。`item.occurrence_count`(選定時にer105が本文一致を保証)との不変条件で担保 | 下記 3-4 |
| 品詞が割れた項目(同綴の別用法リスク) | NLTK perceptron品詞で全確定ヒットを推定し、同一項目内で品詞が割れた8項目を人手確認 | 7項目はタガー誤り(`sponsored`のJ/N揺れ等で同一用法)、1項目が実際の品詞違い(`shriek`名詞/`shrieked`動詞=同一語彙素)。**別意味の混同は0** |
| 判定保留で加算を止めたもの | `veil`(←`veiled`、形容詞->名詞)は誤加算になるところを保留で阻止。`bother/bothers`(←`bothered`)は正しい出現だが保留 | 保留3件のうち誤加算阻止1・取りこぼし2(下記) |

広域走査(955項目・ヒット1,107 exact + 非exact確定17 + 保留9): 非exact確定17件(`supplements`・`charging`・`shrieked`・`hold their son back`〔`hold someone's/one's son back`のスロット〕)を全件確認 -> 誤り 0。保留9は同じ`veil`/`bother`系の重複(複数runに同一本文)。

### 3-3. 取りこぼし(FN)の監査
緩い基準のoracle(`oracle_nearmiss_01.py`: 各項目の内容語の語幹が全て同一文に在るのに集計がヒットしない箇所を列挙)の**45行を人手で分類**:

| 分類(`nearmiss.tsv` の `judgement` 列) | 行数 | 内訳 |
|---|---|---|
| TN_unrelated: 語幹の偶然一致/別の語 | 28 | `constable`~`consider`、`call on`~`called "the Cathedral"`、`carry over`~`carried into`、`way off`~`way of dressing`、`bothered`~`both families`、`hard on someone`~`hard time`、`thankful`~`harder` 等 |
| TN_derivational: 派生語(別見出し語) | 9 | `persuade`<->`persuasion`(4)、`investigation`<->`investigate`(2)、`shrinkage`<->`shrinking`(3) |
| TN_different_structure: 語順/構文が異なる別表現 | 7 | `what it helps with` <-> `What does having it there help with?`(5)、`hear it out` <-> `we've heard that…`/`hear the closing summary`(2) |
| BORDERLINE_insertion: 語の挿入 | **1** | `make life work` <-> `make daily life work`(語が挿入された別形として加算しない) |
| **確定すべきなのに落ちた(FN)** | **0** | |
| 計 | 45 | |

保留に回した真の出現は2件(`bother me`/`bothers me`)。確定集合に入れるか保留のままにするかはDESIGN §8-3,4のレビュー論点。

### 3-4. 不変条件: 本集計の「選定表層と一致する件数」 = 旧 `item.occurrence_count`(er105)
- 比較対象253項目(X: Story+In One Line+Title の完全一致〔`article.md` は末尾に In One Line を含む〕、Y/Z: Story+Title)。
- **251/253一致**。不一致2件は同一の `surname_choice` の `adopted`(旧記録4 / 現本文3): 旧記録は `occurrence_sentence_ids=[S2,S5,S7,S38]` を持つが現本文のS5には `adopted` が無い -> **KP生成後に本文(intro patch: `_backup_apply_v1_intro_patch_01`)が変わった実例**。回数を選定時点の現本文で再計算する設計(DESIGN §3)の根拠。
- 別途: `campaign` が `campaign's` を数える規約は、この不変条件で発見して修正(初回は4->3の不一致だった)。

### 3-5. 公開済みenduser pageとの突合(run dirの本文 vs 実際に公開されている表示本文)
- 20ページ・195項目。**Story と In One Line の回数は195/195一致**。Comment/Preview まで含め全区分一致が160項目、残る35項目は差が「run dirにPreview/Commentが無い(KP-only evidence run=redelivery_fee 18項目 + melos 17項目)ため未取得、公開ページは0」というだけで、実質の差ではない。
- Local Rewrite(LR)等による表示本文の書換えで回数がずれた項目は、この195項目には0。

## 4. ユーザー指定5表現の実本文での確認(`family_x_untidiness_family_resource_01`)

選定候補ではない表現だが、分離形・活用形・同形(`in a way`)を含む実例として集計。**本文を人手でgrepして数えた正解と全件一致**(確定ヒット Advanced 18 + Standard 13 = 31件、FP 0 / FN 0)。

| 表現 | 水準 | Story | Comment | Preview | In One Line | 合計 | 保留(Title) | 数えた形 |
|---|---|---|---|---|---|---|---|---|
| put away | Advanced | 4 | 1 | 0 | 1 | **6** | | put away x3, put it away, put that away, putting something away |
| put away | Standard | 5 | 0 | 0 | 1 | **6** | | put it away x3, put away, put that away, putting something away |
| in the way | Adv / Std | 1 / 1 | 0 | 0 | 0 | **1 / 1** | | in the way(`in a way`・`different way` は数えない=否定の実例) |
| force away | Advanced | 1 | 0 | 0 | 0 | **1** | | force it away |
| force away | Standard | 0 | 0 | 0 | 0 | **0** | | (本文は `make the person put it away`) |
| leave out | Advanced | 3 | 1 | 1 | 0 | **5** | 1 | left out x4, leave it out |
| leave out | Standard | 3 | 0 | 0 | 0 | **3** | 1 | left out x2, leave it out |
| in sight | Advanced | 3 | 1 | 0 | 1 | **5** | | in sight x5 |
| in sight | Standard | 1 | 0 | 0 | 2 | **3** | | in sight x3 |

保留(Title): `The Trial of “Leaving Things Out” Is Now in Session` の `Leaving Things Out`(句動詞の間に名詞句)。Titleは合計に含めず、保留にも計上しない設計のため合計は変わらない。Standardの Preview/Comment は日本語本文なので0。
`in the way` の Advanced Story の1件は「邪魔」の意味で、ユーザー原文が意図する用法そのもの(同じ綴りで別意味の出現は、このデータには無い)。

## 5. 単体test(誤カウント防止、受入条件5)
`tools/occurrence_count_01_test_01.py` **30件PASS**(`evidence/unittest_output.txt`): 部分文字列(`within the wayside`/`insight`/`input away`/`put-away`/`putaway`)、ハイフン語、`in a way`/`by the way`、大小文字、句読点・改行・文境界・em dashの非跨ぎ、所有格`'s`、活用(規則/不規則/複数)、分詞形容詞の逆引き禁止(puzzling)、`news`->`new`禁止、逆引きの保留、代名詞の間=確定・名詞句の間=保留・前置詞型=保留・4語離れ=不成立、人称スロット(閉集合)、名詞句スロット=保留、N5形(`hear someone out`<-`hear it out`)の下限保証、`a/an`<->`this/that`可・`the`不可、区分別・title除外・未取得の区別、日本語本文=0、決定性。

## 6. 例外・判定不能の実影響(明示)

| ケース | 実データでの件数 | 実影響 |
|---|---|---|
| 同綴の多義(`in the way`の「様子」等) | 確認できた誤カウント 0(253項目) | 理論上は残る。注記常設+`forms`確認で対応。判別機構は作らない |
| 品詞違いの同綴(`bar`名詞/動詞等) | 品詞割れ1項目(`shriek`、同一語彙素) | 〃 |
| 判定保留(加算しない) | 3ヒット(広域走査で9、全て同じ2語) | 合計から除外、`＋判定保留N`で併記 |
| 派生語(persuade/persuasion等) | 9行 | 別見出し語として数えない(仕様) |
| 語の挿入(`make daily life work`) | 1 | 数えない(境界) |
| 本文が取得できない区分 | 4 memberの一部 | 0にせず「未集計」と明示 |
| 選定後に本文が変わる | 旧記録との不一致2(`adopted`) | 選定時点の現本文で計数。差は再計算で検出可能 |

## 7. 限界(この検証でカバーしていないこと)
- 既存runはN5(2026-10-30配線)以前で、候補docに `n5_generalization` が0件。N5形は単体test(スロット/下限保証)でのみ検証。委任_02の最初にN5配線後の新規runで再実測する。
- 分離句動詞(`sep_*`)・名詞句スロットは、既存253項目の実本文では自然発生0件(ユーザー指定5表現と単体testで検証)。
- 公開URL上のPC/スマホ実操作は本委任の範囲外(実装後)。

## 8. 追記(委任_02、2026-10-31): oracleの限界と正式module(er140)での再検証
- **oracleの限界(Opus推奨)**: §3-3 の「取りこぼし0」は、緩い基準oracle(内容語の語幹が全て同一文に在るのにヒットしない箇所)が**見つけた範囲で**0という意味。oracleは語幹の先頭4字一致で作った基準のため、(1)不規則活用(語幹が変わる `go→went`、`leave→left` 等は語幹先頭4字が一致せず拾えない)、(2)先頭の be/have/do の活用形(`was in the way` ← `be in the way`。委任_01時点では確定集合にも無く、oracleの語幹基準でも内容語が `way` だけになり判定できない)は、そもそも検出できない。この2系統は単体testで直接検証する(`er140_selection_occurrence_count_01_test_02.py` M3・Er105Snapshot)。M3(先頭be/have/do)はこの限界のため実データでは0件の差になる。
- **正式module(er140_*)での再実測**(`tools/run_precision_02.py`、同一27 member・253項目・API 0): 確定335 / 保留3 / 誤カウント0 / 取りこぼし0(nearmiss 45行は委任_01と同一集合=人手分類を引き継ぎ、境界1) / 旧`occurrence_count`との不変条件251/253(不一致2=`surname_choice` adopted、既知)。**委任_01との差分(`evidence_02/diff_vs_01.tsv`)は0行**。理由: M1(除外表)・M2(前置詞兼用の不変化詞)・M3(be/have/do)・縮約's・sb/sth・人名スロット・S/U和集合は、既存253項目の実本文では自然発生しない(委任_01の§7「sep/slot系は自然発生0件」と同じ構造)。新規則の効きは単体test(64件)と、ユーザー指定5表現+単語 `leave` の実本文集計(`occ_userfive` member、`EVIDENCE_01.md`)で確認する。
- **loaderの単位(Opus推奨「段落内改行の潰し」)**: 試作の `_paras`(`" ".join(p.split())`)は段落内の改行を空白に潰し、Yの見出し・話者ラベル行(`First to speak is ...` の次行)と本文1行目を連結していた。実データ(Y translate 40ファイル=240段落のうち120が複数行、Z writer r2.md/std.md 152ファイル=4,282段落は複数行0、X parts 1,733段落のうち9が複数行)で、複数行段落の全行が文末記号で終わることを確認(行途中の折り返し本文は0)。正式loaderは **1行=1 unit**(改行をまたぐ一致は規則どおり不成立)にした。件数は不変(上記diff 0行)。
- **N5形(§7)**: 現行run dir(er019/er121/er026)の候補docに `n5_generalization` を持つものは0件のまま(grep確認)。N5形は単体test(`N5GeneralizedForms`・`UnionOfGeneralizedAndSurface`)で検証済み。N5配線後の新規runが出た時点でexport時の自己検査(`occurrence_selfcheck_mismatch`警告)が実表現の完全一致を候補docの値と突合するため、運用で検出できる。
