# ADOPTION_NOTE_01 (Production採用する場合の必要作業・影響範囲。**未承認・参考**。Trial結果は`TRIAL_RESULT_01.md`)

Status(Sonnet所見): 採用判断前。Phase 1でアームAは事前登録基準を満たさず(2本中1本)、Phase 2未実施。以下は「採用する場合」に必要になる作業の整理であり、採用推奨ではない。

## 1. 変更が必要になるファイル(Family X専用。Z/Yは到達させない)
| 機能 | 変更候補ファイル | 分類 |
|---|---|---|
| B3追記ブロック(Storylineに答えの数値<=2) | `er019_family_x_storyline_b3_fact_selection_01.py`(`USER_PROMPT_TEMPLATE`の追記)またはrunnerのextra_note | J1: B3 Promptの意味的変更=ユーザー承認事項 |
| M1検査(Storyline数値の検証・B3再実行1回)・E導出 | 新module(`derive_E`相当)+`er019_family_x_entertainment_production_runner_01.py`のB3段後 | 新規 |
| 範囲値正規化(入力側R4) | `er053_family_x_factlock_ja_writer_01.py`の`run_w1_writer`(ニュース欄・テーマ行) | J2(承認済み規則同士の矛盾の是正) |
| 範囲値正規化(**出力側**R1/R2) | `er053_family_x_factlock_ja_writer_01.py`の`astra_stage` | **新規(Opus未レビュー)**。記号QAのSTOPを避けるために必須(実測) |
| 保持Gate(R0/R1/R2)・段限定再実行・STOP | `er053_family_x_factlock_ja_writer_01.py` | J3: STOP→HRの既定をユーザー判断 |
| 較正済み照合・単位言い換え表 | 新module(`match_core`) | 新規 |
| 計測(選定数/必要数/掲載数/不要数) | `er114`/`er115` | 運用ツール |
| CURRENT_SPEC.md / DECISION_LOG.md / OPEN_ITEMS.md | 規則5(許可のみ→Eは必須)、B3契約、範囲値規則 | ドキュメント |

## 2. 影響範囲・確認事項
- B3 PromptファイルはFamily Xの名前だがY Trial(`er036_family_y_voice_structure_trial_01.py:33`ほか)から多数importされている(Opus所見)。Productionに入れる場合は、Y/ZのProduction経路が`USER_PROMPT_TEMPLATE`/`selected_storyline`を使っていないことのGrepをIsolation testに含める。追記型でOFF時バイト一致を保てば撤退は`git revert`で容易。
- 既存公開記事は不変(再生成しない限り)。月のProduction再実行は採用判断後。
- Isolation test(採用時): (a)OFF時`build_r0_prompt`バイト一致、(b)Z/Yのimport・参照0のGrep、(c)flag未設定でAPI呼出0・出力不変(DefaultOffIsolation型)、(d)起動script/.envで暗黙にONにしない。
- 量産単価増分: `TRIAL_RESULT_01.md` §4(実測ベース)。HR増加量はSTOP率(Phase 1: Gate由来のSTOP 0/3、記号QA由来のSTOP 2/2[出力側正規化導入前])。

## 3. 採用前に残る課題(Trial結果より)
1. **非E中核数値の扱い**(約750 mが4/5標本で中核、2/5でStoryline入り、2/2フルチェーンで掲載)。Eだけでは「必要十分」にならない。選択肢: (a)B3追記ブロックに『比較対象の値は文で述べ数値はStorylineに入れない』を足す、(b)E非空のときだけ非E中核をWriter向けに周辺扱いにする(規則5の運用変更)、(c)現状のまま過剰掲載は許容し人手判定。いずれもユーザー判断/新仕様(未Trial)。
2. R1がニュース欄にない数値(約45 m)を足す事例(B/s1、1/3)。既存R1挙動で本Trialの責務外だが、周辺数値混入の監視指標として記録。
3. n小(フルチェーン3本、B3 5本)。Phase 2(過去記事3本)は未実施。
