# -*- coding: utf-8 -*-
"""er110_family_y_opinion_based_03.py
FAMILY-Y-VOICES-DESIGN-01 委任_24: 『実在意見ベースの3 Voice生成』の**テーマ非依存の一般化**(DEV/Trial専用module)。

目的: 02 の runner はSNSテーマのSheet・World frame・WHO_JAをコード内に持つ。別テーマで再現Trialをするとき、
テーマ固有の情報(World frame・Persona Sheet・人物名ラベル)を**データ(THEME_DATA_*.json)から読む**ようにして、
コード・Promptにテーマ固有の語を増やさない(ユーザー原文§2: 今回の題材だけに依存するハードコードや個別Promptを増やさない)。

位置づけ(重要):
  - **未配線のDEV/Trial module**。どのProduction runner・既存er110 moduleからもimportされない(testでGrep固定)。import時にAPI呼出0・ファイル副作用0・client生成0。
    環境変数・flag・CLI引数でProduction挙動が変わる経路はない。
  - 02 の改訂Voice Prompt(VOICE_PROMPT_OB2=考え方A〜D入り)・render_persona_ob2・反復検出・OPENING_GUIDE を**そのまま再利用**する(Promptの文面は一字も変えない)。
    01(`er110_family_y_opinion_based_01.py`)・02 は**無変更**(run_01〜run_03の再現性を保つ)。差し替えは `patched_ob_03()` のwith内だけで、抜けると元に戻る。
  - **有料runは予算承認ファイルが無い限り起動しない**: `er110_output/family_y_opinion_based_03/BUDGET_APPROVED.json` ({"cap_jpy": <数値>, "runs": n}) が存在し、
    かつCLIに明示flag `--paid` がある場合のみ main() がAPIを呼ぶ。承認ファイルは本委任では作成していない(次委任でFableの委任文を根拠に作成)。
    起動はrun名のみ(許可リスト `RUN_DIRS_03`)。起動済みrunは再起動不可。出力先は `er110_output/` 配下に固定。
  - 新しい合格基準・閾値は作らない。出典照合・UNMAPPED再生成・予算の歯止めは 01 のまま。
"""
from __future__ import annotations

import contextlib
import copy
import json
import os
import sys
import traceback

import er053_family_x_factlock_ja_writer_01 as w1
import er110_family_y_text_trial_01 as y0
import er110_family_y_persona_pipeline_01 as pl
import er110_family_y_opinion_based_01 as ob
import er110_family_y_opinion_based_02 as ob2

MANAGEMENT_ID = ob.MANAGEMENT_ID
SLOTS = ob.SLOTS
THEME_FILE = "docs/research/FAMILY-Y-VOICES-DESIGN-01/OPINION_BASED_02/THEME_DATA_02.json"
RUN_DIRS_03 = {"run_01": "er110_output/family_y_opinion_based_03/redelivery_fee/run_01",
               "run_02": "er110_output/family_y_opinion_based_03/redelivery_fee/run_02"}
APPROVAL_FILE_03 = "er110_output/family_y_opinion_based_03/BUDGET_APPROVED.json"
LEDGER_MD_03 = "docs/research/FAMILY-Y-VOICES-DESIGN-01/OPINION_BASED_02/BUDGET_LOG_OB_04.md"

# Sheetに必須の欄(02のSheetが使う欄を正とする。relevant_termsは任意)
REQUIRED_SHEET_KEYS = tuple(k for k in ob2.SHEETS_02["voice_2"].keys() if k not in ("tbs_only", "r2plus_only", "relevant_terms"))     # 02が使う全欄(人物像・stake・arcを含む)


def validate_theme(theme: dict) -> None:
    """データ不備を、有料run前に止める(API 0)。欠落欄・未知の冒頭の型・relevant_termsが定義に無い・3 slot以外は例外。"""
    if set(theme["sheets"]) != set(SLOTS) or set(theme["who_ja"]) != set(SLOTS):
        raise ValueError("THEME_SLOTS_MISMATCH")
    terms = {d["term_ja"] for d in theme["world_frame"].get("distinctions", [])}
    for slot, sh in theme["sheets"].items():
        miss = [k for k in REQUIRED_SHEET_KEYS if k not in sh]
        if miss:
            raise ValueError(f"THEME_SHEET_MISSING_KEYS:{slot}:{miss}")
        if sh["opening_type"] not in ob2.OPENING_GUIDE_02:
            raise ValueError(f"THEME_UNKNOWN_OPENING_TYPE:{slot}:{sh['opening_type']}")
        bad = [t for t in (sh.get("relevant_terms") or []) if t not in terms]
        if bad:
            raise ValueError(f"THEME_RELEVANT_TERM_NOT_DEFINED:{slot}:{bad}")
        ids = [x["id"] for x in sh["experiences"]]
        if len(set(ids)) != len(ids) or not ids:
            raise ValueError(f"THEME_EXPERIENCE_IDS:{slot}")
        for x in sh["experiences"]:
            if x["kind"] not in ("E", "O") or not x["source_ids"]:
                raise ValueError(f"THEME_EXPERIENCE_FIELDS:{slot}:{x['id']}")


def load_theme(path: str = None) -> dict:
    """THEME_DATA(JSON)を読み、`r2plus_only`(=権利区分R2+/R3の出典だけが根拠の項目の印。公開前Gateの確認対象。前テーマの `tbs_only` を今回の意味に合わせて改名)を付けて返す。
    01の照合が読む旧名 `tbs_only` は、patched_ob_03 のwith内でだけ別名として付ける(01は無変更)。"""
    t = json.load(open(path or THEME_FILE, encoding="utf-8"))
    restricted = set(t.get("restricted_voice_ids", []))
    sheets = copy.deepcopy(t["sheets"])
    for sh in sheets.values():
        for x in sh["experiences"]:
            x["r2plus_only"] = bool(x["source_ids"]) and all(i in restricted for i in x["source_ids"])
    theme = {"theme_id": t["theme_id"], "world_frame": copy.deepcopy(t["world_frame"]), "sheets": sheets, "who_ja": dict(t["who_ja"])}
    validate_theme(theme)
    return theme


@contextlib.contextmanager
def patched_ob_03(cap_jpy: float, theme: dict, ledger_md: str = LEDGER_MD_03):
    """01の runner を、テーマデータ(Sheet・WHO_JA)+02の改訂Prompt/render/OPENING_GUIDE+予算で動かす(with内だけ差し替え)。"""
    saved = {k: getattr(ob, k) for k in ob2._PATCH_KEYS}
    orig_build = saved["build_voice_prompt_ob"]
    sheets = copy.deepcopy(theme["sheets"])
    for _sh in sheets.values():                                    # 01の照合は旧名 tbs_only を読む(with内の写しにだけ別名を付ける。themeそのものは変更しない)
        for _x in _sh["experiences"]:
            _x["tbs_only"] = _x["r2plus_only"]

    def build(wf: dict, slot: str, emphasize: bool = False) -> str:
        """区別の定義を、Sheetの relevant_terms にある用語だけに絞って 01 のbuilderへ渡す(未指定のSheetは全件)。"""
        terms = sheets[slot].get("relevant_terms")
        wf2 = copy.deepcopy(wf)
        if terms is not None:
            wf2["distinctions"] = [d for d in wf2.get("distinctions", []) if d["term_ja"] in terms]
        return orig_build(wf2, slot, emphasize)
    try:
        ob.SHEETS, ob.VOICE_PROMPT_OB, ob.render_persona_ob = sheets, ob2.VOICE_PROMPT_OB2, ob2.render_persona_ob2
        ob.build_voice_prompt_ob = build
        ob.WHO_JA, ob.OPENING_GUIDE, ob.BUDGET_STOP_JPY, ob.LEDGER_MD = theme["who_ja"], ob2.OPENING_GUIDE_02, float(cap_jpy), ledger_md
        yield
    finally:
        for k, v in saved.items():
            setattr(ob, k, v)


def run_pipeline_03(client, rd: str, *, cap_jpy: float, theme: dict = None, ledger_md: str = LEDGER_MD_03) -> dict:
    theme = theme or load_theme()
    with patched_ob_03(cap_jpy, theme, ledger_md):
        st = ob.run_pipeline(client, rd, wf=theme["world_frame"], ledger_md=ledger_md)
    reps = {s: ob2.repetition_report(st["final_texts"][s]) for s in SLOTS}
    st["repetition_03"] = reps
    w1.wj(os.path.join(rd, "repetition_report_03.json"), reps)
    w1.wj(os.path.join(rd, "state.json"), st)
    return st


def read_cap(path: str = None):
    """予算承認ファイルから「1runあたりの上限」(cap_jpy / runs)を読む。無い・不正なら None(= 有料runを起動しない)。runs省略時は1。"""
    try:
        d = json.load(open(path or APPROVAL_FILE_03, encoding="utf-8"))
        v = float(d["cap_jpy"]) / max(1, int(d.get("runs", 1)))
        return v if v > 0 else None
    except Exception:  # noqa: BLE001
        return None


def main(run_name=None, paid: bool = False) -> int:
    """run_name は RUN_DIRS_03 のキーのみ。有料runは paid=True(CLI `--paid`)かつ予算承認ファイルがある場合のみ。テーマデータの不備は有料run前に止める(API 0)。"""
    if run_name not in RUN_DIRS_03:
        print(f"[OB3] run名が不正(run_01 / run_02 のいずれかを引数に指定): {run_name!r}", flush=True)
        return 7
    rd = RUN_DIRS_03[run_name]
    ledger_md = LEDGER_MD_03
    if os.path.exists(os.path.join(rd, "entry_point.json")):
        print(f"[OB3] already launched: {rd}/entry_point.json exists (再起動不可)", flush=True)
        return 5
    if not paid:
        print("[OB3] 有料runには CLI明示flag `--paid` が必要。flagが無いため起動しない(API 0)", flush=True)
        return 8
    cap = read_cap()
    if cap is None:
        print(f"[OB3] 予算承認ファイル({APPROVAL_FILE_03})が無い/不正のため、有料runを起動しない(API 0)", flush=True)
        return 6
    try:
        theme = load_theme()                      # 不備があれば有料run前にここで止まる
    except Exception as e:  # noqa: BLE001
        print(f"[OB3] テーマデータが不正のため起動しない(API 0): {e!r}", flush=True)
        return 9
    os.makedirs(rd, exist_ok=True)
    import er005_cost_logger as cl
    import er003_v1_en_direct_vfl_01_generate as vfl01
    cl.install(os.path.join(rd, "raw_usage_log.jsonl"))
    w1.wj(os.path.join(rd, "entry_point.json"), {"runner": "er110_family_y_opinion_based_03.py", "management_id": MANAGEMENT_ID, "run_name": run_name, "run_dir": rd, "theme_id": theme["theme_id"],
                                                 "theme_file": THEME_FILE, "started": pl.now_iso(), "writer_model": ob.MODEL_TOP, "judge_model": ob.MODEL_CHEAP, "budget_stop_jpy_per_run": cap,
                                                 "flags": "なし(予算承認ファイルの金額のみ。引数はrun名のみ)"})
    try:
        client = vfl01.get_client()
        st = run_pipeline_03(client, rd, cap_jpy=cap, theme=theme, ledger_md=ledger_md)
        w1.wj(os.path.join(rd, "run_status.json"), {"status": "DONE", "gate_status": st.get("gate_status"), "final_cost_jpy": st.get("final_cost_jpy")})
        print("[OB3] DONE", flush=True)
        return 0
    except (pl.PipelineStop, y0.YStop) as e:
        code = getattr(e, "code", type(e).__name__)
        with patched_ob_03(cap, theme, ledger_md):
            ob.write_partial(rd)
        w1.wj(os.path.join(rd, "run_status.json"), {"status": "STOP", "code": code, "message": str(e)})
        print(f"[OB3] STOP {code}: {e}", flush=True)
        return 4
    except Exception as e:  # noqa: BLE001
        w1.wj(os.path.join(rd, "run_status.json"), {"status": "ERROR", "error": repr(e), "trace": traceback.format_exc()})
        print(f"[OB3] ERROR {e!r}", flush=True)
        return 4


if __name__ == "__main__":
    _args = sys.argv[1:]
    _paid = "--paid" in _args
    _pos = [a for a in _args if a != "--paid"]
    sys.exit(main(_pos[0] if len(_pos) == 1 else None, paid=_paid))
