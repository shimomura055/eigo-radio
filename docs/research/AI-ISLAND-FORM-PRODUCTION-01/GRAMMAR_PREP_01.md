# GRAMMAR_PREP_01 文法解説の「今回記事限り・暫定」事前生成(AI-ISLAND-FORM-PRODUCTION-01 委任_01)

**位置づけ(混同禁止)**: ユーザー指示2026-10-27 §4の「正式配線が未完成の場合、承認済み品質仕様を保ったまま今回の記事に限り選定前に解説を準備する」に基づく**暫定運用**。GRAMMAR-PREGEN-ALL-LEVELS-01(正式配線、OPEN-559/560系)の**PRODUCTION_WIRED判定とは無関係**。`production_connected`はfalseのまま、Production run dirは未改変。

## 方式
- 使用関数: GRAMMAR-PREGEN委任_02 commit `b27d88309`(origin/main)の`er119_kp_human_review_01`/`er119_grammar_review_01`/`er120_part2_grammar_production_01`/`er120_part2_wiring_01`を`git show`で固定版import(並行Agentの作業ツリー編集の影響なし)。`candidate_and_pregen_stage`(= Step A''候補抽出 → 全候補Step B事前生成、PREGEN_MAX=8、`ref_ja=None`)をそのまま呼ぶ。Prompt/model/閾値/Validatorは無変更(blob sha256を`grammar_prep_out/summary_<level>.json`に記録)。
- Prompt sha: Step A'' `51912fe1e241…`(STEPA)、Step B `59588b5961e8…`(STEPB)。model=gpt-6-luna(`routing.SUPPORT_MODEL`、応答モデル一致)。
- ツール: `docs/research/AI-ISLAND-FORM-PRODUCTION-01/tools/grammar_prep_01.py`。出力: `grammar_prep_out/<level>/study_text/{grammar_candidates.json, grammar_explanations.json(grammar_explanations_v1), grammar_human_review.json(v2 PENDING), grammar_human_review_request.md, form_grammar_bundle.json}`。

## 結果
| level | 候補 | 解説(Step B) | Step A'' | 新規費用 |
|---|---|---|---|---|
| Standard(a2) | **4件**(T1: 比較省略×3[did better / one step ahead / did better,and…]・長い主語×1) | 4件全部 `source=pregen` | 新規抽出1 call(¥0.4165) | ¥0.7047 |
| Advanced(b1b) | **3件**(T1: what節主語・関係節を含む長い主語・that節複合主語) | 3件全部 `source=pregen` | 旧run_ai_01の候補doc再利用(API 0) | ¥0.1683 |
- 全`validate_explanations`(sha・signature・構造・digest・完全性)通過。`form_grammar_bundle`(SCHEMA_CONTRACT_01 §5)は`candidates_available`、`n_not_generated=0`(PREGEN_MAX超過なし)。
- 各解説は【日本語訳】/【文法・構文の仕組み】/(【通常の表現・語順との比較】)/【意味・ニュアンス・表現効果】の承認済み構造。全文をフォームで表示。ユーザー提示後に再生成しない(選定後は凍結値として使用=委任_02)。
- 例(Adv 1位 `gcc2541c879` what節主語): 「島は以前の状態に戻ったが、AIが発見したことは消去されなかった。」+構文解説(全455字)。

## 品質上の観察(報告のみ。Prompt/基準は変更していない)
1. Standard候補3件の見出しが同じ『比較対象が省略された比較表現』。フォームには例文が併記されるため区別できるが、見出しだけでは判別しにくい(Step A'' construct_ja の仕様)。
2. Advの解説訳(【日本語訳】)とPart 1(T1)訳の食い違いは、選定後finalizeの`translation_issues`(SCHEMA_CONTRACT_01 §6、ISSUE rc=4)で検査される。本委任では未検査(選定後=委任_02で対応。食い違い時は別候補/省略/ユーザー了承のいずれか)。
3. HR(Human Review)は省略しない: 解説全文をフォームでユーザーが読んで選定する(=HR)。AIによる選定代行なし。

## 再現
`.venv\Scripts\python.exe docs\research\AI-ISLAND-FORM-PRODUCTION-01\tools\grammar_prep_01.py --level a2 --out docs\research\AI-ISLAND-FORM-PRODUCTION-01\grammar_prep_out --budget-jpy 6`
`... --level b1b --reuse-old-adv ...`(2回目以降は保存済みを再利用=API 0)。
