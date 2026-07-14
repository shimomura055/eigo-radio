# gather_topic.py - ネタ収集エージェント(工程①②の自動化・試作版)
#
# これまで「Claudeが検索してTOPIC_PACKAGEを手書きする」でやっていた作業を、
# OpenAI Responses APIのWeb検索ツールに肩代わりさせる試作。
#
# 二段構えの設計:
#   ①調査フェーズ(Web検索あり): ジャンルを指定すると、今一番盛り上がっている
#     話題を見つけ、複数の独立した情報源の見出し・リード文を集めて
#     生の調査メモ(プレーンテキスト)を書く。
#   ②整形フェーズ(Web検索なし): その調査メモを、generate_test.pyが読める
#     TOPIC_PACKAGE形式のJSONに厳密に変換する。
#
# 検索と厳密なJSON出力を1回のリクエストに混ぜると崩れやすいため、
# あえて2段階に分けている。
#
# 使い方:
#   python gather_topic.py --genre="阪神タイガース"

import json
import re
import sys
from datetime import date
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

MODEL_SEARCH = "gpt-5.6-luna"  # 調査フェーズ用(generate_test.pyのMODEL_PLANと同じ格)
TODAY = date.today().strftime("%B %d, %Y")

# ============================================================
# ブロック1: 起動オプションの読み取り(--genre=)
# ============================================================
GENRE = None
for arg in sys.argv:
    if arg.startswith("--genre="):
        GENRE = arg.split("=", 1)[1]
if not GENRE:
    raise SystemExit('ジャンルを指定してください。例: python gather_topic.py --genre="阪神タイガース"')

print(f"ジャンル: {GENRE}")

# ============================================================
# ブロック2: 調査フェーズ(Web検索ツールで生の調査メモを書かせる)
# ============================================================
RESEARCH_PROMPT = f"""You are a news researcher for a Japanese English-learning podcast about "{GENRE}".
Today is {TODAY}.

Search the web for recent news (prioritize the last 7 days) about this topic.

Your job:
1. Identify the SINGLE most newsworthy, emotionally engaging recent event or storyline -
   not just any news item, but the one that independent sources are treating as the main
   story right now (dramatic, surprising, or emotionally resonant - the kind of thing a fan
   would want to keep following).
2. Gather this from AT LEAST 4 independent, reputable sources (news outlets, official
   team/league/artist sites).
3. For each source, note: the outlet name, their headline, and their opening/lead sentence.
   ALWAYS PARAPHRASE IN YOUR OWN WORDS - never quote source text verbatim. This is a strict
   copyright requirement.
4. Separately list:
   - VERIFIED FACTS: numbers, dates, names, outcomes explicitly confirmed by at least one source.
   - GENERAL KNOWLEDGE: background context you already know that helps explain the story.
   - CONTESTED / SINGLE-SOURCE: claims attributed to only one outlet, or disputed details.
5. PLAY-BY-PLAY AGENCY RULE: for any sequence of in-game events (hits, errors, walks, goals,
   fouls, saves, etc.), always state WHO did WHAT, in plain active voice. Never write a passive
   sentence like "faced a bases-loaded situation after a hit, an error, and a walk" that hides
   who was pitching/playing when those events happened - this kind of phrasing gets
   misread downstream as "inherited a mess someone else created" even when the same
   person caused it. If the same player/pitcher was involved in both creating and resolving
   a situation, say so explicitly (e.g. "X allowed the leadoff hit himself, then walked a batter,
   before escaping the jam he had created").
6. Note whether the story involves Japanese individual people's names that could plausibly
   be romanized more than one way (yes/no, and which names).

Write your findings in plain text under these exact headings:
## MAIN STORY
## VERIFIED FACTS
## GENERAL KNOWLEDGE
## CONTESTED OR SINGLE-SOURCE
## SOURCE HEADLINES
(one per line, format: "Outlet: paraphrased headline")
## SOURCE LEAD SENTENCES
(one per line, format: "Outlet: paraphrased gist of their opening line")
## NAME CHECK NEEDED
(yes/no, and which names if yes)
"""

print()
print("工程①: Web検索で調査中(数十秒かかることがあります)...")
research = client.responses.create(
    model=MODEL_SEARCH,
    input=RESEARCH_PROMPT,
    tools=[{"type": "web_search"}],
)
research_notes = research.output_text.strip()

print("  → 調査メモを取得しました(下記に一部を表示)")
print("-" * 60)
print(research_notes[:500] + ("..." if len(research_notes) > 500 else ""))
print("-" * 60)

# ============================================================
# ブロック3: 整形フェーズ(調査メモ→TOPIC_PACKAGE形式のJSON)
# ============================================================
STRUCTURE_PROMPT = f"""Convert the research notes below into a TOPIC_PACKAGE JSON object for a
podcast script generator. Follow the schema and formatting EXACTLY - another program will
read this JSON directly.

Research notes:
{research_notes}

IMPORTANT: When converting play-by-play sequences into the "facts" field, preserve WHO did
WHAT in active voice. Do not flatten a sequence into a passive phrase (e.g. "faced a
bases-loaded situation after a hit, an error, and a walk") that could be misread as someone
else having created the situation - if the research notes are ambiguous about who was
involved, keep that ambiguity explicit rather than smoothing it into a cleaner-sounding
but less accurate sentence.

Return ONLY valid JSON in this exact schema:
{{
  "topic": "one sentence, present tense, describing the story (this becomes the episode's TOPIC line)",
  "facts": "a single multi-line string formatted EXACTLY like this template (keep the section headers verbatim):\\n\\nVERIFIED FACTS (confirmed by <comma-separated outlet names> - use as-is, do not invent numbers/quotes beyond these):\\n- fact 1\\n- fact 2\\n\\nCONTESTED / SINGLE-SOURCE (attribute clearly, do not present as settled fact):\\n- claim 1 (or omit this section's bullets and just keep the header if none)\\n\\nGENERAL KNOWLEDGE (you may explain these established concepts from your own knowledge):\\n- concept 1\\n\\nSPECULATION (encouraged, but always clearly framed, e.g. \\"If X happens...\\"):\\n- speculation 1",
  "headlines": ["Outlet: paraphrased headline", "Outlet: paraphrased headline", "..."],
  "article_summaries": "a single multi-line string formatted EXACTLY like: \\"Lead sentences by outlet (paraphrased close to the original opening line, not verbatim):\\n\\nOutlet: paraphrased gist.\\n\\nOutlet: paraphrased gist.\\"",
  "needs_name_check": true or false
}}"""

print()
print("工程②: TOPIC_PACKAGE形式に整形中...")
res = client.chat.completions.create(
    model=MODEL_SEARCH,
    messages=[{"role": "user", "content": STRUCTURE_PROMPT}],
    response_format={"type": "json_object"},
)
package = json.loads(res.choices[0].message.content)

# ============================================================
# ブロック4: 保存と表示
# ============================================================
slug = re.sub(r"[^\w]+", "_", GENRE).strip("_")
json_path = f"topic_package_{slug}_{date.today().isoformat()}.json"
py_path = f"topic_package_{slug}_{date.today().isoformat()}.py"

with open(json_path, "w", encoding="utf-8") as f:
    json.dump(package, f, ensure_ascii=False, indent=2)


def to_py_literal(value):
    """
    JSONから読み込んだ値(true/false/null)を、そのままPythonコードとして
    貼り付けても動く形の文字列に変換する。
    - bool/None: repr()を使うとPythonのTrue/False/Noneになる(JSONのtrue/falseとの
      取り違え事故を防ぐのが狙い)。
    - 長い複数行の文字列(facts/article_summaries): 読みやすいtriple-quote形式にする。
    - それ以外の文字列・リスト: repr()に任せる(引用符の混在も自動で処理される)。
    """
    if isinstance(value, bool) or value is None:
        return repr(value)
    if isinstance(value, str) and "\n" in value and '"""' not in value:
        return f'"""{value}"""'
    return repr(value)


def build_topic_package_py(pkg):
    lines = ["TOPIC_PACKAGE = {"]
    for key in ["topic", "facts", "headlines", "article_summaries", "needs_name_check"]:
        lines.append(f"    {key!r}: {to_py_literal(pkg.get(key))},")
    lines.append("}")
    return "\n".join(lines)


with open(py_path, "w", encoding="utf-8") as f:
    f.write(build_topic_package_py(package) + "\n")

print()
print(f"{json_path} に保存しました(記録用)。")
print(f"{py_path} に保存しました(generate_test.pyへの貼り付け用・Python形式)。")
print("=" * 60)
print("【中身の確認(人間の目視チェック用)】")
print("トピック:", package.get("topic"))
print()
print("見出し一覧:")
for h in package.get("headlines", []):
    print(" -", h)
print()
print("人名確認が必要か:", package.get("needs_name_check"))
print("=" * 60)
print()
print(f"内容を確認し、問題なければ {py_path} の中身をそのまま")
print("generate_test.py の TOPIC_PACKAGE ブロックに貼り付けてください。")
print("(true/false→True/Falseの手直しは不要になっています)")