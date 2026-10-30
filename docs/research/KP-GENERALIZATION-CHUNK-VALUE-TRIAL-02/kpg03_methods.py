# -*- coding: utf-8 -*-
"""KP-GENERALIZATION-CHUNK-VALUE-TRIAL-02 Trial専用: 方式E1〜E4(Production非接触)。
比較基準=方式D(TRIAL-01)。D'(ガード追加の反復)は行わない。
 E1L/E1S: Dと同じ順序(過剰生成→塊判定→一般化→別系列検証)。塊判定Promptを強化(定義+判定テスト+専門名詞句+G1型)。E1S=塊判定にgpt-6.1-sol。
 E2    : 順序変更(過剰生成→一般化(全候補)→塊判定(一般化後の見出し形を判定)→別系列検証)。luna。
 E3    : E2 + 別系列(gemini)検証にFREE_COMBINATION/WORD_ONLYの選定ゲートを併合(同一call)。
 E4    : E2の塊判定をsolに + 別系列ゲート。
易しい表現(rely on等)は除外しない(difficultyは並び順にのみ使用)。"""
import os, sys, re, json, concurrent.futures as cf
HERE = os.path.dirname(os.path.abspath(__file__))
OLD = os.path.join(HERE, "..", "KP-GENERALIZATION-CHUNK-VALUE-TRIAL-01")
sys.path.insert(0, HERE); sys.path.insert(0, OLD)
import kpg03_llm as L
import kpg02_methods as M2          # WordNet lock・複数形lemma補正のmonkeypatch継承、FRAG、guard_tokens
import kpg01_validate as V
import kpg01_gen2 as G
from kpg01_methods import prompt_B1, B1_SCHEMA, prompt_B4, B4_SCHEMA, prod_p7_cands, BODY
from kpg01_methods2 import _contains

SOL, LUNA, GEM = "gpt-6.1-sol", "gpt-6-luna", "gemini-3.8-flash"

# ============ 塊判定: 3区分の定義強化 + 判定テスト + 専門名詞句 + G1型 ============
CHUNK_DEFS_V3 = """## ひと塊として覚える価値の3区分(各候補を必ず1つに分類する)
- W(単語型): 個々の単語が難しいだけ。フレーズ枠には入れない。
- F(自由な組合せ): 通常の単語を通常の文法で組み合わせただけで、語を同類の語に入れ替えても同じように成り立つもの。**フレーズ枠には入れない**。次はすべてF:
  * 形容詞/副詞/名詞+名詞の**描写的な組合せ**(各語の意味から全体が導ける)。専門分野の記述的な名詞句もF(例: a faint signal / thermal noise level / seed funding round の類)。
    ただし学習者用英英辞書に一般語として見出しがあり、他の文脈でも使える定着した複合名詞はC(例: pain point / glass ceiling / bottom line)。
  * 動詞+目的語で、動詞が字面どおりの意味(例: open a window / write a report)。
  * 比喩的でも、辞書に定着していない一回限りの言い回し・本文の文脈でだけ成立する比喩(例: need a map for the road ahead)。
  * 修飾語+名詞で、修飾語を同類の語(early/late、deep/shallow等)に替えても同じ型で成り立つもの。
- C(塊): 次のいずれかで、「なぜこの組合せをひと塊で覚える価値があるか」を40字以内で言えるもの。
  * idiom(慣用表現): 語の意味の和では決まらない、または辞書に定着した比喩(例: set the record straight / pull strings)
  * phrasal_verb(句動詞・前置詞付き動詞): 動詞+粒子/前置詞の組合せ自体が見出しで特有の意味や必須の組合せ(例: walk someone through / run out of / bring something down)
  * collocation(強い連語): 特定の語同士が強く結びつき、言い換えると不自然、または組合せで覚えないと誤用しやすい(例: pay attention to / draw a conclusion)
  * fixed_phrase(固定表現・前置詞句・談話標識): 全体が決まった言い回し(例: in the long run / on behalf of)
  * compound_noun(定着した複合名詞): 1つの概念として辞書に定着(例: pain point)
## 判定テスト(順に適用。1つでも当てはまればF)
T1 辞書テスト: 学習者用英英辞書の見出し・派生項目・句動詞項目・連語欄に載りそうか。載らなければF。
T2 置換テスト: 構成語の1つを同類の別の語に替えても、同じ型で自然に成り立ち意味も同様に導けるならF(塊ではなく型)。
T3 予測テスト: すべての語を知っている学習者が、意味も、この語の組合せ(この動詞にこの前置詞/粒子)も自力で推測・再現できるならF。
T4 理由テスト: 「なぜひと塊で覚える価値があるか」を具体的に言えなければF。
難易度(difficulty)は区分と独立に記録する(advanced/upper_intermediate/easy)。**塊(C)であれば、基本語だけの句動詞・前置詞付き動詞でもCのまま**とし、易しいことを理由にFへ下げない/keepを下げない(難易度は並び順にだけ使う)。
## 一般化後に独立した学習価値がある場合(G1型)
本文の語句が個別の名詞を含み自由な組合せに見えても、**可変部の名詞をsomething/someoneに置き換えた見出し形**(動詞+前置詞/粒子の組合せ自体が辞書の見出し)が成立するなら、その見出し形で判定してC(例: set the numbers aside -> set something aside / bring the costs down -> bring something down)。
逆に、一般化(修飾語の除去など)の結果、字面どおりの易しい組合せになって独立した学習価値が消える場合はF。"""

EXTRA_RULES_V3 = """## 追加の判定規則
(a) 受動態・完了形・不定詞の断片: 受動形や過去分詞が核で辞書の能動の塊になっていないものはpassive_fragment=true、keep=false(be taken aback等、受動形そのものが見出しなら塊として扱ってよい)。
(b) 節の断片(whose…/which…/that…で始まる等)は塊ではない。
(c) 候補が不足してもkeepを甘くしない(品質を下げて埋めない)。keep=trueにできるのは、区分がCで、本文語義でのまとまりとして成立し、他の候補と意味・用法が重ならないものだけ。同じ意味・用法の候補が複数ある場合は最も代表的な1つだけkeepにする。"""

SEL3_SCHEMA = {"name": "kp_rank3", "schema": {"type": "object", "additionalProperties": False, "required": ["judgements"], "properties": {
    "judgements": {"type": "array", "items": {"type": "object", "additionalProperties": False,
        "required": ["id", "cls", "chunk_type", "reason_ja", "difficulty", "keep", "passive_fragment"],
        "properties": {"id": {"type": "integer"}, "cls": {"type": "string", "enum": ["W", "F", "C"]},
                       "chunk_type": {"type": "string", "enum": ["idiom", "phrasal_verb", "collocation", "fixed_phrase", "compound_noun", "none"]},
                       "reason_ja": {"type": "string"}, "difficulty": {"type": "string", "enum": ["advanced", "upper_intermediate", "easy"]},
                       "keep": {"type": "boolean"}, "passive_fragment": {"type": "boolean"}}}}}}}


def prompt_S3(text, cands, mode):
    """mode='span': 本文の語句を判定(E1。G1型は『可変部をsomething化した見出し形』で判定)/ mode='form': 一般化後の見出し形を判定(E2〜E4)"""
    lines = []
    for k, c in enumerate(cands, 1):
        if mode == "form":
            lines.append(f"{k}. 学習者に提示する形: {c['display_form']}\n   意味: {c.get('gloss_ja')}\n   本文の根拠(変更しない): {c['span']}\n   文: {c['sentence']}")
        else:
            w = V.wn_multiword(c["span"])
            h = f" [WordNet複合語見出し: {'あり' if w else 'なし' if w is False else '-'}(参考のみ)]"
            lines.append(f"{k}. {c['span']}{h}\n   文: {c['sentence']}")
    head = ("次は英語記事から抽出された学習候補です。各候補を評価し、ユーザーが修正せずに選べる候補だけをkeep=trueにしてください。\n"
            + ("**判定の対象は『学習者に提示する形』(一般化済み)です。** 本文の根拠は文脈確認のための参考で、提示形が辞書の見出しとして独立の学習価値を持つかで区分を決める。\n" if mode == "form"
               else "判定の対象は本文の語句ですが、個別の名詞を含む場合は可変部をsomething/someoneにした見出し形で成立するかを考慮する(G1型)。\n")
            + "\n")
    return (head + CHUNK_DEFS_V3 + "\n\n" + EXTRA_RULES_V3 + "\n\n"
            "各候補についてid・cls・chunk_type・reason_ja(40字以内)・difficulty・keep・passive_fragmentのみ返す。\n\n【候補】\n" + "\n".join(lines) + BODY + text)


# ============ 一般化 v4: トークン分類の規則見直し ============
GEN4_EXTRA = """
## 追加規則(v4)
A. 人称: 目的語の位置の語が本文で『人』を指すならSLOT_PERSON(someone)、『物・事』ならSLOT_THING(something)。代名詞itでも文脈で人を指すなら人。
B. **修飾語(形容詞・副詞・比較級・否定語)の保持と除去は『除去テスト』で決める**:
   (1) 修飾語を除いた形が、同じ辞書見出し・同じ語義の表現として成り立つ -> 本文固有の具体化なのでDROP。
   (2) 除くと別の表現・別の語義になる、表現の意味が失われる、または修飾語自体が見出しの一部(否定語notなど) -> CORE。
   (3) SLOTにする名詞に付く修飾語は常にDROP。
   (4) 迷うときはDROPせずCOREのまま残す(誤った見出し形を作るより、残して選定段で自由な組合せとして落とす方が安全)。
C. 受動態・過去分詞を核に残さない。能動の一般形にできなければ無理に一般化せず元の形のままCOREにする。動詞は固定句の中でも原形(例: or so it seemed -> or so it seems)にする。
D. **表示形(display_form)と本文の根拠(source_span)は別管理**です。source_spanは変更しない。display_formは学習者用の見出し形。
   一般化後に動詞+前置詞/粒子の組合せ自体が辞書見出しになる(別の名詞に替えても同じ構文・同じ語義で成り立つ)なら、本文の個別名詞は積極的にSLOT_THINGにする(例: put the blame on -> put something on の型が成り立つか確認する)。
"""


def prompt_G4(text, cands, with_chunk):
    blocks = []
    for i, c in enumerate(cands, 1):
        tk = G.tokenize(c["span"])
        b = f"{i}. 語句: {c['span']}\n   トークン: " + " ".join(f"[{n}]{t}" for n, t in enumerate(tk, 1)) + f"\n   本文の文: {c['sentence']}"
        if with_chunk:
            b += f"\n   塊の種類/理由: {c.get('chunk_type')} / {c.get('chunk_reason_ja')}"
        blocks.append(b)
    rules = G.GEN2_RULES.replace("gloss_ja: **一般形", GEN4_EXTRA + "\ngloss_ja: **一般形", 1)
    head = ("次は学習候補です。各語句を、学習用の一般形に仕上げるため、トークンごとに分類してください。"
            + ("選定は完了済みで変更しません。" if with_chunk else "選定はこの後に別の工程で行うので、塊かどうかは気にせず、一般形づくりの規則だけに従ってください。")
            + "ユーザーは提示された形を修正せずにそのまま選びます。\n\n")
    schema = {"name": "kp_gen_tokens4", "schema": G.G2_SCHEMA["schema"]}
    return head + rules + "\n\n【候補】\n" + "\n".join(blocks) + BODY + text, schema


# ============ 別系列検証(+選定ゲート) ============
GATE_CODES = ["OK", "FREE_COMBINATION", "WORD_ONLY", "NOT_GENERALIZED", "OVER_GENERALIZED", "MEANING_CHANGED", "UNNATURAL", "OTHER"]
_p = json.loads(json.dumps(B4_SCHEMA))
_it = _p["schema"]["properties"]["verdicts"]["items"]
_it["properties"].update(gate_cls={"type": "string", "enum": ["W", "F", "C"]}, gate_code={"type": "string", "enum": GATE_CODES})
_it["required"] = _it["required"] + ["gate_cls", "gate_code"]
B5_SCHEMA = {"name": "kp_verify_gate", "schema": _p["schema"]}

GATE_ADD = ("\n\n## 追加: 選定ゲート(別系列の独立確認)\n上の検査に加えて、各項目の『学習用の形』を次の3区分で分類し、gate_clsに書く(W=単語難のみ / F=自由な組合せ・描写的な名詞句・一回限りの比喩 / C=辞書に定着した塊)。"
            "gate_codeは、Fなら FREE_COMBINATION、Wなら WORD_ONLY、それ以外の問題は NOT_GENERALIZED / OVER_GENERALIZED / MEANING_CHANGED / UNNATURAL / OTHER の最も主要な1つ、問題なしはOK。"
            "**易しい表現であることはゲート不可の理由にしない**(基本語の句動詞・前置詞付き動詞でも、辞書の見出しとして成立するならC)。"
            "一般化後の見出し形(動詞+前置詞/粒子の組合せ自体が見出し)として独立の学習価値があるならCとしてよい。")


def prompt_B5(text, items):
    return prompt_B4(text, items) + GATE_ADD


def _meta(m):
    return {k: m[k] for k in ("model_id", "in", "out", "cost_jpy", "sec")}


# ============ 共通部品 ============
def collect(case, log, tag):
    """候補源=現行P7(保存済みdoc/再現) + 過剰生成(luna。TRIAL-01と同一promptなのでcache hitすれば費用0)。"""
    text = case["text"]
    base = [dict(c, sentence=c.get("sentence") or "") for c in prod_p7_cands(case)] if case.get("before") else []
    cands = list(base)
    o, m = L.call(LUNA, prompt_B1(text), B1_SCHEMA, tag=f"{case['id']}:{tag}:B1", max_out=6000)
    log["stages"].append({"stage": "B1_overgen", **_meta(m)})
    for c in o["candidates"]:
        if V.span_in_text(c["span"], text) and not any(_contains(c["span"], b["span"]) for b in cands):
            cands.append(c)
    for c in cands:
        if not c.get("sentence"):
            for sent in text.replace("\n", " ").split(". "):
                if V.span_in_text(c["span"], sent):
                    c["sentence"] = sent.strip()
                    break
    cands = [c for c in cands if not M2.FRAG.search(c["span"])]
    log["cands"] = [c["span"] for c in cands]
    log["cands_from_p7"] = [c["span"] for c in base]
    return cands


def generalize(case, cands, log, *, m_gen, eff_gen, tag, with_chunk, guard=False, label="GEN"):
    """トークン分類(v4規則)->display_form決定論組立。cands全件を返す(欠落/組立失敗はlogのみ)。"""
    if not cands:
        return []
    p, sch = prompt_G4(case["text"], cands, with_chunk)
    o, m = L.call(m_gen, p, sch, effort=eff_gen, tag=f"{case['id']}:{tag}:{label}", max_out=7000)
    log["stages"].append({"stage": label, **_meta(m)})
    gm = {x["id"]: x for x in o["items"]}
    items = []
    for i, c in enumerate(cands, 1):
        x = gm.get(i)
        if not x:
            log.setdefault("gen_missing", []).append(c["span"])
            continue
        toks, restored = (M2.guard_tokens(c["span"], x["tokens"]) if guard else (x["tokens"], []))
        df, err = G.assemble(c["span"], toks)
        if df is None:
            log.setdefault("assemble_failed", []).append({"span": c["span"], "err": err})
            continue
        ok, why = V.display_check(df, c["span"])
        if not ok:
            log.setdefault("gen_validator_dropped", []).append({"span": c["span"], "display_form": df, "why": why})
            continue
        items.append(dict(c, display_form=df, gloss_ja=x["gloss_ja"], sense_note_ja=x["sense_note_ja"], generalization_note_ja=x["note_ja"],
                          tokens=[(t["n"], t["label"], t["lemma"]) for t in toks], guard_restored=restored))
    return items


def select(case, cands, log, *, m_sel, eff_sel, tag, mode, label="SEL"):
    """塊判定1 pass。returns 判定付き候補のlist(全件。keep判定は呼出側ではなくここでcandに付与)。"""
    if not cands:
        return []
    mo = 7000 if m_sel == LUNA else 5000
    o, m = L.call(m_sel, prompt_S3(case["text"], cands, mode), SEL3_SCHEMA, effort=eff_sel, tag=f"{case['id']}:{tag}:{label}", max_out=mo)
    log["stages"].append({"stage": label, **_meta(m)})
    jm = {j["id"]: j for j in o["judgements"] if 1 <= j["id"] <= len(cands)}
    out = []
    for i, c in enumerate(cands, 1):
        j = jm.get(i)
        cc = dict(c)
        if j:
            cc.update(cls=j["cls"], chunk_type=j["chunk_type"], chunk_reason_ja=j["reason_ja"], difficulty=j["difficulty"],
                      keep=bool(j["keep"] and j["cls"] == "C" and not j["passive_fragment"]), passive_fragment=j["passive_fragment"], judged=True)
        else:
            cc.update(cls="?", chunk_type="none", chunk_reason_ja="", difficulty="upper_intermediate", keep=False, passive_fragment=False, judged=False)
        out.append(cc)
    log.setdefault("judged", []).extend([{"span": c["span"], "display_form": c.get("display_form"), "cls": c["cls"], "difficulty": c["difficulty"],
                                           "keep": c["keep"], "reason": c["chunk_reason_ja"]} for c in out])
    return out


RANK = {"advanced": 0, "upper_intermediate": 1, "easy": 2}


def pick(judged, cap):
    """keep済みを難易度順(advanced先)・同順位は元の順で並べ、重複(span包含/同一display_form)を除いてcapまで。易しいものは除外せず後ろに並べるだけ。"""
    ks = [c for c in judged if c["keep"]]
    ks.sort(key=lambda c: RANK.get(c["difficulty"], 1))
    out = []
    for c in ks:
        dfl = (c.get("display_form") or "").lower()
        if any(_contains(c["span"], o["span"]) or _contains(o["span"], c["span"]) for o in out):
            continue
        if dfl and any((o.get("display_form") or "").lower() == dfl for o in out):
            continue
        out.append(c)
    return out[:cap]


def verify(case, items, log, *, tag, gate):
    """別系列(gemini 非thinking・出力上限明示)の検証/修正。gate=True: 選定ゲート併合(FREE_COMBINATION/WORD_ONLYなら除外)。"""
    if not items:
        return []
    pr, sch = (prompt_B5(case["text"], items), B5_SCHEMA) if gate else (prompt_B4(case["text"], items), B4_SCHEMA)
    o, m = L.call(GEM, pr, sch, tag=f"{case['id']}:{tag}:{'GATE' if gate else 'VER'}", think_budget=0, max_out=4500)
    log["stages"].append({"stage": "GATE" if gate else "VER", **_meta(m)})
    vd = {x["id"]: x for x in o["verdicts"]}
    final = []
    for i, c in enumerate(items, 1):
        v = vd.get(i, {})
        c["verify"] = v
        if gate and v.get("gate_code") in ("FREE_COMBINATION", "WORD_ONLY") and v.get("gate_cls") in ("F", "W"):
            log.setdefault("gate_dropped", []).append({"span": c["span"], "display_form": c["display_form"], "gate_cls": v.get("gate_cls"), "gate_code": v.get("gate_code")})
            continue
        if v.get("verdict") == "REJECT":
            log.setdefault("verify_dropped", []).append({"span": c["span"], "issue": v.get("issue")})
            continue
        if v.get("verdict") == "FIX":
            fx = V.strip_trailing_slot((v.get("fix_display_form") or "").replace(" / ", " ").strip())
            if fx:
                okf, whyf = V.display_check(fx, c["span"])
                if okf:
                    c["display_form_pre_fix"] = c["display_form"]; c["display_form"] = fx
                else:
                    log.setdefault("fix_rejected_by_validator", []).append({"span": c["span"], "fix": fx, "why": whyf})
            if v.get("fix_gloss_ja"):
                c["gloss_ja"] = v["fix_gloss_ja"]
        if v.get("meaning_preserved") is False:     # 意味が変わった一般化は元の形へ戻す(安全側。D'から継承)
            orig = re.sub(r"[.,;:!?\"()]+$", "", " ".join(G.tokenize(c["span"])).lower())
            if orig != c["display_form"]:
                log.setdefault("reverted_to_span", []).append({"span": c["span"], "from": c["display_form"], "to": orig, "issue": v.get("issue")})
                c["display_form_pre_revert"] = c["display_form"]; c["display_form"] = orig; c["reverted"] = True
        ok, why = V.display_check(c["display_form"], c["span"])
        if not ok:
            log.setdefault("validator_dropped", []).append({"span": c["span"], "display_form": c["display_form"], "why": why})
            continue
        final.append(c)
    return final


def pack(c):
    return dict(source_span=c["span"], source_sentence=c["sentence"], display_form=c["display_form"], gloss_ja=c["gloss_ja"],
                cls=c.get("cls"), chunk_type=c.get("chunk_type"), chunk_reason_ja=c.get("chunk_reason_ja"), difficulty=c.get("difficulty"),
                sense_note_ja=c.get("sense_note_ja"), generalization_note_ja=c.get("generalization_note_ja"), tokens=c.get("tokens"),
                verify=c.get("verify"), display_form_pre_fix=c.get("display_form_pre_fix"), reverted=c.get("reverted", False),
                display_form_pre_revert=c.get("display_form_pre_revert"))


# ============ 方式 ============
def run_E1(case, *, m_sel=LUNA, eff_sel=None, tag="E1", cap=7):
    """Dと同じ順序。塊判定(v3 Prompt)->一般化(v4)->別系列検証。"""
    log = {"stages": [], "tag": tag}
    cands = collect(case, log, tag)
    judged = select(case, cands, log, m_sel=m_sel, eff_sel=eff_sel, tag=tag, mode="span")
    kept = pick(judged, cap)
    items = generalize(case, kept, log, m_gen=LUNA, eff_gen=None, tag=tag, with_chunk=True)
    final = verify(case, items, log, tag=tag, gate=False)
    return {"items": [pack(c) for c in final], "log": log}


def run_E2(case, *, m_sel=LUNA, eff_sel=None, gate=False, tag="E2", cap=7):
    """順序変更: 一般化(全候補)->塊判定(一般化後の形)->別系列検証(+ゲート)。"""
    log = {"stages": [], "tag": tag}
    cands = collect(case, log, tag)
    gen = generalize(case, cands, log, m_gen=LUNA, eff_gen=None, tag=tag, with_chunk=False, label="GEN_ALL")
    # 一般化後に同一display_formとなった候補は代表1件に(cost削減)。span包含重複はpickで除く
    seen, uniq = set(), []
    for c in gen:
        k = c["display_form"].lower()
        if k in seen:
            log.setdefault("dup_display_dropped", []).append(c["span"])
            continue
        seen.add(k); uniq.append(c)
    judged = select(case, uniq, log, m_sel=m_sel, eff_sel=eff_sel, tag=tag, mode="form")
    kept = pick(judged, cap)
    final = verify(case, kept, log, tag=tag, gate=gate)
    return {"items": [pack(c) for c in final], "log": log}


ARMS = {
    "E1L": lambda c: run_E1(c, tag="E1L"),
    "E1S": lambda c: run_E1(c, m_sel=SOL, eff_sel="low", tag="E1S"),
    "E2": lambda c: run_E2(c, tag="E2"),
    "E3": lambda c: run_E2(c, gate=True, tag="E3"),
    "E4": lambda c: run_E2(c, m_sel=SOL, eff_sel="low", gate=True, tag="E4"),
}
