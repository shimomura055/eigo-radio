# -*- coding: utf-8 -*-
"""aggregate_02.py -- 委任_21: 改善R0 run_02a/run_02b と 旧R0(run_01)の決定論集計(ローカル正規表現のみ。API 0)と、EVAL_SET_02.md / BLIND_KEY_02.json / structure_metrics_02.json の生成。
指標の正規表現は本ファイルで固定し、結果を見て調整していない(1回実行)。合否には使わない(記録専用)。構造タグ(冒頭型・結び型)は各runに記録済みのluna判定。"""
import json
import random
import re
import sys

sys.path.insert(0, ".")
import er110_family_y_opinion_based_01 as ob
import er110_family_y_opinion_based_02 as ob2

OUT = "docs/research/FAMILY-Y-VOICES-DESIGN-01/OPINION_BASED_01"
RUNS = {"旧R0(run_01)": "er110_output/family_y_opinion_based_01/sns_age_limit/run_01",
        "run_02a": "er110_output/family_y_opinion_based_02/sns_age_limit/run_02a",
        "run_02b": "er110_output/family_y_opinion_based_02/sns_age_limit/run_02b"}
SLOTS = ob.SLOTS
SEED = 20261024
OLD = "旧R0(run_01)"

MONITOR_RE = re.compile(r"(見られ|見張|監視|のぞか|のぞい|チェックされ|見せる|見せなきゃ|見せなく|見守)")
BEKI_RE = re.compile(r"べき")
INSTITUTION_RE = re.compile(r"(制度|法律|法的|国が|国で|規制|規則|仕組み|機能設計|本人確認|プラットフォーム|事業者|企業|運営|ルール作り|ルールを作)")
CONCERN_RE = re.compile(r"(心配|不安|気がかり|困る|困った|嫌|怖い|しんどい|イライラ)")
WISH_RE = re.compile(r"(ほしい|欲しい|たい[。 ]|ほうがいい)")
TBS07_RE = re.compile(r"(静かにして|助か|画面に助け|しんどい|見ていてほしい)")
CONFESS_RE = re.compile(r"(自分も|私も|僕も|わたしも|自分の都合|私の都合|例外|情けな|正直)")
ORDER_END_RE = re.compile(r"(ほしい|欲しい|してくれ|お願い|ください)")
SIMILE_END_RE = re.compile(r"(ような|みたい|たとえ|海|泳ぐ|放り出|ようだ)")


def sents(t):
    return [s.strip() for s in re.split(r"(?<=[。！？!?])", t) if s.strip()]


def closing_heur(last):
    if SIMILE_END_RE.search(last):
        return "たとえ・像"
    if ORDER_END_RE.search(last):
        return "望み・注文(〜してほしい)"
    return "その他"


def metrics(t, slot, st):
    ss = sents(t)
    rep = ob2.repetition_report(t)
    sb = st.get("structure") or {}
    tags = ((sb.get("tags_after") or sb.get("tags_before") or {}).get("tags") or {}).get(slot, {})
    m = {"chars": len(t), "n_sentences": len(ss),
         "repeat_pairs": rep["n_repeat_pairs"], "contrast_turns": rep["contrast_turns"], "last_vs_first_echo": rep["last_vs_first_echo"],
         "opening_type_tag": tags.get("opening_type"), "closing_type_tag": tags.get("closing_type"), "development_type_tag": tags.get("development_type"),
         "closing_heur": closing_heur(ss[-1]) if ss else "", "first_sentence": ss[0] if ss else "", "last_sentence": ss[-1] if ss else "",
         "monitor_sentences": [s for s in ss if MONITOR_RE.search(s)], "beki_sentences": [s for s in ss if BEKI_RE.search(s)],
         "institution_sentences": [s for s in ss if INSTITUTION_RE.search(s)], "concern_sentences": [s for s in ss if CONCERN_RE.search(s)],
         "wish_sentences": [s for s in ss if WISH_RE.search(s)], "tbs07_like_sentences": [s for s in ss if TBS07_RE.search(s)],
         "confession_like_sentences": [s for s in ss if CONFESS_RE.search(s)]}
    m["n_monitor"], m["n_beki"], m["beki_rate"] = len(m["monitor_sentences"]), len(m["beki_sentences"]), round(len(m["beki_sentences"]) / max(1, len(ss)), 2)
    m["n_institution"], m["n_tbs07_like"] = len(m["institution_sentences"]), len(m["tbs07_like_sentences"])
    fm = (st.get("final_maps") or {}).get(slot)
    m["final_unmapped"] = fm["n_unmapped"] if fm else None
    m["tbs07_by_id"] = len([r for r in fm["rows"] if "ONE_d" in r["source_ids"]]) if fm else None
    ur = (st.get("unmapped_regen") or {}).get(slot)
    m1 = (st.get("stages") or {}).get("map1", {}).get(slot)
    m["unmapped_initial"] = ur["n_unmapped_before"] if ur else (m1["n_unmapped"] if m1 else None)
    m["unmapped_regen_count"] = 1 if ur else 0
    m["structure_regen"] = bool(sb.get("regen") and sb["regen"]["slot"] == slot)
    return m


def main():
    data, all_m = {}, {}
    for name, d in RUNS.items():
        st = json.load(open(f"{d}/state.json", encoding="utf-8"))
        data[name] = st
        all_m[name] = {s: metrics(st["final_texts"][s], s, st) for s in SLOTS}
    json.dump(all_m, open(f"{OUT}/structure_metrics_02.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    rng = random.Random(SEED)
    order = list(RUNS)
    rng.shuffle(order)
    labels = dict(zip(("甲", "乙", "丙"), order))
    json.dump({"seed": SEED, "labels_V1": labels, "note": "Fable評価の結果記入後に開く"}, open(f"{OUT}/BLIND_KEY_02.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    L = []
    w = L.append
    w("# EVAL_SET_02 (委任_21 OF-Y7-06: Fable評価用資料。評価を2種類に分ける)\n")
    w("機械指標はローカル正規表現(`scripts/aggregate_02.py`、API 0、結果を見て調整していない)。**合否ではなく目視の補助**。VALIDATED判定はFable。構造タグ(冒頭型・結び型)は各runのluna判定。数値の詳細は`structure_metrics_02.json`。\n")
    w("## (A) V1の新旧比較(同じ人物。Prompt・Sheetだけが変わる=本当の新旧比較)\n")
    w("下の3本は旧R0・run_02a・run_02bのV1(One Voice)を乱数でラベル付替えしたもの。ラベルの対応は`BLIND_KEY_02.json`(**評価を記入してから開く**)。見る点: (1)TBS-07由来の内容が何回出るか(目標1文) (2)葛藤が残っているか (3)冗長か。\n")
    for lab, nm in labels.items():
        w(f"### V1-{lab}\n\n{data[nm]['final_texts']['voice_1']}\n")
    w("| 観点 | V1-甲 | V1-乙 | V1-丙 |\n|---|---|---|---|")

    def row(title, f):
        w(f"| {title} | " + " | ".join(str(f(all_m[labels[lab]]["voice_1"])) for lab in ("甲", "乙", "丙")) + " |")
    row("TBS-07由来らしい文の数(正規表現)", lambda m: m["n_tbs07_like"])
    row("TBS-07由来の文の数(出典付番ONE_d)", lambda m: m["tbs07_by_id"])
    row("repetition_reportの反復ペア数", lambda m: m["repeat_pairs"])
    row("対比語(でも・けど・ただ・いや等)の数", lambda m: m["contrast_turns"])
    row("結びが冒頭と近いか(last_vs_first_echo)", lambda m: m["last_vs_first_echo"])
    row("文数 / 字数", lambda m: f"{m['n_sentences']}文 / {m['chars']}字")
    row("結びの型(luna) / (正規表現)", lambda m: f"{m['closing_type_tag']} / {m['closing_heur']}")
    w("| Fable判定: 葛藤が残っているか | | | |\n| Fable判定: 冗長か | | | |\n| Fable判定: 新旧どちらが良いか | | | |\n")
    w("## (B) V2/V3の絶対評価(旧R0と人物が変わったので新旧盲検は成立しない。観点表で見る)\n")
    for nm in ("run_02a", "run_02b"):
        for s, ttl in (("voice_2", "V2 高校生(Another Voice)"), ("voice_3", "V3 中学生の子の親(A Third Voice)")):
            w(f"### {nm} {ttl}\n\n{data[nm]['final_texts'][s]}\n")
    w("| 観点 | 02a V2 | 02b V2 | 旧R0 V2(参考) | 02a V3 | 02b V3 | 旧R0 V3(参考) |\n|---|---|---|---|---|---|---|")

    def r2(title, f):
        cells = [str(f(all_m[nm][s])) for s in ("voice_2", "voice_3") for nm in ("run_02a", "run_02b", OLD)]
        w(f"| {title} | " + " | ".join(cells) + " |")
    r2("監視に触れる文の数(V2は1文以内が目安)", lambda m: m["n_monitor"])
    r2("制度・仕組みの解説らしい文の数(正規表現。その人が言いそうか目視で確認)", lambda m: m["n_institution"])
    r2("「べき」を含む文の割合", lambda m: f"{m['n_beki']}/{m['n_sentences']} ({m['beki_rate']})")
    r2("一人称の気がかり(心配・不安・困る・嫌等)の文の数", lambda m: len(m["concern_sentences"]))
    r2("一人称の望み(ほしい・たい等)の文の数", lambda m: len(m["wish_sentences"]))
    r2("反復ペア数(repetition_report)", lambda m: m["repeat_pairs"])
    r2("結びが冒頭と近いか", lambda m: m["last_vs_first_echo"])
    w("| Fable判定: テーマ一言テスト(この人は年齢による制限に何を望むのか、一言で言えるか) | | | | | | |\n| Fable判定: 制度設計の解説(その人が言いそうにない文)の有無 | | | | | | |\n| Fable判定: 自然さ | | | | | | |\n")
    w("## (C) 3人全体の冒頭型・結び型\n")
    w("| run | Voice | 冒頭型(luna) | 結びの型(luna) | 結びの型(正規表現) | 冒頭の文 | 結びの文 |\n|---|---|---|---|---|---|---|")
    for nm in (OLD, "run_02a", "run_02b"):
        for s in SLOTS:
            m = all_m[nm][s]
            w(f"| {nm} | {ob.SLOT_HEADING[s]} | {m['opening_type_tag']} | {m['closing_type_tag']} | {m['closing_heur']} | {m['first_sentence']} | {m['last_sentence']} |")
    for nm in (OLD, "run_02a", "run_02b"):
        c = {all_m[nm][s]["closing_type_tag"] for s in SLOTS}
        o = {all_m[nm][s]["opening_type_tag"] for s in SLOTS}
        w(f"\n- {nm}: 結びの型(luna)の種類={len(c)}/3、冒頭型(luna)の種類={len(o)}/3")
    w("\n| Fable判定: 結びの型が分かれているか / 冒頭の型が別々か | |\n|---|---|\n| run_02a | |\n| run_02b | |\n")
    w("## (D) 出典(UNMAPPEDと自己告白チェック)\n")
    w("| run | Voice | 初回UNMAPPED | UNMAPPED再生成 | 最終UNMAPPED | 構造再生成 | 自己告白らしい文(正規表現: 自分も・私の都合・例外・正直等) |\n|---|---|---|---|---|---|---|")
    for nm in (OLD, "run_02a", "run_02b"):
        for s in SLOTS:
            m = all_m[nm][s]
            w(f"| {nm} | {ob.SLOT_HEADING[s]} | {m['unmapped_initial']} | {m['unmapped_regen_count']} | {m['final_unmapped']} | {m['structure_regen']} | {'; '.join(m['confession_like_sentences']) or 'なし'} |")
    w("\n自己告白の出典照合(出典にない自己告白があるか)は、`PROVENANCE_02a.md`/`PROVENANCE_02b.md`の備考(agent目視)を参照。V1の許容される告白は出典ONE_d(TBS-07)の1文のみ。\n")
    open(f"{OUT}/EVAL_SET_02.md", "w", encoding="utf-8").write("\n".join(L))
    print("OK")


if __name__ == "__main__":
    main()
