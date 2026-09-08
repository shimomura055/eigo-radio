# FAMILY-A-DAILY-NEWS-FOCUS-LAYER-COMPARISON-TRIAL-04 報告書

管理ID: FAMILY-A-DAILY-NEWS-FOCUS-LAYER-COMPARISON-TRIAL-04(Lane A、A-UDR-12)。
**Trial(生成実行の再比較)。Production/Prompt/SSOT編集・Git操作は一切行って
いない。monkeypatch・グローバル書き換えなし。TTSは実行していない
(text-onlyまで)。** 並列稼働中のLane B(A2 Production wiring、`er012_*`/
`er003_v1_n3_01_assemble.py`)の成果物は参照していない。`docs/pm/
ACTIVE_TASK.md`/`RESULT_PACKET.md`は編集していない。

ユーザー決定根拠: A-UDR-12(接続案(b)、`FAMILY-A-POINT-ROLE-PLANNING-
FOCUS-MODULE-CONNECTION-TRIAL-03_REPORT.md`でVALIDATED)を、Hanshin Ledger
固定でbaseline/focus x A2/B1B x **N=3**(12本)で再比較し、単一runの成功例
だけで結論を出さない。A-UDR-13(Point Overlap Loop Budget高頻度)は別
failure modeとして混同せず、閾値・Loop上限は変更していない。

新規ファイル(いずれもTrial、Production未編集): `er011_daily_news_focus_
layer_comparison_trial_04.py`、`_cost_compute.py`、`_cost_recover_run23.py`、
`er011_output/daily_news_focus_layer_comparison_trial_04/`一式。

---

## 1. 12本の結果一覧

| run | 条件 | Level | status | retry | fact_verdict | ledger_status | P1 overlap(flag) | P2 overlap(flag) | 語数 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | baseline | B1B | OK | 0 | PASS | LEDGER_COMPLIANT | 0.241 | 0.355 | 241 |
| 1 | baseline | A2 | NG | 2/2 | (未到達) | (未到達) | 0.444(F) | 0.333 | 248 |
| 1 | focus | B1B | NG | 2/2 | (未到達) | (未到達) | 0.154 | 0.412(F) | 272 |
| 1 | focus | A2 | NG | 2/2 | (未到達) | (未到達) | 0.462(F) | 0.259 | 225 |
| 2 | baseline | B1B | NG | 2/2 | (未到達) | (未到達) | 0.379 | 0.267 | 264 |
| 2 | baseline | A2 | NG | 2/2 | (未到達) | (未到達) | 0.621(F) | 0.536(F) | 260 |
| 2 | focus | B1B | OK | 1 | REVIEW_REQUIRED | LEDGER_COMPLIANT | 0.394 | 0.37 | 227 |
| 2 | focus | A2 | OK | 2/2 | PASS | LEDGER_COMPLIANT | 0.296 | 0.143 | 252 |
| 3 | baseline | B1B | OK | 2/2 | PASS | LEDGER_COMPLIANT | 0.28 | 0.303 | 288 |
| 3 | baseline | A2 | NG | 2/2 | FAIL | (未到達) | 0.37 | 0.241 | 262 |
| 3 | focus | B1B | NG | 2/2 | (未到達) | (未到達) | 0.346 | 0.323 | 256 |
| 3 | focus | A2 | OK | 0 | REVIEW_REQUIRED | LEDGER_COMPLIANT | 0.333 | 0.3 | 257 |

閾値0.4(既存Production既定、変更なし)。詳細: `{a2,b1b}/{baseline,focus}/
run{1..3}/analysis.json`。

---

## 2. 集計(baseline vs focus)

| 指標 | baseline(N=6) | focus(N=6) |
|---|---|---|
| NG_REVIEW_REQUIRED率 | 66.7%(4/6) | 50.0%(3/6) |
| retry回数平均 | 1.67 | 1.50 |
| P1 overlap平均(flagged数) | 0.389(2件) | 0.331(1件) |
| P2 overlap平均(flagged数) | 0.339(1件) | 0.301(1件) |
| 語数平均 | 260.5語 | 248.2語 |

レベル別status(3本中OK数): baseline A2=0/3、baseline B1B=2/3、focus
A2=2/3、focus B1B=1/3。**A2はfocusでNG率改善(100%→33%)、B1Bはfocusで
NG率悪化(33%→67%)**という逆方向の傾向がレベル間で見られ、統合すると
相殺し合っている。N=3/レベルでは傾向として断定できない。

**役割再現率(Point Role Planning出力、キーワード機械分類+短い根拠)**:
mechanism/beyond_the_headline/limitationの語彙が厳密に一致したのは、
baseline P2で1/6(mechanism)、focus P1で3/6(mechanism1+beyond_the_
headline2)、focus P2で2/6(mechanism1+limitation1)のみで、残りは
すべて「other」(キーワード非一致)。特に**run3(focus B1B/A2)でのみ**、
hint文言の語彙("additional...beyond the headline"「what remains
unconfirmed」相当)がrole文言にほぼそのまま反映された("An additional-
contribution point"「A fact-bound nuance...that the ledger does not
establish」等)。run1・run2のfocus条件では、意味的には近い設計(late-game
lineup depth mechanism、damage control等)がされているものの、hintの
語彙をそのまま反映してはおらず、キーワード機械分類では検出できなかった
(この分類はキーワード一致ベースの簡易ヒューリスティックであり、再現率
=分類ヒット率であって「意味的に役割を体現しているか」の網羅的な判定では
ない。人手による粗い読みでは、baseline条件でも大半のPointは実質
「mechanism寄り」の説明になっており、focus条件固有ではない)。

**Point本文がroleを体現しているか(body_embodies_role)**: `analysis.json`
の`point_one_body_embodies_role`/`point_two_body_embodies_role`に記録
(role=other時は判定対象外)。role=beyond_the_headline/limitation/
mechanismに分類できた9件(baseline3+focus6)のうち、本文キーワード一致が
確認できたのは6件(baselineの1件含む、focusの5件)。詳細は各`analysis.json`
参照。

**自然さ(既存Naturalness QA方針での簡易評価、主観・簡易読みであることを
明記)**: 12本中いくつか(run1 B1B baseline/focus、run3 B1B focus等)を
抜粋読みした限り、focus条件で不自然な文体・機械的な語彙の混入は見られず、
baseline同様に流暢な成人向けニュース英語だった。ただし本評価は網羅的な
QAツールによるものではなく、担当エージェントによる主観的な抜粋確認である。

---

## 3. A-UDR-13向け観測データ(Focus Module要因との切り分け)

baseline条件(hint=""・Focus Moduleなし、Production既定と同一設定)で
既に**NG率66.7%(特にA2は3/3全てNG)**が観測されており、これは既存
Production既定の挙動そのもの(本Trialが発生させたものではない)。focus
条件のNG率(50%)はbaselineより**低い**ため、少なくとも本Trialの範囲では
「Focus ModuleがNG率を悪化させた」形跡はない。Point Overlap ratio平均も
focusの方がわずかに低い(P1 0.331<0.389、P2 0.301<0.339)。したがって
A-UDR-13(Point Overlap Loop Budget高頻度)の主要因はFocus Module以前の
既存Production挙動(baseline A2の恒常的な高NG率)にあり、Focus Module
接続案(b)がこの問題を新たに発生・悪化させた証拠は本Trialでは見られな
かった。ただしN=3/レベルでは統計的に弱く、「focusがNG率を有意に改善する」
とまでは言えない(§2参照、レベル間で逆方向の傾向あり)。

---

## 4. 副作用の整理

- 新規failure modeの発生: なし(既存の安全装置=Point Overlap retry上限
  2回・Point-only regeneration無効化・Fact Checker FAIL時停止・Local
  Rewrite cycle上限はいずれもそのまま作動、baseline run3 A2ではFact
  Checker FAIL[信頼できる情報と明確に矛盾]が発生し正しくNG_REVIEW_
  REQUIREDで停止した。これはFocus Moduleと無関係のbaseline条件下の既存
  安全装置の作動)。
- Overlap悪化: focus条件で「focus条件の方が高いoverlap」が観測された
  のはrun1 focus A2(P1=0.462、baseline同runのA2=0.444よりわずかに高い)
  のみ。平均では前述のとおりfocusの方が低い。
- Retry回数: focus平均1.50 < baseline平均1.67(系統的な悪化なし)。
- 語数: focus平均248.2語 < baseline平均260.5語(目立った逸脱なし、既存
  target/tolerance rangeは`length_report.json`参照、いずれもrun中に
  hard failureなし)。

---

## 5. 費用・latency

**費用**: 合計約**¥95.5**(上限¥150以内)。内訳:
- run1(4本): ¥24.1(`cl.install()`が正常稼働し全call実測、
  `cost_summary.json`)。
- run2/run3(8本): **運用ミス**により、別プロセス(バックグラウンド実行)
  でrun2/run3を実行した際に`cl.install()`(全API call実測用の既存
  monkeypatch機構)の呼び出しを失念し、生ログ(raw_usage_log.jsonl)への
  記録が欠落した(TTS/ASRは実行していないため安全上の実害はない。費用
  実測の欠落のみ)。事後回復として、各記事の監査証跡(audit配下JSON)に
  保存済みのresponse_idを`responses.retrieve()`(課金なしのメタデータ
  取得)で再取得し、¥56.0を実測回復した(`cost_recovery_run2_3.json`)。
  ただしPoint Overlap Diagnostic Full Retryで上書きされた前段の生成
  呼び出し・Local Rewrite内部呼び出しはresponse_id自体が監査証跡に保存
  されておらず(この欠落はrun1でも同様に存在する構造的な記録範囲の限界
  であり、今回の運用ミス固有ではない)事後回復不可能なため、run1の同型
  ギャップの実測値(A2 retry 1回=¥0.95、B1B retry 1回=¥1.11、local
  rewrite 1cycle=¥0.95)を根拠に保守的な加算推定(¥15.4)を行った
  (`cost_summary_final.json`、方法論は同ファイル内に明記)。
- 費用超過は発生しておらず、N=2への縮退・STOPは不要だった。

**latency**: 1本あたり88.9秒(run3 focus A2、retry 0)〜290.0秒(run2
focus B1B、retry 1+ledger deviation+local rewrite 2 cycle)。retry回数・
local rewrite発生有無に強く依存し、focus/baselineの系統差は明確でない
(`{level}/{condition}/run{N}/analysis.json`の`elapsed_seconds`参照)。

---

## 6. Gate 4 / Gate 1分類 / Production配線に必要な判断

**Gate 4**: PASS。`er003_v1_n3_01_articles_generate.py`/`er011_point_
role_value_planning_01.py`/Trial-03(`run_one_pattern_connected`等)は
いずれもimportのみで無編集(grep差分なし)。monkeypatch・グローバル書き
換えなし。Lane B成果物は参照していない。ただし上記費用実測の運用ミス
(`cl.install()`呼び忘れ)はGate 4(Production安全性)には無関係(Trial側
の計測ツール呼び出し漏れであり、Production/Prompt/SSOTには一切影響
しない)。

**Gate 1分類: USER_DECISION_REQUIRED**。理由:
1. NG率・overlap平均はfocus条件の方がわずかに良好だが、レベル別では
   A2改善・B1B悪化と**逆方向**であり、N=3では方向性を確定できない。
2. Point Role Planningへのhint反映(role文言への語彙反映)は**run3のみ
   明確**で、run1・run2では意味的類似はあっても hint語彙の直接反映は
   確認できず、**接続の効果自体が run 間で再現的とは言えない**
   (Trial-03の単一成功例で見えた「明確な反映」が、N=3では毎回起きるわけ
   ではないことが判明した)。
3. 新規failure mode・重大な副作用は観測されなかった(§4)。

以上より、「効果が再現的に確認された(VALIDATED)」とも「効果なし/副作用
あり(REJECTED)」とも言い切れず、採用判断には人間ユーザーの判断が必要。

**Production配線に必要な判断項目(実装しない、次段階向け)**:
1. Focus Module最終文言(`MAJOR_DAILY_NEWS_FOCUS_MODULE_BLOCK`)を今回の
   ドラフトのまま確定するか、語彙調整するか。
2. Point Role Planning用hint文言(`MAJOR_DAILY_NEWS_POINT_ROLE_HINT_
   BLOCK`)を今回のまま確定するか。反映率が安定しない(§2)ことを踏まえ、
   hintをより強い指示(例: JSON schema自体にrole候補をenumとして追加）
   へ強化するかどうかも論点。
3. mode名`"major_daily_news"`を`EDITORIAL_TYPE_MODULE_BLOCKS`辞書へ登録
   するか否か(現状Trial限定の直接注入のみ、未登録)。
4. Trend Synthesis側のPoint Role hintは、今回も`point_role_hint_
   block=""`(空)のまま不変維持(A-UDR-11付随決定を維持)。
5. N数不足の解消(追加要否): 本Trialで既にN=3を実施したが、レベル間で
   逆方向の傾向が出たため、採用判断のためにさらに大きいN(例:
   レベル別N=5〜)が必要かどうかはユーザー判断事項。
6. 費用実測の運用手順改善(Lane A固有の再発防止、Production採用判断とは
   別軸): 別プロセスでの実行時に`cl.install()`呼び出しを必ず確認する
   チェックリスト化が必要かどうか。

---

## 7. 新規ファイル一覧

- `er011_daily_news_focus_layer_comparison_trial_04.py`(生成本体)
- `er011_daily_news_focus_layer_comparison_trial_04_cost_compute.py`
  (run1費用集計)
- `er011_daily_news_focus_layer_comparison_trial_04_cost_recover_run23.py`
  (run2/3費用事後回復)
- `er011_output/daily_news_focus_layer_comparison_trial_04/`
  (`{a2,b1b}/{baseline,focus}/run{1..3}/`各記事一式、
  `all_results_so_far.json`、`aggregate_summary.json`、
  `raw_usage_log.jsonl`、`cost_summary.json`、`cost_recovery_run2_3.json`、
  `cost_summary_final.json`)
- `FAMILY-A-DAILY-NEWS-FOCUS-LAYER-COMPARISON-TRIAL-04_REPORT.md`(本ファイル)

Git操作・Production/Prompt/SSOT編集は一切行っていない。
