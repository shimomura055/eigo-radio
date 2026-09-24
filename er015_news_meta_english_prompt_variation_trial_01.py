# ============================================================
# er015_news_meta_english_prompt_variation_trial_01.py
# NEWS-META-ENGLISH-PROMPT-VARIATION-TRIAL-01 (ユーザー指示、2026-09-24)
# ============================================================
# 目的: NEWS-META-SOURCE-VOLUME-FORMAT-TRIAL-01条件2素材(日本語2文・209字)
# を固定し、英語記事のEntertainment性低下が「英語Prompt/Revision表現」に
# 起因するかを切り分けるため、5 arm(A/B/C1/C2/C3)でCore Prompt/Revision
# 指示の英語表現だけを変えて比較するTrial。
#
#   Arm A : NEWS-META-ENGLISH-ONLY-TRIAL-01の既存artifactをそのまま再利用
#           (再callしない。コピーのみ)。
#   Arm B : P7日本語Promptを逐語使用し出力言語のみ英語指定(長さ行・出力行の
#           2行だけ置換)。
#   Arm C1: 日本語Promptの自然な英語意訳(新しいEditorial principleは追加
#           しない)。
#   Arm C2: 日本語Promptに元々含まれる思想を英語で強めに明示した版。
#   Arm C3: Conversation/Storytelling寄りに英語で強く出した版。
#
# 固定(Arm間で変えない): 同一素材(条件2)/Luna/effort high/Original->R1->R2/
# previous_response_id連鎖/Web Searchなし/Ledgerなし/Production contract
# (Point One/Point Two/`###`/`## In one line`/280-420語target)なし/Audio
# なし/Title+Body only/English output。R3は生成しない。
#
# Production実装ではない。Production code/SSOTは変更しない。
#
# 依存(いずれも無変更・import再利用のみ):
#   - er003_v1_en_direct_vfl_01_generate (vfl01): get_client
#   - er005_cost_logger (cl): usage log install
#   - er015_news_core_idea_editorial_trial_01 (er015base): response_meta,
#     _load_pricing, _price, USD_TO_JPY
#   - er015_news_iterative_entertainment_trial_02 (trial02): call_fresh,
#     call_with_previous_response_id(previous_response_id連鎖の実装、無変更)
#   - er015_news_original_baseline_repro_01 (repro01): WRITER_MODEL, WRITER_EFFORT
#
# Arm B/C1/C2/C3のCore Prompt・R1・R2はFable固定(delegation_log記載の逐語)。
# 本ファイルはそれを定数として保持するのみ。
#
# サブコマンド:
#   --arms B,C1,C2,C3 --stages 0,1,2 --out-dir <OUT> [--reuse-arm-a <ARM_A_DIR>]
#       : Arm Aは<ARM_A_DIR>からコピー(指定時)、B/C1/C2/C3はStage別生成
#         (冪等、--forceで再生成)
#   --assemble-only --out-dir <OUT>
#       : 生成済み5 armからtitles/metrics/fact_diff_machine/prompt_echo/
#         comparison_all.md/blind_r2.md/blind_key.json/cost.jsonを組み立て
# ============================================================
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import shutil

import er003_v1_en_direct_vfl_01_generate as vfl01
import er005_cost_logger as cl
import er015_news_core_idea_editorial_trial_01 as er015base
import er015_news_iterative_entertainment_trial_02 as trial02
import er015_news_original_baseline_repro_01 as repro01

THEME_TAG = "NEWS_META_ENGLISH_PROMPT_VARIATION_TRIAL_01"

WRITER_MODEL = repro01.WRITER_MODEL
WRITER_EFFORT = repro01.WRITER_EFFORT

ALL_ARMS = ["A", "B", "C1", "C2", "C3"]
NEW_CALL_ARMS = ["B", "C1", "C2", "C3"]  # Aは再利用のみ、再callしない

# ------------------------------------------------------------
# 入力素材(条件2、逐語。sha256で一致確認)
# ------------------------------------------------------------
COND2_SOURCE_PATH = os.path.join(
    "er015_output", "news_meta_source_volume_format_trial_01", "inputs", "cond2.md")
COND2_EXPECTED_SHA256 = (
    "4a2d9f899cc6083eb46cd006d8df1fdb02db10c23bdce020b7d6ee58bf903ecb")

MATERIAL_JA = (
    "Reuters(2026年9月22日、NEW YORK発)によると、Metaは個人向けAIエージェント"
    "「Muse」の電話代行機能について、一部の通話を人間の契約スタッフが裏で担当する"
    "「人間コンシェルジュ」の試験を社内で行っていたことが、Reutersが確認した社内投稿"
    "で判明した。従業員から通話内容の外部流出などプライバシー面の懸念が示され、"
    "Meta幹部はこの機能を一旦取りやめた(rolled back)と説明した。"
)

DEVELOPER_EN = (
    "You are a writer who explains the news clearly and makes it enjoyable to read.")
DEVELOPER_JA_P7 = "あなたは日本語のニュースを分かりやすく面白く伝える書き手です。"

# ------------------------------------------------------------
# Arm B: P7逐語(prompts.md)、長さ行・出力行の2行のみ置換(唯一の差異)
# ------------------------------------------------------------
ARM_B_USER = (
    "以下のニュースを、友人に「これ、ちょっと面白くない？」と話すような読み物にしてください。\n"
    "\n"
    "ニュースの中から、最も意外な事実ではなく、最も面白い「見方」を一つ選んでください。"
    "その見方に必要な事実だけを使い、ニュース全体を説明しようとしないでください。\n"
    "\n"
    "語り口は自然で軽快にします。新聞、行政資料、学校教材のような文章にはしません。"
    "難しい内容は、短く簡単な日本語に言い換えてください。日本語を勉強している外国人が、"
    "音声で一度聞いて理解できる程度を目安にします。\n"
    "\n"
    "遠い地域だけの特殊な話に見える場合は、読者の暮らしや、より大きな社会の変化との"
    "つながりを一度だけ示してください。ただし、話を無理に広げる必要はありません。\n"
    "\n"
    "事実関係は厳守し、架空の出来事や発言は加えません。\n"
    "\n"
    "テーマ：MetaのAI電話代行が、通話の一部を裏で人間スタッフに担当させる実験を行っている\n"
    "\n"
    "長さ：英語で350〜450語程度\n"
    "\n"
    "出力はタイトルと本文のみ。本文とタイトルは英語で書いてください。\n"
    "\n"
    "[ニュース]\n" + MATERIAL_JA
)
ARM_B_R1 = "この記事を、事実関係は変えずに、もっとエンターテインメント性の高い記事に修正してください。英語で出力してください。"
ARM_B_R2 = "この記事を、事実関係は変えずに、さらにもっとエンターテインメント性の高い記事に修正してください。英語で出力してください。"

THEME_EN = ("Theme: I asked an AI to call a store for me, and it turned out "
            "a human was secretly on the line.")

ARM_C1_USER = (
    "Write this news story the way you'd tell a friend: \"Hey, did you hear "
    "about this? It's kind of interesting.\"\n"
    "\n"
    "Don't go for the most surprising fact. Instead, pick the one angle that "
    "makes the story most interesting, and build the piece around it. Use only "
    "the facts that angle needs — don't try to cover the whole story.\n"
    "\n"
    "Keep the voice natural and light. It shouldn't read like a newspaper "
    "article, an official document, or a school textbook. Put difficult ideas "
    "into short, simple English, at a level an English learner could follow "
    "by listening just once.\n"
    "\n"
    "If the story looks like it only matters somewhere far away, connect it "
    "once to the reader's own life or to a bigger change in society — but "
    "don't stretch it.\n"
    "\n"
    "Stay strictly factual. Don't invent events or quotes.\n"
    "\n"
    f"{THEME_EN}\n"
    "\n"
    "Length: about 350–450 words.\n"
    "\n"
    "Give only the title and the body, in English.\n"
    "\n"
    "[News]\n" + MATERIAL_JA
)
ARM_C1_R1 = "Make this piece more entertaining, keeping every fact exactly the same."
ARM_C1_R2 = "Now make it even more entertaining, still keeping every fact exactly the same."

ARM_C2_USER = (
    "Turn the news below into a piece you'd share with a friend: \"Hey, isn't "
    "this kind of interesting?\"\n"
    "\n"
    "Do not try to explain the entire news story. Choose the single most "
    "interesting angle — not the most surprising fact — and build the whole "
    "piece around that one angle. Use only the facts needed for that angle "
    "and leave the rest out. Do not let the piece turn into an explanatory "
    "summary of the news.\n"
    "\n"
    "Keep the tone natural and light. Do not write like a newspaper, a "
    "government document, or a school textbook. Rephrase difficult content "
    "in short, simple English that a learner could understand by listening "
    "once.\n"
    "\n"
    "If the story seems specific to a distant place, connect it once to the "
    "reader's life or to a larger social change, without forcing it.\n"
    "\n"
    "Stick strictly to the facts. Add no fictional events or quotes.\n"
    "\n"
    f"{THEME_EN}\n"
    "\n"
    "Length: about 350–450 words.\n"
    "\n"
    "Output only the title and the body, in English.\n"
    "\n"
    "[News]\n" + MATERIAL_JA
)
ARM_C2_R1 = ("Revise this piece to be more entertaining, without changing the facts. "
             "Keep it built around the one angle; do not expand it into an "
             "explanatory summary.")
ARM_C2_R2 = ("Revise it again to be even more entertaining, without changing the "
             "facts. Stay on the one angle; still no explanatory summary.")

ARM_C3_USER = (
    "Tell this news the way you'd tell a friend over coffee: \"Hey, listen "
    "to this — it's kind of interesting.\"\n"
    "\n"
    "Find the one angle that makes it worth telling, and tell it as something "
    "that happened — concrete moments and scenes — rather than as a topic to "
    "be explained. Use only the facts that angle needs; don't cover the "
    "whole story.\n"
    "\n"
    "Talk, don't lecture. Keep it natural and light, never like a newspaper, "
    "an official document, or a textbook. Make the listener want to hear "
    "what happens next. Use short, simple English that a learner could "
    "follow by listening once.\n"
    "\n"
    "If it seems like a faraway story, connect it once to the listener's "
    "own life or to a bigger change — no need to force it.\n"
    "\n"
    "Everything must be true to the facts: no invented events, scenes, or "
    "quotes.\n"
    "\n"
    f"{THEME_EN}\n"
    "\n"
    "Length: about 350–450 words.\n"
    "\n"
    "Give only the title and the body, in English.\n"
    "\n"
    "[News]\n" + MATERIAL_JA
)
ARM_C3_R1 = "Tell it again, more entertainingly — same facts, nothing invented."
ARM_C3_R2 = "Once more, even more entertaining — same facts, nothing invented."

ARM_DEFS = {
    "B": {"developer": DEVELOPER_JA_P7, "user": ARM_B_USER, "r1": ARM_B_R1, "r2": ARM_B_R2},
    "C1": {"developer": DEVELOPER_EN, "user": ARM_C1_USER, "r1": ARM_C1_R1, "r2": ARM_C1_R2},
    "C2": {"developer": DEVELOPER_EN, "user": ARM_C2_USER, "r1": ARM_C2_R1, "r2": ARM_C2_R2},
    "C3": {"developer": DEVELOPER_EN, "user": ARM_C3_USER, "r1": ARM_C3_R1, "r2": ARM_C3_R2},
}

STAGE_KEY = {0: "original", 1: "r1", 2: "r2"}
STAGE_FILE = {0: "original.md", 1: "revision1.md", 2: "revision2.md"}

# Fact機械観測用: 条件2素材(日本語)の対訳語として事前承認済みの語
# (NEWS-META-ENGLISH-ONLY-TRIAL-01と同一リスト)。
ALLOWED_REFERENCE_TOKENS = {
    "Meta", "Muse", "Reuters", "Human", "Concierge", "Contract", "Staff",
    "Privacy", "Rolled", "Back", "New", "York", "September", "NEW", "YORK",
}

NUMBER_RE = re.compile(r"\d[\d,\.]*")
CAP_WORD_RE = re.compile(r"\b[A-Z][A-Za-z]*\b")
QUOTE_RE = re.compile(r'["“]([^"”]{1,200})["”]')

ECHO_PATTERNS = [
    "Isn't this",
    "kind of interesting",
    "Hey,",
    "listen to this",
    "Here's something interesting",
    "これ、ちょっと面白くない",
]


# ------------------------------------------------------------
# 共通ヘルパー
# ------------------------------------------------------------
def out_path(out_dir: str, *parts: str) -> str:
    return os.path.join(out_dir, *parts)


def arm_dir(out_dir: str, arm: str) -> str:
    return out_path(out_dir, "arms", arm)


def save_text(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def load_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def save_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, default=str)


def load_json(path: str):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def install_logger(out_dir: str) -> None:
    cl.install(out_path(out_dir, "raw_usage_log.jsonl"))


def _sha256_of_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def _check_material_sha256(out_dir: str) -> str:
    actual_sha256 = _sha256_of_file(COND2_SOURCE_PATH)
    if actual_sha256 != COND2_EXPECTED_SHA256:
        stop = {
            "stop_reason": "条件2素材を正確に再利用できない(sha256不一致)",
            "expected_sha256": COND2_EXPECTED_SHA256,
            "actual_sha256": actual_sha256,
            "source_path": COND2_SOURCE_PATH,
        }
        save_json(out_path(out_dir, "stop_reason.json"), stop)
        print(f"[STOP] sha256 mismatch: expected={COND2_EXPECTED_SHA256} actual={actual_sha256}")
        raise SystemExit(1)
    return actual_sha256


# ------------------------------------------------------------
# Arm A: 既存artifactのコピー(再callしない)
# ------------------------------------------------------------
def cmd_reuse_arm_a(out_dir: str, arm_a_src: str) -> None:
    dst = arm_dir(out_dir, "A")
    os.makedirs(dst, exist_ok=True)

    developer = load_text(os.path.join(arm_a_src, "prompt_developer.txt")).strip()
    user_prompt = load_text(os.path.join(arm_a_src, "prompt_user_stage0.txt"))
    save_text(out_path(dst, "prompt_core.txt"),
              "[developer]\n" + developer + "\n\n[user]\n" + user_prompt)

    for stage, api_prompt_key in ((1, "prompt_r1.txt"), (2, "prompt_r2.txt")):
        raw = load_text(os.path.join(arm_a_src, api_prompt_key))
        # 既存ファイルは "English (sent to API):\n<text>\n\nJapanese (reference..." 形式。
        # 実際にAPIへ送った英語部分のみを抽出する。
        m = re.search(r"English \(sent to API\):\n(.*?)\n\nJapanese",
                       raw, flags=re.DOTALL)
        sent_text = m.group(1).strip() if m else raw.strip()
        fname = "prompt_r1.txt" if stage == 1 else "prompt_r2.txt"
        save_text(out_path(dst, fname), sent_text)

    for src_name, dst_name in (
        ("en_original.md", "original.md"),
        ("en_revision1.md", "revision1.md"),
        ("en_revision2.md", "revision2.md"),
    ):
        shutil.copyfile(os.path.join(arm_a_src, src_name), out_path(dst, dst_name))

    for stage in (0, 1, 2):
        fname = f"api_meta_stage{stage}.json"
        shutil.copyfile(os.path.join(arm_a_src, fname), out_path(dst, fname))

    save_json(out_path(dst, "reuse_source.json"), {
        "reused_from": arm_a_src,
        "note": "Arm Aは再callしていない。既存artifactをそのままコピーした。",
    })
    print(f"[OK] Arm A reused from {arm_a_src} (no new API call)")


# ------------------------------------------------------------
# Arm B/C1/C2/C3: 生成
# ------------------------------------------------------------
def cmd_generate(out_dir: str, arms: list, stages: list, force: bool) -> None:
    os.makedirs(out_dir, exist_ok=True)
    _check_material_sha256(out_dir)
    install_logger(out_dir)
    client = vfl01.get_client()

    for arm in arms:
        if arm not in ARM_DEFS:
            print(f"[SKIP] unknown arm (not B/C1/C2/C3): {arm}")
            continue
        defn = ARM_DEFS[arm]
        dst = arm_dir(out_dir, arm)
        os.makedirs(dst, exist_ok=True)

        save_text(out_path(dst, "prompt_core.txt"),
                  "[developer]\n" + defn["developer"] + "\n\n[user]\n" + defn["user"])
        save_text(out_path(dst, "prompt_r1.txt"), defn["r1"])
        save_text(out_path(dst, "prompt_r2.txt"), defn["r2"])

        prev_id = None
        for stage in stages:
            stage_key = STAGE_KEY[stage]
            article_path = out_path(dst, STAGE_FILE[stage])
            meta_path = out_path(dst, f"api_meta_stage{stage}.json")
            if os.path.exists(article_path) and not force:
                print(f"[SKIP] existing: {article_path}")
                if os.path.exists(meta_path):
                    prev_id = load_json(meta_path).get("response_id", prev_id)
                continue
            call_label = f"variation_{arm}_{stage_key}"
            if stage == 0:
                response = trial02.call_fresh(
                    client, defn["developer"], defn["user"], WRITER_EFFORT, call_label)
                prompt_for_meta = defn["user"]
            else:
                instruction = defn[stage_key]
                response = trial02.call_with_previous_response_id(
                    client, instruction, WRITER_EFFORT, prev_id, call_label)
                prompt_for_meta = instruction
            text = response.output_text.strip()
            meta = er015base.response_meta(
                response, prompt_for_meta, defn["developer"],
                extra={"arm": arm, "stage": stage_key, "effort_requested": WRITER_EFFORT,
                       "chain_method": "fresh" if stage == 0 else "previous_response_id",
                       "previous_response_id": prev_id if stage != 0 else None},
            )
            save_text(article_path, text)
            save_json(meta_path, meta)
            prev_id = response.id
            print(f"[OK] arm={arm} stage{stage}({stage_key}): {len(text)}字/chars "
                  f"model={meta['response_model_actual']} id={response.id}")


# ------------------------------------------------------------
# assemble-only
# ------------------------------------------------------------
def _load_arm_stage_texts(out_dir: str, arm: str) -> dict:
    texts = {}
    d = arm_dir(out_dir, arm)
    for stage, fname in STAGE_FILE.items():
        p = out_path(d, fname)
        if os.path.exists(p):
            texts[STAGE_KEY[stage]] = load_text(p)
    return texts


def _first_line_title(text: str) -> str:
    for line in text.split("\n"):
        line = line.strip()
        if line:
            return line.lstrip("#").strip()
    return ""


def _word_count(text: str) -> int:
    return len(text.split())


def _fact_diff_for_stage(text: str) -> dict:
    numbers = sorted(set(NUMBER_RE.findall(text)))
    cap_words = sorted(set(CAP_WORD_RE.findall(text)))
    quotes = QUOTE_RE.findall(text)
    cap_words_not_reference = [w for w in cap_words if w not in ALLOWED_REFERENCE_TOKENS]
    return {
        "numbers": numbers,
        "capitalized_words": cap_words,
        "capitalized_words_not_in_reference_list": cap_words_not_reference,
        "quoted_spans": quotes,
    }


def _prompt_echo_for_stage(text: str) -> dict:
    hits = {}
    for pat in ECHO_PATTERNS:
        hits[pat] = bool(re.search(re.escape(pat), text, flags=re.IGNORECASE))
    return hits


def cmd_assemble(out_dir: str) -> None:
    arm_texts = {arm: _load_arm_stage_texts(out_dir, arm) for arm in ALL_ARMS}
    missing = [arm for arm, t in arm_texts.items() if not t]
    if missing:
        print(f"[STOP] missing arm outputs: {missing}; run generation/reuse first")
        raise SystemExit(1)

    titles = {arm: {stage: _first_line_title(text) for stage, text in texts.items()}
              for arm, texts in arm_texts.items()}
    save_json(out_path(out_dir, "titles.json"), titles)

    metrics = {arm: {stage: {"char_count": len(text), "word_count": _word_count(text),
                              "paragraph_count": len([p for p in text.split("\n\n") if p.strip()])}
                      for stage, text in texts.items()}
               for arm, texts in arm_texts.items()}
    save_json(out_path(out_dir, "metrics.json"), metrics)

    fact_diff = {arm: {stage: _fact_diff_for_stage(text) for stage, text in texts.items()}
                 for arm, texts in arm_texts.items()}
    save_json(out_path(out_dir, "fact_diff_machine.json"), fact_diff)

    prompt_echo = {arm: {stage: _prompt_echo_for_stage(text) for stage, text in texts.items()}
                   for arm, texts in arm_texts.items()}
    save_json(out_path(out_dir, "prompt_echo.json"), prompt_echo)

    # comparison_all.md(生成完了後にのみ、日本語条件2R2を参照)
    ja_r2_path = os.path.join(
        "er015_output", "news_meta_source_volume_format_trial_01", "cond2_revision2.md")
    ja_r2 = load_text(ja_r2_path) if os.path.exists(ja_r2_path) else "(ファイルなし)"

    lines = ["# comparison_all.md (NEWS-META-ENGLISH-PROMPT-VARIATION-TRIAL-01)", "",
             "## 日本語Baseline(NEWS-META-SOURCE-VOLUME-FORMAT-TRIAL-01 条件2 R2)", "",
             ja_r2, "", "---", ""]
    for arm in ALL_ARMS:
        texts = arm_texts[arm]
        t = titles[arm]
        lines += [f"## Arm {arm}", "",
                  f"### Title: Original={t.get('original','')} / "
                  f"R1={t.get('r1','')} / R2={t.get('r2','')}", "",
                  f"#### Original", "", texts.get("original", "(未生成)"), "",
                  f"#### R1", "", texts.get("r1", "(未生成)"), "",
                  f"#### R2", "", texts.get("r2", "(未生成)"), "", "---", ""]
    save_text(out_path(out_dir, "comparison_all.md"), "\n".join(lines))

    # blind_r2.md / blind_key.json(5 armのR2をランダム記号P/Q/R/S/Tで提示)
    symbols = ["P", "Q", "R", "S", "T"]
    arms_shuffled = list(ALL_ARMS)
    random.shuffle(arms_shuffled)
    mapping = dict(zip(symbols, arms_shuffled))  # symbol -> arm
    reverse_mapping = {arm: sym for sym, arm in mapping.items()}
    save_json(out_path(out_dir, "blind_key.json"), {
        "symbol_to_arm": mapping,
        "arm_to_symbol": reverse_mapping,
        "note": "Fableはblind_r2.mdを先に読み、このファイルは参考評価の後に開く想定。",
    })
    blind_lines = ["# blind_r2.md (NEWS-META-ENGLISH-PROMPT-VARIATION-TRIAL-01)", "",
                   "5つのR2記事をランダムな記号で提示する(arm名・Promptは書かない)。", ""]
    for sym in symbols:
        arm = mapping[sym]
        text = arm_texts[arm].get("r2", "(未生成)")
        blind_lines += [f"## {sym}", "", text, "", "---", ""]
    save_text(out_path(out_dir, "blind_r2.md"), "\n".join(blind_lines))

    # cost.json(新規9 call = B/C1/C2/C3 x 3 stage。Arm Aは再利用のため0円)
    log_path = out_path(out_dir, "raw_usage_log.jsonl")
    pricing = er015base._load_pricing()
    luna_in = er015base._price(pricing, "openai", "gpt-5.6-luna", "input_tokens")
    luna_cached = er015base._price(pricing, "openai", "gpt-5.6-luna", "cached_input_tokens")
    luna_out = er015base._price(pricing, "openai", "gpt-5.6-luna", "output_tokens")

    entries = []
    if os.path.exists(log_path):
        with open(log_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    entries.append(json.loads(line))
    # trial02.call_fresh/call_with_previous_response_idはtrial02自身の
    # THEME_TAGをcl.logging_contextへ渡すため、9 callはそのthemeで記録される
    # (NEWS-META-ENGLISH-ONLY-TRIAL-01と同一の既知挙動)。
    entries = [e for e in entries if e.get("theme") == trial02.THEME_TAG]

    per_call = []
    total_usd = 0.0
    total_input = total_output = total_cached = 0
    for e in entries:
        it = e.get("input_tokens") or 0
        ct = e.get("cached_input_tokens") or 0
        ot = e.get("output_tokens") or 0
        billable_in = max(it - ct, 0)
        usd = 0.0
        if luna_in is not None:
            usd += (billable_in / 1_000_000) * luna_in
        if luna_cached is not None:
            usd += (ct / 1_000_000) * luna_cached
        if luna_out is not None:
            usd += (ot / 1_000_000) * luna_out
        per_call.append({
            "stage": e.get("stage"), "input_tokens": it, "cached_input_tokens": ct,
            "output_tokens": ot, "elapsed_seconds": e.get("elapsed_seconds"),
            "usd": round(usd, 6),
        })
        total_usd += usd
        total_input += it
        total_output += ot
        total_cached += ct

    arm_a_reused_cost_jpy = None
    arm_a_reused_cost_path = os.path.join(
        "er015_output", "news_meta_english_only_trial_01", "cost.json")
    if os.path.exists(arm_a_reused_cost_path):
        arm_a_reused_cost_jpy = load_json(arm_a_reused_cost_path).get("total_jpy")

    result = {
        "theme": THEME_TAG,
        "new_calls": len(entries),
        "per_call": per_call,
        "total_input_tokens": total_input,
        "total_cached_input_tokens": total_cached,
        "total_output_tokens": total_output,
        "total_usd_new_calls": round(total_usd, 4),
        "total_jpy_new_calls": round(total_usd * er015base.USD_TO_JPY, 2),
        "arm_a_reused_no_new_call": True,
        "arm_a_prior_cost_jpy_reference_only": arm_a_reused_cost_jpy,
        "usd_to_jpy": er015base.USD_TO_JPY,
        "budget_jpy": 10,
        "within_budget": round(total_usd * er015base.USD_TO_JPY, 2) <= 10,
    }
    save_json(out_path(out_dir, "cost.json"), result)

    print(f"[OK] assemble complete: titles/metrics/fact_diff_machine/prompt_echo/"
          f"comparison_all.md/blind_r2.md/blind_key.json/cost.json written. "
          f"new_calls={result['new_calls']} total_jpy_new_calls={result['total_jpy_new_calls']} "
          f"within_budget={result['within_budget']}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--arms", default=None,
                         help="comma-separated arm labels among B,C1,C2,C3 (A is reuse-only)")
    parser.add_argument("--stages", default=None,
                         help="comma-separated stage numbers, e.g. 0,1,2")
    parser.add_argument("--reuse-arm-a", default=None,
                         help="path to NEWS-META-ENGLISH-ONLY-TRIAL-01 output dir to copy as Arm A")
    parser.add_argument("--assemble-only", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if args.assemble_only:
        cmd_assemble(args.out_dir)
        return

    os.makedirs(args.out_dir, exist_ok=True)
    if args.reuse_arm_a:
        _check_material_sha256(args.out_dir)
        cmd_reuse_arm_a(args.out_dir, args.reuse_arm_a)

    if args.arms:
        if not args.stages:
            parser.error("--stages is required when --arms is given")
        arms = [a.strip() for a in args.arms.split(",") if a.strip()]
        stages = [int(s) for s in args.stages.split(",")]
        cmd_generate(args.out_dir, arms, stages, args.force)


if __name__ == "__main__":
    main()
