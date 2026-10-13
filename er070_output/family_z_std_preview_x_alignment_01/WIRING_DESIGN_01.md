# WIRING_DESIGN_01 Comment 1・2入力の設計(**実装しない**。Production未配線。将来のProduction採用判断用)

## 変更箇所案(採用された場合のみ)
| # | 対象 | 現行 | 変更案 |
|---|---|---|---|
| W1 | `er026_family_z_fiction_production_runner_01.py` L468-480 `_FAMILY_Z_PREVIEW_ROLE_JA`/`build_family_z_preview_prompt` | 固定文字列(placeholderなし) | `er070`のZ_ROLE_TEMPLATE(`{comment_1}`/`{comment_2}`付き。Family X `PREVIEW_ROLE`と同じ`.format`方式)へ差替。`_BANNED_PHRASES_INSTRUCTION`は含めない(Family X逐語) |
| W2 | `er062_family_z_writer_01.py` L878-881 | `role = build_family_z_preview_prompt() + "【重複回避】…Comment 1…"`、ctx=`【物語全文(参考、新しい設定・事実の追加禁止)】` | `role = TEMPLATE.format(comment_1=out["comments"]["1"], comment_2=out["comments"]["2"])`、ctx=`【エピソード全文(参考、新しいFactの追加禁止)】\n{full_text}`(Family X L345と同一)。`out["comments"]`はL855-875で生成済み/prior再利用済みのため両方利用可能 |
| W3 | `er026` L502-512 `generate_family_z_preview`(legacy Phase1) | `build_family_z_preview_prompt()`直接使用 | placeholder化するとDangling Referenceになる(`{comment_1}`が未解決のまま送信)。legacy経路はProduction E2E(run_support_std)では不使用のため、(a)legacy側でも2 Commentを渡す、または(b)legacy関数は旧定数を別名で保持、のいずれかが必要(要判断) |
| W4 | テスト | `er062_family_z_writer_01_test_01.py`/`er026_*_test.py`にPreview prompt文面の完全一致assertがある場合は更新(今回のgrepでは`build_family_z_preview_prompt`参照はer026/er062のみ、他テスト参照なし) | 追加: Preview role内に両Commentが含まれること |

## 初回/retry/regeneration/prior整合表
| 経路 | 挙動(変更案適用時) | 整合 |
|---|---|---|
| 初回 | Comment 1->2->3生成(各lint+retry1)->Preview(両Comment入力)。Comment 2はPreview前に確定 | OK |
| lint retry(Preview) | `generate_with_lint`は`gen_p(i)`を同一roleで再呼出。roleは関数開始時に1回組立のため両Commentが毎回入る | OK |
| lint retry後NG | 既存どおり`FamilyZLintStop`。上限(retries=1)は不変 | OK。注意: roleから`_BANNED_PHRASES_INSTRUCTION`を除くとLISTEN_INSTRUCTION lint違反率が上がる可能性(未検証、1サンプルでは違反なし) |
| regeneration(stage再生成、prior指定) | Comment 1/2は再利用、Comment 3のみ再生成。`prior["preview"]`があればPreviewは再利用=**新Promptでは再生成されない** | 矛盾はないが、新Promptを既存記事へ反映するにはpriorからpreviewを除く等の運用判断が必要 |
| Comment 2のみ再生成される運用 | 現行仕様で存在しない(Comment 1/2は常にセット再利用) | OK |
| Advanced | 既にComment 1・2両方(`b1s.PREVIEW_ROLE`)。変更なし | OK |

## Trialでの再現
Trialは`er070_*.py`で、`run_e2e_02/support/a2_support.json`のComment 1・2を読込み、Family Xと同じ`.format`で埋込、`a2gen.run_support_text`(Production同一model/effort/developer message/`build_support_prompt`)で1 call。実際に両Commentが最終送信prompt(`prompt_after_full_assembled_01.txt`)に入ることをassertで確認済み。Production経路(run_support_std)自体の呼出は未実行(編集禁止・有料再生成禁止のため)。mockで現行経路がComment 1のみであることをbaselineとして実測。
