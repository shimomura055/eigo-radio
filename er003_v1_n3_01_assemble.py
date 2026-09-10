# ============================================================
# er003_v1_n3_01_assemble.py
# ER-003-A2-B1-N3-01: 3テーマ×2レベル Full Audio組み立て
# ============================================================
# B1: er003_v1_b1redesign_assemble04.py(v4、Point Notification直後
# pause除去済み)のtimeline構造をそのまま再利用する。
# A2: er003_v1_iran01_a2_audio04_generate.py(v4)のtimeline構造を
# そのまま再利用する。
# Shell共通のCharon文言(Welcome/Preview intro/Key phrases intro/
# Full story intro/num_one〜five)は、記事非依存の音声としてIRAN01の
# 既存ファイルをそのままコピーして再利用し、新規TTSは行わない
# (A2側はA01のservice-level共有ディレクトリを直接参照する、既存の
# A2アーキテクチャをそのまま踏襲)。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_n3_01_assemble.py <theme_id>
#   (theme_idを省略すると3テーマ全部を実行)

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
import time

import numpy as np

import er002_common as common
import er003_b1_p9a_audio as p9a
import er003_v1_b1_scaffold_audio_03_generate as audio03
import er003_v1_crosslevel_audio_02_common as c
import er003_v1_n3_01_articles_generate as gen
import er003_v1_n3_01_tts_generate as n3_tts

SR = p9a.TARGET_SAMPLE_RATE
POINT_NOTIFICATION_MP3_PATH = "C:/Users/tensh/eigo-radio/notification/universfield-new-notification-07-210334.mp3"

# B1既存のshared Charon shell音声(記事非依存、コピー元)
B1_SHARED_SOURCE_DIR = "er003_output/b1redesign_audio_01/IRAN01/narration"
B1_SHARED_NAMES = ("welcome_charon.wav", "preview_intro_charon.wav", "key_phrases_intro_charon.wav",
                    "full_story_intro_charon.wav", "num_one_charon.wav", "num_two_charon.wav",
                    "num_three_charon.wav", "num_four_charon.wav", "num_five_charon.wav")

# 既存Shellで確立済みのpause定数のみ再利用(新規値は作らない)。
NOTIFICATION_ENTRY_PAUSE_SECONDS = 0.5
HEADING_TO_BODY_PAUSE_SECONDS_B1 = audio03.POINT_EXPLANATION_PAUSE_SECONDS
AOEDE_TO_CHARON_PAUSE_SECONDS = audio03.COMMENT_EN_TO_JA_PAUSE_SECONDS
CHARON_TO_AOEDE_PAUSE_SECONDS = audio03.COMMENT_JA_TO_EN_PAUSE_SECONDS
IN_ONE_LINE_TO_OUTRO_PAUSE_SECONDS = audio03.IN_ONE_LINE_TO_OUTRO_PAUSE_SECONDS
OUTRO_EXTRA_GAIN_LINEAR = audio03.OUTRO_EXTRA_GAIN_LINEAR
OUTRO_FURTHER_EXTRA_GAIN_LINEAR = audio03.OUTRO_FURTHER_EXTRA_GAIN_LINEAR


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ============================================================
# ER-008-AUDIO-VALIDATION-GATE-AND-EVIDENCE-MAJOR-AUDIT-05 Part B〜E:
# Production全体向けの汎用Audio Validation Gate
# ============================================================
# 由来: ER-008-N7-CONTENT-AUDIO-QA-02で、B1 Key Phrase rank2の日本語gloss
# TTSがSTOPPEDになったにもかかわらず、assembly側がそれに気づかず、disk
# に残っていた前回実行(別のKey Phraseセット)の古い音声をそのまま使って
# しまう事故が実際に発生した。同種の事故はKey Phraseに限らず、全ての
# segment(Full Story/Point/Preview/Comment/In One Line等)で理論上
# 起こりうる(各TTS試行はASR検証前に無条件でファイルをdisk上書きする
# ため)。ここでは、Key Phrase専用だった旧verify_key_phrase_audio_
# integrity()を一般化し、tts_generation_results.json(このrunで書かれる
# 診断ファイル、既に全segment/Key Phraseの生成結果を含んでいる)に
# 記録された状態だけを正とする単一のgateへ統合する(重複実装を避ける、
# Part F)。
#
# ステータス語彙: VALIDATED(status=OK、reused含む)/ HUMAN_APPROVED
# (ASR_VALIDATION_UNCERTAINだが、canonical_textが変わっていない明示的
# Human Review記録がある)/ UNVALIDATED(承認記録の無いASR_VALIDATION_
# UNCERTAIN、または記録自体が無い)/ STOPPED。assembly許可はVALIDATED・
# HUMAN_APPROVEDのみ(Part D)。1件でも許可条件を満たさなければ
# EPISODE_BLOCKED_BY_AUDIO_VALIDATIONとしてRuntimeErrorを送出し、
# assembly全体を中止する(Part E・G、「とりあえず最後のWAVを使う」の禁止)。
#
# tts_generation_results.jsonを書かない旧pipeline/legacy scriptは対象外
# とし、何もしない(後方互換、Part H: 現行Production経路[本ファイル]
# のみを対象とする)。
AUDIO_GATE_ALLOWED_STATUSES = ("VALIDATED", "HUMAN_APPROVED")


def human_approval_path(out_dir: str) -> str:
    return f"{out_dir}/audit/human_approved_segments.json"


def record_human_approval(out_dir: str, segment_key: str, canonical_text: str, approved_by: str = "user") -> None:
    """Human Reviewで実際に聴取しPASSと判断したsegmentを記録する。
    canonical_textのsha256を保存し、後でtext自体が変わっていないかを
    照合する(記事本文が変わった後に古い承認を誤って使い回さないため)。"""
    path = human_approval_path(out_dir)
    approvals = load_json(path) if os.path.exists(path) else {}
    approvals[segment_key] = {
        "canonical_text_sha256": hashlib.sha256((canonical_text or "").encode("utf-8")).hexdigest(),
        "approved_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "approved_by": approved_by,
    }
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(approvals, f, ensure_ascii=False, indent=2)


def _segment_gate_status(entry: dict, segment_key: str, approvals: dict) -> str:
    if entry is None:
        return "UNVALIDATED"  # このrunに記録が無い(fail-closed)
    status = entry.get("status")
    if status == "OK":
        return "VALIDATED"
    # "HUMAN_REVIEW_LOCKED"はER-011のHuman Review Lockが後から追加した
    # status値で、record_human_approval()による承認確認の対象に含める
    # (このgateがER-011より先に実装されており、当初は未対応だった)。
    # "STOPPED"(3回試行してもASR検証に合格しなかった場合の終端状態)も
    # 同様に承認確認の対象に含める。ER-009-N1-LEDGER-DEVIATION-
    # RECALIBRATION-02のAudio段階(2026-08-30)で、STOPPEDのみ承認確認
    # 対象から漏れていたため(record_human_approval()自体はSTOPPEDを
    # 想定して設計されていたが、この関数側の分岐がASR_VALIDATION_
    # UNCERTAIN/HUMAN_REVIEW_LOCKEDしか見ていなかった)、ユーザー承認済み
    # segmentがブロックされ続ける実バグとして発見・修正した。
    if status in ("ASR_VALIDATION_UNCERTAIN", "HUMAN_REVIEW_LOCKED", "STOPPED"):
        approval = approvals.get(segment_key)
        if approval is not None:
            canon = entry.get("canonical_text") or entry.get("text") or ""
            if approval.get("canonical_text_sha256") == hashlib.sha256(canon.encode("utf-8")).hexdigest():
                return "HUMAN_APPROVED"
        return "STOPPED" if status == "STOPPED" else "UNVALIDATED"
    return "UNVALIDATED"


# ER-008-N8-FINAL-QA-HARDENING-21 Item 1: No.8完成版のA2 Key Phrase 2
# ("uneven choice")で、disfluency QA(er008_disfluency_qa_18)は
# PRODUCTION_WIREDと報告済みだったにもかかわらず、実際にAssembleへ採用
# されたkp2_en.wavにはdisfluency QAが一度も適用されていなかった。
#
# 原因調査の結論: kp2_en.wavはdisfluency QAがgenerate_key_phrase_
# component_verified()へ配線される前(commit bef70c1より約1日前)に
# Master Audio Store経由で生成されたasset で、tts_generation_results.
# jsonの記録もそのときのコード(disfluency_checkedフィールド自体が
# 存在しない旧形式)のまま残っていた。disfluency QA配線後、この記事の
# Assembleは同じ既存master(同一text/voice/model/style)をcache hit
# として再利用し続け、また本Gateはstatus=="OK"しか見ていなかったため、
# 「QA機能は実装済みだが、この特定assetには一度も適用されていない」
# という状態を検知できなかった(該当segmentがresumeやcache経由で
# 生成された場合も同様に発生し得る、A2 slowdown invariantと同型の
# 「必須post-process証跡の欠落」問題)。
#
# 対策: disfluency QA対象として承認済みの短文high-riskセグメント
# (Key Phrase英語/Point見出し/Preview・Comment・In One Line)については、
# status=="OK"だけでなく、そのsegmentの記録に
# disfluency_checked is True(top-level、後述の生成側修正で必ず記録
# されるようになった)が無ければAssembleをブロックする。これにより、
# QA配線前に作られた既存assetやresume/cache経由の取りこぼしは、
# 「証跡が無い」という理由で機械的にfail-closedされ、再生成を強制する。
#
# 重要: disfluency QA(faster-whisper)は英語専用の仕組みであり、A2の
# preview/comment_1-4は日本語音声(disfluency_checkedは常にFalseで
# 記録される、設計上パス不能)。level別に対象segmentを分ける必要が
# あり、level非依存の単一listにすると、A2側が恒久的にGateを通過
# できなくなる(この実装ミスはNo.8実データでの検証中に発見・修正した)。
DISFLUENCY_QA_MANDATORY_SEGMENTS_BY_LEVEL = {
    # EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PHASE1-01: 3V(3声
    # Voice構成)のNarrator見出しsegment`point_three_heading`を追加した
    # (既存"B1"キーへの1エントリ追加のみ、他は無変更)。point_three_heading
    # は既存point_one_heading/point_two_headingと同一の
    # `point_headings.generate()`(無変更)で生成されるため、同じ規約で
    # disfluency_checked記録が付く。A-Family/2V B-Familyのepisodeには
    # 存在しないsegment名のため、既存判定への影響はない
    # (er012_editorial_b_family_voices_3v_production_wiring_phase1_test_01.py
    # で非影響を固定)。
    "B1": ("preview", "comment_1", "comment_2", "comment_3", "comment_4",
           "in_one_line", "point_one_heading", "point_two_heading", "point_three_heading"),
    "A2": ("in_one_line", "point_one_heading", "point_two_heading"),
    # EDITORIAL-B-FAMILY-VOICES-A2-PRODUCTION-WIRING-01 Gate 3 item 7: B-Family
    # A2は標準A2と全く同じ3segment名(point_one_heading/two_heading/in_one_line、
    # いずれもNarrator=Aoede英語A2 slowdown対象)を使うため、標準A2と同一の対象
    # セットをそのまま登録する。B-FamilyのVoice A/B本文(point_one/point_two)は
    # generate_voice_body_wide_margin()がdisfluency gateをenabled=False固定で
    # 呼ぶため(B1 Phase1と共有、既存関数は無変更)対象に含めない(標準A2も
    # point_one/point_two本文は対象外のため対称)。Comment 1-4/Previewは日本語
    # 音声のため対象外(標準A2と同じ理由、上記コメント参照)。
    "B_FAMILY_A2": ("in_one_line", "point_one_heading", "point_two_heading"),
}


def _segment_missing_mandatory_disfluency_qa(name: str, entry: dict, level: str) -> bool:
    mandatory = DISFLUENCY_QA_MANDATORY_SEGMENTS_BY_LEVEL.get(level, ())
    if name not in mandatory and not name.endswith("_english"):
        return False
    return entry.get("disfluency_checked") is not True


# ER-008-N8-FINAL-QA-HARDENING-21 Item 7: 「validation recordだけで
# 判断しない」という今回の要求への対応。tts_generation_results.jsonに
# 記録されたsha256と、実際にnarration_dir上に存在するwavファイルの
# sha256を突き合わせ、不一致ならstaleとしてブロックする。これは今回の
# セッション自体がPoint-only regenerationの検証で行った「.bakから手動
# でarticle.md/parts.jsonを復元する」といった、JSON記録とファイル実体が
# 手動操作でズレるケースに対する一般的な安全網であり、disfluency QA
# 以外の全post-process(6% slowdown・calm style等)にも等しく効く。
def _segment_asset_hash_stale(entry: dict, narration_dir: str) -> bool:
    recorded_sha256 = entry.get("sha256")
    path = entry.get("path")
    if not recorded_sha256 or not path:
        return False
    full_path = path if os.path.isabs(path) or os.path.exists(path) else f"{narration_dir}/{os.path.basename(path)}"
    if not os.path.exists(full_path):
        return False
    with open(full_path, "rb") as f:
        actual_sha256 = hashlib.sha256(f.read()).hexdigest()
    return actual_sha256 != recorded_sha256


# OPEN-112-THEME2-AUDIO-REVIEW-FIX-02 サブタスクG: A2 Point Twoの
# Human Review accept経路(サブタスクE、`stage_assemble_a2()`は無変更)で
# 実際に発生した抜け穴の恒久修正に使う許容比率。ER-008-A2-TIMESTRETCH-
# ABC-10で承認された6% time-stretch(`er008_a2_postprocess_slowdown_01.
# A2_SLOWDOWN_PERCENT`)を反映した`{name}.wav`と`{name}_original.wav`の
# duration比は、既存Production実データ97件(全A2 slowdown対象segment、
# er006/er011配下)で実測すると1.0557〜1.0599に収まっており(mean
# 1.0557)、今回の抜け穴事例(無関係な旧`point_two_original.wav`が残存
# していたケース)は比率0.8126と明確に外れていた。ここでは実測分布に
# 十分な余裕を持たせつつ無関係ペアを弾けるレンジ[1.03, 1.09]を採用する。
_A2_SLOWDOWN_ORIGINAL_RATIO_MIN = 1.03
_A2_SLOWDOWN_ORIGINAL_RATIO_MAX = 1.09


def _segment_missing_mandatory_a2_slowdown(name: str, entry: dict, narration_dir: str = None) -> bool:
    """ER-008-N8-PRODUCTION-WIRING-AND-FOLLOWUP-19 Item 5-A: No.8
    point_one_headingが、Human Review Lock経由で承認された結果、6%
    time-stretchという必須post-processを一度も受けないままVALIDATED
    扱いでAssembleへ到達していた事故を受けた恒久対策。

    第一の証拠はtts_generation_results.jsonに記録された`slowdown_applied`
    フィールド(新規生成経路[generate_a2_segment_with_slowdown]が必ず
    記録する、最も明示的なevidence)。ただし横断調査で、No.8の他segment
    (full_story_part1/2・point_one・point_two・point_two_heading・
    in_one_line)は実際には6% slowdownを受けていた(`{name}_original.wav`
    が現存する)にもかかわらず、当時これらを扱った「resume」系script
    (既存fileから結果を引き継ぐ簡易script)がslowdown_appliedフィールド
    自体を記録していなかったことが判明した(音声は正しいが、metadataだけ
    が欠落している既存データの穴、新規バグではない)。この既存データを
    誤ってblockしないよう、`{name}_original.wav`が実際に存在することを
    第二の(やや弱いが独立した)evidenceとして受け入れる。新規生成経路は
    常に両方の証拠を残すため、この緩和は既存データの後方互換のみに効く。

    OPEN-112-THEME2-AUDIO-REVIEW-FIX-02サブタスクGで発見した抜け穴の
    恒久修正(2点): (1) `slowdown_applied`が明示的に`False`の場合(旧
    「resume」系scriptがフィールド自体を書かなかった=Noneのケースとは
    異なり、Human Review accept経路が「今回のattemptには未適用」と
    正直に記録した既知の事実)は、無関係な旧`{name}_original.wav`が
    存在するというだけの弱い証拠で上書きしてはならない(現に、この
    ケースでPoint Twoが誤って通過した)。フィールドが本当に存在しない
    (None、上記の既存後方互換対象)場合のみ、引き続きファイル存在を
    弱い証拠として認める。(2) その弱い証拠についても、単なる存在確認
    だけでなく、現在の`{name}.wav`との再生時間比が実際の6%
    time-stretch比率に整合しているか(`_A2_SLOWDOWN_ORIGINAL_RATIO_MIN`
    `_MAX`)を追加検証する。これにより、同名だが現在のattemptに対応
    しない無関係な旧originalファイル(duration比が大きく外れる)を
    誤ってevidence扱いしない。既存の`{name}_original.wav`存在チェック
    を置き換えるものであり、新規Validator・別台帳は追加していない。"""
    if name not in n3_tts.A2_SLOWDOWN_TARGET_SEGMENTS:
        return False
    recorded = entry.get("slowdown_applied")
    if recorded is True:
        return False
    if recorded is False:
        # 明示的に「今回のattemptには未適用」と記録されている場合、
        # 無関係な旧originalファイルの存在だけで見逃してはならない。
        return True
    if not narration_dir:
        return True
    original_path = f"{narration_dir}/{name}_original.wav"
    current_path = f"{narration_dir}/{name}.wav"
    if not (os.path.exists(original_path) and os.path.exists(current_path)):
        return True
    try:
        original_duration = n3_tts.a2_slowdown.read_wav_duration_seconds(original_path)
        current_duration = n3_tts.a2_slowdown.read_wav_duration_seconds(current_path)
        ratio = current_duration / original_duration
    except Exception:
        return True  # durationを読めない場合は安全側(missing扱い)に倒す
    if _A2_SLOWDOWN_ORIGINAL_RATIO_MIN <= ratio <= _A2_SLOWDOWN_ORIGINAL_RATIO_MAX:
        return False
    return True


# ============================================================
# OPEN-129-AUDIO-GATE-STRUCTURAL-COMPLETENESS-PRODUCTION-WIRING-01:
# opt-in(既定None=OFF、既存呼び出し元は全て無変更のためこの引数は渡され
# ない)。「entryの状態」ではなく「entry集合そのものの完全性」(丸ごと
# 欠落・余剰・voice割当の不一致)を検知する。reorderは検知対象外
# (segmentの順序はtimeline builder[build_b1_timeline/build_a2_timeline
# 等]が別途保証しており、tts_generation_results.jsonのdict順序自体は
# 現行アーキテクチャで意味を持たないため、OPEN-129-AUDIO-GATE-
# STRUCTURAL-COMPLETENESS-TRIAL-01のnegative controlどおり検知しない
# 仕様)。正本(何がrequired_segmentsか)はこの関数の外(B-Family:
# er012_b_family_editorial_type_registry_01.build_required_structure()、
# A-Family: 本ファイルのderive_a_family_required_structure())に置き、
# ここでは受け取ったrequired_structureを参照して検証するだけで、別の
# 正本は持たない。Key Phraseのsub-key名称(english/japanese_meaning等の
# schema drift)には依存せず、rank毎のsub-entry件数のみで判定する
# (Trial-01で確認済みの、命名drift由来のfalse reject回避策)。
# ============================================================
def _check_structural_completeness(data: dict, required_structure: dict) -> list:
    segs = data.get("segments") or {}
    kp = data.get("key_phrases") or {}
    expected_segments = required_structure["segments"]
    expected_names = {name for name, _ in expected_segments}
    problems = []

    for name, expected_voice in expected_segments:
        entry = segs.get(name)
        if entry is None:
            problems.append(f"{name}=MISSING(STRUCTURAL_COMPLETENESS)")
            continue
        actual_voice = entry.get("voice")
        if expected_voice is not None and actual_voice is not None and actual_voice != expected_voice:
            problems.append(f"{name}=VOICE_MISMATCH(expected={expected_voice} actual={actual_voice})"
                             "(STRUCTURAL_COMPLETENESS)")

    for name in sorted(n for n in segs if n not in expected_names):
        problems.append(f"{name}=UNEXPECTED_EXTRA_SEGMENT(STRUCTURAL_COMPLETENESS)")

    expected_ranks = {str(i) for i in range(1, required_structure["key_phrase_ranks"] + 1)}
    subkey_count = required_structure["key_phrase_subkey_count"]
    for rank_str in sorted(expected_ranks, key=int):
        sub = kp.get(rank_str)
        if sub is None:
            problems.append(f"kp{rank_str}=MISSING_KEY_PHRASE_RANK(STRUCTURAL_COMPLETENESS)")
            continue
        if len(sub) < subkey_count:
            problems.append(f"kp{rank_str}=INCOMPLETE_KEY_PHRASE_SUBENTRIES(has {len(sub)}, "
                             f"expected {subkey_count})(STRUCTURAL_COMPLETENESS)")
    for rank_str in sorted(r for r in kp if r not in expected_ranks):
        problems.append(f"kp{rank_str}=UNEXPECTED_EXTRA_KEY_PHRASE_RANK(STRUCTURAL_COMPLETENESS)")

    return problems


# A-Family用の期待構造(正本)。load_b1_sources()/load_a2_sources()/
# build_b1_timeline()/build_a2_timeline()が実際に読み込む・使うsegment名
# から導出した一覧(既存関数は無変更、新規追加のみ)。full_story_part1/2・
# point_one/point_twoは、既存Production実データ(n3_01 3テーマ・rerun_04)
# でvoiceフィールドが常にNone(未記録)であるため、expected_voice=Noneと
# して既知の後方互換として扱う(OPEN-129-AUDIO-GATE-STRUCTURAL-
# COMPLETENESS-TRIAL-01 Part 3と同じ扱い、false reject防止)。
A_FAMILY_B1_REQUIRED_SEGMENTS = (
    ("topic_intro", "Charon"), ("preview", "Charon"),
    ("comment_1", "Charon"), ("comment_2", "Charon"), ("comment_3", "Charon"), ("comment_4", "Charon"),
    ("point_one_heading", "Aoede"), ("point_two_heading", "Aoede"),
    ("full_story_part1", None), ("full_story_part2", None),
    ("point_one", None), ("point_two", None),
    ("in_one_line", None),
)
A_FAMILY_A2_REQUIRED_SEGMENTS = (
    ("topic_intro", "Aoede"), ("japanese_title", "Aoede"), ("preview", "Aoede"),
    ("comment_1", "Aoede"), ("comment_2", "Aoede"), ("comment_3", "Aoede"), ("comment_4", "Aoede"),
    ("point_one_heading", "Aoede"), ("point_two_heading", "Aoede"),
    ("full_story_part1", "Aoede"), ("full_story_part2", "Aoede"),
    ("point_one", "Aoede"), ("point_two", "Aoede"),
    ("in_one_line", "Aoede"),
)


def derive_a_family_required_structure(level: str) -> dict:
    """OPEN-129 opt-in引数向け。level="B1"/"A2"。A-Family用の正本はここ
    (このモジュール)に置き、Gate側(本ファイルの`verify_episode_audio_
    validation_gate`自身)は受け取った辞書を参照するだけ。"""
    if level == "B1":
        segs = A_FAMILY_B1_REQUIRED_SEGMENTS
    elif level == "A2":
        segs = A_FAMILY_A2_REQUIRED_SEGMENTS
    else:
        raise ValueError(f"unknown level for A-Family required structure: {level!r}")
    return {"segments": segs, "key_phrase_ranks": 5, "key_phrase_subkey_count": 2}


def verify_episode_audio_validation_gate(out_dir: str, level: str, required_structure: dict | None = None) -> None:
    result_path = f"{out_dir}/audit/tts_generation_results.json"
    if not os.path.exists(result_path):
        return
    data = load_json(result_path) or {}
    approvals_path = human_approval_path(out_dir)
    approvals = load_json(approvals_path) if os.path.exists(approvals_path) else {}
    narration_dir = f"{out_dir}/narration"

    blocked = []
    for name, entry in (data.get("segments") or {}).items():
        final = _segment_gate_status(entry, name, approvals)
        if final not in AUDIO_GATE_ALLOWED_STATUSES:
            blocked.append(f"{name}={final}")
            continue
        if level == "A2" and _segment_missing_mandatory_a2_slowdown(name, entry, narration_dir):
            blocked.append(f"{name}={final}(MISSING_MANDATORY_A2_SLOWDOWN)")
        if _segment_missing_mandatory_disfluency_qa(name, entry, level):
            blocked.append(f"{name}={final}(MISSING_MANDATORY_DISFLUENCY_QA)")
        if _segment_asset_hash_stale(entry, narration_dir):
            blocked.append(f"{name}={final}(ASSET_HASH_MISMATCH)")
    for rank, kp in (data.get("key_phrases") or {}).items():
        for sub_key, sub_entry in kp.items():
            seg_key = f"kp{rank}_{sub_key}"
            final = _segment_gate_status(sub_entry, seg_key, approvals)
            if final not in AUDIO_GATE_ALLOWED_STATUSES:
                blocked.append(f"{seg_key}={final}")
                continue
            if _segment_missing_mandatory_disfluency_qa(seg_key, sub_entry, level):
                blocked.append(f"{seg_key}={final}(MISSING_MANDATORY_DISFLUENCY_QA)")
            if _segment_asset_hash_stale(sub_entry, narration_dir):
                blocked.append(f"{seg_key}={final}(ASSET_HASH_MISMATCH)")

    if required_structure is not None:
        blocked.extend(_check_structural_completeness(data, required_structure))

    if blocked:
        raise RuntimeError(
            f"EPISODE_BLOCKED_BY_AUDIO_VALIDATION: {level}のepisode assemblyを中止し"
            f"ました。以下のsegmentが今回のrunでVALIDATED/HUMAN_APPROVED状態ではありま"
            f"せん、または必須post-processのevidenceがありません: {blocked}。未検証・"
            "stale・STOPPEDの音声、または6% slowdown等の必須post-processを経ていない"
            "音声をそのまま完成扱いにすることは許可されていません(ER-008-AUDIO-"
            "VALIDATION-GATE-AND-EVIDENCE-MAJOR-AUDIT-05、ER-008-N8-PRODUCTION-"
            "WIRING-AND-FOLLOWUP-19)。該当segmentを再生成するか、post-processを"
            "適用してから再度assemblyを実行してください。")


def copy_b1_shared_assets(narration_dir: str) -> None:
    for name in B1_SHARED_NAMES:
        dst = f"{narration_dir}/{name}"
        if not os.path.exists(dst):
            shutil.copyfile(f"{B1_SHARED_SOURCE_DIR}/{name}", dst)


# ============================================================
# B1組み立て
# ============================================================
def load_b1_sources(theme: dict) -> dict:
    out_dir = f"{theme['out_dir']}/b1b"
    narration_dir = f"{out_dir}/narration"
    verify_episode_audio_validation_gate(out_dir, "B1")
    copy_b1_shared_assets(narration_dir)

    intro = p9a.load_and_resample_to_target(p9a.INTRO_MP3_PATH)
    notification = p9a.load_and_resample_to_target(p9a.NOTIFICATION_MP3_PATH)
    point_notification = p9a.load_and_resample_to_target(POINT_NOTIFICATION_MP3_PATH)
    outro = p9a.load_and_resample_to_target(p9a.OUTRO_MP3_PATH)

    narration = {}
    for name in ("welcome", "preview_intro", "key_phrases_intro", "full_story_intro"):
        mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/{name}_charon.wav")
        assert sr == common.SAMPLE_RATE
        narration[name] = mono
    for name in ("num_one", "num_two", "num_three", "num_four", "num_five"):
        mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/{name}_charon.wav")
        assert sr == common.SAMPLE_RATE
        narration[name] = mono
    # topic_introは記事固有(N3-01 TTS生成scriptがtopic_intro.wavという
    # ファイル名で新規生成済み)なので、共有Charon shellのコピー元とは
    # 別に、記事ごとのnarration_dirから直接読み込む。
    mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/topic_intro.wav")
    assert sr == common.SAMPLE_RATE
    narration["topic_intro"] = mono

    b1_segments = {}
    for name in ("full_story_part1", "full_story_part2", "point_one", "point_two"):
        mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/{name}.wav")
        assert sr == common.SAMPLE_RATE
        b1_segments[name] = mono
    for name in ("comment_1", "comment_2", "comment_3", "comment_4", "preview"):
        mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/{name}.wav")
        assert sr == common.SAMPLE_RATE
        b1_segments[name] = mono
    mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/in_one_line.wav")
    assert sr == common.SAMPLE_RATE
    b1_segments["in_one_line"] = mono
    mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/point_one_heading.wav")
    assert sr == common.SAMPLE_RATE
    b1_segments["point_one_heading"] = mono
    mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/point_two_heading.wav")
    assert sr == common.SAMPLE_RATE
    b1_segments["point_two_heading"] = mono

    kp = load_json(f"{out_dir}/key_phrases/keywords_canonicalized.json")
    kp_items = sorted(kp["items"], key=lambda it: it["rank"])
    key_phrase_components, key_phrase_meanings = {}, {}
    for item in kp_items:
        rank = item["rank"]
        mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/kp{rank}_en.wav")
        # ER-008-N7-BASELINE-RESET-AND-MIDDLE-DEFER-01: ER-008-N7-MIDDLE-
        # SPEC-STORY-BALANCE-KEYPHRASE-AUDIT-01で追加したtight_speech_only()
        # trimming(A2側の頭無音除去と揃える調整)を、正式Baseline仕様へ
        # 戻すため一旦revertする。pause差の扱いは未確定のためDEFERRED
        # (OPEN_ITEMS.md参照)。
        key_phrase_components[rank] = mono
        mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/kp{rank}_ja_charon.wav")
        key_phrase_meanings[rank] = mono

    return {"intro": intro, "notification": notification, "point_notification": point_notification, "outro": outro,
            "narration": narration, "b1_segments": b1_segments,
            "key_phrase_components": key_phrase_components, "key_phrase_meanings": key_phrase_meanings,
            "kp_items": kp_items}


def apply_b1_gain(sources: dict) -> dict:
    preview_mono = sources["b1_segments"]["preview"]
    full_story_part1_mono = sources["b1_segments"]["full_story_part1"]
    target_rms = (p9a.rms(preview_mono) + p9a.rms(full_story_part1_mono)) / 2
    gain_report = {"target_rms": round(target_rms, 5)}

    def gain_to_rms(data, target, label):
        gain = p9a.compute_gain_for_target_rms(data, target)
        gained = data * gain
        gain_report[label] = {"gain": round(float(gain), 4), "rms_before": round(p9a.rms(data), 5),
                               "rms_after": round(p9a.rms(gained), 5), "peak_after": round(p9a.peak(gained), 5)}
        return gained

    result = {}
    result["intro"] = gain_to_rms(sources["intro"]["samples"], target_rms, "intro")
    result["notification"] = gain_to_rms(sources["notification"]["samples"], target_rms, "notification")
    result["point_notification"] = gain_to_rms(
        sources["point_notification"]["samples"], target_rms, "point_notification")

    intro_final_rms = p9a.rms(result["intro"])
    outro_matched = sources["outro"]["samples"] * p9a.compute_gain_for_target_rms(
        sources["outro"]["samples"], intro_final_rms)
    outro_v2 = outro_matched * OUTRO_EXTRA_GAIN_LINEAR
    outro_v3 = outro_v2 * OUTRO_FURTHER_EXTRA_GAIN_LINEAR
    result["outro"] = outro_v3
    gain_report["outro"] = {
        "matched_to": "intro_post_gain_rms", "intro_post_gain_rms": round(intro_final_rms, 5),
        "rms_after_match": round(p9a.rms(outro_matched), 5),
        "rms_final": round(p9a.rms(outro_v3), 5), "peak_final": round(p9a.peak(outro_v3), 5),
    }

    result["preview"] = p9a.mono_24k_to_stereo_target(preview_mono)
    gain_report["preview"] = {"gain": 1.0, "note": "無加工(RMSアンカー)"}

    for name, mono in sources["narration"].items():
        gained = gain_to_rms(mono, target_rms, name)
        result[name] = p9a.mono_24k_to_stereo_target(gained)

    key_phrase_stereo, key_phrase_meaning_stereo = {}, {}
    for rank, mono in sources["key_phrase_components"].items():
        gained = gain_to_rms(mono, target_rms, f"key_phrase_en_{rank}")
        key_phrase_stereo[rank] = p9a.mono_24k_to_stereo_target(gained)
    for rank, mono in sources["key_phrase_meanings"].items():
        gained = gain_to_rms(mono, target_rms, f"key_phrase_ja_{rank}")
        key_phrase_meaning_stereo[rank] = p9a.mono_24k_to_stereo_target(gained)
    result["key_phrase_components"] = key_phrase_stereo
    result["key_phrase_meanings"] = key_phrase_meaning_stereo

    b1_stereo = {}
    for name, mono in sources["b1_segments"].items():
        if name == "preview":
            continue
        gained = gain_to_rms(mono, target_rms, f"b1_{name}")
        b1_stereo[name] = p9a.mono_24k_to_stereo_target(gained)
    b1_stereo["preview"] = result["preview"]
    result["b1_segments"] = b1_stereo

    result["kp_items"] = sources["kp_items"]
    result["gain_report"] = gain_report
    return result


def build_b1_key_phrase_blocks(parts: dict) -> list:
    num_names = ["num_one", "num_two", "num_three", "num_four", "num_five"]
    blocks = []
    for item in parts["kp_items"]:
        rank = item["rank"]
        num_key = num_names[rank - 1]
        block = p9a.build_key_phrase_block(
            parts[num_key], parts["key_phrase_components"][rank], parts["key_phrase_meanings"][rank], SR)
        blocks.append(block)
    return blocks


def build_b1_timeline(parts: dict) -> list:
    key_phrase_blocks = build_b1_key_phrase_blocks(parts)
    b1 = parts["b1_segments"]

    seq = [
        ("Intro", parts["intro"]),
        ("Welcome (Charon)", parts["welcome"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
        ("Topic intro (Charon)", parts["topic_intro"]),
        ("pause_0.65", p9a.silence_stereo(0.65)),
        ("Notification 1", parts["notification"]),
        ("pause_0.4", p9a.silence_stereo(0.4)),
        ("Preview intro (Charon)", parts["preview_intro"]),
        ("pause_0.65", p9a.silence_stereo(0.65)),
        ("Preview (Charon)", b1["preview"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
        ("Notification 2", parts["notification"]),
        ("pause_0.4", p9a.silence_stereo(0.4)),
        ("Key phrases intro (Charon)", parts["key_phrases_intro"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
    ]
    kp_labels = tuple(f"Key Phrase {i}" for i in range(1, len(key_phrase_blocks) + 1))
    for label, block in zip(kp_labels, key_phrase_blocks):
        seq.append((label, block))

    seq += [
        ("Notification 3", parts["notification"]),
        ("pause_0.4", p9a.silence_stereo(0.4)),
        ("Full story intro (Charon)", parts["full_story_intro"]),
        ("pause_1.0", p9a.silence_stereo(AOEDE_TO_CHARON_PAUSE_SECONDS)),
        ("Comment 1 (Charon)", b1["comment_1"]),
        ("pause_0.8", p9a.silence_stereo(CHARON_TO_AOEDE_PAUSE_SECONDS)),
        ("Full Story Part 1 (Aoede)", b1["full_story_part1"]),
        ("pause_1.0", p9a.silence_stereo(AOEDE_TO_CHARON_PAUSE_SECONDS)),
        ("Comment 2 (Charon)", b1["comment_2"]),
        ("pause_0.8", p9a.silence_stereo(CHARON_TO_AOEDE_PAUSE_SECONDS)),
        ("Full Story Part 2 (Aoede)", b1["full_story_part2"]),
        ("pause_1.0", p9a.silence_stereo(AOEDE_TO_CHARON_PAUSE_SECONDS)),
        ("Comment 3 (Charon, Bridge)", b1["comment_3"]),
        ("pause_0.5_notification_entry", p9a.silence_stereo(NOTIFICATION_ENTRY_PAUSE_SECONDS)),
        ("Point Notification (Point One cue)", parts["point_notification"]),
        ("Point One semantic heading (Aoede)", b1["point_one_heading"]),
        ("pause_0.7_heading_to_body", p9a.silence_stereo(HEADING_TO_BODY_PAUSE_SECONDS_B1)),
        ("Point One (Aoede)", b1["point_one"]),
        ("pause_0.5_notification_entry", p9a.silence_stereo(NOTIFICATION_ENTRY_PAUSE_SECONDS)),
        ("Point Notification (Point Two cue)", parts["point_notification"]),
        ("Point Two semantic heading (Aoede)", b1["point_two_heading"]),
        ("pause_0.7_heading_to_body", p9a.silence_stereo(HEADING_TO_BODY_PAUSE_SECONDS_B1)),
        ("Point Two (Aoede)", b1["point_two"]),
        ("pause_1.0", p9a.silence_stereo(AOEDE_TO_CHARON_PAUSE_SECONDS)),
        ("Comment 4 (Charon)", b1["comment_4"]),
        ("pause_0.8", p9a.silence_stereo(CHARON_TO_AOEDE_PAUSE_SECONDS)),
        ("In One Line (Aoede)", b1["in_one_line"]),
        ("pause_0.8_in_one_line_to_outro", p9a.silence_stereo(IN_ONE_LINE_TO_OUTRO_PAUSE_SECONDS)),
        ("Outro (Charon)", parts["outro"]),
    ]
    return seq


# ============================================================
# A2組み立て
# ============================================================
def load_a2_sources(theme: dict) -> dict:
    out_dir = f"{theme['out_dir']}/a2"
    narration_dir = f"{out_dir}/narration"
    verify_episode_audio_validation_gate(out_dir, "A2")

    intro = p9a.load_and_resample_to_target(p9a.INTRO_MP3_PATH)
    notification = p9a.load_and_resample_to_target(p9a.NOTIFICATION_MP3_PATH)
    point_notification = p9a.load_and_resample_to_target(POINT_NOTIFICATION_MP3_PATH)
    outro = p9a.load_and_resample_to_target(p9a.OUTRO_MP3_PATH)

    preview_mono, preview_sr, _, _ = common.read_wav_float(f"{narration_dir}/preview.wav")
    assert preview_sr == common.SAMPLE_RATE

    narration = {}
    for name in c.SERVICE_LEVEL_NARRATION_NAMES:
        mono, sr, _, _ = common.read_wav_float(f"{c.A01_NARRATION_DIR}/{name}.wav")
        assert sr == common.SAMPLE_RATE
        narration[name] = mono
    for name in ("topic_intro", "japanese_title"):
        mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/{name}.wav")
        assert sr == common.SAMPLE_RATE
        narration[name] = mono

    kp = load_json(f"{out_dir}/key_phrases/keywords_canonicalized.json")
    kp_items = sorted(kp["items"], key=lambda it: it["rank"])
    for i in range(1, len(kp_items) + 1):
        mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/meaning_{i}.wav")
        assert sr == common.SAMPLE_RATE
        narration[f"meaning_{i}"] = mono

    key_phrase_components = {}
    for item in kp_items:
        rank = item["rank"]
        mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/kp{rank}_en.wav")
        # ER-011-NO18-A2-TIGHT-SPEECH-AND-TRIM030-PRODUCTION-WIRING-23:
        # generation-time KEY_PHRASE_TRIM_SAFETY_MARGIN_SECONDS(0.30秒、
        # er003_v1_repro01_main_generate.py)で確保した終端marginを、
        # ここでtight_speech_only()により再cropしていたため、No.18 A2
        # kp5「be powered off」の語末/f/がmargin無しの状態でAssembleに
        # 渡っていた(Trial-15で発見、ユーザー試聴・承認済み)。B1側は
        # ER-008-N7-BASELINE-RESET-AND-MIDDLE-DEFER-01で既にこの再crop
        # を行わない仕様(上のload_b1_sources()参照)であり、この変更で
        # A2もB1と同じ「generation-time marginをそのままAssembleへ渡す」
        # 仕様に揃う。tight_speech_only()の関数定義自体
        # (er003_b1_p7c_audio.py)は他script参照があるため削除しない。
        key_phrase_components[rank] = mono

    a2_segments = {}
    for name in ("comment_1", "comment_2", "comment_3", "comment_4", "full_story_part1", "full_story_part2",
                  "point_one", "point_two", "point_one_heading", "point_two_heading", "in_one_line"):
        mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/{name}.wav")
        assert sr == common.SAMPLE_RATE
        a2_segments[name] = mono

    return {
        "intro": intro, "notification": notification, "point_notification": point_notification, "outro": outro,
        "preview_mono": preview_mono, "narration": narration,
        "key_phrase_components": key_phrase_components, "a2_segments": a2_segments, "kp_items": kp_items,
    }


def apply_a2_gain(sources: dict) -> dict:
    target_rms = (p9a.rms(sources["preview_mono"]) + p9a.rms(sources["a2_segments"]["full_story_part1"])) / 2
    gain_report = {"target_rms": round(target_rms, 5)}

    def gain_to_rms(data, target, label):
        gain = p9a.compute_gain_for_target_rms(data, target)
        gained = data * gain
        gain_report[label] = {"gain": round(float(gain), 4), "rms_before": round(p9a.rms(data), 5),
                              "rms_after": round(p9a.rms(gained), 5), "peak_after": round(p9a.peak(gained), 5)}
        return gained

    result = {}
    result["intro"] = gain_to_rms(sources["intro"]["samples"], target_rms, "intro")
    result["notification"] = gain_to_rms(sources["notification"]["samples"], target_rms, "notification")
    result["point_notification"] = gain_to_rms(
        sources["point_notification"]["samples"], target_rms, "point_notification")

    intro_final_rms = p9a.rms(result["intro"])
    outro_matched = sources["outro"]["samples"] * p9a.compute_gain_for_target_rms(
        sources["outro"]["samples"], intro_final_rms)
    outro_final = outro_matched * OUTRO_EXTRA_GAIN_LINEAR
    result["outro"] = outro_final
    gain_report["outro"] = {
        "matched_to": "intro_post_gain_rms", "intro_post_gain_rms": round(intro_final_rms, 5),
        "rms_after_match": round(p9a.rms(outro_matched), 5),
        "extra_gain_linear": round(float(OUTRO_EXTRA_GAIN_LINEAR), 4),
        "rms_final": round(p9a.rms(outro_final), 5), "peak_final": round(p9a.peak(outro_final), 5),
    }

    result["preview"] = p9a.mono_24k_to_stereo_target(sources["preview_mono"])

    for name, mono in sources["narration"].items():
        gained = gain_to_rms(mono, target_rms, name)
        result[name] = p9a.mono_24k_to_stereo_target(gained)

    key_phrase_stereo = {}
    for number, mono in sources["key_phrase_components"].items():
        gained = gain_to_rms(mono, target_rms, f"key_phrase_en_{number}")
        key_phrase_stereo[number] = p9a.mono_24k_to_stereo_target(gained)
    result["key_phrase_components"] = key_phrase_stereo

    a2_stereo = {}
    for name, mono in sources["a2_segments"].items():
        gained = gain_to_rms(mono, target_rms, f"a2_{name}")
        a2_stereo[name] = p9a.mono_24k_to_stereo_target(gained)
    result["a2_segments"] = a2_stereo

    gain_report["preview"] = {"gain": 1.0, "note": "無加工(新規Preview音声を保持)"}
    result["kp_items"] = sources["kp_items"]
    result["gain_report"] = gain_report
    return result


# ER-008-N7-CONTENT-AUDIO-QA-02 Part B(+0.1秒)→ER-008-EVIDENCE-
# COMPRESSION-PROD-AND-N7-AUDIO-06 Part E(さらに+0.1秒、ユーザー確認
# 済み)。A2の番号読み上げ→Key Phrase本体の間だけ、既存のKEY_PHRASE_
# INTERNAL_PAUSE_SECONDS(0.4秒)より合計+0.2秒長くする(元Baseline比、
# B1は変更しない、= p9a.KEY_PHRASE_INTERNAL_PAUSE_SECONDSのまま)。将来
# Middle再開時にA2のKey Phraseをそのまま使う仕様のため、Middleもこの値を
# 自動的に継承する。
A2_KEY_PHRASE_NUMBERING_PAUSE_SECONDS = p9a.KEY_PHRASE_INTERNAL_PAUSE_SECONDS + 0.2


def build_a2_key_phrase_blocks(parts: dict) -> list:
    num_names = ["num_one", "num_two", "num_three", "num_four", "num_five"]
    blocks = []
    for i, item in enumerate(parts["kp_items"]):
        rank = item["rank"]
        num_key = num_names[i]
        meaning_key = f"meaning_{i + 1}"
        block = p9a.build_key_phrase_block(
            parts[num_key], parts["key_phrase_components"][rank], parts[meaning_key], SR,
            numbering_pause_seconds=A2_KEY_PHRASE_NUMBERING_PAUSE_SECONDS)
        blocks.append(block)
    return blocks


def build_a2_timeline(parts: dict) -> list:
    key_phrase_blocks = build_a2_key_phrase_blocks(parts)
    a2 = parts["a2_segments"]

    seq = [
        ("Intro", parts["intro"]),
        ("Welcome", parts["welcome"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
        ("Topic intro", parts["topic_intro"]),
        ("pause_0.65", p9a.silence_stereo(0.65)),
        ("Japanese title", parts["japanese_title"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
        ("Notification 1", parts["notification"]),
        ("pause_0.4", p9a.silence_stereo(0.4)),
        ("Preview intro", parts["preview_intro"]),
        ("pause_0.65", p9a.silence_stereo(0.65)),
        ("Point explanation", parts["point_explanation"]),
        ("pause_0.7_point_explanation", p9a.silence_stereo(c.POINT_EXPLANATION_PAUSE_SECONDS)),
        ("Preview", parts["preview"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
        ("Notification 2", parts["notification"]),
        ("pause_0.4", p9a.silence_stereo(0.4)),
        ("Key phrases intro", parts["key_phrases_intro"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
    ]
    kp_labels = tuple(f"Key Phrase {i + 1}" for i in range(len(key_phrase_blocks)))
    for label, block in zip(kp_labels, key_phrase_blocks):
        seq.append((label, block))

    seq += [
        ("Notification 3", parts["notification"]),
        ("pause_0.4", p9a.silence_stereo(0.4)),
        ("Full story intro", parts["full_story_intro"]),
        ("pause_1.0_en_to_ja", p9a.silence_stereo(1.0)),
        ("Comment 1", a2["comment_1"]),
        ("pause_0.8_ja_to_en", p9a.silence_stereo(0.8)),
        ("Full Story Part 1", a2["full_story_part1"]),
        ("pause_1.0_en_to_ja", p9a.silence_stereo(1.0)),
        ("Comment 2", a2["comment_2"]),
        ("pause_0.8_ja_to_en", p9a.silence_stereo(0.8)),
        ("Full Story Part 2", a2["full_story_part2"]),
        ("pause_1.0_en_to_ja", p9a.silence_stereo(1.0)),
        ("Comment 3", a2["comment_3"]),
        ("pause_0.5_notification_entry", p9a.silence_stereo(NOTIFICATION_ENTRY_PAUSE_SECONDS)),
        ("Point Notification (Point One cue)", parts["point_notification"]),
        ("Point One semantic heading", a2["point_one_heading"]),
        ("pause_0.7_heading_to_body", p9a.silence_stereo(c.POINT_EXPLANATION_PAUSE_SECONDS)),
        ("Point One", a2["point_one"]),
        ("pause_0.5_notification_entry", p9a.silence_stereo(NOTIFICATION_ENTRY_PAUSE_SECONDS)),
        ("Point Notification (Point Two cue)", parts["point_notification"]),
        ("Point Two semantic heading", a2["point_two_heading"]),
        ("pause_0.7_heading_to_body", p9a.silence_stereo(c.POINT_EXPLANATION_PAUSE_SECONDS)),
        ("Point Two", a2["point_two"]),
        ("pause_1.0_en_to_ja", p9a.silence_stereo(1.0)),
        ("Comment 4", a2["comment_4"]),
        ("pause_0.8_ja_to_en", p9a.silence_stereo(0.8)),
        ("In One Line", a2["in_one_line"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
        ("Outro", parts["outro"]),
    ]
    return seq


# ============================================================
# 共通組み立てヘルパー
# ============================================================
def assemble_with_timeline(seq: list) -> dict:
    pieces = [samples for _, samples in seq]
    assembled = np.ascontiguousarray(np.concatenate(pieces, axis=0))
    timeline = []
    t = 0.0
    for name, samples in seq:
        dur = len(samples) / SR
        timeline.append({"part": name, "start_seconds": round(t, 3), "duration_seconds": round(dur, 3)})
        t += dur
    return {"assembled": assembled, "timeline": timeline, "total_duration_seconds": round(t, 3)}


# ============================================================
# ER-011-ASSEMBLY-HEADROOM-SAFETY-VALVE-PRODUCTION-WIRING-01
# ============================================================
# 由来(OPEN-115、実測確定はOPEN-112-TREND-THEME2-B-A2-PEAK-MEASUREMENT-16):
# apply_a2_gain/apply_b1_gain内のcompute_gain_for_target_rms(max_peak=0.95)
# は、各segmentを24kHz mono・gain適用直後の時点でのみpeak<=0.95に制限する。
# その直後にmono_24k_to_stereo_target()が行うresample_poly(24kHz→48kHz)
# はゲイン制御の外にあり、内容(語頭の破裂音・強勢等)依存で最大+8.9%程度
# のオーバーシュートを起こす(Trial-13 A2のPoint Oneで実測: 0.95000→
# 1.03502)。assemble_with_timeline()はnp.concatenateのみ(重ね合わせ無し)
# のため、完成ミックス全体のpeakは常にseq中いずれかのpieceのpeakと一致する
# (計測-16で実測確認済みの構造)。ここでは、完成ミックスのpeakが
# HEADROOM_PEAK_THRESHOLDを超えたときだけ、エピソード全体へ一律スカラー
# gainを掛けて閾値以内へ収める(相対バランスは変えない)。閾値以下なら
# 一切変更せず、渡されたassembled配列をそのまま返す(byte同一を保証)。
# 安全弁適用後もなおpeakが1.0を超える異常時は、write_wav_float()の
# assertに到達させず、原因pieceを含むドメイン例外(RuntimeError)で
# 停止する(write_wav_float()側のassert自体は最後の砦として残す)。
# 安全≠成功原則(PM_GOVERNANCE.md)により、適用有無・適用前後peak・
# スカラー値・原因pieceは必ず戻り値のreportへ記録し、呼び出し側が
# gain_report.json/headroom_report.json/run_summary_assemble.jsonへ
# 書き出す(静かに救済しない)。
HEADROOM_PEAK_THRESHOLD = 0.98


def apply_headroom_safety_valve(assembled: "np.ndarray", seq: list) -> dict:
    peak_before = float(np.max(np.abs(assembled))) if len(assembled) else 0.0

    # 原因piece特定: np.concatenateのみのAssemblyでは、完成ミックスの
    # peakは必ずseq中いずれかのpieceのpeakと一致するため、最大peakの
    # pieceをそのまま原因として報告できる(計測-16の実測構造どおり)。
    piece_peaks = [(name, float(np.max(np.abs(samples))) if len(samples) else 0.0) for name, samples in seq]
    cause_name, cause_peak = max(piece_peaks, key=lambda t: t[1]) if piece_peaks else (None, 0.0)

    report = {
        "threshold": HEADROOM_PEAK_THRESHOLD,
        "peak_before": round(peak_before, 7),
        "cause_piece": cause_name,
        "cause_piece_peak": round(cause_peak, 7),
    }

    if peak_before <= HEADROOM_PEAK_THRESHOLD:
        report["applied"] = False
        report["scalar"] = 1.0
        report["peak_after"] = round(peak_before, 7)
        return {"assembled": assembled, "report": report}

    scalar = HEADROOM_PEAK_THRESHOLD / peak_before
    scaled = assembled * scalar
    peak_after = float(np.max(np.abs(scaled))) if len(scaled) else 0.0
    report["applied"] = True
    report["scalar"] = round(float(scalar), 8)
    report["peak_after"] = round(peak_after, 7)

    if peak_after > 1.0:
        raise RuntimeError(
            "ASSEMBLY_HEADROOM_SAFETY_VALVE_INSUFFICIENT: ヘッドルーム安全弁"
            f"(閾値{HEADROOM_PEAK_THRESHOLD}、scalar={report['scalar']})を適用した後も"
            f"peak={peak_after}が1.0を超えています。原因piece候補: "
            f"{cause_name}(適用前peak={cause_peak})。Assemblyを中止しました"
            "(ER-011-ASSEMBLY-HEADROOM-SAFETY-VALVE-PRODUCTION-WIRING-01)。")

    return {"assembled": scaled, "report": report}


def stage_assemble_b1(theme: dict) -> dict:
    out_dir = f"{theme['out_dir']}/b1b"
    os.makedirs(f"{out_dir}/assembled", exist_ok=True)
    os.makedirs(f"{out_dir}/audit", exist_ok=True)
    sources = load_b1_sources(theme)
    parts = apply_b1_gain(sources)
    seq = build_b1_timeline(parts)
    result = assemble_with_timeline(seq)
    headroom = apply_headroom_safety_valve(result["assembled"], seq)
    assembled = headroom["assembled"]

    out_path = f"{out_dir}/assembled/English_Your_Way_B1B_{theme['theme_id'].upper()}.wav"

    # ER-011-ASSEMBLY-HEADROOM-SAFETY-VALVE-PRODUCTION-WIRING-01: 診断性
    # 改善のため、gain_report/timeline/headroom_reportをwrite_wav_float()
    # (クリッピング防止assertを持つ)より前に書き出す。
    with open(f"{out_dir}/audit/gain_report.json", "w", encoding="utf-8") as f:
        json.dump(parts["gain_report"], f, ensure_ascii=False, indent=2)
    with open(f"{out_dir}/audit/timeline.json", "w", encoding="utf-8") as f:
        json.dump(result["timeline"], f, ensure_ascii=False, indent=2)
    with open(f"{out_dir}/audit/headroom_report.json", "w", encoding="utf-8") as f:
        json.dump(headroom["report"], f, ensure_ascii=False, indent=2)

    common.write_wav_float(out_path, assembled, SR, 2)
    metrics = common.measure_metrics(assembled[:, 0], SR)

    summary = {
        "status": "OK", "out_path": out_path, "duration_seconds": result["total_duration_seconds"],
        "clipping_detected": metrics["clipping_detected"], "peak": round(p9a.peak(assembled), 5),
        "sample_rate": SR, "channels": 2, "headroom_safety_valve": headroom["report"],
    }
    with open(f"{out_dir}/run_summary_assemble.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    print(f"[N3-ASSEMBLE][{theme['theme_id']}/b1b] status={summary['status']} "
          f"duration={summary['duration_seconds']} peak={summary['peak']} clipping={summary['clipping_detected']} "
          f"headroom_applied={headroom['report']['applied']}")
    return summary


def stage_assemble_a2(theme: dict) -> dict:
    out_dir = f"{theme['out_dir']}/a2"
    os.makedirs(f"{out_dir}/assembled", exist_ok=True)
    os.makedirs(f"{out_dir}/audit", exist_ok=True)
    sources = load_a2_sources(theme)
    parts = apply_a2_gain(sources)
    seq = build_a2_timeline(parts)
    result = assemble_with_timeline(seq)
    headroom = apply_headroom_safety_valve(result["assembled"], seq)
    assembled = headroom["assembled"]

    out_path = f"{out_dir}/assembled/English_Your_Way_A2_{theme['theme_id'].upper()}.wav"

    # ER-011-ASSEMBLY-HEADROOM-SAFETY-VALVE-PRODUCTION-WIRING-01: 診断性
    # 改善のため、gain_report/timeline/headroom_reportをwrite_wav_float()
    # (クリッピング防止assertを持つ)より前に書き出す。
    with open(f"{out_dir}/audit/gain_report.json", "w", encoding="utf-8") as f:
        json.dump(parts["gain_report"], f, ensure_ascii=False, indent=2)
    with open(f"{out_dir}/audit/timeline.json", "w", encoding="utf-8") as f:
        json.dump(result["timeline"], f, ensure_ascii=False, indent=2)
    with open(f"{out_dir}/audit/headroom_report.json", "w", encoding="utf-8") as f:
        json.dump(headroom["report"], f, ensure_ascii=False, indent=2)

    common.write_wav_float(out_path, assembled, SR, 2)
    metrics = common.measure_metrics(assembled[:, 0], SR)

    summary = {
        "status": "OK", "out_path": out_path, "duration_seconds": result["total_duration_seconds"],
        "clipping_detected": metrics["clipping_detected"], "peak": round(p9a.peak(assembled), 5),
        "sample_rate": SR, "channels": 2, "headroom_safety_valve": headroom["report"],
    }
    with open(f"{out_dir}/run_summary_assemble.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    print(f"[N3-ASSEMBLE][{theme['theme_id']}/a2] status={summary['status']} "
          f"duration={summary['duration_seconds']} peak={summary['peak']} clipping={summary['clipping_detected']} "
          f"headroom_applied={headroom['report']['applied']}")
    return summary


def run_theme(theme: dict) -> dict:
    b1_result = stage_assemble_b1(theme)
    a2_result = stage_assemble_a2(theme)
    return {"b1b": b1_result, "a2": a2_result}


def main():
    theme_ids = sys.argv[1:] or [t["theme_id"] for t in gen.THEMES]
    themes_by_id = {t["theme_id"]: t for t in gen.THEMES}
    for theme_id in theme_ids:
        run_theme(themes_by_id[theme_id])
    print("[N3-ASSEMBLE] 完了。")


if __name__ == "__main__":
    main()
