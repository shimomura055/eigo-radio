# -*- coding: utf-8 -*-
"""FACTLOCK-ASTRA-E2E-TRIAL-01 委任_05: 2腕E2E runner(Trial/DEV、Production経路ではない)。

旧仕様腕(old)  = er019 Production経路(Luna R0->R1->R2 -> EN Advanced/Standard、M1/M2/M3 OFF)をそのまま使う。
新仕様腕(new)  = Fact Lock R0[Luna] -> Astra R1 -> R2[系列X逐語] -> 後処理 -> ja_writer/revision2.md に置いて er019 再利用分岐へ乗せる
                 (EN: OPEN243_M1=1、Checker: OPEN233_RECLASSIFY_PROTECT_FLAGS=changed_actor)。回復手段はB1(新Writer再実行、1記事1回、Trial全体3回)。
共通: 台帳・B3が揃った状態から開始し、research/B3段は呼ばない(guardで即停止)。腕・段ごとにsubprocess分離し環境変数はホワイトリスト。
書込はtmp->rename、stage完了マーカー(state.jsonl追記専用)・追記専用費用台帳で再開可能。既存Production/Prompt/Fact Lock R0_PROMPTは無編集。
実行(例): .venv/Scripts/python.exe -X utf8 er052_factlock_astra_e2e_runner_01.py run --root <dir> --themes meta --arms old,new --worker-id 1 [--stub]
内部: stage <name> / er019-shim <er019 args>(子processとして起動される)。E2E_STUB=1 は G0 dry-run 専用(API呼び出し0)。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TRIAL_ID = "FACTLOCK-ASTRA-E2E-TRIAL-01"
TRIAL_ROOT = "er052_output/factlock_astra_e2e_trial_01"
ASTRA_MODEL = "gpt-6-astra"
# 系列Xユーザーメッセージ(astra_revise_matrix_01/02 run_matrix*.py USER_TMPL の逐語。変更禁止)
USER_TMPL = "以下の記事:\n\n{body}\n\n事実は変えずにエンターテイメント性をもっと上げた記事にReviseください。長さは800〜1000字程度でお願いします。"
EXIT_RECHECK, EXIT_FORBIDDEN, EXIT_TAG_LEAK, EXIT_STOP, EXIT_PROVENANCE = 42, 44, 45, 46, 47
SPEC_FILES = ("B3_ANNOTATION_SPEC_v2_ANNOTATOR.md", "ANNOTATION_DELEGATION_TEMPLATE_v2.md", "B3_ANNOTATION_SPEC_v2.md")

_FL, _B3, _W = ("er052_output/factlock_writer_trial_01", "er052_output/open233_b3_trial_01/runs", "er052_output/gpt6_wiring_e2e_01/run_02")
FROZEN = {   # 旧4の凍結入力(DESIGN_E2E_01.md 2節の表。sha256先頭16桁は実測)。台帳は常にこの凍結値に固定する
    "meta": dict(ledger=f"{_FL}/runs/meta/control/b2__factlock__r1/research_ledger/verified_fact_ledger.txt", ledger16="ea0ce587e605beea",
                 b3_dir=f"{_B3}/meta/nb/V0/b2/storyline_b3", b3_16="055b1385b6db97e9", cross=f"{_B3}/meta/nb/V0/b2/research_ledger/verified_fact_ledger.txt",
                 annotated=f"{_FL}/briefs/meta/b2/selected_brief_factlock.md"),
    "hormuz": dict(ledger=f"{_FL}/runs/hormuz/control/b2__factlock__r1/research_ledger/verified_fact_ledger.txt", ledger16="9bd6834e68e7e437",
                   b3_dir=f"{_B3}/hormuz/nb/V0/b2/storyline_b3", b3_16="e1f892dffb7ff3cf", cross=f"{_B3}/hormuz/nb/V0/b2/research_ledger/verified_fact_ledger.txt",
                   annotated=f"{_FL}/briefs/hormuz/b2/selected_brief_factlock.md"),
    "space_weapons": dict(ledger=f"{_FL}/runs/space_weapons/control/b2__factlock__r1/research_ledger/verified_fact_ledger.txt", ledger16="f172a253f24b99d6",
                          b3_dir=f"{_B3}/space_weapons/nb/V0/b2/storyline_b3", b3_16="e29575ffe46ba132",
                          cross=f"{_B3}/space_weapons/nb/V0/b2/research_ledger/verified_fact_ledger.txt",
                          annotated=f"{_FL}/briefs/space_weapons/b2/selected_brief_factlock.md"),
    "small_bag": dict(ledger=f"{_W}/research_ledger/verified_fact_ledger.txt", ledger16="0cc8ca3f2e73a1f9", b3_dir=f"{_W}/storyline_b3",
                      b3_16="55bb9ba3ef209214", cross=None, annotated=f"{_FL}/astra_revise_matrix_02/inputs/small_bag/selected_brief_factlock.md"),
}
OLD_STAGES = ["old_ja", "old_ii", "old_adv", "old_std", "old_shadow", "old_check_adv", "old_check_std"]
NEW_JA = ["new_r0", "new_r1", "new_r2", "new_ii"]
NEW_STAGES = NEW_JA + ["new_en_adv", "new_en_std", "new_shadow", "new_check_adv", "new_check_std"]
EST = {"ja": 1.5, "r0": 1.5, "astra": 16.0, "ii": 0.5, "en": 1.0, "shadow": 3.0, "check": 6.0}   # 予約用の見積(円、見積であり実測ではない)
STAGE_OUT = {"old_ja": ["ja_writer/revision2.md"], "old_ii": ["telemetry/ii.json"], "old_adv": ["b1b/article.md"], "old_std": ["a2/article.md"],
             "old_shadow": ["telemetry/shadow.json"], "old_check_adv": ["checker/advanced.json"], "old_check_std": ["checker/standard.json"],
             "new_r0": ["new_writer/r0.md", "new_writer/r0_meta.json"], "new_r1": ["new_writer/r1.p1.md", "new_writer/r1_fc.json"],
             "new_r2": ["ja_writer/revision2.md", "new_writer/r2_fc.json"], "new_ii": ["telemetry/ii.json"], "new_en_adv": ["b1b/article.md"],
             "new_en_std": ["a2/article.md"], "new_shadow": ["telemetry/shadow.json"], "new_check_adv": ["checker/advanced.json"],
             "new_check_std": ["checker/standard.json"]}
ARM_FLAGS = {"old": {}, "new": {"OPEN243_M1": "1", "OPEN233_RECLASSIFY_PROTECT_FLAGS": "changed_actor"}}
FLAG_KEYS = ("OPEN243_M1", "OPEN243_M2", "OPEN233_RECLASSIFY_PROTECT_FLAGS", "OPEN243_G3_TELEMETRY_PATH")
BASE_ENV = ("PATH", "SYSTEMROOT", "SystemRoot", "TEMP", "TMP", "USERPROFILE", "HOME", "APPDATA", "LOCALAPPDATA", "COMSPEC", "PATHEXT", "WINDIR",
            "OPENAI_API_KEY", "OPENAI_ORG_ID", "OPENAI_BASE_URL", "GEMINI_API_KEY", "GOOGLE_API_KEY", "PYTHONPATH", "VIRTUAL_ENV", "HTTP_PROXY",
            "HTTPS_PROXY", "NO_PROXY", "SSL_CERT_FILE", "REQUESTS_CA_BUNDLE")
FORBIDDEN_TAGS = {"research", "ledger", "storyline_b3"}


class GlobalStop(RuntimeError):
    pass


class ProvenanceViolation(RuntimeError):
    pass


class TagLeak(RuntimeError):
    pass


class ForbiddenStageCall(BaseException):   # except Exception に捕まらないようBaseException
    pass


class StopAfterR0(BaseException):
    pass


# ------------------------------------------------------------ 共通I/O(tmp->rename)
def sha_text(s: str) -> str:
    return hashlib.sha256((s or "").encode("utf-8")).hexdigest()


def sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha_file(p: str) -> str:
    with open(p, "rb") as f:
        return sha_bytes(f.read())


def sha_file_lf(p: str) -> str:
    with open(p, "rb") as f:
        return sha_bytes(f.read().replace(b"\r\n", b"\n"))


def rd(p: str) -> str:
    with open(p, encoding="utf-8", newline="") as f:
        return f.read()


def rdt(p: str) -> str:
    """API/Productionへ渡す文章の読込。er019/efamと同じtext mode(CRLF->LF)。コピー・sha照合は rd/sha_file(バイト保存)を使う。"""
    with open(p, encoding="utf-8") as f:
        return f.read()


def rj(p: str):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def wt(p: str, text: str) -> None:
    os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    tmp = f"{p}.tmp{os.getpid()}"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    os.replace(tmp, p)


def wj(p: str, obj) -> None:
    wt(p, json.dumps(obj, ensure_ascii=False, indent=2, default=str))


def append_jsonl(p: str, obj) -> None:
    os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    with open(p, "ab") as f:
        f.write((json.dumps(obj, ensure_ascii=False, default=str) + "\n").encode("utf-8"))


def read_jsonl(p: str) -> list:
    if not os.path.exists(p):
        return []
    out = []
    for line in rd(p).splitlines():
        if line.strip():
            out.append(json.loads(line))
    return out


def stage_ok(p: str) -> bool:
    """出力が存在・非空・NUL無し・(.jsonなら)JSON妥当。"""
    try:
        with open(p, "rb") as f:
            b = f.read()
        if not b.strip() or b"\x00" in b:
            return False
        if p.endswith(".json"):
            json.loads(b.decode("utf-8"))
        return True
    except (OSError, ValueError):
        return False


# ------------------------------------------------------------ 決定論の部品((b)(c)(e))
TAG_LEAK_RE = re.compile(r"【\s*(?:事実|[FＦ]|中核数値|周辺数値)[^】\n]{0,30}】")
ECHO_RE = re.compile(r"これ[、,]?\s*ちょっと\s*面白くない[？?]")


def strip_markdown(raw: str) -> str:
    """er052_step2_astra_r3_01_run.strip_markdown と同一(テストで同一性を確認)。"""
    out = []
    for ln in raw.replace("\r\n", "\n").split("\n"):
        s = ln.rstrip()
        if re.fullmatch(r"\s*(-{3,}|\*{3,}|_{3,})\s*", s):
            continue
        s = re.sub(r"^\s{0,3}#{1,6}\s*", "", s)
        s = re.sub(r"^\s*[-*+]\s+", "", s)
        s = s.replace("**", "").replace("__", "")
        out.append(s)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip() + "\n"


def dash_to_comma(t: str) -> str:
    return re.sub(r"[—―]{1,3}", "、", t)


def postprocess_ja(raw: str) -> str:
    """(e) Astra出力の後処理(決定論): strip_markdown -> 「……」「…」を文末は「。」文中は「、」 -> 「——」を「、」。"""
    import er003_audio_tts_asr_safety as safety
    return dash_to_comma(safety.normalize_ellipsis_pause_ja(strip_markdown(raw)))


def assert_no_tag_leak(text: str) -> str:
    if TAG_LEAK_RE.search(text or ""):
        raise TagLeak(f"タグ類が残存: {TAG_LEAK_RE.findall(text)[:3]}")
    return text


def clean_ja_for_next(text: str) -> str:
    """(c) 【事実N】等の除去の単一経路。初回生成・B1回復・EN段手前の全てがここを通る。残存があればTagLeak。
    ニュース本文に元からある「【速報】」等はタグではないので残す(残存「【」の件数は測定として r0_meta に記録)。"""
    import er052_factlock_writer_trial_01_run as fl
    return assert_no_tag_leak(fl.strip_tags(text))


def detect_r0_echo(text: str) -> dict:
    """(b) OPEN-175 R0冒頭復唱の検出のみ(修正しない)。タイトル行(最初の非空行)を除いた本文で判定。"""
    lines = [l for l in (text or "").split("\n") if l.strip()]
    body = "\n".join(lines[1:])
    return {"echo_anywhere": bool(ECHO_RE.search(body)), "echo_in_head120": bool(ECHO_RE.search(body[:120])), "n": len(ECHO_RE.findall(body))}


def parse_brief_md(text: str):
    """er052_open233_polysemy_nb_dev_01.parse_brief_md と同一仕様(テストで同一性を確認)。"""
    text = text.replace("\r\n", "\n")      # 実ファイルがCRLFでも親(dev.parse_brief_md はtext mode読込でLF化)と同じ結果にする
    h1, h2 = "## Storyline\n", "\n## Selected Facts\n"
    if h1 not in text or h2 not in text:
        raise ValueError("brief-mdが『## Storyline』『## Selected Facts』形式でない")
    storyline, facts = text.split(h1, 1)[1].split(h2, 1)
    storyline, facts = storyline.strip(), facts.strip("\n")
    if not storyline or not facts.strip():
        raise ValueError("brief-mdのStorylineまたはFactsが空")
    return storyline, facts


def md_facts_of_json(jo: dict) -> str:
    """fact_selection_evidence.json の selected_fact_brief_text から、build_selected_brief_markdown と同じ規則(先頭がStorylineと
    完全一致なら除去)で selected_brief.md の『## Selected Facts』本文を再構成する。"""
    t, story = jo.get("selected_fact_brief_text", ""), jo.get("selected_storyline", "")
    return (t[len(story):].lstrip("\n") if story and t.startswith(story) else t).strip("\n")


def annotated_json_from(jo: dict, annotated_md: str) -> dict:
    """注記版JSONが未着の場合の仮生成: 原JSONのselected_fact_brief_textの『Facts部』だけを注記版briefのFacts部へ差し替える(Storyline重複頭部は保持)。"""
    t, story, new_facts = jo["selected_fact_brief_text"], jo.get("selected_storyline", ""), parse_brief_md(annotated_md)[1]
    head = ""
    if story and t.startswith(story):
        rest = t[len(story):]
        head = story + rest[:len(rest) - len(rest.lstrip("\n"))]
    return {**jo, "selected_fact_brief_text": head + new_facts}


def dryrun_annotate(brief_md: str) -> str:
    """dry-run専用の仮注記(v2注記仕様の成果物ではない)。Selected Facts節で、箇条書き行は行頭「- 」の直後へ、地の文の行は
    文末「。」の直後に改行と「- 」を入れて、それぞれ【事実N】を連番で足すだけ。仕様の許す挿入(節先頭行/「。\n」直後の「- 」、
    「。」直後の「\n- 」)の位置だけに限る(許されない位置の文は無注記のまま)。Storyline重複行・素材行は対象外。"""
    out, n, in_f, seen, prev = [], 0, False, False, ""
    for ln in brief_md.split("\n"):
        cr = "\r" if ln.endswith("\r") else ""
        core = ln[:-1] if cr else ln
        if core.strip() == "## Selected Facts":
            in_f, seen, prev = True, False, ""
        elif in_f and core.startswith("## "):
            in_f = False
        elif in_f and core.strip() and not core.startswith(("Storyline：", "素材:")):
            if core.startswith("- "):
                n += 1
                new_core = f"- 【事実{n}】" + core[2:]
            else:
                parts, tagged = re.split(r"(?<=。)(?![」』）]|$)", core), []
                for k, ptxt in enumerate(parts):
                    if k > 0 or (not seen) or prev.endswith("。"):    # 行頭の「- 」が許される位置か
                        n += 1
                        tagged.append(f"- 【事実{n}】{ptxt}")
                    else:
                        tagged.append(ptxt)
                new_core = "\n".join(tagged)
            prev, seen, core = core, True, new_core
        elif in_f and core.strip():
            prev, seen = core, True
        else:
            prev = core if core.strip() else ""
        out.append(core + cr)
    if n == 0:
        raise GlobalStop("[STOP] dry-run仮注記: Selected Facts節に注記できる行が無い")
    return "\n".join(out)


def make_fixture(fid: str, ledger: str, article: str, ja: str) -> dict:
    """動的fixture(baseline_parsed=None)。キー集合は er050.load_audit_fixture の戻りと同一(テストで確認)。"""
    return {"id": fid, "source_path": "dynamic(E2E生成記事)", "source_sha256": None, "ledger_text": ledger, "article_text": article,
            "source_article_text": ja, "include_related_fact_id": True, "hook_aware": False, "gold_note": "E2E generated (no gold)",
            "baseline_parsed": None}


def make_instance(fx: dict) -> dict:
    return {"instance_id": fx["id"], "group": "e2e", "fixture": fx, "stage1_mode": "fresh", "stage1_source": None,
            "substitute_baseline_on_stage1_miss": False, "s1u_eligible": False, "expected_group_label": "E2E generated"}


# ------------------------------------------------------------ 単価・費用((k))
def _prices(snapshot: str = "er005_output/cost_baseline_01/pricing_snapshot.json"):
    return rj(os.path.join(HERE, snapshot))["prices"]


def row_cost_usd(rec: dict, prices=None) -> float:
    """raw_usage_logの1行の費用(USD)。単価未登録はGlobalStop(fail-closed)。efam.compute_cost_jpy_so_farと同じ算式(cached割引なし=安全側)。"""
    if rec.get("provider") != "openai" or not (rec.get("model_id") or rec.get("model")):
        return 0.0
    prices = prices or _prices()
    model = rec.get("model_id") or rec.get("model")
    if model.startswith(ASTRA_MODEL):
        model = ASTRA_MODEL

    def price(m, meter):
        for p in prices:
            if p["provider"] == "openai" and p["model"] == m and p["meter"] == meter and p.get("tier", "Standard") == "Standard":
                return p["price"]
        raise GlobalStop(f"[STOP] 単価未登録model: openai/{m} meter={meter}(PricingNotFoundError相当)")
    usd = (rec.get("input_tokens") or 0) * price(model, "input_tokens") / 1e6 + (rec.get("output_tokens") or 0) * price(model, "output_tokens") / 1e6
    ws = rec.get("web_search_call_count") or 0
    if ws:
        usd += ws * price("N/A (tool, all models)", "web_search_call") / 1000
    return usd


def arm_cost(arm_dir: str, astra_factor: float = 1.5, usd_jpy: float = 160.0) -> tuple:
    """(raw_jpy, guard_jpy)。arm dir直下の raw_usage_log*.jsonl 全ての合計。astra行はguardでのみ x astra_factor。"""
    prices, raw, guard = _prices(), 0.0, 0.0
    for fn in sorted(os.listdir(arm_dir)) if os.path.isdir(arm_dir) else []:
        if fn.startswith("raw_usage_log") and fn.endswith(".jsonl"):
            for r in read_jsonl(os.path.join(arm_dir, fn)):
                j = row_cost_usd(r, prices) * usd_jpy
                raw += j
                guard += j * (astra_factor if str(r.get("model_id") or "").startswith(ASTRA_MODEL) else 1.0)
    return raw, guard


class BudgetGuard:
    """(k) 横断予算予約: worker別の追記専用台帳(ledger_costs_worker{N}.jsonl)を全workerぶん合算し、各API段の前に
    (確定額+実行中予約+この段の見積)が上限を超えるならGlobalStop。astra分は請求照合までx1.5(guard額)。"""

    def __init__(self, root: str, worker_id: int, cap: float = 1000.0, alert: float = 800.0, astra_factor: float = 1.5):
        self.root, self.wid, self.cap, self.alert, self.f = root, worker_id, cap, alert, astra_factor
        self.path = os.path.join(root, f"ledger_costs_worker{worker_id}.jsonl")

    def entries(self) -> list:
        out = []
        if os.path.isdir(self.root):
            for fn in sorted(os.listdir(self.root)):
                if fn.startswith("ledger_costs_worker") and fn.endswith(".jsonl"):
                    out += read_jsonl(os.path.join(self.root, fn))
        return out

    def totals(self) -> dict:
        es = self.entries()
        settled = sum(e["jpy_guard"] for e in es if e["kind"] == "settle")
        released = {e["id"] for e in es if e["kind"] == "release"}
        open_res = sum(e["jpy_guard"] for e in es if e["kind"] == "reserve" and e["id"] not in released)
        return {"settled_guard_jpy": round(settled, 4), "open_reserved_jpy": round(open_res, 4), "total_jpy": round(settled + open_res, 4),
                "settled_raw_jpy": round(sum(e["jpy_raw"] for e in es if e["kind"] == "settle"), 4)}

    def reserve(self, theme: str, arm: str, stage: str, est: float, astra: bool = False) -> str:
        est_g = est * (self.f if astra else 1.0)
        t = self.totals()
        if t["total_jpy"] + est_g > self.cap:
            raise GlobalStop(f"[BUDGET_HARD_STOP] 累計{t['total_jpy']:.2f}+見積{est_g:.2f} > 上限{self.cap}(stage={theme}/{arm}/{stage})")
        rid = f"{self.wid}-{int(time.time() * 1000)}-{theme}-{arm}-{stage}"
        append_jsonl(self.path, {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "kind": "reserve", "id": rid, "theme": theme, "arm": arm,
                                 "stage": stage, "jpy_guard": est_g, "jpy_raw": est})
        return rid

    def settle(self, rid: str, theme: str, arm: str, stage: str, raw: float, guard: float) -> None:
        now = time.strftime("%Y-%m-%dT%H:%M:%S")
        append_jsonl(self.path, {"ts": now, "kind": "release", "id": rid, "theme": theme, "arm": arm, "stage": stage, "jpy_guard": 0.0, "jpy_raw": 0.0})
        append_jsonl(self.path, {"ts": now, "kind": "settle", "id": rid, "theme": theme, "arm": arm, "stage": stage, "jpy_guard": round(guard, 4),
                                 "jpy_raw": round(raw, 4)})

    def alert_reached(self) -> bool:
        return self.totals()["total_jpy"] >= self.alert


_SCRIPTS = ("er052_factlock_astra_e2e_runner_01.py", "er052_factlock_astra_e2e_stub_01.py", "er019_family_x_entertainment_production_runner_01.py",
            "er019_family_x_ja_writer_o_r1_r2_01.py", "er019_family_x_storyline_b3_fact_selection_01.py", "er012_e_family_entertainment_two_level_runner_01.py",
            "er052_factlock_writer_trial_01_run.py", "er052_open233_self_recovery_flow_runner_01.py", "er052_open233_stage1_reclassify_01.py",
            "er003_v1_en_direct_vfl_01_generate.py", "er003_v1_n3_01_advanced_adaptation_generate.py", "er003_v1_n3_01_standard_a2_generate.py")


def script_shas() -> dict:
    """provenance用: 実行する全スクリプトのsha256(LF正規化)。再開時に前回と同一であること(5-4)を確認する。"""
    return {n: sha_file_lf(os.path.join(HERE, n)) for n in _SCRIPTS if os.path.exists(os.path.join(HERE, n))}


def record_provenance(ctx, arm: str, ad: str, stage: str, env: dict) -> None:
    """腕・段ごとのprovenance(フラグ実値・スクリプトsha256)を追記。再開時にスクリプトが変わっていたらSTOP(--allow-script-changeで記録のみ)。"""
    pp, cur = f"{ad}/provenance.jsonl", script_shas()
    prev = read_jsonl(pp)
    if prev and prev[0]["scripts"] != cur:
        diff = sorted(k for k in set(cur) | set(prev[0]["scripts"]) if cur.get(k) != prev[0]["scripts"].get(k))
        if not ctx.allow_script_change:
            raise GlobalStop(f"[STOP] スクリプトsha256が前回と不一致(事前登録の変更禁止違反、Fable判断要): {diff}")
        ArmState(ad).add("script_changed", files=diff)
    append_jsonl(pp, {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "stage": stage, "arm": arm, "stub": ctx.stub, "scripts": cur,
                      "flags": {k: env.get(k) for k in FLAG_KEYS}, "python": sys.version.split()[0]})


def free_mem_gb():
    try:
        import ctypes

        class MS(ctypes.Structure):
            _fields_ = [("l", ctypes.c_ulong), ("load", ctypes.c_ulong), ("tp", ctypes.c_ulonglong), ("ap", ctypes.c_ulonglong),
                        ("tv", ctypes.c_ulonglong), ("av", ctypes.c_ulonglong), ("ex1", ctypes.c_ulonglong), ("ex2", ctypes.c_ulonglong),
                        ("ex3", ctypes.c_ulonglong)]
        m = MS()
        m.l = ctypes.sizeof(MS)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
        return m.ap / 2 ** 30
    except Exception:  # noqa: BLE001
        return None


def wait_memory(min_gb: float = 4.0, max_wait_min: float = 60.0) -> None:
    t0 = time.time()
    while True:
        g = free_mem_gb()
        if g is None or g >= min_gb:
            return
        if time.time() - t0 > max_wait_min * 60:
            raise GlobalStop(f"[STOP] 空き物理メモリ{g:.1f}GB<{min_gb}GBが{max_wait_min}分継続")
        time.sleep(20)


# ------------------------------------------------------------ 腕状態(追記専用マーカー)
class ArmState:
    def __init__(self, arm_dir: str):
        self.path = os.path.join(arm_dir, "state.jsonl")

    def add(self, ev: str, **kw) -> None:
        append_jsonl(self.path, {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "ev": ev, **kw})

    def events(self) -> list:
        return read_jsonl(self.path)

    def status(self, stage: str):
        st = None
        for e in self.events():
            if e["ev"] in ("stage_done", "stage_stop", "stage_failed") and e.get("stage") == stage:
                st = e["ev"][6:]
            elif e["ev"] == "reset" and stage in e.get("stages", []):
                st = None
        return st

    def count(self, ev: str) -> int:
        return sum(1 for e in self.events() if e["ev"] == ev)


def assert_arm_env(arm: str, env: dict) -> None:
    """腕のフラグが期待値と一致すること(不一致=provenance違反、全体STOP)。M2は両腕OFF。"""
    exp = ARM_FLAGS[arm]
    bad = {k: (env.get(k), exp.get(k)) for k in ("OPEN243_M1", "OPEN243_M2", "OPEN233_RECLASSIFY_PROTECT_FLAGS") if env.get(k) != exp.get(k)}
    if bad:
        raise ProvenanceViolation(f"[STOP] 腕{arm}のフラグが期待と不一致(actual,expected): {bad}")


def build_env(ctx, arm: str, arm_dir: str) -> dict:
    env = {k: os.environ[k] for k in BASE_ENV if k in os.environ}
    env.update(PYTHONUTF8="1", PYTHONIOENCODING="utf-8", E2E_ARM=arm, E2E_STUB_DIR=arm_dir, **ARM_FLAGS[arm])
    env["OPEN243_G3_TELEMETRY_PATH"] = os.path.join(arm_dir, "telemetry", "g3_telemetry.jsonl")
    if ctx.stub:
        env["E2E_STUB"] = "1"
        if os.environ.get("E2E_STUB_SCENARIO"):
            env["E2E_STUB_SCENARIO"] = os.environ["E2E_STUB_SCENARIO"]
    assert_arm_env(arm, env)
    return env


# ------------------------------------------------------------ G0照合・入力準備
def g0_check(shared: str, cfg: dict) -> dict:
    """G0: 台帳sha・B3 md/JSON sha・strip後一致・JSON内容一致・宇宙兵器台帳一致・仕様ファイルsha。FAILが1つでもあれば pass=False。"""
    sys.path.insert(0, os.path.join(HERE, TRIAL_ROOT))
    import b3_annotation_check_01 as chk
    r, ok = {"checks": {}, "substitutions": cfg.get("substitutions", [])}, True

    def put(name, passed, **kw):
        nonlocal ok
        r["checks"][name] = {"pass": bool(passed), **kw}
        ok = ok and bool(passed)
    L, B, AB = rd(f"{shared}/ledger.txt"), rd(f"{shared}/brief_original.md"), rd(f"{shared}/brief_annotated.md")
    lp = f"{shared}/ledger.txt"
    if cfg.get("ledger_frozen"):     # 旧4: 台帳は凍結ファイル(raw sha256先頭16桁を固定値と照合)と同一内容(LF正規化)であること
        put("ledger_frozen_file_integrity", sha_file(cfg["ledger_frozen"])[:16] == cfg["ledger16"], sha256=sha_file(cfg["ledger_frozen"]),
            expected16=cfg["ledger16"])
        put("ledger_equals_frozen", sha_file_lf(lp) == sha_file_lf(cfg["ledger_frozen"]), sha256_lf=sha_file_lf(lp), sha256_raw=sha_file(lp))
    else:
        put("ledger_sha256_recorded", True, sha256=sha_file(lp), sha256_lf=sha_file_lf(lp), note="新6: 凍結pinはmanifestで照合")
    put("brief_original_sha256", cfg.get("b3_16") is None or sha_file(f"{shared}/brief_original.md")[:16] == cfg["b3_16"],
        sha256=sha_file(f"{shared}/brief_original.md"), expected16=cfg.get("b3_16"))
    ca = chk.check_a(B, AB)
    put("annotated_strip_equals_original", ca["status"] in ("PASS", "PASS_LAYOUT_NORMALIZED"), status=ca["status"],
        strict_equal=ca["strict_equal_after_strip"], reason=ca["reason"])
    jo, ja = rj(f"{shared}/fact_selection_evidence_original.json"), rj(f"{shared}/fact_selection_evidence_annotated.json")
    story, facts = parse_brief_md(B)
    put("json_original_matches_md", md_facts_of_json(jo) == facts.strip("\n") and jo.get("selected_storyline", "").strip() == story,
        json_sha256=sha_file(f"{shared}/fact_selection_evidence_original.json"))
    cj = chk.check_json(ja, jo, chk.norm_nl(B))
    if cfg.get("annotated_json_auto"):    # v2は注記版JSONの生成手順を定義していない。自動導出JSONは整列検査をskip(EN段はshimで案Bを無効化しbrief文を使わない)
        put("annotated_json_vs_original", True, skipped="auto-derived annotated JSON(v2未定義)", would_be_status=cj["status"], reason=cj.get("reason"))
    else:
        put("annotated_json_vs_original", cj["status"] == "PASS", notes=cj.get("notes"), aligned=cj.get("aligned"), reason=cj.get("reason"),
            other_keys_identical=cj.get("other_keys_identical"))
    put("annotated_json_tags_equal_md", cj.get("fact_tags") == chk.check_d(AB)["fact_numbers"])
    if cfg.get("cross"):
        put("ledger_cross_equal", sha_file_lf(cfg["cross"]) == sha_file_lf(lp), cross=cfg["cross"])
    man = cfg.get("manifest") or {}
    for key, fn in (("ledger_sha256", "ledger.txt"), ("brief_sha256", "brief_original.md"), ("json_sha256", "fact_selection_evidence_original.json"),
                    ("annotated_brief_sha256", "brief_annotated.md"), ("annotated_json_sha256", "fact_selection_evidence_annotated.json")):
        for suffix, fn_sha in (("", sha_file), ("_lf", sha_file_lf)):     # manifestのキーは raw または _lf(LF正規化)
            if man.get(key + suffix):
                put(f"manifest_{key}{suffix}", fn_sha(f"{shared}/{fn}") == man[key + suffix], expected=man[key + suffix])
    if os.path.exists(f"{shared}/annotation.json"):
        full = chk.run(B, AB, L, rj(f"{shared}/annotation.json"), ja, jo)
        put("b3_annotation_full_check", full["verdict"] == "PASS", verdict=full["verdict"])
    spec_dir = os.path.join(HERE, TRIAL_ROOT)
    rec = rj(os.path.join(spec_dir, "B3_SPEC_V2_SHA256.json"))["sha256"]
    r["spec_sha256"] = {n: {"recorded": rec.get(n), "raw": sha_file(os.path.join(spec_dir, n)), "lf_normalized": sha_file_lf(os.path.join(spec_dir, n))}
                        for n in SPEC_FILES}
    put("spec_sha256_matches_raw_or_lf", all(v["recorded"] in (v["raw"], v["lf_normalized"]) for v in r["spec_sha256"].values()))
    r["pass"] = ok
    return r


def prepare_theme(ctx, theme: str) -> dict:
    """共有dir(shared/)と腕dirへ台帳・B3・注記版を配置しG0を実施。入力は inputs/<theme>/ 優先。凍結fallbackと仮注記は明示フラグのみ許可し記録する。"""
    td, subs = f"{ctx.root}/{theme}", []
    sh = f"{td}/shared"
    d, fz = f"{ctx.inputs_dir}/{theme}", FROZEN.get(theme)
    src = {"ledger": f"{d}/ledger.txt", "brief": f"{d}/selected_brief.md", "json": f"{d}/fact_selection_evidence.json",
           "annotated": f"{d}/selected_brief_annotated.md", "annotated_json": f"{d}/fact_selection_evidence_annotated.json",
           "sidecar": f"{d}/annotation.json", "topic": f"{d}/topic.txt"}
    sr, sr_man, from_sr = f"{ctx.stage_r_dir}/{theme}", {}, False       # 委任_06(Stage R)の出力は読取のみ
    if not os.path.exists(src["ledger"]) and os.path.exists(f"{sr}/research_ledger/verified_fact_ledger.txt"):
        src["ledger"] = f"{sr}/research_ledger/verified_fact_ledger.txt"
        subs.append("ledger=Stage R出力から取得")
    if not os.path.exists(src["brief"]) and os.path.exists(f"{sr}/storyline_b3/selected_brief.md"):
        src["brief"], src["json"], from_sr = f"{sr}/storyline_b3/selected_brief.md", f"{sr}/storyline_b3/fact_selection_evidence.json", True
        subs.append("B3=Stage R出力(委任_06)から取得")
        pins = os.path.join(ctx.stage_r_dir, "FROZEN_INPUTS_SHA256.json")
        t = (rj(pins).get("themes") or {}).get(theme) if os.path.exists(pins) else None
        if t:   # Stage Rが記録した凍結sha(LF正規化)と照合する
            sr_man = {"ledger_sha256_lf": t["ledger"]["sha256_lf"], "brief_sha256_lf": t["selected_brief.md"]["sha256_lf"],
                      "json_sha256_lf": t["fact_selection_evidence.json"]["sha256_lf"]}
    if fz:   # 旧4の台帳は常に凍結値へ固定(不一致はG0でFAIL)
        if not os.path.exists(src["ledger"]):
            src["ledger"] = os.path.join(HERE, fz["ledger"])
            subs.append("ledger=凍結台帳を使用(旧4は台帳凍結)")
        if ctx.allow_frozen and not os.path.exists(src["brief"]):
            src["brief"], src["json"] = os.path.join(HERE, fz["b3_dir"], "selected_brief.md"), os.path.join(HERE, fz["b3_dir"], "fact_selection_evidence.json")
            subs.append("B3=凍結B3で代用(委任_06の再生成B3が未着の場合のdry-run用)")
    frozen_b3 = bool(fz) and os.path.abspath(src["brief"]) == os.path.abspath(os.path.join(HERE, fz["b3_dir"], "selected_brief.md"))
    if ctx.substitute_annotation and not os.path.exists(src["annotated"]) and os.path.exists(src["brief"]):
        if frozen_b3:
            src["annotated"] = os.path.join(HERE, fz["annotated"])
            subs.append("注記版brief=旧手付け注記(selected_brief_factlock.md)で代用(dry-run用。v2注記仕様の成果物ではない)")
        else:
            src["annotated"] = f"{td}/shared/_dryrun_annotated_brief.md"
            wt(src["annotated"], dryrun_annotate(rd(src["brief"])))
            subs.append("注記版brief=dry-run用の機械的な仮注記(箇条書きへ【事実N】を足すだけ。v2注記仕様の成果物ではない)")
    for k in ("ledger", "brief", "json", "annotated"):
        if not os.path.exists(src[k]):
            raise GlobalStop(f"[STOP] 入力欠落 {theme}: {k}={src[k]}(research/B3段はrunnerでは実行しない)")
    wt(f"{sh}/ledger.txt", rd(src["ledger"]))
    wt(f"{sh}/brief_original.md", rd(src["brief"]))
    wt(f"{sh}/fact_selection_evidence_original.json", rd(src["json"]))
    wt(f"{sh}/brief_annotated.md", rd(src["annotated"]))
    json_auto = not os.path.exists(src["annotated_json"])
    if not json_auto:
        wt(f"{sh}/fact_selection_evidence_annotated.json", rd(src["annotated_json"]))
    else:   # 注記版JSON未着: 原JSONの selected_fact_brief_text だけ注記版briefのFacts部へ差し替えて作る(仮)
        wj(f"{sh}/fact_selection_evidence_annotated.json", annotated_json_from(rj(src["json"]), rd(src["annotated"])))
        subs.append("注記版JSON=原JSONのselected_fact_brief_textのFacts部を注記版briefのFacts部へ差し替えて自動生成(仮)")
    if os.path.exists(src["sidecar"]):
        wt(f"{sh}/annotation.json", rd(src["sidecar"]))
    topic = rd(src["topic"]).strip() if os.path.exists(src["topic"]) else ctx.topics.get(theme, f"{theme}(topic未取得)")
    wt(f"{sh}/topic.txt", topic)
    if not os.path.exists(src["topic"]) and theme not in ctx.topics:
        subs.append("topic未取得(placeholder)")
    man = {**sr_man, **(rj(f"{d}/input_manifest.json") if os.path.exists(f"{d}/input_manifest.json") else {})}
    g0 = g0_check(sh, {"ledger16": fz["ledger16"] if fz else None, "ledger_frozen": os.path.join(HERE, fz["ledger"]) if fz else None,
                       "b3_16": fz["b3_16"] if frozen_b3 else None, "cross": fz["cross"] and os.path.join(HERE, fz["cross"]) if fz else None,
                       "substitutions": subs, "manifest": man, "annotated_json_auto": json_auto})
    wj(f"{td}/g0.json", g0)
    for arm, brief, js in (("old", "brief_original.md", "fact_selection_evidence_original.json"), ("new", "brief_annotated.md", "fact_selection_evidence_annotated.json")):
        ad = f"{td}/{arm}"
        wt(f"{ad}/research_ledger/verified_fact_ledger.txt", rd(f"{sh}/ledger.txt"))
        wt(f"{ad}/storyline_b3/selected_brief.md", rd(f"{sh}/{brief}"))
        wt(f"{ad}/storyline_b3/fact_selection_evidence.json", rd(f"{sh}/{js}"))
        os.makedirs(f"{ad}/telemetry", exist_ok=True)
    if not g0["pass"]:
        raise GlobalStop(f"[STOP] G0照合FAIL({theme}): " + ", ".join(k for k, v in g0["checks"].items() if not v["pass"]))
    return g0


# ------------------------------------------------------------ (m) 研究/B3呼び出し検出
def detect_forbidden_api(arm_dir: str, shared: str | None = None) -> list:
    f = []
    for fn in sorted(os.listdir(arm_dir)) if os.path.isdir(arm_dir) else []:
        if fn.startswith("raw_usage_log") and fn.endswith(".jsonl"):
            for r in read_jsonl(os.path.join(arm_dir, fn)):
                if (r.get("stage") in FORBIDDEN_TAGS) or (r.get("web_search_call_count") or 0) > 0:
                    f.append({"file": fn, "stage": r.get("stage"), "web_search_call_count": r.get("web_search_call_count")})
    for p in ("research_ledger/runtime_evidence.json", "research_ledger/audit/researcher_full_record.json", "storyline_b3/runtime_evidence.json"):
        if os.path.exists(os.path.join(arm_dir, p)):
            f.append({"new_artifact": p})
    if shared:
        arm = os.path.basename(arm_dir.rstrip("/\\"))
        exp = {"research_ledger/verified_fact_ledger.txt": "ledger.txt",
               "storyline_b3/selected_brief.md": "brief_original.md" if arm == "old" else "brief_annotated.md",
               "storyline_b3/fact_selection_evidence.json":
                   "fact_selection_evidence_original.json" if arm == "old" else "fact_selection_evidence_annotated.json"}
        for a, s in exp.items():
            if os.path.exists(os.path.join(arm_dir, a)) and sha_file(os.path.join(arm_dir, a)) != sha_file(os.path.join(shared, s)):
                f.append({"input_changed": a})
    return f


# ------------------------------------------------------------ 子processワーカー: Astra / 新Writer
def call_astra(client, user: str, stage: str, retries: int = 2):
    import er005_cost_logger as cl
    last = None
    for i in range(1 + retries):
        try:
            with cl.logging_context(TRIAL_ID, stage):   # service_tier指定なし(Standard同期)、previous_response_id/developerなし
                resp = client.responses.create(model=ASTRA_MODEL, reasoning={"effort": "high"}, input=[{"role": "user", "content": user}])
            if not str(getattr(resp, "model", "")).startswith(ASTRA_MODEL):
                raise ProvenanceViolation(f"[STOP] Astra段のmodelが{ASTRA_MODEL}で始まらない: {getattr(resp, 'model', None)}")
            return resp
        except ProvenanceViolation:
            raise
        except Exception as e:  # noqa: BLE001  一時エラーは最大2回再試行
            last = e
            time.sleep(0 if os.environ.get("E2E_STUB") else 3 * (i + 1))
    raise RuntimeError(f"Astra API失敗(再試行{retries}回後): {last!r}")


def fc_record(fc: dict) -> dict:
    devs = (fc["parsed"] or {}).get("deviations", [])
    ma = [d for d in devs if d.get("severity") == "MAJOR"]
    return {"overall_status": fc["parsed"].get("overall_status"), "n_major": len(ma),
            "n_minor": sum(1 for d in devs if d.get("severity") == "MINOR"), "majors": ma,
            "response_id": fc.get("response_id"), "model": fc.get("model")}


def worker_new_r0(a, ctx_dir: str, ledger: str) -> int:
    import er005_cost_logger as cl
    import er019_family_x_ja_writer_o_r1_r2_01 as jaw
    import er003_v1_en_direct_vfl_01_generate as vfl01
    import er052_factlock_writer_trial_01_run as fl
    arm_dir = ctx_dir
    storyline, facts = parse_brief_md(rdt(f"{arm_dir}/storyline_b3/selected_brief.md"))   # 注記版brief
    mf = rj(a.must_fix_file) if a.must_fix_file else None
    client = vfl01.get_client()
    saved, calls, fcs = fl.apply_factlock_patches(), [], []
    o_fresh, o_dev, o_prev = jaw.call_fresh, vfl01.run_deviation_check, jaw.call_with_previous_response_id

    def fresh(c, developer, user, effort, stage):
        r = o_fresh(c, developer, user, effort, stage)
        calls.append({"stage": stage, "response_id": r.id, "model": r.model, "text": r.output_text.strip()})
        return r

    def dev(*x, **k):
        r = o_dev(*x, **k)
        fcs.append(r)
        return r

    def stop_r1(*x, **k):
        raise StopAfterR0()
    jaw.call_fresh, vfl01.run_deviation_check, jaw.call_with_previous_response_id = fresh, dev, stop_r1
    status, err = "completed_R0_only", None
    try:
        try:
            jaw.run_ja_writer_o_r1_r2(client, storyline, facts, full_ledger_text=ledger, original_must_fix=mf)
        except StopAfterR0:
            pass
        except jaw.JAFactCheckStopError as e:   # R0のmust-fix1回後もMAJOR/記号 -> 既存どおりSTOP
            status, err = "STOP_JA_FACT_CHECK", str(e)
            wj(f"{arm_dir}/new_writer/r0_stop.json", {"stage": e.stage, "rejected_text": e.rejected_text, "must_fix_used": e.must_fix_used,
                                                      "checks": [vfl01.deviation_audit_record(c) for c in e.checks]})
    finally:
        jaw.call_fresh, vfl01.run_deviation_check, jaw.call_with_previous_response_id = o_fresh, o_dev, o_prev
        fl.restore_factlock_patches(saved)
    if status != "completed_R0_only":
        print(err)
        return EXIT_STOP
    final = calls[-1]["text"]
    clean = clean_ja_for_next(final).strip() + "\n"      # (c) 単一のstrip経路(タグ残存はTagLeak)
    wt(f"{arm_dir}/new_writer/r0_with_tags.md", final)
    wt(f"{arm_dir}/new_writer/r0.md", clean)
    facts_map = fl.parse_annotated_facts(rdt(f"{arm_dir}/storyline_b3/selected_brief.md"))
    sents = fl.split_sentences(final)
    wj(f"{arm_dir}/new_writer/r0_meta.json", {
        "writer_calls": [{k: v for k, v in c.items() if k != "text"} for c in calls], "ja_fact_checks": [fc_record(f) for f in fcs],
        "must_fix_applied": any(c["stage"].startswith("ja_original_must_fix") for c in calls), "recovery_must_fix": mf,
        "tagged_sentences": sum(1 for s in sents if s["tags"] and not s["is_title"]), "facts_in_brief": list(facts_map),
        "tags_used": sorted({t for s in sents for t in s["tags"]}), "marks_echoed": len(fl.MARK_RE.findall(final)),
        "r0_echo": detect_r0_echo(clean), "r0_sha256": sha_text(clean),
        "factlock_r0_block_sha256": sha_text(fl.build_r0_block(jaw.CONCRETENESS_CONTROL_AN3_BLOCK)), "tag_check_note": "測定のみ(STOP・再生成なし)"})
    return 0


def worker_new_astra(a, arm_dir: str, ledger: str, which: str) -> int:
    import er019_family_x_ja_writer_o_r1_r2_01 as jaw
    import er003_v1_en_direct_vfl_01_generate as vfl01
    import er003_audio_tts_asr_safety as safety
    import er005_cost_logger as cl
    client = vfl01.get_client()
    if not os.environ.get("E2E_STUB"):
        import er006_model_routing_contract_01 as routing
        routing.require_model_or_override("B1_WRITER", ASTRA_MODEL, override_reason=f"{TRIAL_ID} (Trial/DEV、Production採用ではない)")
    src = rdt(f"{arm_dir}/new_writer/r0.md") if which == "r1" else rdt(f"{arm_dir}/new_writer/r1.raw.md")   # R2の入力=R1の生出力(matrixと同一)
    user = USER_TMPL.format(body=src.strip())
    t0 = time.time()
    resp = call_astra(client, user, f"astra_{which}")
    raw = (resp.output_text or "").strip()
    p = postprocess_ja(raw)
    wt(f"{arm_dir}/new_writer/{which}.raw.md", raw)
    wj(f"{arm_dir}/new_writer/{which}.response.json", {
        "requested_model": ASTRA_MODEL, "model": resp.model, "reasoning": {"effort": "high"}, "previous_response_id_used": False,
        "developer_message": None, "service_tier": None, "user_message_sha256": sha_text(user), "response_id": resp.id,
        "sec": round(time.time() - t0, 1), "output_chars": len(raw), "symbol_gate_findings": safety.detect_prohibited_symbols(p, "ja"),
        "usage": {"input_tokens": getattr(resp.usage, "input_tokens", None), "output_tokens": getattr(resp.usage, "output_tokens", None)}})
    with cl.logging_context(TRIAL_ID, f"new_{which}_fc"):
        fc = vfl01.run_deviation_check(client, ledger, p.strip(), hook_aware=False, include_related_fact_id=True)
    rec = {**fc_record(fc), "text_sha256": sha_text(p)}
    if which == "r1":
        wt(f"{arm_dir}/new_writer/r1.p1.md", p)
        wj(f"{arm_dir}/new_writer/r1_fc.json", rec)
        return 0
    final = clean_ja_for_next(p)      # (c) revision2.mdへ置く前にもう一度単一経路を通す
    echo = detect_r0_echo(final)
    wt(f"{arm_dir}/ja_writer/original.md", rdt(f"{arm_dir}/new_writer/r0.md"))
    wt(f"{arm_dir}/ja_writer/revision1.md", rdt(f"{arm_dir}/new_writer/r1.p1.md"))
    wt(f"{arm_dir}/ja_writer/revision2.md", final)           # = er019再利用分岐に乗せる
    wj(f"{arm_dir}/new_writer/r2_fc.json", {**rec, "shadow_stop": rec["n_major"] > 0, "r2_echo_after_revision": echo,
                                            "symbol_gate_findings": safety.detect_prohibited_symbols(final, "ja")})
    return 0


def worker_ii(a, arm_dir: str, shared: str) -> int:
    """新規具体主張(ii)検出器(fl.untagged_check)を両腕のJA最終本文(+R0)へ。"""
    import er003_v1_en_direct_vfl_01_generate as vfl01
    import er005_cost_logger as cl
    import er006_model_routing_contract_01 as routing
    import er052_factlock_writer_trial_01_run as fl
    client = vfl01.get_client()
    facts = fl.parse_annotated_facts(rdt(f"{shared}/brief_annotated.md"))
    r0p = f"{arm_dir}/new_writer/r0.md" if a.arm == "new" else f"{arm_dir}/ja_writer/original.md"
    out = {"arm": a.arm, "judge_model": routing.WRITER_FACT_CHECK_MODEL}
    for name, path in (("final", f"{arm_dir}/ja_writer/revision2.md"), ("r0", r0p)):
        if os.path.exists(path):
            with cl.logging_context(TRIAL_ID, f"ii_{name}"):
                r = fl.untagged_check(client, routing.WRITER_FACT_CHECK_MODEL, f"e2e_{a.arm}_{name}", fl.split_sentences(rdt(path)), facts)
            out[name] = {"counts": r["counts"], "new_specific_claim": r["counts"].get("new_specific_claim", 0),
                         "items_new_specific": [i for i in r["items"] if i["label"] == "new_specific_claim"], "text_sha256": sha_file(path)}
    out["delta_new_specific_final_minus_r0"] = (out.get("final", {}).get("new_specific_claim", 0) - out.get("r0", {}).get("new_specific_claim", 0))
    wj(f"{arm_dir}/telemetry/ii.json", out)
    return 0


def split_adv(text: str):
    m = re.match(r"# (.*?)\n\n(.*?)\n\n## In one line\n(.*)\Z", text.strip(), flags=re.S)
    return (m.group(1), m.group(2), m.group(3)) if m else (None, None, None)


def worker_shadow(a, arm_dir: str, ledger: str) -> int:
    """影の対照(ログ専用、判定に使わない): M1(a)入力追加、M1(b)要約のみ再生成、Standard(d)のattempt1 MAJOR分類。M3は集計側で台帳から(費用0)。"""
    import er003_v1_en_direct_vfl_01_generate as vfl01
    import er003_v1_n3_01_advanced_adaptation_generate as adv_gen
    import er012_e_family_entertainment_two_level_runner_01 as efam
    import er005_cost_logger as cl
    client, ja = vfl01.get_client(), rdt(f"{arm_dir}/ja_writer/revision2.md")
    res = {"arm": a.arm, "note": "ログ専用。腕比較の結果をM1/M3単独の効果と書かない"}
    title, body, summ = split_adv(rdt(f"{arm_dir}/b1b/article.md"))
    att1 = rj(f"{arm_dir}/b1b/audit/deviation_checks/advanced_attempt1.json")
    majors = [d for d in (att1.get("parsed") or {}).get("deviations", []) if d.get("severity") == "MAJOR"]
    if title is not None:
        with cl.logging_context(TRIAL_ID, "shadow_m1a"):
            # 実際の腕と逆の入力: new(M1 ON)には旧入力(title,body)、old(M1 OFF)にはM1入力(ja_text,ledger_text)
            iol = (adv_gen.generate_family_x_in_one_line(client, title, body) if a.arm == "new"
                   else adv_gen.generate_family_x_in_one_line(client, title, body, ja_text=ja, ledger_text=ledger))
            alt = f"# {title}\n\n{body}\n\n## In one line\n{iol['text']}"
            dev = vfl01.run_deviation_check(client, ledger, alt, hook_aware=False, include_related_fact_id=True, source_article_text=ja)
        res["m1a"] = {"alt_rule": "old_input" if a.arm == "new" else "m1_input", "alt_summary": iol["text"], "alt_check": fc_record(dev),
                      "actual_attempt1_status": (att1.get("parsed") or {}).get("overall_status"), "actual_summary": summ}
        only_sum = bool(majors) and efam.open243_majors_only_in_summary(majors, summ, body)
        res["m1b"] = {"actual_attempt1_n_major": len(majors), "majors_only_in_summary": only_sum,
                      "fired_in_arm": os.path.exists(f"{arm_dir}/b1b/audit/deviation_checks/advanced_attempt2.json"),
                      "counterfactual": None}
        if only_sum:
            with cl.logging_context(TRIAL_ID, "shadow_m1b"):
                mf = efam._must_fix_from_deviations(majors)
                if a.arm == "new":     # 旧規則: Advanced本文ごと再生成1回 + EN検査1回(約0.6円/発火)
                    tr = adv_gen.generate_family_x_faithful_translation(ja, client=client, must_fix=mf)
                    i2 = adv_gen.generate_family_x_in_one_line(client, tr.title, tr.body)
                    t2 = f"# {tr.title}\n\n{tr.body}\n\n## In one line\n{i2['text']}"
                    d2 = vfl01.run_deviation_check(client, ledger, t2, hook_aware=False, include_related_fact_id=True, source_article_text=ja,
                                                   prior_issues=mf)
                    res["m1b"]["counterfactual"] = {"rule": "old_full_regen", "check": fc_record(d2)}
                else:                  # 新規則: 要約のみ再生成(open243_m1_summary_only_retry、最大2回)
                    m1 = efam.open243_m1_summary_only_retry(client, ledger_text=ledger, ja_text=ja, title=title, body=body, must_fix=mf, max_attempts=2)
                    res["m1b"]["counterfactual"] = {"rule": "m1_summary_only", "success": m1["success"], "reason": m1["reason"],
                                                    "attempts": len(m1["attempts"])}
    if os.path.exists(f"{arm_dir}/a2/audit/deviation_checks/standard_attempt1.json"):
        s1 = rj(f"{arm_dir}/a2/audit/deviation_checks/standard_attempt1.json")
        sm = [d for d in (s1.get("parsed") or {}).get("deviations", []) if d.get("severity") == "MAJOR"]
        st = rdt(f"{arm_dir}/a2/article.md")
        s_sum = st.split("## In one line\n")[-1] if "## In one line" in st else ""
        res["standard_attempt1_major"] = {"n_major": len(sm), "only_in_summary": bool(sm) and efam.open243_majors_only_in_summary(sm, s_sum, st),
                                          "summary_found": bool(s_sum), "note": "Standard側のM1効果は未測定(M1 Standardは実装しない)"}
    wj(f"{arm_dir}/telemetry/shadow.json", res)
    return 0


class RunCapExceeded(RuntimeError):
    pass


def worker_check(a, arm_dir: str, ledger: str) -> int:
    level = a.level
    art = rdt(f"{arm_dir}/{'b1b' if level == 'advanced' else 'a2'}/article.md")
    fx = make_fixture(f"{a.theme}_{a.arm}_{level}", ledger, art, rdt(f"{arm_dir}/ja_writer/revision2.md"))
    inst = make_instance(fx)
    out = f"{arm_dir}/checker/{level}.json"
    if os.environ.get("E2E_STUB"):
        import er052_factlock_astra_e2e_stub_01 as stub
        wj(out, stub.stub_check_one(inst, a.arm))
        return 0
    import er052_open233_self_recovery_flow_runner_01 as runner
    import er052_open233_e2e_acceptance_01 as old
    import er003_v1_en_direct_vfl_01_generate as vfl01
    applied = runner.apply_open233_approved_flow_switches()
    runner.assert_open233_approved_flow_switches()
    if applied.get("FLOOR_MODE") != "number_only":
        raise ProvenanceViolation(f"[STOP] FLOOR_MODEがnumber_onlyでない: {applied.get('FLOOR_MODE')}")
    cdir = f"{arm_dir}/checker/_runner"
    runner.OUT_DIR, runner.BUDGET_STATE_PATH = cdir, f"{cdir}/budget_state_{fx['id']}.json"
    runner.TOTAL_BUDGET_JPY = a.checker_cap + 5.0
    state, start = runner.load_budget_state(), 0.0
    start = state["cumulative_jpy"]

    def hook(st):
        if st["cumulative_jpy"] - start > a.checker_cap:
            raise RunCapExceeded(f"run_cost_gt_{a.checker_cap}")
    runner.RUN_CALL_HOOK = hook
    prov, t0 = old.provenance(applied), time.time()
    try:
        r = runner.run_instance(vfl01.get_client(), state, [0], inst, enable_s1u=False, stage1_cache=None, instances_subdir=f"checker/_runner/{fx['id']}")
    except RunCapExceeded as e:
        wj(out, {"instance_id": fx["id"], "aborted": True, "abort_reason": str(e), "total_cost_jpy": round(state["cumulative_jpy"] - start, 4), "provenance": prov,
                 "final_state": "ABORTED_BY_RUN_CAP"})
        return 0
    finally:
        runner.RUN_CALL_HOOK = None
    r.update(provenance=prov, waste_flags=old.post_run_waste_flags(r), provenance_violations=old.provenance_violations({**r, "provenance": prov}),
             wall_seconds=round(time.time() - t0, 3), run_cost_incl_retries_jpy=round(state["cumulative_jpy"] - start, 4))
    wj(out, r)
    return 0


# ------------------------------------------------------------ 子process: er019 shim
def worker_er019_shim(argv: list) -> int:
    arm = os.environ["E2E_ARM"]
    assert_arm_env(arm, os.environ)
    out_dir = argv[argv.index("--out-dir") + 1]
    tdir = f"{out_dir}/telemetry"
    if os.environ.get("E2E_STUB"):
        import er052_factlock_astra_e2e_stub_01 as stub
        stub.install_all()
    import er003_v1_en_direct_vfl_01_generate as vfl01  # noqa: F401
    import er012_e_family_entertainment_two_level_runner_01 as efam
    import er019_family_x_entertainment_production_runner_01 as e19
    import er019_family_x_storyline_b3_fact_selection_01 as b3

    def forbid(name):
        def f(*x, **k):
            wj(f"{tdir}/forbidden_call.json", {"call": name, "arm": arm, "ts": time.strftime("%Y-%m-%dT%H:%M:%S")})
            raise ForbiddenStageCall(name)
        return f
    efam.run_researcher_for_topic, efam.run_verification_for_topic = forbid("run_researcher_for_topic"), forbid("run_verification_for_topic")
    b3.run_storyline_b3_selection = forbid("run_storyline_b3_selection")        # (m) 研究/B3は絶対に呼ばない
    orig_once = efam._run_writer_stage_once

    def once(client, theme, ja_text, ledger_text, budget_jpy, only=None):
        try:
            return orig_once(client, theme, ja_text, ledger_text, budget_jpy, only=only)
        except efam.JARecheckRequiredError as exc:
            ev = {"arm": arm, "stage": exc.stage, "n_major": len(exc.major_deviations), "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
                  "n_ja_source": sum(1 for d in exc.major_deviations if d.get("origin") == "ja_source"), "major_deviations": exc.major_deviations}
            append_jsonl(f"{tdir}/ja_recheck_events.jsonl", ev)       # 初回(回復前)のJA_RECHECK率の記録
            wj(f"{tdir}/ja_recheck_trigger.json", ev)
            raise
    efam._run_writer_stage_once = once
    if arm == "new":      # 新腕へ旧Luna Writer(案B)を混入させない: storyline_line/selected_fact_brief_text=None で案Bを無効化
        orig_rws = efam.run_writer_stage

        def rws(client, theme, ja_text, ledger_text, budget_jpy, only=None, storyline_line=None, selected_fact_brief_text=None, _ja_recheck_attempted=False):
            assert_no_tag_leak(ja_text)                       # EN段へ渡す直前のタグ残存確認(残存ならTagLeak)
            return orig_rws(client, theme, ja_text, ledger_text, budget_jpy, only=only, storyline_line=None, selected_fact_brief_text=None)
        e19.efam.run_writer_stage = rws
    sys.argv = ["er019_family_x_entertainment_production_runner_01.py"] + argv
    try:
        e19.main()
        return 0
    except ForbiddenStageCall:
        return EXIT_FORBIDDEN
    except TagLeak as e:
        print(e)
        return EXIT_TAG_LEAK
    except efam.JARecheckRequiredError as e:
        print(f"JA_RECHECK: {e}")
        return EXIT_RECHECK
    except ProvenanceViolation as e:
        print(e)
        return EXIT_PROVENANCE
    except RuntimeError as e:
        if type(e).__name__ == "PricingNotFoundError":
            raise
        if "[STOP]" in str(e):
            wj(f"{tdir}/stage_stop.json", {"arm": arm, "message": str(e)[:1500], "ts": time.strftime("%Y-%m-%dT%H:%M:%S")})
            print(str(e))
            return EXIT_STOP
        raise


def stage_main(a) -> int:
    arm_dir = f"{a.root}/{a.theme}/{a.arm}"
    assert_arm_env(a.arm, os.environ)
    import er005_cost_logger as cl
    if os.environ.get("E2E_STUB"):
        import er052_factlock_astra_e2e_stub_01 as stub
        stub.install_all()
    cl.install(f"{arm_dir}/raw_usage_log_{a.stage}.jsonl")
    ledger, shared = rdt(f"{arm_dir}/research_ledger/verified_fact_ledger.txt"), f"{a.root}/{a.theme}/shared"
    try:
        if a.stage == "new_r0":
            return worker_new_r0(a, arm_dir, ledger)
        if a.stage in ("new_r1", "new_r2"):
            return worker_new_astra(a, arm_dir, ledger, a.stage[-2:])
        if a.stage.endswith("_ii"):
            return worker_ii(a, arm_dir, shared)
        if a.stage.endswith("_shadow"):
            return worker_shadow(a, arm_dir, ledger)
        if "_check_" in a.stage:
            a.level = "advanced" if a.stage.endswith("adv") else "standard"
            return worker_check(a, arm_dir, ledger)
    except TagLeak as e:
        print(e)
        return EXIT_TAG_LEAK
    except ProvenanceViolation as e:
        print(e)
        return EXIT_PROVENANCE
    raise SystemExit(f"unknown stage {a.stage}")


# ------------------------------------------------------------ オーケストレータ
class Ctx:
    def __init__(self, a):
        self.root, self.themes, self.arms, self.wid = a.root, [t for t in a.themes.split(",") if t], [x for x in a.arms.split(",") if x], a.worker_id
        self.stub, self.until, self.inputs_dir = a.stub, a.until, a.inputs_dir
        self.allow_frozen, self.substitute_annotation, self.stage_r_dir = a.allow_frozen_b3, a.substitute_annotation, a.stage_r_dir
        self.arm_cap, self.checker_cap, self.b1_max, self.no_mem = a.arm_cap, a.checker_cap, a.b1_total_max, a.no_mem_check
        self.allow_script_change = a.allow_script_change
        self.guard = BudgetGuard(a.root, a.worker_id, a.cap_jpy, a.alert_jpy)
        self.topics = {}
        for p in (a.topics_json or []):
            if os.path.exists(p):
                self.topics.update(rj(p))   # 委任_06の出力ディレクトリは読取のみ

    def stop_file(self):
        return f"{self.root}/STOP.json"


def launch(ctx, arm: str, arm_dir: str, args: list, log: str) -> int:
    env = build_env(ctx, arm, arm_dir)
    os.makedirs(os.path.dirname(log), exist_ok=True)
    with open(log, "ab") as lf:
        return subprocess.run([sys.executable, "-X", "utf8", os.path.join(HERE, "er052_factlock_astra_e2e_runner_01.py")] + args, env=env, cwd=HERE,
                              stdout=lf, stderr=subprocess.STDOUT, timeout=3600).returncode


def stage_kind(stage: str) -> tuple:
    """(est円, astra?)"""
    if stage in ("new_r1", "new_r2"):
        return EST["astra"], True
    for k, key in (("_check_", "check"), ("_shadow", "shadow"), ("_ii", "ii"), ("_ja", "ja"), ("_r0", "r0"), ("_en_", "en"), ("_adv", "en"), ("_std", "en")):
        if k in stage:
            return EST[key], False
    return 1.0, False


def run_stage(ctx, theme: str, arm: str, stage: str, topic: str) -> str:
    """戻り値: done / stop(記事STOP) / recheck(新腕EN段ja_source MAJOR) / failed(技術障害、2回再試行後)。全体STOPはGlobalStop。"""
    td = f"{ctx.root}/{theme}"
    ad, st = f"{td}/{arm}", ArmState(f"{td}/{arm}")
    if os.path.exists(ctx.stop_file()):
        raise GlobalStop("STOP.json 検出(他workerが全体停止)")
    outs_ok = all(stage_ok(f"{ad}/{o}") for o in STAGE_OUT[stage])
    if st.status(stage) == "done" and outs_ok:
        return "done"
    if st.status(stage) in ("stop", "failed"):
        return st.status(stage)
    if stage == "old_std" and outs_ok and stage_ok(f"{ad}/writer_run_summary.json") and rj(f"{ad}/writer_run_summary.json").get("ja_recheck_used"):
        st.add("stage_done", stage=stage, via="old_advanced_ja_recheck(案BでStandardまで生成済み)", outputs={})
        return "done"
    if st.status(stage) is None and outs_ok:      # 完了済み出力の再API呼び出しは禁止(マーカー欠落時は採用して記録)
        st.add("stage_done", stage=stage, via="adopted_existing_outputs", outputs={o: sha_file(f"{ad}/{o}") for o in STAGE_OUT[stage]})
        return "done"
    est, astra = stage_kind(stage)
    if not ctx.no_mem:
        wait_memory()
    record_provenance(ctx, arm, ad, stage, build_env(ctx, arm, ad))
    rid = ctx.guard.reserve(theme, arm, stage, est, astra)
    raw0, guard0 = arm_cost(ad, ctx.guard.f)
    sub = {"old_ja": ["--stage", "writer", "--stop-after", "writer"], "old_adv": ["--stage", "advanced"], "old_std": ["--stage", "standard"],
           "new_en_adv": ["--stage", "advanced"], "new_en_std": ["--stage", "standard"]}
    if stage in sub:
        args = ["er019-shim", "--theme", topic, "--slug", theme, "--out-dir", ad, "--budget-jpy", str(ctx.arm_cap)] + sub[stage]
    else:
        args = ["stage", stage, "--root", ctx.root, "--theme", theme, "--arm", arm, "--checker-cap", str(ctx.checker_cap)]
        if stage == "new_r0" and os.path.exists(f"{ad}/recovery/must_fix.json"):
            args += ["--must-fix-file", f"{ad}/recovery/must_fix.json"]
    rc, t0, pricing_stop = 1, time.time(), False
    try:
        for attempt in range(3):
            try:
                rc = launch(ctx, arm, ad, args, f"{ad}/logs/{stage}.log")
            except subprocess.TimeoutExpired:
                rc = 1
            if rc in (0, EXIT_RECHECK, EXIT_FORBIDDEN, EXIT_TAG_LEAK, EXIT_STOP, EXIT_PROVENANCE):
                break
            tail = rd(f"{ad}/logs/{stage}.log")[-3000:] if os.path.exists(f"{ad}/logs/{stage}.log") else ""
            if "単価未登録" in tail or "PricingNotFoundError" in tail:
                pricing_stop = True
                break
            st.add("stage_retry", stage=stage, rc=rc, attempt=attempt + 1)
    finally:
        raw1, guard1 = arm_cost(ad, ctx.guard.f)
        if stage.endswith(("check_adv", "check_std")):     # CheckerのコストはRun JSONの total_cost_jpy(runnerが計算した確定額)
            cj = f"{ad}/checker/{'advanced' if stage.endswith('adv') else 'standard'}.json"
            c = rj(cj).get("total_cost_jpy", 0.0) if stage_ok(cj) else 0.0
            ctx.guard.settle(rid, theme, arm, stage, c, c)
        else:
            ctx.guard.settle(rid, theme, arm, stage, raw1 - raw0, guard1 - guard0)
    sec = round(time.time() - t0, 1)
    bad = detect_forbidden_api(ad, f"{td}/shared")
    if rc == EXIT_FORBIDDEN or bad:
        raise GlobalStop(f"[STOP] 研究/B3呼び出し検出(凍結違反/重複支出): {theme}/{arm}/{stage} rc={rc} {bad[:3]}")
    if pricing_stop or rc in (EXIT_TAG_LEAK, EXIT_PROVENANCE):
        raise GlobalStop(f"[STOP] 単価未登録/provenance/タグ漏れ: {theme}/{arm}/{stage} rc={rc} pricing={pricing_stop}")
    n_err = sum(1 for fn in os.listdir(ad) if fn.startswith("raw_usage_log") for r in read_jsonl(f"{ad}/{fn}") if r.get("success") is False)
    if n_err > 3:
        raise GlobalStop(f"[STOP] API失敗が3件超({n_err}): {theme}/{arm}")
    if rc == EXIT_RECHECK and arm == "new":
        st.add("stage_recheck", stage=stage, sec=sec)
        return "recheck"
    if rc in (EXIT_STOP, EXIT_RECHECK):
        st.add("stage_stop", stage=stage, rc=rc, sec=sec)
        return "stop"
    if rc != 0 or not all(stage_ok(f"{ad}/{o}") for o in STAGE_OUT[stage]):
        st.add("stage_failed", stage=stage, rc=rc, sec=sec)
        return "failed"
    summ = f"{ad}/writer_run_summary.json"
    if stage_ok(summ) and any(v.get("fallback_detected") for v in rj(summ).values() if isinstance(v, dict)):
        raise GlobalStop(f"[STOP] fallback_detected: {theme}/{arm}/{stage}")
    st.add("stage_done", stage=stage, sec=sec, outputs={o: sha_file(f"{ad}/{o}") for o in STAGE_OUT[stage]})
    return "done"


def b1_try(ctx, theme: str, trigger: str, must_fix: list) -> bool:
    """B1回復の可否判定と準備。1記事1回(R2後FC由来とEN段由来で共通の枠)・Trial全体 ctx.b1_max 回。許可時は旧成果物を別名保存して該当stageをreset。"""
    ad, st = f"{ctx.root}/{theme}/new", ArmState(f"{ctx.root}/{theme}/new")
    lock, gpath = f"{ctx.root}/.b1_lock", f"{ctx.root}/b1_counter.jsonl"
    if st.count("b1_recovery") >= 1:
        st.add("b1_denied", trigger=trigger, reason="per_article_limit(1記事1回)")
        return False
    for _ in range(50):
        try:
            os.mkdir(lock)
            break
        except FileExistsError:
            time.sleep(0.2)
    try:
        n = len(read_jsonl(gpath))
        if n >= ctx.b1_max:
            st.add("b1_denied", trigger=trigger, reason=f"trial_limit({n}/{ctx.b1_max})、STOP記録")
            return False
        append_jsonl(gpath, {"theme": theme, "trigger": trigger, "n_before": n, "ts": time.strftime("%Y-%m-%dT%H:%M:%S")})
    finally:
        os.rmdir(lock)
    st.add("b1_recovery", trigger=trigger, n_global_after=n + 1)
    for d in ("new_writer", "ja_writer", "b1b", "a2", "checker"):      # 元の失敗成果物は上書きせず別名保存
        if os.path.exists(f"{ad}/{d}"):
            os.replace(f"{ad}/{d}", f"{ad}/{d}_prev_b1")
    if os.path.exists(f"{ad}/telemetry/ii.json"):
        os.replace(f"{ad}/telemetry/ii.json", f"{ad}/telemetry/ii_prev_b1.json")
    wj(f"{ad}/recovery/must_fix.json", must_fix)
    st.add("reset", stages=NEW_STAGES, reason="b1_recovery")
    return True


def run_new_arm(ctx, theme: str, topic: str) -> dict:
    ad, st = f"{ctx.root}/{theme}/new", ArmState(f"{ctx.root}/{theme}/new")
    info, en_out = {}, "done"
    while True:
        restart = False
        for s in NEW_JA + ["new_en_adv", "new_en_std"]:
            if ctx.until and ctx_after(s, ctx.until, NEW_STAGES):
                return {**info, "halted": f"until={ctx.until}"}
            out = run_stage(ctx, theme, "new", s, topic)
            if out == "done" and s == "new_r2":
                r2 = rj(f"{ad}/new_writer/r2_fc.json")
                if r2["n_major"] > 0:      # W4b: R2後FC MAJOR -> shadow_stop記録 -> B1(1記事1回、EN由来と共通枠)
                    st.add("shadow_stop", final=False, n_major=r2["n_major"])
                    if b1_try(ctx, theme, "r2_fc_major", _must_fix(r2["majors"])):
                        restart = True
                        break
                    st.add("shadow_stop", final=True, reason="B1回復枠なし/回復後もR2 FC MAJOR(影STOP、続行)")
            elif out == "recheck":          # W5: EN段 ja_source MAJOR(初回JA_RECHECK) -> B1
                trig = rj(f"{ad}/telemetry/ja_recheck_trigger.json")
                ja_src = [d for d in trig["major_deviations"] if d.get("origin") == "ja_source"]
                if b1_try(ctx, theme, "en_ja_source_major", _must_fix(ja_src or trig["major_deviations"])):
                    restart = True
                    break
                st.add("stage_stop", stage=s, reason="JA_RECHECK後のB1回復不可/回復後もMAJOR(STOP記録)")
                en_out = "stop"
                break
            elif out != "done":
                en_out = out
                break
        if not restart:
            break
    info["b1_recoveries"] = st.count("b1_recovery")
    return _post_en(ctx, theme, "new", topic, NEW_STAGES[NEW_STAGES.index("new_shadow"):], en_out, info)


def _must_fix(devs: list) -> list:
    return [{"fact_id": d.get("related_fact_id", ""), "claim_in_article": d.get("claim_in_article", ""), "issue": d.get("issue", ""),
             "explanation": d.get("explanation", "")} for d in devs]


def ctx_after(stage: str, until: str, order: list) -> bool:
    return until in order and order.index(stage) > order.index(until)


def _post_en(ctx, theme, arm, topic, rest, out, info):
    ad = f"{ctx.root}/{theme}/{arm}"
    info["en_state"] = out
    for s in rest:
        if ctx.until and ctx_after(s, ctx.until, NEW_STAGES if arm == "new" else OLD_STAGES):
            info["halted"] = f"until={ctx.until}"
            break
        if s.endswith("check_adv") and not stage_ok(f"{ad}/b1b/article.md") or s.endswith("check_std") and not stage_ok(f"{ad}/a2/article.md"):
            continue          # EN STOP -> Checker未到達(分母に残る独立カテゴリ)
        if s.endswith("shadow") and not (stage_ok(f"{ad}/b1b/article.md") and stage_ok(f"{ad}/ja_writer/revision2.md")):
            continue
        info[s] = run_stage(ctx, theme, arm, s, topic)
    return info


def run_old_arm(ctx, theme: str, topic: str) -> dict:
    info, out = {}, "done"
    for s in ["old_ja", "old_ii", "old_adv", "old_std"]:
        if ctx.until and ctx_after(s, ctx.until, OLD_STAGES):
            return {"halted": f"until={ctx.until}"}
        out = run_stage(ctx, theme, "old", s, topic)
        info[s] = out
        if out != "done" and s != "old_ii":
            break
    info["first_ja_recheck"] = os.path.exists(f"{ctx.root}/{theme}/old/telemetry/ja_recheck_events.jsonl")
    return _post_en(ctx, theme, "old", topic, ["old_shadow", "old_check_adv", "old_check_std"], out, info)


def run_theme(ctx, theme: str) -> dict:
    if ctx.guard.alert_reached():
        raise GlobalStop(f"[SOFT_ALERT] 累計がアラート{ctx.guard.alert}円に到達。新テーマ開始を止めFableへ報告({theme})")
    g0 = prepare_theme(ctx, theme)
    topic = rd(f"{ctx.root}/{theme}/shared/topic.txt")
    res = {"theme": theme, "g0_pass": g0["pass"], "substitutions": g0["substitutions"]}
    for arm in ctx.arms:
        res[arm] = (run_old_arm if arm == "old" else run_new_arm)(ctx, theme, topic)
    wj(f"{ctx.root}/{theme}/theme_summary.json", res)
    return res


def cmd_run(a) -> int:
    ctx = Ctx(a)
    os.makedirs(ctx.root, exist_ok=True)
    if a.g0_only:      # G0照合だけ(API・stage実行なし)
        summ = {}
        for t in ctx.themes:
            try:
                g = prepare_theme(ctx, t)
                summ[t] = {"pass": True, "substitutions": g["substitutions"], "checks": {k: v["pass"] for k, v in g["checks"].items()}}
            except GlobalStop as e:
                g0p = f"{ctx.root}/{t}/g0.json"
                summ[t] = {"pass": False, "reason": str(e), "checks": {k: v["pass"] for k, v in rj(g0p)["checks"].items()} if os.path.exists(g0p) else {}}
        wj(f"{ctx.root}/g0_summary.json", summ)
        print(json.dumps({t: v["pass"] for t, v in summ.items()}, ensure_ascii=False))
        return 0 if all(v["pass"] for v in summ.values()) else 1
    results = []
    try:
        for t in ctx.themes:
            results.append(run_theme(ctx, t))
    except (GlobalStop, ProvenanceViolation) as e:
        wj(ctx.stop_file(), {"reason": str(e), "worker": ctx.wid, "ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "totals": ctx.guard.totals()})
        print(str(e))
        return 3
    wj(f"{ctx.root}/run_summary_worker{ctx.wid}.json", {"themes": results, "totals": ctx.guard.totals(), "stub": ctx.stub})
    print(json.dumps(ctx.guard.totals(), ensure_ascii=False))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    sp = p.add_subparsers(dest="cmd", required=True)
    r = sp.add_parser("run")
    r.add_argument("--root", required=True)
    r.add_argument("--themes", required=True)
    r.add_argument("--arms", default="old,new")
    r.add_argument("--worker-id", type=int, default=1)
    r.add_argument("--inputs-dir", default=f"{TRIAL_ROOT}/inputs")
    r.add_argument("--topics-json", action="append", default=[f"{TRIAL_ROOT}/stage_r/old4_topics.json", f"{TRIAL_ROOT}/stage_r/topics.json"])
    r.add_argument("--until", default=None, help="この段まで実行して止める(G1用)")
    r.add_argument("--stage-r-dir", default=f"{TRIAL_ROOT}/stage_r", help="Stage R(委任_06)出力。読取のみ")
    r.add_argument("--stub", action="store_true")
    r.add_argument("--allow-frozen-b3", action="store_true")
    r.add_argument("--substitute-annotation", action="store_true")
    r.add_argument("--cap-jpy", type=float, default=1000.0)
    r.add_argument("--alert-jpy", type=float, default=800.0)
    r.add_argument("--arm-cap", type=float, default=100.0, help="er019内蔵のarm別予算ガード(横断予約が主)")
    r.add_argument("--checker-cap", type=float, default=10.0)
    r.add_argument("--b1-total-max", type=int, default=int(os.environ.get("E2E_B1_TOTAL_MAX", "3")))
    r.add_argument("--no-mem-check", action="store_true")
    r.add_argument("--allow-script-change", action="store_true", help="再開時にスクリプトsha256が変わっていても記録のみで続行(既定はSTOP)")
    r.add_argument("--g0-only", action="store_true", help="G0照合だけ実施して終了(API・stageなし)")
    s = sp.add_parser("stage")
    s.add_argument("stage")
    s.add_argument("--root", required=True)
    s.add_argument("--theme", required=True)
    s.add_argument("--arm", required=True)
    s.add_argument("--checker-cap", type=float, default=10.0)
    s.add_argument("--must-fix-file", default=None)
    return p


def main(argv=None) -> int:
    for st in (sys.stdout, sys.stderr):
        if hasattr(st, "reconfigure"):
            st.reconfigure(encoding="utf-8", errors="replace")
    argv = sys.argv[1:] if argv is None else argv
    os.chdir(HERE)
    if argv and argv[0] == "er019-shim":
        return worker_er019_shim(argv[1:])
    a = build_parser().parse_args(argv)
    return cmd_run(a) if a.cmd == "run" else stage_main(a)


if __name__ == "__main__":
    sys.exit(main())
