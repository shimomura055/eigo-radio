# 事前登録 T2(①v3、OPEN-233-CHECKER-ACTION-POLICY-STAGE2-01 委任_03)
登録時刻: 2026-10-08 00:42(replay実行前。この後ライン・数値は変更しない)
位置づけ: Trial/DEV。Production変更なし。②(`OPEN233_STAGE2_READER_BELIEF`)はOFFのまま(打ち止め)。

## 対象・条件
- 対象=段階2と同じ7対象(`eval/stage3_targets.json`、構造要素にBLOCKING finding)×3反復=21試行。v3(`OPEN233_STRUCTURAL_REWRITE_RULES=2`)のみ実API。v2(=1)・OFFの結果は段階2の保存値(`replay_dev/stage3_rewrite/`)を比較に使う。
- 4照合+語り枠保持は決定論。Recheckは段階2と同じ(W1/W2 ON、構造要素の前後対つき)。

## 合否ライン(件数で判定、全てPASSでPASS、1つでもFAILならFAIL。CONDITIONALは設けない)
1. 規則違反0件(受理された出力のうち、4照合・語り枠保持に違反するもの=0。判定は事前登録後の独立再照合=決定論の再実行と目視)。
2. 構造要素由来STOP(ladder枯渇)が21試行中**≤1件**(件数)。
3. 盲点2種の解消=再現テスト(単体fixture: `The AI makes the call.`→`The human makes the call.`、タイトルの一人称枠消失)で却下**かつ**実replayの受理出力に再発**0件**。
4. AI→Muse型の正しい具体化(元に一般名詞、出力が台帳登録の具体例)の**誤却下0件**(単体fixture+実replayの却下理由の目視)。
5. 削除文0件(21試行の削除文数合計、Hook最終手段削除含む)。
6. 費用≤¥25(型付けLLM・Rewrite・Recheck合計、¥22でSTOP)。

## 補足(判定の機械適用)
- 「Checker由来の新規NG」(主体・極性・数値の変化)は目視で列挙して報告するが、ライン外(PASS/FAILには含めない)。ただしライン1の「規則違反」に該当する変化があればライン1。
- 21試行はサンプリング揺れを含み、N小。有意差は主張しない。
