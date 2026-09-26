# fact_fidelity_fix_01.md — MUSE-HC-012 時制修正記録

管理ID: NEWS-FAMILY-X-B3-DIVERSITY-TRIAL-01(Meta記事run_01への付随修正、
新Trialではない)

## 問題

Ledger `MUSE-HC-012`:
> 「MetaのSuperintelligence Labs部門の副社長は、適切な開示なしに契約
> スタッフが電話をかけるテストを開始したことを「ミス」だったと認め、
> 機能を当面ロールバックした**と社内投稿で説明した**。」

Fact自体は完了形(「ロールバックした」)だが、修正前の生成済み本文は
未来形だった:

- JA R2(修正前): 「人間のコンシェルジュ機能は当面ロールバックされます。」
- Advanced/Standard(修正前): "The human concierge feature **will be
  rolled back** for now."

## 修正内容(最小限のlocal修正、再生成なし)

| ファイル | 修正前 | 修正後 |
|---|---|---|
| `ja_writer/revision2.md` | 「人間のコンシェルジュ機能は当面ロールバックされます。」 | 「人間のコンシェルジュ機能は当面ロールバックされました。」 |
| `b1b/article.md` | "The human concierge feature will be rolled back for now." | "The human concierge feature has been rolled back for now." |
| `a2/article.md` | "The human concierge feature will be rolled back for now." | "The human concierge feature has been rolled back for now." |

該当文以外は無変更。LLMによる再生成は行っていない(テキストエディタ的な
文字列置換のみ)。

## Superseded保存

修正前の全文を以下へ保存済み(削除ではなく保存):

- `audit/superseded_fact_fidelity_01/revision2_superseded.md`
- `audit/superseded_fact_fidelity_01/b1b_article_superseded.md`
- `audit/superseded_fact_fidelity_01/a2_article_superseded.md`
- `audit/superseded_fact_fidelity_01/b1b_parts_superseded.json`
- `audit/superseded_fact_fidelity_01/a2_parts_superseded.json`

## 副次的な再生成(parts.jsonの整合性維持のため)

`b1b/parts.json`・`a2/parts.json`は、修正後の`article.md`に対して
既存の`er003_v1_n3_01_scaffold_generate.split_article_text()`
(決定的なテキスト分割関数、LLM呼び出しなし)を再実行して更新した
(本文が1文だけ変わったことによるpart1/part2の再分割結果を反映するため。
Point/In One Lineの内容自体はこの修正で変化していない)。

## 修正後の検証(既存vfl01.run_deviation_check、Full Ledger照合)

既存Production関数`er003_v1_en_direct_vfl_01_generate.
run_deviation_check(client, ledger_text, article_text, hook_aware=False)`
を、修正後のb1b/article.mdおよびa2/article.mdに対して再実行した
(一回限りのTrial専用検証スクリプト、Production module自体は無変更)。

| level | overall_status | response_id |
|---|---|---|
| b1b(Advanced) | LEDGER_COMPLIANT | resp_0b5749199ac9572e006ab7a283866887d0aad916f076b0101b |
| a2(Standard) | LEDGER_COMPLIANT | resp_082f5e1128ab50bd006ab7a28d01dc87d0b92656e325e4144f |

詳細JSON: `audit/b1b_deviation_check_after_fix.json`、
`audit/a2_deviation_check_after_fix.json`、サマリ:
`audit/fact_fidelity_fix_01_recheck_summary.json`。

## 費用

`audit/fact_fidelity_fix_01_usage_log.jsonl`より、b1b再検証=0.323円、
a2再検証=1.244円、合計1.568円(集計は
`er019_output/family_x_b3_diversity_trial_01/cost.json`に含む)。

## 結論

再生成せずlocal修正のみでFact fidelityを回復し、既存のFull Ledger
deviation checkでLEDGER_COMPLIANTを再確認した。Production採用可否の
判断はユーザーに委ねる(本タスクはPRODUCTION_WIRED済みrunnerの出力への
事後修正であり、新規Production配線変更は行っていない)。
