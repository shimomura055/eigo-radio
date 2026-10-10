# -*- coding: utf-8 -*-
import os, sys, json, re, collections
sys.stdout.reconfigure(encoding="utf-8")
HERE=os.path.dirname(os.path.abspath(__file__))
PK=json.load(open(os.path.join(HERE,"blind_packet_01.json"),encoding="utf-8")); IDS=[x["id"] for x in PK["items"]]
ITEM={x["id"]:x for x in PK["items"]}
MODELS=[("Fable","claude-fable-5-1"),("Opus","claude-opus-5-5"),("Sonnet","claude-sonnet-5-5"),("Luna","gpt-6-luna"),("Sol","gpt-6.1-sol"),("Astra","gpt-6-astra")]
R={}; S={}
for nm,mid in MODELS:
    d=os.path.join(HERE,"runs",mid)
    if not os.path.isdir(d): continue
    res={}; s=dict(cost=0,inp=0,out=0,reas=0,retries=0,fails=0,calls=0,resp_models=set(),resp_ids=[],ts=[])
    for b in (1,2,3):
        j=json.load(open(os.path.join(d,"batch_%d.json"%b),encoding="utf-8"))
        s["retries"]+=int(j["retried"]); s["fails"]+=int(not j["valid"]); s["cost"]+=j["total_cost_jpy"]
        for a in j["attempts"]:
            s["calls"]+=1
            if "usage" in a: s["inp"]+=a["usage"]["input_tokens"]; s["out"]+=a["usage"]["output_tokens"]; s["reas"]+=a["usage"]["reasoning_tokens"] or 0; s["resp_models"].add(a["response_model"]); s["resp_ids"].append(a["response_id"]); s["ts"].append(a["timestamp"])
        for x in j["parsed"] or []: res[x["id"]]=x
    R[nm]=res; S[nm]=s
# 23番 = ID順の23件目
N23=IDS[22]
KW=re.compile(r"split|truncat|cut off|cut-off|cut short|fragment|incomplete|abbreviat|sentence break|breaks? (?:off|mid)|mid-sentence|artifact|period after|\"U\.S\.\"|U\.S\. as|sentence boundary|segmentation|chopped|broken",re.I)
L=["# RESULT_01: POST-EN-HUMAN-PRE-SORTER-BLIND-TRIAL-01 一次報告(Trial/DEV、2026-10-10)","",
"**User/ChatGPTのA/B/C/D判定は一切参照していない。User列・一致率はない(ChatGPT側で照合)。Production変更ゼロ。AI Pre-sorterのProduction wiringへは進まない。**","",
"## 0. 実行できたモデル/できなかったモデル",
"- 実行できた(3): Luna `gpt-6-luna` / Sol `gpt-6.1-sol` / Astra `gpt-6-astra`(OpenAI Responses API直接、reasoning effort=medium、API応答のmodel欄と要求IDが一致)。",
"- **UNAVAILABLE(3)**: Fable `claude-fable-5-1` / Opus `claude-opus-5-5` / Sonnet `claude-sonnet-5-5`。理由: ANTHROPIC_API_KEYが環境(process/User/Machine/.env)に存在しない・`.venv`にanthropic SDKなし。api.anthropic.comへ3モデルを鍵なしで疎通し3件とも HTTP 401 authentication_error「x-api-key header is required」(model_check_01.json、request_id記録)。モデルの存在・権限は鍵がないため未検証。別モデルへの置換なし。GPT系3モデルのみ先行実施(ユーザー指示7のfallback)。","",
"## 1. 一覧(Blind判定。User列なし。IDはPOST-EN-TRIAL-01の既存ID(稿番号-文番号)、ID順=BLIND_PACKET_01.mdの並び)","",
"| # | ID | Fable | Opus | Sonnet | Luna | Sol | Astra |","|---|---|---|---|---|---|---|---|"]
for i,k in enumerate(IDS,1):
    L.append("| %d | %s | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | %s |"%(i,k," | ".join(R[m][k]["grade"] for m in ("Luna","Sol","Astra"))))
L+=["","## 2. モデル別集計(実測)","","| モデル | actual model_id(API応答) | A | B | C | D | 修正推奨Yes | Human Review High | 費用(実測JPY) | 入力tok | 出力tok(うちreasoning) | calls | retry | API/JSON failure |","|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
for nm in ("Luna","Sol","Astra"):
    r=R[nm]; c=collections.Counter(x["grade"] for x in r.values()); s=S[nm]
    L.append("| %s | %s | %d | %d | %d | %d | %d | %d | %.2f | %d | %d (%d) | %d | %d | %d |"%(nm,",".join(sorted(s["resp_models"])),c["A"],c["B"],c["C"],c["D"],sum(x["fix_recommended"]=="Yes" for x in r.values()),sum(x["human_review_value"]=="High" for x in r.values()),s["cost"],s["inp"],s["out"],s["reas"],s["calls"],s["retries"],s["fails"]))
tot=sum(S[m]["cost"] for m in S)
L+=["| Fable/Opus/Sonnet | - | UNAVAILABLE | | | | | | 0 | | | 0 | | |","",
"合計実費 **JPY %.2f**(見積 中央JPY249.5/高位JPY452.8に対し大幅に下回った。見積のreasoning仮定が過大だった。実測の1モデル当たり入力/出力は上表)。routing: 全て直接OpenAI API(api.openai.com、Responses API)、effort=medium、max_output_tokens=16,000。単価: 登録値(Luna 0.1/0.5、Sol 2/10、Astra 10/50 $/1M、USD/JPY=160、cached入力は登録cached単価)。"%tot,
"retry: 全9 callで再試行なし・JSON valid(attempts=1)。API failure: 0。使用モデル: 最新世代(Luna=最新の効率系、Sol 6.1=最新の推奨系、Astra=最新の旗艦、PM_GOVERNANCE 25節)。runtime evidence: `runs/<model_id>/batch_<n>.json`(system_prompt・user_message・packet/prompt sha・raw_text・response_id・usage・cost・timestamp・retried・parsed)、`cost_ledger_presorter_01.jsonl`。",""]
# モデル間一致
L+=["## 3. モデル間の一致(3モデルのみ。User判定との照合は行わない)",""]
allsame=[k for k in IDS if len({R[m][k]["grade"] for m in ("Luna","Sol","Astra")})==1]
L.append("- 3モデル全一致: %d/29件。"%len(allsame))
sp=[k for k in IDS if len({R[m][k]["grade"] for m in ("Luna","Sol","Astra")})==3]
big=[k for k in IDS if max(ord(R[m][k]["grade"]) for m in ("Luna","Sol","Astra"))-min(ord(R[m][k]["grade"]) for m in ("Luna","Sol","Astra"))>=2]
L.append("- 3モデルが全て異なる件: %s"%(", ".join(sp) or "なし"))
L.append("- 最大差が2段階以上(例 A-C, B-D)の件: %s"%(", ".join("%s(%s)"%(k,"/".join(R[m][k]["grade"] for m in ("Luna","Sol","Astra"))) for k in big) or "なし"))
for a,b in (("Luna","Sol"),("Luna","Astra"),("Sol","Astra")):
    L.append("- %s vs %s 完全一致: %d/29"%(a,b,sum(R[a][k]["grade"]==R[b][k]["grade"] for k in IDS)))
L+=["",""]
# 23番
L+=["## 4. 23番(ID順23件目 = %s。U.S.のピリオドでsentence splitterが途中切断した例のうち、ユーザー指示の「23番」に相当すると推定した位置。対象モデルには一切教えていない)"%N23,"",
"Flag対象文: %s"%ITEM[N23]["flagged_sentence"]["text"],""]
for nm in ("Luna","Sol","Astra"):
    x=R[nm][N23]; m=KW.search(x["reason"])
    L.append("- %s: grade=%s / fix=%s / HR=%s / splitter・切断への言及(キーワード機械判定)=%s%s\n  理由: %s"%(nm,x["grade"],x["fix_recommended"],x["human_review_value"],"あり" if m else "なし",(" 「%s」"%m.group(0)) if m else "",x["reason"]))
L+=["","参考: 全29件の理由文のうち分割/切断への言及(同キーワード機械判定)があった件:",""]
for nm in ("Luna","Sol","Astra"):
    ks=[k for k in IDS if KW.search(R[nm][k]["reason"])]
    L.append("- %s: %s"%(nm,", ".join(ks) or "なし"))
L+=["","(注: 23番=ID順23件目という対応は推定。ユーザーの番号体系と違う場合は ChatGPT側で補正。同じくU.S.で切れた文の候補が他にも29件内にある場合がある。)",""]
L+=["## 5. 各判定理由の全文(モデル別。raw responseから転記、改変なし)",""]
for nm in ("Luna","Sol","Astra"):
    L+=["### %s"%nm,""]
    for i,k in enumerate(IDS,1):
        x=R[nm][k]; L.append("- **%d. %s** [%s] fix=%s HR=%s — %s"%(i,k,x["grade"],x["fix_recommended"],x["human_review_value"],x["reason"].replace("\n"," ")))
    L.append("")
L+=["## 6. 未決事項・STOP","- Fable/Opus/Sonnetの実行にはANTHROPIC_API_KEY(とSDK)の用意が必要(ユーザー判断)。用意されれば同じpacket/prompt/バッチで追実行可能(事前登録のsha固定済み)。ただし今回はSTOP。","- User/ChatGPTのA/B/C/D照合はChatGPT側。Production wiringへは進まない。Closeout分類(Sonnet提案): USER_DECISION_REQUIRED(Anthropic 3モデル未実施・User照合未了のためVALIDATED/REJECTEDにしない)。Fable確定。",""]
open(os.path.join(HERE,"RESULT_01.md"),"w",encoding="utf-8",newline="\n").write("\n".join(L))
print("\n".join(L[:70]))
