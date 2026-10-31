import os, sys, json
roots = sys.argv[2:]
out = {}
for r in roots:
    for dp, dn, fn in os.walk(r):
        for f in fn:
            p = os.path.join(dp, f)
            try:
                st = os.stat(p); out[p.replace("\\", "/")] = [st.st_size, int(st.st_mtime)]
            except OSError:
                pass
json.dump(out, open(sys.argv[1], "w"))
print(len(out))
