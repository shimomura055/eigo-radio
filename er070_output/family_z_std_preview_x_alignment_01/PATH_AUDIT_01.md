# PATH_AUDIT_01 (FAMILY-Z-STANDARD-PREVIEW-X-ALIGNMENT-01) 正本・経路確認(読み取りのみ)

| 項目 | Family X Standard(基準) | Family Z Standard(現行Production) |
|---|---|---|
| Prompt正本 | `er003_v1_iran01_a2_generate.py` L174-204 `PREVIEW_ROLE`(theme/problem/value、question任意、2文・80〜110字目安/4文・150字超不可、答え/数字/結論/turning point先出し禁止、Comment 1・2重複禁止) | `er026_family_z_fiction_production_runner_01.py` L468-477 `_FAMILY_Z_PREVIEW_ROLE_JA`(状況設定2〜3文80〜110字、結末/山場に触れない、本文外事実禁止、`fam_c._BANNED_PHRASES_INSTRUCTION`付与)。取得は`build_family_z_preview_prompt()`(L479) |
| 組立 | `PREVIEW_ROLE.format(comment_1=c1.text or "(生成失敗)", comment_2=c2.text or "(生成失敗)")`(L341-344、format placeholder方式) | `er062_family_z_writer_01.py::run_support_std` L878-880: `build_family_z_preview_prompt() + "【重複回避】直前に流れるComment 1は…\n{comments['1']}"`(文字列結合、**Comment 1のみ**) |
| context | `【エピソード全文(参考、新しいFactの追加禁止)】\n{a2_text}`(L345) | `【物語全文(参考、新しい設定・事実の追加禁止)】\n{full_text}`(L881) |
| 生成呼出 | `run_support_text(client, preview_role, preview_context)`(model=A2_SUPPORT既定、developer=`日本語のListening Support原稿を作成してください。`、`build_support_prompt`がSUPPORT_JA_PRINCIPLE/PROHIBITIONS付与、max_attempts=2=技術失敗retry) | `fn(client, role, ctx, model=routing.require_model("A2_SUPPORT",...))`(`a2gen.run_support_text`、同一) |
| 生成順序 | Comment 1 -> 2 -> 3 -> 4 -> Preview(L325-345)。Preview生成時にComment 1・2が利用可能 | Comment 1 -> 2 -> 3 の for ループ(L853-875) の後にPreview(L878-)。**Preview生成時点でComment 1・2・3全て生成済み**(mock実測: Preview呼出が4回目、`er070_*_test_01.py`) |
| lint/retry | 機械lintなし(技術失敗のみ2回) | `generate_with_lint(gen_p, lint)` retries=1 -> なおNGなら`FamilyZLintStop`(`lint_support_text(t,'ja',story_key)`: LANG/COMMON/LISTEN_INSTRUCTION/FORBIDDEN_NAME/SPOILER) |
| prior再利用 | - | `prior`指定(`regenerate_stage==support_a2`かつ既存json、er026 L1126-1133)時、Comment 1/2を再利用しComment 3のみ再生成。`prior["preview"]`があればPreviewも再利用(L885-887、Preview再生成しない) |
| Comment 2不在時 | `"(生成失敗)"`埋込(X) | Z: Comment生成失敗は`FamilyZStop`/`FamilyZLintStop`で停止するため「不在」は発生しない |
| 旧経路 | - | `generate_family_z_preview`(er026 L502、Phase1 legacy `run_text_stage` L679から呼出)が`build_family_z_preview_prompt()`を**直接**使用。重複回避なし。run_support_std(L1132 `runner`)が現行E2E経路 |
| Adv(参考) | - | `run_support_adv` L921: `b1s.PREVIEW_ROLE.format(comment_1=, comment_2=)`(Family X B1、Comment 1・2両方)。**Adv Previewは既にComment 1・2**。今回変更なし |

## CURRENT_SPEC(既存ユーザー承認内容)
- 1590行「Preview原則」: 「テーマ・問題意識・聞く価値・最後まで聞きたくなる問いを示す。具体的な答え・数字・転換点・結論を先出ししない。A2ではComment1/2がListening Focusとして機能するようPreviewとの情報重複を特に避ける」(Family X/Z共通原則として記載)。
- 2026-10-12決定(CURRENT_SPEC 1524行): Family Z Stdは3分割Story・Comment 3つ・**In One Lineなし・Comment4なし**(Point構造なし)。
- Family Z Std Preview文面そのもの(`_FAMILY_Z_PREVIEW_ROLE_JA`)をユーザーが承認した記載は`Preview.*Family Z`系のGrepでは確認できず(Family Z Std Previewの専用承認行なし)。本ID(2026-10-13)で「Family X基準へ統一」の設計方針のみユーザー確定。Production配線は未承認。

## 整合上の事実
1. Comment 2はPreview生成時に利用可能(生成順序と矛盾しない)。STOP条件(3)に該当しない。
2. prior再利用時、Previewも再利用されるため、Prompt変更後も既存run_e2e_02のPreviewは再生成されない(新Promptを反映するには新規run、またはprior未指定/preview除去の再生成が必要)。
3. `build_family_z_preview_prompt()`はlegacy `generate_family_z_preview`も使用。format placeholder化する場合は呼出側整理が必要(`WIRING_DESIGN_01.md`)。
