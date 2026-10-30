# -*- coding: utf-8 -*-
"""KP-GENERALIZATION-MEANING-PRESERVATION-TRIAL-03 Trial専用: 方式N1a/N1/N2/N4/N5。Production(er*)非接触・非import。
比較基準=E1L(基本)/D/E4/現行Production。設計=DESIGN_01.md、根拠=ROOT_CAUSE_01.md。
 N1a(切り分け用) : E1Lと同じ候補源+塊判定(span,luna) -> 一般化は塊判定の理由を渡さない(anchor除去) -> 既存VER。E1Lとの差=anchor除去のみ
 N1  (方式B+C統合): N1a + 検証Promptに意味・用法の保持検査を統合(追加call 0)
 N2  (方式A+B+C統合): N1 + 一般化を『意味確定先行』の構造化出力にし、tokensとheadword_frameの不一致を決定論で検出/調停
 N4  (N2 + 方式C限定): N2 + 疑わしい候補(決定論flag)だけを別系列上位モデル(gpt-6.1-sol)で局所文脈つき独立検査
 N5  (参照のみ): N2 + 全候補をsolで検査(N4の限定がどれだけ安く同等かを見る上限対照。限られたcase/probeのみ)
Trial専用。Production経路へ配線しない。"""
import os, sys, re, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kpg04_llm as L                      # 先にimport(kpg03_llm.callの無効化)
import kpg03_methods as M3
M3.L = L                                   # M3.collect/select/generalize/verifyのLLM呼出をkpg04(Cap/台帳)へ差し替え
import kpg01_validate as V
import kpg01_gen2 as G
from kpg01_methods import prompt_B4, B4_SCHEMA, BODY

SOL, LUNA, GEM = M3.SOL, M3.LUNA, M3.GEM
DET = {"the", "a", "an", "this", "that", "these", "those"}
PRON = {"it", "them", "him", "her", "me", "us", "you", "its", "his", "their", "my", "our", "your", "one", "himself", "herself", "itself", "themselves"}
FRAME_BAD = ("OBJECT_DROPPED_SENSE_CHANGED", "SENSE_CHANGED", "FRAME_CHANGED")

# ============ N2: 意味確定先行の一般化(source_sense -> headword_frame -> tokens -> gloss) ============
GEN5_EXTRA = """
## 追加規則(v5。意味確定先行)
**出力の順序を守る**: 各項目で、(1)source_sense_ja(本文の文脈での語句の意味。日本語の意味や塊の理由には頼らず、本文の文と前後から独立に判断する) -> (2)arg_notes(目的語・主語・代名詞が本文で何を指すか。
kind=person/thing/event/personified_thing/fixed_pronoun[慣用表現に含まれる固定のit等]/none) -> (3)headword_frame(学習者用英英辞書の見出し形。someone/something/one's/someone's可。本文の語義と同じ語義の見出しであること)
-> (4)frame_change(本文から見出し形へ行った操作の申告) -> (5)tokens(headword_frameを作る分類にする) -> (6)gloss_ja の順に決める。
A. **someone/somethingは『本文で指す対象』ではなく『その見出し形の辞書上の標準的な用法』で決める**。標準の用法が人を取る見出し(hear someone out / talk someone into / see someone off)なら、本文の目的語が物(擬人化した物を含む)でもSLOT_PERSON(someone)。
   本文の比喩・擬人化はsense_note_jaに書く。物・事を取る見出し(sit through something / shake something off)はSLOT_THING。人も物も取る見出し(put up with)は本文に合わせる。
   慣用表現の一部として固定されたit/them(take it out on / make it up to / call it a day / lose it)は、SLOTにせずCOREのまま残す。
B. **目的語のDROPは、残った形が本文と同じ語義の辞書見出しである場合に限る**。残った形が別の見出し・別の語義になる、または複数の語義を持つ場合
   (take points away from -> take away from[=損なう、別見出し]は不可。take something away from にする。take up space -> take up は語義が不定になるため take up space のままCOREに残す)は、目的語をSLOT_THINGにして枠を残すか、COREに残す。
C. **修飾語(形容詞・副詞)のDROPは許容**: 除いた形が同じ見出し・同じ語義で成立するなら除いてよい(set a lower limit -> set a limit / took an unexpected turn -> take a turn / take good care of -> take care of)。
   成立しない(break new ground / in the long run / turn a blind eye to)ものは修飾語をCOREに残す。
D. **gloss_jaは見出し形(headword_frame)そのものの語義**。DROP/SLOTにした語や修飾語の意味を含めない。本文固有の意味を足さない(本文固有の語義はsense_note_jaへ)。
E. 受動態・過去分詞を核に残さない。動詞は固定句の中でも原形。can't help thinking のように語形そのものが見出しの一部の場合は語形を保つ。
"""

GEN5_SCHEMA = {"name": "kp_gen_tokens5", "schema": {"type": "object", "additionalProperties": False, "required": ["items"], "properties": {
    "items": {"type": "array", "items": {"type": "object", "additionalProperties": False,
        "required": ["id", "source_sense_ja", "arg_notes", "headword_frame", "frame_change", "tokens", "gloss_ja", "sense_note_ja", "note_ja"],
        "properties": {
            "id": {"type": "integer"},
            "source_sense_ja": {"type": "string"},
            "arg_notes": {"type": "array", "items": {"type": "object", "additionalProperties": False, "required": ["n", "referent_ja", "kind"],
                "properties": {"n": {"type": "integer"}, "referent_ja": {"type": "string"},
                               "kind": {"type": "string", "enum": ["person", "thing", "event", "personified_thing", "fixed_pronoun", "none"]}}}},
            "headword_frame": {"type": "string"},
            "frame_change": {"type": "array", "items": {"type": "string", "enum": ["NONE", "OBJECT_SLOT", "OBJECT_DROPPED", "MODIFIER_DROPPED", "POSSESSIVE_SLOT", "INFLECTION", "ARTICLE_DROPPED", "PERSON_OVERRIDE"]}},
            "tokens": {"type": "array", "items": {"type": "object", "additionalProperties": False, "required": ["n", "label", "lemma"],
                "properties": {"n": {"type": "integer"}, "label": {"type": "string", "enum": G.LABELS}, "lemma": {"type": "string"}}}},
            "gloss_ja": {"type": "string"}, "sense_note_ja": {"type": "string"}, "note_ja": {"type": "string"}}}}}}}


def prompt_G5(text, cands):
    blocks = []
    for i, c in enumerate(cands, 1):
        tk = G.tokenize(c["span"])
        blocks.append(f"{i}. 語句: {c['span']}\n   トークン: " + " ".join(f"[{n}]{t}" for n, t in enumerate(tk, 1)) + f"\n   本文の文: {c['sentence']}")
    rules = G.GEN2_RULES.replace("gloss_ja: **一般形", GEN5_EXTRA + "\ngloss_ja: **一般形", 1)
    head = ("次は学習候補です。各語句について、まず本文の意味を確定し、その意味を保つ学習用の見出し形(一般形)を作ってください。"
            "選定は別の工程で行うので、塊かどうかは気にしないでください。ユーザーは提示された形を修正せずにそのまま選びます。\n\n")
    return head + rules + "\n\n【候補】\n" + "\n".join(blocks) + BODY + text


def _norm_hw(s):
    s = re.sub(r"[.,;:!?\"()]+", " ", (s or "").lower().replace("’", "'"))
    s = s.replace("somebody", "someone")
    return [t for t in s.split() if t]


def reconcile(display_form, headword_frame):
    """tokens由来のdisplay_formと、モデルが別表現で書いたheadword_frameの調停(決定論)。
    returns (form, status): SAME / SLOT_TYPE_OVERRIDDEN(someone<->somethingのみ違い。headword側=辞書の標準用法を採用) / FRAME_MISMATCH(それ以外の違い。flag対象、formは変更しない)"""
    d, h = _norm_hw(display_form), _norm_hw(headword_frame)
    if d == h:
        return display_form, "SAME"
    if len(d) == len(h) and all(a == b or {a, b} <= {"something", "someone"} for a, b in zip(d, h)):
        return " ".join(h), "SLOT_TYPE_OVERRIDDEN"
    return display_form, "FRAME_MISMATCH"


def generalize5(case, cands, log, *, tag, label="GEN5"):
    if not cands:
        return []
    o, m = L.call(LUNA, prompt_G5(case["text"], cands), GEN5_SCHEMA, tag=f"{case['id']}:{tag}:{label}", max_out=9000)
    log["stages"].append({"stage": label, **M3._meta(m)})
    gm = {x["id"]: x for x in o["items"]}
    items = []
    for i, c in enumerate(cands, 1):
        x = gm.get(i)
        if not x:
            log.setdefault("gen_missing", []).append(c["span"]); continue
        df, err = G.assemble(c["span"], x["tokens"])
        if df is None:
            log.setdefault("assemble_failed", []).append({"span": c["span"], "err": err}); continue
        df2, st = reconcile(df, x["headword_frame"])
        if st == "SLOT_TYPE_OVERRIDDEN":
            ok, _ = V.display_check(df2, c["span"])
            if ok:
                log.setdefault("slot_type_overridden", []).append({"span": c["span"], "tokens_form": df, "headword_frame": x["headword_frame"], "adopted": df2})
                df = df2
            else:
                st = "FRAME_MISMATCH"
        ok, why = V.display_check(df, c["span"])
        if not ok:
            log.setdefault("gen_validator_dropped", []).append({"span": c["span"], "display_form": df, "why": why}); continue
        items.append(dict(c, display_form=df, gloss_ja=x["gloss_ja"], sense_note_ja=x["sense_note_ja"], generalization_note_ja=x["note_ja"],
                          tokens=[(t["n"], t["label"], t["lemma"]) for t in x["tokens"]], source_sense_ja=x["source_sense_ja"], arg_notes=x["arg_notes"],
                          headword_frame=x["headword_frame"], frame_change=x["frame_change"], reconcile=st))
    return items


# ============ 検証: 既存VERに意味・用法の保持検査を統合(追加call 0) ============
VER5_ADD = """

## 追加検査(意味・用法の保持。上の(a)〜(e)に加えて必ず行う)
各項目で次を判定し、source_sense_ja・frame_preserved・argument_type_okに書く。
(1) source_sense_ja: 本文の文脈で語句が何を意味しているかを日本語で書く。『日本語の意味』『塊の理由』は参考にせず、本文の文と前後から独立に判断する。
(2) frame_preserved: 学習用の形は、本文の語句と『同じ語義・同じ構文(動詞+前置詞/粒子の枠、目的語の有無)』の辞書見出しか。
    SAME=同じ / MODIFIER_DROPPED_OK=修飾語を除いたが同じ見出し・同じ語義 /
    OBJECT_DROPPED_SENSE_CHANGED=目的語を除いた結果、別の見出し・別の語義になった(例: take points away from[減点する] -> take away from[損なう、別見出し]) /
    SENSE_CHANGED=別の語義になった / FRAME_CHANGED=構文の枠が変わった / OTHER。
(3) argument_type_ok: somethingとsomeone、one'sとsomeone'sの選択が、『その見出し形の辞書上の標準的な用法』に合っているか。本文で物を擬人化している場合も、標準の用法が人を取る見出しならsomeoneが正しい(例: hear it out[itは擬人化された物] -> hear someone out)。
修正方針: 形と日本語の意味が食い違うときは、本文の文脈の語義を基準にどちらを直すか決める。**日本語の意味に合わせるためだけに、目的語や前置詞を削ってはならない**(目的語を除くのは、除いた形が本文と同じ語義の見出しである場合に限る)。
frame_preservedがOBJECT_DROPPED_SENSE_CHANGED/SENSE_CHANGED/FRAME_CHANGEDなら、目的語をsomething/someoneで残すfix_display_formを書く(書けなければREJECT)。
修飾語の除去(set a lower limit -> set a limit等)だけを理由にNGにしない。ただしその場合、日本語の意味は『一般形そのものの語義』にし、除いた修飾語の意味を含めない(含んでいればfix_gloss_jaで直す)。"""

_v = json.loads(json.dumps(B4_SCHEMA))
_vi = _v["schema"]["properties"]["verdicts"]["items"]
_vi["properties"].update(source_sense_ja={"type": "string"}, argument_type_ok={"type": "boolean"},
                         frame_preserved={"type": "string", "enum": ["SAME", "MODIFIER_DROPPED_OK", *FRAME_BAD, "OTHER"]})
_vi["required"] = _vi["required"] + ["source_sense_ja", "argument_type_ok", "frame_preserved"]
VER5_SCHEMA = {"name": "kp_verify5", "schema": _v["schema"]}


def prompt_V5(text, items):
    return prompt_B4(text, items) + VER5_ADD


def src_form(span):
    return re.sub(r"[.,;:!?\"()]+$", "", " ".join(G.tokenize(span)).lower())


def revert_to_span(c, log, why, key="reverted_to_span"):
    """意味が変わった一般化は本文の形(正規化のみ)へ戻す(安全側。Productionの『そのまま通す』挙動と同等)。"""
    orig = src_form(c["span"])
    if orig != c["display_form"]:
        log.setdefault(key, []).append({"span": c["span"], "from": c["display_form"], "to": orig, "issue": why})
        c["display_form_pre_revert"] = c["display_form"]; c["display_form"] = orig; c["reverted"] = True


def verify5(case, items, log, *, tag):
    if not items:
        return []
    o, m = L.call(GEM, prompt_V5(case["text"], items), VER5_SCHEMA, tag=f"{case['id']}:{tag}:VER5", think_budget=0, max_out=6000)
    log["stages"].append({"stage": "VER5", **M3._meta(m)})
    vd = {x["id"]: x for x in o["verdicts"]}
    final = []
    for i, c in enumerate(items, 1):
        v = vd.get(i, {})
        c["verify"] = v
        if v.get("verdict") == "REJECT":
            log.setdefault("verify_dropped", []).append({"span": c["span"], "issue": v.get("issue")}); continue
        if v.get("verdict") == "FIX":
            fx = V.strip_trailing_slot((v.get("fix_display_form") or "").replace(" / ", " ").strip())
            if fx:
                okf, whyf = V.display_check(fx, c["span"])
                if okf:
                    if fx != c["display_form"]:
                        c["display_form_pre_fix"] = c["display_form"]; c["display_form"] = fx
                else:
                    log.setdefault("fix_rejected_by_validator", []).append({"span": c["span"], "fix": fx, "why": whyf})
            if v.get("fix_gloss_ja"):
                c["gloss_ja"] = v["fix_gloss_ja"]
        if v.get("meaning_preserved") is False or (v.get("frame_preserved") in FRAME_BAD and not c.get("display_form_pre_fix")):
            revert_to_span(c, log, v.get("issue"))
        ok, why = V.display_check(c["display_form"], c["span"])
        if not ok:
            log.setdefault("validator_dropped", []).append({"span": c["span"], "display_form": c["display_form"], "why": why}); continue
        final.append(c)
    return final


# ============ 疑わしい候補の決定論flag(方式C限定の対象選別。LLM不使用) ============
def flag_item(c):
    fl = []
    sp = G.tokenize(c["span"])
    lab = {n: l for n, l, _ in (c.get("tokens") or [])}
    for n, surf in enumerate(sp, 1):
        l = lab.get(n, "CORE"); s = surf.lower().strip(".,;:!?\"()")
        if l.startswith("SLOT") and s in PRON:
            fl.append("PRONOUN_SLOT")
        if l == "DROP" and s not in DET:
            fl.append("CONTENT_DROPPED")
    if c.get("reconcile") in ("FRAME_MISMATCH", "SLOT_TYPE_OVERRIDDEN"):
        fl.append(c["reconcile"])
    v = c.get("verify") or {}
    pf = c.get("display_form_pre_fix")
    if pf and pf != c.get("display_form"):       # 検証が形を実際に変えた場合のみ(同一形へのFIX=gloss修正のみは対象外)
        fl.append("VER_FIXED_FORM")
    if v.get("frame_preserved") in FRAME_BAD or v.get("argument_type_ok") is False:
        fl.append("VER_FLAG")
    return sorted(set(fl))


# ============ 方式C限定: 別系列上位モデル(sol)の局所文脈つき独立検査 ============
CHK_REL = ["SAME", "MODIFIER_DROPPED_OK", "SENSE_SHIFT", "ARG_TYPE_SHIFT", "FRAME_SHIFT", "GLOSS_MISMATCH"]
CHK5_SCHEMA = {"name": "kp_check5", "schema": {"type": "object", "additionalProperties": False, "required": ["checks"], "properties": {
    "checks": {"type": "array", "items": {"type": "object", "additionalProperties": False,
        "required": ["id", "context_sense_ja", "example_en", "relation", "fix_display_form", "fix_gloss_ja", "reason_ja"],
        "properties": {"id": {"type": "integer"}, "context_sense_ja": {"type": "string"}, "example_en": {"type": "string"},
                       "relation": {"type": "string", "enum": CHK_REL}, "fix_display_form": {"type": "string"}, "fix_gloss_ja": {"type": "string"},
                       "reason_ja": {"type": "string"}}}}}}}

CHK5_RULES = """あなたは英語学習教材の独立審査員です。学習者には『学習用の形(見出し形)』と『日本語の意味』を提示します。各項目について、本文でその語句が使われている意味・用法と、提示形が『同じ語義・同じ構文の見出し』かを、与えられた前後の文脈だけから審査してください(他の工程の判定は与えられません)。
各項目で次の順に書く: (1)context_sense_ja: 文脈での語句の意味 (2)example_en: 提示形と日本語の意味に合う新しい自然な英語例文(本文の語は使わない) (3)relation:
 SAME=同じ語義・同じ構文 / MODIFIER_DROPPED_OK=修飾語を除いたが同じ見出し・語義(set a lower limit -> set a limitのように、日本語が一般形の語義なら問題なし) /
 SENSE_SHIFT=別の語義の見出しになった(例: take points away from[減点する] -> take away from[損なう]) /
 ARG_TYPE_SHIFT=someone/somethingの選択が、見出し形の辞書上の標準用法に合わない(標準が人を取る見出しなら、本文で物を擬人化していてもsomeone) /
 FRAME_SHIFT=構文の枠(目的語の有無・前置詞/粒子)が変わった / GLOSS_MISMATCH=形は妥当だが日本語の意味が形と合わない(除いた修飾語の意味を含む等)。
修正: SENSE_SHIFT/ARG_TYPE_SHIFT/FRAME_SHIFTで本文と同じ語義の形に直せるなら fix_display_form(someone/something/one'sの置換と、目的語・前置詞を残す修正のみ。核の語は本文の語形違いのみ)を書く。GLOSS_MISMATCHなら fix_gloss_ja。不要なら空文字。
易しい表現かどうか、自由な組合せかどうかは審査しない。修飾語の除去だけを理由にNGにしない。"""


def local_context(text, sentence, n=1):
    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.replace("\n", " ")) if s.strip()]
    key = (sentence or "")[:40]
    idx = next((i for i, s in enumerate(sents) if key and key in s), None)
    if idx is None:
        return sentence
    return " ".join(sents[max(0, idx - n): idx + n + 1])


def prompt_C5(text, items):
    lines = [f"{i}. 本文の語句: {c['span']}\n   文脈: {local_context(text, c['sentence'])}\n   学習用の形: {c['display_form']}\n   日本語の意味: {c['gloss_ja']}" for i, c in enumerate(items, 1)]
    return CHK5_RULES + "\n\n【検査対象】\n" + "\n".join(lines)


def run_check(case, items, log, *, tag, scope, model=None):
    """scope='flagged'(疑わしい候補のみ) / 'all'(参照) / 'none'。結果は item['check']に保存、修正はvalidator通過時のみ採用、直せなければ本文の形へ戻す。"""
    for c in items:
        c["flags"] = flag_item(c)
    if scope == "none":
        return items
    tgt = [c for c in items if (scope == "all" or c["flags"]) and not c.get("reverted")]
    log["check_targets"] = [{"span": c["span"], "display_form": c["display_form"], "flags": c["flags"]} for c in tgt]
    if not tgt:
        return items
    model = model or SOL
    if model.startswith("deepseek"):      # 別系列(luna/geminiと別系列)・低単価の検査器(非thinking、max_tokens明示)。JSON形式はプロンプトで指定
        hint = ("\n\n出力はJSONのみ: " + json.dumps({"checks": [{"id": 1, "context_sense_ja": "", "example_en": "", "relation": "SAME", "fix_display_form": "", "fix_gloss_ja": "", "reason_ja": ""}]}, ensure_ascii=False)
                + " の形で全項目分。relationは" + "/".join(CHK_REL) + "のいずれか。説明文は書かない。")
        o, m = L.call_ds(model, prompt_C5(case["text"], tgt) + hint, tag=f"{case['id']}:{tag}:CHK5", max_tokens=4000, mock_name="kp_check5")
    else:
        o, m = L.call(model, prompt_C5(case["text"], tgt), CHK5_SCHEMA, effort="low", tag=f"{case['id']}:{tag}:CHK5", max_out=6000)
    log["stages"].append({"stage": "CHK5", **M3._meta(m)})
    ck = {x["id"]: x for x in o.get("checks", []) if x.get("relation") in CHK_REL}
    for i, c in enumerate(tgt, 1):
        x = ck.get(i)
        if not x:
            continue
        c["check"] = x
        rel = x["relation"]
        if rel in ("SAME", "MODIFIER_DROPPED_OK"):
            if rel == "MODIFIER_DROPPED_OK" and x.get("fix_gloss_ja"):
                c["gloss_ja"] = x["fix_gloss_ja"]
        elif rel == "GLOSS_MISMATCH":
            if x.get("fix_gloss_ja"):
                c["gloss_ja"] = x["fix_gloss_ja"]
        else:
            fx = V.strip_trailing_slot((x.get("fix_display_form") or "").replace(" / ", " ").strip())
            okf = bool(fx) and V.display_check(fx, c["span"])[0]
            if okf:
                log.setdefault("check_fixed", []).append({"span": c["span"], "from": c["display_form"], "to": fx, "relation": rel})
                c["display_form_pre_check"] = c["display_form"]; c["display_form"] = fx
                if x.get("fix_gloss_ja"):
                    c["gloss_ja"] = x["fix_gloss_ja"]
            else:
                revert_to_span(c, log, x.get("reason_ja"), key="check_reverted_to_span")
    return items


# ============ pack / 方式 ============
def pack(c):
    d = M3.pack(c)
    d.update(source_sense_ja=c.get("source_sense_ja"), headword_frame=c.get("headword_frame"), frame_change=c.get("frame_change"),
             reconcile=c.get("reconcile"), flags=c.get("flags", []), check=c.get("check"), display_form_pre_check=c.get("display_form_pre_check"))
    return d


def run_N(case, *, gen, ver, check, tag, cap=7, chk_model=None):
    """gen: 'g4'(anchor除去のみ)/'g5'(意味確定先行) ver: 'old'/'v5' check: 'none'/'flagged'/'all'"""
    log = {"stages": [], "tag": tag}
    cands = M3.collect(case, log, tag)
    judged = M3.select(case, cands, log, m_sel=LUNA, eff_sel=None, tag=tag, mode="span")      # E1Lと同一Prompt(cache hitで費用0)
    kept = M3.pick(judged, cap)
    items = M3.generalize(case, kept, log, m_gen=LUNA, eff_gen=None, tag=tag, with_chunk=False) if gen == "g4" else generalize5(case, kept, log, tag=tag)
    final = M3.verify(case, items, log, tag=tag, gate=False) if ver == "old" else verify5(case, items, log, tag=tag)
    final = run_check(case, final, log, tag=tag, scope=check, model=chk_model)
    return {"items": [pack(c) for c in final], "log": log}


ARMS = {
    "N1a": lambda c: run_N(c, gen="g4", ver="old", check="none", tag="N1a"),
    "N1": lambda c: run_N(c, gen="g4", ver="v5", check="none", tag="N1"),
    "N2": lambda c: run_N(c, gen="g5", ver="v5", check="none", tag="N2"),
    "N4": lambda c: run_N(c, gen="g5", ver="v5", check="flagged", tag="N4"),
    "N5": lambda c: run_N(c, gen="g5", ver="v5", check="all", tag="N5"),
    "N4d": lambda c: run_N(c, gen="g5", ver="v5", check="flagged", tag="N4d", chk_model="deepseek-v4-pro"),   # 検査器を低単価の別系列(deepseek-v4-pro)にした版
}


# ============ 検証ケース(probe)実行: 選定(SEL)を省き、一般化->検証(->検査)だけを短文で測る ============
PROBE_CFG = {"P0": dict(gen="g4", ver="old", check="none"), "P1": dict(gen="g4", ver="v5", check="none"),
             "P2": dict(gen="g5", ver="v5", check="none"), "P4": dict(gen="g5", ver="v5", check="flagged"), "P5": dict(gen="g5", ver="v5", check="all"),
             "P4d": dict(gen="g5", ver="v5", check="flagged", chk_model="deepseek-v4-pro")}


def run_probe(cfg_name, probes):
    cfg = PROBE_CFG[cfg_name]
    text = "\n\n".join(f"[{p['id']}] {p['context']}" for p in probes)
    case = {"id": "probes", "text": text}
    log = {"stages": [], "tag": cfg_name}
    cands = [dict(span=p["span"], sentence=p["sentence"], chunk_type="phrasal_verb", chunk_reason_ja="", cls="C", difficulty="upper_intermediate", keep=True, probe_id=p["id"]) for p in probes]
    items = M3.generalize(case, cands, log, m_gen=LUNA, eff_gen=None, tag=cfg_name, with_chunk=False) if cfg["gen"] == "g4" else generalize5(case, cands, log, tag=cfg_name)
    final = M3.verify(case, items, log, tag=cfg_name, gate=False) if cfg["ver"] == "old" else verify5(case, items, log, tag=cfg_name)
    final = run_check(case, final, log, tag=cfg_name, scope=cfg["check"], model=cfg.get("chk_model"))
    out = []
    for c in final:
        d = pack(c); d["probe_id"] = c.get("probe_id"); out.append(d)
    return {"items": out, "log": log, "cfg": cfg_name}


def score_probe(item, probe):
    """決定論採点: PASS(許容形) / FAIL(既知のNG形) / REVIEW(どちらでもない=Sonnet実読)。"""
    f = " ".join(_norm_hw(item["display_form"]))
    ok = {" ".join(_norm_hw(x)) for x in probe.get("ok", [])}
    ng = {" ".join(_norm_hw(x)) for x in probe.get("ng", [])}
    if f in ng:
        return "FAIL"
    if f in ok:
        return "PASS"
    return "REVIEW"
