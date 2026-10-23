# -*- coding: utf-8 -*-
"""FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_22: 課題① Trial_05 生成arm(B0/M/X1/X2/Cp)・held-out・盲検表 (DEV専用、er112基盤)。
Production file(er003_*/er019_*/er026_*/er105_*)は編集しない。importして呼ぶだけ(Trial_04のproduction hash検査を踏襲)。
費用台帳=er112_output/kp_gm_trial_05/paid_calls.jsonl。上限=個別枠8.33円(Trial_04枠残3.43+rep2枠残4.90)。cap検査は発行前累計+見込みで判定、1call 0.20円超でSTOP。
arm:
  B0 = 現行Production gloss生成(ga.build_user_message_corrected+GLOSS_ALIGNMENT_JSON_SCHEMA)
  M  = Trial_04のM-base(再整合用指示を除く、制約句は残す、M_SCHEMA)
  X1 = M-base + 制約句置換のみ(欄追加なし)。出力schemaはProduction互換(OF-KP1-07)
  X2 = X1 + meaning_in_text_en -> naive_ja -> naive_ja_conveys -> japanese_gloss(案A)。Production互換schema+新欄(japanese_glossの前)
  Cp = Trial_04のCp(CP_BLOCK + cp_schema、gloss後の自己監査欄)
モデル: gpt-6-luna(Production系列と同一=比較のため。25節の例外理由=評価対象がluna生成の品質そのもの)、effort=high固定。
"""
from __future__ import annotations

import argparse, hashlib, json, os, sys, threading, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")
OUT5 = ROOT / "er112_output" / "kp_gm_trial_05"
LEDGER5 = OUT5 / "paid_calls.jsonl"
RES5 = OUT5 / "results.jsonl"
CAP_JPY = 8.33
PER_CALL_MAX = 0.20
RD = ROOT / "docs/research/FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01"
STOP_PATHS = [OUT5 / "STOP", OUT5 / "STOP_ALL", ROOT / "er026_output/family_z_production_e2e_01/STOP_ALL", RD / "STOP", ROOT / "er112_output/kp_gm_trial_04/STOP"]

import er112_kp_gm_trial_04 as X4                      # noqa: E402  (all_kps, read_jsonl)
import er112_kp_gm_trial_04_gen as G                   # noqa: E402  (M_*, CP_BLOCK, cp_schema, _targets, art_id)
import er112_kp_gm_trial_02 as T                       # noqa: E402  (client, LUNA)
import er003_key_words_gloss_alignment as ga           # noqa: E402
import er019_family_x_kp_explanation_01 as kx          # noqa: E402
import er009_n1_routing_governance_10_actual_model_cost as pricing   # noqa: E402

_lock = threading.Lock()
_halt = {"flag": False, "why": ""}
EFFORT = "high"
ARMS = ("B0", "M", "X1", "X2", "Cp")


def stop():
    return _halt["flag"] or any(p.exists() for p in STOP_PATHS)


def _append(path, rec):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(path), os.O_WRONLY | os.O_APPEND | os.O_CREAT)
    try:
        os.write(fd, (json.dumps(rec, ensure_ascii=False) + chr(10)).encode("utf-8"))
    finally:
        os.close(fd)


def read_jsonl(p):
    return X4.read_jsonl(p)


def total():
    t = 0.0
    for r in read_jsonl(LEDGER5):
        t += r.get("cost_jpy") or 0
    return t


def load_res():
    d = {}
    for r in read_jsonl(RES5):
        d[(r["arm"], r["key"], r["rep"])] = r
    return d


# ------------------------------------------------------------------ KP集合
def heldout_kps():
    p = OUT5 / "heldout_set_05.json"
    return json.load(open(p, encoding="utf-8")) if p.exists() else {}


def all_kps5():
    A = dict(X4.all_kps())
    for k, v in heldout_kps().items():
        A.setdefault(k, v)
    return A


R_KEYS = ["draw a line", "an unseen clock", "question shaped like a trophy", "greener grass", "come down", "behind the scenes", "sound no one asked for"]
R_CORE = ["draw a line", "an unseen clock", "question shaped like a trophy", "greener grass"]


def heldout_order():
    p = OUT5 / "heldout_selection_log_05.json"
    return json.load(open(p, encoding="utf-8"))["selected"] if p.exists() else []


# ------------------------------------------------------------------ X1/X2 message・schema (DEV)
X_HEAD = ("以下の各英語key_phraseは、教材として最終確定した英語表現です。各項目について、日本語グロス(japanese_gloss)を新しく書いてください(全項目、日本語グロスは未生成です)。\n\n"
          "日本語グロスは、このkey_phraseが【記事本文】のこの箇所で実際に表している意味を、日本語で短く自然に表したものにしてください。"
          "本文固有の固有名詞・数値・この記事だけの出来事はグロスに入れないでください。\n\n")
X_NEWGEN = ("【新規生成の規則】\n- source_sentenceと記事本文の前後の文脈は、key_phraseの語義と用法(字義どおりか、比喩・慣用か)を決めるために使ってください"
            "(文中の固有名詞・数値・この記事だけの出来事をグロスに入れないでください)。\n\n")
X_OUTRULES = ("【出力欄の規則】\n"
              "- current_gloss_consistent: 全項目で必ずfalse(日本語グロスは未生成のため)。\n"
              "- qa_reflects_all_key_phrase_words: japanese_glossがkey_phrase全体の意味を過不足なく反映できている場合のみPASS。\n"
              "- added_word_mappings: added_content_wordsの各語について、japanese_glossの中でその語の意味を表している部分を、japanese_glossからそのまま切り出して書いてください"
              "(english_wordには対応させる英語の語、複数語をまとめた句でもかまいません。japanese_spanにはjapanese_glossに含まれない文字列や、「～」などの記号だけを書かないでください)。"
              "複数の英語語が一つの日本語表現でまとめて表されている場合は、同じ部分を複数の語に対応させてかまいません。added_content_wordsが空の項目は、added_word_mappingsを空配列にしてください。\n"
              "- reasoning: 判断の根拠を短く書いてください。\n\n")
X2_MEANING = ("【意味の決め方(各項目、japanese_glossを書く前に、この順で必ず出力してください)】\n"
              "- meaning_in_text_en: 【記事本文】のこの箇所(source_sentenceとその前後の文)でkey_phraseが実際に表している意味を、平易な英語1文で書く。"
              "key_phraseの語をそのまま繰り返さず言い換える。字義どおりの用法なら字義の意味、比喩・慣用・筆者が作った比喩ならその比喩が表す意味を書く。記事固有の固有名詞・数値は入れない。\n"
              "- naive_ja: key_phraseの英単語を、それぞれ日本語の対応語に置き換えただけの訳を、意味の解釈を加えずに書く。\n"
              "- naive_ja_conveys: 日本語だけを読む学習者が、naive_jaからmeaning_in_text_enの意味を受け取れるか。"
              "yes(同じ意味・同じ比喩が日本語でも通じる、または字義どおりの用法)/ partly(一部が落ちる)/ no(字義の動作・物の像しか伝わらず、本文での意味は伝わらない)。\n"
              "- japanese_gloss: yesなら、naive_jaをそのまま写さず、自然で平易な訳(英和辞典の定訳や日本語の慣用表現があればそれ)を選ぶ。"
              "partly/noなら、naive_jaの字義の像を使わず、meaning_in_text_enの意味を日本語の慣用表現か平易な短い言い換えで表す。"
              "key_phrase全体(目的語・修飾語を含む)の意味を落とさず、key_phraseと同じ品詞・同じ程度の長さの句にする(説明文・定義文にしない)。\n\n")


def x_schema(arm):
    s = json.loads(json.dumps(ga.GLOSS_ALIGNMENT_JSON_SCHEMA))
    it = s["schema"]["properties"]["items"]["items"]
    props = {}
    for k, v in it["properties"].items():
        if k == "japanese_gloss" and arm == "X2":
            props["meaning_in_text_en"] = {"type": "string"}
            props["naive_ja"] = {"type": "string"}
            props["naive_ja_conveys"] = {"type": "string", "enum": ["yes", "partly", "no"]}
        props[k] = v
    it["properties"] = props
    it["required"] = list(props)
    s["name"] = "kp_gloss_%s_trial05" % arm.lower()
    return s


def build_x_message(arm, tgt, article, prior=None):
    rules = (ga.preflight(True) or {})["rules"]
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
        items.append(d)
    person = ga.PERSON_CONSTRAINT_TEXT
    a1 = "current_japanese_glossがそうなっている場合は、指示2の『書き換えない』の例外として、current_gloss_consistent=falseにして書き換えてください。"
    a2 = "display_phrase_before_canonicalization・current_japanese_gloss・source_sentenceにある"
    a3 = ("source_sentenceは、辞書に複数の語義がある表現で、そのうちどの語義かを選ぶためだけに使い、"
          "人称の指示対象を決めるためには使わないでください。")
    assert a1 in person and a2 in person and a3 in person
    person = (person.replace(a1, "").replace(a2, "display_phrase_before_canonicalization・source_sentenceにある")
              .replace(a3, "source_sentenceと前後の文脈は語義と用法を決めるために使い、人称の指示対象を決めるためには使わないでください。"))
    return (X_HEAD + (person if any_person else "") + X_NEWGEN + (X2_MEANING if arm == "X2" else "") + X_OUTRULES +
            "【日本語グロスの規則(承認済み選定Promptと同一)】\n" + rules + "\n\n"
            "【対象項目】\n" + json.dumps(items, ensure_ascii=False, indent=2) + "\n\n【記事本文(参考)】\n" + article)


def build(arm, tgt, article):
    """戻り=(developer, message, schema)。"""
    if arm == "M":
        return G.M_DEVELOPER, G.build_m_message(tgt, article), G.M_SCHEMA
    if arm in ("X1", "X2"):
        return G.M_DEVELOPER, build_x_message(arm, tgt, article), x_schema(arm)
    msg = ga.build_user_message_corrected(tgt, article)
    schema, dev = ga.GLOSS_ALIGNMENT_JSON_SCHEMA, ga.DEVELOPER_MESSAGE
    if arm == "Cp":
        anchor = "【日本語グロスの規則(承認済み選定Promptと同一)】"
        assert anchor in msg
        msg = msg.replace(anchor, G.CP_BLOCK + anchor, 1)
        schema = G.cp_schema()
    return dev, msg, schema


def call(arm, kps, model=None):
    model = model or T.LUNA
    tgt = G._targets(kps)
    dev, msg, schema = build(arm, tgt, kps[0]["article"])
    r = T.client().responses.create(model=model, reasoning={"effort": EFFORT}, text={"format": {"type": "json_schema", **schema}},
                                    input=[{"role": "developer", "content": dev}, {"role": "user", "content": msg}])
    u = kx._usage_dict(r.usage)
    od = getattr(r.usage, "output_tokens_details", None)
    u["reasoning_tokens"] = getattr(od, "reasoning_tokens", None) if od is not None else None
    c = pricing.cost_jpy_for_call("openai", r.model or model, u.get("input_tokens"), u.get("cached_input_tokens"), u.get("output_tokens"))
    return tgt, json.loads(r.output_text)["items"], c, u


def validate_compat(tgt_item, resp_item):
    """Production validate_item_corrected(括弧禁止・数字・人称整合・qa・current_gloss_consistent型)への互換(M6)。X1/X2/B0/Cpのみ。"""
    try:
        v = ga.validate_item_corrected(resp_item, tgt_item)
        return {"valid": v["valid"], "reasons": v["reasons"]}
    except Exception as e:   # noqa: BLE001
        return {"valid": False, "reasons": ["validate_exception:%s" % e]}


EXTRA = ("meaning_in_text_en", "naive_ja", "naive_ja_conveys", "usage_in_sentence", "usage_meaning_en", "gloss_alone_reading_en", "gloss_conveys",
         "current_gloss_consistent", "qa_reflects_all_key_phrase_words", "reasoning")


def run_gen(arm, reps, keys, cap, tag="", workers=2, max_calls=None):
    A = all_kps5()
    groups = {}
    for k in keys:
        groups.setdefault(G.art_id(A[k]), []).append(A[k])
    done = load_res()
    jobs = [(rep, g) for rep in reps for g in groups.values() if any((arm, kp["key"].lower(), rep) not in done for kp in g)]
    if max_calls:
        jobs = jobs[:max_calls]
    print(arm, "gen jobs", len(jobs), "reps", reps, flush=True)

    def w(j):
        rep, g = j
        g = [kp for kp in g if (arm, kp["key"].lower(), rep) not in done]
        if stop():
            return ("SKIP_STOP", rep, g[0]["key"])
        est = PER_CALL_MAX
        with _lock:
            if total() + est > cap:
                _halt["flag"], _halt["why"] = True, "cap: cum %.3f + est %.2f > %.2f" % (total(), est, cap)
                return ("SKIP_CAP", rep, g[0]["key"])
        tgt, items, c, u = call(arm, g)
        with _lock:
            _append(LEDGER5, dict(kind="gen", arm=arm, tag=tag, keys=[x["key"] for x in g], rep=rep, usage=u, cost_jpy=round(c, 5), ts=time.strftime("%Y-%m-%dT%H:%M:%S")))
            arm_calls = [x["cost_jpy"] for x in read_jsonl(LEDGER5) if x.get("arm") == arm and x.get("kind") == "gen" and not str(x.get("tag", "")).startswith("pilot")]
            arm_calls += [x["cost_jpy"] for x in read_jsonl(LEDGER5) if x.get("arm") == arm and str(x.get("tag", "")).startswith("pilot")]
            if c > 2 * PER_CALL_MAX or (len(arm_calls) >= 4 and sum(arm_calls) / len(arm_calls) > PER_CALL_MAX):
                _halt["flag"], _halt["why"] = True, "per-call %.4f (>2x%.2f) or arm(%s) avg %.4f > %.2f" % (c, PER_CALL_MAX, arm, sum(arm_calls) / len(arm_calls), PER_CALL_MAX)
        by = {it.get("rank"): it for it in items}
        for i, kp in enumerate(g):
            it = by.get(i + 1) or {}
            rec = dict(arm=arm, key=kp["key"].lower(), rep=rep, kind="G", sent=kp["sent"], gloss=it.get("japanese_gloss"),
                       fields={k: it.get(k) for k in EXTRA if k in it}, call_cost_jpy=round(c, 5), n_in_call=len(g), tag=tag,
                       reasoning_tokens=u.get("reasoning_tokens"), output_tokens=u.get("output_tokens"), family=kp.get("family"), tier=kp.get("tier"))
            if arm != "M":
                rec["validate"] = validate_compat(tgt[i], it)
            with _lock:
                _append(RES5, rec)
        return (arm, rep, [x["key"] for x in g], round(c, 4))

    with ThreadPoolExecutor(workers) as ex:
        for f in as_completed([ex.submit(w, j) for j in jobs]):
            print(f.result(), "cum=%.3f" % total(), flush=True)
    if _halt["flag"]:
        print("HALT:", _halt["why"], flush=True)


def keys_of(a):
    if a.keys:
        return [k.strip() for k in a.keys.split("|")]
    if a.set == "R":
        return R_KEYS
    if a.set == "RCORE":
        return R_CORE
    if a.set == "H":
        order = heldout_order()
        return order[: a.nheld] if a.nheld else order
    raise SystemExit("--set R|RCORE|H or --keys")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("--arm", default="")
    ap.add_argument("--reps", default="1")
    ap.add_argument("--set", default="")
    ap.add_argument("--keys", default="")
    ap.add_argument("--nheld", type=int, default=0)
    ap.add_argument("--cap", type=float, default=CAP_JPY)
    ap.add_argument("--tag", default="")
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--max-calls", type=int, default=0)
    a = ap.parse_args()
    if a.cmd == "gen":
        run_gen(a.arm, [int(x) for x in a.reps.split(",")], keys_of(a), a.cap, tag=a.tag or a.arm, workers=a.workers, max_calls=a.max_calls or None)
    elif a.cmd == "total":
        print("cum=%.4f cap=%.2f" % (total(), a.cap))
    elif a.cmd == "dump":     # API 0: message/schemaを確認する
        A = all_kps5()
        ks = keys_of(a)
        kps = [A[k] for k in ks if G.art_id(A[k]) == G.art_id(A[ks[0]])]
        tgt = G._targets(kps)
        dev, msg, schema = build(a.arm, tgt, kps[0]["article"])
        print("[developer]", dev, "\n[schema]", json.dumps(schema["schema"]["properties"]["items"]["items"]["required"], ensure_ascii=False), "\n[message]\n" + msg)
