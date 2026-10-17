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
| 3 | Adv KP英英解説Style = P3 | **判断済み**(2026-10-12記録) | いいえ(反映作業のみ) | OPEN-317(L820、更新済み)、DECISION_LOG「PM-COFFEE-REASSEMBLY...」。推薦P5/P8は無効 【2026-10-16 09:00更新】Adv KP英英解説Styleは**P7が旧P3を置換**(ユーザー最終判断、原文=`docs/pm/delegation_log/2026-10-16_FAMILY-X-20261016-0900-USER-DECISION-RECORD-01_USER.md`。判断済み、Status=`APPROVED_FOR_PRODUCTION`・未配線、旧P3は履歴)。P7の同名別Trial(P2+P5)との取違えはFable確認要 |
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
| 47 | Coffee Std未完(委任_03でKP再生成も再度INVALID[同じrank5『based on』]・Adv正式assembleがAudio Validation GateでBLOCK・KP canonicalization INVALID・Std Full Story part2のfallback take)の扱い=追加KP再生成の可否[委任_03で許可1回を使用済み・同一INVALID再発のため再実行は無意味、selection/canonicalization側の対処は新仕様]・fallback takeの人間承認か再生成か・runner assemble経由の完走方法(N-1適用範囲/N-3対象=Full Storyのみ/X-1原稿正本/X-2再生成範囲は推奨解釈で実装) | **開発側責任として是正中**(2026-10-13ユーザー指示、FAMILY-XZ-M2P0-N01-PRODUCTION-COMPLETION-01。是正①②=FIXED_PENDING_PRODUCTION_RUN、③と完走は委任_02。残る実判断候補=Part 2 N01再生成後の聴感のみ) | はい(Family X `PRODUCTION_WIRED`付与の前提) | OPEN-343、`er071_output/m2p0_n01_production_wiring_01/FINAL_REPORT_02.md` **【2026-10-13 委任_02追記】** 是正①②③実装済み・Std KPは別item(『raw-bean』)でINVALID再発(OPEN-349)、Adv Preview E1未配線(OPEN-350)でSTOP。開発側責任は継続、ユーザー判断が必要なのはOPEN-349/350の2点(Fable経由)。 |
| 48 | Family Z Std PreviewのComment参照条件(FAMILY-Z-STANDARD-PREVIEW-COMMENT-DEPENDENCY-TRIAL-01、OPEN-338)の結果を受けた方針=PreviewとComment 1の役割衝突への対処[P1 Preview構成指針追加=Family X共通仕様変更要否 / P2 Preview先行+Comment 1調整=処理フロー変更(Opus条件A) / 現状維持]、Comment 1重複の許容範囲 | **USER_DECISION_REQUIRED**(#51へ統合参照: A/B Trial完了、採否は#51で判断) | いいえ(Family Z記事再生成・音声化STOP維持中) | OPEN-338、`er074_output/family_z_std_preview_comment_dependency_01/FINAL_REPORT_01.md` |
| 49 | Coffee Std/Advの聴感判断(Std 6%減速後168WPM[参考157±6の外]・Adv 178WPM・文末ポーズ平均572ms。Productionに自動の速度/ポーズ合否基準なし、新Gateは作っていない) | **Deferred**(2026-10-14、完成版試聴ページ`user_test/coffee_m2p0_n01_final_03/`提示時に判断、タイミング合意済み。Std 6%減速後157.7WPM/Adv 178.2WPM/文末ポーズ平均 Std629ms・Adv572msを同ページに掲載) | いいえ | `er071_output/m2p0_n01_production_wiring_01/EVIDENCE_01.md`、試聴ページ |
| 50 | Std KP『based on』型のRule7 INVALID再発への対処(selection段の機能語fragment選択防止・canonicalization側対処は新仕様候補/手動KP差替え/Std KPなしで進行)と、Adv/Std正式`--stage assemble`の完走手段(v5再利用segmentのAudio Validation Gate上の扱い=OPEN-346②) | **開発側責任として是正中**(2026-10-13ユーザー指示、FAMILY-XZ-M2P0-N01-PRODUCTION-COMPLETION-01。是正①②=FIXED_PENDING_PRODUCTION_RUN、③と完走は委任_02。残る実判断候補=Adv preview/in_one_lineのProduction検証手段[別take再生成か否か]はFable切り分け) | はい(Family X `PRODUCTION_WIRED`付与の前提) | OPEN-343/346/310、`er071_output/m2p0_n01_production_wiring_01/FINAL_REPORT_02.md` **【2026-10-13 委任_02追記】** 是正①②③実装済み・Std KPは別item(『raw-bean』)でINVALID再発(OPEN-349)、Adv Preview E1未配線(OPEN-350)でSTOP。開発側責任は継続、ユーザー判断が必要なのはOPEN-349/350の2点(Fable経由)。 |
| 51 | Family Z Std Preview/Comment 1の役割分担方式の採否。元指示(2026-10-13/14)の枠組み=A(Preview先行・Comment 1補足)/B(Advanced型の非常に短いComment 1先行→独立Preview)の独立Trial各3 Take・合計6ペア・上限JPY20は**Trial完了**(Aは委任_01、Bは委任_03で仕様どおり正実施。旧Bは仕様差で無効)。ユーザーが6セット(`SETS_02.md`)を読んでA採否・B採否・どちらも不採用(現状維持)を判断する。(以前の『Aか現状維持』『B′を先にTrial』の3択表現は撤回。追加Trialは未承認で実施しない。) 関連: Melos最終試聴・受入(#23)は判断保留・未完了のまま。#48(P1/P2/現状維持)は本件へ統合参照 | **USER_DECISION_REQUIRED**(Trial完了・採否ユーザー判断待ち) | いいえ(Family Z記事再生成・音声化STOP維持中。Production採用は人間ユーザーのみ) | OPEN-338、`er076_output/family_z_preview_comment1_dual_trial_01/SETS_02.md`・`PRODUCTION_IMPACT_02.md`・`SETS_01.md`(FAMILY-Z-PREVIEW-COMMENT1-DUAL-TRIAL-01 委任_03) |
| 52 | **UDR-1 OOV(CMU未収録語)の扱い**(ASR-PHONETIC-EQUIVALENCE-M1-F1-PRODUCTION-WIRING-01、OPEN-339): A=(iii) 綴りfallbackでOOVも救済 / B=読み確定+Pronunciation Ledger高信頼化(unique・信頼度high)のみ使用 / C=(i) CMU収録語のみで止める。Opus評価: Aは『辞書駆動・allow-listなし』の必須条件に抵触、Bが唯一原理的、12/12目標自体の見直しが必要。M1(i)実益=674ペアで新規受理0件。OOVコードは未実装 | **判断済み**(2026-10-13ユーザー承認「複数の合理的な発音候補のいずれか1つで音韻整合すれば許容」、2026-10-14再確認。**綴りだけを根拠に任意の発音を許容してよいわけではない**=許容不可を併記。同じ採否を再質問しない。M1は配線済み・隔離runner evidence取得済み・`PRODUCTION_WIRED`未宣言[`CHECKLIST_M1_01.md`]) | いいえ | STOP-NOTICE-SCOPE-RULE-PRODUCTION-01/ASR-M1-OOV-MULTI-PRONUNCIATION-PRODUCTION-01、OPEN-339、`er075_output/m1_f1_production_wiring_01/OOV_SAFETY_01.md`・`M1_BENEFIT_CENSUS_01.md` |
| 53 | **UDR-2 Eq Layer(OPEN-122)のF1ガード**: F1の戻り値diffを最初の残差とし、Eq Layerは残差ちょうど1件かつ同位置のみ評価(OPEN-122の受理範囲を広げず限定方向のみ)。**今回実装済み**として記録。ユーザー異議があれば差戻し | **判断済み(判断不要・既存承認範囲内)**(2026-10-14照合: ユーザー承認済みF1仕様[2026-10-13、OPEN-340、全差分点検で残差を厳しくする方向のみ]の帰結として、Eq Layerを残差ちょうど1件かつ同位置のみ評価に限定。実装[`er011_connected_speech_equivalence_layer_production_01.py` L241-256]は受理範囲を広げず限定のみ=範囲内。新規の許容ルールではないため再承認を求めない。『異議がなければ承認』扱いはしていない) | いいえ | STOP-NOTICE-SCOPE-RULE-PRODUCTION-01、OPEN-340、OF-168、`er011_connected_speech_equivalence_layer_production_01.py` |
| 54 | **UDR-3 US sea blockade 4件の扱いと誤NG定義**: 固定定義『全差分が承認済みPattern A/B/Cまたは既存正規化で説明できるのにF1が非PASS』に4件は該当しない(Pattern Aが`US`→`U`+sを複数形と誤認、未承認の頭字語正規化)。頭字語の扱いは新規OPEN-348として起票済み(未承認・未実装)。誤NG定義の確定と頭字語扱いの要否 | **判断済み**(2026-10-14ユーザー: 当面、新たな頭字語正規化仕様の開発・Production採用は進めない。未解決の実害はOPEN-348で管理) | いいえ | STOP-NOTICE-SCOPE-RULE-PRODUCTION-01、OPEN-348、`er075_output/m1_f1_production_wiring_01/F1_IMPACT_CENSUS_02.md` |
| 55 | **UDR-4 F1とM1のPRODUCTION_WIRED分離宣言**: F1=`WIRED_PENDING_RUNTIME_EVIDENCE`(実装済み・Production runでの自然発生evidence取得後に`PRODUCTION_WIRED`)、M1=設計済み未配線。F1の`PRODUCTION_WIRED`をM1やOOV判断に依存させない | **判断済み**(2026-10-14ユーザー: F1とM1は仕様・runtime evidence・Production Gateを別々に評価。Coffee AdvancedでF1のruntime発火が確認された報告だけを根拠に全Checklistを省略して`PRODUCTION_WIRED`を付与しない。区分管理自体の再承認は不要) | いいえ | STOP-NOTICE-SCOPE-RULE-PRODUCTION-01、OPEN-340/339、`er075_output/m1_f1_production_wiring_01/` |
| 56 | (Fable経由) Std KP Rule7でspan外補語を許容する新ルール(OPEN-349)とAdv Preview E1配線(OPEN-350) | **USER_DECISION_REQUIRED**(Fable判断・Opus条件B/A) | いいえ | OPEN-349/350、`er071_output/m2p0_n01_production_wiring_01/completion_02/CHECKLIST_03.md` |
| 57 | (Fable経由) **G**: 案A'でKPが元候補の外へ伸びたitemのja_gloss整合(Coffee Std KP #4『based on interviews』/『～をもとにした』)。G1=軽度不整合は許容して続行 / G2=gloss再生成工程の新設 / G3=窓上限縮小等A'再設計 | **判断不要**(2026-10-14ユーザー指示=基本品質要件として開発側で是正。gloss再整合工程で是正済み、Coffee Std完成。残る新工程の採用位置づけはOPEN-356) | いいえ(Coffee Std完成済み) | OPEN-352、`er071_output/m2p0_n01_production_wiring_01/completion_03/gloss_check_03.md` |
| 58 | (Fable経由) **C**: 供給/選定段のfragment候補対策(C1〜C4)。canonicalization側A'は事後吸収のみ | **判断済み**(2026-10-14 C4『当面変更なし・A′の結果を確認』選択済み、再提示しない) | いいえ | OPEN-353、`completion_03/expansion_census_03.md` |
| 59 | (Fable経由) **PM-AUTONOMOUS-PROJECT-OPERATING-MODEL-RESEARCH-01 運営モデル採否**(FINAL_REPORT_01 §8の7項目、U1〜U4含む: 案D採否とPhase 1着手/QCD床・天井/予算と合計ハード上限[U3]/バグ修正のシャドー運用と包括承認[U2]/Production Gate厳格化もユーザー判断[U1]/HR方針/CLAUDE.md PM層削除[U4]) | **USER_DECISION_REQUIRED**(Research完了・Opus条件A所見OF-209〜224反映済み。規則・Agent定義・SSOT・Productionは変更していない) | いいえ(他の生産作業はブロックしない) | `docs/research/PM-AUTONOMOUS-PROJECT-OPERATING-MODEL-RESEARCH-01/FINAL_REPORT_01.md` §8 |
| 60 | (Fable経由) **KP gloss再整合工程(修正版corrected)のProduction採用**(KGDC VALIDATED後の採用判断、旧OPEN-356の採用位置づけUDR[Q1/Q2/Q3・既定ON/OFF・gate化・P3書換許容]の後継) | **判断済み**(2026-10-15採用。`APPROVED_FOR_PRODUCTION`、付随事項3件承認: 機械検査=記録のみ/HR通知先=報告書+run summary+stdout+STOP status[音声HR queue不使用]/規則15行型=選定段責務。採用対象=corrected、legacy撤去、Production既定ONへ) | いいえ(承認済みの配線作業。ただし`PRODUCTION_WIRED`宣言は10条件充足後、OPEN-359未解決でgloss不整合KPが流出しうるなら不可) | DECISION_LOG「KP-GLOSS-ALIGNMENT-CORRECTED-PRODUCTION-WIRING-01 委任_01」、OPEN-356/359、`er071_output/m2p0_n01_production_wiring_01/gloss_alignment_production_wiring_01/PRODUCTION_WIRING_DESIGN_01.md` **【追記2026-10-15 委任_04】配線済み・既定ON(Production正式runner)。`PRODUCTION_WIRED`判定は保留(Z E2E完成未確認、#70)。** |
| 61 | (Fable経由) **KGCPW 委任_03で出たユーザー判断事項**: (a)Adv英語解説LLMのphraseがdisplay_phrase基準でglossと食い違う(OPEN-360、OF-KGCPW-18) (b)A/B/C等Legacy Familyへの共有Gate関所追加(OPEN-362、OF-KGCPW-10) (c)OPEN-359本体(b)冗長/記号NGのKPがXで完成へ進む・(c)放棄attemptのartifactがTTSへ進む(別承認) | **USER_DECISION_REQUIRED**(未決。`PRODUCTION_WIRED`判定[Fable委任_04]とは独立に提示可) | いいえ(他の生産作業はブロックしない。ただしOPEN-359未解決でXから不整合KP流出しうる点は`PRODUCTION_WIRED`判定で考慮) | OPEN-359/360/362、er071_output/m2p0_n01_production_wiring_01/gloss_alignment_production_wiring_01/VALIDATION_WIRING_03.md **【追記2026-10-15 委任_04】配線済み・PRODUCTION_WIRED判定保留(OPEN-359本体未解決・Z E2E完成未確認)。** |
| 62 | (Fable経由) **PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01 Day3〜4 ユーザー判断U1〜U6** | **判断済み**(2026-10-15: U1 Charter案A/U2 回数制不採用・QDC管理/U3 Agent役割案A/U3' 5条件付き既定OFF一般例外+違反時廃止/U4(a)(b)(c)承認/U5 量産費70円・日次1,000円を必須実装/U6 Open Item管理。実装=F2 `a342f7b52`・F1 `71baeb78f`。#59『運営モデル採否』のDay1〜Day2分はこの#62で判断済み、#59の残項目は別途) | いいえ(実装進行中。運営刷新全体は未完了、盲検リプレイ未実施) | DECISION_LOG『PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01 Day3〜4 ユーザー正式判断U1〜U6』、OPEN-363 |
| 63 | (Fable経由) **U2-Q1: 11-4(自律3回・4回目以降毎回ユーザーGate)の取扱い**(A現行維持/B回数基準→QDC基準へ置換[推奨]/C回数拡大) | **判断済み**(2026-10-15ユーザー正式承認 決定②=案B採用: 11-4の固定回数制限を撤廃しQDC7観点へ。元の状態『USER_DECISION_REQUIRED[非ブロッキング。回答まで11-4は逐語維持]』。反映=PM_GOVERNANCE 11-4/11-6、`286b71e9a`) | いいえ | `day3/U2_AUTONOMOUS_RESOLUTION_RULE_DESIGN_01.md` §3 U2-Q1、PM_GOVERNANCE 11-4/11-6、OPEN-363 |
| 64 | (Fable経由) **U2-Q2: L3診断後のHuman Gate**(A当面維持[推奨]/B統合/C廃止) | **Deferred**(維持。盲検リプレイ後に再提示) | いいえ | 同書 §3 U2-Q2、OPEN-363 |
| 65 | (Fable経由) **U3'-Q1: 潜在迂回路(未発火・未有効化)をSUSPENDED(失効ではない・安全停止してユーザー裁定)とするFable判断の確認**(ユーザー原文は『隔離が破られ承認前に発火または有効配線された場合』に廃止と定め、『SUSPENDED』はFableが追加した設計=ユーザー原文の解釈を含む) | **判断済み**(2026-10-15ユーザー正式承認 決定③A: ACTIVE/SUSPENDED/REVOKED運用。元の状態『Deferred / Non-blocking[確認推奨]』。反映=PM_GOVERNANCE 11-7、`286b71e9a`) | いいえ | PM_GOVERNANCE 11-7、OF-D3-05、OPEN-365 |
| 66 | (Fable経由) **U5-Q1/Q2: 70円のTTS判定=Production実経路で判定しBatch換算を併記(未配線表示)/1,000円/日の成文化と超過見込み=実行前承認** | **判断済み**(2026-10-15ユーザー正式承認 決定③B: Production実経路の実費基準・Batch換算は参考・70円は目標でSTOP条件でない。元の状態『Deferred / Non-blocking[確認推奨]』。反映=PM_GOVERNANCE 15-9、`286b71e9a`。7-4『量産=Batch前提』は不変) | いいえ | `day3/U5_COST_MANAGEMENT_DESIGN_01.md` §6、OF-D3-10、OPEN-366 |
| 67 | (Fable経由) **U6: pre-commit secret scan hook** | **Deferred / Non-blocking**(ユーザー合意=Open Itemで継続管理。再質問しない) | いいえ | OPEN-364 |
| 68 | (Fable経由) **STANDARD-KP-JA-TTS-STYLE-TRIAL-01/02: Std KP日本語意味のStyle候補の試聴と採否**(Trial-01試聴済み=P5が最も希望に近いがやや抑制的→P5基準でTrial-02[P6〜P10]の試聴待ち) | **USER_DECISION_REQUIRED**(Trial-02ユーザー試聴待ち。採用時はProduction変更=Opus条件C) | いいえ | OPEN-367、`er057_output/std_kp_ja_style_trial_02/TRIAL_REPORT_02.md`、試聴ページ https://shimomura055.github.io/eigo-radio/user_test/coffee_std_kp_ja_style_trial_02/index.html 【2026-10-16 09:00更新】**判断済み**(ユーザー最終判断: Std KP日本語意味=**P8**採用、旧M2を置換。原文=`docs/pm/delegation_log/2026-10-16_FAMILY-X-20261016-0900-USER-DECISION-RECORD-01_USER.md`。Status=`APPROVED_FOR_PRODUCTION`・Production未配線)。区分は『USER_DECISION_REQUIRED』から『判断済み・未配線』へ(表中の元の区分記載は履歴として保持) |
| 69 | (Fable経由) **FAMILY-X-COFFEE-FINAL-SPEC-COMPLETENESS-AUDIT-01 監査(a)〜(d)**: (a)In One Lineの仕様の持ち方[A=CURRENT_SPEC:583準拠/B=2文方針を正式化/C=Coffeeのみ2〜3文+仕様化は後、推奨C] (b)是正範囲と順序の承認[1=A+B+C最大17ファイル(推奨)/2=IOLのみ先行/3=Trial扱いで記録] (c)Adv Comment1〜4の承認Style正本[E0維持かE2_UPBEAT相当、ユーザー試聴で決定] (d)Coffee原稿の正本[v5 Tone原稿維持の確認、既存UDR #4と重複] | **USER_DECISION_REQUIRED**(監査完了・STOP・ユーザー判断待ち。ユーザー報告済み2026-10-15) | いいえ(他の生産作業はブロックしない。Coffee再生成のみ待つ) | `er071_output/m2p0_n01_production_wiring_01/coffee_spec_completeness_audit_01/AUDIT_REPORT_01.md` §9(commit `8f8a43d1b`) 【2026-10-16 09:00更新】(a)In One Line=**基本2文・必要な場合のみ3文、旧1文Prompt改修**で判断済み・配線待ち(原文=`docs/pm/delegation_log/2026-10-16_FAMILY-X-20261016-0900-USER-DECISION-RECORD-01_USER.md`。選択肢A/B/Cとの厳密な対応はFable確認)。(b)K2/M2是正はK2採用・M2→P8置換で判断済み・配線待ち(是正範囲・順序の承認自体は原文に明記なし=未回答として残す)。(c)Adv Comment1〜4 Style・(d)原稿正本は原文に言及なし=未決のまま(ただし原文§3で『Coffeeは全面新規生成・旧原稿を完成品として流用しない』ため(d)の前提は変化。Fable確認要)。#69全体のUDRはcloseしない |
| 70 | (Fable経由) **KGCPW Z E2E完成のための音声HR Lock 3 clip再生成承認**(`approve_regenerate`、約JPY5〜10): `er011_human_review_lock_01`でLock中のkp1_en(ASR TRUE_CONTENT_MISMATCH)/kp3_en(TTS_FAILURE×2)/full_story_part1_c5(ASR_VALIDATION_UNCERTAIN「Melos said.」→「Nello said.」)。gloss整合とは無関係の既存安全装置で、人間承認が必要。推奨=承認(理由: Z E2E完成evidenceが唯一の残件、費用小、gloss配線とは独立の既存安全装置) | **USER_DECISION_REQUIRED**(非ブロッキング。承認しなければZ E2E完成は未確認のまま`APPROVED_FOR_PRODUCTION`維持) | いいえ(他の生産作業はブロックしない。`PRODUCTION_WIRED`判定のみ待つ) | `er071_output/m2p0_n01_production_wiring_01/gloss_alignment_production_wiring_01/VALIDATION_WIRING_04.md` §5、OPEN-356 |
| 71 | (Fable経由) **盲検リプレイ実施方法=Fable自律起動を原則(決定①)**: Fableが隔離環境から被験セッションを起動し独立Opusが採点、ユーザーのPowerShell操作・新規セッション起動は原則要求しない。事前確認7項目(起動可否/モデル・ルーティング/課金経路・費用上限/ツール権限・委任機能/独立性/漏洩なし/Production Repo・秘密情報へ非アクセス)、既存の安全Gate・承認Gateは迂回しない | **判断済み**(2026-10-15ユーザー正式承認 決定①。実施はPhase B/C別委任・未実施) | いいえ | `day3/BLIND_REPLAY_RUNBOOK_01.md` §2、DECISION_LOG『Day3〜4 ユーザー正式決定①〜③』、OPEN-363 |
| 72 | (Fable経由) **Day5〜6移行可否**: 盲検リプレイ元基準で欠陥0/2(②見落とし2/2)、実運用有効性は部分的。Fable推奨=**保留**(欠陥②対策の規則強化→別事例での再盲検後に再判断)。移行する場合の範囲・条件もユーザー判断 | **判断済み**(2026-10-15ユーザー正式決定①、DAY3-4-CORRECTION-REBLIND-01。Day5〜6へは進まない=保留・開始禁止。是正・再盲検結果をFableが独立評価し、ユーザーが改めて移行を決定する。再盲検合格で自動開始しない。元の状態『USER_DECISION_REQUIRED[Day5〜6のみブロック]』。Day5〜6の開始判断自体は未決[保留中]) | はい(Day5〜6のみ) | `day3/BLIND_REPLAY_SCORING_01.md`、OPEN-363 【2026-10-16追記】ユーザー原文(PM-20261016-AUW-CLOSEOUT-DQI-PRODUCTION-01 _USER.md §3)『Day 5〜6の保留は維持する』。状態変更なし(判断済み・保留・開始禁止を継続)。 |
| 73 | (Fable経由) **`docs/pm/PM_BRIEF.md`:305の2026-10-08「明確なGo指示があるまで委任を一切出さない」の扱い**(撤去/範囲限定/維持)。7-9・11-6の自律運用と緊張し、盲検でセッション間の解釈が揺れた(D2,E1,E3,E4は従い、D1,D3,E2は触れず) | **判断済み**(2026-10-15ユーザー正式決定③、範囲限定を採用: 新規案件の開始=ユーザーGo必要/承認済み案件内の再委任・検証・是正・SSOT記録=Fable自律可/新仕様採用・Production採用・予算上限変更・Human Gate越え=ユーザー判断/UDR発生時=STOP/明示STOP=常に優先。反映=`docs/pm/PM_BRIEF.md`:305-306、`e9ee8dbbb`。元の状態『USER_DECISION_REQUIRED』) | いいえ | `day3/BLIND_REPLAY_SCORING_01.md` §E-3 U-a |
| 74 | (Fable経由) **11-7曖昧点の裁定**: 既定ON+Production経路無条件呼出+未実行を「受入前検出(違反でない)」と「(b)有効配線=REVOKED」のどちらで扱うか | **判断済み**(2026-10-15ユーザー正式決定④: 有効配線は実行履歴がなくても違反状態/発火も違反状態/違反はREVOKED/ただしFableが受入前に検出し直ちに差戻して採用を阻止した場合はSUSPENDEDとして裁定を求める/不明な状態を根拠なしに安全・無害と断定しない。反映=`docs/pm/PM_GOVERNANCE.md` 11-7『既定ON・未実行状態の裁定』、`e9ee8dbbb`。元の状態『USER_DECISION_REQUIRED』) | いいえ | `day3/BLIND_REPLAY_SCORING_01.md` §E-3 U-b、OPEN-365 |
| 75 | (Fable経由) **採点基準修正提案(a)〜(e)の採用**(次回再盲検用。今回結果へは遡及適用しない) | **判断済み**(2026-10-15ユーザー正式決定⑤、(a)〜(e)を次回以降の採点基準として採用・今回結果へ遡及適用しない。反映=Repo外`RUBRIC_R1_R10_v2.md`+`EXPECTED_SC_v2.md`、記録=`day3/CRB_PHASE1_APPLIED_01.md`。元の状態『USER_DECISION_REQUIRED[次回用]』) | いいえ | `day3/BLIND_REPLAY_SCORING_01.md` §E-1、OPEN-368 |
| 76 | (Fable経由) **欠陥②対策の規則強化案**: 受入記録の必須項目に「失敗終了時の最終成果物=目的要件を満たすか(ファイル:行+観測値)」を追加し、満たさなければ受入不可(既存文言は変えず様式で強制)。規則変更のためユーザー承認が必要 | **判断済み**(2026-10-15ユーザー正式決定②、受入記録の必須化[当初目的/最終成果物/証拠/一致・不一致/判定と理由、失敗終了時の最終成果物を含む]を採用。反映=`.claude/agents/sandwich-pm.md` 手順4-2、`docs/pm/PM_GOVERNANCE.md` Gate 7・9-0、テンプレ、`e9ee8dbbb`。元の状態『USER_DECISION_REQUIRED』) | いいえ | `day3/BLIND_REPLAY_SCORING_01.md` §E-3 U-e、OPEN-369 |
| 77 | (Fable経由) **再盲検不合格後の次手(a)/(b)/(c)**: 再盲検で欠陥①2/2検出・欠陥②0/2見落とし(前回同様)。(a)是正2[受入記録(1)にユーザー原文の目的・品質要件の逐語引用を必須化+承認済み設計どおりを目的適合の根拠にしない旨を4-2へ追加]→別の未使用欠陥事例で再盲検(定価換算USD 5〜10) (b)有効性『部分的』のままDay5〜6へ進み、失敗経路の受入判定を当面ユーザーが抜き取り確認 (c)運営刷新を一時停止。**Fable推奨=(a)**(原因特定済み・修正小、同一事例は学習バイアスで証明力弱) | **USER_DECISION_REQUIRED**(2026-10-15 委任_N起票。追加Trialは自律でしない) | はい(#72と連動) | `docs/research/PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01/day3/REBLIND_SCORING_01.md` §4、OPEN-363/369 |
| 78 | (Fable経由) **採点基準v2の欠陥提案(A)〜(D)の採用**: (A)陰性R3で11-7(c)該当/非該当の明示必須 (B)R11は項目単位評価 (C)R11(1)当初目的にユーザー原文の目的・品質要件引用必須 (D)見出し語は実質判定。次回再盲検用(今回結果へは遡及適用しない) | **USER_DECISION_REQUIRED**(2026-10-15 委任_N起票) | いいえ | `docs/research/PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01/day3/REBLIND_SCORING_01.md` §3、OPEN-368 |

## 区分別集計(2026-10-13更新・51件(#51追加: FAMILY-Z-PREVIEW-COMMENT1-DUAL-TRIAL-01)。#45を判断済み化[Strategy L維持・移行案REJECTED、FAMILY-Z-KP-STRATEGY-L-DECISION-CLOSEOUT-01]。#49・#50追加・#46判断済み化・#45はTrial承認済み/移行方式採用判断のみ未決[FAMILY-XZ-M2P0-N01-PRODUCTION-WIRING-01 委任_03]。#48追加[Comment参照条件Trial、USER_DECISION_REQUIRED]。#45〜#47追加[M2P0/N01 Production配線、USER_DECISION_REQUIRED]。#44追加[3 take比較、USER_DECISION_REQUIRED]。#43追加[分割Trial R1判断、USER_DECISION_REQUIRED]。#41はOpus条件A後にUSER_DECISION_REQUIRED化。#42追加[FAMILY-Z-STANDARD-PREVIEW-X-ALIGNMENT-01、USER_DECISION_REQUIRED]。#41追加[ASR-PHONETIC-EQUIVALENCE-GENERALIZATION-01、調査・Trial中]。#39・#40追加。#10は判断済みへ、#14と#23は判断保留へ、#36追加)

| 区分 | 件数 | 項目# |
|---|---|---|
| 判断済み | 18 | 2, 3, 10, 13, 17, 34, 35, 36, 37, 38, 39, 40, 45, 46, 52, 53, 54, 55 |
| 判断保留(依存事項待ち、判断時期延期) | 2 | 14, 23 |
| 調査・Trial中 | 1 | 19 |
| USER_DECISION_REQUIRED | 29 | 1, 4(暫定), 5, 7, 8, 9, 11, 12, 15, 18, 24〜33, 41, 42, 43, 44, 47, 48, 49, 50, 51 |
| Deferred / Non-blocking | 5 | 6, 16, 20, 21, 22 |
| 合計 | 55 | |

### 2026-10-15追記集計(#56〜#69。上表は#55まで未更新のため、追記のみ。上表の数値は書き換えない)
| 区分 | 件数 | 項目# |
|---|---|---|
| 判断済み | 3 | 58, 60, 62 |
| 判断不要 | 1 | 57 |
| USER_DECISION_REQUIRED | 7 | 56, 59, 61, 63, 68, 69, 70 |
| Deferred / Non-blocking | 4 | 64, 65, 66, 67 |
| 合計 | 15 | |
(上表の#1〜#55と合算した全件数は70件[2026-10-15 委任_05で#70追加]。ブロックするUDRは本追記に新規なし。表題の「#56〜#69」は#70追加後も#56〜#70を指す。)
(2026-10-15 DAY3-4-CORRECTION-REBLIND-01 委任_L: #72〜#76を『判断済み(決定①〜⑤)』へ追記更新。上表の数値は書き換えない。差分: 判断済み+5、USER_DECISION_REQUIRED-5[#72はDay5〜6の開始判断自体が未決のため、Day5〜6のみブロックの趣旨は保留として継続]。)

## 「次工程をブロックするUDR」のみ(これだけを最優先で提示する)

1. **#1 OPEN-316**: In One Line関連仕様(Comment4 Trial-03採否)。Coffee再Assembly(OPEN-321)の前提。
2. (2026-10-13更新)旧#10 Melos HR試聴は判断済み。Melos最終試聴(#23)は判断保留のためブロックUDRに含めない。

(#4 Coffee原稿正本U1/U2は根拠行を特定できず、Fableが原典を指定した場合のみ提示。#5/#7は特定の完了判定・継続に影響するが、他の作業を止めない。)

## 提示ルール(運用)

- 報告前に本表をCURRENT_SPEC/DECISION_LOG/OPEN_ITEMSと照合し、区分を更新する。
- 『判断済み』は再質問禁止。`APPROVED_FOR_PRODUCTION`を未決扱いに戻さない。
- UDRのうち『ブロックする』ものだけを提示し、Deferred/調査中は一括再提示しない。

### 2026-10-15 委任_H Phase A追記(#63/#65/#66の判断済み化・#71追加。上表の数値は書き換えず追記のみ)
- #63(U2-Q1)・#65(U3'-Q1)・#66(U5-Q1/Q2)はユーザー正式承認で**判断済み**(決定②③)。上の2026-10-15追記集計では#63=USER_DECISION_REQUIRED、#65/#66=Deferredと数えているが、本追記時点では判断済み。#71(決定①)は**判断済み**として新規追加。
- 本追記後の#56〜#71内訳: 判断済み 7(58, 60, 62, 63, 65, 66, 71)/判断不要 1(57)/USER_DECISION_REQUIRED 6(56, 59, 61, 68, 69, 70)/Deferred・Non-blocking 2(64, 67)/合計16。全件数は71件(#1〜#55との合算)。ブロックするUDRは本追記に新規なし。

### 2026-10-15 委任_K3 Phase C追記(#72〜#76追加。上表の数値は書き換えず追記のみ)
- #72〜#76はいずれも**USER_DECISION_REQUIRED**として新規追加(Phase B/C盲検リプレイ結果)。ブロックするのは#72(Day5〜6移行)のみで、他の作業は止めない。#73・#74・#75・#76は規則側の未決/次回用。
- 本追記後の#56〜#76内訳: 判断済み 7(58, 60, 62, 63, 65, 66, 71)/判断不要 1(57)/USER_DECISION_REQUIRED 11(56, 59, 61, 68, 69, 70, 72, 73, 74, 75, 76)/Deferred・Non-blocking 2(64, 67)/合計21。全件数は76件(#1〜#55との合算)。

### 2026-10-15 委任_N追記(再盲検結果。上表の既存行は書き換えず追記のみ)
- #72: 再盲検不合格(欠陥②0/2)によりDay5〜6**保留・開始禁止を継続**(判断済み状態は不変、移行判断は#77の結論後にユーザーが改めて行う)。
- #76: 規則は**反映済みだが有効性未実証**(再盲検で様式は①に発火、②には届かず)。是正2案は#77(a)。
- #77(次手a/b/c、推奨a)・#78(v2欠陥提案A〜D採用)を**USER_DECISION_REQUIRED**として新規追加。件数集計: #56〜#76の内訳に#77・#78(いずれもUSER_DECISION_REQUIRED)を加え、全件数は78件。

### 2026-10-15 委任_O OAR-02追記(#77/#78判断済み化・#79追加。上表の既存行は書き換えず追記のみ)
- #77: ユーザー決定「(a)採用(是正2+未使用事例で再盲検1ラウンド)」で**判断済み**(`DAY3-4-OBJECTIVE-ALIGNMENT-REBLIND-02`、DECISION_LOG末尾節)。(b)(c)は不採用。
- #78: ユーザー決定「(A)〜(D)採用(次回以降、遡及なし)」で**判断済み**。採点基準v3に反映済み。
- #72: **保留継続(不変)**。Day5〜6は保留・開始禁止。再盲検に合格しても自動移行しない(ユーザーの別途承認が必要)。
- #79(新規): `PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01／DAY3-4-OBJECTIVE-ALIGNMENT-REBLIND-02` 是正方針(A/B/C)。Status=`APPROVED_FOR_PRODUCTION`(是正方針)/目標`PRODUCTION_WIRED`(再盲検合格が条件。現時点は未達・再盲検未実施)。**判断済み**。出典=`docs/pm/delegation_log/2026-10-15_DAY3-4-OBJECTIVE-ALIGNMENT-REBLIND-02_USER.md`、OPEN-363/368/369。
- 本追記後の#56〜#79内訳: 判断済み 15(58, 60, 62, 63, 65, 66, 71, 72, 73, 74, 75, 76, 77, 78, 79。#72〜#76は委任_L追記で判断済み、#72はDay5〜6保留を継続)/判断不要 1(57)/USER_DECISION_REQUIRED 6(56, 59, 61, 68, 69, 70)/Deferred・Non-blocking 2(64, 67)/合計24。全件数は79件(#1〜#55との合算)。

### 2026-10-15 委任_R OAR-02 Phase C追記(再盲検結果。上表・既存行は書き換えず追記のみ)
- #79: **再盲検実施済み・Fable判定=不合格(厳格)・PRODUCTION_WIRED未達**(判断済み状態[是正方針の採用]は不変。有効性は「判定行動の改善は確認、合格条件(1)は厳格判定で未達」)。出典=`docs/research/PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01/day3/OAR2_SCORING_01.md`。
- #72: **保留継続(不変)**。Day5〜6は保留・開始禁止。
- #80(新規・USER_DECISION_REQUIRED): 本ラウンドの最終扱い(A)。選択肢=厳格判定=不合格[Fable推奨]/検出基準=合格(合格条件(1)を「(4)での検出」で読む)。
- #81(新規・USER_DECISION_REQUIRED): 次の一手(B)。(B1)是正3[受入記録(5)に反実仮想チェックと「目的不適合の成果物はユーザーへ提示・選定依頼しない」を必須化]+v3欠陥提案①〜⑥反映+ハーネスdeny拡張を行い、ユーザーが別途承認した場合のみ追加ラウンド/(B2)現状で運営刷新を部分有効と評価しDay5〜6へ(ユーザー抜き取り確認付き)/(B3)一時停止。**Fable推奨=B1**(原因が「統合」に局在し修正が小さい。追加ラウンドはユーザー承認事項で自動実行しない)。 【2026-10-16追記】#88へ統合・判断済み(ユーザー原文§2、PM-20261016-AUW-CLOSEOUT-DQI-PRODUCTION-01)。
- #82(新規・USER_DECISION_REQUIRED): v3欠陥提案①〜⑥の採用(C)。見出し語=`docs/research/PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01/day3/OAR2_SCORING_01.md`§3。
- 本追記後の#56〜#82内訳: 判断済み 15(58, 60, 62, 63, 65, 66, 71, 72, 73, 74, 75, 76, 77, 78, 79)/判断不要 1(57)/USER_DECISION_REQUIRED 9(56, 59, 61, 68, 69, 70, 80, 81, 82)/Deferred・Non-blocking 2(64, 67)/合計27。全件数は82件(#1〜#55との合算)。ブロックするのは#72(Day5〜6移行、保留継続)と#81(追加ラウンド)のみ。

### 2026-10-16 委任_07 AUW追記(`ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01` Closeout準備。上表・既存行は書き換えず追記のみ)
- 経緯: AUWは実装済み(branch `feat/auw-unified-asr-01`、`origin/main`取込済み)・main merge待ち・`PRODUCTION_WIRED`未宣言。下記#83〜#87をいずれも**USER_DECISION_REQUIRED**として新規追加。出典=`er058_output/unified_all_roles_production_wiring_01/CLOSEOUT_PLAN_07.md`、`DESIGN_02_ADDENDUM_01.md`§11、`OPEN_ITEMS.md` OPEN-370〜OPEN-380、`DECISION_LOG.md` 末尾「ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01」節。
- #83(新規・USER_DECISION_REQUIRED) **U1: JAのC1固有名詞差・類似度<0.4の不一致を、統一フロー[不一致の種類によらず原則Secondary]でSecondaryへ回してよいか**(2026-10-11承認の除外条件の扱い)。現状挙動=現行維持中(`U1_KEEP_C1_SIMILARITY_EXCLUSIONS=True`、除外のままSecondary不呼出でNG_EXCLUDED→再生成)。推奨=現行維持のまま運用し、実測で誤NGが問題になれば解放。影響=解放は`er078_asr_unified_judge_01.py:65`を1行False、Secondary費用が増える。Blocking=いいえ(merge可)。
- #84(新規・USER_DECISION_REQUIRED) **U2: LR後v1のSecondary必須化の範囲**(Primary PASSでもSecondary確認するか)。現状挙動=`A2_ONLY`暫定(`U2_FORCE_SECONDARY_SCOPE`、A2のLR後v1のみ`force_secondary=True`)。推奨=A2_ONLYを維持。影響=B1等へ広げると費用と所要時間が増える。Blocking=いいえ。
- #85(新規・USER_DECISION_REQUIRED) **U3: 「十分/10分」型AMBIGUOUSの同表層の扱い**。選択肢=(a)現行=Secondary転写が原稿と同一表層なら警告付き採用[`NUMERIC_AMBIGUOUS_SURFACE`]/(b)NG_BOTH保守[AMBIGUOUSは採用しない]/(c)Writer側で「10分」と表記する運用に寄せる。推奨=(a)現行維持+(c)の運用併用。影響=(b)は誤採用リスク最小だが再生成が増える。Blocking=いいえ。
- #86(新規・USER_DECISION_REQUIRED) **U4: 技術STOP≠HR Lockの早期return+Secondary障害時のLR抑止**(HR Lockロジック`record_outcome`冒頭への約3行の早期return追加を承認するか)。現状挙動=Secondary障害のみで最終STOPPEDのclipがLock(HUMAN_REVIEW_REQUIRED)に入り、LRまで進む(安全側、06d `tstop`・06e F5で実測)。推奨=承認する(影響clipは最大1〜2件/run、人手の不要な承認が減る)。ただしLockロジック変更のためユーザー承認なしには実施しない。Blocking=いいえ(現行挙動のままmerge可)。OPEN-371。
- #87(新規・USER_DECISION_REQUIRED) **Go: AUWを`main`へ単一merge(`git merge --no-ff feat/auw-unified-asr-01`、squash禁止)する承認**。前提=Gate 3/4/7チェックリスト・revert予行(`REVERT_REHEARSAL_07.md`:revert適用は衝突0でmain相当へ完全復元)・後方互換test 53 passed・Dangling注記済み・15条件の最終表(`CLOSEOUT_PLAN_07.md`§4:未充足=条件1・2・4・9の一部[F4/B A2 narrator実音声]・12[merge]・15[Fable独立照合])。Fable推奨=Fable独立照合(条件15)を済ませたうえでGo。影響=本番の音声ASR判定が全Family・全Sectionで統一judgeに切替わる(誤受理0を06b/06d/06eで確認済み、追加費用は中央値0.55〜0.82円/セット見込み)。Blocking=**はい**(mergeまで`PRODUCTION_WIRED`宣言不可)。
- 本追記後: 追加#83〜#87はすべてUSER_DECISION_REQUIRED。全件数は87件(#1〜#82との合算)。ブロックするのは既存の#72・#81に加え#87(merge)のみ。
- 2026-10-16 ユーザー指示(原文=`docs/pm/delegation_log/2026-10-16_AUW-FAMILY-C-DQI-USER-INSTRUCTION.md`)による更新: #87=**判断済み(Go)**、merge commit `b010cb469`。#86 U4=**判断済み(現行挙動を当面許容。Lock変更なし。OPEN-371で独立管理)**。#83 U1=**判断済み(方針): 除外は承認済み統一仕様との不整合として是正する[固有名詞差・類似度<0.4でもPrimary NGならSecondary確認、数値・否定保護と独立QAは維持]。実装は委任_09以降**。#84 U2=**調査中(A2_ONLY例外の成立経緯・必要性を確認し承認範囲内で整理。根拠なく全レベルへ拡大しない)**。#85 U3=据え置き(今回指示に言及なし。UDRのまま)。
- 2026-10-16 委任_10更新: #83 U1=**実装済み(委任_10、commit=`git log`でメッセージ冒頭『ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01 委任_10』を特定)・ただし既定は暫定True(条件付きSTOP s1: live負例対照でPrimary PASS 3件[U1と無関係]に文言上該当、Fable採否判断待ち=OPEN-392)**。範囲限定A7(登録読み保護=reading_dictionary_mismatchだけ事前除外のまま)はFable判断、ユーザー報告で明示。#84 U2=**整理済み(i)維持**(理由: 2026-08-26承認のminimal fallback誤PASS事故対策、LR固有ではない、拡大根拠なし。死定数撤去・呼出点は静的testで1箇所固定)。
- 2026-10-16 委任_11更新: #83 U1=**実装・発効(委任_11、本commit(メッセージ冒頭『ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01 委任_11』を`git log`で特定))。範囲限定A7=登録読み保護**(Fable判断でs1非該当、`U1_KEEP_C1_SIMILARITY_EXCLUSIONS=False`)。除外として残る: A1/A2(数値・否定)・A3(length。是正は条件付きSTOP s4で保留=OPEN-388)・A4(C2同形異音)・A7(登録読み辞書不一致)。ロールバックは同定数を1行`True`へ。Primary層の弱点(誤文面TTSの原稿どおりPASS)は独立問題OPEN-394として**ユーザー判断事項**。`PRODUCTION_WIRED`は未宣言。

### 2026-10-16 09:00 JST ユーザー最終判断の追記(`FAMILY-X-20261016-0900-USER-DECISION-RECORD-01`。上表・既存行の数値は書き換えず追記のみ)
- 原文=`docs/pm/delegation_log/2026-10-16_FAMILY-X-20261016-0900-USER-DECISION-RECORD-01_USER.md`。正本=CURRENT_SPEC「Family X 最終ユーザー判断(2026-10-16 09:00 JST…)」、DECISION_LOG同ID。対象=Family X全体(Family Zへの自動展開は対象外)。以下8仕様は**判断済み**で再質問しない。ただし**配線Statusが異なる**ため区別する。
- 区分=判断済み・未配線/配線Status:

| # | 仕様 | 区分 | 配線Status | 備考 |
|---|---|---|---|---|
| FXUD-1 | B3・日本語Writer R0→R1→R2 すべて`gpt-6.1-sol` | 判断済み | **`PRODUCTION_WIRED`維持**(実装・runtime証拠との整合はFXWA 01A監査中) | 既存 |
| FXUD-2 | Full Story TTS(Std/Adv)=PD06 | 判断済み | `APPROVED_FOR_PRODUCTION`・未配線(配線状況は未確認) | 正本=`er057_output/pace_trial_02/prompts/prompts_pace_02.md:74-82`(PD6) |
| FXUD-3 | KP英語音声(Std/Adv)=K2 | 判断済み | `APPROVED_FOR_PRODUCTION`・未配線(配線状況は未確認) | 正本=`er057_tone_trial_kp_ja_gen_01.py:38-39`+B_GUARD`:33` |
| FXUD-4 | KP日本語意味(Std)=P8(旧M2置換)。#68を判断済み化 | 判断済み | `APPROVED_FOR_PRODUCTION`・未配線 | 正本=`er057_std_kp_ja_style_trial_02.py:25` |
| FXUD-5 | KP英語解説(Adv)=P7(旧P3置換)。#3を更新 | 判断済み | `APPROVED_FOR_PRODUCTION`・未配線 | 正本=`er080_coffee_kp_pacing_trial_01.py:35`(同名別P7あり、Fable確認要) |
| FXUD-6 | KP候補供給=M2P0 | 判断済み | `APPROVED_FOR_PRODUCTION`(2026-10-13決定の維持)。配線StatusはCURRENT_SPEC「Key Phrase」節の記載に従う | |
| FXUD-7 | KP選定優先順位=A方式(現行)、B/C方式不採用 | 判断済み | `APPROVED_FOR_PRODUCTION`(現行維持のため配線差分なしの見込みだが未確認) | `FAMILY-X-KP-IDIOM-PRIORITY-ABC-TRIAL-01` |
| FXUD-8 | In One Line(Std/Adv)=基本2文(必要時3文)、旧1文Prompt改修 | 判断済み | `APPROVED_FOR_PRODUCTION`・未配線(改修Prompt未作成=正本未特定) | #69(a)を判断済み化 |

- Coffee制作の前提: Researchから音声完成まで全面新規生成(旧Coffee原稿・KP・音声は流用しない)。再生成はFXWA監査・Production Wiring完了後、別途指示。
- 件数: 追加FXUD-1〜FXUD-8(並行委任との番号衝突回避のため連番#ではなくFXUD-N。本表の連番への正式採番はFableが行う)はすべて『判断済み』。既存の判断済み化は#68(全面)・#3(更新)・#69(a/b一部)。USER_DECISION_REQUIRED(#69の(b)是正範囲承認・(c)・(d))は残る。close 0件。

### 2026-10-16 委任_14 AUW Closeout追記(Fable独立照合[条件15]=`PRODUCTION_WIRED`判定の記録。既存行は書き換えず追記のみ)
- **Fable判定: `PRODUCTION_WIRED`(2026-10-16)**。出典=`er058_output/unified_all_roles_production_wiring_01/CLOSEOUT_PLAN_07.md`§4-e。
- #83=**判断済み・実装・発効**(U1: `U1_KEEP_C1_SIMILARITY_EXCLUSIONS = False`、委任_11。付帯=A7登録読み保護は維持、新規UDR #95)。#84=**判断済み・整理済み**(U2: (i)維持、死定数撤去)。#86=**判断済み**(U4: 現行許容、OPEN-371で独立管理)。#87=**判断済み**(Go・merge済み、`b010cb469`)。#85(U3)は本追記では判断状態を変更しない(UDRのまま)。
- #88(新規・USER_DECISION_REQUIRED) **DQI改善パッケージP(PM判断品質改善の規則文変更)の採用可否** 原文=`docs/research/PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01/dqi/DQI_PROPOSAL_01.md`§3・§7(1)。sandwich-pm.md/PM_GOVERNANCE/templatesの規則文変更=運用仕様の変更のため、ユーザー判断なしに適用しない。推奨=採用。理由=AUW #83〜#86型の『Sonnet草案がUDR化する/承認原文との不整合が見逃される』問題の再発防止(Opus Q1〜Q7を反映済み)。影響=PM層の運用負荷は条件付き展開・1行集約で最小化。 Blocking=いいえ。
- #89(新規・USER_DECISION_REQUIRED) **重大NG 2軸定義の承認(パッケージPの一部)** 原文=`docs/research/PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01/dqi/DQI_PROPOSAL_01.md`§3・§7(2)・§9(#4,#5)。重大NGの定義を2軸(例示・過剰STOP歯止め付き)で固定。推奨=承認(Pの1項目として)。理由=ユーザーC-2提案①の文言が出所、D-9と整合。影響=成果物の無条件ACCEPTEDを防ぐ。 Blocking=いいえ。
- #90(新規・USER_DECISION_REQUIRED) **遡及机上チェック(代替案(c))の実施可否** 原文=`docs/research/PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01/dqi/DQI_PROPOSAL_01.md`§4(c)・§7(3)。過去判断を机上で遡及点検する案。推奨=実施(JPY0、検証力は低いと明記)。影響=費用なし、新規API呼出なし。 Blocking=いいえ。
- #91(新規・USER_DECISION_REQUIRED) **問題1の実例確認(非ブロッキング確認)** 原文=`docs/research/PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01/dqi/DQI_PROPOSAL_01.md`§7(4)。ユーザーが問題1として念頭に置く実例はAUW #83〜#86か、他か。推奨=#83〜#86と仮定して進行し、異なる場合のみユーザーが訂正。影響=提案書の根拠事例の確定のみ。 Blocking=いいえ。
- #92(新規・USER_DECISION_REQUIRED) **Family C 承認済み音声の再利用保証(OPEN-385案1 wav sha256固定マニフェスト + OPEN-387 story_001コロン)** OPEN-385(承認済みTrial-11 Memory A2の9clipの出自をリポジトリ内で証明できない)とOPEN-387(story_001本文中コロンがGateで再生成をブロック)。推奨=案1(wav sha256固定マニフェスト)を採用。理由=原稿不変で両方を解決できる。影響=Family Cの承認済み音声が再利用でき、再生成費用が発生しない。Family C全体のStatusは不変。 Blocking=いいえ。
- #93(新規・USER_DECISION_REQUIRED) **OPEN-394 Primary層の弱点(誤った文面でTTSした音声が原稿どおりPASSする)=仕様候補** OPEN-394(ガス→カス、Metaの綴り読み等)。仕様候補のためユーザー判断事項。推奨=次回Trial設計時に扱う(今は観察のみ、Production挙動は変更しない)。影響=現行Productionは不変。 Blocking=いいえ。
- #94(新規・USER_DECISION_REQUIRED) **OPEN-395 JA Latin語web lookup費用(1回JPY21.47)の量産単価への影響評価と対処方針** OPEN-395(`er025`内蔵`ja_web_lookup_call`、AKB48/ishで1回JPY21.4688)。推奨=negative cache/Ledger保存の有無調査を先行(JPY0、コード読みのみ)してから対処方針を提示。影響=量産単価目標70円/記事セットに対する影響の有無を確定。 Blocking=いいえ。
- #95(新規・USER_DECISION_REQUIRED) **A7範囲限定(登録読み辞書不一致のみSecondary事前除外)の是非** #83付帯。A7はSecondary事前除外として維持(Fable判断、2026-10-11安全条件の適用。`er078_asr_unified_judge_01.py:125/:148`)。推奨=維持(既定は維持のまま、ユーザーが異議あれば除外表1行で解放)。影響=解放すると登録読み辞書不一致でもSecondaryへ回る。 Blocking=いいえ。
- 本追記後: 追加#88〜#95はすべてUSER_DECISION_REQUIRED(非ブロッキング)。全件数は95件(#1〜#87との合算)。#87は判断済みへ確定したため、ブロックするのは既存の#72・#81のみ。

### FXWA監査 Fable最終(2026-10-16、FAMILY-X-WRITER-TRIAL-ADOPTION-AND-PRODUCTION-GAP-AUDIT-01 委任_03、Opus FXWA-R-01〜12全件採用)

原文・詳細=`docs/research/FAMILY-X-WRITER-TRIAL-ADOPTION-AND-PRODUCTION-GAP-AUDIT-01/AUDIT_REPORT_01.md`§14。全件`USER_DECISION_REQUIRED`。(d)英語化モデルと(e)AN3第1文置換、P1-3(R0規則7)はUDRにしない((d)=独立改善候補C、(e)(P1-3)=承認Trialと同一でA)。

- #96(新規・USER_DECISION_REQUIRED) **(a)+(b)P7の正本とPD06の名称対応(Yes/No 1問)** 「P7=`er080_coffee_kp_pacing_trial_01.py:35`のp7(速度・リズムのバランス型)」「PD06=Pace Trial-02の`PD6`」で追認するか。推奨=追認。理由=同名の別P7がCS:1239に実在し、FX記録§3が要確認と自記。er080側はユーザー指示原文と逐語一致。PD06表記は09:00文書以外に無い。影響=KP英語解説(Adv)とFull Story TTS(Std/Adv)の全記事。 Blocking=はい(配線前)。
- #97(新規・USER_DECISION_REQUIRED) **(c)In One Line 2文Promptの文面承認(基本2文・必要時のみ3文の基準を含む)** 推奨=配線設計時に文面案+offline出力サンプル少数を添え、1回で承認。理由=改修自体は判断済みで、承認が要るのは文面と「必要時3文」の基準のみ。影響=全記事のIn One Line(Adv生成・Std継承・Local Rewrite経路)。 Blocking=はい(設計後)。
- #98(新規・USER_DECISION_REQUIRED) **(g)Hook Side output(R2完成後にLunaでHook1本)の扱い** 推奨=廃止(R2 Title表示のみ維持)。理由=現Family X runnerにstageが無く、比較観測用で品質に直結しない。後続仕様で失われた過去決定に該当するため廃止にはユーザー判断が要る。影響=比較観測の継続可否のみ。 Blocking=いいえ。
- #99(新規・USER_DECISION_REQUIRED) **(h)+(f)一括整理**: OPEN-237系・RF候補(a)(b)(c)・代理指標・Pre-sorter・OPEN-243(守り撤去後の継続/close)。補完sweepで判明したOPEN-56/59(Evidence Compression B版、旧B1/A2 Writer Prompt対象、PRE_USER_VALIDATION)も候補に追加。推奨=報告書§3のとおり一括提示(継続/廃止)。理由=個別に問い直すより一括整理が現実的。影響=OI整理のみ。 Blocking=いいえ。
- #100(新規・USER_DECISION_REQUIRED) **E1/R2のFamily X既定化** E1(Adv Preview音声Style)とR2(Std日本語Preview/Comment音声Style)を、Coffee限定承認(OPEN-298/300)からFamily X全体の既定へ拡げるか。推奨=既定化(ただしユーザー原文に無いため要確認)。理由=09:00の表にE1・R2は無く、CS:1244の拡大文は記録者の解釈。要約で承認範囲を拡げない。影響=Family X共通仕様の完成・取り違え防止。 Blocking=いいえ(Coffee再制作はCoffee限定承認のまま可)。
- 備考: FXUD-1〜8は「判断済み・未配線」のまま。配線Blocking最終版=`docs/research/FAMILY-X-WRITER-TRIAL-ADOPTION-AND-PRODUCTION-GAP-AUDIT-01/AUDIT_REPORT_01.md`§14-6(IOL 2文化[Prompt承認→Adv/Std/Local Rewriteラベル改修/文数保持test]/PD06・K2・P8・P7配線[Master Store新style id・version、P8名称衝突回避]/既定profile化[4仕様のみ]/OPEN-343 triage/実走Gate項目)。Std 6%減速併用の既定慣行採用・PD06等の既定profile化はFable判断(B)。
- 本追記後: 追加#96〜#100はすべてUSER_DECISION_REQUIRED。ブロックするのは#96・#97(配線前/設計後)と既存の#72・#81。全件数は100件。

### 2026-10-16 FXPW 委任_01 判断反映(`FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01`、ユーザー正式指示。#96〜#100を判断済みへ。既存行は書き換えず追記のみ)

原文(全文)=`docs/pm/delegation_log/2026-10-16_FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01_USER.md`。全件ユーザー本人の原文に基づく(Fableの推奨による代理判断ではない)。

- #96 **判断済み(Yes)**: P7の正本=`er080_coffee_kp_pacing_trial_01.py`のp7、PD06=Pace Trial-02の`PD6`。原文『P7＝`er080_coffee_kp_pacing_trial_01.py`のp7』『PD06＝`er057_output/pace_trial_02/prompts/prompts_pace_02.md`のPD6』(併せて表『Full Story TTS（Std／Adv） | **PD06**：聞き手への語りかけ＋落ち着き』『KP英語解説（Adv） | **P7**：速度・リズムのバランス型。旧P3を置換』)。
- #97 **ユーザー承認不要・設計して報告(判断済み)**: In One Line 2文Prompt文面の承認は不要。原文『具体的Prompt文面と3文にする基準は設計して報告する。これは既存承認仕様の実装であり、文数方針を再度Trialに戻さない。』『ただし、新しい編集方針を追加する必要が生じた場合は、ユーザー判断を要する。』設計案=`docs/research/FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01/WIRING_DESIGN_01.md`§C(新編集方針が必要と判断した箇所なし、Fable確認事項3点)。
- #98 **判断済み=廃止**: Hook Side Output。原文『Hook Side Output | **廃止**。R2 Titleを正式表示する仕様は維持』『Hook Side Outputはユーザー正式判断により廃止し、OPEN-176等を更新する。』
- #99 **判断済み=今回は個別採否を行わず、A/B/C分類でSSOT記録。Aはdeferred**: 原文『今回、ユーザーは**個別の採否判断を行わない**と明示した。』『したがって、Aはdeferredとして管理し、今回のProduction作業を妨げない。ただし、勝手に採用・不採用へ変更しない。』『この整理のための追加Trial・個別質問は禁止。』分類結果=`docs/research/FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01/VALIDATED_TRIAGE_01.md`(A=3[OPEN-56/59、OPEN-243 M1(b)、OPEN-316(c)]/B=12/C=11)。
- #100 **判断済み=採用**: E1/R2のFamily X既定化。原文『Advanced Preview音声 | **E1**』『Standard日本語Preview／Comment音声 | **R2**』『**適用範囲：Family X全体。Family Z等への拡大は対象外。**』
- 備考(FXUD-1〜FXUD-8): Status『判断済み・未配線』を維持。本管理ID`FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01`で配線する(設計=`docs/research/FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01/WIRING_DESIGN_01.md`、Opus条件Aレビュー前)。付随判断: 『Standard Full Storyの既存6%減速は維持し、PD06との併用を実証する。』
- 本追記後: #96〜#100はすべて判断済み。ブロックするのは既存の#72・#81のみ(#96・#97のBlockingは解消)。新規USER_DECISION_REQUIRED=0件(`docs/research/FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01/SPEC_WIRING_MATRIX_01.md`§3)。
- 2026-10-16 ユーザー指示(`PM-20261016-AUW-CLOSEOUT-DQI-PRODUCTION-01`、原文=`docs/pm/delegation_log/2026-10-16_PM-20261016-AUW-CLOSEOUT-DQI-PRODUCTION-01_USER.md`)による更新(既存行は不変、以下が現行):
- #88=**判断済み=採用**(DQIパッケージP): 原文§2『ユーザーはDQIパッケージPを正式採用した。』『Status：`APPROVED_FOR_PRODUCTION`』。#89=**判断済み=採用**(重大NG 2軸定義): 原文§2『ユーザーはパッケージPを承認しており、この定義もその構成要素として扱う。別途承認を求めない。』。#90=**判断済み=採用**(遡及机上チェック): 原文§3 Phase 2『まず既存のDay 3・4の失敗事例など、利用可能な記録で無課金検証する。』『その結果は、既知の正解を使った机上評価と明示する。』。#91=**判断済み(Fable読み取り)**(問題1の実例確認): 原文§3『まず既存のDay 3・4の失敗事例など、利用可能な記録で無課金検証する。』に従い、本日の実例(AUW #83〜#86、FXWA、FCJ)を机上評価に含めて処理(`DQI_DESK_EVAL_01.md`)。ユーザーからの追加の実例指定なし。#80〜#82(Day3 再盲検の最終扱い・次の一手・v3欠陥提案)は#88〜#91へ統合済みとして同扱い(Fable読み取り、原文§2・§3)。
- #85(U3 AMBIGUOUS同表層)・#93(OPEN-394)・#94(OPEN-395)・#95(A7範囲限定)=**記録のみ(判断要求を再発行しない)**(Fable読み取り。ユーザー原文に#番号の明示なし): 原文§1-A『承認済みAUWの再Trial・再実装・追加改修は行わない。』『**AUW本体は完了。** 別の改善候補を理由にStatusを後退させない。』§7『ユーザーが明示的に保留した非Blocking事項は、判断要求を再発行せず記録のみ維持する。』
- #92(Family C 再利用保証 OPEN-385/387)=**判断不要・作業禁止**(Family C開発停止): 原文§1-C『Family A・B・Cは開発停止とする。』。OPEN-385/386/387は凍結(closeではない)。
- AUW=**`PRODUCTION_WIRED`ユーザー正式承認**(新規UDRではなく記録): 原文§1-A『**ユーザーが`PRODUCTION_WIRED`を正式承認。**』。#83・#84・#86・#87の既存「判断済み」は不変。
- 本追記後: 本管理IDによる新規USER_DECISION_REQUIREDは0件。#80〜#95のUSER_DECISION_REQUIRED残は0件。ブロックする既存UDR(#72等)の現状はFableがREGISTER本体で照合して確定する(本委任ではREGISTER編集禁止のため#72・#81の最終状態を未確認。#81は#88〜#91へ統合として扱う)。
- 2026-10-16 FXPW 委任_04: FXUD-1〜FXUD-8の備考=配線実装済み(本commit=メッセージ冒頭『FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01 委任_02A/02B/04』)・runtime evidence(Coffee正式実走)待ち。`PRODUCTION_WIRED`ではない。#97=設計報告済み(Prompt全文=`docs/research/FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01/WIRING_DESIGN_01.md`§K-1、ユーザー承認不要)。#98(Hook Side Output廃止)=コードにHook stage無し・SSOT反映済み。新規USER_DECISION_REQUIRED=0件(判断候補: Coffee実走の費用承認=見積最悪約162円>100円、7-7)。
- 2026-10-16 CEC 委任_05(新規UDRなし・判断済み記録): (1)Coffee E2E費用承認=原文§3『**今回のユーザー承認上限：205円。**』『この金額はCoffee E2Eに限定し、追加Trialや他案件へ流用しない。』(7-7の費用承認として判断済み)。(2)K2代替音声=原文§4『**この問題はCoffee制作から切り分け、Open Itemとして管理する。**』『**今回、K2 fallbackの改修や追加Trialは行わない。**』→OPEN-399(非Blocking・ユーザー明示deferred、再質問しない)。(3)DQI=原文§5『**今後の実際の受入案件10件について、DQIの効果を測定する。**』→`DQI_PROSPECTIVE_OBS_01.md`。(4)Day 5・6=原文§6『**PM自律運営モデルのDay 5・6は保留を維持する。**』。いずれも判断済みとして扱い、再質問しない。

- 2026-10-16 FXPW 委任_06: 判断済み追記=Coffee run_fxpw_01のMandatory STOP解除・音声化進行(ユーザー正式承認、原文=`docs/pm/delegation_log/2026-10-16_FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01_AUDIO-RESUME_USER.md`、Coffee E2E上限JPY205内)。FXUD-1〜FXUD-8の「runtime evidence待ち」を証拠で更新: FXUD-1(Sol B3/R0/R1/R2)=`er019_output/coffee_prices/run_fxpw_01/ja_writer/runtime_evidence.json`・`storyline_b3/runtime_evidence.json`(委任_05)、FXUD-2〜7(PD06/K2/P8/P7/E1/R2)=`er019_output/family_x_audio_production_wiring_01/coffee_prices__run_fxpw_01/audit/e2e_segment_style_table.json`・`er019_output/family_x_audio_production_wiring_01/coffee_prices__run_fxpw_01/audit/style_profile.json`、FXUD-8(IOL 2文)=`er019_output/coffee_prices/run_fxpw_01/writer_run_summary.json`+各level `parts.json` in_one_line。実走結果は証拠記録のみ。`PRODUCTION_WIRED`判定はFable待ち、ユーザー試聴は未。

- 2026-10-16 FXPW 委任_07: FXUD-1〜FXUD-8のStatus=配線実装済み・runtime evidence取得済み・**PRODUCTION_WIRED(Fable判定2026-10-16)**(旧『判断済み・未配線』『配線実装済み・runtime evidence待ち』の記述は履歴として保持。判定本文=`CURRENT_SPEC.md`同日Fable判定行)。
- 未回答報告(2026-10-16 FXPW 委任_07、新規UDRではない・既定次工程): Coffee run_fxpw_01 `USER_LISTENING_PENDING`。試聴ページ=https://shimomura055.github.io/eigo-radio/user_test/coffee_fxpw_e2e_01/index.html (#std/#adv)。重点確認=Std Full Story体感速度(PD06+6%減速)/Adv Full Story速度/K2語頭語尾/P8日本語意味/P7英語解説/PASS_WITH_WARNING 3件(Adv KP3英語・KP3解説・KP5解説)。ユーザー試聴評価は未実施でありPASS扱いしない。

### 2026-10-16 RLCO 委任_02追記(`FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-ANALYSIS-01`、UDR deferred・非Blocking。既存行は書き換えず追記のみ)

- #101(新規・UDR deferred・非Blocking) 案1(Fact単位探索上限+出典ロケータ引継ぎ)を検証Trialへ進めるか — D区分、推奨=Fable所見は報告で提示、Trial約JPY150〜200(出典=docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-ANALYSIS-01/ANALYSIS_REPORT_01.md §9、OPEN-403)。 [2026-10-17 ユーザー指示でTrial方針承認(金額は別途承認)]
- #102(新規・UDR deferred・非Blocking) 案2(Select-then-Verify)を検証Trial・設計へ進めるか — D区分、構造変更、Trial約JPY55〜60+実装別途+Opus条件A(11-3)。出典=同上、OPEN-403。 [2026-10-17 ユーザー指示でTrial方針承認(金額は別途承認)]
- #104(新規・UDR-blocking) RLCT有料実行の費用承認【2026-10-17 委任_03で見積v2へ更新】 — 必須(Stage 1)=期待約JPY502.6/上限約JPY986.3(M0'をStage 1へ追加、inbound再選定p=1、技術retry余裕込み。v1は期待376〜443/上限860)。段階実行案X=1a Coffee+inbound[期待267.6/上限493.0、冒頭にCoffee M2 smoke]→1b streaming→openai→central[期待235.0/上限493.3]、1a→1b進行条件あり。条件付き: Stage 2 openai/central M0'(M1呼出ログで上限が拘束した場合のみ)16.4/18.8。任意(選択肢、必須に混ぜない): A故障注入プローブ(3記事)32.7/54.3、B M2初回B3追加(Coffee/inbound)23.0/27.6、C Stage 3 RF比較(W-1なし)4.3/6.4。>JPY100のため7-7によりユーザー承認なしでは有料実行不可。日次1,000円: 本日使用済み約44.6、期待は枠内、上限986.3は合計約1,030.9で約30.9超過(1a/1b別日または実費ガードで担保)。D区分。Opus条件Aレビュー実施済み(設計v2に反映)。出典=docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01/COST_ESTIMATE_02.md、OPEN-403。

### 2026-10-17 SJS4 委任_01追記(`FAMILY-X-COFFEE-STANDARD-JA-SUPPORT-CALM-STYLE-TRIAL-04`、既存行は書き換えず追記のみ)

- #103(新規・未回答報告・ユーザー試聴待ち) Std日本語解説(Preview/Comment1〜4)Style選定(試聴後) — 基準P2/R2+S1〜S8を各2 Takeで比較、2 Takeとも許容範囲か確認の上で選定。試聴ページ=https://shimomura055.github.io/eigo-radio/user_test/coffee_ja_style_trial_04/index.html。選定後に別タスクでProduction反映(OPEN-404)。


### 2026-10-17 S3W 委任_02追記(`FAMILY-X-STD-JA-S3-ADOPTION-AND-WIRING-01`、既存行は書き換えず追記のみ)

- #103(判断済み: S3選定、2026-10-17) Std日本語解説(Preview/Comment1〜4)Styleとして S3 を選定(原文=docs/pm/delegation_log/2026-10-17_FAMILY-X-STD-JA-S3-ADOPTION-AND-WIRING-01_USER.md)。
- #105(新規・UDR-blocking・Phase B開始条件) S3をFamily X Std日本語解説の正式Styleとして採用するか(S3版試聴後) — D区分。S3版試聴ページ=https://shimomura055.github.io/eigo-radio/user_test/coffee_fxpw_e2e_01_s3/index.html(R2版と並列再生可)。採用時のみPhase B(Production配線)へ進む。Production不変・未承認。

- #105(判断済み: S3を正式採用、2026-10-17) S3をFamily X全体のStd日本語解説(Preview/Comment1〜4)の正式Styleとして採用(APPROVED_FOR_PRODUCTION、旧R2)。原文=docs/pm/delegation_log/2026-10-17_FAMILY-X-STD-JA-S3-ADOPTION-AND-WIRING-01_PHASE-B_USER.md(sha256 2d79e61fd8dfc788168972f7ed906dd0fc7fdfd2e38ebc71f080bebdde010cec)。Phase B(委任_03)でProduction既定profile fx_20261017へ配線(コード・test済み、runtime evidence待ち)。PRODUCTION_WIRED判定はFable。

### 2026-10-17 S3W 委任_05 / RLCT 委任_05 / BAPE 委任_02追記(既存行は書き換えず追記のみ)

- #105(判断済み+PRODUCTION_WIRED、2026-10-17 Fable判定) S3をFamily X Std日本語解説の正式Styleとして採用。Phase B配線・正式経路runtime evidenceをFableが受入。
- #105(試聴PASS 2026-10-17) Coffee S3正式版ユーザー試聴PASS、USER_LISTENING_PENDING close。
- #104(判断済み: 承認(b)+任意A、2026-10-17) RLCT有料実行の費用承認。累計上限JPY1,040、Stage 1a上限493。原文=docs/pm/delegation_log/2026-10-17_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01_APPROVAL_USER.md(sha256 b04eb8e1…)。
- #106(新規・UDR-blocking・未回答) BAPE(FAMILY-X-BOREDOM-AGGRESSION-PRODUCTION-E2E-01)の費用上限(180円案)承認(7-7)。OPEN-408。回答まで有料実行は開始しない。
- #106(判断済み 2026-10-17) BAPE E2E費用上限JPY180承認(期待約95、当該記事限定・別Trial流用不可)。原文=2026-10-17_FAMILY-X-BOREDOM-AGGRESSION-PRODUCTION-E2E-01_COST-APPROVAL-S3-PASS_USER.md。
- #107(判断済み 2026-10-17) RLCT Stage 1b前の案2設計: 選択肢(b)最終B3確認パス追加を正式承認。Trial設計是正でありProduction採用ではない。原文=docs/pm/delegation_log/2026-10-17_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01_DESIGN-FIX-1B_USER.md(sha256 835f6972fde54f298a11b631446058750ac7e15be7b07affd2f23b22988a2cdb)。TRIAL_DESIGN_03.md。OPEN-410。
- 未回答報告: なし(Coffee S3正式版はユーザー試聴PASSでclose、2026-10-17)。旧記載=Coffee S3正式版 試聴 https://shimomura055.github.io/eigo-radio/user_test/coffee_fxpw_e2e_01_s3prod/index.html
- #48/#51(判断済み 2026-10-17 §2A) Family Z Preview/Comment 1の方式: 現行方式を維持、A/B Trialの新方式は不採用、Preview改善の追加Trialは行わない(#42/#44も同決定で整理)。OPEN-338 CLOSED。原文=docs/pm/delegation_log/2026-10-17_FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01_COMPLETION-AND-CROSS-FAMILY_USER.md。#23(Melos最終試聴・受入判断)は本決定と区別し判断保留のまま、新しい正式試聴ページ完成時に提示する。
- #108(新規・UDR-blocking・未回答) Family Z Melos完成の追加費用: 別枠JPY100案(期待約45、再生成見積35〜50・最大約67)。¥300枠(CURRENT_SPEC.md:1608)の残(ledger基準66.5/KGCPW Z・AUW算入で約21)では今回のPD06/S3等の再生成に不足の見込み。回答まで有料実行なし。OPEN-412。
- #109(新規・UDR-blocking・未回答) Source Reference ContractのFamily Z(Strategy L、shortlistなし)適用方式: D1事後決定論ID付与[prompt無変更・KP再利用可]/D2 promptへ文ID付与・LLMがID返却[契約に忠実・KP再選定要]/D3 Opusレビュー_Cの第3案。Fable推奨はOpus_C受領後に確定(暫定D1)。OPEN-412。
