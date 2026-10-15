# FAMILY-C-JA-TTS-PRODUCTION-FIX-01 委任_03 委任文(保存、T-0)

(注: 固定ブロック群[E-1/D-1/G-1/F-1/T-0/T-2/T-3]の条文のみ要約転記。他は委任文の内容を保持。)

## 管理ID
`FAMILY-C-JA-TTS-PRODUCTION-FIX-01` 委任_03(Fable判断を受けた有料evidence Run A/Bの実装・実行+EVIDENCE/SSOT更新+commit/push)。並行: AUW 委任_10(er078/er007系を編集、commit/pushあり)。編集ファイルは重ならない。Git競合回避: commit時`.git/index.lock`があれば60秒待ち再試行(最大10回)。mainへの反映は`C:\Users\tensh\eigo-radio-crbn`で`git pull --ff-only origin main`→`git merge --ff-only work/post-merge-01`(ff不可なら`--no-ff`、競合は中止報告)→`git push origin main`(rejectedなら`pull --ff-only`→再push、最大3回)。SSOT追記直前に`git fetch origin; git merge --ff-only origin/main`で最新化。

## 前委任(FCJ 委任_02)の受入記録(Gate 7)
- 当初目的(ユーザー原文逐語、`docs/pm/delegation_log/2026-10-16_FAMILY-C-JA-TTS-PRODUCTION-FIX-01_01.md` L19-57): 「到達目標：正式Production経路で日本語音声生成・検証・再利用整合が正常動作すること」「必要な実音声をProduction正式経路から生成し、runtime evidenceを取得する。」B-4「Family C日本語Commentの新規TTS成功/必要な日本語Sectionの生成・ASR確認/英語Sectionの回帰なし/原稿変更時の誤音声再利用なし/Production実行でruntime evidence取得/…/実成果物が既存Family C仕様を満たすこと」。
- 最終成果物: commit `482603716`。有料Run A/B未実施(条件付きSTOP(b))。証拠: `EVIDENCE_02.md`、`evidence_02/`。
- 判定: 委任_02=CONDITIONALLY_ACCEPTED。QDC: 費用JPY0/改善見込み高/次=本委任。

## Fable判断(条件付きSTOP(b)の解除理由)
- STOP(b)の趣旨は「ユーザー試聴承認済みの音声を差し替えないこと」。本委任のRun A/Bは隔離した新規出力dirで実行し、承認済み資産のファイルは一切変更・削除・上書きしない。したがって有料evidenceは進めてよい。
- 承認済み資産の将来の再利用保証(案1=wav sha256固定マニフェスト、推奨)はOPEN-385としてユーザー判断事項(非ブロッキング)。本委任では実装しない。
- 追加費用: Run AでStory等の英語clipも再生成される分(最大9 clip)を許容。

## 性質/禁止事項/費用
- 到達上限Status: `FIX_EVIDENCED_PENDING_FABLE`。`PRODUCTION_WIRED`は書かない。
- 禁止: `git add -A`/`-f`、amend、rebase、force push、stash、clean、`reset --hard`、`checkout -f`、STOPセンチネル削除・回避、HR Lock迂回・変更、承認済み資産dir(`er013_output/family_c_episode_trial_11/`、`family_c_episode_trial_12/`、Memory本番a2出力dir、`CURRENT_SPEC.md:1047-1149`で試聴承認が記録されたdir)への書込・削除・上書き、Production flag追加、Voice/Validator/閾値変更、OPEN-385案1〜3の実装、有料runの再起動(途中終了は事実記録しFableへ)、runner本体の追加改修(最小修正のみ可、内容を記録)。
- 費用見積 約JPY8(Run A: JA 5 clip+英語最大9 clip、Run B: 最大3 clip)。上限JPY14(Guardrail)、承認区分C。T-3定型文: 到達・接近時は承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用合理的/QCD便益明らか であれば超過を記録して継続、暴走疑い時のみSTOP。
- T-2: `TTS_EXECUTION_MODE=STANDARD`明示。実行前に(1)差分再生成可否(2)再利用キャッシュ有無(3)--budget明示(4)想定外の全再生成ならAPI前STOP(Run Aの英語最大9 clip再生成は許容済み、topic_intro等の共有asset再生成が判明した場合のみSTOP)。

## ユーザー指示(原文)
`docs/pm/delegation_log/2026-10-16_AUW-FAMILY-C-DQI-USER-INSTRUCTION.md`「# B.」節。特にB-2「必要な実音声をProduction正式経路から生成し、runtime evidenceを取得する。」B-4完了条件9項目。

## KPI provenance
JA新規TTS成功(Run A JA 5 clip)・英語回帰: `production_formal_path`(fresh)。Run B: `production_formal_path`(fresh、test fixture表示)。E2E自己確認「fresh Production初回pathを含むE2E値か」: Run A=Yes。

## Opus台帳更新
`OF-FCJ-04`・`OF-FCJ-06`・`OF-FCJ-07`を`EVIDENCED`へ(追記のみ)。

## 手順
0. fetch/ff、evidence_03作成、stop_scope_check rc=0、承認済み資産dirのsha256を実行前保存。
1. `er079_family_c_ja_evidence_01.py`に`run_a`/`run_b`実装(費用meter・hard_stop JPY14・STOP監視・T-2自動記録・承認済みdir書込禁止ガード)。
2. Run A: `run_a --article-config <実パス> --reuse-from er013_output\family_c_episode_trial_11\memory_a2 --out ...evidence_03\run_a --budget-jpy 14 --execute`(Production正式entry経由、LLM 0 call)。
3. Run B: Run A出力をreuse_fromに、出力dir側のcomments_ja.mdのComment1だけ変更(test fixture表示)。期待=Comment1のみ再生成。
4. 実行後sha256一覧を取りbeforeと差分0を確認。
5. test再実行(API 0、netguard): er079_family_c_ja_tts_fix_02_test_01.py + er013_family_c_production_test_01.py(60 passed期待)。
6. `EVIDENCE_02.md`に§6追記、OPEN-385/OPEN-372行内追記、DECISION_LOG/CURRENT_SPEC/REPORT_LEDGER/Opus台帳更新、secret scan hits=0、明示`git add`、commit、crbn経由でmainへff push。
RESULT_PACKETは`docs/pm/RESULT_PACKET_FCJ3.md`(10項目)。
