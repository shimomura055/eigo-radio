# 委任_01: 修正案P1の offline what-if (API 0 / Production module無変更。monkeypatchは本processの中だけ)
# P1 = M1 `_post_check`(er006_m1_multi_candidate_01.py:407)の「exact以外の置換はf1_explainedに含まれること(benign吸収は不受理、OF-178)」を、
#      「置換後の文が既存Production判定(classify_asr_match)でshould_passになり、F1残差0であること」へ置き換えた場合の判定。
#      = Melo(benign複数形で現行自動PASS)と同じ音素列(M EH L OW)の Mello/Mellow に、Meloと同じ判定を与える(2026-10-13合意の設計原則「同じ音素列には同じ判定」)。
#      新しい許容語を増やすのではなく、Meloが既に受理されている文脈に限って綴り違い同音素列を揃えるだけだが、OF-178(Opus BLOCKER・採用済み)の撤回を伴うため仕様変更候補。
# 実行: .venv\Scripts\python.exe -X utf8 <this file> --out <json>   (cwd=repo root)
import sys, os, json, argparse, collections, hashlib
sys.path.insert(0, os.getcwd())
import er021_en_asr_semantic_equivalence_production_01 as se
se.append_telemetry_log = lambda *a, **k: None
import er006_m1_multi_candidate_01 as m1
import er011_b1_connected_speech_validator_01 as csv3
import er006_preprod_hardening_01_validation as val
import er006_pronunciation_ledger_01 as pl

E21 = "er021_output/en_asr_semantic_equivalence_production_wiring_01/telemetry.jsonl"
ASRJ = "docs/research/FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01/asr_consistency_part3c1_01_result.json"
LEDGER = "er006_output/pronunciation_ledger_01/ledger.json"
CANON = ("He remembered the hands held out for the chains. His friend trusted him without asking for another promise. "
         "Water came slowly through a crack in the rock. Melos drank, got onto his knees, and stood up. He managed one step, "
         "then took another. At the city gates, the bell rang for his friend's death. He raced to the square, where the sword "
         "was already raised above his friend.")
ORIG_POST = m1._post_check


def p1_post_check(canonical, asr2, subs):
    cs2 = csv3.classify_connected_speech(canonical, asr2)
    if cs2.get("f1_residual"):
        return False, m1.R_POST_RESIDUAL, cs2
    c2 = val.classify_asr_match(canonical, asr2)
    if not c2.should_pass:
        return False, m1.R_NOT_EXPLAINED, cs2
    return True, None, cs2


def run(canon, asr, frozen, patched):
    m1._post_check = p1_post_check if patched else ORIG_POST
    try:
        cls = val.classify_asr_match(canon, asr)
        r = m1.m1_multi_candidate_judge(canon, asr, frozen, base_cls=cls)
        return r.accepted, r.reason
    finally:
        m1._post_check = ORIG_POST


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    s0 = sha(LEDGER)
    snap = pl._load()
    frozen = m1.freeze_candidates(CANON, ledger_snapshot=snap, segment_started_at="2026-10-19T12:00:00")
    aj = json.load(open(ASRJ, encoding="utf8"))["runs"]
    e21 = [json.loads(l) for l in open(E21, encoding="utf8")]
    texts = {"att2_primary_PRODUCTION(E21行9613) 'Mello drank'": e21[9612]["asr"],
             "att2_azure 'Mellows drank'": aj["run04_att2"]["azure_with_phraselist"]["text"],
             "att3_primary 'Mello drank'": aj["run04_att3"]["primary_openai"]["text"],
             "att3_azure 'Mellow strength'": aj["run04_att3"]["azure_with_phraselist"]["text"],
             "run03_PASS_primary 'Mellow drank'": aj["run03_att1_PASS_pre_slowdown"]["primary_openai"]["text"]}
    out = {"recording_what_if": {}}
    for k, t in texts.items():
        out["recording_what_if"][k] = {"current_M1": run(CANON, t, frozen, False), "P1_M1": run(CANON, t, frozen, True)}
    # 負例(P1が広げる受理面を可視化する fixture: 記事非依存の文)
    fx = []

    def ctx(name, verb):
        return CANON.replace("Melos drank,", "%s %s," % (name, verb))
    for fname, verb, asrname, extra, desc in [
        ("非歯擦音後続 Melos left -> Mello left", "left", "Mello", None, "現行M1=不受理(OF-178)、P1=Melo(現行自動PASS)と同判定になるか"),
        ("非歯擦音後続 Melos left -> Melo left (現行Production)", "left", "Melo", None, "現行でPASS(長文ではbenign複数形+ratio)"),
        ("歯擦音後続 Melos said -> Mello said", "said", "Mello", None, "現行M1受理(Pattern A)"),
        ("母音差 Melos -> Milo (別音素列)", "left", "Milo", None, "どちらも不受理であること"),
        ("母音差 Melos -> Malos", "left", "Malos", None, "どちらも不受理であること"),
        ("同音素列 + 別内容語 (Mello took)", "left", "Mello", ("left,", "took,"), "どちらも不受理であること"),
        ("語末脱落が他の語 (Melos -> Mel)", "left", "Mel", None, "どちらも不受理であること")]:
        canon = ctx("Melos", verb)
        asr = ctx(asrname, verb)
        if extra:
            asr = asr.replace(extra[0], extra[1])
        fz = m1.freeze_candidates(canon, ledger_snapshot=snap, segment_started_at="2026-10-19T12:00:00")
        base = val.classify_asr_match(canon, asr).classification
        fx.append({"name": fname, "desc": desc, "base_classification": base, "current_M1": run(canon, asr, fz, False), "P1_M1": run(canon, asr, fz, True)})
    out["fixtures"] = fx
    # 実データ census: E21 telemetry 全行(canonical/asr全文あり)で、現行M1と P1-M1 の受理数を比較
    fcache = {}
    cur_acc = p1_acc = rows_n = 0
    newly = collections.OrderedDict()
    for r in e21:
        if r.get("sub_reason") != "entity_only" or not r.get("canonical") or not r.get("asr"):
            continue
        rows_n += 1
        c, t = r["canonical"], r["asr"]
        if c not in fcache:
            fcache[c] = m1.freeze_candidates(c, ledger_snapshot=snap, segment_started_at="2026-10-19T12:00:00")
        try:
            ca, _ = run(c, t, fcache[c], False)
            pa, _ = run(c, t, fcache[c], True)
        except Exception:
            continue
        cur_acc += int(ca)
        p1_acc += int(pa)
        if pa and not ca:
            d = r.get("diff_span") or {}
            key = (d.get("canonical_word"), d.get("asr_word"))
            newly[key] = newly.get(key, 0) + 1
    out["census_E21_entity_only_rows"] = {"rows_evaluated": rows_n, "current_M1_accept": cur_acc, "P1_M1_accept": p1_acc,
                                         "newly_accepted_by_P1_unique_pairs": [{"canonical": k[0], "asr": k[1], "rows": v} for k, v in newly.items()]}
    out["ledger_sha256_unchanged"] = (s0 == sha(LEDGER))
    json.dump(out, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for k, v in out["recording_what_if"].items():
        print(k, v)
    for f in fx:
        print(f["name"], f["current_M1"], f["P1_M1"])
    print(out["census_E21_entity_only_rows"])
    print("ledger unchanged:", out["ledger_sha256_unchanged"])


main()
