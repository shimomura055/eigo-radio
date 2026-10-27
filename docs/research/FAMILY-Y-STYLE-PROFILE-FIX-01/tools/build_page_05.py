# -*- coding: utf-8 -*-
"""FAMILY-Y-STYLE-PROFILE-FIX-01 委任_07: `_03` 表示修正(API 0・音声/本文/KP/学習内容は不変)。

ユーザー正式決定(2026-10-27 USER_04 §1-B/C)への追従のみ:
 (B) Voice説明文を承認文言へ差替え(index.html の y-ai-notice と制作情報節、preview_segments_01.html の同notice)。
 (C) 実測ポーズ表示(`&#9208;0.70s@0:39.0` 等のASR由来span)を全撤去。実TTS Chunk分割境界は本記事では0件
     (chunk_tts_decision.json: a2/b1b とも全segment chunked=False)なので、`⏸` マーカーは置かない。
     凡例noteの『実測停止』説明と『▼表示』説明は撤去(委任_09: ⏸凡例行も公開ページに残さない)。
使い方: py docs/research/FAMILY-Y-STYLE-PROFILE-FIX-01/tools/build_page_05.py   (冪等: 2回目は変更0)
"""
from __future__ import annotations
import json, os, re, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
DEST = "user_test/family_y_production_redelivery_fee_03"
APPROVED = "Voice 1〜3は実在人物の発言をそのまま再現したものではなく、実際に投稿された意見をもとに、AIが編集・再構成したものです。"
OLD_NOTICE = "本コンテンツのVoiceは、実在する人々の意見を参考に、AIが編集・構成したものであり、特定の実在人物の発言を再現したものではありません。"
OLD_PROD = "Voice 1〜3は実在人物の発言ではなく、AIが編集した意見です。"
PAUSE_SPAN = re.compile(r"\s?<span style=\"[^\"]*\"(?: title=\"[^\"]*\")?>&#9208;\d+\.\d+s@\d+:\d+\.\d</span>")
LEGEND = re.compile(r"<br><span style=\"[^\"]*\">&#9208;1\.25s@0:13\.7</span>.*?(?:今回はありません)\)。</div>", re.S)
NEW_LEGEND = "</div>"  # 委任_09: 凡例行(⏸記号)は公開ページに出さない(USER_04 §1-C。開発用マーカーは公開ページ非表示)


def fix(path: str) -> dict:
    t = open(path, encoding="utf-8").read()
    o = t
    t = t.replace(OLD_NOTICE, APPROVED).replace(OLD_PROD, APPROVED)
    t, n_leg = LEGEND.subn(NEW_LEGEND, t)          # 凡例(先に処理: 凡例内の見本spanもPAUSE_SPANに一致するため)
    t, n_span = PAUSE_SPAN.subn("", t)
    if t != o:
        open(path, "w", encoding="utf-8", newline="").write(t)
    return {"path": path, "approved_notice_count": t.count(APPROVED), "pause_spans_removed": n_span, "legend_replaced": n_leg,
            "left_9208": t.count("&#9208;"), "left_old_wording": t.count("参考に、AIが編集・構成") + t.count("ではなく、AIが編集した意見")}


if __name__ == "__main__":
    os.chdir(ROOT)
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps([fix(f"{DEST}/index.html"), fix(f"{DEST}/preview_segments_01.html")], ensure_ascii=False, indent=1))
