## 管理ID
FAMILY-A-DISCOVERY-S2-PRODUCTION-DESIGN-01

## 範囲
性質: ¥0設計(実装・配線禁止)。到達Status: 設計完了→`USER_DECISION_REQUIRED`(Gate 2)でSTOP。現在Status=VALIDATED→Production設計着手可(APPROVED_FOR_PRODUCTIONではない)。Productionコード(er0*)無編集、Trial driverも無編集。並行中のFuture Family C(`EDITORIAL-FUTURE-*`、`er013_*`)のファイルに触れない。API呼び出しなし。Sonnet往復1回で完結(不明点は代替案併記)。`git index.lock`があれば10秒待ち最大3回。

## 固定ブロック
---
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0: 本委任文を`docs/pm/delegation_log/FAMILY-A-DISCOVERY-S2-PRODUCTION-DESIGN-01.md`へ保存し、`.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file "C:\Users\tensh\eigo-radio\docs\pm\delegation_log\FAMILY-A-DISCOVERY-S2-PRODUCTION-DESIGN-01.md" --json-out "C:\Users\tensh\eigo-radio\docs\pm\delegation_log\FAMILY-A-DISCOVERY-S2-PRODUCTION-DESIGN-01_check.json"`を実行し結果をRESULT_PACKETへ1行記録(FAILでも継続)。
---

## ユーザー指示(原文、REPORT冒頭に転記)
> ユーザーは、S2について追加Trialを先に増やさず、Production設計フェーズへ進むことを承認しました。ただし、これはまだProduction実装・配線承認ではありません。現在StatusはVALIDATED→Production設計着手可であり、APPROVED_FOR_PRODUCTIONではありません。次は費用ゼロで、S2のProduction設計を詰めてください。設計対象は少なくとも以下です。現行`run_one_pattern`をどう分割するか/Focus→Main Story→Point Role Planning→Point生成、の正式な処理順/retry単位/`STAGE1_MAX_REGENERATIONS`のProduction値案/「通常はMain Story固定、ただしLocal Rewrite等の安全装置による修正は例外」という原則/Main Story側MAJOR・FAIL時のStage 1再生成条件/Stage 2-3 exhaustion時の扱い/Local Rewrite・Point Overlap・Point Value・Directional Precheck・Evidence Compressionとの整合/retry・fallback・regeneration全体での一貫性/News・Trend・Discovery既存Productionとの競合・共通化可能性/Fact Checker FAILのlocus分類をProductionでどう扱うか/Dangling Reference有無。設計案には、推奨案だけでなく主要な代替案とQCD上の差も示してください。Productionコードへの実装・配線はまだ行わず、設計完了後にGate 2としてユーザー判断を求めてSTOPしてください。

## 事前指定Read一覧
- `er011_discovery_focus_s2_full_trial_01.py`(全文、1回。冒頭の分岐コメントと各Stage関数)
- `FAMILY-A-DISCOVERY-FOCUS-S2-FULL-QA-PARITY-TRIAL-01_REPORT.md`: §3・§4・§7のみ(Grep `^## `で位置特定→該当範囲)

## 事前指定Grep一覧+更新位置の手順
1. `er003_v1_n3_01_articles_generate.py`: Grep `-n` `def run_one_pattern|editorial_mode|EDITORIAL_TYPE_MODULE_BLOCKS|resolve_editorial_type_module_block|POINT_OVERLAP_ARTICLE_RETRY_MAX|MAX_REWRITE_CYCLES|diagnostic_full_retry|run_point_role_planning|apply_evidence_compression|run_directional` で分割点候補の行番号を特定し、`run_one_pattern`本体(L818-1248付近)は1回だけ範囲Read。
2. `er011_point_role_value_planning_01.py`: Grep `-n` `def run_point_role_planning|def build_role_planning_block|ROLE_PLANNING_PROMPT_TEMPLATE`(シグネチャ確認のみ)。
3. `er006_pool_pilot_01_writer.py`および`er011_discovery_generalization*_run.py`: Grep `-n` `run_one_pattern\(`(Production呼び出し元の一覧と引数)。
4. `CURRENT_SPEC.md`: Grep `-n` `run_one_pattern|Point Role Planning|Trend Synthesis|editorial_type_module_block`(現行正式仕様の該当行のみ)。
5. `docs/pm/PM_GOVERNANCE.md`: Grep `-n` `Gate 3|14項目`(配線時チェックリストの所在確認のみ)。
SSOT全文読込禁止。

## 設計内容(REPORTに章立て)
1. **分割設計**: `run_one_pattern`を(a)`run_stage1_main_story`(Focus付きMain Story生成+Stage 1 QA)/(b)`run_stage2_role_planning`(Main Story本文入力)/(c)`run_stage3_points_and_qa`(Point生成+Evidence Compression+結合+記事全体QA)に分割し、既存`run_one_pattern`は**無変更のまま残す**(News/Trend既定経路)か、共通関数化して`editorial_mode`で分岐するか — 代替案を最低2案(案P1: Discovery専用の新関数`run_one_pattern_staged`を追加し既存は不変[opt-in]/案P2: `run_one_pattern`内部を段階化し全モードで同じ骨格にする[News/Trendも影響])とし、QCD(品質・安全・コスト・納期・回帰範囲)を表で比較。推奨+理由。
2. **正式処理順**: Focus決定(型モジュール解決)→Stage 1→Stage 1 QA→Stage 2→Stage 3→記事全体QA→Directional Precheck、の順を図示。各Stageの入力・出力・保存artifact。
3. **retry単位・しきい値**: 通常=Stage 1固定でStage 2-3再実行(`POINT_OVERLAP_ARTICLE_RETRY_MAX`既存値)。Stage 1再生成条件=Main Story側Ledger MAJORがLocal Rewrite上限で未解決/Stage 1 Fact Checker FAIL/Stage 2-3 exhaustion後のfallback。`STAGE1_MAX_REGENERATIONS`のProduction値案(1 vs 2、コスト・安全のトレードオフ、Trial実測[Main Story ¥15〜20/本]から期待コスト増を試算)。全体の再生成回数上限と既存Diagnostic Full Retryとの対応関係(重複しないよう1本化)。
4. **Main Story固定原則の明文化**: 「Stage 2-3を通じてMain Storyは固定。ただしLocal Rewrite等の既存安全装置による局所修正は例外として許容し、修正後は差分QAで再検証」を仕様文として起草。
5. **Fact Checker FAILのlocus分類**: 案(i) `unsupported_specific_claims`の各claimを`locate_target_sentence`でMain Story/Point側に分類しMain Story側があればStage 1へ/案(ii) 簡略ルール(Stage 2-3 exhaustion後のみStage 1)/案(iii) 常にStage 1から。QCD比較+推奨。
6. **既存QAとの整合表**: Local Rewrite/Point Overlap/Point Value/Directional Precheck/Evidence Compression/差分QA/3V無関係、それぞれ「どのStageで・何回・既存値のまま」を表に。
7. **News/Trend/Discoveryとの競合・共通化**: 案P1/P2それぞれで、既存モードのバイト不変性をどう担保するか(既存テストのパターン、`editorial_mode`既定値)。将来News/Trendへ段階化を広げる場合の条件。
8. **Dangling Reference**: Trial-04/S2 Trialファイルへの依存が残らない構成(Production化時にTrial専用コピーを廃止するか、参照を切るか)。
9. **Gate 3への準備**: 配線時に必要なテスト一覧(分岐テスト、バイト不変テスト、統合テスト、runtime evidence取得方法)と、実データ未検証分岐(Stage 1再生成等)の検証計画(意図的MAJAR Ledgerでの1本、見積)。
10. **Gate 2判断事項**: ユーザーに決めてもらう項目を列挙(案P1/P2、`STAGE1_MAX_REGENERATIONS`値、locus分類案、Trial専用ファイルの扱い、実装着手の可否と費用)。

## 実行コマンド全文
- `git status --porcelain`

## SSOT追記文
- 編集しない(REPORT末尾に「SSOT追記文案」として、OPEN-135追記案・DECISION_LOG案・CURRENT_SPEC案[Gate 2承認後に反映する条件付き]を提示)。

## Git
明示`git add`: `FAMILY-A-DISCOVERY-S2-PRODUCTION-DESIGN-01_REPORT.md`、`docs/pm/delegation_log/FAMILY-A-DISCOVERY-S2-PRODUCTION-DESIGN-01*`、`docs/pm/RESULT_PACKET_S2D.md`は`.gitignore`対象なら除外。`-A`/`stash`/`amend`禁止、`er013_*`/`EDITORIAL-FUTURE-*`を含めない。コミットメッセージ`FAMILY-A-DISCOVERY-S2-PRODUCTION-DESIGN-01: Discovery S2 Production設計(¥0、Gate 2判断待ち)`、末尾に
```
Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01THnbjj6FiMbJtrKdFteoE4
```
`git push origin main`まで(拒否時はエラー原文を報告し回避しない)。

## 報告
`docs/pm/RESULT_PACKET_S2D.md`(30行以内): 推奨案とQCD差の要点、`STAGE1_MAX_REGENERATIONS`案、locus分類推奨、Gate 2判断事項一覧、T-0検証結果、commit hash。最終メッセージ8行以内。
