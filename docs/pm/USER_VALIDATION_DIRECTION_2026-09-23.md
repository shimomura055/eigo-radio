# ユーザ実検証(2026-09-23時点)と今後の開発方向性 — PM記録

管理ID: PM-USER-VALIDATION-DIRECTION-RECORD-01 / 作成日: 2026-09-23 / 性質: PM背景情報(SSOTではない。正式仕様はCURRENT_SPEC.md、決定はDECISION_LOG.md、未決事項はOPEN_ITEMS.md) / Status: RECORDED

## 1. ユーザ実検証の前提

- 現時点で9名分の回答を確認済み
- 有料モニター分は回答完了
- 今後追加回答が来る可能性はあるため、最終結果ではない
- ただし今後の開発方針を考えるには十分な示唆が得られたため、現時点の結果を開発判断に利用する

## 2. 基本品質について

- 英語の聞き取りやすさ、速度、エピソード長等は概ね高評価
- 1エピソードの長さは9/9で「ちょうどよい」
- 基本的な音声教材品質を大きく崩す必要は現時点ではない

## 3. 主な課題・示唆

- 「良い英語教材」であるだけでは、継続利用・有料利用の十分な理由にならない
- ユーザーが聞きたくなるテーマ自体の魅力が重要
- 数字、複数調査、抽象論が多い記事は音声だけでは理解しづらいというFeedbackあり
- Evidenceを大量に提示することより、1つの分かりやすい中心命題を持つことが重要
- 身近、生活に役立つ、好奇心を満たす、思わず答えを知りたくなるテーマを増やす
- 政治・国際ニュースだけに偏らない

## 4. 競合認識(DMM Daily News)

- DMM Daily Newsを現時点の主要Benchmarkとする
- DMMは、無料/更新量が多い/AI音声品質も比較的高い/Vocabulary、例文、発音記号、Questions等も充実 しており、「英語News＋音声＋Vocabulary」というだけでは十分な差別化にならない
- eigo-radioの重要な差別化方向は、「そもそも記事そのものを聞きたくなるコンテンツに編集し、その上に英語学習体験を載せる」こと

## 5. 今後の大きな方向性

- Topic Selection自体を重要なプロダクト課題として扱う
- 将来的には魅力的なテーマ候補を自動で発見・選定できる仕組みが必要
- NewsはEvidence-firstから、Core Idea / Core Questionを中心にした設計へ見直す方向
- Evidenceは主役ではなく、事実確認・現実接続・Core Idea補強に使う方向
- Voicesは概ね好評だが、引用後の抽象的なまとめを分かりやすくする余地あり
- Futureは将来的にFuture限定ではなくFiction / 小説系として広げる方向を検討
- Fictionは同じテイストに偏らない多様性が課題
- 「ながら聴き専用」にはせず、Audio-firstと画面学習の2本柱を想定
- Key Phraseは独立した改善課題として今後検討
- 有料PMF / Pricingは記事品質・差別化・Learning UX改善後に改めて検証する

## 6. 重要なStatus注意

この文書は、ユーザ実検証から得られた示唆/今後のProduct Direction/将来のTrial設計に使うPM背景情報 を記録するものである。以下を意味しない。

- 各項目の具体仕様がAPPROVED_FOR_PRODUCTIONになった
- 新しいNews方式が正式Production仕様になった
- Future→Fiction変更が正式仕様になった
- Key Phrase仕様変更が承認された
- Learning UI仕様が確定した

個別仕様は、その開発に着手する際に別管理IDでTrial・ユーザー判断・Production Gateを適用すること。

## 7. 既存SSOTとの照合結果(要約、2026-09-23 PM-USER-VALIDATION-DIRECTION-RECONCILE-01)

- 音声向け情報設計(数字・調査・抽象論の密度)は既存`OPEN-164`(2026-09-17起票、DEFERRED、量産開始前に方針決定)と同一論点。
- Voicesの立場純化は`OPEN-167`で審議中。「引用後のまとめの抽象性」はその7論点に含まれない隣接論点で、該当segmentは`Tension`(二次的に`Closing`)。
- Family C(Future Story)でProduction仕様として記録されているのはStory TTS分割とA2 Comment Contractの2点のみ(`APPROVED_FOR_PRODUCTION / WIRING_INCOMPLETE`)。Writer方式・Core Provocation選定方式はProduction仕様として未記載。
- Key Phraseの現行`DECIDED`仕様は「English→Japanese→English、英英説明は不採用」(2026-08-17)。「日本語音声不要」「英語で意味説明」はこの仕様と競合するため、着手時に仕様再検討の要否をユーザー判断する。
- 量産APIコスト最適化`OPEN-143`(DEFERRED、trigger「ユーザー実検証後」)は着手時期未決。
- Topic Selection自動化・DMM差別化原則・Learning UX・Pricingは既存SSOTに言及なし(新規論点)。
- PM_GOVERNANCE 13節(新規記事テーマはユーザーが選定)は、候補生成の自動化と両立可能(最終選定はユーザー)。

## 8. 参照

- `DECISION_LOG.md`エントリ`PM-USER-VALIDATION-DIRECTION-RECORD-01`
- `OPEN_ITEMS.md`(OPEN-143/164/167)
- `CURRENT_SPEC.md`(B1 Key Phrase節、Family C節)
- `docs/pm/PM_GOVERNANCE.md` 13節
