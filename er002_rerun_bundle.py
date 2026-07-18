# ============================================================
# er002_rerun_bundle.py
# ER-002-S3-B1: 独立再実行用入力バンドル
# ============================================================
# A01/A02の「6記事初回生成完了後の独立再実行(機械的再現性確認)」で使う
# 入力一式を、初回実行時に保存しておくためのスキーマと関連関数。
#
# 独立再実行の定義(このリポジトリでの決め事):
#   再実行しないもの: Web検索・トピック候補取得・トピック採点・記事選定・
#                      確認済みファクトの作り直し
#   新しく実行するもの: 台本生成・台本検品・TTS・QA・Dynamics3
#   初回の台本や音声は再利用しない(script_generation_inputから台本を
#   新規に生成し直す)。
#
# このモジュールはB1時点では実際の再実行を行わない(入力バンドルの保存と
# 検証のみ)。実際の再実行はB1後の別工程で行う。

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Optional

BUNDLE_SCHEMA_VERSION = "er002-rerun-bundle-v1"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_json(obj: Any) -> str:
    return sha256_text(json.dumps(obj, ensure_ascii=False, sort_keys=True))


@dataclass
class RerunInputBundle:
    article_id: str
    selected_candidate_id: str
    selected_topic: str
    topic_selection_result: dict
    source_refs: list
    source_retrieved_at: str
    verified_facts: list
    script_generation_input: dict  # 台本生成アダプターへ渡す最小入力({"topic":..., "facts":...})
    frozen_conditions_sha256: str
    script_prompt_sha256: str  # このバンドル作成時点で実際に使ったQAではなく台本生成プロンプトのsha256
    topic_prompt_sha256: str
    model_names: dict
    model_settings: dict
    original_run_id: str
    genre: Optional[str] = None
    voice: Optional[str] = None
    bundle_schema_version: str = BUNDLE_SCHEMA_VERSION
    topic_selection_sha256: str = ""
    source_refs_sha256: str = ""
    verified_facts_sha256: str = ""
    script_generation_input_sha256: str = ""

    def compute_hashes(self) -> "RerunInputBundle":
        self.topic_selection_sha256 = sha256_json(self.topic_selection_result)
        self.source_refs_sha256 = sha256_json(self.source_refs)
        self.verified_facts_sha256 = sha256_json(self.verified_facts)
        self.script_generation_input_sha256 = sha256_json(self.script_generation_input)
        return self


def build_bundle(**kwargs) -> RerunInputBundle:
    bundle = RerunInputBundle(**kwargs)
    bundle.compute_hashes()
    return bundle


def save_bundle(bundle: RerunInputBundle, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(asdict(bundle), f, ensure_ascii=False, indent=2)


def load_bundle(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


class BundleIntegrityError(ValueError):
    pass


def verify_bundle_integrity(bundle_dict: dict) -> None:
    """保存済みバンドル(dict)の内容ハッシュを再計算し、記録済みハッシュと
    一致することを確認する(改ざん・破損検出、fail-closed)。"""
    checks = {
        "topic_selection_sha256": sha256_json(bundle_dict["topic_selection_result"]),
        "source_refs_sha256": sha256_json(bundle_dict["source_refs"]),
        "verified_facts_sha256": sha256_json(bundle_dict["verified_facts"]),
        "script_generation_input_sha256": sha256_json(bundle_dict["script_generation_input"]),
    }
    mismatches = {
        key: {"recorded": bundle_dict.get(key), "recomputed": recomputed}
        for key, recomputed in checks.items()
        if bundle_dict.get(key) != recomputed
    }
    if mismatches:
        raise BundleIntegrityError(f"再実行入力バンドルのハッシュが一致しません: {mismatches}")


def verify_bundle_frozen_conditions(bundle_dict: dict, current_frozen_conditions_sha256: str) -> None:
    """ER-002-v1.0以外の条件で保存されたバンドルを拒否する。"""
    recorded = bundle_dict.get("frozen_conditions_sha256")
    if recorded != current_frozen_conditions_sha256:
        raise BundleIntegrityError(
            "再実行入力バンドルのfrozen_conditions_sha256が現在の凍結条件と一致しません"
            f"(bundle={recorded}, current={current_frozen_conditions_sha256})。"
            "ER-002-v1.0以外の条件で保存されたバンドルの可能性があります。"
        )


def make_rerun_script_write_fn(bundle_dict: dict, script_write_fn_factory: Callable[[dict], Callable]):
    """script_generation_input(トピック・ファクトのみ)から新規に台本生成を
    行うscript_write_fnを構築する。script_write_fn_factoryは
    er002_script_adapter.make_script_write_fnのような
    (topic_package: dict) -> script_write_fn を渡す想定。

    初回のscript_en.json等は一切参照しない(=初回台本を再利用しない)。"""
    return script_write_fn_factory(bundle_dict["script_generation_input"])


def run_independent_rerun(
    bundle_dict: dict,
    script_write_fn: Callable[[dict], dict],
    tts_call_fn: Callable[[str], bytes],
    qa_call_fn: Callable[[str, bytes], str],
    current_frozen_conditions_sha256: str,
    run_article_fn: Callable,
    sleep_fn: Optional[Callable[[float], None]] = None,
    output_dir: Optional[str] = None,
):
    """独立再実行を1件実行する。Web検索・トピック候補取得・採点・選定は
    一切行わない(このシグネチャにそもそもそれらの引数が存在しない)。
    run_article_fn には er002_runner.run_article を渡す想定
    (依存性注入によりこのモジュール自体はer002_runnerをimportしない)。"""
    verify_bundle_integrity(bundle_dict)
    verify_bundle_frozen_conditions(bundle_dict, current_frozen_conditions_sha256)

    config = {
        "experiment_id": "ER-002-S3-RERUN",
        "article_id": bundle_dict["article_id"],
        "genre": bundle_dict.get("genre"),
        "topic_or_source": bundle_dict["selected_topic"],
        "voice": bundle_dict.get("voice"),
        "prompt_version": "er002-v1.0-rerun",
        "rerun_of": bundle_dict["original_run_id"],
    }
    return run_article_fn(
        config, script_write_fn, tts_call_fn, qa_call_fn, sleep_fn=sleep_fn, output_dir=output_dir,
    )
