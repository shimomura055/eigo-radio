# Post-EN Risk Flagger Review Queue: paycheck_personality__run_pp_01 / a2

- run_id: `rf20261021T034913Z-d5eb`  status: **OK**
- article_sha256: `8b000a58f424cb10bce87db533f7a47ee2c1cd1d5a1546dadc925ded693aadef`  ledger_sha256: `a31992b53082d2f143f9b32949dbb926d353c1034a04e2fad666cceca21b0980`
- level: `a2` (b1b=Advanced, a2=Standard)  splitter: `en_split_v1`  producer: `deterministic_v2`  run_label: `FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01`
- sentences: 47  facts: 19  candidate issues: 4

これは**候補一覧**です(合否判定ではありません)。判定はHuman Review側で行います。

## Conditions
- luna A3: OK flags=1 cost_jpy=0.189808 model=gpt-6-luna
- luna A4: OK flags=3 cost_jpy=0.255808 model=gpt-6-luna
- gemini35fl A3: OK flags=1 cost_jpy=0.17013 model=gemini-3.5-flash-lite
- gemini35fl A4: OK flags=0 cost_jpy=0.204424 model=gemini-3.5-flash-lite

## Issues

### s6  (confidence max 0.28)
- issue_id: `paycheck_personality__run_pp_01__a2__8b000a58__rf20261021T034913Z-d5eb__s6`
- sentence: But this time, the people in the story are not rich people.
- before: “Or do you start taking things more seriously after you earn more?” / When you hear about studies on income and personality, you may expect to learn the “secret of people who earn a lot.”
- after: They are “your past self” and “your later self.” / The research brought together 11 large studies.
- detected_by: luna-A4(0.28)
- reason [不在断定]: 「not rich people」と参加者の収入層を断定していますが、台帳には富裕層ではないとは記載されていないのではありませんか。
- fact F04: 研究は事前登録された連続時間メタ分析で、11件の大規模な縦断パネル研究の個人レベルデータを統合した。解析に含まれた参加者数は最大134,515人で、解析ごとに参加者数は異なる。
  scope: 11件の全国または地域代表性を持つ縦断研究。最大解析標本数は134,515人
  conditions: 参加者数はBig Five各特性と収入の解析ごとに異なる。研究者は就労中で、性格と仕事からの収入の情報を報告した参加者を解析対象とした。
  numeric_value: 11研究; 最大134,515人 (numeric_scope: 統合した縦断研究数と解析に含まれた最大参加者数。全モデルで同一のNではない。)
  date_or_period: 一次研究で利用可能なデータの最終リリースは2022年11月時点
  notes_for_writer: 「134,515人がすべてのモデルに参加した」とは書かない。

### s10  (confidence max 0.32)
- issue_id: `paycheck_personality__run_pp_01__a2__8b000a58__rf20261021T034913Z-d5eb__s10`
- sentence: The number of people was not the same in every study.
- before: The research brought together 11 large studies. / They looked at people who had jobs and shared information about their personality and work income.
- after: The researchers used data from up to 134,515 people. / Each study measured the same people’s income and personality at least three times.
- detected_by: luna-A4(0.32)
- reason [数量時系列]: 「every study」と各研究で人数が異なると述べていますが、台帳が示すのは解析ごとに参加者数が異なることではありませんか。
- fact F04: 研究は事前登録された連続時間メタ分析で、11件の大規模な縦断パネル研究の個人レベルデータを統合した。解析に含まれた参加者数は最大134,515人で、解析ごとに参加者数は異なる。
  scope: 11件の全国または地域代表性を持つ縦断研究。最大解析標本数は134,515人
  conditions: 参加者数はBig Five各特性と収入の解析ごとに異なる。研究者は就労中で、性格と仕事からの収入の情報を報告した参加者を解析対象とした。
  numeric_value: 11研究; 最大134,515人 (numeric_scope: 統合した縦断研究数と解析に含まれた最大参加者数。全モデルで同一のNではない。)
  date_or_period: 一次研究で利用可能なデータの最終リリースは2022年11月時点
  notes_for_writer: 「134,515人がすべてのモデルに参加した」とは書かない。

### s12  (confidence max 0.3)
- issue_id: `paycheck_personality__run_pp_01__a2__8b000a58__rf20261021T034913Z-d5eb__s12`
- sentence: Each study measured the same people’s income and personality at least three times.
- before: The number of people was not the same in every study. / The researchers used data from up to 134,515 people.
- after: The important thing was how the researchers compared people. / They looked separately at differences between people that usually stay the same.
- detected_by: gemini35fl-A3(0.3)
- reason [数量時系列]: s12の「Each study measured the same people’s income and personality at least three times.」という記述は、F07の適格条件（縦断的に3回以上測定）と一致していますが、各研究内の「同じ人々」が全測定波に参加し続けたと読者に誤解を与えないか確認してください。
- fact F07: 対象研究は、収入とBig Fiveの少なくとも1特性を縦断的に3回以上測定することなどを適格条件とし、解析には個人レベルの変化を扱うランダム切片交差遅延パネルモデルを用いた連続時間メタ分析を行った。
  scope: メタ分析に含めた縦断研究と、統合個人レベルデータの解析
  conditions: 個人レベルデータまたは必要な同時・自己回帰・交差遅延相関情報が得られ、標本数や測定間隔などの記述情報が利用可能であることも条件とした。
  numeric_value: 最低3測定波 (numeric_scope: 一次研究の縦断研究としての適格条件)
  notes_for_writer: モデルは安定した個人間差と個人内の変化を分けて推定する。縦断的な交差遅延関係の推定だけで因果効果が確定するわけではない。

### s18  (confidence max 0.94)
- issue_id: `paycheck_personality__run_pp_01__a2__8b000a58__rf20261021T034913Z-d5eb__s18`
- sentence: In a way, the researchers stopped comparing people with others.
- before: Not, “What’s different between me and that person who earns a lot?” / But, “How are my past self and my later self different?”
- after: Instead, they followed each person over time. / It is like putting down binoculars you use to look at your neighbor’s greener grass.
- detected_by: luna-A3(0.86), luna-A4(0.94)
- reason [その他]: 「stopped comparing people with others」は、研究者が人々の間の安定した差も別途扱ったというFactと食い違うのではありませんか。
- reason [否定反転]: 「stopped comparing people with others」と比較をやめたと述べていますが、台帳では安定した個人間差も別に分析したのではありませんか。
- fact F07: 対象研究は、収入とBig Fiveの少なくとも1特性を縦断的に3回以上測定することなどを適格条件とし、解析には個人レベルの変化を扱うランダム切片交差遅延パネルモデルを用いた連続時間メタ分析を行った。
  scope: メタ分析に含めた縦断研究と、統合個人レベルデータの解析
  conditions: 個人レベルデータまたは必要な同時・自己回帰・交差遅延相関情報が得られ、標本数や測定間隔などの記述情報が利用可能であることも条件とした。
  numeric_value: 最低3測定波 (numeric_scope: 一次研究の縦断研究としての適格条件)
  notes_for_writer: モデルは安定した個人間差と個人内の変化を分けて推定する。縦断的な交差遅延関係の推定だけで因果効果が確定するわけではない。
