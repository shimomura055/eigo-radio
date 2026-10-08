管理ID: OPEN-243-TRANSLATION-NG-ANALYSIS-01 委任_02(S0 オフライン監査、API支出¥0、既存artifactのみ+SSOT記録+commit)。日付 2026-10-08。ユーザーGo取得済み(「1: OK / 2: OK。まずTrial、結果を見てProduction採否判断 / 3: 今聞く必要なし」)。

## 禁止事項
- API支出 ¥0(LLM呼び出し禁止)。
- Production コード・CURRENT_SPEC.md を変更しない。
- `git add -A` 禁止。個別 add。
- 推測で数値を書かない。件数は出典ファイル・行を示す。判断を伴う分類は「判定: 手動」と根拠引用。
- 委任文(このメッセージ全文)を一字一句そのまま `docs/pm/delegation_log/2026-10-08_OPEN-243-TRANSLATION-NG-ANALYSIS-01_02.md` に保存し、`docs/pm/tools/check_delegation_prompt.py --file <path>` を実行して結果を記録(FAILでも続行)。
- 結果は `docs/pm/RESULT_PACKET.md` と `docs/pm/delegation_log/2026-10-08_OPEN-243-TRANSLATION-NG-ANALYSIS-01_02_result.md` に書く。

## 前提(Opusレビュー結果の要点、`er052_output/open243_translation_ng_analysis_01/` の ANALYSIS_01.md / COUNTERMEASURES_01.md と合わせて読む)
- EV-25「Meta was asked」は Checker Stage 1(r3)が `changed_actor=true`・HC-011 で正しく検出していた(`er052_output/all6_writer_redesign_necessity_01/runs/meta/control/b3__baseline__r1/checker/runs/meta_run03_advanced.json` L4294-4331)。承認構成の再分類(`STAGE1_RECLASSIFY=True`、`er052_open233_self_recovery_flow_runner_01.py` L497-522、`er052_open233_stage1_reclassify_01.py` L93-191)が C6 を `SUPPORTED`/`actor_match=match`/`excluded=true` と判定して除外(L3680-3696)。再分類 prompt には Stage 1 の issue・フラグが渡らない。
- 要約「In one line」: STOP 8/8、attempt1 MAJOR 14/24 が要約。要約再生成に must_fix が渡らない(`er003_v1_n3_01_advanced_adaptation_generate.py` L699-718)。要約だけが MAJOR でも本文ごと再生成(`er012_e_family_entertainment_two_level_runner_01.py` L418-425)。
- 最小構成候補: M1(G2+B2+要約だけ再生成)、M2(D1+D3 同時)、M3(E0: 再分類で changed_actor 付き候補を保護)。S0 はその効果量を実装前に見積るための監査。

## S0 作業
(a) **再分類による除外の集計**: 既存の Checker 実行 dump を Glob で収集(`er052_output/all6_writer_redesign_necessity_01/runs/**/checker/runs/*.json`、`er052_output/factlock_writer_trial_01/runs/**/checker/**/*.json`、`er052_output/open233_*/**/runs/*.json`、`er052_output/gpt6_wiring_e2e_01/**/checker/**/*.json` 等。承認構成で動いた run に限定し、構成の判定根拠(approved_switches_dump / switches_equal 等)を記録)。各 dump について、再分類で `excluded=true` になった model 候補を全件抽出し、Stage 1 のフラグ(changed_actor / changed_negation / changed_causality / changed_scope / changed_number / unsupported_new_claim)、related_fact_id、issue 文、再分類の verdict(SUPPORTED 等)、最終状態を表にする。集計: 除外候補の総数、フラグ別件数、changed_actor=true で除外された件数。
(b) **盲検NGとの突合**: (a) の除外候補を `items.jsonl`(53事象)と文一致で突合し、「候補化なし 10/24」「ACCEPTABLE 残存 8」のうち再分類で落ちた事象を特定。→ M3(E0)を入れた場合に救済され得る事象数(上限)を出す。
(c) **要約 MAJOR 14世代の精査**: 各世代の要約文・指摘・台帳の該当行を列挙し、一次分類「明確な誤り / 境界例 / 過剰判定の疑い」を手動判定で付ける(根拠引用)。境界例・過剰判定疑いのうち**最大3件**をユーザー確認用に3行形式(要約文・台帳・指摘理由)で `S0_USER_CHECK.md` に抜く。
(d) **FLOOR_MODE の確認**: Trial A/B の Checker 実行が `FLOOR_MODE=number_only` だったかを switch dump(`approved_switches_dump_after_p01.json` 等)で確認。
(e) **EV-28 の証跡照合**(Opus未照合): 該当 run の EN deviation check と Checker dump で、要約「callers」の検出・救済経路を確認。
(f) 成果物: `er052_output/open243_translation_ng_analysis_01/S0_AUDIT_01.md`(集計表・突合表・精査表・FLOOR_MODE・EV-28)、`S0_USER_CHECK.md`、機械可読 `s0_excluded_candidates.jsonl`。所見は事実のみ(推奨は Fable)。

## SSOT記録(同梱)
1. `docs/pm/OPUS_FINDINGS_LEDGER.md`: 本日の Opus レビュー(OPEN-243-TRANSLATION-NG-ANALYSIS-01)の所見を既存書式で追加(再分類除外が EV-25 の脱落点/第2意見は結果に影響なし/「幹部」は brief 段階で一般化・翻訳で増幅/要約に must_fix が渡らない・本文ごと再生成/最小構成 M1〜M3、不採用 C・G1・F・E1・E3/ユーザー判断 B1・B3・E0・D1/D3・再試行方針)。
2. `OPEN_ITEMS.md` OPEN-243: Opus所見の要点と、ユーザー決定(2026-10-08: S0実施、M1〜M3はTrial経路で検証後にProduction採否判断、B1/B3は今回保留)を追記(本体3,000字以内、超過分は OPEN_ITEMS_HISTORY.md へ)。
3. `DECISION_LOG.md` 本日分: (i) OPEN-243 解析→Opus→ユーザー決定の逐語、(ii) gpt-6-astra 正式単価の確認(Standard 10/1/12.5/50、Batch・Flex 5/0.5/–/25、出典 https://platform.openai.com/docs/pricing、2026-10-08 16:38 JST、`er052_output/factlock_writer_trial_01/astra_pricing_01/`)と、過去の「Sol×2.5推定」が誤りだったこと、再計算(3試験合計 ¥134→¥254、META上限¥60に対し¥94、ホルムズ+ミニバッグ上限¥80に対し¥124 の予算超過)、(iii) ユーザー決定: ホルムズ・ミニバッグも系列X採用、(iv) Batch 調査結果の要点(24h窓のみ、2段で最悪48h、Flex は同価格で同期、`docs/pm/delegation_log/2026-10-08_FACTLOCK-WRITER-REDESIGN-TRIAL-01_18_result.md`)、(v) ユーザー指示(2026-10-08)「価格等大事な情報は推測で言わない」→ PM運用ルール化。
4. `docs/pm/PM_BRIEF.md` の「PM運用メモ」節に1行追加: 「2026-10-08 ユーザー指示: 価格・費用・予算等の重要数値は出典のある確認済みの値のみ提示する。未確認は数字を出さず『未確認』と明記し、推定値を費用表・判断材料に使わない」。
5. `OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md` §106〜108 の「Sol×2.5推定」費用記述に、訂正注記(正式単価での再計算値と参照先)を追記(元の記述は消さない)。
6. `docs/pm/REPORT_LEDGER.md` 更新。

## Git
個別 add: `er052_output/open243_translation_ng_analysis_01/`(`_*.py`/`_*.json` の中間物は含めてよい)、`er052_output/factlock_writer_trial_01/astra_pricing_01/`(raw・raw_batch・extracted_pricing.json)、上記 SSOT(OPUS_FINDINGS_LEDGER、OPEN_ITEMS(+HISTORY)、DECISION_LOG、PM_BRIEF、REPORT、REPORT_LEDGER)、delegation_log の本委任・委任_17・_18・OPEN-243 委任_01 の委任文/check/result。`git status` で混入確認後 commit(例: 「OPEN-243: 翻訳段NG解析+Opus所見(再分類除外がEV-25脱落点)+S0監査、astra正式単価確認(Sol×5、過去推定訂正・予算超過記録)、Batch調査、ユーザー決定記録」)、`git push origin main`。conflict/エラー時は中断して報告。

## result に書くこと
S0 (a)〜(e) の集計要点(数値・出典)、M3 で救済され得る事象数、要約 MAJOR の一次分類内訳、ユーザー確認3件、FLOOR_MODE 確認結果、EV-28 の経路、変更ファイル一覧、commit hash と raw URL(https://raw.githubusercontent.com/shimomura055/eigo-radio/main/<path>)、check_delegation_prompt 結果、所要時間、未確認事項。
