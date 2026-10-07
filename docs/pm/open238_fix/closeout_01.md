# OPEN-238-PRECHECK-FALSE-POSITIVE-FIX-TRIAL-01 Closeout(委任_C1、2026-10-07、¥0・API呼び出しなし)
Status=**VALIDATED(Trial限定。Production採用はAPPROVED_FOR_PRODUCTIONではなく、ユーザー判断待ち)**(Fable判定)。Production無変更・Checker未配線(PRODUCTION_WIRED未)維持。

## 1 案別の効果・副作用
| 項目 | 案1(ホワイトリスト+M1〜M3) | 案2(数字・%なし文はclaim化しない) |
|---|---|---|
| 効果 | 「a third party」型の偽陽性を抽出段階で除外。26 run Regressionで発火2→0、他run不変 | 実測では案1と同じ1件を防ぐのみ(分数語を含む文は全コーパスで1文) |
| 副作用 | 直後が動詞等の正当分数の取りこぼし(軽微)。残る偽陽性例あり(§3) | 分数語のみの文の機械検出を失う(コーパスに正当分数語0件で実測0=安全の証明にならず) |
| 判定 | **推奨(Trial VALIDATED)** | **不採用**(Opus同意) |
| 実装範囲 | Trial専用DEVラッパ`er052_open238_precheck_fix_dev_01.py`のみ(Production無変更) | 未実装 |
| O1(分数語をforeign証拠から外す単純案) | ユーザー決定: **今回は不採用・記録のみ**(2026-10-07) | 同左 |

## 2 既存Regression・テスト・実経路
- 単体テスト12件PASS(`er052_output/open238_precheck_fix_trial_01/tests/test_precheck_fix_dev_01.py`)。
- 決定論Regression 26 run(修正前/後同一プロセス): fires 2→0、差分runはai_control P2 rep2のみ。O2のbit単位不変(loose抽出/台帳loose/L322/number_mismatch以外の全finding)=全True。保存ベースラインと一致。`.../regression/REGRESSION.md`。
- 実経路再生N=1(ai_control P2 rep2 cycle1、Stage1→2→Rewrite): precheck発火0、third party文保持、84%文混入なし、retry/fallback 0件、最終RESOLVED_REWRITE_THEN_DOWNGRADE 3cycle(修正前4cycle)。実費¥5.54/上限¥100。`.../replay/REPLAY_RESULT.md`。
- O3 "percentage point(s)": 36/58テキストで0件。新規起票不要(記録のみ)。

## 3 費用・処理時間への影響
precheckは決定論処理のため追加API費用0、処理時間影響なし。Trial自体の費用は実経路再生の¥5.54のみ。

## 4 Production実装時の注意点(採用された場合のみ。Opus指摘)
- `extract_percentages_strict`を新設し、`check_number_mismatch`の`foreign_observed`計算(precheck L262)のみ厳格版へ差し替え。台帳値確認・expected・all_ledger_pct・L322・runner L2585/L2838/L3090・coverage_checker L475は現行(緩い)抽出のまま。
- runner `resolve_precheck_target_sentence`(L8093)のnumber_mismatch対象文特定も厳格版へ。
- `FRACTION_WORD_TO_PERCENT`と現行`extract_percentages`は不変。`PRECHECK_MODE`・runner L8784-8800(precheck floorのStage 2スキップ)・Stage 2は不変。
- 想定は2ファイル数十行。実装時はOpus条件Cレビュー+既存9 run json(+全26 run)での決定論Regression再実行が必須。CURRENT_SPEC更新・APPROVED_FOR_PRODUCTIONは人間ユーザーのみ。

## 5 残存リスク
1. 残る偽陽性例: 「seeking a third.」「half the time」「in a quarter.」等(M3で期待値=抽出と明記)。
2. 直後が動詞の正当表現等の取りこぼし(ホワイトリスト語彙外)。比較形容詞の語彙漏れ。LLM Stage1/2が残るため軽微。
3. コーパスに正当な分数語がほぼ無く(分数語を含む文は1文のみ)、取りこぼし側の実測は不足。
4. 実経路再生はN=1・LLM非決定性あり(precheck消失は決定論側で裏付け、文保持は参考)。
5. 分数語以外の偽陽性(序数・金額・日付辞書、COUNT_WORD_RE)の網羅走査は未実施。
6. Checker OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01は未配線、残11 runは停止継続(本Trial成功を理由に再開しない)。

## 6 参照
`docs/pm/open238_fix/design_01.md`、`docs/pm/opus_l2_review_open238_fix_01.md`、`er052_output/open238_precheck_fix_trial_01/`、`er052_open238_precheck_fix_dev_01.py`、`docs/pm/open238_precheck_mislink_diag_01.md`、REPORT §96/§98、commit 8f543442(DIAG)/0afc0911(Phase A/B)/971e9be1(B2)。
