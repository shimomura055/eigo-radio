# usage: python launch_gate.py <label>   -- blocks until >=150s since the last recorded launch (and <=1 launch in the last 300s window besides it), then records this launch.
import sys, time, os
F = os.path.join(os.path.dirname(os.path.abspath(__file__)), "launch_epochs.txt")
label = sys.argv[1]
while True:
    rows = []
    if os.path.exists(F):
        for l in open(F).read().splitlines():
            t, _, lab = l.partition(" ")
            rows.append((float(t), lab))
    now = time.time()
    last = max([t for t, _ in rows] or [0])
    recent = [t for t, _ in rows if now - t < 300]
    if now - last >= 150 and len(recent) < 2:
        break
    time.sleep(5)
with open(F, "a") as f:
    f.write(f"{time.time()} {label}\n")
with open(os.path.join(os.path.dirname(F), "launch_times.txt"), "a") as f:
    f.write(time.strftime("%H:%M:%S") + "\n" + label + "\n")
print("gate ok", label)
