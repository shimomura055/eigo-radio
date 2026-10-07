# -*- coding: utf-8 -*-
"""段階2 メモリ監視(Trial専用、read-only)。15秒ごとにpython子プロセスのWorkingSet/PrivateとOS空きメモリ/コミットを eval/mem_samples.csv へ追記。"""
import subprocess, time, os, sys, csv
OUT = "er052_output/open233_control_checker_polysemy_trial_01/runs/mem_samples.csv"
PS = r'''
$os = Get-CimInstance Win32_OperatingSystem
$p = Get-Process python -ErrorAction SilentlyContinue
$n = ($p | Measure-Object).Count
$ws = ($p | Measure-Object WorkingSet64 -Maximum).Maximum
$pv = ($p | Measure-Object PrivateMemorySize64 -Maximum).Maximum
"$n,$ws,$pv,$($os.FreePhysicalMemory),$($os.TotalVirtualMemorySize),$($os.FreeVirtualMemory)"
'''
new = not os.path.exists(OUT)
with open(OUT, "a", encoding="utf-8", newline="") as f:
    if new: f.write("time,n_python,max_ws_bytes,max_private_bytes,free_phys_kb,total_virt_kb,free_virt_kb\n")
    while not os.path.exists("er052_output/open233_control_checker_polysemy_trial_01/logs/MEMMON_STOP"):
        r = subprocess.run(["powershell", "-NoProfile", "-Command", PS], capture_output=True, text=True).stdout.strip()
        f.write(time.strftime("%H:%M:%S") + "," + r + "\n"); f.flush()
        time.sleep(15)
