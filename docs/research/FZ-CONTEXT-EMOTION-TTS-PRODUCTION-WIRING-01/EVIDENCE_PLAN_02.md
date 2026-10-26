# EVIDENCE_PLAN_02 — Phase 2 runtime evidence 計画(未実行)

driver: `er122_fzcw_runtime_evidence_01.py`(正式runner main()を同一processで起動、module属性wrapで強制NGはNG方向のみ。pages stages禁止)。実行前に`tools/stop_scope_check_01.py`でrc=0確認。`TTS_EXECUTION_MODE=STANDARD`明示。専用run dir(公開dir・完成版runと別)。
共通コマンド形: `.venv\Scripts\python.exe er122_fzcw_runtime_evidence_01.py --case <E-n> --work the_monkeys_paw --run run_fzcw_<en>_01 --budget-jpy <60|15> [--level a2|b1b] [--only-clips ...]`
証跡: 各runの`evidence_*.json`(前後の台帳行数・run識別子[R-1]、TTS requests、ctx有無、overrides、cooldown実秒、peak分布)。

| case | Std/Adv | 実行 | 期待値 |
|---|---|---|---|
| E-1 | 両level(a2=Std相当/b1b=Adv相当経路)| `--case E-1 --budget-jpy 60` | 全dialogue TTS promptにCONTEXT含有、notes.json保存、attempt1でPASS、`dialogue_tts.policy=fz_ctx_v1`、ctx音声peak分布を観測報告(peak_max=0.999は新基準ではなく観測) |
| E-2 | Std+Adv | `--level a2` / `--level b1b` | attempt1・2=ctx(待機0)、cooldown実測>=600s、attempt3 promptにCONTEXT/話者/前後セリフ/manner 0、従来style、PASS時mode=legacy_fallback |
| E-3 | Std | `--kill-in-cooldown 30`後に同一argsで再起動 | 再開でattempt1・2を再実行しない(TTS呼出増0)、cooldown残り分のみ待機、総10分未満にならない、3回上限内 |
| E-4 | Std+Adv両方 | 3回強制NG | 総TTS生成3回(4回目なし)、STOPPED->HR Lock、最終成果物=STOP。**期待値にASR由来HR queue行を含めない**(強制NGはrepetition QA段階、ASR判定はPASS)。forced run由来の台帳行は`evidence_only_rows`として無効化(R-1)、台帳に「evidence専用・対応不要」 |
| E-5 | Std | `--kill-after-attempt 1` | attempt1のみNG(強制)->kill後再開でn=2はctx即時PASS、TTS総回数=2、再開で1回目重複なし |
| E-6 | Adv | post-slowdown側でattempt1をNG | 外側ループが継続し通算n=2もctx、`prior_generations`で二重計上なし、総3回上限 |
合否: 上記期待を満たし、新規費用が見積内、ASR表記違いのみ理由の再生成0。不合格はFableへ原因・証拠付き報告。

## 実行後の逸脱履歴(委任_03、2026-10-26追記。計画本文は改訂せず履歴として残す)

実行結果=EVIDENCE_01.md。計画からの逸脱は以下(詳細・理由・影響はEVIDENCE_01.md §5):
- D-1 作品を猿の手→melos(猿の手seed更新によるprovenance不一致STOP[API 0]。melosは`run_p2_evidence_r3`のtext資産copy、dialogue TTSは全新規生成)。
- D-2 driver修正2点(prompt非str記録、再開用`--ordinal-offset`)。再開起動は「同一args」ではなくkillフラグ除去+offset付き。
- D-3 準備段階の起動重ねで猿の手`run_fzcw_e1_01`にRESTART_STORM(STOP+LOCK)。解除せず、melos別run dirで継続。
- D-4/D-5 budget値・追加text資産copy(study_text、keywords_canonicalized)。
- 計画表のE-1は「両level 1run」で実施(`--level`なし、default stagesの1起動)。E-2〜E-6の対象clipは`full_story_part1_c2`(Std/Adv共通のdialogue clip)。
