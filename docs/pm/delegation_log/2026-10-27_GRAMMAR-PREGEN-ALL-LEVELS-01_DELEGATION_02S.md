## 管理ID

GRAMMAR-PREGEN-ALL-LEVELS-01 委任_02S(Opus O-2/O-8/O-10に基づく前倒し作業: (A)Standard本文での文法候補抽出率の計測(DEV script、Production関数を無変更でimport、Production非接触、有料上限¥7)、(B)evidence元runの実現性確認(read-only: Family別にpagesまで追加TTSなしで到達できるrunの有無、到達不能時のkp以降正式runner実行の費用再見積、6セル非0件経路・2件採用1経路の計画)。並行Agent: GRAMMAR-PREGEN-ALL-LEVELS-01 委任_02(er120/er119_grammar_review実装中=読むのは`git show origin/main:<path>`のHEAD版)、KP-CONFIRMED-CONTENT-PROTECTION-01 委任_03(evidence)。Productionファイルは編集しない。あなたの所有=`docs/research/GRAMMAR-PREGEN-ALL-LEVELS-01/{STD_CANDIDATE_RATE_01,EVIDENCE_SOURCE_CHECK_01,EVIDENCE_PLAN_02}.md`+`tools/std_candidate_rate_01.py`+`std_rate_out/`(DEV出力、raw_usage_log不追跡)、`docs/pm/delegation_log/2026-10-27_GRAMMAR-PREGEN-ALL-LEVELS-01_DELEGATION_02S.md`(+check.json)、`docs/pm/RESULT_PACKET_GPG2S.md`(gitignore、`-f`禁止)。SSOT編集権なし。pathspec付きcommit。

## 性質/禁止

- 性質: 実装前の不確実性低減(計測+計画)。到達上限=計測結果+EVIDENCE_PLAN_02。
- 禁止: Prompt/閾値の変更(Std向けのlevel差込は別承認事項=試さない)、Production runの改変、Step B(解説生成)の実行(候補抽出Step A''のみ。Step Bの費用は既存実測値を使う)、¥7超過、禁止Git操作。
- 時間見込み: 約1.5h。

## 固定ブロック

従来どおり(E-1/D-1/G-1/F-1)。T-0: 委任文保存+check、結果1行。T-2(有料前): `py tools/stop_scope_check_01.py --managed-id GRAMMAR-PREGEN-ALL-LEVELS-01 --run-dir <scratch> --out <...>`、起動規律は単発scriptのため非該当(明記)。T-3: 費用実測。
T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-27_GRAMMAR-PREGEN-ALL-LEVELS-01_DELEGATION_02S.md` をN=718から順に試し、先頭「## 管理ID」+「GRAMMAR-PREGEN-ALL-LEVELS-01 委任_02S」のものを採用(同時刻に委任_02あり)。

## 実施事項

(A) **Std候補率計測(`STD_CANDIDATE_RATE_01.md`)**: 既存のStandard(a2)本文`article.md`を最大8本(X 3〜4記事、Y 1〜2記事、Z 2〜3作品。公開済み/evidence runから選定し出所を記録)に対し、`er120_part2_grammar_production_01`のStep A''(候補抽出)を**Production関数のまま**(Prompt sha不変、model=routing.SUPPORT_MODEL)DEV scriptから実行し、候補数・eligible数・Tier分布・候補文の例・費用/本・所要を集計。Advanced既存実測(X 3.0/Y 2.3/Z 0.7)と比較。0件率、B1〜B2向けPrompt(er120:55,118)とStd(A2)本文のミスマッチ所見(事実のみ、Prompt変更提案はしない)。上限¥7(Step A'' ¥0.26-0.88/call→最大8本)。
(B) **evidence元run実現性(`EVIDENCE_SOURCE_CHECK_01.md`)**: Family別に、現行runner世代で「Std/Adv本文・音声・pagesが揃い、kp stage以降を再実行しても本文TTSを再生成せず(KP音声のみ再生成)にpagesまで到達できるrun」を探す(候補: X `er019_output/family_x_audio_production_wiring_01/`配下の完成run、Y `run_style_fix_01`、Z `melos`/`after_twenty_years`等の完成run)。各runで必要stage・推定費用(KP音声TTS=KP件数×単価、Part 2 Step B=候補数×¥0.05-0.11、Step A''、RQA)、HR Lock/STOP残置、確定内容保護レコードの有無、Std/Advの文法候補≥1が見込めるか((A)の結果を使う)、2件採用を実証できる経路(候補≥2)を表にする。到達不能なFamilyは「kp以降を正式runnerで実行」の費用見積(本文TTS含む)。
(C) **`EVIDENCE_PLAN_02.md`**: 6セル(X/Y/Z×Std/Adv)それぞれの元run・stage列・非0件経路の実証方法・2件採用の実証経路(最低1)・0件セルの扱い(「非0件はmockのみ・runtime未観測」明記)・費用合計(上限¥150、300円以下=AI自律)・所要・起動規律(150秒・5分3回)・コピーdir方針(repo外)。方式B(新規記事)は次の通常制作に相乗り。

## 事前指定Read一覧

- `docs/research/GRAMMAR-PREGEN-ALL-LEVELS-01/{EVIDENCE_PLAN_01,COST_ESTIMATE_01,CURRENT_FLOW_01}.md`、`docs/research/KP-CONFIRMED-CONTENT-PROTECTION-01/{EVIDENCE_Y_01,EVIDENCE_PLAN_01}.md`、`docs/research/KP-PHRASE7-WORD5-PRODUCTION-01/{EVIDENCE_01,COST_01}.md`
- `er120_part2_grammar_production_01.py`(HEAD版: Grep `def extract|STEPA|paragraphs_from_article_md|eligible|Tier|MODEL` ±10)、`er121_family_y_runner_01.py:30-60`(STAGE_EST_JPY)、`er019_output/part2_hr_evidence_01/run_r1/a2/article.md`(Std本文例)
- run一覧: `Get-ChildItem er019_output/family_x_audio_production_wiring_01, er121_output/family_y_production_01/*, er026_output/family_z_production_e2e_01/*`(dir名・更新日・pages/audioの有無のみ)

## 実行コマンド全文

- `py docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-27_GRAMMAR-PREGEN-ALL-LEVELS-01_DELEGATION_02S.md --json-out ...\_check.json`
- DEV script: `.venv\Scripts\python.exe docs\research\GRAMMAR-PREGEN-ALL-LEVELS-01\tools\std_candidate_rate_01.py --articles <list> --out docs\research\GRAMMAR-PREGEN-ALL-LEVELS-01\std_rate_out\ --budget-jpy 7`
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## SSOT追記文

編集権なし。`RESULT_PACKET_GPG2S.md`にOPEN-559追記文案(Std候補率実測・evidence計画v2・費用)。

## Git

- commit message: `GRAMMAR-PREGEN-ALL-LEVELS-01 委任_02S: Std本文の文法候補率計測(Step A''のみ、実費¥N)+evidence元run実現性確認+EVIDENCE_PLAN_02(上限¥150)`。trailer: `Delegation: GRAMMAR-PREGEN-ALL-LEVELS-01/02S`。push。

## 報告

`docs/pm/RESULT_PACKET_GPG2S.md`: (0)T-0、(1)Std候補率表(本文別候補数・0件率・例・費用)、(2)元run実現性表、(3)EVIDENCE_PLAN_02要点(6セル・費用)、(4)判断候補(Std 0件率が高い/難度不一致の事実があれば「D-a(2) Prompt変更=別承認事項」として材料のみ整理、提案はしない)、(5)必須4行+「判定整合: 重大NG=<なし|あり>」、(6)SSOT文案、commit hash・raw URL。末尾5行要約。