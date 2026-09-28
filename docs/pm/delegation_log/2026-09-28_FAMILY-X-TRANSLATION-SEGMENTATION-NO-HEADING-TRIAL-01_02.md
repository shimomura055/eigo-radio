## 管理ID

FAMILY-X-TRANSLATION-SEGMENTATION-NO-HEADING-TRIAL-01(修正1回目、委任 _02)。一時ファイル `docs/pm/ACTIVE_TASK_NH1B.md` / `docs/pm/RESULT_PACKET_NH1B.md`(commitしない)。並行: 別Sonnet 2件(Task 4 Phase B `er019_family_x_audio_production_runner_01.py`/`er033_*`/`er003_b1_p9a_audio.py`/`er003_v1_n3_01_tts_generate.py`/SSOT 4点、AN3 reminder 削除 `er019_family_x_ja_writer_o_r1_r2_01.py`)→ 触れない。SSOT 4点は編集権なし。本タスクの所有: `er045_family_x_no_heading_segmentation_trial_01.py`(+test)、`er045_output/family_x_no_heading_segmentation_trial_01/`、`user_test/no_heading_trial_01/`、`FAMILY-X-TRANSLATION-SEGMENTATION-NO-HEADING-TRIAL-01_REPORT.md`(§追記)、設計書(§追記)、delegation_log。**Production code・正式Prompt・CURRENT_SPEC・Comment 仕様・OPEN-228 関連(split/Gate/retry)は変更禁止。削除・移動・`rm`・`git clean`・stash/rebase/reset/amend/force push 禁止。未追跡ファイルは他Agent/ユーザーの作業物として扱う。push競合時は `git merge origin/main` のみ。APIキー本文表示禁止。**

## 性質/到達上限Status/禁止事項

- 性質: Trial の比較条件の是正(Baseline と同等の must-fix retry を Trial にも適用)+In One Line のユーザー仕様(短い自然な一文)への適合。Status `USER_DECISION_REQUIRED` のまま。
- 費用: 上限¥10(想定: Meta 忠実英訳の must-fix retry 1 call、In One Line v2 2 call、rubric 再評価 2 call)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時のみSTOPし報告。
- 禁止: 本文の再構成・新規 Fact 追加・見出し生成・分割のための本文書き換え(分割は決定論のまま)、In One Line のための本文逆算書き換え、Comment 変更、独自 retry ループ(must-fix は Production と同じ **1 回のみ**)。v1(初回)の出力・指標は削除せず併載(透明性)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)

E-1/D-1/G-1/F-1 標準。
T-0: 本委任文を `docs/pm/delegation_log/2026-09-28_FAMILY-X-TRANSLATION-SEGMENTATION-NO-HEADING-TRIAL-01_02.md` へ逐語保存し、`.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-28_FAMILY-X-TRANSLATION-SEGMENTATION-NO-HEADING-TRIAL-01_02.md --json-out docs/pm/delegation_log/2026-09-28_FAMILY-X-TRANSLATION-SEGMENTATION-NO-HEADING-TRIAL-01_02.md_check.json` を実行し結果1行記録。
T-2: TTSなし。T-3: 上記「性質」欄の定型文に従う。

## 手順

1. **Meta の must-fix retry(Production 同等・1回)**: 初回 Trial 英訳の Deviation Check で出た MAJOR/MINOR(「元に戻しました」→ "put back the feature" の意味反転 等)を、Production と同じ `build_must_fix_block()`(または同等の既存 must-fix ブロック生成関数)で Trial 忠実英訳 Prompt に付加して **1 回だけ**再生成し、`run_deviation_check()` を再実行。結果が `LEDGER_COMPLIANT` にならなければそれ以上 retry せず記録(Production と同じ 1 回→STOP)。Hormuz は既に COMPLIANT のため再生成しない。
2. **In One Line v2(両記事)**: ユーザー仕様「記事の核心を短く自然な一文で言う/一文/一回聞いて理解できる/複数論点を詰め込みすぎない/新しい Fact を加えない/結論・教訓を勝手に追加しない」を Trial 用 Prompt に明示し(Trial 限定、設計書に逐語)、目安として「主節 1 つ、従属節は最大 1 つ、およそ 12〜18 語」を **参考ガイド**として付す(数値は Trial 限定の目安と明記)。1 call ずつ再生成。v1(28 語/27 語)と Baseline(14 語/20 語)と並べて語数・文数・論点数を表示。
3. **rubric 再評価**: 変更した要素(Meta 本文 v2、In One Line v2 ×2)について同じ 14 項目 rubric を再評価(Comment 文脈込み、v1 と同条件)。Hormuz 本文の rubric は再評価不要。
4. ページ更新: 記事ごとに「Trial v1/Trial v2(must-fix 後)」「In One Line v1/v2」を併載し、差分が分かるようにする。Deviation Check 結果(Baseline/Trial v1/Trial v2)を表に。push 後 `curl -sI` 200+headless DOM で本文実表示を確認。
5. REPORT に「修正1回目(2026-09-28)」節を追記(理由、実施、結果、費用、Production 無変更)。設計書に同旨。SSOT 文案(RESULT_PACKET)を更新(Meta v2 の結果、In One Line v2 の語数)。
6. テスト: 既存 14 件 PASS 維持(+v2 Prompt に見出し生成指示が無い assert を追加)。`run_project_regression.py --pattern "er045*_test_*.py"`。

## 事前指定Read一覧

- `FAMILY-X-TRANSLATION-SEGMENTATION-NO-HEADING-TRIAL-01_REPORT.md`: Grep `LEDGER_DEVIATION|In One Line|語数|MAJOR` → 該当範囲
- `er045_family_x_no_heading_segmentation_trial_01.py`: Grep `def |PROMPT|must_fix|in_one_line|rubric`
- `er019_family_x_ja_writer_o_r1_r2_01.py` または Advanced 化側: Grep `def build_must_fix_block`(既存 must-fix ブロック生成の流用元。読み取りのみ)

## 事前指定Grep一覧+追記位置・更新位置の手順

- Grep対象: 上記。更新位置: `er045_*.py`(v2 経路追加)、出力 dir、`user_test/no_heading_trial_01/index.html`、REPORT・設計書末尾。

## 実行コマンド全文

- `.venv\Scripts\python.exe er045_family_x_no_heading_segmentation_trial_01.py --article meta --stage must-fix-retry --out-dir "er045_output/family_x_no_heading_segmentation_trial_01/meta" --budget-jpy 10`、`--stage in-one-line-v2`(hormuz/meta)、`--stage rubric-v2`(引数は実装に合わせ逐語記録)
- `.venv\Scripts\python.exe run_project_regression.py --pattern "er045*_test_*.py"`
- `git diff --stat HEAD -- "er0*.py" "er003_v1_translator_briefs/" | grep -v er045`(本タスク由来なし)
- `curl -sI https://shimomura055.github.io/eigo-radio/user_test/no_heading_trial_01/index.html`、headless DOM(逐語記録)

## SSOT追記文

RESULT_PACKET の文案を更新(編集せず)。

## Git

- add対象(path指定のみ): `er045_*`、`er045_output/.../`(json/md)、`user_test/no_heading_trial_01/`、REPORT、設計書、delegation_log+`_check.json`。SSOT 編集権なし。
- メッセージ: `FAMILY-X-TRANSLATION-SEGMENTATION-NO-HEADING-TRIAL-01: 修正1回目(Meta忠実英訳へProduction同等のmust-fix retry 1回、In One Line v2の簡潔化、rubric再評価、v1/v2併載)`、trailer `Management-ID: FAMILY-X-TRANSLATION-SEGMENTATION-NO-HEADING-TRIAL-01`。`git push origin main`。

## 報告(RESULT_PACKET_NH1B + handback、目安25行)

Meta v2 の Deviation 結果(MAJOR/MINOR 件数、修正箇所の逐語)/In One Line v1→v2(両記事、語数・文数・全文)/rubric v2 の変化/費用実測/Regression/公開確認/commit hash・raw URL/STOP有無/新たな USER_DECISION_REQUIRED 事項。
