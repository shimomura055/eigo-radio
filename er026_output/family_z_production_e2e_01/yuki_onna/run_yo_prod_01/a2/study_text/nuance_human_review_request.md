# ニュアンス解説 Human Review 依頼

- level: a2(Standard) / 最大1件・採用するか不採用かを決めます(不採用でも代替候補は自動補充されません)
- 候補ID: nuance_e97496c894b00f2a / candidate_sha256: e97496c894b00f2aa9cd3d480935b1b4f53902163f0f4f7a2124f26f66754457

## not even
- 本文の英文: Never tell anyone about tonight, not even your mother.
- 日本語訳: 今夜のことは誰にも話してはいけない。お母さんにさえ話してはいけない。
- ポイント: 否定の中で「例外になりそうなもの」まで含める強調

解説(全文):
「not even」は、否定の範囲に「当然なら例外になりそうなもの」まで含める強調です。ここでは母親にも話すなと例外を封じ、秘密の厳しさを際立たせています。単に「母親を含めて誰にも言うな」と伝える including your mother より、「母親でさえ例外ではない」という意外性が前に出ます。日本語の「〜でさえ」に近い感覚で捉えられます。

- 重複判定(KP/Word): pass / 暫定選定のKey Phrase・Wordとは学習上の焦点が別と判定しました。

## 決め方
- V3フォーム: 『ニュアンス解説』欄で採用/不採用を選び、KP・文法と一緒に送信(推奨)
- CLI(KPを先に確定した場合など): `py er119_kp_human_review_cli_01.py nuance-select --run er026_output/family_z_production_e2e_01/yuki_onna/run_yo_prod_01 --level a2 --choice adopt|reject --candidates-sha e97496c894b00f2aa9cd3d480935b1b4f53902163f0f4f7a2124f26f66754457 --by <名前> --user-ref <ユーザー発言のdelegation_logパス>`
