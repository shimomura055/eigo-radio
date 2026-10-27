# ユーザー指示原文(2026-10-28、管理ID: LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01)

# Claude Code指示｜Local Rewrite・Fallback横断仕様の正式採用・Production Wiring

## 1. 目的・正式採用Status

ユーザーが決定したLocal Rewrite（LR）・Fallback・M3 Gate・最終Human報告の共通仕様を、正式Production経路へ反映し、PRODUCTION_WIREDまで完了させてください。

**Status：APPROVED_FOR_PRODUCTION**

到達目標：PRODUCTION_WIRED

対象：
- Family X/Y/Z：Standard／Advanced、全音声Role
- Family A/B/C等の既存Family：適用可能な最終Human報告仕様
- retry／fallback／LR／regeneration／resume／組立／公開／最終Human報告
- 既存公開記事のLRによる本文・音声不一致

既存Familyの音声生成方式を、今回の決定を理由に無断でX/Y/Z方式へ置換しないこと。

本指示は、2026-10-27のLR横断監査（OPEN-565）および修正4件を前提とする。

## 2. 最重要原則：表示は最終Human報告用資料のみ

**今回の赤色・濃い青色の表示、注記、変更履歴の説明は、TTS・ASR・音声組立が完了した後のユーザー最終確認資料にのみ適用する。**

以下には絶対に混入させないこと。

- 制作スクリプトの文章
- TTSへ送信する読み上げ原稿
- ASRの正解原稿
- 学習者向けの通常公開ページ本文
- Key Phrase・Key Word・文法の学習用表示
- TTS用Style Prompt

最終確認資料の注記は、音声として読み上げない。

ただし、LRによる実際の英文変更そのものは別扱い。最終的な表示本文・TTS入力・ASR正解原稿を一致させ、必要な後続成果物へ正しく伝搬させること。

**装飾用注記と、実際に採用された英文を混同しない。**

## 3. UD-1：LR後の本文・音声一致

正式採用：

- LRによって変更された英文を、最終的な表示本文にも反映する。
- TTS用英文だけが変更され、公開本文が旧原稿のままになることを認めない。
- LR前後の英文、変更箇所、変更理由、対象音声区間を記録する。
- 最終表示本文・TTS入力・ASR正解原稿が一致することを検証する。
- 確定済みKey Phrase／Key Word／文法・日本語訳・Fact・原作保持要件を保護する。
- 確定内容に干渉する場合は、無断で変更せず適切なSTOP／USER_DECISION_REQUIREDとする。

LRの正常発動そのものではHuman Reviewに移行しない。

ただし、品質NGや重大な内容不整合については従来の品質Gateを維持する。

## 4. UD-2：AI島の本文・音声不一致の是正

Family X「AIの仮想の島」について、以下を正式採用する。

Standard：
- 変更前：AIs
- 変更後：AI agents

Advanced：
- 変更前：AIs
- 変更後：AI systems

既存のLR後音声を使用し、不要な再TTSは行わない。

変更対象は、今回のLRが適用された該当英文箇所だけとする。

本文、学習項目、解説、ASR正解原稿、組立、公開表示の整合を確認し、最終Human報告では変更前後を赤色で明示する。

## 5. UD-3：M3／関連Style Gateの扱い

ユーザー正式決定：

1. **承認済みStyleとの照合は維持。**
2. **Fallback検出・記録は維持するが、正常なFallback発動のみを理由とする組立停止・Human Review要求は解除。**
3. **LR検出・記録は維持するが、正常なLR発動のみを理由とする組立停止・Human Review要求は解除。**

Family XのM3だけでなく、Family YのStyle Gate、Family Zや他Familyの相当する品質確認経路も対象に整合を確認する。

ただし以下は従来どおり停止対象とする。

- 未承認・不明なStyleへの切替
- 許可されていないFallback方式
- Style記録・証拠の欠落、不一致
- ASR NGやその他の音声品質NG
- LRによる意味・Fact・確定内容・原作保持条件の違反
- 本文と音声の不一致
- 技術的STOP、安全上のSTOP

**正常なLR／Fallbackという既知の例外を、品質異常として扱わない。**

今回の正式承認は、ASRやStyleの品質検査そのものを弱める許可ではない。

## 6. 最終Human報告用資料の表示仕様

全Family・全レベル・全音声Roleに適用。

### A. Local Rewrite

最終Human確認用の英文表示で、変更箇所を**赤色**にする。

必須表示情報：
- Local Rewriteが発動したこと
- 対象音声区間
- 変更前の英文
- 変更後の英文
- 変更された語句・表現

対象テキストのうち、LRによる実際の変更箇所を赤色表示する。

### B. Fallback

最終Human確認用の対象テキスト全体を**濃い青色**で表示する。

必須表示情報：
- Fallbackが発動したこと
- 最終採用音声に適用されたStyle名
- 通常Styleから何に切り替わったか
- 適用された音声区間・Chunk・本文範囲

注記も濃い青色とし、対象テキストと同じ色で表示する。

対象には次を含める。

- 英語短文Style（Minimal）
- 日本語短文Style（Minimal）
- ENGLISH_LOCK
- Family ZのDialogue Style切替
- その他、承認済みFallbackで実際にStyleが変更された採用音声

Styleが変わらない再試行は、Style変更があったかのように表示しない。

### C. LRとFallbackが重複した場合

- LRによる英文変更と、FallbackによるStyle変更を両方表示する。
- 赤色と濃い青色の意味が混同されないようにする。
- 対象区間全体と変更語句の両方を識別できるようにする。
- LR・Fallbackの実行履歴と、最終採用音声の状態を区別する。

**採用されなかった試行のFallbackを、最終採用音声のStyleとして誤表示しないこと。**

なお、開始時刻・終了時刻などの技術情報の表示は不要。

## 7. 正式TTS仕様の維持

CURRENT_SPECおよび49経路対応表の最新仕様を正とする。

代表的な仕様：

- X/Y/ZのLR対象英語音声：元原稿で最大3回＋LR後最大3回、総最大6回
- 通常の3回構成：Role Style2回→180秒待機→Fallback1回
- LR後も同じ3回構成、LR再入禁止
- 日本語音声：最大3回、日本語短文Style Fallback、LRなし
- Key Phrase英語：通常2回＋ENGLISH_LOCK2回、最大4回、LRなし
- Advanced Key Phrase英語解説：最大3回、英語短文Style Fallback、LRなし
- Family Z Dialogue：最大3回。文脈・感情方式では3回目に従来Dialogue Styleへ切替、LRなし
- 固定Shell英語：既存方式維持
- 固定MP3：TTS生成なし

今回の変更で以下を変えない。

- TTS試行回数
- 待機時間
- Fallback Style
- LR適用範囲
- ASR判定基準
- Voice／速度
- 既存の確定内容保護ルール

全49経路の対象表と実際のProduction配線を照合し、旧仕様へのDangling Referenceを残さない。

## 8. 既公開記事への対応

LR横断監査で本文・音声不一致が確認された以下を対象とする。

- Family X「英単語ガチャ」Advanced
- Family Z「走れメロス」Advanced
- Family Z「猿の手」Standard
- Family X「AIの仮想の島」Standard／Advanced

変更前後の本文、実音声、ASR基準、学習項目、ユーザー承認記録を照合する。

LRに関係する不一致箇所のみを必要十分に修正し、不要な本文・音声の再生成や既公開記事の一律作り直しは行わない。

既存の確定内容やユーザー承認と衝突する場合は、影響を具体的に示して適切なSTOPとする。

公開差替えについては記事単位の承認・既存運用を遵守し、無関係の過去記事へ無断遡及しない。

## 9. Family Z「告げ口心臓」との整合

「告げ口心臓」は、別途承認済みの本文固定・学習項目再選定・音声再制作案件として進行する。

- Standard／Advancedの①②③選定内容・照合コードを維持する。
- 文法は両レベルとも0件で正式確定。
- 既存スクリプトを変更しない。
- 本文音声・Key Phrase音声・解説・組立・公開を進める。
- 今回の新仕様が正式配線された経路では、その仕様を使用する。
- LRにより本文変更が必要になった場合は、今回の共通仕様との整合を確認する。

「告げ口心臓」の完成作業を、独立して実施可能なLR横断作業のために不必要に停止させないこと。

## 10. 検証・受入条件

Production Wiringでは、少なくとも以下を確認する。

1. 正式初回Production経路へ反映されている。
2. retry／fallback／regeneration／resumeで同じ仕様が適用される。
3. LR後の本文・TTS入力・ASR正解原稿の整合が保たれる。
4. 既存のKP／KW／文法／Fact等の確定内容が保護される。
5. 正常なLR／FallbackだけではHuman Reviewに入らない。
6. 異常なStyleや品質NGは、従来どおり停止する。
7. すべての対象Roleの発動記録が最終Human報告へ伝搬する。
8. 最終Human報告資料の赤・濃い青表示、注記、区間対応が正しい。
9. 注記が制作本文・TTS・ASR・学習者向け公開表示に混入しない。
10. 必須Regression／Validator／Integration TestがPASSする。
11. 正式runtime evidenceで発火と挙動を確認する。
12. Fable独立受入、CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS／Gitへの反映を完了する。

各Family・Levelで証拠を区別すること。

コード配線のみ、DEV動作のみ、単体テストのみではPRODUCTION_WIREDと判定しない。

## 11. QCD・進行方法

優先順位：

**品質 ＞ Delivery ＞ 量産単価 ≫ 開発費用**

- 承認済み品質を守りながら、完了までの時間を最小化する。
- 独立作業は原則並列化する。
- 既存成果物・保存済み音声・実行記録を最大限再利用する。
- 調査・表示・Gate修正は原則API費用0で進める。
- 有料runtime検証は既存予算枠内で最小限に実施する。
- 日次開発費1,000円（JST）と個別承認枠を管理する。
- 技術的な不具合は承認範囲内で自律的に修正・検証する。
- 品質基準の引上げ・引下げ、未承認の追加Trial、新仕様採用、予算超過は行わない。
- 同一方向の無益なTrialを反復しない。
- 必要十分な品質に到達したら速やかに完了する。

## 12. 最終報告

以下の順で報告してください。

1. **Family別・Level別のPRODUCTION_WIRED判定と根拠**
2. LR後の本文・音声一致の是正結果
3. M3および他Style Gateの変更結果
4. 最終Human報告用資料の完成画面URL・表示例
5. 既公開記事4件の整合・差替え状況
6. 「告げ口心臓」への適用状況
7. TTS／ASR／Style／retry／resumeのRegressionとruntime evidence
8. QCD実績・追加制作単価への影響
9. Fable受入・SSOT／Git反映
10. 残Open Item／USER_DECISION_REQUIRED

**重要：今回の正式仕様は、LR・Fallbackを隠すことでも、品質Gateを弱めることでもありません。品質を維持しながら不要なHuman Review停止を解消し、最終確認資料で変更内容を人間が確実に把握できる状態にすることです。**

全Family・全レベルの対象経路でPRODUCTION_WIREDまで完了させてください。
