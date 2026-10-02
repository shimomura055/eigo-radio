## 管理ID

`OPEN-233-SELF-RECOVERY-TRIAL-01`(委任_44: **2周目・3周目で新しい問題が見つかる件の原因切り分け+対策設計**[ユーザー指示§5]。既存記録の読み取り分析、¥0)。
**並行タスクあり**: 委任_42(別のsonnet-worker)が`er052_open233_self_recovery_flow_runner_01.py`とそのテスト・SSOT・`docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md`を編集中でcommitも行う。委任_43・45はread-only調査。**本委任はコード・SSOT・ACTIVE_TASK・RESULT_PACKETを一切編集せず、git add/commit/pushもしない**。
(注: 本ファイルは受領した委任文の要約保存。逐語全文ではなく、構造[管理ID・性質/到達上限Status/禁止事項・固定ブロック・ユーザー指示・分析の定義・出すべき結果・事前指定Read・Grep・実行コマンド・Git・報告]を保持して圧縮した。)

## 性質/到達上限Status/禁止事項

- 性質: read-onlyの既存記録分析と対策設計案の提示(実装しない)。Opus独立技術レビューGate(PM_GOVERNANCE 11-3)の該当判定: 分析自体は非該当。ただし本分析に基づく対策は条件A該当のため、実装前にFableがOpus独立レビューへ回す。報告はOpusが検証できる根拠付きで書く。
- 到達上限Status: 原因の切り分けと対策設計案の報告まで。
- 費用: ¥0(API・TTS・Trial・LLM呼び出しなし)。
- 禁止事項: 実装しない(*.py・Prompt・テスト・SSOT・設計書を編集しない)。runner・Trial・回帰テストを実行しない。Production正式pathを変更しない。git操作は読み取り系のみ。新規作成してよいのはT-0の2ファイルと、`er052_output/open233_cycle_new_issue_analysis_01/`の分析スクリプト・結果のみ。報告は最終メッセージ本文で返す。runnerは`git show e0ae8de0:`のコピーで読む。推測を事実として書かない(決定論的に言えることと推定を書き分ける)。cycle上限を増やす案を第一案にしない。判定基準・Safety原則を変える案はユーザーSTOP条件に触れる旨を明記。CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS全文Read禁止、er0XX_output全文Read禁止。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない。D-1: Grep→該当行範囲Read。G-1: git出力は最小化。F-1: transcript退避不要。T-0: 委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し`check_delegation_prompt.py`を実行、結果を記録(FAILでも継続)。T-2: TTSを伴わない(非該当)。T-1・T-3非該当。

## ユーザー指示(原文、2026-10-02、§5・§6・§8抜粋)

§5: 2周目・3周目で新しい問題が見つかる件は、原因調査だけでなく対策まで行う。同じ元記事でも、1周目では問題Aだけ検出/2周目で別問題Bを初めて検出/3周目でさらに別問題C/あるrunではB/C自体が出ない、という揺れがある。各ケースについて具体文付きで、1周目・2周目・3周目で何を検出したか、各指摘はMinor/Majorどちらか、元記事に最初から存在した問題か、Rewriteで新しく発生した問題か、同じ問題がMinor→Majorへ変化したのか、1周目では完全に見逃していたMajorかを明確にする。原因ごとに対策まで: 重大問題の見逃し→Checker Prompt・チェック順序・全件走査方法を見直し、1回目で重大問題をまとめて検出できる構造を優先/Minor・Major判定の揺れ→基準明確化・決定論的Safetyルールへ寄せる/Rewriteが新しい問題を作る→Rewrite Prompt・最小修正ルール・Rewrite後QAを是正/周回構造→cycle上限を安易に増やさず、なぜ複数周必要になるのかを減らす設計を優先。原因分析だけでSTOPせず、Guardrail内で対策実装+限定再確認まで行う。
§6: Checker出力契約変更/日本語側処理構造見直し/Checker見逃し対策など構造変更に該当する場合は実装前にOpusレビュー必須。
§8: STOP条件(新しいProduct原則の採用/Safety原則の変更/Production正式仕様の変更判断/¥600予算上限超過/Claude案とOpusが重要点で対立しFableで解消不能/QCDトレードオフがありユーザー判断が必要)のみUSER_DECISION_REQUIRED。
(本委任の担当は切り分けと対策設計案まで。実装と限定再確認はOpusレビュー後に別委任。)

## 分析の定義

対象: `er052_output/open233_self_recovery_flow_runner_01_*/instances_*/*.json`のうち2周以上実行されたrun(委任_41と同じ277ファイルの範囲)。「2周目以降の新規指摘」=cycle k(k>=2)でRecheckが返した指摘のうちStage 2後の最終重大度がBLOCKINGのもの。Checkerの`severity`とStage 2の判定(`llm_materiality`・`floor_reason`)を両方記録。分類: (P)元記事に最初から存在[P1 重大度揺れ/P2a 同一fact別箇所の取りこぼし/P2b fact初出の完全見逃し/P3 BLOCKINGのまま書き換えで直らず再指摘]、(R)Rewrite起因[R1 直そうとした範囲そのもの/R2 対象外を変えた]、(U)判定不能。run間の揺れ(固定Stage 1のrun同士)と、固定fixtureとの関係(cycle1 Stage 1出力に低重大度で含まれていたか)を示す。

## 出すべき結果

A. ケース別切り分け(meta_run03_standardの全run、runごとの周回別表と8項目への答え、HC-010・HC-012の既知例の確認、全記事の集計と代表例、Stage 4に限った内訳)/B. 原因ごとの規模/C. なぜ起きるか(コード・Prompt根拠、確認済みと推定の区別)/D. 既存の仕組みと過去の対策(A既存仕様/B過去Trial・未採用/C新規)/E. 原因ごとの対策設計案(1〜3案、Trial専用範囲か・追加LLM費用・非決定性/人間確認/不要Rewrite/Safetyへの影響・既存との重複・STOP条件)、優先順位、最小で効果が見込める組み合わせ、限定再確認の骨子と費用概算。

## 事前指定Read・Grep・実行コマンド

runner(`git show e0ae8de0:`のコピー)の1105〜1188・1277〜1300・1468〜1700・4075〜4264・4490〜4650、`er003_v1_en_direct_vfl_01_generate.py`502〜601、`er051_open233_checker_trial_variant_01.py`175〜250、`er052_open233_self_recovery_stage2_production_01.py`40〜130、固定fixture(rep19)、設計書§4-16・§6-6・§6-8・§6-9・§6-14〜§6-16、`claims_detail_01.csv`。D項のGrep(設計書・Opus L2レビュー・REPORT)。実行: Python `.venv\Scripts\python.exe`で`er052_output/open233_cycle_new_issue_analysis_01/analyze_01.py`を2回実行し結果同一を確認。検算(i)rep21 s1 cycle3のMUSE-HC-010、(ii)rep21 s1 cycle2「These calls were about…」がP3、(iii)無作為10件目視。T-0実行。git add/commit/pushはしない。

## SSOT追記文・Git

SSOT追記なし。git add/commit/pushは行わない。

## 報告

RESULT_PACKETには書かず最終メッセージ本文に: 1結論 2対象・分母・除外 3A 4B 5C 6D 7E 8検算・限界 9読んだファイル・T-0結果1行・作成ファイル。
