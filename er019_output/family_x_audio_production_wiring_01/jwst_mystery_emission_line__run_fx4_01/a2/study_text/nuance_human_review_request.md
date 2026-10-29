# ニュアンス解説 Human Review 依頼

- level: a2(Standard) / 最大1件・採用するか不採用かを決めます(不採用でも代替候補は自動補充されません)
- 候補ID: nuance_a908f53870b003fe / candidate_sha256: a908f53870b003fee04fed613dbebcacd6fde0a931b3e2d4f430395fb2545f04

## could not confirm
- 本文の英文: They could not confirm that an image showed an object where the line was.
- 日本語訳: 画像が、光の線があった場所に天体を示しているとは確認できませんでした。
- ポイント: 「確認できない」と「存在しないと確認した」の区別

解説(全文):
could not confirm that ... は「…ではないと確認した」ではなく、「…だと確かめられなかった」という意味です。否定されているのは確認できたということ自体で、対象が存在しないとは断定していません。たとえば They confirmed that no object was there. なら「そこに天体がないと確認した」です。本文では、画像で確認できないことと、存在しないことを慎重に区別しています。

- 重複判定(KP/Word): pass / 暫定選定のKey Phrase・Wordとは学習上の焦点が別と判定しました。

## 決め方
- V3フォーム: 『ニュアンス解説』欄で採用/不採用を選び、KP・文法と一緒に送信(推奨)
- CLI(KPを先に確定した場合など): `py er119_kp_human_review_cli_01.py nuance-select --run er019_output/family_x_audio_production_wiring_01/jwst_mystery_emission_line__run_fx4_01 --level a2 --choice adopt|reject --candidates-sha a908f53870b003fee04fed613dbebcacd6fde0a931b3e2d4f430395fb2545f04 --by <名前> --user-ref <ユーザー発言のdelegation_logパス>`
