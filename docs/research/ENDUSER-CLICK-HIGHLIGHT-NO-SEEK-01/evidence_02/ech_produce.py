import os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ejh_dirs import DIRS, M
S = os.path.dirname(os.path.abspath(__file__))
WT = "C:/Users/tensh/ech02"
key = sys.argv[1]
d = DIRS[key]
cmd = [f"{M}/.venv/Scripts/python.exe", f"{S}/ejh_run.py", WT, M, "er135_enduser_page_01", "produce", "--family", d["family"], "--dev-dir", d["dev"],
       "--run-dir", d["run"], "--cache-dir", d["run"] + "/enduser_sync_cache", "--result-json", f"{S}/produce_{key}_result.json"]
if d["ja"]:
    cmd += list(d["ja"])
print(" ".join(cmd), flush=True)
sys.exit(subprocess.call(cmd))
