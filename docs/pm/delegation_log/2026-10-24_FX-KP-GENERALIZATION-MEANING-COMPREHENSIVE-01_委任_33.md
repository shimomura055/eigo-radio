FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_33(Fableから、API 0): Opus第二評価のラベルを保存し、Fable+Opus二重判定(厳しい側採用)で集計、Trial_06のCloseout記録とSSOT更新、UDR登録、commit/pushまで。

## 1. Opusラベル保存
`TRIAL_06/opus_labels_06.json` に以下を逐語保存(100セル):
{"1:A":"PASS","2:A":"PASS","3:A":"PASS","4:A":"PASS","4:B":"THIN","5:A":"THIN","6:A":"PASS","6:B":"PASS","7:A":"FAIL_LIT","7:B":"PASS","8:A":"PASS","8:B":"PASS","9:A":"PASS","9:B":"PASS","10:A":"PASS","10:B":"THIN","11:A":"PASS","11:B":"PASS","12:A":"PASS","12:B":"PASS","13:A":"PASS","13:B":"PASS","14:A":"PASS","14:B":"PASS","15:A":"THIN","16:A":"PASS","17:A":"PASS","18:A":"PASS","19:A":"THIN","19:B":"PASS","20:A":"PASS","20:B":"THIN","20:C":"PASS","20:D":"PASS","21:A":"PASS","21:B":"PASS","21:C":"PASS","22:A":"PASS","22:B":"PASS","22:C":"THIN","23:A":"PASS","23:B":"PASS","24:A":"PASS","24:B":"THIN","25:A":"PASS","25:B":"PASS","26:A":"PASS","26:B":"THIN","27:A":"PASS","27:B":"PASS","28:A":"PASS","28:B":"THIN","29:A":"THIN","29:B":"PASS","29:C":"PASS","30:A":"PASS","30:B":"PASS","31:A":"THIN","31:B":"PASS","32:A":"PASS","32:B":"PASS","33:A":"THIN","33:B":"PASS","34:A":"PASS","34:B":"PASS","35:A":"PASS","35:B":"PASS","36:A":"PASS","37:A":"PASS","37:B":"THIN","38:A":"PASS","38:B":"PASS","39:A":"PASS","39:B":"FAIL_LIT","40:A":"PASS","40:B":"PASS","41:A":"PASS","41:B":"PASS","41:C":"PASS","41:D":"PASS","42:A":"PASS","43:A":"PASS","43:B":"PASS","44:A":"PASS","44:B":"PASS","45:A":"PASS","45:B":"PASS","45:C":"THIN","45:D":"FAIL_LIT","46:A":"PASS","46:B":"PASS","47:A":"PASS","47:B":"PASS","48:A":"PASS","49:A":"PASS","49:B":"THIN","50:A":"PASS","50:B":"THIN","51:A":"PASS","51:B":"PASS"}
Opusの理由(THIN/FAIL)は `TRIAL_06/OPUS_EVAL_06.md` に逐語で保存(本委任文末尾【Opus理由】)。

## 2. 集計(厳しい側採用、継承ラベル含む=スクリプト既定)
`py er112_kp_gm_trial_06_blind2.py agree --labels1 TRIAL_06/fable_labels_06.json --labels2 TRIAL_06/opus_labels_06.json` → `TRIAL_06/AGREE_06_FINAL.md`。加えて次を表にする:
(a) Fable–Opus一致率(100セル、ラベル完全一致/PASS・非PASSの二値一致)。
(b) arm別分布 HC/R/S2 × B0p/X2pp を3通り並べる: Fable単独 / Opus単独 / 厳しい側(継承込み)。
(c) X2ppの非PASS全セルを列挙(KP・文字列・Fable/Opus/継承ラベル・理由種別[字義訳/持ち込み/説明的/含意欠落/ずれ])。
(d) TRIAL_DESIGN_07 §3 事前基準 (b)(1)〜(4)、(b')、(c)(1)〜(4) の基準値と実測値(3通り)。
(e) 持ち込み検出(record-only)5件/2件の目視確認: 各hitの文字列と「真の持ち込み/偽陽性」(機械検出の説明のみ、合否ラベルには使わない)。
(f) 費用・時間: METRICS_06の値(S2単価、1記事セット換算増分0.438円、level時間増分25.8s、記事セットあたりの推定時間増分=level数×増分)。
(g) Family別: HCのうちZ小説5KPのB0p/X2pp分布、X(残り)の分布。

## 3. Fable判定(逐語で `TRIAL_06/TRIAL_RESULT_06.md` に記録。DRAFTの欄を埋める)
- 字義訳の根本問題: X2p'は新難例9KP(18出力)で字義訳0・FAIL 0、元難例R集合でもFAIL 0(継承ラベル厳しい側で1件FAIL_LIT=『賞の形をした問いかけ』、今回のFable=THIN・Opus=PASS)。現行B0pは新難例で字義訳1・THIN2。**字義訳の解消は本番相当構成でも再現**。過剰解釈(字義が正解のKP)=0。
- 新規悪化: 通常KP(Stage 2 54KP)でPASS→THIN(意味は誤りでないが弱い・説明調・対象の持ち込み)が、Fable単独2件、厳しい側採用では(集計値)件。PASS→FAIL系は0。持ち込み検出(機械)はB0p 2→X2pp 5(偽陽性疑い含む)。
- 事前基準との照合: (c)(2) PASS→THIN≤2/54 は厳しい側採用で(集計値)、(b') R集合のFAIL系0は継承ラベル採用で不適合、(4)持ち込み検出は増加。**事前基準を全ては満たさないため、FableはVALIDATEDを宣言しない**。REJECTEDとも判定しない(根本問題=字義訳は解消し、悪化はTHIN級に限られ、単価増+0.44円/記事セット[0.6%]のため)。
- **Trial最終Status: USER_DECISION_REQUIRED**(品質トレードオフ: 意味の誤り[字義訳]の解消 vs 通常KPでの弱い訳の微増+単価0.6%増)。TRIAL_DESIGN_07「Prompt修正は1回のみ」を守り、本Trial内で追加のPrompt調整は行わない。
- X/Y/Z適用: Xが主対象(比喩KP 15.4%)。ZはHC 5KPの結果を(g)で示し、比喩KP発生率2.2%のため「Z除外」または「X/Z共通」をユーザー判断の選択肢に含める。Yは共通KP段(`er003_v1_n3_01_scaffold_generate.py` align_glosses)に依存し、OPEN-484(Y正式経路)と同時に配線される構造(実装なし)。

## 4. UDR登録・SSOT
- `docs/pm/USER_DECISION_REGISTER_01.md` に **UDR #179(新規・未回答・非blocking)**: 件名=KP① X2p'(意味確定段付きgloss生成)の採否。選択肢=(A)X2p'を採用候補として確定し、Production採用の正式判断へ(配線はユーザー承認後、WIRING_DESIGN_07に従い単一commit・revert撤退、持ち込み件数のrecord-only監視付き。Z適用はA-1=X/Z共通 / A-2=Xのみ) / (B)説明調・持ち込みを抑える規則を1回だけ追加して再検証(約20円、KP累計約335円/500円。改善見込み中) / (C)現行維持(REJECTED)。Fable推奨=A(理由: 学習者に誤った意味を教える字義訳を本番構成で0にできた一方、悪化は「正しいが弱い訳」に限られ単価増0.6%。弱い訳は配線後の監視と定訳辞書で漸減できる)。※Fable推奨は記録のみ、採用判断はユーザー。
- `OPEN_ITEMS.md` OPEN-474 に Trial_06結果とStatus 1行。`DECISION_LOG.md` 1エントリ(Trial_06集計・Fable判定・UDR #179)。`CURRENT_SPEC.md`は触らない。
- 予算: 本委任0円。KP累計314.74円/500円、10-24日次(把握分)約433円/1,000円を `BUDGET_LOG_T6_01.md` 末尾に記録。
- Opusが挙げた盲検表の設計課題(継承セルの識別、add up再照合不成立、someone's→one's正規化、語義選択と持ち込みの境界、leap/jump重複)を `TRIAL_06/EVAL_DESIGN_ISSUES_06.md` に記録(次Trialがあれば反映。本Trialでは再計算しない)。

## 5. Git
`git status`でindex確認→`git commit --only -- <本委任ファイル>`→`git push origin HEAD:main`。`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・reset --hard・checkout -f禁止。他agent(Family Y 委任_24)の未commit差分を巻き込まない(SSOTは一時index方式)。secret grep 0件。
委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-24_FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01_委任_33.md`(Nは先頭「FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_33」を含むAgent呼出の0始まり通番、直近456以降)。

## 6. handback
(a)〜(g)の数値(特に厳しい側でのS2 PASS→THIN件数とX2pp非PASS一覧)、UDR #179登録確認、commit hash、raw URL。

【Opus理由】
- 4:B THIN(狭い/ずれ): 「大ざっぱ」は「粗い・不正確」の意味に寄る。too broad は「範囲が広すぎる」。
- 5:A THIN(説明的): 「greener grass」は名詞(よく見える他人の境遇)なのに、glossは「〜こと」という現象の説明になっている。
- 7:A FAIL_LIT(字義訳): 「カーテンの裏に」では「陰で操る者」という本文の意味が伝わらない。
- 10:B THIN(説明的): 定義文になっていて、句の訳になっていない。
- 15:A THIN(持ち込み:対象): come down 自体には「値(価格)」は含まれず、本文の価格を持ち込んでいる。語義の選択としては正しいので、厳しい側でTHINにした。
- 19:A THIN(狭い): keep company は「話し相手」に限らず、「そばにいて寂しくさせない」全般を指す。
- 20:B THIN(持ち込み:対象): KPの them を「人々」に特定している。過剰解釈ではない。
- 22:C THIN(説明的): 「誰かの脚が体を支えられなくなる」は説明文で、「誰かの」も不自然。
- 24:B THIN(持ち込み:主語): 本文の the weight in my chest を「気持ち」として持ち込んでいる。
- 26:B THIN(含意欠落): brace の「身構える・覚悟する」が抜け、「備える」だけになっている。
- 28:B THIN(説明的): 「支払いに備えて」で句の意味を説明している。さらに「誰かの財布」と組み合わさって、他人の財布で払うようにも読めてしまう。
- 29:A THIN(ずれ): 「こわばる」は緊張・恐れの方向に寄る。本文は支配者の顔が険しく、冷たくなる場面。
- 31:A THIN(説明的/持ち込み:主語): 「人間だと明かす」は本文の事情を説明的に持ち込んでいる。
- 33:A THIN(説明的): 「〜状況」で終わる長い説明句になっている。
- 37:B THIN(含意欠落): 喜ぶ・勝利の含意がなく、動作の字義だけ。日本語の「こぶしを突き上げる」は抗議にも読める。
- 39:B FAIL_LIT(字義訳): 「ハンドルを握る」は日本語では運転の字義が中心で、主導権の意味が伝わらない。
- 45:C THIN(ずれ): 「規則が摩擦のように感じられる」から「人がやりにくさを感じる」へ構文の主体が移っている。意味は近い。
- 45:D FAIL_LIT(字義訳): 日本語の「摩擦」は対立・衝突(貿易摩擦など)の連想が強く、「邪魔・負担」の意味が伝わらない。
- 49:B THIN(狭い/持ち込み:対象): picture(状況・全体像)を本文の話題に引きずられて「傾向」に狭めている。
- 50:B THIN(字義訳): 擬人化の字義のままで、「出費に驚く」という意味の伝達が弱い。
- 再照合: add up(1:A)PASS(否定の持ち込みなし。否定入り文字列が無く再照合は不成立)。reach for someone's wallet 28:A=過去のユーザー判断と整合させPASS(「誰かの財布」は他人の財布に読まれやすい注記)、28:B=THIN。
- 過剰解釈: 字義が正解の対照(20・21・41)で解釈訳化なし。41は4件ともPASS。
- 設計課題: (1)継承セルが識別できない (2)add up再照合不成立 (3)KP表記 someone's/harden の正規化揺れ、所有格はone'sに統一が望ましい (4)語義選択と持ち込みの境界を基準に明記 (5)leap/jump into actionの重複。