import sys; sys.stdout.reconfigure(encoding="utf-8")
import csv, re
rows=list(csv.DictReader(open('polis/at.csv',encoding='utf-8')))
p1=re.compile(r"\bich\b.{0,80}\b(arbeite|pendle|fahre|wohne|lebe|habe\b.{0,20}(kinder|auto|familie|haus|job)|bin\b.{0,20}(landwirt|bauer|pendler|mutter|vater|pensionist|rentner|schüler|student|alleinerziehend|selbst))",re.I|re.S)
p2=re.compile(r"\b(meine? (kinder|familie|frau|mann|eltern|großeltern|kunden|firma|arbeit)|mein (job|beruf|betrieb|arbeitsweg|auto)|als (landwirt|bauer|pendler|mutter|vater|pensionist|selbst\w+|handwerker|lehrer\w*))\b",re.I)
hit=[r for r in rows if p1.search(r['comment-body']) or p2.search(r['comment-body'])]
print(len(hit),'of',len(rows), round(100*len(hit)/len(rows),1),'%')
for r in hit:
    print(r['comment-id'],r['agrees'],r['disagrees'],'|',r['comment-body'][:300].replace('\n',' '))
