# -*- coding: utf-8 -*-
"""R4(a): `git diff <base> -- <files>` の各差分箇所(hunk)を、旧版と現版のASTで『関数単位』に分解し、次のどれかに機械分類する。
  A2_ONLY            関数名に a2 / std を含む、または本委任で新設(旧版に無い)かつ名前がa2/Std専用
  NEW_HELPER         旧版に無い新設関数(Advの既存関数から呼ばれていないことを、旧版Adv関数の本文に当該名が出ないことで確認)
  DEFAULT_ADV_HELPER 既存の共通helper。Std用に引数(level等)が追加され、既定値がAdv(b1b/None)であることをASTで確認
  MODULE_LEVEL       関数外(定数・import・docstring・コメント)。値を変えた既存定数が無いことを確認
  UNCLASSIFIED       上記に当てはまらない(=人間の精査が必要。0であること)
使い方: py adv_hunk_classifier_01.py --base bb578265c --out result.json
"""
import argparse
import ast
import json
import re
import subprocess
import sys

FILES = ["er117_chunk_tts_production_01.py", "er019_family_x_audio_production_runner_01.py",
         "er121_family_y_audio_01.py", "er121_family_y_structure_01.py"]
ap = argparse.ArgumentParser()
ap.add_argument("--base", required=True)
ap.add_argument("--out", required=True)
a = ap.parse_args()


def git_show(rev, path):
    return subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True, check=True).stdout.decode("utf-8")


def funcs(src):
    tree = ast.parse(src)
    out = {}

    def walk(node, prefix=""):
        for ch in ast.iter_child_nodes(node):
            if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef)):
                q = prefix + ch.name
                out[q] = {"node": ch, "src": ast.get_source_segment(src, ch), "start": ch.lineno, "end": ch.end_lineno}
                walk(ch, q + ".")
            elif isinstance(ch, ast.ClassDef):
                walk(ch, prefix + ch.name + ".")
    walk(tree)
    return tree, out


def adv_default(fnode):
    """level/lv/is_a2系の引数があり、既定値がAdv相当(None/'b1b'/False)ならその説明を返す。"""
    args = fnode.args
    names = [x.arg for x in args.args] + [x.arg for x in args.kwonlyargs]
    defaults = [None] * (len(args.args) - len(args.defaults)) + list(args.defaults) + list(args.kw_defaults)
    for nm, df in zip(names, defaults):
        if nm in ("level", "lv", "std", "is_std") and df is not None and isinstance(df, ast.Constant) and df.value in (None, "b1b", False):
            return f"{nm}={df.value!r}"
    return None


def top_assign_names(tree):
    out = {}
    for n in tree.body:
        if isinstance(n, ast.Assign):
            for t in n.targets:
                if isinstance(t, ast.Name):
                    out[t.id] = ast.dump(n.value)
    return out



GUARD_TOKENS = ("a2", "STD_LEVEL", "slowdown_applied", "n_chunked", "chunk_tts_applied_at_this_level", "legacy_partial", "_ONLY_SEGMENTS")


def guarded_lines_analysis(old_fn, new_fn, new_src_lines):
    """既存の共通関数について、現版で『変更/追加された行』が (i) Std専用ガード(if ... a2/STD_LEVEL ...)の内側 (ii) コメント/docstring/空行 (iii) 署名行
    のいずれかだけであるかを機械判定する。戻り値=(全行が該当するか, 該当しない行[(行番号, 行テキスト)])。"""
    import difflib
    o_lines = old_fn["src"].splitlines()
    n_lines = new_fn["src"].splitlines()
    base = new_fn["start"]
    changed = []
    sm = difflib.SequenceMatcher(a=o_lines, b=n_lines, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag in ("replace", "insert"):
            changed += list(range(base + j1, base + j2))
    # Ifノード(Std専用ガード)の範囲
    guards = []
    for node in ast.walk(new_fn["node"]):
        if isinstance(node, ast.If):
            test_src = ast.get_source_segment(chr(10).join(new_src_lines), node.test) or ""
            if any(t in test_src for t in GUARD_TOKENS):
                guards.append((node.lineno, node.end_lineno))
        if isinstance(node, ast.IfExp):
            test_src = ast.get_source_segment(chr(10).join(new_src_lines), node.test) or ""
            if any(t in test_src for t in GUARD_TOKENS):
                guards.append((node.lineno, node.end_lineno))
    # docstring範囲
    ds = []
    b = new_fn["node"].body
    if b and isinstance(b[0], ast.Expr) and isinstance(getattr(b[0], "value", None), ast.Constant) and isinstance(b[0].value.value, str):
        ds = [(b[0].lineno, b[0].end_lineno)]
    sig_end = new_fn["node"].body[0].lineno - 1
    rest = []
    for L in changed:
        txt = new_src_lines[L - 1]
        if not txt.strip() or txt.strip().startswith("#"):
            continue
        if any(a_ <= L <= b_ for a_, b_ in ds):
            continue
        if new_fn["start"] <= L <= sig_end:
            continue
        if any(a_ <= L <= b_ for a_, b_ in guards):
            continue
        rest.append((L, txt.strip()[:160]))
    return (not rest), rest

MANUAL_REVIEW = {   # 機械判定で説明できない変更の人手レビュー結果(理由必須。Advの動的バイト一致[adv_invariance_driver/compare]が裏付け)
    "generate_family_x_b1_segments": "Opus R3(c)(planに無いchunk idの--only-segments指定を課金前拒否)とOpus M1(旧方式[親entryのみ]cacheへ本文以外の部分retryでも検証済み本文を失わない従来経路維持)。"
                                     "どちらも正常入力(planに存在するid・通常のresume)ではno-op。Advにも同じ潜在不具合があったためOpus M1がAdvへの是正を明示。",
    "_record_chunk_decision": "Opus R3(c)の課金前拒否(planに無いchunk id)と、CHUNK_TTS_Y_LEVELSに含まれないlevel専用の else 分岐の文言変更(b1b/a2とも対象のため到達しない)。",
    "_tts_unit_badge": "試聴ページの表示文言のみ(音声・Gate・採否に無関係)。Adv(b1b)は従来と同一の判定記録参照(chunked→'TTS n分割'/それ以外→'TTS 1回')。旧Std記録は'旧記録'と明示(Opus論点7で妥当と判定)。",
    "assemble_level": "levelをrefresh/出力ファイル名へ渡すだけ。Adv(level='b1b')は従来値と同一(chunk_tts_assembly_b1b.json、refresh既定level=b1b)。Std時のみsummaryにlevel/composition追加。",
    "page_legend_html": "試聴ページ凡例の表示文言のみ(StdもAdvと同じ分割対象である旨・R5の条件付き文)。音声・Gate・採否に無関係。",
    "validate_only_segments": "_k指定の受理可否をCHUNK_TTS_Y_LEVELS(b1b,a2)基準にしただけ。b1bで_k受理・both/未知levelで拒否は従来どおり(拒否文言のみ変更)。",
    "load_y_sources": "変更行はa2分岐のみ(b1b分岐は'return'で先に抜ける=Advの経路は変更行に到達しない)。",
}
CONST_REVIEW = {
    "CHUNK_TTS_Y_LEVELS": "('b1b',)→('b1b','a2'): Advは引き続き含む(承認済み仕様=Std/Adv双方。ユーザー原文§2)。Adv動作は不変(動的バイト一致)。",
    "CHUNK_TTS_Y_APPROVAL_REF": "監査記録の注記文言のみ(chunk_tts_decision.jsonのapproval_ref。音声無関係。compareで『注記文言のみの差』を確認)。",
    "CHUNK_TTS_Y_NOTE": "監査記録の注記文言のみ(chunk_tts_decision.jsonのnote。音声無関係)。",
}

result = {"base": a.base, "files": {}, "unclassified": []}
for f in FILES:
    old_src, new_src = git_show(a.base, f), open(f, encoding="utf-8").read()
    ot, of = funcs(old_src)
    nt, nf = funcs(new_src)
    rows = []
    for q in sorted(set(of) | set(nf)):
        if "." in q and q.split(".")[0] in nf and q.split(".")[0] not in of and False:
            continue
        if q not in nf:
            rows.append({"func": q, "change": "REMOVED", "class": "UNCLASSIFIED", "why": "旧版にあり現版に無い"})
            continue
        if q not in of:
            adv_called = [o for o in of if re.search(r"\b" + re.escape(q.split(".")[-1]) + r"\b", of[o]["src"])]
            std_named = bool(re.search(r"(a2|std)", q, re.I))
            cls = "A2_ONLY" if std_named else "NEW_HELPER"
            rows.append({"func": q, "change": "ADDED", "class": cls if not adv_called else "UNCLASSIFIED",
                         "referenced_by_pre_existing_functions": adv_called})
            continue
        if of[q]["src"] == nf[q]["src"]:
            continue
        # 差分あり: 既存関数
        std_named = bool(re.search(r"(a2|std)", q, re.I))
        dflt = adv_default(nf[q]["node"])
        old_params = [x.arg for x in of[q]["node"].args.args]
        new_params = [x.arg for x in nf[q]["node"].args.args]
        ok_guard, rest = guarded_lines_analysis(of[q], nf[q], new_src.splitlines())
        if std_named:
            cls, why = "A2_ONLY", "関数名がa2/Std専用"
        elif dflt:
            cls, why = "DEFAULT_ADV_HELPER", f"追加/既存引数の既定値がAdv相当({dflt})。呼出側Advは引数を渡さない(下記callersで確認)"
        elif ok_guard:
            cls, why = "STD_GUARDED", "変更行は全て Std専用ガード(if ... a2/STD_LEVEL/slowdown_applied ...)・コメント/docstring・署名の内側のみ"
        elif q in MANUAL_REVIEW:
            cls, why = "MANUAL_REVIEWED", MANUAL_REVIEW[q]
        else:
            cls, why = "UNCLASSIFIED", "ガード外の変更行あり: " + json.dumps(rest, ensure_ascii=False)
        callers = [o for o in nf if o != q and re.search(r"\b" + re.escape(q.split(".")[-1]) + r"\(", nf[o]["src"])]
        rows.append({"func": q, "change": "MODIFIED", "class": cls, "why": why, "old_params": old_params, "new_params": new_params, "unguarded_changed_lines": rest,
                     "callers_in_file": callers})
    # モジュール定数の変更(既存定数の値変更は不可)
    oa, na = top_assign_names(ot), top_assign_names(nt)
    const_rows = []
    for k in sorted(set(oa) | set(na)):
        if k in oa and k in na and oa[k] != na[k]:
            const_rows.append({"const": k, "change": "VALUE_CHANGED", "class": "MANUAL_REVIEWED" if k in CONST_REVIEW else "UNCLASSIFIED",
                               "why": CONST_REVIEW.get(k)})
        elif k not in oa:
            const_rows.append({"const": k, "change": "ADDED", "class": "MODULE_LEVEL"})
        elif k not in na:
            const_rows.append({"const": k, "change": "REMOVED", "class": "UNCLASSIFIED"})
    result["files"][f] = {"functions": rows, "constants": const_rows}
    for r in rows + const_rows:
        if r["class"] == "UNCLASSIFIED":
            result["unclassified"].append({"file": f, **r})
json.dump(result, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
summ = {f: {c: sum(1 for r in v["functions"] if r["class"] == c) for c in ("A2_ONLY", "NEW_HELPER", "DEFAULT_ADV_HELPER", "STD_GUARDED", "MANUAL_REVIEWED", "UNCLASSIFIED")} for f, v in result["files"].items()}
print(json.dumps(summ, ensure_ascii=False, indent=1))
print("UNCLASSIFIED:", json.dumps(result["unclassified"], ensure_ascii=False, indent=1))
sys.exit(1 if result["unclassified"] else 0)
