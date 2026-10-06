## 管理ID

OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01(委任_07: ラベル統合[Fable突合判定反映]→正式集計A〜E→真の重大見逃し検証→REPORT §81・SSOT・ACTIVE_TASK更新→commit/push。¥0)。並行タスクなし。本委任がgit・SSOT・`docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md`の編集権を持つ。

**作業方式**: `Write`/`Edit`で小分け(1回40行以内)、Bash heredoc不使用。T-0の委任文保存はWriteを3分割して逐語保存。説明は最小限。**コード・prompt・runner・E2E出力(runs/)は変更しない。残り11 runは開始しない。**

## 性質/到達上限Status/禁止事項

- 性質: 9/20 run時点の正式集計と記録。Status: 本管理ID=APPROVED_FOR_PRODUCTION・配線実装済み・9/20 run E2E完了・**PRODUCTION_WIRED未**(20 run完了・ユーザー総合レビュー後)。
- 禁止: PRODUCTION_WIRED宣言/残11 run開始/仕様・prompt・コード変更/ラベルの独自変更(Fable突合判定は下記のとおり適用、他はworkerラベルをそのまま使う)/有料API/`git add -A`・`stash`・`amend`/`ACTIVE_TASK.md`・`RESULT_PACKET*.md`のadd。
- 費用: ¥0。Opus Gate: 非該当。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない。D-1: Grep→該当行範囲Read。G-1: git出力は`--porcelain`/`--short`で最小化。F-1: transcript退避不要。T-1: 事前指定Read/Grep一覧に従う(一覧外は理由を記録)。T-0(2026-09-13、全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ逐語で保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行、結果をRESULT_PACKETへ1行記録(FAILでも継続)。T-2(2026-09-25): TTSなし。T-2追記(7-5): TTSなし。T-3(2026-09-26): ¥0のため適用対象外。

## ユーザー指示(原文、要点)

> 報告で必ず出す数値: A. Checker(AI判定: 候補/真に問題/不要候補化。機械判定: 同。AI＋機械: AIのみ/機械のみ/両方重複/延べ/重複除外後総候補)。B. 後段AI(重大/軽微/問題なし、事後評価: 真に重大/不要に重大/真に重大なのに軽微・問題なし)。後段機械判定[数字のみ](発火/AI判定との重複/真に重大/不要に重大化)。C. Rewrite(発生件数/発生run数/必要/不要/再修正要)。D. Human Review(0件なら明記、発生時は詳細)。E. Safety・Cost(真の重大Fact見逃し/重大Fact検出/run別費用/合計/平均/Rewrite・Checker・後段判定の費用分離)。
> Production Wiring確認: 初回経路だけでなくRewrite後Recheck/retry/fallback/regeneration/最終出口確認でも矛盾がないこと、旧仕様の「数字以外の機械的強制重大化」が後段経路に残っていないこと。CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS等は実態に合わせて更新する。9/20 run時点ではPRODUCTION_WIRED完了扱いにしない。9 run終了後は残り11 runを勝手に開始せず、報告して待つこと。

## KPI provenance欄

全KPI=fresh(新仕様9 run、Production初回path含むE2E=Yes、`er052_output/open233_prod_e2e_02/`)。事後評価ラベル=Sonnet推測(W1/W2/W3、label_source付き)+Fable突合判定(下記、confirmed_by=`fable_2026-10-06`)。ユーザー未確認。旧9 run値=frozen・比較用のみ。

## Fable突合判定(ラベルへ反映、逐語)

1. meta_adv「restored the human concierge feature to the way it had been before」(MUSE-HC-012): Ledger「機能を当面ロールバックした」=撤回。記事は復元=方向反転、gold A5-0型 → `severity_eval=重大`、`true_problem=Y`、`true_critical=Y`、reason「HC-012ロールバック(撤回)を復元と記述=方向反転、A5-0同型」。**最終本文にこの文(または同義)が残っているか、Rewriteされたか、後段AI/S1の判定は何だったかを必ず検証し、残存なら『真の重大Fact見逃し=1』として報告**。
2. meta_std「It said human staff made inappropriate comments about race during calls.」(MUSE-HC-011): Ledger=1従業員が1通話記録内の不適切発言を報告。複数化(comments/calls)+報告元不明 → `重大/Y/Y`維持(従来RCAでも正当BLOCKING)。
3. neg3「On July 13, Trump posted that all cargo ... should provide a 20 percent reimbursement.」(HF-002): Ledgerと一致 → `問題なし/N/N`(W3判定維持。見本Bとの差異を注記)。
4. neg7「the AI on your screen handles everything for you」(MUSE-HC-002、Hook): `軽微/Y/N`(境界、従来RCAでは判断不能)。
5. neg2「They enjoyed the ease of AI.」(cycle1/2): `問題なし/N/N`(Factを含まない修辞)。
6. neg1「A human can handle situations that AI alone finds difficult.」(MUSE-HC-008): **保留→本委任で判定材料を提示**: Ledger MUSE-HC-008とMUSE-HC-002の原文(fixtureから)を逐語で引用し、gold B4-a(HC-002「take over when AI alone has trouble」=BLOCKING)と同型か(Ledgerに「AIが難しい場面を人間が担当する」趣旨の記述があるか)を比較表にしてRESULT_PACKETへ。暫定ラベルは`UNDECIDABLE`のまま(集計では「判断不能」枠)。
7. W1/W3のrewrite_needed仮置き: 集計scriptの実Rewrite対象との突合で確定(Rewrite対象claimのみ、severity_evalが重大/軽微ならY、問題なしならN)。

## 事前指定Read一覧

1. `docs/pm/RESULT_PACKET.md`: L1-L60(委任_05bの結果要約・run別表・引継ぎ)。
2. `er052_output/open233_prod_e2e_02/labels/labels_w1.json`・`labels_w2.json`・`labels_w3.json`: 全文(統合用)。`labels_w*_notes.md`: Grep `重大|UNDECIDABLE|gold` →該当箇所のみ。
3. `er052_output/open233_prod_e2e_02/report/report_abcde.md`: 全文(一次集計、ラベル前)。`watchlist_trace.md`: 全文。
4. `er052_output/open233_prod_e2e_01/aggregate_report_abcde_01.py`: Grep `--labels|def load_labels|claim_key|rewrite_needed|true_critical|safety|--aggregate-json` →ラベルjson形式・keyの一致規則・Safety欄の算出。
5. 判定1の検証: `er052_output/open233_prod_e2e_02/runs/meta_adv*.json`をGrep `restored the human concierge|way it had been before|MUSE-HC-012` →該当claimのStage 1候補有無・再分類verdict・Stage 2 materiality・S1・Rewrite record・最終本文での残存。
6. 判定6の材料: Ledger fixture(`er052_open233_e2e_acceptance_01.py` `prepare_instances()`またはs2c `build_eval_groups()`、Globで特定)をGrep `MUSE-HC-008|MUSE-HC-002` →原文。
7. `OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`: Grep `^## §80` →§80の見出しと末尾(§81追記位置)。
8. `docs/pm/ACTIVE_TASK.md`: 全文。

## 事前指定Grep一覧+追記位置・更新位置の手順

- ラベル統合: 3 jsonを`labels_merged.json`へ統合(key衝突は`|dup`含め保持)、Fable判定1〜5を上書き(`confirmed_by=fable_2026-10-06`)、6はUNDECIDABLE維持。統合後の件数=123を検算。
- 正式集計: `aggregate_report_abcde_01.py --runs-dir er052_output\open233_prod_e2e_02\runs --out-dir er052_output\open233_prod_e2e_02\report_final --labels er052_output\open233_prod_e2e_02\labels\labels_merged.json --aggregate-json er052_output\open233_prod_e2e_02\e2e_summary_02.json`。出力のA〜Eを`report_final/report_abcde.md`で確認し、UNLABELED/MISSINGが残る項目は理由を明記。
- 真の重大見逃し検証: true_critical=Yの全claim(予定3件: B3 gold、neg3 HF-009型、meta_adv HC-012型)について、Stage 1候補→再分類verdict→Stage 2判定→S1→Rewrite→Recheck→最終本文残存の経路表を`report_final/critical_trace.md`に作る。最終本文に残存(未修正)なら「真の重大見逃し」に計上、修正済みなら「重大Fact検出」に計上。
- 旧9 run(frozen)との並記表(A〜E主要値、同instance対比、n=1注記)。
- REPORT §81「OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01: 新仕様9/20 run E2E結果(委任_05b〜07)」を`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`末尾へ4〜5回のEditで追加: (a)provenance・構成(承認構成dump参照)・実行(3並列、技術障害0)、(b)A Checker表、(c)B 後段判定表(AI・数字floor(a)/(c)・S1)、(d)C Rewrite・D Human Review(0件明記)・E Safety/Cost、(e)critical_trace要約・watch list・旧9 run比較・ラベルprovenance(Sonnet推測+Fable突合、ユーザー未確認、UNDECIDABLE 1件の材料)・Production Wiring確認の参照(§80-3)・残存リスク・次(残11 runはユーザー確認待ち)。
- `OPEN_ITEMS.md`: Grep `OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01` →行末尾へ「委任_07(2026-10-06): 正式集計A〜E完了(主要値: Checker候補66[旧151]/floor発火4[旧37]/Rewrite 6件・4 run[旧40件・8 run]/Human Review 0[旧1]/真の重大見逃しN件/重大検出N件/¥31.52[旧¥43.91])、REPORT §81、ラベル=Sonnet推測+Fable突合(ユーザー未確認)。9/20 run時点、PRODUCTION_WIRED未。残11 runはユーザー総合レビュー待ち。」
- `DECISION_LOG.md`: Grep 同ID →エントリ末尾へ「9/20 run結果要約+Fable突合判定1〜6+ユーザー総合レビュー事項(Checker改善の実効/数字のみfloorのSafety/不要Rewrite減/Human Review 0/残11 run可否)」を追記。
- `CURRENT_SPEC.md`: 注記(L2372付近)に「9/20 run E2E完了(2026-10-06、REPORT §81)、PRODUCTION_WIRED未」を追記のみ。
- `docs/pm/REPORT_LEDGER.md`: 末尾1行(委任_04〜07の要約、REPORT §80/§81)。
- `docs/pm/ACTIVE_TASK.md`: 固定ヘッダで上書き(Status: 9/20 run完了・ユーザー総合レビュー待ち[残11 run開始禁止]、UDR-blocking: 残11 run可否・UNDECIDABLE 1件[neg1 HC-008]の確認・重大3件のラベル確認)。

## 実行コマンド全文

1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-06_OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01_07.md --json-out docs\pm\delegation_log\2026-10-06_OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01_07.md_check.json`
2. ラベル統合script(小規模、`er052_output/open233_prod_e2e_02/labels/merge_labels_01.py`)作成→実行→`labels_merged.json`。
3. 正式集計(上記コマンド)。
4. critical_trace作成(run jsonからGrepで抽出、¥0)。
5. REPORT §81・SSOT・ACTIVE_TASK・RESULT_PACKET更新。
6. `git status --porcelain`→明示add→commit→push。

## SSOT追記文

上記のとおり(実測値で埋める)。

## Git

明示add対象のみ: `er052_output/open233_prod_e2e_02/labels/`(labels_w1/2/3.json、notes、merge_labels_01.py、labels_merged.json)、`er052_output/open233_prod_e2e_02/report_final/`、`OPEN_ITEMS.md`、`DECISION_LOG.md`、`CURRENT_SPEC.md`、`docs/pm/REPORT_LEDGER.md`、`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`、`docs/pm/delegation_log/2026-10-06_OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01_06-W1.md`・`_06-W2.md`・`_06-W3.md`・`_07.md`(各+`_check.json`)。`ACTIVE_TASK.md`・`RESULT_PACKET*.md`はaddしない。
コミットメッセージ: `OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01: 新仕様9/20 run E2E正式集計【Checker候補66(旧151)、floor発火4(旧37)、Rewrite 6件/4run(旧40/8)、Human Review 0、真の重大見逃しN、重大検出N、¥31.52(旧¥43.91)】+事後評価ラベル(3 worker+Fable突合)+REPORT §81、PRODUCTION_WIRED未・残11 runはユーザー確認待ち(委任_06/07、¥0)`(実測値で埋める)
SSOT編集権: あり。push前に`git status --porcelain`で混入確認。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET.md`へ(上書き): 1. T-0結果。2. ラベル統合結果(123件、severity分布、Fable判定反映箇所)。3. **A〜Eの正式値(ユーザー指定の全項目、表)**+UNLABELED/MISSING残存項目と理由。4. critical_trace要約(true_critical 3件の経路と最終残存の有無、真の重大見逃し件数・重大検出件数)。5. 判定6(neg1 HC-008)の材料表(Ledger HC-008/HC-002原文、gold B4-a定義、同型か否かの論点)。6. 旧9 run比較表。7. watch list結果。8. Production Wiring確認の参照(§80-3)と9 runで観測した後続経路の動作(Recheck/出口での再分類の実動作、S1 BLOCKING化1件の経路)。9. 残存リスク。10. commit hash・push結果・raw URL。11. 一覧外Read理由。
