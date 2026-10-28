# FAMILY-Z-IN-A-GROVE-PRODUCTION-01 委任_06(本文逐語、2026-10-28)

管理ID FAMILY-Z-IN-A-GROVE-PRODUCTION-01 委任_06「RESTART_STORM解除(Fable明示承認)+kp_a2再生成+Std選定フォーム公開+200実測」。前提=委任_05(`CP_RESULT_03.md`、削除パッチ済みStd sha 4f7fb3dc…、plan_a2/support_a2再生成済み、kp_a2起動がRESTART_STORM[3起動/300秒、原因=worker側の起動間隔運用ミス、API呼出0、暴走なし]で自動STOP)。**Fable判断(PM_GOVERNANCE 26節:3564)**: 原因が運用上の起動間隔ミスで副作用0と確認済みのため、Fable権限で解除を承認する。解除コマンドは `--clear-stop --reason "FAMILY-Z-IN-A-GROVE-PRODUCTION-01 委任_06: RESTART_STORM(委任_05の起動間隔運用ミス、API 0・副作用なし)をFable承認で解除。audit記録"` とし、`audit_stop_sentinel.jsonl`への記録を確認。STOP_ALLは触らない。
並行worker: Family Y 委任_03(SSOT・ACTIVE_TASK編集中=直前再Read・最小Edit)。SSOT編集なし(ACTIVE_TASK(H)行のみ可)。
開始時と有料前に stop_scope_check_01.py(--managed-id FAMILY-Z-IN-A-GROVE-PRODUCTION-01 --run-dir docs/research/FAMILY-Z-IN-A-GROVE-PRODUCTION-01 --out .../stop_check_06.json)(rc=3かつ理由がRESTART_STORM以外なら停止)。本委任Cap¥5(run累計約¥37/Cap¥70)。

## 手順
1. run_launch_log.jsonlで直近300秒窓に起動がないことを確認(必要なら待機)→--clear-stop --reason …で解除→STOP/RESTART_STORM_LOCK.jsonの状態とaudit記録を確認・転記。
2. _run5.shで --stages kp --regenerate-stage kp_a2 を1起動のみ(rc=4 KP_REVIEW_PENDINGが正常)。起動後、part2_cand_a2がstaleのままなら、150秒以上あけて必要な1起動だけ追加(合計2起動以内、300秒窓に3起動を入れない)。provenanceのdownstream_staleが空になったことを確認。
3. Std候補一覧(review_request.md)を取得し、Std選定フォーム公開(user_test/selection_form_v3/data/in_a_grove__a2__prod.json+articles.json登録)→commit→git push origin HEAD:main(FFのみ。委任_05のcommit 24538ae4dがorigin/mainに届いているかもgit fetch+git log origin/mainで確認し、未pushなら本pushに含める)→Pages反映(最大10分)後に Std/Adv の data JSON とフォームURL(index.html?a=in_a_grove__a2 / __b1b)のHTTP 200を実測。
4. hand-back: 解除記録、kp結果(候補sha・rc)、Std候補一覧(逐語)、Std/AdvフォームURL+200結果、累計費用、commit sha(push確認済み)、Fable注記(訳ずれ・文法Top1/Top2重複・Adv文法0件の扱い)。
## 成果物・Git
RESUME_06.md、docs/pm/RESULT_PACKET_FZIG6.md(≤15行、4行+判定整合行)、本ファイル(本文逐語)、ACTIVE_TASK(H)行更新。自分のファイルのみ明示add。git add -A禁止。
