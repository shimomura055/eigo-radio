import re,sys,html,difflib
def vis(p):
    s=open(p,encoding='utf-8').read()
    s=re.sub(r"<div class='rpt-notes'.*?</div>\s*</div>","",s,flags=re.S)  # notes block (LR/fallback)
    s=re.sub(r"<p class='rpt-legend'.*?</p>","",s,flags=re.S)
    s=s.replace("<br>","\n"); s=re.sub(r"<[^>]+>","",s); s=html.unescape(s).replace("⏸","")
    return s
a,b=vis(sys.argv[1]),vis(sys.argv[2])
wa,wb=a.split(),b.split()
sm=difflib.SequenceMatcher(None,wa,wb,autojunk=False)
for t,i1,i2,j1,j2 in sm.get_opcodes():
    if t!='equal': print(t,wa[i1:i2],'->',wb[j1:j2])
print('words',len(wa),len(wb))
