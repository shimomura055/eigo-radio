# ============================================================
# er012_editorial_b_voices_trial_10_comment1.py
# EDITORIAL-B-FAMILY-VOICES-COMMENT1-CONTRACT-FIX-TRIAL-10
# ============================================================
# Lane: Lane B / Voices-Perspective。種別: Comment 1 Contract最小修正Trial
# (2026-09-08、ユーザー決定反映)。
#
# 背景: ユーザーがTrial-09完成episodeを試聴し、Voices Comment Contractの
# Comment 2〜4は問題なしと判断。Comment 1のみ、「MC補足なのか本文なのか
# 曖昧」という指摘を受けた(実際の生成結果: "Even a familiar workplace can
# feel very different from one person to another." がThe Question本文の
# 主張を語ってしまっている)。修正方針(ユーザー指定): News/Discovery型
# Comment 1(er003_v1_b1_scaffold_01_generate.COMMENT_1_ROLE、役割=
# Listening Focus、"リスナーが次に何を聞けばよいか、注目点を示す")と同様に、
# 本文を語らずリスナーの聞き方を案内する役割へ寄せる。
#
# 設計方針(重要): 本ファイルはTrial-09の記事・本文(article.md/parts.json)
# をそのまま読み取り専用で再利用し、Comment 1だけを新Contractで再生成する。
# Trial-09のスクリプト(er012_editorial_b_voices_trial_09_audio.py)・出力
# ディレクトリ(er012_output/editorial_b_voices_trial_09_audio/)は一切変更
# しない(importして関数・定数を読むだけ)。Writer呼び出しは既存Production
# primitive (er003_v1_b1_scaffold_01_generate.run_support_text、Trial-09で
# 使ったものと同一関数)をそのまま使う。TTS呼び出しも既存Production
# primitive (er003_v1_sing01_voice01_generate.generate_charon_english、
# Trial-09のcomment_1-4生成と同一関数・同一style_prefix)をそのまま使う。
#
# 触れないもの: docs/pm/PM_GOVERNANCE.md、player生成コード、
# er012_output/editorial_b_voices_trial_09_audio/配下、er011_output/配下、
# CURRENT_SPEC.md/DECISION_LOG.md/OPEN_ITEMS.md。
# 書き込み: 本ファイル(root)、er012_output/editorial_b_voices_trial_10_
# comment1/ 配下のみ。Git操作はこのタスクでは行わない。
#
# cost > 100円でSTOP(委任範囲: Comment 1再生成1件 + TTS 1 segment)。
from __future__ import annotations

import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

# PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-01: 正式リリース前はStandard同期を使う。
os.environ["TTS_EXECUTION_MODE"] = "STANDARD"

import er003_v1_b1_scaffold_01_generate as b1s
import er003_v1_n3_01_tts_generate as tts_gen
import er003_v1_sing01_voice01_generate as voice01
import er005_cost_logger as cl
import er006_model_routing_contract_01 as routing
import er012_editorial_b_voices_trial_09_audio as t9  # 読み取り専用(article/sections/定数の再利用のみ)

TRIAL07_ARTICLE_PATH = t9.TRIAL07_ARTICLE_PATH  # Trial-09と同一記事(再生成しない)

OUT_DIR = "er012_output/editorial_b_voices_trial_10_comment1"
COST_LOG_PATH = f"{OUT_DIR}/audit/raw_usage_log.jsonl"
PRICING_SNAPSHOT_PATH = "er005_output/cost_baseline_01/pricing_snapshot.json"
USD_JPY = 160.0
BUDGET_JPY_CAP = 100.0


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, default=str)


# ============================================================
# コスト計測(Trial-09と同一ロジック、Trial-10専用ログへ適用、上限¥100)
# ============================================================
def _load_pricing():
    prices = load_json(PRICING_SNAPSHOT_PATH)["prices"]

    def price(provider, model, meter):
        return next(p["price"] for p in prices
                    if p["provider"] == provider and p["model"] == model and p["meter"] == meter
                    and p.get("tier", "Standard") == "Standard")
    return price


def compute_cost_jpy_so_far() -> tuple:
    if not os.path.exists(COST_LOG_PATH):
        return 0.0, {}
    price = _load_pricing()
    total_usd = 0.0
    by_provider = {}
    with open(COST_LOG_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            provider = rec.get("provider")
            model = rec.get("model_id") or rec.get("model")
            usd = 0.0
            try:
                if provider in ("gemini", "openai", "openai_asr") and model:
                    in_tok = rec.get("input_tokens") or 0
                    out_tok = rec.get("output_tokens") or 0
                    usd = in_tok * price(provider, model, "input_tokens") / 1e6 \
                        + out_tok * price(provider, model, "output_tokens") / 1e6
            except StopIteration:
                usd = 0.0
            total_usd += usd
            by_provider[provider] = by_provider.get(provider, 0.0) + usd
    jpy = total_usd * USD_JPY
    return jpy, {k: round(v * USD_JPY, 2) for k, v in by_provider.items()}


def assert_budget_ok(note: str = "") -> float:
    jpy, by_provider = compute_cost_jpy_so_far()
    print(f"[TRIAL10-COMMENT1][cost] so far={jpy:.2f} JPY by_provider={by_provider} ({note})")
    if jpy > BUDGET_JPY_CAP:
        raise RuntimeError(f"[BUDGET_GUARD] cost so far {jpy:.2f} JPY > cap {BUDGET_JPY_CAP} JPY. Stopping ({note}).")
    return jpy


# ============================================================
# Comment 1 Contract 最小修正版(旧: t9.VOICES_COMMENT_1_ROLE)
# ============================================================
# 修正差分の要旨(詳細diffはREPORT参照):
#   - 役割名を「テーマ・場面への自然な導入」から News/Discovery型と同じ
#     「Listening Focus」へ変更。
#   - 「これから始まるテーマ・場面へ、リスナーの意識を自然に向けます」という
#     曖昧な役割記述を、「これから聞くThe Questionに対して、何に注目して
#     聞けばよいかを明確に案内する(例: "Listen for ..."/"As you listen,
#     notice ..."のような、聞き方を指示する話法)」という明示的なNavigate
#     指示へ変更。
#   - 禁止事項に「テーマ・場面についての一般的な説明・主張文(聞き方の案内
#     ではなく、内容そのものを語ってしまう文)」を追加(今回の問題事例
#     "Even a familiar workplace can feel very different from one person to
#     another."のような、The Questionの結論めいた主張文を明示的に禁止)。
#   - Comment 2〜4(VOICES_COMMENT_2_ROLE/3/4)は無変更、Reference Exampleの
#     「要約しない・答えを先取りしない・どちらが正しいか評価しない」という
#     既存の禁止方向性(t9.VOICES_COMMENT_1_ROLEの「The Questionで語られる
#     具体的な状況・問いの先取り」等の既存禁止事項)はそのまま維持する。
VOICES_COMMENT_1_ROLE_TRIAL10 = """あなたはPodcastのナビゲーターです。これから、あるテーマ・場面を短く
提示する「The Question」(冒頭の問いかけ本文)をリスナーが聞きます。その直前に流す、
Comment 1(役割: Listening Focus)を書いてください。

役割: リスナーがこれから聞くThe Questionに対して、何に注目して聞けばよいかを
明確に案内します(例: "Listen for ..."/"As you listen, notice ..."のような、
聞き方を指示する話法)。テーマ・場面についての一般的な説明文や、内容についての
主張・結論めいた文を語ってはいけません(悪い例:「〜は人によって違って感じられる」
のような、The Questionの内容そのものを述べる文)。

以下は避けてください:
- The Questionで語られる具体的な状況・問いの先取り(内容の先出し)
- "First point"/"Second point"のようなPoint要約めいた話法
- 事実を解説するような硬い、Discovery的な説明口調
- テーマ・場面についての一般的な説明・主張文(聞き方の案内ではなく、内容そのものを
  語ってしまう文)

1文程度の、非常に短いListening Focusにしてください。

【重要・出力への制約】出力する文章自体に"Part 1"・"Part 2"・"Hook"・"The Question"
のような制作内部の構造ラベルを含めないでください。リスナーは番組の内部構成を
意識しません。"""


def run_comment1_regen() -> dict:
    with open(TRIAL07_ARTICLE_PATH, encoding="utf-8") as f:
        article_text = f.read()
    sections = t9.split_five_voice_sections(article_text)
    if sections is None:
        raise RuntimeError("5区切り構造の検出に失敗しました(Trial-09と同じ記事のはずが解析できません)")

    old_text = load_json(f"{t9.OUT_B1_DIR}/b1_support_texts.json")["comment_1"]

    client = b1s.get_client()
    model = routing.require_model("B1_SUPPORT", routing.SUPPORT_MODEL)

    print("[TRIAL10-COMMENT1] Comment 1(修正Contract)再生成開始...")
    c1_context = f"【これから聞く本文(The Question)】\n{sections['hook_body']}"
    c1 = b1s.run_support_text(client, VOICES_COMMENT_1_ROLE_TRIAL10, c1_context, model=model)

    result = {
        "old_text_trial09": old_text,
        "new_generation": c1,
        "new_text": c1.get("text"),
        "context": c1_context,
        "role_prompt": VOICES_COMMENT_1_ROLE_TRIAL10,
        "model": model,
    }
    save_json(f"{OUT_DIR}/audit/comment1_regeneration.json", result)
    assert_budget_ok("after Comment 1 scaffold regen")
    return result


def run_comment1_tts(new_text: str) -> dict:
    narration_dir = f"{OUT_DIR}/narration"
    os.makedirs(narration_dir, exist_ok=True)
    out_path = f"{narration_dir}/comment_1.wav"
    print("[TRIAL10-COMMENT1] Comment 1 TTS(Charon、Trial-09と同一Production primitive)...")
    with cl.segment_context("comment_1_trial10"):
        r = voice01.generate_charon_english(
            tts_gen.tts_safe_number_words_en(tts_gen.tts_safe_en(new_text)), out_path,
            style_prefix_override=tts_gen.B1_PREVIEW_STYLE_PREFIX_CALM, disfluency_qa=True)
    r["canonical_text"] = new_text
    save_json(f"{OUT_DIR}/audit/comment1_tts_result.json", r)
    assert_budget_ok("after Comment 1 TTS")
    print(f"[TRIAL10-COMMENT1] TTS status={r.get('status')} asr_verified={r.get('asr_verified')} "
          f"asr_text={r.get('asr_text')!r}")
    return r


def main() -> None:
    os.makedirs(f"{OUT_DIR}/audit", exist_ok=True)
    cl.install(COST_LOG_PATH)

    scaffold_result = run_comment1_regen()
    new_text = scaffold_result["new_text"]
    if not new_text:
        print(f"[TRIAL10-COMMENT1] Comment 1生成に失敗しました。TTSは実行しません。"
              f"scaffold_result={scaffold_result['new_generation']}")
        jpy, by_provider = compute_cost_jpy_so_far()
        print(f"[TRIAL10-COMMENT1] 完了(TTS未実行)。累積cost={jpy:.2f} JPY by_provider={by_provider}")
        return

    tts_result = run_comment1_tts(new_text)

    save_json(f"{OUT_DIR}/audit/run_summary.json", {
        "old_text_trial09": scaffold_result["old_text_trial09"],
        "new_text": new_text,
        "tts_status": tts_result.get("status"),
        "asr_verified": tts_result.get("asr_verified"),
        "asr_text": tts_result.get("asr_text"),
    })

    jpy, by_provider = compute_cost_jpy_so_far()
    print(f"[TRIAL10-COMMENT1] 完了。累積cost={jpy:.2f} JPY by_provider={by_provider}")


if __name__ == "__main__":
    main()
