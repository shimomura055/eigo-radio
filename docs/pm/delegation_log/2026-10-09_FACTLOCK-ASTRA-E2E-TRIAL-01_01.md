管理ID: FACTLOCK-ASTRA-E2E-TRIAL-01 委任_01(設計書+事前登録+新テーマ候補+ユーザー決定記録、API生成支出¥0、Production変更なし)。日付 2026-10-09。

## 背景(Fableからの要約、正本は参照先)
- 目的: 新Writer仕様(Fact Lock R0[Luna] + Astra Revise R1→R2[系列X]) と 翻訳段対策(OPEN-243 M1+M3 ON、M2は見送り=OFF維持)を織り込んだE2E Trialを10記事で走らせ、(1)Writer変更の良化、(2)翻訳仕様変更(M1/M3)の良化、(3)Checkerの重大/軽微・Rewrite率・Human Review率を、旧仕様との差分付きで評価する。
- ユーザー決定(2026-10-09、逐語に近い形で記録すること):
  1. E2E Trial規模: 10記事 / TTS 2本 / **予算上限¥1,000**(途中停止を避けるため¥700から引き上げ)。
  2. Astra tier: E2EはStandard同期。Flexは別途評価(本Trialに含めない)。Batchは対象外(委任_18の調査結果: 24h窓・2段で算術上限48h・改修7箇所)。
  3. M2(EN検査プロンプト拡張)は見送り(OFF維持)。
  4. 構成: **旧4テーマ(META/ホルムズ/宇宙兵器space_weapons/ミニバッグsmall_bag)+新6テーマ(候補提示→ユーザー選定)=10記事。全記事で旧仕様腕を併走**(paired design: research→台帳→B3は両腕で共有。旧4テーマは凍結済みの台帳・B3を再利用、新6テーマは新規research)。
  5. 設計書作成へGo(「OKです。開始してください。」)。実行(API支出)はまだGoされていない。
- Fableの見積(確定値ではない、設計書では「見積」と明記): 新仕様腕 約¥56/記事 + 旧仕様腕 約¥9〜10/記事 ≈ ¥65〜66/記事 ×10 + TTS 2本・ASR 約¥40 ≈ ¥700前後。時間: 3並列で約2〜2.5時間(Checker 345秒/run実測×40 run が主)。
- PM運用ルール: 価格・費用など重要数値は確認済みの出典のみ使い、未確認は「未確認」と書く(推定を確定値のように書かない)。astra単価の正本: `er052_output/factlock_writer_trial_01/astra_pricing_01/extracted_pricing.json`(Standard 10/1/12.5/50 $/1M、Batch・Flex 50%、2026-10-08 16:38 JST取得)。USD/JPY=160。

## 事前指定Read一覧(全文読込禁止のSSOTはGrepのみ)
- `docs/pm/PM_BRIEF.md`(固定ヘッダ+PM運用メモ)
- `OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md` §81(新仕様Checker 9 run結果、L4763〜4830付近)、§106〜§110(Fact Lock/Astra matrix/OPEN-243 M1-M3)。GrepでSection見出しを特定してから該当範囲のみRead。
- `er052_output/open243_translation_ng_analysis_01/{ANALYSIS_01.md, COUNTERMEASURES_01.md, trial_m123_01/DESIGN_M123.md, trial_m123_01/RESULTS_M123.md}`
- `er052_output/factlock_writer_trial_01/astra_revise_matrix_02/{DESIGN.md または設計相当, USER_PACK_02.md, COST_MATRIX_02.md}`、`astra_revise_matrix_01/{DESIGN.md, tools/run_matrix.py}`(系列Xのユーザーメッセージ逐語・reasoning high・previous_response_id不使用・800〜1000字ソフトキャップ)
- `er052_output/factlock_writer_trial_01/RESULT.md`(Fact Lock v1仕様、R0プロンプト漏れ「これ、ちょっと面白くない？」と思うのは、harness不具合=phase2 JA再生成でタグ残存)
- `docs/pm/e2e_plan_open233_stage1_loop2_01.md`(前回E2Eの計画書フォーマット・Waste検知・停止条件)
- `er052_output/open233_prod_e2e_02/e2e_summary_02.json`(並列実行の実測時間)、`er052_output/gpt6_wiring_e2e_01/E2E_EVIDENCE.md`(run_02 費用¥19.105・326秒)
- `docs/pm/delegation_log/2026-10-08_FACTLOCK-WRITER-REDESIGN-TRIAL-01_18_result.md`(Batch/Flex事実表)
- 凍結データの所在確認(存在確認のみ、内容の全文Readは不要): `er052_output/all6_writer_redesign_necessity_01/runs/driver_result.json`、`er052_output/factlock_writer_trial_01/runs/driver_result.json`、`er052_output/gpt6_wiring_e2e_01/run_02/{research_ledger/verified_fact_ledger.txt, storyline_b3/selected_brief.md}`、`er052_output/open233_prod_e2e_02/`
- コード(該当箇所のみGrep/Read): `er019_family_x_ja_writer_o_r1_r2_01.py`(Production JA Writer)、`er012_e_family_entertainment_two_level_runner_01.py`(M1分岐 L418付近)、`er003_v1_n3_01_advanced_adaptation_generate.py`(generate_family_x_in_one_line)、`er052_open233_stage1_reclassify_01.py`(M3)、`er006_model_routing_contract_01.py`・`er005_output/cost_baseline_01/pricing_snapshot.json`(astra単価未登録のfail-closed)、`er052_open233_e2e_acceptance_01.py`(前回E2E runnerの構造)

## 成果物(すべて新規作成。既存コード・Production・SSOT本体の変更は本委任では禁止。例外: 下記のDECISION_LOG/ACTIVE_TASK/REPORT_LEDGER追記)
1. `er052_output/factlock_astra_e2e_trial_01/DESIGN_E2E_01.md` — 設計書。必須節:
   - §1 目的・評価対象(1)(2)(3)と、各々の指標定義・比較対象(旧仕様腕=同一台帳/B3からLuna R0→R2+EN(M1/M3 OFF)+Checker; 加えて旧4テーマは過去の凍結出力[§81の9 run等]とも並記)。指標は§81と同じ集計表フォーマットに揃える。
   - §2 処理フロー(1記事): research→台帳→B3(新6のみ。旧4は凍結再利用のパスを明記)→[新仕様腕] Fact Lock R0(Luna、プロンプト漏れ修正後)+JA FC → Astra R1→R2(Standard同期、reasoning high、系列Xユーザーメッセージ逐語、previous_response_id不使用、各段後JA FC、800〜1000字ソフトキャップ)→記号後変換(「……」「——」)+Markdown除去→EN Advanced+Standard(M1 ON、Standard分岐の実装要否を明記)→EN deviation check→Checker(承認スイッチ`OPEN233_APPROVED_FLOW_SWITCHES`・`FLOOR_MODE=number_only`+M3 `OPEN233_RECLASSIFY_PROTECT_FLAGS=changed_actor`)、[旧仕様腕] Luna R0→R1→R2(現Production経路)→EN(フラグ全OFF)→Checker(同承認スイッチ、M3 OFF)。TTS 2本はStandard同期(対象記事はテキスト結果後にFable/ユーザーが選定)。
   - §3 M1/M3の寄与分離テレメトリ: 別runを増やさず、M1再生成の発火前/後の要約・検査結果、M3で保護されたclaimとその後の判定を全件ログに残し「フラグが無ければどうなっていたか」を再構成できるようにする設計。
   - §4 前提作業一覧(実装は本委任では行わない。各項目に対象ファイル・行・見積行数・リスク): (a) gpt-6-astra単価の正式登録(routing contract+pricing_snapshot、出典・取得時刻付き)、(b) Fact Lock R0プロンプト漏れ修正、(c) phase2 JA再生成のタグ残存不具合修正、(d) M1 Standard(A2)分岐実装、(e) 記号後変換+Markdown除去の組込位置、(f) 2腕並走runner(台帳/B3共有、腕ごとの環境変数分離、同一ファイル・state競合の回避)、(g) 予算ガードがweb_search課金を計上しない既知差(E2E_EVIDENCE.md L44)への対処方針。
   - §5 実行計画: 並列度3(単層並列、PCクラッシュ教訓: 二重並列禁止、空き物理メモリ監視)、実行順(旧4→新6、各テーマ内で旧腕→新腕 or 並走)、1 run費用上限・Waste検知・即停止条件(前回計画書を踏襲)、累計上限¥1,000、途中停止時の再開手順。
   - §6 費用・時間見積(見積と明記。実測根拠は出典付き。astra単価は上記正本)。
   - §7 評価手順: 自動集計→Sonnetラベル(3 worker分割可)→Fable突合→ユーザー人間確認(2〜3記事)→Opus条件C。ユーザー提示パック(元記事+新R2のみ、R1不要)の形式。
   - §8 Opus条件Aレビューに出す論点(5〜7個)。
2. `er052_output/factlock_astra_e2e_trial_01/PREREGISTRATION_01.md` — 事前登録: 各指標の判定基準(良化/同等/悪化の線引き)、n=10の統計的限界の明記、変更禁止事項。
3. `er052_output/factlock_astra_e2e_trial_01/NEW_THEME_CANDIDATES_01.md` — 新テーマ候補 **10件**(英語タイトル・日本語タイトル・短い選定理由・一次情報が取れそうな根拠・難易度[数字多い/固有名詞多い/因果が絡む等の多様性を確保])。既存テーマ(META/ホルムズ/宇宙兵器/ミニバッグ/下水道/旅行荷物/AI採用)と重複しないこと。ユーザーが6件選ぶ前提。web検索APIは使わない(¥0)。
4. SSOT追記(本体の全文読込禁止、末尾追記のみ): `DECISION_LOG.md`末尾に本管理IDのユーザー決定1〜5を記録(日付・逐語に近い形)。`docs/pm/ACTIVE_TASK.md`固定ヘッダを本管理ID 委任_01=DESIGN_READY(実行Go未)に更新(既存のUDR-blocking・未回答報告の行は削除せず維持)。`docs/pm/REPORT_LEDGER.md`に1行追加。
5. 委任記録: 本委任文全文を `docs/pm/delegation_log/2026-10-09_FACTLOCK-ASTRA-E2E-TRIAL-01_01.md` に保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path>` の結果を記録(FAILでも続行、記録用)。最終報告を `docs/pm/delegation_log/2026-10-09_FACTLOCK-ASTRA-E2E-TRIAL-01_01_result.md` と `docs/pm/RESULT_PACKET.md` の両方に書く。
6. Git: 上記の新規・変更ファイルだけを明示的に`git add`(`git add -A`禁止)、commit、`origin/main`へpush。commit hashと変更ファイルのraw.githubusercontent.com URL(https://raw.githubusercontent.com/shimomura055/eigo-radio/main/<path>)を報告に含める。

## 禁止事項
- API生成呼び出し(OpenAI/Gemini)一切禁止。¥0で完了すること。
- 既存の`er0XX_*.py`・Prompt・`CURRENT_SPEC.md`・`OPEN_ITEMS.md`の編集禁止。
- 設計書の中で未確認の数値を確定値として書かない。推定には「見積」「推定」を付け、根拠ファイルを併記。
- 新テーマをFable/Sonnetが単独で決めない(候補提示のみ)。

## 報告形式(result.md)
1. 成果物パス一覧とcommit hash・raw URL
2. 設計の要点(10行以内)
3. 前提作業一覧の要約(a〜g、各1行: 対象ファイル・見積行数・リスク)
4. 費用・時間見積の要約(出典付き)
5. Opus条件Aに出す論点
6. 未確認事項・判断が必要な点(Fable向け)
7. 所要時間・API支出(¥0であること)

---
## check_delegation_prompt.py 結果(記録用、2026-10-09、FAILでも続行)
status: FAIL。必須セクション欠落(事前指定Grep一覧+追記位置・更新位置の手順/実行コマンド全文)、固定ブロックラベル欠落(E-1/D-1/G-1/F-1)。warnings: TTS_EXECUTION_MODE=STANDARD未明示・差分再生成/--budget未言及(本委任はTTS実行なし、設計のみ)、KPI provenance欄なし、Opus台帳更新欄なし。指示どおり続行。
