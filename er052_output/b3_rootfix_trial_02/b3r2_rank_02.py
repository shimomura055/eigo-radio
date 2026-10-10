# -*- coding: utf-8 -*-
"""B3-FACT-INSTRUCTION-SEPARATION-ROOTFIX-TRIAL-02 Trial module (DEV/Trial only; not Production).
数値ランクの (1) 決定論の表記抽出 (2) 規則に基づく中核/周辺の導出(Lane B注記仕様 3-5 の機械適用)
(3) LLMが出した number_ranks の決定論検証 (4) 決定論のタグ挿入。LLM不使用・API不使用。

委任_03(Phase 2b) v2差分(post-hoc修正。v1=b3r2_rank_01.pyのcentral_bank誤判定を見てからの最小差分。PREREGISTRATION_03.md参照):
 V2-1 単位換算表 canon_unit(): ベーシスポイント/パーセントポイント/%ポイント/ポイント -> 同一単位(pp)、パーセント -> %。
 V2-2 main_numbers(): 単位がベーシスポイントの数値は pp へ換算(25ベーシスポイント -> 0.25)。
 V2-3 _numbers_of(): 「N ベーシスポイント」には N/100 (pp値) も加える(適格判定が 0.25パーセントポイント でも通る)。
 V2-4 unit_of(): canon_unit を通す(概念キー・Storyline表記の紐付けが単位表記ゆれに依存しない)。
 (万/億/兆の桁展開・全角半角 NFKC・桁区切りは v1 で対応済み。変更なし)

委任_02(Phase 2a)での修正(Opusレビュー是正 A1〜A3):
 A1 一致判定に数字境界条件(直前に数字・.・,が無い/直後に数字が無い)。NFKC正規化。
 A2 抽出正規表現に 月のみ日付・日のみ・第N四半期・時刻・合成数(1万5000)・通貨記号前置を追加。
    漢数字(三千人)・「数百」「数千」は数字を含まないため対象外(仕様どおり。annotation_notes相当に記録する対象)。
 A3 仕様3-5-2の代替規則: 台帳に numeric_value 欄が1件も無い場合のみ Fact本文(ID行)の数字で比べる。
    date_or_period 欄が1件も無い場合のみ Fact本文の最初の日付表現で比べる。概念キーに Fact ID と単位を含める(仕様3-3)。
kind(LLM出力)は規則導出では使わない(表記からkindを再導出する)。kindの一致率は報告のみ。
"""
import re, sys, os, unicodedata
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "er052_output", "b3_fact_instruction_separation_trial_01"))
import b3sep_build_01 as B1   # 読み取り再利用(parse_ledger/clean/assemble_D)

HEDGE_PRE = r"(?:約|およそ|ほぼ|最大で|最大|少なくとも|数)?"
HEDGE_POST = r"(?:超|以上|以下|未満|前後|近く)?"
UNIT = r"(?:ベーシスポイント|ポイント|パーセント|％|%|ドル|円|ユーロ|バレル|リットル|万|億|兆|千|件|人|社|倍|機|隻|台|施設|カ国|か国|ヶ国|基|周年|年|カ月|か月|ヶ月|日間|時間|分|週間|週|回|度|位|点|割|歳|本|個|枚|名|店|校|軒|世帯|戸|便|票|カ所|か所|ヶ所|品目|種類|種|冊|部)*"
NUM = r"\d[\d,]*(?:\.\d+)?"
NUM_C = NUM + r"(?:[万億兆]" + NUM + r")*"          # A2: 合成数 1万5000
CUR_PRE = r"[$¥€£]?"
QUARTER = r"(?:\d{4}年)?第\d+四半期"                  # A2
DATE_FULL = r"\d{4}年\d{1,2}月\d{1,2}日(?:(?:午前|午後)?\d{1,2}時(?:\d{1,2}分)?)?"
DATE_YM = r"\d{4}年\d{1,2}月"
DATE_MD = r"\d{1,2}月\d{1,2}日(?:(?:午前|午後)?\d{1,2}時(?:\d{1,2}分)?)?"
MONTH_ONLY = r"\d{1,2}月(?!\d)"                      # A2: 9月
DAY_ONLY = r"\d{1,2}日(?!間|あたり|当たり|につき)"      # A2: 翌14日の「14日」(日間・1日あたりは除く)
TIME = r"(?:午前|午後)?\d{1,2}時(?!間)(?:\d{1,2}分)?|\d{1,2}:\d{2}"   # A2
RANGE = NUM + r"\s*[～〜~\-–]\s*" + NUM
IDENT = r"\d{1,2}:\d{2}-[A-Za-z]{2}-\d+"                    # 事件番号(1:26-cv-08892)は識別子=name_embedded
ISO = r"\d{4}-\d{1,2}-\d{1,2}"                              # 2026-10-08
DATE_RANGE = r"\d{1,2}月\d{1,2}日?\s*[～〜~\-–]\s*(?:\d{1,2}月)?\d{1,2}日"      # 10月27~28日
RATIO = r"\d+対\d+"                                                 # 12対0(票数など)
NAME_EMB = r"[A-Z][A-Za-z]+ " + r"\d{1,4}(?!\d|\.\d|,\d|ドル|円|%|％|万|億|兆|件|人|社|倍|年|月|日|台|機|名|分|時)"   # Fall 2026 / Hyperion 12 (名称の一部の番号)
PERDAY = r"(?P<perday>\d{1,2})(?=日(?:あたり|当たり|につき))"   # 「1日あたり」の1は抽出しない(毎日の意味)
SURF_RE = re.compile("|".join([
    PERDAY, IDENT, NAME_EMB, QUARTER, ISO, DATE_FULL, DATE_RANGE, RATIO, DATE_YM, DATE_MD, MONTH_ONLY, DAY_ONLY, TIME,
    HEDGE_PRE + CUR_PRE + r"(?:" + RANGE + r")" + UNIT + HEDGE_POST,
    r"第" + NUM + r"[回条号章]",
    HEDGE_PRE + CUR_PRE + NUM_C + UNIT + HEDGE_POST,
]))
DEFAULT_KINDS = ("magnitude", "date_time", "range", "year", "ordinal", "name_embedded")
DIGITS = "0123456789"


def nfkc(s):
    return unicodedata.normalize("NFKC", s or "")


def dec(s):
    """10進比較用の正規化(1,500 -> 1500, 4.00 -> 4, 04 -> 4)。"""
    s = s.replace(",", "")
    try:
        f = float(s)
    except ValueError:
        return s
    return str(int(f)) if f == int(f) else repr(f)


# ---------- A1: 数字境界つき一致 ----------
def find_all(norm, s):
    """norm(NFKC済)中の s(NFKC済)の出現位置リスト。数字で始まる表記は直前が数字・'.'・','でないこと、
    数字で終わる表記は直後が数字でなく、'.'/',' + 数字 でもないこと。(1.5%の中の5%、13日の中の3日、2,300件の中の300、5.5の中の5 を除く)"""
    out, start = [], 0
    if not s:
        return out
    while True:
        p = norm.find(s, start)
        if p < 0:
            break
        e = p + len(s)
        ok = True
        if s[0] in DIGITS and p > 0 and (norm[p - 1] in DIGITS or norm[p - 1] in ".,"):
            ok = False
        if ok and s[-1] in DIGITS and e < len(norm):
            c = norm[e]
            if c in DIGITS or (c in ".," and e + 1 < len(norm) and norm[e + 1] in DIGITS):
                ok = False
        if ok:
            out.append(p)
        start = p + 1
    return out


def contains(hay, s):
    return bool(find_all(nfkc(hay), nfkc(s)))


def _compound_value(t):
    """1万5000 -> 15000(合成数の10進値)。合成数でなければ None。"""
    m = re.fullmatch(r"(\d[\d,]*(?:\.\d+)?)([万億兆])(\d[\d,]*(?:\.\d+)?)", t)
    if not m:
        return None
    mult = {"万": 10 ** 4, "億": 10 ** 8, "兆": 10 ** 12}[m.group(2)]
    v = float(m.group(1).replace(",", "")) * mult + float(m.group(3).replace(",", ""))
    return dec(repr(v))


def value_of(t):
    """数値表記の値(万・億・兆の倍率つき。2億5,000万 -> 250000000, 1万5000 -> 15000, 200万 -> 2000000)。数字が無ければ None。"""
    toks = re.findall(r"(\d[\d,]*(?:\.\d+)?)([万億兆]?)", nfkc(t))
    if not toks:
        return None
    mult = {"": 1, "万": 10 ** 4, "億": 10 ** 8, "兆": 10 ** 12}
    v = sum(float(n.replace(",", "")) * mult[m] for n, m in toks)
    return dec(repr(v))


def surface_kind(surf):
    t = nfkc(surf)
    if re.fullmatch(IDENT, t) or re.fullmatch(NAME_EMB, t):
        return "name_embedded"
    if re.fullmatch(ISO, t):
        return "date_time"
    if re.fullmatch(RATIO, t):
        return "magnitude"
    if re.fullmatch(DATE_RANGE, t):
        return "date_time"
    if re.search(r"第\d+四半期", t):
        return "date_time"
    if re.search(r"第\d+[回条号章]", t):
        return "ordinal"
    if re.search(r"\d+月", t) or re.fullmatch(r"(?:午前|午後)?\d{1,2}時(?:\d{1,2}分)?|\d{1,2}:\d{2}|\d{1,2}日", t):
        return "date_time"
    if re.fullmatch(r"\d{4}年", t):
        return "year"
    if re.search(RANGE, t):
        return "range"
    return "magnitude"


def unit_of(surf):
    """単位(ヘッジ語・通貨前置・数字を除いた残り)。概念キー用(仕様3-3: 台帳IDと単位を含める)。"""
    t = nfkc(surf)
    t = re.sub("^" + HEDGE_PRE, "", t)
    t = re.sub(HEDGE_POST + "$", "", t)
    return canon_unit(re.sub(r"[\s$¥€£]|" + NUM, "", t))     # V2-4


def canon_unit(u):
    """V2-1 単位換算表(決定論)。ポイント系(ベーシスポイント・パーセントポイント・%ポイント・ポイント)は同一単位<pp>、パーセントは%。"""
    for a in ("ベーシスポイント", "パーセントポイント", "%ポイント", "ポイント"):
        u = u.replace(a, "\x00")
    u = u.replace("パーセント", "%")
    return u.replace("\x00", "<pp>")


def _bp_to_pp(v):
    """V2-2 ベーシスポイント値 -> パーセントポイント値(10進。25 -> 0.25)。"""
    from decimal import Decimal
    return dec(str(Decimal(v) / 100))


def main_numbers(surf, kind):
    """概念キー用の主数字(主数字=表記末尾の数字列。合成数は値に展開。dateは年/月/日の存在要素、時刻・四半期は別キー)。"""
    t = nfkc(surf)
    if kind == "date_time":
        iso = re.fullmatch(r"(\d{4})-(\d{1,2})-(\d{1,2})", t)
        if iso:
            return ("D", iso.group(1), dec(iso.group(2)), dec(iso.group(3)))
        q = re.search(r"(?:(\d{4})年)?第(\d+)四半期", t)
        if q:
            return ("Q", q.group(1), q.group(2))
        y = re.search(r"(\d{4})年", t); m = re.search(r"(\d{1,2})月", t); d = re.search(r"月(\d{1,2})|(\d{1,2})日", t)
        if y or m or d:
            return ("D", y.group(1) if y else None, dec(m.group(1)) if m else None, dec(d.group(1) or d.group(2)) if d else None)
        tm = re.search(r"(\d{1,2})時(?:(\d{1,2})分)?|(\d{1,2}):(\d{2})", t)
        if tm:
            h = tm.group(1) or tm.group(3); mi = tm.group(2) or tm.group(4)
            return ("T", dec(h), dec(mi) if mi else None)
        return ("D", None, None, None)
    if kind in ("year", "ordinal", "name_embedded"):
        return (kind[0].upper(), tuple(dec(x) for x in re.findall(NUM, t)))
    nums = re.findall(NUM_C, t)
    if kind == "range":
        rr = re.findall(NUM, t)
        return ("R", tuple(dec(x) for x in rr[:2]))
    if not nums:
        return ("M", None)
    # 主数字=表記末尾の数字列(仕様3-5-1)。倍率(万・億・兆)がつく場合は倍率適用後の値(比較は台帳側も同じ展開を使う)
    mu = re.search(r"((?:\d[\d,]*(?:\.\d+)?[万億兆]?)+)(?!.*\d)", t)
    val = value_of(mu.group(1)) if mu else dec(re.findall(NUM, nums[-1])[-1])
    if "ベーシスポイント" in t and val is not None:       # V2-2
        val = _bp_to_pp(val)
    return ("M", val)


def extract_surfaces(text):
    out = []
    for m in SURF_RE.finditer(nfkc(text)):
        if m.group("perday"):
            continue
        s = m.group(0).strip()
        if re.search(r"\d", s):
            out.append(s)
    return out


def _date_expr_first(text):
    """先頭の日付表現 -> (年|None, 月, 日|None) 。ISO形・和文(年月日/年月/月日)。"""
    t = nfkc(text or "")
    cands = []
    for pat, f in ((r"(\d{4})-(\d{1,2})-(\d{1,2})", lambda m: (m.group(1), dec(m.group(2)), dec(m.group(3)))),
                   (r"(\d{4})年(\d{1,2})月(\d{1,2})日", lambda m: (m.group(1), dec(m.group(2)), dec(m.group(3)))),
                   (r"(\d{4})年(\d{1,2})月", lambda m: (m.group(1), dec(m.group(2)), None)),
                   (r"(?<![\d年])(\d{1,2})月(\d{1,2})日", lambda m: (None, dec(m.group(1)), dec(m.group(2))))):
        m = re.search(pat, t)
        if m:
            cands.append((m.start(), f(m)))
    return min(cands, key=lambda x: x[0])[1] if cands else None


def _numbers_of(text):
    """表記集合(10進)。numeric_scope括弧内は除く。合成数は値も追加。"""
    t = nfkc(text or "")
    t = re.sub(r"\(numeric_scope:[^)]*\)", "", t)
    out = {dec(x) for x in re.findall(NUM, t)}
    for c in re.findall(r"(?:\d[\d,]*(?:\.\d+)?[万億兆]?)+", t):
        v = value_of(c)
        if v:
            out.add(v)
    for c in re.findall(r"(\d[\d,]*(?:\.\d+)?)\s*ベーシスポイント", t):      # V2-3
        out.add(_bp_to_pp(dec(c)))
    return out


def ledger_flags(facts):
    """仕様3-5-2の代替規則の発動条件(台帳全体で欄が1件も無いか)。"""
    return {"has_numeric_value": any(f.get("numeric_value") for f in facts.values()),
            "has_date_or_period": any(f.get("date_or_period") for f in facts.values())}


def eligible(kind, key, fact, lflags=None):
    """適格判定(仕様3-5-2)。lflags の欄が台帳に1件も無い場合のみ、Fact本文(ID行)で代替する。"""
    lflags = lflags or {"has_numeric_value": True, "has_date_or_period": True}
    if kind in ("year", "ordinal", "name_embedded"):
        return False
    if kind == "date_time":
        if key[0] != "D":
            return False
        if lflags["has_date_or_period"]:
            d = _date_expr_first(fact.get("date_or_period"))
        else:
            d = _date_expr_first(B1.clean(fact.get("claim", "")))
        if not d or key[2] is None:
            return False
        y, m, dd = key[1], key[2], key[3]
        if y is not None and (d[0] is None or y != d[0]):
            return False
        if m != d[1]:
            return False
        if dd is not None and (d[2] is None or dd != d[2]):
            return False
        return True
    src = fact.get("numeric_value") if lflags["has_numeric_value"] else B1.clean(fact.get("claim", ""))
    if not src:
        return False
    nums = _numbers_of(src)
    ms = [x for x in (key[1] if key[0] == "R" else (key[1],)) if x is not None]
    return bool(ms) and all(x in nums for x in ms)


def cap_of(n):
    return max(3, min(6, n // 2))


def concept_key(fact_id, kind, key, surf):
    """概念キー(仕様3-3): Fact ID + 種類 + 主数字 + 単位。日付は同一Fact内で包含関係(9月 ⊂ 2026年9月13日)なら同じ概念に束ねる(別関数で後処理)。"""
    if kind == "magnitude" or kind == "range":
        return (fact_id, kind, key, unit_of(surf))
    return (fact_id, kind, key)


def _merge_date_concepts(items):
    """同一Fact内の日付表記で、含まれる側(要素が全て一致して少ない側)を長い表記の概念へ束ねる。"""
    by_fact = {}
    for it in items:
        if it["kind"] == "date_time" and it["key"][0] == "D":
            by_fact.setdefault(it["fact_id"], []).append(it)
    for fid, its in by_fact.items():
        for a in its:
            ka = a["key"]
            for b in its:
                kb = b["key"]
                if a is b or sum(x is not None for x in kb[1:]) <= sum(x is not None for x in ka[1:]):
                    continue
                if all(ka[i] is None or ka[i] == kb[i] for i in (1, 2, 3)):
                    a["ckey"] = b["ckey"]
                    break


def derive_ranks(ledger_text, ordered_ids, storyline, surfaces_by_fact=None, with_story=False, text_by_fact=None):
    """決定論の導出。surfaces_by_fact={fact_id:[surface,...]} を与えればその表記を使う(LLM出力の規則検証用)。
    与えなければ各Fact claimからregexで抽出(D-det腕)。
    戻り値: {"items":[{fact_id,surface,kind,key,role,concept,eligible,ckey}],n_concepts,cap,capped_off}"""
    facts, _ = B1.parse_ledger(ledger_text)
    lf = ledger_flags(facts)
    items = []
    for fid in ordered_ids:
        f = facts[fid]
        srfs = surfaces_by_fact.get(fid, []) if surfaces_by_fact is not None else list(dict.fromkeys(extract_surfaces((text_by_fact or {}).get(fid) or B1.clean(f["claim"]))))
        for s in srfs:
            k = surface_kind(s)
            key = main_numbers(s, k)
            items.append({"fact_id": fid, "surface": s, "kind": k, "key": key, "ckey": concept_key(fid, k, key, s)})
    if with_story:
        # Storylineにだけ現れる表記(要約で表記が変わる等)も印の対象。同じ(種類,主数字)の表記を持つ最初のFactへ紐付け、無ければ未紐付け(_STORY)=中核にしない
        have = {nfkc(it["surface"]) for it in items}
        for s_ in dict.fromkeys(extract_surfaces(storyline or "")):
            if nfkc(s_) in have:
                continue
            k_ = surface_kind(s_)
            key_ = main_numbers(s_, k_)
            m_ = next((it for it in items if it["kind"] == k_ and it["key"] == key_), None)
            fid_ = m_["fact_id"] if m_ else "_STORY"
            items.append({"fact_id": fid_, "surface": s_, "kind": k_, "key": key_, "ckey": concept_key(fid_, k_, key_, s_), "story_only": True})
    _merge_date_concepts(items)
    # 概念(仕様3-3/3-1): 同じ表記(NFKC)は全Factで1概念 / 同じFactで概念キー一致 / 同じFactで一方が他方に(境界つきで)含まれる表記 は1概念に束ねる
    parent = list(range(len(items)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            a_, b_ = items[i], items[j]
            si, sj = nfkc(a_["surface"]), nfkc(b_["surface"])
            same_fact = a_["fact_id"] == b_["fact_id"]
            if si == sj or (same_fact and (a_["ckey"] == b_["ckey"] or contains(si, sj) or contains(sj, si))):
                parent[find(i)] = find(j)
    story = nfkc(storyline or "")
    concepts = {}
    for i, it in enumerate(items):
        r = find(i)
        c = concepts.setdefault(r, {"kind": it["kind"], "elig": False, "in_story": False, "first": i, "name": "|".join(map(str, it["ckey"])), "len": 0})
        if len(nfkc(it["surface"])) > c["len"]:
            c["kind"], c["len"] = it["kind"], len(nfkc(it["surface"]))   # 概念の種類=最も長い表記の種類
        it["_root"] = r
        if eligible(it["kind"], it["key"], facts.get(it["fact_id"], {}), lf):
            c["elig"] = True
        if contains(story, it["surface"]):
            c["in_story"] = True
    counted = [k for k, c in concepts.items() if c["kind"] in ("magnitude", "date_time", "range")]
    cap = cap_of(len(counted))

    def prio(k):
        c = concepts[k]
        if c["kind"] == "date_time":
            return (2, c["first"])
        return (0 if c["in_story"] else 1, c["first"])
    order = sorted([k for k, c in concepts.items() if c["elig"] and c["kind"] in ("magnitude", "range", "date_time")], key=prio)
    core = set(order[:cap])
    capped_off = [concepts[k]["name"] for k in order[cap:]]
    for it in items:
        it["role"] = "core" if it["_root"] in core else "peripheral"
        it["eligible"] = concepts[it["_root"]]["elig"]
        it["concept"] = concepts[it["_root"]]["name"]
        it["ikey"] = "|".join(map(str, it["ckey"]))
    return {"items": items, "n_concepts": len(counted), "cap": cap, "capped_off": capped_off,
            "ledger_flags": lf}


def validate_number_ranks(number_ranks, ledger_text, selected_ids, storyline):
    """LLM出力 number_ranks の決定論検証。戻り値 dict(errors=ハード(技術不整合), flags=報告のみ)。
    errors: 未知fact_id / 選択外fact_id / surfaceが当該Factのclaim・numeric_value・date_or_periodのどれにも(境界つきで)無い / role・kind不正値 / (fact_id,surface)重複。
    flags(報告のみ・技術retry対象外): surfaceがclaimに無くledger欄にのみ有る / claim数字の欠落 / 中核0件 / Storylineの新数字 / 規則導出roleとの不一致。"""
    facts, _ = B1.parse_ledger(ledger_text)
    sel = set(selected_ids)
    errors, flags, seen, by_fact = [], [], set(), {}
    for r in number_ranks or []:
        fid, s, role, kind = r.get("fact_id"), r.get("surface"), r.get("role"), r.get("kind")
        if fid not in facts:
            errors.append(f"UNKNOWN_FACT_ID:{fid}"); continue
        if fid not in sel:
            errors.append(f"FACT_NOT_SELECTED:{fid}"); continue
        if role not in ("core", "peripheral"):
            errors.append(f"BAD_ROLE:{fid}:{role}")
        if kind not in DEFAULT_KINDS:
            errors.append(f"BAD_KIND:{fid}:{kind}")
        f = facts[fid]
        claim = nfkc(B1.clean(f["claim"]))
        hay = nfkc(" ".join([claim, f.get("numeric_value", ""), f.get("date_or_period", "")]))
        if not contains(claim, s):
            if contains(hay, s):
                flags.append(f"SURFACE_ONLY_IN_LEDGER_FIELD_NOT_CLAIM:{fid}:{s}")
            else:
                errors.append(f"SURFACE_NOT_IN_FACT:{fid}:{s}")
        if (fid, nfkc(s)) in seen:
            errors.append(f"DUPLICATE:{fid}:{s}")
        seen.add((fid, nfkc(s)))
        by_fact.setdefault(fid, []).append(s)
    for fid in selected_ids:
        if fid not in facts:
            continue
        got = [nfkc(x) for x in by_fact.get(fid, [])]
        want = set(extract_surfaces(B1.clean(facts[fid]["claim"])))
        miss = sorted(w for w in want if not any(contains(g, w) or contains(w, g) for g in got))
        if miss:
            flags.append(f"MISSING_SURFACES:{fid}:{miss}")
    if number_ranks and not any(r.get("role") == "core" for r in number_ranks):
        flags.append("NO_CORE")
    story_new = [s for s in extract_surfaces(storyline or "")
                 if not any(contains(B1.clean(facts[f]["claim"]), s) or contains(facts[f].get("numeric_value", ""), s)
                            for f in selected_ids if f in facts)]
    if story_new:
        flags.append(f"STORYLINE_NUMBER_NOT_IN_SELECTED_FACTS:{story_new}")
    if not errors and number_ranks:
        der = derive_ranks(ledger_text, [f for f in selected_ids if f in facts], storyline, surfaces_by_fact=by_fact)
        dmap = {(it["fact_id"], nfkc(it["surface"])): it["role"] for it in der["items"]}
        dis = [(r["fact_id"], r["surface"], r["role"], dmap.get((r["fact_id"], nfkc(r["surface"])))) for r in number_ranks
               if dmap.get((r["fact_id"], nfkc(r["surface"]))) != r["role"]]
        if dis:
            flags.append(f"ROLE_DISAGREES_WITH_RULE:{dis}")
    return {"errors": errors, "flags": flags}


MARK = {"core": "【中核数値】", "peripheral": "【周辺数値】"}


def _norm_with_map(text):
    """NFKC正規化文字列と、正規化後index -> 原文index の対応(1文字ずつ正規化するため単調)。"""
    norm, idx = [], []
    for i, ch in enumerate(text):
        n = unicodedata.normalize("NFKC", ch)
        for c in n:
            norm.append(c); idx.append(i)
    return "".join(norm), idx


def insert_marks(text, items):
    """決定論のタグ挿入。items=[{surface,role}]。原文(text)は一切改変せず、表記の末尾へ印だけを足す。
    A1: 数字境界つき一致(1.5%の中の5%には付けない)。長い表記を優先し、すでに印が付いた範囲と重なる出現はスキップ。
    同じ表記が複数itemにあれば、coreが1つでもあればcore(同じ表記は同じ印)。"""
    norm, idx = _norm_with_map(text)
    role_of = {}
    for it in items:
        s = nfkc(it["surface"])
        if s and (role_of.get(s) != "core"):
            role_of[s] = it["role"]
    spans = []
    for s in sorted(role_of, key=lambda x: -len(x)):
        for p in find_all(norm, s):
            a, b = p, p + len(s)
            if not any(a < e and b > st for st, e, _ in spans):
                spans.append((a, b, role_of[s]))
    out, last = [], 0
    for a, b, role in sorted(spans):
        end_orig = idx[b - 1] + 1
        out.append(text[last:end_orig]); out.append(MARK[role]); last = end_orig
    out.append(text[last:])
    return "".join(out)


def strip_marks(text):
    return text.replace(MARK["core"], "").replace(MARK["peripheral"], "")
