FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_34(Fableから、Read-only調査・再報告のみ。Trial・Prompt・仕様・Productionコードの変更禁止、未承認改善案の採用禁止、API 0、Git変更はユーザー原文と委任文の逐語保存+調査報告書の追加のみ)。

ユーザー依頼: 「Key Phrase日本語意味の字義訳問題(`draw a line`→『線を引く』に代表)の経緯・現状の再報告」。ユーザーが過去経緯を確認できなくなったため、報告済み内容も省略せず最初から再構成する。不明は推測せず「未確認」。**一般的な日本語gloss自然化対策(Production既存)と、字義訳問題(課題①)の解決とを混同しない。ユーザー承認/コード実装/正式runtime確認を区別。**

## 0. 保存
- ユーザー原文(本委任文末尾【ユーザー原文】、逐語)を `docs/pm/delegation_log/2026-10-24_FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01_USER_08.md` に保存。

## 1. 調査(節単位Grep、全文読込禁止)
- `DECISION_LOG.md`/`DECISION_LOG_HISTORY.md`: Grep「字義」「draw a line」「線を引く」「gloss」「課題①」「X2p」「KP-GENERALIZATION」「GLOSS_ALIGNMENT」「G1」「G3」「検査方式C」。各該当エントリの日付・決定内容・管理IDを時系列に。
- `OPEN_ITEMS.md`(+HISTORY): OPEN-474(本体と履歴)、関連OPEN(gloss自然化・G1/G1'・検査方式等)、Status。
- `docs/pm/USER_DECISION_REGISTER_01.md`: #169(A-1)、#173(②配線/①)、#178(補強Trial予算)、#179(X2p'採否、未回答)、それ以前の字義訳・gloss関連UDR(Grep「字義」「gloss」「draw a line」)。
- `CURRENT_SPEC.md`: KP gloss節(gloss alignment `EIGO_KP_GLOSS_ALIGNMENT`、G1/G1'、「他の文脈でも再利用できる訳」句、A-1、課題②)。何が「承認済みProduction仕様」で何が「Trial」か。
- `docs/research/FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01/`: ROOT_CAUSE_*(特に04)、DESIGN_07、TRIAL_DESIGN_05/06/07、TRIAL_05/TRIAL_RESULT_05、TRIAL_06/TRIAL_RESULT_06、OPUS_REVIEW_07/08、ADOPTION_PROPOSAL_01/02、GOLD_LABELS_FINAL_01(draw a lineのgold)、PROD_WIRING_EVIDENCE_07〜09、WIRING_DESIGN_06/07。ユーザー原文 `docs/pm/delegation_log/2026-10-24_FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01_USER_0*.md`(特に_05 wallet判断、_07 ①の指示、_08[今日の補強Trial承認])。管理IDの前身(例: FX-KP-*、KP字義訳の最初の発見記事)もGrepで辿る(`docs/research/` と `docs/pm/delegation_log/` を「字義」「draw a line」で検索)。
- コード: `er003_key_words_gloss_alignment.py`(G1/G1'の内容=何を検査・修正するか)、`er003_key_words_canonicalization.py`、`er003_v1_n3_01_scaffold_generate.py:525-545`(align_glossesの呼出とflag)、`er003_v1_translator_briefs/*gloss*`/canonicalization template(「他の文脈でも再利用できる訳」句の所在)、X/Z/Y各Familyの呼出経路(er019/er062/er026/er110)とretry/fallback/regenerationでの適用(KP再生成経路があるか)、`er112_kp_gm_trial_0*.py`(DEV専用、Production未import)。

## 2. 報告書 `docs/research/FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01/HISTORY_REPORT_01.md`(ユーザー原文§1の①〜⑤に対応。各事実に出典[ファイル:行 or エントリ日付/ID]を付ける。推測は書かず「未確認」)
① 発端: 最初に発見した記事・KP・出力された日本語gloss・適切な訳・事例数(draw a line以外の字義訳例: 例 `question shaped like a trophy`→「トロフィーの形をした質問」、`reach for someone's wallet`→「人の財布に手を伸ばす」のユーザー判断[PASS]等、Trial_05 hard-core 12KPのB0 10/12 FAIL等)。
② 原因: ROOT_CAUSE_04の結論(意味確定段の欠如=主因、文脈限定句=増悪因子、型=新造/断片化比喩)、既存Prompt・G1/G1' Validator・QAが防げなかった理由、過去Trial(Trial_02〜06)の結果要約と数値。
③ 対策とユーザー判断: 提案→採否の表(検査方式C=不採用[日付/原文]、Opus条件C=追加検証先行、X2p→X2p'、UDR #178承認[上限500円]、UDR #179未回答[A-1/A-2/B/C、Fable推奨A-2])。一般的gloss自然化対策(G1/G1'、gloss alignment)との関係=「存在するが字義訳は防げない」を事実で。
④ 現在のProduction実装: 字義訳対策(X2p')は**未配線・DEV専用**(VALIDATED未宣言・UDR #179待ち)。配線済みはA-1(UDR #169)と課題②所有格一般化(UDR #173、X/Z PRODUCTION_WIRED、Y=OPEN-484)。Family別Status表、正式初回経路/retry/fallback/regenerationの適用状況(KP段が再実行されるのはどの経路か)、Validator/自動修正の有無(G1/G1'は何をするか)、runtime evidence/Regressionの所在。
⑤ 未解決: `draw a line`自体の現状(Production現行B0ではどう出るか=Trial_06 B0p出力「線引きをする」等の事実、gold label)、再発可能性(比喩KP発生率X 15.4%/Z 2.2%、字義訳NG 2.1〜3.5%)、関連OPEN/UDRとStatus、今後のユーザー判断(UDR #179)。
- 末尾に「報告済み内容からの差分」節(直近の報告=本日のTrial_06 Closeout報告との差分があれば)。

## 3. Git
- 報告書・原文・委任文逐語保存のみcommit(`git status`→`git commit --only`→`git push origin HEAD:main`、他agent差分を巻き込まない=一時index、禁止操作なし、secret grep 0件)。委任文逐語: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-24_FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01_委任_34.md`(Nは先頭「FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_34」を含むAgent呼出の0始まり通番、直近479以降)。

## 4. handback: 報告書の要点(①〜⑤を各5〜10行、出典付き)、未確認事項の一覧、commit hash、raw URL。

【ユーザー原文】
# Claude Codeへの指示
## Key Phrase日本語意味の字義訳問題：経緯・現状の再報告

`draw a line` →「線を引く」に代表される、Key Phrase日本語意味の字義訳問題について、過去の検討・判断・対応状況を再報告してください。

ユーザー側で過去の経緯を確認できなくなったため、**報告済みの内容も省略せず、経緯を最初から再構成すること**。

### 1. 報告してほしい内容

**① 問題の発端**
- どの記事・Key Phraseで問題が発見されたか。
- 実際にどのような日本語意味が出力されたか。
- 本来どのような訳が適切だったか。
- 単発の問題か、複数事例があったか。

**② 原因究明**
- なぜ字義訳が発生したのか。
- 既存のPrompt・Validator・QAがなぜ防げなかったのか。
- 過去に実施した調査・Trialの結果。

**③ 対策とユーザー判断**
- これまで提案した対策と、その採否。
- ユーザーが承認・却下・保留した内容。
- それぞれの判断日と根拠となる記録。
- 一般的な日本語gloss自然化対策との関係。

**④ 現在のProduction実装状況**
- 承認済み対策が実際に配線されているか。
- Family X／Y／ZそれぞれのStatus。
- 正式初回経路、retry／fallback／regenerationへの適用状況。
- Validatorや自動修正機構の有無。
- Production runtime evidenceとRegression結果。

**⑤ 未解決事項**
- `draw a line` の問題自体は解決済みか。
- 同様の字義訳が今後も発生する可能性。
- 関連するOPEN_ITEMS・UDRと現在のStatus。
- 今後ユーザー判断が必要な事項。

### 2. 調査対象

CURRENT_SPEC、DECISION_LOG、OPEN_ITEMS、関連Trial・実装報告、Prompt、Validator、Productionコードを照合すること。

古い記録と現行仕様を混同せず、**ユーザー承認・コード実装・正式runtimeでの動作確認を区別**する。

過去に報告済みであれば、その内容を再掲し、現在までに変更があれば差分を明示すること。

### 3. 報告形式

エンジニアではないユーザーが状況を理解できるよう、次の順序で報告する。

1. **結論：現在どう決着しているか**
2. 問題発見から現在までの時系列
3. 承認済み対策とProduction反映状況
4. 未解決の問題・品質リスク
5. 必要なユーザー判断と推奨方針

技術的な説明は必要最小限とするが、判断の根拠は省略しない。

### 4. 作業範囲

今回はRead-only調査・再報告のみ。

- 新たなTrialは禁止。
- Prompt・仕様・Productionコードの変更は禁止。
- 未承認の改善案を採用しない。
- 不明な事項は推測で補完せず「未確認」とする。

**最重要：一般的な日本語訳の自然化対策がProductionに存在することと、今回の `draw a line` の字義訳問題が解決済みであることを混同しないこと。**

Fableによる事実関係の照合を経て、現在の正確な状況を報告してください。