import sys,os,time,json
sys.path.insert(0,os.path.dirname(__file__))
import dgm5_copy as d
p=sys.argv[1]
st=os.lstat(p)
print(json.dumps({"path":p,"size":st.st_size,"age_s":round(time.time()-st.st_mtime,1),"file_in_use":d.file_in_use(p)}))
