# 訂正記録(Sonnet作業ミス)

このディレクトリの内容は、当初「Theme 2 Ledger(承認済み)」として
`er011_output/open112_trend_engagement_reference_ab_trial_10/research/
verified_fact_ledger.txt`(米国・イラン、ホルムズ海峡テーマ)を誤って使用した
runtime evidenceである。

実際の「Theme 2」(`APPROVED_FOR_PRODUCTION`、rerun_04完成音声、
`FAMILY-A-TREND-SYNTHESIS-PRODUCTION-READINESS-01_REPORT.md`§0が指す
「若者の旅」)は、日本の若者のスロー旅行志向を扱う別テーマであり、
そのLedgerは
`er011_output/open112_trend_theme2_b_a2_b1_text_trial_12/research/
theme2_verified_fact_ledger_CORRECTED_trial12.txt`である(イラン・
ホルムズ海峡はOPEN-112-TREND-SYNTHESIS-MINIMAL-PROMPT-TRIAL-09/
OPEN-112-TREND-ENGAGEMENT-REFERENCE-AB-TRIAL-10がFocus Module検証用に
使った別の一回限りのTrialテーマであり、「Theme 2」に昇格したことはない)。

この誤りは生成後に気づき、正しいTheme 2 Ledger/topicを使って別途
`../a2/`・`../b1b/`(親ディレクトリ直下)を再生成した。こちらの
イラン・ホルムズ海峡run(B1B/A2各1回+A2追加retry1回+B1B Key Phrase
1回)は、Production Writer配線(editorial_mode="trend_synthesis"、
Focus Module実発火)が実際のテーマで機能することを示す証跡としては
有効なため削除せず保持する。ただし「Theme 2 Ledgerの再利用」という
今回のGate 3要件の証跡としては**無効**であり、正式なruntime evidenceは
親ディレクトリの`a2/`・`b1b/`(訂正後、正しいTheme 2 Ledger使用)を
参照すること。

費用: このミス分の実費は約¥83(raw_usage_log_iran_hormuz_mistake.jsonl
参照)。訂正後の正しいrunの費用と合わせて、最終報告書の費用欄に合算して
記載する(超過見込みでのSTOPには該当しない金額だが、上限¥100を
結果として超過した経緯として報告する)。
