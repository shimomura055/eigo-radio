# RESULT_01: WRITER-DEV-RISK-FLAGGER-POST-EN-TRIAL-01 結果(Trial/DEV、2026-10-10)

**Closeout分類(Sonnet提案、Fable確定): USER_DECISION_REQUIRED。** VALIDATED/REJECTEDではなく、A3+A4の英訳後配置・R0後Hard STOP Check除去・翻訳後Hard STOP Check除去の正式判断をユーザー確認待ちでSTOP。APPROVED_FOR_PRODUCTION/PRODUCTION_WIREDへは進めない。Production変更ゼロ。
有用/不要の最終ラベルは確定しない。下記の『Known/New』『束ね方』は機械的な提案で、ユーザー確認用。旧Hard STOP Checkを正解教師として扱わない。

## 0. 実施概要

- 11本(既定8テーマ + 既知例用の追加3本。INVENTORY_01.md)× A3/A4 = 22呼び出し。全22完走、全てattempts=1・valid JSON、再試行なし。
- Flagger: model `gpt-6.1-sol`(API応答のmodel欄の実測値: gpt-6.1-sol)/ reasoning effort=medium / ANTENNA-TRIAL-01と同一構成。最新モデル原則(PM_GOVERNANCE 25節)に沿う構成(ANTENNA-TRIAL-01と同一であること以外に新たな最新性の再確認はしていない)。
- A3/A4 prompt: ANTENNA-TRIAL-01と**バイト一致**(A3 `9d995042...`、A4 `c87b95e5...`。英語注記追加なし = 差分ゼロ。EN_ADAPTATION_01.md)。強制TopNなし・0件許容・confidence閾値なし・A5/A6なし・再生成なし・STOPなし。
- 費用: 実測 JPY49.38(見積中央値 JPY50.83、高位 JPY78.75、累計上限 JPY76.25。逸脱なし)。入力 110278 tokens / 出力 8805 tokens。1セル平均 JPY2.24。
- 所在差異(要確認): ユーザー指示のOpenAI日本語R2と英語引用は別世代の稿。詳細 INVENTORY_01.md §2。『STOP稿』(U07, U08, X11)は完成記事ではない。

## 1. 記事別結果(Union = A3 ∪ A4、同一文は1行、typeが違えば併記)

### U01 meta — Advanced B1b(英語Advanced)

- English source: `inputs/U01_meta.md`(採用稿(ADOPTED。Advanced checker RESOLVED_STAGE2_DOWNGRADE))
- A3 Flag: 0件 [] / A4 Flag: 1件 ['s18'] / Union: 1件 / A3∩A4 overlap: 0件 / 意味上の問題単位: 1件

| 文ID / 対象文 | A3 type conf | A4 type conf | Related Fact | Reason(Flaggerのquestion、原文のまま日本語) | Known issue(提案) | New issue(提案) |
|---|---|---|---|---|---|---|
| s18: We cannot assume from this story that any information was shared. | - | 主体対象入替 0.35 | MUSE-HC-010 | A4: 「any information was shared」は、台帳が未確認としている「機微情報の意図しない共有」から「情報共有全般」へと範囲を広げているのではありませんか。 | - | New: (旧Check指摘なし) |

### U02 hormuz — Advanced B1b

- English source: `inputs/U02_hormuz.md`(採用稿(ADOPTED。Adv RESOLVED_STAGE2_DOWNGRADE))
- A3 Flag: 1件 ['s18'] / A4 Flag: 1件 ['s18'] / Union: 1件 / A3∩A4 overlap: 1件 / 意味上の問題単位: 1件

| 文ID / 対象文 | A3 type conf | A4 type conf | Related Fact | Reason(Flaggerのquestion、原文のまま日本語) | Known issue(提案) | New issue(提案) |
|---|---|---|---|---|---|---|
| s18: So Brent futures did not suddenly plunge. | その他 0.72 | その他 0.50 | HF-009, HF-011 | A3: 「So Brent futures did not suddenly plunge」は置換発表によって急落が起きなかったという因果関係と急落の不在を示唆しますが、台帳が示すのは「一時的な上げ幅縮小とその後の回復」であり、因果関係や急落の不在までは確認できないのではありませんか / A4: 「So Brent futures did not suddenly plunge」は、台帳の「一時的な上げ幅縮小とその後の回復」という観測を超えて、償還料案の置換が急落を防いだという未確認の因果関係を示す表現ではありませんか。 | - | New: (旧Check指摘なし。U02は旧CheckでCOMPLIANT) |

### U03 space_weapons — Advanced B1b(B1回復後の最終稿)

- English source: `inputs/U03_space_weapons.md`(採用稿(ADOPTED。Adv RESOLVED_REWRITE_THEN_DOWNGRADE))
- A3 Flag: 5件 ['s1', 's5', 's13', 's17', 's33'] / A4 Flag: 5件 ['s1', 's5', 's13', 's17', 's33'] / Union: 5件 / A3∩A4 overlap: 5件 / 意味上の問題単位: 2件

| 文ID / 対象文 | A3 type conf | A4 type conf | Related Fact | Reason(Flaggerのquestion、原文のまま日本語) | Known issue(提案) | New issue(提案) |
|---|---|---|---|---|---|---|
| s1: # Space Weapons: Their Special Attack Is Secret, but Their “Address” Was Made Public | その他 0.72 | その他 0.35 | F-001 | A3: 見出しの「Their Special Attack Is Secret」は、台帳の「具体的なシステム名・攻撃能力・標的は推測で補わない」よりも強く、特定の攻撃能力が存在し秘密扱いされていると述べる表現ではありませんか / A4: 見出しの「Their Special Attack Is Secret」は、台帳の「具体的なシステム名・攻撃能力・標的は推測で補わない」という注意書きよりも強く、攻撃能力の存在とその機密扱いを断定しているのではありませんか。 | Known系統: 能力の秘匿・不在断定系(旧Check: b1b_prev_b1 attempt1『has not explained what they can do』= changed_fact/unsupported_new_claim, translation)。ただし最終稿U03自体は旧CheckがCOMPLIANT | - |
| s5: The details of the system’s performance remain secret, while the U.S. | その他 0.83 | その他 0.40 | F-001 | A3: 「the system’s performance remain secret」は、台帳で具体的な性能が示されていないことを、性能が秘密扱いされているという事実に置き換えているのではありませんか / A4: 「the system’s performance remain secret」は、台帳の「具体的なシステム名・攻撃能力・標的は推測で補わない」とは異なり、性能の詳細が機密扱いであると断定しているのではありませんか。 | Known系統: 同上(能力・性能が秘密/非開示という断定)。文がU.S.の位置で分割されており途中で切れている | - |
| s13: But no specific system names or attack capabilities have been given. | 不在断定 0.70 | 不在断定 0.35 | F-001 | A3: 「no specific system names or attack capabilities have been given」は、台帳の「具体的なシステム名・攻撃能力・標的は推測で補わない」を超えて、それらが一切公表されていないと断定しているのではありませんか / A4: 「no specific system names or attack capabilities have been given」は、台帳の「具体的なシステム名・攻撃能力・標的は推測で補わない」という注意書きを、具体名や攻撃能力の公表がないという未確認の断定に広げているのではありませんか。 | Known系統: 同上(『no specific system names or attack capabilities have been given』) | - |
| s17: Russia has destroyed satellites with ground-launched anti-satellite missiles. | 数量時系列 0.76 | 数量時系列 0.40 | F-003 | A3: 「has destroyed satellites」という複数形は、台帳に記載された「COSMOS 1408」という1基の破壊を、複数の衛星を破壊した実績へ広げているのではありませんか / A4: 「Russia has destroyed satellites」という複数形は、台帳が記録する「COSMOS 1408」という1基の破壊を、複数の衛星を破壊した実績に広げているのではありませんか。 | Known系統: 旧Check: space a2稿attempt1/2が『Russia has destroyed satellites』複数形を翻訳由来MAJOR(changed_number等)と指摘。b1b稿には旧Check指摘なし | - |
| s33: The United States has publicly acknowledged deploying space-control weapons in orbit, but has not disclosed their capabilities. | 不在断定 0.68 | 不在断定 0.35 | F-001 | A3: 「has not disclosed their capabilities」は、台帳の「具体的なシステム名・攻撃能力・標的は推測で補わない」より範囲が広く、防護用途の説明はあるにもかかわらず能力全般が非開示であると断定しているのではありませんか / A4: 「has not disclosed their capabilities」は、台帳の「具体的なシステム名・攻撃能力・標的は推測で補わない」という注意書きとは異なり、能力が公表されていないと断定しているのではありませんか。 | Known系統: 同上(『has not disclosed their capabilities』。E2E EVALが最終Adv『In one line』に残存と記録した文) | - |

束ね方(提案): 【能力・性能の秘匿/非開示の断定(F-001注記)】= s1,s5,s13,s33

### U04 small_bag — Advanced B1b

- English source: `inputs/U04_small_bag.md`(採用稿(ADOPTED。Adv RESOLVED_STAGE2_DOWNGRADE))
- A3 Flag: 2件 ['s7', 's15'] / A4 Flag: 1件 ['s7'] / Union: 2件 / A3∩A4 overlap: 1件 / 意味上の問題単位: 1件

| 文ID / 対象文 | A3 type conf | A4 type conf | Related Fact | Reason(Flaggerのquestion、原文のまま日本語) | Known issue(提案) | New issue(提案) |
|---|---|---|---|---|---|---|
| s7: In other words, the point is not just “What can I fit inside?” but also “How does it look as part of an outfit?” Rather than a helper working behind t… | 主体対象入替 0.45 | 主体対象入替 0.42 | MB-05 | A3: 「a mini bag」を荷物を運ぶ役割より装いのアクセントとして説明している点は、台帳の「実用性より芸術性の強い小型クラッチ」という特定の形状への評価を、ミニバッグ全般へ広げているのではありませんか。 / A4: 台帳の「実用性より芸術性の強い小型クラッチ」という特定のランウェイ上の形状についての説明が、本文の「a mini bag」によってミニバッグ全般の役割についての説明へ広がっているのではありませんか？ | - | New: (旧Check指摘なし) |
| s15: It’s a showcase of choices: go small for decoration, or carry a big bag. | 主体対象入替 0.30 | - | MB-03, MB-05 | A3: 「go small for decoration, or carry a big bag」という用途の分け方は、台帳の特定の小型クラッチについての装飾性の説明を、小型バッグ全般は装飾用で大型バッグは荷物を運ぶためのものという区分に広げているのではありませんか。 | - | New: (旧Check指摘なし) |

束ね方(提案): 【小型クラッチ特定の評価をミニバッグ全般へ拡張(MB-05/MB-03)】= s7,s15

### U05 byd_recall — Advanced B1b

- English source: `inputs/U05_byd_recall.md`(採用稿(ADOPTED。Adv RESOLVED_REWRITE_THEN_DOWNGRADE))
- A3 Flag: 2件 ['s1', 's6'] / A4 Flag: 2件 ['s4', 's6'] / Union: 3件 / A3∩A4 overlap: 1件 / 意味上の問題単位: 3件

| 文ID / 対象文 | A3 type conf | A4 type conf | Related Fact | Reason(Flaggerのquestion、原文のまま日本語) | Known issue(提案) | New issue(提案) |
|---|---|---|---|---|---|---|
| s1: # A Car’s Red Lights Say “Braking!” Even When No One Is Pressing the Pedal—A Surprising Solo Play-by-Play | その他 0.35 | - | BYD-RECALL-07 | A3: 見出しの「Red Lights Say “Braking!” Even When No One Is Pressing the Pedal」は現に起きている現象と読めますが、台帳の「極端な場合」に「点灯し続ける可能性がある」という条件付きの説明より強い断定ではありませんか | Known関連: BYD In One Lineの条件落ち(旧Check A2稿 changed_scope)と同系統の『極端な場合』条件落ちだが、Flagされたのは見出し文。In One Line文(s27)自体は未Flag | - |
| s4: But the driver has no idea why. | - | その他 0.28 | (なし) | A4: 「the driver has no idea why」は運転者が原因を知らないとの断定ですが、運転者の認識については台帳に記載がなく、確認できない主張ではありませんか | - | New: (旧Check指摘なし。Fact無し=台帳にない主張) |
| s6: A recall notice in China named 183,211 cars from BYD’s Tang and Qin lines. | 主体対象入替 0.88 | 数量時系列 0.94 | BYD-RECALL-01 | A3: 「A recall notice」が183,211台を記載したという表現は、台帳の「2件の召回公告」の対象台数を合算して183,211台となるという集計範囲と食い違うのではありませんか / A4: 「A recall notice」に183,211台が記載されたという表現は、台帳の「2件の公告の対象台数を合算した183,211台」と公告数および数値の集計範囲が食い違うのではありませんか | - | New: (旧Check指摘なし。台帳BYD-RECALL-01は『2件の公告の合算』) |

### U06 streaming_price — Advanced B1b

- English source: `inputs/U06_streaming_price.md`(採用稿(ADOPTED。Adv RESOLVED_STAGE2_DOWNGRADE))
- A3 Flag: 3件 ['s8', 's9', 's17'] / A4 Flag: 5件 ['s8', 's9', 's16', 's17', 's21'] / Union: 5件 / A3∩A4 overlap: 3件 / 意味上の問題単位: 4件

| 文ID / 対象文 | A3 type conf | A4 type conf | Related Fact | Reason(Flaggerのquestion、原文のまま日本語) | Known issue(提案) | New issue(提案) |
|---|---|---|---|---|---|---|
| s8: The monthly ad-supported plan by itself will go from $11.99 to $12.49, a difference of $0.50. | 数量時系列 0.35 | 主体対象入替 0.40 | F02, F05, F06 | A3: 「will go from」は値上げが今後始まる意味に読めますが、台帳では新規契約者には2026年9月23日から新価格が適用され、既存契約者には10月21日以降の請求サイクルから適用されるという区別ではありませんか / A4: 「will go from $11.99 to $12.49」は対象を限定せず一律の改定と読めますが、台帳では米国向け価格であり「第三者請求経由では価格が異なる場合がある」とされているのではありませんか。 | - | New: (旧Check指摘なし) |
| s9: The monthly Premium plan by itself will go from $18.99 to $21.49, a difference of $2.50. | 数量時系列 0.35 | 主体対象入替 0.40 | F03, F05, F06 | A3: 「will go from」は値上げが今後始まる意味に読めますが、台帳では新規契約者には2026年9月23日から新価格が適用され、既存契約者には10月21日以降の請求サイクルから適用されるという区別ではありませんか / A4: 「will go from $18.99 to $21.49」は対象を限定せず一律の改定と読めますが、台帳では米国向け価格であり「第三者請求経由では価格が異なる場合がある」とされているのではありませんか。 | - | New: (旧Check指摘なし) |
| s16: So the headline about the price increase is a preview sent to everyone. | - | その他 0.20 | (なし) | A4: 「a preview sent to everyone」は比喩だけでなく全員への通知送付とも読めますが、全員に送付されたという事実は台帳では確認できないのではありませんか。 | - | New: (旧Check指摘なし。Fact無し) |
| s17: But the day the main story begins on your bill is different for each person. | 主体対象入替 0.64 | 数量時系列 0.55 | F06 | A3: 「is different for each person」は全員の適用日がそれぞれ異なるという断定に読めますが、台帳の「各利用者の請求サイクルにより異なる」は同じ日に適用される利用者もあり得るという意味ではありませんか / A4: 「is different for each person」は全員の適用日が互いに異なると読めますが、台帳の「各利用者の請求サイクルにより異なる」は同じ日に適用される利用者もいることを排除していないのではありませんか。 | - | New: (旧Check指摘なし) |
| s21: The price list tells you “how much.” When you look at it together with when you signed up and your billing cycle, you can see when the change starts f… | - | その他 0.35 | F05, F06 | A4: 「when you signed up and your billing cycle」で適用時期を確定できるという記述は、台帳の「第三者請求パートナー経由では価格や適用条件が異なる場合がある」という条件を落として断定しているのではありませんか。 | - | New: (旧Check指摘なし。台帳F05の第三者請求条件の脱落) |

束ね方(提案): 【値上げ適用の範囲・時期(will go from…。F02/F03/F05/F06)】= s8,s9

### U07 openai_copyright — Advanced B1b(B1回復後のJA R2由来)

- English source: `inputs/U07_openai_copyright.md`(【STOP稿】翻訳後Hard STOP Check(JA_RECHECK_REQUIRED)で止まった英語生成稿。完成記事ではない。article.mdは存在せず、dev-check promptの『検証対象の記事』欄から復元)
- A3 Flag: 1件 ['s5'] / A4 Flag: 4件 ['s1', 's5', 's21', 's22'] / Union: 4件 / A3∩A4 overlap: 1件 / 意味上の問題単位: 4件

| 文ID / 対象文 | A3 type conf | A4 type conf | Related Fact | Reason(Flaggerのquestion、原文のまま日本語) | Known issue(提案) | New issue(提案) |
|---|---|---|---|---|---|---|
| s1: # More Than $250 Million—and a Demand to “Destroy the Models,” Too: AI Lawsuits Are About More Than Money | - | 主体対象入替 0.30 | F6 | A4: 見出しの「AI Lawsuits Are About More Than Money」は、台帳の「本件訴状で求められた救済」をAI訴訟一般へ広げた表現ではありませんか。 | Known: 旧Check: 見出し『AI Lawsuits Are About More Than Money』のscope拡張(changed_scope, origin=ja_source, F6)= U07がSTOPした直接原因。A3は未Flag、A4のみ | - |
| s5: Their list of demands also includes the “destruction” of models such as GPT. | 主体対象入替 0.62 | 主体対象入替 0.65 | F6 | A3: 「models such as GPT」は、台帳の「原告らのコンテンツを組み込んだGPTその他の大規模言語モデル」という限定を欠き、破棄請求の対象をGPTなどのモデル全般へ広げて読める表現ではありませんか。 / A4: 「destruction of models such as GPT」は、台帳の「原告らのコンテンツを組み込んだ」という対象限定がなく、GPTなどのモデル全般の破棄を求めていると読める表現ではありませんか。 | - | New: (旧Check指摘なし) |
| s21: At the time of Reuters’ report, OpenAI had not yet responded to a request for comment. | - | 不在断定 0.30 | F7 | A4: 「had not yet responded」は、台帳の「直ちには応じなかった」より強く、Reutersの報道時点まで応答が一切なかったと断定する表現ではありませんか。 | - | New: (旧Check指摘なし) |
| s22: In AI news, performance and convenience often take center stage. | - | その他 0.20 | (なし) | A4: 「performance and convenience often take center stage」というAI報道全般の傾向は、台帳のどのFactにも対応する根拠がなく、別途確認が必要な主張ではありませんか。 | - | New: (旧Check指摘なし。Fact無し) |

### U08 semiconductor_earnings — Advanced B1b

- English source: `inputs/U08_semiconductor_earnings.md`(【STOP稿】翻訳後Hard STOP Check(JA_RECHECK_REQUIRED)で止まった英語生成稿。完成記事ではない。article.mdは存在せず、dev-check promptから復元)
- A3 Flag: 1件 ['s25'] / A4 Flag: 1件 ['s25'] / Union: 1件 / A3∩A4 overlap: 1件 / 意味上の問題単位: 1件

| 文ID / 対象文 | A3 type conf | A4 type conf | Related Fact | Reason(Flaggerのquestion、原文のまま日本語) | Known issue(提案) | New issue(提案) |
|---|---|---|---|---|---|---|
| s25: But even if the company’s forecast appears beside that line, we cannot say, “AI demand is strong, so revenue will be about $34.8 billion.” This announ… | 不在断定 0.68 | 不在断定 0.35 | F4, F6 | A3: 文中の「This announcement alone does not explain how the two are connected」は、台帳の「連結売上高見通し」と「CEOによる需要評価」からは確認できない、発表内に両者の関連説明がないという断定ではありませんか。 / A4: 「This announcement alone does not explain how the two are connected」という説明の不在の断定は、台帳の「連結売上高見通し」と「需要についてのCEOの説明」だけでは、決算発表全体に両者の関係の説明がないことまで確認できないのではありませんか。 | Known(境界例): 旧Check: unsupported_new_claim(F6)。ユーザー判断は『ベストではないが問題視するほどではない』= 過剰Flagを見る境界例 | - |

### X09 hormuz — Advanced B1b_prev_b1(B1回復前の初回英語稿)

- English source: `inputs/X09_hormuz.md`(【追加・既知例用】B1回復前の英語稿(ja_source MAJORでSTOPし、JA再生成=B1回復の起点となった稿)。採用稿ではない。dev-check promptから復元)
- A3 Flag: 1件 ['s8'] / A4 Flag: 2件 ['s8', 's10'] / Union: 2件 / A3∩A4 overlap: 1件 / 意味上の問題単位: 2件

| 文ID / 対象文 | A3 type conf | A4 type conf | Related Fact | Reason(Flaggerのquestion、原文のまま日本語) | Known issue(提案) | New issue(提案) |
|---|---|---|---|---|---|---|
| s8: Trump’s “20% plan.” It called for a 20% payment on all cargo passing through the Strait of Hormuz, as reimbursement for the cost of ensuring U.S. | 主体対象入替 0.65 | 主体対象入替 0.83 | HF-002 | A3: 「the cost of ensuring U.S.」は米国自体の安全確保に要する費用とも読めますが、台帳の「米国がホルムズ海峡の安全と警備を提供するための費用」とは安全確保の対象が異なるのではありませんか / A4: 「the cost of ensuring U.S.」は米国自体の安全確保の費用と読めますが、台帳の「米国がホルムズ海峡の安全と警備を提供するための費用」とは安全確保の対象が異なるのではありませんか。 | - | New: (旧Check指摘なし。『U.S.』で文が分割され『ensuring U.S.』で切れた分割アーティファクトの可能性) |
| s10: The size of the figure and the broad scope of the plan were enough to grab the headlines. | - | その他 0.28 | (なし) | A4: 「The size of the figure and the broad scope」が「grab the headlines」の理由だったという説明は、台帳に対応する記述がなく、確認できない因果関係を加えているのではありませんか。 | - | New: (旧Check指摘なし。Fact無し) |

### X10 space_weapons — Advanced B1b_prev_b1(B1回復前稿)

- English source: `inputs/X10_space_weapons.md`(【追加・既知例用】B1回復前の英語稿(attempt2でdev-check COMPLIANTだったがB1回復で置換された)。最終採用稿ではない)
- A3 Flag: 0件 [] / A4 Flag: 1件 ['s5'] / Union: 1件 / A3∩A4 overlap: 0件 / 意味上の問題単位: 1件

| 文ID / 対象文 | A3 type conf | A4 type conf | Related Fact | Reason(Flaggerのquestion、原文のまま日本語) | Known issue(提案) | New issue(提案) |
|---|---|---|---|---|---|---|
| s5: The main subject here is not a weapon that can blow up Earth, but the line around what counts as a “space weapon.” This is news where the label matter… | - | その他 0.30 | F-001 | A4: 「not a weapon that can blow up Earth」は兵器の能力を否定する断定にも読めますが、台帳では具体的な攻撃能力は示されず「攻撃能力を推測で補わない」とされており、台帳で確認できる範囲を超えているのではありませんか。 | Known: 旧Check: space a2_prev_b1 Standard attempt1『The main subject is not a weapon that can blow up Earth.』(unsupported_new_claim, ja_source)と同一文。A3は未Flag、A4のみ | - |

### X11 openai_copyright — Advanced B1b_prev_b1(B1回復前の初回英語稿)

- English source: `inputs/X11_openai_copyright.md`(【追加・最重要既知例用・STOP稿】B1回復前に翻訳後Hard STOP Check(changed_actor MAJOR, ja_source)で止まった英語生成稿。完成記事ではない。dev-check promptから復元)
- A3 Flag: 4件 ['s4', 's7', 's17', 's25'] / A4 Flag: 2件 ['s4', 's7'] / Union: 4件 / A3∩A4 overlap: 2件 / 意味上の問題単位: 3件

| 文ID / 対象文 | A3 type conf | A4 type conf | Related Fact | Reason(Flaggerのquestion、原文のまま日本語) | Known issue(提案) | New issue(提案) |
|---|---|---|---|---|---|---|
| s4: The plaintiffs are also asking for models such as GPT that they say contain problematic content, as well as training sets, to be destroyed. | 主体対象入替 0.42 | 主体対象入替 0.36 | F6 | A3: 「contain problematic content」は、台帳の「原告らのコンテンツを組み込んだ」と異なり、破棄請求の対象を原告らのコンテンツ以外にも広げて読める表現ではありませんか。 / A4: 「contain problematic content」は、台帳の「原告らのコンテンツを組み込んだ」という破棄請求の対象を、原告らのコンテンツに限らない「問題のあるコンテンツ」を含むモデルへ広げて読める表現ではありませんか。 | - | New: (旧Check指摘なし) |
| s7: They also say the models’ output copied or put articles together in new ways, and removed copyright management information. | 主体対象入替 0.96 | 主体対象入替 0.94 | F4 | A3: 「the models’ output ... removed copyright management information」は、台帳で除去の主体とされている「OpenAI」を「モデル出力」に置き換えているのではありませんか。 / A4: 「the models’ output ... removed copyright management information」は、台帳では著作権管理情報を除去したと主張されている主体が「OpenAI」であるのに、その主体を「モデル出力」に入れ替えた記述ではありませんか。 | Known: 旧Check: changed_actor(MAJOR, ja_source, F4)『They also say the models' output … removed copyright management information.』= OpenAI actor drift | - |
| s17: It is like seeing the total on a bill and being shocked, then turning to the next page and finding an item called “how to handle models and data.” “Pl… | 主体対象入替 0.35 | - | F6 | A3: 「what we claim you made using those articles」は、台帳の「原告らのコンテンツを組み込んだモデルおよび訓練セット」よりも広く、記事を利用して作ったもの全般を破棄請求の対象にしているように読めるのではありませんか。 | - | New: (旧Check指摘なし) |
| s25: At the time of Reuters’ report, OpenAI had not commented right away. | 不在断定 0.35 | - | F7 | A3: 「OpenAI had not commented right away」は、台帳の「広報担当者がコメント依頼に直ちには応じなかった」という取材状況を、OpenAIによるコメント全般の不在に広げているのではありませんか。 | - | New: (旧Check指摘なし) |

束ね方(提案): 【破棄請求の対象範囲(原告のコンテンツ→広い表現。F6)】= s4,s17

## 2. 集計

| 指標 | 11本(U01-U08 + X09-X11) | 既定8本(U01-U08のみ) |
|---|---|---|
| sentence-level Flag総数(A3+A4) | 45(A3 20 + A4 25) | 35 |
| A3/A4 overlap(同一記事・同一文) | 16 | 13 |
| Union総数(重複除去後) | 29 | 22 |
| 意味上の問題単位に束ねた候補数 | 23 | 17 |
| 1記事あたり平均 Union | 2.64 | 2.75 |
| 1記事あたり平均 問題単位 | 2.09 | 2.12 |

記事別: U01=A3 0・A4 1・Union 1・単位 1 / U02=A3 1・A4 1・Union 1・単位 1 / U03=A3 5・A4 5・Union 5・単位 2 / U04=A3 2・A4 1・Union 2・単位 1 / U05=A3 2・A4 2・Union 3・単位 3 / U06=A3 3・A4 5・Union 5・単位 4 / U07=A3 1・A4 4・Union 4・単位 4 / U08=A3 1・A4 1・Union 1・単位 1 / X09=A3 1・A4 2・Union 2・単位 2 / X10=A3 0・A4 1・Union 1・単位 1 / X11=A3 4・A4 2・Union 4・単位 3

- A3のみ / A4のみ / 両方の内訳: A3のみ 4、A4のみ 9、両方 16(Union 29)。
- 0件の記事(A3/A4どちらも0): なし。A3が0件でA4が1件以上: U01, X10。
- 量産可能な水準かの判断はしない(ユーザー確認用)。参考として、既定8本の平均は1記事あたり約2.1問題単位。

## 3. OpenAI actor drift(専用節)

対象: **X11(B1回復前のSTOP稿、`They also say the models' output copied or put articles together in new ways, and removed copyright management information.` = s7)**。対照: U07(B1回復後の最終STOP稿、s11『They further accuse OpenAI of removing copyright management information.』= 主体OpenAI明示)。

| | A3 | A4 |
|---|---|---|
| X11 s7を拾ったか | **拾った**(主体対象入替、confidence 0.96、Fact ['F4']) | **拾った**(主体対象入替、confidence 0.94、Fact ['F4']) |
| 拾った文 | s7(上記英文全文) | s7(同) |
| actor/主体の問題として認識したか | **認識した**。理由欄原文: 「「the models’ output ... removed copyright management information」は、台帳で除去の主体とされている「OpenAI」を「モデル出力」に置き換えているのではありませんか。」 | **認識した**。理由欄原文: 「「the models’ output ... removed copyright management information」は、台帳では著作権管理情報を除去したと主張されている主体が「OpenAI」であるのに、その主体を「モデル出力」に入れ替えた記述ではありませんか。」 |

- 両方とも、台帳F4が『OpenAIが著作権管理情報を除去したと主張』と述べているのに英文がthe models' outputを主体に読める、という**OpenAI→モデル出力の主体入替**を文言どおりに指摘している(type=主体対象入替)。この稿でFlaggerが付けた最高水準のconfidence(0.94〜0.96)。
- U07(主体OpenAI明示の稿)のs11はA3/A4とも**Flagなし**(= actor driftが無い稿を過剰に拾っていない)。U07でFlagされたのは s5(A3 .62/A4 .65: GPTなど全般への範囲拡張)、s1(A4 .30: 見出しのAI訴訟一般への拡張。旧Check STOPの原因)、s21、s22。
- 起源判定への疑義: ユーザー指摘『日本語R2には明示的にOpenAIがあるのに旧Checkはorigin=ja_source』は、日本語R2が世代違い(B1回復後 `ja_writer/revision2.md` にはOpenAI明示、X11の元の `ja_writer_prev_b1/revision2.md` には『さらに、モデルの出力が記事を複製したり、組み直したりしたほか、著作権管理情報も取り除いたとしています』で主語なし)であることで説明がつく可能性がある(ファイル内容の照合結果。ただしCheckerの判定過程そのものは再検証していない)。

## 4. Semiconductor境界例(U08 s25。過剰Flagかの最終判定はしない)

- 該当文(s25は2文が1IDに結合): 「But even if the company's forecast appears beside that line, we cannot say, “AI demand is strong, so revenue will be about $34.8 billion.” **This announcement alone does not explain how the two are connected.**」
- A3: 拾った(不在断定、confidence **0.68**、Fact ['F4', 'F6'])。理由: 「文中の「This announcement alone does not explain how the two are connected」は、台帳の「連結売上高見通し」と「CEOによる需要評価」からは確認できない、発表内に両者の関連説明がないという断定ではありませんか。」
- A4: 拾った(不在断定、confidence **0.35**、Fact ['F4', 'F6'])。理由: 「「This announcement alone does not explain how the two are connected」という説明の不在の断定は、台帳の「連結売上高見通し」と「需要についてのCEOの説明」だけでは、決算発表全体に両者の関係の説明がないことまで確認できないのではありませんか。」
- U08でFlagされたのはこのs25のみ(両レベルとも1件)。他の文は過剰にFlagされていない。Flaggerは『STOP/Rewriteではなく確認箇所を示すだけ』の位置づけなので、このFlagはHuman Review候補1件(A3 0.68/A4 0.35)として表示される。confidence閾値で除外するか、1件程度は許容するかはユーザー判断(Claudeは閾値を追加していない)。

## 5. 旧Hard STOP Check指摘との対応(旧Checkを正解教師としない。参照のみ)

| 旧Check既知例 | 該当稿 | 本文に実在 | A3 | A4 |
|---|---|---|---|---|
| OpenAI actor drift | X11 s7 | 実在 | 拾った(.96) | 拾った(.94) |
| OpenAI 見出しscope拡張(STOP直接原因) | U07 s1 | 実在 | 拾わない | 拾った(.30) |
| Semiconductor 説明不在の断定(境界例) | U08 s25 | 実在 | 拾った(.68) | 拾った(.35) |
| BYD In One Line条件落ち | U05 s27 | 実在 | 拾わない(隣接の見出しs1で『極端な場合』条件に言及して.35) | 拾わない |
| Hormuz Brent→oil prices | X09 s2, s13 | X09に実在(U02には不在) | **拾わない** | **拾わない**(X09では別文s8/s10) |
| Space『blow up Earth』能力否定 | X10 s5 | X10に実在(U03には不在) | 拾わない | 拾った(.30) |
| Space『capabilities』不在断定(旧Check b1b_prev_b1 attempt1相当) | U03 s33, s13 | 実在 | 拾った(.68, .70) | 拾った(.35, .35) |
| Space ロシア破壊の複数形(a2稿の旧Check指摘) | U03 s17 | b1b稿に実在 | 拾った(.76) | 拾った(.40) |

**見逃し(Flagされなかった既知例)**: Hormuz『oil prices』への一般化(X09 s2, s13)はA3/A4どちらもFlagしなかった。BYD In One Line文(U05 s27)そのものも未Flag。Space blow-up Earth(X10 s5)はA3が拾わなかった。**100% recallを要求するTrialではない**が、事実として記録する。

## 6. 過剰Flag候補(ユーザー確認用。確定しない)

- U08 s25(境界例。上記)。
- 低確信度でFactなし(台帳に対応記述のない一般的説明・比喩): U05 s4(.28)、U06 s16(.20)、U07 s22(.20)、X09 s10(.28)。いずれもA4のみ(A4レベルは『台帳に対応記述がない事実の主張』を拾う設計)。
- 文分割アーティファクトの疑い: X09 s8(A3 .65/A4 .83。『ensuring U.S.』で切れた文を、安全確保の対象が米国自体と読めると指摘)、U03 s5(『while the U.S.』で切れた文)。分割ミスが理由の一部の可能性がある(確定ではない)。
- 『will go from…』の価格改定文(U06 s8, s9)や『a mini bag』(U04 s7, s15)など、台帳の限定条件(適用日・特定の形状)を超えた一般化という指摘は、人間が見る価値があるかが主観的。

## 7. 新規Flag候補(旧Check指摘になかった。ユーザー確認用。確定しない)

- U05 s6(A3 .88/A4 .94): 『A recall notice … named 183,211 cars』。台帳BYD-RECALL-01は『2件の公告の台数を合算した数』。単数公告と読める点。高confidence・Factあり。
- U03 s17(A3 .76): ロシアのCOSMOS 1408(1基)を『satellites』複数形に広げた点(a2稿では旧Checkが指摘していたがb1b稿では旧Check未指摘)。
- U06 s17・s21: 適用日・第三者請求パートナー条件の落ち(台帳F05/F06)。
- U07 s5, s21 / X11 s4, s17, s25: 破棄請求対象の範囲、OpenAIの応答状況の広げ。

## 8. 参考: 旧Hard STOP Checkを外した場合の実務的価値

- 旧CheckはU03(最終稿)とU05(最終稿)をCOMPLIANTにしたが、A3/A4はU03に5文、U05に2文のHuman Review候補を出した。逆に旧CheckがSTOPさせたU07・U08・X11も、A3/A4は候補として表面化した(U07のSTOP理由はA4のみ、U08は両方、X11のactor driftは両方)。
- ただし旧Checkが指摘した全ての問題をA3/A4が拾ったわけではない(上記見逃し)。今回は英訳後配置の初期観察であり、Production採否の根拠にはしない。

## 9. 条件同一性・信頼性

- 全22セル同一モデル・同一effort・同一prompt(A3, A4各1つ)・同一splitter・完全台帳(8テーマ全PASS)。cap/retry発動なし。応答JSONは全て有効(valid=True、attempts=1)。
- 1回ずつの実行であり、同一入力の再実行による再現性(ノイズ幅)は今回測っていない。confidence値・件数は1サンプル。
- 文分割は既存splitterの限界(閉じ引用符直後で分割されない/『U.S.』で分割)がそのまま現れる。文IDは対象文の厳密な単位ではない場合がある。

## 10. 費用・model_id・routing evidence

- 実測 JPY49.38 / 22呼び出し(`cost_ledger_post_en_01.jsonl`、`cost_estimate_post_en_01.json`)。見積中央 JPY50.83に対し 97.1%。
- API応答の `model`: `gpt-6.1-sol`(全22呼び出し。`flags/*/*.json` の `model_ids`、`logs/*_raw.jsonl` の `model_id`)。レイテンシ等の追加routing情報は取っていない。

## 11. 未決事項・USER_DECISION_REQUIRED

1. A3+A4の英訳後・音声化前配置の採否(未VALIDATED。Production wiring未実施)。2. R0後Hard STOP Check除去の採否。3. 翻訳後Hard STOP Check除去の採否。4. 確認すべきFlagの範囲(confidence閾値を設けるか。今回は追加していない)。5. 文分割の改善要否(英語稿の閉じ引用符・略語)。6. OpenAI世代差(INVENTORY_01.md §2)の認識確認。7. 見逃し既知例(Hormuz oil prices、BYD In One Line文)をどう扱うか。8. 『新Writer+Production Checkerなし+A3/A4+Human Review』運用コンセプトはAPPROVED_FOR_PRODUCTION・未PRODUCTION_WIREDのまま(closeしない)。
