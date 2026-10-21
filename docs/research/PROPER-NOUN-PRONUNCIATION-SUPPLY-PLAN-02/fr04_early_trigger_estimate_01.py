# FR-04: 初回NG時調査(早期トリガー) vs 最終slot調査 の0円試算。既存保存データのみ(API 0)。
import json,collections,hashlib,re
RETRY_YEN=5.16   # TTS+ASR 再試行1組(PNEP TRIAL_RESULT_01 §6)
INV_YEN=(5.4,16.3)  # PNEP実測 調査/語
CAP=3            # 現行Production TTS総試行上限(CURRENT_SPEC TTS生成の同一segment総試行回数上限=3)
rows=[json.loads(l) for l in open('er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl',encoding='utf8')]
real=[r for r in rows if 'Temp' not in r['wav_path'] and 'tmp' not in r['wav_path'].lower()]
ah=[json.loads(l) for l in open('er011_output/attempt_history.jsonl',encoding='utf8') if l.strip()]
byh=collections.defaultdict(list)
for a in ah:
    if 'canonical_text_sha256' in a: byh[a['canonical_text_sha256']].append(a)
def art(p):
    p=p.replace(chr(92),'/'); m=re.match(r'(er\d+_output/[^/]+/[^/]+)',p); return m.group(1) if m else p[:40]
J=[]
for r in real:
    h=hashlib.sha256(r['canonical_text'].encode('utf8')).hexdigest()
    if h in byh and r.get('pronunciation_lookups'):
        att=max(x.get('cumulative_tts_attempts',0) for x in byh[h])
        J.append((art(r['wav_path']),list(r['pronunciation_lookups']),att))
print('HR到達(実path)かつ調査対象語あり かつ attempt_history結合できた行:',len(J),'/ 実path HR行',len(real))
raw=sum(a for _,_,a in J); capped=sum(min(a,CAP) for _,_,a in J)
print('累積TTS試行(生)',raw,'上限3で打切り',capped,'初回を除く再試行(上限内)',capped-len(J))
retries=capped-len(J)
pairs={(g,w) for g,ws,_ in J for w in ws}
print('調査が走る(記事群,語)ペア数(語単位キャッシュ後)',len(pairs))
sav_max=retries*RETRY_YEN
print('再試行が全て不要になると仮定した上限削減額(円)',round(sav_max,1),'; 1ペア当たり',round(sav_max/len(pairs),2))
for c in INV_YEN:
    print(f'調査費(c={c}円/語)x{len(pairs)}ペア =',round(c*len(pairs),1),'円')
avg_retry_per_pair=retries/len(pairs)
for q in (0.14,0.5,1.0):
    print(f'取得率q={q}: 1ペア当たり期待削減={q*avg_retry_per_pair*RETRY_YEN:.2f}円(平均再試行{avg_retry_per_pair:.2f}回x{RETRY_YEN}) vs 調査費5.4円')
print('損益分岐の取得率(c=5.4):',round(5.4/(avg_retry_per_pair*RETRY_YEN),2),' (c=16.3):',round(16.3/(avg_retry_per_pair*RETRY_YEN),2))
# 追加: 調査語の内訳(重複語=Ledger/否定記録で再調査を止められる分)
ws=collections.Counter(w for g,w in pairs)
print('ペア24の語別',ws.most_common())
print('distinct語',len(ws),' 2記事群以上で重複した語のペア数(初回を除く再調査候補)',sum(v-1 for v in ws.values()))
