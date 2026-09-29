管理ID: OPEN-233-SELF-RECOVERY-TRIAL-01(委任_01: Production Self-Recovery Flow の設計書作成。**API 呼び出しなし・¥0・Production 非接続・実装なし**)
日付: 2026-09-30。作業ディレクトリ C:\Users\tensh\eigo-radio。

## 0. 前提(必ず最初に読む)
- docs/pm/PM_BRIEF.md 固定ヘッダ、docs/pm/PM_GOVERNANCE.md 8節(禁止事項: 削除・移動・rm・stash・git add -A・履歴書換 禁止)。
- 前 Phase 成果(必要箇所のみ): OPEN-233-CHECKER-REDESIGN-TRIAL-01_REPORT.md §9〜§13、docs/pm/design_open233_checker_redesign_trial_01.md(§2-補 claim 単位 gold 候補表、§4-補 原因分類)、**docs/pm/opus_l2_review_open233_checker_trial_01.md(全文、特に論点 1 推奨 1・2・4[2 段階呼び出し]、論点 2 の claim 単位評価表、論点 4 推奨 2[self-consistency]、論点 5)**、docs/pm/negative_claim_candidates_open233_01.md、er051_open233_checker_trial_variant_01.py(V4-A)、er051_output/open233_checker_trial_01/(Trial 1/2/n=20 生データ)。
- 現行 Production フロー(Grep で該当箇所のみ): er012_e_family_entertainment_two_level_runner_01.py の run_writer_stage()/_run_writer_stage_once()/JARecheckRequiredError 処理(案B: ja_source MAJOR → JA must-fix 差し戻し 1 回 → 再 Fact Check → 再英訳 → 再 Deviation Check → なお MAJOR なら STOP)、Standard/Advanced 段の deviation MAJOR 後の retry 機構(attempt 上限・feedback の渡し方)、er019_family_x_entertainment_production_runner_01.py の STOP/USER_DECISION_REQUIRED 発生箇所、er003_v1_en_direct_vfl_01_generate.py の run_deviation_check()/DEVIATION_PROMPT_TEMPLATE/HOOK_CLAUSE(読むのみ)。
- E2E STOP 実績: FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_REPORT.md の Hormuz run_01〜03 STOP 理由(HF-006/HF-011/HF-009×2)と、Meta run_03 の通過経路(retry 回数)。
- 一時ファイル: docs/pm/ACTIVE_TASK_C233E.md / docs/pm/RESULT_PACKET_C233E.md(新規、commit 禁止)。既存 *_C233A〜D は削除・移動しない。

## 1. ユーザー意図(2026-09-30 更新、逐語要旨。DECISION_LOG へ 1 エントリで記録すること)
- 最終目標: **通常の Production 運用中に、Ledger/Deviation Check を理由としてユーザー判断を求められる状態を実質ゼロにする**。現状「数記事に 1〜2 件 Checker STOP → USER_DECISION_REQUIRED」は量産性・開発速度の両面で許容できない。
- Checker 単体の完璧化が目的ではない。Production フロー全体として「初回 Check → 必要なら再スクリーニング → 必要なら自動 Rewrite → 再 Check → Production 継続」までシステム側で安全に完結させる。ユーザーへ上げるのは「自動処理では安全に解決できない、本当に例外的なケースだけ」。
- Safety は絶対条件: Fact 反転/actor 取り違え/number・numeric scope 重大変更/negation 反転/comparison 方向反転/time・chronology 重大変更/unsupported material fact/主要 Fact 理解を変える causality は確実に止める。**重大 fixture の見逃し 0 件**を維持。
- Self-Recovery Flow: Stage 1 Initial Check(ACCEPTABLE/QUALITY/BLOCKING 分類、ACCEPTABLE/QUALITY は継続候補、BLOCKING のみ次段)→ Stage 2 Re-screening(同じ判定の機械的反復ではなく「本当に Production を止めるべき material error か」を再評価。候補: materiality 専用 Second Judge/独立 Prompt/original Ledger+source context+対象 claim 再提示/qualifier・context・observation 整合確認/deterministic safety rule 照合/GPT-6 Luna 独立再判定。目的=初回 Checker の過剰品質・非決定性の吸収)→ Stage 3 Automatic Rewrite(問題 claim のみ・該当 sentence/local context・必要最小範囲を修正 → 再 Checker、既存案B 等 reuse 可)→ Stage 4 Final Escalation(Re-screening+Rewrite+Recheck でも安全に解消できない場合のみ USER_DECISION_REQUIRED、通常運用では実質ゼロ)。
- 主要受入条件の変更: 「不要 BLOCK 率 ≤25%」は主要受入条件から外し **診断用の中間指標**として残す。Primary KPI=**10〜20 記事規模の Production 相当 Trial で Ledger/Deviation Check 起因の USER_DECISION_REQUIRED=0 件**。Safety=重大 Fact 事故の見逃し 0 件。Self-Recovery 測定: Initial BLOCK 件数/Re-screening 自動解消件数/Rewrite 進行件数/Rewrite 自動解消件数/Final STOP 件数/USER_DECISION_REQUIRED 件数。QCD: Checker call 数/記事、Rewrite 回数/記事、平均追加 cost、P50/P95 latency、completion 率、retry 率、loop 率。**ゼロ STOP を無制限 retry や高コストで実現するのは NG**。
- Trial の考え方: 最初から 10〜20 記事を高コストで回さない。まず既存 fixture/artifact(Hormuz run_01〜03、Meta、A 群、B 群、ER-009-N1 重大 fixture、changed_actor、negative claim 候補、n=20 stability data)を最大限 reuse して Safety/過剰 BLOCK/re-screening/rewrite recovery を検証。設計が成立したら Production 相当の記事 Trial へ拡大。
- Opus L2: recovery flow 全体設計/Second Judge 設計/Rewrite 対象範囲/Safety と生産性のトレードオフ/retry loop 化リスク/cost・latency 肥大化/人間確認ゼロを狙うことによる新規リスク を重点レビュー。重要な設計変更後は再レビュー可。
- Iterative Trial 継続(1 回未達で終了は禁止)。同じ方法で改善しない場合は漫然と反復せず、なぜ改善しないかを分析して別方式へ切り替える。
- 予算: 新たに最大 ¥400(前 Phase の ¥45.68 とは別管理)。iteration 費用/今回 Phase 累計/残予算を管理。
- Mandatory Checkpoint: A=新 Self-Recovery 設計+Opus 初回レビュー完了時、B=最初の実 Trial 終了時、C=大きな設計変更を伴う次 Trial 前、D=Phase 累計 ¥100/¥200/¥300 前後、E=10〜20 記事相当の最終 Trial 前。中間報告項目: 現在 best variant/Safety/Initial BLOCK 率/Re-screening 解消率/Rewrite 解消率/Final STOP・USER_DECISION_REQUIRED/cost/latency/前 iteration からの改善/次に試すこと/最大リスク/Phase 累計費用・残予算。「Production で人間へ上げずに完結できそうか」を中心に。
- USER_DECISION_REQUIRED で即 STOP: 重大 Fact 事故を許容する方向への Safety 緩和/新 Product 原則/gold の意味を大きく変更/Human Review を通常 Production flow に組込/Family X 以外への展開/Production 正式 path 変更/GPT-6 Luna routing 正式変更/最終 Checker 仕様の Production 採用。
- Production はまだ触らない(Trial/DEV 専用)。目標達成後 `VALIDATED` で STOP し正式採用をユーザーへ求める。
- 目指す挙動: Normal=Check→PASS→継続/False・borderline BLOCK=Check→BLOCK→Re-screen→QUALITY/ACCEPTABLE→継続/Real but fixable=Check→BLOCK→Re-screen→Rewrite→Recheck→PASS→継続/True exceptional=それでも解消不能→USER_DECISION_REQUIRED(通常運用ではほぼ発生しない)。

## 2. Fable 判定(設計の前提として明記)
- 前 Phase の USER_DECISION_REQUIRED 3 件(指標定義/gold/materiality 軸)は、本 Phase では次のように再構成し、Checkpoint A でユーザー確認を取る(独断確定しない): (a) 不要 BLOCK 率は診断指標へ格下げ(ユーザー指示)。(b) gold は **「最終到達状態」ベース**へ再構成する: 重大 fixture(ER-009-N1 9 種・A 群・changed_actor)=Stage 1/2 で必ず BLOCKING 維持(Stage 2 で通過させたら Safety 事故)、その後 Rewrite→PASS が期待到達状態。B2=Stage 2 で QUALITY 通過が期待。B1/B4=Opus claim 単位評価どおり material claim(B1-c/B4-a)は Rewrite 対象、非 material claim(B1-a/b、B4-b/c)は Stage 2 通過が期待、fixture としては Rewrite→PASS 到達が期待。B3=material(HF-007 conditions)につき Rewrite→PASS が期待。negative claim 候補 16 件=Stage 1 または Stage 2 で通過が期待。**いずれも「候補 gold(ユーザー確認待ち)」と明記**。(c) materiality 軸は Stage 2 Second Judge の判定基準として設計する(Stage 1 Production Prompt は不変)。
- Stage 2 の **deterministic safety floor**: Stage 1 で changed_actor/changed_number/changed_negation/changed_comparison/changed_time のいずれかが true の deviation は、Stage 2 で ACCEPTABLE/QUALITY へ降格させない(Rewrite 必須)。Stage 2 が降格できるのは、これら flag が全て false の deviation のみ。降格判断は「迷ったら Rewrite へ」(fail-closed)。
- 既存案B(ja_source MAJOR → JA 差し戻し 1 回)は Stage 3 の JA 側 Rewrite として位置づけ直し、無駄な全文再生成を避ける「局所 Rewrite」を優先候補とする。
- loop 上限は設計で固定(例: Stage 2 は 1 回、Stage 3 Rewrite は記事あたり最大 2 回、Recheck は Rewrite ごと 1 回、合計 Checker call 上限/記事)。無制限 retry 禁止。

## 3. 作成する設計書 docs/pm/design_open233_self_recovery_flow_01.md(章立て固定)
1. 目的・ユーザー意図(§1 の逐語要旨)・Fable 判定(§2)
2. **現行 Production フローの実態**: Family X の Check→retry→STOP の現行経路を図示(段階/attempt 上限/feedback 内容/STOP 条件)。Hormuz run_01〜03・Meta run_03 の各 STOP/通過が現行フローのどこで起きたかを Evidence 付きで表にする。「現行でも Rewrite 相当(retry)は存在するのに STOP した理由」を run ごとに分類(retry 上限到達/ja_source 案B 1 回上限/retry しても同じ deviation が再発/ 等)。
3. Self-Recovery Flow 設計(Stage 1〜4): 各 Stage の入力・出力・判定基準・使用 Prompt/モデル(gpt-6-luna、Trial 限定)・deterministic rule・loop 上限・STOP 条件・ログ項目。状態遷移図(テキスト)と、記事 1 本あたりの最大 call 数・最大コストを明記。
4. Stage 2 Second Judge 設計: 独立 Prompt(Stage 1 Prompt と別物、Opus 論点 1 推奨 2 の materiality 基準[Ledger claim/scope/numeric_value/date_or_period/conditions との矛盾=BLOCKING、Ledger が保証しない関係付け=QUALITY、一般常識背景=ACCEPTABLE]、「迷ったら BLOCKING」)、入力(Ledger 全文+source context+対象 claim+Stage 1 の deviation 出力+前後 sentence)、出力 schema(materiality/basis/qualifier/observation_consistent/rewrite_hint)、deterministic safety floor(§2)、Stage 1 との独立性担保(Prompt/温度/呼び出し分離)。
5. Stage 3 Automatic Rewrite 設計: 局所 Rewrite(問題 claim を含む sentence±1 のみを Ledger と rewrite_hint で書き換え)/段階別(JA 側は案B reuse、EN Standard/Advanced 側は局所 Rewrite)/Rewrite 後の再 Check 範囲(全文 Checker か局所 Checker か、fail-closed の観点で全文推奨かを検討)/Rewrite が原文構造(見出し・In one line・Phrase 等の Family X 構造)を壊さないための guard(既存 split_family_x_article_text_v2 の NG 条件 reuse)/上限。
6. Stage 4 Escalation 条件と、そこで人間に渡す情報(何を確認すべきかを一意に示す)。
7. gold(最終到達状態ベース、§2(b)、候補としてユーザー確認待ち)と fixture 群の再編: Safety 群/False・borderline 群/Real-but-fixable 群/Normal 群(negative 16 件)。各 fixture について期待 Stage 経路(例: B2=S1 BLOCK→S2 QUALITY→PASS)。
8. 測定項目(ユーザー指定 Self-Recovery 6 項目+QCD 7 項目)の定義と算出方法。不要 BLOCK 率は診断指標として併記。
9. Trial 計画: Phase 1(既存 fixture/artifact reuse: Stage 2 単体を既存 Stage 1 出力[Trial 1/2/n=20 の deviation json]へ適用=Stage 1 の再課金なし、Rewrite は B 群・Hormuz・Meta の実 artifact で実施)、Phase 2(Production 相当 10〜20 記事、Checkpoint E 前に別途計画)。Phase 1 の call 数・費用見積(公式単価 gpt-6-luna In $0.10/Cached $0.01/Out $0.50、¥156.88、既存 Trial の実測 token を根拠に)・Guardrail。
10. リスク: retry loop 化、cost/latency 肥大、人間確認ゼロによる新規リスク(Stage 2 が material を通す/Rewrite が新たな逸脱を生む/Rewrite が構造を壊す)、Stage 1 非決定性(recall 85〜100%)が Stage 2 以降で拡大しないか、HOOK_CLAUSE 衝突(Family 横断時)。各リスクの緩和策。
11. Opus L2 に問う論点(ユーザー指定 7 点を中心に 5〜7 個、各論点に本設計の暫定答えを添える)。
12. ユーザー判断 11 該当有無(該当すれば内容と STOP 提案)。

## 4. 記録・Git
- 新 REPORT: OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md を新規作成(§1 設計フェーズ、費用: 今回 ¥0/Phase 累計 ¥0/残 ¥400、前 Phase 累計 ¥45.68 は参考として別枠記載)。
- SSOT(最小限、1 agent のみ): DECISION_LOG.md にユーザー意図(§1)と Fable 判定(§2)を 1 エントリ。OPEN_ITEMS.md の OPEN-233 行に「新 Phase OPEN-233-SELF-RECOVERY-TRIAL-01 開始、Status=DESIGN_IN_PROGRESS、予算 ¥400 別管理」を追記(既存追記は削除しない)。CURRENT_SPEC.md 不変。REPORT_LEDGER は文案のみ。
- delegation_log: docs/pm/delegation_log/2026-09-30_OPEN-233-SELF-RECOVERY-TRIAL-01_01.md 作成+check_delegation_prompt.py 実行(FAIL 既知・non-blocking)。
- commit: パス指定 git add(-A 禁止)、Management-ID trailer、ACTIVE_TASK*/RESULT_PACKET*/.env は add しない。競合時 git merge origin/main のみ。
- 事後確認: git diff --stat で Production ファイル無変更。
- 報告(RESULT_PACKET_C233E.md と handback、簡潔に): 【現在の状態】【現行フローで STOP が起きた理由の分類(run 別)】【Self-Recovery Flow 概要(Stage 1〜4、loop 上限、記事あたり最大 call/cost)】【Second Judge 設計の要点と deterministic safety floor】【Rewrite 設計の要点】【gold 候補(到達状態ベース)】【Phase 1 Trial 計画・費用見積・Guardrail】【最大リスク】【Opus 論点案】【ユーザー判断 11 該当有無】【費用 ¥0/累計 ¥0/残 ¥400】【Git(hash・raw URL)】【Status=DESIGN_READY_FOR_OPUS_L2 または USER_DECISION_REQUIRED】。

## 5. 禁止
API 呼び出し(有料)、Production ファイル(er003_*/er006_*/er012_*/er019_*)の変更、gold の独断確定、Stage 1 Production Prompt の変更提案を「採用済み」のように書くこと。
