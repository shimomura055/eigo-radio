"""全回帰ラッパ(OPEN-487): --base を付けると er006/er021 を修正前(base_HEAD05)に差し替えて run_project_regression を同条件で実行。py regress_wrap_05.py [--base] --json out.json"""
import sys, os, runpy, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, R); os.chdir(R)
args = sys.argv[1:]
if "--base" in args:
    args.remove("--base")
    for n in ("er006_preprod_hardening_01_validation", "er021_en_asr_semantic_equivalence_production_01"):
        spec = importlib.util.spec_from_file_location(n, os.path.join(HERE, "base_HEAD05", n + ".py")); m = importlib.util.module_from_spec(spec)
        sys.modules[n] = m; spec.loader.exec_module(m)
sys.argv = ["run_project_regression.py"] + args
runpy.run_path(os.path.join(R, "run_project_regression.py"), run_name="__main__")
