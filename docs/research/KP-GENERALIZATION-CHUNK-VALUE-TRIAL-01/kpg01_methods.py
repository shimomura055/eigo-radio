# -*- coding: utf-8 -*-
"""KP-GENERALIZATION-CHUNK-VALUE-TRIAL-01: Trial専用の方式A/B/C。Production module非依存(P7文言のみ参照のためコピーを保持)。
プロンプトに必須9検証例(take points away from等)は含めない(過学習防止)。例示は別の表現を使う。"""
import json, os, sys
import kpg01_llm as L
import kpg01_validate as V

BODY = "\n\n---\n\n【記事本文】\n"

# ---- Productionの難易度優先条件(P7条件4・5を逐語維持) ----
PROD_DIFFICULTY = ("4. **上級者向けの学習価値**：上級者でも学ぶ価値のある語彙・イディオム・慣用表現を優先する。\n"
                   "5. **易しい表現の除外**：基本語だけで構成され、字面どおりに意味が分かる表現や、上級者なら知っている易しい表現は除外する。\n")

CHUNK_DEFS = """## ひと塊として覚える価値の3区分(各候補を必ずこのどれかに分類する)
- W(単語型): 個々の単語が難しいだけ。フレーズ枠には入れない(単独の難語はword_candidatesへ)。
- F(自由な組合せ): 通常の単語を通常の文法で組み合わせただけ。各語の意味から全体の意味が導け、語を入れ替えても同じように成り立つ(例: describe a long process / buy a new car)。**フレーズ枠には入れない**。
- C(塊): 次のいずれかで、「なぜこの組合せをひと塊で覚える価値があるか」を1文で説明できるもの。
  * idiom(慣用表現): 語の意味の和では意味が決まらない、または比喩(例: set the record straight / pull strings)
  * phrasal_verb(句動詞・前置詞付き動詞): 動詞+粒子/前置詞で特有の意味や必須の組合せ(例: walk someone through / run out of)
  * collocation(強い連語): 特定の語同士が強く結びつき、言い換えると不自然、または学習者が組合せで覚えないと誤用しやすい(例: pay attention to / draw a conclusion)
  * fixed_phrase(固定表現・前置詞句・談話標識): 全体が決まった言い回し(例: in the long run / on behalf of)
  * compound_noun(定着した名詞句・複合名詞): 1つの概念として定着した名詞の組合せ(例: pain point / bottom line)
  複数語だというだけでは採用しない。語の意味から自明に分かる組合せは採用しない。
  字面どおりの意味と慣用的・比喩的な意味の両方を持つ表現は、本文で慣用的・比喩的に使われていればC(idiom)。字面だけで意味が取れる場合はF。"""

GEN_RULES = """## 一般化(display_form)の規則: 学習者が別の文脈でも使える、辞書の見出し語に近い自然な形にする
単に短くするのではなく、**表現の核**(動詞・固定の前置詞/粒子・固定された名詞)と、**自由に入れ替わる部分**(本文固有の目的語・主語・修飾語・人称)を区別する。
1. 自由に入れ替わる目的語・主語は something / someone / somewhere に置換する(例: "walked her through the steps" -> "walk someone through"、"pay off the debts" -> "pay something off")。所有格は one's / someone's、再帰代名詞は oneself。
   **見出し語テスト**: 学習者用英英辞書の見出し・句動詞の項目として載りそうな形を想定する。その形で目的語名詞が something/someone と書かれる(=別の名詞に入れ替えて同じ構文が自然に成り立つ)なら、その名詞は可変部としてsomethingに置換する(例: "cut costs down" -> "cut something down"、"keep patience in check" -> "keep something in check")。名詞自体が見出しに含まれる慣用的な核(例: set the record straight、pull strings、open the floodgates)の場合だけ名詞を残す。
2. 目的語を省いても成立する句動詞・前置詞付き動詞は、目的語を削った核の形にする(例: "tighten up the rules" -> "tighten up")。
3. 固定語の一部である名詞・冠詞・前置詞は保持する(例: "set the record straight" は全体が固定。"make up one's mind" の mind は固定)。固定でない後続名詞句(前置詞の目的語など)は残さない。
4. 必要な前置詞・粒子・補語は保持する(例: depend on の on、lead to の to)。
5. 動詞は原形、名詞は単数の見出し語形にする(複数形が普通の語は除く)。時制・人称は消す。
6. 核の語は本文の語の語形違いだけを使う。本文に無い語を足さない・別の語に言い換えない(置換してよいのはsomething/someone/one's/oneself/somewhereのみ)。
7. **意味を変える一般化は禁止**。本文での意味(語義)を保てない形にしない。複数の語義がある表現は、本文での語義をgloss_jaとsense_note_jaで明示し、その語義に合う形にする。
8. 5語以内。プレースホルダは、本文の語を置き換えた分だけ(本文に無い目的語を足さない)、多くても2個。
9. **末尾の自由な目的語は付けない**: 前置詞・粒子で終わる形(…for / …of / …to / …into)はそのまま提示し、末尾にsomethingを足さない(例: "in light of the report" -> "in light of")。プレースホルダを置くのは、目的語が表現の途中に挟まる場合(walk someone through、give something up)や、目的語なしでは動詞の意味が成立しない場合だけ。
10. **固定された言い回しの後ろに続く本文固有の名詞句・動名詞は必ず除く**(後続に名詞句を取る表現でも、学習用の表示では核を明確にする)。前置詞句の見出しは前置詞で終える。例: "in the event of a delay" -> "in the event of"、"by the end of the week" -> "by the end of"、"on the verge of collapse" -> "on the verge of"。
11. 英語は1つの形だけを書く("/"や括弧で選択肢を並べない)。冠詞(a/the)は本文のまま変えない。核の語を言い換えない。
12. gloss_jaは、display_formと同じ抽象度で、本文での意味を日本語で簡潔に(20字程度)書く。本文の具体的な名詞(固有の対象)をglossに残さない。"""

ITEM_PROPS = {
    "source_span": {"type": "string"}, "source_sentence": {"type": "string"},
    "display_form": {"type": "string"}, "gloss_ja": {"type": "string"},
    "chunk_type": {"type": "string", "enum": ["idiom", "phrasal_verb", "collocation", "fixed_phrase", "compound_noun"]},
    "chunk_reason_ja": {"type": "string"}, "difficulty": {"type": "string", "enum": ["advanced", "upper_intermediate"]},
    "sense_note_ja": {"type": "string"}, "generalization_note_ja": {"type": "string"},
}
ITEM_REQ = list(ITEM_PROPS)
A_SCHEMA = {"name": "kp_cards", "schema": {"type": "object", "additionalProperties": False, "required": ["items", "word_candidates"], "properties": {
    "items": {"type": "array", "items": {"type": "object", "additionalProperties": False, "required": ITEM_REQ, "properties": ITEM_PROPS}},
    "word_candidates": {"type": "array", "items": {"type": "string"}}}}}


def prompt_A(text):
    return ("以下の記事から、英語上級者が学ぶ価値のあるフレーズ・表現(2語以上の連続した語句)を、学習価値の高い順に**最大7つ**選び、"
            "学習用の形(display_form)まで仕上げてください。ユーザーは提示された候補を**修正せずにそのまま選ぶ**ので、"
            "一般化が不十分な形や、ひと塊で覚える価値の乏しい表現を出してはいけません。\n\n"
            "## 選定条件(上位から順に適用)\n"
            "1. **本文一致(絶対条件)**: source_spanは本文中の連続した語句をそのまま抜き出す(変更・言い換え・創作は禁止)。\n"
            "2. **5語以内(絶対条件)**: source_spanもdisplay_formも5語以内。\n"
            "3. **ひと塊の学習価値(必須)**: 下の区分でCに当たるものだけを選ぶ。\n"
            + PROD_DIFFICULTY +
            "6. 最大7件・学習価値の高い順。互いに同一または包含する類似表現を重ねない。意味・用法が重なる表現も重ねない。"
            "**適切な候補が不足する場合は7件未満でよい。数合わせはしない(品質を下げて埋めない)。**\n"
            "単独の難しい単語に学習価値がある場合はフレーズ枠に入れず、word_candidates(本文に現れる1語、最大3つ)に書く。\n\n"
            + CHUNK_DEFS + "\n\n" + GEN_RULES +
            "\n\n各候補にchunk_reason_ja(なぜ塊で覚える価値があるか、40字以内)、sense_note_ja(本文での語義、30字以内)、generalization_note_ja(何を核とし何を可変部としたか、40字以内)を書く。"
            "source_sentenceは本文中でその語句を含む文(そのまま)。" + BODY + text)


# ---- B: 工程分離 ----
B1_SCHEMA = {"name": "kp_extract", "schema": {"type": "object", "additionalProperties": False, "required": ["candidates"], "properties": {
    "candidates": {"type": "array", "items": {"type": "object", "additionalProperties": False, "required": ["span", "sentence"],
                                               "properties": {"span": {"type": "string"}, "sentence": {"type": "string"}}}}}}}


def prompt_B1(text, n=14):
    return (f"以下の記事から、英語上級者が学ぶ価値のあるフレーズ・表現・イディオム・句動詞・連語・定着した名詞句(2語以上の連続した語句)の**候補を最大{n}個**、"
            "広めに挙げてください(後段で絞り込みます。ランキングは不要)。\n\n"
            "1. **本文一致(絶対条件)**: 本文中の連続した語句をそのまま抜き出す。変更・言い換え・創作は禁止。\n"
            "2. **5語以内(絶対条件)**: 6語以上は出力禁止。\n"
            "3. 意味と自然さを保てる最短の形で抜き出す。\n"
            + PROD_DIFFICULTY +
            "同じ語句や、一方が他方を含む類似語句は重ねない。sentenceは本文中でその語句を含む文をそのまま書く。" + BODY + text)


B2_SCHEMA = {"name": "kp_rank", "schema": {"type": "object", "additionalProperties": False, "required": ["judgements"], "properties": {
    "judgements": {"type": "array", "items": {"type": "object", "additionalProperties": False,
        "required": ["id", "cls", "chunk_type", "chunk_reason_ja", "difficulty", "keep"],
        "properties": {"id": {"type": "integer"}, "cls": {"type": "string", "enum": ["W", "F", "C"]},
                       "chunk_type": {"type": "string", "enum": ["idiom", "phrasal_verb", "collocation", "fixed_phrase", "compound_noun", "none"]},
                       "chunk_reason_ja": {"type": "string"}, "difficulty": {"type": "string", "enum": ["advanced", "upper_intermediate", "easy"]},
                       "keep": {"type": "boolean"}}}}}}}


def prompt_B2(text, cands, wn_hints=True):
    lines = []
    for i, c in enumerate(cands, 1):
        h = ""
        if wn_hints:
            w = V.wn_multiword(c["span"])
            h = f" [WordNet複合語見出し: {'あり' if w else 'なし' if w is False else '-'}(参考。なしでも塊でないとは限らない)]"
        lines.append(f"{i}. {c['span']}{h}\n   文: {c['sentence']}")
    return ("次は英語記事から抽出された学習候補フレーズです。各候補を評価し、ユーザーが修正せずに選べる候補だけをkeep=trueにしてください。\n\n"
            + CHUNK_DEFS + "\n\n"
            "## 判定手順\n"
            "各候補について(1)W/F/Cの区分、(2)Cなら塊の種類と『なぜこの組合せをひと塊で覚える価値があるか』の1文説明(40字以内)、"
            "(3)難易度(advanced=上級者でも学ぶ価値/upper_intermediate=中上級/easy=易しい)を判定する。\n"
            "keep=trueにできるのは、区分がCで、難易度がeasyでなく、本文語義でのまとまりとして成立し、他の候補と意味・用法が重ならないものだけ。"
            "**候補が不足してもkeepを甘くしない(品質を下げて埋めない)。**\n"
            "難易度の優先: advancedを先に、次にupper_intermediate。\n\n【候補】\n" + "\n".join(lines) + BODY + text)


B3_SCHEMA = {"name": "kp_generalize", "schema": {"type": "object", "additionalProperties": False, "required": ["items"], "properties": {
    "items": {"type": "array", "items": {"type": "object", "additionalProperties": False,
        "required": ["id", "display_form", "gloss_ja", "sense_note_ja", "generalization_note_ja"],
        "properties": {"id": {"type": "integer"}, "display_form": {"type": "string"}, "gloss_ja": {"type": "string"},
                       "sense_note_ja": {"type": "string"}, "generalization_note_ja": {"type": "string"}}}}}}}


def prompt_B3(text, sel):
    lines = [f"{i}. source_span: {c['span']}\n   本文の文: {c['sentence']}\n   塊の種類/理由: {c.get('chunk_type')} / {c.get('chunk_reason_ja')}" for i, c in enumerate(sel, 1)]
    return ("次は、ひと塊で覚える価値があると判定済みの学習候補です(選定は変更しません)。各候補を、学習用の一般形(display_form)と日本語の意味(gloss_ja)に仕上げてください。"
            "ユーザーは提示された形を修正せずにそのまま選びます。\n\n" + GEN_RULES +
            "\n\nsense_note_jaは本文での語義(30字以内)、generalization_note_jaは何を核とし何を可変部としたか(40字以内)。\n\n【候補】\n" + "\n".join(lines) + BODY + text)


B4_SCHEMA = {"name": "kp_verify", "schema": {"type": "object", "additionalProperties": False, "required": ["verdicts"], "properties": {
    "verdicts": {"type": "array", "items": {"type": "object", "additionalProperties": False,
        "required": ["id", "verdict", "meaning_preserved", "gloss_consistent", "natural_headword", "issue", "fix_display_form", "fix_gloss_ja"],
        "properties": {"id": {"type": "integer"}, "verdict": {"type": "string", "enum": ["OK", "FIX", "REJECT"]},
                       "meaning_preserved": {"type": "boolean"}, "gloss_consistent": {"type": "boolean"}, "natural_headword": {"type": "boolean"},
                       "issue": {"type": "string"}, "fix_display_form": {"type": "string"}, "fix_gloss_ja": {"type": "string"}}}}}}}


def prompt_B4(text, items):
    lines = [f"{i}. 本文の語句: {c['span']}\n   本文の文: {c['sentence']}\n   学習用の形: {c['display_form']}\n   日本語の意味: {c['gloss_ja']}\n   塊の理由: {c.get('chunk_reason_ja')}" for i, c in enumerate(items, 1)]
    return ("あなたは英語教材の校閲者です。本文の語句を学習用の一般形に直した結果を検査してください。\n"
            "この検査は『この語句を選ぶべきか』の判断ではありません(選定は完了済み)。形と意味の検査だけを行ってください。各項目について: (a)学習用の形は本文の語句と同じ意味・語義を保っているか(別の意味になっていないか)、(b)日本語の意味は学習用の形と本文の語義の両方に合っているか、"
            "(c)学習用の形は辞書の見出し語として自然で、別の文脈でも使える英語か(不要な目的語・文脈語が残っていないか、逆に必要な前置詞・固定語が欠けていないか)、"
            "(d)自由に入れ替わる目的語名詞(意味の違う別の名詞に替えても同じ構文・同じ意味で成り立つもの)が、somethingやsomeoneにならずに残っていないか、"
            "(e)前置詞で終わる固定表現の後ろに、本文固有の名詞句・動名詞が残っていないか(学習用の表示では核を明確にするため除く)、を判定する。(d)(e)に該当する場合はFIXとし、fix_display_formに直した形を書く。\n"
            "verdict: OK=そのままユーザーに提示できる / FIX=小さな修正で提示できる(fix_display_form/fix_gloss_jaに修正案。核の語は本文の語の語形違いのみ、something/someone/one'sのみ置換可) / REJECT=一般化で意味・語義が変わる、または英語として不自然で修正案も作れず提示不可。選定の是非(塊としての価値)を理由にREJECTしない。"
            "**重要**: 学習用の形が本文固有の語(DROP/something化した語)を除いて一般化されているのは意図どおりであり、元の本文の語を戻す方向のfix_display_formは書かない(例: at the time of writing -> at the time of は正しい一般化)。日本語の意味が一般形より具体的すぎる(除いた語の意味を含む)場合は、fix_gloss_jaで日本語の側を一般形に合わせて直す。日本語の意味は名詞句・副詞句・動詞句のいずれの形でもよく、品詞の形だけを理由にFIXしない。fix_gloss_jaを書くときも、日本語の意味は**本文での語義(sense)を保つ**こと。辞書にある別の語義や、より一般的な語義に置き換えない(例: 『順序を逆にする』の意味を『好転させる』に変えない)。OKのとき、fix欄は空文字。\n\n【検査対象】\n" + "\n".join(lines) + BODY + text)


def run_B(case, *, m_extract="gpt-6-luna", m_rank="gpt-6-luna", m_gen="gpt-6-luna", m_verify="gemini-3.8-flash",
          eff_rank=None, eff_gen=None, cands_override=None, wn_hints=True, tag="B", cap=7, verify_think=1024, do_verify=True):
    """B(工程分離): 1抽出 -> 2難易度+塊価値判定 -> 3一般化 -> 4検証(別系列) -> 決定論検査。cands_override=C1(Production P7候補をそのまま入力)。"""
    text = case["text"]
    log = {"stages": [], "tag": tag}

    def rec(name, meta):
        log["stages"].append({"stage": name, **{k: meta[k] for k in ("model_id", "in", "out", "cost_jpy", "sec")}})
    if cands_override is None:
        o, m = L.call(m_extract, prompt_B1(text), B1_SCHEMA, tag=f"{case['id']}:{tag}:B1")
        rec("B1_extract", m)
        cands = [c for c in o["candidates"] if V.span_in_text(c["span"], text)]
        log["dropped_not_in_text"] = [c["span"] for c in o["candidates"] if not V.span_in_text(c["span"], text)]
    else:
        cands = cands_override
    log["extracted"] = [c["span"] for c in cands]
    o, m = L.call(m_rank, prompt_B2(text, cands, wn_hints), B2_SCHEMA, effort=eff_rank, tag=f"{case['id']}:{tag}:B2")
    rec("B2_rank", m)
    sel = []
    for j in o["judgements"]:
        if 1 <= j["id"] <= len(cands):
            c = dict(cands[j["id"] - 1])
            c.update(cls=j["cls"], chunk_type=j["chunk_type"], chunk_reason_ja=j["chunk_reason_ja"], difficulty=j["difficulty"], keep=j["keep"])
            sel.append(c)
    log["judged"] = [{k: c[k] for k in ("span", "cls", "chunk_type", "difficulty", "keep", "chunk_reason_ja")} for c in sel]
    rankmap = {"advanced": 0, "upper_intermediate": 1, "easy": 2}
    kept = [c for c in sel if c["keep"] and c["cls"] == "C" and c["difficulty"] != "easy"]
    kept.sort(key=lambda c: rankmap[c["difficulty"]])   # 安定sort: 同難易度はmodel順
    kept = kept[:cap]
    if not kept:
        return {"items": [], "log": log}
    o, m = L.call(m_gen, prompt_B3(text, kept), B3_SCHEMA, effort=eff_gen, tag=f"{case['id']}:{tag}:B3")
    rec("B3_generalize", m)
    g = {x["id"]: x for x in o["items"]}
    items = []
    for i, c in enumerate(kept, 1):
        x = g.get(i)
        if not x:
            continue
        items.append(dict(c, display_form=x["display_form"], gloss_ja=x["gloss_ja"], sense_note_ja=x["sense_note_ja"], generalization_note_ja=x["generalization_note_ja"]))
    vd = {}
    if do_verify:
        o, m = L.call(m_verify, prompt_B4(text, items), B4_SCHEMA, tag=f"{case['id']}:{tag}:B4", think_budget=verify_think)
        rec("B4_verify", m)
        vd = {x["id"]: x for x in o["verdicts"]}
    final = []
    for i, c in enumerate(items, 1):
        v = vd.get(i, {})
        c["verify"] = v
        if v.get("verdict") == "REJECT":
            log.setdefault("verify_dropped", []).append({"span": c["span"], "issue": v.get("issue")})
            continue
        if v.get("verdict") == "FIX":
            if v.get("fix_display_form"):
                c["display_form_pre_fix"] = c["display_form"]
                c["display_form"] = v["fix_display_form"]
            if v.get("fix_gloss_ja"):
                c["gloss_ja"] = v["fix_gloss_ja"]
        c["display_form"] = V.strip_trailing_slot(c["display_form"])
        ok, why = V.display_check(c["display_form"], c["span"])
        if not ok:
            log.setdefault("validator_dropped", []).append({"span": c["span"], "display_form": c["display_form"], "why": why})
            continue
        final.append(c)
    return {"items": [dict(source_span=c["span"], source_sentence=c["sentence"], display_form=c["display_form"], gloss_ja=c["gloss_ja"],
                           chunk_type=c["chunk_type"], chunk_reason_ja=c["chunk_reason_ja"], difficulty=c["difficulty"],
                           sense_note_ja=c["sense_note_ja"], generalization_note_ja=c["generalization_note_ja"], verify=c.get("verify"),
                           display_form_pre_fix=c.get("display_form_pre_fix")) for c in final],
            "log": log}


def run_A(case, *, model="gpt-6-luna", effort=None, tag="A"):
    log = {"stages": [], "tag": tag}
    o, m = L.call(model, prompt_A(case["text"]), A_SCHEMA, effort=effort, tag=f"{case['id']}:{tag}")
    log["stages"].append({"stage": "A_integrated", **{k: m[k] for k in ("model_id", "in", "out", "cost_jpy", "sec")}})
    items, dropped = [], []
    for c in o["items"]:
        c["display_form"] = V.strip_trailing_slot(c["display_form"])
        ok1 = V.span_in_text(c["source_span"], case["text"])
        ok2, why = V.display_check(c["display_form"], c["source_span"])
        if ok1 and ok2:
            items.append(c)
        else:
            dropped.append({"span": c["source_span"], "display_form": c["display_form"], "why": (["本文不一致"] if not ok1 else []) + why})
    log["validator_dropped"] = dropped
    log["word_candidates"] = o.get("word_candidates")
    return {"items": items[:7], "log": log}


def prod_p7_cands(case):
    """C1用: Production P7の出力(selection_phrase=本文表層形)をB2への入力にする。"""
    b = case["before"]
    out = []
    for c in b["candidates"]:
        if c["kind"] == "phrase" and c["origin"] in ("call1", "backfill"):
            out.append({"span": c["selection_phrase"], "sentence": c.get("sentence") or ""})
    return out
