# OPEN517_DESIGN_02(OPEN-517是正設計の改訂。Opus条件Cレビュー反映。JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_06、2026-10-25。DEV/proto・API 0・Production変更0)
`OPEN517_DESIGN_01.md`(凍結・本文は変更しない)の**事実誤認の訂正**と**F2のv4定義**を記す。Opusレビュー原文=`OPUS_REVIEW_01_OPEN517.md`(逐語)。評価=`OPEN517_EVAL_02.md`、適用計画=`OPEN517_APPLY_PLAN_01.md`。
## 0. Opus所見の採否(Fable判断2026-10-25: M-1〜M-5・R-1〜R-7すべて採用)
| 所見 | 反映先 |
|---|---|
| M-1 skipの出自の事実訂正 | 本書§1(DESIGN_01 §1・OPEN-517・報告文の訂正) |
| M-2 弱い読み(なのか/ようか/とお)の置換候補除外+単調性ガード | proto v4 V4-1/V4-2、test `M2_NEG`・`test_basis7_monotonic_guard_*` |
| M-3 語境界(長いかな数詞の前半/後半)・最長一致 | proto v4 V4-3(同unit逆引き表による等価判定)、test `M3_NEG` |
| M-4 適用範囲は明示引数、negation_diffは元テキスト | proto v4 V4-4(`kana_unify`)、test `test_basis7_negation_uses_original_text`・`..._f2_off_for_primary_ng_and_secondary_gates` |
| M-5 合成負例一式=基準7 | `OPEN517_PREREGISTERED_02.md` 基準7、`proto_value_gate_fix_04_test_01.py`(19件) |
| R-1 未知データ | `collect_unknown_pool_02.py`、`OPEN517_EVAL_02.md` §3 |
| R-2 過去公開物監査 | `open517_public_audit_01.py`、`OPEN517_PUBLIC_AUDIT_01.md` |
| R-3 適用後初回runの集計 | `OPEN517_APPLY_PLAN_01.md` §6 |
| R-4 DEMOTEはSecondary stub | `OPEN517_EVAL_02.md` §6-3、PREREGISTERED_02 基準10 |
| R-5 適用手順の抜け | `OPEN517_APPLY_PLAN_01.md` §3〜§5 |
| R-6 parity testの意図差分 | `OPEN517_APPLY_PLAN_01.md` §3(parity) |
| R-7 助数詞表外(晩等)は別OPEN | `OPEN517_APPLY_PLAN_01.md` §7、OPEN_ITEMS新規行 |
## 1. DESIGN_01 §1「skipの出自」の訂正(事実)
DESIGN_01 §1は『skipの出自=`IMPLEMENTATION_02b.md:19`のSonnet設計判断。READING_MATCH個別のユーザー承認原文は未発見』と書いたが、**不正確**。正しくは:
- skipの設計根拠は、承認済み設計追補`er058_output/unified_all_roles_production_wiring_01/DESIGN_02_ADDENDUM_01.md:65`(§1-3)「最終ANDゲートは、承認済みのequivalence(`HOMOPHONE_MATCH_NUMBER_EXCEPTION`、Tier1 diff-anchored、**読み一致**)で既にPASSと確定した結果を再否定しない。再否定が起きると承認済み救済が値ガードで無効化されるため。」
- これは前回Opus条件Aレビュー(`OPUS_REVIEW_A_01_VERBATIM.md:43`)の推奨を**Fableが`OF-AUW-01`として採用**したもの(同追補§0の採否表L11、`DECISION_LOG.md:21653`「条件A…採用14(01,02,…)」。見出しは`DECISION_LOG.md:21645`「Fable判断で採用した技術決定(ユーザー原文の範囲内。新仕様の追加ではない)」)。`CURRENT_SPEC.md:2850`は追補を「正本設計(DESIGN_01と食い違う場合は追補優先)」と位置づける。`IMPLEMENTATION_02b.md:19`はそれを**実装しただけ**。
- **ユーザーの個別承認の有無**: ユーザー原文(`docs/pm/delegation_log/2026-10-15_ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01_01.md`)は管理ID全体を`APPROVED_FOR_PRODUCTION`としたが、`読み一致`のskipには言及がない(同原文をGrep: `読み一致`/`READING_MATCH`0件)。一方、原文L97は「数値・否定などの明確な重大内容差を誤採用しないことを優先する。保護すべき差異を警告だけで無条件に解放する仕様にはしない」と明記。つまり**追補L65の『読み一致をskip』はFable採用の設計判断(ユーザー個別承認なし)で、かつユーザー原文L97と緊張関係にある**。
- F1の位置づけ(Opus): `CURRENT_SPEC.md:2855`「採用しようとする転写すべてに値ガードDIFF・否定差が無いことを独立に再確認する」とコードが矛盾 → 11-8不具合判定T1。合格範囲を狭める(より安全な)方向で、上位のユーザー原文へそろえる是正。**ただし**追補L65(Fable採用・前回Opus推奨)の撤回を伴うため、ユーザー承認必須ではないが報告必須(追補L65との矛盾、前回Opus推奨を今回撤回する方向、再生成・HR Lock増のリスク)。Fableが追補L65を『ユーザー承認済み仕様』と判断する場合は仕様変更=ユーザー判断(本書の事実確認では個別承認は見つからない)。
- **L65の元の理由の手当て**: 『承認済み救済が値ガードで無効化される(誤NG防止)』はF2が受け持つ(正しい読みのかな書き数詞は値同一と判定してPASSを維持)。適用時のSSOT更新案=`OPEN517_APPLY_PLAN_01.md` §5。
## 2. F2 v4(最新定義。DESIGN_01 §2のF2をこれで置換)
`proto_value_gate_fix_04.py`(sha `19aea160…`)。規則(汎用、ID特例なし):
1. 対象=Primary PASS(根拠READING_MATCH)の最終ゲートのみ。明示引数`kana_unify=True`で有効(呼出回数に依存しない)。Primary NG(P1)とSecondary gateでは常にOFF。`negation_diff`は常に置換前の元テキストで判定。
2. 期待読み表(er066 Trial `_cands`)の読みのうち、`WEAK_KANA_NUMERALS`(なのか/ようか/とお)の読み、および同unit内で値が一意でない読みは候補から除く。
3. 置換対象=F2前のguardで『相手側atomが未対応(drop)、または別のかな数詞atomと誤対応(単位違い等)だった』ものに限る。
4. 一致したかな列が、同一unitのより大きい数詞の読みの一部(直前/直後8文字までの連結が別値の読み、または直後が拗音小字)なら置換しない。既存atomを内包する候補(`みっか`⊂`みっかかん`、`よっか`⊂`にじゅうよっか`、`いつか`⊂`いつかかん`)は吸収して置換する。
5. 統一後に『F2前の非EQUAL pair(置換に対応するpairを除く)』が同じ(src,hyp,verdict)で全て残らなければ、F2前の結果を採用(単調性ガード)。
6. 統一前の警告を併合し、統一で認識した不規則読み署名にはJA_NUMERIC_IRREGULAR_READING警告を付与(v3と同じ)。
- 期待読みに無い読み(`さんにち`・`いちふん`・`さんほん`)は置換されずNG/DEMOTEのまま(2026-10-11の不規則読み保護は維持)。
## 3. 影響・リスク(DESIGN_01 §4からの更新点のみ)
- 実コーパス(既存771+未知493)での判定変化はv3と同一(13件、正常NG化0)。未知データは値違い・かな数詞を含まず検出力の検証にならないため、合成負例(基準7)と系統スイープで補完(`OPEN517_EVAL_02.md` §3・§5)。
- 過去公開物: 該当0件(`OPEN517_PUBLIC_AUDIT_01.md`)。ユーザーへ遡及是正を依頼する事項なし。
- **再利用guard**: `er078_reuse_value_guard_01.py`は再利用前に保存転写を現行judgeへ通し、`final_gate_value_diff`等なら再生成へ回す。F1適用後は『READING_MATCHで過去PASSした値違い音声』が再利用時にblockされ得る(監査上は該当0なので増分はほぼ無し)。
- 再生成・HR Lock増: 真の値違いのみ(正常143件・未知96件でNG化0)。最終slotでも値DIFFが残る真の誤読だけがHR Lockへ入る。
## 4. 新規に見つかった既存の限界(F1/F2無関与。別OPEN候補)
(1)`KANA_NUMERALS`正規表現に語境界が無く、`にじゅうよっか`内の`よっか`を4日atomと拾う(原稿`4日`↔`にじゅうよっか`が現行からEQUAL=PASS)。(2)弱いかな数詞(`なのか`/`ようか`/`とお`)を含む文は値ガードが`UNKNOWN`で素通し(原稿`6日`↔転写`なのか`が現行からPASS)。(3)助数詞表外(`晩`等。R-7)。いずれも現行Productionに既存で、F1/F2で悪化しない(F2前の結果と同一をtestで固定)。登録=`OPEN_ITEMS.md`新規行(分類=既知の限界/修正へ進む候補。`OPEN517_APPLY_PLAN_01.md` §7)。
