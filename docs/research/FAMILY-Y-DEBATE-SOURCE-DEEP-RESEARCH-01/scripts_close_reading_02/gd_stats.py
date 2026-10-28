import sys; sys.stdout.reconfigure(encoding="utf-8")
import csv, io, re
hdr = open('gd/head.bin','rb').read().decode('utf-8','replace')
cols = next(csv.reader(io.StringIO(hdr.split('\n"2-')[0])))
raw = open('gd/mid.bin','rb').read().decode('utf-8','replace'); raw = raw[raw.find('\n"2-')+1:]
rows=[r for r in csv.reader(io.StringIO(raw)) if len(r)==len(cols)]
print('rows',len(rows),'ref',rows[0][0],rows[-1][0], 'created', rows[0][2], rows[-1][2])
full=lambda r:" ".join(r[10:])
occ=re.compile(r"(je travaille|mon travail|mon métier|mon entreprise|salarié|retraité|agricult|artisan|infirmi|commerçant|chômeur|étudiant|domicile[- ]travail|domicile/travail|trajet.{0,20}travail|lieu de travail|mon employeur|mon patron)",re.I)
fam=re.compile(r"(mes enfants|mon enfant|mes? (petits-)?enfants|ma famille|mon mari|ma femme|mon épouse|mon conjoint|mes parents|nos enfants|mes fils|mes filles|mes 2 |ma fille|mon fils)",re.I)
dist=re.compile(r"\b\d+\s?(km|kilom)",re.I)
emo=re.compile(r"(j'ai peur|inquiet|inquiète|angoiss|ras-le-bol|ras le bol|marre|injuste|colère|révolt|j'aimerais|je souffre|souffre|stress|honte|fier|fière|crève|étouff|abandonn|oubli)",re.I)
n=len(rows)
c=lambda p:sum(1 for r in rows if p.search(full(r)))
print('occ',c(occ),'fam',c(fam),'dist',c(dist),'emo',c(emo))
both=sum(1 for r in rows if occ.search(full(r)) and (fam.search(full(r)) or dist.search(full(r))))
print('occ & (fam|dist)',both)
three=sum(1 for r in rows if sum(bool(p.search(full(r))) for p in (occ,fam,dist,emo))>=3)
print('>=3 of 4 categories',three)
nonemp=sum(1 for r in rows if len(full(r).strip())>20)
print('non-empty answers',nonemp)
# print specific
for ref in ('2-2376','2-2104','2-2179','2-2325','2-2105'):
    for r in rows:
        if r[0]==ref:
            print('=====',ref,r[9],r[2])
            for i in (13,14,15,17,19,21,22,25):
                if r[i].strip(): print(' [%d]'%i,r[i][:900].replace('\n',' '))
print('\n#### >=3 categories list')
for r in rows:
    f=full(r)
    if sum(bool(p.search(f)) for p in (occ,fam,dist,emo))>=3 and len(f)<1800:
        print('=====',r[0],r[9]);
        for i in (13,15,16,17,21,25):
            if r[i].strip(): print(' [%d]'%i,r[i][:350].replace('\n',' '))
