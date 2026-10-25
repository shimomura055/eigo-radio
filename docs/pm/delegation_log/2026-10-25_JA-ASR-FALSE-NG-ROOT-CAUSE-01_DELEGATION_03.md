管理ID: JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_03(Phase 3 有料検証の実行+評価。到達上限VALIDATED。Production変更禁止)。

## 予算(Fable確認済み)
- 本日JST 2026-10-25の日次上限は1,500円へ引上げ済み(ユーザー指示)。直近の日次累計は約1,067円(`py docs/pm/tools/daily_dev_cost_01.py`の表示はer110 Round 2分94.28円が未反映の可能性あり。起動前に表示値+94.28円で見積ること)。Phase 3 Cap 60円(BUDGET_PLAN_02どおり)。累計+60円が1,500円を超える見込みならSTOP報告。
- 他案件(KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01 evidence ≤300円)が同日並行で有料実行する可能性あり。各stage起動前に日次を再確認。

## 読むもの
`docs/pm/PM_BRIEF.md`、`docs/pm/ACTIVE_TASK.md`(本案件節のみ更新)、`docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/{ROOT_CAUSE_01,DESIGN_01,PREREGISTERED_CRITERIA_02,OPUS_REVIEW_01,BUDGET_PLAN_02,EVAL_01}.md`、`phase3_paid_runner_01.py`(+test)、`n3_clips_01.json`、`proto_reading_compare_01.py`(v1 sha `8799aa60…`、凍結)、`eval_api0_v1_01.py`、ユーザー原文 `docs/pm/delegation_log/2026-10-25_FX-CORE-NUMERIC-RETENTION-TRIAL-01_USER_06.md`(Task B)、委任_01/_02逐語。

## 手順
1. `py tools/stop_scope_check_01.py --managed-id JA-ASR-FALSE-NG-ROOT-CAUSE-01 --run-dir <Phase3出力dir> --out <同dir>/stop_check_委任_03.json`(rc=3なら起動しない)。prototype v1のsha不変を確認。test PASS確認(API 0)。
2. Fable権限で `docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/PHASE3_GO.json` を作成: `{"managed_id":"JA-ASR-FALSE-NG-ROOT-CAUSE-01","cap_jpy":60,"stages":["A1_azure_moon","A2_openai_moon_x3","A3_azure_flip","N3_tts","N3_asr","O1_format_prompt"],"approved_by":"Fable(承認済みScope内・案件300円以下、7-7)/日次1,500円引上げ(2026-10-25ユーザー指示)","basis":"BUDGET_PLAN_02"}`(runnerのschemaに合わせて調整。不足keyはrunnerの要求に従う)。
3. 有料実行は`.venv\Scripts\python.exe`で、BUDGET_PLAN_02 §の順序どおり**1起動1 stage**(A1→A2→A3→N3_tts→N3_asr→O1)。同一run dirへの起動間隔150秒以上・5分以内3回起動禁止。外部停止・原因不明rc≠0が2回続いたら再起動せずSTOP。各stage後に実費を集計しCap 60円を超えない(超える見込みなら残stageを実行せず報告)。
4. 評価(`EVAL_02.md`、事前登録02に従う): 主要指標=増分誤PASS 0(負例でPASSにならない)・非回帰100%(既存PASS/NGの判定が変わらない)・「しわ」→詩/死/氏、「8,900本」型の誤NGが案Aで正しくPASS_WITH_WARNING(`JA_PRON_EQUIVALENT`)になるか・Azure/OpenAI別・N-3 30clipの結果・O1(数値フォーマットPrompt)の効果。Status候補はVALIDATED/REJECTED/UDRを事前登録写像で機械的に出し、最終はFable。メロスpreview flip(A3)の試聴素材があれば試聴用の置き場所(公開不要ならローカルパス)を明記。
5. `TRIAL_RESULT_01.md`(ユーザー閲覧用、ユーザー指定の報告順: 原因/対策/検証/QCD/Fable・Opus評価[欄は空欄]/Status/判断)。`BUDGET_LOG_01.md`。
6. SSOT: OPEN-515・OPEN-517更新(直前再Read・最小Edit・バックアップ。他agentが並行編集中)。Production変更0・新flag 0。CURRENT_SPEC変更なし。
7. Git: 対象pathのみadd(wav/raw_usage_log不追跡)→`git commit --only`→`git push origin HEAD:main`(non-fast-forwardならfetch→`git merge --no-edit origin/main`→push。競合は両方残しSTOP報告)。`git add -A/-u`・amend・rebase・force・stash・reset --hard禁止。secret grep 0件。
8. 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-25_JA-ASR-FALSE-NG-ROOT-CAUSE-01_DELEGATION_03.md`(Nは579前後、先頭「管理ID: JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_03」を575〜600で走査)。

## 禁止
Production code(ASR cascade・normalize_ja・Variant Layer・閾値・Prompt)の変更、prototype v1の変更(凍結)、品質を下げる対策(免除・閾値緩和)、A4(b)新仕様候補の実装、Phase 3範囲外の追加Trial。最新モデル原則: 使用モデル名(OpenAI gpt-4o-mini-transcribe等は既存Production比較のための例外理由を明記)。

## 報告(RESULT_PACKET_JAASR3.md+口頭要約)
ユーザー指定順(原因/対策/検証/QCD/Fable・Opus評価欄/Status/判断)で要約、stage別の実費・Cap内、増分誤PASS・非回帰の数値、案Aの効果(件数)、残課題(OPEN-517 API-0設計等)、commit hash・raw URL、RESULT_PACKET 4行+判定整合、判断候補(27-3仕分け。Phase 4=Production適用はユーザー判断)。