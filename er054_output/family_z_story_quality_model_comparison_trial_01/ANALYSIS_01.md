# ANALYSIS_01 (委任_02 実評価 gpt-6-luna 12作品x4方式xN=2)

本書は機械集計。『候補』は確定判定ではなく、Claude/人が根拠の妥当性を確認する(AI評価だけで最終FIXしない)。

- 解析対象: 成功96件 / 失敗・欠損0件 / actual model_id: ['gpt-6-luna']

## 1. 極端結果の検出

- 方式A: 検出なし
- 方式B: 検出なし
- 方式C: 検出なし
- 方式D: 検出なし

## 2. 再現性(同一方式N回の差=LLMゆらぎ)

| 方式 | 作品ペア数 | rep間の差の平均(0-1) | 最大 | 軸一致率 | Spearman(rep1,rep2) |
|---|---|---|---|---|---|
| A | 12 | 0.021 | 0.125 | 0.875 | 0.84 |
| B | 12 | 0.031 | 0.125 | 0.938 | 0.54 |
| C | 12 | 0.036 | 0.062 | 0.854 | 0.64 |
| D | 12 | 0.042 | 0.188 | 0.833 | 0.77 |

切り分け: 同一方式のrep間差=LLMゆらぎ、方式間の順位差=Prompt/基準差。rep間の順位相関が高く方式間相関が低ければPrompt設計差、rep間相関自体が低ければLLM能力/ゆらぎ。

## 3. 方式間で順位が大きく割れる作品

- L02: 順位差8.5 {'A': 4.5, 'B': 12.0, 'C': 3.5, 'D': 6.0}
- L07: 順位差8.5 {'A': 8.0, 'B': 8.0, 'C': 1.5, 'D': 10.0}
- L12: 順位差8.0 {'A': 9.5, 'B': 3.5, 'C': 1.5, 'D': 7.5}
- L13: 順位差7.0 {'A': 1.0, 'B': 1.5, 'C': 8.0, 'D': 1.0}
- L09: 順位差6.5 {'A': 4.5, 'B': 8.0, 'C': 11.0, 'D': 9.0}

## 4. L05(交尾)の方式別評価

- 方式A: 正規化0.69 順位12.0 軸別={'A': [4.0, 4.0], 'B': [4.0, 4.0], 'C': [4.0, 5.0], 'D': [3.0, 2.0]}
- 方式B: 正規化0.88 順位8.0 軸別={'A': [2.0, 2.0], 'B': [2.0, 2.0], 'C': [2.0, 2.0], 'D': [1.0, 1.0]}
- 方式C: 正規化0.75 順位12.0 軸別={'hook': [4.0, 4.0], 'development': [4.0, 4.0], 'aftertaste': [4.0, 4.0], 'originality': [4.0, 4.0]}
- 方式D: 正規化0.47 順位11.5 軸別={'extractability': [4.0, 4.0], 'loss_severity': [2.0, 2.0], 'reproducibility': [3.0, 4.0], 'style_independence': [2.0, 2.0]}

## 5. 根拠とスコアの矛盾候補(機械抽出)

候補33件(弱点語彙判定は文脈を見ないため偽陽性を含む)。

- 方式A L01 rep1 [weak_word_vs_high_score] A: 高評価なのに弱点語彙 ['困難']
- 方式A L01 rep1 [weak_word_vs_high_score] D: 高評価なのに弱点語彙 ['削る', '失われ']
- 方式A L01 rep2 [weak_word_vs_high_score] D: 高評価なのに弱点語彙 ['失われ']
- 方式A L02 rep1 [weak_word_vs_high_score] D: 高評価なのに弱点語彙 ['削る']
- 方式A L02 rep2 [weak_word_vs_high_score] D: 高評価なのに弱点語彙 ['削る']
- 方式A L07 rep2 [weak_word_vs_high_score] B: 高評価なのに弱点語彙 ['消え']
- 方式A L07 rep2 [weak_word_vs_high_score] C: 高評価なのに弱点語彙 ['消え']
- 方式A L09 rep1 [weak_word_vs_high_score] D: 高評価なのに弱点語彙 ['薄れ']
- 方式A L10 rep1 [weak_word_vs_high_score] D: 高評価なのに弱点語彙 ['削る']
- 方式A L10 rep2 [weak_word_vs_high_score] D: 高評価なのに弱点語彙 ['削る', '失われ']
- 方式A L12 rep2 [weak_word_vs_high_score] D: 高評価なのに弱点語彙 ['薄れ']
- 方式B L05 rep1 [weak_word_vs_high_score] A: 高評価なのに弱点語彙 ['弱い']
- 方式B L07 rep1 [weak_word_vs_high_score] B: 高評価なのに弱点語彙 ['失う']
- 方式B L07 rep1 [weak_word_vs_high_score] C: 高評価なのに弱点語彙 ['失う']
- 方式B L07 rep2 [weak_word_vs_high_score] B: 高評価なのに弱点語彙 ['失う']
- 方式B L11 rep2 [weak_word_vs_high_score] C: 高評価なのに弱点語彙 ['薄れ']
- 方式B L12 rep1 [weak_word_vs_high_score] D: 高評価なのに弱点語彙 ['薄れ']
- 方式B L13 rep1 [weak_word_vs_high_score] D: 高評価なのに弱点語彙 ['難し']
- 方式C L02 rep2 [weak_word_vs_high_score] hook: 高評価なのに弱点語彙 ['失い']
- 方式C L04 rep2 [weak_word_vs_high_score] development: 高評価なのに弱点語彙 ['失い']
- 方式C L07 rep1 [weak_word_vs_high_score] development: 高評価なのに弱点語彙 ['薄れ']
- 方式C L07 rep1 [weak_word_vs_high_score] aftertaste: 高評価なのに弱点語彙 ['失う']
- 方式C L07 rep2 [weak_word_vs_high_score] development: 高評価なのに弱点語彙 ['失われ']
- 方式C L07 rep2 [weak_word_vs_high_score] aftertaste: 高評価なのに弱点語彙 ['失う']
- 方式C L07 rep2 [weak_word_vs_high_score] originality: 高評価なのに弱点語彙 ['薄れ']
- 方式C L09 rep2 [weak_word_vs_high_score] originality: 高評価なのに弱点語彙 ['失う']
- 方式C L13 rep1 [weak_word_vs_high_score] development: 高評価なのに弱点語彙 ['失われ']
- 方式D L01 rep1 [lost_high_vs_overall] overall: severity=high2件なのに総合4
- 方式D L01 rep2 [lost_high_vs_overall] overall: severity=high2件なのに総合4
- 方式D L04 rep1 [lost_high_vs_overall] overall: severity=high2件なのに総合4
- 方式D L08 rep1 [lost_high_vs_overall] overall: severity=high2件なのに総合4
- 方式D L09 rep1 [weak_word_vs_high_score] reproducibility: 高評価なのに弱点語彙 ['削る']
- 方式D L13 rep1 [weak_word_vs_high_score] style_independence: 高評価なのに弱点語彙 ['薄れ']

## 6. 引用の文字列一致率(原作理解の誤りとは別集計)

| 方式 | 引用数 | 不一致 | 一致率 |
|---|---|---|---|
| A | 188 | 18 | 0.904 |
| B | 192 | 7 | 0.964 |
| C | 189 | 10 | 0.947 |
| D | 192 | 17 | 0.911 |

不一致の内訳: {'near': 41, 'absent': 11}(near=表記ゆれ・軽微な欠落、absent=原文に存在しない)。

## 7. 原作理解の誤り候補(機械抽出。確定は人/Claude)

- [character_not_in_source] A L01 王ディオニス
- [character_not_in_source] A L01 メロスの妹
- [character_not_in_source] A L01 王ディオニス
- [character_not_in_source] A L01 メロスの妹
- [character_not_in_source] A L02 髪を抜かれる死人の女
- [character_not_in_source] A L03 白熊のような二匹の犬
- [character_not_in_source] A L03 山猫軒の主人や店の者たち
- [character_not_in_source] A L03 白熊のような二匹の犬
- [character_not_in_source] A L03 山猫軒の奥にいる者たち
- [character_not_in_source] A L04 若い法律家（賭けの相手で、十五年間監禁される）
- [character_not_in_source] A L04 老銀行家（賭けを持ちかけ、期限直前に法律家を殺そうと考える）
- [character_not_in_source] A L04 老銀行家
- [character_not_in_source] A L04 若い法律家（囚人）
- [character_not_in_source] A L05 病身の語り手
- [character_not_in_source] A L05 路地の二匹の白猫
- [character_not_in_source] A L05 雄と雌の河鹿
- [character_not_in_source] A L05 病気の語り手
- [character_not_in_source] A L05 雄と雌の河鹿
- [character_not_in_source] A L07 李徴の妻子
- [character_not_in_source] A L08 喜助：貧しい暮らしの末、苦しむ弟の願いに応じて剃刀を抜き、弟を死なせた罪人。
- [character_not_in_source] A L08 羽田庄兵衛：喜助を護送する同心。喜助の話を聞き、自分の暮らしや罪の判断を考える。
- [character_not_in_source] A L08 喜助の弟：病気で苦しみ、兄に剃刀を抜いてくれるよう頼む。
- [character_not_in_source] A L08 喜助の弟
- [character_not_in_source] A L09 二人の若い土工
- [character_not_in_source] A L09 良平の弟と隣の子供
- [character_not_in_source] A L09 良平の両親
- [character_not_in_source] A L09 良平の弟と隣の子供
- [character_not_in_source] A L09 若い土工二人
- [character_not_in_source] A L09 良平の両親
- [character_not_in_source] A L10 どんぐりたち
- [character_not_in_source] A L10 どんぐりたち
- [character_not_in_source] A L11 語り手
- [character_not_in_source] A L11 語り手の「私」
- [character_not_in_source] A L11 友人たち（下宿の背景として登場）
- [character_not_in_source] A L12 語り手
- [character_not_in_source] A L12 死を告げ、百年後の再会を約束する女
- [character_not_in_source] A L12 女を見送り、墓のそばで待つ語り手
- [character_not_in_source] A L13 蜘蛛の糸を上る罪人たち
- [character_not_in_source] A L13 糸を上る罪人たち
- [character_not_in_source] B L01 メロスの妹
- [character_not_in_source] B L01 メロス：王の暴政に憤り、友との約束を守ろうとする牧人
- [character_not_in_source] B L01 セリヌンティウス：メロスを信じて人質となる石工
- [character_not_in_source] B L01 ディオニス：人を信じられず暴政を行う王
- [character_not_in_source] B L01 メロスの妹とその花婿
- [character_not_in_source] B L02 老婆が髪を抜いていた女の死骸
- [character_not_in_source] B L02 老婆が髪を抜いていた死人の女
- [character_not_in_source] B L03 二疋の犬
- [character_not_in_source] B L03 山猫軒の奥にいる者たち
- [character_not_in_source] B L03 二疋の猟犬
- [character_not_in_source] B L03 山猫軒の主人と声の主たち
- [character_not_in_source] B L04 銀行家
- [character_not_in_source] B L04 若い法律家
- [character_not_in_source] B L04 銀行家。賭けの期限が近づくと、支払いで破産することを恐れ、法律家を殺そうと考える。
- [character_not_in_source] B L04 若い法律家。孤独な監禁の中で多様な本を読み、最後には富や世俗の価値を拒絶する。
- [character_not_in_source] B L05 病気を抱えた語り手
- [character_not_in_source] B L05 路地で交尾する二匹の白猫
- [character_not_in_source] B L05 渓流で求愛する雄と雌の河鹿
- [character_not_in_source] B L05 路地を巡回する夜警
- [character_not_in_source] B L05 語り手
- [character_not_in_source] B L05 雄の河鹿

## 8. 運用(時間・費用)

| 方式 | calls | 平均秒 | 平均出力tok | 実費(円) |
|---|---|---|---|---|
| A | 24 | 13.48 | 1487.0 | 5.145 |
| B | 24 | 17.77 | 1900.0 | 5.941 |
| C | 24 | 13.33 | 1359.0 | 4.851 |
| D | 24 | 19.66 | 1908.0 | 6.017 |

## 9. 人間確認推奨作品

- 各方式の最高/最低: A: 最高L13/最低L05; B: 最高L03/最低L02; C: 最高L07/最低L05; D: 最高L13/最低L05
- 割れ作品: ['L02', 'L07', 'L12', 'L13', 'L09']
- 常に確認: ['L05'](重要検証対象『交尾』)

## 10. 推奨・次点・不採用(人/Fableが記入。雛形)

- 最有望: (未記入)
- 次点: (未記入)
- 不採用: (未記入、理由付き)
- 限界・追加検証条件: (未記入)
