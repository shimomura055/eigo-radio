# VALIDATED_TRIAGE_01(FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01 委任_01、2026-10-16、SSOT整理のみ・JPY0)

根拠: ユーザー2026-10-16指示§7(原文「過去の未決Trialは以下に分類してSSOTへ記録する。A：VALIDATEDだが正式採否未決／B：後続の承認済み仕様に吸収・代替済み／C：不成立・不採用・未検証。今回、ユーザーは個別の採否判断を行わないと明示した。したがって、Aはdeferredとして管理し、今回のProduction作業を妨げない。ただし、勝手に採用・不採用へ変更しない。Bは後続仕様との関係と根拠を記録する。CはVALIDATEDと誤記しない。この整理のための追加Trial・個別質問は禁止。」)。対象=FXWA(`AUDIT_REPORT_01.md`)§3(9行)・§15(S1〜S14)・`PART_B_TRIAL_MATRIX_01.md`§2(R01〜R45)の**未決**Trial/仕様。

**分類の運用(本書の定義)**: 「VALIDATED」はTrial判定欄(PB §2)が`V`またはOI区分が`PRE_USER_VALIDATION`(ユーザー検証待ち)で結果が肯定的なものだけに使う。UDR/CONDITIONAL/M(測定のみ)/NS/Rのものは**VALIDATEDと呼ばない**(C)。採用・不採用への変更は一切しない(A=deferred)。FXWAの「独立改善候補A〜C」とは別体系である点に注意(本書のA/B/CはユーザーのA/B/C)。

## 1. 集計

| 分類 | 件数 | 内訳 |
|---|---|---|
| **A** VALIDATEDだが採否未決 → **deferred(2026-10-16ユーザー指示§7)** | 3 | A1 OPEN-56/59、A2 OPEN-243 M1(b)、A3 OPEN-316(c) |
| **B** 後続の承認済み仕様に吸収・代替済み | 12 | R02、R06、R08、R15、R25、R26、R27、R28、R29、R30、R33、R36 |
| **C** 不成立・不採用・未検証(VALIDATEDではない) | 11 | R03、R05、R07、R19、R21、R22、R23、R24(M2/M3)、R32、R40、R41 |
| 対象外(決着済み・配線済み・OI/配線案件) | 末尾§5 | 分類不要 |

## 2. A: VALIDATEDだが正式採否未決(deferred、今回のProduction作業を妨げない)

| # | Trial名 | 管理ID | VALIDATED根拠 | 分類 | OPEN | 備考 |
|---|---|---|---|---|---|---|
| A1 | Evidence Compression(聞かせる部分のEvidence detail圧縮、B版) | `ER-007-SPOKEN-EVIDENCE-DENSITY-AB-01`(2026-08-24)、`ER-007-EVIDENCE-WORDCOUNT-JA-ASR-EFFECTIVENESS-AUDIT-01` | B版でFact Check FAIL 0・Ledger外claim 0(FXWA §15 S4)。OI区分`PRE_USER_VALIDATION`・ステータス`A/B READY FOR USER LISTENING`(OI:230)。ユーザーの採否(全面/一部/再調整/現状維持)は未提示 | **A: deferred(2026-10-16ユーザー指示§7)** | OPEN-56(OI:230)、OPEN-59(OI:234) | 対象は旧B1/A2 Writer Prompt。Family XのW-1/R0は別構造のため直接のProductionギャップではない。**採用・不採用へ変更しない** |
| A2 | OPEN-243 M1(b)(翻訳段の事実NG対策: 要約MAJOR前回指摘解消) | `OPEN-243-TRANSLATION-NG-ANALYSIS-01`(2026-10-08、M1/M2/M3) | M1=要約MAJOR14世代の前回指摘解消14/14(従来6/14)・要約STOP相当8→2(OI:745)。M1(a)のみAdvanced限定で2026-10-10採用済み(DL:20530(6)、`EFAM:327`)。(b)以降は採否未判断 | **A: deferred** | OPEN-243(OI:745) | 「現行の守り」(EN deviation check等)の撤去はRF配線の帰結(CS:1182)。M2/M3は下記C11。**closeしない** |
| A3 | Comment4 B1(Advanced)側への「最後に」2文の展開 | `COMMENT4-SHORT-BRIDGE-RETRIAL-02`/`MINIMAL-PROMPT-TRIAL-03`/`STD-COMMENT4-BRIDGE-PROMPT-TRIAL-01`(2026-10-12) | Std側はユーザー決定A(CS:2677)で`AFP`・配線済み(`AP:221-238`)。B1(Advanced)側の展開はOPEN-316(c)で未決(意図的、FXWA §2 #10) | **A: deferred** | OPEN-316(OI:819) | Comment4はIOL文数に依存しない(「1文とは限りません」、FXWA §14-2 #3)ため本作業を妨げない |

## 3. B: 後続の承認済み仕様に吸収・代替済み

| # | Trial名 | 管理ID | VALIDATED/判定の根拠 | 分類 | 吸収先仕様と根拠 | OPEN |
|---|---|---|---|---|---|---|
| B1 | B3 Diversity/Advanced Retry Root Cause | `NEWS-FAMILY-X-B3-DIVERSITY-TRIAL-01`/`B3-ADVANCED-RETRY-ROOTCAUSE-01`(2026-09-26) | small_bag・meta=V、hormuz=NOT_COMPLETED。PB R02 | **B** | `NEWS-FAMILY-X-B3-FACT-SELECTION-PRODUCTION-WIRING-01`(R01、`PW`)に吸収(DL:9645 X-2決着)。JA段Gate対策は2026-10-10に旧Checker撤去とともに撤去(PB R02/R39) | — |
| B2 | OPEN-237 台帳明確化(P') | `OPEN-233-LEDGER-CLARITY-DESIGN-01`/`LEDGER-CLARITY-P-TRIAL-01`(2026-10-06) | UDR(Fable)。HC-012型0・重大NG0・断定強化1件で保留(PB R06)=VALIDATEDではない | **B** | Writer誤読の上流対策という目的は、後続の承認済み**決定論B3 producer(notes_for_writerをassemblerが制約ブロックへ転記)+W-1 Fact Lock**で別方式により代替(`er053_b3_deterministic_producer_01.py:141`、OI:750 OPEN-248)。Researcher prompt側のP'規則は未配線のまま残る点を明記 | OPEN-237(OI:739) |
| B3 | Note転記マトリクス(META-ROLLBACK-MINIMAL-NOTE、META-ALLFACT-NOTE) | `META-ROLLBACK-MINIMAL-NOTE-TRIAL-01/02`、`META-ALLFACT-NOTE-ENT/E2E-TRIAL`(2026-10-07) | UDR/CONDITIONAL(PB R08)=VALIDATEDではない | **B** | 同上(B2)。Note転記は決定論assemblerで吸収 | OPEN-237 |
| B4 | News Hook Side output(R2後にLunaでHook1本) | `NEWS-HOOK-POLICY-DECISION-01`(2026-09-24)+`HOOK-MODEL-COMPARISON-01`/`R2-TO-HOOK-TRIAL-01` | 生成順のみV(PB R15)。Side outputはProduction未配線 | **B** | **2026-10-16ユーザー指示§2「Hook Side Output=廃止。R2 Titleを正式表示する仕様は維持」**に吸収(#98判断済み)。OPEN-176は行内追記のみ・closeは実装後 | OPEN-176(OI:357) |
| B5 | OPEN-233 Checker選別再分類 | `OPEN-233-CHECKER-SELECTIVITY-RECLASSIFY-01/02`ほか | V(PB R25)。`APPROVED_FOR_PRODUCTION`→SUPERSEDED(PWになったことは無い) | **B** | 2026-10-10ユーザー決定(DL:20530(8))=新方針(W-1+RF+Human Review、旧Fact Checker撤去)により**SUPERSEDED**。履歴保持 | OPEN-233(OI:416) |
| B6 | OPEN-233 Self-Recovery | `OPEN-233-SELF-RECOVERY-TRIAL-01`+`PRODUCTION-WIRING-01`(+CORRECTION-01/02) | V(条件付き)(PB R26) | **B** | 同上(B5) | OPEN-233 |
| B7 | OPEN-233 KPI Recovery Redesign | `OPEN-233-KPI-RECOVERY-REDESIGN-02`、`STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01`ほか | UDR→SUPERSEDED(PB R27) | **B** | 同上(B5) | OPEN-233 |
| B8 | OPEN-238 Precheck偽陽性修正 | `OPEN-238-PRECHECK-FALSE-POSITIVE-FIX-TRIAL-01`/`PRODUCTION-WIRING-01` | V、Self-Recovery flow runnerに対して`PW`(PB R28) | **B** | このflow自体が2026-10-10にSUPERSEDED。Family X Production到達経路なし(FXWA §4 #1) | OPEN-238(OI:740) |
| B9 | ALL-6-LUNA Writer再設計必要性 | `ALL-6-LUNA-WRITER-REDESIGN-NECESSITY-TRIAL-01`+`PRODUCTION-MODEL-ROUTING-GPT6-WIRING-01` | M(測定、PB R29) | **B** | 判断7(DL:20263)=Luna方針+2026-10-11 E案(JA B3/R0/R1/R2=gpt-6.1-sol、`PW`)に吸収。英語化モデルの個別比較は未実施(FXWA §14-5 独立改善候補。UDRにしない) | OPEN-241(OI:743) |
| B10 | WRITER-R0-MODEL-IMPACT | `WRITER-R0-MODEL-IMPACT-TRIAL-01/-FIX01/-FIX02`(PB R30) | UDR(DL)。OIに該当行0件 | **B** | E案(DL:20573、`FAMILY-X-JA-MODEL-ALLOCATION-SOL61-PRODUCTION-WIRING-01`)で実質置換。吸収の明示記録がなかった点を本書で補う | — |
| B11 | FACTLOCK-ASTRA-E2E-TRIAL-01 単体 | 同左(PB R33) | G2完走、Fable判定UDR(DL:20429) | **B** | W-1採用(DL:20532、`PW`)に吸収。Trial単体の採否回答は不要 | — |
| B12 | TRANSLATION-SEGMENTATION-NO-HEADING Trial v1(忠実英訳) | `TRANSLATION-SEGMENTATION-NO-HEADING-TRIAL-01`→`FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01`(PB R36) | UDR(Trial)。must-fix retryで解決する前提 | **B** | 同前提のretryは2026-10-10の旧Checker撤去で撤去。Fact精度は後続のRF+Human Reviewに吸収(OI:412注記候補) | OPEN-230(OI:412) |

## 4. C: 不成立・不採用・未検証(VALIDATEDではない)

| # | Trial名 | 管理ID | 状態と理由 | 分類 | OPEN |
|---|---|---|---|---|---|
| C1 | brief構造(V1/V3/V5/V6) | `OPEN-233-B3-BRIEF-STRUCTURE-TRIAL-01`(PB R03) | 重大NGは全条件0件(床効果)、逆方向対照V6が悪化せず操作確認不成立。Fable判定`NOT_SUPPORTED` | **C** | — |
| C2 | B3注記自動化(Lane B) | `B3-ANNOTATION-AUTOMATION-TRIAL-01`(PB R05) | `REJECTED`(ユーザー最終判断) | **C** | — |
| C3 | 多義語Note自動生成 | `OPEN-233-LEDGER-POLYSEMY-NOTE-DESIGN-01`/`TRIAL-02/03/04`(PB R07)+`CONTROL-CHECKER-POLYSEMY-PRODUCTION-PATH-TRIAL-01` | TRIAL-03で自動生成不成立、Rollback誤読0/22・曖昧→正の改善なし(CONDITIONAL)、N小で採否不能。「Note系Trial群は本Trialで上書き[SUPERSEDED/DEFERRED]」(OI:739)=VALIDATEDではない | **C** | OPEN-237 |
| C4 | エンタメ性の代理指標v1 | `docs/pm/stage0_01/narrative_elements_v1.md`(PB R19) | 暫定・未承認・Trialでの使用は未確認。参照するコード/運用手順なし | **C** | — |
| C5 | OPEN-220 固有名詞抑制がJA段のみ | `FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-01/02`のOPEN-220(PB R21) | M。Advanced側拡張の要否は未検証。既存の`DEFERRED`(ユーザー明示defer)を維持=今回変更しない | **C** | OPEN-220(OI:403) |
| C6 | OPEN-233 DIRECTIONAL-MISREAD-SAFETY | `OPEN-233-DIRECTIONAL-MISREAD-SAFETY-DESIGN-01`/`TRIAL-01/02/03`(PB R22) | TRIAL-03=`REJECTED`。設計はOPEN-233系のSUPERSEDED整理に包含 | **C** | OPEN-233 |
| C7 | OPEN-233 DANGER-SENTENCE-RELATION-CHECK系 | `...STAGE0-01`/`T1`/`T3`/`T4`/`CHECKER-ACTION-POLICY`(PB R23) | 機械適用FAIL。結果がDL/LED/OIにほぼ未記録(SSOT記録は開発側是正) | **C** | OPEN-233 |
| C8 | OPEN-243 M2/M3 | `OPEN-243-TRANSLATION-NG-ANALYSIS-01`のM2/M3(PB R24) | M2=陽性26のtranslation判定 旧7→新6・重大EV-25は旧新とも未検出。M3=EV-25を渡してBLOCKING 1/3回。結果が決定的でない(測定のみ、採否未判断)=VALIDATEDではない | **C** | OPEN-243(OI:745) |
| C9 | WRITER-EVAL-DUAL-LLM-METHOD | `WRITER-EVAL-DUAL-LLM-METHOD-TRIAL-01`(PB R32) | `REJECTED`(Fable最終判定) | **C** | — |
| C10 | POST-EN Human Pre-sorter Blind | `POST-EN-HUMAN-PRE-SORTER-BLIND-TRIAL-01`(PB R40) | GPT系3モデルのみ、Anthropic 3モデルは鍵なしで未実行(未検証)。Production配線しない旨はユーザー明言(`2026-10-10_RISK-FLAGGER-PRODUCTION-WIRING-01_01.md:4`) | **C** | — |
| C11 | RF新仕様候補(a)台帳にない定量・事実の挿入検出、(b)確信度閾値による可変件数、(c)D2ベース+疑義時のみ専用呼出 | (PB R41) | 候補のみ・未実装・未検証。OI/REGに行なし | **C** | — |

## 5. 対象外(分類しない: 既に決着・配線済み・OI/配線案件)

- 配線済み(`PW`): R01、R04(`B3-FACT-INSTRUCTION-SEPARATION-ROOTFIX`、2026-10-11)、R10/R39(Risk Flagger)、R11/R12/R14(W-1・Sol統一)、R13/R42(旧Fact Checker撤去済み)、R17(AN3)、R18/R31(E案)、R34/R35(Std/Adv語彙)、R38。
- ユーザー決定済み: R16(Task B REJECTED・AN3採用)、R20(AN3第1文置換=承認Trialと同一[FXWA §14-2 #6])、R44(最新モデル原則)、KP選定A/B/C(2026-10-13、2026-10-16でA採用)、P7(OPEN-393→2026-10-16採用)、P8(`STANDARD-KP-JA-TTS-STYLE-TRIAL-02`→2026-10-16採用)、PD06/K2/E1/R2(2026-10-16採用)。
- 分析のみ・OI整理: R09、R43(OPEN-183/174/175の確認待ち)、R45(09:00判断記録)。

## 6. SSOT反映計画(本委任で実施・追記のみ)

- `OPEN_ITEMS.md`行内追記(既存記述・Statusタグは不変): OPEN-56/59/243(A: deferred、OPEN-243のM2/M3はC)、OPEN-316(A: B1展開deferred)、OPEN-237(B/C: VALIDATEDではない・吸収先)、OPEN-220(C)、OPEN-176(Hook廃止)。それ以外のB/C項目は`OPEN_ITEMS.md`に独立行が無い(PB R05/R30/R32/R33/R40/R41/R19等)ため、本書と`DECISION_LOG.md`の委任_01エントリで記録する。
- `DECISION_LOG.md`末尾: A=3/B=12/C=11の一覧参照を追記。
- 採用・不採用・close・Status変更は行わない。
