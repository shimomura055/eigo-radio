# -*- coding: utf-8 -*-
"""ENDUSER-EN-JA-LINKED-HIGHLIGHT-01 委任_02: End Userページの『英語文 -> 対応する日本語訳』連動ハイライト用の文対応づけ(`ja_align`)。

方針(DESIGN_01 + Opus条件Aレビュー M1/M2/M4/M5/M10):
 - 入力 = 最終 article.json の story part(`paragraphs`=EN文、`ja`=日本語段落)。出力 = `ja_align`(オフセット方式。訳本文・英語本文は書き換えない)。
 - 対応づけは『段落内の単調DP(文数1:1/1:2/2:1/2:2/1:3/3:1。EN/JA片側のみの欠落moveも可)』+ 埋め込み類似度(OpenAI text-embedding-3-large)。
   新規LLM生成呼出なし(埋め込みAPIのみ)。埋め込みは `<cache_dir>/ja_align_embed_v1.jsonl` にテキストsha256キーで保存し、再実行・page_verifyはAPI 0。
 - 採否は安全側(誤ハイライトより非ハイライト): 群ごとに (a)cos>=TAU (b)DP経路の余裕(その群を禁止した最良経路とのコスト差>=DELTA_PATH)
   (c)境界1文ずらし案(JA範囲の+-1文 shift/伸縮)に対する群・EN各文のcos余裕 (d)数字一致(EN数字はJA数字に含まれる。M10) (e)段落全体の整合
   (段落平均cos>=TAU_PARA かつ 群cos最小>=TAU_FLOOR)。不成立の群は `ja:null`、段落全体が不成立なら全群null。
 - オフセットは JavaScript の String と同じ UTF-16 code unit 単位(M4)。正規化・trimは行わない。Pythonでは slice_u16() で切り出す。
 - 埋め込み失敗は全null + degraded記録(M5)。ON/OFFのflagは設けない。
閾値(PARAMS)はゴールド(docs/research/ENDUSER-EN-JA-LINKED-HIGHLIGHT-01/gold/)で決め、固定(testで固定値を検査)。
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import time
import unicodedata
from pathlib import Path

import numpy as np

ALIGN_METHOD = "mono_dp_embed_v1"
EMBED_MODEL = "text-embedding-3-large"
EMBED_DIMS = 1024
EMBED_CACHE_NAME = "ja_align_embed_v1.jsonl"
EMBED_USD_PER_MTOK = 0.13

# 固定パラメータ(ゴールドで決定。変更はゴールド再評価が要る)
PARAMS = {
    "lam": 2.0,            # DP: (1-cos)の重み
    "len_w": 1.0,          # DP: 文字数比log差の重み
    "pen_12": 0.9,         # DP: 1:2 / 2:1 move の事前ペナルティ(1:1は0)
    "pen_22": 4.0,        # DP: 2:2 move
    "pen_13": 1.5,        # DP: 1:3 / 3:1 move
    "skip": 3.0,           # DP: EN/JA片側のみのmove
    "tau": 0.50,           # 群cos下限
    "delta_path": 0.10,    # 群を禁止した最良経路とのコスト差の下限
    "delta_group": 0.0,    # JA境界を1文ずらした案(shift/伸縮6種)に対する群cos余裕
    "delta_sent": 0.0,     # 同: EN各文のcos余裕(own - max alt)。ゴールドの合成ずらし336件を全棄却する主条件
    "delta_group_en": -0.10,  # EN範囲を1文ずらした案(shift/伸縮)の方が群cosで0.10以上上回るなら棄却(緩い拒否。ホールドアウトig合成ずらし1/94の取りこぼしを受けて追加)
    "delta_sent_en": -0.10,   # 同: JA各文について
    "eq_delta_ja": 0.0,    # 文数一致の段落(1:1経路)のJA側: 隣のJA文より自分の対応文がcosで上回る余裕
    "eq_delta_en": 0.0,    # 同: EN側(JA文から見て隣のEN文より自分の対応文が上回る余裕)
    "tau_para": 0.55,      # 段落平均cos下限
    "tau_floor": 0.40,     # 段落内の群cos最小値の下限(下回ると段落全体null)
}
MOVES = ((1, 1), (1, 2), (2, 1), (2, 2), (1, 3), (3, 1))


class AlignEmbedError(Exception):
    pass


# ------------------------------------------------------------
# UTF-16 code unit offsets (M4)
# ------------------------------------------------------------
def u16_len(s: str) -> int:
    return len(s.encode("utf-16-le")) // 2


def cp_to_u16(s: str) -> list:
    """code point index -> UTF-16 offset の表(長さ len(s)+1)。"""
    out, k = [0], 0
    for ch in s:
        k += 2 if ord(ch) > 0xFFFF else 1
        out.append(k)
    return out


def slice_u16(s: str, a: int, b: int) -> str:
    """JavaScript の s.substring(a,b)(UTF-16 code unit)と同じ切り出し。サロゲートペアを割る位置はValueError。"""
    raw = s.encode("utf-16-le")[2 * a:2 * b]
    return raw.decode("utf-16-le")        # 孤立サロゲートはUnicodeDecodeError(=ValueError)


# ------------------------------------------------------------
# 日本語文分割(連結==元段落。『』「」（）内の句点では切らない)
# ------------------------------------------------------------
_OPEN = "「『（(【〈《"
_CLOSE = "」』）)】〉》"
_END = "。！？!?"


def split_ja(text: str) -> list:
    """[(start,end)] code point offsets。隙間なく連結==text。末尾空白は直前の文に含める。"""
    n, i, depth, start, out = len(text), 0, 0, 0, []
    while i < n:
        ch = text[i]
        if ch in _OPEN:
            depth += 1
        elif ch in _CLOSE:
            depth = max(0, depth - 1)
        if ch in _END and depth == 0:
            j = i + 1
            while j < n and (text[j] in _END or text[j] in _CLOSE):
                if text[j] in _CLOSE:
                    depth = max(0, depth - 1)
                j += 1
            while j < n and text[j] in " \t\r\n　":
                j += 1
            out.append((start, j))
            start, i = j, j
            continue
        i += 1
    if start < n:
        out.append((start, n))
    return out


# ------------------------------------------------------------
# 数字(M10)
# ------------------------------------------------------------
_EN_NUMW = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
            "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90,
            "hundred": 100, "thousand": 1000}
_KD = {"〇": 0, "一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
_KU = {"十": 10, "百": 100, "千": 1000}


def _kanji_value(s: str):
    total, cur, digits = 0, 0, ""
    for ch in s:
        if ch in _KD:
            digits += str(_KD[ch])
            cur = int(digits)
        elif ch in _KU:
            total += (cur or 1) * _KU[ch]
            cur, digits = 0, ""
        elif ch == "万":
            total = (total + cur) * 10000
            cur, digits = 0, ""
        else:
            return None
    return total + cur


def _digit_values(t: str) -> set:
    out = set()
    for m in re.finditer(r"\d[\d,]*(?:\.\d+)?", t):
        v = m.group(0).replace(",", "")
        try:
            f = float(v)
            out.add(int(f) if f == int(f) else f)
        except ValueError:
            pass
    return out


def en_numbers(text: str) -> set:
    """EN側の数値集合(算用数字と two..twelve/twenty..hundred/thousand。'one'は代名詞と区別できないため対象外)。"""
    t = unicodedata.normalize("NFKC", text)
    out = _digit_values(t)
    for w in re.findall(r"[A-Za-z]+", t.lower()):
        if w in _EN_NUMW:
            out.add(_EN_NUMW[w])
    return out


def ja_numbers(text: str) -> set:
    """JA側の数値集合(算用数字[全角含む]・漢数字)。『一緒』等の1文字漢数字は余分な値になるだけ(EN<=JAの判定なので害なし)。"""
    t = unicodedata.normalize("NFKC", text)
    out = _digit_values(t)
    for m in re.finditer(r"[〇一二三四五六七八九十百千万]+", t):
        v = _kanji_value(m.group(0))
        if v is not None:
            out.add(v)
    return out


def numbers_ok(en_text: str, ja_text: str) -> bool:
    return en_numbers(en_text) <= ja_numbers(ja_text)


def names_ok(en_text: str, ja_text: str, name_map: dict | None) -> bool:
    """固有名(M10): name_map={EN表記:[許容するJA表記...]}に登録された名前がENにあれば、JAにいずれかの表記があること。辞書に無い名前は判定に使わない。"""
    if not name_map:
        return True
    for en, jas in name_map.items():
        if re.search(r"(?<![A-Za-z])" + re.escape(en) + r"(?![A-Za-z])", en_text) and not any(j in ja_text for j in jas):
            return False
    return True


# ------------------------------------------------------------
# 埋め込み(sha256キャッシュ)
# ------------------------------------------------------------
def _key(text: str) -> str:
    return hashlib.sha256(f"{EMBED_MODEL}|{EMBED_DIMS}|{text}".encode("utf-8")).hexdigest()


def openai_embedder(texts: list) -> tuple:
    """(vectors, total_tokens)。最大2回再試行(計3回)。失敗はAlignEmbedError。"""
    last = None
    for attempt in range(3):
        try:
            from dotenv import load_dotenv
            load_dotenv()
            from openai import OpenAI
            r = OpenAI().embeddings.create(model=EMBED_MODEL, input=texts, dimensions=EMBED_DIMS)
            return [d.embedding for d in sorted(r.data, key=lambda d: d.index)], int(getattr(r.usage, "total_tokens", 0) or 0)
        except Exception as e:                          # noqa: BLE001
            last = e
            time.sleep(1.0 + attempt)
    # build_infoに残る文言なので、URL・pathを含みうる例外本文は載せない(例外クラス名と状態コードのみ)
    raise AlignEmbedError(f"{type(last).__name__} status={getattr(last, 'status_code', None)}")


class EmbedStore:
    """テキスト->単位ベクトル。cache_dir=None はメモリのみ。allow_api=False(verify)はキャッシュに無ければAlignEmbedError。"""

    def __init__(self, cache_dir=None, embedder=None, allow_api: bool = True):
        self.dir = Path(cache_dir) if cache_dir else None
        self.embedder = embedder or openai_embedder
        self.allow_api = allow_api
        self.mem: dict = {}
        self.stats = {"api_calls": 0, "tokens": 0, "texts_embedded": 0, "cache_hits": 0}
        if self.dir:
            p = self.dir / EMBED_CACHE_NAME
            if p.is_file():
                for line in p.read_text(encoding="utf-8").splitlines():
                    if line.strip():
                        try:
                            o = json.loads(line)
                            self.mem[o["k"]] = np.asarray(o["v"], dtype=np.float32)
                        except Exception:               # noqa: BLE001  (半端な最終行は無視=再計算)
                            continue

    def missing(self, texts: list) -> list:
        return sorted({t for t in texts if _key(t) not in self.mem})

    def ensure(self, texts: list) -> None:
        miss = self.missing(texts)
        self.stats["cache_hits"] += len(set(texts)) - len(miss)
        if not miss:
            return
        if not self.allow_api:
            raise AlignEmbedError(f"埋め込みキャッシュに無い文が{len(miss)}件(verifyはAPIを呼ばない)")
        for i in range(0, len(miss), 200):
            batch = miss[i:i + 200]
            vecs, tok = self.embedder(batch)
            self.stats["api_calls"] += 1
            self.stats["tokens"] += tok
            self.stats["texts_embedded"] += len(batch)
            lines = []
            for t, v in zip(batch, vecs):
                a = np.asarray(v, dtype=np.float64)
                a = (a / (np.linalg.norm(a) or 1.0)).astype(np.float32)
                self.mem[_key(t)] = a
                lines.append(json.dumps({"k": _key(t), "v": [round(float(x), 6) for x in a]}))
            if self.dir:
                self.dir.mkdir(parents=True, exist_ok=True)
                with open(self.dir / EMBED_CACHE_NAME, "a", encoding="utf-8", newline="\n") as f:
                    f.write("\n".join(lines) + "\n")

    def vec(self, text: str):
        k = _key(text)
        if k not in self.mem:
            raise AlignEmbedError("埋め込みキャッシュに無い文")
        return self.mem[k]

    def cost_jpy(self, usd_jpy: float = 155.0) -> float:
        return round(self.stats["tokens"] * EMBED_USD_PER_MTOK / 1e6 * usd_jpy, 4)


# ------------------------------------------------------------
# 単調DP
# ------------------------------------------------------------
def _norm(v):
    n = float(np.linalg.norm(v))
    return v / n if n else v


def _mean(vs):
    return _norm(np.mean(np.stack(vs), axis=0))


def _dp(n: int, m: int, cost_fn, skip: float, excl=None):
    """(total, edges) 最良経路。edges=[(i0,i1,j0,j1)]。excl=禁止するedge集合。到達不能は(inf,None)。"""
    best = {(0, 0): (0.0, None, None)}
    for i in range(n + 1):
        for j in range(m + 1):
            if (i, j) not in best:
                continue
            c0 = best[(i, j)][0]
            for di, dj in MOVES + ((1, 0), (0, 1)):
                ni, nj = i + di, j + dj
                if ni > n or nj > m:
                    continue
                e = (i, ni, j, nj)
                if excl and e in excl:
                    continue
                c = c0 + (cost_fn(i, ni, j, nj) if di and dj else skip)
                if (ni, nj) not in best or c < best[(ni, nj)][0] - 1e-12:
                    best[(ni, nj)] = (c, (i, j), e)
    if (n, m) not in best:
        return float("inf"), None
    edges, k = [], (n, m)
    while k != (0, 0):
        _, p, e = best[k]
        edges.append(e)
        k = p
    return best[(n, m)][0], edges[::-1]


def _move_pen(P: dict, a: int, b: int) -> float:
    if a == 1 and b == 1:
        return 0.0
    if a == 2 and b == 2:
        return P["pen_22"]
    if a + b == 3:
        return P["pen_12"]
    return P["pen_13"]


def _alt_ranges(j0: int, j1: int, m: int) -> list:
    """境界を1文ずらした代替範囲(同サイズshift / 片端の伸縮)。"""
    out = []
    for a, b in ((j0 - 1, j1 - 1), (j0 + 1, j1 + 1), (j0 - 1, j1), (j0 + 1, j1), (j0, j1 - 1), (j0, j1 + 1)):
        if 0 <= a < b <= m and (a, b) != (j0, j1):
            out.append((a, b))
    return out


class _Para:
    """1段落の埋め込み・DPコスト・群の採否特徴量。"""

    def __init__(self, en_texts, ja_texts, store, P):
        self.P, self.en, self.ja = P, en_texts, ja_texts
        self.n, self.m = len(en_texts), len(ja_texts)
        self.ev = [store.vec(t) for t in en_texts]
        self.jv = [store.vec(t) for t in ja_texts]
        self.le = [len(t) for t in en_texts]
        self.lj = [len(t) for t in ja_texts]
        self.r = sum(self.le) / max(1, sum(self.lj))
        self._g: dict = {}

    def gv(self, kind, a, b):
        k = (kind, a, b)
        if k not in self._g:
            self._g[k] = _mean((self.ev if kind == "e" else self.jv)[a:b])
        return self._g[k]

    def cos(self, i0, i1, j0, j1):
        return float(np.dot(self.gv("e", i0, i1), self.gv("j", j0, j1)))

    def cost(self, i0, i1, j0, j1):
        P = self.P
        e, j = sum(self.le[i0:i1]), sum(self.lj[j0:j1]) * self.r
        return (P["len_w"] * abs(math.log((e + 8) / (j + 8))) + _move_pen(P, i1 - i0, j1 - j0)
                + P["lam"] * (1.0 - self.cos(i0, i1, j0, j1)))

    def feats(self, i0, i1, j0, j1) -> dict:
        """own=群cos / gm_ja,sm_ja=JA範囲を1文ずらした案に対する余裕(群・EN各文) / gm_en,sm_en=EN範囲を1文ずらした案に対する余裕(群・JA各文)"""
        own = self.cos(i0, i1, j0, j1)
        aj = _alt_ranges(j0, j1, self.m)
        ae = _alt_ranges(i0, i1, self.n)
        f = {"own": own, "gm_ja": 9.0, "sm_ja": 9.0, "gm_en": 9.0, "sm_en": 9.0}
        if aj:
            f["gm_ja"] = own - max(self.cos(i0, i1, a, b) for a, b in aj)
            f["sm_ja"] = min(float(np.dot(self.ev[i], self.gv("j", j0, j1))) - max(float(np.dot(self.ev[i], self.gv("j", a, b))) for a, b in aj) for i in range(i0, i1))
        if ae:
            f["gm_en"] = own - max(self.cos(a, b, j0, j1) for a, b in ae)
            f["sm_en"] = min(float(np.dot(self.jv[j], self.gv("e", i0, i1))) - max(float(np.dot(self.jv[j], self.gv("e", a, b))) for a, b in ae) for j in range(j0, j1))
        return f

    def screen_equal(self, i, name_map=None, j=None) -> tuple:
        """文数一致の段落(EN n文==JA n文)でDP経路が全て1:1のとき、i番目のペアの採否。
        1:1が事前に強い(ゴールド41段落・154ペアで全て恒等)ため、境界ずらし案は同サイズの隣接ずらし(JA側 j+-1 / EN側 i+-1)に限る。
        JA側: E_iはJ_iを隣のJ_(i+-1)より上回る / EN側: J_iはE_iを隣のE_(i+-1)より上回る(相互最良)。"""
        P = self.P
        j = i if j is None else j                      # j!=iは検証用(誤った隣接ペアの棄却確認)
        own = self.cos(i, i + 1, j, j + 1)
        aj = [self.cos(i, i + 1, x, x + 1) for x in (j - 1, j + 1) if 0 <= x < self.m]
        ae = [self.cos(k, k + 1, j, j + 1) for k in (i - 1, i + 1) if 0 <= k < self.n]
        f = {"own": own, "gm_ja": own - max(aj) if aj else 9.0, "sm_ja": own - max(aj) if aj else 9.0,
             "gm_en": own - max(ae) if ae else 9.0, "sm_en": own - max(ae) if ae else 9.0}
        if own < P["tau"]:
            return "cos_low", f
        if not numbers_ok(self.en[i], self.ja[j]):
            return "number_mismatch", f
        if not names_ok(self.en[i], self.ja[j], name_map):
            return "name_mismatch", f
        if f["gm_ja"] < P["eq_delta_ja"]:
            return "equal_shift_margin_ja", f
        if f["gm_en"] < P["eq_delta_en"]:
            return "equal_shift_margin_en", f
        return None, f

    def screen(self, i0, i1, j0, j1, name_map=None) -> tuple:
        """(why|None, feats)。None=採用可。DP経路の余裕(path_margin)と段落全体の整合は呼出側(align_paragraph)。"""
        P = self.P
        f = self.feats(i0, i1, j0, j1)
        t_ja = "".join(self.ja[j0:j1])
        t_en = " ".join(self.en[i0:i1])
        if f["own"] < P["tau"]:
            return "cos_low", f
        if not numbers_ok(t_en, t_ja):
            return "number_mismatch", f
        if not names_ok(t_en, t_ja, name_map):
            return "name_mismatch", f
        if f["gm_ja"] < P["delta_group"]:
            return "group_shift_margin", f
        if f["sm_ja"] < P["delta_sent"]:
            return "sent_shift_margin", f
        if f["gm_en"] < P["delta_group_en"]:
            return "group_shift_margin_en", f
        if f["sm_en"] < P["delta_sent_en"]:
            return "sent_shift_margin_en", f
        return None, f


def align_paragraph(en_texts: list, ja_texts: list, store: EmbedStore, params: dict = PARAMS, name_map=None, with_diag: bool = False):
    """1段落(EN文list, JA文list)を対応づける。返り値=groups=[{'en':[i..],'ja':(j0,j1)|None,'conf':float,'why':str}] (ENの全文を順に含む)。
    JA文は[j0,j1)の連続区間。ja=Noneは非ハイライト。with_diag=Trueは(groups, diag)。"""
    P = params
    n, m = len(en_texts), len(ja_texts)
    if n == 0:
        return ([], {}) if with_diag else []
    if m == 0:
        g = [{"en": [i], "ja": None, "conf": 0.0, "why": "no_ja"} for i in range(n)]
        return (g, {}) if with_diag else g
    px = _Para(en_texts, ja_texts, store, P)
    total, edges = _dp(n, m, px.cost, P["skip"])
    if edges is None:
        g = [{"en": [i], "ja": None, "conf": 0.0, "why": "no_path"} for i in range(n)]
        return (g, {}) if with_diag else g
    groups = []
    equal_mode = n == m and edges == [(i, i + 1, i, i + 1) for i in range(n)]
    for (i0, i1, j0, j1) in edges:
        if i1 == i0:
            continue                                    # JAのみ未対応
        if j1 == j0:
            groups.append({"en": list(range(i0, i1)), "ja": None, "conf": 0.0, "why": "unpaired_en"})
            continue
        why, f = px.screen_equal(i0, name_map) if equal_mode else px.screen(i0, i1, j0, j1, name_map)
        pm = None
        if why is None:
            alt_total, _ = _dp(n, m, px.cost, P["skip"], excl={(i0, i1, j0, j1)})
            pm = alt_total - total
            if pm < P["delta_path"]:
                why = "path_margin"
        groups.append({"en": list(range(i0, i1)), "ja": (j0, j1) if why is None else None, "conf": round(f["own"], 4), "why": why or "ok",
                       "_cand": (j0, j1), "_pm": pm, "_f": f})
    # 段落全体の整合: 候補群の平均cosと最小cos。不成立なら全群null
    cands = [g for g in groups if g.get("_cand")]
    para_fail = None
    if cands:
        cs = [g["conf"] for g in cands]
        if sum(cs) / len(cs) < P["tau_para"]:
            para_fail = "paragraph_mean_cos"
        elif min(cs) < P["tau_floor"]:
            para_fail = "paragraph_floor_cos"
    else:
        para_fail = "no_candidate"
    if para_fail:
        for g in groups:
            if g["ja"] is not None:
                g["ja"], g["why"] = None, para_fail
    out = groups if with_diag else [{k: v for k, v in g.items() if not k.startswith("_")} for g in groups]
    return (out, {"total": total, "para_fail": para_fail}) if with_diag else out


# ------------------------------------------------------------
# part / article
# ------------------------------------------------------------
def part_input_sha(part: dict) -> str:
    """alignの入力(EN文列[sid,text] + JA段落 + 方式)のsha。ENまたはJAが変わればこのshaが変わる(陳腐化検出)。"""
    obj = {"en": [[[s["sid"], s["text"]] for s in pa] for pa in part.get("paragraphs", [])], "ja": list(part.get("ja") or []),
           "method": ALIGN_METHOD, "model": EMBED_MODEL, "dims": EMBED_DIMS, "params": PARAMS}
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def part_texts(part: dict) -> list:
    """このpartの埋め込み対象テキスト(EN文+JA文)。"""
    out = []
    for pa in part.get("paragraphs", []):
        out += [s["text"] for s in pa]
    for t in part.get("ja") or []:
        out += [t[a:b].strip() for a, b in split_ja(t)]
    return out


def align_part(part: dict, store: EmbedStore, params: dict = PARAMS, name_map=None) -> tuple:
    """(ja_align list, stats)。part['ja']とparagraphs必須。段落数不一致は全null(stats.para_mismatch)。"""
    paras, jas = part["paragraphs"], part["ja"]
    try:
        store.ensure(part_texts(part))                  # 未キャッシュ分だけ埋め込み。失敗した段落は下で個別にdegraded(全null)
    except AlignEmbedError:
        pass
    groups_out, g = [], 0
    stats = {"sentences": 0, "linked": 0, "groups": 0, "groups_null": 0, "reasons": {}, "para_mismatch": len(paras) != len(jas), "degraded": []}
    for pi, pa in enumerate(paras):
        en_texts = [s["text"] for s in pa]
        stats["sentences"] += len(pa)
        segs, map_u16 = [], [0]
        if pi < len(jas) and not stats["para_mismatch"]:
            segs = split_ja(jas[pi])
            ja_texts = [jas[pi][a:b].strip() for a, b in segs]
            map_u16 = cp_to_u16(jas[pi])
            try:
                res = align_paragraph(en_texts, ja_texts, store, params, name_map)
            except AlignEmbedError as e:
                res = [{"en": [i], "ja": None, "conf": 0.0, "why": "degraded_embed"} for i in range(len(pa))]
                stats["degraded"].append(f"{part['key']}#p{pi}: {e}")
        else:
            res = [{"en": [i], "ja": None, "conf": 0.0, "why": "para_mismatch"} for i in range(len(pa))]
        for grp in res:
            sids = [pa[i]["sid"] for i in grp["en"]]
            ja = None
            if grp["ja"] is not None:
                a_cp, b_cp = segs[grp["ja"][0]][0], segs[grp["ja"][1] - 1][1]
                txt = jas[pi]
                while a_cp < b_cp and txt[a_cp].isspace():
                    a_cp += 1
                while b_cp > a_cp and txt[b_cp - 1].isspace():
                    b_cp -= 1
                ja = [pi, map_u16[a_cp], map_u16[b_cp]]
            groups_out.append({"g": g, "sids": sids, "ja": ja, "conf": float(grp["conf"])})
            g += 1
            stats["groups"] += 1
            if ja is None:
                stats["groups_null"] += 1
                stats["reasons"][grp["why"]] = stats["reasons"].get(grp["why"], 0) + 1
            else:
                stats["linked"] += len(sids)
    return groups_out, stats


def build_article_align(article: dict, store: EmbedStore, name_map=None) -> dict:
    """article['levels'][lv]['parts'][*]['ja_align'] を付与する(in place)。
    返り値=build_info.ja_align: {method,model,dims,params,applicable,coverage{lv:{...}},input_sha256{lv:{key:sha}},degraded[],embedding{...}}"""
    cov, shas, degraded = {}, {}, []
    texts = []
    for L in article["levels"].values():
        for p in L["parts"]:
            if p.get("ja") and p.get("paragraphs"):
                texts += part_texts(p)
    emb_err = None
    if texts:
        try:
            store.ensure(texts)
        except AlignEmbedError as e:
            emb_err = str(e)
    for lv, L in article["levels"].items():
        c = {"story_parts": 0, "sentences_total": 0, "sentences_linked": 0, "groups_total": 0, "groups_null": 0, "reasons": {}}
        shas[lv] = {}
        for p in L["parts"]:
            if not (p.get("ja") and p.get("paragraphs")):
                continue
            al, st = align_part(p, store, PARAMS, name_map)       # 欠けた埋め込みの段落は個別にdegraded(全null)
            p["ja_align"] = al
            shas[lv][p["key"]] = part_input_sha(p)
            c["story_parts"] += 1
            c["sentences_total"] += st["sentences"]
            c["sentences_linked"] += st["linked"]
            c["groups_total"] += st["groups"]
            c["groups_null"] += st["groups_null"]
            for k, v in st["reasons"].items():
                c["reasons"][k] = c["reasons"].get(k, 0) + v
            degraded += st["degraded"]
            if st["para_mismatch"]:
                degraded.append(f"{lv} {p['key']}: EN段落数とJA段落数が不一致(全null)")
        c["coverage"] = round(c["sentences_linked"] / c["sentences_total"], 4) if c["sentences_total"] else None
        cov[lv] = c
    if emb_err:
        degraded.insert(0, f"embedding_unavailable: {emb_err}")
    applicable = any(c["story_parts"] for c in cov.values())
    return {"method": ALIGN_METHOD, "model": EMBED_MODEL, "dims": EMBED_DIMS, "params": dict(PARAMS), "applicable": applicable,
            "coverage": cov, "input_sha256": shas, "degraded": degraded,
            "embedding": {"api_calls": store.stats["api_calls"], "tokens": store.stats["tokens"], "cached_hits": store.stats["cache_hits"],
                          "cost_jpy": store.cost_jpy()}}


# ------------------------------------------------------------
# 検証(構造・陳腐化・再計算)
# ------------------------------------------------------------
def check_part_align(part: dict, label: str) -> list:
    """ja_alignの構造不変条件。違反メッセージlistを返す。"""
    V = []
    al = part.get("ja_align")
    if al is None:
        return V
    if not part.get("ja"):
        return [f"{label}: ja_alignがあるのにjaが無い"]
    sid_pos = {}
    for pi, pa in enumerate(part["paragraphs"]):
        for si, s in enumerate(pa):
            sid_pos[s["sid"]] = (pi, si)
    seen, last_en, last_ja = set(), (-1, -1), (-1, -1)
    for k, g in enumerate(al):
        if g.get("g") != k:
            V.append(f"{label}: g={g.get('g')} が連番でない({k}期待)")
        sids = g.get("sids") or []
        if not sids:
            V.append(f"{label} g{k}: sidsが空")
            continue
        pos = []
        for s in sids:
            if s not in sid_pos:
                V.append(f"{label} g{k}: sid {s} が段落に無い")
            elif s in seen:
                V.append(f"{label} g{k}: sid {s} が複数の群にある")
            else:
                seen.add(s)
                pos.append(sid_pos[s])
        if len(pos) == len(sids):
            if len({p[0] for p in pos}) != 1 or [p[1] for p in pos] != list(range(pos[0][1], pos[0][1] + len(pos))):
                V.append(f"{label} g{k}: sidsが同一段落の連続する文でない")
            if pos[0] <= last_en:
                V.append(f"{label} g{k}: ENの順序が逆行")
            last_en = pos[-1]
        ja = g.get("ja")
        conf = g.get("conf")
        if ja is None:
            continue
        if not (isinstance(ja, list) and len(ja) == 3 and all(isinstance(x, int) and not isinstance(x, bool) for x in ja)):
            V.append(f"{label} g{k}: jaが[paraIdx,start,end]でない")
            continue
        pi, a, b = ja
        if not (0 <= pi < len(part["ja"])):
            V.append(f"{label} g{k}: paraIdx範囲外")
            continue
        if len(pos) == len(sids) and pos and pos[0][0] != pi:
            V.append(f"{label} g{k}: ENの段落とJAの段落が異なる")
        if not (0 <= a < b <= u16_len(part["ja"][pi])):
            V.append(f"{label} g{k}: オフセットが範囲外")
            continue
        try:
            sl = slice_u16(part["ja"][pi], a, b)
        except ValueError:
            V.append(f"{label} g{k}: オフセットがサロゲートペアを割る")
            continue
        if not sl.strip():
            V.append(f"{label} g{k}: スライスが空")
        if (pi, a) < last_ja:
            V.append(f"{label} g{k}: JA範囲が単調でない/重なる")
        last_ja = (pi, b)
        if not isinstance(conf, (int, float)) or conf < PARAMS["tau"]:
            V.append(f"{label} g{k}: confが閾値({PARAMS['tau']})未満なのにjaあり")
    return V


def verify_article_align(article: dict, ja_info: dict | None, store: EmbedStore | None) -> tuple:
    """(violations[str], checked{})。storeがあれば保存ベクトルからDPを再実行して一致を確認(API 0)。無ければ構造+入力shaのみ。"""
    V, checked = [], {"parts": 0, "recompute": "skipped_no_cache"}
    if ja_info is None:
        for lv, L in article["levels"].items():
            for p in L["parts"]:
                if p.get("ja_align") is not None:
                    V.append(f"{lv} {p['key']}: ja_alignがあるのにbuild_info.ja_alignが無い")
        return V, checked
    for lv, L in article["levels"].items():
        for p in L["parts"]:
            if p.get("ja") and p.get("paragraphs") and ja_info.get("applicable"):
                if p.get("ja_align") is None:
                    V.append(f"{lv} {p['key']}: 訳があるのにja_alignが無い")
                    continue
                checked["parts"] += 1
                V += check_part_align(p, f"{lv} {p['key']}")
                want = (ja_info.get("input_sha256") or {}).get(lv, {}).get(p["key"])
                if want != part_input_sha(p):
                    V.append(f"{lv} {p['key']}: ja_alignの入力sha不一致(EN文またはJAが変わったのに対応が古い=陳腐化)")
            elif p.get("ja_align") is not None and not p.get("ja"):
                V.append(f"{lv} {p['key']}: jaが無いpartにja_align")
    if store is not None and not V and not ja_info.get("degraded"):
        checked["recompute"] = "done"
        try:
            for lv, L in article["levels"].items():
                for p in L["parts"]:
                    if p.get("ja_align") is not None:
                        store.ensure(part_texts(p))
                        al, _ = align_part(p, store, PARAMS)
                        if al != p["ja_align"]:
                            V.append(f"{lv} {p['key']}: 保存ベクトルからの再計算がja_alignと一致しない")
        except AlignEmbedError as e:
            V.append(f"ja_align再計算不能(埋め込みキャッシュ欠落。verifyはAPIを呼ばない): {e}")
    return V, checked
