# ============================================================
# er002_common.py
# ER-002: 共通実験基盤(記事横断で共有するロジック)
# ============================================================
# ER-001B-9/10で確立された1人語り仕様(Emotional+Connected+Level2 /
# Point One・Point Two / In One Line必須 / セクション間0.8秒無音 /
# 全文結合後にDynamics3を一度だけ適用)を、記事ごとにスクリプトを
# コピーせず共通利用するためのモジュール。
#
# このモジュールはTTS/QA APIを直接呼び出さない。呼び出しは引数として
# 注入されたコーラブル(tts_call_fn / qa_call_fn)を通して行われるため、
# テスト時はモックを渡すだけで実APIを一切呼ばずに検証できる。
# (ER-002-S1では実APIを呼ぶ実装・実行のいずれも行っていない)
#
# ER-001Bとの既知の差分(ER-002-S0で発見):
#   POINT_LABEL_FIDELITY_RULEに老老介護由来の"care point"という表現が
#   残っており、阪神記事のスクリプト(er001b10)にもそのままコピーされて
#   いた。このモジュールではER-001B-7B時点の記事非依存の文言
#   ("point"のみ)へ戻す形で修正する。ER-001Bの既存ファイル
#   (er001b9_caregiving_common_spec.py / er001b10_hanshin_common_spec.py等)
#   は遡って変更していない。
#
# 台本スキーマは既存のer001b5_*_script.jsonと同一
#   {"title": str, "sections": [
#       {"type": "body", "paragraphs": [str, ...]},
#       {"type": "section", "heading": str, "subsections": [
#           {"heading": str, "paragraphs": [str, ...]},
#           {"heading": str, "paragraphs": [str, ...]},
#       ]},
#       {"type": "section", "heading": "In One Line", "paragraphs": [str, ...]},
#   ]}
# を前提とする。"Today's ... Points"の見出し文字列そのものは記事ごとに
# 異なってよい(ハードコードしない)。subsectionsは正確に2件を必須とする。

from __future__ import annotations

import hashlib
import io
import json
import re
import wave
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

import numpy as np
from scipy.signal import lfilter

# ============================================================
# ブロック1: 確定パラメータ(ER-001B-9/10・ER-002-S0の凍結仕様から変更しない)
# ============================================================
MODEL_NAME = "gemini-2.5-pro-preview-tts"
QA_MODEL_NAME = "gemini-3-flash-preview"
LANGUAGE_CODE = "en-us"
SAMPLE_RATE = 24000

SECTION_JOIN_PAUSE_SECONDS = 0.8
EXPECTED_CHUNK_COUNT = 3
EXPECTED_SECTION_JOIN_COUNT = 2  # 3チャンク構成 → 無音は2箇所のみ(全見出し間ではない)

WORD_COUNT_TARGET_MIN = 380
WORD_COUNT_TARGET_MAX = 420
WORD_COUNT_ACCEPT_MIN = 320
WORD_COUNT_ACCEPT_MAX = 480

DURATION_WARN_MIN_SECONDS = 130
DURATION_WARN_MAX_SECONDS = 200

MAX_SCRIPT_ATTEMPTS = 2        # 初回 + 全文再生成1回
MAX_TTS_CONTENT_ATTEMPTS = 3   # 1話者につき最大3コンテンツ試行
MAX_TTS_API_RETRY = 2          # TTS呼び出し自体の障害時リトライ(ER-001B-6系と同一)
MAX_QA_API_RETRY = 5           # QA呼び出し自体の障害時リトライ(ER-001B-9/10と同一)
QA_API_RETRY_SLEEP_SECONDS = 8
TTS_API_RETRY_SLEEP_SECONDS = 2

DYNAMICS3_PARAMS = {
    "type": "soft_knee_compressor",
    "threshold_percentile": 60,
    "ratio": 8.0,
    "knee_db": 6.0,
    "attack_ms": 5.0,
    "release_ms": 200.0,
    "gain_smoothing_ms": 8.0,
}
PEAK_CEILING_DB = -1.0
LOUDNESS_MATCH_TARGET_LU = 0.3

REQUIRED_FINAL_HEADING = "In One Line"

# ============================================================
# ブロック2: 共通演技指示(記事非依存)
# ============================================================
COMMON_BASE_INSTRUCTION = """TTS the following complete story in natural, engaging English.

Speak directly to one interested listener rather than announcing to a large crowd.

Create a natural emotional arc that follows the meaning already present in the script. Let the energy, weight, and pace rise or fall when the story itself changes. Do not add excitement, sadness, urgency, or drama that is not supported by the words.

Carry the meaning naturally across sentence boundaries. Do not reset your pitch, energy, or rhythm after every sentence. Group related sentences into complete thoughts, while keeping important contrasts and turning points clear.

Treat the narration as one continuous program, even when it is generated in separate sections.

Read every title, section heading, and subsection heading exactly as written. Never skip, paraphrase, shorten, or silently absorb a heading into the following text.

Clearly say "In One Line" before reading the final section.

Do not shout, sound like a movie trailer, become gloomy or sleepy, or use a distant and overly formal newsreader style.

"""

LEVEL2_INSTRUCTION = """Give the narration a noticeably animated, emotionally present, and expressive delivery.

Use a clearly wider vocal range, stronger emphasis on important words and turning points, and more distinct rises and falls in energy.

Make the listener feel that the story matters and that you genuinely want them to keep listening.

Keep the narration moving with confident momentum, including during explanatory passages. Avoid becoming passive, flat, or overly restrained.

Allow the most important moments, contrasts, and conclusions to land with clear emotional impact.

Use stronger expression than Level 1, but vary the intensity across the story. Do not stay at maximum intensity throughout.

Do not shout, force emotion, exaggerate feelings that are not present in the script, or sound like a sports commentator or movie trailer.

"""

# ER-002-S1で採用する修正版(ER-001B-7B時点の記事非依存の文言に統一)。
# er001b9/er001b10にあった "before the first care point and ... second
# care point" という老老介護由来の表現は使わない。
POINT_LABEL_FIDELITY_RULE = """Read every title, section heading, point label, and subsection heading exactly as written.
Clearly say "Point One" before the first point and "Point Two" before the second point.
Clearly say "In One Line" before the final section.
Do not skip, repeat, paraphrase, shorten, or merge any title, heading, point label, or subsection heading with the following text.

"""

WPM_PATTERN = re.compile(r"\d+\s*[-–]?\s*\d*\s*words per minute|\bwpm\b", re.IGNORECASE)

# ER-002-S0で実際に発見された混入語("care point")と、想定される再発
# パターン(記事固有の固有名詞・チーム名・ジャンル名)を共通指示から締め
# 出すためのdenylist。記事を追加するたびに書き足す運用は想定しておらず、
# 「共通指示そのものに記事語を書かない」ことが本来のルール。このリストは
# 過去に混入した実例に対する回帰防止用。
KNOWN_GENRE_LEAKAGE_TERMS = [
    "care point",
    "care points",
    "tiger",
    "tigers",
    "hanshin",
    "kesamaru",
    "caregiv",  # caregiving / caregiver 等の語幹
    "aoede",
    "charon",
]


def find_genre_leakage(text: str, extra_terms: Optional[list[str]] = None) -> list[str]:
    """共通指示テキストに記事固有語が含まれていないかを調べる(検出のみ、例外は出さない)。"""
    terms = list(KNOWN_GENRE_LEAKAGE_TERMS) + list(extra_terms or [])
    lowered = text.lower()
    return sorted({t for t in terms if t.lower() in lowered})


def assert_no_wpm_specification(text: str) -> None:
    assert not WPM_PATTERN.search(text), "演技指示に話速の数値指定が含まれています"


def assert_no_genre_leakage(text: str, extra_terms: Optional[list[str]] = None) -> None:
    found = find_genre_leakage(text, extra_terms)
    assert not found, f"共通演技指示に記事固有語が含まれています: {found}"


def build_style_prefix() -> str:
    prefix = COMMON_BASE_INSTRUCTION + LEVEL2_INSTRUCTION + POINT_LABEL_FIDELITY_RULE
    assert_no_wpm_specification(prefix)
    assert_no_genre_leakage(prefix)
    return prefix


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ============================================================
# ブロック3: 台本構造検証(確定8項目構成、subsections=2件の強制)
# ============================================================
@dataclass
class StructureValidationResult:
    valid: bool
    errors: list = field(default_factory=list)
    body_section: Optional[dict] = None
    points_section: Optional[dict] = None
    final_section: Optional[dict] = None
    subsections: list = field(default_factory=list)


def validate_script_structure(script: dict) -> StructureValidationResult:
    """確定構造(body → Today's...Points[2 subsections] → In One Line)を検証する。
    subsectionsが1件・3件以上の場合は明示的に構造検品不合格にする(可変数への対応は非対象)。
    """
    errors: list[str] = []
    sections = script.get("sections", [])

    body_sections = [s for s in sections if s.get("type") == "body"]
    if len(body_sections) != 1:
        errors.append(f"bodyセクションは1件である必要があります(実際: {len(body_sections)}件)")

    points_sections = [s for s in sections if s.get("type") == "section" and "subsections" in s]
    if len(points_sections) != 1:
        errors.append(
            f"subsectionsを持つセクション(Today's ... Points相当)は1件である必要があります"
            f"(実際: {len(points_sections)}件)"
        )

    final_sections = [
        s for s in sections if s.get("type") == "section" and s.get("heading") == REQUIRED_FINAL_HEADING
    ]
    if len(final_sections) != 1:
        errors.append(f"'{REQUIRED_FINAL_HEADING}'セクションは1件である必要があります(実際: {len(final_sections)}件)")

    subsections: list = []
    if len(points_sections) == 1:
        subsections = points_sections[0].get("subsections", [])
        if len(subsections) != 2:
            errors.append(
                f"subsectionは正確に2件である必要があります(実際: {len(subsections)}件)。"
                f"1件または3件以上は構造検品不合格です(可変数への対応は非対象)。"
            )
        elif subsections[0].get("heading") == subsections[1].get("heading") and \
                subsections[0].get("paragraphs") == subsections[1].get("paragraphs"):
            errors.append(
                "Point OneとPoint Twoの内容が完全に重複しています(小見出し・本文が同一)"
            )

    if not errors:
        expected_order_objs = [body_sections[0], points_sections[0], final_sections[0]]
        indices = [sections.index(o) for o in expected_order_objs]
        if indices != sorted(indices):
            errors.append("セクションの並び順がbody→Today's...Points→In One Lineの順になっていません")
        if len(sections) != 3:
            errors.append(
                f"確定構造では合計3セクション(body/Today's...Points/In One Line)を想定していますが、"
                f"実際は{len(sections)}件です"
            )

    return StructureValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        body_section=body_sections[0] if body_sections else None,
        points_section=points_sections[0] if len(points_sections) == 1 else None,
        final_section=final_sections[0] if final_sections else None,
        subsections=subsections,
    )


class ScriptStructureError(Exception):
    def __init__(self, errors: list[str]):
        super().__init__("; ".join(errors))
        self.errors = errors


# ============================================================
# ブロック4: チャンク構築(ER-001B-9/10と同じ3チャンク・結合方法)
# ============================================================
@dataclass
class NarrationPlan:
    chunks: list  # [(label, text), ...] 3件
    full_text: str
    required_headings_in_order: list
    title: str
    points_heading: str
    sub1_heading: str
    sub2_heading: str
    final_heading: str


def build_narration_plan(script: dict) -> NarrationPlan:
    result = validate_script_structure(script)
    if not result.valid:
        raise ScriptStructureError(result.errors)

    title = script["title"]
    body = result.body_section
    points = result.points_section
    sub1, sub2 = result.subsections
    final = result.final_section

    chunk1_text = "\n\n".join([title] + body["paragraphs"])
    chunk2_lines = (
        [points["heading"], "Point One", sub1["heading"]] + sub1["paragraphs"]
        + ["Point Two", sub2["heading"]] + sub2["paragraphs"]
    )
    chunk2_text = "\n\n".join(chunk2_lines)
    chunk3_text = "\n\n".join([final["heading"]] + final["paragraphs"])

    chunks = [("body", chunk1_text), (points["heading"], chunk2_text), (final["heading"], chunk3_text)]
    full_text = "\n\n".join([chunk1_text, chunk2_text, chunk3_text])

    required_headings = [
        title, points["heading"], "Point One", sub1["heading"], "Point Two", sub2["heading"], final["heading"],
    ]

    return NarrationPlan(
        chunks=chunks,
        full_text=full_text,
        required_headings_in_order=required_headings,
        title=title,
        points_heading=points["heading"],
        sub1_heading=sub1["heading"],
        sub2_heading=sub2["heading"],
        final_heading=final["heading"],
    )


def build_expected_elements(plan: NarrationPlan) -> list[tuple[str, str]]:
    """個別カウント判定の対象となる7要素(見出し・ラベル系)。"""
    return [
        ("title", plan.title),
        ("today_points_heading", plan.points_heading),
        ("point_one", "Point One"),
        ("subheading1", plan.sub1_heading),
        ("point_two", "Point Two"),
        ("subheading2", plan.sub2_heading),
        ("in_one_line", plan.final_heading),
    ]


# ============================================================
# ブロック5: 音声結合(セクション間0.8秒無音、ER-001B-9/10と同一方式)
# ============================================================
def assemble_audio(pcm_chunks: list[bytes], sample_rate: int = SAMPLE_RATE,
                    pause_seconds: float = SECTION_JOIN_PAUSE_SECONDS) -> tuple[bytes, list[int]]:
    """2件目以降のチャンクの前にのみ無音を挿入する(全見出し間ではない)。
    戻り値は (結合後PCM, 無音を挿入したバイトオフセットのリスト)。"""
    pause = b"\x00\x00" * int(sample_rate * pause_seconds)
    audio = b""
    pause_positions = []
    for i, pcm in enumerate(pcm_chunks):
        if i > 0:
            pause_positions.append(len(audio))
            audio += pause
        audio += pcm
    return audio, pause_positions


def pcm_to_wav_bytes(pcm_bytes: bytes, sample_rate: int = SAMPLE_RATE) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        w.writeframes(pcm_bytes)
    return buf.getvalue()


def pcm_bytes_to_float_mono(pcm_bytes: bytes) -> "np.ndarray":
    """16bit PCMモノラルの生バイト列を-1.0〜1.0のfloat配列へ変換する
    (ファイルへ書き出さずにDynamics3処理へ渡すためのヘルパー)。"""
    return np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float64) / 32768.0


def read_wav_float(path: str):
    with wave.open(path, "rb") as w:
        channels = w.getnchannels()
        sampwidth = w.getsampwidth()
        framerate = w.getframerate()
        nframes = w.getnframes()
        raw = w.readframes(nframes)
    assert sampwidth == 2
    samples = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768.0
    return samples, framerate, channels, nframes


def write_wav_float(path: str, samples: "np.ndarray", framerate: int, channels: int) -> None:
    assert np.all(np.isfinite(samples)), "出力サンプルにNaN/Infが含まれています"
    peak = np.max(np.abs(samples))
    assert peak <= 1.0 + 1e-9, f"出力にクリッピングの恐れがあります(peak={peak})"
    clipped = np.clip(samples, -1.0, 1.0)
    pcm16 = (clipped * 32767.0).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(channels)
        w.setsampwidth(2)
        w.setframerate(framerate)
        w.writeframes(pcm16.tobytes())


# ============================================================
# ブロック6: 語数・尺・実効wpm
# ============================================================
def word_count(text: str) -> int:
    return len(text.split())


def evaluate_word_count(count: int) -> dict:
    within_target = WORD_COUNT_TARGET_MIN <= count <= WORD_COUNT_TARGET_MAX
    within_accept = WORD_COUNT_ACCEPT_MIN <= count <= WORD_COUNT_ACCEPT_MAX
    return {
        "word_count": count,
        "target_min": WORD_COUNT_TARGET_MIN,
        "target_max": WORD_COUNT_TARGET_MAX,
        "accept_min": WORD_COUNT_ACCEPT_MIN,
        "accept_max": WORD_COUNT_ACCEPT_MAX,
        "within_target": within_target,
        "status": "within_acceptable_range" if within_accept else "out_of_range",
    }


def evaluate_duration(duration_seconds: float) -> dict:
    """130〜200秒は警告の目安であり、自動不合格条件にはしない(is_hard_gate=False)。"""
    within_warn_band = DURATION_WARN_MIN_SECONDS <= duration_seconds <= DURATION_WARN_MAX_SECONDS
    return {
        "duration_seconds": round(duration_seconds, 3),
        "warn_band_min_seconds": DURATION_WARN_MIN_SECONDS,
        "warn_band_max_seconds": DURATION_WARN_MAX_SECONDS,
        "within_warn_band": within_warn_band,
        "is_hard_gate": False,
    }


def effective_wpm(word_count_value: int, duration_seconds: float) -> Optional[float]:
    if duration_seconds <= 0:
        return None
    return round(word_count_value / (duration_seconds / 60.0), 2)


# ============================================================
# ブロック7: QAプロンプト構築(11分類を個別フィールド化)
# ============================================================
def build_embedded_qa_prompt(plan: NarrationPlan) -> str:
    elements = build_expected_elements(plan)
    element_texts_json = json.dumps({k: v for k, v in elements}, ensure_ascii=False)
    expected_order = [k for k, _ in elements]
    return f"""You are doing an automated technical QA check of a TTS-generated narration, comparing it against the approved source text below. Do NOT judge subjective voice quality or how expressive it sounds - only the technical criteria listed.

APPROVED SOURCE TEXT (must be read verbatim, in this exact order, not summarized/shortened/added to/reworded):
---
{plan.full_text}
---

REQUIRED ELEMENTS (JSON key -> exact text). Each must be spoken exactly once, in this order, as literal words (not paraphrased, not silently skipped, not merged with surrounding text):
{element_texts_json}

Listen to the audio and return ONLY valid JSON, no other text, in exactly this shape:
{{
  "element_counts": {{"title": 1, "today_points_heading": 1, "point_one": 1, "subheading1": 1, "point_two": 1, "subheading2": 1, "in_one_line": 1}},
  "body_dropped": false, "body_dropped_evidence": [],
  "body_duplicated": false, "body_duplicated_evidence": [],
  "unauthorized_paraphrase": false, "unauthorized_paraphrase_evidence": [],
  "section_order_changed": false, "observed_section_order": {json.dumps(expected_order, ensure_ascii=False)},
  "extra_unscripted_speech": false, "extra_unscripted_speech_evidence": [],
  "notes": "brief explanation in English"
}}

Where "element_counts" gives, for each key above, how many times that exact text is spoken as its own distinct element (0 = missing, 1 = correct, 2+ = duplicated).
"body_dropped"/"body_dropped_evidence": true and the missing sentence(s) if any part of the body text is missing.
"body_duplicated"/"body_duplicated_evidence": true and the repeated sentence(s) if any body sentence is spoken twice.
"unauthorized_paraphrase"/"unauthorized_paraphrase_evidence": true and {{"expected": "...", "observed": "..."}} pairs if wording is meaningfully changed.
"section_order_changed"/"observed_section_order": true and the actual spoken order of the element keys above if the order differs from the expected order.
"extra_unscripted_speech"/"extra_unscripted_speech_evidence": true and the extra text if anything is spoken that is not in the source text (including non-English speech or read-aloud stage directions/JSON keys/Markdown)."""


def build_grounded_qa_prompt(plan: NarrationPlan) -> str:
    elements = build_expected_elements(plan)
    element_texts_json = json.dumps({k: v for k, v in elements}, ensure_ascii=False)
    expected_order = [k for k, _ in elements]
    return f"""Here is the exact approved source text this audio should read aloud verbatim, in order:
---
{plan.full_text}
---

REQUIRED ELEMENTS (JSON key -> exact text), each expected exactly once, in this order:
{element_texts_json}

Listen to the audio and:
1. Transcribe exactly what is spoken, verbatim, from start to finish.
2. Independently (without reusing any prior judgment) count occurrences of each required element above.
3. Identify any dropped body content, duplicated body content, unauthorized paraphrasing, changed section order, or extra unscripted speech.

Return ONLY valid JSON, no other text, in exactly this shape:
{{
  "transcript": "...",
  "element_counts": {{"title": 1, "today_points_heading": 1, "point_one": 1, "subheading1": 1, "point_two": 1, "subheading2": 1, "in_one_line": 1}},
  "body_dropped": false, "body_dropped_evidence": [],
  "body_duplicated": false, "body_duplicated_evidence": [],
  "unauthorized_paraphrase": false, "unauthorized_paraphrase_evidence": [],
  "section_order_changed": false, "observed_section_order": {json.dumps(expected_order, ensure_ascii=False)},
  "extra_unscripted_speech": false, "extra_unscripted_speech_evidence": [],
  "notes": "brief explanation in English"
}}"""


# ============================================================
# ブロック8: QA応答の解析・分類・突合(fail-closed)
# ============================================================
class QAParseError(Exception):
    pass


def parse_qa_json(raw_text: Optional[str]) -> dict:
    """QAモデルの応答テキストからJSONを取り出す。解析できない場合は
    QAParseErrorを送出する(呼び出し元は合格扱いにしてはならない)。"""
    if raw_text is None:
        raise QAParseError("QA応答がNoneです(レスポンス欠落)")
    cleaned = re.sub(r"^```(json)?|```$", "", raw_text.strip(), flags=re.MULTILINE).strip()
    if not cleaned:
        raise QAParseError("QA応答が空文字列です")
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise QAParseError(f"QA応答をJSONとして解析できません: {e}")
    if not isinstance(parsed, dict):
        raise QAParseError("QA応答がJSONオブジェクトではありません")
    return parsed


def classify_element_counts(element_counts: Any, expected_keys: list[str]) -> dict:
    checks = {}
    for key in expected_keys:
        observed = element_counts.get(key) if isinstance(element_counts, dict) else None
        if not isinstance(observed, int) or isinstance(observed, bool):
            status = "unknown"
        elif observed == 1:
            status = "ok"
        elif observed == 0:
            status = "missing"
        elif observed > 1:
            status = "duplicated"
        else:
            status = "unknown"
        checks[key] = {"expected_count": 1, "observed_count": observed if isinstance(observed, int) else None, "status": status}
    return checks


def classify_qa_result(raw_result: dict, plan: NarrationPlan) -> dict:
    """1回のQA呼び出し結果(embeddedまたはgrounded)を11分類の個別フィールドへ整理する。
    欠落キー・型不一致は"unknown"扱いとし、"unknown"は合格として扱わない(fail-closed)。"""
    expected_keys = [k for k, _ in build_expected_elements(plan)]
    element_checks = classify_element_counts(raw_result.get("element_counts", {}), expected_keys)

    def bool_or_none(key: str):
        v = raw_result.get(key)
        return v if isinstance(v, bool) else None

    scalar_checks = {
        "body_dropped": bool_or_none("body_dropped"),
        "body_duplicated": bool_or_none("body_duplicated"),
        "unauthorized_paraphrase": bool_or_none("unauthorized_paraphrase"),
        "section_order_changed": bool_or_none("section_order_changed"),
        "extra_unscripted_speech": bool_or_none("extra_unscripted_speech"),
    }

    element_all_ok = all(c["status"] == "ok" for c in element_checks.values())
    # Trueなら「問題あり」。Noneは「モデルが答えなかった」ので合格扱いにしない(fail-closed)。
    scalar_all_clean = all(v is False for v in scalar_checks.values())
    passed = element_all_ok and scalar_all_clean

    reasons = [k for k, c in element_checks.items() if c["status"] != "ok"]
    reasons += [k for k, v in scalar_checks.items() if v is not False]

    return {
        "element_checks": element_checks,
        "scalar_checks": scalar_checks,
        "evidence": {
            "body_dropped_evidence": raw_result.get("body_dropped_evidence"),
            "body_duplicated_evidence": raw_result.get("body_duplicated_evidence"),
            "unauthorized_paraphrase_evidence": raw_result.get("unauthorized_paraphrase_evidence"),
            "observed_section_order": raw_result.get("observed_section_order"),
            "extra_unscripted_speech_evidence": raw_result.get("extra_unscripted_speech_evidence"),
        },
        "expected_text": plan.full_text,
        "transcript": raw_result.get("transcript"),
        "notes": raw_result.get("notes"),
        "passed": passed,
        "reasons": reasons,
    }


def aggregate_qa(embedded_classified: dict, grounded_classified: dict) -> dict:
    """embedded/grounded両方の分類結果を突合する。どちらかがpassed=Falseなら不合格。
    両方passed=Trueでも要素カウントが一致しない場合は「未解決の矛盾」として不合格にする
    (fail-closed。矛盾を握りつぶして合格にしない)。"""
    all_keys = set(embedded_classified["element_checks"]) | set(grounded_classified["element_checks"])
    agreement = {}
    disagreements = []
    for key in sorted(all_keys):
        e = embedded_classified["element_checks"].get(key, {}).get("observed_count")
        g = grounded_classified["element_checks"].get(key, {}).get("observed_count")
        agree = e == g
        agreement[key] = {"embedded": e, "grounded": g, "agree": agree}
        if not agree:
            disagreements.append(key)

    passed = embedded_classified["passed"] and grounded_classified["passed"] and not disagreements
    reasons = list(dict.fromkeys(embedded_classified["reasons"] + grounded_classified["reasons"]))
    if disagreements:
        reasons.append("embedded_grounded_disagreement")

    return {
        "passed": passed,
        "reasons": reasons,
        "agreement": agreement,
        "disagreements": disagreements,
        "embedded": embedded_classified,
        "grounded": grounded_classified,
    }


# ============================================================
# ブロック9: QA呼び出し(API障害時リトライ)。実API未使用(引数で注入)
# ============================================================
@dataclass
class QACallOutcome:
    raw_result: Optional[dict]
    api_retry_count: int
    parse_failed: bool = False
    error: Optional[str] = None


def call_qa_with_retry(
    qa_call_fn: Callable[[str, bytes], str],
    prompt: str,
    wav_bytes: bytes,
    max_retry: int = MAX_QA_API_RETRY,
    sleep_fn: Optional[Callable[[float], None]] = None,
) -> QACallOutcome:
    """qa_call_fn(prompt, wav_bytes) -> 生レスポンス文字列、を呼び出しJSON解析まで行う。
    呼び出し自体が例外を出す場合のみAPI障害としてリトライする。JSON解析に失敗した場合は
    リトライせず即座にfail-closed(呼び出し元は合格扱いにしてはならない)。"""
    last_error = None
    for attempt in range(max_retry + 1):
        try:
            raw_text = qa_call_fn(prompt, wav_bytes)
        except Exception as e:  # API障害
            last_error = str(e)
            if sleep_fn:
                sleep_fn(QA_API_RETRY_SLEEP_SECONDS)
            continue
        try:
            parsed = parse_qa_json(raw_text)
        except QAParseError as e:
            return QACallOutcome(raw_result=None, api_retry_count=attempt, parse_failed=True, error=str(e))
        return QACallOutcome(raw_result=parsed, api_retry_count=attempt, parse_failed=False)
    return QACallOutcome(
        raw_result=None, api_retry_count=max_retry, parse_failed=True,
        error=f"QA呼び出しが{max_retry + 1}回とも失敗しました: {last_error}",
    )


def _call_tts_with_retry(
    tts_call_fn: Callable[[str], bytes], prompt: str, max_retry: int, sleep_fn: Optional[Callable[[float], None]]
):
    last_error = None
    for attempt in range(max_retry + 1):
        try:
            pcm = tts_call_fn(prompt)
            return pcm, attempt, True, None
        except Exception as e:
            last_error = str(e)
            if sleep_fn:
                sleep_fn(TTS_API_RETRY_SLEEP_SECONDS)
    return None, max_retry, False, last_error


# ============================================================
# ブロック10: QA評価試行(TTS再生成とは分離。同じ音声につき最大2回)
# ============================================================
# ER-002-S1.1で変更: 「QAが不調」というだけの理由で直ちに同じ内容の
# TTSを再生成しない。同じ音声(TTSコンテンツ試行)に対して、QA自体の
# 評価だけを最大2回まで独立にやり直せるようにする。
#
# 「判定不能(inconclusive)」= 同じ音声でQAだけ再評価する対象:
#   - JSON解析不能 / 必須フィールド欠落 / 型不一致
#   - embeddedとgroundedの未解決な矛盾(要素カウント不一致)
#   - QAレスポンスとして判定不能
#
# 「確定的な不合格(conclusive_fail)」= 有効な形式で不具合を検出した場合。
# 同じ音声のQAを繰り返さず、次のTTSコンテンツ試行へ進む:
#   - 必須要素欠落・重複、本文欠落・重複、言い換え、順序変更、追加発話
#
# 2回ともinconclusiveならQA_INCONCLUSIVEとして不合格(TTS_CONTENT_FAILURE
# =conclusive_failとは区別する)。いずれの場合も不合格音声は採用しない。
MAX_QA_EVALUATION_ATTEMPTS = 2  # 1つのTTS音声につきQA評価は最大2回


@dataclass
class QAEvaluationAttemptRecord:
    qa_evaluation_attempt_number: int
    outcome: str  # "passed" / "conclusive_fail" / "inconclusive"
    reasons: list
    embedded_qa_api_retry_count: int
    grounded_qa_api_retry_count: int
    embedded_classified: Optional[dict] = None
    grounded_classified: Optional[dict] = None
    aggregated: Optional[dict] = None


@dataclass
class QAEvaluationOutcome:
    final_outcome: str  # "passed" / "conclusive_fail" / "inconclusive"
    reasons: list
    attempts: list  # list[QAEvaluationAttemptRecord]
    total_embedded_qa_api_retry_count: int
    total_grounded_qa_api_retry_count: int


def evaluate_qa_for_audio(
    plan: NarrationPlan,
    wav_bytes: bytes,
    qa_call_fn: Callable[[str, bytes], str],
    max_qa_eval_attempts: int = MAX_QA_EVALUATION_ATTEMPTS,
    max_api_retry: int = MAX_QA_API_RETRY,
    sleep_fn: Optional[Callable[[float], None]] = None,
) -> QAEvaluationOutcome:
    """同一のwav_bytes(TTSを再生成しない)に対して、QA評価だけを最大
    max_qa_eval_attempts回まで行う。API通信障害時のリトライ
    (call_qa_with_retryの内部)はqa_evaluation_attempt_numberを
    増やさない(このループの1周が1回のqa_evaluation_attemptに対応する)。"""
    attempts: list[QAEvaluationAttemptRecord] = []
    total_embedded_retry = 0
    total_grounded_retry = 0

    for qa_attempt in range(1, max_qa_eval_attempts + 1):
        embedded_outcome = call_qa_with_retry(
            qa_call_fn, build_embedded_qa_prompt(plan), wav_bytes, max_retry=max_api_retry, sleep_fn=sleep_fn)
        total_embedded_retry += embedded_outcome.api_retry_count

        if embedded_outcome.parse_failed or embedded_outcome.raw_result is None:
            attempts.append(QAEvaluationAttemptRecord(
                qa_evaluation_attempt_number=qa_attempt, outcome="inconclusive",
                reasons=["embedded_qa_unavailable_or_unparseable"],
                embedded_qa_api_retry_count=embedded_outcome.api_retry_count,
                grounded_qa_api_retry_count=0,
            ))
            continue  # 同じ音声で再評価

        embedded_classified = classify_qa_result(embedded_outcome.raw_result, plan)
        if not embedded_classified["passed"]:
            # 有効な形式で不具合を検出できた = 判定不能ではなく確定的な不合格。再評価しない。
            attempts.append(QAEvaluationAttemptRecord(
                qa_evaluation_attempt_number=qa_attempt, outcome="conclusive_fail",
                reasons=embedded_classified["reasons"],
                embedded_qa_api_retry_count=embedded_outcome.api_retry_count,
                grounded_qa_api_retry_count=0,
                embedded_classified=embedded_classified,
            ))
            return QAEvaluationOutcome(
                final_outcome="conclusive_fail", reasons=embedded_classified["reasons"], attempts=attempts,
                total_embedded_qa_api_retry_count=total_embedded_retry,
                total_grounded_qa_api_retry_count=total_grounded_retry,
            )

        grounded_outcome = call_qa_with_retry(
            qa_call_fn, build_grounded_qa_prompt(plan), wav_bytes, max_retry=max_api_retry, sleep_fn=sleep_fn)
        total_grounded_retry += grounded_outcome.api_retry_count

        if grounded_outcome.parse_failed or grounded_outcome.raw_result is None:
            attempts.append(QAEvaluationAttemptRecord(
                qa_evaluation_attempt_number=qa_attempt, outcome="inconclusive",
                reasons=["grounded_qa_unavailable_or_unparseable"],
                embedded_qa_api_retry_count=embedded_outcome.api_retry_count,
                grounded_qa_api_retry_count=grounded_outcome.api_retry_count,
                embedded_classified=embedded_classified,
            ))
            continue

        grounded_classified = classify_qa_result(grounded_outcome.raw_result, plan)
        if not grounded_classified["passed"]:
            attempts.append(QAEvaluationAttemptRecord(
                qa_evaluation_attempt_number=qa_attempt, outcome="conclusive_fail",
                reasons=grounded_classified["reasons"],
                embedded_qa_api_retry_count=embedded_outcome.api_retry_count,
                grounded_qa_api_retry_count=grounded_outcome.api_retry_count,
                embedded_classified=embedded_classified, grounded_classified=grounded_classified,
            ))
            return QAEvaluationOutcome(
                final_outcome="conclusive_fail", reasons=grounded_classified["reasons"], attempts=attempts,
                total_embedded_qa_api_retry_count=total_embedded_retry,
                total_grounded_qa_api_retry_count=total_grounded_retry,
            )

        aggregated = aggregate_qa(embedded_classified, grounded_classified)
        if aggregated["disagreements"]:
            # 両者とも有効な形式だが未解決の矛盾がある = 判定不能。同じ音声で再評価。
            attempts.append(QAEvaluationAttemptRecord(
                qa_evaluation_attempt_number=qa_attempt, outcome="inconclusive",
                reasons=["embedded_grounded_disagreement"],
                embedded_qa_api_retry_count=embedded_outcome.api_retry_count,
                grounded_qa_api_retry_count=grounded_outcome.api_retry_count,
                embedded_classified=embedded_classified, grounded_classified=grounded_classified,
                aggregated=aggregated,
            ))
            continue

        attempts.append(QAEvaluationAttemptRecord(
            qa_evaluation_attempt_number=qa_attempt, outcome="passed", reasons=[],
            embedded_qa_api_retry_count=embedded_outcome.api_retry_count,
            grounded_qa_api_retry_count=grounded_outcome.api_retry_count,
            embedded_classified=embedded_classified, grounded_classified=grounded_classified,
            aggregated=aggregated,
        ))
        return QAEvaluationOutcome(
            final_outcome="passed", reasons=[], attempts=attempts,
            total_embedded_qa_api_retry_count=total_embedded_retry,
            total_grounded_qa_api_retry_count=total_grounded_retry,
        )

    # max_qa_eval_attempts回すべてinconclusiveのまま終了
    return QAEvaluationOutcome(
        final_outcome="inconclusive", reasons=["qa_inconclusive_after_max_attempts"], attempts=attempts,
        total_embedded_qa_api_retry_count=total_embedded_retry,
        total_grounded_qa_api_retry_count=total_grounded_retry,
    )


# ============================================================
# ブロック11: TTSコンテンツ試行のオーケストレーション(fail-closed)
# ============================================================
# outcome分類(failure_classification用):
#   "passed"          -> 採用
#   "conclusive_fail" -> TTS_CONTENT_FAILURE(音声そのものの不具合)
#   "inconclusive"    -> QA_INCONCLUSIVE(2回とも判定不能)
#   "tts_api_exhausted" -> TTS_API_EXHAUSTED(TTS呼び出し自体の通信障害)
OUTCOME_LABELS = {
    "passed": "passed",
    "conclusive_fail": "TTS_CONTENT_FAILURE",
    "inconclusive": "QA_INCONCLUSIVE",
    "tts_api_exhausted": "TTS_API_EXHAUSTED",
}


@dataclass
class ContentAttemptRecord:
    tts_content_attempt_number: int
    outcome: str  # "passed" / "conclusive_fail" / "inconclusive" / "tts_api_exhausted"
    tts_api_retry_count: int
    qa_evaluation_attempts: list = field(default_factory=list)  # list[QAEvaluationAttemptRecord]
    qa_evaluation_attempt_count: int = 0
    embedded_qa_api_retry_count: int = 0
    grounded_qa_api_retry_count: int = 0
    qa_api_retry_count: int = 0
    reasons: list = field(default_factory=list)
    audio: Optional[bytes] = None


@dataclass
class TTSRunResult:
    status: str  # "OK" または "FAILED_ALL_ATTEMPTS"
    accepted_attempt: Optional[int] = None
    accepted_audio: Optional[bytes] = None
    attempts: list = field(default_factory=list)


def summarize_failure_outcomes(attempts: list) -> dict:
    """TTS_CONTENT_FAILUREとQA_INCONCLUSIVEを別々に集計する。"""
    counts = {label: 0 for label in OUTCOME_LABELS.values()}
    for a in attempts:
        counts[OUTCOME_LABELS.get(a.outcome, a.outcome)] += 1
    return counts


def run_tts_content_attempts(
    plan: NarrationPlan,
    style_prefix: str,
    tts_call_fn: Callable[[str], bytes],
    qa_call_fn: Callable[[str, bytes], str],
    max_content_attempts: int = MAX_TTS_CONTENT_ATTEMPTS,
    max_api_retry: int = MAX_TTS_API_RETRY,
    max_qa_eval_attempts: int = MAX_QA_EVALUATION_ATTEMPTS,
    sample_rate: int = SAMPLE_RATE,
    sleep_fn: Optional[Callable[[float], None]] = None,
) -> TTSRunResult:
    """既存のfail-open処理(ER-001B-6/7B)は参照・流用しない。全試行不合格なら
    FAILED_ALL_ATTEMPTSとし、不合格音声を採用しない。TTSコンテンツ試行(最大
    max_content_attempts回)ごとに、同じ音声でQA評価を最大max_qa_eval_attempts回
    まで行う(evaluate_qa_for_audio)。QAが判定不能なだけでは直ちに新しい音声を
    生成しない。"""
    attempts: list[ContentAttemptRecord] = []

    for content_attempt in range(1, max_content_attempts + 1):
        pcm_chunks = []
        chunk_api_retries = 0
        failed_chunk_generation = False

        for _label, text in plan.chunks:
            pcm, retries, ok, _err = _call_tts_with_retry(tts_call_fn, style_prefix + text, max_api_retry, sleep_fn)
            chunk_api_retries += retries
            if not ok:
                failed_chunk_generation = True
                break
            pcm_chunks.append(pcm)

        if failed_chunk_generation:
            attempts.append(ContentAttemptRecord(
                tts_content_attempt_number=content_attempt, outcome="tts_api_exhausted",
                tts_api_retry_count=chunk_api_retries, reasons=["tts_api_exhausted"],
            ))
            continue

        audio, _pause_positions = assemble_audio(pcm_chunks, sample_rate=sample_rate)
        wav_bytes = pcm_to_wav_bytes(audio, sample_rate)

        qa_outcome = evaluate_qa_for_audio(
            plan, wav_bytes, qa_call_fn,
            max_qa_eval_attempts=max_qa_eval_attempts, max_api_retry=MAX_QA_API_RETRY, sleep_fn=sleep_fn,
        )

        record = ContentAttemptRecord(
            tts_content_attempt_number=content_attempt,
            outcome=qa_outcome.final_outcome,
            tts_api_retry_count=chunk_api_retries,
            qa_evaluation_attempts=qa_outcome.attempts,
            qa_evaluation_attempt_count=len(qa_outcome.attempts),
            embedded_qa_api_retry_count=qa_outcome.total_embedded_qa_api_retry_count,
            grounded_qa_api_retry_count=qa_outcome.total_grounded_qa_api_retry_count,
            qa_api_retry_count=qa_outcome.total_embedded_qa_api_retry_count + qa_outcome.total_grounded_qa_api_retry_count,
            reasons=qa_outcome.reasons,
            audio=audio,
        )
        attempts.append(record)

        if qa_outcome.final_outcome == "passed":
            return TTSRunResult(status="OK", accepted_attempt=content_attempt, accepted_audio=audio, attempts=attempts)
        # "conclusive_fail"・"inconclusive"のいずれも、この音声は採用せず次のTTS
        # コンテンツ試行へ進む(判定不能だからといって即座に新しい音声を作るわけ
        # ではなく、既にevaluate_qa_for_audio内で同じ音声のQA再評価は使い切っている)。

    return TTSRunResult(status="FAILED_ALL_ATTEMPTS", attempts=attempts)


# ============================================================
# ブロック11: 台本試行のオーケストレーション(fail-closed)
# ============================================================
@dataclass
class ScriptAttemptRecord:
    attempt_number: int
    word_count: Optional[int]
    word_count_status: str
    structure_valid: bool
    structure_errors: list


@dataclass
class ScriptRunResult:
    status: str  # "OK" または "FAILED_ALL_ATTEMPTS"
    accepted_attempt: Optional[int] = None
    script: Optional[dict] = None
    plan: Optional[NarrationPlan] = None
    attempts: list = field(default_factory=list)


def run_script_attempts(
    config: dict,
    script_write_fn: Callable[[dict], dict],
    max_attempts: int = MAX_SCRIPT_ATTEMPTS,
) -> ScriptRunResult:
    """初回+全文再生成1回(最大2試行)。語数320〜480語の範囲外、または構造検証
    (subsections=2件など)に失敗した場合は全文再生成し、再生成後も失敗すれば
    FAILED_ALL_ATTEMPTSとする。人間による部分修正・候補選抜は行わない。"""
    attempts: list[ScriptAttemptRecord] = []

    for attempt in range(1, max_attempts + 1):
        script = script_write_fn(config)
        structure = validate_script_structure(script)

        plan = None
        wc = None
        wc_status = "structure_invalid"
        if structure.valid:
            plan = build_narration_plan(script)
            wc = word_count(plan.full_text)
            wc_status = evaluate_word_count(wc)["status"]

        passed = structure.valid and wc_status == "within_acceptable_range"
        attempts.append(ScriptAttemptRecord(
            attempt_number=attempt, word_count=wc, word_count_status=wc_status,
            structure_valid=structure.valid, structure_errors=structure.errors,
        ))
        if passed:
            return ScriptRunResult(status="OK", accepted_attempt=attempt, script=script, plan=plan, attempts=attempts)

    return ScriptRunResult(status="FAILED_ALL_ATTEMPTS", attempts=attempts)


# ============================================================
# ブロック12: Dynamics3(ER-001B-8/9/10と同一実装・同一パラメータ)
# ============================================================
def design_rbj_highshelf(sr, f0, gain_db, q):
    A = 10 ** (gain_db / 40)
    w0 = 2 * np.pi * f0 / sr
    alpha = np.sin(w0) / (2 * q)
    cos_w0 = np.cos(w0)
    sqrtA = np.sqrt(A)
    b0 = A * ((A + 1) + (A - 1) * cos_w0 + 2 * sqrtA * alpha)
    b1 = -2 * A * ((A - 1) + (A + 1) * cos_w0)
    b2 = A * ((A + 1) + (A - 1) * cos_w0 - 2 * sqrtA * alpha)
    a0 = (A + 1) - (A - 1) * cos_w0 + 2 * sqrtA * alpha
    a1 = 2 * ((A - 1) - (A + 1) * cos_w0)
    a2 = (A + 1) - (A - 1) * cos_w0 - 2 * sqrtA * alpha
    return np.array([b0, b1, b2]) / a0, np.array([a0, a1, a2]) / a0


def design_rbj_highpass(sr, f0, q):
    w0 = 2 * np.pi * f0 / sr
    alpha = np.sin(w0) / (2 * q)
    cos_w0 = np.cos(w0)
    b0 = (1 + cos_w0) / 2
    b1 = -(1 + cos_w0)
    b2 = (1 + cos_w0) / 2
    a0 = 1 + alpha
    a1 = -2 * cos_w0
    a2 = 1 - alpha
    return np.array([b0, b1, b2]) / a0, np.array([a0, a1, a2]) / a0


LUFS_METHOD_NOTE = (
    "ITU-R BS.1770のK-weightingを24kHz向けにRBJ Audio EQ Cookbookの式で再設計し、"
    "2段階ゲーティングで積分ラウドネスを近似計算したもの(ER-001B-7A/8/9/10と同一実装)。"
    "公式のBS.1770準拠測定器とは完全には一致しない可能性がある近似値。"
)
LRA_METHOD_NOTE = "3秒窓・1秒ホップの短時間ラウドネス分布のP95-P10による簡易近似。EBU R128のLRA完全準拠アルゴリズムではない。"


def k_weight(samples, sr):
    b1, a1 = design_rbj_highshelf(sr, 1681.9, 3.999844545, 0.7071752369554193)
    b2, a2 = design_rbj_highpass(sr, 38.13547087613982, 0.5003270373238773)
    return lfilter(b2, a2, lfilter(b1, a1, samples))


def integrated_lufs_approx(samples, sr):
    y = k_weight(samples, sr)
    block, hop = int(0.4 * sr), int(0.1 * sr)
    if len(y) < block:
        return None
    z = np.array([np.mean(y[s:s + block] ** 2) for s in range(0, len(y) - block + 1, hop)])
    z = z[z > 0]
    if len(z) == 0:
        return None
    loudness = -0.691 + 10 * np.log10(z)
    gated1 = z[loudness > -70]
    if len(gated1) == 0:
        return None
    ungated_loudness = -0.691 + 10 * np.log10(np.mean(gated1))
    rel_gate = ungated_loudness - 10
    loudness1 = -0.691 + 10 * np.log10(gated1)
    gated2 = gated1[loudness1 > rel_gate]
    if len(gated2) == 0:
        gated2 = gated1
    return float(-0.691 + 10 * np.log10(np.mean(gated2)))


def loudness_range_approx(samples, sr):
    y = k_weight(samples, sr)
    block, hop = int(3.0 * sr), int(1.0 * sr)
    if len(y) < block:
        return None
    vals = []
    for s in range(0, len(y) - block + 1, hop):
        z = np.mean(y[s:s + block] ** 2)
        if z > 0:
            vals.append(-0.691 + 10 * np.log10(z))
    if len(vals) < 2:
        return None
    vals = np.array(vals)
    gated = vals[vals > -70]
    if len(gated) < 2:
        gated = vals
    return float(np.percentile(gated, 95) - np.percentile(gated, 10))


def db(x):
    return 20 * np.log10(max(x, 1e-12))


def measure_metrics(mono, sr):
    peak = float(np.max(np.abs(mono)))
    rms = float(np.sqrt(np.mean(mono ** 2)))
    clip_count = int(np.sum(np.abs(mono) >= 0.999))
    lufs = integrated_lufs_approx(mono, sr)
    lra = loudness_range_approx(mono, sr)
    crest_factor_db = round(db(peak) - db(rms), 2) if rms > 0 else None
    return {
        "duration_seconds": round(len(mono) / sr, 3),
        "sample_count": int(len(mono)),
        "sample_rate": sr,
        "peak_dbfs": round(db(peak), 2),
        "rms_dbfs": round(db(rms), 2),
        "integrated_lufs_approx": round(lufs, 2) if lufs is not None else None,
        "loudness_range_approx_lu": round(lra, 2) if lra is not None else None,
        "crest_factor_db": crest_factor_db,
        "clipping_sample_count": clip_count,
        "clipping_detected": clip_count > 0,
    }


def soft_knee_gain_reduction_db(level_db, threshold_db, ratio, knee_db):
    gr = np.zeros_like(level_db)
    lower, upper = threshold_db - knee_db / 2, threshold_db + knee_db / 2
    below, above = level_db <= lower, level_db >= upper
    within = ~below & ~above
    gr[above] = (level_db[above] - threshold_db) * (1 / ratio - 1)
    x = level_db[within] - lower
    gr[within] = ((1 / ratio - 1) * (x ** 2)) / (2 * knee_db)
    return gr


def envelope_follower_db(mono, sr, attack_ms, release_ms):
    abs_sig = np.abs(mono)
    attack_coef = np.exp(-1.0 / (sr * attack_ms / 1000.0))
    release_coef = np.exp(-1.0 / (sr * release_ms / 1000.0))
    env = np.zeros_like(abs_sig)
    prev = 0.0
    for i, x in enumerate(abs_sig):
        coef = attack_coef if x > prev else release_coef
        prev = coef * prev + (1 - coef) * x
        env[i] = prev
    return 20 * np.log10(np.maximum(env, 1e-9))


def apply_compressor(mono, sr, params):
    env_db = envelope_follower_db(mono, sr, params["attack_ms"], params["release_ms"])
    threshold_db = float(np.percentile(env_db, params["threshold_percentile"]))
    gr_db = soft_knee_gain_reduction_db(env_db, threshold_db, params["ratio"], params["knee_db"])
    smooth_coef = np.exp(-1.0 / (sr * params["gain_smoothing_ms"] / 1000.0))
    gr_db_smoothed = np.zeros_like(gr_db)
    prev = 0.0
    for i, g in enumerate(gr_db):
        prev = smooth_coef * prev + (1 - smooth_coef) * g
        gr_db_smoothed[i] = prev
    gain_linear = 10 ** (gr_db_smoothed / 20)
    return mono * gain_linear, gr_db_smoothed, threshold_db


PEAK_CEILING_DB = -1.0


def match_loudness(processed, target_lufs, sr):
    compressed_lufs = integrated_lufs_approx(processed, sr)
    current_peak_db = db(float(np.max(np.abs(processed))))
    desired_gain_db = 0.0 if (target_lufs is None or compressed_lufs is None) else target_lufs - compressed_lufs
    max_gain_allowed_by_peak_db = PEAK_CEILING_DB - current_peak_db
    final_gain_db = min(desired_gain_db, max_gain_allowed_by_peak_db)
    gained = processed * (10 ** (final_gain_db / 20))
    final_lufs = integrated_lufs_approx(gained, sr)
    shortfall_lu = round(target_lufs - final_lufs, 3) if (target_lufs is not None and final_lufs is not None) else None
    return gained, {
        "target_lufs": round(target_lufs, 2) if target_lufs is not None else None,
        "compressed_lufs_before_gain": round(compressed_lufs, 2) if compressed_lufs is not None else None,
        "desired_gain_db": round(desired_gain_db, 3),
        "peak_ceiling_db": PEAK_CEILING_DB,
        "max_gain_allowed_by_peak_db": round(max_gain_allowed_by_peak_db, 3),
        "applied_fixed_gain_db": round(final_gain_db, 3),
        "peak_ceiling_prioritized": bool(final_gain_db < desired_gain_db - 1e-9),
        "final_peak_dbfs": round(db(float(np.max(np.abs(gained)))), 2),
        "final_lufs_approx": round(final_lufs, 2) if final_lufs is not None else None,
        "loudness_shortfall_lu": shortfall_lu,
        "within_0_3_lu_target": (abs(shortfall_lu) <= LOUDNESS_MATCH_TARGET_LU) if shortfall_lu is not None else None,
    }


@dataclass
class DynamicsApplicationResult:
    c1_samples: Any
    metrics_c0: dict
    metrics_c1: dict
    loudness_matching: dict
    dynamics_params: dict
    applied_once: bool = True


def apply_dynamics3_once(c0_mono, sample_rate: int = SAMPLE_RATE) -> DynamicsApplicationResult:
    """C0(生音声)へDynamics3を一度だけ適用してC1を返す。安全アサーション
    (減衰のみ・NaN/Infなし・増幅なし)はER-001B-8/9/10と同一。"""
    c0_metrics = measure_metrics(c0_mono, sample_rate)
    processed, gr_db_series, _threshold_db_used = apply_compressor(c0_mono, sample_rate, DYNAMICS3_PARAMS)

    assert np.all(gr_db_series <= 1e-6), "ゲインリダクションが正(増幅)になっています(想定外)"
    assert np.all(np.isfinite(processed)), "処理直後の信号にNaN/Infが含まれています"
    assert np.all(np.abs(processed) <= np.abs(c0_mono) + 1e-9), "処理直後のサンプル絶対値がC0を上回っています(想定外の増幅)"

    target_lufs = c0_metrics["integrated_lufs_approx"]
    matched, loudness_info = match_loudness(processed, target_lufs, sample_rate)
    assert not np.any(np.abs(matched) >= 1.0), "ラウドネス整合後にクリッピングの恐れがあります"

    c1_metrics = measure_metrics(matched, sample_rate)
    return DynamicsApplicationResult(
        c1_samples=matched,
        metrics_c0=c0_metrics,
        metrics_c1=c1_metrics,
        loudness_matching=loudness_info,
        dynamics_params=dict(DYNAMICS3_PARAMS),
    )


# ============================================================
# ブロック13: 記事成果物ファイル一覧(Git追跡方針、ER-002-S1.1で確定)
# ============================================================
# er002_output/<article_id>/ 配下でGit追跡する成果物のファイル名。
# 音声実体(*.wav)・A/B対応表(*_ab_mapping.json)・元記事全文キャッシュ
# (raw_source_fulltext*)・一時ファイルは.gitignoreで個別に除外している
# (このリストには含めない)。
TRACKED_ARTIFACT_FILENAMES = [
    "manifest.json",
    "topic_candidates.json",
    "topic_selection.json",
    "source_refs.json",
    "raw_facts.json",
    "script_ja.json",
    "script_en.json",
    "tts_expected_text.txt",
    "script_attempts.json",
    "tts_attempts.json",
    "qa_results.json",
    "dynamics_metrics.json",
    "final_audio_ref.json",
    "failure_classification.json",
    "user_evaluation.json",
    "run_summary.txt",
]

# 追跡対象外にする名前の慣習(実ファイルは.gitignoreの
# er002_output/**/raw_source_fulltext* / *_ab_mapping.json / *.wav で除外)
UNTRACKED_ARTIFACT_NAME_HINTS = [
    "raw_source_fulltext",  # 元記事全文のローカルキャッシュ
    "_ab_mapping.json",     # A/B対応表
    ".wav",                 # 音声実体
]


# ============================================================
# ブロック14: ユーザー評価スキーマ(記事/サンプル単位、A/B追加項目)
# ============================================================
def default_user_evaluation() -> dict:
    """記事(またはA/Bの1サンプル)単位のユーザー評価の初期値。
    生成直後は常にstatus="pending_user_listening"で始まる。"""
    return {
        "status": "pending_user_listening",  # "pending_user_listening" / "completed"
        "listened_to_end": None,             # bool | null
        "wants_more_topics": None,           # bool | null
        "content_interest": None,            # "yes" / "neutral" / "no" | null
        "voice_fit": None,                   # bool | null
        "structure_issue": {"present": None, "notes": None},
        "dynamics_issue": {"present": None, "notes": None},
        "other_notes": None,
        "completed_at": None,
    }


def default_ab_user_evaluation() -> dict:
    """A/B比較記事(A04・A05)向けの追加項目込みの評価スキーマ。"""
    evaluation = default_user_evaluation()
    evaluation.update({
        "more_suitable_voice": None,  # "sample_1" / "sample_2" / "no_difference" | null
        "easier_to_finish": None,     # 同上
        "difference": None,           # 同上
        "reason": None,
    })
    return evaluation


def mark_user_evaluation_completed(evaluation: dict, **fields) -> dict:
    """評価入力を反映し、statusをcompletedへ進める(呼び出し側が実際の
    値を渡す。ここでは初期状態からの遷移の形だけを提供する)。"""
    updated = dict(evaluation)
    updated.update(fields)
    updated["status"] = "completed"
    return updated
