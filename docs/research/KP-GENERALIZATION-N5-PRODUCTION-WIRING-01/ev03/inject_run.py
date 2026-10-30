"""技術失敗injection(1回のrunでのみ使う試験用harness)。N5 L3のGEN5(`gen5`)呼出を、**1つのcallの全attempt分(call_llmのMAX_ATTEMPTS=2)だけ**失敗させ、
N5TechnicalFailure -> 外側retry(er119_kp_candidates_01 outer attempt)で回復し、N5なし候補が出ないことを実runで観測する。
usage: <python> inject_run.py <runner.py> <runner args...>   (runnerをrunpyで実行。injectionログ=<cwd>/inject_log.jsonl)。再試行ラッパではない(1回だけ起動)。
失敗は`_send`の送信前に例外を投げる(API呼出・課金なし)。それ以外の呼出は無改変。"""
import sys, os, json, time, runpy
sys.path.insert(0, os.getcwd())
import er138_kp_n5_generalization_01 as n5
LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inject_log.jsonl")
state = {"gen5_fail": 0, "calls": 0}
orig = n5._send


def send(stage, model, user, schema, max_out):
    state["calls"] += 1
    if stage == "gen5" and state["gen5_fail"] < n5.MAX_ATTEMPTS:
        state["gen5_fail"] += 1
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps({"t": time.strftime("%H:%M:%S"), "stage": stage, "injected": state["gen5_fail"], "of": n5.MAX_ATTEMPTS, "call_no": state["calls"]}) + "\n")
        raise ConnectionError("injected transient failure (KP-N5 ev03 技術失敗injection)")
    return orig(stage, model, user, schema, max_out)


n5._send = send
runner = sys.argv[1]
sys.argv = [runner] + sys.argv[2:]
runpy.run_path(runner, run_name="__main__")
