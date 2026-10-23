MARKER: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_21 (2026-10-24, Fable→sonnet-worker)

# 管理ID: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_21(課題① 日本語意味の字義訳: 原因究明のやり直し→根本対策候補の立案→Trial設計。API 0円・Production変更0・SSOT編集なし。Opus独立レビューはFableが起動)

## 0. ユーザー決定(2026-10-24、原文は別agent[委任_20]が `docs/pm/delegation_log/2026-10-24_FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01_USER_07.md` に保存中。保存前なら本委任末尾§Zを参照)
- 課題①: 検査方式Cは現段階でProduction採用しない(字義NG 6→1の効果はあるが検出19件中14件が修正不要)。**原因究明からやり直し**、「LLMが確率的に字義訳を選ぶ」で終わらせない。生成後検査ありきでなく**正しい意味を最初から生成する方法を優先**、既存call内の改善を優先し追加LLM callを極力抑える。Opus独立レビュー(原因分析・対策案・見落とし・既存Trialとの重複)。Trialの自己ループは承認済み範囲内で自律。採用はユーザー判断。
- 課題②(所有格一般化)は別委任_20が並行してProduction配線中。**本委任は②のコード・SSOTに触らない**。

## 1. 解明すべき7点(ユーザー§2-2。各項目に証拠=ファイル・行・実例・集計を付けて回答)
 1. なぜ本文の文脈から適切な意味を取得できず字義訳を選ぶのか。
 2. Key Phrase選定時点で表現の意味・文脈が失われていないか(選定工程の出力に「用法/比喩か字義か/文脈上の意味」が含まれるか、それが意味生成へ渡るか)。
 3. 意味生成Promptへの入力情報は十分か(渡しているのは見出し語だけか、本文文か、段落か、選定時の意味メモか。Prompt本文を引用)。
 4. 文脈の解釈と日本語への変換が一度に行われることが原因ではないか(1 callで「意味の同定」と「日本語化」を同時にさせているか)。
 5. 過去のPrompt改善Trial(Trial_02 G0/G2/G3、Trial_03、Trial_04 C/Cp/M)が効かなかった本質的理由(各armが変えたもの/変えなかったものの対比表)。
 6. 字義訳NGの発生事例に共通する構造・条件(`draw a line`/`an unseen clock`/`question shaped like a trophy`/`take the wheel`/`greener grass` 等: 比喩が本文で新造か慣用か、見出し語が名詞句か動詞句か、本文の文がその比喩を直後に説明しているか、Std/Advの差、モデル差、同一KPのrep間ゆれ)。Trial_02〜04の全NG(△含む)を1表に。
 7. 誤訳を生成させないために変更が有効な工程はどこか(選定/意味生成/入力構造/出力構造/処理順序)。

## 2. 調査対象(読むもの)
- 本番KP生成経路: KP選定・canonicalization(A-1)・意味生成のコードとPrompt(X/Z共通module、`er0XX`のKP関連。`CURRENT_SPEC.md`はKP節のみGrep)。実際にLLMへ渡しているmessagesをDEVでダンプ(API呼出はしない。Prompt組立関数をローカルで呼んで文字列を得る)。
- 既存Trialデータ: `docs/research/FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01/{ROOT_CAUSE_03,DESIGN_04,05,06,TRIAL_RESULT_02,03,04}.md`、`TRIAL_02/GOLD_LABELS_FINAL_01.md`、`TRIAL_03/FABLE_BLIND_RESULT_03.md`、`TRIAL_04/{FABLE_BLIND_RESULT_04,REPORT_FABLE_04,FABLE_JUDGMENT_04,fable_blind_04.md,fable_blind_04_key.json}`、`AUDIT_01/{STD_AUDIT_01,FABLE_VERIFICATION_01,02}.md`、`er112_output/kp_gm_trial_0{2,3,4}/` の生出力(NG事例の入力Prompt・出力・モデル・temperature等の生データ)。
- 重複回避: 既にやったこと(Prompt文言の強化、意味の再整合指示、独立検査C、同一call自己監査Cp)を「試行済み」として明記し、同じ方向の提案を繰り返さない。

## 3. 成果物(`docs/research/FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01/ROOT_CAUSE_04.md` ほか)
 A. `ROOT_CAUSE_04.md`: 上記7点の回答+証拠。字義訳NGの発生機序の仮説を複数立て、既存データで支持/反証できるものは判定(例: 「選定工程は用法を把握しているが意味生成へ渡していない」「意味生成の入力が見出し語+1文のみで、比喩の説明文が範囲外」「出力形式が短い日本語glossを要求するため字義像に引かれる」「意味同定と訳出の同時実行」等)。
 B. `DESIGN_07.md`: 根本対策候補を3案以上、各案について: 変更する工程・入出力構造、追加LLM callの有無(0を優先)、既存call内での実現方法、比喩/慣用/通常表現の扱い、通常表現の非劣化をどう担保するか、X/Y/Z共通性、量産単価・速度への影響、既存Trialとの差(なぜ今回は効くと言えるか)、リスク。**推奨案と理由**。例: (i)選定工程で得た「文脈上の意味(英語1文)」をKPごとに意味生成へ構造化して渡す[call数不変]、(ii)意味生成を「文脈解釈→日本語化」の2段出力に分け同一call内で先に英語paraphraseを書かせてから日本語化[call数不変]、(iii)出力schemaに `is_figurative`/`literal_image_avoid` を追加、(iv)その他Claude自身の案。
 C. `TRIAL_DESIGN_05.md`: 推奨案(+対照)のTrial設計: 既存の代表的失敗例(gold NG)と正常例の固定セット(Trial_04 F層/N層KPを再利用、新規生成を最小化)、Before/After比較、残存NG・新規悪化の測り方(Fable盲検の書式継承)、費用見込み(モデル gpt-6.1-sol/luna の実績単価から)、必要予算。**予算枠の事実**: 課題①の残存個別承認枠はTrial_04 60円枠の残約3.4円+rep2 25円枠の残約4.9円(台帳 `TRIAL_04/BUDGET_LOG_01.md` で再確認し正確な残額を書く)。この残額で実施できる最小Trialと、必要なら追加予算案(金額・根拠)を併記(Fableがユーザーへ提示)。
 D. `OPUS_REVIEW_REQUEST_07.md`: 論点を絞る(原因分析の妥当性、対策案の比較、見落とし、既存Trialとの重複、通常表現の非劣化、call数)。Fableが起動する。
 E. 記録: `docs/pm/ACTIVE_TASK.md` 自分の行(委任_21新設)。SSOTは編集しない。委任文逐語保存 `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-24_FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01_委任_21.md`(先頭MARKER一致、0始まり)。commit(researchフォルダとdelegation_logのみ、`git commit --only -- <paths>`、`git add -A/-u/-f`禁止、secret grep 0件)→`git push origin HEAD:main`。
 F. 報告 `docs/pm/RESULT_PACKET_KPGM21.md`: 7点の回答要約、主因仮説と支持証拠、推奨案、Trial費用と残枠、4行(既存仕様整合/未承認機能の既定値/失敗終了時の最終成果物/撤去)、判定整合行、所要時間。

## §Z ユーザー指示(課題①該当部、逐語)
## 2. 課題① 日本語意味の字義訳｜根本解決
**Status：対策未採用。Trialで検証後、正式採否をユーザー判断に戻す。**
### 2-1. 問題認識
今回のTrialでは、独立検査方式Cによって字義訳NGが6件から1件へ減少した一方、19件の検出中14件が修正不要だった。
これは、検査による品質改善には一定の効果があっても、誤検知・再生成・運用負荷の問題が大きいことを示している。
**検査方式Cを現段階でProduction採用しない。**
ただし、字義訳問題の解決そのものを諦めてはならない。
### 2-2. 原因究明を徹底する
単に「LLMが確率的に字義訳を選ぶ」という説明で終わらせないこと。
以下を具体的に解明する。
1. なぜ本文の文脈から適切な意味を取得できず、字義訳を選択するのか。
2. Key Phrase選定時点で、表現の意味・文脈が失われていないか。
3. 意味生成Promptへの入力情報は十分か。
4. 文脈の解釈と日本語への変換が一度に行われることが原因ではないか。
5. 過去のPrompt改善Trialが効かなかった本質的な理由は何か。
6. 字義訳NGの発生事例に共通する構造・条件は何か。
7. そもそも誤訳を生成させないために、どの工程を変更するのが有効か。
既存Trialデータ、失敗事例、Prompt、生成処理を調査し、原因仮説を証拠とともに整理する。
**Opusによる独立レビューを実施し、原因分析・対策案・見落とし・既存Trialとの重複を確認すること。**
### 2-3. 根本対策の立案
生成後の検査追加ありきではなく、**正しい意味を最初から生成する方法を優先**する。
候補例：
- 本文の文脈から意味を先に解釈し、その解釈を日本語化する。
- Key Phrase選定時に把握した意味・用法を意味生成工程へ確実に引き継ぐ。
- 比喩・慣用表現・通常の字義表現を文脈に応じて扱う。
- 意味生成工程の入力・出力構造や処理順序を見直す。
これらは例示であり、実装方法を限定しない。
Claude自身で有効な代替案を考案し、Opusレビューも活用して比較すること。
追加検査方式も排除しないが、誤検知の多さ、再生成負荷、量産単価への影響を踏まえ、必要性と有効性を説明できる場合に限り候補とする。
既存call内で改善できる方法を優先し、追加LLM callを極力抑える。
### 2-4. Trialと自己ループ
原因究明 → 対策立案 → Trial → 評価 → 改善を自律的に繰り返す。
- 既存の代表的な失敗例と、正常な意味表現を比較対象とする。
- 比喩・慣用表現の改善だけでなく、通常表現の意味が悪化しないことも確認する。
- 成功例だけでなく、残存NG・新規悪化・費用を記録する。
- 効果がない場合は同じPrompt変更を繰り返さず、原因仮説や方式を見直す。
- Opusレビューは初期原因分析に加え、必要な方針転換や最終評価にも活用する。
- 品質を守りながらTrialの検証効率を最大化する。
**「何度か試したがうまくいかなかった」という理由だけで、安易にUSER_DECISION_REQUIREDへ戻さないこと。**
解決の見込みがある限り、承認済み範囲内で自律的に取り組む。
一方、効果のない反復や、品質水準を超える過剰な改善は行わない。
### 2-5. Trial Closeoutと正式採用
今回の課題①について、Production採用は未承認である。
Trial結果を踏まえ、REJECTED / VALIDATED / USER_DECISION_REQUIREDのいずれかに分類する。
VALIDATEDとなってもProduction実装は自動開始しない。
採用可能な改善策が得られた場合、以下を報告し、ユーザーの正式採否判断を受けること。
- 根本原因 / 採用候補の仕組み / Before / After / 残存NG・新規悪化 / X/Y/Z共通仕様への影響 / 量産単価・速度への影響
## 3. 予算・STOP条件
既存の承認済みTrial予算・作業範囲・日次開発費上限を厳守する。課題①は残存する個別承認枠を確認し、その範囲内で原因調査と有効なTrialを優先する。少額費用ごとにユーザー判断を求めない。ただし、承認済み予算・Scopeの超過/未承認の新仕様・品質基準変更が必要/重大な品質・安全リスク/合理的な代替案を検討しても解決見込みがなく根本的な方針変更を要する、ではSTOPし判断を求める。