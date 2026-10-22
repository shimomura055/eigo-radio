# Post-EN Risk Flagger Review Queue: paycheck_personality__run_pp_02 / a2

- run_id: `rf20261022T000559Z-2e9f`  status: **OK**
- article_sha256: `2db51c61d5f76b3867969725af74713a6a334e3d10f2e1efe7f2e049b8170489`  ledger_sha256: `a31992b53082d2f143f9b32949dbb926d353c1034a04e2fad666cceca21b0980`
- level: `a2` (b1b=Advanced, a2=Standard)  splitter: `en_split_v1`  producer: `deterministic_v2`  run_label: `FAMILY-X-B3-CORE-NUMBER-ROUNDING-ARTICLE-A-REMAKE-C2`
- sentences: 48  facts: 19  candidate issues: 9

これは**候補一覧**です(合否判定ではありません)。判定はHuman Review側で行います。

## Conditions
- luna A3: OK flags=2 cost_jpy=0.233536 model=gpt-6-luna
- luna A4: OK flags=9 cost_jpy=0.314576 model=gpt-6-luna
- gemini35fl A3: OK flags=0 cost_jpy=0.19876 model=gemini-3.5-flash-lite
- gemini35fl A4: OK flags=0 cost_jpy=0.20452 model=gemini-3.5-flash-lite

## Issues

### s14  (confidence max 0.72)
- issue_id: `paycheck_personality__run_pp_02__a2__2db51c61__rf20261022T000559Z-2e9f__s14`
- sentence: But this series did not compare people with the talented coworker next door.
- before: So this was not one quick look. / The studies followed changes over time.
- after: Each person was compared with their usual self. / The researchers looked separately at differences between people and changes within each person.
- detected_by: luna-A3(0.34), luna-A4(0.72)
- reason [否定反転]: 「did not compare people」と、台帳の「differences between peopleを分けて推定した」は食い違っているのではありませんか。
- reason [その他]: 「did not compare people」と「differences between people and changes within each personを別々に検討した」は食い違うのではありませんか。
- fact F07: 対象研究は、収入とBig Fiveの少なくとも1特性を縦断的に3回以上測定することなどを適格条件とし、解析には個人レベルの変化を扱うランダム切片交差遅延パネルモデルを用いた連続時間メタ分析を行った。
  scope: メタ分析に含めた縦断研究と、統合個人レベルデータの解析
  conditions: 個人レベルデータまたは必要な同時・自己回帰・交差遅延相関情報が得られ、標本数や測定間隔などの記述情報が利用可能であることも条件とした。
  numeric_value: 最低3測定波 (numeric_scope: 一次研究の縦断研究としての適格条件)
  notes_for_writer: モデルは安定した個人間差と個人内の変化を分けて推定する。縦断的な交差遅延関係の推定だけで因果効果が確定するわけではない。

### s17  (confidence max 0.78)
- issue_id: `paycheck_personality__run_pp_02__a2__2db51c61__rf20261022T000559Z-2e9f__s17`
- sentence: They did not ask, “How are you doing compared with other people?”
- before: Each person was compared with their usual self. / The researchers looked separately at differences between people and changes within each person.
- after: Instead, they asked, “How have you changed from your usual self?” / They found that when a person’s income was higher than usual, they were a little more serious about work later.
- detected_by: luna-A3(0.55), luna-A4(0.78)
- reason [否定反転]: 「They did not ask ... compared with other people」と、台帳の「differences between peopleを分けて推定した」は食い違っているのではありませんか。
- reason [その他]: 「did not ask how you are doing compared with other people」と「differences between peopleも扱った」は食い違うのではありませんか。
- fact F07: 対象研究は、収入とBig Fiveの少なくとも1特性を縦断的に3回以上測定することなどを適格条件とし、解析には個人レベルの変化を扱うランダム切片交差遅延パネルモデルを用いた連続時間メタ分析を行った。
  scope: メタ分析に含めた縦断研究と、統合個人レベルデータの解析
  conditions: 個人レベルデータまたは必要な同時・自己回帰・交差遅延相関情報が得られ、標本数や測定間隔などの記述情報が利用可能であることも条件とした。
  numeric_value: 最低3測定波 (numeric_scope: 一次研究の縦断研究としての適格条件)
  notes_for_writer: モデルは安定した個人間差と個人内の変化を分けて推定する。縦断的な交差遅延関係の推定だけで因果効果が確定するわけではない。

### s21  (confidence max 0.3)
- issue_id: `paycheck_personality__run_pp_02__a2__2db51c61__rf20261022T000559Z-2e9f__s21`
- sentence: Think of conscientiousness as being serious about your work.
- before: They found that when a person’s income was higher than usual, they were a little more serious about work later. / The study calls this trait conscientiousness.
- after: They also found that people earned a little more later when they were more serious than usual. / Income and later seriousness were linked.
- detected_by: luna-A4(0.3)
- reason [その他]: 「conscientiousness」と「being serious about your work」を同じ意味として示すのは、台帳にない特性の定義を加えているのではありませんか。
- fact F02: 一次研究はWen-Dong Li、Kaili Yu、Weiwen Yang、Zhen Zhang、Xin Zhang、Christian Dormann、Huanxi Zhang、Yanglei Zhengによる、収入と性格特性の双方向関係を扱った連続時間メタ分析である。
  scope: Psychological Bulletin掲載論文
  numeric_value: 著者8名 (numeric_scope: 論文著者数)
  date_or_period: 2026
  notes_for_writer: 論文のオンライン先行公開日は2026年7月16日。巻号は152巻5–6号、頁は509–543。
- fact F13: 性格特性から後の収入への関連と、収入から後の性格変化への関連の推定は、特性により正負が異なる。勤勉性・情緒安定性では両方向が正、外向性では両方向が負、協調性では収入から後の協調性への関連が負で逆方向は非有意、開放性では両方向が非有意だった。
  scope: 統合された個人内縦断モデル
  conditions: 因果方向を確定する実験ではなく、先行値から後続値への交差遅延関連。
  causal_strength: OBSERVED_REPORTED
  notes_for_writer: 「双方向」は両方向に時間的な関連をモデル化したことを指し、すべての特性で両方向の関連が有意だったという意味ではない。

### s27  (confidence max 0.3)
- issue_id: `paycheck_personality__run_pp_02__a2__2db51c61__rf20261022T000559Z-2e9f__s27`
- sentence: This was not a big story where a pay rise makes you extremely serious!
- before: The road we thought went only one way also had a lane in the other direction. / Still, both links were small.
- after: If you are thinking of a yearly income ranking, set it aside for now. / This is not about serious people earning more than others.
- detected_by: luna-A4(0.3)
- reason [その他]: 「a pay rise makes you」と因果を表す語が、因果関係を確定できないという記述と食い違うのではありませんか。
- fact F08: 最大標準化交差遅延効果では、収入から勤勉性への関連は+0.0630、勤勉性から後の収入への関連は+0.0589で、いずれも約1.30年の間隔で最大だった。
  scope: 11研究の統合個人内モデル。特性別解析のNは異なる。
  conditions: 報告値は複数の測定間隔にわたる最大の標準化離散時間交差遅延効果。
  numeric_value: 収入→勤勉性 +0.0630; 勤勉性→収入 +0.0589 (numeric_scope: それぞれの方向の最大標準化交差遅延効果。単位は標準化されたモデル係数。)
  date_or_period: 最も大きい推定効果は約1.30年の時間間隔
  causal_strength: OBSERVED_REPORTED
  notes_for_writer: 観察された縦断的関連であり、因果効果として表現しない。最大値は該当する時間間隔での推定値。
- fact F15: 著者らは、観察された関係から因果関係を確定できないと明記した。年齢を調整した追加解析では主要な結果・結論は大きく変わらなかったが、年齢以外の第三変数の可能性がなくなるわけではない。
  scope: 一次研究の全縦断分析
  conditions: 追加解析では年齢を統制した。著者らは、因果関係のより強い根拠を得るため、可能であればフィールド実験を提案した。
  causal_strength: OBSERVED_REPORTED
  notes_for_writer: 「収入が性格を変えた」「性格が収入を増減させた」と因果を断定しない。

### s29  (confidence max 0.61)
- issue_id: `paycheck_personality__run_pp_02__a2__2db51c61__rf20261022T000559Z-2e9f__s29`
- sentence: This is not about serious people earning more than others.
- before: This was not a big story where a pay rise makes you extremely serious! / If you are thinking of a yearly income ranking, set it aside for now.
- after: The study looks at changes within the same person. / It is like watching yourself over time, with no one to compete against.
- detected_by: luna-A4(0.61)
- reason [その他]: 「not about serious people earning more than others」と、モデルが人々の間の差も個人内の変化と分けて扱ったことは食い違うのではありませんか。
- fact F07: 対象研究は、収入とBig Fiveの少なくとも1特性を縦断的に3回以上測定することなどを適格条件とし、解析には個人レベルの変化を扱うランダム切片交差遅延パネルモデルを用いた連続時間メタ分析を行った。
  scope: メタ分析に含めた縦断研究と、統合個人レベルデータの解析
  conditions: 個人レベルデータまたは必要な同時・自己回帰・交差遅延相関情報が得られ、標本数や測定間隔などの記述情報が利用可能であることも条件とした。
  numeric_value: 最低3測定波 (numeric_scope: 一次研究の縦断研究としての適格条件)
  notes_for_writer: モデルは安定した個人間差と個人内の変化を分けて推定する。縦断的な交差遅延関係の推定だけで因果効果が確定するわけではない。

### s31  (confidence max 0.48)
- issue_id: `paycheck_personality__run_pp_02__a2__2db51c61__rf20261022T000559Z-2e9f__s31`
- sentence: It is like watching yourself over time, with no one to compete against.
- before: This is not about serious people earning more than others. / The study looks at changes within the same person.
- after: It is also too soon to say, “I became more serious because my pay went up.” / The researchers say these results alone cannot show what caused what.
- detected_by: luna-A4(0.48)
- reason [その他]: 「with no one to compete against」と、モデルが人々の間の差も扱ったことは食い違うのではありませんか。
- fact F07: 対象研究は、収入とBig Fiveの少なくとも1特性を縦断的に3回以上測定することなどを適格条件とし、解析には個人レベルの変化を扱うランダム切片交差遅延パネルモデルを用いた連続時間メタ分析を行った。
  scope: メタ分析に含めた縦断研究と、統合個人レベルデータの解析
  conditions: 個人レベルデータまたは必要な同時・自己回帰・交差遅延相関情報が得られ、標本数や測定間隔などの記述情報が利用可能であることも条件とした。
  numeric_value: 最低3測定波 (numeric_scope: 一次研究の縦断研究としての適格条件)
  notes_for_writer: モデルは安定した個人間差と個人内の変化を分けて推定する。縦断的な交差遅延関係の推定だけで因果効果が確定するわけではない。

### s37  (confidence max 0.27)
- issue_id: `paycheck_personality__run_pp_02__a2__2db51c61__rf20261022T000559Z-2e9f__s37`
- sentence: Low income does not mean you are lazy.
- before: Finding a link does not tell us what caused it. / So you do not need to use your pay slip as a scorecard for how serious you are.
- after: High income does not mean you are a model student. / This study cannot give us such a simple report card.
- detected_by: luna-A4(0.27)
- reason [その他]: 「Low income does not mean you are lazy」と断定することは、収入と性格の関連について台帳が述べる範囲を超えているのではありませんか。
- fact F13: 性格特性から後の収入への関連と、収入から後の性格変化への関連の推定は、特性により正負が異なる。勤勉性・情緒安定性では両方向が正、外向性では両方向が負、協調性では収入から後の協調性への関連が負で逆方向は非有意、開放性では両方向が非有意だった。
  scope: 統合された個人内縦断モデル
  conditions: 因果方向を確定する実験ではなく、先行値から後続値への交差遅延関連。
  causal_strength: OBSERVED_REPORTED
  notes_for_writer: 「双方向」は両方向に時間的な関連をモデル化したことを指し、すべての特性で両方向の関連が有意だったという意味ではない。
- fact F15: 著者らは、観察された関係から因果関係を確定できないと明記した。年齢を調整した追加解析では主要な結果・結論は大きく変わらなかったが、年齢以外の第三変数の可能性がなくなるわけではない。
  scope: 一次研究の全縦断分析
  conditions: 追加解析では年齢を統制した。著者らは、因果関係のより強い根拠を得るため、可能であればフィールド実験を提案した。
  causal_strength: OBSERVED_REPORTED
  notes_for_writer: 「収入が性格を変えた」「性格が収入を増減させた」と因果を断定しない。

### s38  (confidence max 0.27)
- issue_id: `paycheck_personality__run_pp_02__a2__2db51c61__rf20261022T000559Z-2e9f__s38`
- sentence: High income does not mean you are a model student.
- before: So you do not need to use your pay slip as a scorecard for how serious you are. / Low income does not mean you are lazy.
- after: This study cannot give us such a simple report card. / Income may come from a person’s personality.
- detected_by: luna-A4(0.27)
- reason [その他]: 「High income does not mean you are a model student」と断定することは、収入と性格の関連について台帳が述べる範囲を超えているのではありませんか。
- fact F13: 性格特性から後の収入への関連と、収入から後の性格変化への関連の推定は、特性により正負が異なる。勤勉性・情緒安定性では両方向が正、外向性では両方向が負、協調性では収入から後の協調性への関連が負で逆方向は非有意、開放性では両方向が非有意だった。
  scope: 統合された個人内縦断モデル
  conditions: 因果方向を確定する実験ではなく、先行値から後続値への交差遅延関連。
  causal_strength: OBSERVED_REPORTED
  notes_for_writer: 「双方向」は両方向に時間的な関連をモデル化したことを指し、すべての特性で両方向の関連が有意だったという意味ではない。
- fact F15: 著者らは、観察された関係から因果関係を確定できないと明記した。年齢を調整した追加解析では主要な結果・結論は大きく変わらなかったが、年齢以外の第三変数の可能性がなくなるわけではない。
  scope: 一次研究の全縦断分析
  conditions: 追加解析では年齢を統制した。著者らは、因果関係のより強い根拠を得るため、可能であればフィールド実験を提案した。
  causal_strength: OBSERVED_REPORTED
  notes_for_writer: 「収入が性格を変えた」「性格が収入を増減させた」と因果を断定しない。

### s40  (confidence max 0.36)
- issue_id: `paycheck_personality__run_pp_02__a2__2db51c61__rf20261022T000559Z-2e9f__s40`
- sentence: Income may come from a person’s personality.
- before: High income does not mean you are a model student. / This study cannot give us such a simple report card.
- after: But it can also help us think about how their personality may change later. / From “Who earns the most?”
- detected_by: luna-A4(0.36)
- reason [その他]: 「Income may come from a person’s personality」と因果の向きを示す表現は、因果関係を確定できないという記述と食い違うのではありませんか。
- fact F13: 性格特性から後の収入への関連と、収入から後の性格変化への関連の推定は、特性により正負が異なる。勤勉性・情緒安定性では両方向が正、外向性では両方向が負、協調性では収入から後の協調性への関連が負で逆方向は非有意、開放性では両方向が非有意だった。
  scope: 統合された個人内縦断モデル
  conditions: 因果方向を確定する実験ではなく、先行値から後続値への交差遅延関連。
  causal_strength: OBSERVED_REPORTED
  notes_for_writer: 「双方向」は両方向に時間的な関連をモデル化したことを指し、すべての特性で両方向の関連が有意だったという意味ではない。
- fact F15: 著者らは、観察された関係から因果関係を確定できないと明記した。年齢を調整した追加解析では主要な結果・結論は大きく変わらなかったが、年齢以外の第三変数の可能性がなくなるわけではない。
  scope: 一次研究の全縦断分析
  conditions: 追加解析では年齢を統制した。著者らは、因果関係のより強い根拠を得るため、可能であればフィールド実験を提案した。
  causal_strength: OBSERVED_REPORTED
  notes_for_writer: 「収入が性格を変えた」「性格が収入を増減させた」と因果を断定しない。
