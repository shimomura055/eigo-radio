# -*- coding: utf-8 -*-
"""FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_30: 課題① 補強検証用 DEV harness (OPUS_REVIEW_08 OF-KP2-01/02/07)。
DEV/Trial専用。Production module(er003_*/er019_*/er026_*/er105_*)は編集せずimportのみ。本委任ではAPI 0(--cap 0 のdry-runのみ。有料実行は次委任・ユーザー予算承認後)。

arm:
  B0p  = 現行Productionの gloss生成を **そのまま** 呼ぶ(ga.align_glosses: rules_fulltext自動選択・prior再提示・retry上限2・DEVELOPER_MESSAGE・GLOSS_ALIGNMENT_JSON_SCHEMA)
  X2pp = X2p'(X2p + 範囲の規則 + 定訳優先)を本番構成で呼ぶ。Trial_05のX2p(`er112_kp_gm_trial_05.build_x_message`)との差分は
         (1)rules=rules_fulltext (2)priorのprevious_attempt_rejected再提示 (3)X2PP_SCOPE/X2PP_MEANING(範囲の規則・定訳優先) のみ。
         gate loopはga.run_alignment_gate_corrected と同一構造(item単位retry・上限2)のDEVコピー。
本番構成 = 1記事level(同一run・同一keywords_canonicalized.json)の全KPを1 call(--siblings on)。evalは対象KPのみ、同levelの他KPはsibling(生成するが評価しない)。
cmd: plan(API 0。job数・KP数・見積) / gen(--cap必須。cap<=0はdry-run=plan表示のみでAPI呼出0) / prodhash(API 0) / dump(API 0: message確認)
"""
from __future__ import annotations

import argparse, collections, glob, hashlib, json, os, re, sys, threading, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")
OUT6 = ROOT / "er112_output" / "kp_gm_trial_06"
LEDGER6 = OUT6 / "paid_calls.jsonl"
RES6 = OUT6 / "results.jsonl"
RD = ROOT / "docs/research/FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01"
STOP_PATHS = [OUT6 / "STOP", OUT6 / "STOP_ALL", ROOT / "er026_output/family_z_production_e2e_01/STOP_ALL", RD / "STOP",
              ROOT / "er112_output/kp_gm_trial_05/STOP", ROOT / "er112_output/kp_gm_trial_04/STOP"]
EFFORT = "high"
ARMS = ("B0p", "X2pp")
PER_JOB_MULT = 2.0          # 1 jobが見積(retry1回込み)の2倍を超えたらHALT
PROD_FILES = ["er003_key_words_gloss_alignment.py", "er003_v1_n3_01_scaffold_generate.py", "er003_key_words_canonicalization.py",
              "er019_family_x_kp_explanation_01.py", "er026_family_z_fiction_production_runner_01.py", "er105_kp_fulltext_selector_01.py"]

import er112_kp_gm_trial_05 as T5                      # noqa: E402  (X_HEAD/X_NEWGEN/X_OUTRULES/x_schema/all_kps5)
import er112_kp_gm_trial_04 as X4                      # noqa: E402
import er112_kp_gm_trial_04_gen as G                   # noqa: E402  (M_DEVELOPER, art_id)
import er112_kp_gm_trial_02 as T                       # noqa: E402  (client, LUNA)
import er003_key_words_gloss_alignment as ga           # noqa: E402
import er019_family_x_kp_explanation_01 as kx          # noqa: E402
import er009_n1_routing_governance_10_actual_model_cost as pricing   # noqa: E402

_lock = threading.Lock()
_halt = {"flag": False, "why": ""}

# ------------------------------------------------------------------ X2p' (OF-KP2-02(a)。修正は1回のみ。差分=TRIAL_DESIGN_07.md)
X2PP_SCOPE = ("【範囲の規則(meaning_in_text_enとjapanese_glossの両方に適用)】\n"
              "- 本文で使われている語義・用法(字義どおりか、比喩・慣用か)を選んでください。"
              "ただし、japanese_glossが表すのはkey_phraseの範囲だけです。key_phraseに含まれていない、本文側の否定・主語・時制・具体的な対象・場面は、"
              "japanese_glossに持ち込まないでください(例: 本文が「the plan did not work out」でkey_phraseが「work out」なら、"
              "japanese_glossは「うまくいかなかった」ではなく「うまくいく」)。\n\n")
X2PP_MEANING = ("【意味の決め方(各項目、japanese_glossを書く前に、この順で必ず出力してください)】\n"
                "- meaning_in_text_en: 【記事本文】のこの箇所(source_sentenceとその前後の文)でkey_phrase【全体】が表している意味を、平易な英語1文で書く。"
                "key_phraseの語をそのまま繰り返さず言い換える。本文の話題の一側面(例: 差の大きさ、時間、量など)だけに絞らず、key_phrase全体が何を言っているかを書く。"
                "字義どおりの用法なら字義の意味。比喩・慣用・筆者が作った比喩なら、その比喩が指す一般的な意味(what it stands for)を書く。記事固有の固有名詞・数値は入れない。\n"
                "- naive_ja: key_phraseの英単語を、それぞれ日本語の対応語に置き換えただけの訳を、意味の解釈を加えずに書く。\n"
                "- naive_ja_conveys: 日本語だけを読む学習者が、naive_jaからmeaning_in_text_enの意味を受け取れるか。"
                "yes(同じ意味・同じ比喩が日本語でも通じる、または字義どおりの用法)/ partly(一部が落ちる)/ no(字義の動作・物の像しか伝わらず、本文での意味は伝わらない)。\n"
                "- japanese_gloss: yesなら、naive_jaをそのまま写さず、自然で平易な訳(英和辞典の定訳や日本語の慣用表現があればそれ)を選ぶ。"
                "partly/noのときは、まず、このkey_phraseのこの語義に日本語の定訳(英和辞典の見出し訳や日本語として定着した言い方。例: cut cornersなら「手を抜く」、break evenなら「収支がとんとんになる」)があればそれを優先し、"
                "無い場合だけ、naive_jaの字義の像を使わず、meaning_in_text_enの意味【全体】を日本語の慣用表現か平易な短い言い換えで表す(意味の一部だけを取り出した語にしない)。"
                "naive_jaの語を別の語に置き換えるときは、動作主(誰が)・動詞の意味を変えない(例: 「誰も出なかった電話」を「誰もかけたくなかった電話」のように、動詞の意味を別の意味にずらさない)。"
                "key_phrase全体(目的語・修飾語を含む)の意味を落とさず、key_phraseと同じ品詞・同じ程度の長さの句にする(説明文・定義文にしない)。\n\n")


def _person_block(tgt):
    """T5.build_x_message と同一の人称規則の文脈限定句置換(Trialとの差分を作らない)。"""
    person = ga.PERSON_CONSTRAINT_TEXT
    a1 = "current_japanese_glossがそうなっている場合は、指示2の『書き換えない』の例外として、current_gloss_consistent=falseにして書き換えてください。"
    a2 = "display_phrase_before_canonicalization・current_japanese_gloss・source_sentenceにある"
    a3 = ("source_sentenceは、辞書に複数の語義がある表現で、そのうちどの語義かを選ぶためだけに使い、"
          "人称の指示対象を決めるためには使わないでください。")
    assert a1 in person and a2 in person and a3 in person
    return (person.replace(a1, "").replace(a2, "display_phrase_before_canonicalization・source_sentenceにある")
            .replace(a3, "source_sentenceと前後の文脈は語義と用法を決めるために使い、人称の指示対象を決めるためには使わないでください。"))


def build_x_message06(tgt, article, rules=None, prior=None, meaning=None, scope=None):
    """X2p'の本番構成message。rules=None -> rules_fulltext(Production全文選定itemが使う規則)。prior={rank:{gloss,reasons}}でretry再提示。
    meaning/scope引数はgolden test用(meaning=T5.X2P_MEANING, scope='', rules=非fulltext, prior=None でTrial_05 X2pのmessageと完全一致する)。"""
    rules = rules if rules is not None else (ga.preflight(True) or {})["rules_fulltext"]
    meaning = X2PP_MEANING if meaning is None else meaning
    scope = X2PP_SCOPE if scope is None else scope
    items, any_person = [], False
    for it in tgt:
        d = {"rank": it["rank"], "key_phrase": it["key_phrase"], "display_phrase_before_canonicalization": it.get("display_phrase"),
             "source_sentence": it.get("source_sentence", ""),
             "added_content_words": ga.added_content_words(it.get("display_phrase"), it.get("key_phrase"))}
        ind = ga.indefinite_person_tokens(it.get("key_phrase"))
        if ind:
            any_person = True
            d["indefinite_person_tokens_in_key_phrase"] = ind
            pairs = ga.person_generalization_pairs(it)
            if pairs:
                d["person_generalization"] = pairs
        if prior and it["rank"] in prior:     # build_user_message_corrected と同一の項目形式
            d["previous_attempt_rejected"] = {"gloss": prior[it["rank"]].get("gloss"), "reasons": list(prior[it["rank"]].get("reasons") or [])}
        items.append(d)
    prior_block = ("previous_attempt_rejected(ある項目のみ)は、前回の応答が検証で却下された理由です。同じ誤りを繰り返さないでください。\n\n" if prior else "")
    return (T5.X_HEAD + (_person_block(tgt) if any_person else "") + T5.X_NEWGEN + scope + meaning + T5.X_OUTRULES + prior_block +
            "【日本語グロスの規則(承認済み選定Promptと同一)】\n" + rules + "\n\n"
            "【対象項目】\n" + json.dumps(items, ensure_ascii=False, indent=2) + "\n\n【記事本文(参考)】\n" + article)


def x06_schema():
    s = T5.x_schema("X2p")
    s["name"] = "kp_gloss_x2pp_trial06"
    return s


# ------------------------------------------------------------------ record-only 持ち込み検出(OPUS_REVIEW_08 論点2。合否に使わない。Production新経路validatorへの移植候補)
NEG_TOKENS = {"not", "no", "never", "without", "none", "nothing", "nobody", "cannot", "neither", "nor", "hardly", "barely", "unable"}
NEG_JA = re.compile("ない|なかっ|ません|ぬ$|ずに|ず$")
PAST_JA = re.compile("(た|だった)$")


def detect_import(key_phrase, gloss):
    """戻り=list[str]。KPに否定語が無いのにglossに否定 / glossが過去形『た』で終わる。記録のみ(合否に使わない)。"""
    flags = []
    toks = re.findall("[a-z']+", (key_phrase or "").lower())
    kp_neg = any(t in NEG_TOKENS or t.endswith("n't") or (t.startswith("un") and len(t) > 4) for t in toks)
    g = (gloss or "").strip()
    if not kp_neg and NEG_JA.search(g):
        flags.append("neg_in_gloss_not_in_kp")
    if PAST_JA.search(g):
        flags.append("past_tense_ending")
    return flags


# ------------------------------------------------------------------ KP集合・level group
def hc_kps():
    p = OUT6 / "hardcore_set_06.json"
    return json.load(open(p, encoding="utf-8")) if p.exists() else {}


def all_kps6():
    A = dict(T5.all_kps5())
    for k, v in hc_kps().items():
        A.setdefault(k, v)
    return A


def keys_of(a):
    if a.keys:
        return [k.strip() for k in a.keys.split("|")]
    if a.set == "S2":
        return T5.keys_of(argparse.Namespace(keys="", set="S2", nheld=0))
    if a.set == "HC":
        return list(hc_kps())
    if a.set == "R":
        return list(T5.R_KEYS)
    raise SystemExit("--set S2|HC|R or --keys")


def _level_file(run):
    if not run:
        return None
    for p in glob.glob(str(ROOT / run / "**" / "keywords_canonicalized.json"), recursive=True):
        return p
    return None


def build_groups(keys, siblings, max_level=0):
    """戻り=[{gid, article, targets[{rank,key_phrase,display_phrase,source_sentence,...}], eval_keys{key->rank}, siblings_used, n_sibling}]。
    siblings=True: 同一runのkeywords_canonicalized.jsonの全itemを1 level(=本番のalign対象)として1 callにまとめる。見つからない場合はeval KPのみ。"""
    A = all_kps6()
    groups, order = {}, []
    for k in keys:
        kp = A[k]
        f = _level_file(kp.get("run", "")) if siblings else None
        gid = ("lvl:" + f.replace(chr(92), "/").split("eigo-radio/", 1)[-1]) if f else "art:" + G.art_id(kp)
        if gid not in groups:
            groups[gid] = dict(gid=gid, article=kp["article"], kps=[], level_file=f, run=kp.get("run"))
            order.append(gid)
        groups[gid]["kps"].append(kp)
    out = []
    for gid in order:
        g = groups[gid]
        tgts, have = [], set()
        if g["level_file"]:
            for it in (json.load(open(g["level_file"], encoding="utf-8")).get("items") or []):
                kk = (it.get("used_form") or it.get("key_phrase") or "").strip()
                s = it.get("source_sentence") or ""
                if not kk or not s or kk.lower() in have:
                    continue
                have.add(kk.lower())
                tgts.append(dict(key=kk, display_phrase=it.get("display_phrase") or kk, source_sentence=s))
        for kp in g["kps"]:       # eval KPが level file に無い(または level file無し)場合は追加
            if kp["key"].lower() not in have:
                have.add(kp["key"].lower())
                tgts.append(dict(key=kp["key"], display_phrase=kp["display"], source_sentence=kp["sent"]))
        evalset = {kp["key"].lower() for kp in g["kps"]}
        targets, evalk = [], {}
        for i, t in enumerate(tgts):
            targets.append({"rank": i + 1, "key_phrase": t["key"], "display_phrase": t["display_phrase"], "japanese_gloss": None,
                            "source_sentence": t["source_sentence"], "fulltext_source_ref": "fulltext_exact_v1"})
            if t["key"].lower() in evalset:
                evalk[t["key"].lower()] = i + 1
        if max_level and len(targets) > max_level:     # 本番のlevelは5件前後。eval KPを優先して残し、siblingは先頭(rank順)から詰める
            keep = [t for t in targets if t["key_phrase"].lower() in evalk]
            keep += [t for t in targets if t["key_phrase"].lower() not in evalk][: max(0, max_level - len(keep))]
            keep.sort(key=lambda t: t["rank"])
            targets = [dict(t, rank=i + 1) for i, t in enumerate(keep)]
            evalk = {t["key_phrase"].lower(): t["rank"] for t in targets if t["key_phrase"].lower() in evalset}
        out.append(dict(gid=gid, article=g["article"], targets=targets, eval_keys=evalk, siblings_used=bool(g["level_file"]),
                        n_sibling=len(targets) - len(evalk), run=g["run"]))
    return out


# ------------------------------------------------------------------ 台帳・見積
def read_jsonl(p):
    return X4.read_jsonl(p)


def total():
    return sum((r.get("cost_jpy") or 0) for r in read_jsonl(LEDGER6))


def stop():
    return _halt["flag"] or any(p.exists() for p in STOP_PATHS)


def cost_fit():
    """Trial_05台帳(実測)からarm別の 1call費用 = a + b*(call内KP数) を最小二乗で求める。B0p<-B0, X2pp<-X2p(X2p'の追加分は未測定のため+10%の余裕)。
    注意: 実測のcall内KP数は最大4。本番構成(5前後)は外挿であり、補強検証(c)の目的の一つがこの外挿の実測。"""
    rows = [r for r in read_jsonl(T5.LEDGER5) if r.get("keys") and r.get("cost_jpy")]
    fit = {}
    for arm, src, margin in (("B0p", "B0", 1.0), ("X2pp", "X2p", 1.10)):
        v = [(len(r["keys"]), r["cost_jpy"]) for r in rows if r["arm"] == src]
        n = [x[0] for x in v]
        c = [x[1] for x in v]
        mn, mc = sum(n) / len(n), sum(c) / len(c)
        sxx = sum((x - mn) ** 2 for x in n)
        b = sum((x - mn) * (y - mc) for x, y in zip(n, c)) / sxx if sxx else 0.0
        a0 = mc - b * mn
        fit[arm] = dict(a=a0 * margin, b=max(b, 0.0) * margin, n_rows=len(v), n_max=max(n), per_kp_mean=sum(c) / sum(n))
    return fit


def est_call(arm, n_kp, fit=None):
    f = (fit or cost_fit())[arm]
    return f["a"] + f["b"] * n_kp


# ------------------------------------------------------------------ API呼出(有料。cap>0を明示した場合のみ)
class RecClient:
    """make_alignment_fn に渡すclientラッパ。各create()の所要時間・usage・reasoning_tokens・費用を記録する(OF-KP2-07(e)実測)。"""
    def __init__(self, c):
        self._c = c
        self.calls = []
        self.responses = self

    def create(self, **kw):
        t0 = time.monotonic()
        r = self._c.responses.create(**kw)
        dt = time.monotonic() - t0
        od = getattr(r.usage, "output_tokens_details", None)
        u = kx._usage_dict(r.usage)
        u["reasoning_tokens"] = getattr(od, "reasoning_tokens", None) if od is not None else None
        c = pricing.cost_jpy_for_call("openai", r.model or T.LUNA, u.get("input_tokens"), u.get("cached_input_tokens"), u.get("output_tokens"))
        self.calls.append(dict(wall_s=round(dt, 2), usage=u, cost_jpy=round(c, 5)))
        return r


def _append(path, rec):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(path), os.O_WRONLY | os.O_APPEND | os.O_CREAT)
    try:
        os.write(fd, (json.dumps(rec, ensure_ascii=False) + chr(10)).encode("utf-8"))
    finally:
        os.close(fd)


def run_gate_x(rec, targets, article, max_attempts=None):
    """ga.run_alignment_gate_corrected と同一構造(item単位retry・上限MAX_GLOSS_ALIGNMENT_ATTEMPTS・prior再提示)のDEVコピー。messageだけX2p'。"""
    max_attempts = max_attempts or ga.MAX_GLOSS_ALIGNMENT_ATTEMPTS
    rules = (ga.preflight(True) or {})["rules_fulltext"]
    adopted, prior, pending, attempts, msgs = {}, {}, list(targets), [], []
    for attempt in range(1, max_attempts + 1):
        if not pending:
            break
        msg = build_x_message06(pending, article, rules, prior or None)
        msgs.append(msg)
        fn = ga.make_alignment_fn(msg, client=rec, model=T.LUNA, reasoning_effort=EFFORT, developer_message=G.M_DEVELOPER, schema=x06_schema())
        a = dict(attempt=attempt, target_ranks=[t["rank"] for t in pending])
        try:
            raw, model_id, _rid = fn()
            parsed = json.loads(raw)
        except Exception as e:     # noqa: BLE001
            a.update(status="TECHNICAL_OR_PARSE_FAILED", error="%s: %s" % (type(e).__name__, e))
            attempts.append(a)
            continue
        by = {it["rank"]: it for it in (parsed.get("items") or []) if isinstance(it, dict) and isinstance(it.get("rank"), int)}
        n_valid = 0
        for t in pending:
            resp = by.get(t["rank"])
            v = ga.validate_item_corrected(resp, t)
            newf = [k for k in ("meaning_in_text_en", "naive_ja", "naive_ja_conveys")
                    if not (isinstance(resp, dict) and isinstance(resp.get(k), str) and resp.get(k).strip())]
            if isinstance(resp, dict) and resp.get("naive_ja_conveys") not in ("yes", "partly", "no"):
                newf.append("naive_ja_conveys_enum")
            if newf:
                v["valid"] = False
                v["reasons"] = list(v["reasons"]) + ["meaning_stage_fields_invalid:" + ",".join(newf)]
            if v["valid"]:
                adopted[t["rank"]] = dict(gloss=v["adopt_gloss"], attempt=attempt, resp=resp)
                n_valid += 1
            else:
                prior[t["rank"]] = {"gloss": v.get("proposed_gloss"), "reasons": list(v["reasons"])}
        a.update(status="ALIGN_PASS" if n_valid == len(pending) else ("ALIGN_PARTIAL" if n_valid else "ALIGN_INVALID"), n_valid=n_valid)
        attempts.append(a)
        pending = [t for t in pending if t["rank"] not in adopted]
    return dict(adopted=adopted, unresolved=[t["rank"] for t in pending], attempts=attempts, messages=msgs)


def run_group(arm, rep, g, tag, rec):
    """1 group(=1 level)を本番構成で実行。戻り=(結果rowのlist, API call記録)。"""
    t0 = time.monotonic()
    if arm == "B0p":
        merged = {"items": [dict(t) for t in g["targets"]]}

        def factory(msg):
            return ga.make_alignment_fn(msg, client=rec, model=T.LUNA, reasoning_effort=EFFORT)   # Production既定のdeveloper/schema(B0)
        al = ga.align_glosses(merged, g["article"], factory, out_dir=None, article_id=g["gid"], enabled=True)
        final = {it["rank"]: (it.get("japanese_gloss") if it.get("gloss_alignment_status") == ga.STATUS_ALIGNED else None) for it in al["merged"]["items"]}
        meta = dict(status=al["status"], unresolved=al["unresolved_ranks"], attempts=len(al["attempts"]), rules_sha256=al["rules_sha256"])
        fields = {}
    else:
        gt = run_gate_x(rec, g["targets"], g["article"])
        final = {t["rank"]: (gt["adopted"][t["rank"]]["gloss"] if t["rank"] in gt["adopted"] else None) for t in g["targets"]}
        fields = {r: {k: gt["adopted"][r]["resp"].get(k) for k in ("meaning_in_text_en", "naive_ja", "naive_ja_conveys")} for r in gt["adopted"]}
        meta = dict(status="ALIGN_PASS" if not gt["unresolved"] else "UNRESOLVED", unresolved=gt["unresolved"], attempts=len(gt["attempts"]),
                    rules_sha256=ga.preflight(True)["sha256_fulltext"])
    wall = round(time.monotonic() - t0, 2)
    cost = round(sum(c["cost_jpy"] for c in rec.calls), 5)
    rows = []
    for t in g["targets"]:
        gl = final.get(t["rank"])
        rows.append(dict(arm=arm, key=t["key_phrase"].lower(), rep=rep, kind="L", is_eval=t["key_phrase"].lower() in g["eval_keys"], gloss=gl,
                         fields=fields.get(t["rank"], {}), tag=tag, sent=t["source_sentence"], gid=g["gid"], n_in_call=len(g["targets"]),
                         n_sibling=g["n_sibling"], level_cost_jpy=cost, level_wall_s=wall, level_calls=len(rec.calls),
                         level_out_tokens=sum((c["usage"].get("output_tokens") or 0) for c in rec.calls),
                         level_reasoning_tokens=sum((c["usage"].get("reasoning_tokens") or 0) for c in rec.calls),
                         level_in_tokens=sum((c["usage"].get("input_tokens") or 0) for c in rec.calls),
                         flags=detect_import(t["key_phrase"], gl), meta=meta))
    return rows, rec.calls


def _setup(a):
    keys = keys_of(a)
    sib = {"on": True, "off": False, "auto": a.set == "S2"}[a.siblings]
    return keys, sib, build_groups(keys, sib, getattr(a, "max_level", 0))


def cmd_gen(a):
    keys, sib, groups = _setup(a)
    arms = [x for x in a.arm.split(",") if x]
    assert all(x in ARMS for x in arms), arms
    reps = [int(x) for x in a.reps.split(",")]
    done = {(r["arm"], r["key"], r["rep"]) for r in read_jsonl(RES6) if r.get("is_eval")}
    jobs = [(arm, rep, g) for arm in arms for rep in reps for g in groups if any((arm, k, rep) not in done for k in g["eval_keys"])]
    if a.max_calls:
        jobs = jobs[: a.max_calls]
    fit = cost_fit()
    est = sum(est_call(arm, len(g["targets"]), fit) for arm, rep, g in jobs)
    print("jobs", len(jobs), "groups", len(groups), "siblings", sib, "eval KP", len(keys), "est %.3f yen (1 attempt/job, retry別)" % est, "cap", a.cap, flush=True)
    if a.cap <= 0:
        print("DRY-RUN (cap<=0): API呼出0。--cap に正の値を指定した場合のみ有料実行", flush=True)
        return
    client = T.client()

    def w(j):
        arm, rep, g = j
        if stop():
            return ("SKIP_STOP", arm, rep, g["gid"])
        e = est_call(arm, len(g["targets"]), fit) * 2     # retry 1回分まで含めた上限見込み
        with _lock:
            if total() + e > a.cap:
                _halt["flag"], _halt["why"] = True, "cap: cum %.3f + est %.3f > %.2f" % (total(), e, a.cap)
                return ("SKIP_CAP", arm, rep, g["gid"])
        rec = RecClient(client)
        rows, calls = run_group(arm, rep, g, a.tag or arm, rec)
        c = sum(x["cost_jpy"] for x in calls)
        with _lock:
            for x in calls:
                _append(LEDGER6, dict(kind="gen", arm=arm, tag=a.tag or arm, gid=g["gid"], n_in_call=len(g["targets"]), rep=rep, usage=x["usage"],
                                      wall_s=x["wall_s"], cost_jpy=x["cost_jpy"], ts=time.strftime("%Y-%m-%dT%H:%M:%S")))
            for r in rows:
                _append(RES6, r)
            if c > PER_JOB_MULT * e:
                _halt["flag"], _halt["why"] = True, "per-job %.4f > %.1fx est %.4f" % (c, PER_JOB_MULT, e)
        return (arm, rep, g["gid"], len(g["targets"]), round(c, 4))

    with ThreadPoolExecutor(a.workers) as ex:
        for f in as_completed([ex.submit(w, j) for j in jobs]):
            print(f.result(), "cum=%.3f" % total(), flush=True)
    if _halt["flag"]:
        print("HALT:", _halt["why"], flush=True)


def cmd_plan(a):
    keys, sib, groups = _setup(a)
    fit = cost_fit()
    arms = [x for x in a.arm.split(",") if x]
    reps = [int(x) for x in a.reps.split(",")]
    sizes = collections.Counter(len(g["targets"]) for g in groups)
    print("set", a.set or "(keys)", "eval KP", len(keys), "groups(=call/attempt)", len(groups), "siblings", sib, "siblings_used", sum(g["siblings_used"] for g in groups),
          "level不明(eval KPのみ)", sum(not g["siblings_used"] for g in groups))
    print("call内KP数の分布", dict(sorted(sizes.items())), "total targets", sum(len(g["targets"]) for g in groups), "sibling総数", sum(g["n_sibling"] for g in groups))
    for arm in arms:
        e1 = sum(est_call(arm, len(g["targets"]), fit) for g in groups)
        print("  %s: fit a=%.4f b=%.4f(/KP) [rows=%d, 実測n最大=%d]  1rep見積=%.3f円  x%d rep=%.3f円(retryなし) / retry上限込み(x1.3)=%.3f円" % (
            arm, fit[arm]["a"], fit[arm]["b"], fit[arm]["n_rows"], fit[arm]["n_max"], e1, len(reps), e1 * len(reps), e1 * len(reps) * 1.3))
    if a.verbose:
        for g in groups:
            print("   ", g["gid"][-60:], "targets", len(g["targets"]), "eval", len(g["eval_keys"]), "sib", g["n_sibling"], sorted(g["eval_keys"]))


def cmd_prodhash(a):
    h = {f: hashlib.sha256(open(ROOT / f, "rb").read()).hexdigest() for f in PROD_FILES}
    OUT6.mkdir(parents=True, exist_ok=True)
    (OUT6 / ("production_hash_%s.txt" % (a.tag or "now"))).write_text(json.dumps(h, indent=1), encoding="utf-8")
    print(json.dumps(h, indent=1))


def cmd_dump(a):
    keys, sib, groups = _setup(a)
    print(build_x_message06(groups[0]["targets"], groups[0]["article"]))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("--arm", default="B0p,X2pp")
    ap.add_argument("--reps", default="1")
    ap.add_argument("--set", default="")
    ap.add_argument("--keys", default="")
    ap.add_argument("--siblings", default="auto", choices=["auto", "on", "off"])
    ap.add_argument("--cap", type=float, default=0.0)      # 既定0=dry-run(API 0)
    ap.add_argument("--tag", default="")
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--max-calls", type=int, default=0)
    ap.add_argument("--max-level", type=int, default=0, help="1 callあたりの最大KP数(0=levelの全KP)。eval KP優先、siblingはrank順で詰める")
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()
    {"gen": cmd_gen, "plan": cmd_plan, "prodhash": cmd_prodhash, "dump": cmd_dump}[a.cmd](a)
