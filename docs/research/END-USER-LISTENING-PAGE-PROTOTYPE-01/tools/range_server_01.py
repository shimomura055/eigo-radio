# -*- coding: utf-8 -*-
"""ローカル検証用の静的サーバ(HTTP Range対応。python標準のhttp.serverはRange非対応でaudioのシークが検証できないため)。
使い方: py range_server_01.py <port> <root_dir>"""
import os, re, sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer


class H(SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send_head(self):
        rng = self.headers.get('Range')
        path = self.translate_path(self.path)
        if not rng or not os.path.isfile(path):
            return super().send_head()
        m = re.match(r'bytes=(\d*)-(\d*)$', rng.strip())
        size = os.path.getsize(path)
        if not m:
            return super().send_head()
        a, b = m.groups()
        start = int(a) if a else max(0, size - int(b))
        end = int(b) if (a and b) else size - 1
        end = min(end, size - 1)
        if start > end:
            self.send_error(416)
            return None
        f = open(path, 'rb')
        f.seek(start)
        self.send_response(206)
        self.send_header('Content-Type', self.guess_type(path))
        self.send_header('Accept-Ranges', 'bytes')
        self.send_header('Content-Range', 'bytes %d-%d/%d' % (start, end, size))
        self.send_header('Content-Length', str(end - start + 1))
        self.end_headers()
        self._left = end - start + 1
        return f

    def copyfile(self, src, dst):
        left = getattr(self, '_left', None)
        if left is None:
            return super().copyfile(src, dst)
        while left > 0:
            buf = src.read(min(65536, left))
            if not buf:
                break
            dst.write(buf)
            left -= len(buf)
        self._left = None


if __name__ == '__main__':
    port, root = int(sys.argv[1]), sys.argv[2]
    os.chdir(root)
    ThreadingHTTPServer(('127.0.0.1', port), H).serve_forever()
