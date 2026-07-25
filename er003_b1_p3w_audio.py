# ============================================================
# er003_b1_p3w_audio.py
# ER-003-B1-P3W: MFAマーカー置換・短尺検証
# ============================================================
# ER-003-B1-P3Vで、Gemini TTSにはBreak/Mark/Timestamp機能がないことを
# 確認した。本ステージでは、TTS用の一時原稿に発話可能な明示マーカー語
# 「キーワード挿入位置」を入れ、Montreal Forced Aligner(MFA、既存
# 依存関係にはない新規ツールだが、アプリ本体のproduction依存関係とは
# 完全に分離した専用環境へ構築する)で、そのマーカー語の開始・終了時刻を
# 取得する。無音長・ASRタイムスタンプ・GPT推測はいずれも使わない。
#
# 再利用するもの(再実装しない):
#   - er002_common.SAMPLE_RATE/read_wav_float/write_wav_float/
#     pcm_bytes_to_float_mono/measure_metrics/apply_dynamics3_once/
#     _call_tts_with_retry/MODEL_NAME
#   - er002_gemini_client.make_tts_call_fn(voice_name)
#   - er003_b1_p3r_audio.VOICE_NAME/build_style_prefix/build_tts_prompt
#   - er003_b1_p3t_audio.SOURCE_INTEGRATED_SENTENCE/
#     SOURCE_JAPANESE_FULL_SENTENCE/SOURCE_ENGLISH_KEYWORD
#   - er003_b1_p3u_audio.BOUNDARY_PAUSE_SECONDS(0.12秒)/
#     join_with_boundary_pauses
#   - er003_b1_p3u_audio.EXISTING_EN_PATH配下で作られたtrim済み英語音声
#     (er003_output/b1_p3u/A01/components/en_shot_on_target_trimmed.wav)

from __future__ import annotations

import os
import re
import subprocess

import er003_b1_p3r_audio as p3r
import er003_b1_p3t_audio as p3t
import er003_b1_p3u_audio as p3u

# ------------------------------------------------------------
# MFA(Montreal Forced Aligner)専用環境
# ------------------------------------------------------------
# アプリ本体のproduction依存関係(.venv)とは完全に分離した、micromamba
# root prefix + isolated env + 日本語音響/辞書/tokenizerモデル一式。
# mfa_tool/はGit管理対象外(.gitignore参照)。

_REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
MFA_MICROMAMBA_EXE = os.path.join(_REPO_ROOT, "mfa_tool", "Library", "bin", "micromamba.exe")
MFA_ENV_PREFIX = os.path.join(_REPO_ROOT, "mfa_tool", "envs", "mfa")
MFA_ROOT_DIR = os.path.join(_REPO_ROOT, "mfa_tool", "mfa_root")
MFA_ACOUSTIC_MODEL_NAME = "japanese_mfa"
MFA_DICTIONARY_NAME = "japanese_mfa"


def mfa_environment_available() -> bool:
    return os.path.exists(MFA_MICROMAMBA_EXE) and os.path.isdir(MFA_ENV_PREFIX)


# デフォルトのKaldiビーム幅(beam=10, retry_beam=40)では、マーカー語
# (辞書内の希少語3語の連続)を含む文で "NoAlignmentsError"(1発話全体で
# 整列パスが1つも見つからない)が発生することを実機で確認した。これは
# 語彙・無音長・ASR等の代替推定とは無関係な、Kaldiデコーダの探索幅の
# 問題であり、MFA公式のエラーメッセージ自身が
# "mfa align ... --beam 100 --retry_beam 400" を最初の対処として提示する
# 標準的なチューニングパラメータである。スモークテスト(採用済み文言、
# マーカーなし)はデフォルトビーム幅のまま成功しており、変更するのは
# 本ステージのマーカー整列のみに限定する。
MFA_BEAM = 100
MFA_RETRY_BEAM = 400


def run_mfa_align(
    corpus_dir: str,
    output_dir: str,
    timeout_seconds: int = 600,
    beam: int = MFA_BEAM,
    retry_beam: int = MFA_RETRY_BEAM,
) -> dict:
    """隔離環境のmfa align <corpus_dir> japanese_mfa japanese_mfa <output_dir>
    --clean --beam <beam> --retry_beam <retry_beam>をsubprocessで実行する。
    無音長・ASR等の代替推定は一切行わず、MFAの整列結果(TextGrid)のみを
    次段の根拠とする。"""
    env = dict(os.environ)
    env["MFA_ROOT_DIR"] = MFA_ROOT_DIR
    cmd = [
        MFA_MICROMAMBA_EXE, "run", "-p", MFA_ENV_PREFIX,
        "mfa", "align", corpus_dir, MFA_DICTIONARY_NAME, MFA_ACOUSTIC_MODEL_NAME, output_dir,
        "--clean", "--beam", str(beam), "--retry_beam", str(retry_beam),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_seconds, env=env)
    return {
        "command": cmd,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "success": result.returncode == 0,
    }


_TEXTGRID_INTERVAL_PATTERN = re.compile(
    r'intervals\s*\[\d+\]:\s*'
    r'xmin\s*=\s*([\d.]+)\s*'
    r'xmax\s*=\s*([\d.]+)\s*'
    r'text\s*=\s*"([^"]*)"',
)


def parse_textgrid_words_tier(textgrid_path: str) -> list[dict]:
    """MFAが出力したPraat long-format TextGridの'words' IntervalTierを
    パースし、[{'text','xmin','xmax'}, ...]を返す(空文字intervalも含む)。
    praatio等の外部ライブラリには依存しない最小実装(このプロジェクトの
    productionには不要な重い依存を持ち込まないため)。"""
    with open(textgrid_path, encoding="utf-8") as f:
        content = f.read()

    tier_blocks = re.split(r'item\s*\[\d+\]:\s*', content)[1:]
    words_block = None
    for block in tier_blocks:
        if 'name = "words"' in block:
            words_block = block
            break
    if words_block is None:
        raise ValueError(f"'words' tierが見つかりません: {textgrid_path}")

    # 次のtierブロック(phones等)の内容を誤って取り込まないよう、
    # 自分のブロック分のみを対象にする(tier_blocksの分割で既に区切り済み)。
    intervals = []
    for m in _TEXTGRID_INTERVAL_PATTERN.finditer(words_block):
        intervals.append({
            "xmin": float(m.group(1)),
            "xmax": float(m.group(2)),
            "text": m.group(3),
        })
    return intervals


# MFAの日本語tokenizer(japanese_mfa)は、マーカー語(MARKER_TOKEN=
# "キーワード挿入位置")を辞書内の3つの実在語へ分割して認識する
# (実機のTextGridで確認済み: "キーワード"/"挿入"/"位置")。この3語が
# この順で連続して現れる区間を、マーカー区間として扱う(指示section4の
# 「複数tokenに分かれる場合は、先頭token開始から末尾token終了までを
# マーカー区間とする」に対応)。
MARKER_TOKEN_SEQUENCE = ("キーワード", "挿入", "位置")


def find_marker_span(words: list[dict], marker_tokens: tuple = None) -> tuple[dict | None, str | None]:
    """MFAのwords tierから、マーカー語のtoken列(marker_tokens、連続する
    複数tokenでもよい)が現れる区間を特定する。先頭token開始〜末尾token
    終了を区間とする。マーカーtoken同士の間に無音interval(text="")が
    挟まっていても連続とみなす(実機で、マーカー語の途中に短い間が
    生じるケースを確認済み。無音の長さそのものを判定根拠にはせず、
    あくまで語順の一致のみを根拠にする)。直前が「シュート」、直後が
    「を」であることを、無音を除いた実語ベースで確認し、満たさない
    場合は(None, 理由)を返して呼び出し側で停止させる。"""
    if marker_tokens is None:
        marker_tokens = MARKER_TOKEN_SEQUENCE
    marker_tokens = tuple(marker_tokens)
    n = len(marker_tokens)

    # 無音interval(text="")を除いた実語のみを対象に語順を照合する。
    non_empty = [(i, w["text"]) for i, w in enumerate(words) if w["text"] != ""]
    non_empty_texts = [t for _, t in non_empty]

    match_starts = [
        i for i in range(len(non_empty_texts) - n + 1)
        if tuple(non_empty_texts[i:i + n]) == marker_tokens
    ]
    if len(match_starts) == 0:
        return None, f"マーカー語の並び{marker_tokens}がTextGrid内に見つかりません"
    if len(match_starts) > 1:
        return None, f"マーカー語の並び{marker_tokens}が複数箇所で見つかりました(位置: {match_starts})"

    ne_first = match_starts[0]
    ne_last = ne_first + n - 1
    first_idx = non_empty[ne_first][0]
    last_idx = non_empty[ne_last][0]

    if ne_first == 0 or ne_last == len(non_empty) - 1:
        return None, "マーカー語の前後に単語が存在せず、直前・直後token順を確認できません"

    prev_idx = non_empty[ne_first - 1][0]
    next_idx = non_empty[ne_last + 1][0]
    prev_word = words[prev_idx]
    next_word = words[next_idx]

    if prev_word["text"] != "シュート":
        return None, f"マーカー語の直前token順を確認できません(期待: シュート, 実際: {prev_word['text']!r})"
    if next_word["text"] != "を":
        return None, f"マーカー語の直後token順を確認できません(期待: を, 実際: {next_word['text']!r})"

    return {
        "marker_token_count": n,
        "marker_tokens": list(marker_tokens),
        "marker_start_seconds": words[first_idx]["xmin"],
        "marker_end_seconds": words[last_idx]["xmax"],
        "marker_duration_seconds": round(words[last_idx]["xmax"] - words[first_idx]["xmin"], 4),
        "preceding_token": prev_word["text"],
        "preceding_start_seconds": prev_word["xmin"],
        "preceding_end_seconds": prev_word["xmax"],
        "following_token": next_word["text"],
        "following_start_seconds": next_word["xmin"],
        "following_end_seconds": next_word["xmax"],
    }, None

ARTICLE_ID = "A01"
VOICE_NAME = p3r.VOICE_NAME  # "Aoede"(既存採用済み仕様と同一)
build_style_prefix = p3r.build_style_prefix
build_tts_prompt = p3r.build_tts_prompt

SOURCE_INTEGRATED_SENTENCE = p3t.SOURCE_INTEGRATED_SENTENCE
SOURCE_JAPANESE_FULL_SENTENCE = p3t.SOURCE_JAPANESE_FULL_SENTENCE
SOURCE_ENGLISH_KEYWORD = p3t.SOURCE_ENGLISH_KEYWORD  # "shot on target"

# 承認済み原稿の語句・意味は変更しない。挿入位置を作るための一時的な
# 発話可能マーカー語のみを追加する(編集用であり完成音声には残さない)。
MARKER_TOKEN = "キーワード挿入位置"
_INSERTION_MARKER = "枠内シュートを記録できないまま"
_INSERTION_REPLACEMENT = f"枠内シュート、{MARKER_TOKEN}を記録できないまま"

# 既存のtrim済み英語音声を再利用する(再TTS生成しない)。
EXISTING_EN_TRIMMED_PATH = p3u.EXISTING_JA_PATH.replace(
    "b1_p3t/A01/raw/ja_full_sentence.wav",
    "b1_p3u/A01/components/en_shot_on_target_trimmed.wav",
)

BOUNDARY_PAUSE_SECONDS = p3u.BOUNDARY_PAUSE_SECONDS  # 0.12秒(P3Uと同一)
MAX_TTS_TECHNICAL_RETRY = 1

# MFA smoke test対象(既存のP3T日本語音声)
SMOKE_TEST_WAV_PATH = "er003_output/b1_p3t/A01/raw/ja_full_sentence.wav"
SMOKE_TEST_TEXT = SOURCE_JAPANESE_FULL_SENTENCE


def build_tts_marker_script(source_japanese_full_sentence: str = SOURCE_JAPANESE_FULL_SENTENCE) -> str:
    """承認済み日本語原稿の英語Key Phrase挿入位置へ、発話可能な一時
    マーカー語(MARKER_TOKEN)を追加する。語彙・語順・助詞は一切変更せず、
    挿入位置(「枠内シュート」と「を記録できないまま」の間)へマーカー語
    のみを追加する。この位置は元の統合原稿で英語Key Phraseがあった位置
    と同じである。"""
    if _INSERTION_MARKER not in source_japanese_full_sentence:
        raise ValueError("挿入位置のマーカーが日本語通し原稿内に見つかりません")
    return source_japanese_full_sentence.replace(_INSERTION_MARKER, _INSERTION_REPLACEMENT, 1)


def remove_marker_span(
    ja_samples: "object",
    sample_rate: int,
    marker_start_seconds: float,
    marker_end_seconds: float,
):
    """MFAで特定したmarker区間([marker_start_seconds, marker_end_seconds))
    を完全に削除し、その前後(前半・後半)を返す。区間の中身は一切
    再利用しない(マーカー語自体は完成音声に残さない)。"""
    if marker_end_seconds <= marker_start_seconds:
        raise ValueError("marker_end_secondsはmarker_start_secondsより後である必要があります")
    start_sample = max(0, int(round(marker_start_seconds * sample_rate)))
    end_sample = min(len(ja_samples), int(round(marker_end_seconds * sample_rate)))
    before = ja_samples[:start_sample]
    after = ja_samples[end_sample:]
    return before, after
