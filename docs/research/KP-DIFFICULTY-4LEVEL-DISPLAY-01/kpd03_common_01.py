# -*- coding: utf-8 -*-
"""KP-DIFFICULTY-4LEVEL-DISPLAY-01 委任_03 held-out評価の共通部(Cap 6円固定)。本番moduleは変更しない。"""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
MAIN = r'C:\Users\tensh\eigo-radio'
OUT = os.path.join(HERE, 'kpd03_out'); os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, ROOT)
CAP_JPY = 6.0
USD_JPY = 160.0
PRICE = {"gpt-6-luna": (0.10, 0.01, 0.50), "gemini-3.8-flash": (0.75, 0.075, 3.75)}   # $/1M (in, cached, out) 出典: docs/pm/dev_eval_model_inventory_01.md
# held-out: 委任_02の55件(ai_island_temple/redelivery_fee/melos)と重複しない既存run保存doc
SETS = [
    ('X', 'a2', MAIN + r'\er019_output\family_x_audio_production_wiring_01\uk_train_speaker_playback__run_kp75_ev_01\a2\key_phrases\kp_candidates.json'),
    ('X', 'b1b', MAIN + r'\er019_output\family_x_audio_production_wiring_01\uk_train_speaker_playback__run_kp75_ev_01\b1b\key_phrases\kp_candidates.json'),
    ('Y', 'a2', MAIN + r'\er121_output\family_y_production_01\sns_age_limit\run_01\key_phrases\a2\kp_candidates.json'),
    ('Y', 'b1b', MAIN + r'\er121_output\family_y_production_01\sns_age_limit\run_01\key_phrases\b1b\kp_candidates.json'),
    ('Z', 'a2', MAIN + r'\er026_output\family_z_production_e2e_01\the_tell_tale_heart\run_reselect_01\key_phrases\a2\kp_candidates.json'),
    ('Z', 'b1b', MAIN + r'\er026_output\family_z_production_e2e_01\the_tell_tale_heart\run_reselect_01\key_phrases\b1b\kp_candidates.json'),
]
USER_EXAMPLES = [
    {"candidate_id": "ux_rely", "selection_phrase": "rely on", "used_form": "rely on", "japanese_gloss": "〜に頼る", "source_sentence": "Many people rely on public transport to get to work.", "kind": "phrase"},
    {"candidate_id": "ux_room", "selection_phrase": "make room for", "used_form": "make room for", "japanese_gloss": "〜のために場所・余地を空ける", "source_sentence": "We need to move the table to make room for the new sofa.", "kind": "phrase"},
    {"candidate_id": "ux_narrow", "selection_phrase": "narrow down", "used_form": "narrow down", "japanese_gloss": "(候補などを)絞り込む", "source_sentence": "The committee tried to narrow down the list to three finalists.", "kind": "phrase"},
]
ORD = {'easy': 0, 'medium': 1, 'hard': 2, 'rare': 3}

def load_sets():
    out = []
    for fam, lv, p in SETS:
        d = json.load(open(p, encoding='utf-8'))
        out.append({'family': fam, 'level': lv, 'path': p, 'cands': d['candidates']})
    return out

def cost_of(model, tin, tout, cached=0):
    p = PRICE[model]
    return (((tin - cached) * p[0] + cached * p[1] + tout * p[2]) / 1e6) * USD_JPY

def ledger_total():
    f = os.path.join(OUT, 'kpd03_cost_ledger.jsonl')
    return sum(json.loads(l).get('cost_jpy', 0.0) for l in open(f, encoding='utf-8') if l.strip()) if os.path.exists(f) else 0.0

def ledger(rec):
    with open(os.path.join(OUT, 'kpd03_cost_ledger.jsonl'), 'a', encoding='utf-8') as f:
        f.write(json.dumps(rec, ensure_ascii=False) + '\n')

def jobs():
    return [(f"{s['family']}-{s['level']}", s['cands'], s['level']) for s in load_sets()] + [('UX-a2', USER_EXAMPLES, 'a2'), ('UX-b1b', USER_EXAMPLES, 'b1b')]

def v2_text(old):
    new = old.replace("4. 基準の目安(例): easy=look for, weather / medium=come up with, reliable / hard=stave off, disparity / rare=doff, perspicacious。\n",
      "4. 基準の目安(例): easy=look for, weather, pick up / medium=come up with, reliable, hold back / hard=stave off, disparity, bear out / rare=doff, perspicacious。\n")
    new = new.replace("5. 迷ったときは極端な段階を避け、より近い段階を選ぶ。全項目に必ず1つの段階を付ける。\n",
      "5. 基準は日本の英語学習者の視点: easyは中学〜高校初級で習う基本語・基本熟語に限る。それ以外の句動詞・イディオム・比喩的/文語的な語・多義で用法に注意が要る語は原則medium以上。全項目に必ず1つの段階を付け、候補全体で段階を使い分ける(全部同じ段階にしない)。\n")
    assert new != old and new.count('pick up') == 1 and '使い分ける' in new
    return new
