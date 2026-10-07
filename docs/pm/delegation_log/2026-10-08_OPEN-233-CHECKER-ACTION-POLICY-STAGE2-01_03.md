# 2026-10-08 OPEN-233-CHECKER-ACTION-POLICY-STAGE2-01 委任_03(T2: ①v3=役割クラス比較+語り枠保持、7対象×3反復のreplay、上限¥25)

Management-ID: OPEN-233-CHECKER-ACTION-POLICY-STAGE2-01(委任_03)
性質: Trial/検証(DEV)。Production変更なし、APPROVED_FOR_PRODUCTIONなし。SSOT/ACTIVE_TASK/RESULT_PACKET編集禁止、git禁止。

## 並行タスク(衝突回避)
委任(REVERSAL-DETECT-01_01: `er052_output/open233_reversal_detect_01/`、`docs/pm/reversal_detect_01/`)が並行。本委任の書込先: runner `er052_open233_self_recovery_flow_runner_01.py` の構造要素Rewrite規則部分(①のみ。②のコードは触らない)、tests、`er052_output/open233_stage2_01/v3/`、`docs/pm/checker_action_policy_01/preregistration_T2.md`、delegation_log。起動前に`Get-Process python*`を確認し二重起動を防ぐ(M6)。API上限¥25、¥22でSTOP。②スイッチ(`OPEN233_STAGE2_READER_BELIEF`)はOFFのまま。

## 事前指定Read
- `er052_output/open233_stage2_01/eval/STAGE2_RESULT.md`
- `docs/pm/checker_action_policy_01/design_02.md` §1、runnerの①実装(`OPEN233_STRUCTURAL_REWRITE_RULES`、4照合、主体部分集合)、`er052_open233_stage2_w1w2_test_01.py`と①のテスト
- 台帳の実体一覧の構造(replay対象記事の台帳JSON)

## 作業
1. `docs/pm/checker_action_policy_01/preregistration_T2.md`(時刻付き)。合否ライン=規則違反0件/構造要素由来STOP≤1件(7対象×3反復=21試行中、件数)/盲点2種(一般名詞の主体入替・一人称枠消失)の解消=再現テストで0件/AI→Muse型の正しい具体化の誤却下0件/削除文0件/費用≤¥25。
2. ①v3実装(`OPEN233_STRUCTURAL_REWRITE_RULES=2`でv3、=1は現行v2のまま): (a)主体の役割クラス写像(人/AI・システム/組織/利用者・公衆/その他)を台帳実体一覧+小辞書で決定論付与。型が無ければ台帳ごとに1回だけLLMで型付けしキャッシュ(`v3/entity_class_cache/<ledger_sha>.json`、費用記録)。(b)照合1=出力側の主体クラス集合⊆元のクラス集合(台帳登録実体が元クラスの具体例なら許可=AI→Muse可。クラスをまたぐ入替=AI→humanは却下。辞書に無い一般名詞の新規導入は却下)。(c)語り枠保持=元のタイトル・HookにI/you/we/問いかけ(?)があれば出力にも残る(決定論)。(d)既存の極性・数値・形式照合は維持。(e)不通過→再生成1回→不通過なら元のまま+`kept_original_quality_record`(BLOCKING未修正の出口は作らない=M4。ladder枯渇時は既存STOP経路のまま)。
3. 単体テスト: 盲点2種の再現fixture、AI→Muse許可、1語追加許可、v2/v3/OFFの分岐。既存テスト全件PASS。
4. replay: 段階2と同じ7対象×3反復、v3でRewrite→4照合→Recheck。違反件数、STOP件数、盲点再現0か、誤却下、削除文、Checker由来の新規NG(目視)、費用。段階2のv2結果と並べた表。
5. `er052_output/open233_stage2_01/v3/T2_RESULT.md`(事前登録照合、PASS/FAIL、限界)。
6. T-0: 本委任文保存+check.json。

## 報告
12行以内: v3の規則要点、テスト件数、21試行の違反/STOP/盲点/誤却下/削除/新規NG、v2との比較、PASS/FAIL、費用、ファイルパス。
