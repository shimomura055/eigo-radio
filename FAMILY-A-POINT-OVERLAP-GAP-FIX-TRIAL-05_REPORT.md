# FAMILY-A-POINT-OVERLAP-GAP-FIX-TRIAL-05 報告書

管理ID: FAMILY-A-POINT-OVERLAP-GAP-FIX-TRIAL-05(Lane A)。
**Trial(Production実装ではない)。Production/Prompt/SSOT編集・Git操作は
一切行っていない。monkeypatch・グローバル書き換えなし。TTSは実行して
いない(text-onlyまで)。閾値(0.40)・`POINT_OVERLAP_ARTICLE_RETRY_MAX`
(2)・retry判定ロジック(`lexical_flagged`/`still_flagged`)は一切変更
していない。** 並列稼働中のSSOT統合タスク(SSOT・Git担当)の成果物は
参照していない。`docs/pm/ACTIVE_TASK.md`/`RESULT_PACKET.md`は編集して
いない。

背景: `FAMILY-A-POINT-OVERLAP-COUNTERMEASURE-PRE-AUDIT-01_REPORT.md`が
発見した2つの実装ギャップ、G1(Diagnostic Full Retry診断promptで前回
Point本文がハードコードされたプレースホルダーのまま実テキストが渡って
いない)・G2(`cross_point_overlap`が計算されているのにretry判定にも
診断promptにも未使用)について、ユーザーが2026-09-09に、大規模な(a)/(b)
比較Trialではなく本ギャップ修正のみの小規模Trialを指示した。ただし
「G1/G2それぞれ、過去の正式承認仕様との対応関係を確認してから進める」
というReconciliation Check先行の条件付きだった。

---

## Step 1: Reconciliation Check

### G1: 前回Point本文の診断promptへの埋め込み

**該当コード**: `er009_diagnostic_full_retry_modules_12.py::build_diagnostic_
section()`(89-108行)。`DIAGNOSTIC_SECTION_TEMPLATE`(60-86行)自体には
`{previous_point_one}`/`{previous_point_two}`という、`{previous_full_story}`
と同じ構造のplaceholderスロットが存在するが、実際に渡される値は
ハードコードされたリテラル文字列`"(Point One body from previous
attempt)"`/`"(Point Two body from previous attempt)"`(99行・103行)。

**承認済み設計との対応関係**: `git log -S`で本module追加commit(`f46b6e1`、
2026-08-30、コミットメッセージ「ER-009-N1-DIAGNOSTIC-FULL-RETRY-
PRODUCTION-12: Diagnostic Full Retry検証完了・Production統合準備」)を
確認したところ、この**同一commit**で2ファイルが同時に追加されていた。

1. `er009_n1_diagnostic_full_retry_production_12.py`(実際にNo.9 A2で
   runtime検証したscript、DECISION_LOG.md`ER-009-N1-DIAGNOSTIC-FULL-
   RETRY-CLOSEOUT-14`が引用する実測結果[Point Overlap Initial
   0.545/0.519→Retry1 0.25/0.367、Design比較でPoint Role Planning
   0/3 PASS vs Diagnostic Full Retry 3/3 PASSの根拠]の元になった
   script)は、`generate_full_article_diagnostic_retry()`内で
   `previous_point_one=previous_article["point_one_body"]`/
   `previous_point_two=previous_article["point_two_body"]`と、**実際の
   前回Point本文を正しく渡していた**(186行・190行)。
2. 同じ設計の元になった前段Trial`er009_n1_diagnostic_retry_11.py`
   (192行・196行)も同様に実テキストを渡していた。
3. Production本体(`er003_v1_n3_01_articles_generate.py`)が実際にimport
   するのは、**この検証済みscriptではなく**、同一commitで並行して
   作られた「module化形式」`er009_diagnostic_full_retry_modules_12.py`
   の方であり、このmodule化の際にのみ、実テキストの受け渡しが
   ハードコードされたプレースホルダー文字列へ**後退**していた。
   加えて、Production側の呼び出し元`build_diagnostic_retry_prompt()`
   (`er003_v1_n3_01_articles_generate.py` 611-627行)は、`sections =
   split_common_sections_for_point_qa(previous_article_text)`で
   `sections["point_one_body"]`/`sections["point_two_body"]`を既に
   抽出済みであるにもかかわらず、それらを`build_diagnostic_section()`
   へ渡していない(抽出はしているのに使っていない、という二重の配線
   漏れ)。

DECISION_LOG.md`ER-009-N1-DIAGNOSTIC-FULL-RETRY-CLOSEOUT-14`
(2026-08-31)自体には「前回Point本文を渡す」という文言の直接引用は
無いが、この決定が引用する実runtime evidence(3/3 PASS、Household実発火
確認)の元になったscriptが実テキストを渡していたことが今回のcommit
調査で確認できた以上、**「前回Point本文を渡す」は承認・検証済み設計の
一部であり、module化時に配線が失われた実装漏れ**と判定する。

**判定: G1 = 実装漏れ(承認済み範囲内)。仕様追加ではない。**

### G2: `cross_point_overlap`の診断promptへの追加

**該当コード**: `run_point_overlap_qa_and_regenerate()`
(`er003_v1_n3_01_articles_generate.py` 675-743行)が`cross_point_overlap`
(Point One⇔Point Two相互overlap)を計算している(710行)。一方、
`run_one_pattern()`のretry判定`lexical_flagged`(863-865行)は
`before_overlap`(Point vs Full Story)のみを見ており、`cross_point_
overlap`のflagは判定に含まれていない。診断prompt構築
(`build_diagnostic_retry_prompt()`)へ渡す`point_overlap_result`
(903-906行)も`before_overlap`のみで、`cross_point_overlap`の値・
共有語は一切含まれない。

**承認済み設計との対応関係**: `CURRENT_SPEC.md`「Point One対Point Twoの
lexical overlap検査(追加ペア)」行(ER-011-NO18-PRODUCTION-SPEC-
IMPROVEMENT-01、`DECIDED`/`PRODUCTION_WIRED`)を確認したところ、
承認されている内容は以下の通り引用できる:

> ユーザーが正式決定し、同一の`overlap_qa.flag_possible_paraphrase()`
> (閾値0.40、新規関数は作らない)をPoint One⇔Point Two間にも双方向で
> 追加適用した。既存のFull Story対Point One/Twoチェックと同じ
> `still_flagged`判定・同じDiagnostic Full Retryループへ統合済み
> (新しい別のretry機構は作らない)

この文面が承認しているのは「`cross_point_overlap`を既存の`still_flagged`
判定(=retry判定トリガー)へ統合すること」のみである。実装を確認すると、
`still_flagged`(886行)は`lexical_flagged or value_qa_flagged`であり、
`lexical_flagged`自体が`cross_point_overlap`を含んでいないため、
**この承認済み設計(retry判定への統合)自体も実際には未実装のまま**
であることが判明した(CURRENT_SPEC.mdの「統合済み」という記述と実装が
食い違っている)。

一方、本Trialのユーザー指示は「retry判定への使用は今回対象外(閾値・
Loop Budget不変のため)、診断promptへの追加のみ実施」というものだった。
しかし、上記の承認済み文面には「`cross_point_overlap`の値・共有語を
**診断prompt本文のテキストとして明示的に追加する**」ことへの言及が
一切ない(承認されているのはretry判定トリガーとしての統合のみ)。
ER-011-NO18-PRODUCTION-SPEC-IMPROVEMENT-01の他の記述(Point Value QA
NG理由は診断section直後に追加する、という文言)を確認しても、
`cross_point_overlap`を診断prompt本文へ追加するという設計は見当たらない。
また、`cross_point_overlap`をretry判定に使わないまま診断prompt本文にだけ
追加すると、「retryが発火した理由(before_overlapのflag)」と「診断
prompt内に表示される理由」が一致するとは限らず、Writerへの説明として
不完全・中途半端になる懸念もある(retry判定へ統合して初めて意味を持つ
情報を、判定と無関係に一部だけ表示することになる)。

**判定: G2(診断promptへの追加) = 仕様追加候補。承認済み記録に明記が
ない。本Trialでは実装しない(除外)。**

なお、`cross_point_overlap`をretry判定(`still_flagged`)へ統合すること
自体は、CURRENT_SPEC.mdが「統合済み」と誤って記載している通り**承認済み
仕様でありながら未実装**という別の実装漏れが今回判明したが、これは
ユーザーが本タスクで明示的に対象外とした「retry判定への使用」に該当する
ため、本Trialでは変更していない(別途`USER_DECISION_REQUIRED`として
報告、§4参照)。

---

## Step 2: Trial実装(G1のみ)

新規ファイル`er011_point_overlap_gap_fix_trial_05.py`(root)。

- `build_diagnostic_section_gapfix()`: `diagnostic_mod.build_diagnostic_
  section()`のコピー改変版。`DIAGNOSTIC_SECTION_TEMPLATE`自体・
  `classify_overlap()`/`compose_diagnosis()`は無変更のままimportし、
  `previous_point_one`/`previous_point_two`へハードコードされた
  プレースホルダーではなく実際の前回Point本文を渡すことのみ変更。
- `build_diagnostic_retry_prompt_gapfix()`: `prod_gen.split_common_
  sections_for_point_qa()`(Production関数、無変更)が既に抽出している
  `point_one_body`/`point_two_body`を、`build_diagnostic_section_
  gapfix()`へ渡すことのみ追加。
- `run_one_pattern_gapfix()`: `prod_gen.run_one_pattern()`のコピー改変版。
  Diagnostic Full Retry prompt構築の呼び出し先を`build_diagnostic_
  retry_prompt_gapfix()`へ差し替える1箇所のみが変更点(それ以外は全て
  `prod_gen.*`経由でProduction関数[`run_point_overlap_qa_and_regenerate`/
  `_generate_and_compress_article`/`compute_metrics`/`run_deviation_
  check`/`build_fact_check_prompt`/`run_fact_checker_with_gates`/
  `audit_article_directional_facts`/local_rewrite一式/`run_point_role_
  planning`/`run_point_value_qa`/`normalize_article_formatting`]をその
  まま呼ぶ)。monkeypatch不使用(コピー関数として実装、既存関数のパッチ
  ではない)。
- baseline条件は`prod_gen.run_one_pattern`を完全に無変更のまま直接呼ぶ
  (コピーではなく正真正銘のProduction経路)。

**単体テスト2件、実行しPASS確認**(`python er011_point_overlap_gap_fix_
trial_05.py test`):
1. `test_g1_gapfix_only_differs_by_point_body_text`: 合成fixtureで、
   G1修正版の診断promptからbaseline側のプレースホルダー文字列2箇所を
   逆置換すると、baseline側の出力とバイト完全一致することを確認
   (=差分が前回Point本文の埋め込み以外に存在しないことの動的証明)。
2. `test_run_one_pattern_gapfix_matches_production_except_diagnostic_
   call`: `inspect.getsource()`で`prod_gen.run_one_pattern`と
   `run_one_pattern_gapfix`のソースを取得し、意図した1箇所(診断prompt
   構築の呼び出し)を正規化した上で行単位diffを取り、**完全一致**する
   ことを確認(=retry判定・閾値・Loop Budget・その他ロジックを一切
   変更していないことの静的証明)。

両テストともPASS(実行ログ: `[GAPFIX-05][tests] all_pass=True`)。

---

## Step 3: 実行・計測

### 3.1 費用と縮退(N=3→N=2)

実測費用(`cl.install()`実測、`er011_point_overlap_gap_fix_trial_05_cost_
compute.py`、`er005_output/cost_baseline_01/pricing_snapshot.json`単価)。
N=3(run1〜3、18本)を予定していたが、run1(6本、¥62.2)+run2(6本、
¥117.8、累計¥180.0)の時点で1本あたり平均が上昇傾向(theme2側で
Fact Checker/Ledger Deviation/Directional Precheckまで到達するrunが
増え、web_search呼び出し込みで1本¥15〜35に達する例が複数発生)であり、
run3をそのまま実行すると上限¥200を明確に超過する見込みとなったため、
**ユーザー指示通りrun3を実施せずN=2へ縮小した**(Hanshin gapfix・
Theme2 baseline・Theme2 gapfixの新規生成4条件×2レベルをN=2で確定、
Hanshin baselineのみ再利用によりN=3のまま)。

**最終実測費用: 合計¥180.0**(上限¥200以内、133 API call)。
内訳(`by_target_theme_jpy`): Hanshin(gapfixのみ新規)¥32.8、
Theme2(baseline+gapfix)¥147.1。`by_condition_jpy`:
hanshin_gapfix ¥32.8、theme2_baseline ¥78.9、theme2_gapfix ¥68.3。
Theme2側が高いのはFact Checker(Web検索)・Ledger Deviation・
Directional Fact Precheckまで到達する頻度がHanshin側より高かった
ため(§3.2参照)。TTS/ASRは未実行(text-onlyのみ、`provider=openai`
以外が記録された場合はcost_compute側がValueErrorで停止する設計、
実際に停止は発生しなかった)。

### 3.2 結果一覧(18本、Hanshin baselineはTrial-04からの再利用N=3、他はN=2)

| theme | condition | level | run | source | status | retry | 最終lex flag | 最終value_qa flag | fact_verdict | ledger_status(count) | dir_precheck | P1 overlap | P2 overlap | cross(1→2/2→1) | 語数 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hanshin | baseline | A2 | 1 | reused | NG | 2 | True | False | - | - | - | 0.444 | 0.333 | 0.333/0.30 | 248 |
| hanshin | baseline | A2 | 2 | reused | NG | 2 | True | True | - | - | - | 0.621 | 0.536 | 0.241/0.25 | 260 |
| hanshin | baseline | A2 | 3 | reused | NG(fact=FAIL) | 2 | False | False | FAIL | - | - | 0.37 | 0.241 | 0.074/0.069 | 262 |
| hanshin | gapfix | A2 | 1 | new | NG | 2 | True | False | - | - | - | 0.472 | 0.5 | 0.167/0.231 | 253 |
| hanshin | gapfix | A2 | 2 | new | NG(fact=FAIL) | 1 | False | False | FAIL | - | - | 0.233 | 0.241 | 0.033/0.034 | 220 |
| hanshin | baseline | B1B | 1 | reused | OK | 0 | False | False | PASS | LEDGER_COMPLIANT(0) | PASS | 0.241 | 0.355 | 0.138/0.129 | 241 |
| hanshin | baseline | B1B | 2 | reused | NG | 2 | False | True | - | - | - | 0.379 | 0.267 | 0.0/0.0 | 264 |
| hanshin | baseline | B1B | 3 | reused | OK | 2 | False | False | PASS | LEDGER_COMPLIANT(0) | DIRECTION_REVIEW_REQUIRED | 0.28 | 0.303 | 0.08/0.061 | 288 |
| hanshin | gapfix | B1B | 1 | new | NG | 2 | False | True | - | - | - | 0.275 | 0.37 | 0.075/0.111 | 306 |
| hanshin | gapfix | B1B | 2 | new | NG | 2 | True | True | - | - | - | 0.41 | 0.6 | 0.179/0.233 | 289 |
| theme2 | baseline | A2 | 1 | new | OK | 1 | False | False | REVIEW_REQUIRED | LEDGER_COMPLIANT(1) | DIRECTION_REVIEW_REQUIRED | 0.268 | 0.29 | 0.098/0.129 | 318 |
| theme2 | baseline | A2 | 2 | new | NG | 2 | True | False | - | - | - | 0.405 | 0.278 | 0.135/0.139 | 305 |
| theme2 | gapfix | A2 | 1 | new | NG | 2 | True | False | - | - | - | 0.289 | 0.405 | 0.158/0.162 | 315 |
| theme2 | gapfix | A2 | 2 | new | OK | 1 | False | False | REVIEW_REQUIRED | LEDGER_COMPLIANT(0) | PASS | 0.231 | 0.179 | 0.179/0.179 | 298 |
| theme2 | baseline | B1B | 1 | new | NG | 2 | False | True | - | - | - | 0.344 | 0.357 | 0.094/0.071 | 385 |
| theme2 | baseline | B1B | 2 | new | OK | 1 | False | False | REVIEW_REQUIRED | LEDGER_COMPLIANT(1) | DIRECTION_REVIEW_REQUIRED | 0.265 | 0.353 | 0.029/0.029 | 385 |
| theme2 | gapfix | B1B | 1 | new | NG | 2 | True | True | - | - | - | 0.242 | 0.595 | 0.121/0.095 | 334 |
| theme2 | gapfix | B1B | 2 | new | OK | 0 | False | False | REVIEW_REQUIRED | LEDGER_COMPLIANT(0) | PASS | 0.229 | 0.314 | 0.086/0.086 | 345 |

閾値0.40(既存Production既定、変更なし)。詳細は各`analysis.json`/
`point_overlap_article_retry_log.json`参照。

### 3.3 集計(条件別NG率・retry回数)

| theme | condition | level | n | NG率 | retry平均 | Diagnostic Full Retry発火数 |
|---|---|---|---|---|---|---|
| hanshin | baseline | A2 | 3 | 100%(3/3) | 2.0 | 3 |
| hanshin | gapfix | A2 | 2 | 100%(2/2) | 1.5 | 2 |
| hanshin | baseline | B1B | 3 | 33%(1/3) | 1.33 | 2 |
| hanshin | gapfix | B1B | 2 | 100%(2/2) | 2.0 | 2 |
| theme2 | baseline | A2 | 2 | 50%(1/2) | 1.5 | 2 |
| theme2 | gapfix | A2 | 2 | 50%(1/2) | 1.5 | 2 |
| theme2 | baseline | B1B | 2 | 50%(1/2) | 1.5 | 2 |
| theme2 | gapfix | B1B | 2 | 50%(1/2) | 1.0 | 1 |

**Diagnostic Full Retryは18本中16本(89%)で実発火**(不発火はtheme2
gapfix B1B run2の1本のみ、初回で全QA通過)。修正の効果を評価できる
機会は十分にあった。

### 3.4 NG_REVIEW_REQUIREDの原因内訳(12本、G1が寄与しうる範囲の切り分け)

NG 12本のうち、最終attemptで:
- **lexical overlapのみ未解消**(`final_lex=True`かつ`final_val=False`、
  G1の診断改善が直接効きうる範囲): 4本
  (hanshin baseline A2 run1、hanshin gapfix A2 run1、
  theme2 baseline A2 run2、theme2 gapfix A2 run1)
- **lexical・value QA両方未解消**: 3本
  (hanshin baseline A2 run2、hanshin gapfix B1B run2、
  theme2 gapfix B1B run1)
- **Point Value QAのみ未解消**(`final_lex=False`かつ`final_val=True`、
  G1はlexical overlap診断のみの修正のためこのfailure modeには無関与):
  3本(hanshin baseline B1B run2、hanshin gapfix B1B run1、
  theme2 baseline B1B run1)
- **Fact Checker FAIL**(lexical/value QAはむしろ解消済み、Point Overlap
  機構とは独立した別stageでの停止、G1と無関係): 2本
  (hanshin baseline A2 run3、hanshin gapfix A2 run2)

NG 12本中5本(42%)は、そもそもG1が触れる範囲(lexical overlap診断)の
外側の原因(Value QA単独 3本、Fact Checker FAIL 2本)で発生しており、
G1修正の有無に関わらず解消しない。G1が理論上寄与しうる「lexical
overlapが最後まで未解消」の7本(pure 4本+両方未解消3本)についても、
baseline側3本・gapfix側4本と、明確な改善方向は確認できなかった
(§3.5参照)。

### 3.5 収束軌跡の定性観察(N=2による示唆、統計的検証ではない)

各attemptのoverlap ratio推移を見ると、gapfix側で「1回のretryで
lexical overlapが大きく低下し解消する」明確な収束例が複数観測された:
- hanshin gapfix A2 run2: attempt0(P1=0.652, P2=0.367)→
  attempt1(P1=0.233, P2=0.241)で一気に解消、そのままOK到達。
- theme2 gapfix A2 run2: attempt0(P1=0.615, P2=0.464)→
  attempt1(P1=0.231, P2=0.179)で一気に解消、そのままOK到達。
- hanshin gapfix B1B run1: attempt0(P1=0.652, P2=0.519)→
  attempt1(P1=0.342, P2=0.261)で大きく改善(lexicalは解消、
  value QAのみ残存)。

一方、gapfix側でも収束しない・悪化する例がある(hanshin gapfix B1B
run2: attempt0→2でP2が0.281→0.6と悪化して終了。theme2 gapfix B1B
run1: attempt0→2でP2が0.438→0.595と悪化)。baseline側(旧プレース
ホルダー版)でも同様に非単調な例が見られる(hanshin baseline A2 run2:
attempt0(0.375)→attempt2(0.621)とむしろ悪化して終了。theme2
baseline A2 run2: attempt1(0.342)→attempt2(0.405)と悪化)。

**判定**: gapfix側に「1回のretryで大きく改善し即座に解消する」明確な
成功例が複数(3/7)観測された一方、baseline側の観測範囲(本Trialで
実際に確認した6本)には同程度に劇的な単発収束例は無かった。これは
G1修正が効いている可能性を示唆する定性的傾向ではあるが、**双方の
条件とも非単調・悪化する例も残っており、N=2(gapfix)/N=3(baseline
再利用)という小standardサンプルでは、この傾向が偶然のrun間分散を
超えて再現的かどうかは統計的に確定できない**(Trial-04報告書の
「N=3では方向性を確定できない」という先例と同種の限界)。

### 3.6 事実逸脱・自然さ・レベル間差

- **Fact Checker/Ledger Deviation**: OK到達5本(hanshin B1B×2[baseline
  reused]、theme2 A2×2[baseline1+gapfix1]、theme2 B1B×2[baseline1+
  gapfix1])はいずれもLedger Deviationが`LEDGER_COMPLIANT`(MAJOR
  0件、MINOR最大1件)で、Fact Checkerは`PASS`または`REVIEW_REQUIRED`
  (non-blocking advisory、既存方針通り)。`FAIL`(blocking)が2本
  (hanshin baseline A2 run3・hanshin gapfix A2 run2)で発生したが、
  いずれもPoint Overlap機構とは独立したFact Checker側の既存挙動
  (既知の非決定性、CURRENT_SPEC.md記載のOPEN-92と同種)であり、G1
  修正との関連は確認されなかった。
- **自然さ(簡易目視確認)**: OK到達した記事本文(例:
  `hanshin/a2/gapfix/run2/article.md`、`theme2/a2/gapfix/run2/
  article.md`)を通読したところ、いずれも自然な英語の記事として
  問題なく、診断prompt由来のテキスト漏れ(プレースホルダー文字列や
  診断メタ情報の混入)は本文中に一切確認されなかった(診断section
  はWriterへの入力promptにのみ追加され、出力される記事本文の構造
  [Title/Main Story/Point見出し/In one line]には現れない設計のため、
  想定通り)。
- **A2・B1B差**: 明確な系統差は確認できなかった(NG率はA2の方が
  やや高い傾向[hanshin A2 100%×2条件 vs B1B 33%〜100%とばらつき大]
  だが、N=2〜3では確定的な結論を出せない)。
- **語数**: 220〜385語の範囲(既存target/tolerance rangeからの
  逸脱によるhard failureは0件)。

### 3.7 Trend Synthesis(Theme 2)・通常News(Hanshin)への副作用

`editorial_type_module_block`の解決(`prod_gen.resolve_editorial_
type_module_block()`)は、baseline/gapfix両条件で共有ハーネスコード
(`run_one_combo`)内の同一呼び出しであり、`run_one_pattern_gapfix`
の変更箇所(Diagnostic Full Retry prompt構築)より前段で完了して
いるため、G1修正が`editorial_type_module_block`の内容・挿入箇所へ
影響する余地は構造的に無い(静的diffテスト`test_run_one_pattern_
gapfix_matches_production_except_diagnostic_call`がこれを担保)。
実データでも、Theme 2(trend_synthesis mode)側4条件・Hanshin(mode
指定なし通常News)側4条件のいずれでも、記事の構造的異常(見出し欠落・
Point構造崩れ・Trend Synthesis特有の言い回しの欠落等)は観測され
なかった。

---

## Step 4: 判定

### Gate 4(Production無変更、Trial-only依存なし)

**PASS**。`er003_v1_n3_01_articles_generate.py`/`er009_diagnostic_
full_retry_modules_12.py`/`er008_point_overlap_qa_18.py`/`er011_
point_role_value_planning_01.py`等はいずれもimportのみで無編集
(grep差分なし)。monkeypatch・グローバル書き換えなし。`run_one_
pattern_gapfix()`は`prod_gen.run_one_pattern()`のコピー関数であり、
静的diffテスト(`inspect.getsource()`による行単位比較)で意図した
1箇所(Diagnostic Full Retry prompt構築の呼び出し先)以外の差分が
無いことを機械的に確認済み。閾値(0.40)・`POINT_OVERLAP_ARTICLE_
RETRY_MAX`(2)・retry判定ロジック(`lexical_flagged`/`still_flagged`)
は無変更。G2(仕様追加候補と判定)は実装していない。Git操作なし。

### Gate 1分類: **USER_DECISION_REQUIRED**

理由:
1. NG率・avg retry・収束軌跡のいずれも、gapfix条件がbaseline条件より
   系統的に優れているとは言い切れない(§3.3・3.5、レベル・テーマに
   よって方向がまちまち)。
2. gapfix側に「1回のretryで劇的に収束する」明確な成功例が複数観測
   された(§3.5)ことは、G1修正(実Point本文をWriterへ実際に見せる)
   が機能している可能性を示す肯定的なシグナルではあるが、同程度に
   非単調・悪化する例も残っており、N=2(新規生成4条件)という小標本
   では「再現的な改善」と結論づけるだけの統計的根拠がない。
3. NG_REVIEW_REQUIRED全体の42%(12本中5本)は、そもそもG1が対象と
   しないfailure mode(Point Value QA単独・Fact Checker FAIL)に
   起因しており、G1修正だけでは既存の高NG率問題を解消しきれない
   ことが明確になった(これは既知の限界であり、当初のPre-Auditの
   予想通り)。
4. 新規failure mode・重大な副作用は観測されなかった(§3.6・3.7)。
5. G1がProduction承認済み設計からの実装漏れであることはReconciliation
   Check(§1)で確定しているため、「実装すべきか」自体はUSER_DECISION
   ではなく、「今回の限定的な実データで観測された効果の大きさを踏まえて
   どう配線するか(単独配線か、Value QA診断の同時強化とセットにするか
   等)」がユーザー判断事項となる。

### Production配線案(G1、実装しない)

- **修正箇所**: `er009_diagnostic_full_retry_modules_12.py::build_
  diagnostic_section()`の`previous_point_one`/`previous_point_two`
  引数へ、呼び出し元(`er003_v1_n3_01_articles_generate.py::build_
  diagnostic_retry_prompt()`)が既に保有している`sections["point_one_
  body"]`/`sections["point_two_body"]`を渡すよう、関数shape変更
  (`build_diagnostic_section(previous_article_text, point_one_overlap,
  point_two_overlap)` → `previous_point_one_text`/`previous_point_
  two_text`引数を追加)。本Trialの`build_diagnostic_section_gapfix()`/
  `build_diagnostic_retry_prompt_gapfix()`がそのままProduction実装の
  参考実装になる(コピーではなく、Production関数自体を書き換える形)。
- **G2(仕様追加候補、診断promptへの追加)は実装しない**。ただし
  Reconciliation Checkで判明した「`cross_point_overlap`のretry判定
  [`still_flagged`]統合は`CURRENT_SPEC.md`上は`DECIDED`/`PRODUCTION_
  WIRED`と記載されているが実装が伴っていない」という不整合は、G2とは
  独立の課題として別途`USER_DECISION_REQUIRED`で報告する(§4「回帰
  テスト案」直後に記載)。
- **回帰テスト案**: (1)本Trialの`test_g1_gapfix_only_differs_by_
  point_body_text`と同型の単体テストをProduction側`er009_diagnostic_
  full_retry_modules_12.py`のテストへ追加し、修正後の`build_
  diagnostic_section()`が実際にPoint本文を埋め込むことを固定する。
  (2)`run_project_regression.py`の既存Diagnostic Full Retry関連
  regressionの再実行。(3)No.9等、既に`PRODUCTION_WIRED`として承認
  済みの記事のGit保全版に対し、`article_text`が変わらないことを
  sha256等で確認する退行防止チェック(既存記事のDiagnostic Full Retry
  自体が発火していない場合は影響なし)。

### 別途USER_DECISION_REQUIRED(本Trialのスコープ外だが発見事項として報告)

`CURRENT_SPEC.md`「Point One対Point Twoのlexical overlap検査
(追加ペア)」行が「既存のFull Story対Point One/Twoチェックと同じ
`still_flagged`判定・同じDiagnostic Full Retryループへ統合済み」と
記載しているにもかかわらず、実装(`run_one_pattern()`の`lexical_
flagged`)は`cross_point_overlap`を含んでいない(§1 G2節)。これは
G2(診断promptへの追加)とは別の、**CURRENT_SPEC.mdの記載と実装の
不一致**であり、(a)記載通りに実装を追加するか、(b)記載を実態に
合わせて修正するか、ユーザー判断が必要。

---

---

## 新規ファイル一覧

- `er011_point_overlap_gap_fix_trial_05.py`(Trial本体、G1修正版
  `build_diagnostic_section_gapfix`/`build_diagnostic_retry_prompt_
  gapfix`/`run_one_pattern_gapfix`、単体テスト2件、実行・集計ハーネス、
  `cl.install()`を`__main__`冒頭で必ず呼ぶ)
- `er011_point_overlap_gap_fix_trial_05_cost_compute.py`(費用集計、
  Trial-04 cost_computeと同一ロジック・同一pricing snapshot参照)
- `er011_output/point_overlap_gap_fix_trial_05/`
  (`hanshin/{a2,b1b}/baseline/run{1..3}/`は再利用元へのポインタのみ
  [`analysis.json`/`reused_from.txt`、新規生成なし]、
  `{hanshin,theme2}/{a2,b1b}/gapfix/run{1,2}/`・
  `theme2/{a2,b1b}/baseline/run{1,2}/`は新規生成記事一式、
  `all_analyses.json`、`aggregate_summary.json`、`raw_usage_log.jsonl`、
  `cost_summary.json`)
- `FAMILY-A-POINT-OVERLAP-GAP-FIX-TRIAL-05_REPORT.md`(本ファイル)

Git操作・Production/Prompt/SSOT編集は一切行っていない。
