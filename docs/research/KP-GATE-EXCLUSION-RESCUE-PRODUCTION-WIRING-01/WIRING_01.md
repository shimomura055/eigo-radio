# WIRING_01: 救済フローのProduction配線(KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01 委任_02)

2026-10-26 / ユーザーAPPROVED_FOR_PRODUCTION(2026-10-26)の限定配線。**PRODUCTION_WIRED判定はFable**(本書はEVIDENCE_COLLECTEDまでの実装記録)。設計=DESIGN_03.md §3/§6、是正=FIX_01.md。

## 1. 配線箇所(5か所+文脈)
| # | 場所(file:行) | 内容 | 発火条件 |
|---|---|---|---|
| H1 | `er105_kp_fulltext_selector_01.py:961-979` `contains_finite_aux_role_based` | 従来guard(`..._raw`)がTrueでも、`er125.idiom_aux_exception_applies(text)`(辞書見出し一致の助動詞始まり慣用句)ならFalse。遅延import関数`_rescue()`(:966) | `rescue_active()`=kill switch未OFF **かつ** generate_candidates文脈内 |
| H2 | `er105_kp_fulltext_selector_01.py:245-267` `validate_and_resolve`、`:302` `build_original_items`、`:408-417` `apply_exclusions`(R6) | 選定段の救済(D1再アンカー/慣用句の主語除去)。M1の重複再照合、`selection_rescue`メタ付与 | 同上 |
| H3 | `er003_v1_n3_01_scaffold_generate.py:475-567` `run_key_phrase_canonicalization(..., rescue=False)` | `rescue=True`かつ全文選定item: 所有格role後処理の後ろにrevert/M1救済を連結(:510-515)、merge+gloss整合の後に救済rankのgloss強制再整合+QA再判定(承認済みfulltext prompt/schema無変更、1 call)(:553-567) | 明示引数`rescue=True`(= `er119_kp_candidates_01.py:174-176`だけが渡す) |
| H4 | `er119_kp_candidates_01.py:157-163,164,308-324,349-351,375`、`er119_kp_human_review_01.py:834-835,1216-1219,1283-1291` | wrapper(contextvarセット)、NG元句照合、`annotate_candidate`(旗・gates・auto_eligibleはANDのみ)、M3、doc単位provenance、HR依頼書の旗列、gloss解決後のauto再計算、resume時ドリフトlog | 常時(救済なしの候補は無変更) |
| 文脈 | `er125_kp_rescue_production_01.py:53-73` `_rescue_ctx`/`rescue_context`/`rescue_active` | `generate_candidates`だけがセット(終了時に必ず戻す) | - |

## 2. kill switch・既定値
- `EIGO_KP_RESCUE`(既定ON=ユーザー正式採用)。`"0"`のときだけ全hook無効=従来動作。読取りは`er125.rescue_enabled()`の1関数のみ(`er125:48-52`。全repo Grep: `.py`でKILL_SWITCH_ENV読取=1か所。testで固定=`TestWiringSites::test_kill_switch_read_by_single_function`)。起動script/.envでON/OFFを暗黙に変えていない。
- Grep結果(`EIGO_KP_RESCUE` Production `.py`): `er125_kp_rescue_production_01.py:48`のみ(test除く)。
- 新規承認なしの機能ではない(ユーザーAPPROVED_FOR_PRODUCTION 2026-10-26)ため、11-7の「既定OFF」例外には該当しない。

## 3. 旧経路(M2): 救済が発火しない経路の一覧(`run_selection_gate(`/`validate_and_resolve(`/`run_fulltext_selection(` Grep、全repo)
| 呼出元 | 文脈 | 結果 |
|---|---|---|
| `er119_kp_candidates_01.py:206`(call1 `select_fn`=`sc.run_key_phrase_selection`→`er003_v1_n3_01_scaffold_generate.py:357`→`ft.run_fulltext_selection`→`run_selection_gate`→`validate_and_resolve`) と `:74`(`run_vocab_selection`) | generate_candidates内 | 救済あり(X/Y/Z共通の正式経路) |
| `er062_family_z_writer_01.py:1364 run_kp_with_outer_retry_fulltext`(Zの`_kp_fn_for_ctx`既定)、`er121_family_y_runner_01.py:538-551`旧kp_fnアダプタ(test/mock専用hook) | 文脈外 | **救済なし**(従来どおり除外→外側retry)。test: `test_w4_old_routes_do_not_rescue_even_when_env_on` |
| `er003_v1_b1_p2_generate.py:37`・`er003_v1_sing01_kp_generate.py:43`(`bk.run_selection_gate`=B1 P2の別実装) | 別module | 無関係(ft.run_selection_gateではない) |
| `er123_kp_rescue_dev_01.py:612`(DEV)、`er124_kp_phrase_word_trial_01.py:142`(Trial; generate_candidatesを使うTrialは文脈内で救済の対象) | DEV/Trial | DEVは文脈外=従来。Trial(er124)はgenerate_candidates経由のため救済も作用(Trial専用経路) |
| A/B/C(`allow_inflection_normalization=False`、`sc.run_key_phrases`系) | - | `rescue`引数なし・validatorは旧関数 → **バイト同一**(golden 1002件 BYTE_IDENTICAL) |

## 4. `candidates_sha256`・resume
- 候補ごとの`rescue`メタ、doc単位の`rescue_provenance`は`kp_candidates.json`に含まれ、`candidates_sha256`(doc全体のsha)に包含される(`test_w1b_candidates_sha_covers_rescue_meta`)。
- resume(`ensure_kp_review`)は保存済み候補を読み戻すだけで再計算しない(API 0。`test_w2_resume_reads_back_without_any_llm_call`、fresh run再起動でAPI 0・sha不変=EVIDENCE_01)。
- AI島`run_ai_01`の既存HR候補は不変(固定fixtureのresume統合test、`candidates_sha256`不変)。
