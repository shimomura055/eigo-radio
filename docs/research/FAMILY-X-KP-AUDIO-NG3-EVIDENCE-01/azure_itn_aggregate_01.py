# AZURE_ITN_IMPACT_01 集計script(読み取りのみ・API 0・費用0)。
# 実行: .venv\Scripts\python.exe docs/research/FAMILY-X-KP-AUDIO-NG3-EVIDENCE-01/azure_itn_aggregate_01.py
import glob, json, os, re, sys, collections
sys.path.insert(0, os.getcwd())
OUT = "docs/research/FAMILY-X-KP-AUDIO-NG3-EVIDENCE-01/azure_itn_aggregate_01.json"
NUMW = {"0": "zero", "1": "one", "2": "two", "3": "three", "4": "four", "5": "five", "6": "six", "7": "seven", "8": "eight", "9": "nine",
        "10": "ten", "11": "eleven", "12": "twelve", "13": "thirteen", "14": "fourteen", "15": "fifteen", "16": "sixteen",
        "17": "seventeen", "18": "eighteen", "19": "nineteen", "20": "twenty", "30": "thirty", "40": "forty", "50": "fifty",
        "60": "sixty", "70": "seventy", "80": "eighty", "90": "ninety", "100": "hundred"}


def de_itn(t):  # 近似: 整数tokenを英単語へ戻す(Azure lexical形の近似。実lexicalではない)
    return re.sub(r"\b(\d+)(?=\b|')", lambda m: NUMW.get(m.group(1), m.group(1)), t)


DIG = re.compile(r"[0-9]")
ONE_POSS = re.compile(r"\b(one's|ones|someone's|anyone's|everyone's|one-on-one)\b", re.I)
ONE_ANY = re.compile(r"\b(one|ones|one's|someone|someone's|anyone|anyone's|everyone|everyone's|no one)\b", re.I)
import er104_kp_three_asr_vote_01 as v


def canon_map(audit_dir):
    p = os.path.join(audit_dir, "tts_generation_results.json")
    m = {}
    if os.path.exists(p):
        try:
            d = json.load(open(p, encoding="utf8"))
            for n, e in (d.get("key_phrases") or {}).items():
                t = ((e or {}).get("english") or {}).get("text")
                if t:
                    m[f"kp{n}_en"] = t
        except Exception:
            pass
    kc = os.path.join(os.path.dirname(audit_dir), "key_phrases", "keywords_canonicalized.json")
    if os.path.exists(kc):
        try:
            d = json.load(open(kc, encoding="utf8"))
            for it in d.get("items") or []:
                t = it.get("used_form") or it.get("key_phrase")
                if t and it.get("rank") and f"kp{it['rank']}_en" not in m:
                    m[f"kp{it['rank']}_en"] = t
        except Exception:
            pass
    return m


recs = {}
kp_final = {}
kp_all = {}
for f in glob.glob("**/audit/review_lock_state.json", recursive=True):
    if ".venv" in f:
        continue
    ad = os.path.dirname(f)
    cm = canon_map(ad)
    try:
        d = json.load(open(f, encoding="utf8"))
    except Exception:
        continue
    for seg, e in d.items():
        if not re.fullmatch(r"kp\d_en", seg) or not isinstance(e, dict):
            continue
        canon = cm.get(seg)
        kp_final[(ad, seg)] = e.get("state")
        kp_all[(ad, seg)] = canon
        for a in e.get("last_attempts_log") or []:
            aj = a.get("asr_judgement") or {}
            sec = aj.get("secondary") or {}
            if not sec.get("called") and not sec.get("text"):
                continue
            sha = aj.get("audio_sha256")
            if not sha:
                continue
            vs = ((aj.get("vote") or {}).get("secondary")) or {}
            recs[sha] = dict(src="review_lock_state", run=ad, seg=seg, canon=canon, azure=sec.get("text"),
                             azure_pass=vs.get("pass") if vs else sec.get("accepted"), sec_protected=vs.get("protected_diff"),
                             judge_state=aj.get("state"), vote_state=(aj.get("vote") or {}).get("state"),
                             whisper_called=(aj.get("vote") or {}).get("whisper_called"), final_state=e.get("state"),
                             attempt=a.get("attempt"))
for f in glob.glob("**/narration/attempts/kp*_en_attempt*.json", recursive=True):
    if ".venv" in f:
        continue
    try:
        d = json.load(open(f, encoding="utf8"))
    except Exception:
        continue
    az = [s for s in d.get("cascade_steps") or [] if s.get("provider") == "azure"]
    if not az:
        continue
    sha = d.get("sha256")
    if sha in recs:
        continue
    ad = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(f))), "audit")
    seg = d.get("segment_id")
    s = az[-1]
    cls = s.get("classification")
    st = s.get("unified_judge_state")
    recs[sha] = dict(src="attempt_json", run=ad, seg=seg, canon=canon_map(ad).get(seg), azure=s.get("text"),
                     azure_pass=(cls == "NORMALIZED_MATCH") if cls else None, sec_protected=None, judge_state=st,
                     vote_state=None, whisper_called=None, final_state=kp_final.get((ad, seg)), attempt=d.get("attempt_number"))
rows = list(recs.values())


def tag(r):
    c, a = r["canon"], r["azure"]
    r["has_canon"] = bool(c)
    r["azure_has_digit"] = bool(a and DIG.search(a))
    r["canon_has_digit"] = bool(c and DIG.search(c))
    r["itn_digit"] = bool(r["azure_has_digit"] and c and not r["canon_has_digit"])
    r["canon_one_poss"] = bool(c and ONE_POSS.search(c))
    r["canon_one_any"] = bool(c and ONE_ANY.search(c))
    r["azure_ng"] = (r["azure_pass"] is False)
    r["hr_final"] = (r["final_state"] == "HUMAN_REVIEW_REQUIRED")
    if r["itn_digit"]:
        try:  # 保存Azure転写を現行voter(make_voter=classify+値guard)で再判定(API 0)。azure_pass未保存行の補完にも使う
            rv0 = v.make_voter("azure", c, a)
            r["replay_pass"] = rv0.passed
            r["replay_protected_diff"] = rv0.protected_diff
            r["replay_label"] = rv0.label
        except Exception as ex:
            r["replay_error"] = str(ex)
        try:
            t2 = de_itn(a)
            vt = v.make_voter("azure", c, t2)
            r["cf_deitn_text"] = t2
            r["cf_pass"] = vt.passed
            r["cf_label"] = vt.label
            r["cf_protected"] = vt.protected_diff
        except Exception as ex:
            r["cf_error"] = str(ex)


for r in rows:
    tag(r)


def cnt(p):
    return sum(1 for r in rows if p(r))


S = {}
S["population_azure_transcripts"] = len(rows)
S["by_src"] = dict(collections.Counter(r["src"] for r in rows))
S["with_canonical"] = cnt(lambda r: r["has_canon"])
S["azure_text_missing"] = cnt(lambda r: not r["azure"])
S["i_itn_digit_total"] = cnt(lambda r: r["itn_digit"])
S["i_itn_digit_azure_ng"] = cnt(lambda r: r["itn_digit"] and r["azure_ng"])
S["ii_itn_digit_azure_ng_final_hr"] = cnt(lambda r: r["itn_digit"] and r["azure_ng"] and r["hr_final"])
S["azure_ng_total"] = cnt(lambda r: r["azure_ng"])
S["azure_ng_total_final_hr"] = cnt(lambda r: r["azure_ng"] and r["hr_final"])
S["azure_pass_total"] = cnt(lambda r: r["azure_pass"] is True)
S["azure_pass_unknown"] = cnt(lambda r: r["azure_pass"] is None)
S["itn_digit_replay_pass"] = cnt(lambda r: r.get("replay_pass") is True)
S["itn_digit_replay_ng"] = cnt(lambda r: r.get("replay_pass") is False)
S["itn_digit_replay_protected_diff"] = cnt(lambda r: r.get("replay_protected_diff") is True)
S["itn_digit_cf_pass"] = cnt(lambda r: r.get("cf_pass") is True)
S["itn_digit_azure_ng_cf_pass"] = cnt(lambda r: r.get("cf_pass") is True)
S["itn_digit_azure_ng_cf_not_pass"] = cnt(lambda r: r.get("cf_pass") is False)
S["iii_attempts_canon_one_poss"] = cnt(lambda r: r["canon_one_poss"])
S["iii_attempts_canon_one_poss_azure_ng"] = cnt(lambda r: r["canon_one_poss"] and r["azure_ng"])
S["iii_attempts_canon_one_any"] = cnt(lambda r: r["canon_one_any"])
S["iii_attempts_canon_one_any_azure_ng"] = cnt(lambda r: r["canon_one_any"] and r["azure_ng"])
S["kp_segments_total_in_lock_state"] = len(kp_final)
S["kp_segments_with_canonical"] = sum(1 for k, c in kp_all.items() if c)
S["kp_segments_hr"] = sum(1 for s in kp_final.values() if s == "HUMAN_REVIEW_REQUIRED")
S["kp_segments_canon_one_poss"] = sum(1 for c in kp_all.values() if c and ONE_POSS.search(c))
S["kp_segments_canon_one_any"] = sum(1 for c in kp_all.values() if c and ONE_ANY.search(c))
S["kp_segments_canon_one_poss_hr"] = sum(1 for k, c in kp_all.items() if c and ONE_POSS.search(c) and kp_final[k] == "HUMAN_REVIEW_REQUIRED")
S["kp_segments_canon_one_any_hr"] = sum(1 for k, c in kp_all.items() if c and ONE_ANY.search(c) and kp_final[k] == "HUMAN_REVIEW_REQUIRED")
ah_hr = set()
ah_seg = set()
for ln in open("er011_output/attempt_history.jsonl", encoding="utf8"):
    try:
        o = json.loads(ln)
    except Exception:
        continue
    if not re.fullmatch(r"kp\d_en", str(o.get("segment_id"))):
        continue
    k = (o.get("theme_id"), o.get("level"), o.get("segment_id"))
    ah_seg.add(k)
    if o.get("human_review_reached"):
        ah_hr.add(k)
S["attempt_history_kp_en_segments"] = len(ah_seg)
S["attempt_history_kp_en_segments_hr"] = len(ah_hr)
rv = json.load(open("docs/research/KP-THREE-ASR-MAJORITY-PRODUCTION-01/stored_audio_reeval_02.json", encoding="utf8"))["rows"]
rvrows = []
for x in rv:
    c = x.get("canonical")
    a = (x.get("secondary") or {}).get("text")
    ad = x.get("adapter") or {}
    rvrows.append(dict(id=x.get("id"), corpus=x.get("corpus"), label=x.get("label"), canon=c, azure=a,
                       azure_pass=ad.get("secondary_pass"), vote_state=ad.get("vote_state"),
                       itn_digit=bool(a and DIG.search(a) and c and not DIG.search(c)),
                       canon_one_any=bool(c and ONE_ANY.search(c)), canon_one_poss=bool(c and ONE_POSS.search(c))))
S["reeval02_rows"] = len(rvrows)
S["reeval02_itn_digit"] = sum(1 for r in rvrows if r["itn_digit"])
S["reeval02_itn_digit_azure_ng"] = sum(1 for r in rvrows if r["itn_digit"] and r["azure_pass"] is False)
S["reeval02_canon_one_any"] = sum(1 for r in rvrows if r["canon_one_any"])
S["reeval02_canon_one_any_azure_ng"] = sum(1 for r in rvrows if r["canon_one_any"] and r["azure_pass"] is False)
S["reeval02_canon_one_poss"] = sum(1 for r in rvrows if r["canon_one_poss"])
json.dump(dict(summary=S, itn_digit_rows=[r for r in rows if r["itn_digit"]], one_any_rows=[r for r in rows if r["canon_one_any"]],
               reeval02_itn_or_one=[r for r in rvrows if r["itn_digit"] or r["canon_one_any"]]),
          open(OUT, "w", encoding="utf8"), ensure_ascii=False, indent=1)
print(json.dumps(S, ensure_ascii=False, indent=1))
