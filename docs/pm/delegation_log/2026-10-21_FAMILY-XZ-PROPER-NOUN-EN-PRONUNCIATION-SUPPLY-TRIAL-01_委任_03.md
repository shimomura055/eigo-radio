# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-XZ-PROPER-NOUN-EN-PRONUNCIATION-SUPPLY-TRIAL-01 委任_03(Fable最終ラベルの記録+Opus台帳R-03補完+Perplexity利用枠切れの事実記録。API 0・費用JPY0・コード変更なし)。並行agentなし。

## Fable最終ラベル(記録用、変更しない)
- **Status = `USER_DECISION_REQUIRED`**(Trial終了)。理由: (a)機構(検出→調査→validator→Trial Ledger登録→Phrase List供給→重み2.0の実投入証拠)は動作確認済み・設計外API呼出0・誤登録0・実Ledger不変・Production diff 0(安全面OK)。(b)必須要件K1(byUsの英語発音を根拠付きで登録→PL供給)は**要件未達**: 英語の公式発音情報が存在せず(公式は日本語読み「バイアス」のみ)、設計どおり安全終了(登録0)。達成にはJ7(権利者の公式な日本語読みが英単語と一意対応する場合の登録可否)のユーザー判断が必要。(c)効果は限定的(腕Mで多語化3例中1例NG→PASS)で、研究費用は約5〜16円/名=原価悪化寄り。(d)PLが実発音の誤り(Lion)を転写上で隠す経路が実在(誤PASSは未発生だが運用注意)。REJECTEDではない(誤登録・誤PASS増・Ledger悪化・Production影響なし)。Production採用は未承認。
- 新事実(別件): Perplexity APIがHTTP 401 insufficient_quota(利用枠切れ)。Production資産`research_pronunciations`(固有名詞Human Reviewパッケージ充実用)が現状動作しない可能性。復旧は外部課金=ユーザー側。

## 作業
S0. T-0: `docs/pm/delegation_log/2026-10-21_FAMILY-XZ-PROPER-NOUN-EN-PRONUNCIATION-SUPPLY-TRIAL-01_委任_03.md`へ逐語保存(`.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out <path>`、N=「PRONUNCIATION-SUPPLY-TRIAL-01 委任_03」を含む最新index)。check結果1行。
S1. `docs/pm/OPUS_FINDINGS_LEDGER.md` OF-PNEP-R-03行を補完: 要旨=「M1の発動範囲拡大と取消手段。承認範囲内(2026-10-13 M1原文はLedger増加を前提)だがM1 C2はconfidenceで候補を絞らず、登録validatorだけが品質を守る。自動/人手entry区別(OPEN-339)未解決。採用時はPL/M1用disableが前提条件」、Fable判定=ADOPTED(Trial: Z1のM1受理分を全件出力→結果: hypo条件でもM1候補集合16/16不変[既存melos entryと同音素列のため、拡大懸念は未反証])、Status=RESOLVED_FOR_TRIAL/J6へDEFERRED。
S2. `OPEN_ITEMS.md` OPEN-434行頭Statusを`USER_DECISION_REQUIRED(Trial終了: 機構VALIDATED相当・必須要件K1未達[英語公式発音なし→安全終了]・効果限定・原価悪化寄り。採用はユーザー。J2/J3/J6/J7)`へ(旧Status保持)、行末にFable理由(a)〜(d)+Perplexity 401事実。
S3. `docs/pm/USER_DECISION_REGISTER_01.md`追記節`### 2026-10-21 PNEP 委任_03追記`に: #133(UDR・未回答)「固有名詞英語発音供給の扱い: (ア)J7を認めて再Trial[byUs登録→PL供給の実証] (イ)現状維持(CMU層+人間承認)で採用見送り(Fable推奨) (ウ)綴りのみPL供給(J2)の限定採用Trial」、#134(UDR・未回答・外部課金)「Perplexity API利用枠切れの復旧要否(Production `research_pronunciations`が動作しない可能性。代替=OpenAI web_search[高コスト]か、復旧か、固有名詞HRパッケージの縮退を許容か)」。
S4. `DECISION_LOG.md`末尾に1件(②Trial終了・Fableラベル・根拠・費用JPY113.10・Opus Go条件4点反映・原文path+sha256 7da03fa5…[本文のみ]・Production未変更)。REPORT_LEDGER 1行、ACTIVE_TASK先頭追記(UDR-blocking: #133/#134は非blocking[記事制作を止めない]、#131、#129)。
S5. secret scan→明示add→commit(`FAMILY-XZ-PROPER-NOUN-EN-PRONUNCIATION-SUPPLY-TRIAL-01 委任_03: Fableラベル USER_DECISION_REQUIRED記録+Opus台帳R-03補完+REGISTER #133/#134(Perplexity枠切れ)`)→`git push origin HEAD:main`→到達確認。

## 報告(docs/pm/RESULT_PACKET_PNEP3.md 上書き)
各反映行番号、commit hash、raw URL、4行判定。