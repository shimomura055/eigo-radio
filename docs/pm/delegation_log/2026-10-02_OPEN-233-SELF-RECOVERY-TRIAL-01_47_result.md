抽出元: `C:/Users/tensh/.claude/projects/C--Users-tensh-eigo-radio/f9ae115b-0305-437d-ac2d-b452b22a5e2a/subagents/agent-ac88cbc42b80c26c8.jsonl`のSubagentHandback message。本文は改変していない。

---

## OPEN-233-SELF-RECOVERY-TRIAL-01 委任_47 報告(read-only照合、費用¥0、LLM/API/Trial再実行なし)

### 1. 結論(10行)
- 問1-5: 「Safety-criticalな文が元のまま残り・一度もBLOCKINGで指摘されず・人間確認なしで終了」した実行は、新方式(rep22 T1)が 3/4(s1・s3・s4)、旧方式(固定入力7実行)が 1/7(rep21 s2)。委任_46の途中観察は確定記録で追認された。委任_46の results_01.json と 11実行すべて一致した。
- 委任_42報告の「false PASS 0」は「検出済みBLOCKINGが未解消のまま合格した例が0」という意味で、正解ラベルとの照合ではない。この意味では事実と合う。ただし正解ラベル(Meta-1)で照合すると上の 3/4 になる。
- 問1-4: runnerには評価関数 `detect_safety_critical_misdowngrades` があり、rep22スクリプトはT1にだけ実行して記録値は `[]`。この関数は「指摘された後に降格された」件しか見ない。一度も指摘されなかった文は構造的に拾えない。T2・T3は未評価。
- 問2: 「LLM判定BLOCKING→規則でQUALITYへ降格」は 3件。s1・s3・s4の最終周回の指摘は各1件で、すべて MUSE-HC-012「They enjoyed AI's convenience...」。降格規則は `apply_disclosure_gap_downgrade`。この文はs2と旧方式の複数実行ではBLOCKINGになっている(揺れ)。設計書の正解ラベル表に、この文の個別行はない。
- 問3: 成功条件5項目のうち、項目2(縮小なし)は読み方によらず「満たす」。項目1・3・4・5は読み方による(詳細は問3)。
- 問4: 新方式は周回・call・費用が小さい。ただし旧方式は古いコード版を含み、n も小さいため因果は断定できない。T2の水準③棄却は、語 `users` が同じ段落の確定範囲の外に既にあった。ガードは確定範囲(target)だけを比較している。T3の carry_forward では後続claimの issue はRewriteに渡っていない(後続のRewrite呼び出しは0回)。

### 2. 詳細

#### 問1 表(最終EN記事に「Also, some calls needed user information to continue.」が元のまま残るか。完全一致、空白正規化のみ)
| 実行 | final_state / Stage4理由 | 周回 | 文が元のまま残存 | HC-010がBLOCKINGで指摘された周回 | Meta-1/2評価(SAFETY_CRITICAL_CLAIM_DEFS照合) | 対象パターン |
|---|---|---|---|---|---|---|
| T1 s1 | RESOLVED_REWRITE_THEN_DOWNGRADE / - | 2 | 残る | なし | 該当claimなし | **該当** |
| T1 s2 | STAGE4_ESCALATION / cycle_limit_exhausted | 3 | 変更あり | cycle2(BLOCKING) | Meta-1 cycle2 BLOCKING | 非該当 |
| T1 s3 | RESOLVED_REWRITE_THEN_DOWNGRADE / - | 2 | 残る | なし | 該当claimなし | **該当** |
| T1 s4 | RESOLVED_REWRITE_THEN_DOWNGRADE / - | 2 | 残る | なし | 該当claimなし | **該当** |

- s2の最終文(逐語): 「If a call needs user information, it may be shared by mistake with call center contract workers.」(cycle2の水準④で書き換え)
- T2(2周目再現、1周のみ):
  - 最終状態は両sampleとも `UNRESOLVED_AFTER_ONE_CYCLE`(合格ではない)。
  - 文は両sampleで書き換え前後とも残存した。
  - T2 s1: Recheck(EN)で HC-010 の指摘なし。
  - T2 s2: Recheck(EN)で HC-010 を severity=MAJOR で指摘(逐語 claim「Also, some calls needed user information to continue.」)。T2ではStage 2を実行していないため、BLOCKINGかどうかは未確定。
- T3(`safety_er009_changed_number`):
  - 別記事で、このinstanceは `SAFETY_CRITICAL_CLAIM_DEFS` に未登録。
  - 正解ラベルは設計書7-1/7-0-iter4「er009_changed_number=BLOCKING(改竄数値 more than 30 million、Ledger値F-002 1,300万件超)」。
  - 結果は `RESOLVED_REWRITE`。「more than 30 million」は最終記事に残らない。最終記事の逐語は「Researchers studied more than 13 million credit card payments in New York City taxis, and found that higher suggested tip rates led passengers to leave more money.」。
  - 改竄claimは cycle1 で BLOCKING 2件(`deterministic_floor:changed_number` と `precheck_floor`)。Recheck は LEDGER_COMPLIANT、`all_prior_issues_resolved=True`。
- 1-4(runnerの評価の有無):
  - 評価関数は `er052_open233_self_recovery_flow_runner_01.py` 5689-5714行 `detect_safety_critical_misdowngrades`、定義は 5659-5686行 `SAFETY_CRITICAL_CLAIM_DEFS`。
  - rep22スクリプト 113行がT1にだけ実行。記録値 `summary_rep22.json` の `safety_critical_misdowngrade_rows` は `[]`。
  - T2はinstance JSONに `cycles` キーがなく対象外。T3は登録外。どちらも未評価。
  - 私のスクリプトでの再照合では、T1 s2 の Meta-1 が cycle2 で BLOCKING で、降格なし。他の3実行は Meta-1/2 に該当するclaimがそもそも存在しない。
- 1-5 並べ表(新方式 T1 4実行 / 旧方式 固定入力7実行):

| 項目 | 新方式 | 旧方式 |
|---|---|---|
| 文が最終記事に元のまま残る | 3 | 4 |
| HC-010(文)がBLOCKINGで指摘された実行 | 1(s2) | 4(iter8 s1・rep19 s1・rep20 s1=cycle2、rep21 s1=cycle3) |
| Stage 4で終了 | 1 | 5 |
| 対象パターン | **3** | **1(rep21 s2)** |

- 旧方式の「残るが未指摘」は 3 実行(iter8 s2、rep20 s2、rep21 s2)だが、うち iter8 s2 と rep20 s2 は Stage 4 に落ちて人間確認になっている。新方式の「残るが未指摘」3実行は3つとも解消扱いで終了している。
- 旧方式7実行の内訳: iter8 s1/s2、rep19 s1、rep20 s1/s2、rep21 s1/s2(固定Stage 1と claim が一致するものを機械抽出)。

#### 問2 s1・s3・s4 の最終周回(cycle2)の指摘(全件。各実行1件)
共通項目:
- `related_fact_id`=MUSE-HC-012、Checker severity=MAJOR、Stage 2のLLM判定=BLOCKING、最終判定=QUALITY。
- floor理由=`disclosure_gap_negative_inference_downgrade(委任_18 2-2)`。降格関数は runner 2040-2066行 `apply_disclosure_gap_downgrade`。
- `floor_cited_materiality`=BLOCKING、`floor_cited_reason`=null、route=body、detected_by=stage1_llm。

| 実行 | claim_in_article(逐語) | issue(逐語) | trueのフラグ |
|---|---|---|---|
| s1 | “They enjoyed AI’s convenience, but a human was on the other end. They did not realize it.” | This presents users’ enjoyment and lack of awareness as actual experiences. The Ledger supports that the test began without appropriate disclosure, but does not establish what users actually thought or realized. | changed_fact, unsupported_new_claim |
| s3 | They enjoyed AI’s convenience, but a human was on the other end. They did not realize it. | The article presents users’ enjoyment and lack of awareness as facts. The Ledger confirms human-handled calls and a disclosure concern, but does not establish users’ actual reactions or that they did not realize a human was speaking. | changed_fact, changed_certainty, unsupported_new_claim |
| s4 | “They enjoyed AI’s convenience, but a human was on the other end. They did not realize it.” | The article states as fact that users enjoyed the service and did not realize a human was handling the call. The Ledger reports a test without appropriate disclosure, but does not establish users’ actual awareness or experience. | changed_fact, changed_certainty, unsupported_new_claim |

- **LLM判定BLOCKING→規則でQUALITY降格は3件**(上記3件すべて)。この3文は3実行とも最終EN記事にそのまま残る。
- 重大度の揺れ(同じ文・HC-012、固定入力11実行の全周回25行を機械照合):
  - HC-012の24行のうち、LLMがBLOCKINGは23行、LLMがQUALITYは1行(s3 cycle1)。
  - 最終BLOCKINGは3行: s2 cycle3(floorなし)、iter8 s1 cycle3(floorなし)、rep19 s1 cycle2(floorなし)。
  - 20行は規則でQUALITYへ降格された。
  - 他に iter8 s2 cycle2 が MUSE-HC-007 でBLOCKING(包含一致で拾った別factの行)。
- 設計書の正解ラベル:
  - `Meta_run03_standard` はfixture単位で BLOCKING(7-1 negative control)。
  - claim行で明記されているのは Meta-1/Meta-2(「Also, some calls needed user information to continue.」)だけ。
  - 「They enjoyed AI's convenience...」はclaim単位のBLOCKING正解ラベル表に載っていない。
  - この文を降格する規則(委任_18 2-2、設計書 1228-1246行)は意図して導入されたTrial限定の判定候補で、Production採用には別途ユーザー承認が必要と書かれている。
  - HC-011(単数化)は「数値・規模の歪曲でBLOCKING維持が正しい」(設計書 3141-3147行)。
- 付記: s1・s3・s4 の cycle1 で HC-011 の2文は「during one call / a call」「This call」に書き換えられた。Recheckで再指摘はなし。この書き換え自体の正否はこの委任では未確認。

#### 問3 成功条件5項目(`DECISION_LOG.md` 17042-17050行の原文を逐語)
成功条件:
- 2文取りこぼしによるHuman Review 0
- Checkerが示した違反範囲を勝手に縮小しない
- 誤って危険な記事をPASSしない
- Rewrite範囲は最小修正優先
- 不要な段落・全文Rewriteを増やさない
- 費用は既存予算内で最小限にしてください。

| 項目 | 当てはめ(材料) | 判定 |
|---|---|---|
| 1 | T1: 2文claim(HC-011)が4/4で①の対象。取りこぼし起因のStage 4は0。s2のStage 4は別原因(HC-010の初検出、HC-012の揺れ)。 | 「取りこぼし起因のHuman Review」なら満たす。「Human Review全体」と読むと、T1の1/4(s2)が残るので満たさない。T2は1周で終了、JA未解消のためHuman Reviewの判定は範囲外(未確認)。 |
| 2 | 水準①の試行6件(T1 4+T2 2)で「対象==確定範囲」6/6、不一致0。縮小0。carry_forward でも範囲を縮小していない。 | 満たす。ただし「Checkerが範囲を示さなかった文」(HC-010の未指摘)はこの条件の対象外。 |
| 3 | 検出済みBLOCKINGの未解消合格は0。T3は改竄数値が是正。一方、Meta-1(Safety-critical)が残るまま未指摘で合格が T1 3/4。HC-012は3件が規則降格でQUALITYのまま合格。 | 「検出済みBLOCKINGが未解消でPASS」と読むと満たす。「正解ラベルでBLOCKING対象の文が残ってPASS」と読むと満たさない(3/4)。HC-012は正解ラベル表に行がないため、読み方次第。 |
| 4 | 開始水準: T1は①(s2 cycle2のHC-010のみ既存規則で④開始)、T2は①を試行し declined、T3は③開始(既存規則)。 | 「既存の水準選択規則に従った最小」なら満たす。「常に①から」だと T1 s2 cycle2 と T3 は満たさない(2件)。 |
| 5 | ⑥は0件。④はT1で1/4、旧方式の同じ入力では4/7実行で④成立(analysisの旧4実行では1/4)。T2は④でしか成立せず(旧方式は全水準失敗でStage 4)。T2の④は①declined後、③が `users` ガード棄却(問4-2)。 | T1だけなら増加なし。T2の④は、ガード棄却が妥当ならやむを得ない・不当なら増加と読める。 |

費用: ¥8.1025(Guardrail ¥15の54%)。analysis_rep22.json の合算と手計算で一致。

#### 問4
**4-1 周回・call・費用・成立水準**
- 新方式 T1: s1(2周・4call・¥1.121・①1)、s2(3周・7call・¥2.1773・①1と④1)、s3(2周・4call・¥1.314・①1)、s4(2周・4call・¥1.0118・①1)。
- 新方式 T2: 各1周・6call・¥1.0338 / ¥1.0143。成立水準は④のみ。
- 新方式 T3: 1周・3call・¥0.2311。成立水準は③1件と、後続claimのスキップ1件。
- T3 run1(是正前): 1周・2call・¥0.1992、`violation_span_unverified` で Stage 4。
- 旧方式7実行:
  - iter8 s1: 3周・17call・¥5.1772・①5/③2/④2、Stage 4(same_claim_fact_id_reblocked)
  - iter8 s2: 2周・14call・¥2.9468・①4/③2/④1/none1、Stage 4(target_not_locatable)
  - rep19 s1: 3周・31call・¥6.2845・①10/③3/④1、Stage 4(cycle_limit_exhausted_after_recheck)
  - rep20 s1: 3周・7call・¥2.0186・①1/④1、RESOLVED_REWRITE_THEN_DOWNGRADE
  - rep20 s2: 2周・7call・¥1.8301・①1/none1、Stage 4(ladder_exhausted_without_full_rewrite)
  - rep21 s1: 3周・8call・¥2.1567・①2、Stage 4(cycle_limit_exhausted)
  - rep21 s2: 2周・4call・¥1.2052・①1、RESOLVED_REWRITE_THEN_DOWNGRADE
- 合計: 新方式T1は19call・¥5.6241。旧方式7実行は88call・¥21.6191。

**4-2 T2で水準③が棄却された件(2件、s1・s2とも同じ)**
- 棄却の根拠語: `users`。③の revised の2文は ["Without a clear explanation, users might not know if it was AI or a person.", ""]。
- 同じ段落の書き換え前に `users` は既存: 「If no one explained this clearly, users could not know.」
- 確定範囲(「They could not tell if it was AI or a person」「They did not realize it.」)の内には `users` はない。段落内の確定範囲の外にある。
- ガード: runner 423-441行 `actor_rewrite_guard_ok`(`_ACTOR_NOUN_PATTERN`)。呼び出しは 3820-3824行(paired経路)。同様のガードが 3364・3530行(single経路)にもある。
- ガードは `lv["en_target"]`(target)と revised の主体語集合だけを比較する。新語がLedgerの小文字化テキスト(JAのみで、runner import探索で `users` を含まないことを確認)に無ければ棄却する。
- 水準①は両sampleで `declined`。④の結果は s1 が Recheck(EN)で LEDGER_COMPLIANT、s2 が Recheck(EN)で元からのHC-010のみMAJOR、JA Recheckは両方 `ja_ok=False`(JA未解消)。
- ④の書き換え後の文(逐語): s1「Meta later called the test a mistake because people were not told clearly.」/ s2「Meta later said the test began without proper notice.」。この内容がLedgerで裏付けられるかは未確認。

**4-3 carry_forward_resolution(T3、1件)**
- 先行claim: 検出元 stage1_llm、related_fact_id=null、`deterministic_floor:changed_number`、issue 逐語「記事は対象取引数を「3,000万件超」としているが、Ledgerが確認しているのは「1,300万件超」であり、3,000万件超という数値は裏付けられていない。チップ額への効果の記述はLedgerと一致する。」
- 後続claim: 検出元 precheck、related_fact_id=F-002、`precheck_floor`、issue 逐語「precheck detected number_mismatch vs ledger_value=1,300万件超」
- 先行claim の rewrite_hint は「more than 30 million」→「more than 13 million」置換。実際の Rewrite も 30→13 million。後続claimの `claim_in_article` は先行と完全に同一(同じ1文)。
- 後続claimの issue は Rewrite の指示文には渡されていない。後続の rewrite_records は `level_attempts` が0件(Rewrite LLM call 0回、`covered_by_earlier_rewrite_in_cycle`)。
- コード: `carry_forward_resolution` は runner 3978-4008行、呼び出し元 `run_stage3_for_claim_spans` は 4011-4050行。判定は「後続の範囲が先行Rewriteの before_units に含まれるか」だけで、後続の issue が先行の書き換えで解消するかは見ない。解消の判定は全文Recheckに任せる設計。
- 記録上は Recheck が LEDGER_COMPLIANT、`all_prior_issues_resolved=True` で、後続の issue(数値)も解消した。
- 本件では先行・後続が同一の数値問題。issue が異なる別内容の2claimが同じ文を指す場合は、本Trialでは未検証。

### 3. 検算・限界
- 検算:
  - 旧方式の固定入力7実行の件数(対象パターン1)は委任_46の results_01.json と一致した(11実行すべて一致)。
  - 費用合算: T1 ¥5.6241、T2 ¥2.0481、T3 ¥0.4303、合計 ¥8.1025 で analysis_rep22.json と一致。
  - 委任_42の報告値(final_state・周回・call・費用・水準別の成立)と記録に矛盾はなし。食い違いは「false PASS 0」の定義(上記)のみ。
- 限界・未確認:
  - 旧方式7実行は iter8〜rep21 のコード版が混在し、n も小さい。新旧の差(3/4 対 1/7、HC-010指摘 1/4 対 4/7)の因果は断定できない。Checkerの非決定性による揺れの可能性は排除できない。
  - T2は1周限定の再現で、最終合否の判定材料にならない。
  - T2 ④の書き換え内容のLedger裏付け、HC-011の「calls→one call」書き換えの正否は未確認。
  - T2のガードの「Ledgerに `users` が無い」は、runner を import した一時探索(保存せず)で確認した。作成スクリプトでは再検証していない。
  - HC-012「They enjoyed AI's convenience...」の正解ラベルがBLOCKINGかどうかはSSOT上で未確定。

### 4. 読んだファイル・行範囲・作成ファイル
- 読んだ範囲:
  - `er052_output/open233_missed_detection_truth_check_01/check_01.py`(全文)、`results_01.json`(スクリプトで抽出)
  - rep22 の `analysis_rep22.json`、`summary_rep22.json`、各instance JSON(スクリプトで抽出)
  - runner: 414-441、2040-2070、3770-3840、3960-4069、5645-5714行
  - `er052_open233_self_recovery_flow_runner_01_rep22_representative_01.py` 96-115、320-410行
  - `DECISION_LOG.md` 16977-17066、17243-17272行
  - 設計書(`docs/pm/design_open233_self_recovery_flow_01.md`)1226-1247、1296-1310、3128-3152、3240-3305、3425-3455、3481-3541、3611-3650、3711-3755行
- 一覧外の追加Read: 設計書 1226-1247・1296-1310・3128-3152・3240-3305 行(HC-012の降格規則・揺れの正解ラベル位置づけの確認のため)、runner 2040-2070・414-441・3770-3840 行(降格関数名・ガードの正確な位置のため)、および runner import の一時探索1回(ledger_text と主体語抽出の確認。LLM呼び出しなし、ファイル保存なし)。
- T-0: `check_delegation_prompt.py` の結果は **FAIL**。理由は「プレースホルダ混入: 同上x1」(委任文中の「同上」を検出、記録用で作業は継続)。
- 作成ファイル(すべて未追跡、git操作なし):
  - `C:\Users\tensh\eigo-radio\er052_output\open233_rep22_truth_label_check_01\check_rep22_01.py`
  - `C:\Users\tensh\eigo-radio\er052_output\open233_rep22_truth_label_check_01\results_01.json`
  - `C:\Users\tensh\eigo-radio\er052_output\open233_rep22_truth_label_check_01\cases_01.csv`
  - `C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_47.md`
  - `C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_47.md_check.json`
