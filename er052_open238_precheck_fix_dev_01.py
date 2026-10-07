"""OPEN-238-PRECHECK-FALSE-POSITIVE-FIX-TRIAL-01 Trial/DEV専用ラッパ(Production非配線、既定では何もしない)。

Opus条件Cレビュー必須修正M1〜M3を反映:
 M1 厳格版抽出(extract_percentages_strict)は check_number_mismatch の foreign_observed 計算のみ。
    台帳値確認(expected/observed/_any_close)・all_ledger_pct・L322・runner L2585/L2838/L3090・
    coverage_checker L475 は現行(緩い)extract_percentages のまま。
 M2 runner.resolve_precheck_target_sentence(L8093)の対象文特定も厳格版。差し替えは「実行中の
    モジュール」へ(install(runner_module, precheck_module))。runnerが__main__の場合は呼び出し側が
    runnerをimportしてからmain()を呼ぶこと。カウンタで反映箇所を検証する。
 M3 half の直前語が first/second/last/latter/other/better/earlier/later なら不採用。
明示的に install() を呼んだ場合のみ有効。uninstall() で元に戻る。"""
import re

STRICT_PRIOR_BLOCK = {"first", "second", "last", "latter", "other", "better", "earlier", "later"}
_COMPARATIVE = {"more", "less", "fewer", "again", "as", "higher", "lower", "larger", "smaller",
                "greater", "bigger", "than"}
_DETERMINERS = {"the", "their", "its", "all", "these", "those"}
_CONJ = {"and", "or", "but", "so", "that", "is", "was", "are", "were", "had", "has", "to", "by", "in"}
_OF = {"of"}
STRICT_FOLLOW_ALLOW = _OF | _COMPARATIVE | _DETERMINERS | _CONJ

counters = {"strict_foreign": 0, "strict_locate": 0, "loose_extract_percentages": 0, "v2_calls": 0}
_state = {"installed": False, "orig": {}}
_WORD_AFTER = re.compile(r"\s+([A-Za-z]+)")
_WORD_BEFORE = re.compile(r"([A-Za-z]+)\s+$")


def extract_percentages_strict(text, _pre=None):
    """PERCENT_RE(現行)+分数語辞書(ホワイトリスト+M3)。分数語のみ文脈判定を行う。"""
    import er052_open233_self_recovery_precheck_01 as pre0
    pre = _pre or pre0
    text = text or ""
    out = set()
    for m in pre.PERCENT_RE.finditer(text):
        out.add(round(pre._to_float(m.group(1)), 2))
    for phrase, pct in pre.FRACTION_WORD_TO_PERCENT.items():
        for m in re.finditer(r"\b" + re.escape(phrase) + r"\b", text, re.I):
            s, e = m.start(), m.end()
            if s > 0 and (text[s - 1].isalnum() or text[s - 1] == "-"):
                continue
            if e < len(text) and text[e] == "-":
                continue
            pb = _WORD_BEFORE.search(text[:s])
            if pb and pb.group(1).lower() in STRICT_PRIOR_BLOCK:  # M3
                continue
            rest = text[e:]
            if rest.strip() == "" or not rest[:1].isspace():
                ok = True  # 文末 / 句読点・閉じ括弧等が直後
            else:
                wa = _WORD_AFTER.match(rest)
                if wa:
                    ok = wa.group(1).lower() in STRICT_FOLLOW_ALLOW
                else:
                    ok = True  # 空白の後が句読点など
            if ok:
                out.add(round(pct, 2))
    return out


def _make_v2(pre, orig_check):
    def check_number_mismatch_v2(fact, article_text, all_ledger_pct=None, all_ledger_cnt=None):
        counters["v2_calls"] += 1
        res = orig_check(fact, article_text, all_ledger_pct, all_ledger_cnt)  # 現行の全ゲート(緩い抽出)
        if res is None or not res.get("article_evidence", "").startswith("percent"):
            return res  # count種別は無変更
        expected = pre.extract_percentages(fact.get("numeric_value"))  # 台帳側は現行
        other = (all_ledger_pct or set()) - expected
        counters["strict_foreign"] += 1
        observed = extract_percentages_strict(article_text, pre)
        foreign = {o for o in observed if not pre._any_close({o}, other)}
        if not foreign:
            return None
        new = dict(res)
        new["foreign_values"] = sorted(foreign)
        new["article_evidence"] = f"percent values found in article not matching any ledger fact: {sorted(foreign)}"
        return new
    return check_number_mismatch_v2


def _make_locate_v2(pre, runner, orig_locate):
    def resolve_precheck_target_sentence_v2(article_text, finding):
        if finding.get("kind") != "number_mismatch":
            return orig_locate(article_text, finding)
        sentences = runner.split_sentences_generic(article_text)
        for v in finding.get("foreign_values") or []:
            for s in sentences:
                counters["strict_locate"] += 1
                nums = extract_percentages_strict(s, pre) | set(pre.extract_counts(s))
                if v in nums:
                    return s, "precheck_number_locate"
        return None, "not_locatable"
    return resolve_precheck_target_sentence_v2


def install(runner_module, precheck_module):
    """実行中モジュールへ差し替え。runner_module=None ならprecheckのみ。"""
    if _state["installed"]:
        raise RuntimeError("already installed")
    pre = precheck_module
    if runner_module is not None:
        assert runner_module.precheck is pre, "runner.precheck is not the given precheck module"
    orig_loose = pre.extract_percentages
    orig_check = pre.check_number_mismatch

    def counting_loose(text):
        counters["loose_extract_percentages"] += 1
        return orig_loose(text)
    _state["orig"] = {"pre": pre, "extract_percentages": orig_loose, "check_number_mismatch": orig_check,
                      "runner": runner_module}
    pre.extract_percentages = counting_loose
    pre.check_number_mismatch = _make_v2(pre, orig_check)
    if runner_module is not None:
        _state["orig"]["locate"] = runner_module.resolve_precheck_target_sentence
        runner_module.resolve_precheck_target_sentence = _make_locate_v2(pre, runner_module, _state["orig"]["locate"])
    _state["installed"] = True


def uninstall():
    if not _state["installed"]:
        return
    o = _state["orig"]
    o["pre"].extract_percentages = o["extract_percentages"]
    o["pre"].check_number_mismatch = o["check_number_mismatch"]
    if o.get("runner") is not None:
        o["runner"].resolve_precheck_target_sentence = o["locate"]
    _state["installed"] = False
    _state["orig"] = {}


def reset_counters():
    for k in counters:
        counters[k] = 0
