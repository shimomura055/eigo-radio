# -*- coding: utf-8 -*-
"""FAMILY-XZ-PROPER-NOUN-EN-PRONUNCIATION-SUPPLY-TRIAL-01 (Trial専用) lib。

位置づけ: Offline Trial。Production moduleは**import・呼出のみ**(無改変)。本fileはProduction経路に配線しない。
未承認機能のflag/Productionへの新コード経路は置かない(Production側変更0)。実Ledger・HR queue・telemetry・cost log・
Master Storeへは書かない(TrialIsolationでTrial dirへ隔離。testで固定)。

構成:
  A. 隔離(TrialIsolation): Trial Ledgerコピー、研究API stub(腕A/B以外で呼ばれたら記録して失敗)、Azure転写注入stub、
     HR queue / attempt_history / telemetry / cost logのTrial dir化、M1 cache reset。
  B. 実投入証拠: Azure SDK診断ログ(Speech_LogFilename)から speech.context の dgi.Items / bias を呼出ごとに抽出。
  C. 検出器: D1(規則,API 0) / D2(LLM文脈抽出,記事単位1回)。
  D. 研究: 腕A(OpenAI web_search) / 腕B(Perplexity)。
  E. 登録validator: V1〜V6 + V1'(出典URLのHTTP取得とquote本文一致)。
"""
from __future__ import annotations

import contextlib
import copy
import hashlib
import json
import os
import re
import shutil
import time
import unicodedata
import wave
from typing import Any, Callable, Optional

ROOT = os.path.dirname(os.path.abspath(__file__))
TRIAL_ID = "FAMILY-XZ-PROPER-NOUN-EN-PRONUNCIATION-SUPPLY-TRIAL-01"
OUT_ROOT = os.path.join(ROOT, "er089_output", "proper_noun_en_pronunciation_trial_01")
REAL_LEDGER_PATH = "er006_output/pronunciation_ledger_01/ledger.json"

AZURE_JPY_PER_SEC = 1.0 * 160.0 / 3600.0  # USD1.0/audio-hour(pricing_snapshot.json azure audio_hour)、JPY160/USD
JPY_PER_USD = 160.0
# 単価($/1M tokens)。出典: er005_output/cost_baseline_01/pricing_snapshot.json(gpt-6.1-sol=2/0.1/10, gpt-6-luna=0.1/0.01/0.5)、
# 公式 https://developers.openai.com/api/docs/pricing(2026-10-21再取得で一致確認)。web_search toolは$10/1,000 calls。
PRICES = {
    "gpt-6.1-sol": {"in": 2.0, "cached": 0.1, "out": 10.0},
    "gpt-6-luna": {"in": 0.1, "cached": 0.01, "out": 0.5},
    "gpt-4o-mini-transcribe": {"in": 1.25, "out": 5.0},  # 参考(K3 ASR 1回。音声token課金の厳密値は応答usageから算出できない場合は上限見積)
}
WEB_SEARCH_USD_PER_CALL = 10.0 / 1000.0
# Perplexity(sonar chat/completions)は pricing_snapshot.json 未登録。旧Sonar公開単価の保守的上限(入出力$1/M+$0.012/request)
# で見積計上し、応答に usage.cost があればそれを優先(実測値として偽装しない: cost_source欄に区別を記録)。
PERPLEXITY_SONAR_UPPER = {"in": 1.0, "out": 1.0, "per_request_usd": 0.012}


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(t: str) -> str:
    return hashlib.sha256((t or "").encode("utf-8")).hexdigest()


def wav_seconds(path: str) -> float:
    with wave.open(path, "rb") as w:
        return w.getnframes() / float(w.getframerate())


def jsonl_append(path: str, rec: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def read_jsonl(path: str) -> list:
    if not os.path.exists(path):
        return []
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


# ============================================================
# 費用台帳(呼出ごと1行。設計外呼出の検出にも使う)
# ============================================================
def usd_to_jpy(usd: float) -> float:
    return usd * JPY_PER_USD


def llm_cost_usd(model: str, usage: dict, web_search_calls: int = 0) -> float:
    p = PRICES.get(model)
    if not p:
        return 0.0
    cached = usage.get("cached_input_tokens") or 0
    inp = max(0, (usage.get("input_tokens") or 0) - cached)
    out = usage.get("output_tokens") or 0
    usd = inp / 1e6 * p["in"] + cached / 1e6 * p.get("cached", p["in"]) + out / 1e6 * p["out"]
    return usd + web_search_calls * WEB_SEARCH_USD_PER_CALL


class PaidCallLedger:
    """有料呼出の台帳(paid_calls.jsonl)。Cap監視もここで行う。"""

    def __init__(self, path: str, cap_jpy: float):
        self.path, self.cap_jpy = path, cap_jpy

    def total_jpy(self) -> float:
        return round(sum(r.get("jpy", 0.0) for r in read_jsonl(self.path)), 4)

    def record(self, rec: dict) -> dict:
        rec = dict(rec)
        rec["ts"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        jsonl_append(self.path, rec)
        return rec

    def check_cap(self, planned_jpy: float = 0.0) -> None:
        if self.total_jpy() + planned_jpy > self.cap_jpy:
            raise RuntimeError(f"[STOP] Cap超過見込み: 累計{self.total_jpy()}+計画{planned_jpy} > {self.cap_jpy}")


# ============================================================
# A. 隔離
# ============================================================
class TrialIsolation:
    """Trial processの副作用をTrial dirへ閉じ込める(R-01/R-02)。

    * LEDGER_PATH を Trial Ledgerコピーへ(実Ledgerへは書かない)。条件切替は set_ledger()。
    * research_pronunciations は allow_research_arm('B') コンテキスト外では stub(記録して FAILED を返す)。
    * get_full_text_via_azure_stt_with_phrase_list は allow_azure() コンテキスト外では「既存転写注入stub」。
    * HUMAN_REVIEW_LOG_PATH / ATTEMPT_HISTORY_PATH / er025 TELEMETRY_PATH / er021 telemetry / cost logger をTrial dirへ。
    """

    def __init__(self, out_dir: str = OUT_ROOT, real_ledger: str = REAL_LEDGER_PATH):
        import er005_cost_logger as cl
        import er006_pronunciation_ledger_01 as led
        import er006_pronunciation_research_01 as res
        import er006_secondary_asr_01 as sec
        import er011_human_review_lock_01 as rl
        import er021_en_asr_semantic_equivalence_production_01 as sem
        import er025_entity_pronunciation_resolver_core_01 as e25
        self.m = {"cl": cl, "led": led, "res": res, "sec": sec, "rl": rl, "sem": sem, "e25": e25}
        self.out_dir = out_dir
        self.real_ledger = real_ledger
        self.iso_dir = os.path.join(out_dir, "isolated")
        self.ledger_dir = os.path.join(out_dir, "ledger_trial_copy")
        self.trial_ledger = os.path.join(self.ledger_dir, "ledger.json")
        self.base_ledger = os.path.join(self.ledger_dir, "ledger_baseline_copy.json")
        self.unexpected_path = os.path.join(self.iso_dir, "unexpected_calls.jsonl")
        self.azure_stub_path = os.path.join(self.iso_dir, "azure_stub_calls.jsonl")
        self.injected_azure: dict = {}   # wav abs path -> azure transcript(既存転写注入)
        self._research_arm: Optional[str] = None
        self._azure_real = False
        self._saved: dict = {}
        self.real_ledger_sha_start: Optional[str] = None
        self.real_ledger_sha_end: Optional[str] = None
        self.watch_paths = [
            real_ledger,
            "er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl",
            "er011_output/attempt_history.jsonl",
            "er025_output/pronunciation_resolution_core_telemetry_01/telemetry.jsonl",
            "er021_output/en_asr_semantic_equivalence_production_wiring_01/telemetry.jsonl",
            "er006_output/master_audio_store_01/manifest.json",
        ]
        self.watch_start: dict = {}

    # --- context ----------------------------------------------------------
    def _stat(self, p: str) -> dict:
        ap = os.path.join(ROOT, p)
        if not os.path.exists(ap):
            return {"exists": False}
        st = os.stat(ap)
        return {"exists": True, "size": st.st_size, "mtime": st.st_mtime}

    def __enter__(self) -> "TrialIsolation":
        os.makedirs(self.iso_dir, exist_ok=True)
        os.makedirs(self.ledger_dir, exist_ok=True)
        self.real_ledger_sha_start = sha256_file(os.path.join(ROOT, self.real_ledger))
        if not os.path.exists(self.base_ledger):
            shutil.copyfile(os.path.join(ROOT, self.real_ledger), self.base_ledger)
        if not os.path.exists(self.trial_ledger):
            shutil.copyfile(self.base_ledger, self.trial_ledger)
        self.watch_start = {p: self._stat(p) for p in self.watch_paths}
        m = self.m
        self._saved = {
            "LEDGER_PATH": m["led"].LEDGER_PATH,
            "HR": m["sec"].HUMAN_REVIEW_LOG_PATH,
            "ATT": m["rl"].ATTEMPT_HISTORY_PATH,
            "E25": m["e25"].TELEMETRY_PATH,
            "sem_append": m["sem"].append_telemetry_log,
            "research": m["res"].research_pronunciations,
            "sec_research_ref": getattr(m["sec"].pronun_research, "research_pronunciations", None),
            "azure_fn": m["sec"].get_full_text_via_azure_stt_with_phrase_list,
            "cl_path": m["cl"]._LOG_PATH,
        }
        m["led"].LEDGER_PATH = self.trial_ledger
        m["sec"].HUMAN_REVIEW_LOG_PATH = os.path.join(self.iso_dir, "human_review_queue.jsonl")
        m["rl"].ATTEMPT_HISTORY_PATH = os.path.join(self.iso_dir, "attempt_history.jsonl")
        m["e25"].TELEMETRY_PATH = os.path.join(self.iso_dir, "er025_telemetry.jsonl")
        sem_path = os.path.join(self.iso_dir, "semantic_equivalence_telemetry.jsonl")
        orig_sem = self._saved["sem_append"]
        m["sem"].append_telemetry_log = lambda record, path=None: orig_sem(record, path=sem_path)
        m["cl"].init_logger(os.path.join(self.iso_dir, "production_cost_log_isolated.jsonl"))
        real_research = self._saved["research"]

        def research_gate(entities, model="sonar", timeout=60.0):
            if self._research_arm == "B":
                return real_research(entities, model=model, timeout=timeout)
            jsonl_append(self.unexpected_path, {"kind": "research_pronunciations", "arm": self._research_arm,
                                                "n_entities": len(entities or []), "ts": time.strftime("%Y-%m-%dT%H:%M:%S")})
            return {"status": "FAILED", "http_status": None, "body": "TRIAL_STUB_UNEXPECTED_RESEARCH_CALL"}

        m["res"].research_pronunciations = research_gate
        real_azure = self._saved["azure_fn"]

        def azure_gate(wav_path, language="en-US", phrases=None, timeout_seconds=90.0):
            if self._azure_real:
                return real_azure(wav_path, language=language, phrases=phrases, timeout_seconds=timeout_seconds)
            key = os.path.abspath(wav_path)
            hit = self.injected_azure.get(key)
            jsonl_append(self.azure_stub_path, {"wav": os.path.relpath(key, ROOT), "phrases": list(phrases or []),
                                                "hit": hit is not None})
            if hit is None:
                return None, "trial_stub_no_stored_transcript"
            return hit, None

        m["sec"].get_full_text_via_azure_stt_with_phrase_list = azure_gate
        return self

    def __exit__(self, *exc) -> None:
        m, s = self.m, self._saved
        m["led"].LEDGER_PATH = s["LEDGER_PATH"]
        m["sec"].HUMAN_REVIEW_LOG_PATH = s["HR"]
        m["rl"].ATTEMPT_HISTORY_PATH = s["ATT"]
        m["e25"].TELEMETRY_PATH = s["E25"]
        m["sem"].append_telemetry_log = s["sem_append"]
        m["res"].research_pronunciations = s["research"]
        m["sec"].get_full_text_via_azure_stt_with_phrase_list = s["azure_fn"]
        m["cl"]._LOG_PATH = s["cl_path"]
        self.real_ledger_sha_end = sha256_file(os.path.join(ROOT, self.real_ledger))

    # --- helpers ----------------------------------------------------------
    def set_ledger(self, path: str) -> None:
        """LEDGER_PATH切替+M1凍結cache reset(R-02: 条件切替ごとに必須)。"""
        self.m["led"].LEDGER_PATH = path
        self.m["sec"]._reset_m1_freeze_cache()

    @contextlib.contextmanager
    def allow_research_arm(self, arm: str):
        prev = self._research_arm
        self._research_arm = arm
        try:
            yield
        finally:
            self._research_arm = prev

    @contextlib.contextmanager
    def allow_azure(self):
        prev = self._azure_real
        self._azure_real = True
        try:
            yield
        finally:
            self._azure_real = prev

    def unexpected_calls(self) -> list:
        return read_jsonl(self.unexpected_path)

    def watch_report(self) -> dict:
        """実運用ファイルの前後stat。他agentの並行書込があり得るため『差=本Trial起因』とは断定しない(参考)。"""
        end = {p: self._stat(p) for p in self.watch_paths}
        sha_end = sha256_file(os.path.join(ROOT, self.real_ledger))
        return {"start": self.watch_start, "end": end,
                "real_ledger_sha_start": self.real_ledger_sha_start, "real_ledger_sha_end": sha_end,
                "real_ledger_unchanged": self.real_ledger_sha_start == sha_end}


def ledger_snapshot(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def ledger_diff(before: dict, after: dict) -> dict:
    added = sorted(set(after) - set(before))
    removed = sorted(set(before) - set(after))
    changed = sorted(k for k in set(before) & set(after) if before[k] != after[k])
    return {"added": added, "removed": removed, "changed": changed}


# ============================================================
# B. 実投入証拠(SDK診断ログ -> speech.context)
# ============================================================
_CTX_RE = re.compile(r"speech\.context='(\{.*\})'")


def extract_speech_context(log_text: str) -> dict:
    """SDK診断ログから speech.context の dgi.Items / bias を抽出する。キー/regionは取り出さない。"""
    ctxs = []
    for line in log_text.splitlines():
        m = _CTX_RE.search(line)
        if not m:
            continue
        try:
            ctxs.append(json.loads(m.group(1)))
        except json.JSONDecodeError:
            continue
    items, biases = [], []
    for c in ctxs:
        dgi = c.get("dgi") or {}
        for g in dgi.get("Groups") or []:
            for it in g.get("Items") or []:
                if it.get("Text") is not None and it["Text"] not in items:
                    items.append(it["Text"])
        if "bias" in dgi:
            biases.append(float(dgi["bias"]))
    return {"n_context": len(ctxs), "dgi_items": items, "bias": sorted(set(biases)),
            "has_dgi": any("dgi" in c for c in ctxs)}


@contextlib.contextmanager
def sdk_log_to(path: str):
    """azure SpeechConfig 生成直後に Speech_LogFilename を付与する(Production関数は無改変)。"""
    import azure.cognitiveservices.speech as speechsdk
    if os.path.exists(path):
        os.remove(path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    orig = speechsdk.SpeechConfig

    def _cfg(*a, **k):
        c = orig(*a, **k)
        c.set_property(speechsdk.PropertyId.Speech_LogFilename, path)
        return c

    speechsdk.SpeechConfig = _cfg
    try:
        yield
    finally:
        speechsdk.SpeechConfig = orig


def azure_production_call(iso: TrialIsolation, paid: PaidCallLedger, wav: str, phrases: list, tag: dict,
                          sdk_log_dir: str, evidence_path: str) -> dict:
    """Production関数 get_full_text_via_azure_stt_with_phrase_list を実呼出し、speech.contextの実投入証拠を1行記録する。"""
    import gc
    import er006_secondary_asr_01 as sec
    dur = wav_seconds(wav)
    est = dur * AZURE_JPY_PER_SEC
    paid.check_cap(est)
    log = os.path.join(sdk_log_dir, f"sdk_{int(time.time()*1000)}.log")
    t0 = time.time()
    with iso.allow_azure(), sdk_log_to(log):
        text, err = sec.get_full_text_via_azure_stt_with_phrase_list(wav, language="en-US", phrases=phrases or None)
    gc.collect()
    ev = {}
    if os.path.exists(log):
        ev = extract_speech_context(open(log, encoding="utf-8", errors="replace").read())
        with contextlib.suppress(OSError):
            os.remove(log)  # 生ログは削除(subscription key等が含まれ得るため保存しない)
    weight_const = sec.AZURE_PHRASE_LIST_WEIGHT
    expected = list(phrases or [])
    match = (ev.get("dgi_items") == expected and (not expected or ev.get("bias") == [float(weight_const)])) if ev else None
    rec = {"wav": os.path.relpath(wav, ROOT), "phrases_expected": expected, "dgi_items": ev.get("dgi_items"),
           "bias": ev.get("bias"), "weight_const": weight_const, "match": match, "has_dgi": ev.get("has_dgi"),
           "transcript": text, "err": err, "elapsed_s": round(time.time() - t0, 2), "duration_s": round(dur, 2),
           "jpy": round(est, 4), "tag": tag}
    try:
        import azure.cognitiveservices.speech as speechsdk
        rec["sdk_version"] = getattr(speechsdk, "__version__", None)
    except Exception:  # noqa: BLE001
        pass
    paid.record({"kind": "azure_stt", "wav": rec["wav"], "jpy": rec["jpy"], "tag": tag, "phrases": expected})
    jsonl_append(evidence_path, rec)
    return rec


# ============================================================
# C. 検出器
# ============================================================
_QUOTES = "\u201c\u201d\u2018\u2019\"'`"
_TOKEN_RE = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9'\u2019\-]*[A-Za-z0-9])?")
_CAMEL_RE = re.compile(r"^(?:[a-z]+[A-Z][A-Za-z]*|[A-Z][a-z]+[A-Z][A-Za-z]*|[A-Z]{2,}[a-z][A-Za-z]*)$")
_ALLCAPS_RE = re.compile(r"^[A-Z]{2,}$")
_KANA_RE = re.compile(r"[\u3040-\u30ff\u3400-\u9fff]")
CUE_WORDS = ("called", "named", "known as", "pronounced", "spelled", "dubbed", "so-called", "app", "service", "platform",
             "brand", "company", "launch of")
# 文頭語として自然に大文字になる一般語(固有名詞候補にしない)
_STOP_CAP = {"i", "i'm", "i'd", "i'll", "i've", "a", "the", "in", "on", "at", "it", "he", "she", "we", "they", "you", "his", "her",
             "my", "your", "our", "their", "this", "that", "these", "those", "and", "but", "or", "so", "if", "then", "when", "what",
             "who", "why", "how", "where", "which", "is", "are", "was", "were", "do", "does", "did", "can", "will", "would",
             "could", "should", "may", "might", "not", "no", "yes", "oh", "well", "now", "for", "to", "of", "with", "by"}


def _cmu_has(word: str) -> bool:
    import pronouncing
    return bool(pronouncing.phones_for_word(word.lower().strip("'\u2019")))


def hint_format_ok(hint: str) -> bool:
    if not hint or len(hint) > 40:
        return False
    if re.search(r"[()/\\\u3000]| or | / |\u307e\u305f\u306f|[^\x00-\x7f]", hint):
        return False
    return bool(_HINT_RE.match(hint.strip()))


_HINT_RE = re.compile(r"^[A-Za-z][A-Za-z'\-]*(?: [A-Za-z][A-Za-z'\-]*){0,3}$")


def en_pron_info_qualifies(entry: dict) -> bool:
    """『EN発音情報あり』(R-06拒否権/未登録判定の共通定義): hint非空∧sources非空∧confidence>=medium∧V3形式適合∧
    entity_type≠ja_reading_katakana/cascade_unresolved_entity。"""
    if not entry:
        return False
    if entry.get("entity_type") in ("ja_reading_katakana", "cascade_unresolved_entity"):
        return False
    if not entry.get("pronunciation_hint") or not entry.get("sources"):
        return False
    if entry.get("confidence") not in ("high", "medium"):
        return False
    return hint_format_ok(entry.get("pronunciation_hint", ""))


def ledger_en_entries_for(ledger: dict, surface: str) -> list:
    s = surface.strip().lower()
    return [e for e in ledger.values() if (e.get("surface") or "").strip().lower() == s]


def _sentence_start_flags(text: str, spans: list) -> list:
    flags = []
    for (a, _b) in spans:
        i = a - 1
        while i >= 0 and (text[i].isspace() or text[i] in _QUOTES + "([{\u2014-"):
            i -= 1
        flags.append(i < 0 or text[i] in ".!?\n")
    return flags


_STRONG_RULES = {"R_CAMEL", "R_QUOTED", "R_FACT", "R_LEDGER_JA_KATAKANA_LATIN", "R_JA_GATE_UNKNOWN_LATIN", "R_ALLCAPS",
                 "R_CAP_PHRASE", "R_READOUT_EVIDENCE_ONLY"}


def detect_d1(text: str, ledger: Optional[dict] = None, fact_terms: Optional[list] = None,
              ja_gate_tokens: Optional[list] = None) -> dict:
    """D1: 規則抽出(API 0)。戻り値 {candidates:[{surface,key,rules,evidence_only}], excluded:[...]}。
    再現率優先(誤検出は件数報告のみ)。除外=EN発音情報ありのLedger語/CMU収録の一般語で手がかりなし。"""
    ledger = ledger or {}
    toks = [(re.sub(r"['’]s$", "", m.group(0)) if len(m.group(0)) > 4 else m.group(0), m.start(), m.end())
            for m in _TOKEN_RE.finditer(text)]  # 所有格(Melos's)は語幹で扱う(R-11d)
    spans = [(a, b) for (_t, a, b) in toks]
    start_flags = _sentence_start_flags(text, spans)
    cands: dict = {}

    def add(surface: str, rule: str, evidence_only: bool = False) -> None:
        surface = surface.strip(_QUOTES + " .,;:!?")
        if not surface or not re.search(r"[A-Za-z]", surface):
            return
        key = re.sub(r"\s+", " ", surface.lower())
        d = cands.setdefault(key, {"surface": surface, "key": key, "rules": [], "evidence_only": True})
        if rule not in d["rules"]:
            d["rules"].append(rule)
        if not evidence_only:
            d["evidence_only"] = False
        if sum(c.isupper() for c in surface) > sum(c.isupper() for c in d["surface"]):
            d["surface"] = surface

    # (i) 大文字始まり語(文頭語は非CMU or 全大文字 or CamelCaseのみ)。連続大文字語は句としても追加
    i = 0
    while i < len(toks):
        t, a, b = toks[i]
        if t[0].isupper() and t.lower() not in _STOP_CAP:
            if (not start_flags[i]) or (not _cmu_has(t)) or _ALLCAPS_RE.match(t) or _CAMEL_RE.match(t):
                j = i
                phrase = [t]
                while (j + 1 < len(toks) and toks[j + 1][0][0].isupper() and toks[j + 1][0].lower() not in _STOP_CAP
                       and text[toks[j][2]:toks[j + 1][1]] == " "):
                    j += 1
                    phrase.append(toks[j][0])
                add(t, "R_CAP_MID" if not start_flags[i] else "R_CAP_START_OOV_OR_ALLCAPS")
                if len(phrase) > 1:
                    add(" ".join(phrase), "R_CAP_PHRASE")
                    for p in phrase[1:]:
                        if p.lower() not in _STOP_CAP:
                            add(p, "R_CAP_MID")
                i = j
        i += 1
    # (ii) CamelCase/語中大文字 (iii') 全大文字
    for t, _a, _b in toks:
        if _CAMEL_RE.match(t):
            add(t, "R_CAMEL")
        elif _ALLCAPS_RE.match(t):
            add(t, "R_ALLCAPS")
    # (iii) 引用符で囲まれた1〜3語
    for m in re.finditer(r"[\u201c\"\u2018]([^\u201c\u201d\"\u2018\u2019]{1,40})[\u201d\"\u2019]", text):
        inner = m.group(1).strip().rstrip(".,!?;:")
        words = _TOKEN_RE.findall(inner)
        if 1 <= len(words) <= 3 and len(inner) <= 30:
            add(inner, "R_QUOTED")
    # (iv) 手がかり語の直後n語
    for cue in CUE_WORDS:
        for m in re.finditer(r"\b" + re.escape(cue) + r"\b[\s:\u201c\"\u2018']*", text, flags=re.I):
            tail = text[m.end():m.end() + 60]
            w = _TOKEN_RE.findall(tail)[:2]
            if w and w[0].lower() not in _STOP_CAP:
                add(w[0], "R_CUE_" + cue.replace(" ", "_"))
                if len(w) == 2 and w[1][0].isupper():
                    add(" ".join(w), "R_CUE_" + cue.replace(" ", "_"))
    # (v) 読み明示文: 候補を拾う手がかりにだけ使う(発音の根拠にはしない=Writer自己生成)
    for m in re.finditer(r"pronounced\s+[\u201c\"\u2018']?([A-Za-z][A-Za-z'\-]*)", text, flags=re.I):
        add(m.group(1), "R_READOUT_EVIDENCE_ONLY", evidence_only=True)
    # (vi) Fact由来
    for ft in fact_terms or []:
        if re.search(r"(?<![A-Za-z0-9])" + re.escape(ft) + r"(?![A-Za-z0-9])", text, flags=re.I):
            add(ft, "R_FACT")
    # (vii) ハイフン/数字入り造語
    for t, _a, _b in toks:
        if ("-" in t and t.replace("-", "").isalpha()) or (re.search(r"\d", t) and re.search(r"[A-Za-z]", t)):
            add(t, "R_HYPHEN_DIGIT")
    # (R-12) Ledgerにja_reading_katakana entryのあるLatin語 / JA側Gate検出の未知Latin語
    low = text.lower()
    for e in ledger.values():
        if e.get("entity_type") == "ja_reading_katakana" and re.search(r"[A-Za-z]", e.get("surface", "")):
            s = e["surface"].lower()
            if re.search(r"(?<![a-z0-9])" + re.escape(s) + r"(?![a-z0-9])", low):
                m = re.search(r"(?<![A-Za-z0-9])" + re.escape(e["surface"]) + r"(?![A-Za-z0-9])", text, flags=re.I)
                add(m.group(0) if m else e["surface"], "R_LEDGER_JA_KATAKANA_LATIN")
    for g in ja_gate_tokens or []:
        m = re.search(r"(?<![A-Za-z0-9])" + re.escape(g) + r"(?![A-Za-z0-9])", text, flags=re.I)
        if m:
            add(m.group(0), "R_JA_GATE_UNKNOWN_LATIN")

    excluded, kept = [], []
    for d in cands.values():
        ents = ledger_en_entries_for(ledger, d["surface"])
        if any(en_pron_info_qualifies(e) for e in ents):
            excluded.append({**d, "excluded_reason": "en_pronunciation_already_registered"})
            continue
        words = d["key"].split(" ")
        all_cmu = all(_cmu_has(w) for w in words)
        has_strong = any(r in _STRONG_RULES or r.startswith("R_CUE_") for r in d["rules"])
        if all_cmu and not has_strong and set(d["rules"]) <= {"R_CAP_MID", "R_CAP_START_OOV_OR_ALLCAPS"} and \
                d["key"] in {"i", "japan", "english", "october", "monday", "tuesday", "wednesday", "thursday", "friday",
                             "saturday", "sunday"}:
            excluded.append({**d, "excluded_reason": "cmu_common_word_no_cue"})
            continue
        kept.append(d)
    return {"candidates": sorted(kept, key=lambda x: x["key"]), "excluded": excluded}


def recall_against(cands: list, must_have: list) -> dict:
    """must_have(語/句) の再現率。句は句候補、または全構成語が候補に出ていれば検出済み(components)。"""
    keys = {c["key"] for c in cands}
    res = {}
    for m in must_have:
        k = m.lower()
        if k in keys:
            res[m] = "found"
        elif all(w in keys for w in k.split(" ")):
            res[m] = "found_by_components"
        else:
            res[m] = "MISSED"
    return {"per_word": res, "recall": sum(1 for v in res.values() if v != "MISSED") / max(1, len(res))}


def load_ja_gate_tokens(telemetry_path: str, since: str, until: str) -> list:
    """er025 telemetry(JA側resolver)の tokens(Latin語)を期間内で集める(R-12)。"""
    out = []
    for r in read_jsonl(telemetry_path):
        ts = r.get("logged_at", "")
        if since <= ts <= until and isinstance(r.get("tokens"), list):
            out.extend(t for t in r["tokens"] if re.search(r"[A-Za-z]", t))
    return sorted(set(out))


# ---------- D2: LLM文脈抽出(記事単位1回) ----------
D2_PROMPT = """You help a podcast pipeline find proper nouns whose English pronunciation may be uncertain.
Read the English article below (and the context) and list every proper noun, brand/product/service name, person or place name,
and coined word that a text-to-speech engine or a speech-recognition engine could mispronounce or misrecognise.
Include names that start with a lowercase letter (for example camelCase product names) when the context shows they are names.
Do NOT include ordinary dictionary words unless the article uses them as a name. Do NOT guess pronunciations.

Return JSON only: {{"items":[{{"surface":"<exact spelling as in the article>","kind":"brand|person|place|org|coinage|product","why":"<short quote from the article showing the cue>"}}]}}

Context title/theme: {title}
Known fact-card proper nouns (may be empty): {facts}

ARTICLE:
{article}
"""


def parse_json_lenient(text: str) -> Optional[dict]:
    if not text:
        return None
    t = text.strip()
    t = re.sub(r"^```(?:json)?\s*|\s*```$", "", t, flags=re.S)
    try:
        return json.loads(t)
    except json.JSONDecodeError:
        pass
    m = re.search(r"\{.*\}", t, flags=re.S)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            return None
    return None


def _usage_dict(usage: Any) -> dict:
    if usage is None:
        return {}
    d = {"input_tokens": getattr(usage, "input_tokens", None), "output_tokens": getattr(usage, "output_tokens", None)}
    det = getattr(usage, "input_tokens_details", None)
    if det is not None:
        d["cached_input_tokens"] = getattr(det, "cached_tokens", None)
    od = getattr(usage, "output_tokens_details", None)
    if od is not None:
        d["reasoning_tokens"] = getattr(od, "reasoning_tokens", None)
    return d


def openai_client():
    from dotenv import load_dotenv
    load_dotenv()
    from openai import OpenAI
    return OpenAI()


class RecordingClient:
    """OpenAI client proxy。responses.create の応答(usage含む)を sink に記録する(make_writer_research_fn へ渡す)。"""

    def __init__(self, real, sink: list):
        self._real, self.sink = real, sink
        outer = self

        class _R:
            def create(self, **kw):
                resp = outer._real.responses.create(**kw)
                outer.sink.append(resp)
                return resp

        self.responses = _R()


def detect_d2(paid: PaidCallLedger, article_text: str, title: str, facts: list, model: str, tag: dict,
              client=None, planned_jpy: float = 3.0) -> dict:
    """D2: LLM文脈抽出。記事単位1呼出。出力は『候補提案』のみ(D1の候補を捨てる権限なし)。"""
    paid.check_cap(planned_jpy)
    client = client or openai_client()
    prompt = D2_PROMPT.format(title=title, facts=", ".join(facts) if facts else "(none)", article=article_text)
    kw = {"model": model, "input": [{"role": "user", "content": prompt}]}
    if model.startswith("gpt-6.1-sol"):
        kw["reasoning"] = {"effort": "low"}
    t0 = time.time()
    resp = client.responses.create(**kw)
    usage = _usage_dict(getattr(resp, "usage", None))
    usd = llm_cost_usd(model, usage)
    text = getattr(resp, "output_text", "") or ""
    parsed = parse_json_lenient(text)
    items = []
    if isinstance(parsed, dict) and isinstance(parsed.get("items"), list):
        for it in parsed["items"]:
            if isinstance(it, dict) and it.get("surface"):
                items.append({"surface": str(it["surface"]).strip(), "kind": it.get("kind"), "why": it.get("why")})
    rec = paid.record({"kind": "d2_detect", "model": model, "resp_model": getattr(resp, "model", None),
                       "response_id": getattr(resp, "id", None), "usage": usage, "jpy": round(usd_to_jpy(usd), 4),
                       "elapsed_s": round(time.time() - t0, 2), "parse_ok": parsed is not None, "tag": tag,
                       "prompt_sha256": sha256_text(prompt)})
    return {"items": items, "raw_text": text, "paid": rec}


# ============================================================
# D. 研究(腕A: OpenAI web_search / 腕B: Perplexity)
# ============================================================
RESEARCH_PROMPT = """Find how English speakers actually pronounce each name below, using the OFFICIAL website, official announcement, or the
owner's/official audio or video (podcast, interview, official video) as the primary source. Dictionaries (Merriam-Webster, Oxford,
Cambridge, Forvo) are acceptable secondary sources for ordinary names.

STRICT RULES
1. Do NOT infer an English pronunciation from a Japanese katakana reading, a Japanese-language page alone, or from the spelling.
   If the only evidence is a Japanese-language statement of the reading, return status "UNCONFIRMED" and say so.
2. Every CONFIRMED item MUST include a real source_url that you opened, and a verbatim quote (copy-paste from that page) that states or shows
   the English pronunciation (spoken-form text, phonetic respelling, or IPA).
3. If no official English pronunciation exists or you cannot find one, return status "UNCONFIRMED" with a short reason. Never invent.
4. confidence "high" only when the source is audio/video of the owner/official pronouncing it; text-only or dictionary sources are "medium" or lower.
5. pronunciation_hint must be one plain English respelling made only of ASCII letters, hyphens and apostrophes, e.g. "oh-TOH-nee"
   (no parentheses, no alternatives; put other accepted pronunciations in alternate_pronunciations).

NAMES (surface | type guess | context):
{names}

Return JSON only:
{{"items":[{{"surface":"","entity_type":"person|place|organization|product|brand|coinage","canonical_spelling":"","status":"CONFIRMED|UNCONFIRMED",
"unconfirmed_reason":"","pronunciation_hint":"","expected_pronunciation_ipa":"","alternate_pronunciations":[],"confidence":"high|medium|low",
"source_url":"","quote":"","source_type":"audio_video|official_text_phonetic|dictionary|other|japanese_text_only","ambiguity_note":""}}]}}
"""


def build_research_prompt(targets: list, extra: str = "") -> str:
    names = "\n".join(f"- {t['surface']} | {t.get('type', 'unknown')} | {t.get('context', '')}" for t in targets)
    return RESEARCH_PROMPT.format(names=names) + (("\nADDITIONAL FOCUS:\n" + extra) if extra else "")


def research_arm_a(paid: PaidCallLedger, targets: list, model: str = "gpt-6.1-sol", effort: str = "medium",
                   client=None, planned_jpy: float = 30.0, extra: str = "") -> dict:
    """腕A: OpenAI Responses web_search(既存 er002 make_writer_research_fn を無改変で利用。RecordingClientで使用量を記録)。"""
    import er002_ja_web_research_r3 as r3
    paid.check_cap(planned_jpy)
    real = client or openai_client()
    sink: list = []
    prompt = build_research_prompt(targets, extra)
    fn = r3.make_writer_research_fn(
        prompt, client=RecordingClient(real, sink), model=model, reasoning_effort=effort,
        developer_message="You are a careful pronunciation researcher. Answer in English. Output JSON only.")
    t0 = time.time()
    text, resp_model, resp_id, search_usage, sources = fn()
    resp = sink[-1] if sink else None
    usage = _usage_dict(getattr(resp, "usage", None))
    n_search = int(search_usage.get("web_search_call_count", 0))
    usd = llm_cost_usd(model, usage, web_search_calls=n_search)
    parsed = parse_json_lenient(text)
    rec = paid.record({"kind": "research_arm_a", "model": model, "resp_model": resp_model, "response_id": resp_id,
                       "usage": usage, "web_search_calls": n_search, "queries": search_usage.get("queries"),
                       "jpy": round(usd_to_jpy(usd), 4), "elapsed_s": round(time.time() - t0, 2), "parse_ok": parsed is not None,
                       "prompt_sha256": sha256_text(prompt), "n_targets": len(targets), "effort": effort})
    return {"arm": "A", "items": (parsed or {}).get("items") or [], "raw_text": text, "sources": sources, "paid": rec,
            "prompt_sha256": sha256_text(prompt), "model": resp_model, "response_id": resp_id}


PPLX_SCHEMA = {
    "type": "object",
    "properties": {"items": {"type": "array", "items": {"type": "object", "properties": {
        "surface": {"type": "string"}, "entity_type": {"type": "string"}, "canonical_spelling": {"type": "string"},
        "status": {"type": "string", "enum": ["CONFIRMED", "UNCONFIRMED"]}, "unconfirmed_reason": {"type": "string"},
        "pronunciation_hint": {"type": "string"}, "expected_pronunciation_ipa": {"type": "string"},
        "alternate_pronunciations": {"type": "array", "items": {"type": "string"}},
        "confidence": {"type": "string", "enum": ["high", "medium", "low"]}, "source_url": {"type": "string"},
        "quote": {"type": "string"}, "source_type": {"type": "string"}, "ambiguity_note": {"type": "string"}},
        "required": ["surface", "status"]}}},
    "required": ["items"]}


def research_arm_b(paid: PaidCallLedger, targets: list, model: str = "sonar", planned_jpy: float = 5.0,
                   timeout: float = 90.0) -> dict:
    """腕B: Perplexity(現行資産と同じendpoint/認証)。Production関数`research_pronunciations`はper-item quote/source_urlを要求できない
    (固定promptとschema)ため、同じPerplexity chat/completionsへTrial promptを直接送る=『現行ベンダー資産のベースライン』。
    Production research_pronunciations は呼ばない(TrialIsolationのstubは発火しない)。"""
    import requests
    from dotenv import load_dotenv
    load_dotenv()
    paid.check_cap(planned_jpy)
    key = os.getenv("PERPLEXITY_API_KEY")
    if not key:
        return {"arm": "B", "items": [], "error": "CREDENTIAL_REQUIRED", "paid": None}
    prompt = build_research_prompt(targets)
    t0 = time.time()
    r = requests.post("https://api.perplexity.ai/chat/completions",
                      headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                      json={"model": model, "messages": [{"role": "user", "content": prompt}],
                            "response_format": {"type": "json_schema", "json_schema": {"schema": PPLX_SCHEMA}}},
                      timeout=timeout)
    el = round(time.time() - t0, 2)
    if r.status_code != 200:
        rec = paid.record({"kind": "research_arm_b", "model": model, "http_status": r.status_code, "jpy": 0.2,
                           "cost_source": "failed_call_assumed_minimal", "elapsed_s": el, "body": r.text[:300]})
        return {"arm": "B", "items": [], "error": f"HTTP {r.status_code}", "paid": rec}
    data = r.json()
    content = data["choices"][0]["message"]["content"]
    parsed = parse_json_lenient(content)
    usage = data.get("usage") or {}
    cost_obj = usage.get("cost")
    if isinstance(cost_obj, dict) and cost_obj.get("total_cost") is not None:
        usd, src = float(cost_obj["total_cost"]), "response.usage.cost.total_cost"
    else:
        u = PERPLEXITY_SONAR_UPPER
        usd = ((usage.get("prompt_tokens") or 0) / 1e6 * u["in"] + (usage.get("completion_tokens") or 0) / 1e6 * u["out"]
               + u["per_request_usd"])
        src = "estimated_upper_bound(legacy Sonar public price; unregistered in pricing_snapshot.json)"
    rec = paid.record({"kind": "research_arm_b", "model": model, "resp_model": data.get("model"), "response_id": data.get("id"),
                       "usage": usage, "jpy": round(usd_to_jpy(usd), 4), "cost_source": src, "elapsed_s": el,
                       "parse_ok": parsed is not None, "prompt_sha256": sha256_text(prompt), "n_targets": len(targets)})
    return {"arm": "B", "items": (parsed or {}).get("items") or [], "raw_text": content, "citations": data.get("citations", []),
            "paid": rec, "prompt_sha256": sha256_text(prompt), "model": data.get("model"), "response_id": data.get("id")}


# ============================================================
# E. 登録validator
# ============================================================
_PRON_CUE_RE = re.compile(
    r"pronounc|pronunciation|sounds? like|said as|say it|read as|phonetic|respell|rhymes? with|ipa"
    r"|[\u02c8\u02cc\u0259\u025b\u026a\u028a\u0251\u0252\u0254\u025c\u028c\u0283\u0292\u03b8\u00f0\u014b]", re.I)
_IPA_SLASH_RE = re.compile(r"/[^/\s][^/]*/")
_JA_ONLY_NOTE_RE = re.compile(r"katakana|japanese reading|japanese-language|japanese only|only (?:in )?japanese|romaniz|\u30ab\u30bf\u30ab\u30ca", re.I)


def norm_for_quote(s: str) -> str:
    s = unicodedata.normalize("NFKC", s or "").lower()
    s = s.replace("\u2019", "'").replace("\u2018", "'").replace("\u201c", '"').replace("\u201d", '"')
    s = re.sub(r"[^a-z0-9\u3040-\u30ff\u3400-\u9fff]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def html_to_text(html_s: str) -> str:
    import html as _html
    s = re.sub(r"(?is)<(script|style|noscript).*?</\1>", " ", html_s)
    s = re.sub(r"(?s)<[^>]+>", " ", s)
    return _html.unescape(re.sub(r"\s+", " ", s))


def default_fetch(url: str, timeout: float = 15.0) -> str:
    """URLを取得して本文テキストを返す。失敗は例外。text以外(音声/動画等)は ValueError('non_text_media')。"""
    import requests
    r = requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0 (EigoRadioTrial; source verification)"},
                     allow_redirects=True)
    r.raise_for_status()
    ct = (r.headers.get("Content-Type") or "").lower()
    if not any(x in ct for x in ("text", "html", "json", "xml")):
        raise ValueError(f"non_text_media:{ct}")
    return html_to_text(r.text) if ("html" in ct or "xml" in ct) else r.text


def verify_quote_in_source(url: str, quote: str, fetch: Callable[[str], str] = default_fetch) -> dict:
    """V1': source URLをHTTP取得し、quoteの本文一致を確認する。'...'/'…'で区切った各断片(12字以上)がすべて含まれること。"""
    out = {"url": url, "fetched": False, "quote_found": False, "error": None}
    try:
        page = fetch(url)
    except Exception as exc:  # noqa: BLE001
        out["error"] = f"{type(exc).__name__}: {str(exc)[:160]}"
        return out
    out["fetched"] = True
    np_ = norm_for_quote(page)
    frags = [norm_for_quote(f) for f in re.split(r"\.\.\.|\u2026", quote or "")]
    frags = [f for f in frags if len(f) >= 12] or [norm_for_quote(quote)]
    out["quote_found"] = bool(frags) and all(f and f in np_ for f in frags)
    out["page_chars"] = len(page)
    return out


def validate_item(item: dict, surface_in_text: str, ledger: dict, fetch: Callable[[str], str] = default_fetch,
                  arm: str = "?", meta: Optional[dict] = None) -> dict:
    """登録判定 V1〜V6 + V1'。戻り値 {decision:'REGISTER'|'UNCONFIRMED_SAFE', reasons:[...], checks:{...}, entry:{...}|None}。
    1つでも不成立なら登録しない(UNCONFIRMED_SAFE)。"""
    meta = meta or {}
    reasons, checks = [], {}
    quote = (item.get("quote") or "").strip()
    url = (item.get("source_url") or "").strip()
    stype = (item.get("source_type") or "").strip().lower()
    note = item.get("ambiguity_note") or ""

    if (item.get("status") or "").upper() != "CONFIRMED":
        reasons.append("research_status_unconfirmed:" + (item.get("unconfirmed_reason") or "")[:80])
    # V1 根拠
    has_cue = bool(_PRON_CUE_RE.search(quote + " " + (item.get("expected_pronunciation_ipa") or "")))
    v1 = bool(re.match(r"^https?://", url)) and bool(quote) and (has_cue or stype == "audio_video")
    if stype in ("japanese_text_only", "ja_text_only"):
        v1 = False
    checks["V1"] = v1
    if not v1:
        reasons.append("V1_no_valid_source_or_quote")
    # V2 非カタカナ推定
    ja_quote = bool(_KANA_RE.search(quote))
    v2 = not (ja_quote or stype in ("japanese_text_only", "ja_text_only") or _JA_ONLY_NOTE_RE.search(note))
    checks["V2"] = v2
    if not v2:
        reasons.append("V2_japanese_only_or_katakana_inference")
    # V3 形式
    hint = (item.get("pronunciation_hint") or "").strip()
    cs = (item.get("canonical_spelling") or "").strip()
    alts_ok, alts_clean = True, []
    for a in (item.get("alternate_pronunciations") or []):
        if not a:
            continue
        m = _IPA_SLASH_RE.search(a)  # alternate_pronunciationsはIPA(M1が読む)。説明語(British English等)を除いたスラッシュ内のみ採用
        if hint_format_ok(a):
            alts_clean.append(a)
        elif m:
            alts_clean.append(m.group(0))
        else:
            alts_ok = False
    item = dict(item)
    item["alternate_pronunciations"] = alts_clean
    v3 = (hint_format_ok(hint) and re.sub(r"\s+", " ", cs.lower()) == re.sub(r"\s+", " ", surface_in_text.lower()) and alts_ok)
    checks["V3"] = v3
    if not v3:
        reasons.append("V3_format_or_canonical_mismatch")
    # V4 confidence(R4基準: highは音声のみ。それ以外はmedium以下へ)
    conf = (item.get("confidence") or "low").lower()
    downgraded = False
    if conf == "high" and stype != "audio_video":
        conf, downgraded = "medium", True
    v4 = conf in ("high", "medium")
    checks["V4"] = v4
    checks["V4_downgraded_high_to_medium"] = downgraded
    if not v4:
        reasons.append("V4_confidence_low")
    # V5 競合(R-06: 拒否権=EN発音情報あり∧品質基準を満たすentryのみ)
    veto_ents = [e for e in ledger_en_entries_for(ledger, surface_in_text) if en_pron_info_qualifies(e)]
    conflict = []
    for e in veto_ents:
        same_hint = (e.get("pronunciation_hint") or "").lower() == hint.lower()
        same_ipa = (e.get("expected_pronunciation_ipa") or "") == (item.get("expected_pronunciation_ipa") or "")
        if not (same_hint and same_ipa):
            conflict.append({"ledger_surface": e.get("surface"), "entity_type": e.get("entity_type"), "hint": e.get("pronunciation_hint")})
    v5 = not conflict
    checks["V5"] = v5
    checks["V5_veto_candidates"] = len(veto_ents)
    checks["V5_non_veto_coexisting"] = [
        {"entity_type": e.get("entity_type"), "confidence": e.get("confidence"), "hint": (e.get("pronunciation_hint") or "")[:40]}
        for e in ledger_en_entries_for(ledger, surface_in_text) if not en_pron_info_qualifies(e)]
    if not v5:
        reasons.append("V5_conflict_with_qualifying_entry")
    # V1' 出典の実在性・quote本文一致(HTTP取得)
    vp = {"skipped": True}
    if v1 and v2:
        if stype == "audio_video":
            vp = {"url": url, "fetched": False, "quote_found": False, "error": "media_source_quote_not_text_verifiable"}
        else:
            vp = verify_quote_in_source(url, quote, fetch)
    checks["V1p"] = bool(vp.get("quote_found"))
    checks["V1p_detail"] = vp
    if v1 and v2 and not vp.get("quote_found"):
        reasons.append("source_unverifiable")
    # V6 追跡
    v6 = all(meta.get(k) for k in ("retrieved_at", "model", "prompt_sha256"))
    checks["V6"] = v6
    if not v6:
        reasons.append("V6_missing_trace_fields")

    decision = "REGISTER" if not reasons else "UNCONFIRMED_SAFE"
    entry = None
    if decision == "REGISTER":
        et = (item.get("entity_type") or "proper_noun").lower()
        if et in ("cascade_unresolved_entity", "ja_reading_katakana"):
            et = "proper_noun"
        entry = {
            "entity_type": et, "canonical_spelling": cs, "language_origin": item.get("language_origin", ""),
            "expected_pronunciation_ipa": item.get("expected_pronunciation_ipa", ""), "pronunciation_hint": hint,
            "alternate_pronunciations": [a for a in (item.get("alternate_pronunciations") or []) if a],
            "confidence": conf, "ambiguity_note": note, "sources": [url],
            "resolution_method": "en_web_research_trial", "resolved_at_stage": "trial_pre_tts",
            "tts_injection_disabled": True, "tts_injection_disabled_reason": f"{TRIAL_ID}: Trial、TTS注入なし",
            "trace": {"arm": arm, "quote": quote, **{k: meta.get(k) for k in ("retrieved_at", "model", "prompt_sha256", "response_id")}},
        }
    return {"decision": decision, "reasons": reasons, "checks": checks, "entry": entry, "surface": surface_in_text, "arm": arm}


def register_entry(ledger_path: str, surface: str, entry: dict) -> str:
    """Trial Ledgerにだけ登録(LEDGER_PATHをTrialIsolationが差替え済みの前提。path検査で実Ledger書込を拒否)。"""
    import er006_pronunciation_ledger_01 as led
    if os.path.abspath(led.LEDGER_PATH) != os.path.abspath(ledger_path):
        raise RuntimeError(f"[STOP] LEDGER_PATH不一致: {led.LEDGER_PATH} != {ledger_path}(Trial Ledger以外への書込を拒否)")
    if os.path.abspath(ledger_path) == os.path.abspath(os.path.join(ROOT, REAL_LEDGER_PATH)):
        raise RuntimeError("[STOP] 実Ledgerへの書込を拒否")
    e = {k: v for k, v in entry.items() if k != "trace"}
    key = led.LedgerKey(surface=surface, entity_type=e["entity_type"], source_context="")
    return led.upsert(key, e)


def get_pl_list(text: str) -> list:
    """Production caller(er003/er012)と同一式: get_hint_for_text(text, 'low') の canonical_spelling。"""
    import er006_pronunciation_ledger_01 as led
    return [h["canonical_spelling"] for h in led.get_hint_for_text(text, min_confidence="low")]


def m1_candidate_set(canonical_text: str, ledger_path: str) -> dict:
    """R-06: 共存時のM1候補集合(C2のledger_key別・candidate_set_hash)を記録する(凍結の読取のみ)。"""
    import er006_m1_multi_candidate_01 as m1
    snap = ledger_snapshot(ledger_path)
    fz = m1.freeze_candidates(canonical_text, ledger_snapshot=snap, segment_started_at=time.strftime("%Y-%m-%dT%H:%M:%S"))
    d = fz.to_dict()
    c2 = {w: [c for c in cs if str(c.get("source", "")).startswith("C2")] for w, cs in (d.get("words") or {}).items()}
    # candidate_set_hash(M1内部)は segment_started_at(時刻)を含むため毎回変わる。変化検出には時刻を除いた安定hashを併記する。
    stable = hashlib.sha1(json.dumps(d.get("words") or {}, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()[:16]
    return {"candidate_set_hash": fz.candidate_set_hash, "stable_candidates_hash": stable,
            "c2_by_word": {w: v for w, v in c2.items() if v}}
