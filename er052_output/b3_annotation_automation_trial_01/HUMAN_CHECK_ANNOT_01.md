# HUMAN_CHECK_ANNOT_01: ユーザーに見てほしい箇所だけの抜粋(全件確認は求めない)
対象 = 判断が微妙 / Production採用判断に影響 / Fact Lockへ危険な入力を渡し得るもの。出力実体は `runs/<model>/<theme>/rep<n>/annotated.md`(FORMAT_FAIL/STOPの出力は reply.txt)。

## H-1 【全モデル共通・最重要】指示文が【事実】の中に入ったまま(W-1既知欠陥OC-11と同根)
B3の「Selected Facts」に、事実の末尾へ書かれた指示/制約文(例: 「〜を付け加えないこと」「〜と断定しないこと」「「mini」と「micro」を混同しないこと」「具体的なシステム名や攻撃能力は補わない」)が混在している。**Sonnet 5.5もLunaも、GT(旧Trial統合)も、これを分離せず【事実N】の一部として注記した**(仕様v2は本文非改変のため分離できない)。機械検査もこれを検出しない。
- 該当(テーマ): semiconductor_earnings【事実1】、small_bag【事実3】、space_weapons【事実1〜5】、hormuz【事実2/4】、central_bank_mortgage【事実4/6】。
- 抜粋: `runs/sonnet55/semiconductor_earnings/rep1/annotated.md`【事実1】末尾 =「これらの需要評価と業績・見通しの間に、Ledgerで確認されていない因果関係を付け加えないこと。また、Ledgerは「最も最近」…断定しないこと。」
- 意味: 注記の自動化では解決しない(B3出力の構造=指示と事実を別欄にする、が必要)。Fact Lock Writerが指示文を事実として扱う可能性は注記方式の選択と無関係に残る。**ユーザー判断事項(B3側の改善はこのTrial範囲外=新仕様候補)。**

## H-2 【Luna固有】指示文を単独の【事実】にした(検査では捕捉されない型)
`runs/luna/semiconductor_earnings/rep1/annotated.md`: 指示文「また、Ledgerは「最も最近」の発表という選定条件を確定できないとしているため、Broadcomをその条件を満たす企業と断定しないこと。」が **【事実6】として独立**し、sidecarで台帳 F1 に紐付いた(`annotation.json`)。この出力は別理由(348億ドルの中核落ち)でFAILしたため採用されなかったが、**指示文の事実化そのものは機械検査の検出対象外**。同じ誤りが他の数値誤りを伴わずに起きれば検査をすり抜ける。

## H-3 【Luna固有】Storyline要約行の事実化(検査で捕捉された)
`runs/luna/openai_copyright/rep1/annotated.md`: Selected Facts内の「Storyline: …」要約行(原文では見出し行相当)を【事実1】にした。検査(d: 非事実行に【事実】)がFAIL判定。Sonnet 2回・Luna rep2は正しく無印のまま。

## H-4 【Luna固有】Fact境界の文途中分割
`runs/luna/byd_recall/rep1/reply.txt`: 1文「…制動灯が点灯し続け、後方車両に誤った信号を伝える懸念がある。」を読点で割り【事実3】【事実4】にした(断片事実)。形式(終端マーカー)FAILであり、仮に寛容に読んでも本文非改変検査(a)でFAIL(`analysis/luna_format_fail_lenient_supplement.json`)。

## H-5 【中核/周辺の判断が微妙】
- `runs/luna/central_bank_mortgage/rep2`: 30年固定の「30年」を中核、7.40％を周辺(5.98％は中核) = 対になる金利の片方だけ中核。検査FAIL(c)。
- Sonnet central_bank_mortgage(rep1/2とも打切りで非採用): 「0.25ポイント」を周辺(GTは中核)。Sonnetは2回とも同じ判断=判断が割れる箇所(上限3の扱い)。
- semiconductor_earnings(Luna rep1): 次四半期売上「約348億ドル」を周辺(GT/Sonnetは中核)=中核数値の欠落。検査FAIL(c)。

## H-6 【Luna rep2 semiconductor_earnings】STOP返答
`runs/luna/semiconductor_earnings/rep2/reply.txt`: 「Storylineの『CEOはAI関連需要が非常に強いと述べた』は台帳F6の範囲を超える」としてSTOP。同じ入力で Luna rep1・Sonnet 2回は注記を完遂。STOPが妥当な指摘か過剰かの判断はユーザー/Factチェック側(仕様§4にSTOP条件あり)。**Luna出力の揺れの代表例**。

## H-7 【Sonnet 5.5】出力打切り(技術問題、品質問題ではない)
central_bank_mortgage と inbound_tourism の各2回が max_tokens=16000 で打切り(thinking tokensが12,764〜15,936、本文は途中まで)。注記版本文は完成していたがsidecar JSONが欠落しFORMAT_FAIL。結果は変更せず記録。再実行して打切りを解消するかはFable/ユーザー判断(予想費用 約JPY120)。
