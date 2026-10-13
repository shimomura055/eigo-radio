# M1_WIRING_DESIGN_01 M1(連結発音におけるASR表記揺れの発音同等性判定)のProduction配線設計

到達上限Status: `WIRING_DESIGN_DRAFT(Opus条件A/C待ち)`。Production code無変更。`PRODUCTION_WIRED`ではない。
前提: ユーザー正式決定(M1/F1=`APPROVED_FOR_PRODUCTION`)。上流設計=ER-068 DESIGN_DRAFT_02(`er068_asr_phonetic_equivalence_generalization_01_offline.py` の `m1_try`/`design_judge`、Opus条件A必須修正1〜4反映版)。
**重要**: OOV(CMU未収録語)の扱いは承認範囲外の可能性が高く、`OOV_SAFETY_01.md` 参照。本設計はOOV部分を「承認がない限り移行しない(選択肢i)」を既定とし、承認後に差替え可能な形で記す。

## 1. 配置(1か所に集約し全経路へ効かせる)
- 新関数(案): `er0XX_asr_phonetic_equivalence_m1_production_01.py::m1_try_production(canonical, asr_text, cls, ...)`(ER-068のロジックを無変更移植+下記ガード。**Trial scriptのimportは禁止、Production専用moduleへ移植**)。
- 呼出位置: `er006_secondary_asr_01.py::evaluate_attempt_with_cascade_detail` の **Primary#1判定(`val.evaluate_attempt`)の直後、`cascade_eligible` early return(L726〜)より前、Tier3(Azure corroboration)より前**。
  - 理由: `ASR_VALIDATION_UNCERTAIN`(固有名詞/同音語のみの差)は `cascade_eligible` では扱われる/扱われないが、early returnより後ろでは到達しない分岐が出る。前に置けば全経路が1回の分岐で網羅できる。
- 追加の適用点: Primary#2(P2)/Secondary#1(S1)/Secondary#2(S2)の各判定直後(L764/L795/L826付近)にも同じ関数を適用(ASR転写が変わるため)。
- 減速後: `_post_slowdown_cascade_rescue`(`er003_v1_n3_01_tts_generate.py` L146)と減速後再検証(L196)は同じdetail関数を呼ぶため**追加配線不要**(自動で効く。実行証拠はEVIDENCE_PLAN_01)。

## 2. 適用条件(狭く保つ)
| 項目 | 設計 |
|---|---|
| 対象判定 | Primary/各stepの `classification == ASR_VALIDATION_UNCERTAIN` かつ `protected_check` 通過(数字/否定不一致は対象外)の場合のみ。`TRUE_CONTENT_MISMATCH`(内容語の差)は対象外(Eq Layerの別問題として混ぜない) |
| 言語・種別 | en-US narration/dialogueのみ。日本語・KP・他言語は対象外 |
| `segment_id` | **非依存**(dialogue/point_headings_aoedeが `segment_id` 未渡しでも効く。F1のrole gatingとは独立) |
| 判定の根拠 | **辞書駆動のみ**: ASRトークンとcanonical語のCMU音素列(確認済み発音)が一致すること。固有名詞のallow-list・綴り近似は不可 |
| 受理理由の限定 | 置換後の文を既存判定へ流し、受理理由が `EXACT_MATCH`/`NORMALIZED_MATCH`/`CONNECTED_SPEECH_ACCEPT`/`CONNECTED_SPEECH_PASS_WITH_WARNING`/`CONNECTED_SPEECH_RESEGMENTATION` の場合のみ(`HIGH_SIMILARITY_SAFE`/`NUMERIC_EQUIVALENCE_MATCH`/`HOMOPHONE_EQUIVALENT`等での受理は不可) |
| 固有名詞らしき差 | 保守基準(CMU代表発音同士の一致のみ。`entity_word_arpabet_primary_match`と同じ)。固有名詞への `HOMOPHONE_EQUIVALENT` 経路受理は根拠にしない(F2) |
| 所有格 | `Mello's` → `Mellos` へ `'s`→`s` 正規化(ASR/canonical両方に同関数)。正規化したことをaudit trailに記録 |
| 結果 | 常に **PASS_WITH_WARNING**(ブロッキングしないが警告を残す)。audit trail必須 |
| F1 | M1が表記を正規化した後も、`F1_FIX_DESIGN_01.md` の全差分検証を適用(置換トークン以外の残差があれば不受理) |

## 3. fallback / HR との関係
- fallback(`force_secondary=True`)およびLR後再検証: M1は Primary 判定だけで確定せず、**Secondary ASR同意必須**(Primary・Secondary双方の転写を独立にM1へ通し、両方が同じcanonical語への同音綴りと判定される場合のみ受理)。片方のみの場合は既存どおりHR/retryへ。
- M1が不受理のとき: 判定を変えない(既存のretry/fallback/HR上限をそのまま維持。上限回数・Gateの緩和なし)。
- M2(音素説明付きHR候補への分類)はEquivalence Layer領域に近く本委任の承認範囲外。**M1とは独立**とし、本設計では実装対象にしない(記録のみ)。

## 4. audit trail(監査・追跡可能性)
`cls.connected_speech_info` と attempt/telemetry の `m1` サブオブジェクトに記録: `original_asr`(原文のASR転写)/`normalized_asr`/`subs`(from, to, 根拠=`phoneme`, 規則=`exact`/`drop_final_S_or_Z`/`drop_ed`/`add_s`, canonical語)/`variant_classification`/`possessive_normalized`/`layer_invoked`(到達・実行証拠用)/`segment_id`(あれば)/`engine`。`oov_*` 根拠は **記録しない=使えない**(OOV不採用のため。承認された場合のみ `basis` に追加)。
OPEN-328の観測性(connected_speech_enabled実値・layer_invoked)は **M1のログに限り** 同時に残す(Fable判断で別Open Itemと統合)。

## 5. 依存・孤立チェック(Dangling Reference Check)
- 新module名をProduction codeから参照する場合、DECISION_LOG/CURRENT_SPECに正式仕様(承認済みM1の範囲)を記載した後に配線する(委任_03がSSOT担当)。
- 初回・retry・fallback・減速後・dialogue・point_headings_aoedeの全てから同じ関数を経由すること(上表)。孤立候補なし。
- Trial専用の `er068_*` / `er065_*` はProductionからimportしない。

## 6. 非対象(混入禁止)
R1(Writer語順制約)・V2(末尾エネルギー検査)・固有名詞allow-list・既存ASR品質Gate緩和・M1/F1と無関係なPrompt変更・Family Z再生成。

## 7. 未解決(USER_DECISION_REQUIRED候補)
1. **OOV語の扱い**(`OOV_SAFETY_01.md`): 既定=CMU収録語のみ。Melos 12件のPASS数は4/12で現行と同じ(M1の主目的は達成できない)。(iii)を採るにはユーザーの新基準承認が必要。
2. Eq Layerの同種F1不備を今回の是正範囲に含めるか(`F1_FIX_DESIGN_01.md`)。
