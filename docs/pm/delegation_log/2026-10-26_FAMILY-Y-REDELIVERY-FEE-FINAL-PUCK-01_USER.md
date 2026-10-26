# 【改訂指示】Family Y『宅配の再配達は有料にすべきか？』完成版制作・公開 (ユーザー指示原文・逐語)

**対象：Family Y『宅配の再配達は有料にすべきか？』Standard／Advanced**

**目標：承認済みの最新Production仕様を反映した完成版を制作し、ユーザー最終試聴へ提出する。**

## 1. 今回反映する2つの正式仕様

### ① Voice 1＝Puck
ユーザー正式承認済み。
- Voice 1はAlgiebaからPuckへ変更。
- Family Yの男性候補No.1はPuck、No.5はIapetus。
- Family ZのVoice候補は変更しない。

Family YのVoice変更がPRODUCTION_WIREDに到達したことを確認し、**本記事のVoice 1音声を正式Production経路でPuckを使って再生成すること。**

### ② AdvancedのComment 2削除
ユーザーによれば、AdvancedのComment 2削除は既にPRODUCTION_WIRED済み。
CURRENT_SPEC・承認記録・正式Productionコード・runtime evidenceを照合し、実際に反映されていることを確認する。
**Advanced完成版ではComment 2を含めない。**
- 音声だけでなく、スクリプト・組立・公開ページからも除外する。
- Comment 2削除によって前後の接続、内容の流れ、再生順序に不整合が生じないことを確認する。
- Standardには、承認されていない構成変更を加えない。
既に配線済みである場合、同じ機能を重複実装しない。

## 2. 制作方針
既存の確定済み記事本文・構成・3人の人物像・Human Review結果を最大限再利用する。
変更対象は原則として以下に限定する。
1. Standard／AdvancedのVoice 1音声をPuckで再生成。
2. AdvancedのComment 2削除が完成版全体に反映されていることを確認。
3. 上記変更に必要な組立・メタデータ・公開ページの更新。
Voice 2／3、その他の正常な音声は原則再利用し、不要な再生成を行わない。
ただし、再利用によって最新の承認済みProduction仕様や品質検査と不整合が生じる場合は、必要な部分のみ再生成・修正すること。

## 3. Production実行・品質検査
Standard／Advancedそれぞれについて、正式Production経路で完成版を組み立てること。
- Voice 1のactual voiceがPuckであることをruntimeで確認。
- 現行の正式TTSモデル・Style・速度・Retry／Fallbackを使用。
- ASR、発音、内容一致、繰り返し、不自然な長ポーズ、速度、音量など、既存の必須品質検査をPASS。
- AdvancedのComment 2が音声・本文・公開ページのいずれにも残存していないこと。
- Comment 2削除に伴う音声順序・つながりを確認。
- Key Phrase・解説・既存Human Reviewの確定内容と最終成果物が一致すること。
- retry／fallback／regeneration／resumeでも旧Voiceや削除済みComment 2が復活しないこと。
Family YのChunk分割については、現在の1段落本文構成を維持する。Chunk発火のために本文を無断変更しない。

## 4. 完成版の公開
Standard／Advancedの両方を試聴できる完成版ページを公開する。
ページには、通し再生、パート別再生、確定スクリプト、Key Phrase・解説等の既存仕様に沿った学習情報を掲載する。
再生リンク・音声参照・スクリプトの整合を確認する。
公開後、ユーザーへ完成版URLを報告すること。

## 5. 作業順序・QCD
Family Y Voice 1＝PuckのProduction Wiringは先行条件とする。
Comment 2削除の既存配線確認、使用可能な音声の棚卸し、組立・公開準備などの独立作業は並列で進めてよい。
品質 ＞ Delivery ＞ 量産単価。
既存の正常な成果物を再利用し、不要なTrial・音声再生成・待機を行わない。
承認済み予算・日次1,000円（JST）を守る。

## 6. 完了条件・報告
Fable独立受入のうえ、以下を簡潔に報告すること。
1. Family Y Voice 1＝PuckのPRODUCTION_WIRED確認
2. Advanced Comment 2削除のPRODUCTION_WIRED確認
3. Standard／Advancedの正式Production生成・組立結果
4. Voice 1のruntime evidence（Puck使用）
5. Advanced Comment 2の完全除外証拠
6. 品質検査・再利用状況・追加費用
7. 完成版の公開試聴URL
8. SSOT／Git反映と残Open Item

**最終Statusは「完成版・ユーザー最終試聴待ち」。**
ユーザーによる試聴承認を先取りして完成確定・Closeoutしないこと。

---
**今回の最終成果物は、Voice 1＝Puck、Advanced＝Comment 2なし、という2つの正式仕様を反映した『宅配の再配達は有料にすべきか？』のStandard／Advanced完成版である。**

(原文ここまで)
