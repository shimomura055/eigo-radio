Fableからの委任_02B(NUANCE-EXPLANATION-PRODUCTION-WIRING-01 Track A+C: 表示(ニュアンス独立コーナー・文法0件完全非表示)・page_verify一般化・HR統合(V3フォーム/exporter/confirm)。API 0)。本プロンプト全文を `docs/pm/delegation_log/2026-10-29_NUANCE-EXPLANATION-PRODUCTION-WIRING-01_委任_02B.md` に逐語保存してから開始。`tools/stop_scope_check_01.py --managed-id NUANCE-EXPLANATION-PRODUCTION-WIRING-01 --run-dir docs/research/NUANCE-EXPLANATION-PRODUCTION-WIRING-01 --out docs/research/NUANCE-EXPLANATION-PRODUCTION-WIRING-01/stop_check_02B.json`(rc=3で停止)。

## 1. 正本とFable判断
ユーザー原文 `docs/pm/delegation_log/2026-10-29_NUANCE-EXPLANATION-PRODUCTION-WIRING-01_USER.md` §2A-5/6・§2C・§2D・§5。設計 `WIRING_DESIGN_01.md`(§5 HR・§6・§7 表示・§9)、`CURRENT_STATE_01.md`、`TEST_PLAN_01.md`、Opusレビュー `OPUS_REVIEW_01.md`(並行02Aが数分内に機械抽出・commit。読めるまで待ち、読めたらM-/R-の該当項目を精読)。**Fable判断: Opus M-1〜M-10・R-1〜R-16をすべて採用。**本Trackの要点:
- 表示(F-6/OK-1): 合成点`er120_part2_wiring_01.compose_page_html`(:507)→`er120_part2_grammar_production_01.compose_study_html`(:1449)に「ニュアンス解説」独立コーナー(採用時のみ)を追加。見出し=「ニュアンス解説」(「Deeper Understanding」不使用、R-12 Fable判断)。**文法0件はコーナー全体非表示**: `ZERO_P2`固定文面(:161,1420,1436)撤去、ブロック数検査「ちょうど1」→「0または1」(:1368、Y:1049、Z:1861)。CSSは「最初の非空ブロックが持つ」へ一般化、3ブロック空なら空文字。R-6: `compose_page_html`のnuanceは既定値なしの必須keyword(`compose_study_html`側のNone既定は残してよい)。
- M-5: `er121_family_y_runner_01.py:1054`の`section.index(PART2_MARKER)`は文法0件でValueError→「存在するブロック同士の相対順」検査へ一般化。同型assertのtest群(`er121_y_highlight_wiring_test_01.py:106-107`、`er121_family_y_runner_01_test_01.py:758-761`、`er019_x_highlight_wiring_test_01.py:371`、`er120_part2_wiring_integration_test_01.py:509`、`er003_kp_general_explanation_01_runner_integration_test_01.py:252,288-289`+再Grep)を是正。
- M-6: 既存0件run(ZERO_P2入り旧md)のページ再構築が`verify_outputs`(er120_part2_wiring:439-442→prod:1370)でPart2Staleになる→0件結果で旧固定文面と完全一致するmdは決定論で`.legacy_zero_p2.md`へ退避(削除しない)してから検証、検証側は「0件=md不在」を要求。
- M-7: ニュアンス節単位の一致検証(`render_html_block(nuance_result)`が当該level節に含まれる/期待件数ADOPTED=1・他=0/`PAGE_FORBIDDEN_RE`をニュアンス本文へ適用)。
- HR(F-5/OK-2/M-3/M-4/R-4/R-5/R-11): 既存`er128.cmd_from_form`(:1390付近)へニュアンス採否を追加、V3フォーム(`user_test/selection_form_v3/` html/js/`form_logic.js`)に「ニュアンス解説」節(1候補・採用/不採用、`shared_terms`/`grammar_conflicts`の警告表示、`FAILED_TECHNICAL`は「候補なし(技術失敗)」と区別表示)、exporter(`docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/tools/export_form_data_01.py`)にnuance追加、照合コード`AIF2`(`nuance_spec`なしはAIF1でバイト不変)、sidecar `confirmed_nuance.json`(文法sidecar直後に書込み、commit点er128:1488不変)、未回答=ISSUE(黙って不採用にしない)。**M-3**: 確定後・候補再利用のbindingは`candidates_sha256`でなく`pool_identity_sha`(candidate_id+used_form/display_phrase/key_phrase+kind)+`text_sha256`+`confirmation_id`(HR提示時の鮮度確認のみcandidates_sha256)。**M-4**: N2(確定時のAPI 0最終確認)は「確定した①②の全idがN1の`against[]`に含まれる」を必須(欠ければISSUE rc=4)、`pool_ids`はexporterと同じ関数で算出。**R-4**: `SUPPRESSED`廃止→ISSUE rc=4(人間の採用を自動で覆さない)。**R-11**: revoke後の再確定時は旧採否を既定表示(明示送信は必須)。**R-1**: `--grammar-pending`との結合(H-13)は外す。
- R-13: R-G3のGrepはProduction moduleに限定、`er120_part2_grammar_production_01_test_01.py:108`のZERO_P2一致assertは削除。
- 既存公開記事(ZERO_P2文面入りHTML 15ファイル)は非遡及で残す(R-14)。
- M-1/M-2(N1挿入位置・N0発行契機)とR-3/R-7(finalize位置・DEPENDENTS)はrunner接続=委任_02C(本Trackでは設計注記のみ、runner本体は編集しない)。

## 2. やること
1. 表示: er120 prod/wiringの変更+表示test(ニュアンス採用/不採用/候補なし × 文法採用/0件の4組合せでHTMLに見出し・空枠・プレースホルダーが無い。X/Y/Z×Std/Advの6経路の合成関数に対するtest)。
2. page_verify一般化(M-5)+M-6退避+M-7節検証+同型assert testの是正。`er121_family_y_runner_01.py`は**:1054付近のみ**を編集(並行(I)がer121:1282付近を編集中の可能性=編集直前Re-Read、差分最小)。
3. HR: er128/exporter/V3フォーム/照合コード/sidecar/N2検査/ISSUE。test(H-1〜H-14相当+M-3/M-4/R-4/R-11: 採用・不採用・未回答ISSUE・AIF1バイト不変・revise後も確定維持・pool外id拒否・被覆欠落ISSUE)。
4. 既存regression(er120/er128/er119/er121/er019/er026 test群)全PASS。合格基準=HEAD失敗ID集合からの新規失敗0。
5. `docs/research/NUANCE-EXPLANATION-PRODUCTION-WIRING-01/TRACK_AC_EVIDENCE_01.md`(変更一覧file:line・test結果・4組合せHTML断片)。ACTIVE_TASK(O)行更新(Re-Read)。commit(編集ファイル明示`git add`)→push。並行02A(er134新module・routing・自身のtest)とは編集ファイルを分ける。index.lock衝突は数秒待って再試行。
6. `docs/pm/RESULT_PACKET_NXW2B.md`(整合/未承認機能/成果物と目的適合/判断候補/費用0/commit、`判定整合:`行)。最終回答は短く(test件数・変更ファイル数・commit・判断候補)。

## 3. 範囲(11-8)
範囲内=承認仕様の実装・Opus修正・承認済み仕様との矛盾の是正(既存assertの一般化)・Regression。範囲外=文法選定方式・HR採否基準の変更、公開記事の変更、Part 4、Family A/B/C、runner接続(02C)。
