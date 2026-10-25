# 委任_10｜JA-ASR-FALSE-NG-ROOT-CAUSE-01 ③ Family X の commit後runtime証拠の確定+Fable受入結果のSSOT反映

## 背景(Fableから)
- 委任_09(commit `58cbf7786`/`7261b9fff`、報告は `docs/pm/RESULT_PACKET_JAASR9.md`・`docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/OPEN517_RUNTIME_EVIDENCE_01.md`)で、OPEN-517 F1+F2(+523/524)の正式runtime証拠は X=経路通過のみ(ただし当該runは commit `5e50613f5` 21:56:35 より前の21:27起動で、作業ツリーの未commit差分で動いた。F2のR-5記録なし)、Z=commit後の専用run(`er078_output/open517_runtime_evidence_01/z_one_clip_02/a2`)で `final_gate.applied=True`・`r5.f2.enabled=true`・fired 0、Y=コード配線完了・runtime未確認(委任_06のE-1実走で回収予定)。
- **Fableの受入判定(本委任でSSOTへ反映する内容)**:
  - Z: `PRODUCTION_WIRED`(Fable受入2026-10-25)。根拠=commit後の正式音声生成関数経由のrunで、READING_MATCH一致がbase受理に使われず最終Gate(F1)が適用された記録、F2有効・評価済み(fired 0=該当差分なし)、Production関数での再現一致差分0(1,232件)、Regression、model_id照合(Primary openai_asr/gpt-4o-mini-transcribe、Secondary azure-speech-stt)、HR Lock整合。注記: F2の実変換事例・DEMOTE事例は正式runtimeで0件のため、以後の正式runごとに `open517_first_run_tally_01.py` で監視(DEMOTE 1runで3件超はFableへ即報告)。
  - X: 本委任で commit `5e50613f5` 以降起動のX正式経路JA判定artifactを確定できれば `PRODUCTION_WIRED`(同じ根拠)。確定できなければ「経路通過のみ(commit前run)・runtime未確認」のまま。
  - Y: 「コード配線完了・runtime未確認」(OPEN-517追跡、委任_06のE-1で回収)。
- 並行agent: (A) KP HR/Part 2 evidence R1〜R4(X/Zのrunnerを実走中。er019/er026/er062/er119/er120系と`er119_output/`等のrun dirを所有)、(B) Y 委任_06(er121系・`er121_output/`所有)。これらのファイル・run dirは**編集禁止・読取専用**。

## やること
### 1. X の commit後証拠の確定(まず読取専用、足りなければ1 clip有料run)
- (i) 委任_09が「`run_r1` の japanese_title 1件に `r5` あり」と報告した artifact(並行agent Aのrun dir配下。OPEN517_RUNTIME_EVIDENCE_01.md / out.json にパスがあるはず)を読取専用で確認: そのattemptの起動/生成時刻が `5e50613f5`(21:56:35)以降か、`final_gate` と `r5`(`f1`/`f2.enabled`)が記録されているか、READING_MATCH一致の有無。これが Z と同等の証拠(commit後・正式経路・final_gate適用またはF1/F2評価記録)なら、それをX証拠として採用し有料runは不要。Aの他のX run(R2〜R4)にも commit後起動のJA判定があれば同様に集計(すべて読取専用)。
- (ii) (i)で不足する場合のみ、委任_09がZで行ったのと同じ方式(runner全体を回さず、Xの正式音声生成関数を1 clip単位で呼ぶ。`open517_z_one_clip_evidence_01.py` を参考に `open517_x_one_clip_evidence_01.py` を作る)で、X の日本語segment(READING_MATCHに当たりやすいもの=既存Xの日本語title/a2 preview等から、過去artifactで `READING_MATCH` が記録されたものを選ぶ)を1〜2 clip生成。専用dir `er078_output/open517_runtime_evidence_01/x_one_clip_01/`。**上限5円**。有料run=`.venv\Scripts\python.exe`。起動前: `py docs/pm/tools/daily_dev_cost_01.py` の表示値+94.28円が実累計で、+5円で1,480円を超えるなら実行せず報告。`py tools/stop_scope_check_01.py --managed-id JA-ASR-FALSE-NG-ROOT-CAUSE-01 --run-dir er078_output/open517_runtime_evidence_01/x_one_clip_01 --out er078_output/open517_runtime_evidence_01/x_one_clip_01/stop_check_10.json`(rc=3なら起動しない)。**起動間隔は150秒以上を時計で確認してから**(委任_09は58秒間隔で違反した。同じ誤りを繰り返さない。2回目を起動するなら `Get-Date` を前後で記録して差を報告に書く)。同一run 5分3回禁止。HR Lockに当たっても `approved_by="user"` は付けない。wav/raw_usage_log/lockは追跡しない。
- (iii) 結果で `open517_first_run_tally_01.py` を回し、DEMOTE/NG化/F2 fired を集計(X/Z両方)。
- 出力: `docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/OPEN517_RUNTIME_EVIDENCE_02.md`(X/Z/Y 3行表を更新。各行: run dir / 起動時刻 / commit後か / final_gate適用 / r5.f1 / r5.f2 enabled・fired / 523・524 / DEMOTE / NG化 / model_id / HR Lock / 事実ベースStatus候補)。

### 2. Fable受入結果のSSOT反映(上記Fable判定どおり。あなたの判定で変えない)
- `OPEN_ITEMS.md` OPEN-517: Status行を「X=<1.の結果に応じて PRODUCTION_WIRED(Fable受入2026-10-25) or 経路通過のみ・runtime未確認>/Z=PRODUCTION_WIRED(Fable受入2026-10-25)/Y=コード配線完了・runtime未確認(委任_06 E-1で回収)」に最小追記。監視条件(tallyをrunごと・DEMOTE 3件超即報告)も1文。直前再Read・最小Edit・バックアップ。
- `DECISION_LOG.md`: 1件追記(タイトル例「OPEN-517 F1+F2(+523/524) Family別Status確定: Z PRODUCTION_WIRED(Fable受入)、X <結果>、Y runtime未確認」。根拠・commit sha `5e50613f5`/`58cbf7786`/`7261b9fff`/本委任commit・証拠ファイル名・監視条件・rollback定数名を簡潔に)。他agentの未commit差分が混ざる可能性が高いので、HEADのblobに自分のエントリだけを足す一時index+commit-tree方式で、自分のhunkのみcommitする(委任_05/08と同じ方式)。直前再Read。
- `CURRENT_SPEC.md`: 07A/09が L2855〜2857付近に追加した行のStatus表記に Family別Statusを最小反映(1行以内)。
- 追補 `er058_output/unified_all_roles_production_wiring_01/DESIGN_02_ADDENDUM_01.md` L65 の上書き注記は07Aで済んでいることを確認のみ(編集不要なら触らない)。

### 3. Git・ログ
- 禁止=`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・`git checkout -- <file>`。commitは対象pathのみ、`git push origin HEAD:main`(non-fast-forwardなら fetch→`git merge --no-edit origin/main`→push、競合は両方残しSTOP報告)。secret grep 0件。作業ブランチ `work/post-merge-01`。
- 委任文の逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-25_JA-ASR-FALSE-NG-ROOT-CAUSE-01_DELEGATION_10.md`(直近既知index=599(委任_09)。600以降を順に試し、先頭行が「# 委任_10｜JA-ASR-FALSE-NG-ROOT-CAUSE-01」のものだけ採用)。

## 報告(`docs/pm/RESULT_PACKET_JAASR10.md`+最終報告)
1. X証拠の確定結果(採用artifact・時刻・final_gate/r5の値・有料run実施有無・実費・起動間隔の実測)
2. tally結果(X/Z: F1 NG化/DEMOTE/F2 fired/523/524)
3. SSOT反映内容(OPEN-517/DECISION_LOG/CURRENT_SPECの差分要約)とcommit sha・raw URL
4. 当日累計(表示値+94.28円)
5. RESULT_PACKET 4行+判定整合行
6. 未解決(あれば)
事実と推測を分ける。Statusの語はFable判定の転記としてのみ使う。