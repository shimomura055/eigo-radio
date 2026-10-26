# DATA_CONTRACT_01: KP候補doc(`kp_candidates.json`)のフォーム側向けデータ契約(F-2)

KP-GATE-DROP-BACKFILL-PRODUCTION-01 委任_02、2026-10-26。読み手=学習項目選定フォーム(LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01)・HR依頼書・AUTO選定。**既存項目は無変更**、追記専用(下の「追記」印が今回の追加)。実装=`er119_kp_candidates_01.py`(`_gate_chain`/`_run_backfill`/`_generate_candidates_impl`)・`er119_kp_backfill_01.py`。fixtureの実物=`golden_02a/*.json`(補完OFF)と`er119_kp_backfill_test_01.py`の`test_data_contract_fields_F2_TBF26`。

## 1. 候補(`candidates[]`、AI順位`ai_rank`の昇順で並ぶ。補完候補は末尾)
| key | 型 | 意味 |
|---|---|---|
| `candidate_id` | string | `p_`+選定句のphrase_key sha1先頭10桁。reviewのverdicts/selectionのキー |
| `ai_rank` | int(1..8) | Gate通過後の連番。call1→call2→補完の順 |
| `kind` | `"phrase"`\|`"word"` | **追記(R-1)**。`used_form`の英単語数が1なら`word`、それ以外は`phrase`。フォームの『フレーズ最大7/単語最大5』枠の振り分けに使う |
| `origin` | `"call1"`\|`"call2"`\|`"backfill"` | 選定の出所。`backfill`=Gate除外分の補完(Prompt 2-Vの再利用) |
| `selection_phrase` / `used_form` | string | AIが選んだ表層形 / 基本形化後(音声・解説に使う形) |
| `japanese_gloss` / `source_sentence` / `source_sentence_id` | string | 本文中の意味 / 出典文 / 文ID |
| `word_count` | int | `used_form`の語数 |
| `reason_ja` | string | AIの選定理由(call1は空) |
| `auto_eligible` | bool | AUTO採用できるか(qa_fail/gloss_hr_pending/similar_to_ng/救済でauto不可なら false) |
| `human_selectable` | bool | 常にtrue(Humanは全候補を選べる) |
| `flags.qa_fail` / `flags.gloss_hr_pending` / `flags.similar_to_ng` | bool | HR限定の理由旗 |
| `flags.redundant_with` | [candidate_id] | Redundancy QAの重複旗(提示用。確定集合ではfinalizeが再判定) |
| `flags.rescued` / `flags.rescue_codes` | bool / [string] | 救済済み(RESCUED)と理由コード(救済成立時のみ存在) |
| `rescue` | object | 救済の元句・理由コード・QA再判定(救済成立時のみ。`rescue.selection.original_phrase`/`rescue.canonicalization.display_phrase`が元句、`rescue.codes`が理由コード) |
| `rescue_note` | string | 救済候補のHR表示用文(元句+コード) |
| `gates.*` | object | validate/cmu/canonicalization/gloss/symbol/src_d1の状態 |
| `item` | object | 後段が読む完成KP item(canonicalization・gloss済み) |

## 2. docレベル
| key | 型 | 意味 |
|---|---|---|
| `shortfall` | bool | 既存。候補数<8 |
| `shortfall_detail` | object | **追記(F-2)**。`{n_candidates, cap(8), missing, E_total, backfilled, unfilled_by_kind: {phrase,word}\|null}`。補完発動時のみ`unfilled_by_kind`が入り、Eに対して補えなかった種類別の件数 |
| `backfill` | object | **追記(F-2)**。下表 |
| `dropped[]` | array | 既存。Gate除外された候補(参考表示用)。`{raw_rank, phrase, stage, reasons[], origin}`。**追記**: `origin=call1`(call1最終attemptの除外、補完ON時のみ)、`origin=backfill`(補完側の除外)、stage `backfill_duplicate`・`excluded`(補完側の機械除外) |
| `outer_retry_log[]` | array | 既存。各周に`backfill`の要約(`triggered/status/E/added`)を追記 |

`backfill`:
```json
{
  "enabled": true,                 // 生成1回につき1回読んだEIGO_KP_BACKFILLの結果(0のみfalse)
  "triggered": true,               // 補完callを行ったか
  "status": "OK",                  // OK | FAILED | NOT_TRIGGERED | DISABLED
  "reason": "E=0",                 // NOT_TRIGGEREDのみ: E=0 | no_candidate | no_room
  "failure": null,                 // FAILEDのみ: call2_selection_failed | no_live_items | canonicalization_<status> | technical:<例外名>: <文>
  "E": {                           // 除外件数(AIが選んだitemのうち最終的にGate除外されたもの。救済成立・HR限定候補・overflowは数えない)
    "total": 2, "phrase": 1, "word": 1,
    "human_ng": 0, "excluded": 0,  // Humanが不適切としたNG句/累積除外句をAIが再び選んだ件数(別カウンタ。totalにも含む)
    "by_stage": {"validate": 1, "cmu": 1},
    "items": [{"phrase": "…", "kind": "phrase", "stage": "validate", "origin": "call2"}]
  },
  "N": {"room": 2, "total": 2, "phrase_wanted": 1, "word_wanted": 1, "capped": false},   // 補完件数の上限(=min(E, 8-現存, 5))
  "added":   [{"candidate_id": "p_…", "kind": "phrase", "used_form": "…", "ai_rank": 7}],  // 実際に末尾へ追加した候補
  "surplus": [{"candidate_id": "p_…", "kind": "phrase", "used_form": "…"}],                  // Gate通過したが種類別quota/上限で採らなかった候補(候補にしない)
  "dropped_by_stage": {"validate": 1},   // 補完側の除外のstage別件数(明細はdoc.dropped[]のorigin=backfill)
  "prompt_id": "kp_prompt_2v", "prompt_sha256": "…", "model_id": "…", "response_id": "…",
  "attempts": [{"attempt": 1, "status": "OK", "n_selected": 3, "n_kept": 2, "n_dropped": 1}]
}
```
`enabled=false`(flag OFF)のときは`{"enabled": false, "triggered": false, "status": "DISABLED"}`だけ。NOT_TRIGGEREDは`{"enabled", "triggered": false, "status", "reason", "E"}`。

## 3. フォーム側の使い方(推奨)
- 表示順=`ai_rank`昇順。補完候補(`origin=backfill`)は末尾。HR依頼書は『補完候補(Gate除外の代替)』の旗を出している。
- フレーズ枠/単語枠の振り分けは`kind`。現行Productionの候補プールは単語とフレーズの混在で最大8件(7+5構成ではない。単語専用抽出は将来の7+5 Prompt採用待ち)。枠数の上限を超える分は表示のみ・採用は人間が選ぶ。
- 上限未達の理由は`shortfall_detail`と`backfill`で説明できる(例:『Gate除外2件に対し補完1件、単語1件は適切な候補が不足』)。
- 古いdoc(補完導入前)には`kind`/`backfill`/`shortfall_detail`が無い。読み手は欠落を許容すること(`kind`が無ければ`word_count==1`で補う)。
