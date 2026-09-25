# ============================================================
# er019_family_x_pointless_scaffold_01.py
# NEWS-FAMILY-X-POINTLESS-TRIAL-01 Phase B
# ============================================================
# 設計書: docs/pm/recon_family_x_pointless_trial_01.md (A-3)
#
# Family X(Point構造廃止・3分割)向けの記事分割・Comment生成。
# Point前提が強く残る箇所(3分割ロジック・Comment 3/4のrole文言)のみを
# このファイルにコピーして変更する。Comment 1/2・Preview role・
# run_support_text・Key Phrase関連は、既存Family Aモジュール
# (er003_v1_b1_scaffold_01_generate.py = b1s)から無変更のまま
# importして呼ぶ(Point前提を持たないため)。
#
# 本Trialは既存Family A記事(article.md)のMain Story部分のみを再利用し、
# Writerの再実行は行わない(Point節は内容ごと破棄する、
# ユーザー指示どおり)。Key Phraseは生成しない(このTrialでは不要)。
#
# Family A側ファイル(er003_v1_n3_01_scaffold_generate.py等)は
# 一切変更しない(読み取り専用でimportもしない。低レベルの
# run_support_text/role文言のみb1s経由で流用する)。

from __future__ import annotations

import json
import os
import re

import er003_v1_b1_scaffold_01_generate as b1s

# ============================================================
# 記事本文の分割(title / part1 / part2 / part3 / in_one_line)
# ============================================================
_MD_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")


def _strip_markdown_bold(s: str) -> str:
    return _MD_BOLD_RE.sub(r"\1", s)


def split_article_text_3way(text: str) -> dict:
    """既存Family A article.md(Title→Main Story→###見出し×2[Point]→
    ## In one line)からMain Story部分だけを取り出し、3分割する。
    Point節(###見出し以降、## In one lineより前)は内容ごと完全に破棄する
    (見出しテキスト・本文のいずれも使わない)。

    3分割点は、既存split_article_text()(er003_v1_n3_01_scaffold_
    generate.py:104-159)の2分割ロジック(隣接差絶対値最小化)と同じ
    考え方を3パートへ一般化したもの: 段落境界の全組み合わせのうち、
    3パートの(最大語数-最小語数)が最小になる組を選ぶ。"""
    title_match = re.match(r"^#\s+(.+?)\s*\n", text)
    title = title_match.group(1).strip() if title_match else ""
    body_start = title_match.end() if title_match else 0

    h3_matches = list(re.finditer(r"^###\s+(.+?)\s*$", text, flags=re.MULTILINE))
    in_one_line_match = re.search(r"^##\s+In [Oo]ne [Ll]ine[…\.]*\s*\n(.+)", text, flags=re.MULTILINE | re.DOTALL)
    if not in_one_line_match:
        raise RuntimeError("『## In one line…』見出しが見つかりません")

    # Point節(### 見出し)が存在すればMain Storyはそれより前まで、
    # 存在しなければ(将来Point節を持たない入力にも対応できるよう)
    # In One Lineの直前までをMain Storyとみなす。
    main_story_end = h3_matches[0].start() if h3_matches else in_one_line_match.start()
    intro_text = text[body_start:main_story_end].strip()
    in_one_line_text = in_one_line_match.group(1).strip()

    title = _strip_markdown_bold(title)
    intro_text = _strip_markdown_bold(intro_text)
    in_one_line_text = _strip_markdown_bold(in_one_line_text)

    paragraphs = [p.strip() for p in intro_text.split("\n\n") if p.strip()]
    if len(paragraphs) < 3:
        raise RuntimeError(f"Main Storyの段落数が3未満のため3分割できません(検出数: {len(paragraphs)})")

    word_counts = [len(re.findall(r"[A-Za-z']+", p)) for p in paragraphs]
    n = len(paragraphs)
    best_ij = None
    best_score = None
    for i in range(1, n - 1):
        for j in range(i + 1, n):
            c1 = sum(word_counts[:i])
            c2 = sum(word_counts[i:j])
            c3 = sum(word_counts[j:])
            score = max(c1, c2, c3) - min(c1, c2, c3)
            if best_score is None or score < best_score:
                best_score = score
                best_ij = (i, j)
    i, j = best_ij
    part1 = "\n\n".join(paragraphs[:i])
    part2 = "\n\n".join(paragraphs[i:j])
    part3 = "\n\n".join(paragraphs[j:])

    return {
        "title": title, "part1": part1, "part2": part2, "part3": part3,
        "in_one_line": in_one_line_text,
        "split_word_counts": {
            "part1": sum(word_counts[:i]), "part2": sum(word_counts[i:j]), "part3": sum(word_counts[j:]),
            "total": sum(word_counts), "paragraph_count": n, "split_indices": [i, j],
        },
    }


def reconstruct_article_text_no_point(parts: dict) -> str:
    """Point節を含まない、Family X用の「エピソード全文」(Preview生成の
    参考context用)を再構成する。Point節の内容はここにも一切含めない。"""
    return (f"# {parts['title']}\n\n{parts['part1']}\n\n{parts['part2']}\n\n{parts['part3']}\n\n"
            f"## In one line\n{parts['in_one_line']}")


# ============================================================
# Comment 3/4 role(新設、Point前提を除去): B1(英語出力)
# ============================================================
# 既存COMMENT_3_ROLE(b1s、"Bridge to Points")・COMMENT_4_ROLE(b1s、
# "Point Recovery")のPoint前提部分のみを書き換えたコピー。それ以外の
# 制約(答え先出し禁止・新Fact追加禁止・制作内部ラベル禁止・sentence数
# 断定禁止)はb1s版と同一の文言を維持する。
FAMILY_X_COMMENT_3_ROLE = """あなたはPodcastのナビゲーターです。リスナーは本文の第1部・第2部を
すでに聞き終わり、これから本文の第3部を聞きます。その間に流す、
Comment 3(役割: Mid-story Recovery + Bridge to Part 3)を書いてください。

役割: ここまでの内容の核心を短く整理し、第3部で何を聞けばよいかを示します。
第3部の結論を先に言ってはいけません。新しいFactを追加しないでください。
易しい英語で2〜3文にしてください。

【重要・出力への制約】出力する文章自体に"Part 1"・"Part 2"・"Part 3"・"Full Story"のような
制作内部の構造ラベルを含めないでください。リスナーは番組の内部構成を意識しません。"""

FAMILY_X_COMMENT_4_ROLE = """あなたはPodcastのナビゲーターです。リスナーは本文の第3部を含む
本文全体をすでに聞き終わり、これからIn One Line(結びのまとめ)を聞きます。
その間に流す、Comment 4(役割: Story Recovery + Bridge to In One Line)を
書いてください。

役割: 記事全体の意味を軽く回収し、In One Lineへつなぎます。本文を再説明し
すぎないでください。2〜3文にしてください。

注意: In One Lineの実際のsentence数は記事により異なります(1文とは限り
ません)。「一文で」「one sentenceで」「一言で」等、sentence数を断定する
表現は使わないでください。

【重要・出力への制約】出力する文章自体に"Part 1"・"Part 2"・"Part 3"・"Full Story"のような
制作内部の構造ラベルを含めないでください。リスナーは番組の内部構成を意識しません。"""


def get_client():
    return b1s.get_client()


def run_family_x_b1_scaffold(client, parts: dict, out_dir: str) -> dict:
    """B1(English)Preview/Comment1-4を生成する。Comment1/2/PreviewはPoint
    前提を持たないため既存b1s.COMMENT_1_ROLE/COMMENT_2_ROLE/PREVIEW_ROLEを
    無変更のまま流用する。Comment3/4のみ本ファイルのFAMILY_X_COMMENT_3/4_
    ROLE(Point前提を除去したコピー)を使う。"""
    print(f"[FAMILY-X-SCAFFOLD] B1 Comment 1生成開始({out_dir})...")
    c1_context = f"【これから聞く本文(第1部)】\n{parts['part1']}"
    c1 = b1s.run_support_text(client, b1s.COMMENT_1_ROLE, c1_context)

    print(f"[FAMILY-X-SCAFFOLD] B1 Comment 2生成開始({out_dir})...")
    c2_context = f"【すでに聞いた本文(第1部)】\n{parts['part1']}\n\n【これから聞く本文(第2部)】\n{parts['part2']}"
    c2 = b1s.run_support_text(client, b1s.COMMENT_2_ROLE, c2_context)

    print(f"[FAMILY-X-SCAFFOLD] B1 Comment 3生成開始({out_dir})...")
    c3_context = f"【本文(第1部)】\n{parts['part1']}\n\n【本文(第2部)】\n{parts['part2']}"
    c3 = b1s.run_support_text(client, FAMILY_X_COMMENT_3_ROLE, c3_context)

    print(f"[FAMILY-X-SCAFFOLD] B1 Comment 4生成開始({out_dir})...")
    c4_context = (f"【本文(第1部)】\n{parts['part1']}\n\n【本文(第2部)】\n{parts['part2']}\n\n"
                  f"【本文(第3部)】\n{parts['part3']}")
    c4 = b1s.run_support_text(client, FAMILY_X_COMMENT_4_ROLE, c4_context)

    print(f"[FAMILY-X-SCAFFOLD] B1 Preview生成開始({out_dir})...")
    preview_prompt_role = b1s.PREVIEW_ROLE.format(
        comment_1=c1.get("text") or "(生成失敗)", comment_2=c2.get("text") or "(生成失敗)")
    article_text_no_point = reconstruct_article_text_no_point(parts)
    preview_context = f"【エピソード全文(参考、新しいFactの追加禁止)】\n{article_text_no_point}"
    preview = b1s.run_support_text(client, preview_prompt_role, preview_context)

    results = {"preview": preview, "comment_1": c1, "comment_2": c2, "comment_3": c3, "comment_4": c4}
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(f"{out_dir}/audit", exist_ok=True)
    with open(f"{out_dir}/b1_support_texts.json", "w", encoding="utf-8") as f:
        json.dump({k: v.get("text") for k, v in results.items()}, f, ensure_ascii=False, indent=2)
    with open(f"{out_dir}/audit/b1_support_generation.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    return results
