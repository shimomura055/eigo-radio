# GAP_MAP_01: 発音同等性ASR判定 — 既存機構との対応・ギャップ整理

管理ID: ASR-PHONETIC-EQUIVALENCE-GENERALIZATION-01 委任_01 / Status: `DESIGN_DRAFT`(整理のみ。Production無変更、費用JPY0)。
根拠: Productionコードの読取り(下記の行番号。2026-10-13時点のworking tree)と既存SSOT/報告(`docs/pm/reports/2026-10-13_CONNECTED_SPEECH_REPORT_REPLAY_01.md`、`CS_AUDIT_01.md`、`PHASE2_REPORT_02.md`)。**未確認の箇所は「未確認」と明記**。
KPI provenance: 本書の件数は配線状態のセル数(reuse=既存コード読取り)。fresh E2E値ではない。

## 0. 既存資産照合(PM_GOVERNANCE 21節 A/B/C分類)

| 論点 | 分類 | 根拠・扱い |
|---|---|---|
| 発音上の同等性・連結発音を診断して許容する思想 | **A. 既存仕様あり** | 承認済み原則(CURRENT_SPEC L2025/L2026、OPEN-107/110/122)。新仕様にしない。 |
| 同音異綴り(`Mello`/`Mellow`≡`Melo`)をPattern Aと同じ基準で扱う | **B. 過去Trialあり・未採用** | OPEN-327 C-1(stem同音A')、ASR汎用Trial(`p2_phon.py`、Production未配線)。A'は効果がMelos固有(合成18名でMelosのみ+12件)。本設計は「ASR側同音綴り正規化+既存判定」で再検討(何が変わったか=Pattern A比の誤PASS増分を実測する評価Bを追加)。 |
| 一般語の同音異綴り(wait/weight) | **A. 既存仕様あり** | `er008_asr_variant_hardening_15_homophone_en.py`、`_step_alternate_pass`(承認済み、CMU Case A)。 |
| 固有名詞の同音異綴り(CMU代表発音一致) | **A. 既存仕様あり** | `entity_word_arpabet_primary_match`(Tseの実例に基づく保守基準)。OOV(Melos)は未解決のまま(Ledger推定・low confidence)。 |
| 減速後へのEq Layer適用 | **A→既知スコープ外** | OPEN-122(4)に既知Gapとして記録済み。承認済み仕様の配線漏れではなく、スコープ外・ユーザー承認なしに実装しない(OPEN-328)。 |
| Std減速後のTier3/CMU Case A救済 | **A. 是正済み** | eb4c6479(`_post_slowdown_cascade_rescue`)。 |
| 音響独立証拠(摩擦区間長)を許容の根拠にする | **B. 過去Trial・REJECTED** | AUC=0.74で単独gate不可(PHASE2_REPORT_02)。 |
| 文脈付きASR結合(C-c)をauto-accept条件にする | **B. 過去Trial・REJECTED** | OPEN-318。 |
| clip末尾完全性の独立確認 | **C. 本当に新規(設計草案のみ)** | 過去Trialは必要性のみ指摘(D-4増分誤許容19件=syn_B1_trunc*)。本委任のoffline評価で最小プロトタイプを評価。 |
| G2P(OOV固有名詞の音素推定)導入 | **B. 提案のみ・未導入** | PHASE2_REPORT_02。新規依存。本設計では**使わない**(推定音素は確認済み発音と扱わない)。 |
| Dialogue clipのsegment_id未伝播 | **A. 配線漏れ(OPEN-322)** | 承認済みrole gating(er021 Tier1/Tier3)が効かない。本設計と独立。 |

## 1. 7段構造 × 既存機構の対応表

凡例: **対応済み** / **部分対応** / **未対応**(理由)。列=既存機構。

| 段(ユーザー合意の7段構造) | Pattern A/B/C | Equivalence Layer(OPEN-122) | Resolver / Ledger / CMU Case A | ASR Semantic Eq(er021) | Secondary ASR Cascade Tier3 | `_post_slowdown_cascade_rescue` | LR 7 Gates |
|---|---|---|---|---|---|---|---|
| (1) 差分検出 | 部分対応(`word_diff`は**最初の差のみ**。後続差分を見ない) | 部分対応(同じ`word_diff`を再利用) | 対応済み(`protected_check`のdifflib全差分) | 部分対応(`determine_sub_reason`は**ちょうど1トークン差**のみ) | 部分対応(同左) | 対応済み(Primaryの判定結果を引継ぐ) | 対象外(テキスト側Gate。NG span特定は別: er020 Part C) |
| (2) 固有名詞・一般語それぞれの発音確認 | 未対応(綴りのみ、発音を見ない) | 部分対応(CMU`word_phones`。OOV固有名詞は不可=`melos`は`None`) | 部分対応(一般語=CMU全変種一致、固有名詞=CMU代表発音のみ。OOVはLedger推定=low confidenceでTTS注入対象外、`melos`は期待読みと実TTSが不一致=OPEN-308) | 未対応(発音確認ではなくTier1値等価/Tier3 corroboration) | 部分対応(独立ASRが綴りまで支持すること=発音確認ではない。Phrase Listが綴りを誘導) | 継承 | 未対応 |
| (3) 音素レベルの同等性評価 | **未対応**(綴り水準: `canonical == asr+s/es`) | 部分対応(`phoneme_prefix_drop`[末尾脱落1〜2音素]/`phoneme_final_place_substitution`のみ。同音異綴り・母音差・OOVは不可) | 部分対応(単語1対1の同音のみ。連結考慮なし) | 未対応 | 未対応 | 継承 | 未対応 |
| (4) 同音異綴り/自然な連結/融合・弱化・脱落/再分割の区別診断 | 部分対応(A=歯擦音連続の接尾辞s脱落、B=同系破裂音の-ed脱落、C=再分節[追加子音]。**同音異綴りの区別なし**) | 部分対応(カテゴリA〜G診断あり。入口が`TRUE_CONTENT_MISMATCH`限定でUNCERTAIN[固有名詞・同音語]には届かない=`er006_secondary_asr_01.py` L547-548) | 同音異綴りのみ | 未対応 | 未対応 | **Eq Layer未配線**(OPEN-122(4)、dead wiring: 入口条件が噛み合わない) | 未対応 |
| (5) 既存承認済み許容ルールの一貫適用 | 対応済み(ただし**綴り変種ごとに非対称**: `Melo`は受理、同音の`Mello`は未受理=OPEN-327/330) | 対応済み(承認範囲内で) | 対応済み | 対応済み(Tier1/Tier3、role gating) | 対応済み | 対応済み(是正A) | 対応済み |
| (6) 安全条件の維持(否定・時制・数・重要語) | 部分対応(`protected_check`通過後に呼ばれる=数・否定は保護。ただし**first-diff-only**で後続の無関係な置換を見逃す既存の限界[本委任で特性固定]、語幹末s受理範囲=OPEN-330) | 対応済み(`protected.passed=True`必須+独立ASR corroboration必須) | 対応済み(固有名詞は代表発音のみの保守基準) | 対応済み(数値/否定は別ゲート) | 部分対応(Phrase Listによる誘導。決定的≠忠実) | 対応済み(fail-closed、例外時は救済しない) | 対応済み(7 Gates) |
| (7) 根拠不十分なら無条件PASSにせず既存判定/HRへ | 対応済み(非該当はUNCLASSIFIED→既存判定) | 対応済み(INSUFFICIENT_EVIDENCE等は既存判定のまま、診断のみ付与) | 対応済み | 対応済み | 対応済み(corroborationなし=既存判定) | 対応済み | 対応済み(NO_CANDIDATE→HR) |

**要点**: (3)(4)が構造的に弱い。綴り水準のPattern Aは、同音異綴りの正規化層が無いために `Melo`/`Mello` 非対称を生む。Eq Layerは音素水準だが、入口条件(`TRUE_CONTENT_MISMATCH`限定)とOOV(G2P不在)で固有名詞には届かず、減速後には配線すらされない。

## 2. 6経路 × 既存機構の配線状態

区分: **配線済み** / **未配線**(承認済み仕様の配線漏れ) / **既知スコープ外**(OPEN-122(4)等、承認なしに実装しない) / **新規仕様が必要**。(`W`=配線済み)

| 経路 | Pattern A/B/C | Eq Layer | CMU Case A(Resolver) | ASR Sem. Tier1 | Tier3/Cascade | LR(回復) |
|---|---|---|---|---|---|---|
| R1 Std減速前(narration、`generate_a2_segment_with_slowdown`→`generate_english_segment_with_fallback`) | W | W(role判定`connected_speech_enabled_for`、er020 L162。`er003_v1_n3_01_tts_generate.py` L352) | W | W | W | W |
| R1' Std減速前(dialogue clip、`er012_b_family_voices_production_01.py` L549) | W(role非依存) | **未確認**(flag伝播は呼出元依存。dialogue呼出がflagをTrueで渡すかは未確認) | W | **未配線**(OPEN-322: `segment_id`未伝播でrole gating無効) | **未配線**(同) | **未確認** |
| R2 Std減速後(`apply_a2_slowdown_postprocess` `er003_v1_n3_01_tts_generate.py` L169、`classify_asr_match(segment_id=name)` L196) | W | **既知スコープ外**(OPEN-122(4)/OPEN-328。`_post_slowdown_cascade_rescue` L117はUNCERTAIN以外を即returnし、Eq Layer入口はTRUE_CONTENT_MISMATCH限定のためflagを渡すだけではdead wiring) | W(`is_homophone_candidate_mismatch` `er003_v1_n3_01_tts_generate.py` L235+cascade内`_step_alternate_pass` `er006_secondary_asr_01.py` L739/L764/L795) | W(L196) | W(**UNCERTAINのみ**、是正A。減速後のTRUE_CONTENT_MISMATCHはcascade対象外=上記と同じ既知スコープ外) | **未配線**(OPEN-320: 減速後NGがHRに到達せず`STOPPED`のままになる状態不整合) |
| R3 Advanced(B1B、`er003_v1_sing01_news_tail_fix.py` L202-205、`voice01` L238-247) | W | W | W | W | W(narrator。dialogue bodyはOPEN-322で未配線) | W(`run_local_rewrite_recovery` news_tail L368 / voice01 L359) |
| R4 初回生成(Std/Adv共通primitive) | W | W | W | W | W | 対象外(初回はLR前) |
| R5 retry/fallback/regeneration(標準2+fallback1=総3回、cool-down、HR後`REGENERATE_APPROVED_GRANTED`) | W | W | W | W | W | W(`maybe_cooldown_before_attempt` / `run_local_rewrite_recovery`) |
| R6 Local Rewrite後の再検証(`er003_v1_crosslevel_audio_02_common.py` L261-293/L411) | W | W | W | W | W | **新規仕様が必要**(OPEN-318: 2語clipでは1語入れ替えがGate7=全面書換と判定されて全候補不通過) |

**セル数集計(7行×6列=42セル)**: 配線済み **34** / 未配線 **3**(R1' Tier1・Tier3=OPEN-322、R2 LR=OPEN-320) / 既知スコープ外 **1**(R2 Eq Layer) / 新規仕様が必要 **1**(R6 LR) / 未確認 **2**(R1' Eq Layer・LR) / 対象外 **1**(R4 LR)。

**注意**: 本表は**既存の承認済み機構が各経路に届いているか**であり、本委任の新設計(DESIGN_DRAFT_01の方式M1)の適用先とは別。M1は、全経路が共通して通る `val.classify_asr_match`(Pattern A/B/C・Tier1)と共有cascade(`secondary_asr.evaluate_attempt_with_cascade_detail`)の**内側**に置くため、R1〜R6のうち既にPattern Aに届いている経路(R1/R2/R3/R4/R5/R6)には同時に効く(減速後だけ後追いにならない)。R1'は`segment_id`未伝播でも判定自体は動く(M1はrole非依存にできる)。

## 3. 新規発見(既存仕様の穴。本委任では修正せず報告のみ)

| # | 内容 | 実証 | 扱い |
|---|---|---|---|
| F1 | Pattern A/B/Cは`word_diff`の**最初の食い違いのみ**で判定し、後続の無関係な置換(`cats`→`dogs`)を検査せずACCEPTにする | `The studies suggest cats today.`/`The study suggests dogs today.` が`CONNECTED_SPEECH_ACCEPT`(特性test固定) | OPEN-330/339へ追記(既存Pattern Aの誤PASS露出)。ユーザー判断。 |
| F2 | 固有名詞の保守基準(代表発音のみ)が、`_step_alternate_pass`の`HOMOPHONE_EQUIVALENT`(CMU全変種のいずれか一致)経路では実質緩い(`entity_like`かつ`homophone_candidate`の語は後者でPASSし得る。例: `Tse`/`C`の第2変種一致) | `Kristie Tse` vs `Christy C`(M1が`christy→kristie`正規化後に遭遇) | 本設計はこの緩い経路をM1の受理根拠にしない(HR候補止まり)。Production側は無変更・報告のみ。 |
| F3 | 受理面: Pattern Aは`Hayes said`←`Hay said`のように、語幹が別の実在語になり得る場合も綴りだけで受理する(語末s脱落の仮定) | OFFLINE_EVAL_01 §5 | OPEN-330(既存)。 |
| F4 | 既存回帰test `er026_post_slowdown_cascade_rescue_01_test_01.py` は共有`telemetry.jsonl`へ3行追記する(未patchのtestがある) | stub差替えで再現確認(+3/実行) | OPEN-328へ運用メモ追記。 |
