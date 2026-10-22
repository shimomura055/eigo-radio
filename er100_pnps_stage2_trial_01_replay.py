# -*- coding: utf-8 -*-
"""保存音声のASR転写への新方式(Trial内比較のみ)のreplay。0円。Production判定は変更しない/importしない(CMU取得はpronouncingのみ)。
arm: V4=独立2推定(E2 G2P ∩ E3 LLM)の共通部分 / EXT=V4 + 取得根拠(許可リストA・媒体2件一致・単一サイト+推定1つ一致) / DIAG_UNION=全候補の和集合(誤PASS余力の診断のみ)。"""
import itertools, json, os, re, sys
sys.path.insert(0, os.getcwd())
from urllib.parse import urlparse
from er100_pnps_stage2_trial_01_common import *
from er006_m1_multi_candidate_01 import default_cmu

A_ALLOW = ("wikipedia.org", "wiktionary.org", "dictionary.cambridge.org")
IDENTITY = {   # 人手の根拠付き同定注記(対象の固有名詞を指すか)
    "meink": ("CONFIRMED", "en.wikipedia.org/wiki/Troy_Meink=米空軍長官Troy Meink本人の記事。HR記事(space_weapons)の文脈と同一人物"),
    "altuzarra": ("CONFIRMED_BRAND", "媒体ガイド4件(BI/Nylon/Elle AU/HerWorld)がブランド/デザイナー名Altuzarraの読みとして記載"),
    "khaite": ("CONFIRMED_BRAND", "Nylon発音ガイドがラグジュアリーブランドKhaiteの読みとして記載(1媒体のみ)"),
    "canele": ("SPELLING_ONLY_DICT_SITE", "youpronounce.it(辞書サイト、許可リスト外)のcanelé(菓子)英語読み。1サイト"),
    "melos": ("NOT_CONFIRMED_SAME_ENTITY", "Cambridge/dictionary.com=普通名詞melos、Wikipedia Milos=島。『走れメロス』の登場人物Melosと同一とは確認できない"),
    "toteme": ("NONE", "取得できず"), "zabelina": ("NONE", "取得できず(人物の発音を示す出典なし)")}


def strip_st(seq):
    return tuple(re.sub(r"\d", "", p) for p in seq)


def first_class(seq):
    v = {"AA", "AE", "AH", "AO", "AW", "AY", "EH", "ER", "EY", "IH", "IY", "OW", "OY", "UH", "UW"}
    return "V" if seq[0] in v else seq[0]


def load():
    pop = json.load(open(f"{OUT}/o0_population.json", encoding="utf-8"))
    wh = json.load(open(f"{OUT}/o0_whisper.json", encoding="utf-8"))
    est = json.load(open(f"{OUT}/est_e2_e3.json", encoding="utf-8"))
    r0 = json.load(open(f"{OUT}/r0_extractions.json", encoding="utf-8"))
    return pop, wh, est, r0


def build_sets(est, r0):
    sets = {}
    for w in TARGETS:
        e2 = {tuple(est[w]["E2_g2p_en"])}
        e3 = {tuple(c["arpa"]) for c in est[w]["E3_candidates"]}
        rej, ret = [], []
        for pg in r0.get(w, []):
            for e in pg.get("extractions", []) or []:
                if not e["arpa"]:
                    if e["type"] in ("ipa", "respelling", "caps_respelling"):
                        rej.append({"url": pg["url"], "raw": e["raw"], "why": "ARPA変換不可"})
                    continue
                a = strip_st(e["arpa"])
                if e["type"] == "ipa" and len(a) < 3:
                    rej.append({"url": pg["url"], "raw": e["raw"], "why": "短すぎる/無関係IPA"}); continue
                if first_class(a) != first_class(next(iter(e2))):
                    rej.append({"url": pg["url"], "raw": e["raw"], "why": "語頭音がG2P推定と異なる=別語の可能性(抽出誤り)"}); continue
                ret.append({"url": pg["url"], "domain": urlparse(pg["url"]).netloc.replace("www.", ""), "type": e["type"], "raw": e["raw"], "arpa": a, "context": e["context"]})
        seen, ret2 = set(), []
        for x in sorted(ret, key=lambda x: (x["type"] != "caps_respelling")):
            k = (x["domain"], x["arpa"])
            if k in seen:
                continue
            if x["type"] == "ipa" and any(y["domain"] == x["domain"] and y["type"] == "caps_respelling" for y in ret):
                continue
            seen.add(k); ret2.append(x)
        sets[w] = {"E2": e2, "E3": e3, "retrieved": ret2, "rejected": rej}
    return sets


def accepted(w, S):
    e2, e3, ret = S["E2"], S["E3"], S["retrieved"]
    v4 = e2 & e3
    tierA = {x["arpa"] for x in ret if x["domain"].endswith(A_ALLOW) and IDENTITY[w][0] == "CONFIRMED"}
    by_arpa = {}
    for x in ret:
        by_arpa.setdefault(x["arpa"], set()).add(x["domain"])
    media = {a for a, d in by_arpa.items() if len(d) >= 2 and IDENTITY[w][0].startswith("CONFIRMED")}
    single_plus_est = {a for a in by_arpa if (a in e2 or a in e3) and IDENTITY[w][0] != "NOT_CONFIRMED_SAME_ENTITY"}
    # EXT: 取得根拠(許可リストA / 媒体2件以上の一致)があれば取得根拠のみ(推定は上書きされる=推定の共通部分が取得発音と食い違う場合の誤受理を防ぐ)。無ければV4+単一サイト&推定一致
    ext = (tierA | media) if (tierA | media) else (set(v4) | single_plus_est)
    union = set(e2) | set(e3) | set(by_arpa)
    return {"V4": v4, "EXT": ext, "DIAG_UNION": union, "tierA": tierA, "media_consensus": media, "single_plus_est": single_plus_est}


def tok_variants(toks, cap=64):
    vs = []
    for t in toks:
        c = default_cmu(t)
        if not c:
            return None
        vs.append(sorted(set(c)))
    n = 1
    for v in vs:
        n *= len(v)
    if n > cap:
        return None
    return {tuple(x for part in combo for x in part) for combo in itertools.product(*vs)}


def obs_verdict(word, toks, accset):
    if toks is None:
        return "UNALIGNED", ""
    if len(toks) == 1 and toks[0] == word:
        return "EXACT", word
    v = tok_variants(toks)
    if v is None:
        return "OOV", " ".join(toks)
    if v & accset:
        return "MATCH", " ".join(toks)
    return "MISMATCH", " ".join(toks)


def classify_obs(obs, acc_nonempty):
    """区別候補(機械的な候補であり正否の確定ではない)。obs=[(label, string)]"""
    vals = [s for _, s in obs if s]
    if not vals:
        return "不明(整列不能)"
    distinct = set(vals)
    if any(l == "EXACT" for l, _ in obs) and len(distinct) > 1:
        return "ASR誤認識候補(ASR間不一致、正しい綴りを書いたASRもある)"
    if len(distinct) >= 3:
        return "ASR不安定/誤認識候補(3通り以上に割れる)"
    if len(distinct) == 1 and not any(l == "EXACT" for l, _ in obs):
        return "TTS実誤発音の候補(全ASRが同一の別語を出力)" + ("" if acc_nonempty else "。ただし期待発音が未確定のため断定不可")
    return "不明(2通りに割れる)"


def main():
    pop, wh, est, r0 = load()
    rows = load_rows()
    S = build_sets(est, r0)
    A = {w: accepted(w, S[w]) for w in TARGETS}
    last_row = {}
    for t in pop["table"]:
        if t["wav_exists"]:
            last_row[(t["wav_path"], t["word"])] = t["row"]
    by_row = {}
    for t in pop["table"]:
        by_row.setdefault(t["row"], []).append(t)
    detail = []
    for t in pop["table"]:
        w, r = t["word"], t["row"]
        ct = rows[r]["canonical_text"]
        observations = {k: t[k] for k in ("primary_1", "primary_2", "secondary_1", "secondary_2")}
        same_gen = False
        if t["wav_exists"] and last_row.get((t["wav_path"], w)) == r:
            import datetime
            mt = datetime.datetime.fromtimestamp(os.path.getmtime(t["wav_path"]))
            tsd = datetime.datetime.fromisoformat(t["ts"])
            same_gen = abs((mt - tsd).total_seconds()) <= 150   # 保存wavが当該HR事象の世代と推定できる条件
            for sz in ("small", "medium"):
                sp = asr_span(ct, wh[t["wav_path"]][sz], w)
                observations[("whisper_" if same_gen else "whisperREF_") + sz] = sp
        # 保存されたステップに無い観測(None)は空応答ではなく「未観測/整列不能」。Primary/Secondaryが空listのものは"脱落"として扱う
        res = {}
        for arm in ("V4", "EXT", "DIAG_UNION"):
            accset = A[w][arm]
            ob = [(*obs_verdict(w, v, accset), k) for k, v in observations.items() if v is not None]
            labs_prod = [a for a, _, k in ob if not k.startswith("whisperREF")]   # 別世代のWhisper(REF)は判定に使わない
            if not accset:
                v = "HR_MAINTAINED(推定不成立)"
            elif labs_prod and all(l in ("MATCH", "EXACT") for l in labs_prod) and "MATCH" in labs_prod:
                v = "PASS_WITH_WARNING"
            elif "MISMATCH" in labs_prod and "OOV" not in labs_prod:
                v = "NG"
            else:
                v = "HR_MAINTAINED(判定不能: ASR側がCMU未収録/整列不能/混在)"
            res[arm] = {"verdict": v, "obs": ob, "accepted": sorted(" ".join(a) for a in accset)}
        ob_ext = [(a, d) for a, d, _ in res["EXT"]["obs"]]
        t2 = dict(t)
        t2.update(same_generation_audio=same_gen, res=res, observations=observations, distinguish=classify_obs(ob_ext, bool(A[w]["EXT"])))
        detail.append(t2)
    dmap = {(d["row"], d["word"]): d for d in detail}
    summ = {}
    for arm in ("V4", "EXT", "DIAG_UNION"):
        pass_rows, ng_rows, hr_rows = [], [], []
        for r, ts in by_row.items():
            unresolved = set(unresolved_spans(rows[r]))
            my = {t["word"]: dmap[(r, t["word"])]["res"][arm]["verdict"] for t in ts}
            others = unresolved - set(my)
            if not others and all(v == "PASS_WITH_WARNING" for v in my.values()):
                pass_rows.append(r)
            elif any(v == "NG" for v in my.values()):
                ng_rows.append(r)
            else:
                hr_rows.append(r)
        summ[arm] = {"rows_total(HR events)": len(by_row), "PASS_WITH_WARNING_rows": pass_rows, "n_pass": len(pass_rows), "NG_rows": len(ng_rows), "HR_maintained_rows": len(hr_rows),
                     "word_level_pass": sorted({(d["row"], d["word"]) for d in detail if d["res"][arm]["verdict"] == "PASS_WITH_WARNING"}),
                     "word_level_NG": sum(1 for d in detail if d["res"][arm]["verdict"] == "NG"),
                     "word_level_verdicts": {v: sum(1 for d in detail if d["res"][arm]["verdict"] == v) for v in {d["res"][arm]["verdict"] for d in detail}}}
    out = {"accepted_sets": {w: {k: sorted(" ".join(a) for a in v) if isinstance(v, set) else v for k, v in A[w].items()} for w in TARGETS},
           "estimator_sets": {w: {"E2": [" ".join(a) for a in S[w]["E2"]], "E3": [" ".join(a) for a in S[w]["E3"]],
                                  "retrieved": [{"domain": x["domain"], "type": x["type"], "raw": x["raw"], "arpa": " ".join(x["arpa"]), "url": x["url"], "context": x["context"]} for x in S[w]["retrieved"]],
                                  "rejected_extractions": S[w]["rejected"], "identity": IDENTITY[w]} for w in TARGETS},
           "summary": summ, "detail": detail}
    json.dump(out, open(f"{OUT}/replay_result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=list)
    print(json.dumps(out["accepted_sets"], ensure_ascii=False, indent=1))
    print(json.dumps(summ, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
