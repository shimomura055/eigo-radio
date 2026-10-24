# -*- coding: utf-8 -*-
"""build_provenance_02.py -- 委任_21: PROVENANCE_02a.md / PROVENANCE_02b.md を、runの出典対応(luna付番+機械照合)とagent目視メモから生成する。API 0。
agent目視メモ(A_02a / A_02b)は、全文を読んで付けた(slot, 文番号0始まり) -> (agent判定, 備考)。判定語: OK / 補った表現のみ / OK(要注意) / OK(機械判定は偽陽性) / 出典外の意見(要注意)。"""
import json
import sys

sys.path.insert(0, ".")
import er110_family_y_opinion_based_02 as ob2

OUT = "docs/research/FAMILY-Y-VOICES-DESIGN-01/OPINION_BASED_01"
ops = {x["id"]: x for x in json.load(open(f"{OUT}/sources/mirai_topics/_ops_v2.json", encoding="utf-8"))}
TBS = "https://newsdig.tbs.co.jp/articles/-/2618789"
SLOTS = ("voice_1", "voice_2", "voice_3")
HEAD = {"voice_1": "One Voice", "voice_2": "Another Voice", "voice_3": "A Third Voice"}
item = {x["id"]: x for s in SLOTS for x in ob2.SHEETS_02[s]["experiences"]}

A_02A = {
    ("voice_1", 0): ("OK", ""), ("voice_1", 1): ("OK", ""),
    ("voice_1", 2): ("OK", "ONE_fの『危険を危険と気づかない』を、子の様子への推測(〜のかな)として言い換え"),
    ("voice_1", 3): ("OK(要注意)", "ONE_a(話すと止まることも多い)と逆向きの留保『話せば大丈夫とも言い切れない』を足している。出典に直接ない解釈"),
    ("voice_1", 4): ("補った表現のみ", "Personaの芯(年齢に応じたはっきりした決まり)。『動画やメッセージのアプリも含めて』は世界設定の前提"),
    ("voice_1", 5): ("OK(要注意)", "『そのたびに私が迷わずに済むように』は出典にない気持ちの補い(ONE_cの見守り設定の面倒の言い換えに近いが、直接の対応はない)"),
    ("voice_1", 6): ("出典外の意見(要注意)", "『成長に合わせて広げる形』は世界設定の『段階的な制限』の定義由来で、V1の経験欄にない(V3の主張に近い)"),
    ("voice_1", 7): ("OK", "TBSのみ根拠(TBS-07)。V1のTBS-07由来はこの1文のみ"),
    ("voice_1", 8): ("OK(要注意)", "『守りたいから賛成、とすぐには言えない自分もいる』は、TBS-07の『助かる』とは別の自己の迷いの補い(出典にない自己告白に近い)。『アカウントを持つこと自体を禁止』は世界設定の区別定義由来"),
    ("voice_2", 0): ("OK", ""),
    ("voice_2", 1): ("OK(機械判定は偽陽性)", "TWO_e(高校生でアカウントを作れないと困る)+TWO_a(子ども同士の連絡)に対応。lunaが付番を取りこぼした"),
    ("voice_2", 2): ("OK", ""),
    ("voice_2", 3): ("OK", "葛藤(自分で判断したい↔悪口や脅しの時は大人に頼りたい)は1か所。MR-T010-02の核心。監視への言及なし"),
    ("voice_2", 4): ("補った表現のみ", "口調"), ("voice_2", 5): ("OK", "TWO_a(安全フィルターなど別の対策)"),
    ("voice_3", 0): ("OK(機械判定は偽陽性)", "人物設定(中学生の子を育てている親=Sheetのrole)の描写。出典の経験ではなく立場の手がかり"),
    ("voice_3", 1): ("OK(要注意)", "THREE_a(年齢は大凡の目安)に対応。『うちの子はもう大丈夫だとは思えない』は仮定の外での『うちの子』(Sheetの指示は仮定の中のみ)。出来事ではないが境界"),
    ("voice_3", 2): ("OK", "THREE_b"), ("voice_3", 3): ("OK", "THREE_dを仮定(もし〜)で語る"),
    ("voice_3", 4): ("OK(機械判定は偽陽性)", "THREE_dの言い換え。『触ったこともない』は『何の準備もしていなかったら』の言い換えだが、事実の追加に近い言い方"),
    ("voice_3", 5): ("OK", "THREE_b/c"), ("voice_3", 6): ("OK(要注意)", "THREE_dのたとえ(泳ぐ練習)。『うちの子にも…時間が必要』は仮定の外の言い方"),
}
A_02B = {
    ("voice_1", 0): ("OK", ""), ("voice_1", 1): ("OK", ""),
    ("voice_1", 2): ("OK(要注意)", "ONE_aと逆向きの留保『話せば済むということでもない』を足している。出典に直接ない解釈"),
    ("voice_1", 3): ("OK", "ONE_f"),
    ("voice_1", 4): ("OK(機械判定は偽陽性)", "Personaの芯(年齢に応じたはっきりした決まり)。出典IDのない主張・望みの文"),
    ("voice_1", 5): ("出典外の意見(要注意)", "『アカウントを持たせないことと、使える機能を決めることは、分けて考えたい』は世界設定の区別定義由来で、V1の経験欄にない意見。lunaのUNMAPPEDは妥当"),
    ("voice_1", 6): ("OK", "TBSのみ根拠(TBS-07)。V1のTBS-07由来の文はこの1文のみ(次の文のluna付番ONE_dはAgent目視ではTBS由来でない)"),
    ("voice_1", 7): ("OK(要注意)", "『守りたいのは本当』(Personaの建前)+『まだ言葉がまとまらない』(葛藤を抱えた結び=補った表現)。lunaはONE_d/ONE_fと付番したが、TBS-07の内容ではない"),
    ("voice_2", 0): ("OK", ""), ("voice_2", 1): ("OK", ""), ("voice_2", 2): ("OK", ""),
    ("voice_2", 3): ("OK", "葛藤(自分で考えたい↔悪口や脅しの時は大人に頼りたい)は1か所。監視への言及なし"),
    ("voice_2", 4): ("補った表現のみ", "口調"), ("voice_2", 5): ("OK", "TWO_g(利用する側のことを考えないルール)の言い換え"), ("voice_2", 6): ("OK", "TWO_a"),
    ("voice_3", 0): ("OK(機械判定は偽陽性)", "人物設定(中学生の子を持つ親)の描写。出典の経験ではなく立場の手がかり"),
    ("voice_3", 1): ("OK", "THREE_b"),
    ("voice_3", 2): ("OK(要注意)", "THREE_c/d。『アカウントを持つことまで禁止するより』は世界設定の区別定義由来"),
    ("voice_3", 3): ("OK", "THREE_dのたとえ"),
    ("voice_3", 4): ("OK(機械判定は偽陽性)", "THREE_d(禁止の年齢を過ぎて準備なしに触れると事故)を、仮定(もし〜)+『うちの子』(細部なし)で語る。Sheetの指示どおり"),
    ("voice_3", 5): ("OK", "THREE_a/d"), ("voice_3", 6): ("OK", "THREE_dのたとえ(心配の像)。結びの型=像"),
}


def url(i):
    return TBS if i.startswith("TBS") else ops[i]["url"]


def build(run, A, title):
    rd = f"er110_output/family_y_opinion_based_02/sns_age_limit/{run}"
    st = json.load(open(f"{rd}/state.json", encoding="utf-8"))
    rows, tbs_rows, flags, fp = [], [], 0, 0
    for s in SLOTS:
        fm = st["final_maps"][s]
        for r in fm["rows"]:
            verdict, note = A[(s, r["idx"])]
            ids = r["source_ids"]
            src = "; ".join(f"{i}(" + ",".join(item[i]["source_ids"]) + ")" for i in ids) or "(IDなし)"
            urls = "; ".join(sorted({url(x) for i in ids for x in item[i]["source_ids"]}))
            if "要注意" in verdict:
                flags += 1
            if "偽陽性" in verdict:
                fp += 1
            rows.append(f"| {HEAD[s]} | 第{r['idx'] + 1}文 | {r['text']} | {src} | {urls} | {','.join(r['supplement_kinds']) or 'なし'} | {r['verdict']} | {verdict} | {note or '—'} |")
            if any(x.startswith("TBS") for i in ids for x in item[i]["source_ids"]) and r["idx"] in fm.get("tbs_only_idx", []):
                tbs_rows.append(f"| {HEAD[s]} | 第{r['idx'] + 1}文 | {r['text']} |")
    unm = {s: st["final_maps"][s]["n_unmapped"] for s in SLOTS}
    first = {s: (st["unmapped_regen"][s]["n_unmapped_before"] if s in st["unmapped_regen"] else st["stages"]["map1"][s]["n_unmapped"]) for s in SLOTS}
    md = f"""# {title} (委任_21: 改善R0 {run} の出典対応表。内部記録・リスナーには見せない)

対象: `{rd}/article_ja.md`(確定稿)。書式は`PROVENANCE_TEMPLATE_01.md`+「TBSのみが根拠の文」欄+agent目視判定。生成: `scripts/build_provenance_02.py`(runの`state.json`のluna付番+機械照合の結果と、agentが全{len(rows)}文を読んで付けた列を結合。API 0)。
手順は`PROVENANCE_01.md`と同じ(luna付番 → 機械照合 → UNMAPPEDのVoiceだけ各1回再生成 → agent目視)。**手作業での本文修正は0**。

## 1. 件数
- 初回生成の機械照合UNMAPPED: One Voice {first['voice_1']}文 / Another Voice {first['voice_2']}文 / A Third Voice {first['voice_3']}文。UNMAPPED再生成: {', '.join(f'{HEAD[s]} 1回' for s in st['unmapped_regen']) or 'なし'}(各Voice1回まで)。
- **再生成後の最終稿の機械照合UNMAPPED(final_map)**: One Voice {unm['voice_1']}文 / Another Voice {unm['voice_2']}文 / A Third Voice {unm['voice_3']}文。規則どおり再生成は各Voice1回までのため、最終稿のUNMAPPEDは記録のみ(再生成の追加・手作業修正はしていない)。
- agent目視: 機械判定の**偽陽性**と判断した文 **{fp}件**(Personaの立場の手がかり、または経験欄の項目への対応をlunaが取りこぼした文)。**要注意**(意味・文脈のずれ、出典にない補い)は **{flags}件**(下表の備考)。出来事・人物・会話の捏造は**0件**。
- 判定の限界: lunaの付番はIDの付け間違い・取りこぼしがある。IDの正しさはagent目視で補ったが、**1名(1agent)の目視であり、独立した第二者の確認ではない**。

## 2. 対応表(1行=1文)
| Voice | 位置 | 文 | 経験欄ID(根拠の声ID) | 根拠URL | 補った表現(luna種別) | 機械判定 | agent判定 | 備考(要注意・偽陽性・TBSのみ) |
|---|---|---|---|---|---|---|---|---|
""" + "\n".join(rows) + f"""

## 3. TBSのみが根拠の文(公開前の権利確認の対象。OF-Y6-10)
| Voice | 位置 | 文 |
|---|---|---|
""" + ("\n".join(tbs_rows) or "| (なし) | | |") + """

- 上記以外の文は、みらい議会(CC BY 4.0)の本人回答、Personaの立場・口調・芯(補った表現)、または世界設定の定義に対応する。TBS-10・TBS-02は本稿のいかなる文の根拠にもしていない。
"""
    open(f"{OUT}/{title}.md", "w", encoding="utf-8").write(md)
    print(title, len(rows), "flags", flags, "fp", fp, "tbs", len(tbs_rows))


build("run_02a", A_02A, "PROVENANCE_02a")
build("run_02b", A_02B, "PROVENANCE_02b")
