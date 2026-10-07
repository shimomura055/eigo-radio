# -*- coding: utf-8 -*-
"""STAGE2-01 測定(3)補助: ON/OFFで実際に変わった文(前後)を全件列挙し、主体・極性・数値の変化を決定論で付記する(目視確認用)。API無し。出力: eval/stage3_changes.md"""
import difflib
import glob
import json
import pathlib
import re

import replay_lib as L

OUT, cap2 = L.OUT, L.cap2
SENT = re.compile(r"(?<=[.!?])\s+")


def sents(md):
    out = []
    for p in re.split(r"\n\s*\n", md.strip()):
        p = p.strip()
        if p.startswith("#"):
            out.append(p)
            continue
        out += [s.strip() for s in SENT.split(p) if s.strip()]
    return out


def changed_pairs(before, after):
    sb, sa = sents(before), sents(after)
    sm = difflib.SequenceMatcher(None, sb, sa)
    res = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag != "equal":
            res.append((" ".join(sb[i1:i2]), " ".join(sa[j1:j2]), tag))
    return res


def main():
    tg = json.loads((OUT / "eval" / "stage3_targets.json").read_text(encoding="utf-8"))
    lines = ["# 構造要素Rewriteの実出力(ON=新規則 / OFF=現行相当)と決定論の変化検出", "",
             "各行: 前→後。`flags`は4照合(主体=新規の主体・代名詞、極性=否定語の有無、数値、形式)の違反。目視で意味の変化を確認すること。", ""]
    n_changes, n_flag = {"on": 0, "off": 0}, {"on": 0, "off": 0}
    for t in tg:
        run, ledger, art = L.load_run(t["run"])
        vocab = cap2.proper_noun_vocab(ledger, art)
        lines.append(f"## 対象{t['i']} {t['run'].split('runs/')[-1]} [{t['section_type']}] {t['source']}")
        lines.append(f"- claim: {t['claim'][:110]}")
        for rep in range(3):
            for on in (True, False):
                f = OUT / "replay_dev" / "stage3_rewrite" / f"t{t['i']}_r{rep}_{'on' if on else 'off'}.json"
                if not f.exists():
                    continue
                d = json.loads(f.read_text(encoding="utf-8"))
                tag = "ON" if on else "OFF"
                if not d["guard_ok"]:
                    lines.append(f"- rep{rep} {tag}: 書換え無し(ladder枯渇=構造要素STOP経路、元のまま) regen={(d.get('structural_rules') or {}).get('regen_calls')}")
                    continue
                for b, a, op in changed_pairs(art, d["updated_text"]):
                    kind = "title" if b.lstrip().startswith("#") else "hook"
                    c = cap2.four_checks(kind, b, a, vocab, art)
                    n_changes["on" if on else "off"] += 1
                    n_flag["on" if on else "off"] += 0 if c["ok"] else 1
                    lines.append(f"- rep{rep} {tag} [{op}] flags={c['violations'] or '-'} new_subjects={c['new_subjects'] or '-'}")
                    lines.append(f"    前: {b[:300]}")
                    lines.append(f"    後: {a[:300]}")
        lines.append("")
    lines.insert(2, f"集計(対象文の変更単位): ON変更{n_changes['on']}件・うち4照合違反{n_flag['on']} / OFF変更{n_changes['off']}件・うち4照合違反{n_flag['off']}")
    (OUT / "eval" / "stage3_changes.md").write_text("\n".join(lines), encoding="utf-8")
    print(n_changes, n_flag)


if __name__ == "__main__":
    main()
