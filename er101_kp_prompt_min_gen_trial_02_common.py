# -*- coding: utf-8 -*-
"""FAMILY-X-KP-SELECTION-PROMPT-MIN-AND-GENERALIZATION-TRIAL-02 委任_01: Trial専用 共通部。
er098共通部(無改変)をimportし、出力先・台帳・モデル表のみ差し替える。Productionは一切import/変更しない。"""
import er098_kp_six_model_trial_01_common as C

OUT = C.ROOT / "er101_output" / "kp_prompt_min_gen_trial_02"
C.OUT = OUT
C.LEDGER = OUT / "paid_calls.jsonl"     # ledger_add/ledger_total_jpyはモジュール変数LEDGERを参照
MANIFEST_PREV = C.ROOT / "er098_output" / "kp_six_model_trial_01" / "inputs" / "manifest.json"

# Trial① 5モデル(KP6M m2=Solを除外。キー番号は委任文の表のNo.に合わせる)
MODELS = {
 "n1_gpt-6-luna":            dict(no=1, label="GPT-6 Luna", provider="openai", model_id="gpt-6-luna", prev_key="m1_gpt-6-luna"),
 "n2_gemini-3.1-flash-lite": dict(no=2, label="Gemini 3.1 Flash-Lite", provider="gemini", model_id="gemini-3.1-flash-lite", prev_key="m3_gemini-3.1-flash-lite"),
 "n3_gemini-3.5-flash-lite": dict(no=3, label="Gemini 3.5 Flash-Lite", provider="gemini", model_id="gemini-3.5-flash-lite", prev_key="m4_gemini-3.5-flash-lite"),
 "n4_claude-haiku-5-5":      dict(no=4, label="Claude Haiku 5.5", provider="anthropic", model_id="claude-haiku-5-5", prev_key="m5_claude-haiku-5-5"),
 "n5_claude-sonnet-5-5":     dict(no=5, label="Claude Sonnet 5.5", provider="anthropic", model_id="claude-sonnet-5-5", prev_key="m6_claude-sonnet-5-5"),
}
PRICES = C.PRICES
cost_usd = C.cost_usd

def stop_present(): return C.stop_present(OUT)
