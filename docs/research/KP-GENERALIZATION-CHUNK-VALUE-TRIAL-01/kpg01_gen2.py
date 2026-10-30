# -*- coding: utf-8 -*-
"""Trial専用: 構造化一般化(トークンラベル方式)。モデルは各トークンを CORE/SLOT/DROP に分類し、display_formはコードが決定論で組み立てる
(=核と可変部の区別を明示させ、本文に無い語の混入・選択肢併記・末尾プレースホルダをコード側で防ぐ)。"""
import re
import kpg01_llm as L
import kpg01_validate as V
from kpg01_methods import BODY

LABELS = ["CORE", "SLOT_THING", "SLOT_PERSON", "SLOT_POSS_SELF", "SLOT_POSS_OTHER", "DROP"]
G2_SCHEMA = {"name": "kp_gen_tokens", "schema": {"type": "object", "additionalProperties": False, "required": ["items"], "properties": {
    "items": {"type": "array", "items": {"type": "object", "additionalProperties": False,
        "required": ["id", "tokens", "gloss_ja", "sense_note_ja", "note_ja"],
        "properties": {"id": {"type": "integer"},
                       "tokens": {"type": "array", "items": {"type": "object", "additionalProperties": False, "required": ["n", "label", "lemma"],
                                                              "properties": {"n": {"type": "integer"}, "label": {"type": "string", "enum": LABELS}, "lemma": {"type": "string"}}}},
                       "gloss_ja": {"type": "string"}, "sense_note_ja": {"type": "string"}, "note_ja": {"type": "string"}}}}}}}

GEN2_RULES = """## 学習用の一般形づくり(トークン分類)
各候補の語句は番号付きトークンに分けてあります。**各トークンを次のどれかに分類**してください(語を書き換えたり足したりしません)。
- CORE: 学習する表現の核。動詞、固定の前置詞・粒子、表現の一部として固定された名詞・形容詞・冠詞。lemmaに辞書の見出し語形(動詞は原形、名詞は単数。活用・複数・時制を消した形。変えない語はそのまま)を書く。
- SLOT_THING: 自由に入れ替わる『物・事』の語(本文固有の目的語・主語)。連続するSLOTは1つのsomethingにまとめられる。lemmaは空文字。
- SLOT_PERSON: 自由に入れ替わる『人』を指す語(目的格の代名詞he/him/her/it(人)など)。someoneになる。lemmaは空文字。
- SLOT_POSS_SELF: 動作主自身を指す所有格(his/her/their/my...)。one'sになる。
- SLOT_POSS_OTHER: 動作主とは別の人の所有格。someone'sになる。
- DROP: 一般形から除く語(本文固有の修飾語・文脈語・省略しても成立する目的語・固定表現の後ろに続く名詞句や動名詞)。
判断の原則:
1. 核と可変部を区別する。**入替テスト**: その名詞を、意味の違う無関係な別の名詞(例: money、plans、people。同義語ではない)に替えても、同じ構文で自然に成り立ち、表現の意味(本文の語義)も変わらないなら、その名詞は自由に入れ替わる可変部=SLOT_THING(学習者用英英辞書ではsomethingと書かれる部分)。替えると意味が変わる/成り立たない(動詞とその名詞が慣用的に結びついている)ならCORE(例: set the record straight、pull strings、open the floodgates、動詞とセットで見出しになる連語の名詞)。**表現の骨格の見つけ方**: 表現の骨格は『動詞+粒子/前置詞』または『慣用句全体』である。動詞+粒子/前置詞が1つのまとまり(句動詞・前置詞付き動詞)で、その間や後ろに本文の具体的な対象(目的語名詞)が挟まっているだけなら、その名詞は可変部=SLOT_THING(例: "keep the costs down" -> keep=CORE, costs=SLOT_THING, down=CORE => keep something down、"get the plan off the ground" -> get something off the ground)。一方、名詞が動詞と結びついて初めて意味が出る連語・慣用句(break the ice、take place、pay attention to、draw a conclusion)では名詞をCOREにする。動詞と名詞の組合せが、その名詞に限らず他の名詞でも通じる一般的な動作(make、take、get、put、keepなどの軽い動詞+対象)なら、骨格は動詞+粒子/前置詞側と考える。
**名詞をCOREに残すのは、『他の無関係な名詞に替えるとその言い回しの意味が失われる』場合だけ**。『本文では比喩的に聞こえる』『本文の語義に必要に見える』『文脈上その名詞が重要』は残す理由にならない(本文の語義は日本語の意味gloss_jaとsense_note_jaで補う。一般形が本文の語義を包含する、より汎用的な項目になるのは意図どおりであり、許容される)。**迷ったらSLOT_THINGにする**。名詞をCOREに残したときは、note_jaに『なぜ他の名詞では成り立たないか』を書く。
2. 目的語を省いても成立する句動詞・前置詞付き動詞(例: tighten up the rules)は、目的語をDROPにして核だけを残す。目的語を表現の途中に挟まないと動詞の意味が成立しない場合(例: walk someone through、give something up)だけSLOTにする。
3. **前置詞・粒子で終わる形が見出しとなる表現(in the event of / by the end of / on the verge of)では、その後ろに続く本文固有の名詞句・動名詞は必ずDROP**(後続に名詞句を取る表現でも、学習用の表示では核を明確にする)。末尾にSLOTを置かない。
4. 必要な前置詞・粒子・補語(depend onのon、lead toのto)はCOREのまま残す。5. **意味を変える一般化は禁止**(本文での語義を保てない分類にしない)。複数の語義がある表現は本文での語義をsense_note_jaに書く。
6. 例(分類のしかたの例。別の表現): walked her through the steps -> walked=CORE(walk), her=SLOT_PERSON, through=CORE, the=DROP, steps=DROP => walk someone through / in the event of a delay -> in,the,event,of=CORE, a=DROP, delay=DROP => in the event of / tightened up the rules -> tightened=CORE(tighten), up=CORE, the=DROP, rules=DROP => tighten up。
gloss_ja: **一般形(DROP/SLOTにした語を除いた形)と同じ抽象度**で、本文での意味(語義)を日本語で簡潔に(20字程度)。DROPした語・SLOTにした語の意味をglossに含めない(例: in the event of a delay -> 『〜の場合には』、walk someone through -> 『(人)に〜を順に説明する』)。本文固有の具体的な名詞をglossに残さない。sense_note_ja: 本文での語義(30字以内)。note_ja: 何を核とし何を可変部としたか(40字以内)。"""


def tokenize(span):
    return [t for t in re.split(r"\s+", V.norm(span).strip()) if t]


def prompt_G2(text, sel):
    blocks = []
    for i, c in enumerate(sel, 1):
        tk = tokenize(c["span"])
        blocks.append(f"{i}. 語句: {c['span']}\n   トークン: " + " ".join(f"[{n}]{t}" for n, t in enumerate(tk, 1)) +
                      f"\n   本文の文: {c['sentence']}\n   塊の種類/理由: {c.get('chunk_type')} / {c.get('chunk_reason_ja')}")
    return ("次は、ひと塊で覚える価値があると判定済みの学習候補です(選定は変更しません)。各語句を、学習用の一般形に仕上げるため、トークンごとに分類してください。"
            "ユーザーは提示された形を修正せずにそのまま選びます。\n\n" + GEN2_RULES + "\n\n【候補】\n" + "\n".join(blocks) + BODY + text)


def assemble(span, tokens):
    """トークン分類 -> display_form(決定論)。returns (display_form, error|None)。"""
    sp = tokenize(span)
    if sorted(t["n"] for t in tokens) != list(range(1, len(sp) + 1)):
        return None, "トークン番号の欠落/重複"
    by = {t["n"]: t for t in tokens}
    out, prev_slot = [], None
    for n, surf in enumerate(sp, 1):
        t = by[n]
        lab = t["label"]
        if lab == "DROP":
            continue
        if lab == "CORE":
            lem = (t["lemma"] or surf).strip().lower() if surf.lower() != "i" else "I"
            lem = re.sub(r"[^\w'\- ]", "", lem)
            if not V.same_word(lem.split()[0] if lem else surf, surf) and lem != surf.lower().strip(".,;:!?\"()"):
                return None, f"lemma'{lem}'が本文の語'{surf}'の語形違いでない"
            out.append(lem)
            prev_slot = None
        else:
            ph = {"SLOT_THING": "something", "SLOT_PERSON": "someone", "SLOT_POSS_SELF": "one's", "SLOT_POSS_OTHER": "someone's"}[lab]
            if prev_slot == ph:
                continue
            out.append(ph)
            prev_slot = ph
    return V.strip_trailing_slot(" ".join(out)), None
