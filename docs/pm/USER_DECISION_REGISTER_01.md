# USER_DECISION_REGISTER_01(ユーザー判断レジスタ)

- 作成: 2026-10-12(PM-COFFEE-REASSEMBLY-CONDITIONS-AND-USER-DECISION-REGISTER-01 委任_01)
- **これはSSOTではない。** 正本は`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`。本書は2026-10-12時点の「判断状態の索引」であり、報告前に必ず正本を再照合して更新する(`docs/pm/PM_GOVERNANCE.md` 12節 12-13)。
- 目的: 判断済み・調査中・将来課題が混在して『判断済み事項の再質問』が起きた問題(2026-10-12ユーザー指示)の再発防止。

## 4区分の定義

1. **判断済み**: 再質問せず、承認内容を実装・検証へ引き継ぐ。`APPROVED_FOR_PRODUCTION`を未決へ戻さない。
2. **調査・Trial中**: 結果が出るまで判断を要求しない。
3. **USER_DECISION_REQUIRED(UDR)**: 判断材料が揃い、実際に判断が必要な事項のみ。
4. **Deferred / Non-blocking**: Open Itemとして管理し、必要なタイミングで提示。

## レジスタ(35件。#23〜#35は2026-10-13追記の索引。要約のみで判断は加えない)

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
| 10 | Melos Human Review 5clip(試聴後のHR採択) | **判断済み**(2026-10-13、Melos HR 3件を個別承認。#23参照) | いいえ | `docs/pm/delegation_log/2026-10-12_FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01_12C_hr_review.md`、OPEN-318(L821)、OPEN-308 |
| 11 | 恒久策 D-11(Trial実施可否と予算) | **UDR**(統一フロー設計判断D-1..D-11) | いいえ | `docs/pm/delegation_log/2026-10-11_FAMILY-X-EN-ASR-CONFIRM-RETRY-REDESIGN-01_01.md` L22(TARGET_FLOW_DESIGN_01.md)。OPEN_ITEMS該当行なし |
| 12 | JA数字(三日間/3日間、漢数字表記ゆれ) | **UDR** | いいえ(TTS再生成の浪費は発生) | OPEN-319(L822)、OPEN-287(L790) |
| 13 | He drank(Local Rewriteの原稿不一致) | **判断済み**(ユーザー決定③=原作保持Validator撤廃、gate修正実装済み) | いいえ | DECISION_LOG「FAMILY-Z-MELOS...委任_12B/12C/12D」委任_12D(1) |
| 14 | Melos Voice承認(Algieba暫定) | **判断保留**(2026-10-13、依存事項待ち・判断時期延期。#23) | いいえ(判断保留) | OPEN-306(L809) |
| 15 | Dialogue clip TTSモデル不一致(gemini-2.5-pro-preview-tts) | **UDR**(実測済み、モデル統一の要否) | いいえ | OPEN-307(L810) |
| 16 | Budget guardがrun単位で旧run累計を見ない | **Deferred**(回避策=`--approved-budget-jpy`を残枠へ) | いいえ | OPEN-315(L818) |
| 17 | Comment3共通化(Z所有、Adv/Std共通、到着・結末を含めない規則) | **判断済み**(Fable判断、ユーザー再質問なし) | いいえ | DECISION_LOG「委任_12D(2)Comment3規則」 |
| 18 | ASR統一フロー D-1〜D-19 | **UDR**(統一フロー導入は未承認、Production未導入) | いいえ(既存Production経路は稼働) | DECISION_LOG「ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01 委任_06」(`er058_output/RECONCILIATION_FINAL_REPORT_01.md`)、OPEN-286〜291、OPEN-270は是正済みCLOSED |
| 19 | D主+C補助の評価方式正式化・ユーザー実読後の整合 | **調査・Trial中**(ユーザー実読待ち、判断材料未完) | いいえ | OPEN-292(L795)、OPEN-267/268の追記 |
| 20 | 記号QA(生成段階の禁止記号予防/句読点重複)・SCG辞書補強 | **Deferred** | いいえ | OPEN-261(L763)、OPEN-262(L764)、OPEN-263(L766) |
| 21 | Story Pool L05『交尾』・底本権利 / test cp932文字化け | **Deferred**(L05はユーザー実読待ち、cp932は環境起因の軽微修正) | いいえ | OPEN-267(L770)、OPEN-268(L771)、関連OPEN-266/269 |
| 22 | XZ残(Family X/Z共通仕様レビューの残件)・g8(ガス->カス、C1カタカナ率ヒューリスティック)・Std Preview/Commentの全記事共通化 | **Deferred** | いいえ | XZ残: 管理ID `FAMILY-XZ-CROSS-FAMILY-SPEC-REVIEW-01`(`docs/pm/design/2026-10-11_FAMILY-XZ-CROSS-FAMILY-SPEC-REVIEW-01_XZ_MAPPING_01.md`、**OPEN_ITEMS該当行なし**、起票はFable判断)。g8=OPEN-272(L775、U-1)。共通化=OPEN-295(L798)/OPEN-298(L801) |
| 23 | **Melos最終試聴・受入判断** | **判断保留**(依存事項待ち、判断時期延期、2026-10-13ユーザー指示)。依存: (a)Voice Prompt改善の正式採用仕様とMelos適用範囲 (b)ASR連結発音・短尺判定の改善(OPEN-318/327/330/331/122(4)/335、短尺ASR判断1〜4)。現行試聴ページは暫定。再試聴依頼禁止 | いいえ(判断保留。追加生成・Production反映は進めない) | OPEN-331/306/320、DECISION_LOG「FAMILY-Z-MELOS-FINAL...委任_04」、`docs/pm/delegation_log/2026-10-13_FAMILY-Z-MELOS-FINAL-ASSEMBLY-AND-ASR-GENERALIZATION-01_04.md` |
| 24 | JA-ASR 判断1〜5(要約のみ、判断は加えない) | **UDR** | いいえ | OPEN-333/334、`docs/pm/delegation_log/2026-10-13_JA-ASR-ORTHOGRAPHIC-EQUIVALENCE-COMPREHENSIVE-01_02.md` |
| 25 | 短尺ASR 判断1〜4(FAMILY-Z-SHORT-CLIP-ASR-CONTEXT-GENERALIZATION-TRIAL-01) | **UDR**(#23の依存事項) | いいえ | OPEN-318/327、`docs/pm/delegation_log/2026-10-13_FAMILY-Z-SHORT-CLIP-ASR-CONTEXT-GENERALIZATION-TRIAL-01_04.md` → ASR-PHONETIC-EQUIVALENCE-GENERALIZATION-01で設計方針合意(2026-10-13)、実装・安全性は未検証(OPEN-339、判断1〜4のうちMelo/Mello非対称[判断3]はOPEN-339論点1へ接続) |
| 26 | KP Idiom 優先度ABC 判断1〜4 | **UDR** | いいえ | OPEN-325、`docs/pm/delegation_log/2026-10-13_FAMILY-X-KP-IDIOM-PRIORITY-ABC-TRIAL-01_01.md` |
| 27 | OPEN-332(Coffee v5文末ポーズ緩和)= 8way/H-speedで代替検討 | **UDR**(8way/H-speed結果待ち) | いいえ | OPEN-332、`docs/pm/delegation_log/2026-10-13_FAMILY-X-COFFEE-V5-PAUSE-ROOT-CAUSE-01_01.md` |
| 28 | Coffee 8way候補選定 | **UDR**(ユーザー試聴・選定。#23の依存事項) | いいえ | `docs/pm/delegation_log/2026-10-13_FAMILY-X-COFFEE-TTS-STYLE-8WAY-AB-TRIAL-01_02.md` |
| 29 | Coffee H-speed候補選定 | **UDR**(ユーザー試聴待ち。#23の依存事項) | いいえ | `docs/pm/delegation_log/2026-10-13_FAMILY-X-COFFEE-TTS-STYLE-H-SPEED-TRIAL-02_02.md` |
| 30 | KP候補選定品質 設計A〜J | **UDR**(設計案提出済み、Fable照合待ち) | いいえ | OPEN-336、`docs/pm/delegation_log/2026-10-13_FAMILY-X-KP-CANDIDATE-SELECTION-QUALITY-DESIGN-01_02.md` |
| 31 | Coffee v5 判断1〜4 | **UDR** | いいえ | OPEN-332、`docs/pm/delegation_log/2026-10-13_FAMILY-X-COFFEE-V5-PAUSE-ROOT-CAUSE-01_01.md` |
| 32 | OPEN-325(KP Idiom抽出・選定改善の採用) | **UDR**(再設計見込み) | いいえ | OPEN-325 |
| 33 | OPEN-333/334/335(JA-ASR低重大度候補、HR queue verdict記録) | **UDR / OPEN候補** | いいえ | OPEN-333/334/335 |
| 34 | OPEN-323 | **判断済み**(CLOSED) | いいえ | `docs/pm/delegation_log/2026-10-13_EIGO-RADIO-QUALITY-CROSS-FAMILY-FOLLOWUP-01_OPEN323.md` |
| 35 | Melos HR 3件(Std part1_c5 attempt4/Adv part1_c5/Std comment_1) | **判断済み**(個別承認、record_human_approval済み) | いいえ | `docs/pm/delegation_log/2026-10-13_FAMILY-Z-MELOS-FINAL-ASSEMBLY-AND-ASR-GENERALIZATION-01_01.md`、CURRENT_SPEC追記 |
| 36 | TRIAL-03予算¥300承認(Coffee H-speed音声Prompt探索、Trialのみ) | **判断済み**(2026-10-13ユーザー承認、累計¥300上限、Production採用なし) | いいえ | `docs/pm/delegation_log/2026-10-13_FAMILY-X-COFFEE-TTS-STYLE-H-SPEED-TRIAL-04_01.md` |
| 37 | (b1)LLM補助抽出 Round 3 Trial承認(Trialのみ) | **判断済み**(2026-10-13ユーザー承認、既存累計¥300上限、Production採用なし) | いいえ | `docs/pm/delegation_log/2026-10-13_FAMILY-X-KP-INTEGRATED-OPTIMIZATION-TRIAL-01_03.md` |
| 38 | 探索Trial一括承認運用ルール(低コスト・既存予算内・Production非変更の探索Trialで個別選択肢を逐一確認しない。Gate承認・Production採用・仕様変更・予算超過・重大品質リスクはユーザー判断) | **判断済み**(2026-10-13ユーザー決定) | いいえ | `docs/pm/PM_GOVERNANCE.md` 7-8節 |
| 39 | K06 Std / K01 Adv(Coffee H-speed TRIAL-04のレベル別Prompt)のユーザー試聴評価 | **判断済み**(2026-10-13ユーザー試聴: **NG**。比較対象から除外。Production採用なし。5候補比較試聴ページ作成済み、候補選定は#29のUDR継続) | いいえ | DECISION_LOG「FAMILY-X-COFFEE-TTS-STYLE-H-SPEED-LISTEN-COMPARE-01 委任_01」、`docs/pm/delegation_log/2026-10-13_FAMILY-X-COFFEE-TTS-STYLE-H-SPEED-LISTEN-COMPARE-01_01.md` |
| 40 | KP `no way`単独選定の最小修正P0X(Meta Adv)の採否 | **判断済み**(ユーザー事前規定「Side effect確認時は不採用・M2P0維持」を適用。Trial Status=REJECTED。Production採用なし) | いいえ | DECISION_LOG「FAMILY-X-KP-NO-WAY-MINIMAL-FIX-TRIAL-01 委任_02」、OPEN-336追記、`er064_output/kp_no_way_fix_01/TRIAL_REPORT_02.md` |
| 41 | ASR発音同等性に基づく一般化判定(全Family共通設計方針)の実装方式・安全性(ASR-PHONETIC-EQUIVALENCE-GENERALIZATION-01) | **USER_DECISION_REQUIRED**(Opus条件Aレビュー後の判断事項4件。設計=DESIGN_REVISED[Opus必須1〜4反映済み]、検証=V1'テキストのみREJECTED/V2'末尾暫定ゲート付きUSER_DECISION_REQUIRED。(1)優先順位R1/F1/M1(Opus推奨R1>F1>M1) (2)暫定非対称の許容か末尾確認の全経路化(OPEN-341) (3)F1是正(OPEN-340、既存成果物の判定がPASS→NGになり得る)の承認 (4)CMU未収録名で綴り基準へ戻すことの許容+初出時1回HR要否) | いいえ(Melos最終試聴#23の依存事項。追加生成・Production反映は進めない) | OPEN-339・340・341・342(OPEN-122(4)/318/327/328/330/331/335と整理)、DECISION_LOG「ASR-PHONETIC-EQUIVALENCE-GENERALIZATION-01 委任_01/委任_02」、`er068_output/asr_phonetic_equivalence_generalization_01/`(DESIGN_DRAFT_02.md/OFFLINE_EVAL_02.md/FINAL_SUMMARY_01.md) |

| 42 | Family Z Std PreviewのFamily X基準統一Promptの採否・追加調整要否(OPEN-338。設計方針=Family X基準はユーザー確定済み、変更後Promptは検証済みでなくProduction未採用) | **USER_DECISION_REQUIRED**(Trial結果: あらすじ化なし/抽象・評論調残存/終盤示唆の可能性、1サンプル) | いいえ | DECISION_LOG「FAMILY-Z-STANDARD-PREVIEW-X-ALIGNMENT-01 委任_01」、`er070_output/family_z_std_preview_x_alignment_01/TRIAL_REPORT_01.md`。2026-10-13追記: 3 take比較(#44)でStd 3件も抽象・評論調で同傾向、`er072_output/melos_preview_std_adv_3take_01/COMPARE_REPORT_01.md` 2026-10-13追記: Comment参照条件B〜E比較(FAMILY-Z-STANDARD-PREVIEW-COMMENT-DEPENDENCY-TRIAL-01、#48) |

| 43 | Family Z 語末s名+s始まり動詞の分割Trial(FAMILY-Z-ATTRIBUTION-CLIP-SPLIT-IMPROVEMENT-TRIAL-01、OPEN-318)のR1(原稿側ルール「語末歯擦音の固有名詞の直後に歯擦音始まりの語を置かない」)のProduction化判断 | **USER_DECISION_REQUIRED**(Trial、s+s融合が主因と分離、効果はMelos型の名前のみ、R2は効果未検出。選択肢A=Writer prompt指針+決定論WARN lintをProduction化、B=追加確認[別名前タイプ・ledger未登録名のPLなし通過率]を先に、C=見送り。Opus推奨順 R1>F1>M1) | いいえ(Melos最終試聴#23の依存事項。Production無変更) | OPEN-318、DECISION_LOG「FAMILY-Z-ATTRIBUTION-CLIP-SPLIT-IMPROVEMENT-TRIAL-01 委任_01〜_02」、`er069_output/attribution_clip_split_trial_01/trial_conclusion_02.md` |
| 44 | Family Z Std/Adv Preview 3 take比較(FAMILY-Z-MELOS-PREVIEW-STD-ADV-3TAKE-COMPARE-01、OPEN-338)の結果を受けたStd Preview方針(統一Promptの採否・追加切り分けTrialの要否) | **USER_DECISION_REQUIRED**(Trial、Std 3件は抽象・評論調で一貫、Adv 3件は具体的発端を提示。原因はComment量との交絡があり断定不可。選択肢案: A=Comment量/Prompt構造の切り分けTrialを先に行う、B=統一Promptを現状評価のまま判断、C=見送り。採用判断はしていない) | いいえ | DECISION_LOG「FAMILY-Z-MELOS-PREVIEW-STD-ADV-3TAKE-COMPARE-01 委任_01」、`er072_output/melos_preview_std_adv_3take_01/COMPARE_REPORT_01.md` 2026-10-13追記: Comment参照条件B〜E比較(FAMILY-Z-STANDARD-PREVIEW-COMMENT-DEPENDENCY-TRIAL-01、#48) |
| 45 | Family Z KPのDB Hybrid+M2P0移行方式(Z-1。Z KPは現状Strategy L) | **判断済み**(2026-10-13ユーザー正式決定: Family Z KP=Strategy L維持、DB Hybrid+M2P0移行案=REJECTED。以前の『ZにもM2P0適用』決定は撤回。Family XのM2P0・両FamilyのN01は維持。再度ユーザー判断に戻さない) | いいえ | OPEN-344(CLOSED/REJECTED)、DECISION_LOG「FAMILY-Z-KP-STRATEGY-L-DECISION-CLOSEOUT-01」 |
| 46 | N01の『sharing a true story』文言のFamily Z(Fiction)での扱い(N-2) | **判断済み**(2026-10-13ユーザー正式判断: 文言変更不要。再度ユーザー判断に戻さない) | いいえ | OPEN-345(CLOSED)、DECISION_LOG「FAMILY-XZ-M2P0-N01-PRODUCTION-WIRING-01 委任_03」 |
| 47 | Coffee Std未完(委任_03でKP再生成も再度INVALID[同じrank5『based on』]・Adv正式assembleがAudio Validation GateでBLOCK・KP canonicalization INVALID・Std Full Story part2のfallback take)の扱い=追加KP再生成の可否[委任_03で許可1回を使用済み・同一INVALID再発のため再実行は無意味、selection/canonicalization側の対処は新仕様]・fallback takeの人間承認か再生成か・runner assemble経由の完走方法(N-1適用範囲/N-3対象=Full Storyのみ/X-1原稿正本/X-2再生成範囲は推奨解釈で実装) | **開発側責任として是正中**(2026-10-13ユーザー指示、FAMILY-XZ-M2P0-N01-PRODUCTION-COMPLETION-01。是正①②=FIXED_PENDING_PRODUCTION_RUN、③と完走は委任_02。残る実判断候補=Part 2 N01再生成後の聴感のみ) | はい(Family X `PRODUCTION_WIRED`付与の前提) | OPEN-343、`er071_output/m2p0_n01_production_wiring_01/FINAL_REPORT_02.md` |
| 48 | Family Z Std PreviewのComment参照条件(FAMILY-Z-STANDARD-PREVIEW-COMMENT-DEPENDENCY-TRIAL-01、OPEN-338)の結果を受けた方針=PreviewとComment 1の役割衝突への対処[P1 Preview構成指針追加=Family X共通仕様変更要否 / P2 Preview先行+Comment 1調整=処理フロー変更(Opus条件A) / 現状維持]、Comment 1重複の許容範囲 | **USER_DECISION_REQUIRED** | いいえ(Family Z記事再生成・音声化STOP維持中) | OPEN-338、`er074_output/family_z_std_preview_comment_dependency_01/FINAL_REPORT_01.md` |
| 49 | Coffee Std/Advの聴感判断(Std 6%減速後168WPM[参考157±6の外]・Adv 178WPM・文末ポーズ平均572ms。Productionに自動の速度/ポーズ合否基準なし、新Gateは作っていない) | **USER_DECISION_REQUIRED**(試聴ページで確認) | いいえ | `er071_output/m2p0_n01_production_wiring_01/EVIDENCE_01.md`、試聴ページ |
| 50 | Std KP『based on』型のRule7 INVALID再発への対処(selection段の機能語fragment選択防止・canonicalization側対処は新仕様候補/手動KP差替え/Std KPなしで進行)と、Adv/Std正式`--stage assemble`の完走手段(v5再利用segmentのAudio Validation Gate上の扱い=OPEN-346②) | **開発側責任として是正中**(2026-10-13ユーザー指示、FAMILY-XZ-M2P0-N01-PRODUCTION-COMPLETION-01。是正①②=FIXED_PENDING_PRODUCTION_RUN、③と完走は委任_02。残る実判断候補=Adv preview/in_one_lineのProduction検証手段[別take再生成か否か]はFable切り分け) | はい(Family X `PRODUCTION_WIRED`付与の前提) | OPEN-343/346/310、`er071_output/m2p0_n01_production_wiring_01/FINAL_REPORT_02.md` |
| 51 | Family Z Std Preview/Comment 1の役割分担方式(A=Preview先行・Comment 1補足 / B=Comment 1先行[今回実装はREJECTED案、Adv型Comment 1適用は未検証] / E方式[Preview単独先行・Comment現行] / 現状維持)、およびStd Comment 1を聴取ガイド化するか。#48(P1/P2/現状維持)の具体化・関連 | **USER_DECISION_REQUIRED** | いいえ(Family Z記事再生成・音声化STOP維持中) | OPEN-338、`er076_output/family_z_preview_comment1_dual_trial_01/SETS_01.md`・`PRODUCTION_IMPACT_01.md`(FAMILY-Z-PREVIEW-COMMENT1-DUAL-TRIAL-01) |
| 52 | **UDR-1 OOV(CMU未収録語)の扱い**(ASR-PHONETIC-EQUIVALENCE-M1-F1-PRODUCTION-WIRING-01、OPEN-339): A=(iii) 綴りfallbackでOOVも救済 / B=読み確定+Pronunciation Ledger高信頼化(unique・信頼度high)のみ使用 / C=(i) CMU収録語のみで止める。Opus評価: Aは『辞書駆動・allow-listなし』の必須条件に抵触、Bが唯一原理的、12/12目標自体の見直しが必要。M1(i)実益=674ペアで新規受理0件。OOVコードは未実装 | **USER_DECISION_REQUIRED** | はい(M1配線のみ。F1は独立に実装済み) | OPEN-339、`er075_output/m1_f1_production_wiring_01/OOV_SAFETY_01.md`・`M1_BENEFIT_CENSUS_01.md` |
| 53 | **UDR-2 Eq Layer(OPEN-122)のF1ガード**: F1の戻り値diffを最初の残差とし、Eq Layerは残差ちょうど1件かつ同位置のみ評価(OPEN-122の受理範囲を広げず限定方向のみ)。**今回実装済み**として記録。ユーザー異議があれば差戻し | **USER_DECISION_REQUIRED**(実装済み記録、異議時のみ差戻し) | いいえ | OPEN-340、OF-168、`er011_connected_speech_equivalence_layer_production_01.py` |
| 54 | **UDR-3 US sea blockade 4件の扱いと誤NG定義**: 固定定義『全差分が承認済みPattern A/B/Cまたは既存正規化で説明できるのにF1が非PASS』に4件は該当しない(Pattern Aが`US`→`U`+sを複数形と誤認、未承認の頭字語正規化)。頭字語の扱いは新規OPEN-348として起票済み(未承認・未実装)。誤NG定義の確定と頭字語扱いの要否 | **USER_DECISION_REQUIRED** | いいえ | OPEN-348、`er075_output/m1_f1_production_wiring_01/F1_IMPACT_CENSUS_02.md` |
| 55 | **UDR-4 F1とM1のPRODUCTION_WIRED分離宣言**: F1=`WIRED_PENDING_RUNTIME_EVIDENCE`(実装済み・Production runでの自然発生evidence取得後に`PRODUCTION_WIRED`)、M1=設計済み未配線。F1の`PRODUCTION_WIRED`をM1やOOV判断に依存させない | **USER_DECISION_REQUIRED**(分離宣言の確認) | いいえ | OPEN-340/339、`er075_output/m1_f1_production_wiring_01/` |

## 区分別集計(2026-10-13更新・51件(#51追加: FAMILY-Z-PREVIEW-COMMENT1-DUAL-TRIAL-01)。#45を判断済み化[Strategy L維持・移行案REJECTED、FAMILY-Z-KP-STRATEGY-L-DECISION-CLOSEOUT-01]。#49・#50追加・#46判断済み化・#45はTrial承認済み/移行方式採用判断のみ未決[FAMILY-XZ-M2P0-N01-PRODUCTION-WIRING-01 委任_03]。#48追加[Comment参照条件Trial、USER_DECISION_REQUIRED]。#45〜#47追加[M2P0/N01 Production配線、USER_DECISION_REQUIRED]。#44追加[3 take比較、USER_DECISION_REQUIRED]。#43追加[分割Trial R1判断、USER_DECISION_REQUIRED]。#41はOpus条件A後にUSER_DECISION_REQUIRED化。#42追加[FAMILY-Z-STANDARD-PREVIEW-X-ALIGNMENT-01、USER_DECISION_REQUIRED]。#41追加[ASR-PHONETIC-EQUIVALENCE-GENERALIZATION-01、調査・Trial中]。#39・#40追加。#10は判断済みへ、#14と#23は判断保留へ、#36追加)

| 区分 | 件数 | 項目# |
|---|---|---|
| 判断済み | 14 | 2, 3, 10, 13, 17, 34, 35, 36, 37, 38, 39, 40, 45, 46 |
| 判断保留(依存事項待ち、判断時期延期) | 2 | 14, 23 |
| 調査・Trial中 | 1 | 19 |
| USER_DECISION_REQUIRED | 33 | 1, 4(暫定), 5, 7, 8, 9, 11, 12, 15, 18, 24〜33, 41, 42, 43, 44, 47, 48, 49, 50, 51, 52, 53, 54, 55 |
| Deferred / Non-blocking | 5 | 6, 16, 20, 21, 22 |
| 合計 | 55 | |

## 「次工程をブロックするUDR」のみ(これだけを最優先で提示する)

1. **#1 OPEN-316**: In One Line関連仕様(Comment4 Trial-03採否)。Coffee再Assembly(OPEN-321)の前提。
2. (2026-10-13更新)旧#10 Melos HR試聴は判断済み。Melos最終試聴(#23)は判断保留のためブロックUDRに含めない。

(#4 Coffee原稿正本U1/U2は根拠行を特定できず、Fableが原典を指定した場合のみ提示。#5/#7は特定の完了判定・継続に影響するが、他の作業を止めない。)

## 提示ルール(運用)

- 報告前に本表をCURRENT_SPEC/DECISION_LOG/OPEN_ITEMSと照合し、区分を更新する。
- 『判断済み』は再質問禁止。`APPROVED_FOR_PRODUCTION`を未決扱いに戻さない。
- UDRのうち『ブロックする』ものだけを提示し、Deferred/調査中は一括再提示しない。
