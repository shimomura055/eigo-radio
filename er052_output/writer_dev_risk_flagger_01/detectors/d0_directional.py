# -*- coding: utf-8 -*-
"""D0 決定論・方向語/不在断定cue/数量の検出器(API不要・費用0円)。DEV専用Risk Flagger。
Flagを立てるだけ。合否判定しない・Rewriteしない・自動修正しない。
入力unit: dict(unit_id, facts=[{fact_id,text}], sentences=[{sid,text,before,after}])
出力: Flag(dict)のlist。

委任_02 P0(Opus条件Aレビュー反映)での変更:
 - R語彙から『the way it had been』を削除。K01(rf_y84g5r)は語彙設計時に参照した『回帰テスト(汚染済み)』であり、
   D0の汎化証拠からは除外する(casebank/設計書に明記)。
 - 英語語の照合を『語境界+活用語尾のみ許容』へ(『block』が『blockade』に当たる等の前方一致誤マッチを修正)。
 - 文×Factの対応付けを『方向語を含む文 × 方向語を含むFact』の総当たり(言語をまたぐ)へ。casebank(英文×日本語台帳)でも
   記事モードでも同じ規則。重なり(固有名詞・数値)は確信度の加点のみに使う。1文×1グループにつき1Flag(fact_idsに複数列挙)。
 - Flagに gate_only を付与。和集合(D3)に入れてよいのは rollback反転 のみ(gate_only=False)。
   不在断定・数量時系列・増減反転・許可禁止反転は『D1呼び出しのゲート用』に格下げ(gate_only=True)。
 - 一般否定(did not / has not / never 等)をABSENCE_CUESから外した(誤Flag構造)。
"""
import re

# 方向語グループ。side "W"=撤回・停止・巻き戻し側 / "R"=復元・再開・元に戻す側。
GROUPS = {
    "rollback反転": {
        "W": ["ロールバック", "撤回", "停止", "中止", "取り下げ", "取りやめ", "取り止め", "見送り", "無効化", "凍結",
              "廃止", "撤廃", "差し戻し", "巻き戻", "棚上げ", "一時停止", "打ち切り",
              "roll back", "rolled back", "rollback", "rolling back", "withdraw", "withdrew", "withdrawn", "suspend",
              "halt", "pause", "cancel", "revoke", "scrap", "put on hold", "on hold", "shelve", "discontinue",
              "disable", "deactivate", "pull the plug", "walked back", "walk back", "called off", "backed out"],
        "R": ["復元", "復活", "再導入", "再開", "元に戻", "以前の状態", "もとに戻", "復旧", "再有効", "再び有効",
              "再稼働", "戻しました", "戻した", "戻す", "再掲", "再投入",
              "restore", "restored", "restoring", "put back", "putting back", "reinstate", "reinstated",
              "bring back", "brought back", "resume", "resumed", "reintroduce", "re-introduce", "re-enable",
              "reenable", "reactivate", "relaunch", "reopen", "back to normal",
              "went back to", "returned to", "revert"],
    },
    "増減反転": {
        "W": ["減少", "低下", "下落", "縮小", "引き下げ", "値下げ", "削減", "急落", "減った", "下がった",
              "decrease", "decline", "fell", "drop", "reduce", "lower", "shrink", "shrank"],
        "R": ["増加", "上昇", "拡大", "引き上げ", "値上げ", "増額", "急騰", "増えた", "上がった",
              "increase", "rise", "rose", "grew", "grow", "raise", "higher", "expand", "surge"],
    },
    "許可禁止反転": {
        "W": ["禁止", "却下", "否決", "拒否", "不許可", "認めない", "ban", "prohibit", "reject",
              "deny", "denied", "forbid", "block", "refuse"],
        "R": ["許可", "承認", "可決", "認める", "認めた", "解禁", "解除", "allow", "permit", "approve",
              "authorize", "lift", "legalize"],
    },
}
# 日本語は部分一致、英語は『語境界+活用語尾(s/es/ed/d/ing/ned/ning/ped/ping)のみ』許容(前方一致の誤マッチ防止)

ABSENCE_CUES = [
    "公表されていない", "明らかにされていない", "確認されていない", "報告されていない", "存在しない", "起きていない",
    "一度もない", "まだない", "示されていない", "分かっていない", "わかっていない", "判明していない",
    "not been made public", "has not been reported", "have not been reported", "has not reported", "have not reported",
    "no one has", "nobody has", "no evidence", "not yet", "nor has", "nor have", "not reported",
    "undisclosed", "not disclosed", "not been disclosed", "has never", "have never",
]  # 一般否定(did not / has not 単独 / never 単独 / なかった)は誤Flag構造のため外した(Opus所見7)

_STOP_EN = set("the a an of to in on at for and or but is are was were be been it its this that these those with as by from "
               "their his her they he she we you i not no has have had will would can could may might also than then "
               "there about into over after before during under which who whom what when where why how more most".split())
_EN_SUFFIX = r"(?:s|es|ed|d|ing|ned|ning|ped|ping)?"
_num_re = re.compile(r"\d[\d,]*\.?\d*")
_cap_re = re.compile(r"\b[A-Z][A-Za-z0-9\-]{2,}\b")
_ja_tok_re = re.compile(r"[ァ-ヴー]{2,}|[一-龥]{2,}|[A-Za-z][A-Za-z0-9\-]{2,}")


def _norm(s):
    return (s or "").replace("　", " ").lower()


def side_hits(text, group):
    """textに含まれるW/R側の語。戻り値 dict(W=[...], R=[...])。"""
    t = _norm(text)
    out = {"W": [], "R": []}
    for side in ("W", "R"):
        for w in GROUPS[group][side]:
            wl = w.lower()
            if re.search(r"[a-z]", wl):
                if re.search(r"(?<![a-z])" + re.escape(wl) + _EN_SUFFIX + r"(?![a-z])", t):
                    out[side].append(w)
            elif wl in t:
                out[side].append(w)
    return out


def numbers(text):
    res = set()
    for m in _num_re.findall(text or ""):
        m = m.replace(",", "").rstrip(".")
        if m:
            res.add(m)
    return res


def content_tokens(text):
    """固有名詞・数値・カタカナ/漢字語・英単語(非ストップ)の集合。文とFactの対応付けの近似用。"""
    toks = set()
    for m in _cap_re.findall(text or ""):
        toks.add(m.lower())
    for m in _ja_tok_re.findall(text or ""):
        m = m.lower()
        if m not in _STOP_EN:
            toks.add(m)
    toks |= {"#" + n for n in numbers(text)}
    return toks


def overlap_score(sentence, fact):
    a, b = content_tokens(sentence), content_tokens(fact)
    if not a or not b:
        return 0.0
    return len(a & b) / float(min(len(a), len(b)))


def map_facts(sentence, facts, top_k=3, min_score=0.0):
    """文に最も近いFactを top_k 件返す: [(score, fact)]。固有名詞・数値の重なりで近似(0円)。"""
    scored = sorted(((overlap_score(sentence, f["text"]), f) for f in facts), key=lambda x: -x[0])
    return [(s, f) for s, f in scored[:top_k] if s >= min_score]


def _mk(unit, sent, typ, fact_ids, conf, severity, question, basis, gate_only, detector="d0"):
    return dict(unit_id=unit["unit_id"], sentence_id=sent["sid"], sentence=sent["text"], type=typ,
                fact_ids=list(fact_ids), confidence=round(conf, 2), severity=severity, question=question,
                basis=basis, detector=detector, gate_only=gate_only)


def any_direction_word(text):
    """文にどのグループの方向語が1つでも含まれるか(D1ゲート用。ラベル・Factは使わない)。"""
    return any(side_hits(text, g)[s] for g in GROUPS for s in ("W", "R"))


def ledger_numbers(facts):
    nums = set()
    for f in facts:
        nums |= numbers(f["text"])
    return nums


def detect(unit, top_k=3, align_min=0.15):
    """unit内の全文を走査してFlagを返す(casebank・記事とも同じ規則)。overlapは確信度の加点にのみ使う。"""
    flags = []
    facts = unit["facts"]
    fact_side = {g: {f["fact_id"]: side_hits(f["text"], g) for f in facts} for g in GROUPS}
    fnums_all = ledger_numbers(facts)
    for sent in unit["sentences"]:
        text = sent["text"]
        for group in GROUPS:
            sh = side_hits(text, group)
            if not (sh["W"] or sh["R"]) or (sh["W"] and sh["R"]):
                continue  # 方向語なし、または文中で両側が共存(曖昧)はスキップ
            want = "W" if sh["R"] else "R"  # 文がR側ならFactはW側のみ、文がW側ならFactはR側のみ
            other = "R" if want == "W" else "W"
            hit_facts = []
            for f in facts:
                fh = fact_side[group][f["fact_id"]]
                if fh[want] and not fh[other]:
                    hit_facts.append((overlap_score(text, f["text"]), f, fh))
            if not hit_facts:
                continue
            hit_facts.sort(key=lambda x: -x[0])
            best_score, best_f, best_fh = hit_facts[0]
            conf = 0.65 if best_score >= align_min else 0.45
            rollback = group == "rollback反転"
            typ = "rollback反転" if rollback else "その他"
            sw = sh[other]
            wname = "停止・撤回・減少・禁止"
            rname = "復元・再開・増加・許可"
            flags.append(_mk(
                unit, sent, typ, [f["fact_id"] for _s, f, _h in hit_facts[:top_k]], conf, "重大",
                "台帳Factは『%s』(%s側)と書いていますが、この文は『%s』(%s側)と読めます。向きは台帳どおりですか。" % (
                    ",".join(best_fh[want][:2]), wname if want == "W" else rname,
                    ",".join(sw[:2]), rname if want == "W" else wname),
                "dir:%s fact_side=%s sent=%s n_facts=%d best_align=%.2f" % (group, want, sw[:3], len(hit_facts), best_score),
                gate_only=not rollback))
        # 不在断定cue
        tl = " " + _norm(text) + " "
        hits = [c for c in ABSENCE_CUES if c.lower() in tl]
        if hits:
            ranked = sorted(((overlap_score(text, f["text"]), f) for f in facts), key=lambda x: -x[0])[:1]
            flags.append(_mk(unit, sent, "不在断定", [f["fact_id"] for _s, f in ranked], 0.35, "重大",
                             "この文は『ない・未公表』と断定しています。台帳にその不在を支える記述はありますか(台帳の記述と食い違っていませんか)。",
                             "absence_cue=%s" % hits[:3], gate_only=True))
        # 数量: 文中の数値が台帳全体のどのFactにもない
        sn = numbers(text)
        extra = sorted(n for n in sn if n not in fnums_all and len(n) >= 2)
        if extra and fnums_all:
            flags.append(_mk(unit, sent, "数量時系列", [], 0.3, "重大",
                             "文中の数値(%s)が台帳のどのFactにもありません。数量・日付は台帳どおりですか。" % ",".join(extra[:3]),
                             "numbers_not_in_ledger=%s" % extra[:3], gate_only=True))
    return flags


def gate_types(unit):
    """D1全5タイプのうち、D0のラベル不使用ゲートで呼び出す対象タイプ(規則は設計書に事前登録)。
    主体対象入替・否定反転 = 常に呼ぶ(決定論の手がかりが作れない) / rollback反転 = いずれかの文に方向語 /
    不在断定 = いずれかの文に不在cue / 数量時系列 = いずれかの文に数値。"""
    types = {"主体対象入替", "否定反転"}
    for sent in unit["sentences"]:
        t = sent["text"]
        if any_direction_word(t):
            types.add("rollback反転")
        tl = " " + _norm(t) + " "
        if any(c.lower() in tl for c in ABSENCE_CUES):
            types.add("不在断定")
        if numbers(t):
            types.add("数量時系列")
    return types
