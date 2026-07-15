# generate_test.py v9.0 - 汎用トピック対応 + カジュアル化 + 概要/キーワードコーナー分離
#                        + レベル切替(A2/B1/B2) + AUTOモード + 注目度シグナル分析
#
# 工程の全体像:
#   ①ネタ準備(手動: TOPIC/FACTS/ARTICLE_SUMMARIES) → ②注目度分析(任意)
#   → ③ブレスト → [人間採点 or AUTO] → 企画(①概要+②キーワード選定含む)
#   → 構成表[人間承認] → 台詞化 → 軽量推敲 → 論理検品(報告のみ)
#   → 概要・キーワードコーナー組み立て(機械的) → 保存
#
# 使い方:
#   python generate_test.py --level=B1 --topic=topic_package_NISA_2026-07-14.json
#   python generate_test.py --level=A2 --topic=topic_package_X.json --auto
#   python generate_test.py --level=B2 --topic=topic_package_X.json --auto --full-auto
#
# --topic=は、gather_topic.pyが出力したtopic_package_*.jsonのパスを指定する(必須)。

import glob
import json
import os
import random
import re
import shutil
import sys
from datetime import date
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

MODEL_PLAN = "gpt-5.6-luna"    # 企画・ブレスト・構成・注目度分析(速さ重視)
MODEL_WRITE = "gpt-5.6-terra"  # 台詞化・推敲・単語コーナー(品質重視)
TODAY = date.today().strftime("%B %d, %Y")

# ============================================================
# ブロック1: レベル規格(A2/B1/B2) + 起動オプションの読み取り
# ============================================================

# --- ブロック1-1: 3レベル分のレベル規格を辞書で定義 ---
# 別ファイルから読み込み。レベルはそちらで調整。
from levels import LEVELS

MAX_RETRY = 2  # 語数規格外だった場合、差し戻して作り直す回数の上限

# --- ブロック1-2: コマンドライン引数(--auto, --full-auto, --level=)を読み取る ---
# "--auto"を付けると人間採点(ブレスト30個の選定)をスキップ。環境変数AUTO_APPROVE=1でも同じ効果。
# "--full-auto"は、それに加えて構成表の承認関所(input())もスキップする、検証ループ専用モード。
# 本番の1話を出すときは、承認関所を残すため"--auto"のみを使うことを推奨する。
AUTO_MODE = "--auto" in sys.argv or "--full-auto" in sys.argv or os.getenv("AUTO_APPROVE") == "1"
FULL_AUTO_MODE = "--full-auto" in sys.argv or os.getenv("FULL_AUTO_APPROVE") == "1"
AUTO_SELECT_COUNT = 10  # AUTOモード時、ブレスト30個からランダムに何個採用するか

# --- ブロック1-3: --level=XX の指定を読み取り、実際に使うレベルを確定する ---
# 実行例: python generate_test.py --level=B1 --full-auto
# デフォルト値は持たない(tts_test.pyとデフォルトが食い違い、指定漏れ事故につながるため指定必須)
LEVEL_KEY = None
for arg in sys.argv:
    if arg.startswith("--level="):
        LEVEL_KEY = arg.split("=", 1)[1].upper()
if LEVEL_KEY is None:
    raise SystemExit("エラー: --level=A2/B1/B2 のいずれかを指定してください(例: python generate_test.py --level=B1 --full-auto)")
if LEVEL_KEY not in LEVELS:
    raise SystemExit(f"未知のレベルです: {LEVEL_KEY}(A2/B1/B2から選んでください)")

LEVEL = LEVELS[LEVEL_KEY]
MIN_WORDS = LEVEL["min_words"]
MAX_WORDS = LEVEL["max_words"]

# --- ブロック1-4: --topic=path/to/topic_package_X.json の指定を読み取る ---
# 実行例: python generate_test.py --level=B1 --topic=topic_package_NISA_2026-07-14.json
# デフォルト値は持たない(貼り付け・git checkoutでの手動運用に戻さないため指定必須)
TOPIC_PATH = None
for arg in sys.argv:
    if arg.startswith("--topic="):
        TOPIC_PATH = arg.split("=", 1)[1]
if TOPIC_PATH is None:
    raise SystemExit(
        "エラー: --topic=path/to/topic_package_X.json を指定してください"
        "(例: python generate_test.py --level=B1 --topic=topic_package_NISA_2026-07-14.json)"
    )

# レベルごとにファイルを分けるためのパターン。
# これにより candidates_A2_001.md と episode_B2_003.json のように混ざらなくなる。
CANDIDATES_PATTERN = f"candidates_{LEVEL_KEY}_*.md"
EPISODE_PATTERN = f"episode_{LEVEL_KEY}_*.json"

print(f"レベル設定: {LEVEL_KEY}({LEVEL['level_name']}) / AUTO_MODE={AUTO_MODE} / FULL_AUTO_MODE={FULL_AUTO_MODE}")


# ============================================================
# ブロック2: 今日のネタ(1トピック分をまとめて管理する)
# ============================================================
# TOPIC_PACKAGEはコードに直接書かず、--topicで指定した外部ファイル
# (gather_topic.py が出力する topic_package_*.json)から読み込む。
# これにより「貼り付け→確認→git checkoutで戻す」という手動運用と、
# それに伴う編集の巻き込み事故がなくなる。
REQUIRED_TOPIC_KEYS = ["topic", "facts", "headlines", "article_summaries", "needs_name_check"]

def load_topic_package(path):
    """--topicで指定された.jsonファイルを読み込み、TOPIC_PACKAGE辞書として返す。"""
    if not os.path.isfile(path):
        raise SystemExit(f"エラー: --topicで指定されたファイルが見つかりません: {path}")
    try:
        with open(path, "r", encoding="utf-8") as f:
            package = json.load(f)
    except json.JSONDecodeError as e:
        raise SystemExit(f"エラー: --topicのファイルが正しいJSONではありません({path}): {e}")
    missing = [k for k in REQUIRED_TOPIC_KEYS if k not in package]
    if missing:
        raise SystemExit(f"エラー: {path} のTOPIC_PACKAGEに必要なキーが不足しています: {', '.join(missing)}")
    return package

TOPIC_PACKAGE = load_topic_package(TOPIC_PATH)
print(f"トピック読み込み: {TOPIC_PATH}")

TOPIC = TOPIC_PACKAGE["topic"]
FACTS = TOPIC_PACKAGE["facts"]
HEADLINES = TOPIC_PACKAGE["headlines"]
ARTICLE_SUMMARIES = TOPIC_PACKAGE["article_summaries"]
NEEDS_NAME_CHECK = TOPIC_PACKAGE["needs_name_check"]

# --- 出だしのバリエーション(トピックが変わっても使い回せる) ---
OPENERS = [
    "MAYA saw a headline or a viral clip about this topic and can't stop thinking about it",
    "MAYA witnessed a small real-life scene today that connects to this topic (something she saw or overheard)",
    "MAYA heard a story from a friend that she can't believe is real, and wants LEO to confirm or destroy it",
    "MAYA and a friend argued about this topic over lunch, and she wants LEO to settle it",
    "MAYA just checked her phone and saw people online reacting strongly to this, and wants to know what actually happened",
]

# 締め方のスタイル一覧。「毎回同じ余韻+問いかけ」で終わるのを避けるため、
# OPENERSと同じ発想でランダムに1つ選ぶ。weightで出現頻度を調整でき、
# 従来の「余韻を残す絵+問いかけ」だけ低頻度の特別枠にしてある。
CLOSERS = [
    {
        "name": "curiosity_hook",
        "weight": 3,
        "instruction": (
            "End with a light, casual curiosity about what might happen NEXT in this ongoing "
            "story - not a profound life lesson. MAYA or LEO simply wonders out loud what comes "
            "next, like trailing off at the end of a chat with a friend. Keep closing_image very "
            "short (one plain sentence, not a big crafted picture). closing_question should be a "
            "small, low-stakes question about what happens next in the story itself - NOT a big "
            "question about the listener's own life."
        ),
    },
    {
        "name": "one_line_reaction",
        "weight": 3,
        "instruction": (
            "End with a short, plain reaction line from MAYA or LEO - something like a casual "
            "'huh, good for him' or 'wow, ok' level comment. No big closing picture, no rhetorical "
            "question, no life lesson. Set closing_image to that one short reaction line, and set "
            "closing_question to \"none\"."
        ),
    },
    {
        "name": "bookend",
        "weight": 3,
        "instruction": (
            "End by lightly circling back to the episode's opening line or situation (element 1, "
            "SCENE) - a quick, light callback that gives a sense of closure WITHOUT any big "
            "philosophical turn. Keep it short. closing_question should either be \"none\" or a "
            "very light, playful echo of the opening tone - not a big personal question."
        ),
    },
    {
        "name": "vivid_moment",
        "weight": 1,
        "instruction": (
            "One short vivid picture, set in the listener's own life, that crystallizes the "
            "episode's core insight - concrete enough to see, personal enough to feel. Then the "
            "closing question: plain, personal words. NEVER \"time will tell\"."
        ),
    },
]



# ============================================================
# ブロック2-5: 固有名詞の自動抽出+ローマ字表記の自動検証
# ============================================================
# 確認済みの正しい英語表記をキャッシュしておく辞書。
# 一度検索で確認した人名・固有名詞はここに蓄積され、次回以降は再検索しない。
NAME_GLOSSARY = {}

NAME_CHECK_PROMPT = """Extract ONLY real Japanese individual people's names from the text below - the kind of name that could plausibly be romanized in more than one way (e.g. surname-first vs given-name-first order, or ambiguous vowel/consonant choices).

Do NOT include:
- Any name that is not a Japanese person's name (foreign countries, foreign officials, organizations, agencies, companies, media outlets, places).
- Japanese team/organization names, even if written in Japanese.
- Any name already written in the text using standard Hepburn romanization that has no plausible alternative reading.

If there are no qualifying Japanese person names, return an empty list.

Text:
{text}

Return ONLY valid JSON: {{"names": ["name1 in original Japanese script", "name2"]}}"""

def extract_names(text):
    """FACTSに含まれる固有名詞を機械的に抜き出す(NER的な処理)。"""
    out = ask_llm(MODEL_PLAN, NAME_CHECK_PROMPT.format(text=text))
    return out.get("names", [])

def verify_romanization(name):
    """OpenAIのWeb検索ツール(Responses API)を使い、実在人物の正しい英語表記を確認する。"""
    res = client.responses.create(
        model=MODEL_PLAN,
        input=(f"Search the web to find the standard, official English romanization "
               f"(as used on their own official social media, official site, or Wikipedia) "
               f"of the name: {name}. "
               f"Return ONLY the romanized name, nothing else."),
        tools=[{"type": "web_search"}],
    )
    return res.output_text.strip()

def build_verified_glossary(text):
    """FACTS内の固有名詞を抽出し、1つずつ検索して正しい表記を確認、辞書として返す。"""
    names = extract_names(text)
    glossary = {}
    for name in names:
        if name in NAME_GLOSSARY:
            glossary[name] = NAME_GLOSSARY[name]  # 既知のものは再検索しない
            continue
        print(f"  人名確認中: {name} ...")
        romanized = verify_romanization(name)
        glossary[name] = romanized
        print(f"    → {romanized}")
    return glossary

# ============================================================
# ブロック3: 驚き生成レンズ(トピック非依存の8本) + ブレストのプロンプト
# ============================================================
LENSES = [
    {"tag": "歴史",  "rule": "HISTORICAL ECHO: a REAL, verifiable past moment - any era, any field - when society faced the SAME PATTERN as today's topic. One striking TRUE detail. No invented quotes."},
    {"tag": "鏡",    "rule": "THE MIRROR: a 30-second second-person scene from the listener's ordinary day TODAY, where this topic is quietly operating on them without their noticing."},
    {"tag": "機構",  "rule": "HIDDEN ENGINE: the surprising mechanism driving this (brain reward, incentive design, money flow) - shown through one concrete scene, never named abstractly."},
    {"tag": "逆説",  "rule": "COUNTERINTUITIVE TRUTH: a real finding or fact about this topic that contradicts what most listeners assume. State it concretely, not as a teaser."},
    {"tag": "極端",  "rule": "EDGE OF THE SPECTRUM: a real, verifiable extreme case showing how far this phenomenon actually goes, in one vivid scene."},
    {"tag": "受益者", "rule": "WHO PROFITS: who quietly makes money, power, or attention from this behavior - and what the system looks like from THEIR side of the counter."},
    {"tag": "尺度",  "rule": "VISCERAL SCALE: take one number, amount, or frequency from this topic and make it physically feelable (time, money, distance) - comparison drawn from the topic's own domain."},
    {"tag": "もし",  "rule": "WHAT IF: one clearly-framed speculative scene - where this could plausibly lead, OR an alternate world where it never existed - whichever fits the topic better."},
]

BRAINSTORM_PROMPT = """You are a creative director for an English-listening podcast for Japanese learners. Listeners choose this show because it makes them say "whoa" on their commute.

Today is {today}.
Topic: {topic}
Material:
{facts}

Your job: generate CANDIDATE EXAMPLES - vivid raw material, not a script.

Step 1 (anti-cliche): silently list the 5 most obvious examples every article gives about this topic. These are BANNED. Do not output them.

Step 2: for EACH lens below, generate exactly 5 examples beyond those cliches (total 30):
{lenses}

Rules for every example:
- A concrete SCENE or striking fact in 25 words or less - never an abstract category.
- One unexpected, specific detail. Second person ("you", "your") where possible.
- Real facts must be real and verifiable; speculation must sound clearly speculative.
- Simple English (feeds a B1-level episode).

Return ONLY valid JSON:
{{"examples": [{{"tag": "copy the lens tag exactly", "text": "..."}}]}}"""

# ============================================================
# ブロック4: 注目度シグナル分析(見出し/記事から焦点を測定する)
# ============================================================
FOCUS_SIGNAL_PROMPT = """You are a media analyst. Below are real headlines/titles about the same event, collected from independent sources.

Headlines/titles:
{headlines}

Task: identify which specific element (a person, a moment, a stat) is being treated as the LEAD/main story across these sources - not by your own opinion of what's interesting, but by counting what actually appears first, most often, and with the most emotional language (crowd reaction words, exclamation, etc.) across these independent headlines.

Return ONLY valid JSON:
{{"ranked_focus": [
    {{"element": "...", "evidence": "which headlines featured this, and how prominently", "rank": 1}}
  ]}}"""

FOCUS_SIGNAL_PROMPT_V2 = """You are a media analyst counting how independent outlets chose to lead their coverage of the same event.

Below are the OPENING LINES (lede) from multiple independent outlets, collected as close to verbatim as possible - your own interpretation should be minimal here. Each is labeled with its source.

Lead sentences by outlet:
{lead_sentences}

Task: do NOT judge which angle is more "interesting." Instead, literally COUNT which specific element (a person, a moment, a narrative arc) each outlet chose as its lede subject. Group outlets by which element they led with.

Return ONLY valid JSON:
{{"lede_tally": [
    {{"element": "...", "outlet_count": 0, "outlets": ["outlet1", "outlet2"], "rank": 1}}
  ],
  "notable_quotes": [
    {{"speaker": "...", "gloss": "paraphrased gist of what they said, not verbatim", "outlet": "..."}}
  ]}}"""

def build_focus_signal_text():
    """
    ここでは、見出し(HEADLINES)または記事要約(ARTICLE_SUMMARIES)をもとに、
    「世間が実際にどこへ注目していたか」を分析し、PLAN_PROMPTに埋め込むための
    テキストブロックを組み立てている。
    ARTICLE_SUMMARIESがあればそちらを優先(記事本文まで読める分、精度が高い)。
    どちらも空ならこの分析自体をスキップし、LLMの判断に任せる旨を明記する。
    """
    if ARTICLE_SUMMARIES.strip():
        print("工程(2)b: リード文から注目度シグナルを分析中(V2: リード文ベース)...")
        out = ask_llm(MODEL_PLAN, FOCUS_SIGNAL_PROMPT_V2.format(lead_sentences=ARTICLE_SUMMARIES))
    elif HEADLINES:
        print("工程(2)b: 見出しから注目度シグナルを分析中(V1: 見出しベース)...")
        out = ask_llm(MODEL_PLAN, FOCUS_SIGNAL_PROMPT.format(headlines="\n".join(f"- {h}" for h in HEADLINES)))
    else:
        return "(No focus signal collected for this topic - use editorial judgment.)"

    ranked = out.get("lede_tally", [])
    lines = [
        f"{f['rank']}. [{'MAIN FOCUS - build around this' if f['rank'] == 1 else 'supporting color only'}] "
        f"{f['element']} - led by {f['outlet_count']} outlet(s): {', '.join(f['outlets'])}"
        for f in ranked
    ]
    text = "FOCUS SIGNAL (counted from how independent outlets actually chose to lead their coverage - not your own judgment):\n" + "\n".join(lines)

    quotes = out.get("notable_quotes", [])
    if quotes:
        quote_lines = [f"- {q['speaker']}: {q['gloss']} ({q['outlet']})" for q in quotes]
        text += "\n\nNotable real quotes (paraphrased) that reveal what sources consider the story:\n" + "\n".join(quote_lines)

    text += ("\n\nINSTRUCTION: your core_wow and concept ladder MUST be built around the #1 ranked element. "
             "Elements ranked #2 or below may only appear as supporting color (image role) - they must never "
             "become the emotional center of the episode, even if they seem more \"interesting\" to you as a writer.")

    if ranked:
        print(f"  → rank1: {ranked[0]['element']}")
    return text

# ============================================================
# ブロック5: 道具(ファイル名の採番、話者名の正規化、語数カウント、LLM呼び出し)
# ============================================================
def next_number(pattern):
    files = glob.glob(pattern)
    nums = [int(re.search(r"(\d{3})", os.path.basename(f)).group(1))
            for f in files if re.search(r"(\d{3})", os.path.basename(f))]
    return max(nums, default=0) + 1

def norm_speaker(name):
    u = name.upper()
    if "MAYA" in u or u.endswith("AYA"):
        return "MAYA"
    if "LEO" in u:
        return "LEO"
    return "LEO"

def count_words(turns):
    return sum(len(t["text"].split()) for t in turns)

def overview_word_range(level):
    """概要(overview)の目安語数を、レベルのwpm_range平均値から動的に算出する(30〜40秒分)。"""
    lo, hi = level["wpm_range"].split("-")
    avg_wpm = (int(lo) + int(hi)) / 2
    return round(avg_wpm * 30 / 60), round(avg_wpm * 40 / 60)

def ask_llm(model, prompt):
    """OpenAIにプロンプトを送り、JSON形式で結果を受け取って辞書に変換する共通処理。"""
    res = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    return json.loads(res.choices[0].message.content)

def brainstorm_examples():
    """レンズを6本ランダムに選び、30個の候補例をLLMに生成させる(採点シートの中身の元)。"""
    lenses = random.sample(LENSES, 6)
    print("工程(3)a-1: 候補30個をブレスト中(レンズ: "
          + " / ".join(l["tag"] for l in lenses) + ")...")
    out = ask_llm(MODEL_PLAN, BRAINSTORM_PROMPT.format(
        today=TODAY, topic=TOPIC, facts=FACTS,
        lenses="\n".join(f'- tag "{l["tag"]}": {l["rule"]}' for l in lenses)))
    return out["examples"]

def create_sheet():
    """ブレスト結果を採点シート(candidates_XXX.md)として書き出し、人間の採点待ちにする。"""
    examples = brainstorm_examples()
    n = next_number(CANDIDATES_PATTERN)
    path = f"candidates_{LEVEL_KEY}_{n:03d}.md"
    lines = [
        f"# 採点シート {n:03d}({LEVEL_KEY})",
        f"# トピック: {TOPIC}",
        "# 記入方法: [ ] の中に 〇 / △ / × を記入。理由は一言でOK(空欄可)。",
        "# 〇=このまま採用 / △=惜しい(磨けば化ける) / ×=不採用",
        "# 記入して保存したら、もう一度 python generate_test.py を実行。",
        "",
    ]
    for i, ex in enumerate(examples, 1):
        lines.append(f'{i:02d}. [ ] <{ex["tag"]}> {ex["text"]}')
        lines.append("    理由: ")
        lines.append("")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    # このprint()は、シートが出来上がったことと、次に何をすべきかをユーザーに知らせるためのもの。
    print(f"採点シート {path} を作成しました({len(examples)}個)。")
    print("VS Codeで採点・保存後、もう一度このプログラムを実行してください。")

MARU = {"〇", "○", "◯", "o", "O"}
SANKAKU = {"△", "▲"}
BATSU = {"×", "x", "X", "✕", "☓"}

def parse_sheet(path):
    """人間が記入した採点シート(candidates_XXX.md)を読み込み、〇△×を構造化データに変換する。"""
    items = []
    current = None
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            m = re.match(r"^(\d{2})\.\s*\[(.*?)\]\s*<(.*?)>\s*(.*)$", line.strip())
            if m:
                mark_raw = m.group(2).strip()
                mark = ("〇" if mark_raw in MARU else
                        "△" if mark_raw in SANKAKU else
                        "×" if mark_raw in BATSU else "")
                current = {"no": int(m.group(1)), "mark": mark,
                           "tag": m.group(3), "text": m.group(4), "reason": ""}
                items.append(current)
            elif current and line.strip().startswith("理由:"):
                current["reason"] = line.strip()[3:].strip()
    return items

if NEEDS_NAME_CHECK:
    print("工程(2)c: 固有名詞のローマ字表記を検索・検証中...")
    verified_glossary = build_verified_glossary(FACTS)
    NAME_GLOSSARY.update(verified_glossary)
else:
    print("工程(2)c: 今回のトピックは日本語人名確認をスキップします")

# ============================================================
# ブロック6: メイン分岐(AUTOモード or 採点シートモード)
# ============================================================
if AUTO_MODE:
    # AUTOモードでは、採点シートのファイルは一切見ずに、その場でブレストして
    # ランダムにAUTO_SELECT_COUNT個を選ぶ。人間の好みを毎回インプットする必要がない
    # 反復テストのためのモード。
    print("⚡ AUTO_APPROVEモード: 人間採点シートをスキップします")
    examples = brainstorm_examples()
    chosen = random.sample(examples, min(AUTO_SELECT_COUNT, len(examples)))
    chosen_texts = [ex["text"] for ex in chosen]
    sheet_path = None  # ファイルなし = judgements移動もスキップする、という目印
else:
    sheets = sorted(glob.glob(CANDIDATES_PATTERN))
    if not sheets:
        create_sheet()
        raise SystemExit

    sheet_path = sheets[-1]
    items = parse_sheet(sheet_path)
    if not any(it["mark"] for it in items):
        print(f"{sheet_path} がまだ未記入です。〇△×を記入して保存後、再実行してください。")
        raise SystemExit

    maru = [it for it in items if it["mark"] == "〇"]
    sankaku = [it for it in items if it["mark"] == "△"]
    chosen = maru + sankaku[:max(0, 4 - len(maru))]
    if not chosen:
        print("〇も△もありません。シートを削除して再実行すると新しい30個が出ます。")
        raise SystemExit

    # このprint()は、採点結果の内訳(何個が〇/△/×だったか)を確認できるようにするためのもの。
    print(f"{sheet_path}: 〇{len(maru)} / △{len(sankaku)} / "
          f"×{len([i for i in items if i['mark'] == '×'])}")
    chosen_texts = [it["text"] for it in chosen]

# ============================================================
# ブロック7: 企画書(注目度シグナル反映 + カジュアル化 + 単語コーナー分離)
# ============================================================

# --- ブロック7-1: 注目度シグナルを先に計算しておく(ブロック4の関数を呼ぶ) ---
focus_signal_text = build_focus_signal_text()

# --- ブロック7-2: 出だしと締め方をランダムに1つずつ選ぶ ---
opener = random.choice(OPENERS)
closer = random.choices(CLOSERS, weights=[c["weight"] for c in CLOSERS], k=1)[0]

# --- ブロック7-2b: 概要(overview)の目安語数をレベルのwpmから算出 ---
OVERVIEW_MIN, OVERVIEW_MAX = overview_word_range(LEVEL)

# --- ブロック7-3: 企画書生成プロンプト本体 ---
PLAN_PROMPT = f"""You are the editor-in-chief of an English-listening podcast for Japanese learners. Every episode must be genuinely fascinating - never like a textbook or a news brief.

Today is {TODAY}.
Topic: {TOPIC}
Material:
{FACTS}

{focus_signal_text}

The editor liked these candidate examples. They are an OPTIONAL palette, not requirements - structure comes first, and examples are used only where they serve it. Cutting most of them is fine:
{json.dumps(chosen_texts, ensure_ascii=False, indent=2)}

SPECIFICITY TEST (apply this while designing every element below, especially core_wow and the "domain" example): before settling on an angle, mentally strip out the person's name and every specific date/number, and read the domain's beat-by-beat explanation again. If it STILL reads as a complete, satisfying explanation of a generic mechanism (a release-timing pattern, a procedural fact, "how X usually works") with the identifying details simply plugged back in, it FAILS the test - inserting a name, a date, or a quote into a generic structure does not make that structure specific, it only decorates it. A passing domain is one where the beat-by-beat explanation becomes incoherent or empty once you remove the specific person/moment - because the explanation IS that person's specific choice, feeling, or circumstance, not a generic pattern illustrated by them.

FIRST-PERSON MATERIAL PRIORITY: if the Material above contains any first-person material (a quote, blog post, or interview comment from the person/people at the center of the story - their own words about their own feelings, choices, or process), it must be the SUBJECT of "domain", not a decoration added to a structural/procedural domain. Concretely: the domain's 2-3 beats must be built around what this material reveals about them (their feeling, their reasoning, their specific situation), and any structural/procedural facts (release timing, rankings, schedules) must be demoted to "contrast", "image", or supporting evidence for that emotional throughline - never the throughline itself. If you choose not to make the first-person material the domain's subject, you must explain in domain_rationale, in concrete terms, why the emotional material was too thin to build 2-3 beats on - "the structural story was more interesting" is NOT an acceptable reason.

Design these elements:

1. SCENE: {opener}. Write MAYA's exact casual opening line for this situation. She knows only the surface; LEO knows the substance.

2. CONCEPT LADDER: design an ordered list of 2-3 concepts the episode introduces, each building on the previous and raising the stakes. Less is more: an episode that truly lands ONE big idea beats an episode that covers four. A common shape: (a) the surface-level hook - relatable and immediately interesting on its own; (b) the real mechanism underneath - what is actually driving this; (c) what it means for the listener's own life. Adapt this shape to fit the topic at hand; do not force unrelated concepts into it just to fill rungs. IMPORTANT: the ladder's rungs are what the beat sheet is required to follow strictly (a later stage cannot fix an earlier stage's angle) - so the SPECIFICITY TEST and FIRST-PERSON MATERIAL PRIORITY defined above apply to EVERY rung of this ladder, not just to the "domain" in section 4. If first-person material exists, the ladder's throughline (not just its domain beat) must be built around it - a ladder whose rungs are all structural/procedural (a release timeline, a schedule, a ranking) while the person's own words are saved for a single later rung is exactly the failure this test exists to catch, and it will fail even if section 4/5 correctly name the domain as the first-person material, because the beat sheet follows the ladder, not the domain_rationale.

3. TENSION: design MAYA's reasonable pushback (a natural doubt, counterexample, or "but isn't this normal?" objection a smart layperson would raise) vs LEO's answer (why it doesn't fully hold up, or what makes this moment different). If a real comparative or historical example strengthens LEO's answer, use exactly ONE - the strongest. No second one anywhere in the episode.

4. EXAMPLE PLAN: assign roles only to examples that genuinely serve the structure:
   - "domain": the ONE impact area for the deep dive (2-3 connected beats) - must pass the SPECIFICITY TEST above.
   - "contrast": the ONE historical/comparative moment (see 3), if any.
   - "image": one-line color dropped inside LEO's explanation - never a topic, never its own beat.
   - "cut": everything else. Cutting is good editing.

5. DOMAIN RATIONALE: in one or two sentences, state what remains of the domain's explanation once the person's name and specific dates/numbers are stripped out (per the SPECIFICITY TEST) - if nothing coherent remains, that confirms a pass. Also explicitly confirm whether the Material contained first-person material and, if so, why it was or was not made the domain's subject (see FIRST-PERSON MATERIAL PRIORITY). Finally, explicitly check: does the CONCEPT LADDER's throughline (not just the domain) also center on this same subject? If the ladder's rungs are actually built around a different, more structural/procedural throughline than the domain, say so plainly - do not claim consistency that is not there.

6. OVERVIEW: write a {OVERVIEW_MIN}-{OVERVIEW_MAX} word (about 30-40 seconds at this level's speaking pace) narrator intro that airs BEFORE the dialogue begins, in plain English using {LEVEL['vocab_range']} (do NOT translate or simplify this into Japanese - it stays in English at every level). It must ONLY set up the situation the listener is about to hear about (who/what/where, in broad strokes), addressing the listener directly in a warm narrator voice (e.g. "Today, we're talking about..."). It must NOT reveal the conclusion, the core_wow chain, any surprising twist, or how the tension resolves - all of that must stay completely fresh for the dialogue itself. If the overview gives away the payoff, it fails its job.

7. KEYWORDS: choose 5 to 7 vocabulary PHRASES or collocations (never a single isolated word) that will be PRE-TAUGHT in a separate keyword corner before the dialogue starts, so the dialogue itself can use them naturally WITHOUT any explanation ritual. Prioritize, in this order:
   (a) any phrase without which the dialogue's meaning would not land - always include these regardless of the rest below.
   (b) phrases likely to reappear across OTHER episodes in the same genre, beyond just this topic (e.g. "military facility", "peace talks", "nuclear program" for a geopolitics episode) - favor these over one-off phrasing specific only to today.
   (c) phrase/collocation units over single words (e.g. "take off", "look forward to", "stock market").
   (d) fit for the {LEVEL['level_name']} level.
   For each phrase, also give a natural, idiomatic Japanese translation.
   Separately, if (and only if) the episode's core requires ONE genuinely specialist term or acronym that ordinary people would not know, name it as "specialist_term" - this one word keeps an in-dialogue moment where MAYA asks and LEO explains. NEVER pick a word or acronym that matches the topic's own name/label (e.g. if the topic is about NISA, "NISA" itself cannot be the specialist_term) - that term belongs in the SCENE/opening or the early dialogue where it gets introduced naturally, not saved for a mid-episode "reveal a jargon word" beat. specialist_term exists only for a secondary, peripheral technical term encountered while digging into the topic, not the topic's own name. If no such secondary term is truly needed, set specialist_term to "none". Every other technical or academic term is BANNED from the episode - the concept must be expressed in everyday words without ever naming it.

8. CLOSING IMAGE + QUESTION: {closer['instruction']}

9. REGISTER: this is two friends gossiping over coffee about something juicy - never a lecture, never a report. Concrete people doing concrete things, not abstract nouns doing things to each other. Test: if a sentence would fit in a research summary, it is wrong - rewrite it as something you would actually say out loud to a friend.

Return ONLY valid JSON:
{{
  "scene": "MAYA's exact opening line + one sentence of situation",
  "concept_ladder": [{{"concept": "...", "reveal_bridge": "..."}}],
  "tension": "the yes-but axis in one sentence",
  "core_wow": "one sentence: the chain that makes this big",
  "deep_dive": "the ONE domain + its 2-3 beats",
  "example_plan": [{{"example": "...", "role": "domain / contrast / image / cut", "note": "where it serves"}}],
  "domain_rationale": "1-2 sentences: why the domain passes the SPECIFICITY TEST, and whether first-person material existed and was/wasn't used",
  "overview": "the 30-40 second narrator intro, English only, situation setup without any conclusion/wow/twist",
  "keywords_plan": [{{"phrase": "English phrase or collocation", "japanese": "natural Japanese translation"}}],
  "specialist_term": "... or none",
  "closing_image": "the closing line/picture, following the style instruction given above",
  "closing_question": "the closing question following the style instruction above, or \"none\" if the chosen style has no question",
  "tone_notes": "mood and energy notes"
}}"""

print()
print("工程(3)a-2: 企画書を作成中...")
brief = ask_llm(MODEL_PLAN, PLAN_PROMPT)

# --- keywords_planの個数検証 + 簡単なリトライ(語数チェック&差し戻しと同じ考え方) ---
# LLMがまれに「5〜7個」という指示を守らず少数しか返さないことがあるため、
# 規定を下回った場合は当該部分だけを再生成する(1回のみ試みる。深追いはしない)。
MIN_KEYWORDS = 5
KEYWORDS_RETRY_PROMPT = f"""The keywords_plan below was generated for a podcast episode brief, but it has only {{count}} phrase(s), while the rule requires 5 to 7. Regenerate ONLY the keywords_plan, following the same selection rules as before.

Topic: {TOPIC}
Material:
{FACTS}

Episode brief so far (for context):
{{brief_context}}

KEYWORDS RULES: choose 5 to 7 vocabulary PHRASES or collocations (never a single isolated word). Prioritize, in this order:
   (a) any phrase without which the dialogue's meaning would not land - always include these regardless of the rest below.
   (b) phrases likely to reappear across OTHER episodes in the same genre, beyond just this topic.
   (c) phrase/collocation units over single words (e.g. "take off", "look forward to", "stock market").
   (d) fit for the {LEVEL['level_name']} level.
   For each phrase, also give a natural, idiomatic Japanese translation.

Return ONLY valid JSON:
{{{{"keywords_plan": [{{{{"phrase": "English phrase or collocation", "japanese": "natural Japanese translation"}}}}]}}}}"""

current_count = len(brief.get("keywords_plan", []))
if current_count < MIN_KEYWORDS:
    print(f"  ⚠ keywords_planが{current_count}個しかありません(規定5〜7個)。再生成を試みます...")
    retry_out = ask_llm(MODEL_PLAN, KEYWORDS_RETRY_PROMPT.format(
        count=current_count,
        brief_context=json.dumps(brief, ensure_ascii=False, indent=2)))
    retry_count = len(retry_out.get("keywords_plan", []))
    if retry_count >= MIN_KEYWORDS:
        brief["keywords_plan"] = retry_out["keywords_plan"]
        print(f"  → 再生成後: {retry_count}個に更新しました")
    else:
        print(f"  → 再生成でも{retry_count}個止まりでした。現状のまま続行します(要人間確認)")

# このprint()ブロックは、企画書の要点だけを人間が目視で確認できるようにするためのもの。
# 全文はJSONに入っているので、ここでは概要だけ表示している。
print()
print("【企画書(要点)】")
print("場の設定  :", brief.get("scene"))
print("対立軸    :", brief.get("tension"))
print("一本掘り  :", brief.get("deep_dive"))
print("固有性の根拠:", brief.get("domain_rationale"))
print("概要      :", brief.get("overview"))
print("キーワード:", ", ".join(f"{k['phrase']}({k['japanese']})" for k in brief.get("keywords_plan", [])))
print("専門用語  :", brief.get("specialist_term"))
print("締めスタイル:", closer["name"])
print("締めの絵  :", brief.get("closing_image"))
print("締めの問い:", brief.get("closing_question"))

# ============================================================
# ブロック8: 構成表(二人芝居スキーマ) + 人間の承認関所
# ============================================================

BEAT_PROMPT = """You are the story architect of an English-listening podcast for Japanese learners. Convert the brief below into a BEAT SHEET: the episode's complete structural blueprint. This is NOT dialogue - it is the ordered plan the dialogue will follow exactly.

Today is {today}.
Brief:
{brief}

TWO-ACTOR RULE (most important): every beat is one exchange with TWO separate parts:
- "maya_move": what MAYA herself says or does, in one short sentence. It must be something MAYA can plausibly do (react, ask, half-restate, push back). NEVER assign MAYA's move to LEO, and never put MAYA's actions inside leo_point.
- "leo_point": the ONE thing LEO conveys in this beat - written as the gist he would BLURT OUT to a friend, NOT as an information sentence for a report.
If LEO poses a rhetorical question to himself as a bridge, that is part of leo_point, and maya_type for that beat is "reaction".

Other rules:
- 8 to 11 beats, strict narrative order. Total word budget: about {total_words_target}. Vary budgets: reaction/scene beats light, deep explanation beats heavier.
- Follow the concept ladder strictly: never let a later concept appear in an earlier beat. Each rung ends with its reveal bridge.
- One idea per beat. NO idea, example, or explanation may appear in two beats.
- TENSION-BEAT RULE: if the brief's tension relies on a comparative/historical example, exactly ONE such example may appear in the whole episode, inside the tension beat. maya_move there: she vaguely recalls or raises it in general terms, without specific names/brands where possible; LEO supplies the specifics. No second such example anywhere else in the episode.
- IMAGE RULE: "image"-role material never gets its own beat and never carries a new word. Attach it as optional one-line color inside an existing beat's leo_point, or drop it.
- KEYWORDS: the listener has already learned today's keyword phrases in a keyword corner before the dialogue. Each phrase from keywords_plan appears naturally in exactly ONE beat (mark it in "keyword", copying the phrase text) - LEO or MAYA just USES it in context, nobody explains it.
- SPECIALIST TERM: if the brief names a specialist_term (not "none"), exactly ONE beat contains its ask-and-explain moment (MAYA asks, LEO explains plainly). No other term gets this treatment.
- JARGON BAN: no technical or academic term outside keywords_plan and specialist_term may appear in any beat.
- maya_type per beat, exactly one of: "question" / "reaction" (a short surprised or doubting line, OR a short acknowledgment showing she now understands or agrees, e.g. "oh, that makes sense" / "huh, I get it now" - neither version is a question) / "restate" (half-step restatement, may be slightly wrong) / "pushback".
  Rhythm: never more than 2 "question" beats in a row; after 2 questions the next must be reaction or restate.
- Beat 1 = the scene (MAYA's opening). Second-to-last beat: maya_move reacts in whatever way fits the chosen closing style - a personal takeaway for the "vivid_moment" style, or a lighter comment/callback/curiosity for the other styles - NOT a mechanical recap of vocabulary or concepts. Last beat: leo_point = the closing_image; if closing_question is not "none", it becomes the episode's FINAL line; otherwise the episode simply ends on leo_point, optionally with one short MAYA button line right after.

Additionally, for each beat, add a "rationale" field: one short sentence IN JAPANESE explaining, for a human reviewer, which specific piece of the brief this beat is built from (e.g. which fact, which concept_ladder rung, which lens, or which focus-signal insight) and what job this beat is doing in the episode's arc. This field is for human review only - it does not change what the beat itself says.

Return ONLY valid JSON:
{{"beats": [{{"id": 1, "rung": "a/b/c", "maya_move": "...", "maya_type": "question/reaction/restate/pushback", "leo_point": "...", "example": "... or none", "keyword": "... or none", "words": 70, "rationale": "..."}}],
  "total_words": {total_words_target}}}"""

print()
print("工程(3)a-3: 構成表(ビートシート)を作成中...")
beat_out = ask_llm(MODEL_PLAN, BEAT_PROMPT.format(
    today=TODAY,
    brief=json.dumps(brief, ensure_ascii=False, indent=2),
    total_words_target=int((MIN_WORDS + MAX_WORDS) / 2),
))
beats = beat_out["beats"]
planned_total = sum(b.get("words", 0) for b in beats)


# このprint()ブロックは、人間が「この構成でいいか」を承認するために全ビートを一覧表示している。
# 次のinput()が、実質的な人間の承認関所そのもの。
print()
print(f"【構成表】全{len(beats)}ビート / 予算合計 {planned_total} 語")
for b in beats:
    nw = f" キーワード:{b['keyword']}" if b.get("keyword") and b["keyword"] != "none" else ""
    ex = f" 例あり" if b.get("example") and b["example"] != "none" else ""
    print(f"  {b['id']:2d}. [{b['rung']}] ~{b.get('words')}語{nw}{ex}")
    print(f"      MAYA({b.get('maya_type','?')}): {b.get('maya_move','')}")
    print(f"      LEO : {b.get('leo_point','')}")
    if b.get("rationale"):
        print(f"      └ 根拠: {b['rationale']}")
print()

# rationaleは人間の確認用の追加出力であり、台詞化(DIALOGUE_TEMPLATE)に渡す情報は
# これまでと完全に同じにするため、ここで取り除いたコピーを別途作る(プロセス自体は不変)。
beats_for_dialogue = [{k: v for k, v in b.items() if k != "rationale"} for b in beats]

if FULL_AUTO_MODE:
    print("⚡ FULL_AUTO_MODE: 構成表の承認関所をスキップし、そのまま台詞化に進みます")
else:
    answer = input("この構成で台詞化に進みますか? [Enter=進む / q=中止] : ")
    if answer.strip().lower() == "q":
        raise SystemExit("中止しました(シートは残っています)。")

# ============================================================
# ブロック9: 台詞化(構成表→対話)+ 語数の範囲検品(両側)
# ============================================================
DIALOGUE_TEMPLATE = """You are an expert dialogue writer for an English-listening podcast for Japanese learners. Convert the beat sheet into a natural dialogue between MAYA and LEO. The beat sheet is LAW: follow beat order, both actors' assignments, and word budgets exactly.

Today is {today}. Treat any dates before today as the past.

# Beat sheet (the law)
{beats}

# Material rules (three layers)
{facts}
- Layer 1 VERIFIED FACTS: never invent numbers, dates, or quotes beyond these.
- Layer 2 GENERAL KNOWLEDGE: explain established concepts vividly in your own words.
- Layer 3 SPECULATION: encouraged, always signaled ("Imagine if...", "If he's right...").

# SPOKEN REGISTER - the most important section. It overrides everything else about style.
This is NOT written English read aloud. It is two friends chatting. Concrete laws:

1. PERSON AS SUBJECT: people do and feel things. An abstract noun must never act on the world.
   - BAD:  A staged post can make an imagined life feel reachable for a moment.
   - GOOD: You stage one photo, and for a second you honestly feel like that is your real life.

2. NO WRITERLY PHRASES: if a phrase could appear in a novel or an essay, it is banned. Replace it with what a person would actually blurt out.
   - BAD:  It can replace your face with an impossible standard. The result is synthetic, but it can look better than any real morning.
   - GOOD: It gives you a face that does not even exist. Total fake. And the annoying part, it still looks better than my actual face at 7 a.m.

3. REACT FIRST, EXPLAIN SECOND: LEO may open with a short spoken reaction (Right?, Oh it gets worse, Honestly? Yes) before his point.

4. REDUNDANCY IS GOOD: real chat says the important thing twice in different plain words. A listener at 70 percent attention must still catch the point. Do not maximize information per word - maximize how easily the ONE point lands.

5. FRAGMENTS ARE LEGAL: Faster than tying your shoes is a perfectly good spoken sentence.

6. DISCOURSE MARKERS: use natural spoken glue (I mean, you know, right?, kind of, wait) a few times per episode - enough to sound alive, not so much it becomes a tic.

7. SELF-TEST for every single turn: would this exact sentence survive being said out loud to a friend over coffee? If it sounds like a report, rewrite until it doesn't.

# How to convert each beat
- Each beat becomes: MAYA's turn realizes her maya_move (in the form of her maya_type), then LEO's leo_point is delivered as TWO separate LEO turns with ONE short MAYA interjection between them (see LEO SPLIT RULE below) - so a beat with a leo_point normally yields 4 turns (MAYA move -> LEO part 1 -> MAYA interjection -> LEO part 2), not 2-3. Stay near the beat's word budget across the two LEO turns combined.
- LEO SPLIT RULE (applies to every beat that has a leo_point, no exceptions): split leo_point at a natural break in its own content into two LEO turns, each roughly half to two-thirds of the original leo_point's length - do not cut content, just divide where it already breaks naturally. Between the two LEO turns, insert ONE short MAYA interjection line: a brief exclamation or reaction (e.g. "Oh...", "Wait, really?", "Huh."), NOT a question. This interjection is separate from the beat's own maya_move/maya_type - it does not count toward the "no more than 2 question beats in a row" rhythm rule, and it is not itself a beat.
- maya_type "reaction": a short surprised or doubting line, OR a short acknowledgment showing she now understands or agrees (e.g. "oh, that makes sense", "huh, I get it now") - neither version is a question.
- maya_type "restate": she rephrases LEO's previous point a half-step, sometimes slightly wrong; LEO gently corrects.
- MAYA never introduces facts, names, or dates. Where the sheet says she vaguely recalls, keep it name-free; LEO supplies specifics.
- TENSION-BEAT RULE: only the single comparative/historical example in the beat sheet (if any) may appear. No other such example may be named.
- Q&A CONTRACT: when MAYA asks, LEO's FIRST sentence is a direct declarative answer matching the question type (how->mechanism, how fast->speed in real-world terms, why->reason). "Imagine" may appear only AFTER that first sentence, and at most 2 turns in the episode may start with "Imagine".
- When a person is first named, LEO adds their role in a few words.
- Speakers strictly alternate.
- Today's keyword phrases were pre-taught before this dialogue in a keyword corner: use each naturally, never explain or define them mid-conversation.
- If the beat sheet contains a specialist-term beat, that is the ONLY ask-and-explain moment in the episode.
- JARGON BAN: outside the new words and the specialist term, do not use any word an ordinary person would not use over coffee. If you feel the need for a technical term, say the everyday version instead.
- CLOSING: LEO's final turn is at most 3 short sentences: one concrete picture, one plain line, then the question. If the listener cannot repeat the question from one hearing, it is too complex.

# Language constraints ({level_name}, TOEIC {toeic_range}) - MACHINE-CHECKED
1. Vocabulary: use the {vocab_range} of English wherever possible.
2. New words: only those in the beat sheet (proper nouns excluded from counting).
3. Sentences: average {avg_sentence_len} words or fewer. No more than one nested clause.
4. No culture-specific idioms. Reactions use very common words.
5. TOTAL LENGTH: {min_w}-{max_w} words.

# Output format
Return ONLY valid JSON:
{{"title": "short catchy episode title",
  "turns": [{{"speaker": "MAYA", "text": "..."}}, {{"speaker": "LEO", "text": "..."}}]}}"""

prompt = DIALOGUE_TEMPLATE.format(
    today=TODAY,
    beats=json.dumps(beats_for_dialogue, ensure_ascii=False, indent=2),
    facts=FACTS,
    min_w=MIN_WORDS, max_w=MAX_WORDS,
    **LEVEL,
)
messages = [{"role": "user", "content": prompt}]

data = None
draft_words = 0
for attempt in range(1, MAX_RETRY + 2):
    print()
    print(f"工程(3)b: 台詞化中(試行 {attempt} 回目)...")
    res = client.chat.completions.create(
        model=MODEL_WRITE,
        messages=messages,
        response_format={"type": "json_object"},
    )
    raw = res.choices[0].message.content
    data = json.loads(raw)
    data["turns"] = [{"speaker": norm_speaker(t["speaker"]), "text": t["text"]}
                     for t in data["turns"]]
    draft_words = count_words(data["turns"])
    # このprint()は、生成のたびに語数規格に収まっているかをその場で確認するためのもの。
    print(f"  語数: {draft_words}(規格 {MIN_WORDS}-{MAX_WORDS})")
    if MIN_WORDS <= draft_words <= MAX_WORDS:
        break
    if draft_words < MIN_WORDS:
        fix = (f"REJECTED: only {draft_words} words (minimum {MIN_WORDS}). Do NOT pad. "
               "Expand the deep-dive beats with the concrete material already in the beat sheet. "
               "Keep all rules. Return full JSON again.")
    else:
        fix = (f"REJECTED: {draft_words} words (maximum {MAX_WORDS}). Trim by tightening "
               "wordy turns - do NOT delete beats or keyword phrases. Keep all rules. "
               "Return full JSON again.")
    print("  → 規格外。差し戻します")
    messages.append({"role": "assistant", "content": raw})
    messages.append({"role": "user", "content": fix})
else:
    print("  ※ 上限回数でも規格外。現状版で続行します(要人間判断)")

# ============================================================
# ブロック10: 軽量推敲(語数凍結)
# ============================================================
REVISE_PROMPT = """You are a script doctor doing a LIGHT final polish on a podcast dialogue. The dialogue is already good. Your only jobs:
1. Add a few touches of natural speech (an occasional "hmm", "wait", a brief incomplete sentence) - at most 4-5 spots in the whole episode.
2. Make the final two turns quietly land: personal, lingering, no tidy summary. The final line stays LEO's closing question.
3. If any turn declares emotion with empty words ("fascinating", "amazing"), replace with a shown reaction.

FROZEN (do not change): structure, beat order, facts, roles, vocabulary level, the keyword phrases, and TOTAL WORD COUNT (stay within 3% of the original). When in doubt, change nothing.

Script:
{script}

Return ONLY valid JSON in the same format:
{{"title": "...", "turns": [{{"speaker": "...", "text": "..."}}]}}"""

print()
print("工程(3)c: 軽量推敲中...")
final = ask_llm(MODEL_WRITE, REVISE_PROMPT.format(
    script=json.dumps({"title": data["title"], "turns": data["turns"]},
                      ensure_ascii=False, indent=2)))
final["turns"] = [{"speaker": norm_speaker(t["speaker"]), "text": t["text"]}
                  for t in final["turns"]]
final_words = count_words(final["turns"])
print(f"  語数: 台詞化 {draft_words} → 推敲後 {final_words}")

if not (MIN_WORDS - 20 <= final_words <= MAX_WORDS + 20):
    print("  → 推敲で規格を外れたため、台詞化版を採用します(推敲を破棄)")
    final = {"title": data["title"], "turns": data["turns"]}
    final_words = draft_words

# ============================================================
# ブロック11: 論理検品(レポートのみ・自動修理なし)
# ============================================================
CHECK_PROMPT = """You are a dialogue-logic inspector. Read the script and examine every adjacent pair of turns. Report ONLY these problem types:
(a) dodged question: LEO's opening sentence does not directly answer the type of MAYA's question.
(b) leap: MAYA restates or concludes something LEO has not yet implied.
(c) topic jump: a turn does not grow out of the previous turn.
(d) metaphor as topic: a joke/image treated as a real impact area.
(e) duplicated beat: the same pushback, explanation, or example handled twice.
(f) written register: a turn that reads like written prose - abstract noun as subject, literary imagery, or a sentence nobody would say out loud.

Script:
{script}

Return ONLY valid JSON: {{"issues": [{{"turn_index": 0, "type": "a-f", "problem": "one line", "fix_hint": "one line"}}]}}. If clean, return {{"issues": []}}."""

print()
print("工程(3)d: 論理検品中(報告のみ・自動修理なし)...")
check = ask_llm(MODEL_WRITE, CHECK_PROMPT.format(
    script=json.dumps({"title": final["title"], "turns": final["turns"]},
                      ensure_ascii=False, indent=2)))
issues = check.get("issues", [])
if issues:
    # このprint()は、検品官が見つけた問題点を人間の最終判断のために一覧表示している。
    # 自動修理は行わず、あくまで報告のみ(過去に自動修理で事故が起きたための方針)。
    print(f"  検査官の指摘 {len(issues)} 件(参考情報。修理はしません):")
    for it in issues:
        print(f"   - turn {it.get('turn_index')} [{it.get('type')}] {it.get('problem')}")
else:
    print("  指摘なし(つなぎ目クリーン)")

# ============================================================
# ブロック12: ①概要(overview_intro) + ②キーワードコーナー(keywords_intro)の組み立て
# ============================================================
# overview_intro: 企画書のoverviewをそのまま採用(LLMが既にナレーター向けの
# 状況説明として書いているため、追加の前振り文は不要)。
final["overview_intro"] = brief.get("overview", "").strip()

# keywords_intro: LLMを使わず、keywords_planから機械的に「英語→日本語→英語」を
# 項目ごとに組み立てる(型崩れのリスクを避けるため)。項目間は空行で軽い間を表現する。
keywords_plan = brief.get("keywords_plan", [])
final["keywords_plan"] = keywords_plan
keyword_cycles = [f"{kw['phrase']}. {kw['japanese']}. {kw['phrase']}." for kw in keywords_plan]
final["keywords_intro"] = "\n\n".join(keyword_cycles)

print()
print("工程(3)e: 概要・キーワードコーナーを組み立て中...")
print("  概要      :", final["overview_intro"][:80], "...")
print("  キーワード数:", len(keywords_plan))

# ============================================================
# ブロック13: 保存と表示
# ============================================================
ep = next_number(EPISODE_PATTERN)
ep_path = f"episode_{LEVEL_KEY}_{ep:03d}.json"
final["level"] = LEVEL_KEY
final["brief"] = brief
final["beats"] = beats
final["draft_turns"] = data["turns"]
final["draft_words"] = draft_words
final["final_words"] = final_words
final["logic_issues"] = issues
final["judgements_sheet"] = sheet_path
with open(ep_path, "w", encoding="utf-8") as f:
    json.dump(final, f, ensure_ascii=False, indent=2)

# AUTOモードで採点シートを使わなかった場合(sheet_path=None)は、
# judgementsフォルダへの退避もスキップする。
if sheet_path:
    os.makedirs("judgements", exist_ok=True)
    shutil.move(sheet_path, f"judgements/{date.today().isoformat()}_{sheet_path}")

# 最終的な仕上がりを人間が確認できるよう、全文をターミナルに表示している。
print()
print("タイトル:", final["title"])
print(f"レベル: {LEVEL_KEY} / 語数: {final_words}(規格 {MIN_WORDS}-{MAX_WORDS}) / "
      f"ターン数: {len(final['turns'])} / 概算 {final_words/130:.1f} 分")
print("キーワード:", ", ".join(f"{k['phrase']}({k['japanese']})" for k in final["keywords_plan"]))
print("-" * 60)
print("【①概要】")
print(final["overview_intro"])
print("-" * 60)
print("【②キーワードコーナー】")
print(final["keywords_intro"])
print("-" * 60)
for t in final["turns"]:
    print(f'{t["speaker"]}: {t["text"]}')
    print()
print("-" * 60)
print(f"{ep_path} に保存しました(構成表・初稿・検品報告・概要・キーワードコーナーも同梱)")