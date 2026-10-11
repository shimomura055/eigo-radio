# -*- coding: utf-8 -*-
"""ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01 委任_04B Trial B: 日英共通の意図的誤読テスト(Trial隔離、Production変更なし)。

正しい原稿(canonical)に対し、意図的に誤った文面(spoken)でTTS合成し、その音声を「正しい原稿」で既存validatorに掛けて
Primary(gpt-4o-mini-transcribe)/Azure(Phrase Listなし、一部ENのみPhrase Listあり)/local faster-whisper medium が
原稿に引きずられて誤PASSするかを測る。対照(spoken==canonical)で誤NGも測る。

隔離: er005_cost_logger.install()を呼ばない(Production telemetry無書込)。attempt_history/queue/Master Store 非接触。
出力は er058_output/trial_abc/ のみ。--approved-budget-jpy 必須(実費がこれを超える前にSTOP)。
使い方: --mode mock(API無し乾式) / --mode real --approved-budget-jpy 20 / --mode estimate
"""
import argparse, concurrent.futures as cf, hashlib, io, json, os, re, sys, wave

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
OUT = os.path.join(ROOT, "er058_output", "trial_abc")
AUDIO = os.path.join(OUT, "audio")
RES = os.path.join(OUT, "trial_b_results_01.json")
COST = os.path.join(OUT, "cost_actual_B_01.json")

USD_JPY = 160
TTS_MODEL = "gemini-3.8-flash-lite-tts"
TTS_OUT_PER_M = 6.0      # USD / 1M audio output tokens (25 tok/s)
TTS_IN_PER_M = 0.5
AZURE_PER_HOUR = 1.0     # USD / hour of audio
OPENAI_ASR_PER_MIN = 0.003  # USD / min (gpt-4o-mini-transcribe, 公称概算)

EN_STYLE_KEY = "FULL_STORY"
EN_SLOWER = ("Speak at a slightly slower, relaxed pace than natural adult narration, while keeping the delivery smooth, "
             "conversational, and natural. Do not exaggerate pauses or sound instructional.")

# (id, type, canonical, spoken_misread, has_control, phrase_list_phrases or None)
EN = [
    ("en_num1", "number", "I waited two hours.", "I waited three hours.", True, None),
    ("en_num2", "number", "We sold two cups.", "We sold ten cups.", False, None),
    ("en_num3", "number", "It took nine months.", "It took five months.", True, None),
    ("en_num4", "number", "She bought two bags.", "She bought three bags.", False, None),
    ("en_neg1", "negation", "She can't come today.", "She can come today.", True, None),
    ("en_neg2", "negation", "He did not call me.", "He did call me.", True, None),
    ("en_neg3", "negation", "They don't sell it.", "They do sell it.", False, None),
    ("en_inf1", "inflection", "He showed us the map.", "He show us the map.", True, ["showed"]),
    ("en_inf2", "inflection", "She asked me twice.", "She ask me twice.", True, ["asked"]),
    ("en_inf3", "inflection", "The beans are cheap.", "The bean are cheap.", True, ["beans"]),
    ("en_inf4", "inflection", "Costs rose last year.", "Cost rose last year.", False, None),
    ("en_voi1", "voicing", "He parked the van.", "He barked the van.", True, ["parked"]),
    ("en_voi2", "voicing", "The price went up.", "The prize went up.", False, None),
    ("en_len1", "length", "The ship left early.", "The sheep left early.", True, ["ship"]),
    ("en_len2", "length", "They are leaving now.", "They are living now.", False, None),
    ("en_min1", "minimal_pair", "The raw bean price rose.", "The robin price rose.", True, ["raw bean"]),
    ("en_min2", "minimal_pair", "We buy raw beans.", "We buy robbing beans.", False, ["raw beans"]),
    ("en_prn1", "proper_noun", "We met at Starbucks.", "We met at Starbacks.", True, ["Starbucks"]),
    ("en_prn2", "proper_noun", "Coffee from Colombia.", "Coffee from Columbia.", True, ["Colombia"]),
    ("en_prn3", "proper_noun", "Beans from Ethiopia.", "Beans from Ethopia.", True, ["Ethiopia"]),
    ("en_hom1", "homograph", "I will read it tomorrow.", "I will red it tomorrow.", True, None),
    ("en_hom2", "homograph", "He tried to lead the team.", "He tried to led the team.", False, None),
]
JA = [
    ("ja_voi1", "voicing", "ガスが出ました。", "カスが出ました。", True),
    ("ja_voi2", "voicing", "バスが来た。", "パスが来た。", True),
    ("ja_voi3", "voicing", "ゴミを捨てた。", "コミを捨てた。", False),
    ("ja_voi4", "voicing", "ビルが高い。", "ヒルが高い。", False),
    ("ja_voi5", "voicing", "電気をつけた。", "てんきをつけた。", True),
    ("ja_num1", "number", "三つ買った。", "四つ買った。", True),
    ("ja_num2", "number", "二人で行った。", "三人で行った。", False),
    ("ja_neg1", "negation", "彼は来なかった。", "彼は来た。", True),
    ("ja_neg2", "negation", "行きたくない。", "行きたい。", True),
    ("ja_frm1", "form", "とても楽しいです。", "とても楽しかったです。", True),
    ("ja_frm2", "form", "友達と会います。", "友達と会いました。", False),
    ("ja_len1", "length", "おじさんが来た。", "おじいさんが来た。", True),
    ("ja_len2", "length", "ビルを見た。", "ビールを見た。", False),
    ("ja_len3", "length", "ゆきが降った。", "ゆうきが降った。", True),
    ("ja_prn1", "proper_noun", "メタンが増えた。", "メタが増えた。", True),
    ("ja_prn2", "proper_noun", "スターバックスで会う。", "スターバクスで会う。", True),
    ("ja_prn3", "proper_noun", "コーヒーを飲む。", "コヒーを飲む。", False),
    ("ja_hom1", "homograph", "会議を行った。", "会議をいった。", True),
    ("ja_hom2", "homograph", "人気がない。", "にんきがない。", True),
    ("ja_hom3", "homograph", "そこへ行った。", "そこをおこなった。", False),
    ("ja_min1", "minimal_pair", "社外の人が来た。", "社会の人が来た。", True),
    ("ja_min2", "minimal_pair", "仕事を紹介した。", "仕事を照会した。", False),
]


def build_clips():
    clips = []
    voices = ["Charon", "Aoede"]
    for i, (cid, typ, canon, spoken, ctl, pl) in enumerate(EN):
        v = voices[i % 2]
        clips.append(dict(clip_id=cid + "_mis", base=cid, lang="en", type=typ, kind="misread", canonical=canon, spoken=spoken, voice=v, pl=pl))
        if ctl:
            clips.append(dict(clip_id=cid + "_ctl", base=cid, lang="en", type=typ, kind="control", canonical=canon, spoken=canon, voice=v, pl=None))
    clips.append(dict(clip_id="en_ctl_us_ctl", base="en_ctl_us", lang="en", type="format_control", kind="control",
                      canonical="US data shows costs rose.", spoken="US data shows costs rose.", voice="Aoede", pl=None))
    for cid, typ, canon, spoken, ctl in JA:
        clips.append(dict(clip_id=cid + "_mis", base=cid, lang="ja", type=typ, kind="misread", canonical=canon, spoken=spoken, voice="Aoede", pl=None))
        if ctl:
            clips.append(dict(clip_id=cid + "_ctl", base=cid, lang="ja", type=typ, kind="control", canonical=canon, spoken=canon, voice="Aoede", pl=None))
    return clips


def style_for(lang):
    import er033_tts_flash_lite_family_x_styles_01 as st
    if lang == "en":
        return st.FAMILY_X_ROLE_STYLE_EN[EN_STYLE_KEY] + "\n" + EN_SLOWER
    return st.FAMILY_X_ROLE_STYLE_JA


def wav_dur(path):
    with wave.open(path, "rb") as w:
        return w.getnframes() / w.getframerate()


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def load_res():
    if os.path.exists(RES):
        return json.load(open(RES, encoding="utf-8"))
    return {"clips": {}, "cost": {"tts_calls": 0, "tts_seconds": 0.0, "azure_seconds": 0.0, "openai_seconds": 0.0,
                                  "azure_calls": 0, "openai_calls": 0}}


def save_res(r):
    json.dump(r, open(RES, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def cost_jpy(c):
    tts = (c["tts_seconds"] * 25 / 1e6 * TTS_OUT_PER_M + c["tts_calls"] * 120 / 1e6 * TTS_IN_PER_M) * USD_JPY
    az = c["azure_seconds"] / 3600 * AZURE_PER_HOUR * USD_JPY
    oa = c["openai_seconds"] / 60 * OPENAI_ASR_PER_MIN * USD_JPY
    return {"tts_jpy": round(tts, 3), "azure_jpy": round(az, 3), "openai_asr_jpy": round(oa, 3), "total_jpy": round(tts + az + oa, 3)}


def save_cost(r, budget, mode):
    c = r["cost"]
    json.dump({"mode": mode, "approved_budget_jpy": budget, "usd_jpy": USD_JPY, "units": c, "jpy": cost_jpy(c),
               "pricing_basis": {"tts": "gemini-3.8-flash-lite-tts output $6/1M tokens @25tok/s + input $0.5/1M (pricing_snapshot.json)",
                                 "azure": "$1.00/audio hour (pricing_snapshot.json, 送信WAV尺)",
                                 "openai_asr": "gpt-4o-mini-transcribe 概算$0.003/min(公称。API応答usageを取得していないため尺換算)"}},
              open(COST, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def pcm_to_wav(pcm, path):
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(pcm)


def classify(lang, canonical, asr):
    """既存validatorをTrial隔離で呼ぶ(Production telemetry/queue非接触)。"""
    if asr is None:
        return {"cls": "NO_TRANSCRIPT", "pass": False, "entity_like": None}
    if lang == "en":
        import er006_preprod_hardening_01_validation as val
        c = val.classify_asr_match(canonical, asr, segment_id="trialB")
        diffs = [(d["canonical"], d["asr"]) for d in c.protected.content_word_diffs]
        return {"cls": c.classification, "pass": bool(c.should_pass), "diffs": diffs, "entity_like": None}
    import er007_ja_asr_validator_01 as javal
    c = javal.classify_ja_asr_match(canonical, asr, allow_reading_resolver=False)  # Resolver(LLM)は呼ばない(費用0)
    return {"cls": c.classification, "pass": bool(c.should_pass), "entity_like": bool(javal.is_entity_like_mismatch_ja(c)),
            "reason": c.reason[:160]}


def main():
    global RES, COST
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["mock", "real", "estimate"], required=True)
    ap.add_argument("--approved-budget-jpy", type=float, default=None)
    ap.add_argument("--limit", type=int, default=None, help="先頭N clipのみ(smoke用)")
    a = ap.parse_args()
    clips = build_clips()
    if a.limit:
        clips = clips[:a.limit]
    os.makedirs(AUDIO, exist_ok=True)
    if a.mode == "estimate":
        n = len(clips); sec = 3.0
        npl = sum(1 for c in clips if c["pl"])
        c = {"tts_calls": n, "tts_seconds": n * sec, "azure_seconds": (n + npl) * sec, "openai_seconds": n * sec,
             "azure_calls": n + npl, "openai_calls": n}
        print(n, "clips, PL", npl, cost_jpy(c))
        return
    if a.mode == "real":
        if a.approved_budget_jpy is None:
            sys.exit("--approved-budget-jpy 必須")
        budget = a.approved_budget_jpy
    else:
        budget = a.approved_budget_jpy or 20
    mock = a.mode == "mock"
    if mock:
        RES = os.path.join(OUT, "trial_b_results_MOCK.json")
        COST = os.path.join(OUT, "cost_actual_B_MOCK.json")
    r = load_res()
    cost = r["cost"]

    def guard():
        if cost_jpy(cost)["total_jpy"] > budget:
            save_res(r); save_cost(r, budget, a.mode)
            sys.exit(f"STOP: 予算超過 {cost_jpy(cost)['total_jpy']} > {budget}")

    # ---- 1. TTS ----
    if mock:
        for c in clips:
            p = os.path.join(AUDIO, c["clip_id"] + "_MOCK.wav")
            pcm_to_wav(b"\x00\x00" * 24000 * 3, p)
            r["clips"][c["clip_id"]] = {**c, "wav": p, "dur": 3.0, "sha256": sha(p)}
            cost["tts_calls"] += 1; cost["tts_seconds"] += 3.0
    else:
        import er033_tts_flash_lite_backend_wiring_01 as fl
        todo = [c for c in clips if "wav" not in r["clips"].get(c["clip_id"], {})]

        def do_tts(c):
            fn = fl.make_speech_metadata_call_fn(TTS_MODEL, c["voice"])
            last = None
            for attempt in range(2):
                try:
                    pcm = fn((c["spoken"], style_for(c["lang"])))
                    p = os.path.join(AUDIO, c["clip_id"] + ".wav")
                    pcm_to_wav(pcm, p)
                    return c, p, attempt + 1, None
                except Exception as e:  # noqa
                    last = str(e)[:200]
            return c, None, 2, last
        with cf.ThreadPoolExecutor(4) as ex:
            for c, p, n_calls, err in ex.map(do_tts, todo):
                if p:
                    d = wav_dur(p)
                    r["clips"][c["clip_id"]] = {**c, "wav": p, "dur": d, "sha256": sha(p)}
                    cost["tts_calls"] += n_calls; cost["tts_seconds"] += d * n_calls
                else:
                    r["clips"][c["clip_id"]] = {**c, "tts_error": err}
                    cost["tts_calls"] += n_calls
                print("TTS", c["clip_id"], p and round(wav_dur(p), 2), err, flush=True)
                guard()
    save_res(r); save_cost(r, budget, a.mode)
    ok = [r["clips"][c["clip_id"]] for c in clips if "wav" in r["clips"].get(c["clip_id"], {})]
    total_dur = sum(x["dur"] for x in ok)
    pl_dur = sum(x["dur"] for x in ok if x.get("pl"))
    proj = dict(cost)
    proj["azure_seconds"] += total_dur + pl_dur
    proj["openai_seconds"] += total_dur
    projected = cost_jpy(proj)["total_jpy"]
    skip_pl = False
    print(f"TTS完了。残りASR込み予測総額 {projected}円 (予算{budget})", flush=True)
    if projected > budget and pl_dur > 0:
        proj["azure_seconds"] -= pl_dur
        projected = cost_jpy(proj)["total_jpy"]
        skip_pl = projected <= budget
        print(f"Phrase List群を省略した場合の予測 {projected}円 skip_pl={skip_pl}", flush=True)
    if projected > budget:
        sys.exit(f"STOP: 予測総額{projected} > 予算{budget}(TTS音声は保存済み。ASR未実行)")

    # ---- 2. Primary / Azure / local ----
    import er005_cost_logger as cl
    cl.init_logger(os.path.join(OUT, "azure_cl_log_B_local.jsonl"))  # Trial隔離: Production telemetryではなくtrial_abc配下へ
    import er006_asr_provider_routing_01 as routing
    import er006_secondary_asr_01 as sec
    import er007_ja_secondary_asr_01 as jasec
    import er008_disfluency_qa_18 as dq

    def tx_primary(x):
        if mock:
            return x["spoken"], None
        return routing._transcribe_openai_mini(x["wav"], "en-US" if x["lang"] == "en" else "ja-JP", "gpt-4o-mini-transcribe")

    def tx_azure(x, pl=False):
        if mock:
            return (x["canonical"] if pl else x["spoken"]), None
        if x["lang"] == "en":
            return sec.get_full_text_via_azure_stt_with_phrase_list(x["wav"], "en-US", phrases=(x["pl"] if pl else None))
        return jasec._azure_stt_strict(x["wav"], "ja-JP")

    def tx_local(x):
        if mock:
            return x["spoken"], None
        m = dq._get_model("medium")
        segs, _ = m.transcribe(x["wav"], language=x["lang"], condition_on_previous_text=False, vad_filter=False)
        t = " ".join(s.text.strip() for s in segs).strip()
        return re.sub(r"\s+([.%,?!])", lambda mm: mm.group(1), t), None

    def run_one(x, key, fn):
        if key in x.get("asr", {}):
            return x, key, None
        return x, key, fn(x)

    for key, fn, wrk, unit in [("primary", tx_primary, 4, "openai"), ("azure", tx_azure, 4, "azure"),
                               ("local_medium", tx_local, 1, None), ("azure_pl", lambda x: tx_azure(x, True), 4, "azure")]:
        if key == "azure_pl" and skip_pl:
            continue
        pool = [x for x in ok if (key != "azure_pl" or x.get("pl"))]
        with cf.ThreadPoolExecutor(wrk) as ex:
            for x, k, res in ex.map(lambda z: run_one(z, key, fn), pool):
                if res is None:
                    continue
                t, err = res
                x.setdefault("asr", {})[k] = {"text": t, "error": err}
                if unit == "openai":
                    cost["openai_seconds"] += x["dur"]; cost["openai_calls"] += 1
                if unit == "azure":
                    cost["azure_seconds"] += x["dur"]; cost["azure_calls"] += 1
                print(key, x["clip_id"], repr(t), err, flush=True)
                guard()
        save_res(r); save_cost(r, budget, a.mode)

    # ---- 3. 判定(既存validator) ----
    for x in ok:
        x["judge"] = {k: classify(x["lang"], x["canonical"], v["text"]) for k, v in x.get("asr", {}).items()}
    save_res(r); save_cost(r, budget, a.mode)
    print("DONE", cost_jpy(cost), flush=True)


if __name__ == "__main__":
    main()
