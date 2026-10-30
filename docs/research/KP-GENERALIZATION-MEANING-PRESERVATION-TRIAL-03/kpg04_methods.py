# -*- coding: utf-8 -*-
"""KP-GENERALIZATION-MEANING-PRESERVATION-TRIAL-03 Trial専用: 方式N1a/N1/N2/N4/N4d/N5。Production(er*)非接触・非import。
比較基準=E1L(基本)/D/E4/現行Production。設計=DESIGN_01.md(委任_01)+委任_02のOpus条件Aレビュー反映(M1〜M10)、根拠=ROOT_CAUSE_01.md。
 N1a(切り分け用) : E1Lと同じ候補源+塊判定(span,luna) -> 一般化は塊判定の理由を渡さず(anchor除去)、検証入力からも理由を外す -> 旧VER Prompt(文言は旧のまま)。E1Lとの差=anchor除去のみ
 N1  (方式B+C統合): N1a + 検証Prompt(VER5: 本文基準の語義導出、目的語を訳に合わせて削らない、戻す方向のfix可)
 N2  (方式A+B+C統合): N1 + 一般化を『意味確定先行』の構造化出力にし、tokensとheadword_frameの不一致を決定論で検出/調停
 N4  (N2 + 方式C限定): N2 + 疑わしい候補(凍結した決定論flag)だけを別系列上位モデル(gpt-6.1-sol)で局所文脈つき独立検査
 N4d (N4の検査器をdeepseek-v4-pro) / N5(参照のみ: 全候補をsolで検査)
委任_02の変更点(M1〜M10): M1 戻す時は訳も本文語義へ(取れなければ除外)・本文形はlemma化 / M2 VER FIXがslot/CORE語を削る場合は不採用・arg_type_ok=False+FIXなしは戻し
 / M3 VER入力から塊の理由を外す・矛盾文言の整合 / M9 reconcile正規化・flag定義凍結。Trial専用。Production経路へ配線しない。"""
import os, sys, re, json, hashlib
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kpg04_llm as L                      # 先にimport(kpg03_llm.callの無効化)
import kpg03_methods as M3
M3.L = L                                   # M3.collect/select/generalize/verifyのLLM呼出をkpg04(Cap/台帳)へ差し替え
import kpg01_validate as V
import kpg01_gen2 as G
from kpg01_methods import prompt_B4, B4_SCHEMA, BODY

SOL, LUNA, GEM = M3.SOL, M3.LUNA, M3.GEM
DS_PRO = "deepseek-v4-pro"
DET = {"the", "a", "an", "this", "that", "these", "those"}
PRON = {"it", "them", "him", "her", "me", "us", "you", "its", "his", "their", "my", "our", "your", "one", "himself", "herself", "itself", "themselves"}
FRAME_BAD = ("OBJECT_DROPPED_SENSE_CHANGED", "SENSE_CHANGED", "FRAME_CHANGED")
SLOT_WORDS = {"something", "someone", "one's", "someone's", "oneself"}

# ============ N2: 意味確定先行の一般化(source_sense -> headword_frame -> tokens -> gloss) ============
GEN5_EXTRA = """
## 追加規則(v5。意味確定先行)
**出力の順序を守る**: 各項目で、(1)source_sense_ja(本文の文脈での語句の意味を、辞書の語義gloss形式で20〜30字。日本語の意味や塊の理由には頼らず、本文の文と前後から独立に判断する) -> (2)arg_notes(目的語・主語・代名詞が本文で何を指すか。
kind=person/thing/event/personified_thing/fixed_pronoun[慣用表現に含まれる固定のit等]/none) -> (3)headword_frame(学習者用英英辞書の見出し形。someone/something/one's/someone's可。本文の語義と同じ語義の見出しであること)
-> (4)frame_change(本文から見出し形へ行った操作の申告) -> (5)tokens(headword_frameを作る分類にする) -> (6)gloss_ja の順に決める。
A. **someone/somethingは『本文で指す対象』ではなく『その見出し形の辞書上の標準的な用法』で決める**。標準の用法が人を取る見出し(hear someone out / talk someone into / see someone off)なら、本文の目的語が物(擬人化した物を含む)でもSLOT_PERSON(someone)。
   本文の比喩・擬人化はsense_note_jaに書く。物・事を取る見出し(sit through something / shake something off)はSLOT_THING。人も物も取る見出し(put up with)は本文に合わせる。
   **someoneかsomethingかで語義が変わる句動詞(bring someone up[育てる]/bring something up[話題に出す]、put someone up[泊める]/put something up[建てる]、see someone through[支える]/see something through[やり遂げる])は、本文の語義に合う方を選ぶ**。
   慣用表現の一部として固定されたit/them(take it out on / make it up to / call it a day / lose it)は、SLOTにせずCOREのまま残す。
B. **目的語のDROPは、残った形が本文と同じ語義の辞書見出しである場合に限る**。目的語を除くと語義が不定になる動詞+粒子(take up / put up / bring up / pick up / see through)や、人か物かで語義が変わる句動詞は、目的語をDROPせずSLOT_PERSON/SLOT_THINGで残す(put up the tent -> put something up、put up our guests -> put someone up)。残った形が別の見出し・別の語義になる、または複数の語義を持つ場合
   (take points away from -> take away from[=損なう、別見出し]は不可。take something away from にする。take up space -> take up は語義が不定になるため take up space のままCOREに残す)は、目的語をSLOT_THINGにして枠を残すか、COREに残す。
C. **修飾語(形容詞・副詞)のDROPは許容**: 除いた形が同じ見出し・同じ語義で成立するなら除いてよい(set a lower limit -> set a limit / took an unexpected turn -> take a turn / take good care of -> take care of)。
   成立しない(break new ground / in the long run / turn a blind eye to / give someone a big hand[拍手] / take a back seat)ものは修飾語をCOREに残す。
D. **gloss_jaは見出し形(headword_frame)そのものの語義**。DROP/SLOTにした語や修飾語の意味を含めない。本文固有の意味を足さない(本文固有の語義はsense_note_jaへ)。
E. 受動態・過去分詞を核に残さない。動詞は固定句の中でも原形。can't help thinking のように語形そのものが見出しの一部の場合は語形を保つ。
   **名詞の複数形が表現に固定されているもの(come to terms with / make ends meet / articles of incorporation / on good terms)は、lemmaも複数形のまま書く(単数化しない)**。
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


# ---- 正規化(M9): 末尾slot・one's・oneself・sb/sth・to不定詞
def _norm_hw(s):
    s = (s or "").lower().replace("’", "'")
    s = re.sub(r"[.,;:!?\"()]+", " ", s)
    s = re.sub(r"\bsomebody's\b|\bsb's\b", "someone's", s)
    s = re.sub(r"\bsomebody\b|\bsb\b", "someone", s)
    s = re.sub(r"\bsth\b", "something", s)
    s = re.sub(r"\b(yourself|himself|herself|themselves|myself)\b", "oneself", s)
    t = [x for x in s.split() if x]
    if t and t[0] == "to" and len(t) > 1:
        t = t[1:]
    return t


def _strip_trail(t):
    t = list(t)
    while t and t[-1] in SLOT_WORDS and len(t) > 1:
        t.pop()
    return t


def _swappable(a, b):
    return a == b or {a, b} <= {"something", "someone"} or {a, b} <= {"one's", "someone's"}


def reconcile(display_form, headword_frame):
    """tokens由来のdisplay_formと、モデルが別表現で書いたheadword_frameの調停(決定論)。
    returns (form, status): SAME / SLOT_TYPE_OVERRIDDEN(someone<->something、one's<->someone'sのみ違い。headword側=辞書の標準用法を採用) / FRAME_MISMATCH(それ以外の違い。flag対象、formは変更しない)"""
    d, h = _strip_trail(_norm_hw(display_form)), _strip_trail(_norm_hw(headword_frame))
    if d == h:
        return display_form, "SAME"
    if len(d) == len(h) and all(_swappable(a, b) for a, b in zip(d, h)):
        return " ".join(h), "SLOT_TYPE_OVERRIDDEN"
    core_d, core_h = [t for t in d if t not in SLOT_WORDS], [t for t in h if t not in SLOT_WORDS]
    if core_d == core_h and sum(t in SLOT_WORDS for t in h) > sum(t in SLOT_WORDS for t in d):
        return " ".join(h), "SLOT_INSERTED"          # 核は同じで、見出しには語義を決める目的語枠がある(put up -> put someone up)。目的語枠を戻す方向のみ採用
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
        if st in ("SLOT_TYPE_OVERRIDDEN", "SLOT_INSERTED"):
            ok, _ = V.display_check(df2, c["span"])
            if ok:
                log.setdefault("slot_type_overridden" if st == "SLOT_TYPE_OVERRIDDEN" else "slot_inserted", []).append(
                    {"span": c["span"], "tokens_form": df, "headword_frame": x["headword_frame"], "adopted": df2})
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


# ============ 検証5: 本文基準の意味・用法検査(追加call 0)。M3: 『塊の理由』を入力に含めず、旧Promptの矛盾文言(戻す方向のfix禁止/不要な目的語)を整合 ============
VER5_HEAD = ("あなたは英語教材の校閲者です。本文の語句を学習用の一般形に直した結果を検査してください。\n"
             "この検査は『この語句を選ぶべきか』の判断ではありません(選定は完了済み)。形と意味の検査だけを行ってください。各項目について: (a)学習用の形は本文の語句と同じ意味・語義を保っているか(別の意味になっていないか)、(b)日本語の意味は学習用の形と本文の語義の両方に合っているか、"
             "(c)学習用の形は辞書の見出し語として自然で、別の文脈でも使える英語か。本文の語義に必要な目的語(someone/something)・前置詞・固定語が欠けていないか、逆に本文固有の文脈語が残っていないか、"
             "(d)自由に入れ替わる目的語名詞(意味の違う別の名詞に替えても同じ構文・同じ意味で成り立つもの)が、somethingやsomeoneにならずに残っていないか、"
             "(e)前置詞で終わる固定表現の後ろに、本文固有の名詞句・動名詞が残っていないか(学習用の表示では核を明確にするため除く)、を判定する。(d)(e)に該当する場合はFIXとし、fix_display_formに直した形を書く。\n"
             "verdict: OK=そのままユーザーに提示できる / FIX=小さな修正で提示できる(fix_display_form/fix_gloss_jaに修正案。核の語は本文の語の語形違いのみ、something/someone/one'sのみ置換可) / REJECT=一般化で意味・語義が変わる、または英語として不自然で修正案も作れず提示不可。選定の是非(塊としての価値)を理由にREJECTしない。\n"
             "**重要(fixの方向)**: 学習用の形が本文固有の語(DROP/something化した語)を除いて一般化されているのは原則として意図どおり(例: at the time of writing -> at the time of は正しい一般化)。"
             "ただし除いた結果が本文と別の語義・別の構文になる場合は、除いた目的語をsomething/someone/one'sで残す、または本文の語を戻す方向のfix_display_formを書いてよい。"
             "**日本語の意味に合わせるためだけに、目的語や前置詞を削るfixは書かない**(その場合は日本語の側を本文の語義に合わせて直す)。日本語の意味が一般形より具体的すぎる(除いた語の意味を含む)場合は、fix_gloss_jaで日本語の側を一般形に合わせて直す。"
             "日本語の意味は名詞句・副詞句・動詞句のいずれの形でもよく、品詞の形だけを理由にFIXしない。fix_gloss_jaを書くときも、日本語の意味は**本文での語義(sense)を保つ**こと。辞書にある別の語義や、より一般的な語義に置き換えない(例: 『順序を逆にする』の意味を『好転させる』に変えない)。OKのとき、fix欄は空文字。\n")

VER5_ADD = """

## 追加検査(意味・用法の保持。上の(a)〜(e)に加えて必ず行う)
各項目で次を判定し、source_sense_ja・frame_preserved・argument_type_okに書く。
(1) source_sense_ja: 本文の文脈で語句が何を意味しているかを、辞書の語義gloss形式で20〜30字の日本語で書く。『日本語の意味』は参考にせず、本文の文と前後から独立に判断する。
(2) frame_preserved: 学習用の形は、本文の語句と『同じ語義・同じ構文(動詞+前置詞/粒子の枠、目的語の有無)』の辞書見出しか。
    SAME=同じ / MODIFIER_DROPPED_OK=修飾語を除いたが同じ見出し・同じ語義 /
    OBJECT_DROPPED_SENSE_CHANGED=目的語を除いた結果、別の見出し・別の語義になった(例: take points away from[減点する] -> take away from[損なう、別見出し]) /
    SENSE_CHANGED=別の語義になった / FRAME_CHANGED=前置詞・粒子を落とす/変える、または表現の途中の目的語を落とすことで、別の語義になる・語義が不定になる(例: came to terms with -> come to terms、looked down on -> look down、took up space -> take up)/ OTHER。
    **表示の約束(これらはFRAME_CHANGEDにもOBJECT_DROPPEDにも該当しない)**: (i)前置詞・粒子で終わる形は末尾の目的語(something/someone)を示さない約束である(take something away from / put up with / look down on / take it out on / make it up to / talk someone into)。末尾に目的語が無いこと自体は誤りではない。
    (ii)目的語を示さなくても同じ語義の見出しとして通用する形(carry out / narrow down / tighten up / look into / sort out)は、目的語が無くてよい。(iii)本文の語句に付いている助詞・修飾語・本文固有の補語(joining、the whole lecture等)が形から除かれているのは意図どおり。
(3) argument_type_ok: somethingとsomeone、one'sとsomeone'sの選択が、『その見出し形の辞書上の標準的な用法』と『本文の語義』に合っているか。本文で物を擬人化している場合も、標準の用法が人を取る見出しならsomeoneが正しい(例: hear it out[itは擬人化された物] -> hear someone out)。
    someoneかsomethingかで語義が変わる句動詞は、本文の語義に合う方が正しい。
修正方針: 形と日本語の意味が食い違うときは、本文の文脈の語義を基準にどちらを直すか決める。**日本語の意味に合わせるためだけに、目的語や前置詞を削ってはならない**。
frame_preservedがOBJECT_DROPPED_SENSE_CHANGED/SENSE_CHANGED/FRAME_CHANGEDなら、目的語をsomething/someoneで残すfix_display_formを書く(書けなければREJECT)。
修飾語の除去(set a lower limit -> set a limit等)だけを理由にNGにしない。ただしその場合、日本語の意味は『一般形そのものの語義』にし、除いた修飾語の意味を含めない(含んでいればfix_gloss_jaで直す)。"""

_v = json.loads(json.dumps(B4_SCHEMA))
_vi = _v["schema"]["properties"]["verdicts"]["items"]
_vi["properties"].update(source_sense_ja={"type": "string"}, argument_type_ok={"type": "boolean"},
                         frame_preserved={"type": "string", "enum": ["SAME", "MODIFIER_DROPPED_OK", *FRAME_BAD, "OTHER"]})
_vi["required"] = _vi["required"] + ["source_sense_ja", "argument_type_ok", "frame_preserved"]
VER5_SCHEMA = {"name": "kp_verify5", "schema": _v["schema"]}


def prompt_V5(text, items):
    lines = [f"{i}. 本文の語句: {c['span']}\n   本文の文: {c['sentence']}\n   学習用の形: {c['display_form']}\n   日本語の意味: {c['gloss_ja']}" for i, c in enumerate(items, 1)]
    return VER5_HEAD + VER5_ADD + "\n\n【検査対象】\n" + "\n".join(lines) + BODY + text


def prompt_B4_noreason(text, items):
    """N1a/P0用: 旧VER Prompt(文言は旧のまま)から『塊の理由』行だけを外す(アンカー除去の切り分け)。"""
    return re.sub(r"\n   塊の理由: [^\n]*", "", prompt_B4(text, items))


def src_form(span):
    return re.sub(r"[.,;:!?\"()]+$", "", " ".join(G.tokenize(span)).lower())


def _verb_base(w):
    try:
        return V.wn.morphy(w, "v") or w
    except Exception:
        return w


def revert_form(c):
    """M1: 本文の形へ戻す時の形。先頭の動詞だけをWordNet/GENのlemmaで原形化(P7のcanonicalizationと同等の動詞原形化。took -> take)。それ以外の語は本文の語形のまま
    (複数形固定の名詞come to termsの単数化や名詞articles of incorporationの誤原形化を避ける)。"""
    sp = G.tokenize(c["span"])
    lab = {n: (l, lem) for n, l, lem in (c.get("tokens") or [])}
    out = []
    for n, surf in enumerate(sp, 1):
        s = surf.lower().strip(".,;:!?\"()")
        if n == 1:
            nxt = sp[1].lower().strip(".,;:!?\"()") if len(sp) > 1 else ""
            noun_head = s.endswith("s") and nxt in {"of", "in", "for", "on", "to", "with", "at", "from", "by"} and bool(V.wn.synsets(s, "n"))
            lem = (lab.get(1, ("", ""))[1] or "").strip().lower()
            vb = _verb_base(s)
            out.append(s if noun_head else (lem if lem and lem == vb else vb))
        else:
            out.append(s)
    f = re.sub(r"\s+", " ", " ".join(out)).strip()
    return f if V.display_check(f, c["span"])[0] else src_form(c["span"])


def span_gloss(case, c):
    """M1: 本文の語義を表す日本語gloss。優先=現行Productionの同一span gloss > VER5のsource_sense_ja(独立導出) > GEN5のsource_sense_ja > sense_note_ja。取れなければ(None, None)。"""
    for b in ((case.get("before") or {}).get("candidates") or []):
        if _norm_hw(b.get("selection_phrase")) == _norm_hw(c["span"]) and (b.get("gloss") or "").strip():
            return b["gloss"].strip(), "PROD_GLOSS"
    for key, src in (("verify.source_sense_ja", c.get("verify") or {}), ("source_sense_ja", c), ("sense_note_ja", c)):
        x = (src.get(key.split(".")[-1]) or "").strip()
        if x:
            return x, key
    return None, None


def revert_to_span(case, c, log, why, key="reverted_to_span"):
    """M1: 意味が変わった一般化は、形を本文の形(lemma化)へ、訳も本文語義へ戻す。訳が取れずに形が変わる場合は除外(False)。"""
    orig = revert_form(c)
    gl, gsrc = span_gloss(case, c)
    changed = orig != c["display_form"]
    if changed and not gl:
        log.setdefault("reverted_dropped_no_gloss", []).append({"span": c["span"], "from": c["display_form"], "issue": why})
        return False
    log.setdefault(key, []).append({"span": c["span"], "from": c["display_form"], "to": orig, "gloss_from": c.get("gloss_ja"), "gloss_to": gl or c.get("gloss_ja"),
                                    "gloss_src": gsrc, "issue": why})
    c["display_form_pre_revert"], c["gloss_pre_revert"] = c["display_form"], c.get("gloss_ja")
    c["display_form"], c["reverted"] = orig, True
    if gl:
        c["gloss_ja"], c["gloss_source"] = gl, gsrc
    return True


def fix_drops_content(pre, fix):
    """M2: FIXがFIX前の形から something/someone/one's 等のslotや核(CORE)語を削るか。返り値=削られた要素のlist(空=削っていない)。冠詞の増減は無視。slotの種類の入替(someone<->something)は削除ではない。"""
    a = [t for t in _norm_hw(pre) if t not in DET]
    b = [t for t in _norm_hw(fix) if t not in DET]
    def groups(ts):             # 連続するslot(one's someone等の重複表記)は1つの目的語枠として数える
        n, prev = 0, False
        for t in ts:
            cur = t in SLOT_WORDS
            n += (cur and not prev)
            prev = cur
        return n
    a_slots, b_slots = groups(a), groups(b)
    a_core = [t for t in a if t not in SLOT_WORDS]
    b_core = [t for t in b if t not in SLOT_WORDS]
    gone = []
    pool = list(b_core)
    for t in a_core:
        hit = next((x for x in pool if x == t or V.same_word(x, t)), None)
        if hit is None:
            gone.append(t)
        else:
            pool.remove(hit)
    if b_slots < a_slots:
        gone.append("<slot>")
    return gone


def verify_old(case, items, log, *, tag, strip_reason):
    """旧VER(M3.verifyの非gate版の複製。Prompt文言は旧のまま)。strip_reason=True: 塊の理由行を外す(N1a/P0)。False: 理由を渡す(P0i=E1L再現)。
    基線として挙動は旧と同一(M1/M2の改良は適用しない)。"""
    if not items:
        return []
    pr = (prompt_B4_noreason if strip_reason else prompt_B4)(case["text"], items)
    o, m = L.call(GEM, pr, B4_SCHEMA, tag=f"{case['id']}:{tag}:VER", think_budget=0, max_out=4500)
    log["stages"].append({"stage": "VER", **M3._meta(m)})
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
                    c["display_form_pre_fix"] = c["display_form"]; c["display_form"] = fx
                else:
                    log.setdefault("fix_rejected_by_validator", []).append({"span": c["span"], "fix": fx, "why": whyf})
            if v.get("fix_gloss_ja"):
                c["gloss_ja"] = v["fix_gloss_ja"]
        if v.get("meaning_preserved") is False:
            orig = src_form(c["span"])
            if orig != c["display_form"]:
                log.setdefault("reverted_to_span", []).append({"span": c["span"], "from": c["display_form"], "to": orig, "issue": v.get("issue")})
                c["display_form_pre_revert"] = c["display_form"]; c["display_form"] = orig; c["reverted"] = True
        ok, why = V.display_check(c["display_form"], c["span"])
        if not ok:
            log.setdefault("validator_dropped", []).append({"span": c["span"], "display_form": c["display_form"], "why": why}); continue
        final.append(c)
    return final


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
        c["gloss_pre_ver"] = c["gloss_ja"]
        form_fixed, fix_blocked = False, False
        if v.get("verdict") == "FIX":
            fx = V.strip_trailing_slot((v.get("fix_display_form") or "").replace(" / ", " ").strip())
            if fx and _norm_hw(fx) != _norm_hw(c["display_form"]):
                okf, whyf = V.display_check(fx, c["span"])
                gone = fix_drops_content(c["display_form"], fx) if okf else []
                if not okf:
                    fix_blocked = True
                    log.setdefault("fix_rejected_by_validator", []).append({"span": c["span"], "fix": fx, "why": whyf})
                elif gone:                       # M2: FIXがslot/CORE語を削る(訳に形を合わせる誤り型)。決定論で不採用
                    fix_blocked = True
                    log.setdefault("fix_rejected_slot_drop", []).append({"span": c["span"], "pre_fix": c["display_form"], "fix": fx, "dropped": gone, "fix_gloss": v.get("fix_gloss_ja")})
                else:
                    c["display_form_pre_fix"] = c["display_form"]; c["display_form"] = fx; form_fixed = True
            if fix_blocked:
                c["fix_rejected"] = True        # 不採用FIXの訳修正も採らない(削った形に合わせた訳のため)
            elif v.get("fix_gloss_ja"):
                c["gloss_ja"] = v["fix_gloss_ja"]
        why_rv = None
        if v.get("meaning_preserved") is False:
            why_rv = "meaning_preserved=false"
        elif v.get("frame_preserved") in FRAME_BAD and not form_fixed:
            why_rv = f"frame_preserved={v.get('frame_preserved')}(FIXなし)"
        elif v.get("argument_type_ok") is False and not form_fixed:
            why_rv = "argument_type_ok=false(FIXなし)"; c["arg_unfixed"] = True
        if why_rv:
            if not revert_to_span(case, c, log, f"{why_rv}: {v.get('issue')}"):
                continue
        ok, why = V.display_check(c["display_form"], c["span"])
        if not ok:
            log.setdefault("validator_dropped", []).append({"span": c["span"], "display_form": c["display_form"], "why": why}); continue
        final.append(c)
    return final


# ============ 疑わしい候補の決定論flag(方式C限定の対象選別。LLM不使用)。M9: 定義をP1前に凍結(FLAGS_V1)。結果を見てから変えない ============
FLAGS_V1 = {
    "PRONOUN_SLOT": "代名詞(it/them/her等)がSLOT(something/someone)にされた",
    "CONTENT_DROPPED": "冠詞・指示詞以外の語(修飾語・目的語・文脈語)がDROPされた",
    "SLOT_TYPE_OVERRIDDEN": "tokensのsomeone/something(one's/someone's)とheadword_frameが食い違い、headword側を採用した(決定論調停)",
    "FRAME_MISMATCH": "tokens由来の形とheadword_frameが構造的に食い違う(調停不可)",
    "PERSON_OVERRIDE": "GEN5自身がframe_changeでPERSON_OVERRIDE(本文の指示対象と見出しの標準項タイプが異なる)を申告した",
    "PERSONIFIED_THING": "arg_notesに擬人化された物(personified_thing)がある",
    "VER_FIXED_FORM": "VERが形を実際に変更した(同一形のgloss修正のみは対象外)",
    "VER_FLAG": "VERが frame_preserved=NG または argument_type_ok=false と報告した",
    "VER_GLOSS_FIXED": "VERが日本語の意味を修正した(訳が本文語義から離れる経路)",
    "FIX_REJECTED": "VERのFIXを決定論規則(slot/CORE語を削る/validator不通過)で不採用にした",
}
FLAGS_V1_HASH = hashlib.sha256(json.dumps(FLAGS_V1, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:12]


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
    if "PERSON_OVERRIDE" in (c.get("frame_change") or []):
        fl.append("PERSON_OVERRIDE")
    if any(a.get("kind") == "personified_thing" for a in (c.get("arg_notes") or [])):
        fl.append("PERSONIFIED_THING")
    v = c.get("verify") or {}
    pf = c.get("display_form_pre_fix")
    if pf and pf != c.get("display_form"):       # 検証が形を実際に変更した場合のみ(同一形へのFIX=gloss修正のみは対象外)
        fl.append("VER_FIXED_FORM")
    if v.get("frame_preserved") in FRAME_BAD or v.get("argument_type_ok") is False:
        fl.append("VER_FLAG")
    if c.get("gloss_pre_ver") is not None and c.get("gloss_ja") != c.get("gloss_pre_ver") and not c.get("reverted"):
        fl.append("VER_GLOSS_FIXED")
    if c.get("fix_rejected"):
        fl.append("FIX_REJECTED")
    return sorted(set(fl))


# ============ 方式C限定: 別系列上位モデル(sol / deepseek-v4-pro)の局所文脈つき独立検査 ============
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
 ARG_TYPE_SHIFT=someone/somethingの選択が、見出し形の辞書上の標準用法または本文の語義に合わない(標準が人を取る見出しなら、本文で物を擬人化していてもsomeone) /
 FRAME_SHIFT=構文の枠(目的語の有無・前置詞/粒子)が変わった / GLOSS_MISMATCH=形は妥当だが日本語の意味が形と合わない、または日本語の意味が本文とは別の語義(除いた修飾語の意味を含む等)。
修正: SENSE_SHIFT/ARG_TYPE_SHIFT/FRAME_SHIFTで本文と同じ語義の形に直せるなら fix_display_form(someone/something/one'sの置換と、目的語・前置詞を残す修正のみ。核の語は本文の語形違いのみ)と、その形に合う日本語 fix_gloss_ja(必須)を書く。GLOSS_MISMATCHなら fix_gloss_ja。不要なら空文字。
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
    """scope='flagged'(疑わしい候補のみ) / 'all'(参照) / 'none'。結果は item['check']に保存。修正はvalidator通過+訳つき+slot/CORE語を削らない場合のみ採用、直せなければ本文の形(訳も本文語義)へ戻す。"""
    for c in items:
        c["flags"] = flag_item(c)
    if scope == "none":
        return items
    tgt = [c for c in items if (scope == "all" or c["flags"]) and not c.get("reverted")]
    log["check_targets"] = [{"span": c["span"], "display_form": c["display_form"], "flags": c["flags"]} for c in tgt]
    if not tgt:
        return items
    model = model or SOL
    if model.startswith("deepseek"):      # 別系列・低単価の検査器(非thinking、max_tokens明示)。JSON形式はプロンプトで指定
        hint = ("\n\n出力はJSONのみ: " + json.dumps({"checks": [{"id": 1, "context_sense_ja": "", "example_en": "", "relation": "SAME", "fix_display_form": "", "fix_gloss_ja": "", "reason_ja": ""}]}, ensure_ascii=False)
                + " の形で全項目分。relationは" + "/".join(CHK_REL) + "のいずれか。説明文は書かない。")
        o, m = L.call_ds(model, prompt_C5(case["text"], tgt) + hint, tag=f"{case['id']}:{tag}:CHK5", max_tokens=4000, mock_name="kp_check5")
    else:
        o, m = L.call(model, prompt_C5(case["text"], tgt), CHK5_SCHEMA, effort="low", tag=f"{case['id']}:{tag}:CHK5", max_out=3500)
    log["stages"].append({"stage": "CHK5", **M3._meta(m)})
    ck = {x["id"]: x for x in o.get("checks", []) if x.get("relation") in CHK_REL}
    dropped = []
    for i, c in enumerate(tgt, 1):
        x = ck.get(i)
        if not x:
            continue
        c["check"] = x
        rel = x["relation"]
        if rel in ("SAME", "MODIFIER_DROPPED_OK"):
            if rel == "MODIFIER_DROPPED_OK" and x.get("fix_gloss_ja"):
                c["gloss_pre_check"] = c["gloss_ja"]; c["gloss_ja"] = x["fix_gloss_ja"]
        elif rel == "GLOSS_MISMATCH":
            if x.get("fix_gloss_ja"):
                c["gloss_pre_check"] = c["gloss_ja"]; c["gloss_ja"] = x["fix_gloss_ja"]
            else:
                if not revert_to_span(case, c, log, x.get("reason_ja"), key="check_reverted_to_span"):
                    dropped.append(c)
        else:
            fx = V.strip_trailing_slot((x.get("fix_display_form") or "").replace(" / ", " ").strip())
            okf = bool(fx) and bool((x.get("fix_gloss_ja") or "").strip()) and V.display_check(fx, c["span"])[0] and not fix_drops_content(c["display_form"], fx)
            if okf:
                log.setdefault("check_fixed", []).append({"span": c["span"], "from": c["display_form"], "to": fx, "relation": rel, "gloss_from": c["gloss_ja"], "gloss_to": x["fix_gloss_ja"]})
                c["display_form_pre_check"], c["gloss_pre_check"] = c["display_form"], c["gloss_ja"]
                c["display_form"], c["gloss_ja"] = fx, x["fix_gloss_ja"]
            elif not revert_to_span(case, c, log, f"{rel}: {x.get('reason_ja')}", key="check_reverted_to_span"):
                dropped.append(c)
    return [c for c in items if c not in dropped]


# ============ pack / 方式 ============
def pack(c):
    d = M3.pack(c)
    d.update(source_sense_ja=c.get("source_sense_ja"), headword_frame=c.get("headword_frame"), frame_change=c.get("frame_change"),
             reconcile=c.get("reconcile"), flags=c.get("flags", []), check=c.get("check"), display_form_pre_check=c.get("display_form_pre_check"),
             gloss_pre_revert=c.get("gloss_pre_revert"), gloss_pre_check=c.get("gloss_pre_check"), gloss_pre_ver=c.get("gloss_pre_ver"),
             gloss_source=c.get("gloss_source"), fix_rejected=c.get("fix_rejected", False), arg_unfixed=c.get("arg_unfixed", False), arg_notes=c.get("arg_notes"))
    return d


def run_N(case, *, gen, ver, check, tag, cap=7, chk_model=None):
    """gen: 'g4'(anchor除去のみ)/'g5'(意味確定先行) ver: 'old'(理由なし旧Prompt)/'v5' check: 'none'/'flagged'/'all'"""
    log = {"stages": [], "tag": tag, "flags_v1_hash": FLAGS_V1_HASH}
    cands = M3.collect(case, log, tag)
    judged = M3.select(case, cands, log, m_sel=LUNA, eff_sel=None, tag=tag, mode="span")      # E1Lと同一Prompt(cache hitで費用0)
    kept = M3.pick(judged, cap)
    items = M3.generalize(case, kept, log, m_gen=LUNA, eff_gen=None, tag=tag, with_chunk=False) if gen == "g4" else generalize5(case, kept, log, tag=tag)
    final = verify_old(case, items, log, tag=tag, strip_reason=True) if ver == "old" else verify5(case, items, log, tag=tag)
    final = run_check(case, final, log, tag=tag, scope=check, model=chk_model)
    log["retries"] = list(L.RETRY_LOG)
    return {"items": [pack(c) for c in final], "log": log}


ARMS = {
    "N1a": lambda c: run_N(c, gen="g4", ver="old", check="none", tag="N1a"),
    "N1": lambda c: run_N(c, gen="g4", ver="v5", check="none", tag="N1"),
    "N2": lambda c: run_N(c, gen="g5", ver="v5", check="none", tag="N2"),
    "N4": lambda c: run_N(c, gen="g5", ver="v5", check="flagged", tag="N4"),
    "N5": lambda c: run_N(c, gen="g5", ver="v5", check="all", tag="N5"),
    "N4d": lambda c: run_N(c, gen="g5", ver="v5", check="flagged", tag="N4d", chk_model=DS_PRO),   # 検査器を低単価の別系列(deepseek-v4-pro)にした版
    "E1L": lambda c: M3.run_E1(c, tag="E1L"),     # held-out用の基準(TRIAL-02と同一方式。M3.Lがkpg04のCap/台帳に差し替え済み)
    "N5d": lambda c: run_N(c, gen="g5", ver="v5", check="all", tag="N5d", chk_model=DS_PRO),      # 全候補をdeepseek-v4-proで検査(sol全件N5より低単価。HARD6でflag限定では拾えなかった訳の語義ずれを拾えるかの確認)
}


# ============ 検証ケース(probe)実行: 選定(SEL)を省き、一般化->検証(->検査)だけを短文で測る。M7: 7件ずつ分割して呼出 ============
PROBE_BATCH = 7
PROBE_CFG = {"P0": dict(gen="g4", ver="old", check="none"),                       # 基線(N1a相当: 理由なし・旧VER)
             "P0i": dict(gen="g4", ver="old", check="none", inject=True),         # E1L再現: 誤った塊の理由を注入した版(GEN・VERに理由を渡す)。注入対象probeのみ
             "P1": dict(gen="g4", ver="v5", check="none"), "P2": dict(gen="g5", ver="v5", check="none"),
             "P4": dict(gen="g5", ver="v5", check="flagged"), "P5": dict(gen="g5", ver="v5", check="all"),
             "P4d": dict(gen="g5", ver="v5", check="flagged", chk_model=DS_PRO)}


def _batches(xs, n):
    return [xs[i:i + n] for i in range(0, len(xs), n)]


def run_probe(cfg_name, probes):
    cfg = PROBE_CFG[cfg_name]
    if cfg.get("inject"):
        probes = [p for p in probes if p.get("wrong_reason_ja")]
    out, log = [], {"stages": [], "tag": cfg_name, "batches": [], "flags_v1_hash": FLAGS_V1_HASH}
    for bi, pb in enumerate(_batches(probes, PROBE_BATCH), 1):
        text = "\n\n".join(f"[{p['id']}] {p['context']}" for p in pb)
        case = {"id": f"probes{bi}", "text": text}
        lg = {"stages": [], "tag": f"{cfg_name}.{bi}"}
        cands = [dict(span=p["span"], sentence=p["sentence"], chunk_type="phrasal_verb", chunk_reason_ja=(p.get("wrong_reason_ja") or "") if cfg.get("inject") else "",
                      cls="C", difficulty="upper_intermediate", keep=True, probe_id=p["id"]) for p in pb]
        if cfg["gen"] == "g4":
            items = M3.generalize(case, cands, lg, m_gen=LUNA, eff_gen=None, tag=f"{cfg_name}.{bi}", with_chunk=bool(cfg.get("inject")))
        else:
            items = generalize5(case, cands, lg, tag=f"{cfg_name}.{bi}")
        final = verify_old(case, items, lg, tag=f"{cfg_name}.{bi}", strip_reason=not cfg.get("inject")) if cfg["ver"] == "old" else verify5(case, items, lg, tag=f"{cfg_name}.{bi}")
        final = run_check(case, final, lg, tag=f"{cfg_name}.{bi}", scope=cfg["check"], model=cfg.get("chk_model"))
        for c in final:
            d = pack(c); d["probe_id"] = c.get("probe_id"); out.append(d)
        got = {c.get("probe_id") for c in final}
        lg["missing_probe_ids"] = [p["id"] for p in pb if p["id"] not in got]
        log["stages"] += lg["stages"]
        log["batches"].append({k: v for k, v in lg.items() if k != "stages"})
    log["retries"] = list(L.RETRY_LOG)
    return {"items": out, "log": log, "cfg": cfg_name}


def _same_form(a, b):
    return " ".join(_strip_trail(_norm_hw(a))) == " ".join(_strip_trail(_norm_hw(b)))


def score_probe(item, probe):
    """決定論採点(形): PASS(許容形) / FAIL(既知のNG形) / KEPT(本文の形へ戻した/未一般化。意味は安全側だが一般化なし) / REVIEW(どれでもない=Sonnet実読)。"""
    f = " ".join(_norm_hw(item["display_form"]))
    ok = {" ".join(_norm_hw(x)) for x in probe.get("ok", [])}
    ng = {" ".join(_norm_hw(x)) for x in probe.get("ng", [])}
    if f in ng:
        return "FAIL"
    if f in ok:
        return "PASS"
    toks = item.get("tokens") or []
    if item.get("reverted") or (toks and all(t[1] == "CORE" for t in toks)):       # 本文の形へ戻した/全トークンCORE(=一般化なし。活用の原形化のみ)
        return "KEPT"
    return "REVIEW"


def score_gloss(item, probe):
    """M5: 訳の決定論採点(事前登録キーワード)。GOK=正しい語義のキーワードを含み、誤語義キーワードを含まない / GNG=誤語義キーワードを含む / GREV=どちらでもない(Sonnet実読)。"""
    g = item.get("gloss_ja") or ""
    bad = probe.get("gloss_bad_kw") or []
    good = probe.get("gloss_ok_kw") or []
    if any(re.search(k, g) for k in bad):
        return "GNG"
    mw = probe.get("mod_word")
    if mw and mw not in " ".join(_norm_hw(item.get("display_form", ""))).split() and any(re.search(k, g) for k in (probe.get("gloss_mod_kw") or [])):
        return "GNG"      # 削った修飾語の意味が訳に残っている(一般形と訳が対応しない)
    if good and any(re.search(k, g) for k in good):
        return "GOK"
    return "GREV"


def probe_verdict(item, probe):
    """形と訳を合わせた最終判定。FAIL(形NG or 訳NG) / PASS(形PASS and 訳GOK) / KEPT(形KEPT and 訳GOK/GREV除く) / REVIEW。"""
    f, g = score_probe(item, probe), score_gloss(item, probe)
    if f == "FAIL" or g == "GNG":
        return "FAIL"
    if f == "PASS" and g == "GOK":
        return "PASS"
    if f == "KEPT" and g == "GOK":
        return "KEPT"
    return "REVIEW"
