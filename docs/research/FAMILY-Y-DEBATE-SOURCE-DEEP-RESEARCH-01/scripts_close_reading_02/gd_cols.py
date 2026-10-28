import sys; sys.stdout.reconfigure(encoding="utf-8")
import csv, io
hdr = open('gd/head.bin','rb').read().decode('utf-8','replace')
cols = next(csv.reader(io.StringIO(hdr.split('\n"2-')[0])))
for i,c in enumerate(cols): print(i,c[:110])
