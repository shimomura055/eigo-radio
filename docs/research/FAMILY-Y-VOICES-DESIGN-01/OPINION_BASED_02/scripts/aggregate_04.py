# -*- coding: utf-8 -*-
"""aggregate_04.py -- 委任_25: 再配達テーマ R0 run_01 の決定論集計(ローカル正規表現のみ。API 0)と EVAL_SET_04.md / structure_metrics_04.json の生成。
指標の関数は OPINION_BASED_01/scripts/aggregate_02.py をそのまま再利用(結果を見て調整していない)。合否ではなく目視の補助。Fable判定欄は空欄で返す。
実行: .venv\\Scripts\\python.exe docs/research/FAMILY-Y-VOICES-DESIGN-01/OPINION_BASED_02/scripts/aggregate_04.py(リポジトリ直下から)"""
import json
import os
import re
import sys

sys.path.insert(0, ".")
sys.path.insert(0, "docs/research/FAMILY-Y-VOICES-DESIGN-01/OPINION_BASED_01/scripts")
import aggregate_02 as a2  # noqa: E402
import er110_family_y_opinion_based_01 as ob  # noqa: E402

OUT = "docs/research/FAMILY-Y-VOICES-DESIGN-01/OPINION_BASED_02"
SLOTS = a2.SLOTS
RUNS = {"再配達 R0(run_01)": "er110_output/family_y_opinion_based_03/redelivery_fee/run_01",
        "SNS run_03": "er110_output/family_y_opinion_based_02/sns_age_limit/run_03"}
NAMES = list(RUNS)
RD, SNS = NAMES
DEV_RE = re.compile(r"(待遇|賃金|給料|報酬|労働|ブラック|残業|環境問題|環境|CO2|二酸化炭素|排出|温暖化|エコ|脱炭素)")      # 再配達テーマの逸脱(物流待遇・環境)。SNS側は監視(MONITOR_RE)を使う
QTY_RE = re.compile(r"[0-9０-９]+|[一二三四五六七八九十百千万]+(?:年|か月|ヶ月|歳|人|回|割|円|時間|分間?|日|週間?|台|件|度目?|本|倍|軒|つ|か所|番目)")
ANGER_RE = re.compile(r"(腹が立|腹立|怒|イライラ|ムカ|許せ)")
HOME_RE = re.compile(r"(家にいた|家にいる|在宅|チャイム|鳴らさ|鳴らされ|いるのに)")
COUNT_PARAPHRASE_RE = re.compile(r"(最初|くり返|何度|いきなり)")
FIRST_PERSON_RE = re.compile(r"(私|わたし|僕|うち)")


def main():
    data, all_m = {}, {}
    for name, d in RUNS.items():
        st = json.load(open(f"{d}/state.json", encoding="utf-8"))
        data[name] = st
        all_m[name] = {s: a2.metrics(st["final_texts"][s], s, st) for s in SLOTS}
        for s in SLOTS:
            ss = a2.sents(st["final_texts"][s])
            all_m[name][s]["theme_deviation_sentences"] = [x for x in ss if DEV_RE.search(x)]
            all_m[name][s]["qty_expressions"] = QTY_RE.findall(st["final_texts"][s])
    json.dump(all_m, open(f"{OUT}/structure_metrics_04.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    L = []
    w = L.append
    w("# EVAL_SET_04 (委任_25: 再配達テーマ R0 run_01 の Fable評価用資料。前テーマのSNS run_03と並記)\n")
    w("機械指標はローカル正規表現(`scripts/aggregate_04.py`=前回の`aggregate_02.py`の関数を再利用、API 0、結果を見て調整していない)。**合否ではなく目視の補助**。Fable判定欄は空欄。構造タグ(冒頭型・結び型)は各runのluna判定。数値の詳細は`structure_metrics_04.json`。")
    w("\n**注意**: 再配達R0はrunnerがLeakage Gateを`SKIPPED_BUDGET`にしたため、同一委任内で後追い実行した(`PASS`、判定1回、flagged 0、本文不変、`gate_status_original`を`state.json`に保存)。SNS run_03も同じ流れで後追いPASS済み。比較は**盲検ではない**(題材が違い、読めば区別できる)。\n")
    w("## (A) R0全文(3 Voice)\n")
    st = data[RD]
    for s in SLOTS:
        w(f"### {ob.SLOT_HEADING[s]}\n\n{st['final_texts'][s]}\n")
    w("## (B) 機械指標: 再配達R0 と SNS run_03 の並記\n")
    heads = [f"{ob.SLOT_HEADING[s]} / {n}" for n in NAMES for s in SLOTS]
    w("| 観点 | " + " | ".join(heads) + " |\n|" + "---|" * (len(heads) + 1))

    def row(title, f):
        w(f"| {title} | " + " | ".join(str(f(all_m[n][s], n)) for n in NAMES for s in SLOTS) + " |")
    row("文数 / 字数", lambda m, n: f"{m['n_sentences']}文 / {m['chars']}字")
    row("repetition_reportの反復ペア数(記録専用)", lambda m, n: m["repeat_pairs"])
    row("対比語(でも・けど・ただ・いや等)の数", lambda m, n: m["contrast_turns"])
    row("結びが冒頭と近いか(last_vs_first_echo)", lambda m, n: m["last_vs_first_echo"])
    row("監視相当: テーマ逸脱文の数(再配達=物流待遇・環境の語[正規表現]/ SNS=監視に触れる文)", lambda m, n: len(m["theme_deviation_sentences"]) if n == RD else m["n_monitor"])
    row("「べき」を含む文の割合", lambda m, n: f"{m['n_beki']}/{m['n_sentences']} ({m['beki_rate']})")
    row("制度・仕組みの解説らしい文の数(正規表現。目視で確認。『仕組み』『ルール』等の語を含む)", lambda m, n: m["n_institution"])
    row("一人称の気がかり(心配・不安・困る・嫌等)の文の数", lambda m, n: len(m["concern_sentences"]))
    row("一人称の望み(ほしい・たい等)の文の数", lambda m, n: len(m["wish_sentences"]))
    row("冒頭型(luna)", lambda m, n: m["opening_type_tag"])
    row("結びの型(luna) / (正規表現)", lambda m, n: f"{m['closing_type_tag']} / {m['closing_heur']}")
    row("初回UNMAPPED / UNMAPPED再生成 / 最終UNMAPPED", lambda m, n: f"{m['unmapped_initial']} / {m['unmapped_regen_count']} / {m['final_unmapped']}")
    row("構造再生成", lambda m, n: m["structure_regen"])
    row("自己告白らしい文(正規表現: 自分も・私の都合・例外・正直等)", lambda m, n: "; ".join(m["confession_like_sentences"]) or "なし")
    row("数字・数量表現の該当(正規表現。再配達は漢数字+軒・目・つ等も含む)", lambda m, n: "; ".join(m["qty_expressions"]) or "なし")
    w("\n- 再配達R0の反復ペア(記録専用・目視確認済み): One Voice 第2文と第6文(『そのまま』の語の重なり)、A Third Voice 第1文と第2文(営業所・ロッカー・受け取りの語の重なり)および第2文と第6文は、**語の重なりによる簡易判定の偽陽性で、同じ主張・同じたとえの反復ではない**(agent目視)。")
    for n in NAMES:
        c = {all_m[n][s]["closing_type_tag"] for s in SLOTS}
        o = {all_m[n][s]["opening_type_tag"] for s in SLOTS}
        w(f"\n- {n}: 結びの型(luna)の種類={len(c)}/3、冒頭型(luna)の種類={len(o)}/3")
    w("\n## (C) 冒頭の文・結びの文\n")
    w("| run | Voice | 冒頭型(luna) | 結びの型(luna) | 冒頭の文 | 結びの文 |\n|---|---|---|---|---|---|")
    for n in NAMES:
        for s in SLOTS:
            m = all_m[n][s]
            w(f"| {n} | {ob.SLOT_HEADING[s]} | {m['opening_type_tag']} | {m['closing_type_tag']} | {m['first_sentence']} | {m['last_sentence']} |")
    # ---- Opus「R0後に見る事項」の機械的事実 ----
    t = st["final_texts"]
    v1, v2, v3 = (a2.sents(t[s]) for s in SLOTS)
    w("\n## (D) Opusレビュー『R0後に見る事項』の観点表(機械的事実。判断はFable)\n")
    w("| 観点 | 機械的事実 | Fable判定 |\n|---|---|---|")
    w(f"| V1: RV-58の怒りが語りの中心になっていないか / 矛盾が一か所で収まっているか | 怒り語(腹が立つ・怒り・イライラ等)の該当 {len([x for x in v1 if ANGER_RE.search(x)])}文 / {len(v1)}文。対比語を含む文 {all_m[RD]['voice_1']['contrast_turns']}件。『割り切れない』の葛藤文: " + "; ".join(x for x in v1 if '割り切れ' in x or 'それでも' in x) + " | |")
    w(f"| V2: 在宅中の不在票を自分の出来事にしていないか | 在宅・チャイム・『いるのに』等の語の該当 {len([x for x in v2 if HOME_RE.search(x)])}文(該当文=『家にいる日と時間に指定している』=TWO_aの習慣の説明で、在宅中の不在票の出来事ではない。TWO_e=仮定の意見は語りに出ていない)。出来事の文: " + "; ".join(x for x in v2 if '不在票' in x) + " | |")
    w(f"| 回数の言い換えが自然か / 『二回目』等の漏れ | 数量表現の漏れ {len(all_m[RD]['voice_1']['qty_expressions']) + len(all_m[RD]['voice_2']['qty_expressions']) + len(all_m[RD]['voice_3']['qty_expressions'])}件。言い換えの文: " + "; ".join(x for s in (v1, v2, v3) for x in s if COUNT_PARAPHRASE_RE.search(x)) + " | |")
    w(f"| 3人の結論の幅 | V1 冒頭『{v1[0]}』結び『{v1[-1]}』 / V2 冒頭『{v2[0]}』結び『{v2[-1]}』 / V3 冒頭『{v3[0]}』結び『{v3[-1]}』。有料化への賛否の語: V3『有料でいい』を含む文={len([x for x in v3 if '有料でいい' in x])}、V2『払うのは納得できない』を含む文={len([x for x in v2 if '払うのは納得できない' in x])}、V1『割り切れない』を含む文={len([x for x in v1 if '割り切れ' in x])} | |")
    w(f"| 冒頭・結びの型が分かれているか(luna) | 冒頭 {[all_m[RD][s]['opening_type_tag'] for s in SLOTS]} / 結び {[all_m[RD][s]['closing_type_tag'] for s in SLOTS]}(SNS run_03: 冒頭 {[all_m[SNS][s]['opening_type_tag'] for s in SLOTS]} / 結び {[all_m[SNS][s]['closing_type_tag'] for s in SLOTS]}) | |")
    w(f"| 補った一人称の自然さ(私・わたし・僕) | 一人称語を含む文の数: V1 {len([x for x in v1 if FIRST_PERSON_RE.search(x)])}/{len(v1)}、V2 {len([x for x in v2 if FIRST_PERSON_RE.search(x)])}/{len(v2)}(『わたし』『わたしも夫も』)、V3 {len([x for x in v3 if FIRST_PERSON_RE.search(x)])}/{len(v3)}(『僕』)。男性2人(V1私・V3僕)の声の割り当ては音声段階の宿題 | |")
    w("| 多様性・面白さ(SNS run_03との比較) | 上の(B)(C)。SNSはV1=迷い・V2=要求・V3=たとえ。再配達はV1=要求、V2=問い返し、V3=迷い(引け目)で型は3/3 | |")
    w("\n## (E) 費用・Gate\n")
    w("| run | 費用(円) | gate_status |\n|---|---|---|")
    for n in NAMES:
        s_ = data[n]
        w(f"| {n} | {s_.get('final_cost_jpy')}(本文生成まで。後追いGateを含む合計は`BUDGET_LOG_OB_05.md`) | {s_.get('gate_status')}(元: {s_.get('gate_status_original', '—')}) |")
    w("\n| Fable判定 | 内容 |\n|---|---|\n| 再配達R0は方式の再現(VALIDATED限定の別テーマでの再現)として十分か | |\n| V1の根拠がR2+のみ(公開前の許諾か置換)の扱い | |\n| 規則9(数字禁止)と回数が論点のテーマの相性 | |\n")
    open(f"{OUT}/EVAL_SET_04.md", "w", encoding="utf-8").write("\n".join(L))
    print("OK")


if __name__ == "__main__":
    main()
