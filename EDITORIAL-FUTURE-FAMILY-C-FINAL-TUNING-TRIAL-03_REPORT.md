# EDITORIAL-FUTURE-FAMILY-C-FINAL-TUNING-TRIAL-03

管理ID: EDITORIAL-FUTURE-FAMILY-C-FINAL-TUNING-TRIAL-03
性質: 最小Trial(Sonnet往復1回)。**Production配線・CURRENT_SPEC正式化・
APPROVED変更なし**。既存Production経路・Discovery成果物・SSOT本文は無編集。
Git操作なし(別途Fableが統合)。

## ユーザー確定判断(原文)

> hedging削減+A2短縮の最終調整Trialを進めてください。前回の再設計で、統計冒頭/study
> found型研究説明/製品名・仕様列挙/研究・データ解説感が解消した点は、ユーザー方針に
> 合っています。この構造は維持し、今回は主に以下を調整してください。想像枠内のmay /
> could等のhedging過多を抑える/想像であることを入口で明示した後は、場面内ではより
> 自然で力のある語りを許容する/「わくわく」「不安」「葛藤」の感情強度を上げる/A2を
> 標準分量へ近づける/Fact Safetyは一切弱めない/研究・データ解説っぽさを再流入させない。
> 特に、短くするために研究説明へ戻る、または断定感を出すために現在事実と想像の境界を
> 曖昧にすることは避けてください。同一Ledger再利用で、前回見積の¥20〜30程度を目安に
> 最小Trialを実施して構いません。こちらもProduction採用承認ではありません。今回到達
> してよいStatusは最大VALIDATEDです。

## 1. 何が問題だったか

Trial-02(前回の再設計)は、統計冒頭・研究解説文体・製品名列挙という大きな問題は
解消していたが、実データを詳しく調べると次の2点が残っていた。

- **hedging過多**: 記事全体で"may/might/could"等が非常に多く使われ、場面の力強さが
  弱まっていた。詳細確認の結果、`[[IMAGINED]]`マーカーの中身自体は既にhedgingが
  少なかった(A2は0/59文)。過多だったのは、各想像場面の直後に続く「その場面が
  もたらす反応・葛藤」の段落(マーカーの**外側**)で、ここに大量のmay/could/mightが
  集中していた(A2で54件)。
- **A2の分量過多**: A2が1161語、B1が1145語と、目安(CURRENT_SPECにA2向けの明示的な
  語数上限は無かったため、ユーザー指示書が例示した450〜600語をFamily C A2の目安と
  して採用)の約2倍に達していた。

## 2. 何を変更したか

新規ファイルのみ追加し、`_02`ファイルは無編集のまま維持した。

- `er013_family_c_future_writer_03.py`: Writer promptを調整。(a) 想像枠(`[[IMAGINED]]`)
  内はhedging語(may/might/could/perhaps/possibly)を使わず現在形・断定調で書く、
  かつ**その場面から直接生まれる人物の反応・選択・感情までを同じ枠内に含める**よう
  明示(枠外の一般的な示唆・まとめは従来どおりhedging付きのまま維持=境界原則は
  変更していない)。(b) 各場面で最低1回、行動または短い台詞で具体的な楽しみ・不安・
  葛藤を示す指示、記事内で希望と不安を明示的に対比させる指示を追加。(c) A2は
  450〜600語、B1は500〜700語を目安とし、「短縮のために場面や感情の描写を削って
  研究解説的な要約へ戻すこと」を明示的に禁止。
- `er013_family_c_future_qa_03.py`: `_02`の全機能を無変更のまま再輸出したうえで、
  決定的スキャンに「枠内hedge密度」と「語数」を追加し、既存5項目(統計値・研究語・
  製品名・FACT件数上限・冒頭段落)と統合した編集Gate(`scan_editorial_gate_v3`)を
  新設。閾値超過はWriter再生成(最大1回)。
- `er013_family_c_future_trial_03_run.py`: Trial-02のResearch/World Scaffold/
  Layer2-3/World Packageを再利用(コピーのみ、費用¥0)し、上記Writer/QAで記事生成
  →既存Fact Checker A'/Ledger Deviation Checker/Local Rewrite/Future Framing QA v2
  (いずれも無改変)を実行。
- offline unit test(`er013_family_c_future_qa_test_03.py`、21件、¥0)。既存
  `er013_family_c_future_qa_test_02.py`(24件)は無変更でPASS維持を確認。

## 3. 何が改善されるか(実データ)

| 指標 | Trial-02 A2 | Trial-03 A2 | Trial-02 B1 | Trial-03 B1 |
|---|---|---|---|---|
| 語数 | 1161 | **550**(目安450-600内) | 1145 | 744(目安500-700をやや超過) |
| 枠内hedge密度 | 0.000 | 0.000 | 0.190 | **0.023** |
| 感情強度(0-2、主観、引用必須) | 1 | **2** | 0 | **2** |
| 研究解説スキャン該当数 | 0 | 0 | 0 | 0 |
| Future Framing QA v2 | PASS | PASS | PASS | PASS |
| Fact Checker contradictions | 0 | 0 | 0 | 0 |
| Ledger Deviation | LEDGER_COMPLIANT | LEDGER_COMPLIANT | LEDGER_COMPLIANT | LEDGER_COMPLIANT |
| 編集Gate最終status | PASS | PASS | PASS | FAIL(下記参照) |

詳細な引用根拠・全文比較は`er013_output/family_c_future_trial_03/comparison.md`・
`index.html`(Trial-02/Trial-03記事を並置)参照。

A2は台詞(“Help needed,” “Watch this part again,” “Keep going,” “I will do this
part.”)と行動に紐づく感情描写(“Mara feels a thrill... She also feels
irritation. She pulls on shoes”)を伴いつつ550語まで短縮でき、「The hope is
simple...The concern is sharper...」で希望/不安を明示的に対比できた。B1も同様に
台詞3件・行動連動の感情表現・希望/不安の対比を達成した。研究解説スキャン・Fact
Checker矛盾・Ledger逸脱・境界チェック(枠外の未来断定/枠内の現在事実捏造)はいずれも
Trial-02から変わらず0件を維持しており、**Fact Safetyは弱めていない**。

## 4. リスクや注意点

- **B1の編集Gate最終status=FAIL**: 2回目のWriter再生成attemptでも(i)語数がやや
  超過(744語 > 700語目安)、(ii)`product_name_hits=['Stretch']`が発火した。(ii)は
  実際には“long stretche**s**”という一般語の部分文字列一致による**誤検知**であり
  (`er013_family_c_future_qa_02.py::scan_product_name_hits()`の単純な部分文字列
  一致という既存[v2、無改変]の設計上の限界。本タスクで新設した機能ではない)、
  Stretchという製品名自体は本文に存在しない。この件は修正せず報告のみとする
  (次の一手はFableまたはユーザー判断: 語境界を考慮した一致判定への改善候補として
  `OPEN_ITEMS.md`への新規登録が考えられるが、本タスクでは実装していない)。
- **記事全体overall_status**: A2/B1とも`NG_REVIEW_REQUIRED`(Fact Checker A'の
  verdictが`REVIEW_REQUIRED`のため。原因は「想像上の帰結("could/would"付きの
  仮定的主張)は具体的な裏付けが確認できない」という、想像記事の性質上避けられない
  advisory的な指摘であり、`contradictions`は両レベルとも0件)。この扱いはTrial-02
  のA2と同じ既存パターンであり、本Trialで新規に発生した問題ではない。
- 費用実測: ¥13.55(内訳: `er013_output/family_c_future_trial_03/cost_summary.json`、
  Research再利用のため¥0。ユーザー見積¥20〜30の範囲内、実際は下回った)。
- 本Trialは**VALIDATED**到達を上限とする(ユーザー指示)。Production採用・
  CURRENT_SPEC正式化はしていない。A2の450〜600語という目安値は、CURRENT_SPECに
  A-Family A2の明示的なhard word_count仕様が見つからなかったため、ユーザー指示書
  の例示値をそのままTrial限定で採用したものであり、恒久Production仕様として
  提案するものではない(正式化する場合は別途USER_DECISION_REQUIRED)。

## 5. 検証(実行済み)

- offline unit test: `er013_family_c_future_qa_test_03.py`(21件、¥0)+既存
  `er013_family_c_future_qa_test_02.py`(24件、無変更PASS)。Trial-02実データへの
  回帰確認(A2/B1とも語数超過でFAILになることを確認)含む。
- `run_project_regression.py --pattern "er013*"`: collected=67・passed=67・
  failed=0・errors=0。
- `run_project_regression.py`(default、全件): collected=2535・passed=2532・
  failed=3・errors=0(既知の無関係failureの1つ`er003_test_bad.FixtureTests.
  test_case_0`[意図的self-check]を個別に確認済み。残る2件は継続的にSSOTへ記録
  されてきた既知の無関係failureパターンと一致)。A/B-Family既存Production経路への
  無影響を確認した。
- 実Trial実行(Standard同期、実API): `er013_family_c_future_trial_03_run.py`
  (reuse_research→a2→b1→evaluate)。実測費用¥13.55。

## 6. 到達Status

**VALIDATED**(ユーザー指定の上限どおり)。hedging削減・感情強度向上・A2短縮・
研究解説感の再流入なし・Fact Safety維持を実データで確認した。B1の編集Gate FAIL
(既存v2製品名スキャンの誤検知+軽微な語数超過)は次の一手の候補として報告する。
Production採用・CURRENT_SPEC正式化はユーザーの別途承認が必要。

## 7. 成果物

- 新規: `er013_family_c_future_writer_03.py`、`er013_family_c_future_qa_03.py`、
  `er013_family_c_future_trial_03_run.py`、`er013_family_c_future_qa_test_03.py`
- `er013_output/family_c_future_trial_03/`(research/a2/b1/comparison.md/
  index.html/cost_summary.json/e2e_evaluate_summary.json/raw_usage_log.jsonl)
- `docs/pm/RESULT_PACKET_FC3.md`

## 8. Dangling Reference Check

`_02`ファイルは本タスクで一切改変していない(参照確認済み)。`_03`は`_02`を
import・再輸出するのみで、既存Production経路(A-Family/B-Family)・Discovery
成果物(`FAMILY-A-DISCOVERY-*`、`er011_*`)は一切importしていない。
