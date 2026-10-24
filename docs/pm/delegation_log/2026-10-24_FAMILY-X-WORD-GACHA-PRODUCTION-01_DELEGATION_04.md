FAMILY-X-WORD-GACHA-PRODUCTION-01 委任_04(Fableから): ユーザーがAdvanced `full_story_part3` の現行音声を承認(UDR #183=(a))。人間承認を正式記録し、Std/Advを正式組立、切替試聴ページを公開、最終公開品質検査まで完了する。追加TTS生成は不要(禁止)。ASR根本対策Trialは別agentが並行(本委任はProductionコードに触れない)。

## 0. 記録(0円)
- ユーザー指示原文(本委任文末尾【ユーザー原文】、逐語)を `docs/pm/delegation_log/2026-10-24_FAMILY-X-WORD-GACHA-PRODUCTION-01_USER_02.md` に保存。
- UDR #183 を「判断済み(2026-10-24): (a)現行音声を承認。OPEN-498案Aの個別登録ではなく包括的な根本対策Trial(別管理ID ASR-OOV-HOMOPHONE-ROOT-CAUSE-01)へ」に更新。

## 1. 人間承認の正式記録 → 組立 → 公開
- Style Profile Gateの正規手順 `record_human_approval`(`er019_family_x_style_profile_01.py`)で `full_story_part3`(b1b)を承認記録(approver=user、reason="USER_APPROVED 2026-10-24 UDR #183 (a): current audio accepted; Local Rewrite you've->you have; ASR primary gotcha, secondary(azure) gacha confirmed"、Fable経由である旨を注記)。Gate迂回・ファイル直接編集は禁止。
- 起動前: `tools/stop_scope_check_01.py --managed-id FAMILY-X-WORD-GACHA-PRODUCTION-01` rc=0、`git status`でX経路import graphに未commit変更なし(別agentのASR Trialコードは`docs/research`またはDEV専用に置く約束。もし共有Validatorの.pyに未commit変更があればFableへ報告して待つ)。
- Adv `--stage assemble`(1起動)→ 試聴ページ `er019_nws2_final_page_01.py`(`user_test/family_x_word_gacha_01/`、Std/Adv切替・通し・パート別・全スクリプト・KP、開発者向け情報なし)→ 公開page_verify `er019_nws2_play_verify_01.py`(Playwright実再生)PASS証跡。
- 最終公開品質検査(音声・スクリプト・KP)の既存Gate結果を `RUNTIME_EVIDENCE_01.md` に追記(Std/Adv通し秒数、KP、PASS_WITH_WARNING一覧、Local Rewrite 1件の音声/表示差の開示、Human Review承認記録のパス)。

## 2. SSOT・Git
- OPEN_ITEMS: OPEN-499をCLOSED(ユーザー承認(a))、本作のUDR待ち項目を更新。`docs/pm/USER_DECISION_REGISTER_01.md` に新規UDR(最終試聴PASS可否: 両レベル試聴URL、A PASS/B指摘、推奨A、耳確認候補=PASS_WITH_WARNING Std 3件+Adv part3)。DECISION_LOG 1エントリ(ユーザー承認・組立・公開・最終実費104.73円+本委任0円)。
- Git: `git status`→`git commit --only`→`git push origin HEAD:main`(wav/mp3/raw_usage_log不追跡、他agent差分を巻き込まない=一時index方式、禁止操作なし、secret grep 0件)。
- 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-24_FAMILY-X-WORD-GACHA-PRODUCTION-01_DELEGATION_04.md`(Nは先頭「FAMILY-X-WORD-GACHA-PRODUCTION-01 委任_04」を含むAgent呼出の0始まり通番、直近470以降)。

## 3. handback(ユーザー原文§6-A): Std/Adv最終試聴URL、正式組立・公開検査結果、Human Review承認記録、最終実費、Production完成状況と残Open Item、UDR番号、commit hash、raw URL。RESULT_PACKET 4行。

【ユーザー原文】
(§1のみ本委任に関係。全文は別管理IDの委任でも保存)
# Claude Codeへの指示
## Family X『英単語ガチャ』完成・ASR同音誤認の根本対策

### 1. ユーザー承認事項

Family X『英単語ガチャ』Advanced最終パートの現行音声を承認する。

- `full_story_part3` の人間承認を正式記録する。
- 追加TTS生成は不要。
- 承認済みのStandard／Advancedを正式組立する。
- 両レベルを切り替えて試聴できる最終ページを公開する。
- 音声・スクリプト・Key Phraseを含め、既存の最終公開品質検査を完了する。

**Standard／Advanced双方の最終版試聴URLを提出すること。**

今回の承認は現行音声の受入であり、新しいASR救済仕様のProduction採用を意味しない。

### 2. `gacha` ASR問題の原因究明

今回、`gacha` が繰り返し `gotcha` と転写され、TTS再試行、Azure追加検査、Human Review、費用超過が発生した。

単なる個別単語の登録ではなく、同種の問題を包括的に解決する。

以下を調査する。

- 実際のTTS音声は正しく発音されていたのか。
- OpenAI Primary ASRはなぜ繰り返し `gotcha` と認識したのか。
- 既存の同音判定・異表記救済・発音辞書・Azure Secondaryがなぜ十分に機能しなかったのか。
- 過去に承認・実装した包括的な同音救済仕様との関係。
- `gacha` 以外の外来語・辞書未登録語でも同じ問題が発生するのか。
- 同音誤認が不必要なTTS再生成やAzure呼出につながる原因。

CURRENT_SPEC、DECISION_LOG、過去Trial、既存Productionコードを照合すること。

### 3. 対策立案

目標は、**正しい発音を誤ってNGにせず、実際の誤発音は確実に検出すること**。

対策は特定の単語だけでなく、辞書未登録語・借用語などにも通用する方式を優先する。

既存の仕組みを可能な限り活用し、判定機構を不必要に複雑化しない。

以下を重視する。

1. 誤NGによる不要なTTS再生成の削減。
2. Azure Secondaryの不要な呼出削減。
3. 誤PASSを増やさないこと。
4. Family X／Z／将来のYへの共通適用。
5. 量産単価70円／記事セットとの整合。

過去に不採用とした方式や、承認済み仕様と矛盾する方式を無断で再導入しない。

### 4. 検証Trial・自律解決

原因調査から対策立案、Trial、評価、必要な修正・再検証まで、Fable管理下で自律的に進める。

- まず保存済み音声・ASR結果を最大限再利用する。
- 独立した調査・検証は並列化する。
- 可能な限りオフラインで検証し、API費用を抑える。
- 正しい発音の救済率と、実際の誤発音の検出維持を両方評価する。
- 過去の正常例・異常例を使ってRegressionを行う。
- 必要な場合は、異なる原因を代表するケースで追加Trialを行う。
- 効果が乏しい方式は反復せず、原因・前提・アプローチを見直す。

既存の承認済み開発予算内で自律的に費用配分すること。品質を犠牲にした原価削減は認めない。

### 5. Production適用の境界

今回承認されたのは記事最終音声であり、ASR対策の新仕様ではない。

したがって、

- 原因調査・Trial・Trial専用コード変更は承認範囲内で進める。
- 新しい同音判定方式や救済仕様をProductionへ無断採用しない。
- Trial成功時はVALIDATEDとして報告する。
- Production採用が必要な場合は、QCD影響と既存仕様との差分を明示してユーザー判断を求める。

既存の承認済み仕様の単なる不具合修正であれば、既存の委任・承認範囲に従って自律的に修正・検証してよい。

### 6. 報告事項

**A. 記事完成報告**

- Standard／Advancedの最終試聴URL
- 両レベルの正式組立・公開検査結果
- Human Review承認記録
- 最終実費
- Production完成状況と残Open Item

**B. ASR根本対策Trial報告**

- 根本原因
- 既存仕様が機能しなかった理由
- 検討した対策と比較結果
- Trialの実測結果
- 誤NG・誤PASS・Azure呼出・TTS再生成・コストへの影響
- Family X／Z／Yへの適用範囲
- Fable独立評価
- Trial Closeout Status
- Production採用に必要なユーザー判断

必要なSSOT・OPEN_ITEMS・Git記録を更新すること。

### 7. 実行上の重要事項

**記事完成とASR改善Trialは並行して進める。**

記事の公開をASR改善Trialの終了まで待たせない。

また、今回は単に `gacha` と `gotcha` を例外登録することが目的ではない。

**類似する外来語・辞書未登録語で同じ不具合を繰り返さず、品質を維持しながら量産費用を下げられる仕組みを目指すこと。**

品質・予算・承認境界を遵守しながら、自律的に原因究明と検証を完了させること。