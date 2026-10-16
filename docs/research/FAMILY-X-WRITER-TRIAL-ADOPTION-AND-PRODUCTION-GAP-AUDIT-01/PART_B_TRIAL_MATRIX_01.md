# PART_B_TRIAL_MATRIX_01(FAMILY-X-WRITER-TRIAL-ADOPTION-AND-PRODUCTION-GAP-AUDIT-01 委任_01B、2026-10-16、read-only・JPY0)

到達Status: `PART_B_COMPLETE`(§5の未確認事項を除く)。Git操作・有料API・Production変更・SSOT編集は一切なし。作成物は本書・`docs/pm/RESULT_PACKET_FXWA1B.md`・委任文保存のみ。

**略記**: DL=`DECISION_LOG.md`、OI=`OPEN_ITEMS.md`、CS=`CURRENT_SPEC.md`、REG=`docs/pm/USER_DECISION_REGISTER_01.md`、LED=`docs/pm/REPORT_LEDGER.md`。[FC]=Fable確認要。
**09:00決定記録**=`docs/pm/delegation_log/2026-10-16_FAMILY-X-20261016-0900-USER-DECISION-RECORD-01_USER.md`(ユーザー原文、以下「09:00記録」)。CS:1202〜1247とDL:21631に並行workerが反映中(いずれも未commit)。

**方法上の注意**
- OI/REGに載っていること自体を「ユーザー保留の証拠」として扱っていない。「ユーザー判断」欄はDL等の「ユーザー決定」記述の行番号を出典にした。DLの記述の多くは「逐語」または「逐語要旨」であり、チャット原文そのものはRepo外にある。ユーザー原文がRepoに保存されているものは(09:00記録、`..._USER.md`)原文を優先した。Repoに該当記述が見つからないものは「判断証拠なし」。
- 「Production実装」欄は、私が直接Grep/Readで確認できたfile:lineのみ記載。それ以外は「未確認(Part Cで照合)」。
- **行番号の変動**: 監査中に並行workerがCS(+約50行、CS:1202付近とCS:2669付近)・DL・OIを未commitで編集していた。CS:1202以降の旧行番号は+46〜+53ずれる。本書は読了時点(2026-10-16 09:3x JST)の行番号。DL/OIの行番号も同様に変動しうる。

---------------------------------------------------------------------
## §1 対象Trial/仕様の一覧(ユーザー指示§3の14項目への対応付け)

行ID(R01…)は§2のマトリクス行。

### (1) B3 Storyline／Fact Selection／Brief構造改善
- R01 `NEWS-FAMILY-X-B3-FACT-SELECTION-PRODUCTION-WIRING-01`(2026-09-26、DL:9596付近・CS:829)
- R02 `NEWS-FAMILY-X-B3-DIVERSITY-TRIAL-01`/`NEWS-FAMILY-X-B3-ADVANCED-RETRY-ROOTCAUSE-01`(2026-09-26、DL:9660)
- R03 `OPEN-233-B3-BRIEF-STRUCTURE-TRIAL-01`(2026-10-07、DL:20227)
- R04 `B3-FACT-INSTRUCTION-SEPARATION-ROOTFIX-TRIAL-01/02`(2026-10-10、DL:20535〜20544、OI:750)
- R05 `B3-ANNOTATION-AUTOMATION-TRIAL-01`(Lane B、2026-10-10、DL:20532・20534)

### (2) Fact台帳・notes_for_writer・Writerへの情報引き渡し
- R06 `OPEN-233-LEDGER-CLARITY-DESIGN-01`/`LEDGER-CLARITY-P-TRIAL-01`(OPEN-237、2026-10-06、DL:20128・20135)
- R07 `OPEN-233-LEDGER-POLYSEMY-NOTE-DESIGN-01`/`TRIAL-02/03/04`(2026-10-06〜07、DL:20145・20157・20164)
- R08 `META-ROLLBACK-MINIMAL-NOTE-TRIAL-01/02`・`META-ALLFACT-NOTE-ENT-TRIAL-01`・`META-ALLFACT-NOTE-E2E-TRIAL-02`・`NOTE-TRANSFER-MATRIX-TRIAL-01`・`CONTROL-CHECKER-POLYSEMY-PRODUCTION-PATH-TRIAL-01`(2026-10-07、DL:20173〜20243)
- R09 `E2E-STAGEWISE-NG-AUDIT-01`・`NG-ROOT-CAUSE-ANALYSIS-01`(2026-10-07、分析のみ、DL:20199・20234)

### (3) B3 deterministic producer・Fact Lock入力契約
- R10 `RISK-FLAGGER-PRODUCTION-WIRING-01` Lane A(決定論B3 producer D-det v2+assembler、注記済みB3入力契約V1〜V10、U-1/U-2)(2026-10-10〜11、DL:20530・20544・20550、OI:746・749、CS:1165・1186)

### (4) W-1 R0 Writer Prompt
- R11 `FACTLOCK-WRITER-REDESIGN-TRIAL-01`(2026-10-08、DL:20297〜20347)
- R12 W-1正式採用(`RISK-FLAGGER-PRODUCTION-WIRING-01` 委任_04)(2026-10-10、DL:20530)

### (5) R1／R2 Entertainment Revision
- R13 `NEWS-ITERATIVE-ENTERTAINMENT-TRIAL-01/02`+`NEWS-ITERATIVE-R2-PRODUCTION-WIRING-01`(2026-09-24、DL:9372・9380、CS:829)
- R14 `FACTLOCK-WRITER-REDESIGN-TRIAL-01` ASTRA-REVISE-MATRIX-01/02(R1/R2のAstra化・系列X)(2026-10-08、DL:20332・20340・20349)
- R15 `NEWS-HOOK-POLICY-DECISION-01`(R2完成後のLuna Side output Hook)(2026-09-24、DL:9415、OI:357)

### (6) Writerの具体性・自然さ・エンターテイメント性改善
- R16 `FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-01`(Task A/B/C)(2026-09-28、DL:11854)
- R17 `FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-02`(2026-09-28、DL:11969)
- R18 `FAMILY-X-JA-ARTICLE-QUALITY-MODEL-ALLOCATION-TRIAL-01`+OPEN-255(META記事の面白さ低下懸念)(2026-10-11、DL:20571、OI:757)
- R19 エンタメ性の代理指標v1(`docs/pm/stage0_01/narrative_elements_v1.md`、2026-10-07、DL:20245(d))

### (7) AN3 Concreteness Control
- R20 `FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01`(2026-09-28〜29、DL:12138・12424、CS:886〜957)
- R21 OPEN-220(固有名詞抑制がJA段のみで英語へ伝播しない)(2026-09-28、OI:403)

### (8) Fact誤読・意味反転・曖昧表現対策(OPEN-233関連)
- R22 `OPEN-233-DIRECTIONAL-MISREAD-SAFETY-DESIGN-01`/`TRIAL-01/02/03`/`OPUS-REVIEW-03`(2026-10-06、DL:20076〜20127、OI:728)
- R23 `OPEN-233-DANGER-SENTENCE-RELATION-CHECK-STAGE0-01`(DL:20245)+T1`REVERSAL-DETECT-HUMAN-ROUTE-TRIAL-01`・T3`SENTENCE-FACT-LINK-PRECISION-TRIAL-01`・T4`PAIRWISE-JUDGE-MODEL-TRIAL-01`・`CHECKER-ACTION-POLICY-DESIGN-01`/`STAGE2-01`(2026-10-07〜08)
- R24 `OPEN-243-TRANSLATION-NG-ANALYSIS-01`(翻訳段NG・M1/M2/M3)(2026-10-08、DL:20349・20358、OI:745)
- R25 `OPEN-233-CHECKER-SELECTIVITY-RECLASSIFY-01/02`・`FLOOR-SELECTIVITY-OPTIMIZATION-01`・`CHECKER-FLOOR-PRODUCTION-E2E-01`(2026-10-06、DL:19967〜20051、OI:726・727)

### (9) Self Recovery・Rewrite改善
- R26 `OPEN-233-SELF-RECOVERY-TRIAL-01`(委任_01〜_60番台、約140エントリ)+`OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01`(+CORRECTION-01/02)(2026-09-30〜10-05、DL:13286〜19420・18820、CS:2462・2501・2519・2536)
- R27 `OPEN-233-KPI-RECOVERY-REDESIGN-02`・`OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01`・`E2E-ACCEPTANCE-01`(2026-10-04〜06、DL:18551・19426・19825、OI:729・732)
- 注: TTS側のLocal Rewrite(`OPEN-256`等)は「Writer」範囲外(本Partでは扱わない)。

### (10) Precheck誤検出対策(OPEN-238)
- R28 `OPEN-238-PRECHECK-FALSE-POSITIVE-FIX-TRIAL-01`/`PRODUCTION-WIRING-01`/`PRECHECK-MISLINK-DIAG-01`(2026-10-07、DL:20211〜20226、OI:740)

### (11) Writerモデル配置・Luna／Astra／Sol比較
- R29 `ALL-6-LUNA-WRITER-REDESIGN-NECESSITY-TRIAL-01`+`PRODUCTION-MODEL-ROUTING-GPT6-WIRING-01`(OPEN-241)(2026-10-08、DL:20252・20259〜20296、OI:743)
- R30 `WRITER-R0-MODEL-IMPACT-TRIAL-01`/`-FIX01`/`-FIX02`(2026-10-10、DL:20476〜20491)
- R31 `FAMILY-X-JA-ARTICLE-QUALITY-MODEL-ALLOCATION-TRIAL-01`→`FAMILY-X-JA-MODEL-ALLOCATION-SOL61-PRODUCTION-WIRING-01`(E案)(2026-10-11、DL:20571・20574、CS:1157・1159)
- R32 `WRITER-EVAL-DUAL-LLM-METHOD-TRIAL-01`(評価者構成)(2026-10-09、DL:20435・20441)
- (参考)Family Z側`FAMILY-Z-STORY-QUALITY-MODEL-COMPARISON-TRIAL-01`/`FAMILY-Z-MELOS-SOL-B3Z-COMPARISON-TRIAL-01`はFamily Zのため本表の対象外(存在のみ記録)。

### (12) Fact Lock／Astra E2E Trial
- R33 `FACTLOCK-ASTRA-E2E-TRIAL-01`(2026-10-09、委任_01〜_16、DL:20367〜20434)

### (13) 英語Advanced生成・Standard難易度調整
- R34 `NEWS-STANDARD-A2-PROMPT-V2-TRIAL-01`〜`NEWS-STANDARD-A2-VOCAB-6000-CUTOFF-TRIAL-01`/`-PRODUCTION-WIRING-01`+`NEWS-VOCAB-LEVEL-PRODUCTION-WIRING-01`(2026-09-24〜27、DL:9432・9449・9468・9645、CS:831)
- R35 `ADVANCED-VOCAB-V2-PRODUCTION-RESTORE-01`/`NEWS-ADVANCED-A2-PRODUCTION-E2E-WIRING-01`(2026-09-25〜26、DL:9557・9468、CS:830)
- R36 `FAMILY-X-TRANSLATION-SEGMENTATION-NO-HEADING-TRIAL-01`→`FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01`(新記事構造・忠実英訳)(2026-09-28〜29、DL:12475・12517・12718、CS:1371)
- R37 In One Line(M1(a)と文数仕様)(DL:20530(6)、2026-10-15 Coffee監査、`er071_output/m2p0_n01_production_wiring_01/coffee_spec_completeness_audit_01/AUDIT_REPORT_01.md` §4、09:00記録)

### (14) Writer品質評価・QA・Risk Flaggerへの連携
- R38 `WRITER-DEV-RISK-FLAGGER-DESIGN-01`/`ANTENNA-TRIAL-01`/`POST-EN-TRIAL-01`/`WRITER-RISK-FLAGGER-A4-DUALMODEL-OR-TRIAL-01`/`META-ROLLBACK-CROSSMODEL-01`/`META-ROLLBACK-CHECK-01`(2026-10-09〜10、DL:20459〜20515・20525〜20531)
- R39 `RISK-FLAGGER-PRODUCTION-WIRING-01`(RF 4条件+Review Queue+旧Fact Checker撤去)(2026-10-10〜11、DL:20530〜20560、CS:1155〜1200)
- R40 `POST-EN-HUMAN-PRE-SORTER-BLIND-TRIAL-01`(2026-10-10、DL:20515・20518)
- R41 RFの新仕様候補(a)(b)(c)・確信度閾値(DL:20465・20471・20495・20512)

### 上記14項目に当てはまらず拾ったもの
- R42 `NEWS-FAMILY-X-JA-FACT-CHECK-PRODUCTION-WIRING-01`(JA段Fact Check、2026-09-27、DL:9726、CS:829末尾)→2026-10-10に撤去(R39に包含)
- R43 OPEN-183(旧Meta記事のユーザー確認待ち、OI:364)・OPEN-174/175(素材混入・冒頭復唱の監視、OI:355・356)
- R44 `PM-DEV-EVAL-LATEST-MODEL-RULE-01`(評価モデル原則、DL:20450、PM運用)
- R45 2026-10-16 09:00 最終ユーザー判断(`FAMILY-X-20261016-0900-USER-DECISION-RECORD-01`、DL:21631、CS:1202〜1247)—§4で扱う

### 該当Trialなし(探索範囲)
- 「Writerの自然さ」を独立に検証したTrial: **該当Trialなし**(探索範囲: DL見出し・LEDGER・delegation_logのファイル名[2026-09-27〜10-16]・OI Grep「自然」「Entertainment」「面白」)。自然さ・面白さはR13、R18、R19に分散。
- Self-Recovery配下のWriter再生成(Rewrite)専用の個別Trial: R26に含まれ独立IDなし。

---------------------------------------------------------------------
## §2 11項目判定マトリクス(1行1Trial/仕様)

凡例(Trial判定): V=VALIDATED、R=REJECTED、UDR=USER_DECISION_REQUIRED、M=MEASURED(判定語なし)、NS=NOT_SUPPORTED(Fable判定)。

| 行 | 管理ID | 目的 | Trial結果 | Trial判定 | ユーザー判断(出典) | 正式仕様 | Production実装(初回/retry/fallback/regen) | runtime evidence | 現在Status | 問題 | 必要対応 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R01 | NEWS-FAMILY-X-B3-FACT-SELECTION-PRODUCTION-WIRING-01 | Storylineを人手指定せずAIが決定→B3 4テスト→Selected Fact Brief | Meta runtime evidence(15 Fact中3採用)、Gate3 24/24 | (配線案件) | 正式決定: DL:9596付近(「ユーザー確定事項(逐語ベース要旨)」)。X-2は仕様変更しない: DL:9645項3 | CS:829(追記)・CS:1165 | 初回: `er019_family_x_entertainment_production_runner_01.py:147`(`run_storyline_b3`)、`er019_family_x_storyline_b3_fact_selection_01.py:209`。モデル=`FAMILY_X_STORYLINE_B3`(gpt-6.1-sol: `er006_model_routing_contract_01.py:134`、runner:151-153)。retry/fallback/regen: 未確認(Part C) | あり(`er019_output/family_x_b3_production_wiring_01/run_01/`) | PRODUCTION_WIRED(2026-09-26、CS:829。2026-10-11 Sol化後もPRODUCTION_WIRED) | 問題なし | 対応不要 |
| R02 | B3-DIVERSITY-TRIAL-01 / B3-ADVANCED-RETRY-ROOTCAUSE-01 | B3の汎化確認と、英訳段retryで直らないMAJORの原因 | small_bag・meta=V、hormuz=NOT_COMPLETED(Advanced段Gate STOP)。逸脱はJA Writer段で発生(英訳段retryでは構造的に解消不可) | V(2件)/NOT_COMPLETED(1件) | X-2決着: DL:9645。Diversity個別結果の採否: 判断証拠なし(Fable評価のみ: DL:9660) | CS:829 | R01に吸収。root cause対策(JA段Gate)はR42で配線後、2026-10-10に撤去(R39) | Trial | R01に吸収 | 問題なし | 対応不要 |
| R03 | OPEN-233-B3-BRIEF-STRUCTURE-TRIAL-01 | brief構造(V1/V3/V5/V6)で誤読NGを減らす | 55記事で重大NGは全条件0件(床効果)。軽微差は評価者差と同程度。逆方向対照V6が悪化せず操作確認不成立 | NS(Fable) | DL:20227(c)「段階2再開=YES」のみ。brief構造の採否に関するユーザー決定: 判断証拠なし(Fableが「Production採用候補にしない」と判定: DL:20227(a)) | なし | なし | Trial | NOT_SUPPORTED | 問題なし | 対応不要 |
| R04 | B3-FACT-INSTRUCTION-SEPARATION-ROOTFIX-TRIAL-01/02 | B3 Selected FactsにFact/指示/制約が混在する根本解消 | 案D(決定論assemble+制約ブロック別連結)でFact側命令文0。D-det v2(単位換算)=V。D-plus/Sep=R。役割宣言のみ=V(不採用) | V(案D, D-det v2)/R | DL:20538「案D採用」、DL:20544「ユーザー最終決定(ROOTFIX最終仕様)」=D-det v2+決定論assembler=APPROVED_FOR_PRODUCTION、役割宣言=不採用、周辺数値Gate化=新仕様化しない | CS:1165(経路図) | 初回: `er053_b3_deterministic_producer_01.py:843`(`produce_annotated_b3`)を`er019…runner:200`(`run_annotation_producer`)が呼ぶ。「初回/regeneration/resume/再利用の全分岐を通る」はCS:1165の記載(コード照合は未確認、Part C) | あり(L3 coffee_prices run_l3_01、`er053_output/risk_flagger_production_wiring_01/completion_matrix_01.md`) | PRODUCTION_WIRED(2026-10-11) | OI:750の見出しStatus(「Production採用はUSER_DECISION_REQUIRED」)が古いまま(本文は最終決定を追記済み) | 開発側是正(OI見出し)[FC] |
| R05 | B3-ANNOTATION-AUTOMATION-TRIAL-01(Lane B) | Sonnetでの注記自動化 | 約JPY15.7/記事 | R(ユーザー最終決定) | DL:20544「Lane B=REJECTED・superseded by D-det v2・クローズ」 | なし | なし | Trial | REJECTED・クローズ | 問題なし | 対応不要 |
| R06 | OPEN-233-LEDGER-CLARITY-DESIGN-01 / P-TRIAL-01(OPEN-237) | Writerが誤解しやすい台帳表現を上流で明確化 | P'Trial(JPY34.85): HC-012型0、真の重大NG0、断定強化1件で保留。判断事項5点 | UDR(Fable) | 判断証拠なし(DL:20135(e)は「判断待ち」の列挙のみ。回答の記録なし)。OI:739の最終更新は2026-10-07でUDRのまま | なし | なし(P'規則がResearcher promptに入っているかは未確認、Part C) | Trial | USER_DECISION_REQUIRED | A: 判断漏れ。2026-10-08のFact Lock再設計後に再整理した記録なし | ユーザー判断[FC] |
| R07 | OPEN-233-LEDGER-POLYSEMY-NOTE-DESIGN-01 / TRIAL-02/03/04 | 多義語notes(逆になる表現)を最小変更で台帳に入れる | 自動Note生成は3ループで不成立。推奨=既存notes昇格+B3転記 | UDR | 判断証拠なし(DL:20164(d)は選択肢提示のみ) | なし | notes_for_writer自体はR04のassemblerが制約ブロックへ転記(OI:750)。多義語Note供給源は未設計(OI:739) | Trial | USER_DECISION_REQUIRED。Note系を「上書き[SUPERSEDED/DEFERRED]」とするOI:739の記載はFable記載でユーザー決定の逐語は見つからない | A: 判断漏れ+記録欠落 | ユーザー判断(R06とまとめて)[FC] |
| R08 | META-ROLLBACK-MINIMAL-NOTE-TRIAL-01/02、META-ALLFACT-NOTE-ENT/E2E-TRIAL、NOTE-TRANSFER-MATRIX-TRIAL-01、CONTROL-CHECKER-POLYSEMY-PRODUCTION-PATH-TRIAL-01 | Note注意喚起で誤読を予防 | Rollback誤読0/22。曖昧→正の改善なし。N小で採否不能。CONTROL…=CONDITIONAL | UDR/CONDITIONAL | 判断証拠なし(DL:20173〜20243は「Trial実施承認」と「Status判定」のみ) | なし | なし | Trial | USER_DECISION_REQUIRED/CONDITIONAL | A: 判断漏れ(R07と同根) | R07と合わせて判断[FC] |
| R09 | E2E-STAGEWISE-NG-AUDIT-01 / NG-ROOT-CAUSE-ANALYSIS-01 | NG多発の原因が測定手順差か否か | 最大の説明は測定手順一式の差。「前回評価が過大」とは結論しない | (分析) | DL:20234「RCA結論採用(Fable判定+ユーザー報告済み)」。ユーザー採否の逐語: 判断証拠なし | なし | なし | 既存データ再評価 | 分析完了 | 問題なし | 対応不要 |
| R10 | RISK-FLAGGER-PRODUCTION-WIRING-01 Lane A(決定論B3 producer+契約V1〜V10+U-1/U-2) | 注記済みB3を決定論生成しFact Lock Writerへ契約付きで渡す | L3 coffee_prices run_l3_01で通し確認。違反は課金前STOP | (配線案件) | DL:20530(委任_04 ユーザー確定事項15項目)・DL:20544・DL:20550(正式完了承認の逐語) | CS:1165・1186 | `er053_b3_deterministic_producer_01.py:843`、契約`er053_b3_annotation_contract_01.py`、`er019…runner:196-250`(U-1 `LegacyWriterProvenanceStop`) | あり(同上) | PRODUCTION_WIRED(2026-10-11) | 問題なし。OPEN-249/250(U-1相当の未実装部分)は継続OPEN(OI:751・752) | 対応不要 |
| R11 | FACTLOCK-WRITER-REDESIGN-TRIAL-01 | Writer根本設計(Fact Lock)でFact NGを下げる | v1 MEASURED(面白さNG[pairwise 9対35]のユーザー指摘→禁止誘導を最小化)。sweep評価: S0基準で明確に上0、下S6のみ、他ノイズ幅 | M | DL:20297(数値規則(c)・R1/R2は5則・名称内番号はA、sweep上限¥300等、逐語要旨) | CS:1169 | `er053_family_x_factlock_ja_writer_01.py:262-273`(`build_r0_prompt`)・`:281-`(R0単発、developer=`DEVELOPER_MESSAGE`、effort=high、previous_response_idなし)。harness欠陥「タグ除去漏れ(Production採用検討時に要修正)」(DL:20297)のProduction側対応は未確認(Part C) | あり | W-1としてPRODUCTION_WIRED | D: R20参照(AN3第1文の置換) | R20参照 |
| R12 | W-1正式採用(RISK-FLAGGER-PRODUCTION-WIRING-01 委任_04) | 注記版B3→Fact Lock R0→R1→R2を正式採用 | W-2/3/4は不採用 | (採用決定) | DL:20530(1)「新Writer=W-1を正式採用(APPROVED_FOR_PRODUCTION)」。また09:00記録§2「既存PRODUCTION_WIRED維持」 | CS:1155・1169 | R11と同じ。`run_w1_writer`=`er053…writer_01.py:318`。記号QA: R0は1回だけ再生成/R2はR2のみ1回再実行(`:355-431`) | あり | PRODUCTION_WIRED(2026-10-11) | D: CS:1169が古い(R0=Luna、R1/R2=Astra と記載。実体はSol: `er006…:137-138`)。見出しCS:1157・1159に更新注記はあるが当該bulletは未更新 | 開発側是正(SSOT整合)[FC] |
| R13 | NEWS-ITERATIVE-ENTERTAINMENT-TRIAL-01/02+NEWS-ITERATIVE-R2-PRODUCTION-WIRING-01 | Original→Entertainment revision→Further revision(R2)で面白さ向上 | 12記事比較、R2を標準、R3は標準に含めない | V→採用 | DL:9380「User正式承認(原文引用)」 | CS:829 | W-1が置換。`REVISION_INSTRUCTIONS`(r1/r2)は`er019_family_x_ja_writer_o_r1_r2_01.py`に逐語。実際のR1/R2は独立call・previous_response_idなし・R2入力=R1 raw・Sol(CS:1169、`er053…writer_01.py:42`) | あり | PRODUCTION_WIRED(2026-09-26)。ただし実装は別方式に置換済み | D: CS:829が現行実装と食い違う(model=gpt-5.6-luna、previous_response_id連鎖、JA Fact Check must-fix retryを現行として記述。CS:829内に"W-1"の語0件)。置換注記なし | 開発側是正(CS:829へ置換注記)[FC] |
| R14 | FACTLOCK-WRITER-REDESIGN-TRIAL-01 ASTRA-REVISE-MATRIX-01/02 | R1/R2のRevision方式(系列X=ユーザーPromptのみ) | 「Xの方がよく、R2が落としどころ」 | M→採用 | DL:20340・20349(iii)(ユーザー判定、系列X採用) | CS:1169 | R13と同じ | あり | PRODUCTION_WIRED(W-1に含む) | 問題なし | 対応不要 |
| R15 | NEWS-HOOK-POLICY-DECISION-01(+HOOK-MODEL-COMPARISON-01、R2-TO-HOOK-TRIAL-01) | R2完成後にLunaで比較観測用Hookを1本Side output生成 | 生成順「R2完成記事→Hook」=V。Sol/Terra=DEFERRED/HOLD | V(生成順) | DL:9415「ユーザー指示原文(要旨、項目別)」: 正式表示=R2 Title、R2後にLuna Hook1本Side output | OI:357(OPEN-176)。CSにSide output記載0件 | 未配線: `er019*`/`er012_e*`/`er053*`にSide output Hook実装0件(Grep)。OI:357が「Side output未配線」と自記 | なし | OPEN/MONITORING | B: ユーザー正式決定の未配線。現Family X runner(W-1以降)に該当stageなし | ユーザー判断(引継ぐか廃止か)+(引継ぐなら)開発側[FC] |
| R16 | FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-01 | 数字・時刻・固有名詞の過剰具体性の抑制(Task A初稿/B cleanup/C R1→R2改善) | A3(強)・B1(cleanup)でHormuz MAJOR。軽度Pattern・Task Cは無傷 | Task B=R、全体UDR | DL:11854(Fable判定)。Task A/Cの帰結: R17→AN3採用、Task C=reminder削除(据え置き: DL:12424)。Task B「REJECTED確定」のユーザー最終確認: 判断証拠なし | CS:886 | AN3として配線(R20) | あり | A→AN3、B→REJECTED、C→据え置き | 問題なし | 対応不要 |
| R17 | FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-02 | AN3(A3+N2)とAN2の比較 | 実本文で必要情報を残しつつ不要な具体性をより強く落とせた→AN3 | V | DL:12138(ユーザー正式決定)、CS:886(逐語思想) | CS:886〜957 | R20 | あり | AN3採用・AN2/T1不採用 | 問題なし | 対応不要 |
| R18 | FAMILY-X-JA-ARTICLE-QUALITY-MODEL-ALLOCATION-TRIAL-01+OPEN-255 | META記事のエンタメ性・品質低下懸念 | 3テーマN=1のBlind評価でE案(全段Sol)が最高グループ | V(Blind) | DL:20571「ユーザー決定(逐語)」E案正式採用(APPROVED_FOR_PRODUCTION) | CS:1157・1159、OI:757 | E案: `er006…:134-138`、`er053…writer_01.py:40-42`。E案マスター(`docs/quality/ja_quality_masters/`)を参照するコード: `ja_quality_masters`を含む.pyが0件(Grep) | あり(`er019_output/meta/run_sol61_01/`) | PRODUCTION_WIRED(2026-10-11、OI:757 Close) | F寄り: マスターは「品質回帰の第一基準」(DL:20571)とされたが運用手順・自動参照がRepoに見つからない | 開発側(運用手順化)[FC] |
| R19 | エンタメ性の代理指標v1(`docs/pm/stage0_01/narrative_elements_v1.md`) | 夜間自律ループでエンタメ性を代理指標で見る | 暫定・未承認 | (判定語なし) | DL:20245(d)「暫定・未承認」。承認の逐語: 判断証拠なし | なし | なし(計数script`docs/pm/stage0_01/narrative_count.py`のみ) | 既存データ | 暫定・未承認のまま | A: 未承認放置(以後のTrialでの使用は未確認) | ユーザー判断(廃止/正式化)または対応不要[FC] |
| R20 | FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01 | AN3 Promptを正式JA Writer経路へ配線 | sha 067030ff…がHormuz/Meta一致。回帰全PASS | (配線案件) | DL:12138(ユーザー正式決定)、DL:12424(R1/R2 reminder削除) | CS:886〜957 | `er019_family_x_ja_writer_o_r1_r2_01.py:99-132`(`build_original_prompt`で付与)。W-1 R0では`er053…writer_01.py:131-139`(`build_r0_block`)が第1文(数字・時刻の抑制)をFact Lock数字規則(5)で置換し、第2文(固有名詞)のみ逐語保持 | あり(Hormuz/Meta) | PRODUCTION_WIRED(2026-09-29)。W-1経路では第1文が置換済み | D: 仕様の上書き。CS:905は「AN3 blockはW-1 R0に含まれたまま有効(sha 067030ff…)」と記述。R0へ実際に入る文は第1文が別文。置換が「数値規則(c)」(DL:20297)の意図的採用かは、DL:20297の要旨からは確認できない | ユーザー判断(AN3第1文置換の追認)+開発側(CS:905訂正)[FC] |
| R21 | OPEN-220(固有名詞抑制がJA段のみ) | AN3の固有名詞方針を英語最終成果物まで反映 | 主因はカウント方式のアーティファクトで影響は当初想定より小さい可能性 | M | DL:12138「現行Advanced Prompt維持」(T0側)。Advanced側拡張の要否: OI:403では「ユーザー判断待ち(優先度低)」 | CS:886(「Advanced化Promptは一切変更しない」) | なし(意図的) | Trial | DEFERRED | C: 部分配線(JAのみ)。ユーザー思想「固有名詞も同様に」(CS:895付近)の英語伝播は未対応 | ユーザー判断(優先度低)[FC] |
| R22 | OPEN-233-DIRECTIONAL-MISREAD-SAFETY-DESIGN-01 / TRIAL-01/02/03 / OPUS-REVIEW-03 | 方向反転等の系統的読み違いを専用Safetyで検出 | TRIAL-03: HC-012 X1/3・Y0/3、A5-0 X1/3・Y0/3(TRIAL-02の3/3から退行)、D61 2/3 | TRIAL-01/02=UDR、-03=R | DL:20076〜20127は指示要点の記録(Trial実施承認)。TRIAL-03結果に対する判断: 判断証拠なし | なし | なし | Trial | REJECTED(-03)。設計はOPEN-233系の整理に包含(OI:728がSUPERSEDED整理行かは行内で未確認) | E: 結果と後続の位置づけが未記録 | 対応不要(SUPERSEDEDに包含)[FC] |
| R23 | OPEN-233-DANGER-SENTENCE-RELATION-CHECK-STAGE0-01 / T1 / T3 / T4 / CHECKER-ACTION-POLICY-STAGE2-01 | 危険文限定の関係検査・リンク精度・pairwise判定・Stage2方針 | T1 FAIL(`er052_output/open233_reversal_detect_01/T1_RESULT.md`)、T3 FAIL(`…link_precision_01/T3_RESULT.md`)、T4 A・B とも FAIL(`…pairwise_judge_01/T4_RESULT.md`)、Stage2 FAIL(`…open233_stage2_01/eval/STAGE2_RESULT.md:7`) | R(機械適用) | DL:20245「ユーザー決定1=(A)Opus推奨経路採用、決定2=段階0開始承認」(要旨)。T1/T3/T4/Stage2のFAILへの判断: 判断証拠なし | なし | なし | Trial | FAIL(machine) | E: SSOT記録欠落。DL/LED/OIに`ACTION-POLICY`・`STAGE0`・`REVERSAL-DETECT`・`PAIRWISE-JUDGE`・`SENTENCE-FACT-LINK`の語が0件(Grep、DLは`DANGER-SENTENCE`のみ1件) | 開発側(結果のSSOT記録、重要度低)[FC] |
| R24 | OPEN-243-TRANSLATION-NG-ANALYSIS-01(M1/M2/M3、OI:745) | 翻訳段(EN化)で生じる事実NGと検査の見逃し | M1(要約だけ再生成+JA/台帳入力)・M2(EN検査の主体定義拡張)・M3(再分類でchanged_actor保護)を既定OFFで実装 | M(Trial) | DL:20349(iii)(系列X)。DL:20367決定3「M2見送り(OFF維持)、M1・M3はON」(FACTLOCK-ASTRA-E2E設計、要旨) | なし | M1(a)(Advanced In One LineへJA R2+Ledger)のみProductionへ(`er012_e…two_level_runner_01.py:327` `_advanced_in_one_line`、`er003_v1_n3_01_advanced_adaptation_generate.py:593-611`)。M1の「要約だけ再生成」・M2・M3は旧Fact Checker/Checker撤去(2026-10-10)で消滅(`er053_dangling_reference_check_01.py:40`に`OPEN243_M1`等が撤去対象として登録) | あり(Trial E2E、L3) | OI:745は`OPEN`(2026-10-08記載のまま)。DL:20530(6)でM1(a)はAdvanced限定で正式維持 | E: OI:745の「現行の守り=6-luna EN検査の厳格化(OPEN-241)とO3観測(EN STOP率)」はEN deviation check撤去(CS:1182)で成立しない。残る守りはRFのみ。OI:745の(3)末尾要約文の付け足し・(4)複数形化・(5)訳語選択をRFが拾う想定かの記録なし | ユーザー判断(OPEN-243の継続/close。RFで守る範囲の確認)[FC] |
| R25 | OPEN-233-CHECKER-SELECTIVITY-RECLASSIFY-01/02、FLOOR-SELECTIVITY-OPTIMIZATION-01、CHECKER-FLOOR-PRODUCTION-E2E-01 | Checkerの選択性・floor誤爆(35件)の改善 | RECLASSIFY-02=V。E2Eは9/20 runで停止 | V | DL:20022「ユーザー決定2点(Checker新仕様正式採用/後段機械判定は数字のみ)をAPPROVED_FOR_PRODUCTIONとして記録(逐語)」 | CS:2536付近(OPEN-233節) | 配線されず。2026-10-10にユーザー決定でSUPERSEDED(OI:416・727・730・731、DL:20530(8)) | E2E 9/20 runで停止(DL:20022(g)) | APPROVED_FOR_PRODUCTION→SUPERSEDED(PRODUCTION_WIREDになったことはない) | D: CS:2462・2501・2519の見出し・Status行が「APPROVED_FOR_PRODUCTION」のまま。SUPERSEDED注記はCS:2538のみ | 開発側是正(注記追加)[FC] |
| R26 | OPEN-233-SELF-RECOVERY-TRIAL-01+PRODUCTION-WIRING-01(+CORRECTION-01/02) | Writer初稿の事実誤りをChecker→Rewrite→Recheckで自己修復 | rep30 VALIDATED(条件付き): Human Review 0・重大見逃し0・平均+¥0.13/run。CORRECTION-02でfresh確認FAIL | V(条件付き) | DL:18820(2026-10-05ユーザー決定、逐語)APPROVED_FOR_PRODUCTION、DL:19195・19301(是正指示)。2026-10-10にSUPERSEDED(OI:416・731、DL:20530(8)の要旨) | CS:2462・2501・2519・2536 | 未配線のままSUPERSEDED。Family X ProductionからSelf-Recoveryは参照されない(`er019*`/`er053*`のGrep: `er052_open233_self_recovery`の参照は`er053_en_sentence_splitter_01.py:9`のコメントのみ) | Trial(rep30等) | SUPERSEDED(Production未配線) | D(R25と同じ注記漏れ)。B(APPROVED未配線)ではなくユーザー決定によるSUPERSEDED | R25と同じ[FC] |
| R27 | OPEN-233-KPI-RECOVERY-REDESIGN-02、STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01、E2E-ACCEPTANCE-01 | Stage1 Checker再検証・後段誤降格・KPI | E2E 20 runで停止、Human Review KPI FAIL1件等 | UDR | DL:19825・19928(ユーザー決定) | CS:2536付近 | なし | Trial | UDR→SUPERSEDED | D(R25に包含) | R25と同じ |
| R28 | OPEN-238-PRECHECK-FALSE-POSITIVE-FIX-TRIAL-01/PRODUCTION-WIRING-01 | precheckの数値偽陽性(分数語「a third」→33.3%)除去 | 単体12 PASS、26 run Regression 発火2→0、実費JPY5.30 | V | DL:20217「案1をProduction採用=APPROVED_FOR_PRODUCTION」(ユーザー決定2026-10-07)、DL:20223(Fable判定PRODUCTION_WIRED確定) | 独立節なし(OPEN-233節内、OI:740) | `er052_open233_self_recovery_precheck_01.py:179`(`extract_percentages_strict`)、`er052_open233_self_recovery_flow_runner_01.py:8405`。Family X Production(`er019*`/`er053*`/`er012_e*`)からの参照0件(Grep) | あり(ai_control P2 rep2、実費JPY5.30) | PRODUCTION_WIRED(Self-Recovery flow runnerに対して。このflow自体が10/10にSUPERSEDED) | C/E: 名目上PRODUCTION_WIREDだが到達するFamily X Production経路がない。OI:740にこの事実の注記なし | Fable判断(PRODUCTION_WIRED表記の扱い)+開発側(OI:740注記)[FC] |
| R29 | ALL-6-LUNA-WRITER-REDESIGN-NECESSITY-TRIAL-01+PRODUCTION-MODEL-ROUTING-GPT6-WIRING-01(OPEN-241) | Writer等を5.6-luna→6-lunaへ。根本再設計の要否 | 48本生成。費用/本JPY9.46→4.29。事実NGは評価者で方向が割れ、T-B重大検出1/14→4/14 | M | DL:20259「判断7(新規): 全6-luna化をProduction方針として進めてOK」(逐語) | Model Routing節 | `er006_model_routing_contract_01.py:48-50`(WRITER_MODEL=SUPPORT_MODEL=gpt-6-luna)・:105(`STANDARD_A2_ADAPTATION`)・:110(`NATURAL_ENGLISH_ADAPTATION`)=Luna。Family X JA WriterはSolへ(R31) | あり(`er052_output/gpt6_wiring_e2e_01/E2E_EVIDENCE.md`) | PRODUCTION_WIRED(2026-10-08、DL:20287) | C: Sol統一は日本語B3/R0/R1/R2のみ(DL:20571は音声・翻訳・TTS・RF等を対象外と明記)。英語化(Luna)のLuna/Astra/Sol比較・判断: 判断証拠なし。OI:743の「O3観測(EN STOP率)」はEN deviation撤去後に観測不能 | ユーザー判断(EN化のモデル配置)[FC] |
| R30 | WRITER-R0-MODEL-IMPACT-TRIAL-01/-FIX01/-FIX02 | R0モデルの影響をRisk Flaggerで測定 | パーサ欠落を是正して再実行、12本RF | UDR | 判断証拠なし(DL:20476〜20491は「USER_DECISION_REQUIRED」のみ)。後のDL:20571(E案)で実質置換 | なし | R31が実質置換 | Trial | UDR(DL)。OIに該当行0件(Grep `WRITER-R0-MODEL-IMPACT`) | A: 判断漏れ(E案で実質吸収。吸収の明示記録なし) | 対応不要/Fable確認[FC] |
| R31 | FAMILY-X-JA-MODEL-ALLOCATION-SOL61-PRODUCTION-WIRING-01(E案) | B3/R0/R1/R2をgpt-6.1-solに統一 | Blind評価でE案は3記事とも最高グループ、費用も有利 | V(Blind) | DL:20571(逐語)。09:00記録§2で再確認 | CS:1157・1159 | `er006…:134-138`、`er019…runner:151-153`(B3 require_model)、`er053…writer_01.py:40-42,283,334-335`(R0/R1/R2 require_model+返却model不一致STOP) | あり(merge adb15c30、rollback tag) | PRODUCTION_WIRED(2026-10-11) | D(CS:1169 bulletが古い、R12参照) | R12と同じ |
| R32 | WRITER-EVAL-DUAL-LLM-METHOD-TRIAL-01 | 二重LLMによる評価方式の妥当性 | 4モデル(6-luna/5.6-luna/sol/DeepSeek)全てがK01(META反転)を見逃し | R(Fable最終判定) | DL:20435(ユーザー判断[逐語])・DL:20441(ユーザー指示要旨) | なし | なし(評価方式、Production外) | Trial | REJECTED | 問題なし(RFが後続の代替として配線) | 対応不要 |
| R33 | FACTLOCK-ASTRA-E2E-TRIAL-01 | 新Writer仕様+翻訳段対策のE2E(10記事、paired design) | G2テキスト完走。Fable最終判定はUDR(選択肢(a)〜(e)) | UDR(DL:20429) | 設計の決定1〜9: DL:20367・20377・20384(逐語要旨)。Trial結果に対する直接の採否回答: 判断証拠なし。2026-10-10にW-1採用(R12)で実質採用 | CS:1169 | R12 | G2 evidence(`er052_output/factlock_astra_e2e_trial_01`) | Trial単体=UDR、W-1としてPRODUCTION_WIRED | A: Trial単体の判定が未回答のまま別経路(W-1設計)で採用。吸収の明示記録なし | 対応不要/Fable確認[FC] |
| R34 | NEWS-STANDARD-A2-*(v1R/v2V/v3V/v4R/v5V)+NEWS-VOCAB-LEVEL-PRODUCTION-WIRING-01 | Standardの難易度(6,000語ライン+自然さ) | v5=V(必要語保持・不自然置換なし・2記事再現) | V(v5) | DL:9449(2026-09-25正式採用)、DL:9645項4(2026-09-26 firm 6,000語Band追加、逐語) | CS:831 | `er003_v1_n3_01_standard_a2_generate.py`(`generate_standard_a2`)。モデル`er006…:105`=Luna | あり(DL:9468) | PRODUCTION_WIRED | CS:831の"deviation MAJOR時の再生成"等が撤去済み機構の記述か未確認(Part C) | 確認のみ[FC] |
| R35 | ADVANCED-VOCAB-V2-PRODUCTION-RESTORE-01 / NEWS-ADVANCED-A2-PRODUCTION-E2E-WIRING-01 | Advanced英語の語彙平易化(v2)と自然な英語化 | v3=REJECTED確定、v2採用 | V | DL:9557(ユーザー決定)、DL:9432 | CS:830 | `er003_v1_n3_01_advanced_adaptation_generate.py:144`(`ADVANCED_VOCAB_RULE_V2_BLOCK`)・:350 | あり | PRODUCTION_WIRED | 問題なし(OPEN-182継続観察) | 対応不要 |
| R36 | TRANSLATION-SEGMENTATION-NO-HEADING-TRIAL-01→FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01 | 英訳から途中Headingを廃し段落境界3分割 | Meta v1でMAJOR1件(意味反転)→v2解消、Hormuzは初回から準拠 | UDR(Trial) | Trial: DL:12475。採用: OI:412「ユーザーが新構造(見出しなし)を正式採用」(2026-09-29)。逐語は未確認(DL:12517近傍) | CS:1371 | `er003_v1_n3_01_advanced_adaptation_generate.py`(commit 8d9064083)。must-fix retryは2026-10-10に撤去 | あり(Meta run_03、DL:12718) | PRODUCTION_WIRED(Gate3) | OI:412(OPEN-230)は「must-fix retryで解消」を前提にするがそのretryは撤去済み(CS:1182)。意味反転の守りはRFのみ(E) | 開発側(OI:412注記)[FC] |
| R37 | In One Line(M1(a)・文数仕様) | Advanced In One LineをJA+台帳入力で生成。文数「中心1文+補足2文程度」→最新ユーザー決定「基本2文・必要時のみ3文」 | 10/15 Coffee監査: final_03は両レベル1文のまま(層A=Promptが`Exactly one sentence`、層B=2文原稿が記事ソースに戻らず旧1文wavへ置換) | (監査) | 09:00記録§2(原文): 「In One Line（Std／Adv）：基本2文、必要な場合のみ3文。旧1文Promptを改修する」(2026-10-16 09:00 JST)。M1(a)のAdvanced限定維持: DL:20530(6) | CS:583(DECIDED「中心1文+補足2文程度」)、CS:1202〜1247(09:00記録、未commit) | Production Promptは今も`Exactly one sentence`(`er003_v1_n3_01_advanced_adaptation_generate.py:558`、template:551〜、M1変種:593〜611。最終commit 2026-10-08)。改修Promptは未作成(CS:1202〜1247にも「正本未特定」と記載) | 10/15監査で実測 | 09:00記録でAPPROVED_FOR_PRODUCTION・未配線 | B+F: 承認済みだがPrompt未反映。CS:583(中心1文+補足2文程度)との整合は仕様化時に確定(CS:1202〜1247) | 開発側(Prompt改修・Wiring)[FC] |
| R38 | WRITER-DEV-RISK-FLAGGER-DESIGN-01 / ANTENNA-TRIAL-01 / POST-EN-TRIAL-01 / A4-DUALMODEL-OR-TRIAL-01 / META-ROLLBACK-CROSSMODEL-01 / META-ROLLBACK-CHECK-01 | WriterのFact事故をCheckerなしで人間確認候補として拾う(A3/A4 Risk Flagger) | KPI1〜4は判定線上合格、KPI5未取得。4条件(Luna A3/A4、Gemini A3/A4)を選択 | UDR→(POST-EN)V | DL:20515「A3+A4 RFを英訳後・音声化前: VALIDATED。R0後・翻訳後Hard STOP Fact Checkを外す: APPROVED_FOR_PRODUCTION」(ユーザー決定、逐語要旨)、DL:20498(運用コンセプトAPPROVED) | CS:1155・1173 | `er053_risk_flagger_production_01.py`(CS:1173)。4条件・OR統合・Review Queue | あり(L3) | PRODUCTION_WIRED | 問題なし | 対応不要 |
| R39 | RISK-FLAGGER-PRODUCTION-WIRING-01 | RF 4条件+Review Queue+旧Fact Checker撤去を正式経路へ | 完了条件19項目中17充足→ユーザーが正式完了承認 | (配線案件) | DL:20550「ユーザー正式決定(Production Wiring正式完了承認…、逐語)」 | CS:1155〜1200 | CS:1182(撤去28行)。Production範囲(`er012_e*`/`er019*`/`er053*`)の旧Checker符号をGrepで0件確認(`must_fix`/`Stage1`/`Stage2`/`reclassify`/`JA_RECHECK_REQUIRED`/`OPEN243_*`/`OPEN233_*`/`run_deviation_check`ほか、`er053_dangling_reference_check_01.py:34-60`のリストと同一) | あり(L3) | PRODUCTION_WIRED | 問題なし(OPEN-245/246/249/250は残OPENだが非ブロッキング) | 対応不要 |
| R40 | POST-EN-HUMAN-PRE-SORTER-BLIND-TRIAL-01 | Human Review前にAIで候補を並べ替え | GPT系3モデルのみ実行(Anthropic3モデルは鍵なしUNAVAILABLE) | UDR | DL:20518「未決」。Production配線しない旨は委任_01 §ユーザー正式決定(`docs/pm/delegation_log/2026-10-10_RISK-FLAGGER-PRODUCTION-WIRING-01_01.md:4`「ChatGPT Pre評価をrunnerへAPI組み込みしない」) | なし | なし(組込禁止) | Trial | UDR(Trial)・Production配線せず | A: UDRのまま。OIに該当行0件 | ユーザー判断(Anthropic APIでの再実行要否)または対応不要[FC] |
| R41 | RFの新仕様候補(a)台帳にない定量・事実の挿入検出、(b)確信度閾値による可変件数、(c)D2ベース+疑義時のみ専用呼出(D1コスト削減) | RF検出範囲・件数・費用の改善 | 候補のみ(未実装) | (候補) | DL:20465・20471「未実装・要承認」。その後の回答: 判断証拠なし(DL:20495・20512は「確信度閾値の要否」を未決のまま列挙) | なし | なし | なし | 未承認の新仕様候補。OI/REGに行なし(Grep: `台帳にない定量`・`確信度閾値`はDL以外に0件) | A/E: 判断漏れ+Open Item不在 | ユーザー判断(3候補の採否)[FC] |
| R42 | NEWS-FAMILY-X-JA-FACT-CHECK-PRODUCTION-WIRING-01 | JA段のFull Ledger照合+must-fix retry | Meta/Hormuz run_02で実発火 | (配線案件) | DL:9726(Production配線)。撤去はR39(DL:20530(8)) | CS:829末尾 | 2026-10-10に撤去(符号は`er053_dangling_reference_check_01.py:34-50`の撤去対象。Production範囲のGrep 0件) | あり→撤去 | 撤去済み | D: CS:829が撤去を未反映(R13) | R13と同じ |
| R43 | OPEN-183 / OPEN-174 / OPEN-175 | 旧B3配線初回Meta記事の確認、素材混入・冒頭復唱の監視 | — | — | 判断証拠なし(OI:364はUSER_DECISION_REQUIRED、確認完了記録は見つからず) | — | — | — | OPEN | E: 記事は以後再生成・Sol化され陳腐化の可能性 | Fable確認(close可否)[FC] |
| R44 | PM-DEV-EVAL-LATEST-MODEL-RULE-01 | 評価用途の最新モデル原則 | — | — | DL:20450(ユーザー正式採用) | PM_GOVERNANCE 25節 | 運用ルール | — | ADOPTED | 問題なし | 対応不要 |
| R45 | FAMILY-X-20261016-0900-USER-DECISION-RECORD-01(2026-10-16 09:00 JST最終ユーザー判断) | Family X全体の最新承認基準(Sol統一、PD06、K2、P8、P7、M2P0、選定A、In One Line 2〜3文) | — | — | 09:00記録(ユーザー原文): `docs/pm/delegation_log/2026-10-16_FAMILY-X-20261016-0900-USER-DECISION-RECORD-01_USER.md:§2` | CS:1202〜1247、DL:21631(未commit) | §4参照 | §4参照 | RECORDED。新規採用はAPPROVED_FOR_PRODUCTION | §4・§3 B | §4参照 |

(補足)R26はSelf-Recovery配下の約66委任を代表させた。個別委任に独立の追加ユーザー判断はなかった(代表エントリのみ読了、§5)。

---------------------------------------------------------------------
## §3 問題分類A〜F別の該当一覧

各項目: 根拠(file:line)/重要度(H高・M中・L低)/[FC]=Fable確認要。

### A. VALIDATED(またはTrial成果)の放置・未回答
- A-1 R06/R07/R08(OPEN-237系: 台帳明確化P'・多義語Note・Note転記)(M)[FC]: DL:20135・20157〜20243。OI:739が2026-10-07を最後にUSER_DECISION_REQUIREDのまま。2026-10-08のFact Lock再設計後に整理した記録なし。notes_for_writerは決定論assemblerが制約ブロックへ転記(OI:750)したが、「Researcher prompt側のP'規則」「ambiguityのtxt出力」は未回答。
- A-2 R41(RF新仕様候補(a)(b)(c)・確信度閾値)(M)[FC]: DL:20465・20471・20495・20512。OI/REGに行がない。
- A-3 R19(エンタメ代理指標v1、暫定・未承認)(L)[FC]: DL:20245(d)。
- A-4 R40(Pre-sorter UDR)(L)[FC]: DL:20518。Anthropic鍵が無く3モデル未実行。Production配線しないことはユーザー明言。再実行要否のみ未回答。
- A-5 R30(WRITER-R0-MODEL-IMPACT)・R33(FACTLOCK-ASTRA-E2E Trial単体)のUDR(L)[FC]: 後続(W-1採用、E案採用)で実質吸収されたが明示記録なし。R30はOIに行がない。
- (参考)R15の「Sol/Terra: DEFERRED/HOLD」はユーザー明示defer(DL:9415項3・4)=放置ではない。

### B. APPROVEDの未配線
- B-1 **09:00記録の6仕様(H)[FC]**: PD06(Full Story TTS Std/Adv)、K2(KP英語音声 Std/Adv)、P8(Std KP日本語意味、旧M2置換)、P7(Adv KP英語解説、旧P3置換)、In One Line基本2文(旧1文Prompt改修)、KP選定A方式(現行維持=変更不要)。いずれも09:00記録で`APPROVED_FOR_PRODUCTION`・Family X正式経路未配線(CS:1202〜1247の自己記録も「配線の有無は未確認」)。私の確認: Production module(`er019*`、`er003_v1_n3*`、`er053*`、`er012_e*`)に、09:00記録が示すPD06のsha `3a680861…`、P8 sha `b12c8721…`、P7 sha `05180006…`、K2 sha `9d905cfe…`の出現は0件(Grep)。`er019_family_x_style_profile_01.py:16-17`は「他Role(K2/M2/A5/B5/E1/R2等)は後続Phase」と明記、profile定義(:100-108)はN01+R2+P3(+E1)でPD06/P8/P7/K2なし。A方式(現行)は変更不要のためProduction現状=A(未確認だが09:00記録は「A=現行Prompt変更なし」)。
- B-2 R15 NEWS-HOOK-POLICY-DECISION-01(M)[FC]: ユーザー正式決定「R2完成後にLunaでHookを1本Side output」(DL:9415)。OI:357が「Side output未配線」と自記。Family X runnerに該当stageなし(Grep 0件)。
- B-3 補足: OPEN-233系(R25/R26/R27)は「APPROVED_FOR_PRODUCTION→ユーザー決定でSUPERSEDED」で、未配線の放置ではない(DL:20530(8))。

### C. 部分配線
- C-1 R21 OPEN-220(L)[FC]: AN3の固有名詞方針はJA Writerのみ。英語側`ADVANCED_VOCAB_RULE_V2_BLOCK`は固有名詞KEEPのまま。「Advanced Prompt維持」(CS:886)に基づく意図的な部分適用で、要否はユーザー判断待ち。
- C-2 R28 OPEN-238 Precheck(M)[FC]: コードは`er052_open233_self_recovery_precheck_01.py:179`・flow runner:8405にあるが、Family X Productionからの参照0件。名目上「PRODUCTION_WIRED」(DL:20223)でも、到達するProduction経路がない。
- C-3 R29 英語Advanced/Standard生成モデル(M低): Writer系のSol統一は日本語B3/R0/R1/R2のみ。英語化は`er006…:105,110`=Lunaのまま。意図的(DL:20571は音声・翻訳・TTS・RF等を対象外と明記)か、比較未実施かの判断証拠は見つからない。

### D. 仕様の上書き・消失
- D-1 R20 AN3第1文の置換(M)[FC]: `er053_family_x_factlock_ja_writer_01.py:131-139`が、ユーザー承認AN3の第1文(数字・時刻の抑制)をFact Lock数字規則(5)で置換。CS:905は「AN3 blockはW-1 R0に含まれたまま有効(sha 067030ff…)」と記述。置換が「数値規則(c)」(DL:20297)の意図的採用かは、DL:20297の要旨からは確認できない。
- D-2 R13/R42 CS:829の陳腐化(M)[FC]: 現行実装(Sol・独立call・R2入力=R1 raw・Fact Checker撤去)と、CS:829(Luna・previous_response_id連鎖・JA Fact Check retry)の食い違い。置換注記なし。
- D-3 R12/R31 CS:1169のR0=Luna・R1/R2=Astra記述(L)[FC]: 見出し側(CS:1157・1159)に追記あるが当該bullet未更新。
- D-4 R25/R26/R27 CS:2462・2501・2519(L)[FC]: APPROVED_FOR_PRODUCTIONのStatus行にSUPERSEDED注記がない(注記はCS:2538のみ)。
- D-5 R04 OI:750の見出しStatusが古い(L)[FC]。
- D-6 R37 CS:583(中心1文+補足2文程度)と09:00記録(基本2文・必要時3文)の整合は未確定(CS:1202〜1247に「仕様化時に確定」と明記済み)(M)。
- D-7 09:00記録の旧決定との関係: 旧M2→P8、旧P3→P7、PD8→P8→N01(Full Story)→PD06という置換連鎖。CS:2669〜2678(Coffee限定Style節)に履歴として残る。取り違えを避けるため、現行=09:00記録と読む旨の冒頭注記がCS:2669〜側にあるかは未確認(L)。

### E. Dangling Reference
- E-1 R24 OPEN-243(M)[FC]: OI:745の「現行の守り」(EN deviation check、O3観測)は撤去済み(CS:1182)。OPEN-241の「O3観測(EN STOP率)」も観測不能。
- E-2 R36 OPEN-230(L): 解決策(must-fix retry)が撤去済み。
- E-3 R23 OPEN-233周辺のTrial(Stage0/T1/T3/T4/ACTION-POLICY/Stage2): 結果は`er052_output`配下にあるがDL/LED/OIに語がほぼ0件(L)。
- E-4 R43 OPEN-183: 旧Meta記事の確認待ち(L)。
- E-5(技術面は問題なし)Production範囲に旧Fact Checker符号の残存0件(R39に同じGrep)。

### F. 承認済み仕様と完成品の不一致
- F-1 R37 In One Line(H)[FC]: CS:583は「中心1文+補足2文程度」、09:00記録は「基本2文、必要時3文」だが、Production Promptは`Exactly one sentence`(`er003_v1_n3_01_advanced_adaptation_generate.py:558`)。10/15 Coffee監査の層A。10/16時点で未修正。
- F-2 K2/M2/P8/PD06/P7のProfile未反映(H)[FC]: B-1と同じ根拠。10/15 Coffee監査の層B(§5-2)。
- F-3 R18 品質マスター(`docs/quality/ja_quality_masters/`)を参照する手順・コードがない(L)[FC]。
- F-4 09:00記録のStd Full Storyの扱い(M)[FC]: 09:00記録の備考にあるとおり、PD06の正本Trial(Trial-02)はAdvanced Full Story対象で、Std Full Storyへの同一文適用・6%減速併用は正本に明記なし(CS:1202〜1247の自己記載)。完成品との照合時に曖昧さが残る。

---------------------------------------------------------------------
## §4 §6既存決定事項7件の配線状況(09:00記録§2の表と対応)

| # | 既存決定 | ユーザー判断の出典 | 実装(file:line) | runtime evidence | 判定 | 備考 |
|---|---|---|---|---|---|---|
| 1 | B3/R0/R1/R2のSol統一 | DL:20571(逐語)、09:00記録§2 | `er006_model_routing_contract_01.py:134-138`、`er019…runner:151-153`、`er053…writer_01.py:40-42,283,334-335` | あり(`er019_output/meta/run_sol61_01/`) | PRODUCTION_WIRED(CS:1159) | 英語化はLunaのまま(C-3)。CS:1169 bulletが古い(D-3) |
| 2 | Family X正式WriterのFact Lock構造 | DL:20530(1)・DL:20544 | `er053_family_x_factlock_ja_writer_01.py:262-445`ほか | あり(L3) | PRODUCTION_WIRED(CS:1169) | AN3第1文置換(D-1) |
| 3 | CoffeeをResearchから全面再制作 | 09:00記録§3(原文): 「Coffeeはテーマのみ維持し、Researchから音声完成まで全面新規生成」 | — | — | 未着手(記録のみ、09:00記録§7「Coffeeの再生成は開始しない」) | 配線状況の対象外 |
| 4 | Coffeeを代表記事としてFamily X共通Production仕様を完成 | 09:00記録§1・§3(原文): 「Coffee限定仕様ではない」「対象Family=Family X全体」 | — | — | 記録済み | CS:2669〜(Coffee限定Style節)の「全記事共通は未承認(OPEN-298)」との関係は、09:00記録が「Coffee限定だった各Style承認(OPEN-298/300)は拡大された」と明記(CS:1202〜1247)。OI側の更新は並行worker作業中(OI:801・803・816が変更差分に含まれる) |
| 5 | KP候補供給M2P0、選定優先順位A | M2P0: DL:20958付近(2026-10-13、逐語要旨)、09:00記録§2。優先順位A: 09:00記録§2(原文)。以前はREG#26/OI:828が「UDR」(今回の判断で解消) | M2P0: `er071_output/m2p0_n01_production_wiring_01/`ほか、`er019_family_x_audio_production_runner_01.py`系(詳細Part C)。A=現行 | M2P0 Coffee runtimeあり(DL:20958付近) | M2P0=配線済み・未完了(PRODUCTION_WIRED不付与)/A=現行Prompt維持(コード変更なし) | OI:828(OPEN-325)・REG#26・#32の更新状況は未確認(並行worker作業中) |
| 6 | Full Story PD06、KP英語K2、Std日本語意味P8、Adv英語解説P7 | 09:00記録§2(原文) | 未配線(B-1。shaのGrep 0件) | なし(Trial: PD06=`er057_output/pace_trial_02`、P8=`er057_output/std_kp_ja_style_trial_02`、P7=`er080_output/coffee_kp_en_explanation_pacing_trial_01`) | APPROVED_FOR_PRODUCTION・未配線 | PD06の正本対応づけは名称による(CS:1202〜1247自記)。Trial-02はAdv対象。OI:902(OPEN-393)は私の読了時点で「試聴待ち」のまま |
| 7 | In One Lineは基本2文、必要な場合のみ3文 | 09:00記録§2(原文) | 未実装(`…advanced_adaptation_generate.py:558`) | — | APPROVED_FOR_PRODUCTION・未配線 | F-1。OI:802(OPEN-299)は私の読了時点で「未仕様化・未承認」のまま(更新作業中の可能性) |

---------------------------------------------------------------------
## §5 未確認事項・探索できなかった範囲

1. チャット原文そのもの: Repo外。DLの「逐語」記述がチャット原文と一致するかは未検証。09:00記録(`..._USER.md`)と本件`..._USER.md`はRepo内原文として扱った。
2. Production実装のretry/fallback/regenerationの分岐別コード照合(`--regenerate-stage`、resume、記号QA再実行、U-1の全分岐、sha整合): Part Cの範囲。私が確認したのはfile:line数点のみ。
3. 実Prompt本文とCS記載の突合(R0_PROMPT、DEVELOPER_MESSAGE、REVISION_INSTRUCTIONS、RF Prompt sha): Part C。
4. `docs/pm/REPORT_LEDGER.md`は管理ID検索のみ(行ごとの初回報告/Feedback状態は未精査)。
5. `ER-*_REPORT.md`/`docs/research/`の結論節は一部のみ。Glob `**/B3*`・`**/AN3*`・`**/FACT-LOCK*`等のREPORT個別の読了は未実施(DL/OI/CSを正本とした)。
6. Self-Recovery Trial(約140エントリ・約66委任)は代表エントリのみ読了。rep1〜rep30の細部は未精査。
7. 並行worker編集の影響: CURRENT_SPEC.md/DECISION_LOG.md/OPEN_ITEMS.mdは読了中に未commitで更新された(CS:+50行、DL:+26行、OI:18行変更)。本書のCS:1202以降・DL末尾・OI(OPEN-298/299/300/313/317/325等)の記述は更新前後が混在しうる。最終commit後の再照合が必要。
8. Family Z側のWriter/Story品質Trial、Family Y(Voices)は対象外。他Family(A/B/C)に残る共有関数(`vfl01.run_deviation_check`等)は未調査。
9. 2026-10-15〜16のASR/TTS/KP gloss/AUW系決定はWriter関連ではないため範囲外。

---------------------------------------------------------------------
## §6 Sonnet所見(参考。判断はFable)

1. 09:00記録の6仕様(PD06・K2・P8・P7・In One Line・A方式)は承認済み・未配線。最優先は「配線の有無」ではなく、(a)各仕様の正本Prompt(sha)をProduction側の定数・profileへ落とす先(`er019_family_x_style_profile_01.py`は現状N01+R2+P3+E1までで、K2/M2はスコープ外と自記)、(b)In One Lineの2文Promptを新規作成する際のCS:583との整合、の設計判断。これらは10/15 Coffee監査の層Aと層B(profile外のStyle)の再発防止と同根。
2. SSOT内の「置換されたが注記がない」記述(CS:829・CS:905・CS:1169・CS:2462〜2519)が最も取り違えやすい。実装は正しいが、仕様文書を読む次の担当者が旧方式(Luna・previous_response_id・Fact Check retry・Self-Recovery APPROVED)を現行と誤認する構造。09:00記録の「旧仕様は履歴として保持し、現行仕様と取り違えない」に直結する。
3. 「OIに載っている=ユーザー保留」ではない点を守ると、OPEN-237系(台帳明確化・Note)とRF新仕様候補(a)(b)(c)は「判断漏れ」として残る。2026-10-08のFact Lock再設計と10/10のRF導入で問題設定が変わっているため、個別に問い直すより「継続/廃止/対応不要」の一括整理をユーザーに求めるほうが現実的(R06〜R08、R41)。
4. AN3第1文の置換(D-1)は、W-1 R0の品質(「数字を極力使わない」)にとって最も実質的な差。ユーザー決定としての追認がDLの要旨では見つからない。
5. OPEN-243(翻訳段NG)は「守り」が撤去されRFだけが残る。RFが対象とする型(主体入替・複数形化・訳語ずれ・要約付け足し)の範囲をユーザーに確認する価値がある。
