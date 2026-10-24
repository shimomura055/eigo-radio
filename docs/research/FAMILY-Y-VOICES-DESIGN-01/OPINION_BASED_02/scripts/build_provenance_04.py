# -*- coding: utf-8 -*-
"""build_provenance_04.py -- 委任_25: PROVENANCE_04.md(宅配再配達テーマ R0 run_01 の出典対応表)を、runの出典対応(luna付番+機械照合)とagent目視メモから生成する。API 0。
実行: .venv\\Scripts\\python.exe docs/research/FAMILY-Y-VOICES-DESIGN-01/OPINION_BASED_02/scripts/build_provenance_04.py(リポジトリ直下から)
agent目視メモ(A_04)は、全文を読んで付けた(slot, 文番号0始まり) -> (agent判定, 備考)。判定語: OK / 補った表現のみ / OK(要注意) / OK(機械判定は偽陽性) / 出典外(捏造)。"""
import json
import os
import re
import sys

sys.path.insert(0, ".")
HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import er110_family_y_opinion_based_03 as ob3  # noqa: E402
import verify_voices_02 as vv  # noqa: E402

RD = "er110_output/family_y_opinion_based_03/redelivery_fee/run_01"
VJ = json.load(open(f"{D}/VOICES_02.json", encoding="utf-8"))
V = {v["id"]: v for v in VJ["voices"]}
S = VJ["sources"]
TH = ob3.load_theme()
ITEM = {x["id"]: x for sh in TH["sheets"].values() for x in sh["experiences"]}
SLOTS = ("voice_1", "voice_2", "voice_3")
HEAD = {"voice_1": "One Voice", "voice_2": "Another Voice", "voice_3": "A Third Voice"}
RESTRICTED = set(json.load(open(f"{D}/THEME_DATA_02.json", encoding="utf-8"))["restricted_voice_ids"])

A_04 = {
    ("voice_1", 0): ("OK", "ONE_c(不在票を入れて帰るときの気持ち。RV-55の趣旨を自分の言葉で)"),
    ("voice_1", 1): ("OK", "ONE_c末尾(そのまま次の家へ向かう)"),
    ("voice_1", 2): ("OK", "ONE_c(減ってほしい)+芯『きついのは本当』"),
    ("voice_1", 3): ("OK", "芯・矛盾欄(割り切れない)。ONE_aの反対側の言い換え"),
    ("voice_1", 4): ("OK", "ONE_a(請求より料金全体で受け止める)。逐語でなく言い換え"),
    ("voice_1", 5): ("OK", "ONE_a(送料無料の見直し=RV-56)+ONE_b(会社の側が見直されなくなる)。lunaはONE_aのみ"),
    ("voice_1", 6): ("OK(要注意)", "ONE_a(運ぶ人に回る=RV-56)。『運ぶ人』が三人称で、ドライバー本人の語りとして役割の手がかりがやや弱い(捏造ではない)。『料金の組み方まで』は注文の補い"),
    ("voice_2", 0): ("OK", "TWO_g/芯(払うとなると引っかかる)。lunaがTWO_eも付けたが、本文に『家にいたのに不在票』の自分の出来事は**ない**(TWO_eは仮定の意見欄で未使用)"),
    ("voice_2", 1): ("OK", "TWO_a・TWO_d"),
    ("voice_2", 2): ("OK", "TWO_b(午前指定、外出、戻ったら不在連絡票)。Eの出来事一つ"),
    ("voice_2", 3): ("OK", "TWO_a"),
    ("voice_2", 4): ("OK", "TWO_d(有料化の前に時間指定の遵守・届く日時の事前通知)"),
    ("voice_2", 5): ("OK", "TWO_f(配達員の事情は分かる)"),
    ("voice_2", 6): ("OK", "TWO_g/矛盾欄(分かるが納得できない)"),
    ("voice_2", 7): ("OK(要注意)", "感情の癖欄の『わたしが悪いの、と問い返す』を結びにした文。自分への問い返しの補い(出来事の追加ではない)"),
    ("voice_3", 0): ("OK", "THREE_a"),
    ("voice_3", 1): ("OK", "THREE_a(都合のいい時間に取りに行ける)+THREE_b(ロッカーにできない・営業所は遅れる・対面で受け取る)。Eの出来事は欄にあるもの"),
    ("voice_3", 2): ("OK", "THREE_c(同じ料金はおかしい)+THREE_a"),
    ("voice_3", 3): ("OK", "THREE_d(配達する人の時間を奪う、有料でいい)"),
    ("voice_3", 4): ("OK", "THREE_h(最初は無料で、くり返す人から)。V2には同種の項目なし(OF-Y8-04)"),
    ("voice_3", 5): ("OK(機械判定は偽陽性)", "THREE_e/矛盾欄(営業所が近い人の言い分かもしれない=引け目1つ)。lunaがIDを付けられずUNMAPPEDとしたが、Sheetの矛盾欄そのもの"),
}


def pages_text(src_ids):
    out = {}
    for s in src_ids:
        out[s] = vv.cut_ai_and_sidebar(vv.load_page_text(S[s]["url"].split("?")[0]))
    return out


def norm(s):
    return re.sub(r"[\s　、。，．,.!！?？「」『』（）()・…\-—:：;；\"'“”]", "", s)


def longest_common(a, b, n=8):
    grams = {b[i:i + n] for i in range(len(b) - n + 1)}
    for i in range(len(a) - n + 1):
        if a[i:i + n] in grams:
            j = i + n
            while j < len(a) and a[i:j + 1] in b:
                j += 1
            return a[i:j]
    return ""


def main():
    st = json.load(open(f"{RD}/state.json", encoding="utf-8"))
    final = st["final_texts"]
    rows, flags, fp = [], 0, 0
    r2p = {s: 0 for s in SLOTS}
    nsent = {s: 0 for s in SLOTS}
    src_dep = {s: {} for s in SLOTS}
    for s in SLOTS:
        fm = st["final_maps"][s]
        for r in fm["rows"]:
            verdict, note = A_04[(s, r["idx"])]
            ids = r["source_ids"]
            vids = sorted({v for i in ids for v in ITEM[i]["source_ids"]})
            src = "; ".join(f"{i}(" + ",".join(ITEM[i]["source_ids"]) + ")" for i in ids) or "(IDなし)"
            urls = "; ".join(sorted({S[V[v]["src"]]["url"] for v in vids})) or "—"
            if "要注意" in verdict:
                flags += 1
            if "偽陽性" in verdict:
                fp += 1
            nsent[s] += 1
            if ids and all(ITEM[i].get("r2plus_only") for i in ids):
                r2p[s] += 1
            for v in vids:
                src_dep[s][v] = src_dep[s].get(v, 0) + 1
            rows.append(f"| {HEAD[s]} | 第{r['idx'] + 1}文 | {r['text']} | {src} | {urls} | {','.join(r['supplement_kinds']) or 'なし'} | {r['verdict']} | {verdict} | {note or '—'} |")
    unm = {k: st["final_maps"][k]["n_unmapped"] for k in SLOTS}
    first = {k: (st["unmapped_regen"][k]["n_unmapped_before"] if k in st["unmapped_regen"] else st["stages"]["map1"][k]["n_unmapped"]) for k in SLOTS}
    # 長一致の機械照合(R0本文 vs R2+/R3出典本文。8文字以上、句読点除去後)
    restricted_src = sorted({V[v]["src"] for v in RESTRICTED})
    pg = pages_text(restricted_src)
    lm = []
    for s in SLOTS:
        t = norm(final[s])
        for src, body in pg.items():
            m = longest_common(t, norm(body))
            if m:
                lm.append((HEAD[s], src, m))
    NUM = re.compile(r"[0-9０-９]+|[〇一二三四五六七八九十百千万]+(?:年|か月|ヶ月|カ月|ケ月|歳|人|回|割|パーセント|円|時間|分間?|日|週間?|台|件|校|度|本|倍|軒|目|つ|か所)")
    qty = [(HEAD[s], m.group(0)) for s in SLOTS for m in NUM.finditer(final[s])]
    md = f"""# PROVENANCE_04 (委任_25: テーマ『宅配の再配達は有料にすべきか?』R0 run_01 の出典対応表。内部記録・リスナーには見せない)

対象: `{RD}/article_ja.md`(確定稿)。書式は`../OPINION_BASED_01/PROVENANCE_TEMPLATE_01.md`+「R2+のみが根拠の文」欄+agent目視判定。生成: `scripts/build_provenance_04.py`(runの`state.json`のluna付番+機械照合の結果と、agentが全{len(rows)}文を読んで付けた列を結合。API 0)。
手順は`PROVENANCE_03.md`と同じ(luna付番 → 機械照合 → UNMAPPEDのVoiceだけ各1回再生成 → agent目視)。**手作業での本文修正は0**。

## 1. 件数
- 初回生成の機械照合UNMAPPED: One Voice {first['voice_1']}文 / Another Voice {first['voice_2']}文 / A Third Voice {first['voice_3']}文。UNMAPPED再生成: {', '.join(f'{HEAD[k]} 1回' for k in st['unmapped_regen']) or 'なし'}(各Voice1回まで)。
- **再生成後の最終稿の機械照合UNMAPPED(final_map)**: One Voice {unm['voice_1']}文 / Another Voice {unm['voice_2']}文 / A Third Voice {unm['voice_3']}文(規則どおり再生成は各Voice1回までのため、最終稿のUNMAPPEDは記録のみ)。
- agent目視: 機械判定の**偽陽性**と判断した文 **{fp}件**(A Third Voice 第6文=Sheetの矛盾欄THREE_eにそのまま対応)。**要注意**(意味・文脈のずれ、出典にない補い)は **{flags}件**(下表の備考)。**出来事・人物・会話の捏造は0件**。最終稿に残る機械UNMAPPED {sum(unm.values())}文は上記の偽陽性。
- 世界設定の定義由来の出典外意見: 0件(V1・V2・V3に『物流業界全体の待遇』『環境』の語なし。EVAL_SET_04の逸脱文検査も0)。
- **Gate(Leakage判定)**: runnerは累計22円超で`SKIPPED_BUDGET`にしたため、同一委任内で後追い実行 -> **{st['gate_status']}**(判定1回、flagged {st['gate'].get('first_judgement_flagged')}、書換0、本文不変。`gate_status_original`=SKIPPED_BUDGET を`state.json`・`run_status.json`に残した)。
- 判定の限界: lunaの付番はIDの付け間違い・取りこぼしがある(例: Another Voice 第1文にTWO_eが付いたが本文に該当内容なし)。IDの正しさはagent目視で補ったが、**1名(1agent)の目視であり、独立した第二者の確認ではない**。

## 2. 対応表(1行=1文)
| Voice | 位置 | 文 | 経験欄ID(根拠の声ID) | 根拠URL | 補った表現(luna種別) | 機械判定 | agent判定 | 備考(要注意・偽陽性) |
|---|---|---|---|---|---|---|---|---|
""" + "\n".join(rows) + f"""

## 3. R2+のみが根拠の文(公開前の権利確認の対象。SOURCE_LOG_02 §5 (e)(f))と単一出典依存度
| Voice | 文数 | R2+/R3のみが根拠の文 | 声ID別の依存(その声を根拠に含む文数) |
|---|---|---|---|
""" + "\n".join(f"| {HEAD[s]} | {nsent[s]} | {r2p[s]} | " + ", ".join(f"{k}:{n}" for k, n in sorted(src_dep[s].items())) + " |" for s in SLOTS) + f"""

- **One Voice(V1)は全{nsent['voice_1']}文がR2+/R3(個人ブログ・note)のみを根拠にし、全文がRV-55(note、現役ドライバー1人)を根拠に含む**。Opus指摘どおり、V1は別人2系統以上の声(RV-55/56/59 = R2+、RV-29 = R2)の集約で、根拠はR2+だけ。V1の経験欄のうちONE_e/f/g/h(RV-58・RV-59・RV-29・RV-57)は今回の語りでは未使用で、語りはONE_a〜ONE_dの意見・気持ちが中心(RV-58の怒りは出ていない)。公開・商用化の前に許諾か他の声への置換が必要(DEV/Trialの範囲では使用可)。
- Another Voice(V2)・A Third Voice(V3)はR2(Yahoo知恵袋・小町等)の声が根拠で、R2+のみの文は0。V2の経験欄(E)は全件RV-08(知恵袋の1人)の1出典に依存(公開前Gate(e)の既知の例外、`PROMPT_DIFF_06.md`)。

## 4. 長一致の機械照合(公開前Gate(f))と数量表現の検査
- R0本文と、R2+/R3の出典({', '.join(restricted_src)})の本文の、**8文字以上(句読点・空白除去後)の共通部分列**: {('なし(0件)' if not lm else '; '.join(f'{a} x {b}: 「{c}」' for a, b, c in lm) + '。**agent判定: 偽陽性**(「〜るんじゃないかと」は一般的な推量の語尾で、出典の固有の言い回し・構成の写しではない。前後の語は一致していない)')}。
- R0本文の数字・数量表現(算用数字、漢数字+単位[年・歳・人・回・度・日・本・軒・目・つ等])の該当: {('なし(0件)' if not qty else '; '.join(f'{a}: 「{b}」' for a, b in qty))}。
- 回数の言い換え(Opus論点5): 『最初の再配達は無料にして、くり返し不在になる人から』(A Third Voice 第5文)。『二回目』『一度』等の数量表現は漏れていない。
"""
    open(f"{D}/PROVENANCE_04.md", "w", encoding="utf-8").write(md)
    print("PROVENANCE_04", len(rows), "flags", flags, "fp", fp, "longmatch", lm, "qty", qty, "r2p", r2p)


if __name__ == "__main__":
    main()
