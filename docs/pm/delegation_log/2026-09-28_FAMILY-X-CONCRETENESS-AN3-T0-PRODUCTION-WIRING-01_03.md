## 管理ID

FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01(修正1回目=診断のみ、委任 _03)。一時ファイル `docs/pm/ACTIVE_TASK_AN3C.md` / `docs/pm/RESULT_PACKET_AN3C.md`(commitしない)。並行Agentなし。本タスクの所有: 新規 `docs/pm/diag_open_228_main_story_paragraph_check_01.md`、delegation_log。**コード・Prompt・SSOT・REPORT・出力ディレクトリは一切変更しない(読み取りのみ)。API支出 上限¥0(LLM/TTS/ASR 呼び出し禁止)。** **削除・移動・`rm`・`git clean`・stash/rebase/reset/amend/force push 禁止**。未追跡ファイルは他Agent/ユーザーの作業物として扱う。push競合時は `git merge origin/main` のみ。APIキー本文表示禁止。

## 性質/到達上限Status/禁止事項

- 性質: 診断(Fable Gate 3 判定の材料集め)。Status 変更なし。
- 背景: Phase B の確認用再生成で、Hormuz の Advanced 生成が `er003_v1_n3_01_scaffold_generate.py::split_article_text()` の「Main Story(タイトル直後〜最初の ### 見出し前)は段落数 2 以上」チェックに **2 回連続で失敗**(未捕捉 RuntimeError、`parts.json` 未生成)。Meta は 1 回で PASS。REPORT `FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01_REPORT.md` §14、OPEN-228。Fable の懸念: これが AN3 配線に起因する系統的な構造変化(JA 導入部が短くなり Advanced 化で導入部が 1 段落に圧縮される)なのか、配線前から存在する偶発的ばらつきなのかを切り分けたい。
- 禁止: 修正案の実装、再生成の実行、Prompt の変更。提案は文案のみ。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない。D-1: Grep→該当行範囲Read。G-1: git出力最小化。F-1: transcript退避不要。
T-0: 本委任文を `docs/pm/delegation_log/2026-09-28_FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01_03.md` へ逐語保存し、`.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-28_FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01_03.md --json-out docs/pm/delegation_log/2026-09-28_FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01_03.md_check.json` を実行し結果1行記録。
T-2: TTSなし。T-3: API支出なし。

## 調査項目(すべて根拠ファイル・行を記録)

1. **チェックの実体**: `split_article_text()` の段落数条件(閾値・段落の定義=空行区切りか)、呼び出し元 `er012_e_family_entertainment_two_level_runner_01.py::run_writer_stage()` で例外が捕捉されない経路、既存 `run_writer_with_technical_retry()`(`validate_point_structure`、max_attempts=2)が **この段落数チェックを含んでいない** ことの確認。
2. **Advanced Prompt が導入部の段落数を指示しているか**: `er003_v1_n3_01_advanced_adaptation_generate.py` の Prompt(Grep `paragraph|段落|Main Story|introduction|###`)。指示が無ければ「チェックは Prompt に裏付けのない潜在的脆弱性」と判定。
3. **配線前の実績(履歴)**: Family X の既存 Production/Trial run(`er019_output/**/b1b/article.md` または advanced 出力、`er012_output/**`、`er039_output/**/cells/*_en.md`、`er037_output/**`)を Glob し、各 Advanced 記事の「タイトル直後〜最初の ### までの段落数」を機械的に数える(Python ワンライナー可、API 不要)。特に Hormuz `hormuz__run_06_flashlite_full_kp/b1b/article.md`(配線前 Production)と、Trial-02 の Hormuz AN3-T0/AN2-T0/Baseline の EN 本文、Meta 同様。表にする(記事 × run × 導入部段落数 × 合計段落数 × 文字数)。
4. **過去の同一失敗の有無**: `git log --oneline -S "段落数" -- "*.md"`、REPORT/DECISION_LOG/OPEN_ITEMS を Grep(`段落数|split_article_text|Main Story`)し、配線前にこのチェックで失敗した記録があるか。runner のログ/`attempt`/`audit` JSON も Glob して RuntimeError の痕跡を探す。
5. **AN3 JA 記事の構造比較**: Hormuz JA R2(AN3、`er019_output/family_x_entertainment_production_runner_01/an3_t0_wiring_regression_01/hormuz/` 配下)と配線前 Hormuz JA R2(run_06 の JA、Trial-02 Baseline JA)の段落数・導入部の段落数・文字数を比較。Trial-02 の AN3-T0 Hormuz EN 本文(`er039_output/.../cells/AN3-T0_en.md`)の導入部段落数も確認(Trial-02 では同じ AN3 JA から Advanced 化して段落数チェックを通ったか/そもそも Trial-02 はこのチェックを実行していたか)。
6. **切り分け判定**: 上記を踏まえ、(a) AN3 起因の可能性(高/中/低)と根拠、(b) 配線前からの偶発ばらつきの可能性と根拠、(c) 追加サンプルで判定するなら必要な再実行回数と概算費用(Hormuz Advanced 段階のみ ≈ ¥4/回を目安に実測値から)、(d) 対処選択肢(実装しない): ①既存 `run_writer_with_technical_retry` の対象に段落数チェックを含める(既存機構の適用範囲拡張、コード規模)、②段落数チェックを警告化(Gate 弱体化、非推奨理由)、③Advanced Prompt へ導入部 2 段落の明示(現行英語化 Prompt 変更=ユーザー禁止事項に抵触)、④何もしない(Production 稼働時のクラッシュリスク)。各案の影響範囲・リスク・費用を表に。

## 事前指定Read一覧

- `er003_v1_n3_01_scaffold_generate.py`: Grep `def split_article_text|段落|paragraph|RuntimeError` → 該当範囲
- `er012_e_family_entertainment_two_level_runner_01.py`: Grep `split_article_text|run_writer_with_technical_retry|validate_point_structure|def run_writer_stage`
- `er003_v1_n3_01_advanced_adaptation_generate.py`: Grep 上記2
- `FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01_REPORT.md` §14(344-375行)
- `an3_t0_wiring_regression_01/hormuz/` 配下の JA/Advanced 本文・ログ(Glob)

## 事前指定Grep一覧+追記位置・更新位置の手順

- Grep対象: 上記。SSOT は Grep のみ(編集禁止)。
- 追記位置: 新規 `docs/pm/diag_open_228_main_story_paragraph_check_01.md`。
- 更新位置: なし。

## 実行コマンド全文

- 段落数集計は `.venv\Scripts\python.exe -c "..."` のワンライナーまたは scratchpad の一時スクリプト(`C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\f1538907-8efe-486d-9790-ef5c6cd789fa\scratchpad\` 配下、リポジトリへは置かない)。実行したコマンドを逐語記録。
- `git log --oneline -S "段落数" -- "*.md" | head -20`

## SSOT追記文

不要(診断のみ)。

## Git

- add対象(path指定のみ): 診断書、delegation_log+`_check.json`。SSOT編集権: なし。
- メッセージ: `FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01: OPEN-228 診断(Main Story段落数チェック失敗の切り分け、¥0)`、trailer `Management-ID: FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01`。`git push origin main`。

## 報告(RESULT_PACKET_AN3C + handback、目安25行)

調査項目1〜6の結論(表は診断書、handback は要約)、切り分け判定と根拠、選択肢表の要約、commit hash・raw URL、STOP有無。
