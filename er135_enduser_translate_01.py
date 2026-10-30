# ============================================================
# er135_enduser_translate_01.py
# ENDUSER-EN-JA-LINKED-HIGHLIGHT-01 委任_03T(2026-10-30)
# End Userページの英日連動ハイライト用: 日本語訳が存在しないパート(Z story / Adv Preview・Comment・In One Line / Std In One Line)の
# 日本語訳を文ID付きで新規生成する standalone module。**未配線**(er135_enduser_page_01.py等から呼ばれない。統合は委任_03)。
# 新規生成経路である(既存KP引用用 er003_kp_source_sentence_ja_01 のPrompt(MAX_SENTENCES=5・文脈なし)は流用しない)。
# 流用するのは構造Gate check_ja とパターン定数(import)のみ。
# 設計(Fable判断 M1〜M7): 意味検証必須(数値=決定論 + 対訳照合=LLM 1 call/part)/文脈付き番号付きID出力・件数ID検査→retry1回→fail-closed/
#   fail-closed粒度=段落/生成訳は公開dir内 ja_generated.json に保存し再利用(鍵=英語文sha、Prompt sha・modelは鍵に含めない、失敗は非キャッシュ)/
#   ja_source="generated"(承認済み原稿と区別)。Std日本語に英語は新設しない(本moduleは英語→日本語のみ)。
# LLM呼出は注入(llm(kind, prompt)->str)。本委任ではmockのみ(API 0)。
# ============================================================
from __future__ import annotations

import hashlib
import json
import math
import os
import re
import time
import unicodedata

import er003_kp_source_sentence_ja_01 as kpja
import er006_model_routing_contract_01 as routing

MANAGEMENT_ID = "ENDUSER-EN-JA-LINKED-HIGHLIGHT-01"
TRANSLATE_PROCESS = "ENDUSER_JA_TRANSLATE"
VERIFY_PROCESS = "ENDUSER_JA_VERIFY"
MODEL = routing.SUPPORT_MODEL
JA_SOURCE = "generated"
SCHEMA_VERSION = "enduser_ja_generated_v1"
GENERATED_FILENAME = "ja_generated.json"
MAX_TRANSLATE_ATTEMPTS = 2   # 初回 + retry1回(上限厳守)
MAX_VERIFY_ATTEMPTS = 2
MAX_VERIFY_ROUNDS = 2   # 対訳照合NG段落は、指摘付きで再翻訳→再照合を1回だけ(初回+1回。上限厳守)
COS_MIN_DEFAULT = 0.3

TRANSLATE_HEAD = """あなたは英日翻訳者です。英語学習者(日本語話者)が読むページに載せるため、英語の文章を日本語に訳してください。
英語と日本語を並べて表示し、1文ずつ対応づけるため、下の「訳す英文」の番号ごとに、その1文だけの訳を書いてください。

# 訳し方
- 意味を正確に訳す。意味を変えず、情報の追加・省略をしない。平易で読みやすい自然な日本語にする。
- 番号1つにつき訳は1つ。複数の番号を1つにまとめない。1つの番号の英文を複数の番号に分けない。
- 数字・数量・固有名(人名・地名・作品名)は原文どおりに保つ。数字を言い換えたり変えたりしない。
- 引用符の中の台詞は、台詞として自然に訳す(「」で囲んでよい)。文が引用符をまたいで途中で終わる断片も、その断片だけを訳す。
- 「文脈」は理解のための参考であり、訳さない。解説・注釈・前置きは書かない。

"""
TRANSLATE_CONTEXT_LABEL = "# 文脈(訳さない。同じパートの他の文)\n"
TRANSLATE_TARGET_LABEL = "# 訳す英文\n"
TRANSLATE_BODY = """
# 出力形式
JSONのみ(前後に文章やコードブロックを付けない)。「訳す英文」の番号をそのまま使う。
{"translations": [{"id": 1, "ja": "(1番の英文の日本語訳)"}, {"id": 2, "ja": "..."}]}
"""
VERIFY_HEAD = """あなたは英日対訳の校閲者です。下の番号付き対訳(英文と日本語訳)を1組ずつ確認し、日本語訳が英文の意味を正しく伝えているか判定してください。

# 判定する誤り(これらがあれば ok=false)
- 意味の反転・取り違え(肯定/否定、主語と目的語、時制や条件の逆転など)
- 数値・数量・順序の違い
- 固有名(人名・地名・作品名)の違い・取り違え
- 英文にある情報の欠落、英文にない情報の追加
言い回しの自然さ・文体の好みだけを理由に ok=false にしない。

# 対訳
"""
VERIFY_BODY = """
# 出力形式
JSONのみ(前後に文章やコードブロックを付けない)。すべての番号について1つずつ書く。ok=falseの場合のみissueに短い理由を書く。
{"results": [{"id": 1, "ok": true}, {"id": 2, "ok": false, "issue": "否定が抜けている"}]}
"""
PROMPT_TEMPLATE_SHA256 = hashlib.sha256(
    "␟".join([TRANSLATE_HEAD, TRANSLATE_CONTEXT_LABEL, TRANSLATE_TARGET_LABEL, TRANSLATE_BODY, VERIFY_HEAD, VERIFY_BODY]).encode("utf-8")).hexdigest()

_CJK_RE = kpja._CJK_RE
_CTRL_RE = kpja._CTRL_RE


class EnduserTranslateError(RuntimeError):
    pass


class ModelContractError(EnduserTranslateError):
    pass


# ------------------------------------------------------------
# 入力
# ------------------------------------------------------------
def _clean_sentences(sentences: list) -> list:
    if not isinstance(sentences, (list, tuple)) or not sentences:
        raise ValueError("sentencesが空です")
    out, seen = [], set()
    for s in sentences:
        sid, en = s.get("sid"), s.get("en")
        if not isinstance(sid, str) or not sid or sid in seen:
            raise ValueError(f"sidが不正/重複: {sid!r}")
        if not isinstance(en, str) or not en.strip():
            raise ValueError(f"空の英文: sid={sid}")
        if _CJK_RE.search(en):
            raise ValueError(f"日本語(CJK)を含む英文は翻訳対象にできません: sid={sid}")
        if _CTRL_RE.search(en):
            raise ValueError(f"改行・制御文字を含む英文: sid={sid}")
        seen.add(sid)
        out.append({"sid": sid, "en": en.strip(), "para": s.get("para", 0)})
    return out


def _paragraphs(sents: list) -> list:
    """連続する同一paraを1段落にまとめる(順序保持)。"""
    paras, last = [], object()
    for s in sents:
        if s["para"] != last:
            paras.append([])
            last = s["para"]
        paras[-1].append(s)
    return paras


def para_key(para: list) -> str:
    """キャッシュ鍵=段落の英語文群のsha256(NFKC・空白正規化)。Prompt sha・modelは含めない(M5)。"""
    norm = [re.sub(r"\s+", " ", unicodedata.normalize("NFKC", s["en"])).strip() for s in para]
    return hashlib.sha256(json.dumps(norm, ensure_ascii=False).encode("utf-8")).hexdigest()


# ------------------------------------------------------------
# 数値の決定論照合(three<->3<->三・序数・単位)
# ------------------------------------------------------------
_UNITS = {"zero": 0, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
          "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17,
          "eighteen": 18, "nineteen": 19}
_ONE = {"one": 1}   # "one"は代名詞用法が多い(no one / one of)ので単独では数えない(複合語の中でのみ使用)
_TENS = {"twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90}
_SCALES = {"hundred": 100, "thousand": 1000, "million": 1000000, "billion": 1000000000}
_ORD = {"third": 3, "fourth": 4, "fifth": 5, "sixth": 6, "seventh": 7, "eighth": 8, "ninth": 9, "tenth": 10,
        "eleventh": 11, "twelfth": 12, "twentieth": 20, "thirtieth": 30, "fortieth": 40, "fiftieth": 50, "hundredth": 100, "thousandth": 1000}
# JA側にだけ現れうる暗黙の数(both→二, twice→二度 など): ENにあればJA側の余剰として許容
_IMPLIED = {"both": 2, "twice": 2, "couple": 2, "pair": 2, "double": 2, "twin": 2, "twins": 2, "triple": 3, "thrice": 3,
            "trio": 3, "dozen": 12, "dozens": 12, "once": 1, "single": 1, "half": 2, "quarter": 4, "third": 3}
_EN_TOKEN_RE = re.compile(r"[A-Za-z]+(?:-[A-Za-z]+)*|\d[\d,]*(?:\.\d+)?(?:st|nd|rd|th)?|%")
_KDIGIT = {"〇": 0, "零": 0, "一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
_KSMALL = {"十": 10, "百": 100, "千": 1000}
_KBIG = {"万": 10**4, "億": 10**8}
_KRUN_RE = re.compile(r"[〇零一二三四五六七八九十百千万億]+")
_JDIGIT_RE = re.compile(r"\d[\d,]*(?:\.\d+)?")


def _is_numword(w: str) -> bool:
    return all(b in _UNITS or b in _ONE or b in _TENS or b in _SCALES or b in _ORD for b in w.lower().split("-"))


def _words_to_numbers(run: list) -> list:
    """連続する数詞語の列を値に(twenty-one, two hundred, three thousand five hundred 等)。"""
    atoms = []
    for w in run:
        for p in w.lower().split("-"):
            if p in _UNITS:
                atoms.append(("u", _UNITS[p]))
            elif p in _ONE:
                atoms.append(("one", 1))
            elif p in _TENS:
                atoms.append(("t", _TENS[p]))
            elif p in _SCALES:
                atoms.append(("s", _SCALES[p]))
            elif p in _ORD:
                atoms.append(("o", _ORD[p]))
    vals = []
    st = {"total": 0, "cur": 0, "cnt": 0, "only_one": True}

    def close():
        if st["cnt"] and not (st["only_one"] and st["cnt"] == 1):
            vals.append(st["total"] + st["cur"])
        st.update(total=0, cur=0, cnt=0, only_one=True)
    for k, v in atoms:
        if k == "o":
            close()
            vals.append(v)
            continue
        st["cnt"] += 1
        if k != "one":
            st["only_one"] = False
        if k in ("u", "t", "one"):
            st["cur"] += v
        else:   # scale
            st["cur"] = (st["cur"] or 1) * v
            if v >= 1000:
                st["total"] += st["cur"]
                st["cur"] = 0
    close()
    return vals


def en_numbers(en: str) -> set:
    t = unicodedata.normalize("NFKC", en)
    vals, run = set(), []
    for tok in _EN_TOKEN_RE.findall(t) + ["%"]:   # 末尾のダミーで最後のrunをflush
        if tok[0].isalpha() and _is_numword(tok):
            run.append(tok)
            continue
        if run:
            vals.update(_words_to_numbers(run))
            run = []
        if tok[0].isdigit():
            core = re.sub(r"(st|nd|rd|th)$", "", tok).replace(",", "")
            try:
                f = float(core)
                vals.add(int(f) if f == int(f) else f)
            except ValueError:
                pass
    return vals


def _kanji_run_value(run: str) -> int:
    if all(c in _KDIGIT for c in run):   # 位取り表記(二〇二四)
        return int("".join(str(_KDIGIT[c]) for c in run))
    total, section, num = 0, 0, None
    for c in run:
        if c in _KDIGIT:
            num = _KDIGIT[c]
        elif c in _KSMALL:
            section += (1 if num is None else num) * _KSMALL[c]
            num = None
        elif c in _KBIG:
            section += num or 0
            total += (section or 1) * _KBIG[c]
            section, num = 0, None
    return total + section + (num or 0)


_JMIXED_RE = re.compile(r"((?:\d[\d,]*(?:\.\d+)?[万億千百十])+)(\d[\d,]*)?")
_JPAIR_RE = re.compile(r"(\d[\d,]*(?:\.\d+)?)([万億千百十])")


def ja_numbers(ja: str) -> set:
    t = unicodedata.normalize("NFKC", ja)
    vals = set()

    def add(f):
        vals.add(int(f) if f == int(f) else f)
    # 「3万」「8千」「3万5千」など数字+位(各項と合計)。消費した部分はあとの単独数字/漢数字走査から除く
    for m in _JMIXED_RE.finditer(t):
        total = 0   # 複合(3万5千)は合計だけを数とする(構成要素は数えない)
        for pm in _JPAIR_RE.finditer(m.group(1)):
            total += float(pm.group(1).replace(",", "")) * {**_KBIG, **_KSMALL}[pm.group(2)]
        if m.group(2):
            total += float(m.group(2).replace(",", ""))
        add(total)
    t = _JMIXED_RE.sub(" ", t)
    for m in _JDIGIT_RE.finditer(t):
        try:
            add(float(m.group(0).replace(",", "")))
        except ValueError:
            continue
    for m in _KRUN_RE.finditer(_JDIGIT_RE.sub(" ", t)):
        vals.add(_kanji_run_value(m.group(0)))   # 「三日月」の三のような余剰も数える(保守側=fail-closed)
    return vals


def check_numbers(en: str, ja: str) -> None:
    """数値の決定論照合。ENの数は全てJAに存在し、JA側の余剰数(1を除く)はENの数かENの暗黙数語(both等)に由来すること。"""
    e, j = en_numbers(en), ja_numbers(ja)
    implied = {v for w, v in _IMPLIED.items() if re.search(rf"\b{w}\b", en, re.I)}
    missing = sorted(x for x in e if x not in j)
    extra = sorted(x for x in j if x not in e and x != 1 and x not in implied)
    if missing or extra:
        raise ValueError(f"数値不一致: 英文の数{sorted(e)} / 日本語の数{sorted(j)} (欠落{missing}・余剰{extra})")


# ------------------------------------------------------------
# 構造検査(既存check_jaを流用。ごく短い英文は最小長/かな必須を緩和)
# ------------------------------------------------------------
_SHORT_EN_WORDS = 3


def _terminals_ja(s: str) -> int:
    depth, n = 0, 0
    for c in s:
        if c in "「『（(":
            depth += 1
        elif c in "」』）)":
            depth = max(0, depth - 1)
        elif c in "。！？!?" and depth == 0:
            n += 1
    return n


def _terminals_en(s: str) -> int:
    return len(re.findall(r"[.!?]+(?=[\"'”’)\s]|$)", s))


def structure_check(ja: str, en: str) -> None:
    """既存構造Gate check_ja + 結合の疑い検査。短い台詞("Run!"→「走れ!」)はcheck_jaの最小長4字/かな必須を緩和する。"""
    if len(en.split()) <= _SHORT_EN_WORDS:
        if not isinstance(ja, str) or not ja.strip():
            raise ValueError("空の訳")
        j = ja.strip()
        if _CTRL_RE.search(j):
            raise ValueError("訳に改行・制御文字が含まれます")
        if not _CJK_RE.search(j):
            raise ValueError(f"日本語の訳になっていません: {j[:30]!r}")
        if kpja._norm_match(j) == kpja._norm_match(en):
            raise ValueError("訳が英文と同一です")
        if kpja.PAGE_FORBIDDEN_RE.search(j):
            raise ValueError("訳がページ禁止パターンに該当")
    else:
        kpja.check_ja(ja, en)
    if _terminals_ja(ja.strip()) > _terminals_en(en) + 1:
        raise ValueError(f"文の結合の疑い(日本語の文末{_terminals_ja(ja.strip())}・英文の文末{_terminals_en(en)})")


# ------------------------------------------------------------
# Prompt / parse
# ------------------------------------------------------------
RETRY_NOTE_LABEL = "# 前回の訳への指摘(同じ誤りを繰り返さない。retry時のみ付く)\n"
RETRY_NOTE_VERIFY_HINT = ("対訳照合で不合格(指摘: {issue})。英文の語に対応する語だけで訳し、英文にない情報(材質・種類・服装・場所などの具体化)を足さない。"
                          "英文にある情報を落とさない。")
RETRY_NOTE_NUMBER_HINT = ("英文にない数字・数詞を訳に入れない(英文の they/them は「二人」のような人数にせず「彼ら」と訳す。"
                          "never ... again は「二度と」でなく「もう決して…ない」のように数を含まない表現にする)")


def build_translate_prompt(targets: list, context: list, notes: dict | None = None) -> str:
    """notes={targets内の0始まりindex: 指摘文}はretry時のみ(初回のPromptは従来と同一)。"""
    ctx = ""
    if context:
        ctx = TRANSLATE_CONTEXT_LABEL + "\n".join(f"- {s['en']}" for s in context) + "\n\n"
    nt = ""
    if notes:
        nt = "\n" + RETRY_NOTE_LABEL + "\n".join(f"- {i + 1}番: {m}" for i, m in sorted(notes.items())) + "\n"
    return TRANSLATE_HEAD + ctx + TRANSLATE_TARGET_LABEL + "\n".join(f"{i}. {s['en']}" for i, s in enumerate(targets, 1)) + "\n" + nt + TRANSLATE_BODY


def build_verify_prompt(pairs: list) -> str:
    return VERIFY_HEAD + "\n".join(f"{i}. EN: {en}\n   JA: {ja}" for i, (en, ja) in enumerate(pairs, 1)) + "\n" + VERIFY_BODY


def _strip_fence(text: str) -> str:
    t = (text or "").strip()
    m = re.match(r"^```(?:json)?\s*(.*?)\s*```$", t, re.S)
    return m.group(1) if m else t


def parse_response(text: str, targets: list) -> list:
    """件数・ID(1..n順)の一致、空、重複(結合/分割の兆候)を検査し、日本語訳のlistを返す。失敗はValueError。"""
    if not text or not text.strip():
        raise ValueError("空の応答")
    try:
        d = json.loads(_strip_fence(text))
    except ValueError as e:
        raise ValueError(f"JSONとして読めません: {e}") from e
    tr = d.get("translations") if isinstance(d, dict) else None
    if not isinstance(tr, list):
        raise ValueError("translations配列がありません")
    n = len(targets)
    if len(tr) != n:
        raise ValueError(f"件数が不一致(期待{n}/実際{len(tr)}): 文の結合または分割の疑い")
    ids = []
    for e in tr:
        if not isinstance(e, dict) or not isinstance(e.get("id"), int) or isinstance(e.get("id"), bool):
            raise ValueError(f"idが整数ではありません: {str(e)[:80]}")
        ids.append(e["id"])
    if ids != list(range(1, n + 1)):
        raise ValueError(f"idが1..{n}の順に一致しません: {ids}")
    out = []
    for e in tr:
        ja = e.get("ja")
        if not isinstance(ja, str) or not ja.strip():
            raise ValueError(f"id={e['id']}: 訳が空です")
        out.append(ja.strip())
    dup = [i + 1 for i in range(n) if len(out[i]) >= 4 and out[i] in out[:i]]
    if dup:
        raise ValueError(f"異なる番号に同一の訳があります(結合/分割の疑い): id={dup}")
    return out


def parse_verify(text: str, n: int) -> dict:
    """{id: (ok, issue)}。全idが揃わない/boolでないものはValueError(fail-closed)。"""
    if not text or not text.strip():
        raise ValueError("空の照合応答")
    try:
        d = json.loads(_strip_fence(text))
    except ValueError as e:
        raise ValueError(f"照合応答がJSONとして読めません: {e}") from e
    rs = d.get("results") if isinstance(d, dict) else None
    if not isinstance(rs, list):
        raise ValueError("results配列がありません")
    res = {}
    for e in rs:
        if not isinstance(e, dict) or not isinstance(e.get("id"), int) or not isinstance(e.get("ok"), bool):
            raise ValueError(f"照合resultが不正: {str(e)[:80]}")
        res[e["id"]] = (e["ok"], str(e.get("issue") or ""))
    if sorted(res) != list(range(1, n + 1)):
        raise ValueError(f"照合resultのidが1..{n}に一致しません: {sorted(res)}")
    return res


# ------------------------------------------------------------
# LLM(注入。既定=実API。本委任ではmock)
# ------------------------------------------------------------
class DefaultLLM:
    """実API用(gpt-6-luna、応答modelが期待と違えばModelContractError。fallbackしない)。本委任では使用しない。"""

    def __init__(self, client=None):
        self.client = client
        self.calls = []

    def __call__(self, kind: str, prompt: str) -> str:
        process = TRANSLATE_PROCESS if kind == "translate" else VERIFY_PROCESS
        model = routing.require_model(process, MODEL)
        if self.client is None:
            import er003_v1_b1_scaffold_01_generate as b1s
            self.client = b1s.get_client()
        text, response_model, usage, response_id = kpja._default_call_fn_factory(self.client, model)(prompt)
        self.calls.append({"kind": kind, "response_model": response_model, "usage": usage, "response_id": response_id,
                           "cost_jpy": kpja._cost_jpy(response_model, usage or {})})
        if response_model != model:
            raise ModelContractError(f"応答モデルが不一致(期待{model}/実際{response_model})。fallbackせずSTOP")
        return text


# ------------------------------------------------------------
# キャッシュ / ja_generated.json
# ------------------------------------------------------------
def generated_path(cache_dir) -> str:
    return os.path.join(str(cache_dir), GENERATED_FILENAME)


def load_generated(cache_dir) -> dict:
    p = generated_path(cache_dir)
    if not os.path.exists(p):
        return {"schema": SCHEMA_VERSION, "entries": {}}
    with open(p, encoding="utf-8") as f:
        d = json.load(f)
    if d.get("schema") != SCHEMA_VERSION or not isinstance(d.get("entries"), dict):
        raise EnduserTranslateError(f"{p}: schema不一致/不正(破損した生成訳は読み込まない)")
    return d


def save_generated(cache_dir, doc: dict) -> str:
    os.makedirs(str(cache_dir), exist_ok=True)
    p = generated_path(cache_dir)
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    os.replace(tmp, p)
    return p


def _cached_para(doc: dict, para: list):
    """キャッシュ命中なら訳listを返す。保存値も決定論検査を再実施し、通らなければ無効(=再翻訳)。"""
    ent = doc.get("entries", {}).get(para_key(para))
    if not ent or ent.get("ja_source") != JA_SOURCE or not isinstance(ent.get("ja"), list) or len(ent["ja"]) != len(para):
        return None
    try:
        for s, ja in zip(para, ent["ja"]):
            structure_check(ja, s["en"])
            check_numbers(s["en"], ja)
    except (ValueError, TypeError, AttributeError):
        return None
    return ent["ja"]


def _cos(a, b) -> float:
    na, nb = math.sqrt(sum(x * x for x in a)), math.sqrt(sum(x * x for x in b))
    return 0.0 if not na or not nb else sum(x * y for x, y in zip(a, b)) / (na * nb)


def build_ja_fields(paragraphs: list, ja_by_sid: dict):
    """翻訳結果({sid: 訳|None})から article の `ja`(ENと同数の段落配列。各段落=文の訳を連結)と `ja_align`(1文=1群・how=gen)を作る。
    ja_alignのオフセット(UTF-16 code unit)は連結時に確定する=位置ずれなし・埋め込み0。1文でも訳が無ければ None(部分jaは作らない=全部または無し)。"""
    import er135_enduser_align_01 as AL
    ja_paras, groups, g = [], [], 0
    for pi, pa in enumerate(paragraphs):
        text = ""
        for s in pa:
            t = ja_by_sid.get(s["sid"])
            if not isinstance(t, str) or not t.strip():
                return None
            t = t.strip()
            a = AL.u16_len(text)
            text += t
            groups.append({"g": g, "sids": [s["sid"]], "ja": [pi, a, AL.u16_len(text)], "conf": 1.0, "how": "gen"})
            g += 1
        ja_paras.append(text)
    return ja_paras, groups


# ------------------------------------------------------------
# 公開API
# ------------------------------------------------------------
def translate_part(part_id: str, sentences: list, *, level: str, family: str, cache_dir, llm=None,
                   embed_fn=None, cos_min: float = COS_MIN_DEFAULT, now_fn=None) -> dict:
    """sentences=[{sid,en[,para]}] → {"ja": {sid: 訳|None}, "coverage": {...}, "meta": {...}}。
    fail-closed粒度=段落(para。未指定は全体で1段落)。訳せなかった段落の全文はNone(呼出側は英語のみで表示)。
    llm(kind, prompt)->str は注入。embed_fn(list[str])->list[vector] は任意補助(cos<cos_minで当該段落をNG)。"""
    sents = _clean_sentences(sentences)
    paras = _paragraphs(sents)
    doc = load_generated(cache_dir)
    if llm is None:
        llm = DefaultLLM()
    now = (now_fn or (lambda: time.strftime("%Y-%m-%dT%H:%M:%S%z")))()
    result, failures, hits = {}, {}, 0
    for pi, p in enumerate(paras):
        c = _cached_para(doc, p)
        if c is not None:
            result[pi] = c
            hits += 1
    calls = {"translate": 0, "verify": 0}
    pending = [pi for pi in range(len(paras)) if pi not in result]
    fresh = {}   # 照合前の訳

    notes_by_sid = {}   # retry時のみ: 前回のlocal_check/対訳照合不合格の文 -> 指摘(同じ誤りの反復を避ける)
    for _vround in range(MAX_VERIFY_ROUNDS):
        verify_retry = []
        # --- 翻訳(初回+retry1回。件数/ID不一致=pending全体、個別NG=その段落のみretry) ---
        for _attempt in range(MAX_TRANSLATE_ATTEMPTS if _vround == 0 else 1):
            if not pending:
                break
            targets = [s for pi in pending for s in paras[pi]]
            tset = {s["sid"] for s in targets}
            context = [s for s in sents if s["sid"] not in tset]
            calls["translate"] += 1
            notes = {i: notes_by_sid[s["sid"]] for i, s in enumerate(targets) if s["sid"] in notes_by_sid} if (_attempt or _vround) else None
            try:
                ja_list = parse_response(llm("translate", build_translate_prompt(targets, context, notes)), targets)
            except ModelContractError:
                raise
            except ValueError as e:
                for pi in pending:
                    failures[pi] = f"parse: {e}"
                continue
            by_sid = {s["sid"]: j for s, j in zip(targets, ja_list)}
            still = []
            for pi in pending:
                first_err = None
                for s in paras[pi]:   # 段落内の全文を検査する(retryの指摘に不合格の文すべてを載せるため、最初の不合格で止めない)
                    try:
                        structure_check(by_sid[s["sid"]], s["en"])
                        check_numbers(s["en"], by_sid[s["sid"]])
                    except ValueError as e:
                        first_err = first_err or e
                        msg = str(e)
                        notes_by_sid[s["sid"]] = (RETRY_NOTE_NUMBER_HINT if msg.startswith("数値不一致") else msg) + f"(前回の訳: {by_sid[s['sid']]})"
                if first_err is None:
                    fresh[pi] = [by_sid[s["sid"]] for s in paras[pi]]
                    failures.pop(pi, None)
                else:
                    failures[pi] = f"local_check: {first_err}"
                    still.append(pi)
            pending = still

        # --- 対訳照合(1 call/part、新規訳のみ。応答不正は1回retry→全段落fail-closed) ---
        verify_ids = sorted(pi for pi in fresh if pi not in result)
        if verify_ids:
            flat = [(paras[pi][k]["en"], fresh[pi][k]) for pi in verify_ids for k in range(len(paras[pi]))]
            verdict, verr = None, None
            for _attempt in range(MAX_VERIFY_ATTEMPTS):
                calls["verify"] += 1
                try:
                    verdict = parse_verify(llm("verify", build_verify_prompt(flat)), len(flat))
                    break
                except ModelContractError:
                    raise
                except ValueError as e:
                    verr = str(e)
            vecs = None
            if verdict is not None and embed_fn is not None:
                try:
                    vecs = embed_fn([x for pair in flat for x in pair])
                except Exception as e:   # 任意補助の失敗は検証を通したことにしない(fail-closed)
                    verdict, verr = None, f"embed: {e}"
            idx = 0
            for pi in verify_ids:
                bad = None
                for k in range(len(paras[pi])):
                    idx += 1
                    if verdict is None:
                        bad = f"verify_unavailable: {verr}"
                        continue
                    ok, issue = verdict[idx]
                    if not ok:
                        bad = bad or f"verify_ng: sid={paras[pi][k]['sid']} {issue}"
                        notes_by_sid[paras[pi][k]["sid"]] = (RETRY_NOTE_VERIFY_HINT.format(issue=issue) + f"(前回の訳: {fresh[pi][k]})")
                    elif vecs is not None and _cos(vecs[2 * (idx - 1)], vecs[2 * (idx - 1) + 1]) < cos_min:
                        bad = f"embed_cos_low: sid={paras[pi][k]['sid']}"
                if bad:
                    failures[pi] = bad
                    if bad.startswith("verify_ng:") and _vround + 1 < MAX_VERIFY_ROUNDS:
                        verify_retry.append(pi)   # 不合格の指摘付きで同一段落を1回だけ再翻訳→再照合(照合基準は不変)
                else:
                    result[pi] = fresh[pi]
                    doc["entries"][para_key(paras[pi])] = {   # 成功のみ保存(失敗は非キャッシュ)
                        "part_id": part_id, "level": level, "family": family, "sids": [s["sid"] for s in paras[pi]],
                        "ja": fresh[pi], "ja_source": JA_SOURCE, "model": MODEL,
                        "prompt_sha256": PROMPT_TEMPLATE_SHA256, "generated_at": now}

        if not verify_retry:
            break
        pending = sorted(verify_retry)
        for pi in pending:
            fresh.pop(pi, None)

    # --- 保存(このpartの現行段落に無い旧entryは除去=陳腐化した訳を残さない) ---
    live = {para_key(p) for p in paras}
    for k in [k for k, v in doc["entries"].items() if v.get("part_id") == part_id and k not in live]:
        del doc["entries"][k]
    save_generated(cache_dir, doc)

    ja = {}
    for pi, p in enumerate(paras):
        for k, s in enumerate(p):
            ja[s["sid"]] = result[pi][k] if pi in result else None
    n_tr = sum(1 for v in ja.values() if v is not None)
    cost = None
    if getattr(llm, "calls", None):
        cs = [c["cost_jpy"] for c in llm.calls if c.get("cost_jpy") is not None]
        cost = round(sum(cs), 4) if cs else None
    return {
        "ja": ja,
        "coverage": {"sentences": len(ja), "translated": n_tr, "paragraphs": len(paras), "paragraphs_translated": len(result),
                     "ratio": (n_tr / len(ja)) if ja else 0.0, "complete": n_tr == len(ja)},
        "meta": {"part_id": part_id, "level": level, "family": family, "ja_source": JA_SOURCE, "model": MODEL,
                 "prompt_sha256": PROMPT_TEMPLATE_SHA256, "generated_at": now, "cache_hits": hits,
                 "api_calls": dict(calls), "cost_jpy": cost,
                 "failures": [{"paragraph": pi, "sids": [s["sid"] for s in paras[pi]], "reason": r}
                              for pi, r in sorted(failures.items()) if pi not in result]},
    }
