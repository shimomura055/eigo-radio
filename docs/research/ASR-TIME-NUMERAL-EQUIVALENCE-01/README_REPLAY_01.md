# replay基盤(ASR-TIME-NUMERAL-EQUIVALENCE-01)

前身 `docs/research/FAMILY-Z-AFTER-TWENTY-YEARS-PRODUCTION-01/{replay482.py,pairs482.py,replay482b.py}` を一般化。API 0・読み取り専用。

1. `py replay_extract_pairs_01.py --root ../../.. --out pairs_01.jsonl` : 全リポジトリの .json/.jsonl(47,132ファイル)から(canonical, asr)対を抽出 -> **5,330対**(約6分)。`pairs_01.jsonl`は2026-10-24時点のスナップショット(委任_02で再抽出して比較に追加可)。
2. `py replay_judge_01.py --pairs pairs_01.jsonl --out base.json` : 各対を value_guard / classify_asr_match(role=FULL_STORY) / tier1 / **unified_judge(Primary 1本、`judge_sim_01.py`)** で判定(約40秒)。`--modules DIR` で候補module(例 `proto_C`)をsys.pathの先頭に置いて差し替え。
3. `py replay_compare_01.py base.json cand.json pairs_01.jsonl` : judge PASS->NG / NG->PASS / value_guard / 分類層 / Tier1 の変化を件数と実例で出力。

ベースライン(修正前HEAD)結果: `baseline_replay_01.json`(unified_judge state内訳 NG_SECONDARY_UNAVAILABLE 3,075 / PASS 1,234 / NG_PROTECTED 1,021。Secondaryは呼べないので『Primary 1本の状態』)。案Cとの比較: `protoC_vs_baseline_01.txt`。
注意: 抽出は `text` 系キーも対象にするためCanonical/ASR対でないものも混じる。判定の変化だけを見る用途であり、件数をPASS率として使わない。
