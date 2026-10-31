"""Trial専用(API 0)。委任_05: COMPARISON_05.md の付録(B: N5配線後Production実run参考 / C: N5外の表現)を ev05/appendix_05.md に生成する。PYTHONUTF8=1で実行。"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import io, contextlib
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    import n5r_cmp_05 as C
import n5r_lib_02 as L
EV5 = C.EV5
outside = json.load(open(f"{EV5}/outside_05.json", encoding="utf-8"))
m10 = json.load(open(f"{EV5}/m10_reference_05.json", encoding="utf-8"))
md = []

md.append("## 付録B: N5配線後のProduction実run(参考。同一本文、`KP-GENERALIZATION-N5-PRODUCTION-WIRING-01` M10、ev02/ev03)の phrase kind 最終候補\n")
md.append("Production全工程(call1のP7＋B1 pool→SEL→pick cap7→GEN5/VER5/CHK5→救済→canonicalization QA→backfill)を通した実出力。比較の主表(Trial03のN5出力)とは別のB1抽出drawなので、**現行N5自体の実行間のばらつき**を示す。`origin=backfill`は補完工程で後から入った候補。\n")
md.append("| run | 選定phrase → used_form | 日本語 | origin |\n|---|---|---|---|")
for k, v in m10.items():
    if k.endswith("_dropped"):
        continue
    for x in v:
        md.append(f"| {k} | `{x['selection_phrase']}` → `{x['used_form']}` | {x['japanese_gloss']} | {x['origin']} |")
md.append("")
md.append("同runで落ちた候補(段・理由): ")
for k, v in m10.items():
    if k.endswith("_dropped"):
        md.append(f"- {k[:-8]}: " + " / ".join(f"`{x['phrase']}`({x['stage']})" for x in v))
md.append("")

# ---- 付録C: N5外 ----
CAND = [
    ("untidi_b1b", "gets heated", "高", "議論が白熱するという会話・ニュースで頻出のcollocation。cap10では0/13repで入らない(現行N5のTrial03出力には入っている)。Production実runではcanonicalization QA再判定key不一致で落ちていた(OPEN-633で是正済み)"),
    ("untidi_b1b", "In other words", "中", "談話標識。汎用性は高いが基礎的でSELはeasy判定。cap10では0/13rep"),
    ("untidi_b1b", "No wonder", "中", "会話表現として有用。cap10では0/13rep"),
    ("untidi_b1b", "in a way", "中", "『ある意味では』。基礎的な固定表現。cap10では0/13rep"),
    ("untidi_b1b", "on the job", "中", "『勤務中』。cap10では0/13rep(現行N5は`still on the job`を選定する回がある)"),
    ("untidi_b1b", "taking its job quite seriously", "中", "take something seriouslyの形で汎用。5語で本文形が長い"),
    ("untidi_a2", "Not so fast", "高", "会話の制止表現。cap10入りは1/11rep(現行N5のTrial03出力には入っている)"),
    ("untidi_a2", "take up space", "中", "場所を取るという汎用句動詞的表現。cap10入りは2/11rep"),
    ("untidi_a2", "No wonder", "中", "cap10入りは0/11rep"),
    ("untidi_a2", "In a way", "中", "cap10入りは3/11rep"),
    ("untidi_a2", "in sight", "中", "見える範囲にある。cap10入りは0/11rep(b1bでは12/13rep)"),
    ("untidi_a2", "leave it out", "中", "leave out系。cap10入りは0/11rep(b1bでは9/13rep)。記事主題の核(`Leaving Things Out`)に近い"),
    ("melos_a2", "waited for a reply", "低", "wait for。基礎語の自由な組合せに近い"),
    ("melos_a2", "blocked his way", "中", "block someone's way。cap10入り0/2rep"),
    ("melos_a2", "turned around", "低", "turn around。基礎的な句動詞"),
    ("melos_a2", "kept his eyes on them", "中", "keep one's eye on。現行N5のTrial03出力には入っている"),
    ("melos_a2", "For once", "中", "『今回に限って』。固定表現。cap10入り0/2rep"),
    ("moon_b1b", "In other words", "中", "談話標識。cap10入り0/2rep"),
    ("moon_b1b", "no need for", "中", "no need for something。cap10入り0/2rep"),
    ("moon_b1b", "For now", "中", "『当面は』。cap10入り0/2rep"),
    ("moon_b1b", "quite a lot of", "低", "量の基礎表現"),
    ("moon_b1b", "too soon to say", "中", "『まだ何とも言えない』。記事の論調に関わる表現。cap10入り0/2rep"),
    ("surname_b1b", "got married", "低", "get married。基礎的"),
    ("surname_b1b", "again and again", "中", "繰り返しを表す固定表現。cap10入り0/2rep"),
    ("surname_b1b", "got very upset", "低", "get upset。基礎的"),
    ("surname_b1b", "without getting too close", "低", "VER5でrevertされ汎用形にならず、日本語訳も`without`を反映しない(『深入りしすぎる』)"),
    ("surname_b1b", "decide for themselves", "高", "decide for oneself。A案cap10に入った回でGEN5が`oneself`再帰形のlemma不一致で組立失敗(QA脱落)。現行N5でも同じGEN5で同様に落ちる"),
    ("surname_b1b", "get much time to myself", "中", "time to oneself。同様にGEN5組立失敗(QA脱落)"),
]
md.append("## 付録C: N5(現行cap7・A案cap10)から外れた表現の実測(display_formはGEN5→VER5→CHK5の実出力)\n")
md.append("「pool/keep/cap10」=E2プールに出現したrep数 / SEL keepだったrep数 / A10 cap10に入ったrep数。価値は担当者の暫定評価。\n")
md.append("| 記事 | source_span | display_form (GEN5出力) | 日本語の意味 | pool/keep/cap10 (rep数) | SEL多数ラベル | 価値(暫定)と所見 |\n|---|---|---|---|---|---|---|")
for case, sp, rt, note in CAND:
    rows = outside[case]["rows"]; N = outside[case]["n_reps"]
    k = L.norm_key(sp)
    r = next((x for x in rows if L.norm_key(x["span"]) == k), None)
    g = C.gen_of(case, sp)
    if g and g["outcome"] == "kept":
        df = f"`{g['display_form']}`" + (f" [{g.get('relation')}]" if g.get("relation") not in (None, "SAME") else ""); gl = g["gloss_ja"]
    elif g:
        df = f"(脱落 {C.drop_reason(g)})"; gl = "—"
    else:
        df = "(GEN未処理)"; gl = "—"
    st = f"{r['n_pool']}/{r['n_keep']}/{r['n_in_cap10']} (N={N})" if r else "—"
    lab = max(r["labels"], key=r["labels"].get) if r else "—"
    md.append(f"| {case} | `{sp}` | {df} | {gl} | {st} | {lab} | {rt}: {note} |")
md.append("")
open(f"{EV5}/appendix_05.md", "w", encoding="utf-8").write("\n".join(md))
print("ok", len(md))
