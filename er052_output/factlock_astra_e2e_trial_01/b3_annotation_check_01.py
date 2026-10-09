# -*- coding: utf-8 -*-
"""B3注記仕様 v2 (B3_ANNOTATION_SPEC_v2.md) の決定論検証。LLM不使用・API支出0・既存ファイル非編集。

v1 -> v2 変更 (Opusレビュー8件反映):
  1 注記者用版の分離は文書側。本スクリプトはサイドカーの spec_sha256 / brief_sha256 / annotator を実ファイルと照合する。
  2 中核/周辺は注記者が選ばない。数値の表記・種類・台帳ID・概念から本スクリプトが計算し、サイドカー宣言(class)と
    完全一致を検査する (適格なのに上限内で周辺=付け漏れ も検出)。
  3 E1/E2 の数字比較: 全角->半角、先頭0・小数末尾0を除く10進数正規化、(numeric_scope: ...) を除外、
    照合対象は主数字(表記末尾の数字列、範囲なら両端)のみ。交差判定は廃止。
  4 E2->E2': 台帳 date_or_period の先頭の日付表現と表記の日付が一致 (年のみは対象外、Storyline出現は条件にしない)。
    ISO形式(2026-07-13 10:16 EDT)と和文(2026年9月14日)の両方を解釈。
  5 分割・段落正規化: 許す差分は「Selected Facts節内で 。 の直後に \\n- を挿入」「節の先頭行/'。\\n'直後に - を挿入」
    のみ (挿入の直後は必ず【事実N】)。挿入を逆に除いた結果が原文と厳密一致することを検査する (空白全削除比較は廃止)。
  6 上限式 max(3, min(6, floor(n/2))) は固定。優先順 Storylineにある量 -> その他の量 -> 日付。上限で外れた概念を報告。
  7 台帳外の記述は unmapped_claims に種類別で記録 (STOPしない)。STOP候補は2場合のみ警告として出す。
  8 サイドカー宣言の表記が本文に無い(架空)・概念の束ね不備・sha照合・台帳スキーマ点検・複合タグ禁止。

出典: strip_tags / TAG_RE / BROAD_TAG_RE / MARK_RE / ID_RE / FACT_LINE_RE は er052_factlock_writer_trial_01_run.py
(117-134行, 2026-10-09時点) の同一ロジックのコピー。既存ファイル編集禁止のためimportせず複製した
(本体が変わると乖離しうる)。harness load_core_numbers の年月日分解による周辺数値の見逃しは記録のみ (harness変更禁止)。
CLI: --brief <md> --annotated <md> --ledger <txt> [--json <注記版fact_selection_evidence.json>]
     [--json-orig <元JSON>] [--sidecar <annotation.json>] [--spec <注記者用仕様md>]
     [--emit-core-json <path>] [--out <結果json>]
終了コード: PASS=0 / FAIL=1
"""
import argparse
import hashlib
import json
import re
import sys
from decimal import Decimal, InvalidOperation

SPEC_ID = "B3_ANNOTATION_SPEC_v2"

# ---- 出典: er052_factlock_writer_trial_01_run.py 117-134行 (複製) ----
TAG_RE = re.compile(r"【事実\s*\d+(?:\s*[,、，・]\s*(?:事実\s*)?\d+)*】")
BROAD_TAG_RE = re.compile(r"【\s*[FＦ事実][^】\n]{0,30}】")
MARK_RE = re.compile(r"【(?:中核数値|周辺数値)】")
ID_RE = re.compile(r"(?<![A-Za-z0-9])[A-Z]{1,8}(?:-[A-Z]{1,4})?-\d{1,4}(?![A-Za-z0-9])")
FACT_LINE_RE = re.compile(r"^\s*(?:-|・)\s*【事実(\d+)】\s*(.*)$")


def strip_tags(text):
    t = TAG_RE.sub("", text or "")
    t = BROAD_TAG_RE.sub("", t)
    t = MARK_RE.sub("", t)
    return "\n".join(l.rstrip() for l in t.split("\n"))
# ---- 複製ここまで ----

SIMPLE_TAG_RE = re.compile(r"【事実(\d+)】")
MARK_OF = {"core": "【中核数値】", "peripheral": "【周辺数値】"}
COUNTABLE_KINDS = ("magnitude", "date_time", "range")
QUANTITY_KINDS = ("magnitude", "range")
NEVER_CORE_KINDS = ("name_embedded", "year", "ordinal")
ALL_KINDS = COUNTABLE_KINDS + NEVER_CORE_KINDS
UNMAPPED_TYPES = ("new_fact", "new_number", "new_causal", "generalization", "specification", "qualifier")
FW = str.maketrans("０１２３４５６７８９，．", "0123456789,.")
# 小数・千位区切りを1つの数字列として扱う
DIGIT_RUN = re.compile(r"\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?")
KANJI_NUM_CAND = re.compile(r"[一二三四五六七八九〇十百千万億兆]{2,}(?:年|円|人|件|％|%|ドル|個|倍|社|基)")
PCT_WIDTH_CAND = re.compile(r"[%％]")
QUANT_WORD_RE = re.compile(r"\d[\d,.]*\s*(?:％|%|ドル|円|個|台|人|件|倍|km|基|社|万|億|バレル|賛成|反対|棄権|ポイント|位)")
SCOPE_RE = re.compile(r"\(numeric_scope:.*?\)\s*$|\(numeric_scope:.*$")
NUM_ORDER = {"name_embedded": 0, "ordinal": 1, "year": 2, "range": 3, "date_time": 3, "magnitude": 4}


def fw(s):
    return (s or "").translate(FW)


def norm_nl(s):
    return (s or "").replace("\r\n", "\n").replace("\r", "\n")


def sha256(s):
    return hashlib.sha256((s or "").encode("utf-8")).hexdigest()


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def rstrip_lines(s):
    return "\n".join(l.rstrip() for l in norm_nl(s).split("\n"))


def prep(s):
    return rstrip_lines(s)


def nrm_num(s):
    """10進数正規化 ('04'->'4', '4.00'->'4', '1,500'->'1500')。変換不能は元の文字列。"""
    try:
        d = Decimal(s.replace(",", ""))
    except InvalidOperation:
        return s
    return format(d.normalize(), "f")


def digit_runs(s):
    return [nrm_num(m.group(0)) for m in DIGIT_RUN.finditer(fw(s))]


def main_numbers(surface, kind):
    """主数字: 表記末尾の数字列。範囲(kind=range)は両端。例 '1バレル85ドル'->['85'], '3〜5％'->['3','5']"""
    runs = digit_runs(surface)
    if not runs:
        return []
    if kind == "range" and len(runs) >= 2:
        return [runs[0], runs[-1]]
    return [runs[-1]]


# ------------------------------------------------------------------ 台帳
def parse_ledger(text):
    recs, cur = {}, None
    for line in norm_nl(text).split("\n"):
        m = re.match(r"^\[(\w+)(?:[^\]]*)\]\s+([A-Za-z0-9][A-Za-z0-9_-]*):\s*(.*)$", line)
        if m:
            cur = {"status": m.group(1), "id": m.group(2), "statement": m.group(3), "fields": {}}
            recs[m.group(2)] = cur
            continue
        m2 = re.match(r"^\s+([a-z_]+):\s*(.*)$", line)
        if cur and m2:
            cur["fields"][m2.group(1)] = m2.group(2)
    for r in recs.values():
        r["full"] = r["statement"] + "\n" + "\n".join(r["fields"].values())
    return recs


def strip_scope(s):
    return SCOPE_RE.sub("", s or "")


def ledger_schema(ledger):
    """台帳スキーマ点検: 各記録の欄の有無、欄名ごとの件数、代替規則(fallback)の要否、警告。"""
    presence = {}
    per_rec = {}
    for rid, r in ledger.items():
        per_rec[rid] = {"status": r["status"], "fields": sorted(r["fields"].keys())}
        for k in r["fields"]:
            presence[k] = presence.get(k, 0) + 1
    n = len(ledger)
    has_nv = presence.get("numeric_value", 0) > 0
    has_dp = presence.get("date_or_period", 0) > 0
    warns = []
    if not has_nv:
        warns.append("台帳に numeric_value 欄が1件も無い: 量のE1判定は statement 内の主数字で代替する (fallback)")
    else:
        for rid, r in ledger.items():
            if "numeric_value" not in r["fields"] and QUANT_WORD_RE.search(strip_scope(r["statement"])):
                warns.append(f"{rid}: statement に量を示す語があるが numeric_value 欄が無い (記録漏れの疑い)")
    if not has_dp:
        warns.append("台帳に date_or_period 欄が1件も無い: 日付のE2'判定は statement 内の先頭の日付表現で代替する (fallback)")
    non_verified = sorted(rid for rid, r in ledger.items() if r["status"] != "VERIFIED")
    if non_verified:
        warns.append(f"VERIFIED でない記録: {non_verified}")
    return {"records": n, "field_counts": presence,
            "numeric_value_fallback_to_statement": not has_nv,
            "date_or_period_fallback_to_statement": not has_dp,
            "non_verified_ids": non_verified, "per_record": per_rec, "warnings": warns}


def ledger_number_set(rec, schema):
    """E1用: numeric_value 欄(numeric_scope除外)の数字集合。欄名が台帳に無い場合のみ statement で代替。"""
    if schema["numeric_value_fallback_to_statement"]:
        src = strip_scope(rec["statement"])
    else:
        src = strip_scope(rec["fields"].get("numeric_value", ""))
    return set(digit_runs(src))


# ------------------------------------------------------------------ 日付
ISO_RE = re.compile(r"(\d{4})-(\d{1,2})(?:-(\d{1,2}))?(?:[ T](\d{1,2}):(\d{2}))?")
JA_RE = re.compile(r"(?:(\d{4})年)?(\d{1,2})月(?:(\d{1,2})日)?")
JA_DAY_RE = re.compile(r"(\d{1,2})日")
JA_YEAR_RE = re.compile(r"(\d{4})年")
JA_TIME_RE = re.compile(r"(午前|午後)?(\d{1,2})時(?:(\d{1,2})分)?")


def _i(x):
    return int(x) if x is not None else None


def _time(s, pos=0):
    m = JA_TIME_RE.match(s, pos) or JA_TIME_RE.search(s, pos)
    if not m:
        return None, None
    h = int(m.group(2))
    if m.group(1) == "午後" and h < 12:
        h += 12
    return h, _i(m.group(3))


def first_date_expr(s):
    """文字列中で最初に出現する日付表現 (ISO or 和文)。月が無い(年のみ)表現は日付表現とみなさない。"""
    s = fw(s)
    iso, ja = ISO_RE.search(s), JA_RE.search(s)
    cands = [(m.start(), k, m) for k, m in (("iso", iso), ("ja", ja)) if m]
    if not cands:
        return None
    _, kind, m = min(cands, key=lambda t: t[0])
    if kind == "iso":
        h = _i(m.group(4)) if m.group(4) else None
        mi = _i(m.group(5)) if m.group(5) else None
        return {"Y": _i(m.group(1)), "M": _i(m.group(2)), "D": _i(m.group(3)), "h": h, "m": mi}
    h, mi = _time(s, m.end())
    return {"Y": _i(m.group(1)), "M": _i(m.group(2)), "D": _i(m.group(3)), "h": h, "m": mi}


def parse_surface_date(surface):
    s = fw(surface)
    d = first_date_expr(s)
    if d:
        return d
    dm = JA_DAY_RE.search(s)
    ym = JA_YEAR_RE.search(s)
    h, mi = _time(s)
    return {"Y": _i(ym.group(1)) if ym else None, "M": None, "D": _i(dm.group(1)) if dm else None, "h": h, "m": mi}


def date_matches(sd, ld):
    """E2': 表記の日付成分が台帳の先頭日付表現と一致。月のない表記(年のみ・日のみ)は対象外。"""
    if not sd or not ld or sd.get("M") is None:
        return False
    for k in ("Y", "M", "D"):
        if sd.get(k) is not None and sd[k] != ld.get(k):
            return False
    if sd.get("h") is not None and sd["h"] != ld.get("h"):
        return False
    if sd.get("m") is not None and sd["m"] != ld.get("m"):
        return False
    return True


def ledger_first_date(rec, schema):
    if schema["date_or_period_fallback_to_statement"]:
        return first_date_expr(rec["statement"])
    return first_date_expr(rec["fields"].get("date_or_period", ""))


# ------------------------------------------------------------------ 本文の分節
def sections(text):
    """(storyline文, Selected Facts節の行リスト)"""
    story, facts, mode = [], [], None
    for line in norm_nl(text).split("\n"):
        h = line.strip()
        if h.startswith("## Storyline"):
            mode = "s"
            continue
        if h.startswith("## Selected Facts"):
            mode = "f"
            continue
        if h.startswith("## "):
            mode = None
            continue
        if mode == "s":
            story.append(line)
        elif mode == "f":
            facts.append(line)
    return "\n".join(story), facts


def facts_section_range(text):
    """prep済み text における Selected Facts 節 [start, end) (見出し行の次行頭から次の見出し行頭/末尾)。無ければ None"""
    m = re.search(r"^## Selected Facts[^\n]*\n?", text, re.M)
    if not m:
        return None
    start = m.end()
    m2 = re.search(r"^## ", text[start:], re.M)
    end = start + m2.start() if m2 else len(text)
    return start, end


# ------------------------------------------------------------------ 位置合わせ (許す差分は定義済み挿入のみ)
def align(orig, ann, ins_range=None):
    """annotated から【事実N】【中核/周辺数値】と定義済みの挿入だけを逆に除いた結果が orig と厳密一致するか。
    許す挿入 (ins_range=(s,e) の中のみ):
      (L1) 直前の本文文字が 。 のとき '\\n- ' (直後は必ず【事実N】)
      (L2) 節の先頭行の行頭、または直前が '。\\n' のとき '- ' (直後は必ず【事実N】)
    戻り値: {ok, reason, events:[(orig_offset, 'tag'|'mark', text)], ops:[(orig_offset, str)]}"""
    i = j = 0
    events, ops = [], []
    last, last2 = "", ""
    seen_nonws_in_range = False
    n, m_ = len(ann), len(orig)
    s_, e_ = ins_range if ins_range else (None, None)
    while i < n:
        m = TAG_RE.match(ann, i)
        if m:
            events.append((j, "tag", m.group(0)))
            i = m.end()
            continue
        m = MARK_RE.match(ann, i)
        if m:
            events.append((j, "mark", m.group(0)))
            i = m.end()
            continue
        if j < m_ and ann[i] == orig[j]:
            ch = ann[i]
            if s_ is not None and s_ <= j < e_ and not ch.isspace():
                seen_nonws_in_range = True
            last2, last = last, ch
            i += 1
            j += 1
            continue
        in_rng = s_ is not None and s_ <= j <= e_
        if in_rng:
            if ann.startswith("\n- ", i) and last == "。" and TAG_RE.match(ann, i + 3):
                ops.append((j, "\n- "))
                i += 3
                last, last2 = " ", "-"
                continue
            if ann.startswith("- ", i) and TAG_RE.match(ann, i + 2) and \
                    ((not seen_nonws_in_range) or (last2 == "。" and last == "\n") or (last == "\n" and re.search(r"。\n+$", orig[max(0, j - 12):j]))):  # 委任_09 P3
                ops.append((j, "- "))
                i += 2
                last, last2 = " ", "-"
                continue
        ctx_a = ann[max(0, i - 10):i + 20].replace("\n", "\\n")
        ctx_o = orig[max(0, j - 10):j + 20].replace("\n", "\\n")
        return {"ok": False, "reason": f"許されない差分: 注記版[{ctx_a}] 原文[{ctx_o}] (注記版位置{i}, 原文位置{j})",
                "events": events, "ops": ops}
    if j != m_:
        return {"ok": False, "reason": f"原文の末尾が注記版に無い (原文位置{j}/{m_})", "events": events, "ops": ops}
    return {"ok": True, "reason": "", "events": events, "ops": ops}


def align_md(brief, annotated):
    """md全体の位置合わせ。座標は prep(brief) 上の絶対位置。"""
    b, a = prep(brief), prep(annotated)
    rng = facts_section_range(b)
    r = align(b, a, rng)
    r["brief_prepped"] = b
    r["section_range"] = rng
    if rng is None:
        r["ok"] = False
        r["reason"] = "元briefに '## Selected Facts' 節が無い (分割規則の適用不能)"
    return r


def check_a(brief, annotated, sidecar=None):
    r = align_md(brief, annotated)
    layout_ops = [o for o in r["ops"]]
    split_ins = [o for o in layout_ops if o[1] == "\n- "]
    bullet_ins = [o for o in layout_ops if o[1] == "- "]
    strict = prep(brief) == strip_tags(norm_nl(annotated))
    if not r["ok"]:
        status = "FAIL"
    else:
        status = "PASS" if not layout_ops else "PASS_LAYOUT_NORMALIZED"
    return {"status": status, "reason": r["reason"], "strict_equal_after_strip": strict,
            "inserted_split_breaks": len(split_ins), "inserted_bullet_markers": len(bullet_ins),
            "brief_sha256": sha256(prep(brief)), "stripped_annotated_sha256": sha256(strip_tags(norm_nl(annotated)))}


def check_json(json_annot, json_orig, brief, sidecar=None):
    out = {"status": "PASS", "notes": []}
    ta = json_annot.get("selected_fact_brief_text", "")
    if json_orig is not None:
        to = json_orig.get("selected_fact_brief_text", "")
        r = align(prep(to), prep(ta), (0, len(prep(to))))
        rest_a = {k: v for k, v in json_annot.items() if k != "selected_fact_brief_text"}
        rest_o = {k: v for k, v in json_orig.items() if k != "selected_fact_brief_text"}
        out.update(aligned=r["ok"], reason=r["reason"], other_keys_identical=(rest_a == rest_o),
                   inserted_ops=len(r["ops"]))
        if not r["ok"] or rest_a != rest_o:
            out["status"] = "FAIL"
    else:
        out["notes"].append("json_orig_missing: 弱い検査のみ(stripped各非空行が元briefに含まれるか)")
        bn = re.sub(r"\s+", "", brief)
        miss = [l for l in strip_tags(norm_nl(ta)).split("\n")
                if l.strip() and re.sub(r"^(?:-|・)", "", re.sub(r"\s+", "", l)) not in bn]
        out["lines_not_in_brief"] = miss
        if miss:
            out["status"] = "FAIL"
    out["fact_tags"] = [int(x) for x in re.findall(r"【事実(\d+)】", ta)]
    return out


def check_d(annotated):
    story, facts = sections(annotated)
    ns, problems = [], []
    for line in facts:
        m = FACT_LINE_RE.match(line)
        if m:
            ns.append(int(m.group(1)))
            body = m.group(2).lstrip()
            if body.startswith("Storyline") or body.startswith("素材"):
                problems.append(f"【事実{m.group(1)}】が非事実行(Storyline/素材)に付いている")
    text = norm_nl(annotated)
    all_tags = [int(x) for x in re.findall(r"【事実(\d+)】", text)]
    if ns != all_tags:
        problems.append("【事実N】が箇条書き行頭以外(Storyline/節外/行中)に存在する")
    if ns != list(range(1, len(ns) + 1)):
        problems.append(f"連番でない/重複: {ns}")
    if not ns:
        problems.append("【事実N】が0件")
    compound = [t for t in TAG_RE.findall(text) if not SIMPLE_TAG_RE.fullmatch(t)]
    if compound:
        problems.append(f"複合タグは禁止 (v2): {sorted(set(compound))}")
    unknown = [t for t in re.findall(r"【[^】\n]*】", text)
               if not (TAG_RE.fullmatch(t) or MARK_RE.fullmatch(t))]
    if unknown:
        problems.append(f"未知の【】印: {sorted(set(unknown))}")
    return {"status": "FAIL" if problems else "PASS", "fact_numbers": ns, "problems": problems}


def check_b(annotated, ledger, sidecar, d_res):
    ns = set(d_res["fact_numbers"])
    if sidecar is None:
        ids = [i for i in ID_RE.findall(norm_nl(annotated)) if i in ledger]
        return {"status": "SKIPPED_NO_SIDECAR", "explicit_ledger_ids_in_text": sorted(set(ids))}
    problems, mapping, warns, ambiguous_facts = [], {}, [], {}
    for f in sidecar.get("facts", []):
        n, ids = f.get("n"), f.get("ledger_ids", [])
        mapping[n] = ids
        if not ids:
            problems.append(f"事実{n}: ledger_idsが空")
        for i in ids:
            if i not in ledger:
                problems.append(f"事実{n}: 台帳に存在しないID {i}")
            elif ledger[i]["status"] == "AMBIGUOUS":
                # 委任_10 運用明確化(c): AMBIGUOUS台帳IDへの紐付けは許容(WARN)+ambiguous_factフラグ。評価時は別集計(PREREG v2.2 5-12)
                warns.append(f"事実{n}: 台帳ID {i} は AMBIGUOUS (ambiguous_fact)")
                ambiguous_facts.setdefault(n, []).append(i)
            elif ledger[i]["status"] != "VERIFIED":
                problems.append(f"事実{n}: 台帳ID {i} の status が VERIFIED でない ({ledger[i]['status']})")
    if set(mapping) != ns:
        problems.append(f"サイドカーfacts {sorted(mapping)} と注記版の【事実N】 {sorted(ns)} が不一致")
    _, facts = sections(annotated)
    for line in facts:
        m = FACT_LINE_RE.match(line)
        if m:
            for i in ID_RE.findall(m.group(2)):
                if i in ledger and i not in mapping.get(int(m.group(1)), []):
                    problems.append(f"事実{m.group(1)}: 本文に明示された台帳ID {i} がledger_idsにない")
    return {"status": "FAIL" if problems else "PASS", "mapping": mapping, "problems": problems, "warnings": warns,
            "ambiguous_fact": {str(k): v for k, v in sorted(ambiguous_facts.items())}}


# ------------------------------------------------------------------ 数値: 計算
def _norm_items(sidecar_numbers):
    items = []
    for n in sidecar_numbers:
        ids = n.get("ledger_ids")
        if ids is None:
            ids = [n["ledger_id"]] if n.get("ledger_id") else []
        items.append({"surface": n["surface"], "kind": n.get("kind"), "class": n.get("class"),
                      "concept": n.get("concept") or n["surface"], "ledger_ids": list(ids),
                      "role": n.get("role", "")})
    return items


def _item_eligibility(it, ledger, schema):
    """('E1'|'E2p'|None)。適格性は表記の種類で決まる: 量/範囲->E1、日付->E2'、それ以外は常に不適格。"""
    kind = it["kind"]
    recs = [ledger[i] for i in it["ledger_ids"] if i in ledger]
    if kind in QUANTITY_KINDS:
        mn = main_numbers(it["surface"], kind)
        if mn and any(set(mn) <= ledger_number_set(r, schema) for r in recs):
            return "E1"
    elif kind == "date_time":
        sd = parse_surface_date(it["surface"])
        if any(date_matches(sd, ledger_first_date(r, schema)) for r in recs):
            return "E2p"
    return None


def compute_expected(items, ledger, schema, plain_text, story_text):
    """概念単位の適格性・上限・優先順から、各概念の期待分類を計算する。"""
    plain_fw, story_fw = fw(plain_text), fw(story_text)
    concepts = {}
    for it in items:
        concepts.setdefault(it["concept"], []).append(it)
    info = {}
    for cid, its in concepts.items():
        kinds = sorted({i["kind"] for i in its}, key=lambda k: NUM_ORDER.get(k, 9))
        kind = kinds[0] if kinds else None            # 先頭要素ではなく全要素から最も保守的な種類を採る
        elig = sorted({e for e in (_item_eligibility(i, ledger, schema) for i in its) if e})
        poses = [plain_fw.find(fw(i["surface"])) for i in its]
        poses = [p for p in poses if p >= 0]
        in_story = any(fw(i["surface"]) in story_fw for i in its)
        if kind in QUANTITY_KINDS:
            group = 0 if in_story else 1
        elif kind == "date_time":
            group = 2
        else:
            group = 9
        info[cid] = {"kind": kind, "kinds": kinds, "eligible": elig, "first_pos": min(poses) if poses else 10 ** 9,
                     "in_storyline": in_story, "group": group, "countable": kind in COUNTABLE_KINDS,
                     "surfaces": [i["surface"] for i in its]}
    n = sum(1 for v in info.values() if v["countable"])
    cap = max(3, min(6, n // 2))
    elig_list = sorted([c for c, v in info.items() if v["eligible"] and v["kind"] not in NEVER_CORE_KINDS],
                       key=lambda c: (info[c]["group"], info[c]["first_pos"]))
    core = elig_list[:cap]
    dropped = elig_list[cap:]
    for c, v in info.items():
        v["expected_class"] = "core" if c in core else "peripheral"
    return {"concepts": info, "countable_concepts": n, "core_cap": cap, "expected_core": core,
            "cap_dropped": dropped, "eligible_concepts": elig_list}


def check_concept_bundling(items):
    """概念の束ね不備 (Opus 8): 概念内の台帳ID・種類の不一致、別概念なのに短い表記が長い表記に含まれる/同一主数字。"""
    problems = []
    by = {}
    for it in items:
        by.setdefault(it["concept"], []).append(it)
    for cid, its in by.items():
        kinds = {i["kind"] for i in its}
        if len(kinds) > 1:
            problems.append(f"概念 {cid}: 表記間で kind が割れている {sorted(k or '' for k in kinds)}")
        common = set(its[0]["ledger_ids"])
        for i in its[1:]:
            common &= set(i["ledger_ids"])
        if len(its) > 1 and not common:
            problems.append(f"概念 {cid}: 表記間で台帳IDに共通がない (別概念にすべき)")
    cids = list(by)
    for a in range(len(cids)):
        for b in range(a + 1, len(cids)):
            A, B = by[cids[a]], by[cids[b]]
            kinds = {i["kind"] for i in A + B}
            if kinds & {"year", "ordinal", "name_embedded"}:
                continue
            for x in A:
                for y in B:
                    if not (set(x["ledger_ids"]) & set(y["ledger_ids"])):
                        continue
                    sx, sy = fw(x["surface"]), fw(y["surface"])
                    if sx in sy or sy in sx:
                        problems.append(f"概念 {cids[a]} と {cids[b]}: 短い表記が長い表記に含まれ台帳IDも共通なのに別概念 "
                                        f"('{x['surface']}' / '{y['surface']}')")
                    elif x["kind"] in QUANTITY_KINDS and y["kind"] in QUANTITY_KINDS and \
                            main_numbers(x["surface"], x["kind"]) == main_numbers(y["surface"], y["kind"]):
                        problems.append(f"概念 {cids[a]} と {cids[b]}: 台帳ID共通・主数字同一なのに別概念 "
                                        f"('{x['surface']}' / '{y['surface']}')")
    return sorted(set(problems))


def check_c(annotated, ledger, sidecar, schema=None):
    if sidecar is None:
        return {"status": "SKIPPED_NO_SIDECAR"}
    schema = schema or ledger_schema(ledger)
    items = _norm_items(sidecar.get("numbers", []))
    problems, warns, info = [], [], {"surface_diff": []}
    story, _ = sections(annotated)
    ann_n = norm_nl(annotated)
    plain = strip_tags(ann_n)
    text = TAG_RE.sub("", fw(ann_n))
    story_plain = strip_tags(story)
    # --- 宣言の基本検査
    seen = {}
    for it in items:
        s = fw(it["surface"])
        if it["kind"] not in ALL_KINDS:
            problems.append(f"{it['surface']}: kind '{it['kind']}' が不正")
        if it["class"] not in MARK_OF:
            problems.append(f"{it['surface']}: class '{it['class']}' が不正")
        if s in seen and seen[s] != it["class"]:
            problems.append(f"同一表記の分類衝突: {it['surface']}")
        seen[s] = it["class"]
        if s not in fw(plain):
            problems.append(f"宣言された表記 '{it['surface']}' が本文に1回も出現しない (架空の数値宣言)")
        if re.fullmatch(r"(?:19|20)\d{2}年", s) and it["kind"] != "year":
            problems.append(f"{it['surface']}: 年のみの表記は kind=year でなければならない")
        if re.fullmatch(r"第\d+[条回章項号節]", s) and it["kind"] not in ("ordinal", "name_embedded"):
            warns.append(f"{it['surface']}: 序数に見えるが kind={it['kind']}")
    problems += check_concept_bundling(items)
    # --- 台帳照合
    stop_candidates = []
    for it in items:
        recs = [ledger[i] for i in it["ledger_ids"] if i in ledger]
        is_core = it["class"] == "core"
        if not recs:
            (problems if is_core else warns).append(f"{it['surface']}: ledger_ids {it['ledger_ids']} が台帳にない")
            if fw(it["surface"]) in fw(story_plain) and it["kind"] in COUNTABLE_KINDS:
                stop_candidates.append(f"{it['surface']}: 台帳に無い数字がStoryline(記事の中心)に有る [STOP候補(ii)]")
            continue
        if not any(set(digit_runs(it["surface"])) <= set(digit_runs(r["full"])) for r in recs):
            (problems if is_core else warns).append(f"{it['surface']}: 数字が台帳 {it['ledger_ids']} に存在しない")
            if fw(it["surface"]) in fw(story_plain) and it["kind"] in COUNTABLE_KINDS:
                stop_candidates.append(f"{it['surface']}: 台帳に無い数字がStorylineに有る [STOP候補(ii)]")
        elif not any(it["surface"] in r["full"] or fw(it["surface"]) in fw(r["full"]) for r in recs):
            info["surface_diff"].append({"surface": it["surface"], "ledger_ids": it["ledger_ids"]})
    # --- 計算 vs 宣言
    exp = compute_expected(items, ledger, schema, plain, story_plain)
    concepts = {}
    for it in items:
        concepts.setdefault(it["concept"], []).append(it)
    declared_core = []
    for cid, its in concepts.items():
        if len({i["class"] for i in its}) > 1:
            problems.append(f"概念 {cid}: 表記間で分類が割れている")
        if its[0]["class"] == "core":
            declared_core.append(cid)
    for cid, v in exp["concepts"].items():
        declared = concepts[cid][0]["class"]
        if declared != v["expected_class"]:
            if v["expected_class"] == "core":
                problems.append(f"概念 {cid} {v['surfaces']}: 規則では中核(適格 {v['eligible']}、上限{exp['core_cap']}内)なのに周辺と宣言 (付け漏れ)")
            elif declared == "core" and v["kind"] in NEVER_CORE_KINDS:
                problems.append(f"概念 {cid}: kind {v['kind']} は中核にできない")
            elif declared == "core" and not v["eligible"]:
                problems.append(f"概念 {cid} {v['surfaces']}: 中核適格性なし (E1=量が台帳numeric_valueの主数字と一致 / "
                                f"E2'=日付が台帳date_or_periodの先頭日付表現と一致、のどちらでもない)")
            elif declared == "core":
                problems.append(f"概念 {cid} {v['surfaces']}: 適格だが上限{exp['core_cap']}または優先順で中核に入らない (規則では周辺)")
    info.update(eligibility={c: v["eligible"] for c, v in exp["concepts"].items()},
                countable_concepts=exp["countable_concepts"], core_cap=exp["core_cap"],
                expected_core_concepts=exp["expected_core"], declared_core_concepts=sorted(declared_core),
                cap_dropped_concepts=exp["cap_dropped"], cap_dropped_count=len(exp["cap_dropped"]),
                eligible_concepts=exp["eligible_concepts"],
                concept_detail={c: {k: v[k] for k in ("kind", "eligible", "group", "in_storyline", "expected_class")}
                                for c, v in exp["concepts"].items()})
    # --- 印の位置・分類漏れ
    masked = ID_RE.sub(lambda m: "\0" * len(m.group(0)), text)
    # delegation11: ハイフン無し台帳ID(F01等)もledgerキーに限りマスク(本文括弧内の番号を数字として誤検出しない)
    _lids = sorted((k for k in ledger if isinstance(k, str) and k), key=len, reverse=True)
    if _lids:
        _lre = re.compile(r"(?<![A-Za-z0-9])(?:" + "|".join(re.escape(k) for k in _lids) + r")(?![A-Za-z0-9])")
        masked = _lre.sub(lambda m: "\0" * len(m.group(0)), masked)
    if items:
        alts = sorted({fw(i["surface"]) for i in items}, key=len, reverse=True)
        pat = re.compile("(" + "|".join(re.escape(a) for a in alts) + ")(【中核数値】|【周辺数値】)?")
        covered, attached = [], set()
        for m in pat.finditer(masked):
            exp_mark = MARK_OF[seen[m.group(1)]]
            if m.group(2) != exp_mark:
                problems.append(f"印の不一致/欠落: '{m.group(1)}' (期待 {exp_mark}, 実際 {m.group(2)}) 位置{m.start()}")
            covered.append((m.start(), m.end(1)))
            if m.group(2):
                attached.add(m.end(1))
        orphan = [m.start() for m in MARK_RE.finditer(masked) if m.start() not in attached]
        if orphan:
            problems.append(f"宣言された数値表記に付いていない印が {len(orphan)} 個")
        plain_m = MARK_RE.sub(lambda m: "\0" * len(m.group(0)), masked)
        unc = [m.group(0) for m in DIGIT_RUN.finditer(plain_m)
               if not any(s <= m.start() and m.end() <= e for s, e in covered)]
    else:
        unc = DIGIT_RUN.findall(MARK_RE.sub("", masked))
    if unc:
        problems.append(f"分類漏れの数字(宣言なし・印なし): {unc}")
    kc = KANJI_NUM_CAND.findall(plain)
    info["kanji_numeral_candidates"] = kc
    if kc:
        warns.append("漢数字の数量表現あり(対象外。annotation_notesに記録すること)[持ち越し]")
    if PCT_WIDTH_CAND.search(plain):
        info["percent_sign_variants"] = sorted(set(PCT_WIDTH_CAND.findall(plain)))
        if len(info["percent_sign_variants"]) > 1:
            warns.append("％と%が混在 (NFKC差。警告のみ)[持ち越し]")
    info["stop_candidates"] = stop_candidates
    return {"status": "FAIL" if problems else "PASS", "problems": problems, "warnings": warns, **info}


def check_e_sidecar(sidecar, spec_sha256=None, brief_sha256=None):
    """サイドカーの自己申告 (spec_sha256 / brief_sha256 / annotator / unmapped_claims) を実ファイルと照合"""
    if sidecar is None:
        return {"status": "SKIPPED_NO_SIDECAR"}
    problems, warns = [], []
    if sidecar.get("annotator") not in ("A", "B", "MERGED"):
        problems.append(f"annotator が A/B/MERGED でない: {sidecar.get('annotator')!r}")
    for key, actual in (("spec_sha256", spec_sha256), ("brief_sha256", brief_sha256)):
        if actual is None:
            warns.append(f"{key}: 照合用の実ファイル未指定 (SKIPPED)")
        elif sidecar.get(key) != actual:
            problems.append(f"{key} が実ファイルと一致しない: サイドカー {sidecar.get(key)!r} / 実 {actual!r}")
    for k, c in enumerate(sidecar.get("unmapped_claims", [])):
        if isinstance(c, dict):
            if c.get("type") not in UNMAPPED_TYPES:
                problems.append(f"unmapped_claims[{k}]: type は {UNMAPPED_TYPES} のいずれか")
        else:
            warns.append(f"unmapped_claims[{k}]: 種類別(dict: text/type)でない")
    return {"status": "FAIL" if problems else "PASS", "problems": problems, "warnings": warns,
            "unmapped_claims_by_type": _count_types(sidecar.get("unmapped_claims", []))}


def _count_types(claims):
    out = {}
    for c in claims:
        t = c.get("type") if isinstance(c, dict) else "untyped"
        out[t] = out.get(t, 0) + 1
    return out


def build_core_json(sidecar, slug="", brief="", ledger=None, annotated=None):
    """サイドカーの class (検査で計算結果との一致を確認済みの前提) から harness 互換形式を生成。"""
    core = {}
    for n in sidecar.get("numbers", []):
        if n["class"] == "core":
            c = n.get("concept") or n["surface"]
            core.setdefault(c, {"id": c, "literals": [], "role": n.get("role", "")})["literals"].append(n["surface"])
    peri = [n["surface"] for n in sidecar.get("numbers", []) if n["class"] == "peripheral"]
    return {"slug": slug, "brief": brief, "core": list(core.values()), "peripheral": peri,
            "reason": f"{SPEC_ID} に基づく (サイドカーから機械生成。分類は仕様の計算結果と一致を検査済み)",
            "max_core_per_article": 6}


def run(brief, annotated, ledger_text, sidecar=None, json_annot=None, json_orig=None,
        spec_sha256=None, brief_sha256=None):
    ledger = parse_ledger(ledger_text)
    schema = ledger_schema(ledger)
    res = {"spec": SPEC_ID, "ledger_records": len(ledger)}
    res["f_ledger_schema"] = {"status": "INFO", **schema}
    res["a_strip_equal"] = check_a(brief, annotated, sidecar)
    if json_annot is not None:
        res["a_json"] = check_json(json_annot, json_orig, norm_nl(brief), sidecar)
    res["d_sequence"] = check_d(annotated)
    res["b_ledger_mapping"] = check_b(annotated, ledger, sidecar, res["d_sequence"])
    res["c_numbers"] = check_c(annotated, ledger, sidecar, schema)
    res["e_sidecar_meta"] = check_e_sidecar(sidecar, spec_sha256, brief_sha256)
    if json_annot is not None and res["d_sequence"]["fact_numbers"] != res["a_json"]["fact_tags"]:
        res["a_json"]["status"] = "FAIL"
        res["a_json"]["notes"].append("JSON内の【事実N】がmdと一致しない")
    stats = [v.get("status", "") for v in res.values() if isinstance(v, dict)]
    res["skipped"] = [k for k, v in res.items() if isinstance(v, dict) and str(v.get("status", "")).startswith("SKIPPED")]
    res["verdict"] = "FAIL" if any(s == "FAIL" for s in stats) else "PASS"
    return res


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--brief", required=True)
    ap.add_argument("--annotated", required=True)
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--json")
    ap.add_argument("--json-orig")
    ap.add_argument("--sidecar")
    ap.add_argument("--spec", help="注記者用仕様md (サイドカーの spec_sha256 と実ファイルの照合)")
    ap.add_argument("--emit-core-json")
    ap.add_argument("--out")
    a = ap.parse_args(argv)

    def rd(p):
        return open(p, encoding="utf-8", newline="").read()

    def rb(p):
        return open(p, "rb").read()
    sidecar = json.loads(rd(a.sidecar)) if a.sidecar else None
    res = run(rd(a.brief), rd(a.annotated), rd(a.ledger), sidecar,
              json.loads(rd(a.json)) if a.json else None, json.loads(rd(a.json_orig)) if a.json_orig else None,
              spec_sha256=sha256_bytes(rb(a.spec)) if a.spec else None,
              brief_sha256=sha256_bytes(rb(a.brief)))
    if a.emit_core_json and sidecar and res["verdict"] == "PASS":
        json.dump(build_core_json(sidecar), open(a.emit_core_json, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    s = json.dumps(res, ensure_ascii=False, indent=2)
    if a.out:
        open(a.out, "w", encoding="utf-8").write(s)
    print(s)
    return 0 if res["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
