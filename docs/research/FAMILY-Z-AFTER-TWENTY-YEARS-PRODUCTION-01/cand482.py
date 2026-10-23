import sys,os,importlib.util
sys.path.insert(0,os.getcwd());sys.path.insert(0,sys.argv[1])
import er078_asr_value_guard_01 as old
spec=importlib.util.spec_from_file_location("er078_cand",sys.argv[1]+"/er078_cand.py");new=importlib.util.module_from_spec(spec);sys.modules["er078_cand"]=new;spec.loader.exec_module(new)
cases=[("At ten thirty, a tall man","At 10:30, a tall man","PASS"),("At 10 thirty, a tall man","At 10:30, a tall man","PASS"),
("At ten thirty, a tall man","At 10:13, a tall man","NG"),("At ten thirty, a tall man","At 10:15, a tall man","NG"),("At ten thirty, a tall man","At 11:30, a tall man","NG"),
("At two thirty, a tall man","At 2:03, a tall man","NG"),("At two thirty, a tall man","At 2:30, a tall man","PASS"),("At ten thirty, a tall man","At ten, a tall man","NG"),
("At ten thirty, a tall man","At 40, a tall man","NG"),("At ten thirty, a tall man","At 30, a tall man","NG"),("At ten thirty, a tall man","At 1030, a tall man","NG"),
("At ten thirty pm, a tall man","At 10:30 pm, a tall man","PASS"),("At ten thirty pm","At 10:30 am","NG"),
("At 10:30, a tall man","At ten thirty, a tall man","PASS"),("At twenty one","At 21","PASS"),("At twenty one","At 20:1","NG")]
for s,h,e in cases:
    o=old.value_guard(s,h,"en");n=new.value_guard(s,h,"en")
    print(f"{e:4} old={o.kind:10} new={n.kind:10} {'OK' if (n.kind in ('EQUAL','NO_VALUES','AMBIGUOUS'))==(e=='PASS') else 'BAD'} | {s} || {h}")
