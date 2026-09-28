## 管理ID

FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-02(ユーザー承認済みTrial、Trialのみ)。一時ファイル `docs/pm/ACTIVE_TASK_CC2.md` / `docs/pm/RESULT_PACKET_CC2.md`(commitしない)。並行Agentなし。本タスクの所有: 新規 `er039_family_xy_concreteness_control_trial_02*.py`(+test。Trial-01の `er037_family_xy_concreteness_control_trial_01.py` を import して関数を再利用、er037自体は変更しない)、`er039_output/family_xy_concreteness_control_trial_02/`、`user_test/concreteness_trial_02/`(本文読み比べページ)、新規 `FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-02_REPORT.md`、`docs/pm/design_family_xy_concreteness_control_trial_02.md`、delegation_log。**Production code・正式Prompt・CURRENT_SPEC・routing は一切変更しない**。SSOT 4点は編集権なし(文案をRESULT_PACKETへ)。

## 性質/到達上限Status/禁止事項

- 性質: Trial。到達上限Status: `REJECTED` / `VALIDATED` / `USER_DECISION_REQUIRED`(Sonnetは判定案のみ、`VALIDATED` でもProduction実装へ進まない)。
- 費用: 上限¥70(Guardrail。テキスト生成+評価のみ、TTSなし)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。
- 禁止(ユーザー明示): Production code/正式Prompt/CURRENT_SPEC/routing変更、TTS、不要な再生成(Baseline A0 と Trial-01 の既存出力は再利用)、新規Product仕様の追加、A1/A2単独の再現性3回Trial、cleanup(後段rewrite)の追加Trial、「数字が少ないほど良い」評価、長い新規Prompt(T1は短い追加文のみ)。STOP条件(Essential Fact欠落/意味反転/因果関係の新規捏造/日本語にない固有名詞・数字を英語化で新規追加する構造的問題/既存Family A共有Prompt変更が必要/Production仕様判断が必要/Guardrail超過)に該当したら追加Trialせず報告。`git add -A`/stash/rebase/reset/amend/force push 禁止(push競合時は `git merge origin/main` のみ、conflictは中断報告)。APIキー本文表示禁止。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要。
T-0: 受領した委任文を `docs/pm/delegation_log/2026-09-28_FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-02_01.md` へ保存し `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-28_FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-02_01.md --json-out docs/pm/delegation_log/2026-09-28_FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-02_01.md_check.json`、結果1行記録。
T-2: TTSなし。
T-3: 上記「性質」欄の定型文に従う。

## ユーザー指示(原文)

「管理ID: FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-02。今回の目的は、数字・時刻・固有名詞をできるだけ減らしつつ、記事内容・因果関係・面白さを維持できる組み合わせを比較すること。前回の AN3 = A3 + N2 は、A3単体でMAJORが出た一方、AN3自体ではMAJORなし。したがってAN3は有力候補として継続評価。安全側比較として AN2 = A2 + N2 も追加。
1. Trial設計: 対象記事は Hormuz / Meta。日本語Writer側は2条件 AN3 = A3 + N2 / AN2 = A2 + N2。英語化側は2条件 T0: 現行英語化Prompt / T1: 数字・時刻・固有名詞を抑制するTrial限定Prompt。各記事について 2×2 Matrix(AN3-T0/AN3-T1/AN2-T0/AN2-T1)、計8セル。加えて各記事の Baseline = A0 + 現行英語化Prompt も必ず提示。
2. 英語化Prompt: T1はProduction Promptを変更せず、Trial限定で最小限の制約を加える。目的: 日本語記事で削減した数字・時刻・固有名詞を英語化工程で再び増やさない/日本語記事にない具体情報を英語化時に新規追加しない/翻訳・適応の自然さは維持/Essential Fact・因果関係・Storylineを変えない。長い新規Promptを作らず短い追加文のみ。
3. 固有名詞 9→19 の原因を事実確認(JA AN: 9、Advanced AN: 19): (1) JA側に存在しなかった固有名詞が英語化後に新規出現したのか (2) 同じ固有名詞の繰り返し回数が増えただけか (3) 日本語と英語でカウント単位・tokenizationが異なるだけか (4) 英語化Promptは何を入力として参照しているか(日本語記事のみか、Source/Ledger等も参照しているか) (5)「固有名詞をKEEPする」既存ルールの正確な意味と実際の挙動 (6) 増加元を具体的な名称単位で示す。名前ごとのJA→EN差分表(固有名詞/JA出現回数/EN出現回数/ENで新規追加か/備考)。総数だけで判断しない。
4. 評価: 各セルについて最低限、日本語記事全文/英語記事全文/数字数/過度な精度・時刻数/固有名詞数/JA→ENで新規出現した数字・固有名詞/Essential Fact欠落/因果関係逸脱/Ledger Deviation Check/Leakage Check/面白さ/読みやすさ/聞いた場合の理解しやすさ/現行Baselineとの差。「数字が少ないほど良い」評価は禁止。目標は数字・固有名詞を減らしながら記事内容・意味・面白さを維持すること。
5. ユーザー確認用成果物: Hormuz/Metaそれぞれ Baseline/AN3-T0/AN3-T1/AN2-T0/AN2-T1 を、ユーザーが記事本文を読み比べられる形で提示。可能なら差分も付けるが本文確認を優先。
6. 前回Trialの扱い: AN3継続/AN2新規追加/A1・A2単独の再現性3回Trialは実施しない/前回の単発後段cleanup rewriteはREJECTEDのまま/Cleanupの追加Trialは行わない/C1の思想「R1→R2で新しい数字・固有名詞を前景化しない」は評価対象に残すが主軸は2×2 Matrix。
7. Trial範囲: Production code変更禁止/正式Prompt変更禁止/CURRENT_SPEC変更禁止/routing変更禁止/TTS不要/不要な再生成禁止/既存Source・Ledger・関数を最大限再利用/新規Product仕様を勝手に追加しない。到達Statusは REJECTED/VALIDATED/USER_DECISION_REQUIRED のみ。
8. STOP条件: Essential Fact欠落/意味反転/因果関係の新規捏造/日本語にない固有名詞・数字を英語化で新規追加する構造的問題/既存Family A共有Prompt変更が必要/Production仕様判断が必要/Guardrail超過。
9. Closeout: 2×2 Matrix結果/Baseline比較/Hormuz・Meta本文比較/AN3 vs AN2/T0 vs T1/固有名詞9→19の原因/JA→EN新規追加の有無/数字・固有名詞削減量/Fact・因果・面白さ評価/Leakage・Deviation Check/Cost/Regression/最終Status/USER_DECISION_REQUIRED事項。目的は「最も減らせるPattern」ではなく「減らしながら内容を壊さない最適な組み合わせ」を見つけること。」

## Fable補足

- Trial-01資産の再利用: `er037_family_xy_concreteness_control_trial_01.py`(Pattern文言 A2/A3/N2、JA Writer/Advanced化/`run_deviation_check`/指標カウンタ/rubric)、`er037_output/family_xy_concreteness_control_trial_01/{meta,hormuz}/`(Baseline A0 の JA/EN 本文・指標、AN の JA/EN 本文=固有名詞 9→19 調査の実体)。REPORT `FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-01_REPORT.md` §5/§9、設計書 §1。Baselineは**再生成せず**既存 A0 出力を使う。AN3 は Trial-01 の AN 出力を再利用してよい(同一Pattern。ただし T1 英語化は新規実行)。AN2 は JA 新規生成。
- 手順: (1) 先に「固有名詞 9→19」調査を **read-only** で実施(Trial-01 の AN JA/EN 本文を名称単位で突き合わせ、Advanced化関数 `generate_advanced_adaptation` 等の入力[JA記事のみ/Source/Ledger参照の有無]と「固有名詞KEEP」ルールの原文をGrepで特定・逐語引用。tokenization差[JA形態素 vs EN大文字始まりトークン、"Strait of Hormuz" の複数トークン化等]を明示)。結果を設計書 §2 に表で記載してから Matrix 実行。(2) T1 追加文は短く(例: 「日本語記事に無い数字・時刻・固有名詞を新たに加えないでください。日本語記事で一般化されている表現は英語でも一般化したままにしてください。」相当。文言は設計書に逐語で記録)。T1 は Trial script 内で既存Advanced化Promptへ追記して呼ぶ(正式Prompt定数 sha256 不変 test)。(3) 8セル生成→各セルの指標(数字/過度精度/固有名詞[名称単位表付き]/JA→EN新規出現)、`run_deviation_check`(主判定)、既存 Leakage Check(Family B `run_analytical_leakage_check_3v` は Voice用のため不適なら、Family X 側の該当QAをGrepし無ければ「該当QAなし」と記録し、rubricで代替しない旨明記)、rubric 1 call/セル(面白さ・読みやすさ・聞いた場合の理解しやすさ・Baseline比の情報量、1〜5+根拠引用)。(4) C1思想の評価は、各セルの EN 本文に対して「Baseline比で新規前景化された数字・固有名詞」を数え、R2相当の掘り起こしが起きていないかを記録(R1→R2 の再実行はしない)。
- ユーザー確認用成果物: `user_test/concreteness_trial_02/index.html`(GitHub Pages。記事ごとに Baseline/AN3-T0/AN3-T1/AN2-T0/AN2-T1 の JA 全文・EN 全文をタブまたは並列で表示、各セルの指標小表、可能なら Baseline との単語diffハイライト)+同内容の Markdown `er039_output/.../comparison_{hormuz,meta}.md`。push後 `curl -sI https://shimomura055.github.io/eigo-radio/user_test/concreteness_trial_02/index.html` で200確認。
- 判定案: セルごとに「Deviation MAJOR あり→不合格」「MAJORなし→候補」とし、候補間は削減量と rubric の両方を並べる(数字最少を最良としない)。Sonnetは `VALIDATED` を自己宣言しない。

## 事前指定Read一覧

- `er037_family_xy_concreteness_control_trial_01.py`: Pattern定義・Writer/Advanced化呼び出し・指標関数(Grep `def |PATTERN` → 範囲)
- `er037_output/family_xy_concreteness_control_trial_01/{hormuz,meta}/` の A0/AN の JA/EN 本文と指標json(Glob)
- `FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-01_REPORT.md`:100-170
- Advanced化Prompt原文と入力(Grep `generate_advanced_adaptation|KEEP|固有名詞` -i in Family X/共有Writer module → 該当範囲。Family A と共有か確認)

## 実行コマンド全文

- `.venv\Scripts\python.exe er039_family_xy_concreteness_control_trial_02.py --article hormuz --cells AN3-T0,AN3-T1,AN2-T0,AN2-T1 --baseline-from "er037_output/family_xy_concreteness_control_trial_01/hormuz" --out-dir "er039_output/family_xy_concreteness_control_trial_02" --budget-jpy 70`
- `.venv\Scripts\python.exe er039_family_xy_concreteness_control_trial_02.py --article meta --cells AN3-T0,AN3-T1,AN2-T0,AN2-T1 --baseline-from "er037_output/family_xy_concreteness_control_trial_01/meta" --out-dir "er039_output/family_xy_concreteness_control_trial_02" --budget-jpy 70`(引数は実装に合わせ逐語記録)
- 固有名詞調査: `.venv\Scripts\python.exe er039_family_xy_concreteness_control_trial_02.py --investigate-entities --from "er037_output/family_xy_concreteness_control_trial_01/hormuz" --out "er039_output/family_xy_concreteness_control_trial_02/hormuz/entity_ja_en_diff.md"`(¥0)
- 単体test(¥0): `.venv\Scripts\python.exe -m pytest er039_family_xy_concreteness_control_trial_02_test_01.py -q`(T1追記が正式Prompt定数を変更しないこと[sha256]、名称単位差分表の生成、JA→EN新規出現検出)
- `.venv\Scripts\python.exe run_project_regression.py --pattern "er039*_test_*.py"`
- Production無変更の証拠: `git diff --stat HEAD -- "er0*.py" "er003_v1_translator_briefs/" | grep -v er039`(空)

## SSOT追記文

RESULT_PACKETへ文案のみ(REPORT_LEDGER新行、DECISION_LOG、OPEN候補、OPEN-220[Advanced Prompt側固有名詞抑制]への追記案)。

## Git(明示add対象・コミットメッセージ・trailer)

- add対象: `er039_*`、`er039_output/family_xy_concreteness_control_trial_02/`(md/json)、`user_test/concreteness_trial_02/`、REPORT、設計書、delegation_log+`_check.json`。SSOT編集権: なし。
- メッセージ: `FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-02: AN3/AN2 × T0/T1 の2×2 Matrix(Hormuz/Meta)+固有名詞9→19の実体調査+本文読み比べページ`、trailer `Management-ID: FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-02`。`git push origin main`。

## 報告(RESULT_PACKET項目)

ユーザー指定Closeout項目(2×2 Matrix結果/Baseline比較/本文比較の所在[Pages URL+md]/AN3 vs AN2/T0 vs T1/固有名詞9→19の原因[6点への回答+名称単位表]/JA→EN新規追加の有無/数字・固有名詞削減量/Fact・因果・面白さ評価/Leakage・Deviation Check/Cost/Regression/最終Status案/USER_DECISION_REQUIRED事項/Production無変更の証拠)+STOP該当有無+SSOT文案+commit hash+raw URL。ユーザー向け表記はStandard/Advanced。
