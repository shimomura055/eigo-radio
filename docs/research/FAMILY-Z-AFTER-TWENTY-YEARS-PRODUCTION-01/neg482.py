import sys,os,importlib.util
sys.path.insert(0,os.getcwd());sys.path.insert(0,sys.argv[1])
import er006_preprod_hardening_01_validation as new
spec=importlib.util.spec_from_file_location("er006_old",sys.argv[1]+"/er006_old.py");old=importlib.util.module_from_spec(spec);sys.modules["er006_old"]=old;spec.loader.exec_module(old)
def chk(m,c,a):
    r=m.protected_check(m.tokenize(c),m.tokenize(a));return r.passed,r.number_mismatches
cases=[
("At ten thirty, a tall man","At 10:30, a tall man","PASS"),
("At ten thirty, a tall man","At ten-thirty, a tall man","PASS"),
("At ten thirty, a tall man","At 10:13, a tall man","NG"),
("At ten thirty, a tall man","At ten, a tall man","NG"),
("At ten thirty, a tall man","At 10, a tall man","NG"),
("At ten thirty, a tall man","At 10:15, a tall man","NG"),
("At ten thirty, a tall man","At 40, a tall man","NG"),
("At ten thirty, a tall man","At 30, a tall man","NG"),
("At ten thirty, a tall man","At forty, a tall man","NG"),
("At ten thirty, a tall man","At 10:03, a tall man","NG"),
("At two thirty, a tall man","At 2:30, a tall man","PASS"),
("At two thirty, a tall man","At 2:03, a tall man","NG"),
("At two thirty, a tall man","At 2:13, a tall man","NG"),
("At two thirty, a tall man","At 32, a tall man","NG"),
("At ten thirty, a tall man","At 11:30, a tall man","NG"),
("At one thirty, a tall man","At 1:30, a tall man","PASS"),
("At twenty one, a tall man","At 21, a tall man","PASS"),
("At twenty one, a tall man","At 20:1, a tall man","NG"),
("one hundred thirty people","130 people","PASS"),
("two hundred and five people","205 people","PASS"),
("at seven fifteen sharp","at 7:15 sharp","PASS"),
("at seven fifteen sharp","at 7:50 sharp","NG"),
]
for c,a,exp in cases:
    po=chk(old,c,a);pn=chk(new,c,a)
    print(f"{exp:4} old={po[0]!s:5} new={pn[0]!s:5} {'OK ' if pn[0]==(exp=='PASS') else 'BAD'} | {c} || {a} | new_mm={pn[1]}")
