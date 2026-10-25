# COMPARISON_07(Before=03d/06、After=07。Step B未実行のためStep B全文なし)

管理ID: FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_12 / 日付: 2026-10-25 / Status: DEV/Trial専用。評価はFable。

## 1. 工程比較
| 項目 | 03d(一括生成) | Trial-06 | Trial-07 |
|---|---|---|---|
| Part 2の選定 | Writer LLMが文を選び同時に解説(2件) | LLMは全文分類のみ、コードが2段クラス・固定優先順位で最大2件 | LLMは全文分類+`front_kind`+`teaching_value`、コードが固定優先順位で**最大1件・適格0なら0件** |
| 件数の扱い | 常に2件 | 常に2件選びやすい(適格があれば) | 適格がなければ0件(件数を満たすための選定なし) |
| 学習価値 | 暗黙(LLM任せ) | 欄なし | `teaching_value`=HIGH+`teaching_value_ja`が適格条件 |
| FRONTの採否 | - | 定義と基礎項目が矛盾(許容集合外14件中10件) | `front_kind`で明文化(単純な文頭配置は基礎、複雑な文頭要素は適格) |
| 引用連結 | - | 開いた窓r2で連結→resolve失敗→中核脱落 | Prompt禁止+`resolve7`+`verify_single_span`+回帰テスト |
| 標本・費用 | 5 call 1.376円(追補) | 18 call 8.855円 | 18 call 5.984円 |

## 2. 選定結果の比較(Step A'')
`EVAL_07.md` §2・§5のとおり。許容集合外の選定は Trial-06の14件→Trial-07の1件。難所のある6作品の全標本で中核を選定(0件・許容集合外なし)、二十年後は0件で正しく処理。走れメロスr1の1件(POSTMOD)のみ事前登録上の不合格。

## 3. Step B全文
**Step Bは実行していない**(`PREREGISTERED_CRITERIA_07.md` §4・§5: Step A''不合格のためStep B非実行)。Step Bの品質はTrial-04(`EVAL_04.md`)の評価が有効なまま(PromptはTrial-04と同一で、入力の選定文が変わるだけ)。したがって、Trial-07の選定が1件になった場合のStep B全文(4点解説)の実物は、本Trialでは取得していない(未確認)。
