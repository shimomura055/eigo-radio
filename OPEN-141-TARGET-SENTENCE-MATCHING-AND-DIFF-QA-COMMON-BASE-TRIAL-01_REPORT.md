# OPEN-141-TARGET-SENTENCE-MATCHING-AND-DIFF-QA-COMMON-BASE-TRIAL-01_REPORT

管理ID: OPEN-141-TARGET-SENTENCE-MATCHING-AND-DIFF-QA-COMMON-BASE-TRIAL-01(Phase A: 設計+¥0 offline検証)
実行者: sonnet-worker(read-only+設計REPORT+scratchpad検証のみ。Git操作なし、API呼び出し0件、
SSOT編集なし、Production変更なし)。
Status: **Phase A完了 / Phase B未実施(待ち)**。判定語(REJECTED/VALIDATED/UDR)はFableが確定する。
本REPORTは判定材料の提示のみ。

一時ファイル: `docs/pm/ACTIVE_TASK_TSM.md`。scratchpad(すべてGit未追跡、`C:\Users\tensh\AppData\Local\
Temp\claude\C--Users-tensh-eigo-radio\294958fe-da6e-491c-8a02-4f864d8195c8\scratchpad\`配下):
`open141_a3_reclassify.py`/`open141_a3_reclassify_result.json`、`open141_a4_synthetic.py`/
`open141_a4_synthetic_result.json`、`open141_a2_scan.py`/`open141_a2_scan_result.json`、
`open141_a2_overlap_hist.py`。既存(前タスクStage 1bで生成済み、本タスクで再利用のみ・API再呼び出し
なし): `stage1b1_results.json`/`stage1b1_context_recheck.py`。

---

## 背景(ユーザー正式判断2026-09-13の要約)

OPEN-141(Local Rewrite後に下流QAが再通過しない盲点、`OPEN_ITEMS.md`記載: 「Local Rewrite後の
本文はFact Checker・Point Overlap QA・Point Value QAを再通過しない構造的盲点(全Editorial Type
該当)」)と、target-sentence-matching(受理チェックが隣接文の問題に巻き込まれる、
`EDITORIAL-B-FAMILY-VOICES-FACT-SAFETY-RELAXATION-TRIAL-01_REPORT.md`Stage 1b-1で確認済み)を、
「変更された対象文を特定して必要QAだけ再検証する共通基盤」として統合設計する。3V Stage 3を
blockしない。

---

## A1. 現行実装の把握(該当行番号付き)

### A1-1. Local Rewriteの受理判定ロジック(A/B-Family共通、`er010_ledger_local_rewrite_09.py`)

- `locate_target_sentence()`(L47-65): `claim_in_article`(Ledger Deviation Checkerが返す逸脱箇所の
  引用)を記事本文へ厳密一致で探索し、失敗時は`split_sentences()`(L42-44、`.!?`区切りの正規表現)で
  文分割したうえでword-overlap比率(Jaccard的、記号除去+小文字化)が最大の文をfallback採用する
  (閾値0.25、Trial-08由来)。
- `extract_point_context()`(L76-93): 対象文が属する見出し区切りsection全文を「生成側のcontext」
  として返す(Rewrite生成promptにのみ使用)。
- `rewrite_ng_item()`(L168-219): 3段階escalating attempt。各attemptの受理判定は`run_check_window_fn`
  (L189/199/208で呼び出し)が返す`overall_status`(`LEDGER_COMPLIANT`/`LEDGER_DEVIATION`)のみで
  決まる。渡す`window_text`は「対象文の前後各1文+対象文」(呼び出し元が構築、below)であり、
  `point_context`(section全体)は生成promptにのみ使われ、**受理判定には使われない**(生成context
  >受理判定context、常に受理判定の方が狭い)。
- `apply_rewrites()`(L222-227): `original_ng_sentence`の文字列置換のみ(1回のみ、`str.replace(...,1)`)。

### A1-2. 呼び出し元のwindow構築とcycleループ(A-Family: `er003_v1_n3_01_articles_generate.py`
L1055-1198、B-Family: `er012_b_family_voices_writer_generic_01.py`L781-882、**両者はロジック上
完全に同一**、後者は前者を1:1で複製したコード)

- `_run_check_window(window_text)`(A-Family L1060-1063、B-Family L794-796): `vfl01.run_deviation_check`
  を`window_text`単体に対して呼び、`parsed`(`overall_status`+`deviations`配列)をそのまま返す。
  判定基準・prompt本体はLedger Deviation Checkerの通常呼び出しと同一(window引数を差し替えている
  だけ)。
- window構築: `before_ctx = sentences[sidx-1]`、`after_ctx = sentences[sidx+1]`(A-Family L1094-1095、
  B-Family L824-825、対象文の前後各1文のみ)。`point_context`(section全体)は`extract_point_context`
  失敗時のみ`before_ctx+target+after_ctx`にfallbackする(A-Family L1103-1106、B-Family L826-829)が、
  これは生成prompt用であり受理判定windowには渡らない。
- cycleループ(A-Family L1067-1163、B-Family L800-863): 記事全体を`vfl01.run_deviation_check`で
  再判定し、新たなMAJORが残れば`MAX_REWRITE_CYCLES`(=3、`er010_ledger_local_rewrite_09.py`L28/37)
  まで繰り返す。上限到達でも残ればNG_REVIEW_REQUIRED(A-Family L1179-1198、B-Family呼び出し元
  L992-1004)。

### A1-3. A-Family/B-Family共有部分と分岐

**共有(完全同一実装、`er010_ledger_local_rewrite_09`モジュールをそのままimport)**:
`locate_target_sentence`/`split_sentences`/`extract_point_context`/`REWRITE_SYSTEM_PROMPT`/3段階
attemptテンプレート/`rewrite_ng_item`/`apply_rewrites`/`MAX_REWRITE_CYCLES`。window構築ロジック
(前後各1文)・cycleループの構造もA/Bで行単位までほぼ同一(呼び出し元だけが別ファイル)。

**分岐(Editorial Type固有のQA順序)**:

| 工程 | A-Family(News/Discovery/Trend、`er003_v1_n3_01_articles_generate.py`) | B-Family 3V(`er012_b_family_voices_writer_generic_01.py`) |
|---|---|---|
| Writer draft→Evidence圧縮 | あり(L793-803付近) | あり(`_generate_and_compress_article_3v`) |
| Point Overlap/Value QA | **blocking**、記事全体retry+regenerate付き(`run_point_overlap_qa_and_regenerate`L684-750、article-level retry L864-951、`POINT_OVERLAP_ARTICLE_RETRY_MAX`まで) | **non-blocking monitoring**のみ(`run_overlap_monitoring_3v`、`point_overlap_qa_monitoring_3v.json`へ記録するだけで再生成しない) |
| Fact Checker A' | Point Overlap **後**、`verdict=FAIL`のみblocking(L989-1038) | Point Overlap monitoring **後**、`run_fact_check_a_prime_3v`、`verdict=FAIL`のみblocking(L974-984) |
| Ledger Deviation+Local Rewrite | Fact Checker **後**(L1040-1198) | Fact Checker **後**(L986-1004) |
| Local Rewrite後の追加QA | Directional Fact Precheck(rule-based、advisory、L1200-1213) | Directional Fact Precheck(同、L1006-1014)+Analytical Leakage Check(3V専用、外側の呼び出しループでcorrective note付き再attempt、`build_leakage_corrective_note_3v`等L595-780) |

**A1の核心発見(OPEN_ITEMS.md記載の盲点そのものを行番号で再確認)**: Fact Checker A'とPoint
Overlap/Value QAは、いずれもLedger Deviation Checker/Local Rewriteより**前**に1回だけ実行され、
Local Rewriteが`article_text`を書き換えた**後**は一度も再実行されない(A-Family L1119
`article_text = local_rewrite.apply_rewrites(...)`以降、B-Family L842も同様。以降に呼ばれる
QAはLedger全体再判定[同じLedger Deviation Checkerの再呼び出し]とDirectional Fact Precheck
[rule-basedadvisory]、B-FamilyのみAnalytical Leakage Check[L990で`sections`を再抽出後]のみ)。
これはOPEN_ITEMS.md L43-47の記述と一致する(¥0で再確認できた)。

---

## A2. 既存artifactでの対応付け検証(全163ファイルscan)

`er0*_output/**/audit/local_rewrite_cycles.json`を`Glob`+scratchpadスクリプトで全163件走査した
(`open141_a2_scan.py`)。Local Rewriteが実際に発火した項目(cycle内`results[]`)は合計**63件**
(A-Family21件・B-Family42件、News/Discovery/Trend/3V横断)。

**対応付け成功率(`location_method`の実測分布)**:

| location_method | 件数 | 割合 |
|---|---|---|
| `exact_substring`(claim_in_articleが記事本文に厳密一致) | 42 | 66.7% |
| `sentence_fallback`(word-overlap≥0.25のfallback) | 21 | 33.3% |
| `not_found` | 0 | 0% |

fallback 21件のoverlapは実測min 0.37〜max 1.0、中央値0.50、**0.5未満が9/21件(43%)**(閾値0.25に
対しては十分マージンがあるが、「対象文として意味的にほぼ同一」と呼べる水準からは離れているものも
含む)。`not_found`は0件だった(現行の`locate_target_sentence`自体は実データで対象文特定に
失敗した例がない)。

**失敗パターンの実例(文の結合、`open141_a2_scan_result.json`「multi_clause_examples」3件)**:
`split_sentences()`(`er010_ledger_local_rewrite_09.py`L42-44)は改行を単純にスペース結合してから
`.!?`区切りで分割するため、Markdown見出し行(`###`、`.!?`で終わらない)が前後の文へ**結合**される
ケースが確認できた。実例(`er011_output/daily_news_focus_layer_comparison_trial_04/b1b/focus/run2`):

```
original_ng_sentence = "The early lead faced one clear challenge, not repeated waves of
pressure. ### More than one hitter finished the job Late in the game, more than one hitter
supplied the scoring."
```

この`original_ng_sentence`は実際には2文+見出し1行が結合された「1つの文」としてLedger Deviation
Checkerに検出され、`locate_target_sentence`もこの結合済み文字列全体を1つの対象として扱っている
(overlap=0.43でfallback採用)。同様の結合は`er011_output/family_a_trend_ai_manufacturing_prod_run_01`
と`er012_output/editorial_b_voices_3v_person_voice_trial_01/b1b_run01_attempt3`でも確認した
(3/63件、4.8%)。この場合、「対象文」は実質的に複数文+見出しの塊であり、target-sentence-matching
方式を実装する際に「1文」という単位そのものが曖昧になる既知の弱点である。

**A2のまとめ**: `locate_target_sentence`は実データでは`not_found`0件と頑健だが、(1)fallback採用が
1/3を占め、うち半数近くがoverlap 0.5未満、(2)見出し行の結合により「対象文」が複数文にまたがる
ケースが約5%存在する。target-sentence-matching方式(A3で検証)を実装する場合、この単位の曖昧さを
そのまま引き継ぐ(新たな文分割ロジックを追加で作り直すかどうかは別途の設計判断、Phase Bのスコープ外
にすべきかも含めFableへ判断材料として提示)。

---

## A3. 過去false reject事例のtarget-sentence単位再構成(¥0、保存済み生flagのみ使用)

`stage1b1_results.json`(前タスクで実施済み、8 API呼び出し実測・¥9.75、本タスクでは**再利用のみ、
追加API呼び出し0件**)の生`deviations`配列(`claim_in_article`+`severity`+flags)を対象に、
「windowのoverall_status」ではなく「`claim_in_article`が対象文(rewrite後のfinal_text)と一致する
deviationのみを見る」方式で再分類した(`open141_a3_reclassify.py`、一致判定=厳密部分一致 or
word-overlap≥0.5)。

| tag | window全体のoverall_status(現行方式) | target-sentence単位のoverall_status(新方式) | 判定が変わるか |
|---|---|---|---|
| A_narrow_final_text(ablation個体、狭いwindow) | LEDGER_DEVIATION | **LEDGER_COMPLIANT** | 変わる |
| A_wide_final_text(同、point_context) | LEDGER_DEVIATION | **LEDGER_COMPLIANT** | 変わる |
| B_narrow_final_text(旧run1ng個体、狭いwindow) | LEDGER_DEVIATION | **LEDGER_COMPLIANT** | 変わる |
| B_wide_final_text(同、point_context) | LEDGER_DEVIATION | **LEDGER_COMPLIANT** | 変わる |
| control_wide_trial02_attempt2 | LEDGER_DEVIATION | **LEDGER_COMPLIANT** | 変わる |
| control_wide_regression_attempt2_evenif | LEDGER_COMPLIANT | LEDGER_COMPLIANT | 変わらない |
| control_wide_regression_attempt3_powerisuneven | LEDGER_DEVIATION | **LEDGER_COMPLIANT** | 変わる |
| control_wide_run1ng_cycle2_nyc | LEDGER_DEVIATION | **LEDGER_DEVIATION**(対象文自身に`changed_time`の逸脱あり) | 変わらない(正しく維持) |

**結果**: 8件中6件で、window全体のoverall_statusでは不合格(LEDGER_DEVIATION)だったものが、
target-sentence単位で見ると対象文自体は一度もflagされておらず、正しくLEDGER_COMPLIANTへ変わる
(=false rejectが解消される)。残り2件のうち1件は元々COMPLIANTのままで無変化、もう1件
(`run1ng_cycle2_nyc`)は対象文自体に「毎年」という未確認の頻度情報を追加した本物の逸脱があり、
target-sentence単位でも**正しくLEDGER_DEVIATIONのまま維持**される(=危険な変更を誤って通す
副作用は生じない)。Stage 1b-1が「対象文単独では広い文脈で問題視されなくなる」と結論づけていた
仮説を、target-sentence-matching方式への実際の再分類ロジックで¥0再確認できた。

---

## A4. 合成ケースによる安全性確認(¥0、rule-based、11件)

Local Rewrite後の文に数字・固有名詞/制度名・否定・第三者行動が実際に混入した「真に危険な変更」を
想定した合成deviationを11件作成した(`open141_a4_synthetic.py`)。各ケースは対象文自身がMAJOR
flagを持ち(`changed_number`/`changed_actor`/`changed_negation`/`unsupported_new_claim`等)、
うち10件には無関係な隣接文の別deviation(distractor)を併置し、target-sentence-matchingが
「対象文自身の逸脱は正しく検出したまま、無関係な隣接文の逸脱には引きずられない」ことを確認した。

結果: **11/11件すべてで、target-sentence単位判定後もLEDGER_DEVIATION(MAJOR維持)を正しく
再現した**(distractorの有無に関わらず、対象文自身のMAJOR flagがある限り必ず検出される設計)。
これはtarget-sentence-matching方式が「危険な変更を見逃す」方向には作用しないことを、A3の
false-reject解消6件とあわせて裏付ける(A3=誤って弾いていたものを正しく通す、A4=本当に危険な
ものは変わらず弾く、の両面確認)。

**限界の明記**: A4はrule-based合成(claim_in_articleとseverityを直接指定)であり、実際に
Ledger Deviation Checker(LLM)がこれらの合成文に対して本当にMAJOR+該当flagを返すかどうかは
検証していない(¥0の範囲では確認不可、Phase Bで実LLM呼び出しが必要な項目)。あくまで
「target-sentence-matchingという**照合ロジック自体**が、対象文自身に付与された正しいseverityを
書き換えたり握りつぶしたりしないか」という、ロジック単体の健全性確認である。

---

## A5. 差分QA設計の比較(3案)

前提: OPEN_ITEMS.md記載の盲点は「Fact Checker A'・Point Overlap/Value QA」が対象。既存usage
実測(`EDITORIAL-B-FAMILY-VOICES-FACT-SAFETY-RELAXATION-TRIAL-01_REPORT.md`C1節、`pricing_snapshot.json`
単価: gpt-5.6-luna input $0.20/1M・output $1.20/1M・web_search $10/1000件)から、1回あたりの
概算コストは Fact Checker A'(web_search込み)≈¥12〜47/個体(複数attempt込み)、Ledger Deviation
Checker単体(1呼び出し)は入力8,000〜9,600トークン規模でも≈¥0.0016〜0.0019/回(web_search無し)と
2桁以上安い。

| 案 | 内容 | false accept見込み | false reject見込み | コスト(1記事あたり概算) | latency | retry/fallback整合 | A/B-Family適用範囲 |
|---|---|---|---|---|---|---|---|
| **案I: 対象文にFact Checker A'+Ledger Deviationのみ** | Local Rewrite確定後、書き換わった対象文(+前後1文程度)だけをFact Checker A'(web_search込み)とLedger Deviation Checkerへ再投入 | 低(Fact Checker A'は独立Web検索のためLedgerに無い新事実の混入も検出できる) | 中(Point Overlap/Valueは対象外のままのため、Rewrite後の文がPoint間の重複を新たに生んでも検出されない) | Fact Checker A'再呼び出し1回分≈¥3〜12(web_search 1〜数回)+Ledger再呼び出し≈¥0.002。cycle最大3回×対象文数で増加しうる | Fact Checker A'はweb_search込みで数秒〜十数秒、cycleごとに追加 | 既存retry上限(`MAX_REWRITE_CYCLES`=3)とは独立した新規呼び出しのため、上限混同を避ける設計が必要 | A/B共通(A-Familyは元々Fact Checker A'をblockingで持つため親和性高い。B-FamilyはFact Checker A'呼び出し自体は共通関数`run_fact_check_a_prime_3v`を再利用可能) |
| **案II: 変更要素に応じて必要QAのみ選択** | Rewrite差分(flags: changed_number→事実系、changed_scope/certainty→影響小、Point間重複を生みうる語彙変化→Point Overlap再計算)に応じて、Fact Checker A'/Ledger Deviation/Point Overlap個別に要否判定 | 低〜中(判定ロジック自体の正確性に依存、誤判定リスクあり) | 低(必要なQAを取りこぼしなく選べれば理論上最小) | 案Iより安い見込み(不要なFact Checker A' web_search呼び出しを削減できる)だが、判定ロジックの設計・実装コストが最大 | 案Iと同等〜やや短い(不要な呼び出しを削減した分) | 既存の安全装置(MAJORのみ対象、上限3回)とは別軸の追加ロジックのため、既存Gateとの二重管理リスクが最も高い | A/B共通だが、B-FamilyのPoint Overlapはmonitoring専用(non-blocking)のため「Point Overlap再計算」の意味合いがA-Familyと異なる(A1参照)、設計を分ける必要あり |
| **案III: 常に全文再QA(比較用上限)** | Local Rewrite確定後、記事全体をFact Checker A'・Point Overlap/Value QAへ丸ごと再投入(Editorial Type既存の初回QAと同一呼び出しを再実行) | 最低(見逃しリスクが最小) | 最低(既存QA基準をそのまま適用) | 最大(Fact Checker A'のフルコスト¥12〜47を毎cycle追加、100記事換算で相当な増分) | 最大(既存QA工程をまるごと繰り返す) | 実装は最も単純(既存関数をそのまま再呼び出しするだけ)、上限混同リスクは低い | A/B共通、A-Familyは既存のPoint Overlap article-level retryループへほぼそのまま合流できる |

**Phase Aでの暫定所見(判断はFable/ユーザー)**: 案I(対象文限定+両QA)が「盲点を塞ぐ」という
OPEN-141の目的に対し費用対効果のバランスが良いと見えるが、Point Overlap/Value QAをどう
「対象文だけ」に絞るか(Point全体のoverlap比率計算はセクション単位のため、1文だけの差し替えでは
再計算の意味が薄い可能性がある)という設計課題が残る。案IIは理想形だが、判定ロジック自体の
バグ・誤判定が新たなfalse reject/false acceptを生むリスクを内包し、実装・検証コストが最も高い。
案IIIはコストが最大だが「安全側に倒す」という既存方針(安全≠成功原則)には最も合致する。

---

## A6. Phase B設計(実行しない、設計のみ)

**対象記事候補**: (a)3V Stage 3で新規生成する記事のLocal Rewrite発火時に本基盤を通す(ただし
3V Stage 3自体は`EDITORIAL-B-FAMILY-VOICES-FACT-SAFETY-RELAXATION-TRIAL-01_REPORT.md`のStage 2が
`USER_DECISION_REQUIRED`のままSTOPしており、本Trialが3V Stage 3の前提をblockしないよう、
Stage 3の意思決定とは独立に進められる素材が必要)、(b)A-Family既存Ledger(News/Discovery)で
Local Rewrite発火頻度が高いテーマを1本選び、そのLocal Rewrite再現(保存済みLedger+claim_in_article
を使い、新規記事生成なしで対象文への差分QAのみを追加実行)。(b)の方が3V Stage 3の意思決定と
完全に独立でき、依存関係の整理としては優先度が高い。

**費用見積(Phase B、実行しない場合の試算)**: 案I採用時、対象文1件あたりFact Checker A'
1回(≈¥3〜12、web_search回数依存)+Ledger Deviation Checker 1回(≈¥0.002、無視できる)。
過去実績(A2)で1記事あたりLocal Rewrite発火は平均0.4件程度(63件/163ファイル、ただし発火0件の
記事が大半を占めるため実質的な発火率は個体依存)。1記事のPhase B想定コストは¥5〜20程度
(Fact Checker A' 1〜2回分)。

**STOP条件(Phase B実施時)**: (1)target-sentence-matchingの照合ロジック自体が実データで
`not_found`または誤対応付けを起こした場合、(2)対象文への差分Fact Checker A'がFAILを返した
場合(記事の安全性そのものの問題であり、本Trialの設計問題ではない)、(3)既存`MAX_REWRITE_CYCLES`
や既存Gate(Point Overlap article-level retry等)との呼び出し順序・上限カウントに矛盾が生じた
場合、(4)追加コストが単一記事で¥50を超えた場合。いずれも実装せずFableへ報告してSTOPする。

**依存関係の整理(3V Stage 3をblockしない)**: 本Trial(OPEN-141)は3V Stage 3(Fact Safety
Relaxation Trial Stage 2/3)とは独立した既存の安全装置改善であり、3V Stage 3の意思決定
(Stage 2のゲート設計含む)を待たずにPhase Bへ進めることができる。ただし、Phase Bで
「受理ロジックのtarget-sentence-matching化」自体をProduction実装する場合、これは
`EDITORIAL-B-FAMILY-VOICES-FACT-SAFETY-RELAXATION-TRIAL-01_REPORT.md`Stage 1bが指摘した
「2-Cの前提(判定基準・prompt不変)は維持できるが、受理判定の実装方式は変わる」という
設計変更と実質的に同一のものであり、両タスクは最終的に同じProduction関数
(`run_check_window_fn`のインターフェース)へ収束する可能性が高い。実装順序は
Fable判断に委ねる(OPEN-141を先に実装し3V Fact Safety Stage 2はその実装を再利用する、
または逆順、のいずれもあり得る)。

---

## Fableへの報告事項(判断が必要)

1. A5の3案のうち、どれを次段階(設計詳細化またはPhase B)の候補とするか。
2. Phase Bの対象記事候補は(b)A-Family既存Ledger再現(3V Stage 3非依存)を推奨するが、(a)3V
   Stage 3経路との統合も選択肢としてある。
3. A2で確認した「見出し行が文分割に混入する」既知の弱点(`split_sentences()`)を、本Trialの
   スコープに含めて修正するか、別Issueとして切り出すか。
4. target-sentence-matching実装は、`EDITORIAL-B-FAMILY-VOICES-FACT-SAFETY-RELAXATION-TRIAL-01_REPORT.md`
   Stage 1bが指摘した3V Fact Safety Stage 2の受理ロジック変更と収束する可能性が高いため、
   実装順序・担当タスクの一本化をFableで整理いただきたい。

## 費用(Phase A)

Phase A: API呼び出し0件(¥0)。既存の保存済みデータ(`stage1b1_results.json`、
`er012_output/fact_safety_relaxation_trial_01/*.json`)・全163ファイルのGlob走査・scratchpad
rule-basedスクリプトのみで実施。

---

# Phase B: 実装+1記事統合Trial

管理ID: OPEN-141-TARGET-SENTENCE-MATCHING-AND-DIFF-QA-COMMON-BASE-TRIAL-01(Phase B)
実行者: sonnet-worker。Git操作なし(commitは後続統合で実施)。SSOT編集なし(追記文案のみ本節末尾)。
Status: **Phase B完了(実装+テスト+1記事統合Trial)**。判定語(REJECTED/VALIDATED/UDR/
APPROVED_FOR_PRODUCTION)はFable/ユーザーが確定する。本節は判定材料の提示のみ。

Fable判断(2026-09-13)に基づき、(1)案I採用、(2)対象記事=A-Family既存Ledger再現(News)、
(3)`split_sentences()`見出し混入バグの修正をスコープに含める、(4)`run_check_window_fn`
インターフェースへのopt-in(既定OFF)実装、の4点を反映した。

## B1. target-sentence-matching実装(opt-in、既定OFF)

`er010_ledger_local_rewrite_09.py`(Production共有モジュール、A/B-Family両呼び出し元が
import)に追加(該当行は同ファイル参照、コメントにOPEN-141根拠を明記済み):

- `classify_deviation_role(claim_in_article, target_sentence, before_ctx, after_ctx)`:
  Ledger Deviation Checkerが引用した逸脱箇所(`claim_in_article`)が、window内のtarget/
  before/afterのどれに属するかをexact_substring→word-overlap fallback(Phase A2の
  `locate_target_sentence`と同一閾値0.25)で判定する。複数一致・閾値未満(not_found)・
  僅差(tie、margin 0.05未満)は`role='ambiguous'`とする。
- `evaluate_target_sentence_status(check_result, target_sentence, before_ctx, after_ctx)`:
  window全体のdeviations配列を上記で分類し、対象文自身に紐づくdeviationのみで
  overall_statusを再計算する。ambiguousなdeviationが1件でもあれば、安全側として
  window全体のoverall_statusへフォールバックする(match_fallback=True、危険な変更を
  誤って通さないための保守的挙動)。
- `rewrite_ng_item()`へ`use_target_sentence_matching: bool = False`を追加(11番目の
  引数、既存呼び出し元[A-Family: `er003_v1_n3_01_articles_generate.py`L1107、
  B-Family: `er012_b_family_voices_writer_generic_01.py`L987]は10個の位置引数のみで
  呼び出しており本引数を渡さないため無変更)。既定Falseの間はattemptsエントリも従来通り
  `{'attempt','text','ledger_status'}`の3キーのみで、window全体のoverall_statusのみで
  受理判定する(byte一致、`test_default_off_matches_pre_open141_shape_exactly`で保証)。
  Trueの場合のみ診断用キー(`ledger_status_window`/`target_sentence_eval`)を追加する。

## B2. 差分QA(案I)実装

新規Trialスクリプト`er011_open141_target_sentence_diff_qa_integration_trial_b_01.py`に、
Production自動経路には配線しない形で実装(既存関数の薄いラッパーのみ、新しいLLM判定基準・
promptは作らない):

- `run_diff_qa_for_target_sentence()`: 対象文(+前後1文)を、既存のFact Checker A'
  (`er002_ja_web_research_r3.build_fact_check_prompt`/`make_fact_checker_fn`/
  `run_fact_checker_with_gates`、web_search込み)と既存のLedger Deviation Checker
  (`vfl01.run_deviation_check`、Hook-aware)へ再投入する。呼び出し回数は
  `DIFF_QA_CALLS_PER_ITEM`という独立カウンタで明示し、既存`MAX_REWRITE_CYCLES`
  (記事全体cycle上限=3)・`MAX_REWRITE_ATTEMPTS`(文単位rewrite試行上限=3)とは
  混同しない(本Trialでは対象文1件につき差分QA呼び出し1回のみ、上限運用自体は
  Production採用時に別途Fable/ユーザー判断が必要)。
- `recompute_point_overlap_if_in_point_section()`: 対象文が`split_common_sections_
  for_point_qa()`(既存、`er003_v1_n3_01_articles_generate.py`、読取のみ・無変更)の
  Point One/Two本文内にある場合のみ、既存のrule-based Point Overlap
  (`er008_point_overlap_qa_18.flag_possible_paraphrase`、¥0・LLM再呼び出しなし)を
  そのsectionについて再計算する。Point Value QA(LLMベース、`er011_point_role_
  value_planning_01.run_point_value_qa`)はFable判断通りスコープ外(LLM再呼び出し
  なしの制約のため)。

## B3. `split_sentences()`見出し行除外 + 実データで発見した副次バグ

`er010_ledger_local_rewrite_09.py`の`split_sentences()`を、見出し行(`#`で始まる行)・
空行を連結対象から除外するよう修正した。見出しを含まない入力への影響はbyte一致
(`test_no_heading_input_unchanged`)。

**実データで新たに確認した重大な副次影響**: 選定記事(`er011_output/daily_news_
focus_layer_comparison_trial_04/b1b/focus/run2`)のcycle 1 item 2は、Phase A2で
確認した見出し混入の実例そのものだった。旧`split_sentences()`は対象文を
「"The early lead faced one clear challenge, not repeated waves of pressure. ###
More than one hitter finished the job Late in the game, more than one hitter
supplied the scoring."」という、見出し+2文が結合された文字列として扱っていた。
`apply_rewrites()`はこの結合済み文字列(改行がスペースに変換済み)を実際の記事本文
(改行を含む)に対して`str in updated`で厳密一致検索するため**一致せず、置換が
サイレントに失敗**していた。cycle 1・cycle 2とも`resolved=True`と記録されたが、
出荷された`article.md`には元のMAJOR判定文がそのまま残っていることを実データで確認した
(`test_real_article_reproduction_daily_news_focus_layer_trial_04`で再現)。
Local Rewriteが「解決した」と誤って記録しながら実際には本文を書き換えていなかった、
という見出し混入バグの実害を初めて具体的に特定できた。B3修正後は対象文が正しく
単文として得られ、実際の記事本文とbyte一致するため、この種の無言の置換失敗は解消される。

## B4. テスト結果

新規ファイル`er010_open141_target_sentence_matching_diff_qa_b_test_01.py`(22件、
実LLM呼び出し0件・¥0):

- `SplitSentencesHeadingExclusionTests`(4件): 見出しなし入力のbyte一致、見出し除外、
  H1/H2見出し除外、選定記事の実データ再現。
- `ClassifyDeviationRoleTests`(4件): exact_substring(target/adjacent)、not_found、
  複数一致の曖昧判定。
- `EvaluateTargetSentenceStatusPhaseAReproductionTests`(8件): Phase A3の保存済み
  実データ8件を実際の`evaluate_target_sentence_status()`で再分類し、Phase A3の表
  (6件がCOMPLIANTへ変わる、1件は元々COMPLIANT、1件は正しくDEVIATIONのまま維持)を
  完全再現。
- `EvaluateTargetSentenceStatusSyntheticDangerCasesTests`(1件、11 subTest): Phase A4の
  合成危険11件が全てMAJORを維持することを実関数で再確認(11/11)。
- `RewriteNgItemOptInInvarianceTests`(4件): 既定OFF不変性、opt-in ON時の正しい
  reclassify、対象文自身MAJOR時のescalation維持、対応付けambiguous時の安全側
  フォールバック。
- `CallerSignatureCompatibilityTests`(1件): A/B-Family実呼び出しパターン
  (10位置引数のみ)との互換性。

既存テスト回帰(無変更、全PASS、実測):
- `er010_n9_production_integration_09_test_01.py`: 33件PASS(修正前後で同数・同結果)。
- `er012_editorial_b_family_voices_3v_production_wiring_phase1_test_01.py`
  (3V Stage 2/3並走中、読取専用で実行のみ・無変更): 56件PASS(修正前後で同数・同結果)。

## B5. 1記事統合Trial結果(実LLM呼び出し、実測)

対象: A-Family News、`er011_output/daily_news_focus_layer_comparison_trial_04/
b1b/focus/run2`(記事)+`er003_output/n3_01/hanshin/research/verified_fact_ledger.txt`
(Verified Fact Ledger、保存済み、新規記事生成なし)。対象文はB3節記載の見出し混入
実例の文(`"The early lead faced one clear challenge, not repeated waves of pressure."`)。

実行内容と結果(すべて`er011_output/open141_target_sentence_diff_qa_integration_
trial_b_01/trial_result.json`に保存):

1. **B3確認**: 修正後`split_sentences()`で対象文が単文として正しく取得でき、
   前後文(`before_ctx`/`after_ctx`)が実際の記事本文の隣接文と一致することを確認
   (`b3_heading_exclusion_check.matches_manual_before_ctx/after_ctx = true`)。
2. **Before(現行window方式、実LLM再呼び出し)**: 正しい単文境界のwindow
   (before_ctx+target+after_ctx)を`vfl01.run_deviation_check`(Hook-aware、
   Production同一関数)へ再投入した結果、`overall_status = LEDGER_COMPLIANT`
   (deviations 0件)。
3. **After(B1 target-sentence-matching、追加API呼び出し0件)**: 上記と同一の
   check結果を`evaluate_target_sentence_status()`で再分類しても
   `LEDGER_COMPLIANT`のまま(`verdict_changed_by_target_sentence_matching = false`)。
   **解釈**: この特定事例では、false rejectの主因はB3の見出し混入バグそのもの
   だった(旧実装は結合済みの汚れたwindow文字列をチェッカーへ渡していたため
   繰り返しLEDGER_DEVIATIONと誤判定していた)。B3単独の修正で本事例の
   false rejectは解消し、B1(target-sentence-matching)の追加効果はこの1事例
   では観測されなかった。B1固有の効果はPhase A3(保存済み実データ8件中6件、
   見出し混入とは無関係な「隣接文のみにdeviationがある」ケース)で既に
   ¥0で再現・確認済みであり、両者は独立した異なる不具合パターンに対応する
   ことが実データで裏付けられた。
4. **B2差分QA(案I、実LLM呼び出し)**: 同一window textをFact Checker A'
   (`gpt-5.6-sol`、web_search 4回)へ再投入した結果、`verdict = REVIEW_REQUIRED`
   (contradictionsは0件だが`unsupported_specific_claims`に1件該当)。NPB公式
   play-by-playの独立Web検索により、広島は5回のモンテロ本塁打以外にも
   2回・3回・9回に得点圏へ走者を進めた場面があったことが判明し、「明確な
   脅威は一度だけ」という対象文の記述は客観的に断定できないと指摘された。
   **これはLedger Deviation Checker(window全体・target-sentence-matching
   いずれも)が検出できなかった問題を、独立したFact Checker A'のWeb検索が
   検出した実例であり、OPEN_ITEMS.mdが記載する盲点(Fact Checker A'は
   Local Rewrite後に再実行されない)への対策として案Iが機能することを
   実データで確認できた**。REVIEW_REQUIRED(FAILではない)のため、既存の
   「REVIEW_REQUIREDは原則ブロックしない」運用方針(`er003_v1_n3_01_
   articles_generate.py`L1014-1025のコメント参照、本Trialでは変更していない)
   に従えば追加のRewrite/regenerateはトリガーされない設計上の解釈になるが、
   これはFable/ユーザーが判断すべき閾値設計上の論点として明記する
   (STOP条件(2)「差分Fact Checker A'がFAIL」には該当しないため実装は継続、
   ただしREVIEW_REQUIREDの扱い自体はGate 3で要確認)。
   Ledger Deviation Checker再呼び出し(diff QA内)は`LEDGER_COMPLIANT`
   (`requires_escalation = false`)。
5. **Point Overlap rule-based再計算**: 対象文はPoint One section内
   (`split_common_sections_for_point_qa`で判定)。Full Storyとのoverlap比
   0.394(閾値0.40未満、僅差でflagされず)、他方のPointとのoverlap比0.061
   (flagなし)。¥0・LLM再呼び出しなし。

STOP条件との照合: (1)対応付けnot_found/誤対応=発生せず、(2)差分Fact Checker A'が
FAIL=発生せず(REVIEW_REQUIREDのみ)、(3)既存Gate/上限との矛盾=発生せず、
(4)単一記事コスト¥50超=発生せず(下記B6参照)。よってSTOPには該当しないが、
上記4のREVIEW_REQUIREDの扱いはGate 3確認事項として明記する。

## B6. コスト評価

実測(本Trial、対象文1件分):
- Ledger Deviation Checker(window再判定、Hook-aware): 1回、web_search無し
  (`gpt-5.6-luna`)。
- Fact Checker A'(差分QA): 1回、web_search 4回(`gpt-5.6-sol`、reasoning=high)。
- Ledger Deviation Checker(差分QA内の再確認): 1回、web_search無し。
- Point Overlap rule-based再計算: 0回API呼び出し。

正確なトークン使用量はresponseオブジェクトから今回明示的に記録していないため
(telemetryの改善余地として明記)、`pricing_snapshot.json`記載単価
(`gpt-5.6-sol`: input $5/1M・output $30/1M、web_search $10/1000件、
`gpt-5.6-luna`: input $0.20/1M・output $1.20/1M)とweb_search実測回数(4回)から
概算すると、本Trial全体(対象文1件・差分QA1回・window再判定2回)は**概算¥15〜30
程度**(Fact Checker A'がweb_search 4回+`sol`モデルの高い単価により、Phase A5の
当初見積り¥3〜12/回よりやや高めに実測された。理由: Phase A5見積りは`luna`モデル
単価を基準にしていたが、実際のFact Checker A'呼び出しは既存Production設定通り
`gpt-5.6-sol`[`FACT_CHECKER_MODEL`]を使用するため)。予算上限¥50以内(単一記事
STOP条件¥50超にも該当せず)。

**100記事換算**: Phase A6の実測発火率(1記事あたりLocal Rewrite発火 平均0.4件
程度、A2実データ)を用いると、100記事で約40件のLocal Rewrite発火が見込まれる。
差分QA(案I)を全発火項目に適用した場合、概算100記事換算コストは
**¥15〜30 × 40 ≈ ¥600〜1,200程度**(Point Overlap rule-based再計算は¥0、
target-sentence-matching自体も追加API呼び出し0件のため主要コストは差分QAの
Fact Checker A'呼び出しに集中する)。

**QCD比較表(品質/安全性/1記事コスト/量産コスト/処理時間、概算)**:

| 項目 | 現行(Local Rewrite後QA再実行なし) | 案I(本Phase B実装) | 案III(常に全文再QA) |
|---|---|---|---|
| 品質・安全性 | Local Rewrite後にFact Checker A'/Point Overlapが1度も再実行されない盲点あり(OPEN_ITEMS.md記載) | 対象文+前後1文のみ差分再検証。本Trialで実際に1件の見落とし候補(REVIEW_REQUIRED)を検出 | 記事全体を毎cycle再検証、見逃しリスクは理論上最小 |
| 対象文特定 | – | B1(target-sentence-matching)+B3(見出し除外)で対象文単位を正確化、実データでapply_rewritesのサイレント失敗も検出 | 記事全体のため対象文特定は不要 |
| 1記事あたり追加コスト(Local Rewrite発火時) | ¥0(追加QAなし) | 発火1件あたり概算¥15〜30(Fact Checker A' 1回+Ledger Deviation Checker 1〜2回) | Fact Checker A'フルコスト(¥12〜47、Phase A5)を毎cycle追加、案Iより高い |
| 100記事換算(発火率0.4件/記事) | ¥0 | 概算¥600〜1,200 | 案Iより高い(記事全体再検証のため入力トークン数が案Iより大幅に多い) |
| 処理時間(発火時) | 変化なし | Fact Checker A'のweb_search込みで数秒〜十数秒/対象文、cycleごとに追加 | 案Iと同様の追加だが記事全体再検証のため案Iより長い |
| 既存retry/上限との整合 | – | 新規`DIFF_QA_CALLS_PER_ITEM`カウンタで`MAX_REWRITE_CYCLES`/`MAX_REWRITE_ATTEMPTS`と区別(混同なし) | 既存Article-level retryループへ合流しやすい(実装単純) |

## Gate 1判定材料(判定語はFable)

- B1(target-sentence-matching): Phase A3の保存済み実データ8件を実関数で完全再現
  (6/8でfalse reject解消、1件は元々COMPLIANT維持、1件は正しくDEVIATION維持)。
  Phase A4の合成危険11件も実関数で11/11維持。既定OFF不変性は22件の新規テスト+
  既存89件(33+56)の回帰テストで実測PASS。
- B2(差分QA案I): 実LLM呼び出しによる1記事統合Trialで、Ledger Deviation Checker
  (window全体・target-sentence-matching両方)が見落とした問題をFact Checker A'
  (独立Web検索)が実際に検出した(REVIEW_REQUIRED)実例を確認。OPEN_ITEMS.md記載の
  盲点への対策として機能することを実データで裏付けた。
- B3(見出し除外): 修正前後でbyte一致(見出しなし入力)を保証しつつ、選定記事で
  実際に発生していた「resolved=Trueと記録されながら本文が書き換わっていない」
  という重大な副次バグを具体的に特定・解消した。

## Production採用に必要な確認(Gate 3項目、実装済みだが未確定の論点)

1. B2差分QAの`verdict = REVIEW_REQUIRED`をどう扱うか(既存Fact Checker A'の
   通常運用ではblockingはverdict=FAILのみ、REVIEW_REQUIREDは記録のみで通過
   させる方針だが、差分QAという新しい文脈でも同じ閾値でよいか)。
2. B2差分QAをどのタイミング・どの呼び出し元(A-Family/B-Family)へ実際に配線するか
   (本Phase BはTrialスクリプトのみでProduction自動経路には一切配線していない)、
   および`DIFF_QA_CALLS_PER_ITEM`の実運用上限(現状は上限なし、1件1回のみ想定)。
3. B1のopt-in既定をいつ・どの呼び出し元でTrueへ切り替えるか(3V Fact Safety
   Relaxation Trial Stage 2の受理ロジック変更[Phase A報告事項4]との実装収束・
   順序をFableで整理する必要がある、本Phase Bでは3V側には一切触れていない)。
4. 100記事換算コスト(¥600〜1,200程度、案I採用時)を量産コストとして許容するか。
5. トークン使用量の正確な記録(telemetry)を、Production配線時に追加する必要が
   あるか(本Trialでは`web_search_call_count`のみ実測、input/output token数は
   未記録)。

## SSOT追記文案(編集はFable/PM層が実施、本REPORTでは追記文案の提示のみ)

**CURRENT_SPEC.md追記案**: 「OPEN-141 Phase B(target-sentence-matching+差分QA
案I)がTrial実装として`er010_ledger_local_rewrite_09.py`(opt-in、既定OFF)・
`er011_open141_target_sentence_diff_qa_integration_trial_b_01.py`(Trial専用、
Production未配線)に実装され、A-Family実記事1本(Hanshin News)で実LLM呼び出しに
よる統合Trialを完了した(OPEN-141-TARGET-SENTENCE-MATCHING-AND-DIFF-QA-COMMON-
BASE-TRIAL-01_REPORT.md Phase B参照)。Production自動経路への配線は未実施
(APPROVED_FOR_PRODUCTION判断待ち)。」

**OPEN_ITEMS.md(OPEN-141)追記案**: 「Phase B完了。target-sentence-matching
(opt-in既定OFF)・差分QA案I(Fact Checker A'+Ledger Deviation Checker再投入)・
Point Overlap rule-based再計算をTrial実装し、A-Family実記事1本で実LLM統合Trialを
実施(概算¥15〜30/対象文、100記事換算¥600〜1,200程度)。副次的に`split_sentences()`
の見出し混入バグ(resolved=Trueと記録されながら本文が書き換わらないサイレント
失敗)を実データで発見・修正した。Production採用(APPROVED_FOR_PRODUCTION)・
REVIEW_REQUIREDの扱い・3V Fact Safety Stage 2との実装収束順序はユーザー/Fable
判断待ち(USER_DECISION_REQUIRED)。」

**DECISION_LOG.md追記案**: 「OPEN-141-TARGET-SENTENCE-MATCHING-AND-DIFF-QA-
COMMON-BASE-TRIAL-01 Phase B: target-sentence-matching(opt-in既定OFF)・
差分QA案I・split_sentences見出し除外バグ修正を実装し、テスト(新規22件+既存
89件回帰PASS)と1記事統合Trial(実LLM呼び出し、概算¥15〜30)で検証した。
Production採用は別途ユーザー承認が必要(現時点はTrialのみ、自動経路へ未配線)。」

## 費用(Phase B、実測)

API呼び出し: Ledger Deviation Checker 2回(web_search無し、`gpt-5.6-luna`)+
Fact Checker A' 1回(web_search 4回、`gpt-5.6-sol`)。概算¥15〜30(pricing_
snapshot.json記載単価+web_search実測回数からの概算、正確なtoken使用量は
未記録)。単一記事¥50超のSTOP条件には該当せず。テスト実行(89件既存回帰+
22件新規)はAPI呼び出しを伴わずすべて¥0。
