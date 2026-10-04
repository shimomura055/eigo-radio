# OPEN-233 Self-Recovery Production Wiring Gap棚卸し(rep30有効構成 vs 量産Production実装 1対1対応表)

管理ID: `OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01`(委任_02、2026-10-05)。性質: ¥0・調査と文書作成のみ(コード変更なし、SSOT未編集、commit/pushなし)。
根拠のユーザー決定: 2026-10-05(Trial=VALIDATED、rep30有効構成すべて`APPROVED_FOR_PRODUCTION`、Gate 3[完了条件1〜12]達成後のみ`PRODUCTION_WIRED`、Trial専用`er052_*`のProduction暗黙参照禁止、OFF/REJECTED候補を混ぜない)。**全文は委任_01が`DECISION_LOG.md`へ記録中のため、本文書作成時点(Grep確認)では`DECISION_LOG.md`に2026-10-05エントリは無い**。以下「2026-10-05一括承認」はこの未記録エントリを指す。
区別: **確認**=Grep/Readで実物確認、**推測**=確認していない推論、**要確認**=本調査で判定できず。

---

## 0. 先に結論

1. rep30有効構成: スイッチ22個(`KPI_TRIAL_SWITCHES`の値ON/指定あり22。内訳は§1)+スイッチ化されていない常時有効の機構10種+rubric V7b。ユーザー列挙は個別23項目+「その他」1項目(委任文は「22項目」とするが数え直すと23+その他。本文書はU1〜U24と採番)。**全24項目でProduction側に実装済みのものは0件**(`git grep -n "er052_open233" -- er003*/er009*/er010*/er012*/er019*.py`は0件を再確認)。
2. Production現状は「Checker(`vfl01.run_deviation_check`)→MAJOR→`er010`の文単位Local Rewrite(最大3 attempt×3 cycle)→cycle尽きたら`NG_REVIEW_REQUIRED`/STOP」という**別設計**。rep30の中核(Stage 2 materiality/S1/floor/位置オブジェクト/ladder/許可リスト出口)に対応する経路が無い。
3. Gap種別(U1〜U24、§3): **主たる種別でA=3(U4/U5/U6。関数群は純移植可能だが組込みはB併記)、B=5(U2/U10/U14/U23/U24)、C=16、D=0**(合計24。C+Bの併記を持つ項目[U1/U13/U17/U21]は主たる種別Cで計上)。Dは0(同等実装なし。U2のP3〜P5が暗黙に英語のみである点のみD相当の注記)。
4. **重要な新規発見(確認)**: (a)`er052_open233_self_recovery_stage2_production_01.py`の`MATERIALITY_RUBRIC_V7B`(L74)は**rep30が使うV7bと別物**(rep30は`s2c.RUBRIC_R3_TRIPLE_PRIME_WITH_MISCONCEPTION_PRINCIPLE_V7B`、calibration module L612。同ファイルL63-64のコメントも「現行flowはs2c側」と明記)。「器が既にある」前提でこのモジュールから配線すると**誤ったV7bを配線する**。(b)runnerは`er050`/`er051`/`er052_*`の7 moduleに依存(§2-7)。Stage 1もProductionの`vfl01` Checker promptではなくTrial版(`er051` V4A+misconception principle)。(c)TrialはModel Routing Contractを経由せず`gpt-6-luna`固定、Production`vfl01.MODEL=routing.WRITER_MODEL`("gpt-5.6-luna"、L57)。
5. 構造的競合候補(§4-3): **有り**。要設計(競合ではなく設計判断が要るもの)8件、競合の可能性が高いもの3件(cycle上限の定義差、Checker出力schema拡張[同Fact兄弟列挙]、Family Xの全文再生成retryとの順序)。非競合4件。
6. 推奨方針: 新規Production module(`er0XX_self_recovery_flow_01.py`、Trial計測コード非含有・`er052_*`/`er050`/`er051`をimportしない)に判定ロジックを移し、既存経路は薄い呼出しアダプタ経由。Trial runnerは新moduleをimportして計測だけ残す(逆方向参照のみ)。ただしrep30は構成全体で検証されているため**部分配線で`PRODUCTION_WIRED`にしない**。
7. ユーザー判断候補: 新規記事テーマ(runtime evidenceに新規記事が要る場合)、Standard/Advancedどちらを先に、cycle上限の扱い、Checker出力schema拡張の可否(§5)。

---

## 1. rep30有効構成の正本

### 1-1. 取得元(確認)
- スイッチ定義: `er052_open233_self_recovery_flow_runner_01.py`(以下runner)`KPI_TRIAL_SWITCHES` L418〜452、`apply_kpi_trial_switches` L455。
- rep30スクリプト: `er052_open233_self_recovery_flow_runner_01_rep30_full_01.py` `apply_switches`(L40〜)が`apply_kpi_trial_switches()`後に`RECHECK_BEFORE_AFTER_PAIRS=n3(既定off)`、`STAGE2_VERDICT_REUSE_NONBLOCKING=reuse(既定on)`、`STAGE2_SIBLING_LOCATIONS_CYCLE1=sibling(既定on)`を上書きし、`MAX_CYCLES==2`・`HARD_MAX_CYCLES==3`・`BODY_RUBRIC_DEFAULT is s2c.RUBRIC_R3_TRIPLE_PRIME_WITH_MISCONCEPTION_PRINCIPLE_V7B`、`STAGE2_DOWNGRADE_VERIFY is False`・`TIER0_G_L_ENABLED is False`・`STAGE2_NORMAL_TWO_OF_TWO is False`をassert。起動は`--stage main`既定(`--n3 off --reuse on --sibling on`)。
- 実績記録: `er052_output/open233_self_recovery_flow_runner_01_rep30/summary_kpi_01.json`の`switches`(20キー全てON/指定値)・`models.rubric`=V7b・`models.runner_MODEL`=gpt-6-luna、`summary_rep30_new_01.json`。rep30実績: 38 instance-run・STAGE4 0件・Human Review 0・費用総額¥21.7866(平均¥0.5733/run、worst¥4.1427)・KPI Primary/Safety達成、Cap(worst+¥3以内 vs rep24)のみ未達(safety_A4 +¥3.135)。
- **注(確認)**: rep30の入力は29 instance(Trial fixture、`safety_er009_changed_*`等の合成注入を含む)であり、**Production正式経路での実flowではない**。

### 1-2. 有効スイッチ(rep30でON/指定、22個)

U番号は§1-4の対応(ユーザー列挙24項目)。設計書略称: 設計A=`design_open233_self_recovery_flow_01.md`、設計B=`design_open233_kpi_recovery_02.md`。行番号はrunnerのスイッチ定義行/主実装(関数@定義行)。

| ID | スイッチ=rep30値 | 定義行 | 実装関数@行(runner) | 設計§ | Opus# | ユーザー承認の根拠(DECISION_LOG行、確認) | U |
|---|---|---|---|---|---|---|---|
| S01 | `HANDOFF_MODE`=violation_span | L324 | `annotate_claim_span_identity`@5636、`resolve_violation_spans`@4738、`single_text_rewrite`@6182、`paired_rewrite`@6390、`run_stage3_for_claim`@7108 | 設計A §5(受け渡し再設計) | #5 | 2026-10-02ユーザー決定「基本線5点」(L16750・L16977)。単体のProduction採用承認の明示は確認できず(`open233_closeout_check` §2)。2026-10-05一括承認で補完 | U3 |
| S02 | `VS_MATCH_EXT`=True | L336 | `vs_match_levels`@4614、`vs_edge_punct_match`@4650、`vs_word_boundary_ok`@4600、`_resolve_claim_string_base`@4792、`_resolve_claim_string`@5512 | 設計A §5/OPEN-233-A1-PROD | #5 | `APPROVED_FOR_PRODUCTION` ユーザー意向2026-10-03(L17610) | U4 |
| S03 | `VS_EXPLAIN_SPLIT`=True(P-strict-closed) | L359 | `vs_explain_split_resolve`@4917、`_resolve_claim_string_p`@5541 | 設計B §5 | #7 | `APPROVED_FOR_PRODUCTION` ユーザー決定[3回目]2026-10-04(L17966) | U5 |
| S04 | `VS_SENTENCE_RESTORE`=True(L6完結文復元) | L368 | `vs_sentence_restore_resolve`@5299、`vs_l6_focus_absent`@5474 | 設計B §12-1 | #9 | Fable判断(Opus#9後)。個別のユーザー承認は未確認、2026-10-05一括承認で補完 | U6 |
| S05 | `JA_MODE`=english_only | L339 | `_run_stage3_spans_core`@6994、`full_recheck_required`@7190(`english_only_ja_source_requires_full_recheck`L7250) | 設計A §0/§1 | - | 方針承認(ユーザー決定2026-10-03、`OPEN-233-A1-PROD`行「英語だけ修正の接続仕様」) | U2 |
| S06 | `FLOOR_VERIFY_MODE`=time_only | L402 | `floor_verify_target`@2740、`floor_verify_evaluate`@2930、`run_floor_verify_call`@2879、`run_stage2`@3554 | 設計B(判断D) | #8 | `APPROVED_FOR_PRODUCTION` ユーザー決定[4回目](L18212)・[5回目=選択肢3、時期のみ](L18378) | U7 |
| S07 | `CAUSAL_FLOOR`=True(Tier 0) | L3126 | `causal_floor_guard`@3170、`stage2_release_guard`@3233、`run_stage2`内L3792 | 設計B §9-2/§10 | #11 | Fable判断(Opus#11後)。個別ユーザー承認は未確認、2026-10-05一括承認で補完 | U8 |
| S08 | `CAUSAL_FLOOR_VOCAB`=known6 | L3133 | 同上 | 設計B §11(hold-out誤停止0.19%) | #11 | 同上。`inventory`語彙は不採用(§1-3) | U8 |
| S09 | `STAGE2_SECOND_OPINION`=True(S1) | L3127 | `apply_stage2_second_opinion`@3917、`run_instance`L8382 | 設計B §9-1/#10 | #10 | Fable判断+条件A Opus#10(降格は2回一致必須)。「既存より厳しい変更のためユーザー承認待ち」記録あり(OPEN_ITEMS L662)→2026-10-05一括承認で補完 | U9 |
| S10 | `RECHECK_MERGE_UNRESOLVED`=True(N1′) | L2162 | `run_instance`L9179〜9190、`normalize_recheck_outcome`@2213、`aggregate_prior_issues_resolved`@1884 | 設計B §13-1 | #12 | Fable判断(Opus#12後) | U10 |
| S11 | `STRUCTURAL_ELEMENT_REWRITE`=True | L2168 | `rewrite_ranges_ladder`@5859、`structural_element_reasons`@5794、`STRUCTURAL_REWRITE_HINT_SUFFIX`@5787 | 設計B §14-2/§15-3 | #13 | Fable判断(DECISION_LOG内3件言及) | U11 |
| S12 | `ACTOR_GUARD_MODE`=ag1_strict | L644 | `actor_rewrite_guard_ok`@732、`actor_rewrite_guard_decision`@695 | 設計B §14-3/§15-1(AG1-strict+2条件AND) | #13 | Fable判断。主体置換ガード自体は設計A由来 | U12 |
| S13 | `STRUCTURAL_PAIRS_TO_RECHECK`=True | L2163 | `run_recheck`@1914(L1946)、`build_before_after_instruction`@2040、`run_instance`L9063 | 設計B §15-3 | #13 | Fable判断 | U13 |
| S14 | `STAGE4_ALLOWLIST`=True(I-2) | L2172 | `stage4_allowlist_decision`@7984、`STAGE4_ALLOWED_REASONS`@7977、`structural_ladder_exhausted_verified`@5840、`run_instance`L8462 | 設計B §18-3/§18-C | #14 | Fable判断(Opus#14後)。「出口を許可リスト化」は2026-10-05ユーザー列挙に含まれる | U14 |
| S15 | `LADDER_LOCATION_CARRY`=True(B′+I-1最小) | L2173 | `location_prior_levels`@8040、`update_regions_after_rewrite`@8054、`claim_ranges_in_text`@8027、`run_instance`L8648・L8874 | 設計B §18-4 | #14 | Fable判断。**§0-4(同Fact別箇所で段落Rewriteの廃止)との解釈はClose out確認事項**(設計B §18-4) | U15,U21 |
| S16 | `REWRITE_REVERT_GUARD`=True(A2) | L2174 | `revert_to_prior_state_detected`@8000、ladder L6083、`run_instance`L8687、`_run_stage3_cycle`@8671 | 設計B §18-5 | #14 | Fable判断 | U16 |
| S17 | `SPAN_FALLBACK_CHAIN`=True(D、H-1是正含む) | L2175 | `vs_explain_split_resolve`L5005、`normalize_recheck_outcome`L2254、`run_instance`L8340・L8471・L8735 | 設計B §18-7 | #14 | Fable判断 | U17 |
| S18 | `JUDGE_ONLY_CYCLE_AFTER_CAP`=True(G) | L2176 | `run_instance`L8293・L8580・L9232 | 設計B §18-8 | #14 | Fable判断 | U18 |
| S19 | `LAST_RESORT_DELETE`=True(T) | L2177 | `rewrite_ranges_ladder`L5941(0_delete@L5968)、`run_instance`L8464・L8593・L8789 | 設計B §18-9 | #14 | Fable判断 | U19 |
| S20 | `MATERIALITY_BLOCKING_PIN`=True(S-4 BLOCKING固定) | L2178 | `claim_materiality_key`@8085、`run_instance`L8397・L8427 | 設計B §18-10 | #14 | Fable判断。**CURRENT_SPECの`BLOCKING固定`4件は別文脈の可能性、要確認** | U20 |
| S21 | `STAGE2_VERDICT_REUSE_NONBLOCKING`=True(rep30スクリプト既定`--reuse on`) | L2179 | `run_instance`L8344・L8410 | 設計B §18-10/§18-C-4 | #14 | 事前固定条件(¥0 replay: 抑制8・重大0・flip0)で委任_12がON化。ユーザー確認事項としてCloseoutへ(設計B §18-15) | U22 |
| S22 | `STAGE2_SIBLING_LOCATIONS_CYCLE1`=True(`--sibling on`) | L2180 | `run_instance`L8296。前提として`use_enumeration_stage1`(既定True)の`stage1_fresh_with_enumeration`@1672・`build_deviation_schema_with_enumeration`@1463・`expand_same_fact_id_locations`@1529 | 設計B §18-11 | #14 | 事前固定条件(①=20%>0)で委任_12がON化 | U23 |
| S23 | `BODY_RUBRIC_DEFAULT`=`s2c.RUBRIC_R3_TRIPLE_PRIME_WITH_MISCONCEPTION_PRINCIPLE_V7B`(スイッチ外の既定値) | L506 | `run_stage2`@3554、`run_floor_verify_call`@2879。rubric本体は`er052_..._stage2_calibration_01.py` L612 | CURRENT_SPEC L2338〜 | #8 | `APPROVED_FOR_PRODUCTION` 2026-10-03[2回目]+V7bはユーザー決定[4回目]、再較正PASS(委任_61) | U1 |

(スイッチ数: S01〜S22=22スイッチ+S23 rubric。`KPI_TRIAL_SWITCHES`の他の値はOFF=§1-3。)

### 1-3. スイッチ化されていないがrep30で常時有効な機構(確認、`open233_closeout_check` §4・設計B§18-B/18-C)

| ID | 機構 | runner位置 | 備考 | U |
|---|---|---|---|---|
| N01 | Stage 1 Trial版Checker(er051 variant、`V4A_DEVELOPER_MSG_WITH_MISCONCEPTION_PRINCIPLE`、`build_trial_prompt_template`、`classify_parsed_result_trial`) | runner内`trial.*`16参照 | **Production `vfl01`のChecker promptとは別物**。Productionへ入れるのは「Checker prompt変更」に該当(§4-3 K6) | U1,U24 |
| N02 | Stage 2 batch判定(`run_stage2`@3554、`s2c.run_stage2_batch_variant`、body/hook別`s2h.run_stage2_hook_batch`) | L3554 | Productionに対応物なし | U1,U24 |
| N03 | precheck決定論floor(`precheck.run_precheck`、`apply_floor`@2304、`FLOOR_FLAGS`@757=主体/数値/否定/比較/時期、`build_precheck_floor_claims`@7831) | 複数 | `FLOOR_FLAGS`はProduction `DEVIATION_FLAG_KEYS`(L448)の部分集合(確認) | U7,U8,U24 |
| N04 | 最小Rewriteラダー(水準①語句→③文→④段落、⑥既定OFF)`rewrite_ranges_ladder`@5859 | L5859 | Productionの`er010.rewrite_ng_item`(文単位×3 attempt)とは別設計 | U21,U24 |
| N05 | `MAX_CYCLES=2`・`HARD_MAX_CYCLES=3`(別claimでblocking件数が減少する場合のみcycle3) | L279/L283 | **Production `er010.MAX_REWRITE_CYCLES=3`(L38)と定義が違う**(§4-3 K1) | U24 |
| N06 | `carry_forward_resolution`@6804、`l6_carry_forward_precedence`@6870、`_carry_forward_comparison`@6912、`_record_carry_forward_recheck`@7958 | 複数 | L6とcarry-forwardの順序(委任_05) | U6,U10 |
| N07 | `issue_focus_absent_recheck_only`(Stage 2 BLOCKINGの引用が現行**本文全体**に無ければRecheckのみで解消)、`vs_l6_focus_absent`@5474 | L5474 | 委任_12で本文全体判定へ是正(設計B §18-C-3a) | U24 |
| N08 | degenerate検査拡張・`structural_ladder_exhausted_verified`@5840(許可名への写像禁止) | ladder内 | 設計B §18-C-1 | U14,U24 |
| N09 | API/連続エラー安全装置(`MAX_RETRIES_PER_CALL=2`・`MAX_CONSECUTIVE_ERRORS=3`、fail-closed→`api_failure`) | L276〜277 | Production `run_writer_with_technical_retry`(`max_attempts=2`、vfl01 L403)と同系 | U14 |
| N10 | 位置オブジェクト・同一箇所履歴(`rewritten_regions`/`article_state_history`、I-1最小) | `run_instance` | S15/S16の前提 | U15,U16 |

### 1-4. ユーザー列挙24項目 ⇔ 構成ID

| U | ユーザー項目 | 構成ID |
|---|---|---|
| U1 | 重大度判定Materiality V7b | S23、N01、N02 |
| U2 | 英語本文だけを修正する方針 | S05 |
| U3 | violation spanの引継ぎ | S01、N10 |
| U4 | terminal punctuation差を許容した位置特定 | S02 |
| U5 | Checker説明文混入からの決定論的範囲復元 | S03 |
| U6 | 不完全spanから完結文への復元 | S04、N06 |
| U7 | time系のみAI再確認を許すSafety floor | S06、N03 |
| U8 | 因果等の決定論Safety floor | S07、S08、N03 |
| U9 | Checker重大判定を後段AI1回だけで解除させないSafety構造 | S09(S1:2回一致必須) |
| U10 | Recheck未解決claimを次cycleへ戻す処理 | S10、N06 |
| U11 | 構造要素を空にせず上位Rewriteへ進める処理 | S11、N08 |
| U12 | 主体変更Safety guard | S12 |
| U13 | 構造要素のbefore/afterをRecheckへ渡す処理 | S13 |
| U14 | Human Review出口の許可リスト化 | S14、N08、N09 |
| U15 | 同一箇所のRewrite level引継ぎ | S15、N10 |
| U16 | 元の悪い文章へ戻るRewriteの防止 | S16、N10 |
| U17 | span特定失敗時の段階的fallback | S17 |
| U18 | Rewrite上限後の判定専用cycle | S18 |
| U19 | 非構造要素の最終手段処理 | S19 |
| U20 | 本文不変の重大判定を後段の揺らぎで解除しない固定 | S20 |
| U21 | 同一箇所で修正後も重大なら範囲を一段広げる | S15、N04 |
| U22 | 本文不変・同一箇所で2回非重大一致済みなら判定を再利用 | S21 |
| U23 | 同じFactの別箇所を初回判定時に把握する仕組み | S22(+同fact列挙stage1) |
| U24 | rep30でONだったその他Self-Recovery構成 | N01〜N09(U24専用はN05・N07・N09) |

### 1-5. 「配線しない」表(OFF/REJECTED、Productionへ混ぜない)

| 候補 | 実体・状態(確認) | 根拠 |
|---|---|---|
| F1 品質regen条件変更 | 不採用(現状維持)。Productionの品質判定との整合が必要でFable/ユーザー判断事項 | 設計B §17-2/§18-12 |
| 確認役 `STAGE2_DOWNGRADE_VERIFY` | runner L3034、既定False、実測(NORMAL群47.3%)で不採用 | 設計B §9-7、`KPI_TRIAL_SWITCHES`コメント |
| N3′ `RECHECK_BEFORE_AFTER_PAIRS` | runner L2164、既定False、委任_06 A/Bで不採用(rep30 `--n3 off`、assert) | 設計B §13 |
| G_L `TIER0_G_L_ENABLED` | runner L3042、False(rep30スクリプトがassert) | 設計B §9 |
| NORMAL群2-of-2 `STAGE2_NORMAL_TWO_OF_TWO` | L410、False。Production不在の評価用Trial補助(正解ラベル付きinstance限定) | 設計B 委任_01作業2-3 |
| `CAUSAL_FLOOR_VOCAB=inventory` | 誤停止+13件(2.51%)で不採用。known6のみ | 設計B §10-2/§11 |
| A1 主体語残存チェック | 不採用(誤検出2/3) | 設計B §18-6 |
| C(actor時の最小levelを③から) | 不採用(§0-4衝突) | 設計B §17-3 |
| E1(複数claimを1 Rewriteへ) | 不採用 | 設計B §17-3 |
| E2(同fact全箇所一括・Recheck結果へのenum適用) | 不採用。**S22(cycle 1のStage 2 batchへの兄弟列挙、Rewriteへ渡さない)とは別物**(混同注意) | 設計B §17-3 |
| F2(MAX_CYCLES増) | 不採用(Cap違反) | 設計B §17-2 |
| (補)A3 | 対象外 | 設計B §17-3 |
| (補)`CHECKER_SPANS_MODE=violation_spans` | 不採用(Checker出力形式変更、ユーザー決定2026-10-03)。runner L391、既定legacy | closeout §4 |
| (補)`HANDOFF_MODE=legacy`、`JA_MODE=paired`、`FLOOR_VERIFY_MODE`の`comparison_time`(廃止、`ValueError`) | 比較用残置/廃止 | closeout §4 |
| (補)Trial計測専用: `CORRECT_LABEL_OVERRIDES`@9372、`SAFETY_CRITICAL_CLAIM_DEFS`@9313、`derive_safety_critical_from_labels`@9475、`NORMAL_GROUP_INSTANCE_IDS`、g6/step3cmp fixture、`TOTAL_BUDGET_JPY`/`BUDGET_STATE_PATH`のTrial予算 | 評価・正解ラベル用。Production module側には含めない | runner |

---

## 2. Production実装の現状(read-only、確認)

### 2-1. Production経路の棚卸し

「正式Production経路」は単一ではなく複数familyに分かれ、**Local Rewriteループが3箇所に複製**されている(確認)。

| 経路ID | ファイル・関数(行) | 内容 | MAJOR残存時の現行挙動 |
|---|---|---|---|
| P1 Family X **Advanced** | `er012_e_family_entertainment_two_level_runner_01.py`(`_run_writer_stage_once` L340〜、deviation L381〜432)。`er019_family_x_entertainment_production_runner_01.py`(L358〜397)から呼ぶ | JA→EN忠実翻訳→`vfl01.run_deviation_check(..., include_related_fact_id=True, source_article_text=ja_text)`(L382)。MAJORなら`origin==ja_source`は`JARecheckRequiredError`(L392〜399)、それ以外は**must-fixで全文を1回だけ再生成**(L403)→再検査(`prior_issues=must_fix_used` L415〜417) | 再生成後もMAJORまたは`all_prior_issues_resolved`=False → `RuntimeError("[STOP] ...")`(L423〜432)。未採用textは`rejected_advanced_attempt2.md`へ保存 |
| P2 Family X **Standard** | 同ファイル L478〜522 | Advanced本文→Standard生成→同様の1回だけmust-fix再生成 | 同上(L523付近STOP) |
| P3 discovery_focus_staged(A2/B1b系Stage 1〜3) | `er003_discovery_focus_staged_production_01.py`:`run_ledger_local_rewrite_loop`@195、`run_stage1_qa`@300、`run_one_pattern_staged_discovery_focus`@606(`STAGE1_MAX_REGENERATIONS=1`@97) | Checker(`hook_aware=True`)→MAJOR毎に`er010.locate_target_sentence`→`rewrite_ng_item`→`apply_rewrites`→Ledger全体再判定(最大`MAX_REWRITE_CYCLES`)→Stage 1 QA blockingならStage 1を1回再生成 | `locate`がNone→`human_review_required=True`(L226)。cycle尽き・human_reviewありなら`blocking`→`NG_REVIEW_REQUIRED`(L284、L643〜)。 |
| P4 N3 articles | `er003_v1_n3_01_articles_generate.py`:`run_one_pattern`@888内のLocal Rewriteループ L1142〜1320(P3と**別実装の複製**) | 同上 | `NG_REVIEW_REQUIRED`で返却(L1300〜1318、Directional Precheck以降へ進まない) |
| P5 B-family voices | `er012_b_family_voices_writer_generic_01.py`:`run_ledger_deviation_and_local_rewrite`@1499(さらにvoice safety gate@1451) | 同上(3つ目の複製) | `any_human_review_required`/`remaining_major_count`を返却(L1623〜1630、呼出元が止める) |
| P6 その他 | `er012_b_family_production_runner_01.py` L295・806・1112、`er012_b_family_voices_a2_production_01.py` L239・521、`er009_n1_diagnostic_full_retry_production_12.py` L299 | `run_deviation_check`呼出し。MAJOR時のretry/STOP記述は近傍Grepで確認できず | **要確認**(check-only/記録のみの可能性。配線対象経路かどうかをFable/ユーザーが判断) |

DEVテスト/Trial系の`er012_editorial_*_trial_*.py`・`er003_v1_*_generate.py`等も`run_deviation_check`/`locate_target_sentence`を呼ぶ(`git grep`で40件超)が、Production正式経路ではないため対象外(ただし`vfl01.run_deviation_check`を変更すると影響を受ける。§4-3 K6)。

### 2-2. 初回Checker経路(`er003_v1_en_direct_vfl_01_generate.py`)
- `MODEL = routing.WRITER_MODEL`(L57、"gpt-5.6-luna"とコメント)・`REASONING_EFFORT=r3.WRITER_REASONING_EFFORT`(L58)。Model Routing Contract経由。
- `DEVIATION_FLAG_KEYS`(L448)=10種のflag。`DEVIATION_JSON_SCHEMA`(L454)はseverity MINOR/MAJOR(L466)。`_apply_deviation_post_hoc_validation`(L544): MAJORだがflagが全てfalseならMINORへ自動降格(`auto_downgraded`)。`overall_status`はプログラム側再計算(L560)。**V7b/materiality 3段階/Stage 2は存在しない**。
- `build_prior_issues_instruction`(L678): 前回指摘(fact_id/claim_in_article/issue/explanation)を文字列で提示。`run_deviation_check`(L773)の件数一致式(L826〜829): `all_prior_issues_resolved = len(resolved)==len(prior_issues) and all(resolved)`。`prior_issues`/`include_related_fact_id`/`source_article_text`を指定した場合のみ拡張schema(L708〜)=後方互換のopt-in方式(**配線時に踏襲できる既存の前例**)。
- `causal_strength`はLedger facts側のフィールド(L96/L115/L298)で、Checker判定のfloorではない。

### 2-3. Rewrite経路(`er010_ledger_local_rewrite_09.py`、459行)
- `locate_target_sentence`@68: 完全部分一致→文単位word overlap≥0.25(Jaccard)の2段のみ。**句読点差L0〜L5・単語境界・引用符断片・完結文復元なし**。位置は文字列で毎cycle再取得(座標引継ぎなし)。
- `MAX_REWRITE_ATTEMPTS=3`@29、`MAX_REWRITE_CYCLES=MAX_REWRITE_ATTEMPTS`@38(記事全体cycle)。`rewrite_ng_item`@373(文単位、Point全文をcontextに渡す[`extract_point_context`@97、OPEN-113配線済み])、`apply_diff_qa_to_resolved_rewrite`@336(diff QA)、`apply_rewrites`@454。
- 主体ガード(`actor`)記述は0件(Grep)。ladder・revert検出・delete・構造要素処理は存在しない。

### 2-4. Recheck/再検査・retry・fallback・regeneration
- Recheck: Local Rewrite各cycle後に`run_deviation_check`で**記事全体を再判定**(P3 L262、P4 L1264、P5 L1595)。Family Xは`prior_issues`付き再検査(P1/P2)。
- retry: `run_writer_with_technical_retry`(vfl01 L403、`max_attempts=2`)、Point overlap retry(`POINT_OVERLAP_ARTICLE_RETRY_MAX`)、Family X段落数retry(`_family_x_ensure_split_or_paragraph_retry`@294、deviation retryとは独立軸)、`er009_n1_diagnostic_full_retry_*`(診断情報付き全文再生成)。
- fallback/regeneration: Stage 1 QA再生成(`STAGE1_MAX_REGENERATIONS=1`@er003_discovery L97、blocking時)、Family Xのmust-fix全文再生成(1回)、`--regenerate-stage advanced|standard|writer|storyline_b3`(er019 runner L294〜、er012_e L33)。
- Standard/Advanced分岐: Family X(P1/P2)で顕在。他familyはA2/B1等のlevel別で構造が違う(Advanced/Standard対称性は`_family_x_ensure_split_or_paragraph_retry`のコメントL311〜312)。
- API failure: `vfl01.run_deviation_check`にtry/exceptなし(例外は呼出元へ伝播=プロセス停止)。writer側のみ`run_writer_with_technical_retry`。
- cycle上限到達時: P3は`blocking=True`→`NG_REVIEW_REQUIRED`、P4はNG_REVIEW_REQUIREDで返却、P1/P2は(retry 1回のみ)STOP。span取得失敗(locateがNone)はいずれも`human_review_required=True`。

### 2-5. `er052_open233_self_recovery_stage2_production_01.py`の位置づけ(確認)
- 名称は"production"だが**Trial側module**(`er052_`接頭辞、ヘッダに「Production codeは一切変更しない。Model Routing Contractは経由しない」、MODEL=`gpt-6-luna`ハードコード、Production経路からの`import`は0件、importerは`er052_*`/`er052_output/*`のみ)。
- 内容: Stage 2 per-claim/batchの実装、`MATERIALITY_RUBRIC`@37、`MATERIALITY_RUBRIC_V7B`@L74(**rep30のV7bと別物**、前述)、`build_local_context`等。**rep30の`stage2_*`実装本体は`runner`+`s2c`(calibration)+`s2h`(hook)側にある**。よって「器が存在する」は誤解を生む。配線時は(1)rep30が実際に使うV7b(`s2c` L612)を正本として新Production moduleへ移し、(2)本moduleをProductionから参照しない。

### 2-6. `OPEN-233-A1-PROD`束の現状(確認、`OPEN_ITEMS.md` L727・`open233_closeout_check` §2/§3)
- 7構成要素(本体・V7b・句読点差・説明文混入・英語だけ・時期のみ・動機)すべて`APPROVED_FOR_PRODUCTION`/未配線、Production側の対応箇所なし。「runner/er010共有module」化は**未着手**(共有moduleはまだ存在しない)。
- 配線時必須の9確認項目(quote-heavy実記事のオフライン再生、runnerとProductionの同値テスト、runtime evidence、局所QA fastpath条件(e)置換、解放claimを2-of-2降格対象から除外、`dev`flag不変更、確認call失敗=BLOCKING固定、cycleごと再評価、再生成経路の再検査明記)は未実施。**注**: 2-of-2(NORMAL群)はrep30でOFFのため、「解放claimを2-of-2から除外」はrep30構成では対象外になる(要SSOT整理)。
- `er010.locate_target_sentence`へ同等処理を入れるかは「別のユーザー判断(未決)」とされていたが、2026-10-05一括承認で解決したか**要確認**(SSOT記録待ち)。

### 2-7. runnerが依存するTrial module(Production配線で除去すべき依存、確認)
`er050_gpt6_checker_comparison_trial_01`(fixture/`g6.*`7参照)、`er051_open233_checker_trial_variant_01`(Trial Checker prompt/schema/classify、16参照)、`er052_..._precheck_01`(684行、23参照)、`..._s1d_trial_01`(237行)、`..._stage2_calibration_01`(970行、V7b/Stage 2 batch)、`..._stage2_hook_01`(274行)、`..._stage2_production_01`(333行、`_extract_usage`/`official_cost_jpy`等32参照)、`..._stage3_rewrite_trial_01`(603行、J1 Rewrite prompt/`simple_llm_call`)、`..._phase1_step3_stage1_compare_01`(fixture)。計約4,000行超。Productionから参照してはならない(ユーザー決定)ため**複製・再配置(コピー+Production側テスト)が必要**。

---

## 3. 1対1対応表

凡例: Gap種別=A純移植(関数をProduction moduleへ移し参照切替)/B Production構造への適合が必要(入出力・データ形式が違う)/C Production側に対応経路が無く新設/D既に同等実装あり。
影響経路: 初=初回Checker、R=Rewrite、Rc=Recheck、retry、fb=fallback/Stage1再生成、reg=regeneration(Family Xの全文再生成)、Std/Adv=Family X Standard/Advanced、cap=cycle上限到達時、span=span取得失敗時、api=API failure時。
Trial専用依存: er05x/er050/er051 import、fixture、`CORRECT_LABEL_OVERRIDES`等の計測コードの混入有無。
DRC=Dangling Reference Check 5項目(順に: ①CURRENT_SPECに正式仕様 ②ユーザー承認 ③初回Production経路に存在 ④retry/fallback孤立なし ⑤Trial専用定義へ非依存)。○=充足、△=部分、×=不足、-=該当なし。
evidence: M=実LLM発火が必要な主要flow(runtime evidence必須)、F=fixture補完でよい稀分岐(ただし最低1件のProduction path実行を推奨)。

| U/ID | Production現状 | Gap | 影響経路 | Trial専用依存 | DRC①②③④⑤ | evidence |
|---|---|---|---|---|---|---|
| U1 V7b(S23,N01,N02) | 未実装。Checker=`vfl01`(MAJOR/MINOR+flag auto-downgrade)、Stage 2なし。`s2p.MATERIALITY_RUBRIC_V7B`は別物(§2-5) | C(Stage 2新設)+B(Checker promptへの原則挿入=Checker変更) | 初・retry・reg・Std/Adv・全family | er051/s2c/s2h/s2p | ○(CURRENT_SPEC V7b 7件)/○/×/×/× | M |
| U2 英語だけ修正(S05) | 部分: Family Xはreg経路で英語のみ再生成+`run_deviation_check`再検査(P1 L403〜419)、JA不変。ただし仕様未明記。Local Rewrite系(P3〜P5)は英語のみ | B(Family X: Self-Recovery連携)/D相当(P3〜P5は暗黙に英語のみ) | reg・Std/Adv・R | `full_recheck_required`内のTrial記録 | △(CURRENT_SPEC 3件、再検査明記は不足)/○/△/×/○ | M(reg経路) |
| U3 span引継ぎ(S01,N10) | 未実装。`claim_in_article`文字列を毎cycle`locate`で再照合 | C | 初・R・Rc・retry | `resolve_violation_spans`等は`er052`内 | ×(CURRENT_SPEC 0件、設計書のみ)/△/×/×/× | M |
| U4 句読点差(S02) | 未実装。`locate_target_sentence`は部分一致+overlap0.25のみ | A(`vs_*`関数群の移植)→組込みはB(`er010.locate`置換、4family共有) | 初・R・span | `vs_*`@4535〜4738(runner内) | ○(CURRENT_SPEC 5件)/○(2026-10-03)/×/×/× | M+F |
| U5 説明文混入(S03) | 未実装 | A→B | 初・R・span | `vs_explain_split_resolve`@4917 | △(2件、P-strict-closed明示は薄い)/○(2026-10-04)/×/×/× | F(+quote-heavy実記事オフライン再生) |
| U6 完結文復元(S04,N06) | 未実装 | A→B | 初・R・span | `vs_sentence_restore_resolve`@5299 | ×(L6 1件)/△(個別承認なし)/×/×/× | F+M(1件) |
| U7 time_only確認(S06,N03) | 未実装(floor自体がProductionに無い) | C | 初・Rc | `floor_verify_*`@2740〜2993、precheck | ○(時期11件)/○(2026-10-04[5回目])/×/×/× | F(Safety-critical・解放0確認) |
| U8 因果等floor(S07,S08,N03) | 未実装(10 flagはあるがfloor=決定論BLOCKING確定は無い) | C | 初・Rc | `causal_floor_guard`@3170、`apply_floor`@2304、`precheck` | ×(CURRENT_SPEC 0件)/△/×/×/× | F(hold-out replay)+M |
| U9 S1・Stage 2(S09) | 未実装 | C | 初・Rc・cap | `apply_stage2_second_opinion`@3917、`s2c.run_stage2_batch_variant` | △(S1言及9件、仕様正式化は未確認)/△(2026-10-05一括)/×/×/× | M |
| U10 Recheck未解決→次cycle(S10,N06) | 部分: P1/P2は`all_prior_issues_resolved`(件数一致式vfl01 L826)でSTOP。P3〜P5は全文再判定でMAJOR残存のみ見る(未解決priorを次cycleへ戻す処理なし) | B(P1/P2)/C(P3〜P5) | Rc・retry・cap | `normalize_recheck_outcome`@2213 | ×(Recheck言及7件、N1′は0)/△/△(P1/P2に基礎のみ)/×/× | M |
| U11 構造要素(S11,N08) | 未実装(title/hook/In one lineの特別扱いなし) | C | R・cap | `structural_element_reasons`@5794、`rewrite_ranges_ladder` | ×(0件)/△/×/×/× | F |
| U12 主体変更guard(S12) | 未実装(`er010`にactor記述0件)。Checker flag`changed_actor`のみ | C | R | `actor_rewrite_guard_ok`@732(ag1_strict) | △(1件)/△/×/×/× | F(+Safety-critical) |
| U13 構造before/after(S13) | 未実装 | C+B(Recheck入力にpairsブロック追加。`run_deviation_check`は`prior_issues`方式を踏襲可) | Rc | `build_before_after_instruction`@2040 | ×/△/×/×/× | F |
| U14 許可リスト出口(S14,N08,N09) | 未実装。現行出口は最低6種: `human_review_required`(locate失敗)、`NG_REVIEW_REQUIRED`(P3/P4 cycle尽き)、P1/P2の`RuntimeError STOP`2種(段落数・MAJOR残存)、`JARecheckRequiredError`、`Stage1 qa_exhausted` | B(全出口を4理由+funnelへ置換。Production Gateの再編) | 全経路・cap・api | `stage4_allowlist_decision`@7984 | ×(fail-closed/STAGE4言及22件は旧出口の記述)/△/×/×/× | M |
| U15 level引継ぎ(S15,N10) | 未実装(`previously_seen_claims`は件数用の集合のみ) | C | R・Rc・cap | `location_prior_levels`@8040 他 | ×/△(§0-4解釈要確認)/×/×/× | M |
| U16 revert防止(S16) | 未実装。`er010`は同一文への再試行3回だが過去状態との比較なし | C | R | `revert_to_prior_state_detected`@8000 | ×/△/×/×/× | F |
| U17 span fallback(S17) | 未実装(locate None→即human_review) | C+B(P3〜P5のNone分岐を置換) | span・R | `vs_explain_split_resolve`L5005他 | ×/△/×/×/× | F+M |
| U18 判定専用cycle(S18) | 未実装(cap尽き→blocking/NG_REVIEW) | C | cap | `run_instance`L8293他 | ×/△/×/×/× | F(cap到達はまれ、rep30でも≥3cycle 1/38) |
| U19 最終手段T(S19) | 未実装(deleteはProductionに無い。Trialは"既存0_delete"としてrunner内に実装、grepでProduction側0件) | C | cap・R | `rewrite_ranges_ladder`L5941/5968 | ×/△/×/×/× | F |
| U20 BLOCKING固定(S20) | 未実装 | C(Stage 2導入が前提) | Rc・cap | `claim_materiality_key`@8085 | △(CURRENT_SPEC 4件は文脈要確認)/△/×/×/× | F |
| U21 範囲拡大(S15,N04) | 部分: `er010`は文単位固定(attempt 3回、範囲拡大なし) | C(ladder新設)+B(er010置換) | R・cap | `rewrite_ranges_ladder`@5859 | ×(ladder 0件)/△/×/×/× | M |
| U22 判定再利用(S21) | 未実装 | C | Rc・cost | `run_instance`L8344/8410 | ×(0件)/△(Closeout確認事項)/×/×/× | F |
| U23 同Fact兄弟箇所(S22) | 未実装。Checker出力に`same_fact_id_locations`なし | B(Checker出力schema拡張。§4-3 K8)+C | 初(cycle1) | `build_deviation_schema_with_enumeration`@1463、`expand_same_fact_id_locations`@1529 | ×/△/×/×/× | M |
| U24 N05 cycle上限 | 競合: Production`MAX_REWRITE_CYCLES=3`(各3 attempt)vs Trial`MAX_CYCLES=2`+条件付`HARD=3`+判定専用cycle | B(要設計) | cap・全R | 定数のみ | ×/△/×/×/○ | M |
| U24 N07 focus_absent本文全体 | 未実装 | C | Rc | `vs_l6_focus_absent`@5474 | ×/△/×/×/× | F |
| U24 N09 API安全装置 | 部分: writer側のみ`max_attempts=2`。`run_deviation_check`は例外伝播 | B | api | `MAX_RETRIES_PER_CALL`等 | △/△/△/△/○ | F(API failure注入、¥0) |
| 全体: モデル/routing(Trial MODEL固定) | Productionは`routing.WRITER_MODEL`経由。Trialは経由しない | B | 全 | `runner.MODEL`、`s2p.PRICE_*` | -/△/-/-/× | M(actual model_id記録) |

件数集計(U1〜U24、主たる種別で1カウント): A=3(U4・U5・U6)、B=5(U2・U10・U14・U23・U24)、C=16(U1・U3・U7〜U9・U11〜U13・U15〜U22のうちU10/U14を除く分、複合のC+B併記はU1・U13・U17・U21)、D=0。DRCの「①〜⑤全○」は0件(**配線前にSSOTを整える対象**: CURRENT_SPECに正式仕様が無い項目は§5-4のSSOT整備へ)。

Dangling Reference Check総括(確認):
- ①CURRENT_SPECに正式仕様あり: V7b・句読点差・時期・英語だけのみ(各言及)。ladder・位置引継ぎ・許可リスト・判定専用cycle・T・BLOCKING固定・S1・因果floor・構造要素・兄弟列挙・N1′・AG1は**0件**(設計書・OPEN_ITEMS・REPORTのみ)。→配線前にCURRENT_SPECへ正式仕様化が必要。
- ②ユーザー承認: 個別承認=V7b・句読点差・P-strict-closed・時期のみ・英語だけ・KPI。他は2026-10-05一括承認(DECISION_LOG未記録、委任_01待ち)。
- ③初回経路に存在: 全項目×(Production未配線)。④retry/fallback孤立: 配線時にP1〜P5全経路で同一仕様になるよう設計(§4-2)。⑤Trial専用依存: runnerは§2-7の依存あり→移設時に除去。

---

## 4. 配線方針案(設計の叩き台、実装しない)

### 4-1. module化案の比較

| 案 | 内容 | 長所 | 短所 |
|---|---|---|---|
| **案M(推奨)新規Production module** `er0XX_self_recovery_flow_01.py`(仮名)+各familyは薄い呼出しアダプタ | 判定ロジック(位置解決`vs_*`、Stage 2/S1/floor、ladder、許可リスト、cycle状態)をrunnerから移植。Trial計測(`CORRECT_LABEL_OVERRIDES`・`SAFETY_CRITICAL_CLAIM_DEFS`・fixture・Trial予算)は含めない。Model Routing Contract経由。P1〜P5はアダプタ(Checker呼出し・Rewrite呼出し・出力保存の3点)を渡す | 3複製+Family X再生成の**挙動一致を1箇所で保証**。Trialとの同値テストが書きやすい。Trial→新moduleの一方向参照(`runner`が新moduleをimportしTrial計測だけ残す、逆参照禁止)を機械的に検査可能(`git grep "er052"`=0) | 初期工数大。`er010`を置換/併存させる設計が要る |
| 案D 既存各ファイルへ分散 | er003/er010/er012各loopに直接実装 | 小さく見える | 3複製+Family Xの4実装に同じ高リスクロジック(Safety guard含む)を複製→不一致リスク大、保守負債。§0原則(Production複雑化回避)に反する |

Trial runnerとの関係: runnerは新moduleをimportする(判定ロジックの二重管理を避ける)。ただし**rep30を再現できること**(同値テスト)が前提。Trial側を新moduleへ切り替える作業はProduction配線とは別タスクにするのが安全(rep30再現性を壊さないため、最初は「複製+同値テスト」でもよい。複製は`er052_*`→Production方向のコピーであり参照ではないため禁止に当たらない。推測)。

### 4-2. 各経路での挿入点と出口の置換(案)

| 経路 | 現行出口 | 挿入点 | 置換後 |
|---|---|---|---|
| 初回Checker(P1〜P5共通) | `run_deviation_check`のMAJOR→Rewrite/再生成 | Checker直後に「Stage 2(+Tier0 floor+S1)で各MAJOR claimのmaterialityを判定」を挿入。BLOCKINGのみRewrite/再生成へ、非BLOCKING(軽微/問題なし)は記録して降格 | V7b/S23 |
| Rewrite(P3/P4/P5) | `er010.locate`→`rewrite_ng_item`(3 attempt)→全文再判定 | `locate`をspan解決(S01〜S04,S17)へ、`rewrite_ng_item`をladder(S11,S15,S16,S19)へ、cycle後の全文再判定をN1′/S13/S20付きRecheckへ | 位置は座標で引継ぎ |
| Recheck | 全文再判定のMAJORのみ参照 | 未解決prior/carry listをStage 2へ合流(S10) | |
| retry | writer technical retry、overlap retry、段落数retry | **触らない**(独立軸)。ただしladder④(段落Rewrite)後の段落数検証を既存retry軸と衝突させない | 要設計 K4 |
| fallback | Stage 1 QA再生成(`STAGE1_MAX_REGENERATIONS=1`) | 許可リスト4理由で到達した「出口」の**手前**にあるか後ろにあるかを定義(現行はHuman Review前にStage 1再生成1回)。再生成は許可リスト外理由の出口ではなく別軸として残す案 | 要設計 K5 |
| regeneration(Family X) | must-fix全文再生成1回→STOP | P1/P2は「Local Rewrite優先、全文再生成は維持するか廃止か」を設計。現行の1回再生成を残すなら許可リスト出口との順序規定が必要 | 要設計 K3/K4 |
| Standard/Advanced | Family XでAdvanced→StandardがAdvanced本文由来 | Advancedで確定した修正がStandard生成に伝わる(Standardは再検査で独立にCheck)。両levelに同一flowを適用 | |
| cycle上限 | `NG_REVIEW_REQUIRED`/STOP | 判定専用cycle(S18)→T(S19)→許可リスト4理由(`blocking_confirmed_unlocatable_after_cap`/`blocking_structural_after_ladder`/`post_T_new_blocking`/`api_failure`) | |
| span失敗 | `human_review_required=True` | 段階的fallback(S17)→carry→次cycle→上限後に許可リスト理由 | |
| API failure | 例外伝播/STOP | `api_failure`(許可リスト内。retry回数は既存`max_attempts=2`と整合) | 非競合 |

### 4-3. 構造的競合候補(STOP条件「Trial最終構成とProduction正式経路の構造的競合」「retry/fallbackとの仕様矛盾」に該当しうるもの)

| ID | 内容 | 判定 | 根拠 |
|---|---|---|---|
| K1 | cycle上限の定義: Production`MAX_REWRITE_CYCLES=3`(各cycle最大3 attempt、無条件)vs Trial`MAX_CYCLES=2`+条件付cycle3(blocking減少時)+判定専用cycle(Rewriteなし) | **競合の可能性高/要設計** | 既存の安全装置(上限)を独自判断で変更禁止。「上限=Rewrite回数、判定回数ではない」(設計B §18-8)は既存上限の再定義でユーザー判断対象 |
| K2 | Rewrite単位: Production文単位(`er010`共有、P3〜P5と多数Trial scriptが依存)vs ladder範囲単位+delete | 要設計(置換か併存か) | er010の変更はDEV/Trial 20+ファイルへ波及。併存(新module側に新関数)なら非競合にできる(推測) |
| K3 | Production Gate「MAJORが残ればSTOP/NG_REVIEW」vs materiality降格(Stage 2で非BLOCKINGなら通す) | 要設計(ユーザーはV7b/S1を承認済みだが、Gate自体の定義変更は明示確認が望ましい) | P1/P2のSTOP条件(L423)・P3/P4のblocking定義 |
| K4 | Family X: 全文再生成(1回)+段落数retry(独立軸)vs Local Rewrite(ladder④は段落Rewrite) | **競合の可能性**(段落数≥3を壊す可能性、再生成との順序) | `_family_x_ensure_split_or_paragraph_retry`@294、L409〜414 |
| K5 | `STAGE1_MAX_REGENERATIONS=1`のStage 1再生成 vs 許可リスト4理由で終端 | 要設計(順序規定。再生成を許可リストの外の別軸として残せば非競合) | er003_discovery L636・L659 |
| K6 | Checker prompt/schema変更(V7b原則・`same_fact_id_locations`)が`run_deviation_check`の40超の呼出元(DEV含む)へ波及 | 要設計。**既存`prior_issues`等のopt-in方式(後方互換、未指定なら不変)を踏襲すれば非競合化可能** | vfl01 L782〜787の前例 |
| K7 | Model routing: Trial`gpt-6-luna`固定・routing非経由 vs Production`routing.WRITER_MODEL`("gpt-5.6-luna") | 要設計/ユーザー確認(使用モデル、価格、`actual model_id`記録) | vfl01 L57、s2p L27 |
| K8 | Checker出力schemaへ`same_fact_id_locations`追加 vs 「Checker出力形式変更の不採用」(ユーザー決定2026-10-03、`violation_spans`) | **競合の可能性高**(別フィールドだが同種のChecker出力変更)。ユーザー確認候補 | closeout §4、runner L391 |
| K9 | `FLOOR_FLAGS`(5種)が`DEVIATION_FLAG_KEYS`(10種)の部分集合であること(Checker flag体系は共通) | 非競合(確認) | runner L757、vfl01 L448 |
| K10 | API failure: Trial fail-closed→`api_failure`(許可リスト)/Production例外伝播・writer retry 2回 | 非競合(Trialはより厳格。retry回数`MAX_RETRIES_PER_CALL=2`はProductionの`max_attempts=2`と同値) | runner L276、vfl01 L403 |
| K11 | `blocking_structural_after_ladder`の未検証経路(後述§4-4) | 要設計(Trial実装の穴、配線時是正) | 設計B §18-C |
| K12 | worst費用Cap: rep30 worst+¥3.135(safety_A4)>Cap¥3(vs rep24) | ユーザー判断事項(2026-10-05一括承認の扱い=受容か否か、SSOT記録待ち) | summary_kpi_01.json `cap_worst_add_le_3_vs_rep24=false` |
| K13 | `STAGE2_NORMAL_TWO_OF_TWO`OFF下で「解放claimを2-of-2降格の対象から除外」(OPEN-233-A1-PROD必須確認)が実質無効化 | 非競合だがSSOT整理要(要確認項目の削除/読替) | OPEN_ITEMS L727 |

STOP条件該当候補: **K1・K4・K8**(競合の可能性が高く、Fable/ユーザーに要確認)。K3・K7は設計判断としてユーザー説明が望ましい。

### 4-4. 既知の残穴(`blocking_structural_after_ladder`未検証経路)の配線時是正
runner `run_instance`L8789(`_already_T or _struct or t_used or not LAST_RESORT_DELETE`)・L8593(cap後T不可)・T削除失敗(`_t_fail`)では、構造要素の検証(`structural_ladder_exhausted_verified`@5840)なしで`blocking_structural_after_ladder`が返る(設計B §18-C「範囲外の観察」、degenerate以外の同型の名前洗い替え)。配線時の是正案(新仕様候補。Fable判断・実装はしていない): 各経路を「構造要素∧ladder実試行済み」を関数内で検証したときだけ許可名で返し、それ以外は**許可リスト外のまま記録してfunnel(判定専用cycle)または次cycleへ戻す**。T無効=Production設定上の想定外状態になるためfixture(T無効/T使用済み/cap後T不可/T削除失敗の4強制経路)をProduction module側の単体テストに含める。

### 4-5. runtime evidence計画案(¥は推定、Guardrailであり上限ではない)
- 方針: 新規記事を作らず、既存のProduction生成記事+Trial fixtureの記事本文/Ledgerを、**Production正式path(新module経由、`routing`経由)へ流す**。実LLM発火のM項目(Stage 2/S1/Checker/Rewrite/Recheck)を最低1件ずつ確認。新規記事テーマが必要となる場合は**Fable/Claudeは決めず、複数候補をユーザーへ提示**(`PM_GOVERNANCE` 13節)。再生成/再検査で足りるかを先に検討。
- 最小セット案(推定8〜10 run): ①クリーン記事PASS(Standard・Advanced、各1)②句読点差MAJOR(L5)1③時期claim(floor_verify)1④因果/S1(Safety-critical型、B3/A2A3相当)1⑤構造要素(title)MAJOR→許可リスト出口1⑥cap到達→判定専用cycle(fixtureの強制)1⑦reg経路(Family Xの再生成後再検査)1⑧API failure注入(¥0、fixture)。
- 費用推定(根拠: rep30 平均¥0.573/run・worst¥4.14、runner MODEL`gpt-6-luna`価格$0.10/$0.01(cached)/$0.50 per 1M・USD_JPY156.88[s2p L28〜29]、Production初回Checkerは既知費用の範囲): 8 run×平均¥0.6≈¥5、Safety系worst想定込みで**¥10〜20程度(推定、Guardrail案¥25)**。Productionの実モデル価格が異なる場合は再見積り。TTSは使わない(T-2不要)。
- 確認項目: actual model_id/routing(`fallback_detected`含む)、Checker出力、Stage 2判定、Tier 0/floor発火、S1(2回一致)、Rewrite(level・位置座標)、Recheck、Safety guard、最終PASS/STOP理由(許可リスト4理由のみ)、実費、許可リスト外STAGE4=0、書き換えられていないBLOCKINGによるPASS=0。

### 4-6. Regression/integration test
- 既存枠: `run_project_regression.py`(pattern`er0*_test_*.py`、CURRENT_SPEC L353 collected=2184/passed=2181[基準値の出典。委任文の「基準11件」は本調査で出典を特定できず、**要確認**])。runner側テスト`er052_open233_self_recovery_flow_runner_01_test_01.py`(9,042行・701テスト)。er012 subprocessテスト等は別途。
- 追加すべき: (a)新moduleとrunnerの**同値テスト**(同入力でspan解決・floor・ladder・allowlist判定が一致。rep30の反実仮想replayを再利用)(b)許可リスト外STAGE4=0のproperty test(c)強制経路fixture(T無効/T使用済み/cap後T不可/T削除失敗、API failure、degenerate)(d)各family(P1〜P5)のアダプタintegration test(モックLLM)(e)**逆方向参照検査**(Production moduleが`er050/er051/er052`をimportしない、`git grep`で機械検証)(f)Checker opt-in引数の後方互換テスト(未指定=prompt/schema/戻り値不変、vfl01 L782〜787の方針)(g)quote-heavy実記事の再生・既存346行の再生回帰(OPEN-233-A1-PROD必須)。

### 4-7. 工数・リスク概算(推測)
- 新Production module(移植+整理): **大**(ロジック約4,000行規模のTrial依存を整理、うちrunner本体は10,363行)。リスク大(Safety系)。
- 4family(P1〜P5)アダプタ+出口置換: **大**(特にP1/P2の再生成retry整合とP3〜P5の複製3箇所)。リスク中〜大。
- Checker prompt/schema opt-in化: **中**(K6/K8)。
- SSOT整備(CURRENT_SPECへの正式仕様化): **中**。
- テスト・runtime evidence: **中**(費用は小、設計・分析が主)。

### 4-8. 推奨配線順序(根拠付き)
1. **SSOT整備**(配線前、DRC①②): CURRENT_SPECへ未記載項目(§3のDRC①=×)の正式仕様化。Trial専用定義依存の除去方針、cycle上限・K8のユーザー判断をDECISION_LOGへ。
2. **共通基盤**: 新module骨格+Model Routing経由+位置解決(S01〜S04,S17)+テスト枠。位置が座標で解決できないと後段が成立しない。
3. **Safety系**(U7〜U9,U12,U20): Stage 2/V7b+floor+S1+actor guard+BLOCKING固定。Safetyが最優先、かつS14(許可リスト)の「BLOCKING確定」が前提。ただし**Stage 2単体で入れると降格だけ増えて見逃しが増える**ため、floor/S1/BLOCKING固定を同時に入れる(rep30はこの組合せで検証済み)。
4. **出口許可リスト+ladder/位置引継ぎ**(U14〜U19,U21): S14単独だと許可リスト外理由の戻り先(ladder/判定専用cycle)が無く成立しないため、S15〜S19と一体。
5. **費用系**(U22,U23): 再利用・兄弟列挙。K8のユーザー判断後。
6. 各stepでP1(Family X Advanced)→P2(Standard)→P3〜P5の順にアダプタ接続(Family Xはregeneration・STOP条件が最も複雑なため、最後かつユーザー判断後が安全という見方もあり、「どちらを先に」はユーザー判断、§5)。
- 重要: **rep30は構成全体で検証**された。部分配線は未検証構成であり、**全項目が揃うまで`PRODUCTION_WIRED`としない**(Gate 3)。

---

## 5. Fableへの論点

### 5-1. STOP条件該当候補
- **K1(cycle上限の定義差)**、**K4(Family X再生成retry・段落数retryとの整合)**、**K8(Checker出力schema拡張 vs Checker出力形式変更不採用)**: Trial最終構成とProduction正式経路の構造的競合/retry・fallbackとの仕様矛盾に該当しうる。配線実装前にFable判断・必要ならユーザー確認。
- `s2p.MATERIALITY_RUBRIC_V7B`(誤V7b)を正本とする誤配線の防止(§2-5)。

### 5-2. Opus独立レビューへ渡す論点(条件A=新しい構造・処理フロー、条件C=Production採用提案前)
1. 案M(新module+アダプタ)の妥当性、`er010`置換/併存、3複製の統合。
2. Production Gate再定義(MAJOR→materiality降格)の安全性(K3)、cycle上限定義(K1)。
3. 許可リスト4理由への出口集約が、Family Xのreg/STOP・Stage 1再生成と矛盾しないか(K4/K5)。
4. `blocking_structural_after_ladder`未検証経路の是正方針(§4-4)。
5. Checker opt-in引数の後方互換設計(K6/K8)。
6. runtime evidence最小セットの十分性とSafety-critical代表の網羅。

### 5-3. ユーザー判断が必要になりうる点
- 新規記事テーマ(runtime evidenceで新規記事が必要な場合のみ。Fable/Claudeは決めない)。再生成/再検査で足りるなら不要。
- Production費用(runtime evidence実費、Cap worst+¥3.135超過の扱い K12)。
- Standard/Advanced(Family X)どちらを先に配線するか、およびP3〜P5(Local Rewrite系)との順序。
- cycle上限(K1)と全文再生成retry(K4)の方針、Checker出力schema拡張(K8)の可否。
- `er010.locate_target_sentence`への同等処理の要否(旧「未決」、2026-10-05一括承認で解決済みか要確認)。
- 設計B §18-4のB′と§0-4の解釈、`STAGE2_VERDICT_REUSE_NONBLOCKING`の扱い(Closeout確認事項)。

### 5-4. SSOT整備候補(配線前、本委任では未編集)
CURRENT_SPEC OPEN-233節へ: ladder/位置引継ぎ/許可リスト/判定専用cycle/T/BLOCKING固定/S1/因果floor/構造要素/兄弟列挙/N1′/AG1の正式仕様(DRC①)。OPEN_ITEMS `OPEN-233-A1-PROD`の必須確認9項目の更新(2-of-2除外項目の読替、共有module化の方針)。

---

## 付録: 確認/推測の区別と調査範囲
- 確認: runner定義行・関数行(AST+Grep)、rep30スクリプトassert、summary_kpi_01.json、Production各経路の該当行、`git grep er052_open233`0件、`s2p`importerが`er052_*`のみ、CURRENT_SPEC/DECISION_LOG/OPEN_ITEMSのGrep件数。
- 推測/要確認: P6経路のMAJOR時挙動、K9以外の細部、工数、費用、`MATERIALITY_BLOCKING_PIN`のCURRENT_SPEC言及の文脈、「基準11件」の出典、複製(コピー)が「暗黙参照禁止」に当たらない解釈。

---

## 6. 追加確認(委任_03、2026-10-05、¥0・コード変更なし)

区別: **確認**=Grep/Read/スクリプト実行で実物確認、**推測**=推論、**要確認**=判定できず。比較スクリプトはスクラッチ(`checker_diff.py`、リポジトリ外)で実行。

### 6-1. (a) Trial Stage 1 CheckerとProduction vfl01 Checkerの差(確認)

**Trial Stage 1 Checkerの構成要素**(runner `stage1_fresh_with_enumeration`@L1672、`run_recheck`@L1914):
- prompt: `trial.build_trial_prompt_template("V4A")`(`er051_open233_checker_trial_variant_01.py` L232)= `vfl01.DEVIATION_PROMPT_TEMPLATE` + `TRIAL_PROMPT_DIFF_BLOCK_V01`(L184、qualifier/ledger_field_basis/observation_consistent) + `TRIAL_PROMPT_DIFF_BLOCK_V4A`(L216、カテゴリ非排他・actor/number/negation/comparison重複true指示)。その後ろにrunnerが`vfl01.RELATED_FACT_ID_INSTRUCTION`・`vfl01.ORIGIN_INSTRUCTION_TEMPLATE`・`SAME_FACT_ID_ENUMERATION_INSTRUCTION`(runner L1453、fresh Stage 1のみ。Recheckは既定OFF)を連結。Recheckは`vfl01.build_prior_issues_instruction`(Production関数)を直接使う。
- developer message: `trial.V4A_DEVELOPER_MSG_WITH_MISCONCEPTION_PRINCIPLE`(er051 L61)= `vfl01.DEVIATION_DEVELOPER_MESSAGE` + 重大誤解原則(15行)。
- schema: `vfl01._extended_deviation_item_schema`(Production関数)+ Trial 5フィールド(`qualifier_present`/`qualifier_text`/`ledger_field_basis`/`observation_consistent`/`matched_notes_id`、er051 L249)+ runnerの`same_fact_id_locations`(L1463)。
- 後処理: `vfl01._apply_deviation_post_hoc_validation`(Production関数、共通)→ `trial.classify_parsed_result_trial(V4A)`(post-hoc v2: changed_actor/number/negation/comparisonがtrueでMINORならBLOCKINGへ昇格、er051 L71)。

**逐語比較の結果**(`difflib`/`diff`でprompt文字列比較):

| 対象 | Production(vfl01) | Trial V4A | 差分 |
|---|---|---|---|
| prompt template | 40行 | 73行 | 追加33行・削除0行(`diff`上の`<`1行は「末尾改行なし」の表示差のみ)。Trialは**Production templateで始まる**(`startswith`=True)。追加は上記2ブロック |
| developer message | 1行 | 16行 | 追加15行・削除0行(重大誤解原則)。Production文字列で始まる |
| deviation item schema | 16キー(10 flag+claim_in_article/issue/explanation/severity+related_fact_id/origin) | +6キー | **追加のみ**(上記5+`same_fact_id_locations`)、削除0。`DEVIATION_FLAG_KEYS`10種は同一 |
| post-hoc | `_apply_deviation_post_hoc_validation` | 同関数+Trial昇格ルール(V4A) | Trialは上乗せ |

**結論(確認)**: 関係は「同一」でも「別物」でもなく、**Productionの上に追加のみで構築されたTrial上位版**(コピー後に乖離ではなく、vfl01をimportして文字列連結)。Production vfl01本体は変更されていない(それがTrialの制約だった)。ただし「Checker本体Prompt・Schema・判定方法は変更しない」という前提は**Trial内**では成立していた(V4A以降は固定)が、**Production vfl01 Checkerに対しては成立していない**: rep30の有効Checkerは vfl01 に対して (i) promptに33行、(ii) developer messageに15行、(iii) schemaに6フィールド、(iv) post-hoc昇格ルール、が追加されたものである。Production vfl01(現状)はこれらを持たない。

**rep30がこのTrial Checkerをどこまで実際に通ったか(確認、`er052_output/open233_self_recovery_flow_runner_01_rep30/instances_s*/*.json` 38件)**: `stage1_call_used=True`は**3 instance-run**、`False`(frozen Stage 1出力の再利用、`stage1_reuse`@runner L8103)が**35 instance-run**。つまりrep30のStage 1検出の大半(35/38)は過去Trialで保存されたCheckerの出力を再利用しており、**Production正式経路で新規にCheckerが実行された例は0**。Stage 1を新規に実行した3件はTrial Checker(`gpt-6-luna`+V4A+誤解原則+列挙)。なお再利用元fixtureが具体的にどのvariantで生成されたかは**要確認**(推測: V4A系・iteration別)。Recheck(各cycle)は実LLMでTrial Checker(`run_recheck`)が動く。

**含意(推測)**: Production初回Checkerは常に新規実行であり、rep30の「Stage 1再利用35件」は構成上Productionに存在しない。Production Checker(現vfl01)でStage 1を新規に走らせたときのrecall・flag分布がTrial V4A版と同等かは、rep30では**検証されていない**(検証されているのはStage 2以降・Rewrite・Recheckの挙動)。配線案は(A)Production vfl01をTrial V4A版へ昇格(opt-inまたは置換)する、(B)現vfl01のまま配線して追加検証する、のどちらかであり、(A)は`run_deviation_check`の40超の呼出元へ波及する(§4-3 K6。既存opt-in方式で後方互換を保てる)。いずれでもrep30と**同一構成にならない部分**が出るため、「Stage 1の新規検出」を対象とした最小の追加検証(例: Production Checker×既存fixture記事の新規Stage 1とfrozen出力の比較、費用は小)が要る可能性がある(判断はOpus#15/Fable)。

### 6-2. (b) モデル(確認)

| 経路 | モデルの決まり方 | 値 | 根拠 |
|---|---|---|---|
| Trial runner(Stage 1新規・Recheck・Stage 2・S1・Rewrite・floor_verify等すべて) | 定数`MODEL`ハードコード、routing非経由 | `gpt-6-luna` | runner L278、`s2p.MODEL`(stage2_production L27)、`summary_kpi_01.json`の`models.runner_MODEL` |
| Production Checker(`vfl01.run_deviation_check`) | `model=MODEL` 既定、`MODEL=routing.WRITER_MODEL`(vfl01 L57) | `gpt-5.6-luna` | `er006_model_routing_contract_01.py` L33。P3/P4/P5は呼出元が`ledger_model=routing.require_model(...WRITER_MODEL)`(P3 L325/611、P4 L1141、P5 L1735/1832)を渡す |
| Production Rewrite(`er010.rewrite_ng_item`) | 呼出元が渡す`ledger_model`(=WRITER_MODEL) | `gpt-5.6-luna` | P3 L239、P4 L1209、P5 L1553 |
| Production Recheck(Local Rewrite後の全文再判定) | `run_deviation_check(model=ledger_model)` | `gpt-5.6-luna` | P3 L262、P4 L1264、P5 L1595 |
| Production Writer Fact Check(diff QA等) | `routing.require_model("WRITER_FACT_CHECK", ...)` | `gpt-5.6-luna` | P3 L243/310 |
| Family X(P1/P2) | `run_deviation_check`既定(`MODEL`) | `gpt-5.6-luna` | er012_e L382等(model引数なし=既定) |

- Model Routing Contract(`CURRENT_SPEC.md` L2291〜): Checker相当(B1/A2 Writer、Deviation Check含む)は`gpt-5.6-luna`=`DECIDED`。Fail-Closed契約(規定外モデルは`ModelContractViolation`)。同節L2323〜: **`gpt-6-luna`はChecker採用候補だがProduction routingは未変更・「Routing変更は別途ユーザー判断」**と明記(Trial=`VALIDATED`、`APPROVED_FOR_PRODUCTION`ではない)。
- 価格(CURRENT_SPEC L2330〜、一次ソースopenai pricing 2026-09-29確認と記載): `gpt-6-luna` Input $0.10/Cached $0.01/Output $0.50 per 1M、`gpt-5.6-luna` $0.20/$0.02/$1.20(同箇所は「正確に半額」と書くが、Output $0.50 vs $1.20は半額でない=記述の不整合、要確認)。
- **事実(確認)**: rep30の`VALIDATED`は**`gpt-6-luna`のみ**で成立。2026-10-05一括承認の本文(DECISION_LOG L18785〜)にProduction routingを`gpt-6-luna`へ変更する明示はGrep上見つからない(「actual model_id/routing確認」が完了条件6にあるのみ)。したがって「Productionで`gpt-6-luna`を使う」ことが承認済みかは**要確認**(推測: 未承認。Model Routing変更は別途ユーザー判断と明記されている)。
- **整理**: (案ア)Productionの経路で`gpt-6-luna`を使う: rep30と同一モデルになるが、Routing Contract変更(Contract表・`PROCESS_MODEL_MAP`・Fail-Closed契約・価格表)でユーザー判断が必要。コストは安価。(案イ)Productionは`gpt-5.6-luna`のまま配線: Contract不変だが、rep30は`gpt-5.6-luna`では未検証→Checker/Stage 2/S1/Rewrite各層の判定挙動(特にSafety系の見逃し0・Human Review 0)は別モデルでの再検証が要る。費用は単価約2倍(Output約2.4倍)、runtime evidence規模は上がる(8〜10 run×約2倍≒¥20〜40、**推定**)。(案ウ)混在(Stage 2/S1のみ`gpt-6-luna`等): 検証済み構成の分解でありrep30と一致しないため不採用寄り(推測)。いずれもOpus#15/ユーザー判断事項。

### 6-3. (c) K8: Checker出力形式変更の不採用と`same_fact_id_locations`(確認)

- **不採用の対象は`CHECKER_SPANS_MODE=violation_spans`**(`claim_in_article`を外し`violation_spans`配列を要求する出力形式変更)。出典: `DECISION_LOG.md` L17604(2026-10-03エントリ内の「Fable判断: `VALIDATED`にしない。既定OFFのまま。…現時点では採用しない」)、`docs/pm/open233_closeout_check_2026-10-04.md` L75・L146(「出力形式変更はユーザー決定2026-10-03で不採用」)。**注(確認)**: DECISION_LOG内に「出力形式変更を不採用とする」というユーザー逐語は本調査のGrepでは見つからず、実体は上記Fable判断(BLOCKING検出12/18→8/18の低下のため)。closeout文書がそれをユーザー決定と表記している。ユーザー逐語の有無は**要確認**(Fableが再照合)。
- **`same_fact_id_locations`は別機構で、より前から採用済み**: 委任_20 W2(Opus L2#4、`DECISION_LOG.md` L14858〜)でStage 1・Recheckのschemaへ追加(追加call 0、¥0)。`DECISION_LOG.md` L17944(Opus#7評価)は「Recheck出力に`same_fact_id_locations`欄を常設…で解消、混入0/35」と評価している。rep30でもschema上は存在(`build_deviation_schema_with_enumeration`、runner L1463/L1870)。
- **`STAGE2_SIBLING_LOCATIONS_CYCLE1`(rep30でON)は、Checker出力もschema変更も使わない**: 実装(runner L8296〜8314)は`deterministic_same_fact_id_location_fallback`(L1622、数値トークン・キーワード重複の決定論)で兄弟箇所を得て、`ls in current_en_text`の逐語実在確認(fail-closed)後にStage 2 batchへ足す。`expand_same_fact_id_locations`(L1529)自体も展開と実在確認の決定論処理であり、入力のうちLLM由来なのはfresh Stage 1(rep30で3 instance-run)の`same_fact_id_locations`フィールドのみ。reuse 35 instance-runは`deterministic_same_fact_id_location_fallback`(L8114)で埋める。
- **結論(確認+推測)**: rep30有効構成の兄弟箇所列挙は**決定論の後段処理が主**で、Checker出力のschema変更を**必須とはしない**。Productionでは「fresh Stage 1でLLM列挙を使うか、決定論fallbackのみとするか」の選択になる。決定論のみならばK8は競合ではなく、設計で吸収可能(**推測**: rep30は35/38が決定論fallbackで検証済み。fresh Stage 1でLLM列挙を使った3件との同等性は未比較)。LLM列挙を使う場合も`same_fact_id_locations`は`violation_spans`(不採用)とは別機構(claim_in_articleを残す加算フィールド)であり、vfl01の既存opt-in方式(L782〜787)で後方互換に入れられるが、「Checker出力形式変更」にあたるか否かはユーザー確認候補(Fable/Opus判断)。K8は§4-3の「競合の可能性高」から「**競合ではない/設計で吸収可能(決定論のみの場合)**」へ見直しを推奨する。

### 6-4. (d) K1: cycle上限(確認)

- Production(`er010_ledger_local_rewrite_09.py` L29・L38): `MAX_REWRITE_ATTEMPTS=3`、`MAX_REWRITE_CYCLES = MAX_REWRITE_ATTEMPTS`(L38)。ユーザーがER-010-NO9で許可した「既存上限の適用範囲整理」(L31〜36コメント)。**記事全体のRewrite-Recheck cycle最大3、無条件**(cycleごとに文単位attempt最大3)。
- Trial(runner L279・L283): `MAX_CYCLES=2`、`HARD_MAX_CYCLES=MAX_CYCLES+1=3`(L8572: cycle==MAX_CYCLES+1は「別claimでblocking厳密減少」のとき1回だけ許可)。上限後に**判定専用cycle**(`JUDGE_ONLY_CYCLE_AFTER_CAP`、L8293、cycle>HARD_MAX_CYCLES、Rewriteなし=Stage 2+S1のみ、API呼出あり)→T(最終手段)→許可リスト4理由。
- **差(確認)**: Rewrite実行cycleは両者とも最大3であり、Trialは「3以内かつ条件付き(2+条件付き1)」でProduction以下。違いは(i)cycle 3が条件付きか無条件か、(ii)上限後の判定専用cycle(Rewriteしない、設計B §18-8で「上限=Rewrite回数、判定回数ではない」と整理)とT(削除)が追加されること、(iii)出口が`NG_REVIEW_REQUIRED`/STOPから許可リスト4理由へ変わること。
- **事実(確認)**: rep30の費用(平均¥0.573/run)・Human Review 0・STAGE4 0は、**Trial定義(2+条件付き1+判定専用cycle+T)で得た値**。Production `MAX_REWRITE_CYCLES=3`(無条件cycle 3)へ変えるとrep30と異なる構成になる(費用・Human Reviewとも未検証、推測: cycle 3が無条件なら費用は増え得る)。
- **見立て(推測)**: Rewrite回数の上限を超えないため「既存上限の回避」にはあたらない。Trial定義をそのままProduction新module側の上限として使い、`er010.MAX_REWRITE_CYCLES`は旧経路用に据え置く設計なら吸収可能。ただし「判定専用cycleは上限に含めない」は既存上限の意味の再定義でありユーザー確認候補(Opus#15/Fable判断)。

### 6-5. (e) K4: Family XのRuntimeError STOPとladder④・T(確認)

- P1 Advanced(`er012_e_family_entertainment_two_level_runner_01.py`): MAJORかつ`origin==ja_source`→`JARecheckRequiredError`(L392〜399)。それ以外はmust-fixで**全文を1回だけ再生成**(L401〜404「must-fixで1回だけ再生成します」)。再生成後`split_family_x_article_text_v2`が`status!="OK"`(paragraph_count<3)なら`RuntimeError("[STOP] ... 段落数retryは既に使用済みのため、これ以上自動再生成せずSTOPします")`(L409〜414)。再検査(`prior_issues=must_fix_used`、L415〜417)で`LEDGER_COMPLIANT`かつ`all_prior_issues_resolved`でなければ`rejected_advanced_attempt2.md`保存後`RuntimeError("[STOP] ... 再生成後もMAJOR、または前回指摘の未解消あり ... 本文を手で直さずSTOPします")`(L423〜432)。P2 Standardは同型(L478〜523付近)。
- Trial側(rep30): 全文再生成retryは存在しない(Rewriteはladder①〜④/⑥・T。④=段落Rewrite、T=1記事1回の削除最終手段、出口は許可リスト4理由、`JA_MODE=english_only`でJA本文は修正しない)。
- **関係(確認+推測)**: (1)現行P1/P2の「1回の全文再生成→STOP」は、**Local Rewriteが存在しない**Family X固有の唯一の自己修復+終端であり、Trialのladder/T/許可リストはこれと同じ位置(MAJOR検出後〜終端)を置き換える。(2)両者を同時に残すと順序規定が要る(Local Rewrite→不成立→全文再生成、または全文再生成→再検査→Local Rewrite)。全文再生成を廃止するとP1/P2の既存retry機構を落とす=「既存のretry/fallback/regeneration機構との整合」の確認対象。残す場合、`_family_x_ensure_split_or_paragraph_retry`(L294、段落数retry、独立軸)と、ladder④(段落Rewrite)後の段落数再検証を衝突させない規定が要る。(3)`JARecheckRequiredError`(origin=ja_source)はTrialの`JA_MODE=english_only`(JAは修正しない)と整合するかが**要確認**(runnerのja_pending扱い、Opus#15論点)。(4)終端が`RuntimeError`(プロセスSTOP)から許可リスト出口(Human Review)に変わる点は、Family Xのoperator運用(STOP→手動対応)と整合するか要確認。
- 見立て(推測): 「全文再生成を残すか廃止するか」「JA由来MAJORの扱い」は設計で吸収できるが、品質・費用・STOP運用に影響する選択のため、競合の可能性は残る。Opus#15で本物の競合か切り分け、必要ならユーザー判断候補。

### 6-6. (f) OPEN-233-A1-PROD必須確認「解放claimを2-of-2降格の対象から外す」(確認)

- 該当行(`OPEN_ITEMS.md` L727、委任_59・Fable判断2(g)): 「機械判定の解放(F5、LLM確認)をProduction配線する場合の必須対策: (1)解放されたclaimを2-of-2降格の対象から外す、(2)`dev`のフラグを書き換えない、(3)確認callの失敗はBLOCKING固定、(4)cycleごとに再評価する」。同行の別箇所(委任_68追記、Opus#10): 「S1(降格2-of-2、修正版=2回目の最終materialityで比較・NORMAL群2-of-2は既定OFF)はStage 2と一体で配線」「NORMAL群2-of-2(`apply_stage2_two_of_two`、正解ラベル依存・向きが逆)は配線しない」。
- 「2-of-2」には2種ある: (i)NORMAL群2-of-2(Trial補助、`STAGE2_NORMAL_TWO_OF_TWO=OFF`、配線しない)、(ii)S1(Stage 2第2意見、`STAGE2_SECOND_OPINION=ON`、配線対象)。(1)の文意は元々「floor_verifyで解放済みのclaimを、確認役/2-of-2系の降格で二重に扱わない」。
- **確認**: runnerの`checker_major_downgraded_target`(L3326〜3337、確認役・Tier 0・S1共通の対象判定)が`floor_verify_rec.released`を`False, "floor_verify_released"`として降格対象から**既に除外**している。この除外は`STAGE2_NORMAL_TWO_OF_TWO`スイッチと無関係に効く。
- **読替案**: 「解放claimを2-of-2降格の対象から除外」を「`floor_verify`解放済みclaimをS1の降格対象から除外する(`checker_major_downgraded_target`相当を新Production moduleに移す)。NORMAL群2-of-2は配線しないため(1)の旧文面の対象外」へ置換する。K13は非競合のまま、SSOT上の文言整理(DRC①)で足りる。ユーザー判断は不要(通常のSSOT整合)。

### 6-7. §4-3 K判定の更新(委任_03時点、推測を含む。最終判定はOpus#15→Fable)

| ID | 委任_02時点 | 委任_03時点の見立て |
|---|---|---|
| K1 | 競合の可能性高 | 吸収可能寄り(Rewrite cycle最大3は同じ、Trialは条件付き)。「判定専用cycleは上限に含めない」の再定義のみユーザー確認候補 |
| K4 | 競合の可能性 | 競合の可能性が残る(全文再生成の存廃・順序・JA由来MAJOR・終端がSTOPから許可リスト出口へ変わる点)。Opus#15で切り分け |
| K7 | 設計/ユーザー確認 | 要ユーザー判断の可能性高(Contractが「Routing変更は別途ユーザー判断」と明記、rep30は`gpt-6-luna`のみで成立) |
| K8 | 競合の可能性高 | 競合ではない/設計で吸収可能(決定論のみの場合)。`violation_spans`不採用と`same_fact_id_locations`は別機構 |
| K13 | 非競合 | 非競合(S1側で既に実現)。読替のみ |
| 新規K14 | - | **Production初回CheckerはTrial V4A版ではない**(6-1)。rep30は35/38でStage 1を再利用し、Production新規Stage 1は未検証。要設計+最小追加検証 |
