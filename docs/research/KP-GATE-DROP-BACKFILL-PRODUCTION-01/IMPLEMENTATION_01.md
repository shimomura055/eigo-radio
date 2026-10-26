# IMPLEMENTATION_01: Gate除外候補補完の実装記録(KP-GATE-DROP-BACKFILL-PRODUCTION-01 委任_02、2026-10-26)

Status=IMPLEMENTED(testとmock runtime PASS、API 0・JPY0)。実API/freshのruntime evidenceは委任_03。PRODUCTION_WIRED判定はevidence後のFable。設計=`DESIGN_01.md`+`DESIGN_02.md`、レビュー=`OPUS_REVIEW_01.md`、データ契約=`DATA_CONTRACT_01.md`、撤去=`REMOVAL_RESULT_01.md`。

## 1. commit
| commit | 内容 |
|---|---|
| `cbcd29d27` 委任_02a | `_gate_chain`/`_screen_human_ng`の純抽出(status返却、外側ループ制御を持たない)。抽出前(HEAD)で固定したgolden 13 scenario(`golden_02a/`)と抽出後の候補docが完全一致 |
| 委任_02b(本commit) | 補完実装・外側retry脚撤去[ON時]・HR依頼書表示・test・文書 |

## 2. 変更ファイル
| ファイル | 変更 |
|---|---|
| `er119_kp_backfill_01.py`(新規) | 単一flag読取`backfill_enabled()`(`EIGO_KP_BACKFILL`、既定ON)、`kind_of_phrase`、call1除外の読取(M-1)、`count_exclusions`(R-1/R-4)、`plan_quota`、`pick_backfill`(種類別先頭N)、補完call入力(`shown_phrases`/`rejected_entries`/`existing_entries`)。LLM呼出・er105 importなし |
| `er119_kp_candidates_01.py` | `run_vocab_selection`に`shown_phrases`/`note`(M-5/M-7、既定は従来と同一)、`_run_backfill`(M-4/M-6/R-2/R-3/R-5/R-8)、`_generate_candidates_impl`の配線(ai_rank付番後・Redundancy QA前=R-10)と外側retry条件(ON時は候補0件・技術失敗のみ)、候補`kind`、doc `backfill`/`shortfall_detail`、`make_person_repair_fn`の出力先分離(contextvar) |
| `er119_kp_human_review_01.py` | `render_request_md`に補完の要約1行と『補完候補(Gate除外の代替)』旗(補完発動時のみ。未発動は従来のmdと同一) |
| `er119_kp_prompt_2v_01.py` | 無変更(`build_user_message`が既に`diagnostic_note`を受ける) |
| test | `er119_kp_backfill_test_01.py`(新規55件)、`er119_kp_backfill_golden_01.py`(golden support)、`er119_kp_human_review_01_test_01.py`・`er119_kp_rescue_wiring_test_01.py`(旧retry脚の期待値をOFF明示へ。`REMOVAL_RESULT_01.md`§3) |
| 非変更 | `er105`・`er003`・`er108`・`er125`・Prompt 2/2-V本文(sha pinned test PASS)・A/B/C・X/Y/Z runner |

## 3. 処理フロー(ON時)
```
call1(Prompt 2) -> [M-1] metadataからcall1最終attemptの除外を取得 -> call2(Prompt 2-V) -> screen NG -> _gate_chain(初回)
  -> ai_rank付番 -> _run_backfill:
        E = count_exclusions(dropped, cands)  (種類別、phrase_key重複除去、overflow/救済/HR限定は数えない)
        E=0 / 候補0 / 上限到達 -> 不発動(LLM 0)
        stop_check_fn -> 2-V(already=現存候補+救済前元句、note=既存exclusion note、包含比較先=call1のまま) 1回
        -> 補完応答の最大5件に _gate_chain(work/backfill_1、人称整合は別dir) -> R-3重複除去 -> 種類別の先頭E_phrase/E_word件(上限8-現存)
        失敗(call/live0/canon全体/技術例外) -> backfill.status=FAILED、初回候補で続行(FulltextSelectionError/STOPは伝播)
  -> cands末尾へ追加(origin=backfill、ai_rank連番) -> Redundancy QA(全候補1回) -> 外側retry判定: 候補0件のみ
```

## 4. test結果(mock・API 0)
`RESULT_PACKET_KBF2.md`(3)。
