"""ログ/例外出力の秘密マスキング(GIT-SECRET-REPAIR-01, 2026-10-12).

.env の全値(長さ12以上)と、環境変数のうち名前が KEY/TOKEN/SECRET/PASSWORD を含むものの値を
`***` に置換する。DBG/例外ログ/stderr へ秘密が平文で出るのを防ぐ。値は表示・保存しない。
"""
import os
import re
import sys

MIN_LEN = 12
_NAME_RE = re.compile(r"(KEY|TOKEN|SECRET|PASSWORD|PASSWD)", re.I)
_DOTENV = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")


def _secret_values(extra=None):
    vals = set()
    try:
        from dotenv import dotenv_values
        for v in dotenv_values(_DOTENV).values():
            if v and len(v) >= MIN_LEN:
                vals.add(v)
    except Exception:
        pass
    for k, v in os.environ.items():
        if v and _NAME_RE.search(k) and len(v) >= 8:
            vals.add(v)
    for v in (extra or ()):
        if v and len(v) >= 4:
            vals.add(v)
    # 長い値から置換(部分一致の取りこぼし防止)
    return sorted(vals, key=len, reverse=True)


def mask_secrets(text, extra=None):
    """text(str/bytes/その他)内の秘密値を *** に置換して返す."""
    if isinstance(text, bytes):
        for v in _secret_values(extra):
            text = text.replace(v.encode("utf-8"), b"***")
        return text
    if not isinstance(text, str):
        text = str(text)
    for v in _secret_values(extra):
        text = text.replace(v, "***")
    return text


class MaskingStream:
    """write時に mask_secrets を通す stream wrapper."""

    def __init__(self, stream):
        self._s = stream

    def write(self, data):
        return self._s.write(mask_secrets(data) if isinstance(data, str) else data)

    def __getattr__(self, name):
        return getattr(self._s, name)


def install_stream_masking():
    """sys.stdout/sys.stderr を masking wrapper に置換(冪等)."""
    for n in ("stdout", "stderr"):
        s = getattr(sys, n)
        if not isinstance(s, MaskingStream):
            setattr(sys, n, MaskingStream(s))
