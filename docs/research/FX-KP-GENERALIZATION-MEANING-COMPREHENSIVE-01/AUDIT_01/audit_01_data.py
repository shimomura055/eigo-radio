# AUDIT_01 データ層(読み取り専用。API 0)。ADV/STD/CONSISTENCY生成scriptが共用。
import sys, re, json, collections
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))
from audit_01_t3 import *   # rows, G, E, blind, gl, fable, FAIL, TIN, key
r2, bad2 = load_jsonl(T2/'results.jsonl')
cs2 = load_cache(T2/'judge/sonnet/cache.jsonl')
n30 = open(T2/'e4_normal30.txt', encoding='utf-8').read().strip().split('|')

def e3(r):
    return cs2[rid('E3', r['key'], r['sent'], r['text'])]['verdict']
def g2v(r):
    return cs2[rid('G', r['key'], r['sent'], r['gloss'])]['verdict']
def p3(x):
    return x['sense_ok'] == 1 and x['core'] == 1 and x['single'] == 1
def flags(x):
    f = []
    if x['sense_ok'] == 0: f.append('sense')
    if x['core'] == 0: f.append('core')
    if x['single'] == 0: f.append('single')
    return f
def gok(v):
    return v['sense_ok'] == 1 and v['literal'] == 0 and v['deictic'] == 0
def gflags(v):
    f = []
    if v['sense_ok'] == 0: f.append('sense_ok=0')
    if v['literal']: f.append('literal')
    if v['deictic']: f.append('deictic')
    if v['specific']: f.append('specific')
    if v['multi']: f.append('multi')
    return f

# T02 G行(gloss生成元)の行番号
g2line = {(r['arm'], r['key'], r['rep']): r['_line'] for r in r2 if r['kind'] == 'G'}
def gline_for(arm, key, rep):
    return g2line.get((arm, key, rep)) or g2line.get((arm, key, 1))

# Sonnet T03 detail
SON = {}
for l in open(T3/'sonnet_reference_03_detail.md', encoding='utf-8'):
    m = re.match(r'^\| (hard|normal)/(\S*) \| (.*?) \| (.*)\|\s*$', l)
    if not m: continue
    cells = [c.strip() for c in m.group(4).split('|')]
    if len(cells) != 6: continue
    SON[m.group(3).lower()] = cells
SONARM = [('G0',1),('G0',2),('G2',1),('G2',2),('G3',1),('G3',2)]
def sonnet(kp, arm, rep):
    c = SON[kp.lower()][SONARM.index((arm, rep))]
    return c[0], c[2:]
LBL = {'P': 'PASS', 'T': 'THIN', 'F': 'FAIL'}

def std_label_A(keyn, gloss):
    """Trial_02 G0 gloss(難例20)の正誤。Opus個別判定は未記録のため、判定の出所を併記。"""
    if gloss == '線を引く':
        return '誤り', '字義訳。GOLD_LABELS_FINAL_01の「不可: 線を引く」に明記。Opus Std G0 24/26のNG2件の1つ(確実)'
    if gloss == '人の財布に手を伸ばす':
        return '誤り', '盗む読み。Fable T03で同一文字列がFAIL(blind #15 D)。Opus G0 NG2件の1つ(推定: OPUS_REVIEW_04.md:5「難例の誤り2種」+委任_08 §1「draw a line字義、reach for someone\'s wallet」)'
    if gloss == '人の研究結果を応用する':
        return '正(要注意)', 'Opus G0 NG2件に含まれない(推定)ため正。Sonnet暫定=deictic指摘。Fable T03はG3「人の研究結果を当てはめる」をFAIL(所有者誤り)としており、同型で基準差の可能性(CONSISTENCY_01参照)'
    return '正', 'Opus G0 24/26のNG2件の対象外(推定)。個別判定ログは未保存'
