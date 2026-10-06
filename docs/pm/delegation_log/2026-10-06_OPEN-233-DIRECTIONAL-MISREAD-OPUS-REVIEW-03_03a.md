# 委任_03a 逐語保存(OPEN-233-DIRECTIONAL-MISREAD-OPUS-REVIEW-03)

## 管理ID
OPEN-233-DIRECTIONAL-MISREAD-OPUS-REVIEW-03(委任_03a: Opusレビュー結果・Fable照合のSSOT反映)。並列委任_03b/03c/03dが`docs/pm/opus_l2_review_or03_part*.md`を作成中(触れない)。書込先: `OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`(§85-4/5)、`DECISION_LOG.md`((c))、`docs/pm/OPUS_FINDINGS_LEDGER.md`(OF-058)、`OPEN_ITEMS.md`(進捗)、`docs/pm/ACTIVE_TASK.md`、`docs/pm/RESULT_PACKET_OR03_03A.md`、`docs/pm/delegation_log/`。git操作なし。
作業方式: Edit 1回30行以内、Bash heredoc不使用、説明最小。T-0はWrite+Edit追記で逐語保存。時間目安15分。

## 性質/到達上限Status/禁止事項
性質: SSOT記録(¥0)。Status: OPUS-REVIEW-03=USER_DECISION_REQUIRED(Fable判定)。禁止: TRIAL-03実行/Prompt修正の本実装/Production変更/gold・KPI変更/新Safety仕様の採用/有料API/Fable判定の変更/「決定」の創作。Opus Gate: 実施済み。

## 固定ブロック
E-1: 同一ファイル再読禁止。D-1: Grep→範囲Read。G-1: git出力不使用。F-1: 退避不要。T-0(常時有効): 委任文を本ファイルへ逐語保存しcheck_delegation_prompt.py実行、結果1行をRESULT_PACKETへ。T-1: 事前指定一覧に従う。T-2/T-2追記(7-5): TTSなし。T-3: 対象外(¥0)。

## ユーザー指示(原文、要点)
> Opusレビュー結果を受け取った時点でSTOPし、ユーザーへ報告する。TRIAL-03は開始しない。Status上限DESIGN_READY_FOR_REVIEW/USER_DECISION_REQUIRED。Opusが良いと言っても自動的にVALIDATED/APPROVED_FOR_PRODUCTIONにしない。

## 記録する事実
E1 Evidence(¥0、3 packet `docs/pm/evidence_opus_review_03/01_d61_trace.md`/`02_hc012_a5_fp3.md`/`03_trial01_02_diff.md`)【確認】: D61(G-03)記事文 "After the plan was withdrawn, oil prices fell."(Brent・上げ幅語なし)。現行Ledger側ラベルは既に「Brent先物の上げ幅/水準/価格水準/価格」と実体名入り(実体名が欠けるのは「機能」のみ)。同系ラベルはG-04等で選択できた。TRIAL-01の事象ごと個別判定ではG-03 rep2/3検出、TRIAL-02の単一選択で0/3(3回ともNONE、quoteは記事文を引用)。前後文(article_context)は未投入。Ledger側サンプル揺れあり(HF-009 rep間で2〜3 event)。01→02で変化したid 17件、01検出→02見逃し=G-03・S-06、01誤爆→02解消=F-09/F-10/F-19。
O1 Opus最終判定: (B)設計修正後にTrial。ただし修正内容は現修正案(実体名付与+意味上の部分一致)ではなく別のもの。現修正案=局所patch(しかもD61に効く根拠のない誤診に基づく)。
O2 主因: 1 factに逆向き2事象(暫定: 上げ幅DECREASED/最終: 水準INCREASED)がある状況で、NONE付き単一選択方式が暫定と最終を区別できない。副因: 上位語("oil prices")の対応付けが弱い/前後文未投入/Ledger側ラベルの重複・揺れ。D61の性質=「暫定の下落を結末として述べ高値復帰を落とした時間範囲誤り」で、現enumにこの次元がないためF-09型(暫定の下落を正しく述べた文)と原理的に区別不能。
O3 現修正案の見込み: (a)D61を拾う可能性低(部分一致はSAMEになる「上げ幅」へ吸い寄せ、見逃し→黙って通過に変わるだけ) (b)HC-012/A5-0は壊さないが「機能」具体化はG-02の手掛かりを減らす (c)F-19で「テスト」選択→REVERSED再発経路あり (d)上位語・主語省略(S-01〜05/S-14/N-02)の見逃しが固定。6観点すべてで盲点が残るか悪化。
O4 推奨修正: 修正1(主)=事象に時間位置phase∈{INTERIM,FINAL,SINGLE}を付与、記事側も{INTERIM,FINAL,UNSPECIFIED}を返し、Pythonで「FINAL/UNSPECIFIED↔FINAL/SINGLE」「INTERIM↔INTERIM」で照合。修正2(副)=fact対応付け済み文で単一選択がNONEのとき、TRIAL-01方式の事象ごと個別判定へフォールバック(phase照合併用)。構造上直すべき点: 時間位置次元の欠如/NONE=通過の安全側設計欠如/SAME優先ルール(compare_selected L62)/Ledger側揺れの固定+ラベル正規化/上位語の別名付与(別Trial)/前後文投入(別Trial)/D61型を「時間範囲誤り」として別カテゴリ明示(gold/KPI定義=ユーザー判断)。
O5 TRIAL-03案(Opus): Ledger側phase付き再抽出1回固定(約30 call、¥0.5)、記事側2構成並列(X=修正2のみ/Y=修正1+2)×(63+held-out約10項目)約220 call ¥4.5、フォールバック約50 call ¥1、合計約¥6・上限案¥8、shard並列約10分。held-out約10項目(gold反転4・faithful 6)を実行前に固定(D61過学習防止)。合格基準案7項目: HC-012・A5-0 3/3維持/D61>=2/3/held-out gold平均>=2/3かつ全件>=1/3/faithful誤重大0件/UNCLEAR<=10/不要Rewrite見込み0/新たな重大見逃し0。
F1 Fable照合: Opus判定はEvidenceと整合。Fable/Sonnetの仮説は誤診(ラベル既に具体的)。Opus推奨は既承認設計(案E')の骨格を維持しつつ新次元(phase)を追加するもので、D61型のカテゴリ再定義(gold/KPI定義に関わる)を含むため、11-3節STOP条件(新しい仕様採用・gold定義の扱い)該当→USER_DECISION_REQUIRED。ユーザー指示によりTRIAL-03は未開始。残11 run待機。Production変更なし。本管理ID費用¥0。Opusレビュー逐語は`docs/pm/opus_l2_review_or03_d61_root_cause.md`(別委任で作成)。
F2 ユーザー判断事項(Opus提示7点、Fable推奨付き): (1)現修正案を採らない=推奨採らない (2)TRIAL-03の修正内容を構成X/Yへ差し替え=推奨差し替え (3)予算上限¥8=推奨 (4)held-out固定=推奨固定 (5)D61型を「時間範囲誤り」として別カテゴリ=推奨明示(gold/KPI定義変更のためユーザー判断) (6)「限定語なしの方向主張は結末の主張とみなす」方針=推奨受け入れ(held-out faithfulで誤爆測定) (7)上位語別名・前後文は別Trial=推奨別Trial。追加: (8)残11 E2E再開=Fable推奨はTRIAL-03結果まで待機。

## 作業内容
1. REPORT: Grep `§85-4|§85-5|委任_03で追記` →§85-4をE1・O1〜O5、§85-5をF1・F2で置換。
2. DECISION_LOG: Grep `OPEN-233-DIRECTIONAL-MISREAD-OPUS-REVIEW-03` →(c)をO1・O2要点・F1・F2で置換。「決定したのはFableのStatus判定のみ」明記。
3. OPUS_FINDINGS_LEDGER: Grep `OF-057` →直後にOF-058を既存書式で追加。
4. OPEN_ITEMS: Grep `OPEN-233-DIRECTIONAL-MISREAD` →該当行進捗へ「OPUS-REVIEW-03完了(¥0): Opus判定(B)、現修正案は誤診の局所patch、主因=暫定/最終の未区別、推奨=phase次元+NONEフォールバック、USER_DECISION_REQUIRED(判断8点)、TRIAL-03未開始」を短く追記。
5. ACTIVE_TASK 全面更新: OPUS-REVIEW-03=USER_DECISION_REQUIRED、UDR-blocking=判断8点+残11 run、UDR-deferred=U2/U3/STAGE4、OPEN-235/236未着手、9-8自己確認欄。
6. `docs/pm/RESULT_PACKET_OR03_03A.md`: 追記位置(行)、T-0結果。

## 事前指定Read一覧
`docs/pm/ACTIVE_TASK.md` 全文。

## 事前指定Grep一覧+追記位置・更新位置の手順
上記1〜4のGrep→該当範囲Read(各30行以内)→Edit。全文Read禁止。

## 実行コマンド全文
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-OPUS-REVIEW-03_03a.md --json-out docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-OPUS-REVIEW-03_03a.md_check.json`

## SSOT追記文
上記1〜4。

## Git
なし(委任_03eでcommit)。

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_OR03_03A.md`。最終報告4行以内。
