## 管理ID

KP-CANDIDATE-PHRASE7-WORD5-TRIAL-02 委任_01(ユーザー指示によるKP候補生成Trial再実施: 単語抽出Promptの優先順位是正+単語5件化。前回`KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01`の成果物・P7結果を最大限再利用し、各レベル1回実行。Production不変)。並行Agent: FAMILY-Y-STYLE-PROFILE-FIX-01 委任_02(`er121_*`・`user_test/..._03`・`er121_output/...run_style_fix_01`)、TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_02(`er127_*`、`er020`/`er003_v1_*`/`er122`/`er006`等のleaf)。あなたの所有=`er124_kp_phrase_word_trial_01.py`(Trial専用module。W5 Prompt追加・P7結果再利用経路の追加のみ)、新規test(DefaultOffIsolation型)、`docs/research/KP-CANDIDATE-PHRASE7-WORD5-TRIAL-02/**`、`docs/pm/delegation_log/2026-10-26_KP-CANDIDATE-PHRASE7-WORD5-TRIAL-02_{USER,DELEGATION_01}.md`(+check.json)、`docs/pm/RESULT_PACKET_KPT2.md`。**Production module(`er119_*`/`er105_*`/`er003_*`/`er125_*`)編集禁止**。SSOT編集権なし。pathspec付きcommit。git index.lock競合は10秒待って再実行(最大3回)。

## 性質/到達上限Status/禁止事項

- 性質: Offline Trial(候補生成方式の比較)。到達上限Status=VALIDATED/REJECTED/USER_DECISION_REQUIRED(Fable判定)。Production採用・配線はScope外。前回7+3方式を正式採用済みとして扱わない。
- 禁止: Production Prompt/正式経路/retry/fallback/Gate/`KP_CANDIDATE_MAX`の変更、過去記事・HR確定結果の変更、Family YへのProduction適用、本文再生成、単語自動採用枠・単語優先ルールの導入、評価基準(前回自ルーブリックR1〜R5・Y/B/N・事前判定基準)のAI独自変更、`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・`git checkout -- <file>`。
- 費用: 上限¥40(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。
- 費用/日次: 当日既使用約JPY563(+並行Y再生成≤60)/本委任見積JPY10〜20(W5 6 call+単語のcanonicalization/gloss/RQA+judge 6 call。P7は再利用で0)/改善見込み高/承認区分: C(ユーザー指示Trial、300円以下)。
- Opus独立技術レビューGate: 非該当(Trial、新フローなし)。
- 修正範囲の線引き(11-8): 範囲内=Trial moduleへのW5 Prompt追加・P7再利用・比較集計。範囲外=Production変更一切。
- モデル: 候補生成・canonicalization・gloss・RQA=gpt-6-luna(Production SUPPORT_MODEL=前回と同一、比較条件統一のため最新最上位でない例外)、judge=gpt-6.1-sol(最新)。報告に明記。
- 時間見込み: 約2h(Prompt是正+再利用経路+test 40分/実行(6レベル並列)20分/自ルーブリック+judge 30分/集計・文書30分)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25): 本委任はTTSなし。
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`、ユーザー正式決定、費用上限[Cap]を伴う全委任で常時有効): 費用上限[Cap]は「暴走防止のためのGuardrail」であり、Cap到達=自動STOPではない。禁止事項/性質欄の費用上限記載は次の定型文に従う。「上限¥X(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。」旧来の「上限¥X、超えそうなら実行前STOP」のみの記載(継続条件・STOP条件の書き分けが無いもの)は使用しない。ユーザー承認済みの総予算・個別run上限・STOP条件を優先し、Fable/Workerが独自に過度に厳しい停止条件を追加しない(2026-10-05)。

T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-26_KP-CANDIDATE-PHRASE7-WORD5-TRIAL-02_DELEGATION_01.md` をN=679から順に試し、先頭「## 管理ID」+「KP-CANDIDATE-PHRASE7-WORD5-TRIAL-02 委任_01」のものを採用。ユーザー原文(下記)を`..._USER.md`へ逐語保存。

## ユーザー指示(原文・逐語)

# 【Claude Code指示】Key Phrase候補生成 Trial再実施｜7フレーズ＋5単語

## 1. 目的・背景

前回の `KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01` では、単語抽出Promptの優先順位がユーザー指定と異なっていた。

具体的には、「単語単体の学習価値」が3位の必須条件となり、「上級者向けの学習価値」「易しい語の除外」より優先されていた。

これはユーザーの意図と異なる。

今回はこの不整合を修正し、さらに単語候補数を3件から5件に増やして再Trialを行う。

**目標：上級者にとって本当に学習価値の高い候補を、数合わせによる品質低下なく、十分な数だけ確保する。**

Status：Trial。到達可能StatusはVALIDATED／REJECTED／USER_DECISION_REQUIRED。Production採用・実装は今回のScope外。

## 2. 候補生成方式

- フレーズ・表現・Idiom：最大7件
- 単語単体：最大5件
- 合計：最大12件／レベル
- いずれも学習価値の高い順に順位付けする。
- 条件を満たす候補が不足する場合は、要求数未満でよい。
- 数合わせのために品質を引き下げることは禁止。

フレーズ抽出の仕様は前回Trialから変更しない。

## 3. 単語抽出Prompt（優先順位厳守）

以下の5条件を、**記載順に適用すること。順番を入れ替えたり、必須条件を追加したりしないこと。**

1. **本文一致（絶対条件）**：本文中に実在する単語だけを、本文に現れる形のまま抜き出す。変更・言い換え・追加・創作は禁止。
2. **1語（絶対条件）**：スペースを含まない1語だけを出力する。2語以上は出力禁止。
3. **上級者向けの学習価値**：上級者でも学ぶ価値のある単語を優先。
4. **易しい語の除外**：基本語や、上級者なら知っている易しい単語は除外。
5. **単語単体の学習価値**：意味の明確さ・汎用性・難易度を考慮する。ただし必須条件にはしない。

補足：

- ③④を⑤より必ず優先する。
- ⑤を理由に、③④に適合する単語を不当に除外しない。
- 既存フレーズに含まれる単語であっても、それだけを理由に一律除外しない。学習価値の重複は評価するが、新たな絶対条件にはしない。
- 本文一致と1語条件は必須。既存の承認済みGateは維持する。
- Promptの最終文面と条件の優先順位を、API実行前に自己点検する。

## 4. Trial対象・比較条件

前回と同じ3記事、各Standard／Advancedの計6レベル。

1. Family X『AIの仮想の島』
2. Family X『英国の電車マナー』
3. Family Z『猿の手』

既存の確定本文を再利用し、本文の再生成はしない。

前回Trialのデータを比較対象として再利用する。

今回は原則として各レベル1回ずつ実行する。再現性に疑義がある場合のみ、承認された予算・Scope内で合理的な追加実行を検討する。

Family YへのProduction適用は行わない。

## 5. 検証・評価

各レベルについて次を比較する。

- 前回P7＋W3と今回P7＋W5のフレーズ／単語の候補数
- 抽出された候補の全文・順位・学習価値・選定理由
- 本文一致、1語条件への適合
- 上級者向け語彙としての適切さ
- 易しい単語がどれだけ除外されているか
- 数合わせによる品質低下の有無
- 既存Gateによる除外結果
- 候補数増加による費用・処理時間への影響

特に、前回抽出された `performance`、`audience`、`responsibility` 等の比較的易しい単語が、今回どのように扱われるか確認すること。

これらを個別に禁止するのではなく、③④の条件が実際に機能するかを評価する。

**フレーズ抽出結果と単語抽出結果は別々に評価する。**

前回の7フレーズ方式で確認できた有効性は、不必要に再検証しない。変更しないPrompt・本文・入力条件については、既存結果を再利用して費用と時間を削減する。

## 6. Production・Human Reviewとの境界

今回は候補生成方式のTrialであり、正式なKey Phrase 5件の採用ルールは変更しない。

- 単語の自動採用枠は設けない。
- フレーズより単語を優先する新ルールは導入しない。
- 最終5件の正式採用順位・Human Review仕様は変更しない。
- Production Prompt、正式経路、retry／fallback、既存Gateは変更しない。
- 過去記事やHuman Review確定結果は変更しない。

候補12件と既存候補上限の関係はTrial側で安全に処理し、Production設定を無断変更しない。

## 7. QCD・実施方針

品質 ＞ Delivery ＞ 量産単価。

- 前回成果物・確定本文・評価データを最大限再利用する。
- 独立したレベルのTrialは原則並列実行する。
- 不要な日付分割・待機・逐次処理は行わない。
- 既存予算・日次1,000円（JST）を遵守し、実費を記録する。
- 不具合は承認範囲内で原因究明・修正・再検証する。
- 前回の品質基準をAI独自判断で変更しない。

## 8. 報告・Closeout

報告は次の順序とする。

1. 結論：7＋5方式は成功したか。
2. **6レベルの候補全文一覧（フレーズ・単語を区分し、順位・Y/B/N評価付き）**
3. 特に単語5件の品質評価。③④の条件が守られているか。
4. 前回7＋3方式との比較。改善・悪化した点。
5. Gate除外・不適切候補・数合わせの有無。
6. QCD影響（費用・処理時間・量産単価）。
7. Fable独立評価。
8. Production採用の推奨と残るユーザー判断。

Trial終了後、Gate 1に従いStatusを確定し、OPEN_ITEMS／DECISION_LOG等のSSOTとGitへ反映する。

**VALIDATEDでもProduction採用・配線へ自動移行しない。ユーザーの明示的な採用判断を待つこと。**

前回の7＋3方式を正式採用済みとして扱わないこと。

(原文ここまで)

## Fableの実施指示

1. **前回W3 Promptの事実確認(`PROMPT_DIFF_01.md`)**: `er124_kp_phrase_word_trial_01.py`のW3 Prompt全文(sha256先頭`7a9c47a01410bd9f…`)を引用し、条件の記載順・必須/任意の区別を事実として示す。ユーザー指摘「単語単体の学習価値が3位の必須条件で、上級者向け学習価値・易しい語除外より優先」が当てはまるかを原文で確認し、当てはまる/当てはまらない/部分的に、を証拠付きで記録(推測禁止)。
2. **W5 Prompt作成**: ユーザー§3の5条件を**記載順そのまま**(①本文一致[絶対]②1語[絶対]③上級者向け学習価値④易しい語の除外⑤単語単体の学習価値[必須にしない])で構成し、補足4点(③④>⑤/⑤で③④適合語を不当除外しない/既存フレーズ含有語を一律除外しない・重複は評価のみ/本文一致と1語は必須)を反映。最大5件、学習価値順、不足時は5件未満可、数合わせ禁止を明記。前回W3の「フレーズ候補を入力して重複を避ける」構造は維持(含有語の一律除外にならない文言へ)。それ以外(出力形式・gloss・選定理由)は前回W3と同一。**API実行前に自己点検表**(条件順・必須/任意・追加条件なし)を`PROMPT_SELFCHECK_01.md`に記録し、sha256を固定。
3. **P7結果の再利用**: 前回`trial_runs_01.json`のr1のP7返答(フレーズ候補・Gate結果・自判定・judge)を各レベルの固定入力として再利用(フレーズ側は再実行しない。費用0)。W5にはr1のP7句を入力。レベルごとに1回実行(6 call)。6レベルは並列起動可(rate limitは`--help`/既存runnerの並列設定に従う)。
4. **Gate**: 前回と同一(Production関数import: validate[本文連続一致・1語・有限助動詞・数値]/CMU/containment/canonicalization/gloss再整合/RQA)。候補12件と`KP_CANDIDATE_MAX=8`の関係はTrial側で安全処理(上限を超えた分も全件評価し、Production上限に触れない)。DefaultOffIsolation型test: Trial moduleがProduction経路へ到達しないこと、Production差分0。
5. **評価**: 自ルーブリック(前回R1〜R5・Y/B/N)をjudge前に確定。単語側は追加で「③④適合」列(上級者向けか/易しい語か)を評価し、前回W3で出た`performance`・`audience`・`responsibility`・`discovery`・`Strategy`・`technique`・`carriage`・`automatically`が今回どう扱われたか(出現/不出現/順位)を個別に記録。judge=gpt-6.1-sol(匿名シャッフル、単語のみ新規。フレーズは前回judge再利用)。**フレーズと単語を別々に評価**。
6. **比較(`COMPARISON_02.md`)**: レベル別8行表(前回現行/前回P7+W3 r1/今回P7+W5)+単語側の専用表(件数・Y/B/N・③④適合率・易しい語の件数・前回易語の扱い)+総括表(前回COMPARISON_01 §1形式)。費用・時間・単価影響(W5 call増分、canonicalization/gloss入力増)。
7. **Status案(`STATUS_02.md`)**: 事前基準(前回DESIGN_01 §8と同一+単語側: 単語Yが≥3件のレベル数、易しい語(自N)の割合が前回W3より低下)に照らしてVALIDATED/REJECTED/判断候補を提案(最終判定はFable)。残るユーザー判断(採用可否・有用の閾値・単語枠の扱い)を列挙。

## 事前指定Read一覧

- `docs/research/KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01/{DESIGN_01,COMPARISON_01,STATUS_01}.md`、`trial_runs_01.json`(構造のみ)、`own_rubric_01.json`
- `er124_kp_phrase_word_trial_01.py`: Grep `W3|PROMPT_W|generate|judge|report|KP_CANDIDATE_MAX` → ±15

## 実行コマンド全文

- `py docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-26_KP-CANDIDATE-PHRASE7-WORD5-TRIAL-02_DELEGATION_01.md --json-out ...\_check.json`
- Trial実行: `.venv\Scripts\python.exe er124_kp_phrase_word_trial_01.py …`(サブコマンド・引数は`--help`で実値確認し全文記録。W5は`--word-prompt w5 --reuse-p7 <trial_runs_01.json> --runs 1`相当)
- test: `.venv\Scripts\python.exe run_project_regression.py --pattern "er124*_test_*.py"`(接続0)
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## SSOT追記文

SSOT編集権なし。`RESULT_PACKET_KPT2.md`(9)にOPEN-534更新文案(Trial-02結果、Status案)、DECISION_LOG案。

## Git

- add対象: `er124_kp_phrase_word_trial_01.py`、新規test、`docs/research/KP-CANDIDATE-PHRASE7-WORD5-TRIAL-02/`配下(`RESULT_02.md`[6レベル候補全文]、`COMPARISON_02.md`、`STATUS_02.md`、`PROMPT_DIFF_01.md`、`PROMPT_SELFCHECK_01.md`、`trial_runs_02.json`、`own_rubric_02.json`、`judge/`、`gate_results_02.json`、usage log)、`docs/pm/delegation_log/...`。pathspec付きcommit。
- commit message: `KP-CANDIDATE-PHRASE7-WORD5-TRIAL-02 委任_01: 単語Prompt優先順位是正(ユーザー§3順)+W5化、P7再利用、6レベル×1回、実費¥X(Production不変)`
- trailer: `Delegation: KP-CANDIDATE-PHRASE7-WORD5-TRIAL-02/01`
- push: `git push origin HEAD:main`(non-ffなら fetch→merge --no-edit→push。競合はSTOP報告)。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_KPT2.md`: ユーザー§8の順序(1結論/2 6レベル候補全文[フレーズ・単語区分・順位・Y/B/N]/3単語5件の品質・③④遵守/4前回比較/5 Gate除外・不適切・数合わせ/6 QCD/7 Fable評価用の材料/8 採用推奨案と残るユーザー判断)+(0)T-0、PROMPT_DIFFの事実、必須4行+「判定整合: 重大NG=<なし|あり>」、一覧外Read、commit hash、raw URL。末尾10行要約。