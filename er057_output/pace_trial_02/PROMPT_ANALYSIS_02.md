# PROMPT_ANALYSIS_02
## F5全文(基準)
`warm, gently upbeat and engaging; natural, friendly delivery with a light sense of energy, while maintaining clear and credible news narration. Tell it like a short story to a friend, with a relaxed flow and a lively, natural rhythm; not hurried.`

## 速度に影響していそうな指示(仮説。実測で検証する)
| 語句 | 位置 | 速度への推定影響 | 表情への推定寄与 |
|---|---|---|---|
| gently upbeat | 前半 | 中(upbeat=軽快・前向きなテンポを誘導しやすい) | 高(明るさの核) |
| engaging | 前半 | 小 | 中 |
| light sense of energy | 前半 | 中〜大(energy=活発・速い発話を誘導) | 高 |
| news narration | 前半 | 小〜中(ニュース読みは一般に速め) | 信頼感 |
| Tell it like a short story to a friend | 後半 | 中(友人への語り=会話速度、口語の速さ) | 高(親しみ) |
| relaxed flow | 後半 | 小(flow=滑らかに連続=ポーズが少なくなる側にも働く) | 中 |
| lively, natural rhythm | 後半 | 中〜大(lively/rhythmはテンポ誘導) | 高 |
| not hurried | 後半 | 小(否定形は弱い) | - |
前回(PACE-01)の知見: 後半1文のみの置換では合計WPMが208.6->195〜203に留まり、効いたのは calm/composed/measured(PC1)、settle softly(PC4)、measured deliberate cadence(PC8)。前半の upbeat/energy は温存していたため、減速が限定的だった可能性がある。今回は前半も含め全体を再構成する。

## 8候補の設計(調整思想)
| 候補 | 調整思想 | 調整理由 |
|---|---|---|
| PD1 | ニュースナレーション指示の全体再構成 | upbeat/energy/livelyを全て落とし「落ち着いた報道キャスター+gentle smile」でトーンを保つ。PC1の効果を前半にも適用。 |
| PD2 | テンポ誘導語の除去(削除型) | テンポ・エネルギー語を一切足さず削る。減速指示なしで語彙の削除だけでどこまで落ちるか(因果の切り分け)。表情語(warm, expressive, smile)は残す。 |
| PD3 | 意味単位での間 | 「アイデアが終わる所・コンマ・文間」で短く間を置く指示で息継ぎを増やす。bright, warm toneで暗さ防止。 |
| PD4 | Podcastホスト調 | 役割を変える。confident/savoring(味わう)で驚きの場面に余裕を持たせ、「次の行へ急がない」。 |
| PD5 | 余裕のある語り(明るさ維持) | 「時間がたっぷりある」余裕+key moments呼吸。「slow/sleepyにしない」ガードで低テンション化回避。 |
| PD6 | 聞き手への語りかけ+落ち着き | 朝のラジオホスト像=calm, steady, reassuring。1人への語りかけで過度な高速を抑える。 |
| PD7 | 文間呼吸+局所緩急 | 全体は温かいニュース調のまま、文間の息継ぎと引用・数字のみ緩める。全体を遅くせず局所で整える。 |
| PD8 | ラジオ・フィーチャー調 | unhurried+full vowels(母音を十分に)+richly expressive。発声そのものを丁寧にする方向。flat/sleepy防止。 |
共通: 数値WPM・倍率なし、「ゆっくり読め」だけのPromptなし、教材調一語区切りの誘導なし、置換・削除中心で全案F5より短い(112〜182字、F5 246字)。
