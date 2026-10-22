# Post-EN Risk Flagger Review Queue: paycheck_personality__run_pp_02 / b1b

- run_id: `rf20261022T000459Z-a324`  status: **OK**
- article_sha256: `3b113a9379a27d22a43c79d0f412c0c9abcd2287a5c13882d5723920c9095cf8`  ledger_sha256: `a31992b53082d2f143f9b32949dbb926d353c1034a04e2fad666cceca21b0980`
- level: `b1b` (b1b=Advanced, a2=Standard)  splitter: `en_split_v1`  producer: `deterministic_v2`  run_label: `FAMILY-X-B3-CORE-NUMBER-ROUNDING-ARTICLE-A-REMAKE-C2`
- sentences: 42  facts: 19  candidate issues: 2

これは**候補一覧**です(合否判定ではありません)。判定はHuman Review側で行います。

## Conditions
- luna A3: OK flags=1 cost_jpy=0.194304 model=gpt-6-luna
- luna A4: OK flags=1 cost_jpy=0.200544 model=gpt-6-luna
- gemini35fl A3: OK flags=0 cost_jpy=0.282064 model=gemini-3.5-flash-lite
- gemini35fl A4: OK flags=0 cost_jpy=0.287824 model=gemini-3.5-flash-lite

## Issues

### s10  (confidence max 0.32)
- issue_id: `paycheck_personality__run_pp_02__b1b__3b113a93__rf20261022T000459Z-a324__s10`
- sentence: In every study, personality and income were each measured at least three times.
- before: The researchers brought together data from 11 studies that followed the same people over a long time. / The people in the studies were working and reported on their personality and income from work.
- after: This was not one snapshot, but a series that followed changes over time. / But this series has no contest with “the talented coworker next door.”
- detected_by: luna-A4(0.32)
- reason [その他]: “personality … each measured at least three times” は、台帳の「Big Fiveの少なくとも1特性を3回以上測定」という条件を、各性格特性がすべて3回以上測定されたという範囲に広げていませんか。
- fact F07: 対象研究は、収入とBig Fiveの少なくとも1特性を縦断的に3回以上測定することなどを適格条件とし、解析には個人レベルの変化を扱うランダム切片交差遅延パネルモデルを用いた連続時間メタ分析を行った。
  scope: メタ分析に含めた縦断研究と、統合個人レベルデータの解析
  conditions: 個人レベルデータまたは必要な同時・自己回帰・交差遅延相関情報が得られ、標本数や測定間隔などの記述情報が利用可能であることも条件とした。
  numeric_value: 最低3測定波 (numeric_scope: 一次研究の縦断研究としての適格条件)
  notes_for_writer: モデルは安定した個人間差と個人内の変化を分けて推定する。縦断的な交差遅延関係の推定だけで因果効果が確定するわけではない。

### s26  (confidence max 0.58)
- issue_id: `paycheck_personality__run_pp_02__b1b__3b113a93__rf20261022T000459Z-a324__s26`
- sentence: This is not a story about “more serious people earning more than others.”
- before: This was not a dramatic story where “a pay raise turns you into an extremely serious person!” / If an annual income ranking has popped into your head, put it away for now.
- after: The study looks at changes within the same person. / It is like watching yourself over time, with no one to compete against.
- detected_by: luna-A3(0.58)
- reason [その他]: 「not a story about ‘more serious people earning more than others’」は個人間の差を研究が扱っていないという意味にも読めますが、台帳では個人間差と個人内変化を分けて推定したということではありませんか
- fact F07: 対象研究は、収入とBig Fiveの少なくとも1特性を縦断的に3回以上測定することなどを適格条件とし、解析には個人レベルの変化を扱うランダム切片交差遅延パネルモデルを用いた連続時間メタ分析を行った。
  scope: メタ分析に含めた縦断研究と、統合個人レベルデータの解析
  conditions: 個人レベルデータまたは必要な同時・自己回帰・交差遅延相関情報が得られ、標本数や測定間隔などの記述情報が利用可能であることも条件とした。
  numeric_value: 最低3測定波 (numeric_scope: 一次研究の縦断研究としての適格条件)
  notes_for_writer: モデルは安定した個人間差と個人内の変化を分けて推定する。縦断的な交差遅延関係の推定だけで因果効果が確定するわけではない。
- fact F13: 性格特性から後の収入への関連と、収入から後の性格変化への関連の推定は、特性により正負が異なる。勤勉性・情緒安定性では両方向が正、外向性では両方向が負、協調性では収入から後の協調性への関連が負で逆方向は非有意、開放性では両方向が非有意だった。
  scope: 統合された個人内縦断モデル
  conditions: 因果方向を確定する実験ではなく、先行値から後続値への交差遅延関連。
  causal_strength: OBSERVED_REPORTED
  notes_for_writer: 「双方向」は両方向に時間的な関連をモデル化したことを指し、すべての特性で両方向の関連が有意だったという意味ではない。
