# ユーザー指示原文_03(2026-10-28、管理ID: LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01)

# Claude Codeへの指示｜LR後の本文・音声不一致是正と正式公開

## 1. ユーザー決定

以下3記事について、**LR後の音声と表示本文の不一致を解消するため、修正版への差替え・正式公開を承認します。**

1. Family X『英単語ガチャ』Advanced
2. Family Z『猿の手』Standard
3. Family X『AI島』Standard／Advanced

**AI島については、修正反映後にユーザー最終確認用の完成版を提出してください。**

Status：APPROVED_FOR_PRODUCTION  
目標：PRODUCTION_WIRED（各記事の正式公開反映まで）

## 2. 修正対象

| 記事 | 修正前 | 修正後 |
|---|---|---|
| 英単語ガチャ Adv | If you've felt | If you have felt |
| 猿の手 Std | After their guest left | After their visitor left |
| AI島 Std | The AIs sent | The AI agents sent |
| AI島 Adv | The AIs sent | The AI systems sent |

今回の目的は、**表示本文・TTS入力・ASR正解原稿の三者一致を回復すること**です。

既存のLR後音声は再利用し、原則としてTTSを再生成しないでください。

確定済みKey Phrase／Key Word／文法・その他の学習内容、Voice、速度など、今回の不一致是正に関係しない仕様は変更しません。

## 3. 実施内容

### ① 英単語ガチャ・猿の手

- 検証済み候補ページの修正内容を正式公開版に反映する。
- LR後の表示本文と実音声の一致を確認する。
- 旧「Local Rewrite採用」注記など、不要になった表示を整理する。
- 正式公開URLで反映と再生を確認する。

### ② AI島

- Standard／AdvancedともLR後の英文を正式本文へ反映する。
- 既存の修正音声との一致を確認する。
- 確定済み学習項目、音声、表示内容の整合を確認する。
- 正式公開に必要な既存のHuman Review承認条件・公開Gateを満たす。
- **修正後の完成版をユーザー最終確認用として提出する。**

既存のHuman Reviewに未承認項目が残っている場合は、無断で承認扱いにせず、判断が必要な内容を明示してください。

## 4. 品質・受入条件

以下を確認してください。

1. 表示本文・TTS入力・ASR正解原稿の三者一致。
2. 公開音声が検証済みのLR後音声と一致。
3. 確定済みKP／KW／文法／Factへの意図しない変更なし。
4. LR・Fallbackの赤／濃青注記とChunk境界表示が承認仕様どおり。
5. 公開ページに開発用注記等の不要な混入なし。
6. Standard／Advancedそれぞれの対象範囲を確認。
7. 正式公開経路、必要なRegression、runtime evidenceを確認。
8. CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS／Gitを整合。

不具合が見つかった場合は、既存承認範囲・予算・STOP条件内で原因究明→修正→再検証を自律的に実施してください。

不要な追加Trialや品質基準の変更は行わないこと。

## 5. QCD・進め方

品質を守りながら、完了までの時間を最小化してください。

- 3記事の独立作業は可能な限り並列化する。
- 検証済み候補と既存音声を最大限再利用する。
- 不必要なTTS／ASR再実行を避ける。
- 既存の正式採用済み共通仕様との整合を維持する。
- 正式公開・Production Wiringの完了を証拠に基づいて判定する。

## 6. 最終報告

作業完了後、以下を簡潔に報告してください。

1. **3記事それぞれの正式公開URLと反映結果**
2. 本文・音声・ASRの一致検証結果
3. 音声・学習項目の変更有無
4. Family／Level別Production Wiring Status
5. 残Open Item・ユーザー判断事項
6. QCD実績

**AI島については、Standard／Advancedの完成版試聴URLを必ず提示し、ユーザーが最終試聴・承認判断できる状態にしてください。**

AI島の完成版提出は、ユーザーの最終試聴承認を意味しません。正式公開への反映状況とユーザー最終承認待ちの状態は区別して報告してください。

中間報告は不要です。必要な作業を完了させ、最終結果をまとめて報告してください。
