# FAMILY-A-DISCOVERY-FOCUS-ROLE-PLANNING-CONNECTION-TRIAL-01 比較

**Trial(Article-only)。Production採用ではない。**Discovery Focus Module Part A
(`er011_discovery_stage3_rule_adjustment_trial_09.CURRENT_FOCUS_BLOCK`、無変更)に、
Point Role Planningへの短いhint接続(案2のみ、案2'は対象外、ユーザー確定判断)を
加えた場合の効果を、focus単独(接続なし)と比較する。

テーマ: "Why do we sometimes wake up right before the alarm rings?"
Ledger再利用元: `er011_output/discovery_generalization_wake_before_alarm_trial_12`
(新規Research/Ledger作成なし)。

- focus単独(接続なし)A2/B1: `er011_output/discovery_focus_module_revalidation_01/{a2_focus,b1b_focus}`を
  再利用(再生成なし、追加費用¥0)。
- focus+接続(案2 hint)A2/B1: 本Trialで新規生成
  (`er011_output/discovery_focus_role_planning_connection_trial_01/{a2_connected,b1b_connected}`)。
  接続関数は`er011_point_role_planning_focus_connection_trial_04.run_one_pattern_connected`
  (現行Production `run_one_pattern`[OPEN-141差分QA込み]とhint注入以外の差分ゼロを
  `er011_point_role_planning_focus_connection_trial_04_test_01.py`で機械確認済み)。
- 案2 hint文言(`DISCOVERY_WHY_POINT_ROLE_HINT_BLOCK`、新規創作せず既存draftから転記):

  > This is a Discovery/Why article (Main Story presents a phenomenon without fully resolving why it happens).
  > When planning Point One and Point Two, prefer roles the Ledger actually supports from among: a distinct
  > causal mechanism Main Story left unresolved, an unexpected contributing factor from a different angle
  > (psychological, environmental/design-related, or social/contextual) than the other Point, or a limitation
  > on what the evidence actually explains. Do not assign both Points the same causal angle, and do not let
  > either Point simply restate the phenomenon already described in Main Story.

実費: **¥46.47**(上限¥300、新規生成2記事分、`cost_summary.json`)。

記事全文・role plan JSON全文は [index.html](index.html) を参照(本文をユーザーが直接読める形)。

## 1. 経緯(前回STOP、再読は本節のみで足りるよう要約)

前回(本管理ID初回委任)、Gate 4静的確認で本タスクと同日のcommit `ce39de7b`
(OPEN-141差分QA+target-sentence-matching既定ON)により、再利用予定だった
`er011_point_role_planning_focus_connection_trial_03.py`の`run_one_pattern_connected`
(Trial-03[2026-09-09]時点のコピー)がこの新規安全ゲートを欠くことが判明し、
記事生成を一切行わずSTOPした(詳細:
`FAMILY-A-DISCOVERY-FOCUS-ROLE-PLANNING-CONNECTION-TRIAL-01_REPORT.md`1節)。

Fable判断(選択肢(a)採用): 接続関数を現行Production `run_one_pattern`と同等の
新コピーとして`er011_point_role_planning_focus_connection_trial_04.py`に作り直し、
hint注入以外の差分ゼロを機械的に証明したうえで本Trialを実行した。旧trial_03は
無改変のまま保全(News向けGate 1=VALIDATED実績を維持)。

機械証明の方法: `inspect.getsource(prod_gen.run_one_pattern)`へ既知の置換規則
(関数名変更・引数追加・呼び出し2箇所の置換・bareヘルパー参照14件へのprod_gen.修飾)を
機械的に適用した結果が、`t4.run_one_pattern_connected`のソースとバイト単位で
完全一致することを、`Gate4SourceReconstructionTests`が実行毎に自動確認する
(目視diffではなく再現可能な機械証明)。

| 差分項目 | 内容 |
|---|---|
| 関数名 | `run_one_pattern` → `run_one_pattern_connected` |
| 新規引数 | `point_role_hint_block: str = ""` |
| 呼び出し置換(初回) | `point_planning.run_point_role_planning(...)` → `run_point_role_planning_connected(..., point_role_hint_block=point_role_hint_block)` |
| 呼び出し置換(Diagnostic Full Retry内) | 同上(retry時も同じhintを引き継ぐ) |
| bareヘルパー参照の修飾(14件、ロジック変更なし) | `_writer_process`, `_generate_and_compress_article`, `run_point_overlap_qa_and_regenerate`, `split_common_sections_for_point_qa`, `build_diagnostic_retry_prompt`, `compute_metrics`, `normalize_article_formatting`, `POINT_OVERLAP_ARTICLE_RETRY_MAX`, `POINT_TARGET_LOWER/UPPER`, `POINT_TOLERANCE_LOWER/UPPER`, `TOTAL_SOFT_LOWER/UPPER`, `REASONING_EFFORT` へ`prod_gen.`を付与しただけ |

上記以外の差分は無い(OPEN-141差分QA[Fact Checker A'再実行+Ledger再確認+Point
Overlap再計算]・target-sentence-matching既定ON・retry上限・print文・出力ファイル名は
現行Productionのまま一切変更していない)。LLMモック統合テスト(`RunOnePatternConnectedIntegrationTests`)で、
`point_role_hint_block=""`時にProduction版とtrial_04版のPoint Role Planning requestと
結果構造がbyte一致することも確認済み(6 test全PASS、詳細は
`er011_point_role_planning_focus_connection_trial_04_test_01.py`)。

## 2. 客観データ(Fact Safety・retry)

| Arm | status | fact_verdict | ledger_status | ledger_deviation件数 | local_rewrite cycles/items | article retry | Point Overlap flagged | directional_fact_precheck |
|---|---|---|---|---|---|---|---|---|
| A2 / Focus単独 | OK | PASS | LEDGER_COMPLIANT | 0 | 1 / 1 | 0 | なし | DIRECTION_REVIEW_REQUIRED |
| A2 / Focus+接続 | OK | PASS | LEDGER_COMPLIANT | **1(MINOR)** | 0 / 0 | 0 | なし | DIRECTION_REVIEW_REQUIRED |
| B1 / Focus単独 | OK | PASS | LEDGER_COMPLIANT | 0 | 0 / 0 | 0 | なし | DIRECTION_REVIEW_REQUIRED |
| B1 / Focus+接続 | OK | PASS | LEDGER_COMPLIANT | 0 | 0 / 0 | 0 | なし | DIRECTION_REVIEW_REQUIRED |

`directional_fact_precheck=DIRECTION_REVIEW_REQUIRED`は4記事全てで共通(接続の
有無と無関係、この暫定チェック[ER-008、advisory]がこのLedger/テーマで一貫して
出る特性であり、本Trialの新規事象ではない)。いずれもFact Checker verdict=PASS、
Ledger Deviationはoverall_status=LEDGER_COMPLIANTでblockingなし、Point Overlap
QAも全記事flagなし(4記事ともarticle retry 0回で解消)。

**A2/Focus+接続でのみ検出されたMINOR逸脱1件**(non-blocking、記録のみ、Local
Rewriteは対象外のため未発火):

> "So, on one night, a familiar wake-up time may arrive during a lighter part of
> sleep. On another night, it may arrive during deeper sleep. This may help
> explain why waking before an alarm can sometimes feel clear and easy, but may
> not happen—or may feel very difficult—on another morning."

Ledger Deviation Checkerの指摘: 「睡眠段階に関する証拠(F013・F014)は主に
『起こされたときの目覚めやすさ・睡眠慣性』を示しており、目覚まし前の自然覚醒
そのものの発生有無・時刻を説明するとは限らない。記事は"may"で弱めているが、
睡眠段階を目覚まし前覚醒の発生理由にまで部分的に拡張している」(severity=MINOR、
`changed_causality=true`のみ、Hook対象外)。これは、hintが要求する「Main Storyが
残した『なぜ』への独立した因果的説明」という役割(後述のrole plan参照)を、
Writerが忠実に実行しようとした結果、証拠の射程をわずかに超える因果的言い回しに
踏み出したものと解釈できる。既存の安全装置(MINOR記録・MAJORのみLocal Rewrite対象)
がそのまま機能し、記事は最終的にLEDGER_COMPLIANTのまま安全側に収まっている。
一方で、hint接続は「Main Storyが解決しない因果的機序」をPointに割り当てる方向に
Writerを誘導するため、この種のMINOR逸脱がfocus単独条件より起きやすくなる可能性が
あることは、今後同種のhintを設計する際の留意点として記録する。

## 3. Point Role Planningの接続効果(role要約・hint反映の確認)

| Arm | Point One role(要約) | Point Two role(要約) |
|---|---|---|
| A2 / Focus単独 | 複数の生理指標(ACTH・脳活動・心拍)の先行変化を「段階的なカウントダウン」として統合 | 自己覚醒研究における「意図的な練習・期待」と「偶発的な目覚まし前覚醒」を区別 |
| A2 / Focus+接続 | **睡眠段階(深いNREM→浅いNREM/REM)という別の因果的機序**を提示、目覚めやすさの夜内変動を説明 | 「予定時刻を知った上での自己覚醒」と「偶発的な目覚まし前覚醒」の区別(エビデンスの限界) |
| B1 / Focus単独 | 概日ペースメーカーを「同調範囲に限界のある同調装置」として再定義 | 自己覚醒は学習された技能である可能性(練習・個人差) |
| B1 / Focus+接続 | **睡眠段階(深いNREM→浅いNREM/REM)という別の因果的機序**(A2/Focus+接続とほぼ同一の切り口) | 期待・ルーティンに基づく「学習された約束事」としての自己覚醒(A2/Focus+接続のPoint Twoと同系統) |

hintは「Main Storyが解決しない因果的機序」「他方のPointと異なる角度の要因
(心理的/環境・設計的/社会的)」「エビデンスの限界」という3つの役割候補を提示している。
Point Role Planningの出力(`audit/point_role_planning_initial.json`)を見ると、
**接続ありの2条件(A2・B1)は両方ともPoint Oneに「睡眠段階(sleep architecture)」
という同一の因果的機序を選択し、Point Twoに「学習された期待・ルーティン」という
同系統の役割を選択した**。これはhintが実際にPoint Role Planningの出力語彙・構造に
反映されていることを示す一方、**A2とB1の間で役割選択が収束し、レベル間の書き分けの
多様性という観点では意図しない副作用**になっている(4節参照)。対照的に、focus単独
(接続なし)条件ではA2が「生理指標の段階的カウントダウン」、B1が「概日ペースメーカーの
限界」という異なる切り口を選んでおり、レベル間で異なる役割が自然に生まれていた。

## 4. Main Storyに残した要素/Pointへ繰り延べた要素(対応表)

Role plan中の`evidence_anchor`(Pointが使うエビデンス)と
`must_not_overlap_with_full_story`(Main Storyで繰り返してはいけない内容)を、
実際の記事本文と突き合わせた。

### A2 / Focus+接続

| 項目 | Main Story | Point One | Point Two |
|---|---|---|---|
| 使用したエビデンス | F001(概日同調)、F008(ACTH先行上昇)、F005/F006(脳活動・心拍先行変化)、F003/F017(自己覚醒研究の限界、示唆のみ) | F002・F013・F014(睡眠段階の夜内変化と睡眠慣性) | F003・F017(17研究・715人のレビュー、方法論の相違)、F005・F007(7/15人成功、7日目82%) |
| Main Storyが実際に書いた範囲 | 概日同調・ACTH・脳活動・心拍の先行変化までを提示し、"they do not show that the body knows the exact minute an alarm will ring"で締めている(role planの`must_not_overlap_with_full_story`が禁止した内容は繰り返していない) | (該当なし) | (該当なし) |
| Pointが繰り延べた範囲 | (該当なし) | "Deep sleep becomes less common, while lighter sleep and REM sleep become more common... may help explain why waking before an alarm can sometimes feel clear and easy" — role planの計画通り、睡眠段階という別角度をMain Storyでは触れずPoint Oneのみで展開 | "Many self-awakening studies asked people to expect a certain time... These results suggest that expectation and a repeated schedule may help. They do not prove that the brain can find the exact future moment" — 計画通り、自己覚醒研究の方法論的限界をPoint Twoのみで展開 |

役割分担は計画(role plan)とほぼ一致している。ただしPoint Oneの実装が、3節の
MINOR逸脱で述べた通り、計画上の"may help explain"という留保付き示唆を若干超えて
因果的に読める文へ踏み出した箇所がある。

### B1 / Focus+接続

| 項目 | Main Story | Point One | Point Two |
|---|---|---|---|
| 使用したエビデンス | F001、F008、F005・F006、F003・F017(示唆のみ) | F002・F013・F014 | F003・F004・F007・F017 |
| Main Storyが実際に書いた範囲 | 概日同調・ACTH先行上昇・自己覚醒研究の限界まで(F002由来の睡眠段階には触れていない) | (該当なし) | (該当なし) |
| Pointが繰り延べた範囲 | (該当なし) | "As the night goes on, deep sleep becomes less common... waking from deep sleep is linked with a stronger heavy, slow-to-start feeling. Near the usual wake-up time, a person may be easier to wake..." | "people who did not usually wake on their own reached an 82% success rate by the seventh day... points less to a perfect internal timer and more to a learned appointment with an expected time range" |

B1でも計画通りの役割分担が実装されており、Main Storyは睡眠段階に触れず、Point
Oneのみが担当している。B1のPoint Oneは"may be easier to wake"という留保付きの
書き方に留まっており、A2で見られたMINOR逸脱に相当する踏み込みは見られなかった
(Ledger Deviation上もB1/接続は0件)。

## 5. 書き分け(A2 vs B1、各条件内)

- **Focus単独**: A2は生理指標(ACTH・脳活動・心拍)の時系列を「段階的カウントダウン」
  として統合する切り口、B1は概日ペースメーカーそのものを「同調範囲に限界のある
  装置」として再定義する切り口で、Point Oneの角度が明確に異なる。B1のFull Story側は
  cortisol(F011/F012相当、Ledgerにはコルチゾール関連事実が別途存在)には触れていない
  ものの、"Think of the body clock as a synchronizer, not a perfect stopwatch"
  という比喩でA2にはない独自の説明様式を持つ。
- **Focus+接続**: 前述の通り、A2・BいずれもPoint Oneが「睡眠段階」、Point Twoが
  「学習された期待」に収束しており、A2とB1の差異は主に語彙の平易さ(A2は
  "harder"ではなく単文中心、B1は"slow-to-start feeling"のようなやや複雑な表現)に
  留まる。CEFR難易度の書き分けは維持されているが、**内容面の角度の書き分けという
  観点ではfocus単独条件より弱くなっている**。

## 6. Pointの価値と多様性

- 4記事ともPoint One・Point Twoの重複度は低い(point_overlap_qa.json、
  overlap_ratio 0.10〜0.20、閾値0.4を大きく下回る)。
- 接続ありの2条件は、Point Oneが「Main Storyが解決しない因果的機序」という明確な
  役割を持ち、Full Storyでは触れられない具体的な機序(睡眠段階と目覚めやすさの関係)
  を提示している点で、「新しい価値」の基準(留保だけで構成されない、Full Storyの
  言い換えでない)を満たしている。
- 一方、A2/Focus単独のPoint One(「段階的カウントダウン」)は、実質的にはFull
  Storyで既に提示された3つの生理指標(ACTH・脳活動・心拍)を時系列でまとめ直した
  もので、新規のエビデンス(F002・F013・F014の睡眠段階)を持ち込んだ接続ありの
  Point Oneと比べると、新規性がやや低い(ただし「意義の一般化」という切り口の
  違いはあり、無価値ではない)。
- cross-article角度の多様性という観点では、接続ありのA2・B1がほぼ同じ役割の組へ
  収束したため、本Trial内の4記事全体で見ると「睡眠段階」と「学習された期待」という
  2種類の切り口しか実質的に登場しない(focus単独の2記事はそれぞれ異なる切り口を
  追加していたため、4記事合計で見た多様性はfocus単独の方が高かった)。

## 7. 記事としての面白さ(0〜2点、主観評価、根拠引用付き)

- **A2/Focus単独: 1点**。"Practice changes the question"という見出しは軽い意外性が
  あるが、本文は淡々とした事実列挙に近い。
- **A2/Focus+接続: 2点**。"It can feel as if your body heard a sound that never
  came."という導入の比喩、および"So, on one night, a familiar wake-up time may
  arrive during a lighter part of sleep. On another night, it may arrive during
  deeper sleep."という夜ごとの違いを説明する具体的なイメージが、聞き手にとって
  分かりやすく面白い(ただし3節で述べた通り、この具体的なイメージ自体がMINOR逸脱の
  原因にもなっている)。
- **B1/Focus単独: 1点**。"Think of the body clock as a synchronizer, not a perfect
  stopwatch."という比喩は良いが、Point Twoは統計の列挙に留まる。
- **B1/Focus+接続: 2点**。表題"The Alarm Before the Alarm"、および"Maybe the body
  is learning an appointment"という見出しと"a learned appointment with an
  expected time range"という表現が、記事全体を一貫した物語(体内時計・睡眠段階・
  学習という3層構造)としてまとめており、単なる事実列挙以上の読み応えがある。

主観評価のため、この採点は参考情報として扱い、Gate判定の主軸には用いない。

## 8. Gate 1判定材料(まとめ)

- Fact Safety: 4記事ともFact Checker PASS、Ledger Deviation overall_status=
  LEDGER_COMPLIANT、Point Overlap QA flagなし、article retry 0回。接続ありの
  A2でのみMINOR逸脱1件(non-blocking、記録のみ、安全装置は正常に機能)。
- 接続の効果: Point Role Planningのrole出力にhintの語彙(distinct causal
  mechanism / different angle / limitation)が反映され、実際の本文にも
  「Main Storyに残した現象提示」と「Pointへ繰り延べた機序・限界」の分離が
  計画通り実装されていることを4節の対応表で確認した。
- リスク: (i) 接続ありでA2・B1の役割選択が収束し、レベル間・記事間の角度多様性が
  低下する可能性がある(5〜6節)。(ii) 「Main Storyが解決しない因果的機序」という
  役割の割り当てが、証拠の射程をわずかに超える表現(MINOR逸脱)を誘発する可能性が
  ある(3節)。いずれも既存の安全装置(Ledger Deviation Checker、Point Overlap QA)
  の範囲内で検出・記録されており、記事の最終ステータスはOK/LEDGER_COMPLIANTに
  留まっている。
- 本Trialはコスト¥46.47・記事4本(新規2本)・単一テーマのみであり、cross-article
  角度収束やhintの一般化可能性を確定させるにはサンプル数が不十分(前回・前々回の
  Trialと同様の既知の限界)。

## 9. 残る問題(次善のTrialがある場合の材料)

- 接続ありでのA2/B1角度収束が、hintの語彙構成(mechanism/different-angle
  factor/limitationの3択)自体に起因するのか、単一テーマ・単一Ledgerによる
  偶然かは、本Trial(N=1テーマ)だけでは切り分けられない。
- 案2'(Main Story逆方向注記)は今回未実施(ユーザー確定判断により対象外)。
  Main Story抑制効果を接続なしでどこまで実現できるかは、Focus Module Part A
  単独の効果(3節のFocus単独記事も既にMain Storyでは機序を明示していない)との
  比較で一定の効果が示唆されているが、直接の検証はしていない。

## 10. 費用内訳

`cost_summary.json`(実測): 合計¥46.47(A2/接続 ¥22.09、B1/接続 追加分
¥24.38、focus単独2記事は再利用のため追加費用¥0)。上限¥300に対し十分な余裕。
