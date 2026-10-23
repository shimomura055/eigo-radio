# Fable CPチェックリスト(機械生成: the_open_window、essentials sha 5e624b717d97)

各行の『本文の該当引用』欄にstage別の本文引用(逐語)を記入する。引用できない=欠落。判定・記入はCP担当(Fable/Sonnet記入→Fable確認)。

処置規則(ユーザー承認2026-10-23): (A)重大=ending_reveal・key_roles(keep_name人物の脱落/他人名の増加)・key_causality・setups_and_payoffsのいずれかの欠落 -> CP不合格。TTS前に修正(Writer再実行=承認済みの明示--regenerate-stage、または決定論パッチ)し、原因分析を記録し、C案(軽量事後確認)要否をユーザーへ提示する(報告で`判断候補`)。(B)軽微=結末直前の付加文など、結末前の示唆(withhold_until_end)を希釈する不要文のみ -> 決定論の削除パッチ(exact文字列の削除)を適用し、削除した文・理由・前後sha・対象stageを記録する。所見を処置せずTTSへ進めてはならない。自動判定・LLM検査・retry・Human Reviewは無い。

| # | 深刻度 | 項目 | 内容 | 本文の該当引用(r0) | 本文の該当引用(r1) | 本文の該当引用(r2) | 本文の該当引用(std_adjust) | 判定 |
|---|---|---|---|---|---|---|---|---|
| 1 | 重大 | ending_reveal(種明かしが最終に在る) | The story ends by showing that the girl, Vera, is someone who invents convincing stories on the spur of the moment: her last smooth lie about why Framton ran away proves that her tragic ghost story was invented too. [原作最終文: Romance at short notice was her speciality.] |  |  |  |  |  |
| 2 | 軽微 | withhold_until_end(結末前の示唆・結末直前の付加文が無い) | Before the ending, do not hint at or explain that Vera's story about the open window is invented. |  |  |  |  |  |
| 3 | 重大 | setup と payoff | Vera's sad story: three years ago the aunt's husband and her two young brothers walked out through the open window and were lost in a bog; the aunt still keeps the window open; details are the husband's white coat, the youngest brother's song 'Bertie, why do you bound?' and the brown spaniel.  ->  At dusk three figures with guns, a white coat and a spaniel cross the lawn and the song is heard; Framton runs away in terror; the men walk in, ordinary and muddy. |  |  |  |  |  |
| 4 | 重大 | key_role keep_name=Framton(名前が維持され他人名が増えていない) | the nervous visitor and main character, who flees in terror |  |  |  |  |  |
| 5 | 重大 | key_role keep_name=Vera(名前が維持され他人名が増えていない) | the aunt's fifteen-year-old niece, who tells the false ghost story and then lies smoothly about the dog |  |  |  |  |  |
| 6 | 重大 | key_role(役割・関係で表され名前が付いていない) | the girl's aunt, whose cheerful waiting for the men seems to confirm Vera's story |  |  |  |  |  |
| 7 | 重大 | key_causality | Vera's invented tragedy makes Framton believe the men are ghosts; the aunt's cheerful behavior seems to confirm it; the men's return makes Framton flee in terror; Vera then invents another story to explain why he ran. |  |  |  |  |  |

## 各stageの最終段落(機械抽出、参考。結末直前の付加文の有無はこの直前段落も確認)

### r0(段落数29、語数425)
- 最終段落: Romance at short notice was her speciality.
- 最終の直前段落: “It was the spaniel,” Vera said calmly. “He told me he was terrified of dogs. In India, a pack chased him into an empty grave. He spent the night there, with the dogs snarling above him. A rather unpleasant cure for sleeplessness.”

### r1(段落数29、語数422)
- 最終段落: Inventing convincing stories at a moment’s notice was Vera’s speciality.
- 最終の直前段落: “It was the spaniel,” Vera said calmly. “He told me he was terrified of dogs. In India, a pack chased him into an empty grave. He spent the whole night there while they snarled above him. He couldn’t bear the sight of another dog.”

### r2(段落数29、語数434)
- 最終段落: Inventing convincing stories at a moment’s notice was Vera’s speciality.
- 最終の直前段落: “It was the spaniel,” Vera said calmly. “He told me he was terrified of dogs. In India, a pack chased him into an empty grave. He spent the whole night there, with them snarling above him.”

### std_adjust(段落数29、語数422)
- 最終段落: Vera needed only seconds to invent a story people believed.
- 最終の直前段落: “The dog frightened him,” Vera said, sounding perfectly calm. “He told me dogs terrified him. A group chased him into an empty grave in India. He stayed there all night while they growled above him.”

