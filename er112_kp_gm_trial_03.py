# -*- coding: utf-8 -*-
"""FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_08: Std確認Trial(G0/G2/G3 x 2rep、DEV専用、er112基盤)。
Production file(er003_*/er019_*/runner)は編集しない。importして呼ぶだけ。新しいPrompt案は追加しない(G2/G3はer112_kp_gm_trial_02のブロックをそのまま再利用)。
出力: er112_output/kp_gm_trial_03/ 。費用台帳=paid_calls.jsonl。上限30円。
サブコマンド: set / gloss / e0 / blind / judge / report
"""
from __future__ import annotations
import argparse, hashlib, json, os, random, re, sys, threading, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")
OUT = ROOT / "er112_output" / "kp_gm_trial_03"
LEDGER = OUT / "paid_calls.jsonl"
RES = OUT / "results.jsonl"
CAP_JPY = 30.0
RD = ROOT / "docs/research/FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01"
STOP_PATHS = [OUT / "STOP", OUT / "STOP_ALL", ROOT / "er026_output/family_z_production_e2e_01/STOP_ALL", RD / "STOP"]

import er112_kp_gm_trial_02 as T      # noqa: E402 (DEV module。G2/G3ブロックと呼出関数を再利用)
import er112_kp_gm_kpset_03 as K3     # noqa: E402
import er098_kp_six_model_trial_01_common as C   # noqa: E402 (評価呼出の共通部。Trial専用)

_lock = threading.Lock()
ARMS = ["G0", "G2", "G3"]


def stop():
    return any(p.exists() for p in STOP_PATHS)


def total():
    t = 0.0
    if LEDGER.exists():
        for l in LEDGER.read_text(encoding="utf-8").splitlines():
            if l.strip():
                try:
                    t += json.loads(l).get("cost_jpy", 0)
                except ValueError:
                    pass
    return t


def _append(path, rec):
    fd = os.open(str(path), os.O_WRONLY | os.O_APPEND | os.O_CREAT)
    try:
        os.write(fd, (json.dumps(rec, ensure_ascii=False) + chr(10)).encode("utf-8"))
    finally:
        os.close(fd)


def ledger_add(rec):
    with _lock:
        OUT.mkdir(parents=True, exist_ok=True)
        _append(LEDGER, rec)


def res_add(rec):
    with _lock:
        _append(RES, rec)


def load_res():
    d = {}
    if RES.exists():
        for l in RES.read_text(encoding="utf-8").splitlines():
            if l.strip():
                try:
                    r = json.loads(l)
                except ValueError:
                    continue
                d[(r["arm"], r["key"], r["rep"])] = r
    return d


def kpall():
    """難例20(Trial_02と同一入力) + 新規通常40(Trial_01/02未使用)。"""
    A2 = T.kpset()
    used = set(A2) | set(T.PRE_A1_DROP)
    hard = {k: v for k, v in A2.items() if v["tier"] == "hard"}
    normal, miss = K3.select(used)
    assert not miss, miss
    assert not (set(normal) & set(A2)), "normalがTrial_02集合と重複"
    allkp = dict(hard)
    allkp.update(normal)
    return allkp


def art_id(kp):
    return hashlib.sha256(kp["article"].encode("utf-8")).hexdigest()[:10]


# ------------------------------------------------------------------ gold(Fable確定 2026-10-23。GOLD_LABELS_FINAL_01.md)
def gold_final():
    g = json.load(open(ROOT / "er112_output/kp_gm_trial_02/gold_labels_draft_01.json", encoding="utf-8"))
    fin = {}
    for k, v in g.items():
        if k.startswith("_"):
            continue
        fin[k.lower()] = dict(v)
    fin["draw a line"].update(
        ok_ja="一線を引く/区別をはっきりさせる/線引きをする/境界をはっきりさせる(許容と不許容の区別を示す意味)",
        ng_ja="字義の『線を引く』『境界線を引く』(描く動作)", alt="Fable確定: 『一線を引く』は許容")
    fin["carry the load"].update(ok_ja="(負担・役割)を担う/重い役目を受け持つ。字義(荷物を運ぶ)・比喩とも許容。比喩含意(負担を担う)を含む方が上位", ng_ja="なし", alt="Fable確定: 字義・比喩とも許容")
    fin["take the wheel"].update(ok_ja="ハンドルを握る/運転する(責任を引き受ける・主導する)。Std『ハンドルを握る』許容", ng_ja="なし", alt="Fable確定: Std許容、Adv 'take control' 許容、Std/Adv矛盾に数えない")
    return fin


# ------------------------------------------------------------------ gloss run
def run_gloss(arm, reps, A, cap):
    groups = {}
    for k, kp in A.items():
        groups.setdefault(art_id(kp), []).append(kp)
    done = load_res()
    jobs = [(rep, g) for rep in reps for g in groups.values() if any((arm, kp["key"].lower(), rep) not in done for kp in g)]
    print(arm, "gloss jobs", len(jobs), flush=True)

    def w(j):
        rep, g = j
        if stop() or total() >= cap:
            return ("SKIP", rep, g[0]["key"])
        items, c, u, raw = T.gloss_call(arm, g, T.LUNA)
        ledger_add(dict(kind="gloss", arm=arm, model=T.LUNA, keys=[x["key"] for x in g], rep=rep, usage=u, cost_jpy=round(c, 5), ts=time.strftime("%Y-%m-%dT%H:%M:%S")))
        by = {it["rank"]: it for it in items}
        for i, kp in enumerate(g):
            it = by.get(i + 1) or {}
            res_add(dict(arm=arm, key=kp["key"].lower(), rep=rep, kind="G", tier=kp["tier"], sent=kp["sent"], gloss=it.get("japanese_gloss"), usage_type=it.get("usage_type"),
                         core_sense=it.get("core_sense_en"), candidates=it.get("candidates"), call_cost_jpy=round(c, 5), n_in_call=len(g)))
        return (arm, rep, [x["key"] for x in g], round(c, 4))
    with ThreadPoolExecutor(6) as ex:
        for f in as_completed([ex.submit(w, j) for j in jobs]):
            print(f.result(), "cum=%.3f" % total(), flush=True)


def run_e0(gloss_arm, A, cap):
    """E0(現行Adv Prompt、Production関数と同じ文面をT.expl_call経由で呼ぶ)。入力=gloss_arm rep1の出力。normal 40のみ。"""
    res = load_res()
    out_arm = "E0@" + gloss_arm
    jobs = []
    for k, kp in A.items():
        if kp["tier"] != "normal" or (out_arm, k, 1) in res:
            continue
        gr = res.get((gloss_arm, k, 1))
        if gr and gr.get("gloss"):
            jobs.append((k, kp, gr["gloss"]))
    print(out_arm, "e0 jobs", len(jobs), flush=True)

    def w(j):
        k, kp, g = j
        if stop() or total() >= cap:
            return ("SKIP", k)
        x, c, u, raw = T.expl_call("E0", kp, g)
        ledger_add(dict(kind="expl", arm=out_arm, key=k, rep=1, usage=u, cost_jpy=round(c, 5), ts=time.strftime("%Y-%m-%dT%H:%M:%S")))
        res_add(dict(arm=out_arm, key=k, rep=1, kind="E", tier=kp["tier"], sent=kp["sent"], gloss_in=g, text=x["english_explanation"], call_cost_jpy=round(c, 5)))
        return (out_arm, k, round(c, 4))
    with ThreadPoolExecutor(6) as ex:
        for f in as_completed([ex.submit(w, j) for j in jobs]):
            print(f.result(), "cum=%.3f" % total(), flush=True)


# ------------------------------------------------------------------ Fable盲検表
def make_blind(A):
    res = load_res()
    key_map, lines = {}, []
    lines.append("# fable_blind_std_03: Std日本語gloss盲検表(委任_08 Std確認Trial)\n")
    lines.append("行=Key Phrase、列A〜F=6出力(armとrepはKPごとにランダム化、正体は`fable_blind_std_03_key.json`に分離)。**判定してから key を開くこと。**")
    lines.append("判定記入: 各セルに PASS / 薄(△=意味は誤りでないがフレーズ全体より弱い・含意が欠ける) / FAIL を書く。難例(hard)はGOLD_LABELS_FINAL_01.mdのgold、通常(normal)は本文文の用法とフレーズ全体の意味への一致を基準にする。")
    lines.append("同一出力は同じ文字列のまま別列に出る(重複=その出力が安定している印)。\n")
    lines.append("| # | tier/型/X-Z | key_phrase | 本文の文 | A | B | C | D | E | F |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")
    keys = sorted(A, key=lambda k: (A[k]["tier"] != "hard", k))
    for n, k in enumerate(keys, 1):
        kp = A[k]
        cells = [(arm, rep) for arm in ARMS for rep in (1, 2)]
        rnd = random.Random("blind03-" + k)
        rnd.shuffle(cells)
        key_map[k] = {chr(65 + i): "%s/rep%d" % c for i, c in enumerate(cells)}
        outs = []
        for (arm, rep) in cells:
            r = res.get((arm, k, rep))
            outs.append((r.get("gloss") if r else None) or "(出力なし)")
        meta = "%s/%s/%s" % (kp["tier"], kp.get("type", "-"), kp["family"])
        lines.append("| %d | %s | %s | %s | %s |" % (n, meta, kp["key"], kp["sent"].replace("|", "/"), " | ".join(o.replace("|", "/") for o in outs)))
    (OUT / "fable_blind_std_03.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    json.dump(key_map, open(OUT / "fable_blind_std_03_key.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("blind rows", len(keys))


# ------------------------------------------------------------------ Sonnet参考Judge(3値)
THIN = ("薄い(△)の例: brace yourself for→『～に備える』(身構える・覚悟する含意が欠ける)、keep someone company→『人の相手をする』(一緒にいてあげる意味が弱い)、"
        "a sense of occasion→『特別感』(行事・節目にふさわしい雰囲気の意味が弱い)、behind the scenes→『見えないところで』(裏方・舞台裏の含意が弱い)、"
        "on the throne→『トップの座にいる』(王座・君臨の比喩が失われる)。")
JUDGE_INSTR = (
    "あなたは英語学習コンテンツの独立評価者です。日本人成人の英語学習者向け『Key Phrase』の日本語の意味(gloss)を評価します。各行は独立に評価し、行の並びや番号から推測しないでください。"
    "思考過程や前置きは出力せず、結果だけを出力します。出力形式: 対象行ごとに1行、`<行番号> <P|T|F> <note>`。noteはT/Fのときだけ20字以内で理由を書き、Pなら省略。\n\n"
    "判定: P=本文のその文での用法の意味を、フレーズ全体として正しく十分に伝えている。T(薄い)=意味は誤りではないが、フレーズ全体の意味に比べて弱い・一般的すぎる・含意や構成語の意味が欠ける・やや不自然。"
    "F=用法の取り違え(字義の逐語訳、別義、比喩を字義で訳す等)、誤訳、『あなた/彼』など具体人称への置換、複数の訳の併記、記事固有の情報の混入。\n"
    + THIN + "\n"
    "gold_referenceがある行は、その表現の本文での用法と許容される語義範囲の正解ラベルです(範囲内ならP以上、範囲外・別用法・字義の逐語訳ならF。許容範囲内でもフレーズ全体より弱ければT)。\n"
    "日本語でも同じ比喩が同じ意味で自然に通じる表現(光を当てる、一線を引く)は逐語に数えません。\n\n【対象行】\n")
CONS_INSTR = (
    "あなたは英語学習コンテンツの独立評価者です。同じ表現について、Standard向けの日本語の意味(gloss_ja)とAdvanced向けの英語説明(explanation_en)があります。各行は独立に評価します。"
    "出力形式: 対象行ごとに1行、`<行番号> <sense><consistent> <note>`(sense, consistentは0/1の2桁。例 `11`)。noteは問題があるときだけ20字以内。\n"
    "- sense(1/0): explanation_enが、本文のその文でのこの表現の意味を正しく表しているか(誤り・別義なら0)。\n"
    "- consistent(1/0): gloss_jaとexplanation_enが同じ用法(字義/比喩)・同じ語義を指しているか。表現の細かい違い・言い換えは矛盾に数えない。用法・語義が食い違う場合だけ0。\n\n【対象行】\n")
_L3 = re.compile(r"^\s*(\d+)[.:)]?\s+([PTF])\b\s*(.*)$")
_LC = re.compile(r"^\s*(\d+)[.:)]?\s+([01])([01])\b\s*(.*)$")
JMODEL = "claude-sonnet-5-5"
JBATCH = 25


def _jrid(*parts):
    return hashlib.sha256("\x1f".join(parts).encode("utf-8")).hexdigest()[:12]


def judge_cache():
    p = OUT / "judge" / "cache.jsonl"
    c = {}
    if p.exists():
        for l in p.read_text(encoding="utf-8").splitlines():
            if l.strip():
                r = json.loads(l)
                c[r["id"]] = r
    return c


def judge_call(kind, batch, cap):
    if stop() or total() >= cap:
        return ("SKIP",)
    head = JUDGE_INSTR if kind == "S" else CONS_INSTR
    body = head + "\n".join("%d. %s" % (i, json.dumps({k: v for k, v in r.items() if k not in ("id",)}, ensure_ascii=False)) for i, r in enumerate(batch, 1))
    b = C.build_body("anthropic", JMODEL, body)
    r = C.call_with_retry("anthropic", JMODEL, b)
    if not r["ok"]:
        return ("ERR", str(r["attempts"])[:200])
    cost = C.cost_usd(JMODEL, r["usage"]) * C.USD_JPY
    ledger_add(dict(kind="judge", judge=JMODEL, batch_kind=kind, n=len(batch), usage=r["usage"], cost_jpy=round(cost, 5), ts=time.strftime("%Y-%m-%dT%H:%M:%S")))
    got = {}
    for ln in r["text"].splitlines():
        if kind == "S":
            m = _L3.match(ln)
            if m and 1 <= int(m.group(1)) <= len(batch):
                got[batch[int(m.group(1)) - 1]["id"]] = dict(v=m.group(2), note=m.group(3).strip())
        else:
            m = _LC.match(ln)
            if m and 1 <= int(m.group(1)) <= len(batch):
                got[batch[int(m.group(1)) - 1]["id"]] = dict(sense=int(m.group(2)), consistent=int(m.group(3)), note=m.group(4).strip())
    with _lock:
        (OUT / "judge").mkdir(parents=True, exist_ok=True)
        with open(OUT / "judge" / "cache.jsonl", "a", encoding="utf-8") as f:
            for row in batch:
                if row["id"] in got:
                    f.write(json.dumps(dict(id=row["id"], kind=kind, verdict=got[row["id"]]), ensure_ascii=False) + "\n")
    return ("OK", len(got), len(batch), round(cost, 4))


def judge_rows(A):
    res = load_res()
    gold = gold_final()
    rows = {}
    for (arm, k, rep), r in res.items():
        if r["kind"] == "G" and r.get("gloss"):
            row = dict(kind="G", key_phrase=A[k]["key"], source_sentence=r["sent"], gloss=r["gloss"])
            if k in gold and A[k]["tier"] == "hard":
                g = gold[k]
                row["gold_reference"] = "用法=%s / 許容される意味=%s / 不可=%s" % (g["usage"], g["ok_ja"], g["ng_ja"])
            row["id"] = "S_" + _jrid(k, r["sent"], r["gloss"])
            rows.setdefault(row["id"], row)
    cons = {}
    for (arm, k, rep), r in res.items():
        if r["kind"] == "E" and arm.startswith("E0@"):
            row = dict(kind="C", key_phrase=A[k]["key"], source_sentence=r["sent"], gloss_ja=r["gloss_in"], explanation_en=r["text"])
            row["id"] = "C_" + _jrid(k, r["gloss_in"], r["text"])
            cons.setdefault(row["id"], row)
    return rows, cons


def run_judge(A, cap, what):
    rows, cons = judge_rows(A)
    cache = judge_cache()
    todo = []
    if what in ("S", "all"):
        rs = sorted([r for i, r in rows.items() if i not in cache], key=lambda x: x["id"])
        todo += [("S", rs[i:i + JBATCH]) for i in range(0, len(rs), JBATCH)]
    if what in ("C", "all"):
        rs = sorted([r for i, r in cons.items() if i not in cache], key=lambda x: x["id"])
        todo += [("C", rs[i:i + JBATCH]) for i in range(0, len(rs), JBATCH)]
    print("judge rows S=%d C=%d jobs=%d" % (len(rows), len(cons), len(todo)), flush=True)
    with ThreadPoolExecutor(4) as ex:
        for f in as_completed([ex.submit(judge_call, k, b, cap) for k, b in todo]):
            print(f.result(), "cum=%.3f" % total(), flush=True)


# ------------------------------------------------------------------ 集計(key開封後、Sonnet参考値)
def report(A):
    res = load_res()
    cache = judge_cache()
    rows, cons = judge_rows(A)
    rank = {"P": 2, "T": 1, "F": 0}

    def lab(arm, k, rep):
        r = res.get((arm, k, rep))
        if not r or not r.get("gloss"):
            return None
        v = cache.get("S_" + _jrid(k, r["sent"], r["gloss"]))
        return v["verdict"]["v"] if v else None
    out = {}
    lines = ["# SONNET_REFERENCE_03(参考値。最終判定はFable盲検。Judge=%s、3値 P/T(薄)/F)\n" % JMODEL]
    for tier in ("hard", "normal", "all"):
        ks = [k for k in A if tier == "all" or A[k]["tier"] == tier]
        lines.append("## %s (KP=%d)\n" % (tier, len(ks)))
        lines.append("| arm | n出力 | PASS | 薄(△) | FAIL | 未判定 |\n|---|---|---|---|---|---|")
        for arm in ARMS:
            c = {"P": 0, "T": 0, "F": 0, None: 0}
            for k in ks:
                for rep in (1, 2):
                    c[lab(arm, k, rep)] += 1
            n = sum(c.values())
            lines.append("| %s | %d | %d (%.0f%%) | %d (%.0f%%) | %d (%.0f%%) | %d |" % (arm, n, c["P"], 100 * c["P"] / n, c["T"], 100 * c["T"] / n, c["F"], 100 * c["F"] / n, c[None]))
            out[(tier, arm)] = c
        lines.append("")
        # flip vs G0(rep対応)
        for arm in ("G2", "G3"):
            up = dn = same = 0
            for k in ks:
                for rep in (1, 2):
                    a, b = lab("G0", k, rep), lab(arm, k, rep)
                    if a is None or b is None:
                        continue
                    if rank[b] > rank[a]:
                        up += 1
                    elif rank[b] < rank[a]:
                        dn += 1
                    else:
                        same += 1
            lines.append("- %s vs G0 (rep対応の出力単位): 改善%d / 悪化%d / 不変%d" % (arm, up, dn, same))
        # rep自己一致
        for arm in ARMS:
            ag = txt = n = 0
            for k in ks:
                l1, l2 = lab(arm, k, 1), lab(arm, k, 2)
                if l1 is None or l2 is None:
                    continue
                n += 1
                ag += l1 == l2
                txt += res[(arm, k, 1)]["gloss"] == res[(arm, k, 2)]["gloss"]
            lines.append("- %s rep1/rep2: 判定一致 %d/%d (%.0f%%)、gloss文字列一致 %d/%d (%.0f%%)" % (arm, ag, n, 100 * ag / max(n, 1), txt, n, 100 * txt / max(n, 1)))
        lines.append("")
    # 型別(normal)
    lines.append("## normal 型別 (P=句動詞/I=慣用句・定型/C=コロケーション/T=名詞句・用語) の PASS/薄/FAIL\n")
    for ty in "PICT":
        ks = [k for k in A if A[k]["tier"] == "normal" and A[k].get("type") == ty]
        row = []
        for arm in ARMS:
            c = {"P": 0, "T": 0, "F": 0, None: 0}
            for k in ks:
                for rep in (1, 2):
                    c[lab(arm, k, rep)] += 1
            row.append("%s %d/%d/%d" % (arm, c["P"], c["T"], c["F"]))
        lines.append("- 型%s (KP=%d): %s" % (ty, len(ks), " | ".join(row)))
    # E0引き継ぎ(normal 40 + hard20 Trial_02)
    lines.append("\n## E0引き継ぎ(normal40、E0@G* rep1): sense誤り / Std-Adv矛盾\n")
    for arm in ARMS:
        n = sb = cb = 0
        for k in A:
            r = res.get(("E0@" + arm, k, 1))
            if not r:
                continue
            v = cache.get("C_" + _jrid(k, r["gloss_in"], r["text"]))
            if not v:
                continue
            n += 1
            sb += v["verdict"]["sense"] == 0
            cb += v["verdict"]["consistent"] == 0
        lines.append("- E0@%s: n=%d sense誤り=%d consistent=0(矛盾)=%d" % (arm, n, sb, cb))
    (OUT / "sonnet_reference_03.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("--arm", default="")
    ap.add_argument("--reps", default="1,2")
    ap.add_argument("--cap", type=float, default=CAP_JPY)
    ap.add_argument("--what", default="all")
    ap.add_argument("--hard-only", action="store_true")
    a = ap.parse_args()
    A = kpall()
    if a.cmd == "set":
        import collections
        print(len(A), collections.Counter((v["tier"], v["family"]) for v in A.values()), "articles", len({art_id(v) for v in A.values()}))
        json.dump({k: {x: y for x, y in v.items() if x != "article"} for k, v in A.items()}, open(OUT / "kpall_03.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1) if OUT.exists() else None
    elif a.cmd == "gloss":
        AA = {k: v for k, v in A.items() if not a.hard_only or v["tier"] == "hard"}
        run_gloss(a.arm, [int(x) for x in a.reps.split(",")], AA, a.cap)
    elif a.cmd == "e0":
        run_e0(a.arm, A, a.cap)
    elif a.cmd == "blind":
        make_blind(A)
    elif a.cmd == "judge":
        run_judge(A, a.cap, a.what)
    elif a.cmd == "report":
        report(A)
