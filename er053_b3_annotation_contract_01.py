# -*- coding: utf-8 -*-
"""er053_b3_annotation_contract_01.py
RISK-FLAGGER-PRODUCTION-WIRING-01 Phase 2 C1(追加のみ、2026-10-10)。注記済みB3 入力契約の検証module(DESIGN_03 3節+15-2)。

新Writer W-1 は「注記済みB3 artifact」だけを受け取る。注記なしの selected_brief.md をWriterへ渡す経路は
**コード上に存在させない**(runtime switch・CLI引数・環境変数・自動フォールバックなし)。契約違反は課金前に
AnnotatedB3ContractViolation(STOP)。検証は**構造検証(技術QA、T-19)**であり、Factの内容の正誤判定ではない。
注記ロジック(Lane B: B3-ANNOTATION-AUTOMATION-TRIAL-01)はimportしない(Trial module import禁止)。

Artifact(<out_dir>/storyline_b3/):
  selected_brief.md            既存(注記前のB3出力。無変更)
  selected_brief_annotated.md  必須: 注記済みbrief(# Selected Fact Brief / ## Storyline / ## Selected Facts、Facts各行 `- 【事実N】本文`)
  annotation.json              必須: サイドカー(slug/annotator/spec_sha256/brief_sha256/facts/numbers/unmapped_claims/annotation_notes)
  annotation_manifest.json     必須: 整合manifest(schema_version=b3_annotation_manifest_v1)
  + <out_dir>/research_ledger/verified_fact_ledger.txt(台帳。sha整合・ID整合の対象)

検査:
  V1 5ファイルの存在・UTF-8読込・JSON構文(+サイドカーschema)
  V2 manifest schema_version一致・必須キー
  V3 sha整合(selected_brief.md / 台帳 / annotated md / sidecar が manifest の値と一致=stale・改竄・取り違え検知)
  V4 parse_brief_md成功(## Storyline / ## Selected Facts、空でない)
  V5 Selected Facts の空でない全行が FACT_LINE_RE に一致、番号が1..Kで連続・重複なし、タグは【事実N】のみ(変形タグ・行中タグなし)
     [解釈追加1] Facts節の先頭の空でない行が「Storyline:」または「Storyline：」で始まりStorylineの重複そのものである場合のみ、
       B3(build_selected_brief_markdown)の既存出力形式としてその1行を除外する。実Trial注記成果物9本のうち2本(small_bag,
       openai_copyright)がこの形式。DESIGN_03 15-2 V5強化の字義(全行一致)への解釈追加=C1報告で明示。
  V6 数値印は【中核数値】/【周辺数値】のみ。全ての印は直前がサイドカー numbers の surface(class対応: core=中核/peripheral=周辺)で
     あること、numbers の各surfaceは本文に印付きで最低1回出現すること。
     [解釈変更2] DESIGN_03 3-3 V6の字義「印の総数 == サイドカー numbers 件数」は実Trial成果物と整合しない(サイドカー numbers は
       distinct surface の一覧であり、同じ数字がStorylineとFactsの両方に出れば印は複数回出る。実測9本中5本が不一致)。
       出現ベースの整合に置換した。C1報告で明示。
  V7 サイドカー facts[].n の集合 == V5のN集合、facts[].ledger_ids が台帳に実在
  V8 manifest.checks 5項目が全て PASS / PASS_LAYOUT_NORMALIZED
  V9 sidecar.spec_sha256 == manifest.spec_sha256、sidecar.brief_sha256 == manifest.source_selected_brief_sha256
  V10 [C4追記: annotator=DETERMINISTICのとき、Fact本文の原本は selected_brief.md のFactsではなく「台帳+選択IDからの決定論再導出(D-full)」。
       制約ブロック(writer_constraints.txt)も再導出と一致。V2/V3: DETERMINISTICはmanifest.writer_constraints_sha256必須、あればファイル存在・sha整合]
  V10 Storyline完全一致 + タグ・数値印を除いた事実本文の連結が、空白・箇条記号・改行を除いて原Factsと一致(文字列一致であり内容判定ではない)
     [解釈追加3] 注記済みStorylineには数値印が付く(実Trial成果物9本中5本)ため、Storylineは**数値印・タグを除去した後**に原Storylineと完全一致を要求する。
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass, field

import er053_family_x_factlock_ja_writer_01 as w1
import er053_risk_flagger_production_01 as rfm

MANIFEST_SCHEMA_VERSION = "b3_annotation_manifest_v1"
MANIFEST_REQUIRED_KEYS = ("schema_version", "producer", "source_selected_brief_sha256", "ledger_sha256", "annotated_md_sha256",
                          "sidecar_sha256", "spec_sha256", "generated_at", "checks", "model_ids")
CHECK_KEYS = ("a_alignment", "b_numbers", "c_core_peripheral", "d_tags", "e_sidecar")
CHECK_OK = ("PASS", "PASS_LAYOUT_NORMALIZED")
# F8: Productionで許容するannotatorは DETERMINISTIC のみ(Lane B=LLM注記はREJECTED)。A/B/MERGEDはTrial成果物の検査側(Trial checker)にのみ残る。
ANNOTATORS = ("DETERMINISTIC",)     # DETERMINISTIC=決定論producer(er053_b3_deterministic_producer_01)
DETERMINISTIC = "DETERMINISTIC"

BRIEF_NAME = "selected_brief.md"
ANNOTATED_NAME = "selected_brief_annotated.md"
SIDECAR_NAME = "annotation.json"
MANIFEST_NAME = "annotation_manifest.json"
CONSTRAINTS_NAME = "writer_constraints.txt"        # C4: 制約ブロック(Writerのニュース欄に注記済みFactの後ろへ連結される別欄。manifest.writer_constraints_sha256で束縛)
LEDGER_REL = os.path.join("research_ledger", "verified_fact_ledger.txt")
_BULLET_RE = re.compile(r"^\s*(?:-|・)\s*")
_ANY_NUM_MARK_RE = re.compile(r"【[^】\n]*数値[^】\n]*】")
_CLASS_MARK = {"core": "【中核数値】", "peripheral": "【周辺数値】"}
_STORY_DUP_RE = re.compile(r"^\s*Storyline[:：]\s*(.*)$")


class AnnotatedB3ContractViolation(RuntimeError):
    """注記済みB3 入力契約の違反。API呼出前(課金0)にSTOPする。"""

    def __init__(self, violations: list):
        self.violations = violations
        head = "; ".join(f"{v['check']} {v['detail']}" for v in violations[:6])
        super().__init__(f"[STOP] ANNOTATED_B3_CONTRACT_VIOLATION: {head}")


@dataclass
class AnnotatedB3:
    out_dir: str
    storyline: str
    facts_text: str                 # parse_brief_md が返す注記済みFacts節
    annotated_md_text: str          # Writerへ渡す注記済みmd全文(text mode読込)
    annotated_md_path: str
    annotated_md_sha256: str
    sidecar: dict
    manifest: dict
    producer: str
    fact_numbers: list = field(default_factory=list)
    constraints_text: str = ""        # C4: 制約ブロック(空=制約なし)
    news_field_text: str = ""         # C4: Writer R0 [ニュース]欄の唯一の文字列 = 注記済みFacts + 制約ブロック(制約が空ならFactsのみ)


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _norm_text(s: str) -> str:
    """V10用: タグ・数値印を除去 -> 各行頭の箇条記号を除去 -> 空白・改行を全除去。"""
    t = w1.strip_tags(s)
    lines = [_BULLET_RE.sub("", ln) for ln in t.split("\n")]
    return re.sub(r"\s+", "", "".join(lines))


def _write_violation(out_dir: str, violations: list) -> None:
    try:
        p = os.path.join(out_dir, "storyline_b3", "audit", "contract_violation.json")
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump({"error": "ANNOTATED_B3_CONTRACT_VIOLATION", "violations": violations}, f, ensure_ascii=False, indent=2)
    except OSError:
        pass


def _fail(out_dir: str, violations: list):
    _write_violation(out_dir, violations)
    raise AnnotatedB3ContractViolation(violations)


def validate_annotated_b3(out_dir: str) -> AnnotatedB3:
    """契約違反は AnnotatedB3ContractViolation(contract_violation.jsonに内訳保存)。引数はout_dirのみ(switch無し)。"""
    sdir = os.path.join(out_dir, "storyline_b3")
    paths = {"brief": os.path.join(sdir, BRIEF_NAME), "annotated": os.path.join(sdir, ANNOTATED_NAME),
             "sidecar": os.path.join(sdir, SIDECAR_NAME), "manifest": os.path.join(sdir, MANIFEST_NAME),
             "ledger": os.path.join(out_dir, LEDGER_REL)}
    V = []

    def bad(check, detail):
        V.append({"check": check, "detail": detail})

    # ---------------- V1 ----------------
    raw, text = {}, {}
    for k, p in paths.items():
        if not os.path.isfile(p):
            bad("V1", f"missing file: {os.path.relpath(p, out_dir)}")
            continue
        try:
            raw[k] = open(p, "rb").read()
            text[k] = raw[k].decode("utf-8")
        except (OSError, UnicodeDecodeError) as e:
            bad("V1", f"unreadable ({type(e).__name__}): {os.path.relpath(p, out_dir)}")
    if V:
        _fail(out_dir, V)
    js = {}
    for k in ("sidecar", "manifest"):
        try:
            js[k] = json.loads(text[k])
            if not isinstance(js[k], dict):
                raise ValueError("not an object")
        except ValueError as e:
            bad("V1", f"invalid json: {k} ({e})")
    if V:
        _fail(out_dir, V)
    sc, mf = js["sidecar"], js["manifest"]
    # サイドカーschema(構造のみ)
    if sc.get("annotator") not in ANNOTATORS:
        bad("V1", "sidecar.annotator must be DETERMINISTIC")
    for key in ("slug", "spec_sha256", "brief_sha256"):
        if not isinstance(sc.get(key), str) or not sc.get(key):
            bad("V1", f"sidecar.{key} missing")
    if not isinstance(sc.get("facts"), list) or not all(
            isinstance(f, dict) and isinstance(f.get("n"), int) and not isinstance(f.get("n"), bool)
            and isinstance(f.get("ledger_ids"), list) and all(isinstance(x, str) for x in f["ledger_ids"]) for f in sc.get("facts", [])):
        bad("V1", "sidecar.facts must be [{n:int, ledger_ids:[str]}]")
    if not isinstance(sc.get("numbers"), list) or not all(
            isinstance(x, dict) and "surface" in x and "kind" in x and "class" in x for x in sc.get("numbers", [])):
        bad("V1", "sidecar.numbers must be [{surface, kind, class, ...}]")
    for key in ("unmapped_claims", "annotation_notes"):
        if not isinstance(sc.get(key), list):
            bad("V1", f"sidecar.{key} must be a list")
    if V:
        _fail(out_dir, V)

    # ---------------- V2 ----------------
    missing = [k for k in MANIFEST_REQUIRED_KEYS if k not in mf]
    if missing:
        bad("V2", f"manifest missing keys: {missing}")
    if mf.get("schema_version") != MANIFEST_SCHEMA_VERSION:
        bad("V2", f"manifest.schema_version != {MANIFEST_SCHEMA_VERSION}: {mf.get('schema_version')!r}")
    if not isinstance(mf.get("checks"), dict) or any(k not in mf["checks"] for k in CHECK_KEYS):
        bad("V2", f"manifest.checks must have keys {list(CHECK_KEYS)}")
    if sc.get("annotator") == DETERMINISTIC and not isinstance(mf.get("writer_constraints_sha256"), str):
        bad("V2", "manifest.writer_constraints_sha256 is required for annotator=DETERMINISTIC")
    if V:
        _fail(out_dir, V)

    # ---------------- V3 ----------------
    for label, rawkey, mkey in (("selected_brief.md", "brief", "source_selected_brief_sha256"), ("ledger", "ledger", "ledger_sha256"),
                                ("annotated md", "annotated", "annotated_md_sha256"), ("sidecar", "sidecar", "sidecar_sha256")):
        got = _sha(raw[rawkey])
        if got != mf.get(mkey):
            bad("V3", f"sha mismatch {label}: file={got[:12]} manifest.{mkey}={str(mf.get(mkey))[:12]}")

    constraints_text = ""
    if "writer_constraints_sha256" in mf:                # C4: 制約ブロック(別欄)。manifestに束縛されている場合のみ存在・sha整合を要求
        cpath = os.path.join(sdir, CONSTRAINTS_NAME)
        if not os.path.isfile(cpath):
            bad("V3", f"missing file: {os.path.relpath(cpath, out_dir)} (manifest.writer_constraints_sha256 is set)")
        else:
            craw = open(cpath, "rb").read()
            if _sha(craw) != mf["writer_constraints_sha256"]:
                bad("V3", f"sha mismatch writer_constraints: file={_sha(craw)[:12]} manifest={str(mf['writer_constraints_sha256'])[:12]}")
            try:
                constraints_text = craw.decode("utf-8")
            except UnicodeDecodeError:
                bad("V3", "writer_constraints.txt is not UTF-8")

    # ---------------- V4 ----------------
    storyline = facts_text = None
    try:
        storyline, facts_text = w1.parse_brief_md(text["annotated"])
    except ValueError as e:
        bad("V4", f"parse_brief_md failed: {e}")

    nums = []
    if facts_text is not None:
        # ---------------- V5 ----------------
        lines = [ln for ln in facts_text.split("\n") if ln.strip()]
        if lines:
            md = _STORY_DUP_RE.match(lines[0])
            if md and w1.strip_tags(md.group(1)).strip() == w1.strip_tags(storyline).strip():
                lines = lines[1:]                     # Storyline重複行(B3既存出力形式)のみ除外
        for ln in lines:
            m = w1.FACT_LINE_RE.match(ln)
            if not m:
                bad("V5", f"Selected Facts line does not match FACT_LINE_RE: {ln[:60]!r}")
            else:
                nums.append(int(m.group(1)))
        K = len(nums)
        if all(v["check"] != "V5" for v in V):
            if K < 1:
                bad("V5", "no fact lines")
            elif nums != list(range(1, K + 1)):
                bad("V5", f"fact numbers not 1..K in order without duplicates: {nums}")
        n_broad = len(w1.BROAD_TAG_RE.findall(facts_text))
        n_strict = len(w1.TAG_RE.findall(facts_text))
        if n_broad != n_strict or n_strict != K:
            bad("V5", f"unexpected tag forms: broad={n_broad} strict={n_strict} lines={K} (tags must be exactly one leading 【事実N】 per line)")
        # ---------------- V6 ----------------
        whole = storyline + "\n" + facts_text
        variants = [x for x in _ANY_NUM_MARK_RE.findall(whole) if not w1.MARK_RE.fullmatch(x)]
        if variants:
            bad("V6", f"non-standard number marks: {variants[:3]}")
        unknown_cls = [n.get("class") for n in sc["numbers"] if n.get("class") not in _CLASS_MARK]
        if unknown_cls:
            bad("V6", f"sidecar.numbers class must be core|peripheral: {unknown_cls[:3]}")
        else:
            for m in w1.MARK_RE.finditer(whole):
                before = whole[:m.start()]
                if not any(before.endswith(str(n["surface"])) and _CLASS_MARK[n["class"]] == m.group(0) for n in sc["numbers"]):
                    bad("V6", f"number mark not attached to a sidecar number surface of the same class: ...{before[-12:]}{m.group(0)}")
                    break
            for n in sc["numbers"]:
                if (str(n["surface"]) + _CLASS_MARK[n["class"]]) not in whole:
                    bad("V6", f"sidecar number {n['surface']!r} ({n['class']}) has no marked occurrence in the annotated text")
                    break
        # ---------------- V7 (番号集合) ----------------
        sc_ns = [f["n"] for f in sc["facts"]]
        if len(set(sc_ns)) != len(sc_ns) or set(sc_ns) != set(nums):
            bad("V7", f"sidecar.facts n set {sorted(set(sc_ns))} != text fact numbers {sorted(set(nums))}")
    # ---------------- V7 (台帳ID) ----------------
    try:
        ids = {f["fact_id"] for f in rfm.parse_ledger_complete(text["ledger"])}
        unknown = sorted({lid for f in sc["facts"] for lid in f["ledger_ids"] if lid not in ids})
        if unknown:
            bad("V7", f"ledger_ids not in ledger: {unknown[:5]}")
    except rfm.LedgerIncomplete as e:
        bad("V7", f"ledger structure incomplete: {e}")

    # ---------------- V8 ----------------
    for k in CHECK_KEYS:
        if mf["checks"].get(k) not in CHECK_OK:
            bad("V8", f"manifest.checks.{k} = {mf['checks'].get(k)!r} (must be PASS or PASS_LAYOUT_NORMALIZED)")

    # ---------------- V9 ----------------
    if sc["spec_sha256"] != mf["spec_sha256"]:
        bad("V9", "sidecar.spec_sha256 != manifest.spec_sha256")
    if sc["brief_sha256"] != mf["source_selected_brief_sha256"]:
        bad("V9", "sidecar.brief_sha256 != manifest.source_selected_brief_sha256")

    # ---------------- V10 ----------------
    if facts_text is not None:
        try:
            o_story, o_facts = w1.parse_brief_md(text["brief"])
            if w1.strip_tags(storyline) != o_story:
                bad("V10", "Storyline differs from original selected_brief.md (after removing number marks)")
            if sc.get("annotator") == DETERMINISTIC:
                # C4: 決定論producerのFact欄はB3 LLM文ではなく「台帳+選択IDからの決定論再導出(D-full)」が原本。
                #     原本をここで再導出し(同じ規則moduleを遅延import)、タグ・印を除いたFact本文と制約ブロックが一致することを要求する。
                from er053_b3_deterministic_producer_01 import assemble_plain
                fs = sorted(sc["facts"], key=lambda f: f["n"])
                if any(len(f["ledger_ids"]) != 1 for f in fs):
                    bad("V10", "DETERMINISTIC sidecar.facts[].ledger_ids must have exactly one id per fact")
                else:
                    try:
                        plain = assemble_plain(text["ledger"], [f["ledger_ids"][0] for f in fs], o_story)
                    except (KeyError, ValueError) as e:
                        bad("V10", f"deterministic re-assembly failed: {type(e).__name__}: {e}")
                    else:
                        a, b = _norm_text(facts_text), _norm_text(plain["facts_text"])
                        if a != b:
                            i = next((i for i in range(min(len(a), len(b))) if a[i] != b[i]), min(len(a), len(b)))
                            bad("V10", f"fact text differs from deterministic re-assembly (first diff at normalized char {i}: "
                                       f"annotated={a[i:i + 15]!r} expected={b[i:i + 15]!r})")
                        if constraints_text != plain["constraints_text"]:
                            bad("V10", "writer_constraints.txt differs from deterministic re-assembly")
            else:
                a, b = _norm_text(facts_text), _norm_text(o_facts)
                if a != b:
                    i = next((i for i in range(min(len(a), len(b))) if a[i] != b[i]), min(len(a), len(b)))
                    bad("V10", f"fact text differs from original after removing tags/marks/whitespace/bullets (first diff at normalized char {i}: "
                               f"annotated={a[i:i + 15]!r} original={b[i:i + 15]!r})")
        except ValueError as e:
            bad("V10", f"original selected_brief.md not parsable: {e}")

    if V:
        _fail(out_dir, V)
    with open(paths["annotated"], encoding="utf-8") as f:       # text mode(Writer/Trialと同じCRLF->LF)
        annotated_text = f.read()
    from er053_b3_deterministic_producer_01 import compose_news_field      # 遅延import(循環回避)。ニュース欄の唯一の連結関数
    return AnnotatedB3(out_dir=out_dir, storyline=storyline, facts_text=facts_text, annotated_md_text=annotated_text,
                       constraints_text=constraints_text, news_field_text=compose_news_field(facts_text, constraints_text),
                       annotated_md_path=paths["annotated"], annotated_md_sha256=_sha(raw["annotated"]), sidecar=sc, manifest=mf,
                       producer=str(mf.get("producer")), fact_numbers=nums)
