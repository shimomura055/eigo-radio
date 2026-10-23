# -*- coding: utf-8 -*-
"""FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_14: 課題① 生成arm(B0/M/Cp)・検査・再生成・盲検表 (DEV専用、er112基盤)。
Production file(er003_*/er019_*/runner)は編集しない。importして呼ぶだけ。費用台帳=er112_output/kp_gm_trial_04/paid_calls.jsonl(上限60円は課題②・E2Eを含む全体)。
arm:
  B0 = 現行(Production gloss生成message・schema、luna high)。既存のTrial_03/02 G0出力を再利用し、無いKPだけ新規生成。
  C  = B0出力 -> 独立検査(inspect, v2low) -> flag項目のみ attempt 2 で再生成(previous_attempt_rejected機構)。未flagはB0とバイト同一。
  C-recheck = Cの再生成出力を再検査し、まだflagなら元のB0を採用(FLAGGED_UNREPAIRED)。事後比較。
  Cp = C' 同一callの自己監査欄(japanese_glossの後に追加)。flag時は同じ再生成経路。
  M  = 新規生成項目だけ再整合用の指示・例・qa名を除いたmessage(OF-D5-06)。追加call 0。
"""
from __future__ import annotations

import argparse, json, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import er112_kp_gm_trial_04 as X
from er112_kp_gm_trial_04 import (OUT, ROOT, T, USAGES, CONVEYS, _append, _lock, ledger_add, read_jsonl, stop, total, all_kps)
import hashlib
import er003_key_words_gloss_alignment as ga

RES = OUT / "results.jsonl"


def art_id(kp):
    return hashlib.sha256(kp["article"].encode("utf-8")).hexdigest()[:10]


def load_res():
    d = {}
    for r in read_jsonl(RES):
        d[(r["arm"], r["key"], r["rep"])] = r
    return d


def res_add(rec):
    with _lock:
        _append(RES, rec)


def _targets(kps):
    return [{"rank": i + 1, "key_phrase": kp["key"], "display_phrase": kp["display"], "japanese_gloss": None, "source_sentence": kp["sent"],
             "fulltext_source_ref": "fulltext_exact_v1"} for i, kp in enumerate(kps)]


# --- M: 再整合用(consistency)の指示・例・qa名を除いた新規生成専用message。承認済みgloss規則(rules)・人称規則は維持。
M_DEVELOPER = "英語学習教材のKey Phraseに付ける日本語グロスを書いてください。"
M_SCHEMA = {"name": "kp_gloss_m_trial04", "strict": True, "schema": {"type": "object", "properties": {"items": {"type": "array", "items": {
    "type": "object", "properties": {"rank": {"type": "integer"}, "japanese_gloss": {"type": "string"}}, "required": ["rank", "japanese_gloss"], "additionalProperties": False}}},
    "required": ["items"], "additionalProperties": False}}
M_HEAD = ("以下の各英語key_phraseは、教材として最終確定した英語表現です。各項目について、日本語グロス(japanese_gloss)を新しく書いてください(全項目、日本語グロスは未生成です)。\n\n"
          "key_phrase単体で他の文脈でも再利用できる自然な訳にし、本文固有の固有名詞・文脈の追加はしないでください。\n\n")
M_NEWGEN = ("【新規生成の規則】\n- source_sentenceは、辞書に複数の語義がある表現で、そのうちどの語義かを選ぶためだけに使ってください"
            "(文中の固有名詞・文脈の追加はしないでください)。\n\n")


def build_m_message(tgt, article, prior=None):
    rules = (ga.preflight(True) or {})["rules"]
    items, any_person = [], False
    for it in tgt:
        d = {"rank": it["rank"], "key_phrase": it["key_phrase"], "display_phrase_before_canonicalization": it.get("display_phrase"), "source_sentence": it.get("source_sentence", "")}
        ind = ga.indefinite_person_tokens(it.get("key_phrase"))
        if ind:
            any_person = True
            d["indefinite_person_tokens_in_key_phrase"] = ind
            pairs = ga.person_generalization_pairs(it)
            if pairs:
                d["person_generalization"] = pairs
        if prior and it["rank"] in prior:
            d["previous_attempt_rejected"] = {"gloss": prior[it["rank"]].get("gloss"), "reasons": list(prior[it["rank"]].get("reasons") or [])}
        items.append(d)
    person = ga.PERSON_CONSTRAINT_TEXT
    a1 = "current_japanese_glossがそうなっている場合は、指示2の『書き換えない』の例外として、current_gloss_consistent=falseにして書き換えてください。"
    a2 = "display_phrase_before_canonicalization・current_japanese_gloss・source_sentenceにある"
    assert a1 in person and a2 in person
    person = person.replace(a1, "").replace(a2, "display_phrase_before_canonicalization・source_sentenceにある")
    prior_block = "previous_attempt_rejected(ある項目のみ)は、前回の応答が検証で却下された理由です。同じ誤りを繰り返さないでください。\n\n" if prior else ""
    return (M_HEAD + (person if any_person else "") + M_NEWGEN + prior_block + "【日本語グロスの規則(承認済み選定Promptと同一)】\n" + rules + "\n\n"
            "【対象項目】\n" + json.dumps(items, ensure_ascii=False, indent=2) + "\n\n【記事本文(参考)】\n" + article)


# --- Cp: G0 message + 自己監査欄(japanese_glossの後ろに追加。生成順でglossは影響を受けない)
CP_BLOCK = ("【自己点検(japanese_glossを書いた直後に、同じ項目の中で必ず行う)】\n"
            "1. usage_in_sentence: source_sentenceの中でkey_phraseが表している用法。literal=字義どおり / figurative=慣用・比喩 / term_or_collocation=用語・コロケーション・句動詞など。\n"
            "2. usage_meaning_en: source_sentenceの文脈でkey_phraseが表している意味を、key_phraseの内容語・活用形・同じ語源の語を使わず、平易な英語1文で言い換える。\n"
            "3. gloss_alone_reading_en: **いま書いたjapanese_glossの日本語だけ**を読んだ日本語学習者が受け取る意味を、key_phraseの内容語・活用形・同じ語源の語を使わず、平易な英語1文で言い換える。"
            "日本語として確立した慣用句・比喩は比喩の意味として、字義どおりの動作・物の像として受け取られる日本語は字義どおりの像として受け取る。\n"
            "4. gloss_conveys: 3が2と同じ意味か。same_meaning / literal_image_only(字義の動作・物の像しか伝えず、本文での比喩・慣用の意味を伝えていない) / narrower / broader / other。\n\n")


def cp_schema():
    s = json.loads(json.dumps(ga.GLOSS_ALIGNMENT_JSON_SCHEMA))
    it = s["schema"]["properties"]["items"]["items"]
    extra = {"usage_in_sentence": {"type": "string", "enum": USAGES}, "usage_meaning_en": {"type": "string"}, "gloss_alone_reading_en": {"type": "string"},
             "gloss_conveys": {"type": "string", "enum": CONVEYS}}
    props = {}
    for k, v in it["properties"].items():
        props[k] = v
        if k == "japanese_gloss":
            props.update(extra)
    it["properties"] = props
    it["required"] = list(props)
    s["name"] = "kp_gloss_cp_trial04"
    return s


def gloss_gen(arm, kps, prior=None, model=None, effort="high"):
    """arm: B0 / M / Cp。prior={rank:{gloss,reasons}}ならattempt 2(previous_attempt_rejected)。戻り=(items, cost, usage)。"""
    model = model or T.LUNA
    tgt = _targets(kps)
    article = kps[0]["article"]
    if arm == "M":
        msg, schema, dev = build_m_message(tgt, article, prior), M_SCHEMA, M_DEVELOPER
    else:
        msg = ga.build_user_message_corrected(tgt, article, prior=prior)
        schema, dev = ga.GLOSS_ALIGNMENT_JSON_SCHEMA, ga.DEVELOPER_MESSAGE
        if arm == "Cp":
            anchor = "【日本語グロスの規則(承認済み選定Promptと同一)】"
            assert anchor in msg
            msg = msg.replace(anchor, CP_BLOCK + anchor, 1)
            schema = cp_schema()
    r = T.client().responses.create(model=model, reasoning={"effort": effort}, text={"format": {"type": "json_schema", **schema}},
                                    input=[{"role": "developer", "content": dev}, {"role": "user", "content": msg}])
    c, u = T.cost_of(r, model)
    return json.loads(r.output_text)["items"], c, u


def run_gen(arm, reps, keys, cap, tag=""):
    A = all_kps()
    groups = {}
    for k in keys:
        groups.setdefault(art_id(A[k]), []).append(A[k])
    done = load_res()
    jobs = [(rep, g) for rep in reps for g in groups.values() if any((arm, kp["key"].lower(), rep) not in done for kp in g)]
    print(arm, "gen jobs", len(jobs), flush=True)

    def w(j):
        rep, g = j
        g = [kp for kp in g if (arm, kp["key"].lower(), rep) not in done]
        if stop() or total() >= cap:
            return ("SKIP", rep, g[0]["key"])
        items, c, u = gloss_gen(arm, g)
        ledger_add(dict(kind="gen", arm=arm, tag=tag, keys=[x["key"] for x in g], rep=rep, usage=u, cost_jpy=round(c, 5), ts=time.strftime("%Y-%m-%dT%H:%M:%S")))
        by = {it["rank"]: it for it in items}
        for i, kp in enumerate(g):
            it = by.get(i + 1) or {}
            res_add(dict(arm=arm, key=kp["key"].lower(), rep=rep, kind="G", sent=kp["sent"], gloss=it.get("japanese_gloss"),
                         audit={k: it.get(k) for k in ("usage_in_sentence", "usage_meaning_en", "gloss_alone_reading_en", "gloss_conveys") if k in it},
                         call_cost_jpy=round(c, 5), n_in_call=len(g), tag=tag))
        return (arm, rep, [x["key"] for x in g], round(c, 4))
    with ThreadPoolExecutor(5) as ex:
        for f in as_completed([ex.submit(w, j) for j in jobs]):
            print(f.result(), "cum=%.3f" % total(), flush=True)


def b0_outputs(keys):
    """B0 = 現行G0。既存(Trial_03 G0 2rep、Trial_02 G0)を優先して再利用し、無いものはOUT/results.jsonlのB0(新規生成)。戻り {(key,rep):row}"""
    out = {}
    for src in (ROOT / "er112_output/kp_gm_trial_03/results.jsonl", ROOT / "er112_output/kp_gm_trial_02/results.jsonl"):
        for r in read_jsonl(src):
            if r.get("kind") == "G" and r.get("arm") == "G0" and r["key"] in keys and r.get("gloss") and r["rep"] in (1, 2):
                out.setdefault((r["key"], r["rep"]), dict(r, src=str(src.parent.name)))
    for (arm, k, rep), r in load_res().items():
        if arm == "B0" and k in keys and r.get("gloss"):
            out.setdefault((k, rep), dict(r, src="trial04"))
    return out


def trial_keys(a):
    d = json.load(open(OUT / "strata_04.json", encoding="utf-8"))
    return d["trial_set"] if not a.keys else [k.strip() for k in a.keys.split("|")]


def cmd_gen(a):
    keys = trial_keys(a)
    reps = [int(x) for x in a.reps.split(",")]
    if a.arm == "B0":
        have = b0_outputs(set(keys))
        need = [k for k in keys if any((k, r) not in have for r in reps)]
        print("B0 existing reuse:", sum(1 for k in keys for r in reps if (k, r) in have), "need keys:", len(need))
        run_gen("B0", reps, need, a.cap, tag=a.tag or "b0")
    else:
        run_gen(a.arm, reps, keys, a.cap, tag=a.tag or a.arm)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("--tag", default="")
    ap.add_argument("--cap", type=float, default=X.CAP_JPY)
    ap.add_argument("--arm", default="")
    ap.add_argument("--reps", default="1,2")
    ap.add_argument("--keys", default="")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    if a.cmd == "gen":
        cmd_gen(a)
