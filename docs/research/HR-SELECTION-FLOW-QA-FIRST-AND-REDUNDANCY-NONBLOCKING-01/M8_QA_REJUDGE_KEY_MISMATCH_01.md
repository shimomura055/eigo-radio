# M8_QA_REJUDGE_KEY_MISMATCH_01(委任_03A 3節。時間box 1h。read-only調査、API 0)

結論: **原因特定・修正見送り**(OPEN-601登録)。承認済み救済機能の『明確な不具合』ではなく、再判定の設計(承認済みcanonicalization promptの再利用+key一致要求)に起因する構造的制約で、直すには承認済みPromptまたはQA基準の変更が要る(=新仕様。11-8の対象外)。

## 事実(保存済み`kp_candidates.json`の`rescue.canonicalization`を全走査。評価対象=rescue canonicalization段16件)
- REVERT_SURFACE: NOT_REJUDGED 8 / PASS 3、REDERIVE_M1_WINDOW: NOT_REJUDGED 3 / PASS 2 → 11/16=69%が`NOT_REJUDGED`(`error=key_mismatch_or_invalid_fields`)。
- 不一致11件の `llm_key_phrase`(LLMが最初に返した原形key) と `rescued_key`(救済後=本文の表層/活用形のkey):
  take someone's use into account→take our use into account / hold out one's hands→hold out / intercept and destroy→intercepted and destroyed(display側) / go beyond the evidence→goes beyond the evidence / back operations→backs operations / keep heat from escaping→keeps heat from escaping / urge→urging / make more sense than→makes more sense than / take steps→takes steps / take offense→taking offense / last twenty-three strokes→lasted twenty-three strokes(例は run_kpbf_ev_03・run_reselect_01・run_kprescue_ev_01・run_gpg5_y_01_s23f・surname_choice run_02 b1b 等)。
## 原因(file:line)
- `er125_kp_rescue_production_01.py:503`(`build_qa_rejudge_message`): 承認済みfulltext canonicalization promptを無変更で再利用し、救済後keyを`display_phrase`として渡す。このpromptの課題は『display_phraseから辞書形のkey_phraseを導出する』ことなので、LLMは再び原形へ正規化したkeyを返す。
- `:527`(`qa_rejudge`): `_norm_lc(r["key_phrase"]) != _norm_lc(救済後key)` ならQA欄が正常でも`NOT_REJUDGED`。
- 救済(REVERT_SURFACE/REDERIVE)が必要になった元の原因が『LLMの原形keyが本文表層から導出不能』であり、同じpromptで再判定すると同じ正規化が再現する。したがってkeyが原形化される限り構造的に一致しない(PASSの5件は活用形が原形と一致するなど正規化が起きなかったケース)。
## 影響
仕様①(M8: 未検査救済は提示しない)で約7割の救済候補は提示されず補完で埋まる(fail-closed、品質事故なし。候補の多様性が若干減るのみ)。
## 案(OPEN-601)
A 現状維持(推奨。補完で埋まる) / B 再判定専用の比較規則/Promptを新設(救済keyを固定して12項目だけ判定。承認済みPromptの変更=要承認) / C REVERT_SURFACEは本文逐語一致で決定論的に安全なのでQAの一部を免除(承認済みQA基準の変更=要承認)。
