## 管理ID

FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-02(再開委任。前Agentは固有名詞9→19の調査を完了した時点で、スコープ外の未追跡ファイル2件[`a2_jt_debug.json`、`docs/pm/b1b_naming_investigation.md`]を `rm -f` で誤削除したため停止した。**本タスクでは削除・移動・`rm`・`git clean`・stash/rebase/reset を一切行わない。自タスクの out-dir 外のファイルには触れない**)。一時ファイル `docs/pm/ACTIVE_TASK_CC2.md`(既存、続きを追記)/ `docs/pm/RESULT_PACKET_CC2.md`(commitしない)。並行: 別Sonnetが誤削除ファイルの復元(read-only+新規作成)を実行中 → `a2_jt_debug.json`/`docs/pm/b1b_naming_investigation.md` に触れない。本タスクの所有: 新規 `er039_family_xy_concreteness_control_trial_02*.py`(+test)、`er039_output/family_xy_concreteness_control_trial_02/`、`user_test/concreteness_trial_02/`、新規 `FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-02_REPORT.md`、`docs/pm/design_family_xy_concreteness_control_trial_02.md`、delegation_log。**Production code・正式Prompt・CURRENT_SPEC・routing は一切変更しない**。SSOT 4点は編集権なし(文案をRESULT_PACKETへ)。

## 性質/到達上限Status/禁止事項

- 性質: Trial。到達上限Status: `REJECTED` / `VALIDATED` / `USER_DECISION_REQUIRED`(Sonnetは判定案のみ、`VALIDATED` でもProduction実装へ進まない)。
- 費用: 上限¥70(Guardrail。テキスト生成+評価のみ、TTSなし)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。
- 禁止(ユーザー明示): Production code/正式Prompt/CURRENT_SPEC/routing変更、TTS、不要な再生成(Baseline A0 と Trial-01 の既存出力は再利用)、新規Product仕様の追加、A1/A2単独の再現性3回Trial、cleanupの追加Trial、「数字が少ないほど良い」評価、長い新規Prompt(T1は短い追加文のみ)。STOP条件(Essential Fact欠落/意味反転/因果関係の新規捏造/日本語にない固有名詞・数字を英語化で新規追加する構造的問題/既存Family A共有Prompt変更が必要/Production仕様判断が必要/Guardrail超過)に該当したら追加Trialせず報告。`git add -A` 禁止(push競合時は `git merge origin/main` のみ、conflictは中断報告)。APIキー本文表示禁止。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要。
T-0: 受領した委任文を `docs/pm/delegation_log/2026-09-28_FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-02_02.md` へ保存し `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-28_FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-02_02.md --json-out docs/pm/delegation_log/2026-09-28_FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-02_02.md_check.json`、結果1行記録。
T-2: TTSなし。
T-3: 上記「性質」欄の定型文に従う。

## ユーザー指示(原文)

前委任文 `docs/pm/delegation_log/2026-09-28_FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-02_01.md` の「ユーザー指示(原文)」節を正本として参照(2×2 Matrix[Hormuz/Meta × AN3=A3+N2 / AN2=A2+N2 × T0現行英語化 / T1抑制付き英語化]+Baseline A0、T1はTrial限定の短い追加文、固有名詞9→19の事実確認6点+名称単位差分表、評価項目14点、ユーザー確認用の本文読み比べ成果物、前回Trialの扱い、Trial範囲、STOP条件、Closeout項目。目的は「減らしながら内容を壊さない最適な組み合わせ」)。

## 前Agentからの引き継ぎ(そのまま設計書 §2 へ転記し、名称単位表を完成させる)

固有名詞9→19(Hormuz AN、read-only実コード実行、¥0): JA `extract_entities_ja()` 9件=`イラン, ガソリン, タンカー, トランプ, ドル, ニュース, バレル, ブレント, ホルムズ`。EN `extract_entities_en()` 19件=`Bill, Brent, Character:, Donald, Eastern, Gulf, Hormuz, Iran, July, Main, Market's, Middle, Missing, Oil, Percent, States, Trump, United`。暫定結論: 大部分がカウント方式のアーティファクト。EN 19件中7件(`Oil, Market's, Main, Character:, Missing, Percent, Bill`)はタイトル見出しのTitle Case由来の普通名詞。JA 9件中5件(`ニュース, バレル, ドル, タンカー, ガソリン`)はカタカナ一般名詞(実固有名詞は`トランプ,ホルムズ,ブレント,イラン`の4件)。JA側は漢字表記の固有名詞(米国/中東/湾岸諸国)を正規表現が拾えず過小カウント。EN側は複合固有名詞(United States, Strait of Hormuz, Middle Eastern)を複数トークンに分割。JAに存在しなかった真の新規追加は「Donald」のみ。英語化Prompt: `er003_v1_n3_01_advanced_adaptation_generate.py` の `build_prompt()`/`generate_advanced_adaptation()` はJA記事本文のみを入力とし、Source記事・Ledgerは渡していない。固有名詞KEEPルール=`ADVANCED_VOCAB_RULE_V2_BLOCK` の exception C「人名・企業名・地名」(逐語を設計書へ引用)。→ 本タスクで (a) 名称単位のJA→EN差分表(固有名詞/JA出現回数/EN出現回数/ENで新規追加か/備考[一般名詞・Title Case・複合語分割・漢字未検出等の分類])を完成、(b) **Trial-02の固有名詞カウントは「実固有名詞のみ・複合語は1件・漢字固有名詞も検出・Title Case見出しは除外」の改良カウンタ(Trial内関数、Production無変更)で JA/EN を同一基準で数え直す**(旧カウンタの値も併記)。

## 実装・実行

- Trial script `er039_family_xy_concreteness_control_trial_02.py`(er037を import して再利用)。Baseline=Trial-01の A0(JA/EN)を再利用、AN3=Trial-01 の AN JA 出力を再利用して T0(既存EN出力を再利用)/T1(新規)、AN2=JA新規生成→T0/T1。T1追加文は短く(設計書に逐語)。各セル: JA全文/EN全文/数字数/過度精度・時刻数/固有名詞数(新旧カウンタ)/JA→EN新規出現の数字・固有名詞(名称単位)/`run_deviation_check`(主判定)/Leakage Check(Family X側の該当QAをGrepし、無ければ「該当QAなし」と記録、rubricで代替しない)/rubric 1 call(面白さ・読みやすさ・聞いた場合の理解しやすさ・Baseline比の情報量、1〜5+根拠引用)/C1思想の確認(Baseline比で新規前景化された数字・固有名詞)。
- ユーザー確認用: `user_test/concreteness_trial_02/index.html`(GitHub Pages。記事ごとに Baseline/AN3-T0/AN3-T1/AN2-T0/AN2-T1 の JA全文・EN全文を並列表示、指標小表、可能ならBaselineとの単語diffハイライト)+`er039_output/.../comparison_{hormuz,meta}.md`。push後 `curl -sI https://shimomura055.github.io/eigo-radio/user_test/concreteness_trial_02/index.html` で200確認。
- 判定案: Deviation MAJOR あり→不合格、無し→候補。候補間は削減量とrubricの両方を並べる。Sonnetは `VALIDATED` を自己宣言しない。

## 実行コマンド全文

- `.venv\Scripts\python.exe er039_family_xy_concreteness_control_trial_02.py --article hormuz --cells AN3-T0,AN3-T1,AN2-T0,AN2-T1 --baseline-from "er037_output/family_xy_concreteness_control_trial_01/hormuz" --out-dir "er039_output/family_xy_concreteness_control_trial_02" --budget-jpy 70`
- `.venv\Scripts\python.exe er039_family_xy_concreteness_control_trial_02.py --article meta --cells AN3-T0,AN3-T1,AN2-T0,AN2-T1 --baseline-from "er037_output/family_xy_concreteness_control_trial_01/meta" --out-dir "er039_output/family_xy_concreteness_control_trial_02" --budget-jpy 70`(引数は実装に合わせ逐語記録)
- `.venv\Scripts\python.exe er039_family_xy_concreteness_control_trial_02.py --investigate-entities --from "er037_output/family_xy_concreteness_control_trial_01/hormuz" --out "er039_output/family_xy_concreteness_control_trial_02/hormuz/entity_ja_en_diff.md"`(¥0)
- `.venv\Scripts\python.exe -m pytest er039_family_xy_concreteness_control_trial_02_test_01.py -q`(T1追記が正式Prompt定数を変更しないこと[sha256]、改良カウンタ[複合語1件・Title Case除外・漢字固有名詞]、名称単位差分表、JA→EN新規出現検出)
- `.venv\Scripts\python.exe run_project_regression.py --pattern "er039*_test_*.py"`
- Production無変更の証拠: `git diff --stat HEAD -- "er0*.py" "er003_v1_translator_briefs/" | grep -v er039`(空)

## SSOT追記文

RESULT_PACKETへ文案のみ(REPORT_LEDGER新行、DECISION_LOG、OPEN候補、OPEN-220への追記案)。

## Git

- add対象: `er039_*`、`er039_output/family_xy_concreteness_control_trial_02/`(md/json)、`user_test/concreteness_trial_02/`、REPORT、設計書、delegation_log `_01.md`/`_02.md`+`_check.json`。SSOT編集権: なし。他の未追跡・変更ファイルは一切addしない。
- メッセージ: `FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-02: AN3/AN2 × T0/T1 の2×2 Matrix(Hormuz/Meta)+固有名詞9→19の実体調査+本文読み比べページ`、trailer `Management-ID: FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-02`。`git push origin main`。

## 報告(RESULT_PACKET項目)

ユーザー指定Closeout項目(2×2 Matrix結果/Baseline比較/本文比較の所在[Pages URL+md]/AN3 vs AN2/T0 vs T1/固有名詞9→19の原因[6点への回答+名称単位表]/JA→EN新規追加の有無/数字・固有名詞削減量[新旧カウンタ]/Fact・因果・面白さ評価/Leakage・Deviation Check/Cost/Regression/最終Status案/USER_DECISION_REQUIRED事項/Production無変更の証拠)+STOP該当有無+SSOT文案+commit hash+raw URL。ユーザー向け表記はStandard/Advanced。
