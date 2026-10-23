# ============================================================
# er109_wiring_golden_build_01.py  (API 0 / 費用0)
# ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01 委任_04: 常設golden回帰test(er109_wiring_golden_test_01.py)の入力rowsを作る再現スクリプト。
# golden rows = (1) WIRING_DESIGN_03 §C-4表+決定的ケース(合成) (2) stored_onoff_compare_02.json の NG->PASS 19行(X10+A/B/C相当9)
#               (3) 配線後のX scopeで署名が変わった行(NG->PASS/NG->NG/guard) (4) 各経路の代表行(seed固定のランダム標本: 本文/KP/Azure転写あり/pairs/JA)。
# 配線前HEAD(baseline)でこのrowsの署名を採って fixture に固定する(golden_signatures_pre_wiring_*.jsonl.gz)。
# 使い方: python er109_wiring_golden_build_01.py --all-rows rows.jsonl --changed-keys changed.json --out golden_rows_01.jsonl
#   (all-rows = er109_wiring_signature_01.py --build-rows の出力。changed-keys = 配線後X scopeで署名が変わった行id一覧[json list])
# ============================================================
import argparse
import json
import random
import re

JA = re.compile(r"[぀-ヿ㐀-䶿一-鿿]")

SYNTHETIC = [
    # (canonical, asr, azure, kp, 説明) -- WIRING_DESIGN_03 §C-4 + Opus G3
    ("Pump one's fist.", "Pump 1's fist.", None, False, "C4: one's<->1's"),
    ("I said no.", "I said know.", None, False, "C4: no<->know(PASS_WITH_WARNING)"),
    ("We have two cats.", "We have one cats.", None, False, "C4: 実数値差NG"),
    ("I did not go.", "I did go.", None, False, "C4: not脱落NG"),
    ("I can't go.", "I can go.", None, False, "C4: can't<->can NG"),
    ("I don't know.", "I do know.", None, False, "don't<->do NG"),
    ("He is lead.", "He is led.", None, False, "C4: 同形異音語"),
    ("Take part in it.", "Take apart in it.", None, False, "C4: Take part<->apart NG"),
    ("Visit St. John.", "Visit Street John.", None, False, "St.<->Street(既存層で合格)"),
    ("Point to the map.", "Point 2. the map.", None, False, "C4: Point to<->Point 2. (AMBIGUOUS)"),
    ("Pump one's fist twice, 3 times.", "Pump 1's fist twice, 4 times.", None, False, "one's->1's + 別の実数値差 NG"),
    ("I said no and did not go.", "I said know and did go.", None, False, "否定語がspan内外にまたがるNG"),
    ("I said no.", "I sed no.", "I said know.", False, "Secondary ortho(否定差解除)"),
    ("Pump one's fist.", "Pump a fist.", "Pump 1's fist.", False, "Secondary ortho(値差解除)"),
    ("We have two cats.", "We have tu cats.", "We have one cats.", False, "Secondary 実数値差NG"),
    ("Point to the map.", "Pint to the map.", "Point 2. the map.", False, "Secondary AMBIGUOUS"),
    ("Pump one's fist", "Pump 1's fist", "Pump one's fist", True, "KP: P ortho + S"),
    ("I said no", "I said know", "I said no", True, "KP: P ortho(警告)+S"),
    ("I said no", "I said know", "I said know", True, "KP: P,S ortho"),
    ("I said no", "I said no", "I said know", True, "KP: S ortho"),
    ("I said no", "I sed no", "I said no", True, "KP: S+W(Wはasr転写を再利用=ここではP NG)"),
    ("twenty percent of them", "20% of them", None, False, "既存経路(NUMERIC等)を維持"),
    ("one thousand two hundred", "1,200", None, False, "数の読み"),
    ("They looked at three nearby neighborhoods.", "They looked at 3:00 nearby neighborhoods.", None, False, "3:00 の読み(観察事項)"),
]

# ②英米綴り(UKUS、ASR-QUALITY-2ITEMS 委任_04, OF-UKUS-W-05): 既存golden rows(g0000-g0297)は一切変えず、末尾へ追記する合成行(id g0298〜)。
# (canonical, asr, azure, kp, 説明)。新行のpre署名だけ配線前commit overlay(b7b6d07d8)で採る(manifest.pre_wiring_commit・既存行は不変)。
SYNTHETIC_UKUS = [
    ("Inventing convincing stories at a moment's notice was Vera's speciality.", "Inventing convincing stories at a moment's notice was Vera's specialty.", None, False, "UKUS: c12 speciality/specialty Primary"),
    ("Inventing convincing stories at a moment's notice was Vera's speciality.", "Inventing convincing stories at a moment's notice was Vera's forte.",
     "Inventing convincing stories at a moment's notice was Vera's specialty.", False, "UKUS: c12 Secondary(Azure)がspecialty"),
    ("Her speciality", "Her specialty", "Her speciality", True, "UKUS: KP P ortho(UKUS)+S"),
    ("Her speciality", "Her specialty", "Her specialty", True, "UKUS: KP P,S ortho(UKUS)"),
    ("The colour of the neighbour's jewellery was bright.", "The color of the neighbor's jewelry was bright.", None, False, "UKUS: colour/neighbour's/jewellery 複数位置"),
    ("The tire is flat.", "The tyre is flat.", None, False, "UKUS: AMB逆方向(US形->UK形)NG維持"),
    ("The tyre is flat.", "The tire is flat.", None, False, "UKUS: AMB UK形->US形 PASS"),
    ("He visited Aluminium City last year.", "He visited Aluminum City last year.", None, False, "UKUS負例: 固有名詞(文中大文字)NG維持"),
    ("The speciality is cooking.", "The specialty is cooling.", None, False, "UKUS負例: 綴り差+実誤読 NG"),
    ("The speciality costs 3 pounds.", "The specialty costs 4 pounds.", None, False, "UKUS負例: 綴り差+実数値差 NG"),
    ("He did not like the colour.", "He did like the color.", None, False, "UKUS負例: 綴り差+not脱落 NG"),
    ("Mum said hello to us.", "Mom said hello to us.", None, False, "UKUS負例: mum/mom除外 NG"),
    ("Their speciality was fine at the time.", "There specialty was fine at the time.", None, False, "UKUS: 既存rule(their/there)隣接のn:n span内位置別救済"),
    ("Her jewellery-making kit arrived.", "Her jewelry making kit arrived.", None, False, "UKUS負例: 語数違いspan(ハイフン複合<->分かち書き)NG維持"),
]


def append_ukus(existing_path, out_path):
    """既存golden rows(byte不変)の末尾へSYNTHETIC_UKUSを追記(id連番を継続)。"""
    lines = [l for l in open(existing_path, encoding="utf-8", newline="").read().split("\n") if l.strip()]
    n = len(lines)
    for i, (c, asr, az, kp, why) in enumerate(SYNTHETIC_UKUS):
        lines.append(json.dumps({"id": f"g{n + i:04d}", "canonical": c, "asr": asr, "azure": az, "seg": ("full_story_part1" if not kp else None), "kp": kp, "why": why},
                                ensure_ascii=False, sort_keys=True))
    with open(out_path, "w", encoding="utf-8", newline="\n") as fo:
        fo.write("\n".join(lines) + "\n")
    print(f"golden rows={len(lines)} (appended {len(SYNTHETIC_UKUS)})")


def main():
    import sys
    if len(sys.argv) == 4 and sys.argv[1] == "--append-ukus":      # python er109_wiring_golden_build_01.py --append-ukus EXISTING_ROWS OUT
        append_ukus(sys.argv[2], sys.argv[3])
        return
    ap = argparse.ArgumentParser()
    ap.add_argument("--all-rows", required=True)
    ap.add_argument("--changed-keys", required=True)
    ap.add_argument("--stored-onoff", default="docs/research/ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01/stored_onoff_compare_02.json")
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=109)
    ap.add_argument("--n-sample", type=int, default=160)
    a = ap.parse_args()
    rows = [json.loads(l) for l in open(a.all_rows, encoding="utf-8") if l.strip()]
    by_id = {r["id"]: r for r in rows}
    out, seen = [], set()

    def add(r, why):
        key = (r["canonical"], r["asr"], r.get("azure"), r.get("seg"), bool(r.get("kp")))
        if key in seen:
            return
        seen.add(key)
        out.append({"id": f"g{len(out):04d}", "canonical": r["canonical"], "asr": r["asr"], "azure": r.get("azure"), "seg": r.get("seg"),
                    "kp": bool(r.get("kp")), "why": why})

    for c, asr, az, kp, why in SYNTHETIC:
        add({"canonical": c, "asr": asr, "azure": az, "seg": ("full_story_part1" if not kp else None), "kp": kp}, why)
    d = json.load(open(a.stored_onoff, encoding="utf-8"))
    ng2pass = {(x["c"], x["a"]) for x in d["NG_to_PASS"]}
    for r in rows:
        if (r["canonical"], r["asr"]) in ng2pass:
            add(r, "stored_onoff_compare_02 NG_to_PASS 19行")
    for rid in json.load(open(a.changed_keys, encoding="utf-8")):
        if rid in by_id:
            add(by_id[rid], "配線後X scopeで署名が変わった行")
    rnd = random.Random(a.seed)
    stored = [r for r in rows if r["id"].startswith("st") and not JA.search(r["canonical"])]
    kps = [r for r in stored if r.get("kp")]
    azs = [r for r in stored if r.get("azure")]
    pairs = [r for r in rows if r["id"].startswith("pair") and not JA.search(r["canonical"])]
    ja = [r for r in rows if JA.search(r["canonical"])]
    for pool, n, why in ((stored, a.n_sample // 4, "代表: 保存本文segment"), (kps, a.n_sample // 4, "代表: KP"), (azs, a.n_sample // 4, "代表: Azure転写あり"),
                         (pairs, a.n_sample // 4, "代表: pairs_02"), (ja, 16, "代表: 日本語(ortho対象外)")):
        for r in rnd.sample(pool, min(n, len(pool))):
            add(r, why)
    with open(a.out, "w", encoding="utf-8", newline="\n") as fo:
        for r in out:
            fo.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")
    print(f"golden rows={len(out)}")


if __name__ == "__main__":
    main()
