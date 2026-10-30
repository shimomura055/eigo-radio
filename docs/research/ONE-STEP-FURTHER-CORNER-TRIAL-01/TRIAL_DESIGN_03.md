# TRIAL_DESIGN_03: One Step Further 最終再設計Trial(委任_03、2026-10-30)

原文: `docs/pm/delegation_log/2026-10-30_ONE-STEP-FURTHER-CORNER-TRIAL-01_USER_03.md`。工程は原文§5のStep1〜5をそのまま実装した。Trial専用(`tools/osf03_*.py`)、Production非変更。

## 工程
| Step | 実装 | 入力 | モデル | 機械検査 |
|---|---|---|---|---|
| 1 抽出 | `osf03_run.py extract*` / Prompt `EXTRACT` | 文番号付き本文・レベル・既存KP/Word/文法 | gpt-6-luna(R1,R2)、gpt-6.1-sol(R3) | 引用の本文実在、範囲が引用内、原型の語がターゲット由来、否定/法助動詞の保持、KP/文法との核重複(KP_REUSE_01.md) |
| 2 生成 | `gen_family`/`gen_r3` / Prompt `GEN` | **原型+意味+保持要素+レベル+選定基準のみ**(記事全文・人物心理なし) | gpt-6.1-sol(推論low) | 長文化のみ・元文を残して延長・語順入替・KP重複。単語1つ差はフラグ(良例①も該当のため棄却せず監査へ) |
| 3 Gate A | `gate_a` / `AUDIT_A` | 基本/発展と同一場面の置換文(frame)、保持要素、既存学習項目 | gemini-4-argon(別ベンダー) | 欠陥コード8種(主語対象/情報追加/肯否法助動詞/意味の飛躍/長文化のみ/単語置換のみ/置換不可/不自然/重複)+差の記録+実用上の差(dp) |
| 4 Gate B | `gate_b` / `AUDIT_B` | Gate A通過のみ | gemini-4-argon | 発見・使いたい・場面の広さ・レベル・説明の明瞭さ(1-5)+旗。閾値 d,w,l,c≥4・b≥3・旗なし |
| 5 最終確認 | `final_stage` / `FINAL` | 本文(6記事)+候補 | gemini-4-argon | 引用/範囲/原型/意味の再確認、本文の文へ置換した文の自然さ・同義性、欠陥コード再検査。PASS+B閾値の候補を各レベル最大2件。無ければ0件 |

## 独立性
生成=OpenAI系(sol)、監査=Google系(argon、補助3.1pro)。監査Promptの欠陥例は前回NG5類型と別の例(回帰セットの答えを漏らさない)。

## 回帰セット(合格の前提条件)
原文§4のNG5例+前回主候補7件+良例①②③=15件をGate Aに入力。argonで NG5/5・前回7/7=FAIL、①=PASS_WITH_DIFF、②=PASS_WITH_DIFF(差を記録、無条件PASSではない)、③=FAIL(意味の変化を検出)。3.1proは前回P03・P05を見逃したためGate Aの決定には使わない。検出できない検査器は合格にしない、という条件はargonで満たした。

## 改善の反復(委任文の制約への適合)
- 検査器の欠陥修正: (1)監査Promptのコンパクト化+「何を言うかが変わる差はPASS_WITH_DIFFにしない」規則(P03見逃し対応、1回)、(2)Gemini client初期化競合の修正、(3)機械検査の不規則活用表・否定語の扱い。
- 生成Prompt再設計: 0回(1版のみ)。ただし抽出は不足レベル(X Std/Adv, Y Adv)に対し第2・第3ラウンドを実施(Step5「別の基本表現を探す」)。
