# Post-EN Risk Flagger Review Queue: paycheck_personality__run_pp_02 / a2

- run_id: `rf20261022T005505Z-0146`  status: **OK**
- article_sha256: `909684336e4da8c8d011ed3851e4a01879ce03163404293251121e889cc55f81`  ledger_sha256: `a31992b53082d2f143f9b32949dbb926d353c1034a04e2fad666cceca21b0980`
- level: `a2` (b1b=Advanced, a2=Standard)  splitter: `en_split_v1`  producer: `deterministic_v2`  run_label: `B3RD8 writer after rejudge`
- sentences: 41  facts: 19  candidate issues: 2

これは**候補一覧**です(合否判定ではありません)。判定はHuman Review側で行います。

## Conditions
- luna A3: OK flags=1 cost_jpy=0.186192 model=gpt-6-luna
- luna A4: OK flags=2 cost_jpy=0.204192 model=gpt-6-luna
- gemini35fl A3: OK flags=0 cost_jpy=0.189875 model=gemini-3.5-flash-lite
- gemini35fl A4: OK flags=0 cost_jpy=0.195592 model=gemini-3.5-flash-lite

## Issues

### s17  (confidence max 0.32)
- issue_id: `paycheck_personality__run_pp_02__a2__90968433__rf20261022T005505Z-0146__s17`
- sentence: They moved from ranking people by yearly income to following one person over time.
- before: One example is: “That person works harder than I do and earns more.” / Another question is: “How did my personality change after my income changed?”
- after: It was a different contest altogether. / The trait they focused on was conscientiousness: the habit of working seriously and steadily.
- detected_by: luna-A4(0.32)
- reason [その他]: 「yearly incomeで人々を順位付けしていた」という説明は、台帳にある「個人間差と個人内変化を分けて推定した」という解析方法より広い断定ではありませんか。
- fact F07: 対象研究は、収入とBig Fiveの少なくとも1特性を縦断的に3回以上測定することなどを適格条件とし、解析には個人レベルの変化を扱うランダム切片交差遅延パネルモデルを用いた連続時間メタ分析を行った。
  scope: メタ分析に含めた縦断研究と、統合個人レベルデータの解析
  conditions: 個人レベルデータまたは必要な同時・自己回帰・交差遅延相関情報が得られ、標本数や測定間隔などの記述情報が利用可能であることも条件とした。
  numeric_value: 最低3測定波 (numeric_scope: 一次研究の縦断研究としての適格条件)
  notes_for_writer: モデルは安定した個人間差と個人内の変化を分けて推定する。縦断的な交差遅延関係の推定だけで因果効果が確定するわけではない。

### s25  (confidence max 0.69)
- issue_id: `paycheck_personality__run_pp_02__a2__90968433__rf20261022T005505Z-0146__s25`
- sentence: They found a weak link in both directions: personality with later income, and income with later personality.
- before: But the arrow does not point only one way. / A rise in conscientiousness was also weakly linked to higher income later.
- after: After hearing this, you may want to ask, “Does a pay raise change your personality too?” / But wait before you decide that is true.
- detected_by: luna-A3(0.69), luna-A4(0.68)
- reason [その他]: 「personality」として性格特性全般を両方向の弱い関連に含めていますが、協調性から収入への関連は非有意で、開放性は両方向とも非有意という台帳と食い違うのではありませんか。
- reason [その他]: 「personalityとの関連が両方向に見つかった」という表現は、台帳が一部の特性では逆方向または両方向の関連が非有意としている点を落とし、すべての特性で両方向の関連があったように読めませんか。
- fact F11: 最大標準化交差遅延効果では、収入から協調性への関連は−0.0096、協調性から後の収入への関連は+0.0034で、いずれも約1.25年の間隔で最大だった。協調性から収入への関連は統計的に有意ではなかった。
  scope: 11研究の統合個人内モデル。特性別解析のNは異なる。
  conditions: 報告値は複数の測定間隔にわたる最大の標準化離散時間交差遅延効果。
  numeric_value: 収入→協調性 −0.0096; 協調性→収入 +0.0034 (numeric_scope: それぞれの方向の最大標準化交差遅延効果。協調性→収入の推定は非有意。)
  date_or_period: 最も大きい推定効果は約1.25年の時間間隔
  causal_strength: OBSERVED_REPORTED
  notes_for_writer: 論文の時間集約した個人内モデルでは、収入増加と後の協調性低下の関連を報告。協調性の変化から後の収入への関連は有意ではない。因果効果として表現しない。
- fact F12: 最大標準化交差遅延効果では、収入から開放性への関連は−0.0007、開放性から後の収入への関連は−0.0011で、いずれも約1.20年の間隔で最大だった。両方向とも時間集約モデルでは統計的に有意ではなかった。
  scope: 11研究の統合個人内モデル。特性別解析のNは異なる。
  conditions: 報告値は複数の測定間隔にわたる最大の標準化離散時間交差遅延効果。
  numeric_value: 収入→開放性 −0.0007; 開放性→収入 −0.0011 (numeric_scope: それぞれの方向の最大標準化交差遅延効果。時間集約モデルで両方向とも非有意。)
  date_or_period: 最も大きい推定効果は約1.20年の時間間隔
  causal_strength: OBSERVED_REPORTED
  notes_for_writer: 最大係数の数値だけから有意性を推定しない。論文の結果節では両方向とも非有意。
- fact F13: 性格特性から後の収入への関連と、収入から後の性格変化への関連の推定は、特性により正負が異なる。勤勉性・情緒安定性では両方向が正、外向性では両方向が負、協調性では収入から後の協調性への関連が負で逆方向は非有意、開放性では両方向が非有意だった。
  scope: 統合された個人内縦断モデル
  conditions: 因果方向を確定する実験ではなく、先行値から後続値への交差遅延関連。
  causal_strength: OBSERVED_REPORTED
  notes_for_writer: 「双方向」は両方向に時間的な関連をモデル化したことを指し、すべての特性で両方向の関連が有意だったという意味ではない。
