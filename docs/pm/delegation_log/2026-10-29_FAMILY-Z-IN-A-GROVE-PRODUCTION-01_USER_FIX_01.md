# ユーザー指示原文(逐語、2026-10-29受領。UDR #218の回答=試聴NG、修正①多襄丸配役・②Std KP bandit)
<<<USER>>>
# Claude Codeへの指示｜Family Z『藪の中』Voice配役修正・Key Phrase変更

## 1. 目的・現在のStatus

Family Z『藪の中』Standard／Advancedの完成候補について、ユーザー試聴で以下2点の修正指示がありました。

1. 多襄丸（Tajomaru）のセリフ範囲とVoice配役の整合修正（Standard／Advanced）
2. StandardのKey Phrase変更（constable → bandit）

**現在のStatus：完成候補・ユーザー最終試聴NG（修正待ち）**

今回は既存記事の修正であり、新規制作や記事全体の作り直しは不要です。

承認済みの品質水準を維持し、必要な箇所のみ修正して完成候補を再提出してください。

## 2. 修正①：多襄丸のセリフとVoiceの整合

### ユーザー指摘

Standard本文で、以下の構造になっています。

> "I killed him fairly," Tajomaru said. "The wind lifted her face covering ... She fought with her dagger.
>
> "She held my arm ..."

本来、`Tajomaru said.` はナレーションですが、`The wind lifted her face covering` 以降は多襄丸の直接発言です。

`She fought with her dagger.` の後に閉じ引用符がないため、発言範囲が不明確になっています。

### 修正方針

- `Tajomaru said.`：ナレーターVoice
- `I killed him fairly`：多襄丸Voice（Orus）
- `The wind lifted her face covering` 以降の多襄丸の発言：Orus
- `She fought with her dagger.` の末尾で引用符を適切に閉じる。
- 続く `She held my arm ...` も多襄丸の発言として扱う。

**Standard／Advanced両方で修正してください。**

ただし、引用符の修正だけでVoice配役が正しくなるとは限りません。

本文表記、TTS入力、セグメント分割、実際のVoice割当を照合し、**多襄丸の発言全体がOrusで発声されていること**を確認してください。

すでに正しいVoiceで生成されている音声は再利用し、誤ったVoiceの箇所のみ必要最小限で再生成してください。

### 同種問題の確認

他の6証言者についても、引用符・発言範囲・Voice配役の整合を確認してください。

同様の問題が見つかった場合は、既存の配役仕様に従って原因究明→修正→検証まで実施してください。

記事本文の内容や原作への忠実性は維持し、不要なRewriteは行わないでください。

また、今回の原因が共通のTTS分割・配役処理にある場合は、再発防止を検討してください。既存仕様内の不具合修正は自律的に実施して構いませんが、新しい仕様が必要な場合は採用判断を求めてください。

## 3. 修正②：Standard Key Phrase変更

ユーザー決定：

- Key Phrase：`constable` → **`bandit`**
- `constable`：**追加解説に残す**
- その他の選定内容：変更なし

StandardのHuman Review選定結果、Key Phrase一覧、日本語意味、英語解説、音声、公開ページ表示を整合させてください。

`bandit` の本文出現・選定品質を確認し、承認済みの既存検査を適用してください。

既存の `constable` の解説は追加解説として維持し、重複表示や欠落を防いでください。

AdvancedのKey Phraseは変更しません。

今回の変更について、必要な音声のみ生成し、無関係な音声や本文の再生成は行わないでください。

## 4. 検証・受入条件

以下を確認してください。

1. Standard／Advancedともに、多襄丸の発言がすべてOrusであること。
2. ナレーション部分は承認済みのナレーターVoiceであること。
3. 全7証言について、本文・引用符・TTS入力・Voice割当の整合が取れていること。
4. 修正前後で、証言内容・証言の矛盾・結末・原作への忠実性が維持されていること。
5. StandardのKey Phraseが `bandit` に変更され、`constable` は追加解説に残っていること。
6. 必須のTTS／ASR／品質Gate／Assembly検査がPASSすること。
7. retry／fallback／regeneration／resume経路でも配役が崩れないこと。
8. 公開候補ページで音声再生・表示・レベル切替が正常であること。

修正した音声は、実際のTTS送信Voice・生成音声・組立結果まで追跡し、コード上の設定だけでPASSとしないでください。

必要なRegression testを実施し、既存の正常部分への影響がないことも確認してください。

## 5. QCD・費用・STOP条件

優先順位は **品質 ＞ 完成速度 ＞ 量産単価** です。

- 正常な音声・本文は極力再利用する。
- 必要箇所のみ修正・再生成する。
- 不要な追加Trialやモデル比較は行わない。
- 既存承認・予算範囲内の不具合は自律的に解決する。
- 予算上限超過、新仕様採用、承認済み品質基準変更が必要な場合はSTOPし、判断を求める。

既存の制作費累計86.35円／上限90円を踏まえ、必要費用を確認してください。残予算で実施できない場合は、費用見込みと理由を報告してください。

## 6. 完了報告

修正・検証完了後、以下を報告してください。

- 修正版Standard／Advanced試聴URL
- 多襄丸のVoice問題の原因と修正内容
- 他の証言者への影響調査結果
- Key Phrase変更結果
- 再生成した音声数と追加費用
- TTS／ASR／Gate／公開検証結果
- SSOT／Git反映状況
- Fable独立受入結果
- 未解決事項（あれば）

**完成候補を再提出し、ユーザーの最終試聴判断を待ってください。正式公開はまだ行わないこと。**

今回の修正に必要な範囲で自律的に問題解決を進め、品質を満たした時点で速やかに完成させてください。
<<<END>>>
