# FAMILY-A-DISCOVERY-SPEC-FINALIZATION-RECONCILE-01 — Report

管理ID: `FAMILY-A-DISCOVERY-SPEC-FINALIZATION-RECONCILE-01`(**読み取り専用の分析タスク、Production配線なし**)。実施者: Sonnet(sonnet-worker、Fable委任)。実施日: 2026-09-10。API呼び出し(LLM/TTS)は一切行っていない(¥0)。編集はroot直下の本ファイル1つのみ(`docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md`・`OPEN_ITEMS.md`・`DECISION_LOG.md`・`CURRENT_SPEC.md`・`ARTIFACT_REGISTRY.md`・コード・Promptは未編集)。Git操作は行っていない。

用語注記: 「VALIDATED」=Trialとして技術的に成立したことの確認、「APPROVED_FOR_PRODUCTION」=ユーザーによるProduction採用決定、「PRODUCTION_WIRED」=Production経路への実装配線完了。本報告ではこの3つを混同しない。

## エグゼクティブサマリー(10行以内)

1. Discovery Focus Module本体(Part A、Trial-05〜09と一字一句同一)は`VALIDATED(Trial)`止まりで、Production採用案は2026-09-09ユーザー決定により不承認(REJECTEDではなく再改善中)。
2. Household最終版が使ったPart B案1(`cautionary_constrained`、保険文対策の1文追加)は2026-09-10にProduction採用(c)見送りで確定済み(既決事項、変更提案なし)。
3. Part Bを除いた「Part Aのみ(current_focus/Before)」条件は、Trial-09/10でN=6×2回、保険文2/6・REVIEW率0/6という結果が既にあり、Household最終版はこの条件でも成立する見込みが高い(推測を避け、実際にBefore条件で再生成していない点はSSOT上で特定不可)。
4. `editorial_mode="discovery_why"`はregistry未登録のまま。Household最終版はこの引数を経由せず、Focus Moduleテキストを`build_common_block()`へ直接注入する方式で生成されており、登録の要否とは独立に動作した。
5. Point Role Planning・Point Value QA・Point Overlap QA・Diagnostic Full Retry(Loop Budget=2)・Local Rewrite Loop・Fact Checker・Ledger Deviation Checker v2・Directional Fact Precheckはいずれも`PRODUCTION_WIRED`の共通Writer経路であり、Discovery固有の変更なしにHousehold最終版でそのまま機能した(runtime evidence: `point_role_planning_retry1.json`等の存在)。
6. Verified Fact Ledger v5はHousehold固有の事実精度是正(FACT-03/04整合)であり、Discovery/Why型の一般仕様ではない。
7. A2/B1Bは同一のDiscovery Focus Moduleテキスト(byte一致を確認)・同一のQA/retry経路を共有しており、構造上の差分はA2 JAPANESE_TITLES gap(OPEN-137)のみ。
8. Production採用はいずれもユーザー判断が必要(採用/不採用の混同回避)。

## 1. Discovery Focus Module(Part A/Part B構成)

| 項目 | 現行正式仕様(CURRENT_SPEC出典) | Trial結果 | Household最終版での実使用条件 | 正式仕様として採る候補 | 根拠 | 残リスク |
|---|---|---|---|---|---|---|
| Part A(Focus Module本体) | 「## Discovery/Why(Pool型)」節、`DISCOVERY_FOCUS_MODULE_BLOCK`行(CURRENT_SPEC.md 793行): `VALIDATED(Trial)`止まり。**現行Production採用案は2026-09-09ユーザー決定により不承認**(REVIEW_REQUIRED増加・Point多様性低下懸念、ただしREJECTEDではなく再改善中) | Trial-05でVALIDATED(A2/B1)。Trial-07(Ledger v4時点)でREVIEW率baseline比約5倍・多様性低下観測。Trial-09(Ledger v5是正後)でこの懸念はほぼ解消(真のREVIEW_REQUIRED率0/6)。Trial-10(D-4)でもcurrent_focus(Part Aのみ)条件はREVIEW率0/6 | Part B案1込みで使用(Part Aは無変更のまま流用、`er011_output/household_unified_final_candidate_01/{a2,b1b}/audit/prompt.txt`216行で「他は現行版[Trial-05/07/08/09]と一字一句同一」と明記) | **条件付き採用候補**(Part Aのみ)。ただし現行ユーザー決定は「不承認」のまま変更されておらず、本報告はこの決定を覆す提案をしない | OPEN_ITEMS.md OPEN-135行(2026-09-09ユーザー決定「現行Production採用案は不承認」の記述、本報告執筆時点で撤回記録なし) | Ledger v5是正後の再検証はHousehold1テーマのみ(N=3×2Trial)。他テーマでの追試なし |
| Part B案1(cautionary_constrained) | CURRENT_SPEC.mdに記載なし(未承認候補のためProduction仕様として記載されていない) | `FAMILY-A-DISCOVERY-STAGE4-CAUTIONARY-LANGUAGE-TRIAL-10`でVALIDATED(Trial範囲)。保険文Before 2/6→After 0/6、Fact Safety指標(blocking/Ledger Deviation/創作)は両条件で維持。ただしREVIEW率がBefore 0/6→After 2/6へ上振れ(N=3のため因果未確定) | 使用(`CAUTIONARY_FOCUS_BLOCK`をそのままimportし`editorial_type_module_block`引数へ注入) | **不採用で確定済み**(ユーザー判断、2026-09-10、(c)見送り) | DECISION_LOG.md`PM-CLOSEOUT-CONSOLIDATION-64`(6点根拠)、OPEN_ITEMS.md OPEN-135行 | 既決事項のため本報告では再検討しない(指示範囲外) |
| Part Bを除いた場合に残るもの | — | Trial-09/10のcurrent_focus(Before)条件そのものがPart A単独の実測(N=6×2Trial=12本相当) | Household最終版はPart B込みで生成されたため、**Part Aのみでの同一記事の再生成は行われていない**(SSOT上で特定不可) | 下記「保険文対策を除いてもHousehold最終版が成立するか」参照 | 同上 | 同一記事でのBefore再生成という直接比較データはない(Trial-09/10は別記事run) |

## 2. `editorial_mode="discovery_why"`(registry未登録)

| 項目 | 現行正式仕様 | Trial結果 | Household最終版での実使用条件 | 正式仕様として採る候補 | 根拠 | 残リスク |
|---|---|---|---|---|---|---|
| registry登録要否 | CURRENT_SPEC.md「News Editorial Mode(Trend Synthesis)」節(696行)に、`resolve_editorial_type_module_block(editorial_mode)`という既存の名前解決機構が存在し、現状登録済みmodeは`"trend_synthesis"`のみ。`"discovery_why"`は未登録 | OPEN_ITEMS.md OPEN-135/138行で繰り返し「登録は別途UDR」「本Trialでは未登録の想定名のまま使用」と明記 | **未使用**。`er011_household_unified_final_candidate_01_run.py`は`resolve_editorial_type_module_block()`を一切呼ばず、`prod_gen.build_common_block(..., editorial_type_module_block=CAUTIONARY_FOCUS_BLOCK)`へ直接テキストを渡すバイパス方式で生成した(`er011_output/household_unified_final_candidate_01/a2/audit/prompt.txt`216行のコメント「editorial_mode="discovery_why"は未登録の想定名」も同事実を裏づける) | **見送り確定**(ユーザー判断、2026-09-10、Part B案1不採用と同時に決定) | DECISION_LOG.md`PM-CLOSEOUT-CONSOLIDATION-64`「`editorial_mode="discovery_why"`の正式registry登録もあわせて見送る」 | 見送り後の運用上の扱い: 今後Discovery記事を生成する場合、Household最終版と同じ「build_common_block()へeditorial_type_module_blockを直接渡す」バイパス方式が事実上の前例となっているが、これはTrial限定の手順でありProduction initial pathとして正式採用されていない(**新規名称扱い**、Dangling Reference Check参照) |

## 3. Pointの切り口(Point Role Planning、Discovery型でのPoint設計、Point Overlap対策)

| 項目 | 現行正式仕様 | Trial結果 | Household最終版での実使用条件 | 正式仕様として採る候補 | 根拠 | 残リスク |
|---|---|---|---|---|---|---|
| Point Role Planning + Point Value QA | CURRENT_SPEC.md 974行: `DECIDED`(`PRODUCTION_WIRED`)。全Editorial Type共通(Discovery固有ではない)、`er011_point_role_value_planning_01.py::run_point_role_planning()`がFull Article Writer呼び出し直前に毎回再計画(初回・Diagnostic Full Retry各attemptで再計画) | No.18 B1B実データでNG検出→retry解消の実runtime証拠あり | 使用(`er011_output/household_unified_final_candidate_01/a2/audit/point_role_planning_initial.json`・`point_role_planning_retry1.json`・`point_value_qa_attempt0.json`・`point_value_qa_attempt1.json`が存在、A2でPoint Overlap記事全体retry1回発生と整合) | **既に採用済み(汎用spec、Discovery固有の追加判断不要)** | CURRENT_SPEC.md 974行、実ファイル確認 | Discovery/Why型特有の「切り口」設計(Point Role hint Discovery版)は別項目としてDEFERREDのまま(下記) |
| Point Role hint(Discovery版) | CURRENT_SPEC.md 795行: `DEFERRED`(D3)。「Trial-03の接続パターンは技術的に転用可能と考えられるが、Discoveryでのruntime効果は未検証」 | 未実施 | 未使用(Household最終版はPoint Role Planning[汎用spec]のみ使用、Discovery版Point Role hintは使用していない) | **判断材料不足**(追加Trial要) | CURRENT_SPEC.md 795行 | Discovery版hintと汎用Point Role Planningの役割重複・競合整理が未了 |
| Point Overlap対策のDiscovery適用状況 | CURRENT_SPEC.md 972行: Point Overlap QA(lexical overlap閾値0.40)+Diagnostic Full Retry(Loop Budget=2)は`PRODUCTION_WIRED`、mode非依存(prompt再構築を行わないため) | Household最終版でA2が1回目Point Overlap NGを検知しDiagnostic Full Retryで2回目に解消(runtime evidence: `run_summary.json`) | 使用(既存機構をそのまま利用、Discovery固有のretry方針は追加していない) | **既に採用済み(汎用spec)** | CURRENT_SPEC.md 699行「Evidence Compression Editor・Point Overlap QA・Fact Checker・Ledger Deviation Checkerはいずれも生成済み記事テキストのみを操作し、prompt再構築を行わないためmode非依存で無変更のまま機能する」 | News側で報告されているPoint Overlap構造課題(語彙重複3層反復、cross_point_overlapがretry判定未使用等、`FAMILY-A-NEWS-STAGE4-REDESIGN-INVENTORY-01`)がDiscovery側にも該当する可能性はあるが、本報告の情報源範囲では未検証(SSOT上で特定不可) |

## 4. Fact Safety(Verified Fact Ledger v5、FACT-03、Ledger Deviation、directional fact precheck、Fact Checker)

| 項目 | 現行正式仕様 | Trial結果 | Household最終版での実使用条件 | 正式仕様として採る候補 | 根拠 | 残リスク |
|---|---|---|---|---|---|---|
| Verified Fact Ledger v5(Household固有) | CURRENT_SPEC.mdに「v5」という版番号での記載なし(Household固有のTrial/是正履歴のためOPEN_ITEMS.md OPEN-138行が正式記録)。CURRENT_SPEC.md 825行のFact Safety共通仕様(Ledger→Fact Checker→Ledger Deviation Check)自体は`DECIDED`(`PRODUCTION_WIRED`) | `HOUSEHOLD-LEDGER-FACT-03-REVERIFICATION-01`→`HOUSEHOLD-LEDGER-FACT-03-04-CONSISTENCY-FIX-03`によりv3→v4→v5(バナナ・トマトをFACT-03の低湿度ドロワー例から削除しりんご・洋梨のみへ絞込、FACT-04と無矛盾化) | v5を無変更でread-only使用(`t10.HOUSEHOLD_LEDGER_PATH`、Gate4で`ledger_has_v5_marker`確認) | **Household記事固有の事実修正として既に確定済み**(Discovery/Why型の一般仕様ではない、他テーマのLedgerに機械的に適用するものではない) | OPEN_ITEMS.md OPEN-138行 | v5是正はHousehold1テーマのみ。同種の事実精度リスク(争いのある家庭用ガイド情報)が他Discoveryテーマにも潜在する可能性はSSOT上で特定不可 |
| FACT-03再検証(Fact Checker実行結果) | 同上 | 独立Fact Checker(Web検索付き)でFAIL確定(UC Davis 90〜95%は商業貯蔵条件、家庭用対応づけ誤り) | 是正済みv5を使用(FACT-03問題自体は解消) | 該当なし(既に是正完了) | OPEN-138行 | — |
| Ledger Deviation(v2、Hook-aware、Local Rewrite) | CURRENT_SPEC.md 826/931/932行: いずれも`PRODUCTION_WIRED`(全Editorial Type共通) | No.9/No.18実データで実発火・解消を確認済み(Discovery固有ではない) | 使用(`ledger_status=LEDGER_COMPLIANT(0件)`、A2/B1Bとも) | **既に採用済み(汎用spec)** | 同上 | Local Rewrite LoopはFact Checker REVIEW_REQUIREDには反応しない設計(意図的な区別、CURRENT_SPEC.md 825行) |
| directional fact precheck | CURRENT_SPEC.md 962行: `DECIDED`(`PRODUCTION_WIRED`、暫定策)。**「補助的な警告機能であり、Fact方向の安全性を保証するものではない」**と明記、rule-based・全Editorial Type共通 | fixture 23件全PASS、No.7実データで実証(Discovery固有ではない) | 使用(`audit/directional_fact_precheck.json`が存在、生成自体はblockしない設計のまま) | **既に採用済み(汎用spec)** | CURRENT_SPEC.md 962行 | OPEN-72(構造化comparator等の本格対策)は`DEFERRED / AFTER USER VALIDATION`のまま |
| Fact Checker(REVIEW_REQUIRED non-blocking advisory) | CURRENT_SPEC.md 825行: `DECIDED`(`PRODUCTION_WIRED`、2026-09-01)。全Editorial Type共通 | Household最終版でA2/B1BともPASS | 使用(fact_verdict=PASS) | **既に採用済み(汎用spec)** | 同上 | — |

## 5. Writer / retry / fallback(Loop Budget、Point Overlap記事全体retry、local rewrite、fallback経路)

| 項目 | 現行正式仕様 | Trial結果 | Household最終版での実使用条件 | 正式仕様として採る候補 | 根拠 | 残リスク |
|---|---|---|---|---|---|---|
| Diagnostic Full Retry(Loop Budget=`POINT_OVERLAP_ARTICLE_RETRY_MAX`=2) | CURRENT_SPEC.md 972行: `PRODUCTION_WIRED`(確定)。全Editorial Type共通、mode非依存 | ER-22/23で実runtime evidence取得済み | A2で1回発火・解消(retry内)、B1Bは0回 | **既に採用済み(汎用spec)** | CURRENT_SPEC.md 972行、`gate4_check.json`の`point_overlap_article_retry_max_loop_budget`確認済み | — |
| Point-only regeneration | CURRENT_SPEC.md 972行: `POINT_ONLY_REGENERATION_ENABLED = False`(ユーザー判断により無効化済み、恒久) | ER-20でFact安全性崩壊の実例あり(採用しない理由の根拠) | 未使用(既定Falseのまま) | 該当なし(既に不採用で確定) | 同上 | — |
| Local Rewrite Loop(MAJOR時) | CURRENT_SPEC.md 932行: `APPROVED_FOR_PRODUCTION`→`PRODUCTION_WIRED`(MAX_REWRITE_ATTEMPTS=3、MAX_REWRITE_CYCLES=3、Point-context-only拡張込み) | No.9/No.18実データで実証済み | 使用(`local_rewrite_cycles.json`・`local_rewrite_results.json`が存在、ただしMAJOR残存件数は本報告のRead範囲では未確認、`ledger_status`はLEDGER_COMPLIANT 0件のため最終的にMAJOR残存なしと推定されるが、ファイル内部詳細はSSOT上で特定不可) | **既に採用済み(汎用spec)** | CURRENT_SPEC.md 932行 | — |
| fallback経路(NG_REVIEW_REQUIRED) | CURRENT_SPEC.md 1011行: Production全体retry/regenerate/polling上限の横断監査で「上限が全く無い経路は0件」と確認済み | 同上 | 発動せず(A2/B1BともOK到達) | **既に採用済み(汎用spec)** | CURRENT_SPEC.md 1011行 | — |

## 6. QA / Validator(Point Value QA、Point Overlap QA、Key Phrase redundancy QA、Support QA、Audio Gate)

| 項目 | 現行正式仕様 | Trial結果 | Household最終版での実使用条件 | 正式仕様として採る候補 | 根拠 | 残リスク |
|---|---|---|---|---|---|---|
| Point Value QA | CURRENT_SPEC.md 974行: `DECIDED`(`PRODUCTION_WIRED`) | No.18実データ | 使用(A2でattempt0→attempt1、retry発生と整合) | **既に採用済み(汎用spec)** | 同上 | — |
| Point Overlap QA(lexical、閾値0.40) | CURRENT_SPEC.md 972行: `PRODUCTION_WIRED`(監視+retry統合) | 同上 | 使用(A2で発火・解消) | **既に採用済み(汎用spec)** | 同上 | 閾値0.40の題材別ミスキャリブレーション懸念がNews側監査(`FAMILY-A-NEWS-STAGE4-EVIDENCE-ALLOCATION-AUDIT-01`)で指摘されているが、Discovery側での再検証はSSOT上で特定不可 |
| Key Phrase Set Redundancy QA | CURRENT_SPEC.md 873行: `DECIDED`(`PRODUCTION_WIRED`)。`KEY_PHRASE_REDUNDANCY_RETRY_MAX`=2 | No.18 specfix_v2実データで全10ペアPASS確認 | 使用(A2/B1Bとも1回で`REDUNDANCY_PASS`到達) | **既に採用済み(汎用spec)** | 同上 | — |
| Support QA(Preview/Comment) | CURRENT_SPEC.md「Cross-level仕様」節各行(Preview原則・日本語ラベル禁止等)、`DECIDED` | — | 使用(Scaffold全項目OK) | **既に採用済み(汎用spec)** | 同上 | — |
| Audio Validation Gate | CURRENT_SPEC.md 961行: `DECIDED`(`PRODUCTION_WIRED`)。Assembly直前の検証ゲート、mode非依存 | — | 使用(Gate OFF/opt-in ON両方PASS、A2 330.0秒/peak 0.98[headroom]、B1B 302.8秒/peak 0.953、clippingなし) | **既に採用済み(汎用spec)** | 同上 | — |

## 7. A2 / B1B整合

| 項目 | 現行正式仕様 | Trial結果 | Household最終版での実使用条件 | 正式仕様として採る候補 | 根拠 | 残リスク |
|---|---|---|---|---|---|---|
| Discovery Focus Moduleテキスト | CURRENT_SPEC.md「Cross-Level Consistency Check(A2/B1片側修正の禁止)」行(828行)が一般ルールとして存在 | — | A2/B1Bとも`er011_output/household_unified_final_candidate_01/{a2,b1b}/audit/prompt.txt`216行が完全に同一文言(byte一致確認済み、grep結果同一) | **既に整合済み**(両レベル同一module呼び出し経路) | 実ファイル比較確認 | — |
| Writer/QA/retry経路 | 同一の`prod_gen.run_one_pattern()`をA2/B1Bとも呼ぶ(`er011_household_unified_final_candidate_01_run.py`80-82行、`LEVELS`辞書でinstructionのみ差し替え) | — | A2/B1Bとも同一QA一式(Point Role Planning/Value QA/Overlap QA/Fact Checker/Ledger Deviation/Directional Precheck)を通過 | **既に整合済み** | 同上 | — |
| JAPANESE_TITLES未登録gap(OPEN-137) | CURRENT_SPEC.md 703行: `DECIDED`(直訳の人手供給を正式initial pathとして採用、自動化はOPEN-137として`DEFERRED`) | `FAMILY-A-COMPLETION-A2-TREND-END-TO-END-01`で既知gap確立 | **A2のみ**で再発(B1Bは日本語タイトル不要のため対象外)、既存Household完成版タイトルを流用(新しい主張・数字追加なし、`audit/a2_japanese_title_gap_note.json`) | **既存の人手供給initial pathを継続**(自動化は別途ユーザー判断、Production採用ではなく運用手順) | OPEN_ITEMS.md OPEN-137行、CURRENT_SPEC.md 703行 | 新規Discoveryテーマ(Household以外)で同種gapが今後も発生する構造的問題(A Family全体の共通gap、Discovery固有ではない) |

## 正式仕様として採るべき候補一覧

**採用推奨(Discovery固有の新規判断不要、既に`PRODUCTION_WIRED`の汎用spec)**: Point Role Planning + Point Value QA、Point Overlap QA + Diagnostic Full Retry(Loop Budget=2)、Local Rewrite Loop、Fact Checker(non-blocking advisory)、Ledger Deviation Checker v2(Hook-aware込み)、Directional Fact Precheck、Key Phrase Set Redundancy QA、Audio Validation Gate、Cross-Level Consistency Check。理由: いずれも全Editorial Type共通の既存Production機構であり、Household最終版で無変更のまま実際に機能したrantime evidenceがある。Discovery/Why固有の追加判断・改変は不要。

**条件付き(Household1テーマの事実修正、Discovery一般仕様への機械的適用は不可)**: Verified Fact Ledger v5。理由: FACT-03/04の記述自体はHousehold固有の内容であり、他Discoveryテーマへ転用する性質のものではない。

**不採用(既に確定済み、本報告で再検討しない)**: Discovery Focus Module Part B案1(`cautionary_constrained`)、`editorial_mode="discovery_why"`の正式registry登録。理由: 2026-09-10ユーザー判断により(c)見送りで確定済み(DECISION_LOG.md`PM-CLOSEOUT-CONSOLIDATION-64`)。

**要追加Trial(判断材料不足)**: Discovery Focus Module Part A本体のProduction採用可否(現行ユーザー決定は「不承認」のまま)、Point Role hint(Discovery版)、Engagement/Storytelling原則のDiscoveryへの適用、myth-correction型の扱い、Discovery固有Research方式(説明源優先順位ガイドライン)。いずれもCURRENT_SPEC.md「## Discovery/Why(Pool型)」節で`DEFERRED`または`USER_DECISION_REQUIRED`のまま。

## 「採らない」と確定したもの(保険文制約案)の位置づけ、およびそれを除いた場合の成立可否

Part B案1(`cautionary_constrained`)は2026-09-10にProduction採用(c)見送りで確定済みの既決事項であり、本報告はこの決定の再検討を提案しない(タスク範囲外)。

Household最終版はPart B案1込みで生成されたため、**同一記事をPart A単独(Before)条件で再生成した直接比較データは存在しない**(SSOT上で特定不可)。ただし、Part A単独(current_focus)条件の実測データはTrial-09・Trial-10で計N=6×2回=12本存在し、以下が確認されている。

- 保険文(BROAD regex): Before 2/6(33%、両Trialとも)。出現は争いのある家庭用ガイド記述(FACT-03系、ストロベリー/オレンジの高湿度分類)を明示的に扱ったrunに限定(この争点に触れないrunでは0/16)。
- REVIEW率: Before 0/6(0%、両Trialとも)。
- Fact Safety指標(blocking/Ledger Deviation/創作): いずれもBefore/After両条件で維持。

以上から、Part B(保険文対策)を除いた「Part Aのみ」条件でも、既存のPoint Overlap QA・Fact Checker等の汎用QA一式を通過してHousehold記事が成立する可能性は高いと考えられる(Trial-09/10のcurrent_focus実績がその根拠)。ただし、この記事(Household最終版と同一の生成条件・シードでのBefore単独実行)そのものを対象に再生成して確認した記録はなく、「必ず成立する」と断定はできない。保険文2/6という結果はDiscovery Focus Module Part Aの仕様上の既知の残存事象であり、Part B見送り後は**Human Reviewでの目視修正に委ねる**という選択肢がTrial-10 REPORT(163-177行)で既に提示されている。

## 追加Trialが必要な項目

| 項目 | 目的 | 設計案 | N | 見込み費用 | 判断材料 |
|---|---|---|---|---|---|
| Discovery Focus Module Part A本体のProduction採用可否再検証 | 2026-09-09不承認決定(REVIEW増加・多様性低下懸念)がLedger v5是正後も妥当か再確認 | Household以外のPool型テーマ(複数)でPart A単独条件をN=5程度×A2/B1Bで実施し、REVIEW率・多様性指標を測定 | N=5程度×複数テーマ | 既存Trial単価(Trial-10実測¥100.5/12本)から比例推定でテーマ数×¥50〜100程度(実測なしの見込み、断定しない) | REVIEW率・多様性がHousehold単一テーマの結果と整合するか |
| 保険文問題へのHuman Review目視修正運用の実効性確認 | Part B不採用確定後の代替策(目視修正)が実際に機能するか | Part A単独で複数テーマ生成→保険文検出→人手修正の運用フローをN=3程度で試行 | N=3程度 | 既存機構の流用のためLLM追加費用は限定的(見込み、実測なし) | 目視修正の運用負荷・見落とし率 |
| Point Role hint(Discovery版)のruntime効果検証 | CURRENT_SPEC.md 795行で「未検証」と明記されている効果を確認 | News側Trial-03の接続パターンをDiscoveryへ転用し、Point Role Planningとの重複・競合を確認 | 設計未定(SSOT上で特定不可) | 見込み不明 | News側で確認された重複構造(語彙重複3層反復)がDiscovery側でも同様に発生するか |

## Dangling Reference Check

- `editorial_mode="discovery_why"`: **未定義**(既存SSOTのregistry未登録、OPEN-135/138行に「未登録の想定名」と明記済み)。
- `cautionary_constrained` / `current_focus`: `FAMILY-A-DISCOVERY-STAGE4-CAUTIONARY-LANGUAGE-TRIAL-10`固有のTrial条件名であり、CURRENT_SPEC.mdの正式仕様名ではない(**Trial限定の名称**)。
- 「build_common_block()へeditorial_type_module_blockを直接渡すバイパス方式」: 本報告で言及したHousehold最終版の実装パターンについて、正式なProduction initial pathとしての名称はSSOT上に存在しない(**新規名称**、正式採用されていない)。
- `Verified Fact Ledger v5`: CURRENT_SPEC.mdには版番号としての記載なし。OPEN_ITEMS.md OPEN-138行が正式記録(Household固有)。
- `Point Role Planning`・`Point Value QA`・`Diagnostic Full Retry`・`Local Rewrite Loop`・`Directional Fact Precheck`・`Key Phrase Set Redundancy QA`・`Audio Validation Gate`: いずれもCURRENT_SPEC.md本体に定義済み(出典行は各節参照)。

## ユーザー判断が必要な項目

1. **Discovery Focus Module Part A本体のProduction採用可否**: 2026-09-09の「不承認」決定を維持するか、Ledger v5是正後の結果(Trial-09/10でREVIEW率0/6)を踏まえて再改善Trialへ進めるか。推奨: 他テーマでの追試(N=5程度)を条件に再検討可能と考えるが、Production採用そのものはユーザー判断。
2. **保険文対策の代替運用**: Part B見送り確定後、Part A単独で発生しうる保険文(頻度目安2/6)をHuman Review目視修正に委ねる運用で良いか、追加Trial(Part B以外の対策案)を求めるか。
3. **`editorial_mode="discovery_why"`の位置づけ**: 正式registry登録を見送ったまま、Household最終版が使った「直接テキスト注入」方式を今後もTrial限定の暫定手順として扱うか、それとも正式initial pathとして名称・手順を定義するか。
4. Production採用(`APPROVED_FOR_PRODUCTION`)はいずれの項目についても人間ユーザーのみが判断できる(PM_GOVERNANCE 10節・CLAUDE.md準拠)。本報告はいずれの項目についても採用判断を下していない。

## SSOT上で特定できなかった点

- Household最終版を「Part A単独(Before)」条件で同一記事として再生成した場合の実際の結果(保険文発生有無等)は記録がない。
- Household最終版のLocal Rewrite Loop実行結果の内部詳細(MAJOR検出件数・cycle数)は`local_rewrite_cycles.json`/`local_rewrite_results.json`の存在は確認したが、内容の逐語的確認は本報告の範囲では行っていない(`ledger_status=LEDGER_COMPLIANT(0件)`という最終結果のみ確認済み)。
- Point Overlap QA・Fact Checker閾値0.40の題材別ミスキャリブレーション問題(News側監査で指摘)がDiscovery/Household側にも該当するかは未検証。
- 追加Trialの具体的コスト見込みは実測データがなく、既存Trial単価からの比例推定に留まる。

## QCD(品質/費用/納期)

- **品質**: 情報源はCURRENT_SPEC.md・OPEN_ITEMS.md・DECISION_LOG.md・2件のREPORT・Household実行script・実prompt.txt・実audit JSON存在確認に基づく。推測箇所は明示的に「SSOT上で特定不可」と記載した。
- **費用**: ¥0(API呼び出しなし、既存ファイルの読み取り・grep・突き合わせのみ)。
- **納期**: 単一セッション内で完了(2026-09-10)。

## 成果物一覧

- `FAMILY-A-DISCOVERY-SPEC-FINALIZATION-RECONCILE-01_REPORT.md`(本ファイル、root直下、新規)

読み取りのみで参照した既存ファイル(いずれも変更していない): `CURRENT_SPEC.md`、`OPEN_ITEMS.md`、`DECISION_LOG.md`、`ARTIFACT_REGISTRY.md`、`HOUSEHOLD-UNIFIED-FINAL-CANDIDATE-01_REPORT.md`、`FAMILY-A-DISCOVERY-STAGE4-CAUTIONARY-LANGUAGE-TRIAL-10_REPORT.md`、`er011_household_unified_final_candidate_01_run.py`、`er011_output/household_unified_final_candidate_01/{a2,b1b}/audit/prompt.txt`、`er011_output/household_unified_final_candidate_01/a2/audit/point_value_qa_attempt{0,1}.json`。
