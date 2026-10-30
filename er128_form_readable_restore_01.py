# -*- coding: utf-8 -*-
"""学習項目選定フォームV3: 人間可読の選定結果(+照合コード)からの復元・照合tool
(LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01 委任_07R、ユーザー正式決定USER_03 §B)。

ユーザーがChatGPT経由で貼り付けた人間可読テキスト(`COPY_FORMAT_01.md`)から、公開データJSON(`user_test/selection_form_v3/data/<stem>.json`)
を参照して candidate_id・候補集合sha・本文sha・文法解説全文を**欠落・改変なく**復元し、payload v2(`schema_version:2, schema_minor:1`)を作る。
確定は既存 `er128_kp_confirmed_content_01.cmd_from_form` へ委譲する(検証は緩めない)。照合できなければfail-closed(何も確定・保存しない)。

使い方:
  py er128_form_readable_restore_01.py restore --text <貼付テキスト> [--data-dir <dir>] [--out <payload.json>]      # 復元payloadのみ出力(確定しない)
  py er128_form_readable_restore_01.py confirm --from-readable <貼付テキスト> --run <run> --level a2|b1b --by <名> --user-ref <path> [--dry-run] [--grammar-pending] [--actor user|evidence]
  (同じ引数で `py er119_kp_human_review_cli_01.py confirm --from-readable ...` も使える)

性質: 承認済み改善のClaude側実装。明示実行時のみ動作し、Production既定動作は変えない。API 0。外部HTTP 0。
不一致時の自動補正はしない(訳・解説・区分を黙って置換しない)。照合コードなし/破損時の推測復元はしない。
"""
import argparse
import copy
import hashlib
import itertools
import json
import os
import re
import subprocess
import sys
import tempfile
import unicodedata
import unicodedata

ROOT = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DATA_DIR = os.path.join(ROOT, "user_test", "selection_form_v3", "data")
TOOL_ID = "er128_form_readable_restore_01"
CODE_VERSION = "AIF1"

CAT_HEAD = {1: "① Key Phrase", 2: "② 追加解説", 3: "③ 本文意味表示"}
CAT_LABEL = {1: "①Key Phrase", 2: "②追加解説", 3: "③本文意味表示"}
GLOSS_MARK = {"provisional": "（仮訳・未確定）", "missing": "（日本語訳未生成）"}
MARK_BEGIN, MARK_END = "【解説全文】", "【解説ここまで】"
BODY_TERM = "\n====="
GRAMMAR_TOP_N = 2
GRAMMAR_MAX = 1
MAX_COMBOS = 64
PREFACE_NEW = ("以下はeigo-radioの学習項目選定結果です。内容(英語・日本語訳・区分・文法解説・自由コメント・照合コード)を一切変更・要約・翻訳せず、"
               "下の「選定結果」をそのままコードブロックで返してください。修正してほしい点があればコードブロックの外に書いてください。\n\n")
RECHECK_HINT = "フォームの『選定結果をコピー』をもう一度押し、全文をそのまま貼り付けてください"
KP_CONFIRMED_NOTE = "Key Phrase／Key Word 10件はユーザー確定済み。この送信で再選定していない(selectionは確定内容の逐語)。"

CODE_RE = re.compile(r"AIF1-([A-Za-z0-9_]+)-([0-9a-f]{6})-([0-9a-f]{8})-([0-9a-f]{8})-([0-9a-f]{10})-([0-9a-f]{10}|0)-([0-9a-f]{8}|0)-([0-9a-f]{4})")
# 旧AIF2(ニュアンス解説欄つきフォームの照合コード)は廃止(NUANCE-CORNER-ABOLITION-01、2026-10-30ユーザー決定)。検出して明示拒否するためだけに残す(黙って無視しない)。
CODE2_RE = re.compile(r"AIF2-")
# 移行受理(NUANCE-CORNER-ABOLITION-01 委任_03): 撤去前に発行・送信済みのAIF2回答だけを、撤去前の旧フォームdata(--legacy-form-data)で照合できる場合に限り受理する。
# 新規発行フォームはAIF1のみ(AIF2の発行経路は存在しない)。ニュアンス節は読み捨て(採否は記録しない)。
CODE2_FULL_RE = re.compile(r"AIF2-([A-Za-z0-9_]+)-([0-9a-f]{6})-([0-9a-f]{8})-([0-9a-f]{8})-([0-9a-f]{10})-([0-9a-f]{10}|0)-([0-9a-f]{8}|0)-([0-9a-f]{8}|0)-([0-9a-f]{4})")
MARK_N_BEGIN, MARK_N_END = "【ニュアンス全文】", "【ニュアンスここまで】"
LEGACY_DROP_KEYS = ("nuance", "nuance_spec")   # 旧dataと現行dataの差は、この2キーだけであること(それ以外の差異は別データとして拒否)
NUANCE_ABOLISHED_MSG = ("NUANCE_CORNER_ABOLISHED: ニュアンス解説コーナーは廃止されました(2026-10-30)。旧フォーム(ニュアンス欄つき・照合コードAIF2)の回答は受け付けません。"
                        "フォームを再取得(再出力)して選び直してください")
FENCE_RE = re.compile(r"^\s*```[A-Za-z0-9_-]*\s*$")
BULLET_RE = re.compile(r"^\s*(?:[-－‐–—・•*]|\d+[.)])\s*(.+)$")


class RestoreError(Exception):
    """復元・照合の失敗(fail-closed。何も確定・保存しない)。"""


# ---------------------------------------------------------------- 共通関数
def sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def d6_of_bytes(raw: bytes) -> str:
    """データJSON版の識別子d6。公開Pages=リポジトリのblob(LF)と同一になるよう、Windows作業ツリーのCRLFはLFへ正規化してから計算する。"""
    return hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:6]


def nfkc(s: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", s)).strip()


def items_of(d: dict) -> list:
    return (d.get("phrases") or []) + (d.get("words") or [])


def cid_of(it: dict):
    return it.get("candidate_id") or it.get("id")


def gloss_text(it: dict) -> str:
    return (it.get("ja_gloss") if it.get("ja_gloss") is not None else it.get("meaning_ja")) or ""


def gloss_status(it: dict) -> str:
    t = gloss_text(it)
    if not t:
        return "missing"
    return it.get("ja_gloss_status") or "provisional"


BODY_TERM_RE = re.compile(r"\s*=+\s*\Z")   # 委任_08: 直前に改行が無い「。=====」も除去。本文中の=====は触らない(COPY_FORMAT_01 §6)
COMMENT_NONE_WORDS = ["なし", "特になし", "無し", "特に無し", "ありません", "特にありません", "-", "ー", "―", "—", "n/a", "none"]   # form_logic.js と同一定数


def normalize_comment(c) -> str:
    """委任_08: trim後が空、または既定語(NFKC+小文字で比較)のみなら「コメントなし」=''。form_logic.js normalizeComment と同一。"""
    t = ("" if c is None else str(c)).strip()
    return "" if (t == "" or unicodedata.normalize("NFKC", t).lower() in COMMENT_NONE_WORDS) else t


def body_view(body: str) -> str:
    """表示用: 末尾の内部終端記号(=====)だけ外す(内容は一字も変えない)。"""
    b = body.replace("\r\n", "\n")
    return BODY_TERM_RE.sub("", b) if BODY_TERM_RE.search(b) else b.rstrip("\n")


def norm_body(s: str) -> str:
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    s = BODY_TERM_RE.sub("", s)
    return "\n".join(x.rstrip() for x in s.split("\n")).strip("\n")


def grammar_presented(d: dict) -> list:
    """フォーム(form_logic.js grammarPresented)と同じ: rank順に並べ、上位GRAMMAR_TOP_N件へdisplay_rankを付ける。"""
    gs = list(enumerate(d.get("grammar") or []))
    gs.sort(key=lambda x: (float(x[1]["rank"]) if x[1].get("rank") is not None else 1e9, x[0]))
    out = []
    for k, (_, g) in enumerate(gs[:GRAMMAR_TOP_N]):
        g2 = dict(g)
        g2["display_rank"] = k + 1
        out.append(g2)
    return out


def has_grammar_spec(d: dict) -> bool:
    return bool(d.get("grammar_spec"))


def choices_of(d: dict, st: dict) -> dict:
    if d.get("kp_confirmed"):   # ユーザー確定済みKP/KWは確定内容を常に採用(form_logic.js choicesOf)
        return {r["term"]: r["category"] for r in (d["kp_confirmed"].get("selection") or [])}
    return (st or {}).get("choices") or {}


# ---------------------------------------------------------------- 照合コード / 人間可読コピー(契約の参照実装。フォームJSはこれとバイト一致する)
def make_code(stem: str, d: dict, d6: str, sel_ids: list, gram: list, comment: str) -> str:
    """sel_ids=[(cat, candidate_id)](フォーム表示順=区分①②③の順、各区分内はデータ順) / gram=[(candidate_id, explanation_sha256)]"""
    c8 = (d.get("candidates_sha256") or "0" * 8)[:8]
    t8 = ((d.get("source") or {}).get("text_sha256") or "0" * 8)[:8]
    s10 = sha("v1\n" + "\n".join(f"{c}:{i}" for c, i in sel_ids))[:10]
    g10 = sha("v1\n" + "\n".join(f"{i}:{h}" for i, h in gram))[:10] if gram else "0"
    com = normalize_comment(comment)
    m8 = sha(com)[:8] if com else "0"
    body = f"{CODE_VERSION}-{stem}-{d6}-{c8}-{t8}-{s10}-{g10}-{m8}"
    return body + "-" + sha(body)[:4]


def _gram_pair(g: dict) -> tuple:
    return (g.get("candidate_id") or g["id"], g.get("explanation_sha256") or "")


def build_readable(stem: str, d: dict, st: dict, d6: str, with_preface: bool = False) -> str:
    """st={'choices':{term:cat},'grammar':{id:bool},'grammar_zero':bool,'comment':str}(form_logic.jsの状態と同形)"""
    its = items_of(d)
    ch = choices_of(d, st)
    lines = [f"記事：{d['name']}｜{d.get('level_label') or d.get('level')}", ""]
    sel_ids = []
    for cat in (1, 2, 3):
        lines.append(CAT_HEAD[cat])
        got = [it for it in its if ch.get(it["term"]) == cat]
        for it in got:
            mark = GLOSS_MARK.get(gloss_status(it), "")
            lines.append(f"- {it['term']}：{gloss_text(it) or '(未生成)'}{mark}")
            sel_ids.append((cat, cid_of(it)))
        if not got:
            lines.append("（選択なし）")
        lines.append("")
    gs = [g for g in grammar_presented(d) if (st.get("grammar") or {}).get(g["id"])]
    if has_grammar_spec(d) and grammar_presented(d) and not gs and st.get("grammar_zero") is not True:
        raise ValueError("文法が未決定です(新仕様は『適切な候補なし』の明示選択が必要)")
    if not gs:
        lines.append("文法：選定なし")
    for g in gs:
        lines += [f"文法：{g['title']}", MARK_BEGIN, body_view(g.get("body") or ""), MARK_END]
    lines.append("")
    com = normalize_comment(st.get("comment"))
    lines.append("自由コメント：" + (com if com else "なし"))
    lines += ["", "照合コード(変更しないでください)：" + make_code(stem, d, d6, sel_ids, [_gram_pair(g) for g in gs], com)]
    text = "\n".join(lines)
    return (PREFACE_NEW + text) if with_preface else text


# ---------------------------------------------------------------- データ版の特定
def git_history_lookup(stem: str, d6: str, data_dir: str = DEFAULT_DATA_DIR, max_commits: int = 400):
    """選定時のデータ版をgit履歴から取得する(read-only)。無ければNone。"""
    path = os.path.abspath(os.path.join(data_dir, stem + ".json"))
    cwd = os.path.dirname(path)
    try:
        top = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=cwd, capture_output=True, check=True).stdout.decode("utf-8").strip()
        rel = os.path.relpath(path, top).replace("\\", "/")
        hs = subprocess.run(["git", "log", f"--max-count={max_commits}", "--format=%H", "--", rel], cwd=top, capture_output=True, check=True).stdout.decode().split()
        for h in hs:
            r = subprocess.run(["git", "show", f"{h}:{rel}"], cwd=top, capture_output=True)
            if r.returncode == 0 and d6_of_bytes(r.stdout) == d6:
                return r.stdout
    except (OSError, subprocess.CalledProcessError):
        return None
    return None


# ---------------------------------------------------------------- 復元
def _split_pair(s: str):
    m = re.search(r"[：:]", s)
    return (s[:m.start()], s[m.end():]) if m else (s, None)


def _parse_text(t: str, m: re.Match, legacy: bool = False) -> dict:
    """照合コード行より前の本文を節に分解する。"""
    lines = t[:m.start()].split("\n")
    start = None
    for i, ln in enumerate(lines):
        if re.match(r"^\s*記事\s*[：:]", ln):
            start = i
            break
    if start is None:
        raise RestoreError("『記事：…』の行が見つかりません。" + RECHECK_HINT)
    lines = lines[start:]
    hdr = lines[0].strip()
    got = {1: [], 2: [], 3: []}
    grams = []
    comment_lines = None
    nuance_in = None
    sec = None
    i = 1
    while i < len(lines):
        ln = lines[i]
        s = ln.strip()
        if s.startswith("照合コード"):
            break
        if comment_lines is not None:
            comment_lines.append(ln)
            i += 1
            continue
        mm = re.match(r"^([①②③])", s)
        if mm:
            sec = "①②③".index(mm.group(1)) + 1
            i += 1
            continue
        if s.startswith("文法"):
            sec = "g"
            name = (_split_pair(s)[1] or "").strip()
            if name and name not in ("選定なし", "なし"):
                j = i + 1
                if j >= len(lines) or lines[j].strip() != MARK_BEGIN:
                    raise RestoreError(f"文法「{name}」の{MARK_BEGIN}がありません。" + RECHECK_HINT)
                k = j + 1
                buf = []
                while k < len(lines) and lines[k].strip() != MARK_END:
                    buf.append(lines[k])
                    k += 1
                if k >= len(lines):
                    raise RestoreError(f"文法「{name}」の{MARK_END}がありません(解説が途中で切れています)。" + RECHECK_HINT)
                grams.append((name, "\n".join(buf)))
                i = k + 1
                continue
            i += 1
            continue
        if s.startswith("ニュアンス解説"):   # 旧フォームの欄見出し行(行頭の構造一致)=廃止済み。通常は黙って読み飛ばさず明示拒否。移行受理(legacy)のときだけ節を読み捨てる
            if not legacy:
                raise RestoreError(NUANCE_ABOLISHED_MSG)
            if nuance_in is not None:
                raise RestoreError("『ニュアンス解説：』の行が複数あります。" + RECHECK_HINT)
            name = (_split_pair(s)[1] or "").strip()
            if name in ("採用", "不採用"):
                j = i + 1
                if j >= len(lines) or lines[j].strip() != MARK_N_BEGIN:
                    raise RestoreError(f"ニュアンス解説（{name}）の{MARK_N_BEGIN}がありません。" + RECHECK_HINT)
                k = j + 1
                while k < len(lines) and lines[k].strip() != MARK_N_END:
                    k += 1
                if k >= len(lines):
                    raise RestoreError(f"ニュアンス解説（{name}）の{MARK_N_END}がありません(途中で切れています)。" + RECHECK_HINT)
                nuance_in = name
                i = k + 1
                continue
            if name == "候補なし":
                nuance_in = name
                i += 1
                continue
            raise RestoreError(f"ニュアンス解説の行を『採用|不採用|候補なし』として解釈できません: {s!r}。" + RECHECK_HINT)
        if s.startswith("自由コメント"):
            comment_lines = [(_split_pair(s)[1] or "").lstrip()]
            sec = "c"
            i += 1
            continue
        if isinstance(sec, int):
            bm = BULLET_RE.match(ln)
            if bm:
                term, gl = _split_pair(bm.group(1).strip())
                if gl is None:
                    raise RestoreError(f"項目行を「英語：日本語訳」に分解できません: {bm.group(1).strip()!r}")
                got[sec].append((term.strip(), gl.strip()))
            elif s and not s.startswith("（選択なし）") and not s.startswith("(選択なし)"):
                raise RestoreError(f"解釈できない行: {s!r}")
        elif sec is None and s and not FENCE_RE.match(ln) and BULLET_RE.match(ln):
            raise RestoreError(f"区分見出し(① ② ③)より前に項目があります: {s!r}")
        i += 1
    if comment_lines is None:
        raise RestoreError("『自由コメント：』の行がありません。" + RECHECK_HINT)
    while comment_lines and FENCE_RE.match(comment_lines[-1]):   # コードブロックの閉じ(```)がコメント末尾に残る場合
        comment_lines.pop()
    return {"hdr": hdr, "items": got, "grammar": grams, "comment_lines": comment_lines, "nuance_decision": nuance_in}


def _gloss_marker(gl_nfkc: str):
    mm = re.search(r"\((仮訳・未確定|日本語訳未生成)\)$", gl_nfkc)
    return (gl_nfkc[:mm.start()].strip(), mm.group(1)) if mm else (gl_nfkc, None)


def _legacy_aif2_verify(t: str, data_dir: str, legacy_bytes: bytes):
    """撤去前に発行・送信済みのAIF2回答の移行受理。旧フォームdata(legacy_bytes)に対して照合コード(チェック桁・d6・c8・t8)を検証し、
    旧dataが現行dataと『nuance/nuance_spec以外同一』であることを確認する。成立しなければ NUANCE_CORNER_ABOLISHED で拒否(fail-closed)。
    戻り値=(m, 現行data, 旧dataのnuance候補, legacy_meta)。"""
    m = None
    for m in CODE2_FULL_RE.finditer(t):
        pass
    if not m:
        raise RestoreError(NUANCE_ABOLISHED_MSG + "(旧データによる移行受理: AIF2照合コードを解釈できません)")
    stem, d6, c8, t8, s10, g10, m8, n8, chk = m.groups()
    if sha(m.group(0)[:-5])[:4] != chk:
        raise RestoreError("照合コードが壊れています(チェック不一致)。" + RECHECK_HINT)
    if d6_of_bytes(legacy_bytes) != d6:
        raise RestoreError(NUANCE_ABOLISHED_MSG + f"(--legacy-form-data のd6={d6_of_bytes(legacy_bytes)} が照合コードのd6={d6} と一致しません。移行受理できません)")
    old = json.loads(legacy_bytes.decode("utf-8"))
    if not old.get("nuance_spec"):
        raise RestoreError(NUANCE_ABOLISHED_MSG + "(旧dataにニュアンス仕様マークがなく、AIF2発行フォームのdataではありません)")
    if (old.get("candidates_sha256") or "0" * 8)[:8] != c8 or ((old.get("source") or {}).get("text_sha256") or "0" * 8)[:8] != t8:
        raise RestoreError("候補集合sha/本文shaが照合コードと一致しません(別データ)。" + RECHECK_HINT)
    dpath = os.path.join(data_dir, stem + ".json")
    if not os.path.exists(dpath):
        raise RestoreError(f"現行フォームdataがありません: {dpath}")
    cur = json.loads(open(dpath, "rb").read().decode("utf-8"))
    if any(k in cur for k in LEGACY_DROP_KEYS):
        raise RestoreError("現行フォームdataにニュアンスのキーが残っています(撤去済みでない)。移行受理できません")
    strip = {k: v for k, v in old.items() if k not in LEGACY_DROP_KEYS}
    if json.dumps(strip, sort_keys=True, ensure_ascii=False) != json.dumps(cur, sort_keys=True, ensure_ascii=False):
        raise RestoreError(NUANCE_ABOLISHED_MSG + "(旧dataと現行dataがnuance/nuance_spec以外で異なります。別データのため移行受理しません)")
    meta = {"legacy_aif2_accepted": True, "legacy_form_data_sha256": hashlib.sha256(legacy_bytes).hexdigest(), "legacy_form_data_d6": d6,
            "legacy_aif2_collation_code": m.group(0), "nuance_section": "discarded(採否は記録しない)"}
    return m, cur, (old.get("nuance") or None), meta


def restore(text: str, data_dir: str = DEFAULT_DATA_DIR, git_lookup=None, legacy_form_data: bytes = None):
    """貼付テキスト -> (payload v2, notes)。不一致は RestoreError(何も書かない)。
    git_lookup(stem, d6) -> bytes|None: 現在のデータ版がd6と異なるとき選定時の版を返す関数(None=履歴参照なし)。
    legacy_form_data: 撤去前に発行したAIF2フォームのdata bytes。AIF2回答は、これで照合できる場合に限りニュアンス節を読み捨てて受理する(移行受理)。"""
    t = text.replace("\r\n", "\n").replace("\r", "\n")
    legacy_meta = None
    if CODE2_RE.search(t):   # 旧AIF2(ニュアンス欄つきフォーム)=廃止済み。旧data照合が成立する場合のみ移行受理、それ以外は明示拒否
        if legacy_form_data is None:
            raise RestoreError(NUANCE_ABOLISHED_MSG)
        m, d, n_cand, legacy_meta = _legacy_aif2_verify(t, data_dir, legacy_form_data)
        stem, d6, c8, t8, s10, g10, m8, n8, chk = m.groups()
        notes = [f"旧AIF2フォームを移行受理(旧data d6={d6}で照合、ニュアンス節は読み捨て)"]
    else:
        m = None
        for m in CODE_RE.finditer(t):
            pass
        if not m:
            if re.search(r"AIF\d+-", t):
                raise RestoreError("未対応の形式バージョンの照合コードです(AIF1のみ対応)")
            raise RestoreError("照合コードが見つかりません。" + RECHECK_HINT)
        stem, d6, c8, t8, s10, g10, m8, chk = m.groups()
        if sha(m.group(0)[:-5])[:4] != chk:
            raise RestoreError("照合コードが壊れています(チェック不一致)。" + RECHECK_HINT)
        notes = []
        dpath = os.path.join(data_dir, stem + ".json")
        raw = open(dpath, "rb").read() if os.path.exists(dpath) else None
        if raw is None or d6_of_bytes(raw) != d6:
            raw2 = git_lookup(stem, d6) if git_lookup else None
            if raw2 is None:
                raise RestoreError(f"選定時のデータ版(d6={d6})が見つかりません(現在のデータと異なり、履歴にもありません)。フォームから選び直してください")
            raw = raw2
            notes.append(f"データ版を履歴から復元(d6={d6})")
        d = json.loads(raw.decode("utf-8"))
        if (d.get("candidates_sha256") or "0" * 8)[:8] != c8 or ((d.get("source") or {}).get("text_sha256") or "0" * 8)[:8] != t8:
            raise RestoreError("候補集合sha/本文shaが照合コードと一致しません(別データ)。" + RECHECK_HINT)

    ps = _parse_text(t, m, legacy=legacy_meta is not None)
    if legacy_meta is not None:   # ニュアンス節は読み捨てるが、照合コードのn8と貼付の採否・旧dataの候補が整合することだけ確認する(捏造・改変検出用。採否は記録しない)
        nd = ps["nuance_decision"]
        if nd is None:
            raise RestoreError("旧AIF2回答に『ニュアンス解説：』の行がありません。" + RECHECK_HINT)
        if nd == "候補なし":
            ok_n = (not n_cand) and n8 == "0"
        else:
            dec = {"採用": "adopt", "不採用": "reject"}[nd]
            ok_n = bool(n_cand) and n8 == sha("v1\n" + dec + ":" + n_cand["candidate_sha256"])[:8]
        if not ok_n:
            raise RestoreError("旧AIF2回答のニュアンス節が照合コード(n8)と一致しません(改変の疑い)。" + RECHECK_HINT)
    hdr_body = _split_pair(ps["hdr"])[1] or ""
    if "｜" in hdr_body:
        nm, lv = hdr_body.rsplit("｜", 1)
        if nfkc(nm) != nfkc(d["name"]) or nfkc(lv) != nfkc(d.get("level_label") or d.get("level") or ""):
            raise RestoreError(f"記事見出し {ps['hdr']!r} が照合コードのデータ({d['name']}｜{d.get('level_label') or d.get('level')})と一致しません")
    else:
        raise RestoreError(f"記事見出しを『記事：<記事名>｜<レベル>』に分解できません: {ps['hdr']!r}")
    comment = normalize_comment("\n".join(ps["comment_lines"]))

    its = items_of(d)
    order = {id(it): n for n, it in enumerate(its)}
    entries = []   # (cat, term, options[list of item])
    for cat in (1, 2, 3):
        for term, gl in ps["items"][cat]:
            cand = [it for it in its if it["term"] == term]
            if not cand:
                cand = [it for it in its if nfkc(it["term"]).casefold() == nfkc(term).casefold()]
                if cand:
                    notes.append(f"term正規化一致: {term!r}->{[c['term'] for c in cand]!r}")
            if not cand:
                raise RestoreError(f"英語表現 {term!r} が候補にありません(項目名が書き換えられた可能性)。" + RECHECK_HINT)
            gl_core, mark = _gloss_marker(nfkc(gl))
            ok = []
            for it in cand:
                if gl_core != nfkc(gloss_text(it) or "(未生成)"):
                    continue
                st_ = gloss_status(it)
                if mark is not None and GLOSS_MARK.get(st_, "") != f"（{mark}）":
                    continue   # 注記が区分と矛盾(例: 正式訳なのに『仮訳・未確定』)
                ok.append(it)
            if not ok:
                raise RestoreError(f"日本語訳が候補データと一致しません: {term!r} 貼付={gl!r} / 正={[gloss_text(c) for c in cand]!r}(黙って置換しません)。" + RECHECK_HINT)
            if mark is None and any(gloss_status(it) != "official" for it in ok):
                notes.append(f"{term!r}: 日本語訳の未確定注記が貼付にありません(データ側はofficialではない。確定時にer128が確認します)")
            entries.append((cat, term, ok))
    n_combo = 1
    for _, _, ok in entries:
        n_combo *= len(ok)
    if n_combo > MAX_COMBOS:
        raise RestoreError(f"同一表現が複数候補に該当し、組合せが{MAX_COMBOS}通りを超えます。フォームから選び直してください")
    chosen = None
    hits = 0
    for combo in itertools.product(*[ok for _, _, ok in entries]):
        cids = [cid_of(it) for it in combo]
        if len(set(cids)) != len(cids):
            continue   # 同じ項目が複数区分/重複
        by_cat = {c: sorted([it for (c2, _, _), it in zip(entries, combo) if c2 == c], key=lambda it: order[id(it)]) for c in (1, 2, 3)}
        sel_ids = [(c, cid_of(it)) for c in (1, 2, 3) for it in by_cat[c]]
        if sha("v1\n" + "\n".join(f"{c}:{i}" for c, i in sel_ids))[:10] == s10:
            chosen, hits = by_cat, hits + 1
    if hits == 0:
        raise RestoreError("選択内容(項目・区分)が照合コードと一致しません(項目の欠落・追加・区分の入替え、または変更の疑い)。" + RECHECK_HINT)
    if hits > 1:
        raise RestoreError("選択内容を一意に決定できません。フォームから選び直してください")
    sel = chosen

    gsel = []
    presented = grammar_presented(d)
    pres_ids = {g["id"] for g in presented}
    for title, body in ps["grammar"]:
        same = [g for g in (d.get("grammar") or []) if g["title"] == title]
        if not same:
            same = [g for g in (d.get("grammar") or []) if nfkc(g["title"]) == nfkc(title)]
        if not same:
            raise RestoreError(f"文法名 {title!r} が候補にありません。" + RECHECK_HINT)
        hit = [g for g in same if norm_body(body) == norm_body(g.get("body") or "")]
        if len(hit) != 1:
            raise RestoreError((f"文法「{title}」の解説全文が候補データと一致しません(省略・改変・追記の疑い)。" if not hit
                                else f"文法「{title}」を一意に解決できません(同名・同文{len(hit)}件)。") + RECHECK_HINT)
        if has_grammar_spec(d) and hit[0]["id"] not in pres_ids:
            raise RestoreError(f"文法「{title}」は提示範囲(AI評価Top1/Top2)外の候補です")
        gsel.append(hit[0])
    if len({g["id"] for g in gsel}) != len(gsel):
        raise RestoreError("同じ文法が複数回含まれています")
    pairs = [_gram_pair(g) for g in gsel]
    if (sha("v1\n" + "\n".join(f"{i}:{h}" for i, h in pairs))[:10] if pairs else "0") != g10:
        raise RestoreError("文法選択が照合コードと一致しません。" + RECHECK_HINT)

    cm_ok = None
    for cand_c in (comment, "\n".join(x.rstrip() for x in comment.split("\n"))):   # 行末空白が付いただけの貼付はshaで元と同一と証明できる場合に限り吸収
        if ((sha(cand_c)[:8]) if cand_c else "0") == m8:
            cm_ok = cand_c
            break
    if cm_ok is None:
        raise RestoreError("自由コメントが照合コードと一致しません(変更・追記・削除の疑い)。" + RECHECK_HINT)
    comment = cm_ok

    payload = _build_payload(d, sel, gsel, comment, st_grammar_none=(not gsel))
    payload["restore_meta"] = {"tool": TOOL_ID, "code_version": CODE_VERSION, "collation_code": m.group(0)}
    if legacy_meta is not None:
        payload["restore_meta"]["code_version"] = "AIF2(legacy)"
        payload["restore_meta"]["legacy"] = legacy_meta
    if d.get("kp_confirmed"):
        locked = _locked_selection(d, sel)
        payload["selection"]["key_phrase"] = locked[1]
        payload["selection"]["extra_explanation"] = locked[2]
        payload["selection"]["meaning_display"] = locked[3]
    return payload, notes


def _locked_selection(d: dict, sel: dict) -> dict:
    """確定済みKP/KW(kp_confirmed)の記事: payloadのselectionは確定レコードの逐語(form_logic.js buildStructuredと同じ)。貼付の項目集合と一致を要求。"""
    rec = d["kp_confirmed"].get("selection") or []
    by_cid = {r["candidate_id"]: r for r in rec}
    out = {1: [], 2: [], 3: []}
    got = {(c, cid_of(it)) for c in (1, 2, 3) for it in sel[c]}
    want = {(r["category"], r["candidate_id"]) for r in rec}
    if got != want:
        raise RestoreError("確定済みKey Phrase／Key Wordの内容と貼付の項目・区分が一致しません。" + RECHECK_HINT)
    for r in rec:
        out[r["category"]].append(copy.deepcopy(by_cid[r["candidate_id"]]))
    return out


def _item_record(it: dict, cat: int) -> dict:
    o = {"term": it["term"], "category": cat, "category_label": CAT_LABEL[cat], "ja_gloss": gloss_text(it), "ja_gloss_status": gloss_status(it),
         "candidate_id": cid_of(it), "kind": it.get("kind") if it.get("kind") in ("phrase", "word") else None}
    if it.get("selection_phrase") and it["selection_phrase"] != it["term"]:
        o["selection_phrase"] = it["selection_phrase"]
    return o


def _grammar_record(g: dict) -> dict:
    full = g.get("body") or ""
    r = {"id": g["id"], "title": g["title"], "explanation_full": full, "explanation_status": "provided" if full else "missing", "example": g.get("example") or ""}
    if g.get("candidate_id"):
        r["candidate_id"] = g["candidate_id"]
    if g.get("explanation_sha256"):
        r["explanation_sha256"] = g["explanation_sha256"]
    if g.get("level"):
        r["level"] = g["level"]
    if g.get("display_rank") or g.get("rank"):
        r["rank"] = g.get("display_rank") or g.get("rank")
        r["rank_label"] = "Top " + str(r["rank"])
    return r


def _build_payload(d: dict, sel: dict, gsel: list, comment: str, st_grammar_none: bool) -> dict:
    pres = {g["id"]: g for g in grammar_presented(d)}
    gsel_p = [pres.get(g["id"], g) for g in gsel]   # display_rank付きの提示版(form_logic.jsはgrammarPresented由来のrecordを送る)
    sha_ = d.get("candidates_sha256") or None
    payload = {
        "schema": "eigo_radio_selection_result_v2", "schema_version": 2, "schema_minor": 1,
        "article": {"slug": d["slug"], "level": d["level"], "level_label": d.get("level_label") or "", "name": d["name"],
                    "text_sha256": (d.get("source") or {}).get("text_sha256") or None, "candidates_sha256": sha_,
                    "candidates_sha256_source": d.get("candidates_sha256_source") or ("candidate_doc_field" if sha_ else "unavailable"),
                    "source_kp_candidates_path": d.get("source_kp_candidates_path") or None},
        "selection": {"key_phrase": [_item_record(it, 1) for it in sel[1]], "extra_explanation": [_item_record(it, 2) for it in sel[2]],
                      "meaning_display": [_item_record(it, 3) for it in sel[3]], "grammar": [_grammar_record(g) for g in gsel_p]},
        "comment": comment,
    }
    presented = list(pres.values())
    if has_grammar_spec(d):
        state = "n/a" if not presented else ("selected" if gsel else "none")
        payload["grammar_status"] = {"selected": "user_selected_one", "none": "user_selected_none", "n/a": "no_candidates_found"}[state]
        payload["grammar_decision"] = {"state": state, "spec": "top2_select1_v1", "max_select": GRAMMAR_MAX,
                                       "presented": [{"rank": g["display_rank"], "candidate_id": g.get("candidate_id") or g["id"], "title": g["title"]} for g in presented],
                                       "selected_candidate_id": (gsel[0].get("candidate_id") or gsel[0]["id"]) if gsel else None}
    else:
        payload["grammar_status"] = ("candidates_available" if presented else (d.get("grammar_status") if d.get("grammar_status") == "no_candidates_found" else "no_candidates_ungenerated"))
    if d.get("kp_confirmed"):
        kc = d["kp_confirmed"]
        payload["kp_confirmed"] = {"status": kc.get("status"), "locked": True, "confirmed_at": kc.get("confirmed_at") or None, "user_ref": kc.get("user_ref") or None,
                                   "note_ja": KP_CONFIRMED_NOTE}
    return payload


# ---------------------------------------------------------------- 確定(既存cmd_from_formへ委譲)
def payload_bytes(payload: dict) -> bytes:
    return (json.dumps(payload, ensure_ascii=False, indent=1) + "\n").encode("utf-8")


def summarize(payload: dict, notes: list) -> dict:
    sel = payload["selection"]
    return {"article": f"{payload['article']['name']}｜{payload['article']['level_label']}", "collation_code": payload["restore_meta"]["collation_code"],
            "key_phrase": [(i["term"], i["ja_gloss"], i["candidate_id"]) for i in sel["key_phrase"]],
            "extra_explanation": [(i["term"], i["ja_gloss"], i["candidate_id"]) for i in sel["extra_explanation"]],
            "meaning_display": [(i["term"], i["ja_gloss"], i["candidate_id"]) for i in sel["meaning_display"]],
            "grammar": [(g["title"], g.get("candidate_id") or g["id"], len(g["explanation_full"])) for g in sel["grammar"]],
            "comment": payload["comment"], "candidates_sha256": payload["article"]["candidates_sha256"], "text_sha256": payload["article"]["text_sha256"],
            "payload_sha256": hashlib.sha256(payload_bytes(payload)).hexdigest(), "notes": notes}


def load_restore(text_path: str, data_dir: str = DEFAULT_DATA_DIR, legacy_form_data_path: str = None):
    with open(text_path, "rb") as f:
        raw = f.read()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as e:
        raise RestoreError(f"貼付テキストがUTF-8として読めません: {e}") from e
    legacy_bytes = None
    if legacy_form_data_path:
        with open(legacy_form_data_path, "rb") as f:
            legacy_bytes = f.read()
    payload, notes = restore(text, data_dir, lambda stem, d6: git_history_lookup(stem, d6, data_dir), legacy_form_data=legacy_bytes)
    if len(payload["selection"]["key_phrase"]) != BATCH_KP_EXACT and not payload.get("kp_confirmed"):   # 単体(旧)受入は拒否しない。警告ノートのみ
        notes = list(notes) + [f"警告: ①Key Phraseが{len(payload['selection']['key_phrase'])}件です(新仕様はちょうど{BATCH_KP_EXACT}件。単体受入は互換のため拒否しません)"]
    return raw, payload, notes


def cmd_from_readable(text_path: str, run: str, level: str, by: str, user_ref: str, *, actor: str = "user", grammar_pending: bool = False,
                      dry_run: bool = False, data_dir: str = DEFAULT_DATA_DIR, legacy_form_data_path: str = None) -> dict:
    """貼付テキストを復元し、既存 cmd_from_form(検証・保存は無変更)へ委譲する。貼付原文は確定成功後に rev{N}_readable.txt へそのまま保存する。"""
    raw, payload, notes = load_restore(text_path, data_dir, legacy_form_data_path)
    if payload["article"]["level"] != level:
        raise RestoreError(f"貼付のレベル({payload['article']['level']})が --level={level} と異なります")
    out = {"restored": summarize(payload, notes), "readable_sha256": hashlib.sha256(raw).hexdigest(), "dry_run": dry_run}
    if dry_run:
        out["next"] = "dry-runのため確定していません。--dry-run を外して同じコマンドを実行すると cmd_from_form(confirm --from-form 相当)で確定します"
        return out
    import er128_kp_confirmed_content_01 as c   # 遅延import(復元だけの利用では不要)
    fd, tmp = tempfile.mkstemp(suffix=".json", prefix="readable_restore_")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(payload_bytes(payload))
        legacy = (payload.get("restore_meta") or {}).get("legacy")   # 移行受理(旧AIF2)は確定recordのorigin.transcriptionへ由来を残す
        extra = {"origin_extra": dict(legacy)} if legacy else {}   # 通常(AIF1)は従来どおりの呼出(引数追加なし)
        res = c.cmd_from_form(run, level, tmp, by, user_ref, actor=actor, grammar_pending=grammar_pending, **extra)
    finally:
        try:
            os.remove(tmp)
        except OSError:
            pass
    kp_dir = c._kp_dir_for(run, level)
    sdir = c.paths_of(kp_dir)["source_dir"]
    os.makedirs(sdir, exist_ok=True)
    rpath = os.path.join(sdir, f"rev{res['revision']}_readable.txt")
    with open(rpath, "wb") as f:
        f.write(raw)
    out["confirmed"] = res
    out["readable_saved"] = rpath
    return out


# ---------------------------------------------------------------- 一括受入(SELECTION-UI-BATCH-AND-VOCAB-AUDIO-01 委任_02B。既存restore/cmd_from_readableは無変更。新関数の追加のみ)
BATCH_HEADER_RE = re.compile(r"^[ \t]*件数=(\d+)[ \t]*/[ \t]*生成=(\S+)[ \t]*/[ \t]*バッチ=(\S+?)[ \t]*$", re.M)
BATCH_SEP_RE = re.compile(r"^[ \t]*════ SET (\d+)/(\d+) ｜ ([A-Za-z0-9_]+) ════[ \t]*$", re.M)
BATCH_END_RE = re.compile(r"^[ \t]*════ END 合計(\d+)件 / BATCH1-(\d+)-([0-9a-f]{10}) ════[ \t]*$", re.M)
BATCH_KP_EXACT = 3   # 区分①(Key Phrase)はちょうど3件(2026-10-30ユーザー指示)。kp_confirmed(ユーザー確定済み)はフォームDone条件と同じく免除


def batch_code(codes: list) -> str:
    """一括コード本体 BATCH1-<N>-<sha10>: 各セットの照合コード(AIF1/AIF2全文)を並び順にそのまま連結したもののsha256先頭10桁。"""
    return f"BATCH1-{len(codes)}-" + sha("".join(codes))[:10]


def _batch_codes_in(block: str) -> list:
    """ブロック内の照合コードを全て返す(ちょうど1個を要求するのは呼出側)。AIF\\d+-の出現は全て有効な全文コードでなければならない(壊れた/未対応版コードを黙って無視しない)。"""
    full = [m.group(0) for m in CODE_RE.finditer(block)] + [m.group(0) for m in CODE2_FULL_RE.finditer(block)]
    n_prefix = len(re.findall(r"AIF\d+-", block))
    if n_prefix != len(full):
        raise RestoreError("照合コードが壊れているか未対応の形式バージョンです(AIF1以外・書式不正)。" + RECHECK_HINT)
    return full


def _batch_split(t: str):
    """正規化済みテキスト -> (head, seps, blocks, end)。区切り/ENDの構造検査は呼出側。"""
    seps = list(BATCH_SEP_RE.finditer(t))
    ends = list(BATCH_END_RE.finditer(t))
    return seps, ends


# ---- 委任_04(SELECTION-UI-BATCH-AND-VOCAB-AUDIO-01): 報告(batch)ファイル解決(追加のみ。既存の articles.json batch 経路は無変更) ----
# batch id の正規表現はUI(form_logic.js BATCH_ID_RE)・publish toolと同一。不一致=fail-closed(パストラバーサル対策)
BATCH_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{2,63}$")


def load_batch_file(batch_id: str, batches_dir: str) -> dict:
    """data/batches/<id>.json(schema=eigo_radio_batch_v1)を読み {id, members, ...} を返す。id不正/ファイル無し/schema・id・members不正は RestoreError(何も確定しない)。"""
    if not isinstance(batch_id, str) or not BATCH_ID_RE.match(batch_id):
        raise RestoreError(f"batch id の形式が不正です(英小文字/数字/_/-、3〜64文字): {batch_id!r}")
    base = os.path.realpath(batches_dir)
    path = os.path.realpath(os.path.join(base, batch_id + ".json"))
    if os.path.dirname(path) != base:
        raise RestoreError(f"batchファイルのパスがbatchesディレクトリ外です: {batch_id!r}")
    if not os.path.isfile(path):
        raise RestoreError(f"batchファイルが見つかりません: {path}(報告が未公開か、idが違います)")
    with open(path, "rb") as f:
        doc = json.loads(f.read().decode("utf-8-sig"))
    if not isinstance(doc, dict) or doc.get("schema") != "eigo_radio_batch_v1" or doc.get("id") != batch_id:
        raise RestoreError(f"batchファイルのschema/idが不正です: {path}")
    ms = doc.get("members")
    if not isinstance(ms, list) or not ms or len(set(ms)) != len(ms) or not all(isinstance(m, str) for m in ms):
        raise RestoreError(f"batchファイルのmembersが空/重複/不正です: {path}")
    return doc


def resolve_batch_from_header(t: str, batches_dir: str) -> dict:
    """貼付全文の一括ヘッダ『バッチ=<id>』からbatchファイルを解決する(articles.jsonにbatchキーが無い場合の経路)。"""
    hs = list(BATCH_HEADER_RE.finditer(t))
    if len(hs) != 1:
        raise RestoreError(f"一括ヘッダ『件数=N / 生成=… / バッチ=…』が{len(hs)}個あります(ちょうど1個が必要)。batch(id/members)を特定できません(fail-closed)")
    return load_batch_file(hs[0].group(3), batches_dir)


def restore_batch(text: str, *, articles_json: str, legacy_form_data=None, data_dir: str = DEFAULT_DATA_DIR, git_lookup="default", batches_dir: str = None):
    """一括コピー(フォームの『まとめてコピー』)の貼付全文 -> payload v2のlist(SET順)。1件でも失敗なら RestoreError(何も返さず、全エラーを列挙)。
    検査: ヘッダ(件数/生成/バッチ)・SET区切り連番・END・BATCH1コード・各ブロックにAIF照合コードがちょうど1個・stem一致・重複セットなし・
    articles.json の batch(未指定=fail-closed)の id と members の完全一致(欠落/余剰セット検出)・各ブロックを既存restore()で照合・区分①ちょうど3件(kp_confirmedは免除)。
    legacy_form_data: bytes(単一)またはdict(stem->bytes)。旧AIF2回答の移行受理は既存restore()と同じ条件。git_lookup: 'default'=git履歴参照 / None=参照なし / callable。"""
    errs = []
    t = text.replace("\r\n", "\n").replace("\r", "\n")
    with open(articles_json, "rb") as f:
        art = json.loads(f.read().decode("utf-8-sig"))
    batch = art.get("batch")
    if not isinstance(batch, dict) and (batch is None):
        # 委任_04: articles.json に batch が無い場合のみ、貼付ヘッダのバッチidから data/batches/<id>.json を解決する(articles.json batch 経路は従来どおり)
        batch = resolve_batch_from_header(t, batches_dir or os.path.join(os.path.dirname(os.path.abspath(articles_json)), "batches"))
    if not isinstance(batch, dict) or not batch.get("id") or not isinstance(batch.get("members"), list) or not batch["members"]:
        raise RestoreError("articles.json に batch(id/members)が指定されていません。一括受入は対象バッチが指定されている場合のみ行います(fail-closed)")
    members = list(batch["members"])
    if len(set(members)) != len(members):
        raise RestoreError(f"articles.json batch.members に重複があります: {members!r}")
    seps, ends = _batch_split(t)
    if not seps:
        raise RestoreError("一括コピーの『════ SET i/N ｜ …』区切りが見つかりません。" + RECHECK_HINT)
    if len(ends) != 1:
        raise RestoreError(f"一括コピーの末尾『════ END 合計N件 / BATCH1-…』が{len(ends)}個あります(ちょうど1個が必要。末尾が切れていないか確認してください)")
    end = ends[0]
    if end.start() < seps[-1].end():
        raise RestoreError("END行がSET区切りより前にあります(並びが不正)")
    head = t[:seps[0].start()]
    hs = list(BATCH_HEADER_RE.finditer(head))
    if len(hs) != 1:
        raise RestoreError(f"一括ヘッダ『件数=N / 生成=… / バッチ=…』が{len(hs)}個あります(ちょうど1個が必要)")
    h_n, h_gen, h_id = int(hs[0].group(1)), hs[0].group(2), hs[0].group(3)
    try:
        import datetime as _dt
        _dt.datetime.fromisoformat(h_gen.replace("Z", "+00:00"))
    except ValueError:
        errs.append(f"一括ヘッダの生成日時がISO形式ではありません: {h_gen!r}")
    n = len(seps)
    if h_n != n:
        errs.append(f"ヘッダ件数={h_n} とSET区切りの数={n} が一致しません(欠落/重複の疑い)")
    if int(end.group(1)) != n:
        errs.append(f"END合計={end.group(1)}件 とSET区切りの数={n} が一致しません")
    if h_id != batch["id"]:
        errs.append(f"ヘッダのバッチ={h_id!r} が articles.json の batch.id={batch['id']!r} と異なります(別バッチ/古いフォーム)")
    blocks, stems, codes = [], [], []
    for i, m in enumerate(seps):
        stop = seps[i + 1].start() if i + 1 < len(seps) else end.start()
        blocks.append(t[m.end():stop])
        if int(m.group(1)) != i + 1 or int(m.group(2)) != n:
            errs.append(f"SET区切りの連番が不正です(位置{i + 1}: 『SET {m.group(1)}/{m.group(2)}』、期待 {i + 1}/{n})")
    for i, (m, blk) in enumerate(zip(seps, blocks), 1):
        stems.append(m.group(3))
        try:
            cs = _batch_codes_in(blk)
        except RestoreError as e:
            errs.append(f"SET {i}({m.group(3)}): {e}")
            codes.append(None)
            continue
        if len(cs) != 1:
            errs.append(f"SET {i}({m.group(3)}): 照合コードが{len(cs)}個あります(ちょうど1個が必要。ブロックの混入/欠落の疑い)")
            codes.append(None)
            continue
        cm_ = CODE_RE.fullmatch(cs[0]) or CODE2_FULL_RE.fullmatch(cs[0])
        if cm_.group(1) != m.group(3):
            errs.append(f"SET {i}: 区切りのセット名 {m.group(3)!r} と照合コードのセット名 {cm_.group(1)!r} が一致しません")
        codes.append(cs[0])
    dups = sorted({s for s in stems if stems.count(s) > 1})
    if dups:
        errs.append(f"同じセットが複数含まれています: {dups!r}")
    if set(stems) != set(members):
        errs.append(f"受領したセットがバッチ対象と一致しません(欠落={sorted(set(members) - set(stems))!r} / 対象外={sorted(set(stems) - set(members))!r})")
    got_code = f"BATCH1-{end.group(2)}-{end.group(3)}"
    if all(c is not None for c in codes):
        want = batch_code(codes)
        if want != got_code:
            errs.append(f"一括コードが一致しません(貼付={got_code} / 計算={want})。セットの欠落・順序入替え・内容変更の疑い")
    if git_lookup == "default":
        git_lookup_ = lambda stem, d6: git_history_lookup(stem, d6, data_dir)   # noqa: E731
    else:
        git_lookup_ = git_lookup
    payloads = []
    for i, (blk, code) in enumerate(zip(blocks, codes), 1):
        if code is None:
            continue
        legacy = legacy_form_data.get(stems[i - 1]) if isinstance(legacy_form_data, dict) else legacy_form_data
        try:
            payload, notes = restore(blk, data_dir, git_lookup_, legacy_form_data=legacy)   # 既存restore()をそのまま使用(ブロック1個=コード1個なので最後採用の曖昧さなし)
        except RestoreError as e:
            errs.append(f"SET {i}({stems[i - 1]}): {e}")
            continue
        n_kp = len(payload["selection"]["key_phrase"])
        if n_kp != BATCH_KP_EXACT and not payload.get("kp_confirmed"):
            errs.append(f"SET {i}({stems[i - 1]}): ①Key Phraseが{n_kp}件です(ちょうど{BATCH_KP_EXACT}件が必要。一括受入では拒否します)")
            continue
        payload["restore_meta"]["batch"] = {"id": h_id, "index": i, "n": n, "stem": stems[i - 1], "batch_code": got_code, "generated": h_gen,
                                           "block_sha256": hashlib.sha256(blk.encode("utf-8")).hexdigest()}
        if notes:
            payload["restore_meta"]["notes"] = list(notes)
        payloads.append(payload)
    if errs:
        raise RestoreError("一括受入を拒否しました(何も確定していません)。エラー" + str(len(errs)) + "件:\n- " + "\n- ".join(errs))
    return payloads


def cmd_from_readable_batch(text_path: str, *, articles_json: str, run_map: dict = None, by: str = None, user_ref: str = "", actor: str = "user",
                            grammar_pending: bool = False, dry_run: bool = False, data_dir: str = DEFAULT_DATA_DIR, legacy_form_data_path: str = None) -> dict:
    """一括コピーを復元し(全件検証が通るまで何も書かない)、dry_runでなければ各セットを既存cmd_from_formへ委譲して確定する。
    run_map: {stem: run_dir}(確定時必須。全セット分が揃っていなければ何も確定せず拒否)。確定前に全セットで候補sha・既確定guardを事前検査し、
    全payloadをtempへ書き切ってから確定ループに入る。cmd_from_form自体はセット単位の確定(複数記事を跨ぐ単一トランザクションは作れない)ため、
    事前検査後に想定外の失敗が起きた場合は確定済みセットを例外のbatch_partialへ添えて停止する(隠さない)。"""
    with open(text_path, "rb") as f:
        raw = f.read()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as e:
        raise RestoreError(f"貼付テキストがUTF-8として読めません: {e}") from e
    legacy_bytes = None
    if legacy_form_data_path:
        with open(legacy_form_data_path, "rb") as f:
            legacy_bytes = f.read()
    payloads = restore_batch(text, articles_json=articles_json, legacy_form_data=legacy_bytes, data_dir=data_dir)
    out = {"batch_id": payloads[0]["restore_meta"]["batch"]["id"], "n": len(payloads), "readable_sha256": hashlib.sha256(raw).hexdigest(), "dry_run": dry_run,
           "restored": [summarize(p, (p["restore_meta"].get("notes") or [])) for p in payloads]}
    if dry_run:
        out["next"] = "dry-runのため確定していません。--dry-run を外し --run-map(stem->run dir のjson)を付けて同じコマンドを実行すると各セットをcmd_from_formで確定します"
        return out
    rm = run_map or {}
    stems = [p["restore_meta"]["batch"]["stem"] for p in payloads]
    missing = sorted(set(stems) - set(rm))
    if missing:
        raise RestoreError(f"--run-map に次のセットのrunがありません: {missing!r}(何も確定していません)")
    blocks = []
    t = text.replace("\r\n", "\n").replace("\r", "\n")
    sp = list(BATCH_SEP_RE.finditer(t))
    en = BATCH_END_RE.search(t)
    blocks = [t[m.end():(sp[i + 1].start() if i + 1 < len(sp) else en.start())] for i, m in enumerate(sp)]
    import er128_kp_confirmed_content_01 as c   # 遅延import(復元だけの利用では不要)
    for stem, p in zip(stems, payloads):   # 事前検査(何も書かない): 候補sha・既確定guard
        kp_dir = c._kp_dir_for(rm[stem], p["article"]["level"])
        cands = c.rv.load_candidates(kp_dir)
        if p["article"].get("candidates_sha256") != cands["candidates_sha256"]:
            raise RestoreError(f"{stem}: フォームの候補集合sha256が現在の候補docと一致しません。何も確定していません")
        c.guard(kp_dir, "confirm --from-readable-batch(既にユーザー確定済み)")
    tmps = []
    try:
        for p in payloads:   # 全payloadを先にtempへ書き切る(書込失敗なら確定前に中止)
            fd, tmp = tempfile.mkstemp(suffix=".json", prefix="readable_batch_restore_")
            tmps.append(tmp)
            with os.fdopen(fd, "wb") as f:
                f.write(payload_bytes(p))
        confirmed = []
        for stem, p, tmp, blk in zip(stems, payloads, tmps, blocks):
            lv = p["article"]["level"]
            legacy = (p.get("restore_meta") or {}).get("legacy")
            extra = {"origin_extra": dict(legacy)} if legacy else {}
            try:
                res = c.cmd_from_form(rm[stem], lv, tmp, by, user_ref, actor=actor, grammar_pending=grammar_pending, **extra)
            except Exception as e:
                e.batch_partial = {"confirmed_before_failure": confirmed, "failed_set": stem}
                raise
            sdir = c.paths_of(c._kp_dir_for(rm[stem], lv))["source_dir"]
            os.makedirs(sdir, exist_ok=True)
            rpath = os.path.join(sdir, f"rev{res['revision']}_readable.txt")
            with open(rpath, "wb") as f:
                f.write(blk.encode("utf-8"))
            confirmed.append({"stem": stem, "confirmed": res, "readable_saved": rpath})
        out["confirmed"] = confirmed
    finally:
        for tmp in tmps:
            try:
                os.remove(tmp)
            except OSError:
                pass
    return out


def run_confirm_batch(a) -> int:
    """CLI(--from-readable-batch)。終了コードはrun_confirmと同じ規約: 4=ISSUE/2=拒否。"""
    try:
        rm = None
        if getattr(a, "run_map", None):
            with open(a.run_map, "rb") as f:
                rm = json.loads(f.read().decode("utf-8-sig"))
        if not a.dry_run and not rm:
            raise RestoreError("確定には --run-map(stem->run dirのjson)が必要です(まず --dry-run で照合を確認してください)")
        out = cmd_from_readable_batch(a.from_readable_batch, articles_json=a.articles_json, run_map=rm, by=a.by, user_ref=a.user_ref, actor=a.actor,
                                      grammar_pending=a.grammar_pending, dry_run=a.dry_run, data_dir=a.data_dir, legacy_form_data_path=getattr(a, "legacy_form_data", None))
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0
    except RestoreError as e:
        print(f"[READABLE_RESTORE][REFUSED] {e}", file=sys.stderr)
        return 2
    except Exception as e:
        import er128_kp_confirmed_content_01 as c
        part = getattr(e, "batch_partial", None)
        if part:
            print("[READABLE_RESTORE][BATCH_PARTIAL] " + json.dumps(part, ensure_ascii=False), file=sys.stderr)
        if isinstance(e, c.rv.ConfirmedContentIssue):
            print(f"[CONFIRMED_CONTENT][ISSUE] {e}", file=sys.stderr)
            return c.rv.EXIT_CODE_PENDING
        if isinstance(e, (c.CliError, c.rv.KpReviewError, ValueError)):
            print(f"[CONFIRMED_CONTENT][REFUSED] {type(e).__name__}: {e}", file=sys.stderr)
            return 2
        raise


def add_batch_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("--from-readable-batch", required=True, help="一括コピーの貼付テキストfile。全件照合PASSまで何も書かない。--dry-runで照合のみ")
    p.add_argument("--articles-json", default=os.path.join(DEFAULT_DATA_DIR, "articles.json"), help="batch(id/members)を含むarticles.json(未指定batchはfail-closed)")
    p.add_argument("--run-map", default=None, help="確定時必須: {\"<slug__lvl>\": \"<run dir>\"} のjson")
    p.add_argument("--by", default=None)
    p.add_argument("--user-ref", default="")
    p.add_argument("--grammar-pending", action="store_true")
    p.add_argument("--actor", default="user", choices=("user", "evidence"))
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--data-dir", default=DEFAULT_DATA_DIR)
    p.add_argument("--legacy-form-data", default=None)


# ---------------------------------------------------------------- CLI
def add_confirm_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("--from-readable", required=True, help="貼付テキストのfile(ChatGPTの返信全体でも可)")
    p.add_argument("--run", required=True)
    p.add_argument("--level", required=True, choices=("a2", "b1b"))
    p.add_argument("--by", default=None)
    p.add_argument("--user-ref", default="")
    p.add_argument("--grammar-pending", action="store_true", help="KP/KWだけを確定し文法は選定待ちのままにする(cmd_from_formへ透過)")
    p.add_argument("--actor", default="user", choices=("user", "evidence"))
    p.add_argument("--dry-run", action="store_true", help="復元payloadと照合結果のみ出力し、確定しない")
    p.add_argument("--data-dir", default=DEFAULT_DATA_DIR)
    p.add_argument("--legacy-form-data", default=None, help="撤去前に発行した旧AIF2フォームのdata file(git履歴から取り出したもの)。旧AIF2回答の移行受理(ニュアンス節は読み捨て)にだけ使う。照合が成立しなければ拒否")


def run_confirm(a) -> int:
    """er128のCLIと同じ終了コード規約: 4=ISSUE(要確認)/2=拒否。"""
    try:
        out = cmd_from_readable(a.from_readable, a.run, a.level, a.by, a.user_ref, actor=a.actor, grammar_pending=a.grammar_pending,
                                dry_run=a.dry_run, data_dir=a.data_dir, legacy_form_data_path=getattr(a, "legacy_form_data", None))
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0
    except RestoreError as e:
        print(f"[READABLE_RESTORE][REFUSED] {e}", file=sys.stderr)
        return 2
    except Exception as e:   # er128の例外(ConfirmedContentIssue/CliError等)は遅延importのため型名で分岐
        import er128_kp_confirmed_content_01 as c
        if isinstance(e, c.rv.ConfirmedContentIssue):
            print(f"[CONFIRMED_CONTENT][ISSUE] {e}", file=sys.stderr)
            return c.rv.EXIT_CODE_PENDING
        if isinstance(e, (c.CliError, c.rv.KpReviewError, ValueError)):
            print(f"[CONFIRMED_CONTENT][REFUSED] {type(e).__name__}: {e}", file=sys.stderr)
            return 2
        raise


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("restore", help="復元payloadの出力のみ(確定しない)")
    p.add_argument("--text", required=True)
    p.add_argument("--data-dir", default=DEFAULT_DATA_DIR)
    p.add_argument("--out", default=None)
    p.add_argument("--legacy-form-data", default=None, help="旧AIF2回答の移行受理用(confirmと同じ)")
    add_confirm_args(sub.add_parser("confirm", help="復元して cmd_from_form へ委譲(確定)"))
    add_batch_args(sub.add_parser("confirm-batch", help="一括コピーを全件照合してから各セットを確定(--from-readable-batch。委任_02B)"))
    return ap


def run(argv=None) -> int:
    a = build_parser().parse_args(argv)
    if a.cmd == "restore":
        try:
            _, payload, notes = load_restore(a.text, a.data_dir, a.legacy_form_data)
        except RestoreError as e:
            print(f"[READABLE_RESTORE][REFUSED] {e}", file=sys.stderr)
            return 2
        if a.out:
            with open(a.out, "wb") as f:
                f.write(payload_bytes(payload))
        print(json.dumps({"restored": summarize(payload, notes), "out": a.out}, ensure_ascii=False, indent=2))
        return 0
    if a.cmd == "confirm-batch":
        return run_confirm_batch(a)
    return run_confirm(a)


if __name__ == "__main__":
    sys.exit(run())
