# ============================================================
# er002_runner.py
# ER-002: 記事単位の実験ランナー(本番パイプラインとは分離)
# ============================================================
# 実APIを直接呼び出さない。script_write_fn / tts_call_fn / qa_call_fn は
# すべて呼び出し側が注入するコーラブルであり、ER-002-S1/S1.1時点では
# テスト用のモックのみを渡している(実トピック取得・実TTS・実QAは一切
# 実行していない)。
#
# generate_test.py(本番の記事生成パイプライン)は直接importしていない。
# 理由:
#   generate_test.pyはモジュールトップレベルで
#     - OpenAIクライアントを生成する(`client = OpenAI()`)
#     - `--level=`/`--topic=`のCLI引数が無いとSystemExitする
#   という作りになっており、`if __name__ == "__main__":` によるガードも
#   無いため、安全にimportできるライブラリ構造になっていない。import
#   しただけでテスト実行が落ちる、または意図しない副作用を招く恐れがある。
#   そのためER-002は台本生成をscript_write_fnという差し替え可能な
#   インターフェースの背後に隠し、generate_test.pyとの実際の接続方法
#   (直接拡張するか、アダプター経由にするか)は実際のAPI呼び出しを伴う
#   判断になるため、実API呼び出しを行うS2以降へ持ち越す(ER-002-S0での
#   報告どおり)。
#
# ER-002-S2の対象訂正(ER-002-S1.1時点の記録):
#   S2はA01/A02の独立再現性検証ではなく、以下を使用する。
#     - article_id: A04 / genre: technology
#     - 話者: AoedeとCharonの2話者、同一の英語台本を両方へ使用
#     - A/B匿名化を実施(build_ab_bundleを使用)
#   A01/A02の独立再実行(機械的再現性の確認)は本番バッチ工程で行う。
#   この工程(S1.1)ではS2の実API実行そのものは行っていない。
#
# 生成音声は既存の.gitignore方針(*.wav)に従いGit追跡対象外。
# er002_output/配下のJSON成果物(manifest.json等)はGit追跡対象
# (ER-002-S1.1でer002_output/の一括除外を廃止)。

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict, dataclass, is_dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Optional

import er002_ab_anonymize as ab
import er002_common as common


def _to_jsonable(obj: Any) -> Any:
    if is_dataclass(obj) and not isinstance(obj, type):
        return _to_jsonable(asdict(obj))
    if isinstance(obj, dict):
        return {k: _to_jsonable(v) for k, v in obj.items() if k != "audio"}
    if isinstance(obj, list):
        return [_to_jsonable(v) for v in obj]
    if isinstance(obj, bytes):
        return f"<{len(obj)} bytes>"
    return obj


@dataclass
class ArticleRunOutcome:
    manifest: dict
    c1_samples: Any = None  # numpy配列。status=="OK"の場合のみ設定
    written_files: dict = None  # {filename: path} (output_dir指定時のみ)


REQUIRED_CONFIG_KEYS = [
    "experiment_id", "article_id", "genre", "topic_or_source", "voice",
]

# configで渡された場合にのみ書き出す、S1.1時点では未生成の成果物
# (トピック取得・日本語台本・情報源等はER-002のこの工程では実行しない)
OPTIONAL_PASSTHROUGH_ARTIFACTS = {
    "topic_candidates": "topic_candidates.json",
    "topic_selection": "topic_selection.json",
    "source_refs": "source_refs.json",
    "raw_facts": "raw_facts.json",
    "script_ja": "script_ja.json",
}


def _validate_config(config: dict) -> None:
    missing = [k for k in REQUIRED_CONFIG_KEYS if k not in config]
    if missing:
        raise ValueError(f"configに必須キーが不足しています: {missing}")


def _write_json(path: str, data: Any) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _build_run_summary_text(manifest: dict) -> str:
    lines = [
        f"experiment_id: {manifest.get('experiment_id')}",
        f"article_id: {manifest.get('article_id')}",
        f"status: {manifest.get('status')}",
    ]
    script_run = manifest.get("script_run") or {}
    lines.append(f"script_attempts: {len(script_run.get('attempts', []))} (status={script_run.get('status')})")
    tts_run = manifest.get("tts_run") or {}
    lines.append(f"tts_content_attempts: {len(tts_run.get('attempts', []))} (status={tts_run.get('status')})")
    if manifest.get("word_metrics"):
        lines.append(f"word_count: {manifest['word_metrics'].get('word_count')} "
                      f"({manifest['word_metrics'].get('status')})")
    if manifest.get("duration_metrics"):
        lines.append(f"duration_seconds: {manifest['duration_metrics'].get('duration_seconds')}")
    if manifest.get("effective_wpm") is not None:
        lines.append(f"effective_wpm: {manifest['effective_wpm']}")
    if manifest.get("failure_classification"):
        lines.append(f"failure_classification: {json.dumps(manifest['failure_classification'], ensure_ascii=False)}")
    return "\n".join(lines) + "\n"


def _extract_qa_results(tts_run_jsonable: dict) -> dict:
    """tts_run(JSON化済み)から、各TTSコンテンツ試行内のQA評価試行だけを
    抜き出した一覧を作る(qa_results.json用)。"""
    results = []
    for attempt in tts_run_jsonable.get("attempts", []):
        results.append({
            "tts_content_attempt_number": attempt.get("tts_content_attempt_number"),
            "outcome": attempt.get("outcome"),
            "outcome_label": common.OUTCOME_LABELS.get(attempt.get("outcome"), attempt.get("outcome")),
            "qa_evaluation_attempts": attempt.get("qa_evaluation_attempts", []),
            "embedded_qa_api_retry_count": attempt.get("embedded_qa_api_retry_count"),
            "grounded_qa_api_retry_count": attempt.get("grounded_qa_api_retry_count"),
        })
    return {"tts_content_attempts": results}


def _write_article_artifacts(
    manifest: dict,
    output_dir: Optional[str],
    article_id: str,
    script: Optional[dict],
    plan: Optional["common.NarrationPlan"],
    config: dict,
) -> Optional[dict]:
    if output_dir is None:
        return None
    article_dir = os.path.join(output_dir, article_id)
    os.makedirs(article_dir, exist_ok=True)

    written = {}

    _write_json(os.path.join(article_dir, "manifest.json"), manifest)
    written["manifest.json"] = os.path.join(article_dir, "manifest.json")

    if script is not None:
        path = os.path.join(article_dir, "script_en.json")
        _write_json(path, script)
        written["script_en.json"] = path

    if plan is not None:
        path = os.path.join(article_dir, "tts_expected_text.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(plan.full_text)
        written["tts_expected_text.txt"] = path

    if manifest.get("script_run") is not None:
        path = os.path.join(article_dir, "script_attempts.json")
        _write_json(path, manifest["script_run"])
        written["script_attempts.json"] = path

    if manifest.get("tts_run") is not None:
        path = os.path.join(article_dir, "tts_attempts.json")
        _write_json(path, manifest["tts_run"])
        written["tts_attempts.json"] = path

        path = os.path.join(article_dir, "qa_results.json")
        _write_json(path, _extract_qa_results(manifest["tts_run"]))
        written["qa_results.json"] = path

    if manifest.get("dynamics") is not None:
        path = os.path.join(article_dir, "dynamics_metrics.json")
        _write_json(path, manifest["dynamics"])
        written["dynamics_metrics.json"] = path

    if manifest.get("final_audio") is not None:
        path = os.path.join(article_dir, "final_audio_ref.json")
        _write_json(path, manifest["final_audio"])
        written["final_audio_ref.json"] = path

    if manifest.get("failure_classification") is not None:
        path = os.path.join(article_dir, "failure_classification.json")
        _write_json(path, manifest["failure_classification"])
        written["failure_classification.json"] = path

    if manifest.get("user_evaluation") is not None:
        path = os.path.join(article_dir, "user_evaluation.json")
        _write_json(path, manifest["user_evaluation"])
        written["user_evaluation.json"] = path

    path = os.path.join(article_dir, "run_summary.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(_build_run_summary_text(manifest))
    written["run_summary.txt"] = path

    for config_key, filename in OPTIONAL_PASSTHROUGH_ARTIFACTS.items():
        value = config.get(config_key)
        if value is not None:
            path = os.path.join(article_dir, filename)
            _write_json(path, value)
            written[filename] = path

    return written


def run_article(
    config: dict,
    script_write_fn: Callable[[dict], dict],
    tts_call_fn: Callable[[str], bytes],
    qa_call_fn: Callable[[str, bytes], str],
    sleep_fn: Optional[Callable[[float], None]] = None,
    output_dir: Optional[str] = None,
) -> ArticleRunOutcome:
    """記事1本分を 台本生成→構造/語数検証→TTS→技術検品(QA評価はTTS
    再生成と分離)→Dynamics3→成果物一式の組み立て まで実行する
    (fail-closed。全試行不合格の場合はその時点までのログを残して停止する)。

    config必須キー: experiment_id, article_id, genre, topic_or_source, voice
    config任意キー: topic_source_detail, prompt_version, model, qa_model,
                    model_config, topic_candidates, topic_selection,
                    source_refs, raw_facts, script_ja
                    (最後の5つは渡された場合のみそのままファイルへ書き出す。
                    S1.1では実トピック取得を行わないため通常は未指定)

    output_dirを指定した場合、<output_dir>/<article_id>/ 配下へ
    manifest.json他の成果物一式を書き出す(Git追跡方針はER-002-S1.1の
    .gitignoreを参照。音声実体・A/B対応表・元記事全文キャッシュのみ
    個別に除外)。
    """
    _validate_config(config)
    started_at = datetime.now(timezone.utc).isoformat()
    style_prefix = common.build_style_prefix()

    manifest: dict = {
        "experiment_id": config["experiment_id"],
        "article_id": config["article_id"],
        "genre": config.get("genre"),
        "topic_or_source": config.get("topic_or_source"),
        "voice": config.get("voice"),
        "prompt_version": config.get("prompt_version", "er002-s1.1"),
        "prompt_hash": common.sha256_text(style_prefix),
        "model": config.get("model", common.MODEL_NAME),
        "qa_model": config.get("qa_model", common.QA_MODEL_NAME),
        "model_config": config.get("model_config", {}),
        "retry_limits": {
            "max_script_attempts": common.MAX_SCRIPT_ATTEMPTS,
            "max_tts_content_attempts": common.MAX_TTS_CONTENT_ATTEMPTS,
            "max_qa_evaluation_attempts": common.MAX_QA_EVALUATION_ATTEMPTS,
            "max_tts_api_retry": common.MAX_TTS_API_RETRY,
            "max_qa_api_retry": common.MAX_QA_API_RETRY,
        },
        "started_at": started_at,
        "script_run": None,
        "tts_run": None,
        "dynamics": None,
        "final_audio": None,
        "word_metrics": None,
        "duration_metrics": None,
        "effective_wpm": None,
        "status": None,
        "failure_classification": None,
        "user_evaluation": common.default_user_evaluation(),
    }

    script_result = common.run_script_attempts(config, script_write_fn, max_attempts=common.MAX_SCRIPT_ATTEMPTS)
    manifest["script_run"] = _to_jsonable(script_result)

    if script_result.status != "OK":
        manifest["status"] = "FAILED_SCRIPT"
        manifest["failure_classification"] = {
            "stage": "script_generation",
            "reason": "all_script_attempts_failed",
        }
        manifest["completed_at"] = datetime.now(timezone.utc).isoformat()
        written = _write_article_artifacts(manifest, output_dir, config["article_id"], None, None, config)
        return ArticleRunOutcome(manifest=manifest, written_files=written)

    plan = script_result.plan
    tts_result = common.run_tts_content_attempts(
        plan, style_prefix, tts_call_fn, qa_call_fn,
        max_content_attempts=common.MAX_TTS_CONTENT_ATTEMPTS,
        max_api_retry=common.MAX_TTS_API_RETRY,
        max_qa_eval_attempts=common.MAX_QA_EVALUATION_ATTEMPTS,
        sleep_fn=sleep_fn,
    )
    manifest["tts_run"] = _to_jsonable(tts_result)

    if tts_result.status != "OK":
        outcome_counts = common.summarize_failure_outcomes(tts_result.attempts)
        last_outcome_label = (
            common.OUTCOME_LABELS.get(tts_result.attempts[-1].outcome, tts_result.attempts[-1].outcome)
            if tts_result.attempts else None
        )
        manifest["status"] = "FAILED_ALL_ATTEMPTS"
        manifest["failure_classification"] = {
            "stage": "tts_qa",
            "reason": "all_tts_content_attempts_failed",
            "last_attempt_outcome": last_outcome_label,
            "outcome_counts": outcome_counts,
        }
        manifest["completed_at"] = datetime.now(timezone.utc).isoformat()
        written = _write_article_artifacts(manifest, output_dir, config["article_id"], script_result.script, plan, config)
        return ArticleRunOutcome(manifest=manifest, written_files=written)

    c0_mono = common.pcm_bytes_to_float_mono(tts_result.accepted_audio)
    dynamics_result = common.apply_dynamics3_once(c0_mono, common.SAMPLE_RATE)
    manifest["dynamics"] = {
        "metrics_c0": dynamics_result.metrics_c0,
        "metrics_c1": dynamics_result.metrics_c1,
        "loudness_matching": dynamics_result.loudness_matching,
        "dynamics_params": dynamics_result.dynamics_params,
        "applied_once": dynamics_result.applied_once,
    }

    wc = common.word_count(plan.full_text)
    word_metrics = common.evaluate_word_count(wc)
    duration_seconds = dynamics_result.metrics_c1["duration_seconds"]
    duration_metrics = common.evaluate_duration(duration_seconds)
    wpm = common.effective_wpm(wc, duration_seconds)

    manifest["word_metrics"] = word_metrics
    manifest["duration_metrics"] = duration_metrics
    manifest["effective_wpm"] = wpm

    manifest["final_audio"] = {
        "tts_content_attempt_number": tts_result.accepted_attempt,
        "sample_rate": common.SAMPLE_RATE,
        "raw_c0_pcm_sha256": hashlib.sha256(tts_result.accepted_audio).hexdigest(),
        "note": (
            "S1/S1.1では実音声を生成していないため、この参照はモックTTS呼び出しで"
            "得られたバイト列のsha256のみ(ファイル未保存)。実運用時は"
            "ここにWAVファイルパスとsha256を記録する。"
        ),
    }
    manifest["status"] = "OK"
    manifest["completed_at"] = datetime.now(timezone.utc).isoformat()

    written = _write_article_artifacts(manifest, output_dir, config["article_id"], script_result.script, plan, config)
    return ArticleRunOutcome(manifest=manifest, c1_samples=dynamics_result.c1_samples, written_files=written)


# ============================================================
# A/B匿名化バンドルの組み立て(A04・A05向け)
# ============================================================
def build_ab_bundle(
    article_id: str,
    entries: list[dict],
    wav_bytes_by_label: dict[str, bytes],
    seed: Optional[int] = None,
    output_dir: Optional[str] = None,
) -> dict:
    """entries: [{"voice": "Aoede", ...}, {"voice": "Charon", ...}] のように、
    実際の話者データを記事内での提示順に依存しない形で渡す。
    wav_bytes_by_label: entriesの各要素に対応する生WAVバイト列を
    {"voice": Aoedeのバイト列, ...} のように渡す(呼び出し側でentryの
    識別キーを合わせること)。

    戻り値: {"files": {匿名ファイル名: メタデータ除去済みWAVバイト列, ...},
             "filename_mapping": {匿名ファイル名: 実際の話者情報, ...}
                                  (filesに実際に存在するファイル名だけを含む。
                                  ER-002-S2-C2で判明した「対応表に存在しない
                                  ファイル名が載る」事故の再発防止),
             "mapping_path": 対応表の保存先(output_dir指定時のみ、
                              *_ab_mapping.jsonなのでGit追跡対象外),
             "presentation": ABPresentation,
             "user_evaluations": {匿名ファイル名: A/B評価スキーマ初期値}
                                  (filesと同じキー集合)}

    filename_mapping / files / user_evaluations の3つは、必ず同一のループ内で
    同一のfilename変数から構築しており、キー集合が完全一致することを
    validate_ab_bundle_filename_consistency()で検証できる(ER-002-S2で発生した
    大文字小文字不一致の再発防止)。
    """
    presentation = ab.build_ab_presentation(article_id, entries, seed=seed)

    files = {}
    filename_mapping = {}
    user_evaluations = {}
    for sample_num, label in enumerate(presentation.order, start=1):
        entry = presentation.mapping[label]
        key = entry.get("voice") or entry.get("id")
        raw_bytes = wav_bytes_by_label.get(key)
        filename = ab.anonymized_filename(article_id, sample_num)
        if raw_bytes is None:
            continue  # 実データが無いエントリはfiles/対応表/評価スキーマのいずれにも含めない
        files[filename] = ab.strip_wav_metadata(raw_bytes)
        filename_mapping[filename] = dict(entry)
        user_evaluations[filename] = common.default_ab_user_evaluation()

    speaker_names = [str(e.get("voice", "")) for e in entries if e.get("voice")]
    leak_findings = {
        fname: ab.filename_reveals_speaker(fname, speaker_names) for fname in files
    }

    mapping_path = None
    if output_dir is not None:
        os.makedirs(output_dir, exist_ok=True)
        mapping_path = os.path.join(output_dir, f"er002_{article_id}_ab_mapping.json")
        ab.save_mapping_table(filename_mapping, mapping_path)

    bundle = {
        "files": files,
        "filename_mapping": filename_mapping,
        "mapping_path": mapping_path,
        "presentation": presentation,
        "filename_leak_findings": leak_findings,
        "user_evaluations": user_evaluations,
    }
    ab.validate_ab_bundle_filename_consistency(bundle, article_id, expected_sample_count=len(entries))
    return bundle


def write_ab_bundle_files(bundle: dict, ab_dir: str) -> list[str]:
    """A/Bバンドルの匿名化ファイルを実際にディスクへ書き出し、書き出し後に
    ディレクトリを読み直してbundle["files"]のキーと文字列として完全一致する
    (大文字小文字を含む)ことを検証する。ER-002-S2で手動リネームにより
    対応表とファイル名が食い違った事故の再発防止(この関数を使えば手動
    リネームの余地がない)。"""
    os.makedirs(ab_dir, exist_ok=True)
    for filename, wav_bytes in bundle["files"].items():
        with open(os.path.join(ab_dir, filename), "wb") as f:
            f.write(wav_bytes)

    on_disk = set(os.listdir(ab_dir))
    expected = set(bundle["files"].keys())
    missing = expected - on_disk
    if missing:
        raise ValueError(
            f"書き出したはずのファイルがディスク上に見つかりません(大文字小文字の"
            f"不一致等が疑われます): {missing}"
        )
    return sorted(expected)
