# DATASET_01.md と phase3 csv を生成する(API 0)
import csv
import json
import os
import sys
sys.path.insert(0, ".")
import er091_asr_three_way_trial_01_analyze as an

OUT = an.OUT
RES = an.RES
man_all = an.manifest()
L = ["# DATASET_01 (ASR-THREE-WAY-COMPARISON-TRIAL-01 評価データ台帳、自動生成)\n",
     "正本=`er091_output/asr_three_way_trial_01/dataset_manifest.jsonl`(全フィールド: wav path/sha256/duration/canonical/label/label_basis/tags/ledger_phrases/duplicate_of/src_wav)。音声wavは`er091_output/asr_three_way_trial_01/audio/`(orig=既存音声のコピー[git管理外、src_wavから再生成可]、tts_construct・splice=新規生成[*.wavは.gitignore対象のためgit管理外・ローカル(この作業環境)のみ。TTSは再生成不可なのでバックアップ要否はFable判断])。",
     "label_strength: human_listened_article=ユーザー試聴PASS記事の一部(KP/セグメント単位の個別聴取ではない) / human_approved_segment=HR承認済み / human_listened_user_report=ユーザー聴感指摘(take part) / construction=人間試聴なし。",
     "tags は自動付与(proper_noun は文頭の固有名詞を含め過検出あり)。\n",
     "| id | kind | Family/Level | 台本(canonical) | label | label_strength | 問題種別 | PL | 秒 | dup |", "|---|---|---|---|---|---|---|---|---|---|"]
for m in man_all:
    L.append(f"| {m['id']} | {m['kind']} | {m['family']}/{m['level']} | {m['canonical'][:48].replace('|','/')} | {m['label']} | {m['label_strength'][:28]} | {(m.get('problem_type') or '')[:34]} | {','.join(m['ledger_phrases'])[:24]} | {m['duration_s']:.1f} | {m['duplicate_of'] or ''} |")
open("docs/research/ASR-THREE-WAY-COMPARISON-TRIAL-01/DATASET_01.md", "w", encoding="utf-8").write("\n".join(L))
P3 = json.load(open(os.path.join(RES, "phase3_item_results.json"), encoding="utf-8"))
with open(os.path.join(RES, "phase3_item_results.csv"), "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(P3[0].keys()))
    w.writeheader()
    for r in P3:
        w.writerow({k: (json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v) for k, v in r.items()})
print("ok", len(man_all))
