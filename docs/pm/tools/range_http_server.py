"""range_http_server.py

USER-TEST-SCRIPT-READABILITY-PROD-01 Phase C。
`python -m http.server` はHTTP Range要求(`Range: bytes=...`)に対応しておらず、
mp3のseek(`audio.currentTime`設定)がローカル確認環境で機能しない事例が
Phase Dで確認された(`docs/pm/RESULT_PACKET_SCRIPT_READABILITY_PROD_01.md`
Phase D 10節)。本スクリプトは`http.server`ベースにRangeヘッダ対応
(206 Partial Content応答)を追加した最小限のローカル静的ファイルサーバ。
新規ロジックはRange処理のみで、それ以外は標準ライブラリの
`http.server.SimpleHTTPRequestHandler`をそのまま利用する。

使い方:
  python docs/pm/tools/range_http_server.py --port 8765 [--directory .]
"""

from __future__ import annotations

import argparse
import http.server
import os
import re
import socketserver


class RangeHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def send_head(self):
        range_header = self.headers.get("Range")
        if not range_header:
            return super().send_head()

        path = self.translate_path(self.path)
        if not os.path.isfile(path):
            return super().send_head()

        file_size = os.path.getsize(path)
        m = re.match(r"bytes=(\d*)-(\d*)", range_header)
        if not m:
            return super().send_head()

        start_s, end_s = m.groups()
        if start_s == "" and end_s == "":
            return super().send_head()
        if start_s == "":
            # suffix range: last N bytes
            length = int(end_s)
            start = max(0, file_size - length)
            end = file_size - 1
        else:
            start = int(start_s)
            end = int(end_s) if end_s else file_size - 1
        end = min(end, file_size - 1)
        if start > end or start >= file_size:
            self.send_error(416, "Requested Range Not Satisfiable")
            return None

        length = end - start + 1
        f = open(path, "rb")
        f.seek(start)

        ctype = self.guess_type(path)
        self.send_response(206)
        self.send_header("Content-type", ctype)
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
        self.send_header("Content-Length", str(length))
        self.end_headers()

        self._range_start = start
        self._range_length = length
        return f

    def copyfile(self, source, outputfile):
        if hasattr(self, "_range_length"):
            remaining = self._range_length
            bufsize = 64 * 1024
            while remaining > 0:
                chunk = source.read(min(bufsize, remaining))
                if not chunk:
                    break
                outputfile.write(chunk)
                remaining -= len(chunk)
        else:
            super().copyfile(source, outputfile)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--directory", default=".")
    args = ap.parse_args()

    os.chdir(args.directory)
    handler = RangeHTTPRequestHandler
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", args.port), handler) as httpd:
        print(f"Range-capable HTTP server on port {args.port}, serving {os.getcwd()}", flush=True)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
