# -*- coding: utf-8 -*-
"""build_provenance_03.py -- 委任_22: PROVENANCE_03.md を、runの出典対応(luna付番+機械照合)とagent目視メモから生成する。API 0。
agent目視メモ(A_03)は、全文を読んで付けた(slot, 文番号0始まり) -> (agent判定, 備考)。判定語: OK / 補った表現のみ / OK(要注意) / OK(機械判定は偽陽性) / 出典外の意見(要注意)。"""
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

A_03 = {
    ("voice_1", 0): ("OK", "ONE_a。『課金のしくみ』は経験欄の言い方"),
    ("voice_1", 1): ("OK", "ONE_a"),
    ("voice_1", 2): ("OK(要注意)", "『分かってくれるんだと思う』はONE_a(話すと止まることも多い)の解釈の補い(感情・推測の言い換え。出来事の追加ではない)"),
    ("voice_1", 3): ("OK", "ONE_f(危険に気づけず助けも求められないかも)"),
    ("voice_1", 4): ("OK", "ONE_fへの感情の補い(怖い・放っておけない)"),
    ("voice_1", 5): ("補った表現のみ", "Personaの芯(年齢に応じたはっきりした決まり)。『動画やメッセージのアプリにも』は世界設定の前提。**定義由来の意見ではない**(段階的な制限・禁止と制限の区別の語なし)"),
    ("voice_1", 6): ("OK", "ONE_c(見守りの設定が面倒、もっと簡単に)"),
    ("voice_1", 7): ("OK", "TBSのみ根拠(TBS-07)。V1のTBS-07由来の1文目"),
    ("voice_1", 8): ("OK(要注意)", "Sheetの『矛盾・弱さ』欄(葛藤1か所・解消しない)を結びにした文。『子どもを守るためなら迷わず決められると思うのに…私もまだすぐには答えが出ない』は出典にない自己の迷いの補い(感情の補いの範囲、捏造でない)。lunaがONE_c/d/fを付けたが、TBS-07の内容そのものではない"),
    ("voice_2", 0): ("OK", "TWO_a"),
    ("voice_2", 1): ("OK", "TWO_a+TWO_e"),
    ("voice_2", 2): ("OK", "TWO_a/TWO_b。『アカウントを持つことまで禁止』はV2の主張(TWO_b: 極端な制限は控える)に対応し、世界設定の『利用禁止』語をV2が使うのは妥当"),
    ("voice_2", 3): ("OK(要注意)", "葛藤は1か所(自分で考えたい↔悪口や脅しの時は大人に頼りたい。TWO_c/TWO_f)。末尾『そこは自分でも都合がいいのかもしれない』は出典にない自己評価の補い(Sheetの感情の癖『自分で留保を足す』の範囲、出来事ではない)。監視への言及なし"),
    ("voice_2", 4): ("補った表現のみ", "TWO_b(講習・呼びかけ)の言い換えの否定形"),
    ("voice_2", 5): ("OK", "TWO_a(安全フィルター)。『友達と連絡を取れるまま』はTWO_a/e"),
    ("voice_3", 0): ("OK", "THREE_b。立場(中学生の子)の手がかり"),
    ("voice_3", 1): ("OK", "THREE_b"),
    ("voice_3", 2): ("OK", "THREE_a/b。『急にできるようにしなくていい』は『段階的に広げたい』の言い換え"),
    ("voice_3", 3): ("OK", "THREE_d(禁止の年齢を過ぎて準備なしに触れる)"),
    ("voice_3", 4): ("OK(要注意)", "『触れずにいた間に、使える力までつくとは思えない』はTHREE_dの『何の準備もしていなかったら』の解釈の補い(事実の追加ではない)"),
    ("voice_3", 5): ("OK(要注意)", "THREE_d(事故につながる)。第4・第6文と同じ心配(準備なしに急に使い始める)の言い換えで、**目視で軽い反復**(repetition_reportは0)"),
    ("voice_3", 6): ("OK", "THREE_dのたとえ(泳ぐ練習。たとえは1回)。結びの型=たとえ・像"),
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
    md = f"""# {title} (委任_22: 是正Trial {run} の出典対応表。内部記録・リスナーには見せない)

対象: `{rd}/article_ja.md`(確定稿)。書式は`PROVENANCE_TEMPLATE_01.md`+「TBSのみが根拠の文」欄+agent目視判定。生成: `scripts/build_provenance_03.py`(runの`state.json`のluna付番+機械照合の結果と、agentが全{len(rows)}文を読んで付けた列を結合。API 0)。
手順は`PROVENANCE_01.md`と同じ(luna付番 → 機械照合 → UNMAPPEDのVoiceだけ各1回再生成 → agent目視)。**手作業での本文修正は0**。

## 1. 件数
- 初回生成の機械照合UNMAPPED: One Voice {first['voice_1']}文 / Another Voice {first['voice_2']}文 / A Third Voice {first['voice_3']}文。UNMAPPED再生成: {', '.join(f'{HEAD[s]} 1回' for s in st['unmapped_regen']) or 'なし'}(各Voice1回まで)。
- **再生成後の最終稿の機械照合UNMAPPED(final_map)**: One Voice {unm['voice_1']}文 / Another Voice {unm['voice_2']}文 / A Third Voice {unm['voice_3']}文。規則どおり再生成は各Voice1回までのため、最終稿のUNMAPPEDは記録のみ(再生成の追加・手作業修正はしていない)。
- agent目視: 機械判定の**偽陽性**と判断した文 **{fp}件**(Personaの立場の手がかり、または経験欄の項目への対応をlunaが取りこぼした文)。**要注意**(意味・文脈のずれ、出典にない補い)は **{flags}件**(下表の備考)。出来事・人物・会話の捏造は**0件**。
- **世界設定の定義由来の出典外意見: 0件**(V1に『段階的な制限』『アカウント禁止と機能制限の区別』に当たる文なし。V1第6文は経験欄ONE_c、第8文はSheetの矛盾欄に対応)。**Gate(Leakage判定)は費用が累計22円を超えたため`SKIPPED_BUDGET`で未実行**(01から続く歯止め)。
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


build("run_03", A_03, "PROVENANCE_03")
