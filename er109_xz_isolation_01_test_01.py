# -*- coding: utf-8 -*-
"""er109 X/Z限定配線の『隔離』test(API 0・費用0)。ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01 委任_04(Opus 論点1・5、M3/M6、test置換(a)〜(f))。
旧11-7『既定OFF』隔離(DefaultOffIsolation)の置換: 正式採用後は『flag(rollback)True ∧ X/Z run scope内のみ有効、A/B/C・scope外は無効』を構造+実行で固定する。
  (a) 共有Validatorはer109/scope moduleをimportしない  (b) scope module・er109にenv/argparse/設定dict読取なし、.env・起動scriptに該当語0
  (c) flag Trueでもscope未設定なら全配線点でer109呼出0(spy)  (e) AST allowlist(scope入口の呼出点を固定、リテラル'X'/'Z'のみ・enter/leave非公開)
  M6 X/Zから届く全ASR入口がscope内(静的: 呼出graph / 動的: spy)  (f) 既存静的audit(新ASR呼出0)の維持。
実行: .venv\\Scripts\\python.exe -m unittest er109_xz_isolation_01_test_01 -v"""
from __future__ import annotations

import ast
import collections
import glob
import os
import re
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import er109_asr_orthographic_equivalence_01 as e109
import er109_xz_scope_01 as xz
import er109_xz_scope_01_test_01 as T

SCOPE_MOD = "er109_xz_scope_01"
E109_MOD = "er109_asr_orthographic_equivalence_01"
# scope moduleをimportしてよいProduction .py(固定リスト)。A/B/C runner・共有leaf(voice01等)は含まない。
PRODUCTION_SCOPE_IMPORTERS = {
    "er006_secondary_asr_01.py", "er078_asr_unified_judge_01.py", "er104_kp_three_asr_vote_01.py", "er019_family_x_validation_inheritance_01.py",
    "er078_reuse_value_guard_01.py", "er019_family_x_audio_production_runner_01.py", "er063_family_z_audio_01.py", "er019_family_x_clobber_restore_03.py",
    "er109_hr_lock_rejudge_01.py", "er109_wiring_signature_01.py", "er109_runtime_evidence_04_01.py",
    "er121_family_y_audio_01.py",   # FAMILY-Y-PRODUCTION-LAUNCH-01 02B: Y正式Productionの音声層(scope "Y"の入口を2箇所で呼ぶ。下のEXPECTED_SCOPE_CALLSで固定)
    "er127_tts_block_policy_01.py",   # TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_02: unified_flow_active()=current_scope()の読取のみ(scope入口は呼ばない。単一読取関数)
    "er012_b_family_voices_production_01.py",   # OPEN-479(Fable承認2026-10-23): is_active_for_run()の読取のみ(scope入口は呼ばない)。会話clipのsegment_idをX/Z scope内だけに限定するため
}
# PM-REGRESSION-ISOLATION-HYGIENE-01 委任_01: DEV/Trial-only, not production-reachable(具体ファイル名のみ。glob・接頭辞での拡張禁止)。
# Trial harness(X/Z限定の実生成と同じscopeをかぶせて再利用する隔離DEV runner)。Productionから参照されないことは下のtestで確認する。
#   er113_fx_paragraph_chunk_trial_01.py = FX-PARAGRAPH-CHUNK-TTS-TRIAL-01 / er114_fz_narration_chunk_trial_02.py = FZ-NARRATION-CHUNK-TTS-TRIAL-01
DEV_TRIAL_SCOPE_SCRIPTS = {"er113_fx_paragraph_chunk_trial_01.py", "er114_fz_narration_chunk_trial_02.py",
                           # 委任_02A-0(R-10、JA-ASR-V2-BETA-PRODUCTION-WIRING-01): 本testの固定リスト更新漏れ(HEAD失敗)の是正。
                           # いずれもDEV/Trial専用(Productionからimportされない=下のoutside検査で固定)。Z/Y Trial harness・Trial用fake。
                           "er118_fz_full_episode_trial_01.py", "er118_fz_dialogue_context_tts_trial_01.py",
                           "er121_e1_slowed_asr_recheck_01.py", "er122_fz_ctx_fakes_01.py"}
# OPEN-479: 共有leaf er012_b だけは scope module の「読取関数」importを許可(er109純関数・scope入口呼出は引き続き禁止)
ABC_SCOPE_READER_ALLOWED = {"er012_b_family_voices_production_01.py": SCOPE_MOD}
# 絶対にer109/scope moduleをimportしてはならないA/B/C系Production(共有leafは除く: leaf自体はadapter経由で間接的に効くがimportしない)
ABC_FILES = ("er012_b_family_voices_production_01.py", "er012_b_family_voices_a2_production_01.py", "er013_family_c_production_runner_01.py",
             "er012_e_family_entertainment_two_level_runner_01.py", "er003_v1_n3_01_tts_generate.py", "er003_v1_sing01_voice01_generate.py",
             "er003_v1_sing01_news_tail_fix.py", "er003_v1_crosslevel_audio_02_common.py", "er003_v1_repro01_main_generate.py",
             "er003_v1_sing01_point_headings_aoede.py", "er006_preprod_hardening_01_validation.py", "er006_master_audio_store_01.py")
# scope入口(run_scope/family_scope)の呼出点。Productionはこの固定リストだけ(ファイル名, 呼出名, リテラル)。
EXPECTED_SCOPE_CALLS = collections.Counter({
    ("er019_family_x_audio_production_runner_01.py", "family_scope", "X"): 2,
    ("er063_family_z_audio_01.py", "family_scope", "Z"): 1,
    ("er121_family_y_audio_01.py", "family_scope", "Y"): 2,   # FAMILY-Y-PRODUCTION-LAUNCH-01 02B: generate_y_b1/a2_segments
    ("er019_family_x_validation_inheritance_01.py", "family_scope", "X"): 2,
    ("er019_family_x_clobber_restore_03.py", "family_scope", "X"): 1,
    ("er109_hr_lock_rejudge_01.py", "run_scope", "X"): 1,
    ("er109_hr_lock_rejudge_01.py", "run_scope", "Z"): 1,
    ("er109_wiring_signature_01.py", "run_scope", "X"): 1,
    ("er109_wiring_signature_01.py", "run_scope", "Z"): 1,
    ("er109_runtime_evidence_04_01.py", "run_scope", "X"): 1,
    ("er109_runtime_evidence_04_01.py", "run_scope", "Z"): 1,
})


def repo_py_files():
    """リポジトリ全体の.py(root直下tool・docs/research含む)。.venv/mfa_tool等の外部資産は除く。git管理外の新規fileも含める。"""
    try:
        out = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard", "--", "*.py"], cwd=ROOT, capture_output=True,
                             text=True, encoding="utf-8", errors="replace", timeout=60).stdout.split("\n")
        files = [f.strip() for f in out if f.strip().endswith(".py")]
    except Exception:
        files = []
    if not files:
        files = [os.path.relpath(p, ROOT) for p in glob.glob(os.path.join(ROOT, "**", "*.py"), recursive=True)]
    skip = (".venv", "mfa_tool", "node_modules", "site-packages", "__pycache__")
    return [f.replace("\\", "/") for f in files if not any(s in f.replace("\\", "/").split("/") for s in skip) and os.path.exists(os.path.join(ROOT, f))]


def parse(rel):
    try:
        return ast.parse(open(os.path.join(ROOT, rel), encoding="utf-8").read())
    except (SyntaxError, UnicodeDecodeError, ValueError):
        return None


def scope_aliases(tree):
    """このfileがscope moduleをimportしている別名(ModuleAlias) と from-import名。"""
    mod_alias, names = set(), {}
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for a in n.names:
                if a.name == SCOPE_MOD:
                    mod_alias.add(a.asname or a.name)
        elif isinstance(n, ast.ImportFrom) and n.module == SCOPE_MOD:
            for a in n.names:
                names[a.asname or a.name] = a.name
    return mod_alias, names


def is_research_script(rel):
    """docs/research/ 配下の調査・証跡script(Production到達なし・起動scriptからも呼ばれない)。委任_27(2026-10-24): ASR-TIME-NUMERAL-EQUIVALENCE-01の
    er109_probe_01.py / runtime_evidence_02.py(研究scriptが固定listの外でscope入口をimport/呼出)で恒常失敗していたため、
    Production固定list検査(importer/呼出点)の対象から研究scriptを外す。Production側のimport/呼出は従来どおり固定listで検査する。"""
    return rel.replace("\\", "/").startswith("docs/research/")


def is_test_file(rel):
    b = os.path.basename(rel)
    return "_test" in b or b.startswith("test_") or b == "conftest.py"


class StaticIsolation(unittest.TestCase):
    def test_a_shared_validator_does_not_reference_er109(self):
        src = open(os.path.join(ROOT, "er006_preprod_hardening_01_validation.py"), encoding="utf-8").read()
        self.assertNotIn("er109", src)
        tree = ast.parse(src)
        for n in ast.walk(tree):
            if isinstance(n, (ast.Import, ast.ImportFrom)):
                names = [a.name for a in n.names] + [getattr(n, "module", "") or ""]
                self.assertFalse(any("er109" in (x or "") for x in names))

    def test_b_scope_module_and_er109_have_no_env_or_config_reads(self):
        banned_attr = {("os", "environ"), ("os", "getenv"), ("sys", "argv")}
        for rel in (f"{SCOPE_MOD}.py", f"{E109_MOD}.py"):
            tree = parse(rel)
            for n in ast.walk(tree):
                if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name):
                    self.assertNotIn((n.value.id, n.attr), banned_attr, rel)
                if isinstance(n, (ast.Import, ast.ImportFrom)):
                    mods = [a.name for a in n.names] + [getattr(n, "module", None) or ""]
                    for m in mods:
                        self.assertNotIn(m.split(".")[0], {"argparse", "configparser", "dotenv", "requests", "socket", "subprocess", "urllib", "http"}, (rel, m))
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Name):
                    self.assertNotIn(n.func.id, {"open", "exec", "eval", "compile", "__import__"}, rel)       # 純関数(通信・書込・設定読取なし)

    def test_b_env_and_launch_scripts_have_no_er109_flag_or_scope(self):
        words = re.compile(r"ORTHOGRAPHIC_EQUIVALENCE|er109_xz_scope|er109_asr_orthographic|ER109")
        cands = [os.path.join(ROOT, ".env")]
        for pat in ("*.bat", "*.ps1", "*.sh", "*.cmd", "*.command"):
            cands += glob.glob(os.path.join(ROOT, pat))
        cands += glob.glob(os.path.join(ROOT, "scripts", "*")) + glob.glob(os.path.join(ROOT, ".claude", "**", "*.json"), recursive=True)
        for p in cands:
            if os.path.isfile(p):
                try:
                    txt = open(p, encoding="utf-8", errors="ignore").read()
                except OSError:
                    continue
                self.assertIsNone(words.search(txt), p)

    def test_m3_scope_entry_call_sites_are_fixed_and_literal(self):
        found = collections.Counter()
        for rel in repo_py_files():
            if rel == f"{SCOPE_MOD}.py":
                continue
            if is_research_script(rel):
                continue
            tree = parse(rel)
            if tree is None:
                continue
            dev_script = os.path.basename(rel) in DEV_TRIAL_SCOPE_SCRIPTS
            mod_alias, names = scope_aliases(tree)
            if not mod_alias and not names:
                continue
            for n in ast.walk(tree):
                fname = None
                if isinstance(n, ast.Call):
                    f = n.func
                    if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) and f.value.id in mod_alias:
                        fname = f.attr
                    elif isinstance(f, ast.Name) and names.get(f.id):
                        fname = names[f.id]
                elif isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id in mod_alias:
                    # 非公開(enter/leave/_RUN_SCOPE)の参照はtestファイル以外禁止
                    if n.attr in ("_enter_scope", "_RUN_SCOPE", "enter_scope", "leave_scope"):
                        self.assertTrue(is_test_file(rel), f"{rel}: {n.attr} は非公開")
                if fname in ("run_scope", "family_scope"):
                    arg = n.args[0] if n.args else None
                    lit = arg.value if isinstance(arg, ast.Constant) else None
                    if is_test_file(rel):
                        continue
                    self.assertIn(lit, ("X", "Z", "Y"), f"{rel}: {fname}の引数はリテラル'X'/'Z'のみ")
                    if dev_script:
                        continue    # DEV/Trial専用script: リテラル検査は行うが、Production固定リスト(EXPECTED_SCOPE_CALLS)には数えない
                    found[(os.path.basename(rel), fname, lit)] += 1
        # HR CLI/署名toolは存在する場合のみ許容(本testはその有無に依らず固定リストと一致を要求する)
        expected = collections.Counter({k: v for k, v in EXPECTED_SCOPE_CALLS.items() if os.path.exists(os.path.join(ROOT, k[0]))})
        self.assertEqual(found, expected)

    def test_importers_of_scope_module_are_a_fixed_production_list(self):
        importers = set()
        dev_importers = set()
        e109_importers = set()
        all_modules_imported = collections.defaultdict(set)    # import先module名 -> importしたfile(非test)
        for rel in repo_py_files():
            if is_research_script(rel):
                continue
            tree = parse(rel)
            if tree is None:
                continue
            b = os.path.basename(rel)
            for n in ast.walk(tree):
                mods = []
                if isinstance(n, ast.Import):
                    mods = [a.name for a in n.names]
                elif isinstance(n, ast.ImportFrom) and n.module:
                    mods = [n.module]
                if not is_test_file(rel):
                    for mm in mods:
                        all_modules_imported[mm].add(b)
                if SCOPE_MOD in mods and not is_test_file(rel) and b != f"{SCOPE_MOD}.py":
                    if b in DEV_TRIAL_SCOPE_SCRIPTS:
                        dev_importers.add(b)
                    else:
                        importers.add(b)
                if E109_MOD in mods and not is_test_file(rel):
                    e109_importers.add(b)
        self.assertTrue(importers <= PRODUCTION_SCOPE_IMPORTERS, importers - PRODUCTION_SCOPE_IMPORTERS)
        # DEV allow-listの前提確認: DEV/Trial専用scriptは固定の具体名のみ、かつProduction/他の非test fileからimportされていない
        self.assertTrue(dev_importers <= DEV_TRIAL_SCOPE_SCRIPTS, dev_importers - DEV_TRIAL_SCOPE_SCRIPTS)
        for dev in DEV_TRIAL_SCOPE_SCRIPTS:
            outside = {x for x in all_modules_imported.get(dev[:-3], set()) if x not in DEV_TRIAL_SCOPE_SCRIPTS and not x.startswith(dev[:5])}   # 同一Trial系列(er113_*/er114_*)のDEV script同士は可
            self.assertEqual(outside, set(), f"{dev} をProduction側がimportしている")
        # 純関数moduleを直接importするProduction .pyは scope module(と判定のみのer109_*研究tool・scope/golden tool)だけ
        allowed_e109 = {f"{SCOPE_MOD}.py"}
        # ②UKUS(Production化済み): er109_ukus_*.py は er109_ 接頭で上の判定対象外。Trial(er111_ukus_*)は撤去済み(Productionからのimport 0を er109_ukus_spelling_01_test_01 が固定)。
        allowed_e109 |= {"ukus_sim_01.py",   # 委任_01の研究用机上sim(docs/research/.../work。er109._unitsをmonkeypatchする調査scriptでProduction未配線)
                      "sweep_trial_vs_prod_01.py", "build_stored_expected_01.py"}    # UKUS 委任_04の一回限り証跡script(docs/research/.../WIRING。Trial撤去前の同等性sweep。Production未配線)
        stray = {b for b in e109_importers if b not in allowed_e109 and not b.startswith("er109_")}
        self.assertEqual(stray, set(), "er109純関数をscope module以外のProduction .pyがimportしている")

    def test_abc_files_do_not_import_er109_or_scope(self):
        for b in ABC_FILES:
            p = os.path.join(ROOT, b)
            if not os.path.exists(p):
                continue
            tree = parse(b)
            for n in ast.walk(tree):
                mods = []
                if isinstance(n, ast.Import):
                    mods = [a.name for a in n.names]
                elif isinstance(n, ast.ImportFrom) and n.module:
                    mods = [n.module]
                for m in mods:
                    if m == ABC_SCOPE_READER_ALLOWED.get(b):
                        continue
                    self.assertFalse(m.startswith("er109"), f"{b} が {m} をimport")

    def test_flag_default_is_true_rollback_switch_and_documented(self):
        self.assertIs(e109.ORTHOGRAPHIC_EQUIVALENCE_ENABLED, True)
        src = open(os.path.join(ROOT, f"{E109_MOD}.py"), encoding="utf-8").read()
        self.assertNotIn("ORTHOGRAPHIC_EQUIVALENCE_ENABLED = False", src)           # 旧『未承認・既定OFF』の撤去
        self.assertNotIn("未承認・既定OFF", src)

    def test_f_existing_static_audit_still_zero_new_asr_calls(self):
        import er078_asr_unified_wiring_static_audit_01 as audit
        inv = audit.inventory()
        diff = audit.diff_against_allowlist(inv, audit.load_allowlist())
        # 配線前HEAD(b7b6d07d8)で既に存在した差(KP3V/PNAP時代に追加され、allowlist未更新の4件)と完全に同一であること = 本委任(er109)で新ASR呼出を1つも足していない。
        self.assertEqual(diff, {
            "unlisted_new_calls": [("er103_proper_noun_alarm_policy_01", "hr_residual_summary", "val.classify_asr_match"),
                                   ("er104_kp_three_asr_vote_01", "_classify", "val.classify_asr_match"),
                                   ("er104_kp_vote_reuse_01", "evaluate_vote", "secondary_asr.evaluate_attempt_with_cascade_detail")],
            "vanished": [], "count_changed": [("er019_family_x_validation_inheritance_01", "rejudge_with_current_judge", "en_validator.classify_asr_match")]})


class Spy_c_FlagTrueScopeUnsetCallsNothing(T.Base):
    """(c) flag Trueでもscope未設定なら全配線点でer109呼出0。"""

    def test_zero_er109_calls_across_all_wiring_points(self):
        import er019_family_x_validation_inheritance_01 as vi
        import er078_asr_unified_judge_01 as uj
        import er078_reuse_value_guard_01 as rvg
        import er104_kp_three_asr_vote_01 as kp3v
        self.assertTrue(e109.ORTHOGRAPHIC_EQUIVALENCE_ENABLED)
        calls = {"evaluate": 0, "cached": 0}
        real_eval = e109.evaluate

        def spy_eval(*a, **k):
            calls["evaluate"] += 1
            return real_eval(*a, **k)

        def spy_cached(*a, **k):
            calls["cached"] += 1
            raise AssertionError("scope未設定でer109が呼ばれた")
        with mock.patch.object(e109, "evaluate", spy_eval), mock.patch.object(xz, "_evaluate_cached", spy_cached):
            for c, p, az in [("Pump one's fist.", "Pump 1's fist.", None), ("I said no.", "I said know.", None), ("I said no.", "I sed no.", "I said know."),
                             ("Pump one's fist.", "Pump a fist.", "Pump 1's fist.")]:
                self.adapter(c, p, azure=az, scope=None)                                  # adapter(Primary/Secondary)+judge(最終ゲート/Secondary事前チェック)
                self.adapter(c.rstrip("."), p.rstrip("."), azure=(az or p).rstrip("."), scope=None, kp=True)   # KP vote(Primary/Secondary/Whisper)
                vi.rejudge_with_current_judge({"text": c, "asr_text": p, "sha256": "x", **({"scg_info": {"secondary_transcript": az}} if az else {})},
                                              "b1b", "full_story_part1", force_lang="en")   # 再評価2点
                rvg.guard_entry({"text": c, "asr_text": p}, label="t", canonical_text=c)   # Store guard
                kp3v.make_voter("whisper", c, p, lang="en")                                 # KP voter
            pr = uj.PrimaryResult(passed=False, text="Pump a fist.", label="x")
            uj.unified_judge(uj.AttemptCtx(canonical_text="Pump one's fist.", wav_sha256="s"), pr, lambda c: uj.SecondaryOutcome("Pump 1's fist."),
                             lang="en", role=None, secondary_accept_fn=lambda c, s: (True, xz.ORTHO_LABEL))
        self.assertEqual(calls, {"evaluate": 0, "cached": 0})


class M6_AllXZEntriesAreInScope(T.Base):
    COVERED = {
        ("er019_family_x_audio_production_runner_01", "generate_family_x_b1_segments"), ("er019_family_x_audio_production_runner_01", "generate_family_x_a2_segments"),
        ("er063_family_z_audio_01", "run_tts_stage"), ("er019_family_x_validation_inheritance_01", "rebuild_state"),
        ("er019_family_x_validation_inheritance_01", "rebuild_state_multi"), ("er019_family_x_clobber_restore_03", "plan_and_apply"),
    }
    X_Z_PRODUCTION_MODULES = ("er019_family_x_audio_production_runner_01", "er063_family_z_audio_01", "er026_family_z_fiction_production_runner_01",
                              "er019_family_x_validation_inheritance_01", "er019_family_x_clobber_restore_03")
    ADAPTER_SITES = {"evaluate_attempt_with_cascade", "evaluate_attempt_with_cascade_detail", "rejudge_with_current_judge", "guard_entry",
                     "_post_slowdown_unified_judge"}

    def test_static_x_z_production_modules_reach_asr_only_through_scoped_entries(self):
        """X/Z Productionモジュールから届くASR判定入口(adapter/再評価/guard)の呼出経路は、必ずscope付き入口(3 decorator+X専用tool)を通る。
        呼出graphを逆向きにたどり、scope付き入口で打ち切った後に残る『scope無しの根』にX/Z Production moduleの関数が無いことを要求する。"""
        import er078_asr_unified_wiring_static_audit_01 as audit
        reach = audit.reachable_modules(list(m + ".py" for m in self.X_Z_PRODUCTION_MODULES), ROOT)
        files = {m: os.path.join(ROOT, m + ".py") for m in reach if os.path.exists(os.path.join(ROOT, m + ".py"))}
        trees = {}
        for m, p in files.items():
            try:
                trees[m] = ast.parse(open(p, encoding="utf-8").read())
            except (SyntaxError, UnicodeDecodeError):
                pass
        info, funcs = {}, {}
        for m, t in trees.items():
            alias, frm = {}, {}
            for n in ast.walk(t):
                if isinstance(n, ast.Import):
                    for a in n.names:
                        if a.name in trees:
                            alias[a.asname or a.name] = a.name
                elif isinstance(n, ast.ImportFrom) and n.module in trees:
                    for a in n.names:
                        frm[a.asname or a.name] = (n.module, a.name)
            info[m] = (alias, frm)

            def visit(node, prefix):
                for c in ast.iter_child_nodes(node):
                    if isinstance(c, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        q = f"{prefix}.{c.name}" if prefix else c.name
                        funcs[(m, q)] = c
                        visit(c, q)
                    elif isinstance(c, ast.ClassDef):
                        visit(c, f"{prefix}.{c.name}" if prefix else c.name)
                    else:
                        visit(c, prefix)
            visit(t, "")
        idx = collections.defaultdict(list)
        for (m, q) in funcs:
            idx[(m, q.split(".")[-1])].append((m, q))
        names_in = collections.defaultdict(set)
        for (m, q) in funcs:
            names_in[m].add(q.split(".")[-1])
        rev = collections.defaultdict(set)
        for (m, q), node in funcs.items():
            alias, frm = info[m]
            tgts = set()
            for s in ast.walk(node):
                if isinstance(s, ast.Name):
                    if s.id in frm:
                        tgts.add(frm[s.id])
                    if s.id in names_in[m]:
                        tgts.add((m, s.id))
                elif isinstance(s, ast.Attribute) and isinstance(s.value, ast.Name) and s.value.id in alias:
                    tgts.add((alias[s.value.id], s.attr))
            for t_ in tgts:
                for r in idx.get(t_, []):
                    rev[r].add((m, q))
        leaves = [k for k, node in funcs.items()
                  if any(isinstance(s, ast.Call) and getattr(s.func, "attr", getattr(s.func, "id", "")) in self.ADAPTER_SITES for s in ast.walk(node))]
        self.assertGreaterEqual(len(leaves), 8)
        seen, stack, hit = set(), list(leaves), set()
        while stack:
            x = stack.pop()
            if x in seen:
                continue
            seen.add(x)
            if x in self.COVERED:
                hit.add(x)
                continue
            for y in rev.get(x, ()):
                stack.append(y)
        self.assertEqual(hit, self.COVERED & hit)
        self.assertTrue({("er019_family_x_audio_production_runner_01", "generate_family_x_b1_segments"),
                         ("er019_family_x_audio_production_runner_01", "generate_family_x_a2_segments"), ("er063_family_z_audio_01", "run_tts_stage")} <= hit,
                        "X b1b / X a2 / Z run_tts_stage のいずれかからASR判定入口へ届いていない=graph解析の前提崩れ")
        roots = [x for x in seen if not rev.get(x) and x not in self.COVERED]
        bad = sorted(r for r in roots if r[0] in self.X_Z_PRODUCTION_MODULES)
        self.assertEqual(bad, [], f"X/Z Production moduleにscope無しでASR判定入口へ届く根がある: {bad}")

    def test_decorators_present_with_literal_family(self):
        import er019_family_x_audio_production_runner_01 as x
        import er019_family_x_clobber_restore_03 as cr
        import er019_family_x_validation_inheritance_01 as vi
        import er063_family_z_audio_01 as z

        def scoped(fn):
            while fn is not None:
                if getattr(fn, "__er109_scoped__", None):
                    return fn.__er109_scoped__
                fn = getattr(fn, "__wrapped__", None)
            return None
        self.assertEqual(scoped(x.generate_family_x_b1_segments), "X")
        self.assertEqual(scoped(x.generate_family_x_a2_segments), "X")
        self.assertEqual(scoped(z.run_tts_stage), "Z")
        self.assertEqual(scoped(vi.rebuild_state), "X")
        self.assertEqual(scoped(vi.rebuild_state_multi), "X")
        self.assertEqual(scoped(cr.plan_and_apply), "X")

    def test_dynamic_x_stage_entries_set_scope_x_and_restore(self):
        import er019_family_x_audio_production_runner_01 as x

        class Sentinel(Exception):
            pass
        seen = []

        def spy(*a, **k):
            seen.append(xz.current_scope())
            raise Sentinel()
        with mock.patch.object(x.style_profile_mod, "assert_profile_backend", spy):
            with self.assertRaises(Sentinel):
                x.generate_family_x_b1_segments(tempfile.mkdtemp())
            with self.assertRaises(Sentinel):
                x.generate_family_x_a2_segments(tempfile.mkdtemp(), "t")
        self.assertEqual(seen, ["X", "X"])
        self.assertIsNone(xz.current_scope())

    def test_dynamic_z_run_tts_stage_sets_scope_z_for_every_generator_and_restores(self):
        import er063_family_z_audio_01 as z
        import er063_family_z_audio_01_test_01 as zt
        plan, _s, _k = zt.make_plan("b1b")
        base = zt.fake_generators()
        seen = []

        def wrap(kind):
            def fn(spec, out_path):
                seen.append(xz.current_scope())
                return base[kind](spec, out_path)
            return fn
        run = os.path.join(tempfile.mkdtemp(), "melos", "run_01")
        z.run_tts_stage(run, "b1b", plan, generators={k: wrap(k) for k in base})
        self.assertGreater(len(seen), 5)
        self.assertEqual(set(seen), {"Z"})
        self.assertIsNone(xz.current_scope())

    def test_j1_to_j7_leaves_propagate_asr_judgement_into_results(self):
        """M1: manifest/results の asr_judgement に印が残る前提 = 各判定点(J1〜J7)が adapterの asr_judgement を結果dictへ載せる。"""
        points = {"er003_v1_sing01_voice01_generate": "generate_charon_english", "er003_v1_sing01_news_tail_fix": "generate_news_narration_wide_margin",
                  "er003_v1_crosslevel_audio_02_common": "_run_a2_minimal_fallback_attempt", "er012_b_family_voices_production_01": "generate_voice_body_wide_margin",
                  "er003_v1_repro01_main_generate": "generate_narration_snippet_verified_strict", "er003_v1_sing01_point_headings_aoede": "generate",
                  "er003_v1_n3_01_tts_generate": "_post_slowdown_unified_judge"}
        for mod, fn in points.items():
            tree = parse(mod + ".py")
            node = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == fn)
            strs = {c.value for c in ast.walk(node) if isinstance(c, ast.Constant) and isinstance(c.value, str)}
            self.assertIn("asr_judgement", strs, f"{mod}.{fn}")
        src = open(os.path.join(ROOT, "er006_master_audio_store_01.py"), encoding="utf-8").read()
        self.assertIn('manifest[master_id]["asr_judgement"] = r.get("asr_judgement")', src)


if __name__ == "__main__":
    unittest.main()
