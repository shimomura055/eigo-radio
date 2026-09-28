## 管理ID

FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-01(ユーザー承認済みTrial、Trialのみ)。一時ファイル `docs/pm/ACTIVE_TASK_CC1.md` / `docs/pm/RESULT_PACKET_CC1.md`(commitしない)。並行衝突: 別Sonnetが `TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01`(`er038_*`、`er038_output/`、`user_test/tts_all_role_style_trial_01/`、`TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01_REPORT.md`)を実行中 → これらに触れない。本タスクの所有: 新規 `er037_family_xy_concreteness_control_trial_01*.py`(+test)、`er037_output/family_xy_concreteness_control_trial_01/`、新規 `FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-01_REPORT.md`、`docs/pm/design_family_xy_concreteness_control_trial_01.md`、delegation_log。**Production code・CURRENT_SPEC・正式Prompt(`er0*.py`既存ファイル、`er003_v1_translator_briefs/`等のPromptファイル)は一切変更しない**(import/読み込みによる流用のみ)。SSOT 4点(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/`docs/pm/REPORT_LEDGER.md`)は**編集権なし**(追記文案をRESULT_PACKETへ)。

## 性質/到達上限Status/禁止事項

- 性質: Trial(Production実装なし)。到達上限Status: `REJECTED` / `VALIDATED` / `USER_DECISION_REQUIRED` のいずれか(Sonnetは判定案のみ、`VALIDATED` でもProductionへ実装しない)。
- 費用: 上限¥80(Guardrail、テキスト生成+LLM評価のみ、TTS/ASRなし)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。
- 禁止(ユーザー明示): Production正式path変更/Production default routing変更/CURRENT_SPECをProduction採用済みとして更新/retry・fallbackの正式仕様変更/新しい仕様候補の勝手な追加実装/新規記事生成(Meta・Hormuzの既存Source/Ledgerを使う)/Trialのためだけの必要以上の再生成/新しい名称・原則の安易な新設/過剰な長文Prompt/「数字が少ないほど高得点」の単純評価。STOP条件(Essential Factが落ちる/意味・因果関係が変わる/Prompt追加で記事品質が明確に劣化/既存仕様と競合/新しいProduct仕様判断が必要)に該当したら追加Trialを増やさずSTOP報告。`git add -A` 禁止、履歴書き換え禁止、APIキー本文表示禁止。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要。
T-0: 受領した委任文を `docs/pm/delegation_log/2026-09-28_FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-01_01.md` へ保存し `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-28_FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-01_01.md --json-out docs/pm/delegation_log/2026-09-28_FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-01_01.md_check.json`、結果1行記録。
T-2: TTSなし(テキストのみ)。
T-3: 上記「性質」欄の定型文に従う。

## ユーザー指示(原文)

「共通前提: 今回の作業はTrialのみ。ユーザーはまだProduction採用を決めていない。Trial終了時は必ずREJECTED/VALIDATED/USER_DECISION_REQUIREDのいずれかに分類してSTOP。VALIDATEDでもProductionへ実装しない。Production code / CURRENT_SPEC / 正式Promptへの変更は禁止。着手前にCURRENT_SPEC / DECISION_LOG / OPEN_ITEMS / 既存Trial / Production codeを確認し、既存仕様・過去Trialとの重複を整理。新しい名称や原則を安易に作らない。
Task A — 記事の数字・時刻・固有名詞 前景化抑制Trial。目的: Family X / Yで確認された、細かい数字・正確すぎる時刻・不要な固有名詞が記事理解に必要以上に前景化され、音声として聞きづらくなる問題を改善する。HormuzではOriginal時点で既に数字が多く、R1→R2でさらにLedger内の細かい数字・時刻が掘り起こされていることを確認済み。Trial対象(必須): Meta記事、Hormuz記事。既存の同一Source/Ledgerを使い条件比較できるようにする。新規記事は不要。
A. Initial Writer Prompt Trial: 現行をBaselineとして追加文言だけを変える複数Patternを比較。最低限: A0 現行(追加なし)/A1「記事の理解に必要な数字だけを使ってください。」/A2「細かい数字や時刻は基本使わず、話の理解に必要な場合だけ使ってください。」/A3「数字・時刻は基本的に使わないでください。記事の理解に本当に必要な場合だけ、最小限に使ってください。」/A4「数字・時刻は原則使わないでください。省くと話の意味が変わる場合に限り、必要最小限だけ使ってください。」/A5「数字・時刻は原則書かないでください。主旨の理解に不可欠なものだけ、最小限残してください。」。課題は数字だけでなく固有名詞も対象。固有名詞についても、なるべく単純な追加文言で同様の抑制を検証。過剰な長文Promptにしない。「最小限の指示でどこまで効くか」を見る。
B. 後段cleanup Trial: 過去のFamily A等に、数字・具体情報の後処理/cleanupに類する既存方式がないか先に確認。存在すれば再利用を優先し新方式を勝手に作らない。目的は意味・因果関係・Storyline・Essential Factを保持したまま、聞き取りに不要な細かい数字・時刻・固有名詞を削減すること。
C. R1→R2 Entertainment Revision改善: 現行Revision Promptとの比較Trial。改善側では、Entertainment性を上げるために新しい数字・時刻・固有名詞をLedgerから掘り起こさない/面白さは構成・対比・場面・人間の反応・テンポ等で作る/Fact自体は変えない、という方向を可能な限り短いPromptで試す。Family YのVoice/Reaction系Trialの考え方も参照(Family Y専用仕様をそのままProduction仕様化しない)。
評価: 数字総数/時刻・過度な精度の数/固有名詞数/Original→R1→R2で新規に前景化された数字・固有名詞/Essential Fact欠落の有無/Storyline・因果関係維持/Entertainment性/一度聞いただけで理解しやすいか/現行比で情報が薄くなりすぎていないか。単純な「数字が少ないほど高得点」にしない。
Closeout報告(12項目): 1 Existing Spec/Prior Trial確認結果 2 実施Pattern 3 Baselineとの差 4 成果物 5 定量結果 6 品質評価 7 Regression 8 コスト 9 新しく判明した問題 10 REJECTED/VALIDATED/USER_DECISION_REQUIRED 11 ユーザー判断が必要な事項 12 Production変更が一切入っていない証拠。Closeout時に未報告Trial/未処理USER_DECISION_REQUIRED/TrialからProductionへ誤って入った変更/Dangling Reference/SSOT・Open Item記録漏れがないことも確認。」

## Fable補足(Existing Spec Check の入口)

- Family体系: Active=X/Y/Z、A/B/C=legacy(read-only参照可、変更不可)。Family Yは着手済み実装なし(Family B Voices記事はTrial参照のみ)。本TrialはFamily X記事(Meta/Hormuz、`er019_output/family_x_audio_production_wiring_01/` 配下の既存run: Hormuz `hormuz__run_0x`、Meta の run。Original/R1/R2の本文artifact・Ledger・Storyline/B3 Fact選定結果を特定)を入力に使う。
- Family Xの既存名称: 「Storyline決定+B3 Fact選定」(`er019_family_x_storyline_b3_fact_selection_01.py`)、Fact Ledger(`[VERIFIED] fact_id:` 形式)、R1→R2 Entertainment Revision(英語本文側のR1→R2実装をGrep `r1|r2|revision|entertain` -i in `er019_*.py`/`er003_v1_n3_01_articles_generate.py` で特定。JA側は `er019_family_x_ja_writer_o_r1_r2_01.py`)、Fact Check/Essential Fact判定の既存関数(Grep `fact_check|essential` -i)。これら正式名称をそのまま使い、新名称を作らない。
- 過去Trial・既存仕様の重複確認: `DECISION_LOG.md`/`OPEN_ITEMS.md`/`CURRENT_SPEC.md` を Grep `数字|時刻|固有名詞|concrete|numeric|cleanup|simplif|前景` で確認。Family A legacy の後処理(Grep `cleanup|postprocess|simplify|number` -i in `er0*.py` の A系runner/Writer)に「数字・具体情報の後処理」があれば B で再利用(関数呼び出し、変更なし)。無ければ「該当なし」と記録し、Bは既存R1→R2の枠組みで「削減指示のみ」の最小Promptを1 Patternに限定(新方式の設計はしない)。
- Family Y参照: `docs/pm/design_family_y_voice_structure_trial_01.md`、`FAMILY-Y-VOICE-STRUCTURE-TRIAL-01_REPORT.md` §5/§8(R2が割当Fact原文から数字・固有名詞を掘り出した観測)。
- 実施計画(QCD): レベルは **Advanced(B1B)を主**とし、A0〜A5+固有名詞Pattern(N1「固有名詞は、記事の理解に必要なものだけを使ってください。」、N2「人名・企業名・地名などの固有名詞は、話の理解に必要な場合だけ使い、それ以外は一般的な言い方にしてください。」の2案)+数字・固有名詞の組合せ1案(最も効いたA系+N系)を2記事で実施。Standard(A2)は最良1〜2 Patternのみ追試。C(R1→R2)は現行Revision Prompt vs 改善Prompt(短文1案、必要なら2案)を各記事Advancedで実施。A0(Baseline)は既存artifactがあれば再生成しない。各生成はProductionと同じWriter関数・同じmodel・同じLedger入力で、追加文言だけを差し込む(Trial script内で組み立て、正式Promptファイルは無変更)。
- 評価(決定論+LLM): 決定論=数字トークン数(桁数字・数詞)、時刻/日付/小数・%等の「過度な精度」件数、固有名詞数(大文字始まりトークン集合、既存 `er025`/`er006` の entity_like 判定器を流用可)、Original→R1→R2で新規出現した数字・固有名詞(Ledger原文照合)、語数。LLM評価=既存Family X Fact Check/Essential Fact判定関数を流用してEssential Fact欠落有無(流用不可なら1 call rubric)、+1 call rubric(Storyline/因果維持、Entertainment性、一度聞いて理解しやすいか、情報の薄さ、各1〜5+根拠引用)。**「数字が少ないほど良い」にしない**: Essential Fact欠落・因果変化があれば当該Patternを不合格。
- 判定案は Pattern×記事×レベルの表で示し、Sonnetは `VALIDATED` を自己宣言しない。

## 事前指定Read一覧

- `CURRENT_SPEC.md` Family X節(Grep `## Family X` → 節範囲、特にWriter/Storyline/B3/R1→R2/Fact Check)
- `er019_family_x_storyline_b3_fact_selection_01.py`(関数signature、Grep `def `)
- Family X英語Writer/R1→R2/Fact Checkの該当関数(Grep結果の範囲のみ)
- Meta/Hormuz の既存artifact: `er019_output/family_x_audio_production_wiring_01/**/{article*.md,ledger*,storyline*,fact*}`(Glob)。Original/R1/R2の対応関係を `audit/` から特定。
- `docs/pm/design_family_y_voice_structure_trial_01.md` §B〜§E
- `FAMILY-Y-VOICE-STRUCTURE-TRIAL-01_REPORT.md`:61-118

## 事前指定Grep一覧+追記位置・更新位置の手順

- 上記Grep群。結果を設計書 §1(Existing Spec/Prior Trial Check: 分類A/B/C、既存名称対応表、Family A cleanup既存方式の有無)に記載してから実装。
- Trial script `er037_family_xy_concreteness_control_trial_01.py`: `--article {meta,hormuz} --level {a2,b1b} --patterns A0,A1,...,N1,N2,AN --revision {current,improved} --out-dir ... --budget-jpy`。出力: Pattern毎の本文、決定論指標json、LLM評価json、`summary.json`/`summary.md`(比較表)。
- Dangling Reference Check: Grep `er037_|concreteness_control` 全体。

## 実行コマンド全文

- `.venv\Scripts\python.exe er037_family_xy_concreteness_control_trial_01.py --article hormuz --level b1b --patterns A0,A1,A2,A3,A4,A5,N1,N2 --out-dir "er037_output/family_xy_concreteness_control_trial_01" --budget-jpy 80`
- `.venv\Scripts\python.exe er037_family_xy_concreteness_control_trial_01.py --article meta --level b1b --patterns A0,A1,A2,A3,A4,A5,N1,N2 --out-dir "er037_output/family_xy_concreteness_control_trial_01" --budget-jpy 80`
- 組合せ(最良A+N)と Standard追試、Revision比較(`--revision current` / `--revision improved`)は上記結果を見て実行(実行したコマンドを逐語記録)。
- 単体test(¥0、mock): `.venv\Scripts\python.exe -m pytest er037_family_xy_concreteness_control_trial_01_test_01.py -q`(指標カウンタ、Ledger照合の新規前景化検出、Pattern文言が正式Promptファイルを変更しないこと[ファイルhash不変]のassert)
- `.venv\Scripts\python.exe run_project_regression.py --pattern "er037*_test_*.py"`
- Production無変更の証拠: `git diff --stat HEAD -- "er0*.py" "er003_v1_translator_briefs/" | grep -v er037`(空であること)を逐語記録。

## SSOT追記文

RESULT_PACKETへ文案のみ: REPORT_LEDGER新行(Trial、Status案)、DECISION_LOG(Trial実施記録、ユーザー指示要旨、Status案、Production採用未決)、OPEN_ITEMS候補(新発見問題のみ)。CURRENT_SPEC変更なし。

## Git(明示add対象・コミットメッセージ・trailer)

- add対象: `er037_*`、`er037_output/family_xy_concreteness_control_trial_01/`(md/json)、REPORT、設計書、delegation_log+`_check.json`。他Agent差分・SSOTは一切addしない。SSOT編集権: なし。
- メッセージ: `FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-01: 数字・時刻・固有名詞の前景化抑制Trial(Writer Prompt A0-A5/N1-N2、cleanup、R1→R2改善、Meta/Hormuz)`、trailer `Management-ID: FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-01`。`git push origin main`。

## 報告(RESULT_PACKET項目)

ユーザー指定12項目(1 Existing Spec/Prior Trial確認結果[分類・既存名称対応表・Family A cleanup既存方式の有無] 2 実施Pattern[逐語] 3 Baselineとの差 4 成果物path 5 定量結果表[Pattern×記事×レベル: 数字総数/過度精度件数/固有名詞数/新規前景化数/語数] 6 品質評価[Essential Fact欠落・因果維持・Entertainment・理解しやすさ・情報の薄さ、根拠引用] 7 Regression 8 コスト実測(call数・¥) 9 新しく判明した問題 10 Status案 11 ユーザー判断が必要な事項 12 Production変更が一切入っていない証拠[git diff結果])+STOP該当有無+SSOT文案+commit hash+raw URL。ユーザー向け表記はStandard/Advanced。
