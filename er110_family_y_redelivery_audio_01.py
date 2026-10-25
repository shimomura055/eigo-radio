# -*- coding: utf-8 -*-
"""er110_family_y_redelivery_audio_01.py
FAMILY-Y-VOICES-DESIGN-01 委任_27: 『宅配の再配達は有料にすべきか?』音声化Trial(DEV/Trial専用の薄いglue)。

位置づけ(重要):
  - **Family YのDEV/Trial経路**。どのProduction runner・.env・起動scriptからも参照されない(testでGrep固定)。import時にAPI呼出0・ファイル副作用0。
    環境変数・flagでProduction挙動が変わる経路はない。`production_reachable=False`(Y正式Production入口は存在しない=OPEN-484)。
  - **新しい処理flow・Validator・組立方式・Voice選定方式・Styleは作らない**。次の既存部品を呼ぶだけ:
      日本語R0(委任_25、無変更・再生成しない) + リード/Tension+Closing(5パート契約=er110_family_y_text_trial_01のY_R0_HEAD仕様、
      Tension+Closingは er110_family_y_persona_text_trial_01 の生成・Leakage Gate部品) → 忠実英訳/A2簡易化(Family X承認済み関数)
      → Comment1〜3/Preview/KP(er110_family_y_text_trial_01_run.cmd_scaffold = 既存5パート版) → 音声(er110_family_y_audio_trial_01 = 既存5パート版、
      固定Voice Algieba/Zephyr/Schedar + ナレーターAoede) → 試聴ページ(er110_family_y_audio_page_01の部品)。
  - 追加するのはデータ(テーマ固有のラベル・主張の要点・共通前提)と、出力先の差替え(process内、finallyで復元)だけ。
  - **有料runは予算承認ファイル(`ROOT/BUDGET_APPROVED.json`)と明示 `--paid` が無い限り起動しない**。承認ファイルは委任文の承認に基づきPhase 1開始時に作成する。
"""
from __future__ import annotations

import argparse
import contextlib
import glob
import hashlib
import json
import os
import re
import sys
import unicodedata

import er053_family_x_factlock_ja_writer_01 as w1
import er110_family_y_text_trial_01 as y0
import er110_family_y_persona_text_trial_01 as p

MANAGEMENT_ID = "FAMILY-Y-VOICES-DESIGN-01"
THEME_TAG = "FAMILY_Y_REDELIVERY_AUDIO_01"
ROOT = "er110_output/family_y_redelivery_audio_01"
RD = f"{ROOT}/redelivery_fee"
AUDIO_ROOT = f"{ROOT}/audio"
SRC_R0 = "er110_output/family_y_opinion_based_03/redelivery_fee/run_01"          # 日本語R0(読取りのみ・再生成しない)
SOURCES_DIR = "docs/research/FAMILY-Y-VOICES-DESIGN-01/OPINION_BASED_02/sources"  # 出典本文(権利照合のみに使用)
APPROVAL_FILE = f"{ROOT}/BUDGET_APPROVED.json"
CAND = "r0"                                                                         # 既存5パート版音声moduleのcandidate名(1候補)
TEXT_CAP_JPY = 20.0                                                                 # 本run dir(テキスト+scaffold)の保険。音声は別Cap(--budget-jpy 35)
WEB_DIR = "user_test/family_y_redelivery_audio_01"

TITLE_JA = "宅配の再配達、それぞれの声"
DISCLOSURE_JA = "これから聞くのは、実在の特定の人の話ではない。ネットなどで公開されている複数の意見をもとに、組み立てた声だ。"
PREMISE_JA = "宅配便の再配達に、通常の配送料とは別に、受け取る人が料金を払う仕組みにするかどうか。"
SLOTS = ("voice_1", "voice_2", "voice_3")
# 人物ラベル・主張の要点・対比の具体物(PERSONAS_05 §1・R0本文に出てきた語のみ。新しい事実・人物像を足さない)
SHEETS_R = {
    "voice_1": {"label": "現役の宅配ドライバー(男性・私)", "claim": "きついのは本当。でも、お客さんから料金を取って片づく話ではなく、会社や料金全体の側で考えることだと思う。",
                "tension_object": "不在票を入れて、そのまま次の家へ向かうとき"},
    "voice_2": {"label": "共働きで家を空ける時間が長い受取人(女性・わたし)", "claim": "有料にする前に、指定した時間に来ることと、届く日時を知らせることが先。",
                "tension_object": "午前を指定したのに来なくて、戻ったら入っていた不在票"},
    "voice_3": {"label": "営業所やロッカーで受け取る工夫をしている受取人(男性・僕)", "claim": "手間をかけている側として、くり返し頼む人と同じ料金はおかしい。有料でいい。ただ、受け取り方を選べる自分の言い分かもしれない。",
                "tension_object": "営業所やロッカーで受け取る手間"},
}
# Voice割当の根拠: Family Z正式表(er062 assign_dialogue_voices、男女独立・登場順)の結果が、ユーザー決定の固定割当(#163 D3)と一致する
ROSTER = (
    {"speaker": "voice_1", "gender": "male", "order": 1, "first_appearance": "One Voice(私・現役の宅配ドライバー)"},
    {"speaker": "voice_2", "gender": "female", "order": 2, "first_appearance": "Another Voice(わたし・共働きの受取人)"},
    {"speaker": "voice_3", "gender": "male", "order": 3, "first_appearance": "A Third Voice(僕・受け取り方を工夫する受取人)"},
)
EXPECTED_VOICES = {"voice_1": "Algieba", "voice_2": "Zephyr", "voice_3": "Schedar"}
# 日本語・Adv・Stdの5パート対応確認用の話者アンカー(各人物の本文に出る語。決定論の記録用で、Gateにしない)
ANCHORS = {
    "voice_1": {"ja": r"(不在票|料金全体|送料|運ぶ人|配る人|荷物を運ぶ)", "en": r"(notice|slip|delivering|deliver|shipping|drivers?|carry|carrying)"},
    "voice_2": {"ja": r"(午前|夫|指定した|指定できる|届く日時|わたし)", "en": r"(morning|husband|specif|time slot|window|arriv)"},
    "voice_3": {"ja": r"(営業所|ロッカー|僕|最初の再配達)", "en": r"(locker|pick ?up|pickup|depot|branch|office|collect|first)"},
}
FIRST_PERSON_JA = {"voice_1": "私", "voice_2": "わたし", "voice_3": "僕"}


# ============================================================
# 予算承認・停止(有料runの入口)
# ============================================================
def read_cap(path: str) -> dict:
    """承認ファイルを読む。既定引数に実pathを固定しない(過去事故[FYT17]の再発防止)。"""
    if not os.path.exists(path):
        raise RuntimeError(f"[NO_APPROVAL] {path} がありません。有料runは起動しません")
    d = json.load(open(path, encoding="utf-8"))
    if not isinstance(d.get("cap_jpy"), (int, float)) or d["cap_jpy"] <= 0:
        raise RuntimeError("[BAD_APPROVAL] cap_jpyが不正")
    return d


def require_paid(paid_flag: bool, approval_path: str = None) -> dict:
    if not paid_flag:
        raise RuntimeError("[NO_PAID_FLAG] --paid が無いため有料runを起動しません")
    return read_cap(approval_path or APPROVAL_FILE)


def total_cost_jpy(rd: str) -> float:
    import er053_cost_aggregate_01 as ca
    return round(sum(ca.compute_stage_cost_breakdown_multi(f)["total_jpy"] for f in glob.glob(f"{rd}/**/raw_usage_log*.jsonl", recursive=True)), 3)


def guard(note: str, cap: float):
    c = total_cost_jpy(RD)
    if c > cap:
        raise RuntimeError(f"[BUDGET_GUARD] cost so far {c} JPY > cap {cap} JPY ({note})")
    print(f"[Y-REDELIVERY] cost so far {c} JPY ({note})")


def other_tts_processes() -> list:
    """他agentのTTS/音声生成processの有無(直列化の確認用。終了はしない)。python processのcommand lineにtts/audio/e2e/production系語を含むものを列挙。"""
    import subprocess
    try:
        out = subprocess.run(["powershell", "-NoProfile", "-Command",
                              "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | ForEach-Object { \"$($_.ProcessId)`t$($_.CommandLine)\" }"],
                             capture_output=True, text=True, timeout=30).stdout
    except Exception as e:  # noqa: BLE001
        return [f"PROCESS_LIST_UNAVAILABLE:{e!r}"]
    me = str(os.getpid())
    hits = []
    for ln in out.splitlines():
        if not ln.strip() or ln.split("\t")[0] == me:
            continue
        if re.search(r"(tts|audio|e2e|production_runner|run_e2e|run_sf_prod|chunk)", ln, re.I) and "er110_family_y_redelivery" not in ln:
            hits.append(ln.strip()[:300])
    return hits


# ============================================================
# 日本語5パート原稿(R0を無変更で使い、リードとTension+Closingだけ補完)
# ============================================================
def parse_r0(path: str) -> dict:
    txt = open(path, encoding="utf-8").read()
    blocks = [b.strip() for b in re.split(r"\n\s*\n", txt.strip()) if b.strip()]
    # 期待: '# title', 開示文, '## One Voice', V1, '## Another Voice', V2, '## A Third Voice', V3
    if len(blocks) != 8 or not blocks[0].startswith("# "):
        raise RuntimeError(f"R0の形が想定と違います(blocks={len(blocks)})")
    heads = [blocks[2], blocks[4], blocks[6]]
    if heads != ["## One Voice", "## Another Voice", "## A Third Voice"]:
        raise RuntimeError(f"R0の見出し順が想定と違います: {heads}")
    return {"title": blocks[0][2:].strip(), "disclosure": blocks[1], "voice_1": blocks[3], "voice_2": blocks[5], "voice_3": blocks[7]}


def load_r0() -> dict:
    r0 = parse_r0(f"{SRC_R0}/article_ja.md")
    gate = json.load(open(f"{SRC_R0}/gate_voices/gate_result.json", encoding="utf-8"))
    final = json.load(open(f"{SRC_R0}/gate_voices/final_texts.json", encoding="utf-8"))
    if gate.get("status") != "PASS":
        raise RuntimeError("R0 Leakage Gateが PASS ではありません")
    for s in SLOTS:
        if final[s].strip() != r0[s].strip():
            raise RuntimeError(f"R0本文とgate最終本文が一致しません: {s}")
    if r0["title"] != TITLE_JA or r0["disclosure"] != DISCLOSURE_JA:
        raise RuntimeError("R0のタイトル/開示文が定数と一致しません")
    return r0


def lead_spec_from_y0() -> str:
    """5パート契約のリード仕様を旧Y版R0 Promptから逐語抽出(複製しない)。"""
    m = re.search(r"・1段落目 リード\(語り手の声、約110字\):.*", y0.Y_R0_HEAD)
    if not m:
        raise RuntimeError("Y_R0_HEADにリード仕様が見つかりません")
    return m.group(0).strip()


LEAD_DEVELOPER = "あなたは日本語のラジオ読み物の語り手(ナレーター)です。これから三人の声を聞く人に向けて、短い導入を話し言葉で語ります。"
LEAD_PROMPT_TMPL = """次のテーマで、読み物の最初の1段落(リード)だけを書いてください。

【テーマ】@@PREMISE@@
(話題の問い: 宅配の再配達は有料にすべきか。再配達=受取人の不在などで荷物を渡せず、配達員があらためて届けに行くこと)

【リードの仕様(5パート構成の1段落目)】
@@SPEC@@

【書き方】
- 語り手(ナレーター)の声。一人称(私・俺・僕・わたし)は使わない。話し言葉の常体(「〜だ」「〜だよね」など)。「です・ます」調にしない。
- 約70〜100字、1段落、2〜3文。最後の文で「ここに、立場も暮らしも違う3人の声を並べる」という予告をする(この段落の後に『これから聞くのは、実在の特定の人の話ではない』という開示文が続くので、その言い方は繰り返さない)。
- 3人の立場・結論・職業の詳細は書かない。数字・企業名・制度名は入れない。新しい事実や出来事を作らない。
- 括弧・コロン・スラッシュ・三点リーダー・波ダッシュ・絵文字を使わない。

出力はリードの本文のみ(見出し・ラベルなし)。"""


def build_lead_prompt() -> str:
    return LEAD_PROMPT_TMPL.replace("@@PREMISE@@", PREMISE_JA).replace("@@SPEC@@", lead_spec_from_y0())


def check_lead(text: str) -> dict:
    v = []
    t = (text or "").strip()
    if not t:
        v.append("EMPTY")
    if "\n" in t:
        v.append("MULTI_PARAGRAPH")
    if y0.FIRST_PERSON_RE.search(t):
        v.append("HAS_FIRST_PERSON")
    if y0.LEAD_BAD_RE.search(t):
        v.append("HAS_INTERVIEWER_EXPRESSION")
    if y0.LABEL_START_RE.match(t):
        v.append("LABEL_AT_START")
    if re.search(r"[0-9０-９]", t):
        v.append("HAS_DIGIT")
    if y0.DESU_MASU_RE.search(t):
        v.append("DESU_MASU")
    if not (40 <= len(t) <= 130):
        v.append(f"LENGTH={len(t)}")
    return {"ok": not v, "violations": v}


def generate_lead(client, *, out_dir: str, model: str = None, effort: str = "high") -> dict:
    import er003_audio_tts_asr_safety as safety
    model = model or y0.MODEL_TOP
    os.makedirs(out_dir, exist_ok=True)
    prompt = build_lead_prompt()
    w1.wt(os.path.join(out_dir, "lead_prompt.txt"), prompt)
    calls, hist, cur = [], [], prompt
    for k in (1, 2):
        resp = y0.chat(client, model=model, effort=effort, user=cur, developer=LEAD_DEVELOPER, stage="yr_lead" + ("" if k == 1 else "_regen"))
        raw = resp.output_text.strip()
        calls.append({**y0.resp_meta(resp), "prompt_sha256": w1.sha_text(cur)})
        w1.wt(os.path.join(out_dir, f"lead_raw_try{k}.txt"), raw)
        probs = []
        try:
            final, sym = p._fin(raw)
            probs += check_lead(final)["violations"]
            if safety.symbol_gate_requires_stop(sym):
                probs.append(f"SYMBOL:{sym}")
        except w1.TagLeak as e:
            final, probs = "", [f"TAG_LEAK:{e}"]
        hist.append(probs)
        if not probs:
            w1.wt(os.path.join(out_dir, "lead.txt"), final + "\n")
            w1.wj(os.path.join(out_dir, "lead_meta.json"), {"calls": calls, "problems_per_try": hist, "sha256": w1.sha_text(final)})
            return {"text": final}
        if k == 1:
            cur = prompt + "\n\n【前回の出力の問題(今回は避けてください)】\n" + "\n".join(f"- {x}" for x in probs)
    raise y0.YStop("LEAD_CONTRACT_STOP", f"lead: 再生成後も契約違反 {hist[-1]}", hist)


@contextlib.contextmanager
def patched_persona_module():
    """persona moduleのTension生成/書き換えPromptが読む共通前提・規則を、process内だけ今回テーマへ差替える(finallyで復元。ファイルは変更しない)。"""
    old_example = "あなたの家では、夜、スマホはどこに置いてある?"
    if old_example not in p.TENSION_RULES:
        raise RuntimeError("persona TENSION_RULESの例文が想定と違います")
    prev = (p.COMMON_PREMISE_JA, p.TENSION_RULES, y0.THEME_TAG)
    p.COMMON_PREMISE_JA = PREMISE_JA
    p.TENSION_RULES = p.TENSION_RULES.replace(old_example, "あなたは、荷物が届くはずの日、どこで待っている?")
    y0.THEME_TAG = THEME_TAG
    try:
        yield
    finally:
        p.COMMON_PREMISE_JA, p.TENSION_RULES, y0.THEME_TAG = prev


def assemble_ja(lead_body: str, r0: dict, tension: str) -> str:
    """5パートの日本語原稿(タイトル1行+空行+5段落)。リード=生成文+開示文(R0に既にある文を逐語で後置)。"""
    lead = lead_body.strip() + r0["disclosure"]
    paras = [lead, r0["voice_1"], r0["voice_2"], r0["voice_3"], tension.strip()]
    return y0.render_article(r0["title"], paras)


def cmd_ja(a):
    import er005_cost_logger as cl
    import er003_v1_en_direct_vfl_01_generate as vfl01
    cap = min(require_paid(a.paid)["cap_jpy"], TEXT_CAP_JPY)
    os.makedirs(RD, exist_ok=True)
    cl.install(f"{RD}/raw_usage_log.jsonl")
    client = vfl01.get_client()
    r0 = load_r0()
    voices = {s: r0[s] for s in SLOTS}
    w1.wj(f"{RD}/entry_point.json", {"runner": "er110_family_y_redelivery_audio_01.py", "management_id": MANAGEMENT_ID, "src_r0": SRC_R0,
                                      "production_reachable": False, "writer_model": y0.MODEL_TOP, "judge_model": y0.MODEL_CHEAP,
                                      "module_sha256": hashlib.sha256(open("er110_family_y_redelivery_audio_01.py", "rb").read()).hexdigest()})
    with patched_persona_module():
        ld = f"{RD}/lead"
        if not os.path.exists(f"{ld}/lead.txt"):
            generate_lead(client, out_dir=ld)
            guard("after lead", cap)
        lead = w1.rdt(f"{ld}/lead.txt").strip()
        td = f"{RD}/tension"
        if not os.path.exists(f"{td}/tension.txt"):
            p.generate_tension(client, voices, out_dir=td, sheets=SHEETS_R)
            guard("after tension", cap)
        tension = w1.rdt(f"{td}/tension.txt").strip()
        gt = f"{RD}/gate_tension"
        if not os.path.exists(f"{gt}/gate_result.json"):
            r = p.run_gate(client, kind="tension", stage="yr_tension_gate", texts={"tension": tension}, out_dir=gt, voices_ctx=voices,
                           judge_model=y0.MODEL_CHEAP, judge_effort="high")
            print(f"[Y-REDELIVERY] tension gate status={r['status']} judgements={r['n_judgements']}")
            guard("after tension gate", cap)
        tension_g = p.load_gated_or_stop(gt)["tension"]
    ja = assemble_ja(lead, r0, tension_g)
    c = y0.check_contract(y0.parse_article(ja))
    if not c["ok"]:
        raise y0.YStop("JA_CONTRACT_STOP", str(c["violations"]))
    gd = f"{RD}/y_writer/gate_r0"
    w1.wt(f"{gd}/article_final.md", ja)
    w1.wj(f"{gd}/gate_result.json", {"status": "PASS", "components": {
        "voices": {"source": f"{SRC_R0}/gate_voices/gate_result.json", "status": "PASS", "note": "R0確定本文は無変更(sha一致確認済み)"},
        "tension": {"source": f"{gt}/gate_result.json", "status": "PASS"},
        "lead": {"checks": check_lead(lead), "note": "決定論の契約確認のみ(リードにはLeakage項目なし=既存仕様)"}}})
    w1.wj(f"{RD}/monitors_ja.json", {"tension": p.tension_monitors(tension_g), "lead": {"chars": len(lead), "check": check_lead(lead)}})
    guard("after ja", cap)
    print("[Y-REDELIVERY] ja完了")


# ============================================================
# 5パート対応確認(日本語/Adv/Std。決定論、記録用でGateにしない)
# ============================================================
def mapping_check(ja_paras: list, en_paras: dict) -> dict:
    """ja_paras: 日本語5段落。en_paras: {'adv': [5段落], 'std': [5段落]}。各言語で: 5段落/段落2〜4の一人称/段落1,5のナレーター/話者アンカーが自分の段落に出る。"""
    rows, ok = [], True
    langs = {"ja": ja_paras, **en_paras}
    for lang, ps in langs.items():
        r = {"lang": lang, "n_paragraphs": len(ps), "checks": []}
        if len(ps) != 5:
            r["checks"].append({"check": "PARAGRAPH_COUNT", "ok": False, "detail": len(ps)})
            ok = False
            rows.append(r)
            continue
        for i, s in enumerate(SLOTS, start=1):
            txt = ps[i]
            if lang == "ja":
                fp = FIRST_PERSON_JA[s] in txt
                own = bool(re.search(ANCHORS[s]["ja"], txt))
            else:
                fp = bool(re.search(r"\b(I|I'm|I've|my|me|myself)\b", txt, re.I))
                own = bool(re.search(ANCHORS[s]["en"], txt, re.I))
            r["checks"].append({"check": f"para{i + 1}_{s}", "first_person": fp, "own_anchor": own, "ok": fp and own})
            ok = ok and fp and own
        for i in (0, 4):
            narr_fp = bool(y0.FIRST_PERSON_RE.match(ps[i][:4])) if lang == "ja" else bool(re.match(r"^(I|I'm|I've|My|Me)\b", ps[i]))
            r["checks"].append({"check": f"para{i + 1}_narrator", "starts_with_first_person": narr_fp, "ok": not narr_fp})
            ok = ok and not narr_fp
        rows.append(r)
    return {"ok": ok, "rows": rows}


# ============================================================
# 権利確認(出典との連続一致。機械チェック)
# ============================================================
def _norm_ja(s: str) -> str:
    s = unicodedata.normalize("NFKC", s)
    return re.sub(r"[\s　「」『』、。，．,.！？!?…・\-ー〜~()（）\[\]【】]", "", s)


def _norm_en(s: str) -> list:
    return re.findall(r"[a-z0-9']+", unicodedata.normalize("NFKC", s).lower())


def shingle_hits_ja(text: str, src_texts: dict, n: int = 20) -> list:
    b = _norm_ja("\n".join(l for l in text.splitlines() if not l.startswith("#")))
    sh = {b[i:i + n] for i in range(len(b) - n + 1)}
    hits = []
    for path, t in src_texts.items():
        nt = _norm_ja(t)
        for k in sh:
            if k in nt:
                hits.append({"source": path, "shingle": k})
                break
    return hits


def shingle_hits_en(text: str, src_texts: dict, n: int = 8) -> list:
    w = _norm_en(text)
    sh = {" ".join(w[i:i + n]) for i in range(len(w) - n + 1)}
    hits = []
    for path, t in src_texts.items():
        nt = " ".join(_norm_en(t))
        for k in sh:
            if k in nt:
                hits.append({"source": path, "shingle": k})
                break
    return hits


def load_sources(src_dir: str = SOURCES_DIR) -> dict:
    out = {}
    for pth in glob.glob(src_dir + "/**/*", recursive=True):
        if os.path.isfile(pth):
            try:
                out[pth] = open(pth, encoding="utf-8", errors="ignore").read()
            except OSError:
                pass
    return out


def cmd_rights(a):
    srcs = load_sources()
    res = {"n_source_files": len(srcs), "checks": []}
    cands = [("ja_article_final", f"{RD}/y_writer/gate_r0/article_final.md", "ja"), ("ja_r0_run01", f"{SRC_R0}/article_ja.md", "ja")]
    for lvl in ("b1b", "a2"):
        cands.append((f"en_{lvl}_article", f"{RD}/english_r0/{lvl}/article.md", "en"))
    for lvl, nm in (("b1b", "b1_support_texts.json"), ("a2", "a2_support_texts.json")):
        cands.append((f"en_{lvl}_support", f"{RD}/english_r0/scaffold_{lvl}/{nm}", "en"))
    for name, path, lang in cands:
        if not os.path.exists(path):
            res["checks"].append({"name": name, "path": path, "skipped": "not_found"})
            continue
        t = open(path, encoding="utf-8").read()
        hits = shingle_hits_ja(t, srcs, 20) if lang == "ja" else shingle_hits_en(t, srcs, 8)
        res["checks"].append({"name": name, "path": path, "rule": "ja 20字以上" if lang == "ja" else "en 8語以上", "hits": len(hits), "detail": hits[:3]})
    res["all_zero"] = all(c.get("hits", 0) == 0 for c in res["checks"] if "hits" in c)
    w1.wj(a.out, res)
    print(json.dumps({"all_zero": res["all_zero"], "checks": [(c["name"], c.get("hits", c.get("skipped"))) for c in res["checks"]]}, ensure_ascii=False))


# ============================================================
# 英語(Family X承認済み関数: 忠実英訳→In One Line→A2簡易化)
# ============================================================
def y5_contrast_must_fix() -> list:
    """persona版 y_contrast_must_fix(OF-Y3-01(b)、Opus確認済み)の5パート版。段落番号のみ差替え。X関数・A2 Prompt本体は無変更(must_fix欄経由)。"""
    return [{"fact_id": "", "claim_in_article": "", "issue": "KEEP_SPEAKER_CONTRAST",
             "explanation": ("Paragraphs 2, 3 and 4 are spoken by three different people in the first person, and paragraphs 1 and 5 are a narrator. "
                             "Keep each speaker's sentence-length contrast, hesitations, questions-back and directness, and keep who is speaking, "
                             "even when you simplify the English. Do not even out the rhythm across the paragraphs or turn them into a neutral explanation. "
                             "Keep each speaker's concrete objects and everyday words (delivery notice, delivery time slot, pickup locker) rather than abstract wording. "
                             "Do not add any new fact, event or claim.")}]


LEDGER_PLACEHOLDER = ("(この記事は、公開されている複数の意見をもとに組み立てた3人の声であり、検証済みの事実台帳はありません。"
                      "数値・統計・制度・企業の具体的な事実主張を新たに述べてはいけません。)")


def cmd_english(a):
    import er005_cost_logger as cl
    import er003_v1_en_direct_vfl_01_generate as vfl01
    import er003_v1_n3_01_advanced_adaptation_generate as adv_gen
    import er003_v1_n3_01_standard_a2_generate as std_gen
    import er012_e_family_entertainment_two_level_runner_01 as efam
    cap = min(require_paid(a.paid)["cap_jpy"], TEXT_CAP_JPY)
    cl.install(f"{RD}/raw_usage_log_en.jsonl")
    client = vfl01.get_client()
    ed = f"{RD}/english_r0"
    if os.path.exists(f"{ed}/en_summary.json"):
        print("skip english")
        return
    ja = y0.load_gated_article_or_stop(f"{RD}/y_writer/gate_r0")
    w1.wt(f"{RD}/research_ledger/verified_fact_ledger.txt", LEDGER_PLACEHOLDER)
    mf = y5_contrast_must_fix()

    def _adv(extra=None):
        r = adv_gen.generate_family_x_faithful_translation(ja, client=client, must_fix=mf + (extra or []))
        iol = efam._advanced_in_one_line(client, r.title, r.body, ja, LEDGER_PLACEHOLDER)
        return f"# {r.title}\n\n{r.body}\n\n## In one line\n{iol['text']}"
    adv = _adv()
    c = y0.check_en_contract(adv)
    retried = False
    if not c["ok"] and any("PARAGRAPH_COUNT" in v for v in c["violations"]):
        retried = True
        adv = _adv(efam._FAMILY_X_PARAGRAPH_RETRY_MUST_FIX)
        c = y0.check_en_contract(adv)
    w1.wt(f"{ed}/b1b/article.md", adv)
    w1.wj(f"{ed}/b1b/contract.json", {"retried": retried, **{k: v for k, v in c.items() if k != "split"}})
    if not c["ok"]:
        w1.wj(f"{ed}/en_summary.json", {"status": "ADV_CONTRACT_STOP", "violations": c["violations"]})
        print("Advanced 契約違反", c["violations"])
        return
    s = std_gen.generate_family_x_standard_a2_no_heading(adv, client=client, must_fix=mf)
    cs = y0.check_en_contract(s.text)
    sretried = False
    if not cs["ok"] and any("PARAGRAPH_COUNT" in v for v in cs["violations"]):
        sretried = True
        s = std_gen.generate_family_x_standard_a2_no_heading(adv, client=client, must_fix=mf + efam._FAMILY_X_PARAGRAPH_RETRY_MUST_FIX)
        cs = y0.check_en_contract(s.text)
    w1.wt(f"{ed}/a2/article.md", s.text)
    w1.wj(f"{ed}/a2/contract.json", {"retried": sretried, **{k: v for k, v in cs.items() if k != "split"}})
    w1.wj(f"{ed}/en_monitors.json", {"b1b": y0.en_monitors(adv), "a2": y0.en_monitors(s.text)})
    s3 = {}
    if a.s3 and cs["ok"]:
        for lvl, tx in (("a2", s.text), ("b1b", adv)):                          # 監視専用(記録のみ、Gateにしない=既存S3)
            sp = y0.split_en_article(tx)
            if len(sp["paragraphs"]) == 5:
                chk = y0.run_leakage_check(client, y0.sections_from_paragraphs(sp["paragraphs"]), model=y0.MODEL_CHEAP, effort="high",
                                           stage=f"yr_s3_leak_{lvl}", language_note="英語")
                s3[lvl] = {k: v for k, v in chk.items() if k != "parsed"}
                s3[lvl]["parsed"] = chk["parsed"]
    w1.wj(f"{ed}/s3_monitor_leakage.json", s3)
    ja_paras = y0.parse_article(ja)["paragraphs"]
    mp = mapping_check(ja_paras, {"adv": y0.split_en_article(adv)["paragraphs"], "std": y0.split_en_article(s.text)["paragraphs"]})
    w1.wj(f"{ed}/mapping_check.json", mp)
    w1.wj(f"{ed}/en_summary.json", {"status": "OK" if cs["ok"] else "STD_CONTRACT_STOP", "std_violations": cs["violations"],
                                    "ja_sha256": w1.sha_text(ja), "adv_sha256": w1.sha_text(adv), "mapping_ok": mp["ok"]})
    guard("after english", cap)
    print(f"[Y-REDELIVERY] english完了 mapping_ok={mp['ok']}")


def cmd_scaffold(a):
    """Comment1〜3/Preview/KP/日本語タイトル。既存5パート版 er110_family_y_text_trial_01_run.cmd_scaffold をそのまま呼ぶ(Comment 4は生成しない)。"""
    import er110_family_y_text_trial_01_run as yrun
    cap = min(require_paid(a.paid)["cap_jpy"], TEXT_CAP_JPY)
    yrun.BUDGET = cap          # process内のみ(既存module定数の一時差替え。保険として本run dirのCapへ)
    prev_tag = y0.THEME_TAG
    y0.THEME_TAG = THEME_TAG
    try:
        yrun.cmd_scaffold(argparse.Namespace(run_dir=RD, log="raw_usage_log_sc.jsonl", stages="r0"))
    finally:
        y0.THEME_TAG = prev_tag
        yrun.BUDGET = 215.0
    guard("after scaffold", cap)


# ============================================================
# 音声(既存5パート版 er110_family_y_audio_trial_01 を出力先差替えのみで使う)
# ============================================================
@contextlib.contextmanager
def audio_module_redirected():
    import er110_family_y_audio_trial_01 as old
    prev = (old.BASE, old.SRC, old.OUT_ROOT)
    old.BASE, old.SRC, old.OUT_ROOT = ROOT, RD, AUDIO_ROOT
    try:
        yield old
    finally:
        old.BASE, old.SRC, old.OUT_ROOT = prev


def verify_voice_assignment() -> dict:
    import er062_family_z_structure_01 as z
    got = z.assign_dialogue_voices(ROSTER)
    if got != EXPECTED_VOICES:
        raise RuntimeError(f"Z正式表の割当 {got} が固定割当 {EXPECTED_VOICES} と一致しません。Voice方式を変えず停止します")
    import er110_family_y_audio_trial_01 as old
    if old.FIXED_VOICE_SLOTS != EXPECTED_VOICES:
        raise RuntimeError("既存Y音声moduleの固定割当が想定と違います")
    return {"z_rule_assignment": got, "y_fixed_slots": old.FIXED_VOICE_SLOTS, "narrator": "Aoede", "match": True}


def cmd_audio(a):
    if a.stage != "prep":
        require_paid(a.paid)
    vs = verify_voice_assignment()
    w1.wj(f"{ROOT}/voice_assignment_check.json", vs)
    with audio_module_redirected() as old:
        argv = ["er110_family_y_audio_trial_01.py", "--cand", CAND, "--stage", a.stage, "--level", a.level, "--budget-jpy", str(a.budget_jpy)]
        prev_argv = sys.argv
        sys.argv = argv
        try:
            old.main()
        finally:
            sys.argv = prev_argv


def main():
    ap = argparse.ArgumentParser(description="Family Y 再配達 音声化Trial(DEV/Trial専用の薄いglue)")
    ap.add_argument("cmd", choices=("ja", "english", "scaffold", "rights", "audio"))
    ap.add_argument("--paid", action="store_true", help="有料run。予算承認ファイルも必要")
    ap.add_argument("--s3", action="store_true")
    ap.add_argument("--stage", default="prep", choices=("prep", "tts", "assemble", "all"))
    ap.add_argument("--level", default="both", choices=("a2", "b1b", "both"))
    ap.add_argument("--budget-jpy", type=float, default=35.0)
    ap.add_argument("--out", default=f"{ROOT}/rights_check.json")
    a = ap.parse_args()
    {"ja": cmd_ja, "english": cmd_english, "scaffold": cmd_scaffold, "rights": cmd_rights, "audio": cmd_audio}[a.cmd](a)


if __name__ == "__main__":
    main()
