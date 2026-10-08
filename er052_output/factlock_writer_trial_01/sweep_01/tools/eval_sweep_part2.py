# -*- coding: utf-8 -*-
"""sweep評価 本評価部(委任_04c)。eval_sweep.py から呼ばれる。規則は eval/EVAL_RULES_V2.md。
サブコマンド: cells | pairwise | facts | blind | rubric | human_check | diversity | style | summary | cost
"""
import glob
import json
import os
import random
import re
import statistics
import sys
from concurrent.futures import ThreadPoolExecutor

import eval_sweep as E

SW, EV = E.SW, E.EV
SEED = 20261008
VIDS_NEW = None


def vids_new():
    return [v["id"] for v in E.variants()["variants"]]


def all_vids():
    return ["S0", "S5"] + vids_new()


def cells():
    """{vid: {"slug/bN": {"dir","text","en","exists"}}} 。S9はR3採否も記録。"""
    out = {}
    for vid in all_vids():
        out[vid] = {}
        for slug, b in E.briefs():
            d = E.art_dir(vid, slug, b)
            t = E.final_text(d) if os.path.isdir(d) else None
            enp = f"{d}/b1b/article.md"
            en = E.clean(E.read(enp)) if os.path.exists(enp) else None
            c = {"dir": d, "text": t, "en": en, "exists": bool(t)}
            r3 = E.jload(f"{d}/sweep_r3.json")
            if r3:
                c["r3_adopted"] = r3.get("adopted")
            out[vid][f"{slug}/b{b}"] = c
    return out


# ---------------- pairwise ----------------
def pairwise(model, only=None):
    C = cells()
    res, forfeit = {}, {}
    pairs, meta = [], []
    for vid in (only or vids_new() + ["S5"]):
        for k, c in C[vid].items():
            s0 = C["S0"][k]
            if not c["text"] or not s0["text"]:
                forfeit.setdefault(vid, []).append(k)
                continue
            pairs.append((f"{vid}|{k}", c["text"], s0["text"]))
    r = E.run_pairs(pairs, f"{EV}/pairwise_{model}.json", model, workers=6)
    for pid, v in r.items():
        vid, k = pid.split("|")
        res.setdefault(vid, {})[k] = v
    if only:  # 部分実行は既存スコアにマージ(他変種を消さない)
        old = E.jload(f"{EV}/pairwise_scores_{model}.json") or {"scores": {}, "forfeit": {}}
        old["scores"].update(res)
        old["forfeit"].update(forfeit)
        res, forfeit = old["scores"], old["forfeit"]
    E.jdump({"model": model, "scores": res, "forfeit": forfeit}, f"{EV}/pairwise_scores_{model}.json")
    n = len(pairs)
    print(model, "pairs", n, "forfeit", {k: len(v) for k, v in forfeit.items()})


def agreement():
    a = E.jload(f"{EV}/pairwise_scores_{E.MAIN_JUDGE}.json")
    b = E.jload(f"{EV}/pairwise_scores_{E.SUB_JUDGE}.json")
    if not b:
        return None
    ma = E.jload(f"{EV}/pairwise_{E.MAIN_JUDGE}.json")
    mb = E.jload(f"{EV}/pairwise_{E.SUB_JUDGE}.json")
    same = tot = 0
    bs_same = bs_tot = 0
    for k in ma:
        if k in mb:
            tot += 1
            same += ma[k]["winner_label"] == mb[k]["winner_label"]
    for vid, d in a["scores"].items():
        for k, v in d.items():
            w = b["scores"].get(vid, {}).get(k)
            if w:
                bs_tot += 1
                bs_same += v["x_score"] == w["x_score"]
    posA = {m: sum(1 for x in M.values() if x["winner_label"] == "A") / max(len(M), 1) for m, M in ((E.MAIN_JUDGE, ma), (E.SUB_JUDGE, mb))}
    posB = {m: sum(1 for x in M.values() if x["winner_label"] == "B") / max(len(M), 1) for m, M in ((E.MAIN_JUDGE, ma), (E.SUB_JUDGE, mb))}
    return {"judgment_agree": f"{same}/{tot}", "brief_score_agree": f"{bs_same}/{bs_tot}", "A_rate": posA, "B_rate": posB}


# ---------------- 数値チェック(決定論) ----------------
KAN = {"〇": 0, "一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
UNITS = "%％円ドルユーロ人年月日割倍万億兆基隻回件か国カ国発機本枚社分秒時間キロメートルバレルトン歳世紀位番目ポイント"
ARABIC = re.compile(r"(?<![0-9A-Za-z])[0-9][0-9,]*(?:\.[0-9]+)?")
KANNUM = re.compile(r"[〇一二三四五六七八九十百千万億兆]+(?=[" + UNITS + r"])")


def kan2int(s):
    total, cur, big = 0, 0, 0
    mult = {"十": 10, "百": 100, "千": 1000}
    bigu = {"万": 10 ** 4, "億": 10 ** 8, "兆": 10 ** 12}
    for ch in s:
        if ch in KAN:
            cur = cur * 10 + KAN[ch] if (len(s) > 1 and not any(c in mult or c in bigu for c in s)) else KAN[ch]
        elif ch in mult:
            total += (cur or 1) * mult[ch]
            cur = 0
        elif ch in bigu:
            big += (total + cur or 1) * bigu[ch]
            total, cur = 0, 0
    return big + total + cur


def numbers_in(text):
    vals = []
    for m in ARABIC.findall(text):
        try:
            vals.append(float(m.replace(",", "")))
        except ValueError:
            pass
    for m in KANNUM.findall(text):
        try:
            vals.append(float(kan2int(m)))
        except Exception:  # noqa: BLE001
            pass
    return vals


def src_numbers(d):
    s = ""
    for p in (f"{d}/storyline_b3/selected_brief.md", f"{d}/research_ledger/verified_fact_ledger.txt"):
        if os.path.exists(p):
            s += E.read(p) + "\n"
    return set(numbers_in(s)), bool(s)


def amp_ii(d):
    out = {}
    for st in ("r0", "r2"):
        j = E.jload(f"{d}/factlock_check_{st}.json")
        if j is None:
            return None
        items = (j.get("ii_untagged") or {}).get("items") or []
        out[st] = sum(1 for i in items if i.get("label") == "new_specific_claim")
    return {"r0": out["r0"], "r2": out["r2"], "amp": out["r2"] - out["r0"]}


def inconsistency_i(d):
    j = E.jload(f"{d}/factlock_check_r2.json")
    if not j:
        return None
    items = (j.get("i_pairs") or {}).get("items") or []
    bad = sum(1 for i in items if i.get("verdict") != "整合")
    return {"bad": bad, "n": len(items)}


def ja_fc(d):
    ev = E.jload(f"{d}/ja_writer/runtime_evidence.json") or {}
    fc = ev.get("fact_checks_summary") or {}
    o = fc.get("original") or {}
    r = fc.get("r2") or {}
    man = E.jload(f"{d}/manifest.json") or {}
    return {"orig_status": o.get("final_status"), "orig_must_fix": bool(o.get("must_fix_applied")),
            "r2_status": r.get("final_status"), "r2_must_fix": bool(r.get("must_fix_applied")),
            "exit_reason": man.get("exit_reason"), "has_manifest": bool(man)}


def facts():
    C = cells()
    out = {}
    for vid in all_vids():
        out[vid] = {}
        for k, c in C[vid].items():
            d = c["dir"]
            rec = {"exists": c["exists"], "r3_adopted": c.get("r3_adopted")}
            if c["exists"]:
                src, ok = src_numbers(d)
                nums = numbers_in(c["text"])
                bad = [n for n in nums if n not in src]
                rec.update(num_total=len(nums), num_bad=len(bad), num_bad_vals=bad, src_ok=ok)
            rec["amp"] = amp_ii(d)
            rec["inc_i"] = inconsistency_i(d)
            rec["ja_fc"] = ja_fc(d)
            out[vid][k] = rec
    E.jdump(out, f"{EV}/facts_deterministic.json")
    print("facts done")


# ---------------- 盲検コピー + 重大候補rubric ----------------
def blind():
    C = cells()
    rnd = random.Random(SEED)
    keys = [(vid, k) for vid in all_vids() for k in C[vid] if C[vid][k]["exists"]]
    rnd.shuffle(keys)
    mp = {}
    for i, (vid, k) in enumerate(keys, 1):
        code = f"X{i:03d}"
        c = C[vid][k]
        slug = k.split("/")[0]
        bd = f"{EV}/blind_sweep/{slug}/{code}"
        os.makedirs(bd, exist_ok=True)
        open(f"{bd}/ja_r2.md", "w", encoding="utf-8").write(c["text"])
        open(f"{bd}/en.md", "w", encoding="utf-8").write(c["en"] or "")
        mp[code] = {"variant": vid, "key": k, "slug": slug, "dir": c["dir"]}
    E.jdump(mp, f"{EV}/_private/MAP_SWEEP.json")
    print("blind", len(mp))


def rubric(model=E.MAIN_JUDGE, workers=4):
    sys.path.insert(0, "er052_output/factlock_writer_trial_01/tools")
    import eval_ta_shared as ev
    mp = E.jload(f"{EV}/_private/MAP_SWEEP.json")
    rub = E.read("docs/pm/b3_trial_01/eval_rubric.md")
    os.makedirs(f"{EV}/rubric", exist_ok=True)

    def one(code):
        out = f"{EV}/rubric/{code}.json"
        if os.path.exists(out):
            return
        m = mp[code]
        bd = f"{EV}/blind_sweep/{m['slug']}/{code}"
        ledger = E.read(f"er052_output/open233_polysemy_trial_02/ledgers/{m['slug']}/control/research_ledger/verified_fact_ledger.txt")
        instr = ev.INSTR + "\n- 今回の軽量判定ではR0は提供しない。in_r0は常にfalseとし、R2とENのみを対象にする。"
        prompt = (f"{instr}\n\n# ルーブリック(重大/軽微の定義節を中心に適用)\n{rub}\n\n# Verified Fact Ledger\n{ledger}\n\n"
                  f"# R0(修正前JA原稿)\n(提供なし)\n\n# R2(JA最終稿)\n{E.read(bd + '/ja_r2.md')}\n\n# EN(英語版)\n{E.read(bd + '/en.md') or '(英語版なし)'}\n")
        p, actual = E.call_json(model, "あなたは厳密で一貫した事実評価者です。", prompt, ev.SCHEMA, "rubric_light", effort="high")
        E.jdump({"code": code, "judge": actual, "parsed": p}, out)

    with ThreadPoolExecutor(max_workers=workers) as ex:
        list(ex.map(one, sorted(mp)))
    print("rubric done", len(mp))


def human_check():
    mp = E.jload(f"{EV}/_private/MAP_SWEEP.json")
    majors, minors = [], {}
    for code, m in sorted(mp.items()):
        r = E.jload(f"{EV}/rubric/{code}.json")
        if not r:
            continue
        for i in r["parsed"]["ng_items"]:
            ja = i["in_r2"]
            en_only = i["in_en"] and not ja
            if i["severity"] == "major":
                majors.append((code, m, i))
            else:
                d = minors.setdefault(m["variant"], {"ja": 0, "en_only": 0})
                d["en_only" if en_only else "ja"] += 1
    L = ["# HUMAN_CHECK_SWEEP: 重大候補(LLM抽出、人間確認待ち)", "",
         "性質: 軽量rubric call(gpt-6-luna、JA R2+EN、1記事1 call)が`major`と判定した全件。**LLM抽出であり確定ではない**。人間確認で true/false を付ける(下の列を埋める)。盲検コード→変種は`eval/_private/MAP_SWEEP.json`。", "",
         f"件数: {len(majors)}件", ""]
    for n, (code, m, i) in enumerate(majors, 1):
        where = "/".join(x for x, f in (("JA R2", i["in_r2"]), ("EN", i["in_en"])) if f) or "不明"
        L += [f"## H{n:02d}. {code} ({m['variant']} {m['key']}) 所在={where}", f"- 該当文: {i['text']}", f"- 種別: {i['kind']} / fact_id: {i['fact_id']}",
              f"- 判定理由: {i['reason']}", f"- 記事: `{m['dir']}/ja_writer/revision2.md`", "- 人間確認: (未)  true重大 / false(誤検出) / 境界", ""]
    open(f"{EV}/HUMAN_CHECK_SWEEP.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    E.jdump({"majors": [(c, m["variant"], m["key"], i) for c, m, i in majors], "minors": minors}, f"{EV}/rubric_collected.json")
    print("majors", len(majors), minors)


# ---------------- 多様性 ----------------
DOMAINS = {
    "舞台": ["舞台", "幕", "配役", "主役", "せりふ", "代役", "劇", "ショー", "衣装", "お色直し", "着替え", "衣替え", "小道具", "脚本", "筋書き", "開演", "開幕", "楽屋", "観客", "登場", "退場"],
    "ゲーム": ["ゲーム", "カード", "札", "駒", "盤", "チェス", "将棋", "囲碁", "サイコロ", "手札", "切り札", "ポーカー", "ババ抜き"],
    "探偵": ["探偵", "手がかり", "犯人", "謎", "事件", "捜査", "推理", "証拠", "ミステリー"],
    "料理": ["料理", "レシピ", "味付け", "煮込", "スパイス", "食材", "隠し味", "調味料", "下ごしらえ", "シェフ", "スープ"],
    "スポーツ": ["試合", "ゴール", "選手", "ボール", "延長戦", "後半戦", "前半戦", "マラソン", "ランナー", "バトン", "キックオフ", "ホイッスル", "審判"],
    "天気": ["天気", "嵐", "台風", "雲", "雷", "霧", "風向き", "天気予報", "晴れ間"],
    "旅": ["旅", "道のり", "地図", "旅路", "行き先", "寄り道", "道案内", "迷路", "分かれ道", "交差点"],
    "医療": ["診断", "処方", "治療", "薬", "カルテ", "症状", "手術", "体温", "脈"],
    "音楽": ["楽譜", "指揮者", "演奏", "交響曲", "リズム", "ハーモニー", "メロディ", "合唱", "不協和音"],
    "建築": ["土台", "柱", "屋根", "基礎", "積み木", "設計図", "足場"],
}
BOILER = {"もし…なら": r"もし.{0,40}なら", "あなたなら": r"あなたなら", "かもしれません": r"かもしれません", "ではありません": r"ではありません|ではない",
          "のではないでしょうか": r"のではないでしょうか", "ということです": r"ということです", "ましょう": r"ましょう", "みなさん": r"みなさん|皆さん",
          "実は": r"実は", "つまり": r"つまり", "さて": r"さて", "いかがでしょうか": r"いかがでしょうか", "のようです": r"のようです|ようですね"}


def body_of(text):
    ls = text.strip().split("\n")
    return ("\n".join(ls[1:]) if len(ls) > 1 else text).replace("\n", "")


def sents(text):
    return [s.strip() for s in re.split(r"(?<=[。！？!?])", body_of(text)) if s.strip()]


def domain_hits(text):
    flat = body_of(text)
    return {d: sum(1 for w in ws if w in flat) for d, ws in DOMAINS.items()}


def open_type(t):
    s = sents(t)
    if not s:
        return "なし"
    f = s[0]
    if "？" in f or "?" in f or f.rstrip("。").endswith("か"):
        return "問い"
    if re.search(r"[0-9]", f):
        return "数字"
    return "断定・描写"


def close_type(t):
    s = sents(t)
    if not s:
        return "なし"
    f = s[-1]
    if "？" in f or "?" in f or f.rstrip("。").endswith("か"):
        return "問い"
    if re.search(r"つまり|まとめ|ということ|大切|ポイント", f):
        return "まとめ"
    return "余韻・その他"


def diversity_mech():
    C = cells()
    out = {}
    for vid in all_vids():
        ts = [c["text"] for c in C[vid].values() if c["text"]]
        rec = {"n": len(ts)}
        if len(ts) < 2:
            out[vid] = rec
            continue
        hits = [domain_hits(t) for t in ts]
        used = [{d for d, n in h.items() if n >= 2} for h in hits]
        rec["domains_common_all"] = sorted(set.intersection(*used)) if used else []
        top = []
        for h in hits:
            m = max(h.values())
            top.append(max(h, key=h.get) if m >= 2 else "なし")
        rec["dominant"] = top
        rec["dominant_same_all"] = len(set(top)) == 1 and top[0] != "なし"
        rec["boiler_common"] = sorted(k for k, pat in BOILER.items() if all(re.search(pat, t) for t in ts))
        rec["open_types"] = [open_type(t) for t in ts]
        rec["close_types"] = [close_type(t) for t in ts]
        rec["open_distinct"] = len(set(rec["open_types"]))
        rec["close_distinct"] = len(set(rec["close_types"]))
        # char bigram jaccard (付録)
        def bg(t):
            f = re.sub(r"\s", "", body_of(t))
            return {f[i:i + 2] for i in range(len(f) - 1)}
        bgs = [bg(t) for t in ts]
        js = [len(a & b) / len(a | b) for i, a in enumerate(bgs) for b in bgs[i + 1:]]
        rec["bigram_jaccard_max"] = round(max(js), 3)
        out[vid] = rec
    E.jdump(out, f"{EV}/diversity_mech.json")
    return out


def diversity_llm():
    C = cells()
    rnd = random.Random(SEED + 1)
    vs = [v for v in all_vids() if sum(1 for c in C[v].values() if c["text"]) >= 2]
    order = vs[:]
    rnd.shuffle(order)
    code = {v: f"G{i + 1:02d}" for i, v in enumerate(order)}
    E.jdump(code, f"{EV}/_private/MAP_DIVERSITY.json")
    blocks = []
    for v in order:
        arts = [c["text"] for c in C[v].values() if c["text"]]
        blocks.append(f"## 組{code[v]}\n" + "\n\n".join(f"### 記事{i + 1}\n{t}" for i, t in enumerate(arts)))
    prompt = ("以下は同じ条件で書かれた日本語ラジオ記事の組です(組ごとに3本、テーマは組の中で別々)。各組について、3本の構成・比喩・導入・結びの"
              "共通点(1パターン化しているか)を、具体的な語や型を挙げて2〜3文で記述してください。組の間を比べて、特に画一的な組と多様な組も挙げてください。\n\n" + "\n\n".join(blocks))
    schema = {"name": "div", "strict": True, "schema": {"type": "object", "additionalProperties": False, "required": ["per_group", "overall"], "properties": {
        "per_group": {"type": "array", "items": {"type": "object", "additionalProperties": False, "required": ["group", "finding"], "properties": {"group": {"type": "string"}, "finding": {"type": "string"}}}},
        "overall": {"type": "string"}}}}
    p, actual = E.call_json(E.MAIN_JUDGE, "あなたは日本語ラジオの編集者です。", prompt, schema, "diversity_llm", effort="medium")
    inv = {v: k for k, v in code.items()}
    E.jdump({"code_to_variant_NOTE": "変種名は評価後に開示", "result": p, "model": actual}, f"{EV}/diversity_llm.json")
    print("diversity llm", len(vs))


# ---------------- 文体 / O2 / O4 ----------------
def style_all():
    import style_metrics as sm
    C = cells()
    per = {}
    for vid in all_vids():
        for k, c in C[vid].items():
            if c["text"]:
                m = sm.metrics(c["text"])
                n = max(m["chars"], 1)
                f = lambda x: round(x / n * 1000, 2)
                per[f"{vid}|{k}"] = {"polite_ratio": m["polite_ratio"], "arabic_per1000": f(m["arabic_numbers"]), "metaphor_distinct_per1000": f(m["metaphor_distinct"]),
                                     "speculation_per1000": f(m["speculation"]), "questions_per1000": f(m["questions"]), "chars": m["chars"]}
    E.jdump(per, f"{EV}/style_normalized.json")
    return per


def o2(per, model=E.MAIN_JUDGE):
    sc = E.jload(f"{EV}/pairwise_scores_{model}.json")
    keys = ["polite_ratio", "arabic_per1000", "metaphor_distinct_per1000", "speculation_per1000", "questions_per1000", "chars"]
    res = {k: {"pos": 0, "neg": 0, "zero": 0} for k in keys}
    npairs = 0
    for vid, d in sc["scores"].items():
        for k, v in d.items():
            if v["x_score"] == 0.5:
                continue
            a, b = per.get(f"{vid}|{k}"), per.get(f"S0|{k}")
            if not a or not b:
                continue
            npairs += 1
            win_is_var = v["x_score"] == 1.0
            for m in keys:
                diff = (a[m] - b[m]) * (1 if win_is_var else -1)  # 勝者-敗者
                res[m]["pos" if diff > 0 else "neg" if diff < 0 else "zero"] += 1
    return {"n_decided_pairs": npairs, "by_metric": res}


def ngram_rate(text, ref, n=8):
    norm = lambda s: re.sub(r"[\s、。，．・「」『』（）()【】！？!?\-ー]", "", s)
    t, r = norm(body_of(text)), norm(ref)
    if len(t) < n:
        return 0.0
    grams = {r[i:i + n] for i in range(len(r) - n + 1)}
    hit = sum(1 for i in range(len(t) - n + 1) if t[i:i + n] in grams)
    return hit / (len(t) - n + 1)


def o4():
    C = cells()
    out = {}
    for vid in all_vids():
        rs = []
        for k, c in C[vid].items():
            if c["text"]:
                slug = k.split("/")[0]
                led = E.read(f"er052_output/open233_polysemy_trial_02/ledgers/{slug}/control/research_ledger/verified_fact_ledger.txt")
                rs.append(ngram_rate(c["text"], led))
        out[vid] = round(statistics.mean(rs), 3) if rs else None
    return out


REASON_CATS = {"比喩・たとえ": r"比喩|たとえ|見立て|舞台|カード|クイズ|探偵|ゲーム", "問い・呼びかけ": r"問い|呼びかけ|問いかけ", "具体的な数字・事実": r"数字|具体|バレル|％|%",
               "流れ・構成": r"流れ|構成|筋|順序|展開|整理", "冒頭・結び": r"冒頭|最後|結び|締め|導入|オチ", "硬い・説明的": r"硬|説明的|注意書き|淡々", "繰り返し・作り込み": r"繰り返|重な|作り込|窮屈|くどい"}


def reason_types():
    ma = E.jload(f"{EV}/pairwise_{E.MAIN_JUDGE}.json")
    out = {}
    for k, v in ma.items():
        vid = k.split("|")[0]
        d = out.setdefault(vid, {"n": 0, **{c: 0 for c in REASON_CATS}})
        d["n"] += 1
        for c, pat in REASON_CATS.items():
            if re.search(pat, v["reason"]):
                d[c] += 1
    return out


def extras(agg, F, per, O4, div):
    L = ["", "## 7. 理由の型分類(主judgeのreasonを事後に機械分類、判定数中の出現数。reasonは勝者側の長所として書かれることが多い)", "",
         "| 変種 | 判定数 | " + " | ".join(REASON_CATS) + " |", "|---|---|" + "---|" * len(REASON_CATS)]
    for vid, d in sorted(reason_types().items(), key=lambda x: (x[0] != "S5", int(x[0][1:]) if x[0] != "S5" else 0)):
        L.append(f"| {vid} | {d['n']} | " + " | ".join(str(d[c]) for c in REASON_CATS) + " |")
    briefs = [f"{s}/b{b}" for s, b in E.briefs()]
    pairs = [("S0", "S1", "タグの副作用"), ("S1", "S2", "R0の1文禁止"), ("S2", "S3", "数値規則(metaは数値なしのため除外)"), ("S3", "S4", "R1/R2の2文制約"),
             ("S4", "S9", "R3回数"), ("S4", "S10", "手段リスト"), ("S3", "S8", "連鎖切り"), ("S4", "S6", "骨格→肉付け(複合)"), ("S4", "S7", "目標形対規則形(複合)"),
             ("S4", "S11", "数値を書かせない(metaは除外)"), ("S5", "S12", "v1+語り口規則")]
    L += ["", "## 8. 軸別の対比(S0基準スコアの差と決定論指標の差。事実の並置であり、変種間の勝敗ではない)", "",
          "S0基準スコアの差=B変種の合計−A変種の合計(両側とも有効briefが同じものだけ)。数値は事実のみ。", "",
          "| 軸 | A→B | スコア差(S0基準) | 数値NG差/本 | 増幅(ii)差/本 | 比喩異なり/1000字差 | 台帳8-gram率差 | 備考 |", "|---|---|---|---|---|---|---|---|"]
    for a, b, name in pairs:
        ks = [k for k in briefs if not (("数値" in name and "meta" in k and ("S2" in a or "S4" in a and b == "S11")))]
        def sc_of(v):
            return {k: agg[v]["scs"][i] for i, k in enumerate(briefs)} if v in agg else {}
        sa, sb = sc_of(a), sc_of(b)
        if a == "S0":
            sa = {k: 0.5 for k in briefs}  # S0対S0は定義上0.5
        use = [k for k in ks if sa.get(k) is not None and sb.get(k) is not None]
        ds = round(sum(sb[k] - sa[k] for k in use), 2) if use else None
        nb = lambda v: [F[v][k]["num_bad"] for k in use if F[v][k]["exists"]]
        am = lambda v: [F[v][k]["amp"]["amp"] for k in use if F[v][k]["exists"] and F[v][k]["amp"]]
        mean = lambda xs: statistics.mean(xs) if xs else None
        d_nb = None if mean(nb(a)) is None or mean(nb(b)) is None else round(mean(nb(b)) - mean(nb(a)), 2)
        d_am = None if mean(am(a)) is None or mean(am(b)) is None else round(mean(am(b)) - mean(am(a)), 2)
        mm = lambda v: [per[f"{v}|{k}"]["metaphor_distinct_per1000"] for k in use if f"{v}|{k}" in per]
        d_m = None if not mm(a) or not mm(b) else round(mean(mm(b)) - mean(mm(a)), 2)
        d_o = None if O4.get(a) is None or O4.get(b) is None else round(O4[b] - O4[a], 3)
        note = f"対象brief={[k.split('/')[0] for k in use]}" + ("; S0基準スコアはS0同士で0.5相当" if a == "S0" else "")
        L.append(f"| {name} | {a}→{b} | {ds} | {d_nb} | {d_am} | {d_m} | {d_o} | {note} |")
    # 同等以上かつ非悪化
    L += ["", "## 9. 「面白さ同等以上、かつ決定論指標が悪化していない」変種の一覧(事実の並べ替え。推奨ではない)", "",
          "条件(事前に固定): 3段階の読みが「同等」または「明確に上」、有効brief=3(不戦敗0)、数値NG/本がS0以下、増幅(ii)/本が0以下。STOPが含まれる変種は注記。", ""]
    ok, ng = [], []
    s0nb = statistics.mean(F["S0"][k]["num_bad"] for k in briefs if F["S0"][k]["exists"])
    for vid, a in agg.items():
        valid = all(s is not None for s in a["scs"])
        fr = F[vid]
        ex = [r for r in fr.values() if r["exists"]]
        nbv = statistics.mean(r["num_bad"] for r in ex) if ex else 99
        ampv = statistics.mean(r["amp"]["amp"] for r in ex if r["amp"]) if any(r["amp"] for r in ex) else 0
        stops = [k for k in briefs if fr[k]["ja_fc"]["exit_reason"] not in (None, "completed")]
        cond = valid and a["label"] in ("同等", "明確に上") and nbv <= s0nb and ampv <= 0
        (ok if cond else ng).append(f"{vid}(合計{a['tot']}, 数値NG{round(nbv,2)}, 増幅{round(ampv,2)}{', STOPあり:'+','.join(k.split('/')[0] for k in stops) if stops else ''})")
    L += ["- 該当: " + "; ".join(ok), "- 非該当: " + "; ".join(ng), ""]
    # 多様性LLM所見(変種開示)
    dl = E.jload(f"{EV}/diversity_llm.json")
    mp = E.jload(f"{EV}/_private/MAP_DIVERSITY.json")
    if dl and mp:
        inv = {v: k for k, v in mp.items()}
        L += ["## 10. 多様性LLM所見(盲検で生成、評価後に変種名を開示。S8・S10は2本のみ)", ""]
        for g in sorted(dl["result"]["per_group"], key=lambda x: int(inv.get(x["group"].replace("組", ""), "S99")[1:])):
            L.append(f"- {inv.get(g['group'].replace('組', ''), g['group'])}: {g['finding']}")
        L += ["- 全体所見: " + dl["result"]["overall"], ""]
    return L


# ---------------- 集計 ----------------
def cost_summary():
    tot = 0.0
    rates = {"gpt-6-luna": (0.10, 0.01, 0.50), "gpt-5.6-luna": (0.20, 0.02, 1.20)}
    by = {}
    for f in glob.glob(f"{EV}/raw_usage_log_eval_sweep*.jsonl"):
        for ln in open(f, encoding="utf-8"):
            r = json.loads(ln)
            if not r.get("success"):
                continue
            pr = rates.get(r["model_id"], rates["gpt-5.6-luna"])
            it, ct, ot = r.get("input_tokens", 0), r.get("cached_input_tokens", 0), r.get("output_tokens", 0)
            c = (max(it - ct, 0) / 1e6 * pr[0] + ct / 1e6 * pr[1] + ot / 1e6 * pr[2]) * 156.88
            tot += c
            by[r["stage"]] = by.get(r["stage"], 0) + c
    return tot, by


def read_label(vid, tot, scs, band, noise_up):
    if len(scs) < 3:
        return "判定不能(有効brief<3)"
    if all(s == 1.0 for s in scs) and tot >= 2.5:
        return "明確に上"
    if all(s == 0.0 for s in scs):
        return "明確に下"
    return "同等"


def summary():
    C = cells()
    F = E.jload(f"{EV}/facts_deterministic.json")
    sc = E.jload(f"{EV}/pairwise_scores_{E.MAIN_JUDGE}.json")
    band = E.jload(f"{EV}/noise_band.json")
    div = diversity_mech()
    per = style_all()
    O2 = o2(per)
    O4 = o4()
    ag = agreement()
    col = E.jload(f"{EV}/rubric_collected.json") or {"majors": [], "minors": {}}
    cost, costby = cost_summary()
    rows, appx = [], []
    briefs = [f"{s}/b{b}" for s, b in E.briefs()]
    sty_keys = ["polite_ratio", "arabic_per1000", "metaphor_distinct_per1000", "speculation_per1000", "questions_per1000", "chars"]

    def mean_style(vid):
        rs = [per[f"{vid}|{k}"] for k in briefs if f"{vid}|{k}" in per]
        return [round(statistics.mean(r[m] for r in rs), 2) for m in sty_keys] if rs else None

    agg = {}
    for vid in vids_new() + ["S5"]:
        scs_d = sc["scores"].get(vid, {})
        scs = [scs_d[k]["x_score"] if k in scs_d else None for k in briefs]
        valid = [s for s in scs if s is not None]
        tot = sum(valid)
        split = sum(1 for s in valid if s == 0.5)
        forf = sc["forfeit"].get(vid, [])
        label = read_label(vid, tot, valid, band, None)
        inband = "幅内" if band["band"][0] <= tot <= band["band"][1] and len(valid) == 3 else ("幅外" if len(valid) == 3 else "n/a")
        fr = F[vid]
        ex = [r for r in fr.values() if r["exists"]]
        nb = [r["num_bad"] for r in ex]
        amp = [r["amp"]["amp"] for r in ex if r["amp"]]
        fc_major = sum(1 for r in ex if r["ja_fc"]["orig_status"] not in (None, "LEDGER_COMPLIANT") or r["ja_fc"]["r2_status"] not in (None, "LEDGER_COMPLIANT"))
        fc_mf = sum(1 for r in ex if r["ja_fc"]["orig_must_fix"] or r["ja_fc"]["r2_must_fix"])
        stops = sum(1 for k in briefs if (not fr[k]["exists"]) or (fr[k]["ja_fc"]["exit_reason"] not in (None, "completed")))
        dv = div.get(vid, {})
        majors = sum(1 for m in col["majors"] if m[1] == vid)
        r3 = [fr[k].get("r3_adopted") for k in briefs if fr[k].get("r3_adopted") is not None]
        sty = mean_style(vid)
        agg[vid] = dict(scs=scs, tot=tot, label=label, nb=nb, amp=amp, sty=sty)
        rows.append(f"| {vid} | {' / '.join('-' if s is None else str(s) for s in scs)} | {tot}{'(有効'+str(len(valid))+')' if len(valid)<3 else ''} | {split}/{len(valid) or 0} | {inband} | {len(forf)} | "
                    f"{round(sum(nb)/len(nb),2) if nb else '-'} | {round(sum(amp)/len(amp),2) if amp else 'n/a'} | MAJOR系{fc_major}/{len(ex)}・must-fix{fc_mf}・STOP/欠{stops} | "
                    f"{len(dv.get('domains_common_all', []))}(最多一致={'○' if dv.get('dominant_same_all') else '×'}) | {len(dv.get('boiler_common', []))} | "
                    f"{sty} | 重大候補{majors} | {label}{' (R3採用'+str(sum(1 for x in r3 if x))+'/'+str(len(r3))+')' if r3 else ''} |")
    L = ["# SUMMARY_SWEEP: Fact Lock Writer prompt 変種sweep 評価(委任_04c、2026-10-08、Status上限=EVALUATED、推奨は書かない)", "",
         "規則=`eval/EVAL_RULES_V2.md`(評価前固定、Opus任意レビューM1〜M7+O1/O2/O4反映)。N=3 brief×1反復。LLM判定のみ(gpt-6-luna主、gpt-5.6-luna併用)。**事実は変わらない=この規模・この指標で検出できる差がない、の意味**。", "",
         f"判定ノイズ幅(S0 r1対r2、同条件の3 brief合計): {band['band'][0]}〜{band['band'][1]}(中央{band['median']})。`NOISE_BASELINE.md`。", "",
         "## 1. 一覧表",
         "文体列=[です・ます文率, 半角数字/1000字, 比喩異なり/1000字, 推量・仮定語/1000字, 問い/1000字, 字数](3記事平均)。数値NG=本文数字のうちbrief・台帳に無いもの/本。増幅=new_specific_claimのR0→R2増加/本。",
         "", "| 変種 | brief別スコア(meta b2 / hormuz b4 / space_weapons b3) | 合計(0-3) | 割れ率 | ノイズ幅 | 不戦敗 | 数値NG/本 | 増幅(ii)/本 | JA FC(非COMPLIANT/must-fix/STOP) | 比喩領域共通(最多一致) | 決まり文句共通 | 文体 | 重大候補(LLM) | 3段階の読み |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"] + rows
    # S0行
    s0n = [F["S0"][k]["num_bad"] for k in briefs if F["S0"][k]["exists"]]
    s0d = div.get("S0", {})
    L.append(f"| S0(基準) | - | - | - | - | - | {round(sum(s0n)/len(s0n),2) if s0n else '-'} | n/a | - | {len(s0d.get('domains_common_all', []))}(最多一致={'○' if s0d.get('dominant_same_all') else '×'}) | {len(s0d.get('boiler_common', []))} | {mean_style('S0')} | 重大候補{sum(1 for m in col['majors'] if m[1]=='S0')} | - |")
    L += ["", "S5行はアンカー(Fact Lock v1 対 S0の再測)。重大候補は`HUMAN_CHECK_SWEEP.md`で人間確認待ち(LLM抽出、確定値ではない)。", ""]
    L += ["## 2. O2: pairwise勝者−敗者の文体指標差の符号集計(割れ除く決着対のみ)", f"決着対数={O2['n_decided_pairs']}", "",
          "| 指標 | 勝者が高い | 勝者が低い | 同値 |", "|---|---|---|---|"]
    for m, v in O2["by_metric"].items():
        L.append(f"| {m} | {v['pos']} | {v['neg']} | {v['zero']} |")
    L += ["", "注: 文体指標はpromptの変更で動いた経路(媒介)であり、「この文体を指定すれば面白くなる」とは読まない。", "",
          "## 3. O4: 台帳との逐語8-gram一致率(転記度、3記事平均)", "", "| 変種 | " + " | ".join(all_vids()) + " |", "|---|" + "---|" * len(all_vids()),
          "| 8-gram率 | " + " | ".join(str(O4[v]) for v in all_vids()) + " |", ""]
    if ag:
        L += ["## 4. O1: 5.6併用の一致度", f"- 個別判定の一致: {ag['judgment_agree']} / brief別スコアの一致: {ag['brief_score_agree']}", f"- Aを選んだ率: {ag['A_rate']} / Bを選んだ率: {ag['B_rate']}", ""]
    L += ["## 5. 参考: LLM所見(多様性)・軽微", "- 多様性LLM所見: `eval/diversity_llm.json`(変種名は伏せたコード、対応は`_private/MAP_DIVERSITY.json`)。", f"- 軽微(参考、JA/EN分離): {json.dumps(col['minors'], ensure_ascii=False)}", ""]
    L += ["## 6. 費用", f"- eval実費(raw_usage_logからの概算): ¥{cost:.2f} / 上限¥120。内訳(stage別): {json.dumps({k: round(v,2) for k,v in costby.items()}, ensure_ascii=False)}", ""]
    L += extras(agg, F, per, O4, div)
    open(f"{EV}/SUMMARY_SWEEP.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    E.jdump({"agg": agg, "o2": O2, "o4": O4, "agreement": ag, "cost": cost}, f"{EV}/summary_data.json")
    print("\n".join(L))


def main(cmd, args):
    models = [E.SUB_JUDGE] if "--sub" in args else [E.MAIN_JUDGE]
    if cmd == "cells":
        for v, d in cells().items():
            print(v, {k: (c["exists"], c.get("r3_adopted")) for k, c in d.items()})
    elif cmd == "pairwise":
        only = args[args.index("--vars") + 1].split(",") if "--vars" in args else None
        for m in models:
            pairwise(m, only)
    elif cmd == "facts":
        facts()
    elif cmd == "blind":
        blind()
    elif cmd == "rubric":
        rubric()
    elif cmd == "human_check":
        human_check()
    elif cmd == "diversity":
        diversity_mech()
        diversity_llm()
    elif cmd == "style":
        per = style_all()
        print(json.dumps(o2(per), ensure_ascii=False), o4())
    elif cmd == "summary":
        summary()
    elif cmd == "cost":
        print(cost_summary())
    else:
        raise SystemExit("unknown cmd " + cmd)
