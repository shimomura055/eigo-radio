# RUNTIME_EVIDENCE_01(KP-CANON-REVIEW-REQUIRED-FIX-01 委任_01、2026-10-25)

入力: 『告げ口心臓』Std(a2)本文(保存済み`.../the_tell_tale_heart/_bak_pre04/kp_try1/a2/outer_retry/attempt_1/keywords_selector_prompt.txt`の本文部)と、
保存済みの`vulture's`を含む選定(`in heaven and on earth`/`vulture's`/`metal catch`。旧run attempt_3と同じ3件)。
経路: Z Production既定のkp_fn `er062.run_kp_with_outer_retry_fulltext` = X/Z共通 `er003_v1_n3_01_scaffold_generate.run_kp_with_outer_retry`(修正後)。
DEV注入(選定#1のみ保存済み選定を注入)。Production run dirへは書かない。script・生成物: `er026_output/family_z_production_e2e_01/the_tell_tale_heart/_evidence_kcrr1/`(`run_evidence.py`、`summary_{A,B,C}.json`、`mode_{A,B,C}/kp/`、`mode_A_stdout.log`)。

## 旧挙動の実例(修正前、同じ旧run)
`_bak_pre04/kp_try1/a2/keywords_canonicalized.json`: `overall_status=REVIEW_REQUIRED`、`vulture's`(QA FAIL: standalone_natural_unit/reusable_other_context/standalone_comprehensibility)がそのまま最終KPとして**自動採用**されていた(外側retry 3周のうちattempt 2・3はREVIEW_REQUIREDで、attempt 2が採用)。

## mode A(実API最小。選定#1=注入、canonicalization/再選定/gloss alignment/redundancy=実API)
`summary_A.json`(所要214秒):
- 外側1周目: `vulture's`を含む選定 -> canonicalization = **CANONICALIZATION_REVIEW_REQUIRED**(review_required_ranks=[2])。旧挙動ならここで採用されていた。修正後は不採用、`keywords_canonicalized.STALE_attempt1.json`へ退避、`vulture's`が理由付き除外語に追加(`excluded_phrases_added=["vulture's"]`)。
- 外側2周目: 除外語付き実再選定(`frozemyblood`系3件) -> CANONICALIZATION_INVALID(既存のINVALID経路。通算failures=2)。
- 外側3周目: `in heaven and on earth`/`sure of myself`->`sure of oneself`/`Pull up the floorboards` -> **CANONICALIZATION_PASS**・REDUNDANCY_PASS -> **PASSのみ採用**(adopted_items 3件すべてqa PASS)。
- 通算failures=2 < max_outer=3 のため、上限内で再選定が収束。

## mode B(API 0。canonicalization応答を旧runの保存済みQA FAIL行[attempt_3]で再生)
`summary_B.json`: 周1 REVIEW_REQUIRED(rank2 `vulture's`) -> 除外 -> 周2は`vulture's`抜きの2件でCANONICALIZATION_PASS -> 採用は`in heaven and on earth`/`metal catch`のみ。`vulture's`は最終KPに入らない。

## mode C(API 0。全itemが保存済み`vulture's`相当のQA FAIL -> 再選定でも解消しない)
`summary_C.json`: 周1 REVIEW_REQUIRED(rank1,2,3) -> 周2・周3は全句除外で選定INVALID -> `final_status=OUTER_RETRY_EXHAUSTED`、`keywords_canonicalized.json`は本名で残らず(`kp_final_exists=false`、`STALE_attempt1.json`のみ)。
X stageは`kp_stage_failure_status`=`KP_STAGE_FAILED(OUTER_RETRY_EXHAUSTED)`、Z stageは`FamilyZE2EStop`(`FAMILY_Z_KP_NOT_PASSED`)で人間確認へ回る(test: `er003_test_kp_review_required_retry_01`)。

## 費用
mode A: 実API約10呼出(選定4[gate内再試行含む]+canonicalization約3+gloss alignment/redundancy約3)。cost loggerを装着していないため実測せず概算 3〜6円(上限10円内)。mode B/C: API 0。
