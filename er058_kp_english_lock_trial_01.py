# -*- coding: utf-8 -*-
"""ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01 委任_04D Trial D(Trial専用・Production非経由)。
Key Phrase英語: 現行Production Prompt / K2 / K2+対策+English Lock(簡潔版・完全版) を各1回生成し評価。
Master Store/manifest/telemetry/queue/attempt_history/cost_loggerへは書かない。
modes: prompts / estimate / gen / eval"""
import os, sys, json, time, re, hashlib, concurrent.futures as cf
sys.path.insert(0, os.getcwd())
os.environ["TTS_EXECUTION_MODE"] = "STANDARD"
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = f"{ROOT}/er058_output/kp_english_lock_trial_01"
RAW = f"{OUT}/raw"
import er057_tone_trial_kp_ja_gen_01 as G
G.RAW = RAW
MODEL, VOICE = G.MODEL, G.VOICE_EN
WORDS = ["new normal", "default", "cashless", "work-life balance", "raw bean", "push prices up", "a catch", "price tag"]
WHY = {"new normal": "過去に日本語/中国語の翻訳的書起こし(新常態)", "default": "同(デフォルト)", "cashless": "ASR false rejection残存例",
       "work-life balance": "過去Trial語(長め・ハイフン)", "raw bean": "Coffee最終試聴で異音が出た語", "push prices up": "Coffee Standard KP(語尾上がり検討語)",
       "a catch": "冠詞aが強く長くなった語(Trial26)", "price tag": "Coffee Advanced KP(語末子音)"}


def prompts():
    import er003_v1_repro01_main_generate as r
    K2 = ("Say the phrase as one single, smoothly connected chunk of meaning, as if the words belong together and are not read one by one. "
          "Keep the pitch movement small and continuous across the whole phrase. Say only this phrase, exactly once, without adding, omitting, or changing any words, "
          "and make sure the final sound is actually spoken.")
    CONCISE = ("Say the phrase as one single, smoothly connected chunk of meaning, as if the words belong together and are not read one by one. "
               "Keep the pitch movement small and continuous across the whole phrase, with no single sound over-emphasized. "
               "Keep small function words such as \"a\", \"an\", \"the\" light and unstressed, flowing into the next word but still audible. "
               "Pronounce it as English throughout, not as a Japanese or Chinese reading. "
               "Say only this phrase, exactly once, without adding, omitting, or changing any words, and make sure the final sound is actually spoken, not trailed off.")
    FULL = K2 + "\n\n" + r.FUNCTION_WORD_REDUCTION_SUFFIX + r.KEY_PHRASE_ENGLISH_LANGUAGE_LOCK_SUFFIX
    return {"V1": ("現行Production(Minimal)", r.KEY_PHRASE_MINIMAL_INSTRUCTION_PREFIX), "V2": ("K2単体", K2),
            "V3": ("K2+対策+English Lock 簡潔版", CONCISE),
            "V4": ("K2+対策+English Lock 完全版(K2+現行function-word文+現行English Lock文を逐語連結)", FULL)}


def jobs():
    import er003_v1_n3_01_tts_generate as n3
    P = prompts()
    return [{"id": f"{v}_{i}", "v": v, "word": w, "text": n3.tts_safe_kp_en(w), "style": P[v][1], "voice": VOICE,
             "margin": G.KP_EN_MARGIN, "lang": "en", "spec": v, "grp": "B"} for i, w in enumerate(WORDS, 1) for v in P]


def write_prompts():
    P = prompts()
    md = "# Trial D Prompt一覧(逐語)\n\n送信: speech_metadata.style=下記、Part.text=Key Phrase原稿、model=gemini-3.8-flash-lite-tts、Aoede、Standard同期(DEV)。\n\n"
    for v, (n, s) in P.items():
        md += f"## {v} {n}(文字数 {len(s)}、語数 {len(s.split())})\n\n```\n{s}\n```\n\n"
    open(f"{OUT}/prompts_D.md", "w", encoding="utf-8").write(md)
    return {v: (len(s), len(s.split())) for v, (n, s) in P.items()}


def estimate():
    J = jobs()
    tot_s = 0
    tot_in = 0
    for j in J:
        tot_s += 1.6 + 0.6
        tot_in += len(j["text"]) / 2 + len(j["style"]) / 4 + 20
    usd = tot_s * 25 * G.PRICE_OUT_PER_M / 1e6 + tot_in * G.PRICE_IN_PER_M / 1e6
    asr_jpy = len(J) * (2.0 / 60) * 0.003 * G.USD_JPY
    tts_jpy = usd * G.USD_JPY * 1.2
    md = (f"# COST_ESTIMATE_D_01 (2026-10-12)\n\n- TTS call数: {len(J)}(8語x4版、各1回、技術失敗時のみ1回retry見込み+20%)。model=gemini-3.8-flash-lite-tts(Production同一)。\n"
          f"- 想定出力音声 約{tot_s:.0f}秒(25token/秒)、入力token約{tot_in:.0f}。単価 出力$6/M・入力$0.5/M、USD_JPY=160(前Trialと同一式)。\n"
          f"- TTS概算: 約JPY{tts_jpy:.1f}(retry込み)。\n- Primary ASR(OpenAI gpt-4o-mini-transcribe、約2秒x{len(J)}、$0.003/分想定): 約JPY{asr_jpy:.2f}。Azure/Secondaryは呼ばない。ローカルwhisperは0円。\n"
          f"- 合計見込み: 約JPY{tts_jpy+asr_jpy:.1f}。上限JPY10。{'実行可' if tts_jpy+asr_jpy<=10 else 'STOP'}。\n")
    open(f"{OUT}/COST_ESTIMATE_D_01.md", "w", encoding="utf-8").write(md)
    print(md)
    return tts_jpy + asr_jpy


def gen():
    J = jobs()
    rp = f"{OUT}/results_gen.jsonl"
    done = {}
    if os.path.exists(rp):
        for l in open(rp, encoding="utf-8"):
            r = json.loads(l)
            done[r["id"]] = r
    todo = [j for j in J if done.get(j["id"], {}).get("status") != "OK"]
    print("todo", len(todo), flush=True)
    res = dict(done)
    with cf.ThreadPoolExecutor(4) as ex:
        for r in ex.map(G.gen_one, todo):
            res[r["id"]] = r
            print(r["id"], r["status"], r.get("duration_s"), r.get("reason", ""), flush=True)
    with open(rp, "w", encoding="utf-8") as f:
        for j in J:
            f.write(json.dumps(res[j["id"]], ensure_ascii=False) + "\n")
    pt = ct = calls = 0
    for r in res.values():
        calls += r.get("call_count", 0)
        for u in r.get("usage", []) or []:
            if u:
                pt += u.get("prompt_tokens") or 0
                ct += u.get("candidates_tokens") or 0
    usd = ct * G.PRICE_OUT_PER_M / 1e6 + pt * G.PRICE_IN_PER_M / 1e6
    cost = {"calls_total": calls, "jobs": len(J), "ok": sum(r["status"] == "OK" for r in res.values()), "prompt_tokens": pt, "candidates_tokens": ct,
            "est_usd": round(usd, 5), "est_jpy": round(usd * G.USD_JPY, 2), "model": MODEL,
            "basis": "usage_metadata実測tokens x Standard単価、USD_JPY=160。請求画面は未確認。ASR費用は別(eval)"}
    json.dump(cost, open(f"{OUT}/cost_actual_D_tts.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(cost)


NONLATIN = re.compile(r"[぀-ヿ㐀-鿿가-힯Ѐ-ӿ]")


def evaluate():
    import er006_asr_provider_routing_01 as routing
    import er006_preprod_hardening_01_validation as av
    import er003_v1_repro01_main_generate as r
    import er008_disfluency_qa_18 as dq
    rows = []
    for l in open(f"{OUT}/results_gen.jsonl", encoding="utf-8"):
        g = json.loads(l)
        if g["status"] != "OK":
            rows.append({**g, "eval": "GEN_FAILED"})
            continue
        wav = f"{RAW}/{g['id']}.wav"
        asr, err = routing.transcribe(wav, language="en-US", prompt=r.KEY_PHRASE_EN_ASR_NO_TRANSLATE_PROMPT)
        cls = av.classify_asr_match(g["text"], asr) if asr is not None else None
        nl = bool(asr and NONLATIN.search(asr))
        dis = dq.check_segment_for_disfluency(wav, "en", "small")
        wh = dis["transcript"]
        exp_words = len(g["text"].replace("-", " ").split())
        rep = {"adjacent_repeat": dis["flagged"], "whisper_word_count": dis["word_count"], "expected_words": exp_words,
               "extra_words": dis["word_count"] > exp_words + 1}
        anomaly = g.get("duration_anomaly", {}).get("is_anomaly")
        length_ok = asr is not None and len(asr) <= len(g["text"]) + 10
        rows.append({"id": g["id"], "v": g["id"].split("_")[0], "word": g["text"], "dur": g["duration_s"], "raw_dur": g["raw_duration_s"], "asr": asr, "asr_err": err,
                     "primary_pass": bool(cls and cls.should_pass and length_ok), "classification": getattr(cls, "classification", None),
                     "should_pass": getattr(cls, "should_pass", None), "length_ok": length_ok, "non_latin": nl, "whisper_small": wh, "rep": rep,
                     "duration_anomaly": anomaly, "sha256": g["sha256"]})
        print(rows[-1]["id"], rows[-1]["primary_pass"], rows[-1]["classification"], repr(asr), "|", wh, rep["adjacent_repeat"], flush=True)
    json.dump(rows, open(f"{OUT}/eval_D.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    m = sys.argv[1]
    if m == "prompts":
        print(write_prompts())
    elif m == "estimate":
        write_prompts()
        estimate()
    elif m == "gen":
        gen()
    elif m == "eval":
        evaluate()
