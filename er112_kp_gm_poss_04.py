# -*- coding: utf-8 -*-
"""FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_14: 課題② 見出し語の人称placeholder — DEV/Trial実装(possessor_roles + 決定論写像/修復)。

位置づけ: DEV/Trial専用。Productionモジュール(er003_*/er105_*)・Prompt・template・flag・閾値は**一切編集しない**。
`install_poss_patches()`を明示的に呼ぶまで何も差し替えない(import副作用0・既定OFF)。Production到達経路: 無し。
正式配線は未承認(Offline Trial -> VALIDATED -> ユーザー正式採用 -> Production実装)。

設計: docs/research/FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01/DESIGN_06.md §2。
  - fulltext専用schemaの`rank`直後に`possessor_roles`(display内の所有格1個につき{token, role}を出現順に)を追加。
  - 再帰代名詞(yourself等)はroleを問わず決定論でself(閉じた表がoneselfのみ許可。変更なし)。
  - 決定論後処理: roleと見出し語(key)の食い違いを1トークン置換で修復(role / revert / none の3モード。API 0で事後比較できるよう生出力を全て記録)。
  - 置換しない(displayの語のまま)ことはどのroleでも常に許可。none/non_personなのに置換されていたらdisplayの語へrevert。
"""
from __future__ import annotations

import copy
import json
import re
import unicodedata

POSSESSIVES = ("my", "your", "his", "her", "its", "their", "our")
GENERIC_POSS = ("one's", "someone's", "somebody's")
ROLES = ("self", "other_person", "non_person", "none")
# 許可表の拡張(DESIGN_06 §2-3): my/ourにも別の人(someone's)を許可。Productionの表は編集せず、DEV install時にdictへ一時追加し、uninstallで元に戻す。
EXT_TABLE_ADD = {"my": {"someone's", "somebody's"}, "our": {"someone's", "somebody's"}}

_TOKEN_RE = re.compile(r"[A-Za-z0-9]+(?:['’\-][A-Za-z0-9]+)*")


def _norm_text(s: str) -> str:
    return unicodedata.normalize("NFKC", s or "").replace("’", "'")


def tokens(s: str) -> list:
    return _TOKEN_RE.findall(_norm_text(s))


def possessive_slots(display: str) -> list:
    """display内の所有格(POSSESSIVES)の位置。[(token_index, token_lower)]。"""
    return [(i, t.lower()) for i, t in enumerate(tokens(display)) if t.lower() in POSSESSIVES]


def validate_roles(roles, display: str) -> tuple:
    """(ok, reason)。要素数=display内の所有格数、tokenが出現順に一致、roleがenum内。"""
    slots = possessive_slots(display)
    if not isinstance(roles, list):
        return False, "roles_not_list"
    if len(roles) != len(slots):
        return False, f"count_mismatch(expected={len(slots)},got={len(roles)})"
    for k, (r, (_, tok)) in enumerate(zip(roles, slots)):
        if not isinstance(r, dict) or str(r.get("token", "")).strip().lower() != tok:
            return False, f"token_mismatch@{k}(expected={tok},got={r.get('token') if isinstance(r, dict) else r})"
        if r.get("role") not in ROLES:
            return False, f"role_not_in_enum@{k}({r.get('role')})"
    return True, ""


def _pair_ok(kt: str, dt: str, idx: int, key_tokens: list, window: list, ext: bool = True) -> bool:
    import er105_kp_fulltext_selector_01 as ft
    kl, dl = kt.lower(), dt.lower()
    if kl == dl:
        return True
    if ext and kl in EXT_TABLE_ADD.get(dl, ()):
        return True
    if ft._token_pair_ok(kt, dt, idx, key_tokens):
        return True
    try:
        import er112_kp_gm_trial_01 as t1
        if t1._ref_pair_ok(kt, dt, idx, key_tokens, window):
            return True
    except Exception:
        pass
    return False


def find_window(key: str, display: str):
    """keyがdisplayの連続トークン範囲の1対1置換で得られるときの開始index(最初に見つかったもの)。無ければNone。"""
    k, d = tokens(key), tokens(display)
    if not k or len(k) > len(d):
        return None
    for start in range(0, len(d) - len(k) + 1):
        w = d[start:start + len(k)]
        if all(_pair_ok(kt, dt, i, k, w) for i, (kt, dt) in enumerate(zip(k, w))):
            return start
    return None


def _replace_token(key: str, idx: int, new: str) -> str:
    """key文字列のidx番目のtoken(_TOKEN_RE)をnewに置換(周囲の文字列は保持。先頭大文字は引き継ぐ)。"""
    s = _norm_text(key)
    for n, m in enumerate(_TOKEN_RE.finditer(s)):
        if n == idx:
            old = m.group(0)
            repl = (new[:1].upper() + new[1:]) if old[:1].isupper() else new
            return s[:m.start()] + repl + s[m.end():]
    return key


def desired_for_role(role: str, display_tok: str):
    """role -> 許可する一般形の集合(置換する場合)。displayの語のまま(置換しない)は常に許可。"""
    if role == "self":
        return {"one's"}
    if role == "other_person":
        return {"someone's", "somebody's"}
    return set()   # non_person / none: 一般形は不可(displayの語のまま)


def repair_item(display: str, key: str, roles, mode: str = "role") -> dict:
    """mode: 'role'(roleに合わせてトークン1個を置換) / 'revert'(食い違いはdisplayの語へ戻す) / 'none'(修復しない)。
    戻り値: {key_after, status, repairs[], roles_ok, roles_reason, window_start}
    status: NO_POSSESSIVE / UNVERIFIED_ROLES / NO_WINDOW / NO_CHANGE / REPAIRED / DISABLED。
    修復は語数不変の1対1トークン置換のみ(既存validator er105/is_valid_inflection_normalizationを通る形のまま)。"""
    out = dict(key_after=key, status="NO_POSSESSIVE", repairs=[], roles_ok=None, roles_reason="", window_start=None)
    slots = possessive_slots(display)
    if not slots:
        return out
    ok, why = validate_roles(roles, display)
    out["roles_ok"], out["roles_reason"] = ok, why
    if mode == "none":
        out["status"] = "DISABLED"
        return out
    if not ok:
        out["status"] = "UNVERIFIED_ROLES"      # 迷えば触らない(現行どおり)。件数を記録して測る
        return out
    start = find_window(key, display)
    out["window_start"] = start
    if start is None:
        out["status"] = "NO_WINDOW"
        return out
    d = tokens(display)
    kt = tokens(key)
    new_key = key
    for ord_, ((di, dtok), r) in enumerate(zip(slots, roles)):
        ki = di - start
        if ki < 0 or ki >= len(kt):
            continue    # 所有格が窓の外(keyに含まれない)
        cur = kt[ki].lower()
        if cur not in GENERIC_POSS:
            continue    # 置換していない(displayの語のまま等)=常に許可
        role = r["role"]
        allowed = desired_for_role(role, dtok)
        if cur in allowed:
            continue
        if mode == "role" and role in ("self", "other_person"):
            target = "one's" if role == "self" else "someone's"
            rule = "role_%s" % role
        else:
            target = dtok
            rule = "revert_%s" % role
        new_key = _replace_token(new_key, ki, target)
        out["repairs"].append(dict(ordinal=ord_, display_token=dtok, role=role, before=cur, after=target, rule=rule))
    out["key_after"] = new_key
    out["status"] = "REPAIRED" if out["repairs"] else "NO_CHANGE"
    return out


def recompute_fields(item: dict, display: str, new_key: str) -> dict:
    """修復後のchanged_from_display_phrase / normalization_reason / QA実効値を決定論で再計算(OF-D5-02(iv))。
    前例: kc._qa_field_effective_verdict(er003_key_words_canonicalization.py)。変更点だけを返す。"""
    import er105_kp_fulltext_selector_01 as ft
    kn, dn = tokens(new_key), tokens(display)
    chg = {}
    same = [t.lower() for t in kn] == [t.lower() for t in dn]
    chg["changed_from_display_phrase"] = not same
    person_sub = any(t.lower() in GENERIC_POSS or t.lower() == "oneself" for t in kn)
    reason = item.get("normalization_reason")
    if same:
        chg["normalization_reason"] = "none"
    elif person_sub:
        chg["normalization_reason"] = "generalize_person_dependent_reference"
    elif reason == "generalize_person_dependent_reference":
        chg["normalization_reason"] = "lemma_normalization" if ft.is_valid_inflection_normalization(new_key, display) else reason
    # QA: roleに従った(または置換しない)結果なので、人称一般化QAはPASS。連続範囲QAは決定論validator合格ならPASS。
    chg["qa_person_reference_generalized"] = "PASS"
    if item.get("qa_traceable_contiguous_span") == "FAIL" and (same or ft.is_valid_inflection_normalization(new_key, display)):
        chg["qa_traceable_contiguous_span"] = "PASS"
    return chg


# ------------------------------------------------------------------ prompt template (DEV copy。Production templateは不変)
ROLE_BLOCK = (
    "   **所有格のrole判定(置換を決める前に必ず行い、出力のpossessor_rolesに記録します)**: display_phraseに所有格(my/your/his/her/its/their/our)が含まれる場合、"
    "出現順にすべての所有格について、possessor_rolesへ1要素ずつ{token, role}を書いてください(display_phraseに所有格が無ければ空配列[])。"
    "目的格のher(told her the truthのher)など、所有格として働かないhis/herは、role=noneで1要素記録します。判定は次の2つの問いで行います。"
    "(1)その所有格が指す対象は、この表現の動作主(または表現が述べる経験・所有の主体)自身か。(2)その対象は人(擬人化された人称的な存在を含む)か、物・組織・場所・研究・概念か。"
    "role=self: 動作主自身を指す人(擬人化を含む)/ role=other_person: 動作主とは別の人 / role=non_person: 人でないもの(動作主自身であっても物・組織ならnon_person)/ role=none: 所有格として働かない。"
    "置換してよいのは、role=selfならone's、role=other_personならsomeone'sまたはsomebody'sだけです。role=non_person・noneの所有格は置換せず、そのまま残してください"
    "(物が動作主の決まった定型表現もそのまま残します)。**置換しない(display_phraseの語のまま残す)ことは、どのroleでも常に許されます**。判定に迷う場合、"
    "または特定の所有格を含むこと自体が表現の一部である場合は、置換しないでください。再帰代名詞(yourself/himself/herself/themselves)を一般化する場合は、roleにかかわらずoneselfにします。\n"
)

_POSS_EDITS = [
    # (old, new)  oldは元template(A-1適用後)に**ちょうど1回**存在しなければならない(drift guard)
    ("例: \"catch their attention\"→\"catch someone's attention\"、\"a piece of your attention\"→\"a piece of someone's attention\"。",
     "例(動作主自身の所有=self): \"lost his temper\"→\"lose one's temper\"。(動作主とは別の人の所有=other_person): \"praised their effort\"→\"praise someone's effort\"。"
     "(所有者が人でない=non_person): \"challenged its conclusions\"→\"challenge its conclusions\"(置換しない)。"),
    ("\"pumps its fist\"→\"pump its fist\"(人称の一般化と併用する場合は\"pump one's fist\")、",
     "\"lost his temper\"→\"lose his temper\"(人称の一般化と併用する場合は、規則3のpossessor_rolesに従い\"lose one's temper\")、"),
    ("この置換は必ずnormalization_reason=\"generalize_person_dependent_reference\"を使い、人称代名詞・所有格以外の語は一切変更しないでください。",
     ROLE_BLOCK + "   この置換は必ずnormalization_reason=\"generalize_person_dependent_reference\"を使い、人称代名詞・所有格以外の語は一切変更しないでください。"),
    ("(display_phraseに元々人称代名詞・所有格が含まれない場合は、該当なしとして常にPASS)",
     "(display_phraseに元々人称代名詞・所有格が含まれない場合は、該当なしとして常にPASS。possessor_rolesに従って一般化しなかった場合[non_person・none、または置換しない選択]もPASS)"),
]


def build_poss_template(base_template: str) -> str:
    t = base_template
    for old, new in _POSS_EDITS:
        if t.count(old) != 1:
            raise RuntimeError(f"poss template drift: anchor count={t.count(old)} for {old[:50]!r}")
        t = t.replace(old, new)
    return t


def build_poss_schema(base_schema: dict) -> dict:
    """base(=DEV fulltext schema)の`rank`直後にpossessor_rolesを挿入(properties順=生成順)。A/B/C・Production schemaは不変(deepcopy)。"""
    s = copy.deepcopy(base_schema)
    it = s["schema"]["properties"]["items"]["items"]
    props = {"rank": it["properties"]["rank"],
             "possessor_roles": {"type": "array", "items": {"type": "object", "properties": {
                 "token": {"type": "string"}, "role": {"type": "string", "enum": list(ROLES)}},
                 "required": ["token", "role"], "additionalProperties": False}}}
    props.update({k: v for k, v in it["properties"].items() if k != "rank"})
    it["properties"] = props
    it["required"] = list(props)
    s["name"] = "key_words_canonicalization_fulltext_poss_trial04"
    return s


def extract_items_from_message(user_message: str) -> dict:
    """canonicalization user_messageの末尾JSONから rank -> display_phrase。"""
    tail = user_message.split("【Key Phrase候補(JSON)】\n", 1)[1]
    arr = json.loads(tail)
    return {int(x["rank"]): x["display_phrase"] for x in arr}


def process_response_text(text: str, display_by_rank: dict, mode: str = "role") -> tuple:
    """LLM応答JSON textを後処理して(新text, log)を返す。possessor_rolesは取り除く(Production側は知らない欄)。"""
    parsed = json.loads(text)
    log = []
    for it in parsed.get("items", []):
        rank = it.get("rank")
        roles = it.pop("possessor_roles", None)
        disp = display_by_rank.get(rank)
        if disp is None:
            continue
        rec = dict(rank=rank, display=disp, roles=roles, key_before=it.get("key_phrase"), reason_before=it.get("normalization_reason"))
        r_role = repair_item(disp, it.get("key_phrase") or "", roles, "role")
        r_rev = repair_item(disp, it.get("key_phrase") or "", roles, "revert")
        rec["repair_role"] = r_role
        rec["repair_revert"] = r_rev
        use = {"role": r_role, "revert": r_rev}.get(mode)
        if use is not None and use["status"] == "REPAIRED":
            before = {f: it.get(f) for f in ("key_phrase", "changed_from_display_phrase", "normalization_reason", "qa_person_reference_generalized", "qa_traceable_contiguous_span")}
            it["key_phrase"] = use["key_after"]
            chg = recompute_fields(it, disp, use["key_after"])
            it.update(chg)
            rec["applied"] = dict(mode=mode, before=before, after={f: it.get(f) for f in before})
        log.append(rec)
    return json.dumps(parsed, ensure_ascii=False), log


# ------------------------------------------------------------------ gold(目視ラベル、t1_referent_table.py REF 由来。per-possessiveの出現順role)
def score_headword(display: str, key: str, gold_roles: list) -> str:
    """決定論スコア: CORRECT_GENERALIZED / KEPT(置換なし=許容) / WRONG / NA(窓なし)。gold_rolesは出現順(self/other_person/non_person/none)。
    1つでもWRONGならWRONG。全て置換なしならKEPT。置換が1つ以上で全て正しければCORRECT_GENERALIZED。"""
    slots = possessive_slots(display)
    start = find_window(key, display)
    if not slots or start is None or len(gold_roles) != len(slots):
        return "NA"
    kt = tokens(key)
    res = []
    for (di, dtok), g in zip(slots, gold_roles):
        ki = di - start
        if ki < 0 or ki >= len(kt):
            continue
        cur = kt[ki].lower()
        if cur not in GENERIC_POSS:
            res.append("KEPT")
        elif cur in desired_for_role(g, dtok):
            res.append("CORRECT_GENERALIZED")
        else:
            res.append("WRONG")
    if not res:
        return "NA"
    if "WRONG" in res:
        return "WRONG"
    return "CORRECT_GENERALIZED" if "CORRECT_GENERALIZED" in res else "KEPT"


# ------------------------------------------------------------------ DEV patch(trial_01のinstall_dev_patchesの上に重ねる。poss flagのarmだけ有効)
import threading   # noqa: E402

LOGS: dict = {}
_LOG_LOCK = threading.Lock()
_ORIG: dict = {}
_INSTALLED = False
POSS_ARMS = {
    # a1r_c: A-1 + possessor_roles(canonicalizationのみ。gloss/説明は呼ばない)。'a1_c'=C0A(trial_01の既存arm)
    "a1r_c": dict(a1=True, a2=False, a3=False, share=False, ctx=False, skip_gloss=True, skip_expl=True, poss=True),
    # a1r: gloss/説明まで通す(E2E用)
    "a1r": dict(a1=True, a2=False, a3=False, share=False, ctx=False, poss=True),
}


def install_poss_patches(mode: str = "role"):
    """trial_01.install_dev_patches()を呼んだ上で、(1)template (2)schema (3)decode後処理 (4)許可表(my/our)を重ねる。"""
    global _INSTALLED
    if _INSTALLED:
        return
    import er112_kp_gm_trial_01 as t1
    import er003_key_words_canonicalization as kc
    for k, v in POSS_ARMS.items():
        t1.ARMS[k] = dict(v)
    t1.install_dev_patches()
    _ORIG["load_prompt_template"] = kc.load_prompt_template
    _ORIG["make_canonicalization_fn"] = kc.make_canonicalization_fn
    _ORIG["table"] = {k: set(v) for k, v in kc._PERSON_DEPENDENT_TO_GENERIC.items()}
    poss_schema = build_poss_schema(t1._dev_schema())
    prev_load, prev_make = kc.load_prompt_template, kc.make_canonicalization_fn

    def p_load(path=kc.PROMPT_TEMPLATE_PATH):
        t = prev_load(path)
        c = t1.cur()
        if c and c.cfg.get("poss") and path == kc.FULLTEXT_PROMPT_TEMPLATE_PATH:
            return build_poss_template(t)
        return t

    def p_make(user_message, *a, **kw):
        c = t1.cur()
        poss = bool(c and c.cfg.get("poss"))
        if poss and kw.get("schema") is t1._PROD_FT_SCHEMA:
            kw["schema"] = poss_schema
        fn0 = prev_make(user_message, *a, **kw)
        if not poss:
            return fn0
        disp = extract_items_from_message(user_message)
        key = (c.arm, c.rep, c.unit)

        def fn():
            text, model, rid = fn0()
            try:
                new_text, log = process_response_text(text, disp, mode=mode)
            except Exception as e:   # noqa: BLE001  後処理失敗時は生出力をそのまま返す(現行と同じ挙動)
                with _LOG_LOCK:
                    LOGS.setdefault(key, []).append(dict(error=f"{type(e).__name__}: {e}", raw=text))
                return text, model, rid
            with _LOG_LOCK:
                LOGS.setdefault(key, []).append(dict(call=len(LOGS.get(key, [])) + 1, items=log, raw=text))
            return new_text, model, rid
        for attr in ("model", "reasoning_effort", "uses_web_search_tool", "uses_structured_output"):
            setattr(fn, attr, getattr(fn0, attr, None))
        return fn

    for dest, add in EXT_TABLE_ADD.items():
        kc._PERSON_DEPENDENT_TO_GENERIC[dest] = set(kc._PERSON_DEPENDENT_TO_GENERIC.get(dest, set())) | add
    kc.load_prompt_template = p_load
    kc.make_canonicalization_fn = p_make
    _INSTALLED = True


def uninstall_poss_patches():
    global _INSTALLED
    if not _INSTALLED:
        return
    import er112_kp_gm_trial_01 as t1
    import er003_key_words_canonicalization as kc
    kc.load_prompt_template = _ORIG["load_prompt_template"]
    kc.make_canonicalization_fn = _ORIG["make_canonicalization_fn"]
    kc._PERSON_DEPENDENT_TO_GENERIC.clear()
    kc._PERSON_DEPENDENT_TO_GENERIC.update(_ORIG["table"])
    t1.uninstall_dev_patches()
    _INSTALLED = False
