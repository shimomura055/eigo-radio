# -*- coding: utf-8 -*-
"""FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_14: 課題① Std字義訳 — 独立検査(inspect) + flag項目のみ再生成 の DEV/Trial(er112基盤)。
Production file(er003_*/er019_*/runner)は編集しない。importして呼ぶだけ。出力: er112_output/kp_gm_trial_04/ 。費用台帳=paid_calls.jsonl。上限60円(課題②・E2E含む全体)。
サブコマンド: phase0 / phase0-report / strata / ... (追加は下部)
"""
from __future__ import annotations

import argparse, hashlib, json, os, re, sys, threading, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")
OUT = ROOT / "er112_output" / "kp_gm_trial_04"
LEDGER = OUT / "paid_calls.jsonl"
CAP_JPY = 60.0
RD = ROOT / "docs/research/FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01"
STOP_PATHS = [OUT / "STOP", OUT / "STOP_ALL", ROOT / "er026_output/family_z_production_e2e_01/STOP_ALL", RD / "STOP"]

import er112_kp_gm_trial_02 as T      # noqa: E402 (DEV: client/cost_of/LUNA/gloss_call)

_lock = threading.Lock()


def stop():
    return any(p.exists() for p in STOP_PATHS)


def _append(path, rec):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(path), os.O_WRONLY | os.O_APPEND | os.O_CREAT)
    try:
        os.write(fd, (json.dumps(rec, ensure_ascii=False) + chr(10)).encode("utf-8"))
    finally:
        os.close(fd)


def ledger_add(rec):
    with _lock:
        _append(LEDGER, rec)


def total():
    t = 0.0
    if LEDGER.exists():
        for l in LEDGER.read_text(encoding="utf-8").splitlines():
            if l.strip():
                try:
                    t += json.loads(l).get("cost_jpy") or 0
                except ValueError:
                    pass
    return t


def read_jsonl(p):
    out = []
    if Path(p).exists():
        for l in Path(p).read_text(encoding="utf-8").splitlines():
            if l.strip():
                try:
                    out.append(json.loads(l))
                except ValueError:
                    pass
    return out


# ------------------------------------------------------------------ 検査call(OF-D5-03: 出力順 usage -> usage_meaning_en -> gloss_alone_reading_en -> gloss_conveys)
INSPECT_DEVELOPER = "あなたは英語学習教材の独立した検査者です。指定されたJSON形式だけを返します。"
CONVEYS = ["same_meaning", "literal_image_only", "narrower", "broader", "other"]
USAGES = ["literal", "figurative", "term_or_collocation"]
INSPECT_SCHEMA = {"name": "kp_gloss_inspect_trial04", "strict": True, "schema": {"type": "object", "properties": {"items": {"type": "array", "items": {
    "type": "object", "properties": {
        "rank": {"type": "integer"},
        "usage_in_sentence": {"type": "string", "enum": USAGES},
        "usage_meaning_en": {"type": "string"},
        "gloss_alone_reading_en": {"type": "string"},
        "gloss_conveys": {"type": "string", "enum": CONVEYS}},
    "required": ["rank", "usage_in_sentence", "usage_meaning_en", "gloss_alone_reading_en", "gloss_conveys"], "additionalProperties": False}}},
    "required": ["items"], "additionalProperties": False}}

INSPECT_VERSION = os.environ.get("KP04_INSPECT_VERSION", "v1")
INSPECT_EFFORT = os.environ.get("KP04_INSPECT_EFFORT", "medium")
INSPECT_PROMPT_HEAD = (
    "以下の各項目は、日本人成人向け英語学習教材の『Key Phrase』(英語の語句key_phrase)と、その語句が使われた本文中の1文(source_sentence)、"
    "教材に付けた日本語の意味(japanese_gloss)です。japanese_glossが、本文のその文での意味を、日本語だけを読む学習者に正しく伝えているかを、項目ごとに独立に検査してください。"
    "他の項目の出力や並びから推測しないでください。\n\n"
    "各項目で、次の順に必ず出力してください(出力順=考える順です)。\n"
    "1. usage_in_sentence: source_sentenceの中でkey_phraseが表している用法。literal=語の字義どおりの意味(動作・物そのもの)/ "
    "figurative=慣用・比喩(語ごとの字義とは別の意味を表す)/ term_or_collocation=用語・コロケーション・句動詞など(字義から大きく外れない定まった組合せ)。\n"
    "2. usage_meaning_en: source_sentenceの文脈でkey_phraseが表している意味を、平易な英語1文で言い換える。"
    "**key_phraseに含まれる内容語(名詞・動詞・形容詞・副詞)と、その活用形・同じ語源の語を一切使わずに**書く(言い換えにkey_phraseの語を使うと検査が成立しなくなります)。\n"
    "3. gloss_alone_reading_en: **key_phraseとsource_sentenceを見なかったものとして**、japanese_glossの日本語だけを読んだ日本語学習者が受け取る意味を、平易な英語1文で言い換える。"
    "これも、key_phraseの内容語・活用形・同じ語源の語を使わない。日本語として確立した慣用句・比喩(日本語の読者もその比喩の意味で理解する表現)は、その比喩の意味として受け取る。"
    "そうでなく、字義どおりの動作・物の像として受け取られる日本語は、字義どおりの像として受け取る。\n"
    "4. gloss_conveys: 3がusage_meaning_en(2)と同じ意味か。same_meaning=同じ意味 / literal_image_only=japanese_glossが字義の動作・物の像しか伝えず、本文での比喩・慣用の意味を伝えていない / "
    "narrower=意味はずれていないが狭い・弱い / broader=広すぎる・一般的すぎる / other=その他の食い違い。\n\n"
    "【対象項目】\n")

_STOP = set("a an the to of in on at for with by from up out off over down into onto about as and or but not no one's someone's somebody's oneself someone somebody one "
            "my your his her its their our me you him them us it be is are was were been being do does did have has had get gets got".split())


def stems(text: str) -> set:
    out = set()
    for w in re.findall(r"[A-Za-z]+", (text or "").lower().replace("'", "")):
        s = w
        for suf in ("ing", "ed", "es", "s", "ly"):
            if len(s) > len(suf) + 2 and s.endswith(suf):
                s = s[:-len(suf)]
                break
        out.add(s)
    return out


def content_stems(kp: str) -> set:
    return {s for w in re.findall(r"[A-Za-z']+", (kp or "").lower()) if w not in _STOP for s in stems(w)}


def overlap(kp: str, *texts) -> list:
    cs = content_stems(kp)
    got = set()
    for t in texts:
        got |= cs & stems(t)
    return sorted(got)


INSPECT_SCHEMA_V2 = json.loads(json.dumps(INSPECT_SCHEMA))
_p = INSPECT_SCHEMA_V2["schema"]["properties"]["items"]["items"]
_p["properties"] = {"rank": _p["properties"]["rank"], "usage_in_sentence": _p["properties"]["usage_in_sentence"], "usage_meaning_en": _p["properties"]["usage_meaning_en"],
                    "ja_expression_shares_figure": {"type": "string", "enum": ["yes", "no", "not_figurative"]},
                    "gloss_alone_reading_en": _p["properties"]["gloss_alone_reading_en"], "gloss_conveys": _p["properties"]["gloss_conveys"]}
_p["required"] = list(_p["properties"])
INSPECT_SCHEMA_V2["name"] = "kp_gloss_inspect_trial04_v2"
INSPECT_PROMPT_HEAD_V2 = INSPECT_PROMPT_HEAD.replace(
    "3. gloss_alone_reading_en:",
    "3. ja_expression_shares_figure: japanese_glossの日本語表現そのものが、日本語の読者にとって、usage_meaning_enと同じ比喩・慣用の意味を(話題が分かれば)自然に想起させる、"
    "日本語として一般に通じる表現か。yes=日本語でも同じ比喩が成立している(字義の像を介して比喩の意味に自然に届く)/ no=字義の動作・物の像しか想起させず、比喩の意味へは届きにくい(または別の意味に取られやすい)/ "
    "not_figurative=key_phraseが字義どおりの用法・用語で、比喩を問題にしない。\n"
    "4. gloss_alone_reading_en:", 1).replace("4. gloss_conveys:", "5. gloss_conveys:", 1).replace(
    "同じ意味か。same_meaning=同じ意味 /", "同じ意味か(3がyesまたはnot_figurativeで、意味がずれていなければsame_meaning)。same_meaning=同じ意味 /", 1)     .replace("literal_image_only=japanese_glossが字義の動作・物の像しか伝えず、本文での比喩・慣用の意味を伝えていない /",
             "literal_image_only=japanese_glossが字義の動作・物の像しか伝えず、本文での比喩・慣用の意味を伝えていない(3がnoのときだけ選ぶ) /", 1).replace("5. gloss_conveys: 3が", "5. gloss_conveys: 4が", 1)


def build_inspect_message(rows: list) -> str:
    items = [{"rank": i + 1, "key_phrase": r["key_phrase"], "source_sentence": r["source_sentence"], "japanese_gloss": r["gloss"]} for i, r in enumerate(rows)]
    head = INSPECT_PROMPT_HEAD_V2 if INSPECT_VERSION == "v2" else INSPECT_PROMPT_HEAD
    return head + json.dumps(items, ensure_ascii=False, indent=2)


def inspect_call(rows: list, model=None, effort=None):
    model = model or T.LUNA
    effort = effort or INSPECT_EFFORT
    schema = INSPECT_SCHEMA_V2 if INSPECT_VERSION == "v2" else INSPECT_SCHEMA
    msg = build_inspect_message(rows)
    r = T.client().responses.create(model=model, reasoning={"effort": effort}, text={"format": {"type": "json_schema", **schema}},
                                    input=[{"role": "developer", "content": INSPECT_DEVELOPER}, {"role": "user", "content": msg}])
    c, u = T.cost_of(r, model)
    items = json.loads(r.output_text)["items"]
    by = {it["rank"]: it for it in items}
    outs = []
    for i, row in enumerate(rows):
        it = by.get(i + 1)
        if it is None:
            outs.append(None)
            continue
        ov = overlap(row["key_phrase"], it["usage_meaning_en"], it["gloss_alone_reading_en"])
        outs.append(dict(it, overlap=ov, invalid=bool(ov)))
    return outs, c, u


def flag_variants(o: dict) -> dict:
    """同一出力から事後計算する flag 条件(OF-D5-03/追加費用0)。invalid=内容語重なりで検査不成立(flagしない=fail-open)。"""
    if not o:
        return dict(V1=False, V2=False, V1_inv=False, V2_inv=False, V3=False, invalid=None)
    lit = o["gloss_conveys"] == "literal_image_only"
    fig = o["usage_in_sentence"] == "figurative"
    inv = bool(o.get("invalid"))
    return dict(V1=lit and not inv, V2=lit and fig and not inv,      # 検査不成立は非flag
                V1_inv=lit, V2_inv=lit and fig,                       # 検査不成立でもflag(上限比較用)
                V3=(o["gloss_conveys"] in ("literal_image_only", "other") and fig and not inv), invalid=inv)


# ------------------------------------------------------------------ Phase 0: 既存出力(Trial_02/03)で検査器を較正
FABLE_T3_FAIL = [(1, "F"), (5, "D"), (15, "D"), (15, "E"), (23, "B"), (23, "D"), (50, "F")]
FABLE_T3_THIN = [(2, "A"), (13, "E"), (15, "A"), (44, "E"), (54, "A"), (54, "E"), (54, "F")]
LITERAL_NG_T3 = [(5, "D"), (23, "B"), (23, "D")]          # 字義訳NG(draw a line G2/rep2、an unseen clock G0 rep1/rep2)
T2_LITERAL_NG = [("G0", "draw a line", 1), ("G0", "draw a line", 3)]   # Trial_02 G0 「線を引く」×2 (ROOT_CAUSE_03 §B-1 #1,#2)


def phase0_cells():
    """(key_phrase, sent, gloss) -> label dict。T3の360セルのFable全数ラベル + T2 draw a line 9セル(G0/G2/G3 x3rep、Fable合算確定)。"""
    import er112_kp_gm_trial_03 as T3
    A3 = T3.kpall()
    blind = (ROOT / "er112_output/kp_gm_trial_03/fable_blind_std_03.md").read_text(encoding="utf-8").splitlines()
    key_map = json.load(open(ROOT / "er112_output/kp_gm_trial_03/fable_blind_std_03_key.json", encoding="utf-8"))
    rownum = {}
    for ln in blind:
        m = re.match(r"\| (\d+) \| [^|]+ \| ([^|]+) \|", ln)
        if m:
            rownum[int(m.group(1))] = m.group(2).strip()
    res = [r for r in read_jsonl(ROOT / "er112_output/kp_gm_trial_03/results.jsonl") if r.get("kind") == "G"]
    byc = {(r["arm"], r["key"], r["rep"]): r for r in res}

    def cell(num, col):
        k = rownum[num].lower()
        arm, rep = key_map[k][col].split("/")
        return byc[(arm, k, int(rep[3:]))]
    lab_cells = {}   # (arm,key,rep) -> label
    for num, col in FABLE_T3_FAIL:
        r = cell(num, col)
        lab_cells[(r["arm"], r["key"], r["rep"])] = "FAIL"
    for num, col in FABLE_T3_THIN:
        r = cell(num, col)
        lab_cells.setdefault((r["arm"], r["key"], r["rep"]), "THIN")
    lit = set()
    for num, col in LITERAL_NG_T3:
        r = cell(num, col)
        lit.add((r["arm"], r["key"], r["rep"]))
    rows = {}
    for (arm, k, rep), r in byc.items():
        if not r.get("gloss"):
            continue
        kp = A3[k]["key"]
        lab = lab_cells.get((arm, k, rep), "PASS")
        cls = "LITERAL_NG" if (arm, k, rep) in lit else ("OTHER_NG" if lab == "FAIL" else ("THIN" if lab == "THIN" else "PASS"))
        key = (kp, r["sent"], r["gloss"])
        e = rows.setdefault(key, dict(key_phrase=kp, source_sentence=r["sent"], gloss=r["gloss"], cells=[], cls=cls, src="T3"))
        e["cells"].append("T3:%s/%s/rep%d" % (arm, k, rep))
        # 同一文字列で判定が割れる場合は重い方
        order = {"PASS": 0, "THIN": 1, "OTHER_NG": 2, "LITERAL_NG": 3}
        if order[cls] > order[e["cls"]]:
            e["cls"] = cls
    # Trial_02 draw a line (G0/G2/G3 x3rep=9セル、Fable合算「字義 G0 2/5 G2 1/5 G3 0/5」)
    r2 = [r for r in read_jsonl(ROOT / "er112_output/kp_gm_trial_02/results.jsonl") if r.get("kind") == "G" and r["key"] == "draw a line" and r["arm"] in ("G0", "G2", "G3")]
    for r in r2:
        if not r.get("gloss"):
            continue
        key = ("draw a line", r["sent"], r["gloss"])
        cls = "LITERAL_NG" if (r["arm"], "draw a line", r["rep"]) in [(a, k, p) for a, k, p in T2_LITERAL_NG] else "PASS"
        e = rows.setdefault(key, dict(key_phrase="draw a line", source_sentence=r["sent"], gloss=r["gloss"], cells=[], cls=cls, src="T2"))
        e["cells"].append("T2:%s/draw a line/rep%d" % (r["arm"], r["rep"]))
        if cls == "LITERAL_NG":
            e["cls"] = "LITERAL_NG"
    return list(rows.values())


def run_inspect_rows(rows: list, outpath: Path, cap: float, bs: int = 8, workers: int = 4, tag: str = ""):
    done = {(r["key_phrase"], r["source_sentence"], r["gloss"]) for r in read_jsonl(outpath)}
    todo = [r for r in rows if (r["key_phrase"], r["source_sentence"], r["gloss"]) not in done]
    batches = [todo[i:i + bs] for i in range(0, len(todo), bs)]
    print("inspect rows todo", len(todo), "batches", len(batches), flush=True)

    def w(b):
        if stop() or total() >= cap:
            return ("SKIP", len(b))
        outs, c, u = inspect_call(b)
        ledger_add(dict(kind="inspect", tag=tag, n=len(b), usage=u, cost_jpy=round(c, 5), ts=time.strftime("%Y-%m-%dT%H:%M:%S")))
        for row, o in zip(b, outs):
            with _lock:
                _append(outpath, dict(key_phrase=row["key_phrase"], source_sentence=row["source_sentence"], gloss=row["gloss"], cls=row.get("cls"), cells=row.get("cells"), out=o, call_cost_jpy=round(c / len(b), 5)))
        return ("OK", len(b), round(c, 4))
    with ThreadPoolExecutor(workers) as ex:
        for f in as_completed([ex.submit(w, b) for b in batches]):
            print(f.result(), "cum=%.3f" % total(), flush=True)


def cmd_phase0(a):
    rows = phase0_cells()
    import collections
    print("phase0 unique triples", len(rows), collections.Counter(r["cls"] for r in rows))
    p = OUT / "phase0" / ("inspect_%s.jsonl" % a.tag)
    run_inspect_rows(rows, p, a.cap, tag="phase0_" + a.tag)


def phase0_metrics(path):
    rs = read_jsonl(path)
    import collections
    lines = []
    cnt = collections.Counter(r["cls"] for r in rs)
    lines.append("- 入力: 一意(KP,文,gloss) %d件。Fable確定ラベル別: %s" % (len(rs), dict(cnt)))
    n_inv = sum(1 for r in rs if r["out"] and r["out"]["invalid"])
    n_none = sum(1 for r in rs if not r["out"])
    lines.append("- 検査不成立(内容語重なり)=%d件(%.1f%%)、出力欠落=%d" % (n_inv, 100 * n_inv / max(len(rs), 1), n_none))
    cm = collections.Counter((r["cls"], r["out"]["gloss_conveys"]) for r in rs if r["out"])
    lines.append("- gloss_conveys 分布(ラベル別): " + "; ".join("%s/%s=%d" % (k[0], k[1], v) for k, v in sorted(cm.items())))
    um = collections.Counter((r["cls"], r["out"]["usage_in_sentence"]) for r in rs if r["out"])
    lines.append("- usage_in_sentence 分布(ラベル別): " + "; ".join("%s/%s=%d" % (k[0], k[1], v) for k, v in sorted(um.items())))
    lines.append("")
    lines.append("| flag条件 | 字義NG検出(recall) | 他NG(OTHER_NG)flag | 薄(THIN)flag | PASSのflag(偽陽性) | precision(字義NG/flag全体) | flag総数 |")
    lines.append("|---|---|---|---|---|---|---|")
    for v in ("V1", "V2", "V1_inv", "V2_inv", "V3"):
        c = collections.Counter()
        for r in rs:
            f = flag_variants(r["out"])
            if f[v]:
                c[r["cls"]] += 1
        tot = sum(c.values())
        lit = cnt.get("LITERAL_NG", 0)
        lines.append("| %s | %d/%d | %d/%d | %d/%d | %d/%d | %s | %d |" % (v, c["LITERAL_NG"], lit, c["OTHER_NG"], cnt.get("OTHER_NG", 0), c["THIN"], cnt.get("THIN", 0),
                                                                    c["PASS"], cnt.get("PASS", 0), ("%.0f%%" % (100 * c["LITERAL_NG"] / tot)) if tot else "-", tot))
    return "\n".join(lines), rs


def cmd_phase0_report(a):
    p = OUT / "phase0" / ("inspect_%s.jsonl" % a.tag)
    txt, rs = phase0_metrics(p)
    print(txt)
    print()
    for r in rs:
        f = flag_variants(r["out"])
        if r["cls"] != "PASS" or f["V1_inv"] or f["V1"]:
            o = r["out"] or {}
            print("[%s] V1=%s V2=%s inv=%s | %s | %s | %s | usage=%s conveys=%s | U:%s | G:%s | ov=%s" % (
                r["cls"], f["V1"], f["V2"], f["invalid"], r["key_phrase"], r["source_sentence"][:40], r["gloss"], o.get("usage_in_sentence"), o.get("gloss_conveys"),
                (o.get("usage_meaning_en") or "")[:60], (o.get("gloss_alone_reading_en") or "")[:60], o.get("overlap")))


# ================================================================== ① Trial: KP集合・事前層別(出力を見る前に確定。層定義=STRATA_04.md)
F_LAYER = [   # F層: key_phraseの内容語が字義でも文法的に成立する具体語を含み、本文では比喩・慣用として使われる(見出し語と本文だけから判断)
    "add up", "an unseen clock", "behind the curtain", "behind the scenes", "brace yourself for", "carry the load", "catch one's breath", "center stage",
    "draw a line", "fire the starting gun", "give way", "go cold", "go out of one's way", "greener grass", "grow lighter", "in the spotlight",
    "jump to conclusions", "keep someone company", "leap into action", "move in the other direction", "not the same picture", "off the hook", "on paper",
    "on the throne", "play a part", "pump one's fist", "put on hold", "question shaped like a trophy", "reach for someone's wallet", "rise above the other voices",
    "run on", "shine a light on", "shock someone's wallet", "sound no one asked for", "spread through the whole market", "take a sharp turn",
    "take off an ai costume", "take the wheel", "the new normal", "turn on its head", "weak link"]
N_SAMPLE_SEED = 11
N_SAMPLE_SIZE = 20


def all_kps():
    import er112_kp_gm_trial_03 as T3
    A = dict(T.kpset())
    for k, v in T3.kpall().items():
        A.setdefault(k, v)
    return A


def kp_sets():
    import random
    A = all_kps()
    assert len(A) == 115, len(A)
    F = [k for k in F_LAYER]
    assert all(k in A for k in F), [k for k in F if k not in A]
    N = sorted(k for k in A if k not in set(F))
    rnd = random.Random(N_SAMPLE_SEED)
    Ns = sorted(rnd.sample(N, N_SAMPLE_SIZE))
    return A, F, N, Ns


def cmd_strata(a):
    A, F, N, Ns = kp_sets()
    d = dict(note="事前層別(見出し語と本文のみから決定、gloss出力を見る前)。F層=字義読みも文法的に成立する具体語を含む比喩・慣用。N層=コロケーション・用語・句動詞・字義用法。N標本=seed固定で20件。",
             F_layer=F, N_layer_all=N, N_sample=Ns, N_sample_seed=N_SAMPLE_SEED, anchors=["draw a line", "an unseen clock"],
             trial_set=sorted(set(F) | set(Ns)))
    (OUT / "strata_04.json").write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    print("F", len(F), "N", len(N), "N_sample", len(Ns), "trial_set", len(d["trial_set"]))
    print("N_sample:", Ns)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("--tag", default="v1")
    ap.add_argument("--cap", type=float, default=CAP_JPY)
    a = ap.parse_args()
    if a.cmd == "phase0":
        cmd_phase0(a)
    elif a.cmd == "phase0-report":
        cmd_phase0_report(a)
    elif a.cmd == "strata":
        cmd_strata(a)
