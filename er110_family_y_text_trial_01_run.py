# -*- coding: utf-8 -*-
"""er110_family_y_text_trial_01_run.py -- Family Y統合Trial(Phase 1/2テキスト段階)の薄い入口(DEV/Trial専用)。

subcommand(各自1回実行。監督ループ・自動再試行ラッパは持たない。既存artifactがあれば再利用=二重課金防止):
  prep     : Research→Ledger→B3(X共有関数)→注記producer→丸め判断→Y版視点候補→Voice Card
  write    : Y版R0→R1→R2(raw chain、各段保存)
  gate     : 各段にLeakage Check→局所書き換え→Acceptance Gate
  english  : Gate通過原稿ごとに忠実英訳→In One Line→A2簡易化(+S2)→5段落確認→監視Leakage(S3)→(RF)
X runner/X共有関数は呼ぶのみで無変更。run dir は er110_output/family_y_trial_01/<slug>/(X/Z出力dirには書かない)。
"""
import argparse
import hashlib
import json
import os
import re
import sys
import types

import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_advanced_adaptation_generate as adv_gen
import er003_v1_n3_01_standard_a2_generate as std_gen
import er005_cost_logger as cl
import er012_e_family_entertainment_two_level_runner_01 as efam
import er019_family_x_entertainment_production_runner_01 as xr
import er053_b3_annotation_contract_01 as contract
import er053_family_x_factlock_ja_writer_01 as w1
import er095_b3_core_number_rounding_01 as rounding
import er110_family_y_text_trial_01 as y

RUN_DIR = "er110_output/family_y_trial_01/school_phone_ban"
TOPIC = ("学校でスマホを禁止すべきか(学校へのスマートフォン持ち込み・使用制限をめぐる日本と各国の動き。"
         "公的なガイドライン・制度・実施例と、確認できる研究・調査)")
USER_THEME = "学校でスマホを禁止すべき?"
STAGES = ("r0", "r1", "r2")
BUDGET = 215.0     # run dir単位の保険(上限250円から他dir分[M7・Phase3確保]を除いた額)


def _client():
    return vfl01.get_client()


def _load_ctx(run_dir: str) -> dict:
    annotated = contract.validate_annotated_b3(run_dir)
    storyline, facts_text = w1.parse_brief_md(annotated.annotated_md_text)
    overlay, _ev = rounding.load_overlay_for_writer(run_dir, annotated.annotated_md_sha256)
    from er053_b3_deterministic_producer_01 import CONS_HEADING, compose_news_field
    news_text = rounding.news_field_for_writer(annotated.news_field_text, facts_text, annotated.constraints_text, overlay,
                                               CONS_HEADING, compose_news_field)
    facts = w1.parse_annotated_facts(annotated.annotated_md_text)
    return {"annotated": annotated, "storyline": storyline, "facts_text": facts_text, "overlay": overlay, "news_text": news_text, "facts": facts}


def cmd_prep(a):
    rd = a.run_dir
    os.makedirs(rd, exist_ok=True)
    cl.install(f"{rd}/raw_usage_log.jsonl")
    client = _client()
    w1.wj(f"{rd}/entry_point.json", {"runner": "er110_family_y_text_trial_01_run.py", "management_id": y.MANAGEMENT_ID, "topic": TOPIC,
                                      "user_theme": USER_THEME, "started": y.now_iso(), "chain_method": y.CHAIN_METHOD,
                                      "tts_voice_fixed": y.TTS_VOICE_FIXED,
                                      "module_sha256": hashlib.sha256(open("er110_family_y_text_trial_01.py", "rb").read()).hexdigest()})
    led = xr.run_research_and_ledger(client, TOPIC, f"{rd}/research_ledger")
    ledger_text = led["ledger_text"]
    efam.assert_budget_ok(rd, BUDGET, "after research_ledger")
    if not os.path.exists(f"{rd}/storyline_b3/selected_brief.md"):
        xr.run_storyline_b3(client, TOPIC, ledger_text, rd)
        efam.assert_budget_ok(rd, BUDGET, "after storyline_b3")
    xr.assert_b3_min_verified(rd)
    xr.run_annotation_producer(rd)
    xr.run_core_number_rounding(client, rd, ledger_text, types.SimpleNamespace(regenerate_stage=None, budget_jpy=BUDGET), "all")
    ctx = _load_ctx(rd)
    facts = ctx["facts"]
    fact_ids = set(facts)
    ydir = f"{rd}/y_cast"
    # --- 視点候補(Y-B3) ---
    cp = f"{ydir}/cast_candidates.json"
    if not os.path.exists(cp):
        prompt = y.build_cast_prompt(USER_THEME, ctx["storyline"], facts)
        for k in (1, 2):
            resp = y.chat(client, model=y.MODEL_TOP, effort="medium", user=prompt, developer=y.CAST_DEVELOPER, schema=y.CAST_SCHEMA,
                          stage="y_cast" + ("" if k == 1 else "_retry"))
            cast = json.loads(resp.output_text)
            errs = y.validate_cast(cast, fact_ids)
            w1.wj(f"{ydir}/cast_try{k}.json", {"cast": cast, "errors": errs, "meta": y.resp_meta(resp), "prompt_sha256": w1.sha_text(prompt)})
            if not errs:
                break
        else:
            raise y.YStop("CAST_STOP", f"視点候補が2回検証に失敗 {errs}")
        w1.wj(cp, {"cast": cast, "meta": y.resp_meta(resp), "prompt": prompt})
    cast = json.load(open(cp, encoding="utf-8"))["cast"]
    # --- Voice Card ---
    kp = f"{ydir}/voice_cards.json"
    if not os.path.exists(kp):
        prompt = y.build_card_prompt(USER_THEME, cast, facts)
        for k in (1, 2):
            resp = y.chat(client, model=y.MODEL_TOP, effort="medium", user=prompt, developer=y.CAST_DEVELOPER, schema=y.CARD_SCHEMA,
                          stage="y_card" + ("" if k == 1 else "_retry"))
            cards = json.loads(resp.output_text)
            errs = y.validate_cards(cards, fact_ids)
            w1.wj(f"{ydir}/cards_try{k}.json", {"cards": cards, "errors": errs, "meta": y.resp_meta(resp), "prompt_sha256": w1.sha_text(prompt)})
            if not errs:
                break
        else:
            raise y.YStop("CARD_STOP", f"Voice Cardが2回検証に失敗 {errs}")
        cards["not_my_point_deterministic"] = y.derive_not_my_point(cards)
        cards["tts_voice_fixed"] = y.TTS_VOICE_FIXED
        w1.wj(kp, {**cards, "meta": y.resp_meta(resp), "prompt": prompt})
    efam.assert_budget_ok(rd, BUDGET, "after prep")
    print("[Y-TRIAL] prep完了")


def _cards(rd):
    d = json.load(open(f"{rd}/y_cast/voice_cards.json", encoding="utf-8"))
    return {"cards": d["cards"]}


def cmd_write(a):
    rd = a.run_dir
    cl.install(f"{rd}/raw_usage_log.jsonl")
    client = _client()
    ctx = _load_ctx(rd)
    cards = _cards(rd)
    wd = f"{rd}/y_writer"
    r0d = f"{wd}/r0"
    if not os.path.exists(f"{r0d}/r0_final.md"):
        prompt = y.build_y_r0_prompt(ctx["storyline"], ctx["news_text"], cards, ctx["overlay"])
        w1.wt(f"{r0d}/r0_prompt.txt", prompt)
        y.generate_r0(client, prompt=prompt, out_dir=r0d)
        efam.assert_budget_ok(rd, BUDGET, "after r0")
    r0 = w1.rdt(f"{r0d}/r0_final.md")
    r0meta = json.load(open(f"{r0d}/r0_meta.json", encoding="utf-8"))
    mon0 = y.monitors(y.parse_article(r0), r0meta.get("tagged_paragraphs"))
    w1.wj(f"{r0d}/monitors.json", mon0)
    r1d = f"{wd}/r1"
    if not os.path.exists(f"{r1d}/r1_final.md"):
        y.generate_revision(client, src_text=r0, stage="r1", out_dir=r1d)
        efam.assert_budget_ok(rd, BUDGET, "after r1")
    r1raw = w1.rdt(f"{r1d}/r1_raw_try1.md") if os.path.exists(f"{r1d}/r1_raw_try1.md") else None
    r1 = w1.rdt(f"{r1d}/r1_final.md")
    w1.wj(f"{r1d}/monitors.json", y.monitors(y.parse_article(r1)))
    r2d = f"{wd}/r2"
    if not os.path.exists(f"{r2d}/r2_final.md"):
        # R2の入力 = R1の最終稿(Xは生出力。Yは後処理済みの最終稿を渡す=契約確認済みの5段落を保証するため。差分は記録)
        y.generate_revision(client, src_text=r1, stage="r2", out_dir=r2d)
        efam.assert_budget_ok(rd, BUDGET, "after r2")
    r2 = w1.rdt(f"{r2d}/r2_final.md")
    w1.wj(f"{r2d}/monitors.json", y.monitors(y.parse_article(r2)))
    print("[Y-TRIAL] write完了")


def cmd_gate(a):
    rd = a.run_dir
    cl.install(f"{rd}/raw_usage_log.jsonl")
    client = _client()
    ctx = _load_ctx(rd)
    cards = _cards(rd)
    valid_nums = {int(re.sub(r"\D", "", k)) for k in ctx["facts"]}
    for st in (a.stages.split(",") if a.stages else STAGES):
        gd = f"{rd}/y_writer/gate_{st}"
        if os.path.exists(f"{gd}/gate_result.json"):
            print("skip", st)
            continue
        text = w1.rdt(f"{rd}/y_writer/{st}/{st}_final.md")
        parsed = y.parse_article(text)
        try:
            r = y.run_gate(client, stage=f"y_{st}_gate", title=parsed["title"], paragraphs=parsed["paragraphs"], cards_obj=cards, out_dir=gd,
                           judge_model=a.judge_model, judge_effort=a.judge_effort, r0_tags=(st == "r0"),
                           facts_text=ctx["news_text"] if st == "r0" else None, valid_fact_nums=valid_nums)
            print(f"[Y-TRIAL][{st}] gate status={r['status']} judgements={r['n_judgements']}")
        except y.YStop as e:
            print(f"[Y-TRIAL][{st}] STOP {e.code}: {e}")
        efam.assert_budget_ok(rd, BUDGET, f"after gate {st}")


def _std_must_fix_speaker():
    # S2: 『各段落の話者・一人称・迷いの表現を保つ』1文を、既存のmust_fix欄(build_must_fix_block)経由で足す(A2 Prompt本体は無変更)
    return [{"fact_id": "", "claim_in_article": "", "issue": "KEEP_SPEAKER_VOICE",
             "explanation": ("Paragraphs 2, 3 and 4 are spoken by three different people in the first person. In each of those paragraphs, "
                             "keep who is speaking, the first-person 'I' voice, and any hesitation or mixed feeling, even when you simplify the English. "
                             "Do not turn them into a neutral explanation.")}]


def total_cost_jpy(rd: str) -> float:
    """run dir内の全 raw_usage_log*.jsonl(並列実行ではprocessごとに別log)を合算(openai+gemini、fail-closed)。"""
    import glob
    import er053_cost_aggregate_01 as ca
    return round(sum(ca.compute_stage_cost_breakdown_multi(p)["total_jpy"] for p in glob.glob(f"{rd}/raw_usage_log*.jsonl")), 3)


def _budget_guard(rd: str, note: str):
    def _f():
        c = total_cost_jpy(rd)
        if c > BUDGET:
            raise RuntimeError(f"[BUDGET_GUARD] cost so far {c} JPY > cap {BUDGET} JPY ({note})")
    return _f


def cmd_rf(a):
    """Risk Flagger(X既定、非停止)を英語記事に適用し flag件数を記録(S5)。X共有関数 rf.run_risk_flagger を呼ぶのみ。
    **Review Queueは本Trialのdir内**(english_<stage>/review_queue_post_en)へ保存し、X/Zの正式Queue(review_queue/post_en)には書かない。"""
    import shutil
    import er053_review_queue_01 as rq
    import er053_risk_flagger_production_01 as rf
    rd = a.run_dir
    cl.install(f"{rd}/{a.log}")
    for st in a.stages.split(","):
        ed = f"{rd}/english_{st}"
        os.makedirs(f"{ed}/research_ledger", exist_ok=True)
        shutil.copyfile(f"{rd}/research_ledger/verified_fact_ledger.txt", f"{ed}/research_ledger/verified_fact_ledger.txt")
        out = {}
        for level in ("b1b", "a2"):
            ap_ = f"{ed}/{level}/article.md"
            if not os.path.exists(ap_):
                continue
            try:
                res = rf.run_risk_flagger(article_path=ap_, ledger_path=f"{ed}/research_ledger/verified_fact_ledger.txt",
                                          article_id=f"family_y_trial__{st}", article_level=level, out_dir=ed, producer=None,
                                          run_label=f"FAMILY-Y-TRIAL-{st}", budget_check=_budget_guard(rd, f"rf {st} {level}"))
                saved = rq.save_queue(res, out_dir=ed, root=f"{ed}/review_queue_post_en")
                out[level] = {"status": res["status"], "issue_count": len(res["issues"]), "queue_saved": saved.get("saved"),
                              "rf_run_id": res["rf_run_id"]}
                w1.wj(f"{ed}/rf_{level}_result.json", res)
            except (rf.BudgetCheckStop, rf.ArticleModifiedError):
                raise
            except Exception as exc:  # noqa: BLE001 非Blocking(RF_UNAVAILABLE)
                out[level] = {"status": "RF_UNAVAILABLE", "reason": f"{type(exc).__name__}: {str(exc)[:200]}"}
        w1.wj(f"{ed}/rf_summary.json", out)
        print(f"[Y-TRIAL][{st}] RF {out}")


def cmd_scaffold(a):
    """学習支援構造(Comment1〜3/Preview/KP/日本語タイトル)を既存scaffold部品で生成。Comment 4は生成しない。X部品は呼ぶのみ。"""
    import er003_v1_b1_scaffold_01_generate as b1s
    import er003_v1_iran01_a2_generate as a2gen
    import er003_v1_n3_01_scaffold_generate as sc
    import er019_family_x_audio_production_runner_01 as ar
    rd = a.run_dir
    cl.install(f"{rd}/{a.log}")
    client = _client()
    for st in a.stages.split(","):
        ed = f"{rd}/english_{st}"
        ja_title = y.parse_article(w1.rdt(f"{rd}/y_writer/gate_{st}/article_final.md"))["title"]
        w1.wj(f"{ed}/japanese_title.json", {"japanese_title": ja_title, "source": f"y_writer/gate_{st}/article_final.md(LLM 0 call)"})
        for level, gen, mfn, proc in (("b1b", b1s, ar._b1_support_model, "B1_SUPPORT"), ("a2", a2gen, ar._a2_support_model, "A2_SUPPORT")):
            sd = f"{ed}/scaffold_{level}"
            if os.path.exists(f"{sd}/scaffold_summary.json"):
                print("skip", st, level)
                continue
            text = w1.rdt(f"{ed}/{level}/article.md")
            sp = y.split_en_article(text)
            P = sp["paragraphs"]
            assert len(P) == 5
            first_sentences = "\n".join("- " + re.split(r"(?<=[.!?])\s", p)[0] for p in P[1:4])
            c1 = gen.run_support_text(client, gen.COMMENT_1_ROLE, "【これから聞く本文(導入)】\n" + P[0], model=mfn())
            c2 = gen.run_support_text(client, y.Y_COMMENT_2_ROLE[level],
                                      "【すでに聞いた導入】\n" + P[0] + "\n\n【これから聞く3人の語り(それぞれの冒頭の1文のみ)】\n" + first_sentences, model=mfn())
            c3 = gen.run_support_text(client, y.Y_COMMENT_3_ROLE[level],
                                      "【導入】\n" + P[0] + "\n\n" + "\n\n".join(f"【人物{i}の語り】\n{P[i]}" for i in (1, 2, 3)), model=mfn())
            prev_role = gen.PREVIEW_ROLE.format(comment_1=c1.get("text") or "(生成失敗)", comment_2=c2.get("text") or "(生成失敗)")
            prev = gen.run_support_text(client, prev_role, "【エピソード全文(参考、新しいFactの追加禁止)】\n# " + sp["title"] + "\n\n" + "\n\n".join(P), model=mfn())
            res = {"preview": prev, "comment_1": c1, "comment_2": c2, "comment_3": c3}
            w1.wj(f"{sd}/audit/support_generation.json", res)
            w1.wj(f"{sd}/{'b1_support_texts' if level == 'b1b' else 'a2_support_texts'}.json", {k: v.get("text") for k, v in res.items()})
            kp = sc.run_key_phrases(text, f"{sd}/key_phrases", f"FAMILY_Y_TRIAL_{st}_{level}", level, process=proc, kp_backend="fulltext_p2", stop_run_dir=ed)
            kp_status = (kp["canonicalization"] or {}).get("status") if kp.get("canonicalization") else (kp.get("selection") or {}).get("status")
            w1.wj(f"{sd}/scaffold_summary.json", {"support_status": {k: v.get("status") for k, v in res.items()}, "kp_status": kp_status,
                                                  "kp_run_status": kp.get("status"), "comment_4_generated": False})
            _budget_guard(rd, f"scaffold {st} {level}")()
            print(f"[Y-TRIAL][{st}][{level}] scaffold完了 kp_status={kp_status}")


def cmd_ablation(a):
    """対策の強さの評価用(記録専用の比較アーム。採用候補にはしない): 
    A0=対策弱化(5段落+一人称+話し言葉だけ。数字禁止/not_my_point/世界スコープ規則/Fact Lockなし)、
    A1=Voice背景factを0件にしたこと以外は通常のY版R0(世界のことにはVoiceでふれない)。"""
    rd = a.run_dir
    cl.install(f"{rd}/{a.log}")
    client = _client()
    ctx = _load_ctx(rd)
    cards = _cards(rd)
    # --- A0 ---
    d0 = f"{rd}/y_writer/ablation_a0_light"
    if not os.path.exists(f"{d0}/r0_final.md"):
        prompt = y.build_y_r0_light_prompt(ctx["storyline"], ctx["news_text"], cards)
        w1.wt(f"{d0}/r0_prompt.txt", prompt)
        y.generate_r0(client, prompt=prompt, out_dir=d0)
    t0 = w1.rdt(f"{d0}/r0_final.md")
    p0 = y.parse_article(t0)
    chk0 = y.run_leakage_check(client, y.sections_from_paragraphs(p0["paragraphs"]), model=a.judge_model, effort=a.judge_effort, stage="y_a0_leak")
    w1.wj(f"{d0}/leak_check_raw.json", chk0)
    w1.wj(f"{d0}/monitors.json", y.monitors(p0))
    # --- A1 ---
    d1 = f"{rd}/y_writer/ablation_a1_nofact"
    cards_nf = {"cards": [{**c, "background_fact_ids": []} for c in cards["cards"]]}
    if not os.path.exists(f"{d1}/r0_final.md"):
        prompt = y.build_y_r0_prompt(ctx["storyline"], ctx["news_text"], cards_nf, ctx["overlay"])
        w1.wt(f"{d1}/r0_prompt.txt", prompt)
        y.generate_r0(client, prompt=prompt, out_dir=d1)
    t1 = w1.rdt(f"{d1}/r0_final.md")
    p1 = y.parse_article(t1)
    w1.wj(f"{d1}/monitors.json", y.monitors(p1))
    valid_nums = {int(re.sub(r"\D", "", k)) for k in ctx["facts"]}
    if not os.path.exists(f"{d1}/gate/gate_result.json"):
        try:
            r = y.run_gate(client, stage="y_a1_gate", title=p1["title"], paragraphs=p1["paragraphs"], cards_obj=cards_nf, out_dir=f"{d1}/gate",
                           judge_model=a.judge_model, judge_effort=a.judge_effort, r0_tags=True, facts_text=ctx["news_text"], valid_fact_nums=valid_nums)
            print(f"[Y-TRIAL][a1] gate status={r['status']} judgements={r['n_judgements']}")
        except y.YStop as e:
            print(f"[Y-TRIAL][a1] STOP {e.code}: {e}")
    _budget_guard(rd, "after ablation")()


def cmd_english(a):
    rd = a.run_dir
    cl.install(f"{rd}/{a.log}")
    client = _client()
    ledger_text = w1.rdt(f"{rd}/research_ledger/verified_fact_ledger.txt")
    for st in a.stages.split(","):
        ed = f"{rd}/english_{st}"
        if os.path.exists(f"{ed}/en_summary.json"):
            print("skip", st)
            continue
        ja = w1.rdt(f"{rd}/y_writer/gate_{st}/article_final.md")
        # 忠実英訳(Advanced)
        r = adv_gen.generate_family_x_faithful_translation(ja, client=client)
        title, body = r.title, r.body
        iol = efam._advanced_in_one_line(client, title, body, ja, ledger_text)
        adv_text = f"# {title}\n\n{body}\n\n## In one line\n{iol['text']}"
        c = y.check_en_contract(adv_text)
        retried_adv = False
        if not c["ok"] and any("PARAGRAPH_COUNT" in v for v in c["violations"]):
            retried_adv = True
            r = adv_gen.generate_family_x_faithful_translation(ja, client=client, must_fix=efam._FAMILY_X_PARAGRAPH_RETRY_MUST_FIX)
            title, body = r.title, r.body
            iol = efam._advanced_in_one_line(client, title, body, ja, ledger_text)
            adv_text = f"# {title}\n\n{body}\n\n## In one line\n{iol['text']}"
            c = y.check_en_contract(adv_text)
        w1.wt(f"{ed}/b1b/article.md", adv_text)
        w1.wj(f"{ed}/b1b/contract.json", {"retried": retried_adv, **{k: v for k, v in c.items() if k != "split"}})
        if not c["ok"]:
            w1.wj(f"{ed}/en_summary.json", {"status": "ADV_CONTRACT_STOP", "violations": c["violations"]})
            print(f"[Y-TRIAL][{st}] Advanced 契約違反 {c['violations']}")
            continue
        # Standard(X既定)と S2(話者保持1文追加)の2通り
        variants = {"x": None}
        if a.s2 and st == a.s2_stage:
            variants["s2"] = _std_must_fix_speaker()
        for name, mf in variants.items():
            s = std_gen.generate_family_x_standard_a2_no_heading(adv_text, client=client, must_fix=mf)
            std_text = s.text
            cs = y.check_en_contract(std_text)
            retried = False
            if not cs["ok"] and any("PARAGRAPH_COUNT" in v for v in cs["violations"]):
                retried = True
                s = std_gen.generate_family_x_standard_a2_no_heading(adv_text, client=client,
                                                                     must_fix=(mf or []) + efam._FAMILY_X_PARAGRAPH_RETRY_MUST_FIX)
                std_text = s.text
                cs = y.check_en_contract(std_text)
            sub = "a2" if name == "x" else "a2_s2"
            w1.wt(f"{ed}/{sub}/article.md", std_text)
            w1.wj(f"{ed}/{sub}/contract.json", {"retried": retried, **{k: v for k, v in cs.items() if k != "split"}})
        # 監視モニタ(記録専用)+ S3 監視専用Leakage(Std英語、Gateにしない)
        mon = {"b1b": y.en_monitors(adv_text)}
        for sub in [d for d in ("a2", "a2_s2") if os.path.exists(f"{ed}/{d}/article.md")]:
            mon[sub] = y.en_monitors(w1.rdt(f"{ed}/{sub}/article.md"))
        w1.wj(f"{ed}/en_monitors.json", mon)
        s3 = {}
        if a.s3:
            for sub in [d for d in ("a2",) if os.path.exists(f"{ed}/{d}/article.md")]:
                sp = y.split_en_article(w1.rdt(f"{ed}/{sub}/article.md"))
                if len(sp["paragraphs"]) == 5:
                    chk = y.run_leakage_check(client, y.sections_from_paragraphs(sp["paragraphs"]), model=a.s3_model, effort=a.s3_effort,
                                              stage=f"y_{st}_s3_leak_{sub}", language_note="英語")
                    s3[sub] = {k: v for k, v in chk.items() if k != "parsed"}
                    s3[sub]["parsed"] = chk["parsed"]
        w1.wj(f"{ed}/s3_monitor_leakage.json", s3)
        w1.wj(f"{ed}/en_summary.json", {"status": "OK", "ja_sha256": w1.sha_text(ja), "adv_sha256": w1.sha_text(adv_text)})
        _budget_guard(rd, f"after english {st}")()
        print(f"[Y-TRIAL][{st}] english完了")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("prep", "write", "gate", "english", "rf", "scaffold", "ablation"))
    ap.add_argument("--run-dir", default=RUN_DIR)
    ap.add_argument("--stages", default="")
    ap.add_argument("--log", default="raw_usage_log.jsonl", help="並列実行時はprocessごとに別名(例 raw_usage_log_en_r0.jsonl)。集計は全logの合算")
    ap.add_argument("--judge-model", default=y.MODEL_TOP)
    ap.add_argument("--judge-effort", default="medium")
    ap.add_argument("--s2", action="store_true")
    ap.add_argument("--s2-stage", default="r2")
    ap.add_argument("--s3", action="store_true")
    ap.add_argument("--s3-model", default=y.MODEL_CHEAP)
    ap.add_argument("--s3-effort", default="high")
    a = ap.parse_args()
    {"prep": cmd_prep, "write": cmd_write, "gate": cmd_gate, "english": cmd_english, "rf": cmd_rf, "scaffold": cmd_scaffold, "ablation": cmd_ablation}[a.cmd](a)


if __name__ == "__main__":
    main()
