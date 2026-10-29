# -*- coding: utf-8 -*-
"""使い捨てtool A(FAMILY-Y-SURNAME-CHOICE-PRODUCTION-01 委任_04B。Opus条件Aレビュー M1〜M8 反映)。

目的: Family Y「夫が妻の姓を選ぶとき」run_02のV1人物紹介1行だけを、ユーザー指示(原文 USER_02 §2。個別是正)の固定文へ差替える。
**汎用opではない**: slug=surname_choice / run=run_02 / V1固定 / 対象5ファイルの旧file sha・旧行・新行・行番号・行数を定数で固定し、1つでも違えば拒否する(M4)。
再翻訳しない(本文=Voice発言の英語が変わるため)。紹介行だけを差替え、来歴(provenance.json)の整合を**期待旧値と一致する場合のみ**付替える(M2/M5)。
**API 0**(runner/Production moduleは編集せずimportのみ。LLMは一切呼ばない。呼ぼうとすると例外=_NoApiClient+予算0.01円)。

M1: tts_b1b / tts_a2 の来歴は付替えない。`downstream_stale`へ加える(fail-closed)。音声は04Cで再生成する(2起動。PLAN_04B_01.md 04C手順)。
M2: 付替えるshaはrunner自身の関数(R._sha / ys.canonical_body / g.cand_stage_input_sha / p2w.cand_marker)で再計算。「旧値一致かつ再計算後に変わるentry」の集合が
    宣言集合と完全一致しなければSTOP。
M3: kp_<lv>: (1)読取のみで確定item・文法・ニュアンスの出典文の逐語残存を事前検査 (2)cc.stale_or_rebind (3)新署名取得 (4)期待旧値sha(旧text|旧sig)一致時のみ付替え
    (5)kp_<lv>_result.jsonの署名・shaと整合検査。REBOUND後の確定物(keywords_canonicalized/vocab_confirmed/final)がsha系を除き退避版と内容一致(runnerのstage_kp内G1)。
M4: 対象5ファイルを定数固定。split_y_articleでtitle/lead/全voice body/V2・V3紹介/closing一致、support jsonに「father/父親」無し、Std KP3文がa2に逐語残存。
M5: rebinds履歴にtool_id・USER_02のpath+file sha・§2・旧/新行とsha・output_origin=human_patched_line・旧LLM response_idが新出力を生成していない旨。適用済みなら2回目はno-op。
M6: 触る領域をsha manifest付きで退避→一時ファイル+os.replace→provenanceはfile/KP変更の最後→失敗時は全復元。--rehearsal-dirでrun_02の複製に対して先に通す。
M7: 固定EN文をtranslate段と同じ ys.check_y_article(en) + Std決定論検査(std_gen.run_checks)で検査。JA固定行はcheck_intro(+Trial補助Gate PASS記録の参照)。

実行: .venv\\Scripts\\python.exe docs\\research\\FAMILY-Y-SURNAME-CHOICE-PRODUCTION-01\\tools\\apply_v1_intro_patch_01.py [--dry-run] [--rehearsal-dir <root>] --by <名>
  --rehearsal-dir <root>: <root>/surname_choice/run_02 を対象にする(run_02の複製。本体には一切書かない)。未指定=本体(04C)。
"""
from __future__ import annotations

import argparse
import contextlib
import copy
import datetime as dt
import hashlib
import io
import json
import os
import re
import shutil
import sys
import tempfile
from typing import Optional

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.chdir(ROOT)

TOOL_ID = "apply_v1_intro_patch_01"
SLUG, RUN = "surname_choice", "run_02"
REAL_RUN_ROOT = "er121_output/family_y_production_01"
THEME_PKG = "docs/research/FAMILY-Y-SURNAME-CHOICE-PRODUCTION-01/theme_packages/surname_choice_package_01.json"
REUSE_MANIFEST = "er121_output/family_y_production_01/surname_choice/run_01/reuse_r0/reuse_manifest.json"
USER_REF = "docs/pm/delegation_log/2026-10-29_FAMILY-Y-SURNAME-CHOICE-PRODUCTION-01_USER_02.md"
USER_REF_SHA256 = "d61c35967dd81ae958f92c010901542d35cea8057d30af8133ab28bcc11b3876"
USER_SPEC = "§2 人物紹介の一般化改善Trial(V1『父親』の誤紹介の是正。個別是正。一般化方式のProduction採用とは独立)"
OUTPUT_ORIGIN = "human_patched_line"
TRIAL_GATE_RESULT = "er121_output/family_y_intro_trial_01/surname/v1_gate_result.json"      # Trial REC案のcheck_intro+補助Gate(luna)PASS記録

JA_OLD = "最初に話すのは、婿養子として妻の姓を名乗る父親。妻の実家で、家族と暮らしている。"
JA_NEW = "最初に話すのは、妻の姓を名乗り、妻の実家で家族と暮らしている男性だ。"
EN_B1B_OLD = "The first speaker is a father who took his wife’s last name when he joined her family as an adopted son. He lives with his family at his wife’s parents’ home."
EN_A2_OLD = "The first speaker is a father. He took his wife’s last name and joined her family as an adopted son. He lives with his family at his wife’s parents’ home.  "
EN_NEW = "The first speaker is a man who took his wife’s last name. He lives with his family at his wife’s parents’ home."          # 記事表記のU+2019
EN_NEW_A2 = EN_NEW + "  "                                                                                                      # a2は行末空白2つへ正規化(既存の表記に合わせる)
# Std(a2)の文数: 旧a2のV1紹介行は3文、M7固定文(fixed2)は2文 -> a2の以降の全文の番号S<n>が1つずれ、a2の候補doc/確定レコードの source_sentence_id が全て本文とずれる
# (04Bリハーサルで HL_SENTENCE_MISMATCH を実測)。文数を保つ代替(split3)は --std-variant split3 で明示したときだけ使える(Fable決定が要る。既定=fixed2はハイライトGateで安全にSTOP)。
EN_NEW_A2_SPLIT3 = "The first speaker is a man. He took his wife’s last name. He lives with his family at his wife’s parents’ home.  "
STD_VARIANTS = {"fixed2": EN_NEW_A2, "split3": EN_NEW_A2_SPLIT3}
STD_VARIANT_NEW_SHA = {"fixed2": "dca0e4fabebcac764bfcd8eac4208321ced311277c41b44b5d62b06f419bbafb", "split3": "c5aa775ea3218e1d66fdf26600df29824b82a4f4bd512bedccb495fdcc600fde"}

# 対象5ファイル(M4: 旧file sha・旧行・新行・行番号・行数を固定。1つでも違えば拒否)
TARGETS = [
    {"rel": "text/article_ja.md", "old_sha": "7f5fe4c8dd6b319a9005dbb718a99444f44b923cecf43e6131501292466a4f0e", "line_no": 5, "n_lines": 15,
     "old": JA_OLD, "new": JA_NEW, "ends_nl": True},
    {"rel": "text/article_assembled.md", "old_sha": "7f5fe4c8dd6b319a9005dbb718a99444f44b923cecf43e6131501292466a4f0e", "line_no": 5, "n_lines": 15,
     "old": JA_OLD, "new": JA_NEW, "ends_nl": True},
    {"rel": "text/lead_intro/intros_final.json", "old_sha": "a91653b8b1c1e6ba99f962e0b384a6119d3f51989cfe59a4212959b17ca26bce", "line_no": 2, "n_lines": 5,
     "old": f'  "voice_1": "{JA_OLD}",', "new": f'  "voice_1": "{JA_NEW}",', "ends_nl": False},
    {"rel": "translate/b1b.md", "old_sha": "2fc717a75ea68899754d38d4fd118d0f02577adcee7ffe98a7ead45f14af3825", "line_no": 5, "n_lines": 15,
     "old": EN_B1B_OLD, "new": EN_NEW, "ends_nl": True},
    {"rel": "translate/a2.md", "old_sha": "73929763ae8261a72db25190a1b2ab3ab71458f2323c18e1e1daa5a228b2e5f2", "line_no": 5, "n_lines": 15,
     "old": EN_A2_OLD, "new": EN_NEW_A2, "ends_nl": True},
]
# 差替え後のfile sha(M4。適用前に算出して固定。一致しなければ拒否)
NEW_FILE_SHA = {
    "text/article_ja.md": "215c6595525b08e2312f7ad4af5c60062cf8cb372b4ce1add3520272f256b187",
    "text/article_assembled.md": "215c6595525b08e2312f7ad4af5c60062cf8cb372b4ce1add3520272f256b187",
    "text/lead_intro/intros_final.json": "88773778bd3b856b5724fa95985e0561a7cae87e61a2459cf1ae7abd7e663495",
    "translate/b1b.md": "180c1d36a74918a647ec6ef2933d8e486726afe80fbe31195f175997d58e60d1",
    "translate/a2.md": STD_VARIANT_NEW_SHA["fixed2"],
}


def set_std_variant(name: str) -> None:
    """a2のV1新行を切替える(モジュール定数を更新。TARGETS/NEW_FILE_SHA/rebinds履歴のline_new)。"""
    global EN_NEW_A2
    if name not in STD_VARIANTS:
        raise ToolRefused(f"--std-variant は {sorted(STD_VARIANTS)} のみ")
    EN_NEW_A2 = STD_VARIANTS[name]
    for t in TARGETS:
        if t["rel"] == "translate/a2.md":
            t["new"] = EN_NEW_A2
    NEW_FILE_SHA["translate/a2.md"] = STD_VARIANT_NEW_SHA[name]

# 宣言集合(M2): 来歴の入力/出力shaが変わるentry。これと完全一致しなければSTOP。tts_*は付替えずstale化(M1)。
DECLARED_CHANGED = ("text", "translate_b1b", "translate_a2", "support_b1b", "support_a2", "part2_cand_b1b", "part2_cand_a2", "part2_b1b", "part2_a2", "kp_b1b", "kp_a2")
DECLARED_STALE = ("tts_b1b", "tts_a2")
# 変更が起き得る領域(M6の退避対象)。これ以外のファイルが変わったら失敗扱い(復元)
MUTABLE_SUBTREES = ("text", "translate", "support", "key_phrases", "b1b/key_phrases", "a2/key_phrases", "study_text", "a2/study_text")
MUTABLE_FILES = ("provenance.json", "kp_review_pending.json", "study_text_slots.json", "voice_assignment.json",
                 "audit/highlight_resolution_b1b.json", "audit/highlight_resolution_a2.json",
                 "b1b/audit/confirmed_selection.json", "a2/audit/confirmed_selection.json")
RUN_LOCK_NAME = "RUN_LOCK.json"
LEVELS = ("b1b", "a2")


class ToolRefused(Exception):
    pass


class _NoApiClient:
    """LLM client。何かを呼ぼうとしたら例外(本toolはAPI 0)。"""
    def __getattr__(self, name):
        raise RuntimeError(f"{TOOL_ID}: API呼出が試みられました({name})。本toolはAPI 0です")


def _sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _sha_text(s: str) -> str:
    return _sha_bytes(s.encode("utf-8"))


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def _read_bytes(p: str) -> bytes:
    with open(p, "rb") as f:
        return f.read()


def _write_atomic(path: str, data: bytes) -> None:
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_v1patch_")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        os.replace(tmp, path)
    except BaseException:
        with contextlib.suppress(OSError):
            os.remove(tmp)
        raise


def tree_manifest(run_dir: str) -> dict:
    out = {}
    for root, _dirs, files in os.walk(run_dir):
        for n in files:
            p = os.path.join(root, n)
            rel = os.path.relpath(p, run_dir).replace("\\", "/")
            if rel == RUN_LOCK_NAME or n.startswith(".tmp_v1patch_"):
                continue
            out[rel] = _sha_bytes(_read_bytes(p))
    return out


def _in_mutable(rel: str) -> bool:
    return rel in MUTABLE_FILES or any(rel == s or rel.startswith(s + "/") for s in MUTABLE_SUBTREES)


# ------------------------------------------------------------------------------------------------------------------------------------------------
# 対象file群の検証と新内容の生成(読取のみ)
# ------------------------------------------------------------------------------------------------------------------------------------------------
def build_patched(run_dir: str) -> dict:
    """returns {rel: {"old_bytes","new_bytes","old_sha","new_sha","old_text","new_text"}}。定数と1つでも違えばToolRefused。"""
    out = {}
    for t in TARGETS:
        p = os.path.join(run_dir, t["rel"])
        if not os.path.exists(p):
            raise ToolRefused(f"対象fileがありません: {t['rel']}")
        raw = _read_bytes(p)
        if _sha_bytes(raw) != t["old_sha"]:
            raise ToolRefused(f"{t['rel']}: 旧file shaが定数と一致しません(実={_sha_bytes(raw)[:16]} 期待={t['old_sha'][:16]})。別状態のrunへは適用しません")
        txt = raw.decode("utf-8")
        if "\r" in txt:
            raise ToolRefused(f"{t['rel']}: CR文字を含みます(想定外の改行形式)")
        lines = txt.split("\n")
        if len(lines) != t["n_lines"]:
            raise ToolRefused(f"{t['rel']}: 行数が定数と一致しません(実={len(lines)} 期待={t['n_lines']})")
        if txt.endswith("\n") != t["ends_nl"]:
            raise ToolRefused(f"{t['rel']}: 末尾改行の有無が定数と一致しません")
        if lines[t["line_no"] - 1] != t["old"]:
            raise ToolRefused(f"{t['rel']}: {t['line_no']}行目が旧行と逐語一致しません: {lines[t['line_no'] - 1]!r}")
        hits = [i for i, ln in enumerate(lines, 1) if ln == t["old"]]
        if hits != [t["line_no"]]:
            raise ToolRefused(f"{t['rel']}: 旧行の出現位置が{hits}(期待=[{t['line_no']}]のみ)")
        new_lines = list(lines)
        new_lines[t["line_no"] - 1] = t["new"]
        new_txt = "\n".join(new_lines)
        diff_lines = [i + 1 for i, (x, y) in enumerate(zip(lines, new_lines)) if x != y]
        if diff_lines != [t["line_no"]]:
            raise ToolRefused(f"{t['rel']}: 差分行が{diff_lines}(期待=[{t['line_no']}]のみ)")
        nb = new_txt.encode("utf-8")
        out[t["rel"]] = {"old_bytes": raw, "new_bytes": nb, "old_sha": t["old_sha"], "new_sha": _sha_bytes(nb), "old_text": txt, "new_text": new_txt}
    for rel, expect in NEW_FILE_SHA.items():
        if expect is not None and out[rel]["new_sha"] != expect:
            raise ToolRefused(f"{rel}: 差替え後のfile shaが定数と一致しません(実={out[rel]['new_sha']} 期待={expect})")
    oj, nj = json.loads(out["text/lead_intro/intros_final.json"]["old_text"]), json.loads(out["text/lead_intro/intros_final.json"]["new_text"])
    if {k: v for k, v in oj.items() if k != "voice_1"} != {k: v for k, v in nj.items() if k != "voice_1"} or nj.get("voice_1") != JA_NEW or oj.get("voice_1") != JA_OLD:
        raise ToolRefused("intros_final.json: voice_1以外が変わる、または新旧文が定数と一致しません")
    return out


def check_article_invariants(patched: dict, run_dir: str) -> dict:
    """M4: split_y_articleでV1紹介行以外が不変(JA/EN全て)。supportに『father/父親』無し。Std KP3文(V3紹介行)がa2に逐語残存。"""
    import er121_family_y_structure_01 as ys
    rep = {}
    for rel in ("text/article_ja.md", "text/article_assembled.md", "translate/b1b.md", "translate/a2.md"):
        po, pn = ys.split_y_article(patched[rel]["old_text"]), ys.split_y_article(patched[rel]["new_text"])
        if po["title"] != pn["title"] or po["lead"] != pn["lead"] or po["closing"] != pn["closing"]:
            raise ToolRefused(f"{rel}: title/lead/closingが変わります")
        for i in range(3):
            if po["voices"][i]["body"] != pn["voices"][i]["body"]:
                raise ToolRefused(f"{rel}: Voice{i + 1}本文が変わります")
        if po["voices"][1]["intro"] != pn["voices"][1]["intro"] or po["voices"][2]["intro"] != pn["voices"][2]["intro"]:
            raise ToolRefused(f"{rel}: V2/V3紹介が変わります")
        if po["voices"][0]["intro"] == pn["voices"][0]["intro"]:
            raise ToolRefused(f"{rel}: V1紹介が変わっていません")
        rep[rel] = {"v1_intro_old": po["voices"][0]["intro"], "v1_intro_new": pn["voices"][0]["intro"], "others_identical": True}
    for lv in LEVELS:
        sp = os.path.join(run_dir, "support", f"{lv}_support.json")
        with open(sp, encoding="utf-8") as f:
            t = f.read()
        if re.search(r"father|父親", t, re.I):
            raise ToolRefused(f"{sp}: supportに『father/父親』が含まれます(Preview/Commentの再生成が要る=本toolの範囲外)")
    rep["support_no_father"] = True
    kp3 = "A relative took his wife’s last name."
    if kp3 not in patched["translate/a2.md"]["new_text"]:
        raise ToolRefused(f"Std KP3文({kp3!r})がa2に逐語で残っていません")
    rep["std_kp3_sentence_in_a2"] = True
    return rep


def check_new_lines(patched: dict) -> dict:
    """M7: 固定ENをtranslate段と同じ check_y_article(en) + Std決定論検査器(run_checks)で検査。JA固定行は check_intro(theme spec)。"""
    import er003_v1_n3_01_standard_a2_generate as std_gen
    import er121_family_y_structure_01 as ys
    import er121_family_y_text_core_01 as tc
    rep = {}
    for rel in ("translate/b1b.md", "translate/a2.md"):
        chk = ys.check_y_article(patched[rel]["new_text"], lang="en")
        if not chk["ok"]:
            raise ToolRefused(f"{rel}: check_y_article(en)不合格 {chk['violations']}")
        rep[rel] = {"check_y_article_en": chk}
    std_chk = std_gen.run_checks(patched["translate/b1b.md"]["new_text"], patched["translate/a2.md"]["new_text"])
    if std_chk["checks_failed"]:
        raise ToolRefused(f"Std決定論検査(run_checks)不合格: {std_chk['checks_failed']}")
    rep["std_run_checks"] = {"checks_failed": std_chk["checks_failed"], "numbers_missing": std_chk["numbers_missing"], "numbers_added": std_chk["numbers_added"],
                             "proper_nouns_added_observed_only": std_chk["proper_nouns_added_observed_only"]}
    for rel in ("text/article_ja.md", "text/article_assembled.md"):
        chk = ys.check_y_article(patched[rel]["new_text"], lang="ja")
        if not chk["ok"]:
            raise ToolRefused(f"{rel}: check_y_article(ja)不合格 {chk['violations']}")
    theme = tc.load_theme_package(THEME_PKG)["theme"]
    explicit = None
    try:
        with open(REUSE_MANIFEST, encoding="utf-8") as f:
            explicit = (json.load(f) or {}).get("intro_checks")
    except OSError:
        pass
    spec = tc.intro_spec(theme, explicit)
    parsed = ys.split_y_article(patched["text/article_ja.md"]["new_text"])
    ci = tc.check_intro(JA_NEW, "voice_1", parsed["voices"][0]["body"], spec)
    if not ci["ok"]:
        raise ToolRefused(f"check_intro(V1新紹介)不合格: {ci['violations']}")
    rep["check_intro_ja"] = {"ok": True, "len": len(JA_NEW), "spec_mode": spec["mode"]}
    with open(TRIAL_GATE_RESULT, encoding="utf-8") as f:
        gate = json.load(f)
    rec = gate.get("REC") or {}
    if rec.get("text") != JA_NEW or (rec.get("leadintro_gate") or {}).get("status") != "PASS" or not (rec.get("check_intro") or {}).get("ok"):
        raise ToolRefused("Trial補助Gate(REC)の記録が固定JA文のPASSと一致しません")
    rep["trial_aux_gate"] = {"path": TRIAL_GATE_RESULT, "status": "PASS", "model": rec["leadintro_gate"].get("model"),
                             "note": "補助Gate(luna)はTrial時にJA固定文でPASS済み(本toolでは再実行しない=API 0)"}
    return rep


# ------------------------------------------------------------------------------------------------------------------------------------------------
# runner context(API 0)
# ------------------------------------------------------------------------------------------------------------------------------------------------
def run_dir_of(rehearsal_dir: Optional[str]) -> str:
    root = rehearsal_dir if rehearsal_dir else REAL_RUN_ROOT
    return os.path.join(root, SLUG, RUN)


def build_ctx(rehearsal_dir: Optional[str]):
    import er121_family_y_runner_01 as R
    root = rehearsal_dir if rehearsal_dir else REAL_RUN_ROOT
    ctx = R.YContext(slug=SLUG, run=RUN, mode="real", run_root=root, theme_package_path=THEME_PKG, reuse_manifest_path=REUSE_MANIFEST)
    ctx.llm_client = _NoApiClient()
    ctx.budget = R.E2EBudget(0.01, spent_fn=lambda: 0.0)       # 0.01円: 新規API呼出のguardは全て予算STOP
    R.resolve_style_profile(ctx, write=False)
    return R, ctx


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


# ------------------------------------------------------------------------------------------------------------------------------------------------
# 来歴oracle(M2: runner自身の関数で再計算。旧値は旧内容から、新値は差替え後の内容から)
# ------------------------------------------------------------------------------------------------------------------------------------------------
def oracle(R, ctx, ja: str, texts: dict, kp_sigs: Optional[dict] = None) -> dict:
    """name -> {"input":sha|None,"output":sha|None}。ja=article_ja.md全文、texts={'b1b':全文,'a2':全文}(translate/*.md)。kp_sigs={lv:selection_signature}。"""
    import er119_grammar_review_01 as gr
    import er120_part2_grammar_production_01 as g
    import er120_part2_wiring_01 as p2w
    import er121_family_y_structure_01 as ys
    sh = R._sha
    base_mf = ys.y_contrast_must_fix()
    mf_a2 = base_mf + ys.y_no_iol_must_fix()
    o = {"text": {"input": None, "output": sh(ja)}}
    o["translate_b1b"] = {"input": sh(f"translate_b1b|{sh(ja)}||{sh(json.dumps(base_mf, ensure_ascii=False, sort_keys=True))}"), "output": sh(texts["b1b"])}
    o["translate_a2"] = {"input": sh(f"translate_a2|{sh(ja)}|{sh(texts['b1b'])}|{sh(json.dumps(mf_a2, ensure_ascii=False, sort_keys=True))}"), "output": sh(texts["a2"])}
    for lv in LEVELS:
        o[f"support_{lv}"] = {"input": sh(f"support_{lv}|{sh(texts[lv])}"), "output": None}
        paras, label = ys.canonical_body(texts[lv]).split("\n\n"), p2w.label_for(texts[lv])
        o[f"part2_cand_{lv}"] = {"input": g.cand_stage_input_sha(paras, label), "output": sh(p2w.cand_marker(R._part2_dir(ctx, lv), paras, label, level=lv))}
        review = gr.load_review(R._part2_dir(ctx, lv))       # 文法の確定review(selection_signatureは本文shaを含まない確定内容の署名。rebind後に変われば事後検査でSTOP)
        o[f"part2_{lv}"] = {"input": g.final_stage_input_sha(paras, label, review), "output": None}
        if kp_sigs and kp_sigs.get(lv):
            o[f"kp_{lv}"] = {"input": sh(f"{ys.canonical_body(texts[lv])}|{kp_sigs[lv]}"), "output": None}
    return o


def _entry_view(prov, name):
    e = prov.stage_entry(name)
    return None if e is None else {"input": e.get("input_sha256"), "output": e.get("output_sha256")}


def check_declared(changed) -> None:
    """M2: 『旧値一致かつ再計算後に変わるentry』の集合が宣言集合と完全一致しなければSTOP(純関数)。"""
    got = set(changed)
    if sorted(got) != sorted(DECLARED_CHANGED):
        raise ToolRefused(f"変わるentry集合が宣言集合と一致しません: 実={sorted(got)} 宣言={sorted(DECLARED_CHANGED)}")


def plan_provenance(R, ctx, patched: dict) -> dict:
    """M2: 旧oracle==記録値(runnerの式が現行entryを再現)の確認と、新oracleで『変わるentry』の集合==宣言集合の検査(kpはREBOUND後に別途確定)。"""
    prov = R._prov(ctx)
    old_ja, new_ja = patched["text/article_ja.md"]["old_text"], patched["text/article_ja.md"]["new_text"]
    old_t = {"b1b": patched["translate/b1b.md"]["old_text"], "a2": patched["translate/a2.md"]["old_text"]}
    new_t = {"b1b": patched["translate/b1b.md"]["new_text"], "a2": patched["translate/a2.md"]["new_text"]}
    old_o, new_o = oracle(R, ctx, old_ja, old_t), oracle(R, ctx, new_ja, new_t)
    rep = {"old_matches_recorded": {}, "changed": [], "unchanged": []}
    for name, ov in old_o.items():
        rec = _entry_view(prov, name)
        if rec is None:
            raise ToolRefused(f"来歴entryがありません: {name}")
        for fld in ("input", "output"):
            if ov[fld] is not None and ov[fld] != rec[fld]:
                raise ToolRefused(f"来歴{name}.{fld}: 旧内容からrunner式で再計算した値が記録値と一致しません(記録={str(rec[fld])[:16]} 再計算={ov[fld][:16]})。付替えません")
        rep["old_matches_recorded"][name] = {f: (ov[f] is not None) for f in ("input", "output")}
        if (new_o[name]["input"], new_o[name]["output"]) != (ov["input"], ov["output"]):
            rep["changed"].append(name)
        else:
            rep["unchanged"].append(name)
    check_declared(set(rep["changed"]) | {"kp_b1b", "kp_a2"})       # kpは署名変化(REBOUND後)で確定するため宣言に含める
    for n in DECLARED_STALE:
        if prov.stage_entry(n) is None:
            raise ToolRefused(f"来歴entryがありません: {n}")
        if n in prov.data["downstream_stale"]:
            raise ToolRefused(f"{n}は既にstale(別操作の途中状態の疑い)")
    rep["declared_changed"] = list(DECLARED_CHANGED)
    rep["declared_stale"] = list(DECLARED_STALE)
    return rep


# ------------------------------------------------------------------------------------------------------------------------------------------------
# KP(M3 (1) 読取のみの事前検査)
# ------------------------------------------------------------------------------------------------------------------------------------------------
def kp_precheck(R, ctx, lv: str, new_text_full: str) -> dict:
    import er119_kp_human_review_01 as rv
    import er121_family_y_structure_01 as ys
    cc = rv._cc()
    kp_dir = R._kp_src_dir(ctx, lv)
    rec = cc.live_user_record(kp_dir)
    if rec is None:
        raise ToolRefused(f"kp_{lv}: ユーザー確定レコード(live)がありません")
    cands = rv.load_candidates(kp_dir)
    review = rv.load_review(kp_dir)
    if cands is None or review is None:
        raise ToolRefused(f"kp_{lv}: 候補/reviewがありません")
    old_text_sha = (rec.get("article") or {}).get("text_sha256")
    if cands.get("text_sha256") != old_text_sha or review.get("text_sha256") != old_text_sha:
        raise ToolRefused(f"kp_{lv}: 確定レコード/候補/reviewのtext_sha256が一致しません(別状態)")
    canon = ys.canonical_body(new_text_full)
    ntext = cc._norm_ws(canon)
    cm = cc._cand_map(cands)
    verbatim = []
    for it in rec.get("items") or []:
        sent = cc._source_sentence_of(cm.get(it["candidate_id"]))
        verbatim.append({"kind": "kp/vocab", "candidate_id": it["candidate_id"], "sentence": sent, "in_new_text": bool(sent) and cc._norm_ws(sent) in ntext})
    for gid, sent in cc._grammar_sentences(kp_dir, rec):
        verbatim.append({"kind": "grammar", "candidate_id": gid, "sentence": sent, "in_new_text": cc._norm_ws(sent) in ntext})
    for nid, quote in cc._nuance_quotes(kp_dir, rec):
        verbatim.append({"kind": "nuance", "candidate_id": nid, "sentence": quote, "in_new_text": cc._norm_ws(quote) in ntext})
    bad = [v for v in verbatim if not v["in_new_text"]]
    if bad:
        raise ToolRefused(f"kp_{lv}: 確定済みの出典文/文法/ニュアンス引用が新本文に逐語で残っていません: {bad}")
    return {"level": lv, "n_checked": len(verbatim), "all_verbatim_in_new_text": True, "old_text_sha": old_text_sha, "old_signature": review.get("selection_signature"),
            "new_text_sha": rv.sha256_text(canon)}


# ------------------------------------------------------------------------------------------------------------------------------------------------
# 退避・復元(M6)
# ------------------------------------------------------------------------------------------------------------------------------------------------
def backup_run(run_dir: str, backup_dir: str) -> dict:
    os.makedirs(backup_dir, exist_ok=True)
    man = {}
    for sub in MUTABLE_SUBTREES:
        src = os.path.join(run_dir, sub)
        if os.path.isdir(src):
            shutil.copytree(src, os.path.join(backup_dir, sub))
    for f in MUTABLE_FILES:
        src = os.path.join(run_dir, f)
        if os.path.exists(src):
            os.makedirs(os.path.dirname(os.path.join(backup_dir, f)), exist_ok=True)
            shutil.copy2(src, os.path.join(backup_dir, f))
    for root, _d, files in os.walk(backup_dir):
        for n in files:
            p = os.path.join(root, n)
            man[os.path.relpath(p, backup_dir).replace("\\", "/")] = _sha_bytes(_read_bytes(p))
    with open(os.path.join(backup_dir, "BACKUP_MANIFEST.json"), "w", encoding="utf-8") as f:
        json.dump({"tool": TOOL_ID, "at": _now(), "files": man}, f, ensure_ascii=False, indent=1)
    return man


def restore_run(run_dir: str, backup_dir: str) -> None:
    """退避した領域を丸ごと復元(領域内に新規作成されたfileも消える)。"""
    for sub in MUTABLE_SUBTREES:
        dst, src = os.path.join(run_dir, sub), os.path.join(backup_dir, sub)
        if os.path.isdir(dst):
            shutil.rmtree(dst)
        if os.path.isdir(src):
            shutil.copytree(src, dst)
    for f in MUTABLE_FILES:
        dst, src = os.path.join(run_dir, f), os.path.join(backup_dir, f)
        if os.path.exists(src):
            shutil.copy2(src, dst)
        elif os.path.exists(dst):
            os.remove(dst)


# ------------------------------------------------------------------------------------------------------------------------------------------------
# 来歴の書換え(M5)
# ------------------------------------------------------------------------------------------------------------------------------------------------
def _event(entry_before: dict, fld_changes: dict, by: str) -> dict:
    rid = entry_before.get("response_id")
    return {"at": _now(), "tool_id": TOOL_ID, "reason": "v1_intro_line_user_instruction", "by": by,
            "user_ref": {"path": USER_REF, "file_sha256": USER_REF_SHA256, "section": USER_SPEC},
            "line_old": {"ja": JA_OLD, "en_b1b": EN_B1B_OLD, "en_a2": EN_A2_OLD},
            "line_old_sha256": {"ja": _sha_text(JA_OLD), "en_b1b": _sha_text(EN_B1B_OLD), "en_a2": _sha_text(EN_A2_OLD)},
            "line_new": {"ja": JA_NEW, "en_b1b": EN_NEW, "en_a2": EN_NEW_A2},
            "line_new_sha256": {"ja": _sha_text(JA_NEW), "en_b1b": _sha_text(EN_NEW), "en_a2": _sha_text(EN_NEW_A2)},
            "output_origin": OUTPUT_ORIGIN, "changes": fld_changes, "api_calls": 0,
            "note": (f"旧LLM response_id={rid} は新出力を生成していない(V1紹介行のみ人手指示の固定文へ差替え。他の行はLLM出力のまま)" if rid
                     else "V1紹介行のみ人手指示の固定文へ差替え(他の行は不変)。このstageのLLM出力は紹介行を含まない/または変更なし")}


def rewrite_provenance(R, ctx, new_o: dict, kp_info: dict, by: str) -> dict:
    """宣言集合のentryを付替え、tts_*をstaleへ。provenanceは1回の原子的書込。returns {name: change}。"""
    prov = R._prov(ctx)
    changes = {}
    for name in DECLARED_CHANGED:
        e = prov.stage_entry(name)
        if e is None:
            raise ToolRefused(f"来歴entryがありません: {name}")
        e2 = copy.deepcopy(e)
        fc = {}
        if name.startswith("kp_"):
            lv = name.split("_", 1)[1]
            k = kp_info[lv]
            want_old = R._sha(f"{k['old_canon']}|{k['old_signature']}")
            if e["input_sha256"] != want_old:
                raise ToolRefused(f"{name}: 記録の入力shaが sha(旧text|旧sig) と一致しません(期待旧値不一致)。付替えません")
            new_in = R._sha(f"{k['new_canon']}|{k['new_signature']}")
            fc["input_sha256"] = {"from": e["input_sha256"], "to": new_in}
            fc["kp_selection_signature"] = {"from": e.get("kp_selection_signature"), "to": k["new_signature"]}
            e2["input_sha256"], e2["kp_selection_signature"] = new_in, k["new_signature"]
        else:
            nv = new_o[name]
            if nv["input"] is not None and nv["input"] != e["input_sha256"]:
                fc["input_sha256"] = {"from": e["input_sha256"], "to": nv["input"]}
                e2["input_sha256"] = nv["input"]
            if nv["output"] is not None and nv["output"] != e["output_sha256"]:
                fc["output_sha256"] = {"from": e["output_sha256"], "to": nv["output"]}
                e2["output_sha256"] = nv["output"]
            if name in ("text", "translate_b1b", "translate_a2"):
                e2["output_origin"] = OUTPUT_ORIGIN
        if not fc:
            raise ToolRefused(f"{name}: 宣言集合に含まれるのに変更がありません")
        e2["rebinds"] = list(e.get("rebinds") or []) + [_event(e, fc, by)]
        prov.data["downstream_stages"][name] = e2          # set_entry()は旧entryをregenerationsへ足してしまう(再生成ではない)ため直接置換する
        changes[name] = fc
    for n in DECLARED_STALE:
        if n not in prov.data["downstream_stale"]:
            prov.data["downstream_stale"].append(n)
        prov.data["downstream_stages"][n]["stale_marked_by"] = {
            "tool_id": TOOL_ID, "at": _now(), "reason": "V1紹介行差替えに伴い音声(y_intro_1)を04Cで再生成する。来歴は付替えない(M1)"}
    prov.save()
    return changes


# ------------------------------------------------------------------------------------------------------------------------------------------------
# 本体
# ------------------------------------------------------------------------------------------------------------------------------------------------
def tts_regeneration_plan(R, ctx) -> dict:
    """読取専用(API 0): 現在の本文・KP確定・解説と、既存TTS結果(audit/tts_generation_results.json)のcanonical_textを突き合わせ、04Cで再生成が必要になるsegmentを列挙する。
    runnerの_generate_or_reuseも同じcanonical_text一致で再利用を判断するため、ここに出ないsegmentはwavを再利用する(音声は変わらない)。"""
    import er121_family_y_structure_01 as ys
    out = {}
    for lv in LEVELS:
        with open(os.path.join(ctx.out_dir, lv, "audit", "tts_generation_results.json"), encoding="utf-8") as f:
            res = json.load(f)
        segs = ys.split_y_article(R._rd(R._level_text_path(ctx, lv)))["segments"]
        need = []
        for name, text in segs.items():
            rec = (res.get("segments") or {}).get(name) or {}
            if rec.get("canonical_text") != text:
                need.append(name)
        with open(os.path.join(ctx.out_dir, lv, "key_phrases", "keywords_canonicalized.json"), encoding="utf-8") as f:
            items = sorted(json.load(f)["items"], key=lambda x: x["rank"])
        kp_expl = {}
        if lv == "b1b":
            with open(os.path.join(R._kp_src_dir(ctx, lv), "kp_explanations.json"), encoding="utf-8") as f:
                kp_expl = json.load(f)["items"]
        for it in items:
            rk = str(it["rank"])
            kres = (res.get("key_phrases") or {}).get(rk) or {}
            if ((kres.get("english") or {}).get("canonical_text")) != it["used_form"]:
                need.append(f"kp{rk}_english")
            if lv == "b1b" and ((kres.get("explanation") or {}).get("canonical_text")) != (kp_expl.get(rk) or {}).get("english_explanation"):
                need.append(f"kp{rk}_explanation")
        out[lv] = sorted(need)
    return out


def already_applied(run_dir: str) -> bool:
    n = 0
    for t in TARGETS:
        p = os.path.join(run_dir, t["rel"])
        if os.path.exists(p) and _sha_bytes(_read_bytes(p)) != t["old_sha"]:
            n += 1
    return n == len(TARGETS)


RUN_DIR_FOR_CHECK = [None]


def applied_state_ok(R, ctx) -> dict:
    prov = R._prov(ctx)
    def _has(n):
        if any(ev.get("tool_id") == TOOL_ID for ev in (prov.stage_entry(n) or {}).get("rebinds") or []):
            return True
        # part2_<lv>は再finalize(regenerate)でentryが新規作成されるため、付替え履歴は regenerations[].old に残る
        return any(r_.get("stage") == n and any(ev.get("tool_id") == TOOL_ID for ev in (r_.get("old") or {}).get("rebinds") or []) for r_ in prov.data.get("regenerations") or [])
    missing = [n for n in DECLARED_CHANGED if not _has(n)]
    wrong = [t["rel"] for t in TARGETS if NEW_FILE_SHA.get(t["rel"]) and _sha_bytes(_read_bytes(os.path.join(RUN_DIR_FOR_CHECK[0], t["rel"]))) != NEW_FILE_SHA[t["rel"]]]
    if wrong:
        raise ToolRefused(f"適用済みに見えますが、選択したvariantの新内容(定数sha)と一致しないfileがあります: {wrong}(別のvariantで適用済みの可能性。再適用しません)")
    if missing:
        raise ToolRefused(f"fileは差替え済みに見えますが来歴にrebinds履歴がありません: {missing}。途中失敗の状態の疑い=手動で確認(再適用しません)")
    return {"already_applied": True, "rebinds_in": list(DECLARED_CHANGED)}


def _strip_sha(o):
    drop = re.compile(r"(sha256|signature|_at$|^at$|revision)", re.I)
    if isinstance(o, dict):
        return {k: _strip_sha(v) for k, v in o.items() if not drop.search(k)}
    if isinstance(o, list):
        return [_strip_sha(x) for x in o]
    return o


def _json_equal_ignoring_sha(a: Optional[bytes], b: Optional[bytes]):
    if a is None and b is None:
        return True, []
    if a is None or b is None:
        return False, ["(片方が存在しない)"]
    try:
        x, y = _strip_sha(json.loads(a.decode("utf-8"))), _strip_sha(json.loads(b.decode("utf-8")))
    except ValueError:
        return a == b, ([] if a == b else ["(JSONでなく内容不一致)"])
    if x == y:
        return True, []
    diffs = []

    def walk(p, q, path=""):
        if isinstance(p, dict) and isinstance(q, dict):
            for k in sorted(set(p) | set(q)):
                walk(p.get(k), q.get(k), f"{path}/{k}")
        elif isinstance(p, list) and isinstance(q, list) and len(p) == len(q):
            for i, (u, w) in enumerate(zip(p, q)):
                walk(u, w, f"{path}[{i}]")
        elif p != q:
            diffs.append(path)
    walk(x, y)
    return False, diffs


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--rehearsal-dir", default=None, help="<root>/surname_choice/run_02 を対象にする(run_02の複製)。未指定=本体")
    ap.add_argument("--by", default=None)
    ap.add_argument("--std-variant", default="fixed2", choices=sorted(STD_VARIANTS), help="Std(a2)のV1新行。fixed2=M7固定文(2文)、split3=3文(文番号を保つ)")
    ap.add_argument("--report", default=None, help="結果JSONの書出し先(任意)")
    a = ap.parse_args(argv)
    if not a.dry_run and not a.by:
        print(f"[{TOOL_ID}][REFUSED] --by <名> が必要です", file=sys.stderr)
        return 2
    set_std_variant(a.std_variant)
    run_dir = run_dir_of(a.rehearsal_dir)
    report = {"tool": TOOL_ID, "std_variant": a.std_variant, "dry_run": a.dry_run, "run_dir": run_dir, "rehearsal": bool(a.rehearsal_dir), "at": _now()}
    lock_taken, st, backup_dir = False, None, None
    try:
        if not os.path.isdir(run_dir):
            raise ToolRefused(f"run dirがありません: {run_dir}")
        if _sha_bytes(_read_bytes(USER_REF)) != USER_REF_SHA256:
            raise ToolRefused("ユーザー原文(USER_02)のfile shaが定数と一致しません")
        with _quiet():
            R, ctx = build_ctx(a.rehearsal_dir)
        st = R._m().st
        st.check_stop_sentinel("tool:start", run_dir)
        if already_applied(run_dir):
            RUN_DIR_FOR_CHECK[0] = run_dir
            with _quiet():
                rep = applied_state_ok(R, ctx)
            report.update(rep, result="NO_OP_ALREADY_APPLIED")
            print(json.dumps(report, ensure_ascii=False, indent=1, default=str))
            return 0
        patched = build_patched(run_dir)
        report["file_patch"] = {rel: {"old_sha": v["old_sha"], "new_sha": v["new_sha"]} for rel, v in patched.items()}
        report["article_invariants"] = check_article_invariants(patched, run_dir)
        with _quiet():
            report["line_checks"] = check_new_lines(patched)
            report["provenance_plan"] = plan_provenance(R, ctx, patched)
            report["kp_precheck"] = {lv: kp_precheck(R, ctx, lv, patched[f"translate/{lv}.md"]["new_text"]) for lv in LEVELS}
        if a.dry_run:
            report["result"] = "DRY_RUN_OK(何も書いていません)"
            print(json.dumps(report, ensure_ascii=False, indent=1, default=str))
            return 0

        # ---- 適用 ----
        st.acquire_run_lock(run_dir, sys.argv)
        lock_taken = True
        import er119_kp_human_review_01 as rv
        import er120_part2_wiring_01 as p2w
        import er121_family_y_structure_01 as ys
        import er119_grammar_review_01 as gr
        cc = rv._cc()
        before_manifest = tree_manifest(run_dir)
        cost_log = os.path.join(run_dir, "cost_log.jsonl")
        cost_before = _sha_bytes(_read_bytes(cost_log)) if os.path.exists(cost_log) else None
        stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join(os.path.dirname(run_dir), f"_backup_{TOOL_ID}_{stamp}")
        backup_man = backup_run(run_dir, backup_dir)
        report["backup"] = {"dir": backup_dir.replace("\\", "/"), "n_files": len(backup_man)}
        new_ja = patched["text/article_ja.md"]["new_text"]
        old_t = {"b1b": patched["translate/b1b.md"]["old_text"], "a2": patched["translate/a2.md"]["old_text"]}
        new_t = {"b1b": patched["translate/b1b.md"]["new_text"], "a2": patched["translate/a2.md"]["new_text"]}
        # 1) 5ファイルの原子的差替え(一時ファイル+os.replace)
        for rel, v in patched.items():
            _write_atomic(os.path.join(run_dir, rel), v["new_bytes"])
        # 2) KP: REBOUND(M3 (2)(3))。確定物(退避される前の版)を保持して後で内容比較
        retired_snap, kp_info = {}, {}
        for lv in LEVELS:
            kp_dir = R._kp_src_dir(ctx, lv)
            pth = rv.paths(kp_dir)
            retired_snap[lv] = {k: (_read_bytes(pth[k]) if os.path.exists(pth[k]) else None) for k in ("kp", "vocab", "final")}
            old_canon, new_canon = ys.canonical_body(old_t[lv]), ys.canonical_body(new_t[lv])
            old_rev = rv.load_review(kp_dir)
            with _quiet():
                res = cc.stale_or_rebind(kp_dir, new_canon, rv.sha256_text(new_canon))
            if res != "REBOUND":
                raise ToolRefused(f"kp_{lv}: stale_or_rebind が REBOUND ではありません: {res!r}")
            new_rev = rv.load_review(kp_dir)
            # 文法(Part 2)の確定: 本文再バインド(er119_grammar_review_01の同じ関数。確定した選定文が新本文に逐語で存在する場合のみ。API 0)
            sd = R._part2_dir(ctx, lv)
            gstate = cc.grammar_state(sd)
            if gstate is None:
                raise ToolRefused(f"part2_{lv}: ユーザー確定済みの文法がありません(想定外)")
            gparas, glabel = ys.canonical_body(new_t[lv]).split("\n\n"), p2w.label_for(new_t[lv])
            with _quiet():
                gr._rebind_grammar_text(sd, gstate, gr.load_candidates(sd), gr.load_review(sd), gparas, glabel)
            kp_info[lv] = {"old_canon": old_canon, "new_canon": new_canon, "old_signature": old_rev.get("selection_signature"),
                           "new_signature": new_rev.get("selection_signature")}
        # 3) 新oracle(kp署名はREBOUND後に確定)と part2_cand marker の書換え(runner自身の cand_marker)
        with _quiet():
            new_o = oracle(R, ctx, new_ja, new_t, {lv: kp_info[lv]["new_signature"] for lv in LEVELS})
            for lv in LEVELS:
                paras, label = ys.canonical_body(new_t[lv]).split("\n\n"), p2w.label_for(new_t[lv])
                old_paras, old_label = ys.canonical_body(old_t[lv]).split("\n\n"), p2w.label_for(old_t[lv])
                mpath = os.path.join(R._part2_dir(ctx, lv), "part2_cand_stage.json")
                with open(mpath, encoding="utf-8") as f:
                    old_marker = f.read()
                if old_marker != p2w.cand_marker(R._part2_dir(ctx, lv), old_paras, old_label, level=lv):
                    raise ToolRefused(f"part2_cand_{lv}: 現行markerが旧本文からのcand_markerと一致しません(想定外の状態)")
                _write_atomic(mpath, p2w.cand_marker(R._part2_dir(ctx, lv), paras, label, level=lv).encode("utf-8"))
        # 4) 来歴(最後): 宣言集合の付替え + tts stale
        before_prov = json.loads(json.dumps(R._prov(ctx).data))
        report["provenance_rewrite"] = rewrite_provenance(R, ctx, new_o, kp_info, a.by)
        mid_prov = json.loads(json.dumps(R._prov(ctx).data))
        # 5) 検証: runner自身のstage_kpを(API 0で)通す → KP/文法/Part1/Part2が全てreused、確定物の再finalize(G1)
        with _quiet():
            kp_res = R.stage_kp(ctx)
        report["stage_kp"] = json.loads(json.dumps(kp_res, default=str))
        post_kp_prov = json.loads(json.dumps(R._prov(ctx).data))
        # 5b) Part 2(文法)の結果(part2_result.json)は本文sha・候補docを埋め込むため本文変更で『古い』になる(リハーサルで _assert_study_ready の FAMILY_Y_PART2_NOT_READY を実測)。
        #     runnerが案内する公式手順(--regenerate-stage part2_<lv>: 再finalizeのみ・LLM 0・再抽出なし)を level別に単一regenで順に実行する
        report["part2_refinalize"] = []
        for target in ("part2_b1b", "part2_a2"):
            ctx.regenerate_stage = target
            with _quiet():
                res_p2 = R.stage_kp(ctx)
            report["part2_refinalize"].append({"regenerate": target, "status": res_p2.get(target)})
        ctx.regenerate_stage = None
        with _quiet():
            R.stage_kp(ctx)       # 再生成指定なしで全stageがreusedになること
            ready = {"b1b": bool(R._assert_study_ready(ctx, "tool:v1_intro_patch")), "a2": bool(R._assert_std_study_ready(ctx, "tool:v1_intro_patch"))}
        report["study_ready_after"] = ready
        # 6) 事後検査
        after_prov = R._prov(ctx).data

        def _nor(d):
            return {k: v for k, v in (d or {}).items() if k != "rebinds"}

        def _changed(x, y):
            return sorted(n for n in set(x["downstream_stages"]) | set(y["downstream_stages"]) if _nor(x["downstream_stages"].get(n)) != _nor(y["downstream_stages"].get(n)))
        diff_names = _changed(mid_prov, post_kp_prov)
        report["post_kp_entry_changes_by_runner"] = diff_names
        if diff_names:
            raise ToolRefused(f"stage_kpが追加で来歴entryを変更しました(宣言外): {diff_names}")
        total = _changed(before_prov, after_prov)
        report["total_entry_changes"] = total
        if total != sorted(set(DECLARED_CHANGED) | set(DECLARED_STALE)):
            raise ToolRefused(f"変更されたentry集合が宣言集合と一致しません: 実={total}")
        new_regen = [r_ for r_ in (after_prov.get("regenerations") or [])[len(before_prov.get("regenerations") or []):]]
        report["new_regenerations"] = [r_.get("stage") for r_ in new_regen]
        if sorted(after_prov["downstream_stale"]) != sorted(DECLARED_STALE) or sorted(report["new_regenerations"]) != ["part2_a2", "part2_b1b"]:
            raise ToolRefused(f"downstream_stale / regenerations が想定と異なります: stale={after_prov['downstream_stale']} regen={report['new_regenerations']}")
        report["finals_equal_ignoring_sha"] = {}
        for lv in LEVELS:
            pth = rv.paths(R._kp_src_dir(ctx, lv))
            for k in ("kp", "vocab", "final"):
                old_b = retired_snap[lv][k]
                new_b = _read_bytes(pth[k]) if os.path.exists(pth[k]) else None
                eq, diffs = _json_equal_ignoring_sha(old_b, new_b)
                report["finals_equal_ignoring_sha"][f"{lv}.{k}"] = {"equal": eq, "diff_paths": diffs[:10], "file_changed": old_b != new_b}
                if not eq:
                    raise ToolRefused(f"kp_{lv}: REBOUND後の確定物 {k} がsha系を除いて退避版と一致しません: {diffs[:5]}")
        res_chk = {}
        for lv in LEVELS:
            rp = f"{run_dir}/key_phrases/{lv}_result.json"
            e = R._prov(ctx).stage_entry(f"kp_{lv}")
            with open(rp, encoding="utf-8") as f:
                txt = f.read()
            res_chk[lv] = {"output_sha_matches_entry": R._m().w62.file_sha(rp) == e["output_sha256"],
                           "entry_signature_is_new": e["kp_selection_signature"] == kp_info[lv]["new_signature"],
                           "result_json_embeds_old_signature": bool(kp_info[lv]["old_signature"]) and kp_info[lv]["old_signature"] in txt,
                           "result_json_embeds_new_signature": bool(kp_info[lv]["new_signature"]) and kp_info[lv]["new_signature"] in txt}
            if not (res_chk[lv]["output_sha_matches_entry"] and res_chk[lv]["entry_signature_is_new"]):
                raise ToolRefused(f"kp_{lv}_result.json の整合検査に失敗: {res_chk[lv]}")
        report["kp_result_json_check"] = res_chk
        report["tts_stale"] = {n: (n in after_prov["downstream_stale"]) for n in DECLARED_STALE}
        with _quiet():
            hl = R._resolve_highlights_or_stop(ctx, "tool:v1_intro_patch", R.LEVELS)
        report["highlight_resolution"] = {"returned": type(hl).__name__, "levels": sorted(hl) if isinstance(hl, dict) else None}
        with _quiet():
            report["tts_regeneration_plan"] = tts_regeneration_plan(R, ctx)
        if report["tts_regeneration_plan"] != {"b1b": ["y_intro_1"], "a2": ["y_intro_1"]}:
            raise ToolRefused(f"04Cで再生成が必要なsegmentが想定({{b1b:[y_intro_1], a2:[y_intro_1]}})と異なります: {report['tts_regeneration_plan']}")
        after_manifest = tree_manifest(run_dir)
        changed = sorted(r for r in set(before_manifest) | set(after_manifest) if before_manifest.get(r) != after_manifest.get(r))
        outside = [r for r in changed if not _in_mutable(r)]
        report["changed_files"] = {"n": len(changed), "list": changed, "outside_mutable_area": outside}
        if outside:
            raise ToolRefused(f"想定外の領域のfileが変わりました: {outside[:10]}")
        cost_after = _sha_bytes(_read_bytes(cost_log)) if os.path.exists(cost_log) else None
        report["api_calls_check"] = {"cost_log_unchanged": cost_before == cost_after, "budget_guard_log": getattr(ctx.budget, "log", [])}
        if cost_before != cost_after:
            raise ToolRefused("cost_logが変わりました(API呼出の疑い)")
        for rel, v in patched.items():
            if _sha_bytes(_read_bytes(os.path.join(run_dir, rel))) != v["new_sha"]:
                raise ToolRefused(f"{rel}: 書込後のshaが想定と違います")
        report["result"] = "APPLIED"
        if a.report:
            with open(a.report, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=1, default=str)
        print(json.dumps(report, ensure_ascii=False, indent=1, default=str))
        return 0
    except BaseException as e:   # noqa: BLE001  失敗=全復元
        restored = False
        if backup_dir and os.path.isdir(backup_dir):
            try:
                restore_run(run_dir, backup_dir)
                restored = True
            except Exception as e2:   # noqa: BLE001
                print(f"[{TOOL_ID}][RESTORE_FAILED] {e2.__class__.__name__}: {e2}", file=sys.stderr)
        kind = "REFUSED" if isinstance(e, ToolRefused) else "FAILED"
        print(f"[{TOOL_ID}][{kind}] {e.__class__.__name__}: {e}  (restored={restored})", file=sys.stderr)
        if isinstance(e, (KeyboardInterrupt, SystemExit)):
            raise
        return 2
    finally:
        if lock_taken and st is not None:
            st.release_run_lock(run_dir)


if __name__ == "__main__":
    sys.exit(main())
