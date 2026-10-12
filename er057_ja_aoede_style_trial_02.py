# -*- coding: utf-8 -*-
"""FAMILY-X-COFFEE-STANDARD-JA-AOEDE-STYLE-TRIAL-02 委任_01 Trial専用script(Production非経由)。
基準P2(Preview/Comment)・M2(KP日本語意味)を中心にR1〜R8 / Q1〜Q8を生成。
01Bのscript(er057_tone_trial_kp_ja_gen_01)の call_tts/gen_one/load_texts を再利用(同一リクエスト形・trim・anomaly)。
Master Store/manifest/telemetry/queue/attempt_history/cost_loggerへは書かない。
modes: specs / estimate / gen / asr"""
import os, sys, json, hashlib, time, concurrent.futures as cf
sys.path.insert(0, os.getcwd())
from dotenv import load_dotenv
load_dotenv()
import soundfile as sf
import er057_tone_trial_kp_ja_gen_01 as g

ROOT = g.ROOT
OUT = f"{ROOT}/er057_output/ja_aoede_style_trial_02"
RAW, PROMPTS = f"{OUT}/raw", f"{OUT}/prompts"
PREV = f"{ROOT}/er057_output/coffee_final_listening_tone_trial_01/part_BCD"   # 基準P2/M2の既存Trial音声
J2 = g.JA_J2
P2 = g.D_SPECS["P2"][1]
M2 = g.C_SPECS["M2"][1]
PUNCT = "句読点の記号そのものに反応して声の高さを変えないでください。読点は短い息継ぎの間、句点はやや長めの間として、音程は変えずに自然に置いてください。"

# --- R: Preview/Comment用(P2中心。置換・整理を含む。いずれも「速度数値のみ」の差ではない) ---
R = {
 "R1": ("P2の整理・簡潔化(J2の重複表現を整理し、句読点の指示は維持)",
        "J2の「聞き手に楽しく語りかける〜/ニュース番組としての明瞭さ」を1文に整理して短くし、P2の句読点指示だけを残した。冗長な指示が演技や抑揚の付けすぎを誘っていないかを見る。",
        "明るく温かみのある親しみやすい話し方で、自然な抑揚と軽やかなリズムで。演技がかった話し方は避けてください。句読点の記号では声の高さを変えず、読点は短い息継ぎ、句点はやや長めの間として置いてください。"),
 "R2": ("親しみ(身近な相手に話題を教える語りかけ)",
        "J2の「聞き手に楽しく語りかける」を「身近な人に話題を教える」に置換し、親しみやすさを出す。P2の句読点指示は維持。",
        "明るく、温かみのある話し方で。身近な人にちょっとした話題を教えてあげるように、自然な抑揚と軽やかなリズムをつけてください。ニュース番組としての明瞭さは保ち、演技がかった話し方は避けてください。" + PUNCT),
 "R3": ("適度な明るさ(微笑みを含んだやわらかい声)",
        "「楽しく」を「口元にほんのり笑みを浮かべたようなやわらかい明るさ」に置換。はしゃがない範囲の明るさを狙う。P2の句読点指示は維持。",
        "口元にほんのり笑みを浮かべたような、やわらかく明るい声で、温かみのある親しみやすい話し方をしてください。はしゃいだり演技がかったりせず、自然な抑揚と軽やかなリズムで、ニュース番組としての明瞭さも保ってください。" + PUNCT),
 "R4": ("控えめな表情(内容に合わせた共感・驚きをほんの少し)",
        "「軽やかなリズム」の代わりに、内容に応じた共感や驚きを声の表情へほんの少しだけ乗せる指示を入れ、抑揚の付けすぎは明示的に禁止。P2の句読点指示は維持。",
        "明るく、温かみのある親しみやすい話し方で。内容に合わせて、共感や驚きの気持ちをほんの少しだけ声の表情にのせてください。ただし抑揚をつけすぎず、演技がかった話し方やアナウンサーのような話し方は避けてください。" + PUNCT),
 "R5": ("聞き取りやすさ(語頭・語尾をくっきり、硬くしない)",
        "J2の「ニュース番組としての明瞭さ」を「語頭と語尾までくっきり」に置換し、硬いアナウンサー調に寄らない聞き取りやすさを狙う。P2の句読点指示は維持。",
        "明るく、温かみのある親しみやすい話し方で、自然な抑揚と軽やかなリズムをつけてください。語の頭と終わりまで一つ一つはっきり聞き取れるように発音しつつ、硬いアナウンサー調や演技がかった話し方は避けてください。" + PUNCT),
 "R6": ("意味のまとまりの息(句読点の間に加え、意味の切れ目でも自然に息継ぎ)",
        "P2の「記号を間として扱う」に、意味のまとまりごとの息の流れを追加。記号がなくても息が自然に流れる読みを狙う(句読点指示は維持)。",
        "明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽やかなリズムをつけ、演技がかった話し方は避けてください。句読点の記号そのものに反応して声の高さを変えないでください。読点は短い息継ぎの間、句点はやや長めの間として、音程は変えずに置き、意味のまとまりごとに息が自然に流れるように読んでください。"),
 "R7": ("やわらかな文末(語尾を伸ばさず軽く下げて収める)",
        "P2の句読点指示に、語尾を伸ばさず上げず、やわらかく収める指示を組み合わせる。語尾上がり・語尾の不自然な持ち上がりの抑制を狙う。",
        "明るく、温かみのある親しみやすい話し方で、自然な抑揚と軽やかなリズムをつけてください。演技がかった話し方は避け、文の終わりは語尾を伸ばさず上げず、やわらかく収めてください。句読点の記号そのものに反応して声の高さを変えないでください。読点は短い息継ぎの間、句点はやや長めの間として置いてください。"),
 "R8": ("落ち着いた温かさ(明るさを抑え、穏やかな大人の話し相手)",
        "J2の「明るく・楽しく」を抑え、穏やかで温かい落ち着いた話し手に置換。明るさが過剰に感じられる場合の対極案。P2の句読点指示は維持。",
        "落ち着いた温かみのある声で、信頼できる大人がゆったり語りかけるように話してください。抑揚は自然で控えめにし、演技がかった話し方やアナウンサーのような話し方は避けてください。" + PUNCT),
}
# --- Q: KP日本語意味用(M2中心、Rと方向を対応付け。Promptは独立) ---
Q = {
 "Q1": ("R1対応: M2の整理・簡潔化", "M2を最小の2要素(ひと息で滑らか/抑揚小さく)に整理して短くした。",
        "短い言葉を、ひと息で滑らかに。抑揚は小さく自然にしてください。"),
 "Q2": ("R2対応: 親しみ(言葉の意味をそっと教える)", "M2に「友人に言葉の意味をそっと教える」親しみを追加し、冷たい辞書調を避ける。",
        "友人に言葉の意味をそっと教えるように、やさしく自然な声で。一つの意味のまとまりとして、途切れさせずに滑らかに、ひと息で読んでください。単語ごとに区切らず、抑揚の上下も小さくしてください。"),
 "Q3": ("R3対応: 適度な明るさ(微笑みを含んだ声)", "M2に、ほんのり笑みを含んだやわらかい明るさを追加。はしゃがない範囲。",
        "ほんのり笑みを含んだ、やわらかく明るい声で。一つの意味のまとまりとして、途切れさせずに滑らかに、ひと息で読んでください。単語ごとに区切らず、抑揚の上下も小さく自然にしてください。"),
 "Q4": ("R4対応: 控えめな表情(意味に合わせてほんの少し)", "M2に、語の意味に合わせた表情をごく控えめに加える。抑揚の付けすぎは禁止。",
        "言葉の意味に合わせて、表情をほんの少しだけ声にのせてください。ただし大げさにせず、一つの意味のまとまりとして、途切れさせずに滑らかに、ひと息で読んでください。抑揚の上下は小さく自然にしてください。"),
 "Q5": ("R5対応: 聞き取りやすさ(語頭・語尾をくっきり)", "M2に、語の頭と終わりまでくっきり聞き取れる指示を追加(硬くしない)。",
        "語の頭と終わりまでくっきり聞き取れるように、ただし硬くならないように。一つの意味のまとまりとして、途切れさせずに滑らかに、ひと息で読んでください。抑揚の上下は小さく自然にしてください。"),
 "Q6": ("R6対応: 意味の流れに沿った息", "M2の「ひと息」を「意味の流れに沿って息を切らさない」に置換し、単語境界の不自然な間を避ける。",
        "意味の流れに沿って、息を切らさずに一続きで読んでください。単語の境目で間を入れず、抑揚の上下も小さく自然にしてください。"),
 "Q7": ("R7対応: やわらかな語尾", "M2に、語尾を伸ばさず上げず、やわらかく収める指示を追加。",
        "一つの意味のまとまりとして、途切れさせずに滑らかに読み、語尾は伸ばさず上げず、やわらかく収めてください。単語ごとに区切らず、抑揚の上下も小さく自然にしてください。"),
 "Q8": ("R8対応: 落ち着いた温かさ", "M2を、落ち着いた穏やかな温かい声の指示に置換。明るさ控えめの対極案。",
        "落ち着いた温かみのある声で、静かに読んでください。一つの意味のまとまりとして、途切れさせずに滑らかに、ひと息で。単語ごとに区切らず、抑揚の上下も小さく自然にしてください。"),
}
SEG = g.SEG_NAMES


def sha_s(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def jobs():
    kp, segs = g.load_texts()
    J = []
    for sid, (_, _, style) in R.items():
        for nm in SEG:
            J.append({"id": f"{sid}_{nm}", "spec": sid, "grp": "D", "text": segs[nm]["tts"], "style": style, "voice": g.VOICE_JA, "margin": g.JA_MARGIN, "lang": "ja"})
    for sid, (_, _, style) in Q.items():
        for it in kp:
            J.append({"id": f"{sid}_kp{it['idx']}", "spec": sid, "grp": "C", "text": it["ja"], "style": style, "voice": g.VOICE_JA, "margin": g.JA_MARGIN, "lang": "ja"})
    return J, kp, segs


def write_prompts():
    J, kp, segs = jobs()
    d = "# Prompt一覧 R1〜R8(Preview/Comment1〜4、Standard日本語Aoede)\n\n送信方式: generate_content、Part(text=<原稿逐語>, speech_metadata=SpeechMetadata(style=<下記>))、model=gemini-3.8-flash-lite-tts、voice=Aoede、language_code=ja-JP、Standard同期(DEV)。\n\n"
    d += f"## 基準 P2(Final v2採用、逐語、{len(P2)}文字、sha256={sha_s(P2)})\n\n```\n{P2}\n```\n\n"
    for sid, (ap, aim, st) in R.items():
        d += f"## {sid} {ap}\n\n- 文字数: {len(st)}(P2={len(P2)}、差{len(st)-len(P2):+d})\n- 調整内容・狙い: {aim}\n- sha256: {sha_s(st)}\n\nstyle(逐語):\n\n```\n{st}\n```\n\n"
    c = "# Prompt一覧 Q1〜Q8(KP日本語意味、Standard日本語Aoede)\n\n送信方式はRと同じ。原稿(tts_safe後): " + " / ".join(f"`{it['ja']}`" for it in kp) + "\n\n"
    c += f"## 基準 M2(Final v2採用、逐語、{len(M2)}文字、sha256={sha_s(M2)})\n\n```\n{M2}\n```\n\n"
    for sid, (ap, aim, st) in Q.items():
        c += f"## {sid} {ap}\n\n- 文字数: {len(st)}(M2={len(M2)}、差{len(st)-len(M2):+d})\n- 調整内容・狙い: {aim}\n- sha256: {sha_s(st)}\n\nstyle(逐語):\n\n```\n{st}\n```\n\n"
    open(f"{PROMPTS}/prompts_R.md", "w", encoding="utf-8").write(d)
    open(f"{PROMPTS}/prompts_Q.md", "w", encoding="utf-8").write(c)
    meta = {"P2": {"chars": len(P2), "sha256": sha_s(P2)}, "M2": {"chars": len(M2), "sha256": sha_s(M2)},
            **{k: {"chars": len(v[2]), "sha256": sha_s(v[2])} for k, v in {**R, **Q}.items()}}
    json.dump(meta, open(f"{PROMPTS}/prompt_sha256.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("prompts written; jobs=", len(J))
    for k, v in meta.items():
        print(k, v["chars"], v["sha256"][:12])


def estimate():
    J, kp, segs = jobs()
    tot_s = tot_in = 0.0
    for j in J:
        base = f"{PREV}/raw/P2_{j['id'].split('_',1)[1]}.wav" if j["grp"] == "D" else f"{PREV}/raw/M2_kp{j['id'].split('kp')[1]}.wav"
        tot_s += sf.info(base).duration + 0.6
        tot_in += (len(j["text"]) + len(j["style"])) / 2.0 + 20
    usd = tot_s * 25 * g.PRICE_OUT_PER_M / 1e6 + tot_in * g.PRICE_IN_PER_M / 1e6
    jpy, jpy_r = usd * g.USD_JPY, usd * 1.2 * g.USD_JPY
    asr_jpy = 90 / 60 * 0.003 * g.USD_JPY * 1.5   # 90件x約1分/60件相当の保守的見積(gpt-4o-mini-transcribe目安$0.003/分)
    md = (f"# COST_ESTIMATE_01 (2026-10-12)\n\n- call数: {len(J)} (R 8x5=40 + Q 8x5=40)。各1回、技術失敗時のみ1回retry(見込み+20%)。基準P2/M2は既存音声再利用(再TTSなし)。\n"
          f"- 想定出力音声: 約{tot_s:.0f}秒(基準P2/M2の既存尺+margin、25 token/秒)。入力token約{tot_in:.0f}(保守的)。\n"
          f"- 単価(01Bと同一式): 出力${g.PRICE_OUT_PER_M}/M tokens、入力${g.PRICE_IN_PER_M}/M tokens、USD_JPY={g.USD_JPY}。\n"
          f"- TTS概算: ${usd:.4f} = 約JPY {jpy:.1f}(retry+20%見込み 約JPY {jpy_r:.1f})。\n"
          f"- ASR(Primary OpenAI ja-JP、候補80+基準10=90件): 約JPY {asr_jpy:.1f}以下(保守的見積)。\n"
          f"- 合計概算 約JPY {jpy_r+asr_jpy:.1f}(retry込み・ASR込み)。上限JPY 25。上限以下なら実行可、超過ならSTOP。\n")
    open(f"{OUT}/COST_ESTIMATE_01.md", "w", encoding="utf-8").write(md)
    print(md)


def call_tts_mv(text, style, voice):
    """g.call_ttsと同一リクエスト形。応答model_versionをusageへ追記するための複製(挙動は同一)。"""
    import er033_tts_flash_lite_backend_wiring_01 as flw
    import er006_model_routing_contract_01 as rc
    import er002_gemini_client as gclient
    import er002_common as common
    from google.genai import types
    flw.assert_sdk_supports_speech_metadata()
    model = rc.require_model(flw.FAMILY_X_FLASH_LITE_TTS_PROCESS, g.MODEL)
    if g._client is None:
        g._client = gclient.make_client()
    content = types.Content(parts=[types.Part(text=text, speech_metadata=types.SpeechMetadata(style=style))], role="user")
    resp = g._client.models.generate_content(
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
             "total_tokens": getattr(u, "total_token_count", None), "model_version": getattr(resp, "model_version", None)}
    return samples, usage


def probe_model_version():
    """本Trial生成(80 call)時はmodel_versionを記録し損ねたため、同一リクエスト形で1 call(Q1 style・kp1)だけ追加実行し応答model_versionを実測記録(音声は保存しない)。"""
    J, kp, segs = jobs()
    j = [x for x in J if x["id"] == "Q1_kp1"][0]
    _, usage = call_tts_mv(j["text"], j["style"], j["voice"])
    json.dump({"probe_id": "Q1_kp1", "usage": usage, "note": "本生成でmodel_version未記録のため追加1 callで実測(音声は破棄)"},
              open(f"{OUT}/model_version_probe_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(usage)


def gen():
    g.RAW = RAW
    g.call_tts = call_tts_mv
    J, *_ = jobs()
    rp = f"{OUT}/results_01.jsonl"
    done = {}
    if os.path.exists(rp):
        for l in open(rp, encoding="utf-8"):
            r = json.loads(l); done[r["id"]] = r
    todo = [j for j in J if done.get(j["id"], {}).get("status") != "OK"]
    print("todo", len(todo), flush=True)
    res = dict(done)
    t0 = time.time()
    with cf.ThreadPoolExecutor(6) as ex:
        for r in ex.map(g.gen_one, todo):
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
                pt += u.get("prompt_tokens") or 0; ct += u.get("candidates_tokens") or 0
    usd = ct * g.PRICE_OUT_PER_M / 1e6 + pt * g.PRICE_IN_PER_M / 1e6
    cost = {"calls_total": calls, "jobs": len(J), "ok": sum(r["status"] == "OK" for r in res.values()), "prompt_tokens": pt, "candidates_tokens": ct,
            "est_usd": round(usd, 5), "est_jpy": round(usd * g.USD_JPY, 2), "wall_seconds_this_run": round(time.time() - t0, 1),
            "basis": "usage_metadata実測tokens×Standard単価(出力$6/M、入力$0.5/M)、USD_JPY=160。請求画面は未確認"}
    json.dump(cost, open(f"{OUT}/cost_actual_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(cost)


def asr():
    """Primary ASR(routing.transcribe, ja-JP)+classify_ja_asr_match(純関数)のみ。cascade/human_review_log/再生成は呼ばない。NGでも再生成しない。"""
    import er006_asr_provider_routing_01 as routing
    import er007_ja_asr_validator_01 as javal
    J, kp, segs = jobs()
    items = [(j["id"], j["text"], f"{RAW}/{j['id']}.wav") for j in J]
    for nm in SEG:
        items.append((f"P2_{nm}", segs[nm]["tts"], f"{PREV}/raw/P2_{nm}.wav"))
    for it in kp:
        items.append((f"M2_kp{it['idx']}", it["ja"], f"{PREV}/raw/M2_kp{it['idx']}.wav"))

    def one(x):
        i, text, p = x
        t, err = routing.transcribe(p, language="ja-JP")
        c = javal.classify_ja_asr_match(text, t)
        return {"id": i, "canonical": text, "asr_text": t, "asr_error": err, "classification": c.classification,
                "should_pass": c.should_pass, "len_ratio": round(len(t) / len(text), 3) if t else None}
    with cf.ThreadPoolExecutor(6) as ex:
        out = list(ex.map(one, items))
    with open(f"{OUT}/asr_results_01.jsonl", "w", encoding="utf-8") as f:
        for r in out:
            f.write(json.dumps(r, ensure_ascii=False, default=str) + "\n")
    from collections import Counter
    print(Counter(r["classification"] for r in out))
    for r in out:
        if r["classification"] not in ("EXACT_MATCH", "NORMALIZED_MATCH"):
            print(r["id"], r["classification"], r["canonical"], "=>", r["asr_text"])


if __name__ == "__main__":
    {"probe": probe_model_version, "specs": write_prompts, "estimate": estimate, "gen": gen, "asr": asr}[sys.argv[1]]()
