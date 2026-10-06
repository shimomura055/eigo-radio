# Opus独立技術レビュー(条件A) OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01 (2026-10-06、要旨)

(1)結論: 変更は必要。計画は修正要(方向は妥当: post-filter方式/案B/`apply_floor`発火集合の縮小/`CAUSAL_FLOOR=False`・`FLOOR_VERIFY_MODE=off`)。修正3点: 再分類の位置(合流前)、Recheckでの前回指摘の扱い、再分類callのeffort固定。

(2)推奨構造:
- M1 再分類は`union_candidates`(coverage_checker L725-747、sources/flagsをORで合流)の前に経路別entryで1箇所適用(module側`candidate_filter`、`run_stage1_coverage` L870/`run_recheck_scope` L1034/`run_exit_full_r3` L1052)。混在候補でモデル側フラグ(`changed_number`含む)が決定論側保持で残り、却下フラグで数字floorが発火しうるため。Trialは合流前entryで判定(reclassify L101-112, L273-279)。
- M2 `prior_issues_resolved`は`run_recheck_scope`内部(L1037)で再分類前の候補で計算される→再分類後に。前回指摘と同文の候補は再分類対象外(fail-closed、Stage 2が再判定)。`MATERIALITY_BLOCKING_PIN`(L8678-8690)はStage 2到達候補にしか効かない。出口にも同保護。fact_id単位未解消規則(L1009 `same_fact`)は残存リスク。
- M3 `make_stage1_call_fn`(L1765-1771)はラベルでeffortを決め、r3系以外は`STAGE1_R5_REASONING`=high→再分類はmedium固定のcall_fnを新設。`DEVELOPER_MESSAGE`(L33-36)も逐語移植しsha256テスト。
- M4 precheck候補はStage 1既存fact_idを除外して作られる(L8597-8598、L8031)ため再分類で候補が減ると数字以外precheckのStage 2スキップBLOCKINGが増える→number_mismatchのみ、`build_precheck_floor_claims`とF3記録(L8456)が1関数を共用。
- M5 承認構成をrunner側の名前付き定数に。

(3)リスク: R1 失敗時はCANDIDATE残し(fail-closed)、provenanceで「対象0件」と「失敗全通過」を区別。Recheck・出口の再分類はTrial未検証、E2Eが初証拠。R2【確認】上書き箇所: `apply_floor` L2437(唯一の流れ制御)/`apply_floor_cited` L2499(記録)/floor_verify L3831(off)/Tier0 L3920(`CAUSAL_FLOOR`で囲まれる)/`downgrade_verify` L3558(既定`STAGE2_DOWNGRADE_VERIFY=False`)/precheck Stage 2スキップ L8644。E2E assertに`STAGE2_DOWNGRADE_VERIFY=False`・`TIER0_G_L_ENABLED=False`追加。`DISCLOSURE_GAP_DISQUALIFYING_FLAGS`は明示リストへ切り離し推奨。R3 数字検査3系統: (a)LLM `changed_number`→`apply_floor`、(b)決定論`number_not_in_fact`は候補化のみ、(c)precheck `number_mismatch`→Stage 2スキップ。R4 時期floor廃止後neg3 b1b型は再分類・Stage 2・S1依存、9 runでneg3 n=1。R5 承認構成がE2E scriptにしか無いとTrial専用→定数化。S1対象は増える。

(4)代替: 第1案M1(module側filter)、第2案runnerで再構成→重複実装のため第2候補。

(5)実装前必須: M1/M2/M3/M4/E2E assert追加/M5。推奨: ¥0事前replay(watch list)。

(6)9 runで主張できる: 技術障害なく完走/run別費用・工程内訳/候補数・Rewrite数・Human Review数/数字floor発火(a/c別)/再分類除外数/S1 BLOCKING化件数。主張できない: 重大見逃し0のSafety KPI/A2A3・A4・A5・B4・neg5のrecall/主体・比較・否定floor廃止の安全影響/統計的改善幅/hold-out再現。

(7)Dangling: `KPI_TRIAL_SWITCHES`(L425, L432)のSUPERSEDED明記要。CURRENT_SPEC L2373-2389・L2397、OPEN_ITEMS L727、A1-PROD行。
