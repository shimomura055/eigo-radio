# 2026-10-07 OPEN-233-CHECKER-ACTION-POLICY-DESIGN-01 委任_02(Opus条件Aレビューの必須修正M1〜M4・任意O1〜O3を設計v2へ反映し、段階2の事前登録を書く。¥0)

(保存注記: 受領した委任文の要旨再構成。見出しは標準テンプレートに合わせて補完。)

## 管理ID
OPEN-233-CHECKER-ACTION-POLICY-DESIGN-01(委任_02)

## 性質/到達上限Status/禁止事項
- 性質: 設計文書のみ。API禁止・git禁止・コード/SSOT/ACTIVE_TASK/RESULT_PACKET編集禁止。held-out項目は参照しない。
- 並行タスク: STAGE2-01_01(W1/W2バグ修正、runner・tests・`er052_output/open233_stage2_01/precheck/`)。書込先は`docs/pm/checker_action_policy_01/`、`docs/pm/opus_l2_review_checker_action_policy_01.md`、delegation_logのみ。
- 禁止事項: Agent/Subagent起動、`git add -A`、無関係差分の編集、Production変更。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0)
- E-1: 事前指定範囲だけを実行。D-1: Production経路とTrial経路を区別。G-1: 実測だけを報告。F-1: 詳細は既存構造、RESULT_PACKETは短く。T-0: 本委任文を保存しcheck.json。

## 事前指定Read一覧
- `docs/pm/checker_action_policy_01/design_01.md`(v1全文)
- `er052_output/open233_stage0_01/{reclass/RECLASS.md,danger/DANGER_COVERAGE.md,stability_v1/STABILITY_V1.md}`(要点のみ)

## 事前指定Grep一覧+追記位置・更新位置の手順
- Grepなし。追記位置・更新位置: 新規作成のみ(opus_l2_review_checker_action_policy_01.md、design_02.md、preregistration_stage2.md、human_review_priority_v1.md)。

## 実行コマンド全文
コマンド行なし(ファイル作成のみ。Opus台帳更新はFable側、OPUS_FINDINGS_LEDGER.mdへ後日記録)。

## SSOT追記文
- なし(SSOT編集禁止。Fableが後で扱う)。

## 作業内容
1. Opus条件Aレビュー(2026-10-07夜、Fable転記)を`docs/pm/opus_l2_review_checker_action_policy_01.md`へ保存(結論/観点1〜5/必須修正/任意改善/段階2持ち越し/先行可)。要点: M1 ①は全手段に4照合+主体語差し替え禁止(主体集合は部分集合)。M2 語り手の枠は世界主張にしない、Hook削除は最終手段。M3 ガード対象は決定論で付与、「安全側」→「Rewrite増側」。M4 ④番号写像は明示テーブル・文ID方式、未定義なら段階3以降、r3 support_fact_ids保存を先行。O1 2nd opinion 2回目は文を見せない。O2 既払い不一致信号で人間確認順位。O3 ②不合格ならrubric追記打ち止め。
2. `design_02.md`(v1は残す)へM1〜M4・O1〜O3を[Opus M1]等の印付きで反映。④は段階3以降(M4条件付き)、r3 support_fact_ids保存は①②と同段階、③は既払い不一致信号による人間確認優先順位付け(O2)として再定義。Reconciliation表更新。
3. `preregistration_stage2.md`(時刻付き): 合否ライン(数値不変)+O3+構造要素由来STOP≤3%+held-out 1回(方向一致・回帰0のみ)+replay対象は現行Stage1版と同版ログの記事(`precheck/replay_targets.json`参照)+測定順序(0)〜(4)。費用上限: 段階2合計¥200。
4. `human_review_priority_v1.md`(O2規則と上位10%運用)。
5. 本委任文の保存+check.json。

## Git
- git禁止(Fableが明示addで扱う)。

## 報告
- 12行以内: M1〜M4・O1〜O3各1行、合否ライン列挙、費用上限、ファイルパス。RESULT_PACKETは編集しない(最終メッセージで返す)。
