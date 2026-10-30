# -*- coding: utf-8 -*-
"""KP-GENERALIZATION-N5-PRODUCTION-WIRING-01 委任_02: Key Phrase一般化 N5方式の正式Production module(ユーザー正式決定 2026-10-30
APPROVED_FOR_PRODUCTION、Trial 03 方式B=N5。原文=docs/pm/delegation_log/2026-10-30_KP-GENERALIZATION-N5-PRODUCTION-WIRING-01_USER.md)。

N5 = B1過剰生成(luna) -> SEL(塊価値判定、luna) -> pick(cap7) -> GEN5(意味確定先行の一般化、luna) -> VER5(別系列検証、gemini-3.8-flash)
     -> CHK5(別系列独立検査・revertされていない全件、gpt-6.1-sol)。Trial確定版(docs/research/KP-GENERALIZATION-MEANING-PRESERVATION-TRIAL-03/kpg04_methods.py の
     ARMS["N5"])のPrompt本文・schema・工程順・判定条件・閾値・max_out/think_budget/effort・revert/fix規則を**改変せず**移植した。Trial codeはimportしない
     (Trial専用のCap/台帳/phase/SALT/mock/cache keyは移植しない)。移植時に変えたのは: 入出力の型変換、LLM呼出基盤(Production用: routing contract・
     cost loggerのstageタグ・model照合・stop_check_fn)、Trial cache key算出の撤去、span_glossのPROD_GLOSS入力の渡し方(case['before']->item['prod_gloss'])のみ。
     Prompt等の同一性は回帰test(er138_kp_n5_generalization_01_test_01.py)がTrialのcache keyの再計算一致で実入力に対して証明する。

配線(er119_kp_candidates_01、X/Y/Z共通の1配線点): L1 = call1(P7)直後に B1過剰生成∪P7 -> 既存Gate -> SEL -> pick(`pool_and_select`)。
L3 = `_gate_chain`内でcanonicalization直後(CMU post-canonの前)に GEN5->VER5->CHK5(`run_l3` + `apply_to_item`)。補完(backfill)も同じ`_gate_chain`を通る。
既定ON・flagなし・kill switchなし(撤退手段=導入commitの単一git revert。N5段の失敗はSTOP/外側retry=N5なしの候補を出さない)。
対象はフレーズ(kind=phrase)のみ。単語(W5')はTrial未検証のため対象外(現状維持)。Prompt/閾値/規則の変更にはユーザー承認が必要(ここへ新Gate・Prompt改善を足さない)。
"""
from __future__ import annotations

import contextlib
import hashlib
import json
import os
import re
import sys
import threading
import time
import types
from typing import Any, Callable, Optional

import er105_kp_fulltext_selector_01 as ft      # FulltextSelectionError(STOP伝播の既存基底)・count_words・validate_and_resolve等

HERE = os.path.dirname(os.path.abspath(__file__))
METHOD_ID = "N5@T3-2026-10-30"
TRIAL_SOURCE = "docs/research/KP-GENERALIZATION-MEANING-PRESERVATION-TRIAL-03/kpg04_methods.py ARMS['N5']"

# ---- モデル・呼出パラメータ(Trial確定版と同一。変更はユーザー承認事項) ----
SOL, LUNA, GEM = "gpt-6.1-sol", "gpt-6-luna", "gemini-3.8-flash"
STAGE_PARAMS = {
    "b1":   {"model": LUNA, "max_out": 6000, "effort": None,  "think_budget": None},
    "sel":  {"model": LUNA, "max_out": 7000, "effort": None,  "think_budget": None},
    "gen5": {"model": LUNA, "max_out": 9000, "effort": None,  "think_budget": None},
    "ver5": {"model": GEM,  "max_out": 6000, "effort": None,  "think_budget": 0},
    "chk5": {"model": SOL,  "max_out": 3500, "effort": "low", "think_budget": None},
}
# routing contractのprocess(luna段は呼出元のA2_SUPPORT/B1_SUPPORT[=SUPPORT_MODEL]、別系列2段は専用process)
STAGE_PROCESS = {"b1": None, "sel": None, "gen5": None, "ver5": "KP_N5_VERIFY", "chk5": "KP_N5_CHECK"}
PHRASE_PICK_CAP = 7             # Trial run_N(cap=7)=P7最大件数と同じ
MAX_ATTEMPTS = 2                # 技術失敗のretry(er105.MAX_ATTEMPTS / er119_kp_difficulty と同じ既存上限。独自に増減しない)
JSON_TRUNCATION_MAX_OUT_FACTOR = 1.6    # Trial確定版: JSON途切れ(出力上限到達)は1回だけmax_outを1.6倍にして再試行
MAX_WORDS = 5                   # 承認済み制約(5語以下)。N5形used_formにも既存ft.count_wordsで適用(Opus M6)
# bf.NOT_COUNTED_STAGES(Eに数えない段)へ入れる段名(Opus M3)。Eに数えるのは「pick後に失われた候補」(n5_generalize/n5_verify/n5_check)のみ
STAGE_POOL, STAGE_SELECT, STAGE_PICK = "n5_pool", "n5_select", "n5_pick"
STAGE_GENERALIZE, STAGE_VERIFY, STAGE_CHECK = "n5_generalize", "n5_verify", "n5_check"
NOT_COUNTED_N5_STAGES = (STAGE_POOL, STAGE_SELECT, STAGE_PICK)
N5_NORMALIZATION_REASON = "n5_generalization"


class N5Error(RuntimeError):
    """N5段の失敗の基底。"""


class N5TechnicalFailure(N5Error):
    """通信等の技術失敗(retry上限到達)。呼出側(er119_kp_candidates)は外側retryへ接続する(N5なしの候補は出さない=fail-closed)。"""


class N5ContractError(ft.FulltextSelectionError):
    """routing違反・actual model不一致・WordNet欠落/改変・単価未登録など、retryで直らない契約違反(STOP)。
    ft.FulltextSelectionErrorを継承するため既存のbf.is_propagating_exceptionで握られず伝播し、runnerは[STOP] rc=2で停止する(自動retry・N5なし続行なし)。"""



# ============================================================
# Trial確定版の決定論部品・Prompt本文(verbatim移植。Prompt本文/schema/規則は一字も変えない。同一性はTrial cache keyの再計算一致で回帰testが証明する)
# 出典: docs/research/KP-GENERALIZATION-CHUNK-VALUE-TRIAL-01/kpg01_validate.py ・ -01/kpg01_gen2.py ・ -01/kpg01_methods.py ・ -02/kpg03_methods.py ・
#       docs/research/KP-GENERALIZATION-MEANING-PRESERVATION-TRIAL-03/kpg04_methods.py
# ============================================================

PLACE = {"something", "someone", "somebody", "one's", "someone's", "somebody's", "oneself", "somewhere", "one", "sth", "sb"}

def norm(s):
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').replace("—", " ").replace("–", "-")
    return s

def toks(s):
    s = norm(s).lower()
    return [t.strip(".,;:!?\"()[]*#") for t in re.split(r"\s+", s) if t.strip(".,;:!?\"()[]*#")]

def span_in_text(span, text):
    ts, tt = toks(span), toks(text)
    n = len(ts)
    if n == 0: return False
    return any(tt[i:i + n] == ts for i in range(len(tt) - n + 1))

def same_word(a, b):
    if {a.lower(), b.lower()} == {"a", "an"}:    # 冠詞a/anの音韻的交替は同一語とみなす
        return True
    return bool(lemmas(a) & lemmas(b))

def display_check(display, span):
    """returns (ok, reasons)。displayの非プレースホルダ語がspanの語の語形違いで、かつ順序どおり(部分列)。"""
    reasons = []
    d, s = toks(display), toks(span)
    if not (1 <= len(d) <= 5): reasons.append(f"display語数{len(d)}")
    core = [t for t in d if t not in PLACE]
    if not core: reasons.append("核語なし")
    j = 0
    for t in core:
        found = False
        while j < len(s):
            if same_word(t, s[j]): found = True; j += 1; break
            j += 1
        if not found:
            reasons.append(f"核語'{t}'がsource_span由来でない/順序違い")
            break
    npl = sum(1 for t in d if t in PLACE)
    if npl > 2: reasons.append("プレースホルダ3個以上")
    unmatched = [t for t in s if t not in ("a", "an", "the") and not any(same_word(t, c) for c in core)]
    # 本文に目的語が現れない(受動・省略)句動詞等のため、表現の途中(先頭・末尾でない位置)に限りプレースホルダを1個まで追加できる
    internal_extra = 0
    if npl > len(unmatched):
        idx = [i for i, t in enumerate(d) if t in PLACE]
        internal_extra = sum(1 for i in idx if 0 < i < len(d) - 1)
    if len(d) >= 3 and d[-1] in PLACE and d[-2] in PREPS: reasons.append("前置詞の後ろに末尾プレースホルダが残る")
    if npl > len(unmatched) + min(1, internal_extra): reasons.append(f"プレースホルダ{npl}個が本文の置換語{len(unmatched)}個を超える")
    if re.search(r"[~〜…　-鿿]", display): reasons.append("記号/日本語混入")
    return (not reasons), reasons

PREPS = {"for", "of", "to", "from", "with", "on", "in", "at", "by", "into", "as", "about", "over", "up", "down", "out", "off", "through", "around", "away", "back"}

def strip_trailing_slot(display):
    """末尾のプレースホルダを決定論で除去(直前が前置詞/粒子の場合のみ)。例: 'make room for something' -> 'make room for'。"""
    t = display.split()
    if len(t) >= 3 and t[-1].lower() in PLACE and t[-2].lower() in PREPS:
        return " ".join(t[:-1])
    return display


# ============================================================
# WordNet(Trial T1/nltk_dataは未追跡=Productionへtracked資産としてvendoring。SEL Promptの「WordNet複合語見出し」ヒントとdisplay_check/revert_formが使う)
# 欠落・sha不一致・読込失敗はfail-closed(N5ContractError=STOP。N5なし/別辞書で続行しない)。NLTKのWordNet(zip)はthread非安全のためRLockで全アクセスを直列化(Trialと同一)。
# ============================================================
WORDNET_DIR = os.path.join(HERE, "data", "nltk_data")
WORDNET_ZIP = os.path.join(WORDNET_DIR, "corpora", "wordnet.zip")
WORDNET_SHA256 = "cbda5ea6eef7f36a97a43d4a75f85e07fccbb4f23657d27b4ccbc93e2646ab59"       # 回帰testで固定。出典=NLTK wordnet corpus(Princeton WordNet 3.0、ライセンス=https://wordnet.princeton.edu/license-and-commercial-use)
_WN_LOCK = threading.RLock()
_WN = None


def _wn():
    """検証済みWordNet corpus readerを返す(初回のみsha256照合・読込)。失敗はN5ContractError。"""
    global _WN
    if _WN is not None:
        return _WN
    with _WN_LOCK:
        if _WN is not None:
            return _WN
        if not os.path.exists(WORDNET_ZIP):
            raise N5ContractError(f"WordNet資産が見つかりません({WORDNET_ZIP})。N5はWordNetなしで続行しません(fail-closed)")
        h = hashlib.sha256()
        with open(WORDNET_ZIP, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        if h.hexdigest() != WORDNET_SHA256:
            raise N5ContractError(f"WordNet資産のsha256が固定値と一致しません(実際: {h.hexdigest()[:16]}…)。改変/破損の疑い(fail-closed)")
        try:
            import nltk
            nltk.data.path.insert(0, WORDNET_DIR)
            from nltk.corpus import wordnet as wn
            if not wn.synsets("take"):
                raise RuntimeError("synsets('take')が空")
        except N5ContractError:
            raise
        except Exception as e:      # noqa: BLE001
            raise N5ContractError(f"WordNetを読み込めません(fail-closed): {type(e).__name__}: {e}") from e
        _WN = wn
        return _WN


def _lemmas_base(tok):
    wn = _wn()
    t = tok.lower().replace("'s", "")
    out = {t}
    for pos in ("v", "n", "a", "r"):
        m = wn.morphy(t, pos)
        if m:
            out.add(m)
    if t.endswith("ing") and len(t) > 5:
        out.add(t[:-3])
        out.add(t[:-3] + "e")
    return out


def lemmas(tok):
    """Trial kpg02_methods._lemmas_plus(+WordNet lock)と同一: 基本のlemma + 名詞複数形の補正(WordNet morphyが'sales'を'sale'と一致させない問題)。"""
    with _WN_LOCK:
        out = set(_lemmas_base(tok))
        t = tok.lower().replace("'s", "")
        if t.endswith("ies") and len(t) > 4:
            out.add(t[:-3] + "y")
        elif t.endswith("es") and len(t) > 3:
            out.add(t[:-2])
        if t.endswith("s") and len(t) > 3:
            out.add(t[:-1])
        return out


def wn_multiword(display):
    """WordNetに複合語見出しがあるか(冠詞除去/the,a挿入/末尾前置詞除去の変形を試す)。supporting signalのみ(None=単語/判定不能)。(Trial kpg01_validate.wn_multiword + lock)"""
    with _WN_LOCK:
        wn = _wn()
        core = [t for t in toks(display) if t not in PLACE and t not in ("a", "an", "the")]
        if len(core) < 2:
            return None
        preps = {"for", "of", "to", "from", "with", "on", "in", "at", "by", "into", "as"}
        variants = [core]
        if core[-1] in preps and len(core) > 2:
            variants.append(core[:-1])
        for v in list(variants):
            for pos in ("v", "n"):
                m = wn.morphy("_".join(v), pos)
                if m and wn.synsets(m):
                    return True
            if wn.synsets("_".join(v)):
                return True
            for art in ("the", "a"):
                for i in range(1, len(v)):
                    if wn.synsets("_".join(v[:i] + [art] + v[i:])):
                        return True
            for i, t in enumerate(v[:1]):
                for l in lemmas(t):
                    if wn.synsets("_".join([l] + v[1:])):
                        return True
        return False


def _contains(a, b):
    """Trial kpg01_methods2._contains(span包含: 一方が他方のtoken部分列)。"""
    ta, tb = toks(a), toks(b)
    n, m = len(ta), len(tb)
    return any(ta[i:i + m] == tb for i in range(n - m + 1)) or any(tb[i:i + n] == ta for i in range(m - n + 1))


# 節の断片(関係詞・疑問詞で始まる/前置詞+関係詞を含む形)は塊として不可(決定論。Trial kpg02_methods.FRAG)
FRAG = re.compile(r"^(whose|which|what|who|whom|where|when|whether|that|how)\b|\b(at|in|on|of|to|for|with|by)\s+(which|whom|whose)\b", re.I)



V = types.SimpleNamespace(norm=norm, toks=toks, span_in_text=span_in_text, lemmas=lemmas, same_word=same_word, display_check=display_check,
                          wn_multiword=wn_multiword, strip_trailing_slot=strip_trailing_slot, PLACE=PLACE)


LABELS = ["CORE", "SLOT_THING", "SLOT_PERSON", "SLOT_POSS_SELF", "SLOT_POSS_OTHER", "DROP"]

GEN2_RULES = """## 学習用の一般形づくり(トークン分類)
各候補の語句は番号付きトークンに分けてあります。**各トークンを次のどれかに分類**してください(語を書き換えたり足したりしません)。
- CORE: 学習する表現の核。動詞、固定の前置詞・粒子、表現の一部として固定された名詞・形容詞・冠詞。lemmaに辞書の見出し語形(動詞は原形、名詞は単数。活用・複数・時制を消した形。変えない語はそのまま)を書く。
- SLOT_THING: 自由に入れ替わる『物・事』の語(本文固有の目的語・主語)。連続するSLOTは1つのsomethingにまとめられる。lemmaは空文字。
- SLOT_PERSON: 自由に入れ替わる『人』を指す語(目的格の代名詞he/him/her/it(人)など)。someoneになる。lemmaは空文字。
- SLOT_POSS_SELF: 動作主自身を指す所有格(his/her/their/my...)。one'sになる。
- SLOT_POSS_OTHER: 動作主とは別の人の所有格。someone'sになる。
- DROP: 一般形から除く語(本文固有の修飾語・文脈語・省略しても成立する目的語・固定表現の後ろに続く名詞句や動名詞)。
判断の原則:
1. 核と可変部を区別する。**入替テスト**: その名詞を、意味の違う無関係な別の名詞(例: money、plans、people。同義語ではない)に替えても、同じ構文で自然に成り立ち、表現の意味(本文の語義)も変わらないなら、その名詞は自由に入れ替わる可変部=SLOT_THING(学習者用英英辞書ではsomethingと書かれる部分)。替えると意味が変わる/成り立たない(動詞とその名詞が慣用的に結びついている)ならCORE(例: set the record straight、pull strings、open the floodgates、動詞とセットで見出しになる連語の名詞)。**表現の骨格の見つけ方**: 表現の骨格は『動詞+粒子/前置詞』または『慣用句全体』である。動詞+粒子/前置詞が1つのまとまり(句動詞・前置詞付き動詞)で、その間や後ろに本文の具体的な対象(目的語名詞)が挟まっているだけなら、その名詞は可変部=SLOT_THING(例: "keep the costs down" -> keep=CORE, costs=SLOT_THING, down=CORE => keep something down、"get the plan off the ground" -> get something off the ground)。一方、名詞が動詞と結びついて初めて意味が出る連語・慣用句(break the ice、take place、pay attention to、draw a conclusion)では名詞をCOREにする。動詞と名詞の組合せが、その名詞に限らず他の名詞でも通じる一般的な動作(make、take、get、put、keepなどの軽い動詞+対象)なら、骨格は動詞+粒子/前置詞側と考える。
**名詞をCOREに残すのは、『他の無関係な名詞に替えるとその言い回しの意味が失われる』場合だけ**。『本文では比喩的に聞こえる』『本文の語義に必要に見える』『文脈上その名詞が重要』は残す理由にならない(本文の語義は日本語の意味gloss_jaとsense_note_jaで補う。一般形が本文の語義を包含する、より汎用的な項目になるのは意図どおりであり、許容される)。**迷ったらSLOT_THINGにする**。名詞をCOREに残したときは、note_jaに『なぜ他の名詞では成り立たないか』を書く。
2. 目的語を省いても成立する句動詞・前置詞付き動詞(例: tighten up the rules)は、目的語をDROPにして核だけを残す。目的語を表現の途中に挟まないと動詞の意味が成立しない場合(例: walk someone through、give something up)だけSLOTにする。
3. **前置詞・粒子で終わる形が見出しとなる表現(in the event of / by the end of / on the verge of)では、その後ろに続く本文固有の名詞句・動名詞は必ずDROP**(後続に名詞句を取る表現でも、学習用の表示では核を明確にする)。末尾にSLOTを置かない。
4. 必要な前置詞・粒子・補語(depend onのon、lead toのto)はCOREのまま残す。5. **意味を変える一般化は禁止**(本文での語義を保てない分類にしない)。複数の語義がある表現は本文での語義をsense_note_jaに書く。
6. 例(分類のしかたの例。別の表現): walked her through the steps -> walked=CORE(walk), her=SLOT_PERSON, through=CORE, the=DROP, steps=DROP => walk someone through / in the event of a delay -> in,the,event,of=CORE, a=DROP, delay=DROP => in the event of / tightened up the rules -> tightened=CORE(tighten), up=CORE, the=DROP, rules=DROP => tighten up。
gloss_ja: **一般形(DROP/SLOTにした語を除いた形)と同じ抽象度**で、本文での意味(語義)を日本語で簡潔に(20字程度)。DROPした語・SLOTにした語の意味をglossに含めない(例: in the event of a delay -> 『〜の場合には』、walk someone through -> 『(人)に〜を順に説明する』)。本文固有の具体的な名詞をglossに残さない。sense_note_ja: 本文での語義(30字以内)。note_ja: 何を核とし何を可変部としたか(40字以内)。"""

def tokenize(span):
    return [t for t in re.split(r"\s+", V.norm(span).strip()) if t]

def assemble(span, tokens):
    """トークン分類 -> display_form(決定論)。returns (display_form, error|None)。"""
    sp = tokenize(span)
    if sorted(t["n"] for t in tokens) != list(range(1, len(sp) + 1)):
        return None, "トークン番号の欠落/重複"
    by = {t["n"]: t for t in tokens}
    out, prev_slot = [], None
    for n, surf in enumerate(sp, 1):
        t = by[n]
        lab = t["label"]
        if lab == "DROP":
            continue
        if lab == "CORE":
            lem = (t["lemma"] or surf).strip().lower() if surf.lower() != "i" else "I"
            lem = re.sub(r"[^\w'\- ]", "", lem)
            if not V.same_word(lem.split()[0] if lem else surf, surf) and lem != surf.lower().strip(".,;:!?\"()"):
                return None, f"lemma'{lem}'が本文の語'{surf}'の語形違いでない"
            out.append(lem)
            prev_slot = None
        else:
            ph = {"SLOT_THING": "something", "SLOT_PERSON": "someone", "SLOT_POSS_SELF": "one's", "SLOT_POSS_OTHER": "someone's"}[lab]
            if prev_slot == ph:
                continue
            out.append(ph)
            prev_slot = ph
    return V.strip_trailing_slot(" ".join(out)), None


G = types.SimpleNamespace(LABELS=LABELS, GEN2_RULES=GEN2_RULES, tokenize=tokenize, assemble=assemble)


BODY = "\n\n---\n\n【記事本文】\n"

# ---- Productionの難易度優先条件(P7条件4・5を逐語維持) ----
PROD_DIFFICULTY = ("4. **上級者向けの学習価値**：上級者でも学ぶ価値のある語彙・イディオム・慣用表現を優先する。\n"
                   "5. **易しい表現の除外**：基本語だけで構成され、字面どおりに意味が分かる表現や、上級者なら知っている易しい表現は除外する。\n")

# ---- B: 工程分離 ----
B1_SCHEMA = {"name": "kp_extract", "schema": {"type": "object", "additionalProperties": False, "required": ["candidates"], "properties": {
    "candidates": {"type": "array", "items": {"type": "object", "additionalProperties": False, "required": ["span", "sentence"],
                                               "properties": {"span": {"type": "string"}, "sentence": {"type": "string"}}}}}}}

def prompt_B1(text, n=14):
    return (f"以下の記事から、英語上級者が学ぶ価値のあるフレーズ・表現・イディオム・句動詞・連語・定着した名詞句(2語以上の連続した語句)の**候補を最大{n}個**、"
            "広めに挙げてください(後段で絞り込みます。ランキングは不要)。\n\n"
            "1. **本文一致(絶対条件)**: 本文中の連続した語句をそのまま抜き出す。変更・言い換え・創作は禁止。\n"
            "2. **5語以内(絶対条件)**: 6語以上は出力禁止。\n"
            "3. 意味と自然さを保てる最短の形で抜き出す。\n"
            + PROD_DIFFICULTY +
            "同じ語句や、一方が他方を含む類似語句は重ねない。sentenceは本文中でその語句を含む文をそのまま書く。" + BODY + text)

B4_SCHEMA = {"name": "kp_verify", "schema": {"type": "object", "additionalProperties": False, "required": ["verdicts"], "properties": {
    "verdicts": {"type": "array", "items": {"type": "object", "additionalProperties": False,
        "required": ["id", "verdict", "meaning_preserved", "gloss_consistent", "natural_headword", "issue", "fix_display_form", "fix_gloss_ja"],
        "properties": {"id": {"type": "integer"}, "verdict": {"type": "string", "enum": ["OK", "FIX", "REJECT"]},
                       "meaning_preserved": {"type": "boolean"}, "gloss_consistent": {"type": "boolean"}, "natural_headword": {"type": "boolean"},
                       "issue": {"type": "string"}, "fix_display_form": {"type": "string"}, "fix_gloss_ja": {"type": "string"}}}}}}}



# ============ 塊判定: 3区分の定義強化 + 判定テスト + 専門名詞句 + G1型 ============
CHUNK_DEFS_V3 = """## ひと塊として覚える価値の3区分(各候補を必ず1つに分類する)
- W(単語型): 個々の単語が難しいだけ。フレーズ枠には入れない。
- F(自由な組合せ): 通常の単語を通常の文法で組み合わせただけで、語を同類の語に入れ替えても同じように成り立つもの。**フレーズ枠には入れない**。次はすべてF:
  * 形容詞/副詞/名詞+名詞の**描写的な組合せ**(各語の意味から全体が導ける)。専門分野の記述的な名詞句もF(例: a faint signal / thermal noise level / seed funding round の類)。
    ただし学習者用英英辞書に一般語として見出しがあり、他の文脈でも使える定着した複合名詞はC(例: pain point / glass ceiling / bottom line)。
  * 動詞+目的語で、動詞が字面どおりの意味(例: open a window / write a report)。
  * 比喩的でも、辞書に定着していない一回限りの言い回し・本文の文脈でだけ成立する比喩(例: need a map for the road ahead)。
  * 修飾語+名詞で、修飾語を同類の語(early/late、deep/shallow等)に替えても同じ型で成り立つもの。
- C(塊): 次のいずれかで、「なぜこの組合せをひと塊で覚える価値があるか」を40字以内で言えるもの。
  * idiom(慣用表現): 語の意味の和では決まらない、または辞書に定着した比喩(例: set the record straight / pull strings)
  * phrasal_verb(句動詞・前置詞付き動詞): 動詞+粒子/前置詞の組合せ自体が見出しで特有の意味や必須の組合せ(例: walk someone through / run out of / bring something down)
  * collocation(強い連語): 特定の語同士が強く結びつき、言い換えると不自然、または組合せで覚えないと誤用しやすい(例: pay attention to / draw a conclusion)
  * fixed_phrase(固定表現・前置詞句・談話標識): 全体が決まった言い回し(例: in the long run / on behalf of)
  * compound_noun(定着した複合名詞): 1つの概念として辞書に定着(例: pain point)
## 判定テスト(順に適用。1つでも当てはまればF)
T1 辞書テスト: 学習者用英英辞書の見出し・派生項目・句動詞項目・連語欄に載りそうか。載らなければF。
T2 置換テスト: 構成語の1つを同類の別の語に替えても、同じ型で自然に成り立ち意味も同様に導けるならF(塊ではなく型)。
T3 予測テスト: すべての語を知っている学習者が、意味も、この語の組合せ(この動詞にこの前置詞/粒子)も自力で推測・再現できるならF。
T4 理由テスト: 「なぜひと塊で覚える価値があるか」を具体的に言えなければF。
難易度(difficulty)は区分と独立に記録する(advanced/upper_intermediate/easy)。**塊(C)であれば、基本語だけの句動詞・前置詞付き動詞でもCのまま**とし、易しいことを理由にFへ下げない/keepを下げない(難易度は並び順にだけ使う)。
## 一般化後に独立した学習価値がある場合(G1型)
本文の語句が個別の名詞を含み自由な組合せに見えても、**可変部の名詞をsomething/someoneに置き換えた見出し形**(動詞+前置詞/粒子の組合せ自体が辞書の見出し)が成立するなら、その見出し形で判定してC(例: set the numbers aside -> set something aside / bring the costs down -> bring something down)。
逆に、一般化(修飾語の除去など)の結果、字面どおりの易しい組合せになって独立した学習価値が消える場合はF。"""

EXTRA_RULES_V3 = """## 追加の判定規則
(a) 受動態・完了形・不定詞の断片: 受動形や過去分詞が核で辞書の能動の塊になっていないものはpassive_fragment=true、keep=false(be taken aback等、受動形そのものが見出しなら塊として扱ってよい)。
(b) 節の断片(whose…/which…/that…で始まる等)は塊ではない。
(c) 候補が不足してもkeepを甘くしない(品質を下げて埋めない)。keep=trueにできるのは、区分がCで、本文語義でのまとまりとして成立し、他の候補と意味・用法が重ならないものだけ。同じ意味・用法の候補が複数ある場合は最も代表的な1つだけkeepにする。"""

SEL3_SCHEMA = {"name": "kp_rank3", "schema": {"type": "object", "additionalProperties": False, "required": ["judgements"], "properties": {
    "judgements": {"type": "array", "items": {"type": "object", "additionalProperties": False,
        "required": ["id", "cls", "chunk_type", "reason_ja", "difficulty", "keep", "passive_fragment"],
        "properties": {"id": {"type": "integer"}, "cls": {"type": "string", "enum": ["W", "F", "C"]},
                       "chunk_type": {"type": "string", "enum": ["idiom", "phrasal_verb", "collocation", "fixed_phrase", "compound_noun", "none"]},
                       "reason_ja": {"type": "string"}, "difficulty": {"type": "string", "enum": ["advanced", "upper_intermediate", "easy"]},
                       "keep": {"type": "boolean"}, "passive_fragment": {"type": "boolean"}}}}}}}

def prompt_S3(text, cands, mode):
    """mode='span': 本文の語句を判定(E1。G1型は『可変部をsomething化した見出し形』で判定)/ mode='form': 一般化後の見出し形を判定(E2〜E4)"""
    lines = []
    for k, c in enumerate(cands, 1):
        if mode == "form":
            lines.append(f"{k}. 学習者に提示する形: {c['display_form']}\n   意味: {c.get('gloss_ja')}\n   本文の根拠(変更しない): {c['span']}\n   文: {c['sentence']}")
        else:
            w = V.wn_multiword(c["span"])
            h = f" [WordNet複合語見出し: {'あり' if w else 'なし' if w is False else '-'}(参考のみ)]"
            lines.append(f"{k}. {c['span']}{h}\n   文: {c['sentence']}")
    head = ("次は英語記事から抽出された学習候補です。各候補を評価し、ユーザーが修正せずに選べる候補だけをkeep=trueにしてください。\n"
            + ("**判定の対象は『学習者に提示する形』(一般化済み)です。** 本文の根拠は文脈確認のための参考で、提示形が辞書の見出しとして独立の学習価値を持つかで区分を決める。\n" if mode == "form"
               else "判定の対象は本文の語句ですが、個別の名詞を含む場合は可変部をsomething/someoneにした見出し形で成立するかを考慮する(G1型)。\n")
            + "\n")
    return (head + CHUNK_DEFS_V3 + "\n\n" + EXTRA_RULES_V3 + "\n\n"
            "各候補についてid・cls・chunk_type・reason_ja(40字以内)・difficulty・keep・passive_fragmentのみ返す。\n\n【候補】\n" + "\n".join(lines) + BODY + text)

RANK = {"advanced": 0, "upper_intermediate": 1, "easy": 2}



DET = {"the", "a", "an", "this", "that", "these", "those"}

PRON = {"it", "them", "him", "her", "me", "us", "you", "its", "his", "their", "my", "our", "your", "one", "himself", "herself", "itself", "themselves"}

FRAME_BAD = ("OBJECT_DROPPED_SENSE_CHANGED", "SENSE_CHANGED", "FRAME_CHANGED")

SLOT_WORDS = {"something", "someone", "one's", "someone's", "oneself"}

# ============ N2: 意味確定先行の一般化(source_sense -> headword_frame -> tokens -> gloss) ============
GEN5_EXTRA = """
## 追加規則(v5。意味確定先行)
**出力の順序を守る**: 各項目で、(1)source_sense_ja(本文の文脈での語句の意味を、辞書の語義gloss形式で20〜30字。日本語の意味や塊の理由には頼らず、本文の文と前後から独立に判断する) -> (2)arg_notes(目的語・主語・代名詞が本文で何を指すか。
kind=person/thing/event/personified_thing/fixed_pronoun[慣用表現に含まれる固定のit等]/none) -> (3)headword_frame(学習者用英英辞書の見出し形。someone/something/one's/someone's可。本文の語義と同じ語義の見出しであること)
-> (4)frame_change(本文から見出し形へ行った操作の申告) -> (5)tokens(headword_frameを作る分類にする) -> (6)gloss_ja の順に決める。
A. **someone/somethingは『本文で指す対象』ではなく『その見出し形の辞書上の標準的な用法』で決める**。標準の用法が人を取る見出し(hear someone out / talk someone into / see someone off)なら、本文の目的語が物(擬人化した物を含む)でもSLOT_PERSON(someone)。
   本文の比喩・擬人化はsense_note_jaに書く。物・事を取る見出し(sit through something / shake something off)はSLOT_THING。人も物も取る見出し(put up with)は本文に合わせる。
   **someoneかsomethingかで語義が変わる句動詞(bring someone up[育てる]/bring something up[話題に出す]、put someone up[泊める]/put something up[建てる]、see someone through[支える]/see something through[やり遂げる])は、本文の語義に合う方を選ぶ**。
   慣用表現の一部として固定されたit/them(take it out on / make it up to / call it a day / lose it)は、SLOTにせずCOREのまま残す。
B. **目的語のDROPは、残った形が本文と同じ語義の辞書見出しである場合に限る**。目的語を除くと語義が不定になる動詞+粒子(take up / put up / bring up / pick up / see through)や、人か物かで語義が変わる句動詞は、目的語をDROPせずSLOT_PERSON/SLOT_THINGで残す(put up the tent -> put something up、put up our guests -> put someone up)。残った形が別の見出し・別の語義になる、または複数の語義を持つ場合
   (take points away from -> take away from[=損なう、別見出し]は不可。take something away from にする。take up space -> take up は語義が不定になるため take up space のままCOREに残す)は、目的語をSLOT_THINGにして枠を残すか、COREに残す。
C. **修飾語(形容詞・副詞)のDROPは許容**: 除いた形が同じ見出し・同じ語義で成立するなら除いてよい(set a lower limit -> set a limit / took an unexpected turn -> take a turn / take good care of -> take care of)。
   成立しない(break new ground / in the long run / turn a blind eye to / give someone a big hand[拍手] / take a back seat)ものは修飾語をCOREに残す。
D. **gloss_jaは見出し形(headword_frame)そのものの語義**。DROP/SLOTにした語や修飾語の意味を含めない。本文固有の意味を足さない(本文固有の語義はsense_note_jaへ)。
E. 受動態・過去分詞を核に残さない。動詞は固定句の中でも原形。can't help thinking のように語形そのものが見出しの一部の場合は語形を保つ。
   **名詞の複数形が表現に固定されているもの(come to terms with / make ends meet / articles of incorporation / on good terms)は、lemmaも複数形のまま書く(単数化しない)**。
"""

GEN5_SCHEMA = {"name": "kp_gen_tokens5", "schema": {"type": "object", "additionalProperties": False, "required": ["items"], "properties": {
    "items": {"type": "array", "items": {"type": "object", "additionalProperties": False,
        "required": ["id", "source_sense_ja", "arg_notes", "headword_frame", "frame_change", "tokens", "gloss_ja", "sense_note_ja", "note_ja"],
        "properties": {
            "id": {"type": "integer"},
            "source_sense_ja": {"type": "string"},
            "arg_notes": {"type": "array", "items": {"type": "object", "additionalProperties": False, "required": ["n", "referent_ja", "kind"],
                "properties": {"n": {"type": "integer"}, "referent_ja": {"type": "string"},
                               "kind": {"type": "string", "enum": ["person", "thing", "event", "personified_thing", "fixed_pronoun", "none"]}}}},
            "headword_frame": {"type": "string"},
            "frame_change": {"type": "array", "items": {"type": "string", "enum": ["NONE", "OBJECT_SLOT", "OBJECT_DROPPED", "MODIFIER_DROPPED", "POSSESSIVE_SLOT", "INFLECTION", "ARTICLE_DROPPED", "PERSON_OVERRIDE"]}},
            "tokens": {"type": "array", "items": {"type": "object", "additionalProperties": False, "required": ["n", "label", "lemma"],
                "properties": {"n": {"type": "integer"}, "label": {"type": "string", "enum": G.LABELS}, "lemma": {"type": "string"}}}},
            "gloss_ja": {"type": "string"}, "sense_note_ja": {"type": "string"}, "note_ja": {"type": "string"}}}}}}}

def prompt_G5(text, cands):
    blocks = []
    for i, c in enumerate(cands, 1):
        tk = G.tokenize(c["span"])
        blocks.append(f"{i}. 語句: {c['span']}\n   トークン: " + " ".join(f"[{n}]{t}" for n, t in enumerate(tk, 1)) + f"\n   本文の文: {c['sentence']}")
    rules = G.GEN2_RULES.replace("gloss_ja: **一般形", GEN5_EXTRA + "\ngloss_ja: **一般形", 1)
    head = ("次は学習候補です。各語句について、まず本文の意味を確定し、その意味を保つ学習用の見出し形(一般形)を作ってください。"
            "選定は別の工程で行うので、塊かどうかは気にしないでください。ユーザーは提示された形を修正せずにそのまま選びます。\n\n")
    return head + rules + "\n\n【候補】\n" + "\n".join(blocks) + BODY + text

# ---- 正規化(M9): 末尾slot・one's・oneself・sb/sth・to不定詞
def _norm_hw(s):
    s = (s or "").lower().replace("’", "'")
    s = re.sub(r"[.,;:!?\"()]+", " ", s)
    s = re.sub(r"\bsomebody's\b|\bsb's\b", "someone's", s)
    s = re.sub(r"\bsomebody\b|\bsb\b", "someone", s)
    s = re.sub(r"\bsth\b", "something", s)
    s = re.sub(r"\b(yourself|himself|herself|themselves|myself)\b", "oneself", s)
    t = [x for x in s.split() if x]
    if t and t[0] == "to" and len(t) > 1:
        t = t[1:]
    return t

def _strip_trail(t):
    t = list(t)
    while t and t[-1] in SLOT_WORDS and len(t) > 1:
        t.pop()
    return t

def _swappable(a, b):
    return a == b or {a, b} <= {"something", "someone"} or {a, b} <= {"one's", "someone's"}

def reconcile(display_form, headword_frame):
    """tokens由来のdisplay_formと、モデルが別表現で書いたheadword_frameの調停(決定論)。
    returns (form, status): SAME / SLOT_TYPE_OVERRIDDEN(someone<->something、one's<->someone'sのみ違い。headword側=辞書の標準用法を採用) / FRAME_MISMATCH(それ以外の違い。flag対象、formは変更しない)"""
    d, h = _strip_trail(_norm_hw(display_form)), _strip_trail(_norm_hw(headword_frame))
    if d == h:
        return display_form, "SAME"
    if len(d) == len(h) and all(_swappable(a, b) for a, b in zip(d, h)):
        return " ".join(h), "SLOT_TYPE_OVERRIDDEN"
    core_d, core_h = [t for t in d if t not in SLOT_WORDS], [t for t in h if t not in SLOT_WORDS]
    if core_d == core_h and sum(t in SLOT_WORDS for t in h) > sum(t in SLOT_WORDS for t in d):
        return " ".join(h), "SLOT_INSERTED"          # 核は同じで、見出しには語義を決める目的語枠がある(put up -> put someone up)。目的語枠を戻す方向のみ採用
    return display_form, "FRAME_MISMATCH"



# ============ 検証5: 本文基準の意味・用法検査(追加call 0)。M3: 『塊の理由』を入力に含めず、旧Promptの矛盾文言(戻す方向のfix禁止/不要な目的語)を整合 ============
VER5_HEAD = ("あなたは英語教材の校閲者です。本文の語句を学習用の一般形に直した結果を検査してください。\n"
             "この検査は『この語句を選ぶべきか』の判断ではありません(選定は完了済み)。形と意味の検査だけを行ってください。各項目について: (a)学習用の形は本文の語句と同じ意味・語義を保っているか(別の意味になっていないか)、(b)日本語の意味は学習用の形と本文の語義の両方に合っているか、"
             "(c)学習用の形は辞書の見出し語として自然で、別の文脈でも使える英語か。本文の語義に必要な目的語(someone/something)・前置詞・固定語が欠けていないか、逆に本文固有の文脈語が残っていないか、"
             "(d)自由に入れ替わる目的語名詞(意味の違う別の名詞に替えても同じ構文・同じ意味で成り立つもの)が、somethingやsomeoneにならずに残っていないか、"
             "(e)前置詞で終わる固定表現の後ろに、本文固有の名詞句・動名詞が残っていないか(学習用の表示では核を明確にするため除く)、を判定する。(d)(e)に該当する場合はFIXとし、fix_display_formに直した形を書く。\n"
             "verdict: OK=そのままユーザーに提示できる / FIX=小さな修正で提示できる(fix_display_form/fix_gloss_jaに修正案。核の語は本文の語の語形違いのみ、something/someone/one'sのみ置換可) / REJECT=一般化で意味・語義が変わる、または英語として不自然で修正案も作れず提示不可。選定の是非(塊としての価値)を理由にREJECTしない。\n"
             "**重要(fixの方向)**: 学習用の形が本文固有の語(DROP/something化した語)を除いて一般化されているのは原則として意図どおり(例: at the time of writing -> at the time of は正しい一般化)。"
             "ただし除いた結果が本文と別の語義・別の構文になる場合は、除いた目的語をsomething/someone/one'sで残す、または本文の語を戻す方向のfix_display_formを書いてよい。"
             "**日本語の意味に合わせるためだけに、目的語や前置詞を削るfixは書かない**(その場合は日本語の側を本文の語義に合わせて直す)。日本語の意味が一般形より具体的すぎる(除いた語の意味を含む)場合は、fix_gloss_jaで日本語の側を一般形に合わせて直す。"
             "日本語の意味は名詞句・副詞句・動詞句のいずれの形でもよく、品詞の形だけを理由にFIXしない。fix_gloss_jaを書くときも、日本語の意味は**本文での語義(sense)を保つ**こと。辞書にある別の語義や、より一般的な語義に置き換えない(例: 『順序を逆にする』の意味を『好転させる』に変えない)。OKのとき、fix欄は空文字。\n")

VER5_ADD = """

## 追加検査(意味・用法の保持。上の(a)〜(e)に加えて必ず行う)
各項目で次を判定し、source_sense_ja・frame_preserved・argument_type_okに書く。
(1) source_sense_ja: 本文の文脈で語句が何を意味しているかを、辞書の語義gloss形式で20〜30字の日本語で書く。『日本語の意味』は参考にせず、本文の文と前後から独立に判断する。
(2) frame_preserved: 学習用の形は、本文の語句と『同じ語義・同じ構文(動詞+前置詞/粒子の枠、目的語の有無)』の辞書見出しか。
    SAME=同じ / MODIFIER_DROPPED_OK=修飾語を除いたが同じ見出し・同じ語義 /
    OBJECT_DROPPED_SENSE_CHANGED=目的語を除いた結果、別の見出し・別の語義になった(例: take points away from[減点する] -> take away from[損なう、別見出し]) /
    SENSE_CHANGED=別の語義になった / FRAME_CHANGED=前置詞・粒子を落とす/変える、または表現の途中の目的語を落とすことで、別の語義になる・語義が不定になる(例: came to terms with -> come to terms、looked down on -> look down、took up space -> take up)/ OTHER。
    **表示の約束(これらはFRAME_CHANGEDにもOBJECT_DROPPEDにも該当しない)**: (i)前置詞・粒子で終わる形は末尾の目的語(something/someone)を示さない約束である(take something away from / put up with / look down on / take it out on / make it up to / talk someone into)。末尾に目的語が無いこと自体は誤りではない。
    (ii)目的語を示さなくても同じ語義の見出しとして通用する形(carry out / narrow down / tighten up / look into / sort out)は、目的語が無くてよい。(iii)本文の語句に付いている助詞・修飾語・本文固有の補語(joining、the whole lecture等)が形から除かれているのは意図どおり。
(3) argument_type_ok: somethingとsomeone、one'sとsomeone'sの選択が、『その見出し形の辞書上の標準的な用法』と『本文の語義』に合っているか。本文で物を擬人化している場合も、標準の用法が人を取る見出しならsomeoneが正しい(例: hear it out[itは擬人化された物] -> hear someone out)。
    someoneかsomethingかで語義が変わる句動詞は、本文の語義に合う方が正しい。
修正方針: 形と日本語の意味が食い違うときは、本文の文脈の語義を基準にどちらを直すか決める。**日本語の意味に合わせるためだけに、目的語や前置詞を削ってはならない**。
frame_preservedがOBJECT_DROPPED_SENSE_CHANGED/SENSE_CHANGED/FRAME_CHANGEDなら、目的語をsomething/someoneで残すfix_display_formを書く(書けなければREJECT)。
修飾語の除去(set a lower limit -> set a limit等)だけを理由にNGにしない。ただしその場合、日本語の意味は『一般形そのものの語義』にし、除いた修飾語の意味を含めない(含んでいればfix_gloss_jaで直す)。"""

def prompt_V5(text, items):
    lines = [f"{i}. 本文の語句: {c['span']}\n   本文の文: {c['sentence']}\n   学習用の形: {c['display_form']}\n   日本語の意味: {c['gloss_ja']}" for i, c in enumerate(items, 1)]
    return VER5_HEAD + VER5_ADD + "\n\n【検査対象】\n" + "\n".join(lines) + BODY + text

def src_form(span):
    return re.sub(r"[.,;:!?\"()]+$", "", " ".join(G.tokenize(span)).lower())

def fix_drops_content(pre, fix):
    """M2: FIXがFIX前の形から something/someone/one's 等のslotや核(CORE)語を削るか。返り値=削られた要素のlist(空=削っていない)。冠詞の増減は無視。slotの種類の入替(someone<->something)は削除ではない。"""
    a = [t for t in _norm_hw(pre) if t not in DET]
    b = [t for t in _norm_hw(fix) if t not in DET]
    def groups(ts):             # 連続するslot(one's someone等の重複表記)は1つの目的語枠として数える
        n, prev = 0, False
        for t in ts:
            cur = t in SLOT_WORDS
            n += (cur and not prev)
            prev = cur
        return n
    a_slots, b_slots = groups(a), groups(b)
    a_core = [t for t in a if t not in SLOT_WORDS]
    b_core = [t for t in b if t not in SLOT_WORDS]
    gone = []
    pool = list(b_core)
    for t in a_core:
        hit = next((x for x in pool if x == t or V.same_word(x, t)), None)
        if hit is None:
            gone.append(t)
        else:
            pool.remove(hit)
    if b_slots < a_slots:
        gone.append("<slot>")
    return gone

# ============ 疑わしい候補の決定論flag(方式C限定の対象選別。LLM不使用)。M9: 定義をP1前に凍結(FLAGS_V1)。結果を見てから変えない ============
FLAGS_V1 = {
    "PRONOUN_SLOT": "代名詞(it/them/her等)がSLOT(something/someone)にされた",
    "CONTENT_DROPPED": "冠詞・指示詞以外の語(修飾語・目的語・文脈語)がDROPされた",
    "SLOT_TYPE_OVERRIDDEN": "tokensのsomeone/something(one's/someone's)とheadword_frameが食い違い、headword側を採用した(決定論調停)",
    "FRAME_MISMATCH": "tokens由来の形とheadword_frameが構造的に食い違う(調停不可)",
    "PERSON_OVERRIDE": "GEN5自身がframe_changeでPERSON_OVERRIDE(本文の指示対象と見出しの標準項タイプが異なる)を申告した",
    "PERSONIFIED_THING": "arg_notesに擬人化された物(personified_thing)がある",
    "VER_FIXED_FORM": "VERが形を実際に変更した(同一形のgloss修正のみは対象外)",
    "VER_FLAG": "VERが frame_preserved=NG または argument_type_ok=false と報告した",
    "VER_GLOSS_FIXED": "VERが日本語の意味を修正した(訳が本文語義から離れる経路)",
    "FIX_REJECTED": "VERのFIXを決定論規則(slot/CORE語を削る/validator不通過)で不採用にした",
}

def flag_item(c):
    fl = []
    sp = G.tokenize(c["span"])
    lab = {n: l for n, l, _ in (c.get("tokens") or [])}
    for n, surf in enumerate(sp, 1):
        l = lab.get(n, "CORE"); s = surf.lower().strip(".,;:!?\"()")
        if l.startswith("SLOT") and s in PRON:
            fl.append("PRONOUN_SLOT")
        if l == "DROP" and s not in DET:
            fl.append("CONTENT_DROPPED")
    if c.get("reconcile") in ("FRAME_MISMATCH", "SLOT_TYPE_OVERRIDDEN"):
        fl.append(c["reconcile"])
    if "PERSON_OVERRIDE" in (c.get("frame_change") or []):
        fl.append("PERSON_OVERRIDE")
    if any(a.get("kind") == "personified_thing" for a in (c.get("arg_notes") or [])):
        fl.append("PERSONIFIED_THING")
    v = c.get("verify") or {}
    pf = c.get("display_form_pre_fix")
    if pf and pf != c.get("display_form"):       # 検証が形を実際に変更した場合のみ(同一形へのFIX=gloss修正のみは対象外)
        fl.append("VER_FIXED_FORM")
    if v.get("frame_preserved") in FRAME_BAD or v.get("argument_type_ok") is False:
        fl.append("VER_FLAG")
    if c.get("gloss_pre_ver") is not None and c.get("gloss_ja") != c.get("gloss_pre_ver") and not c.get("reverted"):
        fl.append("VER_GLOSS_FIXED")
    if c.get("fix_rejected"):
        fl.append("FIX_REJECTED")
    return sorted(set(fl))

# ============ 方式C限定: 別系列上位モデル(sol / deepseek-v4-pro)の局所文脈つき独立検査 ============
CHK_REL = ["SAME", "MODIFIER_DROPPED_OK", "SENSE_SHIFT", "ARG_TYPE_SHIFT", "FRAME_SHIFT", "GLOSS_MISMATCH"]

CHK5_SCHEMA = {"name": "kp_check5", "schema": {"type": "object", "additionalProperties": False, "required": ["checks"], "properties": {
    "checks": {"type": "array", "items": {"type": "object", "additionalProperties": False,
        "required": ["id", "context_sense_ja", "example_en", "relation", "fix_display_form", "fix_gloss_ja", "reason_ja"],
        "properties": {"id": {"type": "integer"}, "context_sense_ja": {"type": "string"}, "example_en": {"type": "string"},
                       "relation": {"type": "string", "enum": CHK_REL}, "fix_display_form": {"type": "string"}, "fix_gloss_ja": {"type": "string"},
                       "reason_ja": {"type": "string"}}}}}}}

CHK5_RULES = """あなたは英語学習教材の独立審査員です。学習者には『学習用の形(見出し形)』と『日本語の意味』を提示します。各項目について、本文でその語句が使われている意味・用法と、提示形が『同じ語義・同じ構文の見出し』かを、与えられた前後の文脈だけから審査してください(他の工程の判定は与えられません)。
各項目で次の順に書く: (1)context_sense_ja: 文脈での語句の意味 (2)example_en: 提示形と日本語の意味に合う新しい自然な英語例文(本文の語は使わない) (3)relation:
 SAME=同じ語義・同じ構文 / MODIFIER_DROPPED_OK=修飾語を除いたが同じ見出し・語義(set a lower limit -> set a limitのように、日本語が一般形の語義なら問題なし) /
 SENSE_SHIFT=別の語義の見出しになった(例: take points away from[減点する] -> take away from[損なう]) /
 ARG_TYPE_SHIFT=someone/somethingの選択が、見出し形の辞書上の標準用法または本文の語義に合わない(標準が人を取る見出しなら、本文で物を擬人化していてもsomeone) /
 FRAME_SHIFT=構文の枠(目的語の有無・前置詞/粒子)が変わった / GLOSS_MISMATCH=形は妥当だが日本語の意味が形と合わない、または日本語の意味が本文とは別の語義(除いた修飾語の意味を含む等)。
修正: SENSE_SHIFT/ARG_TYPE_SHIFT/FRAME_SHIFTで本文と同じ語義の形に直せるなら fix_display_form(someone/something/one'sの置換と、目的語・前置詞を残す修正のみ。核の語は本文の語形違いのみ)と、その形に合う日本語 fix_gloss_ja(必須)を書く。GLOSS_MISMATCHなら fix_gloss_ja。不要なら空文字。
易しい表現かどうか、自由な組合せかどうかは審査しない。修飾語の除去だけを理由にNGにしない。"""

def local_context(text, sentence, n=1):
    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.replace("\n", " ")) if s.strip()]
    key = (sentence or "")[:40]
    idx = next((i for i, s in enumerate(sents) if key and key in s), None)
    if idx is None:
        return sentence
    return " ".join(sents[max(0, idx - n): idx + n + 1])

def prompt_C5(text, items):
    lines = [f"{i}. 本文の語句: {c['span']}\n   文脈: {local_context(text, c['sentence'])}\n   学習用の形: {c['display_form']}\n   日本語の意味: {c['gloss_ja']}" for i, c in enumerate(items, 1)]
    return CHK5_RULES + "\n\n【検査対象】\n" + "\n".join(lines)




# ============================================================
# LLM呼出基盤(Production)。Trial kpg04_llm/kpg02_llm.callの『送り方』を保ち、Trial専用のCap/台帳/cache/SALT/mockは持たない。
# 送り方(Opus M7): OpenAI=Responses API(developer messageなし・user 1通・json_schema strict・effortがNoneならreasoning指定なし・max_output_tokens明示)、
#   Gemini=generate_content(response_mime_type=json・response_schemaはadditionalProperties除去・thinking_budget明示・max_output_tokens明示)。
# model照合: OpenAIはresponse.model、Geminiはresponse.model_version(正規化比較、Opus M13)。不一致=N5ContractError(STOP、自動downgradeなし)。
# 費用はer005 cost logger(SDK patch)が記録する(stageタグ=kp_n5_<stage>、segment=呼出文脈)。
# ============================================================
USD_JPY = 160.0             # Trial kpg02_llm.USD_JPYと同一(Trial費用との比較用)
_CLIENT_LOCK = threading.Lock()
_CLIENTS: dict = {}


def _get_openai_client():
    with _CLIENT_LOCK:
        if "openai" not in _CLIENTS:
            from dotenv import load_dotenv
            load_dotenv()
            from openai import OpenAI
            _CLIENTS["openai"] = OpenAI()
        return _CLIENTS["openai"]


def _get_gemini_client():
    with _CLIENT_LOCK:
        if "gemini" not in _CLIENTS:
            from dotenv import load_dotenv
            load_dotenv()
            from google import genai
            _CLIENTS["gemini"] = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        return _CLIENTS["gemini"]


def _strip(s):
    """Gemini response_schema用: additionalProperties除去(Trial kpg02_llm._strip)。"""
    if isinstance(s, dict):
        return {k: _strip(v) for k, v in s.items() if k != "additionalProperties"}
    if isinstance(s, list):
        return [_strip(x) for x in s]
    return s


_PRICES = None


def _price_per_m(model: str) -> tuple:
    """(input, cached_input, output) USD per 1M tokens。pricing_snapshot.json(Production単価の正本)から取得。未登録はfail-closed(0円扱いにしない)。"""
    global _PRICES
    if _PRICES is None:
        with open(os.path.join(HERE, "er005_output", "cost_baseline_01", "pricing_snapshot.json"), encoding="utf-8") as f:
            _PRICES = json.load(f)["prices"]
    got = {p["meter"]: p["price"] for p in _PRICES if p["model"] == model and p.get("tier") == "Standard"
           and p["meter"] in ("input_tokens", "cached_input_tokens", "output_tokens")}
    if "input_tokens" not in got or "output_tokens" not in got:
        import er006_model_routing_contract_01 as routing
        raise routing.PricingNotFoundError(f"model '{model}' の単価がpricing_snapshot.jsonに無い(N5費用計算はfail-closed)")
    return got["input_tokens"], got.get("cached_input_tokens", got["input_tokens"]), got["output_tokens"]


def cost_jpy(model: str, tin: int, tout: int, cached: int = 0) -> float:
    p = _price_per_m(model)
    return ((tin - cached) * p[0] + cached * p[1] + tout * p[2]) / 1e6 * USD_JPY


def resolve_stage_model(stage: str, process: Optional[str]) -> str:
    """API call**前**にrouting contractでmodelを確定する(fail-closed)。luna段(b1/sel/gen5)は呼出元のA2_SUPPORT/B1_SUPPORT(=SUPPORT_MODEL)、
    別系列2段(ver5/chk5)は専用process(KP_N5_VERIFY/KP_N5_CHECK)。解決結果がTrial確定版のmodelと一致しなければN5ContractError。"""
    import er006_model_routing_contract_01 as routing
    want = STAGE_PARAMS[stage]["model"]
    sp = STAGE_PROCESS[stage]
    try:
        if sp is None:
            if process not in ft.ALLOWED_PROCESSES:
                raise N5ContractError(f"N5 {stage}段のprocessはB1_SUPPORT/A2_SUPPORTのみ(実際: {process!r})")
            got = routing.require_model(process, routing.SUPPORT_MODEL)
        else:
            got = routing.require_model(sp, want)
    except routing.ModelContractViolation as e:
        raise N5ContractError(f"routing contract違反(N5 {stage}): {e}") from e
    if got != want:
        raise N5ContractError(f"routing解決モデルがTrial確定版と一致しない(N5 {stage}: 期待 {want} / 実際 {got})")
    return got


def normalize_model_version(v: Optional[str]) -> Optional[str]:
    if not v:
        return None
    v = str(v).strip().lower()
    return v[len("models/"):] if v.startswith("models/") else v


def gemini_version_matches(requested: str, version: Optional[str]) -> bool:
    """Gemini応答のmodel_versionが要求modelと同一か(Opus M13)。正規化(小文字・models/接頭辞除去)後に、完全一致、または要求名+'-'+版数suffix
    (例: gemini-3.8-flash-001 / gemini-3.8-flash-preview-0930)を許容する。別modelへの置換(例: gemini-3.8-flash-lite)は不一致。"""
    nv = normalize_model_version(version)
    if nv is None:
        return False
    req = requested.lower()
    if nv == req:
        return True
    if nv.startswith(req + "-"):
        rest = nv[len(req) + 1:]
        return bool(re.fullmatch(r"(?:\d[\w.]*|preview(?:-[\w.]+)?|latest|exp(?:-[\w.]+)?)", rest))
    return False


def _send(stage: str, model: str, user: str, schema: dict, max_out: int) -> tuple:
    """SDK 1 call。returns (raw_text, meta)。tests/replayはこの関数を差し替える(Trial cache key再計算一致の証明点)。"""
    p = STAGE_PARAMS[stage]
    t0 = time.time()
    if model.startswith("gpt-"):
        client = _get_openai_client()
        kw: dict = dict(model=model, input=[{"role": "user", "content": user}],
                        text={"format": {"type": "json_schema", "name": schema["name"], "strict": True, "schema": schema["schema"]}},
                        max_output_tokens=max_out)
        if p["effort"]:
            kw["reasoning"] = {"effort": p["effort"]}
        try:
            r = client.responses.create(**kw)
        except Exception as e:   # noqa: BLE001  schema拒否(HTTP 400)は設定不備=retryで直らない
            if type(e).__name__ == "BadRequestError" or getattr(e, "status_code", None) == 400:
                raise N5ContractError(f"N5 {stage} APIが要求を拒否しました(HTTP 400、設定/schema不備。retryしません): {e}") from e
            raise
        mid = getattr(r, "model", None)
        if mid != model:
            raise N5ContractError(f"応答モデルが不一致です(N5 {stage}: 期待 {model} / 実際 {mid})")
        u = r.usage
        tin, tout = u.input_tokens, u.output_tokens
        cached = getattr(getattr(u, "input_tokens_details", None), "cached_tokens", 0) or 0
        meta = {"model_req": model, "model_id": mid, "model_version": None, "in": tin, "out": tout, "cached": cached}
        return getattr(r, "output_text", None) or "", dict(meta, sec=round(time.time() - t0, 1), cost_jpy=round(cost_jpy(model, tin, tout, cached), 4))
    if model.startswith("gemini-"):
        from google.genai import types as gtypes
        client = _get_gemini_client()
        cfg = dict(response_mime_type="application/json", response_schema=_strip(schema["schema"]),
                   thinking_config=gtypes.ThinkingConfig(thinking_budget=p["think_budget"]), max_output_tokens=max_out)
        r = client.models.generate_content(model=model, contents=user, config=gtypes.GenerateContentConfig(**cfg))
        mv = getattr(r, "model_version", None)
        if mv is not None and not gemini_version_matches(model, mv):
            raise N5ContractError(f"応答モデルが不一致です(N5 {stage}: 期待 {model} / 実際 model_version={mv!r})")
        um = r.usage_metadata
        tin = um.prompt_token_count or 0
        tout = (um.candidates_token_count or 0) + (getattr(um, "thoughts_token_count", 0) or 0)
        meta = {"model_req": model, "model_id": model if mv is None else normalize_model_version(mv), "model_version": mv,
                "model_version_unverified": mv is None, "in": tin, "out": tout, "cached": 0}
        return r.text or "", dict(meta, sec=round(time.time() - t0, 1), cost_jpy=round(cost_jpy(model, tin, tout, 0), 4))
    raise N5ContractError(f"未対応model: {model}")


class N5Ctx:
    """1回の生成(初回/補完/再選定round)の呼出文脈。M12: N5はthread並列にしない(er125 contextvar・cost logger globalを共有するため)。"""

    def __init__(self, process: str, *, tag: str = "", stop_check_fn: Optional[Callable] = None, sleep_fn: Optional[Callable] = None,
                 article_id: str = ""):
        self.process, self.tag, self.stop_check_fn, self.sleep_fn, self.article_id = process, tag, stop_check_fn, sleep_fn, article_id
        self.metas: list = []           # 呼出ごとのmeta(stage別費用・actual model・model_version・JSON途切れ再試行)


@contextlib.contextmanager
def cost_context(stage_label: str, segment: Optional[str] = None):
    """er005 cost loggerのstage/segmentタグを一時的に差し替える(themeは保持)。logger未installでもno-op相当。"""
    try:
        import er005_cost_logger as cl
    except Exception:   # noqa: BLE001
        yield
        return
    prev = (cl._CONTEXT.get("stage"), cl._CONTEXT.get("segment"))
    cl._CONTEXT["stage"] = stage_label
    if segment:
        cl._CONTEXT["segment"] = segment
    try:
        yield
    finally:
        cl._CONTEXT["stage"], cl._CONTEXT["segment"] = prev


def _is_propagating(e: BaseException) -> bool:
    if isinstance(e, (KeyboardInterrupt, SystemExit, ft.FulltextSelectionError)):
        return True
    n = type(e).__name__
    return "Stop" in n or "Sentinel" in n or n == "ModelContractViolation"


def call_llm(stage: str, user: str, schema: dict, ctx: N5Ctx, *, label: str = "") -> tuple:
    """1段のLLM呼出。returns (parsed_json, meta)。順序: routing確定(API前) -> stop_check -> 送信。
    JSON途切れ(出力上限到達)は**先に**max_outを1.6倍して1回だけ再試行(Trial確定版の挙動)。それでも失敗した同一失敗は技術失敗として既存retry(MAX_ATTEMPTS=2、sleep(2))へ。
    N5ContractError/STOP/routing違反は握らず伝播。技術失敗がretry上限に達したらN5TechnicalFailure。"""
    model = resolve_stage_model(stage, ctx.process)
    if ctx.stop_check_fn is not None:
        ctx.stop_check_fn(f"kp_n5_{stage}:{ctx.tag or ctx.article_id}")
    sleep = ctx.sleep_fn if ctx.sleep_fn is not None else time.sleep
    last: Optional[BaseException] = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        mo = STAGE_PARAMS[stage]["max_out"]
        truncated = False
        try:
            with cost_context(f"kp_n5_{stage}", ctx.tag or None):
                for trunc in (0, 1):
                    text, meta = _send(stage, model, user, schema, mo)
                    ctx.metas.append(dict(meta, stage=stage, label=label or stage.upper(), max_out=mo, attempt=attempt, json_ok=None, tag=ctx.tag))
                    try:
                        out = json.loads(text)
                        ctx.metas[-1]["json_ok"] = True
                        break
                    except json.JSONDecodeError:
                        ctx.metas[-1]["json_ok"] = False
                        if trunc == 1:
                            raise
                        truncated = True
                        mo = int(mo * JSON_TRUNCATION_MAX_OUT_FACTOR)
            return out, dict(ctx.metas[-1], truncation_retried=truncated)
        except Exception as e:   # noqa: BLE001
            if _is_propagating(e):
                raise
            last = e
            if attempt < MAX_ATTEMPTS:
                sleep(2)
    raise N5TechnicalFailure(f"N5 {stage}段が技術失敗(retry上限{MAX_ATTEMPTS}): {type(last).__name__}: {last}") from last


def _meta(m: dict) -> dict:
    return {k: m.get(k) for k in ("model_id", "in", "out", "cost_jpy", "sec")}



# ---- VER5 schema(Trial: B4_SCHEMAを複製して3欄追加) / FLAGS_V1_HASH ----
_v = json.loads(json.dumps(B4_SCHEMA))
_vi = _v["schema"]["properties"]["verdicts"]["items"]
_vi["properties"].update(source_sense_ja={"type": "string"}, argument_type_ok={"type": "boolean"},
                         frame_preserved={"type": "string", "enum": ["SAME", "MODIFIER_DROPPED_OK", *FRAME_BAD, "OTHER"]})
_vi["required"] = _vi["required"] + ["source_sense_ja", "argument_type_ok", "frame_preserved"]
VER5_SCHEMA = {"name": "kp_verify5", "schema": _v["schema"]}
FLAGS_V1_HASH = hashlib.sha256(json.dumps(FLAGS_V1, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:12]


# ============================================================
# Trial確定版の決定論部品(移植。変更点=span_glossのPROD_GLOSS入力の渡し方とdrop記録のみ)
# ============================================================
def _verb_base(w):
    try:
        with _WN_LOCK:
            return _wn().morphy(w, "v") or w
    except N5ContractError:
        raise
    except Exception:
        return w


def revert_form(c):
    """M1: 本文の形へ戻す時の形。先頭の動詞だけをWordNet/GENのlemmaで原形化(P7のcanonicalizationと同等の動詞原形化。took -> take)。それ以外の語は本文の語形のまま
    (複数形固定の名詞come to termsの単数化や名詞articles of incorporationの誤原形化を避ける)。"""
    sp = G.tokenize(c["span"])
    lab = {n: (l, lem) for n, l, lem in (c.get("tokens") or [])}
    out = []
    wn = _wn()
    for n, surf in enumerate(sp, 1):
        s = surf.lower().strip(".,;:!?\"()")
        if n == 1:
            nxt = sp[1].lower().strip(".,;:!?\"()") if len(sp) > 1 else ""
            with _WN_LOCK:
                noun_head = s.endswith("s") and nxt in {"of", "in", "for", "on", "to", "with", "at", "from", "by"} and bool(wn.synsets(s, "n"))
            lem = (lab.get(1, ("", ""))[1] or "").strip().lower()
            vb = _verb_base(s)
            out.append(s if noun_head else (lem if lem and lem == vb else vb))
        else:
            out.append(s)
    f = re.sub(r"\s+", " ", " ".join(out)).strip()
    return f if display_check(f, c["span"])[0] else src_form(c["span"])


def span_gloss(c):
    """M1: 本文の語義を表す日本語gloss。優先=現行Productionの同一span gloss(PROD_GLOSS=P7由来[call1/backfill]のcanon・ga後japanese_glossのみ。B1由来には無い、Opus M4a)
    > VER5のsource_sense_ja(独立導出) > GEN5のsource_sense_ja > sense_note_ja。取れなければ(None, None)。"""
    pg = (c.get("prod_gloss") or "").strip()
    if pg:
        return pg, "PROD_GLOSS"
    for key, src in (("verify.source_sense_ja", c.get("verify") or {}), ("source_sense_ja", c), ("sense_note_ja", c)):
        x = (src.get(key.split(".")[-1]) or "").strip()
        if x:
            return x, key
    return None, None


def _drop(log, c, stage, reasons):
    """Production追加: 除外したitemの段・理由をlogへ記録(Trialのlog listは別に維持)。"""
    log.setdefault("drops", []).append({"key": c.get("key"), "span": c.get("span"), "stage": stage, "reasons": [str(r) for r in reasons]})


def revert_to_span(c, log, why, key="reverted_to_span"):
    """M1: 意味が変わった一般化は、形を本文の形(lemma化)へ、訳も本文語義へ戻す。訳が取れずに形が変わる場合は除外(False)。"""
    orig = revert_form(c)
    gl, gsrc = span_gloss(c)
    changed = orig != c["display_form"]
    if changed and not gl:
        log.setdefault("reverted_dropped_no_gloss", []).append({"span": c["span"], "from": c["display_form"], "issue": why})
        _drop(log, c, STAGE_VERIFY if key == "reverted_to_span" else STAGE_CHECK, [f"本文の形へ戻す際に本文語義の訳が取れない: {why}"])
        return False
    log.setdefault(key, []).append({"span": c["span"], "from": c["display_form"], "to": orig, "gloss_from": c.get("gloss_ja"), "gloss_to": gl or c.get("gloss_ja"),
                                    "gloss_src": gsrc, "issue": why})
    c["display_form_pre_revert"], c["gloss_pre_revert"] = c["display_form"], c.get("gloss_ja")
    c["display_form"], c["reverted"] = orig, True
    if gl:
        c["gloss_ja"], c["gloss_source"] = gl, gsrc
    return True


# ============================================================
# 工程(Trial: M3.select/pick, kpg04.generalize5/verify5/run_check の移植)
# ============================================================
def select(text, cands, log, ctx, *, label="SEL"):
    """SEL(塊価値判定1 pass、luna)。判定付き候補のlist(全件)を返す。label=監査用の呼出名(J2是正の再判定は"SEL_DEFERRED")。"""
    if not cands:
        return []
    o, m = call_llm("sel", prompt_S3(text, cands, "span"), SEL3_SCHEMA, ctx, label=label)
    log["stages"].append({"stage": label, **_meta(m)})
    jm = {j["id"]: j for j in o["judgements"] if 1 <= j["id"] <= len(cands)}
    out = []
    for i, c in enumerate(cands, 1):
        j = jm.get(i)
        cc = dict(c)
        if j:
            cc.update(cls=j["cls"], chunk_type=j["chunk_type"], chunk_reason_ja=j["reason_ja"], difficulty=j["difficulty"],
                      keep=bool(j["keep"] and j["cls"] == "C" and not j["passive_fragment"]), passive_fragment=j["passive_fragment"], judged=True)
        else:
            cc.update(cls="?", chunk_type="none", chunk_reason_ja="", difficulty="upper_intermediate", keep=False, passive_fragment=False, judged=False)
        out.append(cc)
    log.setdefault("judged", []).extend([{"span": c["span"], "display_form": c.get("display_form"), "cls": c["cls"], "difficulty": c["difficulty"],
                                           "keep": c["keep"], "reason": c["chunk_reason_ja"]} for c in out])
    return out


def pick(judged, cap):
    """keep済みを難易度順(advanced先)・同順位は元の順で並べ、重複(span包含/同一display_form)を除いてcapまで。易しいものは除外せず後ろに並べるだけ。"""
    ks = [c for c in judged if c["keep"]]
    ks.sort(key=lambda c: RANK.get(c["difficulty"], 1))
    out = []
    for c in ks:
        dfl = (c.get("display_form") or "").lower()
        if any(_contains(c["span"], o["span"]) or _contains(o["span"], c["span"]) for o in out):
            continue
        if dfl and any((o.get("display_form") or "").lower() == dfl for o in out):
            continue
        out.append(c)
    return out[:cap]


def generalize5(text, cands, log, ctx, *, label="GEN5"):
    if not cands:
        return []
    o, m = call_llm("gen5", prompt_G5(text, cands), GEN5_SCHEMA, ctx, label=label)
    log["stages"].append({"stage": label, **_meta(m)})
    gm = {x["id"]: x for x in o["items"]}
    items = []
    for i, c in enumerate(cands, 1):
        x = gm.get(i)
        if not x:
            log.setdefault("gen_missing", []).append(c["span"])
            _drop(log, c, STAGE_GENERALIZE, ["GEN5の出力に当該項目が無い"])
            continue
        df, err = G.assemble(c["span"], x["tokens"])
        if df is None:
            log.setdefault("assemble_failed", []).append({"span": c["span"], "err": err})
            _drop(log, c, STAGE_GENERALIZE, [f"一般形の組立に失敗: {err}"])
            continue
        df2, st = reconcile(df, x["headword_frame"])
        if st in ("SLOT_TYPE_OVERRIDDEN", "SLOT_INSERTED"):
            ok, _ = display_check(df2, c["span"])
            if ok:
                log.setdefault("slot_type_overridden" if st == "SLOT_TYPE_OVERRIDDEN" else "slot_inserted", []).append(
                    {"span": c["span"], "tokens_form": df, "headword_frame": x["headword_frame"], "adopted": df2})
                df = df2
            else:
                st = "FRAME_MISMATCH"
        ok, why = display_check(df, c["span"])
        if not ok:
            log.setdefault("gen_validator_dropped", []).append({"span": c["span"], "display_form": df, "why": why})
            _drop(log, c, STAGE_GENERALIZE, [f"一般形の検査(display_check)不通過: {w}" for w in why])
            continue
        items.append(dict(c, display_form=df, gloss_ja=x["gloss_ja"], sense_note_ja=x["sense_note_ja"], generalization_note_ja=x["note_ja"],
                          tokens=[(t["n"], t["label"], t["lemma"]) for t in x["tokens"]], source_sense_ja=x["source_sense_ja"], arg_notes=x["arg_notes"],
                          headword_frame=x["headword_frame"], frame_change=x["frame_change"], reconcile=st))
    return items


def verify5(text, items, log, ctx):
    if not items:
        return []
    o, m = call_llm("ver5", prompt_V5(text, items), VER5_SCHEMA, ctx, label="VER5")
    log["stages"].append({"stage": "VER5", **_meta(m)})
    vd = {x["id"]: x for x in o["verdicts"]}
    final = []
    for i, c in enumerate(items, 1):
        v = vd.get(i, {})                   # 判定欠落はTrial確定版どおり {} 扱い(OK相当)。件数はn5.stats.verify_missingに記録(新Gateにしない)
        if i not in vd:
            log["verify_missing"] = log.get("verify_missing", 0) + 1
        c["verify"] = v
        if v.get("verdict") == "REJECT":
            log.setdefault("verify_dropped", []).append({"span": c["span"], "issue": v.get("issue")})
            _drop(log, c, STAGE_VERIFY, [f"VER5がREJECT: {v.get('issue')}"])
            continue
        c["gloss_pre_ver"] = c["gloss_ja"]
        form_fixed, fix_blocked = False, False
        if v.get("verdict") == "FIX":
            fx = strip_trailing_slot((v.get("fix_display_form") or "").replace(" / ", " ").strip())
            if fx and _norm_hw(fx) != _norm_hw(c["display_form"]):
                okf, whyf = display_check(fx, c["span"])
                gone = fix_drops_content(c["display_form"], fx) if okf else []
                if not okf:
                    fix_blocked = True
                    log.setdefault("fix_rejected_by_validator", []).append({"span": c["span"], "fix": fx, "why": whyf})
                elif gone:                       # M2: FIXがslot/CORE語を削る(訳に形を合わせる誤り型)。決定論で不採用
                    fix_blocked = True
                    log.setdefault("fix_rejected_slot_drop", []).append({"span": c["span"], "pre_fix": c["display_form"], "fix": fx, "dropped": gone, "fix_gloss": v.get("fix_gloss_ja")})
                else:
                    c["display_form_pre_fix"] = c["display_form"]
                    c["display_form"] = fx
                    form_fixed = True
            if fix_blocked:
                c["fix_rejected"] = True        # 不採用FIXの訳修正も採らない(削った形に合わせた訳のため)
            elif v.get("fix_gloss_ja"):
                c["gloss_ja"] = v["fix_gloss_ja"]
        why_rv = None
        if v.get("meaning_preserved") is False:
            why_rv = "meaning_preserved=false"
        elif v.get("frame_preserved") in FRAME_BAD and not form_fixed:
            why_rv = f"frame_preserved={v.get('frame_preserved')}(FIXなし)"
        elif v.get("argument_type_ok") is False and not form_fixed:
            why_rv = "argument_type_ok=false(FIXなし)"
            c["arg_unfixed"] = True
        if why_rv:
            if not revert_to_span(c, log, f"{why_rv}: {v.get('issue')}"):
                continue
        ok, why = display_check(c["display_form"], c["span"])
        if not ok:
            log.setdefault("validator_dropped", []).append({"span": c["span"], "display_form": c["display_form"], "why": why})
            _drop(log, c, STAGE_VERIFY, [f"検証後の形のdisplay_check不通過: {w}" for w in why])
            continue
        final.append(c)
    return final


def _check_call(text, tgt, log, ctx, label):
    o, m = call_llm("chk5", prompt_C5(text, tgt), CHK5_SCHEMA, ctx, label=label)
    log["stages"].append({"stage": label, **_meta(m)})
    return {x["id"]: x for x in o.get("checks", []) if x.get("relation") in CHK_REL}


def run_check(text, items, log, ctx):
    """CHK5(別系列独立検査、gpt-6.1-sol effort=low)。対象=revertされていない全件(Opus M8: Trial `scope='all'` は `not c.get('reverted')` で絞る)。
    結果は item['check']。修正はvalidator通過+訳つき+slot/CORE語を削らない場合のみ採用、直せなければ本文の形(訳も本文語義)へ戻す。
    Opus M9: 判定が欠落/不正なitemは**欠落分のみ1回**再呼出(技術retry)し、なお欠落なら除外(stage=n5_check、Eに数える)。Trial確定版は欠落を未検査のまま通過させていた(差異はDECISION_LOGに記録)。"""
    for c in items:
        c["flags"] = flag_item(c)
    tgt = [c for c in items if not c.get("reverted")]
    log["check_targets"] = [{"span": c["span"], "display_form": c["display_form"], "flags": c["flags"]} for c in tgt]
    if not tgt:
        return items
    ck = _check_call(text, tgt, log, ctx, "CHK5")
    missing = [i for i in range(1, len(tgt) + 1) if i not in ck]
    if missing:
        sub = [tgt[i - 1] for i in missing]
        ck2 = _check_call(text, sub, log, ctx, "CHK5_retry")
        log["check_missing_retry"] = {"first_missing": len(missing), "spans": [c["span"] for c in sub]}
        for j, i in enumerate(missing, 1):
            if j in ck2:
                ck[i] = ck2[j]
    dropped = []
    for i, c in enumerate(tgt, 1):
        x = ck.get(i)
        if not x:
            dropped.append(c)
            log.setdefault("check_missing_dropped", []).append({"span": c["span"], "display_form": c["display_form"]})
            _drop(log, c, STAGE_CHECK, ["CHK5の判定が欠落(再呼出しても得られず、未検査のまま提示しない)"])
            continue
        c["check"] = x
        rel = x["relation"]
        if rel in ("SAME", "MODIFIER_DROPPED_OK"):
            if rel == "MODIFIER_DROPPED_OK" and x.get("fix_gloss_ja"):
                c["gloss_pre_check"] = c["gloss_ja"]
                c["gloss_ja"] = x["fix_gloss_ja"]
        elif rel == "GLOSS_MISMATCH":
            if x.get("fix_gloss_ja"):
                c["gloss_pre_check"] = c["gloss_ja"]
                c["gloss_ja"] = x["fix_gloss_ja"]
            else:
                if not revert_to_span(c, log, x.get("reason_ja"), key="check_reverted_to_span"):
                    dropped.append(c)
        else:
            fx = strip_trailing_slot((x.get("fix_display_form") or "").replace(" / ", " ").strip())
            okf = bool(fx) and bool((x.get("fix_gloss_ja") or "").strip()) and display_check(fx, c["span"])[0] and not fix_drops_content(c["display_form"], fx)
            if okf:
                log.setdefault("check_fixed", []).append({"span": c["span"], "from": c["display_form"], "to": fx, "relation": rel, "gloss_from": c["gloss_ja"], "gloss_to": x["fix_gloss_ja"]})
                c["display_form_pre_check"], c["gloss_pre_check"] = c["display_form"], c["gloss_ja"]
                c["display_form"], c["gloss_ja"] = fx, x["fix_gloss_ja"]
            elif not revert_to_span(c, log, f"{rel}: {x.get('reason_ja')}", key="check_reverted_to_span"):
                dropped.append(c)
    return [c for c in items if c not in dropped]


def enforce_max_words(items, log):
    """Opus M6: 承認済み制約(5語以下)をN5形used_formにも既存ft.count_wordsで適用する。違反=既存の検証除外(stage=n5_verify)。
    (display_checkも語数1〜5を見るが、こちらはProductionの語数定義[スペース区切り、ft.count_words]で最終形を確認する。)"""
    out = []
    for c in items:
        wc = ft.count_words(c["display_form"])
        if not (1 <= wc <= MAX_WORDS):
            log.setdefault("max_words_dropped", []).append({"span": c["span"], "display_form": c["display_form"], "word_count": wc})
            _drop(log, c, STAGE_VERIFY, [f"N5形が{MAX_WORDS}語以下の承認済み制約に違反(実際: {wc}語)"])
            continue
        out.append(c)
    return out


def pack(c):
    """Trialのpack(kpg03 pack + kpg04拡張)と同じ内容(監査・replay比較用)。"""
    return dict(source_span=c["span"], source_sentence=c["sentence"], display_form=c["display_form"], gloss_ja=c["gloss_ja"],
                cls=c.get("cls"), chunk_type=c.get("chunk_type"), chunk_reason_ja=c.get("chunk_reason_ja"), difficulty=c.get("difficulty"),
                sense_note_ja=c.get("sense_note_ja"), generalization_note_ja=c.get("generalization_note_ja"), tokens=c.get("tokens"),
                verify=c.get("verify"), display_form_pre_fix=c.get("display_form_pre_fix"), reverted=c.get("reverted", False),
                display_form_pre_revert=c.get("display_form_pre_revert"),
                source_sense_ja=c.get("source_sense_ja"), headword_frame=c.get("headword_frame"), frame_change=c.get("frame_change"),
                reconcile=c.get("reconcile"), flags=c.get("flags", []), check=c.get("check"), display_form_pre_check=c.get("display_form_pre_check"),
                gloss_pre_revert=c.get("gloss_pre_revert"), gloss_pre_check=c.get("gloss_pre_check"), gloss_pre_ver=c.get("gloss_pre_ver"),
                gloss_source=c.get("gloss_source"), fix_rejected=c.get("fix_rejected", False), arg_unfixed=c.get("arg_unfixed", False), arg_notes=c.get("arg_notes"))


def new_log(tag: str) -> dict:
    return {"stages": [], "tag": tag, "flags_v1_hash": FLAGS_V1_HASH}


def generalize_verify_check(text, cands, ctx, *, tag="N5") -> tuple:
    """GEN5 -> VER5 -> CHK5 -> 5語以下(Trial run_Nの後半。cands=SEL/pick済みの{span, sentence, ...})。returns (final items, log)。"""
    log = new_log(tag)
    items = generalize5(text, cands, log, ctx)
    final = verify5(text, items, log, ctx)
    final = run_check(text, final, log, ctx)
    final = enforce_max_words(final, log)
    return final, log


def run_trial_equivalent(text, base_cands, ctx, *, cap=PHRASE_PICK_CAP) -> dict:
    """Trial run_N(gen='g5', ver='v5', check='all')と同じ工程(collect[Gate関数なし]->select->pick->GEN5->VER5->CHK5)。回帰test(Trial出力とのexact一致)専用の経路で、
    Production経路(pool_and_select/run_l3)の部品を同じ順で呼ぶ。5語制約(enforce_max_words)はTrialに無い追加のため呼ばない。"""
    log = new_log("N5")
    o, m = call_llm("b1", prompt_B1(text), B1_SCHEMA, ctx, label="B1_overgen")
    log["stages"].append({"stage": "B1_overgen", **_meta(m)})
    cands, rejected = collect_pool(text, base_cands, o["candidates"])
    judged = select(text, cands, log, ctx)
    kept = pick(judged, cap)
    items = generalize5(text, kept, log, ctx)
    final = verify5(text, items, log, ctx)
    final = run_check(text, final, log, ctx)
    return {"items": [pack(c) for c in final], "log": log, "pool_rejected": rejected}


# ============================================================
# L1: 候補プール(P7 ∪ B1過剰生成) -> 既存Gate -> SEL -> pick   (Opus M2/M3)
# ============================================================
def _fill_sentence(text, c):
    if not c.get("sentence"):
        for sent in text.replace("\n", " ").split(". "):
            if span_in_text(c["span"], sent):
                c["sentence"] = sent.strip()
                break


def collect_pool(text, base, b1_cands, *, gate_fn: Optional[Callable] = None, defer_out: Optional[list] = None) -> tuple:
    """Trial M3.collect の候補プール構築。base=P7候補[{span, sentence, ...}]、b1_cands=B1過剰生成[{span, sentence}]。
    gate_fn=None: Trialと完全同一(本文一致 -> span包含dedupe)。gate_fn指定(Production): B1候補は本文一致 -> **既存Gate(gate_fn)** -> span包含dedupe の順
    (Gateで落ちる候補が他の有効候補の包含dedupeを妨げないため)。gate_fn(c)->(c2|None, reasons)。最後にFRAG除外(P7候補にも適用=Trial同様)。
    defer_out(list、Production専用。委任_03 J2是正): 包含dedupeで落とした**B1候補**を{cand, blocked_by}で追記する(呼出側がSEL後に、包含相手がkeepでなければ再判定する)。None=Trialと完全同一。
    returns (pool, rejected[{span, stage, reasons, origin}])。"""
    cands = [dict(c, sentence=c.get("sentence") or "") for c in base]
    rejected = []
    for c in b1_cands:
        if not span_in_text(c["span"], text):
            rejected.append({"span": c["span"], "stage": STAGE_POOL, "reasons": ["B1候補が本文に連続一致しない"], "origin": "B1"})
            continue
        c = dict(c)
        if gate_fn is not None:
            c2, why = gate_fn(c)
            if c2 is None:
                rejected.append({"span": c["span"], "stage": STAGE_POOL, "reasons": list(why), "origin": "B1"})
                continue
            c = c2
        blk = next((b for b in cands if _contains(c["span"], b["span"])), None)
        if blk is not None:
            rejected.append({"span": c["span"], "stage": STAGE_POOL, "reasons": ["既存候補とspanが包含関係(重複)"], "origin": "B1", "blocked_by": blk["span"]})
            if defer_out is not None and toks(c["span"]) != toks(blk["span"]):      # 同一span(表記違い含む)の重複は再判定しない(同じ候補を2回判定しない)
                defer_out.append({"cand": c, "blocked_by": blk["span"]})
            continue
        cands.append(c)
    for c in cands:
        _fill_sentence(text, c)
    kept = []
    for c in cands:
        if FRAG.search(c["span"]):
            rejected.append({"span": c["span"], "stage": STAGE_POOL, "reasons": ["節の断片(関係詞・疑問詞始まり)は塊でない"], "origin": c.get("n5_origin") or "P7"})
            continue
        kept.append(c)
    return kept, rejected


def make_b1_gate(units: list, screen_fn: Optional[Callable] = None) -> Callable:
    """B1候補に既存のGate(本文一致+1〜5語+旧形式precheck[ft.validate_and_resolve]・CMU[er108]・Human NG/除外[screen_fn])を課す(Opus M2)。
    gate_fn(c)->(c2|None, reasons)。c2はn5_origin='B1'・item(build_original_itemsの原型)・span(=source_span)・sentence(=本文の文)を持つ。"""
    import er108_kp_cmu_lexicon_gate_01 as cmu

    def gate(c: dict):
        phrase = c["span"]
        v = ft.validate_and_resolve([{"phrase": phrase, "declared_word_count": ft.count_words(phrase)}], units)
        if v["item_reasons"]:
            return None, ["既存Gate(validate): " + " / ".join(v["item_reasons"][0]["reasons"])]
        rec = v["resolved"][0]
        cr = cmu.reasons_for_phrase(rec["phrase"])
        if cr:
            return None, ["既存Gate(CMU): " + " / ".join(cr)]
        if screen_fn is not None:
            why = screen_fn(rec["phrase"])
            if why:
                return None, [why]
        item = ft.build_original_items([rec])[0]
        return dict(c, span=rec["source_span"], sentence=rec["source_sentence"], n5_origin="B1", item=item), []
    return gate


def pool_and_select(text: str, p7_items: list, ctx: N5Ctx, *, include_b1: bool, units: Optional[list] = None, screen_fn: Optional[Callable] = None,
                    seen_keys: Optional[set] = None, cap: int = PHRASE_PICK_CAP, origin_label: str = "P7") -> dict:
    """L1: P7候補(p7_items=er105 original_items)∪B1過剰生成(include_b1、初回のみ) -> 既存Gate -> SEL -> pick(cap)。
    returns {"picked": [{"item", "n5_origin", "reason_ja", "difficulty", "cls", "chunk_type"}...pick順], "dropped": [er119 dropped形式。P7由来のSEL/pick除外のみ],
             "record": {...}, "log": {...}, "seen_keys": set}。
    補完(include_b1=False)では seen_keys(初回にjudge済み/採用済みのphrase_key)を除外してSELの再判定(同一判定の重複費用)を避ける。
    B1プールのGate除外・FRAG・包含dedupe・SEL非keep・pick超過は**Eに数えない**(Opus M3。stage=n5_pool/n5_select/n5_pick)。"""
    preflight()
    log = new_log(ctx.tag or "N5")
    seen = set(seen_keys or set())
    base = []
    for n, it in enumerate(p7_items, 1):
        k = ft.phrase_key(it["display_phrase"])
        if k in seen:
            continue
        base.append({"span": it["display_phrase"], "sentence": it.get("source_sentence") or "", "n5_origin": origin_label, "item": it, "p7_rank": n})
    b1 = []
    if include_b1:
        o, m = call_llm("b1", prompt_B1(text), B1_SCHEMA, ctx, label="B1_overgen")
        log["stages"].append({"stage": "B1_overgen", **_meta(m)})
        b1 = [dict(span=c["span"], sentence=c.get("sentence") or "") for c in o["candidates"]]
    gate = make_b1_gate(units, screen_fn) if (units is not None) else None
    defer = []
    pool, rejected = collect_pool(text, base, b1, gate_fn=gate, defer_out=defer)
    pool = [c for c in pool if ft.phrase_key(c["span"]) not in seen]
    judged = select(text, pool, log, ctx)
    # J2是正(委任_03): Trial 03のP7入力は保存済みProductionの最終候補(QA通過後)であり、QAで落ちる前のP7 sub-spanはpoolに存在しなかった。
    # 本配線のP7候補はQA前なので、sub-span(包含相手)がSELでkeepにならない場合はB1 supersetがTrial同様にpoolに残る条件を再現する(SEL後にdedupe)。
    # 包含相手がkeepのときは従来(Trial)どおりsuperset側を落とす。defer無しの場合は追加callなし=Trial exact。
    deferred_rejudged = []
    if defer:
        keep_spans = [c["span"] for c in judged if c["keep"]]
        second = []
        for d in defer:
            b = dict(d["cand"])
            _fill_sentence(text, b)
            if ft.phrase_key(b["span"]) in seen or FRAG.search(b["span"]):
                continue
            if any(_contains(b["span"], k) for k in keep_spans):
                continue                    # 包含相手がkeep: superset側を落とす(Trial逐語の挙動)
            if any(_contains(b["span"], o["span"]) for o in second):
                continue                    # 再判定候補同士の包含重複(先着を残す。Trialのcollectと同じ順序規則)
            second.append(b)
        if second:
            rejudged = select(text, second, log, ctx, label="SEL_DEFERRED")
            judged = judged + rejudged
            blk_of = {d["cand"]["span"]: d["blocked_by"] for d in defer}
            deferred_rejudged = [{"span": c["span"], "blocked_by": blk_of.get(c["span"]), "keep": c["keep"]} for c in rejudged]
            done = {r["span"] for r in deferred_rejudged}
            rejected = [r for r in rejected if not (r.get("blocked_by") and r["span"] in done)]
    for r in rejected:
        if r.get("blocked_by") and toks(r["span"]) == toks(r["blocked_by"]):
            r["reasons"] = ["既存候補と同一span(重複。Trialと同じ除外)"]
        elif r.get("blocked_by"):
            r["reasons"] = [r["reasons"][0] + f"(相手=『{r['blocked_by']}』。Trial差分: Trialのpoolは保存済みQA通過後のP7のみ。本実装は相手がSELでkeepでない場合にB1側をSEL再判定する。この件は再判定の条件に該当せずTrial同様に除外)"]
    kept = pick(judged, cap)
    kept_ids = {id(x) for x in kept}
    dropped = []
    for c in judged:
        if id(c) in kept_ids:
            continue
        if c.get("n5_origin") == "B1":
            continue                # B1過剰生成のSEL非keep/pick超過は監査recordのみ(AIが選んだ候補ではない=dropped一覧に出さない)
        st = STAGE_PICK if c["keep"] else STAGE_SELECT
        why = ("keepだが重複/上限(cap)で採用されず" if c["keep"] else f"塊価値判定でkeepでない(cls={c['cls']}, passive_fragment={c['passive_fragment']}): {c['chunk_reason_ja']}")
        dropped.append({"raw_rank": c.get("p7_rank"), "phrase": c["span"], "stage": st, "reasons": [why], "origin": "call1"})
    picked = [{"item": c["item"], "n5_origin": c["n5_origin"], "reason_ja": (c["item"].get("reason_ja") if c["n5_origin"] != "B1" else c.get("chunk_reason_ja")) or "",
               "difficulty": c.get("difficulty"), "cls": c.get("cls"), "chunk_type": c.get("chunk_type"), "sel_reason_ja": c.get("chunk_reason_ja")}
              for c in kept]
    rec = {"method": METHOD_ID, "include_b1": include_b1, "n_p7_in": len(base), "n_b1_returned": len(b1), "pool_size": len(pool),
           "pool_rejected": rejected, "pool_rejected_by_reason": _count_by(rejected, "stage"), "deferred_rejudged": deferred_rejudged, "n_judged": len(judged),
           "n_keep": sum(1 for c in judged if c["keep"]), "n_picked": len(kept), "picked_origin": {"P7": sum(1 for c in kept if c["n5_origin"] != "B1"),
                                                                                                "B1": sum(1 for c in kept if c["n5_origin"] == "B1")},
           "judged": log.get("judged"), "stages": log["stages"]}
    seen |= {ft.phrase_key(c["span"]) for c in judged}
    return {"picked": picked, "dropped": dropped, "record": rec, "log": log, "seen_keys": seen}


def _count_by(rows, key):
    out = {}
    for r in rows:
        out[r.get(key)] = out.get(r.get(key), 0) + 1
    return out


# ============================================================
# L3: GEN5 -> VER5 -> CHK5(canonicalization直後・CMU post-canonの前)  (Opus M1/M4/M5/M6/M8/M9)
# ============================================================
def run_l3(text: str, targets: list, ctx: N5Ctx) -> dict:
    """targets=[{"key", "span"(=selection_phrase、Opus M4b), "sentence", "prod_gloss"(P7由来のcanon・ga後japanese_glossのみ。B1由来はNone、Opus M4a), "n5_origin"}]。
    returns {"kept": {key: pack済みdict(+内部c)}, "dropped": [{"key","span","stage","reasons"}], "log": log}。"""
    preflight()
    cands = [dict(span=t["span"], sentence=t["sentence"], key=t["key"], prod_gloss=t.get("prod_gloss"), n5_origin=t.get("n5_origin") or "P7") for t in targets]
    final, log = generalize_verify_check(text, cands, ctx, tag=ctx.tag or "N5")
    kept = {c["key"]: c for c in final}
    drops = [d for d in log.get("drops", []) if d["key"] not in kept]
    seen = set()
    uniq = []
    for d in drops:                 # 1 itemが複数回記録される場合(revert失敗等)は最初の1件
        if d["key"] in seen:
            continue
        seen.add(d["key"])
        uniq.append(d)
    return {"kept": kept, "dropped": uniq, "log": log}


def _norm_phrase(s: str) -> str:
    return " ".join(_norm_hw(s))


def apply_to_item(item: dict, c: dict, *, display_phrase: Optional[str] = None) -> dict:
    """N5確定後の(表示形, 日本語訳)の組をProduction itemへ反映する(Opus M5)。**item(merged item)をin-placeで更新して返す。**
    used_form==key_phrase(kc.merge_canonicalization_result同値不変条件)=N5形、japanese_gloss=N5確定gloss(japanese_gloss_ttsは再計算)、
    source_span/source_sentence/display_phrase=本文根拠(無変更)。canon由来でN5後に陳腐化するfield(gloss_alignment_status/gloss_alignment/changed_from_display_phrase/
    normalization_reason/reasoning/kp_extends_beyond_candidate/japanese_gloss_tts)は旧値を n5.canon_* へ退避し、N5の形と訳の組で決め直す。
    QA12(qa/qa_overall_status)は**canon形(N5前)**を判定した結果として無変更で保持する(解釈β′、CURRENT_SPEC記載)。"""
    import er003_key_words_canonicalization as kc
    pre = {k: json.loads(json.dumps(item.get(k))) for k in ("key_phrase", "used_form", "japanese_gloss", "japanese_gloss_tts", "changed_from_display_phrase",
                                                            "normalization_reason", "reasoning", "kp_extends_beyond_candidate", "gloss_alignment_status", "gloss_alignment")
           if k in item}
    new_form, new_gloss = c["display_form"], c["gloss_ja"]
    same_pair = (_norm_phrase(item.get("key_phrase") or "") == _norm_phrase(new_form)) and ((item.get("japanese_gloss") or "").strip() == (new_gloss or "").strip())
    n5 = pack(c)
    n5.update(method=METHOD_ID, origin=c.get("n5_origin"), canon_pre=pre, canon_key_phrase_pre=pre.get("key_phrase"), canon_gloss_pre=pre.get("japanese_gloss"),
              pair_unchanged_from_canon=same_pair, source_span_input=c["span"],
              source_span_matches_item=(_norm_phrase(item.get("source_span") or "") == _norm_phrase(c["span"])))
    item["n5"] = n5
    if same_pair:
        return item                  # 形・訳ともcanonと同じ=旧fieldは陳腐化しない(canonのgloss整合記録をそのまま残す)
    item["key_phrase"] = item["used_form"] = new_form
    item["japanese_gloss"] = new_gloss
    item["japanese_gloss_tts"] = kc.convert_display_gloss_to_tts_text(new_gloss)
    dp = display_phrase if display_phrase is not None else item.get("display_phrase")
    item["changed_from_display_phrase"] = _norm_phrase(new_form) != _norm_phrase(dp or "")
    item["normalization_reason"] = N5_NORMALIZATION_REASON if item["changed_from_display_phrase"] else "none"
    item["reasoning"] = f"[N5] {c.get('generalization_note_ja') or ''}".strip()
    item["kp_extends_beyond_candidate"] = False
    item["gloss_review_hint"] = False
    item["gloss_alignment_status"] = "ALIGNED"
    item["gloss_alignment"] = {"version": METHOD_ID, "status": "N5_CONFIRMED", "original_japanese_gloss": pre.get("japanese_gloss"),
                               "confirmed_by": ["VER5", "CHK5"], "reverted_to_span": bool(c.get("reverted")),
                               "check_relation": (c.get("check") or {}).get("relation"), "verify_verdict": (c.get("verify") or {}).get("verdict")}
    return item


def person_check_after_n5(items: list) -> list:
    """N5後の(表示形, 訳)に既存の決定論的人称整合検査(ga.person_reference_mismatch、API 0)を適用し、不整合のitemのrankを返す(Opus M5)。"""
    import er003_key_words_gloss_alignment as ga
    return [it["rank"] for it in ga.select_person_mismatches(items)]


# ============================================================
# 監査・preflight
# ============================================================
def _sha16(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


def prompt_shas() -> dict:
    """監査用(doc.generalization / 回帰test固定値)。固定ダミー入力(本文=[[BODY]]、候補1件)での全文sha256[:16]と、規則文・schemaのsha。"""
    cand = [dict(span="hear it out", sentence="She wanted to hear it out.", display_form="hear someone out", gloss_ja="最後まで聞く")]
    sj = lambda d: _sha16(json.dumps(d, ensure_ascii=False, sort_keys=True))     # noqa: E731
    return {
        "B1": _sha16(prompt_B1("[[BODY]]")), "SEL": _sha16(prompt_S3("[[BODY]]", cand, "span")), "GEN5": _sha16(prompt_G5("[[BODY]]", cand)),
        "VER5": _sha16(prompt_V5("[[BODY]]", cand)), "CHK5": _sha16(prompt_C5("[[BODY]]", cand)),
        "CHUNK_DEFS_V3+EXTRA_RULES_V3": _sha16(CHUNK_DEFS_V3 + "\n\n" + EXTRA_RULES_V3), "GEN5_EXTRA": _sha16(GEN5_EXTRA), "GEN2_RULES": _sha16(G.GEN2_RULES),
        "VER5_HEAD+VER5_ADD": _sha16(VER5_HEAD + VER5_ADD), "CHK5_RULES": _sha16(CHK5_RULES),
        "schema": {"B1": sj(B1_SCHEMA), "SEL": sj(SEL3_SCHEMA), "GEN5": sj(GEN5_SCHEMA), "VER5": sj(VER5_SCHEMA), "CHK5": sj(CHK5_SCHEMA)},
        "FLAGS_V1_HASH": FLAGS_V1_HASH,
    }


def audit_record() -> dict:
    return {"method": METHOD_ID, "trial_source": TRIAL_SOURCE, "approved": "APPROVED_FOR_PRODUCTION 2026-10-30 (user)",
            "models_requested": {s: STAGE_PARAMS[s]["model"] for s in STAGE_PARAMS},
            "params": {s: {k: v for k, v in STAGE_PARAMS[s].items() if k != "model"} for s in STAGE_PARAMS},
            "processes": dict(STAGE_PROCESS), "prompt_sha16": prompt_shas(), "wordnet_sha256": WORDNET_SHA256,
            "scope": "phrase(kind=phrase)のみ。単語(W5')は対象外"}


_PREFLIGHT_OK = False


def preflight() -> None:
    """API call前のfail-closed確認(WordNet資産・全モデルの単価登録)。失敗=N5ContractError/PricingNotFoundError(STOP。N5なしで続行しない)。初回のみ実行。"""
    global _PREFLIGHT_OK
    if _PREFLIGHT_OK:
        return
    _wn()
    for s, p in STAGE_PARAMS.items():
        _price_per_m(p["model"])
    _PREFLIGHT_OK = True
