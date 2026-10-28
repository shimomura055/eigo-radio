import sys; sys.stdout.reconfigure(encoding="utf-8")
import csv, re
rows=list(csv.DictReader(open('polis/at.csv',encoding='utf-8')))
print('n',len(rows))
fp=re.compile(r"\b(ich|mein|meine|meinen|meinem|meiner|wir|unser|unsere|mich|mir)\b",re.I)
occ=re.compile(r"(arbeite|beruf|pendl|landwirt|bauer|pensionist|rentner|schüler|student|handwerk|selbständig|selbstständig|berufstätig|angestellt|unternehm)",re.I)
fam=re.compile(r"(kinder|meine familie|mein mann|meine frau|enkel|eltern|haushalt)",re.I)
loc=re.compile(r"(land\b|auf dem land|dorf|stadt|wohne|lebe|ländlich|gemeinde)",re.I)
c=lambda p:[r for r in rows if p.search(r['comment-body'])]
print('first-person',len(c(fp)),'occupation',len(c(occ)),'family',len(c(fam)),'residence',len(c(loc)))
sd=[r for r in rows if re.search(r"\b(ich|mein\w*|wir|unser\w*)\b",r['comment-body'],re.I) and (occ.search(r['comment-body']) or re.search(r"(wohne|lebe|auf dem land|pendl|kinder|mein mann|meine frau|meine familie)",r['comment-body'],re.I))]
print('self-disclosure (1st person + job/residence/family)',len(sd))
import statistics
print('median length',statistics.median(len(r['comment-body']) for r in rows))
for r in sd[:20]:
    print(r['comment-id'],r['agrees'],r['disagrees'],'|',r['comment-body'][:260].replace('\n',' '))
