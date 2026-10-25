# OPEN_TRACKING_04: Family Y Production立上げ — 未完了事項の追跡(委任_05更新)

管理ID: FAMILY-Y-PRODUCTION-LAUNCH-01 委任_05 / 2026-10-25(JST)。`OPEN_TRACKING_03.md`からの**更新と追加**のみ。正本の追跡先は`OPEN_ITEMS.md`(OPEN-520/484/463。OPEN-520は委任_03所有のため本委任では編集しない=必要な更新は報告で依頼)。分類は11-8(修正へ進む/ユーザー判断要/実害なし)。
ユーザー追加承認の原文: `docs/pm/delegation_log/2026-10-25_FAMILY-Y-PRODUCTION-LAUNCH-01_USER_03.md`(以下「U3」)。台帳=`SPEC_LEDGER_04.md`。

## 1. 既存OTの更新

| ID | 更新内容 | 現Status(2026-10-25 委任_05) | 11-8分類 |
|---|---|---|---|
| OT-27 | 案Bの残存FAIL: U3 §1(選択肢Ⅱ)で**`leak_evidence_memorable`のみのFAIL・本文byte一致・書換えなしに限り個別Human承認で採用**。実装・offline test済み(HUMAN_APPROVAL_CASE_B_01)。他項目FAILはSTOP。実走で本経路が発火した記録は未取得(E-1では案Bは1回判定でPASS) | **CLOSE候補**(実装完了。発火は条件付き=発火時に記録を確認) | 修正へ進む→完了 |
| OT-20 | Gate文言の扱い: U3 §2で`leak_discovery_syntax`の補足一文のみ承認・実装(較正済み)。`leak_tension_reverts_to_research`肯定側(G-1)は承認に含まれず据え置き | 部分解消(discovery_syntaxのみ)。tension_revertsは継続管理 | 継続管理 |
| OT-44(a) | 共通`er020`のY chunk ID解決(`_FAMILY_Y_SEGMENT_PATTERN`へ`(?:_k[1-9][0-9]*)?`追加+自己検査) | **完了**(`y_voice_2_k1`等・既存ID不変test。er117 testのy_除外) | 修正へ進む→完了 |
| OT-44(b) | runnerの`chunk_tts: not_applicable_Y`→`applied_X_method` | 委任_03へ要求(未反映。runner 984/1181行・runner test 118行) | 修正へ進む(次委任) |

## 2. 新規OT

| ID | 種別 | 内容 | Status | 11-8分類 |
|---|---|---|---|---|
| **OT-47** | 発見・開示(Fable判断候補) | 委任文の補足後半「ただし、3人の語りに根拠がない解釈、不要な一般化、研究・調査の説明への逆戻りは引き続きFAIL」を`leak_discovery_syntax`定義に足すと、案Bが`leak_discovery_syntax`で3/3 FAIL(U3 §1の救済条件と衝突、STOPになる)・過去本文のdiscovery FAILが4→10/42へ増えた。ユーザー承認原文の一文のみを採用(discovery FAIL 4→2/42、H2 3/3→0/3、負例3本は3/3 FAILのまま)。Fableが後半の再追加を望む場合は案Bとの衝突を踏まえた再判断(ユーザー承認原文は一文のみ) | 実装はユーザー承認原文どおり。GATE_CALIBRATION_02 | B承認範囲内で自己解決(判断候補はFableへ開示) |
| **OT-48** | 継続管理(実害は未確認) | 補足あり(v1/v2)で、補足なしでは0 FAILの本文に別項目のFAILが散発(v2: 12本36回中7回[補足なし対照0]、別日時データの10本30回中5回[対照1])。n=3で判定器の揺らぎと補足による判定の摂動を判別できない。Closing Gate FAILは既存機構(判定<=3+局所書換え)で扱う範囲 | Y実走のgate_history蓄積で確認(追加の有料較正は必要十分の範囲を超えるため実施せず) | 実害なし(要観察) |
| **OT-49** | 観測(取り下げ) | `er121_family_y_structure_match_test_01.py::NoticeDisplay::test_no_xz_page_in_repo_contains_the_y_notice`が本委任の作業中に1回失敗した(`user_test/family_y_production_sns_age_limit_01/index.html`をX/Zページと判定)が、その後の再実行(同test単体・関連415件)でPASS。他agent(委任_03)の公開ページ作業が進行中だった一過性と推定(原因は未確認)。再発した場合は委任_03/02Bの領域として扱う | 取り下げ(再発時に再起票) | 実害なし |

## 3. 完了条件の更新

OT-27は上記のとおりCLOSE候補。OT-44(b)(runner表記)・E-1〜E-5・OT-46(公開条件)の残りは従来どおり。`PRODUCTION_WIRED`の検討(判定はFable、ユーザー最終試聴PASSは別Status)は、本委任の変更(案B個別承認・discovery_syntax補足)がProduction runtime evidenceで確認された後。
