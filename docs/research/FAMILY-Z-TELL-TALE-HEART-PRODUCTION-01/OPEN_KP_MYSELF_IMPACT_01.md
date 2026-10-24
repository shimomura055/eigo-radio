# OPEN_KP_MYSELF_IMPACT_01(FZTTH 委任_04 案B影響分析、2026-10-24)

変更: `er003_key_words_canonicalization.py` の閉じた語彙表 `_PERSON_DEPENDENT_TO_GENERIC` へ `"myself": {"oneself"}` を1行追加(yourself/himself/herself/themselves→oneself と同系のデータ補完。Prompt・正規表現・閾値・Gateは不変)。

## 経緯
委任_03のStd KP再選定で `sure of myself` が「myself未登録」で構造INVALID(outer_retry_log attempt1)。他の-self形は表に既存、myselfのみ欠落。

## 影響分析(API 0)
1. 参照箇所: 表は er003_key_words_gloss_alignment.py:237/324(`_CONCRETE_PERSON_EN`はmyselfを既に含む=不変、`person_generalization_pairs`はmyself→oneselfの組を新たに返し得る)、er105_kp_fulltext_selector_01.py:676(`_token_pair_ok`)、er112_kp_gm_poss_04.py(表を退避/復元、my/our専用)。
2. 既存test全PASS(.venv python): er003_test_key_words_canonicalization 66→67(追加1件)OK / gloss_alignment 70 OK / canonicalization_dangling_span 20 OK / kp_possessor_roles_wiring_01 57 OK / min_unit 78 OK / er112_kp_gm_poss_04_test_01 rc=0。
3. 保存KP entry replay(スクリプトは作業用、repo外scratchpad): 全 `keywords_canonicalized.json` 934ファイル・3,793 item(X/Z/他)に対し `_is_valid_person_generalization` と `person_generalization_pairs` を表変更前後で比較 → **結果変化0件**。(Z『20年後』のcouldn't bring myself to…は旧artifactでkey=displayのまま=変化なし)
4. 他の-self形(保存itemのdisplay_phrase内): itself 1 / yourself 18 / oneself 2 / herself 4。いずれも今回対象外(myselfのみ。itself→oneself等は意味的変更の恐れがあり追加しない)。ourselvesも今回追加しない。
5. 挙動: myself→oneselfのみ許可(myself→someoneself等や他語への置換は不許可のまま)。flag不要(既存表のデータ追加)。Production影響=今後KP選定でmyself含むKPがINVALIDにならず一般形oneselfで受理され得る。
