# -*- coding: utf-8 -*-
"""er110_family_y_persona_text_trial_01_run.py -- Family Y Persona→Voice Trial(Phase B テキスト段階)の薄い入口(DEV/Trial専用)。

subcommand(各自1回実行。監督ループ・自動再試行ラッパは持たない。既存artifactがあれば再利用=二重課金防止):
  b0       : Leakage positive/negative control(現行判定[旧Y Trial build_leakage_prompt]を許容リストなしで3回)
  text     : Voice×3(別call)→ Voice Leakage Gate → Tension+Closing → Tension Leakage Gate → 見出し → 日本語原稿 article_ja.md
  english  : 忠実英訳(Y wrapper)→ In One Line → Std簡易化(Y wrapper)→ 4パート確認 →(監視Leakage)
  scaffold : Comment 1/2(Y role)・Preview・Key Phrases・日本語タイトル(X scaffold部品を呼ぶのみ)
  rf       : Risk Flagger(X既定、非停止。Queueは本Trial dir内)
X共有関数は呼ぶのみで無変更。run dir は er110_output/family_y_persona_trial_01/school_phone_ban/<iter>/(X/Z出力dirには書かない)。
"""
import argparse
import glob
import hashlib
import json
import os
import re
import shutil
import sys

import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_advanced_adaptation_generate as adv_gen
import er003_v1_n3_01_standard_a2_generate as std_gen
import er005_cost_logger as cl
import er012_e_family_entertainment_two_level_runner_01 as efam
import er053_family_x_factlock_ja_writer_01 as w1
import er110_family_y_text_trial_01 as y0
import er110_family_y_persona_text_trial_01 as p

ROOT = "er110_output/family_y_persona_trial_01/school_phone_ban"
OLD_RUN = "er110_output/family_y_trial_01/school_phone_ban"       # 台帳(研究結果)の再利用元。読取りのみ
JA_TITLE = "朝に預けるスマホ、それぞれの声"
BUDGET = 70.0     # このTrialのrun dir単位の保険(Y Trial残枠74.62円の内数。超過見込みで停止)


def _client():
    return vfl01.get_client()


def ledger_text() -> str:
    dst = f"{ROOT}/research_ledger/verified_fact_ledger.txt"
    if not os.path.exists(dst):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(f"{OLD_RUN}/research_ledger/verified_fact_ledger.txt", dst)       # 0円(台帳再利用)
    return w1.rdt(dst)


def total_cost_jpy(rd: str = ROOT) -> float:
    import er053_cost_aggregate_01 as ca
    return round(sum(ca.compute_stage_cost_breakdown_multi(f)["total_jpy"] for f in glob.glob(f"{rd}/**/raw_usage_log*.jsonl", recursive=True)), 3)


def guard(note: str):
    c = total_cost_jpy()
    if c > BUDGET:
        raise RuntimeError(f"[BUDGET_GUARD] cost so far {c} JPY > cap {BUDGET} JPY ({note})")
    print(f"[Y-PERSONA] cost so far {c} JPY ({note})")


# ============================================================
# B-0: Leakage positive/negative control(現行判定のまま、許容リストなし)
# ============================================================
B0_BASES = {
    "A": ("現場の仕事で、帰りはいつも遅い。家に着くと、娘は居間でスマホを見ている。取り上げると、翌朝の食卓が冷える。"
          "この前も、娘に「みんなは返事が早いのに、私だけ遅れると外される」と言われて、俺は何も言えなかった。"
          "学校が決めてくれたら、俺は楽になる。正直、そう思う。家では俺ひとりが悪者だ。結局、楽したいだけなんだよな、俺は。"),
    "B": ("朝いちばんの保健室に、眠そうな子が来る。この前も、ベッドで寝ている子の枕元で画面が光っていた。眠い、って。頭が痛い、って。"
          "それを見ていると、夜のことが気になる。取り上げて、それで安心していいのかな。私は、保健室まで没収の場にしたくない。そう思う。"),
    "C": ("僕は昼、倉庫で荷物を仕分けして、夜に定時制へ通ってる。授業中は鞄の奥に入れる。約束する。でも、朝から預けっぱなしは無理だ。"
          "休憩中にシフトの連絡が来る。返事が遅いと、他の人に回される。信用をなくしたくない。決める前に、僕らの話を聞いてほしい。"),
}
B0_INSERT = {
    "P": "俺が聞いた話だと、国も高校は校内で使うのを控えさせる考えらしい。",
    "N1": "調べた研究では、校内の使用を制限した高校のほうが、授業に集中しやすいという結果が出ている。",
    "N2": "ある研究が、禁止した高校では生徒の集中が上がると示したらしい、と聞いた。",
}
B0_TENSION = ("3人とも、スマホで子どもが困らないでほしいと思っている。ただ、困る場所が違う。夜の居間のカゴ、朝の保健室のベッド、"
              "休憩中に届くシフトの連絡。守りたいものも、それぞれ違う。あなたの家では、夜、スマホはどこに置いてある?")
# Latin square: run k で (base, variant) を回す
B0_SQUARE = [(("A", "P"), ("B", "N1"), ("C", "N2")), (("B", "P"), ("C", "N1"), ("A", "N2")), (("C", "P"), ("A", "N1"), ("B", "N2"))]


def _with_insert(base: str, variant: str) -> str:
    sents = [s for s in y0.SENT_SPLIT_RE.split(base) if s.strip()]
    sents.insert(3, B0_INSERT[variant])
    return "".join(sents)


def cmd_b0(a):
    d = f"{ROOT}/b0"
    os.makedirs(d, exist_ok=True)
    cl.install(f"{d}/raw_usage_log.jsonl")
    client = _client()
    results = []
    for k, assign in enumerate(B0_SQUARE, start=1):
        fp = f"{d}/run{k}.json"
        if os.path.exists(fp):
            results.append(json.load(open(fp, encoding="utf-8")))
            continue
        secs = {}
        slots = {}
        for slot, (base, variant) in zip(("voice_1", "voice_2", "voice_3"), assign):
            secs[slot] = _with_insert(B0_BASES[base], variant)
            slots[slot] = {"base": base, "variant": variant}
        secs["tension"] = B0_TENSION
        chk = y0.run_leakage_check(client, secs, model=y0.MODEL_CHEAP, effort="high", stage=f"yp_b0_run{k}")
        out = {"run": k, "slots": slots, "sections": secs, "check": {x: chk[x] for x in ("model", "effort", "meta", "flagged_items", "any_flagged")},
               "parsed": chk["parsed"], "prompt_sha256": chk["prompt_sha256"]}
        w1.wj(fp, out)
        results.append(out)
    # 集計: variantごとのPASS/FAIL(voice_1..3の7項目)
    summ = {"P": [], "N1": [], "N2": []}
    for r in results:
        for slot, meta in r["slots"].items():
            it = r["parsed"][slot]
            fails = [f for f in y0.VOICE_LEAKAGE_FIELDS if it[f] == "FAIL"]
            summ[meta["variant"]].append({"run": r["run"], "base": meta["base"], "pass": not fails, "fail_fields": fails, "quoted": it["quoted_evidence"]})
    verdict = {
        "positive_control_P_all_pass": all(x["pass"] for x in summ["P"]),
        "negative_control_N1_all_fail": all(not x["pass"] for x in summ["N1"]),
        "negative_control_N2_all_fail": all(not x["pass"] for x in summ["N2"]),
    }
    w1.wj(f"{d}/b0_summary.json", {"summary": summ, "verdict": verdict, "judge": f"{y0.MODEL_CHEAP} high(M7校正済み現行判定・許容リストなし)",
                                   "note": "P=本人主語の伝聞1文(PASS期待) / N1=研究主語(FAIL期待) / N2=研究主語の伝聞形(FAIL期待)。各3回(base A/B/Cをラテン方陣で回転)"})
    print(json.dumps({"verdict": verdict, "P": [(x["base"], x["pass"], x["fail_fields"]) for x in summ["P"]],
                      "N1": [(x["base"], x["pass"], x["fail_fields"]) for x in summ["N1"]],
                      "N2": [(x["base"], x["pass"], x["fail_fields"]) for x in summ["N2"]]}, ensure_ascii=False, indent=1))
    guard("after b0")


# ============================================================
# text: Voice×3 → Gate → Tension → Gate → 見出し → 日本語原稿
# ============================================================
def cmd_text(a):
    rd = f"{ROOT}/{a.iter}"
    os.makedirs(rd, exist_ok=True)
    cl.install(f"{rd}/raw_usage_log.jsonl")
    client = _client()
    ledger_text()
    errs = p.validate_sheets()
    if errs:
        raise p.YStop("SHEET_INVALID", str(errs))
    w1.wj(f"{rd}/entry_point.json", {"runner": "er110_family_y_persona_text_trial_01_run.py", "management_id": p.MANAGEMENT_ID, "iter": a.iter,
                                      "started": p.now_iso(), "sheets": p.SHEETS, "common_premise": p.COMMON_PREMISE_JA,
                                      "module_sha256": hashlib.sha256(open("er110_family_y_persona_text_trial_01.py", "rb").read()).hexdigest(),
                                      "writer_model": p.MODEL_TOP, "judge_model": a.judge_model, "judge_effort": a.judge_effort})
    vd = f"{rd}/voices"
    voices = {}
    for s in p.VOICE_SLOTS:
        if not os.path.exists(f"{vd}/{s}.txt"):
            p.generate_voice(client, s, out_dir=vd)
            guard(f"after {s}")
        voices[s] = w1.rdt(f"{vd}/{s}.txt").strip()
    gv = f"{rd}/gate_voices"
    if not os.path.exists(f"{gv}/gate_result.json"):
        r = p.run_gate(client, kind="voices", stage="yp_voices_gate", texts=voices, out_dir=gv, judge_model=a.judge_model, judge_effort=a.judge_effort)
        print(f"[Y-PERSONA] voices gate status={r['status']} judgements={r['n_judgements']}")
        guard("after voices gate")
    voices_g = p.load_gated_or_stop(gv)
    td = f"{rd}/tension"
    if not os.path.exists(f"{td}/tension.txt"):
        p.generate_tension(client, voices_g, out_dir=td)
        guard("after tension")
    tension = w1.rdt(f"{td}/tension.txt").strip()
    gt = f"{rd}/gate_tension"
    if not os.path.exists(f"{gt}/gate_result.json"):
        r = p.run_gate(client, kind="tension", stage="yp_tension_gate", texts={"tension": tension}, out_dir=gt, voices_ctx=voices_g,
                       judge_model=a.judge_model, judge_effort=a.judge_effort)
        print(f"[Y-PERSONA] tension gate status={r['status']} judgements={r['n_judgements']}")
        guard("after tension gate")
    tension_g = p.load_gated_or_stop(gt)["tension"]
    hd = f"{rd}/headings"
    if not os.path.exists(f"{hd}/headings.json"):
        p.generate_headings(client, voices_g, out_dir=hd)
    paras = [voices_g[s] for s in p.VOICE_SLOTS] + [tension_g]
    w1.wt(f"{rd}/article_ja.md", p.render_article(JA_TITLE, paras))
    mon = {"voices": {s: p.voice_monitors(voices_g[s], s) for s in p.VOICE_SLOTS}, "tension": p.tension_monitors(tension_g)}
    w1.wj(f"{rd}/monitors_ja.json", mon)
    guard("after text")
    print("[Y-PERSONA] text完了")


# ============================================================
# english
# ============================================================
def _ja_to_adv(client, ja_text: str, ledger: str):
    r = adv_gen.generate_family_x_faithful_translation(ja_text, client=client, must_fix=p.y_contrast_must_fix())
    iol = efam._advanced_in_one_line(client, r.title, r.body, ja_text, ledger)
    return f"# {r.title}\n\n{r.body}\n\n## In one line\n{iol['text']}"


def cmd_english(a):
    rd = f"{ROOT}/{a.iter}"
    cl.install(f"{rd}/raw_usage_log_en.jsonl")
    client = _client()
    led = ledger_text()
    ed = f"{rd}/english"
    if os.path.exists(f"{ed}/en_summary.json"):
        print("skip english")
        return
    ja = w1.rdt(f"{rd}/article_ja.md")
    for st in ("gate_voices", "gate_tension"):
        p.load_gated_or_stop(f"{rd}/{st}")      # Acceptance Gate: PASS以外は後続へ流さない
    adv_path = f"{ed}/b1b/article.md"
    if os.path.exists(adv_path) and os.path.exists(f"{ed}/b1b/contract.json") and json.load(open(f"{ed}/b1b/contract.json", encoding="utf-8")).get("ok"):
        adv = w1.rdt(adv_path)        # resume: 契約PASS済みのAdvanced英訳は再生成しない(二重課金防止)
    else:
        adv = _ja_to_adv(client, ja, led)
    c = p.check_en_contract(adv)
    retried = False
    if not c["ok"] and any("PARAGRAPH_COUNT" in v for v in c["violations"]):
        retried = True
        r = adv_gen.generate_family_x_faithful_translation(ja, client=client, must_fix=p.y_contrast_must_fix() + efam._FAMILY_X_PARAGRAPH_RETRY_MUST_FIX)
        iol = efam._advanced_in_one_line(client, r.title, r.body, ja, led)
        adv = f"# {r.title}\n\n{r.body}\n\n## In one line\n{iol['text']}"
        c = p.check_en_contract(adv)
    w1.wt(f"{ed}/b1b/article.md", adv)
    w1.wj(f"{ed}/b1b/contract.json", {"retried": retried, **{k: v for k, v in c.items() if k != "split"}})
    if not c["ok"]:
        w1.wj(f"{ed}/en_summary.json", {"status": "ADV_CONTRACT_STOP", "violations": c["violations"]})
        print("Advanced 契約違反", c["violations"])
        return
    s = std_gen.generate_family_x_standard_a2_no_heading(adv, client=client, must_fix=p.y_contrast_must_fix())
    cs = p.check_en_contract(s.text)
    sretried = False
    if not cs["ok"] and any("PARAGRAPH_COUNT" in v for v in cs["violations"]):
        sretried = True
        s = std_gen.generate_family_x_standard_a2_no_heading(adv, client=client, must_fix=p.y_contrast_must_fix() + efam._FAMILY_X_PARAGRAPH_RETRY_MUST_FIX)
        cs = p.check_en_contract(s.text)
    w1.wt(f"{ed}/a2/article.md", s.text)
    w1.wj(f"{ed}/a2/contract.json", {"retried": sretried, **{k: v for k, v in cs.items() if k != "split"}})
    mon = {"b1b": p.en_monitors(adv), "a2": p.en_monitors(s.text)}
    w1.wj(f"{ed}/en_monitors.json", mon)
    s3 = {}
    if a.s3 and cs["ok"]:
        sp = p.split_en_article(s.text)
        vs = {k: sp["paragraphs"][i] for i, k in enumerate(p.VOICE_SLOTS)}
        s3["voices"] = p.run_leak(client, "voices", vs, model=y0.MODEL_CHEAP, effort="high", stage="yp_s3_leak_voices", language_note="英語")
        s3["tension"] = p.run_leak(client, "tension", {"tension": sp["paragraphs"][3]}, model=y0.MODEL_CHEAP, effort="high", stage="yp_s3_leak_tension",
                                   language_note="英語")
    w1.wj(f"{ed}/s3_monitor_leakage.json", s3)
    w1.wj(f"{ed}/en_summary.json", {"status": "OK" if cs["ok"] else "STD_CONTRACT_STOP", "std_violations": cs["violations"],
                                    "ja_sha256": w1.sha_text(ja), "adv_sha256": w1.sha_text(adv)})
    guard("after english")


# ============================================================
# scaffold: Comment 1/2 / Preview / KP / 日本語タイトル(X部品を呼ぶのみ)
# ============================================================
def cmd_scaffold(a):
    import er003_v1_b1_scaffold_01_generate as b1s
    import er003_v1_iran01_a2_generate as a2gen
    import er003_v1_n3_01_scaffold_generate as sc
    import er019_family_x_audio_production_runner_01 as ar
    rd = f"{ROOT}/{a.iter}"
    ed = f"{rd}/english"
    cl.install(f"{rd}/raw_usage_log_sc.jsonl")
    client = _client()
    led = ledger_text()
    facts = p.comment1_facts_block(led)
    w1.wj(f"{ed}/japanese_title.json", {"japanese_title": JA_TITLE, "source": "決定論(JA_TITLE定数)。LLM 0 call"})
    c1_ctx = (f"【番組で考える具体案】{p.COMMON_PREMISE_JA}\n\n【背景として使ってよい事実(確認済み。この範囲外の新しいFactは追加しない。"
              f"日付・数字は入れても入れなくてもよいが、改変しない)】\n{facts}")
    for level, gen, mfn, proc in (("b1b", b1s, ar._b1_support_model, "B1_SUPPORT"), ("a2", a2gen, ar._a2_support_model, "A2_SUPPORT")):
        sd = f"{ed}/scaffold_{level}"
        if os.path.exists(f"{sd}/scaffold_summary.json"):
            print("skip", level)
            continue
        text = w1.rdt(f"{ed}/{level}/article.md")
        sp = p.split_en_article(text)
        P = sp["paragraphs"]
        assert len(P) == 4
        c1 = gen.run_support_text(client, p.Y_COMMENT_1_ROLE[level], c1_ctx, model=mfn())
        c2 = gen.run_support_text(client, p.Y_COMMENT_2_ROLE[level],
                                  "【Comment 1(すでに聞いた内容)】\n" + (c1.get("text") or "") + "\n\n【これから聞く声の数】暮らしも立場も違う3人", model=mfn())
        prev_role = gen.PREVIEW_ROLE.format(comment_1=c1.get("text") or "(生成失敗)", comment_2=c2.get("text") or "(生成失敗)")
        prev = gen.run_support_text(client, prev_role, "【エピソード全文(参考、新しいFactの追加禁止)】\n# " + sp["title"] + "\n\n" + "\n\n".join(P), model=mfn())
        res = {"preview": prev, "comment_1": c1, "comment_2": c2}
        w1.wj(f"{sd}/audit/support_generation.json", res)
        w1.wj(f"{sd}/{'b1_support_texts' if level == 'b1b' else 'a2_support_texts'}.json", {k: v.get("text") for k, v in res.items()})
        kp = sc.run_key_phrases(text, f"{sd}/key_phrases", f"FAMILY_Y_PERSONA_TRIAL_{a.iter}_{level}", level, process=proc, kp_backend="fulltext_p2", stop_run_dir=ed)
        kp_status = (kp["canonicalization"] or {}).get("status") if kp.get("canonicalization") else (kp.get("selection") or {}).get("status")
        w1.wj(f"{sd}/scaffold_summary.json", {"support_status": {k: v.get("status") for k, v in res.items()}, "kp_status": kp_status,
                                              "kp_run_status": kp.get("status"), "comment_3_generated": False, "comment_4_generated": False})
        guard(f"scaffold {level}")
        print(f"[Y-PERSONA][{level}] scaffold完了 kp_status={kp_status}")


# ============================================================
# rf
# ============================================================
def cmd_rf(a):
    import er053_review_queue_01 as rq
    import er053_risk_flagger_production_01 as rf
    rd = f"{ROOT}/{a.iter}"
    ed = f"{rd}/english"
    cl.install(f"{rd}/raw_usage_log_rf.jsonl")
    os.makedirs(f"{ed}/research_ledger", exist_ok=True)
    shutil.copyfile(f"{ROOT}/research_ledger/verified_fact_ledger.txt", f"{ed}/research_ledger/verified_fact_ledger.txt")
    out = {}
    for level in ("b1b", "a2"):
        ap_ = f"{ed}/{level}/article.md"
        try:
            res = rf.run_risk_flagger(article_path=ap_, ledger_path=f"{ed}/research_ledger/verified_fact_ledger.txt", article_id=f"family_y_persona_trial__{a.iter}",
                                      article_level=level, out_dir=ed, producer=None, run_label=f"FAMILY-Y-PERSONA-TRIAL-{a.iter}",
                                      budget_check=lambda: guard(f"rf {level}"))
            saved = rq.save_queue(res, out_dir=ed, root=f"{ed}/review_queue_post_en")
            out[level] = {"status": res["status"], "issue_count": len(res["issues"]), "queue_saved": saved.get("saved"), "rf_run_id": res["rf_run_id"]}
            w1.wj(f"{ed}/rf_{level}_result.json", res)
        except (rf.BudgetCheckStop, rf.ArticleModifiedError):
            raise
        except Exception as exc:  # noqa: BLE001 非Blocking(RF_UNAVAILABLE)
            out[level] = {"status": "RF_UNAVAILABLE", "reason": f"{type(exc).__name__}: {str(exc)[:200]}"}
    w1.wj(f"{ed}/rf_summary.json", out)
    print(f"[Y-PERSONA] RF {out}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("b0", "text", "english", "scaffold", "rf"))
    ap.add_argument("--iter", default="it1")
    ap.add_argument("--judge-model", default=y0.MODEL_CHEAP)
    ap.add_argument("--judge-effort", default="high")
    ap.add_argument("--s3", action="store_true")
    a = ap.parse_args()
    {"b0": cmd_b0, "text": cmd_text, "english": cmd_english, "scaffold": cmd_scaffold, "rf": cmd_rf}[a.cmd](a)


if __name__ == "__main__":
    main()
