# -*- coding: utf-8 -*-
"""T3 共通: 記事のunit分割(APIなし、決定論)とdev/held-out項目。Trial専用。"""
import sys, os, json, pathlib
sys.path.insert(0, 'er052_output/open233_stage2_01')
import replay_lib as RL  # noqa (chdir ROOT, imports runner)
runner = RL.runner
import er052_open233_stage1_coverage_checker_01 as cov
OUT = RL.ROOT / 'er052_output' / 'open233_link_precision_01'

def split(art):
    return cov.split_units(art, runner.vs_sentence_segments_l6, runner.CAUSAL_SENTENCE_INITIAL_EN)

def article_runs(kind):
    items = RL.dev_items(kind)
    by = {}
    for i in items: by.setdefault(i['run'], []).append(i)
    return by
