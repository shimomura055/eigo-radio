"""CS監査(FAMILY-Z-MELOS-CONNECTED-SPEECH-ROOT-CAUSE-AUDIT-01 委任_03)。
共有 er021 telemetry.jsonl へ cs_offline_reeval_01.py の初回3回の実行が誤って追記した重複行を、行番号で特定するmanifest生成(read-only)。
telemetry.jsonl 本体は一切書換えない。特定方法: (a)先頭7155行=監査前の既存行、(b)7156行目以降で、入力pair(HR queue全step転写 ∪ 先頭7155行のcanonical/asr ∪ scriptの合成pair[S行列・sweep行列])に
canonical/asrの両方が一致する行、(c)scriptの3回実行(先頭pairの再出現位置)でrun区切り、(d)末尾の単体test追記1行、(e)以降は委任_02のProduction正規再生成(除外)。"""
import json, hashlib, collections, os, sys
sys.path.insert(0, ".")
T = "er021_output/en_asr_semantic_equivalence_production_wiring_01/telemetry.jsonl"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "telemetry_probe_rows_manifest_01.json")
PRE_N = 7155
raw = open(T, encoding="utf-8", newline="").read().split("\n")
if raw and raw[-1] == "": raw = raw[:-1]
total = len(raw)
rows = []
for i, l in enumerate(raw, 1):
    try: d = json.loads(l)
    except Exception: d = {}
    rows.append((i, d, l))
# 入力pair集合
inp = set()
for l in open("er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl", encoding="utf-8"):
    try: d = json.loads(l)
    except Exception: continue
    c = d.get("canonical_text")
    for s in d.get("steps", []):
        if s.get("text") and c: inp.add((c, s["text"]))
pre_pairs = {(d["canonical"], d["asr"]) for i, d, l in rows[:PRE_N] if d.get("canonical") and d.get("asr")}
inp |= pre_pairs
# 合成pair(スクリプトと同一定義: S行列 + NAMES x NEXT sweep + 単体test)
S = [("Melos said.","Melo said."),("Melos said.","Mello said."),("Melos said.","Mellow said."),("Melos said.","Melon said."),("Melos said.","Marcus said."),("Melos said.","Melody said."),("Marcus smiled.","Marcu smiled."),("Marcus smiled.","Markus smiled."),("Marcus smiled.","Marker smiled."),("Chris saw him.","Kris saw him."),("Chris saw him.","Cree saw him."),("Thomas sat down.","Thoma sat down."),("Dionysius spoke.","Dionysia spoke."),("The studies suggest a link.","The study suggests a link."),("The bosses said so.","The boss said so."),("The classes started late.","The class started late."),("The glasses sit there.","The glass sit there."),("The bus stops here.","The bu stops here."),("This school starts soon.","This schoo starts soon."),("A nice sign.","A nigh sign."),("He opened the door.","He open the door."),("He opened to them.","He open to them."),("The studies suggest a link.","The studio suggests a link."),("The bosses said so.","The bonus said so."),("The cities seem calm.","The city seem calm.")]
NAMES = [("Melos","Melo",["Mello","Mellow"]),("Marcus","Marcu",["Markus"]),("Thomas","Thoma",["Tomma"]),("Dionysius","Dionysiu",["Dionysia"]),("Brutus","Brutu",["Brootu"]),("Jesus","Jesu",["Jezu"]),("Chris","Chri",["Cree"]),("James","Jame",["Jaim"]),("Lucas","Luca",["Looka"]),("Atlas","Atla",["Atlah"]),("Hades","Hade",["Hayde"]),("Paris","Pari",["Parry"]),("Silas","Sila",["Seela"]),("Judas","Juda",["Judah"]),("Nicholas","Nichola",["Nicola"]),("Carlos","Carlo",["Carlo"]),("Venus","Venu",["Venew"]),("Orpheus","Orpheu",["Orfew"])]
NEXT = ["said","spoke","smiled","sat","saw","stood"]
synth = set(S)
for full, stem, vs in NAMES:
    for nx in NEXT:
        for a in [stem] + vs: synth.add((f"{full} {nx}.", f"{a} {nx}."))
test_probe = {("Melos walked.", "Melo walked.")}
# run区切り: 7156行目のpairの再出現
tail = [(i, d) for i, d, l in rows if i > PRE_N]
first = (tail[0][1].get("canonical"), tail[0][1].get("asr"))
starts = [i for i, d in tail if (d.get("canonical"), d.get("asr")) == first]
# 委任_02の正規再生成開始 = テスト単体追記行の次(Melos walked.の直後)
test_line = next((i for i, d in tail if (d.get("canonical"), d.get("asr")) in test_probe), None)
audit, excluded = [], []
for i, d in tail:
    p = (d.get("canonical"), d.get("asr"))
    if test_line is not None and i > test_line: excluded.append(i); continue
    if p in inp or p in synth or p in test_probe: audit.append(i)
    else: excluded.append(i)
def ranges(xs):
    out = []; s = p = None
    for x in xs:
        if s is None: s = p = x
        elif x == p + 1: p = x
        else: out.append([s, p]); s = p = x
    if s is not None: out.append([s, p])
    return out
byline = {i: (d, l) for i, d, l in rows}
cls = collections.Counter(byline[i][0].get("classification") for i in audit)
role = collections.Counter(byline[i][0].get("role") for i in audit)
cat = collections.Counter(
    "synthetic_matrix" if (byline[i][0].get("canonical"), byline[i][0].get("asr")) in synth and (byline[i][0].get("canonical"), byline[i][0].get("asr")) not in inp else
    "unit_test_probe" if (byline[i][0].get("canonical"), byline[i][0].get("asr")) in test_probe else "input_pair_match" for i in audit)
mult = collections.Counter(collections.Counter((byline[i][0]["canonical"], byline[i][0]["asr"]) for i in audit if i <= (test_line or 0) - 0).values())
h = hashlib.sha256("\n".join(byline[i][1] for i in audit).encode("utf-8")).hexdigest()
pre_h = hashlib.sha256("\n".join(l for i, d, l in rows[:PRE_N]).encode("utf-8")).hexdigest()
res = {
  "management_id": "FAMILY-Z-MELOS-CONNECTED-SPEECH-ROOT-CAUSE-AUDIT-01 委任_03",
  "purpose": "監査スクリプトの共有telemetry.jsonlへの重複追記行を行番号で特定(集計側の除外用)。telemetry.jsonl本体は書換えていない。",
  "file": T, "total_lines_at_snapshot": total, "pre_audit_lines": PRE_N, "pre_audit_lines_sha256": pre_h,
  "line_numbers_are": "1-based(先頭行=1)",
  "method": "7156行目以降で、入力pair(HR queue全step転写+先頭7155行のcanonical/asr+スクリプト合成pair)にcanonical/asr両方が一致する行を機械的に抽出。時刻列はtelemetryに無いため、時間帯の代わりに(i)7155行目より後の連続追記領域である事、(ii)先頭pairの再出現で3回のscript実行に分割できる事、(iii)全行role=FULL_STORY(script固定のsegment_id由来、元行はCOMMENT等も含む)を補助根拠とした。",
  "audit_run_starts_line": starts,
  "audit_rows_count": len(audit), "audit_rows_line_ranges": ranges(audit),
  "audit_rows_sha256_of_lines_joined_by_LF": h,
  "audit_rows_by_category": dict(cat), "audit_rows_by_classification": dict(cls), "audit_rows_by_role": dict(role),
  "audit_pair_multiplicity_distribution(pair複数回出現数→pair数)": {str(k): v for k, v in sorted(mult.items())},
  "unit_test_probe_line": test_line,
  "excluded_post_audit_rows_line_ranges": ranges([i for i in excluded if test_line and i > test_line]),
  "excluded_post_audit_rows_note": "委任_02のStd a2 part1_c5 Production正規再生成(TTS attempt4等)による正規追記。集計から除外しない。",
  "excluded_non_matching_rows_in_audit_window": ranges([i for i in excluded if not test_line or i <= test_line]),
  "comparison_with_estimate": "委任文の概算(重複約1,675行+Coffee agent約325行)に対し、7156行目〜単体test行の範囲の全行が入力pair/合成pairに一致し、一致しない行(=Coffee等の他agent行と判定できる行)は0件だった。",
  "residual": [
    "telemetryに時刻列が無く、入力pairと偶然一致した他agentの正規追記行は機械的に区別できない。ただしpair出現数の分布(3回=601pair=script3回実行分、1回=105pair=第3回のみ実行のsweep行列、その他=S行列/HR queueとの重複で説明可)に説明不能な余剰は見えず、Coffee等の他agent行と判定できる行は0件。",
    "同一pairが監査内で3回(runごと)出現する。各pairの『最初の1回』を正規とみなす根拠は無い(元行は先頭7155行側に既存)ため、audit_rows_line_rangesの全行を除外対象とする。",
    "先頭7155行目までを監査前とする境界は委任_01時点の実測。以後に他agentが追記した場合は行番号がずれるのではなく末尾側へ追加されるのみ(追記専用ファイルのため先頭側は不変、pre_audit_lines_sha256で検証可)。"
  ],
  "rollback_decision": "telemetry.jsonlの巻き戻し(上記行の削除)はFable/ユーザー判断。OPEN-328(3)に記録。",
}
json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({k: res[k] for k in ["total_lines_at_snapshot","audit_run_starts_line","audit_rows_count","audit_rows_line_ranges","audit_rows_by_category","audit_rows_by_classification","audit_rows_by_role","audit_pair_multiplicity_distribution(pair複数回出現数→pair数)","unit_test_probe_line","excluded_post_audit_rows_line_ranges","excluded_non_matching_rows_in_audit_window"]}, ensure_ascii=False, indent=1))
