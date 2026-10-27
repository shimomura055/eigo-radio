# ユーザー指示原文(2026-10-27、管理ID: LR-FALLBACK-M3-CROSS-FAMILY-AUDIT-01)

# Claude Code指示｜Local Rewrite・Fallback・M3 Gateの全Family横断調査と是正

## 1. 目的・対象・Status

Family X/Y/ZのLocal Rewrite（LR）、TTS Fallback、Human Review、M3 Gateを横断的に調査し、承認済み仕様との不整合や、本文と音声の不一致を解消する。

特に、Family X「AIの仮想の島」で発生した問題を起点として、同種問題が他のFamily・音声Roleでも起きない状態を目指す。

**対象**
- Family X/Y/Z × Standard/Advancedの本文音声（全6経路）
- 本文以外でLRが適用される音声Role
- 正式初回Production経路、retry、fallback、regeneration、resume、再利用、公開ページ
- ASR、確定内容保護、M3およびその他の関連Gate

**Status**
- 調査・承認済み仕様内の不具合修正：実施可
- 新しい仕様・Gate緩和：USER_DECISION_REQUIRED
- 新仕様候補のTrial：個別承認が必要
- 新仕様のProduction採用：未承認

現時点で、LR後の自動採用条件変更、M3緩和、記事本文の自動書換え方式の新設は承認されていない。

## 2. 今回のAI島で確認された事象

対象はStandard／Advancedとも英語本文 `full_story_part1_k2`。

| 項目 | Standard | Advanced |
|---|---|---|
| 元原稿 | The AIs sent to the island had no set tasks or rewards. | The AIs sent to the island had no specific tasks or rewards. |
| 初回〜3回目 | 検査NG | 検査NG |
| Fallback | 3回目にMinimal instruction使用、NG | 3回目にMinimal instruction使用、NG |
| LR後TTS入力 | The AI agents sent to the island had no set tasks or rewards. | The AI systems sent to the island had no specific tasks or rewards. |
| LR後ASR | PASS | PASS |
| 最終停止 | M3のLR履歴検出によるHuman Review要求 | 同左 |

記事本文は元の `AIs` のままであり、TTS入力・音声だけが変更されている。

**重要：今回のHuman Reviewの直接原因はFallbackではなく、M3によるLR使用履歴の検出。**

ただし、上表はこれまでの調査報告に基づく。今回の調査では保存済みruntime evidenceと照合し、最新の正式仕様と区別して確定させること。

## 3. 最優先調査：なぜLR後に本文が更新されないのか

次を既存仕様、設計書、コード、実際の保存データ、ユーザー承認履歴から調査する。

1. LRが記事本文ではなくTTS送信用の英文だけを変更する設計になっているか。
2. その設計はユーザーが正式承認したものか、それとも実装・配線上の欠落か。
3. LR後の英文が、どのデータ項目に保存され、どの後続工程へ伝搬するか。
4. 記事本文、公開スクリプト、表示ハイライト、Key Phraseの出現箇所、文法解説、TTS、ASRの正解原稿が、それぞれ何を参照するか。
5. LR後に本文を更新しようとした場合、既存の本文ハッシュ、ユーザー確定済みKP/KW、文法、Fact、QA、翻訳、選定ロックにどのような影響があるか。

**品質原則：英語学習教材では、ユーザーが読む英文と実際に聞く英文の一致が必要。**

ただし、この原則を満たすための具体的な変更方式は今回まだ承認していない。

既存承認仕様で修正可能な不具合なら自律的に是正する。新しい記事本文更新方式・確定内容の変更・品質基準変更が必要なら、推奨案と影響を整理してUSER_DECISION_REQUIREDとする。

AI島の原稿やユーザー確定内容を、独断で変更しない。

## 4. X/Y/Z全6経路のLR・Fallback実装確認

2026-10-27の最新「TTS Retry/Fallback/Local Rewrite 統一仕様」を現行正本として確認する。

旧「標準2回＋Minimal Fallback1回」などの歴史的記述を、最新仕様と混同しないこと。

全6経路について次を確認する。

- LRの適用対象と発火条件
- 通常TTSとFallbackの試行回数・実行順序
- Minimal instructionの使用条件
- Fallback時に使用する実際のPrompt／Style
- LR後のTTS試行回数・Style・ASR検査
- Standardの減速後ASR再検証
- LR成功後の状態遷移
- Human Reviewへ移行する条件
- M3または他のGateによる採用制限
- retry／fallback／regeneration／resumeでの整合

コード上の配線、単体・結合テスト、実際のruntime発火を区別すること。

未観測の場合は、実証済みと報告しない。

## 5. M3・Local Rewrite・Human Reviewの整合調査

Repoには、LR後のASRがPASSすれば `RESOLVED_BY_LOCAL_REWRITE` としてHuman Review Lockに進まない仕様がある。

一方、Family XのM3は、LR使用履歴を検出すると人間承認を要求している。

この2つについて、以下を明確にする。

1. それぞれの設計目的とユーザー承認履歴
2. 適用Family・Level・Role
3. M3が禁止する対象は、LRそのものか、承認済みStyleからの逸脱か
4. fallback音声とLR回復音声がどのように区別されているか
5. LR後も承認済みStyleが維持されているか
6. ASR PASS後にHuman Reviewを要求する正当な理由があるか
7. 人間承認の重複や不要な制作停止が生じていないか

**既存のM3やHuman Reviewの条件を独断で撤去・緩和しないこと。**

ただし、既存の承認済み仕様同士に矛盾がある場合は、それを隠さず整理し、品質・速度・量産単価への影響を踏まえた推奨案を提示する。

## 6. 本文以外のLR適用範囲を横断調査

Family X/Y/Zの全音声Roleを調べ、LRの適用有無を一覧化する。

本文以外にもLRが存在する場合は、次を確認する。

- 音声に読ませる原稿とユーザー向け表示テキストの一致
- LR後の書換え結果の伝搬先
- ASR判定の正解原稿
- 確定済み学習項目との整合
- 後続の公開ページ・字幕・スクリプト・音声との一致
- Human Reviewへの移行条件
- 既存の再利用・再開時に旧原稿が復活しないか

音声のないRoleやLR非対象のRoleは、その理由と正式仕様を記録する。

今回のAI島だけを個別修正して終了せず、**同じ原因による問題が他のProduction経路で再発しないか**を確認する。

## 7. 原因究明後の対応方針

原因を次の3種類に分類する。

**A. 承認済み仕様からの実装逸脱**

既存の委任・承認・予算範囲内で、修正→テスト→必要なruntime検証まで自律的に進める。

**B. 承認済み仕様同士の矛盾**

矛盾する決定と実装経路を示し、整合案を提示する。新しい採用判断が必要ならUSER_DECISION_REQUIREDで停止する。

**C. 仕様どおり動作しているが、品質上の問題が残る**

品質問題、影響範囲、代替案、推奨案、QCDへの影響を報告する。未承認の仕様変更は行わない。

新仕様のProduction Wiringや新規Trialへ無断移行しない。

## 8. 検証・受入条件

実装修正を行った場合は、関連するX/Y/Z全経路を対象として次を確認する。

- 記事本文と音声用原稿の一致
- LR後のASR正解原稿と公開表示の整合
- 確定済みKP/KW・文法・日本語訳の保護
- 元のFact・意味・文脈の維持
- 承認済みStyleの維持または適切な例外処理
- Human Review Gateの正しい適用
- retry／fallback／regeneration／resume
- 必須Regression／Validator／Integration Test
- 正式Production経路でのruntime evidence
- Fable独立受入
- CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS／Git更新
- Dangling Reference・旧仕様残存の確認

Production Wiringを実施した対象は、全要件を満たした経路だけPRODUCTION_WIREDと判定する。

## 9. QCD・進行方法

優先順位：**品質 ＞ Delivery ＞ 量産単価 ≫ 開発費用**

- 既存ログ・保存データを再利用し、調査は原則API費用0。
- 独立したFamily・Roleの調査を並列化する。
- 関係のない本文や音声を再生成しない。
- 同一方向の無益なTrialを反復しない。
- 既存仕様内の不具合は自律的に解決する。
- 日次開発費1,000円（JST）と個別承認枠を遵守する。
- 追加Trial、新仕様採用、重要なGate変更はユーザー承認を必須とする。
- 品質Gateを無断で緩和しない。
- 必要十分な品質に到達したら不要な磨き込みを行わない。

他の独立した承認済み作業を、不合理に停止させないこと。

## 10. 報告事項

技術調査の実施順ではなく、PM判断への重要度順に報告すること。

1. **AI島の本文と音声が不一致になった真因**
2. **本文反映が既存仕様上どう扱われるべきだったか**
3. **M3とLRの関係、Human Reviewの必要性**
4. X/Y/Z × Standard/AdvancedのLR・Fallback適用状況
5. 本文以外のLR適用箇所と同種不具合の有無
6. 承認済み仕様内で修正した内容と検証結果
7. 未解決の仕様矛盾・新しいユーザー判断事項
8. QCD影響（品質、完了までの時間、量産単価、開発実費）
9. Fable受入・SSOT／Git・Open Item

**最重要：今回は単なるAI島の音声承認案件ではありません。Local Rewriteで本文と音声が食い違う原因、M3による不要なHuman Reviewの可能性、全Familyへの波及を確認し、必要な是正につなげる案件です。**

ユーザーに技術的な小判断を繰り返し求めず、既存の承認範囲で解決できる事項は自律的に完了してください。
