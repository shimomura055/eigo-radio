# ============================================================
# er003_b1_p4d_sudachi_tokenize_helper.py
# ER-003-B1-P4D: 隔離MFA環境(mfa_tool/envs/mfa)内でSudachiPyを実行する
# 単独ヘルパー。アプリ本体(.venv)のproduction依存関係にsudachipyを
# 追加しないため、er003_b1_p4d_audio.pyがmicromamba経由でこのファイル
# だけをサブプロセス実行する(er003_b1_p3w_audio.run_mfa_alignと同じ
# 隔離方式)。このファイル自体はer002_*/er003_*の他モジュールを一切
# importしない(隔離環境にはアプリ本体の依存関係が入っていないため)。
#
# 使い方: python er003_b1_p4d_sudachi_tokenize_helper.py <入力txt> <出力json>
import json
import sys

import sudachipy

input_path = sys.argv[1]
output_path = sys.argv[2]

with open(input_path, encoding="utf-8") as f:
    text = f.read()

tokenizer = sudachipy.Dictionary().create()
morphemes = tokenizer.tokenize(text)

results = []
for m in morphemes:
    results.append({
        "surface": m.surface(),
        "dictionary_form": m.dictionary_form(),
        "reading_form": m.reading_form(),
        "part_of_speech": list(m.part_of_speech()),
    })

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
