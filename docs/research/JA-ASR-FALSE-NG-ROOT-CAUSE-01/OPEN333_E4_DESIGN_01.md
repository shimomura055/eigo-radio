# OPEN333_E4_DESIGN_01(E4=便乗PASS是正 / E4-N=E3副作用の整合化の設計。JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_13、2026-10-26)
**区分: 承認済み不具合是正(PM_GOVERNANCE 11-8)の設計。Production適用は本委任の範囲外**(Opusの短縮確認後に別委任)。API 0・実費0円。事前登録=`OPEN333_E4_PREREGISTERED_01.md`、評価=`OPEN333_E4_EVAL_01.md`、適用計画=`OPEN333_E4_APPLY_PLAN_01.md`。

## 1. 結論(事実)
- **Cascadeへ戻す既存の経路は在る。新しい分岐も新しい受理クラスも要らない。** `er011_ja_asr_variant_layer_01.py:304-306` の `_cascade(reason)`(= `ClassificationResultJA("ASR_VALIDATION_UNCERTAIN", …, should_pass=False, should_retry=False)`)は、同じ関数 `try_rescue_before_resolver` のCandidate B/C/D-1(`:314,329,344`)が『濁点差のみ一致=Cascade対象、即PASSにはしない』として既に使っている。E4は、Candidate Eの `_pass(...)`(`:380`)を、cascade_eligible差分が残るときだけ同じ `_cascade(...)` にするもの。
- 戻したあとの流れは既存のまま: `er007_ja_asr_validator_01.py:407-409`(cascade_eligible/non_cascade分類)・`:501-509`(cascade差のみ→UNCERTAIN)と同じ label → adapter `er007_ja_secondary_asr_01.py:551-604`(`is_tcm`でないためA4/A6/保護signalsを作らない)→ 統一judge `er078_asr_unified_judge_01.py:639-662`(Primary NG: P1[値DIFF/否定]→P2[除外表]→P3 Azure 1回)→ Secondaryの許容集合(EXACT/NORMALIZED、ORTHOGRAPHIC_VARIANT_CONFIRMED)。
- E4-Nは**『PASSを広げない振替』にならない**(§4)。実データ1,327行で影響0件、合成のみ。評価の結論は §5。

## 2. 既存の安全条件(E4が戻そうとしている仕様)
- 承認済み: entity_like(両側カタカナ/略語のreplace)と濁点/半濁点のみ差(phonetic_uncertain)は、TTSの内容誤りとして即再生成せず `ASR_VALIDATION_UNCERTAIN` としてCascade(Azure再確認)へ回す(`er007_ja_asr_validator_01.py:307-327,403-409,501-509`、ER-007-JA-ASR-TTS-RETRY-PATH-FIX-01 Part B)。
- 不具合: Candidate Eは `remaining_diffs = [d … if not d["cascade_eligible"]]`(`er011:366`)だけを見て、それが全部『読み候補』で説明できると PASS を返す(`:367-384`)。`content_diffs` に cascade_eligible 差分(カタカナ名の母音違い等)が同居していても、その差は検査されず PASS に便乗する(Eが救う別の同音差=乗り物が、本来Cascadeへ行く差を持ち込む)。E分岐の前に `protected.passed=False`(数字差)でもEに入る経路があり(`er007_ja_asr_validator_01.py:391-395`)、数値entryはE3が先に全差分再検査する(`er011:373-383,418-462`)ため、E4が実際に効くのは **cascade_eligible差分が `content_diffs` に在る = 数値span以外の差が普通に分離されているケース**。
- 実例(HEAD=E3適用済み): `走れメロス`→`走レメラス`(Primary転写)が現行PASS(`open333_e4_eval_01.out.json` real[]、id=`…customb8f0ff16.json:japanese_title`)。

## 3. E4の設計
- 位置: `try_rescue_before_resolver` の Candidate E分岐、E3の拒否判定(`_rej`)の**後**・`return _pass("PHONETIC_MATCH", "(…Candidate E)…")`(`:380`) の**前**。
- 規則: `cascade_diffs = [d for d in protected.content_diffs if d["cascade_eligible"]]` が空でなければ `return _cascade(<理由>)`。理由文に『Candidate Eは救済したが cascade_eligible 差分が未検査で残る』を記す。
- 監視(M-6同形): `protected.candidate_e_cascade_diffs = [(canonical, asr), …]` を記録し、adapterが `asr_judgement.candidate_e_cascade_return` に読取専用で複写(判定不変)。
- rollback定数(env/flag/引数で切替不可、1行): `CANDIDATE_E_CASCADE_DIFF_RETURN = True`(False=HEAD完全一致)。
- fail-closed: cascade判定中の例外は『Cascadeへ返す』(PASSにしない)。`content_diffs`要素に `cascade_eligible` が無ければ cascade 扱い(`d.get("cascade_eligible", True)`)。
- 方向性: 変更は『PASS→ASR_VALIDATION_UNCERTAIN』のみ。Primary段のPASS集合は縮む。最終PASSはCascade(Azure転写が原稿とEXACT/NORMALIZED一致)でしか得られず、不一致ならNG(NG_BOTH)→既存の再生成。
- 新しい受理クラスなし。ORTHOGRAPHIC_VARIANT_CONFIRMED(Primary UNCERTAIN + 読み候補確認)が誤って開かないことは、`er007_ja_secondary_asr_01.py:361-383` の `_orthographic_reading_confirmed` が `any(not d["cascade_eligible"])` で False を返すため(Eの救済対象は必ず non-cascade 差分を1つ以上持つ)構造的に保証され、評価でも受理変化0(`OPEN333_E4_EVAL_01.md` §7)。
- E4(cascade_eligible全般)かE4E(entity_like限定)か: 実測では差が出ない(ひらがなのみの濁点差は、現行HEADで便乗PASSを再現できなかった=§評価 3.2)。承認済み安全条件が『entity_like **と** 濁点差』の両方を明記しているため、仕様どおりの E4(cascade_eligible全般)を採る。

## 4. E4-Nの設計と、見つかった重大な性質
- 設計: 数値entryでE3が『説明できない非数値差』を理由にEを拒否する(`return None`)とき、説明できない差が**全て** cascade_eligible(protected_check_jaと同じ述語: replaceかつ entity_like[両側カタカナ/略語] または 濁点のみ差)で、かつ値ガードが EQUAL/NO_VALUES/AMBIGUOUS なら、拒否ではなく `_cascade` を返す。1件でも非cascade差(しわ→すわ等)・値ガードDIFF/UNKNOWN・helper例外があれば従来どおり拒否。実装はE3 helperの拒否要素に `cascade_eligible` キーを足すだけ(proto_06 `audit_e3_classified`)。
- **事実(評価で判明)**: E4-Nで『拒否→Cascade』になる44行は**全て HEAD で `NG_EXCLUDED / p2_exclusion:A4_C2_HOMOGRAPH`**(統一judgeのP2除外表A4=同形異音候補。2026-10-11ユーザー逐語採用の安全条件、`er078_asr_unified_judge_01.py:148`)だった。つまりE4-Nの実効は『数値entryのA4除外を、Cascadeに振り替えることで解除する』こと。HEADで最初からP3(Azure)に行っていた30行はTRUE_CONTENT_MISMATCH→UNCERTAINのラベル変更のみで最終判定は不変。
- 理由: 数値entryでE3が拒否すると TRUE_CONTENT_MISMATCH になり、adapterが `is_tcm` として `_scg_c2_candidate`(`er007_ja_secondary_asr_01.py:589-590`(`is_tcm`は:567))を計算してA4除外に当たる。一方、非数値entryで同じ状況(カタカナ差+Eが救う同音差)は UNCERTAIN になり `is_tcm=False` なのでA4は計算されずP3へ行く。この差がE4-Nの言う『不整合』の正体で、**E3の副作用ではなく、既存のA4が TCM のときだけ働く構造**に起因する。
- 帰結: E4-Nは『拒否→Cascade』の振替であって Primary PASSは増やさないが、HEADで確実にNG(A4除外で再生成)だった行が、Azure転写次第で最終PASS(PASS_WITH_WARNING)になり得る。**最終PASSの到達可能性を広げるため、依頼の『PASSを広げる変更は不可』には厳密には抵触する**。A4を解除する判断はユーザー逐語採用の安全条件に触れるため、AI単独では決めない(判断候補D、実害が出た場合のみ)。A4を維持する変形(A4に当たる行は拒否のまま)にすると、実効は『30行のラベル変更のみ』で、実データ・最終判定とも変化0=導入する意味が無い。

## 5. 採否の見立て(詳細は評価・QCD)
- E4: 適用推奨(事前登録K1〜K5・K7〜K11を満たす)。実データ4/676行(0.59%)がPASS→Cascade、うち読み違い疑い2・正常等価表記2。
- E4-N: 見送り推奨。実データ影響0件、便益は合成の正常等価表記のみ、効果の本体がA4解除(安全条件への接触)。E4を先に入れ、正式runで数値entryのA4即NG(`p2_exclusion:A4_C2_HOMOGRAPH`かつ canonical に数値、直前にカタカナ差)が実際に発生した場合に再検討する。

## 6. 限界
- 乗り物5種・名前16種の合成負例に基づく。Cascade後のAzure一致率は未測定(API 0)。注入(補足)では『Azureが原稿どおり』→PASS_WITH_WARNING、『AzureがPrimaryと同じ誤り』→NG_BOTHを確認。
- `is_entity_like_mismatch_ja`(`er007_ja_asr_validator_01.py:517`)は `content_diffs` の全要素が cascade_eligible のときだけ True を返す診断関数のため、E4でUNCERTAINになった行(non-cascade差を持つ)ではFalseになる。統一judgeの経路では使われない(`grep`: 呼出元は診断/試験scriptのみ: `er007_ja_cost_latency_projection_01.py:87`、`er058_trial_b_intentional_misread_01.py:160`、`verify_ja_cascade_production_on.py:51`)。
