# JA-ASR-FALSE-NG-ROOT-FIX-02 委任_01B 統一評価ハーネス(API 0・socket guard・決定的)。事前登録=PREREGISTERED_01.md。
# 再現: PYTHONUTF8=1 .venv/Scripts/python.exe docs/research/JA-ASR-FALSE-NG-ROOT-FIX-02/eval_unified_01.py [out_json_path]
# 方式 M0=現行Production HEAD最終判定(adapter→統一judge[Primary→P1/P2→Secondary→最終AND gate]、F1+F2/E3/E4/R4R3込み)
#      M1=v2読み規則をPrimary+Secondary値等価層へ(Production層の差替+フォールバック[M1 ⊇ M0])
#      M2=β(b_light_proto_02.composite_judge)をM0の後段に追加  M3=P-1(v2のうち助詞は→わ/へ→えが必要な救済だけ。P-1 ⊂ v2)
#      M4=M1+M2  M5=判定前のOpenAI再転写(best-of-N)は正例のdraw集合でのみ集計(render側)
import collections, hashlib, json, os, sys
sys.path.insert(0, "."); sys.path.insert(0, "docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01"); sys.path.insert(0, "docs/research/FX-MOON-SHRINKING-RESELECT-REMAKE-01")
import eval_common_02 as E
import er007_ja_secondary_asr_01 as sec
import er078_asr_unified_judge_01 as uj
import er078_asr_value_guard_01 as vg
import proto_reading_compare_02 as P
import b_light_proto_02 as B
import n1_pairs_01 as N1
import sweep_cases_open333_02 as S333
import sweep_cases_open333_e4_02 as S333E4
import r4r3_eval_api0_01 as R4
import er066_ja_asr_orthographic_equivalence_01_cases as c1

J = "docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/"
FXD = "docs/research/FX-MOON-SHRINKING-RESELECT-REMAKE-01/"
OUT = "docs/research/JA-ASR-FALSE-NG-ROOT-FIX-02/"
MOON = "月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密"
RUNS = {"run_ms_03": "er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_ms_03/a2/narration/attempts/",
        "run_reselect_01": "er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_reselect_01/a2/narration/attempts/"}
ATT = {1: "japanese_title_attempt1_customb8f0ff16", 2: "japanese_title_attempt2_customb8f0ff16", 3: "japanese_title_attempt3_minimalfallback"}
PASSING = uj.PASSING_STATES
ELIG = ("p1_value_diff", "final_gate_value_diff", "p1_protected_diff:number_mismatch", "secondary_not_accepted")
_ORIG = sec._numeric_value_equivalence
USED = []


def make_layer(mode):
    def layer(canon, asr, cls):
        side = "secondary" if sys._getframe(1).f_code.co_name == "_secondary_accept" else "primary"
        r = P.pron_value_equivalence(canon, asr, cls=cls, expected_readings=None, side=side)
        if r.equal:
            ok = mode == "v2" or r.kind == "VALUE_ONLY" or (r.cause in ("A2_particle", "A3_value+A2_particle"))
            if ok:
                if r.kind == "PRON":
                    USED.append(f"{side}:{r.cause}")
                return P.to_classification(r, cls)
        return _ORIG(canon, asr, cls)      # フォールバック=Production層(M1 ⊇ M0、M3 ⊇ M0)
    return layer


def adapter(canon, prim, sec_text, wav, layer_mode):
    del USED[:]
    orig_az = sec._azure_stt_strict
    if sec_text is not None:
        sec._azure_stt_strict = lambda p, language="ja-JP", timeout_seconds=90: (sec_text, None)
    else:
        sec._azure_stt_strict = lambda p, language="ja-JP", timeout_seconds=90: (None, "api0_stub_no_secondary")
    sec._numeric_value_equivalence = make_layer(layer_mode) if layer_mode else _ORIG
    try:
        r = sec.evaluate_attempt_ja_with_cascade_detail(canon, prim, wav, cascade_enabled=True, attempt_ctx={"max_len": 400})
    finally:
        sec._azure_stt_strict = orig_az
        sec._numeric_value_equivalence = _ORIG
    j = r["asr_judgement"]
    st, rc = j.get("state"), j.get("reason_code")
    if st in PASSING:
        if st == "PASS_WITH_WARNING":
            cat, route = "PASS_W", "prod_warning:" + ",".join(j.get("warnings") or [])
        elif USED:
            cat, route = "PASS_W", "v2_pron:" + "|".join(sorted(set(USED)))
        else:
            cat, route = "PASS", "prod:" + str(rc)
    else:
        cat, route = "NG", str(rc)
    return {"cat": cat, "state": st, "reason": rc, "route": route, "sec_called": bool((j.get("secondary") or {}).get("called"))}


def all_methods(canon, prim, sec_text, wav):
    sha = hashlib.sha256(open(wav, "rb").read()).hexdigest()
    base = {"M0": adapter(canon, prim, sec_text, wav, None), "M1": adapter(canon, prim, sec_text, wav, "v2"), "M3": adapter(canon, prim, sec_text, wav, "p1")}
    out = {"M0": base["M0"], "M1": base["M1"], "M3": base["M3"]}
    for tag, src in (("M2", "M0"), ("M4", "M1")):
        b = dict(base[src])
        if b["cat"] == "NG" and sec_text and any(str(b["reason"]).startswith(e) for e in ELIG):
            r = B.composite_judge(canon, prim, sec_text, {"engine": "azure", "wav_sha256": sha, "model_id": "azure-speech-stt"})
            if r.equal:
                b = {"cat": "PASS_W", "state": "PASS_WITH_WARNING", "reason": "composite", "route": "beta_composite" + (":listen" if r.listen_required else ""),
                     "sec_called": b["sec_called"], "beta_needs_new_azure_call": (not b["sec_called"])}
            else:
                b["beta_blocked_by"] = r.blocked_by
        out[tag] = b
    return out


def load_positives():
    log = [json.loads(l) for l in open(J + "phase3_run/usage_log.jsonl", encoding="utf8")]
    reasr = json.load(open(FXD + "ja_title_reasr_01.out.json", encoding="utf8"))
    wl = {"run_ms_03": json.load(open(J + "whisper_local_3wav_01.json", encoding="utf8")), "run_reselect_01": json.load(open(FXD + "ja_title_local_whisper_reselect_01.json", encoding="utf8"))}
    pos = []
    for run, d in RUNS.items():
        for k in (1, 2, 3):
            wav = d + ATT[k] + ".wav"
            a = json.load(open(d + ATT[k] + ".json", encoding="utf8"))
            sha = hashlib.sha256(open(wav, "rb").read()).hexdigest()
            assert sha == a["sha256"], (run, k)
            oai = [("stored", a["asr_text"])]
            az = []
            st_az = (a.get("scg_info") or {}).get("secondary_transcript")
            if st_az:
                az.append(("stored_scg_info", st_az))
            if run == "run_ms_03":
                for r in log:
                    if r["item"].startswith(os.path.basename(wav)):
                        if r["stage"] == "A2_openai_moon_x3":
                            oai.append((f"phase3_redraw{r['item'].split('#')[1]}", r["text"]))
                        if r["stage"] in ("A1_azure_moon", "A3_azure_flip") and r["text"] not in [t for _, t in az]:
                            az.append(("phase3_azure", r["text"]))
            else:
                for r in reasr:
                    if r["wav"] == os.path.basename(wav):
                        for i, o in enumerate(r["openai"]):
                            oai.append((f"reasr_openai{i}", o["text"]))
                        if r["azure"]["text"] not in [t for _, t in az]:
                            az.append(("reasr_azure", r["azure"]["text"]))
            whisper = {kk.split(":")[0]: v for kk, v in wl[run].items() if kk.split(":")[1].startswith(os.path.basename(wav)[:-4])}
            pos.append({"run": run, "attempt": k, "wav": wav, "sha16": sha[:16], "openai": oai, "azure": az, "whisper_local": whisper})
    return pos


TAIL = "！その奥に潜む「岩の上着」の秘密"
UC6_DEF = {
    "U1_異なる発音": ["月のすわ、8,900本超", "月のしば、8,900本超", "月のつわ、8,900本超", "月のしあ、8,900本超", "月のしわし、8,900本超"],
    "U2_異なる数値": ["月のしわ、8,800本超", "月のしわ、890本超", "月のしわ、89,000本超", "月のしわ、8,090本超", "月のしわ、9,900本超"],
    "U3_助数詞違い": ["月のしわ、8,900個超", "月のしわ、8,900枚超", "月のしわ、8,900人超", "月のしわ、8,900冊超", "月のしわ、8,900円超"],
    "U6_同音異表記便乗": ["月の詩は、8,800本超", "月の詩は、890本超", "月の氏は、8,900個超", "月の死は、8,900本超", "月の詩は、8,900円超"],
}
UC6_FULL = {
    "U4_語句脱落": ["月のしわ、8,900本", "月のしわ、8,900本超！その奥に潜む秘密", "月のしわ、その奥に潜む「岩の上着」の秘密", "月のしわ、8,900本超！その奥に「岩の上着」の秘密", "月、8,900本超！その奥に潜む「岩の上着」の秘密"],
    "U5_意味を変える読み違い": ["月のしわ、8,900本超！その奥に潜む「岩の下着」の秘密", "月のしわ、8,900本超！その奥に潜む「石の上着」の秘密", "月のしわ、8,900本超！その奥に潜む「岩の上着」の秘書",
                    "月のしわ、8,900本未満！その奥に潜む「岩の上着」の秘密", "月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密ではない"],
    "U6_同音異表記便乗": ["月の死は、8,900本超！その奥に潜む「岩の下着」の秘密", "月の詩は、8,900本超！その奥に潜む秘密"],
}
UC6 = []
for cat, items in UC6_DEF.items():
    for a in items:
        UC6.append((cat, MOON, a + TAIL))
for cat, items in UC6_FULL.items():
    for a in items:
        UC6.append((cat, MOON, a))
UC6 += [("U2_異なる数値", "売上は1,200円で利益は3,500円です", "売上は1,200円で利益は3,600円です"), ("U2_異なる数値", "売上は1,200円で利益は3,500円です", "売上は12,000円で利益は3,500円です"),
        ("U2_異なる数値", "参加者は3,000人でした", "参加者は300人でした"), ("U3_助数詞違い", "参加者は3,000人でした", "参加者は3,000個でした"),
        ("U3_助数詞違い", "犬が三匹いる", "犬が三頭いる"), ("U3_助数詞違い", "本を三冊買う", "本を三本買う"),
        ("U4_語句脱落", "参加者は3,000人でした", "参加者は3,000人"), ("U4_語句脱落", "売上は1,200円で利益は3,500円です", "売上は1,200円です"),
        ("U5_意味を変える読み違い", "売上は増えました", "売上は減りました"), ("U5_意味を変える読み違い", "彼女は来なかった", "彼女は来た"),
        ("U1_異なる発音", "橋を渡る", "箸を渡る"), ("U1_異なる発音", "学校へ行く", "学校に行く"),
        ("U6_同音異表記便乗", "今日は晴れです", "京は晴れです"), ("U6_同音異表記便乗", "私は本を読みます", "私は本を読みません")]


def corpus():
    C = []

    def txt(group, truth, tag, canon, asr):
        C.append({"group": group, "truth": truth, "tag": tag, "canon": canon, "primary": asr, "scen": {"P_only": None, "PS_same": asr, "S_canon": canon}})
    for p in N1.all_pairs():
        txt("N1_150", "UNL" if p["kind"] == "structural" else "NEG", p["type"], p["canon"], p["asr"])
    for cls, canon, asr, tag, note in S333.CASES:
        txt("OPEN333_sweep8", "NEG" if tag == "block" else "POS", f"class{cls}:{note}", canon, asr)
    for r in S333E4.build():
        txt("OPEN333_E4", {"neg_hira": "NEG", "e4n_keep_reject": "NEG", "out_of_scope": "UNL"}[r["kind"]], r["kind"] + ":" + r["label"], r["canon"], r["asr"])
    for canon, asr, t in R4.EXTRA_NEG:
        txt("R4R3_extra18", "NEG", t, canon, asr)
    for canon, asr, t in R4.POS:
        txt("R4R3_pos", "POS", t, canon, asr)
    for t in c1.POSITIVE:
        txt("er066_POSITIVE", "POS", t[2], t[0], t[1])
    for cat, canon, asr in UC6:
        txt("UC6_" + cat, "NEG", cat, canon, asr)
    import er066_ja_asr_orthographic_equivalence_01_trial as tr
    for u in ["day", "person", "hour", "minute", "month", "year", "age", "kai", "ken", "ko", "week", "yen", "mai", "dai", "bai", "do", "hon", "haku", "ban", "go"]:
        surf = vg.COUNTERS[u][0]
        for n in (1, 2, 3, 5, 10, 20, 100, 1000):
            rd = [x for x in tr._cands(n, u) if x]
            if not rd:
                continue
            m = n + 1
            txt("OPEN517_wrongvalue_kana", "NEG", f"{u}:{n}->{m}", f"それは{m}{surf}です", f"それは{rd[0]}です")
    S_OK = "杉野氏は8900本超。その奥に潜む岩の上着の秘密。"
    TL = "。その奥に潜む岩の上着の秘密。"
    X = []
    for v in ["8,800", "89,000", "8,090", "9,900", "千九百", "八万九千", "8000800", "8000句800", "8万9千", "890"]:
        pv = f"月のしわ、{v}本超{TL}"
        X += [("value_wrong:P(S=原稿値)", MOON, pv, S_OK), ("value_wrong:Both", MOON, pv, pv), ("value_wrong:S_only", MOON, "月のしわ、8,900本超" + TL, pv)]
    for rd_ in ["すわ", "しば", "し", "巣は", "しわし"]:
        for pv in ("8000900", "8,900", "8000九百"):
            X.append(("reading_wrong:P(S=原稿値)", MOON, f"月の{rd_}、{pv}本超{TL}", S_OK))
    X += [("irregular", "三日待った", "3日待った。", "3日待った。"), ("irregular", "三日待った", "三日間待った。", "3日待った。"), ("irregular", "二十歳になった", "20歳になった", "20歳になった"),
          ("irregular", "十月一日に会う", "10月1日に会う", "10月1日に会う"), ("negation", "三人は行かない", "3人は行く", "3人は行かない"), ("negation", "三人は行かない", "3人は行かない", "3人は行く"),
          ("counter", "犬が三匹いる", "犬が三頭いる", "犬が三匹いる"), ("counter", "本を三冊買う", "本を三本買う", "本を3冊買う"),
          ("value", "売上は1,200円です", "売上は1,300円です", "売上は1,200円です"), ("value", "売上は1,200円です", "売上は12,000円です", "売上は1,200円です")]
    C2_, S2_, C3_, S3_ = "売上は1,200円で利益は3,500円です", "売上は1200円で利益は3500円です", "1,200円と1,200円を払う", "1200円と1200円を払う"
    for t, p, s in [("first_explained+second_contradiction", "売上は1000200円で利益は4,500円です", S2_), ("first_contradiction+second_explained", "売上は1,300円で利益は3000五百円です", S2_),
                    ("second_garble_sum_mismatch", "売上は1,200円で利益は3000200円です", S2_), ("first_garble_sum_mismatch", "売上は1000500円で利益は3,500円です", S2_),
                    ("secondary_order_swapped", "売上は1000200円で利益は3,500円です", "売上は3500円で利益は1200円です"), ("secondary_missing_atom", "売上は1000200円で利益は3,500円です", "売上は1200円です"),
                    ("secondary_extra_atom", "売上は1000200円で利益は3,500円です", "売上は1200円で利益は3500円で費用は100円です"), ("secondary_repeated_atom", "売上は1000200円で利益は3,500円です", "売上は1200円で利益は3500円と3500円です"),
                    ("secondary_second_value_wrong", "売上は1000200円で利益は3,500円です", "売上は1200円で利益は3,600円です"), ("primary_order_swapped", "利益は3,500円で売上は1000200円です", S2_),
                    ("primary_extra_number", "売上は1000200円で利益は3,500円です。費用は100円", S2_), ("primary_second_atom_missing", "売上は1000200円です", S2_)]:
        X.append(("multi:" + t, C2_, p, s))
    for t, p, s in [("second_garble_wrong", "1000200円と1000500円を払う", S3_), ("first_garble_wrong", "1000500円と1000200円を払う", S3_), ("primary_second_missing", "1000200円を払う", S3_),
                    ("secondary_missing", "1000200円と1000200円を払う", "1200円を払う"), ("second_value_wrong", "1000200円と1,300円を払う", S3_)]:
        X.append(("same_counter:" + t, C3_, p, s))
    for c, p, s, t in [("売上は1,200円です", "売上は1000200円です", "売上はせんにひゃく円です", "FB:secondary_kana_numeral"), ("売上は1,200円です", "売上は1000200円です", "売上は千にひゃく円です", "FB:secondary_kana_mixed"),
                       ("売上は8,900円です", "売上は8000900円です", "売上は8000 900円です", "FB:secondary_space_run"), ("売上は8,900円です", "売上は8000900円です", "売上は8万900円です", "FB:secondary_man"),
                       ("売上は8,900円です", "売上は8000900円です", "売上は8万9千円です", "FB:secondary_man_sen"), ("売上は8,900円です", "売上は8000 900円です", "売上は8900円です", "FB:primary_space_run"),
                       ("売上は8,900円です", "売上は8000万900円です", "売上は8900円です", "FB:primary_man_in_run"), ("売上は8,900円です", "売上は8万900円です", "売上は8900円です", "FB:primary_man_kanji"),
                       ("売上は8,900円です", "売上は8000九万円です", "売上は8900円です", "FB:primary_kanji_man"), ("売上は12,300円です", "売上は12000300円です", "売上は12300円です", "FB:front_fragment_not_d10k"),
                       ("売上は100,500円です", "売上は100200300円です", "売上は100500円です", "FB:three_fragments"), ("売上は9,800円です", "売上は80九百円です", "売上は9800円です", "FB:front_fragment_80"),
                       ("売上は1,200円で犬が3匹います", "売上は1000200円で犬が3匹います", "売上は1200円で犬がさんびきいます", "FB:secondary_kana_numeral_other_atom"),
                       ("売上は1,200円で犬が3匹います", "売上は1000200円で犬が3匹います", "売上は1200円で犬がみっつです", "FB:secondary_kana_tsu")]:
        X.append((t, c, p, s))
    for t, c, p, s in X:
        C.append({"group": "BLIGHT_synthetic", "truth": "NEG", "tag": t, "canon": c, "primary": p, "scen": {"explicit": s}})
    log = [json.loads(l) for l in open(J + "phase3_run/usage_log.jsonl", encoding="utf8")]
    clips = {c["id"]: c for c in json.load(open(J + "n3_clips_01.json", encoding="utf8"))}
    for r in log:
        if r["stage"] == "N3_asr":
            c = clips[r["item"]]
            C.append({"group": "N3_real30", "truth": "NEG", "tag": c["type"] + "|tts=" + c["tts_input"], "canon": c["canonical"], "primary": r["openai_text"], "scen": {"real": r["azure_text"]}})
    for x in json.load(open(J + "ng_pool_cases_01.json", encoding="utf8")):
        if x.get("secondary") and x.get("primary") and x.get("canon"):
            C.append({"group": "HIST_43pairs", "truth": "UNL", "tag": os.path.basename(x["file"]) + ":" + str(x.get("seg")), "canon": x["canon"], "primary": x["primary"], "scen": {"real": x["secondary"]}})
    seen, out = set(), []
    for c in C:
        k = (c["group"], c["canon"], c["primary"], json.dumps(c["scen"], sort_keys=True, ensure_ascii=False))
        if k in seen:
            continue
        seen.add(k)
        out.append(c)
    return out


def main():
    outp = sys.argv[1] if len(sys.argv) > 1 else OUT + "eval_unified_01.out.json"
    E.api0_guard_on()
    dwav = E.dummy_wav()
    res = {"head_consts": {"READING_MATCH_FINAL_GATE": uj.READING_MATCH_FINAL_GATE, "JA_SECONDARY_VALUE_EQUIVALENCE_ENABLED": sec.JA_SECONDARY_VALUE_EQUIVALENCE_ENABLED}}
    prow = []
    for p in load_positives():
        pairs = []
        for otag, ot in p["openai"]:
            for ai, (atag, at) in enumerate(p["azure"]):
                pairs.append({"openai_tag": otag, "openai": ot, "azure_tag": atag, "azure": at, "res": all_methods(MOON, ot, at, p["wav"]), "stored": (otag == "stored" and ai == 0)})
            pairs.append({"openai_tag": otag, "openai": ot, "azure_tag": "none", "azure": None, "res": all_methods(MOON, ot, None, p["wav"]), "stored": False, "p_only": True})
        prow.append({k: p[k] for k in ("run", "attempt", "sha16", "wav", "openai", "azure", "whisper_local")} | {"pairs": pairs})
    res["positives"] = prow
    rows = []
    for c in corpus():
        for sn, st in c["scen"].items():
            rows.append({"group": c["group"], "truth": c["truth"], "tag": c["tag"], "canon": c["canon"], "primary": c["primary"], "scenario": sn, "secondary": st,
                         "res": all_methods(c["canon"], c["primary"], st, dwav)})
    res["rows"] = rows
    E.api0_guard_off()
    s = json.dumps(res, ensure_ascii=False, sort_keys=True, indent=1)
    open(outp, "w", encoding="utf-8", newline="\n").write(s)
    print("sha256", hashlib.sha256(s.encode("utf-8")).hexdigest(), "rows", len(rows), "pos_pairs", sum(len(p["pairs"]) for p in prow))


if __name__ == "__main__":
    main()
