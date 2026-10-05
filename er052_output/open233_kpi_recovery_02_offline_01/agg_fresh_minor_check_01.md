# fresh MINOR確認(委任_05 事前作業1、¥0)

- 入力: er052_output/open233_stage1_phase1_recall_check_01/a_frozen_fresh_01(32 run、provenance=fresh)
- 全32 runのraw_parsed(モデル出力そのまま)severity分布: {'MAJOR': 40} / post-hoc後: {'MAJOR': 40} / auto_downgraded: 0

| 対象 | instance | runs | MAJOR | MINOR | 指摘なし | run別 |
|---|---|---|---|---|---|---|
| neg5 B3-same (SC, HF-007) | neg5_hormuz_div_a2 | 2 | 0 | 0 | 2 | none,none |
| A4-0 (SC, MUSE-HC-006) | safety_A4 | 4 | 2 | 0 | 2 | none,MAJOR,none,MAJOR |
| HF-011 (monitor, B2_hormuz) | bgroup_B2_hormuz | 2 | 0 | 0 | 2 | none,none |
| B4 non-SC: Meta had run a test (HC-006) | bgroup_B4 | 2 | 1 | 0 | 1 | MAJOR,none |
| B4 non-SC: People feel differently/Names, plans (HC-010) | bgroup_B4 | 2 | 1 | 0 | 1 | MAJOR,none |
| B4 non-SC: As AI makes calls (HC-010/004) | bgroup_B4 | 2 | 0 | 0 | 2 | none,none |
| B4 non-SC: voice sound human (HC-004) | bgroup_B4 | 2 | 0 | 0 | 2 | none,none |

## 判定: MINOR切り捨て(H2)が主因か

- **判定: No(A構成freshの範囲では主因ではない)**【確認】対象文のMINOR出力は計0件。全32 runでMINOR自体が計0件(モデルはV4A promptでMINORを実質出さず、出した指摘は全てMAJOR)。見逃しの実体は「指摘自体なし」であり、MINORに付いて後段へ渡らなかったケースではない。
- 【確認】neg5 B3-sameはfresh 0/2でMAJOR・MINORとも出ず(run_1は別文のHF-008を指摘、run_2は指摘ゼロ)。A4-0はMAJOR 2/4、指摘なし 2/4。
- 【推測】H2(MINOR切り捨て)は構造上の穴として残るが、A構成freshでは顕在化していない。MINORを多く出す構成(Production V0等)では別に確認が必要(本集計の範囲外)。主因は検出自体の非網羅(Opus#16 1-b「迷えば許容」・1-a文またぎ因果)と推測。
