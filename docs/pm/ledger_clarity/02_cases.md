# 02_cases: Ledger明確化の事例集(委任_01b、read-only、¥0)

注意: 以下の【案】は原資料との意味一致を未確認。台帳・gold・SSOTは未変更。原文(英語記事)はrepo内に保存されておらず(grep: rolled back/rollback等0件、ER019/052配下の台帳・draft・audit)、出典URLの再取得は未実施(API不使用)。

## A. HC-012(Meta、`er019_output/meta/run_03/ledger/verified_fact_ledger.txt` L74-78)

現行台帳block(逐語):
> [VERIFIED] MUSE-HC-012: MetaのSuperintelligence Labs部門の副社長は、適切な開示なしに契約スタッフが電話をかけるテストを開始したことを「ミス」だったと認め、機能を当面ロールバックしたと社内投稿で説明した。
> scope: Meta社内テストの人間コンシェルジュ機能 / conditions: 適切な開示なしで契約スタッフが電話を担当していたテスト / date_or_period: 2026年9月22日まで
> notes_for_writer: 「サービス全体を停止した」とは書かない。ロールバック対象は人間コンシェルジュ機能として扱う。(出典 channelnewsasia.com Reuters転載)

draft側(`research_ledger/fact_ledger_draft.json`): subject=「人間コンシェルジュ機能のロールバック」、causal_strength=NOT_APPLICABLE、support_level=DIRECTLY_STATED、ambiguity=「ロールバック後の再開時期、対象範囲、代替方式は公表されていない。」。verification_notes=「機能を当面ロールバックしたと記載。サービス全体の停止とはしておらず」。

原資料: Reuters "Exclusive-Meta testing a 'human concierge' for its new personal AI agent, Muse"(上記URL)。英語原文は未保存。台帳内の根拠で意味を判定すると、ロールバック=「テスト中の機能を取り下げる(撤回)」であり「過去の状態へ復元」ではない(根拠: (1)「ミス」と認めた文脈、(2)HC-014 notes「ロールバックされた人間コンシェルジュ実験」、(3)testset registry rationale「ロールバック=撤回→STOPPED、「当面」の一時性からPAUSEDも許容」)。ただし原文の語・再開の有無は未照合。

多義性: 「ロールバック」は(a)機能・変更の撤回/取り下げ(正) と(b)以前の状態への復元(Writerの誤読)の両義。「当面」が付くため(c)一時停止/(d)再開済み と読む余地もある。

Writer誤読の実例(逐語):
- `er052_output/open233_prod_e2e_02/runs/meta_run03_advanced.json` L331: "The company also restored the human concierge feature to the way it had been before, at least for now."(related_fact_id=MUSE-HC-012、決定論検査 negation_polarity_mismatch で差戻し。testset G-01、ラベル重大)
- testset_01 G-02: "They also temporarily put back the feature in which humans handled the calls."(gold A5-0、重大、期待AVAILABLE)
- testset_01 G-06: "The company also changed the human concierge feature back to how it was before, at least for now."(曖昧、G-01と近接)
- 人工反転 S-12/S-13: "Meta has restored the human concierge feature." / "put the human-call feature back in service."(決定論置換)
- 忠実文(対比): F-19 "For now, Meta has pulled back the human concierge feature."(STOPPED) / F-20 "temporarily put the human-call feature back on hold."(PAUSED)。同じ"put back"でも"on hold"か"in service"かで逆転する語であることが注目点。
- testset紐付き件数: 同一factに忠実文2・NOT_MENTIONED17・gold2・曖昧1・人工反転2(testset_01、計24、testset_02で24、testset_03で25)。N-xxの多くは「開示の欠如が問題」文で、Writerが1 factを周辺論点へ展開した例。

## B. HF-009(Hormuz、`er019_output/family_x_refresh_e2e_01/hormuz/run_03/ledger/verified_fact_ledger.txt`)

現行台帳block(逐語):
> [VERIFIED] HF-009: Yahoo Financeは、7月14日の撤回・投資案件への置換発表後、Brent先物が一時的に上げ幅を縮小したものの、ほどなく発表前に近い高い水準へ戻ったと報じた。記事掲載時点ではBrent先物は約2.6％高で、1バレル85ドルを上回っていた。
> scope: 国際指標Brent原油先物の短時間の値動き / conditions: 撤回発表以外にも、米・イラン間の攻撃、海上封鎖、タンカー安全上の懸念が継続していた。 / numeric_value: 約 +2.6%、$85/バレル超 (numeric_scope: 記事掲載時点のリアルタイムに近い価格スナップショット。日中高値でも終値でもない) / date_or_period: 2026-07-14、撤回発表後の取引時間中 / causal_strength: CAUSAL_STATED_BY_SOURCE
> notes_for_writer: 撤回後に原油価格が全面的に下落したとは書かない。観測されたのは一時的な上げ幅縮小と、その後の回復。

1 fact内の2要素(逐語): 【途中】「Brent先物が一時的に上げ幅を縮小した」→【最終】「ほどなく発表前に近い高い水準へ戻った。記事掲載時点では約2.6％高、85ドル超」。加えて「上げ幅縮小」は"上昇の縮小"であり"下落"ではない点、「戻った」の基準が"発表前に近い"(数値なし)である点も曖昧。原文(Yahoo Finance)は未保存・未照合。台帳側ラベル: testset registry は ledger状態=UNCHANGED(「一時縮小→高水準へ復帰=実質変化なし」)。

Writer側の文と状態(testset_01〜03):
- F-09/F-10(忠実、ledger全体=UNCHANGEDだが記事文=DECREASED): "After the fee plan was withdrawn and replaced, Brent crude oil futures briefly lost some of their gains." / "...briefly gave up some of their gains." → 1 factの前半(途中)だけを正しく述べた文。fact全体状態と文の状態が食い違い誤爆(誤重大)の原因になる(記事側にphase=途中/最終の区別がないと逆転と誤判定)。
- G-03(gold重大、委任_60): "After the plan was withdrawn, oil prices fell."
- G-04(K16、重大・時期型): "The fee plan left the stage, but the events driving oil prices—and the prices themselves—quickly returned."
- G-05(K19、QUALITY): "Just after the charge plan disappeared, prices began to fall. Soon, however, they returned to a high level."
- S-06(人工反転): "After the fee plan was reinstated and replaced, Brent crude oil futures briefly lost some of their gains." S-07: "...briefly added some of their gains."(INCREASED)
- held-out(trial_03): H-G1〜G3 "Oil prices dropped after the withdrawal." 等、H-F1 "Prices initially fell but recovered."(忠実)、H-F2 "Oil prices briefly dipped."、H-F4 "The drop was short-lived."
- 失敗構造: 「途中」だけ/「最終」だけを切り出した文は、どちらも元factの片側として正しく、台帳が"全体=UNCHANGED"1状態しか持たないため判定がぶれる(Opus REVIEW-03の「phase次元」指摘と整合)。

## C. 曖昧Fact棚卸し(Meta 15 + Hormuz 12 = 27 fact)

観点: i多義語/抽象動詞、ii複数事象、iii主体・相手先省略、iv因果強度(causal_strength欄)、v時点、vi否定・限定。度=高/中/低(目視判定、機械検査は用語・欄の有無のみ)。「使用」=既存testset/goldでの使用(testset_01〜03のfact_registry)。ER系の過去検出(HF-007 B3等)はtestset記載外のため対応は名称のみ。

| fact | 度 | 該当観点と根拠語 | 過去事例/使用 |
|---|---|---|---|
| HC-001 | 低 | 日付・主体明示 | 未使用 |
| HC-002 | 低 | 「交渉する」「必要な権限が付与された場合」(vi条件あり) | 未使用 |
| HC-003 | 低 | 2文だが設計説明のみ | 未使用 |
| HC-004 | 低 | Reuters報道転載(iii報道主体) | 使用(ND-01) |
| HC-005 | 中 | ii「8月から従業員にテスト」+「公開後数日間に段階展開」の2段階、v「8月〜9月中旬」 | 未使用 |
| HC-006 | 中 | iii/vi「一部の電話」「テスト」、「human concierge」と「human agent calls」併記 | 使用(ND-04/05)、HC-006 A4-0対応 |
| HC-007 | 中 | v/vi「半数」の分母不確定(draft ambiguity明記)、「有効化」 | 未使用 |
| HC-008 | 中 | ii人間の成功率とAI単独(数値なし)の2要素、vi「可能性が示された」、iv OBSERVED_REPORTED | 未使用 |
| HC-009 | 低 | 「AIだと認識した相手」限定あり、iv OBSERVED_REPORTED | 未使用 |
| HC-010 | 中 | vi「意図せず共有される可能性」(懸念であり事実ではない)、iv | 使用(ND-03) |
| HC-011 | 低 | 1件の従業員報告と明記、iv | 未使用 |
| HC-012 | 高 | i「ロールバック」、v「当面」、iv NOT_APPLICABLE | 使用(G-01/02/06、A5-0、重大) |
| HC-013 | 中 | ii「反応」と「目的」の2事項、vi「圧倒的に肯定的」は主張 | 使用(ND-02) |
| HC-014 | 中 | iii「商業者との改善」(商業者=?)、i「公開展開」、v 9/22時点、vi条件付き | 未使用 |
| HC-015 | 低 | 公式仕様の列挙、日付明示 | 未使用 |
| HF-001 | 中 | i「再確認」「維持すべき」(規範表現)、v開催期間と公表日の併記、iv因果なしnotes | 未使用 |
| HF-002 | 中 | i「償還を求める」(課税/料金との混同余地)、v時刻明示 | 使用(S-10、HF-002対応、期待STARTED) |
| HF-003 | 中 | vi否定+列挙(徴収主体...法的根拠)、方向性なし | 使用(F-16〜18、S-11)、HF-003 A2A3-0対応 |
| HF-004 | 中 | iii「別の専門家試算」(主体省略)、ii2種の試算、vi仮定 | 未使用 |
| HF-005 | 低 | OHLC数値、numeric_scope明示 | 未使用 |
| HF-006 | 中 | ii清算値+「Reutersが関連付けた」の2事象、iv CAUSAL_STATED_BY_SOURCE | 未使用 |
| HF-007 | 中 | i「置き換える」(撤回と置換の同居)、v時刻、iv CAUSAL_STATED | 使用(F-11〜13、S-08/09)、HF-007 B3対応 |
| HF-008 | 低 | 「好まない」発言、v「置換発表後」 | 未使用 |
| HF-009 | 高 | ii「途中の上げ幅縮小」+「最終の高水準」、「戻った」の基準が曖昧 | 使用(F/G/S/H多数、K16/K19) |
| HF-010 | 低 | OHLC、numeric_scope明示 | 未使用 |
| HF-011 | 中 | ii上昇+「2営業日連続で6月12日以来の高い清算値」、conditions内に撤回併記、iv OBSERVED_REPORTED | 使用(F-21、S-14)、HF-011対応 |
| HF-012 | 高 | ii「発言→WTI一時マイナス圏→攻撃報道→回復」の3段、i「開放する」「マイナス圏」(前日比か価格か不明、原文未確認)、WTIとBrentの混同余地 | 未使用 |

集計: 高3(HC-012/HF-009/HF-012)、中14、低10(合計27)。ER-012 B4-a等は本testsetに記載がなく、対応付けは未確認(要_01d/PM照合)。

## D. held-out候補(未使用fact、testset_01〜03のfact_registryに無い、曖昧度中以上、8件)

| fact | 度 | 理由(逐語根拠) |
|---|---|---|
| HF-012 | 高 | HF-009と同型の「途中/最終」: 「WTI先物が一時マイナス圏へ転じ、その後...価格が回復した」。「マイナス圏」が価格か前日比か原文未確認。WTI/Brent混同も誘発。過学習検査の最良候補 |
| HC-014 | 中 | 「商業者との改善を続け、準備が整い...公開展開する」。公開展開vs人間コンシェルジュ撤回の区別(notes)。HC-012と隣接するが別事象 |
| HC-008 | 中 | 「成功率が95〜98%に達する可能性」+「AIだけ...低い」。比較の方向(人間>AI)がWriterで強調され得る |
| HC-005 | 中 | 「8月から従業員にテスト」と「公開後数日間にユーザー向け段階展開」の時系列2段 |
| HC-007 | 中 | 「半数」分母不確定+「オプトアウト」。数量系の曖昧 |
| HF-006 | 中 | 「7.29ドル、9.59％上昇」+「Reutersが関連付けた」。因果強度(CAUSAL_STATED_BY_SOURCE)の取り違え |
| HF-004 | 中 | 「約3400万ドル」と「別の専門家試算約3200万ドル」。仮定試算を実額と誤読する余地 |
| HF-001 | 中 | 「再確認した」「維持すべき」(規範)を「決定/規制」と誤読する余地。7/14撤回との因果なし |

他fixture存在確認(Globではなく全走査、内容hash別): 台帳(verified_fact_ledger.txt)は`er019_output`配下に3種のみ。(1)Meta 15 fact(コピー7箇所、本棚卸し対象)、(2)Hormuz 12 fact(コピー8箇所、同)、(3)small_bag 17 fact(`family_x_b3_diversity_trial_01/small_bag/run_01/research_ledger/`、コピー2箇所、英語台帳・F001〜F018でF014欠番・notes_for_writer欄なし)。(3)は本棚卸し未実施(深掘り不要の範囲)。ただし別テーマ・方向語を含む(F002「scaled-down minis were being displaced by capacious totes」、F009「contrasted tiny summer purses with autumn's return to more substantial bags」)ため、過学習防止の第3テーマとして候補。要_01c/PM判断(書式差=英語・notes欄なし)。

## E. Before/After案(【案】。原資料との意味一致は未確認。台帳は未変更)

### E-1. HC-012
【案1: ID維持・本文明確化】
> MUSE-HC-012: MetaのSuperintelligence Labs部門の副社長は、適切な開示なしに契約スタッフが電話をかけるテストを開始したことを「ミス」だったと認め、人間コンシェルジュ機能(契約スタッフが電話を担当する機能)を当面取り下げたと社内投稿で説明した。以前の状態への復元ではない。
【案2: 子事象へ分割】
> HC-012a: (同副社長は)適切な開示なしに契約スタッフが電話をかけるテストを開始したことを「ミス」だったと認めた(社内投稿)。
> HC-012b: (同副社長は)人間コンシェルジュ機能を当面取り下げたと社内投稿で説明した。再開時期・対象範囲・代替方式は未公表。
自己チェック: 追加情報=案1の「以前の状態への復元ではない」は台帳内根拠(HC-014 notes・testset rationale)からの派生で原文確認が必要(追加情報の疑い、要確認)。「取り下げ」への言い換えが原文の意味(撤回/一時停止)と一致するか未確認。失われた関係=案2はa(ミス認定)とb(取り下げ)が同一投稿で述べられたという同時性、案1にある「ミスと認めた上で取り下げた」の連結がnotesへ移す必要(因果は台帳に明記なし、断定不可)。「当面」(一時性)は両案で維持。

### E-2. HF-009
【案1: ID維持・本文明確化(時系列番号)】
> HF-009: Yahoo Financeは、7月14日の撤回・投資案件への置換発表後、Brent先物について、(1)まず一時的に上げ幅が縮小した(値下がりではない)が、(2)ほどなく発表前に近い高い水準へ戻ったと報じた。記事掲載時点ではBrent先物は約2.6％高で、1バレル85ドルを上回っていた。
【案2: 子事象へ分割(順序・対象・関係を明示)】
> HF-009a(途中): Yahoo Financeは、7月14日の撤回・置換発表後、Brent先物が一時的に上げ幅を縮小したと報じた。
> HF-009b(その後・最終): 同報道によれば、その後ほどなく、Brent先物は発表前に近い高い水準へ戻った。記事掲載時点では約2.6％高、85ドル超だった。
> 関係: 9bは9aの後、同一報道・同一対象(Brent)、縮小は一時的で最終的には高水準。全体として全面下落ではない。
自己チェック: 追加情報=案1「(値下がりではない)」はnotes由来の解釈で、原文確認要。conditions(攻撃・海上封鎖・安全上の懸念が継続)と数値スコープ(スナップショット、高値でも終値でもない)は両案で子事象bへ継承が必要(欠けると失われる)。失われた関係=案2はa/bのtemporal連結(「一時的」「ほどなく」)を明記しないと分断され、aだけがWriterに選ばれると「価格が下落した」誤読(G-03/G-05型)が起きる。案2はfact数が1→2に増え、fact選択・ID参照(testset/gold/selected_brief)への影響は_01aで確認要。
