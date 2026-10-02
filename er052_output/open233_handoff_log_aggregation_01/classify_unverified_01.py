# -*- coding: utf-8 -*-
"""OPEN-233-SELF-RECOVERY-TRIAL-01 委任_45: 「Checker引用の特定不能35件」の原因分類(分析専用)。

【性質】既存の er052_output/open233_self_recovery_flow_runner_01_*/instances_*/*.json を読むだけ。
LLM/API/TTS/Web Searchは一切使わない。既存モジュール(aggregate_01.py・runner等)はimportしない
(標準ライブラリのみ)。出力は同ディレクトリの unverified35_classification_01.csv。
どこからも呼ばれない。範囲の確定には使わない(診断用の出現回数・位置は「診断」と明記)。

手順:
 1. 全instance JSONから、委任_41と同じ定義(K1=Checker自身のclaim_in_article、BLOCKING)の指摘を取り出し、
    独立に実装した照合(L0〜L4)で「確定不能(A4)」を再抽出する。委任_41のclaims_detail_01.csvの該当行と突き合わせる。
 2. 13種類(ユニーク)それぞれに、記事本文の該当箇所(逐語)・差分・区分を目視で判定した結果をMANUALに記入。
    記事本文の該当箇所は、スクリプトが記事に実在する(逐語substring)ことを確認する(転記ミス防止)。
 3. 各行に、現行方式での最終結果・次周回での同fact再指摘・現行の対象の一致判定を付けてCSVへ。
"""
import csv
import glob
import json
import os
import re
import sys
from collections import Counter, OrderedDict, defaultdict

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
TARGET = re.compile(r"(iter[5-8]|rep(7|8|9|1\d|2[01]))$")
CURLY = {"’": "'", "‘": "'", "“": '"', "”": '"'}
PAIRS = [("“", "”"), ('"', '"'), ("‘", "’"), ("「", "」"), ("『", "』")]
FRAG = re.compile(r"“([^”]+)”|「([^」]+)」|『([^』]+)』")
CONN = re.compile(r"\b(and|or)\b|[&,;、，；と/／.。:：]|および|\s", re.I)
TRAIL = ".,;:!?。、，；：！？ "


def norm(s, lower):
    out = []
    prev_sp = False
    for ch in s:
        if ch.isspace():
            if not prev_sp:
                out.append(" ")
            prev_sp = True
            continue
        prev_sp = False
        ch = CURLY.get(ch, ch)
        out.append(ch.lower() if lower else ch)
    return "".join(out)


def count(text, sub):
    return text.count(sub) if sub else 0


def match(cand, text):
    """独立実装のL0〜L3。返値 ok/multi/none。"""
    raw = cand.strip()
    st = None
    if len(raw) >= 2:
        for o, c in PAIRS:
            if raw[0] == o and raw[-1] == c:
                st = raw[1:-1].strip()
    for lower in (None, False, True):
        for v in (raw, st):
            if not v:
                continue
            if lower is None:  # L0/L1 完全一致
                n = count(text, v)
            else:  # L2/L3
                n = count(norm(text, lower), norm(v.strip(), lower).strip())
            if n == 1:
                return "ok"
            if n >= 2:
                return "multi"
    return "none"


def resolve(claim, text):
    r = match(claim, text)
    if r != "none":
        return r
    frags = [next(g for g in m.groups() if g is not None) for m in FRAG.finditer(claim)]
    rest = CONN.sub("", FRAG.sub("", claim))
    if len(frags) >= 2 and rest == "":
        return "ok" if all(match(f, text) == "ok" for f in frags) else "none"
    if frags and rest != "":
        return "explanatory"
    return "none"


def is_ja(s):
    t = re.sub(r"\s", "", s)
    return bool(t) and len(re.findall(r"[぀-ゟ゠-ヿ一-鿿]", t)) / len(t) >= 0.15


def load_runs():
    runs = []
    for dd in sorted(glob.glob(os.path.join(ROOT, "er052_output", "open233_self_recovery_flow_runner_01_*"))):
        name = os.path.basename(dd).split("_01_", 1)[1]
        if not TARGET.match(name):
            continue
        for f in sorted(glob.glob(os.path.join(dd, "instances_*", "*.json"))):
            d = json.load(open(f, encoding="utf-8"))
            if "cycles" not in d:
                continue
            rel = os.path.relpath(f, os.path.join(ROOT, "er052_output")).replace("\\", "/")
            rel = rel.replace("open233_self_recovery_flow_runner_01_", "")
            runs.append({"path": rel, "dir": name, "d": d})
    return runs


def cycle_texts(cycles, i):
    c = cycles[i]
    en, ja = c.get("en_text_before_rewrite"), c.get("ja_text_before_rewrite")
    if i > 0:
        p = cycles[i - 1]
        en = en if en is not None else p.get("en_text_after_rewrite")
        ja = ja if ja is not None else p.get("ja_text_after_rewrite")
    return en, ja


def borrow_map(runs):
    en_t = defaultdict(set)
    ja_t = defaultdict(set)
    for r in runs:
        cs = r["d"]["cycles"]
        if cs:
            if cs[0].get("en_text_before_rewrite") is not None:
                en_t[r["d"]["instance_id"]].add(cs[0]["en_text_before_rewrite"])
            if cs[0].get("ja_text_before_rewrite") is not None:
                ja_t[r["d"]["instance_id"]].add(cs[0]["ja_text_before_rewrite"])
    return ({k: next(iter(v)) for k, v in en_t.items() if len(v) == 1},
            {k: next(iter(v)) for k, v in ja_t.items() if len(v) == 1})


# ---------------------------------------------------------------- 目視判定(13種類)
# key = claim先頭(委任_41 CSVの出現順にひも付ける)。art = 記事本文の該当箇所(逐語。実在をスクリプトが確認)。
MANUAL = OrderedDict()
MANUAL["U01"] = dict(
    key="“A call came from an AI agent. That was what it seemed. But while", lang="EN", main="C3",
    sub="C3b:説明文+断片2つ以上",
    secondary="C4:隣り合う2段落(冒頭段落と次段落)の結合",
    art=["A call came from an AI agent. That was what it seemed. But while the conversation continued, the voice on the other end was not AI. It was a person.",
         "Meta had run a test that produced exactly this kind of surprise."],
    diff="断片2つとも記事に逐語で存在(1つ目は先頭の“Ring, ring... ”を除いた段落、2つ目は文末ピリオドまで引用符内)。"
         "断片の間に、Checker自身の語「Meta’s test」が入っている(記事の語ではない。2つ目の断片の主語を補う説明)。言い換えはない。",
    cur_target="一部のみ(2断片中、冒頭段落だけ。2つ目の「Meta had run a test that produced exactly this kind of surprise.」は未変更)",
    prompt="見込める(断片は2つとも逐語。つなぎの説明語を入れず別々に返すだけ)",
    recv="断片分解は説明文(Meta’s test)が残るため不可(再推測)")
MANUAL["U02"] = dict(
    key="“people who thought they were speaking with AI were actually", lang="EN(つなぎ語のみ日本語)", main="C3",
    sub="C3b:説明文+断片2つ以上",
    secondary="C4:離れた2箇所(本文の中ほどの文と冒頭)の結合",
    art=["people who thought they were speaking with AI were actually speaking with human staff",
         "That was what people thought as they spoke."],
    diff="断片2つとも記事に逐語で存在・各1箇所。断片間が日本語の「および冒頭の」(=and the opening's、接続語+位置語)。"
         "英語の引用に日本語のつなぎ語が混ざっている(言語の混在)。断片自体の言い換えはない。",
    cur_target="一部のみ(1つ目の文は直したが、冒頭の「That was what people thought as they spoke.」は未変更。4/4 runで次周回に冒頭を同fact[MUSE-HC-012]で再指摘)",
    prompt="見込める(断片は逐語。つなぎを入れず2要素に分ければよい。英語claimに日本語のつなぎ語が出る点は現行Promptに書式指示が無いことの表れ)",
    recv="位置語「冒頭の」を許す=語彙リストを持つ再推測寄り。不可(Opus判断)")
MANUAL["U03"] = dict(
    key="“Trump’s proposed Hormuz fee vanished overnight.”", lang="EN", main="C2",
    sub="C2:末尾の句読点(読点→ピリオド)+文の途中で終了",
    secondary="",
    art=["Trump’s proposed Hormuz fee vanished overnight, but crude oil prices stayed high as tensions and tanker fears remained."],
    diff="記事は「…vanished overnight, but crude oil…」と続く。Checkerは「vanished overnight」で止め、読点の代わりにピリオドを引用符内に付けた。語は一字も違わない(末尾句読点のみの差)。",
    cur_target="一致(当該文のovernightの節を削除。現行はsequence_matcher ratio=0.51で当該文を選んだ)",
    prompt="見込める(末尾句読点の付加は癖。指示で抑えられる見込み。未測定)",
    recv="末尾句読点の除去で1箇所一致(文字単位の同値変換、可)")
MANUAL["U04"] = dict(
    key="Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14, so the flashy 20% plan left the stage.", lang="EN", main="C2",
    sub="C2:末尾の句読点(読点→ピリオド)+文の途中で終了",
    secondary="",
    art=["Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14, so the flashy 20% plan left the stage, but the chart only pulled back briefly before recovering"],
    diff="記事は「…left the stage, but the chart only pulled back…」と続く。Checkerは「left the stage」で止めて読点をピリオドに替えた。語の違いはない。",
    cur_target="一致(「so」を含むin one line文を直した。古いfixture、issue記録なし)",
    prompt="見込める(末尾句読点)",
    recv="末尾句読点の除去で1箇所一致(文字単位の同値変換、可)")
MANUAL["U05"] = dict(
    key="“attacks by the United States and Iran ... continued”", lang="EN", main="C4",
    sub="C4b:省略記号で中略(同一文内)",
    secondary="",
    art=["attacks by the United States and Iran, a sea blockade, and concerns about tanker safety continued"],
    diff="「...」が「, a sea blockade, and concerns about tanker safety」を省略している(同一文内の中略)。前後の断片(「attacks by the United States and Iran」「continued」)は逐語だが、「continued」単独は記事内に複数箇所ある。",
    cur_target="一致(当該文の攻撃に触れる部分を削除。古いfixture、issue記録なし)",
    prompt="見込めるが1件のみで確度は低い(「省略せず引用」を指示すれば解消する可能性。未測定)",
    recv="「A ... B」を『Aの先頭〜Aの後の最初のBの末尾』と読む決定論的解釈は可能だが、中略の標準解釈を使う判断であり同値変換とは言い切れない(Opus判断)")
MANUAL["U06"] = dict(
    key="“That was what people thought as they spoke.” The opening also", lang="EN", main="C3",
    sub="C3a:説明文+断片1つ",
    secondary="",
    art=["That was what people thought as they spoke."],
    diff="断片は記事の冒頭段落2文目に逐語で存在(1箇所)。続く「The opening also presents the call as one people believed was from an AI.」はChecker自身の説明文(記事の文ではない)。"
         "「also」「The opening」は、断片以外に冒頭段落(1〜3文目)全体も指している可能性がある(範囲が断片より広い恐れ)。",
    cur_target="一致(広め。冒頭の3文を1文に置き換えた。Stage 2のhint引用による)",
    prompt="見込めるが条件付き(説明文をissueへ移し範囲を配列で返せば解消。範囲が冒頭の1文か段落全体かはChecker自身が選び直す必要がある)",
    recv="断片だけの採用は不可(説明文が段落全体を指している可能性があり、範囲を縮小しうる)")
MANUAL["U07"] = dict(
    key="Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14, so the flashy 20% plan left the stage, but the chart only pulled back briefly before recovering.", lang="EN", main="C2",
    sub="C2:末尾の句読点(コロン→ピリオド)+文の途中で終了",
    secondary="",
    art=["Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14, so the flashy 20% plan left the stage, but the chart only pulled back briefly before recovering"],
    diff="記事は「…before recovering: the policy turn and the oil chart’s “not over yet” movement happened on the same day.」と続く。Checkerは「recovering」で止め、コロンをピリオドに替えた。語の違いなし(要約ではない。委任_41の「言い換え・要約」は類似度による診断の誤り)。"
         "固定fixture(bgroup_B3)のStage 1出力の再生で、20行は同一のChecker出力1件の再利用(独立サンプルではない)。",
    cur_target="一致(「so」の文を直した。issueが「so」を明記しており、直した箇所と一致)",
    prompt="見込める(末尾句読点の付加。ただし受け取り側の同値変換でPromptなしに解消できる)",
    recv="末尾句読点の除去で1箇所一致(文字単位の同値変換、可)")
MANUAL["U08"] = dict(
    key="The headline says “I Thought It Was an AI Call—But There Was a Person Inside?”", lang="EN", main="C3",
    sub="C3b:説明文+断片2つ以上",
    secondary="C4:見出しと冒頭(別の箇所)の結合",
    art=["I Thought It Was an AI Call—But There Was a Person Inside?", "A call came from an AI agent. That was what it seemed."],
    diff="断片2つとも記事に逐語で存在・各1箇所(見出しは「…Inside? Meta’s Unexpected Muse Test」の前半)。断片以外は位置ラベル(The headline says / and the opening says,)のみ。言い換えなし。",
    cur_target="一部のみ(冒頭の2文だけ直した。見出しは未変更。cycle3が最終でStage 4)",
    prompt="見込める(断片は逐語。位置ラベルをissueへ移すだけ)",
    recv="位置ラベルだけなら2断片が確定するが、ラベル語彙の判断が必要(Opus判断)。ラベルが範囲の拡大(見出し全体・冒頭段落全体)を意味する可能性を排除できない")
MANUAL["U09"] = dict(
    key="“Meta had run a test that caused exactly this surprise,”", lang="EN", main="C3",
    sub="C3b:説明文+断片2つ以上",
    secondary="C2:両断片とも末尾の句読点が記事と異なる(1つ目は読点、2つ目は見出しにない末尾ピリオド)",
    art=["Meta had run a test that caused exactly this surprise.", "We Thought It Was AI—But There Was a Person Inside Meta’s Muse"],
    diff="1つ目は記事が「…this surprise.」(ピリオド)、Checkerは「…surprise,」(読点を引用符内に付加)。2つ目は記事の見出しにピリオドがなく、Checkerが末尾にピリオドを付けた。"
         "つなぎの「reinforced by the headline」は説明文(位置+動詞)。",
    cur_target="一部のみ(1つ目だけ直した。見出しは未変更→次周回でMUSE-HC-006の見出しだけが単独で再指摘された)",
    prompt="見込める(句読点は引用符の外へ置く/付けない指示+別要素で返す)",
    recv="説明文が残るため断片分解は不可。末尾句読点の同値変換を断片に適用すれば各断片は逐語一致する")
MANUAL["U10"] = dict(
    key="Headline: “We Thought It Was AI—But There Was a Person Inside Meta’s Muse.”", lang="EN", main="C3",
    sub="C3a:説明文+断片1つ(位置ラベル「Headline:」のみ)",
    secondary="C2:見出しにない末尾ピリオドの付加",
    art=["We Thought It Was AI—But There Was a Person Inside Meta’s Muse"],
    diff="見出しの全文と一致(見出し行に末尾ピリオドなし)。Checkerは「Headline:」の位置ラベルと末尾ピリオドを付けた。ラベルが指す範囲=見出し全体で断片と同じ。",
    cur_target="判定不能(最終周回cycle3のため書き換え未実行。Stage 4 cycle_limit_exhausted)",
    prompt="見込める(位置ラベルをissueへ。末尾ピリオド付加の禁止)",
    recv="位置ラベル除去は再推測寄り(原則不可)。ただし本件は断片=見出し全体で、除去しても範囲は縮まない")
MANUAL["U11"] = dict(
    key="“Oil prices moved briefly, then returned to a high level.” The headline and one-line summary", lang="EN", main="C3",
    sub="C3a:説明文+断片1つ(説明文が未引用の2箇所を指す)",
    secondary="C4:未引用の追加箇所(見出し・in one line)を引用なしで示している",
    art=["Oil prices moved briefly, then returned to a high level.", "The Fee Plan Leaves, But High Oil Prices Stay", "The fee plan vanished, but oil prices stayed high as tensions around the Strait of Hormuz continued."],
    diff="断片は記事に逐語で存在(1箇所)。続く説明文「The headline and one-line summary also state this more broadly…」は、見出しとin one lineの2箇所を引用せず位置だけで指す。"
         "同じ指摘の`same_fact_id_locations`には両箇所の逐語文が入っていた(Checkerは別欄なら逐語で返せている)。断片だけを採ると範囲が3箇所から1箇所に縮む。",
    cur_target="一部のみ(本文の1文とin one lineは直したが、見出しは未変更。最終はStage 4 ja_deviation_unresolved、日本語側の問題も重なる)",
    prompt="見込めるが、見出し・in one lineの引用も別要素で返させる必要あり(同じ欄で返せるかは未測定。別欄の前例では逐語で返していた)",
    recv="断片だけの採用は不可(未引用の2箇所を落とし範囲を縮小する)")
MANUAL["U12"] = dict(
    key="“Oil prices moved briefly, then returned to a high level”; “oil prices stayed high”", lang="EN", main="C3",
    sub="C3b:説明文+断片2つ以上",
    secondary="C4:離れた2箇所(本文とin one line)+未引用の見出し",
    art=["Oil prices moved briefly, then returned to a high level", "oil prices stayed high"],
    diff="断片2つとも記事に逐語で存在(1つ目は文末ピリオドを除いたもの、2つ目はin one line内)。「; … (also reflected in the headline)」は説明文で、未引用の見出しを指す。",
    cur_target="一部のみ(本文の1文だけ直した。in one lineと見出しは未変更→次周回でその2箇所だけが再指摘された)",
    prompt="見込める(2断片は逐語。見出しも別要素で返せるかは未測定)",
    recv="説明文が未引用の見出しを含むため不可(範囲を縮小する)")
MANUAL["U13"] = dict(
    key="“High Oil Prices Stay” (headline); “oil prices stayed high” (one-line summary).", lang="EN", main="C3",
    sub="C3b:説明文+断片2つ以上",
    secondary="C4:見出しとin one line(別の箇所)の結合",
    art=["High Oil Prices Stay", "oil prices stayed high"],
    diff="断片2つとも記事に逐語で存在・各1箇所(見出しは「The Fee Plan Leaves, But High Oil Prices Stay」の末尾)。括弧内の位置ラベルは断片の実際の位置と一致。言い換えなし。",
    cur_target="一部のみ(in one lineだけ直した。見出しは未変更。cycle3が最終でStage 4)",
    prompt="見込める(断片は逐語。位置ラベルをissueへ移すだけ)",
    recv="位置ラベルが実際の位置と一致する場合に限りラベル語を許すなら確定する(語彙リスト=再推測寄り、Opus判断)")


def era(dn):
    if dn in ("iter5", "iter6", "iter7"):
        return "iter5-7(古い固定データ中心)"
    if dn in ("rep7", "rep8", "rep9", "rep10", "rep11", "rep12", "rep13", "rep16"):
        return "rep7-16"
    return "rep17以降/iter8"


def main():
    runs = load_runs()
    b_en, b_ja = borrow_map(runs)
    sel, nonblock, k2_disc, borrow_extra = [], [], [], []
    for run in runs:
        d = run["d"]
        cycles = d["cycles"]
        iid = d["instance_id"]
        for ci, c in enumerate(cycles):
            en, ja = cycle_texts(cycles, ci)
            en0, ja0 = en, ja
            if ci == 0:
                # 補助集計: cycle1本文が未記録のrunは、同一fixtureのcycle1本文(全run一致で1種類)を借用する。
                # 主集計(35行)には「照合に使う言語の本文が記録されている行」だけを入れ、
                # 借用した本文で初めて照合できた行はborrowed=Trueとして別枠(borrow_extra)で数える。
                en = en if en is not None else b_en.get(iid)
                ja = ja if ja is not None else b_ja.get(iid)
            nxt = cycles[ci + 1] if ci + 1 < len(cycles) else None
            for k, s in enumerate(c["stage2_results"]):
                dev = s["dev"]
                if s.get("detected_by") == "precheck" or dev.get("enumeration_source_claim"):
                    continue  # K3 / K2
                claim = (dev.get("claim_in_article") or "").strip()
                locs = dev.get("same_fact_id_locations")
                if isinstance(locs, list) and en is not None:
                    for loc in locs:
                        if isinstance(loc, str) and loc.strip() and loc.strip() != claim and loc.strip() not in en:
                            k2_disc.append((run["path"], c["cycle"], loc.strip(), resolve(loc.strip(), en)))
                if not claim:
                    continue
                if is_ja(claim) and ja is None:
                    continue
                if (not is_ja(claim)) and en is None:
                    continue
                res = []
                if en is not None:
                    res.append(resolve(claim, en))
                if ja is not None:
                    res.append(resolve(claim, ja))
                if not res:
                    continue
                if "ok" not in res and "multi" not in res:
                    borrowed = (en0 is None and not is_ja(claim)) or (ja0 is None and is_ja(claim))
                    rec = dict(borrowed=borrowed, run=run["path"], dir=run["dir"], inst=iid, cycle=c["cycle"], k=k, claim=claim,
                               mat=s["materiality"], res=res, en=en, ja=ja, d=d, c=c, nxt=nxt, s=s)
                    if borrowed:
                        borrow_extra.append(rec)
                    else:
                        (sel if s["materiality"] == "BLOCKING" else nonblock).append(rec)
    # --- 突き合わせ(委任_41のCSV)
    csv41 = list(csv.DictReader(open(os.path.join(HERE, "claims_detail_01.csv"), encoding="utf-8-sig")))
    ref = {(r["run"], r["cycle"], r["k"]) for r in csv41
           if r["kind"] == "K1" and r["materiality"] == "BLOCKING" and r["cat"] == "A4"}
    mine = {(r["run"], str(r["cycle"]), str(r["k"])) for r in sel}
    print("再抽出(BLOCKING確定不能)行数:", len(sel), "ユニーク:", len({r["claim"] for r in sel}))
    print("委任_41 CSV該当行数:", len(ref), " 差(自分のみ/CSVのみ):", len(mine - ref), len(ref - mine))
    nb_ref = {(r["run"], r["cycle"], r["k"]) for r in csv41
              if r["kind"] == "K1" and r["materiality"] != "BLOCKING" and r["cat"] == "A4"}
    nb_mine = {(r["run"], str(r["cycle"]), str(r["k"])) for r in nonblock}
    print("非BLOCKING確定不能: 自分", len(nb_mine), "CSV", len(nb_ref), "差", len(nb_mine ^ nb_ref))
    # --- 13種類へのひも付け
    order = [r["claim"] for r in csv41 if r["kind"] == "K1" and r["materiality"] == "BLOCKING" and r["cat"] == "A4"]
    uniq = OrderedDict((cl, None) for cl in order)
    assert len(uniq) == 13
    uid = {}
    for (u, m), cl in zip(MANUAL.items(), uniq.keys()):
        assert cl.startswith(m["key"]), (u, cl[:60])
        uid[cl] = u
    assert {r["claim"] for r in sel} == set(uid.keys())
    text_for = {}
    for r in sel:
        text_for.setdefault(uid[r["claim"]], r["en"])
    for u, m in MANUAL.items():
        for a in m["art"]:
            assert a in text_for[u], (u, a[:60])
    print("目視判定の記事該当箇所(13種類): すべて記事に逐語で実在(転記確認OK)")
    # --- 診断(範囲確定には使わない)
    diag = {}
    for cl, u in uid.items():
        en = text_for[u]
        st = None
        for o, c in PAIRS:
            if cl[0] == o and cl[-1] == c:
                st = cl[1:-1]
        base = (st if st is not None else cl).strip()
        stripped = base.strip(TRAIL)
        frags = [next(g for g in m.groups() if g is not None) for m in FRAG.finditer(cl)]
        fr = ["%d/%d" % (en.count(f.strip()), en.count(f.strip().strip(TRAIL))) for f in frags]
        ell = ""
        if "..." in cl or "…" in cl:
            parts = re.split(r"\s*(?:\.\.\.|…)\s*", base)
            ell = "+".join(str(en.count(p.strip(TRAIL))) for p in parts)
        diag[u] = "末尾句読点除去後の全体の記事内出現=%d; 引用断片の出現(そのまま/句読点除去後)=%s%s; 断片を除いた残り=%r" % (
            en.count(stripped) if stripped else 0, ",".join(fr) if fr else "なし",
            ("; 中略の前後断片の出現=" + ell) if ell else "", FRAG.sub("<断片>", cl)[:100])
    # --- 行ごと
    cols = ["row", "unique_id", "run", "dir", "era", "instance", "cycle", "k", "phase", "stage1_fixture_replay",
            "checker_lang", "claim", "article_nearest(逐語)", "diff", "main_class", "sub_class", "secondary_class",
            "diagnostic(自動・範囲確定には使わない)", "final_state", "stage4_reason", "rewrite_method",
            "current_target_judgement(目視)", "next_cycle_same_fact_reflag",
            "prompt_effect_estimate(見積もり、実測ではない)", "receiver_side_note"]
    out = []
    cnt_main, cnt_main_u = Counter(), defaultdict(set)
    sub_rows, sub_u = Counter(), defaultdict(set)
    judg, judg_u = Counter(), defaultdict(set)
    for i, r in enumerate(sel):
        u = uid[r["claim"]]
        m = MANUAL[u]
        d = r["d"]
        rr = r["c"].get("rewrite_records") or []
        bidx = [kk for kk, ss in enumerate(r["c"]["stage2_results"]) if ss["materiality"] == "BLOCKING"]
        meth = rr[bidx.index(r["k"])].get("method", "") if (len(rr) == len(bidx) and r["k"] in bidx) else ""
        if r["nxt"] is not None:
            fid = r["s"].get("related_fact_id")
            same = [x for x in r["nxt"]["stage2_results"]
                    if x["materiality"] == "BLOCKING" and x.get("related_fact_id") == fid]
            refl = "有(%d件)" % len(same) if same else "無"
        else:
            refl = "(次周回なし)"
        phase = "Stage1初回(cycle1)" if r["cycle"] == 1 else "Recheck(cycle%d)" % r["cycle"]
        replay = r["cycle"] == 1
        cur = m["cur_target"]
        jk = cur.split("(")[0]
        if u == "U07" and d["final_state"] == "STAGE4_ESCALATION":
            cur = "一致(ただし最終はStage 4 ja_deviation_unresolved。日本語側の別原因で、EN側の対象とは無関係)"
        judg[jk] += 1
        judg_u[jk].add(u)
        out.append([i + 1, u, r["run"], r["dir"], era(r["dir"]), r["inst"], r["cycle"], r["k"], phase,
                    "はい(固定fixtureのStage 1出力を再生)" if replay else "いいえ(Checker実出力)", m["lang"], r["claim"],
                    " || ".join(m["art"]), m["diff"], m["main"], m["sub"], m["secondary"], diag[u],
                    d["final_state"], d.get("stage4_reason") or "", meth, cur, refl, m["prompt"], m["recv"]])
        cnt_main[m["main"]] += 1
        cnt_main_u[m["main"]].add(u)
        sub_rows[m["sub"][:3]] += 1
        sub_u[m["sub"][:3]].add(u)
    with open(os.path.join(HERE, "unverified35_classification_01.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        w.writerows(out)
    print("主区分(行/ユニーク):", {k: (cnt_main[k], len(cnt_main_u[k])) for k in sorted(cnt_main)})
    print("細分(行/ユニーク):", {k: (sub_rows[k], len(sub_u[k])) for k in sorted(sub_rows)})
    print("区分の合計: 行", sum(cnt_main.values()), "ユニーク", sum(len(v) for v in cnt_main_u.values()))
    print("現行の対象一致判定(行/ユニーク):", {k: (judg[k], len(judg_u[k])) for k in judg})
    print("副区分(ユニーク種類):", dict(Counter(MANUAL[u]["secondary"][:2] or "なし" for u in uid.values())))
    runs_all = {r["run"] for r in sel}
    print("35行が属するrun数:", len(runs_all))
    print("記事別(行):", dict(Counter(r["inst"] for r in sel)))
    print("時期別(行):", dict(Counter(era(r["dir"]) for r in sel)), " 時期別(run):",
          dict(Counter(era(x.split("/")[0]) for x in runs_all)))
    print("初回(固定fixture再生)行/Recheck(実出力)行:", sum(1 for r in sel if r["cycle"] == 1),
          sum(1 for r in sel if r["cycle"] != 1))
    print("最終状態(行):", dict(Counter(r["d"]["final_state"] for r in sel)))
    run_final = {r["run"]: r["d"]["final_state"] for r in sel}
    print("最終状態(run):", dict(Counter(run_final.values())))
    run_j = defaultdict(set)
    for i, r in enumerate(sel):
        run_j[r["run"]].add(out[i][21].split("(")[0])
    print("run単位の目視判定(集合の種類別run数):", dict(Counter(tuple(sorted(v)) for v in run_j.values())))
    fin_by_j = Counter()
    for i, r in enumerate(sel):
        fin_by_j[(out[i][21].split("(")[0], r["d"]["final_state"])] += 1
    print("目視判定×最終状態(行):", dict(fin_by_j))
    print("補助(cycle1本文を同一fixtureから借用した行・主集計外):", [(r["run"], r["cycle"], r["mat"], r["claim"][:40]) for r in borrow_extra])
    print("--- 非BLOCKING確定不能", len(nonblock))
    for r in nonblock:
        print("   ", r["run"], r["cycle"], r["mat"], "|", r["claim"][:150].replace("\n", " "))
    print("--- K2で捨てられたsame_fact_id_locations", len(k2_disc))
    seen, n = set(), 0
    for run, cy, loc, res in k2_disc:
        if (run, cy, loc) in seen:
            continue
        seen.add((run, cy, loc))
        n += 1
        print("   ", n, run, cy, res, "|", loc[:140])
    print("K2捨て(重複除外):", n)


if __name__ == "__main__":
    main()
