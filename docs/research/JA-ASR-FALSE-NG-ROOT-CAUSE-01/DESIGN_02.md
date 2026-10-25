# DESIGN_02(JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_04、2026-10-25。v1→v2差分・OPEN-517是正案方向)
## 1. v1→v2 差分(事前登録§1の手順準拠)
事前登録`PREREGISTERED_CRITERIA_02.md`§1: 「増分誤PASS 1件でも出たら不合格=原因修正→v2として再凍結→再評価」。v1(`proto_reading_compare_01.py`、sha256 `8799aa60fed66e2d78eea00bb263e99ebf069db83c6fe1d3191d1d96870c1733`)は**変更せず凍結のまま残置**(実行前後で一致を確認)。v2=`proto_reading_compare_02.py`(sha256 `bcb042c651f05c7801b382e51b802a870e1240892d3ae65efc6cdbbca27c6144`、再凍結)。
- 変更点は**1点のみ(V2-1)**: A4(a)=Secondary転写の「値のみ一致」(kind=VALUE_ONLY)を、原稿側atomが不規則読み数詞(Production関数`er078_asr_value_guard_01.is_irregular_sig`該当=日(1〜10・14・20・24日、末尾4/7/9)・人(1,2人、末尾4)・20歳・ツ系・月/時の末尾4/7/9)のとき救済せず、NG維持(`blocked_by=A4a_irregular_reading`)。`pron_value_equivalence(..., side="secondary")`のときだけ有効。**Primary層(side既定"primary")はv1とコードパス同一**(Productionの`_numeric_value_equivalence`が既に受理する対を失わない。test: N-1+正例+負例+月題+Melos 200超対でPrimary判定がv1と完全一致)。
- 理由: ASR転写の算用数字/漢数字(`3日`/`三日`)からは読み(みっか/さんにち)の正誤が判別できない。不規則読みを持つ値は「値一致=読み一致」と言えないため、Secondaryの値一致だけでPASSさせない(厳格化方向。緩和ではない)。N3-21(`三日待った`/音声`さんにち`/Azure`3日`)が根拠。
- 判定(関数はProduction関数を直接import、複製なし): `vg.extract_atoms_ja(canonical_text)`のkind=="num"のatomを`vg.is_irregular_sig(value, unit)`で判定。
- 影響しない範囲(test固定): 否定/値ガード/A7/C2の順序、Primary側、A4(b)(PRON)、不規則でない値(`8,900`↔`8900`、`十一日`↔`11日`等)のA4(a)受理。
### unified diff(v1→v2、`diff -u`)
```diff
--- proto_reading_compare_01.py	2026-10-25 16:29:24.344252300 +0900
+++ proto_reading_compare_02.py	2026-10-25 19:48:23.489830100 +0900
@@ -1,4 +1,9 @@
-# JA-ASR-FALSE-NG-ROOT-CAUSE-01 Phase 3 prototype v1 (research/DEV only; NOT imported by Production; API 0).
+# JA-ASR-FALSE-NG-ROOT-CAUSE-01 Phase 3 prototype v2 (research/DEV only; NOT imported by Production; API 0).
+# v1 (sha256 8799aa60fed66e2d..., proto_reading_compare_01.py, 凍結・変更なし) からの差分 = 委任_04 の1点のみ:
+#   V2-1: A4(a)=Secondary転写の「値のみ一致」(kind=VALUE_ONLY)を、原稿側atomが不規則読み数詞(Production `er078_asr_value_guard_01.is_irregular_sig` 該当)
+#         のとき救済しない(NG維持)。side="secondary" 指定時のみ有効。Primary層(side="primary"既定)はv1と完全に同一(Productionが既に受理する対を失わない)。
+#   動機: N3-21 原稿`三日`/音声`さんにち`/Azure`3日` の増分誤PASS(事前登録§1不合格)。ASRの漢数字/算用数字表記から不規則読みの正誤は判別できない。
+# 以下はv1ヘッダ(経緯):
 # v0 (sha256 c3e61412c7adaada..., 凍結; 退避=proto_reading_compare_01_v0_frozen.py.txt) からの差分 = Opus条件Aレビュー必須修正 M1/M2/M3/M7:
 #   M1: 救済しない条件を追加 = A7 登録読み不一致(expected_readings) / C2 同形異音候補(順方向=Production `_scg_c2_candidate`、
 #       逆方向=ASR側の漢字spanが複数読みを持ち原稿の読みがその1つ)。Primary・Secondaryとも同じ関数を使う。
@@ -86,7 +91,8 @@
 
 
 def pron_value_equivalence(canonical_text: str, asr_text: str | None, cls=None,
-                           expected_readings: dict | None = None, require_value_atoms: bool = False) -> V1Result:
+                           expected_readings: dict | None = None, require_value_atoms: bool = False,
+                           side: str = "primary") -> V1Result:
     """案A v1: Primary/Secondary共通の判定(純関数、API 0)。clsはclassify結果(None=内部で計算、resolver=OFF)。"""
     if asr_text is None:
         return V1Result(False, None, "asr_none")
@@ -123,6 +129,11 @@
     if c == a:
         if sec._has_negation_ja_text(cf) != sec._has_negation_ja_text(af):
             return V1Result(False, None, "negation_after_value_form", blocked_by="negation")
+        if side == "secondary" and has_atoms:           # V2-1: A4(a) 不規則読み数詞の値のみ一致は救済しない
+            irr = [a.surface for a in vg.extract_atoms_ja(canonical_text)
+                   if a.kind == "num" and vg.is_irregular_sig(a.value, a.unit)]
+            if irr:
+                return V1Result(False, None, f"a4a_irregular_reading_value:{','.join(irr)}", blocked_by="A4a_irregular_reading")
         cause = "A1_value_notation" if has_atoms else "unexpected_surface_equal"
         return V1Result(True, "VALUE_ONLY", "surface_equal_after_value_form", VALUE_LABEL, warnings, cause)
     p_with, p_plain = pron_hira(c), _tag_pron(c, False)
```
## 2. 既知の残存リスク(v2でも残る。隠さず記載)
`is_irregular_sig`はProductionの閉集合(日・人・歳・つ・月・時)で、連濁/音便系(三本=さんぼん、六百=ろっぴゃく、三百=さんびゃく、三階=さんがい、一分=いっぷん)は含まない。API 0確認: A4(a)は`三本ください↔3本ください`・`六百円↔600円`・`三百円↔300円`・`三階↔3階`を**依然受理**する(`一分↔1分`・`八日`・`十日`・`二十歳`・`三日`は不受理)。これはPrimary層が既に同じ値のみ一致(`NUMERIC_VALUE_EQUIVALENT_MATCH`、N3-18が既存誤PASS)を受理しているProduction既存の盲点と同型で、仕様L2865(Secondary受理にも値等価を含む)に沿ったSecondary側の整合。N-3実音声(三本・六百・一分)では増分誤PASSは出ていない(TTSが正しく読むか、Primaryが既に通していたため)。**範囲拡大(連濁/音便系を除外)はv3案**として記録のみ(今回は実装せず。事前登録は厳格化可・本件は基準を満たすため不要)。
## 3. OPEN-517 是正案(実装しない。別委任用の設計方向)
### 3-1 現状(件数・型別。N-3 30 clip実音声、既存誤PASS 16件、`eval_api0_v2_01_phase3.out.json`)
| 型 | 件数 | ID | 検出可否(テキストのみ) |
|---|---|---|---|
| 値の最終確認skip(PHONETIC_MATCH) | 1 | N3-02(音声`八万九千`=89,000/原稿8,900) | 値ガードDIFFで検出可 |
| 近音しわ→すわ(PHONETIC_MATCH、Variant Layer Candidate Eの漢字候補総当たり) | 1 | N3-07(`月の巣は`) | 値ガードでは不可(EQUAL)。別規則が必要 | **【2026-10-25 委任_12訂正】この分類(『Candidate Eの漢字候補総当たり』=承認済みEの設計どおりの過許容)は不正確。N3-07は『実装不具合』(protected_check_ja[er007:258-261]が数字の異なるopcodeに糊付けされた非数値差を content_diffs へ入れず、Eが未検査のまま通した検査漏れ)であり、し↔すを同一視する規則はEに存在しない。区分と是正(E3)は `OPEN333_DESIGN_01.md`/`OPEN333_DESIGN_02.md`、Opus所見は `OPUS_REVIEW_01_OPEN333.md`。OPEN-333本来(同形異音の過許容)とは別原因。**
| ASR表記から正誤判別不能(同形異音: 今日/市場/行った/一日/人気、連濁: 三本/六百、不規則: 二十歳、助詞: 月は/町へ/私は、N3-26わ/N3-27え、N3-24町へ) | 14 | 09,10,11,12,14,16,18,20,22,23,24,25,26,27 | ASRが原稿と同じ表記/同読み表記を書くため文字からは不可(ASRの限界、本層の対象外) |
- 「承認済み安全条件(値・否定の最終確認)との矛盾」と言えるのは**値最終確認skipのN3-02(+N-1の`三日間`/`三日目`・`3~5日`/`35日`型)**。N3-07は近音(Candidate E)の別問題。残り14件はASRの盲点で矛盾ではなく既知の限界(O3)。
### 3-2 該当規則の箇所
- 分類`PHONETIC_MATCH`の生成: `er007_ja_asr_validator_01.py:441,502`(content_diffs空/全文読み一致)およびVariant Layer Candidate E(`er011_ja_asr_variant_layer_01`、漢字候補読み総当たり)。
- adapterが`equivalence_basis="READING_MATCH"`を付与: `er007_ja_secondary_asr_01.py:427,603`。
- 最終ANDゲートskip: `er078_asr_unified_judge_01.py:68-73`(`APPROVED_EQUIVALENCE_BASES`に`READING_MATCH`)、`:526-530`(approvedなら`final_gate.applied=False`)。**これにより値DIFF/否定差の再確認が走らない**。
### 3-3 是正案の方向
`READING_MATCH`のPASSでも、最終ANDゲートの**値ガード(DIFF)と否定差は常に適用**する(値の最終確認を`PHONETIC_MATCH`より優先)。`READING_MATCH`をAPPROVED基底から外すのではなく、読み一致根拠のPASSに対して値/否定チェックのみ実行する形(他の承認根拠のskipは触らない)。
### 3-4 API 0影響調査(`open517_value_gate_probe_01.py`、実行済み、Production無変更)
現行PrimaryがPHONETIC_MATCH/READING_RESOLVED_MATCHでPASSした155件(P-4実attempt 133・N-1 19・N-3 3)に値ガード/否定差を当てた: **NGに変わるのは10件**。内訳=既知の負例9(N-1の`三日間`↔`三日目`×4、`3~5日`↔`35日`×2、`一分`↔`いちふん`[AMBIGUOUS]、`三日`↔`さんにち`、N-3のN3-02)+**実attempt1件(comment_4_attempt1: `いちばん低い`↔`一番低い`、値ガードがDIFF判定)=正常音声の新規誤NG**。
- 含意: 単純に値ガードを適用すると**正常音声1/133(0.75%)を誤NGにする**。`一番`/`いちばん`(順位・最上級語。数詞でない)の値atom誤認の除外が必須(同種語の洗い出しを含む)。この除外をつけた上で、HR/retry増加0をP-4で担保する必要がある。
- API 0で検証可能: 保存転写(P-4 421・N-1・N-3・Phase 3転写)で判定の前後差を完全に再現できる(上記probeと同じ手法)。有料API 0・実費0円。
### 3-5 見積・体制
別委任1件(設計+実装+test+回帰、API 0、費用0円)。Productionのゲート変更のため、条件A(新構造ではないが既存Gateの意味変更)に準じOpus軽量レビューを推奨(Fable判断)。範囲=値ガード適用+`一番`系除外+N3-07(Candidate E近音)の扱いは別調査(Candidate Eが承認済み仕様の範囲かの確認が先)。
