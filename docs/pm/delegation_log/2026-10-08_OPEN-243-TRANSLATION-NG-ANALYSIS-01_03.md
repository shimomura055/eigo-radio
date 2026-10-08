管理ID: OPEN-243-TRANSLATION-NG-ANALYSIS-01 委任_03(M1〜M3 の Trial 実装と既存データでの検証)。日付 2026-10-08。ユーザーGo取得済み(「M1-M3のTrialに進んでください」)。ユーザー確認3件の回答: 確認1「users」=許容(文脈から一般に想像できる補足)/確認2「so」=この事例では許容、ただし勝手に因果関係を作るのは潜在的リスク/確認3「oil prices」=許容(一般ニュースでもありえる)。

## 予算・制約
- API予算 上限 ¥60(検証の換算見込み約¥30、全て gpt-6-luna=登録済み単価。astra は使わない)。超過見込みで停止して報告。
- **Production の既定動作を変えない**: すべての変更はフラグ(環境変数または引数、既定 OFF)の背後に置く。承認済み Checker 構成(`OPEN233_APPROVED_FLOW_SWITCHES`)の値は変更せず、Trial 用スイッチを別名で追加する。CURRENT_SPEC.md は変更しない。既存の回帰テスト(`er006_model_routing_pricing_coverage_test_01.py` 等、該当するもの)をフラグ OFF で実行し PASS を確認。
- `git add -A` 禁止。個別 add。
- 推測で数値を書かない(費用は実測トークン×登録単価、USD/JPY=160)。
- 委任文(このメッセージ全文)を一字一句そのまま `docs/pm/delegation_log/2026-10-08_OPEN-243-TRANSLATION-NG-ANALYSIS-01_03.md` に保存し、`docs/pm/tools/check_delegation_prompt.py --file <path>` を実行して結果を記録(FAILでも続行)。
- 結果は `docs/pm/RESULT_PACKET.md` と `docs/pm/delegation_log/2026-10-08_OPEN-243-TRANSLATION-NG-ANALYSIS-01_03_result.md` に書く。`docs/pm/ACTIVE_TASK.md` の固定ヘッダを本管理ID・Status=IN_PROGRESS(Trial)に更新してよい。

## 前提資料(先に読む)
- `er052_output/open243_translation_ng_analysis_01/{ANALYSIS_01.md,COUNTERMEASURES_01.md,S0_AUDIT_01.md,S0_USER_CHECK.md,items.jsonl,s0_excluded_candidates.jsonl}`
- `docs/pm/OPUS_FINDINGS_LEDGER.md` OF-088〜094
- 実装箇所: 要約生成 `er003_v1_n3_01_advanced_adaptation_generate.py`(`generate_family_x_in_one_line` 付近 L699-718)、runner の再生成分岐 `er012_e_family_entertainment_two_level_runner_01.py`(L377-453)、EN deviation check `er003_v1_en_direct_vfl_01_generate.py`(`run_deviation_check` L506-545、分類項目定義、origin 判定)、Checker 再分類 `er052_open233_stage1_reclassify_01.py`(L93-191)、runner `er052_open233_self_recovery_flow_runner_01.py`(L497-522)

## 実装(Trial フラグ、既定 OFF)
**M1(要約)** フラグ例 `OPEN243_M1=1`:
- 要約「In one line」の生成入力に、英語本文に加えて **日本語 R2 本文と台帳** を渡し、must_fix(前回の MAJOR 指摘)があればそれも渡す。
- 検査で **要約だけが MAJOR** の場合は本文を作り直さず、**要約だけを再生成**(最大2回)。本文に MAJOR がある場合は従来どおり。
- プロンプト文言は最小限(禁止列挙を増やさない)。変更前後のプロンプト全文を設計メモに残す。

**M2(EN検査)** フラグ例 `OPEN243_M2=1`:
- D1: `changed_actor` の定義を「依頼主体・行為主体・受け手/かけ手の入替、受動化による主体転換、主語省略の誤補完」まで明示的に拡張(分類の説明文の変更。severity 規則は現状維持)。
- D3: origin 判定を「対応する日本語 R2 文に同じ逸脱が無ければ translation」に修正(現状の判定ロジックを読んで差分を明記)。
- ユーザー回答の反映(校正): 「文脈から一般に想像できる補足(例: 開示の相手=利用者)」「指標の一般化(Brent先物→oil prices)」は MAJOR にしない旨を**1〜2文**で追加してよい(過剰な誘導は避ける)。因果の付与は現状どおり指摘対象のまま(ユーザー注記「潜在的リスク」)。

**M3(Checker 再分類)** Trial スイッチ例 `OPEN233_RECLASSIFY_PROTECT_FLAGS="changed_actor"`(承認構成には含めない):
- 再分類で、Stage 1 の model 候補のうち指定フラグが true のものは **除外しない**(CANDIDATE のまま Stage 2 へ、fail-closed)。既定 OFF。
- 併せて G3: translation 起源 MINOR と再分類除外候補のフラグを telemetry(jsonl)に記録(¥0)。

## 検証(既存データ、新規の全体生成なし)
- **V1(M1)**: 要約 MAJOR 14世代(S0 §3)と EV-28 を fixture に、各世代の保存済み英語本文・日本語 R2・台帳・attempt1 の指摘を入力として、新方式で要約だけを再生成→EN deviation check を実行。指標: MAJOR 件数(旧 attempt1 基準/ユーザー回答で「許容」とした型は別掲)、解消率(従来 6/14 との比較)、要約の主体・範囲の保持。費用。
- **V2(M2)**: fixture = 翻訳由来/増幅 26事象(陽性: translation と判定され、主体型は changed_actor=true になるべき)+ JA由来 27事象(origin は ja_source のまま)+ ユーザー許容3文(MAJOR にならないべき)。保存済み英語記事に対し `run_deviation_check` だけを旧/新で再実行し、混同行列(origin、changed_actor、severity)と、59記事の最終英文での MAJOR 件数(=STOP 率への影響)を旧/新で比較。費用。
- **V3(M3)**: `s0_excluded_candidates.jsonl` の changed_actor=true 38件を含む run(最終英文に残る19件を優先)について、保存済み Stage 1 候補から再分類→Stage 2 を新スイッチで replay。指標: 保護された候補の Stage 2 判定(BLOCKING/QUALITY/ACCEPTABLE)、EV-25 が BLOCKING になるか、誤った書き換え(台帳と整合する文の書き換え)の件数。費用(換算見込み 約¥0.35/run)。
- 各検証は並列実行可(最大4スレッド)。実行コマンド・固定SHA・出力先(`er052_output/open243_translation_ng_analysis_01/trial_m123_01/`)を記録。

## 判定材料(事実のみ、Fable が判定)
- M1: 要約 STOP 相当(未解消 MAJOR)が 8→何件か。
- M2: 陽性26のうち translation と判定された数/主体型で changed_actor=true になった数/許容3文が MAJOR になっていないか/59記事の MAJOR 総数の増減。
- M3: EV-25 の最終判定、保護19件の内訳、誤書き換え件数。

## SSOT・Git
- `OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md` に新§(§109 の次): 設計(フラグ・差分)、V1〜V3 の結果表、費用、Status=MEASURED(Production 変更なし、フラグ既定 OFF)。
- `DECISION_LOG.md`: ユーザー回答3件の逐語と Go、本委任の結果要約。
- `OPEN_ITEMS.md` OPEN-243: Trial 実装・検証結果の1行追記(3,000字制限、超過は HISTORY へ)。
- `docs/pm/REPORT_LEDGER.md` 更新。
- 個別 add(変更コード、trial_m123_01/、SSOT、delegation_log)。`git status` で混入確認後 commit(例: 「OPEN-243 M1-M3 Trial: 要約だけ再生成+JA/台帳入力、EN検査の主体定義拡張+origin修正、再分類でactor候補保護(全て既定OFF)、既存データ検証 V1 x/14・V2 …・V3 EV-25 …、実費¥xx、REPORT §110」)、`git push origin main`。conflict/エラー時は中断して報告。

## result に書くこと
変更ファイルと差分要点(プロンプト変更前後の全文)、V1〜V3 の結果表と判定材料、実費(トークン×登録単価)、回帰テスト結果(フラグOFF)、commit hash と raw URL(https://raw.githubusercontent.com/shimomura055/eigo-radio/main/<path>)、check_delegation_prompt 結果、所要時間、未解決点・逸脱。
