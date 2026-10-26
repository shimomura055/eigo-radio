# SPEC_CHECK_01: KP候補Gate除外の「修正救済」方式 既存仕様照合(read-only・API 0・2026-10-26)

管理ID: KP-GATE-EXCLUSION-RESCUE-DESIGN-01 委任_01(調査・設計のみ)

## 0. PM_GOVERNANCE 21節 A/B/C 分類

| 論点 | 区分 | 根拠 |
|---|---|---|
| Gate除外された候補を「修正→既存Gateで再検査→HR候補へ残す」救済フロー全体 | **C: 新規(既存仕様なし・過去Trialなし)** | CURRENT_SPEC/DECISION_LOGに該当記述なし(Grep `救済`/`rescue`)。PM_GOVERNANCE 11-8「新しい処理方式・Gate・検査の追加」=新設/拡大に当たる=ユーザー判断事項 |
| 救済の部品(「invalidなら決定論でdisplayへ戻す」) | **A: 既存仕様あり(同型の先例)** | `er105_kp_fulltext_selector_01.py:927-1002 postprocess_possessor_roles`(UDR #173② `APPROVED_FOR_PRODUCTION` 2026-10-24、DECISION_LOG.md:50)。「revertのみ・API 0・revert後にvalidatorを通らなければ無変更・新しいINVALIDを作らない」。hook=`er003_v1_n3_01_scaffold_generate.py:502-507`(`run_canonicalization_gate(postprocess=)`) |
| Gate除外のitem単位化(INVALIDならitemを除外し残りで再実行・全体PASSのみ受理) | **A: 既存仕様あり** | Opus M-7(a) `docs/research/KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01/OPUS_REVIEW_01.md:50-52`、実装 `er119_kp_candidates_01.py:226-246` |
| 数合わせ・補充(8件に届かないことの扱い) | **A: 既存(補充なし・shortfall受容)** | KP_CANDIDATE_COUNT_CHECK_01.md:3,18-31。ユーザー原文 `2026-10-25_KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01_USER.md:24,32` |
| 過去Trialでの同種検討 | **該当なし** | 救済方式のTrialは未実施。OPEN-456 F1(`KP-OUTER-RETRY-SAME-PHRASE-FIX-01`)は「同じ句を再選定させない」方向(除外の累積)であり救済ではない |

## 1. 承認済み規則 / 出典 / 実装箇所 / X・Y・Z適用

| 規則 | 出典(ファイル:行) | 実装箇所 | X | Y | Z |
|---|---|---|---|---|---|
| 5語以下(1〜5語) | Prompt 2「5語以内(絶対条件)」(`er105_kp_fulltext_selector_01.py:35 KP_WORDS_MAX=5`)、`er003_key_words_canonicalization.py:214-215` | 選定段 `er105.validate_and_resolve:236-238`(実語数)、canon段 `er003_kc.validate_canonicalization_item:628-631`(key語数) | ○ | ○ | ○ |
| 本文対応(本文の連続一致) | Prompt 2「本文一致(絶対条件)」 | `er105.validate_and_resolve:243-248`(`locate_phrase`) | ○ | ○ | ○ |
| Rule7(source_span内の連続部分文字列/無変更/人称一般化/基本形化[fulltextのみ]以外を拒否) | `er003_kc.validate_canonicalization_item:605-621` | 同左 | ○ | ○ | ○ |
| 人称代名詞・所有格の一般化(閉じた語彙集合の1対1置換) | DECISION_LOG.md:10185-10205(`_is_valid_person_generalization`、PRODUCTION_WIRED) | `er003_kc:484-503` | ○ | ○ | ○ |
| 所有格role条件付き受理+A-1参照語不定化(revertのみ後処理) | DECISION_LOG.md:50(委任_20、UDR #173②/#169) | `er105:812-827 find_inflection_window`、`:927 postprocess_possessor_roles` | ○ | ○ | ○ |
| **活用形→基本形の1対1置換(fulltext限定のRule7例外)** | CURRENT_SPEC.md:1997(「基本形化=活用形→基本形の1対1トークン置換のみ許す決定論validator[先頭または`to`直後の動詞・最終語の複数形、除外表あり]。Rule7の例外であり人物一般化と同型のX/Z限定例外」)、DECISION_LOG.md:88(Fable決定の開示「Rule7に基本形化例外」)、Opus `OPUS_REVIEW_COND_A_01.md:108-122`(P-02(3)(4)/P-04)、`IMPLEMENTATION_DESIGN_01.md:15,72-73` | `er003_kc:529-541 _is_valid_fulltext_normalization`、`:610-614`(`allow_inflection_normalization`)、`:696`(`=_is_ft`)、`er105:670-691 _token_pair_ok`+`:662-667 _guard_ok`+閉表`:577-622` | ○ | ○(下記§2) | ○ |
| 有限助動詞を含まない | `er003_key_words_min_unit.py:260-261 _FINITE_AUX_WORDS`(is/are/was/were/has/have/had/will/would/can/could/should/may/might/must) | 選定段 `er105._legacy_form_reasons:213-222`、canon段 `er003_kc:439-441,627` | ○ | ○ | ○ |
| CMU辞書登録語のみ(代替合格禁止) | CURRENT_SPEC.md:2001(OPEN-458) | `er108_kp_cmu_lexicon_gate_01.py`、`er119_kp_candidates_01.py:87-89,264-267` | ○ | ○ | ○ |
| 数合わせ禁止/TOP 8まで(上限) | `2026-10-25_KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01_USER.md:24,32,38` | `er119_kp_human_review_01.py:49 KP_CANDIDATE_MAX=8`、`er119_kp_candidates_01.py:353 shortfall` | ○ | ○ | ○ |
| 最大8件(call1=3 + call2=最大5) | DECISION_LOG.md:7、`DESIGN_02.md:18 M-7c` | `er119_kp_candidates_01.py:94-98`、`er119_kp_prompt_2v_01.py:19,26-29` | ○ | ○ | ○ |
| NG復活禁止 | USER.md:97(「retry・fallback・regeneration・resumeで復活させない」) | `er119_kp_candidates_01.py:212,293`(`rv.match_ng`)、`er119_kp_human_review_01.py:336` | ○ | ○ | ○ |
| 重複排除(call2は前記3件と同一/包含を除外、Redundancy QA) | Prompt 2-V条件6、Opus M-8 | `er119_kp_candidates_01.py:30-33,81-83,311-327`、finalizeで再適用 | ○ | ○ | ○ |
| 外側retry(AUTO可<3 かつ Gate除外あり、候補list全体置換) | Opus M-7(c)、DECISION_LOG.md:87(F1: 除外句の累積) | `er119_kp_candidates_01.py:329-340` | ○ | ○ | ○ |
| Z限定: SRC D1/人称整合 | Opus M-7(b) | `er119_kp_candidates_01.py:118-145,272-283` | - | - | ○ |

注: 全規則は`er119_kp_candidates_01.py generate_candidates`(`fulltext_p2`経路)に共通。X/Y/Zの差はSRC D1・人称整合(Z限定)のみ。A/B/C旧経路(`kp_backend="strategy_l"`)は27-7により対象外・無変更。

## 2. 独立節: 「活用形→基本形例外」のer119経路適用状況(Fable指定の最重要照合点)

**結論: 例外は er119 候補経路に適用されている(配線漏れではない)。`studied separately`の除外は、例外に付随する実装guardによる設計どおりの拒否であり、そのguardはCURRENT_SPEC文面に記載がない(記録漏れ)。**

根拠(コード+実ログ):
1. (a)いつ・誰が: 全文選定(`KP-FULLTEXT-SELECTION-3KP-PRODUCTION-01` 委任_02、2026-10-22、commit `84d9a6412`)でOpus条件A P-02(3)(4)/P-04を受けFableが採用し、DECISION_LOG.md:88が「Fable決定の開示: Rule7に基本形化例外(人物一般化と同型)」と記録。ユーザー原文でこの例外自体を名指しで承認した行は見つからない(ユーザーは全文選定の`APPROVED_FOR_PRODUCTION`を承認、例外はその実装設計としてFableが開示)。=出典は「Fable決定の開示」。
2. (b)実装: `er003_key_words_canonicalization.py:529-541 _is_valid_fulltext_normalization` → `er105_kp_fulltext_selector_01.py:830-837 is_valid_inflection_normalization` → `:812-827 find_inflection_window` → `:670-691 _token_pair_ok`。
3. (c)er119経路への適用: `er003_kc:666,686 _is_ft = fulltext_by_rank.get(rank)`、`:696 allow_inflection_normalization=_is_ft`。er119のitemは `ft.build_original_items`(`er105:266-290`)が`fulltext_source_ref`を付与するので`_is_ft=True`。実ログで確認: AI島 a2 の通過候補`carried over→carry over`(`kp_candidates.json` candidates[0]、`normalization_reason=lemma_normalization`)と`taken a detour→take a detour`、b1b の`looked at separately→look at separately`、`called on→call on`がこの例外でPASSしている。
4. では`studied separately→study separately`はなぜ不通過か: `er105:670-691 _token_pair_ok`は動詞の基本形化に`_guard_ok`(`:662-667`)を課す: 「直後が限定詞/代名詞/不変化詞/前置詞、または句末が不変化詞」(`_GUARD_DET:614`、`_GUARD_PARTICLE:618`)。`studied separately`は直後が副詞`separately`(どの表にも無い)かつ句末も不変化詞でないためguardで拒否。b1b の`looked at separately`は直後が`at`(`_GUARD_PARTICLE`)でPASS。再現: `recheck_01.json` AI2-a(`study separately` → ok=False、理由=Rule7拒否文)、AI2-f(`look at separately` → ok=True)。
5. guardの出典: コードコメント`er105:570-575`が「OF-KPFT-P-04」を根拠に記述。Opus P-04原文(`OPUS_REVIEW_COND_A_01.md:118-123`)は「先頭トークンかtoの直後に限る」「複数→単数は除外表」までで、**次トークン条件は書かれていない**。CURRENT_SPEC.md:1997の要約にも次トークン条件は無い。=guardは実装時のFable採用範囲の具体化(`heated debate→heat debate`防止)で、仕様文書への記録漏れ。

11-8分類(判定は報告のみ・今回は実装しない):
- **範囲内(文書是正)**: CURRENT_SPEC.md:1997へ「次トークン条件(限定詞/代名詞/不変化詞/前置詞)と閉表」を追記する記録是正。コードは現状維持。
- **範囲内の可能性あり(Fable判定要)**: guard語彙の網羅漏れ。コードコメントは「限定詞」と書くが`_GUARD_DET:614`は`a/an/the/some/any/this/…`のみで、`no`/`each`/`every`/`all`/`both`/`another`等を欠く。実害: `accepts no responsibility`(Z)・`leaving no mark`(Z)が除外(`inventory_01.json`)。また`_PAST_ONLY_IRREGULAR:577-582`に`rang`が無い(`rang through`、Z melos R4)。ただし閉表の拡張は受理面の拡大でもあるため、Fableが「記述意図への是正」か「拡大」かを判定(本報告では`W1`/`W3`とし、段階2の新規則扱い)。
- **範囲外(新設/拡大=ユーザー承認)**: 動詞+副詞(`studied separately`)・動詞+名詞(`lost touch`)・動詞+形容詞(`pulling free`)の基本形化受理。`er105:575`が明示的に「V+名詞は基本形化せず表層形のまま」としており、承認済み設計は「基本形化しない」を選んでいる。
