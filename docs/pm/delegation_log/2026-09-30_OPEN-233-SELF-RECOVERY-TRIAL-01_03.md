管理ID: OPEN-233-SELF-RECOVERY-TRIAL-01(委任_03: opus-consultant model 更新+Stage 1 設計再検証+Self-Recovery 案修正+claim 単位正解ラベル整理。**API 呼び出しなし・¥0・Production 非接続・実装なし**)
日付: 2026-09-30。作業ディレクトリ C:\Users\tensh\eigo-radio。

## 0. 前提
- docs/pm/PM_BRIEF.md 固定ヘッダ、docs/pm/PM_GOVERNANCE.md 8節(削除・移動・rm・stash・git add -A・履歴書換 禁止)。
- 対象: docs/pm/design_open233_self_recovery_flow_01.md(§1〜§13)、OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md、docs/pm/opus_l2_review_open233_checker_trial_01.md(前 Phase Opus 所見)、docs/pm/design_open233_checker_redesign_trial_01.md(§2 gold 表・§2-補 claim 単位候補表・§4-補)、OPEN-233-CHECKER-REDESIGN-TRIAL-01_REPORT.md §9〜§12(Trial 1/2/n=20 実測)、er051_open233_checker_trial_variant_01.py(V4-A)、docs/pm/negative_claim_candidates_open233_01.md。
- 一時ファイル: docs/pm/ACTIVE_TASK_C233G.md / docs/pm/RESULT_PACKET_C233G.md(新規、commit 禁止)。既存 *_C233A〜F は削除・移動しない。

## 1. ユーザー意図(2026-09-30 再明確化、逐語要旨。DECISION_LOG へ 1 エントリで記録)
- 最終ゴール: 通常 Production 運用で Ledger/Deviation Check 起因の USER_DECISION_REQUIRED を実質ゼロ。10〜20 記事規模 Production 相当 Trial で同時達成: Ledger/Deviation 起因ユーザー確認 0 件/重大 Fact 見逃し 0 件/追加量産コスト +¥3/記事以内(使い切る前提ではなく可能な限り安く)/Human Review を通常運用にしない。初回 Checker 単体の誤 BLOCK 率は最終 KPI ではない。
- Self-Recovery 構成(Initial Check → 必要時だけ再スクリーニング → 必要時だけ Rewrite → Recheck → 解決不能な例外だけ Escalation)は固定仕様ではない。KPI をより安全・安価・安定に満たせる設計があれば改善してよい。
- **Stage 1 再考**: 現行 Production Checker には changed_actor 等の重大 Fact 見逃し/severity 不安定/category 検出揺れ/A-1 時制 drift 見逃しが確認済み。「なぜ Stage 1 を現行 Checker のまま使う設計が最適か」を再検討。現行のままでも Self-Recovery 全体で 見逃し 0/Escalation 0/+¥3 以内 を満たせる合理的根拠があればそれでよい。Stage 1 改善が KPI 達成に有利なら Trial 専用改善 variant を使ってよい。**Stage 1 の実装方法をユーザーに逐一確認しない。KPI 達成優先**。Production 正式 path は変更禁止。
- 確定済み Trial 前提: Stage 2 materiality 判定 Trial 実施可/QUALITY は通過可能という思想/actor・number・negation・comparison の重大見逃し対策 Trial/Family X 限定 variant/Hormuz B2 は Trial 上 QUALITY/Trial 上の正解ラベル整理は実施可/QUALITY ログ・Human Review 運用詳細は Trial 後へ defer/対象モデル GPT-6 Luna/Sol 保留/Astra 対象外。
- 用語: 「gold」ではなく **「Trial 上の正解」「正解ラベル」**を使う。B1=生活へのブリッジ文(許容 claim と修正すべき claim が混在)/B2=Hormuz 因果境界(正解 QUALITY)/B3=`so` 等で元 Fact にない因果を付与(正解 BLOCKING)/B4=一般化(許容と BLOCKING が混在)。**claim 単位で評価**。
- KPI 固定: Primary=10〜20 記事 Trial で Ledger/Deviation 起因 USER_DECISION_REQUIRED 0 件/Safety=重大 Fact 見逃し 0/Cost=追加継続コスト ≤ +¥3/記事。各 Trial で 固定追加費/条件付き追加費/Stage 2 費用/Rewrite 費用/Recheck 費用/1 記事平均/worst case/P50/P95 を追跡。+¥3 超が必要と判断した時点で早めに報告。
- 改善ループ継続(1 回で終了しない、同方式の漫然反復禁止、改善しなければ原因分析し別方式へ)。Phase 予算 ¥400。
- Opus L2 は **`claude-opus-5-5`** を使用。実行前に probe(利用可否/actual model_id/runtime 上の実モデル)し報告に runtime evidence を残す。5.5 が利用不能な場合のみ STOP せず、利用可能な最新 Opus の actual model_id と差分を中間報告。批判的レビュー対象: Self-Recovery 全体設計/Stage 1 設計/Second Judge/Rewrite 戦略/Safety/Cost/loop 化リスク/Escalation ゼロの現実性。
- 中間報告は原則「進捗と方向性確認のため」。Guardrail(KPI・Safety・Cap・Production 非変更)内では Trial 専用 Prompt/schema variant/deterministic rule/Second Judge/Rewrite 方法/regression fixture/retry 構造を自律的に改善。細かい実装判断を逐一 USER_DECISION_REQUIRED にしない。
- USER_DECISION_REQUIRED で止める条件(原則これのみ): KPI 自体の変更/重大 Fact Safety の緩和/+¥3 Cap 超過が必要/Production 正式採用・配線/Family X 以外への正式展開/新 Product 原則/予算 ¥400 超過。
- Checkpoint A(再設計+Opus 5.5 レビュー完了時)/B(最初の実 Trial 終了時)/C(大きな設計変更を伴う次 Trial 前)/D(累計 ¥100/¥200/¥300 に近づいた時)/E(10〜20 記事 Trial 前)。必須内容: 現在 best variant/重大 Fact 見逃し/Initial BLOCK 件数/Re-screening 解消件数/Rewrite 解消件数/Final STOP 件数/USER_DECISION_REQUIRED 件数/追加コスト/記事/latency/前回からの改善/次に試すこと/Phase 累計費用・残予算。中心テーマ「Production で人間へ上げず、安全に自動完結できそうか」。
- Production Prompt/schema/Validator/routing/runnerは変更しない。目標達成後 `VALIDATED` で STOP しユーザーへ正式採用判断を求める。

## 2. 作業 A: opus-consultant の model 更新
- `.claude/agents/opus-consultant.md` の frontmatter `model: opus` を `model: claude-opus-5-5` に変更(この 1 行のみ。本文は変更しない)。変更前後の diff を REPORT に記録。
- 注: 実際の利用可否は Fable が起動 probe で確認する(本委任では検証しない)。

## 3. 作業 B: Stage 1 設計の再検証(設計書 §3 の改訂+新設 §14「Stage 1 設計判断」)
既存 Evidence のみで(API 呼び出しなし)、以下の選択肢を KPI(見逃し 0/Escalation 0/Cap)で比較し、**Fable/Claude 側で結論を出す**(ユーザー確認は求めない):
- S1-A: 現行 Production Checker(Prompt/schema 不変、モデルは Trial では gpt-6-luna)。
- S1-B: Trial 専用改善 variant V4-A(category 境界明確化+schema variant+post-hoc 昇格のみ)。changed_actor 5/5、重大群 12/12、B 群 2/4、call 単価 +30%、latency +60%。
- S1-C: V4-A+一般常識許容規定の具体化(前 Phase C2 相当、現行 Prompt L527-528 の適用明確化。未実測)。
- S1-D: その他(例: Stage 1 に materiality を直接出させて Stage 2 を省く一体型。前 Phase Opus は「detect と materiality の分離」を推奨、理由: Safety 資産保存。これとの整合を論じる)。
比較軸: (1) 重大 Fact 見逃し(重大群/changed_actor/実データ recall n=20 の実測値、A-1 時制 drift のような検出漏れ型を Stage 2 以降で救えるか=**Stage 1 が検出しなければ Stage 2/3 は発火しない**という構造的事実を明記)、(2) Initial BLOCK 率→Stage 2/3 発動率→条件付きコスト(§13 モデルへ代入)、(3) 非決定性(検出/非検出の揺れ)への耐性、(4) Production 採用時の変更範囲(S1-B/C は Production Prompt 変更を伴うが、Trial では可)。
結論として **Stage 1 の Trial 採用案を 1 つ確定**し、根拠と残リスクを書く。「現行のまま」を選ぶ場合はその合理的根拠、変える場合は Trial variant 名と差分の sha256 を明記。
併せて、**検出漏れ型 Safety 対策**(Stage 1 recall 85〜100%)について、Cap 内で可能な選択肢(例: deterministic pre-check[数値・固有名詞・日付の機械照合、¥0]/BLOCK 時ではなく PASS 時の限定 2nd run は固定費になるため原則不採用/など)を検討し、採否と理由を書く。

## 4. 作業 C: claim 単位「Trial 上の正解ラベル」表の確定(設計書 §7 改訂)
- 用語を全面的に「Trial 上の正解ラベル」へ統一(設計書・REPORT の本 Phase 文書内。前 Phase 文書は変更しない)。
- B1〜B4 を claim 単位で表にし、前 Phase Opus 論点 2 の評価表と、ユーザー確定事項(B2=QUALITY、B3=BLOCKING、B1/B4=混在)を統合して **確定ラベル**を付ける(B1-a/b=ACCEPTABLE、B1-c=BLOCKING、B2=QUALITY、B3=BLOCKING、B4-a=BLOCKING、B4-b/c=ACCEPTABLE〜QUALITY[Trial では QUALITY 扱い]、B4-d=QUALITY〜BLOCKING[Trial では BLOCKING 扱い=fail-closed 側])。fail-closed 側に倒した箇所は明記。
- 各 fixture の**期待到達経路**(例: B2=S1 BLOCK→S2 QUALITY→PASS、B3=S1 BLOCK→S2 BLOCKING→S3 Rewrite→Recheck PASS、重大群=S1 BLOCK→S2 BLOCKING[降格不可]→S3 Rewrite→PASS、negative 16 件=S1 PASS または S2 ACCEPTABLE/QUALITY)を表にし、Phase 1 Trial の評価基準にする。
- 「Trial 上の正解ラベルの整理はユーザー承認済み。KPI/Safety の意味は変えていない」と明記。

## 5. 作業 D: Self-Recovery 案の修正点反映
- §3 Stage 1 を作業 B の結論で更新。§13 コストモデルを Stage 1 の選択(単価・発動率)で再計算(楽観/中央/悲観、worst、Cap 余裕)。
- Stage 2 入力設計(記事全文 vs 縮小)を確定(前委任で未確定)。Fable 案: 対象 claim を含む段落±1+Ledger 全文+Stage 1 deviation 出力(全文は渡さない)。fail-closed の観点で不足する場合の条件も書く。
- §11 Opus 論点をユーザー指定 8 項目(Self-Recovery 全体/Stage 1/Second Judge/Rewrite/Safety/Cost/loop 化/Escalation ゼロの現実性)に整理し、各論点に本設計の暫定答えと「批判してほしい点」を添える。
- §12 を「USER_DECISION_REQUIRED 条件(ユーザー指定 7 項目)」に置き換え、それ以外は自律改善範囲と明記。Checkpoint A の報告項目(§13 必須 12 項目+コスト内訳)を更新。

## 6. 記録・Git
- REPORT §3「Stage 1 再検証・設計修正(委任_03)」追記(費用 ¥0/累計 ¥0/残 ¥400)。
- SSOT(最小限、1 agent のみ): DECISION_LOG.md に §1 ユーザー意図+Stage 1 結論+正解ラベル確定を 1 エントリ。OPEN_ITEMS.md OPEN-233 行に「Stage 1 案確定、Opus 5.5 指定、Checkpoint A 前」を追記。CURRENT_SPEC.md 不変。
- delegation_log: docs/pm/delegation_log/2026-09-30_OPEN-233-SELF-RECOVERY-TRIAL-01_03.md+check script(FAIL 既知・non-blocking)。
- commit: `.claude/agents/opus-consultant.md` を含め、変更ファイルをパス指定 git add(-A 禁止)、Management-ID trailer、ACTIVE_TASK*/RESULT_PACKET*/.env は add しない。競合時 git merge origin/main のみ。
- 事後確認: git diff --stat で Production ファイル(er003_*/er006_*/er012_*/er019_*)無変更。
- 報告(RESULT_PACKET_C233G.md と handback、簡潔に): 【opus-consultant 変更 diff】【Stage 1 結論と根拠(選択肢比較表の要約)】【検出漏れ型 Safety 対策の採否】【claim 単位正解ラベル表(要約)と期待到達経路】【Stage 2 入力設計の確定】【再計算後の追加コスト/記事(固定/条件付き/P50/P95/worst/Cap 余裕)】【Opus 論点 8 項目と暫定答え】【USER_DECISION_REQUIRED 該当有無(ユーザー指定 7 条件)】【費用 ¥0/累計 ¥0/残 ¥400】【Git(hash・raw URL)】【Status=DESIGN_READY_FOR_OPUS_L2】。

## 7. 実行結果メモ(委任_03実施記録、Sonnet追記)
- 作業A: `.claude/agents/opus-consultant.md` L5 `model: opus` → `model: claude-opus-5-5` に変更(1行のみ)。
- 作業B: 選択肢S1-A/B/C/Dを4軸で比較し、S1-B(Trial variant V4-A)を採用確定。理由・残リスクは設計書§14に記載。検出漏れ型Safety対策としてdeterministic pre-check(¥0)を採用、PASS時限定2nd runは不採用。
- 作業C: claim単位確定ラベル表(§7-0)を新設、B1-a/b=ACCEPTABLE、B1-c=BLOCKING、B2=QUALITY、B3=BLOCKING、B4-a=BLOCKING、B4-b/c=QUALITY扱い、B4-d=BLOCKING扱い(fail-closed)。期待到達経路を§7-1〜7-6に整理。
- 作業D: §3-1/§4-4/§11/§12/§13を改訂・再計算。worst caseがCap超過(¥3.96/記事、概算発生率約1%)という新規知見を§13-6/§13-7/§13-10/§14-3に明記。
- 実行コマンド全文: 本委任はAPI呼び出し・シェルコマンド実行を伴わない設計書編集作業のみ(Read/Edit/Bashのgrep等の調査コマンドのみ使用、Production/Trial実行コマンドは実行していない)。
