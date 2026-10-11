# -*- coding: utf-8 -*-
"""FAMILY-X-COFFEE-FINAL-LISTENING-TONE-TRIAL-01 委任_01B Trial専用script(Production非経由)。
対象: B=Key Phrase英語Phrase(Aoede) / C=Key Phrase日本語意味(Aoede) / D=Standard日本語Preview・Comment1-4(Aoede)。
modes: specs(prompts書出し) / estimate(費用概算) / gen(生成)。後処理・ページは er057_tone_trial_kp_ja_build_01.py。
Master Store/manifest/telemetry/human_review_queue/attempt_history/cost_loggerへは一切書かない
(Production runnerを使わず、flw.make_speech_metadata_call_fn と同一リクエスト形を直接API呼び出し)。
model=gemini-3.8-flash-lite-tts、speech_metadata.style方式、Standard同期(DEV)。"""
import os, sys, json, time, hashlib, concurrent.futures as cf
sys.path.insert(0, os.getcwd())
os.environ["TTS_EXECUTION_MODE"] = "STANDARD"
import numpy as np
import soundfile as sf

ROOT = os.path.dirname(os.path.abspath(__file__))
TONE = r"C:\Users\tensh\eigo-radio-tone\er019_output\family_x_audio_production_wiring_01\coffee_prices__run_e_tone_01\a2"
OUT = f"{ROOT}/er057_output/coffee_final_listening_tone_trial_01/part_BCD"
PAGE = f"{ROOT}/user_test/coffee_tone_trial_01/keyphrases_jacomments"
RAW, MP3, PROMPTS = f"{OUT}/raw", f"{OUT}/mp3", f"{OUT}/prompts"
VOICE_EN = "Aoede"   # 現行Production KP英語Voice(er006 shared_narration.ensure_key_phrase_english_component: speaker_voice="Aoede")
VOICE_JA = "Aoede"   # 現行JA Voice(tts_generation_results実測: Aoede)
MODEL = "gemini-3.8-flash-lite-tts"
BACKEND = "speech_metadata_flash_lite"
KP_EN_MARGIN = 0.30   # er003_v1_repro01 KEY_PHRASE_TRIM_SAFETY_MARGIN_SECONDS
JA_MARGIN = 0.35      # p3u.NARRATION_BODY_TRIM_SAFETY_MARGIN_SECONDS
USD_JPY = 160.0
PRICE_OUT_PER_M, PRICE_IN_PER_M = 6.0, 0.5   # Standard単価(前Trial同一式。audio出力25tok/s)

# --- Baseline(現行Production Style、逐語) -------------------------------------
JA_J2 = ("明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽やかなリズムをつけてください。"
         "ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。")

# --- B: 英語Phrase専用 5仕様(style全文。共通guard=1回のみ・語の追加省略禁止・末尾音まで発話) ----
B_GUARD = " Say only this phrase, exactly once, without adding, omitting, or changing any words, and make sure the final sound is actually spoken."
B_SPECS = {
    "K1": ("短い語句の自然なアクセント",
           "Read this as a short vocabulary phrase in natural spoken English. Put the natural stress on the main content word and keep small function words light and unstressed, "
           "so the phrase has the same accent pattern it would have inside a real sentence." + B_GUARD),
    "K2": ("意味のまとまり(1つのかたまり)",
           "Say the phrase as one single, smoothly connected chunk of meaning, as if the words belong together and are not read one by one. Keep the pitch movement small and continuous across the whole phrase." + B_GUARD),
    "K3": ("文末の安定(語尾を上げない)",
           "Calm and steady. Let the phrase end with a settled, naturally falling pitch, as a finished statement. Do not raise the pitch at the end, and do not sound like a question or an unfinished list item." + B_GUARD),
    "K4": ("過剰強調の抑制(淡々と自然に)",
           "Plain, understated and natural, like a teacher quietly reading one vocabulary item to a learner. No special emphasis on any word, no dramatic intonation, no exaggerated energy." + B_GUARD),
    "K5": ("学習者向けの明瞭なモデル発音",
           "A clear model pronunciation for English learners: each sound distinctly articulated, natural native rhythm, an even and gentle tone, and a crisp, clean finish on the last sound." + B_GUARD),
}
# --- C: 日本語意味(短い語句) 5仕様。Bの各仕様と対応付け(Promptは独立) --------------------
C_SPECS = {
    "M1": ("語尾を上げず自然に言い切る(K1対応)",
           "短い言葉の意味を伝える自然な話し言葉で。語尾を上げず、自然に音程を下げて言い切ってください。明るさは保ちつつ、演技がかった話し方は避けてください。"),
    "M2": ("ひとまとまりの意味として滑らかに(K2対応)",
           "一つの意味のまとまりとして、途切れさせずに滑らかに、ひと息で読んでください。単語ごとに区切らず、抑揚の上下も小さく自然にしてください。"),
    "M3": ("落ち着いて穏やかに終える(K3対応)",
           "落ち着いた穏やかな声で、文のように大げさに読まず、短い言葉として静かに言い終えてください。終わりで声が持ち上がらないようにしてください。"),
    "M4": ("淡々とした辞書の意味説明(K4対応)",
           "辞書の意味の説明を読むように、淡々と自然に。特定の語を強調せず、抑揚も控えめにしてください。ただし暗くならず、聞き取りやすい声で。"),
    "M5": ("学習者向けの明瞭さ(K5対応)",
           "日本語学習者や英語学習者にも聞き取りやすいよう、一語一語の発音をはっきり、標準的な速さで読んでください。語尾は自然に収め、上げすぎないでください。"),
}
# --- D: Standard日本語Preview/Comment 5仕様(現行J2を逐語で土台にし、句読点付近の音程の不自然な上下を方向別に是正) ----
D_ADD = {
    "P1": ("文末・句末の音程を安定させる",
           "読点や句点の前後で声の高さを急に上げ下げせず、文の終わりは自然に音程を下げて落ち着かせてください。"),
    "P2": ("句読点を「間」として扱う",
           "句読点の記号そのものに反応して声の高さを変えないでください。読点は短い息継ぎの間、句点はやや長めの間として、音程は変えずに自然に置いてください。"),
    "P3": ("意味のまとまり(文節)ごとのリズム",
           "読点ではなく意味のまとまりごとに、ひとつながりの滑らかなイントネーションで読んでください。まとまりの中では声の高さを保ち、まとまりの終わりで自然に収めてください。"),
    "P4": ("会話的な自然さ",
           "ラジオのパーソナリティが目の前の一人に話しかけるような、自然な話し言葉で。原稿を読み上げる感じを避け、記号で区切らず息の流れに沿って話してください。"),
    "P5": ("文全体のなだらかな音程設計",
           "声の高さは文全体でなだらかに流れるようにし、細かな上下は抑えてください。文の途中で急に高くなったり低くなったりせず、明るさと温かみは保ってください。"),
}
D_SPECS = {k: (v[0], JA_J2 + v[1]) for k, v in D_ADD.items()}
SEG_NAMES = ("preview", "comment_1", "comment_2", "comment_3", "comment_4")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def load_texts():
    import er003_v1_n3_01_tts_generate as n3
    import er003_audio_tts_asr_safety as safety
    k = json.load(open(f"{TONE}/key_phrases/keywords_canonicalized.json", encoding="utf-8"))["items"]
    k = sorted(k, key=lambda it: it["rank"])
    kp = []
    for i, it in enumerate(k, start=1):
        gloss, _ = n3.resolve_key_phrase_ja_gloss_tts(it)
        kp.append({"idx": i, "rank": it["rank"], "en": n3.tts_safe_kp_en(it["used_form"]), "used_form": it["used_form"],
                   "ja": safety.to_tts_safe_japanese_fraction_reading(n3.tts_safe_ja(gloss)), "ja_gloss_tts": gloss})
    st = json.load(open(f"{TONE}/a2_support_texts.json", encoding="utf-8"))
    segs = {}
    for name in SEG_NAMES:
        segs[name] = {"manuscript": st[name],
                      "tts": safety.to_tts_safe_japanese_fraction_reading(n3.tts_safe_ja(st[name]))}
    return kp, segs


def jobs():
    import er003_v1_repro01_main_generate as repro01
    kp, segs = load_texts()
    J = []
    for sid, (_, style) in B_SPECS.items():
        for it in kp:
            J.append({"id": f"{sid}_kp{it['idx']}", "spec": sid, "grp": "B", "text": it["en"], "style": style, "voice": VOICE_EN,
                      "margin": KP_EN_MARGIN, "lang": "en"})
    for sid, (_, style) in C_SPECS.items():
        for it in kp:
            J.append({"id": f"{sid}_kp{it['idx']}", "spec": sid, "grp": "C", "text": it["ja"], "style": style, "voice": VOICE_JA,
                      "margin": JA_MARGIN, "lang": "ja"})
    for sid, (_, style) in D_SPECS.items():
        for name, s in segs.items():
            J.append({"id": f"{sid}_{name}", "spec": sid, "grp": "D", "text": s["tts"], "style": style, "voice": VOICE_JA,
                      "margin": JA_MARGIN, "lang": "ja"})
    return J, kp, segs, repro01.KEY_PHRASE_MINIMAL_INSTRUCTION_PREFIX


def write_prompts():
    J, kp, segs, kp_base = jobs()
    hdr = ("送信方式: `generate_content`、`Part(text=<原稿逐語>, speech_metadata=SpeechMetadata(style=<下記style>))`、"
           f"model=`{MODEL}`、voice=`Aoede`、language_code=ja-JP(Production同一)、Standard同期(DEV)。\n\n")
    b = "# Prompt一覧 B: Key Phrase英語Phrase(Standard/Advanced共通・Aoede)\n\n" + hdr
    b += "原稿(逐語、tts_safe_kp_en後): " + " / ".join(f"`{it['en']}`" for it in kp) + "\n\n"
    b += "## Baseline(現行Production Style = KEY_PHRASE_MINIMAL_INSTRUCTION_PREFIX、逐語)\n\n```\n" + kp_base + "\n```\n\n"
    for sid, (ap, st) in B_SPECS.items():
        b += f"## {sid} {ap}\n\nstyle(逐語):\n\n```\n{st}\n```\n\n"
    c = "# Prompt一覧 C: Key Phrase日本語意味(Standard・Aoede)\n\n" + hdr
    c += "原稿(逐語、tts_safe後): " + " / ".join(f"`{it['ja']}`" for it in kp) + "\n\n"
    c += f"## Baseline(現行Production Style = JA_J2_BRIGHT、逐語)\n\n```\n{JA_J2}\n```\n\n"
    for sid, (ap, st) in C_SPECS.items():
        c += f"## {sid} {ap}\n\nstyle(逐語):\n\n```\n{st}\n```\n\n"
    d = "# Prompt一覧 D: Standard日本語 Preview/Comment1-4(Aoede)\n\n" + hdr
    d += "原稿は既存run dirの`a2_support_texts.json`から逐語(preview, comment_1〜4)。各仕様=現行J2逐語(土台)+追記。\n\n"
    d += f"## Baseline(現行Production Style = JA_J2_BRIGHT、逐語)\n\n```\n{JA_J2}\n```\n\n"
    for sid, (ap, st) in D_SPECS.items():
        d += f"## {sid} {ap}\n\n追記部分: `{D_ADD[sid][1]}`\n\nstyle(逐語、J2+追記):\n\n```\n{st}\n```\n\n"
    for n, t in (("prompts_B.md", b), ("prompts_C.md", c), ("prompts_D.md", d)):
        open(f"{PROMPTS}/{n}", "w", encoding="utf-8").write(t)
    print("prompts written; jobs=", len(J))


def estimate():
    J, kp, segs, _ = jobs()
    base = {}
    for i in range(1, 6):
        base[f"kp{i}_en"] = sf.info(f"{TONE}/narration/kp{i}_en.wav").duration
        base[f"meaning_{i}"] = sf.info(f"{TONE}/narration/meaning_{i}.wav").duration
    for n in SEG_NAMES:
        base[n] = sf.info(f"{TONE}/narration/{n}.wav").duration
    tot_s, tot_in = 0.0, 0.0
    for j in J:
        if j["grp"] == "B": d = base[f"kp{j['id'].split('kp')[1]}_en"]
        elif j["grp"] == "C": d = base[f"meaning_{j['id'].split('kp')[1]}"]
        else: d = base[j["id"].split("_", 1)[1]]
        tot_s += d + 0.6   # trim後の既存尺+前後margin分の余裕
        tot_in += (len(j["text"]) + len(j["style"])) / 2.0 + 20  # 保守的(1token=2文字)
    usd = tot_s * 25 * PRICE_OUT_PER_M / 1e6 + tot_in * PRICE_IN_PER_M / 1e6
    usd_ret = usd * 1.2
    md = (f"# COST_ESTIMATE_01B (2026-10-11)\n\n- call数: {len(J)} (B 25 + C 25 + D 25)。各1回、技術失敗時のみ1回retry。ASRなし(無料)。\n"
          f"- 想定出力音声: 合計 約{tot_s:.0f}秒(既存音声尺+margin。25 token/秒)。入力token合計 約{tot_in:.0f}(保守的)。\n"
          f"- 単価(前Trial TTS_VOICE_TONE_BRIGHTNESS_TRIALと同一式): 出力${PRICE_OUT_PER_M}/M tokens、入力${PRICE_IN_PER_M}/M tokens、USD_JPY={USD_JPY}。\n"
          f"- 概算: ${usd:.4f} = 約¥{usd*USD_JPY:.1f}(技術失敗retry+20%見込み 約¥{usd_ret*USD_JPY:.1f})。\n"
          f"- 上限判定: 上限¥50。概算が¥50以下なら実行可、超過ならSTOP。\n")
    open(f"{OUT}/COST_ESTIMATE_01B.md", "w", encoding="utf-8").write(md)
    print(md)


_client = None
def call_tts(text, style, voice):
    """flw.make_speech_metadata_call_fn と同一リクエスト形(Standard同期)。usageを捕捉するため同形をここで直接呼ぶ。"""
    global _client
    import er033_tts_flash_lite_backend_wiring_01 as flw
    import er006_model_routing_contract_01 as rc
    import er002_gemini_client as gclient
    import er002_common as common
    from google.genai import types
    flw.assert_sdk_supports_speech_metadata()
    model = rc.require_model(flw.FAMILY_X_FLASH_LITE_TTS_PROCESS, MODEL)
    if _client is None:
        _client = gclient.make_client()
    content = types.Content(parts=[types.Part(text=text, speech_metadata=types.SpeechMetadata(style=style))], role="user")
    resp = _client.models.generate_content(
        model=model, contents=content,
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(language_code=common.LANGUAGE_CODE, voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice))),
            http_options=types.HttpOptions(timeout=gclient.TTS_TIMEOUT_MS)))
    parts = resp.candidates[0].content.parts
    raw = b"".join(p.inline_data.data for p in parts if p.inline_data and p.inline_data.data)
    if not raw:
        raise RuntimeError("empty audio")
    samples, fr = flw._decode_audio_defensive(raw)
    samples = flw._resample_to_common_rate(samples, fr)
    u = getattr(resp, "usage_metadata", None)
    usage = {"prompt_tokens": getattr(u, "prompt_token_count", None), "candidates_tokens": getattr(u, "candidates_token_count", None),
             "total_tokens": getattr(u, "total_token_count", None)} if u else None
    return samples, usage


def gen_one(j):
    import er002_common as common
    import er003_b1_p3u_audio as p3u
    import er003_audio_tts_asr_safety as safety
    out = f"{RAW}/{j['id']}.wav"
    calls, usages, err = 0, [], None
    for attempt in (1, 2):   # 技術失敗時のみ1回retry
        calls += 1
        t0 = time.time()
        try:
            samples, usage = call_tts(j["text"], j["style"], j["voice"])
            usages.append(usage)
            trimmed, ti = p3u.trim_english_keyword_silence(samples, common.SAMPLE_RATE, safety_margin_seconds=j["margin"])
            if trimmed is None:
                err = "no speech detected"
                continue
            anomaly = safety.detect_duration_anomaly(ti["raw_duration_seconds"], j["text"], j["lang"])
            common.write_wav_float(out, trimmed, common.SAMPLE_RATE, 1)
            return {"id": j["id"], "spec": j["spec"], "grp": j["grp"], "status": "OK", "text": j["text"], "style": j["style"],
                    "voice": j["voice"], "model": MODEL, "tts_backend": BACKEND, "call_count": calls, "retry_count": calls - 1,
                    "duration_s": round(len(trimmed) / common.SAMPLE_RATE, 3), "raw_duration_s": ti["raw_duration_seconds"],
                    "duration_anomaly": anomaly, "usage": usages, "sha256": sha(out), "elapsed_s": round(time.time() - t0, 1)}
        except Exception as e:
            err = f"{type(e).__name__}: {e}"
    return {"id": j["id"], "spec": j["spec"], "grp": j["grp"], "status": "FAILED", "reason": err, "call_count": calls, "usage": usages}


def gen():
    J, *_ = jobs()
    rp = f"{OUT}/results_01B.jsonl"
    done = {}
    if os.path.exists(rp):
        for l in open(rp, encoding="utf-8"):
            r = json.loads(l)
            done[r["id"]] = r
    todo = [j for j in J if done.get(j["id"], {}).get("status") != "OK"]
    print("todo", len(todo), flush=True)
    res = dict(done)
    with cf.ThreadPoolExecutor(6) as ex:
        for r in ex.map(gen_one, todo):
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
    usd = ct * PRICE_OUT_PER_M / 1e6 + pt * PRICE_IN_PER_M / 1e6
    cost = {"calls_total": calls, "jobs": len(J), "ok": sum(r["status"] == "OK" for r in res.values()),
            "prompt_tokens": pt, "candidates_tokens": ct, "est_usd": round(usd, 5), "est_jpy": round(usd * USD_JPY, 2),
            "basis": "usage_metadata実測tokens×Standard単価(出力$6/M、入力$0.5/M)、USD_JPY=160。請求画面は未確認"}
    json.dump(cost, open(f"{OUT}/cost_actual_01B.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(cost)


if __name__ == "__main__":
    {"specs": write_prompts, "estimate": estimate, "gen": gen}[sys.argv[1]]()
