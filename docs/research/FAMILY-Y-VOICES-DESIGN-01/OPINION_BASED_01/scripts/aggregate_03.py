# -*- coding: utf-8 -*-
"""aggregate_03.py -- 委任_22: run_02a / run_02b / run_03 の決定論集計(ローカル正規表現のみ。API 0)と EVAL_SET_03.md / structure_metrics_03.json の生成。
指標は aggregate_02.py の関数をそのまま再利用(結果を見て調整していない)。合否ではなく目視の補助。Fable判定欄は空欄で返す。"""
import json
import sys

sys.path.insert(0, ".")
sys.path.insert(0, "docs/research/FAMILY-Y-VOICES-DESIGN-01/OPINION_BASED_01/scripts")
import aggregate_02 as a2
import er110_family_y_opinion_based_01 as ob

OUT = a2.OUT
SLOTS = a2.SLOTS
RUNS = {"run_02a": a2.RUNS["run_02a"], "run_02b": a2.RUNS["run_02b"], "run_03": "er110_output/family_y_opinion_based_02/sns_age_limit/run_03"}
NAMES = list(RUNS)
DEF_RE = __import__("re").compile(r"(成長に合わせて|広げる形|分けて考え|段階|区別|アカウントを持たせない)")


def main():
    data, all_m = {}, {}
    for name, d in RUNS.items():
        st = json.load(open(f"{d}/state.json", encoding="utf-8"))
        data[name] = st
        all_m[name] = {s: a2.metrics(st["final_texts"][s], s, st) for s in SLOTS}
        for s in SLOTS:
            all_m[name][s]["definition_like_sentences"] = [x for x in a2.sents(st["final_texts"][s]) if DEF_RE.search(x)]
    json.dump(all_m, open(f"{OUT}/structure_metrics_03.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    L = []
    w = L.append
    w("# EVAL_SET_03 (委任_22: run_03 の Fable評価用資料。EVAL_SET_02と同じ表構成で run_02a / run_02b / run_03 を並べる)\n")
    w("機械指標はローカル正規表現(`scripts/aggregate_03.py`=`aggregate_02.py`の関数を再利用、API 0、結果を見て調整していない)。**合否ではなく目視の補助**。Fable判定欄は空欄。構造タグ(冒頭型・結び型)は各runのluna判定。数値の詳細は`structure_metrics_03.json`。\n")
    w("**注意: run_03は費用が累計22円を超えたためGate(Leakage判定)が`SKIPPED_BUDGET`で実行されていない(01/02と同じ歯止め。run_02aはGate実行、run_02bは一部実行)。**\n")
    w("## (A) V1の比較(同じ人物。run_02a / run_02b / run_03。盲検ではない)\n")
    w("見る点: (1)世界設定の定義由来の意見(『段階的な制限』『アカウント禁止と機能制限の区別』)が混入しているか (2)TBS-07由来の内容が何回出るか(目標1文) (3)葛藤が残っているか (4)冗長か。\n")
    for nm in NAMES:
        w(f"### V1 {nm}\n\n{data[nm]['final_texts']['voice_1']}\n")
    w("| 観点 | " + " | ".join(f"V1 {n}" for n in NAMES) + " |\n|---|---|---|---|")

    def row(title, f):
        w(f"| {title} | " + " | ".join(str(f(all_m[n]["voice_1"])) for n in NAMES) + " |")
    row("定義由来らしい語を含む文(正規表現: 成長に合わせて・広げる形・分けて考え・段階・区別・アカウントを持たせない)", lambda m: "; ".join(m["definition_like_sentences"]) or "なし")
    row("TBS-07由来らしい文の数(正規表現)", lambda m: m["n_tbs07_like"])
    row("TBS-07由来の文の数(出典付番ONE_d)", lambda m: m["tbs07_by_id"])
    row("repetition_reportの反復ペア数", lambda m: m["repeat_pairs"])
    row("対比語(でも・けど・ただ・いや等)の数", lambda m: m["contrast_turns"])
    row("結びが冒頭と近いか(last_vs_first_echo)", lambda m: m["last_vs_first_echo"])
    row("文数 / 字数", lambda m: f"{m['n_sentences']}文 / {m['chars']}字")
    row("結びの型(luna) / (正規表現)", lambda m: f"{m['closing_type_tag']} / {m['closing_heur']}")
    w("| Fable判定: 定義由来の出典外意見の有無 | | | |\n| Fable判定: 葛藤が残っているか | | | |\n| Fable判定: 冗長か | | | |\n")
    w("## (B) V2/V3の絶対評価\n")
    for nm in NAMES:
        for s, ttl in (("voice_2", "V2 高校生(Another Voice)"), ("voice_3", "V3 中学生の子の親(A Third Voice)")):
            w(f"### {nm} {ttl}\n\n{data[nm]['final_texts'][s]}\n")
    heads = [f"{n} {v}" for v in ("V2", "V3") for n in NAMES]
    w("| 観点 | " + " | ".join(heads) + " |\n|" + "---|" * 7)

    def r2(title, f):
        cells = [str(f(all_m[nm][s])) for s in ("voice_2", "voice_3") for nm in NAMES]
        w(f"| {title} | " + " | ".join(cells) + " |")
    r2("監視に触れる文の数(V2は1文以内が目安)", lambda m: m["n_monitor"])
    r2("制度・仕組みの解説らしい文の数(正規表現。その人が言いそうか目視で確認)", lambda m: m["n_institution"])
    r2("「べき」を含む文の割合", lambda m: f"{m['n_beki']}/{m['n_sentences']} ({m['beki_rate']})")
    r2("一人称の気がかり(心配・不安・困る・嫌等)の文の数", lambda m: len(m["concern_sentences"]))
    r2("一人称の望み(ほしい・たい等)の文の数", lambda m: len(m["wish_sentences"]))
    r2("反復ペア数(repetition_report。記録専用)", lambda m: m["repeat_pairs"])
    r2("結びが冒頭と近いか", lambda m: m["last_vs_first_echo"])
    z = " | ".join([""] * 6)
    w(f"| Fable判定: テーマ一言テスト | {z} |\n| Fable判定: 制度設計の解説(その人が言いそうにない文)の有無 | {z} |\n| Fable判定: 自然さ(V3は同じたとえ・同じ心配の反復も) | {z} |\n")
    w("## (C) 3人全体の冒頭型・結び型\n")
    w("| run | Voice | 冒頭型(luna) | 結びの型(luna) | 結びの型(正規表現) | 冒頭の文 | 結びの文 |\n|---|---|---|---|---|---|---|")
    for nm in NAMES:
        for s in SLOTS:
            m = all_m[nm][s]
            w(f"| {nm} | {ob.SLOT_HEADING[s]} | {m['opening_type_tag']} | {m['closing_type_tag']} | {m['closing_heur']} | {m['first_sentence']} | {m['last_sentence']} |")
    for nm in NAMES:
        c = {all_m[nm][s]["closing_type_tag"] for s in SLOTS}
        o = {all_m[nm][s]["opening_type_tag"] for s in SLOTS}
        w(f"\n- {nm}: 結びの型(luna)の種類={len(c)}/3、冒頭型(luna)の種類={len(o)}/3")
    w("\n| Fable判定: 結びの型が分かれているか / 冒頭の型が別々か | |\n|---|---|\n" + "\n".join(f"| {n} | |" for n in NAMES) + "\n")
    w("## (D) 出典(UNMAPPEDと自己告白チェック)\n")
    w("| run | Voice | 初回UNMAPPED | UNMAPPED再生成 | 最終UNMAPPED | 構造再生成 | 自己告白らしい文(正規表現: 自分も・私の都合・例外・正直等) |\n|---|---|---|---|---|---|---|")
    for nm in NAMES:
        for s in SLOTS:
            m = all_m[nm][s]
            w(f"| {nm} | {ob.SLOT_HEADING[s]} | {m['unmapped_initial']} | {m['unmapped_regen_count']} | {m['final_unmapped']} | {m['structure_regen']} | {'; '.join(m['confession_like_sentences']) or 'なし'} |")
    w("\n自己告白の出典照合は`PROVENANCE_03.md`の備考(agent目視)を参照。V1の許容される告白は出典ONE_d(TBS-07)の1文のみ。\n")
    w("## (E) 費用・生成時間・Gate\n")
    w("| run | 費用(円) | gate_status |\n|---|---|---|")
    for nm in NAMES:
        w(f"| {nm} | {data[nm].get('final_cost_jpy')} | {data[nm].get('gate_status')} |")
    w("\n| Fable判定: 世界設定の定義由来の出典外意見が解消したか(Status確定: VALIDATED限定 / VALIDATED_LIMITED) | |\n|---|---|\n| run_03 | |\n")
    open(f"{OUT}/EVAL_SET_03.md", "w", encoding="utf-8").write("\n".join(L))
    print("OK")


if __name__ == "__main__":
    main()
