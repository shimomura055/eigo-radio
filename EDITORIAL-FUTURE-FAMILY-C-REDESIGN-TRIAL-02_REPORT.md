# EDITORIAL-FUTURE-FAMILY-C-REDESIGN-TRIAL-02_REPORT.md

管理ID: EDITORIAL-FUTURE-FAMILY-C-REDESIGN-TRIAL-02
性質: Family C(Future)のドラスティック再設計¥0検討→必要最小限のTrial実行
(残額¥159.17以内)。到達上限は**VALIDATED**(REJECTED/VALIDATED/
USER_DECISION_REQUIRED)。**Production配線・CURRENT_SPEC正式仕様化・
APPROVED_FOR_PRODUCTIONへの変更は禁止**、実施していない。既存Production
経路(A/B-Family)・並行Discovery(`FAMILY-A-DISCOVERY-*`/`er011_*`)・SSOT
本文は無編集。**Git操作は行っていない**(成果物は新規ファイル・
`er013_output/family_c_future_trial_02/`のみ)。Status: **VALIDATED**
(Trial完走、Gate 1判定材料あり)。

## 0. ユーザー方針(原文、冒頭に転記)

> 完成記事に「研究・データ解説っぽさ」が残るのは不可です。…前回提案した
> Writer Promptの軽微な修正だけに限定せず、必要ならドラスティックに設計を
> 変更してください。検討対象には少なくとも以下を含めてください。記事構成
> そのもの/Ledger→Writerへの情報の渡し方/Writer Prompt/研究・統計・製品
> 情報を本文へ出す条件/Future Framing QA/完成記事の編集Gate。
> 完成記事の主役はResearchではなく、未来の生活場面→そこで何が起きるか→
> 人の生活・感情・選択に何をもたらすか→楽しみ/期待/不安/葛藤です。…
> 時間軸: 今回の2030→2035→2040は固定仕様にしません。…機械的に3時点へ
> 当てはめることではなく、そのテーマで最も意味のある未来変化を描くこと
> です。

## 1. 何が問題だったか(Trial-01の残存問題)

`EDITORIAL-FUTURE-FAMILY-C-PROTOTYPE-TRIAL-01_REPORT.md`(VALIDATED)の
記事A2/B1は、Fact Safety(Ledger 3層・Fact Checker A'・Deviation
Checker)は正しく機能していたが、完成記事の**読み味**が「研究・データ
解説」寄りだった。具体的には: 冒頭が統計値の列挙("more than 2.1
million"、"about 57%"等)から始まる/"In one home study"・"A long home
study found"のような研究説明文が残る/B1で製品名・型番(Roborock Saros
Z70、Weave Robotics Isaac 1、LG CLOiD等)が列挙される/未来の時点数が
2030→2035→2040の3段階に固定され、Layer3の出力とそのまま一致していた
(機械的な当てはめの疑い)。

## 2. 何を変更したか(前回→今回、6項目)

1. **記事構成**: 統計提示から始まる導入を廃止し、生活場面から直接始める
   構成へ全面変更。時点数・間隔・時系列/分岐はWriterがテーマに応じて
   選び、選択理由を読者向け本文に出さない内部メモ(`[[META]]...
   [[/META]]`)に記録させる。
2. **Ledger→Writerへの情報の渡し方**: 新設した**World Scaffold**
   (`er013_family_c_future_scaffold_02.py`)により、Layer1の生の統計・
   出典・製品名をWriterへ直接渡すことを廃止した。Layer1→LLM1回で
   「現在できること/できないこと/変化の方向」を、数字・出典・固有名詞を
   含まない平易な文へ変換し、Layer2/3(`er013_family_c_future_ledger_02.py`)
   ・Writerともにこの変換後テキストのみを参照する設計へ変更した。
3. **Writer Prompt**(`er013_family_c_future_writer_02.py`): 統計値・
   比率・年次データ・"study/research/survey/report found/show"型表現・
   製品名/型番の列挙・Research解説構造を明文化して禁止した。現在事実への
   明示的な言及は、World Scaffold由来の平易な言い換えに限り記事全体で
   最大2件まで許可し、`[[FACT: <scaffold_id>]]...[[/FACT]]`で明示させる
   (編集Gate側で機械的にカウント)。
4. **本文へ出す条件・完成記事の編集Gate**(新設、
   `er013_family_c_future_qa_02.py::scan_editorial_gate`): 決定的スキャン
   (¥0)で、(i)統計値・比率・年次データの残存(未来timeframeの年は例外)、
   (ii)研究・データ解説を示す語、(iii)製品名(World Scaffold抽出リストと
   突合)、(iv)FACT例外件数の上限超過、(v)冒頭段落への(i)(ii)の残存、を
   判定する。1つでも該当すればFAILとし、Writer再生成(最大1回)を行う。
5. **Future Framing QA**(v2、6項目目追加): 前回5項目(未来の断定/現在
   事実の捏造/仮定の明示/Discovery化/枠外の未来断定)に加え、6項目目
   「discovery_style_density(記事全体が研究・データ解説として読める
   箇所)」をLLM判定に追加した。
6. **Fact Safety**: Layer1(枠外の現在事実文)に対するFact Checker A'・
   Ledger Deviation Checkerは**Trial-01と同一の既存関数を無改変で
   再利用**し、判定範囲・閾値は一切緩和していない。World Scaffold化に
   より枠外の現在事実文自体が減るのは「緩和」ではなく「本文に出さない」
   設計の帰結である(指示書§作業A-7、以下§7で実測に基づき確認)。

## 3. offline検証結果(¥0、API呼び出しなし)

`.venv/Scripts/python.exe -m unittest er013_family_c_future_qa_test_02 -v`
→ **24 tests, OK**(World Scaffoldの数字/製品名漏洩検出・grounding検証、
Layer2/3(v2)のgrounding検証、Writer Prompt(v2)の禁止語リスト・FACT上限
含有確認、META/FACT/IMAGINEDマーカーの抽出・除去・整合性チェック、編集
Gateの決定的スキャン、を検証)。うち3件は**Trial-01の実際の完成記事
(`er013_output/family_c_future_trial_01/{a2,b1}/reader_facing_article.txt`)
を新設の編集Gateへ入力する回帰テスト**で、両記事が実際にFAILになること
(=前回の問題を今回の設計変更が検出できること)を確認した。

`run_project_regression.py --pattern "er013_*_test_*.py"` →
collected=46 passed=46 failed=0(Trial-01の22件+Trial-02の24件)。
`run_project_regression.py`(default全件)→ collected=2512 passed=2509
failed=3(失敗3件は`er003_test_p2j_investigate.py`の既知の履歴カウント
照合テストで、Trial-01報告時から継続する既存の性質のものであり本Trialとは
無関係)。本Trialの新規ファイルはA-Family/B-Family/Discoveryのどの
ファイルもimport・改変していない。

### 実装中に発見・修正した不具合(実データ実行中)

編集Gateの数字トークン抽出正規表現が、"around 2035."のように未来
timeframeの年の直後に文末ピリオドが続く場合、ピリオドを数字トークンへ
誤って含めてしまい、正当な未来年表現を統計値として誤検出する不具合が
あった(B1のTrial実行中に発見)。正規表現を
`\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?`へ修正し、回帰テスト2件を
追加した上で24/24 PASSを確認してから本Trialを再実行した(詳細は
`er013_output/family_c_future_trial_02/comparison.md`§4)。

## 4. 費用実測(実測、5区分、Trial-01との対比)

同一テーマ「家庭用ロボットと家事」。Research/Ledger Verification(Layer1)
はTrial-01の成果物(`er013_output/family_c_future_trial_01/research/
layer1_only_ledger.txt`)を無変更で再利用(¥0)。

| 区分 | Trial-01(円) | Trial-02(円) |
|---|---|---|
| Research | 24.81 | 0(再利用) |
| Ledger Verification | 34.23 | 0(再利用) |
| World Scaffold生成(新設) | - | 1.88 |
| Layer2/3生成 | 0.50 | 0.64 |
| Writer(A2+B1) | 2.47 | 2.90 |
| QA(Fact Checker A'+Deviation+Framing QA v2) | 78.82 | 14.66 |
| **合計** | **140.83** | **20.08** |

上限¥159.17に対し実測¥20.08(残り¥139.09、API呼び出し16件、
unpriced_records=0)。Fact Checker A'コストが大幅減(A2: 53.41→8.24円、
B1: 19.84→3.98円)。主因は、本文の枠外(現在事実)テキストが生の統計・
製品名の直接引用ではなく、World Scaffold由来の平易な言い換え中心に
なったため、Fact Checker側の検証対象・retry回数が減ったためと考えられる
(狙って最適化したものではなく、設計変更の副次効果)。

## 5. 実施結果(記事A2/B1、QA・編集Gate)

| level | 編集Gate(新設) | Fact Checker A'(Layer1) | Deviation(Layer1) | Framing QA v2 | overall_status |
|---|---|---|---|---|---|
| A2 | PASS(1回目) | **REVIEW_REQUIRED**(一般化の強さ、捏造なし) | LEDGER_COMPLIANT | PASS(6項目0件) | **NG_REVIEW_REQUIRED** |
| B1 | PASS(バグ修正後1回目) | PASS | LEDGER_COMPLIANT | PASS(6項目0件) | **PASS** |

- A2のFact Checker A' REVIEW_REQUIRED理由: 5件とも捏造ではなく**一般化の
  行き過ぎ**の指摘("Cleaning may happen more often because it is easier
  to start"のような記述が、少数世帯対象の研究知見を家庭用ロボット一般の
  因果として一般化しすぎている、等)。Trial-01の「数値の精度」問題とは
  異なる種類だが、**Fact Checker A'が今回も正しく機能した実例**である
  (「安全≠成功」原則どおり、精度指摘を無視して合格扱いにしていない)。
- B1は全QA・編集Gateを完全PASS。

### 評価表(0〜2点、主観、指示書指定の8観点。引用は`comparison.md`本体)

| 観点 | A2 | B1 |
|---|---|---|
| 面白さ | 2 | 2 |
| Futureらしさ | 2 | 2 |
| 研究解説っぽさの不在 | 2 | 2 |
| 事実と想像の区別 | 2 | 2 |
| throughline | 2 | 2 |
| 1ナレーターの自然さ | 2 | 2 |
| 時間軸の明示 | 2 | 2 |
| 希望/不安の描写 | 2 | 2 |
| **合計** | **16/16** | **16/16** |

全文・引用根拠・World Scaffold・Layer2/3(v2)・Trial-01との定性比較は
`er013_output/family_c_future_trial_02/comparison.md`
(`index.html`も同内容)を参照。

### 定性的な確認事項(指示書の狙いが実現したか)

- 冒頭が生活場面から始まる: A2/B1とも確認(編集Gate`opening_paragraph_
  numeric_hits=0`かつ`opening_paragraph_research_hits=0`)。
- "study/research/survey/report found"型表現: A2/B1とも0件
  (`research_term_hits=[]`)。
- 製品名列挙: A2/B1とも0件(World Scaffold抽出22件との突合で
  `product_name_hits=[]`)。
- 時点数・間隔: Layer2/3(v2)が提案した3時点(around 2030/2035/2040)を
  Writerがそのまま使わず、A2は独自に2030/2040/2050、B1は2035/2045/2055を
  選択した。機械的な当てはめではなく、Writer自身が理由を`[[META]]`へ
  記録している(A2: "This path makes the emotional shift visible..."、
  B1: "This creates a clear path from excitement...to the deeper
  tension...")。
- FACT例外枠(現在事実の明示、最大2件): A2/B1とも**0件**で完結した。
  World Scaffold経由の暗黙のグラウンディングのみで、読者への直接説明
  なしに未来像を成立させられることを示す実例。

## 6. Fact Safety確認(緩和していないことの根拠)

Fact Checker A'(`r3.run_fact_checker_with_gates`)・Ledger Deviation
Checker(`vfl01.run_deviation_check`、`hook_aware=False`)は、Trial-01と
完全に同一の関数・呼び出し方法(無改変)を使用した。判定対象
(`layer1_text_for_fact_check`、想像パッセージ[[IMAGINED]]をプレース
ホルダ化した「枠外」テキスト)の構築ロジックも、マーカー体系が
META/FACTへ拡張された点を除き同一方式(想像パッセージの完全除外)を
踏襲した。A2でFact Checker A'が実際にREVIEW_REQUIREDを検出したことは、
判定が形骸化していないことの実測上の証拠である。捏造検出用のFraming
QA v2の`fabricated_present_facts`項目もA2/B1とも0件(捏造なし、想像枠内
の記述はいずれも正当な想像として判定された)。

## 7. 残る問題・限界

1. A2はFact Checker A'がREVIEW_REQUIREDのため、人手レビューなしでは
   Production採用相当として扱えない(Gate 1材料としては安全装置が正しく
   機能した実例)。
2. 編集Gateの決定的スキャンに、未来年+文末記号の組み合わせによる誤検出
   バグがあり、実データ実行中に発見・修正した(§3参照)。今回のテーマ・
   文体では解消したが、他の言語パターン(未来年の直後にダッシュ・括弧等が
   続く場合等)で同種の誤検出が残る可能性は否定できない。
3. 読者向け本文のマーカー除去箇所に、空行が2〜3行連続する軽微な整形
   アーティファクトが残る(Trial-01から継続する既知の限界、Audio化時は
   事前クレンジングが必要)。
4. baselineなし(Trial-01と同様、2記事構成のみ)。同一テーマ・同一Layer1
   Ledgerでの前後比較(本レポート§5・comparison.md)がbaseline相当を
   兼ねると判断した。
5. World Scaffold生成・Layer2/3(v2)生成はいずれも新設のTrial専用process
   であり、既存`PROCESS_MODEL_MAP`には未登録(Trial-01と同一方針、
   `vfl01.MODEL`を直接指定。SSOT routing契約ファイルへの新規process登録・
   改変は行っていない)。

## 8. Dangling Reference・A/B-Family無影響・retry/fallback整合の確認

- Dangling Reference: 本Trialの新規ファイル(`er013_family_c_future_
  scaffold_02.py`/`_ledger_02.py`/`_writer_02.py`/`_qa_02.py`/
  `_qa_test_02.py`/`_trial_02_run.py`)は、Trial-01の`_01`ファイル群を
  読み取り専用でimportするのみで、`_01`ファイル自体は無編集のまま残る
  (Trial-01のGate 1判定材料としての有効性に影響なし)。
- A/B-Family無影響: §3の通り、default全件回帰(2512件)でA/B-Family・
  Discovery関連の失敗は0件(失敗3件は既知の無関係な履歴カウントテスト)。
  静的にもA-Family/B-Family/Discoveryのいずれのファイルもimportしていない。
- retry/fallback整合: Local Rewrite(`er010_ledger_local_rewrite_09`)は
  Trial-01と同一の無改変再利用、cycle上限もTrial-01と同じ保守的な1
  (Production[3]より厳しい安全側の値)。編集Gate起因のWriter再生成は
  最大1回(指示書§作業A-5「retry 1回」通り)、上限到達後もFact Checker
  A'/Deviation/Framing QAはそのまま実行し(スキップせず)、editorial_
  gate_final_status=FAILの場合はoverall_status=NG_REVIEW_REQUIREDとして
  記録する設計とした(既存の安全装置を独自に回避・無効化していない)。

## 9. ユーザー判断事項

- A2(NG_REVIEW_REQUIRED、Fact Checker A'の一般化指摘)・B1(PASS)を
  Gate 1判定材料としてどう扱うか。
- 本Trialの設計変更(World Scaffold・編集Gate・Framing QA v2・META/FACT
  マーカー)をFamily Cの正式仕様候補として今後どう扱うか(SSOT反映は
  ユーザー承認後)。

## 10. SSOT追記文案(編集していない、ユーザー承認後の反映用)

`CURRENT_SPEC.md`への追記案(未反映、案のみ):

> ## Family C(Future、独立経路、再設計Trial検証済み)
> `EDITORIAL-FUTURE-FAMILY-C-REDESIGN-TRIAL-02`(2026-09-13)で、
> Trial-01の「研究・データ解説っぽさ」の問題に対し、World Scaffold
> (Layer1の生の統計・出典・製品名を含まない言い換え)経由でのみWriterへ
> 情報を渡す設計・完成記事の編集Gate(決定的スキャン)・Future Framing
> QA v2(6項目)・META/FACT/IMAGINEDマーカー体系を追加した。A2は
> NG_REVIEW_REQUIRED(Fact Checker A'の一般化指摘)、B1は全QA PASS。
> **Production未配線**(Trial止まり、`APPROVED_FOR_PRODUCTION`ではない)。

`DECISION_LOG.md`への追記案(未反映、案のみ):

> 2026-09-13 EDITORIAL-FUTURE-FAMILY-C-REDESIGN-TRIAL-02: Family C
> (Future)をドラスティックに再設計(World Scaffold・編集Gate・Framing
> QA v2・META/FACTマーカー)し、同一テーマ「家庭用ロボットと家事」で
> A2/B1各1本を再生成(実費¥20.08、上限¥159.17、Research/Verificationは
> Trial-01成果物を再利用)。B1は全QA・編集Gate PASS、A2はFact Checker A'
> がREVIEW_REQUIRED(一般化指摘、捏造なし)。Trial-01の完成記事を新設
> 編集Gateへ入力する回帰テストでFAILになることを確認し、設計変更が
> 実際に問題を検出できることを確認した。Production採用は別途ユーザー
> 判断。

## 11. 成果物一覧

- 本ファイル(root)
- `er013_family_c_future_scaffold_02.py` / `_ledger_02.py` / `_writer_02.py`
  / `_qa_02.py` / `_qa_test_02.py` / `_trial_02_run.py`(全て新規、
  Trial-01の`_01`ファイルは無編集で保持)
- `er013_output/family_c_future_trial_02/`(research/a2/b1/comparison.md
  /index.html/cost_summary.json/raw_usage_log.jsonl)
- `docs/pm/RESULT_PACKET_FC2.md`
