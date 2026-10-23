"""er109(同音救済, X/Z run-scope内のみ有効)が時刻/桁連結の対にどう反応するかの観測(API 0)。--modules でproto切替。"""
import sys, os, argparse
ap = argparse.ArgumentParser(); ap.add_argument("--modules"); a = ap.parse_args()
R = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, R)
if a.modules: sys.path.insert(0, os.path.abspath(a.modules))
os.chdir(R)
import er109_xz_scope_01 as xz
import judge_sim_01 as js
PAIRS = [("At ten thirty", "At 10:30"), ("At ten thirty", "At 1030"), ("At 10 thirty", "At ten thirty"), ("At 10 thirty", "At 10:30"), ("At ten thirty", "At 10:13"),
         ("At 1030", "At 10:30"), ("At three", "At 3:00"), ("At 10 thirty pm", "At 10:30 pm"), ("In twenty twenty", "In 2020")]
with xz.run_scope("Z"):
    for c, t in PAIRS:
        d = xz.decision(c, t)
        st = js.judge_primary(c, t)
        print(f"er109={'RESCUE' if d is not None else 'none  '} judge={st[0]}/{st[1]} | {c!r} || {t!r}")
