import sys; sys.stdout.reconfigure(encoding="utf-8")
import csv, io, re
hdr = open('gd/head.bin','rb').read().decode('utf-8','replace')
cols = next(csv.reader(io.StringIO(hdr.split('\n"2-')[0])))
raw = open('gd/mid.bin','rb').read().decode('utf-8','replace'); raw = raw[raw.find('\n"2-')+1:]
rows=[r for r in csv.reader(io.StringIO(raw)) if len(r)==len(cols)]
Q = {13:'touchée-comment',17:'incite-changer',19:'solutions-supportables',21:'mobilité alt-si oui',22:'mobilité alt-si non/souhait',24:'autres points'}
Qidx=[13,17,18,19,21,22,25]
fam = re.compile(r"\b(enfants?|famille|mari|épouse|conjoint|petits?-enfants|retrait|travail|boulot|salari|infirm|agricult|artisan|km|kilom|trajet|domicile|seul|handicap|rural|campagne|village|salaire|smic|loyer|crédit|budget)", re.I)
fp = re.compile(r"\b(je|j'|mon|ma|mes|nous|notre|nos)\b", re.I)
c=[]
for r in rows:
    t=" ".join(r[i] for i in Qidx if i<len(r))
    if 200<=len(t)<=1400 and len(fp.findall(t))>=3 and len(fam.findall(t))>=3:
        c.append((len(fam.findall(t)),r))
c.sort(key=lambda x:-x[0])
print(len(rows), 'candidates', len(c))
for n,r in c[:14]:
    print('=====',r[0],'zip',r[9],r[2],'famhits',n)
    for i in Qidx:
        if i<len(r) and r[i].strip(): print('  [%d]'%i, r[i][:420].replace('\n',' '))
