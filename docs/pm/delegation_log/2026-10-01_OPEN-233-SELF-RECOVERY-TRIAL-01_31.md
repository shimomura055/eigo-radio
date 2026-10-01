# 委任ログ: OPEN-233-SELF-RECOVERY-TRIAL-01 委任_31(2026-10-01)

## 1. 委任内容(要旨)

rep16の残3点の是正と再確認。広い29件Trialは禁止。Guardrail¥10。

## 2. 実施内容

### Part1(¥0、是正+unittest)

(a) 主体置換ガードの常時評価: `classify_problem_kind`の優先順位
(term_scope>actor)により、changed_scope/changed_actorが同時に真の
claimで主体置換ガードが一度も発火しない盲点(委任_30で発見)を是正した。
`single_text_rewrite`/`paired_rewrite`両方で`problem_kind == "actor"
and`条件を削除し、常時`actor_rewrite_guard_ok`を評価するよう変更した。
unittest 1件でTrial C期待2の実データ(users→employees)が却下される
ことを確認した。

(b) Hookセクション境界拡張+body rubric V5: neg1(「Meta had run a test
that caused exactly this surprise.」)はHook導入文の締め文であり、
確認済みの出来事から自然に導ける演出のためRewrite不要とFableが判定。
`detect_claim_section_type`が段落①のみをHook候補とし段落②を無条件に
bodyへ分類していたことが根本原因。新設`_hook_paragraph_block()`で、
段落②が1文のみ・数字を含まない場合に限りHookへ含める決定論ヒューリス
ティックを実装した。実fixture 5件で実測し、neg1のみ該当・他4件
(hormuz/neg3/meta_run03_standard/bgroup_B3)は非該当のまま(Safety
回帰なし)を確認。body rubric側にも防御層(`MISCONCEPTION_PRINCIPLE_
TEXT_V5`)を新設し、昇格前にSafety-critical 8claim(B3含む)をStage2
のみ・n=1で再確認し誤降格0件を確認した(¥1.6243)。unittest 8件新規
(Hook境界4件・section_type更新1件・actor guard統合1件・V5 rubric 3件)。

### Part2(rep17、¥3.1313)

`neg1_meta_b3prod_a2`/`neg3_hormuz_prodrunner_b1b`をStage1 fresh・n=2
で再実行した。両instanceともStage4到達0・false PASS 0。neg3は①単語・
接続詞水準のみで解消。neg1はStage1(fresh、非決定性)が今回Hook/
締め文/usersクレームを検出せず、別のbody claimを検出してQUALITYへ
downgrade(Rewrite 0件という結果自体は目標どおり)。本委任の主目的
(Hook境界拡張の効果)はこの特定の実行では直接再現しなかったため、
実fixtureへの¥0直接確認(`detect_claim_section_type`)で構造的な効果
を別途確認した(Hook導入文・締め文ともsection_type="hook"、是正前の
締め文は"body")。

FAILは発生しなかったため、小修正1回・追加予算の発動はなし。

### Part3(記録)

design書§4-24・§9-1㉑、REPORT§29(A〜E対応表)、DECISION_LOG新規
エントリ(委任_30のrm違反開示+本委任中の`unittest discover`使用の開示
を含む)、OPEN_ITEMS(OPEN-233行追記)、読み比べページ更新
(`er052_open233_self_recovery_rewrite_compare_page_rep17_01.py`、
rep16版は`index_rep16.html`へ保存)を実施した。

## 3. 確認事項(Fable/ユーザーへ)

- Phase 2(10〜20実記事規模)の新規テーマ選定(PM_GOVERNANCE§13)。
- 広い29件規模Trialへ進めるかの判断。
- (開示)委任_30のrm違反、本委任中の一時的な`unittest discover`使用。
  いずれも実害なし(他委任の証跡を破壊・汚染していない)が、governance
  違反として記録する。

## 4. 費用・Status

本委任合計¥1.6243(Safety V5再確認)+¥3.1313(rep17)=**¥4.7556**
(Guardrail¥10のうち、残¥5.2444)。
Status=`HOOK_BOUNDARY_ACTOR_GUARD_FIXED_REP17_N2_STAGE4_ZERO_PARTIAL_
CLAIM_COVERAGE_DUE_TO_STAGE1_NONDETERMINISM`。詳細:
`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`§29、
`docs/pm/design_open233_self_recovery_flow_01.md`§4-24/§9-1㉑、
`DECISION_LOG.md`2026-10-01委任_31エントリ、
`er052_output/open233_element_trial_safety_control_03/`、
`er052_output/open233_self_recovery_flow_runner_01_rep17/`。
