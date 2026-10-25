# 委任_09｜JA-ASR-FALSE-NG-ROOT-CAUSE-01 ③ OPEN-517 F1+F2 正式runtime発火証拠(X/Z/Y)+R-5計測実装+Production関数での再現一致確認

## 背景(Fableから。これだけで作業できるように書く)
- 07A(commit `5e50613f5`)で OPEN-517 F1(`READING_MATCH`を`APPROVED_EQUIVALENCE_BASES`から除外・rollback定数`READING_MATCH_FINAL_GATE=True`)+F2(`kana_unify`・期待読み表を`er078_asr_value_guard_01.py`へ移設・M-2弱かな除外+単調guard・M-3境界/最長一致)+OPEN-523(`WEAK_KANA_REGION_COMPAT`)+OPEN-524(`KANA_WORD_BOUNDARY_CHECK`)をProduction(`er078_asr_unified_judge_01.py`/`er078_asr_value_guard_01.py`)へ適用済み。区分=承認済み不具合是正。OPEN-517/523/524はAPPLIED。
- 委任_08(commit `65102859a`)で②B-light βのOpus反映・再評価完了(Production変更0)。同報告の「次委任案(b)」=『07A commit後に、Production関数での`base+F1F2`再現一致確認とR-5計測実装』を本委任で行う。R-5計測仕様は `docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/R5_MEASUREMENT_SPEC_01.md`。初回run集計scriptは `docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/open517_first_run_tally_01.py`(07A作成、R-3)。
- ユーザー指示(2026-10-25「日本語ASR誤PASS是正｜XYZ共通Production正式採用・Wiring完了」、逐語 `docs/pm/delegation_log/2026-10-25_JA-ASR-FALSE-NG-ROOT-CAUSE-01_USER_02.md` を必ず読む)の必須条件: 正式初回経路配線 / retry・Local Rewrite・再利用等との整合 / **正式runtimeでF1+F2が発火した証拠** / Regression / model_id・routing証拠 / HR Lock整合 / SSOT / 追補L65不整合解消 / Git / Fable受入。「Family Yで正式runtime確認が立ち上げ作業の進捗に依存する場合は、コード配線完了とruntime未確認を区別しOPEN_ITEMSで追跡。X/Zの完了をYの待機で不合理に遅らせない」。
- Status定義: PRODUCTION_WIRED判定はFableが行う。あなたはFamily別に「コード配線完了/runtime発火証拠あり・なし」を事実で報告する。

## 並行agentとの衝突回避(厳守)
- 現在並行中: (A) KP HR/Part 2 evidence R1〜R4実走(X/Zの正式runner実走。er019/er026/er062/er119/er120系ファイルと、その出力run dirを所有)、(B) Family Y 委任_06(er121系ファイル・`er121_output/family_y_production_01/redelivery_fee/`を所有)。
- 本委任で**編集してよいファイル**: `er078_asr_unified_judge_01.py`・`er078_asr_value_guard_01.py`・`er007_ja_secondary_asr_01.py`(R-5計測ログの追加に限る)、`docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/`配下の新規/既存ファイル、`OPEN_ITEMS.md`(OPEN-517の最小追記・直前再Read・最小Edit・バックアップ)、`DECISION_LOG.md`/`CURRENT_SPEC.md`(必要最小。直前再Read)、`docs/pm/RESULT_PACKET_JAASR9.md`、`docs/pm/delegation_log/`。
- **編集禁止**: er019/er026/er062/er119/er120/er121系、他agentのrun dir。他agentのrun dirは**読取専用**で参照してよい(集計・証拠抽出)。
- er078/er007への変更は**判定結果を一切変えないログ/計測の追加のみ**(判定分岐・閾値・受理クラスの変更禁止)。変更前後で `er078_asr_value_guard_kana_unify_test_01.py`(44)+既存er078/er007 testが同じ結果であること、07Aの `eval_open517_api0_prod_01.py` 等の判定出力が完全一致することを示す。
- 同一run dirへの同時書込を避けるため、自分の有料runは専用dir(例 `er078_output/open517_runtime_evidence_01/`。既存命名規約に合わせてよい)に閉じる。

## やること
### 1. Production関数でのbase+F1F2再現一致確認(API 0)
- 委任_08は07A未commit時点のスナップショット(pin `89b630bd1`+proto v4)で基準を作った(`prod07a_committed_at_eval=false`)。現在のHEAD Production関数で、同じ入力集合(月題12転写・N系負例・正常143件など07A/08が使った凍結データ)を再判定し、委任_08の`base+F1F2`列および07Aのproto v4結果と**完全一致**するか確認。差分があれば原因を特定し報告(Production側の不具合なら是正、評価側の前提差なら記録)。
- 出力: `docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/OPEN517_PROD_PARITY_01.md`(+json)。

### 2. R-5計測の実装(Production、ログ追加のみ)
- `R5_MEASUREMENT_SPEC_01.md`に従い、正式judge経路で以下を**判定を変えずに**記録する: F1により最終受理を拒否した事例(READING_MATCHのみ一致→NG/DEMOTE)、F2(kana_unify)が有効化/適用された事例とその正規化前後、期待読み表に無い読みによるDEMOTE事例、OPEN-523/524の発火、Secondary(S)転写の保存(仕様にある場合)。既存のaudit/jsonl(例: `human_review_queue.jsonl`・judge結果json)への追加フィールドで実現し、新規の外部依存を増やさない。フィールド名は仕様書の名称に合わせる。
- 07A報告の開示リスク「期待読み表にない正しい読みのDEMOTEが1 runで3件超ならFableへ即報告」を集計できるよう、`open517_first_run_tally_01.py`が新ログを読めることを確認(必要なら最小改修)。
- 仕様書に実装上の不明点があれば、推測で機能を広げず、最小解釈で実装し不明点を報告に列挙。

### 3. 正式runtime発火証拠(X/Z/Y)
- 「発火証拠」の定義(Fable固定): 正式Production経路(各Familyのrunner→er020/er078 judge)で生成されたrun artifact(judge結果json/jsonl・log)に、(a)HEADが`5e50613f5`以降のコードで動いたことを示す証拠(process起動時刻がcommit時刻以降、またはログ内の定数/フィールドの存在、例: `kana_unify`関連info、`READING_MATCH_FINAL_GATE`の記録)と、(b)F1またはF2の経路が実際に評価された記録(F2正規化が適用された比較、または READING_MATCH一致がbase受理に使われなかった記録)があること。発火「0件」(経路は通ったが該当事例が無い)も、経路通過の証拠があれば「経路通過証拠あり・発火事例0」として区別して報告する。
- 手順:
  (i) まず並行agent(A)(B)の既存run dir(読取専用)から、commit `5e50613f5`以降に起動したrunのjudge artifactを探し、上記(a)(b)を集計。X/Zは(A)のR1〜R4、Yは`er121_output/family_y_production_01/`配下。各runの起動時刻(ログ/manifest)とcommit時刻を比較して、旧コードで走ったものは証拠に数えない。
  (ii) (i)で X または Z の証拠が得られない場合のみ、小規模な日本語segment再生成(1〜2 segment、日本語ASR判定を通る正式経路。可能なら既存の正式retry/regen入口を使い、runner全体を回さない)を専用dirで実施。**上限20円**(起動前に `py docs/pm/tools/daily_dev_cost_01.py` で当日累計を確認し、表示値+94.28円(ツールが拾わない`raw_usage_log_high.jsonl`分)を実累計とする。実累計+見積が1,480円を超えるなら有料runをせず報告)。有料run=`.venv\Scripts\python.exe`。起動前に `py tools/stop_scope_check_01.py --managed-id JA-ASR-FALSE-NG-ROOT-CAUSE-01 --run-dir <dir> --out <dir>/stop_check_09.json`(rc=3なら起動しない)。起動間隔150秒以上、同一run 5分3回禁止。HR Lockに当たっても`approved_by="user"`は付けない(Lockは事実として報告)。
  (iii) Yは委任_06が進行中のため、自分で有料runを起動しない。(i)で得られなければ「コード配線完了・runtime未確認」としてOPEN-517に追跡行を追記。
- model_id/routing証拠: judge artifact内のASR model名(Primary/Secondary)と、`er006_model_routing_contract_01.py`の該当routingを照合して記録。
- 出力: `docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/OPEN517_RUNTIME_EVIDENCE_01.md`(Family別表: run dir / 起動時刻 / HEAD証拠 / F1評価件数 / F2適用件数 / 523・524発火 / DEMOTE件数 / NG化件数 / model_id / HR Lock有無 / 判定: 証拠あり|経路通過のみ|未確認)。

### 4. Regression
- 遮断harness(`netblock_harness_01/sitecustomize.py`)下で、er078/er007/er020関連の既存test+kana_unify test 44+`eval_open517_api0_prod_01.py`を実行。結果数を報告(無関係の既知FAILは07A報告の13件と突合)。

### 5. SSOT・Git
- OPEN-517へ: 再現一致確認結果・R-5実装commit・Family別runtime証拠状況(Yは未確認なら追跡行)を最小追記。新規OPEN採番は原則しない(必要なら11-8分類を付ける)。
- CURRENT_SPEC/DECISION_LOGは、R-5計測フィールドの追加が仕様上の記録対象になる場合のみ最小追記(07AがCURRENT_SPEC L2855直後に追加した行の近傍)。
- Git: 禁止=`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・`git checkout -- <file>`。commitは対象pathのみ(`git commit --only <paths>`。共有ファイル(OPEN_ITEMS/DECISION_LOG/CURRENT_SPEC)に他agentの未commit差分が混ざる可能性があるため、その場合は一時index+commit-tree方式で自分のhunkのみ)。`git push origin HEAD:main`(non-fast-forwardなら fetch→`git merge --no-edit origin/main`→push、競合は両方残しSTOP報告)。secret grep 0件確認。wav/raw_usage_log/STOP/lockは追跡しない。作業ブランチ`work/post-merge-01`。
- 委任文の逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-25_JA-ASR-FALSE-NG-ROOT-CAUSE-01_DELEGATION_09.md`(`--index -1`不可。直近の既知indexは598(委任_08)。599以降を順に試し、先頭行が「# 委任_09｜JA-ASR-FALSE-NG-ROOT-CAUSE-01」である出力を採用。一致しないものは保存しない)。

## 報告(`docs/pm/RESULT_PACKET_JAASR9.md`へ書き、同内容を最終報告で返す)
1. 再現一致確認の結果(一致/差分と原因)
2. R-5計測の実装内容(フィールド一覧・判定不変の証拠・test結果)
3. Family別runtime証拠表(X/Z/Y)と、Fable向けの事実ベースStatus候補(コード配線完了+runtime証拠あり / 経路通過のみ / 未確認)
4. 有料run実施有無・実費・当日累計(94.28円加算後)
5. Regression結果
6. SSOT・commit sha・raw URL一覧
7. RESULT_PACKET 4行(既存仕様整合/未承認機能の既定値/失敗終了時の最終成果物/撤去・残置)+判定整合行
8. 未解決・判断候補(27-3分類。ユーザー判断が要るものだけ、推奨付き)
報告は事実と推測を分け、「PRODUCTION_WIRED」という語を自分の判定として使わない。