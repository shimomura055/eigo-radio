# Post-EN Risk Flagger Review Queue: paycheck_personality__run_pp_01 / b1b

- run_id: `rf20261021T034829Z-e230`  status: **OK**
- article_sha256: `7004b24076d6994ab68813041308ee22272b91f32bf8873b89f017e53bf1e829`  ledger_sha256: `a31992b53082d2f143f9b32949dbb926d353c1034a04e2fad666cceca21b0980`
- level: `b1b` (b1b=Advanced, a2=Standard)  splitter: `en_split_v1`  producer: `deterministic_v2`  run_label: `FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01`
- sentences: 36  facts: 19  candidate issues: 1

これは**候補一覧**です(合否判定ではありません)。判定はHuman Review側で行います。

## Conditions
- luna A3: OK flags=0 cost_jpy=0.128512 model=gpt-6-luna
- luna A4: OK flags=0 cost_jpy=0.135552 model=gpt-6-luna
- gemini35fl A3: OK flags=1 cost_jpy=0.349024 model=gemini-3.5-flash-lite
- gemini35fl A4: OK flags=0 cost_jpy=0.281584 model=gemini-3.5-flash-lite

## Issues

### s11  (confidence max 0.7)
- issue_id: `paycheck_personality__run_pp_01__b1b__7004b240__rf20261021T034829Z-e230__s11`
- sentence: In every study, the same people’s income and personality were measured at least three times.
- before: They looked at people who were working and had reported on their personality and income from work. / The number of people varied by analysis, but the researchers used data from as many as 134,515 people.
- after: The key was how the researchers compared people. / They analyzed separately the differences between people that tend not to change and changes that happen within each person.
- detected_by: gemini35fl-A3(0.7)
- reason [数量時系列]: s11の「In every study, the same people’s income and personality were measured at least three times」は、11件の研究すべてで同一の参加者が3回以上測定されたと読めますが、台帳F04では「11件の大規模な縦断パネル研究の個人レベルデータを統合した。解析に含まれた参加者数は最大134,515人で、解析ごとに参加者数は異なる」、F06・F07では各研究の測定波数が3～18回とされています。『各研究内で3回以上測定された』ではなく『すべての研究で同一の人が3回以上』という意味になっていませんか。
- fact F04: 研究は事前登録された連続時間メタ分析で、11件の大規模な縦断パネル研究の個人レベルデータを統合した。解析に含まれた参加者数は最大134,515人で、解析ごとに参加者数は異なる。
  scope: 11件の全国または地域代表性を持つ縦断研究。最大解析標本数は134,515人
  conditions: 参加者数はBig Five各特性と収入の解析ごとに異なる。研究者は就労中で、性格と仕事からの収入の情報を報告した参加者を解析対象とした。
  numeric_value: 11研究; 最大134,515人 (numeric_scope: 統合した縦断研究数と解析に含まれた最大参加者数。全モデルで同一のNではない。)
  date_or_period: 一次研究で利用可能なデータの最終リリースは2022年11月時点
  notes_for_writer: 「134,515人がすべてのモデルに参加した」とは書かない。
- fact F06: 各研究の観測期間は4～20年で、測定波は3～18回、隣り合う測定波の間隔は1～12年だった。
  scope: 統合対象11研究
  conditions: 研究ごとに期間、測定波数、測定間隔が異なる。
  numeric_value: 観測期間4～20年; 3～18測定波; 波間隔1～12年 (numeric_scope: 各研究の範囲。単一の参加者全員に共通する期間・測定スケジュールではない。)
  date_or_period: 各一次研究の縦断観測期間
- fact F07: 対象研究は、収入とBig Fiveの少なくとも1特性を縦断的に3回以上測定することなどを適格条件とし、解析には個人レベルの変化を扱うランダム切片交差遅延パネルモデルを用いた連続時間メタ分析を行った。
  scope: メタ分析に含めた縦断研究と、統合個人レベルデータの解析
  conditions: 個人レベルデータまたは必要な同時・自己回帰・交差遅延相関情報が得られ、標本数や測定間隔などの記述情報が利用可能であることも条件とした。
  numeric_value: 最低3測定波 (numeric_scope: 一次研究の縦断研究としての適格条件)
  notes_for_writer: モデルは安定した個人間差と個人内の変化を分けて推定する。縦断的な交差遅延関係の推定だけで因果効果が確定するわけではない。
