# ============================================================
# er111_ukus_pairs_build_01.py
# ASR-QUALITY-2ITEMS-COMPREHENSIVE-01 ②英米綴り UKUS 委任_02 (DEV/Trial専用・Production未配線)
# 目的: VarCon 2020.12.07 + SCOWL 2020.12.07 から、英米綴り対の『固定対表』er111_ukus_pairs_v1.json を決定論的に生成する(ビルド時のみ。runtimeは固定表だけを読む)。
#   Opus OF-03: VarConタグ解析 = UK側はB/Z(plain)でA(plain)を持たない語、US側はA(plain)でB(plain)を持たない語(Av=米変異綴りはUK側へ入れない)。
#   Opus OF-04: UK形が別の項で有効な米綴り(mum[silent]/mom 型)は自動検出して除外(用法不明のため判定不能)。
#   Opus OF-05: Tier-2(level71-99)は active=False(初回Trialでは非同値=fail-closed)。
#   Opus OF-08: 規則(ise->ize, yse->yze, our->or)の実在語判定は SCOWL固定版(変換前=SCOWL英国語専用リストにある語、変換後=SCOWL米国語/共通語 level<=70)。runtime依存なし。
#   Opus OF-11: breame不採用。出力冒頭に著作権/許諾文・入力hashを残す。
# 入力: docs/research/.../UKUS/work/{varcon_2020.12.07.txt, scowl_subsets_2020.12.07.json.gz}
# 出力: er111_ukus_pairs_v1.json (+ --review で TRIAL_01/PAIRS_REVIEW_01.md の元データ)
# ============================================================
from __future__ import annotations

import argparse
import collections
import gzip
import hashlib
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, "docs", "research", "ASR-QUALITY-2ITEMS-COMPREHENSIVE-01", "UKUS", "work")
VARCON = os.path.join(WORK, "varcon_2020.12.07.txt")
SCOWL_SUB = os.path.join(WORK, "scowl_subsets_2020.12.07.json.gz")
OUT = os.path.join(HERE, "er111_ukus_pairs_v1.json")
BUILD_VERSION = "er111_ukus_pairs_build_01_v1"

LICENSE_TEXT = (
    "VarCon (Variant Conversion Info) 2020.12.07 and SCOWL 2020.12.07 are Copyright 2000-2020 by Kevin Atkinson (VarCon also Benjamin Titze) and the contributors "
    "listed in the SCOWL Copyright file. Permission to use, copy, modify, distribute and sell these word lists, the associated scripts, the output created from the "
    "scripts, and its documentation for any purpose is hereby granted without fee, provided that the above copyright notice appears in all copies and that both that "
    "copyright notice and this permission notice appear in supporting documentation. Kevin Atkinson makes no representations about the suitability of this array for "
    "any purpose. It is provided 'as is' without express or implied warranty. (https://github.com/en-wl/wordlist)")

TIER1_MAX_LEVEL = 70
RULES = [("isation", "ization"), ("isations", "izations"), ("ise", "ize"), ("ised", "ized"), ("ises", "izes"), ("ising", "izing"), ("iser", "izer"),
         ("isers", "izers"), ("yse", "yze"), ("ysed", "yzed"), ("yses", "yzes"), ("ysing", "yzing"), ("our", "or"), ("ours", "ors"), ("oured", "ored"),
         ("ouring", "oring"), ("ourful", "orful"), ("ourite", "orite")]
RULE_MIN_STEM = 4

_HDR = re.compile(r"^# (\S+)(?: (<verified>))? \(level (\d+)\)")
_LINE = re.compile(r"^(?P<grp>[^|#]+?)(?:\s*\|\s*(?P<usage>[^#]*?))?\s*(?:#.*)?$")


def _sha256_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def parse_tags(tagstr: str) -> dict:
    """タグ列 -> {region: suffix_string}。例 'Av'->{'A':'v'}, 'B-'->{'B':'-'}, '_'->無視。数字トークンは無視。"""
    out = {}
    for t in tagstr.split():
        if t.isdigit():
            continue
        m = re.match(r"^([ABCDZ_])([vV\-x.]*)$", t)
        if m and m.group(1) != "_":
            out[m.group(1)] = m.group(2)
    return out


def plain(tags: dict, region: str) -> bool:
    """その地域で『推奨(plain)』の綴りか: タグがあり、v/V/-/x の印が無い('.'は推奨扱い)。"""
    return region in tags and not re.search(r"[vV\-x]", tags[region])


def strict(tags: dict, region: str) -> bool:
    """マーク無し(その地域の第一推奨)のみ。'.'(あまり使われない)も除く。US/UK側の所属判定に使う(OF-03)。"""
    return region in tags and tags[region] == ""


def load_varcon():
    """list of {groups:[(word,tags)], usage, level, verified, lineno}"""
    out = []
    level, verified = 99, False
    for i, raw in enumerate(open(VARCON, encoding="latin-1"), 1):
        raw = raw.rstrip("\n")
        if raw.startswith("# "):
            mh = _HDR.match(raw)
            if mh:
                level, verified = int(mh.group(3)), bool(mh.group(2))
            continue
        if not raw or raw.startswith("#"):
            continue
        m = _LINE.match(raw)
        if not m:
            continue
        usage = (m.group("usage") or "").strip() or None
        groups = []
        for g in m.group("grp").split(" / "):
            tagstr, _, word = g.partition(":")
            word = word.strip()
            if not word or " " in word or "_" in word:
                continue
            groups.append((word, parse_tags(tagstr)))
        out.append({"groups": groups, "usage": usage, "level": level, "verified": verified, "lineno": i})
    return out


def lev(a, b) -> int:
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def load_scowl():
    return json.load(gzip.open(SCOWL_SUB, "rt", encoding="utf-8"))


def varcon_pairs():
    entries = load_varcon()
    a_plain_words = collections.defaultdict(list)   # word -> [lineno] (OF-04用)
    for en in entries:
        for w, tg in en["groups"]:
            if plain(tg, "A") and not w[:1].isupper():
                a_plain_words[w.lower()].append(en["lineno"])
    pairs = {}
    for en in entries:
        us_set, uk_set = [], []
        for w, tg in en["groups"]:
            if w[:1].isupper() or not re.fullmatch(r"[a-z'\-]+", w):
                continue
            a_p = strict(tg, "A")
            # UK形 = B/Z タグがあり(x/-なし)、A が無い/A が非推奨(v/V/-/x/.)。Av(米変異綴り)はB無しなのでUK側に入らない(OF-03)。Bv(英変異)は許す(foetus, encyclopaedia)
            uk_p = any(r in tg and not re.search(r"[x\-]", tg[r]) for r in ("B", "Z")) and not a_p
            if a_p:
                us_set.append(w)                      # A 第一推奨(B/Zとの併記も可: organize=A+Z, encyclopedia=A+B+C+D)
            elif uk_p:
                uk_set.append(w)
        for uk in uk_set:
            for us in us_set:
                if uk == us:
                    continue
                key = (uk, us)
                amb = bool(en["usage"])
                rec = pairs.get(key)
                if rec is None:
                    pairs[key] = {"uk": uk, "us": us, "level": en["level"], "usage": en["usage"], "amb": amb, "lineno": en["lineno"], "src": "varcon"}
                else:
                    rec["level"] = min(rec["level"], en["level"])
                    rec["amb"] = rec["amb"] and amb
    keep, excluded = {}, []
    for (uk, us), rec in pairs.items():
        other = [ln for ln in a_plain_words.get(uk, []) if ln != rec["lineno"]]
        if other:
            excluded.append({"uk": uk, "us": us, "reason": "OF04_uk_form_also_valid_us_elsewhere", "level": rec["level"], "lineno": rec["lineno"], "other_lines": other[:3]})
            continue
        keep[(uk, us)] = rec
    return entries, keep, excluded


def rule_target(w: str):
    for u, a in RULES:
        if w.endswith(u) and len(w) - len(u) >= RULE_MIN_STEM:
            return w[: -len(u)] + a, u
    return None, None


# ---------------------------------------------------------------- 人手レビュー結果(denylist)。(ukの正規表現, usの正規表現, 理由)。fullmatch。
# 次の観点でT1(level<=70)対を全件レビューした: (a)綴り編集距離>2/短語/語頭相違(177件)、(b)CMU両側登録で音素が異なる対(51件)、(c)両形が高頻度独立語(zipf>=3.3、約120件)、
# (d)AMB(用法付き)全件(約117対)、(e)OF-04自動検出(60件)。結果は TRIAL_01/PAIRS_REVIEW_01.md に全件記録。
DENY = [
    (r"arse.*", r".*", "profanity_or_other_word(ass)"),
    (r"saki.*", r"sake.*", "different_word(saki=monkey/sake)"),
    (r"crees", r"ceres", "different_word"), (r"vires", r"viers", "different_word"), (r"loury", r"lory", "different_word"),
    (r"matts?", r"mats?", "different_word(matt!=mat)"),
    (r"(aeq|aet|aeros|oecus|poe|bael|bour|cre|gre|jour|kaed|ren|renes|rens|resh|ret|goey)", r".*", "short_or_rare_junk_pair(VarCon_edge)"),
    (r"rencontre", r"rencounter", "pronunciation_differs_different_word"),
    (r"formulae", r"formulas", "different_number_form_pron_differs"),
    (r"lupins?", r"lupines?", "different_word(lupin_plant/lupine_adj)"),
    (r"groyn.*", r"groin.*", "different_word(groin_body_part)"),
    (r"prise.*|prised|prises|prising|priser.*", r"prize.*", "different_word(prise_vs_prize)"),
    (r"faggot.*", r".*", "offensive_term_hygiene"),
    (r"mum.*|mums", r"mom.*|moms", "OF04_mother_sense_pron_differs"),
    (r"onwards", r"onward", "grammatical_form_not_spelling(s_dropped)"),
    (r"oversized", r"oversize", "grammatical_form_not_spelling(d_dropped)"),
    (r"sweepstakes?|sweepstake's", r"sweepstakes.*", "grammatical_form_not_spelling(s_dropped)"),
    (r"maths", r"math", "grammatical_form_not_spelling(s_dropped)"),
    (r"amongst", r"among", "lexical_variant_pron_differs(st_dropped)"),
    (r"backwards", r"backward", "grammatical_form_not_spelling(s_dropped)"),
    (r"unbeknown", r"unbeknownst", "lexical_variant_pron_differs(st_added)"),
    # ---- 委任_02: UK側定義をBv/B.(英変異)まで広げたことで増えた約430対の人手レビューで除外したもの
    (r"amoebae", r".*", "plural_form_not_spelling"), (r"amidst", r"amid", "lexical_variant_pron_differs(st_dropped)"),
    (r"caulkings", r"caulks", "different_inflection"), (r"cicatrice", r"cicatrix", "different_word_form"), (r"coelomata", r".*", "different_plural_form"),
    (r"dikes?|dykes?", r".*", "offensive_or_ambiguous_term_hygiene"),
    (r"discs?|disks?", r"discs?|disks?", "different_usage_not_regional_spelling(disc/disk)"),
    (r"diss", r"dis", "slang_short_pair"), (r"forego|foregoing", r"forgo|forgoing", "different_words(forego!=forgo)"), (r"hah", r"ha", "interjection_short_pair"),
    (r"kyloes", r"kyles", "different_word"), (r"mattes?", r"mats?", "different_word(matte!=mat)"), (r"nanogrammes", r".*", "different_unit(nano!=micro)"),
    (r"noseys", r"nosies", "different_inflection"), (r"oesophaguses", r"esophagi", "different_plural_form"), (r"premiss(es)?", r"premises?", "different_words(premiss!=premise)"),
    (r"stoor", r"stor", "dialect_short_pair"), (r"tempi", r"tempos", "different_plural_form"), (r"virtuosos", r"virtuosi", "different_plural_form"),
    (r"wiz|wizzes", r"whiz|whizzes", "slang_short_pair"),
    (r"caesar", r"cesar", "proper_name_collision(Caesar/Cesar)"),   # V5c人手レビューで追加
]
_DENY_RX = [(re.compile(a), re.compile(b), why) for a, b, why in DENY]


def denied(uk, us):
    for ra, rb, why in _DENY_RX:
        if ra.fullmatch(uk) and rb.fullmatch(us):
            return why
    return None


def _cmu_info(uk, us, e109):
    pu, pa = e109._strong(e109._word_prons(uk)), e109._strong(e109._word_prons(us))
    if not pu or not pa:
        return None, None
    same = bool(pu & pa)
    dmin = min(lev(x, y) / max(len(x), len(y)) for x in pu for y in pa)
    return (not same), round(dmin, 2)


def build():
    import er109_asr_orthographic_equivalence_01 as e109
    entries, keep, excluded = varcon_pairs()
    sc = load_scowl()
    am70 = set(sc["american"]) | set(sc["english"])
    out, excl = {}, []
    # OF-04 自動検出分: CMU両側登録かつ音素が交わる(同じ発音)ならAMB(UK->USのみ)として復活。交わらない/未登録は除外(mum/mom型)
    for x in excluded:
        pd_, dm = _cmu_info(x["uk"], x["us"], e109)
        if pd_ is False:
            keep[(x["uk"], x["us"])] = {"uk": x["uk"], "us": x["us"], "level": x["level"], "usage": "OF04_auto", "amb": True, "lineno": x["lineno"], "src": "varcon"}
        else:
            excl.append({**x, "cmu": "unregistered" if pd_ is None else "pron_differs"})
    for (uk, us), r in sorted(keep.items()):
        why = denied(uk, us)
        pd_, dm = _cmu_info(uk, us, e109)
        if why:
            excl.append({"uk": uk, "us": us, "reason": "denylist:" + why, "level": r["level"], "lineno": r["lineno"]})
            continue
        if dm is not None and dm > 0.5:
            excl.append({"uk": uk, "us": us, "reason": "tripwire_cmu_distance>0.5", "level": r["level"], "cmu_dist": dm, "lineno": r["lineno"]})
            continue
        tier = "T1" if r["level"] <= TIER1_MAX_LEVEL else "T2"
        out[(uk, us)] = {"uk": uk, "us": us, "tier": tier, "active": tier == "T1", "dir": "uk2us" if r["amb"] else "both", "level": r["level"],
                         "src": r["src"], "amb": bool(r["amb"]), "usage": r["usage"], "pron_differs": pd_, "cmu_dist": dm, "lineno": r["lineno"]}
    # ---- 規則(OF-08): 変換前=SCOWL英国語専用語(level<=95)、変換後=SCOWL米国語/共通語(level<=70)、stem>=4。固定表へ展開(runtime規則なし)
    n_rule_new = n_rule_up = 0
    excl_keys = {(e["uk"], e["us"]) for e in excl}
    for w, lv in sorted(sc["british_only"].items()):
        t, ru = rule_target(w)
        if not t or t not in am70 or (w, t) in excl_keys:
            continue
        if denied(w, t):
            continue
        cur = out.get((w, t))
        pd_, dm = _cmu_info(w, t, e109)
        if dm is not None and dm > 0.5:
            continue
        if cur is None:
            out[(w, t)] = {"uk": w, "us": t, "tier": "R", "active": True, "dir": "both", "level": lv, "src": "rule:" + ru, "amb": False, "usage": None,
                           "pron_differs": pd_, "cmu_dist": dm, "lineno": None}
            n_rule_new += 1
        elif cur["tier"] == "T2" and not cur["amb"]:
            cur.update({"tier": "R", "active": True, "src": "varcon+rule:" + ru})
            n_rule_up += 1
    allp = [out[k] for k in sorted(out)]
    pairs = [p for p in allp if p["active"]]
    inactive = [[p["uk"], p["us"], p["level"], p["dir"]] for p in allp if not p["active"]]
    pairs_for_counts = allp
    meta = {"build_version": BUILD_VERSION, "license": LICENSE_TEXT,
            "inputs": {"varcon": {"file": "docs/research/ASR-QUALITY-2ITEMS-COMPREHENSIVE-01/UKUS/work/varcon_2020.12.07.txt", "sha256": _sha256_file(VARCON)},
                       "scowl_subsets": {"file": "docs/research/ASR-QUALITY-2ITEMS-COMPREHENSIVE-01/UKUS/work/scowl_subsets_2020.12.07.json.gz", "sha256": _sha256_file(SCOWL_SUB),
                                         "source": sc["meta"]["source"]}},
            "policy": {"tier1_max_level": TIER1_MAX_LEVEL, "T2_active": False, "amb_direction": "canonical=UK form -> ASR=US form only",
                       "rules": [list(x) for x in RULES], "rule_min_stem": RULE_MIN_STEM, "breame": "not adopted (Opus OF-11)"},
            "counts": {"pairs_total": len(allp), "active": len(pairs), "T1": sum(1 for p in pairs if p["tier"] == "T1"),
                       "T2_inactive": len(inactive), "R": sum(1 for p in pairs if p["tier"] == "R"),
                       "amb_uk2us": sum(1 for p in pairs if p["dir"] == "uk2us"), "pron_differs_active": sum(1 for p in pairs if p["pron_differs"]),
                       "excluded": len(excl), "rule_new": n_rule_new, "rule_upgrade_T2": n_rule_up}}
    return {"meta": meta, "pairs": pairs, "inactive_T2_uk_us_level_dir": inactive, "excluded": excl}


def review_md(res) -> str:
    """PAIRS_REVIEW_01.md の本文(除外理由付き)。レビュー観点別に全件を出す。"""
    P = res["pairs"]
    ex = res["excluded"]
    m = res["meta"]["counts"]
    L = ["# PAIRS_REVIEW_01 -- 固定対表(er111_ukus_pairs_v1.json)の人手レビュー結果(自動生成: er111_ukus_pairs_build_01.py --review-md)", "",
         f"- 件数: {json.dumps(m, ensure_ascii=False)}",
         "- 入力: VarCon 2020.12.07 / SCOWL 2020.12.07 (許諾文は json 冒頭 meta.license。breame不採用)。UK側=B/Zタグ(x/-なし)でA第一推奨でない語、US側=A第一推奨(OF-03)。",
         "- レビュー観点: (a)編集距離>2/短語/語頭相違 (b)CMU両側登録で音素が異なる (c)両形が高頻度独立語 (d)AMB(用法付き)全件 (e)OF-04自動検出 (f)UK側定義拡張(Bv/B.)で増えた約430対 (g)規則(SCOWL固定)出力。",
         "- レビュー者: 実装担当(Sonnet)。除外はすべて下表の理由付き。判断が割れるものは安全側(除外=従来どおりNG)。", "",
         f"## 1. 除外({len(ex)}件)", "", "| UK形 | US形 | 理由 | level |", "|---|---|---|---|"]
    for e in sorted(ex, key=lambda x: (x["reason"], x["uk"])):
        L.append(f"| {e['uk']} | {e['us']} | {e['reason']}{(' / '+e['cmu']) if e.get('cmu') else ''} | {e.get('level','')} |")
    amb = [p for p in P if p["dir"] == "uk2us" and not p["uk"].endswith("'s")]
    L += ["", f"## 2. AMB(一方向=canonical UK形 -> ASR US形のみ。{len(amb)}件、'sを除く)", "", "| UK形 | US形 | 用法/理由 | pron_differs |", "|---|---|---|---|"]
    for p in sorted(amb, key=lambda x: x["uk"]):
        L.append(f"| {p['uk']} | {p['us']} | {p.get('usage') or ''} | {p['pron_differs']} |")
    pdp = [p for p in P if p["pron_differs"] and not p["uk"].endswith("'s")]
    L += ["", f"## 3. 発音も違う対(pron_differs=True。OF-06: 監査記録・件数監視。{len(pdp)}件)", "", "| UK形 | US形 | dir | cmu_dist |", "|---|---|---|---|"]
    for p in sorted(pdp, key=lambda x: x["uk"]):
        L.append(f"| {p['uk']} | {p['us']} | {p['dir']} | {p['cmu_dist']} |")
    fl = []
    for p in P:
        if p["uk"].endswith("'s"):
            continue
        d = lev(p["uk"], p["us"])
        why = []
        if d > 2:
            why.append(f"lev{d}")
        if min(len(p["uk"]), len(p["us"])) <= 3:
            why.append("short")
        if p["uk"][:1] != p["us"][:1]:
            why.append("first")
        if why:
            fl.append((p["uk"], p["us"], ",".join(why)))
    L += ["", f"## 4. 採用(active)のうち観点(a)に該当し、レビューの結果『採用』としたもの({len(fl)}件。外したものは1.の理由付きdenylist)", "", "| UK形 | US形 | 該当 |", "|---|---|---|"]
    for u, a, w in sorted(fl):
        L.append(f"| {u} | {a} | {w} |")
    L += ["", "## 5. 規則(OF-08: SCOWL固定)", "", f"- 規則適用: 変換前=SCOWL英国語専用語、変換後=SCOWL米国語/共通語 level<=70、stem>=4。新規対 {m['rule_new']} 件(=VarConに無い対は生成されない)、Tier-2->R昇格 {m['rule_upgrade_T2']} 件。",
          "- Tier-2(level71-99)は active=False(初回Trialでは非同値)。件数: " + str(m["T2_inactive"]), ""]
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--review-md", default=None)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args()
    res = build()
    print(json.dumps(res["meta"]["counts"], ensure_ascii=False))
    if a.review_md:
        with open(a.review_md, "w", encoding="utf-8", newline="\n") as f:
            f.write(review_md(res))
        print("wrote", a.review_md)
    if a.write:
        with open(a.out, "w", encoding="utf-8", newline="\n") as f:
            json.dump(res, f, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        print("wrote", a.out, os.path.getsize(a.out))
