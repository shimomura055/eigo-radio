# -*- coding: utf-8 -*-
"""FACTLOCK-WRITER-REDESIGN-TRIAL-01: Trial harness(Production経路ではない、決定Aの例外Trial)。

薄い起動ラッパ。er052_open233_polysemy_nb_dev_01(DEV runner)を同一processで呼び、
  - JA Writer/JA Fact Check/EN phase2 を gpt-6-luna へ(ALL-6-LUNA harnessの apply_all6_patches をそのまま再利用)
  - R0 prompt末尾の AN3 数字抑制ブロックを「Fact Lock R0ブロック」へ差替え(jaw.CONCRETENESS_CONTROL_AN3_BLOCK)
  - R1/R2 指示文に「Fact Lock R1/R2ブロック」を追記(jaw.REVISION_INSTRUCTIONS を in-place 更新)
  - JA Fact Check(vfl01.run_deviation_check)に渡す記事本文からだけ出典タグを除去(両条件で判定入力を同一に保つ)
phase1(Brief->JA R0/R1/R2)後、phase2(EN+Checker)の前に
  - 各段(R0/R1/R2)のタグ照合(測定のみ。STOP・再生成なし)
  - タグ除去(除去前は *_with_tags.md に保存)
を行う。baseline(Production)コードは編集しない。本ファイルは import 時に API を呼ばない。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import unicodedata

TRIAL_ID = "FACTLOCK-WRITER-REDESIGN-TRIAL-01"
BASE_ROOT = "er052_output/factlock_writer_trial_01"
RUNS_ROOT = f"{BASE_ROOT}/runs"
CHECK_PROCESS = "WRITER_FACT_CHECK"
CHECK_MODEL = "gpt-6-luna"
STAGES = ("r0", "r1", "r2")
STAGE_FILES = {"r0": "original.md", "r1": "revision1.md", "r2": "revision2.md"}


def sha256_text(s: str) -> str:
    return hashlib.sha256((s or "").encode("utf-8")).hexdigest()


def sha256_file(path):
    if not path or not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


# ============================================================
# 1. Prompt追記ブロック(Writer側に入る唯一の差分)
# ============================================================
# 出典タグは【事実1】形式(v2でO1採用: 台帳ID F-001/HF-002 等との混同を避ける)。既存の音声化禁止記号Gate
# (丸括弧・角括弧・コロン・スラッシュ等)が角括弧[F-xxx]を検出してしまうため、Gate対象外の【】を使う
# (safety.detect_prohibited_symbolsで確認済み)。内部のID表現は従来どおり "F1"。
MUSTFIX_PRIORITY = "事実確認の修正指示がある場合はそれを最優先し、直すか削る。"

FACTLOCK_R0_BLOCK_HEAD = (
    "\n\n【出典タグの規則(Fact Lock)】\n"
    "この記事は、上のニュース欄に書かれた事実だけを材料にします。ニュース欄の各事実の行頭には"
    "【事実1】【事実2】のような番号が付いています。\n"
    "1. 世界について何かを断定する文(出来事・数値・人物の発言や行動・原因・結果・比較・時期など)は、"
    "文末の句点の直後に、根拠にした事実の番号を【事実1】のように付けてください。複数の事実を使った文は"
    "【事実1,事実2】のようにします。番号はニュース欄にあるものだけを使い、新しい番号を作らないでください。"
    "タイトルには番号を付けないでください。\n"
    "2. 問いかけ・感想・読者への語りかけ・つなぎの文には番号は不要です。ただし、これらの文でも"
    "ニュース欄にない新しい事実を断定しないでください。"
    "暮らしとのつながりは、問いかけや「〜かもしれない」の形で示し、具体的な事実を断定しないでください。\n"
    "3. ニュース欄に書かれていないことは書かないでください。背景知識や常識による補足もしません。"
    "書かれていないことについて「〜かどうかは分かっていない」と述べるのは構いませんが、"
    "分からないことを推測で埋めないでください。\n"
    "4. 事実の範囲(誰が・どこで・いつ・どの集団か)、確かさ(提案か決定か、懸念か事実か)、方向"
    "(増える・減るなど)を、ニュース欄の記述より強くしたり広げたりしないでください。"
    "ニュース欄に「〜ではない」「断定しない」とあることは守ってください。"
    "ニュース欄が触れていない点(誰が・いつ・何人・理由・結果)を、「〜しなかった」「〜はない」「唯一」「初めて」"
    "などと断定して埋めないでください。\n"
    "5. 数字の規則: ニュース欄で【中核数値】と印の付いた数字だけを、記事で使えます。タイトルでも使えますが、"
    "タイトルにはタグを付けません。書き方はニュース欄の表記のままにし"
    "(丸め・単位の換算・「約」「およそ」などの追加や削除・比較値の自分での計算をしない)、本文の文には必ず番号を付けます。"
    "【周辺数値】と印の付いた数字は書かないでください。ただし、【周辺数値】を含む事柄は、数字を省いて述べてよいです"
    "(例: 番号を書かずに「ロシアの衛星」、日付の代わりにニュース欄にある「同日」「翌日」)。"
    "禁じるのは、数字の大きさを「大きく」「急に」「多数」などの言葉で表すことだけです。"
    "ニュース欄に印の無い数字は使いません。"
    "【中核数値】【周辺数値】の印そのものは記事に書かないでください。\n"
)

FACTLOCK_R0_BLOCK_TAIL = "\n7. " + MUSTFIX_PRIORITY

FACTLOCK_REVISION_BLOCK = (
    "\n\n【事実固定の規則(Fact Lock)】\n"
    "この記事の文末には、根拠となる事実の番号タグ(【事実1】など)が付いています。修正でも次を守ってください。\n"
    "1. 番号タグが付いた文の事実の中身(誰が・何を・いつ・どれだけ・なぜ)は変えないでください。"
    "言い回し・順序・比喩・テンポで面白くするのは自由です。\n"
    "2. 新しい事実を述べる文を足さないでください。足してよいのは、問いかけ・感想・読者への語りかけ・"
    "つなぎの文、「もし〜なら」と分かる形のたとえ話・仮定だけです。"
    "これらの文でも、世界について新しい事実を断定しないでください。\n"
    "3. 文を削るのは自由です。\n"
    "4. 「〜かどうかは分かっていない」と書かれていることを、推測で埋めないでください。\n"
    "5. 番号タグは、その文に付けたまま残してください。文を言い換えたり順序を入れ替えたりしても、"
    "タグはその文の事実に対応する文に付けます。新しく足した問いかけ・感想・つなぎの文には付けません。"
    "文をまとめたら両方のタグを付け、分けたらそれぞれに該当するタグを付けます。"
    "記事にすでにある事実の言い直しは、新しい事実に当たりません。\n"
    "6. 数字は、すでに記事に書かれているものだけを、書かれたままの表記で使ってください。"
    "新しい数字を足さない、丸めない、計算し直さない。\n"
    "7. " + MUSTFIX_PRIORITY
)


def build_r0_block(an3_block: str) -> str:
    """AN3(CONCRETENESS_CONTROL_AN3_BLOCK)の第1文(数字・時刻の抑制)を Fact Lock 数字規則(5)で置換し、
    第2文(固有名詞)は逐語で保持する。AN3の2行目が取れなければ ValueError。"""
    lines = (an3_block or "").strip("\n").split("\n")
    proper = [l for l in lines if l.startswith("人名・企業名・地名")]
    if len(proper) != 1:
        raise ValueError("AN3ブロックの固有名詞文が特定できない")
    return FACTLOCK_R0_BLOCK_HEAD + "6. " + proper[0] + FACTLOCK_R0_BLOCK_TAIL


# ============================================================
# 2. タグ・数値の決定論ユーティリティ
# ============================================================
TAG_RE = re.compile(r"【事実\s*\d+(?:\s*[,、，・]\s*(?:事実\s*)?\d+)*】")
# M3: 変形(【Ｆ1】【F2-3】【HF-002】【事実 1-2】等)の消し残しを防ぐ広めの除去(Opus指摘)。strict TAG_REの上位集合。
BROAD_TAG_RE = re.compile(r"【\s*[FＦ事実][^】\n]{0,30}】")
MARK_RE = re.compile(r"【(?:中核数値|周辺数値)】")
ID_RE = re.compile(r"(?<![A-Za-z0-9])[A-Z]{1,8}(?:-[A-Z]{1,4})?-\d{1,4}(?![A-Za-z0-9])")
BULLET_RE = re.compile(r"^\s*(?:-|・)\s*")
FACT_LINE_RE = re.compile(r"^\s*(?:-|・)\s*【事実(\d+)】\s*(.*)$")


def tag_ids(tag: str) -> list:
    return [f"F{n}" for n in re.findall(r"(\d+)", tag)]


def strip_tags(text: str) -> str:
    """出典タグ(と、Writerが誤って書き写した数値印)を除去する。行末空白を整える。"""
    t = TAG_RE.sub("", text or "")
    t = BROAD_TAG_RE.sub("", t)
    t = MARK_RE.sub("", t)
    return "\n".join(l.rstrip() for l in t.split("\n"))


def count_residual_brackets(text: str) -> int:
    """除去後の本文に残った「【」の件数(M3。0であるべき)。"""
    return (text or "").count("【")


def count_broad_only_tags(text: str) -> int:
    """strict形式(【事実N】)ではなく、広め除去だけで消えた変形タグの件数(Writerの書式逸脱の指標)。"""
    return max(0, len(BROAD_TAG_RE.findall(text or "")) - len(TAG_RE.findall(text or "")))


def scan_residual_brackets(run_dir: str) -> dict:
    """M3: run dir全体のうち *_with_tags.md 以外のテキスト系ファイルに「【」が残っていないかを走査する(smoke確認用)。
    hits=「【」を含む全ファイル、unexpected=入力・監査ログ・照合結果として含みうるファイル(許可リスト部分一致)以外。
    smokeでは unexpected が空であること、hits の許可リスト該当分は内容を目視で確認する。"""
    allow = ("_with_tags.md", "selected_brief", "factlock_", "manifest.json", "raw_usage", "prompt", "audit",
             "request", "ledger", "brief", "runtime_evidence", "fact_selection_evidence")   # 02b smoke後に追加: 入力brief由来(fact_selection_evidence)とphase1の生出力監査ログ(runtime_evidence、除去前の生成物・プロンプトを含む。下流の入力には使われない)
    hits, unexpected = [], []
    for root, _, files in os.walk(run_dir):
        for fn in files:
            if not fn.lower().endswith((".md", ".txt", ".json", ".jsonl")):
                continue
            path = os.path.join(root, fn)
            try:
                n = open(path, encoding="utf-8", errors="replace").read().count("【")
            except OSError:
                continue
            if n:
                rel = os.path.relpath(path, run_dir).replace("\\", "/")
                hits.append({"file": rel, "count": n})
                if not any(a in rel for a in allow):
                    unexpected.append({"file": rel, "count": n})
    return {"hits": hits, "unexpected": unexpected, "unexpected_total": sum(u["count"] for u in unexpected)}


_SENT_RE = re.compile(r"[^。！？\n]*[。！？]+[」』）]*(?:\s*【[^】\n]*】)*|[^。！？\n]+")


_QUOTE_RE = re.compile(r"[「『][^」』\n]*[」』]")
_MASK = str.maketrans({"。": "\ue000", "！": "\ue001", "？": "\ue002"})
_UNMASK = str.maketrans({"\ue000": "。", "\ue001": "！", "\ue002": "？"})


def split_sentences(text: str) -> list:
    """本文を文単位に分ける。1行目(非空)はタイトル扱い(is_title=True)。
    戻り値: [{idx, line, text(タグ除去済み), tags[list of F-id], is_title}]"""
    out, idx, first = [], 0, True
    for ln, line in enumerate((text or "").split("\n")):
        if not line.strip():
            continue
        if first:
            first = False
            out.append({"idx": idx, "line": ln, "text": strip_tags(line).strip(),
                        "tags": [], "is_title": True, "raw": line})
            idx += 1
            continue
        masked = _QUOTE_RE.sub(lambda q: q.group(0).translate(_MASK), line)   # 引用符内の句点では切らない
        for m in _SENT_RE.finditer(masked):
            raw = m.group(0).translate(_UNMASK)
            tags = []
            for tm in TAG_RE.finditer(raw):
                for i in tag_ids(tm.group(0)):
                    if i not in tags:
                        tags.append(i)
            plain = strip_tags(raw).strip()
            if not plain:
                continue
            out.append({"idx": idx, "line": ln, "text": plain, "tags": tags, "is_title": False, "raw": raw})
            idx += 1
    return out


# --- 数値抽出 ---
_UNIT_ARABIC = (r"バレル|ドル|ポイント|パーセント|カ国|か国|ヶ国|世紀|番目|時間|%|円|個|件|人|年|月|日|時|分|秒|条|倍|割|社|台|基|隻|本|歳|回|位|度|つ")
_UNIT_KANJI = (r"ドル|パーセント|カ国|か国|世紀|%|円|個|件|人|年|月|日|分|秒|条|倍|割|社|台|基|隻|歳|回|位")
_HEDGE_PRE = r"約|およそ|ほぼ|だいたい|数"
_HEDGE_POST = r"超|以上|以下|近く|ほど|前後|余り"
_ARABIC_RE = re.compile(
    rf"(?P<pre>{_HEDGE_PRE})?(?P<ord>第)?(?P<num>\d+(?:,\d{{3}})*(?:\.\d+)?)"
    rf"(?P<scale>[万億兆千百])?(?P<unit>{_UNIT_ARABIC})?(?P<post>{_HEDGE_POST})?")
_KANJI_RE = re.compile(
    rf"(?P<pre>{_HEDGE_PRE})?(?P<ord>第)?"
    rf"(?:(?P<ks>[一二三四五六七八九十百千万億兆〇零]*[十百千万億兆][一二三四五六七八九十百千万億兆〇零]*)(?!全|能|一|が一|葉|代田|科|貨)"
    rf"|(?P<kp>[一二三四五六七八九〇零十]+)(?=(?:{_UNIT_KANJI})))"
    rf"(?P<unit>{_UNIT_KANJI})?(?P<post>{_HEDGE_POST})?")
_KANJI_DIGIT = {"〇": 0, "零": 0, "一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
_KANJI_SMALL = {"十": 10, "百": 100, "千": 1000}
_KANJI_BIG = {"万": 10 ** 4, "億": 10 ** 8, "兆": 10 ** 12}
_UNIT_NORM = {"パーセント": "%", "か国": "カ国", "ヶ国": "カ国"}
_KANJI_FALSE = {"十分"}   # 副詞の「十分」を10分と誤検出しない
_SCALE_VAL = {"万": 10 ** 4, "億": 10 ** 8, "兆": 10 ** 12, "千": 1000, "百": 100}


def kanji_to_int(s: str) -> int:
    if s and all(c in _KANJI_DIGIT for c in s):   # 二〇二五 のような位取り表記
        return int("".join(str(_KANJI_DIGIT[c]) for c in s))
    total, section, cur = 0, 0, None
    for ch in s:
        if ch in _KANJI_DIGIT:
            cur = _KANJI_DIGIT[ch]
        elif ch in _KANJI_SMALL:
            section += (cur if cur is not None else 1) * _KANJI_SMALL[ch]
            cur = None
        elif ch in _KANJI_BIG:
            section += cur or 0
            total += (section if section else 1) * _KANJI_BIG[ch]
            section, cur = 0, None
    return total + section + (cur or 0)


def _arabic_value(num: str, scale) -> str:
    n = num.replace(",", "")
    if scale:
        v = float(n) * _SCALE_VAL[scale]
        return str(int(v)) if v == int(v) else str(v)
    return n


def extract_numbers(text: str) -> list:
    """本文中の数値トークンを抽出する(全角/半角数字、漢数字、約/およそ+数値、単位付き)。
    台帳ID(F-001, HF-002, MUSE-HC-006)と出典タグ・数値印は事前に除外する。
    戻り値: [{surface, key:(value, unit), hedge:(pre, post)}]"""
    t = unicodedata.normalize("NFKC", text or "")
    t = TAG_RE.sub(" ", unicodedata.normalize("NFKC", t))
    t = BROAD_TAG_RE.sub(" ", t)
    t = MARK_RE.sub(" ", t)
    t = ID_RE.sub(" ", t)
    spans = []
    for m in _ARABIC_RE.finditer(t):
        spans.append((m.start(), m.end(), "a", m))
    for m in _KANJI_RE.finditer(t):
        if (m.group("ks") or m.group("kp")) and m.group(0).lstrip("約およそほぼだいたい数第") not in _KANJI_FALSE:
            spans.append((m.start(), m.end(), "k", m))
    spans.sort(key=lambda s: (s[0], -(s[1] - s[0])))
    out, last_end = [], -1
    for st, en, kind, m in spans:
        if st < last_end:
            continue
        last_end = en
        if kind == "a":
            value = _arabic_value(m.group("num"), m.group("scale"))
        else:
            value = str(kanji_to_int(m.group("ks") or m.group("kp")))
            if value == "0" and (m.group("ks") or m.group("kp")) not in ("〇", "零"):
                continue
        unit = _UNIT_NORM.get(m.group("unit"), m.group("unit"))
        pre, post = m.group("pre"), m.group("post")
        surface = t[st:en].replace(",", "")
        out.append({"surface": surface, "key": (value, unit), "hedge": (pre, post)})
    return out


def load_core_numbers(path: str) -> dict:
    d = json.load(open(path, encoding="utf-8"))
    atoms = {}
    for item in d.get("core", []):
        for lit in item.get("literals", []):
            for tok in extract_numbers(lit):
                atoms.setdefault(tok["key"], set()).add(tok["hedge"])
    surfaces = {}
    for item in d.get("core", []):
        for lit in item.get("literals", []):
            for tok in extract_numbers(lit):
                surfaces.setdefault(tok["key"], set()).add(tok["surface"])
    return {"raw": d, "atoms": atoms, "surfaces": surfaces}


# O2: 数字以外で量を表す語(半分・倍・ひとつ・いくつか等)。決定論の副指標で、判定(mismatch_total)には使わない。
QUANTITY_WORD_RE = re.compile(
    r"半分|半数|過半数|[二三四五六七八九十]倍|倍|ひとつ|ふたつ|みっつ|よっつ|いつつ|いくつか|いくつも|いくつ|"
    r"数人|数件|数社|数カ国|多数|大多数|大半|たくさん")


def count_quantity_words(text: str) -> dict:
    t = strip_tags(text or "")
    items = [m.group(0) for m in QUANTITY_WORD_RE.finditer(t)]
    return {"count": len(items), "items": items}


def check_numbers(text: str, core: dict) -> dict:
    """本文(タグ付きでも可)の数値を中核数値リストと決定論で照合する(測定のみ)。
    status: match(表記一致)/match_surface_diff(値と単位は一致、表記が違う)/hedge_changed(約等の追加・削除)/not_core。
    title(1行目)も対象。core_used_without_tag は本文(タイトル以外)で中核数値が出た文にタグが無いもの。"""
    atoms, surfaces = core["atoms"], core["surfaces"]
    rows, without_tag = [], []
    for s in split_sentences(text):
        for tok in extract_numbers(s["text"]):
            k = tok["key"]
            if k not in atoms:
                st = "not_core"
            elif tok["hedge"] not in atoms[k]:
                st = "hedge_changed"
            elif tok["surface"] in surfaces.get(k, set()):
                st = "match"
            else:
                st = "match_surface_diff"
            rows.append({"sentence_idx": s["idx"], "is_title": s["is_title"], "surface": tok["surface"],
                         "key": list(k), "status": st, "sentence_tagged": bool(s["tags"])})
            if st != "not_core" and not s["is_title"] and not s["tags"]:
                without_tag.append({"sentence_idx": s["idx"], "surface": tok["surface"]})
    cnt = {k: sum(1 for r in rows if r["status"] == k)
           for k in ("match", "match_surface_diff", "hedge_changed", "not_core")}
    return {"tokens": rows, "counts": cnt, "mismatch_total": cnt["hedge_changed"] + cnt["not_core"],
            "core_used_without_tag": without_tag, "total": len(rows),
            "quantity_words": count_quantity_words(text)}


# --- R0->R1->R2 タグ付き文の差分(決定論) ---
def _bigrams(s: str) -> set:
    s = re.sub(r"\s+", "", s)
    return {s[i:i + 2] for i in range(len(s) - 1)} or {s}


def sentence_sim(a: str, b: str) -> float:
    A, B = _bigrams(a), _bigrams(b)
    return len(A & B) / len(A | B) if (A | B) else 0.0


def diff_tagged(prev_text: str, next_text: str, keep_thr: float = 0.9, mod_thr: float = 0.3) -> dict:
    """前段のタグ付き文が次段でどうなったか。同じタグを共有する文のうち最も類似度の高いもので判定:
    sim>=keep_thr 維持 / mod_thr<=sim<keep_thr 改変(言い換え。事実が変わったかは別途のタグ照合で測る) / それ以外 削除。
    次段で前段のどの文にも対応しないタグ付き文は added。数字トークン集合が変わった組は number_changed。"""
    prev = [s for s in split_sentences(prev_text) if s["tags"] and not s["is_title"]]
    nxt = [s for s in split_sentences(next_text) if s["tags"] and not s["is_title"]]
    used, rows = set(), []
    for p in prev:
        best, best_sim = None, 0.0
        for n in nxt:
            if n["idx"] in used or not (set(p["tags"]) & set(n["tags"])):
                continue
            sim = sentence_sim(p["text"], n["text"])
            if sim > best_sim:
                best, best_sim = n, sim
        if best is not None and best_sim >= mod_thr:
            used.add(best["idx"])
            kind = "kept" if best_sim >= keep_thr else "modified"
            nc = {t["key"][0] + (t["key"][1] or "") for t in extract_numbers(p["text"])} != \
                 {t["key"][0] + (t["key"][1] or "") for t in extract_numbers(best["text"])}
            rows.append({"prev_idx": p["idx"], "next_idx": best["idx"], "kind": kind, "sim": round(best_sim, 3),
                         "tags_prev": p["tags"], "tags_next": best["tags"], "number_changed": nc})
        else:
            rows.append({"prev_idx": p["idx"], "next_idx": None, "kind": "deleted", "sim": round(best_sim, 3),
                         "tags_prev": p["tags"], "tags_next": [], "number_changed": False})
    added = [n["idx"] for n in nxt if n["idx"] not in used]
    c = {k: sum(1 for r in rows if r["kind"] == k) for k in ("kept", "modified", "deleted")}
    c["added"] = len(added)
    c["number_changed"] = sum(1 for r in rows if r["number_changed"])
    return {"pairs": rows, "added_next_idx": added, "counts": c}


# ============================================================
# 3. brief(注記版)の事実パース
# ============================================================
def parse_annotated_facts(brief_text: str) -> dict:
    """注記版brief(## Selected Facts 配下の『- 【F1】本文』行)から {F1: 本文} を返す。数値印は除去。"""
    facts, in_facts = {}, False
    for line in brief_text.split("\n"):
        if line.strip().startswith("## Selected Facts"):
            in_facts = True
            continue
        if not in_facts:
            continue
        m = FACT_LINE_RE.match(line)
        if m:
            facts[f"F{m.group(1)}"] = MARK_RE.sub("", m.group(2)).strip()
    return facts


# ============================================================
# 4. LLMによるタグ照合 (i)(ii) (測定のみ)
# ============================================================
CHECK_DEVELOPER = (
    "あなたはFact Lock照合の担当です。文章の面白さ・文体は評価しません。"
    "言い換え・語順・比喩・つなぎは、事実の意味が変わらない限り問題としません。")

# (i) v2(M1): 判定単位は「文 × その文に付いたタグの事実の和集合」。文の主張を分解し、主張ごとに支える事実IDを出させる。
PAIR_PROMPT = """次の「タグ付き文」それぞれについて、文の主張を分解し、主張ごとに、その文に付いたタグの事実(和集合)のどれが支えているかを判定してください。

各文には「直前の文」(代名詞などの参照先を知るための文脈。判定の対象ではない)と「付いたタグの事実」(その文のタグの事実だけ)が付いています。

{blocks}

手順:
1. 文が世界について述べる主張(出来事・数値・主体・範囲・確かさ・方向・原因・結果・時期)を、1文につき1つ以上に分ける。問いかけや感想の部分は主張に数えない。
2. 主張ごとに、「付いたタグの事実」の和集合だけを根拠に、支えている事実のIDを supporting_ids に入れる(複数可)。複数の事実を組み合わせて初めて言える主張は、その複数のIDを入れてよい。
3. status:
- supported: 付いたタグの事実の和集合で、意味(主体・対象・範囲・確かさ・方向・数値)を変えずに支えられている。
- unsupported: どの事実にも根拠がない、事実と矛盾する、または範囲・確かさ・方向・主体・数値を変えている(supporting_ids は空にする)。
- undecidable: 付いたタグの事実だけでは判定できない。
言い換え・語順・比喩・つなぎは、事実の意味が変わらない限り問題としません。claimは30字以内で書いてください。"""

PAIR_SCHEMA = {"name": "factlock_pair_check", "strict": True, "schema": {
    "type": "object", "additionalProperties": False, "required": ["items"],
    "properties": {"items": {"type": "array", "items": {
        "type": "object", "additionalProperties": False,
        "required": ["sentence_index", "claims"],
        "properties": {"sentence_index": {"type": "integer"},
                       "claims": {"type": "array", "items": {
                           "type": "object", "additionalProperties": False,
                           "required": ["claim", "supporting_ids", "status"],
                           "properties": {"claim": {"type": "string"},
                                          "supporting_ids": {"type": "array", "items": {"type": "string"}},
                                          "status": {"type": "string",
                                                     "enum": ["supported", "unsupported", "undecidable"]}}}}}}}}}}

# (ii) v2(M7): 5分類。タイトルもタグなし文として対象に含める。
UNTAGGED_LABELS = ("neutral", "untagged_brief_fact", "hedged_speculation", "background_general", "new_specific_claim")

UNTAGGED_PROMPT = """次の「事実一覧」と「タグなし文」(タイトルを含む)を照合し、各文を分類してください。

【事実一覧】
{facts}

【タグなし文】
{sentences}

分類(labelは次のいずれか):
- neutral: 問いかけ・感想・読者への語りかけ・つなぎ・比喩的な導入などで、世界について新しい事実を断定していない。
- untagged_brief_fact: 事実一覧にある内容を述べている(タグが付いていないだけ)。
- hedged_speculation: 推量・可能性の形で示された、暮らしとのつながりや予測(「〜かもしれない」「〜だろうか」など)。断定していない。
- background_general: 用語の説明・一般常識で、事実一覧にはないが特定の出来事や数値を断定していない。
- new_specific_claim: 事実一覧にない出来事・因果・数値・主体・不在(「〜しなかった」「〜はない」「唯一」「初めて」)などを、世界について断定している(「〜と言われる」等の伝聞形も含む)。
判断に迷う場合は、事実一覧だけを根拠に読者が新しい具体的な事実を得るかどうかで決めてください。reasonは30字以内。"""

UNTAGGED_SCHEMA = {"name": "factlock_untagged_check", "strict": True, "schema": {
    "type": "object", "additionalProperties": False, "required": ["items"],
    "properties": {"items": {"type": "array", "items": {
        "type": "object", "additionalProperties": False,
        "required": ["sentence_index", "label", "reason"],
        "properties": {"sentence_index": {"type": "integer"},
                       "label": {"type": "string", "enum": list(UNTAGGED_LABELS)},
                       "reason": {"type": "string"}}}}}}}


def _facts_block(facts: dict) -> str:
    return "\n".join(f"{k}: {v}" for k, v in facts.items())


def _call_json(client, model: str, prompt: str, schema: dict, stage: str):
    import er005_cost_logger as cl
    import er003_v1_en_direct_vfl_01_generate as vfl01
    with cl.logging_context(TRIAL_ID, stage):
        resp = client.responses.create(
            model=model, reasoning={"effort": vfl01.REASONING_EFFORT},
            text={"format": {"type": "json_schema", **schema}},
            input=[{"role": "developer", "content": CHECK_DEVELOPER}, {"role": "user", "content": prompt}])
    return json.loads(resp.output_text), resp


def aggregate_claims(claims: list) -> str:
    """M1: 文単位の集計。全主張supported=整合 / 1つでもunsupported=不整合 / それ以外(主張なし含む)=判定不能。"""
    if not claims:
        return "判定不能"
    if any(c.get("status") == "unsupported" for c in claims):
        return "不整合"
    if all(c.get("status") == "supported" for c in claims):
        return "整合"
    return "判定不能"


def build_pair_blocks(sentences: list, facts: dict) -> tuple:
    """タグ付き文ごとに『直前の文(文脈)』と『付いたタグの事実だけ』のブロックを作る。
    戻り値: (blocks_text, tagged_sentences, unknown_tags)。facts外のタグは unknown_tag として決定論で数え、LLMには出さない。"""
    tagged = [s for s in sentences if s["tags"] and not s["is_title"]]
    unknown = [{"sentence_idx": s["idx"], "tag": t} for s in tagged for t in s["tags"] if t not in facts]
    blocks = []
    for s in tagged:
        prev = sentences[s["idx"] - 1]["text"] if s["idx"] > 0 else "(なし)"
        fl = "\n".join(f"{t}: {facts[t]}" for t in s["tags"] if t in facts) or "(該当する事実なし)"
        blocks.append(f"[{s['idx']}] タグ: {','.join(s['tags'])}\n直前の文: {prev}\n文: {s['text']}\n付いたタグの事実:\n{fl}")
    return "\n\n".join(blocks), tagged, unknown


def pair_check(client, model, stage, sentences, facts):
    """(i) 文 × その文に付いたタグの事実の和集合 の主張分解判定。"""
    blocks, tagged, unknown = build_pair_blocks(sentences, facts)
    if not tagged:
        return {"items": [], "unknown_tags": unknown, "counts": {}, "claim_counts": {}, "response_id": None,
                "model": None, "tagged_sentences": 0}
    data, resp = _call_json(client, model, PAIR_PROMPT.format(blocks=blocks), PAIR_SCHEMA, f"factlock_pair_{stage}")
    by_idx = {i["sentence_index"]: i for i in data["items"]}
    items = []
    for s in tagged:
        claims = by_idx.get(s["idx"], {}).get("claims", [])
        outside = sorted({x for c in claims for x in c.get("supporting_ids", []) if x not in s["tags"]})
        items.append({"sentence_index": s["idx"], "tags": s["tags"], "claims": claims,
                      "verdict": aggregate_claims(claims), "supporting_outside_tags": outside})
    counts = {v: sum(1 for i in items if i["verdict"] == v) for v in ("整合", "不整合", "判定不能")}
    claim_counts = {v: sum(1 for i in items for c in i["claims"] if c.get("status") == v)
                    for v in ("supported", "unsupported", "undecidable")}
    return {"items": items, "unknown_tags": unknown, "counts": counts, "claim_counts": claim_counts,
            "inconsistent_sentences": [i["sentence_index"] for i in items if i["verdict"] == "不整合"],
            "tagged_sentences": len(tagged),
            "response_id": getattr(resp, "id", None), "model": getattr(resp, "model", None)}


def untagged_check(client, model, stage, sentences, facts):
    """(ii) タグなし文(タイトルを含む)の5分類。"""
    untagged = [s for s in sentences if not s["tags"]]
    if not untagged:
        return {"items": [], "counts": {}, "response_id": None, "model": None, "untagged_sentences": 0}
    lines = [f"[{s['idx']}]{'(タイトル)' if s['is_title'] else ''} {s['text']}" for s in untagged]
    data, resp = _call_json(client, model, UNTAGGED_PROMPT.format(facts=_facts_block(facts), sentences="\n".join(lines)),
                            UNTAGGED_SCHEMA, f"factlock_untagged_{stage}")
    items = data["items"]
    title_idx = {s["idx"] for s in untagged if s["is_title"]}
    for i in items:
        i["is_title"] = i["sentence_index"] in title_idx
    counts = {v: sum(1 for i in items if i["label"] == v) for v in UNTAGGED_LABELS}
    return {"items": items, "counts": counts, "untagged_sentences": len(untagged),
            "title_label": next((i["label"] for i in items if i["is_title"]), None),
            "response_id": getattr(resp, "id", None), "model": getattr(resp, "model", None)}


def check_stage(client, model, stage, text, facts, core, use_llm=True) -> dict:
    sents = split_sentences(text)
    rec = {"stage": stage, "sentences_total": len([s for s in sents if not s["is_title"]]),
           "tagged_sentences": len([s for s in sents if s["tags"] and not s["is_title"]]),
           "tags_used": sorted({t for s in sents for t in s["tags"]}),
           "marks_echoed": len(MARK_RE.findall(text or "")),
           "broad_only_tags": count_broad_only_tags(text),
           "iii_numbers": check_numbers(text, core)}
    if use_llm:
        rec["i_pairs"] = pair_check(client, model, stage, sents, facts)
        rec["ii_untagged"] = untagged_check(client, model, stage, sents, facts)
    return rec


# ============================================================
# 5. patch(Production無編集のmonkeypatch)
# ============================================================
def apply_factlock_patches(mods: dict | None = None) -> dict:
    """Fact Lock の prompt差替え + Fact Check入力のタグ除去。modsはtest用に差替え可能
    (jaw, vfl01 を持つdict)。戻り値は restore_factlock_patches に渡す。"""
    if mods is None:
        import er003_v1_en_direct_vfl_01_generate as vfl01
        import er019_family_x_ja_writer_o_r1_r2_01 as jaw
        mods = {"vfl01": vfl01, "jaw": jaw}
    jaw, vfl01 = mods["jaw"], mods["vfl01"]
    saved = {"_mods": mods, "an3": jaw.CONCRETENESS_CONTROL_AN3_BLOCK,
             "rev": dict(jaw.REVISION_INSTRUCTIONS), "dev": vfl01.run_deviation_check}
    jaw.CONCRETENESS_CONTROL_AN3_BLOCK = build_r0_block(saved["an3"])
    for k in ("r1", "r2"):
        jaw.REVISION_INSTRUCTIONS[k] = saved["rev"][k] + FACTLOCK_REVISION_BLOCK
    orig = saved["dev"]

    def dev_strip(client, verified_ledger_text, article_text, *a, **k):
        if k.get("source_article_text") is not None:
            k["source_article_text"] = strip_tags(k["source_article_text"])
        return orig(client, verified_ledger_text, strip_tags(article_text), *a, **k)

    vfl01.run_deviation_check = dev_strip
    return saved


def restore_factlock_patches(saved: dict) -> None:
    jaw, vfl01 = saved["_mods"]["jaw"], saved["_mods"]["vfl01"]
    jaw.CONCRETENESS_CONTROL_AN3_BLOCK = saved["an3"]
    for k, v in saved["rev"].items():
        jaw.REVISION_INSTRUCTIONS[k] = v
    vfl01.run_deviation_check = saved["dev"]


# ============================================================
# 6. phase1後処理(タグ照合→タグ除去)
# ============================================================
def postprocess_phase1(out_dir: str, brief_md: str, core_json: str, client=None, model: str = CHECK_MODEL,
                       use_llm: bool = True) -> dict:
    """R0/R1/R2の各段をタグ照合(測定のみ)し、除去前を *_with_tags.md に退避してから各 .md を除去版で上書きする。
    EN phase2・Checkerは除去版 revision2.md を入力に使う。"""
    d = f"{out_dir}/ja_writer"
    facts = parse_annotated_facts(open(brief_md, encoding="utf-8").read())
    core = load_core_numbers(core_json)
    texts = {s: open(f"{d}/{STAGE_FILES[s]}", encoding="utf-8").read() for s in STAGES}
    summary = {"facts": list(facts), "stages": {}, "shas": {}, "strip": {}}
    for s in STAGES:
        rec = check_stage(client, model, s, texts[s], facts, core, use_llm=use_llm)
        summary["stages"][s] = rec
        with open(f"{out_dir}/factlock_check_{s}.json", "w", encoding="utf-8") as f:
            json.dump(rec, f, ensure_ascii=False, indent=2)
    summary["diff"] = {"r0_to_r1": diff_tagged(texts["r0"], texts["r1"]), "r1_to_r2": diff_tagged(texts["r1"], texts["r2"]),
                       "r0_to_r2": diff_tagged(texts["r0"], texts["r2"])}
    with open(f"{out_dir}/factlock_diff.json", "w", encoding="utf-8") as f:
        json.dump(summary["diff"], f, ensure_ascii=False, indent=2)
    for s in STAGES:
        p = f"{d}/{STAGE_FILES[s]}"
        wt = p[:-3] + "_with_tags.md"
        with open(wt, "w", encoding="utf-8", newline="") as f:
            f.write(texts[s])
        stripped = strip_tags(texts[s])
        with open(p, "w", encoding="utf-8", newline="") as f:
            f.write(stripped)
        summary["shas"][s] = {"with_tags": sha256_text(texts[s]), "stripped": sha256_text(stripped)}
        # M3: 除去後に残った「【」の件数と、広め除去だけで消えた変形タグ件数を記録(測定のみ)
        summary["strip"][s] = {"residual_brackets_after_strip": count_residual_brackets(stripped),
                               "broad_only_tags_removed": count_broad_only_tags(texts[s])}
    summary["residual_brackets_total"] = sum(v["residual_brackets_after_strip"] for v in summary["strip"].values())
    with open(f"{out_dir}/factlock_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    return summary


# ============================================================
# 7. main
# ============================================================
def build_parser():
    p = argparse.ArgumentParser()
    p.add_argument("--slug", required=True)
    p.add_argument("--brief-md", required=True, help="注記版 selected_brief_factlock.md")
    p.add_argument("--core-numbers-json", required=True)
    p.add_argument("--ledger-txt", required=True)
    p.add_argument("--out-dir", required=True)
    p.add_argument("--budget-jpy", type=float, default=12.0)
    p.add_argument("--theme-file", default=None)
    p.add_argument("--checker-budget-jpy", type=float, default=10.0)
    p.add_argument("--yes-run-paid", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    return p


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = build_parser().parse_args(argv)
    theme_file = args.theme_file or os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(args.ledger_txt))), "topic.txt")
    theme = open(theme_file, encoding="utf-8").read().strip()
    os.environ["OPEN233_RUNS_ROOT"] = RUNS_ROOT
    os.environ.pop("OPEN233_B3_VARIANT", None)
    import er052_open233_polysemy_nb_dev_01 as dev
    import er052_all6_writer_trial_01_run as all6
    import er019_family_x_ja_writer_o_r1_r2_01 as jaw
    import er003_v1_en_direct_vfl_01_generate as vfl01

    manifest = {
        "trial_id": TRIAL_ID, "arm": "factlock_6luna", "slug": args.slug, "out_dir": args.out_dir,
        "brief_md": args.brief_md, "brief_sha256": sha256_file(args.brief_md),
        "core_numbers_sha256": sha256_file(args.core_numbers_json), "ledger_sha256": sha256_file(args.ledger_txt),
        "prompt_sha256": {
            "R0_PROMPT": sha256_text(jaw.R0_PROMPT), "DEVELOPER_MESSAGE": sha256_text(jaw.DEVELOPER_MESSAGE),
            "AN3_original": sha256_text(jaw.CONCRETENESS_CONTROL_AN3_BLOCK),
            "FACTLOCK_R0_BLOCK": sha256_text(build_r0_block(jaw.CONCRETENESS_CONTROL_AN3_BLOCK)),
            "FACTLOCK_REVISION_BLOCK": sha256_text(FACTLOCK_REVISION_BLOCK),
            "R1_instruction_original": sha256_text(jaw.REVISION_INSTRUCTIONS["r1"]),
            "R2_instruction_original": sha256_text(jaw.REVISION_INSTRUCTIONS["r2"]),
            "PAIR_PROMPT": sha256_text(PAIR_PROMPT), "UNTAGGED_PROMPT": sha256_text(UNTAGGED_PROMPT),
            "DEVIATION_DEVELOPER_MESSAGE": sha256_text(vfl01.DEVIATION_DEVELOPER_MESSAGE)},
        "harness_sha256": {"factlock_run": sha256_file(__file__), "all6_run": sha256_file(all6.__file__)},
        "reasoning_effort": vfl01.REASONING_EFFORT, "all6_model": all6.ALL6_MODEL,
        "checker_enabled": True, "budget_jpy": args.budget_jpy, "started_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "phases": [],
    }
    if args.dry_run or not args.yes_run_paid:
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        return 0 if args.dry_run else 2

    saved_all6 = all6.apply_all6_patches()
    saved_fl = apply_factlock_patches()
    t0, rc, exit_reason = time.time(), 0, "completed"
    try:
        check_model = all6.resolve_all6_model(CHECK_PROCESS)
        common = ["--theme", theme, "--slug", args.slug, "--ledger-txt", args.ledger_txt, "--out-dir", args.out_dir,
                  "--yes-run-paid"]
        for phase in ("phase1", "phase2"):
            argv2 = common + ["--phase", phase, "--budget-jpy", str(args.budget_jpy)]
            argv2 += ["--brief-md", args.brief_md] if phase == "phase1" else ["--checker-budget-jpy", str(args.checker_budget_jpy)]
            ts = time.time()
            try:
                prc = dev.main(argv2)
                manifest["phases"].append({"phase": phase, "rc": prc, "sec": round(time.time() - ts, 1)})
                if prc not in (0, None):
                    rc, exit_reason = (prc if isinstance(prc, int) else 1), f"{phase}_rc={prc}"
                    break
                if phase == "phase1":
                    ts2 = time.time()
                    summ = postprocess_phase1(args.out_dir, args.brief_md, args.core_numbers_json,
                                              client=vfl01.get_client(), model=check_model)
                    manifest["postprocess_sec"] = round(time.time() - ts2, 1)
                    manifest["factlock_shas"] = summ["shas"]
            except SystemExit as e:
                manifest["phases"].append({"phase": phase, "rc": f"SystemExit:{e}", "sec": round(time.time() - ts, 1)})
                rc, exit_reason = 1, f"{phase}_SystemExit: {e}"
                break
            except Exception as e:  # noqa: BLE001
                manifest["phases"].append({"phase": phase, "rc": f"error:{e!r}", "sec": round(time.time() - ts, 1)})
                rc, exit_reason = 1, f"{phase}_error: {e!r}"
                break
    finally:
        restore_factlock_patches(saved_fl)
        all6.restore_patches(saved_all6)
        manifest["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        manifest["wall_sec"] = round(time.time() - t0, 1)
        manifest["exit_reason"] = exit_reason
        manifest["model_ids_actual"] = all6.collect_models(args.out_dir)
        manifest["checker"] = all6.checker_summary(args.out_dir)
        cj = f"{args.out_dir}/cost.json"
        manifest["cost"] = json.load(open(cj, encoding="utf-8")) if os.path.exists(cj) else None
        os.makedirs(args.out_dir, exist_ok=True)
        manifest["residual_bracket_scan"] = scan_residual_brackets(args.out_dir)   # M3: smoke/本番とも記録(測定のみ)
        with open(f"{args.out_dir}/manifest.json", "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
    return rc


if __name__ == "__main__":
    sys.exit(main())
