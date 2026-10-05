# 委任_05 委任文(全文保存、2026-10-05)

## 管理ID

`OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01`(委任_05、ループ1「Fable評価」段)。**並行タスクあり**: 委任_06(Trial runner `er052_open233_self_recovery_flow_runner_01.py`・テスト・新規prompt module `er052_open233_stage1_*`を実装)。本委任はそれらのコードに触れない。gitは自分のファイルのみ明示add(index.lockは10秒待ち最大3回再試行)。

## 性質/禁止事項

- 性質: ¥0。(a)Opus#16全文の保存(モデルが本文を再出力せず、`docs/pm/tools/extract_agent_text_from_transcript_01.py`でFableセッション記録から抽出: transcript=`C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\f9ae115b-0305-437d-ac2d-b452b22a5e2a.jsonl`、start-marker=`# Opus独立技術レビュー#16(条件A+ユーザー指示による必須、条件B相当)`、end-marker=`rep30実行時のS1・CAUSAL_FLOOR等のスイッチの実際の値(RCAでも未精査と記載)。`、out=`docs/pm/opus_l2_review_open233_stage1_redesign_16.md`、ヘッダ4行、行頭2スペースのインデント除去)、(b)Fable評価の記録、(c)Opus指摘台帳へ#16のH1〜H4・1-a〜1-cを登録、(d)委任_03の未commit成果物(`docs/pm/design_open233_stage1_redesign_01.md`、`docs/pm/opus_packet_open233_stage1_redesign_01.md`、`er052_output/open233_kpi_recovery_02_offline_01/stage1_redesign_offline_eval_01.*`、委任_03ログ+check.json)のcommit、(e)Opus¥0事前作業1・5の実施。

## Fable評価(Opus#16、逐語記録)

1. 条件B判定「根本設計の問題」を採用。Opusが追加確認した1-a(neg5は文をまたぐ因果「. So」の問題で、文単位分割は悪化させうる)・1-b(Stage 1 promptの「迷えば許容」「MAJORのみ後段へ」「flag全falseはMINOR降格」が再現率を下げる)・1-c(HF-011は正式`SAFETY_CRITICAL_CLAIM_DEFS`に含まれず、設計書の「gold 7」は不整合)を事実として採用。
2. **ループ1の構成**: Sonnet案(3'単独)ではなくOpus修正案を採用 — **3'-R(文ID網羅+関係単位ID[文頭因果・照応語で直前文と組]+OKには`support_fact_ids`と逐語引用必須で機械検査+同一文の判定一致検査+「迷えば候補」へ判定方針を移動し重大度判定はStage 2の責務)+5-lite(Ledger fact→記事方向の逆照合、同じ単位IDを使う1 call)の2経路∪+F3配線(precheck/floorを非検出時も実行)+H1是正(Stage 1 API失敗がPASSへ抜けるfail-openを、再実行→なお失敗ならSTOPへ)+決定論検査(OK判定の単位で数値範囲外・因果語ありで引用factに因果記述なし・否定極性不一致・同文で判定不一致→候補へ戻す。主体名照合は対象外)**。案6はループ2で判断。ループ1では2経路を同じinstanceで別々に実行し、経路別・∪の検出率と見逃し相関を1回で測る。
3. **gold**: 正式`SAFETY_CRITICAL_CLAIM_DEFS`のBLOCKING 6件(B3・A2A3-0・A4-0・A5-0・B4-a・B3-same@neg5)に限定。HF-011は**監視項目**(goldではない)。これはgold変更ではなく、設計書の非公式「7 gold」を正式定義へ戻す是正。Closeout報告でユーザーへ開示(HF-011をgoldに加えるかはユーザー判断事項として提示、本Trialでは加えない)。
4. 採用基準(段階A、事前固定): 正式SC 6件が2経路∪でn=3中3/3(経路別も報告)、er009合成9種はhold-out n=1で新たな見逃しなし、欠落IDは再実行で解消(runの5%超残存はSTOP)。「負例MAJOR率非悪化」は物差しとして不適(新Stage 1はMAJORを出さない)→NORMALの候補数/記事・E2Eでの誤BLOCKING率・Rewrite率・費用で見る。限界(n=3×6は見逃し0の証明ではない)を明記。
5. 段階B(E2E、段階A合格時のみ): SC 7 instance+負例/NORMAL 6をn=2+B2_hormuz・hormuz_run01/02 n=2(約26〜30 run)。Rewrite後のRecheckも新Stage 1仕様で実行(変更単位と前後1単位の再判定、Rewriteが起きた記事は出口前に3'-Rを全文1回)。測定: Human Review/STAGE4、Rewrite率、誤BLOCKING率、平均追加費用、worst run、runtime。STOP: 正式SCの∪見逃し/hold-out見逃し/E2E Human Review/worst ¥3超(報告、FAILではない)/欠落ID 5%超。
6. 費用: ループ1合計約¥90〜110(段階A約¥50〜60、段階B約¥40〜50)、枠約¥238内。平均追加の見込み+¥1.4〜1.8。「追加」基準はProduction現行1記事費用(委任_04c算出¥2.77)を併記しつつ、KPI判定はrep30と同じ「後段+Stage 1の合計/記事」で行う(両方報告)。
7. 11-3 STOP条件照合: Opusが挙げた(1)結論対立はFableがOpus修正案を採用して解消、(3)トレードオフはユーザー§4・§9が測定を指示しているため測って報告、(5)/(7) HF-011は正式定義へ戻す是正でgold変更ではない。11-3 L2138の「OPEN-233は設計+Opus結果でユーザー報告・実装へ進まない」は2026-10-02の個別例であり、2026-10-05ユーザー指示(本管理ID、自律ループ3回)が優先(22節ユーザー指示優先)。よって実装・段階Aへ進む。H1はバグ是正として扱う。

## 禁止

コード変更禁止(委任_06の領域)。有料API禁止。`CURRENT_SPEC.md`/`PM_GOVERNANCE.md`編集禁止。`git add -A`/`stash`/`amend`禁止。`ACTIVE_TASK.md`/`RESULT_PACKET.md`はaddしない。1回の書き込み2,500文字以下。

## 作業(要約)

1. T-0(本ログ+check)。2. Opus#16抽出保存(見出し「## 1. 結論」「## 4. Safety hole」「## 6. ループ1の推奨最小構成と採用基準」「## 9. 答えられなかった点」存在確認)。3. 設計書末尾に§6「Opus#16後のFable評価(ループ1確定構成)」(上記1〜7逐語)、DECISION_LOG末尾に短いエントリ。4. Opus台帳へ#16のH1(fail-open、重大)・H2(MINOR切り捨て)・H3(因果はfloor対象外)・H4(F3)・1-a・1-b・1-c登録(H1〜H4=FABLE_DECIDED→委任_06で実装、1-c=FABLE_DECIDED[gold 6限定・HF-011監視])。5. ¥0事前作業1(`agg_fresh_minor_check_01.py`→json/md): A構成fresh 32 runで neg5 B3-same・A4-0・HF-011・B4非SC 4件の文がMINORとして出た回数を集計、H2が主因かYes/No/部分で判定(確認/推測区別)。6. ¥0事前作業5(`agg_v0_v4a_union_baseline_01.py`→json/md): V0記録n=1・V4A fresh n=2・V0@6luna n=2・候補@5.6 n=1で「V0∪V4A」の正式SC 6件検出・NORMAL候補数の基準線(採用提案ではない)。7. OPEN_ITEMS進捗(委任_05: Opus#16保存・Fable評価…委任_06: 実装(並行)。ループ1/3進行中)、REPORT_LEDGER 1行、REPORT §66、ACTIVE_TASK(addしない)。8. commit/push(明示add)、メッセージ: `OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01: Opus#16保存・Fable評価(3'-R+5-lite 2経路∪・F3・H1是正、gold正式6件限定・HF-011監視)、設計案比較・packet(委任_03)をcommit、fresh MINOR確認【主因判定】・V0∪V4A基準線(委任_05、¥0)`

- 固定ブロックE-1/D-1/G-1/F-1/T-2/T-3は従来どおり(T-0は本ログ+check)。KPI provenance欄: 本委任はKPI算出を行わない(既存データの集計のみ、provenanceは各集計出力に区分明記)。

## 事前指定Read一覧

`a_frozen_fresh_01/*.json`・`agg_phase1.json`/`matrix_2x2.json`・runner Grep `SAFETY_CRITICAL_CLAIM_DEFS`・抽出ツールヘッダ・Opus台帳列定義・設計書末尾。

## 事前指定Grep一覧+追記位置・更新位置の手順

設計書末尾§6、DECISION_LOG末尾、Opus台帳末尾、OPEN_ITEMS本管理ID行、REPORT末尾に§66、REPORT_LEDGER末尾。

## 実行コマンド全文

check_delegation_prompt.py --file docs/pm/delegation_log/2026-10-05_OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01_05.md --json-out docs/pm/delegation_log/2026-10-05_OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01_05.md_check.json
extract_agent_text_from_transcript_01.py --transcript <上記> --start-marker <上記> --end-marker <上記> --out docs/pm/opus_l2_review_open233_stage1_redesign_16.md --header-file <scratch>
集計: agg_fresh_minor_check_01.py / agg_v0_v4a_union_baseline_01.py を作成して実行。Git: git status --porcelain→明示add→commit→git push origin main→git log --oneline -1。

## 報告(短く)

(1)結論6行以内(MINOR確認の判定、V0∪V4A基準線の数値、Opus#16保存文字数)、(2)SSOT・台帳更新、(3)T-0・commit・push・raw URL(Opus#16/設計書)、一覧外Read、確認/推測。
