# 委任文: EDITORIAL-FUTURE-FAMILY-C-V5-EMOTION-RECOVERY-AND-CONSTRAINT-STABILITY-TRIAL-05

## 管理ID

EDITORIAL-FUTURE-FAMILY-C-V5-EMOTION-RECOVERY-AND-CONSTRAINT-STABILITY-TRIAL-05
並行タスク衝突確認: 同時にFAMILY-A-DISCOVERY-S2-PRODUCTION-WIRING-01(er003_*/er011_*/er010_*/SSOT/docs/pm/ACTIVE_TASK.md/Git操作を扱う)が走る。本タスクは**er013_*とer013_output/のみ**を扱い、SSOT(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`)・`docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md`・Git操作(add/commit/push)を**一切行わない**(Fableが後で統合する)。RESULT_PACKETは`docs/pm/RESULT_PACKET_FC5.md`(新規、本タスク専用)へ書く。

## 性質/到達上限Status/禁止事項

- 性質: Trial(Family CはまだProduction採用承認ではない)。到達しうる最終Statusは REJECTED / VALIDATED / USER_DECISION_REQUIRED のいずれか。**VALIDATEDでもProductionへは進まずSTOP**。
- 同一テーマ(家庭用ロボットと家事)・同一Layer 1 Ledger・同一World Scaffold/Layer2-3出力(Trial-02由来、Trial-04と同じ再利用元)を再利用する。別テーマ禁止。Research/Scaffold再生成禁止(¥0再利用)。
- 狙い: 適正な長さ(Trial-04目安: A2 380-520語/B1 450-620語) + 研究・データ解説感0 + Fact Safety維持 + **感情・没入感の回復**(Trial-04で後退した)。
- Fableの前提評価(Trial-04 A2本文をFableが直読した所見): 場面が「認識する→バッグを動かす→コードで止まる→アラート→再開→洗濯物→ベッド」のような出来事列挙になり、感情表現は末尾の"leaves smiling"程度で、Trial-03比で感情強度が2→1に後退。B1では統合示唆段落が場面1と場面2の間に入り、"will"を含む未hedge断定文でFuture Framing QA v2がREVIEW_REQUIRED。
- ユーザーの重要追加指示: **AIへ制約を増やしすぎることで逆に出力が不安定になる可能性も評価する**。単純にルール・禁止事項を積み増す前提にしない。制約過多による不自然さ・機械的文章・不安定化を明示的に評価する。
- 費用上限: Family C残額¥105.01 + 追加最大¥100 = **合計¥205.01(ハード上限)**。v5本体(A2+B1、QA一式込み)の目安¥20-30。追加案の簡易Trialは1案あたり目安¥15-30。上限到達で即STOP。無目的にTrial回数を増やさず「原因仮説→最小検証→評価」の順で進める。
- 禁止: 既存`er013_family_c_future_*_01/_02/_03/_04.py`の編集(新規`_05`系ファイルを作る。既存モジュールのimport再利用は可)/`er013_output/family_c_future_trial_01〜04/`配下の改変/Fact Safety(Layer 1 Ledger Deviation・`[[IMAGINED]]`マーカー・数値/研究語/製品名の編集Gate)の緩和/SSOT・Git操作/er003_*・er011_*・er010_*・er012_*の編集。
- Fact Checker A' verdict=REVIEW_REQUIRED(A2/B1、Trial-03から不変、Layer 1のみ対象)は本タスクの是正対象外。verdictと理由を記録・報告するのみ(変更しない)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

---
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
---

## ユーザー指示(原文)

> v5を**同一テーマ・同一Ledger**で進めてください。狙いは、**適正な長さ＋研究・データ解説感0＋Fact Safety維持＋感情・没入感の回復**の両立です。
> ただしユーザーから重要な追加指示があります。**AIへ制約を増やしすぎることで、逆に出力が不安定になる可能性も評価してください。** したがってv5では、単純にルールや禁止事項を積み増すことを前提にしないでください。まずは前回示した、場面内に感情の起伏1つ/選択1つ/出来事列挙の上限/統合示唆段落の位置整理/枠外hedging契約 を検証して構いませんが、**制約過多による不自然さ・機械的文章・不安定化**も明示的に評価してください。
> さらに、v5が十分うまくいかなかった場合は、**「Trial失敗」でSTOPして報告するだけでは不十分です。** Productionには進まず、Trial範囲内で次を行ってください。1. 失敗原因を分類 2. 追加改善アイデアを複数検討 3. QCDと品質リスクを比較 4. 有望案があれば簡易Trialを実施 5. それでも改善しない場合に初めてUSER_DECISION_REQUIREDとしてSTOP
> 追加改善では、ルール追加だけでなく例えば、必須要素を減らし優先順位だけ与える/「感情1＋選択1」を厳密contractではなくWriterの編集目標にする/場面数を固定せず、総語数budget内でWriterに配分させる/1場面を濃くして2場面目を短いcontrastにする/WriterへのScaffold情報をさらに整理する/前段で台本を作りすぎず、Writerへ創作余地を戻す/QA側で事後評価し、Prompt側の制約を減らす など、**制約削減・自由度調整の方向**も候補にしてください。
> Family CはまだProduction採用承認ではありません。今回の追加Trial予算は、**現在のFamily C残額に加えて、追加で最大＋100円まで**認められています。この＋100円は、v5が不十分だった場合の追加アイデア検証・簡易Trialに使って構いません。ただし、無目的にTrial回数を増やさず、**原因仮説 → 最小検証 → 評価**の順で進めてください。別テーマにはまだ進まないでください。
> 最終的には、何が長文化を生んでいたか/v5で何を変えたか/制約追加が安定性にどう影響したか/語数/感情・没入感/研究解説感0維持/Fact Safety/追加案を試した場合は各案の結果と費用/残る問題/Gate 1判定 を報告してください。Trial終了時は REJECTED/VALIDATED/USER_DECISION_REQUIREDのいずれかに分類し、VALIDATEDでもProductionへは進まずSTOPしてください。

## 事前指定Read一覧

1. `EDITORIAL-FUTURE-FAMILY-C-LENGTH-DIAGNOSIS-AND-RESPEC-TRIAL-04_REPORT.md` L16-80(構造診断・v3→v4契約差分)とL125-140(残る構造問題)。
2. `er013_output/family_c_future_trial_04/comparison.md` 全文(短い)、`er013_output/family_c_future_trial_04/a2/reader_facing_article.txt` 全文、`er013_output/family_c_future_trial_04/b1/reader_facing_article.txt` 全文、`er013_output/family_c_future_trial_03/a2/reader_facing_article.txt` 全文(感情強度の比較基準。Trial-03 B1は不要)。
3. `er013_family_c_future_writer_04.py` 全文(v5 Writer契約の派生元。構造変更対象のため全文可)。
4. `er013_family_c_future_trial_04_run.py` L40-65(THEME_ID/OUT_DIR/BUDGET_JPY_CAP/再利用パス)、L187-222(retry上限定数)、L222-403(`generate_and_qa_family_c_article_v4`の流れ。v5 runはこれを複製し差分のみ変更)。
5. `er013_family_c_future_qa_03.py`: Grep `^def |REVIEW_REQUIRED|will` → Future Framing QA v2の判定関数・hedge判定ロジックの該当範囲のみRead(v5でQA側事後評価を強める案の検討用)。
6. `er013_family_c_future_writer_02.py`: Grep `IMAGINED_OPEN_TEMPLATE|MAX_FACT_EXCEPTIONS|def build_` → 定義範囲のみRead(マーカー契約の確認)。
7. `docs/pm/PM_GOVERNANCE.md`: Grep `15-5|5区分` → 費用報告5区分の定義範囲のみRead。

## 事前指定Grep一覧+追記位置・更新位置の手順

- 新規ファイル作成のみ(既存編集なし): `er013_family_c_future_writer_05.py`(v5契約。v4からのimport再利用可)、`er013_family_c_future_trial_05_run.py`(THEME_ID="family_c_future_trial_05"、OUT_DIR=`er013_output/family_c_future_trial_05`、BUDGET_JPY_CAP実値を設定)、必要なら`er013_family_c_future_qa_05.py`+`er013_family_c_future_qa_test_05.py`、追加案用は`_05b`/`_05c`等の接尾辞で新規ファイル・新規出力dir(`er013_output/family_c_future_trial_05b/`等)。
- v5設計(初回アーム、ユーザー列挙5項目の検証): (1)場面内に感情の起伏1つ、(2)選択1つ、(3)出来事列挙の上限(1場面あたり動作・出来事の連続列挙を上限化)、(4)統合示唆段落は「2つ目の[[IMAGINED]]ブロックの直後、最後の見出し内のみ」に配置固定、(5)枠外(統合示唆・締め)のhedging契約("will"等の断定助動詞を使わずmight/could/may等)。これをv4契約に加える。ただし追加した制約の総数と文章量を明記し、Promptの制約密度(制約項目数・禁止項目数)をv3/v4/v5で表にする。
- 安定性評価(必須): v5契約で各レベル1本の本生成(QA一式込み)に加え、**A2のみWriter呼び出しのみを追加2回**(QA省略、Writer費用のみ、目安¥3-5/回)実行し、計3サンプルで語数・場面数・感情起伏/選択の有無・機械的文章の兆候(同一構文反復、箇条書き的短文連打、テンプレ的言い回し)・マーカー崩れの分散を記録する。これが「制約追加が安定性にどう影響したか」の一次証跡。
- 評価基準(固定、主観評価は本文引用を必ず添える): 語数(目安内か)/研究解説感(数値・研究語・製品名0件+「解説調段落」の有無)/Fact Safety(Layer 1 Ledger Deviation COMPLIANT、[[IMAGINED]]枠内hedge密度、編集Gate PASS)/感情・没入感(0〜3: 0=出来事列挙のみ、1=末尾に感情語1つ程度、2=場面内に感情の起伏または選択が具体描写で1つ、3=起伏と選択が両方あり読者が人物の内面を追える)/機械的文章の兆候(件数と引用)/Future Framing QA v2 verdict。
- v5が不十分(感情・没入感がA2/B1いずれかで2未満、または安定性3サンプルで語数・構造のばらつきが大きい、または機械的文章の兆候が明確)な場合のみ、次を実施: (a)失敗原因を分類(制約過多/制約不足/Scaffold情報過多/QA側の問題/その他)、(b)追加改善案を最低3案検討(必ず「制約削減・自由度調整」方向の案を2案以上含める。例: 必須要素を減らし優先順位のみ/「感情1+選択1」を編集目標化/場面数非固定で総語数budget内配分/1場面を濃く+2場面目を短いcontrast/Scaffold情報整理/QA側事後評価でPrompt制約削減)、(c)各案のQCD(費用・工数・品質リスク・安定性リスク)を表で比較、(d)最有望1案を簡易Trial(A2+B1各1本、または問題側レベルのみ)、費用上限内なら次点1案まで(合計¥205.01を超えない)、(e)それでも改善しなければUSER_DECISION_REQUIRED。
- `docs/pm/RESULT_PACKET_FC5.md`は新規作成。`docs/pm/RESULT_PACKET.md`は触らない。

## 実行コマンド全文

(すべてリポジトリroot `C:\Users\tensh\eigo-radio` で実行)
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\EDITORIAL-FUTURE-FAMILY-C-V5-EMOTION-RECOVERY-AND-CONSTRAINT-STABILITY-TRIAL-05.md --json-out docs\pm\delegation_log\EDITORIAL-FUTURE-FAMILY-C-V5-EMOTION-RECOVERY-AND-CONSTRAINT-STABILITY-TRIAL-05_check.json`
2. offline検証(API呼び出しなし、生成前に実行): `.venv\Scripts\python.exe run_project_regression.py --pattern "er013*"`(基準: Trial-04時点67件PASS。新規テストを加えた件数で全PASS)
3. v5本生成: `.venv\Scripts\python.exe er013_family_c_future_trial_05_run.py`(内部でa2→b1の順に生成・Gate・Fact Checker A'・Layer 1 Ledger Deviation・Local Rewrite・Future Framing QA v2を実行。BUDGET_JPY_CAPで停止)
4. 安定性サンプル: `.venv\Scripts\python.exe er013_family_c_future_trial_05_run.py --stability-samples 2 --level a2`(このフラグを実装すること。Writer呼び出しのみ、出力は`er013_output/family_c_future_trial_05/stability/a2_sample_{1,2}/`)
5. 追加案の簡易Trial(該当時のみ): `.venv\Scripts\python.exe er013_family_c_future_trial_05b_run.py`(案ごとに`_05b`/`_05c`ファイル・出力dirを分ける)
6. 費用集計: 各出力dirの`cost_summary.json`と`raw_usage_log.jsonl`をlogging_contextラベル別に集計し、合計がハード上限¥205.01以内であることを確認。
7. 全件回帰は本タスクでは不要(er013限定回帰のみ。全件は並行タスク側で実施中のため二重実行しない)。
8. 比較HTML: `er013_output/family_c_future_trial_05/index.html`(Trial-03/04/05[+05b等]のA2/B1本文を並べ、語数・感情スコア・QA verdict・費用の表を含む)と`comparison.md`を生成。

## SSOT追記文

本タスクではSSOTを編集しない。root REPORT `EDITORIAL-FUTURE-FAMILY-C-V5-EMOTION-RECOVERY-AND-CONSTRAINT-STABILITY-TRIAL-05_REPORT.md`の末尾に「SSOT追記文案(編集は行っていない)」節として、OPEN-147末尾追記案(Trial-05結果・分類・費用・残額)とDECISION_LOG新エントリ案をそのまま使える形で記載する(Fableが後続のCONSOLIDATIONで反映する)。

## Git(明示add対象・コミットメッセージ・trailer)

本タスクではGit操作(add/commit/push)を行わない(並行タスクとのindex衝突回避。Fableが後続CONSOLIDATIONで明示addする)。RESULT_PACKETに「commit対象候補ファイル一覧」(新規作成した全ファイルと出力dir)を列挙すること。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_FC5.md`(新規)に以下を記載。詳細はroot REPORT。
1. 分類(REJECTED / VALIDATED / USER_DECISION_REQUIRED)と根拠。VALIDATEDでもProductionへ進んでいないことを明記。
2. 何が長文化を生んでいたか(Trial-04診断の要約+v5で新たに分かったこと)。
3. v5で何を変えたか(v4→v5契約差分、制約密度表 v3/v4/v5)。
4. 制約追加が安定性にどう影響したか(安定性3サンプルの語数・構造・感情・機械的兆候の表、引用付き)。
5. 語数(A2/B1、目安、within_range)。
6. 感情・没入感スコア(A2/B1、0〜3、根拠引用。Trial-03/04との比較)。
7. 研究解説感0維持(数値/研究語/製品名件数、解説調段落の有無)。
8. Fact Safety(Layer 1 Ledger Deviation・編集Gate・枠内hedge密度・Fact Checker A' verdict[対象外だが記録])。
9. Future Framing QA v2 verdict(A2/B1)と統合示唆段落の配置結果。
10. 追加案を試した場合: 原因分類、検討案(3案以上、制約削減方向2案以上)、QCD比較表、実施した案ごとの結果と費用。
11. 残る問題。
12. Gate 1判定材料(Fableへ)。
13. 費用: API別+5区分、Trial-05合計、Family C残額(¥105.01+追加¥100からの消費と残)。
14. Artifact: `er013_output/family_c_future_trial_05/index.html`等のrootからの相対パス一覧、commit対象候補ファイル一覧。
15. T-0結果1行、事前指定外Read(理由付き)1行ずつ、STOP該当の有無。

## Fable自己チェック(送信前)

- [x] Read一覧に行範囲/Grepパターンあり
- [x] 追記位置手順あり(新規ファイル・出力dir命名)
- [x] コマンドに引数実値あり
- [x] 禁止事項・費用上限あり(¥205.01ハード上限)
- [x] 並行タスク衝突回避あり(er013限定・SSOT/Git/ACTIVE_TASK不可・RESULT_PACKET分離)
