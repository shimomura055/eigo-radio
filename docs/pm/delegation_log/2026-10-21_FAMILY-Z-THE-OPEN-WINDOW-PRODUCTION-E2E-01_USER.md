# ユーザー指示原文(2026-10-21)
管理ID: FAMILY-Z-THE-OPEN-WINDOW-PRODUCTION-E2E-01

# Family Z 古典文学第2作「開いた窓」Production制作指示

**管理ID：FAMILY-Z-THE-OPEN-WINDOW-PRODUCTION-E2E-01**

## 1. ユーザー正式決定

Family Zの古典文学第2作として、サキ（Saki／H. H. Munro）の **『開いた窓（The Open Window）』** を採用する。

既存のFamily Z正式Production仕様を使用し、Standard／Advancedの両レベルについて、原稿生成からTTS・Audio QA・音声組立・試聴ページ公開まで一括実施する。

**目的：原作の面白さを維持した、完成度の高い英語学習ラジオを、品質を守りながら最短・最小原価で完成させる。**

## 2. 原作・Story品質

制作前に以下を確認する。

- 原作本文を直接取得・確認する。検索結果の要約だけをSeedにしない。
- 日本国内での利用権利を確認し、既存のFamily Z権利GateをPASSする。
- 現代の第三者翻訳・翻案等を権利未確認のまま流用しない。
- `story_type=literature` とする。
- 既存のFamily Z Story品質基準を適用する。

本作で特に守るべき魅力は以下。

1. 少女が語る不気味な出来事と、その話を信じる訪問客の心理。
2. 開いた窓を中心とする伏線。
3. 人影が現れる場面の緊張感。
4. 最後の種明かしと、少女の巧みな嘘によるユーモア。

**結末の意外性を損なう先回りの説明や、過剰な解説を入れないこと。**

原作の中心Story、人物関係、因果関係、結末を維持する。短編化に必要な圧縮は許容するが、不要な創作や設定変更は行わない。

## 3. 原稿仕様

**Full Story本文の目標：400語／レベル**

- Standard：400語目安
- Advanced：400語目安
- 許容範囲：330〜470語
- 範囲外は既存仕様どおりWARNのみ。語数を理由とする不要な再生成は禁止。
- Preview／Comment／Key Phrases等は本文語数に含めない。

既存Productionの文章生成方式を使用する。

- Advanced：承認済みSolによるR0→R1→R2。
- Standard：Advanced最終稿を基に難易度調整。
- 原作の魅力、自然な英語、ストーリーとしての一貫性を重視する。
- StandardとAdvancedで、中心Storyや結末が変わらないようにする。

B3Zなど過去に不採用となった方式を復活させない。

## 4. 音声・品質仕様

**前作「走れメロス」で正式採用・配線済みのFamily Z Production仕様を継承する。**

特に以下を維持する。

- 承認済みNarrator／DialogueのVoice・Style。
- Standard英語音声の既存6%減速。Dialogueにも承認済みの生成後減速方式を適用。
- Preview／Comment／Key Phrasesの現行承認済み仕様。
- Pronunciation LedgerとAzure Phrase List（重み2.0）。
- Primary／Secondary ASRと承認済み発音同値判定。
- TTS retry → Local Rewrite → 再検証 → 必要時のみHuman Reviewの既存フロー。
- Rewrite後は必ず最新原稿を正本としてASR照合する。
- retry／fallback／regeneration／resumeでも原稿・音声の整合を維持する。

新作品に登場する固有名詞については、既存のPronunciation Ledger／読み解決機構を使用する。

**今回の制作を理由に、新しい音声品質基準や未承認の発音判定ルールを追加しないこと。**

## 5. 実行・QCD

正式Production初回経路でE2Eを実行する。

品質 ＞ 完成速度 ＞ 量産単価 ≫ 開発費用。

- 原作・権利確認と独立したProduction準備は並列化する。
- 原作・権利Gateを通過する前に有料の本文生成・TTSへ進まない。
- 既存実装・検証済み成果を再利用し、重複開発・不要なTrial・追加検索を避ける。
- 原稿生成から音声完成まで、不合理な日付分割や待機を設けない。
- 既存の品質Gate・安全条件・STOP条件をすべて維持する。
- 量産原価70円／記事セットを目標とし、実費と原価増加要因を記録する。
- 日次開発予算1,000円（JST）を遵守する。今回の個別費用上限は、既存規定・承認枠を確認し、未承認の上限を推定して適用しない。

承認済み仕様内の軽微な不具合は、原因究明から修正・再検証まで自律的に処理する。

新仕様採用、権利Gate不合格、重大品質問題、予算超過、明示STOPの場合のみ必要なユーザー判断を求める。

## 6. 完成条件

以下をすべて満たすこと。

1. 原作Seed・日本国内権利Gateの確認完了。
2. Standard／Advancedの本文・補助コンテンツ完成。
3. 原作の伏線・心理・結末・ユーモアが適切に維持されている。
4. 全必須Audio QA／Validator／Assembly Gate PASS。
5. Standardの6%減速が実際の完成音声に反映されている。
6. 正式Production runtime evidence取得。
7. Standard／Advancedの試聴ページ公開。
8. SSOT／Git反映とFable独立受入確認。

試聴ページには、完成音声の通し再生、Section別の全文原稿、Key Phrasesを掲載する。

**Production完成とユーザー試聴PASSは区別する。** 完成後は `USER_LISTENING_PENDING` とし、ユーザーの最終試聴を待つ。

## 7. 最終報告

ユーザー判断への重要度順に、以下を簡潔に報告する。

1. **完成可否とStandard／Advancedの試聴URL**
2. 原作・権利Gate結果
3. Story品質と語数、原作からの主要な編集内容
4. 音声QA・6%減速・Human Review結果
5. 実費、量産単価、所要時間
6. Production runtime evidence・Fable受入判定
7. SSOT／Git反映状況
8. 未解決事項・必要なユーザー判断（ある場合のみ）

---

**本件は既存のFamily Z仕様による新規作品制作であり、新たな仕様開発Trialではない。**

前作メロスで完成・承認されたProduction経路を最大限再利用し、『開いた窓』の意外な結末とブラックユーモアを損なわず、必要十分な品質で速やかに完成させること。