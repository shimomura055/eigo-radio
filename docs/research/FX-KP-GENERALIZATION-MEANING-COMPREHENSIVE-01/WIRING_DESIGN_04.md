# WIRING_DESIGN_04: ②possessor_roles / ①独立検査+再生成 の採用時のProduction配線設計(委任_14、API 0。未承認の新仕様。**配線しない**)

管理ID: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_14 / 前版=`WIRING_DESIGN_03.md` / 設計=`DESIGN_06.md` / 実測=`TRIAL_RESULT_04.md`
前提: 以下はユーザー正式採用(`APPROVED_FOR_PRODUCTION`)後にのみ実装する。11-7の限定例外は本件(既存Prompt・validator・schemaの直接編集を伴う)には**適用しない**。②と①は独立に採否を判断できる(②だけ採用して①は見送る、が可能な構造)。

## 1. X/Z共通の変更点(両方とも共有module=X/Z・a2/b1b共通の単一経路)
| # | 変更 | 場所(Production) | 共通性 | 備考 |
|---|---|---|---|---|
| ②-1 | fulltext schemaの`rank`直後に`possessor_roles`追加 | `er003_key_words_canonicalization.py` `_fulltext_item_properties()` | X/Z共通 | A/B/C schemaは不変(fulltext専用schemaだけ変更=既存の方針OF-KPFT-P-02(1)) |
| ②-2 | fulltext templateのrole判定ブロック・規則3/4の例示均等化・QA定義(DEV写し`_POSS_EDITS`の4編集) | `er003_v1_translator_briefs/b1_p2_keywords_canonicalization_fulltext_prompt_template.txt` | X/Z共通 | A-1(規則5)の`_EDITS`と**同一の配線委任で連結**(drift guard: oldが1回だけ存在することを両方で確認。anchorは生templateにもA-1適用後にも各1回[検証済み]) |
| ②-3 | decoding後処理(roles検証・窓特定・修復・再計算・`possessor_roles`除去) | `er003_key_words_canonicalization.py`(新関数、DEV実装=`er112_kp_gm_poss_04.py` `repair_item/recompute_fields/process_response_text`) | X/Z共通 | 呼出位置=`run_canonicalization_gate`のparse直後・validate前。修復は語数不変の1対1置換のみ(既存validatorを通る形) |
| ②-4 | 許可表`_PERSON_DEPENDENT_TO_GENERIC`に`my`/`our`->{someone's, somebody's}追加 | 同上 | X/Z共通 | `er105._token_pair_ok`・`gloss_alignment`も同表を参照するため追従 |
| ②-5 | 記録: `person_role_repair`(発火時)と`possessor_roles`の保存、UNVERIFIED_ROLES件数 | keywords_canonicalized.json / run summary | X/Z共通 | reuse判定(signature)には使わない |
| ①-1 | 検査call(新関数`inspect_usage`)と、`run_alignment_gate_corrected`のattempt 1採用後の注入(DEV実装=`er112_kp_gm_trial_04_e2e.py` `e_gate`) | `er003_key_words_gloss_alignment.py` | X/Z共通 | Zは永続化済みartifactの人称整合修復(`only_ranks`)経路を**対象外**にする(新規生成itemのみ検査)=挙動不変 |
| ①-2 | 検査Prompt(v2)・schema・flag規則(`figurative` AND `literal_image_only`、検査不成立でもflag)・再生成reason文 | 新定数(gloss_alignment内) | X/Z共通 | model=`routing.SUPPORT_MODEL`(luna)、effort=low。routing契約のstatic audit(`er006_model_routing_contract_01_static_audit.py`)に新呼出点を追加する必要あり |
| ①-3 | fail-open記録: `usage_check`=`NOT_FLAGGED`/`REPAIRED`/`FLAGGED_UNREPAIRED`/`FLAGGED_UNREPAIRED_NO_ATTEMPT`/`SKIPPED_TECH_FAIL` | 各itemの`gloss_alignment.usage_check` | X/Z共通 | **run summaryと記事報告に件数を必ず出す**(OF-D5-16) |
| ①-4 | 再生成が成立した項目のgloss変更に伴うb1b Adv再生成 | 既存`gloss_signature`機構(X `er019_..._runner_01.py:1077-1081`、Z `er026_..._runner_01.py:1575-1581`) | X/Z共通・**変更不要** | E2Eで確認済み(`TRIAL_RESULT_04.md`) |

## 2. test影響(OF-D5-13。Grep+DEV再現済み)
- `er064_kp_idiom_trial_01_test_01.py:55-56`: `my`->`someone's`を`assertFalse`で固定=**採用時に期待値反転**(許可表の`my`/`our`拡張に伴う正当な更新)。本環境は`wordfreq`未導入でcollect不可のため実行は未確認(配線委任で導入環境にて確定)。
- `er003_test_kp_fulltext_wiring_01.py`・`er064_kp_opt_01_upstream_test_01.py`: 本環境でcollect不可(`wordfreq`未導入)。fulltext schema/template sha固定testがあれば更新対象。
- `er003_test_key_words_canonicalization.py`・`er112_kp_gm_trial_01_test_01.py`: 許可表拡張をDEV再現しても77 passed(変更なし)。
- 新規test(DEV既存): `er112_kp_gm_poss_04_test_01.py`(16件、決定論部分+DefaultOffIsolation)・`er112_kp_gm_trial_04_test_01.py`(6件)。採用時はProduction側へ移植。

## 3. 既存完成記事・Store reuseへの影響(OF-D5-17)
- 既存完成記事は**自動では変えない**。KP stageを再実行した記事のみ、人称語を含む見出し語(self/non_personの再判定)とgloss(flag項目)が変わりうる。変わった項目のb1b Adv説明は`gloss_signature`で5件まとめて再生成(約0.07円/回)。
- flagは確率的なため、KP stage再実行時に同一記事でもflag項目が前回と異なりうる=KP単位TTS(Store reuse)が崩れて再生成される可能性がある。再実行を行うかは記事ごとの判断(自動化しない)。
- 例(既存coffee記事): `pump one's fist`はTrialでroleがnon_personと判定され`pump its fist`へ後退した(正しい一般化の喪失)。再実行すると見出し語・gloss・Adv・TTSが変わりうる。

## 4. ユーザー判断事項一覧(採用時にまとめて諮る。本委任では実装しない)
| # | 事項 | 区分(27-3) | 備考 |
|---|---|---|---|
| 1 | 記事あたり+1回のLLM call(検査、luna low)と追加約0.2円/記事を許容するか。C'(同一call)は検出力0のため代替にならない | D | 70円目標の約0.3%。事前宣言の上限0.15円/記事を超える |
| 2 | canonicalization規則3の追記・例示変更とschema欄追加(承認済みPromptの変更)。『A-1とは別の変更』 | D | ②のみで採否可能 |
| 3 | 許可表`my`/`our`へのsomeone's追加(ER-011-NO18の承認済み表の拡張) | D | |
| 4 | fail-open(検査スキップ)・再生成失敗時のattempt 1採用・STOPなしという安全方針 | D | HR/STOPを増やさない設計 |
| 5 | 判定基準値(flag項目内の悪化許容、recall、費用)をユーザー定義水準として確認するか | D | Fableが確定可(Trial内事前宣言)。採用時の品質水準は別 |
| 6 | 新規生成message変更(M arm)の採否 | — | **不採用で確定**(効果なし)。判断不要 |
| 7 | 既存完成記事のKP再生成の扱い | D | 自動再生成しない方針の確認 |
