# ユーザー指示原文(逐語) FAMILY-Y-VOICE-TABLE-PRODUCTION-WIRING-01 2026-10-26

# Claude Codeへの指示｜Family XYZ 進行案件の決定反映・Closeout

## 1. 今回のユーザー決定：Voice候補

**Family YのVoice候補変更を正式採用（APPROVED_FOR_PRODUCTION）。**

| No. | Family Y 男性 | Family Y 女性 |
|---|---|---|
| 1 | Puck | Zephyr |
| 2 | Schedar | Kore |
| 3 | Fenrir | Leda |
| 4 | Orus | Sulafat |
| 5 | Iapetus | Erinome |

- AlgiebaはFamily Yの候補から除外。
- Family Y Voice 1はPuckを採用。
- 男性5名・女性5名の候補構成を正式仕様に反映する。
- Voice Registry、正式Production経路、必要なテスト、runtime evidence、SSOT/Gitまで整合させ、**PRODUCTION_WIRED**を目指す。
- 既存の完成音声を無断で差し替えない。今後の制作に適用する。
- Trialで判明したポーズ・再生成率の問題も記録する。

**Family Zは変更しない。**

| No. | Family Z 男性 | Family Z 女性 |
|---|---|---|
| 1 | Algieba | Zephyr |
| 2 | Schedar | Kore |
| 3 | Fenrir | Leda |
| 4 | Orus | Sulafat |
| 5 | Puck | Erinome |

ユーザーはFamily ZのAlgiebaの声を気に入っており、**Family YとFamily ZのVoice候補差分を明示的に許容した。**

この差分は承認済みFamily固有仕様としてCURRENT_SPEC／DECISION_LOG等に記録すること。

共通仕様の統一を理由に、Family ZのAlgiebaを削除したりPuckへ変更したりしない。

## 2. Chunk分割｜Family XYZ

承認済み仕様は以下。

- Family X／Y：段落境界で分割、0.2秒ポーズ。
- Family Z：おおむね70語を目安に段落境界で分割、0.2秒ポーズ。
- Standard／Advancedの両方に適用。
- Standardの既存約6%減速を維持。

**Family X/Z：** 正式runtimeで発火確認済み。残るSSOT/Git反映と証拠の最終照合を完了させる。

**Family Y：** 正式承認・配線済みだが、現行本文が1段落固定のため実記事ではChunkが発火しない。

したがって、**Family YはPRODUCTION_WIREDと判定しない。**

現状をOPEN-527等に正確に記録する。本文の段落構成や分割方式は未承認のまま変更しない。

## 3. Family Z｜文脈・感情付きTTS＋Fallback

承認済み仕様：

1. 1回目：文脈・感情付きTTS
2. 1回目NG：同方式で即時再試行
3. 2回目NG：10分待機
4. 3回目：従来方式のTTS
5. 3回目もNG：承認済みの後続回復処理との整合を確認

文脈・感情付きTTS本体および3回目Fallbackまでは正式runtime検証済み。

ただし、Local Rewriteは未配線であり、現行ではHuman Review／STOPに進む。

SSOT/Gitの最終反映を完了し、Local Rewriteについては次項の調査結果と照合すること。

Local Rewriteの新仕様を独断で追加しない。

## 4. Family XYZ｜Retry・Fallback・Local Rewrite全体調査

別途依頼済みの調査を継続する。

全Family・Standard／Advanced・全音声部位について、以下を星取表で整理する。

- 通常TTSの回数・再試行条件
- Fallbackの有無、種類、発動条件
- Local Rewriteの有無、発動条件
- Rewrite後の再TTS・品質検査
- Human Review／STOP条件
- retry／fallback／regeneration／resumeとの整合
- Rewriteを適用しない理由と、その承認・設計記録
- 承認済み仕様と正式Production実装の一致・不一致

特にRewrite不適用の理由は、既存記録で確認できるものと、Claude/Fableの新たな見解を区別すること。

差異は、承認済みの例外／仕様不一致／理由不明・未承認に分類する。

**本件は調査のみ。結果を待たずに無断でRewriteの仕様変更・Production改修を行わない。**

## 5. Key Phrase｜フレーズ7件＋単語3件Trial

既に指示済みのTrialを継続する。

- X「AIの仮想の島」
- X「英国の電車マナー」
- Z「猿の手」
- 各Standard／Advanced、計6レベル
- フレーズ・表現・Idiomを7件、単語を3件要求
- 各レベル2回実行して生成ばらつきも確認

**目的は10件を強制確保することではない。**

返答不足・Gate除外を見込んで多めに要求し、最終的に質の高い候補を6〜7件程度確保できるか評価する。

現行方式と、候補数・単語の拾い上げ・学習価値・品質・原価を比較する。

ProductionのPrompt・Gate・Human Review候補は変更しない。

Trial完了時はVALIDATED／REJECTED／USER_DECISION_REQUIREDに分類し、正式採用はユーザー判断を待つ。

## 6. PM Gate・QCD・完了条件

品質 ＞ Delivery ＞ 量産単価。

独立して進められる作業は並列化し、SSOTやコードの競合がある場合のみ必要な部分を調整する。

承認済み予算・日次上限1,000円（JST）を遵守し、不要な有料生成・追加Trialを行わない。

各案件についてFableが独立して受入評価する。

**PRODUCTION_WIREDの判定条件：**

- 承認済み仕様に一致
- 正式初回Production経路への実装
- retry／fallback／regeneration／resume整合
- 正式runtimeの発火証拠
- 必須Regression／Validator／integration test PASS
- actual model_id・routing等の必要な証拠
- CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS更新
- Git反映
- 未承認仕様やDangling Referenceがないこと

ユーザー承認済みでも、実装・runtime・記録のいずれかが未確認ならPRODUCTION_WIREDとしない。

**報告は案件別に、現在Status、完了事項、未完了事項、QCD影響、必要なユーザー判断のみを簡潔に示すこと。**

特に、Family Y/ZのVoice候補差分は今回正式に許容されたものであり、今後これを未承認の仕様不一致として扱わないこと。

