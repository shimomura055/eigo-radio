# USER_DECISION_REGISTER_01(ユーザー判断レジスタ)

- 作成: 2026-10-12(PM-COFFEE-REASSEMBLY-CONDITIONS-AND-USER-DECISION-REGISTER-01 委任_01)
- **これはSSOTではない。** 正本は`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`。本書は2026-10-12時点の「判断状態の索引」であり、報告前に必ず正本を再照合して更新する(`docs/pm/PM_GOVERNANCE.md` 12節 12-13)。
- 目的: 判断済み・調査中・将来課題が混在して『判断済み事項の再質問』が起きた問題(2026-10-12ユーザー指示)の再発防止。

## 4区分の定義

1. **判断済み**: 再質問せず、承認内容を実装・検証へ引き継ぐ。`APPROVED_FOR_PRODUCTION`を未決へ戻さない。
2. **調査・Trial中**: 結果が出るまで判断を要求しない。
3. **USER_DECISION_REQUIRED(UDR)**: 判断材料が揃い、実際に判断が必要な事項のみ。
4. **Deferred / Non-blocking**: Open Itemとして管理し、必要なタイミングで提示。

## レジスタ(22件。直近報告で列挙した項目)

| # | 項目 | 区分 | 次工程をブロックするか | 管理ID / 根拠(SSOT行) |
|---|---|---|---|---|
| 1 | Coffee v4試聴 / Comment4 Trial-03採否(74/71/84字、現行81字の認識) | **UDR** | **はい**(Coffee再Assemblyの前提=In One Line関連仕様の確定) | OPEN-316(`OPEN_ITEMS.md` L819)、DECISION_LOG「COMMENT4-MINIMAL-PROMPT-TRIAL-03」。再Assembly計画=OPEN-321 |
| 2 | Std Preview/Comment 1〜4 = R2 | **判断済み** | いいえ(反映作業のみ) | DECISION_LOG「STANDARD-JA-AOEDE-STYLE-TRIAL-02 ユーザー決定」、同「PM-COFFEE-REASSEMBLY...」(2026-10-12に承認済み明示、再質問禁止)。反映=OPEN-321。全記事共通化は#22のOPEN-295/298で別管理 |
| 3 | Adv KP英英解説Style = P3 | **判断済み**(2026-10-12記録) | いいえ(反映作業のみ) | OPEN-317(L820、更新済み)、DECISION_LOG「PM-COFFEE-REASSEMBLY...」。推薦P5/P8は無効 |
| 4 | Coffee原稿正本 U1/U2 | **UDR(暫定)** | 要確認(原稿確定はAssemblyの前提になりうる) | **SSOT根拠行を特定できず**(Grep 0件)。直近報告由来の項目名。Fableが原典を指定するまで再提示しない |
| 5 | P8のfallback / Local Rewrite扱い・`PRODUCTION_WIRED`判定 | **UDR**(判定はFable/ユーザー確認待ち) | Production反映完了判定のみ(再Assembly作業自体は止めない) | OPEN-300(L803)。未実測=内側標準retry、fallback/LR時BLOCK実動作 |
| 6 | Adv/Std Local Rewriteでrole Styleが落ちる既存の穴 | **Deferred**(M3 GateでBLOCK済み) | 部分的(Gate 3のLR項目) | OPEN-312(L815) |
| 7 | Rule7(所有格を含むphrase)頻発リスク | **UDR**(Fable/ユーザー判断) | Melos E2E継続に影響 | OPEN-310(L813)、OPEN-308関連 |
| 8 | ASR統一 U5(Local Rewrite)/U7(6%減速)/U9 | **UDR**(統一フロー導入前の判断) | いいえ(既存経路は稼働中) | DECISION_LOG「ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01 委任_06」、OPEN-286〜291、`RECONCILIATION_REPORT_01.md` 9章 U-0〜U-16(U-9の内容は同章を参照) |
| 9 | KP Idiom: (b1)が設計原則『本文全文をLLMへ送らない』と衝突 / WANT定義 | **UDR**(Trial結果に基づく設計判断) | いいえ | `docs/pm/delegation_log/2026-10-12_FAMILY-X-KP-IDIOM-EXTRACTION-SELECTION-TRIAL-01_02.md`(発見事項5)。**OPEN_ITEMS該当行なし**(Grep 0件、起票はFable判断) |
| 10 | Melos Human Review 5clip(試聴後のHR採択) | **UDR**(ユーザー試聴待ち) | はい(Melos E2E tts以降) | `docs/pm/delegation_log/2026-10-12_FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01_12C_hr_review.md`、OPEN-318(L821)、OPEN-308 |
| 11 | 恒久策 D-11(Trial実施可否と予算) | **UDR**(統一フロー設計判断D-1..D-11) | いいえ | `docs/pm/delegation_log/2026-10-11_FAMILY-X-EN-ASR-CONFIRM-RETRY-REDESIGN-01_01.md` L22(TARGET_FLOW_DESIGN_01.md)。OPEN_ITEMS該当行なし |
| 12 | JA数字(三日間/3日間、漢数字表記ゆれ) | **UDR** | いいえ(TTS再生成の浪費は発生) | OPEN-319(L822)、OPEN-287(L790) |
| 13 | He drank(Local Rewriteの原稿不一致) | **判断済み**(ユーザー決定③=原作保持Validator撤廃、gate修正実装済み) | いいえ | DECISION_LOG「FAMILY-Z-MELOS...委任_12B/12C/12D」委任_12D(1) |
| 14 | Melos Voice承認(Algieba暫定) | **調査・Trial中**(再生成・試聴の後にユーザー判断) | 試聴まで判断不要 | OPEN-306(L809) |
| 15 | Dialogue clip TTSモデル不一致(gemini-2.5-pro-preview-tts) | **UDR**(実測済み、モデル統一の要否) | いいえ | OPEN-307(L810) |
| 16 | Budget guardがrun単位で旧run累計を見ない | **Deferred**(回避策=`--approved-budget-jpy`を残枠へ) | いいえ | OPEN-315(L818) |
| 17 | Comment3共通化(Z所有、Adv/Std共通、到着・結末を含めない規則) | **判断済み**(Fable判断、ユーザー再質問なし) | いいえ | DECISION_LOG「委任_12D(2)Comment3規則」 |
| 18 | ASR統一フロー D-1〜D-19 | **UDR**(統一フロー導入は未承認、Production未導入) | いいえ(既存Production経路は稼働) | DECISION_LOG「ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01 委任_06」(`er058_output/RECONCILIATION_FINAL_REPORT_01.md`)、OPEN-286〜291、OPEN-270は是正済みCLOSED |
| 19 | D主+C補助の評価方式正式化・ユーザー実読後の整合 | **調査・Trial中**(ユーザー実読待ち、判断材料未完) | いいえ | OPEN-292(L795)、OPEN-267/268の追記 |
| 20 | 記号QA(生成段階の禁止記号予防/句読点重複)・SCG辞書補強 | **Deferred** | いいえ | OPEN-261(L763)、OPEN-262(L764)、OPEN-263(L766) |
| 21 | Story Pool L05『交尾』・底本権利 / test cp932文字化け | **Deferred**(L05はユーザー実読待ち、cp932は環境起因の軽微修正) | いいえ | OPEN-267(L770)、OPEN-268(L771)、関連OPEN-266/269 |
| 22 | XZ残(Family X/Z共通仕様レビューの残件)・g8(ガス->カス、C1カタカナ率ヒューリスティック)・Std Preview/Commentの全記事共通化 | **Deferred** | いいえ | XZ残: 管理ID `FAMILY-XZ-CROSS-FAMILY-SPEC-REVIEW-01`(`docs/pm/design/2026-10-11_FAMILY-XZ-CROSS-FAMILY-SPEC-REVIEW-01_XZ_MAPPING_01.md`、**OPEN_ITEMS該当行なし**、起票はFable判断)。g8=OPEN-272(L775、U-1)。共通化=OPEN-295(L798)/OPEN-298(L801) |

## 区分別集計(22件)

| 区分 | 件数 | 項目# |
|---|---|---|
| 判断済み | 4 | 2, 3, 13, 17 |
| 調査・Trial中 | 2 | 14, 19 |
| USER_DECISION_REQUIRED | 11 | 1, 4(暫定), 5, 7, 8, 9, 10, 11, 12, 15, 18 |
| Deferred / Non-blocking | 5 | 6, 16, 20, 21, 22 |
| 合計 | 22 | |

## 「次工程をブロックするUDR」のみ(これだけを最優先で提示する)

1. **#1 OPEN-316**: In One Line関連仕様(Comment4 Trial-03採否)。Coffee再Assembly(OPEN-321)の前提。
2. **#10 Melos HR 5clip試聴**(OPEN-318/308): Melos E2E tts以降の再開に必要。

(#4 Coffee原稿正本U1/U2は根拠行を特定できず、Fableが原典を指定した場合のみ提示。#5/#7は特定の完了判定・継続に影響するが、他の作業を止めない。)

## 提示ルール(運用)

- 報告前に本表をCURRENT_SPEC/DECISION_LOG/OPEN_ITEMSと照合し、区分を更新する。
- 『判断済み』は再質問禁止。`APPROVED_FOR_PRODUCTION`を未決扱いに戻さない。
- UDRのうち『ブロックする』ものだけを提示し、Deferred/調査中は一括再提示しない。
