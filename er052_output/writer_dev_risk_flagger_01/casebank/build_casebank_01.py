# -*- coding: utf-8 -*-
"""WRITER-DEV-RISK-FLAGGER-DESIGN-01 委任_01A: ケースバンク構築(API呼び出しなし、新規生成なし)。
全ての文・台帳・ラベルは過去成果物からの逐語抽出。ラベルは過去成果物の記録に従い、本スクリプトでは再判定しない。
実行: python build_casebank_01.py  (リポジトリroot=eigo-radio で実行)"""
import json, os, re, random, hashlib, subprocess, glob, sys
sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
os.chdir(ROOT)
OUT = "er052_output/writer_dev_risk_flagger_01/casebank"
SEED_ID = 20261009      # case_id生成
SEED_SPLIT = 20261010   # 開発/保留 分割
SEED_MECH = 20261011    # 機械抽出サンプリング
FA = "er052_output/factlock_astra_e2e_trial_01"
THEMES = ["byd_recall", "central_bank_mortgage", "hormuz", "meta", "openai_copyright",
          "semiconductor_earnings", "small_bag", "space_weapons", "streaming_price"]


def rd(p):
    return open(p, encoding="utf-8").read()


def norm(s):
    return (s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
            .replace("“", '"').replace("”", '"').replace("’", "'").strip())


def line_of(path, token):
    """path内でtokenを含む最初の行番号(1始まり)。なければNone"""
    try:
        for i, ln in enumerate(open(path, encoding="utf-8"), 1):
            if token in ln:
                return i
    except Exception:
        pass
    return None


def grep_files(frag, include=("*.md",), roots=("er052_output", "er019_output")):
    cmd = ["grep", "-rlF"] + [f"--include={i}" for i in include] + ["--", frag] + list(roots)
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    return [x.strip() for x in r.stdout.splitlines() if x.strip()]


ART_NAMES = ("article.md", "revision2.md", "revision1.md", "original.md")


def split_sents(text):
    # 段落内の文分割(日本語: 。！？ / 英語: .!? の後の空白)
    parts = re.split(r"(?<=[。！？])|(?<=[.!?])\s+", text)
    return [p.strip() for p in parts if p and p.strip()]


def locate(sentence, hints=(), prefer_article=True):
    """sentenceを含む成果物を探し、(path, 行番号, 前文, 後文, 全文所在)を返す。見つからなければNone。
    articleファイル(article.md/revision*.md/original.md)を優先。評価docは文脈に使わない。"""
    frags = [sentence]
    ns = norm(sentence)
    if ns != sentence:
        frags.append(ns)
    cands = []
    for fr in frags:
        for inc in (ART_NAMES,):
            files = grep_files(fr, include=inc)
            cands += files
        if cands:
            break
    if not cands:
        return None

    def rank(p):
        s = 0
        for h in hints:
            if h in p.replace("\\", "/"):
                s -= 10
        if p.endswith("article.md"):
            s -= 1
        return (s, p)
    cands = sorted(set(cands), key=rank)
    p = cands[0]
    txt = rd(p)
    lines = txt.split("\n")
    for i, ln in enumerate(lines):
        if sentence in ln or ns in norm(ln):
            sents = split_sents(ln)
            idx = None
            tsents = split_sents(sentence)
            span = 1
            for j, s in enumerate(sents):
                if sentence in s or ns in norm(s) or norm(s) in ns:
                    idx = j
                    break
            if idx is None and len(tsents) > 1:
                for j in range(len(sents)):
                    if norm(sents[j]) == norm(tsents[0]) or norm(tsents[0]) in norm(sents[j]):
                        idx, span = j, len(tsents)
                        break
            before = after = None
            if idx is not None:
                before = sents[idx - 1] if idx > 0 else None
                after = sents[idx + span] if idx + span < len(sents) else None
            if before is None:  # 前の非空行の最終文
                for k in range(i - 1, -1, -1):
                    if lines[k].strip():
                        before = split_sents(lines[k])[-1]
                        break
            if after is None:
                for k in range(i + 1, len(lines)):
                    if lines[k].strip():
                        after = split_sents(lines[k])[0]
                        break
            full_sent = sents[idx] if (idx is not None and span == 1) else None
            return dict(sentence_full=full_sent, path=p.replace("\\", "/"), line=i + 1, before=before, after=after,
                        n_hits=len(cands), full_text_path=p.replace("\\", "/"))
    return None


# ---- 台帳 ----
_LEDGER_CACHE = {}


def load_ledger(path):
    if path in _LEDGER_CACHE:
        return _LEDGER_CACHE[path]
    blocks = {}
    cur = None
    for i, ln in enumerate(open(path, encoding="utf-8"), 1):
        m = re.match(r"\[VERIFIED\]\s+([A-Za-z0-9_\-]+):", ln)
        if m:
            cur = m.group(1)
            blocks[cur] = dict(line=i, text=ln.rstrip("\n"))
        elif cur and ln.startswith("  ") and ln.strip():
            blocks[cur]["text"] += "\n" + ln.rstrip("\n")
        elif ln.strip() == "":
            pass
    _LEDGER_CACHE[path] = blocks
    return blocks


def ledger_fact(fact_id, ledger_paths):
    for lp in ledger_paths:
        if lp and os.path.exists(lp):
            b = load_ledger(lp)
            if fact_id in b:
                return dict(id=fact_id, text=b[fact_id]["text"], src=f"{lp.replace(chr(92), '/')}:{b[fact_id]['line']}")
    return dict(id=fact_id, text=None, src=None)


def ledger_for_run_dir(article_path):
    """article_pathから上位をたどりresearch_ledger/verified_fact_ledger.txtを探す"""
    d = os.path.dirname(article_path)
    for _ in range(6):
        c = os.path.join(d, "research_ledger", "verified_fact_ledger.txt")
        if os.path.exists(c):
            return c.replace("\\", "/")
        d = os.path.dirname(d)
    return None


# =========== 元データ ===========
WE = {c["key"]: c for c in json.load(open("er052_output/writer_eval_dual_llm_method_trial_01/cases_01.json", encoding="utf-8"))["cases"]}
RC_PATH = "docs/pm/open233_missed_candidates_reclassification_2026-10-03.md"
RC_LINES = rd(RC_PATH).split("\n")


def rc_section(k):
    """RC文書のKxx節を返す: dict(sentence, ledger_text, head, line, context_ref)"""
    start = None
    for i, ln in enumerate(RC_LINES):
        if ln.startswith(f"### {k} "):
            start = i
            break
    assert start is not None, k
    end = len(RC_LINES)
    for j in range(start + 1, len(RC_LINES)):
        if RC_LINES[j].startswith("### K"):
            end = j
            break
    body = RC_LINES[start:end]
    sent = None
    ctx_ref = None
    for ln in body:
        m = re.match(r"- \*\*原文\*\*\(逐語、(英語|日本語)記事\): `(.*)`\s*$", ln)
        if m:
            sent = m.group(2)
            lang = "EN" if m.group(1) == "英語" else "JA"
        if ln.strip().startswith("- 前後(参考)") or ln.strip().startswith("  - 前後(参考)"):
            ctx_ref = ln.strip()
    led = []
    infence = False
    for ln in body:
        if ln.strip() == "```":
            if infence:
                break
            infence = True
            continue
        if infence:
            led.append(ln.rstrip())
    fid = re.search(r"\[VERIFIED\]\s+([A-Za-z0-9_\-]+):", "\n".join(led)).group(1)
    return dict(sentence=sent, lang=lang, ledger_text="\n".join(led), fact_id=fid, line=start + 1,
                head=RC_LINES[start], ctx_ref=ctx_ref)


CASES = []
used_ids = set()


def mk_id(rnd):
    while True:
        cid = "".join(rnd.choice("abcdefghjkmnpqrstuvwxyz23456789") for _ in range(6))
        if cid not in used_ids:
            used_ids.add(cid)
            return "rf_" + cid


rnd_id = random.Random(SEED_ID)


def add(**kw):
    kw.setdefault("secondary_type", None)
    kw.setdefault("notes", "")
    kw.setdefault("near_dup_group", None)
    kw.setdefault("synthetic", False)
    kw.setdefault("forced_split", None)
    kw["case_id"] = mk_id(rnd_id)
    CASES.append(kw)
    return kw


def ctx_from_locate(loc, fallback_b=None, fallback_a=None, fallback_src=None):
    if loc and (loc.get("before") or loc.get("after")):
        return dict(before=loc["before"], after=loc["after"], source=f"{loc['path']}:{loc['line']}")
    return dict(before=fallback_b, after=fallback_a, source=fallback_src)


# ------------------ WRITER-EVAL K01..K12 ------------------
def we_case(k, label, basis, basis_detail, atype, **kw):
    c = WE[k]
    hits = locate(c["sentence"])  # 記事全文所在(あれば)
    full = hits["full_text_path"] if hits else None
    return add(
        legacy_ids=[f"WE-{k}"], legacy_case_id=c["case_id"], label=label, label_basis=basis, label_basis_detail=basis_detail,
        label_src=c["human_src"], accident_type=atype, lang=c["lang"],
        fact=dict(id=c["fact_id"], text=c["fact"], src=c["fact_src"]),
        sentence=c["sentence"],
        context=dict(before=c["before"], after=c["after"], source=c["sentence_src"]),
        sentence_locator=(f"{hits['path']}:{hits['line']}" if hits else c["sentence_src"]),
        article_full_text=full or "(単体article.mdとしては未保存。sentence_src参照)", **kw)


we_case("K01", "重大", "ユーザー確認", "ユーザー確認済みC(2026-10-09、DECISION_LOG L20053ほか)", "rollback方向反転", near_dup_group="rollback_hc012", forced_split="holdout")
we_case("K02", "重大", "ユーザー確認", "ユーザー確認済み重大(CCP jb9k。K02のhuman_src参照)", "不在断定", secondary_type="否定反転", forced_split="holdout")
we_case("K03", "重大", "ユーザー確認", "ユーザー確認済みC(2026-10-09)。gold A5-0", "rollback方向反転", near_dup_group="rollback_hc012", forced_split="dev")
we_case("K11", "重大", "ユーザー確認", "ユーザー判断『C寄り、Bの余地あり』(2026-10-09)。sw-p2r2-01と同一文", "主体対象入替",
        forced_split="holdout", notes="legacy: ng_origin sw-p2r2-01。ラベルはC寄り(Bの余地あり)のため重大寄りとして扱い、KPIは『Bなら除外』感度も出す")
we_case("K08", "非重大", "ユーザー確認", "ユーザー確認済みA(問題なし、2026-10-09)", "(なし)", forced_split="holdout")
we_case("K09", "非重大", "ユーザー確認", "ユーザー確認済みA(問題なし、2026-10-09)", "(なし)", forced_split="holdout")
we_case("K12", "非重大", "ユーザー確認", "ユーザー確認済みA(問題なし、2026-10-09)。HC-012の忠実文", "(なし)", forced_split="dev")
we_case("K04", "非重大", "Sonnet判定", "Sonnet暫定の境界(B?)。ユーザー未裁定。非重大側に置く(重大/非重大のみの指示)", "(境界・Rollback語義)")
we_case("K06", "非重大", "Sonnet判定", "Sonnet暫定の境界(B?・不在/非公開の断定)。ユーザー未裁定。非重大側", "(境界・不在断定)")
we_case("K10", "非重大", "Sonnet判定", "Sonnet暫定の境界(B?・因果追加型)。ユーザー未裁定。非重大側", "(境界・因果追加)")


# ------------------ 一次artifactから逐語採取する重大(ng_origin §4 / E2E_02 P2 / Safety-critical / RC) ------------------
def prim_case(legacy, sentence, fact_id, ledger_paths, hints, label, basis, basis_detail, label_src, atype, lang="EN",
              secondary_type=None, notes="", near_dup_group=None, ctx_fallback=None, ja_counterpart=None, fact_override=None):
    loc = locate(sentence, hints=hints)
    if loc is None and ja_counterpart:
        pass
    ledger_cands = list(ledger_paths)
    if loc:
        lp = ledger_for_run_dir(loc["path"])
        if lp:
            ledger_cands.insert(0, lp)
    fact = fact_override or ledger_fact(fact_id, ledger_cands)
    ctx = ctx_from_locate(loc, *(ctx_fallback or (None, None, None)))
    frag_note = ""
    if loc and loc.get("sentence_full") and norm(loc["sentence_full"]) != norm(sentence) and norm(sentence) in norm(loc["sentence_full"]):
        frag_note = "対象は断片引用(評価doc)。sentenceは記事内の当該文全体に拡張: 元断片=「%s」。" % sentence
        sentence = loc["sentence_full"]
    if loc and hints and not any(h in loc["path"].replace("\\", "/") for h in hints):
        frag_note += "同一文が見つかった別runの成果物を文脈に使用(元の評価対象記事そのものではない可能性)。"
    notes = (notes + " " + frag_note).strip()
    return add(legacy_ids=legacy, label=label, label_basis=basis, label_basis_detail=basis_detail, label_src=label_src,
               accident_type=atype, secondary_type=secondary_type, lang=lang, fact=fact, sentence=sentence,
               ja_counterpart=ja_counterpart, context=ctx,
               sentence_locator=(f"{loc['path']}:{loc['line']}" if loc else "(記事ファイルでは逐語未特定。label_src内の引用)"),
               article_full_text=(loc["full_text_path"] if loc else "(未特定)"), notes=notes, near_dup_group=near_dup_group)


E2E = "er052_output/open233_allfact_note_e2e_02"
SW = f"{E2E}/eval/stagewise/stagewise_"
SON = "Sonnet判定(STAGEWISE評価、人間確認なし。ng_origin_by_stage.md §4)"

prim_case(["meta-p2r2-02", "E2E02-P2-重大"], "But the humans who ended up in the main role had not been told.", "MUSE-HC-012",
          [f"{E2E}/runs/meta/nb/p2/rep2/research_ledger/verified_fact_ledger.txt"], ["meta/nb/p2/rep2"],
          "重大", "Sonnet判定", SON + "。台帳は開示対象を特定しないのに契約スタッフ本人が知らされていなかったと読める", f"{SW}meta_hormuz.json ('meta-p2r2-02'); docs/pm/ng_root_cause_01/ng_origin_by_stage.md L93",
          "主体対象入替", ja_counterpart="ただし、主役になった人間が知らされていなかった。")
prim_case(["ai-p2r1-01", "E2E02-P2-重大"], "In other words, it was like a heavily guarded prison whose back door had been left unlocked.", "EVID-008",
          [f"{E2E}/runs/ai_control/nb/p2/rep1/research_ledger/verified_fact_ledger.txt"], ["ai_control/nb/p2/rep1"],
          "重大", "Sonnet判定", SON + "。比喩で状況を逆に描く(誤設定環境と自律的乗っ取りの区別)", f"{SW}sewer_ai_control.json ('ai-p2r1-01'); ng_origin_by_stage.md L94",
          "その他", secondary_type="台帳外の比喩追加(状況の逆描写)", ja_counterpart="いわば、厳重な監獄のはずが、裏口の鍵がかかっていなかった状態です。")
prim_case(["ai-p2r1-02", "E2E02-P2-重大"], "whether it tends to be used for harmful purposes", "CONTROL-002",
          [f"{E2E}/runs/ai_control/nb/p2/rep1/research_ledger/verified_fact_ledger.txt"], ["ai_control/nb/p2/rep1"],
          "重大", "Sonnet判定", SON + "(Rewrite前のEN。Rewriteで修正済みの一時重大)", f"{SW}sewer_ai_control.json ('ai-p2r1-02'); ng_origin_by_stage.md L98",
          "主体対象入替", notes="対象はEN断片。locate()は断片を含む文を前後文つきで返す")
prim_case(["ai-p2r2-07", "E2E02-P2-重大"], "In a simulated safety evaluation, Claude Opus 4 attempted blackmail in 84% of rollouts.", "EVID-006",
          [f"{E2E}/runs/ai_control/nb/p2/rep2/research_ledger/verified_fact_ledger.txt"], ["ai_control/nb/p2/rep2"],
          "重大", "Sonnet判定", SON + "(Rewriteが無関係文を置換した事故。OPEN-238)", f"{SW}sewer_ai_control.json ('ai-p2r2-07'); ng_origin_by_stage.md L98",
          "その他", secondary_type="無関係文の挿入(Rewrite由来)", notes="根拠Factは挿入元(EVID-006)。置換先の段落の台帳Factとは無関係")
prim_case(["sw-p2r2-02", "E2E02-P2-重大"], "It is that preparations to secure space have come into public view for the first time.", "F-001",
          [f"{E2E}/runs/space_weapons/nb/p2/rep2/research_ledger/verified_fact_ledger.txt"], ["space_weapons/nb/p2/rep2"],
          "重大", "Sonnet判定", SON + "。『初めて』の対象が兵器配備から防衛の備えへ拡張(再ラベルは委任_95作業)", f"{SW}space_weapons.json ('sw-p2r2-02'); ng_origin_by_stage.md L96",
          "主体対象入替", secondary_type="数量時系列(『初めて』の範囲拡張)", ja_counterpart="宇宙の戸締まりをするための備えが、初めて表に出たことです。")
NTM = "er052_output/open233_note_transfer_matrix_01"
prim_case(["hormuz-T0M0r2-01"], "Mr. Trump posted that for all cargo passing through the Strait of Hormuz, the United States would seek payment equal to 20 percent of the cost of providing safety and security.", "HF-002",
          [f"{NTM}/runs/hormuz/nb/T0M0/rep2/research_ledger/verified_fact_ledger.txt"], ["T0M0/rep2"],
          "重大", "Sonnet判定", SON + "(NTM評価。20%の対象が貨物から費用へ入れ替わり、ENのみ)", f"{NTM}/eval/E_hormuz.md L20; ng_origin_by_stage.md L97",
          "主体対象入替", secondary_type="数量時系列(20%の適用対象)")

# RC文書(委任_51再分類)から
def rc_case(k, label, basis, detail, atype, secondary=None, notes="", hints=(), near=None):
    s = rc_section(k)
    loc = locate(s["sentence"], hints=hints)
    ctx = ctx_from_locate(loc, None, None, f"{RC_PATH}:{s['line']}({s['ctx_ref'] or '前後文の記録なし'})")
    if loc and hints and not any(h in loc["path"] for h in hints):
        notes = (notes + " 同一文が見つかった別runの成果物を文脈に使用。").strip()
    return add(legacy_ids=[f"RC-{k}"], label=label, label_basis=basis, label_basis_detail=detail,
               label_src=f"{RC_PATH}:{s['line']} (見出し: {s['head'][:100]})",
               accident_type=atype, secondary_type=secondary, lang=s["lang"],
               fact=dict(id=s["fact_id"], text=s["ledger_text"], src=f"{RC_PATH}:{s['line']}(Checkerが見たLedgerブロック逐語)"),
               sentence=s["sentence"], context=ctx,
               sentence_locator=(f"{loc['path']}:{loc['line']}" if loc else f"{RC_PATH}:{s['line']}(RC文書内の逐語引用のみ)"),
               article_full_text=(loc["full_text_path"] if loc else "(記事ファイルでは未特定)"), notes=notes, near_dup_group=near)


rc_case("K16", "重大", "Sonnet判定", "委任_51 Sonnet新判定=重大(設計書§0-2 BLOCK候補『継続していた出来事→一度消えて戻った出来事』)。ユーザー未確認", "数量時系列")
# K18はJA原文。EN対応文(A2A3-0)を別caseにせず、K18のja/en対を1件として保存する
_k18 = rc_section("K18")
_en18 = "The idea was that those carrying the cargo would repay the money the United States spends to keep the strait safe."
_loc18 = locate(_en18)
add(legacy_ids=["RC-K18", "Safety-A2A3-0"], label="重大", label_basis="Sonnet判定",
    label_basis_detail="委任_51 Sonnet新判定=重大(境界)+Safety-critical A2A3-0(正式採用基準[ユーザー承認]の机上適用、Fable確定相当)。ユーザー個別確認なし",
    label_src=f"{RC_PATH}:{_k18['line']}; DECISION_LOG.md L17944-17946付近",
    accident_type="主体対象入替", lang="EN",
    fact=dict(id=_k18["fact_id"], text=_k18["ledger_text"], src=f"{RC_PATH}:{_k18['line']}(Ledgerブロック逐語)"),
    sentence=_en18, ja_counterpart=_k18["sentence"],
    context=ctx_from_locate(_loc18, None, None, f"{RC_PATH}:{_k18['line']}(前後文の記録なし)"),
    sentence_locator=(f"{_loc18['path']}:{_loc18['line']}" if _loc18 else f"{RC_PATH}:{_k18['line']}(RC文書内の逐語引用のみ。JA原文はRC文書の『原文』)"),
    article_full_text=(_loc18["full_text_path"] if _loc18 else "(記事ファイルでは未特定)"), notes="支払義務者(貨物を運ぶ側)の特定=台帳は未提示")
rc_case("K20", "重大", "Sonnet判定", "委任_51 Sonnet新判定=重大(境界あり。因果・動機の創作、B4-a=BLOCKINGと整合)。ユーザー未確認", "その他", secondary="因果・動機の創作")

# Safety-critical(正式採用基準の机上適用 DECISION_LOG L17944-17947)。ledgerはhormuz/meta台帳から
HZ_L = f"{FA}/stage_r/hormuz/research_ledger/verified_fact_ledger.txt"
ME_L = f"{FA}/stage_r/meta/research_ledger/verified_fact_ledger.txt"
SC_SRC = "DECISION_LOG.md L17944-17947付近(Safety-critical 5件・正式採用3定義への机上適用); er052_output/open233_safety_control_04/partA_result.json"
SC_DETAIL = "Safety-critical gold(ユーザー承認の正式採用基準に基づくFable判断)。ユーザー個別ラベルは未記録"
prim_case(["Safety-B3"], "Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14, so the flashy 20% plan left the stage",
          "HF-007", [HZ_L, "er019_output/family_x_refresh_e2e_01/hormuz/run_03/ledger/verified_fact_ledger.txt"], ["hormuz"],
          "重大", "Fable確定", SC_DETAIL + "。因果の創作", SC_SRC, "その他", secondary_type="因果の創作")
prim_case(["Safety-B4-a"], "A person can take over when AI alone has trouble.", "MUSE-HC-002", [ME_L], ["meta"],
          "重大", "Fable確定", SC_DETAIL + "。未確認の仕組み・設計意図の追加", SC_SRC, "その他", secondary_type="未確認の仕組みの追加")
prim_case(["Safety-A4-0"], "Through Muse, trained human contract workers made some calls and completed the exchanges with users.",
          "MUSE-HC-006", [ME_L], ["meta"],
          "重大", "Fable確定", SC_DETAIL + "。やり取りの相手(カウンターパート)の取り違え", SC_SRC, "主体対象入替")

# 旧腕 w1-11(Sonnet 重大・境界)
prim_case(["w1-11"], "AIが電話をかけ、相手に切られることもある。そこで人間が電話を担当する。", "MUSE-HC-009",
          [f"{FA}/runs/meta/old/research_ledger/verified_fact_ledger.txt"], ["meta/old"],
          "重大", "Sonnet判定", "labels_merged w1-11: Sonnet暫定『重大(境界、軽微に読む余地あり)』。因果『そこで』の創作", f"{FA}/eval/labels_merged.jsonl (row_id=w1-11)",
          "その他", lang="JA", secondary_type="因果の創作", notes="旧腕JA R2(STOP原因)。台帳は別事実の並記で因果記載なし")

# ------------------ 非重大: RC文書のSonnet判定(Checkerが重大扱いした『過剰品質』型) ------------------
for k, lab, basis, det in [
    ("K19", "非重大", "ユーザー確認", "ユーザー決定2026-10-03: 軽微(旧Sonnet判定は重大(境界))。RC文書見出し"),
    ("K04", "非重大", "ユーザー確認", "ユーザー決定例1: 軽微(QUALITY)"),
    ("K10", "非重大", "ユーザー確認", "ユーザー決定例2: 問題なし(ACCEPTABLE)"),
    ("K01", "非重大", "Sonnet判定", "委任_51 Sonnet新判定=問題なし"),
    ("K02", "非重大", "Sonnet判定", "委任_51 Sonnet新判定=軽微(Brent→oil prices一般化)"),
    ("K03", "非重大", "Sonnet判定", "委任_51 Sonnet新判定=軽微(Brent→oil prices一般化)"),
    ("K05", "非重大", "Sonnet判定", "委任_51 Sonnet新判定=軽微(境界、単数→複数形)"),
    ("K08", "非重大", "Sonnet判定", "委任_51 Sonnet新判定=問題なし"),
    ("K09", "非重大", "Sonnet判定", "委任_51 Sonnet新判定=問題なし"),
    ("K11", "非重大", "Sonnet判定", "委任_51 Sonnet新判定=軽微(副社長→executive)"),
    ("K12", "非重大", "Sonnet判定", "委任_51 Sonnet新判定=問題なし"),
    ("K13", "非重大", "Sonnet判定", "委任_51 Sonnet新判定=問題なし"),
    ("K14", "非重大", "Sonnet判定", "委任_51 Sonnet新判定=問題なし(JA)"),
    ("K15", "非重大", "Sonnet判定", "委任_51 Sonnet新判定=問題なし"),
    ("K17", "非重大", "Sonnet判定", "委任_51 Sonnet新判定=軽微"),
    ("K23", "非重大", "Sonnet判定", "委任_51 Sonnet新判定=問題なし"),
]:
    rc_case(k, lab, basis, det, "(なし)" if "問題なし" in det or "軽微" in det else "(なし)")

# ------------------ 非重大: EVAL_E2E_01 境界・FINAL_MINOR_ITEMS(軽微) ------------------
LM = {}
for ln in open(f"{FA}/eval/labels_merged.jsonl", encoding="utf-8"):
    r = json.loads(ln)
    LM[r["row_id"]] = r


def minor_case(tag, sentence, row_id, theme, arm, hints, ja=False):
    loc = locate(sentence, hints=hints)
    if loc is None:
        return None
    r = LM[row_id]
    lp = ledger_for_run_dir(loc["path"]) or f"{FA}/stage_r/{theme}/research_ledger/verified_fact_ledger.txt"
    B = load_ledger(lp) if os.path.exists(lp) else {}
    blob = " ".join(str(r["orig"].get(k, "")) for k in ("claim", "evidence", "claim_id")) + " " + str(r["claim_text"])
    mentioned = [f for f in B if re.search(r"(?<![A-Za-z0-9])" + re.escape(f) + r"(?![A-Za-z0-9])", blob)]
    if not mentioned:  # 'F5' -> 'F-005' 等の略記
        for f in B:
            m2 = re.match(r"([A-Za-z]+)-0*(\d+)$", f)
            if m2 and re.search(r"(?<![A-Za-z0-9])" + m2.group(1) + m2.group(2) + r"(?![0-9])", blob):
                mentioned.append(f)
    fact_obj = ledger_fact(mentioned[0], [lp]) if mentioned else dict(id="(特定できず: ledger全体が入力)", text=None, src=lp)
    return add(legacy_ids=[tag, row_id], label="非重大", label_basis="Sonnet判定",
               label_basis_detail=f"labels_merged {row_id}: n_sev=軽微(Sonnet暫定、{r['label_source']})。EVAL_E2E_01の{tag}。ユーザー未確認(境界は回答待ち)",
               label_src=f"{FA}/eval/labels_merged.jsonl (row_id={row_id}); {FA}/eval/EVAL_E2E_01.md",
               accident_type="(軽微/境界)", lang=("JA" if ja else "EN"),
               fact=fact_obj,
               sentence=sentence, context=ctx_from_locate(loc), sentence_locator=f"{loc['path']}:{loc['line']}",
               article_full_text=loc["full_text_path"], notes=f"台帳全文: {lp}。Fact特定は評価doc記載のID一致による(複数Factに跨る場合あり: {mentioned})。Flagger入力は台帳全体")


MINORS = [
    ("B-02", "性能表は伏せたまま", "w1-49", "space_weapons", "new", ["space_weapons/new"], True),
    ("B-03", "明らかにされていません", "w1-61", "space_weapons", "old", ["space_weapons/old"], True),
    ("B-04", "Russia has destroyed satellites with anti-satellite missiles fired from the ground.", "w1-52", "space_weapons", "new", ["space_weapons/new"], False),
    ("B-07", "政策金利の目標を0.25ポイント引き上げ、3.75％から4.00％にしました。", "w2-204", "central_bank_mortgage", "new", ["central_bank_mortgage/new"], True),
    ("B-06", "APが示した固定型の住宅ローン金利の全米平均は、5.98％から7.40％へ上昇しました。", "w2-201", "central_bank_mortgage", "new", ["central_bank_mortgage/new"], True),
    ("B-11", "2026年9月23日から新料金です", "w3-98", "streaming_price", "old", ["streaming_price/old"], True),
    ("B-09", "会社が示した次の数字は、AI半導体売上高の予想ではありません。次の四半期の連結売上高の見通しです。", "w3-85", "semiconductor_earnings", "new", ["semiconductor_earnings/new"], True),
    ("B-10", "今回の発表を整理すると、登場するのは三つ。AI半導体の実績、会社全体の実績、会社全体の見通し。", "w3-86", "semiconductor_earnings", "new", ["semiconductor_earnings/new"], True),
]
UNLOCATED = []
for tag, frag, rid, th, arm, hints, ja in MINORS:
    # 完全文でlocateし、失敗したら断片で探して含む文を取る
    ok = minor_case(tag, frag, rid, th, arm, hints, ja)
    if ok is None:
        # 断片 → 含む行を探して文として採用
        files = grep_files(frag, include=ART_NAMES)
        files = sorted(files, key=lambda p: (0 if any(h in p.replace("\\", "/") for h in hints) else 1, p))
        done = False
        for p in files:
            for i, ln in enumerate(rd(p).split("\n"), 1):
                if frag in ln:
                    sents = split_sents(ln)
                    sent = next((s for s in sents if frag in s), None)
                    if sent:
                        ok = minor_case(tag, sent, rid, th, arm, hints, ja)
                        done = ok is not None
                        break
            if done:
                break
        if not done:
            UNLOCATED.append((tag, rid, frag))

# S0_USER_CHECK 3件(要約MAJOR、ユーザー未回答→非重大側)
S0 = "er052_output/open243_translation_ng_analysis_01/S0_USER_CHECK.md"
S0_ITEMS = [
    ("S0-1", "Meta paused its human-concierge feature after contract workers made calls without properly informing users.", "MUSE-HC-012", "「users」(開示対象)を書いたこと", "確認1"),
    ("S0-2", "Meta’s AI calling test used human contractors without proper disclosure, so the company rolled back that feature.", "MUSE-HC-012", "『so』による因果接続", "確認2"),
    ("S0-3", "Oil prices stayed high despite the shift from a proposed Hormuz fee to investment deals, as shipping-safety fears persisted.", "HF-009", "Brent先物→oil pricesの一般化", "確認3"),
]
for tag, sent, fid, nm, kk in S0_ITEMS:
    fl = ME_L if fid.startswith("MUSE") else HZ_L
    add(legacy_ids=[tag, f"S0_USER_CHECK {kk}"], label="非重大", label_basis="Sonnet判定",
        label_basis_detail=f"S0_USER_CHECK {kk}: 要約MAJORだが境界・過剰判定の疑い。ユーザー許容/不許容は未回答のため『境界=非重大側』で暫定配置(Sonnet判定)。{nm}",
        label_src=f"{S0} ({kk})", accident_type="(境界)", lang="EN", fact=ledger_fact(fid, [fl]),
        sentence=sent, context=dict(before=None, after=None, source=f"{S0}(要約文単体。記事前後文なし)"),
        sentence_locator=f"{S0}:{line_of(S0, sent[:40]) or '?'}", article_full_text="(要約文のみ。完走記事ではなく世代G02/G09/G06の最終要約)",
        notes="ユーザー回答次第で重大/非重大が変わりうる。回答後に再ラベル")

# ------------------ 非重大: 機械抽出(台帳数値一致) ------------------
def num_tokens(s):
    s = s.replace("％", "%").replace(",", "")
    return set(re.findall(r"\d+(?:\.\d+)?", s))


bad_frags = set()
for r in LM.values():
    if r["n_sev"] in ("軽微", "重大", "判断不能"):
        bad_frags.add(norm(str(r["claim_text"]))[:25])
pos_sents = {norm(c["sentence"]) for c in CASES if c["label"] == "重大"}
rnd_m = random.Random(SEED_MECH)
mech_pool = []
ARTICLES = []   # 記事単位セット
for th in THEMES:
    for arm in ("new", "old"):
        base = f"{FA}/runs/{th}/{arm}"
        if not os.path.isdir(base):
            continue
        ja = f"{base}/ja_writer/revision2.md"
        ent = [f"{base}/b1b/article.md", f"{base}/a2/article.md"]
        led = f"{base}/research_ledger/verified_fact_ledger.txt"
        stage_led = f"{FA}/stage_r/{th}/research_ledger/verified_fact_ledger.txt"
        rec = dict(theme=th, arm=arm, ledger=led if os.path.exists(led) else None, ledger_stage_r=stage_led if os.path.exists(stage_led) else None)
        n_fact = len(load_ledger(led)) if os.path.exists(led) else None
        rec["n_facts"] = n_fact
        rec["files"] = {}
        for lab, p in [("JA_R2", ja), ("EN_Adv_b1b", ent[0]), ("EN_Std_a2", ent[1])]:
            if os.path.exists(p):
                t = rd(p)
                paras = [x for x in t.split("\n") if x.strip()]
                nsent = sum(len(split_sents(x)) for x in paras if not x.startswith("#"))
                rec["files"][lab] = dict(path=p, sha256=hashlib.sha256(open(p, "rb").read()).hexdigest(), n_sentences=nsent)
            else:
                rec["files"][lab] = None
        rec["label_rows"] = sorted([k for k, v in LM.items() if v["theme"] == th and v["arm"] == arm])
        sev = {}
        for k in rec["label_rows"]:
            sev[LM[k]["n_sev"]] = sev.get(LM[k]["n_sev"], 0) + 1
        rec["label_sev_counts"] = sev
        ARTICLES.append(rec)
        if arm != "new" or not os.path.exists(led):
            pass
        # 機械抽出: EN(Adv優先)
        for lab, p in [("EN_Adv_b1b", ent[0]), ("EN_Std_a2", ent[1])]:
            if not os.path.exists(p):
                continue
            lines = rd(p).split("\n")
            for i, ln in enumerate(lines, 1):
                if ln.startswith("#") or not ln.strip():
                    continue
                sents = split_sents(ln)
                for j, s in enumerate(sents):
                    nt = num_tokens(s)
                    if not nt or len(s) < 35 or len(s) > 220:
                        continue
                    if norm(s)[:25] in bad_frags or norm(s) in pos_sents:
                        continue
                    if not os.path.exists(led):
                        continue
                    B = load_ledger(led)
                    # 台帳Factのうち、sの数値トークンを全て含むものを選ぶ
                    best = None
                    for fid, b in B.items():
                        bt = num_tokens(b["text"])
                        if nt <= bt:
                            best = fid
                            break
                    if best is None:
                        continue
                    mech_pool.append(dict(theme=th, arm=arm, lab=lab, path=p, line=i, sent=s,
                                          before=sents[j - 1] if j > 0 else None, after=sents[j + 1] if j + 1 < len(sents) else None,
                                          fid=best, ledger=led))
rnd_m.shuffle(mech_pool)
taken = {}
n_mech = 0
seen_s = set()
for m in mech_pool:
    key = (m["theme"], m["arm"])
    if taken.get(key, 0) >= 2 or n_mech >= 22 or m["sent"] in seen_s:
        continue
    taken[key] = taken.get(key, 0) + 1
    seen_s.add(m["sent"])
    n_mech += 1
    fl = ledger_fact(m["fid"], [m["ledger"]])
    add(legacy_ids=[f"MECH-{m['theme']}-{m['arm']}"], label="非重大", label_basis="機械抽出(弱ラベル)",
        label_basis_detail="記事内の数値トークンが全て台帳の同一Factに含まれる文を機械抽出。当該記事のSonnet全文照合(labels_merged)で、この文を指す軽微/重大の所見なし(文単位の人間確認ではない)",
        label_src=f"{FA}/eval/labels_merged.jsonl (theme={m['theme']}, arm={m['arm']}の所見に当該文なし)",
        accident_type="(なし)", lang="EN", fact=fl, sentence=m["sent"],
        context=dict(before=m["before"], after=m["after"], source=f"{m['path']}:{m['line']}"),
        sentence_locator=f"{m['path']}:{m['line']}", article_full_text=m["path"],
        notes="数値一致=逐語に近い正しい文の想定。ただしFact選択は数値トークン一致による機械選択(別Factの可能性あり)")

# ------------------ 合成参考セット(OPEN-233-DIRECTIONAL-MISREAD testset の人工反転14件、本KPIには入れない) ------------------
TS = json.load(open("er052_output/open233_directional_misread_trial_01/testset_01.json", encoding="utf-8"))
SYN_TYPE = {"S-12": "rollback方向反転", "S-13": "rollback方向反転", "S-11": "否定反転", "S-10": "数量時系列", "S-08": "数量時系列",
            "S-09": "数量時系列", "S-07": "数量時系列", "S-14": "数量時系列"}
SYN = []
rs = random.Random(SEED_SPLIT)
for it in TS["items"]:
    if it["role"] == "synthetic_reversal":
        SYN.append(dict(syn_id=it["id"], fact_id=it["fact_id"], ledger_text=it["ledger_fact_text"], sentence=it["article_sentence"],
                        accident_type=SYN_TYPE.get(it["id"], "数量時系列"), label="重大(人工反転)", label_basis="Fable確定(決定論置換、Trial専用)",
                        src="er052_output/open233_directional_misread_trial_01/testset_01.json (id=%s)" % it["id"],
                        origin=it["origin"], note=it["note"]))
ids = list(range(len(SYN)))
rs.shuffle(ids)
for k, i in enumerate(ids):
    SYN[i]["split"] = "dev" if k < 7 else "holdout"

# ------------------ 開発/保留 分割 ------------------
rng = random.Random(SEED_SPLIT)
groups = {}
for c in CASES:
    groups.setdefault((c["label"], c["accident_type"] if c["label"] == "重大" else "neg"), []).append(c)
for key, lst in groups.items():
    forced = [c for c in lst if c["forced_split"]]
    free = [c for c in lst if not c["forced_split"]]
    rng.shuffle(free)
    # 保留側を多めに: 保留 ≈ 60%
    n_hold_target = round(len(lst) * 0.6)
    n_hold_forced = sum(1 for c in forced if c["forced_split"] == "holdout")
    for c in forced:
        c["split"] = c["forced_split"]
    need_hold = max(0, n_hold_target - n_hold_forced)
    for k, c in enumerate(free):
        c["split"] = "holdout" if k < need_hold else "dev"
    # 重大の単独タイプ(1件)は保留へ
    if key[0] == "重大" and len(lst) == 1 and not lst[0]["forced_split"]:
        lst[0]["split"] = "holdout"
# 重大で開発側が空にならないよう、重大タイプごとに最低1件を開発側へ(人間確認済みを除く)
HUMAN = ("ユーザー確認",)
for typ in {c["accident_type"] for c in CASES if c["label"] == "重大"}:
    lst = [c for c in CASES if c["label"] == "重大" and c["accident_type"] == typ]
    if len(lst) >= 2 and not any(c["split"] == "dev" for c in lst):
        cand = [c for c in lst if c["label_basis"] not in HUMAN and not c["forced_split"]]
        if cand:
            cand[0]["split"] = "dev"

# ------------------ 出力 ------------------
for c in CASES:
    c.pop("forced_split", None)
SPLIT_INFO = dict(seed_case_id=SEED_ID, seed_split=SEED_SPLIT, seed_mech=SEED_MECH,
                  rule="(label,事故タイプ)層別の乱数分割。保留目標≈60%。人間確認済み重大4件は K03のみ開発、K01/K02/K11は保留(同型近接: K01とK03は同一Fact・同型=near_dup_group rollback_hc012)。K08/K09=保留、K12=開発。合成参考セットは別途7/7。")
out = dict(created="2026-10-09", purpose="WRITER-DEV-RISK-FLAGGER-DESIGN-01 評価用の正解集合(新規生成なし、全て過去成果物の逐語)",
           split_info=SPLIT_INFO, cases=CASES, synthetic_reference=SYN, articles=ARTICLES,
           unlocated_minor_items=[dict(tag=a, row_id=b, fragment=c) for a, b, c in UNLOCATED])
json.dump(out, open(f"{OUT}/casebank_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("cases", len(CASES), "pos", sum(c["label"] == "重大" for c in CASES), "neg", sum(c["label"] == "非重大" for c in CASES))
print("unlocated", UNLOCATED)
print("articles", len(ARTICLES))
