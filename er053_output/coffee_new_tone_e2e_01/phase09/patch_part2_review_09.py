# -*- coding: utf-8 -*-
"""委任_09: part2_review/index.html に「採用済み」バナーを追記(静的HTMLのみ、API呼出0、idempotent)。"""
p = "user_test/coffee_new_tone_01/part2_review/index.html"
t = open(p, encoding="utf-8").read()
B = ('<div class="note" style="background:#e6f6e6;border-color:#7a7"><b>採用済み(2026-10-11)</b>: ユーザー試聴の結果、<b>attempt 4(Local Rewrite後の再TTS)</b>をStandard full_story_part2の採用音声として承認しました'
     '(既存の個別Human Approval機構。自動ASRは不合格のまま)。これはfull_story_part2のみの部分承認で、記事全体の音声品質の承認ではありません。'
     '最終判断は<a href="../index.html">Standard/Advanced完成版の通しページ</a>の試聴で行います。以降の「承認は人間ユーザーのみ」の記述は当時(Human Review待ち)のものです。</div>\n')
if "採用済み(2026-10-11)" not in t:
    k = t.index("<h1>")
    k = t.index("\n", k) + 1
    t = t[:k] + B + t[k:]
    open(p, "w", encoding="utf-8", newline="\n").write(t)
print("ok", "採用済み(2026-10-11)" in t)
