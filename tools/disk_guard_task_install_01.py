"""disk_guard_task_install_01: disk_guard_01 を60分間隔で実行するWindowsタスクを登録(DISK-GUARD-AUTO-CLEANUP-01 R-3a/R-8)。API 0。

ユーザー権限(RunLevel=LeastPrivilege・管理者不要)・pythonw.exe(窓なし)・StartWhenAvailable・電池駆動でも実行・多重起動はIgnoreNew。
実行内容 = `pythonw disk_guard_01.py --auto --quiet`(空き>=20GBなら軽量チェックのみ。<10GBで自動整理)。
使い方: python tools/disk_guard_task_install_01.py [--script <disk_guard_01.pyのpath>] [--dry-run]
削除: schtasks /delete /tn eigo-radio-disk-guard /f
"""
import argparse
import os
import subprocess
import sys
import tempfile
import time

TASK = "eigo-radio-disk-guard"
DEFAULT_SCRIPT = r"C:\Users\tensh\eigo-radio\tools\disk_guard_01.py"
DEFAULT_PYW = r"C:\Users\tensh\eigo-radio\.venv\Scripts\pythonw.exe"

XML = """<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>DISK-GUARD-AUTO-CLEANUP-01: C drive free-space guard (60min interval, --auto --quiet). Records: %LOCALAPPDATA%\\eigo-radio\\disk_guard</Description>
  </RegistrationInfo>
  <Triggers>
    <TimeTrigger>
      <Repetition>
        <Interval>PT60M</Interval>
        <StopAtDurationEnd>false</StopAtDurationEnd>
      </Repetition>
      <StartBoundary>{start}</StartBoundary>
      <Enabled>true</Enabled>
    </TimeTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <ExecutionTimeLimit>PT15M</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>{pyw}</Command>
      <Arguments>"{script}" --auto --quiet</Arguments>
    </Exec>
  </Actions>
</Task>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", default=DEFAULT_SCRIPT)
    ap.add_argument("--pythonw", default=DEFAULT_PYW)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    xml = XML.format(start=time.strftime("%Y-%m-%dT%H:%M:%S"), pyw=a.pythonw, script=a.script)
    if a.dry_run:
        print(xml)
        return 0
    fd, path = tempfile.mkstemp(suffix=".xml", prefix="dg_task_")
    os.close(fd)
    with open(path, "w", encoding="utf-16") as fh:
        fh.write(xml)
    r = subprocess.run(["schtasks", "/create", "/tn", TASK, "/xml", path, "/f"], capture_output=True, text=True)
    os.remove(path)
    print(r.stdout.strip(), r.stderr.strip())
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
