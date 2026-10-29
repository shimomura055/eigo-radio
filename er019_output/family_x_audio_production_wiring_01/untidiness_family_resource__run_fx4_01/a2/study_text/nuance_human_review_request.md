# ニュアンス解説 Human Review 依頼

- level: a2(Standard) / 最大1件・採用するか不採用かを決めます(不採用でも代替候補は自動補充されません)
- 候補ID: nuance_e0dc4b7adeca75d7 / candidate_sha256: e0dc4b7adeca75d7084502efc6b97640ed51941d1af17b4d3922e55ca05006a1

## Not so fast.
- 本文の英文: But the court says, “Not so fast.” This supplement may need a lawyer to speak for it.
- 日本語訳: しかし裁判所は「ちょっと待った」と言います。このサプリメントには、代わりに弁護してくれる人が必要かもしれません。
- ポイント: 判断や行動を急がせない、口語的な制止の含み

解説(全文):
“Not so fast.” は文字どおり「速くない」ではなく、「まだそう決めるのは早い」「ちょっと待って」という制止です。ここでは片づける側の要求をすぐに通さず、別の事情も聞こうという反論の合図になっています。単に相手を止める “Wait!” と比べると、判断や結論を急ぐなという含みが出ます。強い怒りというより、会話をいったん止める口語的な言い方です。

- 重複判定(KP/Word): pass / 暫定選定のKey Phrase・Wordとは学習上の焦点が別と判定しました。

## 決め方
- V3フォーム: 『ニュアンス解説』欄で採用/不採用を選び、KP・文法と一緒に送信(推奨)
- CLI(KPを先に確定した場合など): `py er119_kp_human_review_cli_01.py nuance-select --run er019_output/family_x_audio_production_wiring_01/untidiness_family_resource__run_fx4_01 --level a2 --choice adopt|reject --candidates-sha e0dc4b7adeca75d7084502efc6b97640ed51941d1af17b4d3922e55ca05006a1 --by <名前> --user-ref <ユーザー発言のdelegation_logパス>`
