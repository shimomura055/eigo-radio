## 管理ID

PM-SSOT-SYNC-14(KP-CANDIDATE-PHRASE7-WORD5-TRIAL-02の訂正[救済機構による交絡の明記]+Fable判定のSSOT反映。API 0・JPY0)。並行Agent: FAMILY-Y-STYLE-PROFILE-FIX-01 委任_02(`er121_*`等)、TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_02(`er127_*`・leaf)。**SSOT編集権は本委任のみ**(8-Y)。所有=`OPEN_ITEMS.md`・`DECISION_LOG.md`・`docs/pm/USER_DECISION_REGISTER_01.md`・`docs/pm/ACTIVE_TASK.md`・`docs/research/KP-CANDIDATE-PHRASE7-WORD5-TRIAL-02/{COMPARISON_02,STATUS_02,RESULT_02}.md`(訂正追記のみ)・`docs/pm/delegation_log/2026-10-26_PM-SSOT-SYNC-14_DELEGATION_01.md`(+check.json)・`docs/pm/RESULT_PACKET_SSOT14.md`。pathspec付きcommit。index.lock競合は10秒待って再実行(最大3回)。worktree SSOTがHEADより古ければHEAD blobを書き戻してから自hunk追加。

## 性質/禁止

- 性質: 事実訂正+SSOT同期。到達上限=SYNCED。
- 禁止: SSOT全文読込、Production/Trial moduleの編集、判定語の格上げ、`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・`git checkout -- <file>`。
- 時間見込み: 約40分。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要。
T-0(2026-09-13、全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果をRESULT_PACKETへ1行記録する(FAILでも継続)。
T-2: TTSなし。T-3: 費用なし。

T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-26_PM-SSOT-SYNC-14_DELEGATION_01.md` をN=680から順に試し、先頭「## 管理ID」+「PM-SSOT-SYNC-14」のものを採用。

## 1. 訂正(Fableが一次情報で確認した事実)

Trial-02のフレーズ側で、Trial-01(r1)ではcanonicalizationで除外された4句(`given written permission`・`pulling free`・`pulled free`・`accept no responsibility`)が最終候補に残った理由を、委任_01報告は「LLM再実行の揺れ」としたが、**誤り**。実際は本日PRODUCTION_WIREDとなったKP救済機構(`er125_kp_rescue_production_01.py`、既定ON)が発火して救済したもの(証拠: `runs/monkeys_paw__a2__p7w5__r1/trial_result.json:500-601` `"rescued": true`・`"rescued_key": "pulling free"`・`"rescue_note": "修正済み(元: pulling free / REVERT_SURFACE)"`・`:1391 "rescued_not_auto"`・`:1398 "rescue_enabled": true`、`kp_candidates/round_1/work/canonicalization_runtime_metadata.json:129-135 "kp_rescue"`)。また委任_01報告の「`er125`は不在のためスキップ」も誤り(HEADに存在)。
- 各runの`trial_result.json`で`rescued: true`の候補を全件列挙(句・run・rescue_codes・auto可否[`rescued_not_auto`])し、`COMPARISON_02.md`末尾に「§9 訂正(2026-10-26 Fable確認): 救済機構による交絡」を追記: (a)フレーズ側の件数差(Trial-01 r1 → Trial-02)は救済機構の有無によるもので、P7入力は同一、(b)救済された句はProductionではHR表示のみ(auto不可)扱いになるため「最終候補件数」の比較では救済分を分離した数値(救済除外時のフレーズ件数・Y/B/N)を併記、(c)単語側(W5)への救済の影響有無(単語で`rescued: true`があれば列挙)、(d)Production差分0の確認を`er125`を含めて再確認(`git diff --stat HEAD~3 -- er125_kp_rescue_production_01.py er119_kp_candidates_01.py er105_kp_fulltext_selector_01.py er003_key_words_canonicalization.py`が空であることを示す。注: HEAD~3の起点は委任_01 commit b15266613の親で良い。空でない場合は内容を報告しSTOP)。`STATUS_02.md`・`RESULT_02.md`の冒頭に同趣旨の訂正注記1〜2行を追記(本文は改変しない)。

## 2. Fable判定(転記)

- Trial Status=**USER_DECISION_REQUIRED**(事前基準(1) 自Y min≥5が未達[min 4、median 6]、REJECTED条件非該当=事前規則どおり判断候補)。Fable独立評価: **7+5方式は目標(上級者向けに本当に価値の高い候補を数合わせなく十分な数)を達成していない**。根拠: W5は6/6レベルで上限5件を返し(W3は12/12で3件)、基本寄り(B)+易語(N)の割合が22%→41%、追加11語のうちYは3語(`nationwide`・`drag`・`snatch`)のみ、`Strategy`/`technique`が生返答1位に上がった(④易語除外が上位で機能せず)。改善点は`audience`・`responsibility`の不出現とN率微減。Prompt順是正の効果と3→5件化の効果は未分離。フレーズ側は救済機構の交絡により単純比較不可(救済除外時は前回r1と同一)。
- Fable推奨(ユーザー判断事項): (a)7+5は採用しない。(b)単語枠を残すなら「是正後Prompt順×最大3件」の分離確認1回(約¥10、6レベル)で順序是正の単独効果を測ってから判断するのが最小費用。(c)Gate `duplicate_of_top3`(含有語の機械除外)とユーザー補足「含有語を一律除外しない」の食い違いは、Production Gate変更=ユーザー判断事項(現状はGate維持)。(d)`KP_CANDIDATE_MAX=8`・HR UIとの関係は採用判断後。
- OPEN-534へ統合(新規OPENは立てない): Trial-02結果・Status・救済交絡の事実・判断候補(a)〜(d)・実費¥16.3(run ¥10.58+judge ¥5.73)・単価+¥0.05/level(7+3比)/約+¥0.28/level(現行比)・モデル(gpt-6-luna生成=比較条件統一の例外、judge gpt-6.1-sol)。
- UDR: OPEN-534の判断項目を上記(a)〜(d)+推奨で更新(「7+3方式の採否」→「候補生成方式[現行/7+3/7+5/7+3順序是正]の採否」)。
- DECISION_LOG: 1エントリ(Trial-02実施・Status UDR・救済交絡の訂正)。
- ACTIVE_TASK: 「並行: KPT2=UDR(SSOT反映済み)」を追加、QDC当日約579円(563+16.3)に更新、他は維持。

## 実行コマンド全文

- `py docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-26_PM-SSOT-SYNC-14_DELEGATION_01.md --json-out ...\_check.json`
- `git diff --stat b15266613~1 b15266613 -- er125_kp_rescue_production_01.py er119_kp_candidates_01.py er105_kp_fulltext_selector_01.py er003_key_words_canonicalization.py`
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## Git

- add対象: `OPEN_ITEMS.md`、`DECISION_LOG.md`、`docs/pm/USER_DECISION_REGISTER_01.md`、`docs/research/KP-CANDIDATE-PHRASE7-WORD5-TRIAL-02/{COMPARISON_02,STATUS_02,RESULT_02}.md`、delegation_log。pathspec付きcommit。
- commit message: `PM-SSOT-SYNC-14: KP Trial-02(7+5) Status=USER_DECISION_REQUIRED、救済機構による交絡を訂正記録、OPEN-534統合・UDR更新(API 0)`
- trailer: `Delegation: PM-SSOT-SYNC-14/01`
- push: `git push origin HEAD:main`。

## 報告

`docs/pm/RESULT_PACKET_SSOT14.md`: (0)T-0、(1)救済された候補の全件表(句/run/codes/auto可否)、救済除外時のフレーズ件数・Y/B/N(6レベル)、単語側の救済有無、Production差分確認結果、(2)編集箇所一覧、(3)必須4行+「判定整合: 重大NG=<なし|あり>」、(4)commit hash・raw URL。末尾5行要約。