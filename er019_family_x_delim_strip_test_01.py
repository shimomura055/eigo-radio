"""OPEN-591 第1段: 表示層の終端`=====`strip回帰test。"""
import unittest
from er019_family_x_listening_page_01 import strip_trailing_delim as f


class T(unittest.TestCase):
    def test_html_tail(self):
        self.assertEqual(f("<p>解説です。 =====</p></dd>"), "<p>解説です。</p></dd>")

    def test_md_tail(self):
        self.assertEqual(f("本文\n====="), "本文")
        self.assertEqual(f("本文\n=====\n"), "本文")

    def test_non_terminal_unchanged(self):
        s = "=====ITEM 2=====\n本文 ===== 途中\n続き"
        self.assertEqual(f(s), s)

    def test_no_delim_bytes_unchanged(self):
        s = "<p>a = b == c</p>\n"
        self.assertEqual(f(s), s)


if __name__ == "__main__":
    unittest.main()
