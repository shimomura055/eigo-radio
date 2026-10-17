# -*- coding: utf-8 -*-
"""FAMILY-X-COFFEE-STANDARD-JA-SUPPORT-CALM-STYLE-TRIAL-04 委任_01 Trial専用script(Production非経由、DEV経路)。
基準P2・R2(前回Trial 02の逐語、sha検証)+新規S1〜S8(個別指示+共通指示)を、正式Coffee E2E(coffee_prices__run_fxpw_01)の
Std Preview/Comment1〜4(TTSへ実際に渡したtext)で、各2 Take(A/B)生成し、JA ASR(前回Trial 02と同方式)を実行する。
Master Store/manifest/telemetry/queue/attempt_history/cost_loggerへは書かない。Voice/model/margin/language/後処理は前回Trial 02(=正式版と同一request形)を再利用。
modes: --specs-only / --estimate-only / (生成) / --asr-only"""
import os, sys, json, hashlib, time, argparse, re, concurrent.futures as cf
sys.path.insert(0, os.getcwd())
from dotenv import load_dotenv
load_dotenv()
import er057_ja_aoede_style_trial_02 as t   # 前回Trial(P2/R2の取得元、call_tts_mv)
g = t.g

ROOT = g.ROOT
FORMAL = f"{ROOT}/er019_output/family_x_audio_production_wiring_01/coffee_prices__run_fxpw_01/a2"
PREV_DIR = f"{ROOT}/er057_output/ja_aoede_style_trial_02"
SEG = g.SEG_NAMES
TAKES = ("A", "B")

COMMON = "句読点は自然な間として扱い、記号だけを理由に声の高さを変えないでください。問いかけは穏やかに読み、語尾を大きく跳ね上げないでください。演技がかった強調は避けてください。"

# (見出し名[ユーザー原文], 狙い1行, 個別指示[ユーザー原文逐語])
S = {
 "S1": ("P2の穏やかな修正版", "P2の温かみ・明瞭さを保ち、全体の明るさと文末の力みを抑える。",
        "温かみのある、親しみやすい自然な話し方で。聞き手に穏やかに語りかけるように、内容に沿った控えめな抑揚をつけてください。ニュース番組としての明瞭さを保ち、全体の明るさは控えめにしてください。文末は力を抜いて自然に収めてください。"),
 "S2": ("R2の穏やかな修正版", "R2の「身近な人に伝える」親しみを保ち、調子を落ち着かせ、抑揚を大切な点だけに絞る。",
        "身近な人に興味深い話題を伝えるように、温かみのある自然な話し方で。親しみやすさを保ちながら、落ち着いた調子と無理のないリズムで話してください。大切な点にだけ軽く抑揚をつけ、語尾はやわらかく収めてください。言葉は明瞭に伝えてください。"),
 "S3": ("親しみのあるニュースナレーター", "温かい親しみ+安定した声。抑揚は重要語・対比のみ、文末は軽く下げる。",
        "温かみと親しみのあるニュースナレーターとして、落ち着いた、明瞭な声で伝えてください。声の調子は安定させ、重要な言葉や対比にだけ控えめな抑揚をつけてください。文末は軽く下げて自然に収め、聞き手が内容を追いやすい流れで読んでください。"),
 "S4": ("身近なニュース解説者", "背景を身近な人に説明する口調で、説明の途中でテンションを上げない。",
        "ニュースの背景を身近な人に説明するように、親しみやすく落ち着いた口調で話してください。内容への関心を穏やかに示し、要点や話のつながりを明瞭に伝えてください。説明の途中でテンションを上げず、文末は力を抜いてやわらかく収めてください。"),
 "S5": ("穏やかなニュース系Podcaster", "落ち着いたニュース系Podcastホストの会話調。明るさ控えめ、語尾は短く自然に。",
        "落ち着いたニュース系Podcastのホストとして、温かみのある自然な会話調で話してください。聞き手と話題を共有するような親しみを持ち、内容に沿った穏やかな抑揚と滑らかなリズムで伝えてください。声の明るさは控えめにし、語尾は短く自然に収めてください。"),
 "S6": ("一人の聞き手に向けたPodcaster", "一人の聞き手に丁寧に伝える距離感。普段の会話に近い調子、抑揚は意味を伝える範囲のみ。",
        "関心を持って聞いている一人の相手に、話題を丁寧に伝えるPodcastホストのように話してください。身近で温かい距離感を保ち、落ち着いた普段の会話に近い調子で伝えてください。抑揚は意味を伝えるために必要な範囲にとどめ、文末はやわらかく収めてください。"),
 "S7": ("ニュースの明瞭さ＋Podcastの親しみ", "ニュースの明瞭さとPodcastの親しみを合わせる。要点・対比に軽く抑揚、語尾は伸ばさない。",
        "ニュースナレーターの明瞭さと、Podcastホストの親しみやすさを合わせた話し方で。温かみのある落ち着いた声で、聞き手に自然に語りかけてください。要点や対比には軽く抑揚をつけ、それ以外は穏やかな調子を保ってください。語尾を伸ばさず、自然に収めてください。"),
 "S8": ("さらに抑揚を抑えた中間型", "明瞭さ+温かみの中間型で、抑揚とテンションをさらに抑え、関連する文を滑らかにつなぐ。",
        "ニュースナレーターの明瞭さと、Podcastホストの温かみを持つ、落ち着いた話し方で。声の調子とテンションを穏やかに保ち、重要な点にだけ小さく抑揚をつけてください。親しみはやわらかな声で表し、文末は軽く下げて収めてください。関連する文は滑らかにつないでください。"),
}
# 最終Style全文 = 個別指示 + 共通指示(区切りなしで直接連結。前回Trial 02のR2〜R8がPUNCTを直接連結した方式と同じ)。基準P2/R2は共通指示なし。
STYLES = {}


def sha_s(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def load_baselines():
    """P2/R2は前回Trial 02モジュールの実文字列(g.D_SPECS['P2'], t.R['R2'])をそのまま使い、
    (1)前回Trial記録 prompt_sha256.json (2)前回Prompt一覧 prompts_R.md のコードブロック逐語 (3)Production R2定数 と照合する。不一致なら例外(STOP)。"""
    P2, R2 = t.P2, t.R["R2"][2]
    rec = json.load(open(f"{PREV_DIR}/prompts/prompt_sha256.json", encoding="utf-8"))
    md = open(f"{PREV_DIR}/prompts/prompts_R.md", encoding="utf-8").read()
    blocks = re.findall(r"```\n(.*?)\n```", md, re.S)
    assert P2 in blocks and R2 in blocks, "P2/R2 not verbatim in prompts_R.md"
    assert sha_s(P2) == rec["P2"]["sha256"] and len(P2) == rec["P2"]["chars"], "P2 sha mismatch vs build record"
    assert sha_s(R2) == rec["R2"]["sha256"] and len(R2) == rec["R2"]["chars"], "R2 sha mismatch vs build record"
    import er019_family_x_style_profile_01 as sp
    prod_match = (R2 == sp.R2_TEXT and sha_s(R2) == sp.R2_SHA256)
    return P2, R2, rec, prod_match, sp.R2_SHA256


def build_styles():
    P2, R2, rec, prod_match, prod_sha = load_baselines()
    STYLES["P2"] = P2
    STYLES["R2"] = R2
    for k, (_, _, ind) in S.items():
        STYLES[k] = ind + COMMON
    return rec, prod_match, prod_sha


def load_texts():
    """正式run(coffee_prices__run_fxpw_01)の、TTSへ実際に渡したtext(tts_generation_results.json segments[*].text)。
    a2_support_texts.json から本Trialと同じ変換(tts_safe_ja→to_tts_safe_japanese_fraction_reading)で再計算した値との一致も検証する。"""
    import er003_v1_n3_01_tts_generate as n3
    import er003_audio_tts_asr_safety as safety
    res = json.load(open(f"{FORMAL}/audit/tts_generation_results.json", encoding="utf-8"))["segments"]
    st = json.load(open(f"{FORMAL}/a2_support_texts.json", encoding="utf-8"))
    out = {}
    for nm in SEG:
        sent = res[nm]["text"]
        recomputed = safety.to_tts_safe_japanese_fraction_reading(n3.tts_safe_ja(st[nm]))
        assert sent == recomputed, f"formal sent text mismatch: {nm}"
        out[nm] = {"tts": sent, "manuscript": st[nm], "sha256": sha_s(sent), "formal_status": res[nm]["status"],
                   "formal_duration_s": res[nm]["duration_seconds"]}
    return out


ORDER = ["P2", "R2"] + list(S)


def jobs(texts):
    J = []
    for tk in TAKES:           # Take A全件 → Take B全件(独立呼出)
        for sid in ORDER:
            for nm in SEG:
                J.append({"id": f"{sid}_{tk}_{nm}", "spec": sid, "take": tk, "seg": nm, "grp": "D", "text": texts[nm]["tts"],
                          "style": STYLES[sid], "voice": g.VOICE_JA, "margin": g.JA_MARGIN, "lang": "ja"})
    return J


def write_prompts(out_dir, rec, prod_match, prod_sha, texts):
    d = ("# PROMPTS_01 (SJS4: Coffee Std日本語 Preview/Comment Style比較 Trial 04)\n\n"
         "送信方式: generate_content、Part(text=<原稿>, speech_metadata=SpeechMetadata(style=<下記Style全文>))、model=gemini-3.8-flash-lite-tts、voice=Aoede、language_code=ja-JP、Standard同期(DEV Trial)。\n\n"
         f"S1〜S8のStyle全文 = 個別指示(ユーザー原文逐語)+共通指示(区切りなしで直接連結)。基準P2・R2は共通指示を付けていない(前回Trial 02の逐語)。\n\n"
         f"共通指示({len(COMMON)}文字、sha256={sha_s(COMMON)}):\n\n```\n{COMMON}\n```\n\n")
    d += f"## 基準 P2(前回Trial 02、逐語、{len(STYLES['P2'])}文字、sha256={sha_s(STYLES['P2'])})\n\n取得元: er057_ja_aoede_style_trial_02.py:20 `P2 = g.D_SPECS[\"P2\"][1]`(er057_tone_trial_kp_ja_gen_01.py:73)、前回記録 {PREV_DIR.split('/')[-1]}/prompts/prompt_sha256.json と一致。\n\n```\n{STYLES['P2']}\n```\n\n"
    d += (f"## 基準 R2(前回Trial 02、逐語、{len(STYLES['R2'])}文字、sha256={sha_s(STYLES['R2'])})\n\n取得元: er057_ja_aoede_style_trial_02.py:28 `R[\"R2\"]`。"
          f"Production R2定数(er019_family_x_style_profile_01.py R2_TEXT/R2_SHA256={prod_sha})と文字列・sha一致={prod_match}。\n\n```\n{STYLES['R2']}\n```\n\n")
    for k, (name, aim, ind) in S.items():
        st = STYLES[k]
        d += f"## {k} {name}\n\n- 狙い: {aim}\n- 文字数: {len(st)}(個別{len(ind)}+共通{len(COMMON)})\n- sha256: {sha_s(st)}\n\nTTSへ渡したStyle全文:\n\n```\n{st}\n```\n\n"
    d += "## 原稿5 section(TTSへ渡した実text、正式run coffee_prices__run_fxpw_01 a2/audit/tts_generation_results.json segments[*].text)\n\n"
    for nm in SEG:
        d += f"- {nm}: {len(texts[nm]['tts'])}文字 sha256={texts[nm]['sha256']}\n\n  {texts[nm]['tts']}\n"
    open(f"{out_dir}/PROMPTS_01.md", "w", encoding="utf-8").write(d)
    meta = {k: {"chars": len(v), "sha256": sha_s(v)} for k, v in STYLES.items()}
    meta["_common"] = {"chars": len(COMMON), "sha256": sha_s(COMMON)}
    json.dump({"styles": meta, "texts": {nm: {"chars": len(v["tts"]), "sha256": v["sha256"]} for nm, v in texts.items()},
               "p2_r2_vs_prev_record": {"P2": rec["P2"], "R2": rec["R2"]}, "r2_equals_production": prod_match, "production_r2_sha": prod_sha},
              open(f"{out_dir}/prompt_sha256.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def estimate(out_dir, texts, budget):
    # 出力token=25 tok/s×音声秒(正式版の各segment実尺+trim margin≒raw尺で近似)。入力token≒(text+style)/2+20。単価は前回Trial 02同一式。
    sec = sum(v["formal_duration_s"] + 0.3 for v in texts.values())
    n_sets = len(ORDER) * len(TAKES)
    out_tok = sec * 25 * n_sets
    in_tok = 0
    for sid in ORDER:
        for nm in SEG:
            in_tok += ((len(texts[nm]["tts"]) + len(STYLES[sid])) / 2.0 + 20) * len(TAKES)
    usd = out_tok * g.PRICE_OUT_PER_M / 1e6 + in_tok * g.PRICE_IN_PER_M / 1e6
    jpy = usd * g.USD_JPY
    jpy_r = jpy * 1.1
    asr_min = sec * n_sets / 60.0
    asr_jpy = asr_min * 0.003 * g.USD_JPY   # gpt-4o-mini-transcribe目安$0.003/分
    md = (f"# COST_ESTIMATE_01 (2026-10-17, API 0)\n\n- call数: {len(ORDER)}仕様×{len(TAKES)}Take×{len(SEG)}section = {len(ORDER)*len(TAKES)*len(SEG)}。技術失敗時のみ1回retry(+10%見込み)。\n"
          f"- 想定出力音声: 1セット約{sec:.1f}秒(正式版5 segment実尺+margin)×{n_sets}セット = 約{sec*n_sets:.0f}秒。出力token約{out_tok:.0f}、入力token約{in_tok:.0f}。\n"
          f"- 単価(前回Trial 02と同一式): 出力${g.PRICE_OUT_PER_M}/M、入力${g.PRICE_IN_PER_M}/M、USD_JPY={g.USD_JPY}。\n"
          f"- TTS概算: ${usd:.4f} = 約JPY {jpy:.1f}(retry+10%込み 約JPY {jpy_r:.1f})。\n"
          f"- ASR(OpenAI、約{asr_min:.1f}分、$0.003/分目安): 約JPY {asr_jpy:.1f}。\n"
          f"- 合計概算 約JPY {jpy_r+asr_jpy:.1f}。Guardrail JPY{budget}(接近・超過は記録して継続可)、7-7 JPY100判定: {'超過見込みなし' if jpy_r+asr_jpy < 100 else '超過見込み→実行せず報告'}。\n"
          f"- 補足: 委任文の見積(期待約JPY20)は前回Trial 02の80 clip(うちKP短clip 40)を件数比例で外挿したもの。今回は全clipが長いPreview/Comment(1セット約{sec:.0f}秒)のため、音声秒ベースでは上記が妥当。前回実測 JPY13.73(85 call、候補40セグメント分は約12,800出力token)と25 tok/s換算で整合。\n"
          f"- 再利用/差分再生成: 新規Style×新規Takeの独立生成が目的のため再利用キャッシュ・差分再生成は対象外(Master Audio Store/キャッシュは参照しない)。\n")
    open(f"{out_dir}/COST_ESTIMATE_01.md", "w", encoding="utf-8").write(md)
    print(md)
    return jpy_r + asr_jpy


def gen(out_dir, texts, budget, workers):
    raw = f"{out_dir}/raw"
    os.makedirs(raw, exist_ok=True)
    g.RAW = raw
    g.call_tts = t.call_tts_mv
    J = jobs(texts)
    rp = f"{out_dir}/results_01.jsonl"
    done = {}
    if os.path.exists(rp):
        for l in open(rp, encoding="utf-8"):
            r = json.loads(l); done[r["id"]] = r
    todo = [j for j in J if done.get(j["id"], {}).get("status") != "OK"]
    print("todo", len(todo), "of", len(J), flush=True)
    meta = {j["id"]: j for j in J}
    res = dict(done)
    t0 = time.time()
    calls = 0
    with cf.ThreadPoolExecutor(workers) as ex, open(rp, "a", encoding="utf-8") as f:
        for r in ex.map(g.gen_one, todo):
            j = meta[r["id"]]
            r["take"], r["seg"], r["spec"] = j["take"], j["seg"], j["spec"]
            res[r["id"]] = r
            f.write(json.dumps(r, ensure_ascii=False) + "\n"); f.flush()
            calls += r.get("call_count", 0)
            print(r["id"], r["status"], r.get("duration_s"), r.get("reason", ""), flush=True)
            if calls > 150:   # 暴走防止(100 job想定に対し異常なAPI call数)
                print("RUNAWAY GUARD: calls>150, abort", flush=True); break
    # 正規化して再書込(job順)
    with open(rp, "w", encoding="utf-8") as f:
        for j in J:
            if j["id"] in res:
                f.write(json.dumps(res[j["id"]], ensure_ascii=False) + "\n")
    cost_report(out_dir, res, J, time.time() - t0, budget)


def cost_report(out_dir, res, J, wall, budget, asr_extra=None):
    pt = ct = calls = retries = 0
    for r in res.values():
        calls += r.get("call_count", 0); retries += r.get("retry_count", 0) or (r.get("call_count", 1) - 1)
        for u in r.get("usage", []) or []:
            if u:
                pt += u.get("prompt_tokens") or 0; ct += u.get("candidates_tokens") or 0
    usd = ct * g.PRICE_OUT_PER_M / 1e6 + pt * g.PRICE_IN_PER_M / 1e6
    cost = {"calls_total": calls, "jobs": len(J), "ok": sum(r["status"] == "OK" for r in res.values()), "retry_calls": calls - len(res),
            "prompt_tokens": pt, "candidates_tokens": ct, "tts_est_usd": round(usd, 5), "tts_est_jpy": round(usd * g.USD_JPY, 2),
            "wall_seconds_this_run": round(wall, 1), "budget_guardrail_jpy": budget,
            "basis": "usage_metadata実測tokens×Standard単価(出力$6/M、入力$0.5/M)、USD_JPY=160。請求画面は未確認"}
    if os.path.exists(f"{out_dir}/asr_results_01.jsonl") and False:
        pass
    json.dump(cost, open(f"{out_dir}/cost_actual_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(cost)


def asr(out_dir, texts, workers):
    """前回Trial 02と同方式: Primary ASR(routing.transcribe, ja-JP)+classify_ja_asr_match(純関数)。cascade/再生成は呼ばない。"""
    import er006_asr_provider_routing_01 as routing
    import er007_ja_asr_validator_01 as javal
    import soundfile as sf
    J = jobs(texts)
    done = {}
    ap = f"{out_dir}/asr_results_01.jsonl"
    if os.path.exists(ap):
        for l in open(ap, encoding="utf-8"):
            r = json.loads(l); done[r["id"]] = r
    items = [j for j in J if os.path.exists(f"{out_dir}/raw/{j['id']}.wav") and done.get(j["id"], {}).get("asr_error") in (None, "") and j["id"] not in done]

    def one(j):
        p = f"{out_dir}/raw/{j['id']}.wav"
        tx, err = routing.transcribe(p, language="ja-JP")
        c = javal.classify_ja_asr_match(j["text"], tx)
        dur = sf.info(p).duration
        return {"id": j["id"], "spec": j["spec"], "take": j["take"], "seg": j["seg"], "canonical": j["text"], "asr_text": tx, "asr_error": err,
                "classification": c.classification, "should_pass": c.should_pass, "len_ratio": round(len(tx) / len(j["text"]), 3) if tx else None,
                "audio_seconds": round(dur, 3)}
    with cf.ThreadPoolExecutor(workers) as ex:
        out = list(ex.map(one, items))
    allr = dict(done)
    for r in out:
        allr[r["id"]] = r
    with open(ap, "w", encoding="utf-8") as f:
        for j in J:
            if j["id"] in allr:
                f.write(json.dumps(allr[j["id"]], ensure_ascii=False, default=str) + "\n")
    from collections import Counter
    print(Counter(r["classification"] for r in allr.values()))
    mins = sum(r["audio_seconds"] for r in allr.values()) / 60
    print("asr_audio_minutes", round(mins, 2), "est_jpy", round(mins * 0.003 * g.USD_JPY, 2))
    json.dump({"asr_clips": len(allr), "audio_minutes": round(mins, 2), "est_jpy": round(mins * 0.003 * g.USD_JPY, 2),
               "basis": "gpt-4o-mini-transcribe目安$0.003/分×USD_JPY160(推定、請求画面未確認)"},
              open(f"{out_dir}/asr_cost_estimate_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=f"{ROOT}/er057_output/ja_support_calm_style_trial_04")
    ap.add_argument("--takes", type=int, default=2)
    ap.add_argument("--budget-jpy", type=float, default=40)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--specs-only", action="store_true")
    ap.add_argument("--estimate-only", action="store_true")
    ap.add_argument("--asr-only", action="store_true")
    a = ap.parse_args()
    assert a.takes == 2
    if os.environ.get("TTS_EXECUTION_MODE") not in (None, "STANDARD") and not (a.specs_only or a.estimate_only):
        raise SystemExit("TTS_EXECUTION_MODE must be STANDARD")
    out_dir = os.path.abspath(a.out_dir)
    os.makedirs(out_dir, exist_ok=True)
    rec, prod_match, prod_sha = build_styles()
    texts = load_texts()
    write_prompts(out_dir, rec, prod_match, prod_sha, texts)
    print("styles:", {k: (len(v), sha_s(v)[:12]) for k, v in STYLES.items()}, "R2==Production:", prod_match)
    if a.specs_only:
        sys.exit(0)
    est = estimate(out_dir, texts, a.budget_jpy)
    if a.estimate_only:
        sys.exit(0)
    if est >= 100:
        raise SystemExit("estimate >= JPY100: do not run, report (7-7)")
    if a.asr_only:
        asr(out_dir, texts, 4)
    else:
        gen(out_dir, texts, a.budget_jpy, a.workers)
        asr(out_dir, texts, 4)
