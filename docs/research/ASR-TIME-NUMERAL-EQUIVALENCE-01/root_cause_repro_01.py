"""ROOT_CAUSE_01 の再現(API 0)。正式経路の関数を実入力で呼ぶ。--modules でproto(修正案)に切替。"""
import sys, os, argparse
ap = argparse.ArgumentParser(); ap.add_argument("--modules"); a = ap.parse_args()
R = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, R)
if a.modules: sys.path.insert(0, os.path.abspath(a.modules))
os.chdir(R)
import er021_en_asr_semantic_equivalence_production_01 as t1
import er078_asr_value_guard_01 as vg
import er006_preprod_hardening_01_validation as val
# er003_v1_n3_01_tts_generate は本環境に無い依存(google.genai/pykakasi)をimportするため、純関数 tts_safe_number_words_en の定義部だけを
# ソースから取り出して実行する(同ファイルの _EN_NUMBER_WORDS .. tts_safe_number_words_en。改変なし。API呼出なし)。
_src = open(os.path.join(R, "er003_v1_n3_01_tts_generate.py"), encoding="utf-8").read()
_a = _src.index("_EN_NUMBER_WORDS = {"); _b = _src.index("def tts_safe_paragraphs_en")
_ns = {}; exec(_src[_a:_b], _ns); tts_safe_number_words_en = _ns["tts_safe_number_words_en"]
import judge_sim_01 as js
def atoms(s): return [(x['kind'], str(x.get('value', x.get('word'))), x.get('meridiem')) for x in t1._tier1_atoms(s)]
print("== A. 各層が同じ入力をどう表現するか(normalize_numeric / _tier1_atoms)")
for s in ["At ten thirty", "At 10 thirty", "At 10:30", "At 10 30", "At 1030", "At ten-thirty", "At one thirty", "At two thirty", "In twenty twenty", "In nineteen ninety"]:
    print(f"  {s!r:24} norm={val.normalize_numeric(s)!r:18} atoms={atoms(s)}")
print("== B. TTS入力の数字化(canonical_textの実形)")
for s in ["At ten thirty, a tall man", "At one thirty", "At twelve forty five", "At twenty twenty"]:
    print(f"  tts_safe_number_words_en({s!r}) = {tts_safe_number_words_en(s)!r}   (KP英語 tts_safe_kp_en は数字化しない=語形のまま)")
print("== C. value_guard(最終Gateの値判定)と正式経路の判定(Primary 1本、Secondary不可)")
for c, x in [("At ten thirty", "At 10:30"), ("At ten thirty", "At 1030"), ("At 10 thirty", "At 10:30"), ("At 10 thirty", "At ten thirty"), ("At 10 thirty", "At ten-thirty"), ("At 10 thirty", "At 1030"), ("At one thirty", "At 1:30"), ("At 10 thirty pm", "At 10:30 pm")]:
    r = vg.value_guard(c, x, "en"); st = js.judge_primary(c, x)
    print(f"  {c!r:20}||{x!r:16} vg={r.kind:8} judge={st[0]}/{st[1]}  {list(r.reasons)}")
