# -*- coding: utf-8 -*-
"""FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01 eval v02(委任_02b、Trial専用、API 0)。

TRIAL_DESIGN_01.md §3-v02 の機械評価。閾値は criteria_thresholds_01.json(v02)から読む(ハードコードしない)。
- 主要指標=本番判定のflip(Primary-NG wavで、ベースライン=pl_unspecified対重みwの NG→PASS系 / PASS→NG)。2 role条件
  (FULL_STORY=Tier3あり / Tier3なし=segment_id None)でProduction判定(judge adapter、無変更)に注入。
- 副指標: Melos正認識率、他語perturbation(M-5)、負例の誤PASS・誤Melos(rule of three併記)、境界例(別枠)、決定論抜き打ち、
  S-8の5分類フラグ。raw全行を対象(除外ロジックなし。errは別集計)。録音2(Phase A)は参考値で確認集計から除外。
"""
import argparse
import collections
import difflib
import hashlib
import json
import math
import os
import re
import sys

import er084_azure_phraselist_weight_trial_01_lib as L
import er084_azure_phraselist_weight_trial_01_eval_ext as X

ROLES = ("full_story", "no_tier3")
STOPWORDS = set("""a an the of to in on onto unto at and but or nor so yet he she it they we you i me him her them us his hers its their
our your my was were is are be been being am had has have do does did with without for from by as that which who whom this these those
there here then than if when while where what how why not no into over under up down out off about around across through toward towards
after before again once just very too also all any each both such more most some can could will would shall should may might must
""".split())
NEG_WORDS = {"not", "no", "never", "none", "nobody", "nothing", "neither", "nor", "cannot", "without", "n't"}
NUM_RE = re.compile(r"^\d+(?:[.,]\d+)?$|^(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|hundred|thousand)$")


# ---------------- 入力 ----------------
def load_meta(m1: dict, m2: dict, prod: dict, primary_rows: list, full_story_seg: str) -> dict:
    prim = {r["audio_id"]: r for r in primary_rows if not r.get("err")}
    boundary = set(m2.get("reclassification", {}).keys())
    meta = {}

    def put(a, set_name, primary_text, primary_model, seg):
        meta[a["id"]] = {"id": a["id"], "set": set_name, "label": a.get("label", "positive"), "canonical_text": a["canonical_text"],
                         "text": a.get("text") or a["canonical_text"], "primary_text": primary_text, "primary_model": primary_model,
                         "segment_id": seg, "voice": a.get("voice"), "slow6": bool(a.get("slow6")), "sentence_id": a.get("sentence_id"),
                         "path": a["path"], "duration_s": a.get("duration_s"), "confusable": a.get("confusable"),
                         "ledger_phrases": a.get("ledger_phrases") or ["Melos"], "variant": a.get("variant"),
                         "expected_melos": a.get("expected_melos", len(L.RE_MELOS.findall(a["canonical_text"])))}

    for a in m1["audio"]:
        if a["label"] == "positive":
            sn = "POS_SYN"
        else:
            sn = "NEG_BOUNDARY" if a["sentence_id"] in boundary else "NEG_VALID"
        pr = prim.get(a["id"])
        put(a, sn, pr["text"] if pr else None, pr.get("model", "gpt-4o-mini-transcribe(02a記録。モデル名はrawに無く、route設定を確認)") if pr else None, full_story_seg)
    for a in m2["audio"]:
        pr = prim.get(a["id"])
        put(a, "NEG_MP", pr["text"] if pr else None, pr.get("model") if pr else None, full_story_seg)
    for a in prod["audio"]:
        put(a, "POS_PROD", a["primary_text"], "production_recorded(gpt-4o-mini-transcribe)", a["segment_id"])
    return meta


def azure_rows(rows: list) -> list:
    return [r for r in rows if r.get("phase") == "B"]


# ---------------- 統計 ----------------
def sign_test_p(up: int, down: int) -> float:
    """片側exact符号検定: P(X>=up | n=up+down, p=0.5)。n=0なら1.0。"""
    n = up + down
    if n == 0:
        return 1.0
    return sum(math.comb(n, k) for k in range(up, n + 1)) / (2 ** n)


def rule_of_three_upper(n: int, k: int = 0, numerator: float = 3.0):
    return None if (n <= 0 or k != 0) else numerator / n


# ---------------- 他語perturbation(M-5) ----------------
def _cap_nonfirst(ref_text: str) -> set:
    out = set()
    for sent in re.split(r"(?<=[.!?])\s+", ref_text or ""):
        toks = re.findall(r"[A-Za-z']+", sent)
        for t in toks[1:]:
            if t[0].isupper():
                out.add(t.lower())
    return out


def other_diffs(ref_text: str, hyp_text: str, confusable=None) -> list:
    """ref(原稿)とhyp(Azure転写)の語単位差分のうち、ターゲット語(Melos・誤variant・confusable)を含まないもの。
    各diff: {key,ref,hyp,pos,protected_kinds}。pos=ref内の語位置、melos_dist=Melos位置からの語距離。"""
    r, h = X._tok(ref_text), X._tok(hyp_text)
    tt = X.target_tokens(confusable)
    caps = _cap_nonfirst(ref_text)
    melos_idx = [i for i, t in enumerate(r) if t == "melos" or t in tt]
    out = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, r, h, autojunk=False).get_opcodes():
        if tag == "equal":
            continue
        rs, hs = r[i1:i2], h[j1:j2]
        if any(t in tt for t in rs + hs):
            continue
        kinds = set()
        for t in rs + hs:
            if NUM_RE.match(t):
                kinds.add("number")
            if t in NEG_WORDS:
                kinds.add("negation")
            if t in caps:
                kinds.add("proper_noun")
            if t not in STOPWORDS and not NUM_RE.match(t) and t not in NEG_WORDS:
                kinds.add("content_word")
        dist = min((abs(i1 - m) for m in melos_idx), default=None)
        out.append({"key": f"{' '.join(rs) or '∅'}→{' '.join(hs) or '∅'}", "n_words": max(len(rs), len(hs)), "pos": i1,
                    "protected_kinds": sorted(kinds), "melos_dist": dist})
    return out


def new_errors(base_diffs: list, w_diffs: list) -> dict:
    base_keys = collections.Counter(d["key"] for d in base_diffs)
    new = []
    for d in w_diffs:
        if base_keys.get(d["key"], 0) > 0:
            base_keys[d["key"]] -= 1
        else:
            new.append(d)
    prot = [d for d in new if d["protected_kinds"]]
    return {"n_new_error_words": sum(d["n_words"] for d in new), "n_new_diffs": len(new),
            "n_protected_new_diffs": len(prot), "protected_kinds": sorted({k for d in prot for k in d["protected_kinds"]}),
            "melos_dists": [d["melos_dist"] for d in new if d["melos_dist"] is not None], "new": [d["key"] for d in new]}


# ---------------- 本体 ----------------
def is_pass(state, prefix="PASS") -> bool:
    return bool(state) and str(state).startswith(prefix)


class Evaluator:
    def __init__(self, rows, meta, criteria, judge_fn=None):
        self.rows = azure_rows(rows)
        self.meta = meta
        self.crit = criteria
        self.v = criteria["v02"]
        self.base = criteria["baseline_cond"]
        self.pf = criteria["pass_family_prefix"]
        self._judge = judge_fn or self._default_judge
        self._cache = {}
        # (aid, cond) -> {rep: row}
        self.cells = collections.defaultdict(dict)
        self.n_err = collections.Counter()
        for r in self.rows:
            if r.get("err") or r.get("text") is None:
                self.n_err[(r["audio_id"], r["cond"])] += 1
                continue
            self.cells[(r["audio_id"], r["cond"])][r["rep"]] = r

    @staticmethod
    def _default_judge(canonical, primary, secondary, wav_path, segment_id):
        import er084_azure_phraselist_weight_trial_01_judge as J
        return J.judge_offline(canonical, primary, secondary, wav_path, segment_id=segment_id)

    def role_seg(self, aid, role):
        return self.meta[aid]["segment_id"] if role == "full_story" else None

    def judge(self, aid, text, role):
        m = self.meta[aid]
        k = (aid, text, role)
        if k not in self._cache:
            self._cache[k] = self._judge(m["canonical_text"], m["primary_text"], text, os.path.join(L.ROOT, m["path"]),
                                         self.role_seg(aid, role))
        return self._cache[k]

    def state(self, aid, cond, role, rep=1):
        r = self.cells.get((aid, cond), {}).get(rep)
        if r is None:
            return None
        return self.judge(aid, r["text"], role)["state"]

    def primary_ng(self, aid, role) -> bool:
        m = self.meta[aid]
        if m["primary_text"] is None:
            return False
        j = self.judge(aid, None, role)
        return not is_pass(j["state"], self.pf)

    def unstable(self, aid, cond, role) -> bool:
        c = self.cells.get((aid, cond), {})
        if 1 not in c or 2 not in c:
            return False
        return self.state(aid, cond, role, 1) != self.state(aid, cond, role, 2)

    def has(self, aid, cond):
        return 1 in self.cells.get((aid, cond), {})

    def melos_ok(self, aid, cond):
        r = self.cells.get((aid, cond), {}).get(1)
        if r is None:
            return None
        h = len(L.RE_MELOS.findall(r["text"]))
        e = self.meta[aid]["expected_melos"]
        return h == e and e > 0

    def ids(self, set_names):
        return sorted(a for a, m in self.meta.items() if m["set"] in set_names)

    # ---- flip(主要指標) ----
    def flips(self, role, w, sets=("POS_SYN", "POS_PROD"), base=None):
        base = base or self.base
        up, down, unst, same_ng, same_pass, skipped_pass = [], [], [], [], [], []
        for aid in self.ids(sets):
            if not (self.has(aid, base) and self.has(aid, w)):
                continue
            if not self.primary_ng(aid, role):
                skipped_pass.append(aid)
                continue
            if self.unstable(aid, base, role) or self.unstable(aid, w, role):
                unst.append(aid)
                continue
            sb, sw = self.state(aid, base, role), self.state(aid, w, role)
            pb, pw = is_pass(sb, self.pf), is_pass(sw, self.pf)
            if not pb and pw:
                up.append(aid)
            elif pb and not pw:
                down.append(aid)
            elif pb:
                same_pass.append(aid)
            else:
                same_ng.append(aid)
        return {"up": up, "down": down, "unstable": unst, "same_ng": same_ng, "same_pass": same_pass,
                "primary_pass_excluded": skipped_pass}

    def cluster(self, aid):
        m = self.meta[aid]
        return (m["sentence_id"], m["voice"], m["slow6"])

    def R(self, role="full_story"):
        n = 0
        ids = []
        for aid in self.ids(("POS_SYN", "POS_PROD")):
            if self.has(aid, self.base) and self.primary_ng(aid, role) and not is_pass(self.state(aid, self.base, role), self.pf):
                n += 1
                ids.append(aid)
        return n, ids

    # ---- 負例 ----
    def negatives(self, sets, conds):
        out = {}
        for role in ROLES:
            for c in conds:
                ids = [a for a in self.ids(sets) if self.has(a, c)]
                fp = [a for a in ids if is_pass(self.state(a, c, role), self.pf)]
                out[(role, c)] = {"n": len(ids), "false_pass": len(fp), "false_pass_ids": fp}
        fm = {}
        for c in conds:
            ids = [a for a in self.ids(sets) if self.has(a, c)]
            hit = [a for a in ids if len(L.RE_MELOS.findall(self.cells[(a, c)][1]["text"])) > 0]
            fm[c] = {"n": len(ids), "false_melos": len(hit), "false_melos_ids": hit}
        return out, fm

    # ---- 副作用 perturbation ----
    def perturbation(self, w):
        rows = []
        for aid, m in sorted(self.meta.items()):
            if not (self.has(aid, self.base) and self.has(aid, w)):
                continue
            ref = m["text"]
            bd = other_diffs(ref, self.cells[(aid, self.base)][1]["text"], m["confusable"])
            wd = other_diffs(ref, self.cells[(aid, w)][1]["text"], m["confusable"])
            ne = new_errors(bd, wd)
            rows.append({"audio_id": aid, "set": m["set"], "cond": w, **ne})
        return rows

    # ---- 判定 ----
    def weight_eval(self, w, alpha):
        v, crit = self.v, self.crit
        res = {"cond": w, "alpha": alpha, "roles": {}}
        Rn, Rids = self.R("full_story")
        res["R"], res["R_ids"] = Rn, Rids
        for role in ROLES:
            f = self.flips(role, w)
            up, down = f["up"], f["down"]
            # 悪化: down + (ベースラインMelos正認識→w誤認識でjudge状態は不変のもの)
            melos_degraded = [a for a in self.ids(("POS_SYN", "POS_PROD")) if self.has(a, self.base) and self.has(a, w)
                              and self.melos_ok(a, self.base) and not self.melos_ok(a, w) and a not in down]
            res["roles"][role] = {"up": len(up), "down": len(down), "up_ids": up, "down_ids": down, "unstable": f["unstable"],
                                  "same_ng": len(f["same_ng"]), "same_pass": len(f["same_pass"]),
                                  "primary_pass_excluded": len(f["primary_pass_excluded"]),
                                  "melos_degraded_extra": melos_degraded, "p_sign": sign_test_p(len(up), len(down))}
        f = res["roles"]["full_story"]
        up_ids = f["up_ids"]
        clusters = {self.cluster(a) for a in up_ids}
        vs = {(self.meta[a]["voice"], self.meta[a]["slow6"]) for a in up_ids}
        ctx = {self.meta[a]["sentence_id"] for a in up_ids}
        # 副作用: 有効負例(NEG_VALID + NEG_MP)
        negs, fm = self.negatives(("NEG_VALID", "NEG_MP"), [self.base, w])
        neg_inc = {role: negs[(role, w)]["false_pass"] - negs[(role, self.base)]["false_pass"] for role in ROLES}
        fm_inc = fm[w]["false_melos"] - fm[self.base]["false_melos"]
        degraded = len(f["down_ids"]) + len(f["melos_degraded_extra"])
        c = {}
        c["1_identifiable"] = Rn >= crit["min_R_for_identifiability"]
        c["2_effect"] = len(up_ids) >= crit["fixed_min_abs"] and len(up_ids) >= crit["fixed_min_fraction_of_R"] * max(Rn, 1)
        c["3_sign_test"] = f["p_sign"] <= alpha
        c["4_spread"] = len(clusters) >= v["min_clusters"] and len(vs) >= crit["min_voice_speed_conditions"]
        c["5_no_side_effect"] = all(neg_inc[r] <= crit["negative_false_melos_increase_max"] for r in ROLES) and fm_inc <= crit["negative_false_melos_increase_max"]
        c["6_no_degradation"] = degraded <= crit["degraded_max_abs"] and (degraded < crit["degraded_fraction_of_fixed_exclusive_upper"] * len(up_ids) if up_ids else degraded == 0)
        c["7_tier3less_not_reversed"] = (res["roles"]["no_tier3"]["down"] <= res["roles"]["no_tier3"]["up"]) if v["secondary_role_down_le_up"] else True
        if not c["1_identifiable"]:
            status = "INCONCLUSIVE"
        elif not c["2_effect"]:
            status = "REJECTED"
        elif not c["3_sign_test"]:
            status = "INCONCLUSIVE"
        elif all(c[k] for k in ("4_spread", "5_no_side_effect", "6_no_degradation", "7_tier3less_not_reversed")):
            status = "VALIDATED候補"
        else:
            status = "判断候補"
        res.update({"criteria": c, "status": status, "n_clusters_up": len(clusters), "n_contexts_up": len(ctx),
                    "n_voice_speed_up": len(vs), "neg_false_pass_increase": neg_inc, "neg_false_melos_increase": fm_inc,
                    "degraded_total": degraded, "negatives_detail": {f"{k[0]}|{k[1]}": v_ for k, v_ in negs.items()},
                    "false_melos_detail": fm})
        return res

    def overall(self):
        v = self.v
        res = {"R": None, "weights": {}}
        for w, alpha in ((v["primary_weight_cond"], v["alpha_primary"]), (v["secondary_weight_cond"], v["alpha_secondary"])):
            res["weights"][w] = self.weight_eval(w, alpha)
            res["R"] = res["weights"][w]["R"]
        p = res["weights"][v["primary_weight_cond"]]["status"]
        s = res["weights"][v["secondary_weight_cond"]]
        if p == "VALIDATED候補":
            status = "VALIDATED候補"
        elif s["status"] == "VALIDATED候補" and p != "REJECTED":
            status = "判断候補"
            res["note"] = "主たる重み1.5は基準未達、副2.0がα/2基準で全達成(2.0のみ)"
        else:
            status = p
        res["status"] = status
        return res

    # ---- 副指標 ----
    def melos_rates(self):
        out = {}
        for sets, label in ((("POS_SYN",), "正例(合成30)"), (("POS_PROD",), "正例(本番take20)"), (("POS_SYN", "POS_PROD"), "正例(合算50)")):
            ids = self.ids(sets)
            for c in ("no_pl", "pl_unspecified", "pl_w1.5", "pl_w2.0"):
                n = sum(1 for a in ids if self.has(a, c))
                k = sum(1 for a in ids if self.has(a, c) and self.melos_ok(a, c))
                out[(label, c)] = {"n": n, "melos_ok": k, "rate": (k / n) if n else None}
        return out

    def melos_breakdown(self):
        """文脈別・Voice/話速別・文長別のMelos正認識率(副指標、rep1、正例のみ)。"""
        conds = ("no_pl", "pl_unspecified", "pl_w1.5", "pl_w2.0")
        groups = collections.OrderedDict()

        def add(label, aid):
            groups.setdefault(label, []).append(aid)

        for aid in self.ids(("POS_SYN",)):
            m = self.meta[aid]
            add("合成/文脈=" + str(m["sentence_id"]), aid)
            add("合成/Voice話速=" + f"{m['voice']}{'+減速' if m['slow6'] else ''}", aid)
        for aid in self.ids(("POS_PROD",)):
            m = self.meta[aid]
            add("本番take/長さ=" + ("≤5秒" if m["duration_s"] <= 5 else "5〜15秒" if m["duration_s"] <= 15 else ">15秒"), aid)
            add("本番take/segment=" + str(m["segment_id"]).split("_c")[0], aid)
        out = collections.OrderedDict()
        for label, ids in groups.items():
            row = {"n": len(ids)}
            for c in conds:
                have = [a for a in ids if self.has(a, c)]
                row[c] = sum(1 for a in have if self.melos_ok(a, c))
            out[label] = row
        return out

    def determinism(self):
        """抜き打ち: rep2とrep1のAzure転写一致率(条件別)。pl_unspecified vs pl_w1.0(送信同一)の転写一致率。"""
        det = collections.OrderedDict()
        for c in ("no_pl", "pl_unspecified", "pl_w1.0", "pl_w1.5", "pl_w2.0"):
            pairs = [(a, cc) for (a, cc), d in self.cells.items() if cc == c and 1 in d and 2 in d]
            same = [a for a, _ in pairs if self.cells[(a, c)][1]["text"] == self.cells[(a, c)][2]["text"]]
            det[c] = {"n_pairs": len(pairs), "identical": len(same), "differing": [a for a, _ in pairs if a not in same]}
        eq = []
        for (a, c), d in self.cells.items():
            if c == "pl_w1.0" and 1 in d and (a, "pl_unspecified") in self.cells and 1 in self.cells[(a, "pl_unspecified")]:
                eq.append((a, d[1]["text"] == self.cells[(a, "pl_unspecified")][1]["text"]))
        return det, {"n": len(eq), "identical": sum(1 for _, ok in eq if ok), "differing": [a for a, ok in eq if not ok]}

    def transcript_change_rate(self, w, sets=("POS_SYN", "POS_PROD", "NEG_VALID", "NEG_MP"), base_cond=None):
        b = base_cond or self.base
        ids = [a for a in self.ids(sets) if self.has(a, w) and self.has(a, b)]
        ch = [a for a in ids if self.cells[(a, w)][1]["text"] != self.cells[(a, b)][1]["text"]]
        return {"n": len(ids), "changed": len(ch), "rate": (len(ch) / len(ids)) if ids else None}

    def boundary(self):
        out = {}
        for c in ("no_pl", "pl_unspecified", "pl_w1.5", "pl_w2.0"):
            for role in ROLES:
                ids = [a for a in self.ids(("NEG_BOUNDARY",)) if self.has(a, c)]
                out[(role, c)] = {"n": len(ids), "pass": [a for a in ids if is_pass(self.state(a, c, role), self.pf)],
                                  "melos": [a for a in ids if len(L.RE_MELOS.findall(self.cells[(a, c)][1]["text"])) > 0]}
        return out

    def diagnosis(self, ov):
        d = self.v["diagnosis"]
        role = "full_story"
        pos = [a for a in self.ids(("POS_SYN", "POS_PROD")) if self.has(a, self.base) and self.primary_ng(a, role)]
        base_pass = [a for a in pos if is_pass(self.state(a, self.base, role), self.pf)]
        frac_base_pass = (len(base_pass) / len(pos)) if pos else None
        # no_pl vs pl_unspecified の差
        nopl_pass = [a for a in pos if self.has(a, "no_pl") and is_pass(self.state(a, "no_pl", role), self.pf)]
        out = {"primary_ng_positive_wavs": len(pos), "baseline_pass_fraction_among_primary_ng": frac_base_pass,
               "no_pl_pass": len(nopl_pass), "pl_unspecified_pass": len(base_pass)}
        w15, w20 = ov["weights"]["pl_w1.5"], ov["weights"]["pl_w2.0"]
        tc15, tc20 = self.transcript_change_rate("pl_w1.5"), self.transcript_change_rate("pl_w2.0")
        Rn_, Rids_ = self.R(role)
        # 事前登録文(設計書§3-v02 S-8 e)「R大かつw2.0でもNGが大半」= R(ベースラインNGのPrimary-NG正例)のうちw2.0でもNGのままの割合
        resid = [a for a in Rids_ if self.has(a, "pl_w2.0") and not is_pass(self.state(a, "pl_w2.0", role), self.pf)]
        out["transcript_change_rate_w1.5"], out["transcript_change_rate_w2.0"] = tc15, tc20
        out["residual_ng_after_w2.0"] = {"n": len(resid), "of_R": len(Rids_), "fraction": (len(resid) / len(Rids_)) if Rids_ else None}
        out["transcript_change_rate_pl_unspecified_vs_no_pl"] = self.transcript_change_rate(self.base, base_cond="no_pl")
        # 上位cluster集中(w1.5 up)
        upc = collections.Counter(self.cluster(a) for a in w15["roles"][role]["up_ids"])
        top_share = (upc.most_common(1)[0][1] / sum(upc.values())) if upc else None
        out["w1.5_up_top_cluster_share"] = top_share
        flags = {}
        flags["a_条件が簡単すぎた"] = bool(ov["R"] is not None and ov["R"] < self.crit["min_R_for_identifiability"]) or (
            frac_base_pass is not None and frac_base_pass >= d["a_too_easy_baseline_pass_fraction_min"])
        flags["b_PLが効いていない"] = bool(tc15["rate"] is not None and tc20["rate"] is not None
                                       and tc15["rate"] <= d["b_pl_not_effective_transcript_change_fraction_max"]
                                       and tc20["rate"] <= d["b_pl_not_effective_transcript_change_fraction_max"])
        flags["c_1.0(現行)で既に十分"] = bool(frac_base_pass is not None and frac_base_pass >= d["c_already_enough_baseline_pass_fraction_min"]
                                         and w15["roles"][role]["up"] <= max(self.crit["fixed_min_abs"] - 1, 0))
        flags["d_文脈・音声品質で変わる"] = bool(top_share is not None and top_share >= d["d_context_dependent_top_cluster_share_min"]
                                           and w15["roles"][role]["up"] >= 2) or (
            w15["roles"][role]["up"] != w15["roles"]["no_tier3"]["up"])
        flags["e_重みでは解決できない"] = bool(out["residual_ng_after_w2.0"]["fraction"] is not None
                                          and out["residual_ng_after_w2.0"]["fraction"] >= d["e_not_solved_by_weight_residual_ng_fraction_min"]
                                          and ov["R"] is not None and ov["R"] >= self.crit["min_R_for_identifiability"])
        out["flags"] = flags
        return out


# ---------------- レポート ----------------
def pct(x):
    return "-" if x is None else f"{100 * x:.0f}%"


def render_md(ev: Evaluator, ov: dict, extra: dict) -> str:
    L_ = ["# PHASE_B_RESULT_01 — Azure PhraseList重み比較 Phase B結果(自動生成: eval_v02、raw全行・除外なし)", "",
          f"eval機械判定: **{ov['status']}**(Fable最終ラベル前。到達上限Status=`PLW_TRIAL_CLOSEOUT_PENDING_FABLE`)  /  R(FULL_STORY role、Primary-NGかつベースラインNGの正例)= **{ov['R']}**"]
    if ov.get("note"):
        L_.append(f"注記: {ov['note']}")
    L_ += ["", f"Azure raw行数(Phase B)= {len(ev.rows)}、err行={sum(ev.n_err.values())}(別集計、母数から除外)。使用: Azure en-US(SDK 1.50.0、連続認識、`PhraseListGrammar`+`setWeight`)、Primary=OpenAI `gpt-4o-mini-transcribe`(prompt無し、本番同一関数)、TTS=`gemini-3.8-flash-lite-tts`(最新世代flash-lite、Production同一)。", "",
           "## 1 本番判定のflip(主要指標)", "",
           "| 重み | role | Primary-NG正例のうち up(NG→PASS系) | down(PASS→NG) | 変化なしNG | 変化なしPASS | 不安定(除外) | Primary PASS(除外) | 片側符号検定p | α |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    for w, we in ov["weights"].items():
        for role in ROLES:
            r = we["roles"][role]
            L_.append(f"| {w} | {role} | {r['up']} | {r['down']} | {r['same_ng']} | {r['same_pass']} | {len(r['unstable'])} | {r['primary_pass_excluded']} | {r['p_sign']:.4f} | {we['alpha']} |")
    L_ += ["", "## 2 判定基準(§3-v02)と機械判定", "",
           "| 重み | 1識別力(R≥6) | 2効果量 | 3符号検定 | 4広がり | 5副作用なし | 6悪化なし | 7 Tier3なし非逆転 | 状態 | up cluster数 / Voice話速数 |", "|---|---|---|---|---|---|---|---|---|---|"]
    for w, we in ov["weights"].items():
        c = we["criteria"]
        L_.append(f"| {w} | {c['1_identifiable']} | {c['2_effect']} | {c['3_sign_test']} | {c['4_spread']} | {c['5_no_side_effect']} | {c['6_no_degradation']} | {c['7_tier3less_not_reversed']} | **{we['status']}** | {we['n_clusters_up']} / {we['n_voice_speed_up']} |")
    L_ += ["", "up wav(FULL_STORY role):"]
    for w, we in ov["weights"].items():
        L_.append(f"- {w}: up={we['roles']['full_story']['up_ids']} / down={we['roles']['full_story']['down_ids']} / melos_degraded_extra={we['roles']['full_story']['melos_degraded_extra']}")
    L_ += ["", "## 3 副指標: Melos正認識率(wav単位、rep1)", "", "| 集合 | 条件 | Melos正認識/n | 率 |", "|---|---|---|---|"]
    for (lab, c), v in extra["melos_rates"].items():
        L_.append(f"| {lab} | {c} | {v['melos_ok']}/{v['n']} | {pct(v['rate'])} |")
    L_ += ["", "### 3b 文脈別・Voice/話速別・長さ別のMelos正認識数(rep1。n中の正認識wav数)", "",
           "| グループ | n | no_pl | pl_unspecified | pl_w1.5 | pl_w2.0 |", "|---|---|---|---|---|---|"]
    for lab, v in extra["melos_breakdown"].items():
        L_.append(f"| {lab} | {v['n']} | {v['no_pl']} | {v['pl_unspecified']} | {v['pl_w1.5']} | {v['pl_w2.0']} |")
    L_ += ["", "## 4 負例(誤PASS・誤Melos)と境界例", "",
           f"有効負例=N1・N3の6wav+minimal pair 27wav={len(ev.ids(('NEG_VALID','NEG_MP')))}wav。rule of three(0件のとき95%上限≈3/n)を併記。", "",
           "| 条件 | role | n | 誤PASS(canonical=Melos文を注入した本番判定がPASS系) | 誤PASS率 | 0件のとき95%上限(3/n) |", "|---|---|---|---|---|---|"]
    for w, we in ov["weights"].items():
        pass
    negs, fm = ev.negatives(("NEG_VALID", "NEG_MP"), ["no_pl", "pl_unspecified", "pl_w1.5", "pl_w2.0"])
    for (role, c), v in negs.items():
        r3 = rule_of_three_upper(v["n"], v["false_pass"], ev.v["rule_of_three_numerator"])
        L_.append(f"| {c} | {role} | {v['n']} | {v['false_pass']} {v['false_pass_ids']} | {pct(v['false_pass']/v['n']) if v['n'] else '-'} | {pct(r3)} |")
    L_ += ["", "| 条件 | n | Azure誤`Melos`(Melosと出力) | 率 | 0件のとき95%上限 |", "|---|---|---|---|---|"]
    for c, v in fm.items():
        r3 = rule_of_three_upper(v["n"], v["false_melos"], ev.v["rule_of_three_numerator"])
        L_.append(f"| {c} | {v['n']} | {v['false_melos']} {v['false_melos_ids']} | {pct(v['false_melos']/v['n']) if v['n'] else '-'} | {pct(r3)} |")
    L_ += ["", "### 境界例(N2 mellows / N4 Milos。判定には使わず別枠)", "", "| role | 条件 | n | 本番判定PASS系 | Azureが`Melos`と出力 |", "|---|---|---|---|---|"]
    for (role, c), v in extra["boundary"].items():
        L_.append(f"| {role} | {c} | {v['n']} | {v['pass']} | {v['melos']} |")
    L_ += ["", "### 重みが新たに作った誤PASS(ベースラインNG→重みwでPASS系、有効負例。FULL_STORY role)", "",
           "| 重み | wav | TTSに渡した文 | Primary転写 | ベースラインAzure | 重みwのAzure |", "|---|---|---|---|---|---|"]
    for w, d_ in extra["new_false_pass"].items():
        for r in d_["full_story"]:
            L_.append(f"| {w} | {r['audio_id']} | {r['spoken_text']} | {r['primary']} | {r['baseline_azure']} | {r['w_azure']} |")
    L_ += ["", "### 参考: PhraseList自体(現行の重み未指定)の価値 = no_pl → pl_unspecified の本番判定flip", "",
           "| role | up(NG→PASS系) | down | 変化なしNG | 変化なしPASS | 不安定 | Primary PASS(除外) |", "|---|---|---|---|---|---|---|"]
    for role, v in extra["pl_value_no_pl_to_unspecified"].items():
        L_.append(f"| {role} | {v['up']} | {v['down']} | {v['same_ng']} | {v['same_pass']} | {v['unstable']} | {v['primary_pass_excluded']} |")
    L_.append(f"有効負例の誤PASS(no_pl→pl_unspecified): {extra['neg_false_pass_no_pl_vs_unspecified']}")
    L_ += ["", "## 5 他語perturbation(副作用、M-5)", "", "| 重み | 比較wav数 | 新規誤り語数合計 | うち保護対象diff数 | 保護種別 | Melosからの平均語距離 |", "|---|---|---|---|---|---|"]
    for w, rows_ in extra["perturbation"].items():
        n_new = sum(r["n_new_error_words"] for r in rows_)
        n_prot = sum(r["n_protected_new_diffs"] for r in rows_)
        kinds = sorted({k for r in rows_ for k in r["protected_kinds"]})
        ds = [d for r in rows_ for d in r["melos_dists"]]
        L_.append(f"| {w} | {len(rows_)} | {n_new} | {n_prot} | {kinds} | {('%.1f' % (sum(ds)/len(ds))) if ds else '-'} |")
    L_ += ["", "## 6 決定論の抜き打ち(S-2)", "", "| 条件 | rep1/rep2ペア数 | 転写一致 | 不一致wav |", "|---|---|---|---|"]
    for c, v in extra["determinism"][0].items():
        L_.append(f"| {c} | {v['n_pairs']} | {v['identical']} | {v['differing']} |")
    e = extra["determinism"][1]
    L_.append(f"\n`pl_w1.0` vs `pl_unspecified`(送信バイト同一): {e['identical']}/{e['n']}転写一致、不一致={e['differing']}")
    L_ += ["", "## 7 5分類(S-8)の機械フラグ", "", "```json", json.dumps(extra["diagnosis"], ensure_ascii=False, indent=1, default=str), "```", "",
           "## 8 flipしたwavの転写(試聴ページと対応)", ""]
    for w, we in ov["weights"].items():
        for role in ROLES:
            for a in we["roles"][role]["up_ids"] + we["roles"][role]["down_ids"]:
                m = ev.meta[a]
                L_.append(f"- {w}/{role}/{'up' if a in we['roles'][role]['up_ids'] else 'down'} `{a}`: 原稿=`{m['canonical_text'][:70]}` Primary=`{(m['primary_text'] or '')[:70]}` ベースラインAzure=`{ev.cells[(a, ev.base)][1]['text'][:70]}` w=`{ev.cells[(a, w)][1]['text'][:70]}`")
    return "\n".join(L_) + "\n"


def new_false_pass(ev: "Evaluator", w: str, role: str) -> list:
    """有効負例(NEG_VALID+NEG_MP)のうち、ベースラインNG→重みwでPASS系になった(=重みが新たに作った誤PASS)wavと転写。"""
    out = []
    for a in ev.ids(("NEG_VALID", "NEG_MP")):
        if ev.has(a, ev.base) and ev.has(a, w) and not is_pass(ev.state(a, ev.base, role), ev.pf) and is_pass(ev.state(a, w, role), ev.pf):
            out.append({"audio_id": a, "primary": ev.meta[a]["primary_text"], "baseline_azure": ev.cells[(a, ev.base)][1]["text"],
                        "w_azure": ev.cells[(a, w)][1]["text"], "spoken_text": ev.meta[a]["text"]})
    return out


def run_eval(rows, meta, criteria, judge_fn=None):
    ev = Evaluator(rows, meta, criteria, judge_fn)
    ov = ev.overall()
    pl_value = {}
    for role in ROLES:
        f = ev.flips(role, ev.base, base="no_pl")
        pl_value[role] = {k: (len(v) if isinstance(v, list) else v) for k, v in f.items()}
        pl_value[role]["up_ids"] = f["up"]
    negs_pl, fm_pl = ev.negatives(("NEG_VALID", "NEG_MP"), ["no_pl", ev.base])
    extra = {"melos_rates": ev.melos_rates(), "boundary": ev.boundary(),
             "pl_value_no_pl_to_unspecified": pl_value,
             "neg_false_pass_no_pl_vs_unspecified": {f"{k[0]}|{k[1]}": v["false_pass"] for k, v in negs_pl.items()},
             "new_false_pass": {w: {role: new_false_pass(ev, w, role) for role in ROLES} for w in ("pl_w1.5", "pl_w2.0")},
             "perturbation": {w: ev.perturbation(w) for w in ("pl_w1.5", "pl_w2.0", "no_pl")},
             "determinism": ev.determinism(), "diagnosis": ev.diagnosis(ov), "melos_breakdown": ev.melos_breakdown()}
    return ev, ov, extra


def _jsonable(o):
    if isinstance(o, dict):
        return {(k if isinstance(k, str) else "|".join(map(str, k))): _jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_jsonable(x) for x in o]
    return o


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    ap.add_argument("--primary", required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--manifest2", required=True)
    ap.add_argument("--production-takes", required=True)
    ap.add_argument("--thresholds", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    import er084_azure_phraselist_weight_trial_01_judge as J
    crit = json.load(open(a.thresholds, encoding="utf-8"))
    rows = L.read_raw(a.raw)
    meta = load_meta(json.load(open(a.manifest, encoding="utf-8")), json.load(open(a.manifest2, encoding="utf-8")),
                     json.load(open(a.production_takes, encoding="utf-8")), L.read_raw(a.primary), J.ROLE_FULL_STORY_SEGMENT)
    ev, ov, extra = run_eval(rows, meta, crit)
    open(a.out, "w", encoding="utf-8").write(render_md(ev, ov, extra))
    json.dump(_jsonable({"overall": ov, "extra": extra}), open(os.path.splitext(a.out)[0] + ".json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1, default=str)
    print(f"status={ov['status']} R={ov['R']} rows={len(ev.rows)} -> {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
