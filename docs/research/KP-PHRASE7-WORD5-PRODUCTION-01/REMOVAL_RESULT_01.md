# REMOVAL_RESULT_01: 撤去・残置した旧ルール/検査/定数と残存Grep(KP-PHRASE7-WORD5-PRODUCTION-01 委任_02、2026-10-27)
Charter 8(旧ルール・旧検査の撤去要否確認)。Grepは`.venv`・`docs/`・Trial module(`er123_*`/`er124_*`)を除く`*.py`。

## 撤去したもの
| 識別子 | 旧内容 | 置換先 | 残存Grep |
|---|---|---|---|
| `BACKFILL_MAX_CALL_ITEMS`(`er119_kp_backfill_01.py`) | 補完1回の件数上限5(2-Vの最大件数由来) | 種類別の空き(`PHRASE_CAP=7`/`WORD_CAP=5`)とE_kindの小さい方(`plan_quota`) | `grep BACKFILL_MAX_CALL_ITEMS` → `er119_kp_backfill_test_01.py:142-143`のみ(**撤去確認の否定assert**: `assertFalse(hasattr(bf,"BACKFILL_MAX_CALL_ITEMS"))`)。Production 0件 |
| 単一cap(`KP_CANDIDATE_MAX`)でのroom計算(`plan_quota(counts, n_cands, cap)`) | `room=cap-現存`、`total=min(E,room,5)` | `plan_quota(counts, n_phrase, n_word)`(種類別quota) | `grep "cap - n_cands\|cap-現存"` → 0件 |
| `pick_backfill`の取り数=E_kind | Eで種類別に採り、合計だけ`plan.total`で制限(Opus M-1の過採用: フレーズが8件になる) | quota(`plan.quota_phrase`/`quota_word`) | `pick_backfill`は`counts`引数を残すが取り数には使わない(署名互換)。testで過採用なしを固定(`test_pick_backfill_uses_quota_not_E`) |
| 外側retry判定の独立tuple`("human_ng","overflow","duplicate_of_top3","excluded")`(`er119_kp_candidates_01.py`) | `NOT_COUNTED_STAGES`と別管理(M-2で`overflow_kind`が漏れる) | `bf.GATE_DROP_EXEMPT_STAGES`(=`NOT_COUNTED_STAGES`+human_ng/duplicate_of_top3/excluded)。testで`GATE_DROP_EXEMPT_STAGES[:2] == NOT_COUNTED_STAGES`を固定 | `grep '"human_ng", "overflow"' er119_kp_candidates_01.py` → 0件 |
| 候補生成の既定select/call2が旧Prompt 2/2-V | `select_fn or sc.run_key_phrase_selection`(Prompt 2・3件)、call2=`run_vocab_selection`既定(2-V) | `select_fn or select_p7`(P7・7件)、call2=`spec=SPEC_W5P`(W5') | `_generate_candidates_impl`内に`PROMPT_2_TEXT`/`PROMPT_2V`/`p2v.make_vocab_selector_fn`の参照0件(`TestDefaultOnNoFlagD1.test_old_prompts_not_referenced_from_new_production_path`) |
| 補完が2-Vを使う記述(`candidates:9-10`のdocstring、`_run_backfill`内の`p2v.PROMPT_2V_ID/SHA`) | 補完=2-V 1回 | 補完=種類別P7/W5'(`rec.prompts`)。旧スカラー`prompt_id/prompt_sha256`は`"per_kind"`(互換) | `grep "p2v.PROMPT_2V" er119_kp_candidates_01.py` → 0件 |
| 「3件」固定文言(`build_exclusion_note`/`build_machine_note`の`3件に揃えず`) | P7/W5'/補完でも「3件」と案内 | `limit`引数(既定3=Prompt 2経路はバイト同一、P7=7/W5'=5) | `grep "無理に3件" *.py` → `er105_kp_fulltext_selector_01.py`(既定値の文言は`{limit}`化・既定3で同一)のみ。test(`test_exclusion_note_default_wording_unchanged`)が旧文言のバイト同一を固定 |
| `KP_CANDIDATE_MAX = 8`(`er119_kp_human_review_01.py:52`) | 3+5=8件 | 12(7+5) | `grep "KP_CANDIDATE_MAX\s*=\s*8"` → 0件 |

## 残置したもの(撤去しない理由)
| 識別子 | 理由 |
|---|---|
| `ft.PROMPT_2_TEXT`/`PROMPT_2_SHA256`(`a12896f4…`)・`p2v.PROMPT_2V_TEXT`/`PROMPT_2V_SHA256`(`e1d5349c…`)の本文・pin test | D1=R0。旧runのresume・復帰(`git revert`)の部品。`run_vocab_selection`の`spec=None`既定は2-V(旧)の挙動で、legacy呼出(`er119_kp_rescue_wiring_test_01.test_w5b…`等)の回帰を担保 |
| `er105.run_selection_gate`/`run_fulltext_selection`の既定(Prompt 2・3件) | A/B/C以外でも使う旧経路(Z旧`kp_fn`、Y旧アダプタ、legacy `run_kp_with_outer_retry`)。keyword-only引数の既定=従来動作(testで固定) |
| `sc.run_key_phrase_selection(kp_backend="fulltext_p2")`の分岐(`er003:359-364`、`prompt_sha256=PROMPT_2_SHA256`) | legacy経路。新経路は`select_p7`内で自前のtelemetry(P7 sha)を記録し、scを経由しない。er003は無編集 |
| `er106`の旧定数`KPFT_PROMPT_2_SHA256`/`KPFT_KP_COUNT_MAX` | `prompt_id=kp_prompt_2`の旧runの判定用(`KPFT_EXPECT_BY_PROMPT_ID`)。両shaの無条件許容はしない |
| 旧3+5 golden(`docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/golden_02a`) | 履歴として不変。7+5の新golden(`golden_03`)のcall1の3件分との一致照合(Prompt差替以外の副作用検出)に使う |
| runner内コメント「候補(最大8)」(`er019:800`/`er026:2018`)、`er026:2647,2792`のmock `n_max=8` | 表記のみ(R-5)。runnerは非編集方針のため記録のみ。mock E2Eは別generatorで7+5を通す |

## 残存Grep(実行結果の要約。実行は`IMPLEMENTATION_01.md` §5)
`BACKFILL_MAX_CALL_ITEMS`=Production 0 / `KP_CANDIDATE_MAX = 8`=0 / `一律除外しない`(W5'・Production module)=0(Trial `er124`は履歴として残置) / `PROMPT_2V_TEXT|PROMPT_2_TEXT`の新経路内参照=0 / `Prompt 2-V`を補完の使用Promptとして説明する記述=0(docstringは更新済み。`run_vocab_selection`のdocstringは「既定=2-V」と旧挙動の説明として残置)。
