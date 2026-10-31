import os, subprocess, sys
S = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, S)
from ejh_dirs import DIRS, M
WT = "C:/Users/tensh/AppData/Local/Temp/claude/C--Users-tensh-eigo-radio/7eda59a9-ca6c-4f6c-9eb5-2b973c0ca046/scratchpad/wt_cap"
key = sys.argv[1]; d = DIRS[key]
cmd = [f"{M}/.venv/Scripts/python.exe", f"{S}/capw_run.py", WT, "er135_enduser_page_01", "produce", "--family", d["family"], "--dev-dir", d["dev"],
       "--run-dir", d["run"], "--cache-dir", d["run"] + "/enduser_sync_cache", "--result-json", f"{S}/produce_{key}_result.json"]
if d["ja"]: cmd += list(d["ja"])
print(" ".join(cmd), flush=True)
sys.exit(subprocess.call(cmd))
