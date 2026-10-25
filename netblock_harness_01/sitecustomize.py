# -*- coding: utf-8 -*-
"""ネットワーク遮断harness(KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01 委任_03)。

使い方: PYTHONPATH=netblock_harness_01 NETBLOCK_LOG=<ログ> <python> -m pytest ... (子processにも継承される)
外部への接続(socket.connect / connect_ex / getaddrinfo / create_connection)を OSError で遮断し、試行先を NETBLOCK_LOG へ1行ずつ追記する。
localhost(127.0.0.1/::1/localhost)は許可。huggingfaceへの接続はwordfreq等のcache照合用に許可(NETBLOCK_ALLOW=host1,host2 で追加)。
遮断下で api.openai.com 等への試行が0であることをログで確認する(有料API到達の保証)。本ファイルは環境変数が無ければ何もしない。
"""
import os
import socket

_LOG = os.environ.get("NETBLOCK_LOG")
if _LOG:
    _ALLOW = {"localhost", "127.0.0.1", "::1", "huggingface.co", "cdn-lfs.huggingface.co"} | \
             {h for h in os.environ.get("NETBLOCK_ALLOW", "").split(",") if h}
    _orig = {"getaddrinfo": socket.getaddrinfo, "connect": socket.socket.connect, "connect_ex": socket.socket.connect_ex}

    def _log(kind, host):
        try:
            with open(_LOG, "a", encoding="utf-8") as f:
                f.write(f"{kind}\t{host}\tpid={os.getpid()}\n")
        except OSError:
            pass

    def _host_of(addr):
        if isinstance(addr, (tuple, list)) and addr:
            return str(addr[0])
        return str(addr)

    _ALLOWED_IPS = set()

    def _gai(host, *a, **k):
        h = str(host)
        if h in _ALLOW:
            res = _orig["getaddrinfo"](host, *a, **k)
            for r in res:   # 許可hostの解決済みIPへのconnectも許可する(HFのCDN等)
                _ALLOWED_IPS.add(r[4][0])
            return res
        _log("BLOCKED_getaddrinfo", h)
        raise OSError(f"[NETBLOCK] getaddrinfo blocked: {h}")

    def _conn(self, addr):
        h = _host_of(addr)
        if h in _ALLOW or h in _ALLOWED_IPS or self.family == getattr(socket, "AF_UNIX", -1):
            return _orig["connect"](self, addr)
        _log("BLOCKED_connect", h)
        raise OSError(f"[NETBLOCK] connect blocked: {h}")

    def _conn_ex(self, addr):
        h = _host_of(addr)
        if h in _ALLOW or h in _ALLOWED_IPS or self.family == getattr(socket, "AF_UNIX", -1):
            return _orig["connect_ex"](self, addr)
        _log("BLOCKED_connect_ex", h)
        raise OSError(f"[NETBLOCK] connect_ex blocked: {h}")

    socket.getaddrinfo = _gai
    socket.socket.connect = _conn
    socket.socket.connect_ex = _conn_ex
