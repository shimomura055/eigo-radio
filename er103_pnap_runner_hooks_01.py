# -*- coding: utf-8 -*-
"""固有名詞アラーム方針(PROPER-NOUN-PRONUNCIATION-ALARM-POLICY-PRODUCTION-01)のFamily X/Z runner共通hook(配線点5-2/5-3/5-6/5-7)。
flag(`PROPER_NOUN_ALARM_POLICY_ENABLED`)がOFFのときは**何もしない**(scope非設定・hook非実行=従来と同一)。
ONのときのみ: run scopeをcontext manager+finallyで設定し(OF-PNAP-P-10)、runの終了時(正常終了・STOP・途中失敗のいずれでも=finally)に
`audit/pronunciation_alarms.json`・`audit/operator_alarm_report.md`を再導出して標準出力へも出す(OF-PNAP-P-08)。"""
from __future__ import annotations

import os
import sys

import er103_proper_noun_alarm_policy_01 as pnap
import er103_pronunciation_tts_supply_01 as pnap_supply
import er103_run_entity_table_01 as ret   # ASR-QUALITY PN 委任_04(OPEN-472): Run Entity Table。有効条件は ret.is_active_for_run() の単一関数のみ


def emit_alarm_report(level_dir: str, table=None) -> dict:
    """level_dir/audit/ にアラーム報告を書き、完成報告(標準出力)へ同じ内容を出す。例外を投げない。
    RET有効時(ret.is_active_for_run())のみ、実体表サマリ(表の根拠。Ledger/Perplexity根拠とは別欄)をreportへ追記する(A-16)。RET不活性/rollback時は従来とバイト一致。"""
    rep = pnap.write_run_alarms_safe(level_dir, supply_list=pnap_supply.applied_supplies())
    try:
        if ret.is_active_for_run() and rep.get("md") and os.path.exists(rep["md"]):
            with open(rep["md"], "a", encoding="utf-8") as f:
                f.write("\n### 実体表(固有名詞と認識した根拠。受理判定用。発音の根拠[Ledger/Perplexity調査]とは別)\n"
                        + "\n".join("- " + ln for ln in ret.operator_report_lines(table)) + "\n")
    except Exception as exc:  # noqa: BLE001
        print(f"[WARN][entity_table] 報告への実体表サマリ追記に失敗: {type(exc).__name__}: {exc}", file=sys.stderr)
    try:
        if rep.get("md") and os.path.exists(rep["md"]):
            with open(rep["md"], encoding="utf-8") as f:
                body = f.read()
            print(f"\n===== 固有名詞発音アラーム報告 ({level_dir}) =====\n{body}", file=sys.stdout)
    except Exception as exc:  # noqa: BLE001
        print(f"[WARN][pronunciation_alarms] 報告の標準出力に失敗: {type(exc).__name__}: {exc}", file=sys.stderr)
    return rep


def run_with_alarm_hook(family: str, level_dir: str, fn, *args, _ret_provider=None, **kwargs):
    """flag OFF -> fn(*args, **kwargs) をそのまま呼ぶ。ON -> scope(X|Z)内で実行し、finallyでアラーム報告を出す。
    ASR-QUALITY PN 委任_04(RET、構築点=本関数1か所): scope内かつ ret.is_active_for_run() のとき、`fn`の直前に`_ret_provider()`(provider factory)から
    run単位の実体表を構築し(未カバーtextのみNER。失敗は縮退して表なし=現行)、`fn`の間だけ`ret.run_table`で保持する(finallyで必ず復元)。
    runner本体関数は無変更。dry_run/scope外/PNAP OFFではここに入らない(API 0)。"""
    if not pnap.is_enabled():
        return fn(*args, **kwargs)
    with pnap.run_scope(family):
        pnap_supply.clear_registry()
        table = None
        try:
            if _ret_provider is not None and ret.is_active_for_run():
                table = ret.ensure_table_safe(_ret_provider())
            with ret.run_table(table):
                return fn(*args, **kwargs)
        finally:
            emit_alarm_report(level_dir, table)


def aggregate_article_alarms(article_dir: str, level_dirs: list) -> dict:
    """X: 記事単位(複数level)の集約。各level_dirのaudit/pronunciation_alarms.jsonを読み、`<article_dir>/audit/pronunciation_alarms_article.json`
    と`operator_alarm_report_article.md`を書く。1つでも集計失敗/不一致があれば明示する。例外を投げない。"""
    import json
    out = {"article_dir": article_dir, "levels": {}, "count": 0, "error": None}
    try:
        alarms, failures = [], []
        consist_ok = True
        supply = []
        for ld in level_dirs:
            jp = os.path.join(ld, "audit", "pronunciation_alarms.json")
            if not os.path.exists(jp):
                failures.append(f"{ld}: pronunciation_alarms.json なし(集計失敗または未実行)")
                continue
            with open(jp, encoding="utf-8") as f:
                d = json.load(f)
            out["levels"][ld] = d.get("count")
            if not (d.get("consistency") or {}).get("match", True):
                consist_ok = False
            alarms += d.get("alarms") or []
            supply += d.get("supply_applied") or []
        md = pnap.render_operator_report(
            alarms, supply_list=supply, consistency={"alarm_state_records": len(alarms), "reported": len(alarms), "match": consist_ok})
        if failures:
            md += "\n**アラーム集計失敗(一部level)**: " + " / ".join(failures) + "\n"
        os.makedirs(os.path.join(article_dir, "audit"), exist_ok=True)
        with open(os.path.join(article_dir, "audit", "pronunciation_alarms_article.json"), "w", encoding="utf-8") as f:
            json.dump({"policy_id": pnap.POLICY_ID, "operator_only": True, "count": len(alarms), "levels": out["levels"],
                       "failures": failures, "alarms": alarms}, f, ensure_ascii=False, indent=2, default=str)
        with open(os.path.join(article_dir, "audit", "operator_alarm_report_article.md"), "w", encoding="utf-8") as f:
            f.write(md)
        out["count"] = len(alarms)
        out["md"] = md
    except Exception as exc:  # noqa: BLE001
        out["error"] = f"{type(exc).__name__}: {exc}"
    return out


def family_scope(family: str, subdir: str):
    """Family X TTS段関数(第1引数=theme_out_dir)用decorator。level_dir=<theme_out_dir>/<subdir>。flag OFFなら素通し。"""
    import functools

    def deco(fn):
        @functools.wraps(fn)
        def wrapper(theme_out_dir, *args, **kwargs):
            return run_with_alarm_hook(family, f"{theme_out_dir}/{subdir}", fn, theme_out_dir, *args,
                                       _ret_provider=(lambda: ret.XProvider(theme_out_dir)), **kwargs)
        wrapper.__pnap_scoped__ = True
        return wrapper
    return deco


def attach_alarm_audit(summary: dict, out_dir: str, level: str) -> None:
    """X assembly summary(`run_summary_assemble.json`)へ固有名詞アラームの要約を機械的に埋め込む(非blocking。OF-PNAP-P-08)。
    flag OFFなら何も付けない(従来とバイト一致)。audit/pronunciation_alarms.json(runのfinally hookが出力)が無い場合は『集計失敗』を明示する。"""
    if not pnap.is_enabled():
        return
    import json
    jp = os.path.join(out_dir, "audit", "pronunciation_alarms.json")
    try:
        if not os.path.exists(jp):
            summary["pronunciation_alarm_audit"] = {"level": level, "status": "ALARM_AGGREGATION_FAILED",
                                                    "reason": "audit/pronunciation_alarms.jsonが存在しません", "blocking": False}
            return
        with open(jp, encoding="utf-8") as f:
            d = json.load(f)
        summary["pronunciation_alarm_audit"] = {
            "level": level, "status": "OK" if (d.get("consistency") or {}).get("match", True) else "ALARM_COUNT_MISMATCH",
            "count": d.get("count"), "nouns": sorted({a.get("proper_noun") for a in d.get("alarms") or []}),
            "report": os.path.join(out_dir, "audit", "operator_alarm_report.md"), "consistency": d.get("consistency"),
            "supply_applied": [(x.get("original"), x.get("respelling"), x.get("tier")) for x in d.get("supply_applied") or []],
            "blocking": False}
    except Exception as exc:  # noqa: BLE001
        summary["pronunciation_alarm_audit"] = {"level": level, "status": "ALARM_AGGREGATION_FAILED",
                                                "reason": f"{type(exc).__name__}: {exc}", "blocking": False}
