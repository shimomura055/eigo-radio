FABLE-DELEGATION-MARKER: FAMILY-Z-STD-DIALOGUE-SPEED-AB-TRIAL-01-委任_02-ADV-20261023

# 委任_02(Advanced追加): Family Z Advanced 会話clipの「機械処理6%高速化」版(B)の制作・QA・WPM計測(Trial、素材制作まで。ページ統合は後続委任)

## T-0
1. 委任文逐語保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-23_FAMILY-Z-STD-DIALOGUE-SPEED-AB-TRIAL-01_委任_02_ADV.md`(N≈322〜332、先頭行MARKER一致確認)。
2. ユーザー追加指示原文(§1)を `docs/pm/delegation_log/2026-10-23_FAMILY-Z-STD-DIALOGUE-SPEED-AB-TRIAL-01_USER_02_ADV.md` に逐語保存。
3. **並行制約(重要)**: 同じTrialのStandard側を別agent(委任_01)が進行中で、`user_test/family_z_std_dialogue_speed_ab_01/`・`docs/research/FAMILY-Z-STD-DIALOGUE-SPEED-AB-TRIAL-01/TRIAL_RESULT_01.md`・SSOT(OPEN_ITEMS/DECISION_LOG/UDR/REPORT_LEDGER)・ACTIVE_TASKを編集する。**本委任ではこれらに一切触れない**。成果物は下記の専用dir・専用docのみ。ページ統合とSSOTは後続委任(Fable)が行う。

## 1. ユーザー追加指示原文(逐語)
```
# Claude Codeへの追加指示:Family Z Advanced会話速度+6% Trial

## 1. 追加Trialの目的

先ほど指示したFamily Z Standardの会話速度比較Trialに、Advancedの比較Trialを追加してください。

ユーザーはStandard/Advancedともに、登場人物の会話が相対的にゆっくり聞こえる点を改善したいと考えています。

対象作品は同じく以下の2作品です。

- 『走れメロス』
- 『開いた窓』

**今回もTrial専用とし、Production仕様・既存完成音声は変更しません。**

## 2. 比較条件

| 項目 | A:現行版 | B:Trial版 |
|---|---|---|
| Standard Narrator | 6%減速 | 変更なし |
| Standard 会話 | 6%減速 | 減速処理を撤去 |
| Advanced Narrator | 速度変更なし | 変更なし |
| Advanced 会話 | 速度変更なし | **機械処理で6%高速化** |
| Voice・Prompt・本文 | 現行版 | 変更なし |

Advancedの会話音声は、既存原音を利用して再生時間を約6%短縮してください。

**音程・声質が不自然に変化しない方式**を採用し、既存の機械処理を可能な限り再利用してください。

## 3. 実施方針

- 先行指示のStandard Trialと統合して効率的に実施する。
- 『走れメロス』のVoice割当は現状を維持。
- TTS再生成は原則行わず、既存音声を利用。
- 会話以外の速度・台詞・音声順序・効果音は変更しない。
- 新しいTTS PromptやStyle Profileは作成しない。
- 追加の速度条件・品質基準を独自に設定しない。

## 4. 試聴ページ

両作品でStandard/Advancedそれぞれの現行A版とTrial B版を比較できるようにしてください。

必要な機能は以下です。

1. 各レベルのA/B通し再生。
2. 同一会話clipのA/B個別再生。
3. NarratorとDialogueの速度比較(実測WPM)。
4. 試聴ページ上で変更箇所・変更内容が分かる表示。

前回指示の試聴ページとまとめ、不要なページや重複作業を増やさないでください。

## 5. 検証と報告

- Standardは会話のみ6%減速撤去。
- Advancedは会話のみ6%高速化。
- Narratorなど非対象音声は変更なし。
- A/Bの再生、音声の欠落・順序・音質を確認。
- 既存Production成果物が不変であることを確認。
- 再生成数・追加API費用・処理費用を報告。
- Fable独立確認を実施。

**Trial終了Status:USER_DECISION_REQUIRED**

ユーザーの試聴判断までProductionへ配線しないでください。

## 6. QCD方針

品質を守りながら最速・低コストで実施してください。

2作品・2レベルを可能な範囲で並列化し、既存音声と検証済みの速度処理を再利用してください。

今回の目的は、**会話がNarratorに対して自然な速度に聞こえるかをユーザーが比較評価すること**です。

数値上の速度改善だけでなく、会話の自然さ・聞き取りやすさを比較できる成果物にしてください。
```

## 2. 前提(Fable)
- 対象A(現行Advanced): 『開いた窓』=`er026_output/family_z_production_e2e_01/the_open_window/run_e2e_01/b1b`、『走れメロス』=**受入済み公開ページ`user_test/family_z_melos_02/`の元run**のb1b(委任_01のStandard側と同じ元runを使う。元runの特定方法: `user_test/family_z_melos_02/index.html`の記載・mp3と各run assembled wavの照合。委任_01がすでに`docs/pm/RESULT_PACKET_FZSPAB.md`やTrial dirに記録していればそれを読んで一致させる。特定できなければ理由を書いてSTOP報告)。
- 既存の速度処理: Standardの6%減速はer063の後処理(time-stretch)で実装されている。**同じ実装(ライブラリ・パラメータ方式)を係数のみ変えて再利用**し(例: 再生時間×1/1.06、ピッチ保持)、新方式を独自に作らない。実装箇所・関数名・使用ライブラリを報告に明記。
- Trial作業dir: `er0XX_output/family_z_std_dialogue_speed_ab_01/<story>/b1b_fast/`(委任_01が使っているTrial root名を確認して同じrootのサブdirにする。rootが未作成なら `er026_output/family_z_std_dialogue_speed_ab_01/` を使用)。**Production run dir・公開ページ・Master Audio Storeには書き込まない**。

## 3. 作業(2作品を可能な範囲で並列)
1. A版素材: b1bのassembled wav・timeline・clip wav・plan/speaker_tableをTrial dirへコピー(元は無変更、コピー後にsha一致確認)。
2. B版: dialogue kindのclipだけを既存time-stretch実装で約6%短縮(ピッチ保持)。Narrator・Preview/Comment(Charon)・KP・効果音等は同一ファイル(sha一致)。既存のassemble経路でTrial dir内に通し音声を再構築(無音間隔・順序はAと同一)。
3. QA: (i)会話clipの長さ比 B/A≈0.943(±0.01)を全clipで確認、(ii)非対象clipのsha一致数、(iii)順序・台詞・Voice同一性の照合表、(iv)B版会話clipに対して既存のASR検査(Production既定のFamily Z英語判定器、ローカルWhisper/保存転写が使えるならAPI 0で。実API呼出が必要ならAzure/OpenAI費用見込みを出し、**合計5円以内なら実行、超えるなら実行せず見込みのみ報告**)でPASS維持を確認、(v)音質: クリッピング・無音欠落のチェック(ピーク・RMS・長さ)。
4. WPM: 作品ごと・clipごとに Narrator / Dialogue(A) / Dialogue(B) の語/分を算出(8語以上と全clip加重の両方)、A→Bの差。
5. 素材のmp3化(lameenc 128kbps)は、通し音声A/B・会話clip A/B対をTrial dir内 `mp3/` に出力し、ページ統合用のJSONマニフェスト(`manifest_adv.json`: story、level、clip id、話者、Voice、テキスト、A/B path、A/B秒、WPM、処理係数、sha)を作る。**user_test配下には置かない**。
6. 証跡: `docs/research/FAMILY-Z-STD-DIALOGUE-SPEED-AB-TRIAL-01/TRIAL_RESULT_ADV_01.md`(条件表、元run特定、処理方式・実装再利用箇所、QA結果、WPM表、同一性証拠、Production無変更の証拠[`git status`で対象run・公開ページに差分0、コピー元sha]、費用[処理はローカル0円、API呼出があれば出典])。
7. commit: 自分の成果物のみ明示add(TRIAL_RESULT_ADV_01.md、delegation_log 2件。wav/mp3はgitignore対象なら含めない)、secret_scan `--staged` hits=0、`git push origin HEAD:main`。

## 4. 禁止
- Production仕様・コード・既存成果物・公開ページ・Storeの変更、Standard側の成果物・ページ・SSOT・ACTIVE_TASKの編集、Advancedの再生成(原則。欠落clipがある場合は再生成せず報告)、新Prompt/Style、独自の速度条件・品質基準の追加、メロスVoice割当の変更。

## 5. 報告(docs/pm/RESULT_PACKET_FZSPAB_ADV.md、同内容を最終報告で)
(1)元run特定結果 (2)処理方式(再利用した実装・係数) (3)QA結果(長さ比・sha一致・ASR・音質) (4)WPM表(作品×Narrator/Dialogue A/B) (5)Production無変更の証拠 (6)費用 (7)マニフェスト・素材のpath、commit・raw URL (8)ページ統合時の注意 + RESULT_PACKET 4行 + 「判定整合: 重大NG=あり/なし」。