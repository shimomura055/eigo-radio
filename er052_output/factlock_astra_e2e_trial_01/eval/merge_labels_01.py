# -*- coding: utf-8 -*-
"""FACTLOCK-ASTRA-E2E-TRIAL-01 委任_15: 3 worker のラベル(labels_w{1,2,3}.jsonl)を統合する。

入力(読み取りのみ。原本は編集しない): eval/labels_w1.jsonl, labels_w2.jsonl, labels_w3.jsonl
出力: eval/labels_merged.jsonl, eval/labels_merged_stats.json
API 呼出なし。

統合規則(EVAL_E2E_01.md 2節と同一)
1. 行は削除しない。全行に row_id(=w<worker>-<原本の行番号>)、label_source(原本のまま)、orig(原本行全体)を付ける。
2. 3 worker の担当テーマは重なっていない(下で検証し stats に記録)。したがって worker 間のラベル衝突はない。
3. スキーマが worker ごとに違う(w1=日本語label+英語severity、w2=label/severity同値の日本語、w3=Y/N+severity)ため、
   共通の正規化フィールドを足す: n_sev, n_boundary, n_body, n_shipped, claim_text。
   n_sev ∈ {重大, 軽微, 問題なし, 判断不能, 所見なし(要約・NO_FINDING・対象外)}。
   「境界」(worker が重大/軽微の境界と書いたもの)は n_sev を重大にも軽微にも動かさず n_boundary=True とする。
   境界行の n_sev は worker が付けた側(w1 の『重大(境界)』のみ 重大 だが n_boundary=True。それ以外は 軽微)。
4. 同じ claim の重複(Checker の文分割断片、cycle1/cycle2 の同一 claim、同じ文の複数行)を dup_group にまとめる。
   同一 (theme, arm, n_body) 内で、空白・引用符・末尾の … を除いた claim_text が
   (a) 一致する、または (b) 一方が他方の接頭辞で、短い方が25文字以上 のとき、同一グループ。
   グループ内の最長 claim_text の行を dup_primary=True、他は dup_of=<primary の row_id>。
   resolved_sev = グループ内の最大重大度(重大 > 軽微 > 判断不能 > 問題なし > 所見なし)。
   グループ内で n_sev が食い違った場合は dup_conflict=True(食い違いを隠さない)。
   dup_group の対象は『同じ claim を指す行』だけ。別 claim・別 stage の行は統合しない。
5. 最終本文に残る軽微の件数(判定線 2-2)は、この jsonl から自動では出さない。worker が『最終本文の残存』として
   列挙した項目を judge_table_01.py の FINAL_MINOR_ITEMS に row_id 付きで手で写している(根拠の追跡のため)。
6. 確認欄: confirmed_by(Fable が記入。ここでは None)、qa_note(統合時に見つけた原本の不整合メモ)。
"""
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
SEV_RANK = {"重大": 4, "軽微": 3, "判断不能": 2, "問題なし": 1, "所見なし": 0}


def load(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if line:
                rows.append((i, json.loads(line)))
    return rows


def norm_sev(w, r):
    lab = str(r.get("label", ""))
    sev = str(r.get("severity", ""))
    boundary = False
    if "境界" in lab or "boundary" in sev or "境界" in sev or r.get("borderline_to") or r.get("borderline"):
        boundary = True
    if w == 1:
        if lab == "NO_FINDING":
            return "所見なし", boundary
        if lab.startswith("重大"):
            return "重大", True
        if lab.startswith("軽微"):
            return "軽微", boundary
        if lab == "問題なし":
            return "問題なし", False
    elif w == 2:
        if lab == "-":
            return "所見なし", False
        if lab == "軽微":
            return "軽微", boundary
        if lab == "問題なし":
            return "問題なし", False
    else:
        if lab == "Y":
            return "軽微" if sev == "軽微" else "重大", boundary
        if lab == "N":
            return "問題なし", False
        if lab == "UNDECIDABLE":
            return "判断不能", False
    return "所見なし", boundary


def norm_body(w, r):
    s = f"{r.get('level', '')} {r.get('stage', '')}"
    su = s.upper()
    if "CHECKER" in su or "チェッカー" in s:
        if "ADV" in su:
            return "Checker-Adv"
        if "STD" in su or "STANDARD" in su:
            return "Checker-Std"
        return "Checker"
    if su.startswith("JA") or "JA_FINAL" in su:
        return "JA"
    if "EN_ADV" in su or "EN-ADV" in su or "EN_FINAL-ADV" in su:
        return "EN-Adv"
    if "EN_STD" in su or "EN-STANDARD" in su or "EN_FINAL-STANDARD" in su:
        return "EN-Std"
    lvl = str(r.get("level", ""))
    if lvl.startswith("FINAL_TRACE"):
        st = str(r.get("stage", ""))
        if "ADV" in st.upper():
            return "EN-Adv"
        if "STD" in st.upper():
            return "EN-Std"
    if lvl.startswith("EN"):
        return "EN"
    return "他"


def claim_of(w, r):
    return str(r.get("claim") if w in (1, 2) else r.get("claim_id", ""))


def shipped_of(r):
    if r.get("shipped") is False:
        return False
    s = f"{r.get('level', '')} {r.get('stage', '')}"
    if "rejected" in s.lower() or "UNSHIPPED" in s or "ship" in s and "されず" in s:
        return False
    if r.get("shipped") is True:
        return True
    return None


def key_text(t):
    t = re.sub(r"[\s　]+", " ", t)
    t = t.replace("“", '"').replace("”", '"').replace("’", "'").replace("‘", "'").replace("…", "").strip()
    return t


def main():
    merged = []
    theme_sets = {}
    for w in (1, 2, 3):
        rows = load(os.path.join(BASE, f"labels_w{w}.jsonl"))
        theme_sets[w] = sorted({r["theme"] for _, r in rows})
        for ln, r in rows:
            sev, bd = norm_sev(w, r)
            m = {
                "row_id": f"w{w}-{ln}",
                "worker": w,
                "theme": r["theme"],
                "arm": r["arm"],
                "n_body": norm_body(w, r),
                "n_sev": sev,
                "n_boundary": bool(bd),
                "n_shipped": shipped_of(r),
                "claim_text": claim_of(w, r),
                "label_source": r.get("label_source", f"sonnet_w{w}"),
                "confirmed_by": None,
                "qa_note": None,
                "orig": r,
            }
            merged.append(m)

    # worker 間のテーマ重複検査
    overlap = []
    for a in (1, 2, 3):
        for b in (1, 2, 3):
            if a < b:
                x = set(theme_sets[a]) & set(theme_sets[b])
                if x:
                    overlap.append((a, b, sorted(x)))

    # 重複グループ化(同一 theme/arm/n_body 内)
    groups = {}
    for m in merged:
        groups.setdefault((m["theme"], m["arm"], m["n_body"]), []).append(m)
    gid = 0
    n_dup_groups = 0
    n_conflict = 0
    for k, ms in groups.items():
        parent = list(range(len(ms)))

        def find(i):
            while parent[i] != i:
                parent[i] = parent[parent[i]]
                i = parent[i]
            return i

        keys = [key_text(m["claim_text"]) for m in ms]
        for i in range(len(ms)):
            for j in range(i + 1, len(ms)):
                a, b = keys[i], keys[j]
                if not a or not b:
                    continue
                s, l = (a, b) if len(a) <= len(b) else (b, a)
                if a == b or (len(s) >= 25 and l.startswith(s)):
                    parent[find(i)] = find(j)
        comp = {}
        for i in range(len(ms)):
            comp.setdefault(find(i), []).append(i)
        for idxs in comp.values():
            gid += 1
            gm = [ms[i] for i in idxs]
            prim = max(gm, key=lambda m: len(key_text(m["claim_text"])))
            top = max(gm, key=lambda m: SEV_RANK[m["n_sev"]])["n_sev"]
            conflict = len({m["n_sev"] for m in gm}) > 1
            for m in gm:
                m["dup_group"] = f"g{gid}" if len(gm) > 1 else None
                m["dup_primary"] = (m is prim) if len(gm) > 1 else True
                m["dup_of"] = prim["row_id"] if (len(gm) > 1 and m is not prim) else None
                m["resolved_sev"] = top
                m["dup_conflict"] = conflict
            if len(gm) > 1:
                n_dup_groups += 1
                if conflict:
                    n_conflict += 1

    # 統合時に見つけた原本の不整合メモ(根拠は EVAL_E2E_01.md 3-4節)
    for m in merged:
        o = m["orig"]
        txt = " ".join(str(o.get(k, "")) for k in ("level", "stage", "claim", "claim_id", "evidence"))
        if (m["worker"] == 2 and m["theme"] == "byd_recall" and m["arm"] == "new"
                and "Standard" in str(o.get("level", "")) and "M1" in txt
                and ("発火" in txt or "M1後" in txt)):
            m["qa_note"] = ("M1発火と記載されているが、runログ(new_en_std.log)は『must-fixで1回再生成』のみ。"
                            "REPORT §110: M1はAdvanced枝のみ(Standard未実装)。M1発火の帰属はEVAL 3-4で不一致として扱う。")
    # v2(委任_16、Opusレビュー論点4): 『不在・非公開の断定』を同じ基準(OC-8)にそろえる統合時メモ(原本ラベルは変更しない)。
    # semiconductor新のEN Adv STOP文(w3が『問題なし』=偽陽性)と space_weapons 両腕の不在断定(w1が『軽微』、確信0.5)は同型である。
    # 現ラベルは worker ごとの判断で食い違っており、基準が確定するまで『同型・同基準待ち』として扱う(ラベル値はそのまま)。
    OC8_NOTE = ("OC-8 同型メモ(委任_16): 台帳が『補わない』『確認していない』と指示しただけの事柄を本文が『示されていない/秘密/説明がない』と"
                "不在・非公開として断定する型。semiconductor新EN Adv(w3-90/92: 問題なし=偽陽性)とspace_weapons両腕(w1-49,76,61,62,73,75: 軽微、"
                "確信0.5)は同型で、ラベルが分かれている。基準(OC-8)が確定するまで同じ基準で扱う。原本ラベルは不変。")
    OC8_ROWS = {"w3-90", "w3-92", "w1-49", "w1-76", "w1-61", "w1-62", "w1-73", "w1-75"}
    for m in merged:
        if m["row_id"] in OC8_ROWS:
            m["qa_note"] = (m["qa_note"] + " / " if m.get("qa_note") else "") + OC8_NOTE
    merged.sort(key=lambda m: (m["worker"], int(m["row_id"].split("-")[1])))

    out = os.path.join(BASE, "labels_merged.jsonl")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        for m in merged:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")

    from collections import Counter
    stats = {
        "n_rows": len(merged),
        "rows_per_worker": dict(Counter(m["worker"] for m in merged)),
        "themes_per_worker": theme_sets,
        "worker_theme_overlap": overlap,
        "n_dup_groups": n_dup_groups,
        "n_dup_groups_with_sev_conflict": n_conflict,
        "n_sev": dict(Counter(m["n_sev"] for m in merged)),
        "n_boundary_rows": sum(1 for m in merged if m["n_boundary"]),
        "n_body": dict(Counter(m["n_body"] for m in merged)),
        "label_source": dict(Counter(m["label_source"] for m in merged)),
        "unique_rows_after_dedup": sum(1 for m in merged if m["dup_primary"]),
    }
    with open(os.path.join(BASE, "labels_merged_stats.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    if overlap:
        print("WARNING: worker間のテーマ重複あり", overlap)
        sys.exit(1)


if __name__ == "__main__":
    main()
