# -*- coding: utf-8 -*-
"""build_provenance_01.py -- 委任_18 F: PROVENANCE_01.md を、runの出典対応(luna付番+機械照合)とagent目視メモから生成する。API 0。"""
import json
import sys

sys.path.insert(0, ".")
import er110_family_y_opinion_based_01 as ob

NEW = "er110_output/family_y_opinion_based_01/sns_age_limit/run_01"
OUT = "docs/research/FAMILY-Y-VOICES-DESIGN-01/OPINION_BASED_01"
ops = {x["id"]: x for x in json.load(open(f"{OUT}/sources/mirai_topics/_ops_v2.json", encoding="utf-8"))}
TBS = "https://newsdig.tbs.co.jp/articles/-/2618789"
st = json.load(open(f"{NEW}/state.json", encoding="utf-8"))
item = {x["id"]: x for s in ob.SLOTS for x in ob.SHEETS[s]["experiences"]}


def url(i):
    return TBS if i.startswith("TBS") else ops[i]["url"]


# agent目視(全24文を読んで付与)。kind/summary/edit/supp/verdict/flag。verdict: OK / 補った表現のみ / OK(要注意) / UNMAPPED
A = {
 ("voice_1", 0): ("経験", "子どもが刺激の強いものや課金を興味のままに選んでしまったことがある", "子→「うちの小さい子」(役割の一般化)", "「うちの」(口調)", "OK", ""),
 ("voice_1", 1): ("経験", "話をすると、じゃあやらない、となることも多い", "括弧なしで地の文に", "なし", "OK", ""),
 ("voice_1", 2): ("主張", "年齢に応じた使い方の決まりがあってほしい", "Personaの芯(ONE_e/ONE_fに基づく編集)。出来事なし", "「親が話すだけじゃなくて」(つなぎ)", "OK(要注意)", "意味のずれ小: 出典ONE_aは『話せば止まることも多い』とあり、『話すだけじゃなくて』は出典の意図とずれる言い回し"),
 ("voice_1", 3): ("感情", "はっきりしているほうが安心できる", "Personaの芯。出来事なし", "感情の言い方", "補った表現のみ", ""),
 ("voice_1", 4): ("経験", "静かにしてほしい長い移動の時に動画を見てくれると助かる", "「電車」→「長い移動」(一般化)", "「なんだ」(口調)", "OK", "TBSのみ根拠(TBS-07)"),
 ("voice_1", 5): ("感情", "助かっている(正直な認め)", "TBS-07の「正直助かる」", "なし", "OK", "TBSのみ根拠(TBS-07)"),
 ("voice_1", 6): ("経験", "制限がかかると親もしんどい時がある", "そのまま(親→私)", "なし", "OK", "TBSのみ根拠(TBS-07)"),
 ("voice_1", 7): ("矛盾", "子どものために制限してほしいが、自分の都合では見ていてほしい時もある", "前半=ONE_e/f(制限を望む)、後半=TBS-07(自分の都合)", "「いや、」(口調)", "OK", "後半はTBSのみ根拠(TBS-07)"),
 ("voice_1", 8): ("主張", "小さいうちは、はっきりした決まりがあってほしい", "Personaの芯の再掲", "なし", "補った表現のみ", ""),
 ("voice_2", 0): ("感情", "投稿まで親に見られるのは少し嫌", "「少し嫌」→「正直ちょっと嫌だ」", "「正直ちょっと」(口調)", "OK", ""),
 ("voice_2", 1): ("事情", "友達との連絡にSNSを使う", "「子ども同士」→「友達」。高校生の手がかり", "「高校生の僕には」(手がかり)", "OK", "luna付番はTWO_e,TWO_fだが、agentはTWO_fのみと判断(TWO_eは模試)"),
 ("voice_2", 2): ("意見", "年齢で縛られるのも、アカウントを持てないのも困る", "TWO_f(年齢制限に反対)+TWO_e(作れないと困る)の合成", "なし", "OK", ""),
 ("voice_2", 3): ("矛盾", "見られるとSNSのよさが消えるが、悪口や脅しの時は大人につなげたい", "意味・立場は元の回答のまま", "なし", "OK", ""),
 ("voice_2", 4): ("意見", "全部見せるのは違う", "TWO_b(知られたくない内容も)の軽い一般化", "「やっぱり」(口調)", "OK", ""),
 ("voice_2", 5): ("意見", "安全フィルターなど別のやり方がいい", "TWO_fをそのまま", "なし", "OK(要注意)", "文脈の移し替え: 元は『年齢制限の代わりの対策』で、ここでは『見守り(全部見せる)の代わり』として使われている"),
 ("voice_2", 6): ("主張", "やめさせるより、困った時に頼れるよう細かく調整してほしい", "TWO_a(微調整が必要)", "なし", "OK", ""),
 ("voice_3", 0): ("主張", "判断できるようになってからアカウントを作れるように", "THREE_dをほぼそのまま", "なし", "OK", ""),
 ("voice_3", 1): ("意見", "小学生や中学生にはDMのような機能は不安", "THREE_c(中学生本人の声)", "「わたしたち中学生や小学生には」", "OK(要注意)", "「わたしたち…小学生」は V3が中学生のため言い過ぎ(出典は『小中学生だと不安』)"),
 ("voice_3", 2): ("意見", "高校生くらいになればある程度は自分で考えて使える", "THREE_c", "なし", "OK", ""),
 ("voice_3", 3): ("主張", "使っていい機能は年齢で分けたほうがいい", "THREE_cの理由から導く解釈(topic_title/stanceは不使用)", "「だから」(つなぎ)", "OK(要注意)", "結論はagentによる解釈。本文は機能の例示と理由のみ"),
 ("voice_3", 4): ("意見", "アカウントを作ることと、どの機能でも使えることは同じにしなくていい", "THREE_c(機能の段階)とTHREE_d(作成の条件)の組合せで作られた区別", "仮定・意見の言い換え", "OK(要注意)", "出典に直接ない区別を新しく立てている。出来事ではないがUNMAPPEDではない境界例"),
 ("voice_3", 5): ("意見", "自分で決められないうちから何でもできるようにはしてほしくない", "THREE_c/dの言い換え", "なし", "OK", ""),
 ("voice_3", 6): ("意見", "良し悪しを考えられることが先", "THREE_dの言い換え", "なし", "OK", ""),
 ("voice_3", 7): ("主張", "はっきり決めておくべき", "THREE_c/d(共通の目安への言及は薄い。THREE_g由来の『最低ライン』は出ていない)", "なし", "OK", ""),
}
rows, tbs_rows = [], []
n_flag = 0
for s in ob.SLOTS:
    fm = st["final_maps"][s]
    for r in fm["rows"]:
        k = (s, r["idx"])
        kind, summ, edit, supp, verdict, flag = A[k]
        ids = r["source_ids"]
        src = "; ".join(f"{i}(" + ",".join(item[i]["source_ids"]) + ")" for i in ids) or "(IDなし)"
        urls = "; ".join(sorted({url(x) for i in ids for x in item[i]["source_ids"]}))
        if flag and "TBSのみ" not in flag:
            n_flag += 1
        rows.append(f"| {ob.SLOT_HEADING[s]} | 第{r['idx'] + 1}文 | {summ} | {kind} | {src} | {urls} | {edit} | {supp} / luna種別:{','.join(r['supplement_kinds']) or 'なし'} | {r['verdict']} | {verdict} | {flag or '—'} |")
        if "TBSのみ" in flag:
            tbs_rows.append(f"| {ob.SLOT_HEADING[s]} | 第{r['idx'] + 1}文 | {r['text']} | {flag} |")
unm = {s: (st["unmapped_regen"][s]["n_unmapped_before"] if s in st["unmapped_regen"] else 0) for s in ob.SLOTS}
md = f"""# PROVENANCE_01 (委任_18 F: 実在意見ベースR0の出典対応表。内部記録・リスナーには見せない)

対象: `er110_output/family_y_opinion_based_01/sns_age_limit/run_01/article_ja.md`(確定稿)。書式は`PROVENANCE_TEMPLATE_01.md`+「TBSのみが根拠の文」欄+agent目視判定。生成: `scripts/build_provenance_01.py`(runの`state.json`のluna付番+機械照合の結果と、agentが全{len(rows)}文を読んで付けた列を結合。API 0)。
手順: (1)luna(gpt-6-luna)が各文に許可リストのIDまたは補った表現の種別を付番 → (2)機械照合(許可リスト外ID・IDも補いもない・出来事らしい文でE-IDなし[仮定形は除く]・出来事主張でIDなし=UNMAPPED)→ (3)UNMAPPEDのVoiceだけ各1回再生成 → (4)agentが全文を目視。**手作業での本文修正は0**。

## 1. 件数
- 初回生成の機械照合UNMAPPED: One Voice **{unm['voice_1']}文**、Another Voice **{unm['voice_2']}文**、A Third Voice **{unm['voice_3']}文**(計{sum(unm.values())}文)。各Voiceの再生成は**1回まで**(One Voice 1回、A Third Voice 1回、Another Voice 0回)=計2回。再生成後の最終稿の機械照合UNMAPPEDは **0文**。
- 注記: 初回の3文は、agentの事後確認では出来事の捏造というより、lunaが「年代・立場の手がかり」や既出の経験を取りこぼした**偽陽性の疑いが強い**(例: 「わたしたち中学生にも…目安がほしい」)。ただし規則(UNMAPPEDは再生成)に従い再生成し、初回稿は`state.json`に保存。
- agent目視で付けた**要注意(UNMAPPEDではないが意味・文脈のずれの可能性)**: **{n_flag}件**(下表の備考。TBSのみ根拠の4文は別枠で§3)。出来事・人物・会話の捏造は**0件**。
- 経験(出来事)として本文に出た内容はすべて経験欄(ONE_a/ONE_d)に由来。A Third Voiceには経験欄に出来事が無く、本文にも出来事は出ていない(意見・仮定のみ)。
- 判定の限界: lunaの付番はIDの付け間違いがある(例: Another Voice第2文のID)。機械照合は『許可リスト内か』を見るだけで、IDの正しさまでは保証しない。IDの正しさはagent目視で補ったが、**1名(1agent)の目視であり、独立した第二者の確認ではない**。

## 2. 対応表(1行=1文)
| Voice | 位置 | 主張・経験・感情の要約 | 種別 | 経験欄ID(根拠の声ID) | 根拠URL | 編集・一般化 | 補った表現 | 機械判定 | agent判定 | 備考(要注意・TBSのみ) |
|---|---|---|---|---|---|---|---|---|---|---|
""" + "\n".join(rows) + f"""

## 3. TBSのみが根拠の文(公開前の権利確認の対象。OF-Y6-10)
| Voice | 位置 | 文 | 備考 |
|---|---|---|---|
""" + "\n".join(tbs_rows) + """

- 上記以外の文は、みらい議会(CC BY 4.0)の本人回答、またはPersonaの芯・口調(補った表現)に対応する。
- TBS-10(番組出演者の発言)は、本稿のいかなる文の唯一の根拠にもしていない(反動のイライラはMR-T015-06が根拠)。TBS-02は経験欄(TWO_h)にあったが本文に使われなかった。
- 公開する場合: 上記TBS-07由来の4文(第5・6・7文と第8文の後半)について、TBS NEWS DIGの許諾要否を確認するか、MR由来の内容に差し替える(差し替えはユーザー判断の範囲外=Phase 2の対象外)。

## 4. 本稿に使われた出典IDの集計(経験欄ID→声ID)
""" + "\n".join(f"- {ob.SLOT_HEADING[s]}: " + ", ".join(f"{x['id']}=" + "+".join(x["source_ids"]) + ("(TBSのみ)" if x["tbs_only"] else "") for x in ob.SHEETS[s]["experiences"]) for s in ob.SLOTS) + "\n"
open(f"{OUT}/PROVENANCE_01.md", "w", encoding="utf-8").write(md)
print(len(rows), n_flag, len(tbs_rows))
