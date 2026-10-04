# Opus Context Packet: OPEN-233-KPI-RECOVERY-REDESIGN-02 委任_05(rep27 Human Review 3件の是正・再確認DEVIATION処理設計の批判レビュー、条件A)

作成: Sonnet(委任_05)。依頼元: Fable。対象: (1)実装済みの技術是正(L6とcarry-forwardの順序、runner `l6_carry_forward_precedence`)、(2)neg3 `unconfirmed_after_reverify`のRCAと、再確認DEVIATIONの処理設計案N1〜N3(**未実装**)、(3)残STAGE4経路の棚卸し。
関連: 設計書`docs/pm/design_open233_kpi_recovery_02.md` §12(12-1〜12-3)、replay=`er052_output/open233_kpi_recovery_02_offline_01/`(`replay_cf_l6_order_01.*`・`rca_neg3_prompt_reconstruct_01.*`・`agg_stage4_reasons_01.*`)、前回packet=`docs/pm/opus_packet_open233_kpi_recovery_02_01.md`(別内容、Opus#11)。
KPI(変更・緩和禁止): Primary=USER_DECISION_REQUIRED/Human Review 0件、Safety=重大Fact見逃し0件、平均追加+¥2/記事以内、Cap+¥3/記事以内。QCD優先: 1重大見逃し0 2Human Review 0 3不要Rewriteを増やさない 4+¥2 5非決定性・追加call最小 6Production複雑化回避。「Safetyを理由にHuman Reviewへ逃がさない」。Productionは未変更(編集は`er052_open233_*`のみ)。Checker Prompt・Schema・判定方法・V7bは不変。
Opusの役割: 追認でなく独立評価。Production採用可否は宣言しない。

## (a) 論点(限定)

1. **是正(a)の順序変更の安全性**: L6が復元した文が(i)carry-forward判定(cycle開始時点の本文での照合、委任_04の部分一致含む)で全範囲が先行Rewrite済み、または(ii)L6の復元範囲が同cycleの先行Rewriteの置換後の文(`after_units`)と完全一致、のとき、L6の復元を捨ててcovered(Rewriteしない)にする。「書き換え済みの文の復元を防ぐ」判定として妥当か。同じ文を指す2つのclaimが**別の問題**を指す場合(carry-forwardの完全包含はissue同一性を問わない既存仕様)に、重大見逃しを生まないか(解消の最終担保は全文Recheck+cycle 2)。他のL6復元・carry-forwardを損なわないか。
2. **案N1〜N3の比較**(設計書§12-3): 再確認DEVIATIONを通常のRecheck結果としてStage 2へ流すN1が、Human Reviewへ逃げず・Safety側へ倒れ・新しいretry loopを作らない最小案か。N2(再確認2回)・N3(prior_issues文言の明確化)の判断は妥当か。N1-a(空DEVIATIONはSTAGE4維持)とN1-b(ladder次段Rewrite)のどちらが妥当か。
3. **残STAGE4経路の棚卸しに漏れはないか**(設計書§12-3末尾の表)。KPI構成でHuman Review 0に至るには、他に何が必要か。
4. **より単純な方法はないか**: 特に(i)再確認callを廃止して自己矛盾を直接Stage 2へ流す(再確認の存在理由=静かな降格防止は、deviationsを使えば不要にならないか)、(ii)L6そのものを外す(rep26・27の復元が全て「書き換え済みの文」への復元だった事実から)。
5. **Production配線時の整合**: 再確認callは`er052`のTrial専用で、Productionの再検査(`er012_e_family_entertainment_two_level_runner_01.py` 410〜430行、再生成後に`COMPLIANT∧all_resolved`でなければSTOP)には無い。N1・順序是正をProductionへ載せる場合に必要な整合は何か。

### 論点と材料の対応チェック

| 論点 | 必要な材料 | (b)/(c)のどこにあるか | 不足時の扱い |
|---|---|---|---|
| 1 | A4/A5の記録(claim・level・method)、順序、replay結果、他のL6復元への影響 | (b)「A4/A5」「replay結果」、(c)6316〜6460行 | 規則(2)の誤適用例は実データに無く、合成unit testのみ(未実測と明示) |
| 2 | neg3の逐語(promptはSHA一致で再構築、raw応答は**未保存**)、既存ログ集計、cycle別件数、案比較表 | (b)「neg3」「集計」「比較表」 | raw応答の逐語は無い(設計書§12-2で未確認と明示)。再確認のdeviationsが何かは不明のまま判断する必要がある |
| 3 | stage4_reason別の件数・発生箇所 | (b)「棚卸し表」、(c)行番号 | 旧構成の原因は未分析 |
| 4 | rep26・27のL6復元の全列挙 | (b)「replay結果」 | 他の方法の実測は無い |
| 5 | Productionの再検査コード | (c)`er012`410〜430・`er003`826 | 配線案自体は未設計 |

---

## (b) 主要数値表・要点

### 要点(5行)

1. rep27(Step 6、38 instance-run): Safety 0・不要Rewrite 24件/19 run・平均追加+¥0.02・worst run ¥2.37、**Human Review 3件**(A4 s1・A5 s1=`ladder_exhausted_without_full_rewrite`、neg3 s1=`unconfirmed_after_reverify`)。
2. A4/A5: 同cycleの先行Rewriteが文を書き換えた後、同じ文を**引用符なし**で指す後続claimが本文から消えて`mismatch`になり、**L6が書き換え済みの文を「復元」して2回目のRewrite**(guard失敗→ladder枯渇)。rep24(L6 OFF)では同じclaimが`covered_by_earlier_rewrite_in_cycle`で合格。是正=carry-forwardをL6より先に適用(実装済み、追加call 0)。¥0 replayで解消確認。
3. 是正の副産物: rep26(6記録)・rep27(9記録)の`L6`関与の復元を再現すると、**変わった記録は全て「書き換え済みの文を後続claimが復元して再Rewrite」型**(neg5 HF-007 3件=旧は`issue_focus_absent`でRewriteなし、`changed_number` F-002=旧は不要な二重Rewrite成功、A4×2、A5×1)。先行Rewriteの無いcycleでL6が単独で働いた実例は証跡に0件(L6の本来用途の価値は未観測)。
4. neg3: **Recheck・再確認のraw応答はどのログにも未保存**(確認)。promptは再構築しSHA一致で検証。Recheckが`COMPLIANT∧all_prior=False`になる自己矛盾は**neg3で28回中23回・neg2で8回中7回・他382回中3回**(neg3/neg2にほぼ恒常的)。再確認は21回中5回(24%)DEVIATION、これが最終STAGE4(再確認の`deviations`は従来捨てている・未保存)。今回、次run用に記録専用を追加。
5. 案N1(再確認DEVIATIONを通常のStage 2経路へ合流、追加call 0)を推奨、N3併用候補、N2不採用。Production配線は未設計(再確認callがTrial専用)。

### A4/A5 rep27 s1の記録(確認、`er052_output/open233_self_recovery_flow_runner_01_rep27/instances_s1/safety_A4.json`・`safety_A5.json`)

| instance | rec | claim(Checker文字列、先頭) | level | method | guard_ok |
|---|---|---|---|---|---|
| A4 | 0 | “Through Muse, trained human contract workers ... with users.”(引用符付き) | L1 | e1_minimal_word_edit | True(`users`→`the people they called`) |
| A4 | 1 | “One helper meant one more person handling private data.” | L1 | e1 | True(`meant`→`could mean`) |
| A4 | 2 | Through Muse, ... with users.(引用符なし、rec 0と同じ文) | **L6** | e2_paragraph_rewrite_guard_failed | **False**(書き換え済みの`...the people they called.`を復元→再Rewrite→全水準guard失敗→STAGE4) |
| A4 | 3 | One helper meant one more person handling private data.(引用符なし、rec 1と同じ文) | **L6** | e1 | True(書き換え済みの`could mean`を復元→不要な再Rewrite) |
| A5 | 0/1 | MUSE-HC-012の同型 | L0 / **L6** | e2_generic / guard_failed | True / **False**→STAGE4 |

rep24(L6 OFF)・同instance・同claim: rec 2・3(A5はrec 1)=`covered_by_earlier_rewrite_in_cycle`(Rewriteなし)。A4 s1=RESOLVED_REWRITE_THEN_DOWNGRADE、A5 s1=RESOLVED_REWRITE。

### replay結果(確認、`replay_cf_l6_order_01.json`。記録済みclaim・先行Rewriteの成功置換からRewriteの有無を決定論再現、coreはスタブ)

是正後のtest(runner単体608・er052回帰652 pass、全体回帰は基準11件=6 failure+5 error以外の新規なし): A4 rec 2・3、A5 rec 1=`covered_by_earlier_rewrite_in_cycle`(`l6_skipped.rule=cycle_start_match`、Rewriteなし)。是正前は全て再Rewriteが走る。他: neg5 HF-007(rep26 s1・s2、rep27 s1)・changed_number F-002(rep27 s1)も同様にcoveredへ(上記)。A2A3(rep26・27)の復元は元々carry-forward経由で変化なし。**規則(2)(復元範囲=先行Rewriteの置換後の文)は、実データでは全て規則(1)でも確定しており、(2)単独が効いた実例は無い(合成unit testのみ)**。

### neg3 rep27 s1(確認と未確認、設計書§12-2)

- 対象claim(In one line): `The fee plan left the stage, but the events driving oil prices—and the prices themselves—quickly returned.`(HF-009、`deterministic_floor:changed_time`、LLM=BLOCKING)。Rewrite後(regenあり、同じ文に収束): `The fee plan left the stage, but the prices themselves quickly returned.`
- Recheck: `LEDGER_COMPLIANT`、記録された`deviations=[]`、`all_prior_issues_resolved=False`(=`len(resolved)==len(prior_issues)`かつ全resolved、の否定。prior_issuesは1件)。**`prior_issues_resolved`のraw内容は未保存**。
- 再確認: `LEDGER_DEVIATION`、`all_prior_issues_resolved=True`(cite-or-release後、released 0)。**deviationsの件数・severity・claim・issueは未保存=仮ラベル不能**。
- `prior_issues`(promptをSHA一致で再構築、`rca_neg3_prompt_reconstruct_01.json`): `fact_id=HF-009 | claim_in_article=The fee plan left the stage, but the prices themselves quickly returned.(現行本文) | issue=The sentence describes the events as having quickly returned and as driving oil prices, whereas HF-009 reports ... It changes continued events into returning events and asserts a causal role ... | explanation=The timing changes from concerns that continued to events that returned, ...`(issue・explanationは書き換え前の文の欠陥を述べたまま)。再確認call末尾に`before`/`after`の対が添付される。
- Rewrite後の文はLedger HF-009(価格は一時的に上げ幅を縮めた後、発表前に近い水準へ戻った)と照合して問題なし(Sonnet目視)。neg3は`ACCEPTABLE(Normal群)`記事。
- 同一の書き換え後の文での再確認結果: rep23 s2=DEVIATION・rep27 s1=DEVIATION・rep26 s2=COMPLIANT(同文で割れた=確認callの非決定性)。「出来事の継続を残す」書き換え3件(rep23 s1・rep26 s1・rep27 s2)は全て再確認COMPLIANT。

### 集計(確認、全instance JSON 521件、`agg_stage4_reasons_01.json`)

- `unconfirmed_after_reverify` 10件: neg3 7(iter3・4・5・6、rep9・23・27)+neg2_meta_refresh_a2 3(iter3・4・5)。iter5以降の6件は`DEVIATION∧all_prior=True`(released 0)。再確認のdeviationsを記録したログは0件。
- 自己矛盾(Recheck `COMPLIANT∧all_prior=False`): 418 Recheck中33(7.9%)、neg3 23/28・neg2 7/8・他3/382。再確認を呼んだneg3 21回中DEVIATION 5回、neg2 6回中1回。再確認DEVIATION 6件は全て最終STAGE4。
- cycle別件数(最終cycle数): rep24=0 cycle 7・1 cycle 24・2 cycle 7、rep27=0 cycle 8・1 cycle 28・2 cycle 2、rep26(8 run)=全て1 cycle。**cycle 3到達は0件**(rep24・26・27)。

### 比較表(設計書§12-3、案N1〜N3)

| 観点 | N1 再確認DEVIATIONをStage 2経路へ | N2 再確認2回 | N3 prior_issues明確化 |
|---|---|---|---|
| HR効果 | 再確認DEVIATION 6件がStage 2へ。STAGE4はcycle 2以降の既存経路のみ。実測は次run | 割れた分はN1。自己矛盾(neg3 82%)は減らない | 効果不明(rep26・27で現行本文化後も4/4自己矛盾) |
| Safety | DEVIATION側(安全側)。Stage 2の既存降格ガードは不変 | 同左 | 不変 |
| 不要Rewrite | 軽微以下はStage 2で降格。BLOCKINGのみRewrite | 同左 | 増えない |
| 費用 | 追加call 0 | +約¥0.27/再確認(neg3/neg2は事実上毎回) | 0 |
| 非決定性 | 増えない | 増える方向 | 増えない |
| cycle上限 | 既存の内側、cycle 3実績0 | 同左 | 影響なし |
| Production整合 | 再確認callがTrial専用。再検査経路の設計と一体 | 同左+call増 | `er003`678行はProduction共通 |

### 棚卸し表(設計書§12-3、確認)

| 経路 | runner行 | 全ログ | rep24・26・27 | 扱い |
|---|---|---|---|---|
| violation_span_unverified | 7951 | 6 | 2 | L6で縮小済み(L6単独の価値は未観測)。技術是正 |
| ladder_exhausted_without_full_rewrite | 7970 | 10 | 2(rep27 A4・A5) | 是正(a)で縮小。他の発生は旧構成で未分析 |
| unconfirmed_after_reverify | 8276 | 10 | 1(rep27 neg3) | 設計N1 |
| cycle_limit_exhausted(_after_recheck) | 7834/8309 | 9/6 | 0 | 上限は既存安全装置、触れない |
| same_claim_fact_id_reblocked | 7791 | 23 | 0 | 旧構成のみ |
| ja_deviation_unresolved | 7738 | 12 | 0 | english_onlyで無効 |
| target_not_locatable / degenerate_rewrite_output | 7951/8055 | 2/2 | 0 | 旧構成のみ |

---

## (c) 必要なProduction code/spec sectionの該当行範囲のみ

| ファイル | 行範囲 | この範囲が必要な理由 | Grep確認 |
|---|---|---|---|
| `er052_open233_self_recovery_flow_runner_01.py` | 5174〜5200 | `_resolve_claim_string`: 既存照合が`mismatch`のときL6(`vs_sentence_restore_resolve`、4961)を試す入口=是正前にcarry-forwardより先に走った箇所 | 済(Grep `def _resolve_claim_string`) |
| 同 | 6316〜6365 | `carry_forward_resolution`: cycle開始時点の本文で照合し、先行Rewriteの置換単位(`before_units`)に含まれればcovered(委任_04の部分一致=同issue・同fact_id・同flagのときのみ) | 済 |
| 同 | 6377〜6430 | **新設** `_resolution_used_l6`・`l6_carry_forward_precedence`(規則(1)carry-forward、規則(2)復元範囲=`after_units`) | 済(Grep `def l6_carry_forward_precedence`) |
| 同 | 6448〜6520 | `run_stage3_for_claim_spans`: L6復元の確定を、先行Rewriteがあれば`l6_carry_forward_precedence`へ通し、covered時は`handoff.resolution.l6_skipped`を記録 | 済 |
| 同 | 7889〜7912 | `_run_stage3_cycle`: cycle内の各claimへ`cycle_start_en_text`・`cycle_replaced_units`を渡す | 済 |
| 同 | 8238〜8280 | `en_ambiguous`(自己矛盾)→再確認→`unconfirmed_after_reverify`(8276)→`stage1_deviations`をRecheck本体から作る(8280、再確認のdeviationsは使わない) | 済 |
| 同 | 1774〜1776・1878〜1935 | `all_prior_issues_resolved`の計算式(`er003` 826行と同一)、`run_recheck_confirm`(cite-or-release) | 済 |
| `er012_e_family_entertainment_two_level_runner_01.py` | 410〜430 | Productionの再検査(再生成後に`COMPLIANT∧all_resolved`でなければSTOP)。再確認callは無い | 済(Sonnetが行範囲をRead) |
| `er003_v1_en_direct_vfl_01_generate.py` | 678・820〜830 | `build_prior_issues_instruction`(Production共通)・`all_prior_issues_resolved`計算 | 済(Grep) |

---

## (d) Sonnet要約

L6とcarry-forwardの順序は、rep24(L6 OFF)で通っていた経路をL6が先取りして壊した事実が実データ(A4/A5の記録とrep24対比)で確認でき、是正は決定論・追加call 0で、¥0 replayで二重Rewriteの解消を確認した。ただし是正前にL6が単独で働いた実例はrep26・27に無く、L6の本来の価値は未観測のまま(論点4)。neg3は、**raw応答が保存されておらず再確認のdeviationが何かは不明**で、案N1〜N3は仮説(自己矛盾はneg3/neg2に恒常的、再確認DEVIATIONは約24%)に基づく設計判断である。N1が有力でも、再確認のdeviationsがStage 2で降格されるかは未測定(次runで逐語を記録する追加済み)。Production配線は再確認callがTrial専用のため別設計が必要。懸念: N1で再確認が拾う指摘がBLOCKINGになった場合の不要Rewrite増、自己矛盾(neg3 82%)自体の根本原因(prior_issuesのissue/explanationが書き換え前の文を述べたまま、の推定)が未検証。

---

## (e) Progressive Disclosure手順(Opus向け指示文)

> 上記(a)〜(d)で診断できない場合のみ、追加でファイルを読んでよい。ただし読む前に「読む理由」と「対象ファイル・行範囲」を1行で宣言し、診断結果の最後に「追加で読んだファイル一覧と概算文字数」を自己申告すること。無宣言での巨大ファイル全文読み込みは禁止。診断精度を優先し、必要な事実を省いてまで読込量を減らしてはならない。

---

## (f) 入力文字数の自己計測欄

- (a)論点セクション(論点と材料の対応チェック含む): 約1577字
- (b)主要数値表・要点セクション(A4/A5記録・replay結果・neg3逐語・集計・比較表・棚卸し表を含む。記事本文の転記は対象外[本委任は記事本文を扱わない]): 約5869字
- (c)Production code/spec抜粋セクション(Grep確認欄含む): 約1469字
- (d)Sonnet要約セクション: 約519字
- (e)Progressive Disclosure指示文: 約208字
- packet合計文字数: 約12604字(目安2万字以内。独立レビューブロック[(g)]約1,100字を含む)
- 前回packet(`opus_packet_open233_kpi_recovery_02_01.md`)との差分: 今回は記事本文の転記が無い代わりに、neg3のprompt逐語・集計表・案比較表・棚卸し表を転記した。これにより不要になるProgressive Disclosure読込先は、各instance JSON(neg3 rep23/26/27)と`design_open233_kpi_recovery_02.md` §12(約25,000字)。
- 注記: raw応答(Recheck・再確認)は元データに存在しないため、packetにも載せられない(未保存の事実として明示)。

---

## (g) 発火条件の記入欄と独立レビューブロック

- 発火条件: **条件A**(新しい構造・処理フローの設計): 再確認DEVIATIONの処理設計案N1〜N3(retry/再検査経路の変更)と、L6/carry-forwardの順序という処理フローの変更。条件B(同じ問題へ2回修正後の再発)にも関連: neg3の`unconfirmed_after_reverify`はiter5〜rep27で5回出現し、その間に委任_01(現行本文化)等の是正が入っても再発。「個別バグの連続か、根本設計(再確認のdeviationsを捨てる設計)か」の判定を求める。
- 重複レビューの確認: 同じ内容の既存Opusレビュー=無し(`opus_packet_open233_kpi_recovery_02_01.md`はStage 2後段Safety設計[Opus#11]で別内容)。再レビューではなく新規。

---
【Opus独立技術レビューの目的】
あなたの役割は「重要な技術設計に対する独立レビュー」である。Claude/Fableの案を
追認することが目的ではない。必ず次を独立に評価すること。
- そもそもその設計が必要か
- より単純な方法がないか
- 既存処理をそのまま利用できないか
- 不要な複雑化をしていないか
- 根本原因に対する対策になっているか
- 別のFailureを生まないか

【最低限、独立してレビューする12観点】
1. そもそもこの変更・設計は必要か
2. より単純な構造にできないか
3. 既存処理・既存データを利用できないか
4. 前段で取得済みの情報を後段で失ったり再探索したりしていないか
5. 不要なLLM処理を追加していないか
6. 非決定性を増やさないか
7. Human Reviewを増やさないか
8. 不要Rewriteを増やさないか
9. コストを不必要に増やさないか
10. retry / fallback / regenerationと矛盾しないか
11. Failure時に安全側へ倒れるか
12. 個別パッチではなく再発防止になっているか

【追加観点(発火条件別)】
- 条件B(同じ問題へ2回修正しても再発): 「個別バグの連続なのか、根本設計に問題があるのか」を
  必ず明示的に判定すること。
- 条件C(Production採用候補の最終レビュー): 次の6点も必ず確認すること。
  Trial専用実装になっていないか / Production全体で矛盾しないか /
  初回・retry・fallback間で仕様が一致しているか / Dangling Referenceがないか /
  Failure時に安全側へ倒れるか / QCD上の新しい問題を生まないか。
  これはユーザーのProduction採用判断を代替するものではない(採用可否は
  人間ユーザーのみが決める。あなたは採用可否を宣言しない)。

【レビューの姿勢】
Claude/Fableの案を前提として追認しない。代替案の方が良い場合は、その代替案を
明確に提案すること。結論は「必要/不要」「推奨構造」「リスク」「代替案」の順で
簡潔に返す。
---

