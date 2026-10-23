import sys,os,importlib.util
sys.path.insert(0,os.getcwd())
import er078_asr_value_guard_01 as new
spec=importlib.util.spec_from_file_location("er078_old",sys.argv[1]);old=importlib.util.module_from_spec(spec);sys.modules["er078_old"]=old;spec.loader.exec_module(old)
POS=[("At 10 thirty, a tall man","At 10:30, a tall man"),("At 10 30, a tall man","At 10:30, a tall man"),("At 10:30, a tall man","At 10 thirty, a tall man"),
("At 2 thirty, he left","At 2:30, he left"),("At 1 thirty, he left","At 1:30, he left"),("At 7 fifteen sharp","At 7:15 sharp"),
("At 10 thirty, a tall man","At 10 thirty, a tall man"),("At 5 thirty 10","At 5:30 10")]
NEG=[("At 10 thirty","At 10:13"),("At 10 thirty","At 10:15"),("At 10 thirty","At 10:03"),("At 10 thirty","At 11:30"),("At 10 thirty","At 10"),
("At 10 thirty","At 40"),("At 10 thirty","At 30"),("At 10 thirty","At 10:30 pm"),("At 10 thirty pm","At 10:30 am"),("At 10 thirty pm","At 10:30 pm"),
("At 2 thirty","At 2:03"),("At 2 thirty","At 2:13"),("At 2 thirty","At 32"),("At 7 fifteen","At 7:50"),("At 12 thirty","At 12:03"),
("At 1:30","At 13:00"),("At 3 forty","At 3:04"),("At 11 fifty","At 11:15"),("At 9 ten","At 9:01"),("At 10 thirty","At 10:30:15"),("At 10 thirty","At 20:30"),("At 25 thirty","At 25:30"),("At 10 apples and 30 pears","At 10:30"),
("At 10 percent 30","At 10:30"),("At $10 30","At 10:30"),("At 10 sixty","At 10:60"),("At 10 thirty","At 10:30 and 5")]
bad=0
def ok(k): return k in ("EQUAL","NO_VALUES","AMBIGUOUS")
print("POS");
for s,h in POS:
    o=old.value_guard(s,h,"en");n=new.value_guard(s,h,"en");f="OK " if ok(n.kind) else "BAD"; bad+= f=="BAD"
    print(f, f"old={o.kind:8} new={n.kind:8}", s,"||",h)
print("NEG")
for s,h in NEG:
    o=old.value_guard(s,h,"en");n=new.value_guard(s,h,"en");f="OK " if not ok(n.kind) else "BAD"; bad+= f=="BAD"
    pa = "PASS->NG!" if ok(o.kind) and not ok(n.kind) else ""
    print(f, f"old={o.kind:8} new={n.kind:8}",pa, s,"||",h)
print("bad=",bad)
