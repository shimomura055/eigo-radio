# 委任_01A(2026-10-28、管理ID: JA-ASR-FALSE-NG-ROOT-FIX-02)— Fable→sonnet-worker 委任文(逐語保存)

管理ID: JA-ASR-FALSE-NG-ROOT-FIX-02(新規。前身=JA-ASR-FALSE-NG-ROOT-CAUSE-01/OPEN-515・517・333、FX-MOON-SHRINKING-RESELECT-REMAKE-01 委任_03/04)。本委任=委任_01A「課題A PM管理不備の原因究明」。read-only調査+報告書作成のみ。並行して別worker(委任_01B、ASR再評価)が同じ管理IDの`docs/research/JA-ASR-FALSE-NG-ROOT-FIX-02/`配下で作業中。**あなたのファイル範囲**: `docs/research/JA-ASR-FALSE-NG-ROOT-FIX-02/PM_AUDIT_*`、`docs/pm/RESULT_PACKET_JAFIX2A.md`、`docs/pm/delegation_log/2026-10-28_JA-ASR-FALSE-NG-ROOT-FIX-02_委任_01A.md`(本委任文を逐語保存)のみ。SSOT(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS/USER_DECISION_REGISTER/PM_GOVERNANCE)・Production code・他dirは編集禁止(是正案は報告書に書き、Fable受入後に別委任で反映)。ユーザー原文全文は委任_01B workerが`docs/pm/delegation_log/2026-10-28_JA-ASR-FALSE-NG-ROOT-FIX-02_USER.md`へ保存する(存在すれば参照)。Family A/B/Cには触れない。API支出0。

開始時に `.venv\Scripts\python.exe tools/stop_scope_check_01.py --managed-id JA-ASR-FALSE-NG-ROOT-FIX-02 --out docs/research/JA-ASR-FALSE-NG-ROOT-FIX-02/stop_check_01A.json` を実行(rc=3なら停止して報告)。
(実行注記: 同helperは`--run-dir`必須のため `--run-dir docs/research/JA-ASR-FALSE-NG-ROOT-FIX-02` を付して実行、rc=0・stop=false。)

## ユーザー原文(課題A、逐語)
> ## 3. 課題A｜PM管理不備の原因究明
> 次の疑問に、過去の一次記録を用いて具体的に回答してください。
> **なぜ、元の誤NG問題が未解決なのに、F1+F2・E3・E4を正式採用・完了扱いとし、案件を閉じることができたのか。**
> 必須調査事項：
> 1. 当初の目的・成功条件・受入基準は何だったのか。
> 2. F1+F2・E3・E4のそれぞれの目的は何か。誤PASS防止と誤NG救済のどちらに、実際にどう作用するのか。
> 3. 当時のTrialで、月タイトルの誤NGが未解決であることを誰が、いつ把握していたのか。
> 4. v2／β／P-1が保留された時点で、残る問題はどのように管理されたのか。
> 5. なぜユーザーへ適切な判断材料を提示せず、次工程へ進めたのか。
> 6. Claude・FableのCloseout、Open Item管理、PM Gate、独立受入のどこが機能しなかったのか。
> 7. 当初案件全体のCloseoutと個別対策のProduction Wiringを混同していなかったか。
> 当時の報告、CURRENT_SPEC、DECISION_LOG、OPEN_ITEMS、USER_DECISION_REGISTER、PM_GOVERNANCE、Git履歴を突合してください。
> 単に「報告漏れだった」と結論づけず、**その漏れを許した管理上の原因**まで特定してください。
> 必要十分な再発防止策を提案し、既存ルールで防げるものは新しいGateを増設せず運用是正で対応してください。
> (報告§8A) 当初目的とCloseout実態の差 / なぜ未解決で完了扱いになったのか / Claude・Fableの管理上の原因 / 再発防止策とSSOT／Open Itemへの反映状況

## 一次資料(ここから突合。全文読込せずGrep/範囲読み)
- `docs/pm/delegation_log/2026-10-25_JA-ASR-FALSE-NG-ROOT-CAUSE-01_USER*.md`(USER〜USER_06。ユーザー原文=目的・成功条件・受入基準の正本)、同`_DELEGATION_*.md`(委任_01〜12+)、`2026-10-26_*JA-ASR*`があれば同様。
- `docs/pm/RESULT_PACKET_JAASR*.md`、`docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/`の `ROOT_CAUSE_01.md` / `TRIAL_RESULT_01.md` / `EVAL_0[1-3].md` / `OPEN517_*` / `OPEN333_DESIGN_02.md` / `OPEN333_APPLY_RESULT_01.md` / `B_LIGHT_EVAL_02.md` / `B_LIGHT_DESIGN_02.md` / `OPUS_REVIEW_01*.md`。
- SSOT: `OPEN_ITEMS.md` OPEN-515(行1030)・OPEN-517(行1032)・OPEN-333(行836)の追記履歴、`DECISION_LOG.md`の該当エントリ(例 :22501 付近、Grep「JA-ASR-FALSE-NG」「OPEN-517」「E3」「F1+F2」)、`CURRENT_SPEC.md:2257/2920/2931`付近、`docs/pm/USER_DECISION_REGISTER_01.md` #136・#201〜#203、`docs/pm/PM_GOVERNANCE.md` 11-6/11-8/27-3/27-4/Closeout項目32/Gate 7/12節、`docs/pm/OPUS_FINDINGS_LEDGER.md`該当行。
- Git: `git log --since=2026-10-24 --format="%h %ad %s" --date=iso -- OPEN_ITEMS.md DECISION_LOG.md CURRENT_SPEC.md er078_asr_unified_judge_01.py er007_ja_secondary_asr_01.py er011_ja_asr_variant_layer_01.py docs/pm/USER_DECISION_REGISTER_01.md` と各commitの`git show --stat`。
- 直近の是正: FX-MOON 委任_03/04(`docs/research/FX-MOON-SHRINKING-RESELECT-REMAKE-01/JA_TITLE_ASR_RECURRENCE_01.md` §5、`docs/pm/delegation_log/2026-10-28_FX-MOON-SHRINKING-RESELECT-REMAKE-01_USER_04.md` §5、UDR #201〜#203、`PM_GOVERNANCE.md:2586`「過去対策確認」)。これで十分かも評価する。

## 成果物
1. `docs/research/JA-ASR-FALSE-NG-ROOT-FIX-02/PM_AUDIT_01.md`: 質問1〜7に番号対応で回答。各回答に根拠(file:line、commit sha、日時、誰[ユーザー/Fable/Sonnet/Opus])を付け、事実と推測を分ける。時系列表(日時/出来事/誰が何を把握・判断したか/月題誤NGのStatus)。「当初目的 vs Closeout実態」の対照表。管理上の原因の特定(例: 案件目的[正常音声の救済]と受入単位[個別対策の安全性VALIDATED]の取り違え、27-3仕分けでの扱い、UDR未起票、Closeout項目32[手段の成否と目的達成の区別]の運用、独立受入の(1)原文引用の有無、Fable報告での未解決事項の記載有無 等を**証拠で**確認。該当しなければ該当しないと書く)。
2. 再発防止策: 既存ルール(PM_GOVERNANCE該当節を引用)で防げるものは運用是正(具体的に何を・どの手順で・誰が)とし、新Gate増設は本当に必要な場合のみ理由付きで提案。2026-10-28の是正(UDR #201〜203、11-8追記)との重複・不足を明記。SSOT/Open Itemへの反映案(具体的な追記文案、Fable受入後に別委任で反映)。
3. `docs/pm/RESULT_PACKET_JAFIX2A.md`(10〜20行): 結論・主因・証拠3点・再発防止案の要点・判断候補(A既判断/B承認範囲内/C独立/D真に新しい判断の仕分け+挙証)・判定整合行。
4. `git add <上記3ファイル+stop_check json> && git commit -m "JA-ASR-FALSE-NG-ROOT-FIX-02 委任_01A: PM管理不備の原因究明(read-only、API 0)"` を**1コマンドで**実行(事前に`git diff --cached --name-only`が空であることを確認、他workerのファイルは絶対にaddしない、`git add -A`禁止)。`git push origin HEAD:main`(fast-forwardのみ。拒否されたら`git fetch`後に再試行、force禁止)。
最後に、結論・主因(1〜3行)・commit sha・判断候補をhand-backで返す。
