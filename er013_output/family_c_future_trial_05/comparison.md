# Family C Future — Trial-03 vs Trial-04 vs Trial-05 比較

管理ID: EDITORIAL-FUTURE-FAMILY-C-V5-EMOTION-RECOVERY-AND-CONSTRAINT-STABILITY-TRIAL-05
同一テーマ(家庭用ロボットと家事)・同一Layer1 Ledger・同一Trial-02 World
Scaffold/Layer2-3を再利用(¥0)。v5はv4の場面数決定的絞り込み(2場面)を
維持したまま、(1)場面内の感情の起伏1つ、(2)選択1つ、(3)出来事列挙の
目安上限、(4)統合示唆段落の配置固定(見出し3つに固定し、2つ目の
[[IMAGINED]]ブロック直後の最後の見出し内のみ)、(5)枠外(3つ目の見出し)
での"will"禁止のhedging契約、をPromptへ追加した。Trial限定、Production
未採用。

## 語数・場面数・構成

| 項目 | Trial-03 A2 | Trial-04 A2 | Trial-05 A2 | Trial-03 B1 | Trial-04 B1 | Trial-05 B1 |
|---|---|---|---|---|---|---|
| word_count | 550 | 405 | 434 | 744 | 484 | 520 |
| target_range(Trial限定目安) | 450-600 | 380-520 | 380-520 | 500-700 | 450-620 | 450-620 |
| within_range | PASS | PASS | PASS | FAIL(+44語) | PASS | PASS |
| [[IMAGINED]]場面数 | 3 | 2 | 2 | 3 | 2 | 2 |
| 見出し数 | 3(自由) | 3(自由) | 3(固定契約) | 3(自由) | 3(自由、うち1つが場面間に混入) | 3(固定契約、v5構造Gate PASS) |
| gate_attempts_used | - | - | 1(初回でPASS) | - | - | 1(初回でPASS) |

## Gate・QA結果

| 項目 | Trial-03 A2 | Trial-04 A2 | Trial-05 A2 | Trial-03 B1 | Trial-04 B1 | Trial-05 B1 |
|---|---|---|---|---|---|---|
| 編集Gate(数値/研究語/製品名/hedge密度/語数) | PASS | PASS | PASS | FAIL(製品名漏れ+語数超過) | PASS | PASS |
| v5構造Gate(新規、見出し3固定・場面間見出し・枠外will) | (未実装) | (未実装) | PASS | (未実装) | (未実装、Trial-04で発覚した問題に相当) | PASS |
| imagined_hedge_density(枠内) | 0.0% | 0.0% | 0.0% | 2.3% | 0.0% | 0.0% |
| Fact Checker A'(Layer1、本Trialの是正対象外) | REVIEW_REQUIRED | REVIEW_REQUIRED | REVIEW_REQUIRED(不変) | REVIEW_REQUIRED | REVIEW_REQUIRED | REVIEW_REQUIRED(不変) |
| Ledger Deviation | LEDGER_COMPLIANT | LEDGER_COMPLIANT | LEDGER_COMPLIANT | LEDGER_COMPLIANT | LEDGER_COMPLIANT | LEDGER_COMPLIANT |
| Future Framing QA v2 | PASS | PASS | PASS | PASS | REVIEW_REQUIRED(統合示唆配置+will断定) | **PASS(是正済み)** |
| unhedged_future_claims_heuristic_hits(枠外) | (未計測) | (未計測) | 0 | (未計測) | (未計測、実際に複数検出) | 0 |
| overall_status(全Gate AND) | NG_REVIEW_REQUIRED(Fact Checker A'由来) | NG_REVIEW_REQUIRED(同上) | NG_REVIEW_REQUIRED(同上、Fact Safety自体は全てCOMPLIANT/PASS) | NG_REVIEW_REQUIRED | NG_REVIEW_REQUIRED | NG_REVIEW_REQUIRED(同上) |

(overall_statusがいずれのTrialでもNG_REVIEW_REQUIREDなのは、Fact Checker
A' verdict=REVIEW_REQUIREDがTrial-03から不変で残っているため。これは
本Trialの診断・是正対象[語数構造・感情・統合示唆配置・hedging]とは別の
既存の未解決事項であり、Trial-05では変更していない。編集Gate・v5構造
Gate・Ledger Deviation・Future Framing QA v2という、本Trialの対象4項目は
A2/B1いずれもPASS/COMPLIANTを達成した。)

## 感情・没入感スコア(0〜3、主観評価+本文引用)

| レベル | Trial-03 | Trial-04 | Trial-05 |
|---|---|---|---|
| A2 | 2(場面ごとに感情語+選択の兆しはあるが起伏は弱め。例: "She enjoys the clean room. She does not enjoy becoming its morning supervisor.") | 1(出来事列挙化。末尾"leaves smiling"程度) | **3**(起伏+明確な選択が2場面とも成立。例: "Relief turns into irritation... faces a choice: wait for more help or finish the hard part by hand. 'I'll do this,' they say.") |
| B1 | (本Trial非対象、参考評価せず) | 1(統合示唆が場面間に混入し感情描写が薄い) | **3**(起伏+選択+台詞。例: "Her smile turns into a sigh. She can wait or finish the exception herself... says, 'Keep going.'") |

## 安定性評価(A2、Writer呼び出しのみ×3サンプル)

| サンプル | word_count | within_range | 見出し数 | v5構造Gate | 感情起伏+選択の有無 | 機械的兆候 |
|---|---|---|---|---|---|---|
| 本生成 | 434 | PASS | 3 | PASS | あり("smile fades"→"door opening"、明示選択あり) | なし |
| stability sample1 | 407 | PASS | 3 | PASS | あり("Relief turns into irritation"、明示選択あり) | なし |
| stability sample2 | 444 | PASS | 3 | PASS | あり("excitement turns into impatience"、明示選択あり) | 冒頭"Picture a weekday evening around 2035"がテンプレ的に3サンプル共通(想像枠の入口文契約による意図的な定型であり、Prompt指示通りの挙動。本文中の出来事描写自体はサンプルごとに異なる)

3サンプルとも語数目安内・見出し3つ固定・v5構造Gate PASS・感情の起伏と
選択が明確に確認でき、v4より制約を追加したにもかかわらず出力の不安定化
(語数の大きなばらつき・Gate再試行の多発・崩れたマーカー等)は観測されな
かった(A2/B1本生成ともgate_attempts_used=1、初回でPASS)。

## 費用

Trial-05累積実費(reuse_research¥0+a2+b1+stability2サンプル、Fact
Checker A'・Ledger Deviation・Framing QA込み): ¥22.88
(Family C残額¥105.01+追加上限¥100=合計上限¥205.01のうち、¥22.88消費、
残り¥182.13)

## 結論

v4で解消した語数超過(A2/B1とも目安内)を維持したまま、Trial-04で後退
した感情・没入感を、A2/B1とも0〜3スコアで2→3(A2)・1→3(B1)へ回復
させた。Trial-04でB1のみ発生していたFuture Framing QA v2
REVIEW_REQUIRED(統合示唆段落の配置ミス+枠外"will"の未hedge断定)は、
見出し3つ固定+統合示唆配置の明示+枠外hedging契約の3点により、A2/B1
とも初回生成でPASSした。3サンプルによる安定性評価でも、追加した制約に
よる出力の不安定化(語数ばらつき・構造崩れ・機械的兆候)は観測されな
かった。

ユーザー指示書の判定基準(感情・没入感がA2/B1いずれかで2未満、または
安定性のばらつきが大きい、または機械的兆候が明確、のいずれかで
「不十分」)に照らすと、いずれの条件にも該当しないため、追加改善案の
簡易Trial(05b等)は実施せず、v5を最終アームとして評価した(原因仮説→
最小検証→評価の順を守り、目的なくTrial回数を増やさないため)。

## 記事本文

- Trial-03: `../family_c_future_trial_03/a2/reader_facing_article.txt`
- Trial-04: `../family_c_future_trial_04/a2/reader_facing_article.txt` / `../family_c_future_trial_04/b1/reader_facing_article.txt`
- Trial-05: `a2/reader_facing_article.txt` / `b1/reader_facing_article.txt`
- Trial-05安定性サンプル: `stability/a2_sample_1/reader_facing_article.txt` / `stability/a2_sample_2/reader_facing_article.txt`
