# FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-02 REPORT

## 1. 管理ID・性質

FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-02(ユーザー承認済みTrial、Trialのみ)。
Production code・正式Prompt・CURRENT_SPEC・routingは一切変更していない
(§14で機械的に確認)。到達Status候補は本REPORT末尾§12を参照(Sonnetは
`VALIDATED`を自己宣言しない)。

## 2. 目的・スコープ

Trial-01(`er037`)で観測した「Hormuz AN(A3+N2)で固有名詞がJA 9件->EN
19件に増える」現象の実体調査(read-only)と、Hormuz/Meta 2記事について
日本語Writer側 AN3(A3+N2)/AN2(A2+N2) × 英語化側 T0(現行)/T1(Trial限定
の抑制追記)の2×2 Matrix(+各記事Baseline=A0+T0)を比較し、「数字・固有
名詞を減らしながら記事内容・因果関係・面白さを維持できる組み合わせ」を
探した。詳細設計は`docs/pm/design_family_xy_concreteness_control_trial_02.md`。

## 3. 固有名詞9→19の原因(6項目回答の要約、詳細は設計書§2)

1. JA未存在の固有名詞の新規出現: 「Donald」(Trump氏のfirst name)のみ、
   人物としては既存参照の詳細化であり新規人物ではない。
2. 繰り返し増加が主因か: 影響は小さい(旧カウンタはset集計のため)。
3. カウント単位・tokenization差が主因か: **Yes、主因**。
4. Advanced化Promptの入力: 日本語記事本文(`ja_article_text`)のみ、
   Source/Ledgerは渡していない(`build_prompt()`実装で確認)。
5. 固有名詞KEEPルールの意味: 簡略化(易しい言い換え)をしない除外条件の
   1つ(`ADVANCED_VOCAB_RULE_V2_BLOCK` exception C)であり、新規追加とは
   無関係。
6. 名称単位の内訳: 設計書§2.6の差分表。

**Trial-02限定の改良カウンタ(複合語1件・Title Case見出し除外・kanji
固有名詞検出)で数え直すと、Hormuz ANはJA=EN=**7**で完全一致し、ENで
新規出現した固有名詞は0件だった。「9→19」は実質的にすべてカウント方式
のアーティファクト(タイトル見出し混入7件、複合語分割、kanji未検出)で
あり、日本語に無い固有名詞を英語化工程が実際に新規追加した事実は
確認されなかった。** Meta ANでは旧カウンタ自体が12(JA)->11(EN)と横ばいで
あり、「9→19」という急増自体はHormuz記事特有だった。

## 4. 費用・Regression

- 費用: Hormuz ¥8.768、Meta ¥8.088、固有名詞調査¥0。合計約¥16.9
  (Guardrail ¥70に対し余裕大)。暴走・異常retryなし。
- Regression: `run_project_regression.py --pattern "er039*_test_*.py"`
  で17件全PASS(`er039_family_xy_concreteness_control_trial_02_test_01.py`)。

## 5. 2×2 Matrix 定量結果

数字/過度精度/固有名詞は「旧カウンタ(Trial-01と同一定義)/改良カウンタ
(Trial-02限定)」の順で併記する。

### 5.1 Hormuz

| Cell | JA num/over/ent(旧)/ent(改) | EN num/over/ent(旧)/ent(改) | JA->EN新規固有名詞(改) | Deviation | rubric(causality/fun/comp/thin) |
|---|---|---|---|---|---|
| Baseline(A0+T0) | 39/17/14/8 | 29/17/19/10 | - | LEDGER_COMPLIANT(既存) | - |
| AN3-T0 | 0/0/9/7 | 6/0/19/7 | なし | LEDGER_COMPLIANT | 4/4/4/3 |
| AN3-T1 | 0/0/9/7 | 5/0/18/6* | なし | **LEDGER_DEVIATION(MAJOR×1)** | 4/4/4/3 |
| AN2-T0 | 9/1/12/7 | 7/1/21/7 | なし | LEDGER_COMPLIANT | 4/4/4/3 |
| AN2-T1 | 9/1/12/7 | 7/1/19/7 | なし | LEDGER_COMPLIANT | 4/4/4/3 |

*AN3-T1のEN改良ent=6は、"Brent"が段落先頭語(文頭語除外ロジックの対象)に
なった指標側の検出漏れであり、実際の固有名詞の意味的削減ではない
(設計書§2.6限定事項)。

### 5.2 Meta

| Cell | JA num/over/ent(旧)/ent(改) | EN num/over/ent(旧)/ent(改) | JA->EN新規固有名詞(改) | Deviation | rubric(causality/fun/comp/thin) |
|---|---|---|---|---|---|
| Baseline(A0+T0) | 0/0/13/2 | 0/0/10/3* | - | LEDGER_COMPLIANT(既存) | - |
| AN3-T0 | 0/0/12/2 | 0/0/11/2 | なし | LEDGER_COMPLIANT | 4/4/3/4 |
| AN3-T1 | 0/0/12/2 | 0/0/12/2 | なし | LEDGER_COMPLIANT | 4/4/4/4 |
| AN2-T0 | 0/0/13/2 | 0/0/10/2 | なし | LEDGER_COMPLIANT | 5/5/5/5 |
| AN2-T1 | 0/0/13/2 | 0/0/10/2 | なし | **LEDGER_DEVIATION(MAJOR×1)** | 4/4/4/4 |

*Baseline EN改良ent=3の"Had"は文頭語除外ロジックの既知の残差ノイズ
(見出し直後の文頭語誤検出、AN系では発生していない)。

Metaは元々数字がほぼ0(天井効果、Trial-01と同様)で、AN3/AN2/T0/T1いずれも
数字面での差は測定不能。固有名詞は改良カウンタで全セルJA=EN=2
(Meta, Muse)で安定しており、JA->EN新規固有名詞は0件だった。

## 6. Ledger Deviation Check(主判定)の詳細

- **Hormuz AN3-T1(MAJOR)**: `unsupported_new_claim`(origin=ja_source)。
  「oil prices still connect that distant sea to gasoline and transport
  costs」という経済的連関の主張がLedgerの裏付け範囲を超えると判定。
  同じ日本語原文の主張(「遠い海の話に見えても、原油価格はガソリンや
  運送費につながります」)はBaseline/AN3-T0でも英訳されており、そちらは
  独立した平叙文として簡潔に訳されLEDGER_COMPLIANTだったのに対し、
  AN3-T1では"## In one line"の結論文に複数の主張を圧縮して結合した結果、
  同じ判定器がMAJORとした。origin自体はja_source(新規事実捏造ではない)
  だが、**T1の抑制追記が、英語側の文構造・圧縮のされ方を変え、結果として
  同一判定器の判定を悪化させた実例**として記録する。
- **Meta AN2-T1(MAJOR)**: `changed_scope`(origin=translation)。
  Ledgerでは人間スタッフが電話をかけた相手は企業・店舗等の「相手」
  (MUSE-HC-006)だが、AN2-T1の英文は通話相手を"users"(Museの利用者)と
  記述しており、対象範囲を取り違えている。日本語原文の「相手」という
  一般化された言い方をT1が英語側でも一般化しようとした結果、対象範囲の
  精度が落ちたと推定される、**翻訳段階で新規に生じた意味逸脱の実例**。
- 上記以外の6セル(Hormuz AN3-T0/AN2-T0/AN2-T1、Meta AN3-T0/AN3-T1/
  AN2-T0)はすべてLEDGER_COMPLIANT。

**判定ルール(delegation指定)適用結果**: Deviation MAJORありのセルは
不合格。Hormuz AN3-T1とMeta AN2-T1が該当。**T0(現行英語化)はHormuz/Meta
双方・AN3/AN2双方で常にLEDGER_COMPLIANTだった一方、T1(抑制追記)は
Hormuz/Metaそれぞれ1セルずつでMAJORを出した。** n=1(各セル1回のみ実行)
のため一般化はできないが、T1が意味逸脱リスクを増やす方向に働いた実例が
2記事双方で観測された点は、Trial-01 §9で指摘した「n=1のサンプリング
揺らぎの可能性」を踏まえても軽視できない。

## 7. Leakage Check

Family B(Voices)の`run_analytical_leakage_check_3v`に相当する、Family X
(Entertainment)側のLeakage Check関数は存在しない(`er019_family_x_*`
配下をGrepし該当QA不在を確認)。**該当QAなし**であり、rubricの面白さ・
理解しやすさスコアで代替判定はしていない(deviation checkとrubricは
独立した指標として別掲、混同していない)。

## 8. AN3 vs AN2、T0 vs T1(総合評価)

- **AN3(A3+N2) vs AN2(A2+N2)**: JA数字はAN3が両記事で0(Hormuz/Meta共)を
  維持したのに対し、AN2はHormuz JAで9件(A2はA3より緩い抑制)が残った。
  一方、固有名詞(改良カウンタ)はAN3/AN2ともHormuz=7、Meta=2で同水準
  であり、固有名詞抑制力に差はなかった。Deviation面では、Hormuz AN3が
  T1でMAJORを出した一方、Hormuz AN2はT0/T1ともCOMPLIANTだった。
  Meta側はAN3がT0/T1ともCOMPLIANTで、AN2がT1でMAJORを出した。
  **数字抑制の強さではAN3が優位、Deviation安全性は記事・T variantの
  組み合わせ次第で一貫した優劣がつかなかった**(それぞれ1回ずつしか
  実行していないため、追加Trialなしにどちらかを断定できない)。
- **T0(現行) vs T1(抑制追記)**: 固有名詞(改良カウンタ)・数字ともT0/T1
  で大きな差はなかった(Hormuz AN2でEN数字7->7、entity 7->7)。
  T1は「新しい固有名詞を追加しない」というJA->EN新規固有名詞0件の目標は
  T0と同様に達成できていたが、**T1固有の便益(T0比でさらに数字・固有
  名詞を減らせた事実)は明確には確認できず、むしろMAJOR Deviationを
  2記事で1件ずつ新たに生んだ**。§6の通り、これはT1がJA原文の一般化・
  圧縮表現を英語側でも一般化しようとする過程で、事実の対象範囲や
  文構造の精度を落とす方向に作用した可能性を示す実例である。
- rubric(面白さ・読みやすさ・聞いた場合の理解しやすさ・情報の薄さ)は
  全セルで3〜5点の範囲に収まり、Family Yで観測されたような「数字を
  減らしたのに人気取り的に高得点」という明確な誤判定は今回も観測
  されなかった(Meta AN2-T0が5点満点だった点はrubric側のみの評価であり、
  deviation checkとは独立した指標として解釈する)。

## 9. 新しく判明した問題・限界

- 改良カウンタは文頭語除外ロジックを既存カウンタから継承しており、
  固有名詞が文頭に来る文では検出漏れが起きる(Hormuz AN3-T1の"Brent")。
  次回以降、この限界を解消する改良(文頭語除外を「文全体の最初の語」
  ではなく「記事全体で複数回出現する固有名詞は除外しない」等)が必要に
  なる可能性がある(Production採用判断ではなく、指標改善の技術的課題)。
- T1(抑制追記)は、2記事×1回ずつの実行でそれぞれ1件のMAJOR
  Deviationを出した。T1のみを対象にした再現性検証(複数回実行)は
  delegationで明示的に禁止されている(A1/A2単独の再現性3回Trial禁止と
  同種の運用ルール)ため、本Trialの範囲では「T1が構造的に危険」とまでは
  断定できないが、Production採用を検討する場合は追加検証が必要になる
  可能性が高い。

## 10. Production無変更の証拠

```
git diff --stat HEAD -- "er0*.py" "er003_v1_translator_briefs/" | grep -v er039
```
出力は空(er039以外のer0*.pyファイルに差分なし)。単体testで
`adv_gen.ADVANCED_UNCHANGED_PORTION_SHA256`/`ADVANCED_VOCAB_RULE_V2_
SHA256`がimport時点で自己検証されることも確認済み(§4)。

## 11. 成果物・所在

- Script: `er039_family_xy_concreteness_control_trial_02.py`、単体test
  `er039_family_xy_concreteness_control_trial_02_test_01.py`(17 tests)。
- 出力: `er039_output/family_xy_concreteness_control_trial_02/
  {hormuz,meta}/`(`entity_ja_en_diff.md`、`task_a_ja/AN2_*.md`、
  `cells/{cell}_{ja,en}.md`+`_deviation.json`+`_rubric.json`+
  `_summary.json`、`matrix_summary.json`、`cost_matrix.json`、
  `raw_usage_log.jsonl`、`comparison_{article}.md`)。
- ユーザー確認用: `user_test/concreteness_trial_02/index.html`
  (push後200確認、§12参照)。
- 設計書: `docs/pm/design_family_xy_concreteness_control_trial_02.md`。

## 12. 最終Status案(Sonnet判定案、ユーザー承認待ち)

`USER_DECISION_REQUIRED`を提案する。理由:
- AN3(A3+N2)・AN2(A2+N2)ともT0(現行英語化)ではDeviation MAJORなし
  (数字・固有名詞抑制とEssential Fact維持を両立)、**候補として有望**。
- ただしT1(抑制追記)はHormuz/Meta双方で1セルずつMAJOR Deviationを
  出しており、T1をこのまま採用することは推奨しない。
- 「9→19」問題自体は、改良カウンタでの実測によりカウント方式の
  アーティファクトである可能性が高いと判明したため、Advanced Prompt側の
  固有名詞抑制強化(OPEN-220で示唆されていた方向性)の緊急性は当初想定
  より低い可能性がある。
- Production採用(どのPattern・どのT variantを標準にするか、
  T1のような追記Promptを正式化するか)は人間ユーザーの判断が必要。

## 13. USER_DECISION_REQUIRED事項

1. AN3(A3+N2)とAN2(A2+N2)のどちらを次段階の検証対象として優先するか
   (本Trialでは明確な優劣が出なかった)。
2. T1(抑制追記)方式を今後も検証対象として残すか、それとも今回の
   2件のMAJOR Deviationを理由に一旦保留するか。
3. 「固有名詞9→19」の原因がカウント方式のアーティファクトだったという
   本Trialの実測結果を踏まえ、OPEN-220(Advanced Prompt側固有名詞抑制)の
   優先度・要否をどう扱うか。
