# -*- coding: utf-8 -*-
"""FZCW offline test用 環境補助(Production code ではない)。

目的: システム`py`(3.14)に未導入の第三者package(google.genai / pykakasi)を、importできない場合に限り空stubで補い、
er012_b / er003_n3 / er063 を遮断harness下でimportできるようにする(実APIは呼べない: 補うのはimport名のみ。.venvでは実物が優先され何もしない)。
併せて netblock_harness_01/sitecustomize.py(外部接続遮断)を同じprocess・子processでも有効にする(PYTHONPATHにこのdirを指定する)。
使い方(repo root): $env:PYTHONPATH="docs/research/FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01/env_stub"; $env:NETBLOCK_LOG=<log>; py -m pytest ...
"""
import importlib.abc
import importlib.machinery
import importlib.util
import os
import sys
import types

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", "..", "..", ".."))

# (1) 遮断harness(あれば)を読み込む
_nb = os.path.join(_ROOT, "netblock_harness_01", "sitecustomize.py")
if os.path.exists(_nb):
    _spec = importlib.util.spec_from_file_location("_netblock_sitecustomize", _nb)
    _mod = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)


# (2) 未導入packageのimport名stub(実物があれば使わない)
class _StubFinder(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    def __init__(self, tops):
        self.tops = set(tops)

    def find_spec(self, name, path, target=None):
        if name.split(".")[0] in self.tops:
            return importlib.machinery.ModuleSpec(name, self, is_package=True)
        return None

    def create_module(self, spec):
        m = types.ModuleType(spec.name)
        m.__path__ = []

        def _ga(attr):
            if attr.startswith("__"):
                raise AttributeError(attr)
            return type(attr, (), {})
        m.__getattr__ = _ga
        return m

    def exec_module(self, module):
        pass


def _importable(top):
    try:
        return importlib.util.find_spec(top) is not None
    except (ImportError, ValueError):
        return False


_need = []
if not _importable("pykakasi"):
    _need.append("pykakasi")
try:
    from google import genai  # noqa: F401
except Exception:
    _need.append("google")
if _need:
    sys.meta_path.append(_StubFinder(_need))
    for _k in [k for k in sys.modules if k == "google" or k.startswith("google.")]:
        del sys.modules[_k]
