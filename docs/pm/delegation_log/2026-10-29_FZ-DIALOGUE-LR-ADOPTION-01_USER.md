# ユーザー指示原文(逐語、2026-10-29受領。ZセリフLR正式採用=APPROVED_FOR_PRODUCTION、最大TTS6回統一、藪の中c6をLR段階から再開)

# Claude Codeへの指示｜Family ZセリフLR正式導入・最大TTS6回統一・『藪の中』制作再開

## 1. 目的・正式採用Status

ユーザーは、Family Zのセリフ音声について、従来対象外だったLR（Local Rewrite）を正式採用しました。

**Status：APPROVED_FOR_PRODUCTION**

対象：**Family Z、Standard／Advancedのセリフ音声**

目的は以下の4点です。

1. ZセリフにもLRを正式導入し、最大TTS6回の共通フローへ統一する。
2. 『藪の中』Advancedの武弘の証言 `part3_c6` を、既存3試行の続きであるLR段階から再開する。
3. Fallback・LR適用一覧を更新し、「Zセリフ従来方式」の独立行を整理する。
4. 正式Productionでの配線・検証・SSOT／Git反映を完了する。

既存の承認済み品質基準・音声Style・Voice・Fallback方式は維持してください。

## 2. 新しい正式フロー

Family ZセリフのStandard／Advancedに、以下を適用します。

| 試行 | 方式 | NG時の処理 |
|---|---|---|
| ① | 文脈・感情付きStyle | ②へ |
| ② | 同じ文脈・感情付きStyle | 180秒待機 |
| ③ | 従来Dialogue Style（Fallback） | LRへ |
| LR | Local Rewrite、最大1回 | 書換え後の原稿で④へ |
| ④ | 文脈・感情付きStyle | ⑤へ |
| ⑤ | 同じ文脈・感情付きStyle | 180秒待機 |
| ⑥ | 従来Dialogue Style（Fallback） | Human Review |

**最大TTS6回、LR最大1回、180秒待機最大2回。**

途中で品質GateをPASSした場合は、その時点で終了します。

LRが適用できない場合や、安全・品質上のSTOP条件に該当する場合は、既存の承認済み安全条件に従ってください。

通常のZセリフと同じTTSモデル・Voice・速度・文脈感情Styleを維持し、LR後も同じ品質検査を適用してください。

今回の承認はZセリフへのLR拡大であり、日本語音声・KP音声など、LR対象外の他の区分には拡大しません。

## 3. 『藪の中』AdvancedのLR段階から再開

対象：Family Z『藪の中』Advanced、武弘の証言 `part3_c6`（Voice=Puck、91語）。

このクリップはすでに以下を完了しています。

- #1：文脈・感情付きStyle → NG
- #2：同Style → 減速後再検証NG
- 180秒待機済み
- #3：従来Dialogue Style（Fallback） → 反復検査NG
- Human Review Lock到達

**今回は#1〜#3を再実行せず、LR段階から再開してください。**

実装にあたっては、既存の試行履歴・費用・音声・Gate結果を保持し、新仕様に基づく正規の再開として処理してください。

既存のHuman Review Lock、安全上の試行上限、resume管理を無理に迂回しないこと。

必要な状態移行・実装変更を行い、今回の3試行が消費済みとして正しく引き継がれるようにしてください。

LR後は④〜⑥を必要な範囲で実行し、PASSした時点で停止してください。

### LR品質条件

『藪の中』では特に以下を厳守してください。

- 原作の意味・事実関係を変更しない。
- 武弘の証言内容・人物像・感情表現を維持する。
- 他の証言との矛盾や曖昧さを勝手に解消しない。
- 必要最小限の書換えにとどめる。
- 確定済みKey Phrase・Word・文法・日本語訳等を保護する。
- LR後の最終表示本文・TTS入力・ASR正解原稿の一致を確認する。

LRで適切に改善できない場合は、無理な書換えや品質基準の緩和を行わないでください。

## 4. Fallback・LR適用一覧の更新

正式な一覧を以下の8区分に整理してください。

| 対象 | 3回目のFallback Style | LR | 最大TTS |
|---|---|---|---|
| X/Y/Z Standard 英語本文・Voice等 | 英語短文Style（Minimal） | ○ | 6回 |
| X/Y/Z Advanced 英語本文・Voice等 | 英語短文Style（Minimal） | ○ | 6回 |
| **Zセリフ・文脈感情方式（Std/Adv）** | **従来Dialogue Style** | **○** | **6回** |
| X/Y/Z 日本語音声 | 日本語短文Style（Minimal） | × | 3回 |
| X/Y/Z Key Phrase英語（Std/Adv） | ENGLISH_LOCK（3・4回目） | × | 4回 |
| X/Y/Z Advanced KP英語解説音声 | 英語短文Style（Minimal） | × | 3回 |
| X/Y/Z 英語固定案内音声 | 通常Styleのまま | × | 3回 |
| 固定MP3（Family Y） | なし | — | 0回 |

### Zセリフ従来方式の扱い

従来方式は、現在の正式既定経路では3回目・6回目のFallbackとして使用します。

したがって、**正式Production仕様の一覧から「Zセリフ従来方式」の独立行を削除**してください。

ただし、過去runの再現・互換性・承認済みロールバックのために必要なコードや内部定義は維持してください。

独立行を削除することと、従来Dialogue Styleそのものを撤去することを混同しないでください。

CURRENT_SPEC、関連するROW_MAPPING、実装Policy、テストの整合を取ってください。

## 5. 既存仕様・実装との整合

作業前に以下を確認してください。

- CURRENT_SPEC
- DECISION_LOG
- OPEN_ITEMS
- PM_GOVERNANCE
- `er127_tts_block_policy_01.py`
- `er122_fz_ctx_policy_01.py`
- Family Zの正式TTS生成・Gate・Human Review Lock処理
- LR／Fallback統一仕様と過去Trial
- LR変更内容の最終報告・表示仕様

特に以下が重要です。

1. `Z_DLG_CTX` のLR有効化・最大6回への変更
2. LR前後の試行回数を通算管理すること
3. #3からLRへの状態移行
4. LR後の文脈・感情付きStyle復帰
5. #6での従来Dialogue Fallback
6. retry／fallback／regeneration／resumeとの整合
7. Human Review Lock・終端NG記録の整合
8. Style照合GateとLR採用台帳の整合
9. LR後の表示本文・TTS入力・ASR正解原稿の一致
10. 旧仕様へのDangling Referenceの解消

実装方法は既存の共通LR機構を最大限再利用し、Z専用の重複実装を増やさない方向で判断してください。

既存の正常なX／Y／Z音声生成経路は変更しないこと。

## 6. LR変更内容のユーザー最終報告【必須】

従来の正式採用済み仕様を維持します。

LRが発動した場合、ユーザー向けの最終試聴・確認資料に必ず以下を表示してください。

- Before：LR前の英文
- After：LR後の英文
- **変更箇所を赤字で強調**
- 変更理由
- 対象音声区間
- 最終採用された音声がLR後のものかどうか

Fallbackによる最終採用音声がある場合は、既存仕様どおり濃い青色で区別してください。

LRとFallbackの両方に該当する場合は、双方の情報を表示してください。

これらの注記はユーザー向け最終確認資料に表示し、TTS Prompt・ASR正解原稿・学習者向け本文には混入させないでください。

また、最終表示本文と実際の音声内容が一致することを必須とします。

## 7. Production Wiring・検証

今回の変更はTrial限定ではなく、正式Production採用です。

Family Z Standard／Advanced双方について、正式初回Production経路への実装と検証を実施してください。

必要な検証項目：

- 通常生成2回→180秒→Fallback→LR→通常生成2回→180秒→Fallback
- 最大6回の安全上限
- LR最大1回・再入禁止
- 途中PASS時の即終了
- LR適用不可時の既存安全処理
- LR後の元Style・Voice維持
- ASR・反復検査・減速後再検証
- Human Review Lock・終端NG
- retry／fallback／regeneration／resume
- 既存runからの正規の再開
- 最終本文・音声・学習項目の整合
- X／Y／Zの既存共通経路にRegressionがないこと

**正式runtime evidenceを取得し、DEV／Trial専用経路の動作だけでPRODUCTION_WIREDと判定しないでください。**

Fableによる独立受入評価を実施してください。

## 8. QCD・予算・自律解決

優先順位は **品質 ＞ 完成速度 ＞ 量産単価** です。

- 既存3試行や正常な音声を再生成しない。
- LR・TTSの追加実行は必要最小限とする。
- 既存の共通機構と承認済み品質検査を再利用する。
- 独立した作業は並列化し、完了までの時間を最小化する。
- 既存の開発予算・個別Cap・安全STOP条件を遵守する。
- 予算内の不具合は原因究明→修正→検証まで自律的に解決する。
- 新たな未承認仕様や品質基準変更を行わない。

ZセリフへのLR拡大は、3回NG後の追加処理となるため、量産単価への影響はLR発火率に依存します。

追加LR・TTS費用を実測し、70円／記事セット目標への影響を報告してください。

## 9. 『藪の中』完成候補の再提出

武弘の証言が品質Gateを通過したら、Standard／Advancedの完成候補を再組立し、公開試聴ページを更新してください。

前回修正したVoice配役、Standardの `bandit` 採用、`constable` の追加解説、その他の承認済み内容を維持してください。

完成後は、開発者向け試聴ページを提出してください。

End User向けページの正式Production配線が完了している場合は、そちらも併せて提出してください。未配線の場合は状況を明示し、別途進行中の正式配線タスクと整合させてください。

**記事全体の正式公開は、ユーザーの最終試聴・承認後とします。**

## 10. 完了報告・Status

以下を報告してください。

1. Family Z Standard／AdvancedのProduction Wiring Status
2. 変更後の正式Fallback・LR適用一覧
3. 『藪の中』のLR Before／After（赤字強調）
4. LR後のTTS実行回数・採否・Fallback履歴
5. 最終試聴URL
6. TTS／ASR／品質Gate／Assembly／公開検証結果
7. 追加実費と量産単価への影響
8. Regression・runtime evidence
9. CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS／Git反映結果
10. Fable独立受入結果と未解決事項

Production Wiringの全条件を満たした場合のみ、**PRODUCTION_WIRED**と判定してください。

未完了事項やユーザー判断待ちが残る場合は、対象・理由・次の対応を明示してください。

**最終目標は、Family Zのセリフ音声も他の英語本文・Voiceと同じ最大6回＋LR方式に統一し、今回の『藪の中』を既存3試行の続きから最短で完成候補に戻すことです。**
