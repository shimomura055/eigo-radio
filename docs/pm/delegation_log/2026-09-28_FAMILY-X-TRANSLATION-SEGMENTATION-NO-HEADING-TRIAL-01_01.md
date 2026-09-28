## 管理ID

FAMILY-X-TRANSLATION-SEGMENTATION-NO-HEADING-TRIAL-01(ユーザー承認済みTrial、text のみ、TTS なし)。一時ファイル `docs/pm/ACTIVE_TASK_NH1.md` / `docs/pm/RESULT_PACKET_NH1.md`(commitしない)。並行: 別Sonnet 4件(Task 2 `er046_*`/`user_test/kp_advanced_explanation_audio_trial_04/`、Task 3 `er047_*`/`user_test/fixed_shell_three_five_retrial_01/`、Task 4 設計 `docs/pm/design_tts_variable_role_style_production_wiring_01.md`、SSOT反映Agent[SSOT 4点+REPORT_LEDGER 編集中])→ これらに触れない。SSOT 4点は編集権なし(Grep のみ、文案は RESULT_PACKET へ)。本タスクの所有: 新規 `er045_family_x_no_heading_segmentation_trial_01.py`(+`_test_01.py`)、`er045_output/family_x_no_heading_segmentation_trial_01/`、`user_test/no_heading_trial_01/`、新規 `FAMILY-X-TRANSLATION-SEGMENTATION-NO-HEADING-TRIAL-01_REPORT.md`、`docs/pm/design_family_x_no_heading_segmentation_trial_01.md`、delegation_log。**Production code・正式Prompt・CURRENT_SPEC・routing・Comment 仕様は一切変更しない。削除・移動・`rm`・`git clean`・stash/rebase/reset/amend/force push 禁止。未追跡ファイルは他Agent/ユーザーの作業物として扱う。push競合時は `git merge origin/main` のみ、conflictは中断報告。APIキー本文表示禁止。**

## 最初に実施(重複確認、結果を REPORT 冒頭と handback 冒頭に必ず記載)

Fable 側の事前 Grep(`NO-HEADING|見出し廃止|TRANSLATION-SEGMENTATION` を *.md/er0*.py/user_test で検索、`er045〜er049` の Glob)はいずれも 0 件。Sonnet 側でも `git log --oneline --all | grep -i "NO-HEADING\|SEGMENTATION"`、`docs/pm/REPORT_LEDGER.md`・`OPEN_ITEMS.md`・`DECISION_LOG.md` の Grep、`docs/pm/delegation_log/` の Glob(`*NO-HEADING*`)、`git fetch origin` 後の `git log origin/main --oneline -20` を実施し、**同 Trial が既に存在・進行中なら着手せず STOP して報告**。未着手を確認できた場合のみ続行。

## 性質/到達上限Status/禁止事項

- 性質: Trial(Family X 本文構成の見直し)。到達上限Status: `REJECTED` / `VALIDATED` / `USER_DECISION_REQUIRED`(ユーザー判断前に Production へ実装しない、Production wiring 禁止)。
- 費用: 上限¥30(想定: 2記事 × [忠実英訳 1 call+短い In One Line 1 call+rubric 評価 1 call] 程度、TTS/ASR なし)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。
- **実行安全**: `--stage all` 禁止。Production runner を回さず、Trial script から必要な関数のみ呼ぶ(新規記事生成・Source 取得なし)。実行前に対象記事数・想定 call 数・想定費用を ACTIVE_TASK に記録。
- 禁止: 見出しに合わせた再構成/新しい Fact 追加/元文にない因果追加/内容順序の大幅変更/Entertainment 目的の新エピソード追加/In One Line のための本文逆算書き換え/分割のための本文書き換え/Comment 仕様・Comment 本文の変更(既存 Comment を reuse)/タイトル仕様の変更/**OPEN-228 の単独修正**(split/Gate/retry には触れない)/Family 共有 Prompt の変更。「Advanced 化」を理由に内容編集を増やさない(自然な英語にするための通常の言語変換は許容)。ユーザー向け表記は Standard/Advanced。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)

E-1/D-1/G-1/F-1 標準(全文Readは `er003_v1_n3_01_advanced_adaptation_generate.py` の Prompt 定数部と設計書のみ可)。
T-0: 本委任文を `docs/pm/delegation_log/2026-09-28_FAMILY-X-TRANSLATION-SEGMENTATION-NO-HEADING-TRIAL-01_01.md` へ逐語保存し、`.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-28_FAMILY-X-TRANSLATION-SEGMENTATION-NO-HEADING-TRIAL-01_01.md --json-out docs/pm/delegation_log/2026-09-28_FAMILY-X-TRANSLATION-SEGMENTATION-NO-HEADING-TRIAL-01_01.md_check.json` を実行し結果1行記録。
T-2: TTSなし。T-3: 上記「性質」欄の定型文に従う。

## ユーザー指示(原文要旨、逐語は設計書へ転記)

「Trial仕様: 本文途中の見出しを廃止/日本語完成記事を基本そのまま英訳/英訳時に過度な再構成・再編集をしない/本文を自然な段落境界で Part1/Part2/Part3 に分割/なるべく均等に分けるが、分割のために本文を書き換えない/構成: Comment1・body1・Comment2・body2・Comment3・body3・Comment4・In One Line/In One Line は短い自然な一文/Comment で変化をつけるため、本文見出しは不要。重要: この Trial は OPEN-228 の古い『最初の###見出し前に導入部2段落以上』前提を将来的に不要化できるかを見る意味もある。したがって OPEN-228 を先に単独修正しない。対象: 既存 Family X 記事(Hormuz/Meta)で最小構成。入力: AN3-T0 で生成された日本語完成記事。新しい記事生成・Source 取得は不要。ユーザー仮説(見出し作成→本文編集→構造複雑化→In One Line の過剰圧縮)は仮説であり『見出しが原因』と決めつけて実装しない。評価項目: 日本語原文への忠実性/Fact 保持/因果保持/新規 Fact 0/順序保持/意味の追加・削除/読みやすさ/聞きやすさ/Entertainment 性/3分割の自然さ/長さバランス/Comment との接続自然さ/In One Line の簡潔さ・要旨正確性/見出しをなくした結果、内容が単調になりすぎないか。STOP 条件: 忠実英訳だけでは英語として不自然/3分割で意味が壊れる/Comment 位置が不自然/見出し廃止で著しく聞きにくい/In One Line 簡潔化で重要 Fact が落ちる/既存正式仕様と大きく衝突/Family 共有 Prompt 変更が必要/新しい Product 判断が必要。」

## Fable補足

- **Existing Spec Check(設計書 §1、Grep 先を記録)**: `CURRENT_SPEC.md`(`Section Segmentation|Heading|見出し|body|Comment|In One Line|In one line|Advanced`)で、現在の Section Segmentation Contract、Heading 1/2 が正式 Production 仕様か、body1/2/3 の現在の定義、Comment 1〜4 の配置仕様、In One Line の既存仕様(あれば本 Trial が「既存仕様の復旧」か「新規」かを明記)。`er003_v1_n3_01_advanced_adaptation_generate.py` の Prompt が「翻訳」以外に要求している編集要素(見出し生成・再構成・In One Line 生成の指示、`ADVANCED_VOCAB_RULE_V2_BLOCK` 等)を逐語で列挙。`er003_v1_n3_01_scaffold_generate.py::split_article_text()`(現行の分割規則、OPEN-228 のチェック)。Family A/Y 等との共有 Prompt 有無(Grep `import .*advanced_adaptation|from er003_v1_n3_01_advanced`)。過去の「見出し廃止」「翻訳のみ」Trial の有無(`DECISION_LOG.md`/`OPEN_ITEMS.md`/REPORT を Grep `見出し|heading|翻訳のみ|faithful`)。既存 Family X 音声構造(Comment の位置、`er019_family_x_audio_production_runner_01.py` Grep `comment_|full_story_part|in_one_line`)。
- **入力**: AN3-T0 の日本語完成記事=`er019_output/family_x_entertainment_production_runner_01/an3_t0_wiring_regression_01/{hormuz,meta}/` の JA R2 最終本文(Glob で特定。Hormuz は Advanced 化で OPEN-228 のクラッシュが起きた run だが JA 本文・Fact Check は完了済み)。**Baseline**=同 run の現行 Advanced 出力(見出しあり、現行 In One Line。Hormuz は `LEDGER_COMPLIANT` の2回目本文が REPORT に転記済み/Meta は run 出力)。既存 Comment 1〜4 は同 run または直近 Production run の Comment を reuse(Comment の言語・段階を Existing Spec で確認し記録)。
- **Trial 生成(Trial 限定 Prompt、設計書に逐語)**: (a) 忠実英訳 Prompt=現行 Advanced Prompt の語彙ルール(`ADVANCED_VOCAB_RULE_V2_BLOCK` 等の既存ブロック)は **そのまま流用**し、見出し生成・再構成・In One Line 生成の指示を除いた「日本語完成記事を段落構造を保って忠実に英訳する」Trial 用最小 Prompt を新設(Trial 限定と明記。Production Prompt 定数は無変更)。段落数=JA 段落数を原則維持。(b) 3分割=**LLM に任せず決定論アルゴリズム**で段落境界のみを使い、3区間の文字数(または語数)が最も均等になる境界2点を選ぶ(本文書き換えなし)。(c) In One Line=「記事の核心を短く自然な一文で」の Trial 用最小 Prompt(1 call、新規 Fact・結論・教訓の追加禁止を明記)。(d) 評価=既存 `run_deviation_check()`(Ledger Deviation Check)を Trial EN と Baseline EN の両方に主判定として適用+決定論指標(段落数、3区間の長さ、JA→EN の段落対応、新規固有名詞・数字の有無[改良カウンタ相当]、In One Line の語数・文数)+LLM rubric 1 call(ユーザー評価項目 14 点、1〜5+根拠、Baseline/Trial 両方)。「見出しをなくして単調になりすぎないか/Comment で十分変化が出るか」は rubric 項目に含め、ユーザー試読の主観判断に委ねる旨も明記。
- **成果物ページ** `user_test/no_heading_trial_01/index.html`(GitHub Pages): 記事ごとに JA AN3 原文/Baseline 英語(見出し含む)/Trial 英語(3分割位置を明示、Comment 1〜4 の挿入位置を明示、In One Line Before/After)/Baseline vs Trial の本文差分(段落単位の並列または diff 表示)/指標・rubric。push 後 `curl -sI` 200 と headless Edge/Chrome `--headless --dump-dom` で公開 DOM に本文が実表示されることを確認(音声なし)。
- 判定案: `USER_DECISION_REQUIRED`(ユーザー試読待ち)。Sonnet は `VALIDATED` を自己宣言しない。STOP 条件に該当したら追加改善せず STOP 報告。

## 事前指定Read一覧

- `CURRENT_SPEC.md`: Grep 上記 → 該当行範囲のみ
- `er003_v1_n3_01_advanced_adaptation_generate.py`: Prompt 定数部(Grep `BLOCK|PROMPT|def build_prompt|heading|In one line`)
- `er003_v1_n3_01_scaffold_generate.py`: Grep `def split_article_text|段落|###`
- `er019_family_x_audio_production_runner_01.py`: Grep `comment_|full_story_part|in_one_line|topic_intro`
- `FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01_REPORT.md`: 本文全文転記部(Grep `## 記事本文全文`)
- `er039_family_xy_concreteness_control_trial_02.py`: 改良カウンタ(Grep `def count_|entity|kanji`)流用

## 事前指定Grep一覧+追記位置・更新位置の手順

- Grep対象: 上記+`DECISION_LOG.md`/`OPEN_ITEMS.md`(`見出し|heading|翻訳のみ|OPEN-228|OPEN-165`)。SSOT は Grep のみ(編集禁止)。
- 追記位置: 設計書(新規)、REPORT(新規)。
- 更新位置: なし(既存ファイル無変更)。

## 実行コマンド全文

- `.venv\Scripts\python.exe er045_family_x_no_heading_segmentation_trial_01.py --article hormuz --source-dir "<AN3-T0 run の hormuz ディレクトリ>" --out-dir "er045_output/family_x_no_heading_segmentation_trial_01/hormuz" --budget-jpy 30`(meta も同様。引数は実装に合わせ逐語記録)
- `.venv\Scripts\python.exe -m unittest er045_family_x_no_heading_segmentation_trial_01_test_01 -v`(Production Prompt 定数 sha256 不変、分割アルゴリズムの決定論性・本文不変、Comment 本文不変、Trial Prompt に見出し生成指示が無い)
- `.venv\Scripts\python.exe run_project_regression.py --pattern "er045*_test_*.py"`
- Production無変更の証拠: `git diff --stat HEAD -- "er0*.py" "er003_v1_translator_briefs/" | grep -v er045`(空。他タスク差分は列挙)
- Pages: `curl -sI https://shimomura055.github.io/eigo-radio/user_test/no_heading_trial_01/index.html`、headless DOM 取得(逐語記録)

## SSOT追記文

RESULT_PACKET へ文案のみ(REPORT_LEDGER 新行、DECISION_LOG、OPEN-228 への「本 Trial の結果次第で前提不要化を検討」追記案、新規 OPEN 候補)。

## Git

- add対象(path指定のみ、`git add -A` 禁止): `er045_*`、`er045_output/.../`(json/md)、`user_test/no_heading_trial_01/`、REPORT、設計書、delegation_log+`_check.json`。SSOT編集権: なし。
- メッセージ: `FAMILY-X-TRANSLATION-SEGMENTATION-NO-HEADING-TRIAL-01: 見出し廃止+忠実英訳+段落境界3分割+Comment配置+短いIn One Line のTrial(Hormuz/Meta、Baseline比較ページ)`、trailer `Management-ID: FAMILY-X-TRANSLATION-SEGMENTATION-NO-HEADING-TRIAL-01`。`git push origin main`。

## 報告(RESULT_PACKET_NH1 + handback、目安35行)

冒頭: 重複確認結果。以降ユーザー指定 Closeout: 1 Hormuz 比較 2 Meta 比較 3 見出し有無による本文変化 4 3分割の位置と長さ 5 Comment との接続 6 In One Line Before/After 7 Fact/因果逸脱(Deviation Check 結果、Baseline/Trial) 8 面白さ・聞きやすさ(rubric) 9 Cost 10 Existing Spec との関係(復旧か新規か、衝突の有無) 11 Production 変更ゼロ 12 新規 USER_DECISION_REQUIRED+STOP 条件該当有無+使用 Prompt 全文の所在+公開確認結果+SSOT 文案+commit hash+raw URL+未配線 APPROVED 項目の有無(本 Trial では該当なし)。
