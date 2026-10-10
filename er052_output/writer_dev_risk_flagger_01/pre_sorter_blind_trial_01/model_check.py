# -*- coding: utf-8 -*-
import os, sys, json, urllib.request, urllib.error, datetime
sys.stdout.reconfigure(encoding="utf-8")
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "detectors"))
sys.dont_write_bytecode = True
from dotenv import load_dotenv; load_dotenv(os.path.join(HERE,"..","..","..",".env"))
out=dict(ts=datetime.datetime.now().isoformat(timespec="seconds"), anthropic={}, openai={})
# Anthropic
key=os.environ.get("ANTHROPIC_API_KEY")
out["anthropic"]["ANTHROPIC_API_KEY_present"]=bool(key)
out["anthropic"]["anthropic_sdk_installed_in_.venv"]=False
try:
    import anthropic; out["anthropic"]["anthropic_sdk_installed_in_.venv"]=True
except Exception as e: out["anthropic"]["sdk_error"]=repr(e)
for m in ("claude-fable-5-1","claude-opus-5-5","claude-sonnet-5-5"):
    req=urllib.request.Request("https://api.anthropic.com/v1/messages",data=json.dumps(dict(model=m,max_tokens=8,messages=[dict(role="user",content="ping")])).encode(),
        headers={"content-type":"application/json","anthropic-version":"2023-06-01"}|({"x-api-key":key} if key else {}))
    try: r=urllib.request.urlopen(req,timeout=30); out["anthropic"][m]=dict(status=r.status,body=r.read().decode()[:300])
    except urllib.error.HTTPError as e: out["anthropic"][m]=dict(status=e.code,body=e.read().decode()[:300],note="keyなしで送信(鍵が環境に無いため)" if not key else "")
    except Exception as e: out["anthropic"][m]=dict(error=repr(e))
# OpenAI
from openai import OpenAI
c=OpenAI()
for m in ("gpt-6-luna","gpt-6.1-sol","gpt-6-astra"):
    try:
        r=c.responses.create(model=m,input="Reply with the single word OK.",reasoning={"effort":"medium"},max_output_tokens=300)
        u=r.usage; out["openai"][m]=dict(ok=True,response_model=r.model,text=r.output_text[:40],in_tok=u.input_tokens,out_tok=u.output_tokens)
    except Exception as e: out["openai"][m]=dict(ok=False,error=repr(e)[:400])
json.dump(out,open(os.path.join(HERE,"model_check_01.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
print(json.dumps(out,ensure_ascii=False,indent=1))
