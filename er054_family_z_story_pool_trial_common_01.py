# -*- coding: utf-8 -*-
"""FAMILY-Z-STORY-POOL-SCREENING-TRIAL-01 委任_02: Trial専用の共通部品(モデル解決・Blindガード)。
Production(er026等)からimportされない。Production Routing keyは変更せず、Trial専用keyを参照するだけ。
"""
from __future__ import annotations

import os

import er006_model_routing_contract_01 as routing

# Trial専用routing key(er006 PROCESS_MODEL_MAPに追加済み。値はgpt-6-luna固定。Production keyは流用しない)
KEY_QUALITY = "FAMILY_Z_TRIAL_STORY_QUALITY_EVAL"
KEY_RIGHTS = "FAMILY_Z_TRIAL_RIGHTS_INTERPRET"
TRIAL_KEYS = (KEY_QUALITY, KEY_RIGHTS)

# Blind: 過去Trial評価結果(封印)はdriverから読まない。ファイル名のdeny list。
SEALED_DENY_NAMES = ("SEALED_PAST_RESULTS_L01_L06",)


class SealedFileAccessError(RuntimeError):
    pass


def assert_not_sealed(path: str) -> str:
    """読込前に必ず通す。封印ファイル(過去評価結果)ならSTOP。"""
    norm = os.path.basename(str(path)).upper()
    for n in SEALED_DENY_NAMES:
        if n.upper() in norm or n.upper() in str(path).upper():
            raise SealedFileAccessError(f"STOP(Blind): 封印ファイルの読込は禁止: {path}")
    return path


def resolve_trial_model(key: str) -> str:
    """既存Routing経由でTrial専用keyのモデルを取得(Trial key以外・未知keyは拒否)。"""
    if key not in TRIAL_KEYS:
        raise routing.ModelContractViolation(f"STOP: {key} はFamily Z Trial専用keyではない(Production key流用禁止)。")
    return routing.PROCESS_MODEL_MAP[key]


def check_model(key: str, requested: str) -> str:
    """許可外モデルは拒否(fail-closed)。Astra/Sol等はここで拒否される。"""
    return routing.require_model(key, requested)
