# -*- coding: utf-8 -*-
"""KP-DIFFICULTY-4LEVEL-DISPLAY-01 委任_04 held-out評価の共通部(Cap 4円固定)。本番moduleは変更しない。"""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
MAIN = r'C:\Users\tensh\eigo-radio'
OUT = os.path.join(HERE, 'kpd04_out'); os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, ROOT)
CAP_JPY = 4.0
USD_JPY = 160.0
PRICE = {"gpt-6-luna": (0.10, 0.01, 0.50), "gemini-3.8-flash": (0.75, 0.075, 3.75)}   # $/1M (in, cached, out) 出典: docs/pm/dev_eval_model_inventory_01.md
# held-out: 委任_02の55件(ai_island_temple/redelivery_fee/melos)と重複しない既存run保存doc
SETS = [
    ('X', 'a2', 'coffee', MAIN + r'\er019_output\family_x_audio_production_wiring_01\coffee_prices__run_kpbf_ev_02\a2\key_phrases\kp_candidates.json'),
    ('X', 'b1b', 'coffee', MAIN + r'\er019_output\family_x_audio_production_wiring_01\coffee_prices__run_kpbf_ev_02\b1b\key_phrases\kp_candidates.json'),
    ('X', 'a2', 'yemen', MAIN + r'\er019_output\family_x_audio_production_wiring_01\middle_east_yemen_saudi__run_kpbf_ev_03\a2\key_phrases\kp_candidates.json'),
    ('X', 'b1b', 'yemen', MAIN + r'\er019_output\family_x_audio_production_wiring_01\middle_east_yemen_saudi__run_kpbf_ev_03\b1b\key_phrases\kp_candidates.json'),
    ('Y', 'a2', 'surname', MAIN + r'\er121_output\family_y_production_01\surname_choice\run_02\key_phrases\a2\kp_candidates.json'),
    ('Y', 'b1b', 'surname', MAIN + r'\er121_output\family_y_production_01\surname_choice\run_02\key_phrases\b1b\kp_candidates.json'),
    ('Z', 'a2', 'grove', MAIN + r'\er026_output\family_z_production_e2e_01\in_a_grove\run_sf_prod_01\key_phrases\a2\kp_candidates.json'),
    ('Z', 'b1b', 'grove', MAIN + r'\er026_output\family_z_production_e2e_01\in_a_grove\run_sf_prod_01\key_phrases\b1b\kp_candidates.json'),
]
USER_EXAMPLES = [
    {"candidate_id": "ux_rely", "selection_phrase": "rely on", "used_form": "rely on", "japanese_gloss": "〜に頼る", "source_sentence": "Many people rely on public transport to get to work.", "kind": "phrase"},
    {"candidate_id": "ux_room", "selection_phrase": "make room for", "used_form": "make room for", "japanese_gloss": "〜のために場所・余地を空ける", "source_sentence": "We need to move the table to make room for the new sofa.", "kind": "phrase"},
    {"candidate_id": "ux_narrow", "selection_phrase": "narrow down", "used_form": "narrow down", "japanese_gloss": "(候補などを)絞り込む", "source_sentence": "The committee tried to narrow down the list to three finalists.", "kind": "phrase"},
]
ORD = {'easy': 0, 'medium': 1, 'hard': 2, 'rare': 3}

def load_sets():
    out = []
    for fam, lv, art, p in SETS:
        d = json.load(open(p, encoding='utf-8'))
        out.append({'family': fam, 'level': lv, 'name': f'{fam}:{art}-{lv}', 'path': p, 'cands': d['candidates']})
    return out

def cost_of(model, tin, tout, cached=0):
    p = PRICE[model]
    return (((tin - cached) * p[0] + cached * p[1] + tout * p[2]) / 1e6) * USD_JPY

def ledger_total():
    f = os.path.join(OUT, 'kpd04_cost_ledger.jsonl')
    return sum(json.loads(l).get('cost_jpy', 0.0) for l in open(f, encoding='utf-8') if l.strip()) if os.path.exists(f) else 0.0

def ledger(rec):
    with open(os.path.join(OUT, 'kpd04_cost_ledger.jsonl'), 'a', encoding='utf-8') as f:
        f.write(json.dumps(rec, ensure_ascii=False) + '\n')

def jobs():
    return [(s['name'], s['cands'], s['level']) for s in load_sets()] + [('UX-a2', USER_EXAMPLES, 'a2'), ('UX-b1b', USER_EXAMPLES, 'b1b')]

def v3_text(old):
    """v3: 難/激難の定義具体化(Prompt文言のみ)。ユーザー表示例 rely on/make room for/narrow down は文言に入れない(held-out検証用)。"""
    def rep(s, a, b):
        assert s.count(a) == 1, a
        return s.replace(a, b)
    new = rep(old, "- hard(難): 高度な語彙・熟語・用法の理解が必要な表現。抽象的・文語的・比喩的な用法、複数の意味を使い分ける句動詞・イディオムなど。\n",
      "- hard(難): 高度な語彙・熟語・用法の理解が必要な表現。次のいずれかに当たるものは原則hard: (a)比喩的・慣用的な句動詞/イディオムで、文字どおりの意味では全体の意味が取れないもの(例: bear out, brush off, throw in the towel) (b)文語・文学語、書き言葉で使われる語(例: hideous, linger, gaze) (c)抽象語・概念語(例: disparity, leverage, resilience) (d)辞書で上級(C1相当)の語義・用法として載るもの。\n")
    new = rep(new, "- rare(激難・レア): 特に高度、または使用頻度が低く特殊性の強い表現。専門的・文学的・古風・地域限定の語、ほとんど辞書でしか見ない表現。\n",
      "- rare(激難・レア): 特に高度、または使用頻度が低く特殊性の強い表現。稀な文学語・専門語・古風な表現で、ネイティブでも日常ではまず使わないもの(例: doff, perspicacious, obsequious)。\n")
    new = rep(new, "- easy(易): 比較的基本的で習得しやすい表現。中学〜高校初級で習う語・熟語、日常会話で頻出する表現。\n",
      "- easy(易): 比較的基本的で習得しやすい表現。中学〜高校初級で習う基本語・基本句動詞(例: look for, get up, weather)。\n")
    new = rep(new, "- medium(中): 一般的な英語学習で一定の習熟が必要な表現。ニュースや読み物に普通に出てくるが、意味・用法の理解に練習が要るもの。\n",
      "- medium(中): 上のeasy・hard・rareのどれにも当たらない一般語・一般的な句動詞(例: come up with, reliable, take over)。ニュースや読み物に普通に出てくるもの。\n")
    new = rep(new, "5. 迷ったときは極端な段階を避け、より近い段階を選ぶ。全項目に必ず1つの段階を付ける。\n",
      "5. 上の定義に当てはまる項目は、迷っても段階を下げず該当する段階を付ける(hardの条件(a)〜(d)に当たるものをmediumにしない)。全項目に必ず1つの段階を付ける。\n")
    for ex in ('rely on', 'make room for', 'narrow down'):
        assert ex not in new
    return new
