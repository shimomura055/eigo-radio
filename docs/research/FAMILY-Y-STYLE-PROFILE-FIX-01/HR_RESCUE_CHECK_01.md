# HR_RESCUE_CHECK_01 — 既存の承認済み表記ゆれ・同音救済規則は Std preview に適用できるか(委任_05、API 0)

対象: run `er121_output/family_y_production_01/redelivery_fee/run_style_fix_01` a2 `preview`(lock=HUMAN_REVIEW_REQUIRED、`audit/review_lock_state.json`)。
差分の事実: 原稿「思い**どお**りに」↔ OpenAI/Azure とも「思い**通**りに」(Azureは加えて読点1つ欠落)。取得元: `narration/attempts/preview_attempt{1,2,3}_*.json`、lock `last_attempts_log[].asr_judgement`。

## 1. 照合した承認済み規則(CURRENT_SPEC.md)と適用可否
| 規則 | 場所 | 条件 | 本件 | 判定 |
|---|---|---|---|---|
| OF-AUW-08(R+) JA受理集合 | :2903 | 二次ASRの受理は `EXACT_MATCH`/`NORMALIZED_MATCH` のみ。`ORTHOGRAPHIC_VARIANT_CONFIRMED` は Primary+Secondary の2エンジン確認 | Primary・Secondary とも `ASR_VALIDATION_UNCERTAIN`(`secondary_not_accepted`、`p3_entry=p3_primary_ng`) | 非受理 |
| JA表記ゆれ `ORTHOGRAPHIC_VARIANT_CONFIRMED` | :1859 | ASR側の漢字spanの辞書上の読み候補にcanonicalの期待読みが含まれ、2エンジンが同状態 | 差分spanが `どお`(かな)↔`通`(漢字)と**送り仮名の途中で切れる**ため span単位の候補比較が成立しない(`_span_pair_reading_variant_match("どおり","通り")`=False。`通`の候補には`どおり`があるが`どお`単体とは一致しない。`er011_ja_asr_variant_layer_01.py:514`) | 不成立 |
| OPEN-145 JA表記ゆれ一般化 Variant Layer Candidate B/D-2 | :2232 | D-2は形態素読みが**濁点許容なしで完全一致**した場合のみ `PHONETIC_MATCH` へ引上げ(`er011_ja_asr_variant_layer_01.py:543-570`) | 形態素読み: 原稿 `おもいどおり` / ASR `おもいとおり`(濁点差)。D-2の厳密一致条件を満たさず Cascade対象(UNCERTAIN)のまま | 不成立 |
| 英語homophone / 多語同音救済(:1860, :2921) | — | 英語のみ(CMU辞書) | 日本語は対象外 | 対象外 |
| OPEN-517 F1/F2(READING_MATCH最終Gate・差分span再生成) | OPEN_ITEMS OPEN-517 | READING_MATCH起点の救済・再生成。`r5.f1.reading_match_primary_pass=false`、f2 `enabled=false` | 本件で発火せず(lock内 r5記録) | 不成立 |
| 日本語ASR Secondary Confirm Gate(SCG)/統一judge P3 | :2215, :2889 | Secondary転写が原稿を**独立に**支持(EXACT/NORMALIZED)する場合に採用 | Azure転写も「通り」で原稿と不一致 | 不成立 |

オフライン再現(API 0、`classify_ja_asr_match(..., allow_reading_resolver=False)`、スクラッチ実行): OpenAI全文・Azure全文・Take3全文のいずれも `ASR_VALIDATION_UNCERTAIN`(理由: Candidate B「形態素読みが濁点/半濁点の有無を除き一致、Cascade対象、即PASSにはしない」)、content_diffs=`[replace どお→通, phonetic_uncertain=False, cascade_eligible=False]`。数値・否定のガードは `NO_VALUES`/否定差なし。

## 2. 結論
**既存の承認済み規則では自動PASSに適用できない**(承認済み規則に「通り↔どおり」を自動受理する条項は無い)。したがって規則どおり**Human Reviewパケットを提出する**(`HR_PACKET_STD_PREVIEW_01.md`/`hr_preview_01.html`)。HR必須Gateの緩和・迂回、規則に無い判断での通過は行っていない。

## 3. 参考(今回は実装しない)
「送り仮名の途中でspanが切れる(どお↔通)」型の表記差は、Variant Layerのspan拡張(送り仮名を含むまで広げて候補比較)で救える可能性がある。これはGate/QA blocking条件(受理集合)に関わる新仕様候補であり、本委任では実装・提案採用しない(仕様候補として報告のみ。過去にも `RESULT_PACKET_YSP2.md:36` が同種事象を『ユーザー判断要』候補として記録済み)。
