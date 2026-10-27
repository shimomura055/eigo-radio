# -*- coding: utf-8 -*-
"""SLOT-23-CONSUMER-DESIGN-01 委任_04C: 旧per-article公開ページscript(`er019_*page*.py` 14本)の新表示仕様run誤用ガード。

目的: 確定レコードに`display_spec`(学習項目①②③の新表示仕様のマーク)があるFamily X runを、新仕様に対応していない旧scriptが処理して
「本文ハイライトもStd Part 1も無い公開ページ」を黙って作ることを防ぐ(DESIGN_03 §C-追補 M13)。新規記事の正式経路は
`er019_family_x_listening_page_01.py`(標準builder)。旧scriptは遡及なし=未改修。

使い方: 旧scriptの先頭importに1行だけ追加する(`import er019_x_page_guard_01  # noqa: F401  SLOT-23: display_spec付きrunならSTOP`)。
importすると、このプロセスで`<run>/<level>/`の入力(parts.json・audit/timeline.json・audit/tts_generation_results.json・
key_phrases/keywords_canonicalized.json・assembled/配下のopen/glob)を読もうとした最初の時点で(=ページ生成の入力を読む前に)、そのrunのどちらかのlevelが`display_spec`付きなら`X_PAGE_GUARD_DISPLAY_SPEC_RUN`で止める(RuntimeError)。
表示有効化の判断はflag非経由(er128.display_spec_of相当。確定レコードの直読み)。環境変数・引数で無効化できない(モジュール変数ENABLEDはtest専用)。
display_specが無い旧run=何もしない(従来どおり。バイト同一)。標準builder自身はこのmoduleをimportしない。
"""
from __future__ import annotations

import json
import os
import re
import sys

ENABLED = True          # test専用の切替(旧scriptからは変更されない。環境変数・引数では変えられない)
LEVELS = ("a2", "b1b")
_WATCH_RE = re.compile(r"^(?P<run>.+?)[\\/](?P<lv>a2|b1b)[\\/](?:parts\.json|audit[\\/](?:timeline|tts_generation_results)\.json"
                       r"|key_phrases[\\/]keywords_canonicalized\.json|assembled[\\/][^\\/]*)$")
_checked: dict = {}


class DisplaySpecRunStop(RuntimeError):
    pass


def display_spec_levels(run_dir: str) -> list:
    """run_dir配下で確定レコード(`<run>/<level>/key_phrases/confirmed_selection.json`)にdisplay_specがあるlevelのlist(取消済みは除く)。"""
    out = []
    for lv in LEVELS:
        p = os.path.join(run_dir, lv, "key_phrases", "confirmed_selection.json")
        if not os.path.exists(p):
            continue
        try:
            with open(p, encoding="utf-8") as f:
                rec = json.load(f)
        except (OSError, ValueError):
            continue
        if rec.get("state") == "revoked":
            continue
        if rec.get("display_spec"):
            out.append(lv)
    return out


def assert_no_display_spec(run_dir: str, *, script: str = "") -> None:
    lvs = display_spec_levels(run_dir)
    if lvs:
        raise DisplaySpecRunStop(
            f"[STOP] X_PAGE_GUARD_DISPLAY_SPEC_RUN: {run_dir} の {lvs} は新表示仕様(display_spec付き: 本文ハイライト・Standard Part 1)のrunです。"
            f"旧per-article公開ページscript{('(' + script + ')') if script else ''}は新仕様に未対応のため、ページを作りません"
            "(ハイライト・Std Part 1が無い公開ページを黙って作らない)。新規記事の正式経路: "
            "`py er019_family_x_listening_page_01.py --slug <slug> --run-name <run> --web <出力dir>`。")


def _audit_hook(event, args):
    if event not in ("open", "glob.glob") or not ENABLED:   # open=入力ファイルを読む時 / glob.glob=assembled/*.wavを探す時(旧scriptは音声変換より先にglobする)
        return
    path = args[0]
    if not isinstance(path, (str, bytes, os.PathLike)):
        return
    try:
        p = os.fspath(path)
        if isinstance(p, bytes):
            return
    except TypeError:
        return
    m = _WATCH_RE.match(p)
    if not m:
        return
    run = m.group("run")
    if run in _checked:
        if _checked[run]:
            raise DisplaySpecRunStop(_checked[run])
        return
    try:
        assert_no_display_spec(run, script=os.path.basename(sys.argv[0]) if sys.argv else "")
        _checked[run] = None
    except DisplaySpecRunStop as exc:
        _checked[run] = str(exc)
        raise


sys.addaudithook(_audit_hook)
