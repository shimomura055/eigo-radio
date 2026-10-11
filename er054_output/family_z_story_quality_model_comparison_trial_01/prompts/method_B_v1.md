# 方式B v1: 3段階PASS/WEAK/FAIL + 根拠整合チェック

目的: 粗い3段階でも識別でき、かつ「弱点を書いたのに高評価」の矛盾をモデル自身に点検させる方式。
## DEVELOPER_ADDENDUM
評価は4項目(A〜D)それぞれPASS/WEAK/FAILの3段階で行う。PASS=基準を十分に満たす、WEAK=満たすが弱点が目立つ、FAIL=基準を満たさない。
全項目に差を付ける必要はなく、全項目PASSも全項目FAILも本文が示すなら付けてよい。
各項目に本文からの根拠引用(1〜2個)、日本語の理由(2〜3文)、weakness(その項目の弱点を1文。弱点が見当たらなければ「なし」)を付ける。
全項目の判定後に必ず根拠整合チェックを行う: (1)各項目のweaknessと理由から自己申告した弱点を列挙し、(2)その弱点の重さと判定(PASS/WEAK/FAIL)が矛盾していないか点検して矛盾を contradictions_found に書き、(3)矛盾があれば判定を修正して verdicts_revised=true にする(修正後の判定を最終値として出力)。矛盾がなければ空配列とfalse。

## USER_CRITERIA
[方式B: 既存4軸を PASS/WEAK/FAIL で判定し、根拠整合チェックを行う]
A. 中心事件・変化: 追える中心事件・行動・関係変化・選択があるか。
B. 読者の関心: 読者を引っ張る要素(Hook・緊張・意外性・疑問・人間関係・共感・皮肉・強い状況設定)があるか。派手なHookは必須ではない。
C. 展開・余韻: 意味のある展開・変化または余韻が残るか。明確なオチは必須ではない。
D. 短編化適性: 英語の短編(280〜420語、A2〜B1向け)へ圧縮しても作品の魅力が残るか。文体・長い描写・心理描写そのものが魅力の中心で削ると消える作品は不向き。

[手順]
1. key_facts に中心事件・主要人物・転換点・結末を書く(自分の言葉でよい)。
2. A〜Dを判定する(verdict, evidence_quotes, reason, weakness)。
3. consistency_check(self_reported_weaknesses, contradictions_found, verdicts_revised)を書く。
4. overall.verdict(PASS/WEAK/FAIL)とcommentを書く。
5. 出力はJSONのみ。
